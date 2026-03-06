#!/usr/bin/env bash
# build-leaks.sh — Configure, build, and sign ITK-SNAP for memory leak testing.
# Run from itksnap-developer/ root, or pass DEVDIR as env var.
set -euo pipefail

DEVDIR="${DEVDIR:-$(cd "$(dirname "$0")/.." && pwd)}"
SNAP_DIR="$DEVDIR/itksnap"
BUILD_DIR="$DEVDIR/build-leaks"

# Source local config for default paths (may define ITK_DIR, VTK_DIR, QT_PREFIX)
CONFIG="$DEVDIR/config.local.sh"
if [ -f "$CONFIG" ]; then
  # shellcheck source=../config.local.sh
  source "$CONFIG"
fi

ITK_DIR="${ITK_DIR:-}"
VTK_DIR="${VTK_DIR:-}"

errors=0
if [ -z "$ITK_DIR" ]; then
  echo "ERROR: ITK_DIR not set. Define it in config.local.sh or set it in the environment." >&2
  errors=$((errors + 1))
fi
if [ -z "$VTK_DIR" ]; then
  echo "ERROR: VTK_DIR not set. Define it in config.local.sh or set it in the environment." >&2
  errors=$((errors + 1))
fi
[ $errors -gt 0 ] && exit 1

if [ ! -d "$SNAP_DIR/.git" ]; then
  echo "ERROR: itksnap not found at $SNAP_DIR. Run scripts/setup.sh first." >&2
  exit 1
fi

echo "==> Configuring ($BUILD_DIR)..."
cmake -G Ninja \
  -S "$SNAP_DIR" \
  -B "$BUILD_DIR" \
  -DCMAKE_BUILD_TYPE=Debug \
  -DITK_DIR="$ITK_DIR" \
  -DVTK_DIR="$VTK_DIR"

echo "==> Building ITK-SNAP..."
cmake --build "$BUILD_DIR" --target ITK-SNAP

echo "==> Signing binary for leaks --atExit..."
codesign --force -s - \
  --entitlements /dev/stdin \
  "$BUILD_DIR/ITK-SNAP" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>com.apple.security.get-task-allow</key>
  <true/>
</dict>
</plist>
PLIST

echo "==> Done. Binary: $BUILD_DIR/ITK-SNAP"
echo "    Remember to re-run this script (or just the sign step) after every ninja relink."
