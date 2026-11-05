# bug/4dcta-slice-order — reproduce the upside-down first frame, then check the fix

**PR:** [#307](https://github.com/pyushkevich/itksnap/pull/307) (opened 2026-11-04).

**Report:** a comment on [#128](https://github.com/pyushkevich/itksnap/pull/128) (2026-11-03), from the
author of #128, testing 4.6.0-beta1 with real GE 4D CTA data. The 4D image is detected, but the first
time point has its slices in reverse order. The report includes four lines that change
`make_dicom_ct_exam.py` to reproduce it.

**Cause, in short:** each time point is a stack of files. The reader asked GDCM's `IPPSorter` whether
the stack looked consistent, and reversed the stack only if it said yes. `IPPSorter` compares
`GantryDetectorTilt` as text, so `"0.000000"` in one file and `"0.0"` in the others counts as two
different tilts, and the stack is refused. The time point that holds that file keeps the opposite
order. The 4D geometry is copied from time point 1, so when that is the refused one, the whole image
is also placed 8 mm too low (one volume length). The fix sorts every stack by Z position directly.

## What you need

| | Path | What it is |
|---|---|---|
| **Before** | `build-full-extent-off-by-one/` | Built from a tree identical to `upstream/master` `a16d5c3e` (4.6.0-beta1 + #306): #301 and #302, old sorter. Up to date (2026-11-04). |
| **After** | `build-4dcta-slice-order/` | `bug/4dcta-slice-order` @ `b1da5935` = `upstream/master` + the fix (pushed to `origin` 2026-11-04) |
| Scripts | `reviews/4dcta-slice-order-scripts/` | `compare.sh`, `make_reporter_exam.py` |
| Python | `~/miniconda3/envs/instant3d` | has pydicom 3.0.1 and numpy. Set `PYTHON=` to use another |

`make_reporter_exam.py` is the upstream test-exam script with the reporter's four lines. Its output is
byte-identical to applying those lines to `upstream/master`'s script. `--same-tilt` writes a control in
which every file has `GantryDetectorTilt "0.0"`.

## Step 1 — command line (about 10 s)

```bash
projects/release-460/reviews/4dcta-slice-order-scripts/compare.sh
```

It runs the logic test `TestDicomSeriesDetection` from both builds on the fix branch's test exam, which
now contains the reporter's case. Expected:

```
-- BEFORE: .../build-full-extent-off-by-one
[Dynamic CTA] slice 1 frame 0: 1, expected -1
FAILED: [Dynamic CTA] 14 slices have the wrong intensity
-- AFTER: .../build-4dcta-slice-order
All checks passed
```

Then it writes four folders under `build-4dcta-slice-order/repro/`:

- `reporter_exam/`: the full exam, 3 series.
- `reporter_exam_4d_only/`: the 4D series only, so `-g` opens it with no series page.
- `control_same_tilt/` and `control_same_tilt_4d_only/`: the same, but without the tilt difference.

## Step 2 — the reporter's data in the GUI

Open the 4D series in both builds; two windows can be open at once:

```bash
build-full-extent-off-by-one/ITK-SNAP -g build-4dcta-slice-order/repro/reporter_exam_4d_only/s4_0001.dcm &
build-4dcta-slice-order/ITK-SNAP -g build-4dcta-slice-order/repro/reporter_exam_4d_only/s4_0001.dcm &
```

The image is 16 x 16 x 5 voxels x 3 time points. Every slice is one flat grey value, and the
differences are a few intensity units, so you can't see the bug by eye. Read the numbers:

1. In the main window's **Cursor Inspector** (left panel), set **Cursor position (x,y,z,t)** to
   z = 1 … 5 and t = 1, 2, 3, and read **Intensity under cursor**. x and y don't matter.
2. In **Tools › Layer Inspector › Info**, read **Origin** z, and **World units (NIfTI)** z at each
   cursor z.

Expected (z and t are counted from 1, as the Cursor Inspector shows them):

| Cursor z | Before: t = 1, 2, 3 | After: t = 1, 2, 3 | World Z before → after |
|---:|---|---|---|
| 1 | **4**, 100, 200 | 0, 100, 200 | 2 → 10 mm |
| 2 | **3**, 101, 201 | 1, 101, 201 | 0 → 8 mm |
| 3 | 2, 102, 202 | 2, 102, 202 | −2 → 6 mm |
| 4 | **1**, 103, 203 | 3, 103, 203 | −4 → 4 mm |
| 5 | **0**, 104, 204 | 4, 104, 204 | −6 → 2 mm |
| Origin z | 2 mm | 10 mm | |

**How to read it:** in a correct load, going from t = 1 to t = 2 adds exactly 100 at every slice. In
the before build, t = 1 runs the opposite way to t = 2 and t = 3. The files place the slices at
Z = 2 … 10 mm, so the before build also puts the whole image in the wrong place (2 to −6 mm).

The intensities and Z positions above are from the reader itself, loading the 4D-only folder with no
series hint (as `-g` does), run with both sorters on 2026-11-04. The Cursor Inspector readout (1-based z and t,
current time point) is from reading the code; I did not click through the GUI.

## Step 3 — control: the tilt text is the trigger

Open `control_same_tilt_4d_only/s4_0001.dcm` in the **before** build. It loads correctly, with the
**After** column above. The only difference from the reporter's data is that the first file writes
`GantryDetectorTilt` as `0.0` instead of `0.000000`. The reversed file order in the reporter's script
does not matter.

## Step 4 — optional

- **The real user flow.** File › Open Main Image, pick any file in `reporter_exam/`. The series page
  lists 3 series; choose "Dynamic CTA" (`16 x 16 x 5 x 3`), then do the checks from step 2.
- **No change on real data.** Open one AVRP exam (`bavcta007`, 1.8 GB; see
  [pr-301-test-plan.md](pr-301-test-plan.md)) in both builds, one at a time because of memory. Origin,
  orientation and the intensity at a landmark should match at two or three time points. Those Siemens
  files pass GDCM's check, so the fix should give the same order as before. This has not been tried.

## Results

_To fill in._

| Check | Before | After | Notes |
|---|---|---|---|
| Step 1, logic test | ❌ "14 slices have the wrong intensity" | ✅ all checks passed | 2026-11-04, by `compare.sh` |
| Step 2, Cursor Inspector values | | | |
| Step 2, origin / world Z | | | |
| Step 3, control | | — | |
| Step 4, wizard flow | | | |
| Step 4, AVRP exam | | | |
