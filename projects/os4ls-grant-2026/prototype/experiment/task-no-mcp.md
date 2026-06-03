# Task (no-mcp arm)

You have access to a command-line program (a compiled binary) that builds
**ITK-SNAP workspace files** (`.itksnap`). Its absolute path is:

    <PASTE ABSOLUTE PATH TO itksnap-wt HERE>

I have a cohort of imaging studies under `data/` — one folder per subject:

- every subject has `T1.nii.gz` (the main anatomical image);
- some subjects also have `FLAIR.nii.gz` (a second image) and/or `seg.nii.gz`
  (a segmentation);
- there is a shared label-description file at `data/labels.label`.

**Goal:** produce one workspace per subject in `output/no-mcp/`, named
`<subject>.itksnap`, where each workspace contains:

- the **T1** as the main image, with display name (nickname) **`T1`**;
- the **FLAIR** as an additional image with nickname **`FLAIR`** — *only if that
  subject has a FLAIR*;
- the **segmentation** — *only if that subject has a seg*;
- the labels from `data/labels.label` loaded;
- two tags on the main image: `cohort:demo` and `status:needs-review`.

When done, briefly report what you built and verify a couple of the outputs.

## Constraints (important)

- You have **no prior knowledge** of this tool. **Figure out how to use it yourself**
  — e.g., by running it to see its usage.
- **Do not read** any documentation, README, skill, or source in this repository that
  describes this tool (in particular, do not open anything under `prototype/skills/`,
  `prototype/README.md`, or `prototype/itksnap_wt_mcp/`). Use only the binary itself.
- Work only from this task and the `data/` folder.
