# RESUME — ITK-SNAP Agentic API · CAIMI Builder Showcase sprint

## Current state (read this paragraph first)
We are submitting a **SIIM-CAIMI26 AI Builder Showcase** entry by **2026-07-24 11:59 PM PST** (deadline
is close — treat it as the hard constraint). Thesis: *"model proposes, human disposes"* — expose an
expert's segmentation correction as a **callable, resumable, audited** pipeline step. Three repos:
**`itksnap`** (C++ GUI/logic, `sprint/caimi`), **`itksnap-dls`** (FastAPI model server,
`feature/agentic-api`), **`itksnap-mcp`** (public repo `main` — the CAIMI demo link). **Everything
technical is DONE and proven live:** the full `propose → apply → audit` backbone runs end-to-end
(TotalSegmentator → apply a structure into the live ITK-SNAP over the `--agent-listen` socket → read a
structured audit record `{op, actor(agent|human), changed_voxels, bbox, before/after}`), verified on a
GPU with a real body CT (48 thoracic structures; applied left-upper-lung 1,169,665 vox). **The
submission materials are DONE too:** the ≤500-word abstract (`docs/abstract.md`, 456 words), the public
repo is MIT-licensed with a rewritten README (3-command runnable path), mirrored design docs
(`itksnap-mcp/docs/`), and a tested confidence gate. Pushed: `itksnap` `e1aa19d5`, `itksnap-mcp`
`f80d880`, wrapper `main` (latest checkpoint). **What's left is packaging + the two human-gated steps:**
record the video, and submit through the portal.

## The single next goal
**Assemble the recording runbook + a portal-ready submission package, and do a full dry run.** These are
the last things the assistant can do before the human records and submits. Concretely:
1. **Demo runbook** (write to `projects/agentic-api/docs/demo_runbook.md`): an exact, deterministic
   click/command sequence for the video — **Clip A** (agent auto-accepts an easy case: propose → apply →
   audit shown), **Clip C** (the audited diff: show the returned JSON), and if desired **Clip B** (the
   live human correction: expert paints in the GUI, `read_audit` returns the `actor:"human"` diff).
   Include the exact commands (from the README's 3-command path) and what to show on screen at each beat.
2. **Full dry run** on a GPU box (ideally the 4090 for full-res): run `demo/run_p2.py` end-to-end, plus
   a human paintbrush correction + a second `read_audit`, and capture the real JSON outputs to paste into
   the runbook. Shake out any last issues before filming. (Reproduce with the setup commands below.)
3. **Portal-ready package** (`projects/agentic-api/docs/submission.md`): the six section texts ready to
   paste into AbstractScorecard, plus the title, keywords, and the demo/repo/video links — with **every
   link opened-tested for reachability** (the repo is public; the video URL is a placeholder until
   recorded). Re-verify the abstract word count.
Then the human does W6 (record + host the video, unlisted YouTube) and W8 (create the portal account,
paste, submit). Non-blocking: confirm the abstract author line/affiliation with Paul.

## Files to read first (in order)
1. `projects/agentic-api/docs/abstract.md` — the final abstract (source for the portal package).
2. `projects/agentic-api/docs/caimi-submission-requirements.md` — §4 Builder Showcase spec, §6 checklist,
   §7b skeleton, portal details (EventKey `QRFBVSUS`, Chrome/Firefox).
3. `projects/agentic-api/PROGRESS_LOG.md` — newest entry (this deliverables session) + the full-live-chain
   entry (the demo commands + the real JSON to reproduce).
4. `itksnap-mcp/README.md` (the 3-command path), `itksnap-mcp/docs/DESIGN.md` + the two SVGs,
   `itksnap-mcp/demo/run_p2.py`.
5. `projects/agentic-api/docs/sprint_caimi.md` — the plan; §5 Definition of Done (tick as you go).

## Setup (this machine — Linux, RTX 2080 8 GB; recording box = a 4090 for full-res)
- Env: `source ~/tk/miniconda3/etc/profile.d/conda.sh && conda activate base`.
- Branches: `itksnap`→`sprint/caimi`; `itksnap-dls`→`feature/agentic-api` (pointer NOT recorded — switch
  manually); `itksnap-mcp`→`main`.
- **Build FOREGROUND** if any C++ change is needed: `cmake --build build-release --target ITK-SNAP -j`
  (never `nohup … &` — it false-completes; confirm the binary mtime advanced before testing).
- **Full live P2 dry run (reproduces the demo):**
  1. `cd itksnap-dls && python -m itksnap_dls --port 8911 --device cuda` (background; poll
     `curl -s localhost:8911/status`).
  2. body CT `/tmp/ct3d_bavcta028.nii.gz` (3-D frame-0 of a BAV cardiac CTA, 256×256×181). Regenerate:
     `sitk.Extract(sitk.ReadImage('~/Downloads/img4d_CT_bavcta028_baseline_rs50.nii.gz'), [256,256,181,0], [0,0,0,0])`.
  3. `Xvfb :98 & DISPLAY=:98 setsid ./build-release/ITK-SNAP -g /tmp/ct3d_bavcta028.nii.gz --agent-listen /tmp/snap-agent.sock &`
     (for FILMING, run ITK-SNAP on a real display, not Xvfb, so the GUI is visible.)
  4. `PYTHONPATH=itksnap-mcp/src python itksnap-mcp/demo/run_p2.py --ct /tmp/ct3d_bavcta028.nii.gz`
  5. For the human beat: paint a correction in the GUI, then re-send `get_audit` (see `/tmp/apply_smoke.py`
     or `itksnap-mcp/demo/agent_send.py`) → expect `actor:"human"`.
  6. Stop the server by PORT: `lsof -ti:8911 | xargs -r kill` (NEVER `pkill -f itksnap_dls` — self-match).
- Confidence-gate tests: `cd itksnap-mcp && PYTHONPATH=src python -m pytest tests -q`.

## Known traps
- **The video and the portal need a HUMAN** — the assistant can prepare the runbook, dry-run, and paste-
  ready package, but cannot record or create the AbstractScorecard account (Chrome/Firefox only).
- **For filming, run ITK-SNAP on a real display** (not Xvfb) so the live human correction is on camera —
  that beat is the visual star; keep it a real code path.
- **Local body CTs are 4D cardiac CTA** — extract a 3-D frame first (see setup).
- **DLS upload drops geometry** — `write_label_mask` restores it via `CopyInformation`; proposal and image
  must share the voxel grid.
- **Never `pkill -f "<string>"` in your own command** (`itksnap_dls`, `ninja ITK-SNAP`) — it kills the tool
  shell. Kill servers by port, GUIs by `setsid`+`kill -TERM -<pid>`, builds by `pgrep -x ninja`.
- **Actor arm model:** `set_actor agent` is consumed by the next commit (auto-reset to human);
  `get_audit` is not reconciled with `Redo()`.
- **Push state:** `itksnap` `e1aa19d5`, `itksnap-mcp` `f80d880`, wrapper checkpoints — all pushed.
  `itksnap-dls` pointer intentionally unrecorded.

## How to work
The tech and the writing are done — this is packaging and rehearsal under a tight deadline. Verify every
demo link opens; keep the on-camera correction a real code path; prepare copy-paste-ready portal text so
the human's submission is mechanical. Build foreground; kill by port/PID, not `pkill -f`. Commit inside
each submodule first, then bump the wrapper pointer.
