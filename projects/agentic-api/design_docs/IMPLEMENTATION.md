# ITK-SNAP Agentic API — Implementation

This document is the code-level companion to [`DESIGN.md`](./DESIGN.md). It walks through every
component with file paths, function names, and line numbers, then traces one full request end to
end. Line numbers are as of the commits recorded at the bottom; treat them as signposts and grep
for the symbol if they drift.

Diagrams: [`architecture.svg`](./architecture.svg) (components) and
[`flow-chart.svg`](./flow-chart.svg) (end-to-end flow).

---

## 0. Repository layout

| Repo (submodule) | Branch | Role |
|---|---|---|
| `itksnap/` | `sprint/caimi` | C++ GUI + Logic: the `--agent-listen` channel and the audit engine |
| `itksnap-dls/` | `feature/agentic-api` | FastAPI model server (TotalSegmentator) |
| `itksnap-mcp/` | `main` | Public Python glue: MCP tools, socket client, demo driver |

The wrapper repo `itksnap-developer` pins the `itksnap` and `itksnap-mcp` pointers; the
`itksnap-dls` pointer is intentionally left unrecorded (checked out manually).

---

## 1. Tier 1 — the model server (`itksnap-dls`)

A FastAPI service (default `http://localhost:8911`). The client contract is documented and
implemented in `itksnap-mcp/src/itksnap_mcp/dls_client.py`. Endpoints used by the propose step:

| Endpoint | Meaning |
|---|---|
| `GET /status` | health check → `{"status":"ok","version":...}` |
| `GET /v2/models` | list models |
| `GET /v2/start_session/{model_id}` | begin a session → `session_id` |
| `POST /v2/upload_raw/{session_id}` | upload the scalar volume (gzip float32, `[z,y,x]`) + metadata |
| `GET /v2/run_automatic/{session_id}?fast=true` | run prompt-free segmentation → base64(gzip(int16)) labels + `{id:name}` |

**Wire-format caveat:** `upload_raw` transports raw voxels and **drops spacing/origin/direction**,
so the returned labels live on an identity grid (same voxel indices as the upload, no physical
geometry). The agent restores geometry before applying (see §2.3).

---

## 2. Tier 2 — the agent glue (`itksnap-mcp`)

Pure Python, no ITK/compiled dependency. Four modules under `src/itksnap_mcp/`.

### 2.1 `dls_client.py` — HTTP client for propose

- `class DLSClient` — `start_session`, `upload_image`, `run_automatic`, `list_models`.
- `run_automatic(...)` returns `AutomaticResult` (`labels: np.ndarray [z,y,x]`, `label_map: {id:name}`).
- `load_nifti_for_upload(path)` → `(array_zyx float32, size_xyz, source_sitk_image)`. It returns the
  **source image** too, so callers can copy its geometry back onto results.

### 2.2 `channel.py` — Unix-socket client for the live GUI

- `class SnapChannel(sock_path)` — one request/response per call over `AF_UNIX`.
- `SnapChannel.call(cmd, args)` builds `{"id":1,"cmd":...,"args":...}`, sends one newline-terminated
  JSON line, reads one line back, and raises `SnapChannelError` on `ok:false`.
- Convenience wrappers: `ping`, `set_actor`, `apply_box`, `apply_seg_file`, `get_audit`,
  `get_audit_log`, `set_labels`, `get_labels`, `set_cursor`.
- Stdlib only (`socket` + `json`), so it imports with zero cost anywhere.

### 2.3 `server.py` — the MCP tools (and reusable helpers)

Reusable, MCP-free helpers (also used by the demo driver):

- `propose_segmentation(client, ct_path, model_id, fast, task)` → `(AutomaticResult, source_sitk)`:
  load → `start_session` → `upload_image` → `run_automatic` → `end_session`.
- `proposal_summary(result)` → `{shape_zyx, present_labels:[{id,name,voxels}]}`.
- `write_label_mask(result, source, label_id, out_path)` — extract the binary mask for one label,
  `sitk.GetImageFromArray(...)`, **`CopyInformation(source)`** to restore geometry, write NIfTI.

`build_server(base_url, sock_path)` registers the MCP tools (FastMCP), holding the last proposal in
a closure `state` dict:

| Tool | Does | Backed by |
|---|---|---|
| `list_models()` | list models | `DLSClient.list_models` |
| `propose(ct_path, ...)` | run auto-seg, cache result, return summary | `propose_segmentation` |
| `apply(label_id, itksnap_label, actor, name)` | mask → NIfTI → `set_actor` + `apply_seg_file`, then name the label (`name` or the model's anatomy name) | `write_label_mask` + `SnapChannel` + `_set_labels` |
| `set_labels(labels)` | name/recolor labels (live socket or workspace file) | `normalize_label_spec` + `SnapChannel`/`Workspace` |
| `get_labels()` | read back the id → name/color mapping | `SnapChannel.get_labels` / `Workspace.get_labels` |
| `read_audit()` | last edit's audit record | `SnapChannel.get_audit` |
| `read_audit_log(since)` | *every* edit's record, cursor-paged; syncs the live log into the workspace first | `Workspace.sync_live_audit` + `SnapChannel.get_audit_log` |
| `set_actor(actor)` | arm agent/human | `SnapChannel.set_actor` |

`set_labels` accepts either a mapping (`{id: "name"}` or `{id: {"name":…, "color":[r,g,b]}}`) or a
list of `{"id":…, "name"?:…, "color"?:[r,g,b]}`; `normalize_label_spec` collapses both into the one
canonical list both transports consume. `_set_labels` routes live-when-attached exactly like the
`_apply_mask` helper. A rename preserves the label's other attributes and produces no audit record
(it is configuration, not a segmentation edit).

### 2.4 `demo/run_p2.py` — scripted end-to-end driver

`propose → pick largest (or `--label`) → write_label_mask → set_actor("agent") → apply_seg_file →
get_audit`. This is exactly the sequence the MCP tools expose, runnable as one script.

---

## 3. Tier 3 — ITK-SNAP: the live command channel (`main.cxx`)

`itksnap/GUI/Qt/main.cxx`:

- Flag parsing: `--agent-listen` registered at line **541**, read into `argdata.agentListen` at
  **760–761**.
- Server setup: if the flag is set (line **1465**), a `QLocalServer` is created **before**
  `app.exec()` (line **1469**) and its `newConnection`/`readyRead` handlers (line **1470**, **1473**)
  run on the **GUI (main) thread**. Contrast with `--test`, which runs canned JS on a *worker*
  thread before the loop — the live channel is deliberately main-thread-affine, so calling the
  editing primitives is safe with no cross-thread marshalling.
- Dispatch: a simple `if/else if` on `cmd`. Commands and their lines:

| `cmd` | line | handler summary |
|---|---|---|
| `ping` | 1481 | reply `"pong"` |
| `set_cursor` / `get_cursor` | 1485 | `IRISApplication::Set/GetCursorPosition` |
| `set_actor` | 1509 | validate actor → `driver->SetNextSegmentationCommitActor(...)` |
| `apply_box` | 1533 | build region from corners → `PaintRegionWithLabel` → return audit |
| `apply_seg_file` | 1581 | `itk::ImageFileReader` → `PaintMaskWithLabel` → return audit |
| `get_audit` | 1639 | `GetLastSegmentationAuditRecordJSON` → embed as JSON object |
| `get_audit_log` | 1652 | `GetSegmentationAuditLogJSON(since)` → `{since,total,records[]}` |
| `set_labels` | 1669 | per label: `GetColorLabelTable()->GetColorLabel → SetLabel/SetRGB → SetColorLabel`; no audit (config, not an edit) |
| `get_labels` | 1706 | iterate `GetColorLabelTable()->GetValidLabels()` → `[{id,name,color,visible,alpha}]` |

The `set_labels`/`get_labels` handlers reuse the label table on `IRISApplication`
(`driver->GetColorLabelTable()`) — the same object and the same `GetColorLabel → SetLabel →
SetColorLabel` sequence the GUI's `LabelEditorModel::SetCurrentLabelDescription` uses, so the open
label editor and the slice/mesh views refresh from the events `SetColorLabel` already fires. Line
numbers are signposts; grep for the `cmd` string if they drift.

**Headless (workspace) side.** `Workspace.set_labels`/`get_labels` shell out to `itksnap-wt`
(`-labels-set-name <id> <name>`, `-labels-set-color <id> <r> <g> <b>`, `-P -labels-list`), which call
new `WorkspaceAPI` methods (`SetLabelName`/`SetLabelColor`/`PrintLabels`,
`Logic/WorkspaceAPI/WorkspaceAPI.cxx`). Each loads the current `ColorLabelTable` from the main
layer's `ProjectMetaData.IRIS.LabelTable`, mutates one label, and writes it back — so names/colors
merge incrementally and preserve every other attribute (same folder the pre-existing `-labels-set`
uses). *Gotcha:* the GUI only re-reads that table when the workspace's recorded
`Files.Grey.Dimensions` matches the loaded image (`SNAPRegistryIO::ReadImageAssociatedSettings`
bails early otherwise), which holds for real 3D CTs but silently fails for 2D test images (a
recorded `W H 0` never matches) — verify with a 3D volume.

The `apply_seg_file` handler (line **1581**) reads the mask into a **plain** `itk::Image<LabelType,3>`
(a stock `itk::ImageFileReader`), because the segmentation's own image type is run-length-encoded
(RLE) and cannot be read by a generic reader. Errors from the reader are caught and returned as
`{"ok":false,"error":"read failed: ..."}`.

---

## 4. Tier 3 — ITK-SNAP: the Logic-tier audit engine

All of this is GUI-independent (links `itksnaplogic` alone), which is why it is unit-testable.

### 4.1 The edit funnel — `SegmentationUpdateIterator`

`itksnap/Logic/Framework/SegmentationUpdateIterator.h`. Every voxel edit in ITK-SNAP is expressed by
constructing this iterator over a region with an active label and a "draw-over" rule, calling a paint
method per voxel (`PaintAsForeground` at line **137**, etc.), which:

- computes the per-voxel difference `new − old` and RLE-encodes it into an `UndoDelta`,
- writes the new value into the (RLE) segmentation image,
- increments `m_ChangedVoxels`.

`Finalize(undo_string)` (line **233**) closes the delta and, if anything changed, calls the wrapper's
`StoreUndoPoint(...)` to commit it. This is the single sink all edits pass through.

### 4.2 The commit chokepoint — `LabelImageWrapper::StoreUndoPoint`

`itksnap/Logic/ImageWrapper/LabelImageWrapper.cxx`, line **99**. This is where provenance is captured:

```cpp
int n_rles = um->CommitStaging(text);                       // create the undo commit
bool is_temporary = (text && std::string(text) == TEMPORARY_UNDO_POINT_NAME);
if (n_rles > 0 && !is_temporary) {
  m_LastAuditRecord = SegmentationAuditRecord::BuildFromDeltas(  // line 117: reconstruct
        m_Image,                                                 //   current (post-edit) image
        um->GetLastCommit().GetDeltas(),                         //   the committed delta(s)
        text ? text : "", m_NextCommitActor, m_TimePointIndex);
  m_HasLastAuditRecord = true;
  m_AuditLog.push_back(m_LastAuditRecord);
  if (m_AuditLog.size() > MAX_AUDIT_LOG) m_AuditLog.erase(m_AuditLog.begin());  // bounded
  m_NextCommitActor = SegmentationAuditRecord::HUMAN;       // consume-on-commit (see §4.5)
}
```

Notes:

- Throwaway commits literally named `"Temporary undo point"` (used by smart-brush/lasso paths that
  immediately undo) are **skipped** so they neither pollute the log nor steal the actor tag.
- The in-memory `m_AuditLog` is bounded (`MAX_AUDIT_LOG`) and cleared alongside undo history in
  `ClearUndoPoints*`, so it can't grow without limit.
- `Undo()` (line **183**) sets `m_HasLastAuditRecord = false` — after an undo, `get_audit` reports
  "no record in effect" rather than a reverted edit.

### 4.2b The log tracks undo/redo — `MoveAuditRecord`

`m_AuditLog` describes the edits **currently in effect**, which matters once a caller reads the
*whole* log rather than just the newest record: an undone correction must not still be reported.
`MoveAuditRecord` (line **137**) transfers the newest record for the current time point between
`m_AuditLog` and `m_UndoneAuditRecords`:

- `Undo()` (line **230**) moves log → undone; `Redo()` (line **281**) moves it back and restores it
  as `m_LastAuditRecord`. So `get_audit`/`get_audit_log` now follow redo, not only undo.
- Matching is **per time point** (each time point has its own undo manager, so the newest record
  logged against that time point is the one being undone) and **skips temporary commits**, which
  never entered the log — without that guard, undoing a smart-brush temporary commit would pop the
  genuine record beneath it.
- Covered by scenario 5 of the L1 test (§6), which fails if either guard is removed.

### 4.3 The record and its serializer — `SegmentationAuditRecord`

`itksnap/Logic/Framework/SegmentationAuditRecord.{h,cxx}`.

- `enum Actor { HUMAN, AGENT, UNKNOWN }` (`.h` line **70**), plus `ActorToString`/`ActorFromString`.
- Fields: `op`, `timestamp` (ISO-8601 UTC via `NowIso8601Utc()`), `actor`, `changed_voxels`,
  `rle_count`, `time_point`, `bbox_valid`/`bbox_min`/`bbox_max`, `before_counts`/`after_counts`
  (`std::map<LabelType, unsigned long>`).
- `ToJSON()` (`.h` line **109**, impl in `.cxx`) — a hand-rolled, dependency-free serializer with
  proper string escaping (no Qt in the Logic tier).

### 4.4 The reconstruction — `BuildFromDeltas` (the heart of it)

`SegmentationAuditRecord.h`, static template at line **127**. Templated on the image type so it works
on both the production RLE image and a plain `itk::Image` in tests. The walk:

```cpp
for (UndoDelta<LabelType>* delta : deltas) {          // a commit may hold several deltas
  ImageRegionConstIteratorWithIndex<TImage> it(current_image, delta->GetRegion());
  for each RLE run (length n, value d):
    for j in 0..n-1:
      if (d != 0) {                                   // this voxel changed
        LabelType new_label = it.Get();               // image already holds the NEW state
        LabelType old_label = (LabelType)(new_label - d);   // modular unsigned-short subtraction
        before_counts[old_label]++; after_counts[new_label]++; changed_voxels++;
        update bbox from it.GetIndex();
      }
      ++it;
}
```

Why it is exact: this is the same delta traversal `LabelImageWrapper::Undo()` uses to roll an edit
back (`LabelImageWrapper.cxx:162`), and the RLE was encoded by `SegmentationUpdateIterator` walking
the region in the *same* raster order that `ImageRegionConstIteratorWithIndex` uses. The subtraction
`new − d` is done in `LabelType` (unsigned short) arithmetic, which wraps modulo 65536 and therefore
recovers the exact original label.

**Precondition (documented in the header):** within a single commit no voxel is written to two
different non-zero values. Every real edit path holds this — the active label is constant per commit,
so re-touching a voxel encodes `d == 0`. The unit test exercises the case explicitly (see §6).

### 4.5 The actor model — consume-on-commit

- `LabelImageWrapper::m_NextCommitActor` defaults to `HUMAN`.
- `set_actor` → `IRISApplication::SetNextSegmentationCommitActor` (`IRISApplication.cxx:556`) →
  `LabelImageWrapper::SetNextCommitActor`.
- The next commit (in `StoreUndoPoint`, §4.2) stamps the record with `m_NextCommitActor` and then
  resets it to `HUMAN`, so the tag applies to exactly one commit.

### 4.6 `UndoDataManager` additions

`itksnap/Logic/Framework/UndoDataManager.h`:

- `UndoDataManagerCommit::GetName()` (line **115**) — public getter for the commit title (was
  `protected` with no accessor; required so the record can report `op`).
- `UndoDataManager::GetLastCommit()` (line **166**) — the newest commit, walked by `BuildFromDeltas`.

### 4.7 The apply entry points — `IRISApplication`

`itksnap/Logic/Framework/IRISApplication.cxx`:

- `PaintRegionWithLabel(region, label, undoTitle)` (line **577**) — paint a box; used by `apply_box`.
- `PaintMaskWithLabel(mask, label, undoTitle)` (line **604**) — apply an external plain-image mask;
  used by `apply_seg_file`. It crops to the overlap of the mask and segmentation grids, then walks a
  `SegmentationUpdateIterator` over the RLE segmentation in lockstep with an
  `ImageRegionConstIterator` over the plain mask, painting where the mask is nonzero. It mirrors the
  existing `UpdateSegmentationWithBinarySegmentation` (line **754**) but takes a *plain* image and an
  explicit label with `PAINT_OVER_ALL`.
- `GetLastSegmentationAuditRecordJSON()` (line **568**) — returns the selected layer's last record as
  JSON, or the literal `"null"`.

Both paint methods finish by firing `SegmentationChangeEvent` exactly once, so downstream models/GUI
re-render, and — critically — the audit record is already captured by the time the event fires.

---

## 5. End-to-end code trace: one `apply_seg_file`

Following [`flow-chart.svg`](./flow-chart.svg), here is the apply half, function by function:

1. **Agent** (`server.py::apply` or `run_p2.py`): `write_label_mask(result, source, label_id, out)`
   writes `/tmp/…nii.gz` with the CT's geometry restored; then `SnapChannel.set_actor("agent")` and
   `SnapChannel.apply_seg_file(out, itksnap_label)`.
2. **Socket → ITK-SNAP** (`main.cxx:1509` then `:1581`): `set_actor` arms the actor;
   `apply_seg_file` reads the NIfTI into a plain `itk::Image<LabelType,3>` and calls
   `driver->PaintMaskWithLabel(reader->GetOutput(), label, "Agent apply (proposal)")`.
3. **Paint + commit** (`IRISApplication.cxx:604` → `SegmentationUpdateIterator::Finalize:233` →
   `LabelImageWrapper::StoreUndoPoint:99`): the mask is painted into the RLE segmentation, the delta
   is committed, and `BuildFromDeltas` reconstructs the record (`:117`), tagged `agent`, and stored.
4. **Event** (`IRISApplication.cxx:604` tail): `InvokeEvent(SegmentationChangeEvent())` → the live
   slice re-renders.
5. **Reply** (`main.cxx:1581` tail): the handler calls `GetLastSegmentationAuditRecordJSON()` and
   returns `{"ok":true,"result":{"changed_voxels":N,"audit":{...}}}` on the socket.
6. **Agent**: `read_audit()` (`main.cxx:1639`) can re-fetch the same record any time before the next
   commit.

Observed live (GPU run, `run_p2.py` on a body CT): the applied left-upper-lung produced
`changed_voxels = 1169665`, `after_counts = {"1": 1169665}`, `bbox = [84,2,0]–[247,189,180]`, actor
`agent`.

---

## 6. Testing

- **L1 unit test** — `itksnap/Testing/Logic/SegmentationAuditRecordTest.cxx`, CTest target
  `SegmentationAuditRecordTest`. Links `itksnaplogic` alone (proves the audit engine is GUI-free) and
  checks `BuildFromDeltas` on: a plain image, the **production RLE image type** (proves iterator order
  matches delta encoding), non-zero "before" labels, multi-delta accumulation, **overlapping
  same-voxel deltas counted once** (the precondition from §4.4), and JSON escaping. **Scenario 5**
  drives a real `LabelImageWrapper` through commit → undo → redo → temporary-commit-undo and asserts
  the log tracks what is in effect (§4.2b).
- **Runtime smokes** (headless Xvfb): drive `set_actor`/`apply_box`/`apply_seg_file`/`get_audit` over
  the socket and assert exact voxel counts (e.g. applying `MRIcrop-seg` → 55,893 voxels).
- **Full chain** — `demo/run_p2.py` against the live DLS server + ITK-SNAP (see the sprint's
  `NEXT_SESSION_PROMPT.md` for the exact reproduction commands).

---

## 7. Known limitations / edge cases

- **Actor arming** must happen immediately before a committing operation; a genuine no-op between
  arming and the real edit would carry the tag to the next commit. A fully robust fix would thread
  the actor through `StoreUndoPoint`/`Finalize` as an argument.
- **Audit log bound** — the live log is capped at `MAX_AUDIT_LOG` (4096) records; past that the
  oldest are evicted, which would also break the `since` cursor's alignment with the workspace log.
  Far above any real correction session.
- **Reconstruction precondition** (§4.4) — one constant label per commit. Contrived multi-label
  overwrites in a single commit would mis-reconstruct; no real path does this.
- **Geometry** — the proposal must share the loaded image's grid; the agent restores geometry from
  the source CT before applying. Cross-grid proposals would need resampling first.
- **Multi-label apply** — `apply` currently applies one structure under one label. Applying an entire
  multi-label TotalSegmentator result at once is a straightforward extension of `PaintMaskWithLabel`.

---

## 8. Reference commits

| Repo | Commit | Content |
|---|---|---|
| `itksnap` | `560dcd2f` | audit record core (`SegmentationAuditRecord`, capture, accessors, L1 test) |
| `itksnap` | `f1743f04` | `apply_box` + `PaintRegionWithLabel` (P2 loop closed) |
| `itksnap` | `e1aa19d5` | `apply_seg_file` + `PaintMaskWithLabel` (apply a real proposal) |
| `itksnap-mcp` | `9909663` | `propose`/`apply`/`read_audit` MCP tools + `channel.py` + `demo/run_p2.py` |
