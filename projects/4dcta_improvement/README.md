# 4D CTA Reading Improvement — ITK-SNAP

Improve how ITK-SNAP reads, holds, and writes **4D cardiac CTA** so that it preserves the
**cardiac phase axis** and **important non-PHI metadata**, in a representation that can be re-written
to multiple formats (`.nii.gz`, `.nrrd`, Slicer `.seq.nrrd`).

> **Status (2026-06-28): cardiac `%R-R` axis implemented + verified across all three formats.** On
> itksnap branch **`feature/cardiac-io`** (HEAD `7b51378a`, pushed; wrapper `main` tracks it). 4D CTA
> reads derive the `%R-R` axis from the `SeriesDescription` and carry it via the image
> `MetaDataDictionary`. Writers:
> - **`.seq.nrrd`** (P3.3) — `%R-R` as the non-uniform `axis 0 index values` + units + keys.
> - **`.nii.gz`** (P3.1) — `pixdim[4]` = cardiac-cycle fraction step + a `<name>.json` sidecar with
>   the authoritative `%R-R` array. (`toffset`/`xyzt_units` are ITK defaults; sidecar is canonical.)
> - **`.nrrd`** (P3.2) — the `ITKSNAP_Cardiac_*` keys ride the dictionary automatically (no code).
>
> Verified end-to-end on AVRP `bavcta005` (clean 20-phase → `0 5 … 95`) and `bavcta007` (ambiguous
> 10-phase → non-uniform `0 10.56 … 95`). All code is in `Logic/ImageWrapper/GuidedNativeImageIO.cxx`.
>
> **✅ Requirement 2 (non-PHI curation) done** (commit `7a1c2489`): export now swaps in a curated
> non-PHI **allow-list** (scanner/protocol/technique/cardiac/geometry/calibration/covariates + the
> `ITKSNAP_Cardiac_*` keys, age top-coded at 90 per HIPAA Safe Harbor) before the NRRD/MetaImage
> writer, then restores the in-memory dict (export-only; inspector keeps full fidelity). Verified on
> `bavcta005`: exported `.nrrd` drops name/ID/dates/institution/accession/private-CSA, keeps the
> research metadata. HIPAA rationale in [metadata_reference.md §3.3](metadata_reference.md).
>
> **Remaining:** P2 (typed `TimePointProperties` fields + UI); the float (non-identity-mapping) write
> path still bypasses `SaveNrrdSequence`; the `.seq.nrrd` read-side doesn't repopulate the cardiac
> key; the same export curation could be extended to the general (non-4DCTA) DICOM load path. See
> [improvement_plan.md](improvement_plan.md).
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
