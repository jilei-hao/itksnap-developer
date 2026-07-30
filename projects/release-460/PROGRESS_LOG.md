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
3. **`staging/v460` is cut from `upstream/master`, not `origin/master`** — `origin/master` is 1
   commit behind.
4. **The agentic API is out of scope.** `sprint/caimi` stays alive and gets rebased on `staging/v460`
   at each beta so the October CAIMI demo builds on release code.

### Open — needs Jilei

- The `feature/cardiac-io` ship/hold list (`workstreams/merge-backlog.md` D1). Recommendation is ship all 12,
  but **workspace `FormatVersion` 1→2→3** is a real compatibility break and needs an explicit call.
- The VTK floor: CI is on 9.5.2 (`c480b003`), `CMake/standalone.cmake` still requires 9.3.1.
- Whether `staging/v460` should be pushed to `origin` now.

### Not done

No code was written, nothing was pushed, nothing was committed. `git status` in the wrapper shows
`itksnap` with untracked content (`Submodules/greedy`) — pre-existing, unrelated.

### Tests

None run — no code changed. Baseline to beat is recorded in `SPRINT_PLAN.md`: 30/33 on Linux
headless as of 2026-07-17.
