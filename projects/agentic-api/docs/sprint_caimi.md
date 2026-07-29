# SPRINT: CAIMI AI Builder Showcase — 7-day plan

**Sprint name:** `sprint/caimi`  · **Created:** 2026-07-17 · **Presenting author:** jilei-hao _(placeholder in the abstract header pending consult with Paul)_

**North star.** Submit a **SIIM-CAIMI26 AI Builder Showcase** entry by the deadline with a
*working, demonstrable* prototype: ITK-SNAP exposed as a callable tool an external agent
invokes, where the model proposes an automatic segmentation and a **human expert corrects it,
with the correction returned as a structured, audited record**. "Model proposes, human disposes."

> This sprint is the concrete **evidence-of-function** for **OS4LS Goal 1** (Milestones 1.1 headless
> API + agent-facing MCP + `request_review`; 1.2 expert-interaction capture format). Building the
> showcase demo directly advances the grant deliverable — see `os4ls_work_plan_draft.md`.

---

## 0. Hard constraints (from `caimi-submission-requirements.md`)

- **Deadline: 2026-07-24, 11:59 PM PST** (≈ early morning Jul 25 EST). **7 days from today (Jul 17).**
- **Portal:** AbstractScorecard, EventKey **`QRFBVSUS`**, **Chrome or Firefox only**. Account is
  separate from My SIIM — create it early.
- **Deliverable = 500-word abstract (6 sections) + a demo link reviewers WILL open** (repo / live
  app / short video). "Demo or Evidence of Function" is load-bearing; invest in it.
- Six required sections, in order: **Problem · Approach/What You Built · Demo or Evidence of Function ·
  Clinical/Operational Impact · Current Stage · What Feedback You're Seeking.**
- Review criteria: Problem Relevance · Creativity & Innovation · Feasibility & Real-World Potential ·
  Quality of Demo/Evidence. **Scientific rigor is explicitly NOT primary** — *less polish, more innovation.*
- **Not blind** (unlike Experiential) → institution names are fine; reviewers engage with the repo.

### Eligibility gate — cleared, but confirm (do Day 1)
- **Vendor submissions are forbidden.** ITK-SNAP is academic open-source (GPL-3.0, PICSL/Penn); no
  commercial co-authors; **using TotalSegmentator / nnInteractive models or SDKs is NOT a "vendor
  submission"** (§5: using a vendor's SDK ≠ vendor submission; the problem is a vendor *co-author* or
  product promotion). Keep the framing tool-agnostic and non-promotional. → **clears.**
- **Model licenses for the demo:** TotalSegmentator `total`/`total_mr` weights are **Apache-2.0** (fine);
  nnInteractive weights are **CC BY-NC-SA (non-commercial)** — fine for an academic showcase, flagged as
  a product-transition liability, not a submission blocker.

---

## 1. Scope — what we commit to build

Two tiers, matching the **locked decision** (plan §0.1/§7: *build P2 first, then grow into P1*).

### GUARANTEED floor — **P2 "Callable expert correction as an audited diff"**
An agent calls ITK-SNAP as a tool:
`snap.open(case)` → `snap.propose()` (TotalSegmentator auto-segmentation via the DLS server) →
confidence gate → the **human corrects the label in ITK-SNAP** → `snap.commit()` returns a
**structured JSON audit record** (`{op, timestamp, agent-vs-human, changed-voxel count, bbox,
before/after label counts}`). Films as **Clip A** (callable / auto-accept) + **Clip C** (audited diff).
This alone is a complete, honest, "vibe-coded prototype that works" — exactly what the Showcase rewards.

### STRETCH flagship — **P1 "Uncertain case routed to the human — LIVE"**
Same story, but the correction happens in the **same live GUI process the agent is driving**, via a
new live command channel (`QLocalServer` → `SNAPTestQt` slots). Films as **Clip B** (the on-camera
handoff — the irreplaceable "wow"). **Gated on the Day-2 live-channel spike** (see Gate 2). If the
spike fails, P1 degrades gracefully (Fallback below) and we still submit P2.

**Fallback for the "same session" beat if the live channel slips:** launch ITK-SNAP normally, the
human edits, and the agent observes the change via the audit stream / workspace reload (a weaker but
truthful "human-in-the-loop" story). Do **not** fake a live channel we don't have.

---

## 2. Workstreams (map to plan §5.1 build order)

| # | Workstream | Where it lives | Status today | Plan ref |
|---|---|---|---|---|
| W0 | Env setup + de-risk; scaffold the new public repo | wrapper / venv / `itksnap-mcp` | ✅ done | §6.6 |
| W1 | "Propose" backbone: TotalSegmentator live + thin HTTP client | `itksnap-dls` `feature/agentic-api` | ✅ done (Gate 1 PASS) | §8, §2.5 |
| W2 | **Audit record** (C++ net-new) | `itksnap` `sprint/caimi` | ✅ done (`560dcd2f`) | §2.9, P2 |
| W3 | MCP namespace + confidence gate | new repo `itksnap-mcp` | ✅ tools wired + agreement gate (`f80d880`) | §5.2 |
| W4 | **(STRETCH)** live GUI command channel | `itksnap` `sprint/caimi` | ✅ prototype (Gate 2 PASS) | §6.2, P4 |
| W5 | Demo driver + `manifest.yaml` + golden data | `itksnap-mcp/demo/` | ✅ done (`run_p2.py`, `agent_send.py`, `manifest.example.yaml`; golden data stays out of the repo) | §5.3, §6.6 |
| W6 | Video production (Clips A/C; B if W4) | — | ✅ done (`final-demo.mp4` submitted; hosted at `youtu.be/H60bflq-O1o`) | §5.4 |
| W7 | 500-word abstract + public repo README | `projects/agentic-api/` | ✅ done — superseded by the 11-field form; as-sent text in `caimi-submission/caimi_submitted.md` (README+MIT `f80d880`) | §7b reqs |
| W8 | Portal submission | AbstractScorecard | ✅ done — submission ID `2480386`, status Complete, Oral | §1 reqs |

**Branch/repo layout for this sprint**
- C++ audit record + (stretch) live channel → **`itksnap` submodule, `sprint/caimi`** (already the tracked branch).
- DLS server work → **`itksnap-dls`, `feature/agentic-api`** (origin has the TS wrapper at `bbaac51`).
- Python glue (thin DLS client, MCP server, demo driver, manifest) → **a NEW public repo** (proposed
  `jilei-hao/itksnap-mcp`, transferable to a PICSL/`pyushkevich` org later), added to the wrapper as a
  submodule like `greedy_python`. **This repo is the CAIMI demo link reviewers open, and the future
  pip-shippable L1/MCP artifact** (OS4LS §9 / `greedy_python` pattern). Scaffold it Day 1.
- Internal **planning docs stay private** in the wrapper `projects/agentic-api/` (grant + strategy);
  they are NOT part of the public submission repo.

---

## 3. Day-by-day

> Dates are Jul 17–24. Two go/no-go gates decide whether the flagship (P1/Clip B) is in scope.
> The P2 floor is protected regardless.

**Day 1 (Jul 17) — Environment + first light + spike kickoff**
- W0: create a Python venv; `git switch feature/agentic-api` in `itksnap-dls`
  (currently detached at merge `4c92155`; origin tip `bbaac51`); `pip install -e '.[totalseg]'` + torch (CUDA).
- W0: **scaffold the new public repo** `itksnap-mcp` (README, `pyproject.toml` via scikit-build-core/
  `greedy_python` pattern, `demo/`, MIT-or-compatible license) and add it as a wrapper submodule. This
  becomes the CAIMI demo link.
- W1: **smoke-test TotalSegmentator** — `GET /v2/start_session/TotalSegmentator` → `upload_raw` →
  `GET /v2/run_automatic/{id}?fast=true` on a body CT; confirm the multi-label result decodes with
  correct geometry (int16, client reshapes). **RTX 2080 = 8 GB → use fast (3 mm) mode only.**
- W4 (spike start): read `main.cxx:732-746,1443-1446` + `SNAPTestQt.{h,cxx}`; sketch a `QLocalServer`
  that forwards JSON to existing `SNAPTestQt` slots after `exec()`.
- W8: create the AbstractScorecard portal account now (avoid a deadline-day surprise).
- **Gate 1 (EOD):** TS produces a labeled volume in demo-acceptable time on this GPU **and** DLS serves it.
  - PASS → live TS in the demo. FAIL → cache one good proposal to `expected.nii.gz` and demo from cache.
  - **✅ RESULT (2026-07-18): PASS** — live TS in the demo.

**Day 2 (Jul 18) — Audit record + thin client + spike verdict**
- W2: expose `UndoDataManagerCommit::m_Name` getter + add `{timestamp, actor(agent|human), op-type,
  changed-voxel count, bbox, before/after label counts}`; JSON serializer; confirm `SegmentationChangeEvent`
  fires per commit at the right granularity. Build the tiny Qt-free L1 test binary from §6.4 to prove
  voxel-edit + serialize links `itksnaplogic` alone.
  - **✅ RESULT (2026-07-18): DONE** — `itksnap` `560dcd2f`. `SegmentationAuditRecord.{h,cxx}` +
    getter + `LabelImageWrapper` capture + `IRISApplication`/`--agent-listen` accessors + L1 test
    (`SegmentationAuditRecordTest`, passes, incl. production RLE image). Confirmed one commit → one
    `SegmentationChangeEvent`. **Demonstrated end-to-end over the socket** with a real committing edit
    (`apply_box` + `IRISApplication::PaintRegionWithLabel`, `f1743f04`): `set_actor agent` → `apply_box`
    → `get_audit` returns a populated record; actor consume-on-commit verified live.
- W1: thin **DLS Python client** (HTTP + gzip + base64, **no ITK**) matching the actually-run server;
  pin the version via `/status` in `manifest.yaml`.
- **Gate 2 (EOD): live-channel spike verdict.** Can a `QLocalServer` inject `postEvent`/method-invokes
  into the running loop without the `--test` scaffold?
  - PASS → **P1 flagship IN** (Clip B); schedule W4 finish on Day 4.
  - FAIL → **ship P2** (Clips A+C); use the §1 fallback for the human beat; book P1 as post-submission.
  - **✅ RESULT (2026-07-18): PASS** — P1 flagship IN.

**Day 3 (Jul 19) — MCP namespace + confidence gate + headless slice**
- W3: MCP server with **one tool namespace** — `headless.*` (open/propose/apply/commit/read-audit) and,
  if Gate 2 passed, `live.*` (focus GUI, request_human). Confidence gate = mask instability across 2
  seeds (trivial, agent-side).
- Integrate the headless end-to-end slice: `open → propose → gate → auto-accept → commit → audited result`.
  - **✅ RESULT (2026-07-18): propose → apply → read_audit wired + run LIVE on the GPU.** `itksnap-mcp`
    `9909663` (`server.py` tools, `channel.py`, `demo/run_p2.py`) + `itksnap` `e1aa19d5` (`apply_seg_file`
    + `PaintMaskWithLabel`). Ran TotalSegmentator on a body CT → 48 correct structures → agent applied the
    left-upper-lung (1,169,665 vox) into live ITK-SNAP → populated agent-tagged audit record. **Remaining:
    the confidence gate** (`confidence.py`, mask instability across seeds — still a placeholder).

**Day 4 (Jul 20) — Integration, determinism, (stretch) live channel**
- W5: `demo/manifest.yaml` (never hardcode filenames) + deterministic **demo driver**; golden mask;
  replace `sleep` with poll-until-`SegmentationChangeEvent`.
- W4 (if Gate 2 passed): wire `live.*` to the channel; verify the agent can focus the live window on the
  uncertain slice with the proposal loaded.
- Full dry run of the target clip(s) end-to-end. Fix the packaging nit (`setuptools packages` omits
  `modules`/`common`).

**Day 5 (Jul 21) — Record**
- W6: record **Clip A** (callable/auto-accept + one-line audit) and **Clip C** (audited JSON diff);
  **Clip B** (live handoff) if W4 landed. Captions per §5.4. Host on YouTube (unlisted).

**Day 6 (Jul 22) — Abstract + repo + re-record fixes**
- W7: finalize the **500-word abstract** (§4 draft below); enforce word count excluding title/headings/
  captions/keywords; insert the real demo + repo + video links and **verify every link is reachable**.
- Public repo README: a 3-command runnable path + manifest + video links + license notes.

**Day 7 (Jul 23) — Buffer + SUBMIT**
- W8: submit via portal `QRFBVSUS` in Chrome/Firefox. Run the §6 compliance checklist. **Submit a full
  day early**; keep Jul 24 as emergency buffer only.

---

## 4. Abstract — draft v0 (tighten on Day 6; keep ≤ 500 words)

> Placeholder metrics/links in _italics_. Six sections, exact labels, in order.

**Title:** ITK-SNAP as an Agent-Callable Tool: Expert Human Correction as a Resumable, Audited Pipeline Step
**Keywords:** human-in-the-loop; interactive segmentation; agentic AI; MCP; provenance; foundation models; TotalSegmentator; open-source toolkits

- **Problem Statement.** Automatic segmentation models are good but imperfect; clinical and research
  pipelines still need expert verification, yet there is no clean way for an automated pipeline or AI
  agent to *call* a human expert as a first-class step and get a machine-consumable answer back. Expert
  judgment is trapped inside interactive GUIs.
- **Approach / What You Built.** We exposed ITK-SNAP — a 20-year, 1.1M-download open-source segmentation
  app — as an **agent-callable tool via MCP**. An agent runs automatic segmentation (TotalSegmentator,
  served by our open itksnap-dls model server), applies a confidence gate, and for uncertain cases
  **routes the case to a human** who corrects it in ITK-SNAP; the correction returns as a **structured
  audit record** (operation, actor agent-vs-human, changed-voxel count, bounding box, before/after label
  counts, timestamp). Built on ITK-SNAP's existing Qt-free Logic tier and test-harness command surface.
- **Demo or Evidence of Function.** _GitHub repo URL_ · _short video walkthrough URL_ · _run instructions_.
  The video shows the agent auto-accepting an easy case and deferring an uncertain one to a human who
  corrects it live, with the audited diff flowing back to the agent.
- **Clinical or Operational Impact.** Makes expert review an orchestrable, resumable pipeline step —
  the human becomes a callable checkpoint inside large automated cohorts, and every correction is captured
  as reusable, attributable training/provenance data (feeding model improvement).
- **Current Stage.** **Prototype** (working demo; open-source; not a product).
- **What Feedback You're Seeking.** Which audit-record fields matter most for downstream model
  fine-tuning and provenance? What confidence-gating signals do reviewers trust to decide auto-accept vs
  route-to-human? Where would this plug into your existing annotation/QA workflows?

---

## 5. Definition of done (submission-ready)

- [x] Public repo, README with a ≤3-command runnable path + `manifest.yaml`; license notes present.
- [x] ≥1 hosted, **reachable** video (Clips A+C; B if the flagship landed), captioned. `youtu.be/H60bflq-O1o` (HTTP 200, 2026-07-25).
- [x] 500-word abstract, six sections in order, word count verified (456/500; `docs/abstract.md`). Author line pending Paul. — *Superseded: the portal takes 11 fields × 250 words; the as-sent text is `caimi-submission/caimi_submitted.md`, and authors were confirmed as Hao · Pouch · Yushkevich.*
- [x] Working demo/repo/video links embedded and opened-tested. All three HTTP 200, 2026-07-25.
- [x] Not a vendor submission; framing non-promotional.
- [x] Submitted via `QRFBVSUS` (Chrome/Firefox) before 2026-07-24 11:59 PM PST. Submission ID `2480386`, status Complete.

---

## 6. Sprint risks (beyond the plan's §6)

1. **GPU — resolved favorably.** A **4090+ (24 GB) is available and is the recording box**, so **full-res
   TotalSegmentator is viable** (sharper, more recognizable anatomy → a stronger "good-but-imperfect →
   human corrects" beat) and TS + nnInteractive can co-reside. This local RTX 2080 (8 GB) is fine for
   **dev/iteration in fast (3 mm) mode**. Still cache one golden proposal so filming never blocks on a live
   GPU (plan §6.6). Consequence: full-res TS is multi-minute → route "propose" through the **async-job
   path** (plan §8) for the flagship, keeping the sync endpoint for fast-mode dev.
2. **Live command channel is the hardest net-new piece** (plan §6.2) — that is exactly why it is *stretch*
   behind Gate 2, and why P2 is the protected floor.
3. **Recording determinism** — golden mask + poll-until-event, never `sleep`; scripted demo driver over
   free-form prompting for anything frame-stable.
4. **7 days is tight.** If W2 (audit record) or W3 (MCP) slips, cut the flagship first, then Clip D/E;
   never cut the abstract or the P2 core.
5. **DLS client/server API drift** (plan §2.5) — write the client against the server actually run for the
   recording; pin the version in `manifest.yaml`.

---

## 7. Open items — resolved 2026-07-17

- ✅ **Presenting author:** **jilei-hao** presents; leave a **placeholder in the abstract header**, confirm
  with Paul (affiliation, whether Paul is co-author) before submit.
- ✅ **Recording GPU:** a **4090+ (24 GB)** is available → full-res TotalSegmentator is on the table; this
  RTX 2080 box is for dev only (see §6.1).
- ✅ **Repo:** **yes, one new public repo** (`itksnap-mcp`, proposed) for the Python glue + demo — the CAIMI
  link and future pip artifact; C++/server stay in `itksnap`/`itksnap-dls`; planning stays private in the
  wrapper. Video host: **YouTube (unlisted)** assumed.
- ✅ **Scope:** **confirmed** — P2 "audited callable" is the guaranteed floor; P1 "live handoff" is the
  stretch flagship gated on the Day-2 spike.

Still to confirm with Paul (non-blocking): abstract author line/affiliation; whether the demo repo should
live under `jilei-hao` (now) or a PICSL/`pyushkevich` org (transfer later).
