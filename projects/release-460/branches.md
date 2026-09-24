# Topic branches — the upstream review queue

**Snapshot:** 2026-09-24 · **Base for every branch:** `upstream/master` @ `52ee94fa` · **Pushed:** yes,
all five plus `staging/v460`, to `jilei-hao/itksnap` (2026-09-24). **Merge order and live branch
state:** [MERGE_ORDER.md](MERGE_ORDER.md). · **Meeting page (private):**
https://claude.ai/artifact/QyivAN8NiDzadZ7hPKn6ut — a rendered copy of this file as of 2026-09-24; this file stays the
source of truth.

This is the planning-meeting handout: one row per branch that could become a PR to
`pyushkevich/itksnap`. The branch model itself (why `staging/v460` is test-only) is in
[SPRINT_PLAN.md](SPRINT_PLAN.md) §2. Per-item evidence stays in the workstream files; this file only
maps it onto branches.

---

## Summary

| # | Branch | Tip | Commits | From | Standalone on macOS, 2026-09-24 |
|---|---|---|---:|---|---|
| 1 | `feature/cardiac-io` | `2fc0d9b8` | 12 | W1 · D1 | ✅ builds, **34/34** |
| 2 | `bug/linux-gcc-build` | `fb65f2b9` | 2 | W1 · D2, Q2 | ✅ builds, **34/34** |
| 3 | `bug/rf-layer-crashes` | `9e80001f` | 4 | W8 · 14, 15, 15d, 24 | ✅ builds, 33/34: only the remote flake. `RandomForestBailOut` **really runs** (20.0 s) and passes |
| 4 | `test/harness-false-green` | `83c44f62` | 1 | W8 · 1, 13 | ⚠️ builds, 32/34: a remote flake, plus `RandomForestBailOut` **"no such test"** — **needs #3 merged first** |
| 5 | `test/harness-gui-thread` | `8a28d50c` | 1 | W8 · 17, 25 | ✅ builds, 32/35: two remote flakes, plus `4DReplayWithMeshUpdate` — a known flake: it then passed **5/5** here vs **3/5** on `upstream/master` |

**All five merged (`staging/v460` @ `62588ffc`): 34/35**, failing only `RemoteImageLoadTest_SingleImage`
(remote flake). The Sep 4 pre-split run, on an identical tree, failed the other remote test.
Nothing outside the flake pair failed in either run.

**Baseline — `upstream/master` itself: 34/34, but two of those passes ran nothing.**
`4DContinuousRenderingD` (0.91 s) and `RandomForestBailOut` (0.89 s) pass without executing. #4
and #3 are what make them real. "Remote flake" means `RemoteImageLoadTest_{SingleImage,WorkspaceWithMesh}`:
the documented rotating failure when the three remote tests run back-to-back (W8 item 3/3b).
Compare failure *sets*, not totals.

**Merge order lives in [MERGE_ORDER.md](MERGE_ORDER.md)**, which keeps itself current whenever a
branch moves. As of this snapshot:
- all 10 pairs merge cleanly;
- #3 must come before #4, because #4 on its own fails upstream's never-registered
  `RandomForestBailOut`;
- #3 cannot be split: its test registration alone SEGFAULTs.

`staging/v460` = `upstream/master` + all five, and its tree is **byte-identical** to the pre-split
staging tip `archive/staging-v460-0904`. The split lost nothing and added nothing.

---

## 1 · `feature/cardiac-io` — 4D cardiac CTA / echo phase and metadata I/O

The existing branch, rebased from `679ba76a` onto `52ee94fa` with no conflicts. Old tip kept as
`archive/feature-cardiac-io-pre-rebase` (`9b5d9eb4`).

- **What it does:** reads the cardiac phase (`%R-R`, CT) or frame time (`ms`, echo) off 4D DICOM
  series instead of the hardcoded `0.05` temporal spacing; writes and reads it back through
  `.seq.nrrd` and NIfTI `pixdim[4]` plus a `<name>.json` sidecar; curates exported metadata to a
  non-PHI allow-list (age top-coded at ≥ 90 per HIPAA Safe Harbor); shows the value per time point
  in a "Phase / time:" GUI field; rejects ragged grids with a clear `IRISException`; adds
  `Documentation/Developer/Cardiac4DCTA_IO.md`.
- **Evidence:** end-to-end headless against the AVRP cohort, and GUI field checked by hand
  (`projects/4dcta_improvement/`). Built clean with no warnings on macOS and Linux when merged into
  staging.
- **Gap before a PR:** **no test in `Testing/` covers it.** The work was verified with a one-off
  driver script, and a one-off script catches no regressions. W1's done-criteria asked for a
  `.seq.nrrd` + `.nii.gz`/sidecar round-trip test that fails if the `%R-R` axis is dropped.
- **For Paul:**
  - The export curation changes what metadata users get out; it belongs in the release notes.
  - `TimePointProperties` `FormatVersion` goes 1 → 3. That is **not** a compatibility break: no
    reader validates it (W1 Q1). But a 4.4 build that re-saves the workspace silently drops the
    cardiac keys (W8 items 10, 11).

## 2 · `bug/linux-gcc-build` — build portability, VTK floor

| Commit | Change |
|---|---|
| `9ca38fcb` | GCC/libstdc++ portability: `QString::fromStdString` around `std::string` in `qDebug` streams, explicit `<QTimeZone>` / `<QDialogButtonBox>` includes, and Qt version guards on `qt_add_translations` (≥ 6.7) and `qt_generate_deploy_script` (≥ 6.5). No behavior change. |
| `fb65f2b9` | `CMake/standalone.cmake` VTK floor `9.3.1` → `9.5.2`, the version CI already builds. |

- **Evidence:** Ubuntu 24.04 / GCC 13, 766/766 targets, 0 errors, with no local patches (2026-07-31,
  on staging).
- **For Paul:** the VTK floor is a policy call, not a fix. Raising it affects anyone packaging against
  an older distro VTK. It is a separate commit, so it can be dropped without touching the portability
  fixes.

## 3 · `bug/rf-layer-crashes` — crashes after random-forest cancel and layer teardown

| Commit | Item | Change |
|---|---|---|
| `6afd0d10` | 14 | Register `test_RandomForestBailOut.js` in `TestingScripts.qrc`. It was added in 2018 (`062ba382`) and **has never run**. |
| `0f4cabc5` | 15 | Guard the null `m_ClassificationEngine` on Classify/Train and when leaving a mode that was never fully entered. |
| `76c857f7` | 15d | Use-after-free of `AbstractLayerTableRowModel::m_Layer`: invalidate it on the layer's `DeleteEvent`, synchronously. The regression came from our own leak fix `1712c6e7`, which turned it into a raw pointer. It is the 2018 crash coming back. Upstream had added the same `ApplyColorMap` guard, so that hunk was dropped. |
| `9e80001f` | 24 | Null-layer guards in `CheckState()`: `NO_ROLE` passes the `!= SOME_ROLE` guards. Split out of staging `038fa32b`. |

- **Tests that fail if this regresses:**
  - `RandomForestBailOut` (≈ 20 s). A sub-second pass means it did not run.
  - `MeshWorkspace` (≈ 47 s today, 54 s in August). It segfaulted on the first, incomplete version of
    the 15d fix.
- **Keep the test registration and the fixes together.** Registering the test without the fixes
  turns CI red: `upstream/master` + `6afd0d10` alone → `RandomForestBailOut` **SEGFAULT at 19.8 s**
  (measured 2026-09-24). With the whole branch it passes in 20.0 s.
- **Caveat (W8 item 22):** `RandomForestBailOut` paints nothing, so training throws and the test
  goes through the error-dialog → cancel path. That path is what exposes 15d, so the coverage is
  real, but it is not what the script was written to test.

## 4 · `test/harness-false-green` — a GUI test with a missing script reported Passed

- **What it does:** fixes the `GUI_TESTS` typo `4DContinuousRenderingD`, which pointed at a script
  that doesn't exist. It also stops `TestWorker::readScript()` falling through after queuing
  `NO_SUCH_TEST`; the fall-through let any GUI test with a missing script exit 0.
- **Effect, measured 2026-09-24:**
  - `4DContinuousRendering` really runs now (37.3 s on macOS; 36.5 s on Linux in July).
  - `ITK-SNAP --test ThisTestDoesNotExist` exits **3** instead of 0.
- **Depends on #3.** On its own, `RandomForestBailOut` now fails as "no such test", because upstream
  never registered its script. That is exactly the kind of test this branch exists to expose, but
  merge #3 first.

## 5 · `test/harness-gui-thread` — scripts can no longer touch widgets off the GUI thread

Upstream `dbf8e79f` fixed the same problem differently, and this branch builds on top of it. It keeps
Paul's helper API and his rewritten scripts unchanged, and adds `TestObjectProxy` underneath: scripts
never hold a raw widget, and every access hops to the GUI thread. The GUI-thread assertion sits at
the one choke point (`TestObjectProxy::target()`). Also included:

- `postKeyEventInternal` is moved out of `protected slots:`; QJSEngine exposes protected slots, so
  one line of JS could abort the app.
- A dangling pointer in `printChildren`.
- The teardown races.

It adds the `HarnessThreadSafety` test. Ported from `b3cf79d3`, `5f2825e4` and half of `038fa32b`,
following the resolution in the Sep 4 merge `6f5ae27c`.

- **Measured on the port, 2026-09-24:**
  - I deleted the GUI-thread hop from `findChild()`. `HarnessThreadSafety` then aborted with
    "'TestObjectProxy::target' ran on a worker thread", so the guard still fires after the port.
  - Standalone 32/35. `4DReplayWithMeshUpdate` failed once, then passed 5 reruns out of 5.
    `upstream/master` passed it only 3 of 5, failing at about 25 s. It is the known W8 item 2 flake,
    not a regression from this branch.

- **Needs a conversation before a PR.** It is about 700 lines of harness change competing with a
  design Paul just landed. The argument for it: his helpers fix today's scripts; the proxy makes the
  next off-thread access fail loudly instead of silently. Paul may reasonably say his helpers are
  enough.

---

## Not branched

| What | Why |
|---|---|
| `092022fb` — slider `NOTIFY` (W8 item 21) | Superseded: upstream `93aa9583` fixed it independently, and the Sep 4 merge took upstream's version. |
| `developer-doc` — W2 | **Already upstream**: PR #244 (`5e2984ff`, merged 2026-08-18). `itksnap-dls` has the same docs on `main`. |
| `cb6f692e`, `ea86df0d` on `test/dls_sam2` — async DLS | Not ready: two defects in `cb6f692e` (W1 Q4: undo gap, use-after-free). |
| 6 agentic commits on `sprint/caimi` | Out of scope for 4.6.0. |

## Push record

**Pushed 2026-09-24 to `jilei-hao/itksnap`:**
- The four new branches, with `-u origin`. They now track `origin`, not Paul's `master`.
- `feature/cardiac-io` (`9b5d9eb4` → `2fc0d9b8`) and `staging/v460` (`038fa32b` → `62588ffc`),
  force-pushed with leases pinned to those old tips.

The old tips survive as the local tags `archive/feature-cardiac-io-pre-rebase` and
`archive/staging-v460-0904`. They are not pushed. `9b5d9eb4` is still reachable on `origin` through
`sprint/caimi`; `038fa32b` is not.
