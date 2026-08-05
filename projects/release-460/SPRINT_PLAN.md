# SPRINT_PLAN — ITK-SNAP 4.6.0 release

**Opened:** 2026-07-30 · **Project:** `projects/release-460/` · **Integration branch:** `staging/v460`

Per metronome convention this file holds **scope, goals, and done-criteria**. Only checkboxes change
mid-sprint — except §2, which is a dated snapshot that gets **re-verified, not re-planned**. The
journal is [PROGRESS_LOG.md](PROGRESS_LOG.md); merged history is [change_tracking.md](change_tracking.md);
per-workstream detail is in [workstreams/](workstreams/).

---

## 1. Goal

Ship **ITK-SNAP 4.6.0**: take the 4.6.0-alpha.1 trunk, land the eight workstreams in §3 through a
single integration branch, and deliver a release with notes, developer documentation, and a
governance baseline.

**Explicit non-goal: the agentic API / MCP prototype.** That is the October CAIMI demo
(`projects/agentic-api/`). Keep `sprint/caimi` alive and rebase it on `staging/v460` at each beta so
the demo builds on release code — but do not merge it, and do not merge `itksnap-mcp` at all.

---

## 2. State of the tree — verified 2026-07-30

> Re-verify with §7 and update in place. This is the one section that changes without being a
> re-plan; the numbers are observations, not commitments.

### Integration branch

| | |
|---|---|
| Branch | `staging/v460` (itksnap) |
| Base | `upstream/master` @ `679ba76a` |
| Purpose | Land each workstream, run integration tests, then one wholesale PR to `pyushkevich/itksnap:master` |
| Status | pushed; at `038fa32b`, **23 commits** ahead of base (2026-08-05) |

Nothing merges into `staging/v460` until its workstream row in §3 says the branch builds **and** its
tests pass. Rebase on `upstream/master` before each merge so the final PR stays a clean fast-forward
candidate.

### itksnap — unmerged branches

Counts are commits **not in `upstream/master`**.

| Branch | Ahead | Content | Disposition |
|---|---:|---|---|
| `feature/cardiac-io` | 12 | 4D cardiac CTA + echo phase/metadata I/O | W1 — [decision list](workstreams/merge-backlog.md#decision-list) |
| `sprint/caimi` | 19 | `feature/cardiac-io` (12) + Linux/GCC fix (1) + agentic prototype (6) | split — W1 takes the first 13 |
| `test/dls_sam2` | 4 | async DLS interactions, progress bar, submodule bump, Linux fix | W1 — take 2 of 4 |
| `bug/{4d-mesh-slice,large-image-oom,memory-leak,mesh-update-crash}` | 0 | merged | delete — W8 item 7 |
| `feature/{io-improvement,seq-nrrd-export,vti-io}` | 0 | merged | delete — W8 item 7 |
| `origin/master` | 0 | in sync with `upstream/master` @ `679ba76a` | nothing to do |

`sprint/caimi` decomposes as a clean prefix, so the release work can be taken without touching the
agentic work:

```
upstream/master (679ba76a)
  └─ 12 commits  feature/cardiac-io        4D cardiac I/O        → W1
       └─ 1 commit  ad727107               Linux/GCC build fixes → W1
            └─ 6 commits                   agentic-API prototype → HOLD (October demo)
                 d9f2329f  --agent-listen live command channel
                 560dcd2f  segmentation audit record (P2 core)
                 f1743f04  apply_box channel command + PaintRegionWithLabel
                 e1aa19d5  apply_seg_file
                 e06937f8  label naming/coloring over the agentic API
                 daeeb995  report the whole correction session
```

### Dependency repos

| Repo | Wrapper tracks | Head | Needed for | State |
|---|---|---|---|---|
| **itksnap-dls** | `feature/agentic-api` | `bbaac51` | W4, W5 | ⚠️ 4-branch tangle; the refactor is **already written** — [dls-refactor.md](workstreams/dls-refactor.md) |
| **segflow4d** | `main` | `ed143db` | W5 | Integrated into itksnap-dls at `7ecf586`; 4 unmerged side branches to triage |
| **convert-mesh** (`cmesh`) | `main` | `45482ca` | W7 | Reorganized under `src/cmesh/`; **no release tag**; not yet an itksnap submodule |
| **itksnap-mcp** | `main` | `1228618` | — | Agentic-API only; **not in 4.6.0** |
| **greedy_python** / **cmrep** / **FireANTs** | — | — | — | Not in scope |

---

## 3. Scope

### Workstreams

Branch column is authoritative for "where is this work". Tick the box when §4 is satisfied.

| | Workstream | Branch | Depends on | State |
|---|---|---|---|---|
| ☐ **W1** | [Merge the ready backlog](workstreams/merge-backlog.md) — 4D cardiac I/O, Linux/GCC portability, async DLS | `staging/v460` | — | Steps 1–5 done, Q1–Q3 answered. **Linux verified 2026-07-31** — builds with no local patches, 30/33, no new failures. Step 6 blocked on Q4's two `cb6f692e` defects |
| ☐ **W2** | [Developer docs & governance](workstreams/developer-docs.md) — `CONTRIBUTING`, `CODE_OF_CONDUCT`, governance, dev guide | none yet | — | Not started — net-new |
| ☐ **W3** | [itksnap-dls refactor](workstreams/dls-refactor.md) — promote modules + TotalSegmentator + segflow4d + tests to `main` | `itksnap-dls:feature/agentic-api` | segflow4d | **Largely written** — needs promotion |
| ☐ **W4** | [Auto-segmentation UI](workstreams/auto-seg-ui.md) | none yet | W3 | Not started |
| ☐ **W5** | [Propagation UI](workstreams/propagation-ui.md) | none yet | W3 | Not started |
| ☐ **W6** | [Free-rotation 2D/3D sync](workstreams/free-rotation-sync.md) — [#229](https://github.com/pyushkevich/itksnap/issues/229) | none yet | — | Not started — this is a **bug** |
| ☐ **W7** | [cmesh integration](workstreams/cmesh-integration.md) — tag, submodule, refactor `Logic/Mesh/` | `convert-mesh:main` | cmesh tag | Library exists; itksnap side not started |
| ☐ **W8** | [Bugfixes & small improvements](workstreams/bugfixes.md) | rolling | — | Rolling |

### Release engineering

- [x] `staging/v460` created and pushed (2026-07-30) — keep it rebased on `upstream/master`
- [ ] Version bumped from `4.6.0-alpha.1` to a beta, then to `4.6.0`
- [x] **VTK floor decided** — raised to **9.5.2** (`7cc60053`), matching upstream CI. **Both build
      paths upgraded and verified 2026-07-31**: macOS arm64 (31/33) and Linux/GCC (30/33), each
      building clean with no regressions attributable to the floor change.
- [ ] **Workspace `FormatVersion` decision** — cardiac I/O bumps it 1→3; decide whether
      `SNAP_VERSION_LAST_COMPATIBLE_RELEASE_DATE` moves or the reader degrades
- [ ] `ReleaseNotes.md` gains a 4.6 section, built from [change_tracking.md](change_tracking.md)
- [ ] Merged branches deleted (W8 item 7)
- [ ] Wholesale PR to `pyushkevich/itksnap:master`, or per-workstream PRs if that reviews better
- [ ] Wrapper `SUBMODULE_SYNC.md` + `CLAUDE.md` updated for the post-release submodule contract

---

## 4. Done-criteria

A workstream is done when **all** of these hold. Per metronome's test-as-ratchet rule, "tests exist
and are green" is not the bar — the bar is that a test would **fail on regression**.

1. Its work is merged into `staging/v460`.
2. `staging/v460` builds clean on **macOS arm64** and **Linux/GCC** (the two local build paths).
3. Its behavior has at least one test that fails if the behavior regresses, and `ctest` on
   `staging/v460` is no worse than the baseline below.
4. User-visible changes have a `ReleaseNotes.md` entry; developer-visible ones have a
   `Documentation/Developer/` entry.
5. Its checkbox in §3 is ticked and its own file's done-criteria are met.

**The release is done when** every in-scope workstream is done, the release-engineering list is
complete, the version reads `4.6.0` with no qualifier, and the PR is open with a green CI run.

### Test baseline to beat

**macOS arm64, `staging/v460` @ `038fa32b`, measured 2026-08-05 — this is now the authoritative
baseline. Runs 4/5/6 on this tree gave 32/34, 31/34 and 33/34; every failure in all three is a known
flake. The totals move only because the remote-test flake rotates. Compare the sets, not the numbers.**

| Run | Commit | Failure set |
|---|---|---|
| 1 | `b3cf79d3` | `RemoteImageLoadTest_SingleImage`, `EdgeAttraction`, `RandomForestBailOut` |
| 2 | `092022fb` | `RemoteImageLoadTest_SingleImage`, `4DReplayWithMeshUpdate`, `RandomForestBailOut` |
| 3 | `5f2825e4` | `RemoteImageLoadTest_WorkspaceWithMesh`, `RandomForestBailOut` |
| 4 | `7ba0692e` | `RemoteImageLoadTest_SingleImage`, `4DReplayWithMeshUpdate` |
| 5 | `038fa32b` | `RemoteImageLoadTest_SingleImage`, `RemoteImageLoadTest_WorkspaceWithMesh`, `4DReplayWithMeshUpdate` |
| 6 | `038fa32b` | `RemoteImageLoadTest_WorkspaceWithMesh` |

| Test | State | Note |
|---|---|---|
| `RandomForestBailOut` | ✅ | **Fixed in `7ba0692e`** (W8 item 15d) — a use-after-free of the row model's raw layer pointer, regressed from `1712c6e7`. Re-baselined against a stock build first: `5f2825e4` SEGFAULTs on macOS every run, so W8 item 15's "no longer segfaults" was wrong. Passes at **20.5 s**; a sub-second pass means it is not running. |
| `MeshWorkspace` | ✅ | Briefly SEGFAULTed on the first cut of the item-15d fix — caught and fixed in the same commit. Passes at **54 s**. Not a flake; if it goes red, it is a real regression. |
| `RemoteImageLoadTest_{SingleImage,WorkspaceWithMesh}` | ⚠️ flaky | **Fail only when the three remote tests run back-to-back**, and not always the same one; each passes standalone at the same sub-second duration, so it is not a timeout. Standalone CLI executables — unreachable from the GUI harness. W8 item 3/3b. |
| `4DReplayWithMeshUpdate` | ⚠️ flaky | Timing-sensitive; failed runs 2 and 4, passed runs 1 and 3. W8 item 2. |
| `EdgeAttraction` | ✅ | Red in run 1, and correctly so — it had been passing *because of* the item-17 bug. Green since W8 item 21, at 34.6 s, matching the stock-build timing. |

> ⚠️ **`RandomForestBailOut` is green but does not test what it was written to test.** Its three
> paintbrush strokes are silent no-ops, so the classifier trains on **0 samples** and the run
> follows the "training threw → modal dialog → cancel" path instead. That path is what exposed the
> item-15d use-after-free, so the coverage is real — it is just not the written intent. W8 item 22.

> ⚠️ **Superseded: the 2026-07-30 macOS figure of 32/33.** It predates `1d1fe7ea` and the harness
> fix, and the sprint's two records of it disagreed (32/33 here, 31/33 in the handoff). Do not
> compare against it.

> ⚠️ **The old baseline was not trustworthy.** Until `97285971` + `4e1baa2a`, any GUI test whose
> script was missing reported **Passed**. The previously documented Linux figure of 30/33 counted at
> least one test that executed nothing. Do not compare against it.

**Linux/GCC (Ubuntu 24.04, Xvfb + llvmpipe), `staging/v460` @ `7cc60053`, VTK 9.5.2, measured
2026-07-31: 30/33 — no new failures.** All three are stated debt; none is a regression from the
merge, the VTK upgrade, or `e2f19b56`.

| Test | State | Note |
|---|---|---|
| `RemoteImageLoadTest_Cache` | 🔴 fails | Genuinely **Linux-specific** — passes on macOS, failed here in July too. Download succeeds, `CacheMetadata.xml` is never written. W8 item 3. |
| `RandomForestBailOut` | 🔴 SEGFAULT | Measured before the fix. **Expected green on `7ba0692e`** — the macOS crash root-caused this session is the same stack gdb captured here, so this row needs one Linux run to confirm, not further investigation. The "code path macOS never reaches" claim was disproved: after W8 item 17, macOS reaches it too. |
| `4DReplayWithMeshUpdate` | ⚠️ flaky | llvmpipe timing; the documented cold-start mesh-build budget. W8 item 2. |
| other 30 | ✅ | including `4DContinuousRendering` at **36.5 s** — the false-green canary genuinely runs on Linux too |

Build: **766/766 targets, 0 errors, no local patches** — `git diff HEAD` empty on `staging/v460`.
This is the first time the Linux build has worked from a clean checkout; `e2f19b56` is confirmed
sufficient and the historical six-patch list is retired.

> Linux vs macOS differ by design, not by regression: `RemoteImageLoadTest_Cache` is Linux-only,
> `4DReplayWithMeshUpdate` needs llvmpipe to be slow, and `RemoteImageLoadTest_WorkspaceWithMesh`
> (the ~1-in-4 tdigest flake) happened to pass here and fail on macOS. Compare failure *sets*, not
> totals.

Linux headless, 2026-07-17 on `feature/cardiac-io`, **superseded**: 30/33, failing
`4DContinuousRenderingD`, `4DReplayWithMeshUpdate`, `RemoteImageLoadTest_Cache`. The matching total
is a coincidence — that run counted `4DContinuousRenderingD` as a real test when it executed nothing.

Counting rule: a **new** failure is a regression. The three above are stated debt, not a licence to
ignore new red.

---

## 5. Sequencing

W1 first — it is written, verified, and unblocks a clean `staging/v460`. W3 next, because W4 and W5
both depend on the DLS API it settles. W2, W6, W7, W8 are independent and can interleave.

```
W1 ─┬─► W3 ─┬─► W4
    │       └─► W5
    ├─► W2
    ├─► W6
    ├─► W7
    └─► W8
```

---

## 6. Risks and the cut line

| Risk | Impact | Mitigation |
|---|---|---|
| Workspace `FormatVersion` 1→3 breaks 4.4.0 compatibility | High | Decide in W1 before merging; test a 4.4.0 workspace against a 4.6.0 build **and** the reverse |
| VTK floor inconsistent between CI and CMake | High | Resolve before the first `staging/v460` CI run |
| W4/W5 blocked behind an unsettled DLS API | Medium | Freeze and version the DLS endpoints at the end of W3 |
| cmesh refactor touches the mesh pipeline broadly | Medium | Survey first (W7 step 1); land behind a flag or defer to 4.8 |
| Scope: 8 workstreams in one release | Medium | See the cut line |
| Agentic work rots on `sprint/caimi` while trunk moves | Medium | Rebase `sprint/caimi` on `staging/v460` at each beta |

**Cut line.** The minimum shippable 4.6.0 is **W1 + W2 + W8** plus release engineering. W3 is the
next most valuable. W4, W5, W7 are the first cut candidates. W6 is a bugfix and should survive any
cut that includes W8.

---

## 7. Refreshing §2

```bash
git -C itksnap fetch upstream origin --tags
for b in $(git -C itksnap branch -r --format='%(refname:short)' | grep '^origin/'); do
  echo "$b: +$(git -C itksnap rev-list --count upstream/master..$b)"
done
```

Repeat the fetch for `itksnap-dls`, `segflow4d`, and `convert-mesh`, then update §2 and the State
column in §3. Bump the verified date.
