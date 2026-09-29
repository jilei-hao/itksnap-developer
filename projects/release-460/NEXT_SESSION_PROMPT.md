# RESUME — ITK-SNAP 4.6.0 · Goal (Jilei's words): "review the current status of the release and decide what to do next"

## Current state (read this paragraph first)

The 4.6.0 work lives on **nine topic branches**, each cut from `upstream/master` @ `52ee94fa` (still the
upstream tip on 2026-09-29) and pushed to `jilei-hao/itksnap`. All nine are verified standalone on macOS.
`MERGE_ORDER.md` Status says: all 36 pairs merge cleanly; the one ordering constraint holds; **"Needs
attention: `staging/v460` needs a rebuild"**. `staging/v460` @ `d02236c3` has only the first eight.
Adding the ninth, `bug/remote-cache-test-datadir` (`6ff7a582`, fixes #258), is a force-push, so it is
Jilei's call. None of the nine has a PR yet: Paul's go-ahead comes first.

On GitHub (`upstream.md`):
- the outside PR **#241** (non-ASCII Windows user names) has our 4 commits and our comment, and Marco
  agreed. It waits for the planning meeting;
- **#257** (Windows missing-file exit), **#258** (the remote-cache test) and **#259** (CI: every PR is
  red, and tests never gate a run) were filed on 2026-09-28/29.

Upstream has also had new outside work that **nobody has triaged yet**: PRs #251–#255 and issue #256.
The last two sessions:
- the Windows box (2026-09-25 → 28): first MSVC build, the #241 review and fix-up;
- the Mac (2026-09-28 → 29): sync, the three issues, and the ninth branch's macOS run.

## This session's goal — named by Jilei at the 2026-09-29 handoff

> **"Next session let's do a review of the current status of the release and decide what to do
> next."**

The review is the work. **Deciding is Jilei's** (SPRINT_PLAN rule 2), so don't start code. A way to
run it:

1. **Refresh the facts first.** SPRINT_PLAN §2 is dated 2026-09-24 and still shows five branches.
   - Run the fetch loop in SPRINT_PLAN §7 for `itksnap`, `itksnap-dls`, `segflow4d` and
     `convert-mesh`.
   - Run `git -C itksnap log --oneline 52ee94fa..upstream/master`. If upstream moved, every branch
     needs a rebase (MERGE_ORDER "How to update", step 5).
   - Read MERGE_ORDER Status. The hook refreshes it on `git fetch origin`.
   - Check GitHub. What moved on #241 and #257–#259? What is new since #256?
     `gh issue list -R pyushkevich/itksnap --limit 15` and `gh pr list -R pyushkevich/itksnap`.
2. **Score each workstream** in SPRINT_PLAN §3 against the done-criteria in §4, and the
   release-engineering list. Use the cut line in §6: the minimum release is W1 + W2 + W8 plus release
   engineering.
3. **Sort what is left** into:
   - what we can do alone;
   - what needs Paul, which is the planning-meeting agenda;
   - what needs the Windows or the Linux box.
4. **Show it to Jilei and let Jilei choose.**
   - Refreshing SPRINT_PLAN §2 is allowed: it is a re-verified snapshot, not a re-plan.
   - Changing scope or the cut line is a planning act. Only do it if Jilei says so.
   - The private meeting page (https://claude.ai/artifact/QyivAN8NiDzadZ7hPKn6ut) still shows five
     branches. Offer to republish it from `branches.md`, but ask first.

## The open list — a reminder, not a queue

**Planning meeting: Paul's calls**
- Merge #241, retitling it and rewriting its description as Marco invited. Then `upstream.md`
  action 5, which includes rebasing `test/seg-anchor-4d`: it will conflict in `CMakeLists.txt`.
- The go-ahead to open PRs for our nine branches. Points to raise:
  - `test/harness-gui-thread` competes with Paul's `dbf8e79f`;
  - branches 5–6 change his seg_anchor code;
  - W8 38 is a design question.
- **W8 42:** keep upstream's Qt ≥ 6.9.3 floor, or lower it. It decides how Linux builds work.
- **#259:** the CI fixes, especially item 4, gating on tests.
- **W1:** the workspace `FormatVersion` 1→3 decision.

**Topic branches** (live state: `MERGE_ORDER.md`)
- Rebuild `staging/v460` with all nine (SPRINT_PLAN §7). This is a force-push, so it needs Jilei;
  hand over the exact `--force-with-lease=staging/v460:d02236c3` command.
- The ninth branch's Linux run. The recipe is below; it is blocked by W8 42 unless the quick route is
  used.
- `feature/cardiac-io` has **no test in `Testing/`**. Add a `.seq.nrrd` + `.nii.gz`/sidecar round-trip
  test that fails if the `%R-R` axis is dropped.
- A Linux/GCC run of all branches. The last one was in July; it is blocked by W8 42.
- Manual tests and code review of the branches, and an agent guide. That was the goal Jilei named on
  2026-09-25; it has not been started.

**Upstream** (`upstream.md`)
- #257: needs a fix, on a new topic branch with "Fixes #257". The code is `#ifdef WIN32`, so only the
  Windows box can verify it.
- #258: fixed by the ninth branch.
- #259: filed; the rest is Paul's.
- **Not triaged:**
  - PRs #251–#255 (aycibatuhan, five `BUG:` fixes, 2026-09-13);
  - issue #256 (Windows decimal comma breaks NRRD loading, with a proposed one-line fix in
    `main.cxx`);
  - older open PRs #243, #233, #196, #182, #128, #126.
  - CI for #251–#255 and for #241's head waits for a maintainer's "Approve and run".

**W8** (`workstreams/bugfixes.md`)
- New: 43 (GUI tests write into the real `%APPDATA%`), 44 (= #257).
- From seg_anchor:
  - 38: a same-size 3D segmentation with another header is pasted silently. Paul decides;
  - 39: `GetReferenceSpaceOrigin()` returns the spacing;
  - 40: adding a 4D segmentation prompts about unsaved changes;
  - 41: "TEMP DIAGNOSTIC" logging in `upstream/master`.
- Older clusters:
  - the harness can't report failure: 22, 23, 31–34;
  - crashes: 26–30, 35, 15b;
  - flaky: 2, 3 (= #258, fixed on branch 9), 3b;
  - Linux-only: 18–20;
  - cardiac metadata: 8–11;
  - other: 12, 16, 42.

**W1: ready backlog** (`workstreams/merge-backlog.md`)
- Async DLS (`cb6f692e`, `ea86df0d` on `test/dls_sam2`) is blocked on two defects (W1 Q4). It would
  get a new branch, `feature/dls-async`.
- Re-resolve the `Submodules/{c3d,greedy}` bump against current upstream.
- Delete merged branches: W8 item 7's seven, plus `developer-doc`.

**Other workstreams**
- W3: the itksnap-dls refactor. W4 and W5 (auto-seg and propagation UI) depend on it.
- W6: free-rotation sync (#229).
- W7: cmesh.

**Release engineering** (SPRINT_PLAN §3)
- Version to beta, then `4.6.0`.
- The 4.6 section of `ReleaseNotes.md`.
- Refresh `change_tracking.md` past `679ba76a`.
- Wrapper `SUBMODULE_SYNC.md` / `CLAUDE.md`.

## Linux run of the ninth branch (recorded at Jilei's request, 2026-09-28)

What to show: without the branch, `_Cache` fails and writes into `~/.itksnap.org`. With it, the test
passes and `~/.itksnap.org` is left alone.

- **Blocker, W8 42:** upstream needs Qt ≥ 6.9.3, and the box has apt Qt 6.4.2. Two ways around it:
  - **(a) Quick, test-only (recommended for this item).** `remote_image_load_test` is a Logic test, and
    Qt's version does not matter to it.
    - Make a throwaway detached worktree of `bug/linux-gcc-build`. It carries the GCC fixes and the Qt
      ≥ 6.7 / ≥ 6.5 guards that apt Qt needs to configure.
    - In `CMake/standalone.cmake`, lower the five `FIND_PACKAGE(Qt6… 6.9.3 REQUIRED)` calls to `6.4`.
      **This is local only: never commit it.**
    - Configure against `vtk-dev/installed/lib/cmake/vtk-9.5`, and build only
      `ninja remote_image_load_test`.
    - Run the baseline first. Then `git merge --no-edit bug/remote-cache-test-datadir` on the detached
      HEAD, rebuild the target, and run again.
  - **(b) Full.** Install Qt 6.9.3 (aqtinstall), rebuild VTK 9.5.2 against it (its Qt module links Qt),
    then run the full `xvfb-run -a ctest`. That is the bigger item "A Linux/GCC run of all branches".
- **Checks, in this order:**
  1. **Back up `~/.itksnap.org`.** Snapshot it with
     `find ~/.itksnap.org -exec stat -c '%Y %s %n' {} + | sort`.
  2. **Baseline:** `ctest -R RemoteImageLoadTest_Cache -V` should fail with
     `FAIL: CacheMetadata.xml not created after first download`, and new files should appear under
     `~/.itksnap.org/ITK-SNAP/Cache`.
  3. **With the branch:**
     - `ctest -R RemoteImageLoadTest -V` passes all three. Rerun one that fails on the p25 flake
       (W8 3b).
     - The log shows `Clearing cache at <build>/.itksnap_test/.itksnap.org/ITK-SNAP`: on Linux the `~`
       is expanded from the redirected `$HOME`.
     - The snapshot is unchanged.
  4. **Guard proof:** comment out `RedirectApplicationDataDirectory();` in `main()`, and rebuild.
     `_Cache` must fail with "is outside the test directory" before it clears anything, and
     `~/.itksnap.org` must be unchanged. Then revert.
  5. **Record** in `branches.md` §9 and W8 3. Commenting on #258 publishes, so ask Jilei first.

## Files to read first

1. `SPRINT_PLAN.md`:
   - the three rules at the top;
   - §3, workstreams and release engineering;
   - §4, the done-criteria;
   - §6, the cut line;
   - §7, how to refresh.
2. `MERGE_ORDER.md`: Status, then Queue.
3. `branches.md`: the summary table; one row per branch, with its test result.
4. `upstream.md`: every GitHub item, and the merge rule.
5. `workstreams/bugfixes.md` (W8) and `workstreams/README.md`.
6. `change_tracking.md`: what has merged since 4.4.0. It is stale past `679ba76a`.
7. `PROGRESS_LOG.md`, the entries since "2026-09-24", for how we got here.

## Known traps

**Release and GitHub**
- **Never merge a PR, ours or an outside one, through `gh`, the API or the web UI.** Merges happen only
  at the planning meeting, in person. Every issue, comment, PR or push to someone else's branch needs
  Jilei's OK first.
- **A green CI run does not mean the tests passed** (#259). The green `master` build of `52ee94fa` had
  3 failing tests. Every PR is red whatever the change. The Gatekeeper reads step `outcome`, and the
  Actions API shows a `continue-on-error` step as `success` even when it failed.
- **Force-pushing `staging/v460` needs Jilei.** Don't bump the wrapper's `itksnap` pointer to an
  unpushed commit. Push submodules before bumping the wrapper pointer.
- **SPRINT_PLAN §2 goes stale fastest.** Re-verify it with §7 before trusting a branch count.

**Testing**
- **Compare failure *sets*, never totals.** The three remote-image tests rotate (W8 3b), and
  `4DReplayWithMeshUpdate` is flaky upstream. `MeshWorkspace` is not a flake.
- **A GUI test that passes in under a second is not running.** Reference times: `RandomForestBailOut`
  ≈ 20 s, `MeshWorkspace` ≈ 47 s, `SegmentationSwitching` ≈ 61 s, `SegAnchor4DSwitching` ≈ 73 s.
  Upstream itself has two false passes: `RandomForestBailOut` and `4DContinuousRenderingD`.
- **A branch off `upstream/master` lacks the false-green fix.** Register a new script in BOTH
  `TestingScripts.qrc` and `GUI_TESTS`, and break one assertion to see it fail.
- **Build each branch in its own worktree and build directory.**
- **Several branches edit `CMakeLists.txt` and `TestingScripts.qrc`.** Insert at an anchor no other
  branch uses. `IRISApplicationTest` is used twice: by `test/seg-anchor-4d` and by #241. Check pairs
  with `git merge-tree --write-tree`.
- **Test scripts are compiled into the `ITK-SNAP` binary** (qrc). Rebuild after editing a script.
- **The GUI harness has no scratch directory.** Test save/reload as a C++ Logic test with `${TEMP}`.
- **Selecting a segmentation row in the Layer Inspector makes it the active segmentation.**
- **Grids at exactly 2x put voxel centres on 0.5 boundaries.** Pick probe points that are tie-free.
- **SimpleITK `GetImageFromArray` on a 4D array gives a 3D image.** Use `JoinSeries`.

**Platforms**
- **Windows:**
  - point `APPDATA` at a scratch folder for any `ctest` or GUI run (W8 3, W8 43);
  - `ITK-SNAP -g <missing file>` exits silently (#257);
  - there is no `gh` on that box.
  - More traps are in the Windows section of the wrapper `CLAUDE.md` and `PROGRESS_LOG.md`
    2026-09-25.
- **Linux:** apt's Qt 6.4.2 can't configure `upstream/master` (W8 42).
- **ITK's kwsys already decodes UTF-8 on Windows.** Non-ASCII bugs there are about `argv`, `getenv`
  and the `A` Win32 functions, which follow the process code page.

**Shell (Mac)**
- zsh does not word-split `$var`. A bare `====` is expanded as `=cmd`, so quote separators.
- `ctest | tail` returns tail's exit status. Use an absolute `--testdir`.
- **The Bash tool stops at 10 minutes.** A full `ctest` takes about 9–12, so split it:
  `ctest -I 1,22`, then `ctest -I 23,34`.
- Build in the foreground on macOS. A clean branch build fits in one 10-minute call.
- Never `pkill -f` from your own shell.
- The `MERGE_ORDER.md` hook fires on any branch ref update in `itksnap`.

## How to work

Start by confirming the goal with Jilei. Then refresh the facts, and only then summarize. Keep what
you checked apart from what you inferred. Lead with the answer, in plain language.

Run `/handoff` at the end.
