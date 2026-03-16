#!/usr/bin/env bash
# build-greedy-python.sh — Configure and build the greedy_python Python extension.
# Requires the standalone Greedy build to exist at build-greedy/ (run
# scripts/build-greedy.sh first).
#
# Run from itksnap-developer/ root.
set -euo pipefail

DEVDIR="${DEVDIR:-$(cd "$(dirname "$0")/.." && pwd)}"
# Default: greedy_python/ alongside itksnap-developer (in-tree checkout).
# Override with GP_SRC env var if needed.
GP_SRC="${GP_SRC:-$DEVDIR/greedy_python}"
BUILD_DIR="$GP_SRC/build"
GREEDY_DIR="$DEVDIR/build-greedy/install/lib/cmake/Greedy"

# Source local config for ITK_DIR, VTK_DIR
CONFIG="$DEVDIR/config.local.sh"
if [ -f "$CONFIG" ]; then
  source "$CONFIG"
fi

ITK_DIR="${ITK_DIR:-}"
VTK_DIR="${VTK_DIR:-}"

if [ -z "$ITK_DIR" ] || [ -z "$VTK_DIR" ]; then
  echo "ERROR: ITK_DIR and VTK_DIR must be set (via config.local.sh or env)." >&2
  exit 1
fi

if [ ! -f "$GREEDY_DIR/GreedyConfig.cmake" ]; then
  echo "ERROR: GreedyConfig.cmake not found in $GREEDY_DIR." >&2
  echo "       Run scripts/build-greedy.sh first." >&2
  exit 1
fi

if [ ! -d "$GP_SRC" ]; then
  echo "ERROR: greedy_python source not found at $GP_SRC." >&2
  echo "       Set GP_SRC env var to the correct path." >&2
  exit 1
fi

echo "==> Configuring greedy_python..."
echo "    Source:     $GP_SRC"
echo "    Build:      $BUILD_DIR"
echo "    Greedy_DIR: $GREEDY_DIR"

cmake -G Ninja \
  -S "$GP_SRC" \
  -B "$BUILD_DIR" \
  -DCMAKE_BUILD_TYPE=Release \
  -DFETCH_DEPENDENCIES=OFF \
  -DITK_DIR="$ITK_DIR" \
  -DVTK_DIR="$VTK_DIR" \
  -DGreedy_DIR="$GREEDY_DIR" \
  -DPython3_EXECUTABLE="$(which python3)"

echo "==> Building greedy_python..."
cmake --build "$BUILD_DIR" -- -j$(sysctl -n hw.logicalcpu)

# Copy the extension module into the Python package for in-source use
if [ -d "$GP_SRC/src/picsl_greedy" ]; then
  cp "$BUILD_DIR"/picsl_greedy.cpython-*.so "$GP_SRC/src/picsl_greedy/" 2>/dev/null || true
  cp "$BUILD_DIR"/_picsl_greedy.cpython-*.so "$GP_SRC/src/picsl_greedy/" 2>/dev/null || true
fi

echo "==> Done. Extension module installed in $GP_SRC/src/picsl_greedy/"
