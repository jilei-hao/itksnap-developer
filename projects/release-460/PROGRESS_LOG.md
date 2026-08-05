# PROGRESS_LOG — ITK-SNAP 4.6.0

Append-only. One dated entry per session, newest last. Never rewrite an earlier entry.

---

## 2026-07-30 — Sprint opened; release surveyed

**Goal:** stand up `projects/release-460/` and establish what 4.6.0 actually contains.

### Done

- Created `projects/release-460/` with the metronome three files, plus `change_tracking.md` and
  `workstreams/` (8 specs + a README explaining the structure).
- Created `itksnap:staging/v460` from `upstream/master` @ `679ba76a`. **Local only, not pushed.**
  Upstream tracking was auto-set to `upstream/master` on creation and was **unset immediately** — a
  `git push` from that branch would otherwise have targeted `pyushkevich/itksnap`.
- Fetched `upstream` and `origin` for `itksnap`, plus `itksnap-dls`, `convert-mesh`, `segflow4d`.

### Findings

- **Trunk is already 4.6.0-alpha.1.** `f2bf343a` (2026-05-04) bumped the minor; `28f4ee45` (06-11)
  bumped to alpha.1. Baseline for the changelog is `20f63186` (v4.4.0, 2025-09-08); **101 commits,
  83 non-merge** since.
- **The 4.6 headline is remote/URL image I/O** — ~13 feature commits Apr 27 → May 13 covering
  `scp://`, `sftp://`, HTTP(S), Flywheel `fw://`, a persistent cache with conditional GET, an SSH
  connection pool, and Windows single-instance URL forwarding. Second largest is SAM2 (`2154b1bb`).
- **`sprint/caimi` decomposes as a clean prefix:** `feature/cardiac-io` (12) → `ad727107` Linux/GCC
  (1) → 6 agentic commits. The first 13 can be taken without touching the agentic work. This is the
  answer to "what in agentic-api is not agentic".
- **The Linux/GCC patches are still required.** Re-checked against `upstream/master` today:
  `CMake/standalone.cmake:72` still pins VTK 9.3.1; `CMakeLists.txt:1298` `qt_add_translations` and
  `:1663/:1723/:1813` `qt_generate_deploy_script` are still unguarded.
- **`test/dls_sam2` is not superseded.** Its async-DLS commits (`cb6f692e`, `ea86df0d`, 03-18) sit on
  top of the merged SAM2 commit `2154b1bb` (03-11), so they are genuinely new work — 2 of its 4
  commits are worth taking.
- **The itksnap-dls refactor is largely already written.** `feature/agentic-api` is +6/−0 vs `main`
  and carries the module split, propagation, TotalSegmentator (`bbaac51`), and a test suite:
  21 files, +1333/−361. W3 is a promotion problem, not an implementation problem. The other three
  DLS branches are strict subsets of it.
- **Issue #229 is a bug, not a feature** — 3D mesh loses correspondence with image space under free
  rotation. Open since 2026-04-24, no comments. Recorded as such so it survives any scope cut.
- **No governance baseline exists.** No `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, governance doc,
  `CODEOWNERS`, or root `LICENSE` on `upstream/master`. W2 is entirely net-new.

### Decisions

1. **One sprint directory, one file per workstream** — not eight sub-projects. Metronome's three-file
   pattern is scoped to a sprint, and eight `NEXT_SESSION_PROMPT.md` files would mean seven stale
   ignition keys plus a "which sprint?" prompt at every `/handoff`. Rationale and the promotion rule
   are in `workstreams/README.md`. W3 and W7 are the plausible future promotions.
2. **Everything lives in `SPRINT_PLAN.md`** — the metronome name. This reversed a first attempt that
   split living state into a second file, `sprint_planning.md`, on the reasoning that branch
   positions change every session while metronome keeps `SPRINT_PLAN.md` stable. Jilei pushed back:
   two files one character apart is a discoverability problem that outweighs the discipline, and the
   second file had drifted into duplicating the workstream table anyway. Resolution: `SPRINT_PLAN.md`
   §2 is a **dated snapshot** — re-verified, not re-planned, with the refresh command in §7 — and the
   per-commit ship/hold decisions moved into `workstreams/merge-backlog.md` (D1–D4), which owns them.
   Lesson: when a second file is needed to hold what the convention's file "shouldn't" hold, the
   content is usually in the wrong place, not the convention.
3. **`staging/v460` is cut from `upstream/master`.** (An earlier note here said `origin/master` was
   1 commit behind — **that was wrong**, see the correction below.)
4. **The agentic API is out of scope.** `sprint/caimi` stays alive and gets rebased on `staging/v460`
   at each beta so the October CAIMI demo builds on release code.

---

## 2026-07-30 (cont.) — W1 executed: merge, portability, and a test suite that was lying

Same session. `staging/v460` pushed to `origin`; wrapper project committed at `2c65c23`.

### Landed on `staging/v460` (4 commits, 15 ahead of base)

| Commit | What |
|---|---|
| `594b4033` | Merge `feature/cardiac-io` (D1) — clean, no conflicts. macOS arm64 builds **212/212**, no warnings in any cardiac-io file. |
| `e2f19b56` | Linux/GCC portability (D2) — cherry-picked `ad727107` **minus** its VTK floor line. |
| `97285971` | `4DContinuousRenderingD` typo **and** the silent-pass bug that hid it. |
| `4e1baa2a` | Register `test_RandomForestBailOut.js` in the `.qrc`. |

### Three of four blockers dissolved — two were my own errors

- **Q1 (FormatVersion): premise was wrong.** It is scoped to the `TimePointProperties` folder, not the
  workspace, and *neither* reader validates it — both read it into an unused local
  (`TimePointProperties.cxx:118`; upstream's line 64 identical). `SNAP_VERSION_LAST_COMPATIBLE_RELEASE_DATE`
  is **dead code**: set at `CMakeLists.txt:105`, referenced nowhere. Real exposure is narrower —
  `SaveProjectToRegistry` calls `preg.Clear()` (`IRISApplication.cxx:2283`), so an old build that
  re-saves silently strips the cardiac keys.
- **Q3 (jsoncpp): false alarm.** Already vendored at `Common/JSon/` on `upstream/master`, identical
  CMakeLists lines before and after; the branch touched neither. No new dependency.
- **Q2 (VTK): not a contradiction.** `FIND_PACKAGE(VTK 9.3.1)` is a *minimum* and VTK's config-version
  is compatible-if-newer, so CI at 9.5.2 satisfies it. I had rated this "High risk" — **corrected**.
  The real issue is that nothing exercises the floor. Still Jilei's call.
- **Q4 (undo under async DLS): still open**, and now more pointed — `itksnap/CLAUDE.md` documents four
  unfixed DLS races including a use-after-free, and `cb6f692e` adds another `QtConcurrent` path there.

### The test suite was reporting false greens

Chasing why `4DContinuousRenderingD` *passed* on macOS in 0.98 s while failing on Linux:

- `TestWorker::readScript` called `application_exit(NO_SUCH_TEST)` and **fell through** —
  `application_exit` only *queues* a quit (`QMetaObject::invokeMethod`, `Qt::QueuedConnection`).
  Execution continued past the failed `QFile::open()`, read an empty script off the closed file, and
  `source()` evaluated `""`. An empty program is not a JS error, so it took the success branch and
  queued `SUCCESS`, which landed after and overrode the failure. Exit 0 → ctest `Passed`.
  **All 21 GUI tests were exposed.** Verified fixed: `--test ThisTestDoesNotExist` now exits 3, was 0.
- `test_RandomForestBailOut.js` was the only on-disk script never added to the `.qrc` — since
  `062ba382`, **2018-09-26**. It has never executed.
- With it actually running, **it segfaults** at "Cancel segmentation" — the very scenario `062ba382`
  was written to guard. `EXC_BAD_ACCESS` at `0xfffffffffffffff0`: `__dynamic_cast` ←
  `LayerInspectorRowDelegate::onModelUpdate` ← `LatentITKEventNotifierHelper::dispatchEvent` ←
  `::onQueuedEvent`. Cancel tears down the model while a queued ITK event is still in the Qt loop.
- Consequence: **the memory-leak canary baseline in `itksnap/CLAUDE.md` is invalid** — 
  `RandomForestBailOut`'s ≤600 leaks / ≤90 KB was measured on a process that loaded nothing.

### Tests

macOS arm64 on `staging/v460`: **32/33**, one real failure (`RandomForestBailOut`, the segfault
above). `RemoteImageLoadTest_WorkspaceWithMesh` is flaky by construction — it asserts exact equality
on an approximate tdigest quantile; measured over 4 runs on byte-identical inputs
(`shasum 6437d829…` both sides): `45.065006/45.000507`, `45.080894/45.073586`, pass,
`45.000000/45.066990`. Neither pre-existing failure is attributable to the merge.

Red at handoff, recorded as stated debt per the test-as-ratchet rule: `RandomForestBailOut`. It was
**not** weakened or skipped to get green.

### Process note

`ctest | tail` returns *tail's* exit status. That reported success over two failing tests and I
briefly believed it. Stopped piping; capture real exit codes.

### Open — needs Jilei

- **Q2, the VTK floor** — raise to 9.5.2 (Linux box must upgrade), keep 9.3.1 and add a CI job at the
  floor, or lower to 9.3.0. Affects your Linux box, so it is not mine to decide.
- **W8 item 15, the segfault** — chase it now, or file it and continue W1?
- **Q4** — the undo test for `cb6f692e`, the last thing blocking W1 step 6.
- Whether the wrapper commit should be pushed, and whether `.gitmodules`/`SUBMODULE_SYNC.md` should
  move `itksnap` from `sprint/caimi` to `staging/v460` now that the release is the active work.

### Not done

Wrapper is committed but **not pushed**. Linux build and test run for `staging/v460` **not done** —
`e2f19b56` targets Linux/GCC and has only been verified on clang. W1 steps 6–8 remain.

---

## 2026-07-31 — VTK 9.5.2 on macOS; `staging/v460` pushed

Jilei's four decisions from the previous entry: raise VTK to 9.5.2, chase the segfault now, write
the undo test, don't push yet. All four handled; the last was reversed at the end of the session on
his instruction ("push staging/v460, I'll test on my linux box").

### Landed

| Commit | Repo | What |
|---|---|---|
| `7cc60053` | itksnap | VTK floor → 9.5.2 (Q2) |
| `1d1fe7ea` | itksnap | Null-engine segfault fix (W8 item 15) |
| `4e1baa2a` | itksnap | Register `test_RandomForestBailOut.js` in the `.qrc` |
| `97285971` | itksnap | GUI tests silently passing with a missing script |
| `4bda8dc` | wrapper | `build-deps.sh` tag-checkout fix + macOS VTK 9.5.2 |

`staging/v460` **pushed** to `origin` at `7cc60053`, 18 commits ahead of `upstream/master`.
Wrapper `main` has **4 unpushed commits** (`2c65c23`, `2a6bea1`, `8a84392`, `4bda8dc`).

### VTK 9.5.2

- **`9.5.3` does not exist.** The 9.5 series ends at 9.5.2; zero refs match 9.5.3 in Kitware/VTK.
  Built 9.5.2 — it is upstream CI's version and the floor set in `7cc60053`. 9.6.2 is the newest
  stable if we ever want to move ahead of CI.
- Built via `scripts/build-deps.sh --skip-itk --skip-qt` against Homebrew Qt 6.10.2, AppleClang 21,
  deployment target 12.6. 0 compile errors; `RenderingExternal` present.
- **9.3.1 retained as a fallback.** VTK versions its libs, headers and cmake packages, so
  `install/lib/cmake/vtk-9.3` and `…/vtk-9.5` coexist in one prefix; `VTK_DIR` selects. Reverting is
  a one-line change plus reconfigure — no VTK rebuild.
- ITK-SNAP: configures against the new floor, builds 446 targets with 0 errors, links
  `libvtk*-9.5.1.dylib`.

### Found: `build-deps.sh` would have installed the wrong version silently

`build_vtk()` skipped the clone whenever `lib/vtk/src/.git` existed, without checking the tag.
Bumping `VTK_VERSION` would have rebuilt the 9.3.1 source and installed it as `vtk-9.5` — wrong in a
way that looks right to every consumer, because the directory name would have lied. Fixed to check
out the requested tag, with a post-condition that aborts on a mismatch. Build trees are now
per-version. **`build_itk()` has the identical shape and the same latent bug; left alone** rather
than changing ITK's build as a side effect of a VTK upgrade.

### Corrections to my own earlier claims

1. **The segfault was not a use-after-free.** I read the `.ips` crash report as a dangling
   `dynamic_cast` on the queued ITK→Qt event path. Under lldb the real fault is a plain null
   dereference of `m_ClassificationEngine` (`x0 == 0` at `SnakeWizardModel.cxx:1813`), and
   breakpoints proved `EnterRandomForestPreprocessingMode` is **never called** during the test. I
   should not have asserted a mechanism from a symbolized crash report.
2. **`ctest | tail` returns tail's exit status.** It reported success over two failing tests and I
   briefly believed it. Stopped piping.
3. Prior entry's `origin/master`-is-behind claim was already corrected; `git branch -vv`'s
   `[origin/master: behind 1]` describes the local checkout.

### Q4 answered: do not cherry-pick `cb6f692e` as-is

Two defects in the commit itself — the undo gap is real (the `catch` path calls `on_complete(false)`
after `UpdateSegmentation` may already have mutated the label image, so the change cannot be undone),
and it reproduces the documented `QtConcurrent` use-after-free (parentless watcher, `[=]` captures
`this`, context object is the watcher; `AbstractModel` is an `itk::Object` so it cannot be the
context). **No test was written, deliberately** — the only harness available is the one W8 item 17
describes, and async behaviour tested on a thread-unsafe harness is not evidence.

### The most consequential find: W8 item 17

`class TestWorker : public QThread` runs test scripts inside `run()`, so **every scripted GUI call
executes off the main thread**. That is unsupported by Qt, affects all 21 GUI tests, and is the most
likely source of the suite's run-to-run instability. Surfaced only because fixing the false-green
made `RandomForestBailOut` actually run.

### Tests

macOS arm64, `staging/v460` @ `7cc60053`, against VTK 9.5.2: **31/33**. Both failures pre-existing,
neither attributable to the merge or the VTK upgrade:

- `RemoteImageLoadTest_WorkspaceWithMesh` — asserts exact equality on an approximate tdigest
  quantile; ~1 pass in 4.
- `RandomForestBailOut` — aborts on W8 item 17.

Every VTK-heavy test passes: VolumeRendering, MeshImport, MeshWorkspace, SegmentationMesh,
4DContinuousRendering, 4DReplayWithMeshUpdate, 4DToMC, MCTo4D, DeformationGrid. **No VTK regressions.**

### Not done

Linux: untouched. The box is still on VTK 9.3.0 and cannot configure `staging/v460`. `e2f19b56` —
the Linux/GCC portability fixes — has only ever been compiled with clang. W1 steps 6–8 remain, and
step 6 is blocked behind the two `cb6f692e` defects above, not behind a missing test.

---

## 2026-07-31 (cont.) — Linux/GCC verification of `staging/v460`

**Goal:** the one the previous handoff set — get `staging/v460` building and testing on Linux/GCC
**with no local patches**, and produce a Linux number that can be trusted.

### The headline: it builds clean, with nothing patched by hand

`766/766` targets, **0 errors**, `all` target (so the CLI tools and `SSHTunnelTest` are covered —
two of the portability fixes only bite there). `git diff HEAD` on `itksnap` is **empty**: no local
edits of any kind. The binary links `libvtk*-9.5.so` exclusively, with **zero** 9.3 leakage.

This is the first time the Linux build has worked from a clean checkout. **`e2f19b56` is confirmed
sufficient** and the six-patch table in the wrapper `CLAUDE.md` is now history rather than
instructions. The sixth patch — the VTK floor relax — stayed correctly dropped: 9.5.2 is installed
instead, as Q2 decided.

### Tests: 30/33, no new failures

Xvfb + llvmpipe, VTK 9.5.2. Full table in [SPRINT_PLAN.md](SPRINT_PLAN.md) §4.

- `RemoteImageLoadTest_Cache` — Linux-specific, reproduces July's failure exactly: the download
  reports `done`, then `CacheMetadata.xml` is not created. W8 item 3.
- `RandomForestBailOut` — SEGFAULT. **Not the same crash `1d1fe7ea` fixed** — see below.
- `4DReplayWithMeshUpdate` — the known llvmpipe timing flake.

**The canary passed the honest way: `4DContinuousRendering` took 36.5 s**, matching macOS's ~35 s.
It genuinely runs on Linux; the false-green fix (`97285971`) holds on both platforms.

Linux's 30/33 and macOS's 31/33 are **not** comparable as totals — the failure *sets* differ by
platform, and the tdigest flake landed on opposite sides. Recorded that caveat in §4 rather than
leaving two numbers to be misread later.

### The find that changes an earlier conclusion (W8 item 15d)

`RandomForestBailOut` still segfaults here, and the live gdb backtrace shows a mechanism macOS
**cannot reach**:

```
on_btnClassifyTrain_clicked [.cold]  → Classify/Train threw
  ReportNonLethalException
    QDialog::exec()                  → modal dialog re-enters the event loop
      … sendPostedEvents
        LatentITKEventNotifierHelper::onQueuedEvent → dispatchEvent(EventBucket)
          LayerInspectorRowDelegate::onModelUpdate
            UpdateOverlaysMenu()
              __dynamic_cast          → SIGSEGV
```

The faulting cast is `LayerInspectorRowDelegate.cxx:551`,
`dynamic_cast<ImageWrapperBase*>(m_Model->GetLayer())`. **The error dialog is the trigger**:
reporting a non-lethal exception opens a nested event loop, which delivers a queued ITK→Qt event to
a delegate whose layer is being torn down.

**This vindicates the reading that the previous session retracted.** Item 15 first blamed a
use-after-free in `LayerInspectorRowDelegate::onModelUpdate` on the queued-event path, then withdrew
it in favour of a null `m_ClassificationEngine`. Both are true, and the retraction was right *for
macOS*: there the run never enters RF mode (item 15c), so this path is unreachable and the null
deref is all you can see. On Linux the script gets through "Entering classification mode", paints
three labels, performs classification and cancels — and then dies on the path originally described.
`1d1fe7ea` fixed a real bug; it did not fix this one.

Filed as W8 item 15d, to be promoted alongside item 17. What is **not** yet proven: that the
concurrent teardown is the script's "Cancel segmentation" racing the modal dialog via the
worker-thread harness. That is the obvious candidate and it is labelled as inference in the item.

Method note: this was taken from a live gdb session, not a symbolized crash report — deliberately,
given that a `.ips` misread is exactly what produced the retraction being revisited here.

### Also found by GCC (all pre-existing upstream, none from the merge)

- **W8 item 18** — five `-Wreturn-type` sites: exhaustive enum `switch`es with no fallback `return`.
  Clang does not warn, so macOS never showed them. Verified untouched by `staging/v460`.
- **W8 item 19** — `RESTClient.cxx` uses curl APIs deprecated since 7.55/7.56 (47 warnings),
  including `curl_formadd`, which is slated for removal. Same subsystem as the headline feature.
- **W8 item 20** — `TestLargeImageCheck` prints "only 0.0 GB is currently available" on a box with
  free RAM. The test still passes, so it hides; the number reaches users in an error dialog.

### Two blockers in the wrapper's own tooling

Neither was in the handoff; both would have stopped the session cold.

1. **`build-deps.sh` could not find apt Qt on any Linux box.** `qt_find_root` knows three Qt
   layouts, none of them Debian/Ubuntu multiarch (`lib/<triplet>/cmake/Qt6`). `QT_PREFIX=/usr`
   resolved as invalid and `build_vtk` aborted with "Qt not found" — i.e. the script could not build
   VTK using the distro Qt, which is how this project builds on Linux. Added a multiarch branch.
2. **The VTK install prefix was hardcoded** to `lib/vtk/install`. This box keeps its dependencies in
   `vtk-dev/installed`, which is already on `LD_LIBRARY_PATH` and shared with the other projects
   here. Made it overridable via `VTK_INSTALL_PREFIX` in `config.local.sh`; the default is unchanged,
   so macOS is unaffected.

The handoff's trap 1 resolved itself — the fixed `build-deps.sh` (`4bda8dc`) was unpushed last
session and arrived with the wrapper pull, so the silent wrong-version failure never had a chance to
fire. VTK 9.5.2 built and installed with 0 errors; `RenderingExternal` verified present in the cache
**and** as `libvtkRenderingExternal-9.5.so`, rather than assumed. 9.3.0 retained as a fallback.

Built into a fresh `build-v460/` rather than reusing `build-release/`, whose cache still pointed at
VTK 9.3.0 — reusing a stale cache across a dependency major-version change is the exact failure
class that has bitten this project twice (stale ITK, and the `build-deps.sh` bug above).

### Not done

W1 steps 6–8 untouched: step 6 remains blocked on Q4's two `cb6f692e` defects. The `.gitmodules`
question raised in the last handoff was already settled in `50d7261` (wrapper now tracks
`staging/v460`); `SUBMODULE_SYNC.md` §1 and `.gitmodules` agree.

**Nothing was committed inside `itksnap`** — this was a verification session and the branch needed
no source changes, which is itself the result. `staging/v460` stays at `7cc60053` on both remotes,
so no submodule pointer moved and the `SUBMODULE_SYNC.md` §3 reachability check was not needed.
The wrapper checkpoint carries `build-deps.sh`, the sprint docs, `CLAUDE.md` and a `.gitignore`
entry for `build-v460/` (946 MB, and the ignore list names build dirs individually, so `git add -A`
would have tried to commit it). `config.local.sh` is gitignored and stays machine-local.

**Test result at checkpoint time: 30/33** — the run above, on this exact tree. Not re-run after the
documentation edits, which cannot affect it; `itksnap` is byte-identical to the tested state.

---

## 2026-07-31 (second session, macOS) — W8 item 17 fixed; it exposed item 21

**Goal:** fix the GUI test harness driving Qt from a worker thread. Done, plus the defect it
uncovered. `staging/v460` `7cc60053` → `5f2825e4` (3 commits).

### Two findings that changed the plan before any code was written

The handoff's prescribed fix — "marshal scripted widget calls to the main thread
(`Qt::BlockingQueuedConnection`)" — was right about the bug and wrong about the shape of the fix.

1. **Marshalling `SNAPTestQt`'s own slots is not sufficient.** Scripts call widget methods and write
   widget properties **directly**, on objects returned by `findChild`: 48 × `.click()`,
   17 × `.setSelected()`, 13 × `.setCurrentIndex()`, 5 × `.setCurrentWidget()`, 6 × `.toggle()`, and
   44 property writes (`.value =`, `.text =`, …). None of these pass through `SNAPTestQt`. Wrapping
   its slots would have fixed a minority of the call sites and left the class of bug intact.

2. **The worker thread cannot be removed** — the obvious "just run the script on the GUI thread"
   fix. `openMainImage()` in `test_Library.js`, used by nearly every test, drives the modal
   `ImageIOWizard` *while the GUI thread is blocked inside `QDialog::exec()`*
   (`MainImageWindow.cxx:1884`). A main-thread script would be stuck inside the very modal loop it
   exists to dismiss. The worker thread is load-bearing, not an accident.

### What was built

Scripts no longer see application objects at all. `findChild`/`findWidget` return a
**`TestObjectProxy`**; every member hops to the target's thread first. Reads block for an answer;
actions and property writes are posted — a scripted click can open a modal dialog, and waiting for
one deadlocks against the script that dismisses it — each followed by a round-trip barrier so the
step, including the queued ITK→Qt model updates it triggers, has landed before the next is sent.

**No test script changed.** The proxy carries the exact members the 22 scripts use.

Two things keep it fixed: the proxy is a curated surface, so reaching for an unwrapped widget method
is a JS `TypeError`, not a silent off-thread call; and `TestObjectProxy::target()` — the single point
where application objects become reachable — aborts unless it is on the GUI thread.

`b3cf79d3` first put that assertion *inside* each marshalled block, which only proved that a hop
that still existed had run. Deleting the hop would have deleted its assertion too. `5f2825e4` moved
it to the dereference point, so any unmarshalled access aborts however the marshalling was lost.

### Verified, not assumed

- **The ratchet was tested by breaking it.** Removing the hop from `findChild` and re-running:
  process aborts with `'TestObjectProxy::target' ran on a worker thread instead of the GUI thread`,
  and `HarnessThreadSafety` fails. Restored, rebuilt, green. Per item 13's lesson, a new test that
  has not been seen to fail is not a test.
- `test_HarnessThreadSafety.js` is registered in **both** `TestingScripts.qrc` and `GUI_TESTS` —
  the two ways items 1 and 14 went unnoticed for years.

### W8 item 21 — the bug item 17 exposed, and why it had been invisible

`EdgeAttraction` went red on the fixed harness. It was not flakiness and not a harness bug:

`QDoubleSliderWithEditor` declares `Q_PROPERTY(double value … NOTIFY valueChanged)` but
`setValue()` never emits it — it raises `m_IgnoreSpinnerEvent` around `ui->spinbox->setValue()`, so
the relay that would emit returns early. The widget's only listener is the coupling system, so a
coupled model silently kept its old value. The script sets the bubble radius to 2; the level set
came out at −4, the default.

**Its previous pass was the item-17 bug in action.** The write used to run on the script's worker
thread, so the spinbox's `valueChanged` reached the relay as a *queued cross-thread* call —
delivered after `m_IgnoreSpinnerEvent` had been reset to `false`. The guard was skipped by the race,
the signal went out, and the model updated. Marshalling the write onto the GUI thread made the
connection direct, the guard began working as written, and the notification stopped. Fixed in
`092022fb`; emitting is safe because the coupling guards the model→widget direction with
`m_Updating`. `EdgeAttraction` is now its regression test, and passes at 34.6 s — the stock timing,
versus 24 s when the bubble was wrong.

Method note: `EdgeAttraction` was **not** filed as an honest new failure on inspection. A stock
build of the same tree was made and run twice (34.2 s, 33.2 s, both green) to establish that the
change caused it, then a diagnostic script read the radius back (`before = 4`, `after write = 2`,
level set still −4) to locate the break between widget and model. Only then was the source read.

### Also found

- **`RemoteImageLoadTest_{SingleImage,WorkspaceWithMesh}` fail only in a back-to-back run.** Each
  passes standalone at the same sub-second duration, so it is not a timeout — shared cache state or
  server-side rate limiting. Standalone CLI executables; the GUI harness cannot reach them. Folds
  into W8 item 3/3b, which owns this test family.
- **`printChildren(parent, className)` passed a dangling pointer** — the `QByteArray` backing it went
  out of scope with the `if`-block. Fixed in passing.
- **Harness teardown could delete the script engine, or a running `QThread`, out from under a live
  script.** `m_Worker` is now a `QPointer` (it deletes itself on `finished()`), the destructor waits
  briefly, and marshalled calls stop waiting once `application_exit()` has been queued.

### Not done

- **`RandomForestBailOut` was not re-baselined.** It still SEGFAULTs on macOS. Item 15 claims that
  after `1d1fe7ea` it "no longer segfaults but still fails", which disagrees; that was not resolved,
  because doing it honestly needs a stock-build comparison and the session's build budget went to
  `EdgeAttraction`. **Do not record this as changed by item 17 — it is untested either way.**
- Items 15b/15c/15d untouched. 15c ("why the test never enters RF mode") was expected to be a
  consequence of item 17 and should be re-checked first now that the harness is fixed.
- W1 step 6 still blocked on Q4's two `cb6f692e` defects.
- **Linux not re-run.** The harness change alters timing on every GUI test; the Linux figures in
  §4 predate it.

### Handoff checkpoint

Full suite re-run on the final tree (`5f2825e4`) during handoff, because the earlier 31/34 had been
measured at `092022fb` — before the assertion was moved in `5f2825e4`. **32/34**, failing
`RemoteImageLoadTest_WorkspaceWithMesh` and `RandomForestBailOut`. §4 corrected; the recorded figure
had been attributed to a commit it was not measured on.

Three full runs today, and the totals move because the flakes rotate — **`RandomForestBailOut` is
the only failure common to all three**, which is what makes it the next goal:

| Run | Commit | Result | Failure set |
|---|---|---|---|
| 1 | `b3cf79d3` | 30/33 | `RemoteImageLoadTest_SingleImage`, `EdgeAttraction`, `RandomForestBailOut` |
| 2 | `092022fb` | 31/34 | `RemoteImageLoadTest_SingleImage`, `4DReplayWithMeshUpdate`, `RandomForestBailOut` |
| 3 | `5f2825e4` | 32/34 | `RemoteImageLoadTest_WorkspaceWithMesh`, `RandomForestBailOut` |

`EdgeAttraction` red in run 1 is the item-21 story above, not a flake. The remote-test failure moves
between `SingleImage` and `WorkspaceWithMesh`, which supports shared state or rate limiting over a
defect in either test.

---

## 2026-08-05 — `RandomForestBailOut` re-baselined and fixed; a use-after-free of our own making

**Goal:** re-baseline `RandomForestBailOut` on macOS against a stock build and settle the
item 15 / 15d contradiction.

### Done

- **Re-baselined against a stock build first, as prescribed.** `staging/v460` @ `5f2825e4`, no local
  changes, macOS: `RandomForestBailOut` **SEGFAULTs every run** (exit 139, 3/3). W8 item 15's claim
  that it "no longer segfaults but still fails" was wrong; the row in `SPRINT_PLAN.md` §4 is now
  measured rather than assumed.
- **Root-caused and fixed it — `7ba0692e`, W8 item 15d.** A use-after-free of
  `AbstractLayerTableRowModel::m_Layer`, regressed by **`1712c6e7`** (our own March 2026 leak fix).
- **Fixed the regression the fix itself caused**, before committing: `MeshWorkspace` began
  segfaulting deterministically. Caught by running the full suite, not by inspection.
- **macOS full suite: 32/34**, and for the first time this sprint **every failure is a known flake**
  (`RemoteImageLoadTest_SingleImage`, `4DReplayWithMeshUpdate`).
- Filed two new items: **22** (the test paints nothing) and **23** (`findChild` fails silently).

### Findings

**1. Two bugs, one symptom — that is why items 15 and 15d disagreed.** `1d1fe7ea` fixed a real null
deref. With the harness repaired (item 17) the test gets *further* and hits a second, unrelated
crash. Both are true; neither statement was complete. **Item 15c is resolved by item 17**: the test
does now enter RF mode, proven by `TrainClassifier()` reaching a `throw` that is only reachable with
a non-null engine.

**2. The mechanism, and the inference it disproves.** Item 15d guessed the concurrent teardown was
the harness driving Qt from a worker thread. That is now fixed, and the click runs on the GUI
thread — so the guess was wrong. The real re-entrancy is the **modal error dialog**:
`ReportNonLethalException` → `QDialog::exec()` pumps posted events, so the script's queued "Cancel
segmentation" executes **inside** the nested loop and destroys the layers under the dialog. A queued
ITK event then reaches a delegate whose layer is gone. Proven by deleting the cancel click from a
copy of the script: no crash.

**3. The leak fix and the crash fix were in direct tension, and the leak fix won silently.**
`1712c6e7` changed `m_Layer` to a raw pointer to break a cycle with the wrapper's `m_UserDataMap`.
But invalidation was left in `OnUpdate()`, which only runs when a view calls `Update()` — so between
the layer's destructor and that call, every reader of `GetLayer()` held freed memory.
`LayerInspectorRowDelegate::GetLayer()` calls `Update()` first *for exactly this reason*;
`UpdateOverlaysMenu()` and `onModelUpdate()` read `m_Model->GetLayer()` directly and did not.
**This is the 2018 crash returning** — `062ba382` fixed it with a `SmartPtr` and added this very
test, which never ran until `4e1baa2a`. Fix: observe `DeleteEvent` directly and invalidate at once.
ITK fires it from `UnRegister()` while the object is still alive, and `itk::MemberCommand` holds a
raw back-pointer, so the leak fix is preserved.

**4. Nulling earlier is not free — it converts dangling reads into null reads.** Two sites had to be
repaired in the same commit, one of which the test suite caught and inspection had not:
`AbstractLayerTableRowModel::OnUpdate()` stopped matching its `DeleteEvent` branch (`m_Layer` is
already null, and `HasEvent(evt, NULL)` means *any* source), fell through to `UpdateRoleInfo()`, and
segfaulted `MeshWorkspace`; and `ApplyColorMap()` dereferenced `GetLayer()` unguarded. **Lesson: a
fix that changes when a pointer becomes null must be measured on the whole suite, not the one test
it targets.**

**5. The now-green test does not test what it was written to test (item 22).** Its three paintbrush
strokes are silent no-ops — `findChild(panel0,"sliceView")` matches nothing (the canvas is
`sliceViewCanvas`), so the key events go nowhere and the classifier trains on **0 samples**. The run
follows the "training threw → modal dialog → cancel" path instead. That path is what exposed item
15d, so the coverage is real and worth keeping — **do not just repoint the selector**, since making
training succeed would delete the very path that found the bug. Add a second test for the
trained-then-cancel case.

### Next

Confirm `RandomForestBailOut` on Linux — one run, not an investigation; the gdb stack recorded there
is the same crash. Then W1 step 6, which now has a trustworthy harness *and* a green suite to land on.
