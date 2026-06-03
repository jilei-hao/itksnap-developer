---
name: itksnap-workspace-builder
description: >
  Batch-create ITK-SNAP workspaces (.itksnap) from a folder or manifest of
  medical images using the itksnap-wt MCP server. Use when the user wants to
  prepare review-ready ITK-SNAP sessions for a cohort — e.g. "build a workspace
  for every subject in this directory", "set up review sessions with the T1 and
  a label table for each case", or "assemble workspaces for these scans".
---

# ITK-SNAP Workspace Builder

You assemble **ITK-SNAP workspaces** for a cohort by calling the `itksnap-wt`
MCP server. A workspace bundles a main image + optional overlays/segmentation +
a label table + display settings into one `.itksnap` file a human can open and
review immediately.

## Tools available (from the `itksnap-wt` MCP server)

- `create_workspace(output_path, main_image, main_nickname?, segmentation?, overlays?, labels?, tags?)`
  — create a new workspace from scratch. `overlays` is a list of
  `{"image", "nickname"?, "colormap"?}`. Returns the path, an `ok` flag, the
  itksnap-wt log, and the exact command run.
- `add_segmentation(workspace_path, segmentation, nickname?)` — add a seg layer in place.
- `set_labels(workspace_path, label_file)` — load a label-description file in place.
- `list_layers(workspace_path)` / `inspect_workspace(workspace_path)` — verify your work.
- `itksnap_wt_info()` — confirm which itksnap-wt binary is in use.

## Cohort conventions (apply these defaults unless the user overrides)

When building review-ready workspaces for a cohort organized as one folder per
subject, follow these conventions so every workspace is consistent:

- **Main image** = `T1.nii.gz` (always the main, even if other anatomical images
  sort earlier alphabetically). Nickname **`T1`**.
- **Overlays** = every *other* anatomical image (`FLAIR`, `T2`, `PET`, `CT`, …).
  Add each as an overlay with **nickname = its modality** (the filename stem).
- **Segmentation** = `seg.nii.gz`, if present.
- **Labels** = the cohort's label-description file (e.g. `labels.label`).
- **Tags** on the main image: `cohort:demo` and `status:needs-review`.

Build each subject with **one `create_workspace` call**, passing `main_image` =
the T1 explicitly and `overlays` = the list of the others — this keeps the
"first layer added becomes the main" and per-layer nickname/colormap (picked-layer)
ordering correct automatically. Do not let an alphabetically-earlier image (e.g.
`T2.nii.gz`) become the main by accident.

## Workflow

1. **Discover the inputs.** Scan the user's directory (or read their manifest).
   Group files into cases by subject id. Identify, per case: the main image,
   any overlays, any segmentation, and a shared label-description file if one
   exists. Ask the user only if the grouping is genuinely ambiguous.
2. **Confirm the plan briefly.** Show the user the cases you found and what each
   workspace will contain before creating dozens of files.
3. **Create one workspace per case.** Call `create_workspace` for each, writing
   to an output directory. Use a clear `output_path` like `<out>/<subject_id>.itksnap`.
   Attach useful `tags` (e.g. `"cohort:<name>"`, `"status:needs-review"`) so the
   workspaces are filterable later.
4. **Verify a sample.** After creating, call `list_layers` (or `inspect_workspace`)
   on one or two outputs and confirm the layers/nicknames/labels are as intended.
   Report the exact command from one `create_workspace` call so the user can see
   how it maps to `itksnap-wt`.
5. **Summarize.** Report how many workspaces were created, where, and any failures
   (with the itksnap-wt error message).

## Conventions & tips

- Prefer **one `create_workspace` call per case** (atomic) over many incremental edits.
- Always set a `main_nickname` (e.g. the modality: "T1", "FLAIR") so the human sees
  meaningful layer names.
- Keep `output_path` paths absolute or clearly relative to a stated output dir.
- If `create_workspace` fails, the returned message contains the raw itksnap-wt
  error — surface it; common causes are a missing input file or an unreadable image.
- Do **not** invent label-description files; only pass `labels` if the user has one.

## Example

User: *"Make a review-ready workspace for every T1 in /data/study, each with our
standard label set at /data/labels.txt, tagged for review."*

You:
1. List `/data/study`, find `subjXXX_T1.nii.gz` per subject.
2. For each, call
   `create_workspace(output_path="/data/study/ws/subjXXX.itksnap",
   main_image=".../subjXXX_T1.nii.gz", main_nickname="T1",
   labels="/data/labels.txt", tags=["cohort:study","status:needs-review"])`.
3. `list_layers` on the first result to confirm; report the command and a summary.
