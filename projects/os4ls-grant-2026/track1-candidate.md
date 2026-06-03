# OS4LS Track 1 (candidate) — ITK-SNAP: the Human-in-the-Loop Surface for Agentic Imaging

**Status:** chosen candidate after PI review. Scope cut to **two aims** — Aim 1
(human-in-the-loop core) + Aim 2 (remote data access + open-format interoperability).
*Cut from earlier drafts:* the AI-model-serving aim (the infrastructure already exists in
`itksnap-dls`, which this proposal leverages rather than re-funds) and the dedicated
interoperability-bridge aim (its in-scope part — open-format/DICOM-SEG interchange — is
folded into Aim 2; the FEBio/biomechanics mesh bridge is dropped).
**Track 1 = Domain-Specific Tools, up to $250,000 over 2 years** ($125K/yr max, ≤10%
indirects). A detailed budget is not required at LOI stage. (Track 2 ecosystem variant:
`track2-01.md`.)

---

## One-line pitch

Make ITK-SNAP — one of the most widely adopted interactive medical-image segmentation
tools — the **programmable human-in-the-loop surface for agentic imaging workflows**: the
place where AI **proposes** segmentations and an expert **disposes** (verifies, corrects,
and feeds judgment back), all as callable, composable pipeline steps — plus remote-data
access and open-format interoperability so those workflows reach data wherever it lives.
The "propose" side already exists (the shipped `itksnap-dls` model server); this proposal
builds the *human-in-the-loop layer* that's missing.

> **Core thesis.** MONAI and Hugging Face already make *models* programmable, and our own
> `itksnap-dls` already serves models into ITK-SNAP; what agentic medical-imaging pipelines
> still lack is a way to bring *expert human judgment* in. ITK-SNAP's irreplaceable value is
> the expert at the screen making spatial judgments — so the goal is not "let agents run
> segmentation" (the ecosystem already does that) but **make expert verification,
> correction, and interaction-capture a first-class, orchestrable step** in an
> otherwise-automated loop. *Model proposes, human disposes.*

## Why Track 1 (and why this scope is right)

- Single mature, widely-cited project (ITK-SNAP) with a working AI-serving preliminary
  (`itksnap-dls`) → fits Track 1's "domain-specific tool with demonstrated adoption."
- **Two tightly-coupled aims around one composable surface**, not parallel mini-projects:
  the data layer (Aim 2) feeds the human-in-the-loop core (Aim 1), and both reuse the same
  API + open formats. Interoperability rides on the data layer (open formats), not a
  separate bridge.
- Deliberately **excludes** the GUI rewrite (RFA out-of-scope: "AI-assisted rewrite of a
  legacy tool"), new-model development, new model-serving work (already shipped), and
  data-hosting infrastructure.

## Project in scope

- **ITK-SNAP** (`github.com/pyushkevich/itksnap`) — interactive 3D segmentation; core.

Builds on / integrates these existing, working components (dependencies, not funded line
items): **`itksnap-dls`** (shipped REST model server — provides the "propose" side),
`picsl-greedy` / `greedy_python` (registration Python bindings), **SegFlow4D** (applicant's
4D propagation tool), **FireANTs** (GPU registration backend), MONAI, Hugging Face.

> **PI / buy-in:** PIs are core maintainers of the ITK-SNAP project; all work aligns with
> the project roadmap (AI integration, remote data, scripting). `itksnap-dls`, greedy, and
> SegFlow4D share the same maintainer circle.

---

## Aims

### Aim 1 — Composable human-in-the-loop core: headless API + Python wrapper + agent endpoint
*The connective tissue, and the RFA's #1 priority (agentic/composable workflows). The
distinctive value is not headless inference (MONAI/HF and our own `itksnap-dls` do that) but
making **expert verification, correction, and interaction-capture** an orchestrable pipeline
step — "model proposes, human disposes."*

- **1.1 Headless, scriptable ITK-SNAP core API** over the toolkit-independent layer
  (workspace I/O, image/label ops, segmentation) — no GUI dependency. Builds on the existing
  `Logic/WorkspaceAPI/`.
- **1.2 Python wrapper** (pip-installable) + an **agent-facing endpoint** (MCP/tool-style)
  so LLM agents and data pipelines can call ITK-SNAP as a tool. Shipped as a **distributable
  local (stdio) MCP server** the agent client launches on demand — **no indefinite hosting
  obligation, no per-user cost**; an optional remote (HTTP) mode covers cloud/multi-user.
  Keeps the deliverable as *software*, not hosted infrastructure (good for the RFA's scope +
  sustainability criteria).
- **1.3 Human-in-the-loop primitives** *(the differentiating capability).* Expose the human
  checkpoint as callable operations the agent orchestrates:
  - **Review/correction as a step** — `request_review(image, segmentation) → {corrected
    segmentation, decision, provenance}`: the pipeline pauses, an expert inspects/fixes in
    ITK-SNAP, structured results flow back.
  - **Escalation/triage** — agents route only uncertain/low-confidence cases to a human
    ("review these 12 of 200").
  - **Interaction capture** — expert clicks, scribbles, contours, edits, and accept/reject
    decisions captured as machine-consumable labels, prompts, and preference signals
    (something MONAI/HF have no equivalent for), with provenance/audit logging.
  - Together these enable a **human-in-the-loop data engine** for active learning: candidates
    come from the existing `itksnap-dls` models and SegFlow4D propagation; the human curates
    them.
- **1.4 Unified registration + 4D propagation surface** —
  the same Python/agent surface exposes:
  - **registration** across **greedy (CPU/C++)** and **FireANTs (GPU/PyTorch)** behind a
    backend-agnostic interface (reusing SegFlow4D's proven pluggable handler-factory pattern),
    and
  - **4D/longitudinal propagation** via **SegFlow4D**: propagate a reference-frame
    segmentation (and surface meshes) across all frames of a 4D image — exposed from inside
    ITK-SNAP and via the agent endpoint. The real *within-subject* longitudinal capability
    (e.g. ARIA monitoring, training-data generation), registration-based and low-risk.
- **1.5 Scripted behavioral-regression harness** (`--test`) pinning API/GUI behavior — the
  progress-tracking/validation mechanism the RFA scores, and the fast verification loop that
  makes agent-assisted development safe (see "Achievability").

### Aim 2 — Remote data access + open-format interoperability
*Serves the "data-intensive research" priority; the soundest, lowest-risk plumbing — and the
layer through which ITK-SNAP interoperates with other tools (via open formats, not bespoke
connectors).*

- **2.1 Pluggable backend interface** between an explorer panel and backend plugins.
- **2.2 Initial backends** — local filesystem, remote Linux (SSH), Flywheel (REST/SDK over
  SSL); framework for community plugins (e.g. XNAT).
- **2.3 DICOM/BIDS-aware organization** — auto-detect series and BIDS structure; metadata
  display + search; partial/range reads for large remote files where the format allows.
- **2.4 Remote-aware workspaces** — workspaces reference remote images and can be
  edited/saved without pulling full image data locally. Credentials via OS keychain.
- **2.5 Open-format interoperability (interchange)** — read/write **DICOM-SEG** preserving
  **label semantics** (names, colors, hierarchy, anatomical coding), so segmentations move
  losslessly to/from other tools (e.g. 3D Slicer). This makes ITK-SNAP the human-in-the-loop
  checkpoint inside other pipelines. *Principle: interoperate via open standards, not a
  pairwise connector zoo.*

---

## Architecture — a constellation of composable MCP endpoints

Two design clarifications a reviewer (or PI) will ask about:

**1. ITK-SNAP is not a pass-through to `itksnap-dls`.** `itksnap-dls` is a model-*inference*
engine (image + prompts → mask); for *pure inference* an agent can call it directly — and
should. The ITK-SNAP API sits a layer above: workspaces, label semantics, editing,
registration, 4D propagation, open-format I/O, and the human-in-the-loop primitives. It
*uses* the existing model server for the inference step and orchestrates everything around
it. MCP can live at **both layers**: a thin inference endpoint over the (already-built)
server, and the domain/human MCP over ITK-SNAP that calls it.

**2. We intend more than one MCP — a constellation over the ecosystem.** The same
lightweight wrapping pattern from Aim 1.2 is designed to expose each mature PICSL/ecosystem
tool as its own composable MCP endpoint, with **ITK-SNAP as the human-in-the-loop hub** that
composes them into pipelines:

| Endpoint | MCP exposes | Track 1 status |
|---|---|---|
| **ITK-SNAP** | workspaces, labels, editing, `request_review` (human hub) | committed (Aim 1) |
| **itksnap-dls** | model inference | **existing** — leveraged, not re-funded |
| **greedy** | affine / deformable registration | low-cost demo (picsl-greedy already Python; Aim 1.4) |
| **SegFlow4D** | 4D segmentation + mesh propagation | low-cost demo (already Python; Aim 1.4) |
| **Convert3D / c3d** | image processing, label algebra, format conversion | ecosystem roadmap / Track 2 |
| **ConvertMesh** | mesh conversion / processing | ecosystem roadmap / Track 2 |
| **cmrep** | continuous medial representation / shape modeling | ecosystem roadmap / Track 2 |

**Scope discipline:** Track 1 commits to the **ITK-SNAP endpoint and the shared wrapping
pattern**; `itksnap-dls` already exists; greedy and SegFlow4D are near-free demonstrations of
the pattern (they already ship Python interfaces, via Aim 1.4); c3d / ConvertMesh / cmrep are
the explicit *ecosystem roadmap* (Track 2 or community contributions). We do **not** promise
wrapping the whole constellation in Track 1. The point is the architecture: specialized,
GUI-free tools become composable MCP endpoints that agents chain into pipelines, with
ITK-SNAP supplying the human checkpoint — squarely the RFA's "composable in AI-driven
pipelines" priority.

---

## Illustrative use cases (what success looks like)

Concrete scenarios that exercise the aims and double as use-case-driven success criteria.

### UC-1 — Cohort segmentation with human QC *(the flagship loop)*
A neuroimaging postdoc tells an agent: *"segment the hippocampus in these 200 T1 MRIs and
flag any that look wrong."* The agent runs an automatic model via the existing `itksnap-dls`,
routes the low-confidence cases to `request_review`, and the expert corrects only those.
**Success:** 200 scans triaged; the human touches ~12 instead of 200; every decision logged.
*Model proposes, human disposes — at cohort scale.*
**Uses:** agent/MCP endpoint (1.2) · automatic inference via existing `itksnap-dls` ·
`request_review` HITL primitive + provenance (1.3) · web viewer/QC handoff.

### UC-2 — Longitudinal monitoring via 4D propagation
A dementia-study analyst segments a structure (or an ARIA lesion) at baseline, then
propagates it across all follow-up timepoints with SegFlow4D; the expert reviews only the
frames where propagation drifted. **Success:** serial timepoints segmented consistently
without re-drawing each one; within-subject reuse, no model retraining.
**Uses:** SegFlow4D 4D propagation (1.4) · greedy/FireANTs backend (1.4) · `request_review`
on drifted frames (1.3) · Python/agent API (1.1–1.2).

### UC-3 — Cloud cohort without local download
A researcher browses a Flywheel project, opens a scan, segments it with a model running on a
remote GPU (existing `itksnap-dls`) — never downloading the full dataset locally — then writes
the result back. **Success:** "remote data + remote inference" feels like working locally;
PHI stays in the archive.
**Uses:** Flywheel backend (2.2) · DICOM/BIDS + partial reads (2.3) · remote-aware workspaces
+ keychain creds (2.4) · remote inference via existing `itksnap-dls`.

### UC-4 — Ground-truth / training-data generation *(the data engine)*
A lab building a labeled dataset runs an automatic model (existing `itksnap-dls`) as a first
pass, corrects in ITK-SNAP, and the corrections are captured as structured training data with
provenance. **Success:** faster, auditable ground-truth creation — exactly the
data-preparation work that underpins downstream model training and evaluation.
**Uses:** existing `itksnap-dls` inference · `request_review` + interaction capture +
provenance (1.3) · Python API batch mode (1.1).

### UC-5 — ITK-SNAP as a tool in an agentic pipeline / notebook
A computational researcher drives ITK-SNAP from Python in a reproducible pipeline, or an
agent in Cursor/Claude Code calls it as an MCP tool ("segment structure X across cohort Y,
pause for my review on outliers"). **Success:** ITK-SNAP is scriptable and composable, with
the human checkpoint built into the automation.
**Uses:** headless API (1.1) · Python wrapper + local stdio MCP server (1.2) · `request_review`
(1.3) · `--test` reproducibility (1.5).

### UC-6 — Cross-tool handoff with 3D Slicer
A lab standardized on 3D Slicer hands segmentations to ITK-SNAP for fast expert editing and
back, via DICOM-SEG, with label names/colors/hierarchy preserved. **Success:** ITK-SNAP
becomes the human-correction step in a Slicer-based pipeline without lossy conversions.
**Uses:** DICOM-SEG open-format interchange + label-semantics preservation (2.5) · headless
API (1.1).

---

### Aim 1 spotlight — the new, harder-to-picture capabilities

Aim 1 (headless API **1.1**, Python wrapper + MCP endpoint **1.2**, human-in-the-loop
primitives **1.3**) is the most novel part, so it's worth making concrete. **Today** ITK-SNAP
is GUI-first with only limited scripting (the `itksnap-wt` workspace CLI, `c3d`); there is no
clean, callable library of ITK-SNAP's *semantics* (workspaces, labels, display policies,
tools), and **no way at all to make a human expert a structured, resumable step in an
automated pipeline.** These use cases show what that unlocks.

#### Aim 1.1 — a scriptable core (no GUI)

**UC-A1 — Reproducible cohort pipeline on the cluster.** A lab runs ITK-SNAP segmentation +
volumetry across an ADNI-scale cohort, fully headless on HPC, as a version-controlled
pipeline step (Snakemake/Nextflow) reproducible from the paper's repo. *Today this means
hand-gluing `c3d`/ITK scripts; the API exposes ITK-SNAP's own operations directly.*
**Uses:** headless API (1.1) · batch mode · regression-tested reproducibility (1.5).

**UC-A2 — Programmatic workspace assembly.** A study coordinator generates hundreds of
pre-configured workspaces (image + overlays + label set + display preferences) so every reader
opens a ready-to-go session — instead of hand-setting each case. *Encodes ITK-SNAP session
semantics, not just pixels.* (A working prototype of exactly this is in `prototype/`.)
**Uses:** headless API for workspace I/O + label/display config (1.1); builds on
`Logic/WorkspaceAPI`.

#### Aim 1.2 — Python wrapper + agent endpoint

**UC-A3 — Notebook-native analysis.** A researcher in Jupyter loads a workspace, queries
per-label volumes, thresholds, runs a model, saves — all in Python, results as
numpy/SimpleITK. ITK-SNAP's labels and display logic become first-class in code. *Like having
ITK-SNAP as an importable library.*
**Uses:** Python wrapper (1.2) over the headless API (1.1).

**UC-A4 — Conversational multi-step task via an agent.** In Claude Code / Cursor: *"open these
30 echo studies, run the valve model, compute annular dimensions, and show me the 5 with the
largest change since last visit."* The agent chains MCP tool calls; the researcher reviews the
shortlist. *Natural-language orchestration of a real multi-step study task (and the cardiac /
valve hook).*
**Uses:** local stdio MCP server (1.2) · inference via existing `itksnap-dls`.

#### Aim 1.3 — Human-in-the-loop primitives *(the differentiator — no equivalent exists today)*

**UC-A5 — Active-learning labeling loop.** While building a training set, an automatic model
proposes *with a confidence signal surfaced by `itksnap-dls`*; the **agent/pipeline** ranks
and routes the lowest-confidence cases to an expert via `request_review`; corrections feed the
next round. *(ITK-SNAP provides the confidence pass-through + the human checkpoint; the
acquisition policy lives in the pipeline.)*
**Uses:** confidence from existing `itksnap-dls` · acquisition policy in the agent/pipeline
(1.1–1.2) · `request_review` + interaction capture (1.3).

**UC-A6 — Auditable two-pass study QC.** A multi-site study needs adjudicated segmentations:
automated first pass → structured human review → **every edit, decision, and reviewer logged
with provenance** for audit/regulatory traceability. *Replaces ad-hoc spreadsheets with a
structured, resumable review step.*
**Uses:** `request_review` + provenance/audit logging (1.3) · headless API batch (1.1).

**UC-A7 — Reader-reliability study as a first-class workflow.** Route the same cases to
multiple expert readers (or one reader over time) through `request_review`, capturing decisions
and edits uniformly to compute inter-/intra-rater reliability — e.g. for valve or
hippocampal-subfield segmentation. *ITK-SNAP becomes the instrument for a reader study.*
**Uses:** `request_review` + standardized interaction capture (1.3) · scripted orchestration
(1.1–1.2).

**UC-A8 — Human escalation in an unattended overnight batch.** An agent processes a large
cohort overnight; uncertain cases are parked as pending review tasks; in the morning the
expert clears the queue and the pipeline resumes. *Mixed-initiative automation that respects
expert time — the loop survives the human being asleep.*
**Uses:** `request_review` as a resumable/queued step (1.3) · agent/MCP orchestration (1.2).

> **Why this matters to convince a skeptic:** 1.1/1.2 turn ITK-SNAP from a GUI app into a
> *library and a tool agents can call*; 1.3 is genuinely new — it makes **expert judgment a
> callable, auditable, resumable pipeline step**, which neither the GUI, the workspace CLI,
> nor the MONAI/HF stack (nor `itksnap-dls` alone) provides. That is the proposal's core
> differentiator.

---

## Why this scope is achievable in Track 1 — the coding-agent multiplier

A ~$250K / 2-year budget funds roughly **1–1.5 FTE of engineering**. With the scope now at
**two aims** — and with model serving already shipped — the plan is comfortably within reach,
amplified by a force multiplier that is both **central to the project's thesis** and **already
in daily use by the team**: modern AI coding agents.

1. **Integration, not invention.** Every aim *wires together mature, existing components*
   rather than building from scratch: `itksnap-dls` (shipped), `greedy_python` / `picsl-greedy`,
   SegFlow4D, FireANTs, the existing `WorkspaceAPI`, libssh/libcurl. Coding agents are at their
   most reliable on exactly this kind of work — glue code, API bindings, wrappers, serialization
   layers, and porting an established pattern across similar modules.
2. **Clean architecture gives agents clear contracts.** ITK-SNAP's strict three-layer
   separation (Logic / GUI-model / Qt) and its property/event system give agents well-bounded
   interfaces to target. The headless API (Aim 1) sharpens these contracts further.
3. **A fast, automated verification loop already exists.** The scripted `--test` harness
   (Aim 1.5) means agent-generated code is gated by tests, not trust — directly answering the
   "but is AI-written code reliable?" concern.
4. **The method is the product (dogfooding).** The proposal delivers an *agent-callable* tool
   (Aim 1); the team builds it **using** coding agents — the project is its own first user, so
   productivity gains and product validation reinforce each other. The strongest possible
   evidence for an "AI-native" claim. (A working `itksnap-wt` MCP prototype + an A/B experiment
   already live in `prototype/`.)
5. **A rising tide over a 2-year horizon.** Coding-agent capability is improving rapidly; the
   plan is sized against **today's** capability, so back-half deliverables get cheaper, not
   more expensive. Treated as upside, not dependency.

**Honest framing for reviewers:** we do not claim agents replace expert engineering — the PIs
and a skilled developer remain the bottleneck for design, review, and validation. We claim that
for an integration-heavy, well-tested, cleanly-architected codebase, coding agents convert a
traditional ~2.5 FTE-year scope into something a focused ~1.5 FTE team can deliver in two years,
with the test harness as the safety net.

### Built-in relief valve (prioritization)

If effort runs over, scope sheds in this order, leaving a coherent deliverable at each step:
Aim 2.5 DICOM-SEG interchange polish → Aim 2 advanced features (Flywheel metadata search,
remote-workspace editing) → Aim 1.4 4D-propagation polish. The **MVP core that must ship**:
headless API + Python wrapper + agent endpoint + human-in-the-loop primitives (Aim 1.1–1.3),
and one remote backend with DICOM/BIDS awareness (Aim 2.1–2.3).

---

## Technical feasibility — grounded in the current codebase

The strongest feasibility argument is architectural: **both aims extend shipped, working
components rather than building new subsystems.** ITK-SNAP's strict three-layer design (a
Qt-free Logic layer, a toolkit-independent GUI-Model layer, a thin Qt layer) means the pieces a
programmable/agentic interface needs already exist and are used in production paths.

### Foundations already in the tree

| Capability we need | Already in the codebase |
|---|---|
| Programmatic workspace ops (I/O, layers, labels, tags, display/contrast, export) | `Logic/WorkspaceAPI/WorkspaceAPI.{h,cxx}` — GUI-independent |
| Proof that headless operation works today | `Utilities/Workspace/WorkspaceTool.cxx` (the shipped `itksnap-wt` CLI) |
| REST + SSH transport | `Logic/WorkspaceAPI/RESTClient.cxx`, `SSHTunnel.cxx` (libcurl + libssh, in production) |
| DL-server client (start local subprocess, connect local/remote/SSH, REST) | `GUI/Model/DeepLearningSegmentationModel.{h,cxx}` |
| Async "submit work → poll status → return result" workflow | `GUI/Model/DistributedSegmentationModel.{h,cxx}` (DSS ticket system: auth, `TicketStatus`, logs) |
| Shipped model-serving server (the "propose" side — leveraged) | `itksnap-dls` (FastAPI REST, session-based, nnInteractive) |
| Undo/redo for segmentation edits | `Logic/Framework/UndoDataManager.{h,txx}` + `IRISApplication` |
| Typed, observable property/event system (no Qt) | `Common/PropertyModel.h`, `SNAPEvents.h` (ITK-event based) |
| Python-binding toolchain & expertise | `greedy_python` / `picsl-greedy` (pybind11), SegFlow4D |
| Scripted regression harness | `Testing/GUI/Qt/SNAPTestQt.{h,cxx}` + `--test/--testdir` in `GUI/Qt/main.cxx` |

### Aim 1.1 — Headless API
- **Technology:** a C++ library target exposing `IRISApplication` (Logic/Framework) + the
  toolkit-independent `GUI/Model` layer + `WorkspaceAPI`.
- **Why feasible now:** the Logic layer has no Qt dependency; the GUI-Model layer is
  essentially Qt-free (**only `DeepLearningSegmentationModel.h` `#include`s Qt — for threading —
  out of ~50 model headers**); the property/event system is ITK-based, so models work without a
  GUI event loop; and `itksnap-wt` already drives WorkspaceAPI headlessly.
- **Net-new:** a documented, stable API *facade* + a headless application context (no Qt/OpenGL)
  + decoupling the one Qt-bound model. Mostly facade + build-path work → **moderate effort, low
  novelty.**

### Aim 1.2 — Python wrapper + MCP endpoint
- **Technology:** pybind11 (identical to `greedy_python`) over the 1.1 facade, shipped as a
  wheel; ITK images ↔ numpy/SimpleITK via ITK's existing Python interop; MCP via the official
  MCP Python SDK over **stdio** (local subprocess).
- **Why feasible now:** the team already builds pybind11 bindings; the local-subprocess-launch +
  REST pattern is already implemented in `DeepLearningSegmentationModel`; the MCP server is a
  thin adapter over the wrapper. **A `prototype/` already wraps `itksnap-wt` as an MCP server.**
- **Net-new:** binding coverage + the MCP tool/resource schema. **Low risk.**

### Aim 1.3 — Human-in-the-loop primitives *(the novel one)*
- **Technology:** a review-task + provenance abstraction layered on the workspace/registry; the
  existing REST/session + **DSS-style async ticket workflow** for the request/await/callback;
  interaction capture from the existing edit/undo stack and annotations; handoff to a live GUI /
  web viewer.
- **Why feasible now — the key point:** `request_review`'s "submit work → await → return a
  structured result" is *architecturally the same async pattern already shipped in*
  `DistributedSegmentationModel` (submit ticket → poll status → return result) — repurposed so
  the "worker" is a **human** instead of a compute provider. `UndoDataManager` + workspace
  provenance supply the auditable edit trail.
- **Net-new:** the review-task abstraction, structured interaction logging, and the bridge from
  headless orchestration to a live editing surface. **Highest novelty — but on proven async +
  edit + provenance machinery, not a green field.**

### Aim 2 — Remote data access + interoperability reuses the same foundations
`RESTClient` + `SSHTunnel` + `WorkspaceAPI::UploadWorkspace` + the DSS ticket system already
implement remote workspaces, SSH, and async jobs. *Net-new:* a Flywheel plugin (libcurl —
already a dependency), BIDS/DICOM scanning, the pluggable backend interface, and **DICOM-SEG
read/write** (via dcmqi/ITK) for open-format interchange.

### Cross-cutting risks & mitigations
- **Headless rendering.** The 2D/3D views use OpenGL2 (`Logic/Slicing`), but the *API* surface
  (I/O, segmentation, measurement, registration, propagation) needs **no GL**. Rendering for the
  viewer is client-side (niivue/WebAssembly) or offscreen — off the API's critical path.
- **One Qt-bound model.** `DeepLearningSegmentationModel` pulls Qt only for *threading*
  (`QtConcurrent`/`QFutureWatcher`). For a clean headless build, swap that for a toolkit-neutral
  async mechanism — small, known scope.
- **Live-GUI vs. headless for `request_review`.** The human step needs a live editing surface;
  the MCP server bridges headless orchestration to it. *Mitigation:* reuse the proven DLS
  "launch/attach a local server/session on demand" pattern for the viewer.
- **Python packaging of ITK/VTK.** Bundling a heavy native stack into a wheel is non-trivial —
  but `greedy_python`/`picsl-greedy` already solved this for the team.

**Net:** the great majority of both aims is extension of shipped components; the genuinely new
surface (the 1.3 human-in-the-loop layer) is bounded and built on existing
async/REST/edit/provenance machinery — which is exactly why it fits a focused two-year effort.

---

## Scope discipline (what we deliberately do NOT promise)

- **No GUI rewrite** (Qt→web/Electron). Out-of-scope for the RFA; the headless API de-risks any
  future UI work regardless.
- **No new model-serving work.** `itksnap-dls` already serves models; we *leverage* it for the
  "propose" side and do not re-fund it.
- **No new models / no benchmark study.**
- **No novel registration-method research.** greedy/FireANTs are integrated as engines.
- **No data hosting / repository infrastructure** (RFA out-of-scope).
- **Interoperability via open formats only.** DICOM-SEG interchange (Aim 2.5) — no FEBio/
  biomechanics mesh bridge, no pairwise per-tool connectors. Other tools integrate against the
  open formats.
- **FireANTs as a dependency only** — an optional GPU backend, not a funded project (custom
  license; using it as a dependency avoids that issue).

## Indicative effort shape (illustrative, ~$250K / 2yr ≈ 1.5 FTE-eng + PI)

| Aim | Traditional est. | With agent multiplier |
|-----|------------------|-----------------------|
| Aim 1 — API + Python wrapper + agent endpoint + HITL primitives + registration/4D surface | ~1.5 FTE-yr | ~0.9 FTE-yr |
| Aim 2 — remote data access (backends, BIDS, workspaces) + DICOM-SEG interchange | ~1.2 FTE-yr | ~0.7 FTE-yr |
| PI design/review/validation, docs/tutorials, community | — | ~0.25 FTE-yr |

≈ 2.7 FTE-yr traditional → **~1.85 FTE-yr with the multiplier** — comfortably within a focused
~1.5 FTE team over 2 years, with the relief valve as margin. (≤10% indirects; detailed budget at
full-application stage.)

## How it scores against the RFA criteria

- **Existing impact:** ITK-SNAP's wide adoption + citations; shipped `itksnap-dls` nnInteractive
  integration → a mature project, not a prototype, not a rewrite.
- **Quality:** clean three-layer architecture; existing CI + scripted test harness; public
  GitHub issues/PRs; roadmap alignment; shared maintainer circle.
- **Feasibility:** two aims, integration-heavy work, automated verification, the agent multiplier,
  and an explicit relief valve → a defensible completion story well inside ~1.5 FTE / 2yr.
- **Value / AI-native:** the differentiator is **programmable expert human judgment** — making
  verification/correction/interaction-capture an orchestrable step ("model proposes, human
  disposes"), which the MONAI/HF/`itksnap-dls` inference stack has no equivalent for, and which
  unlocks human-in-the-loop active learning + auditable training-data generation. Supported by
  the agentic API (RFA priority #1), remote data access + open-format interoperability
  (data-intensive, composable), and registration/4D propagation (real longitudinal reuse). A
  previously-unavailable capability that plays to ITK-SNAP's irreplaceable strength rather than
  competing where the ecosystem is already strong.

---

## Open questions before this is LOI-ready

- Confirm PI maintainer status + roadmap-alignment statement.
- Pick host org / fiscal sponsor (single org receives the Track 1 grant).
- Confirm the Flywheel access path (official SDK vs. direct REST) and a target user.
- Confirm SegFlow4D/FireANTs integration depth that fits Aim 1.4 without scope creep.
- Confirm DICOM-SEG round-trip scope with a 3D Slicer user (gates Aim 2.5).
- ITK-SNAP citation/adoption numbers for the impact case.
