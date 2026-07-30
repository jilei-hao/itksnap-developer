# release-460 — ITK-SNAP 4.6.0

Sprint directory for the 4.6.0 release, following the metronome convention
(`~/metronome/docs/sprint-workflow.md`).

## Files

| File | Lifetime | What it holds |
|---|---|---|
| [SPRINT_PLAN.md](SPRINT_PLAN.md) | the sprint | Scope, the eight workstreams, done-criteria, risks, cut line — plus §2, a dated snapshot of branch and dependency state. |
| [PROGRESS_LOG.md](PROGRESS_LOG.md) | append-only | One dated entry per session. Never rewritten. |
| [NEXT_SESSION_PROMPT.md](NEXT_SESSION_PROMPT.md) | one session | The ignition key. Rewritten wholesale at every `/handoff`. |
| [change_tracking.md](change_tracking.md) | the sprint | What has **merged** since v4.4.0, classified feature / bugfix / build / docs. Raw material for `ReleaseNotes.md`. |
| [workstreams/](workstreams/) | the sprint | One spec per workstream. See its [README](workstreams/README.md) for why these are files rather than sub-projects. |

The first three names are fixed by metronome. `change_tracking.md` is the one addition, and it splits
from `SPRINT_PLAN.md` §2 along one line: **merged vs. not merged.** Per-commit ship/hold decisions
live in the workstream file that owns them, not in the plan.

## Start ritual

1. Read [NEXT_SESSION_PROMPT.md](NEXT_SESSION_PROMPT.md).
2. Skim [SPRINT_PLAN.md](SPRINT_PLAN.md) for where the session's goal sits. §2 goes stale fastest —
   re-verify it with §7 before trusting a branch count.
3. Only then touch code.

End the session with `/handoff`.

## Fast facts

| | |
|---|---|
| Release | 4.6.0 (trunk is at `4.6.0-alpha.1`) |
| Previous | 4.4.0, released 2025-09-08 at `20f63186` |
| Integration branch | `itksnap:staging/v460`, cut from `upstream/master` @ `679ba76a` |
| Merged since 4.4.0 | 101 commits (83 non-merge) |
| Unmerged and in scope | 15 commits across `feature/cardiac-io` and `test/dls_sam2` |
| Out of scope | the agentic API — `sprint/caimi` + `itksnap-mcp`, see `projects/agentic-api/` |
