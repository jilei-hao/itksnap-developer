#!/usr/bin/env bash
# setup.sh — Clone (or update) itksnap inside the developer environment.
# Run from itksnap-developer/ root.
set -euo pipefail

DEVDIR="$(cd "$(dirname "$0")/.." && pwd)"
SNAP_DIR="$DEVDIR/itksnap"
FORK_URL="https://github.com/jilei-hao/itksnap.git"
UPSTREAM_URL="https://github.com/pyushkevich/itksnap.git"

if [ ! -d "$SNAP_DIR/.git" ]; then
  echo "Cloning itksnap from fork..."
  git clone --recursive "$FORK_URL" "$SNAP_DIR"
  git -C "$SNAP_DIR" remote add upstream "$UPSTREAM_URL"
  echo "Remotes: origin=$FORK_URL  upstream=$UPSTREAM_URL"
else
  echo "itksnap already cloned at $SNAP_DIR — skipping clone."
  echo "To update: git -C itksnap pull origin bug/memory-leak"
fi
