# RESUME — ITK-SNAP 4.6.0 release · sprint just opened

## Current state (read this paragraph first)

The **release-460 sprint was opened 2026-07-30** and nothing has been built yet — the last session
was pure survey and scaffolding. ITK-SNAP trunk (`upstream/master` @ `679ba76a`) is already at
version **`4.6.0-alpha.1`**; **101 commits (83 non-merge)** have landed since v4.4.0 (`20f63186`,
2025-09-08), dominated by a new **remote/URL image I/O** subsystem (scp/sftp/HTTP/Flywheel) and
**SAM2** integration. An integration branch **`staging/v460`** exists **locally only** in
`itksnap/`, cut from `upstream/master` @ `679ba76a`, with tracking deliberately unset so a stray
push cannot hit `pyushkevich/itksnap`. Eight workstreams are specified in `workstreams/`; **none
has started**. Nothing was committed or pushed last session. The **agentic API is out of scope** —
it stays on `sprint/caimi` for the October CAIMI demo (`projects/agentic-api/`).

## The single next goal

**Get the four blocking decisions answered, then execute W1 (merge the ready backlog).**
W1 is 15 already-written, already-verified commits; it is the only workstream that can finish
without new design, and it unblocks a real `staging/v460`. The decisions, all in
`workstreams/merge-backlog.md` (Q1–Q4, with the per-commit ship/hold list as D1–D4):

1. **Workspace `FormatVersion` 1 → 2 → 3** (`a0f9d6f0`, `c3db9f65`). A 4.6.0 workspace will not open
   in 4.4.0. Move `SNAP_VERSION_LAST_COMPATIBLE_RELEASE_DATE` (still `20131201`), or make the reader
   degrade on an unknown version? **This is the single most consequential open item in the sprint.**
2. **VTK floor.** CI moved to 9.5.2 (`c480b003`); `CMake/standalone.cmake:72` still requires 9.3.1.
   They disagree today.
3. **jsoncpp** — new dependency from the NIfTI sidecar reader (`3033e9e1`). Available on all three
   CI platforms?
4. **Undo under async DLS** (`cb6f692e`) — `PaintbrushModel::CommitDrawing` defers `StoreUndoPoint`
   into the completion handler; cancelled/failed interactions are untested.

Then work `workstreams/merge-backlog.md` steps 1–8 in order.

**Do not start W4/W5** — both depend on W3 freezing the DLS API, and W3 has not begun.

## Files to read first (in order)

1. **`workstreams/merge-backlog.md`** — the concrete W1 plan, the per-commit ship/hold decision list
   (D1–D4), and the four blocking questions. The most useful file here.
2. **`SPRINT_PLAN.md`** — §2 is the dated branch and dependency-repo snapshot; §3 the eight
   workstreams; then done-criteria, sequencing, risks, and the cut line.
3. **`change_tracking.md`** — what already merged; §6 is the release-manager flag list.
4. **`PROGRESS_LOG.md`** — the 2026-07-30 entry for how these conclusions were reached.
5. **`../../SUBMODULE_SYNC.md`** (wrapper root) — which branch each submodule must track, and the
   reachability checks to run before pushing a pointer bump.

## Known traps

- **`staging/v460` had its tracking unset on purpose.** `git branch <name> upstream/master` silently
  sets upstream to `upstream/master`; a later bare `git push` would target `pyushkevich/itksnap`.
  If you re-create the branch, unset it again, or push explicitly with
  `git push -u origin staging/v460`.
- **`git branch -vv`'s `[origin/master: behind 1]` describes the LOCAL checkout, not the remote.**
  `origin/master` and `upstream/master` are both at `679ba76a`. Misreading this cost a wrong entry in
  three files on 2026-07-30 — check with `git rev-list --count origin/master..upstream/master`.
- **Do not re-implement the itksnap-dls refactor.** It already exists on `feature/agentic-api`
  (+6/−0 vs `main`, 21 files, +1333/−361, including TotalSegmentator and a test suite). W3 is a
  promotion problem. `features/segflow4d`, `test/dls_sam2`, and `claude/create-developer-guide-xaMCx`
  are all strict subsets of it.
- **`8539d63c` and `ad727107` are the same Linux/GCC patch set** on two branches. Take one.
- **`71e2544d` (submodule bump) is stale** — re-resolve `Submodules/{c3d,greedy}` against current
  upstream rather than replaying that commit.
- **Push submodules BEFORE recording the pointer in the wrapper.** This broke five wrapper commits
  last sprint. Run the reachability check in `SUBMODULE_SYNC.md` §3 — and do **not** "simplify" it to
  `git ls-remote | grep <sha>`; `ls-remote` lists only ref tips and reports healthy ancestor pointers
  as missing. Use `git branch -r --contains` after a fetch.
- **`.gitmodules` drifts silently.** It will need to move `itksnap` → `staging/v460` and later
  `itksnap-dls` → `main`. A bare `git submodule update --remote` discards undeclared switches.
- **Three tests already fail** on Linux headless (baseline 30/33, 2026-07-17):
  `4DContinuousRenderingD` (a one-character CMake typo — W8 item 1), `4DReplayWithMeshUpdate`
  (timing-flaky under llvmpipe), `RemoteImageLoadTest_Cache`. Inherit them as stated debt; a 4th
  failure is a regression.
- **Never `pkill -f "<string>"` from your own shell** — the pattern matches the tool shell's own
  command line and kills it. Servers by port, GUIs by `setsid` + `kill -TERM -<pid>`.
- **Build FOREGROUND.** `nohup &` reports success instantly while `ninja` is still linking. Confirm
  the binary mtime advanced before testing.

## How to work

W1 is the whole job. It is unglamorous — merging work that already exists — but it is the only path
to a `staging/v460` that means anything, and every other workstream measures itself against it. The
temptation will be to start W4 or W7 because they are new; resist it. Prefer one finished workstream
over three started ones, and remember the cut line: **W1 + W2 + W8 alone is a shippable 4.6.0.**
Run `/handoff` at the end of the session rather than improvising it.
