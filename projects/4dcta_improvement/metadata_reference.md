# 4D CTA Metadata Reference — What to Keep, What to Drop, How to Write It

**Date:** 2026-06-26
Distilled from the AVRP `phase_detection` investigation
(`/Users/jileihao/dev/avrp-developer/projects/phase_detection/`), specifically
`reports/dicom_to_volume_reference.md`, `reports/step1_phase_axis_discovery.md`, and
`scripts/anonymize_4dcta.py`.

This is the **requirements substrate** for the [improvement plan](improvement_plan.md): the exact
fields ITK-SNAP should capture on read, hold in memory, and serialize on write — and the PHI it must
*not* keep.

---

## 1. The three user requirements, made concrete

> 1. keep **cardiac phase information**
> 2. keep **as much important non-PHI info as possible**
> 3. kept info must be **writable to various formats (nii.gz, seq.nrrd, …)**

These map to three in-memory artifacts:

- **(A) A cardiac phase axis** — per-time-point: phase index, `%R-R` value, and (when available)
  `TriggerTime`/`dt`. May be **non-uniform** (the 10-phase case).
- **(B) A curated non-PHI study metadata block** — scanner, protocol, geometry-precision, and
  intensity-calibration facts, minus all PHI.
- **(C) Format-agnostic storage** — both (A) and (B) live in a representation that each writer
  serializes in its own idiom (NIfTI header+sidecar, NRRD keys, Slicer `.seq.nrrd` frame index).

---

## 2. (A) Cardiac phase axis

### 2.1 Standard cardiac DICOM tags — use when present
These are **non-private, non-PHI** and untouched by de-identification. Absent in the AVRP Siemens
"Func" recons, but present in many other 4D vendors/protocols — so capture them when they exist:

| Tag | Name | Meaning |
|---|---|---|
| `(0018,1060)` | `TriggerTime` | ms after R-wave — **the** per-frame phase timing |
| `(0018,1062)` | `NominalInterval` | nominal R-R interval (ms) |
| `(0018,1081)` / `(0018,1082)` | `LowRRValue` / `HighRRValue` | accepted R-R window |
| `(0018,1088)` | `HeartRate` | bpm |
| `(0018,1090)` | `CardiacNumberOfImages` | phases per cycle |
| `(0020,9153)` | `NominalPercentageOfCardiacPhase` | `%R-R` (enhanced/functional IODs) |
| `(0020,9241)` | `NominalCardiacTriggerDelayTime` | enhanced-IOD per-frame delay |

### 2.2 Structural fallback — when no cardiac tag exists (the AVRP case)
Recover the axis from structure (verified on all 4 AVRP studies):

```
N_slices = number of distinct ImagePositionPatient[2] (Z) values
N_phases = N_files / N_slices                  # must be integer (rectangular grid)
phase    = (InstanceNumber - 1) // N_slices    # 0 .. N_phases-1, ascending %R-R
slice    = (InstanceNumber - 1) %  N_slices
%R-R[k]  = linspace(start, end, N_phases)[k]   # start/end parsed from SeriesDescription
```

- `SeriesDescription (0008,103E)` carries the range, e.g. `"Func DS_CorCTA 0.5 Bv36 4  0 - 95 %"`,
  `"DS_CORCTA_FUNC_5 - 95 %_0.75"`, `"DS_CORCTA_FUNC_0-95%"`. Parse `start–end %`.
- **Phase direction:** assume block 0 = lowest `%R-R`, ascending (standard Siemens "Func" order).
  No tag proves it; corroborate later from a motion curve if a detector is built.
- **Ambiguous case:** a 10-phase study labeled "0–95 %" almost certainly samples integer steps
  (`0,10,…,90`), *not* the literal `linspace(0,95,10)`. Flag as approximate / non-uniform.
- **`HeartRate`** for AVRP lives in `ScanOptions` (`OSCRATEAVG0NNBPM`); `%R-R ↔ seconds` via
  `R-R ≈ 60/HR`.

> ITK-SNAP **already recovers `phase`/`slice` correctly** via its group-by-Z + rank-by-InstanceNumber
> sorter (see [analysis §2](analysis_existing_logic.md)). What's missing is computing and keeping the
> **`%R-R` value** per phase — the structural recipe above (or §2.1 tags) is the source.

### 2.3 What to store per time point (proposed model)
```
TimePointCardiacInfo {
  uint     phase_index;        // 0-based, ascending %R-R
  double   rr_percent;         // %R-R; NaN if unknown
  bool     rr_percent_exact;   // false for the ambiguous 10-phase case
  double   trigger_time_ms;    // (0018,1060) if present, else NaN
  double   nominal_interval_ms;// (0018,1062) if present, else NaN
}
```
Plus study-level: `heart_rate_bpm`, `n_phases`, `rr_source ∈ {dicom_tag, series_description, manual}`.

### 2.4 Geometry precision facts (keep as metadata, do not use as Z spacing)
- **Z spacing = geometric** (from consecutive `ImagePositionPatient`, ≈0.3 mm for AVRP) — ITK's
  series reader already does this. **Do not** use `SliceThickness` (0.5 mm) as spacing (would stretch
  Z ~1.67×). `SpacingBetweenSlices (0018,0088)` is absent in AVRP.
- Keep `SliceThickness (0018,0050)` and `PixelSpacing (0028,0030)` as recorded metadata
  (measurement-precision provenance).

---

## 3. (B) Non-PHI metadata to keep

### 3.1 Keep-list (research-relevant, non-PHI)
| Category | Tags / fields |
|---|---|
| Modality/scanner | `Modality (0008,0060)`, `Manufacturer (0008,0070)`, `ManufacturerModelName (0008,1090)`, `SoftwareVersions (0018,1020)` |
| Protocol | `SeriesDescription (0008,103E)`, `ProtocolName (0018,1030)`, `ScanOptions (0018,0022)`, `ImageType (0008,0008)`, `ConvolutionKernel (0018,1210)`, `BodyPartExamined (0018,0015)` |
| CT technique | `KVP (0018,0060)`, `XRayTubeCurrent (0018,1151)`, `Exposure (0018,1152)`, `ExposureTime (0018,1150)`, `SpiralPitchFactor (0018,9311)`, `GantryDetectorTilt (0018,1120)` |
| Cardiac | all of §2.1 |
| Geometry | `PixelSpacing (0028,0030)`, `SliceThickness (0018,0050)`, `ImageOrientationPatient (0020,0037)`, `ImagePositionPatient (0020,0032)` (per slice; origin is in the affine), derived Z spacing |
| Intensity calibration | `RescaleSlope (0028,1053)`, `RescaleIntercept (0028,1052)`, `RescaleType (0028,1054)` (=`HU`), `WindowCenter/Width (0028,1050/1051)` |
| Pixel | `Rows/Columns (0028,0010/0011)`, `BitsStored (0028,0101)`, `PixelRepresentation (0028,0103)` |
| Hierarchy (de-identified) | remapped `StudyInstanceUID`, `SeriesInstanceUID`, `FrameOfReferenceUID` (consistent pseudonymous UIDs) |
| Research covariates (kept; HIPAA basis in §3.3 — age top-coded at 90) | `PatientAge (0010,1010)`, `PatientSex (0010,0040)`, `PatientSize (0010,1020)`, `PatientWeight (0010,1030)`, `PatientBodyMassIndex (0010,1022)` |

### 3.2 Drop-list (PHI — never persist into exported research files)
From `anonymize_4dcta.py` `TAGS_TO_BLANK` — names, IDs, dates (beyond a shifted study date),
contacts, institution/station, operator/physician names, accession/study IDs, all free-text
comment fields, and **all private tags by default** (the Siemens CSA blob `(0029,1010)` carries no
phase content and is dropped). UIDs are kept but **remapped** consistently.

> **Design stance:** ITK-SNAP reads from already-de-identified data in this workflow, so the reader's
> job is *curation* (keep the §3.1 set, present it, and re-emit it on write) rather than
> de-identification. But when re-exporting, the writer should **not** blindly copy the raw DICOM
> dictionary into a NIfTI/NRRD sidecar — it should emit only the curated keep-list, so we never
> launder PHI from a not-fully-cleaned source into a derived file. Treat §3.2 as an explicit
> exclusion filter on export.

### 3.3 HIPAA basis for keeping research covariates (and how it's implemented)

*Not legal advice — the IRB/privacy office has final say.* HIPAA de-identification
(45 CFR §164.514(b)) offers **Safe Harbor** (remove 18 enumerated identifiers) or **Expert
Determination** (statistician certifies low re-identification risk); a **Limited Data Set**
(§164.514(e), needs a Data Use Agreement) may additionally retain dates and full ages.

Per covariate, under Safe Harbor:

| Covariate | One of the 18 Safe Harbor identifiers? | Decision |
|---|---|---|
| `PatientSex (0010,0040)` | No | keep |
| `PatientSize`/height `(0010,1020)` | No | keep |
| `PatientWeight (0010,1030)` | No | keep |
| `PatientBodyMassIndex (0010,1022)` | No | keep |
| `PatientAge (0010,1010)` | **Only if > 89** (ages over 89 are identifiers) | keep, **top-code ≥90 → `090Y`** |

Notes: `PatientBirthDate (0010,0030)` is a date identifier and is dropped (age alone is fine).
De-identification is holistic — keeping covariates is compliant only because the other identifier
categories (names, IDs, full dates, institution, device serials, private tags) are dropped by §3.2.
The AVRP pipeline's `anonymize_4dcta.py` retains *shifted* dates, which is an Expert-Determination /
Limited-Data-Set technique (not Safe Harbor); top-coding age at 90 is the safe move under any route.

**Implemented (itksnap `feature/cardiac-io`, commit `7a1c2489`):** export curation in
`GuidedNativeImageIO::SaveImage` swaps in an **allow-list** dictionary (the §3.1 tags +
`ITKSNAP_Cardiac_*` keys, with `0010|1010` top-coded at 90) before the NRRD/MetaImage writer, then
restores the in-memory dict (curation is **export-only** — the Image Info inspector keeps full
fidelity). Allow-list (not deny-list) so unenumerated/private/free-text tags can never slip through.
No-op for non-DICOM dictionaries, so custom keys on `.nrrd`/`.nii` inputs are preserved.

---

## 4. (C) Writing the axis + metadata per format

The phase axis (§2) is **non-uniform-capable**; most file formats' axes are uniform-only, so the
strategy differs per format. Summary of how the phase_detection reference says to do it:

### 4.1 NIfTI (`.nii.gz`)
- **Uniform header axis:** `pixdim[4]` = cardiac-cycle **fraction step** (e.g. `0.05` for 20-phase
  0–95 %), `xyzt_units` t = *unknown* (= fraction), `toffset = start%/100`. Then
  `%R-R[k] = (toffset + k·pixdim[4])·100`. *(This matches the existing `i4_rs20` convention and is
  what ITK-SNAP's hardcoded `0.05` accidentally equals for one study.)*
- **Exact / non-uniform array:** NIfTI has no native per-frame list. Options, best→worst:
  - **JSON sidecar** (`*.json`) — survives any tool; **treat as authoritative**.
  - **Header extension** (ecode 6, JSON) — proper mechanism but *silently dropped* by some
    FSL/ANTs ops. Write it too, but don't rely on it alone.
  - `descrip` (80 chars) / `intent_p1..3` — hacky; avoid.
- **Recommended:** fraction header **+ JSON sidecar** with the full frame axis + slice thickness.
- **Coordinate convention:** NIfTI affine is **RAS** (flip X/Y from DICOM LPS).

> **Implemented (itksnap):** `WriteCardiacJsonSidecar`/`ReadCardiacJsonSidecar` (jsoncpp) make the
> NIfTI sidecar **bidirectional** — a 4D NIfTI write→reload recovers the frame axis (CT `%R-R` or echo
> `ms`) **and** `SliceThickness` by injecting the keys back into the dictionary. (`SliceThickness` has
> no native NIfTI field either — it lives only in the sidecar there.) NRRD/`.seq.nrrd` carry both
> in-file and need no sidecar; `.seq.nrrd` writes slice thickness as the native `thicknesses:` field.

### 4.2 NRRD (`.nrrd`)
- Geometric axes are also uniform-only, **but** NRRD preserves arbitrary `key:=value` header fields
  on round-trip (unlike NIfTI extensions). Store the exact `%R-R` list **in-file**, no sidecar
  needed, e.g. `AVRP_RR_percent:=0 5 10 … 95`, plus curated metadata keys.

### 4.3 Slicer volume sequence (`.seq.nrrd`) — first-class non-uniform axis
Purpose-built; stores an explicit per-frame index that **can be non-uniform** → models `%R-R`
(including the 10-phase case) as a first-class index. Read natively by Slicer **Sequences** +
**SlicerHeart**.

> **ITK-SNAP status (`master @ 28f4ee45`):** a `.seq.nrrd` **writer now exists**
> (`SaveNrrdSequence`, GuidedNativeImageIO.cxx:1553). It uses NRRD's **native** index mechanism
> (`kinds: list domain domain domain` + `axis 0 index type:=numeric` + `axis 0 index values:=…`),
> which is cleaner than — and an alternative to — the SlicerHeart `MultiVolume.FrameLabels` convention
> below; both are valid and Slicer-readable. **The gap is the values:** the writer currently emits
> ordinals `0 1 2 … T-1`, not `%R-R`, and no extra metadata. The work is to feed the real `%R-R`
> array into `axis 0 index values` and append the curated keys.

**Target header (what the extended writer should emit):**
```
kinds:                  list domain domain domain          # ITK-SNAP order: list axis first
space:                  left-posterior-superior            # LPS
axis 0 index type:=     numeric
axis 0 index values:=   0 5 10 … 95                        # %R-R, non-uniform OK  ◄── the fix
axis 0 index units:=    %                                  # (optional units hint)
AVRP_RR_percent:=       0 5 10 … 95                         # redundant explicit copy
HeartRateBpm:=          51
```
Equivalent SlicerHeart MultiVolume convention (alternative spelling, also accepted by Slicer):
```
MultiVolume.FrameLabels:                  0,5,10,…,95       # non-uniform OK
MultiVolume.NumberOfFrames:               20
MultiVolume.FrameIdentifyingDICOMTagName: CardiacRRPercent
MultiVolume.FrameIdentifyingDICOMTagUnits:%
```

### 4.4 Decision matrix
| Downstream | Recommended output |
|---|---|
| Uniform/resampled phases, generic tools | NIfTI fraction header + JSON sidecar |
| Native non-uniform phases (e.g. 10-phase) | `.seq.nrrd` **or** NIfTI + sidecar |
| Slicer / SlicerHeart | `.seq.nrrd` |
| In-file robustness, no sidecar | plain NRRD with custom keys |
| Existing `.nii.gz` / segflow4d pipeline | NIfTI fraction header + JSON sidecar |

---

## 5. Cohort facts (for tests / fixtures)

| Study | Files | Grid (phases×slices) | %R-R | In-plane mm | Z mm | HR |
|---|---:|---|---|---|---|---:|
| bavcta005 | 3200 | 20×160 | 0,5,…,95 ✅ | 0.314 | 0.3 | 51 |
| bavcta006 | 6954 | 19×366 | 5,10,…,95 ✅ | 0.367 | 0.3 | 49 |
| bavcta007 | 3570 | 10×357 | 0–95 % **ambiguous** ⚠️ | 0.367 | 0.3 | 61 |
| bavcta008 | 5720 | 20×286 | 0,5,…,95 ✅ | 0.377 | 0.3 | 42 |

Raw data: `/Users/jileihao/data/avrp/4DCTA_anon/bavcta00{5,6,7,8}_baseline/`.
Resampled ground-truth (20-phase, uniform) + manual open/close labels: `dev/<study>_rs20/`.
The `i4_rs20` files use `pixdim[4]=0.05` fraction convention — the reference target for NIfTI output.
