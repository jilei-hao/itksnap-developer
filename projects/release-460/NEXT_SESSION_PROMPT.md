# RESUME — ITK-SNAP 4.6.0 · no goal chosen yet: ask Jilei first

## Current state (read this paragraph first)

Upstream `pyushkevich/itksnap` master is **`a16d5c3e`** (2026-11-02). It is 4.6.0-beta.1 (tag
`v4.6.0-beta1`) plus **#306**, our bug-fix PR, which Jilei merged. #306 carries free rotation (Fixes
#229), the full-extent off-by-one, and two crash guards. Two of our PRs, opened 2026-11-04, are
waiting for review:
- **[#307](https://github.com/pyushkevich/itksnap/pull/307)**, `bug/4dcta-slice-order` @
  `b1da5935`. A 4D CTA time point loaded upside down when one file wrote a tag differently. It was
  reported on #128, and the full suite passes 82/82 on macOS.
- **[#308](https://github.com/pyushkevich/itksnap/pull/308)**, `release/4.6.0-beta.2` @ `7385e8fe`.
  It sets the version to 4.6.0-beta.2 (Nov 4, 2026) and updates the release notes. Merge it after
  #307.

The reply on #128 that points the reporter to #307 is **drafted but not posted**. The v4.6.0
milestone is due **2026-11-20**. Three older branches remain in the queue: `bug/linux-gcc-build`,
`test/seg-anchor-4d` and `feature/cardiac-io`. They sit on an old base and differ from `origin`, and
none is built on beta.1. `staging/v460` needs a rebuild. The sprint docs were committed in the
2026-11-05 checkpoint; before that they had been uncommitted since 2026-09-30.

## Session goal

**None chosen.** Jilei picks each session's goal (SPRINT_PLAN rule 2). Show the open list below,
grouped as it is, and ask which item to work on before touching code. If the chosen item depends on
something unfinished, say so first.

## The open list: a reminder, not a queue

**4.6.0-beta.2 (#307, #308)**
- **Post the reply on #128.** The draft is in PROGRESS_LOG, 2026-11-04. It needs Jilei's OK.
- #307: CI (6 checks were pending when it was opened), then Paul's review. The PR was bound to the
  2026-11-04 session, so a new session must bind it again to see its status.
- #308: merge only after #307. Then tag `v4.6.0-beta2` (Paul's tag name for beta.1 was
  `v4.6.0-beta1`). The branch is configured in `build-release-4.6.0-beta.2` but not built.
- Optional checks for #307 (`reviews/4dcta-slice-order-test-plan.md`): the GUI steps 2–4 are not
  recorded, and the AVRP real-data before/after has not been run.
- Paul's own release-note sub-bullets under "Large images" and "Windows" state the bug without
  "Fixed". They were left as they are; Jilei may want them changed.

**Bookkeeping after #306** (nothing blocks it)
- Take `bug/rf-crashes-and-full-extent` out of the MERGE_ORDER queue, which still asks to rebase it,
  and out of upstream.md "Our work not yet upstream". It is merged.
- Check that #306 closed #229. It said "Fixes #229", and #229 was on milestone v4.6.2.
- Mark W6 done in `workstreams/free-rotation-sync.md`. SPRINT_PLAN §3 is already ticked.
- Delete merged branches (W8 item 7; each delete needs Jilei's OK). The list now also includes
  `bug/free-rotation-3d-sync`, `bug/full-extent-off-by-one`, `bug/rf-layer-crashes` and
  `bug/rf-crashes-and-full-extent`.

**The rest of the review queue** (MERGE_ORDER Status, "Needs attention")
- `bug/linux-gcc-build`: the VTK floor to 9.5.2, Paul's call. Rebase it onto the current master.
- `test/seg-anchor-4d`: rebase, build and test. Jilei force-pushes it.
- `feature/cardiac-io`: the largest. Rebase it; it still has no round-trip test. The workspace
  `FormatVersion` decision (SPRINT_PLAN §3) belongs to it.
- `test/harness-gui-thread` is parked: ask Paul first.
- Rebuild `staging/v460` (§7 recipe). The local tip `4ec6ac0b` is not pushed, and the wrapper's
  `itksnap` pointer points at it: do not commit that pointer until it is pushed.

**GitHub, each needs Jilei's OK**
- Close #20 as a duplicate of #69.
- `Common/ExtendedGDCMSerieHelper.cxx:60` throws a bare number instead of the `IRISException` (the
  arguments sit outside the constructor call). File an issue, or fix it on its own branch.
- The `pr-merge/*` pushes in `reviews/milestone-triage-2026-10-21.md` look obsolete, because
  #243, #252 and #255 are merged. Check before acting.

**Code we can do alone on the Mac**
- W8 open items in `workstreams/bugfixes.md`: crash fixes 26–30, 35 and 15b; tests that pass without
  checking anything, 22, 23 and 31–34; 45, Reorient (no issue yet). They were last checked on
  2026-09-30, and Paul's cleanup has landed since, so check each against master first.
- `change_tracking.md` past `679ba76a`.

**Needs another machine**
- Linux: blocked by the Qt ≥ 6.9.3 floor (W8 42). The last full Linux `ctest` was in July.
- Windows: W8 43 (GUI tests write into the real `%APPDATA%`).

**Other workstreams:** W1 async DLS (blocked on Q4); W3, the itksnap-dls refactor, which W4 and W5
depend on; W7, cmesh.

**Release engineering:** 4.6.0 final (milestone due 2026-11-20); the wrapper's `SUBMODULE_SYNC.md`
and `CLAUDE.md`.

## Files to read first

1. `SPRINT_PLAN.md`: the rules at the top and §3. **§2 is stale** (dated 2026-10-21 and 10-02):
   refresh it with §7 before relying on it.
2. `MERGE_ORDER.md`: Status, then Queue, then the constraints table.
3. `upstream.md`: the PR table at the end (#307, #308), and "Our work not yet upstream —
   2026-10-28", which is partly stale (#306 is merged).
4. `branches.md` §13 (#307) and §14 (#308).
5. `reviews/4dcta-slice-order-test-plan.md`.
6. `PROGRESS_LOG.md`: the entries dated 2026-10-21, 2026-10-28 (which runs to 11-02) and 2026-11-04.

## Known traps

**Release and GitHub**
- **Never merge a PR yourself.** Jilei merges; they merged #301 and #306. Every issue, comment,
  milestone change, or push to someone else's branch needs Jilei's OK first.
- **`gh` does not work on this Mac.** The keyring token is invalid, and `api.github.com` gives TLS
  x509 errors. Use Claude in Chrome. Several Chrome browsers connect, and only one is signed in as
  `jilei-hao`. On 2026-11-04 the first one picked was wrong, so check before acting.
- **This session cannot force-push.** The permission guard blocks `--force-with-lease`. Give Jilei
  the exact command. Plain pushes work.
- **`release/` branches are not seen by the git hook.** After changing one, run
  `scripts/merge_order_status.py` by hand.
- **A rebase does not move submodules.** Run `git submodule update` in a worktree before a full suite
  (the 81/81 run of 2026-10-30 was not on the branch's exact tree).
- A version bump changes three lines in `CMakeLists.txt` (qualifier, release date, formatted date)
  and `ReleaseNotes.md`, nothing else.
- Release-note lines say what is fixed ("Fixed …", "now …"), not only what was wrong.

**Testing**
- **Compare failure *sets*, never totals.** `4DReplayWithMeshUpdate` is flaky upstream (W8 2).
- **A GUI test that passes in under a second is not running.** For example, `RandomForestBailOut`
  takes about 20 s and `4DContinuousRendering` about 38 s.
- **Make sure a "before" build was built from the tree you think it was** (the 2026-11-02 slip).
  `build-full-extent-off-by-one/` is now a tree identical to upstream `a16d5c3e`.
- `--test` accepts a script path, so a throwaway script can read any widget value from the real app.
- **Regenerate test DICOM data with `~/miniconda3/envs/instant3d`** (pydicom 3.0.1). pydicom 3.0.2
  changes the Implementation Version Name in every file.
- On macOS, `HOME` does not move ITK-SNAP's settings folder; also set `CFFIXED_USER_HOME`.
- **Warn Jilei before any deliberate crash.** Each abort pops a macOS crash dialog.

**Machine (Mac)**
- Memory is tight: build with `ninja -j4`. The Bash tool stops at 10 minutes, and the full suite
  takes about 21 minutes, so run `ctest` in the background.
- **Scripted doc edits:** read the `git diff` afterwards. In MERGE_ORDER, a phrase can appear in both
  the Queue and the generated Status, so edit the QUEUE block only, then regenerate.

## Left on disk

- **Worktrees** (`worktrees/`):
  - current: `4dcta-slice-order`, `release-4.6.0-beta.2`, `seg-anchor-4d`, `cardiac-io`;
  - `pr-review`: `pr-test/free-rotation`, a scratch for review builds;
  - `full-extent-off-by-one`: the merged #306 branch;
  - retired: `free-rotation-3d-sync`, `remote-cache-test-datadir`, `seg3d-into-4d-check`,
    `ui-language-setting`, `windows-decimal-comma`;
  - out of scope: `agentic-api` and `caimi`.
- **Builds:** each `build-<worktree>` matches its worktree. `build-full-extent-off-by-one` is the
  "before" build for #307, and `build-4dcta-slice-order/repro/` holds the reporter's generated exam.
- **Refs:** local `pr-merge/{243,252,255}` and `pr-test/{301,302,free-rotation}`; tags
  `archive/1002/*`, `archive/1021/*` and `archive/staging-v460-*`.

Run `/handoff` at the end.
