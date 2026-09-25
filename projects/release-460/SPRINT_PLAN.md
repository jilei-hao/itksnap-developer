# SPRINT_PLAN — ITK-SNAP 4.6.0 release

**Opened:** 2026-07-30 · **Re-planned:** 2026-09-24 (branch model and session model — §2, §5) ·
**Project:** `projects/release-460/` · **Testing branch:** `staging/v460` · **Review queue:** [branches.md](branches.md) · **Merge order:** [MERGE_ORDER.md](MERGE_ORDER.md)

Per metronome convention this file holds **scope, goals, and done-criteria**. Only checkboxes change
mid-sprint — except §2, which is a dated snapshot that gets **re-verified, not re-planned**. The
journal is [PROGRESS_LOG.md](PROGRESS_LOG.md); merged history is [change_tracking.md](change_tracking.md);
per-workstream detail is in [workstreams/](workstreams/); the per-branch upstream queue is
[branches.md](branches.md).

> **Three rules set by Jilei on 2026-09-24. They override anything older in this directory.**
>
> 1. **One topic branch per feature or fix, cut from `upstream/master`.** `staging/v460` is for
>    **testing only**: it is `upstream/master` plus a merge of each topic branch, and nothing is
>    committed to it directly. Branches are reviewed and merged one at a time in the planning
>    meeting.
> 2. **Jilei picks each session's goal.** The open backlog is listed in §3 and the workstream files
>    as a reminder, not a queue. A session does not start work until Jilei names the item, and
>    `/handoff` does not choose the next goal.
> 3. **[MERGE_ORDER.md](MERGE_ORDER.md) is updated every time a topic branch changes** — a new
>    branch, a commit, a rebase, a merge upstream, a deletion. Its Status section refreshes itself
>    through a git hook; its Queue and Constraints are updated by hand whenever Status shows ⚠️.
>    A session that changed a branch is not finished until Status reads "Needs attention: nothing".

---

## 1. Goal

Ship **ITK-SNAP 4.6.0**: take the 4.6.0-alpha trunk, land the eight workstreams in §3 as
independently reviewable topic branches (tested together on `staging/v460`), and deliver a release
with notes, developer documentation, and a governance baseline.

**Explicit non-goal: the agentic API / MCP prototype.** That is the October CAIMI demo
(`projects/agentic-api/`). Keep `sprint/caimi` alive, and rebase it onto the accepted topic branches
when the demo needs release code. Do not merge it, and do not merge `itksnap-mcp` at all.

---

## 2. State of the tree — verified 2026-09-24

> Re-verify with §7 and update in place. This is the one section that changes without being a
> re-plan; the numbers are observations, not commitments.

### Branch model (from 2026-09-24)

```
upstream/master (52ee94fa) ──┬── feature/cardiac-io        ─┐
                             ├── bug/linux-gcc-build        │
                             ├── bug/rf-layer-crashes       ├─ merge --no-ff each ─► staging/v460  (testing only)
                             ├── test/harness-false-green   │
                             └── test/harness-gui-thread   ─┘
```

- **Every piece of work lives on its own topic branch off `upstream/master`**, named with the
  repo's existing prefixes: `feature/`, `bug/`, `test/`. One branch = one PR = one decision in the
  planning meeting. A fix to a topic goes on that topic's branch, never on staging.
- **`staging/v460` is disposable.** It is `upstream/master` plus a `--no-ff` merge of every live topic
  branch, used to run the suite on everything together. Rebuild it rather than repairing it (§7).
  Nothing is committed to it directly.
- **When upstream moves:** rebase each topic branch onto the new `upstream/master`, then rebuild
  staging. Keep every branch mergeable on its own: `git merge-tree --write-tree` for each pair must
  be clean.
- **New branches get no upstream tracking.** `git checkout -b X upstream/master` sets the push target
  to Paul's `master`; run `git branch --unset-upstream X` straight away.

### Testing branch

| | |
|---|---|
| Branch | `staging/v460` (itksnap) |
| Base | `upstream/master` @ `52ee94fa` (26 commits past the July base `679ba76a`) |
| Local | `62588ffc` = `upstream/master` + five topic merges. **Tree byte-identical** to the pre-split tip `archive/staging-v460-0904` (`6f5ae27c`) |
| Remote | **Pushed 2026-09-24** — `origin/staging/v460` = `62588ffc` (force-pushed with a lease from `038fa32b`) |

### itksnap — topic branches (the review queue)

Full detail, evidence and discussion points per branch: **[branches.md](branches.md)**. Merge order,
constraints and live state: **[MERGE_ORDER.md](MERGE_ORDER.md)**.

| Branch | Ahead | Content | Pushed |
|---|---:|---|---|
| `feature/cardiac-io` | 12 | 4D cardiac CTA + echo phase/metadata I/O (W1 D1). Rebased onto `52ee94fa`; old tip `archive/feature-cardiac-io-pre-rebase` | yes (forced) |
| `bug/linux-gcc-build` | 2 | GCC portability + VTK floor 9.5.2 (W1 D2, Q2) | yes |
| `bug/rf-layer-crashes` | 4 | RF-cancel and layer-teardown crashes + the test that catches them (W8 14, 15, 15d, 24) | yes |
| `test/harness-false-green` | 1 | missing GUI-test script reported Passed; `GUI_TESTS` typo (W8 1, 13) | yes |
| `test/harness-gui-thread` | 1 | `TestObjectProxy` on top of upstream `dbf8e79f` (W8 17, 25) — **discuss with Paul first** | yes |

### itksnap — other branches

| Branch | Ahead | Content | Disposition |
|---|---:|---|---|
| `sprint/caimi` | 19 | old `feature/cardiac-io` (12) + Linux/GCC fix (1) + agentic prototype (6) | out of scope; rebase on a topic-free base when the demo needs it |
| `test/dls_sam2` | 4 | async DLS interactions (`cb6f692e`, `ea86df0d`), submodule bump, Linux fix | not ready — W1 Q4 |
| `developer-doc` | 0 | W2 — merged upstream as PR #244 | delete |
| `bug/{4d-mesh-slice,large-image-oom,memory-leak,mesh-update-crash}` | 0 | merged | delete — W8 item 7 |
| `feature/{io-improvement,seq-nrrd-export,vti-io}` | 0 | merged | delete — W8 item 7 |
| `origin/master` | 0 | in sync with `upstream/master` @ `52ee94fa` | nothing to do |

What upstream landed since July, and what it means for us:

- **The seg_anchor refactor.** The reference space now follows the active segmentation, and there
  are `GenericImageData` renames. No topic branch conflicted with it.
- **Version `4.6.0-alpha.3`**, and Qt 6.9.3 in CI.
- **PR #244 — our W2 docs.**
- **`dbf8e79f`**, which fixed the harness threading problem its own way. It overlaps W8 item 17 and
  also fixed item 21 and the `ApplyColorMap` null guard; see [branches.md](branches.md) "Not
  branched".
- **Nothing in [change_tracking.md](change_tracking.md) covers these 26 commits yet.** It still
  stops at `679ba76a`.

The pre-rebase layout of `sprint/caimi`, kept for when the agentic work is re-based:

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
| **itksnap-dls** | `feature/agentic-api` | `bbaac51` | W4, W5 | ⚠️ 4-branch tangle; the refactor is **already written** — [dls-refactor.md](workstreams/dls-refactor.md). Checkout currently on `developer-doc` @ `76f609f` (W2 docs, already in `origin/main`), so the wrapper shows the pointer as modified — uncommitted |
| **segflow4d** | `main` | `ed143db` | W5 | Integrated into itksnap-dls at `7ecf586`; 4 unmerged side branches to triage |
| **convert-mesh** (`cmesh`) | `main` | `45482ca` | W7 | Reorganized under `src/cmesh/`; **no release tag**; not yet an itksnap submodule |
| **itksnap-mcp** | `main` | `1228618` | — | Agentic-API only; **not in 4.6.0** |
| **greedy_python** / **cmrep** / **FireANTs** | — | — | — | Not in scope |

---

## 3. Scope

### Workstreams

Branch column is authoritative for "where is this work". Tick the box when §4 is satisfied.
This table and the workstream files are the **reminder list** of what is left — which item a session
works on is Jilei's call (rule 2 at the top).

| | Workstream | Branch | Depends on | State |
|---|---|---|---|---|
| ☐ **W1** | [Merge the ready backlog](workstreams/merge-backlog.md) — 4D cardiac I/O, Linux/GCC portability, async DLS | `feature/cardiac-io`, `bug/linux-gcc-build` | — | Both branches ready for review ([branches.md](branches.md)). Open: cardiac round-trip test; async DLS blocked on Q4's two `cb6f692e` defects; submodule bump; branch cleanup |
| ☑ **W2** | [Developer docs & governance](workstreams/developer-docs.md) — `CONTRIBUTING`, `CODE_OF_CONDUCT`, governance, dev guide | merged upstream | — | **Done** — PR #244 (`5e2984ff`, 2026-08-18); same docs on `itksnap-dls:main` |
| ☐ **W3** | [itksnap-dls refactor](workstreams/dls-refactor.md) — promote modules + TotalSegmentator + segflow4d + tests to `main` | `itksnap-dls:feature/agentic-api` | segflow4d | **Largely written** — needs promotion |
| ☐ **W4** | [Auto-segmentation UI](workstreams/auto-seg-ui.md) | none yet | W3 | Not started |
| ☐ **W5** | [Propagation UI](workstreams/propagation-ui.md) | none yet | W3 | Not started |
| ☐ **W6** | [Free-rotation 2D/3D sync](workstreams/free-rotation-sync.md) — [#229](https://github.com/pyushkevich/itksnap/issues/229) | none yet | — | Not started — this is a **bug** |
| ☐ **W7** | [cmesh integration](workstreams/cmesh-integration.md) — tag, submodule, refactor `Logic/Mesh/` | `convert-mesh:main` | cmesh tag | Library exists; itksnap side not started |
| ☐ **W8** | [Bugfixes & small improvements](workstreams/bugfixes.md) | `bug/rf-layer-crashes`, `test/harness-false-green`, `test/harness-gui-thread`; one new branch per future fix | — | Rolling — 3 branches ready for review; open items in the workstream file |

### Release engineering

- [x] `staging/v460` created and pushed (2026-07-30). **Rebuilt 2026-09-24 as a testing-only branch** (§2); not yet re-pushed
- [ ] Version bumped from `4.6.0-alpha.1` to a beta, then to `4.6.0`
- [x] **VTK floor decided** — raised to **9.5.2** (`7cc60053`), matching upstream CI. **Both build
      paths upgraded and verified 2026-07-31**: macOS arm64 (31/33) and Linux/GCC (30/33), each
      building clean with no regressions attributable to the floor change.
- [ ] **Workspace `FormatVersion` decision** — cardiac I/O bumps it 1→3; decide whether
      `SNAP_VERSION_LAST_COMPATIBLE_RELEASE_DATE` moves or the reader degrades
- [ ] `ReleaseNotes.md` gains a 4.6 section, built from [change_tracking.md](change_tracking.md)
- [ ] Merged branches deleted (W8 item 7)
- [ ] Per-topic PRs to `pyushkevich/itksnap:master` — **decided 2026-09-24** (replaces the wholesale
      PR). One PR per branch in [branches.md](branches.md), in whatever order the planning meeting
      accepts them
- [ ] [change_tracking.md](change_tracking.md) refreshed past `679ba76a` — upstream has moved 26 commits
- [ ] Wrapper `SUBMODULE_SYNC.md` + `CLAUDE.md` updated for the post-release submodule contract

---

## 4. Done-criteria

A workstream is done when **all** of these hold. Per metronome's test-as-ratchet rule, "tests exist
and are green" is not the bar — the bar is that a test would **fail on regression**.

1. Its work is on its own topic branch(es) off the current `upstream/master`, each of which **builds
   and passes the suite standalone**, with no worse a failure set than `upstream/master` itself.
   It is also merged into `staging/v460`, and every pair of live branches merges cleanly.
2. `staging/v460` builds clean on **macOS arm64** and **Linux/GCC** (the two local build paths).
3. Its behavior has at least one test that fails if the behavior regresses, and `ctest` on
   `staging/v460` is no worse than the baseline below.
4. User-visible changes have a `ReleaseNotes.md` entry; developer-visible ones have a
   `Documentation/Developer/` entry.
5. Its checkbox in §3 is ticked and its own file's done-criteria are met.

**The release is done when** every in-scope workstream is done, the release-engineering list is
complete, the version reads `4.6.0` with no qualifier, and every accepted topic PR is merged
upstream with a green CI run.

### Test baseline to beat

**Current — macOS arm64, rebuilt `staging/v460` @ `62588ffc` (= `upstream/master` `52ee94fa` + the
five topic branches), measured 2026-09-24: 34/35, failing only `RemoteImageLoadTest_SingleImage`.**
Run 7, on the byte-identical pre-split tip, failed the *other* remote test. Both runs failed only
within the rotating remote-flake pair, and nothing outside it. Two
reference points go with it, because the branch model makes each of them a merge criterion (§4
item 1):

- **`upstream/master` alone: 34/34**, of which two are vacuous. `4DContinuousRenderingD` passes in
  0.91 s and `RandomForestBailOut` in 0.89 s without running.
- **`4DReplayWithMeshUpdate` fails upstream too:** 3/5 on `upstream/master`, against 5/5 on
  `test/harness-gui-thread`. It is a flake, not a regression.

Per-branch standalone results are in [branches.md](branches.md).

**Superseded — `staging/v460` @ `038fa32b`, measured 2026-08-05.** Runs 4/5/6 on this tree gave
32/34, 31/34 and 33/34; every failure in all three is a known flake. The totals move only because the
remote-test flake rotates. Compare the sets, not the numbers.

| Run | Commit | Failure set |
|---|---|---|
| 1 | `b3cf79d3` | `RemoteImageLoadTest_SingleImage`, `EdgeAttraction`, `RandomForestBailOut` |
| 2 | `092022fb` | `RemoteImageLoadTest_SingleImage`, `4DReplayWithMeshUpdate`, `RandomForestBailOut` |
| 3 | `5f2825e4` | `RemoteImageLoadTest_WorkspaceWithMesh`, `RandomForestBailOut` |
| 4 | `7ba0692e` | `RemoteImageLoadTest_SingleImage`, `4DReplayWithMeshUpdate` |
| 5 | `038fa32b` | `RemoteImageLoadTest_SingleImage`, `RemoteImageLoadTest_WorkspaceWithMesh`, `4DReplayWithMeshUpdate` |
| 6 | `038fa32b` | `RemoteImageLoadTest_WorkspaceWithMesh` |
| 7 | `6f5ae27c` (Sep 4 upstream merge, 35 tests) | `RemoteImageLoadTest_WorkspaceWithMesh` |
| 8 | `62588ffc` (rebuilt from topic branches, same tree as run 7) | `RemoteImageLoadTest_SingleImage` |

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

**Windows 11 / MSVC 19.34, `staging/v460` @ `d02236c3` (built from a byte-identical local merge),
Qt 6.9.3, VTK 9.5.2, ITK 5.4.0, measured 2026-09-25: 40/41.**
First Windows run. Build: 777/777 targets, 0 errors, no patches. The only failure is
`RemoteImageLoadTest_Cache`, which is a test bug on every non-macOS platform (W8 3, root-caused
this run). Real run times are within a few seconds of macOS: `RandomForestBailOut` 20.8 s,
`4DContinuousRendering` 39.1 s, `MeshWorkspace` 47.5 s. `4DReplayWithMeshUpdate` passed. Recipe:
`scripts/windows/`.

Linux headless, 2026-07-17 on `feature/cardiac-io`, **superseded**: 30/33, failing
`4DContinuousRenderingD`, `4DReplayWithMeshUpdate`, `RemoteImageLoadTest_Cache`. The matching total
is a coincidence — that run counted `4DContinuousRenderingD` as a real test when it executed nothing.

Counting rule: a **new** failure is a regression. The three above are stated debt, not a licence to
ignore new red.

---

## 5. Sequencing

**There is no fixed order any more — Jilei picks each session's item (rule 2 at the top).** The graph
below only records hard dependencies, so a pick that violates one gets flagged rather than silently
started:

```
W3 ─┬─► W4        W3 settles the DLS API that W4 and W5 call
    └─► W5
W1, W6, W7, W8    independent — any order
W2                done (upstream PR #244)
```

**The review queue's order and constraints live in [MERGE_ORDER.md](MERGE_ORDER.md)** (rule 3). As
of 2026-09-24:
- `bug/rf-layer-crashes` cannot be split;
- it must precede `test/harness-false-green`;
- the five branches are pairwise conflict-free.

---

## 6. Risks and the cut line

| Risk | Impact | Mitigation |
|---|---|---|
| Workspace `FormatVersion` 1→3 breaks 4.4.0 compatibility | High | Decide in W1 before merging; test a 4.4.0 workspace against a 4.6.0 build **and** the reverse |
| VTK floor inconsistent between CI and CMake | High | Resolve before the first `staging/v460` CI run |
| W4/W5 blocked behind an unsettled DLS API | Medium | Freeze and version the DLS endpoints at the end of W3 |
| cmesh refactor touches the mesh pipeline broadly | Medium | Survey first (W7 step 1); land behind a flag or defer to 4.8 |
| Scope: 8 workstreams in one release | Medium | See the cut line |
| Agentic work rots on `sprint/caimi` while trunk moves | Medium | Rebase `sprint/caimi` onto the accepted topic branches when the demo needs a refresh |
| Topic branches drift apart from each other or from upstream | Medium | Rebase all onto each new `upstream/master`, rebuild staging, re-check pairwise `merge-tree` (§7) |
| Upstream fixes the same bug differently while ours waits for review | Medium | Happened three times in Aug (`dbf8e79f`, `93aa9583`). Before building on a branch, check `git log <old base>..upstream/master` for the files it touches |

**Cut line.** The minimum shippable 4.6.0 is **W1 + W2 + W8** plus release engineering. W3 is the
next most valuable. W4, W5, W7 are the first cut candidates. W6 is a bugfix and should survive any
cut that includes W8.

---

## 7. Refreshing §2

```bash
git -C itksnap fetch --multiple --tags upstream origin
for b in $(git -C itksnap branch -r --format='%(refname:short)' | grep '^origin/'); do
  echo "$b: +$(git -C itksnap rev-list --count upstream/master..$b)"
done
```

Repeat the fetch for `itksnap-dls`, `segflow4d`, and `convert-mesh`, then update §2 and the State
column in §3. Bump the verified date.

### Rebuilding `staging/v460` from the topic branches

Run from `itksnap/`. Tag the old tip first so nothing is lost. The branch list is the live one in §2.

```bash
git tag -a archive/staging-v460-$(date +%m%d) staging/v460 -m "staging/v460 before rebuild"
T=(feature/cardiac-io bug/linux-gcc-build bug/rf-layer-crashes test/harness-false-green test/harness-gui-thread)
for b in $T; do git rebase upstream/master $b; done          # only if upstream moved
for a in $T; do for b in $T; do [[ $a < $b ]] &&             # every pair must merge alone
  { git merge-tree --write-tree $a $b >/dev/null || echo "CONFLICT $a + $b"; }; done; done
git checkout -B staging/v460 upstream/master
for b in $T; do git merge --no-ff --no-edit -m "Merge $b into staging/v460" $b; done
git branch --set-upstream-to=origin/staging/v460   # checkout -B pointed it at upstream/master
python3 ../scripts/merge_order_status.py --check   # the hook already ran; this prints what needs attention
```

The loops use zsh array syntax. In bash, write `"${T[@]}"`: a bare `$T` there silently expands to
the first branch only.
