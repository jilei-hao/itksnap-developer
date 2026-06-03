# Task (vague prompt — used for BOTH arms in Protocol B)

Paste this *same* low-quality prompt in both arms. The only difference between
arms is the environment (no-mcp: bare binary, no skill, no spec; with-mcp: MCP
server + skill). Do **not** provide the spec/README in either arm.

---

> I've got a bunch of subject scans in `data/`. Set them up as ITK-SNAP
> workspaces in `output/<arm>/` so a reviewer can open each one and check the
> segmentation. The itksnap-wt tool is at:
> `/Users/jileihao/dev/itksnap-dev/itksnap-developer/build-release/Utilities/Workspace/itksnap-wt`

---

That's intentionally underspecified — no nicknames, no tags, no per-modality
rules, no mention of which image is "main". The point is to see whether the
**skill's conventions** (on the with-mcp side) produce a correct, consistent
result while the **cold agent** has to guess — and whether it guesses wrong on
the footgun subjects (subj011–013).

(For the no-mcp arm, also forbid reading any itksnap-wt docs/skill/source in the
repo, as in `task-no-mcp.md`.)
