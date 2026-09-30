# RESUME — ITK-SNAP 4.6.0 · no goal chosen yet: ask Jilei first

## Current state (read this paragraph first)

The 4.6.0 work lives on **eleven topic branches**. Each is cut from `upstream/master` @ `52ee94fa`,
which is still the upstream tip on 2026-09-30, and pushed to `jilei-hao/itksnap`. All eleven are
verified standalone on macOS, and all 55 pairs merge cleanly. **`staging/v460` @ `b2f46eaa`** is
upstream plus all eleven. It is pushed, and passed macOS `ctest` **43/45**; the only failures were
the two remote quantile flakes. `MERGE_ORDER.md` Status reads "Needs attention: nothing". None of the
eleven has a PR yet: Paul's go-ahead comes first.

On GitHub:
- the **v4.6.0 milestone** holds everything for the planning meeting: 23 open items;
- **issue #260** is filed (the Language preference; branch 10);
- **#196** (zh_CN translation) is now mergeable, after we merged master into its branch;
- six outside PRs (#243, #251–#255) and Paul's #233 are reviewed, with **draft comments that are not
  posted**.

**#229** (free rotation) is diagnosed and its design is decided, but not implemented.

## Session goal

**None chosen.** Jilei picks each session's goal (SPRINT_PLAN rule 2). Show the open list below,
grouped as it is, and ask which item to work on before touching code. If the chosen item depends on
something unfinished, say so first.

## The open list — a reminder, not a queue

**Planning meeting: Paul's calls** (the meeting pages are below)
- **Our eleven branches:** the go-ahead to open PRs. Points to raise:
  - `test/harness-gui-thread` competes with Paul's `dbf8e79f`;
  - `bug/full-extent-off-by-one` and `bug/seg3d-into-4d-check` change his seg_anchor code;
  - `feature/ui-language-setting` has one question (see #260 below).
- **#241:** merge it, retitling it and rewriting its description as Marco invited. Then
  `upstream.md` action 5, which includes rebasing `test/seg-anchor-4d`: it will conflict in
  `CMakeLists.txt`.
- **Outside PRs** (`reviews/outside-prs-2026-09.md`):
  - #251, #252, #253: merge;
  - #254: merge after "Fixes" becomes "Refs #212";
  - #243: merge after a 5-line fallback;
  - #255: Paul decides. He disagreed in #210, and #260 is the alternative.
- **#196:** merge. It is mergeable now at +33/−33; see `reviews/pr-196.md`.
- **#233** (Paul's own PR): merge. It fixes a crash we reproduced on master. There are two
  suggestions: a grid check, and a message instead of a silent no-op. See `reviews/pr-233.md`.
- **#260:** should the Language preference also change number and date formats, as `--lang` does?
  The branch changes the translation only.
- **W8 45:** Tools › Reorient Image no longer changes the main image (seg_anchor), measured on
  master. There is **no GitHub issue yet**; filing one needs Jilei's OK.
- **The rest:**
  - W8 42: keep the Qt ≥ 6.9.3 floor, or lower it?
  - #259: CI gating;
  - W8 38 (a design question);
  - W8 41: the TEMP DIAGNOSTIC logging;
  - moving the version to beta;
  - the W1 `FormatVersion` checkbox. W1 Q1 closed it on 07-30 as not a break; it is Jilei's call to
    tick it.

**Posting on GitHub (each needs Jilei's OK)**
- the draft comments for #243 and #251–#255;
- the draft comment for #196, a thank-you that explains the merge;
- the draft comment for #233.

**Code we can do alone on the Mac**
- **#229, free rotation.** The cause is in `workstreams/free-rotation-sync.md`: the 3D mesh and the
  3D pick ignore the free-rotation ITK transform, which the 2D views and the volume renderer apply.
  **Jilei's decisions:**
  - loaded meshes turn with the image too;
  - exported meshes stay in the image's own space;
  - test the click-to-cursor maths at the model level, not through a GUI click.

  Use a new branch (e.g. `bug/free-rotation-3d-sync`) whose PR says "Fixes #229".
- W8 crash fixes: 26–30, 35, 15b. W8 test fixes for tests that pass without checking anything: 22,
  23, 31–34.
- `change_tracking.md` past `679ba76a`, and a draft of the 4.6 section of `ReleaseNotes.md`.
- Refresh the meeting pages, but ask first:
  - branches (https://claude.ai/artifact/QyivAN8NiDzadZ7hPKn6ut) still shows five branches;
  - outside PRs (https://claude.ai/artifact/KjsGnpqcBdf2P1G2RyGbCs) lacks #196, #233, #256 and
    #260.
- Follow-ups that others own: #212 is only partly fixed by #254; #196 left four tooltips with the
  old wording.

**Needs the Windows box**
- **Branch 11 `bug/windows-decimal-comma` (#256):** run `ctest -R NumericLocale` (it needs a
  decimal-comma locale such as `de-DE`), plus the full suite.
- **#257 (W8 44):** the fix is known (return the path unchanged when `GetLongPathNameA` fails), in
  the same file as #256. Put it on a new branch that says "Fixes #257", and verify both together.
- W8 43: GUI tests write into the real `%APPDATA%`.
- #255's Windows code path, if Paul wants #255.

**Needs the Linux box** (blocked by W8 42, Qt ≥ 6.9.3, unless the quick route is used)
- The ninth branch's Linux run: recipe below.
- A full Linux `ctest` of `staging/v460`. The last one was in July.

**W1 and other workstreams**
- W1: async DLS is blocked (Q4); the `Submodules/{c3d,greedy}` bump; deleting merged branches (W8
  item 7, plus `developer-doc`).
- W3: the itksnap-dls refactor. W4 and W5 depend on it. W7: cmesh.

**Release engineering** (SPRINT_PLAN §3)
- the version to beta, then `4.6.0`;
- `ReleaseNotes.md`;
- `change_tracking.md`;
- the wrapper's `SUBMODULE_SYNC.md` and `CLAUDE.md`.

## Linux run of the ninth branch (`bug/remote-cache-test-datadir`, #258)

What to show: without the branch, `_Cache` fails and writes into `~/.itksnap.org`. With it, the test
passes and `~/.itksnap.org` is left alone.

**The quick route**, test-only:
1. Make a throwaway detached worktree of `bug/linux-gcc-build`.
2. In `CMake/standalone.cmake`, lower the five `FIND_PACKAGE(Qt6… 6.9.3 REQUIRED)` calls to `6.4`.
   **Never commit this.**
3. Configure against `vtk-dev/installed/lib/cmake/vtk-9.5`, and build only
   `ninja remote_image_load_test`.
4. Back up `~/.itksnap.org`, and snapshot it with
   `find ~/.itksnap.org -exec stat -c '%Y %s %n' {} + | sort`.
5. Run the baseline, `ctest -R RemoteImageLoadTest_Cache -V`. Expect "CacheMetadata.xml not created",
   and new files in the real profile.
6. `git merge --no-edit bug/remote-cache-test-datadir`, rebuild, and run
   `ctest -R RemoteImageLoadTest -V`. Expect all three to pass, the log to say
   `Clearing cache at <build>/.itksnap_test/...`, and the snapshot to be unchanged.
7. Guard proof: comment out `RedirectApplicationDataDirectory();`. `_Cache` must then fail with "is
   outside the test directory".
8. Record the result in branches.md §9 and W8 3. Commenting on #258 needs Jilei's OK.

## Files to read first

1. `SPRINT_PLAN.md`:
   - the three rules at the top;
   - §2, the state of the tree (verified 2026-09-30);
   - §3, the workstreams and release engineering;
   - §6, the cut line.
2. `MERGE_ORDER.md`: Status, then Queue.
3. `branches.md`: the summary table, with one row per branch; §10 and §11 are new.
4. `upstream.md`: every GitHub item, the Milestone section, and the list of issues with no PR.
5. The reviews:
   - `reviews/outside-prs-2026-09.md`, `reviews/pr-196.md` and `reviews/pr-233.md`;
   - `workstreams/free-rotation-sync.md` for #229.
6. `workstreams/bugfixes.md` (W8), with new items 45–47.
7. `PROGRESS_LOG.md`, the entries dated 2026-09-29 and 2026-09-30.

## Known traps

**Release and GitHub**
- **Never merge a PR, ours or an outside one**, through `gh`, the API or the web UI. Merges happen
  only at the planning meeting. Every issue, comment, milestone change, or push to someone else's
  branch needs Jilei's OK first. (#196's push and the milestone changes were OK'd on 2026-09-30.)
- **This session cannot force-push.** The auto-mode permission guard blocks
  `git push --force-with-lease` ("Git Destructive"), even after Jilei approves in chat. Build and test
  locally, then give Jilei the exact command. Plain pushes work.
- **To update an outside PR without a force-push**, merge master into its branch. Pushing to the
  fork's branch works when "maintainers can modify" is on. #196 was done this way.
- **A green CI run does not mean the tests passed** (#259). Every PR is red, whatever the change.

**Testing**
- **Compare failure *sets*, never totals.** The remote-image tests rotate their failures (W8 3b, the
  p25/p50 quantile), and `4DReplayWithMeshUpdate` is flaky upstream (W8 2).
- **A GUI test that passes in under a second is not running.** Reference times:
  - `RandomForestBailOut` ≈ 20 s;
  - `4DContinuousRendering` ≈ 38 s;
  - `LanguagePreference` ≈ 7 s;
  - `MeshWorkspace` ≈ 47 s.
- **A branch off `upstream/master` lacks the false-green fix.** Register a new script in BOTH
  `TestingScripts.qrc` and `GUI_TESTS`, and break one assertion to see it fail.
- **The GUI harness cannot click in the 3D view.** `view3d` is a container, and its OpenGL child,
  which gets the mouse, has no name. The **Space key paints with `dragging = true`, which never runs
  the adaptive brush**: use `postMouseEvent(canvas, x, y, "click", "left")`.
- The harness reads values at the *cursor*, but a click paints under the *mouse*. The Undo action's
  enabled state does not update in the harness.
- **On macOS, `HOME` does not move ITK-SNAP's settings folder.** Also set `CFFIXED_USER_HOME` to a
  scratch folder. A hand-made `UserPreferences.xml` needs `System.CreatedBySNAPVersion`, or it is
  wiped at load.
- **Warn Jilei before any deliberate crash.** Each abort pops a macOS crash dialog.
- **Several branches edit `CMakeLists.txt` and `TestingScripts.qrc`.** Insert at an anchor no other
  branch or open PR uses, and check with `git merge-tree --write-tree` against all branches and
  `refs/pr/*`.

**Machine (Mac)**
- **Memory is tight.** Swap was 9.4 of 10 GB, with the load average at 60–135. Build with
  `ninja -j4`. To test a branch commit quickly, check it out detached in `worktrees/pr-review`: its
  build, `build-pr-review`, is complete, so only the changed files rebuild.
- **The Bash tool stops at 10 minutes.** Run `ctest` in the background.
- zsh does not word-split `$var`, and a bare `====` is expanded. Never `pkill -f` from your own shell.
- **Scripted doc edits that replace a span `s[i:j]` twice dropped paragraphs this session.** Always
  read `git diff` of a scripted edit.

## Left on disk

- **Worktrees** (under `worktrees/`):
  - `cardiac-io`;
  - `ui-language-setting`;
  - `windows-decimal-comma`;
  - `pr-review` (detached at `52ee94fa`; a clean scratch for review builds);
  - the four older ones.
- **Builds:** `build-cardiac-io`, `build-ui-language-setting` and `build-pr-review`.
  `build-windows-decimal-comma` is only partly built.
- **Refs:** local `refs/pr/*`, and local tags `archive/staging-v460-{0924,0929,0930}`.

Run `/handoff` at the end.
