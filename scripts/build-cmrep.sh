#!/usr/bin/env bash
# build-cmrep.sh — Build cmrep with VCG support enabled, used to produce
# ground-truth outputs for ConvertMesh parity tests.
#
# What this builds:
#   - All standard cmrep utilities (vtklevelset, meshdiff, mesh_image_sample,
#     mesh_merge_arrays, mesh2img, warpmesh, ...)
#   - VCG-only utilities (mesh_smooth_curv, mesh_decimate_vcg,
#     mesh_poisson_sample) via -DCMREP_BUILD_VCG_UTILS=ON
#
# Dependencies fetched / required:
#   - vcglib (header-only) is cloned to lib/vcglib if absent
#   - Eigen3 must be available via find_package (Homebrew eigen@3 works)
#   - ITK_DIR / VTK_DIR taken from config.local.sh (same as the other scripts)
#
# Run from itksnap-developer/ root.
set -euo pipefail

DEVDIR="${DEVDIR:-$(cd "$(dirname "$0")/.." && pwd)}"
SRC_DIR="$DEVDIR/cmrep"
BUILD_DIR="${BUILD_DIR:-$DEVDIR/build-cmrep}"
VCGLIB_DIR_DEFAULT="$DEVDIR/lib/vcglib"
VCGLIB_DIR="${VCGLIB_DIR:-$VCGLIB_DIR_DEFAULT}"

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

# Eigen3: must use the same Eigen as ITK to avoid duplicate-Eigen header
# pollution when VCG headers and ITK headers end up in the same TU. ITK 5.4
# installs an Eigen3Config.cmake we can point cmrep at.
EIGEN3_HINT="$(dirname "$ITK_DIR")/ITK-${ITK_VERSION:-5.4}/Modules"

# Fetch vcglib if missing
if [ ! -f "$VCGLIB_DIR/vcg/simplex/vertex/base.h" ]; then
  echo "==> vcglib not found at $VCGLIB_DIR; cloning..."
  mkdir -p "$(dirname "$VCGLIB_DIR")"
  git clone --depth 1 https://github.com/cnr-isti-vclab/vcglib.git "$VCGLIB_DIR"
fi

echo "==> Configuring cmrep with VCG support..."
echo "    Source:     $SRC_DIR"
echo "    Build:      $BUILD_DIR"
echo "    ITK_DIR:    $ITK_DIR"
echo "    VTK_DIR:    $VTK_DIR"
echo "    VCGLIB_DIR: $VCGLIB_DIR"

CMAKE_ARGS=(
  -G Ninja
  -S "$SRC_DIR"
  -B "$BUILD_DIR"
  -DCMAKE_BUILD_TYPE="${CMAKE_BUILD_TYPE:-Release}"
  -DITK_DIR="$ITK_DIR"
  -DVTK_DIR="$VTK_DIR"
  -DCMREP_BUILD_VCG_UTILS=ON
  -DCMREP_BUILD_VSKEL=OFF
  -DCMREP_BUILD_PDE=ON
  -DCMREP_PDE_SPARSE_SOLVER=EIGEN
  -DVCGLIB_DIR="$VCGLIB_DIR"
)

if [ -n "$EIGEN3_HINT" ]; then
  CMAKE_ARGS+=( -DEigen3_DIR="$EIGEN3_HINT" )
fi

cmake "${CMAKE_ARGS[@]}"

echo "==> Building cmrep utilities..."
cmake --build "$BUILD_DIR" \
  --target vtklevelset meshdiff mesh_image_sample mesh_merge_arrays \
           mesh2img warpmesh mesh_smooth_curv mesh_decimate_vcg \
  -- -j"$(sysctl -n hw.logicalcpu 2>/dev/null || nproc || echo 4)"

echo "==> Done. Binaries in: $BUILD_DIR"
