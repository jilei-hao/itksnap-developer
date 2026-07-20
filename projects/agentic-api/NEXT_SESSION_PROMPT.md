# RESUME — ITK-SNAP Agentic API · CAIMI Builder Showcase sprint

## Current state (read this paragraph first)
We are submitting a **SIIM-CAIMI26 AI Builder Showcase** entry by **2026-07-24 11:59 PM PST** (deadline
is close). Thesis: *"model proposes, human disposes"* — an expert's segmentation correction as a callable,
resumable, **audited** pipeline step. Three repos: **`itksnap`** (C++ GUI/logic, `sprint/caimi`),
**`itksnap-dls`** (FastAPI model server, `feature/agentic-api`), **`itksnap-mcp`** (public repo `main` —
the CAIMI demo link). **Everything technical + the submission materials are DONE:** the full
`propose → apply → audit` backbone runs live (verified on GPU with a real body CT); the ≤500-word abstract
(`docs/abstract.md`, 456 words), the MIT-licensed public repo with a rewritten README + mirrored design
docs, and a tested confidence gate are all committed. **The agent-directed flow is now REAL:** the
`itksnap` MCP server is registered with Claude Code (`claude mcp list` → ✔ Connected; tools `list_models ·
propose · apply · apply_file · read_audit · set_actor`) and verified — an MCP client drove ITK-SNAP
end-to-end. There are **sample demo videos** (`design_docs/media/agentic-demo.mp4/.gif`) and a recording
runbook with the exact Claude-Code conversation (`docs/demo_runbook.md`). Pushed: `itksnap` `e1aa19d5`,
`itksnap-mcp` `0297396`, wrapper `main` (latest checkpoint). **What's left is packaging + the two
human-gated steps:** record the live demo, and submit through the portal.

## The single next goal
**Assemble the portal-ready submission package and support a final rehearsal.** Concretely:
1. **`projects/agentic-api/docs/submission.md`** — the exact copy-paste fields for AbstractScorecard:
   title, keywords, and the six sections (from `docs/abstract.md`, verbatim), plus the **Demo/Evidence
   links** — repo URLs (`github.com/jilei-hao/itksnap-mcp`, `…/itksnap`) and the **video URL placeholder**
   (fill after recording). Open-test every link. Re-verify the word count (456/500).
2. **Final rehearsal support** — if asked, do a dry run of the live flow (start the DLS server + ITK-SNAP,
   confirm `claude mcp list` shows itksnap ✔, walk the runbook conversation) and capture the real Clip-B
   `actor:"human"` numbers into the runbook so narration matches.
3. Optional polish: a higher-fidelity sample recording (heart/aorta instead of lung; drop the title bar so
   the menu shows), or move the MCP server to **user scope** if the user will run the demo outside this repo.
Then the human does W6 (record the Claude Code + ITK-SNAP session; host unlisted on YouTube) and W8 (create
the AbstractScorecard account `QRFBVSUS`, paste `submission.md`, submit). Non-blocking: confirm the abstract
author line with Paul.

## Files to read first (in order)
1. `projects/agentic-api/docs/abstract.md` — the final abstract (source for `submission.md`).
2. `projects/agentic-api/docs/demo_runbook.md` — the recording runbook; **§A "Recording with Claude Code"**
   has the setup + the exact prompts to type.
3. `projects/agentic-api/docs/caimi-submission-requirements.md` — §4 Builder Showcase spec, §6 checklist,
   §7b skeleton, portal details.
4. `projects/agentic-api/PROGRESS_LOG.md` — newest two entries (deliverables; sample videos + MCP wiring),
   including the **env lesson** (mcp vs the DLS FastAPI stack).
5. `itksnap-mcp/README.md`, `itksnap-mcp/docs/DESIGN.md`, `design_docs/media/` (the sample videos).

## Setup (this machine — Linux, RTX 2080 8 GB; recording box = a 4090 for full-res)
- **Base env** (DLS server): `source ~/tk/miniconda3/etc/profile.d/conda.sh && conda activate base`.
  Do NOT `pip install mcp` here — it breaks the DLS server's FastAPI (see traps).
- **MCP server env** (isolated): `~/.venvs/itksnap-mcp` (has `itksnap-mcp[mcp]`). The Claude Code MCP
  registration already points at `~/.venvs/itksnap-mcp/bin/python -m itksnap_mcp.server`.
- Branches: `itksnap`→`sprint/caimi`; `itksnap-dls`→`feature/agentic-api` (pointer NOT recorded — switch
  manually); `itksnap-mcp`→`main`.
- **Build FOREGROUND** if C++ changes: `cmake --build build-release --target ITK-SNAP -j` (never `nohup &`;
  confirm the binary mtime advanced before testing).
- **Live agent-directed demo (the real take):**
  1. base env: `cd itksnap-dls && python -m itksnap_dls --port 8911 --device cuda` (poll `/status`).
  2. `ITK-SNAP -g /tmp/ct3d_bavcta028.nii.gz --agent-listen /tmp/snap-agent.sock` on a **real display**.
  3. **Start a fresh `claude` session in this repo** (MCP loads at startup) and type the runbook §A prompts.
  4. Retake without GPU: ask Claude Code to `apply_file /tmp/p2_proposal_10.nii.gz` (label 1).
  5. Stop the DLS server by PORT: `lsof -ti:8911 | xargs -r kill`.
- Sample-video reproduction (no agent, no GPU): `/tmp/drive_demo.py` + `ffmpeg -f x11grab` (see
  `design_docs/media/README.md`).
- Confidence-gate tests: `cd itksnap-mcp && PYTHONPATH=src python -m pytest tests -q`.

## Known traps
- **Never `pip install mcp` into the DLS base env** — it upgrades `starlette` past FastAPI's pin and breaks
  `itksnap_dls` (`on_startup` TypeError). The MCP server lives in its own venv (`~/.venvs/itksnap-mcp`); the
  DLS server stays in base (`starlette 0.46.2`). They cannot share one env.
- **A fresh Claude Code session is required** to see the `itksnap` MCP tools (loaded at session start). It's
  registered at **local (project) scope** for this repo; use `-s user` to run the demo elsewhere.
- **The video + portal need a HUMAN.** Record ITK-SNAP on a real display (not Xvfb) so the live correction
  is on camera; the AbstractScorecard account (Chrome/Firefox) must be created by a person.
- **Local body CTs are 4D cardiac CTA** — extract a 3-D frame first (`/tmp/ct3d_bavcta028.nii.gz`).
- **DLS upload drops geometry** — `write_label_mask` restores it (`CopyInformation`); proposal + image must
  share the grid, or `apply` reports `changed_voxels: 0`.
- **Never `pkill -f "<string>"` in your own command** (`itksnap_dls`, `ninja ITK-SNAP`) — kill servers by
  port, GUIs by `setsid`+`kill -TERM -<pid>`, builds by `pgrep -x ninja`.
- **Sample videos are illustrative** — software-rendered; the "human" beat is a scripted `apply_box`. The
  final take should show a real paintbrush correction driven from a real Claude Code session.
- **Push state:** `itksnap` `e1aa19d5`, `itksnap-mcp` `0297396`, wrapper checkpoints — all pushed.
  `itksnap-dls` pointer intentionally unrecorded.

## How to work
The tech, the writing, and the agent wiring are done — this is packaging and rehearsal under a tight
deadline. Verify every demo link opens; keep the on-camera correction a real code path; produce copy-paste
portal text so the human's submission is mechanical. Build foreground; kill by port/PID, not `pkill -f`.
Commit inside each submodule first, then bump the wrapper pointer.
