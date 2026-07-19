# RESUME — ITK-SNAP Agentic API · CAIMI Builder Showcase sprint

## Current state (read this paragraph first)
We are building a prototype for a **SIIM-CAIMI26 AI Builder Showcase** submission (deadline
**2026-07-24 11:59 PM PST**). Thesis: *"model proposes, human disposes"* — expose expert human
judgment as a **callable, resumable, audited** pipeline step an external agent can invoke. Three code
homes: **`itksnap`** (C++ GUI/logic, branch `sprint/caimi`), **`itksnap-dls`** (Python FastAPI model
server, branch `feature/agentic-api`), **`itksnap-mcp`** (public repo, the agent-facing glue + demo —
the CAIMI link reviewers open). Cleared: **Gate 1** (TotalSegmentator auto-seg live via DLS, 12.9 s on
this RTX 2080), **Gate 2** (`--agent-listen` live command channel drives the running GUI), the **audit
record (P2 core)** — commit `560dcd2f` — and now the **P2 loop is CLOSED end-to-end** (commit `f1743f04`,
both **local, NOT pushed**): an external client over the socket does `set_actor agent` → **`apply_box`**
(a real committing edit via `IRISApplication::PaintRegionWithLabel`) → **`get_audit`** and gets back a
populated, exact record `{actor:"agent", changed_voxels, bbox, before/after label counts, timestamp}`;
an unarmed second edit is correctly tagged `actor:"human"`. **What is proven:** the whole propose-less
loop (apply a labeled region → commit → structured audit read back over the socket). **What is still
box-only:** the "apply" is a geometric box, not a *real proposed segmentation*; and nothing yet wires
the MCP server or the DLS `propose` step into this loop. Absent overall: the MCP tools wired end-to-end,
the demo driver/video, the abstract.

## The single next goal
**Wire the full P2 flow through `itksnap-mcp` with a REAL proposed segmentation: propose
(TotalSegmentator) → apply the proposal into the running ITK-SNAP → read the audit record.** Concretely:
1. **C++**: add an `apply_seg_file {path, label}` command to the `--agent-listen` channel in
   `itksnap/GUI/Qt/main.cxx` (mirror `apply_box`) — ITK-SNAP reads a binary mask NIfTI from `path` and
   applies `label` through the commit path so the audit record is captured. Reuse the pattern in
   `IRISApplication::PaintRegionWithLabel` (`IRISApplication.cxx`, near line 560); the underlying merge
   primitive already exists as `UpdateSegmentationWithBinarySegmentation` (`IRISApplication.cxx:676`) —
   generalize from box → mask (read the file into a `LabelImageType`, tag actor via `set_actor`).
2. **Python**: in `itksnap-mcp/server.py`, expose three agent tools — `propose` (call the DLS
   TotalSegmentator via the existing thin client → a seg file), `apply` (send `apply_seg_file` over the
   socket), `read_audit` (send `get_audit`). Then run the whole chain against a body CT and confirm the
   agent gets back a populated audit record for the applied proposal.
This is the "ITK-SNAP as an agent-callable tool via MCP" story the abstract claims — the submission
backbone. `apply_box` + `PaintRegionWithLabel` are the proven scaffold to generalize; do NOT re-derive
the commit/audit path. After it: the human-correction beat (Clip C), then the demo driver + abstract.

## Files to read first (in order)
1. `projects/agentic-api/docs/sprint_caimi.md` — the plan (scope, day-by-day, DoD). W2 ✅; you are on
   **Day 3+ (W3 MCP namespace)**.
2. `projects/agentic-api/PROGRESS_LOG.md` — newest two entries: the audit record and the P2-loop closure
   (design, commit hashes `560dcd2f`/`f1743f04`, and the build/process traps).
3. In `itksnap/` (`sprint/caimi`, all built + verified):
   - `GUI/Qt/main.cxx` — the `--agent-listen` JSON-RPC block (~1474–1560): `ping/set_cursor/get_cursor/
     set_actor/get_audit/apply_box`. Copy `apply_box` for `apply_seg_file`.
   - `Logic/Framework/IRISApplication.cxx` — `PaintRegionWithLabel` (the apply pattern),
     `UpdateSegmentationWithBinarySegmentation` (676, the mask-merge primitive to reuse),
     `GetLastSegmentationAuditRecordJSON`/`SetNextSegmentationCommitActor`.
   - `Logic/Framework/SegmentationAuditRecord.{h,cxx}` — the record + `ToJSON()`.
4. `itksnap-mcp/` — `server.py` (MCP tools to wire), `dls_client.py` (the thin DLS client, propose),
   `demo/agent_send.py` (socket client pattern), `demo/smoke_totalseg.py` (propose smoke).
5. `projects/agentic-api/docs/caimi-submission-requirements.md` — submission rules + abstract skeleton.

## Setup (this machine — Linux, RTX 2080 8 GB; dev/fast-mode only)
- Env: `conda activate base` (torch 2.3.1+cu121, TotalSegmentator, `itksnap-dls` editable on `feature/agentic-api`).
- Branches: `itksnap`→`sprint/caimi`; `itksnap-dls`→`feature/agentic-api` (pointer NOT recorded in wrapper —
  `git switch` manually); `itksnap-mcp`→`main`.
- **Build (IMPORTANT — build in the FOREGROUND):** `cmake --build build-release --target ITK-SNAP -j`.
  Do NOT launch builds with `nohup … &` — it returns a FALSE "completed" instantly while `ninja` keeps
  building detached (this bit us: smoke tests hit a stale binary). Confirm the ITK-SNAP mtime advanced
  before smoke-testing. Logic test: `--target segmentation_audit_test`; `ctest -R SegmentationAuditRecordTest`.
- Model server: `conda activate base && cd itksnap-dls && python -m itksnap_dls --port 8911 --device cuda`.
- Live channel (headless): `Xvfb :98 & DISPLAY=:98 setsid ./build-release/ITK-SNAP -g <ct>
  --agent-listen /tmp/snap-agent.sock &`, then drive with a small AF_UNIX client
  (`/tmp/apply_smoke.py` this session, or `itksnap-mcp/demo/agent_send.py`).

## Known traps
- **Build:** `nohup … &` false-completes (see above) — build foreground. **Never `pkill -f "<string>"`
  where `<string>` appears in your own command** (e.g. `pkill -f "ninja ITK-SNAP"` SIGKILLs the tool
  shell — exit 1/144, no output). Kill by exact name: `for p in $(pgrep -x ninja); do kill $p; done`,
  or by PID; run the GUI under `setsid` and `kill -TERM -<pid>` the group.
- **Actor "arm" model:** `set_actor agent` is consumed by the *next real commit* (auto-resets to human;
  `"Temporary undo point"` commits skipped). Arm **immediately before** the committing op. Robust fix
  (if the demo needs it) = pass the actor through `StoreUndoPoint`/`Finalize` as an argument.
- **`get_audit` is not reconciled with `Redo()`** — only `Undo()` invalidates the last record. Fine for
  the demo (agent reads immediately post-commit).
- **Audit reconstruction precondition:** exact only because each commit uses one constant active label
  (revisited voxel → zero delta). See the header comment in `SegmentationAuditRecord.h`.
- **`apply_seg_file` geometry:** the proposed mask must match the loaded main image's grid/region, or
  crop/resample first (the DLS scalar `upload_raw` path drops spacing/origin/direction — identity
  geometry — so a round-tripped TS result may need geometry threaded through for faithful output).
- **Unix socket path limit ~108 chars** — use a short `/tmp/snap-agent.sock` (`QLocalServer: Name error`).
- `itksnap-mcp` license undecided (MIT vs GPL-3.0); AbstractScorecard portal account (EventKey
  `QRFBVSUS`, Chrome/Firefox) must be created by a human — not done yet.
- **Push pending:** `itksnap` `f1743f04` (and its parent `560dcd2f`) + the wrapper checkpoints are local
  until pushed. `560dcd2f` was already pushed last session; `f1743f04` is not.

## How to work
Integration over invention; ground claims in real files + line numbers. Protect the P2 floor and the
abstract; live-handoff (Clip B) is stretch. Keep the on-camera human correction a real code path. Build
foreground and confirm the binary relinked before testing. State assumptions; ask before consequential
ones. Commit inside the submodule first, then bump the wrapper pointer.
