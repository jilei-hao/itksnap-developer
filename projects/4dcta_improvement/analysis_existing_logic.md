# Existing 4D CTA Reading Logic in ITK-SNAP — Analysis

**Date:** 2026-06-26 · **Updated:** 2026-06-27 (rebased onto `master`)
**Scope:** How ITK-SNAP currently reads, holds in memory, and writes 4D cardiac CTA
(time-series) images, with emphasis on **cardiac-phase** and **non-PHI metadata** handling.
**Source tree:** `itksnap/` submodule, branch **`master` @ `28f4ee45`** (re-verified line numbers).

Companion docs: [requirements & metadata reference](metadata_reference.md) ·
[improvement plan](improvement_plan.md).

All file references are relative to the repo root (`itksnap/...`).

> **Update 2026-06-27 — `.seq.nrrd` export now exists on `master`.** The original analysis was done
> on `test/dls_sam2 @ 8539d63c`, where `.seq.nrrd` was read-only. `master` adds commit `01e02abd`
> *"Add .seq.nrrd (NRRD volume sequence) export support"* and `2ad9e198` *"Consolidate shared metadata
> members into WrapperBase"*. Net effect on the findings: **G4 narrows** — a `.seq.nrrd` *writer* now
> exists and the write path is unified through `GuidedNativeImageIO::SaveImage()` — but it writes the
> frame axis as **ordinals `0…T-1`, not cardiac `%R-R`, with no cardiac/non-PHI metadata**, so the
> two user requirements remain unmet. **The read-side gaps (G1, G2) are unchanged.** See §5 (rewritten)
> and the gap table in §6.

---

## 0. TL;DR

ITK-SNAP **does** have a dedicated 4D-CTA DICOM path, and the part everyone worries about —
slice/phase ordering — is actually **done correctly**: it groups by spatial Z, ranks phases by
`InstanceNumber`, and orders slices within a phase by geometry (`ImagePositionPatient`). For a clean
rectangular `N_phases × N_slices` grid this reconstructs the phase axis losslessly.

The real gaps are **everything around the pixels**:

1. **The cardiac phase axis is thrown away.** The 4th-dimension spacing is hardcoded to `0.05`
   ([GuidedNativeImageIO.cxx:1165](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx)), with
   the in-code comment *"hardcode 50ms for now, should be extracted from the images."* No `%R-R`, no
   `TriggerTime`, no `HeartRate`, no per-phase label is ever computed or stored.
2. **Per-frame metadata is discarded** — only a single 3D frame's DICOM dictionary survives, and
   even that is the *last* frame the reader touched, not frame 0 (see §3.4).
3. **No robustness/quarantine** for non-rectangular grids — phases are assigned by positional rank
   per slice, so a broken grid silently misaligns phases instead of failing loudly.
4. **Writing preserves no *meaningful* phase axis.** 4D is written as a single ITK image. A
   `.seq.nrrd` writer now exists (master, `SaveNrrdSequence`) but stamps the frame axis with
   ordinals `0…T-1`, not `%R-R`, and writes no cardiac/non-PHI metadata; NIfTI emits only a scalar
   `pixdim[4]`; NRRD writes no custom keys; the `MetaDataDictionary` is still not populated on write.
   (Before the master rebase, `.seq.nrrd` had no writer at all.)
5. **Detection is coarse** — *any* Siemens/GE CT directory is treated as 4D CTA.

The per-time-point property store (`TimePointProperties`) already exists and is serialized into the
workspace, but only holds a `Nickname` + `Tags` — it is the natural home for cardiac-phase data but
has no numeric phase fields today.

---

## 1. Read pipeline overview

```
ParseDicomDirectory()  ──► GuessFormatForFileName()  ──► [FORMAT_DICOM_DIR_4DCTA]
   (enumerate series,           (Modality==CT &&
    SeriesDescription, grid)     Manuf∈{SIEMENS,GE})
        │
        ▼
ReadNativeImageHeader()  ──► MultiFrameDicomSeriesSorter::Sort()  ──► m_DicomFilesToFrameMap
        │                       (group by Z, rank phases by InstanceNumber,
        │                        order slices within a phase by geometry)
        ▼
ReadNativeImageData()  ──► per-frame itk::ImageSeriesReader → 3D volume
        │                  → stack into itk::Image<…,4> (m_NativeImage)
        │                  → spacing[3] = 0.05 (hardcoded)
        │                  → keep ONE frame's MetaDataDictionary
        ▼
ImageWrapper  ──► m_Image4D + m_ImageTimePoints[]  (3D views into the 4D buffer)
```

### 1.1 Directory parsing & series discovery
- `GuidedNativeImageIO::ParseDicomDirectory()`
  ([GuidedNativeImageIO.cxx:2081](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx)) uses
  GDCM to enumerate files and build a `SeriesMap` keyed by `SeriesInstanceUID`, capturing
  `SeriesNumber`, `SeriesDescription`, `Rows/Cols`, `SliceThickness`, etc.
- Relevant tag constants are defined at
  [GuidedNativeImageIO.cxx:2065-2073](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx):
  `SeriesDescription = (0008,103e)`, `InstanceNumber = (0020,0013)`,
  `SliceThickness = (0018,0050)`, etc. **`SeriesDescription` is therefore already in hand** — the
  string the phase_detection work parses for the `%R-R` range (e.g. `"…0 - 95 %"`).

### 1.2 Format detection (coarse)
[GuidedNativeImageIO.cxx:2210-2219](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx):

```cpp
// 4DCTA test
std::string modality = sf.ToString(tag_modality);            // (0008,0060)
if (!modality.compare("CT")) {
  bool hasSiemens = manuf.find("SIEMENS") != std::string::npos;
  if (hasSiemens || !manuf.compare("GE MEDICAL SYSTEMS"))
    return FORMAT_DICOM_DIR_4DCTA;
}
```

> **Gap:** This classifies *every* Siemens/GE CT directory as 4D CTA, including ordinary single-phase
> CT. There is no check that the series is actually multi-phase (e.g. `N_files > N_distinct_Z`).
> A non-4D Siemens CT will be pushed through the 4D assembler and emerge as a 4D image with a single
> time point (mostly harmless) — but it also means the 4D path's assumptions are never validated.

---

## 2. Slice/phase ordering — **this part is correct**

The 4DCTA path is set up at
[GuidedNativeImageIO.cxx:561-578](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx):

```cpp
MFDSSorter->SetGroupingStrategy(MFGroupByIPP2Strategy::New());           // group by Z
MFDSSorter->SetFrameOrderingStrategy(MFOrderByInstanceNumberStrategy::New()); // rank phases
MFDSSorter->SetSliceOrderingStrategy(MFOrderByIPPStrategy::New());       // order slices by geometry
MFDSSorter->Sort();
m_DicomFilesToFrameMap = MFDSSorter->GetOutput();
```

The sorter ([Common/MultiFrameDicomSeriesSorter.cxx](../../itksnap/Common/MultiFrameDicomSeriesSorter.cxx)):

1. **Group by Z** (`MFGroupByIPP2Strategy::Apply`, line 88): bucket files by `ImagePositionPatient[2]`
   → `{ Z → all files at that slice (one per phase) }`.
2. **Rank phases** (`MFOrderByInstanceNumberStrategy::Apply`, line 109): within each Z-bucket, sort
   by `InstanceNumber`; the k-th file at every Z is assigned to **frame k** (`Sort()`, lines 183-197).
3. **Order slices** (`MFOrderByIPPStrategy::Apply`, line 120): for each frame, sort its one-per-Z
   slices with `gdcm::IPPSorter` (true geometry), then **reverse** to undo ITK's RAI default
   (line 144).

**Why this is correct for cardiac CTA:** the phase_detection analysis established that
`InstanceNumber` is **phase-major / slice-minor** (`InstanceNumber-1 = phase·N_slices + slice`).
At a *fixed* slice Z, the instance numbers across phases are
`{slice+1 + phase·N_slices}`, which sort into ascending phase order. So "k-th instance at each Z =
phase k" holds at every slice, and slices are then placed by geometry, not by instance number. This
matches the phase_detection recommendation exactly ("assemble slices by `ImagePositionPatient`, never
by `InstanceNumber` ascending"). **Do not regress this.**

> **Gap (robustness):** Frame assignment is purely positional (the k-th instance at each Z). It
> assumes every Z has exactly `N_phases` files. If the grid is broken (a slice is missing a phase),
> phases silently misalign across slices — there is no `N_files % N_slices == 0` check, no
> "every phase block has all slices" check, and no quarantine. The phase_detection report flags this
> as a required loader guard.

---

## 3. 4D assembly & metadata capture

[GuidedNativeImageIO.cxx:1104-1209](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx).

### 3.1 Per-frame 3D read
Each frame's file list is read with `itk::ImageSeriesReader` and **deep-copied** into a
`frameContainer[frame]` map (lines 1100-1115). One ITK series read per phase.

### 3.2 Geometry
First 3 dims (origin/direction/spacing/region) are taken from frame 1 (lines 1124-1134) and applied
to the 4D image. A RAS flip is applied if `direction(2,2)==1` (lines 1138-1145). Note this uses the
ITK series reader's computed spacing, which derives Z from `ImagePositionPatient` — consistent with
the "use geometric 0.3 mm spacing, not `SliceThickness`" guidance.

### 3.3 The hardcoded temporal axis — **primary gap**
[GuidedNativeImageIO.cxx:1165](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx):

```cpp
spacing4d[3] = 0.05; // hardcode 50ms for now, should be extracted from the images
origin4d[3]  = 0;    // ~line 1154
```

- The temporal axis is **uniform and fixed at 0.05** regardless of acquisition. There is no
  `%R-R`, no real `dt`, no `toffset`, no per-phase value. The developer comment already names the
  fix.
- Coincidentally `0.05` equals the normalized cardiac-cycle-fraction step for a clean 20-phase
  0–95 % study (the `i4_rs20` convention from the phase_detection reference) — but it is a literal,
  not derived, and is wrong for the 19-phase, 10-phase, or any non-uniform study.

### 3.4 Metadata capture — **only one frame, and the wrong one**
[GuidedNativeImageIO.cxx:1205-1209](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx) (the
single-volume DICOM-series path has the same pattern at :1046-1050):

```cpp
const SeriesReaderType::DictionaryArrayType *darr = reader->GetMetaDataDictionaryArray();
if (darr->size() > 0)
  m_NativeImage->SetMetaDataDictionary(*((*darr)[0]));
```

- `reader` is reused inside the per-frame loop, so after the loop it holds the **last** frame's
  dictionary array. `darr[0]` is thus *the first slice of the last phase* — not frame 0, and not a
  study-level merge. For tags that are constant across the series this is harmless; for anything
  phase-varying it is both lossy and inconsistent.
- **All other frames' dictionaries are dropped.** Per-phase `TriggerTime`/`NominalPercentage…` (when
  present) never reach memory.

---

## 4. In-memory 4D data model

- `ImageWrapper` holds `Image4DPointer m_Image4D` plus
  `std::vector<ImagePointer> m_ImageTimePoints` (3D views into the 4D buffer) and a
  `m_TimePointIndex` cursor
  ([ImageWrapper.h](../../itksnap/Logic/ImageWrapper/ImageWrapper.h), ~833-836).
- The full `MetaDataDictionary` lives on `m_Image4D` only. `CopyInformationFrom4DToTimePoint`
  ([ImageWrapper.cxx](../../itksnap/Logic/ImageWrapper/ImageWrapper.cxx), ~96-118) copies
  spacing/origin/direction to each 3D view but **not** the dictionary → per-time-point 3D images
  carry no metadata.
- `GenericImageData` exposes `GetNumberOfTimePoints()` and owns a `TimePointProperties`.

### 4.1 `TimePointProperties` — the existing per-frame store
[Logic/Framework/TimePointProperties.h](../../itksnap/Logic/Framework/TimePointProperties.h):

```cpp
class TimePointProperty : public itk::DataObject {
  std::string Nickname;   // user-assigned name
  TagList     Tags;       // free-form tag set
};
class TimePointProperties { std::map<unsigned int, SmartPtr<TimePointProperty>> m_TPPropertiesMap; };
```

- Already **per-time-point**, already **serialized to the workspace** (`Save`/`Load` →
  `TimePointProperties.TimePoints.TimePoint[n]`, see `TimePointProperties.cxx` ~92-113), already
  queryable by name from the CLI (`WorkspaceAPI.cxx` ~472-547).
- **No numeric fields** — no cardiac phase, no `%R-R`, no trigger time, no generic key/value bag.
  This is the cleanest extension point for cardiac-phase metadata.

### 4.2 Metadata surfacing to the user
- `MetaDataAccess` ([Logic/Common/MetaDataAccess.h/.cxx](../../itksnap/Logic/Common/MetaDataAccess.h))
  wraps the 4D image's dictionary: `GetKeysAsArray`, `GetValueAsString`, `MapKeyToDICOM`.
- `ImageInfoModel::UpdateMetadataIndex`
  ([GUI/Model/ImageInfoModel.cxx](../../itksnap/GUI/Model/ImageInfoModel.cxx) ~325-364) feeds a
  searchable DICOM tag table in the Image Information inspector. So whatever lands in the dictionary
  is already viewable — but today that's one frame's worth, with no phase axis.

### 4.3 Metadata propagation to derived images — dropped
- New segmentations (`InitializeToWrapper`) copy geometry only — **no dictionary**
  ([ImageWrapper.cxx](../../itksnap/Logic/ImageWrapper/ImageWrapper.cxx) ~1510-1536).
- `itk::ResampleImageFilter` usage (~347-365) does not preserve the dictionary.
- Consequence: a segmentation or resampled volume loses all study/cardiac metadata. (Relevant if we
  want exported segmentations to carry the same `%R-R` axis as the image they were drawn on.)

---

## 5. Write pipeline  *(rewritten 2026-06-27 for `master`)*

### 5.1 Supported formats & the 4D decision
Format table at
[GuidedNativeImageIO.cxx:107-128](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx)
(`name, pattern, can_write, can_store_orientation, can_store_float, can_store_short`):

| Format | Extensions | `can_write` |
|---|---|---|
| NiFTI | `nii.gz,nii,nia,nia.gz` | **true** |
| NRRD | `nrrd,nhdr` | **true** |
| MetaImage | `mha,mhd` | true |
| MINC | `mnc` | true |
| **NRRD Volume Sequence** | `seq.nrrd` | **true** ← *now writable* ([:122](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx), commit `01e02abd`) |
| **4D CTA DICOM Series** | — | **false** ← read-only |

The write decision
([ImageWrapper.cxx:2243](../../itksnap/Logic/ImageWrapper/ImageWrapper.cxx)):

```cpp
if (this->GetNumberOfTimePoints() > 1)
  Specialization::Write(m_Image4D.GetPointer(), filename, hints);  // single 4D file
else
  Specialization::Write(m_Image, filename, hints);                 // 3D file
```

A 4D layer is still written as **one 4D file** (good — not split per phase). **The write path is now
unified:** `ImageWrapperPartialSpecializationTraitsCommon::Write` delegates to
`GuidedNativeImageIO::SaveImage()`
([ImageWrapper.cxx:300](../../itksnap/Logic/ImageWrapper/ImageWrapper.cxx)), described in the commit
as *"the single authoritative write path for all formats saved from the GUI."* This matters: it gives
us **one hook** to stamp cardiac/non-PHI metadata onto every export.

### 5.2 The `.seq.nrrd` writer (new on `master`) — container solved, content not
`SaveNrrdSequence<TImageType>()`
([GuidedNativeImageIO.cxx:1553](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx)) hand-writes
the NRRD header + binary payload (ITK's generic writer can't produce the seq header). It is
intercepted for `FORMAT_NRRD_SEQ` in both `SaveImage()`
([:1694](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx), via `if constexpr (ImageDimension==4)`)
and `DoSaveNative()` ([:1673](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx)). What it
emits:

```
NRRD0005
type: <int16/uint16/…>           # mapped from native pixel type
dimension: 4
space: left-posterior-superior   # LPS, ITK/SNAP convention
sizes: T X Y Z                    # T first (fastest); buffer reordered from ITK X-fastest
space directions: none (…) (…) (…)   # list axis = "none"; 3 spatial = spacing·direction
kinds: list domain domain domain
endian: <detected>  encoding: raw
labels: "frame" "" "" ""
space origin: (…)
measurement frame: (1,0,0) (0,1,0) (0,0,1)
axis 0 index type:=numeric
axis 0 index values:=0 1 2 … T-1      ◄── frame ORDINALS, not %R-R   (line 1634)
```

- ✅ Produces a **valid, Slicer-readable** volume sequence with a first-class frame axis, correct
  LPS geometry, and correct buffer reordering (ITK X-fastest → NRRD T-fastest).
- ❌ **Frame axis carries no cardiac meaning:** `axis 0 index values` are `0…T-1`, not the `%R-R`
  values. (Note: the implementation uses NRRD's native `axis N index values` mechanism, which is
  actually *cleaner* than the `MultiVolume.FrameLabels` convention in
  [metadata_reference §4.3](metadata_reference.md#43-slicer-volume-sequence-seqnrrd--first-class-non-uniform-axis)
  — but the **values** are the problem, not the mechanism.)
- ❌ **No cardiac/non-PHI metadata** is written (no HR, no `%R-R` array, no scanner/protocol block).
- ⚠️ Writes the **native stored pixels**; HU rescale (slope/intercept) is whatever the geometry/pixel
  type implies — verify HU fidelity on round-trip.

### 5.3 What survives a write today (NIfTI / NRRD)
- **Geometry:** spacing/origin/direction for all 4 dims (so NIfTI `pixdim[4]` = `m_Image4D`
  spacing[3], i.e. the hardcoded `0.05`). `toffset`, `xyzt_units` left at ITK defaults; `descrip`
  unused.
- **Arbitrary metadata:** `itk::ImageFileWriter` uses `image->GetMetaDataDictionary()` automatically,
  **but ITK-SNAP never populates the dictionary on write**, so nothing custom is emitted. Plain NRRD
  *could* carry `key:=value` pairs (survives round-trip), but no keys are set. NIfTI largely cannot
  carry arbitrary keys anyway.

### 5.4 Net writing gap (post-master)
The `.seq.nrrd` **container** is solved; the **content** is not. There is still **no path** to write
a *meaningful* cardiac phase axis or non-PHI metadata in any format:
- `.seq.nrrd`: writer exists but emits ordinal frame indices and no metadata (§5.2).
- NIfTI: only a scalar uniform `pixdim[4]`; no per-frame `%R-R`, no sidecar, no extension.
- NRRD: no custom keys written.

And note the upstream cause: even a perfect writer has **nothing to write**, because the read path
discards the phase axis (G1/G2). Fixing the writers is gated on fixing the reader.

---

## 6. Summary of gaps (→ requirements for the plan)

| # | Gap | Location (`master @ 28f4ee45`) | Severity | Status |
|---|---|---|---|---|
| G1 | Temporal axis hardcoded `0.05`; no real `dt`/`%R-R`/`toffset` | GuidedNativeImageIO.cxx:1165 | **High** | open |
| G2 | Only one (last) frame's DICOM dict kept; per-phase metadata dropped | GuidedNativeImageIO.cxx:1205-1209 (also :1046-1050) | **High** | open |
| G3 | No cardiac-phase data model (per-TP numeric fields) | TimePointProperties.h | **High** | open |
| G4 | Writer preserves no *meaningful* phase axis. `.seq.nrrd` **writer now exists** (`SaveNrrdSequence`, :1553) but emits ordinal frame indices `0…T-1` (:1634) + no metadata; NIfTI scalar `pixdim[4]` only; no NRRD custom keys | format table :122 + write path | **High** | **narrowed** — container done, content open |
| G5 | No grid validation / quarantine; positional phase assignment can silently misalign | MultiFrameDicomSeriesSorter.cxx:183-197 | Medium | open |
| G6 | 4DCTA detection = any Siemens/GE CT dir (no multi-phase check) | GuidedNativeImageIO.cxx:2210-2219 | Medium | open |
| G7 | No curated non-PHI metadata block; dictionary not propagated to derived/segmentation images | ImageWrapper.cxx (InitializeToWrapper, Resample) | Medium | open |
| G8 | `%R-R` derivable from `SeriesDescription` but never parsed | (read path) | Medium | open |

**What is already correct and must be preserved:** the group-by-Z / rank-by-InstanceNumber /
order-slices-by-geometry pipeline (§2); writing 4D as a single file (§5.1); the **unified
`SaveImage()` write path** and the working `.seq.nrrd` container/geometry/buffer-reordering (§5.2);
the existence of a per-time-point, workspace-serialized property store (§4.1); a searchable metadata
inspector (§4.2).

> **`master` refactor note (commit `2ad9e198`):** shared per-layer metadata members were consolidated
> into `WrapperBase` — `m_CustomNickname`/`m_Tags` now live in
> [WrapperBase.h:124-125](../../itksnap/Logic/ImageWrapper/WrapperBase.h) (`GetCustomNickname()` at
> :43), while `WriteMetaData`/`ReadMetaData` remain in the templated `ImageWrapper`
> ([ImageWrapper.cxx:2602/2617](../../itksnap/Logic/ImageWrapper/ImageWrapper.cxx)). So the curated
> non-PHI block + cardiac model (plan Phase 0) should attach at the **`WrapperBase`** level.
