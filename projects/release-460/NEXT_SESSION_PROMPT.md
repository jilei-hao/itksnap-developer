# RESUME — ITK-SNAP 4.6.0 · Re-baseline `RandomForestBailOut`, then close W1

## Current state (read this paragraph first)

**The GUI test harness is fixed and the suite can now be trusted for the first time this sprint.**
`itksnap:staging/v460` is pushed at **`5f2825e4`**, 21 commits ahead of `upstream/master`. Scripted
Qt access is marshalled to the GUI thread (W8 item 17, three commits), and the one production bug
that fix exposed is fixed too (W8 item 21). macOS is **32/34** — the suite gained a 34th test,
`HarnessThreadSafety` — and across three full runs today **`RandomForestBailOut` is the only failure
that appears every time**; the rest rotate between two known flakes. Both build paths were green as
of the previous session, but **Linux has not been re-run since the harness change**, which alters
timing on every GUI test. Wrapper `main` is pushed at `c430a7b`. The agentic API stays out of scope —
it lives on `sprint/caimi` for the October CAIMI demo.

## The single next goal

**Re-baseline `RandomForestBailOut` on macOS against a stock build, and settle the item 15 / 15d
contradiction.**

It still SEGFAULTs on macOS at `5f2825e4`. W8 item 15 claims that after `1d1fe7ea` it "no longer
segfaults but still fails". Those disagree, and last session deliberately did **not** resolve it —
doing it honestly needs a stock-build comparison and the build budget went to `EdgeAttraction`.
**The row in `SPRINT_PLAN.md` §4 is marked "not re-baselined" for exactly this reason. Do not read
it as changed by item 17; it is untested either way.**

Why this first, and why it is now cheap:

1. **It is the last untrusted number in the sprint.** Everything else in §4 has been measured on the
   fixed harness. This one has not, and it is the only 🔴 that is not a known flake.
2. **Item 17 was the stated blocker.** Item 15d's central inference — that the concurrent teardown is
   the script's "Cancel segmentation" racing the modal dialog *because the harness drove Qt from a
   worker thread* — is now testable. The harness is no longer a plausible alternative explanation.
3. **Item 15c is likely already resolved.** "Why the test never enters RF mode" was recorded as
   "likely a consequence of item 17". Check it first — it may cost one run.

Method that worked last session and should be repeated: **build the stock tree and measure it,
before attributing anything.** `git stash push -u`, rebuild (~1 min, only the harness files change),
run, `git stash pop`. Do not reason about a failure's cause from source alone.

After that, W1 step 6 is the next target — it needs Q4's two `cb6f692e` defects addressed, and it
now has a trustworthy harness to be tested on, which is what it was waiting for.

## What changed last session, and what it means

**Two findings invalidated the previous handoff's prescribed fix before any code was written.** They
are worth internalising because both were only visible by surveying the *scripts*, not the harness:

1. **Marshalling `SNAPTestQt`'s own slots would have fixed a minority of the call sites.** Scripts
   call widget methods and write widget properties **directly**, on objects `findChild` returns —
   48 × `.click()`, 17 × `.setSelected()`, 13 × `.setCurrentIndex()`, 44 property writes. None of
   those pass through `SNAPTestQt`.
2. **The worker thread is load-bearing and cannot be removed.** `openMainImage()` in
   `test_Library.js`, used by nearly every test, drives the modal `ImageIOWizard` while the GUI
   thread is blocked inside `QDialog::exec()` (`MainImageWindow.cxx:1884`). A main-thread script
   would be stuck inside the very modal loop it exists to dismiss.

The fix: scripts never see application objects. `findChild`/`findWidget` return a
**`TestObjectProxy`**; every member hops to the target's thread first. Reads block; actions and
property writes are posted (a scripted click can open a modal dialog, and waiting for one deadlocks
against the script that dismisses it), each followed by a round-trip barrier. **No test script
changed.**

**W8 item 21, and the reason it matters more than its size.** `QDoubleSliderWithEditor` declares
`Q_PROPERTY(double value … NOTIFY valueChanged)` but `setValue()` never emitted it. Its only listener
is the coupling system, so a coupled model silently kept its old value on any programmatic write.
`EdgeAttraction` had been passing **because of** the item-17 bug: the old off-thread write made the
spinbox's relay a *queued cross-thread* call, delivered after the suppression flag had been reset, so
the guard was skipped and the signal went out. Fixing the thread bug made the connection direct and
the notification stopped.

Take the lesson generally: **a test that passed on the old harness is not evidence of correct
behaviour.** If another test goes red on a future harness-adjacent change, check whether it was
passing for a real reason before assuming a regression.

## Files to read first (in order)

1. **`workstreams/bugfixes.md`** — items 15, 15b, 15c, 15d are the goal; 17 and 21 are the context
   for why 15d is now testable.
2. **`SPRINT_PLAN.md`** §4 — the current macOS baseline and the warning on the `RandomForestBailOut`
   row.
3. **`PROGRESS_LOG.md`** — the second 2026-07-31 entry.
4. **`itksnap/Testing/GUI/Qt/SNAPTestQt.h`** — the `TestObjectProxy` class comment states the whole
   contract in one place.
5. **`workstreams/merge-backlog.md`** — Q4, for W1 step 6 afterwards.

## Known traps

- **Adding a scripted widget call may need a proxy member.** Scripts can only reach what
  `TestObjectProxy` declares; anything else is a JS `TypeError`. That is deliberate — it is what
  stops off-thread access creeping back. Add the member, do not unwrap the widget.
- **`TestObjectProxy::target()` aborts off the GUI thread.** If a run dies with `'…::target' ran on
  a worker thread`, a marshalling hop was lost — that is the assertion working, not a flake.
- **A GUI test that passes suspiciously fast is not passing** (item 13). `HarnessThreadSafety`
  legitimately takes ~1.8 s: it has no blank lines, and blank lines are what `readScript` turns into
  `engine.sleep(500)`.
- **Register a new test script in BOTH `TestingScripts.qrc` and `GUI_TESTS`.** Missing either is how
  items 1 and 14 hid for years.
- **Do not compare `ctest` totals across platforms or dates — compare failure *sets*.** The suite is
  34 tests now, not 33. The 2026-07-30 macOS figure (32/33) is superseded and the sprint's two
  records of it disagreed.
- **`RemoteImageLoadTest_*` fail only when the three run back-to-back**; each passes standalone at
  the same sub-second duration. Not a timeout — shared cache state or rate limiting. W8 item 3/3b.
- **`ctest | tail` returns *tail's* exit status.** Redirect to a file; never pipe a command whose
  exit code you need.
- **Use an absolute `--testdir`** when running `ITK-SNAP --test` by hand. A relative path silently
  produces a wrong-looking failure that reads like a regression. `--test` also accepts a path to a
  scratch `.js` file, which is the fastest way to get a diagnostic.
- **Build in `build-release/` on macOS** — it is current (VTK 9.5.2). The "use `build-v460/`" trap in
  the previous handoff was Linux-specific; that tree does not exist on macOS.
- **Build FOREGROUND.** `nohup &` reports success instantly while the linker is still running.
- **Never `pkill -f "<string>"` from your own shell** — the pattern matches the tool shell's own
  command line and kills it.
- **`git branch -vv`'s `[origin/master: behind 1]` describes the LOCAL checkout, not the remote.**
- **Push submodules BEFORE bumping the wrapper pointer**, and run the `SUBMODULE_SYNC.md` §3
  reachability check with `git branch -r --contains` — **not** `git ls-remote | grep <sha>`.
- **The memory-leak canary baseline in `itksnap/CLAUDE.md` is invalid** (item 16) and is now doubly
  stale: the harness allocates a `TestObjectProxy` per wrapped object. They are parented to
  `m_ProxyOwner` and freed in `~SNAPTestQt`, so they should not leak — but re-measure rather than
  assume when item 16 is picked up.
- **`config.local.sh` is gitignored and per-machine.** Do not "sync" macOS and Linux.

## How to work

The bar last session was behavioural, and it should stay there: the new test was verified by
**breaking the code and watching it fail**, then restoring. Per item 13's lesson, a test that has not
been seen to fail is not a test. Expect the same standard for whatever `RandomForestBailOut` turns
out to be — and if it is fixed, the fix needs a test that fails without it.

Run `/handoff` at the end rather than improvising it.
