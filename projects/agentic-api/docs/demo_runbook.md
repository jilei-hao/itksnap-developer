# Demo Recording Runbook — CAIMI Builder Showcase

Shot-by-shot instructions to record the demo video for the SIIM-CAIMI26 AI Builder Showcase.
The story is **"model proposes, human disposes"**: an agent runs an automatic model, applies a
proposal into an **ITK-SNAP workspace**, and reads back a structured audit record; then a human
expert corrects the result in a live ITK-SNAP opened on that same workspace, and the agent receives
the correction as a machine-readable diff.

> **What changed (workspace-first model).** The `apply` step no longer needs a running ITK-SNAP.
> The agent creates a persistent `.itksnap` **workspace** and merges the proposal into its
> segmentation **headlessly** (via `itksnap-wt` + SimpleITK), computing the audit record from the
> before/after label volumes. A live ITK-SNAP is now an **optional** view/correct surface the agent
> *opens on that workspace* (`open_in_itksnap`) for the human beat. So the GUI's on-camera "reveal"
> moves from the apply step to the moment the agent opens the workspace — the window comes up with
> the proposal already in it.

**Target length:** ~2–3 minutes total. Three clips: **A** (callable / headless apply), **C** (the
audited diff), **B** (the live human handoff on the opened workspace — the visual star). Host on
YouTube (unlisted); put the link in the abstract and in `itksnap-mcp/README.md`.

> All commands and expected outputs below are from a verified dry run on the RTX 2080. Numbers (voxel
> counts, structures) depend on the CT and model settings — **do a dry run first** (last section) and
> paste your real numbers over the examples before filming, so the narration matches the screen.

---

## A. Recording with Claude Code — the authentic agent-directed demo (recommended)

This is the version that shows **you directing an agent**: you type prompts to Claude Code, Claude Code
calls the `itksnap` MCP tools, and ITK-SNAP appears when the agent opens the workspace. The tools are
exposed to Claude Code via a registered MCP server.

### One-time setup (already done on this machine)
- The MCP server runs in an **isolated venv** (`~/.venvs/itksnap-mcp`) so it can't clash with the DLS
  server's FastAPI:
  ```bash
  ~/tk/miniconda3/bin/python -m venv ~/.venvs/itksnap-mcp
  ~/.venvs/itksnap-mcp/bin/pip install -e '/home/jileihao/dev/itksnap-developer/itksnap-mcp[mcp]'
  ```
- Point the server at the ITK-SNAP binaries it needs (headless apply needs only `itksnap-wt`; the
  live-GUI beat needs `ITK-SNAP`). These are read from the environment — set them where Claude Code
  launches the server:
  ```bash
  export ITKSNAP_WT_BIN=/home/jileihao/dev/itksnap-developer/build-release/Utilities/Workspace/itksnap-wt
  export ITKSNAP_BIN=/home/jileihao/dev/itksnap-developer/build-release/ITK-SNAP
  # optional: ITKSNAP_DLS_URL (default http://localhost:8911), ITKSNAP_AGENT_SOCK
  # (default /tmp/snap-agent.sock), ITKSNAP_WORKSPACE_DIR, ITKSNAP_LAUNCH_PREFIX="xvfb-run -a".
  ```
- Registered with Claude Code (local scope for this repo):
  ```bash
  claude mcp add itksnap -- /home/jileihao/.venvs/itksnap-mcp/bin/python -m itksnap_mcp.server
  claude mcp list        # -> itksnap: ... ✔ Connected
  ```
  Tools Claude Code sees:
  `list_models · create_workspace · propose · apply · apply_file · open_in_itksnap · read_audit · set_actor`.

### Screen layout for the take
- **Left:** the **Claude Code terminal** (your prompts → its tool calls).
- **Right:** empty at first (desktop / the DLS log). **ITK-SNAP is not pre-launched** — the agent
  opens it mid-demo with `open_in_itksnap`, and it comes up already showing the proposal.
- DLS server running in a background terminal (base env), only needed for `propose`.

### The conversation (type these to Claude Code)
1. **"Using the `itksnap` tools, list the available segmentation models."** → shows the tool call
   (`list_models`) and result.
2. **"Create an ITK-SNAP workspace for `/tmp/ct3d_bavcta028.nii.gz`."** → Claude Code calls
   `create_workspace` → prints the `.itksnap` path (the durable base everything applies into). No GUI
   yet.
3. **"Run automatic segmentation on that CT and tell me which structures you found."** → Claude Code
   calls `propose`; it lists ~48 structures (heart, aorta, lungs, …).
4. **"Apply the left upper lung lobe into the workspace and show me the audit record."** → Claude Code
   calls `apply` (label 10) → it edits the workspace segmentation **headlessly** (no window) and prints
   the audit record (`actor: agent`, `changed_voxels`, bbox, before/after). Narrate: *no GUI is running
   — the workspace on disk is the source of truth.*
5. **"Open ITK-SNAP on the workspace so I can correct it."** → Claude Code calls
   `open_in_itksnap` (`live=True`) → **ITK-SNAP launches showing the CT with the agent's proposal
   already applied** (red). This is the reveal beat.
6. **(You correct it on camera)** — in ITK-SNAP pick the paintbrush and fix a boundary; a few strokes.
7. **"Read the audit record again."** → Claude Code calls `read_audit` → because a live GUI is now
   attached, the record comes from it and shows **`actor: human`** with your stroke's voxel count.

**Determinism tip:** to avoid re-running the GPU on a retake, tell Claude Code:
**"Apply the cached proposal `/tmp/p2_proposal_10.nii.gz` as label 1 and show the audit"** → it calls
`apply_file` (no model run) into the workspace. This is the exact path verified end-to-end
(MCP client → workspace engine → audit record).

> The three narrative beats below (Clip A / C / B) map onto steps 2–4 / 4-audit / 5-7 of this
> conversation. `demo/run_p2.py` remains a fully-scripted, no-agent fallback if you want a hands-off
> capture.

---

## 0. Pre-flight checklist (do this before you hit record)

- [ ] **Env:** `source ~/tk/miniconda3/etc/profile.d/conda.sh && conda activate base`
- [ ] **ITK-SNAP build is current:** `cmake --build build-release --target ITK-SNAP itksnap-wt -j`
      (foreground). Both binaries are needed — `itksnap-wt` for the headless apply, `ITK-SNAP` for
      the human beat.
- [ ] **Binaries exported** so the MCP server / driver can find them:
      ```bash
      export ITKSNAP_WT_BIN=$PWD/build-release/Utilities/Workspace/itksnap-wt
      export ITKSNAP_BIN=$PWD/build-release/ITK-SNAP
      ```
- [ ] **A 3-D body CT** at a known path, e.g. `/tmp/ct3d_bavcta028.nii.gz`. Regenerate from the 4-D
      cardiac CTA if needed:
      ```bash
      python -c "import SimpleITK as sitk; im=sitk.ReadImage('/home/jileihao/Downloads/img4d_CT_bavcta028_baseline_rs50.nii.gz'); \
      sitk.WriteImage(sitk.Extract(im,[256,256,181,0],[0,0,0,0]), '/tmp/ct3d_bavcta028.nii.gz')"
      ```
- [ ] **DLS model server running** and warm (only needed for `propose`):
      ```bash
      cd itksnap-dls && python -m itksnap_dls --port 8911 --device cuda   # leave running
      curl -s localhost:8911/status                                       # -> {"status":"ok",...}
      ```
      (First launch downloads/loads the model; wait for `/status` before filming.)
- [ ] **A short socket path** for the *live* beat: `/tmp/snap-agent.sock` (AF_UNIX limit ~108 chars).
      The socket is created by ITK-SNAP when the agent opens the workspace with `--agent-listen`; you
      do **not** pre-launch it.
- [ ] **Recording box:** the 4090 gives full-res TotalSegmentator (sharper anatomy on camera). The
      RTX 2080 is fine in fast mode for rehearsal.
- [ ] **Determinism:** cache one good proposal so filming never blocks on the GPU (see dry run).

### Screen layout
- **Left ~55%:** a terminal (large font, e.g. 16–18 pt, cleared) — this is the *agent*.
- **Right ~45%:** starts empty; **ITK-SNAP appears here when the agent opens the workspace** (Clip B).
  Film on a **REAL display** (not Xvfb) so the live human correction is visible on camera.

---

## Clip A — "The agent calls ITK-SNAP as a tool" (callable / headless apply)  · ~45 s

**Message:** an external agent creates a workspace, runs automatic segmentation, and applies a proposal
into that workspace **with no GUI running** — the durable `.itksnap` file is the source of truth.

**On screen:** terminal (agent) on the left; no ITK-SNAP window yet — that is the point.

**Action — run the driver (no `--open` yet):**
```bash
PYTHONPATH=itksnap-mcp/src python itksnap-mcp/demo/run_p2.py --ct /tmp/ct3d_bavcta028.nii.gz
```

**What happens / what to show:**
1. `[create_workspace]` prints the `.itksnap` path — the base everything applies into.
2. `[propose]` prints — TotalSegmentator returns the structures. **Point at the list** (heart, aorta,
   lungs, vertebrae…). Expected (dry run): **48 structures**, e.g. `heart` ≈ 867,916 vox, plus aorta,
   all lung lobes, vena cava, ribs.
3. `[apply]` — the driver merges the largest structure (`lung_upper_lobe_left`) into the **workspace
   segmentation**, headlessly. **No window opens.**
4. `[read_audit]` prints the record (lead into Clip C).

**Narration cue:** "The agent built an ITK-SNAP workspace, proposed a segmentation with an open model,
and applied it into the workspace — headlessly, no GUI required. The workspace is a durable, callable
artifact, not a file drop."

**Optional gate overlay (auto-accept):** to show the confidence gate deciding *auto-accept*, narrate it,
or show a two-run agreement check:
```python
# python (illustrative) — high agreement => auto-accept
from itksnap_mcp.confidence import agreement_gate
print(agreement_gate(run1_labels, run2_labels, threshold=0.9).reason)
```

---

## Clip C — "The correction is a return value" (the audited diff)  · ~30 s

**Message:** the edit comes back as structured, machine-consumable provenance — who changed what, where,
and by how much — and it is the **same record schema** whether computed headlessly or reconstructed in
the live GUI.

**On screen:** zoom the terminal on the audit JSON from `[read_audit]` (Clip A step 4).

**Expected (dry run):**
```json
{
  "op": "Agent apply (proposal)",
  "timestamp": "2026-07-19T02:26:20Z",
  "actor": "agent",
  "changed_voxels": 1169665,
  "bbox": { "valid": true, "min": [84, 2, 0], "max": [247, 189, 180] },
  "before_counts": { "0": 1169665 },
  "after_counts":  { "1": 1169665 }
}
```

**What to highlight (point/zoom in this order):** `actor: "agent"` → `changed_voxels` → `bbox` →
`before_counts` / `after_counts`.

**Narration cue:** "Every edit returns a structured audit record — the actor, the voxel count, the
bounding box, and the before/after label mix. The headless apply computes it from the before/after
label volumes; the live GUI reconstructs the same fields from its undo delta — identical schema either
way. Attributable, reproducible provenance."

---

## Clip B — "Model proposes, human disposes" (the live handoff)  · ~60 s · the star

**Message:** for an uncertain case the agent opens ITK-SNAP on the workspace and a human corrects the
proposal in the *live* app; the agent then reads the correction back — tagged as a human edit.

**On screen:** the terminal (agent) triggers the open; **ITK-SNAP launches showing the proposal already
applied**, then takes focus (the human).

**Steps:**
1. **(Narrate the routing)** "The gate flagged this structure as uncertain, so the agent opened the
   workspace for a human." (Optionally show `agreement_gate(...).route_to_human == True`.)
2. **Agent opens ITK-SNAP on the workspace** — re-run the driver with `--open`, or (in the Claude Code
   take) the `open_in_itksnap` call from step 5:
   ```bash
   PYTHONPATH=itksnap-mcp/src python itksnap-mcp/demo/run_p2.py --ct /tmp/ct3d_bavcta028.nii.gz \
     --label 10 --open
   ```
   **The window comes up with the CT and the agent's red proposal already in it** — this reveal is the
   opening beat of the clip.
3. **Human corrects in ITK-SNAP (on camera):**
   - Select the **paintbrush** tool (toolbar) and confirm the **active label** (the label the agent
     applied, or a dedicated correction label).
   - Paint over a wrong/rough boundary to fix it — a few visible strokes; release the mouse (this
     **commits** the edit). Keep it deliberate and on-screen.
4. **Agent reads the correction back** over the live socket:
   ```bash
   python itksnap-mcp/demo/agent_send.py /tmp/snap-agent.sock get_audit
   ```
   **Expected:** a record with **`"actor": "human"`** and the `changed_voxels` / `bbox` / before-after
   of the human's strokes — e.g.
   ```json
   {"actor":"human","changed_voxels":<N>,"bbox":{...},"before_counts":{...},"after_counts":{...}, ...}
   ```

**Narration cue:** "The agent opened the workspace in a real ITK-SNAP, the expert corrected the
proposal, and the agent received the fix as the same structured record — this time tagged `human`.
Expert judgement becomes a callable, audited pipeline step."

> Why `actor` flips to `human` automatically: the agent's apply armed `actor = agent` and that tag was
> consumed by the apply commit, auto-resetting to `human`; the human's paintbrush stroke is the next
> commit, so it is tagged `human` with no extra step.

---

## Teardown

```bash
lsof -ti:8911 | xargs -r kill        # stop the DLS server BY PORT (never pkill -f itksnap_dls)
# close ITK-SNAP normally (or: kill the process by PID)
```

---

## Retake tips & gotchas

- **Real display for filming.** Run the human beat on an actual display, not Xvfb — the live
  correction is the point; it must be visible. (`ITKSNAP_LAUNCH_PREFIX="xvfb-run -a"` is only for a
  headless dry run.)
- **The reveal is the GUI opening.** Because apply is headless, nothing pops into a *running* window
  mid-apply anymore. Capture the reveal at `open_in_itksnap` — the window comes up already populated.
  Don't wait for a live paint-in during apply; it won't happen.
- **Determinism.** TotalSegmentator output is stable for a fixed CT + settings, but cache one good
  proposal (`--out` in `demo/smoke_totalseg.py`, or keep the applied `*.proposal.nii.gz` next to the
  workspace segmentation) so a retake never blocks on the GPU — replay it with `apply_file`.
- **Pick a clean structure for Clip A** (a large lung lobe reads well) and a structure with a visibly
  rough boundary for Clip B so the correction is obviously meaningful.
- **`agent_send.py` supports `get_audit`/`ping`** with no args; use it for the read-back beat once the
  live GUI is open. Before that (headless), read the record from the driver's `[read_audit]` print or
  the workspace audit log.
- **Don't `pkill -f itksnap_dls` / `pkill -f "ITK-SNAP"`** from the recording shell — it can match and
  kill your own shell. Stop the server by port; close the GUI by window or PID.
- **If `apply` reports `changed_voxels: 0`,** the proposal grid didn't line up with the workspace CT —
  make sure the workspace was created from the *same* CT the agent ran `propose` on (the mask geometry
  is copied from that CT).
- **`itksnap-wt` not found / GUI won't open:** the headless apply needs `ITKSNAP_WT_BIN`; `open_in_itksnap`
  needs `ITKSNAP_BIN`. Export both (Pre-flight) before launching the MCP server or the driver.
- **Word/link hygiene:** after hosting, put the video URL in `docs/abstract.md` (Demo section) and
  `itksnap-mcp/README.md`, and open-test every link before submitting.

---

## Dry run (capture real numbers before filming)

```bash
# 0. binaries (headless engine + GUI)
export ITKSNAP_WT_BIN=$PWD/build-release/Utilities/Workspace/itksnap-wt
export ITKSNAP_BIN=$PWD/build-release/ITK-SNAP
# 1. server (only for propose)
cd itksnap-dls && python -m itksnap_dls --port 8911 --device cuda &   # wait for /status
# 2. the whole flow: create workspace -> propose -> apply (headless) -> open GUI on the workspace
#    (Xvfb :98 is fine for the dry run; use a real display for the real take)
PYTHONPATH=itksnap-mcp/src python itksnap-mcp/demo/run_p2.py --ct /tmp/ct3d_bavcta028.nii.gz --open
# 3. (paint a correction in the GUI), then read the human-tagged record over the socket:
python itksnap-mcp/demo/agent_send.py /tmp/snap-agent.sock get_audit
# 4. teardown
lsof -ti:8911 | xargs -r kill
```

Paste the real `[propose]` structure list, the Clip-C JSON, and the Clip-B `actor:"human"` JSON into the
"Expected" blocks above so the on-camera narration matches exactly.
