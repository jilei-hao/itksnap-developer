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

Do these in order. Actions 1–2 come first so that action 3 can cite their numbers.

1. **Create the Windows missing-file issue**, then put its number in the Issues table below and in
   W8 44.
   ```bash
   gh issue create -R pyushkevich/itksnap \
     --title "Windows: ITK-SNAP closes silently when a file given on the command line does not exist" \
     --body-file projects/release-460/reviews/issue-windows-missing-file.md
   ```
2. **Create the CI issue.** Optionally check first, in the Actions log of a fork PR (#241 or #244),
   that `ExperimentalUpdate` fails in `git fetch`. If it does, delete "and this still needs confirming
   from a log" from section 1 of the draft.
   ```bash
   gh issue create -R pyushkevich/itksnap \
     --title "CI: pull requests from forks always fail, and failing tests never fail a run" \
     --body-file projects/release-460/reviews/issue-ci-fork-prs.md
   ```
3. **Comment on #241.** Optionally add the two new issue numbers to the last paragraph of the
   comment first, after "we'll look at them separately" and "we'll fix it on our side".
   ```bash
   gh pr comment 241 -R pyushkevich/itksnap --body-file projects/release-460/reviews/pr-241-comment.md
   ```
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
| _not yet created_ | Windows: ITK-SNAP closes silently when a file given on the command line does not exist | draft, 2026-09-28 | W8 44 | [reviews/issue-windows-missing-file.md](reviews/issue-windows-missing-file.md) | Action 1. Then fix it on a new topic branch off `upstream/master`, with a PR that says "Fixes #N". |
| _not yet created_ | CI: pull requests from forks always fail, and failing tests never fail a run | draft, 2026-09-28 | upstream only | [reviews/issue-ci-fork-prs.md](reviews/issue-ci-fork-prs.md) | Action 2. Its item 4 (gating on tests) is Paul's decision. |

## Pull requests

| PR | Title | Author | State | Local | Next |
|---|---|---|---|---|---|
| [#241](https://github.com/pyushkevich/itksnap/pull/241) | Support non-ASCII characters in Windows user names | marcoduering (outside) | open, milestone v4.6.0. Jilei's 4 commits pushed 2026-09-27; head `b287abe6` | review: [reviews/pr-241.md](reviews/pr-241.md); comment: [reviews/pr-241-comment.md](reviews/pr-241-comment.md) | Action 3 (comment). Merge at the planning meeting (action 4), then action 5. |
| [#244](https://github.com/pyushkevich/itksnap/pull/244) | DOC: Add contributing, governance, code of conduct, and developer guide | jilei-hao | merged | W2 | — |

Our eight topic branches ([branches.md](branches.md)) have **no PRs yet**: Paul's go-ahead comes
first (NEXT_SESSION_PROMPT, "Talk to Paul before opening PRs"). When one is opened, give it a row here.
