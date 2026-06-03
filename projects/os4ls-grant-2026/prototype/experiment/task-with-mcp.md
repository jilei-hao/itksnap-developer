# Task (with-mcp arm)

You have the **`itksnap-wt` MCP server** available (tools: `create_workspace`,
`add_segmentation`, `set_labels`, `list_layers`, `inspect_workspace`,
`itksnap_wt_info`) and the **`itksnap-workspace-builder`** skill.

I have a cohort of imaging studies under `data/` — one folder per subject:

- every subject has `T1.nii.gz` (the main anatomical image);
- some subjects also have additional anatomical images (`FLAIR`, `T2`, `PET`, `CT`)
  and/or a `seg.nii.gz` (a segmentation);
- there is a shared label-description file at `data/labels.label`.

**Goal:** produce one workspace per subject in `output/with-mcp/`, named
`<subject>.itksnap`, following the `itksnap-workspace-builder` skill's conventions
(T1 is always the main; other anatomical images become overlays nicknamed by
modality; seg if present; labels loaded; tags `cohort:demo` + `status:needs-review`).

Use the MCP tools (follow the `itksnap-workspace-builder` skill). When done, verify a
couple of outputs with `list_layers` and report what you built.
