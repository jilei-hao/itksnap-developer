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

## Pending actions

Actions 1–3 are done; 4–5 wait for the planning meeting.

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
4. **Merge #241 at the planning meeting, in person.** Every PR merge happens there, and never through
   `gh` or a script. Bring [reviews/pr-241.md](reviews/pr-241.md) §7 as the evidence, since CI is red
   for the reasons in action 2.
5. **After the merge:**
   - rebase `test/seg-anchor-4d` onto the new `upstream/master` (it conflicts in `CMakeLists.txt`)
     and update [MERGE_ORDER.md](MERGE_ORDER.md) (rule 3);
   - add #241 to [change_tracking.md](change_tracking.md);
   - mark the rows below.

## Milestone

**v4.6.0** (GitHub milestone #1) holds everything on the meeting agenda. Jilei asked for this on
2026-09-30, and I set it the same day:
- PRs #241, #196, #182 (already on it), plus #243 and #251–#255;
- our issues #257–#260;
- the issues those PRs fix: #69, #216, #185, #154, #212, #210.

Added later the same day, at Jilei's request: #256 (Windows decimal comma), #229 (W6 free rotation),
#233 (Paul's adaptive-brush PR) and #222, the issue #233 fixes. That makes 23 open items. The Reorient
bug (W8 45) has no issue yet.

**Issues on the milestone with no PR** (checked with GitHub's closing links, 2026-09-30):
- no fix anywhere yet: #229, #257 (Windows only), #259 (CI; Paul's);
- fixed on our branches, no PR yet: #258 (`bug/remote-cache-test-datadir`), #260
  (`feature/ui-language-setting`), #256 (`bug/windows-decimal-comma`);
- only partly addressed: #212 (#254 stops the crash; the drop still does nothing), and #210 (#255 needs
  Paul's decision; #260 is the alternative).

## Issues

| Issue | Title | State | Tracks | Body | Next |
|---|---|---|---|---|---|
| [#256](https://github.com/pyushkevich/itksnap/issues/256) | NRRD fails to load on Windows with decimal-comma locale | open, filed 2026-09-25 by GoCompute-Philipp-Huber (outside), assigned to Jilei, milestone v4.6.0 | W8 47 | the issue itself (root cause + one-line fix, tested on Windows 11) | Fixed on `bug/windows-decimal-comma` (branches.md §11), which credits the reporter; its PR says "Fixes #256". The Windows run is still to do |
| [#257](https://github.com/pyushkevich/itksnap/issues/257) | Windows: ITK-SNAP closes silently when a file given on the command line does not exist | open, filed 2026-09-28 | W8 44 | [reviews/issue-windows-missing-file.md](reviews/issue-windows-missing-file.md) | Fix it on a new topic branch off `upstream/master`, with a PR that says "Fixes #257". Verify on the Windows box. |
| [#258](https://github.com/pyushkevich/itksnap/issues/258) | Tests: RemoteImageLoadTest_Cache fails on Windows and Linux, and the remote-image tests write into the real ITK-SNAP settings folder | open, filed 2026-09-28 | W8 3 | [reviews/issue-remote-cache-test.md](reviews/issue-remote-cache-test.md) | Fixed by `bug/remote-cache-test-datadir` (branches.md §9); its PR says "Fixes #258". Linux run still to do. |
| [#259](https://github.com/pyushkevich/itksnap/issues/259) | CI: pull request builds always fail, and failing tests never fail a run | open, filed 2026-09-29 | upstream only | [reviews/issue-ci-fork-prs.md](reviews/issue-ci-fork-prs.md) | Paul's call, especially item 4 (gating on tests). Open question: why the second `git fetch` passes on `master`, and why `ctest` exits 0 on macOS after a failed Update. |
| [#260](https://github.com/pyushkevich/itksnap/issues/260) | Preferences: let users choose the user-interface language | open, filed 2026-09-30, assigned to Jilei | new, from the #255 review | [reviews/issue-ui-language-setting.md](reviews/issue-ui-language-setting.md) | Branch `feature/ui-language-setting` (branches.md §10). Its PR says "Fixes #260". Open question for Paul: should the setting change number formats too, as `--lang` does? |

## Pull requests

| PR | Title | Author | State | Local | Next |
|---|---|---|---|---|---|
| [#241](https://github.com/pyushkevich/itksnap/pull/241) | Support non-ASCII characters in Windows user names | marcoduering (outside) | open, milestone v4.6.0, mergeable. Jilei's 4 commits pushed 2026-09-27; head `b287abe6`. Our comment posted 2026-09-28; Marco agreed the same day | review: [reviews/pr-241.md](reviews/pr-241.md); comment: [reviews/pr-241-comment.md](reviews/pr-241-comment.md) (draft; posted text edited) | Merge at the planning meeting (action 4), retitling and rewriting the description as Marco invited; then action 5. |
| [#244](https://github.com/pyushkevich/itksnap/pull/244) | DOC: Add contributing, governance, code of conduct, and developer guide | jilei-hao | merged | W2 | — |
| [#196](https://github.com/pyushkevich/itksnap/pull/196) | zh_CN translation update | liyue3780 + Feiz Escher (outside) | open, milestone v4.6.0. **Now mergeable: +33/−33, 1 file** (2026-09-30) | [reviews/pr-196.md](reviews/pr-196.md) | Jilei chose to push the 33-line version to the PR. Pushed `b934b6aa` to `liyue3780/itksnap:master`, a merge of master that keeps the contributors' commits (no force-push). Next: a thank-you comment (draft in the review, needs Jilei's OK), then merge at the planning meeting |
| [#233](https://github.com/pyushkevich/itksnap/pull/233) | Fix adaptive brush crash: catch std::exception (fixes #222) | pyushkevich | open since 2026-05-13, milestone v4.6.0, merges cleanly | [reviews/pr-233.md](reviews/pr-233.md) | **Merge**, ideally with two follow-ups: compare the grid, not just the size; show a message, not a silent no-op. **Measured:** master crashes on an adaptive-brush click when the segmentation has its own grid (seg_anchor); #233 prevents it. A GUI test repro is in `reviews/pr-233-scripts/`. Draft comment needs Jilei's OK |
| [#243](https://github.com/pyushkevich/itksnap/pull/243) | Fix invalid orientation codes for oblique images (#69) | duchenhe (outside) | open, assigned to Jilei 2026-09-25; no CI run | [reviews/outside-prs-2026-09.md](reviews/outside-prs-2026-09.md) | Merge after one small change: keep the old code whenever it is valid (144 of 576 exact-45° matrices change). Draft comment ready; posting needs Jilei's OK |
| [#251](https://github.com/pyushkevich/itksnap/pull/251) | BUG: Fix RLEImage::CleanUp() (#216) | aycibatuhan (outside) | open, assigned to Jilei; no CI run | same | Merge. Draft comment ready |
| [#252](https://github.com/pyushkevich/itksnap/pull/252) | BUG: Show orientation of the selected layer (#185) | aycibatuhan (outside) | open, assigned to Jilei; no CI run | same | Merge. Found the upstream Reorient bug (W8 45) on the way |
| [#253](https://github.com/pyushkevich/itksnap/pull/253) | BUG: Recognize label files with CRLF or no header (#154) | aycibatuhan (outside) | open, assigned to Jilei; no CI run | same | Merge (two optional tidy-ups) |
| [#254](https://github.com/pyushkevich/itksnap/pull/254) | BUG: Do not crash when a drop carries no URLs (#212) | aycibatuhan (outside) | open, assigned to Jilei; no CI run | same | Merge after "Fixes #212" becomes "Refs #212" |
| [#255](https://github.com/pyushkevich/itksnap/pull/255) | BUG: Choose the UI language from preferred languages (#210) | aycibatuhan (outside) | open, assigned to Jilei; no CI run | same | **Paul's decision** (he disagreed in #210). macOS already correct on Qt 6.9.3; Windows/Linux paths never built |

**Also on GitHub:** #182 (MSVC build speed, +1 line, approved by dzenanz) is on the v4.6.0 milestone since
2026-09-25 and not reviewed here. Issue #256 (a Windows
decimal comma breaks NRRD loading) has a proposed fix in `main.cxx`, the same file as #257's fix.

Our nine topic branches ([branches.md](branches.md)) have **no PRs yet**: Paul's go-ahead comes
first (NEXT_SESSION_PROMPT, "Talk to Paul before opening PRs"). When one is opened, give it a row here.
