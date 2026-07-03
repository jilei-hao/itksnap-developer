# ITK-SNAP Agentic API — Prototype Plan

*Planning document. No implementation or scaffolding was produced this session.*
*"Model proposes, human disposes" — expose **expert human judgment** as a callable, resumable, audited pipeline step an external agent can invoke, and make that step visible on camera.*

All paths are relative to the wrapper repo root `/Users/jileihao/dev/itksnap-dev/itksnap-developer/` unless noted. Every capability claim below is tied to a real file and line range that was read during orientation.

---

## 0. Executive summary (read this first)

The single most important finding: **the headless data plane already exists in C++ and is 100% Qt-free**, proven today by the `itksnap-wt` binary. The differentiator the grant is about — *expert judgment as a callable/resumable/audited step* — is **not blocked by missing image processing**. It is blocked by three small, independently testable NET-NEW pieces:

1. **A Python skin (Layer-1)** over the existing Qt-free Logic tier — no bindings exist today, but the exact recipe is proven next door in `greedy_python`.
2. **A live external command channel (Layer-2)** — the JS test harness (`SNAPTestQt`) already does semantic widget addressing + event injection + image-space cursor control, but only from a canned `.js` file launched via `--test` *before* the event loop starts. Turning it into a live RPC surface is the core Layer-2 work.
3. **An audit record** — the undo engine already captures per-operation voxel deltas, but has no timestamp/identity/op-type/export. Provenance metadata on top of it is net-new but small and localized.

The recommended flagship (**P1: "Uncertain case routed to the human"**) is an *integration* of those three atoms plus existing code. The recommended build order front-loads the two cheapest atoms (audit record, live channel) so the flagship becomes an assembly job rather than a leap.

**The biggest unresolved architectural decision** (needs your input, see §7): does the agent drive edits *into the human's one running GUI process* (favored), or do a headless agent process and a separate GUI process exchange images through a hook? This choice shapes the entire session-lifecycle design.

---

## 1. Workspace map

Wrapper meta-repo aggregating ITK-SNAP + 7 sibling submodules, each on its own branch (`.gitmodules`). Build artifacts sit at root (`build-release/`, `build-debug/`, `build-greedy/`, `build-cmrep/`, `build-convertmesh/`).

| Sub-project | Path | Language / build | Role for the agentic API | Maturity |
|---|---|---|---|---|
| **ITK-SNAP** | `itksnap/` (branch `feature/cardiac-io`) | C++17, CMake/Ninja; ITK 5.4, VTK 9.3, Qt6 | **Core.** Layer-1 substrate (Logic tier) + Layer-2 target (live GUI) | Mature, builds locally (`build-release/`) |
| **itksnap-dls** | `itksnap-dls/` | Python 3.10+, FastAPI + PyTorch + nnInteractive; `pyproject.toml` | **The model server** the agent calls. v0.0.10 | Runnable; small (~550 LOC Python) |
| **greedy_python** | `greedy_python/` (branch `test/integration`) | Python + pybind11 + scikit-build-core | **The binding pattern to copy** for Layer-1 (not itself Layer-1) | Working (`picsl_greedy` v0.0.12, 14/15 tests pass) |
| convert-mesh | `convert-mesh/` | C++17, ITK+VTK | Not on the critical path | Builds |
| cmrep | `cmrep/` (branch `local`) | C++17 | Not on critical path | Builds |
| FireANTs | `FireANTs/` | Python, torch/GPU | Registration backend; out of scope for MVP | v1.5.0 |
| segflow4d | `segflow4d/` | Python; torch + fireants + vtk | 4D propagation; out of scope for MVP | v1.1.3 |

**Two executables ITK-SNAP already ships** (`itksnap/CMakeLists.txt`, `Utilities/Workspace/CMakeLists.txt`):
- `ITK-SNAP` — the GUI (`GUI/Qt/main.cxx`).
- `itksnap-wt` — headless CLI workspace tool (`Utilities/Workspace/WorkspaceTool.cxx`, ~1194 lines). **Links only `itksnaplogic + ITK + CURL`, zero Qt** — this is the existence proof that a Qt-free Layer-1 binary is achievable today.

**Three internal libraries** define the clean tier boundary (`itksnap/CMakeLists.txt:1227-1243`):
- `itksnaplogic` — Logic tier, ITK + VTK-non-rendering, **no Qt**.
- `itksnapui_model` — GUI/Model presenter tier, adds VTK rendering, **still no Qt**.
- `itksnapui_qt` — GUI/Qt view tier, adds Qt.

### Exact itksnap-dls run invocation (for reproducibility)

From `itksnap-dls/itksnap_dls/__main__.py:9-64,140-182` and `docs/quick_start.md`:

```bash
# From the itksnap-dls checkout (deps: fastapi, nnInteractive, torch, huggingface_hub):
python -m itksnap_dls \
  --port 8911 \            # -p ; default 8911
  --host 0.0.0.0 \         # -H ; default 0.0.0.0
  --device cuda \          # cuda | cpu | mps ; auto-detects CUDA else CPU
  --models-path <dir>      # -m ; HuggingFace cache for the model
# First run downloads nnInteractive/nnInteractive (model "nnInteractive_v1.0") from HuggingFace.
# --setup-only downloads the model and exits (good for pre-baking a demo image/cache).
# -k skips HTTPS verify; -N enables ngrok (needs NGROK_AUTHTOKEN).
```

At startup the server pre-warms one nnInteractive session (`server.py:56-62`) so the first `/start_session` is fast; each `/start_session` schedules another pre-warm.

---

## 2. Orientation report (grounded, with corrections to the original notes)

### 2.1 Headless workspace ops — **EXISTS, Qt-free** (Layer-1 substrate)

`Logic/WorkspaceAPI/WorkspaceAPI.{h,cxx}` (298 h / 1372 cxx) is a Registry-backed, **zero-Qt** class over the `.itksnap` XML format:
- I/O: `ReadFromXMLFile`/`SaveAsXMLFile` (`WorkspaceAPI.cxx:21-64`).
- Layer CRUD: `AddLayer` (`cxx:792`), `SetLayer` (`cxx:825`), enumeration via `HasFolder("Layers.Layer[%03d]")` (`cxx:66-85`).
- Labels/tags: `SetLabels` (`cxx:982`), `AddTag`/`FindLayersByTag` (`h:129,163`).
- Export/cloud: `ExportWorkspace` (`cxx:1099`), `CreateWorkspaceTicket`/`DownloadTicketFiles` (`cxx:1258`).

**Correction to notes:** WorkspaceAPI manipulates **paths + metadata only — it never touches pixels.** All image I/O is delegated to `GuidedNativeImageIO` through `IRISApplication`. It is the right Layer-1 *entry* for workspace assembly, but voxel work happens through `IRISApplication`/`ImageWrapper` (below).

### 2.2 Headless proof — `itksnap-wt` (Layer-1 existence proof)

`Utilities/Workspace/WorkspaceTool.cxx:76-1194` exercises every headless op (layer I/O `-i/-o/-a`, labels `-labels-set`, tags, timepoints, DSS tickets `-dss-tickets-create`) with no GUI. Build recipe `Utilities/Workspace/CMakeLists.txt`: `itksnaplogic + ITK + CURL`, **no Qt, no rendering.**

### 2.3 The Qt boundary — **Logic is 100% Qt-free; Model is 99.8% Qt-free**

From the boundary sweep (`itksnap/CMakeLists.txt:1128-1163,1227-1243`):
- `Logic/` — all 11 subdirs, **zero `#include <Q...>`.** Two *optional VTK* touch-points: `Logic/Slicing/IntensityCurveVTK.h` (`vtkKochanekSpline`) and `Logic/Mesh/VTKMeshPipeline.h` (marching cubes). Neither is Qt; both are compile-guardable.
- `GUI/Model/` — **zero Qt.** Only `PaintbrushModel.h:6-7` includes `vtkSmartPointer`/`vtkPoints2D` (2D brush geometry, not rendering).
- `GUI/Qt/` — all 147+ Qt includes live here and only here.

**Correction to notes:** Rendering does **not** live in `GUI/Model/` — it is entirely in `GUI/Renderer/` (65 files). And the DL model does **not** pull in Qt for threading (see 2.5). So the "which GUI-Model headers pull in Qt" hypothesis resolves to: essentially none. A clean Layer-1 library is a **~1–2 week build-config + stub effort**, not a rewrite.

### 2.4 Image-space voxel editing — **EXISTS in Logic, NOT entangled with the GUI**

This is the crux of the GUI-driving strategy and the finding is strongly favorable:
- `IRISApplication::SetCursorPosition(const Vector3ui cursor, bool force=false)` / `GetCursorPosition() const` (`IRISApplication.h:485,490`) — **cursor is set in voxel coordinates via public Logic API.**
- `SegmentationUpdateIterator` (`Logic/Framework/SegmentationUpdateIterator.h:55-220`) — `PaintLabel()`, `PaintAsForeground/Background()`, `ReplaceLabel()` mutate the label image voxel-by-voxel with draw-over filtering and automatic undo-delta capture.
- `IRISApplication::UpdateSegmentationWithBinarySegmentation(...)` (`h:621`) and `UpdateSegmentationWithSliceDrawing(...)` (`h:610`) — apply a whole mask / slice drawing in image space (the latter already used by polygon and DL modes).
- Seeds/bubbles for level-set: `GlobalState::GetBubbleArray/SetBubbleArray/SetActiveBubble` (`Logic/Framework/GlobalState.h:183-192,338-362`), centers already in voxel indices.

**Correction to notes:** Segmentation edits are **not** entangled with GUI mouse handlers. `GUI/Qt/View/PaintbrushInteractionMode.cxx:26-83` only translates pixel→voxel then calls `PaintbrushModel::ApplyBrush` (`GUI/Model/PaintbrushModel.cxx:301-416`), which calls the same Logic APIs above. **Recommendation confirmed: drive all programmatic edits through the voxel API, never pixel math.** Setting the cursor fires `CursorUpdateEvent`, which ripples up through the ITK event chain and re-renders the live slice — so an agent that calls `SetCursorPosition` gets the GUI to follow for free.

### 2.5 The DLS path (the model the agent calls) — **EXISTS, synchronous**

**Server** (`itksnap-dls/itksnap_dls/server.py`, v0.0.10) — FastAPI, in-memory UUID session dict (`session.py:6-25`). Real routes, verbatim:

| Method + path | Payload | Response |
|---|---|---|
| `GET /status` | — | `{status:"ok", version}` |
| `GET /start_session` | — | `{session_id}` (pre-warmed nnInteractive session) |
| `POST /upload_raw/{session_id}` | `file` = gzip(float32 raw), `metadata` = JSON `{dimensions:[z,y,x]}` | `{message}` — image into GPU memory |
| `GET /process_point_interaction/{session_id}?x&y&z&foreground` | voxel index x,y,z (ITK order) + fg/bg bool | `{status, result: base64(gzip(int8 mask))}` |
| `POST /process_scribble_interaction/{session_id}` | `file` = gzip mask image + `metadata` + `foreground` | mask |
| `POST /process_lasso_interaction/{session_id}` | same as scribble | mask |
| `GET /reset_interactions/{session_id}` | — | `{status}` |
| `GET /end_session/{session_id}` | — | `{message}` |

The nnInteractive prompt interface **is voxel coordinates** — no screen pixels anywhere. Note the coordinate reversal at the server boundary: `segment.py:91-93` does `tuple(index_itk[::-1])`, and `read_sitk_image` reverses `dimensions` (`server.py:91`). Point prompts arrive in ITK x,y,z order.

**Correction to notes (important):** DLS is **synchronous** — request → inference → immediate gzipped mask. **There is no ticket/poll/resume on DLS.** The submit→poll→`?since=lastlog_id`→download machinery belongs to a *different* subsystem (DSS, see 2.6). Do not conflate them.

**⚠ Client/server version mismatch — VERIFY before writing the demo client.** The shipped GUI client (`GUI/Model/DeepLearningSegmentationModel.cxx`) targets a **newer `v2/` API** than the local server exposes:

| Operation | GUI client calls (`DeepLearningSegmentationModel.cxx`) | Local server exposes (`server.py` v0.0.10) |
|---|---|---|
| status | `Get("status")` (`:659`) | `/status` ✅ |
| list models | `Get("v2/models")` (`:734`) | *(none)* ❌ |
| start | `Get("v2/start_session/%s", model_id)` (`:817`) | `/start_session` (no model_id) ❌ |
| upload | `PostMultipart("upload_raw/%s?filename=...")` (`:935`) | `/upload_raw/{id}` ✅ (no `filename` param) |
| point | `Get("v2/process_point_interaction/%s?point=%d&point=%d&point=%d&foreground=%s")` (`:1168`) | `/process_point_interaction/{id}?x&y&z&foreground` ❌ (param names differ) |
| reset | `Get("reset_interactions/%s")` (`:973`) | `/reset_interactions/{id}` ✅ |
| end | `Get("v2/end_session/%s")` (`:804`) | `/end_session/{id}` ✅ |

**Implication:** the local `itksnap-dls` checkout and the current GUI are not directly compatible. The demo's thin Python client must be written against **whichever server binary is actually run for the recording**, verified by probing `/status` (version) and the route shape. Pin one server version in the demo manifest; do not assume the table above will hold after a submodule bump.

### 2.6 Async ticket / resume — **EXISTS as DSS (a candidate analog for `request_review`)**

`GUI/Model/DistributedSegmentationModel.{h,cxx}` is a textbook resumable primitive, separate from DLS:
- States `STATUS_INIT/READY/CLAIMED/SUCCESS/FAILED/TIMEDOUT` (`.h:139-141`).
- `AsyncGetTicketListing` (`.cxx:935`), `AsyncGetTicketDetails` (`.cxx:1022`) polling `api/tickets/{id}/detail?since={lastlog_id}` for incremental log/progress.
- `UniversalTicketId = (server_url, ticket_id)` (`.h:198`) — a durable handle that survives restarts.

This is the pattern to model a resumable "human review request" on (park a case, poll for the human's verdict) — but it is DSS-shaped (submit→poll→download), whereas the live-correction demo wants an interactive same-session handoff. See P3 vs P1 in §4.

### 2.7 Property/event system — **EXISTS, Qt-free** (how the agent observes app state)

`Common/PropertyModel.h:504-604` (`AbstractPropertyModel<TVal,TDomain>`), `Common/SNAPEvents.h:105-108` (`ValueChangedEvent`/`DomainChangedEvent`), `Common/AbstractModel.{h,cxx}` + `EventBucket` (batched delivery). `GlobalUIModel::GetCursorPositionModel()` etc. expose live state (cursor, label, tool mode) with ITK observers — no Qt required. **Gap:** no runtime *enumeration/reflection* of all properties; an agent reads named getters, it cannot "list all state" generically.

### 2.8 GUI test harness `SNAPTestQt` — **the Layer-2 foundation** (stronger than the notes assumed, but test-scoped)

`Testing/GUI/Qt/SNAPTestQt.{h,cxx}` runs JavaScript in an embedded `QJSEngine`, on a `TestWorker` QThread, with the whole UI bound into JS (`mainwin`, `engine`, `datadir` globals, `SNAPTestQt.cxx:35-59`). Exposed to scripts:
- **Semantic addressing:** `findChild(parent,"objectName")` (`cxx:88`), `findWidget(name)` (global search, `cxx:93`).
- **Property/method access:** QJSEngine binds `Q_PROPERTY`/slots directly — `btn.click()`, `field.text="200"`, `grp.visible` (seen in `Scripts/test_4DReplayWithMeshUpdate.js`).
- **Actions:** `trigger("actionOpenMain")` (`cxx:148`), `invoke(obj,"slot")` (`cxx:139`), `comboBoxSelect` (`cxx:154`).
- **Event injection:** `postMouseEvent(widget, rel_x, rel_y, type, button)` (`cxx:315`) and `postKeyEvent(obj,"Space")` (`cxx:351`) via real `QApplication::postEvent`.
- **State read:** `tableItemText(table,row,col)` (`cxx:103`), and the `Library.js` idioms `setCursor(x,y,z)`/`setCursor4D(...)` (sets the coupled `inCursorX/Y/Z` voxel spinboxes), `readVoxelIntensity(row)`, `setForegroundLabel(name)`, `enterSnakeMode(pos,size)`.

**Corrections to notes:**
- It is **far more than button clicks** — full Qt property read/write + real event injection. And it already drives edits in **image space** via `setCursor` (voxel spinboxes), not just pixels.
- But `postMouseEvent` takes **relative 0.0–1.0 widget coordinates, not pixels** (`cxx:315`). To hit a specific voxel on the OpenGL canvas via a mouse event you would need camera-matrix math — which is exactly why the **image-space cursor+paint API (2.4) is the right path** and canvas mouse events should be reserved for when showing a raw click *is* the point.
- **It is test-scoped, not a live RPC.** It runs a canned `.js` (from `:/scripts/` or disk) in a thread launched by `--test TESTID --testdir DIR` *before* `QApplication::exec()` (`GUI/Qt/main.cxx:732-746,1443-1446`). There is **no external command channel** today. Converting this into a live socket/stdin RPC that injects into the running event loop is the central Layer-2 net-new task.
- `SliceViewPanel::SaveScreenshot(std::string)` **exists** (`GUI/Qt/Components/SliceViewPanel.h:58`, `.cxx:489`) but is **not bound to the JS engine** — exposing it is a ~1-line binding, not new C++.

### 2.9 Undo/edit history — **EXISTS as a delta engine, NOT an audit trail**

`Logic/Framework/UndoDataManager.{h,txx}` stores RLE label-delta commits (`.h:48-117`); each commit carries a name (e.g. "Paint Brush"); memory-bounded pruning (`.txx:131-176`). `LabelImageWrapper::StoreUndoPoint(text, delta)` commits after an edit; `IRISApplication::UpdateSegmentationWithSliceDrawing` finalizes with an undo title (`.cxx:577-673`).

**Correction to notes:** this is provenance-*capable* but not an audit trail. Gaps: commit `m_Name` is `protected` with **no public getter**; **no timestamp, user/agent identity, op-type, parameters, or before/after voxel counts**; in-memory only, **no export**; `SegmentationChangeEvent` (`SNAPEvents.h:73`) carries no payload. A real audit record = small, localized net-new metadata + a JSON serializer on top of the existing delta.

### 2.10 Python bindings — **NET-NEW for ITK-SNAP; recipe proven in `greedy_python`**

Confirmed: **zero `python|pybind|swig` in `itksnap/CMakeLists.txt`.** The pattern to copy: `greedy_python/CMakeLists.txt` (pybind11 + scikit-build-core), `greedy_python/src/GreedyPythonBindings.cxx:65-245` (SimpleITK⇄ITK image import/export with metadata), `src/picsl_greedy/_greedy_api.py` (Pythonic facade returning NamedTuples). **Caveat:** those converters cover *base* ITK image types; ITK-SNAP's `RLEImage`/`LabelImageWrapper` need new template specializations. The DLS demo client, by contrast, needs **no ITK at all** (pure HTTP + gzip + base64), so it can ship as plain Python before any pybind11 work.

### 2.11 Remote transport — **EXISTS, Qt-free** (reusable)

`Logic/WorkspaceAPI/RESTClient.{h,cxx}` (libcurl, `ServerTraits` pattern; `DLSServerTraits` uses an in-memory URL and shares cookies, `cxx:916-938`) and `SSHTunnel.{h,cxx}` (libssh port forwarding, `cxx:21-376`). Both Qt-free; usable as the MCP↔dls transport or to tunnel a remote server. **Correction to notes:** `DLSServerTraits` stores the URL **in memory per instance** and *includes* cookies in the CURL share; the file-based global-URL behavior belongs to `DSSServerTraits`.

### 2.12 What is NOT headless

Segmentation *algorithms* (snake/level-set, random forest) are **GUI-triggered** — `InitializeActiveContourPipeline` needs interactive parameter preview (`IRISApplication.h:199-204`). So "headless segmentation" in this project means **external proposals** (DLS/nnInteractive, or greedy registration) applied via `UpdateSegmentationWith*`. Do not plan on running the built-in level set headlessly.

---

## 3. Capability map (per building block: EXISTS / THIN-WRAPPER / NET-NEW)

| Building block | Layer | Status | Evidence / what's missing |
|---|---|---|---|
| Headless workspace ops (layer/label/tag CRUD, load/save) | L1 | **EXISTS** | `WorkspaceAPI.{h,cxx}`; headless-proven by `WorkspaceTool.cxx` |
| Image I/O (DICOM/NIfTI/…) | L1 | **EXISTS** | `GuidedNativeImageIO` via `IRISApplication` |
| Cursor set/get in voxel space | L1 | **EXISTS** | `IRISApplication.h:485,490` |
| Voxel/label edits, undo-tracked | L1 | **EXISTS** | `SegmentationUpdateIterator.h:55-220`; `UpdateSegmentationWithBinarySegmentation` `h:621` |
| Level-set seed placement (voxel) | L1 | **EXISTS** | `GlobalState.h:183-192,338-362` |
| DLS inference (point/scribble/lasso→mask) | L1→server | **EXISTS** | `itksnap-dls/server.py:64-236` (⚠ pin API version, §2.5) |
| Observe app state (cursor/label/mode) | L1 | **EXISTS** | `PropertyModel.h:504-604`; `SNAPEvents.h`; no reflection |
| Remote transport (HTTP/SSH) | L1 | **EXISTS** | `RESTClient.{h,cxx}`, `SSHTunnel.{h,cxx}` |
| Async ticket/poll/resume | — | **EXISTS (DSS)** | `DistributedSegmentationModel.cxx:935-1075`; DSS-shaped, not DLS |
| Semantic widget addressing + event injection | L2 | **THIN-WRAPPER** | `SNAPTestQt.cxx:88,315,351` — exists but JS/test-scoped, no live RPC |
| Screenshot GL slice view | L2 | **THIN-WRAPPER** | `SliceViewPanel::SaveScreenshot` exists (`h:58`), unbound to automation |
| Python entrypoint (Layer-1 binding) | L1 | **NET-NEW** | none in itksnap; copy `greedy_python` pattern |
| Live external command channel (RPC into running GUI) | L2 | **NET-NEW** | `SNAPTestQt` runs pre-`exec()` canned JS only |
| Audit record (timestamp/identity/op/diff, exportable) | L1 | **NET-NEW** | metadata + serializer over existing `UndoDataManager` |
| Agent→human handoff on one session | L1+L2 | **NET-NEW** | central design decision, §7 |
| MCP server (unified tool namespace) | L2 | **NET-NEW** | no skeleton anywhere |

**One-line read:** the headless data plane EXISTS; the Python skin, the live-GUI RPC surface, and a real audit trail are NET-NEW and each is small; the handoff is the one genuinely hard integration.

---

## 4. Prototype concepts (ranked by impact-per-effort)

Rule applied: **penalize any concept whose climax is "a model produced a mask."** The visible beat must be a human *overriding* on the live session, with a structured record flowing back.

### P1 — "Uncertain case routed to the human" — **the flagship / the thesis**
- **Demonstrates:** an external agent calls ITK-SNAP as a tool; DLS proposes; the agent's confidence gate flags an ambiguous case; control hands to the **same live GUI**; the expert corrects on camera; a structured, audited result returns to the agent.
- **Single wow beat:** the agent says *"I'm not sure — over to you,"* the live window snaps to the uncertain slice with the model's proposal already loaded, and the human paints the fix the agent then accepts and logs.
- **L1 vs L2:** L1 = load + DLS call + apply mask (`UpdateSegmentationWithBinarySegmentation`) + read audit; L2 = focus the live window (`SetCursorPosition` + `trigger`/`findChild`) and screenshot before/after.
- **Exists vs net-new:** propose + apply EXIST; **handoff orchestration + audit record + MCP tool are net-new.**
- **Effort: L. Risk:** the handoff on one live process (§7). **Thesis fit: bullseye** — callable + resumable + audited in one clip.

### P2 — "Callable expert correction as a diff" — **thinnest vertical slice**
- **Demonstrates:** `snap.propose()` → mask; human paints a fix in the live GUI; `snap.commit()` returns a **structured JSON audit record** (op name, changed-voxel count, bbox, before/after label stats) — the correction is a first-class *return value*, not a side effect.
- **Single wow beat:** split screen — brush stroke on the left; the JSON audit object materializing on the right the instant the mouse releases.
- **L1 vs L2:** L1 subscribes to `SegmentationChangeEvent`, reads the just-stored undo delta, emits JSON; L2 = the existing paintbrush pipeline.
- **Exists vs net-new:** delta capture EXISTS; **exposing commit name (`protected` today) + timestamp/count/bbox + JSON serialize is net-new (small).**
- **Effort: S–M. Risk:** touching `UndoDataManagerCommit` for a getter + provenance fields. **Thesis fit: bullseye on "audited"**; weaker on "resumable" alone — so it lives *under* P1, not instead of it.

### P3 — "Batch triage with a human queue" — **the resumable story (phase 2)**
- **Demonstrates:** agent submits N cases; easy ones auto-accept; hard ones land in a **resumable queue** the expert clears later, reusing the DSS ticket state machine.
- **Single wow beat:** a dashboard of tickets flipping `CLAIMED → SUCCESS` as the human clears the queue, progress driven by real `AsyncGetTicketDetails` polling.
- **Exists vs net-new:** ticket/poll/resume EXIST (DSS, `DistributedSegmentationModel.cxx`); **bridging DLS proposals into a DSS-style queue + a queue UI are net-new.**
- **Effort: M. Risk:** DSS and DLS are separate subsystems; bridging is real work. **Thesis fit:** strong on "resumable," weak on the *live on-camera correction* beat — a follow-on, not the opener.

### P4 — "Semantic vs pixel vs image-space addressing" — **L2 tech demo / P1 infrastructure**
- **Demonstrates:** the MCP driving the live GUI by widget name (`findChild("sliceViewInternalWidget0")`) with pixel-fraction fallback (`postMouseEvent(w,0.5,0.5)`), plus an image-space edit that bypasses pixels (`SetCursorPosition` in voxels).
- **Single wow beat:** the same edit performed two ways side by side — a fragile pixel click vs a robust voxel-space API call landing on the exact same voxel.
- **Exists vs net-new:** primitives EXIST but only inside the JS harness; **exposing them as a live RPC is net-new.**
- **Effort: M. Risk:** the pre-`exec()` test-thread architecture. **Thesis fit: weak** (plumbing, not judgment). **Build it as infrastructure for P1; don't ship it as a standalone clip** except to a technical reviewer audience.

### Ranking and justification (impact-per-effort)
1. **P2 (S–M)** — cheapest path to a *visible audited callable*, and it de-risks the exact audit-record format P1 needs. Highest ratio.
2. **P1 (L)** — the actual thesis; highest impact. Do it, but after P2 proves the audit record and P4 proves the live channel, so it's an assembly not a leap.
3. **P4 (M)** — necessary infrastructure for P1; ranked here only because it has no standalone "wow."
4. **P3 (M)** — great "resumable" story but drops the on-camera live-correction beat that makes the pitch land; phase-2 extension.

P2 and P4 are the two atoms P1 is built from (audit record + live channel). Building them first is what turns the flagship from a leap into an integration.

---

## 5. Recommended MVP + video suite

### 5.1 Flagship + thinnest end-to-end slice

**Flagship: P1.** The thinnest slice that tells the whole story (build P2 first; it *is* P2 wearing P1's clothes):

```
agent (MCP client)
 ├─ snap.open(case)                 L1  WorkspaceAPI.ReadFromXMLFile / IRISApplication            [EXISTS]
 ├─ snap.propose(seed_point)        L1→DLS  /start_session,/upload_raw,/process_point_interaction  [EXISTS — pin API ver]
 ├─ confidence gate                 agent-side heuristic (e.g. mask instability across 2 seeds)     [NET-NEW, trivial]
 │    ├─ confident → auto-accept + audit record
 │    └─ uncertain → snap.request_human(slice_z)
 │          ├─ L2 focus LIVE GUI    SetCursorPosition(voxel) + trigger/findChild                    [prim EXISTS; RPC NET-NEW]
 │          ├─ HUMAN paints on cam  existing paintbrush pipeline (PaintbrushModel.cxx:301)          [EXISTS]
 │          └─ snap.commit()        SegmentationChangeEvent → read UndoDataManager delta → JSON     [NET-NEW small]
 └─ structured audited result returns to agent
```

Every EXISTS box is proven headless or in-GUI; the three NET-NEW boxes (confidence gate, live-GUI RPC, audit serializer) are small and independently testable. The clip exercises **callable + resumable (park-for-human) + audited** in ~45 seconds, and the on-camera human paint stroke is the irreplaceable wow.

**Build order:** (1) audit-record serializer over `UndoDataManager` [P2 core]; (2) minimal external command channel over `SNAPTestQt` primitives [P4 core]; (3) DLS thin Python client (HTTP-only, no ITK); (4) stitch into one MCP tool namespace + confidence gate.

### 5.2 The unified surface & session lifecycle

One local, distributable MCP server exposing **one tool namespace**. Two backends behind it; the tool schema advertises which mode each tool needs:

- **`headless.*` tools** — call Layer-1 directly (workspace open/save, layer/label ops, apply mask, read audit). No GUI process.
- **`live.*` tools** — require an attached, running ITK-SNAP GUI. The server **launches or attaches** a GUI process on demand (reuse the itksnap-dls "launch a local server on demand" ergonomics), then drives it via the new command channel (§2.8).
- A `session` object tracks state: `{ mode: headless | attached, pid, workspace, dls_session_id }`. `live.*` calls on a headless session trigger an attach (launch GUI, load the same workspace). The human "takes over" simply by touching the mouse/keyboard of that same window — no separate mode switch — while the agent watches state via property-model observers and the audit stream.

**Session lifecycle representation** is itself a deliverable design point and hinges on §7's handoff decision.

### 5.3 Dataset manifest (never hardcode filenames)

A `demo/manifest.yaml` parameterizes every clip so more images can be added later:

```yaml
dls:
  server_cmd: "python -m itksnap_dls --port 8911 --device {device}"
  base_url: "http://localhost:8911"
  api_version: "v0.0.10-unprefixed"   # verified via /status before recording
cases:
  - id: case01
    workspace: data/case01/case01.itksnap     # relative; resolved at run time
    main_image: data/case01/img.nii.gz
    seed_point_voxel: [128, 96, 40]           # canned, deterministic
    expected_mask: data/case01/expected.nii.gz # golden output for retakes
    route: uncertain                           # forces the human-handoff branch
  - id: case02
    seed_point_voxel: [64, 64, 30]
    route: confident                           # auto-accept branch
```

### 5.4 Video suite — one through-line, standalone clips (~30–60s each)

Through-line: *an agent runs a segmentation pipeline, and when it hits a case it shouldn't decide alone, a human expert steps in — live — and the agent records the verdict.*

**Clip A — "ITK-SNAP is now a tool an agent can call" (~35s)**
- *On screen:* a terminal/agent transcript; a headless `snap.open()` + `snap.propose()`; the confident case (`case02`) auto-accepts; a one-line audit record prints.
- *Agent action:* `snap.propose(case02.seed)` → mask; confidence gate passes.
- *Payoff caption:* "Callable — no GUI needed for the easy cases."
- *Reproducibility:* canned seed from manifest; DLS response cached to `expected.nii.gz`; assert-equal gate. No live GUI → fully deterministic.

**Clip B — "The model defers to the human" (~50s) — FLAGSHIP**
- *On screen:* same agent hits `case01`; confidence gate fails; the **live ITK-SNAP window** comes forward, already on the uncertain slice with the proposal loaded; the expert paints the correction; agent prints "accepted."
- *Agent action:* `snap.request_human(case01, slice_z)`; then waits.
- *Human takeover:* visibly grabs the mouse and paints two strokes on the canvas.
- *Payoff caption:* "Resumable — the pipeline parks the hard case for a human and continues on their verdict."
- *Reproducibility:* scripted **demo driver** pre-positions the window (`SetCursorPosition`, `trigger`), loads the pinned proposal; the human paint is the only live action; a poll-until-`SegmentationChangeEvent` replaces `sleep`. Retake = re-run driver, repaint. (Optional: pre-record a canned paint via `postMouseEvent`/`postKeyEvent` on the canvas for a hands-free retake, accepting relative-coord fragility.)

**Clip C — "The correction comes back as an audited diff" (~35s)**
- *On screen:* split view — the paint stroke on the left; the JSON audit record (op, timestamp, changed-voxel count, bbox, before/after label counts, user vs agent) materializing on the right; the agent ingests it.
- *Agent action:* `snap.commit()` returns the record; agent appends it to a run log.
- *Payoff caption:* "Audited — expert judgment returns as structured, attributable data."
- *Reproducibility:* deterministic given the same stroke; the serializer is pure over the undo delta. Golden-file the record modulo timestamp.

**Clip D (optional, technical audience) — "Robust addressing" (~40s)**
- *On screen:* the P4 side-by-side — pixel click vs voxel API landing on the same voxel; a `findChild`-addressed panel action.
- *Payoff caption:* "Semantic + image-space addressing — reproducible across layout changes."

**Clip E (phase 2) — "Batch triage queue" (~50s)** — the P3 dashboard, resumable ticket queue.

Clips A→B→C are the core narrative and also stand alone on slides. D and E are audience-specific add-ons.

---

## 6. Risks & open questions (what to verify before committing to the MVP)

1. **[Verify first] DLS API version pin.** The GUI client targets `v2/…?point=` while the local server exposes `/…?x&y&z` (§2.5). Probe `/status` and one route on the actual demo server; write the thin client to match; record the version in `manifest.yaml`. *Cheap, do this in hour one.*

2. **[Hardest] Live external command channel.** `SNAPTestQt` runs canned JS in a test thread *before* `exec()` (`main.cxx:1443`). Verify a socket/stdin RPC can inject `QApplication::postEvent`/method-invokes into the **running** loop after launch, without the `--test` scaffold. Prototype: a tiny `QLocalServer` in `main.cxx` that forwards JSON commands to the existing `SNAPTestQt` slots. Gates P1 and P4.

3. **[Central] Agent→human handoff on ONE session.** A headless L1 process and the human's GUI are, by default, **two `IRISApplication` instances in two processes.** Two viable models (pick before building — see §7):
   - **(A) Drive the live GUI** (favored): the agent's `live.*` tools operate the human's one running process via the channel from risk #2; edits and reads share that process. Cleanest for "same session on camera."
   - **(B) Headless + ingest hook:** agent works headless; the GUI exposes an "import this mask / here's my correction" hook; images cross the process boundary. More moving parts, weaker "same session" story.
   DLS session state is **not persisted across restarts** (`session.py`), so you cannot park a DLS session in one process and resume it in another — reinforcing model (A).

4. **[Favorable, but verify] Headless segmentation apply without GL/Qt.** `itksnap-wt` proves Qt-free *metadata* linking; verify the same for *voxel edits*: build a tiny L1 binary that loads an image, paints via `SegmentationUpdateIterator`, saves — linking `itksnaplogic` alone, no Qt/GL. Compile-guard the optional VTK touch-points (`Logic/Slicing/IntensityCurveVTK.h`, `Logic/Mesh/VTKMeshPipeline.h`).

5. **[Design] Audit record scope.** `UndoDataManagerCommit::m_Name` is `protected` (no getter); no timestamp/identity/op/params/export. Decide the record schema and add a minimal getter + fields + JSON serializer. Confirm `SegmentationChangeEvent` fires at the right granularity to trigger serialization per commit.

6. **[Determinism] Recording flakiness.** No pinned inference seed in DLS; only `sleep()`-based waits in the harness. Mitigate: fixed input + canned seed + **golden mask** (`expected.nii.gz`); replace `sleep` with poll-until-condition; optionally cache the DLS response so a clip doesn't depend on GPU availability (device auto-detects cuda/cpu/mps, `__main__.py:39`). Prefer a scripted **demo driver** over free-form agent prompting for anything that must be frame-stable.

7. **[Packaging] Ship order.** DLS demo client = plain Python (HTTP+gzip+base64), **no ITK** → ship first. Defer the pybind11 Layer-1 binding (new `itksnap/CMakeLists.txt` target; needs `RLEImage`/`LabelImageWrapper` SimpleITK specializations beyond `greedy_python`'s base-type converters). The MCP server is a new local package; no hosted service.

8. **[Scope] Canvas mouse events are relative coords.** `postMouseEvent` is 0.0–1.0 widget-relative (`SNAPTestQt.cxx:315`); hitting a voxel via mouse needs camera math. Route programmatic edits through the voxel API (§2.4); reserve canvas mouse events for clips where a raw click *is* the visual point.

---

## 7. Decisions I need from you (before building)

These are the consequential forks the plan deliberately leaves open rather than assume:

1. **Handoff architecture (§6.3):** model **(A) drive the human's one live GUI process** (my recommendation) vs **(B) headless agent + GUI ingest hook**? This shapes the session-lifecycle design and the command channel.
2. **Flagship scope for the first recordings:** ship **P2 (audited callable)** as the first filmed clip and grow into P1, or go straight for the full **P1** handoff? (I recommend P2-first; it de-risks the audit format P1 depends on.)
3. **DLS server version to pin:** run the local `itksnap-dls` v0.0.10 (un-prefixed API) for the demo, or the newer `v2/` server the GUI expects? Whichever we pin, the thin client is written to match.
4. **Audit record contents:** minimum viable set is {op name, timestamp, agent-vs-human, changed-voxel count, bbox, before/after label counts}. Anything else the grant reviewers will want to see (e.g. per-label Dice vs the proposal, reason string)?

---

## Appendix — key file references

- Plan mandate: `projects/agentic-api/NEXT_SESSION_PROMPT.md`
- Headless proof: `itksnap/Utilities/Workspace/{WorkspaceTool.cxx, CMakeLists.txt}`
- L1 substrate: `itksnap/Logic/WorkspaceAPI/WorkspaceAPI.{h,cxx}`; `itksnap/Logic/Framework/{IRISApplication.h, SegmentationUpdateIterator.h, GlobalState.h, UndoDataManager.{h,txx}}`; `itksnap/Logic/ImageWrapper/LabelImageWrapper.{h,cxx}`
- Live-GUI channel: `itksnap/Testing/GUI/Qt/SNAPTestQt.{h,cxx}`, `itksnap/Testing/GUI/Qt/Scripts/test_Library.js`, `itksnap/GUI/Qt/main.cxx:732-746,1443-1446`; screenshot `itksnap/GUI/Qt/Components/SliceViewPanel.{h:58,cxx:489}`
- Property/event: `itksnap/Common/{PropertyModel.h, SNAPEvents.h, AbstractModel.{h,cxx}, EventBucket.{h,cxx}}`
- DLS server: `itksnap-dls/itksnap_dls/{server.py, session.py, segment.py, __main__.py}`, `itksnap-dls/docs/quick_start.md`
- DLS client: `itksnap/GUI/Model/DeepLearningSegmentationModel.{h,cxx}`
- Ticket/resume (DSS): `itksnap/GUI/Model/DistributedSegmentationModel.{h,cxx}`
- Transport: `itksnap/Logic/WorkspaceAPI/{RESTClient.{h,cxx}, SSHTunnel.{h,cxx}}`
- Python-binding template: `greedy_python/{CMakeLists.txt, src/GreedyPythonBindings.cxx, src/picsl_greedy/_greedy_api.py}`
- Qt boundary / libs: `itksnap/CMakeLists.txt:1128-1163,1227-1243`
