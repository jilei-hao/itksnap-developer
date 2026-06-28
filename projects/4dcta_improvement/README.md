# 4D CTA Reading Improvement — ITK-SNAP

Improve how ITK-SNAP reads, holds, and writes **4D cardiac CTA** so that it preserves the
**cardiac phase axis** and **important non-PHI metadata**, in a representation that can be re-written
to multiple formats (`.nii.gz`, `.nrrd`, Slicer `.seq.nrrd`).

> **Status (2026-06-28): MVP implemented + verified.** Phases **P0 + P1 + P3.3** are done on itksnap
> branch **`feature/cardiac-io`** (commit `0e5168ad`, pushed; wrapper `main` tracks it). 4D CTA reads
> now derive the cardiac `%R-R` axis from the `SeriesDescription` and carry it via the image
> `MetaDataDictionary`; the `.seq.nrrd` writer emits it as the (non-uniform-capable) `axis 0 index
> values`. Verified end-to-end on AVRP `bavcta005` (clean 20-phase → `0 5 … 95`) and `bavcta007`
> (ambiguous 10-phase → non-uniform `0 10.56 … 95`). All MVP code is in
> `Logic/ImageWrapper/GuidedNativeImageIO.cxx`.
>
> **Remaining:** P3.1 (NIfTI fraction header + JSON sidecar), P3.2 (plain `.nrrd` keys — likely free
> via the dictionary), P2 (typed `TimePointProperties` cardiac fields + UI surfacing). The float
> (non-identity-mapping) write path still bypasses `SaveNrrdSequence`, and the `.seq.nrrd` read-side
> doesn't yet repopulate the cardiac key. See [improvement_plan.md](improvement_plan.md).
>
> *History:* analysis was done on `test/dls_sam2 @ 8539d63c` (where `.seq.nrrd` was read-only), then
> reassessed against `master @ 28f4ee45` (which added the seq.nrrd writer + unified `SaveImage()`).

## The three requirements
1. Keep **cardiac phase information**.
2. Keep **as much important non-PHI info as possible**.
3. Kept info must be **writable to various formats** (`.nii.gz`, `.seq.nrrd`, …).

## Documents
| Doc | What |
|---|---|
| [analysis_existing_logic.md](analysis_existing_logic.md) | How ITK-SNAP reads/holds/writes 4DCTA today, with file:line refs and the gap list (G1–G8). |
| [metadata_reference.md](metadata_reference.md) | Concrete tag keep-list / PHI drop-list / per-format write recipes (distilled from AVRP `phase_detection`). |
| [improvement_plan.md](improvement_plan.md) | Phased plan (P0–P5), file-by-file change map, tests, open decisions. |

## TL;DR of the findings
ITK-SNAP has a real 4D-CTA path, and the slice/phase **ordering is already correct** (group by Z →
rank phases by `InstanceNumber` → order slices by geometry). The problems are around the pixels:

- **G1** temporal axis is hardcoded `spacing4d[3] = 0.05`
  ([GuidedNativeImageIO.cxx:1165](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx)) —
  *"should be extracted from the images"*; no `%R-R`, no `TriggerTime`.
- **G2** only one (and the *wrong*, last) frame's DICOM dictionary is kept; per-phase metadata is
  dropped ([:1205](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx)).
- **G3** no cardiac-phase data model — `TimePointProperties` holds only `Nickname`+`Tags`.
- **G4** *(narrowed on master)* the `.seq.nrrd` writer now exists (`SaveNrrdSequence`, [:1553](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx))
  but stamps the frame axis with ordinals `0…T-1` ([:1634](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx)),
  not `%R-R`, and writes no metadata; NIfTI emits a scalar `pixdim[4]`; NRRD writes no custom keys.
- **G5–G8** no grid validation/quarantine, coarse "any Siemens/GE CT = 4DCTA" detection, no curated
  non-PHI block, `%R-R` derivable from `SeriesDescription` but never parsed.

## The fix in one line
Introduce **one format-agnostic in-memory model** (per-time-point cardiac fields + curated non-PHI
block), populate it on read (from cardiac tags *or* the structural `SeriesDescription` recipe), and
serialize it through the now-unified `SaveImage()` write path — starting by feeding `%R-R` into the
**existing** `.seq.nrrd` writer (replacing its ordinal frame index). Minimum viable = plan phases
**P0 + P1 + P3.3**, now a smaller change than originally scoped because the writer already exists.

## Source of requirements
AVRP `phase_detection` investigation:
`/Users/jileihao/dev/avrp-developer/projects/phase_detection/`
(`reports/dicom_to_volume_reference.md`, `reports/step1_phase_axis_discovery.md`,
`scripts/anonymize_4dcta.py`).

## Key code touchpoints (itksnap submodule, `master @ 28f4ee45`)
- `Logic/ImageWrapper/GuidedNativeImageIO.cxx` — DICOM read + 4D assembly (hardcoded `0.05` :1165,
  single-frame metadata :1205); format table (:122); `SaveNrrdSequence` (:1553, ordinal index :1634);
  unified `SaveImage` (:1686).
- `Common/MultiFrameDicomSeriesSorter.cxx` — phase/slice sorting (correct; add validation).
- `Logic/ImageWrapper/WrapperBase.h/.cxx` — consolidated per-layer metadata members (commit
  `2ad9e198`; home for the new cardiac + non-PHI model).
- `Logic/Framework/TimePointProperties.h/.cxx` — per-time-point store (extend for cardiac fields).
- `Logic/ImageWrapper/ImageWrapper.cxx` — 4D model, write decision (:2243), unified Write→SaveImage
  (:300), per-layer metadata serialize (:2602/2617).
- `GUI/Model/ImageInfoModel.cxx` — metadata inspector (surface `%R-R`).
