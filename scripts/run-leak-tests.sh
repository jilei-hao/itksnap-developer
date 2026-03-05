#!/usr/bin/env bash
# run-leak-tests.sh — Run the full GUI leak test suite and print a summary table.
# Usage: ./scripts/run-leak-tests.sh [TestName ...]
#   With no args, runs all known GUI tests.
set -euo pipefail

DEVDIR="${DEVDIR:-$(cd "$(dirname "$0")/.." && pwd)}"
BINARY="${BINARY:-$DEVDIR/build-leaks/ITK-SNAP}"
TESTDIR="${TESTDIR:-$DEVDIR/itksnap/Testing/TestData}"

ALL_TESTS=(
  PreferencesDialog
  RandomForestBailOut
  Workspace
  EchoCartesianDicomLoading
  MeshImport
  MeshWorkspace
  SegmentationMesh
  VolumeRendering
  LabelSmoothing
  NaNs
  DiffSpace
  Reloading
  RegionCompetition
  RandomForest
)

TESTS=("${@:-${ALL_TESTS[@]}}")

if [ ! -x "$BINARY" ]; then
  echo "ERROR: binary not found at $BINARY. Run scripts/build-leaks.sh first." >&2
  exit 1
fi

printf "%-30s %10s  %s\n" "Test" "Leaks" "Bytes"
printf "%-30s %10s  %s\n" "----" "-----" "-----"

for TEST in "${TESTS[@]}"; do
  OUTPUT=$(MallocStackLogging=1 leaks --atExit -- "$BINARY" \
              --test "$TEST" --testdir "$TESTDIR" 2>&1 || true)

  LEAKS=$(echo "$OUTPUT" | grep "leaks for" | grep -oE "^[0-9]+" || echo "ERR")
  BYTES=$(echo "$OUTPUT" | grep "leaks for" | grep -oE "[0-9]+ total leaked bytes" \
            | grep -oE "^[0-9]+" || echo "ERR")

  printf "%-30s %10s  %s\n" "$TEST" "$LEAKS" "$BYTES"
done
