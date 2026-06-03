# Experiment results

Fill in after each run. Lead with **correctness & consistency**, not tokens.

- Date:
- Agent / model:
- Protocol: **A** (spec given) / **B** (vague prompt, no spec)  ← circle one
- itksnap-wt version / commit:

## Scorecard

| Metric | no-mcp | with-mcp |
|---|---|---|
| `verify.py` score (/13) | | |
| Consistency (nicknames/tags uniform?) | | |
| Failed `itksnap-wt` calls before success | | |
| Clarification questions to user | | |
| Wall-clock | | |
| Agent turns | | |
| Tool/bash calls | | |
| Tokens (weak signal — note only) | | |

## Footgun outcomes

| Subject | Footgun | no-mcp | with-mcp |
|---|---|---|---|
| subj011 | both FLAIR + PET overlays, correctly nicknamed | ☐ pass / ☐ fail | ☐ pass / ☐ fail |
| subj012 | T1 is main (NOT T2) | ☐ pass / ☐ fail | ☐ pass / ☐ fail |
| subj013 | CT overlay + seg, main = T1 | ☐ pass / ☐ fail | ☐ pass / ☐ fail |

## verify.py output

```
# paste: python experiment/verify.py output/no-mcp
```

```
# paste: python experiment/verify.py output/with-mcp
```

## Observations / quotes

- no-mcp: (how it discovered the CLI; where it tripped; any wrong guesses)
- with-mcp: (did the skill conventions carry; one-call-per-case?)

## Takeaway (for the full application)

- One or two sentences: where did the scaffolding help, where did it not, and what
  does that imply for the "agent-callable endpoints + skills" deliverable?
