# Demo Recording Runbook — CAIMI Builder Showcase

Shot-by-shot instructions to record the demo video for the SIIM-CAIMI26 AI Builder Showcase.
The story is **"model proposes, human disposes"**: an agent runs an automatic model, applies a
proposal into the *live* ITK-SNAP, and reads back a structured audit record; then a human expert
corrects the result and the agent receives the correction as a machine-readable diff.

**Target length:** ~2–3 minutes total. Three clips: **A** (callable / auto-accept), **C** (the audited
diff), **B** (the live human handoff — the visual star). Host on YouTube (unlisted); put the link in the
abstract and in `itksnap-mcp/README.md`.

> All commands and expected outputs below are from a verified dry run on the RTX 2080. Numbers (voxel
> counts, structures) depend on the CT and model settings — **do a dry run first** (last section) and
> paste your real numbers over the examples before filming, so the narration matches the screen.

---

## A. Recording with Claude Code — the authentic agent-directed demo (recommended)

This is the version that shows **you directing an agent**: you type prompts to Claude Code, Claude Code
calls the `itksnap` MCP tools, and ITK-SNAP reacts live. The tools are exposed to Claude Code via a
registered MCP server.

### One-time setup (already done on this machine)
- The MCP server runs in an **isolated venv** (`~/.venvs/itksnap-mcp`) so it can't clash with the DLS
  server's FastAPI:
  ```bash
  ~/tk/miniconda3/bin/python -m venv ~/.venvs/itksnap-mcp
  ~/.venvs/itksnap-mcp/bin/pip install -e '/home/jileihao/dev/itksnap-developer/itksnap-mcp[mcp]'
  ```
- Registered with Claude Code (local scope for this repo):
  ```bash
  claude mcp add itksnap -- /home/jileihao/.venvs/itksnap-mcp/bin/python -m itksnap_mcp.server
  claude mcp list        # -> itksnap: ... ✔ Connected
  ```
  Tools Claude Code sees: `list_models · propose · apply · apply_file · read_audit · set_actor`.
  (Point the server at a different socket/URL with env vars `ITKSNAP_AGENT_SOCK`, `ITKSNAP_DLS_URL`.)

### Screen layout for the take
- **Left:** the **Claude Code terminal** (your prompts → its tool calls).
- **Right:** the **live ITK-SNAP** on a real display (`ITK-SNAP -g <ct> --agent-listen /tmp/snap-agent.sock`).
- DLS server running in a background terminal (base env).

### The conversation (type these to Claude Code)
1. **"Using the `itksnap` tools, list the available segmentation models."** → shows the tool call
   (`list_models`) and result.
2. **"Run automatic segmentation on `/tmp/ct3d_bavcta028.nii.gz` and tell me which structures you
   found."** → Claude Code calls `propose`; it lists ~48 structures (heart, aorta, lungs, …).
3. **"Apply the left upper lung lobe into ITK-SNAP and show me the audit record."** → Claude Code calls
   `apply` (label 10) → **the red segmentation appears live in ITK-SNAP** → it prints the audit record
   (`actor: agent`, `changed_voxels`, bbox, before/after).
4. **(You correct it on camera)** — in ITK-SNAP pick the paintbrush and fix a boundary; a few strokes.
5. **"Read the audit record again."** → Claude Code calls `read_audit` → the record now shows
   **`actor: human`** with your stroke's voxel count.

**Determinism tip:** to avoid re-running the GPU on a retake, tell Claude Code:
**"Apply the cached proposal `/tmp/p2_proposal_10.nii.gz` as label 1 and show the audit"** → it calls
`apply_file` (no model run). This is the exact path verified end-to-end (MCP client → server → ITK-SNAP).

> The three narrative beats below (Clip A / C / B) map onto steps 3 / 3-audit / 4-5 of this conversation.
> `demo/run_p2.py` remains as a fully-scripted, no-agent fallback if you want a hands-off capture.

---

## 0. Pre-flight checklist (do this before you hit record)

- [ ] **Env:** `source ~/tk/miniconda3/etc/profile.d/conda.sh && conda activate base`
- [ ] **ITK-SNAP build is current:** `cmake --build build-release --target ITK-SNAP -j` (foreground).
- [ ] **A 3-D body CT** at a known path, e.g. `/tmp/ct3d_bavcta028.nii.gz`. Regenerate from the 4-D
      cardiac CTA if needed:
      ```bash
      python -c "import SimpleITK as sitk; im=sitk.ReadImage('/home/jileihao/Downloads/img4d_CT_bavcta028_baseline_rs50.nii.gz'); \
      sitk.WriteImage(sitk.Extract(im,[256,256,181,0],[0,0,0,0]), '/tmp/ct3d_bavcta028.nii.gz')"
      ```
- [ ] **DLS model server running** and warm:
      ```bash
      cd itksnap-dls && python -m itksnap_dls --port 8911 --device cuda   # leave running
      curl -s localhost:8911/status                                       # -> {"status":"ok",...}
      ```
      (First launch downloads/loads the model; wait for `/status` before filming.)
- [ ] **A short socket path:** `/tmp/snap-agent.sock` (AF_UNIX limit ~108 chars).
- [ ] **Recording box:** the 4090 gives full-res TotalSegmentator (sharper anatomy on camera). The
      RTX 2080 is fine in fast mode for rehearsal.
- [ ] **Determinism:** cache one good proposal so filming never blocks on the GPU (see dry run).

### Screen layout
- **Left ~55%:** a terminal (large font, e.g. 16–18 pt, cleared) — this is the *agent*.
- **Right ~45%:** the **ITK-SNAP window on a REAL display** (not Xvfb — the live GUI must be on camera).
- Have the CT already loaded in ITK-SNAP with the command channel open:
  ```bash
  ./build-release/ITK-SNAP -g /tmp/ct3d_bavcta028.nii.gz --agent-listen /tmp/snap-agent.sock
  ```
- Sanity-check the channel before recording: `python itksnap-mcp/demo/agent_send.py /tmp/snap-agent.sock ping` → `pong`.

---

## Clip A — "The agent calls ITK-SNAP as a tool" (callable / auto-accept)  · ~45 s

**Message:** an external agent runs automatic segmentation and applies it into the live app — no human
needed for the easy case.

**On screen:** terminal (agent) on the left, ITK-SNAP on the right showing the CT.

**Action — run the driver:**
```bash
PYTHONPATH=itksnap-mcp/src python itksnap-mcp/demo/run_p2.py --ct /tmp/ct3d_bavcta028.nii.gz
```

**What happens / what to show:**
1. `[propose]` prints — TotalSegmentator returns the structures. **Point at the list** (heart, aorta,
   lungs, vertebrae…). Expected (dry run): **48 structures**, e.g. `heart` ≈ 867,916 vox, plus aorta,
   all lung lobes, vena cava, ribs.
2. `[apply]` — the driver applies the largest structure (`lung_upper_lobe_left`) into ITK-SNAP.
   **The segmentation appears in the ITK-SNAP slices live** — this is the "callable" beat.
3. `[read_audit]` prints the record (lead into Clip C).

**Narration cue:** "The agent proposed a segmentation with an open model and applied it directly into the
running ITK-SNAP — a callable tool, not a file drop."

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
and by how much.

**On screen:** zoom the terminal on the audit JSON from `[read_audit]` (Clip A step 3).

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
bounding box, and the before/after label mix. Attributable, reproducible provenance."

---

## Clip B — "Model proposes, human disposes" (the live handoff)  · ~60 s · the star

**Message:** for an uncertain case the agent routes to a human, who corrects it in the *same* live
ITK-SNAP; the agent then reads the correction back — tagged as a human edit.

**On screen:** ITK-SNAP in focus (the human), terminal visible (the agent).

**Steps:**
1. **(Narrate the routing)** "The gate flagged this structure as uncertain, so the agent routed it to a
   human." (Optionally show `agreement_gate(...).route_to_human == True`.)
2. **Human corrects in ITK-SNAP (on camera):**
   - Select the **paintbrush** tool (toolbar) and confirm the **active label** (the label the agent
     applied, or a dedicated correction label).
   - Paint over a wrong/rough boundary to fix it — a few visible strokes; release the mouse (this
     **commits** the edit). Keep it deliberate and on-screen.
3. **Agent reads the correction back:**
   ```bash
   python itksnap-mcp/demo/agent_send.py /tmp/snap-agent.sock get_audit
   ```
   **Expected:** a record with **`"actor": "human"`** and the `changed_voxels` / `bbox` / before-after
   of the human's strokes — e.g.
   ```json
   {"actor":"human","changed_voxels":<N>,"bbox":{...},"before_counts":{...},"after_counts":{...}, ...}
   ```

**Narration cue:** "The expert corrected the proposal in the live app, and the agent received the fix as
the same structured record — this time tagged `human`. Expert judgement becomes a callable, audited
pipeline step."

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

- **Real display for filming.** Run ITK-SNAP on an actual display, not Xvfb — the live human correction
  is the point; it must be visible.
- **Determinism.** TotalSegmentator output is stable for a fixed CT + settings, but cache one good
  proposal (`--out` in `demo/smoke_totalseg.py`, or keep the applied `/tmp/itksnap_mcp_proposal_*.nii.gz`)
  so a retake never blocks on the GPU.
- **Pick a clean structure for Clip A** (a large lung lobe reads well) and a structure with a visibly
  rough boundary for Clip B so the correction is obviously meaningful.
- **`agent_send.py` supports `get_audit`/`ping`** with no args; use it for the read-back beats.
- **Don't `pkill -f itksnap_dls` / `pkill -f "ITK-SNAP"`** from the recording shell — it can match and
  kill your own shell. Stop the server by port; close the GUI by window or PID.
- **If `apply` reports `changed_voxels: 0`,** the proposal grid didn't line up with the loaded CT —
  make sure ITK-SNAP loaded the *same* CT the agent ran `propose` on (the mask geometry is copied from
  that CT).
- **Word/link hygiene:** after hosting, put the video URL in `docs/abstract.md` (Demo section) and
  `itksnap-mcp/README.md`, and open-test every link before submitting.

---

## Dry run (capture real numbers before filming)

```bash
# 1. server
cd itksnap-dls && python -m itksnap_dls --port 8911 --device cuda &   # wait for /status
# 2. ITK-SNAP (real display for the real take; Xvfb :98 is fine for the dry run)
./build-release/ITK-SNAP -g /tmp/ct3d_bavcta028.nii.gz --agent-listen /tmp/snap-agent.sock &
# 3. the flow
PYTHONPATH=itksnap-mcp/src python itksnap-mcp/demo/run_p2.py --ct /tmp/ct3d_bavcta028.nii.gz
# 4. (paint a correction in the GUI), then:
python itksnap-mcp/demo/agent_send.py /tmp/snap-agent.sock get_audit
# 5. teardown
lsof -ti:8911 | xargs -r kill
```

Paste the real `[propose]` structure list, the Clip-C JSON, and the Clip-B `actor:"human"` JSON into the
"Expected" blocks above so the on-camera narration matches exactly.
