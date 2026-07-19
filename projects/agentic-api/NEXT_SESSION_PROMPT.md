# RESUME — ITK-SNAP Agentic API · CAIMI Builder Showcase sprint

## Current state (read this paragraph first)
We are building a prototype for a **SIIM-CAIMI26 AI Builder Showcase** submission (deadline
**2026-07-24 11:59 PM PST** — ~6 days). Thesis: *"model proposes, human disposes"* — expose expert
human judgement as a **callable, resumable, audited** pipeline step an external agent can invoke. Three
code homes: **`itksnap`** (C++ GUI/logic, branch `sprint/caimi`), **`itksnap-dls`** (Python FastAPI model
server, `feature/agentic-api`), **`itksnap-mcp`** (public repo `main` — the CAIMI link + pip artifact).
**The entire P2 technical backbone is PROVEN LIVE end-to-end** (propose → apply → audit): an agent calls
TotalSegmentator via the DLS server, applies a chosen structure into the running ITK-SNAP over the
`--agent-listen` socket, and reads back a structured audit record `{op, timestamp, actor(agent|human),
changed_voxels, bbox, before/after label counts}` — verified on the RTX 2080 with a real body CT (48
correct thoracic structures; applied the left-upper-lung 1,169,665 vox → agent-tagged audit). Pushed:
`itksnap` `e1aa19d5`, `itksnap-mcp` `9909663`, wrapper `main` (latest checkpoint). **New this session:**
developer docs in `projects/agentic-api/design_docs/` — `DESIGN.md`, `IMPLEMENTATION.md`,
`architecture.svg`, `flow-chart.svg` (excellent source material for the abstract + demo README). **What's
left is the SUBMISSION, not the tech:** the 500-word abstract, a runnable public demo README/manifest, the
confidence gate (nice-to-have), and the video.

## The single next goal
**Draft the submission deliverables: the 500-word abstract + a runnable public demo README/manifest for
`itksnap-mcp`.** The technical backbone is done — the remaining risk is the deadline, and a reviewer-
openable demo + a tight abstract are load-bearing (the review criteria weight Demo/Evidence + Innovation
over rigor). Concretely:
1. **Abstract** — take `docs/sprint_caimi.md` §4 to a tight ≤500 words, six sections in order (Problem ·
   Approach/What You Built · Demo/Evidence · Clinical/Operational Impact · Current Stage · Feedback
   Sought). Use the REAL results in hand (48 TS structures, the audit-record JSON, the MCP-callable flow);
   pull phrasing from `design_docs/DESIGN.md`. Author placeholder = jilei-hao (confirm with Paul).
2. **Public demo README + manifest** in `itksnap-mcp/`: a ≤3-command runnable path (start DLS server →
   launch ITK-SNAP `--agent-listen` → `python demo/run_p2.py --ct <CT>`), fill `demo/manifest.example.yaml`
   → a real `manifest.yaml`, decide the license (MIT vs GPL-3.0), and **mirror the public-facing design
   docs** (`DESIGN.md` + the two SVGs, de-referenced of internal hashes) into `itksnap-mcp/docs/` — that
   repo is the link reviewers open.
3. **(If time) confidence gate** — `itksnap-mcp/src/itksnap_mcp/confidence.py`: run `propose` twice (2
   seeds / fast-vs-full), per-label mask agreement (Dice), decide auto-accept vs route-to-human; wire an
   optional `gate` step into `run_p2.py`.
Then W6 (record Clips A/C) and W8 (submit via portal `QRFBVSUS`, Chrome/Firefox).

## Files to read first (in order)
1. `projects/agentic-api/design_docs/DESIGN.md` + `IMPLEMENTATION.md` — the system explained end to end
   (best source for the abstract + README); `architecture.svg` / `flow-chart.svg` are the figures.
2. `projects/agentic-api/docs/sprint_caimi.md` — the plan; §4 abstract draft, §5 DoD, §1 constraints.
   W1/W2/W4 ✅, W3 ✅ (MCP wired; confidence gate still a placeholder).
3. `projects/agentic-api/PROGRESS_LOG.md` — newest four entries (audit record → P2-loop → full live chain
   → design docs), with commit hashes, the GPU result, and the traps.
4. `projects/agentic-api/docs/caimi-submission-requirements.md` — submission rules, the six-section
   abstract skeleton + word-count exclusions, portal details.
5. `itksnap-mcp/` — `README.md` (needs the runnable path), `demo/run_p2.py`, `demo/manifest.example.yaml`,
   `src/itksnap_mcp/{server,channel,dls_client,confidence}.py`.

## Setup (this machine — Linux, RTX 2080 8 GB; dev/fast-mode only; recording box = a 4090)
- Env: `source ~/tk/miniconda3/etc/profile.d/conda.sh && conda activate base`
  (torch 2.3.1+cu121, TotalSegmentator, `itksnap-dls` editable on `feature/agentic-api`).
- Branches: `itksnap`→`sprint/caimi`; `itksnap-dls`→`feature/agentic-api` (pointer NOT recorded — switch
  manually); `itksnap-mcp`→`main`.
- **Build FOREGROUND:** `cmake --build build-release --target ITK-SNAP -j` (never `nohup … &` — it
  false-completes while ninja keeps building; confirm the binary mtime advanced before testing).
- **Full live P2 run (reproduces session 3):**
  1. `cd itksnap-dls && python -m itksnap_dls --port 8911 --device cuda` (background; poll
     `curl -s localhost:8911/status`).
  2. body CT `/tmp/ct3d_bavcta028.nii.gz` (3D frame-0 of a BAV cardiac CTA, 256×256×181). Regenerate:
     `sitk.Extract(sitk.ReadImage('~/Downloads/img4d_CT_bavcta028_baseline_rs50.nii.gz'), [256,256,181,0], [0,0,0,0])`.
  3. `Xvfb :98 & DISPLAY=:98 setsid ./build-release/ITK-SNAP -g /tmp/ct3d_bavcta028.nii.gz --agent-listen /tmp/snap-agent.sock &`
  4. `PYTHONPATH=itksnap-mcp/src python itksnap-mcp/demo/run_p2.py --ct /tmp/ct3d_bavcta028.nii.gz`
  5. Stop the server by PORT: `lsof -ti:8911 | xargs -r kill` (NEVER `pkill -f itksnap_dls` — self-match).
- Render SVGs to check them: `rsvg-convert -w 1040 design_docs/architecture.svg -o /tmp/a.png`.

## Known traps
- **Local body CTs are 4D cardiac CTA** (`~/Downloads/img4d_CT_bavcta*`, 20 phases) — extract a 3D frame
  before TotalSegmentator (see setup). A cardiac CTA yields heart/aorta/lungs — good demo anatomy.
- **DLS scalar upload drops geometry** (identity). `write_label_mask` restores it via
  `sitk...CopyInformation(source_ct)` so the mask aligns (index-wise) with the CT loaded in ITK-SNAP.
- **Never `pkill -f "<string>"` where `<string>` is in your own command** (`itksnap_dls`, `ninja ITK-SNAP`)
  — it SIGKILLs the tool shell. Kill servers by port (`lsof -ti:PORT | xargs kill`), GUIs by
  `setsid`+`kill -TERM -<pid>`, builds by `pgrep -x ninja`.
- **Actor "arm" model:** `set_actor agent` is consumed by the next real commit (auto-reset to human;
  `"Temporary undo point"` skipped). `get_audit` is not reconciled with `Redo()` (only `Undo` invalidates).
- **Build FOREGROUND** and confirm relink (mtime) before smoke-testing.
- `itksnap-mcp` license undecided (MIT vs GPL-3.0). AbstractScorecard portal account (EventKey `QRFBVSUS`,
  Chrome/Firefox) must be created by a human.
- **Push state:** `itksnap` `e1aa19d5` + `itksnap-mcp` `9909663` + wrapper checkpoints all pushed;
  `itksnap-dls` pointer intentionally unrecorded. Design docs committed in the wrapper this session.

## How to work
Integration over invention; ground claims in real files + results. The tech is done — protect the
deadline: abstract + a reviewer-openable demo first, polish second (rigor is explicitly NOT the primary
criterion). Keep the on-camera human correction a real code path. Build foreground; kill by port/PID, not
`pkill -f`. Commit inside each submodule first, then bump the wrapper pointers.
