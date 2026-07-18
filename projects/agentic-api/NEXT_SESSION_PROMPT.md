# RESUME — ITK-SNAP Agentic API · CAIMI Builder Showcase sprint

## Current state (read this paragraph first)
We are building a prototype for a **SIIM-CAIMI26 AI Builder Showcase** submission (deadline
**2026-07-24 11:59 PM PST**). Thesis: *"model proposes, human disposes"* — expose expert human
judgment as a **callable, resumable, audited** pipeline step an external agent can invoke. Three code
homes: **`itksnap`** (C++ GUI/logic, branch `sprint/caimi`), **`itksnap-dls`** (Python FastAPI model
server, branch `feature/agentic-api`), **`itksnap-mcp`** (public repo, the agent-facing glue + demo —
the CAIMI link reviewers open). Cleared so far: **Gate 1** — automatic segmentation live (TotalSegmentator
fast mode via DLS + the `itksnap-mcp` client, 12.9 s on this RTX 2080); **Gate 2** — a live command
channel (`itksnap` `--agent-listen` QLocalServer) drives the running GUI; and now the **audit record
(P2 core)** — commit `560dcd2f` on `sprint/caimi` (**local, NOT pushed**): every committed segmentation
edit produces a structured JSON record `{op, timestamp, actor(agent|human), changed_voxels, bbox,
before/after label counts}`, reconstructed from the undo delta vs the current image at commit time. It is
unit-tested (L1 test passes, incl. the production RLE image) and the channel exposes `get_audit` +
`set_actor`. **What is proven but NOT yet demonstrated end-to-end:** a *real* segmentation edit flowing
through ITK-SNAP's commit path and returning a *populated* audit record over the socket — because the
channel has no command that triggers a committing edit yet (`get_audit` currently returns `null` until
something commits). Still absent overall: the MCP tool namespace (skeleton only), the demo driver/video,
the abstract.

## The single next goal
**Close the P2 loop with a REAL edit: apply a segmentation through ITK-SNAP's commit path and read back
the populated audit record over the `--agent-listen` socket.** Concretely, add an `apply_segmentation`
command to the channel in `itksnap/GUI/Qt/main.cxx` (next to the new `get_audit`/`set_actor` at ~line
1507): it ingests a label volume (start simple — e.g. a small box or a base64/np payload, or reuse the
DLS-result path) and calls `IRISApplication::UpdateSegmentationWithBinarySegmentation(...)`
(`IRISApplication.cxx:676`) — which finalizes the iterator, commits, fires `SegmentationChangeEvent`, and
(via `LabelImageWrapper::StoreUndoPoint`) captures the audit record. Have the client do
`set_actor agent` → `apply_segmentation` → `get_audit` and confirm a populated record comes back with
`actor:"agent"`, correct `changed_voxels`/`bbox`/`before_counts`/`after_counts`. That is the P2
"commit() returns the audit record" beat filmed as **Clip C** — and it feeds directly into W3 (the MCP
`apply`/`commit`/`read-audit` tools). Then (still P2): wire the MCP `headless.*` namespace to this loop.

## Files to read first (in order)
1. `projects/agentic-api/docs/sprint_caimi.md` — the sprint plan (scope, day-by-day, ticked status, DoD).
   W2 audit record is now ✅; you are on **Day 3 (W3 MCP + headless slice)**.
2. `projects/agentic-api/PROGRESS_LOG.md` — newest entry (this session) has the audit-record design,
   the commit hash, what surprised, and the known residuals.
3. `projects/agentic-api/docs/spike_live_channel.md` — how the live channel works + how to extend it.
4. In `itksnap/` (the audit record — already built, `sprint/caimi`):
   - `GUI/Qt/main.cxx` — the `--agent-listen` block; `get_audit`/`set_actor` are the pattern to copy for
     `apply_segmentation` (JSON-RPC dispatch ~1474–1530).
   - `Logic/Framework/SegmentationAuditRecord.{h,cxx}` — the record type + `ToJSON()` + `BuildFromDeltas`.
   - `Logic/ImageWrapper/LabelImageWrapper.cxx` — `StoreUndoPoint` (capture site), `Undo` (invalidation).
   - `Logic/Framework/IRISApplication.cxx` — `UpdateSegmentationWithBinarySegmentation` (676, the commit
     path to invoke), `GetLastSegmentationAuditRecordJSON`/`SetNextSegmentationCommitActor` (548+).
5. `itksnap-mcp/` (server + `demo/agent_send.py`) — where the MCP `headless.*`/`live.*` tools get wired.
6. `projects/agentic-api/docs/caimi-submission-requirements.md` — submission rules + abstract skeleton.

## Setup (this machine — Linux, RTX 2080 8 GB; dev/fast-mode only)
- Env ready in the **base conda env** (`conda activate base`): torch 2.3.1+cu121, TotalSegmentator,
  `itksnap-dls` editable on `feature/agentic-api`.
- Branches: `itksnap` → `sprint/caimi`; `itksnap-dls` → `feature/agentic-api` (submodule pointer
  intentionally NOT recorded in the wrapper — `git switch` manually); `itksnap-mcp` → `main`.
- Build: `cmake --build build-release --target ITK-SNAP -j` (out-of-source dir `build-release/`).
  Build the logic test: `--target segmentation_audit_test`; run `ctest -R SegmentationAuditRecordTest`.
- Run the model server: `conda activate base && cd itksnap-dls && python -m itksnap_dls --port 8911 --device cuda`.
- Test the live channel (headless): `Xvfb :97 & DISPLAY=:97 setsid ./build-release/ITK-SNAP -g <ct>
  -s <seg> --agent-listen /tmp/snap-agent.sock &`, then send JSON with a small Python AF_UNIX client
  (see `/tmp/audit_smoke.py` this session, or `itksnap-mcp/demo/agent_send.py`).

## Known traps
- **`get_audit` returns `null` until an edit commits.** That is correct (no committed edit = no record).
  Proving a populated record needs the new `apply_segmentation` command — that is the whole next goal.
- **Actor "arm" model.** `set_actor agent` is consumed by the *next real commit* (auto-resets to human;
  `"Temporary undo point"` commits are skipped). Arm it **immediately before** the committing op — if the
  armed op is a genuine no-op, the tag carries to the next commit. A fully robust fix = pass the actor as
  an argument through `StoreUndoPoint`/`Finalize` (a follow-up, only if the demo needs it).
- **`get_audit` is not reconciled with `Redo()`** — only `Undo()` invalidates the last record. Fine for
  the demo (agent reads immediately post-commit); note it if a redo appears in the flow.
- **Audit reconstruction precondition:** exact only because each commit uses one constant active label
  (revisited voxel → zero delta). See the header comment in `SegmentationAuditRecord.h`.
- **`ninja --target A B` may not relink the final exe** — verify the ITK-SNAP binary mtime updated
  before smoke-testing (a batched build silently stopped at the model lib this session).
- **Unix socket path limit ~108 chars** — use a short `/tmp/snap-agent.sock` (`QLocalServer: Name error`).
- **Don't `pkill -f "ITK-SNAP"`** from the working shell (self-matches, exit 144). Launch with `setsid`
  and `kill -TERM -<pid>` the process group; run under `Xvfb` for headless.
- **DLS scalar `upload_raw` drops spacing/origin/direction** — auto-seg runs on identity geometry; thread
  geometry through for anatomically faithful demo output.
- `itksnap-mcp` license undecided (MIT vs GPL-3.0); AbstractScorecard portal account (EventKey
  `QRFBVSUS`, Chrome/Firefox) must be created by a human — not done yet.
- **Push is pending:** `itksnap` `560dcd2f` and the wrapper checkpoint are **local**. Push the submodule
  branch before anyone relies on the wrapper pointer.

## How to work
Integration over invention; ground claims in real files + line numbers. Protect the P2 floor and the
abstract; live-handoff (Clip B) is stretch. Keep the on-camera human correction a real code path. State
assumptions; ask before consequential ones. Commit inside the submodule first, then bump the wrapper.
