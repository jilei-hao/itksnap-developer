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

1. ✅ ~~Fast-forward the local `master` checkout~~ — `origin/master` was already in sync with
   `upstream/master` @ `679ba76a`; only the local checkout lagged. Nothing to push.
2. ✅ Cut `staging/v460` from `upstream/master` @ `679ba76a` and push it. *(2026-07-30)*
3. ✅ Q1, Q2, Q3 resolved below — Q1 and Q3 were false alarms, Q2 narrowed to one decision.
   **Q4 still open.**
4. ✅ Merge `feature/cardiac-io` → `staging/v460` — `594b4033`, clean, no conflicts.
   macOS arm64 builds 212/212 with no warnings in any cardiac-io file. Linux **still pending**.
5. ✅ Cherry-pick `ad727107` **minus** the VTK floor line — `e2f19b56`. Verified on macOS/clang;
   the Linux/GCC build it targets is **still unverified** (needs the Linux box).
6. ⏳ Cherry-pick `cb6f692e` and `ea86df0d` — **blocked on Q4**; add the undo test first.
7. ⏳ Re-resolve the `Submodules/{c3d,greedy}` bump against current upstream rather than replaying
   `71e2544d`.
8. ⏳ Delete the seven fully-merged branches listed in [../SPRINT_PLAN.md](../SPRINT_PLAN.md) §2.

Landed alongside, from investigating the test baseline (W8 items 1 and 13): `97285971` fixes the
`4DContinuousRenderingD` typo **and** the reason it survived — a missing test script was reported as
success, which applied to all 21 GUI tests. See [bugfixes.md](bugfixes.md).

## Open questions

### Q1 — Workspace `FormatVersion` 1 → 2 → 3 · ✅ RESOLVED 2026-07-30: not a blocker

**The premise was wrong. There is no open-failure compatibility break**, and step 4 was unblocked
on this basis. Evidence:

- `FormatVersion` is **scoped to the `TimePointProperties` folder**, not to the workspace. It is the
  only `FormatVersion` in the tree — 4 references, all in `Logic/Framework/TimePointProperties.cxx`.
- **Neither reader validates it.** `TimePointProperties::Load` reads it into a local `version` at
  `TimePointProperties.cxx:118` under a `// Validate version` comment and then never uses it —
  and upstream/master's copy is identical (its line 64). An old build *cannot* reject a v3 folder;
  it never looks at the value.
- The old reader takes `Nickname` and `Tags` by explicit key and enumerates nothing, so the four
  added keys (`RRPercent`, `RRPercentExact`, `FrameValue`, `FrameUnit`) are simply not read.
- The **workspace**-level `Version` key holds a release date (`IRISApplication.cxx:2289`) and is only
  checked for *existence* — `preg.HasEntry("SaveLocation") && preg.HasEntry("Version")` at
  `IRISApplication.cxx:2623`, under a comment that already calls itself "pretty weak". Never compared.
- **`SNAP_VERSION_LAST_COMPATIBLE_RELEASE_DATE` is dead code.** It is `SET` at `CMakeLists.txt:105`
  and referenced nowhere else — no source file, no generated header. Moving it would do nothing.

**The real exposure is different and smaller: silent metadata loss on round-trip.**
`IRISApplication::SaveProjectToRegistry` calls `preg.Clear()` (`IRISApplication.cxx:2283`) and
rebuilds from in-memory state, so a 4.4.0 build that opens a 4.6.0 workspace and re-saves it drops
the cardiac keys with no warning. That is a data-integrity nuisance, not a compatibility break.

**Follow-up (not blocking):** make `FormatVersion` do what its comment claims — warn when the folder
version is newer than the reader knows. Filed as a W8 item.

### Q2 — VTK floor · ✅ RESOLVED 2026-07-30: not a defect; one real decision left

**`c480b003` did not create a contradiction.** `FIND_PACKAGE(VTK 9.3.1 REQUIRED)`
(`CMake/standalone.cmake:72`) declares a **minimum**, and VTK's `vtk-config-version.cmake` sets
`PACKAGE_VERSION_COMPATIBLE` whenever installed ≥ requested. CI at 9.5.2 satisfies a 9.3.1 floor.
Before `c480b003`, CI built exactly `9.3.1` — the floor itself.

The narrower real issue: **nothing exercises the declared floor any more.**

| Where | VTK | vs. declared 9.3.1 floor |
|---|---|---|
| CI (`build.yml:56`, after `c480b003`) | 9.5.2 | above |
| macOS dev box (`lib/vtk/install`) | 9.3.1 | exactly at |
| Linux dev box | 9.3.0 | **below** — which is why `ad727107` relaxed the requirement to `9.3` |

**Decision for Jilei** (it affects your Linux box, so it is not mine to make):

- **(a) Raise the floor to 9.5.2** — the version CI actually verifies. Cleanest, and it makes
  `ad727107`'s VTK relax unnecessary. Cost: the Linux box must upgrade VTK.
- **(b) Keep 9.3.1 and add a CI matrix entry at the floor**, so the claim is tested rather than
  asserted. Cost: a second CI job.
- **(c) Lower to 9.3.0** to match the Linux box. Least tested of the three.

**Whichever is chosen, do not carry `ad727107`'s blanket relax to `9.3` into the release** — it
lowers the project's supported floor to accommodate one development machine.

### Q3 — jsoncpp dependency · ✅ RESOLVED 2026-07-30: false alarm, no new dependency

jsoncpp is **already vendored in-tree** and predates this branch: `Common/JSon/jsoncpp.cpp` and
`Common/JSon/json/json.h` exist on `upstream/master`, registered at `CMakeLists.txt:243` and
`:355–356` with the include directory added at `:1058` — **identical line numbers** before and after.
`git log upstream/master..origin/feature/cardiac-io -- Common/JSon/ CMakeLists.txt` is empty: the
branch touched neither. `3033e9e1` only `#include "json/json.h"` in
`Logic/ImageWrapper/GuidedNativeImageIO.cxx:94`, a header that was already there. Confirmed
empirically — `cmake -S itksnap -B build-release` on the merged tree configures clean. Nothing to
add to the build docs; nothing to verify per-platform.

### Q4 — Undo semantics under async DLS · ✅ ANSWERED 2026-07-30 — **do not cherry-pick as-is**

Two defects, both in `cb6f692e` itself. Step 6 stays blocked, now for understood reasons.

**A. The undo gap is real.** `on_complete` stores the undo point only when passed `true`:

```cpp
auto on_complete = [driver](bool success) {
  if(success) { driver->GetSelectedSegmentationLayer()->StoreUndoPoint("Drawing with paintbrush");
                driver->RecordCurrentLabelUse(); }
};
```

The completion handler wraps `UpdateSegmentation` — which mutates the label image via
`UpdateSegmentationWithSliceDrawing` — in a `try`, and the `catch` calls `on_complete(false)`. A
throw partway through leaves the segmentation **modified with no undo point**, so the user cannot
undo it. (`on_complete(changed)` with `changed == 0` is correct: nothing was modified.)

**B. It reproduces a use-after-free that `itksnap/CLAUDE.md` already documents.** The watcher is
created parentless (`new QFutureWatcher<Result>()`) and the `[=]` lambda captures `this`, calling
`this->UpdateSegmentation` and `this->InvokeEvent`. The connection's context object is `watcher`,
not the model, so nothing disconnects it if the model dies mid-flight. `AbstractModel` is an
`itk::Object`, **not** a `QObject`, so it cannot serve as a context object — which is precisely why
the code is shaped this way. This is race #3 in that list ("the `QtConcurrent` lambda … captures
`this` … a silent use-after-free"), reproduced in new code.

**Before merging:** fix A (make the update transactional, or store the undo point before mutating)
and B (a `QPointer`/weak guard or an explicit cancellation token, since the context-object route is
unavailable).

**No test was written, deliberately.** A GUI-script test would run on the harness in
[bugfixes.md](bugfixes.md) item 17, which drives Qt from a worker thread. A test of *async* behavior
running on a thread-unsafe harness would not be trustworthy evidence either way. Testing this
properly needs item 17 fixed, or a model-level test against a stub server.

## Done-criteria

- `staging/v460` contains all 15 accepted commits; `git rev-list --count upstream/master..staging/v460` == 15.
- A 4D cardiac CTA round-trip test (`.seq.nrrd` and `.nii.gz` + sidecar) exists in `Testing/` and
  fails if the `%R-R` axis is dropped. The 4DCTA work was verified with a throwaway driver — that
  does not ratchet.
- A workspace-compatibility test covers whichever direction Q1 resolves to.
- A test covers undo after a cancelled async DLS interaction.
- Linux/GCC build succeeds with **no** local patches applied on top of `staging/v460`.
