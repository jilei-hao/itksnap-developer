# Agentic API — Progress Log

Newest entries first. See `docs/agentic-prototype-plan.md` for the authoritative plan
and `NEXT_SESSION_PROMPT.md` for the resume prompt.

## 2026-07-25 — CAIMI submitted; abstract rewritten to the real form; submodule sync repaired

**Attempted:** polish the abstract for tone, then — on discovering the portal form was nothing
like our spec — rewrite it against the real form, submit, and record what was actually sent.

**Landed**

- **Submitted. SIIM-CAIMI26 AI Builder Showcase, submission ID `2480386`, status Complete,**
  preferred presentation Oral. Authors: Jilei Hao · Alison M. Pouch · Paul A. Yushkevich.
  Uploads `final-demo.mp4` + `fig1_flow.png`; links to both repos and
  `https://youtu.be/H60bflq-O1o`.
- **The form was not what `docs/caimi-submission-requirements.md` §4 described.** It is
  **11 fields, each capped at 250 words, no overall limit** — not a 500-word six-section
  abstract. Three required fields had no draft content at all: *Tech Stack*, *Known Limitations
  & Honest Failures*, and a demo description. Captured as `docs/caimi_submission_form.pdf`.
- **Rewrote the abstract against the real form** (wrapper `d5c2dcc`). Register moved from
  "scientific abstract" to plain and candid, because the form asks for exactly that
  ("rough edges are welcome", "the community learns more from honest struggles").
  Then a second pass on author direction moved it back toward objective and unpromotional —
  the audience and the PIs read as scientists. Both are recorded in the file header.
- **`caimi-submission/caimi_submitted.md`** — the as-sent text, **verified field-by-field
  against the portal preview PDF by diff**, not by eye. `caimi_submitted.docx` is generated
  from it. Author edits made in the portal are enumerated in its header.
- **`docs/build_caimi_submission.py`** — markdown → `.docx` generator, standard library only
  (no `npm`, no `node_modules`). Prints per-field word counts and **exits non-zero over the
  250-word cap**, so the limit is enforced locally instead of by the portal.
- **`project_retrospective.md`** — limitations and next steps, lessons split into development
  and abstract writing, and an assessment of the sprint system.
- **`SUBMODULE_SYNC.md`** (wrapper root, `48f4d9d`) — source of truth for which branch each
  submodule tracks per wrapper branch. Covers all **eight** submodules; `itksnap-mcp` was
  missing from `CLAUDE.md`'s table.
- **Repaired two real submodule-sync faults** (`9dc1e77`), both found by writing that file:
  - `.gitmodules` declared `itksnap-dls` on `main`, but the agentic API and the
    TotalSegmentator wrapper are on `feature/agentic-api`, where the pointer recorded at
    `3689ba8` (`bbaac51`) exclusively lives. A bare `git submodule update --remote` would
    have regressed the submodule and dropped that work. Now declared correctly.
  - **`git clone --recursive` of the wrapper had been failing.** The pointers for `itksnap`
    (`daeeb99`) and `itksnap-mcp` (`12286185`) were on **no remote branch** — each submodule
    was one commit ahead of its upstream. Pushed: `itksnap` `e06937f8..daeeb995`,
    `itksnap-mcp` `b83ef64..1228618`. No pointer bump was needed; the SHAs the wrapper already
    recorded became valid once they reached the remotes.
- Wrapper commits this session: `3689ba8` (dls bump) · `d5c2dcc` (submission + retrospective) ·
  `48f4d9d` (SUBMODULE_SYNC, authored by owner) · `9dc1e77` (sync fixes).

**Tests** — `itksnap-mcp`: **12 passed** (`~/.venvs/itksnap-mcp/bin/python -m pytest tests/`).
Word-count gate: exit 0 for both the submitted record and the draft. `SUBMODULE_SYNC.md` §3:
all eight submodules `ok` on both checks. A fresh-machine simulation
(`git fetch --depth=1 <url> <sha>` into an empty repo) reports every recorded pointer
**FETCHABLE**. No ITK-SNAP C++ build or `ctest` run — this session changed no C++.

**Broke / surprised**

1. **The submission spec we planned against was wrong**, and we only learned it at submission
   time. Everything downstream of it — a 500-word budget, six section headings, the whole
   `abstract.md` structure — was wasted shape. The requirements file was written from the
   call-for-submissions page; the actual portal form was never opened until the end.
2. **The clone was broken for five wrapper commits and nothing surfaced it** — including
   `48f4d9d`, the commit that added the file documenting it. A pointer to an unpushed commit
   resolves perfectly on the machine that made it; it is invisible without an explicit
   reachability check against the remote.
3. **My first reachability check was itself wrong.** `git ls-remote <url> | grep <sha>` matches
   only ref **tips**, so it reported `segflow4d` as missing when its pointer is a healthy
   ancestor of `origin/main`. Corrected to `git branch -r --contains` after a fetch; the trap
   is written into `SUBMODULE_SYNC.md` §3 so it does not get "simplified" back.
4. **`.docx` output is not byte-reproducible.** `zipfile` stamps entry mtimes, so every rebuild
   dirties git even when content is identical (verified: content hashes match, only
   `date_time` differs). Rebuilding before a commit produces meaningless churn. Fix is a fixed
   `ZipInfo.date_time`; not done — no new work inside a handoff.
5. **`pytest` cannot collect from the base conda env** — `ModuleNotFoundError: itksnap_mcp`,
   because the package is `src`-layout and not installed there. Use the dedicated venv or
   `PYTHONPATH=src`. Do **not** `pip install` into the base env; that is the documented trap
   that previously broke the DLS server.
6. **Word comments do not survive regeneration.** The `.docx` is generated from markdown, so a
   review round is: comment → save → extract → apply to the `.md` → rebuild. Commented copies
   are archived (`caimi_submission.REVIEW*.docx`) rather than lost. Two rounds happened this way.

**Decisions**

- **Markdown is the source of truth; `.docx` is a build artifact.** Chosen after the form
  rewrite, because the text needed to survive several review rounds and a word-count gate.
- **Generator in Python, not `docx`-js** — the npm package was absent, and installing it would
  have put `node_modules` in the repo. Standard library keeps the rebuild dependency-free.
- **`SUBMODULE_SYNC.md` outranks `.gitmodules` and `CLAUDE.md`** when they disagree; the branch
  contract is stated per wrapper branch, since a sprint branch may need different submodules.
- **§6 of that file is a drift log, not a fixed-and-deleted list** — each entry records *how the
  failure recurs*, so the checks stay motivated after the specific instance is gone.
- **Kept the developer-not-clinician disclosure** in the submitted text. It is the honest
  framing and this track rewards it.

## 2026-07-20 (session 2) — Sample demo videos + Claude-Code-callable MCP server

**Attempted:** create sample demo videos of the concept; then (on feedback) make the *agent-directed*
flow real — Claude Code driving ITK-SNAP via MCP, not a hidden script.

**Landed:**
- **Sample screencast** in `design_docs/media/` (committed in the wrapper checkpoint below):
  `agentic-demo.mp4` (15 s, captioned) + `agentic-demo.gif` + two still frames + `drive_demo.py` +
  a `README.md`. Recorded with `ffmpeg -f x11grab` on `Xvfb`, driving ITK-SNAP over the socket (scrub
  slices → apply the cached TS lung proposal, red → a correction, green), captions via a `drawtext`
  filtergraph. Needs no GPU (reuses `/tmp/p2_proposal_10.nii.gz`).
- **Key realization (surfaced by the user):** that screencast shows only ITK-SNAP reacting; the "agent"
  was `drive_demo.py`, a hardcoded socket script — **not** Claude Code, and invisible on screen. So it
  does NOT show "you directing an agent."
- **Wired the tools to Claude Code for real** — `itksnap-mcp` **`0297396`** (pushed): `apply_file` tool
  (apply a cached mask without re-running the model → GPU-free/deterministic demos) + env-var config
  (`ITKSNAP_DLS_URL` / `ITKSNAP_AGENT_SOCK`). Installed the MCP server in an **isolated venv**
  (`~/.venvs/itksnap-mcp`), registered it: `claude mcp add itksnap -- ~/.venvs/itksnap-mcp/bin/python
  -m itksnap_mcp.server` → `claude mcp list` shows **✔ Connected** (tools: list_models · propose · apply
  · apply_file · read_audit · set_actor).
- **`demo_runbook.md`** gained a "Recording with Claude Code" section: the setup, screen layout
  (Claude Code terminal + live ITK-SNAP), and the exact conversation to type.

**Verified:** an MCP client (stdio, exactly like Claude Code) listed the tools and called `apply_file` to
**drive a live ITK-SNAP end-to-end** — lung applied (1,169,665 vox), audit `actor: agent`; the server
logged the real `CallToolRequest`s. `claude mcp list` → ✔ Connected. Confidence tests 4/4.

**Broke / surprised — IMPORTANT env lesson:** `pip install 'itksnap-mcp[mcp]'` into the **base** conda env
upgraded `starlette` to 1.3.1, which **broke the DLS server** (`itksnap_dls` import → FastAPI
`Router.__init__() got an unexpected keyword argument 'on_startup'`). fastapi 0.115 pins `starlette<0.47`;
`mcp` needs a newer one — they **cannot coexist in one env**. Fix: uninstalled `mcp` from base + restored
`starlette 0.46.2` (DLS server imports again), and put the MCP server in its **own venv**. **Never install
`mcp` into the DLS base env; the MCP server gets a dedicated venv.**

**Decisions:** dedicated venv for the MCP server (isolation from the DLS FastAPI stack); `apply_file` for
GPU-free deterministic demos; MCP registered at **local (project) scope** (move to user scope if the demo
runs outside this repo). Sample videos kept as illustrative (software-rendered; the human beat is a
scripted `apply_box` standing in for a paintbrush) — the authentic take is a live Claude Code session.

**Remaining (both human-gated):** record the live Claude-Code demo on a real display (terminal + ITK-SNAP),
and submit via the portal (`QRFBVSUS`, Chrome/Firefox) before **2026-07-24 11:59 PM PST**. A fresh
Claude Code session is needed to see the `itksnap` tools (MCP loads at startup).

## 2026-07-20 — Submission deliverables: abstract + public demo repo

**Attempted:** the next-session goal — draft the SIIM-CAIMI26 submission deliverables (the 500-word
abstract + a runnable public demo README/manifest for `itksnap-mcp`). Done, plus the confidence gate.

**Landed:**
- **Abstract** — `projects/agentic-api/docs/abstract.md` (committed in the wrapper checkpoint below).
  **AI Builder Showcase** track (≤500 words, NOT blind, reviewers open the demo). **456 body words**
  (verified excluding title/headings/keywords), six sections in exact order, real results (48 TS
  structures; a concrete audit-record JSON in the Demo section, the heaviest-weighted criterion).
  Author = jilei-hao (confirm affiliation/co-authors with Paul before submit).
- **`itksnap-mcp` `f80d880`** (pushed): MIT `LICENSE` + pyproject license/classifiers; README rewritten
  to the working-prototype state with a **3-command runnable path** (DLS server → ITK-SNAP
  `--agent-listen` → `demo/run_p2.py`); `docs/` = mirrored DESIGN.md + architecture.svg + flow-chart.svg
  (de-referenced of internal paths — the public CAIMI link); `manifest.example.yaml` updated to the real
  propose/apply/socket flow; `confidence.py` gained the perturbation-agreement gate (`dice` +
  `agreement_gate`, per-label Dice across two runs → route-to-human) + `tests/test_confidence.py`.

**Verified:** abstract word count 456/500 (counter script). `tests/test_confidence.py` **4/4 pass**
(pure numpy, no GPU). All `itksnap-mcp` modules import; README links + mirrored SVGs validated (no
internal-ref leakage, SVGs well-formed). No C++ changed this session (audit-engine tests unchanged,
last 2/2).

**Decisions (why):** **License = MIT** (user-confirmed) — the repo is pure HTTP/socket glue with no ITK
(GPL) source, and MIT maximizes adoption of the pip-installable agent surface (OS4LS distribution goal);
the GUI/model-server repos keep their own licenses. Track = **Builder Showcase** (working tool + demo,
rigor not primary) not Experiential (which is blind + can't rely on a linked app). Mirrored only the
public-facing docs (DESIGN + SVGs), not IMPLEMENTATION.md (internal file:line + commit refs), into the
public repo.

**Remaining for submission (both human-gated):** W6 record the video (Clips A/C — best on the 4090 box);
W8 create the AbstractScorecard portal account (EventKey `QRFBVSUS`, Chrome/Firefox — must be a human)
and submit before **2026-07-24 11:59 PM PST**. Non-blocking: confirm the abstract author line with Paul.

## 2026-07-18 (session 4) — Design docs + architecture/flow figures

**Attempted:** write developer-facing design & implementation documentation for the whole agentic-API
system, with diagrams. Done. **Docs-only session — no code changed.**

**Landed:** new folder `projects/agentic-api/design_docs/` (committed in the wrapper checkpoint below):
- `DESIGN.md` — the *why*: problem framing, the three-tier architecture and why each seam exists, the two
  channels (HTTP propose / Unix-socket drive-read), the core "reconstruct the audit record from the undo
  delta" idea (with a worked 2×2-patch example), actor consume-on-commit, geometry restoration, and the
  end-to-end story. Human-readable.
- `IMPLEMENTATION.md` — the *how*: `file:line` references across all three repos (DLS wire format; the
  `itksnap-mcp` modules; the `main.cxx` channel dispatch table; the Logic-tier engine — `BuildFromDeltas`
  walk, `StoreUndoPoint` chokepoint, actor model, `PaintMaskWithLabel`); a step-by-step end-to-end code
  trace of one `apply_seg_file`; the testing story; known limitations; a reference-commit table.
- `architecture.svg` — layered component diagram (Agent/MCP → DLS via HTTP + ITK-SNAP via socket; the
  ITK-SNAP internal stack from channel → chokepoint → audit record).
- `flow-chart.svg` — a 14-step sequence diagram (Agent · DLS · ITK-SNAP · Human) of the full run:
  propose → gate → apply → in-GUI processing → audit read-back → human correction → human-tagged diff.

**Verified:** both SVGs are well-formed XML and were **rendered to PNG with `rsvg-convert` and visually
inspected** (layout/labels/arrows/legend all legible). C++ tests unchanged — re-ran `IRISApplicationTest`
+ `SegmentationAuditRecordTest` for the record: **2/2 pass**. No submodule code changed (itksnap only has
the pre-existing `Submodules/greedy` untracked content; itksnap-mcp clean).

**Decision (open):** placed the docs in the wrapper's private planning area (`projects/agentic-api/`,
alongside the other docs) because `DESIGN`/`IMPLEMENTATION` cite internal commit hashes + cross-repo paths.
**Open option for next session:** mirror the public-facing pair (`DESIGN.md` + the two SVGs, lightly
de-referenced) into the `itksnap-mcp` repo, since that is the link CAIMI reviewers open — decide when
writing the demo README (W7).

## 2026-07-18 (session 3) — Full P2 flow LIVE: propose → apply → audit through MCP

**Attempted:** the next-session goal — wire the full P2 flow through `itksnap-mcp` with a *real*
proposed segmentation (propose → apply → read the audit record) and run it end-to-end on the GPU.
Landed, including a live GPU run.

**Landed (commit hashes):**
- `itksnap` `sprint/caimi` **`e1aa19d5`** (pushed): `IRISApplication::PaintMaskWithLabel` + `apply_seg_file`
  `{path,label}` channel command — apply a real proposed segmentation FILE as a committed edit (audit
  captured, actor-tagged). The plain-image mask walks in lockstep with the RLE update iterator over the
  grid overlap (mirrors `UpdateSegmentationWithBinarySegmentation`); reads the NIfTI with a plain
  `itk::ImageFileReader` (LabelImageType is RLE, so it can't be read directly).
- `itksnap-mcp` `main` **`9909663`** (pushed): `channel.py` (`SnapChannel` stdlib socket client),
  `server.py` MCP tools `propose`/`apply`/`read_audit`/`set_actor`/`list_models` + reusable helpers
  (`propose_segmentation`/`proposal_summary`/`write_label_mask`), and `demo/run_p2.py` (scripted driver).

**Verified — the whole chain, live on the RTX 2080:** started the DLS server (`itksnap_dls`, port 8911,
cuda), extracted frame 0 of a BAV cardiac CTA (`img4d_CT_bavcta028_baseline_rs50` → 256×256×181, 0.93 mm,
`/tmp/ct3d_bavcta028.nii.gz`), loaded it in headless ITK-SNAP with `--agent-listen`, and ran
`demo/run_p2.py`:
- **propose** (TotalSegmentator fast) → **48 anatomically-correct thoracic structures**: heart (867,916
  vox), aorta, all lung lobes, esophagus/trachea, vertebrae T3–T12, SVC/IVC, atrial appendage, ribs,
  sternum, costal cartilages, liver/spleen/stomach.
- **apply** (largest = `lung_upper_lobe_left`, 1,169,665 vox → ITK-SNAP label 1) → audit
  `{actor:"agent", changed_voxels:1169665, bbox:[84,2,0]-[247,189,180], before:{0:…}, after:{1:…},
  op:"Agent apply (proposal)"}`. `read_audit` returns the same. **exit 0.**
- Also verified independently: `channel.py` drove `apply_seg_file(MRIcrop-seg)` → 55893 vox; the C++
  `apply_seg_file` smoke on MRIcrop-seg. `IRISApplicationTest` + `SegmentationAuditRecordTest` pass.

**Broke / surprised:**
- The local body CTs are **4D cardiac CTA** (`img4d…`, 20 phases); TotalSegmentator needs 3D. Extract
  frame 0 with `sitk.Extract(im4, size_with_0_in_dim3, [0,0,0,0])`.
- **DLS scalar upload drops geometry** (identity) — as noted. `write_label_mask` restores it via
  `sitk.GetImageFromArray(mask_zyx).CopyInformation(source_ct)` so the mask aligns with the CT loaded
  in ITK-SNAP (index-aligned, same grid). Worked cleanly here.
- Kill the long-running DLS server by **port** (`lsof -ti:8911 | xargs kill`), never `pkill -f itksnap_dls`
  (self-matches the tool shell). Same lesson as `pkill -f "ninja ITK-SNAP"` last session.

**Decisions (why):** `apply` extracts ONE proposed structure (largest by default) and applies it under a
single ITK-SNAP label — matches the demo beat ("agent proposes a structure, human corrects it") and keeps
the audit before/after histograms clean. Read the mask into a *plain* image (not RLE) so a stock
`itk::ImageFileReader` works; only the target seg is RLE (behind the update iterator).

## 2026-07-18 (session 2) — P2 loop CLOSED: real edit → audit over the live channel

**Attempted:** the next-session goal — demonstrate the audit record end-to-end with a *real*
committing edit driven over the `--agent-listen` socket (the P2 "commit() returns the audit record"
beat). Landed.

**Landed (commit hash):** `itksnap` `sprint/caimi` **`f1743f04`** (local; **not pushed yet**).
- `IRISApplication::PaintRegionWithLabel(region, label, undoTitle)` — paints a labeled axis-aligned
  voxel region through the normal `SegmentationUpdateIterator → Finalize → commit` path (so the audit
  record is captured and `SegmentationChangeEvent` fires); honors the armed actor; `PAINT_OVER_ALL`.
- `main.cxx` `--agent-listen`: **`apply_box`** `{x0,y0,z0,x1,y1,z1,label}` command → calls it and
  returns the resulting audit record inline (null if nothing committed).

**Verified live (headless Xvfb, real Unix socket), exact values:**
- `set_actor agent` → `apply_box (10,10,5)-(19,19,9) label 5` → `get_audit` returns
  `{actor:"agent", changed_voxels:500, bbox:[10,10,5]-[19,19,9], before:{0:500}, after:{5:500},
  op:"Agent apply (box)", timestamp}`. 500 = 10×10×5. ✓
- A **second, unarmed** `apply_box (30,30,5)-(34,34,7) label 6` → `{actor:"human", changed_voxels:75}`
  (75 = 5×5×3) — proving **consume-on-commit + auto-reset** over the socket (the agent tag was consumed
  by the first commit). ✓
- `IRISApplicationTest` + `SegmentationAuditRecordTest` still pass (ctest); ITK-SNAP builds clean.

**Broke / surprised (process, not code):**
- **`nohup … & ` fires a FALSE "completed" instantly** — the launcher returns immediately while `ninja`
  keeps building detached, so several smoke runs hit a not-yet-relinked binary (`apply_box` = "unknown
  cmd"). Diagnosed via the ITK-SNAP binary mtime not advancing. **Use foreground builds** (or the Bash
  tool's native background that tracks real completion), and confirm the binary relinked before smoke-testing.
- **`pkill -f "ninja ITK-SNAP"` self-matched the tool shell** (its own command line contains the pattern)
  → SIGKILL, exit 1/no output — same class as the `pkill ITK-SNAP` trap. Kill by exact name
  (`pgrep -x ninja` → `kill <pid>`) or by PID; never `pkill -f` a string your own command contains.

**Decisions (why):** started with a geometric `apply_box` (not a full-volume/file apply) because it
closes the loop with zero image-serialization/geometry-matching and is deterministic + headlessly
testable — exactly what the next-session prompt suggested ("start simple — a small box"). It reuses the
tested commit path, so it de-risks the richer "apply a real proposed segmentation" (W3) without new
serialization code. Added an `n==0 → null audit` guard so the response never reports a stale record.

## 2026-07-18 — Audit record (P2 core) built, reviewed, verified

**Attempted:** Build W2 — the segmentation **audit record**, the last net-new piece the
guaranteed P2 "audited callable" demo depends on. Landed complete.

**Landed (commit hash):** `itksnap` `sprint/caimi` **`560dcd2f`** (local; **not pushed yet**).
- New Qt-free `Logic/Framework/SegmentationAuditRecord.{h,cxx}`: value type + hand-rolled
  `ToJSON()` + `BuildFromDeltas()`. Record = `{op, timestamp (ISO-8601 UTC), actor(agent|human),
  changed_voxels, rle_count, time_point, bbox{min,max}, before_counts, after_counts}`.
- `UndoDataManagerCommit::GetName()` getter (the plan's explicit ask; was `protected`, no getter)
  + `UndoDataManager::GetLastCommit()`.
- `LabelImageWrapper`: capture the record in `StoreUndoPoint` (the single commit chokepoint);
  actor **consume-on-commit** with throwaway `"Temporary undo point"` skipped; audit log bounded
  (ring, 4096) + cleared with undo history; last record invalidated on `Undo()`.
- `IRISApplication::SetNextSegmentationCommitActor` (returns bool) / `GetLastSegmentationAuditRecordJSON`.
- `main.cxx` `--agent-listen` channel: `get_audit` + `set_actor` (input-validated) commands.
- `Testing/Logic/SegmentationAuditRecordTest.cxx` — L1 test, links `itksnaplogic` alone.

**Key design decision (why):** the rich fields (bbox, before/after histograms) are **reconstructed
at commit time by walking the committed RLE delta against the current post-edit image**
(`old = new − delta`, modular `LabelType` arithmetic — exactly how `Undo()` recovers prior state).
This puts capture in the ONE chokepoint (`LabelImageWrapper::StoreUndoPoint`) every edit path funnels
through, so **zero changes** to the ~11 `SegmentationUpdateIterator`/Paint call sites, and it handles
multi-delta paintbrush strokes for free.

**Verified:**
- L1 `SegmentationAuditRecordTest` + existing `IRISApplicationTest` **pass** (ctest, 0.08 s). The L1
  test proves reconstruction is exact on a plain image, **the production RLE label image** (confirms
  `ImageRegionConstIteratorWithIndex` raster order matches delta encoding), non-zero before-labels,
  multi-delta accumulation, **overlapping same-voxel deltas counted once**, and serializer escaping.
- ITK-SNAP builds clean (exit 0).
- Headless (Xvfb) channel smoke: `ping`→pong, `get_audit`→null (no edit), `set_actor agent`→ok,
  `set_actor bogus`→`ok:false "unknown actor"`. Round-trips over the Unix socket, no crash.

**Adversarial review (code-reviewer agent, given only the requirement) + fixes.** It found real bugs
in the `actor` field; all fixed and re-verified: (1) actor reset was decoupled from commit creation →
switched to consume-on-commit + skip `"Temporary undo point"`; (2) stale record after undo →
invalidate on `Undo()`; (3) unbounded audit log → bounded + cleared with undo history; (4) softened an
over-strong "exact for every path" comment to the actual precondition; (5) added `set_actor` validation.

**Broke / surprised:**
- **Multi-delta commits.** Paintbrush stages *several* deltas per commit (drag segments) then one
  `StoreUndoPoint`; reconstruction had to walk all deltas in the commit, not one iterator's Finalize.
  The reconstruct-from-delta-vs-image approach handles this cleanly.
- **`ninja --target A B` skipped relinking ITK-SNAP** once (batched build stopped at the model lib;
  binary mtime gave it away) — always confirm the final target actually relinked before smoke-testing.
- Making `PaintBox` a template broke `SmartPointer→T*` deduction in the test (use `.GetPointer()`).

**Known residuals (not blocking P2; see NEXT_SESSION_PROMPT traps):** actor "arm" model leaks if an
agent arms then triggers a genuine no-op (documented contract: arm immediately before a committing op);
`get_audit` not reconciled with `Redo()` (only `Undo` invalidates); one extra O(N) pass on whole-image
commits; a real GUI edit → non-null audit over the socket still needs a paint/apply channel command (W4).

## 2026-07-18 — Session close / handoff

**Attempted:** stand up the CAIMI sprint end-to-end — plan it, execute Day 1 (env + both go/no-go
gates), and build the Gate-2 live command channel. All landed.

**Landed (commit hashes):**
- Planning: `docs/sprint_caimi.md` (7-day plan), `docs/spike_live_channel.md`, rewritten
  `NEXT_SESSION_PROMPT.md`. Wrapper `main`: `b2ee0f5` (sprint docs), `9804b2a` (itksnap-mcp submodule +
  reference docs), `ae72efb` (Day-1 results), `86c68c4` (Gate-2 pointer+docs), `68cffcc` (agent_send bump).
- `itksnap-mcp` (new public repo, submodule tracking `main`): `53f8dbd` scaffold (thin DLS client,
  confidence gate, MCP skeleton, `demo/smoke_totalseg.py`), `46ea911` (`demo/agent_send.py`). Pushed.
- `itksnap` `sprint/caimi`: `d9f2329f` — `--agent-listen` QLocalServer live command channel. Pushed.
- Env (this RTX 2080 box, base conda): `TotalSegmentator` installed + `itksnap-dls` editable on
  `feature/agentic-api`. torch 2.3.1+cu121 CUDA OK.
- **Gate 1 PASS** — TotalSegmentator fast mode end-to-end, 12.9 s, 5 correct thoracic labels.
- **Gate 2 PASS** — external socket client moved the live crosshair (`set_cursor`), no `--test` scaffold.

**Broke / surprised:**
- `conda create --clone base` failed (base has pip-only pkgs + unclonable root pkgs). Base env already
  had the whole stack, so used it directly + `pip install -e itksnap-dls --no-deps`.
- **AF_UNIX `sun_path` ~108-char limit:** `QLocalServer::listen` gave "Name error" on the long
  scratchpad socket path; a short `/tmp/snap-agent.sock` fixed it.
- `pkill -f "ITK-SNAP"` self-matched the tool shell (exit 144) and swept a few stale build-waiter loops.
  Use specific patterns / `setsid`.
- `nnInteractive 1.0.1` requires torch≥2.6 (we have 2.3.1) — TotalSegmentator unaffected; interactive
  nnInteractive deferred (flagship uses human paintbrush).
- DLS scalar `upload_raw` drops spacing/origin/direction (unlike the 4D path) → auto-seg runs on
  identity geometry. Fine for gates; must thread geometry through for anatomically faithful demo output.

**Decisions (why):** use the base conda env (already complete, saves a torch re-download); short socket
path convention; `itksnap-dls` submodule pointer intentionally NOT recorded in the wrapper (wrapper
tracks its `main`; check out `feature/agentic-api` manually); `itksnap-mcp` license still TBD (MIT vs
GPL-3.0); next goal = the audit record (P2 core, guaranteed floor). Both flagship blockers now cleared.

## 2026-07-18 — Gate 2 empirically CLOSED (live command channel works)

Built the live-channel prototype: `itksnap` commit **`d9f2329f`** (`sprint/caimi`, pushed) adds a
`--agent-listen <socket>` `QLocalServer` in `main.cxx`, created before `app.exec()` and dispatching
newline-delimited JSON-RPC on the GUI thread. Empirically verified headless (Xvfb): an external Python
client over a Unix socket ran `ping`→pong and moved the live crosshair via `set_cursor` (61,50,15 →
60,50,15), confirmed by `get_cursor` — **no `--test` scaffold**. This closes the sprint's hardest gate
(plan §6.2) and **unblocks the P1 live-handoff flagship**. Prototype commands: ping/get_cursor/set_cursor
(voxel coords via `IRISApplication::Set/GetCursorPosition`). Gotcha: AF_UNIX path limit ~108 chars → use
a short socket path. Qt6::Network links transitively (no CMake change). Details in
`docs/spike_live_channel.md`. Next: extract `SNAPTestQt` primitives into a shared helper; add
trigger/click/get_state/screenshot; wire the MCP `live.*` tools.

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
