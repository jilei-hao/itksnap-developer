#!/usr/bin/env bash
# sign-binary.sh — Re-sign ITK-SNAP after a ninja relink.
# Run this after every build that relinks the binary.
set -euo pipefail

DEVDIR="${DEVDIR:-$(cd "$(dirname "$0")/.." && pwd)}"
BINARY="${1:-$DEVDIR/build-leaks/ITK-SNAP}"

codesign --force -s - \
  --entitlements /dev/stdin \
  "$BINARY" <<'PLIST'
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

echo "Signed: $BINARY"
