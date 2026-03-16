#!/usr/bin/env bash
# run-greedy-python-tests.sh — Run greedy_python pytest suite.
# Uses the greedy test data from itksnap's greedy submodule.
#
# Run from itksnap-developer/ root.
set -euo pipefail

DEVDIR="${DEVDIR:-$(cd "$(dirname "$0")/.." && pwd)}"
GP_SRC="${GP_SRC:-$DEVDIR/greedy_python}"
GREEDY_TEST_DATA="${DEVDIR}/itksnap/Submodules/greedy/testing/data"

if [ ! -d "$GP_SRC" ]; then
  echo "ERROR: greedy_python source not found at $GP_SRC." >&2
  echo "       Set GP_SRC env var to the correct path." >&2
  exit 1
fi

if [ ! -d "$GREEDY_TEST_DATA" ]; then
  echo "ERROR: Greedy test data not found at $GREEDY_TEST_DATA." >&2
  exit 1
fi

echo "==> Running greedy_python tests..."
echo "    Source:          $GP_SRC"
echo "    Test data:       $GREEDY_TEST_DATA"

GREEDY_TEST_DATA_DIR="$GREEDY_TEST_DATA" PYTHONPATH="$GP_SRC/src:${PYTHONPATH:-}" python3 -m pytest "$GP_SRC/tests" -v "$@"
