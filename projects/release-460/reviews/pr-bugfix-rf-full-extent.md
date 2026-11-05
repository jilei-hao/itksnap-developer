# PR draft — `bug/rf-crashes-and-full-extent`

One PR for three topic branches, at Jilei's request (2026-10-28 and 2026-11-02): `bug/rf-layer-crashes`
(2 commits), `bug/full-extent-off-by-one` (1 commit) and `bug/free-rotation-3d-sync` (3 commits). They
share one file, `CMakeLists.txt`, with separate hunks. The combined branch is on `upstream/master`
`5ad5a025` (tag `v4.6.0-beta1`, with #302). The first three commits had their messages rewritten for
upstream, without our internal W8 numbers and rebase notes; their code is unchanged. The free-rotation
commits were cherry-picked on top on 2026-11-02; `git range-diff` shows them identical to `cd72d7fa`.
The branch keeps its old name, so the compare link below stays valid.

| Commit | From | Change |
|---|---|---|
| `dbe478d7` | `bug/rf-layer-crashes` | no crash on Train or on leaving random-forest mode without an engine |
| `62a1d591` | `bug/rf-layer-crashes` | Layer Inspector row model guarded against a deleted layer |
| `a5759611` | `bug/full-extent-off-by-one` | full-extent region no longer one voxel too large |
| `ad8d68f0` | `bug/free-rotation-3d-sync` | 3D mesh and 3D cursor follow the free rotation (Fixes #229) |
| `335c6737` | `bug/free-rotation-3d-sync` | loaded meshes are outlined in the slice views through the rotation |
| `a9b09a91` | `bug/free-rotation-3d-sync` | volume rendering turns the same way as the slice views |

**Base: `master`.** Open it against `pyushkevich/itksnap:master`, not against another PR's branch.

---

**Title:** Fix the 3D view under free rotation and the cursor limit, and add two safety checks

Fixes #229.

Six commits, four changes. The first two are bugs you can see. The other two are safety checks.

### 1. The 3D view now follows Image Free Rotation

**Tools › Image Free Rotation...** turned the image in the slice views, but the 3D view did not keep up, so the two stopped matching.

**Before:**
- The 3D mesh stayed where it was while the image turned.
- Clicking the mesh with the 3D crosshair put the cursor on the wrong spot in the slice views. This is what #229 reports.
- The outline of a mesh loaded from a file stayed where it was in the slice views.
- Volume rendering turned the opposite way from the slice views. The same happened to an overlay moved with **Tools › Registration**.

**After:** meshes, mesh outlines and volume rendering all turn with the image and match the slice views. A click on the mesh lands on the same spot in the slice views. 3D spray paint and the scalpel were updated to match, so they act on what you see.

Two things stay the same. If you don't rotate the image, nothing changes. And exported meshes stay in the image's own position, not the rotated view.

### 2. The cursor could go one slice past the images

When a segmentation has a different voxel size, position or orientation from the main image, you could scroll one slice past the end of the image. That slice is empty: the views go black and the intensity reads 0. The same limit also sets what "zoom to fit" shows.

**Before:** with `MRIcrop-orig.gipl.gz` and `MRIcrop-seg-hippoL-04mm.nii.gz` from the test data, the cursor could reach (-113, 210, 160), where there is no image.

[drag cursor-before-fix.png here]

**After:** the cursor stops at (-112, 209, 159), the last position that still shows the image.

[drag cursor-after-fix.png here]

The cursor numbers count voxels of the segmentation, which is finer than the image and covers only part of it. That is why they can be negative, or larger than the segmentation's own size ("159 of 92").

ITK-SNAP worked out the cursor's limits by rounding the edges of each image to the nearest slice, and that slice could lie just outside the image. It now counts only the slices whose centres are inside an image. #261 already fixed this for a single image and for a finer segmentation that lines up with the image. This covers the remaining cases. Segmentations on the same grid as the image behave as before.

### 3. Classification step

**Train Classifier**, and leaving the classification step, used the classifier without checking that it exists. An automated test once crashed here because of a problem in the test itself. We found no way to reach this with normal clicks, so nothing changes for users.

### 4. Closing a layer

While a layer is being closed, the Layer Inspector could still try to read it. It now checks that the layer is still there. We found this by reading crash reports and the code. We could not make the crash happen, so there is no test for it, and we can't say it solves a particular crash report.

### Testing

- The full test suite passes on macOS: 82 of 82.
- A new test, `FreeRotation3D`, turns an image by 30 degrees about a slanted axis. It checks clicks, meshes, outlines, volume rendering and the scalpel against where the slice views show the same structure. With the rotation left out on purpose, 9 of its 15 checks fail. It does not cover spray paint, the camera, or whether the 3D view refreshes while the rotation changes.
- A new test, `FullExtentRegion`, checks the cursor's limits against a voxel-by-voxel count for four layouts. Two of them, a shifted segmentation and one whose axes run in another direction, fail without this fix.
- Tested by hand on macOS: free rotation in the app, which looked right; the cursor before and after above; the classification step (train with no examples, train then cancel, go to the next step and back); and closing an overlay, a second segmentation and a mesh with the Layer Inspector open. Nothing crashed, and the layer list stayed correct.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---

## Checks done (2026-10-28, local, not part of the PR text)

Build: `pr-test/free-rotation` @ `9cdc7bc6` (master `a4f01e8d` + free rotation + this branch), in
`build-pr-review`, 0 errors. Pass: `FullExtentRegion` 1.4 s, `RandomForest` 38 s, `RandomForestBailOut`
20.6 s, `SnakeClassificationNavigation` 23.7 s, `ZoomToFitCycle` 24 s, `SegmentationSwitching` 82 s,
`MeshWorkspace` 47 s.

After the rebase onto `5ad5a025` (the pushed tip `a5759611`): `build-full-extent-off-by-one`, 446
steps, 0 errors; `FullExtentRegion` 1.2 s and `TestDicomSeriesDetection` 1.0 s pass.

Full suite on `a5759611`, run 2026-10-30 in `build-full-extent-off-by-one`: **81/81 pass**, none
skipped, 21 min, macOS. **Caveat:** that worktree's `c3d` and `greedy` were 22 and 57 commits behind
what master records, so this run was not on the branch's exact tree. Superseded by the run below.

`FullExtentRegion` without the fix, re-measured 2026-11-02 by relinking the test with master's
`GenericImageData.cxx`: layouts 1 and 2 pass, 3 and 4 fail, "2 layout(s) failed".

**Current, 2026-11-02, pushed tip `a9b09a91`:** submodules synced to the recorded commits, 0 errors, full
suite **82/82 pass**, none skipped, 21 min, macOS. This is the first full run with free rotation on
`5ad5a025`.

`FreeRotation3D` without the fix, measured 2026-11-02 by relinking the test with
`GetImageToReferenceNiftiTransform()` returning identity: 9 of 15 checks fail. The mesh and the loaded
mesh are 7.1 mm off, the outline 8.0 mm, the volume 7.1 mm, and 30 of 60 scalpel voxels are wrong.

## Manual checks (Jilei)

Run from `worktrees/full-extent-off-by-one/Testing/TestData`. The app to test is
`build-full-extent-off-by-one/ITK-SNAP`, the exact pushed tip. For the "before" in check 1, use
`build-full-extent-off-by-one/ITK-SNAP-before-fix`: the same build, relinked with master's
`GenericImageData.cxx`, so it differs only by fix 3. It is a local file that `ninja` does not rebuild.
Do not use `build-ui-language-setting/ITK-SNAP`: it was built on 2026-09-30 from upstream `52ee94fa`,
before #261, and has a different off-by-one (X -114 to 82, Y -66 to 209, Z -1 to 159).

**All three checks passed: Jilei, 2026-11-02**, on `a5759611`. Free rotation: Jilei, 2026-10-30, "looks
good", on `pr-test/free-rotation` @ `9cdc7bc6`, an older base with the same patches
([free-rotation-test-plan.md](free-rotation-test-plan.md)). That build merged these two sets of fixes
together, and the upstream commits since then touch none of the free-rotation files.

**Only check 1 shows a before and after.** The crash fixes were never reproduced by hand, so checks 2
and 3 can only show that normal use still works. A pass there does not prove the guards are needed.

1. **Cursor range.**
   `../../../../build-full-extent-off-by-one/ITK-SNAP -g MRIcrop-orig.gipl.gz -s MRIcrop-seg-hippoL-04mm.nii.gz`.
   In the Cursor Inspector, take X down as far as it goes, and Y and Z up as far as they go. Numbers
   are on the 0.4 mm segmentation grid. Repeat with the old build.

   | Limit | Old build | New build |
   |---|---:|---:|
   | X lowest | -113 | -112 |
   | Y highest | 210 | 209 |
   | Z highest | 160 | 159 |

   In the old build, those last slices should be empty; in the new one, they should show the image.
   With `-s MRIcrop-seg.gipl.gz` (same grid as the image), both builds should give 1 to 78, 1 to 110,
   1 to 64.

   Measured on 2026-11-02 in the real apps: a test script run with `--test <file>` read the minimum and
   maximum of `inCursorX/Y/Z` after loading with `-g -s`. They agree with a probe of the region code
   from 2026-10-30, where the new region matches a voxel-by-voxel count. The hippoR file gives the same
   kind of result in that probe.

   **Passed: Jilei, 2026-11-02**, comparing the pushed build with `ITK-SNAP-before-fix`.

2. **Classification step**, with **Tools › Layer Inspector...** left open throughout. Use
   `-g MRIcrop-orig.gipl.gz`, then **Active Contour Segmentation Mode**, **Segment 3D**, and
   Presegmentation mode **Classification**.
   - *Train with no examples:* **Train Classifier** should give a "Classification Failed" message
     about fewer than two classes. Then **Cancel Segmentation**. This is the path of
     `RandomForestBailOut`, and the one where the Layer Inspector guards were seen to fire.
   - *Train, then cancel:* paint Label 1 and Label 2 on different tissues (Paintbrush Mode), **Train
     Classifier**, **Cancel Segmentation**. No automated test covers this: `RandomForestBailOut` paints
     nothing.
   - *Next and Back:* train, **Next**, go back to the Classification page, train again, **Cancel
     Segmentation**. This leaves and re-enters the mode.

   After each one, the app should be back in the normal view, and the Layer Inspector rows should be
   right.

3. **Closing layers**, with the Layer Inspector open, outside Segment 3D (layers can't be closed
   there). Right-click a row and use its Close item, for:
   - an overlay (**File › Add Another Image ...**);
   - an extra segmentation (**Add Another Segmentation › Open...**);
   - the mesh in `MRIcrop-with-mesh.itksnap`.

   The row should go away, and the others should stay right.

## To open the PR (Jilei)

**Pushed** to `origin` on 2026-11-02 (`a9b09a91`, a fast-forward). GitHub compares it with
`pyushkevich/itksnap:master` as 6 commits ahead, 0 behind.

Open a PR from `jilei-hao:bug/rf-crashes-and-full-extent` to `pyushkevich/itksnap:master`, with
the title and text above. Drag the two PNGs from `reviews/pr-bugfix-images/` onto the `[drag ...]`
lines; GitHub only takes images by upload, and `gh` is still logged out here:
https://github.com/pyushkevich/itksnap/compare/master...jilei-hao:itksnap:bug/rf-crashes-and-full-extent?expand=1

