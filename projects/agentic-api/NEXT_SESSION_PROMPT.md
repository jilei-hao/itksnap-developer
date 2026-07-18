# RESUME — ITK-SNAP Agentic API · CAIMI Builder Showcase sprint

## Current state (read this paragraph first)
We are building a prototype for a **SIIM-CAIMI26 AI Builder Showcase** submission (deadline
**2026-07-24 11:59 PM PST**). Thesis: *"model proposes, human disposes"* — expose expert human
judgment as a **callable, resumable, audited** pipeline step an external agent can invoke, shown on
camera. The demo has three code homes: **`itksnap`** (C++ GUI/logic, branch `sprint/caimi`),
**`itksnap-dls`** (Python FastAPI model server, branch `feature/agentic-api`), and **`itksnap-mcp`**
(new public repo, the agent-facing Python glue + demo — the CAIMI link reviewers open). Both technical
blockers are now **cleared**: **Gate 1** — automatic segmentation works live (TotalSegmentator fast mode
via the DLS server + the `itksnap-mcp` thin client, 12.9 s on this box's RTX 2080); **Gate 2** — a live
command channel (`itksnap` `--agent-listen` QLocalServer, commit `d9f2329f`) lets an external process
drive the running GUI (moved the crosshair via `set_cursor`, no `--test` scaffold). The guaranteed
submission floor is **P2 "audited callable"**; the now-unblocked stretch flagship is **P1 "live
handoff"**. What does NOT exist yet: the **audit record**, the **MCP tool namespace** (only a skeleton),
the demo driver/video, and the abstract.

## The single next goal
**Build the audit record (P2 core) in `itksnap` on `sprint/caimi`.** When a segmentation edit is
committed, produce a structured JSON record: `{op, timestamp, actor(agent|human), changed-voxel count,
bbox, before/after label counts}`. Concretely: add a public getter for `UndoDataManagerCommit::m_Name`
(currently `protected`) and the missing provenance fields, a JSON serializer over the existing undo
delta, and confirm `SegmentationChangeEvent` fires once per commit at the right granularity. This is
the differentiator that makes an expert correction a *return value*, not a side effect — and it is the
last net-new piece the guaranteed P2 demo depends on. (After it: extend the live channel — extract
`SNAPTestQt` primitives into a shared helper, add `trigger`/`click`/`get_state`/`screenshot`, and wire
the MCP `live.*` tools — then record the video and write the 500-word abstract.)

## Files to read first (in order)
1. `projects/agentic-api/docs/sprint_caimi.md` — the sprint plan (scope, day-by-day, ticked status, DoD).
2. `projects/agentic-api/PROGRESS_LOG.md` — newest entry first; the "Session close / handoff" entry has
   every commit hash and every trap.
3. `projects/agentic-api/docs/spike_live_channel.md` — how the live channel works + how to test it.
4. `projects/agentic-api/docs/agentic-prototype-plan.md` — the grounded technical plan; §2.9 (undo
   engine, the audit-record starting point), §5 (MVP + video), §8 (models), §9 (distribution).
5. `projects/agentic-api/docs/caimi-submission-requirements.md` — submission rules + abstract skeleton.
6. For the audit record, in `itksnap/`: `Logic/Framework/UndoDataManager.{h,txx}`,
   `Logic/Framework/IRISApplication.{h,cxx}` (`UpdateSegmentationWith*`), `Common/SNAPEvents.h`
   (`SegmentationChangeEvent`), `Logic/ImageWrapper/LabelImageWrapper.{h,cxx}` (`StoreUndoPoint`).

## Setup (this machine — Linux, has GPUs)
- Env is ready in the **base conda env** (`conda activate base`): torch 2.3.1+cu121 (CUDA OK),
  `TotalSegmentator`, and `itksnap-dls` installed **editable** on `feature/agentic-api`. Recording box
  is a separate **4090+ (24 GB)** → full-res TS viable; this **RTX 2080 (8 GB)** is dev/fast-mode.
- Branches: `itksnap` → `sprint/caimi`; `itksnap-dls` → `feature/agentic-api` (its submodule pointer is
  **intentionally not recorded** in the wrapper, which tracks itksnap-dls `main` — `git switch` manually);
  `itksnap-mcp` → `main`.
- Build ITK-SNAP: `cmake --build build-release --target ITK-SNAP` (out-of-source dir `build-release/`).
- Run the model server: `conda activate base && cd itksnap-dls && python -m itksnap_dls --port 8911 --device cuda`.
- Test the propose backbone: `python itksnap-mcp/demo/smoke_totalseg.py --ct <body_ct.nii.gz> --url http://localhost:8911 --out /tmp/seg.nii.gz`.
- Test the live channel: launch `build-release/ITK-SNAP -g <img> --agent-listen /tmp/snap-agent.sock`,
  then `python itksnap-mcp/demo/agent_send.py /tmp/snap-agent.sock set_cursor 30 40 10`.

## Known traps
- **Unix socket path limit ~108 chars.** `--agent-listen` with a long path → `QLocalServer: Name error`.
  Use a short path like `/tmp/snap-agent.sock`.
- **Don't `pkill -f "ITK-SNAP"`** from the working shell — it self-matches the command (exit 144). Use a
  specific pattern (`ITK-SNAP.*agent-listen`) or `setsid`, and prefer targeting the launcher PID.
- **`nnInteractive` needs torch≥2.6** (we have 2.3.1) — TotalSegmentator is unaffected; only a concern if
  you use the interactive nnInteractive model (the flagship uses the human paintbrush, so likely not).
- **DLS scalar `upload_raw` drops spacing/origin/direction** (unlike the 4D path) — auto-seg runs on
  identity geometry. Fine for smoke tests; thread geometry through for anatomically faithful demo output.
- **`itksnap-mcp` license is undecided** (MIT vs GPL-3.0) — pick before publishing the CAIMI demo link.
- **Portal account** (AbstractScorecard EventKey `QRFBVSUS`, Chrome/Firefox only) must be created by a
  human — not done yet.
- Keep the C++ audit work on `sprint/caimi`; commit inside the submodule first, then bump the wrapper
  pointer.

## How to work
Integration over invention; ground claims in real files + line numbers. Protect the P2 floor and the
abstract; the live-handoff flagship is stretch. The on-camera human correction is the visual star — keep
it a real code path. State assumptions; ask before consequential ones.
