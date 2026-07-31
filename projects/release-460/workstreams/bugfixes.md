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
| 1 | **`GUI_TESTS` name typo** — `4DContinuousRenderingD` (stray trailing `D`) pointed at a script that does not exist; the real `test_4DContinuousRendering.js` was in `TestingScripts.qrc` but orphaned. | Root `CLAUDE.md`; confirmed 2026-07-30 | 1 char | ✅ `97285971` |
| 2 | **`4DReplayWithMeshUpdate` latent hang.** `IsMeshUpdating` is set in `ViewPanel3D.cxx:391` before `QtConcurrent::run` and cleared **only from inside the worker** (`Generic3DModel.cxx:282`). No `QFutureWatcher::finished` main-thread handler — a worker that hangs, or throws anything other than `bad_alloc`/`IRISException`, blocks replay permanently. | Root `CLAUDE.md`; the test's flakiness is a symptom | Small | ☐ |
| 3 | **`RemoteImageLoadTest_Cache`** — download succeeds but `CacheMetadata.xml` is never written. Sits directly on the 4.6 headline feature (§2.1 of change_tracking), so it matters more than a normal flaky test. Passed on macOS 2026-07-30; Linux-specific or flaky. | Linux test run 2026-07-17 | Unknown | ☐ |
| 3b | **`RemoteImageLoadTest_WorkspaceWithMesh` asserts exact equality on an approximate quantile.** It compares p25 of the remote-fetched image against the local one; both are byte-identical (`shasum 6437d829…` on each) and read by the same binary, yet the value differs every run: `45.065006/45.000507`, `45.080894/45.073586`, then a pass, then `45.000000/45.066990`. ITK-SNAP computes quantiles with tdigest — an *approximate*, order-sensitive estimator — so exact comparison can never be stable. Roughly 1-in-4 pass rate. Same test family as item 3. | Measured over 4 runs, 2026-07-30 | Small — compare with a tolerance | ☐ |
| 4 | **VTK version inconsistency** — CI builds 9.5.2 (`c480b003`), `CMake/standalone.cmake:72` requires 9.3.1. | Verified 2026-07-30 | Small, but needs a decision | ☐ |
| 5 | **Duplicate leak-fix commits** — `1712c6e7`/`958646a7` and `0db4b80b`/`35f181fd` are identical pairs. History only; nothing to fix in code, but count them once in the release notes. | [../change_tracking.md](../change_tracking.md) §3.2 | Note only | ☐ |
| 6 | ~~`origin/master` is 1 behind `upstream/master`~~ — **not a bug.** `git branch -vv`'s `[origin/master: behind 1]` describes the *local* checkout, not the remote. Both remotes are at `679ba76a`. | Re-verified 2026-07-30 | — | ✅ n/a |
| 7 | **Delete 7 merged branches** — `bug/{4d-mesh-slice,large-image-oom,memory-leak,mesh-update-crash}`, `feature/{io-improvement,seq-nrrd-export,vti-io}`. All at +0 vs `upstream/master`. | Verified 2026-07-30 | Trivial | ☐ |
| 8 | **4DCTA detection is loose** — currently "any Siemens/GE CT directory". Benign today (a single-phase series loads as 1 time point), but it is a known imprecision. | `projects/4dcta_improvement/progress_summary.md` | Small | ☐ |
| 9 | **Stray `.nii.gz` loses its frame axis** when separated from its `.json` sidecar. `.nrrd`/`.seq.nrrd` keep everything in-file. Design limitation of NIfTI; document it rather than fix it. | Same | Doc | ☐ |
| 10 | **`FormatVersion` is written but never validated.** `TimePointProperties::Load` reads it into an unused local at `TimePointProperties.cxx:118` under a `// Validate version` comment; upstream's copy is identical. Make it do what the comment claims — warn when the folder version exceeds what the reader knows. | W1 Q1 investigation, 2026-07-30 | Small | ☐ |
| 11 | **An older build silently strips cardiac metadata on re-save.** `SaveProjectToRegistry` calls `preg.Clear()` (`IRISApplication.cxx:2283`) and rebuilds from in-memory state, so keys the reader never loaded are dropped without warning. Pairs with item 10. | Same | Needs design | ☐ |
| 12 | **Four unfixed DLS threading races** are documented in `itksnap/CLAUDE.md` — including a `QtConcurrent` lambda capturing `this` that can dereference a destroyed panel after a network timeout (use-after-free). Upstream `679ba76a` fixed a different DLS race; these remain. | `itksnap/CLAUDE.md` | Needs design — likely promote | ☐ |
| 13 | **Any GUI test with a missing script silently PASSED.** `TestWorker::readScript` called `application_exit(NO_SUCH_TEST)` and fell through — `application_exit` only *queues* a quit (`QMetaObject::invokeMethod`, `Qt::QueuedConnection`). Execution continued past the failed `QFile::open()`, read an empty script off the unopened file, and `source()` evaluated `""`. An empty program is not a JS error, so it took the success branch and queued `SUCCESS`, which landed after and overrode the failure. Exit 0 → ctest `Passed`. **This is why item 1 went unnoticed, and it applied to all 21 GUI tests.** | Root-caused 2026-07-30 from the 0.98 s "pass" | Small | ✅ `97285971` |

| 14 | **`test_RandomForestBailOut.js` was never in the `.qrc`** — added to disk and to `GUI_TESTS` in the same 2018 commit `062ba382`, but the runner resolves `:/scripts/...` from Qt resources, not the filesystem. Only on-disk script of 21 that was unregistered. Combined with item 13, it reported `Passed` in ~0.98 s without executing for ~8 years. | Traced 2026-07-30 | 1 line | ✅ `4e1baa2a` |
| 17 | 🔴 **The GUI test harness drives Qt from a worker thread.** `class TestWorker : public QThread` runs the test script inside `run()` (`SNAPTestQt.h:27`), so every scripted widget call — `click()`, `setCurrentIndex()`, `trigger()` — executes off the main thread, which Qt does not support. macOS raises `NSInternalInconsistencyException` ("modification of a menu's items on a non-main thread"); the long-standing `QBasicTimer::start: Timers cannot be started from another thread` warning has the same cause. **Affects all 21 GUI tests** — the others merely avoid the widgets that assert. This is the most likely explanation for the suite's run-to-run instability, including `4DReplayWithMeshUpdate`. Proper fix: marshal scripted calls to the main thread (`Qt::BlockingQueuedConnection`). | Stack frames 27–31 of the abort, 2026-07-30 | **Large — promote** | ☐ |
| 15 | ✅ **Was: SEGFAULT on Classify/Train.** Root-caused to an unguarded null `m_ClassificationEngine`, not the use-after-free first suspected — see the correction below. Fixed in `1d1fe7ea`; the test no longer segfaults but still fails, now on item 17. **Superseded description:** *use-after-free on cancel after random-forest classification.* `m_ClassificationEngine` exists only between `EnterRandomForestPreprocessingMode()` and `Leave…()`. `SnakeWizardModel.cxx:1813` dereferenced it with no guard (`EXC_BAD_ACCESS` at `0x80`, `x0 == 0` — a null `this`), and `IRISApplication.cxx:2852` did the same when leaving a mode never fully entered. **Correction:** my first read of the `.ips` blamed a use-after-free in `LayerInspectorRowDelegate::onModelUpdate` via the queued-event path. Under lldb the real fault is elsewhere and simpler; the `.ips` symbolization was misleading. lldb breakpoints proved `EnterRandomForestPreprocessingMode` is **never called** during the test, so the engine is null throughout. | lldb backtrace + breakpoint evidence, 2026-07-30 | Fixed | ✅ `1d1fe7ea` |
| 15b | **Systemic: action methods guard the engine with `assert()` only.** In `SnakeWizardModel`, query methods use `if(!rfe) return false;` but the void action methods use `assert(rfe);`, which is compiled out under `NDEBUG` — so none of them are protected in release builds. Same shape at `RFClassificationEngine.cxx:54`. Item 15 fixed the one reachable site; the pattern remains. | Surveyed 10 call sites, 2026-07-30 | Medium | ☐ |
| 15c | **Why the test never enters RF mode.** `SetPreprocessingModeValue` does call `EnterPreprocessingMode`, and the combo coupling uses `currentIndexChanged` (which *does* fire on programmatic `setCurrentIndex`), and the item label really is "Classification" — yet the mode change never lands. Note `SNAPTestQt::findItemRow` returns an **invalid QVariant**, not `-1`, when the item is not found, so a failed lookup silently becomes a bad `setCurrentIndex`. Unresolved; likely a consequence of item 17. | Investigated 2026-07-30 | Unknown | ☐ |
| 16 | **Memory-leak canary baseline is invalid.** `itksnap/CLAUDE.md` documents `RandomForestBailOut` as one of two canaries (≤ 600 leaks / ≤ 90 KB). That was measured on a process that loaded no script and exited immediately. Re-baseline once item 15 is fixed, and correct the doc. `PreferencesDialog` is unaffected — its script is registered. | Follows from item 14 | Doc + re-measure | ☐ |

## Triage rule

Promote out of W8 if the fix needs a design decision, touches more than ~3 files, or cannot be
finished in one session. Items 2 and 3 are the likely promotions.

## Done-criteria

- Every ticked row has a commit on `staging/v460`.
- Items 1–3 each gained or repaired a test — they *are* test-infrastructure bugs; fixing them without
  proving the test now catches the failure would repeat the mistake.
- Items that turn out to be documentation rather than code (5, 9) are reflected in
  `ReleaseNotes.md` or `Documentation/Developer/` and marked as such.
