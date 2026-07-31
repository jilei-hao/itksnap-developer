# RESUME — ITK-SNAP 4.6.0 · Fix the GUI test harness (W8 item 17)

## Current state (read this paragraph first)

**Both build paths are now green and W1 is verified everywhere except its last three steps.**
`itksnap:staging/v460` is pushed at **`7cc60053`**, 18 commits ahead of `upstream/master`. It builds
clean on **macOS arm64** (446 targets) and, as of 2026-07-31, on **Linux/GCC** — 766/766 targets, 0
errors, **with no local patches of any kind**, which is the thing the previous two sessions were
trying to establish. Both boxes now run **VTK 9.5.2**. `ctest` is **31/33 on macOS** and **30/33 on
Linux**, with no new failures on either; the differing totals are platform-specific known debt, not
a regression (see the warning in §4 of `SPRINT_PLAN.md` before comparing them). Wrapper `main` has
one unpushed checkpoint commit. The agentic API stays out of scope — it lives on `sprint/caimi` for
the October CAIMI demo.

## The single next goal

**Fix W8 item 17: the GUI test harness drives Qt from a worker thread.**

`class TestWorker : public QThread` runs the test script inside `run()` (`SNAPTestQt.h:27`), so every
scripted `click()`, `setCurrentIndex()` and `trigger()` executes off the main thread. Qt does not
support this. The fix is to marshal scripted widget calls to the main thread
(`Qt::BlockingQueuedConnection`).

**Why this and not the next merge.** It is not the most exciting item, but it is the one everything
else is waiting on:

1. **W1 cannot close without it.** W1's done-criteria require "a test covers undo after a cancelled
   async DLS interaction", and Q4 deliberately declined to write that test — async behaviour tested
   on a thread-unsafe harness is not evidence either way. Step 6 is blocked on Q4's two `cb6f692e`
   defects *and* on having somewhere trustworthy to test them.
2. **It gates the new item 15d.** The Linux segfault below can only be confirmed once the harness
   stops being a plausible alternative explanation.
3. **It undermines every GUI number in this sprint.** It affects all 21 GUI tests and is the most
   likely source of the suite's run-to-run instability, including `4DReplayWithMeshUpdate`.

If it proves larger than one session, the fallback is W2 (developer docs — net-new, independent, and
on the cut line: **W1 + W2 + W8 alone is a shippable 4.6.0**). Do not start W3–W7.

## What was just found, and what it changes

**W8 item 15d — the use-after-free retracted in item 15 is real, and Linux proves it.**
`RandomForestBailOut` still SEGFAULTs on Linux after `1d1fe7ea`. Live gdb backtrace:

```
on_btnClassifyTrain_clicked [.cold]   → Classify/Train threw
  ReportNonLethalException
    QDialog::exec()                   → modal dialog re-enters the event loop
      … sendPostedEvents → onQueuedEvent → dispatchEvent(EventBucket)
        LayerInspectorRowDelegate::onModelUpdate → UpdateOverlaysMenu()
          __dynamic_cast              → SIGSEGV
```

Faulting cast: `LayerInspectorRowDelegate.cxx:551`,
`dynamic_cast<ImageWrapperBase*>(m_Model->GetLayer())`. **The error dialog is the trigger** — a
non-lethal exception report opens a nested event loop that delivers a queued ITK→Qt event to a
delegate whose layer is being torn down.

Item 15's original reading was withdrawn in favour of a null `m_ClassificationEngine`. **Both are
true.** The retraction was correct *for macOS*, where the run never enters RF mode (item 15c) so
this path is unreachable. On Linux the script gets through classification and cancel, and dies where
originally described. `1d1fe7ea` fixed a real null deref; it did not fix this. **Do not treat the
macOS and Linux failures of this test as the same bug.**

Not yet proven: that the concurrent teardown is the script's "Cancel segmentation" racing the modal
dialog via the worker-thread harness. That is the obvious candidate — and it is another reason item
17 comes first.

Also new, all pre-existing upstream and none from the merge: **item 18** (five `-Wreturn-type` sites,
GCC-only), **item 19** (`RESTClient.cxx` on curl APIs deprecated since 7.55/7.56), **item 20**
(`TestLargeImageCheck` reports "0.0 GB available" on a box with free RAM).

## Files to read first (in order)

1. **`workstreams/bugfixes.md`** — item 17 is the goal; 15, 15b, 15c, 15d are its context.
2. **`SPRINT_PLAN.md`** — §4 has both test baselines and the warning against comparing totals.
3. **`PROGRESS_LOG.md`** — the second 2026-07-31 entry (Linux verification).
4. **`workstreams/merge-backlog.md`** — Q4 explains precisely why step 6 is blocked.
5. **Wrapper `CLAUDE.md`** — the Linux build section. The six-patch table is **retired**; needing to
   patch anything now is a new finding.

## Known traps

- **`RandomForestBailOut` is red on purpose** and `4DContinuousRendering` takes ~35 s on purpose.
  Neither was weakened to get green — see the test-as-ratchet rule. Do not "fix" either by reverting
  `4e1baa2a` or `97285971`.
- **A GUI test that passes suspiciously fast is not passing.** Until `97285971` a missing script
  exited 0. If a duration drops sharply, check the script still loads.
- **Do not compare `ctest` totals across platforms or dates.** Linux 30/33 (2026-07-31) and Linux
  30/33 (2026-07-17) match by coincidence — the older run counted a test that executed nothing.
  Linux 30 vs macOS 31 is platform-specific debt, not a regression. Compare failure *sets*.
- **`ctest | tail` returns *tail's* exit status.** It has already reported success over failing tests
  here. Redirect to a file; never pipe a command whose exit code you need.
- **Build in `build-v460/`, not `build-release/`** — the latter is still cached against VTK 9.3.0
  from July. Reconfiguring a stale cache across a dependency major version is the failure class that
  has bitten this repo twice.
- **`build_itk()` in `scripts/build-deps.sh` still has the clone-skip bug** that `build_vtk()` had:
  it skips the clone whenever `lib/itk/src/.git` exists, without checking the tag. Do not bump
  `ITK_VERSION` until it is fixed the same way.
- **`config.local.sh` is gitignored and per-machine.** The Linux box sets `VTK_INSTALL_PREFIX` to
  install into the shared `vtk-dev/installed`; macOS does not. Do not "sync" them.
- **Build FOREGROUND.** `nohup &` reports success instantly while the linker is still running.
  Confirm the binary mtime advanced before testing.
- **Never `pkill -f "<string>"` from your own shell** — the pattern matches the tool shell's own
  command line and kills it. Servers by port, GUIs by `setsid` + `kill -TERM -<pid>`.
- **`git branch -vv`'s `[origin/master: behind 1]` describes the LOCAL checkout, not the remote.**
  Verify with `git rev-list --count origin/master..upstream/master`.
- **Push submodules BEFORE bumping the wrapper pointer**, and run the `SUBMODULE_SYNC.md` §3
  reachability check with `git branch -r --contains` — **not** `git ls-remote | grep <sha>`, which
  lists only ref tips and reports healthy ancestor pointers as missing.
- **The memory-leak canary baseline in `itksnap/CLAUDE.md` is invalid** (≤600 leaks / ≤90 KB for
  `RandomForestBailOut`) — measured on a process that loaded no script. Re-baseline only after item
  15's follow-ups.

## How to work

Item 17 is a real fix to shared test infrastructure, so the bar is behavioural: a scripted widget
call must be *provably* on the main thread afterwards, and the fix must not paper over the failures
it exposes. Expect it to change test results — some currently-passing GUI tests may start failing
honestly. **That is a win, and it must be recorded rather than tuned away.** Re-measure both
baselines in `SPRINT_PLAN.md` §4 when it lands.

Run `/handoff` at the end rather than improvising it.
