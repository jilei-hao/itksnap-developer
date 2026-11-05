# Merge order — itksnap topic branches

The order in which the topic branches should be merged into `pyushkevich/itksnap:master`, the
constraints that force it, and the live state of every branch. Per-branch content and evidence are
in [branches.md](branches.md); the branch model is in [SPRINT_PLAN.md](SPRINT_PLAN.md) §2.

> **Update this file every time a topic branch changes.** That means a new branch, a new commit, a
> rebase, a branch merged upstream, or a deleted branch. **Status** (below) rewrites itself through a
> git hook on `itksnap`. **Queue** and **Constraints** are maintained by hand, and Status flags
> ⚠️ when they have gone stale. See [How to update](#how-to-update).

---

## Queue

The recommended merge order, top to bottom. `verified-at` is the tip at which the branch last passed
the checks in [How to update](#how-to-update). Status flags a branch whose tip has moved since.
The script reads this block: keep one branch per line, as `branch  verified-at  why`.

<!-- QUEUE:BEGIN -->
```text
# branch                    verified-at  why this position
bug/linux-gcc-build         -            one line: the VTK floor to 9.5.2 (Q2); the GCC fixes went obsolete with upstream's Qt 6.9.3 floor
bug/rf-crashes-and-full-extent  a9b09a91  one bug-fix PR (Jilei, 2026-10-28, 2026-11-02): free rotation (Fixes #229), the full-extent fix with its test, and the two RF/Layer Inspector crash guards; replaces bug/rf-layer-crashes, bug/full-extent-off-by-one and bug/free-rotation-3d-sync
bug/4dcta-slice-order       b1da5935     PR #307; reported on #128 against 4.6.0-beta1 (2026-11-03): the first 4D CTA time point loads upside down; one function and its test, on the current upstream/master
release/4.6.0-beta.2        -            PR #308; version bump + release notes for #306 and the 4D CTA fix (Jilei, 2026-11-04); its own PR like upstream's #303; not seen by the git hook (release/ prefix), so refresh Status by hand
test/seg-anchor-4d          -            tests only (seg_anchor with 4D data)
feature/cardiac-io          -            largest; its echo read guards were dropped for upstream's d61b7418
```
<!-- QUEUE:END -->

Only the constraints below are hard. The rest of the order is a recommendation: least
controversial first, then the branches that still need work or a conversation.

## Constraints

**Ordering.** The script checks that the queue respects every row. Keep the first two cells as
backticked branch names.

| Before | After | Why | Evidence | Verified |
|---|---|---|---|---|
| `bug/4dcta-slice-order` | `release/4.6.0-beta.2` | the beta.2 release notes describe the 4D CTA fix (#308 says "merge #307 first") | the notes' DICOM bullet "Fixed one time point of a 4D CTA series loading upside down"; no shared files, so it is order of meaning, not a merge conflict | 2026-11-04 |

Until 2026-11-04 there were no rows since 2026-10-21. The one row then (`bug/rf-layer-crashes` before
`test/harness-false-green`) went with the retired branch, and `bug/rf-layer-crashes` is no longer
indivisible: upstream registered `RandomForestBailOut` itself (`8f210627`).

## Retired 2026-10-21 (and 2026-10-28)

Upstream `8868dc2e` already does what these branches did, so they were **not rebased** and are out of
the queue. Their branches are left as they are, locally and on `origin`; delete them only with
Jilei's OK. The local tips are also tagged `archive/1002/<branch>`.

| Branch | Done upstream by | What upstream lacks |
|---|---|---|
| `test/harness-false-green` | `8f210627` (a missing script fails with NO_SUCH_TEST; `4DContinuousRendering` renamed) | nothing |
| `bug/windows-decimal-comma` | `1df55964` (#290: `LC_NUMERIC` "C" in `main()`) | our `NumericLocaleTest` |
| `bug/seg3d-into-4d-check` | `70271096` (B12: a single time point is checked against the selected segmentation) | nothing; its `TestSegmentationLoadChecks` covers the case |
| `bug/remote-cache-test-datadir` | `60bc0f60` + #272 (the test asks for the data directory; CMake isolates `_Cache` and `_URLKeys`) | the other five remote tests still use the real cache; the "outside .itksnap_test" guard |
| `feature/ui-language-setting` | **2026-10-28:** Paul's #300 (`4006ed6a`, `f0a4d80e`): the same Language preference, under the same key `UserInterface.DefaultBehavior.UILanguage`, read before the translators; #260 closed | nothing |
| `bug/rf-layer-crashes`, `bug/full-extent-off-by-one` | **2026-10-28, combined** into `bug/rf-crashes-and-full-extent` for one PR (Jilei's call). Same code, commit messages rewritten for upstream | nothing; follow the combined branch |
| `bug/free-rotation-3d-sync` | **2026-11-02, added** to `bug/rf-crashes-and-full-extent` for the same PR (Jilei's call). Same patches per `git range-diff` | nothing; follow the combined branch |
| `test/harness-gui-thread` | partly: `5071a54f` (lookups and item models on the GUI thread), `d74b3a77` (null objects fail the test) | the proxy that keeps raw widgets out of scripts. **Parked, not rebased**: ask Paul whether he wants it before spending a rebase on 600 lines of `SNAPTestQt.cxx` |

Trimmed on rebase: `bug/rf-layer-crashes` lost `5857616c` (qrc registration; upstream `8f210627`) and
`ba85b6a3` (synchronous layer invalidation; upstream `93b49626`). `bug/linux-gcc-build` lost
`b139c9bf` (GCC/Qt 6.4 portability; upstream requires Qt ≥ 6.9.3, and its CI builds Linux with GCC 13).

---

## Pending force-push (2026-10-28)

`bug/rf-crashes-and-full-extent` is **pushed** (2026-11-02, `a9b09a91` on upstream `5ad5a025`, a plain
fast-forward push); it is not in the command below, and neither is `bug/free-rotation-3d-sync`, now part
of it. PR not opened yet: see
[reviews/pr-bugfix-rf-full-extent.md](reviews/pr-bugfix-rf-full-extent.md). Staging below still merges the
old branches; rebuild it with the combined branch before pushing it.

The other queue branches were rebased onto `upstream/master` `d7581658` (4.6.0-beta.1) on 2026-10-28,
and staging was rebuilt as `c3f640f5`. **Neither the branches nor that staging tree has been built
or tested on this base.** The last test run is the 2026-10-21 one on `8868dc2e` (branches.md). `origin`
still has the `52ee94fa`-based tips, so the leases are unchanged. Sessions cannot force-push; Jilei
runs this from the wrapper root. The retired branches are not in it.

```bash
git -C itksnap push origin \
  --force-with-lease=bug/linux-gcc-build:fb65f2b936d80c4229429aab5f32df8ceb7d5b2d \
  --force-with-lease=test/seg-anchor-4d:0b671e86a5478ac57f33ca40f3ac060cd14a0927 \
  --force-with-lease=feature/cardiac-io:ffb95b5e3d1c36afec1901f10460061d50ca9125 \
  --force-with-lease=staging/v460:6be1239a8dd9ebc25ee2aec6a232ccfcc4fcd906 \
  bug/linux-gcc-build test/seg-anchor-4d feature/cardiac-io staging/v460
```

Then delete this section. Old tips: `archive/1021/<branch>` (the `8868dc2e`-based ones, including
`feature/ui-language-setting` and staging `b842801f`), `archive/1002/<branch>` (the `651e82c0`-based
ones) and `archive/staging-v460-1021`.

## Status

<!-- AUTO:BEGIN -->
_Generated 2026-11-05 10:30 EST by `scripts/merge_order_status.py` — do not edit by hand._

`upstream/master` = `a16d5c3e` (2026-11-02).

| # | Branch | Tip | Ahead | Base | On `origin` | Verified | Why this position |
|---:|---|---|---:|---|---|---|---|
| 1 | `bug/linux-gcc-build` | `9a6d45c6` | 1 | ⚠️ old (`a4f01e8d`) — rebase | ⚠️ diverged | ⚠️ never | one line: the VTK floor to 9.5.2 (Q2); the GCC fixes went obsolete with upstream's Qt 6.9.3 floor |
| 2 | `bug/rf-crashes-and-full-extent` | `a9b09a91` | 0 | ⚠️ old (`a9b09a91`) — rebase | ✅ in sync | ✅ `a9b09a91` | one bug-fix PR (Jilei, 2026-10-28, 2026-11-02): free rotation (Fixes #229), the full-extent fix with its test, and the two RF/Layer Inspector crash guards; replaces bug/rf-layer-crashes, bug/full-extent-off-by-one and bug/free-rotation-3d-sync |
| 3 | `bug/4dcta-slice-order` | `b1da5935` | 1 | current | ✅ in sync | ✅ `b1da5935` | PR #307; reported on #128 against 4.6.0-beta1 (2026-11-03): the first 4D CTA time point loads upside down; one function and its test, on the current upstream/master |
| 4 | `release/4.6.0-beta.2` | `7385e8fe` | 3 | current | ✅ in sync | ⚠️ never | PR #308; version bump + release notes for #306 and the 4D CTA fix (Jilei, 2026-11-04); its own PR like upstream's #303; not seen by the git hook (release/ prefix), so refresh Status by hand |
| 5 | `test/seg-anchor-4d` | `bac56a42` | 1 | ⚠️ old (`a4f01e8d`) — rebase | ⚠️ diverged | ⚠️ never | tests only (seg_anchor with 4D data) |
| 6 | `feature/cardiac-io` | `c9a4e4a1` | 13 | ⚠️ old (`a4f01e8d`) — rebase | ⚠️ diverged | ⚠️ never | largest; its echo read guards were dropped for upstream's d61b7418 |

**Pairwise merges:** all 15 pairs merge cleanly.
**Ordering constraints:** queue order satisfies 1 of 1.
**`staging/v460`** (`4ec6ac0b`): ⚠️ rebuild — not on the current `upstream/master`; missing `bug/rf-crashes-and-full-extent`, `bug/4dcta-slice-order`, `release/4.6.0-beta.2`; 6 commit(s) not on any queue branch (SPRINT_PLAN §7).

**Needs attention:** `bug/linux-gcc-build` is not on the current `upstream/master`; `bug/linux-gcc-build` differs from `origin/bug/linux-gcc-build`; `bug/linux-gcc-build` has never been verified; `bug/rf-crashes-and-full-extent` is not on the current `upstream/master`; `release/4.6.0-beta.2` has never been verified; `test/seg-anchor-4d` is not on the current `upstream/master`; `test/seg-anchor-4d` differs from `origin/test/seg-anchor-4d`; `test/seg-anchor-4d` has never been verified; `feature/cardiac-io` is not on the current `upstream/master`; `feature/cardiac-io` differs from `origin/feature/cardiac-io`; `feature/cardiac-io` has never been verified; `staging/v460` needs a rebuild.
<!-- AUTO:END -->

---

## How to update

**Whenever a branch changes**, before ending the session:

1. **Read Status.** The hook will already have refreshed it. If it didn't — for example the hook
   isn't installed on this machine — run `scripts/merge_order_status.py`.
2. **For each branch flagged "moved since … — re-verify":**
   - build it standalone in a worktree with its own build directory. Run `git submodule update` in
     the worktree first: a rebase does not move its `c3d` and `greedy`, so `git status` shows them as
     `M` and the build silently uses the old ones;
   - run the full `ctest`, and compare the failure *set* with `upstream/master`'s;
   - re-check every Constraints row that names it;
   - then set its `verified-at` in Queue to the new tip.
   - Rebuild `staging/v460` with SPRINT_PLAN §7, and run the suite there too.
3. **New branch:** add a Queue line where it should merge, with `verified-at` set to `-`, and run
   the checks in step 2.
4. **Found a dependency:** add a Constraints row, with the measurement that shows it, and move the
   Queue line if the order now violates it. Status reports a violated constraint.
5. **Branch merged upstream:**
   - remove its Queue line, and any Constraints rows that name it;
   - `git -C itksnap fetch upstream`, rebase the remaining branches onto the new `upstream/master`
     (Status shows "old — rebase" until you do), and push them;
   - rebuild staging, and re-verify.
6. **Commit this file** with the session's checkpoint. "Needs attention: nothing" is the goal state
   for a handoff.

**Hook setup, once per machine:** `scripts/merge_order_status.py --install-hook`. This symlinks
`scripts/hooks/itksnap-reference-transaction` into the itksnap repo's hooks directory. The hook fires
after any committed update to `refs/heads/{feature,bug,test,staging}/*`, the matching
`refs/remotes/origin/*`, or `refs/remotes/upstream/master`. It never blocks or fails a git command.
To remove it, delete `itksnap/.git/hooks/reference-transaction`.
