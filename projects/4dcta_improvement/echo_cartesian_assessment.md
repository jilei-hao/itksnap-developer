# Philips Cartesian 4D Echo — Cardiac I/O Assessment

**Date:** 2026-06-30.
**Question:** can the 4D CTA cardiac-I/O improvements be applied to the Philips Cartesian 4D echo
(TEE) path in ITK-SNAP?
**Sample:** `/Users/jileihao/data/avrp/4d_echo_cartesian_dicom/bav25/bav25_anon.dcm`.

Short answer: **partly, and the echo path is already ahead of CT on the one thing CT got wrong** (it
uses the real frame time, not a hardcoded value). The transferable wins are (1) writing the temporal
axis explicitly to the export formats, (2) extending the non-PHI curation keep-list to US/echo tags,
and (3) a small read-robustness guard. The `%R-R` phase axis itself does **not** apply — echo is a
time cine, not an ECG-gated reconstruction.

> **Status (2026-06-30): implemented** on itksnap `feature/cardiac-io` (commit `2dc3d470`).
> Items #1, #2, #3, #5 below are done and verified; #4 (GUI) is deferred (the unverifiable piece).
> A modality-agnostic frame axis (`ITKSNAP_FrameAxis_Values/Unit/Label`) is now filled on read for
> both modalities (CT: %R-R/"%"; echo: elapsed time/"ms") and emitted by the writers. **Verified:**
> `bav25` → `.seq.nrrd` carries `axis 0 index values:=0 109.2 … 1965.6`, `units:=ms`, `labels "time"`;
> `.nrrd` export keeps `FrameTime` + covariates and drops `PatientName`; CT (`bavcta005`) output is
> unchanged (still emits the legacy `%R-R` key). See [progress_summary.md](progress_summary.md).

---

## 1. The data (`bav25_anon.dcm`)

A **single multi-frame DICOM file** (131.8 MB), not a directory of files like 4D CTA.

| Property | Value |
|---|---|
| Modality | `US` |
| Manufacturer | `PMS QLAB Cart Export` |
| SOPClassUID | `1.2.840.113543.6.6.1.3.10002` (Philips private 3D echo) |
| ImageType | `DERIVED\PRIMARY` |
| Pixel | 8-bit `MONOCHROME2` (uint8) |
| **Standard** Rows×Cols×Frames | 176 × 176 × **19** |
| **True 4D volume** | **176 (W) × 176 (H) × 224 (D) × 19 (T)** = 131,833,856 bytes = the pixel data exactly |
| Voxel spacing | X ≈ 0.62 mm, Y ≈ 0.64 mm, Z ≈ 0.533 mm |
| **Frame time** | `FrameTime (0018,1063)` = **109.2 ms** (uniform; 19 frames ≈ 2.07 s) |
| Cardiac/ECG tags | **all absent** (`HeartRate`, `NominalInterval`, Low/High `RRValue`, `TriggerTime`) |
| PHI | anonymized (`PatientName=XXXX…`, `PatientID=000000000`) but patient tags still present |

**The trick:** the standard tags describe only `176×176×19`; the **third spatial dimension (224) and
its spacing live in Philips private tags** `(3001,1001)=224` (depth) and `(3001,1003)=0.0533` cm
(ΔZ). X/Y spacing come from top-level US calibration `(0018,602c)/(0018,602e)` (cm). So the real 4D
volume is reconstructed from a mix of standard + private + US tags.

**Key difference from 4D CTA:** the fourth axis here is **real elapsed time (ms)**, a free-running
cine — *not* a `%R-R` cardiac phase. There is no ECG gating metadata, so there is no `%R-R` to
recover; the meaningful axis is the frame time, which is present and exact.

---

## 2. ITK-SNAP's existing echo path (`FORMAT_ECHO_CARTESIAN_DICOM`)

`Logic/ImageWrapper/GuidedNativeImageIO.cxx` — detection at the `GuessFormatForFileName` US branch
(Manufacturer uppercased == `PMS QLAB CART EXPORT`); header decode and data read in the
`FORMAT_ECHO_CARTESIAN_DICOM` branches.

What it does (verified against `bav25`):
- **Decodes the 4D dims correctly** — `[width(0028,0011), height(0028,0010), depth(3001,1001),
  numVolumes(0028,0008)] = [176,176,224,19]`; pixel-data length matches exactly.
- **Sets spacing from real tags** — X/Y from `(0018,602c)/(0018,602e)`×10, Z from `(3001,1003)`×10,
  and **the time axis from `FrameTime` (109.2 ms)**. ✅ *The CT bug (hardcoded `spacing4d[3]=0.05`)
  does not exist here — echo already carries a real temporal spacing.*
- Direction hardcoded **LAS**, origin 0 (echo has no patient-frame geometry).
- **Builds a MetaDataDictionary** — custom keys `Depth` / `Physical Delta Z` for the private tags,
  plus standard `gggg|eeee` public tags (including the `0010,*` patient tags).

So reading is in good shape. The gaps are on the *metadata-preservation / export* side — exactly the
area the 4D CTA work targeted.

---

## 3. Which 4D CTA improvements transfer?

| 4D CTA improvement | Echo? | Notes |
|---|---|---|
| Replace hardcoded temporal spacing | **already correct** | echo uses `FrameTime` (109.2 ms) |
| `%R-R` phase axis from `SeriesDescription` | **N/A** | echo is a time cine; no gating, no `%R-R` |
| Carry axis as `ITKSNAP_*` dict keys | **yes — desirable** | store the per-frame **time** axis (`0, 109.2, …` ms) so writers can emit it |
| `.seq.nrrd` writes axis index values | **yes** | currently echo→seq.nrrd would write **ordinal** frame indices; should write frame **time** + `units:=ms` |
| NIfTI `pixdim[4]` + JSON sidecar | **partly already** | `pixdim[4]` = 109.2 ms already; a sidecar could record the time axis + units explicitly |
| Per-time-point typed model + GUI field | **yes** | generalize the "Cardiac phase" field to show frame **time** (e.g. `873 ms (frame 8/19)`) |
| Non-PHI export curation | **yes — but keep-list is CT-specific** | echo export hits the curation (its dict has `0010,*`), which correctly drops PHI, **but the allow-list also drops echo tags** (`FrameTime 0018,1063`, US `0018,602c/602e`) → extend the keep-list |
| Grid validation/quarantine | **N/A** | single file; the echo analog is a `len == W·H·D·T` pixel-data sanity check |

---

## 4. Recommended improvements (scoped, prioritized)

**The unifying idea:** the 4D CTA work introduced a per-time-point *cardiac axis* (a value + unit per
frame). Echo has the same shape of data with a different unit — **`%` (R-R) for CT, `ms` (frame
time) for echo.** Generalize the existing mechanism to "a labeled time/phase axis (values + unit)"
and echo gets the same multi-format preservation for free.

1. **Capture an explicit time axis on echo read** *(small)* — mirror `ITKSNAP_Cardiac_RRPercent`:
   write the per-frame times (`0, 109.2, 218.4, …`) + a unit key (`ms`) into the image dictionary
   during the echo read (derive from `FrameTime × frame index`).

2. **Emit it in the writers** *(small, reuses existing code)* —
   - `.seq.nrrd`: use those values as `axis 0 index values` with `axis 0 index units:=ms` (instead
     of ordinals) — the same `SaveNrrdSequence` branch, just keyed on the generalized axis.
   - NIfTI: already gets `pixdim[4]`; optionally add the time axis to the JSON sidecar.

3. **Extend the non-PHI curation keep-list to US/echo** *(small)* — add `FrameTime (0018,1063)`,
   `CineRate (0018,0040)`, US `PhysicalDeltaX/Y (0018,602c/602e)`, and the modality/transducer tags
   so curated echo exports keep their relevant non-PHI metadata. (Geometry already rides the ITK
   image, so spacing is safe regardless; this is about the metadata record.) PHI dropping already
   works.

4. **GUI: generalize the "Cardiac phase" field** *(small-medium)* — show frame **time** for echo
   (`873 ms (frame 8/19)`) vs `%R-R` for CT. One read-only property that formats by available axis.

5. **Echo read robustness** *(small)* — the spacing read assumes top-level `(0018,602c)/(0018,602e)`
   exist; if a future export omits them the spacing vector is left short and `SetSpacing` reads out
   of bounds. Add a presence guard + sensible default, and a `len == W·H·D·T` pixel-data check
   (the echo analog of grid validation).

**Not applicable:** `%R-R` recovery, `SeriesDescription` range parsing, the directory/grid sorter,
and the hardcoded-temporal-spacing fix — these are CT-specific or already handled.

---

## 5. Effort / risk

All five are small, localized changes (mostly in the echo branches of `GuidedNativeImageIO.cxx`, the
shared keep-list, and the one GUI property). The highest-value, lowest-risk items are **#3
(keep-list)** and **#1+#2 (time axis → writers)**. #4 (GUI) needs the same interactive verification
the CT field still awaits. No format/architecture changes; the echo container and reader already
work.

> Cross-refs: [improvement_plan.md](improvement_plan.md) (CT plan),
> [metadata_reference.md](metadata_reference.md) (keep-list + HIPAA), and the shipped CT behavior in
> `itksnap/Documentation/Developer/Cardiac4DCTA_IO.md`.
