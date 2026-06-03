#!/usr/bin/env python3
"""
itksnap-wt MCP server — OS4LS grant prototype.

Wraps the *existing* ITK-SNAP workspace CLI (`itksnap-wt`) as a composable MCP
endpoint, so an AI agent can build ITK-SNAP workspaces programmatically (e.g.
batch-create one ready-to-review workspace per subject in a cohort).

This is a deliberately tiny demonstration of two grant ideas:
  - the "constellation of MCP endpoints" (one shared wrapping pattern over a
    mature CLI), and
  - "ITK-SNAP as a tool an agent calls" (Aim 1.2), exercised on the lowest-risk
    surface that already ships.

Transport: local stdio (the client launches this process) — no hosting needed.

Configure the binary via the ITKSNAP_WT env var, or it auto-detects common
build locations / PATH.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# --------------------------------------------------------------------------- #
# Locate the itksnap-wt binary
# --------------------------------------------------------------------------- #
_DEFAULT_CANDIDATES = [
    os.environ.get("ITKSNAP_WT", ""),
    shutil.which("itksnap-wt") or "",
    str(Path.home() / "dev/itksnap-dev/itksnap-developer/build-release/Utilities/Workspace/itksnap-wt"),
    str(Path.home() / "dev/itksnap-dev/itksnap-developer/build-debug/Utilities/Workspace/itksnap-wt"),
    str(Path.home() / "dev/itksnap-dev/itksnap-developer/itksnap/build/Utilities/Workspace/itksnap-wt"),
]


def _find_wt() -> str:
    for c in _DEFAULT_CANDIDATES:
        if c and Path(c).exists():
            return c
    return "itksnap-wt"  # last resort: assume on PATH


WT = _find_wt()
mcp = FastMCP("itksnap-wt")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _run(args: list[str]) -> str:
    """Run itksnap-wt with args; raise on failure (it prints 'ITK-SNAP exception ...')."""
    proc = subprocess.run([WT, *args], capture_output=True, text=True)
    combined = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0 or "ITK-SNAP exception" in combined:
        raise RuntimeError(
            f"itksnap-wt failed (exit {proc.returncode}): "
            f"{(proc.stderr or proc.stdout).strip()}"
        )
    return (proc.stdout or "").strip()


def _require(path: str, what: str) -> str:
    p = str(Path(path).expanduser())
    if not Path(p).exists():
        raise FileNotFoundError(f"{what} not found: {p}")
    return p


def build_workspace(
    output_path: str,
    main_image: str,
    main_nickname: Optional[str] = None,
    segmentation: Optional[str] = None,
    overlays: Optional[list[dict]] = None,
    labels: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> dict:
    """Core logic (importable + unit-testable, independent of MCP).

    Composes a single itksnap-wt invocation that creates a workspace with a main
    anatomical image, optional overlays / segmentation / label table / tags, and
    writes it to output_path.
    """
    main_image = _require(main_image, "main_image")
    args: list[str] = ["-layers-add-anat", main_image]
    if main_nickname:
        args += ["-props-set-nickname", main_nickname]
    for tag in tags or []:
        args += ["-tags-add", tag]

    for ov in overlays or []:
        img = _require(ov["image"], "overlay image")
        args += ["-layers-add-anat", img]
        if ov.get("nickname"):
            args += ["-props-set-nickname", ov["nickname"]]
        if ov.get("colormap"):
            args += ["-props-set-colormap", ov["colormap"]]

    if segmentation:
        seg = _require(segmentation, "segmentation")
        args += ["-layers-add-seg", seg]

    if labels:
        lab = _require(labels, "label file")
        args += ["-labels-set", lab]

    out = Path(output_path).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    args += ["-o", str(out)]

    log = _run(args)
    return {"workspace": str(out), "ok": out.exists(), "log": log, "command": " ".join(args)}


# --------------------------------------------------------------------------- #
# MCP tools
# --------------------------------------------------------------------------- #
@mcp.tool()
def create_workspace(
    output_path: str,
    main_image: str,
    main_nickname: str | None = None,
    segmentation: str | None = None,
    overlays: list[dict] | None = None,
    labels: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    """Create a new ITK-SNAP workspace (.itksnap) from scratch.

    Args:
        output_path: where to write the .itksnap workspace file.
        main_image:  path to the main anatomical image (NIfTI/NRRD/etc.).
        main_nickname: optional display nickname for the main image.
        segmentation:  optional path to a segmentation image layer.
        overlays:    optional list of {"image", "nickname"?, "colormap"?} overlay layers.
        labels:      optional ITK-SNAP label-description file to load.
        tags:        optional list of tags to attach to the main image.

    Returns a dict with the workspace path, ok flag, the itksnap-wt log, and the
    exact command run (handy for the agent to show its work).
    """
    return build_workspace(
        output_path, main_image, main_nickname, segmentation, overlays, labels, tags
    )


@mcp.tool()
def add_segmentation(workspace_path: str, segmentation: str, nickname: str | None = None) -> dict:
    """Add a segmentation layer to an existing workspace (in place)."""
    ws = _require(workspace_path, "workspace")
    seg = _require(segmentation, "segmentation")
    args = ["-i", ws, "-layers-add-seg", seg]
    if nickname:
        args += ["-props-set-nickname", nickname]
    args += ["-o", ws]
    return {"workspace": ws, "log": _run(args)}


@mcp.tool()
def set_labels(workspace_path: str, label_file: str) -> dict:
    """Load an ITK-SNAP label-description file into an existing workspace (in place)."""
    ws = _require(workspace_path, "workspace")
    lab = _require(label_file, "label file")
    return {"workspace": ws, "log": _run(["-i", ws, "-labels-set", lab, "-o", ws])}


@mcp.tool()
def list_layers(workspace_path: str) -> str:
    """List the image/mesh layers in a workspace."""
    return _run(["-i", _require(workspace_path, "workspace"), "-layers-list"])


@mcp.tool()
def inspect_workspace(workspace_path: str) -> str:
    """Dump a workspace in human-readable form (for the agent to verify its work)."""
    return _run(["-i", _require(workspace_path, "workspace"), "-dump"])


@mcp.tool()
def itksnap_wt_info() -> dict:
    """Diagnostic: report the itksnap-wt binary path this server is using."""
    return {"itksnap_wt": WT, "exists": Path(WT).exists()}


if __name__ == "__main__":
    mcp.run()  # stdio transport
