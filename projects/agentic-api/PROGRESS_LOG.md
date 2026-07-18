# Agentic API — Progress Log

Newest entries first. See `docs/agentic-prototype-plan.md` for the authoritative plan
and `NEXT_SESSION_PROMPT.md` for the resume prompt.

## 2026-07-18 — Sprint Day 1 executed (Gate 1 PASS; Gate 2 design GREEN)

**Env (this RTX 2080 box).** The base conda env already had torch 2.3.1+cu121 (CUDA OK) plus the
whole DLS stack (nnunetv2, SimpleITK, fastapi, nnInteractive) and an old `itksnap-dls==0.0.4`.
Cloning base failed (pip pkgs), so instead: `pip install TotalSegmentator` + `pip install -e
itksnap-dls --no-deps` (editable `feature/agentic-api` → shadows 0.0.4). `models: [nnInteractive,
SAM2, TotalSegmentator]`, `TotalSegmentatorWrapper.AUTOMATIC=True`. Caveat: **nnInteractive 1.0.1
wants torch≥2.6** (we have 2.3.1) — irrelevant for TS/Gate 1; only matters if the interactive
nnInteractive model is used later (flagship uses human paintbrush, so likely not).

**itksnap-mcp repo scaffolded + pushed** (`github.com/jilei-hao/itksnap-mcp`, submodule of the
wrapper, tracks `main`): thin DLS client (`dls_client.py`, exact wire format, no ITK dep), confidence
gate placeholder, MCP server skeleton, `demo/smoke_totalseg.py`, pyproject, README. License still TBD.

**Gate 1 — PASS (empirical).** `smoke_totalseg.py` end-to-end on TS example CT (122×101×30, 3mm):
start_session(TotalSegmentator) → upload_raw → run_automatic(fast) → decoded multi-label int16,
shape (30,101,122) matching input, **5 anatomically-correct labels** (lung_upper_lobe_left, heart,
aorta, pulmonary_vein, costal_cartilages). **t[model]=12.9 s** on the RTX 2080. The "propose" backbone
works live. Finding: the DLS scalar `upload_raw` path drops spacing/origin/direction (unlike the 4D
path) → automatic seg runs on identity geometry; fine for Gate 1, must thread geometry through for
faithful demo output.

**Gate 2 — DESIGN GREEN** (`docs/spike_live_channel.md`). Read `main.cxx` (harness built at 1445–1446
*before* `app.exec()` at 1504; `QTimer::singleShot` already defers work into the loop) and
`SNAPTestQt.h` (primitives are main-thread `public slots`). A `QLocalServer` created pre-`exec()` and
serving during it dispatches JSON commands on the GUI thread — *safer* than today's worker-thread JS.
No blocker. Next: a `set_cursor`-only prototype (needs an ITK-SNAP rebuild) to close Gate 2 empirically.

**Commits.** wrapper `b2ee0f5` (sprint docs), `9804b2a` (itksnap-mcp submodule + reference docs);
itksnap-mcp `53f8dbd` (scaffold, pushed). itksnap-dls left on `feature/agentic-api` locally (pointer
intentionally not recorded — wrapper tracks its `main`).

## 2026-07-17 — CAIMI Builder Showcase sprint planned

- Target: submit a **SIIM-CAIMI26 AI Builder Showcase** entry by **2026-07-24 11:59 PM PST** (~7 days) —
  a 500-word abstract (6 sections) + a working demo/repo/video. The demo is concrete evidence-of-function
  for **OS4LS Goal 1** (Milestones 1.1/1.2).
- Wrote **`docs/sprint_caimi.md`** — 7-day plan: scope (**P2 "audited callable" = guaranteed floor;
  P1 "live handoff" = stretch flagship gated on a Day-2 live-channel spike**), workstreams W0–W8,
  day-by-day, two go/no-go gates, an abstract draft, definition-of-done, and sprint risks.
- Rewrote **`NEXT_SESSION_PROMPT.md`** for the sprint + this-machine (Linux) setup.
- Ground truth checked: **this box has an NVIDIA RTX 2080 (8 GB)** → it can be the demo box, **fast-mode
  TS only**. `itksnap-dls` is detached at merge `4c92155`; the TS wrapper `bbaac51` is on
  `origin/feature/agentic-api` — `git switch` to it. C++ audit-record work lands on `itksnap` `sprint/caimi`.
- Eligibility: **clears the vendor gate** (academic OSS; using TS/nnInteractive SDKs ≠ vendor submission);
  TS `total`/`total_mr` Apache; nnInteractive weights non-commercial (demo-OK, product liability).
- **Open items resolved (owner):** presenter = **jilei-hao** (abstract header placeholder pending Paul);
  recording GPU = a **4090+ (24 GB)** available → **full-res TS viable** (this RTX 2080 = dev only);
  **new public repo `itksnap-mcp`** for the Python glue + demo (the CAIMI link + future pip artifact,
  `greedy_python` pattern) — C++/server stay in `itksnap`/`itksnap-dls`, planning stays private;
  scope **P2-floor / P1-stretch confirmed**.

## 2026-07-17 — Planning complete; TotalSegmentator wrapper landed & pushed

### Decisions locked (owner)
1. Handoff architecture: **drive the human's ONE live GUI process** (not headless + ingest hook).
2. Flagship scope: **build P2 "audited callable" first**, then flagship P1 "uncertain case routed to human".
3. DLS work happens on **`feature/agentic-api`** (= `origin/main` + `origin/features/segflow4d` merged).
4. Audit record = min set `{op, timestamp, agent-vs-human, changed-voxel count, bbox, before/after label counts}`.

### Done
- Wrote the full plan `docs/agentic-prototype-plan.md`: workspace map, orientation report,
  capability map, prototype concepts P1–P4 (ranked), MVP + video suite, risks; **§8** model
  roadmap; **§9** distribution/metrics. Grounded in a 12-agent code-orientation pass.
- Created `itksnap-dls` branch `feature/agentic-api`, merged `features/segflow4d` (merge `4c92155`).
- Implemented `TotalSegmentatorWrapper` (commit `bbaac51`) — automatic (prompt-free) segmentation
  model, registered in the `ModelWrapper` registry; new `/v2/run_automatic` + `/v2/models/{id}/labels`
  endpoints; label-preserving encoder; `[totalseg]` optional dep. **Static-verified only** (not run live).
- Both pushed to `origin`.

### Key findings (citations in the plan)
- Headless data plane EXISTS and is Qt-free (proven by `itksnap-wt`); voxel edits go through the
  Logic API (`IRISApplication::SetCursorPosition`, `SegmentationUpdateIterator`), not GUI mouse handlers.
- `SNAPTestQt` is the Layer-2 substrate (semantic addressing + event injection) but is test-scoped
  (canned `.js` via `--test`, pre-`exec()`); a **live external RPC channel is net-new** — the hard part.
- DLS `features/segflow4d` = modular `ModelWrapper` registry (nnInteractive + SAM2) + an async
  submit→poll→result job module (`modules/propagation`) = the right analog for a resumable review step.
- Models (§8): TotalSegmentator = flagship (Apache `total`/`total_mr`); MONAI VISTA3D via NVIDIA
  NV-Segment-CT = strategic (unified auto+interactive, one model); SegVol (MIT) = clean-license backup.
  nnInteractive weights are CC BY-NC-SA (non-commercial) — OK for demo, resolve before shipping.
- Distribution (§9): do NOT pip-ship the compiled Qt GUI (3D Slicer precedent). Pip-ship the L1 Python
  API + MCP server (the `greedy_python` pattern) — that is the auto-updatable, measurable artifact;
  keep the GUI on a native/signed installer; fix version drift with a protocol-version handshake;
  count downloads via `pypistats` + `pypinfo`/BigQuery (filter `installer.name='pip'`, caption "downloads").

### Not done / next
- Live smoke test on a GPU box; async-job version of automatic inference; MVP vertical slice
  (P2 audit record → live GUI channel → MCP namespace). See `NEXT_SESSION_PROMPT.md`.
