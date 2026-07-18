# RESUME — ITK-SNAP Agentic API · CAIMI Builder Showcase sprint

You are resuming the ITK-SNAP "agentic API" prototype. **The current focus is a time-boxed
sprint to submit a SIIM-CAIMI26 AI Builder Showcase entry.** Thesis unchanged:
"model proposes, human disposes" — expose expert human judgment as a callable, resumable,
audited pipeline step an external agent can invoke, shown on camera.

## ⏰ The deadline drives everything
- **CAIMI submission due: 2026-07-24, 11:59 PM PST.** Today's baseline was 2026-07-17 → ~7 days.
- Deliverable = a **500-word abstract (6 sections) + a working demo link reviewers WILL open**
  (repo / video / live app). *Less polish, more innovation* — a working prototype beats a polished slide.
- Portal: AbstractScorecard EventKey **`QRFBVSUS`**, **Chrome/Firefox only**. Create the account early.

## Read first (authoritative, in order)
1. `projects/agentic-api/docs/sprint_caimi.md` — **THE SPRINT PLAN** (scope, workstreams, day-by-day,
   two go/no-go gates, abstract draft, definition-of-done). Start here.
2. `projects/agentic-api/docs/caimi-submission-requirements.md` — submission rules & §7b abstract skeleton.
3. `projects/agentic-api/docs/agentic-prototype-plan.md` — the grounded technical plan:
   §0.1 locked decisions + `features/segflow4d` findings · §5 MVP + video suite · §6 risks ·
   §8 model roadmap (TotalSegmentator flagship) · §9 pip-distribution/metrics.
4. `projects/agentic-api/docs/os4ls_work_plan_draft.md` — the grant this demo is evidence for
   (Goal 1 Milestones 1.1/1.2 == this prototype). Keep the demo aligned to it.
5. `projects/agentic-api/PROGRESS_LOG.md` — history, newest first. Auto-memory `project_agentic_api`.

## Machines (GPUs)
- **This box** (`/home/jileihao/dev/itksnap-developer`, Linux, **RTX 2080 8 GB**) = **dev/iteration**;
  8 GB → **TotalSegmentator fast (3 mm) mode** here. DLS Python deps **not installed yet** — venv Day 1.
- **Recording box = a 4090+ (24 GB)** (available): **full-res TotalSegmentator is viable** and TS +
  nnInteractive can co-reside → record the flagship there. Route full-res "propose" through the
  **async-job path** (plan §8); keep the sync endpoint for fast-mode dev. Always cache one golden
  proposal so filming never blocks on a live GPU.

Branches / repos for the sprint:
- **`itksnap` submodule → `sprint/caimi`** (already the tracked branch; = `feature/cardiac-io` + Linux
  build fixes). C++ work (audit record; stretch: live command channel) lands here.
- **`itksnap-dls` submodule → `feature/agentic-api`** (= `origin/main` + `origin/features/segflow4d` +
  the TotalSegmentator wrapper). **Currently checked out DETACHED at merge `4c92155`; origin tip is
  `bbaac51` (the TS wrapper) — switch to the branch to get it:**

```bash
cd itksnap-dls
git fetch origin
git switch feature/agentic-api      # brings in the TotalSegmentator wrapper (bbaac51)
git pull
python -m venv .venv && . .venv/bin/activate
pip install -e '.[totalseg]'        # + torch with CUDA
```
NOTE: the wrapper `.gitmodules` still tracks itksnap-dls `main` (deliberate) and the submodule pointer
is NOT committed — check out the branch manually as above. itksnap-dls is MIT; branch is `feature/` singular.

- **NEW public repo `itksnap-mcp`** (proposed name; not created yet) — the Python glue (thin DLS client,
  MCP server, demo driver, manifest) + README + video links. **This is the CAIMI demo link reviewers open**
  and the future pip artifact (OS4LS §9 / `greedy_python` pattern). Scaffold Day 1, add as a wrapper
  submodule like `greedy_python`. Keep it clean/public — planning docs stay private in `projects/agentic-api/`.

## State at this handoff
DONE and pushed:
- itksnap-dls `feature/agentic-api` created + `features/segflow4d` merged (merge `4c92155`);
  **`TotalSegmentatorWrapper`** implemented + pushed (commit `bbaac51`) — automatic (prompt-free) model
  in the `ModelWrapper` registry (`AUTOMATIC`+`run()`), label-preserving encoder, `/v2/run_automatic` +
  `/v2/models/{id}/labels` endpoints, `[totalseg]` optional dep. **STATIC-VERIFIED ONLY — never run live.**
- itksnap `sprint/caimi` created & pushed; wrapper tracks it.
NOT yet built (the sprint's net-new work): audit record, thin DLS client, MCP namespace + confidence gate,
(stretch) live GUI command channel, demo driver + manifest, the video, the abstract.

## Immediate next actions (Sprint Day 1 — see sprint_caimi.md §3)
1. **Env + first light:** venv + `git switch feature/agentic-api` + `pip install -e '.[totalseg]'`;
   **scaffold the public `itksnap-mcp` repo** (README, pyproject, `demo/`) and add it as a wrapper submodule.
2. **Smoke-test TotalSegmentator on the GPU:** `GET /v2/start_session/TotalSegmentator` → `upload_raw` →
   `GET /v2/run_automatic/{id}?fast=true`; confirm the multi-label result decodes with correct geometry.
   → **Gate 1:** live TS works on this box, or cache one good proposal to `expected.nii.gz`.
3. **Spike the live command channel** (the flagship's riskiest piece): sketch a `QLocalServer` in
   `itksnap/GUI/Qt/main.cxx` forwarding JSON to existing `SNAPTestQt` slots after `exec()`.
   → **Gate 2 (Day 2):** if injecting into the running loop works, the P1 live-handoff flagship (Clip B)
   is IN; else ship the **P2 "audited callable"** floor (Clips A+C) — still a complete Showcase entry.
4. Create the AbstractScorecard portal account.

## How to work
- **The submission is the deliverable** — protect the P2 floor + the abstract; the live-handoff flagship
  is stretch, gated on the Day-2 spike. Never fake a capability we don't have.
- Integration over invention; ground every claim in real files + line numbers.
- The human-correction step is the visual star — keep it a real code path.
- Ask before consequential assumptions; state the ones you make.
