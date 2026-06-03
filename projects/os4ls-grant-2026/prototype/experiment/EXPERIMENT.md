# Experiment: does the MCP server + skill actually help an agent?

A controlled A/B. **Same agent**, same task, same cohort — the *only* variable is
whether the agent has the `itksnap-wt` **MCP server + skill** scaffolding.

| Arm | Scaffolding | Agent must… |
|-----|-------------|-------------|
| **no-mcp** (`output/no-mcp/`) | none — just the `itksnap-wt` binary | discover the CLI cold and script it |
| **with-mcp** (`output/with-mcp/`) | `itksnap-wt` MCP server + `itksnap-workspace-builder` skill | call structured tools |

This isolates what the grant deliverable (a composable MCP endpoint + an agent
skill) is worth, separately from raw model capability.

## Keeping the no-mcp arm honest (no context leakage)

The repo contains files that describe `itksnap-wt` (the skill, this prototype's
README, the server source). For the no-mcp arm the agent must **not** see them:

- Run it in a **fresh session** with **no MCP server attached**.
- Give it only `task-no-mcp.md`, the **binary path**, and the `data/` folder.
- Instruct it not to read `prototype/skills/**`, `prototype/README.md`, or
  `prototype/itksnap_wt_mcp/**`. (Easiest: run the agent from a scratch dir that
  contains only a copy of `data/`, and pass the absolute binary path.)

The with-mcp arm gets the server registered + the skill loaded, and `task-with-mcp.md`.

## Protocol

1. Build `itksnap-wt` (`build-release/Utilities/Workspace/itksnap-wt`); `export ITKSNAP_WT=...`.
2. **Arm A (no-mcp):** new agent session, no MCP. Paste `task-no-mcp.md`. Let it work
   into `output/no-mcp/`. Record: wall-clock, # of turns/tool (bash) calls, # of failed
   commands, whether it gave up or asked for help.
3. **Arm B (with-mcp):** new agent session with the MCP server + skill. Paste
   `task-with-mcp.md`. Let it work into `output/with-mcp/`. Record the same.
4. **Score both:** `python experiment/verify.py output/no-mcp` and
   `python experiment/verify.py output/with-mcp`.

## What to measure

- **Correctness** — `verify.py` score (0–10), and which layers/tags/labels were wrong.
- **Effort** — wall-clock, agent turns, bash/tool calls, tokens if available.
- **Failures** — # of erroring `itksnap-wt` invocations before success (expect more in no-mcp).
- **Consistency** — did every subject get the same treatment, or did quality drift across 10?
- **Robustness to variation** — did it correctly handle the subjects that have a FLAIR
  overlay (×4) and/or a segmentation (×2), vs. T1-only?

## Expected story (hypothesis)

The no-mcp agent spends turns probing the CLI (running it for usage, trial-and-error on
flag syntax, picked-layer semantics for nicknames/tags) and is more likely to drift or
err across 10 cases. The with-mcp agent calls one documented tool per case and verifies
with `list_layers`. If the scaffolded arm is faster, more correct, and more consistent,
that's direct evidence for the "agent-callable endpoints + skills" deliverable.

> Record the numbers in `RESULTS.md` (create it) so they can go in the full application.
