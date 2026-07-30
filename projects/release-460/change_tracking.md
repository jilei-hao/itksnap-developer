# Change tracking — ITK-SNAP 4.6.0

**What this file is:** everything that has landed on the release trunk since **v4.4.0**, classified
so it can be turned into `ReleaseNotes.md`. It covers **merged** work only. Work still on a branch
is tracked in [SPRINT_PLAN.md](SPRINT_PLAN.md) §2, not here.

| | |
|---|---|
| Baseline | `20f63186` — *"Version bumped to 4.4.0"*, 2025-09-08 (the 4.4.0 release commit) |
| Head | `679ba76a` — *"Fixing major error with race condition when connecting to ITK-SNAP DLS"*, 2026-07-08 |
| Range | `20f63186..upstream/master` |
| Commits | **101** total, **83** non-merge |
| Version already on trunk | `4.6.0-alpha.1`, release date field `20260611` (bumped at `f2bf343a` → `28f4ee45`) |

`upstream` = `github.com/pyushkevich/itksnap`. `origin/master` (`jilei-hao` fork) is **in sync** with
`upstream/master` at `679ba76a`. Only the *local* `master` checkout lags by 1 — a local
`git merge --ff-only`, not a push.

**Last refreshed:** 2026-07-30.

---

## 1. Summary by type

| Type | Count | Notes |
|---|---:|---|
| Feature | 20 | dominated by one theme: remote/URL image I/O |
| Bugfix | 24 | 9 of them memory leaks; 4 Windows registry/URL |
| Refactor | 10 | progress-delegate + RESTClient + RemoteIOContext groundwork |
| Build / CI | 16 | VTK 9.5.2, macOS deployment target, NSIS replaces InnoSetup |
| Docs | 4 | `CLAUDE.md`, developer memory-management docs |
| Test | 3 | remote-IO regression, SSH Docker image, 4D replay |
| Chore / version | 6 | version bumps, trivial commits |

---

## 2. Features

### 2.1 Remote and URL-based image I/O — the headline feature of 4.6

A single sustained push (2026-04-27 → 2026-05-13) that makes ITK-SNAP able to open images and
workspaces straight from a URL. This is the largest coherent block in the release and deserves
its own section in the release notes.

| Commit | Date | What |
|---|---|---|
| `c832c6b3` | 04-28 | Remote image loading via `scp://` and `sftp://` URLs |
| `8a760e03` | 04-30 | Remote **workspace** loading + download progress callback |
| `71abae69` | 04-30 | SSH connection pool — amortizes handshakes across a workspace load (perf) |
| `1178f591` | 05-02 | `itksnap-sftp://` URL scheme, modal progress dialog, deferred loading |
| `860c1a75` | 05-04 | `itksnap-sftp` / `itksnap-scp` URL scheme registration on Windows |
| `878b3905` | 05-07 | Single-instance URL forwarding via a new `--url` flag (Windows) |
| `69f4477b` | 05-07 | NSIS registry handler passes the URL through as `--url` |
| `cc3e3703` | 05-06 | Persistent remote file cache; SSH/URL loading improvements |
| `33f6e4ce` | 05-07 | HTTP/HTTPS remote image source for public dataset URLs |
| `822b4899` | 05-07 | HTTP conditional-GET caching in `RemoteFileCache` |
| `c946c1f4` | 05-11 | **Flywheel.io** remote image source (`fw://` URL scheme) |
| `17d8de35` | 05-12 | Flywheel API-key auto-load, `itksnap-fw://` scheme registration, URL docs |
| `40a5a6c7` | 05-08 | Remote URL shown as its own field in General Layer Properties |

Supporting refactors: `be425043` + `8f02e57e` (RESTClient → `GenericServerTraits` / `DSSRESTClient`
/ `MakeFullURL`), `3a55d177` (`RemoteIOContext` bundle + unified `DownloadRemoteFile()`),
`2ad9e198` (shared metadata members consolidated into `WrapperBase`).
Docs: `Documentation/Developer/RemoteURLs.md`, plus `ad5a3892` in `CLAUDE.md`.
Tests: `114a2198` (remote-IO regression + cache validation), `e726c582` (SSH test Docker image).

### 2.2 Multi-instance / IPC

| Commit | Date | What |
|---|---|---|
| `9daffbf1` | 05-04 | **Window** menu listing every running ITK-SNAP instance |
| `9a5e66cf` | 05-05 | *Send to Other Window* in the drop-action dialog, over IPC shared memory |

### 2.3 Progress reporting and cancellation

| Commit | Date | What |
|---|---|---|
| `848f80fb` | 05-04 | Cancel a running task from an X button in the progress overlay |
| `00c0a073` | 05-04 | `ProgressReportWidget` auto-removal timeout is now opt-in per task |

Groundwork behind these (classified as refactor below): `cbe2a713`, `64d82996`, `a4774941`,
`8543ee78` — progress and SSH-auth reporting unified behind `AbstractProgressDelegate` in `Common/`,
with stdout implementations as the headless default.

### 2.4 AI-assisted segmentation

| Commit | Date | What |
|---|---|---|
| `2154b1bb` | 03-11 | **SAM2 integration** + the new progress bar (24 files, ~1500 lines in `IRISApplication` alone) |
| `8ea18264` | 05-08 | Minimum DLS version raised |

> The async/non-blocking follow-up to this work is **not** merged — see
> [workstreams/merge-backlog.md](workstreams/merge-backlog.md) D3.

### 2.5 Mesh and 4D I/O (contributed from this fork)

| Commit | Date | What |
|---|---|---|
| `9b3d4b75` | 03-11 | I/O support for `.vti` and `.vtp` |
| `01e02abd` | 03-09 | `.seq.nrrd` (NRRD volume sequence) **export** |

### 2.6 Robustness UX

| Commit | Date | What |
|---|---|---|
| `3b4a1f5c` | 02-28 | Explicit out-of-memory dialog when loading a too-large image, instead of a hard failure |

---

## 3. Bugfixes

### 3.1 Crashes and hangs

| Commit | Date | What | Reported |
|---|---|---|---|
| `679ba76a` | 07-08 | **Race condition connecting to the DLS server** — described upstream as a *major* error | |
| `c195eb1d` | 02-27 | Crash when continuous 3D update and 4D replay were both on | |
| `0d179aef` | 2025-10-11 | Crash opening some DICOM files (`GenericSliceRenderer`) | [#204](https://github.com/pyushkevich/itksnap/issues/204) |
| `9b699c7f` | 2025-10-11 | Hang opening some DICOM files (`SliceWindowDecorationRenderer`) | |
| `28f4ee45` | 06-11 | Opening workspaces failed | |

### 3.2 Memory leaks

Nine commits, all from the leak-profiling work (see `projects/memory_leak_profiling/`):
`1712c6e7`, `958646a7` (circular reference in `AbstractLayerTableRowModel`), `0db4b80b`, `35f181fd`
(VTK double-ref-count in `VTKMeshPipeline`), `99a2d81b` (VTK objects), `c0d8f4eb` (rebroadcaster),
`b3b319d2` (`ImageMeshLayers`), `b55fb7e0` (`m_DataMapping` after `QtCouplingHelper` teardown),
`0005a3f7` (remainder).

> ⚠️ `1712c6e7`/`958646a7` and `0db4b80b`/`35f181fd` are **duplicate pairs** — same message, same
> fix, landed twice (rebase or cherry-pick artifact). Harmless, but count them once in the notes.

### 3.3 Rendering and interaction

| Commit | Date | What |
|---|---|---|
| `d73c785d` | 05-12 | Annotations disappeared when switching to the brush/polygon tool |
| `b2b107c8` | 02-27 | Painted content lagged behind the paintbrush cursor circle during fast drags |
| `054ecea9` | 03-06 | Time-point change did not update mesh slice rendering |
| `cb049172` | 05-07 | Progress rows misaligned — cancel-button space is now reserved |

### 3.4 Remote I/O and Windows integration

| Commit | Date | What |
|---|---|---|
| `41b35c93` | 04-27 | Correctness bugs in the SSH tunnel implementation |
| `17c66980` | 05-03 | SFTP session init, connection pool, progress/auth dialog stacking |
| `e726c582` | 05-06 | `-w` flag did not resolve `itksnap-sftp://` URLs |
| `92896dc4` | 05-06 | Windows URL/path handling; `IPCHandler` macro conflict |
| `543afea8` | 05-04 | InnoSetup registry entries for the URL handlers *(superseded by `b7e8663a`)* |
| `59e22f5b` | 05-07 | NSIS registry commands for URL opening |
| `ea3333fb` | 05-07 | Further registry fixes |
| `7832a94b` | 05-12 | Percent-decoding for remote URLs (scp/sftp paths, Flywheel labels) |
| `a08ba762` | 05-01 | Startup image loading deferred until the event loop is running |

---

## 4. Build, CI, and packaging

| Commit | Date | What | Risk |
|---|---|---|---|
| `c480b003` | 03-25 | **VTK 9.3.1 → 9.5.2** — ⚠️ **CI workflow only.** `CMake/standalone.cmake:72` still says `FIND_PACKAGE(VTK 9.3.1 REQUIRED)`. CI and source disagree. | **High** |
| `8a01d7d2`, `b107ab02`, `92b413a1`, `0bd3b062` | 03–05 | `CMAKE_OSX_DEPLOYMENT_TARGET` and macOS runner versions; deployment-target mismatch fix | Medium |
| `b7e8663a` | 05-06 | URL-handler registry keys moved to NSIS; **InnoSetup removed** | Medium |
| `591c3540`, `2d26df2f` | 2025-09-09 | CI on ubuntu-22.04 (contributed by Matt McCormick) | Low |
| `661cd08d` | 05-07 | Removed dead `DeployQt5.cmake` and the `CMP0080 OLD` policy workaround | Low |
| `e83b73d1` | 05-04 | New headers registered in `CMakeLists.txt`; convention documented | Low |
| `4135d80b`, `25f4f6db`, `f0445c14`, `311b60af`, `afbb297a` | 03–04 | Packaging job, ctest verbosity, tmate placement | Low |
| `d88e72ab`, `9995ebcb` | 05-12 | Claude Code Review + PR Assistant GitHub workflows | Low |

---

## 5. Docs

| Commit | Date | What |
|---|---|---|
| `9ad06754` | 04-30 | `CLAUDE.md` added upstream — project layout, build commands, architecture |
| `63ae2293` | 05-07 | `CLAUDE.md` build instructions made platform-agnostic |
| `ad5a3892` | 05-07 | `--url` flag and single-instance forwarding documented |
| `3360b9dd` | 03-05 | `Documentation/Developer/MemoryManagement.md` + `MemoryLeakTestingMacOS.md` |

---

## 6. Flags for the release manager

1. **VTK version is inconsistent.** CI builds against 9.5.2 (`c480b003`) but
   `CMake/standalone.cmake` still requires 9.3.1. Decide the floor for 4.6.0 and make the two
   agree — otherwise the documented minimum is wrong in one place or the other.
2. **`ReleaseNotes.md` has no 4.6 section yet.** The file still tops out at *Version 4.4.0*.
   Sections 2–3 above are the raw material.
3. **InnoSetup is gone.** Any release/packaging runbook that mentions it is stale.
4. **Deduplicate the leak fixes** when writing the notes (§3.2).
5. **The *local* `master` checkout is 1 behind** `origin/master`/`upstream/master` (both `679ba76a`).
   Local housekeeping only — the fork itself is in sync.
6. **No `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, or governance file exists** in the itksnap repo
   (only `GUI/Qt/Resources/license.txt` and `Utilities/licensetemplate.txt`). That is net-new work
   — see [workstreams/developer-docs.md](workstreams/developer-docs.md).

---

## 7. How to refresh this file

```bash
git -C itksnap fetch upstream --tags
git -C itksnap log --no-merges --date=short --format="%h|%ad|%an|%s" 20f63186..upstream/master
```

Append new commits to the right section and bump **Last refreshed** at the top.
