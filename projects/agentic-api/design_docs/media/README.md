# Sample demo media

Illustrative screen recordings of the agentic-API concept — an external agent driving the **live**
ITK-SNAP GUI over the `--agent-listen` socket, with a real TotalSegmentator proposal appearing on the
slices and a correction committed on top.

| File | What it shows |
|---|---|
| `agentic-demo.mp4` (15 s) | The full beat: CT loads → agent applies the proposed **left lung** (red, `actor: agent`, 1,169,665 voxels) → a **correction** (green, `actor: human`, 16,368 voxels) → captioned. |
| `agentic-demo.gif` | Same, as a GIF for embedding in READMEs / slides. |
| `still-agent-apply.png` | Frame at the agent-apply beat. |
| `still-human-correction.png` | Frame at the human-correction beat. |
| `drive_demo.py` | The script that drove the GUI over the socket (paced for recording). |

## How it was made (reproducible)

Recorded with `ffmpeg -f x11grab` on an `Xvfb :99` virtual display, driving ITK-SNAP over the socket:

```bash
Xvfb :99 -screen 0 1280x800x24 &
DISPLAY=:99 ITK-SNAP -g /tmp/ct3d_bavcta028.nii.gz --agent-listen /tmp/snap-agent.sock &
DISPLAY=:99 ffmpeg -f x11grab -video_size 1280x800 -framerate 15 -i :99 -t 15 demo_raw.mp4 &
python3 drive_demo.py /tmp/snap-agent.sock          # scrub slices, apply proposal, apply correction
# captions added afterward with a drawtext filtergraph (title bar + timed lower-thirds).
```

The applied mask `/tmp/p2_proposal_10.nii.gz` is a cached TotalSegmentator result (left upper lung lobe)
from the earlier live GPU run, so this recording needs **no GPU / DLS server**.

## Caveats — these are SAMPLES, not the final submission video

- **Software-rendered** under Xvfb (llvmpipe), 1280×800. The real take should be on a normal display,
  ideally the 4090 box for full-res anatomy.
- **The "human correction" is scripted** — an unarmed `apply_box` edit standing in for a real paintbrush
  stroke. It is genuinely tagged `actor: human` by the real audit logic (the agent's apply consumed the
  `agent` tag, so the next commit auto-tags `human`), but on camera the final video should show a real
  expert painting with the paintbrush tool (see `../../docs/demo_runbook.md`, Clip B).
- The title bar overlaps ITK-SNAP's menu bar (cosmetic).
