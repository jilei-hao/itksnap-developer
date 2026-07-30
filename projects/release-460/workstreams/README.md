# Workstreams

## Why these are files, not sub-projects

Metronome's three-file pattern (`SPRINT_PLAN.md` / `PROGRESS_LOG.md` / `NEXT_SESSION_PROMPT.md`) is
scoped to a **sprint** — one stretch of consecutive sessions with one focus. It is not scoped to a
feature. Giving each of the eight 4.6.0 workstreams its own triple would mean:

- eight `NEXT_SESSION_PROMPT.md` files, seven of which are stale at any moment — and that file's
  whole value is that it is the one true ignition key;
- `/handoff` asking "which sprint?" every session (the skill explicitly does this when more than one
  sprint is active), turning a ritual into a decision;
- one release's history scattered across eight logs.

So: **one sprint directory for the release, one file per workstream here.** Each file holds goal,
current state, branch, dependencies, open questions, and done-criteria — the durable spec. Session
history stays in the single `PROGRESS_LOG.md`.

## The promotion rule

Promote a workstream to a peer sprint directory — `projects/<name>/`, with its own three files —
when **both** hold:

1. It is the sole focus of three or more consecutive sessions, and
2. it has its own repo, branch, and test suite, so its state is genuinely independent of the release.

That is exactly how `projects/agentic-api/` and `projects/4dcta_improvement/` came to exist. Two
candidates here could qualify later: **W3 (itksnap-dls refactor)** and **W7 (cmesh integration)** —
both are cross-repo. Neither qualifies yet; neither has had a session.

On promotion: create `projects/<name>/`, move the workstream file into it as `SPRINT_PLAN.md`, start
fresh `PROGRESS_LOG.md` and `NEXT_SESSION_PROMPT.md`, and leave a one-line pointer in the row here.
Sub-directories under `projects/release-460/` are **not** how it is done — sprint directories are
peers under `projects/`.

## Files

| # | File | Workstream |
|---|---|---|
| W1 | [merge-backlog.md](merge-backlog.md) | Land the ready, unmerged backlog |
| W2 | [developer-docs.md](developer-docs.md) | Developer docs & governance |
| W3 | [dls-refactor.md](dls-refactor.md) | itksnap-dls refactor |
| W4 | [auto-seg-ui.md](auto-seg-ui.md) | Fully automatic segmentation UI |
| W5 | [propagation-ui.md](propagation-ui.md) | Segmentation propagation UI |
| W6 | [free-rotation-sync.md](free-rotation-sync.md) | Free-rotation 2D/3D sync (#229) |
| W7 | [cmesh-integration.md](cmesh-integration.md) | cmesh release + itksnap mesh refactor |
| W8 | [bugfixes.md](bugfixes.md) | Bugfixes & small improvements |

## Template

```markdown
# Wn — <title>

**Status:** not started | in progress | blocked | merged
**Branch:** <repo>:<branch>, or "none yet"
**Depends on:** <workstreams or repos>

## Goal
One paragraph. What is true when this is done that isn't true now.

## Current state
Only what has been verified, with the evidence (commit, file:line, test name).

## Plan
Ordered steps.

## Open questions
Things that need a decision before the work can finish.

## Done-criteria
Beyond SPRINT_PLAN's five general criteria — what is specific to this workstream.
```
