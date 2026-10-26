# RESUME — ITK-SNAP Agentic API · after the CAIMI26 talk

## Current state (read this paragraph first)

The prototype makes ITK-SNAP a tool an AI agent can call. The agent asks a model server for a
segmentation, applies it into the live ITK-SNAP window, a person corrects it, and every edit
comes back as an audit record. The prototype was presented at **SIIM-CAIMI26 on Mon 2026-10-26
(AI Builder Showcase, Session 1007), and the talk went well.** The talk work is finished. It
lives in `presentation/`, which is now an archive and a reusable method (`presentation/method.md`).
No agentic-API code has changed since July. The code is on `itksnap` `sprint/caimi` (6
agentic commits), `itksnap-mcp` `main` and `itksnap-dls` `feature/agentic-api`. None of it is
in ITK-SNAP 4.6; the 4.6 sprint lists it as an explicit non-goal.

## Before touching anything

**Jilei picks this session's goal.** Show the open items below (a reminder list, not a priority
order) and ask which one to work on.

## Open items

**Agentic API code** (from `project_retrospective.md`; none started)
- Wire the confidence gate: `itksnap-mcp/src/itksnap_mcp/confidence.py` (`agreement_gate`) is
  unit-tested but called by nothing. This was future direction 1 in the talk.
- Make accepting or discarding a correction an explicit, recorded action. Today it is implied by
  saving the file.
- A dedicated demo build. `build-release/` is `staging/v460`, which lacks `--agent-listen`, the
  audit code and the `itksnap-wt` label commands. Build `sprint/caimi`, or its 6 agentic commits
  on `upstream/master`, in its own directory. Needed before any further live demo.
- Repoint or remove the broken `itksnap-wt` MCP registration in `~/.claude.json`. It points at a
  deleted file and fails to connect at every session start.

**Where the prototype goes**
- The R01 plan has an open decision: task Y0.3, "Decide the agentic-API prototype's place",
  owners Paul and Jilei. The proposal is to fold the live channel into the bridge protocol and
  the audit record into the provenance work, not to keep a parallel surface. See
  `projects/r01-planning/task_list.md` and `milestones.md`. It depends on that meeting.
- `presentation/qa.md`: three answers drafted on 2026-10-26 (MONAI Label / 3D Slicer; release
  timing; who runs the model server). They are marked `*Unsourced:*` where nothing backs them.
  Jilei hasn't reviewed them; review before reusing.

**After the talk (optional)**
- Record which questions were actually asked in the Q&A, while memory is fresh. Nothing captures
  them yet. They would improve `qa.md` for the next talk.
- The organisers' deck (`presentation/final/uploaded_2026-10-23/1007_Hao.pptx`, local only)
  has a stray period on slide 3, in its own paragraph. This is moot now that the talk is over.

## Files to read first

1. `PROGRESS_LOG.md`, the two newest entries (2026-10-05 → 10-22 built the talk; 10-22 → 10-26
   tuned and delivered it).
2. `project_retrospective.md`: the prototype's limits and next steps.
3. `docs/agentic-prototype-plan.md` and `design_docs/DESIGN.md`: the plan and the design.
4. Only for talk work: `presentation/method.md`, then `presentation/README.md`.

## Commands

```bash
cd itksnap-mcp && PYTHONPATH=src python3 -m pytest -q     # 12 tests; plain pytest cannot import the package
cd projects/agentic-api/presentation && python3 build.py  # deck, script.html, Word script, phone PDFs; prints timing
```

## Known traps

- **`itksnap-mcp` tests need `PYTHONPATH=src`** (or `pip install -e .`). Without it, both test
  files fail to collect with `No module named 'itksnap_mcp'`. That's an environment issue, not
  a failure.
- **`build-release/` can't run the agentic demo** (see above). Don't point the MCP server at it.
- **`presentation/frozen.json` is still in place.** The build refuses on-slide changes. Delete it
  only if the slides are reused for another talk.
- **`build/` is regenerated on every build;** never edit it. To change speaker notes in the
  organisers' deck, edit `talk.md` and run `python3 build.py --notes-into
  final/uploaded_2026-10-23/1007_Hao.pptx`.
- **The repo is public.** The acceptance email, the SIIM template, and `presentation/review/`,
  `final/` and `build/` stay out of git, enforced by `presentation/.gitignore`.
- **SAM2 is being dropped from the DLS,** but the demo footage still shows it in the model table.
- **Language for talks and abstracts is neutral on purpose** (Jilei): no selling points, no
  questions to the audience.
