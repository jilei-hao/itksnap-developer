#!/usr/bin/env python3
"""
Score generated workspaces against the cohort spec — objective A/B metric.

For each subject under --data, derive the expected workspace contents (T1 always;
FLAIR overlay / segmentation only if those files exist), then check the workspace
the agent produced in <output_dir>:
  - main layer present, nickname 'T1', tags cohort:demo + status:needs-review
  - FLAIR overlay (nickname 'FLAIR') present iff expected
  - segmentation present iff expected
  - label table loaded (a named label from labels.label is present)

Usage:
    python experiment/verify.py output/with-mcp
    python experiment/verify.py output/no-mcp --data data --wt /abs/itksnap-wt
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # prototype/


def find_wt(explicit: str | None) -> str:
    if explicit and Path(explicit).exists():
        return explicit
    env = os.environ.get("ITKSNAP_WT")
    if env and Path(env).exists():
        return env
    sys.path.insert(0, str(ROOT / "itksnap_wt_mcp"))
    from server import WT  # noqa
    return WT


def run(wt: str, args: list[str]) -> str:
    p = subprocess.run([wt, *args], capture_output=True, text=True)
    return (p.stdout or "") + (p.stderr or "")


def check_subject(wt: str, data: Path, outdir: Path, sid: str) -> list[str]:
    issues: list[str] = []
    ws = outdir / f"{sid}.itksnap"
    if not ws.exists():
        return ["workspace missing"]

    listing = run(wt, ["-i", str(ws), "-layers-list"])
    dump = run(wt, ["-i", str(ws), "-dump"])
    has_flair = (data / sid / "FLAIR.nii.gz").exists()
    has_seg = (data / sid / "seg.nii.gz").exists()

    # main + nickname
    if "Main" not in listing:
        issues.append("no main layer")
    if "T1" not in listing:
        issues.append("main nickname 'T1' missing")
    # tags
    for tag in ("cohort:demo", "status:needs-review"):
        if tag not in listing:
            issues.append(f"tag '{tag}' missing")
    # overlay
    n_overlay = listing.count("Overlay")
    if has_flair and (n_overlay < 1 or "FLAIR" not in listing):
        issues.append("FLAIR overlay missing/misnamed")
    if not has_flair and n_overlay > 0:
        issues.append("unexpected overlay")
    # segmentation
    n_seg = listing.count("Segmentation")
    if has_seg and n_seg < 1:
        issues.append("segmentation missing")
    if not has_seg and n_seg > 0:
        issues.append("unexpected segmentation")
    # labels (named entry from labels.label)
    if "hippo" not in dump.lower():
        issues.append("labels not loaded")
    return issues


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("output_dir")
    ap.add_argument("--data", default=str(ROOT / "data"))
    ap.add_argument("--wt", default=None)
    args = ap.parse_args()

    wt = find_wt(args.wt)
    data = Path(args.data)
    outdir = Path(args.output_dir)
    subjects = sorted(p.name for p in data.glob("subj*") if p.is_dir())

    print(f"verifying {outdir}  (itksnap-wt: {wt})\n")
    passed = 0
    for sid in subjects:
        issues = check_subject(wt, data, outdir, sid)
        if not issues:
            print(f"  PASS  {sid}")
            passed += 1
        else:
            print(f"  FAIL  {sid}: {'; '.join(issues)}")
    print(f"\nscore: {passed}/{len(subjects)} workspaces correct")
    return 0 if passed == len(subjects) else 1


if __name__ == "__main__":
    raise SystemExit(main())
