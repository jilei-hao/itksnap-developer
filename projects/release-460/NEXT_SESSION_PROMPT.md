# RESUME — ITK-SNAP 4.6.0 · Goal (Jilei's choice): manual tests, code review, maybe a guide for AI agents

## Current state (read this paragraph first)

The 4.6.0 work lives on **eight topic branches**. Each is cut from `upstream/master` @ `52ee94fa`,
passes the full suite on its own, and is pushed to `jilei-hao/itksnap`:

1. `bug/linux-gcc-build`
2. `bug/rf-layer-crashes`
3. `test/harness-false-green`
4. `test/seg-anchor-4d`
5. `bug/full-extent-off-by-one`
6. `bug/seg3d-into-4d-check`
7. `feature/cardiac-io`
8. `test/harness-gui-thread`

That is the recommended merge order. The last session added numbers 4–6, which test Paul's
seg_anchor work (segmentations on their own grid) with 4D data and fix two small bugs in it.

**`staging/v460` @ `d02236c3`** (all eight merged) is pushed and passes **40/41** on macOS, failing
only the rotating remote flake. The wrapper's `itksnap` pointer is at `d02236c3`.
`MERGE_ORDER.md` Status reads "Needs attention: nothing".

Where things are recorded:
- **`branches.md`**: every branch has a plain-language **PR description** for the community, then
  review notes.
- **`MERGE_ORDER.md`**: order, constraints, and live status.
- **`workstreams/bugfixes.md`**: W8 items, including new 36–41.

The agentic API stays out of scope, on `sprint/caimi`.

## This session's goal — named by Jilei at the 2026-09-25 handoff

> **"Manual tests and code review, and probably write some guide for AI agents to work with this
> project."**

Ask Jilei before starting:
1. **Which branches** to manually test and review? All eight, or the three new ones?
2. **What to try by hand?**
3. **Where the agent guide should live and who it is for.** Options:
   - `itksnap/CLAUDE.md` (upstream's, already there);
   - an `AGENTS.md` in `itksnap`;
   - the wrapper's `CLAUDE.md`;
   - `Documentation/Developer/`.

   Should it go upstream as its own topic branch (rule 1)?

**Ready-made material for each part:**

- **Manual tests.** Builds exist:
  - `build-release/` = staging `d02236c3`, all eight merged — the one to try things in;
  - `build-seg-anchor-4d/`, `build-full-extent-off-by-one/`, `build-seg3d-into-4d-check/` = each
    branch alone.

  Worth trying by hand:
  - **W8 36:** open a single image. The cursor boxes should run 1..N. Before the fix they ran 0..N,
    so scroll or arrow-key past the first slice. `branches.md` §7 has a before/after table; its
    click, scroll and zoom rows come from reading the code and were never checked in the app.
  - **W8 37:** open `img4d_11f.nii.gz` and `seg4d_11f_label1.nii.gz`, then open a 3D segmentation of
    another size. Expect "Mismatched Dimensions".
  - **seg_anchor with 4D data:** open `Testing/TestData/img4d_11f_seganchor.itksnap`. Switch with
    `{`/`}`, play the 4D replay, and step through time points.
  - **cardiac-io "Phase / time" field:** needs the cardiac data under `projects/4dcta_improvement/`.
- **Code review.** The diffs are `git -C itksnap diff upstream/master <branch>`. The three new ones
  are small:
  - `6a72f6a1`: `GenericImageData::GetFullExtentImageRegion` plus a test.
  - `635bd1ac`: `LoadSegmentationImageDelegate::ValidateHeader` plus a test.
  - `0b671e86`: tests only.

  PROGRESS_LOG 2026-09-25 lists what an adversarial reviewer already caught. `/code-review` is
  available.
- **Agent guide.** The raw material already exists:
  - "Known traps" below, and the traps in earlier PROGRESS_LOG entries;
  - the wrapper `CLAUDE.md` (build, Linux notes, test status);
  - `itksnap/CLAUDE.md` (architecture, DLS threading notes);
  - the three sprint rules in SPRINT_PLAN;
  - `Documentation/Developer/` (W2 docs, merged as PR #244).

## The open list — a reminder, not a queue

**Getting the eight branches merged** (live state: `MERGE_ORDER.md`)

- SPRINT_PLAN §2 still shows five branches and the old staging tip. Refresh it with §7.
- **Measured order constraint:** `bug/rf-layer-crashes` must merge before `test/harness-false-green`,
  and it cannot be split.
- `feature/cardiac-io` has **no test in `Testing/`**. Add a `.seq.nrrd` + `.nii.gz`/sidecar
  round-trip test that fails if the `%R-R` axis is dropped. Its PR description already says so.
- Run the branches on Linux/GCC. The last Linux run was in July.
- Talk to Paul before opening PRs:
  - `test/harness-gui-thread` competes with his `dbf8e79f`;
  - branches 5–6 change his seg_anchor code, and W8 38 is a design question for him.
- Republish the private meeting page (https://claude.ai/artifact/QyivAN8NiDzadZ7hPKn6ut) from
  `branches.md`. It still shows five branches.

**W8, new from the seg_anchor work** (`workstreams/bugfixes.md`)

- 38: a same-size 3D seg with another header is pasted into a 4D seg silently. Paul decides: refuse,
  resample, or add it as a layer.
- 39: `GetReferenceSpaceOrigin()` returns the spacing. It has no callers.
- 40: adding a 4D seg prompts about unsaved changes it can't overwrite.
- 41: "TEMP DIAGNOSTIC" `FileOpen` logging to `~/itksnap-url-debug.log` in `upstream/master`.

**W1 — ready backlog** (`workstreams/merge-backlog.md`)

- Async DLS (`cb6f692e`, `ea86df0d` on `test/dls_sam2`). It is blocked on two defects in
  `cb6f692e` (W1 Q4). New branch `feature/dls-async`.
- Re-resolve the `Submodules/{c3d,greedy}` bump against current upstream.
- Delete merged branches: W8 item 7's seven, plus `developer-doc`.

**Other workstreams**

- **W3:** the itksnap-dls refactor (promote `feature/agentic-api` to `main`).
- **W4 / W5:** auto-seg and propagation UI. Both depend on W3.
- **W6:** free-rotation sync (#229). It may interact with the reference-space change; check.
- **W7:** cmesh.

**W8 — older open items by cluster**

- **Harness can't report failure:** 22, 23, 31, 32, 33, 34.
- **Crashes:** 26, 27, 28, 29, 30, 35, and 15b.
- **Flaky:** 2, 3, 3b.
- **Linux-only:** 18, 19, 20.
- **Cardiac metadata:** 8, 9, 10, 11.
- **Other:** 12, 16.

**Release engineering**

- Version to beta, then `4.6.0`.
- The `FormatVersion` decision.
- `ReleaseNotes.md` 4.6 section. The PR descriptions in `branches.md` are good raw material.
- Refresh `change_tracking.md` past `679ba76a`.
- Wrapper `SUBMODULE_SYNC.md` / `CLAUDE.md`.

## Files to read first

1. `MERGE_ORDER.md` — Status first.
2. `branches.md` — PR descriptions plus review notes, for all eight branches.
3. `PROGRESS_LOG.md`, the 2026-09-25 entries: what was tested, surprises, and decisions.
4. `workstreams/bugfixes.md`, items 36–41.
5. SPRINT_PLAN's three rules at the top.

## Known traps

**New from the last session**

- **Selecting a segmentation row in the Layer Inspector makes it the active segmentation**, which
  moves the reference space and remaps the cursor. `getLayerResolutionInfo(row)` in
  `test_Library.js` selects the row, so calling it on a non-active segmentation switches
  segmentations.
- **Test scripts are compiled into the `ITK-SNAP` binary** (qrc). After editing a script, rebuild
  `ITK-SNAP` before running it, or the old script runs.
- **The GUI harness has no scratch directory.** A relative filename in a save dialog resolves against
  the dialog's history directory, not the working directory. Test save/reload as a C++ Logic test
  with `${TEMP}`; see `Testing/Logic/SegAnchor4DWorkspaceTest.cxx`.
- **Grids at exactly 2x put voxel centres on 0.5 boundaries.** Cursor remapping between such grids is
  a rounding tie. Pick probe points that are tie-free both ways.
- **Several branches edit `CMakeLists.txt` and `TestingScripts.qrc`.** Insert at an anchor no other
  branch uses, then check every pair with `git merge-tree --write-tree`.
- **Force-pushing `staging/v460` needs Jilei**; the auto-mode classifier blocks it. Hand over the
  exact `--force-with-lease=staging/v460:<old tip>` command. Don't bump the wrapper `itksnap`
  pointer to an unpushed commit.
- **SimpleITK `GetImageFromArray` on a 4D array gives a 3D image.** Build 4D images with
  `JoinSeries`.

**Standing**

- **A branch off `upstream/master` lacks the false-green fix**, so a misnamed or unregistered script
  reports Passed. Register a new script in BOTH `TestingScripts.qrc` and `GUI_TESTS`, check its run
  time, and break one assertion to see it fail.
- **A GUI test that passes in under a second is not running.** Reference times: `RandomForestBailOut`
  ≈ 20 s, `MeshWorkspace` ≈ 47 s, `SegmentationSwitching` ≈ 61 s, `SegAnchor4DSwitching` ≈ 73 s.
- **Compare failure *sets*, never totals.** The remote tests rotate. `4DReplayWithMeshUpdate` is
  flaky upstream (3/5).
- **`MeshWorkspace` is not a flake.** If it fails, it's a real regression.
- **Build each branch in its own worktree and build directory.** They are under `worktrees/` and
  `build-<name>/`, and are untracked in the wrapper. `build-release/` follows the main checkout
  (`staging/v460`).
- **The `MERGE_ORDER.md` hook fires on any branch ref update in `itksnap`.**
- **Shell and process habits:**
  - zsh does not word-split `$var`; use arrays.
  - `ctest | tail` returns tail's exit status.
  - Use an absolute `--testdir`.
  - Build in the foreground on macOS.
  - Never `pkill -f` from your own shell.
- **Push submodules before bumping the wrapper pointer.**
- **`projects/user-support/` has uncommitted changes from another session.** Don't sweep them into
  a checkpoint.

## How to work

The bar is behavioural: reproduce, fix, and reproduce the fix. Ask an auditor to refute, not to
review. For a new test, prove it can fail. Run `/handoff` at the end rather than improvising it.
