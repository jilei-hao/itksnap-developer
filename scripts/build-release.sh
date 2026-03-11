#!/usr/bin/env bash
# build-release.sh — Configure and build ITK-SNAP in Release mode.
# Run from itksnap-developer/ root, or pass DEVDIR as env var.
#
# Usage:
#   scripts/build-release.sh [OPTIONS]
#
# Options:
#   -i, --itk  <path>   Path to ITK build dir (contains ITKConfig.cmake)
#   -v, --vtk  <path>   Path to VTK cmake dir (e.g. .../lib/cmake/vtk-9.3)
#   -q, --qt   <path>   Path to Qt6 install prefix (e.g. .../Qt/6.8.1/macos)
#   -b, --build <path>  Build directory (default: <devdir>/build-release)
#   -h, --help          Show this help message
#
# Environment variable fallbacks (used when flags are not provided):
#   ITK_DIR, VTK_DIR, QT_PREFIX
set -euo pipefail

DEVDIR="${DEVDIR:-$(cd "$(dirname "$0")/.." && pwd)}"
SNAP_DIR="$DEVDIR/itksnap"
BUILD_DIR=""

# Source local config for default paths (may define ITK_DIR, VTK_DIR, QT_PREFIX)
CONFIG="$DEVDIR/config.local.sh"
if [ -f "$CONFIG" ]; then
  # shellcheck source=../config.local.sh
  source "$CONFIG"
fi

ITK_DIR="${ITK_DIR:-}"
VTK_DIR="${VTK_DIR:-}"
QT_PREFIX="${QT_PREFIX:-}"
TARGET_OSX_VERSION="${TARGET_OSX_VERSION:-}"

usage() {
  sed -n '/^# Usage:/,/^set -/{ /^set -/d; s/^# \{0,1\}//; p }' "$0"
}

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    -i|--itk)   ITK_DIR="$2";   shift 2 ;;
    -v|--vtk)   VTK_DIR="$2";   shift 2 ;;
    -q|--qt)    QT_PREFIX="$2"; shift 2 ;;
    -b|--build) BUILD_DIR="$2"; shift 2 ;;
    -h|--help)  usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

BUILD_DIR="${BUILD_DIR:-$DEVDIR/build-release}"

# --- Validate required paths ---
errors=0
if [ -z "$ITK_DIR" ]; then
  echo "ERROR: ITK directory not specified. Use -i/--itk or set ITK_DIR." >&2
  errors=$((errors + 1))
fi
if [ -z "$VTK_DIR" ]; then
  echo "ERROR: VTK directory not specified. Use -v/--vtk or set VTK_DIR." >&2
  errors=$((errors + 1))
fi
if [ -z "$QT_PREFIX" ]; then
  echo "ERROR: Qt6 prefix not specified. Use -q/--qt or set QT_PREFIX." >&2
  errors=$((errors + 1))
fi
[ $errors -gt 0 ] && exit 1

if [ ! -d "$SNAP_DIR/.git" ]; then
  echo "ERROR: itksnap not found at $SNAP_DIR. Run scripts/setup.sh first." >&2
  exit 1
fi

echo "==> Configuration"
echo "    Source:    $SNAP_DIR"
echo "    Build:     $BUILD_DIR"
echo "    ITK_DIR:   $ITK_DIR"
echo "    VTK_DIR:   $VTK_DIR"
echo "    Qt prefix: $QT_PREFIX"
echo "    macOS target: ${TARGET_OSX_VERSION:-(not set)}"
echo ""

echo "==> Configuring ($BUILD_DIR)..."
OSX_TARGET_FLAG=""
[ -n "$TARGET_OSX_VERSION" ] && OSX_TARGET_FLAG="-DCMAKE_OSX_DEPLOYMENT_TARGET=$TARGET_OSX_VERSION"

cmake -G Ninja \
  -S "$SNAP_DIR" \
  -B "$BUILD_DIR" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH="$QT_PREFIX" \
  -DITK_DIR="$ITK_DIR" \
  -DVTK_DIR="$VTK_DIR" \
  ${OSX_TARGET_FLAG:+"$OSX_TARGET_FLAG"}

echo "==> Building ITK-SNAP..."
cmake --build "$BUILD_DIR" --target all

echo "==> Done. Binary: $BUILD_DIR/ITK-SNAP"
