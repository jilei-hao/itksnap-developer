# Submission figures — captions and upload notes

Assets for the SIIM-CAIMI26 **AI Builder Showcase** submission (`docs/abstract.md`).
Captions, per §4 of `../caimi-submission-requirements.md`, **do not count** toward the 500-word body limit.

| Slot | Source SVG | Rendered PNG | Status |
|---|---|---|---|
| Figure 1 | `../../design_docs/flow-chart.svg` (canonical, workspace-first) | `fig1_flow.png` | ready |
| *(Figure 2)* | *two-panel GUI screenshot: agent proposal vs. human correction* | — | **not built** — needs a real paintbrush take (see below) |
| Table 1 | `fig3_audit_record.svg` | `fig3_audit_record.png` | ready |

Numbering is deliberately **Figure 1 / Table 1**, not Figure 1/2/3 — so that dropping the
screenshot slot requires no renumbering of the other two or of the abstract body.

> **Figure 1 is rendered from the canonical `design_docs/flow-chart.svg`** (the redrawn
> workspace-first flow), not a separate SVG — this honors the wrapper↔itksnap-mcp figure
> dedup, so there is only one flow-chart source. The earlier standalone `fig1_flow.svg`
> (a pre-workspace-first draft that showed apply going into the live GUI) was **removed**.
>
> ⚠️ **Stale numbers:** Figure 1 (beat 6) and Table 1 still show the bavcta028 run
> (`changed_voxels = 1,169,665`), and the abstract's Demo section still says "48 …
> thoracic structures / a body CT." These are placeholders from the earlier private-data
> run. Once the public demo hero case is locked, update all three together: the Demo
> number, Figure 1 beat 6, and Table 1.

Both PNGs re-render at 2× via headless Chrome:
```bash
cd projects/agentic-api
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# Figure 1 (viewBox 1180×860):
"$CHROME" --headless --disable-gpu --screenshot=docs/figures/fig1_flow.png --window-size=1180,860 \
  --force-device-scale-factor=2 --default-background-color=FFFFFFFF --hide-scrollbars "file://$PWD/design_docs/flow-chart.svg"
# Table 1 (viewBox 980×596):
"$CHROME" --headless --disable-gpu --screenshot=docs/figures/fig3_audit_record.png --window-size=980,596 \
  --force-device-scale-factor=2 --default-background-color=FFFFFFFF --hide-scrollbars "file://$PWD/docs/figures/fig3_audit_record.svg"
```

---

## Figure 1 — caption

> **Figure 1. One end-to-end run: a model and a human called as two steps in the same pipeline.**
> An agent requests an automatic segmentation from an open model server (TotalSegmentator), then
> applies one proposed structure into a *running* ITK-SNAP over a local JSON-RPC command channel —
> so the edit takes the identical code path a mouse click would. A human expert then corrects that
> proposal in the same live session. Every committed edit returns a structured audit record, and
> the actor tag is the only thing that differs between the machine's edit and the human's.
> Confidence-gated routing (dashed) is planned, not yet implemented.

## Table 1 — caption

> **Table 1. What comes back: the audit record for one committed edit.**
> Values are from the verified end-to-end run — a proposed left upper lung lobe applied into the
> live application on a body CT. The record is reconstructed at commit time from the edit
> ITK-SNAP already stores for undo (`old = new − delta`), so it is captured at a single chokepoint
> and is identical whichever of the application's eleven editing tools made the change; a human
> correction returns the same structure with `actor: "human"`. We are seeking feedback on which of
> these fields matter most for downstream model fine-tuning and quality auditing.

---

## Body-text edits these figures enable

Captions are free words, so move detail out of the 500-word body and cite the figure instead:

1. **`abstract.md:22`** — replace the inline JSON blob
   (`` for example `{actor: agent, changed_voxels: 1169665, bbox: …}` ``) with `(Table 1)`.
   Frees ~35–50 words and reads better; the full record is in the table with its field semantics.
2. **`abstract.md:19`** — the two design choices (reconstructed-from-undo-delta, GUI-thread command
   channel) are both carried by Figure 1 and its caption. The body can compress to one sentence and
   cite `(Figure 1)`, freeing room for a sentence on confidence-gated routing or on where this
   plugs into an existing annotation workflow.

## Upload notes

- **Confirm the figure allowance in the portal before uploading.** §4 of the requirements file is
  silent on figure count for the Builder Showcase; only the Experiential track documents "up to 3."
- Upload the **PNGs** (1960 px wide, ≈300 dpi at 6.5″); SVG uploads are usually rejected.
- Re-render after any SVG edit:
  ```bash
  cd projects/agentic-api/docs/figures && "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --screenshot=fig1_flow.png --window-size=980,676 --force-device-scale-factor=2 --default-background-color=FFFFFFFF --hide-scrollbars "file://$PWD/fig1_flow.svg"
  ```
  (Table 1 uses `--window-size=980,596` and its own filenames.)

## Open honesty item — reads on both Figure 2 and the abstract body

Figure 1 beat 5 shows the expert correcting with the paintbrush. That is the design, and the
single-chokepoint argument means a paintbrush edit genuinely produces the same record — but as of
now **no real expert paintbrush correction has been logged**: the "human correction" in the sample
media is a scripted `apply_box` stand-in (genuinely tagged `actor: "human"` by the real audit
logic, but a box, not expert judgment). This is fine for a flow diagram. It is *not* fine for a
screenshot presented as evidence, which is why Figure 2 is blocked on a real take.

It also reads on **`abstract.md:22`**: "The expert then corrected the result in the GUI" describes
the scripted edit. Either record a real correction before submitting, or tighten that sentence.
