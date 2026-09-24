# RESUME — ITK-SNAP 4.6.0 · Goal (Jilei's choice): test Paul's seg_anchor logic on 4D segmentations

## Current state (read this paragraph first)

The 4.6.0 work lives on **five topic branches**, each cut from `upstream/master` @ `52ee94fa`, all
pushed to `jilei-hao/itksnap`:

- `feature/cardiac-io`
- `bug/linux-gcc-build`
- `bug/rf-layer-crashes`
- `test/harness-false-green`
- `test/harness-gui-thread`

Each builds and passes the suite on its own. **`staging/v460`** (`62588ffc`) is a testing-only merge
of all five: 34/35 on macOS, failing only the rotating remote flake. Jilei reviews and merges the
branches one at a time in the planning meeting. Where things are recorded:

- **`branches.md`** — what each branch contains, with evidence.
- **`MERGE_ORDER.md`** — the order, the measured constraints, and a Status section that a git hook
  regenerates whenever a branch moves. It currently reads "Needs attention: nothing".
- **SPRINT_PLAN's three rules at the top** govern everything: one topic branch per feature or fix,
  staging for testing only; Jilei picks each session's goal; `MERGE_ORDER.md` is updated on every
  branch change.

The global `/handoff` skill now also leaves the next goal to Jilei. The agentic API stays out of
scope, on `sprint/caimi`.

## This session's goal — chosen by Jilei at the 2026-09-24 handoff

> **"Testing Paul's new segmentation logic on 4D segmentations."**

Ask Jilei the open questions below before touching code; the goal is theirs, the scope isn't settled
yet.

**What "Paul's new segmentation logic" is.** The **seg_anchor** work, merged to `upstream/master` via
PRs #247–#249 (2026-08-27 → 09-03). The reference space now follows the *active segmentation* rather
than the main image, so segmentations need not share the main image's grid. Key commits:

| Commit | What it did |
|---|---|
| `431192f7`, `01a011d3` | Moved the reference space to the current segmentation |
| `effccaae` | Switching segmentations now updates the GUI |
| `d057beb9` | Different-spacing tests; `GenericImageData` renames (`GetReferenceSpace*` …) |
| `dbf8e79f` | Harness threading fix + `test_SegmentationSwitching.js` |
| `93aa9583`, `1ce5866b` | Zoom-to-fit uses the full extent |
| `454bcc97` | Stopped the view jumping on a segmentation change |
| `cf65a583` | The last seg layer is no longer made active on workspace load |
| `f9e25378` | The cursor may now sit outside the segmentation region |

**`upstream/seg_anchor` is 1 commit past master**: `88fb7aaa` "added box indicating reference space
bounds". Paul is still working there.

**What is covered today — 3D only.** `test_SegmentationSwitching.js` uses the MRIcrop 3D image with
two 0.4 mm hippocampus segmentations (`MRIcrop-seg-hippo{L,R}-04mm.nii.gz`). It checks:

- the label under the cursor;
- the per-layer resolution shown in the Layer Inspector;
- the 3D mesh;
- `{` / `}` switching.

**Nothing exercises the new logic with a 4D image or a 4D segmentation.**

**4D test data already in `Testing/TestData/`:**

- `img4d_11f.nii.gz` + `seg4d_11f.nii.gz`, with the per-label splits `seg4d_11f_label{1,2}.nii.gz`,
  plus the workspaces `img4d_11f.itksnap` and `img4d_11f_volren.itksnap`.
- `ultrasound_img4d.nii.gz` + `ultrasound_seg4d.nii.gz`, with `ultrasound_ws4d.itksnap`.
- Existing 4D tests: `4DContinuousRendering`, `4DReplayWithMeshUpdate`, `4DToMC`, `MCTo4D`.
- None of these has a segmentation whose grid differs from the main image's — that data will
  probably have to be made, e.g. a resampled `seg4d_11f`.

**Open questions for Jilei at the start:**

1. **Which base?** `upstream/master` (`52ee94fa`) or `upstream/seg_anchor` (`88fb7aaa`)? The topic
   branch should sit on whichever Paul will merge next.
2. **Which 4D cases matter?** For example:
   - a 4D seg on its own grid over a 4D main image;
   - switching between 4D segs with different spacing;
   - time-point changes while a non-anchored seg is active;
   - mesh/replay with a non-anchored 4D seg;
   - workspace save/load round-trip;
   - cardiac 4D CTA, which would pull in `feature/cardiac-io`.
3. **What should come out of it?** Regression tests only, bug reports to Paul, fixes, or all three?

**Where the work goes (rule 1):**

- Tests go on a new branch off the chosen base, e.g. `test/seg-anchor-4d`. Run
  `git branch --unset-upstream` on it immediately.
- Each bug found gets its own `bug/` branch.
- Add each new branch to `MERGE_ORDER.md`'s Queue with `verified-at -`.
- Push the branches, and get Status back to "Needs attention: nothing" before handoff.

## The open list — a reminder, not a queue

**Review queue — getting the five branches merged** (live state: `MERGE_ORDER.md`)

- **Measured order constraint:** `bug/rf-layer-crashes` must merge before `test/harness-false-green`,
  and it cannot be split.
- `feature/cardiac-io` has **no test in `Testing/`**. Add a `.seq.nrrd` + `.nii.gz`/sidecar
  round-trip test that fails if the `%R-R` axis is dropped. It pairs naturally with the 4D goal
  above.
- Linux/GCC run on the branches (the last Linux run was July, on `7cc60053`).
- Talk to Paul about `test/harness-gui-thread` before opening a PR — it competes with his
  `dbf8e79f`.
- PR descriptions from `branches.md` once branches are accepted.

**W1 — ready backlog** (`workstreams/merge-backlog.md`)

- Async DLS (`cb6f692e`, `ea86df0d` on `test/dls_sam2`). It is blocked on two defects in `cb6f692e`:
  an undo gap on throw, and a `this`-capturing lambda (a use-after-free). New branch
  `feature/dls-async`.
- Re-resolve the `Submodules/{c3d,greedy}` bump against current upstream.
- Delete the merged branches: W8 item 7's seven, plus `developer-doc`.

**Other workstreams**

- **W3** — itksnap-dls refactor: promote `itksnap-dls:feature/agentic-api` to `main`.
- **W4** auto-segmentation UI and **W5** propagation UI — both depend on W3; mockups are in
  `user_files/`.
- **W6** — free-rotation 2D/3D sync (#229, a bug). It may interact with seg_anchor's
  reference-space change; check.
- **W7** — cmesh integration.

**W8 — open items by cluster** (evidence in `workstreams/bugfixes.md`)

- **Harness can't report failure:** items 22, 23, 31, 32, 33, 34. Recheck each against Paul's
  rewritten helpers first.
- **Crashes:** 26, 27, 28, 29, 30, 35, and the `assert()`-only pattern (15b). Item 26 (a stale
  mesh-layer id across an IRIS↔SNAP switch) is layer/reference-space code that seg_anchor may have
  changed; re-check it.
- **Flaky tests:** 2 (`4DReplayWithMeshUpdate` — 3/5 on `upstream/master` too), 3 and 3b (remote
  tests).
- **Linux-only:** 18, 19, 20.
- **Cardiac metadata:** 8, 9, 10, 11.
- **Other:** 12 (DLS races), 16 (leak canary baseline).

**Release engineering**

- Version to beta, then `4.6.0`.
- `FormatVersion` decision.
- `ReleaseNotes.md` 4.6 section.
- Refresh `change_tracking.md` past `679ba76a` — 26 upstream commits, including all of seg_anchor,
  are unclassified.
- Wrapper `SUBMODULE_SYNC.md` / `CLAUDE.md`.

## Files to read first

1. **`MERGE_ORDER.md`** — read "Needs attention" first.
2. **`itksnap/Testing/GUI/Qt/Scripts/test_SegmentationSwitching.js`** and **`test_Library.js`** on
   `upstream/master` — the model for a new test, written against Paul's helper API.
3. **`git show d057beb9 dbf8e79f --stat`** and `Logic/Framework/GenericImageData.{h,cxx}` — the
   renamed reference-space API.
4. **`SPRINT_PLAN.md`** — the three rules at the top, §2, and §4 (the baseline).
5. **`branches.md`**, then **`PROGRESS_LOG.md`**'s 2026-09-24 entries.

## Known traps

- **A new test branch off `upstream/master` does NOT have the false-green fix.** It is on
  `test/harness-false-green`, which is unmerged. On `upstream/master`, a misnamed or unregistered
  script still reports **Passed**. Prove a new test really runs: check its duration, and break one
  assertion deliberately to see it fail.
- **Register a new script in BOTH `TestingScripts.qrc` and `GUI_TESTS`.**
- **Write new scripts against Paul's helper API** (`engine.clickChild`, `setChildProperty`,
  `validateChildProperty`, …). It works on `upstream/master` and also under our
  `test/harness-gui-thread` proxy, which kept the same API.
- **The seg_anchor rename (`d057beb9`) changed `GenericImageData` function names.** Code written
  against a pre-August tree won't compile on the new base.
- **Compare failure *sets*, never totals.** The remote tests fail at random when run back-to-back.
  `4DReplayWithMeshUpdate` is flaky on upstream as well (3/5).
- **A GUI test that passes in under a second is not running.** `RandomForestBailOut` takes about
  20 s, `MeshWorkspace` about 47 s, and `SegmentationSwitching` about 61 s.
- **`MeshWorkspace` is not a flake.** If it goes red, it's a real regression.
- **Build each branch in its own worktree + build dir** (full macOS build ≈ 4 min).
  `build-release/` follows the main checkout, which is on `staging/v460`.
- **The `MERGE_ORDER.md` hook fires on any branch ref update in `itksnap`**, including your scratch
  branches. It only rewrites the doc when Status actually changes.
- **zsh does not word-split `$var`.** Use arrays.
- **`ctest | tail` returns tail's exit status.** Redirect to a file instead.
- **Use an absolute `--testdir`.**
- **Build in the foreground on macOS.**
- **Never `pkill -f` from your own shell.**
- **Push submodules before bumping the wrapper pointer.** Check with `git branch -r --contains`.
- **`projects/user-support/` has uncommitted changes from another session.** Don't sweep them into
  a release-460 checkpoint.

## How to work

The bar is behavioural: reproduce, fix, and reproduce the fix. Ask an auditor to refute, not to
review. For a new test, prove it can fail. Run `/handoff` at the end rather than improvising it.
