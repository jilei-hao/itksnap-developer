# RESUME — ITK-SNAP 4.6.0 · Linux verification of `staging/v460`

## Current state (read this paragraph first)

**W1 is done on macOS and completely unverified on Linux. This session is the Linux check.**
`itksnap:staging/v460` is **pushed** to `origin` (`jilei-hao/itksnap`) at **`7cc60053`**, 18 commits
ahead of `upstream/master`: the 12-commit `feature/cardiac-io` stack, the Linux/GCC portability fixes
(`e2f19b56`), three test-infrastructure fixes, and the VTK floor raised to 9.5.2 (`7cc60053`). On
macOS arm64 it builds clean (446 targets, 0 errors) against a freshly built **VTK 9.5.2** and runs
**31/33** on `ctest`. **The Linux box has never seen any of it** — it is still on **VTK 9.3.0**, so
`cmake` will refuse to configure until VTK is upgraded there. Wrapper `main` has **4 unpushed
commits** (`2c65c23`, `2a6bea1`, `8a84392`, `4bda8dc`) — one of which you need before you can build
(see the first trap). The agentic API stays out of scope on `sprint/caimi`.

## The single next goal

**Get `staging/v460` building and testing on Linux/GCC, with no local patches.**

That last clause is the point. Historically the Linux build needed six patches applied by hand
(recorded in the wrapper `CLAUDE.md`); `e2f19b56` puts five of them *on the branch*, and the sixth —
the VTK floor relax — was deliberately dropped in favour of upgrading VTK. So this should be the
first time the Linux build works from a clean checkout. **If you still have to patch anything, that
is the finding.**

In order:

1. **Get the fixed `build-deps.sh`** — see trap 1. Without it the VTK upgrade silently builds the
   wrong version.
2. **Upgrade VTK to 9.5.2** on the Linux box. Edit `config.local.sh` there (it is gitignored, so it
   is per-machine):
   ```
   VTK_VERSION=9.5
   VTK_FULL_VERSION=9.5.2
   VTK_DIR=/home/jileihao/dev/vtk-dev/installed/lib/cmake/vtk-9.5
   ```
   Then `./scripts/build-deps.sh --skip-itk --skip-qt`. **VTK must be built with
   `RenderingExternal`** — `QtFrameBufferOpenGLWidget` uses `vtkExternalOpenGLRenderWindow`. The
   script already passes it; verify it landed rather than assuming.
3. **Build `staging/v460`** with **no local edits**. `scripts/build-release.sh`, or cmake directly.
   Build the `all` target, not just `ITK-SNAP` — the CLI tools and `SSHTunnelTest` are where two of
   the portability fixes bite.
4. **Run the suite**: `xvfb-run -a ctest`. Compare against the expectations below.
5. **Record the result** in `PROGRESS_LOG.md` and update `SPRINT_PLAN.md` §4's baseline with a real
   Linux number for `staging/v460`.

Only after Linux is green should W1 steps 6–8 be touched. **Step 6 is blocked** — not on a missing
test, but on two real defects in `cb6f692e` (see `workstreams/merge-backlog.md` Q4).

## What to expect from `ctest`

macOS baseline on this exact commit: **31/33**. Two known failures, both pre-existing, neither caused
by the merge or the VTK upgrade:

| Test | Why |
|---|---|
| `RemoteImageLoadTest_WorkspaceWithMesh` | Asserts **exact equality on an approximate tdigest quantile**. Byte-identical inputs give a different value every run; ~1 pass in 4. Structurally flaky, not environmental. |
| `RandomForestBailOut` | Runs for the first time since 2018 and aborts on the worker-thread bug (W8 item 17). |

Two positive checks, both cheap and both meaningful:

- **`4DContinuousRendering` must take ~35 s.** If it passes in under a second it is not running —
  that was the false-green bug fixed in `97285971`.
- `RemoteImageLoadTest_Cache` failed on Linux in July but passes on macOS. Worth seeing which way it
  goes now.

**A third failure is a genuine Linux-specific regression** and is the thing this session exists to
find. The old "30/33" Linux figure in the wrapper `CLAUDE.md` is **not** a valid comparison — it was
measured when missing-script tests silently passed.

## Files to read first (in order)

1. **`SPRINT_PLAN.md`** — §2 is the dated branch/dependency snapshot; §4 holds the test baseline and
   the warning about the superseded Linux number.
2. **`workstreams/merge-backlog.md`** — what is on the branch and why; Q1–Q4 with their answers.
   Q4 explains why step 6 is blocked.
3. **`workstreams/bugfixes.md`** — W8 items 13–17, the test-infrastructure findings. Item 17 is the
   one that matters most.
4. **`PROGRESS_LOG.md`** — the 2026-07-31 entry for this session.
5. **Wrapper `CLAUDE.md`** — the Linux build section: apt packages, dependency paths, and the
   patch table (now marked superseded where `e2f19b56` covers it).
6. **`../../SUBMODULE_SYNC.md`** — branch contract per submodule and the reachability checks before
   any pointer bump.

## Known traps

- **The fixed `scripts/build-deps.sh` is in unpushed wrapper commit `4bda8dc`.** The *old* script
  skips the clone whenever `lib/vtk/src/.git` exists, without checking the tag — so bumping
  `VTK_VERSION` compiles the 9.3.0 source and installs it as `vtk-9.5`. It looks like it worked;
  the directory name lies. Either push the wrapper first or check the tag out by hand.
- **`build_itk()` has the same clone-skip bug**, untouched. Do not bump `ITK_VERSION` on the old
  script either.
- **`git branch -vv`'s `[origin/master: behind 1]` describes the LOCAL checkout, not the remote.**
  Misreading it cost wrong entries in three files. Verify with
  `git rev-list --count origin/master..upstream/master`.
- **`ctest | tail` returns *tail's* exit status.** It reported success over two failing tests here.
  Redirect to a file and check `$?` directly; never pipe a command whose exit code you need.
- **A GUI test that passes suspiciously fast is not passing.** Until `97285971`, a missing script
  exited 0. If a test's duration drops sharply, check it still loads its script.
- **`RandomForestBailOut` is red on purpose.** It was never weakened or skipped to get green — see
  the test-as-ratchet rule. Do not "fix" it by reverting `4e1baa2a`.
- **The memory-leak canary baseline in `itksnap/CLAUDE.md` is invalid** (≤600 leaks / ≤90 KB for
  `RandomForestBailOut`) — measured on a process that loaded no script. Re-baseline only after
  W8 item 15's follow-ups.
- **Build FOREGROUND.** `nohup &` reports success instantly while the linker is still running.
  Confirm the binary mtime advanced before testing.
- **Never `pkill -f "<string>"` from your own shell** — the pattern matches the tool shell's own
  command line and kills it. Servers by port, GUIs by `setsid` + `kill -TERM -<pid>`.
- **Push submodules BEFORE bumping the wrapper pointer**, and run the `SUBMODULE_SYNC.md` §3
  reachability check — using `git branch -r --contains`, **not** `git ls-remote | grep <sha>`, which
  lists only ref tips and reports healthy ancestor pointers as missing.
- **`.gitmodules` still points `itksnap` at `sprint/caimi`.** If the wrapper should track
  `staging/v460` now that the release is the active work, that is a deliberate edit to both
  `.gitmodules` and `SUBMODULE_SYNC.md` — decide it, do not let it drift.

## How to work

This is a verification session, not a building one. The valuable output is a trustworthy Linux
number and a clear answer to "does it build with no local patches" — not new features. If the build
fails, fix it on the branch and record the fix in the patch table; if it builds, say so plainly with
the ctest output rather than hedging.

Resist starting W3–W7. W1 is nearly closed and the cut line still holds: **W1 + W2 + W8 alone is a
shippable 4.6.0.**

Run `/handoff` at the end rather than improvising it.
