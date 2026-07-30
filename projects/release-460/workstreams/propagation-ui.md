# W5 — Segmentation propagation UI

**Status:** not started
**Branch:** none yet
**Depends on:** **W3** (`modules/propagation/` + frozen DLS API), `segflow4d:main`

## Goal

A user segments one time point of a 4D image, presses propagate, and gets the segmentation carried
across the remaining frames — running remotely through DLS, with progress and cancellation, without
leaving ITK-SNAP.

## Current state

Nothing on the ITK-SNAP side.

Server side exists on `itksnap-dls:feature/agentic-api` (W3):
`modules/propagation/router.py` (104 lines) and `modules/propagation/jobs.py` (96 lines) — an async
job model, added at `7ecf586` *"segflow4d integration"*.

`segflow4d:main` @ `ed143db` — *"S4 Step 1: warp + write additional_meshes through the propagation
pipeline"*, 2026-05-28. Four unmerged side branches (`bugfix/lowres-clamp`,
`docs/mps-fused-ops-required`, `feature/roi-crop`, `fix/mesh-warp-aliasing`) — triage these before
depending on `main`.

Related prior art in ITK-SNAP: the existing greedy-based propagation
(`Submodules/greedy`, and the `greedy_python` `PropagationWrapper`). Worth checking whether this
should extend that machinery or sit beside it — see open question 1.

## Plan

1. Triage the four segflow4d side branches; land what the pipeline needs.
2. Read `modules/propagation/router.py` and write down the actual job contract: submit, poll,
   retrieve, cancel.
3. ITK-SNAP model layer: a propagation model owning job state, following the async pattern from
   `cb6f692e` (W1).
4. UI: source time point, target frames, model/parameters, submit.
5. Progress via `ProgressReportWidget` (`848f80fb` gives cancellation for free).
6. Result: write propagated segmentations into the 4D segmentation layer, per time point.
7. Test against a stub server with a synthetic 4D image.

## Open questions

1. **Does this replace or sit beside the existing greedy propagation?** ITK-SNAP already propagates
   via greedy locally. Two propagation paths with different UIs would be confusing; decide before
   designing the UI, not after.
2. **Where does the 4D image go over the wire?** Whole volume, or frame-by-frame? A 4D cardiac CTA is
   large; the agentic work already hit *"DLS upload drops geometry"* (see
   `projects/agentic-api/NEXT_SESSION_PROMPT.md`) — the same geometry-restoration care applies here.
3. **Partial results.** If frame 7 of 20 fails, does the user keep frames 1–6? A per-frame job model
   answers this better than a single job.
4. **Does this interact with the 4DCTA phase axis (W1)?** Propagated frames should keep `%R-R` /
   frame-time metadata; that is only true if the write path goes through the curated `SaveImage` route.
5. **GPU availability.** segflow4d propagation is heavy. What does ITK-SNAP show when the server has
   no GPU or is busy?

## Done-criteria

- A user propagates a segmentation across a 4D image from the GUI and the result lands in the right
  time points.
- Cancellation works mid-propagation and leaves the workspace in a defined state.
- The frame axis / cardiac metadata survives propagation — with a test that fails if it is dropped
  (this is exactly the class of silent regression W1's work was built to prevent).
- A test covers the partial-failure path chosen in open question 3.
- `ReleaseNotes.md` entry; user-facing documentation updated.
