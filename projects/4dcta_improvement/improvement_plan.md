# 4D CTA Reading/Writing Improvement Plan — ITK-SNAP

**Date:** 2026-06-26
**Goal:** Make ITK-SNAP's 4D cardiac CTA pipeline (1) preserve the **cardiac phase axis**,
(2) preserve **as much important non-PHI metadata as possible**, and (3) hold both in a
**format-agnostic model** that can be re-written to `.nii.gz`, `.nrrd`, and Slicer `.seq.nrrd`.

Reads on: [analysis of existing logic](analysis_existing_logic.md) ·
[metadata reference](metadata_reference.md).

> **Implementation status (2026-06-28)** — itksnap branch `feature/cardiac-io` (HEAD `7b51378a`),
> all in `Logic/ImageWrapper/GuidedNativeImageIO.cxx`:
> - ✅ **P0** carrier (dictionary keys `ITKSNAP_Cardiac_*` + helpers) — `0e5168ad`
> - ✅ **P1** read extraction (`%R-R` from `SeriesDescription`; temporal axis derived) — `0e5168ad`
> - ✅ **P3.3** seq.nrrd writer emits `%R-R` (non-uniform) — `0e5168ad`
> - ✅ **P3.1** NIfTI `pixdim[4]` + JSON sidecar — `7b51378a`
> - ✅ **P3.2** plain `.nrrd` keys — free via the dictionary (verified, no code)
> - All verified end-to-end on AVRP bavcta005 (clean 20-phase) + bavcta007 (ambiguous 10-phase).
> - 🔴 **non-PHI curation (req. 2)** — plain `.nrrd` dumps the **entire** DICOM dict incl. `0010|*`
>   patient tags + dates (PHI leak on raw data; pre-existing ITK behavior). Emit only the keep-list.
> - ⬜ **P2** typed `TimePointProperties` cardiac fields + UI/workspace surfacing
> - ⬜ **P4** grid validation/quarantine, detection tightening; **float-mapping write path** still
>   bypasses `SaveNrrdSequence`; `.seq.nrrd` read-side doesn't repopulate the cardiac key

---

## 1. Design spine

Introduce **one in-memory cardiac/metadata model** that the reader populates and every writer
consumes. This decouples "what we extracted" from "how each format serializes it" — the key to
requirement (3).

```
                ┌─────────────────────────── read ───────────────────────────┐
DICOM 4DCTA ──► extract phase axis (tags OR structural) + curate non-PHI block
                                         │
                                         ▼
                    ┌──────────────────────────────────────────┐
                    │  Cardiac4DMetadata  (format-agnostic)      │
                    │   • per-TP: phase_index, rr_percent, dt…   │  ◄── lives on the layer,
                    │   • study: HR, n_phases, rr_source, …      │      serialized in workspace
                    │   • curated non-PHI key/value block        │
                    └──────────────────────────────────────────┘
                                         │
        ┌────────────────┬──────────────┼───────────────┬────────────────┐
        ▼                ▼              ▼                ▼                ▼
   NIfTI hdr+         NRRD custom    .seq.nrrd      workspace        Image Info
   JSON sidecar         keys        FrameLabels    (.itksnap)        inspector UI
```

The model attaches to the **layer** (image wrapper) and reuses/extends the existing per-time-point
`TimePointProperties` (already serialized to the workspace and queryable from the CLI).

---

## 2. Phased plan

Each phase is independently shippable and testable. Phases 1–2 satisfy "keep the info"; Phase 3
satisfies "write it back"; Phase 4 hardens; Phase 5 is optional polish.

### Phase 0 — Data model (foundation)
**Outcome:** a place to put cardiac + non-PHI metadata.

- **0.1** Extend `TimePointProperty`
  ([Logic/Framework/TimePointProperties.h](../../itksnap/Logic/Framework/TimePointProperties.h))
  with numeric cardiac fields: `phase_index`, `rr_percent`, `rr_percent_exact`, `trigger_time_ms`,
  `nominal_interval_ms`. Keep `Nickname`/`Tags`. Update `Save`/`Load`
  (TimePointProperties.cxx ~92-113) and bump its `FormatVersion`.
- **0.2** Add a study-level **`Cardiac4DMetadata`** holder on the image layer (or on
  `TimePointProperties` as a sibling): `heart_rate_bpm`, `n_phases`, `rr_source`
  (`dicom_tag|series_description|manual|none`), `rr_unit`, and a `phase_axis_uniform` flag.
- **0.3** Add a **curated non-PHI key/value block** (`std::map<std::string,std::string>` or a small
  typed struct) for the §3.1 keep-list of [metadata_reference](metadata_reference.md). On `master`,
  shared per-layer metadata members were consolidated into **`WrapperBase`** (commit `2ad9e198`;
  `m_CustomNickname`/`m_Tags` at [WrapperBase.h:124-125](../../itksnap/Logic/ImageWrapper/WrapperBase.h))
  — attach the new block there so all layer types share it. Serialize it in
  `ImageWrapper::WriteMetaData`/`ReadMetaData`
  ([ImageWrapper.cxx:2602/2617](../../itksnap/Logic/ImageWrapper/ImageWrapper.cxx)), which today only
  stores Alpha/Sticky/Nickname/Tags.

*Why first:* every later phase reads/writes this; defining it up front avoids churn.

### Phase 1 — Read-side extraction (the core of "keep cardiac phase info")
**Outcome:** loading a 4DCTA populates the model; nothing is silently invented.

- **1.1 Replace the hardcoded temporal axis.**
  [GuidedNativeImageIO.cxx:1165](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx)
  (`spacing4d[3] = 0.05`) → derive:
  - If per-frame `TriggerTime`/`NominalPercentageOfCardiacPhase` exist → use real `dt` (and set
    `origin4d[3] = toffset`).
  - Else (AVRP case) → derive `%R-R` via the structural recipe (parse `SeriesDescription` range +
    `N_phases`); set `pixdim[4]` to the fraction step `(end-start)/100/(N_phases-1)` and
    `origin4d[3] = start/100`.
  - Else → leave a sentinel and set `rr_source = none` (don't fabricate a value).
- **1.2 Capture per-frame metadata for ALL frames**, not just one.
  [GuidedNativeImageIO.cxx:1205-1209](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx): inside
  the per-frame loop (~1118-1132) pull each frame's dictionary (`reader->GetMetaDataDictionaryArray()`
  is valid *per Update*), extract the cardiac tags, and fill the per-TP model. Also fix the latent
  bug where the retained study dict is the *last* frame's, not frame 0. (Same single-frame pattern
  also exists in the single-volume DICOM-series path at :1046-1050.)
- **1.3 Compute the `%R-R` axis** from `SeriesDescription` when tags are absent; mark
  `rr_percent_exact=false` and `phase_axis_uniform=false` for the ambiguous 10-phase case.
- **1.4 Curate the non-PHI block** (§3.1 keep-list), explicitly excluding the §3.2 PHI/drop-list so
  we never carry PHI forward on later export.
- **1.5 `N_phases` is per-study** = `N_files / N_distinct_Z`. Don't hardcode 20. (The sorter already
  computes the grouping; expose its counts.)

### Phase 2 — Propagation & visibility
**Outcome:** the metadata is reachable in UI/CLI and survives a workspace round-trip.

- **2.1** Workspace round-trip: confirm the extended `TimePointProperties` + `Cardiac4DMetadata`
  save/load through `SNAPRegistryIO`. (Per-TP store already serializes;
  [WorkspaceAPI.cxx](../../itksnap/Logic/WorkspaceAPI/WorkspaceAPI.cxx) ~472-547 already prints
  per-TP nickname/tags — extend the listing to show `%R-R`.)
- **2.2** Surface in the **Image Information inspector**: add `%R-R`, phase index, HR to the metadata
  table ([GUI/Model/ImageInfoModel.cxx](../../itksnap/GUI/Model/ImageInfoModel.cxx) ~325-364). Cheap
  win — the inspector already renders dictionary rows.
- **2.3** (Optional) Show `%R-R` next to the time-point cursor / scrubber so users see phase, not just
  frame N.
- **2.4** Decide propagation to derived images: at minimum, copy the curated non-PHI block + phase
  axis to **exported segmentations** so a saved seg carries the same `%R-R` as its parent
  (InitializeToWrapper / resample paths currently drop the dictionary —
  [analysis §4.3](analysis_existing_logic.md)).

### Phase 3 — Write-side (the core of "write to various formats")
**Outcome:** the phase axis + curated metadata are emitted faithfully per format.

> **Updated 2026-06-27 for `master`.** A `.seq.nrrd` **writer already exists** (`SaveNrrdSequence`,
> [GuidedNativeImageIO.cxx:1553](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx)) and the
> write path is **unified** through `GuidedNativeImageIO::SaveImage()`
> ([ImageWrapper.cxx:300](../../itksnap/Logic/ImageWrapper/ImageWrapper.cxx)). So 3.3 changes from
> "build a writer" to "**extend the existing writer**", and 3.4 has a single, clean hook. Net: Phase 3
> effort drops.

- **3.3 (do this first) — make the existing `.seq.nrrd` writer carry cardiac `%R-R`.** Extend
  `SaveNrrdSequence` ([GuidedNativeImageIO.cxx:1553](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx)):
  replace the ordinal `axis 0 index values:=0 1 2 … T-1`
  ([:1634](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx)) with the actual `%R-R` values
  from the Phase-0 model (non-uniform OK — this is exactly what the `list` axis is for), and append
  curated key-value metadata (`AVRP_RR_percent:=…`, `HeartRateBpm:=…`, scanner/protocol block, an
  `axis 0 index units:=%` style hint). NRRD `:=` keys round-trip losslessly. This is now the
  **lowest-effort** path to fully satisfying requirements (1)+(2)+(3) and the best fit for the
  non-uniform 10-phase case. *(The writer already gets LPS geometry and buffer reordering right —
  don't touch those.)*
- **3.4 Stamp curated metadata onto every export via the unified `SaveImage()` hook.** `SaveImage`
  ([:1686](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx)) is now the single authoritative
  write path; populate `image->GetMetaDataDictionary()` there from the curated keep-list (no PHI
  laundering) before the `itk::ImageFileWriter::Update()` call, so NRRD `key:=value` metadata is
  emitted for *plain* `.nrrd` too. For `.seq.nrrd`, route the same curated block into the manual
  header writer (3.3).
- **3.1 NIfTI** (`.nii.gz`): set `pixdim[4]` = fraction step, `toffset` = start fraction,
  `xyzt_units` t-bits; **write a JSON sidecar** (`<name>.json`) with the full `%R-R` array + curated
  metadata (authoritative). Optionally add a JSON header extension (ecode 6) too. Hook in the NIfTI
  branch reached from `SaveImage()`.
- **3.2 Plain NRRD** (`.nrrd`): falls out of 3.4 — the curated `key:=value` block (incl.
  `AVRP_RR_percent`) is written via the populated `MetaDataDictionary`. Lowest-effort faithful in-file
  option for tools that don't read the seq format.

### Phase 4 — Robustness & correctness
- **4.1 Grid validation / quarantine:** enforce `N_files % N_slices == 0` and "every phase block has
  all slices" in the sorter ([MultiFrameDicomSeriesSorter.cxx:183-197](../../itksnap/Common/MultiFrameDicomSeriesSorter.cxx));
  on violation, warn + quarantine (don't crash, don't silently misalign phases).
- **4.2 Tighten 4DCTA detection:** require multi-phase evidence (`N_files > N_distinct_Z`, or a
  `FUNC`/`%`-style `SeriesDescription`) before classifying as `FORMAT_DICOM_DIR_4DCTA`
  ([GuidedNativeImageIO.cxx:2210-2219](../../itksnap/Logic/ImageWrapper/GuidedNativeImageIO.cxx)), so
  ordinary Siemens/GE CT isn't forced through the 4D assembler.
- **4.3 Multi-beat / arrhythmia flag:** the non-monotonic `AcquisitionTime` wrap is the signal
  (phase_detection §2.4). Compute a per-study phase-time dispersion metric and flag outliers in the
  non-PHI block rather than silently averaging.
- **4.4 Direction/`%R-R` provenance:** record `rr_source` and the phase-direction assumption so
  downstream knows whether `%R-R` is measured or inferred.

### Phase 5 — Optional polish
- Round-trip parity tests (read AVRP → write `.seq.nrrd` → re-read → identical axis).
- `c3d`/CLI surfacing of the phase axis.
- Re-derive `%R-R` direction from a motion curve once a detector exists (cross-project with
  phase_detection Step 3).

---

## 3. File-by-file change map

Line numbers are `master @ 28f4ee45`.

| File | Change |
|---|---|
| `Logic/ImageWrapper/WrapperBase.h/.cxx` | Home for the curated non-PHI block + `Cardiac4DMetadata` (members consolidated here by `2ad9e198`; `m_CustomNickname`/`m_Tags` at WrapperBase.h:124-125) (P0) |
| `Logic/Framework/TimePointProperties.h/.cxx` | Add cardiac numeric fields; update Save/Load, bump FormatVersion (P0, P1) |
| `Logic/ImageWrapper/GuidedNativeImageIO.cxx` | Derive temporal axis (:1165); per-frame metadata capture (:1205-1209, :1046-1050); `%R-R` from SeriesDescription; tighten detection (:2210-2219); **extend `SaveNrrdSequence` to emit `%R-R` + metadata (:1553, :1634)**; stamp curated dict in `SaveImage` (:1686); `can_write` for seq.nrrd already `true` (:122) (P1, P3, P4) |
| `Common/MultiFrameDicomSeriesSorter.cxx` | Grid validation + quarantine (:183-197) (P4) |
| `Logic/ImageWrapper/ImageWrapper.cxx` | Serialize curated block in WriteMetaData/ReadMetaData (:2602/2617); 4D write decision unchanged (:2243); unified Write→SaveImage already in place (:300); propagate to derived images (~InitializeToWrapper) (P0, P2, P3) |
| `GUI/Model/ImageInfoModel.cxx` | Surface `%R-R`/phase/HR rows (~325-364) (P2) |
| `Logic/WorkspaceAPI/WorkspaceAPI.cxx` | Extend per-TP listing with `%R-R` (~472-547) (P2) |
| `Testing/` | DICOM grid fixtures + read/write round-trip tests, incl. `.seq.nrrd` `%R-R` round-trip (P4) |

---

## 4. Testing strategy

- **Unit:** `%R-R` derivation from each AVRP `SeriesDescription`; structural phase/slice decomposition
  bijection; grid-validation rejects a deliberately broken grid.
- **Read fixtures:** a tiny synthetic `N_phases×N_slices` DICOM grid (don't commit patient data);
  optionally point an integration test at `/Users/jileihao/data/avrp/4DCTA_anon/` locally.
- **Write round-trip:** read AVRP study → write `.seq.nrrd` and `.nii.gz`+sidecar → re-read → assert
  identical `%R-R` axis, geometry, and HU calibration. Compare NIfTI output's `pixdim[4]`/`toffset`
  against the existing `i4_rs20` convention.
- **Regression guard:** confirm the slice/phase ordering (analysis §2) is unchanged — load an AVRP
  study and verify slice geometry + phase order match the pre-change output.
- **Leak canary:** run the macOS leak canaries (`PreferencesDialog`, `RandomForestBailOut`) per
  CLAUDE.md after touching ImageWrapper.

---

## 5. Open decisions (for the user, before implementation)

1. **Format priority** — the `.seq.nrrd` **writer already exists on `master`** (it just lacks `%R-R`
   + metadata). Recommendation: **extend `.seq.nrrd` first** (smallest diff, fully satisfies all three
   requirements for the non-uniform case — Phase 3.3), then add NIfTI+sidecar for the segflow4d
   pipeline. Plain `.nrrd` keys fall out of the shared `SaveImage` metadata hook (3.4). Confirm this
   ordering.
2. **Surface area** — GUI/workspace only, or also expose via `c3d`/CLI?
3. **Non-PHI scope** — keep research covariates (age/sex/size/weight) by default, or exclude them to
   be conservative?
4. **Phase-direction & ambiguous 10-phase `%R-R`** — adopt the phase_detection assumptions
   (block 0 = lowest `%R-R`; treat 10-phase as `0,10,…,90`) as defaults, surfaced as editable?
5. **Sidecar vs in-file** — for NIfTI, is a `.json` sidecar acceptable downstream, or must everything
   live in-file (→ prefer NRRD/`.seq.nrrd`)?
6. **Scope of metadata propagation** — should exported *segmentations* also carry the phase axis +
   non-PHI block, or images only?

---

## 6. Effort sketch (rough)

| Phase | Relative effort | Risk |
|---|---|---|
| P0 data model | S | low |
| P1 read extraction | M | low-med (DICOM tag variability) |
| P2 propagation/UI | S-M | low |
| P3 writers | **S-M** ↓ | low-med (`.seq.nrrd` writer already exists; just add `%R-R`+metadata via the unified hook) |
| P4 robustness | M | low-med |
| P5 polish | S | low |

Minimum viable slice for the stated goal = **P0 + P1 + P3.3** (model → extract on read → emit `%R-R`
in the existing `.seq.nrrd` writer). With the writer already present on `master`, this is now a
notably smaller change than originally scoped.
