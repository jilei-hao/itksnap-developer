# W8 — Bugfixes and small improvements

**Status:** rolling
**Branch:** rolling — small fixes go straight to `staging/v460`
**Depends on:** nothing

## Goal

A running list of small, self-contained fixes for 4.6.0. Anything needing design or more than a
session gets promoted to its own workstream.

## Known items

Each carries the evidence for why it is a bug. Add rows as things are found; tick when merged.

| # | Item | Evidence | Size | Done |
|---|---|---|---|---|
| 1 | **`GUI_TESTS` name typo** — the entry reads `4DContinuousRenderingD` (stray trailing `D`), so the runner looks for `:/scripts/Scripts/test_4DContinuousRenderingD.js`, which does not exist. The real `test_4DContinuousRendering.js` is in `TestingScripts.qrc` but orphaned. | Root `CLAUDE.md`, Linux test run 2026-07-17; 1 of 3 failures | 1 char | ☐ |
| 2 | **`4DReplayWithMeshUpdate` latent hang.** `IsMeshUpdating` is set in `ViewPanel3D.cxx:391` before `QtConcurrent::run` and cleared **only from inside the worker** (`Generic3DModel.cxx:282`). No `QFutureWatcher::finished` main-thread handler — a worker that hangs, or throws anything other than `bad_alloc`/`IRISException`, blocks replay permanently. | Root `CLAUDE.md`; the test's flakiness is a symptom | Small | ☐ |
| 3 | **`RemoteImageLoadTest_Cache`** — download succeeds but `CacheMetadata.xml` is never written. Sits directly on the 4.6 headline feature (§2.1 of change_tracking), so it matters more than a normal flaky test. | Linux test run 2026-07-17; 1 of 3 failures | Unknown | ☐ |
| 4 | **VTK version inconsistency** — CI builds 9.5.2 (`c480b003`), `CMake/standalone.cmake:72` requires 9.3.1. | Verified 2026-07-30 | Small, but needs a decision | ☐ |
| 5 | **Duplicate leak-fix commits** — `1712c6e7`/`958646a7` and `0db4b80b`/`35f181fd` are identical pairs. History only; nothing to fix in code, but count them once in the release notes. | [../change_tracking.md](../change_tracking.md) §3.2 | Note only | ☐ |
| 6 | ~~`origin/master` is 1 behind `upstream/master`~~ — **not a bug.** `git branch -vv`'s `[origin/master: behind 1]` describes the *local* checkout, not the remote. Both remotes are at `679ba76a`. | Re-verified 2026-07-30 | — | ✅ n/a |
| 7 | **Delete 7 merged branches** — `bug/{4d-mesh-slice,large-image-oom,memory-leak,mesh-update-crash}`, `feature/{io-improvement,seq-nrrd-export,vti-io}`. All at +0 vs `upstream/master`. | Verified 2026-07-30 | Trivial | ☐ |
| 8 | **4DCTA detection is loose** — currently "any Siemens/GE CT directory". Benign today (a single-phase series loads as 1 time point), but it is a known imprecision. | `projects/4dcta_improvement/progress_summary.md` | Small | ☐ |
| 9 | **Stray `.nii.gz` loses its frame axis** when separated from its `.json` sidecar. `.nrrd`/`.seq.nrrd` keep everything in-file. Design limitation of NIfTI; document it rather than fix it. | Same | Doc | ☐ |

## Triage rule

Promote out of W8 if the fix needs a design decision, touches more than ~3 files, or cannot be
finished in one session. Items 2 and 3 are the likely promotions.

## Done-criteria

- Every ticked row has a commit on `staging/v460`.
- Items 1–3 each gained or repaired a test — they *are* test-infrastructure bugs; fixing them without
  proving the test now catches the failure would repeat the mistake.
- Items that turn out to be documentation rather than code (5, 9) are reflected in
  `ReleaseNotes.md` or `Documentation/Developer/` and marked as such.
