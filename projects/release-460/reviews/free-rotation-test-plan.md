# `bug/free-rotation-3d-sync` (#229) — manual test

The branch makes the 3D view follow **Tools › Image Free Rotation...**. Its automated test,
`FreeRotation3D`, checks the maths at the model level. **Nothing has been checked by eye in the app
yet**, and the test can't see three things: whether the 3D view updates when the rotation changes,
where the spray glyphs land, and where the camera centres. Details: [branches.md](../branches.md) §12
and [workstreams/free-rotation-sync.md](../workstreams/free-rotation-sync.md).

## The build

| | |
|---|---|
| Tree | local `pr-test/free-rotation` @ `9cdc7bc6` = `upstream/master` `a4f01e8d` (4.6.0-beta.1 + #301) + `bug/free-rotation-3d-sync` `d09de39f` + `bug/rf-crashes-and-full-extent` `b8c3ba55`, each merged in |
| Automated, 2026-10-28 | 581 targets, 0 errors. Pass: `FreeRotation3D` 1.4 s, `VolumeRendering` 19.9 s, `SegmentationMesh` 73 s, `MeshImport` 28 s, `MeshWorkspace` 47 s. The full suite was not run, to keep the screen free for this test |
| Worktree | `worktrees/pr-review` |
| Run | `build-pr-review/ITK-SNAP` |

Data, from `worktrees/pr-review/Testing/TestData/`:
- `MRIcrop-orig.gipl.gz` + `MRIcrop-seg.gipl.gz`, for the segmentation mesh;
- `MRIcrop-with-mesh.itksnap`, the same image with a loaded mesh (`MRIcrop-ventricle-mesh.vtk`).

```bash
cd worktrees/pr-review/Testing/TestData
../../../../build-pr-review/ITK-SNAP -g MRIcrop-orig.gipl.gz -s MRIcrop-seg.gipl.gz
```

**Use a rotation that is not 90° and not about one axis only**, e.g. about 30° about a slanted axis. A
simple rotation can look right even when the direction is wrong.

## Checks

Before rotating, update the 3D mesh and note where one structure is in the slice views and in 3D.

1. **The mesh turns.** Rotate. The 3D mesh should turn with the image and match the slice views. Note
   whether it follows while you drag the rotation, or only after you press Update.
2. **3D crosshair click** (#229 itself). With the **3D Crosshair Tool**, click a structure on the
   mesh. The cursor in the slice views should land on that structure, and the label under the cursor
   should be the clicked label. Try three or four different view directions.
3. **The other way round.** Click a structure in a slice view. The 3D cursor should sit on the mesh at
   that structure.
4. **3D Scalpel Tool.** Draw a cut across a structure and apply it with a new label. In the slice
   views, the relabelled part should be on the side you chose, cut where the plane was drawn.
5. **3D Spray Paint Tool.** Spray on the mesh. The paint should appear at that spot in the slice
   views, and on the mesh after Update.
6. **Loaded mesh.** Open `MRIcrop-with-mesh.itksnap` and rotate. The ventricle mesh should turn in 3D,
   and its outline in the slice views should stay on the ventricles.
7. **Volume rendering.** Turn it on for the main image ("Enable volume rendering of this layer" in
   the Layer Inspector). After rotating, it should turn the same way as the slice views and line up
   with the mesh. Before the fix, it turned the opposite way.
8. **Export stays in the image's own space.** After rotating, use **Export as Surface Mesh...**. Load
   the file into a fresh session with no rotation: it should match the unrotated segmentation.
9. **Undo the rotation.** Reset the rotation. Everything should go back to the original view.
10. **No rotation, no change.** Without free rotation, the 3D view, click, scalpel and spray should
    behave as in 4.6.0-beta.1.

Optional: **Tools › Registration**. Move an overlay by hand, and its volume rendering should move the
same way as its slices.

## Results

**Jilei, 2026-10-30: looks good**, on the build above. That is the overall result; the checks were not
reported one by one, so the table below stays blank.

**2026-11-02:** these commits now live on `bug/rf-crashes-and-full-extent` (`a9b09a91`), with the same
patches. See [pr-bugfix-rf-full-extent.md](pr-bugfix-rf-full-extent.md).

| # | Check | Result | Notes |
|---:|---|---|---|
| 1 | mesh turns (live or after Update?) | | |
| 2 | 3D crosshair click | | |
| 3 | 2D click → 3D cursor | | |
| 4 | scalpel | | |
| 5 | spray paint | | |
| 6 | loaded mesh, 3D and outline | | |
| 7 | volume rendering | | |
| 8 | export in image space | | |
| 9 | reset rotation | | |
| 10 | no rotation, no change | | |
