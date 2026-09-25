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
bug/linux-gcc-build         fb65f2b9     smallest; no behavior change; the VTK-floor commit can be dropped on its own
bug/rf-layer-crashes        9e80001f     crash fixes + the test that catches them; indivisible; must precede harness-false-green
test/harness-false-green    83c44f62     after rf-layer-crashes (constraint below)
test/seg-anchor-4d          0b671e86     tests only (seg_anchor with 4D data); passes on upstream as is
bug/full-extent-off-by-one  6a72f6a1     small fix in Paul's seg_anchor code, with its test
bug/seg3d-into-4d-check     635bd1ac     small fix in Paul's seg_anchor code, with its test
feature/cardiac-io          2fc0d9b8     largest; add the %R-R round-trip test before the PR
test/harness-gui-thread     8a28d50c     last: discuss with Paul first, it competes with upstream dbf8e79f
```
<!-- QUEUE:END -->

Only the constraints below are hard. The rest of the order is a recommendation: least
controversial first, then the branches that still need work or a conversation.

## Constraints

**Ordering.** The script checks that the queue respects every row. Keep the first two cells as
backticked branch names.

| Before | After | Why | Evidence | Verified |
|---|---|---|---|---|
| `bug/rf-layer-crashes` | `test/harness-false-green` | harness-false-green makes a missing test script fail. Upstream lists `RandomForestBailOut` in `GUI_TESTS` but never registered its script — the registration is in rf-layer-crashes. | harness-false-green alone: `RandomForestBailOut` fails as "no such test" (0.88 s) | 2026-09-24, macOS |

**Indivisible.**

- **`bug/rf-layer-crashes` cannot be split.** `upstream/master` plus only `6afd0d10`, the test
  registration, gives `RandomForestBailOut` **SEGFAULT at 19.8 s**. The whole branch passes in
  20.0 s. Measured 2026-09-24.

**Separable.** Not constraints, but options the meeting can use:

- `bug/linux-gcc-build`: `fb65f2b9` (VTK floor → 9.5.2) can be dropped without touching
  `9ca38fcb` (the portability fixes).

---

## Status

<!-- AUTO:BEGIN -->
_Generated 2026-09-24 15:59 EDT by `scripts/merge_order_status.py` — do not edit by hand._

`upstream/master` = `52ee94fa` (2026-09-03).

| # | Branch | Tip | Ahead | Base | On `origin` | Verified | Why this position |
|---:|---|---|---:|---|---|---|---|
| 1 | `bug/linux-gcc-build` | `fb65f2b9` | 2 | current | ✅ in sync | ✅ `fb65f2b9` | smallest; no behavior change; the VTK-floor commit can be dropped on its own |
| 2 | `bug/rf-layer-crashes` | `9e80001f` | 4 | current | ✅ in sync | ✅ `9e80001f` | crash fixes + the test that catches them; indivisible; must precede harness-false-green |
| 3 | `test/harness-false-green` | `83c44f62` | 1 | current | ✅ in sync | ✅ `83c44f62` | after rf-layer-crashes (constraint below) |
| 4 | `test/seg-anchor-4d` | `0b671e86` | 1 | current | ✅ in sync | ✅ `0b671e86` | tests only (seg_anchor with 4D data); passes on upstream as is |
| 5 | `bug/full-extent-off-by-one` | `6a72f6a1` | 1 | current | ✅ in sync | ✅ `6a72f6a1` | small fix in Paul's seg_anchor code, with its test |
| 6 | `bug/seg3d-into-4d-check` | `635bd1ac` | 1 | current | ✅ in sync | ✅ `635bd1ac` | small fix in Paul's seg_anchor code, with its test |
| 7 | `feature/cardiac-io` | `2fc0d9b8` | 12 | current | ✅ in sync | ✅ `2fc0d9b8` | largest; add the %R-R round-trip test before the PR |
| 8 | `test/harness-gui-thread` | `8a28d50c` | 1 | current | ✅ in sync | ✅ `8a28d50c` | last: discuss with Paul first, it competes with upstream dbf8e79f |

**Pairwise merges:** all 28 pairs merge cleanly.
**Ordering constraints:** queue order satisfies 1 of 1.
**`staging/v460`** (`d02236c3`): contains `upstream/master` and every queue tip, and nothing else. ✅

**Needs attention:** nothing.
<!-- AUTO:END -->

---

## How to update

**Whenever a branch changes**, before ending the session:

1. **Read Status.** The hook will already have refreshed it. If it didn't — for example the hook
   isn't installed on this machine — run `scripts/merge_order_status.py`.
2. **For each branch flagged "moved since … — re-verify":**
   - build it standalone in a worktree with its own build directory;
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
