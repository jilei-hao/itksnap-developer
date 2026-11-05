#!/usr/bin/env bash
# Before/after comparison for bug/4dcta-slice-order (first 4D CTA frame upside down).
# Steps and expected values: ../4dcta-slice-order-test-plan.md
#
# Override any of these from the environment:
#   BEFORE  build of upstream/master (old sorter)    default: build-full-extent-off-by-one
#   AFTER   build of bug/4dcta-slice-order (the fix)  default: build-4dcta-slice-order
#   PYTHON  a Python with pydicom and numpy           default: miniconda env instant3d
#   OUT     where the DICOM test exams are written    default: $AFTER/repro
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
BEFORE=${BEFORE:-$ROOT/build-full-extent-off-by-one}
AFTER=${AFTER:-$ROOT/build-4dcta-slice-order}
PYTHON=${PYTHON:-$HOME/miniconda3/envs/instant3d/bin/python}
OUT=${OUT:-$AFTER/repro}
TESTDATA=$ROOT/worktrees/4dcta-slice-order/Testing/TestData

echo "== 1. Logic test on the fix branch's test exam, which now holds the reporter's case"
for side in BEFORE AFTER; do
  dir=${!side}
  echo "-- $side: $dir"
  "$dir/TestDicomSeriesDetection" "$TESTDATA" 2>&1 | tail -3
done

echo
echo "== 2. Writing the reporter's exam to $OUT"
rm -rf "$OUT"
"$PYTHON" -I "$HERE/make_reporter_exam.py" "$OUT/reporter_exam" || exit 1
"$PYTHON" -I "$HERE/make_reporter_exam.py" "$OUT/control_same_tilt" --same-tilt || exit 1
# Folders holding only the 4D series, so that -g loads it without the series page
for d in reporter_exam control_same_tilt; do
  mkdir -p "$OUT/${d}_4d_only"
  cp "$OUT/$d"/s4_*.dcm "$OUT/${d}_4d_only/"
done
ls -d "$OUT"/*

echo
echo "== 3. Open the 4D series in both builds (two windows), then follow the test plan:"
echo "$BEFORE/ITK-SNAP -g $OUT/reporter_exam_4d_only/s4_0001.dcm &"
echo "$AFTER/ITK-SNAP -g $OUT/reporter_exam_4d_only/s4_0001.dcm &"
