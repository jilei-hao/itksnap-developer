# RESUME — ITK-SNAP 4.6.0 · Ask Jilei for this session's goal

## Current state (read this paragraph first)

**The release work is now five topic branches off `upstream/master` @ `52ee94fa`, not commits on
`staging/v460`.** On 2026-09-24 the branch model changed (SPRINT_PLAN rules 1–3): every feature
or fix lives on its own branch so Jilei can review and merge them one at a time in the planning
meeting, and `staging/v460` is a **testing-only** merge of all of them. The five —
`feature/cardiac-io`, `bug/linux-gcc-build`, `bug/rf-layer-crashes`, `test/harness-false-green`,
`test/harness-gui-thread` — are listed with evidence in **`branches.md`**. They merge pairwise without
conflicts, and rebuilt staging is byte-identical to the pre-split tip. **All of it is pushed to
`jilei-hao/itksnap`**, and the wrapper is committed. The merge order, its measured constraints and the
live state of every branch are in **`MERGE_ORDER.md`**. It must be updated whenever a branch changes
(SPRINT_PLAN rule 3); its Status section regenerates itself through a git hook. Upstream moved 26
commits while we were away. It merged our W2 docs (PR #244), and in `dbf8e79f` it fixed the harness threading problem its own
way. Standalone test results per branch are in `branches.md` → Summary. The agentic API stays out of
scope on `sprint/caimi`.

## This session's goal: not chosen — ask

**Jilei picks the item for each session. Do not start work until they name it.** If the session opens
with nothing more specific than "resume", show the list below, grouped as it is, and ask. It is a
reminder of what is open, not a priority order. If the named item depends on something unfinished
(SPRINT_PLAN §5), say so before starting.

At `/handoff`, rewrite this file with the same shape: current state, this list refreshed, and **no
chosen next goal**.

## The open list

**Review queue — getting the five branches merged**

- **Merge order constraint, measured** (the full list is in `MERGE_ORDER.md`): `bug/rf-layer-crashes` goes before
  `test/harness-false-green`. On its own, the latter honestly fails upstream's never-registered
  `RandomForestBailOut`. `bug/rf-layer-crashes` cannot be split either: registering the test without
  its fixes SEGFAULTs.
- `feature/cardiac-io` has **no test in `Testing/`**. Add a `.seq.nrrd` + `.nii.gz`/sidecar
  round-trip test that fails if the `%R-R` axis is dropped. This is the one gap that weakens its PR.
- Linux/GCC run on the branches. The last Linux run was on `7cc60053`, in July. Expected to confirm
  `RandomForestBailOut` green there.
- Talk to Paul about `test/harness-gui-thread` before opening a PR: it competes with his `dbf8e79f`.
- Write PR descriptions from `branches.md` once branches are accepted.

**W1 — ready backlog** (`workstreams/merge-backlog.md`)

- Async DLS (`cb6f692e`, `ea86df0d` on `test/dls_sam2`). Blocked on two defects in `cb6f692e`: an
  undo gap on throw, and a `this`-capturing lambda (use-after-free). Fix both on a new
  `feature/dls-async`.
- Re-resolve the `Submodules/{c3d,greedy}` bump against current upstream.
- Delete the merged branches: W8 item 7's seven, plus `developer-doc`.

**Other workstreams**

- **W3** itksnap-dls refactor — already written on `itksnap-dls:feature/agentic-api`; the job is
  promoting it to `main` (`workstreams/dls-refactor.md`).
- **W4** auto-segmentation UI and **W5** propagation UI — both depend on W3. Mockups are in
  `user_files/`.
- **W6** free-rotation 2D/3D sync — issue #229, a bug.
- **W7** cmesh integration — tag `convert-mesh`, add it as a submodule, refactor `Logic/Mesh/`.

**W8 — open items, by cluster** (`workstreams/bugfixes.md` has the evidence for each)

- **Harness can't report failure:**
  - 23: `findChild` misses are silent.
  - 31: `validateFloatValue` passes NaN, and a missed lookup becomes NaN.
  - 32: `comboBoxSelect` selects row 0 on a miss.
  - 33: `invokeMethod`/`setProperty` results are discarded.
  - 34: load helpers never check that the load happened.
  - 22: `RandomForestBailOut` paints nothing.
  - Recheck each against upstream's rewritten `test_Library.js` and helpers first — `dbf8e79f` may
    have changed the shape.
- **Crashes:**
  - 26: `Generic3DRenderer` uses a stale mesh-layer id.
  - 27: GMM actions are `assert()`-only.
  - 28: `on_actionClearActive` holds a pointer across a modal dialog.
  - 29: an observer leak in `AbstractLayerAssociatedModel`.
  - 30: `ProgressReportWidget` pumps events without a modal barrier.
  - 35: `ResetSNAPSegmentationImage` is `assert()`-only.
  - 15b: the `assert()`-only pattern across the codebase.
- **Flaky tests:**
  - 2: the `4DReplayWithMeshUpdate` latent hang.
  - 3: `RemoteImageLoadTest_Cache` on Linux.
  - 3b: exact equality on a tdigest quantile.
- **Linux-only:**
  - 18: GCC `-Wreturn-type`.
  - 19: deprecated curl form APIs in `RESTClient`.
  - 20: the available-memory probe reads 0.0 GB.
- **Cardiac metadata:**
  - 8: loose 4DCTA detection.
  - 9: a stray `.nii.gz` loses its frame axis (document it).
  - 10: `FormatVersion` is never validated.
  - 11: an older build strips cardiac keys on re-save.
- **Other:**
  - 12: four DLS threading races.
  - 16: the memory-leak canary baseline is invalid.

**Release engineering** (SPRINT_PLAN §3)

- Version to beta, then `4.6.0`.
- Decide on workspace `FormatVersion`.
- `ReleaseNotes.md` 4.6 section.
- Refresh `change_tracking.md` past `679ba76a`.
- Wrapper `SUBMODULE_SYNC.md` / `CLAUDE.md` for the post-release submodule contract.

## Where work goes

- **New item → new topic branch off `upstream/master`**, prefixed `feature/`, `bug/` or `test/`. Then
  immediately run `git branch --unset-upstream <name>`, because `checkout -b X upstream/master`
  makes a bare push target Paul's `master`.
- **A fix to an existing topic goes on that topic's branch**, never on `staging/v460`.
- **After any branch changes:**
  - rebuild staging with SPRINT_PLAN §7's recipe;
  - push the branch;
  - bring `MERGE_ORDER.md` to "Needs attention: nothing" — re-verify each branch it flags and update
    its `verified-at`.
  The hook refreshes Status on every ref update. On a machine without the hook, run
  `scripts/merge_order_status.py --install-hook` once.
- **Build each branch on its own**, in a worktree with its own build directory. A full macOS build
  takes about 4 minutes. `build-release/` follows the main checkout, which is on `staging/v460`.
- **Before starting on an item, check whether upstream already fixed it:**
  `git log <last base>..upstream/master -- <files>`. It happened three times in August.

## Files to read first

1. **`MERGE_ORDER.md`** — the order, the constraints, and the live Status. Read "Needs attention"
   first.
2. **`branches.md`** — what each branch contains, and its standalone test results.
3. **`SPRINT_PLAN.md`** — the three rules at the top, §2 (branch model), §3 (open items), §4 (baseline).
4. The workstream file for whichever item Jilei names.
5. **`PROGRESS_LOG.md`** — the 2026-09-24 entries.

## Known traps

- **Compare failure *sets*, never totals.** The remote tests fail only when the three run
  back-to-back (item 3/3b), and which one fails rotates, so the total moves on its own.
- **A GUI test that passes suspiciously fast is not passing** (item 13). `RandomForestBailOut` takes
  about 20 s and `MeshWorkspace` about 54 s. Sub-second means the test didn't run.
- **`RandomForestBailOut` is green but paints nothing** (item 22). **Don't just repoint the
  selector**: the "training threw" path it follows is what exposed item 15d. Add a second test.
- **`MeshWorkspace` is not a flake.** If it goes red, it is a real regression.
- **Register a new test script in BOTH `TestingScripts.qrc` and `GUI_TESTS`.** Missing either one
  is how items 1 and 14 went unnoticed for years.
- **`protected slots:` does not hide a method from test scripts.** QJSEngine exposes protected
  slots (item 25).
- **`ctest | tail` returns *tail's* exit status.** Redirect to a file instead.
- **Use an absolute `--testdir`.** A relative one silently fails the image load.
- **zsh does not word-split `$var`.** Loop over an array (`B=(a b); for x in $B`). A
  space-separated string runs the loop once, or zero times, with no error.
- **Build in the foreground on macOS.** `nohup &` reports success while the linker is still running.
- **Never run `pkill -f "<string>"` from your own shell.** It matches the tool shell's own command
  line.
- **Push submodules BEFORE bumping the wrapper pointer.** Check reachability with
  `git branch -r --contains`.
- **`config.local.sh` is gitignored and per-machine.** Don't "sync" macOS and Linux.
- **The memory-leak canary baseline in `itksnap/CLAUDE.md` is invalid** (item 16). Re-measure it;
  don't assume.
- **macOS crash reports are a cheap corpus.** `~/Library/Logs/DiagnosticReports/ITK-SNAP-*.ips`
  are JSON. Classify them by the faulting thread's stack before theorising.

## How to work

The bar is behavioural. Reproduce the bug, fix it, and reproduce the fix. Ask an auditor to refute,
not to review. If a fix changes *when* a pointer becomes null, run the whole suite, not the one test.
Run `/handoff` at the end rather than improvising it.
