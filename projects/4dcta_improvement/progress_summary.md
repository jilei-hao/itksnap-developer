# 4D CTA Cardiac I/O — Progress Summary

**As of 2026-06-29.** itksnap work branch **`feature/cardiac-io`**; wrapper **`main`** tracks it.

This summarizes what was built across the session. For design rationale see
[analysis_existing_logic.md](analysis_existing_logic.md), [metadata_reference.md](metadata_reference.md),
and [improvement_plan.md](improvement_plan.md). For a developer description of the shipped behavior
see the feature doc in the itksnap repo: `itksnap/Documentation/Developer/Cardiac4DCTA_IO.md`.

---

## Goal (all three met)

1. **Keep cardiac phase information** — the `%R-R` axis is recovered on read and preserved.
2. **Keep important non-PHI metadata** — research metadata is curated and re-emitted; PHI is dropped.
3. **Writable to multiple formats** — `.seq.nrrd`, `.nii.gz` (+ sidecar), `.nrrd`.

## What was delivered

| Capability | Status | Notes |
|---|---|---|
| Recover `%R-R` on 4D CTA read | ✅ | parsed from `SeriesDescription` range + phase count; replaces the hardcoded `0.05` temporal spacing |
| Carry phase axis in-memory | ✅ | `ITKSNAP_Cardiac_*` keys on the image `MetaDataDictionary` |
| Typed per-time-point model | ✅ | `TimePointProperty.RRPercent/Exact`; workspace `FormatVersion` 2 |
| `.seq.nrrd` export with `%R-R` | ✅ | non-uniform `axis 0 index values` (+ units + keys) |
| `.nii.gz` export | ✅ | `pixdim[4]` fraction step + `<name>.json` sidecar with the full array |
| `.nrrd` export | ✅ | `ITKSNAP_Cardiac_*` keys via the dictionary (free) |
| Non-PHI curation on export | ✅ | export-only allow-list; age top-coded ≥90 (HIPAA Safe Harbor) |
| Float (non-identity) write path | ✅ | routed through `SaveImage` so it also curates + sidecars |
| Grid validation / quarantine | ✅ | ragged DICOM grid → clear `IRISException` (verified: −1 file → "19 frames but 20 expected") |
| `NumberOfPhases` in seq header | ✅ | all four cardiac keys now round-trip through `.seq.nrrd` |
| GUI "Cardiac phase" field | ⏳ | implemented + compiles + couples; **interactive visual check pending** |

## Verification

- **Headless, end-to-end (verified):** read → `%R-R` derivation → in-memory model → write, using a
  throwaway driver against the AVRP cohort:
  - `bavcta005` (clean 20-phase): `%R-R = 0 5 … 95`, `exact=1`, `spacing(t)=0.05`.
  - `bavcta007` (ambiguous 10-phase): non-uniform `%R-R = 0 10.56 … 95`, `exact=0`, `spacing(t)=0.1056`.
  - `.seq.nrrd` write→read round-trip preserves the cardiac keys.
  - `.nii.gz` writes `pixdim[4]=0.05` + a correct JSON sidecar.
  - `.nrrd` export **drops** name/ID/dates/institution/accession/private-CSA and **keeps** the
    research metadata + covariates + `%R-R`.
- **Build:** full `ITK-SNAP` target builds clean (Release, arm64) and runs; it loaded `bavcta005`
  (20 phases) with no errors.
- **Pending:** a visual confirmation of the GUI "Cardiac phase" field. The screenshot path was
  blocked in this environment (computer-use access grant timed out; the `screencapture` CLI lacked
  Screen Recording permission), so the field — which compiles and is correctly coupled — still needs
  eyes on it: Layer Inspector → General → 4D time-point section, scrub the slider, expect
  `0 → 5 → … → 95% R-R`.

## Commit stack

**itksnap (`feature/cardiac-io`):**
- `0e5168ad` — read + `.seq.nrrd` `%R-R` (P0 carrier, P1 read extraction, P3.3 writer)
- `7b51378a` — NIfTI `pixdim[4]` + JSON sidecar (P3.1)
- `7a1c2489` — non-PHI export curation / allow-list (requirement 2)
- `c1346b9d` — route the float write path through `SaveImage`
- `a0f9d6f0` — per-time-point typed cardiac fields + GUI field (P2)
- `dec2a2f2` — developer doc `Documentation/Developer/Cardiac4DCTA_IO.md`
- `a359b7bd` — P4: grid validation/quarantine + `NumberOfPhases` in seq header
- `2dc3d470` — **4D echo (Philips Cartesian):** modality-agnostic frame axis (CT %R-R / echo ms) +
  US/echo non-PHI keep-list + echo read guards (see [echo_cartesian_assessment.md](echo_cartesian_assessment.md))

**wrapper (`main`):** `223a7c1` (track branch + add project docs) → `cc04988` → `5481c29` →
`dd14216` → `0a36975` → `b9118c3` (pointer bumps + project-doc updates), + this summary.

All itksnap commits are pushed to `origin/feature/cardiac-io`; wrapper `main` is pushed to origin.

## Build environment note (this machine)

Xcode updated 26.2 → 26.5, deleting `MacOSX26.2.sdk`. The local VTK/ITK installs and build caches had
that path baked in, breaking CMake reconfigure. Fixed by replacing `MacOSX26.2.sdk` → `MacOSX.sdk` in
`lib/{vtk,itk}/install/.../*-targets.cmake` and the build caches (backups `*.bak26`). The cleaner
permanent fix (needs sudo, also repairs the greedy/cmrep builds):
`sudo ln -s MacOSX.sdk "<Xcode>/.../SDKs/MacOSX26.2.sdk"`. A VTK/ITK rebuild reverts the patched files.

## What's left

- **Interactive GUI confirmation** of the "Cardiac phase" field — the only functional item left;
  blocked by this environment's screenshot layer (needs eyes on the running app).
- Tighten 4DCTA detection (currently "any Siemens/GE CT directory") — benign today: a single-phase
  series simply loads as a 1‑time‑point image.
- 4D non-identity float export is current-time-point only (`FloatImageType` is 3D); moot for short CT.

Done since the first summary: grid validation/quarantine for non-rectangular grids and
`ITKSNAP_Cardiac_NumberOfPhases` in the seq header (both `a359b7bd`, verified).
