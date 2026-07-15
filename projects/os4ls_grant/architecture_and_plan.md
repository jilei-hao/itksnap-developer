# ITK-SNAP OS4LS — High-Level Plan & Architecture (24-month project)

**Proposal:** ITK-SNAP: Human-in-the-Loop AI Image Segmentation (OS4LS) · PI Paul Yushkevich
**This document:** the engineering bridge between the grant narrative and the code. It turns the
two grant goals into a layered architecture, a capability ledger, and a release-aligned 2-year
roadmap, grounded in the actual codebase as of this session.

**Reads with:**
- `projects/os4ls_grant/work_plan_draft.md` — the grant narrative (goals, outcomes, milestones).
- `projects/agentic-api/docs/agentic-prototype-plan.md` — deep Goal-1 orientation + the demo-video
  prototype plan (Layer-1/Layer-2 findings, DLS internals, distribution strategy). This document
  does **not** repeat that verification; it generalizes it into the full-project architecture and
  adds the Goal-2 half that the prototype plan did not cover.

All paths are relative to the wrapper repo root `/Users/jileihao/dev/itksnap-dev/itksnap-developer/`.

---

## 0. TL;DR — the five findings that shape the plan

1. **Goal 1's data plane is real and Qt-free today.** `Logic/` has **0** Qt includes and `GUI/Model/`
   has **0** (verified on the current `feature/cardiac-io` branch); the three library targets
   `itksnaplogic` / `itksnapui_model` / `itksnapui_qt` enforce the boundary
   (`itksnap/CMakeLists.txt:1228-1234`), and the shipped `itksnap-wt` binary proves a Qt-free
   headless binary links. **A Python skin (Layer 1) is a build-config + binding effort, not a rewrite.**

2. **Goal 2's remote/cloud transport plane is *also* mostly built already** — a genuine surprise that
   strengthens the "integration, not greenfield" thesis. ITK-SNAP already loads images **and**
   `.itksnap` workspaces over `fw://` (Flywheel), `scp://`/`sftp`, and `http(s)://`, with per-scheme
   caching and a checked-in spec (`itksnap/Documentation/Developer/RemoteURLs.md`). What is missing is
   **browsing** (directory listing), an **explorer UI**, **BIDS** awareness, and **multi-workspace** —
   i.e. the *UX and navigation* layer, not the transport.

3. **The "propose" side (itksnap-dls) is ahead of where the prototype plan left it.** The submodule is
   now on branch **`feature/agentic-api`** (v0.1.3), which has merged segflow4d **and already added a
   `TotalSegmentatorWrapper`** — the fully-automatic model §8 of the prototype plan recommended — with
   an `AUTOMATIC` flag and a `run()` method, advertised through `get_model_listing()`
   (`itksnap-dls/itksnap_dls/modules/segmentation/models.py:208-312`). The async job manager
   (`modules/propagation/jobs.py`, `ThreadPoolExecutor`, status `pending|running|completed|failed`)
   is the resumable substrate for both automatic segmentation and `request_review`.

4. **The net-new surface is small, specific, and shared across both goals.** Goal 1: a Python binding
   (Layer 1), a live-GUI command channel (Layer 2), an audit/provenance record, and an MCP server.
   Goal 2: an explorer UI + a browsable data-source abstraction, and a **DICOM-SEG** subsystem
   (genuinely net-new — no `dcmqi`/`DCMTK`/SEG code exists anywhere). Everything else is existing code
   composed behind these thin new pieces.

5. **Version cadence supports the release train.** ITK-SNAP is at **4.6.0-alpha.1** (dated 2026-06-11,
   `itksnap/CMakeLists.txt:94-101`); historical cadence is ~one minor release per year
   (4.0 → 4.2 → 4.4 → 4.6-alpha over 2023–2026). So **4.8 = Year 1** and **4.10 = Year 2** is realistic.

> **Reframing recommended to the grant reviser** (detail in §9): Goal 2 milestone 2.1 should be worded
> as *"a browsable explorer + agent API over the already-shipped remote-IO transport,"* not as building
> remote access from scratch — the code makes the stronger, more honest claim.

---

## 1. Ground truth (current state)

| Component | Path | Branch / version | Role |
|---|---|---|---|
| ITK-SNAP app | `itksnap/` | `feature/cardiac-io` · **4.6.0-alpha.1** | Core substrate + live GUI target |
| itksnap-dls | `itksnap-dls/` | **`feature/agentic-api`** · v0.1.3 (MIT) | Model-serving plane (the "propose" side) |
| greedy_python | `greedy_python/` | `test/integration` · picsl_greedy 0.0.12 | **The Layer-1 binding pattern to copy** |
| segflow4d | `segflow4d/` | v1.1.3 | 4D propagation engine (behind a dls async job) |
| convert-mesh / cmrep / FireANTs | — | — | Off the critical path for this grant |

**Three-tier library boundary** (the architectural spine everything hangs off), `itksnap/CMakeLists.txt:1228-1234`:

- `itksnaplogic` — Logic tier: ITK + non-rendering VTK, **no Qt**. Home of WorkspaceAPI, IRISApplication,
  ImageWrapper, SegmentationUpdateIterator, UndoDataManager, GuidedNativeImageIO, the remote-IO stack,
  RESTClient/SSHTunnel, PropertyModel/events.
- `itksnapui_model` — GUI/Model presenter tier: adds rendering VTK, **still no Qt**. Home of
  DeepLearningSegmentationModel, DistributedSegmentationModel.
- `itksnapui_qt` — GUI/Qt view tier: the only place Qt lives. Home of the live GUI, SNAPTestQt, main.cxx.

**Two shipped executables** prove the boundary is real: `ITK-SNAP` (GUI) and `itksnap-wt` (headless
workspace tool, links `itksnaplogic + ITK + CURL`, zero Qt — `itksnap/Utilities/Workspace/`).

---

## 2. Architecture design

### 2.1 The whole system, one diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  AGENT / DATA PIPELINE   (external: an LLM agent, a batch job, a notebook)      │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                    │  MCP — ONE tool namespace
┌───────────────────────────────────▼──────────────────────────────────────────┐
│  LAYER 2 · MCP SERVER          [NET-NEW · local, pip-installed, no hosted svc] │
│    headless.* tools ─────────┐          live.* tools ──────────┐               │
│    session { mode: headless|attached, pid, workspace, dls_session }            │
└───────────────┬──────────────┘─────────────────────────────────┼─────────────┘
                │ in-process (pybind11)            JSON-RPC over   │ QLocalSocket
┌───────────────▼─────────────────────┐   ┌───────────────────────▼─────────────┐
│ LAYER 1 · pysnap  [NET-NEW, small]   │   │ LIVE COMMAND CHANNEL  [NET-NEW]      │
│  thin wheel; greedy_python recipe    │   │  QLocalServer in main.cxx forwards   │
│  over itksnaplogic. Workspace/label/ │   │  JSON → existing SNAPTestQt          │
│  cursor/apply-mask/read-audit.       │   │  primitives, injected into the       │
│                                      │   │  RUNNING Qt event loop.              │
└───────────────┬─────────────────────┘   └───────────────────────┬─────────────┘
                │                                                  │
┌───────────────▼──────────────────────────────────────────────────▼───────────┐
│  ITK-SNAP CORE   [EXISTS · 3-tier · Qt-free boundary verified]                 │
│    itksnaplogic  ─►  itksnapui_model  ─►  itksnapui_qt (the live GUI)           │
│    WorkspaceAPI · IRISApplication(SetCursorPosition, UpdateSegmentationWith*)   │
│    SegmentationUpdateIterator · UndoDataManager [+ AUDIT RECORD, net-new]       │
│    GuidedNativeImageIO [+ DICOM-SEG, net-new] · Remote-IO stack · PropertyModel │
└───────┬────────────────────────────────────────────────────────┬──────────────┘
        │ HTTP (RESTClient, libcurl)                              │ fw:// scp:// http(s)://
┌────────▼─────────────────────────────┐        ┌────────────────▼───────────────────────┐
│ MODEL PLANE · itksnap-dls  [EXISTS]  │        │ DATA PLANE · remote/cloud IO  [EXISTS]  │
│  feature/agentic-api, MIT            │        │  Flywheel fw:// · SFTP/SCP · HTTP(S) ·   │
│  ModelWrapper registry:              │        │  remote .itksnap workspaces ·           │
│   • interactive: nnInteractive, SAM2 │        │  RemoteFileCache                        │
│     → synchronous session            │        │  ── net-new on top: ──                  │
│   • automatic: TotalSegmentator      │        │  Explorer UI · directory BROWSING ·     │
│     → async job (run())              │        │  BIDS · multi-workspace · DICOM-SEG     │
│   • 4D: segflow4d → async job        │        │                                         │
└──────────────────────────────────────┘        └─────────────────────────────────────────┘
```

The agent sees **one** MCP surface. Behind it, `headless.*` tools run in-process through the Python
binding (no GUI); `live.*` tools require an attached GUI and drive it through the command channel. Both
goals share the same Layer-1/Layer-2 spine — the explorer and interop features of Goal 2 are additional
tools in the *same* namespace, not a separate product.

### 2.2 Goal 1 components — composable human-in-the-loop

**(a) Layer 1 · `pysnap` Python API** — *net-new, small.* pybind11 + scikit-build-core over
`itksnaplogic`, copying the working `greedy_python` recipe (`greedy_python/CMakeLists.txt`,
`src/GreedyPythonBindings.cxx`, `src/picsl_greedy/_greedy_api.py`). Exposes headless workspace open/save
(`WorkspaceAPI`), layer/label CRUD, `apply_mask` (`IRISApplication::UpdateSegmentationWithBinarySegmentation`,
`IRISApplication.h:621`), voxel cursor get/set (`IRISApplication.h:485,490`), and audit read.
*Caveat carried from the prototype plan:* ITK-SNAP's `RLEImage`/`LabelImageWrapper` need SimpleITK⇄ITK
converter specializations beyond greedy_python's base-type ones. The DLS HTTP client needs **no** ITK, so
it ships as plain Python first, ahead of the pybind11 work.

**(b) Live command channel** — *net-new, the hardest integration; the Layer-2 spine.* Today the test
harness `SNAPTestQt` (`itksnap/Testing/GUI/Qt/SNAPTestQt.cxx`) already does semantic widget addressing
(`findChild`/`findWidget`), Qt property read/write, real event injection (`postMouseEvent`,
`postKeyEvent`, `trigger`, `invoke`), and image-space cursor control (`setCursor(x,y,z)` → voxel
spinboxes) — but only from a **canned `.js` launched via `--test` before `QApplication::exec()`**. The
net-new work is a small `QLocalServer` in `main.cxx` that accepts JSON commands over a socket and
forwards them to the existing `SNAPTestQt` slots **inside the running event loop**. This is what makes
`live.*` tools possible and is the single biggest technical risk (§6).

**(c) Audit / provenance record** — *net-new, small, localized.* `UndoDataManager`
(`Logic/Framework/UndoDataManager.{h,txx}`) already captures per-operation RLE label deltas with a
commit name, but has **no timestamp, identity, op-type, counts, or export**, and the commit name has no
public getter. Add the minimum-viable schema `{op, timestamp, agent-vs-human, changed-voxel count,
bbox, before/after label counts}` plus a JSON serializer, triggered off `SegmentationChangeEvent`. This
record is the "audited" leg of the thesis **and** the training signal Goal 1 Year 2 consumes.

**(d) `request_review` — the resumable primitive that *is* the differentiator.** Model proposes → an
agent-side confidence gate flags an uncertain case → the case is *parked* → the live GUI focuses on the
uncertain slice with the proposal loaded → the human corrects on camera → a structured verdict returns.
The resumable state machine is modeled on the DSS ticket lifecycle
(`GUI/Model/DistributedSegmentationModel.h:139-141`, `STATUS_INIT/CLAIMED/SUCCESS/...`) but realized as a
**same-process live handoff** (decision A, §5) rather than cross-process ticket exchange, because DLS
session state does not persist across restarts.

**(e) Layer 2 · MCP server** — *net-new.* One tool namespace, two backends, an explicit `session`
object `{ mode: headless|attached, pid, workspace, dls_session_id }`. `live.*` on a headless session
triggers an attach (launch the GUI, load the same workspace). Ships as a local pip package; no hosted
service, no per-user cost.

**(f) Model plane · itksnap-dls** — *exists, ahead of schedule.* `snap.propose()` is a thin HTTP client
over the pluggable registry: interactive (nnInteractive point/box/scribble/lasso, SAM2 point) on the
synchronous `/v2/...` session path; automatic (TotalSegmentator) and 4D (segflow4d) on the async
`start_job → poll → result` path. *License hygiene (product transition, not grant blocker):*
nnInteractive weights are CC BY-NC-SA; the clean-weight path is TotalSegmentator-core / SegVol (MIT) /
VISTA3D-NV.

### 2.3 Goal 1 Year-2 loop — expert interaction → model improvement

The audit records (2.2c) are the raw material. Year 2 (a) captures expert corrections as
**machine-consumable, provenance-tagged training records** (milestone 1.2), and (b) uses them to
**evaluate the value of expert-in-the-loop correction** on a public benchmark (milestone 1.3): fine-tune a
dls-served model on expert-corrected cases and report the change vs. the uncorrected baseline (overlap +
boundary metrics, magnitude reported), and test whether routing *uncertain* cases to the expert beats
random selection at equal effort — releasing the evaluation harness open source. Candidate benchmarks:
cardiac CT (e.g., MM-WHS — matches the team's CT/TEE data and the TotalSegmentator served model) and/or the MSD hippocampus task — both have strong public benchmarks and in-house/PI
expertise. Architecturally this closes the loop: `request_review` emits structured deltas → a training set
→ an improved `ModelWrapper` served back through the same registry.

### 2.4 Goal 2 components — remote data & interoperability

**What already exists (transport plane — reuse, do not rebuild):**
- **Flywheel** `fw://` — full fetch-by-URL with hierarchy resolution and ticket→S3 download
  (`Logic/ImageWrapper/FlywheelRemoteImageSource.cxx`, ~480 LOC; API key from `~/.fw/config.yml`).
- **SSH/SFTP** single-file download (`Logic/WorkspaceAPI/SSHTunnel.cxx` auth + `direct-tcpip`;
  `Logic/ImageWrapper/SSHConnectionPool.cxx`; `ImageIORemote.cxx` `SCPRemoteImageSource::Download`).
- **HTTP(S)** image + generic download over the reusable libcurl `RESTClient` (`Logic/WorkspaceAPI/RESTClient.{h,cxx}`).
- **Remote `.itksnap` workspaces** — `IRISApplication::OpenProject` (`IRISApplication.cxx:2337+`) rebases
  every layer path into a remote URL and fetches via the same machinery; per-scheme ETag/mtime caching
  (`RemoteFileCache.{h,cxx}`). Spec: `Documentation/Developer/RemoteURLs.md`.
- **DSS ticket** upload/download of whole workspace bundles (`WorkspaceAPI.cxx:1186-1340`).
- **DICOM read** — GDCM series discovery + grouping (`GuidedNativeImageIO.cxx:2745-2882`), incl.
  multi-frame / 4D CTA / echo-cartesian paths; within-directory series picker
  (`GUI/Qt/Components/DICOMListingTable`).

**What is net-new (navigation + interop layer — the actual Goal 2 deliverable):**
- **Pluggable data-source abstraction + explorer UI** — no dataset browser exists anywhere in `GUI/`
  (file-open is native `QFileDialog` only; `QFileSystemModel` is imported but never instantiated). Build
  a source interface `{ list(path) → entries, stat, open }` with backends for local FS, SSH (add
  `sftp_readdir` **directory listing** — today only single-file `stat/open/read` exists), and Flywheel
  (the REST hierarchy-resolution logic in `FlywheelRemoteImageSource.cxx:221-399` is directly reusable
  for a project/subject/session tree). DICOM/BIDS-aware.
- **BIDS awareness** — none today (0 repo matches). Recognize BIDS layout + sidecars for browsing.
- **Agent-callable browse/open** — expose the source abstraction as `headless.*` MCP tools so an agent
  can enumerate and open remote data without local download (grant success indicator 2.1).
- **Multi-workspace management (Year 2)** — today ITK-SNAP is one-workspace-per-process ("open in new
  window" spawns a child process, `MainImageWindow::LoadProjectInNewInstance` →
  `SystemInterface::LaunchChildSNAPSimple`). Holding several workspaces in one explorer is net-new and
  cuts against the singleton `IRISApplication` assumption — scope carefully.
- **DICOM-SEG interoperability (Year 2, 4.10)** — *genuinely net-new subsystem.* No
  `dcmqi`/`DCMTK`/SEG code exists; segmentations save through the same `GuidedNativeImageIO::SaveImage`
  path as scalar images and carry **only integer label values** — names/colors live separately in
  `ColorLabelTable` + workspace registry. DICOM-SEG closes exactly that gap. Work items: a new
  `FileFormat` enum member (`GuidedNativeImageIO.h:68-77`) + registry row, a new ImageIO/delegate (via
  `dcmqi` + `DCMTK`; note ITK already bundles GDCM but **not** DCMTK/dcmqi), and a
  `ColorLabelTable ↔ SEG segment` metadata mapping (anatomy codes, colors). Round-trip validated against
  3D Slicer (success indicator 2.3). **Strong existing scaffolding to imitate:** the recent
  export-time metadata curation + PHI allow-list (`CurateDicomDictionaryForExport`,
  `GuidedNativeImageIO.cxx:417-439`) and the namespaced `ITKSNAP_*` round-trip keys.

### 2.5 Cross-cutting architecture

- **Distribution (decision, §5):** pip-ship **only** Layer-1 `pysnap` + the MCP server as thin wheels
  (cibuildwheel, the greedy_python pattern) — small, auto-updatable, and the surface whose downloads are
  cleanly measurable. Keep the **GUI on a native signed/notarized installer** (the 3D Slicer precedent;
  a Qt+VTK+ITK GUI wheel is high-cost/low-value — PyPI size limits, Qt plugin discovery, GL context,
  Gatekeeper, LGPL). Solve version drift with a **protocol-version handshake** (semver +
  `min_compatible_version`, probing `/status`), not a mega-wheel.
- **Testing:** the grant's headline success indicator is "passes the existing automated test harness"
  (CTest / `SNAPTestQt`). New Python surfaces get pytest suites (the greedy_python model). The live
  channel reuses the harness primitives, so its tests are natural extensions of `SNAPTestQt`.
- **Metrics:** pip-only, CI-excluded, mirror-filtered download counts via `pypinfo`/BigQuery; reported
  honestly as "downloads," GUI installer counts reported separately.

---

## 3. Capability ledger (exists / thin-wrapper / net-new)

| # | Building block | Goal | Status | Anchor / what's missing |
|---|---|---|---|---|
| 1 | Qt-free Logic tier (Layer-1 substrate) | 1 | **EXISTS** | `Logic/`=0 Qt incl.; `CMakeLists.txt:1228` |
| 2 | Headless workspace/label/tag ops | 1 | **EXISTS** | `WorkspaceAPI.{h,cxx}`; proven by `itksnap-wt` |
| 3 | Voxel-space cursor + label edits (undo-tracked) | 1 | **EXISTS** | `IRISApplication.h:485,621`; `SegmentationUpdateIterator.h` |
| 4 | DLS inference: interactive + automatic + 4D | 1 | **EXISTS** | dls `feature/agentic-api` registry (`models.py:208-312`) |
| 5 | Async job (submit→poll→result) | 1 | **EXISTS** | dls `modules/propagation/jobs.py` |
| 6 | Property/event observation of app state | 1 | **EXISTS** | `PropertyModel.h`; no runtime reflection |
| 7 | Semantic widget addressing + event injection | 1 | **THIN** | `SNAPTestQt.cxx` — exists, test-scoped only |
| 8 | GL slice-view screenshot | 1 | **THIN** | `SliceViewPanel::SaveScreenshot` exists, unbound |
| 9 | Layer-1 Python binding (`pysnap`) | 1 | **NET-NEW** | copy greedy_python; +RLEImage converters |
| 10 | Live command channel (RPC into running GUI) | 1 | **NET-NEW** | `QLocalServer` in `main.cxx` → SNAPTestQt slots |
| 11 | Audit/provenance record + serializer | 1 | **NET-NEW** | metadata over `UndoDataManager` |
| 12 | `request_review` resumable handoff | 1 | **NET-NEW** | model on DSS state machine, same-process |
| 13 | MCP server (unified namespace) | 1+2 | **NET-NEW** | no skeleton exists |
| 14 | Expert-interaction capture → retrain loop | 1 | **NET-NEW** | Year-2; consumes #11 |
| 15 | Remote/cloud transport (fw/scp/http, remote ws) | 2 | **EXISTS** | `FlywheelRemoteImageSource`, `ImageIORemote`, `RemoteFileCache` |
| 16 | Reusable REST/SSH transport | 2 | **EXISTS** | `RESTClient.{h,cxx}`, `SSHTunnel.{h,cxx}` |
| 17 | DICOM read + series grouping | 2 | **EXISTS** | `GuidedNativeImageIO.cxx:2745`; GDCM |
| 18 | Remote **directory browsing** (dir listing) | 2 | **NET-NEW** | add `sftp_readdir`; Flywheel tree from reusable logic |
| 19 | Dataset explorer UI (pluggable backends) | 2 | **NET-NEW** | no browser widget in `GUI/` |
| 20 | BIDS awareness | 2 | **NET-NEW** | 0 repo matches |
| 21 | Multi-workspace management | 2 | **NET-NEW** | Year-2; one-ws-per-process today |
| 22 | DICOM-SEG read/write (validated round-trip) | 2 | **NET-NEW** | no dcmqi/DCMTK; new format+delegate+label map |
| 23 | pip wheels (API/MCP) + version handshake | X | **THIN** | greedy_python proves the wheel path |

**One-line read:** both transport/data planes EXIST; the net-new work is a Python skin, a live-GUI RPC,
an audit record, an MCP server, an explorer/browse layer, and a DICOM-SEG subsystem — each small and
independently testable except DICOM-SEG (a real new subsystem) and multi-workspace (an architectural
stretch).

---

## 4. Two-year roadmap (release-aligned)

Mapping to grant milestones in brackets. Critical-path items in **bold**.

### Year 1 → ITK-SNAP 4.8

**Q1 — de-risk the atoms (parallelizable, cheap-first).**
- **Audit-record serializer** over `UndoDataManager` [→1.1]. *(cheapest; de-risks the Year-2 schema)*
- **Live command channel** prototype: `QLocalServer` in `main.cxx` forwarding to SNAPTestQt slots
  [→1.1]. *(hardest; start early)*
- `pysnap` skeleton: workspace open/save + apply-mask + cursor, greedy_python recipe [→1.1].
- DLS thin HTTP client, verified against the `feature/agentic-api` server (`/status` handshake).
- Goal-2 spike: generalize the existing remote-IO sources into a `DataSource` interface; add
  `sftp_readdir` directory listing [→2.1].

**Q2 — assemble Goal 1 + start the explorer.**
- **MCP server**: `headless.*` + `live.*` namespaces, `session` object [→1.1].
- **`request_review`** primitive wired to the confidence-gate → live-handoff → audited-return flow [→1.1].
- Explorer UI v1: local FS + SSH + Flywheel tree, DICOM/BIDS-aware; agent-callable browse/open [→2.1].
- Demo-video suite (from the prototype plan) recorded for dissemination.

**Q3 — harden + BIDS + integrate.**
- BIDS recognition in the explorer [→2.1]; polish remote browse.
- Pass the existing CTest / SNAPTestQt harness with the new surfaces (success indicator).
- Begin YouTube tutorials + dev docs for the headless API and MCP [→3.2, 3.4].

**Q4 — ship 4.8.**
- pip-publish `pysnap` + MCP wheels; native installer for the GUI; protocol handshake in place.
- **Release ITK-SNAP 4.8** carrying both 1.1 (headless API + `request_review`) and 2.1 (remote
  data-access + explorer). *(The shared 4.8 train is a grant open item — §9.)*

### Year 2 → ITK-SNAP 4.10

**Q1–Q2 — Goal 1 improvement loop + multi-workspace.**
- Finalize the **expert-interaction capture format** (machine-consumable, provenance-tagged records) [→1.2].
- **Working across multiple datasets/workspaces** from the explorer, agent-accessible [→2.2].

**Q2–Q3 — DICOM-SEG + validate.**
- **DICOM-SEG read/write** subsystem (dcmqi/DCMTK; new `FileFormat` + delegate + `ColorLabelTable ↔ SEG`
  mapping); **round-trip validated against 3D Slicer** [→2.3].
- **Benchmark the value of expert correction**: report improvement vs. baseline + routing-vs-random
  efficiency on a public dataset (e.g., MM-WHS cardiac CT / MSD hippocampus); release the harness [→1.3].
- **Release ITK-SNAP 4.10** with multi-workspace + validated DICOM-SEG interop.

**Q4 — community + sustainability.**
- **Hybrid training + contributor hackathon** event [→3.1]; complete dev docs [→3.4]; sustained
  tutorials + social presence across both years [→3.2, 3.3].

### Critical paths (what gates what)

- **Goal 1 spine:** live command channel → `request_review` → expert-interaction capture → model-improvement
  loop. *The channel gates every live/on-camera capability and the Year-2 training signal — start it in Q1.*
- **Goal 2 spine:** `DataSource` abstraction + directory browsing → explorer UI → (multi-workspace; DICOM-SEG).
- **Independent, low-risk, do-anytime:** audit serializer, DLS thin client, tutorials/docs.

---

## 5. Key architectural decisions

| # | Decision | Status | Consequence |
|---|---|---|---|
| D1 | **Handoff = drive the human's ONE live GUI process** (not headless+ingest hook) | Locked (prototype §0.1) | Makes the live command channel (2.2b) the Layer-2 spine; rules out cross-process image hand-off |
| D2 | **Programmatic edits go through the voxel API, never pixel math** | Locked | `SetCursorPosition`+`UpdateSegmentationWith*`; canvas mouse events reserved for when a raw click *is* the visual |
| D3 | **Automatic segmentation is an async JOB, not an interactive session** | In code | TotalSegmentator/4D route through `jobs.py`; interactive models stay synchronous |
| D4 | **Audit record starts minimum-viable, extends later** | Locked | `{op,timestamp,agent/human,voxel count,bbox,label counts}`; later: per-label Dice, reason string, model id |
| D5 | **pip-ship API/MCP only; GUI stays a native installer; drift solved by handshake** | Recommended | 3D Slicer precedent; clean download metrics on the pip surface |
| D6 | **Run itksnap-dls `feature/agentic-api`** (supersedes the prototype's `features/segflow4d`) | Updated this session | v2+legacy routes; carries TotalSegmentator + async jobs; pin in the demo manifest |
| D7 | **DICOM-SEG via dcmqi/DCMTK, imitating the existing metadata-curation + `ITKSNAP_*` round-trip pattern** | Proposed | Adds a new external dep (DCMTK) not currently in the stack; scope in Year-2 planning |
| D8 | **Goal-2 explorer reuses the shipped remote-IO transport; net-new is navigation + UI only** | Proposed (§9) | De-risks Year-1 2.1; strengthens the "integration not greenfield" claim |

---

## 6. Risks & what to verify before committing

1. **[Hardest · gates Goal 1] Live command channel.** Verify a `QLocalServer` can inject
   `QApplication::postEvent`/method-invokes into the **running** loop after launch, without the `--test`
   scaffold (`main.cxx:1443` runs canned JS *before* `exec()`). *Prototype in Q1.*
2. **[Real subsystem] DICOM-SEG.** New external dependency (DCMTK/dcmqi) absent from the build today;
   the `ColorLabelTable ↔ SEG` semantic mapping (anatomy codes) is non-trivial. *Spike a one-label
   round-trip vs 3D Slicer before scoping 2.3.*
3. **[Architectural stretch] Multi-workspace** cuts against singleton `IRISApplication` (one-ws-per-process).
   Decide early: true in-process multi-session vs. an explorer that *manages* multiple child processes.
4. **[Favorable, verify] Headless voxel edits without GL/Qt.** `itksnap-wt` proves Qt-free *metadata*
   linking; build a tiny L1 binary that loads → paints via `SegmentationUpdateIterator` → saves, linking
   `itksnaplogic` alone (compile-guard the two optional VTK touch-points).
5. **[Determinism] Recording/agent flakiness** (for the demo suite): fixed inputs + canned seeds + golden
   masks; poll-until-condition instead of `sleep`; scripted demo driver over free-form prompting.
6. **[Packaging] RLEImage/LabelImageWrapper converters** for pybind11 beyond greedy_python's base types.
7. **[Licensing] nnInteractive weights are non-commercial** — fine for the grant demo, a known liability
   for a commercial product; plan the clean-weight migration (TotalSegmentator-core/SegVol/VISTA3D-NV).

---

## 7. Success indicators → architecture mapping

| Grant success indicator | Delivered by |
|---|---|
| 4.8 released with headless API + `request_review`; passes test harness [1.1] | §2.2 a/b/d/e + §2.5 testing |
| Expert interactions captured [1.2]; value of correction benchmarked vs. baseline + routing-vs-random, harness released [1.3] | §2.2c + §2.3 |
| 4.8 remote data access; remote dataset browsed+segmented without local download [2.1] | §2.4 (transport EXISTS + explorer/browse NET-NEW) |
| 4.10 agent-accessible work across multiple datasets/workspaces [2.2] | §2.4 multi-workspace |
| 4.10 DICOM-SEG round-trip validated vs 3D Slicer, fidelity documented [2.3] | §2.4 DICOM-SEG |
| Hybrid event, tutorials, docs, contributors [3.1–3.4] | §4 Year-2 Q4 + ongoing |

---

## 8. Recommendations to the grant reviser

1. **Reword Goal 2 milestone 2.1** to reflect reality: the remote/cloud **transport** (Flywheel, SSH,
   HTTP, remote workspaces, caching) already ships; 2.1 delivers a **browsable explorer + agent API on
   top of it**. This is the stronger, more defensible claim and de-risks Year 1.
2. **Confirm the shared 4.8 train** (open item in the draft): both 1.1 and 2.1 currently land in 4.8. The
   architecture supports it (both are additive), but if the reviewer prefers distinct version numbers per
   goal, split into 4.8 (Goal 1) / 4.9 (Goal 2) — a labeling choice, not an engineering one.
3. **Name the new external dependency (DCMTK/dcmqi)** for DICOM-SEG in the Year-2 plan; it is the one
   milestone that adds a dependency not currently in the stack.
4. **Fill the `[N]` targets** in success indicators (event participants, tutorial count/views, contributors).
5. **Create the GitHub Milestones (4.8, 4.10)** before submission so "published roadmap" is literal.

---

## Appendix — key file references

- **Boundary / build:** `itksnap/CMakeLists.txt:94-101` (version), `:1228-1234` (library targets);
  `itksnap/Utilities/Workspace/` (`itksnap-wt` headless proof).
- **Layer-1 substrate:** `itksnap/Logic/WorkspaceAPI/WorkspaceAPI.{h,cxx}`;
  `itksnap/Logic/Framework/{IRISApplication.h, SegmentationUpdateIterator.h, GlobalState.h,
  UndoDataManager.{h,txx}}`.
- **Live-GUI channel:** `itksnap/Testing/GUI/Qt/SNAPTestQt.{h,cxx}`; `itksnap/GUI/Qt/main.cxx:732-746,1443-1446`;
  screenshot `itksnap/GUI/Qt/Components/SliceViewPanel.{h:58,cxx:489}`.
- **Model plane (dls `feature/agentic-api`):**
  `itksnap-dls/itksnap_dls/modules/segmentation/{models.py:208-312, router.py, session.py}`,
  `modules/propagation/jobs.py`, `server.py`.
- **Remote/data plane:** `itksnap/Logic/ImageWrapper/{FlywheelRemoteImageSource.{h,cxx},
  ImageIORemote.{h,cxx}, SSHConnectionPool.{h,cxx}, RemoteFileCache.{h,cxx}}`;
  `itksnap/Logic/WorkspaceAPI/{RESTClient.{h,cxx}, SSHTunnel.{h,cxx}}`;
  `itksnap/Logic/Framework/IRISApplication.cxx:2337+`; spec `itksnap/Documentation/Developer/RemoteURLs.md`.
- **DICOM / interop:** `itksnap/Logic/ImageWrapper/GuidedNativeImageIO.{h:68-77,cxx:449-471,2745-2882,417-439}`;
  `itksnap/Logic/Common/{MetaDataAccess.cxx, SNAPRegistryIO.cxx}`; `ColorLabelTable`
  (`IRISApplication.cxx:118-122`); adjacent scaffolding `projects/4dcta_improvement/`.
- **Binding template:** `greedy_python/{CMakeLists.txt, src/GreedyPythonBindings.cxx, src/picsl_greedy/_greedy_api.py}`.
- **Companion planning docs:** `projects/os4ls_grant/work_plan_draft.md`;
  `projects/agentic-api/docs/agentic-prototype-plan.md`.
