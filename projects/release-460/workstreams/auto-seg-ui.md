# W4 — Fully automatic segmentation UI

**Status:** not started
**Branch:** none yet
**Depends on:** **W3** (TotalSegmentator wrapper + frozen DLS API)

## Goal

A user opens an image, picks a model, presses one button, and gets a labeled segmentation with real
label names and colors — no interaction, no scribbles. Long-running inference does not freeze the UI
and can be cancelled.

## Current state

Nothing on the ITK-SNAP side. The existing DLS UI
(`GUI/Model/DeepLearningSegmentationModel.{h,cxx}`, `GUI/Qt/Windows/DeepLearningServerPanel.cxx`,
`GUI/Qt/Components/PaintbrushToolPanel`) is built around *interactive* nnInteractive/SAM2 prompts —
point, scribble, lasso — not whole-image inference.

Server side exists: `bbaac51` on `itksnap-dls:feature/agentic-api` adds the TotalSegmentator wrapper
(W3).

Reusable infrastructure already merged upstream:

| Piece | Where | Why it matters |
|---|---|---|
| `ProgressReportWidget` + task cancellation | `2154b1bb`, `848f80fb` | Long-running task UI already exists — don't build a second one |
| `AbstractProgressDelegate` | `cbe2a713` | Progress reporting is unified in `Common/` |
| Async DLS interaction pattern | `cb6f692e` (**unmerged**, W1) | `QtConcurrent::run` + `QFutureWatcher` precedent for non-blocking REST |
| Multi-label naming/coloring over a channel | `e06937f8` on `sprint/caimi` | A whole-body model returns ~100 labels; this solved naming them. **Not** agentic-specific in substance — worth mining |

## Plan

1. Extend `DeepLearningSegmentationModel` with a non-interactive path: list models, submit the whole
   image, poll, retrieve.
2. UI surface — decide between a new dialog and an extension of `DeepLearningServerPanel`
   (open question 1).
3. Model/label catalog: fetch the label set from the server and populate ITK-SNAP's label table
   with real anatomical names and a sensible palette.
4. Wire progress + cancellation through the existing `ProgressReportWidget`.
5. Result handling: new segmentation layer vs. replace vs. merge into the active one.
6. A GUI test under `Testing/GUI/Qt/` driving the flow against a stub server.

## Open questions

1. **Where does this live in the UI?** TotalSegmentator is not a drawing tool, so the paintbrush
   panel is the wrong home. Candidates: a `Segmentation` menu item opening a dialog, or a new tab in
   the DLS panel. Affects discoverability more than anything else in this workstream.
2. **~100 labels arriving at once** — does it replace the label table, merge, or offer a subset
   picker? Merging into a user's existing labels risks ID collisions.
3. **Inference can take minutes.** Modal-with-cancel, or background with the user free to keep
   working? Background raises the question of what happens if they edit the segmentation meanwhile.
4. **Where do model weights come from** — server-side only, or does ITK-SNAP ever trigger a download?
   Ties to W3 open question 2.
5. **3D only, or 4D too?** If 4D, it overlaps W5 (propagation) and the two should share a job model.

## Done-criteria

- A user can run whole-image inference from the GUI on a 3D image and get named, colored labels.
- The main thread stays responsive throughout, and cancel actually cancels — verified against a
  deliberately slow stub.
- A GUI test exercises submit → progress → result → labels-populated and fails if any step regresses.
- `ReleaseNotes.md` entry; user-facing documentation updated.
