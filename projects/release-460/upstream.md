# Upstream — GitHub issues and pull requests

Everything on https://github.com/pyushkevich/itksnap that this sprint opened, is handling or is
waiting on, one row per item. Local work lives elsewhere, and each row links to it:

| Where | What it holds |
|---|---|
| [branches.md](branches.md) | our topic branches. When one becomes a PR, its number goes there as well as here. |
| [workstreams/bugfixes.md](workstreams/bugfixes.md) | W8 bugs. The issue number goes in the W8 row. |
| [reviews/](reviews/) | our reviews of outside PRs, plus drafts of issue and comment bodies |

**Rules:**
- When an item changes on GitHub (created, commented, merged, closed), update its row here in the same
  session, together with the linked W8 or `branches.md` row.
- **PRs are merged only at the planning meeting, in person.** A session never merges one, whether
  through `gh`, the API or the web UI, and never lists a merge as a command to run.

Creating issues and posting comments needs `gh` logged in. **Jilei runs these on the main
workstation**, since the Windows box has no `gh`. Run the commands from the wrapper root after
`git pull`.

## Our work not yet upstream — 2026-10-28

Upstream is `5ad5a025` (tagged `v4.6.0-beta1`): 4.6.0-beta.1 plus #301 and #302. The v4.6.0 milestone
has **0 open items** and 82 closed; it is due **2026-11-20**. Paul merged #302 on 2026-10-28, after
retargeting it to `master`.

**1. The 4.6 review queue: four itksnap branches, no PRs yet** (six until 2026-10-28, when two were combined; five until 2026-11-02, when free rotation joined them). They are rebased onto `a4f01e8d`
locally (the combined bug-fix branch onto `5ad5a025`, and pushed), but the other three are **not pushed** (`origin` has the `52ee94fa`-based tips) and **not built or tested** on beta.1.
Merge order and the force-push command: [MERGE_ORDER.md](MERGE_ORDER.md).

| Branch | Commits | What | Open point |
|---|---:|---|---|
| `bug/linux-gcc-build` | 1 | VTK floor 9.3.1 → 9.5.2 | Paul's call; CI already builds against 9.5.2 everywhere |
| `bug/rf-crashes-and-full-extent` | 6 | one bug-fix PR: free rotation (Fixes #229, still open, milestone v4.6.2); the cursor-range off-by-one, with a test; guards for a null RF engine and for the Layer Inspector after a layer is closed | **pushed** 2026-11-02 (`a9b09a91`, on `5ad5a025`), full suite 82/82 on macOS; manual checks passed (Jilei, 2026-10-30 and 2026-11-02); PR text ready ([reviews/pr-bugfix-rf-full-extent.md](reviews/pr-bugfix-rf-full-extent.md)), PR not opened |
| `test/seg-anchor-4d` | 1 | four tests of seg_anchor with 4D segmentations | none |
| `feature/cardiac-io` | 13 | 4D CTA / echo: R-R% or frame-time axis, JSON sidecar, non-PHI export, phase/time field | the largest; merges cleanly with #301 |

**2. Parked:** `test/harness-gui-thread` (1 commit, old base). Upstream `5071a54f` and `d74b3a77` cover
part of it; ask Paul before rebasing.

**3. Outside the 4.6 queue:**
- itksnap `test/dls_sam2`: async DLS paintbrush and nnInteractive progress bar (`cb6f692e`,
  `ea86df0d`). In scope, but blocked on W1 Q4. Its base is from March, and it conflicts with master in 5
  files after Paul's DLS rework (D1–D9), so it needs redoing, not a rebase.
- itksnap `sprint/caimi`: 6 agentic-API commits (out of scope; `projects/agentic-api/`). The other 13 are
  old copies of `feature/cardiac-io` and the Linux fixes.
- itksnap-dls (fork `main` is fully in `pyushkevich/itksnap-dls` `dda3b044`):
  - `features/segflow4d`: 4 commits, segflow4d integration (W3);
  - `test/dls_sam2`: 3 commits;
  - `feature/agentic-api`: 6 commits (out of scope);
  - `claude/create-developer-guide-xaMCx`: 1 commit, probably superseded by `developer-doc`, which is
    merged.

**4. GitHub, each needs Jilei's OK:**
- Close #20 as a duplicate of #69 (closed by #243).
- A small pre-existing bug: `Common/ExtendedGDCMSerieHelper.cxx:60` throws a bare number instead of
  the `IRISException`.

**5. Cleanup, nothing to merge:**
- Retired branches: `test/harness-false-green`, `bug/windows-decimal-comma`, `bug/seg3d-into-4d-check`,
  `bug/remote-cache-test-datadir`, `feature/ui-language-setting`.
- Fork branches already fully upstream: `bug/4d-mesh-slice`, `bug/large-image-oom`, `bug/memory-leak`,
  `bug/mesh-update-crash`, `developer-doc`, `feature/io-improvement`, `feature/seq-nrrd-export`,
  `feature/vti-io` (W8 item 7).
- Local scratch branches: `pr-merge/{243,252,255}`, `pr-test/{301,302}`.
- The wrapper's sprint docs have been uncommitted since 2026-09-30.

## Pending actions

Actions 1–4 are done; 5 is partly done.

1. ✅ **Done 2026-09-28:** the Windows missing-file issue is [#257](https://github.com/pyushkevich/itksnap/issues/257).
2. ✅ **Done 2026-09-29:** the CI issue is [#259](https://github.com/pyushkevich/itksnap/issues/259). Before
   filing, the draft was corrected against the Actions logs:
   - **every** PR fails, not only fork PRs (#247, from `seg_anchor`, fails the same way), so the title
     changed;
   - the `git fetch` failure comes from a greedy submodule pin (`a88a4f3e`, set by `7ee09def`) that
     no longer exists in pyushkevich/greedy;
   - on macOS the same fetch fails, but `ctest` exits 0 there, so the build still runs;
   - the green `master` build had 3 failing tests, and the `Remote` test label offers a way to gate
     without the flaky tests (`-LE Remote`).
3. ✅ **Done 2026-09-28** (03:49 UTC, as `jilei-hao`, before actions 1–2, so it cites no issue
   numbers). The posted text is an edited version of
   [reviews/pr-241-comment.md](reviews/pr-241-comment.md); GitHub holds the final wording. Marco
   replied the same day: he agrees the guard removal is the real fix and the manifest's value is UTF-8
   `argv`, and invites us to **update the PR title and description when merging** (action 4).
4. ✅ **Done 2026-10-21:** Paul merged #241 himself (`5acdbade`).
5. **After the merge:**
   - ✅ `test/seg-anchor-4d` rebased onto `8868dc2e` (2026-10-21; one `CMakeLists.txt` hunk);
   - add #241 to [change_tracking.md](change_tracking.md);
   - ✅ rows below marked.
6. **New, 2026-10-21 (each needs Jilei's OK):** close #258 and #259, close #20 as a duplicate of
   #69, and push the three `pr-merge/*` branches to #243, #252 and #255. Drafts and commands are in
   [reviews/milestone-triage-2026-10-21.md](reviews/milestone-triage-2026-10-21.md). `gh` on this
   Mac needs `gh auth refresh -h github.com` first: its token is invalid.

## Milestone

**2026-10-21:** the milestone has grown to **74 items, 14 open** (Paul added his own #261–#296).
The open list, what can be closed, and the duplicates are in
[reviews/milestone-triage-2026-10-21.md](reviews/milestone-triage-2026-10-21.md). The rest of this
section is the 2026-09-30 state.

**v4.6.0** (GitHub milestone #1) holds everything on the meeting agenda. Jilei asked for this on
2026-09-30, and I set it the same day:
- PRs #241, #196, #182 (already on it), plus #243 and #251–#255;
- our issues #257–#260;
- the issues those PRs fix: #69, #216, #185, #154, #212, #210.

Added later the same day, at Jilei's request: #256 (Windows decimal comma), #229 (W6 free rotation),
#233 (Paul's adaptive-brush PR) and #222, the issue #233 fixes. That makes 23 open items. The Reorient
bug (W8 45) has no issue yet.

**Issues on the milestone with no PR** (checked with GitHub's closing links, 2026-09-30):
- no fix anywhere yet: #257 (Windows only), #259 (CI; Paul's);
- fixed on our branches, no PR yet: #258 (`bug/remote-cache-test-datadir`), #260
  (`feature/ui-language-setting`), #256 (`bug/windows-decimal-comma`), #229
  (`bug/free-rotation-3d-sync`, 2026-09-30; not yet checked by eye in the app);
- only partly addressed: #212 (#254 stops the crash; the drop still does nothing), and #210 (#255 needs
  Paul's decision; #260 is the alternative).

## Issues

| Issue | Title | State | Tracks | Body | Next |
|---|---|---|---|---|---|
| [#256](https://github.com/pyushkevich/itksnap/issues/256) | NRRD fails to load on Windows with decimal-comma locale | **closed 2026-10-15**, fixed by Paul's #290 (`1df55964`: `LC_NUMERIC` "C") | W8 47 | the issue itself (root cause + one-line fix, tested on Windows 11) | Done. Our `bug/windows-decimal-comma` is retired (MERGE_ORDER "Retired") |
| [#257](https://github.com/pyushkevich/itksnap/issues/257) | Windows: ITK-SNAP closes silently when a file given on the command line does not exist | **closed 2026-10-15**, fixed by Paul's #290 (`DecodeFilename` returns the path when `GetLongPathNameA` fails, as we proposed) | W8 44 | [reviews/issue-windows-missing-file.md](reviews/issue-windows-missing-file.md) | Done |
| [#258](https://github.com/pyushkevich/itksnap/issues/258) | Tests: RemoteImageLoadTest_Cache fails on Windows and Linux, and the remote-image tests write into the real ITK-SNAP settings folder | **closed 2026-10-28** by Paul, after #305 (`7b96436b`) gave every remote image test its own data directory | W8 3 | [reviews/issue-remote-cache-test.md](reviews/issue-remote-cache-test.md) | Done |
| [#259](https://github.com/pyushkevich/itksnap/issues/259) | CI: pull request builds always fail, and failing tests never fail a run | **closed 2026-10-28** by Paul: `51a71530` (#303) now fails the CI job when a test fails, so part 2 was done too | upstream only | [reviews/issue-ci-fork-prs.md](reviews/issue-ci-fork-prs.md) | Done |
| [#260](https://github.com/pyushkevich/itksnap/issues/260) | Preferences: let users choose the user-interface language | **closed 2026-10-28** by Paul, done by his #300 (`4006ed6a`, `f0a4d80e`) | new, from the #255 review | [reviews/issue-ui-language-setting.md](reviews/issue-ui-language-setting.md) | Done. Our `feature/ui-language-setting` is retired (same design, same settings key) |

## Upstream since `52ee94fa`

Paul merged four PRs on 2026-10-01/02; `upstream/master` is now **`651e82c0`**:
- **#261** (seg_anchor fixes and more): full-extent rewrite and caching, reference box and crosshairs
  no longer one voxel short, zoom to fit cycles between scene, main image and segmentation (new GUI
  test `ZoomToFitCycle`), `engine.screenshot()` for GUI test scripts, SSH ProxyJump and key
  passphrases, and a looser quantile tolerance in `RemoteImageLoadTest` (W8 3b).
- **#262, #263:** CI build fixes (Ubuntu libssh 0.9, `NOMINMAX` for every Windows generator).
- **#264:** the 3D view follows the reference space (W8 48, found by our #229 review).

- **#265** (seen 2026-10-05; `upstream/master` = **`41a1e0a6`**): creates the SourceForge folder before
  uploading packages (`CMakeLists.txt`, packaging section) and adds `itksnap-wt
  -dssp-services-available`. It touches nothing our branches change; all twelve and staging merge
  cleanly with it. The branches are still based on `651e82c0`.

- **2026-10-21: `upstream/master` = `8868dc2e`**, 169 commits past `41a1e0a6`. Paul's "4.6 cleanup"
  series #267–#290 (release blockers, segmentation as reference space, DLS, remote IO, translations
  fr/ja/pt_BR, tests for untested areas, autosave), CI rework #275–#293 (ARM builds, Rocky Linux 8,
  ITK 5.4.7, PR builds that build and test), version 4.6.0-alpha.5 with release notes (#289), and the
  merges of #241, #196, #253, #280, #284 and #114. It overlaps our branches heavily: five are
  retired or parked, two were trimmed (MERGE_ORDER.md "Retired 2026-10-21"). The seven left were
  rebased; four needed conflict work (`feature/cardiac-io`, `feature/ui-language-setting`,
  `test/seg-anchor-4d`, `bug/full-extent-off-by-one`).

- **2026-10-28: `upstream/master` = `d7581658`, version 4.6.0-beta.1** (#303). Merged since `8868dc2e`:
  #297 (Windows installer metadata, fixes #291), #182, #243, #298 (DLS server ≥ 0.1.6), #252, #300
  (Paul's Language preference and live preferences dialog), #255, #303 (CI fails on test failures),
  #304, #305 (#258). `feature/ui-language-setting` is retired; the other six were rebased (one
  `CMakeLists.txt` hunk in `test/seg-anchor-4d`). **Still open on the milestone: #301** (4D CTA per
  DICOM series, fixes #218), assigned to Jilei: Paul asked for a test on real 4D CTA data. #302
  (SliceThickness split, replaces #128) is stacked on #301 and not on the milestone. #128 was closed.

Effect on our work: all twelve topic branches were rebased onto `651e82c0` on 2026-10-02 (see
[MERGE_ORDER.md](MERGE_ORDER.md)). Four needed conflict work, and `bug/full-extent-off-by-one`
shrank to the two cases Paul's rewrite still gets wrong. No outside PR was merged. #252 now conflicts
with master.

## Pull requests

| PR | Title | Author | State | Local | Next |
|---|---|---|---|---|---|
| [#241](https://github.com/pyushkevich/itksnap/pull/241) | Support non-ASCII characters in Windows user names | marcoduering (outside) | **merged 2026-10-21** by Paul (`5acdbade`) | review: [reviews/pr-241.md](reviews/pr-241.md); comment: [reviews/pr-241-comment.md](reviews/pr-241-comment.md) (draft; posted text edited) | Done. Add it to change_tracking.md (action 5) |
| [#244](https://github.com/pyushkevich/itksnap/pull/244) | DOC: Add contributing, governance, code of conduct, and developer guide | jilei-hao | merged | W2 | — |
| [#196](https://github.com/pyushkevich/itksnap/pull/196) | zh_CN translation update | liyue3780 + Feiz Escher (outside) | **merged 2026-10-15** by Paul (`a6c488ea`) | [reviews/pr-196.md](reviews/pr-196.md) | Done. The thank-you comment was never posted |
| [#233](https://github.com/pyushkevich/itksnap/pull/233) | Fix adaptive brush crash: catch std::exception (fixes #222) | pyushkevich | **closed 2026-10-21**, not merged: superseded by `0e310d2a` (adaptive brush catches the watershed exception and checks the grid) and #296 (`std::exception` in the paintbrush event handlers) | [reviews/pr-233.md](reviews/pr-233.md) | Done; #222 closed with it. Our draft comment is obsolete |
| [#243](https://github.com/pyushkevich/itksnap/pull/243) | Fix invalid orientation codes for oblique images (#69) | duchenhe (outside) | **merged 2026-10-23** by Paul (`a2aa8f22`, after he merged master into it himself) | [reviews/outside-prs-2026-09.md](reviews/outside-prs-2026-09.md) | Done; #69 fixed. #20 (duplicate of #69) is still open |
| [#251](https://github.com/pyushkevich/itksnap/pull/251) | BUG: Fix RLEImage::CleanUp() (#216) | aycibatuhan (outside) | **closed 2026-10-21**, not merged: #216 was fixed independently by #290 (`1df55964`), same approach | same | Done |
| [#252](https://github.com/pyushkevich/itksnap/pull/252) | BUG: Show orientation of the selected layer (#185) | aycibatuhan (outside) | **merged 2026-10-27** by Paul (`33406511`), with an added per-layer orientation check in the DiffSpace test | same | Done; #185 fixed |
| [#253](https://github.com/pyushkevich/itksnap/pull/253) | BUG: Recognize label files with CRLF or no header (#154) | aycibatuhan (outside) | **merged 2026-10-21** by Paul (`b69c439e`, after he merged master into it) | same | Done |
| [#254](https://github.com/pyushkevich/itksnap/pull/254) | BUG: Do not crash when a drop carries no URLs (#212) | aycibatuhan (outside) | **closed 2026-10-21**, not merged: #212 fixed independently by #290 (`1df55964`), same fix | same | Done |
| [#255](https://github.com/pyushkevich/itksnap/pull/255) | BUG: Choose the UI language from preferred languages (#210) | aycibatuhan (outside) | **merged 2026-10-27** by Paul (`fb1ffb78`), alongside his own Language preference #300 | same | Done |

**Open or just merged, 2026-10-28:**

| PR | Title | Author | State | Next |
|---|---|---|---|---|
| [#301](https://github.com/pyushkevich/itksnap/pull/301) | Choose 4D CTA per DICOM series, not per directory (#218) | pyushkevich | **merged 2026-10-28** by Jilei (`a4f01e8d`), after the manual test on the AVRP exams | Done |
| [#302](https://github.com/pyushkevich/itksnap/pull/302) | Merge DICOM series split by SliceThickness formatting (replaces #128) | pyushkevich | **merged 2026-10-28** by Paul (`283464d3`), after he retargeted it to `master` | Done. Checked beforehand on master `a4f01e8d` + #302: the three DICOM tests pass, and Jilei's manual test looked good |
| [#306](https://github.com/pyushkevich/itksnap/pull/306) | one bug-fix PR from `bug/rf-crashes-and-full-extent`: free rotation (Fixes #229), the full-extent off-by-one, two crash guards | jilei-hao | **merged 2026-11-02** by Jilei (`a16d5c3e`) | Done; retire the branch from MERGE_ORDER |
| [#307](https://github.com/pyushkevich/itksnap/pull/307) | Fix the first 4D CTA time point loading upside down (#128) | jilei-hao | **merged 2026-11-05** (`ba96656b`); opened 2026-11-04 from `bug/4dcta-slice-order` (`b1da5935`) | Done. The reply on #128 (draft in the 2026-11-04 session) is still not posted |
| [#308](https://github.com/pyushkevich/itksnap/pull/308) | Version 4.6.0-beta.2; update the 4.6 release notes | jilei-hao | **merged 2026-11-05** (`1db8f623`); beta.2 packages built and uploaded to SourceForge by Jilei's manual Build run on 2026-11-06 | Done, except the tag: upstream has no `v4.6.0-beta2` (checked 2026-11-17) |
| [#310](https://github.com/pyushkevich/itksnap/pull/310) | Fix three problems loading very large images (#146) | jilei-hao | **opened 2026-11-17** from `bug/large-image-loading` (`a725b797`): Linux free memory read as 0 (every image over 4 GB refused), 32-bit 4D time-point offsets, macOS memory check; Harry Carey (@PolarBean) credited as co-author of the Linux commit; macOS suite 81/82 (`SegmentationAutosave` once, then 3/3) | CI; Paul's OK for 4.6.0 (after beta.2); not on the v4.6.0 milestone. Reply on #146 posted 2026-11-17 ([comment](https://github.com/pyushkevich/itksnap/issues/146#issuecomment-6961660531)), pointing to #310 and crediting @PolarBean; #146 stays open until #310 merges. **CI 6/6 pass** (2026-11-17). Testing-only candidate `rc/4.6.0` (`d092583f`) on the fork = master `8fdc1b37` + this PR, for Jilei's Linux round 2026-11-18; the wrapper's `itksnap` pointer is on it |
| [#312](https://github.com/pyushkevich/itksnap/pull/312) | Fix crash saving a remote workspace from the unsaved changes prompt (Fixes #311) | pyushkevich | **merged 2026-11-18** by Paul (`8fdc1b37`), before our run finished. One commit `7f322b3a` on `1db8f623`, no file shared with #310. Verified here 2026-11-18 in `worktrees/pr-312` / `build-pr-312`: 821/821 built, 0 errors; full suite **83/83**; `RemoteWorkspaceUnsaved` passes (suggests the local name `MRIcrop-with-mesh.itksnap`); with the null-parent fix undone it SIGSEGVs in `SimpleFileDialogWithHistory` from `SaveWorkspace`, the #311 stack, then passes again with the fix restored. Code: all five `parent->testAttribute` sites guarded, no other null-parent `SaveWorkspace` caller. **CI found two problems that are not in the code.** (1) Both macOS jobs pass 83/83, then fail at *Setup codesign keychain*: `notarytool` gets HTTP 403, "A required agreement is missing or has expired". This hits every push to master (also `8fdc1b37`) and blocks signed/notarized macOS 4.6.0 packages until the Apple Developer account holder accepts the agreement. Beta.2 (2026-11-06) still notarized, so it expired since. (2) windows-11-arm on `8fdc1b37`: tests and submit pass, Gatekeeper fails because the dashboard git update hit `upload-pack: not our ref a88a4f3e` in `greedy` (a submodule commit GitHub no longer has); windows-2022 passed the same step | Paul to accept the Apple agreement (developer.apple.com) before packaging 4.6.0; decide whether the windows-11-arm fetch error needs a fix or a rerun. `worktrees/pr-312` + `build-pr-312` can be removed |

**Also on GitHub:** #182 (MSVC build speed, +1 line, approved by dzenanz) is on the v4.6.0 milestone since
2026-09-25 and not reviewed here. Issue #256 (a Windows
decimal comma breaks NRRD loading) has a proposed fix in `main.cxx`, the same file as #257's fix.

Our six topic branches ([branches.md](branches.md)) have **no PRs yet**: Paul's go-ahead comes
first (NEXT_SESSION_PROMPT, "Talk to Paul before opening PRs"). When one is opened, give it a row here.
