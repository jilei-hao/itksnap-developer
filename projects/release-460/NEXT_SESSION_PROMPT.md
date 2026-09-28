# RESUME — ITK-SNAP 4.6.0 · Goal (Jilei's words): continue the PR #241 / upstream work on the Mac

## Current state (read this paragraph first)

The 4.6.0 work now lives on **nine topic branches**, each cut from `upstream/master` @ `52ee94fa` and
pushed to `jilei-hao/itksnap`:
- the eight from 2026-09-25, unchanged;
- **the ninth, `bug/remote-cache-test-datadir`** (`6ff7a582`, W8 3), pushed and recorded 2026-09-28.

**`staging/v460` @ `d02236c3`** holds the first eight only. **`MERGE_ORDER.md` Status is stale**: the
Windows box has no Python to regenerate it. See "The ninth branch" below.

The last session ran on the **Windows build box** (2026-09-25 → 28). It did not work on the previous
goal (manual tests of our branches, code review, agent guide), because Jilei redirected it to an
**outside PR**:
- **[pyushkevich/itksnap#241](https://github.com/pyushkevich/itksnap/pull/241)** "Support non-ASCII
  characters in Windows user names", by Marco Duering, milestone v4.6.0. It was reviewed and tested on
  Windows ([reviews/pr-241.md](reviews/pr-241.md)).
- Jilei chose to fix it up himself rather than start a review round. Four commits were pushed to the
  contributor's branch (`88def486..b287abe6`): `DOC:` correct mechanism, `BUG:` length off by one,
  `ENH:` a real test, `ENH:` `itksnap-wt` manifest.
- **What still has to happen on GitHub is queued in [upstream.md](upstream.md).** That file is new and
  tracks every upstream issue and PR. Actions 1–3 are `gh` commands for the Mac: two issues to create,
  then one comment on #241. **Action 4, the merge, happens at the planning meeting, in person.**
- **W8 43 and 44 are new** (`workstreams/bugfixes.md`). 44 (`-g` with a missing file closes ITK-SNAP
  silently on Windows) has an issue draft ready.

**#241 is based on master as of 2026-08-19 (`a86e42da`), 19 commits behind today's master.** Its
merge commit merged master before seg_anchor #247–#249 landed. GitHub reports it mergeable. The
Windows staging + PR build was the test against current master: 40/42, with no PR-caused failures.
`pr/241-update` exists only on the Windows box. On the Mac, fetch the PR itself with
`git -C itksnap fetch upstream pull/241/head:pr/241`; it includes our four commits.

**The ninth branch: rule 3 is not finished.** It is recorded in Queue (`verified-at` = `-`), in
`branches.md` §9 and in W8 3. Still to do, in `MERGE_ORDER.md`'s "How to update" order:
1. **Regenerate Status.** `git fetch origin` fires the hook. Then delete the "Stale since 2026-09-28"
   note above the AUTO block.
2. **Verify it standalone:** `upstream/master` + branch, full `ctest`, comparing the failure set. Do it
   on macOS, where the test must keep passing and the redirect goes through `$HOME`. Then set
   `verified-at` to `6ff7a582` and update `branches.md` §9's "Testing" line.
3. **Rebuild `staging/v460`** with all nine (SPRINT_PLAN §7). That is a **force-push, so it needs
   Jilei**: hand over the exact `--force-with-lease=staging/v460:d02236c3` command. The evidence so far
   is the Windows local merge `22b009e0` (`d02236c3` + this branch), which ran 41/41.

## This session's goal — named by Jilei at the 2026-09-28 handoff

> **"I'll continue the work on my mac."**

Ask Jilei before starting (rule 2):
1. **Run [upstream.md](upstream.md) actions 1–3 now?**
   - Each one publishes on GitHub. Confirm before running; one yes may cover the group.
   - Run them from the wrapper root.
   - Then put the new issue numbers into `upstream.md`, W8 44 and, optionally, the #241 comment before
     action 3.
2. **Then what?** Possibilities:
   - the W8 44 fix, on a new topic branch off `upstream/master` with "Fixes #N". The code is
     `#ifdef WIN32`, so it can only be verified on the Windows box;
   - the ninth branch's remaining rule-3 steps (above);
   - the previous goal: manual tests and code review of the topic branches, and the agent guide.

**Never merge a PR, ours or an outside one, through `gh`, the API or the web UI.** Merges happen only
at the planning meeting, in person (Jilei, 2026-09-28; the rule is in `upstream.md` too). After Jilei
says #241 is merged, do `upstream.md` action 5:
- rebase `test/seg-anchor-4d`, which will conflict with the new master in `CMakeLists.txt` because both
  add a Logic test right after `IRISApplicationTest`;
- update `MERGE_ORDER.md`;
- add #241 to `change_tracking.md`.

## The open list — a reminder, not a queue

**Upstream (GitHub):** see [upstream.md](upstream.md).
- Issue: Windows missing-file exit (W8 44).
- Issue: CI for fork PRs. Every fork PR is red, and the Gatekeeper never checks test results. Its
  item 4 is Paul's call.
- #241: comment, then the meeting.

**Getting the nine branches merged** (live state: `MERGE_ORDER.md`)
- SPRINT_PLAN §2 still shows five branches and the old staging tip. Refresh it with §7.
- **Measured order constraint:** `bug/rf-layer-crashes` must merge before `test/harness-false-green`,
  and it cannot be split.
- `feature/cardiac-io` has **no test in `Testing/`**. Add a `.seq.nrrd` + `.nii.gz`/sidecar round-trip
  test that fails if the `%R-R` axis is dropped.
- Run the branches on Linux/GCC. The last Linux run was in July, and W8 42 (the Qt ≥ 6.9.3 floor)
  breaks the apt recipe.
- Talk to Paul before opening PRs:
  - `test/harness-gui-thread` competes with his `dbf8e79f`;
  - branches 5–6 change his seg_anchor code, and W8 38 is a design question for him.
- Republish the private meeting page (https://claude.ai/artifact/QyivAN8NiDzadZ7hPKn6ut) from
  `branches.md`. It still shows five branches.

**W8** (`workstreams/bugfixes.md`)
- **New:**
  - 43: GUI tests write into the real `%APPDATA%`;
  - 44: Windows missing-file exit.
- **From seg_anchor:**
  - 38: same-size 3D seg with another header, pasted silently. Paul decides;
  - 39: `GetReferenceSpaceOrigin()` returns the spacing;
  - 40: adding a 4D seg prompts about unsaved changes;
  - 41: "TEMP DIAGNOSTIC" logging in `upstream/master`.
- **Older clusters:**
  - harness can't report failure: 22, 23, 31–34;
  - crashes: 26–30, 35, 15b;
  - flaky: 2, 3 (fixed on `bug/remote-cache-test-datadir`), 3b;
  - Linux-only: 18–20;
  - cardiac metadata: 8–11;
  - other: 12, 16, 42.

**W1 — ready backlog** (`workstreams/merge-backlog.md`)
- Async DLS (`cb6f692e`, `ea86df0d` on `test/dls_sam2`) is blocked on two defects (W1 Q4). New branch:
  `feature/dls-async`.
- Re-resolve the `Submodules/{c3d,greedy}` bump against current upstream.
- Delete merged branches: W8 item 7's seven, plus `developer-doc`.

**Other workstreams:**
- W3: the itksnap-dls refactor.
- W4 / W5: auto-seg and propagation UI, which depend on W3.
- W6: free-rotation sync (#229).
- W7: cmesh.

**Release engineering:**
- Version to beta, then `4.6.0`.
- The `FormatVersion` decision.
- The 4.6 section of `ReleaseNotes.md`.
- Refresh `change_tracking.md` past `679ba76a`.
- Wrapper `SUBMODULE_SYNC.md` / `CLAUDE.md`.

## Files to read first

1. [upstream.md](upstream.md): pending GitHub actions and the merge rule.
2. [reviews/pr-241.md](reviews/pr-241.md) §1 (plain-language verdict) and §7 (what was changed, with
   evidence).
3. `PROGRESS_LOG.md`, the entries from "2026-09-25 (PR #241)" through "2026-09-28 (handoff)".
4. `MERGE_ORDER.md`: Status first.
5. SPRINT_PLAN's three rules at the top.

## Known traps

**New from the Windows box (2026-09-25 → 28)**

- **Windows paths: ITK's kwsys already decodes UTF-8.** `KWSYS_ENCODING_DEFAULT_CODEPAGE=CP_UTF8` has
  been set since the ITK 4.5 era, and VTK does the same. Non-ASCII bugs on Windows are about `argv`,
  `getenv` and the `A` Win32 functions, which follow the process code page. That code page is UTF-8
  only in executables that carry `Utilities/Win32/itksnap.manifest`: after #241, `ITK-SNAP`,
  `nonascii_path_test` and `itksnap-wt`.
- **On Windows, `ITK-SNAP -g <missing file>` exits silently** with 0xC0000409 (W8 44). A test or script
  that launches ITK-SNAP with a bad path "crashes" for this reason, not for its own.
- **A green CI run does not mean the tests passed.** The Gatekeeper checks only configure/build and
  submit. Fork PRs are always red, whatever the change.
- **On Windows, point `APPDATA` at a scratch folder** for any `ctest` or GUI run. Otherwise the tests
  write into the real profile (W8 3, W8 43).
- **A fresh `APPDATA` shows two first-run modals** outside test mode: update checks, and the layout
  reminder. They block a normal close, and then preferences are not saved.
- **The Windows box has no `gh`.** GitHub work goes through `upstream.md` on the Mac. Read-only REST
  calls work without auth; Actions logs need auth.
- **Git Bash on Windows mangles `rev:.path` arguments**, such as `git show pr/241:.clang-format`. Set
  `MSYS_NO_PATHCONV=1`.
- **Windows PowerShell 5.1:** `Start-Process -PassThru` gives an empty `ExitCode` unless `$p.Handle` is
  read first, and variable names are case-insensitive (`$sp` is `$SP`).
- **`.clang-format` pins 19.1.4.** The Windows box has only 18.1.8 (VS Code cpptools); 12 keys have to
  be dropped or renamed to use it.

**Standing**

- **Selecting a segmentation row in the Layer Inspector makes it the active segmentation.**
  `getLayerResolutionInfo(row)` in `test_Library.js` does this.
- **Test scripts are compiled into the `ITK-SNAP` binary** (qrc). Rebuild after editing a script.
- **The GUI harness has no scratch directory.** Test save/reload as a C++ Logic test with `${TEMP}`.
- **Grids at exactly 2x put voxel centres on 0.5 boundaries.** Pick probe points that are tie-free.
- **Several branches edit `CMakeLists.txt` and `TestingScripts.qrc`.** Insert at an anchor no other
  branch uses. `IRISApplicationTest` is now used twice: `test/seg-anchor-4d` and #241. Check pairs with
  `git merge-tree --write-tree`.
- **Force-pushing `staging/v460` needs Jilei.** Don't bump the wrapper's `itksnap` pointer to an
  unpushed commit.
- **SimpleITK `GetImageFromArray` on a 4D array gives a 3D image.** Use `JoinSeries`.
- **A branch off `upstream/master` lacks the false-green fix.** Register a new script in BOTH
  `TestingScripts.qrc` and `GUI_TESTS`, and break one assertion to see it fail.
- **A GUI test that passes in under a second is not running.** Reference times: `RandomForestBailOut`
  ≈ 20 s, `MeshWorkspace` ≈ 47 s, `SegmentationSwitching` ≈ 61 s, `SegAnchor4DSwitching` ≈ 73 s.
- **Compare failure *sets*, never totals.** The remote tests rotate. `4DReplayWithMeshUpdate` is flaky
  upstream.
- **`MeshWorkspace` is not a flake.**
- **Build each branch in its own worktree and build directory.**
- **The `MERGE_ORDER.md` hook fires on any branch ref update in `itksnap`** (on the Mac).
- **Shell habits:**
  - zsh does not word-split `$var`;
  - `ctest | tail` returns tail's exit status;
  - use an absolute `--testdir`;
  - build in the foreground on macOS;
  - never `pkill -f` from your own shell.
- **Push submodules before bumping the wrapper pointer.**

## How to work

The bar is behavioural: reproduce, fix, and reproduce the fix. For a new test, prove it can fail.
#241's test was checked by stripping the manifest and by putting the old guard back.

Confirm every publishing action with Jilei: an issue, a comment, a PR, or a push to someone else's
branch. **Never merge a PR.**

Run `/handoff` at the end.
