# ITK-SNAP OS4LS Ideas (Recalibrated)

Working ideas for an OS4LS-aligned proposal. Each is reframed away from the
5-year R01 "modernization" pitch and toward what OS4LS actually funds:
**enabling software** for **data-intensive and AI-native / agentic workflows**,
delivered in a **2-year scope** (Track 1 ≤ $250K, or Track 2 ≤ $1M if expanded
across the ITK-SNAP + greedy + c3d ecosystem).

**Core thesis (the through-line for every idea below).** MONAI and Hugging Face already
make *models* programmable; what agentic medical-imaging pipelines lack is a way to bring
*expert human judgment* in. ITK-SNAP's irreplaceable value is the expert at the screen
making spatial judgments — so the goal is **not** "let agents run segmentation" (the
ecosystem does that headlessly), but to make **expert verification, correction, and
interaction-capture a first-class, orchestrable step** in an otherwise-automated loop:
***model proposes, human disposes.*** Programmable expert judgment — not another inference
API — is the differentiating, previously-unavailable capability.

Guardrails from the RFA to keep these in scope:
- Out of scope: "AI-assisted rewrite of a legacy tool" → do **not** lead with a Qt→web rewrite.
- Out of scope: "development of AI/ML models themselves" → ship **software that enables**
  inference/training/data-prep, not new models or performance claims.
- Priority: agentic workflows, composability in AI pipelines, large-scale data,
  hardware acceleration, interoperability.
- Builds on demonstrated adoption (ITK-SNAP is widely cited and used) and on
  working preliminary code (nnInteractive integration, WorkspaceAPI).

---

## 1. Remote data access

**Pitch:** Let researchers find, view, and segment imaging that lives in remote
archives (cloud, Flywheel, XNAT, remote Linux filesystems) as seamlessly as local
files — no manual download/upload round-trips.

**Why it fits OS4LS:** Directly serves the "data-intensive research" priority.
It's enabling infrastructure, not a rewrite, and it unblocks data at the scale
AI pipelines need. Strongest-feasibility piece of the original proposal.

**Deliverables:**
- Pluggable backend interface (common API between explorer and backend plugins).
- Initial plugins: local filesystem, remote Linux (SSH), Flywheel (REST/CURL over SSL).
- Lightweight remote agent for browsing, DICOM/BIDS scanning, and partial/range reads
  on large files; clarify the deployment/trust model (no heavyweight daemon required).
- BIDS- and DICOM-aware organization with metadata display and search.
- Workspaces that reference remote images and can be edited/saved without pulling
  the full image data locally.
- Credentials via OS keychain.

**Notes / open questions:**
- Prefer Flywheel's official SDK over hand-rolled CURL unless there's a concrete reason.
- State which formats support range reads (DICOM yes; whole-file NIfTI often not).

---

## 2. AI model serving

**Pitch:** A model-serving layer (Deep Learning Extensions / DLE) that lets users
run, manage, and serve segmentation models from inside ITK-SNAP — locally, on a
remote GPU, or in the cloud — without coding or environment setup.

**Why it fits OS4LS:** Enabling software for **inference** (explicitly in scope),
supports hardware acceleration, and democratizes access to AI for life-science
researchers who lack local GPUs. Anchored by the already-shipped nnInteractive
integration (real preliminary data → strong feasibility/impact signal).

**Deliverables:**
- DLE Python service: a **FastAPI REST** bridge between ITK-SNAP and Python AI APIs,
  generalizing the existing shipped `itksnap-dls` server (which is already REST). Keep
  REST as the baseline transport — it covers upload, discovery, single-shot inference,
  and session lifecycle, tunnels trivially over the SSH/Colab remote modes, and scales
  without sticky-session machinery. **WebSocket (or SSE) is a future add-on**, introduced
  only when a feature needs server push — i.e. live interaction streaming or GPU-queue
  position/"ready" notifications — layered alongside REST, not a rewrite.
- Substrate on MONAI bundles + Hugging Face (preprocessing/postprocessing already
  described by bundles); model-agnostic wrappers map ITK-SNAP prompts→input and
  output→native ITK-SNAP objects (segmentations, confidence maps).
- **Dynamic model discovery (no hardcoded model list).** The GUI does not ship a
  fixed model list; on connect it queries the server for available models +
  capabilities and renders the options. The "model explorer" panel is just the UI
  over this discovery endpoint. This is the *enabling mechanism* for a dynamically
  curated library — a hardcoded list makes that impossible — and it lets new
  wrappers (see below) appear without a GUI release. Standard capability-discovery
  pattern; define the endpoint as part of the DLE protocol so the GUI, the Python
  wrapper (idea #3), and agents all consume one surface.
- Remote GPU execution via the same remote-agent path as idea #1; start single-user,
  then add allocation/queueing (lean on an existing scheduler — Ray Serve / Triton /
  MONAI Deploy — rather than building one).
- Server-side image caching + partial updates to minimize transfer overhead.

**Agent-assisted contributor toolkit (scaling mechanism):**
The way the model library grows without becoming a maintenance sink. An
**agent-agnostic** toolkit that makes integrating a new model into the DLE a
consistent, low-effort, repeatable operation:
- A machine-readable **DLE wrapper spec/contract** + scaffolding templates so every
  model is integrated the same way (prompt→input, output→object, pre/post-processing).
- A **conformance/validation harness** (CI) that checks a candidate wrapper satisfies
  the contract before merge.
- A **coding-agent front-end** (e.g. a Claude skill + prompt scaffolding, but framed
  as one instantiation of a vendor-neutral pattern) that drives an AI coding tool
  through the integration steps.
- Workflow: users experiment with domain-specific model flavors **locally**; when a
  model is broadly useful, the toolkit produces a **PR** that, once it passes
  conformance, is merged for all ITK-SNAP users.
- Why it fits OS4LS: meta-level agentic priority (agents *extend* the tool), plus the
  community-contribution + interoperability story. It's what makes the serving aim
  self-sustaining and scalable — pitch it as the scaling engine, not a separate aim.

**Notes / open questions:**
- Keep model classes broad (task-specific, foundation/interactive, language-vision)
  but frame as *what the serving layer supports*, not models we develop.
- Keep the contributor toolkit vendor-neutral; a Claude skill is one front-end, not
  the whole deliverable (funders prefer open/agnostic framing).
- Crowdsourced rating/review is low-ROI for a 2-year budget — defer or cut.

---

## 3. ITK-SNAP API for human-in-the-loop agentic workflows

**Pitch:** A headless, scriptable ITK-SNAP API with a Python wrapper and an agent-facing
(MCP-style) endpoint — whose *distinctive* purpose is to make **expert human judgment a
callable pipeline step** (review, correction, interaction-capture: *model proposes, human
disposes*), in addition to driving workspace operations, segmentation, and inference.

**Why it fits OS4LS — and why it's not redundant with MONAI/HF:** This is the RFA's **#1
stated priority** ("endpoints/protocols that unlock open source tools in agentic
workflows" / "make tools composable in AI-driven pipelines"). Crucially, the value is
*not* headless inference — MONAI/nnU-Net/HF already do that better, GUI-free. The
unique, previously-unavailable capability is **programmable expert judgment**: the human
checkpoint that agentic medical-imaging pipelines currently have no way to invoke. Highest
value, and ~80% reachable by exposing the existing `Logic/WorkspaceAPI/` + the DLE service.

**Deliverables:**
- Stable, documented headless API over the toolkit-independent core (no GUI dependency).
- Python wrapper package (pip-installable) covering workspace I/O, image/label ops,
  segmentation, and model inference via the DLE layer.
- **Human-in-the-loop primitives (the differentiator):** review/correction as a callable
  step (`request_review(image, seg) → {corrected seg, decision, provenance}`);
  escalation/triage of uncertain cases; capture of expert clicks/scribbles/edits/decisions
  as machine-consumable labels, prompts, and preference signals (no MONAI/HF equivalent);
  audit/provenance logging. Together: a human-in-the-loop **data engine** for active
  learning + auditable training-data generation.
- Agent-facing protocol layer (MCP/tool endpoints) so LLM agents can call ITK-SNAP as
  a tool in a pipeline. Default = a **distributable local (stdio) MCP server** the agent
  client launches on demand — **no indefinite hosting, no per-user cost, no post-grant
  uptime obligation**; optional remote (HTTP) mode for cloud/multi-user. Keeps it
  *software*, not hosted infrastructure (RFA scope + sustainability).
- Batch/headless mode for large-scale processing and reproducible scripted workflows.
- Examples: scripted dataset curation, agent-driven "segment structure X across cohort Y."

**Notes / open questions:**
- Reuse the existing scriptable surface (WorkspaceAPI, c3d) rather than inventing new.
- This idea also de-risks the (deferred) web-GUI work: a clean headless API is the
  prerequisite either way.

---

## 4. LoRA as an enabling feature (not a model-training study)

**Pitch:** An interactive domain-adaptation capability: users turn their own
segmentation corrections into a parameter-efficient (LoRA) adapter for a model they
already use — no coding, with GUI checkpoint/revert. The deliverable is a **reusable
feature**, not a better model or a benchmark win.

**Why it fits OS4LS — and the scope risk it must avoid:** Training-*enablement* is in
scope; "development of AI/ML models themselves" is out. The original Aim 2B read as a
research bake-off (ΔDice, power analysis, LoRA-vs-finetune-vs-UniverSeg). Recalibrate
so the center of gravity is the **corrections→training-data→adapter→serve pipeline**
(data-prep + training-enablement, both explicitly funded), with only a light
feature-validation — not a method comparison.

**Deliverables:**
- Corrections-to-training-data pipeline: capture user edits server-side, tag by
  workflow/domain, assemble into training examples.
- Model-agnostic adapter loop in DLE / MONAI Label: attach LoRA adapter, fine-tune,
  serve; per-domain/per-user adapters.
- GUI controls to launch, checkpoint, and revert adaptation (mitigates catastrophic
  forgetting / overfitting to a few edits / label noise).
- Light validation that the *feature* improves the user's in-workflow segmentation —
  not a cross-method performance study.

**Notes / open questions:**
- Fix the technical framing inherited from the draft: LoRA is `W = W₀ + BA`
  (frozen full-rank `W₀` + low-rank update `BA`); it *is* training, just
  parameter-efficient — drop "no retraining needed."
- Verify architecture fit: nnInteractive is nnU-Net/CNN-based; standard LoRA targets
  transformer linear layers. Either confirm a clean conv-adapter recipe or target a
  transformer-based interactive model (SAM/MedSAM2-style) for the adapter path.
- Use model-agnostic language ("adapt any compatible model") to stay on the
  enabling-software side of the line.
- **Distinguish two adaptation regimes** (see idea #6): *within-subject / time-series*
  reuse is better served by **registration-based propagation (SegFlow4D)** — no model
  retraining, no catastrophic forgetting, works today. LoRA is for *cross-subject /
  cross-domain* adaptation. Don't conflate them; propagation de-risks the longitudinal
  story and can also *generate the training data* LoRA consumes.

---

## 6. Registration & 4D ecosystem (FireANTs + SegFlow4D)

**What's new:** the repo now includes two more ecosystem members alongside ITK-SNAP /
greedy / c3d:

- **FireANTs** (`github.com/jilei-hao/FireANTs`, fork of `rohitrango/fireants`) — a
  **GPU / PyTorch diffeomorphic registration engine** (Riemannian adaptive optimization,
  fused CUDA ops, batched registration, composable transforms). ~10× faster / ~10× less
  memory than DL and traditional methods. CLI mirrors ANTs.
- **SegFlow4D** (`github.com/jilei-hao/segflow4d`, *your* project) — propagates sparse
  segmentations across **all time points of a 4D image** via deformable registration,
  warping **both label maps and surface meshes**. **Pluggable registration backends**
  (FireANTs GPU / greedy CPU / ANTs) behind a handler-factory abstraction; YAML-config
  driven; pip-installable with a CLI.

### Why this matters for the proposal

1. **Hardware-acceleration priority, satisfied for real.** greedy is CPU/C++; FireANTs is
   GPU/PyTorch-native and composable with the AI stack (torch/MONAI). That directly hits
   the RFA's "scalability and performance improvements, including support for hardware
   acceleration."
2. **A genuine longitudinal/4D capability — lower risk than LoRA.** SegFlow4D already does
   registration-based propagation of segmentations (and meshes) across time. This is the
   real answer to "sequential segmentation of same-domain images" (ARIA monitoring,
   training-data generation) that originally motivated the LoRA aim. Use propagation for
   within-subject/time-series; reserve LoRA for cross-domain. Propagation also *produces
   training data* that can feed the (optional) LoRA pipeline.
3. **A proven pluggable-backend abstraction already exists.** SegFlow4D's
   greedy/ANTs/FireANTs handler factory is evidence the team builds composable,
   backend-agnostic interfaces — strong for the feasibility/quality criteria, and the
   same pattern the DLE model-serving layer uses.
4. **4D mesh warping ↔ biomechanics interop.** SegFlow4D warps surface meshes across
   frames → **time-resolved (4D) meshes** for dynamic biomechanics (e.g. mitral valve over
   the cardiac cycle — already a proposal eval dataset). Strong synergy with the
   segmentation→FEBio mesh bridge (idea 5c).

### Idea: unified, agent-callable registration+propagation surface
- One Python/agent API (idea #3) spanning **registration (greedy CPU + FireANTs GPU),
  segmentation (ITK-SNAP), and 4D propagation (SegFlow4D)** — already partly there via
  `picsl-greedy` / `greedy_python` and SegFlow4D's CLI.
- Expose SegFlow4D propagation **from inside ITK-SNAP** (propagate a reference-frame
  segmentation across a 4D workspace) and via the agent endpoint for batch/pipeline use.
- Backend selection (CPU vs GPU, local vs remote) routed through the same remote-agent /
  GPU-serving path as the DLE (idea #2).

### Caveats / eligibility flags
- **FireANTs license:** it ships a **custom "FireANTs License v1.0 (Modified Apache)."**
  OS4LS excludes "software with custom/restrictive licenses." Before naming FireANTs as a
  *funded project*, confirm the license is OSI-standard (or treat FireANTs as an external
  **dependency / optional backend** rather than a funded line item). The upstream author
  (rohitrango) is external — multi-project Track 2 would need their buy-in.
- **SegFlow4D maturity:** it's new and may lack the "demonstrated adoption" the RFA wants
  of a *headline* project. Safer to position it as an **integration target / deliverable**
  within the mature ITK-SNAP ecosystem than as a project claiming independent traction.

---

## 5. Interoperability with other platforms (Slicer, FEBio, napari, …)

**Why it fits OS4LS:** Interoperability is a named **priority area** ("interoperability
frameworks that make tools composable in AI-driven pipelines") and is the entire premise
of **Track 2** ("shared interoperability, integrations, or common interfaces across a set
of related tools"). The guiding principle: ship **open protocols/formats + one or two
reference integrations**, not unbounded pairwise connectors (standards scale; bespoke
connectors become a maintenance sink).

### 5a. Python/agent API as the universal connector *(highest leverage; = idea #3)*
A headless, scriptable ITK-SNAP becomes a node other platforms drive:
- **3D Slicer** calls ITK-SNAP headless from its Python console / an extension (hand off
  a volume for level-set or AI segmentation; pull the labeled result back into MRML).
- **napari** (Python-native, large bioimaging audience) uses ITK-SNAP as a segmentation/AI
  backend in a pipeline.
- An agent orchestrates Slicer + ITK-SNAP + a solver in one workflow.
- One composable surface, not N pairwise integrations.

### 5b. Standardized segmentation interchange (preserve semantics, not just pixels)
The real friction is lost **label names / colors / hierarchy / anatomical coding**, not
the image. Clean round-trip that preserves label metadata across ITK-SNAP ↔ Slicer
Segmentation nodes, with **DICOM-SEG** as the lingua franca (and SNOMED/FMA coding where
available). Low risk, high daily-workflow value; both tools are already ITK/VTK/NRRD-based.

### 5c. Segmentation → simulation-ready mesh bridge (FEBio / OpenSim) *(novel capability)*
ITK-SNAP today emits label images + marching-cubes surfaces; biomechanics needs
**material-tagged volumetric (tet) meshes**. Bridge: multi-label segmentation → clean
surface → tetrahedral volume mesh (TetGen / CGAL / gmsh) with per-label material tags →
export to **FEBio (`.feb`)** / OpenSim. A *previously-unavailable computational capability*
serving the cardiac / mitral-valve / musculoskeletal audience already in the proposal.
In-house wheelhouse (greedy, c3d, VTK meshing, cm-rep/ConvertMesh mesh work).

### 5d. Shared AI model-serving layer across tools *(= idea #2, opened up)*
Document the DLE discovery + inference protocol so **Slicer/napari can call the same DLE
backend**. One AI inference service, many frontends — AI-native + interoperable at once.

**Track mapping:**
- **Track 1:** lean on 5a (already the spine) + add 5b as a concrete deliverable; mention
  5c/5d as future directions.
- **Track 2:** full interop is the natural home — coordinated multi-project ecosystem
  (ITK-SNAP + greedy + c3d core, bridges to Slicer / FEBio-OpenSim / napari-MONAI). See
  `track2-01.md`.

---

## Out of scope for OS4LS (parked, not lost)

### Agentic framework for Qt→Electron GUI conversion

**Idea:** An AI/agentic toolkit to drive the Qt C++ → Electron conversion — design-
pattern advice, data-transfer guidance, a **visual-feedback tool** (agent renders UI
layout sketches as options the user picks, or tweaks live by resizing / color-picking,
to fix coding agents' lack of visual feedback), and refactor-correctness validation.

**Verdict: drop for OS4LS — pursue separately or pitch to a dev-tools funder.**
- **Double out-of-scope.** The RFA names "AI-assisted rewrite of a legacy tool" as
  out of scope; this not only does that rewrite but builds *generic tooling to do
  rewrites* — the exact thing, amplified.
- **Wrong audience.** A general Qt→Electron framework + UI-sketch tool serves
  *software developers broadly*, not life-science researchers. Track 1 excludes tools
  "primarily serving other domains."

**Worth keeping on the merits (just not here):**
- The **visual-feedback / sketch-and-tweak tool** genuinely attacks the real gap in
  agent-driven UI work (no visual feedback). Strong standalone dev-tools idea with its
  own roadmap.
- **Refactor-correctness across C++→JS is very hard** — no cheap semantic-equivalence
  oracle. The tractable slice is *behavioral* validation via ITK-SNAP's existing
  scripted GUI test harness (`--test`), which is reusable for any modernization.

**Salvage into OS4LS:** attach only the **scripted behavioral-regression harness** to
the API aim (idea #3) — "tests that pin GUI/headless behavior" is defensible. Leave
the conversion framework and sketch tool out.

---

## 7. Web viewer for AI IDE-ecosystem integration (VS Code / Cursor)

**Pitch:** A lightweight, web-based ITK-SNAP **viewer / QC panel** — embeddable as a
**VS Code / Cursor webview extension** — that acts as the *visual layer for agent-driven
segmentation*. The agent does the work via the API/MCP (idea #3); the webview lets the
researcher see and QC results **without leaving the IDE**.

**The workflow it closes:** in Cursor/VS Code a researcher tells the agent "segment these
scans and measure volumes." The agent calls ITK-SNAP over **MCP** (idea #3) and runs
inference via the **DLE** (idea #2). Today the results can't be inspected without leaving
the IDE. A web viewer embedded in the IDE closes the loop: **agent acts → human inspects
→ corrects → re-runs**, all in one place.

**Why this is the *fundable* version (not the full Electron rewrite):**
- **Two things were conflated and must be separated:**
  1. *Agent integration* comes from the **headless API + MCP endpoint** (idea #3), which
     is **toolkit-agnostic**. Agents call tools; they do **not** drive GUIs. You get full
     Cursor/VS Code agent integration whether the GUI is Qt, Electron, or absent — the
     rewrite buys nothing here. Don't pitch "Electron → enables agents"; a technical
     reviewer will see through it.
  2. *IDE-ecosystem GUI reuse* is real but narrow: VS Code/Cursor extensions are **not
     Electron apps** — they render UI via the **Webview API** (sandboxed HTML/JS). What
     transfers from any web frontend is the **React/web view layer**, not the Electron
     shell.
- So the deliverable is a **scoped web viewer** (rendering via **niivue / VTK.js** — see
  the rendering decision in the parked Electron notes), shippable both **standalone in a
  browser** and **as a VS Code/Cursor webview**, driven by the headless API.
- This is a **new AI-native capability** (in-IDE visual companion for agentic imaging),
  *not* "modernization for its own sake" — it sidesteps the RFA's "AI-assisted rewrite of
  a legacy tool" exclusion that sinks the full Qt→Electron rewrite.
- It's small, pairs with and **showcases** ideas #2/#3, and the web view layer is the
  reusable seed for any future web GUI — de-risking the larger modernization without
  committing to it.

**Deliverables:**
- A web viewer component (2D slices + 3D, niivue/VTK.js) that loads images +
  segmentations + confidence maps from the headless API.
- A **VS Code / Cursor webview extension** wrapping it (Cursor is a VS Code fork → same
  extension/webview model).
- Basic QC/edit affordances (toggle labels, scrub slices, accept/reject, trigger a
  re-run via the API/DLE) so the agent→inspect→correct loop is real.

**Scope / caveats:**
- **Not** full GUI parity in the browser — that's the expensive, risky part and is *not
  needed* here. Resist scope creep toward a complete web GUI.
- **Track fit:** keep it **out of the Track 1 core** (the three aims are already full);
  mention as a future direction at most. Better as a **Track 2 deliverable** or a
  fast-follow once the headless API (idea #3) exists.

---

## Track decision

- **Track 1 ($250K / 2yr) — recommended:** a single coherent aim built from ideas
  **#3 + #2** (see scoped plan below). All four ideas in one Track 1 is over budget and
  fails the feasibility test.
- **Track 2 (≤ $1M / 2yr):** all four ideas, expanded across the ITK-SNAP ecosystem
  (greedy, c3d, Convert3D) for shared interoperability. Higher ceiling, but needs a
  credible ~4+ FTE-year staffing plan and a multi-project coordination story.

---

## Recommended Track 1 scope

**Budget reality:** $250K / 2yr ≈ **1–1.5 FTE engineer for two years** (~$125K/yr,
≤10% indirects). The four ideas together are ~3–4 FTE-years — too much. Feasibility
("can it be done within budget and by the personnel?") is a scored criterion, so a
tight, completable scope beats breadth.

### One aim, one narrative

> **Make ITK-SNAP a first-class citizen in AI-driven and agentic imaging workflows.**

The spine is ideas **#3 + #2**, which interlock around **one DLE protocol** consumed by
three clients — the GUI, the Python wrapper, and AI agents. This hits every OS4LS
priority (agentic, composable, AI-native) and rests on demonstrated adoption +
shipped preliminary work (nnInteractive).

### Core deliverables (the committed work)

1. **Headless / scriptable ITK-SNAP core API** over the toolkit-independent layer
   (no GUI dependency) — workspace I/O, image/label ops, segmentation.
2. **Python wrapper** (pip-installable) over that API, plus an **agent-facing endpoint**
   (MCP/tool-style) so LLM agents and pipelines can call ITK-SNAP as a tool.
3. **AI model serving (DLE)** — **FastAPI REST** service on MONAI bundles + Hugging
   Face, model-agnostic wrappers (prompt→input, output→native objects), generalizing
   the shipped `itksnap-dls` (nnInteractive) server. REST baseline; WebSocket/SSE
   deferred to when push is needed (streaming, GPU-queue notifications).
4. **Dynamic model discovery** — no hardcoded model list; the GUI/Python/agents query
   the server for available models + capabilities. One discovery endpoint, three
   consumers.
5. **Agent-assisted contributor toolkit** (vendor-neutral) — DLE wrapper spec +
   scaffolding + CI conformance harness, with a coding-agent front-end (a Claude skill
   as one instantiation). This is the **scaling/sustainability mechanism**: local
   experimentation → PR → merge once conformance passes.

### Thin slice from idea #1 (folded in, not a separate aim)

6. **One remote backend** — the minimum needed to serve **remote-GPU model inference**
   (run the DLE service on a remote host the user reaches via the lightweight SSH
   agent). *Not* the full multi-backend explorer / BIDS / remote-workspace work — that
   stays parked as a distinct future Track 1 application (the RFA permits multiple
   applications for the same project when the work is distinct).

### Stretch goal (clearly labeled, only if budget allows)

7. **LoRA adaptation proof-of-concept** (idea #4) — the corrections→training-data→
   adapter→serve pipeline as a *reusable feature*, with light feature-validation only
   (no method bake-off). Labeled as a stretch so the core aim isn't judged on it; carries
   the most risk (scope line + nnInteractive architecture fit). Better as a Track 2 /
   follow-on headline.

### Salvaged validation (from the parked Qt→Electron idea)

8. **Scripted behavioral-regression harness** using ITK-SNAP's existing `--test`
   framework — pins GUI/headless behavior so the new API + serving paths don't regress.
   Doubles as the "plan for tracking and validating progress" the RFA scores.

### Parked (explicitly not in this application)

- Full remote-archive explorer (multi-backend, BIDS, remote workspaces) → future Track 1.
- Qt→Electron conversion framework + visual-feedback/sketch tool → out of scope for
  OS4LS; separate dev-tools effort.
- LoRA as a headline method study → Track 2 / follow-on.

### Why this passes review

- **Feasibility:** ~2 FTE-years of committed work for ~2 FTE-years of budget, plus one
  labeled stretch. Defensible completion story.
- **Value / AI-native:** the agentic API is the RFA's stated #1 priority; serving +
  discovery + contributor toolkit make it composable and self-sustaining.
- **Impact / preliminary data:** builds on ITK-SNAP's adoption and the shipped
  nnInteractive work — not a prototype, not a rewrite.
- **Sustainability:** the contributor toolkit lets the community grow the model library
  without core-team bottlenecks — directly answers the "future plans for maintaining
  the funded work" criterion.
