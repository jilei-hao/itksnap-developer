#!/usr/bin/env python3
"""
Score generated workspaces against the cohort CONVENTION — objective A/B metric.

Convention (single source of truth; also stated in the skill):
  - main image      = T1.nii.gz, nickname "T1"
  - overlay images  = every other *.nii.gz except seg.nii.gz; nickname = modality
                      (the filename stem, e.g. FLAIR, PET, T2, CT)
  - segmentation    = seg.nii.gz (if present)
  - tags on main    = cohort:demo, status:needs-review
  - labels          = loaded from the cohort's labels.label (a named label appears)

This catches the footguns: wrong file chosen as main (e.g. T2), an overlay added
as main / missing overlay, unnamed overlays, missing seg/tags/labels.

Usage:
    python experiment/verify.py output/with-mcp
    python experiment/verify.py output/no-mcp --data data --wt /abs/itksnap-wt
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

ROW_ID = re.compile(r"^\d{3}$")
TAGS = ("cohort:demo", "status:needs-review")


def find_wt(explicit):
    if explicit and Path(explicit).exists():
        return explicit
    env = os.environ.get("ITKSNAP_WT")
    if env and Path(env).exists():
        return env
    sys.path.insert(0, str(ROOT / "itksnap_wt_mcp"))
    from server import WT  # noqa
    return WT


def run(wt, args):
    p = subprocess.run([wt, *args], capture_output=True, text=True)
    return (p.stdout or "") + (p.stderr or "")


def parse_layers(listing: str) -> list[dict]:
    """Parse `-layers-list` rows into {role, nickname, filename, tags}."""
    rows = []
    for raw in listing.splitlines():
        line = raw.strip()
        if line.startswith("2>"):  # strip any stderr prefix
            line = line[2:].strip()
        toks = line.split()
        if len(toks) < 3 or not ROW_ID.match(toks[0]):
            continue
        role = toks[1]
        # filename is the first token containing ".nii"
        fi = next((i for i, t in enumerate(toks) if ".nii" in t), None)
        if fi is None:
            continue
        nickname = toks[2] if fi >= 3 else ""
        filename = toks[fi]
        tags = " ".join(toks[fi + 1:])
        rows.append({"role": role, "nickname": nickname, "filename": filename, "tags": tags})
    return rows


def expected(data: Path, sid: str):
    d = data / sid
    anat = sorted(p for p in d.glob("*.nii.gz") if p.name != "seg.nii.gz")
    overlays = [p.name.split(".")[0] for p in anat if p.name != "T1.nii.gz"]
    return {"overlays": overlays, "has_seg": (d / "seg.nii.gz").exists()}


def check_subject(wt, data, outdir, sid) -> list[str]:
    ws = Path(outdir) / f"{sid}.itksnap"
    if not ws.exists():
        return ["workspace missing"]

    exp = expected(data, sid)
    rows = parse_layers(run(wt, ["-i", str(ws), "-layers-list"]))
    dump = run(wt, ["-i", str(ws), "-dump"])
    issues = []

    mains = [r for r in rows if r["role"] == "Main"]
    if len(mains) != 1:
        issues.append(f"expected 1 main layer, found {len(mains)}")
    else:
        m = mains[0]
        if not m["filename"].endswith("T1.nii.gz"):
            issues.append(f"main is not T1 (got {Path(m['filename']).name})")
        if m["nickname"] != "T1":
            issues.append(f"main nickname != 'T1' (got '{m['nickname']}')")
        for tag in TAGS:
            if tag not in m["tags"]:
                issues.append(f"main missing tag '{tag}'")

    overlays = [r for r in rows if r["role"] == "Overlay"]
    got = {Path(r["filename"]).name.split(".")[0]: r["nickname"] for r in overlays}
    for mod in exp["overlays"]:
        if mod not in got:
            issues.append(f"missing overlay '{mod}'")
        elif got[mod] != mod:
            issues.append(f"overlay '{mod}' nickname is '{got[mod]}' (expected '{mod}')")
    for extra in set(got) - set(exp["overlays"]):
        issues.append(f"unexpected overlay '{extra}'")

    nseg = sum(1 for r in rows if r["role"] == "Segmentation")
    if exp["has_seg"] and nseg < 1:
        issues.append("segmentation missing")
    if not exp["has_seg"] and nseg > 0:
        issues.append("unexpected segmentation")

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
