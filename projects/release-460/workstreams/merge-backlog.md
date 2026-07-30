# W1 — Merge the ready backlog

**Status:** not started (work is written; merge decisions pending)
**Branch:** sources are `itksnap:feature/cardiac-io`, `itksnap:sprint/caimi@ad727107`, `itksnap:test/dls_sam2`; target is `itksnap:staging/v460`
**Depends on:** nothing — this is the first workstream

## Goal

Every piece of already-written, already-verified ITK-SNAP work that is not agentic-API work is
merged into `staging/v460`, and the branches it came from are either deleted or explicitly kept.
After this, "unmerged" means "not yet written".

## Current state

Verified 2026-07-30. Branch positions are in [../SPRINT_PLAN.md](../SPRINT_PLAN.md) §2.

| Source | Commits | Verified as |
|---|---:|---|
| `feature/cardiac-io` | 12 | End-to-end headless against the AVRP cohort; GUI field confirmed; builds clean macOS arm64 (`projects/4dcta_improvement/progress_summary.md`) |
| `ad727107` (Linux/GCC) | 1 | Still required — re-checked against `upstream/master` on 2026-07-30: `CMake/standalone.cmake:72` still pins VTK 9.3.1; `CMakeLists.txt:1298`, `:1663`, `:1723`, `:1813` still unguarded |
| `test/dls_sam2` | 2 of 4 | Based on top of merged `2154b1bb`, so genuinely new. `8539d63c` duplicates `ad727107`; `71e2544d` is a stale submodule bump |

---

## Decision list

Per-commit ship/hold calls. **These are the items that need Jilei's sign-off before step 4.**

### D1 — `feature/cardiac-io`: 4D cardiac CTA/echo I/O (12 commits)

From `projects/4dcta_improvement/`. Verified end-to-end headless against the AVRP cohort; GUI field
confirmed working; builds clean on macOS arm64.

| # | Commit | Change | Type | Recommend |
|---|---|---|---|---|
| 1 | `0e5168ad` | Recover `%R-R` cardiac phase on 4D CTA read; `.seq.nrrd` writes it. **Replaces the hardcoded `0.05` temporal spacing.** | Bugfix + Feature | **Ship** |
| 2 | `7b51378a` | NIfTI `pixdim[4]` + `<name>.json` sidecar with the phase array | Feature | **Ship** |
| 3 | `7a1c2489` | Non-PHI allow-list curation on export; age top-coded ≥90 (HIPAA Safe Harbor) | Feature | **Ship** — privacy-relevant, call it out in the notes |
| 4 | `c1346b9d` | Route the float (non-identity mapping) write path through `SaveImage` | Bugfix | **Ship** |
| 5 | `a0f9d6f0` | Per-time-point typed cardiac fields + GUI. **Workspace `FormatVersion` → 2** | Feature | ⚠️ **see Q1** |
| 6 | `dec2a2f2` | `Documentation/Developer/Cardiac4DCTA_IO.md` | Docs | **Ship** |
| 7 | `a359b7bd` | Ragged-grid quarantine (clear `IRISException`); `NumberOfPhases` in seq header | Bugfix + Feature | **Ship** |
| 8 | `2dc3d470` | 4D echo: modality-agnostic frame axis (CT `%R-R` / echo `ms`), US non-PHI keep-list, read guards | Feature | **Ship** |
| 9 | `c3db9f65` | GUI field generalized to "Phase / time:". **Workspace `FormatVersion` → 3** | Feature | ⚠️ **see Q1** |
| 10 | `3033e9e1` | NIfTI JSON sidecar **reader** (jsoncpp) + slice thickness across formats | Feature | **Ship** — but see Q3 |
| 11–12 | `54601b15`, `9b5d9eb4` | Doc refreshes | Docs | **Ship** |

**Known remaining gaps** (from `projects/4dcta_improvement/progress_summary.md`, all minor, all
tracked as W8 items): 4DCTA detection is loose ("any Siemens/GE CT directory"); 4D non-identity float
export is current-time-point only; a stray `.nii.gz` separated from its `.json` loses the frame axis.

### D2 — `ad727107`: Linux/GCC build portability (1 commit)

**Re-verified 2026-07-30 against `upstream/master`: still required.**

Six patches: VTK `9.3.1`→`9.3`; Qt version guards on `qt_add_translations` and three
`qt_generate_deploy_script` calls; `QString::fromStdString` in `SSHTunnelWorkerThread.cxx` and
`Testing/GUI/Qt/SSHTunnelTest/main.cxx`; `#include <QTimeZone>` in `SNAPQtCommon.cxx`;
`#include <QDialogButtonBox>` + a stream fix in `DeepLearningServerPanel.cxx`.

**Recommend: ship**, but redo the VTK line as a deliberate floor decision (Q2) rather than a blanket
relax to `9.3`. Everything else is a straight portability fix with no behavior change.
`8539d63c` on `test/dls_sam2` is the same patch set — take one, not both.

### D3 — `test/dls_sam2`: async DLS interactions (4 commits)

Based **on top of** upstream `2154b1bb` (SAM2 + progress bar, already merged), so these are genuinely
new work, not a duplicate.

| Commit | Change | Type | Recommend |
|---|---|---|---|
| `cb6f692e` | DLS paintbrush interactions non-blocking — REST on a background thread via `QtConcurrent::run` + `QFutureWatcher`; UI locked while in flight | Feature (UX) | **Ship** — a blocking main thread during inference is the top complaint risk for the DLS feature |
| `ea86df0d` | `DoScribbleInteractionBg` was missing a `ProgressTaskGuard`, so scribbles never showed the progress dialog | Bugfix | **Ship** |
| `71e2544d` | Bump `Submodules/{c3d,greedy}` to latest master | Maintenance | **Ship**, but re-resolve — the pointers have moved since 2026-06 |
| `8539d63c` | Linux/GCC build fixes | Build | **Skip** — same as D2 |

### D4 — Explicitly not in 4.6.0

The 6 agentic-API commits on `sprint/caimi` and the whole `itksnap-mcp` repo. See
[../SPRINT_PLAN.md](../SPRINT_PLAN.md) §1.

---

## Plan

1. ~~Fast-forward the local `master` checkout~~ — `origin/master` was already in sync with
   `upstream/master` @ `679ba76a`; only the local checkout lagged. Nothing to push.
2. Cut `staging/v460` from `upstream/master` @ `679ba76a` and push it.
3. Resolve Q1–Q4 below.
4. Merge `feature/cardiac-io` → `staging/v460`. Build macOS + Linux; run `ctest`.
5. Cherry-pick `ad727107`, reworking the VTK line per Q2.
6. Cherry-pick `cb6f692e` and `ea86df0d`; **add an undo test first** (Q4).
7. Re-resolve the `Submodules/{c3d,greedy}` bump against current upstream rather than replaying
   `71e2544d`.
8. Delete the seven fully-merged branches listed in [../SPRINT_PLAN.md](../SPRINT_PLAN.md) §2.

## Open questions

- **Q1 — Workspace `FormatVersion` 1 → 2 → 3** (`a0f9d6f0`, `c3db9f65`). A 4.6.0 workspace will not
  open in 4.4.0. Either move `SNAP_VERSION_LAST_COMPATIBLE_RELEASE_DATE` (currently `20131201`) or
  make the reader degrade gracefully on an unknown version. **Blocks step 4.** Test both directions.
- **Q2 — VTK floor.** CI moved to 9.5.2 at `c480b003` but `CMake/standalone.cmake:72` still requires
  9.3.1. Pick one. **Blocks step 5.**
- **Q3 — jsoncpp dependency** (`3033e9e1`, the NIfTI sidecar reader). Confirm it is available on all
  three CI platforms and add it to the build docs.
- **Q4 — Undo semantics under async DLS** (`cb6f692e`). `PaintbrushModel::CommitDrawing` now defers
  `StoreUndoPoint` / `RecordCurrentLabelUse` into the completion handler. What happens on a
  cancelled or failed interaction is untested. **Blocks step 6.**

## Done-criteria

- `staging/v460` contains all 15 accepted commits; `git rev-list --count upstream/master..staging/v460` == 15.
- A 4D cardiac CTA round-trip test (`.seq.nrrd` and `.nii.gz` + sidecar) exists in `Testing/` and
  fails if the `%R-R` axis is dropped. The 4DCTA work was verified with a throwaway driver — that
  does not ratchet.
- A workspace-compatibility test covers whichever direction Q1 resolves to.
- A test covers undo after a cancelled async DLS interaction.
- Linux/GCC build succeeds with **no** local patches applied on top of `staging/v460`.
