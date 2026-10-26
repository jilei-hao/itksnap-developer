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
- time: 0:17

### Say

Good afternoon, everyone. I'm Jilei Hao, from the University of Pennsylvania. Today, I'm going to
talk about new features we added to ITK-SNAP, an open-source application for segmenting medical
images. These features make ITK-SNAP a tool that AI agents can call.

## Slide 2: ITK-SNAP and its deep-learning server

- layout: context
- time: 0:37
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

Here is an ITK-SNAP window. It shows each image in linked slice views and a 3D view. Users can
create or edit segmentations with manual or semi-automatic tools. ITK-SNAP can also connect to a
separate model server, usually on a GPU machine. Today, that server runs an interactive model.
This work adds two things. First, a fully automatic model on that server. Second, a way for an AI
agent to drive ITK-SNAP.

## Slide 3: Corrections are manual and unrecorded

- layout: problem-solution
- time: 1:01

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

Models are not perfect, so a person still needs to check the result. Today, that's manually done.
You run the model, find the image and its mask, and open both in ITK-SNAP. You check, fix, and
save. And repeat for all the cases you have. The saved fix is just a new mask. The history of the
change is lost.

So we let an AI agent do the manual part. It uses the Model Context Protocol, or MCP, a standard
way for AI to use tools. The agent runs the model and opens the result in ITK-SNAP. The person
only corrects it. The history of every edit is preserved and comes back to the agent.

The session only allows live demos from a web browser. But ITK-SNAP is a desktop application. So
the following demo is pre-recorded. Let me show you.

## Video: Demo

- time: 3:50
- file: build/CAIMI26_ITK-SNAP_Hao_demo.mp4
- attribution: CT scan: TotalSegmentator dataset (Wasserthal et al., Radiology: AI, 2023), CC BY 4.0

<!-- Since 2026-10-23 the organisers' final deck has the video on its own slide (slide 4), played
     on click; see README. Our own five-slide build still puts this narration in slide 3's notes.
     build_video.py renders it from video.md and burns the attribution into the frame.
     The beats below must add up to the video time, and match the beat table in video.md. -->

### Beat 1: List models (0:20)

This is the agent, in a terminal. Here I prompt it, asking for the available models on the server.
It lists three models. We'll use TotalSegmentator. It's fully automatic. The agent here is Claude
Code. But any client that supports MCP would work.

### Beat 2: Workspace, and ITK-SNAP opens (0:30)

Next, I ask it to make an ITK-SNAP workspace from a CT scan, and to open it. A workspace is
ITK-SNAP's project file. It lists the image, the segmentation and their settings. [0:18: ITK-SNAP
appears] There's ITK-SNAP, opened by the agent.

### Beat 3: The proposal (0:35)

Now I ask for an automatic segmentation. [0:12: the request is sent] The agent sends the image to
the model server. The segmentation process takes about a minute. I've cut the wait time from the
video. [0:17: the result] The model found sixty-eight structures. This is only a proposal. Nothing
is written into the image yet.

### Beat 4: Apply into the open window (1:00)

Here I ask the agent to apply the heart and the vessels. [0:10: structures start to appear] Watch the
right side. Eleven structures appear in the open window, one by one. Applied by the agent using the result sent back from the server. All automatic. The agent writes
straight into the window that's already open. And each structure it applies is recorded in the log. [0:53:
the table] Here the summary table shows the number of voxels for each applied structure.

### Beat 5: The correction (0:40)

Now it's my turn. I zoom in and pick the paintbrush to correct the result. This is only to show the mechanism, as I'm not a clinician. [about 0:14: heart] Here I touch up the
edge of the heart. [about 0:23: aorta] Now I add a little to the aorta. I'm just using ITK-SNAP as
usual. [about 0:34: erase] And here I erase a few voxels.

### Beat 6: The audit (0:45)

Last, I ask the agent what happened. It reads the log from ITK-SNAP. [0:12: the records] Fifteen
records. Eleven are from the agent. Four are from me. For each manual correction, it knows the
tool, the label, the number of voxels, and the time. Here, forty and forty-one voxels on the
heart. Sixty-four on the aorta. Twenty-three erased.

## Slide 4: Every edit comes back as a record

- layout: record
- time: 0:28

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

This is what the agent got back. Each row is one edit. It shows who made it, the tool, the label,
and how many voxels changed. The agent saves the records as a JSON file next to the workspace. So
the history stays with the case. And because the agent is general-purpose, the same steps can run
over many cases, or become part of other workflows.

## Slide 5: Future directions

- layout: closing
- time: 0:42

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

Three directions for future work. First, routing cases by confidence. Agreement between model runs
is one measure. We are still looking for the best one. Second, training models with these records.
Each correction is a labeled example of where the model fails. Third, automating the improvement
loop. The model is retrained, tested, and updated without manual steps. Then users don't have to
choose or tune models. They just keep correcting, and the records show whether the model improves.
Thank you.
