# Prototype: agent-assisted ITK-SNAP workspace creation via MCP

A small, **working** demonstration for the OS4LS proposal: an MCP server that
wraps the *existing* `itksnap-wt` CLI, plus an agent skill that drives it to
**batch-create review-ready ITK-SNAP workspaces** for a cohort.

It exists to make three grant ideas concrete and de-risked:

1. **"ITK-SNAP as a tool an agent calls" (Aim 1.2)** — exercised on the lowest-risk
   surface that already ships (`itksnap-wt`), no new C++ required.
2. **The "constellation of MCP endpoints" pattern** — one thin wrapper turns a
   mature CLI into a composable MCP endpoint; the same pattern extends to greedy,
   SegFlow4D, c3d, etc.
3. **Use case UC-A2 (programmatic workspace assembly)** — an agent prepares
   ready-to-open sessions for every subject, instead of a human hand-configuring each.

> This is a prototype/illustration, **not** the proposed deliverable. The real
> Aim 1 work is a first-class headless API; this shows the agentic flow works today
> by shelling out to `itksnap-wt`.

## Layout

```
prototype/
  itksnap_wt_mcp/server.py     # the MCP server (FastMCP) wrapping itksnap-wt
  skills/itksnap-workspace-builder/SKILL.md   # agent skill that drives the MCP
  demo/batch_create.py         # reference batch run (same core fn the MCP tool wraps)
  demo/sample_manifest.json    # example cohort manifest
```

## Requirements

- A built `itksnap-wt` (this repo's `build-release/Utilities/Workspace/itksnap-wt`).
- Python 3.10+ and the MCP SDK: `pip install "mcp[cli]"`.
- Point the server at the binary: `export ITKSNAP_WT=/abs/path/to/itksnap-wt`
  (it also auto-detects common build dirs / PATH).

## Try it without an agent (reference run)

```bash
export ITKSNAP_WT=$PWD/../../../build-release/Utilities/Workspace/itksnap-wt
python demo/batch_create.py \
  --manifest demo/sample_manifest.json \
  --testdata ../../../itksnap/Testing/TestData \
  --out out/
# -> out/subj001.itksnap, subj002.itksnap, subj003.itksnap
```

Verify a result:

```bash
$ITKSNAP_WT -i out/subj002.itksnap -layers-list
```

## Use it with an agent (the actual demo)

Run the server over stdio and register it with an MCP client (Claude Desktop,
Claude Code, Cursor, …). Example client config:

```json
{
  "mcpServers": {
    "itksnap-wt": {
      "command": "python",
      "args": ["/abs/path/to/prototype/itksnap_wt_mcp/server.py"],
      "env": { "ITKSNAP_WT": "/abs/path/to/itksnap-wt" }
    }
  }
}
```

Then load `skills/itksnap-workspace-builder/SKILL.md` and ask, e.g.:

> "Build a review-ready workspace for every image in `itksnap/Testing/TestData`,
>  each with the T1 as the main layer and tagged `status:needs-review`."

The agent discovers the files, calls `create_workspace` per case, verifies with
`list_layers`, and reports the commands it ran.

## Tools exposed

| Tool | What it does |
|---|---|
| `create_workspace` | new workspace: main image + overlays/seg/labels/tags |
| `add_segmentation` | add a seg layer to an existing workspace |
| `set_labels` | load a label-description file |
| `list_layers` / `inspect_workspace` | verify a workspace |
| `itksnap_wt_info` | report the binary in use |

## A/B experiment (manual-context-free agent vs. MCP-scaffolded agent)

`data/` holds a 10-subject demo cohort; `experiment/` holds a controlled A/B that
runs the **same agent** twice — once with **no** itksnap-wt context (it must discover
the CLI cold), once **with** the MCP server + skill — to isolate what the scaffolding
buys. See `experiment/EXPERIMENT.md` for the protocol, `task-no-mcp.md` /
`task-with-mcp.md` for the two prompts, and:

```bash
export ITKSNAP_WT=$PWD/../../../build-release/Utilities/Workspace/itksnap-wt
python experiment/verify.py output/no-mcp     # objective correctness score (/13)
python experiment/verify.py output/with-mcp
```

## How this maps to the grant

- The MCP server is a stand-in for one node of the **constellation** (`track1-01.md`
  → "Architecture — a constellation of composable MCP endpoints").
- The SKILL.md is a concrete instance of the **agent-assisted contributor toolkit**
  idea (Aim 2.3) applied to *driving* a tool rather than wrapping a model.
- Swapping `itksnap-wt` for the future headless API (Aim 1.1) is a drop-in upgrade:
  the agent-facing surface stays the same; the engine underneath gets richer.
