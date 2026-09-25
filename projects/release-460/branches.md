# Topic branches — the upstream review queue

**Snapshot:** 2026-09-24 · **Base for every branch:** `upstream/master` @ `52ee94fa` · **Pushed:** all eight
branches, plus `staging/v460` @ `d02236c3` (2026-09-25), to `jilei-hao/itksnap`. **Merge order and live branch
state:** [MERGE_ORDER.md](MERGE_ORDER.md). · **Meeting page (private):**
https://claude.ai/artifact/QyivAN8NiDzadZ7hPKn6ut — a rendered copy of this file as of 2026-09-24; this file stays the
source of truth.

This is the planning-meeting handout: one row per branch that could become a PR to
`pyushkevich/itksnap`. The branch model itself (why `staging/v460` is test-only) is in
[SPRINT_PLAN.md](SPRINT_PLAN.md) §2. Per-item evidence stays in the workstream files; this file only
maps it onto branches.

Each branch section has two parts:
- **PR description** — written for the wider ITK-SNAP developer and user community, in plain
  language, ready to paste into the pull request.
- **Review notes** — the internal evidence and discussion points for the planning meeting.

---

## Summary

| # | Branch | Tip | Commits | From | Standalone on macOS, 2026-09-24 |
|---|---|---|---:|---|---|
| 1 | `feature/cardiac-io` | `2fc0d9b8` | 12 | W1 · D1 | ✅ builds, **34/34** |
| 2 | `bug/linux-gcc-build` | `fb65f2b9` | 2 | W1 · D2, Q2 | ✅ builds, **34/34** |
| 3 | `bug/rf-layer-crashes` | `9e80001f` | 4 | W8 · 14, 15, 15d, 24 | ✅ builds, 33/34: only the remote flake. `RandomForestBailOut` **really runs** (20.0 s) and passes |
| 4 | `test/harness-false-green` | `83c44f62` | 1 | W8 · 1, 13 | ⚠️ builds, 32/34: a remote flake, plus `RandomForestBailOut` **"no such test"** — **needs #3 merged first** |
| 5 | `test/harness-gui-thread` | `8a28d50c` | 1 | W8 · 17, 25 | ✅ builds, 32/35: two remote flakes, plus `4DReplayWithMeshUpdate` — a known flake: it then passed **5/5** here vs **3/5** on `upstream/master` |
| 6 | `test/seg-anchor-4d` | `0b671e86` | 1 | seg_anchor 4D goal | ✅ builds, 37/38: only the remote flake. The four new tests pass (SegAnchor4DSwitching 72 s, Load3D 54 s, Mesh 44 s, Workspace 0.8 s) |
| 7 | `bug/full-extent-off-by-one` | `6a72f6a1` | 1 | W8 · 36 | ✅ builds, 34/35: only the remote flake. `FullExtentRegion` passes; `SegmentationSwitching` and `MeshWorkspace` unaffected |
| 8 | `bug/seg3d-into-4d-check` | `635bd1ac` | 1 | W8 · 37 | ✅ builds, 34/35: only the remote flake. `Seg3DInto4D` passes |

**All eight merged (`staging/v460` @ `d02236c3`): 40/41**, failing only
`RemoteImageLoadTest_WorkspaceWithMesh` (remote flake).
- The seven new tests pass with everything merged.
- The tests that other branches make real do run: `4DContinuousRendering` 37.7 s,
  `RandomForestBailOut` 20.3 s, `HarnessThreadSafety` 1.7 s.
- The previous five-branch staging (`62588ffc`, now tag `archive/staging-v460-0924`) ran 34/35.

**Baseline — `upstream/master` itself: 34/34, but two of those passes ran nothing.**
`4DContinuousRenderingD` (0.91 s) and `RandomForestBailOut` (0.89 s) pass without executing. #4
and #3 are what make them real. "Remote flake" means `RemoteImageLoadTest_{SingleImage,WorkspaceWithMesh}`:
the documented rotating failure when the three remote tests run back-to-back (W8 item 3/3b).
Compare failure *sets*, not totals.

**Merge order lives in [MERGE_ORDER.md](MERGE_ORDER.md)**, which keeps itself current whenever a
branch moves. As of this snapshot:
- all 28 pairs merge cleanly;
- #3 must come before #4, because #4 on its own fails upstream's never-registered
  `RandomForestBailOut`;
- #3 cannot be split: its test registration alone SEGFAULTs.

`staging/v460` = `upstream/master` + all eight. Its diff from the five-branch tip
`archive/staging-v460-0924` is exactly the three new branches (14 files, +1208/−11).

---

## 1 · `feature/cardiac-io` — 4D cardiac CTA / echo phase and metadata I/O

### PR description

**Title:** Keep the heartbeat phase and frame timing of 4D heart scans when loading and saving

A 4D cardiac CT is a series of 3D volumes taken at different moments of one heartbeat. Each volume
belongs to a point in the cycle, for example "35% of the way from one heartbeat to the next".
ITK-SNAP used to throw that away and number the volumes 0, 1, 2… with a made-up spacing, and 4D
echocardiography (ultrasound) lost its frame times the same way. This change keeps the information
from loading through to saving, shows it in the program, and stops patient-identifying details from
being copied into exported files.

**What changes**

- **Loading:** for 4D cardiac CT, the heartbeat phase of each volume is read from the DICOM series.
  For 4D echo (Philips Cartesian export), the time of each frame in milliseconds is read.
- **Saving:** `.seq.nrrd` files store the value and unit for every frame. NIfTI files cannot hold
  this in the image itself, so a small `.json` file is saved next to the image with the per-frame
  values and the slice thickness. ITK-SNAP reads it back when the NIfTI file is reopened.
- **In the program:** the Layer Inspector shows **Phase / time** for the current frame, for example
  "35% R-R" or "873 ms".
- **Privacy:** exported files keep only a fixed list of research-relevant DICOM fields (scanner,
  protocol, timing, geometry and similar) and drop names, IDs, dates and other identifying details.
  Ages of 90 and over are recorded as 90. Inside ITK-SNAP, the full information is still shown.
- **Safety:** a cardiac series with missing or extra files is refused with a clear message.
  Previously it loaded with frames silently mixed up.
- **Documentation:** `Documentation/Developer/Cardiac4DCTA_IO.md` explains the design.

**Compatibility**

- Workspaces now store the per-frame phase or time. Older ITK-SNAP versions still open them, but
  drop these values if they save the workspace again.
- Exported files carry less DICOM information than before. This is intended, and worth a line in
  the release notes.

**Testing:** checked end to end on a set of cardiac CT and echo studies, including the new Layer
Inspector field. An automated save-and-reload test is still to be added before merging.

### Review notes (planning meeting)

The existing branch, rebased from `679ba76a` onto `52ee94fa` with no conflicts. Old tip kept as
`archive/feature-cardiac-io-pre-rebase` (`9b5d9eb4`).

- **What it does:** reads the cardiac phase (`%R-R`, CT) or frame time (`ms`, echo) off 4D DICOM
  series instead of the hardcoded `0.05` temporal spacing; writes and reads it back through
  `.seq.nrrd` and NIfTI `pixdim[4]` plus a `<name>.json` sidecar; curates exported metadata to a
  non-PHI allow-list (age top-coded at ≥ 90 per HIPAA Safe Harbor); shows the value per time point
  in a "Phase / time:" GUI field; rejects ragged grids with a clear `IRISException`; adds
  `Documentation/Developer/Cardiac4DCTA_IO.md`.
- **Evidence:** end-to-end headless against the AVRP cohort, and GUI field checked by hand
  (`projects/4dcta_improvement/`). Built clean with no warnings on macOS and Linux when merged into
  staging.
- **Gap before a PR:** **no test in `Testing/` covers it.** The work was verified with a one-off
  driver script, and a one-off script catches no regressions. W1's done-criteria asked for a
  `.seq.nrrd` + `.nii.gz`/sidecar round-trip test that fails if the `%R-R` axis is dropped.
- **For Paul:**
  - The export curation changes what metadata users get out; it belongs in the release notes.
  - `TimePointProperties` `FormatVersion` goes 1 → 3. That is **not** a compatibility break: no
    reader validates it (W1 Q1). But a 4.4 build that re-saves the workspace silently drops the
    cardiac keys (W8 items 10, 11).

## 2 · `bug/linux-gcc-build` — build portability, VTK floor

### PR description

**Title:** Build fixes for Linux (GCC), and require VTK 9.5.2

ITK-SNAP did not compile on Linux with the GCC compiler, which is stricter than the macOS compiler
about a few things. This change makes it build there without changing how the program behaves. In a
separate commit, it also raises the minimum VTK version to the one the project's automated builds
already use.

**What changes**

- A few places that write text to the debug log now convert it explicitly. GCC rejected the
  ambiguous form.
- Two Qt header files are included directly, instead of relying on other headers to bring them in.
- The build works with older Qt 6 releases, such as Qt 6.4 on Ubuntu 24.04. Two optional steps that
  need newer Qt are skipped when Qt is too old: bundling translations (Qt 6.7) and preparing the
  Linux install package (Qt 6.5).
- Separate commit: the minimum VTK version goes from 9.3.1 to 9.5.2.

**Compatibility:** anyone building against a VTK between 9.3.1 and 9.5.2 will need to upgrade. The
VTK change is its own commit, so it can be left out if the project would rather not raise the
minimum now.

**Testing:** built on Ubuntu 24.04 with GCC 13 (all targets, no errors) and on macOS. The full test
suite passes on macOS.

### Review notes (planning meeting)

| Commit | Change |
|---|---|
| `9ca38fcb` | GCC/libstdc++ portability: `QString::fromStdString` around `std::string` in `qDebug` streams, explicit `<QTimeZone>` / `<QDialogButtonBox>` includes, and Qt version guards on `qt_add_translations` (≥ 6.7) and `qt_generate_deploy_script` (≥ 6.5). No behavior change. |
| `fb65f2b9` | `CMake/standalone.cmake` VTK floor `9.3.1` → `9.5.2`, the version CI already builds. |

- **Evidence:** Ubuntu 24.04 / GCC 13, 766/766 targets, 0 errors, with no local patches (2026-07-31,
  on staging).
- **For Paul:** the VTK floor is a policy call, not a fix. Raising it affects anyone packaging against
  an older distro VTK. It is a separate commit, so it can be dropped without touching the portability
  fixes.
- **The Qt guards are now dead code (found 2026-09-25, W8 42).** Upstream `34f091c8` requires Qt
  ≥ 6.9.3, so the `≥ 6.7` / `≥ 6.5` guards in `9ca38fcb` can never be false, and the Ubuntu apt Qt
  6.4.2 they were written for can no longer configure `upstream/master` at all. Either drop the
  guards from this branch, or keep them only if Paul lowers the Qt floor.

## 3 · `bug/rf-layer-crashes` — crashes after random-forest cancel and layer teardown

### PR description

**Title:** Fix crashes when cancelling the classification step and when layers are closed

ITK-SNAP could crash when a user cancelled semi-automatic segmentation during the classification
step, the one where you train a classifier by painting examples. It could also crash when layers
were removed while the Layer Inspector was showing them. A test was written in 2018 for exactly this
crash, but it never ran, because it was never added to the list of test scripts built into the
program. This change turns that test on and fixes the crashes it finds.

**What changes**

- The existing `RandomForestBailOut` test is now included in the build, so it actually runs.
- Pressing Classify/Train, or leaving the classification step, no longer crashes when the
  classifier was never set up.
- The Layer Inspector no longer uses a layer after it has been deleted: it lets go of the layer at
  the moment the layer is removed. This fixes the 2018 crash, which had come back.
- Several of the Layer Inspector's "what can this row do?" checks now handle a removed layer safely.
  These were found by reviewing crash reports.

**Testing:** `RandomForestBailOut` now runs (about 20 seconds) and passes. `MeshWorkspace`, which
caught an earlier, incomplete version of the fix, passes. The full test suite passes on macOS, apart
from the online download tests, which fail intermittently on any branch.

**Note:** the test registration and the fixes belong together. Turning the test on without the fixes
makes it crash, which would turn the automated builds red.

### Review notes (planning meeting)

| Commit | Item | Change |
|---|---|---|
| `6afd0d10` | 14 | Register `test_RandomForestBailOut.js` in `TestingScripts.qrc`. It was added in 2018 (`062ba382`) and **has never run**. |
| `0f4cabc5` | 15 | Guard the null `m_ClassificationEngine` on Classify/Train and when leaving a mode that was never fully entered. |
| `76c857f7` | 15d | Use-after-free of `AbstractLayerTableRowModel::m_Layer`: invalidate it on the layer's `DeleteEvent`, synchronously. The regression came from our own leak fix `1712c6e7`, which turned it into a raw pointer. It is the 2018 crash coming back. Upstream had added the same `ApplyColorMap` guard, so that hunk was dropped. |
| `9e80001f` | 24 | Null-layer guards in `CheckState()`: `NO_ROLE` passes the `!= SOME_ROLE` guards. Split out of staging `038fa32b`. |

- **Tests that fail if this regresses:**
  - `RandomForestBailOut` (≈ 20 s). A sub-second pass means it did not run.
  - `MeshWorkspace` (≈ 47 s today, 54 s in August). It segfaulted on the first, incomplete version of
    the 15d fix.
- **Keep the test registration and the fixes together.** Registering the test without the fixes
  turns CI red: `upstream/master` + `6afd0d10` alone → `RandomForestBailOut` **SEGFAULT at 19.8 s**
  (measured 2026-09-24). With the whole branch it passes in 20.0 s.
- **Caveat (W8 item 22):** `RandomForestBailOut` paints nothing, so training throws and the test
  goes through the error-dialog → cancel path. That path is what exposes 15d, so the coverage is
  real, but it is not what the script was written to test.

## 4 · `test/harness-false-green` — a GUI test with a missing script reported Passed

### PR description

**Title:** Report a GUI test as failed when its script can't be found

ITK-SNAP's GUI tests are scripts that drive the program. When the test runner couldn't find a
test's script, it quietly ran nothing and reported the test as **passed**. Because of that, the
`4DContinuousRendering` test had been "passing" for a long time without ever running: its name in
the test list had a typo.

**What changes**

- A missing script now makes the test fail, with the exit code for "no such test".
- The typo in the test list is fixed, so `4DContinuousRendering` really runs, in about 37 seconds.

**Testing:** asking for a test that doesn't exist now fails, where before it passed.
`4DContinuousRendering` runs its real script and passes.

**Merge order:** merge this after the classification-crash fix. That change adds the
`RandomForestBailOut` script to the build. Without it, this change correctly reports
`RandomForestBailOut` as missing, and the test fails.

### Review notes (planning meeting)

- **What it does:** fixes the `GUI_TESTS` typo `4DContinuousRenderingD`, which pointed at a script
  that doesn't exist. It also stops `TestWorker::readScript()` falling through after queuing
  `NO_SUCH_TEST`; the fall-through let any GUI test with a missing script exit 0.
- **Effect, measured 2026-09-24:**
  - `4DContinuousRendering` really runs now (37.3 s on macOS; 36.5 s on Linux in July).
  - `ITK-SNAP --test ThisTestDoesNotExist` exits **3** instead of 0.
- **Depends on #3.** On its own, `RandomForestBailOut` now fails as "no such test", because upstream
  never registered its script. That is exactly the kind of test this branch exists to expose, but
  merge #3 first.

## 5 · `test/harness-gui-thread` — scripts can no longer touch widgets off the GUI thread

### PR description

**Title:** Make GUI test scripts always act on the program's main thread

ITK-SNAP's GUI tests are JavaScript scripts that click buttons, fill in fields and check results.
The scripts run in the background, alongside the program, but Qt only allows windows and buttons to
be touched from the program's main thread. Touching them from elsewhere can crash on macOS or cause
failures that come and go. The recent update to the test helpers does this correctly for the
existing scripts, but nothing stops a script from reaching a window directly and bypassing the
helpers.

**What changes**

- Scripts now get a stand-in for each window or button, never the real object. Every action through
  the stand-in is carried out on the main thread, and waits until it has taken effect.
- If anything ever reaches a real window from the wrong thread, the test stops with a clear message
  instead of misbehaving silently.
- The existing test scripts and helper functions work unchanged.
- Also fixes one script-callable function that could crash the program, a memory error in a
  debugging helper, and problems when a test shuts down.
- A new test, `HarnessThreadSafety`, checks these protections.

**Testing:** `HarnessThreadSafety` fails if the main-thread safeguard is removed. The full test suite
passes on macOS apart from tests that already fail intermittently without this change: the online
download tests, and `4DReplayWithMeshUpdate`. That test passed 5 times out of 5 with this change,
against 3 out of 5 without it.

### Review notes (planning meeting)

Upstream `dbf8e79f` fixed the same problem differently, and this branch builds on top of it. It keeps
Paul's helper API and his rewritten scripts unchanged, and adds `TestObjectProxy` underneath: scripts
never hold a raw widget, and every access hops to the GUI thread. The GUI-thread assertion sits at
the one choke point (`TestObjectProxy::target()`). Also included:

- `postKeyEventInternal` is moved out of `protected slots:`; QJSEngine exposes protected slots, so
  one line of JS could abort the app.
- A dangling pointer in `printChildren`.
- The teardown races.

It adds the `HarnessThreadSafety` test. Ported from `b3cf79d3`, `5f2825e4` and half of `038fa32b`,
following the resolution in the Sep 4 merge `6f5ae27c`.

- **Measured on the port, 2026-09-24:**
  - I deleted the GUI-thread hop from `findChild()`. `HarnessThreadSafety` then aborted with
    "'TestObjectProxy::target' ran on a worker thread", so the guard still fires after the port.
  - Standalone 32/35. `4DReplayWithMeshUpdate` failed once, then passed 5 reruns out of 5.
    `upstream/master` passed it only 3 of 5, failing at about 25 s. It is the known W8 item 2 flake,
    not a regression from this branch.

- **Needs a conversation before a PR.** It is about 700 lines of harness change competing with a
  design Paul just landed. The argument for it: his helpers fix today's scripts; the proxy makes the
  next off-thread access fail loudly instead of silently. Paul may reasonably say his helpers are
  enough.

## 6 · `test/seg-anchor-4d` — seg_anchor tested with 4D data

### PR description

**Title:** Tests for segmentations with their own resolution, using 4D (time-series) images

ITK-SNAP 4.6 lets each segmentation have its own grid, with its own voxel size and extent, instead
of having to match the main image. The views and the cursor follow whichever segmentation is active.
The one existing test for this uses a single 3D image. This change adds tests with 4D images, which
are series of 3D volumes over time such as a beating heart. Here every segmentation also has a
separate label map for each time point.

**What the tests check**

- At every time point, the label under the cursor comes from the active segmentation at that time
  point. The image intensity shown is the one at the same physical location, whichever segmentation
  is active.
- Each of these keeps the time point, and keeps the cursor on the same spot in the body:
  - loading a second segmentation;
  - switching segmentations with `{` and `}`;
  - picking a segmentation in the Layer Inspector.

  This includes a spot that lies outside the smaller segmentation.
- Opening a single 3D segmentation in a 4D session fills in only the current time point, and is
  refused when it doesn't fit.
- A saved workspace with these segmentations reopens with the first segmentation active. 3D surface
  updates and 4D playback work with either segmentation active.
- Edit a time point, then save and reopen the workspace: each segmentation keeps its own grid, and
  the edit is still there.

**Test data:** three small label images (13 KB in total) made from existing test data by exact
resampling, and one workspace file.

**Testing:** no change to ITK-SNAP itself. The new tests pass on the current code, and each was
checked to fail when the behavior it covers is deliberately broken. The full test suite passes on
macOS, apart from the online download tests, which fail intermittently on any branch.

### Review notes (planning meeting)

Paul's seg_anchor work (PRs #247–#249) had one test, `SegmentationSwitching`, and it is 3D. This
branch adds four tests using a 4D main image (`img4d_11f`) and two 4D segmentations, each on its own
grid: a cropped 2× one (14×58×66×11) and a full-extent 1.5× one (57×53×57×11). Test code only; no
product change. The data is exact nearest-neighbour resamplings of `seg4d_11f_label{1,2}`, checked
voxel by voxel; the recipe is in the commit message.

| Test | What it checks | Time |
|---|---|---:|
| `SegAnchor4DSwitching` | At a probe point P and every time point, the label comes from the active seg's own time point, and the main image is sampled at the same physical point whichever seg is the reference. Loading a second seg, `{`, `}` and selecting a Layer Inspector row keep the time point and move the cursor to P in the new grid. A point Q outside the cropped seg's box (f9e25378) keeps working across switches. | ≈ 74 s |
| `SegAnchor4DLoad3D` | A 3D seg loaded into a 4D workspace replaces only the current time point of a same-grid seg, and is refused (seg untouched) when the grids differ. | ≈ 53 s |
| `SegAnchor4DMesh` | `img4d_11f_seganchor.itksnap` opens with the **first** seg active (cf65a583). The mesh goes stale and updates at several time points with either seg as reference. Replay with continuous update visits all 11 frames. | ≈ 44 s |
| `SegAnchor4DWorkspace` (C++) | Edit a time point of the active seg, save it and the workspace, reopen. Each seg keeps its 4D grid (the saved one on its own grid, with the edit); every layer's reference space is the active seg; switching keeps the cursor on the same physical point. | < 1 s |

- **Every test was shown to fail when broken.**
  - `SegAnchor4DSwitching` failed on a real mismatch while it was being written.
  - `Load3D` and `Mesh` each had one assertion mutated, and failed.
  - `SegAnchor4DMesh` fails on its first-seg-active check in a build with **cf65a583 reverted**.
  - In the C++ test, disabling `UpdateReferenceImageInAllLayers` and the cursor transfer in
    `UpdateActiveSegmentation` fails 11 checks.
- **Reviewed adversarially.** A reviewer's findings on the first version were fixed before the
  push: vacuous mesh checks, a tautological reference check, no data written in the round trip, and
  no GUI workspace load. Its "same size, other header" point is W8 38.
- **Probe points are tie-free.** P and Q map between the two grids with no 0.5 rounding ties, so the
  expected cursor positions are exact rather than floating-point luck.
- **For Paul:**
  - Selecting a segmentation row in the Layer Inspector activates it and moves the reference space
    (`ImageLayerTableRowModel::SetActivated`). Intended? It surprised the first version of these
    tests.
  - The time point stays anchored to the main image (the TODO in
    `GenericImageData::GetCursorTimePoint`). With 4D segs that have the main image's time-point
    count, everything checked here works.

## 7 · `bug/full-extent-off-by-one` — cursor range one voxel outside every image (W8 36)

### PR description

**Title:** Keep the cursor within the loaded images

ITK-SNAP works out the area the cursor may move in, and the area that "zoom to fit" shows, from all
the loaded images. That calculation was off by one voxel at the low end. With a single image 38
slices deep, the cursor boxes allowed 0 to 38 instead of 1 to 38, so the cursor could sit one voxel
outside every image. It went further wrong in two cases:

- When an image's axes point the opposite way from the active segmentation's, which is common
  between scanners and file formats, it was up to two voxels too large at one end and one voxel
  short at the other.
- When two grids line up exactly, the answer depended on rounding in the computer's arithmetic.

**What changes:** the area is now exactly the voxels whose centers lie inside at least one loaded
image.

**What users will notice**

| Where | Before | After |
|---|---|---|
| Cursor position boxes, for an image 38 slices deep | 0 to 38; position 0 is outside the image | 1 to 38 |
| Scrolling or arrow keys through slices | can go one slice past the first slice, onto a slice outside the image that shows nothing | stops at the first slice |
| Clicking outside the image at that edge | the crosshair can land one voxel outside the image | stops on the image's first voxel |
| A segmentation whose axes run the opposite way to the others | two empty slices reachable at one end; the image's last slice at the other end can't be reached | exactly the image's slices |
| Two images whose grids line up exactly | whether the last slice is reachable depends on rounding | always reachable |
| Zoom to fit | fits one extra empty voxel at one edge, half a voxel off-centre (too small to notice in practice) | centred on the images |

When the last slice couldn't be reached, two other things went wrong:
- a cursor position sent from another linked ITK-SNAP window onto that slice was ignored;
- switching segmentations with the cursor on that slice could make the cursor jump to the middle of
  the image.

**Testing:** a new test, `FullExtentRegion`, compares the result with a direct voxel-by-voxel count
for four layouts:
- a single image;
- a finer, cropped segmentation;
- a segmentation on a shifted grid;
- a segmentation with flipped axes.

All four were wrong before this change. The full test suite passes on macOS, apart from the online
download tests, which fail intermittently on any branch.

### Review notes (planning meeting)

- **Bug:** `GetFullExtentImageRegion()` rounded each mapped corner on its own with
  `floor(ci − 0.5)`. That is one voxel low for a low corner, and it swaps with the high corner when
  an axis is flipped.
  - With just a main image the cursor spin boxes run 0..N, and the cursor can sit at index −1.
  - With a flipped layer the region gains two voxels at the low end and loses one at the high end.
  - With aligned grid edges, rounding error decides.
- **Fix:** bound the mapped corners first, then take the reference voxels whose centres lie inside,
  with a 1e-6 tolerance for exact edges.
- **Test:** `FullExtentRegionTest` checks four layouts against a brute-force oracle: main only, a
  2× aligned crop, a 1.5× shifted grid, and another direction matrix. **All four fail** on
  `52ee94fa`; all pass with the fix. < 1 s.
- **For Paul:** this is his seg_anchor code, so it needs his OK. The semantics are "voxels whose
  centre is in some layer". If he meant "any overlap", the fix is the same shape with `±0.5`.

## 8 · `bug/seg3d-into-4d-check` — clear error for a 3D seg that doesn't fit (W8 37)

### PR description

**Title:** Clear error when a 3D segmentation doesn't fit the 4D segmentation it would fill in

When a 4D (time-series) image is open, opening a single 3D segmentation fills in the current time
point of the selected segmentation. Now that segmentations may have their own grid, the old check,
that the file matches the main image, was rightly removed. But nothing replaced it with a check that
the file matches the segmentation being filled in. A file of the wrong size stopped with a confusing
internal message ("Source/Destination region mismatch in ImageWrapper::UpdateTimePoint"). Nothing
was damaged, but the message didn't say what was wrong.

**What changes:** the size is checked before anything is loaded. A mismatch now reports "Mismatched
Dimensions", with both sizes.

**Testing:** a new test, `Seg3DInto4D`, covers both outcomes:
- A file of the wrong size is refused with the clear message, and no time point changes. This part
  failed before the change.
- A file of the right size fills in only the current time point.

The full test suite passes on macOS, apart from the online download tests, which fail
intermittently on any branch.

**Known limitation:** a file of the right size but with a different voxel size or position is still
copied in as it is. How that case should behave is an open question.

### Review notes (planning meeting)

- **Bug:** a 3D seg loaded into a 4D workspace replaces the current time point of the *selected*
  seg. seg_anchor dropped the main-image size check, and nothing checks the target instead. A size
  mismatch therefore reached an assert in `ImageWrapper::UpdateTimePoint`, and the user saw
  "exception occurred during image IO … Source/Destination region mismatch". It is not a crash, and
  nothing is modified.
- **Fix:** `ValidateHeader` compares the 3D size with the selected segmentation's (IRIS mode) and
  throws "Mismatched Dimensions" up front.
- **Test:** `Seg3DInto4DTest`. It checks that a wrong-size 3D seg is refused with `IRISException`
  and leaves every time point unchanged, and that a same-grid one changes only the current time
  point. Without the fix it fails with the low-level exception. < 1 s.
- **For Paul:** the same-size, different-header case is **not** handled; see W8 38 below.

---

## Not branched

| What | Why |
|---|---|
| `092022fb` — slider `NOTIFY` (W8 item 21) | Superseded: upstream `93aa9583` fixed it independently, and the Sep 4 merge took upstream's version. |
| `developer-doc` — W2 | **Already upstream**: PR #244 (`5e2984ff`, merged 2026-08-18). `itksnap-dls` has the same docs on `main`. |
| `cb6f692e`, `ea86df0d` on `test/dls_sam2` — async DLS | Not ready: two defects in `cb6f692e` (W1 Q4: undo gap, use-after-free). |
| 6 agentic commits on `sprint/caimi` | Out of scope for 4.6.0. |
| W8 38 — a same-size 3D seg with another header is pasted into a 4D seg silently | Design question for Paul: refuse, resample, or add it as a layer? |
| W8 39 — `GetReferenceSpaceOrigin()` returns the spacing | No callers; a one-line fix or a delete. Paul's call. |
| W8 40 — adding a 4D seg prompts about unsaved changes it can't overwrite | Pre-dates seg_anchor; minor. |
| W8 41 — "TEMP DIAGNOSTIC" `FileOpen` logging to `~/itksnap-url-debug.log` in `upstream/master` | Ask Paul whether it's still needed before 4.6. |

## Push record

**Pushed 2026-09-24 to `jilei-hao/itksnap`:**
- The four new branches, with `-u origin`. They now track `origin`, not Paul's `master`.
- `feature/cardiac-io` (`9b5d9eb4` → `2fc0d9b8`) and `staging/v460` (`038fa32b` → `62588ffc`),
  force-pushed with leases pinned to those old tips.

The old tips survive as the local tags `archive/feature-cardiac-io-pre-rebase` and
`archive/staging-v460-0904`. They are not pushed. `9b5d9eb4` is still reachable on `origin` through
`sprint/caimi`; `038fa32b` is not.

**Pushed 2026-09-25 to `jilei-hao/itksnap`:**
- `test/seg-anchor-4d`, `bug/full-extent-off-by-one` and `bug/seg3d-into-4d-check`, with
  `-u origin`.
- `staging/v460` (`62588ffc` → `d02236c3`), force-pushed by Jilei with a lease pinned to
  `62588ffc`.

The old staging tip is the local tag `archive/staging-v460-0924`, which is not pushed.
