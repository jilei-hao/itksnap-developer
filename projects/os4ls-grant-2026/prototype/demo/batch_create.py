#!/usr/bin/env python3
"""
Reference batch-creation script — the workflow an agent performs via the MCP server.

This calls the *same* core function the MCP `create_workspace` tool wraps
(`build_workspace`), iterating a cohort manifest to produce one review-ready
ITK-SNAP workspace per subject. It exists so the end-to-end flow can be run and
verified without a live agent; the SKILL.md drives a real agent to do the same
through the MCP tools.

Usage:
    python demo/batch_create.py \
        --manifest demo/sample_manifest.json \
        --testdata /path/to/itksnap/Testing/TestData \
        --out out/
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "itksnap_wt_mcp"))
from server import build_workspace, WT  # noqa: E402


def resolve(testdata: Path, name: str) -> str:
    return str(testdata / name)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--testdata", required=True, help="dir holding the image/label files")
    ap.add_argument("--out", default="out", help="output dir for .itksnap workspaces")
    args = ap.parse_args()

    testdata = Path(args.testdata).expanduser()
    manifest = json.loads(Path(args.manifest).read_text())
    out_dir = Path(args.out)

    print(f"itksnap-wt: {WT}")
    print(f"creating {len(manifest['cases'])} workspaces in {out_dir}/\n")

    ok = 0
    for case in manifest["cases"]:
        cid = case["id"]
        overlays = [
            {**ov, "image": resolve(testdata, ov["image"])}
            for ov in case.get("overlays", [])
        ]
        try:
            r = build_workspace(
                output_path=str(out_dir / f"{cid}.itksnap"),
                main_image=resolve(testdata, case["main"]),
                main_nickname=case.get("main_nickname"),
                segmentation=resolve(testdata, case["segmentation"]) if case.get("segmentation") else None,
                overlays=overlays or None,
                labels=resolve(testdata, case["labels"]) if case.get("labels") else None,
                tags=case.get("tags"),
            )
            print(f"  [ok]   {cid:8s} -> {r['workspace']}")
            ok += 1
        except Exception as e:  # noqa: BLE001
            print(f"  [FAIL] {cid:8s} : {e}")

    print(f"\n{ok}/{len(manifest['cases'])} workspaces created.")
    return 0 if ok == len(manifest["cases"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
