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

## Issues

| Issue | Title | State | Tracks | Body | Next |
|---|---|---|---|---|---|
| [#257](https://github.com/pyushkevich/itksnap/issues/257) | Windows: ITK-SNAP closes silently when a file given on the command line does not exist | open, filed 2026-09-28 | W8 44 | [reviews/issue-windows-missing-file.md](reviews/issue-windows-missing-file.md) | Fix it on a new topic branch off `upstream/master`, with a PR that says "Fixes #257". Verify on the Windows box. |
| [#258](https://github.com/pyushkevich/itksnap/issues/258) | Tests: RemoteImageLoadTest_Cache fails on Windows and Linux, and the remote-image tests write into the real ITK-SNAP settings folder | open, filed 2026-09-28 | W8 3 | [reviews/issue-remote-cache-test.md](reviews/issue-remote-cache-test.md) | Fixed by `bug/remote-cache-test-datadir` (branches.md §9); its PR says "Fixes #258". Linux run still to do. |
| [#259](https://github.com/pyushkevich/itksnap/issues/259) | CI: pull request builds always fail, and failing tests never fail a run | open, filed 2026-09-29 | upstream only | [reviews/issue-ci-fork-prs.md](reviews/issue-ci-fork-prs.md) | Paul's call, especially item 4 (gating on tests). Open question: why the second `git fetch` passes on `master`, and why `ctest` exits 0 on macOS after a failed Update. |

## Pull requests

| PR | Title | Author | State | Local | Next |
|---|---|---|---|---|---|
| [#241](https://github.com/pyushkevich/itksnap/pull/241) | Support non-ASCII characters in Windows user names | marcoduering (outside) | open, milestone v4.6.0, mergeable. Jilei's 4 commits pushed 2026-09-27; head `b287abe6`. Our comment posted 2026-09-28; Marco agreed the same day | review: [reviews/pr-241.md](reviews/pr-241.md); comment: [reviews/pr-241-comment.md](reviews/pr-241-comment.md) (draft; posted text edited) | Merge at the planning meeting (action 4), retitling and rewriting the description as Marco invited; then action 5. |
| [#244](https://github.com/pyushkevich/itksnap/pull/244) | DOC: Add contributing, governance, code of conduct, and developer guide | jilei-hao | merged | W2 | — |

Our nine topic branches ([branches.md](branches.md)) have **no PRs yet**: Paul's go-ahead comes
first (NEXT_SESSION_PROMPT, "Talk to Paul before opening PRs"). When one is opened, give it a row here.
