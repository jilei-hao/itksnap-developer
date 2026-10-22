# CAIMI26 talk: slides and script

Source of truth for the slides, the speaker notes and the rehearsal script.
Edit this file, then run `python3 build.py`. Never edit the files in `build/`.

<!--
How this file is read by build.py:

  ## Meta              "- key: value" lines. In `title`, a " | " forces a line break on the slide.
  ## Slide N: Title    one slide. Under it, "- layout:" and "- time:" (M:SS) are required.
  ### <Heading>        a block of on-slide content. Most headings are printed on the slide as a
                       small label, so renaming the heading renames the label.
  ### Say              what you say on that slide. [Text in square brackets] is a stage
                       direction: it is shown in the script but not counted as spoken words.
  ## Video: Title    the demo video, played on its own between two slides. It is not a
                       slide. "- time:" and "- file:" are required.
  ### Beat N: Title (M:SS)   video section only: one part of the video and its narration.

  In lists, "**Bold lead.** rest" becomes a bold line with a lighter line under it.
  Layouts and what they expect are listed in README.md. Comments like this one are ignored.
-->

## Meta

- title: ITK-SNAP as an | Agent-Callable Tool
- subtitle: Expert Human Correction as a Resumable, Audited Pipeline Step
- presenter: Jilei Hao
- degree:
- authors: Jilei Hao, Alison M. Pouch, Paul A. Yushkevich
- institution: University of Pennsylvania
- session: AI Builder Showcase  ·  Session 1007  ·  October 26, 2026
- output: CAIMI26_ITK-SNAP_Hao
- slot: 7:00
- max slides: 5
- pace: 150

<!-- authors are in submission order; the presenter's name is printed in bold.
     slot and max slides are the organisers' limits. pace is the fastest you speak
     comfortably, in words per minute; the build fails if any slide needs more. -->

## Slide 1: Title slide

- layout: title
- time: 0:10

### Say

Thank you. I'm Jilei Hao, from the University of Pennsylvania. This is joint work with Alison
Pouch and Paul Yushkevich.

## Slide 2: ITK-SNAP and its deep-learning server

- layout: context
- time: 0:45
- image: build/still_itksnap.jpg

<!-- The image is a still from the demo footage, extracted by build_video.py (see Stills in
     video.md). -->

### ITK-SNAP

- Open-source 3D medical image segmentation
- Linked 2D views and a 3D view of each image
- Manual and semi-automatic segmentation tools

### Deep-learning server

- A separate model server, often on a GPU
- Runs an interactive AI model, nnInteractive
- A person guides it with clicks and scribbles

> We added an automatic model to the server, and a way for an AI agent to drive ITK-SNAP.

### Say

First, what we started from. ITK-SNAP is open-source software for segmenting 3D medical
images. It shows each image in linked 2D views and a 3D view, with manual tools like the
paintbrush, and semi-automatic tools. ITK-SNAP also has a
deep-learning server: a separate program, usually on a GPU machine, that runs AI models. Today
its model is interactive: a person guides it with clicks and scribbles. We added an automatic
model to that server, and a way for an AI agent to drive ITK-SNAP.

## Slide 3: Corrections are manual and unrecorded

- layout: problem-solution
- time: 0:45

### Today

1. **Models are not perfect.** A person still has to check and correct the result.
2. **The pipeline stops.** Someone opens the image, fixes it, and passes the file back by hand.
3. **The fix is not recorded.** It is saved as a new mask. Change history is lost.

### What we built

<!-- Three boxes, left to right. Arrows, in order: centre to left, left to centre,
     centre to right, right to centre. The last arrow is the highlighted one. -->

| Box | Role |
|---|---|
| Model server | proposes a segmentation |
| AI agent | calls both as tools (MCP) |
| ITK-SNAP | a person corrects it here |

- arrows: Request auto segmentation, Auto segmentation result, Route for human correction, audit record

> Every edit, by the agent or by the person, comes back as a structured record.

### Say

Models are good, but not perfect, so a person still checks and fixes the result. At that point
the pipeline stops: someone opens the image, fixes it, and passes the file back by hand. When
they save, the fix becomes a new mask, and the change history is lost.

So we let an AI agent drive ITK-SNAP, through the Model Context Protocol, a standard way for an
assistant to use tools. The agent requests an automatic segmentation, routes it to a person for
correction, and gets every edit back as a record. Let me show you.

## Video: Demo

- time: 3:50
- file: build/CAIMI26_ITK-SNAP_Hao_demo.mp4
- attribution: CT scan: TotalSegmentator dataset (Wasserthal et al., Radiology: AI, 2023), CC BY 4.0

<!-- Played on its own, not from a slide: the organisers load the MP4 on the podium PC.
     build_video.py renders it from video.md and burns the attribution into the frame.
     The beats below must add up to the video time, and match the beat table in video.md. -->

### Beat 1: List models (0:20)

On the left is the agent, in a terminal. Here it is Claude Code, but any client that speaks
the protocol would work. I type plain English. I ask which models the server has. We will use
TotalSegmentator, which is fully automatic.

### Beat 2: Workspace, and ITK-SNAP opens (0:30)

Next I ask it to create a workspace from a CT scan and open it. ITK-SNAP starts on the right.
This is the normal application. The only difference is that the agent can talk to it.

### Beat 3: The proposal (0:35)

Now I ask for an automatic segmentation. The scan goes to our model server. The real call
takes about a minute; I cut the waiting from this video. The model found more than sixty
structures. So far this is only a proposal. Nothing has been written into the image.

### Beat 4: Apply into the open window (1:00)

I ask the agent to apply the heart and the vessels. Watch the right side. Eleven structures
appear in the open window, one by one. Each gets its own label and its real name, so the
person sees "heart" and "aorta", not "Label 1". The table shows what the agent wrote. The
heart alone is about two hundred and forty thousand voxels.

### Beat 5: The correction (0:40)

Now it is my turn. I zoom in, pick the paintbrush, and touch up the edge of the heart. Then I
add a little to the aorta, and erase a few voxels. I should be clear: I am a developer, not a
clinician. This shows the mechanism, not clinical judgment. And I did nothing special. There
is no "record" button. I just used ITK-SNAP as usual.

### Beat 6: The audit (0:45)

Last, I ask the agent what happened. It reads the log from ITK-SNAP. Fifteen records. Eleven
are its own. Four are mine. For each of mine it knows the tool, the label, the number of
voxels, and the time. Forty voxels on the heart. Sixty-four on the aorta. Twenty-three
erased. The agent can tell its own work from my corrections. That is the part that is usually
lost.

## Slide 4: Every edit comes back as a record

- layout: record
- time: 0:40

### From the demo log

| Actor | Operation | Label | Voxels |
|---|---|---|---|
| agent | apply | heart | +242,476 |
| human | paintbrush | heart | +40 |
| human | paintbrush | heart | +41 |
| human | paintbrush | aorta | +64 |
| human | paintbrush (erase) | aorta | -23 |

The demo log has 15 records: 11 agent (one shown), 4 human.

### In every record

- **Shown in the table:** actor, operation, label, voxels changed.
- **Also recorded:** time, bounding box, label counts before and after.

> The agent saves the records as a JSON file next to the workspace, so the change history stays with the case.

### Say

This is what the agent got back. The table shows four fields of each record: who made the
edit, the tool, the label, and how many voxels changed. Each record also keeps the time, where
the edit was, and the label counts before and after. The agent saves these records as JSON next
to the workspace, so the change history stays with the case, and any script can read it.

## Slide 5: Future directions

- layout: closing
- time: 0:40

<!-- This slide stays on screen during the Q&A. One numbered list is drawn as cards across
     the slide; two lists would be drawn as two columns. The last block is optional: a URL
     there adds a QR code. -->

### Future directions

1. **Route cases by confidence.** Let agreement between model runs decide which cases a person sees.
2. **Train models with the audit records.** Each correction is a labeled example of where the model fails.
3. **Automate the improvement loop.** Retrain, test, and update the server without manual steps. The records then show whether corrections drop.

### Code and demo

https://github.com/jilei-hao/itksnap-mcp

### Say

Where do we go from here? First, routing: we want agreement between model runs to decide which
cases a person sees. Second, we want to train models with these audit records: every expert
correction is a labeled example of where the model fails. Third, we want to automate that loop:
retrain and test on new corrections, update the model on the server, and use the same records
to see whether corrections go down. The code is open; the QR code goes to the repository. Thank
you.
