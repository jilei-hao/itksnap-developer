# W6 — Free-rotation 2D/3D sync

**Status:** investigated; design decided 2026-09-30; not implemented
**Branch:** none yet
**Depends on:** nothing
**Issue:** [pyushkevich/itksnap#229](https://github.com/pyushkevich/itksnap/issues/229) — open, filed 2026-04-24, no comments

## Goal

Under image free rotation, the 3D rendered mesh and the image share one coordinate space: clicking
the mesh with the 3D crosshair tool moves the 2D cursor to the anatomically corresponding voxel.

## Current state

**Investigated by reading, 2026-09-30.** The code is not written yet. Line numbers are for
`upstream/master` `52ee94fa`.

- **Free rotation transforms the main image and every segmentation.**
  `RegistrationModel::SetMovingTransform` (`RegistrationModel.cxx:599`) calls
  `layer->SetITKTransform(referenceSpace, affine)` on the main image, then the same on every
  `LABEL_ROLE` layer. The 2D views resample through that transform, so they show the segmentation
  rotated.
- **The 3D mesh ignores it.**
  - `VTKMeshPipeline::SetImage` (`VTKMeshPipeline.cxx:363`) places vertices with the segmentation's
    own VTK→NIfTI transform only.
  - `Generic3DRenderer::UpdateMeshAssembly` (`:285`) adds the actors with no user matrix.
  - The volume renderer does apply it: `GetRASMatrix(sw->GetITKTransform()) *
    ConstructVTKtoNiftiTransform(...)` (`Generic3DRenderer.cxx:853`). That is the pattern to copy.
- **The 3D pick ignores it too.** `Generic3DModel::IntersectSegmentation` (`:451`):
  - maps the click ray with the reference space's inverse sform;
  - ray-casts through the selected segmentation's raw voxels;
  - `PickSegmentationVoxelUnderMouse` passes the hit index straight to `SetCursorPosition`.
- **The result.** In 3D, the mesh, the pick and the 3D crosshair agree with each other: all
  un-rotated. But the 2D cursor lands on the un-rotated index, which the rotated 2D views show
  elsewhere. That is the bug in #229.
- **Answers to the open questions:**
  - Q1, "mesh or pick": both ignore the transform, so both need it.
  - Q2, mesh export: not yet checked. The exported mesh presumably comes from the same pipeline, so it
    is un-rotated. Whether that is wrong depends on whether an export should be in the image's
    physical space, which is arguably right, or in the rotated display.
- **Testing.** A GUI click test is not practical as the harness stands. `GenericView3D`
  (`view3d`) is a container. Its OpenGL child, which receives the mouse, has no object name, so
  events posted to `view3d` never reach VTK. Measured: 18 clicks, and the cursor never moved.
  - Better: a Logic/model-level test of the pick maths. Set a segmentation's ITK transform the way
    free rotation does, cast a world-space ray at a labelled structure, and require the resulting
    cursor to land on that label in the resampled (displayed) segmentation.
  - The mesh-transform part is a display change. It is checked by comparing the actor matrix with
    the volume renderer's.
 The issue reports:

> *"If I load an image with a segmentation file, then use free rotation to rotate the images, the
> rendered 3D mesh no longer corresponds when clicking the 3D mesh using the 3D crosshair tool"*

This is a **bug**, not a feature — worth noting, since it was listed alongside the feature items.
That makes it cut-resistant: it should survive any scope reduction that keeps W8.

Context: free rotation is an experimental 4.2.0 feature (`Tools → Image Free Rotation…`, per
`ReleaseNotes.md`) — *"Polygon and paintbrush tools can be applied from oblique rotation angles"*.
Mesh/3D was evidently not covered by that work. Upstream has a stale-looking `rot_via_main_tform`
branch that may hold prior thinking; check it before designing a fix.

Likely area: the transform applied to the mesh in `Logic/Mesh/` and `GUI/Renderer/` vs. the one
applied to slices — the mesh is probably built in raw image space while the slice pipeline carries
the rotation transform, so the two diverge exactly by that transform.

## Decisions (Jilei, 2026-09-30)

1. **Meshes loaded from files turn with the image too.** Under free rotation every mesh, generated
   or loaded, is shown through the main image's transform.
2. **Exported meshes stay in the image's own physical space**, as today. They do not follow the
   rotated view.
3. **Test the click-to-cursor maths at the model level**, not through a GUI click; the harness
   cannot reach the 3D view's OpenGL child. The mesh display is checked by comparing its actor matrix
   with the volume renderer's.

Implementation is for a fresh session, on a new topic branch (for example
`bug/free-rotation-3d-sync`) whose PR says "Fixes #229".

## Plan

1. Reproduce: load an image + segmentation, generate a 3D mesh, apply free rotation, click the mesh
   with the 3D crosshair. Record the coordinate delta — it should identify the missing transform.
2. Locate where the rotation transform is applied to the slice pipeline and where the mesh pipeline
   is built; find the point at which they diverge.
3. Confirm the direction of the bug: is the mesh un-rotated, or is the pick ray un-rotated? Fixing
   the wrong one will look right in some rotations and wrong in others.
4. Fix, and check the reverse direction too — 2D cursor → 3D mesh highlight.
5. Regression test with a non-trivial rotation (not axis-aligned, not 90°).

## Open questions

1. **Is the mesh wrong, or the pick?** Determines whether the fix is in mesh generation or in the 3D
   picker.
2. **Does this also affect mesh export?** If the mesh is built in the wrong space, a mesh saved under
   free rotation is wrong on disk too — a worse bug than the reported one, and worth checking early.
3. **What about externally-loaded meshes?** 4.4.0 added external mesh visualization in 2D slice views.
   They may be affected differently from generated meshes.
4. **`upstream/rot_via_main_tform`** — is it relevant prior art or abandoned?

## Done-criteria

- The reported scenario works: click the mesh under free rotation, the 2D cursor lands on the
  corresponding voxel.
- A test asserts round-trip correspondence under a **non-axis-aligned** rotation and fails if the
  transform is dropped again. An axis-aligned test would pass on the buggy code.
- Question 2 answered in writing; if mesh export is affected, either fixed here or filed separately.
- Issue #229 referenced in the commit and closed by the PR.
