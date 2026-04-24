#!/usr/bin/env bash
# build-convertmesh.sh — Build the standalone ConvertMesh library and cmesh CLI.
#
# Run from itksnap-developer/ root.
set -euo pipefail

DEVDIR="${DEVDIR:-$(cd "$(dirname "$0")/.." && pwd)}"
SRC_DIR="$DEVDIR/ConvertMesh"
BUILD_DIR="${BUILD_DIR:-$DEVDIR/build-convertmesh}"

# Source local config for ITK_DIR, VTK_DIR
CONFIG="$DEVDIR/config.local.sh"
if [ -f "$CONFIG" ]; then
  # shellcheck disable=SC1090
  source "$CONFIG"
fi

ITK_DIR="${ITK_DIR:-}"
VTK_DIR="${VTK_DIR:-}"

if [ -z "$ITK_DIR" ] || [ -z "$VTK_DIR" ]; then
  echo "ERROR: ITK_DIR and VTK_DIR must be set (via config.local.sh or env)." >&2
  exit 1
fi

echo "==> Configuring ConvertMesh..."
echo "    Source:  $SRC_DIR"
echo "    Build:   $BUILD_DIR"
echo "    ITK_DIR: $ITK_DIR"
echo "    VTK_DIR: $VTK_DIR"

cmake -G Ninja \
  -S "$SRC_DIR" \
  -B "$BUILD_DIR" \
  -DCMAKE_BUILD_TYPE="${CMAKE_BUILD_TYPE:-Release}" \
  -DITK_DIR="$ITK_DIR" \
  -DVTK_DIR="$VTK_DIR"

echo "==> Building ConvertMesh..."
cmake --build "$BUILD_DIR" -- -j"$(sysctl -n hw.logicalcpu 2>/dev/null || nproc || echo 4)"

echo "==> Running tests..."
( cd "$BUILD_DIR" && ctest --output-on-failure )

echo "==> Done. Binary at: $BUILD_DIR/cmesh"
