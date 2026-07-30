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
