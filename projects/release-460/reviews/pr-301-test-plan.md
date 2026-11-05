# PR #301 — manual test on real 4D CTA data

[#301](https://github.com/pyushkevich/itksnap/pull/301) "Choose 4D CTA per DICOM series, not per
directory (#218)", by Paul, assigned to Jilei on 2026-10-27, with the request: "could you please try
this out on real 4D CTA Dicom datasets to confirm the fix is working well?" The PR itself says no real
4D CTA data was tested.

## What changed, in one paragraph

Before, any CT file from GE or Siemens made ITK-SNAP read the **whole folder** as one 4D CTA series,
and it skipped the page where you choose a series. Now every DICOM file opens as "DICOM Image
Series", the series page always shows, and a series is read as 4D CTA only if it is a CT series from
GE or Siemens with **more images than distinct slice positions** (several frames per position).
Positions are compared after rounding to 0.001 mm.

## The build

| | |
|---|---|
| Tree | local branch `pr-test/301` = `upstream/master` `d7581658` (4.6.0-beta.1) + #301 head `b5426004`, merged (`b2b32489`) |
| Worktree | `worktrees/pr-review` |
| Build | `build-pr-review/` (Release, VTK 9.5.2, Homebrew Qt) |
| Run | `build-pr-review/ITK-SNAP` (a plain executable, not an `.app`) |
| Compare with | `build-release/ITK-SNAP`: staging `b842801f` on `8868dc2e`, i.e. the old behaviour |
| Built | 2026-10-28: 581/581, 0 errors. Its own tests pass: `TestDicomSeriesDetection` 3.3 s, `DicomSeriesSelection` 32 s, and `EchoCartesianDicomLoading` 23 s (still passes). The full suite was not run |

## The data

All four exams are Siemens, one series per exam, under `/Users/jileihao/data/avrp/4DCTA_anon/`.
Checked with `c3d -dicom-series-list` (2026-10-28): each parses as **one** series with the same ID scheme
ITK-SNAP uses, so #301 should mark each as 4D CTA.

| Exam | Folder | Files | Expected series-page dimensions | Expected image | Size |
|---|---|---:|---|---|---:|
| bavcta007 | `bavcta007_baseline/0000F377/` | 3570 | `512 x 512 x 357 x 10` | 10 time points | 1.8 GB |
| bavcta005 | `bavcta005_baseline/00006EE1/` | 3200 | `512 x 512 x 160 x 20` | 20 time points | 4.2 GB |
| bavcta008 | `bavcta008_baseline/0000CD5C/` | 5720 | `512 x 512 x 286 x 20` | 20 time points | 2.8 GB |
| bavcta006 | `bavcta006_baseline/00009748/` | 6954 | `512 x 512 x 366 x 19` | 19 time points | 3.4 GB |

Spacing from `projects/4dcta_improvement/metadata_reference.md` §5: in-plane 0.314 (005), 0.367
(006, 007), 0.377 (008) mm; slices 0.3 mm. **Start with bavcta007**: it is the smallest, and this Mac
is short on memory.

What this data **cannot** test: an exam folder with several series (the #218 case itself). The
PR's synthetic `dicom_ct_exam` covers that, in `TestDicomSeriesDetection` and `DicomSeriesSelection`.

## Checks

For each exam (at least 007 and one 20-phase one):

1. **File › Open Main Image**, pick any file in the exam folder.
   - The format should read **"DICOM Image Series"**. Before #301 it was "4D CTA DICOM Series".
   - Next: the **series page appears** with one row, and the dimensions in the table above.
2. **Load it.**
   - Time points as in the table; step through them. Each time point should be one coherent volume:
     no slices from other phases mixed in, and no every-other-slice striping.
   - Layer Inspector › Info: size `512 x 512 x <slices>`, spacing as above.
   - **Same geometry as the old build.** Open the same exam in `build-release/ITK-SNAP` and compare
     the size, spacing, origin, orientation code and the voxel coordinates of one landmark.
3. **Drag and drop** one file of the exam onto the main window. The drop dialog should go to the same
   series page.
4. **Command line:** `build-pr-review/ITK-SNAP -g <a file in the exam>`. It should load as 4D with no
   wizard, since the folder has only one series.
5. **Workspace round trip:** save a workspace with the 4D CTA loaded, close it, and reopen it. It
   should still have all time points. A workspace saved by 4.4 or the old build should also still
   open as 4D.
6. Note the **time to parse** the folder compared with the old build. #301 now also reads Modality,
   Manufacturer and ImagePositionPatient from every file while it parses.

Optional: [#302](https://github.com/pyushkevich/itksnap/pull/302), stacked on #301, merges series
that are split only by how SliceThickness is written (`0.625000` vs `0.625`). That came from GE 4D CTA
data in #128. Our exams are Siemens with one series each, so they would not show it.

## Results

_To fill in after the manual test._

| Exam | Series page | Time points | Geometry vs old | Drop | Command line | Workspace | Notes |
|---|---|---|---|---|---|---|---|
| bavcta007 | | | | | | | |
| bavcta005 | | | | | | | |
| bavcta008 | | | | | | | |
| bavcta006 | | | | | | | |
