# Agentic API — Progress Log

Newest entries first. See `docs/agentic-prototype-plan.md` for the authoritative plan
and `NEXT_SESSION_PROMPT.md` for the resume prompt.

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
