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

## Two protocols (run B for the interesting result)

> **Honest finding first:** on a small, well-specified task over a *clean,
> well-documented* CLI like `itksnap-wt`, the unscaffolded agent does fine — and may
> use *fewer* tokens, because the MCP tool schemas add context overhead. That is a
> legitimate result, not a failure. MCP + skills earn their keep on **consistency at
> scale, error-rate on footguns, robustness to vague prompts, and composability** —
> not on token count for an easy task. Design the demo to measure those.

### Protocol A — even playing field (mechanical MCP value)
Both arms get the **task spec** (`data/README.md`) and a clear prompt
(`task-no-mcp.md` / `task-with-mcp.md`). This isolates the *mechanical* difference
(structured tools vs. raw CLI). **Expect a small gap** for a clean CLI — report it as such.

### Protocol B — vague prompt, no spec (the scaffolding's real value)
Remove the spec (`data/README.md`) from **both** scratch dirs. Use the single vague
prompt (`task-vague.md`) for both arms. The with-mcp arm still has the **skill**, which
encodes the conventions (T1 is main, overlays nicknamed by modality, tags, labels); the
no-mcp arm has neither spec nor skill and must **guess**. This is the grant-relevant
comparison — "scaffolding (MCP + skill) vs. nothing" — and it's where the footgun
subjects (subj011–013) separate the two.

> Framing note (state this in writeups): the gap in Protocol B largely reflects the
> **skill encoding institutional conventions** + the MCP tool handling picked-layer
> ordering. That *is* the value of the deliverable — skills carry conventions so a vague
> human request still yields a correct, consistent result.

## Steps (either protocol)

1. Build `itksnap-wt` (`build-release/Utilities/Workspace/itksnap-wt`); `export ITKSNAP_WT=...`.
2. **no-mcp arm:** fresh agent session, **no MCP**, in a scratch dir containing only a
   copy of `data/` (and, for Protocol A, the spec). Paste the prompt. Work into
   `output/no-mcp/`. Record metrics below.
3. **with-mcp arm:** fresh session with the MCP server registered + the
   `itksnap-workspace-builder` skill loaded (`.claude/skills/...`). Paste the prompt.
   Work into `output/with-mcp/`. Record metrics.
4. **Score both:** `python experiment/verify.py output/no-mcp` and `… output/with-mcp`.
5. Fill in `RESULTS.md`.

## What to measure (correctness & consistency — NOT tokens)

- **Correctness** — `verify.py` score (out of 13), and *which* layers/tags/labels/nicknames
  were wrong. This is the headline metric.
- **Footguns** — did it handle the hard cases? Specifically:
  - subj011: both `FLAIR` and `PET` present as overlays, each nicknamed correctly;
  - subj012: **`T1` is the main, not `T2`**;
  - subj013: `CT` overlay + seg, main still `T1`.
- **Consistency** — across 13 cases, did nicknames/tags stay uniform, or drift?
- **Failures** — # of erroring `itksnap-wt` calls before success (expect more, no-mcp).
- **Clarification** — did the agent stop to ask the user (more likely no-mcp on a vague prompt)?
- **Effort** — wall-clock, turns, tool/bash calls. *Token count is a weak signal here* — on
  an easy task MCP can cost more (schema overhead); report it but don't lead with it.

## Expected story (hypothesis)

- **Protocol A (spec given):** small gap. The clean CLI is easy to discover; MCP's overhead
  may even make it cost more tokens. Honest, expected.
- **Protocol B (vague, no spec):** the with-mcp arm follows the skill's conventions and gets
  13/13 with uniform nicknames/tags; the no-mcp arm guesses — most visibly failing the
  footguns (e.g. making `T2` the main in subj012, or leaving overlays unnamed / inconsistently
  named in subj011). The correctness/consistency gap there is the evidence for "agent-callable
  endpoints **+ skills**."

> Record numbers in `RESULTS.md`.
