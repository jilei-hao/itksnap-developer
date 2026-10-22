# CAIMI26 demo video: plan and cut list

Source of truth for the demo MP4. It is played on its own between slides 3 and 4, not from a
slide. The narration and the length of each beat live in `talk.md`; this file says how each
beat is cut, where the on-screen boxes and arrows go, and which stills the slides use.

```bash
python3 build_video.py            # stills, then the MP4 (about a minute)
python3 build_video.py --stills   # stills only (slide 2 uses one)
```

`build_video.py` fails if the segments of a beat do not add up to that beat's time in
`talk.md`, or if a callout falls outside its beat. `build.py` fails if the beat table below
does not match `talk.md`.

<!--
Times are M:SS.s in the source clip. Positions (framings, blur, callouts) are pixels in the
source clip, so they stay right when a framing changes. Speed 2 plays the segment twice as fast and shows a
"2x speed" badge. Hold freezes the segment's last frame for that many seconds. A framing is a
crop of the source; it is scaled to fit 1920 x 1080, with dark bands where the shape differs.
Blur (x y w h, in source pixels) hides part of that framing.
-->

## Output

| Setting | Value | Why |
|---|---|---|
| Length | the slide 3 time in `talk.md` (3:50) | the whole talk is 7:00 |
| Size | 1920 x 1080, 30 fps | the projector is 16:9 |
| Format | MP4, H.264 + silent AAC | plays in PowerPoint on the Windows podium PC |
| Sound | silent | you narrate live |
| Captions | one per beat, shown for its first 5 seconds | readable without narration |
| Callouts | orange boxes and arrows with a label, timed to the action | practice audience could not tell where to look |
| Credit | the `attribution` line from `talk.md`, small, bottom right, throughout | the CT is CC BY 4.0, and no slide carries it now |

## Clips

- footage: /Users/Shared/Movies/260724_CAIMI-ITKSNAP

| Clip | File | Length | What it shows |
|---|---|---|---|
| c1 | clip-1_basic.mov | 1:16 | list models, create a workspace, open ITK-SNAP |
| c4 | clip-4_full-run.mov | 4:27 | one continuous run: workspace and ITK-SNAP, propose, apply (labels 51 to 63), paintbrush, audit |

Not used: `clip-2_auto-seg.mov`, `clip-3_auto-seg-with-labels.mov`, and `final-demo.mp4` (the
8:42 cut submitted in July). Clip 4 gives one consistent set of label numbers and voxel counts
from the apply to the audit.

## Framings

| Framing | Clip | x | y | w | h | Blur | Shows |
|---|---|---|---|---|---|---|---|
| c1-term | c1 | 0 | 1290 | 1755 | 988 | - | the agent terminal, lower part |
| c4-low | c4 | 0 | 1600 | 1845 | 1038 | - | the agent terminal, lower part: prompts and short answers |
| c4-term | c4 | 0 | 1010 | 1845 | 1628 | - | the whole agent terminal: long answers |
| c4-table | c4 | 0 | 1260 | 1845 | 1100 | - | the table of applied structures |
| c4-both | c4 | 0 | 460 | 3780 | 2178 | 0 460 1845 470 | terminal and ITK-SNAP side by side; the model-server log is blurred |
| c4-snap | c4 | 1890 | 460 | 1880 | 1550 | - | the ITK-SNAP window |

## Beats

| Beat | Title | Caption | Must be readable on screen |
|---|---|---|---|
| 1 | List models | The agent lists the models on the server | the prompt; the table of models |
| 2 | Workspace, and ITK-SNAP opens | It creates a workspace and opens ITK-SNAP | the prompt; the ITK-SNAP window appearing |
| 3 | The proposal | A model proposes. Nothing is written yet | the prompt; "68 structures"; "proposed and cached (not applied)" |
| 4 | Apply into the open window | The agent applies 11 structures, each with its name | structures appearing in ITK-SNAP; the table with heart 242,476 |
| 5 | The correction | A person corrects it with the paintbrush | the paintbrush strokes on heart and aorta |
| 6 | The audit | The agent reads back who changed what | "run audit"; 15 records; the four human rows |

## Segments

| Beat | Clip | In | Out | Speed | Hold | Framing | Note |
|---|---|---|---|---|---|---|---|
| 1 | c1 | 0:02.0 | 0:14.5 | 2 | 0 | c1-term | typing the prompt |
| 1 | c1 | 0:22.5 | 0:30.0 | 1 | 6.25 | c1-term | the model table (ends before the next prompt is typed) |
| 2 | c4 | 0:04.0 | 0:19.5 | 2 | 0 | c4-low | typing the prompt |
| 2 | c4 | 0:19.5 | 0:30.0 | 1 | 0 | c4-low | the workspace is created |
| 2 | c4 | 0:30.0 | 0:36.0 | 1 | 5.75 | c4-both | ITK-SNAP opens on the right |
| 3 | c4 | 0:36.0 | 0:59.0 | 2 | 0 | c4-low | typing the prompt |
| 3 | c4 | 0:59.0 | 1:04.5 | 1 | 0 | c4-low | the call starts; the model wait is cut after this |
| 3 | c4 | 1:46.5 | 2:00.0 | 1 | 4.5 | c4-term | the 68 structures arrive |
| 4 | c4 | 2:00.0 | 2:20.0 | 2 | 0 | c4-low | typing the prompt |
| 4 | c4 | 2:29.5 | 3:13.0 | 1 | 0 | c4-both | structures appear in ITK-SNAP |
| 4 | c4 | 3:13.0 | 3:19.5 | 1 | 0 | c4-table | the table of 11 structures |
| 5 | c4 | 3:19.5 | 3:56.0 | 1 | 3.5 | c4-snap | zoom in, paintbrush on heart and aorta |
| 6 | c4 | 3:56.0 | 4:02.0 | 1 | 0 | c4-low | typing "run audit" |
| 6 | c4 | 4:02.0 | 4:13.0 | 2 | 0 | c4-low | the agent reads the log |
| 6 | c4 | 4:13.0 | 4:26.5 | 1 | 20 | c4-low | the four human records |

Cut points were placed from frame differences in the clips and checked frame by frame.

## Callouts

Shape `box` takes `x y w h`; shape `arrow` takes `x1 y1 x2 y2`, tail to head, with the label at
the tail. A callout shows from its From time to its To time; if To reaches the end of a
segment, it stays up through that segment's hold.

| Beat | Clip | From | To | Shape | Where | Label |
|---|---|---|---|---|---|---|
| 1 | c1 | 0:03.0 | 0:14.0 | box | 0 1432 1755 64 | You type a request |
| 1 | c1 | 0:23.0 | 0:26.0 | box | 40 1600 1600 300 | Models on the server |
| 1 | c1 | 0:26.0 | 0:30.0 | box | 40 1828 1600 58 | TotalSegmentator: fully automatic |
| 2 | c4 | 0:31.5 | 0:36.0 | box | 1640 580 1840 1528 | ITK-SNAP opens, connected to the agent |
| 3 | c4 | 1:55.0 | 2:00.0 | box | 10 1208 1835 58 | 68 structures proposed, none applied yet |
| 4 | c4 | 2:33.0 | 3:13.0 | box | 3000 520 730 1480 | Structures appear here, one by one |
| 4 | c4 | 2:33.0 | 3:13.0 | arrow | 1700 2000 2990 1300 | Agent applies |
| 4 | c4 | 3:14.5 | 3:19.5 | box | 40 1478 840 54 | Heart: 242,476 voxels, named |
| 5 | c4 | 3:29.0 | 3:56.0 | box | 1905 755 345 445 | Paintbrush |
| 5 | c4 | 3:33.0 | 3:56.0 | box | 2255 525 1475 715 | Corrections on heart and aorta |
| 6 | c4 | 4:16.5 | 4:20.0 | box | 10 1735 1835 62 | 15 records: 11 by the agent, 4 by the person |
| 6 | c4 | 4:20.0 | 4:26.5 | box | 40 1925 1520 262 | Each human edit: tool, label, voxels, time |

## Stills

| Still | Clip | At | Framing |
|---|---|---|---|
| itksnap | c4 | 3:19.0 | c4-snap |

## Open items

- [ ] Watch the whole render at full size: the cuts, the callouts landing on the right thing,
      and whether the terminal text can be read on a projector.
- [ ] Play the MP4 on the Windows machine.
