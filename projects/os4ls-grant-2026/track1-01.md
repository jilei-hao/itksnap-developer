# OS4LS Track 1 Sketch — ITK-SNAP as an AI-Native, Composable Segmentation Hub

**Status:** draft (companion to `ideas.md`; Track 2 variant in `track2-01.md`).
**Track 1 = Domain-Specific Tools, up to $250,000 over 2 years** ($125K/yr max,
≤10% indirects). A detailed budget is not required at LOI stage.

---

## One-line pitch

Make ITK-SNAP — one of the most widely adopted interactive medical-image segmentation
tools — the **programmable human-in-the-loop surface for agentic imaging workflows**:
the place where AI **proposes** segmentations and an expert **disposes** (verifies,
corrects, and feeds judgment back), all as callable, composable pipeline steps — plus
the model serving and remote-data access that make those workflows practical.

> **Core thesis.** MONAI and Hugging Face already make *models* programmable; agentic
> medical-imaging pipelines lack a way to bring *expert human judgment* in. ITK-SNAP's
> irreplaceable value is the expert at the screen making spatial judgments — so the goal
> is not "let agents run segmentation" (the ecosystem does that headlessly) but **make
> expert verification, correction, and interaction-capture a first-class, orchestrable
> step** in an otherwise-automated loop. *Model proposes, human disposes.*

## Why Track 1 (and why this scope is right)

- Single mature, widely-cited project (ITK-SNAP) with a working AI-serving preliminary
  (`itksnap-dls`) → fits Track 1's "domain-specific tool with demonstrated adoption."
- Three tightly-coupled aims around **one composable surface** — not four parallel
  mini-projects. The aims reinforce each other (the API consumes the serving protocol;
  remote access carries both data and GPU inference).
- Deliberately **excludes** the GUI rewrite (RFA out-of-scope: "AI-assisted rewrite of
  a legacy tool"), new-model development, and data-hosting infrastructure.

## Project in scope

- **ITK-SNAP** (`github.com/pyushkevich/itksnap`) — interactive 3D segmentation; core.

Builds on / integrates these existing, working components (used as dependencies, not
funded line items): `itksnap-dls` (shipped REST AI-serving server), `picsl-greedy` /
`greedy_python` (registration Python bindings), **SegFlow4D** (applicant's 4D
propagation tool), **FireANTs** (GPU registration backend), MONAI, Hugging Face.

> **PI / buy-in:** PI is a core ITK-SNAP maintainer; all work aligns with the project
> roadmap (AI integration, remote data, scripting). `itksnap-dls`, greedy, and SegFlow4D
> share the same maintainer circle.

---

## Aims

### Aim 1 — Composable human-in-the-loop core: headless API + Python wrapper + agent endpoint
*The connective tissue, and the RFA's #1 priority (agentic/composable workflows). The
distinctive value is not headless inference (MONAI/HF do that) but making **expert
verification, correction, and interaction-capture** an orchestrable pipeline step —
"model proposes, human disposes."*

- **1.1 Headless, scriptable ITK-SNAP core API** over the toolkit-independent layer
  (workspace I/O, image/label ops, segmentation) — no GUI dependency. Builds on the
  existing `Logic/WorkspaceAPI/`.
- **1.2 Python wrapper** (pip-installable) + an **agent-facing endpoint** (MCP/tool-style)
  so LLM agents and data pipelines can call ITK-SNAP as a tool. Shipped as a
  **distributable local (stdio) MCP server** the agent client launches on demand — **no
  indefinite hosting obligation, no per-user cost**; an optional remote (HTTP) mode covers
  cloud/multi-user scenarios. Keeps the deliverable as *software*, not hosted
  infrastructure (good for the RFA's scope + sustainability criteria).
- **1.3 Human-in-the-loop primitives** *(the differentiating capability).* Expose the
  human checkpoint as callable operations the agent orchestrates:
  - **Review/correction as a step** — `request_review(image, segmentation) → {corrected
    segmentation, decision, provenance}`: the pipeline pauses, an expert inspects/fixes in
    ITK-SNAP, structured results flow back.
  - **Escalation/triage** — agents route only uncertain/low-confidence cases to a human
    ("review these 12 of 200").
  - **Interaction capture** — expert clicks, scribbles, contours, edits, and accept/reject
    decisions captured as machine-consumable labels, prompts, and preference signals
    (something MONAI/HF have no equivalent for), with provenance/audit logging.
  - Together these enable a **human-in-the-loop data engine** feeding active learning and
    the adaptation work (Aim 2 / SegFlow4D propagation generate the candidates; the human
    curates them).
- **1.4 Unified registration + 4D propagation surface** *(folds in `ideas.md` #6)* —
  the same Python/agent surface exposes:
  - **registration** across **greedy (CPU/C++)** and **FireANTs (GPU/PyTorch)** behind a
    backend-agnostic interface (reusing SegFlow4D's proven pluggable handler-factory
    pattern), and
  - **4D/longitudinal propagation** via **SegFlow4D**: propagate a reference-frame
    segmentation (and surface meshes) across all frames of a 4D image — exposed from
    inside ITK-SNAP and via the agent endpoint. This is the real *within-subject*
    longitudinal capability (e.g. ARIA monitoring, training-data generation),
    registration-based and low-risk.
- **1.5 Scripted behavioral-regression harness** (`--test`) pinning API/GUI behavior —
  the progress-tracking/validation mechanism the RFA scores, and the fast verification
  loop that makes agent-assisted development safe (see "Achievability").

### Aim 2 — AI model serving (generalize `itksnap-dls` → DLE)
*Enabling software for inference (in scope); anchored on shipped, working code.*

- **2.1 Generalize the serving layer** — evolve the existing **FastAPI REST**
  `itksnap-dls` server (today: one hardcoded nnInteractive model) into a **model-agnostic
  serving layer** on MONAI bundles + Hugging Face, with wrappers mapping ITK-SNAP
  prompts→model input and model output→native ITK-SNAP objects. REST stays the baseline
  transport; WebSocket/SSE deferred to when server-push is needed (streaming, queue
  notifications).
- **2.2 Dynamic model discovery (no hardcoded list)** — clients (GUI, Python wrapper,
  agents) query the server for available models + capabilities. The "model explorer"
  panel is the UI over this endpoint; new wrappers appear without a GUI release.
- **2.3 Agent-assisted contributor toolkit** (vendor-neutral) — a machine-readable
  wrapper contract + scaffolding + CI conformance harness, with a coding-agent front-end
  (a Claude skill as one instance). Local experimentation → PR → merge on conformance.
  The **scaling/sustainability engine** for the model library.
- **2.4 Remote/cloud GPU execution** — run the serving layer on a remote GPU (the SSH
  path already works in `itksnap-dls` for local/Colab/SSH); single-user first, with a
  path to allocation/queueing via an existing scheduler.

### Aim 3 — Remote data access
*Serves the "data-intensive research" priority; the soundest, lowest-risk plumbing.*

- **3.1 Pluggable backend interface** between an explorer panel and backend plugins.
- **3.2 Initial backends** — local filesystem, remote Linux (SSH), Flywheel (REST/SDK
  over SSL); framework for community plugins (e.g. XNAT).
- **3.3 DICOM/BIDS-aware organization** — auto-detect series and BIDS structure; metadata
  display + search; partial/range reads for large remote files where the format allows.
- **3.4 Remote-aware workspaces** — workspaces reference remote images and can be
  edited/saved without pulling full image data locally. Credentials via OS keychain.

---

## Why this scope is achievable in Track 1 — the coding-agent multiplier

A ~$250K / 2-year budget funds roughly **1–1.5 FTE of engineering**. Three aims would be
ambitious at that level under *traditional* development economics. This proposal is
credible because of a force multiplier that is both **central to the project's thesis**
and **already in daily use by the team**: modern AI coding agents. Five concrete reasons,
not hand-waving:

1. **Integration, not invention.** Every aim *wires together mature, existing
   components* rather than building from scratch: `itksnap-dls` (shipped), `greedy_python`
   / `picsl-greedy`, SegFlow4D, FireANTs, the existing `WorkspaceAPI`, MONAI, Hugging
   Face, libssh/libcurl. Coding agents are at their most reliable on exactly this kind of
   work — glue code, API bindings, wrappers, serialization layers, and porting an
   established pattern across similar modules.

2. **Clean architecture gives agents clear contracts.** ITK-SNAP's strict three-layer
   separation (Logic / GUI-model / Qt) and its property/event system give agents
   well-bounded interfaces to target, which is where they are most productive and least
   error-prone. The headless API (Aim 1) sharpens these contracts further.

3. **A fast, automated verification loop already exists.** The scripted `--test` GUI/CLI
   harness (Aim 1.5) + CI conformance tests (Aim 2.3) mean agent-generated code is gated
   by tests, not trust. Tight generate→test→correct loops are precisely what makes
   agent-assisted development fast *and* safe, and directly answer the reviewer's natural
   "but is AI-written code reliable?" concern.

4. **The method is the product (dogfooding).** The proposal delivers an
   *agent-callable* tool (Aim 1) and an *agent-assisted contribution toolkit* (Aim 2.3).
   The team builds these features **using** coding agents — the project is its own first
   user, so productivity gains and product validation reinforce each other. This is the
   most credible possible evidence for an "AI-native" claim.

5. **A rising tide over a 2-year horizon.** Coding-agent capability (context length,
   multi-file refactoring, tool use, agentic SDKs) is improving rapidly. The plan is
   sized against **today's** demonstrated capability; capability at month 24 will exceed
   month 0, making the back-half deliverables progressively cheaper rather than more
   expensive. We treat this as upside, not as a dependency.

**Honest framing for reviewers:** we do not claim agents replace expert engineering — the
PI and a skilled developer remain the bottleneck for design, review, and validation. We
claim that for an integration-heavy, well-tested, cleanly-architected codebase, coding
agents convert roughly a traditional ~2.5–3 FTE-year scope into something a focused
~1.5 FTE team can deliver in two years, with the test harness as the safety net.

### Built-in relief valve (prioritization)

If effort runs over, scope sheds in this order, leaving a coherent deliverable at each
step: Aim 3 advanced features (Flywheel search, remote workspaces) → Aim 2.4 multi-user
queueing → Aim 1.4 4D propagation polish. The **MVP core that must ship**: headless API +
Python wrapper + agent endpoint + human-in-the-loop primitives (Aim 1.1–1.3), generalized
REST serving + discovery (Aim 2.1–2.2), and one remote backend (Aim 3.1–3.2).

---

## Scope discipline (what we deliberately do NOT promise)

- **No GUI rewrite** (Qt→web/Electron). Out-of-scope for the RFA; the headless API
  de-risks any future UI work regardless.
- **No new models / no benchmark study.** Aim 2 ships serving + adaptation *software*.
- **No novel registration-method research.** greedy/FireANTs are integrated as engines.
- **No data hosting / repository infrastructure** (RFA out-of-scope).
- **FireANTs as a dependency only** — used as an optional GPU backend, not a funded
  project (it carries a custom license; using it as a dependency avoids that issue).

## Indicative effort shape (illustrative, ~$250K / 2yr ≈ 1.5 FTE-eng + PI)

| Aim | Traditional est. | With agent multiplier |
|-----|------------------|-----------------------|
| Aim 1 — API + Python wrapper + agent endpoint + human-in-the-loop primitives + registration/4D surface | ~1.5 FTE-yr | ~0.9 FTE-yr |
| Aim 2 — generalize DLE + discovery + contributor toolkit + remote GPU | ~1.25 FTE-yr | ~0.75 FTE-yr |
| Aim 3 — remote data access (backends, BIDS, workspaces) | ~1.0 FTE-yr | ~0.6 FTE-yr |
| PI design/review/validation, docs/tutorials, community | — | ~0.25 FTE-yr |

≈ 3.75 FTE-yr traditional → ~2.5 FTE-yr with the multiplier, deliverable by a focused
~1.5 FTE team over 2 years given the relief valve. (≤10% indirects; detailed budget at
full-application stage.)

## How it scores against the RFA criteria

- **Existing impact:** ITK-SNAP's wide adoption + citations; shipped `itksnap-dls`
  nnInteractive integration → mature project, not a prototype, not a rewrite.
- **Quality:** clean three-layer architecture; existing CI + scripted test harness;
  public GitHub issues/PRs; roadmap alignment; shared maintainer circle.
- **Feasibility:** integration-heavy work + automated verification + the agent multiplier
  + an explicit relief valve → a defensible completion story at ~1.5 FTE / 2yr.
- **Value / AI-native:** the differentiator is **programmable expert human judgment** —
  making verification/correction/interaction-capture an orchestrable step ("model
  proposes, human disposes"), which the MONAI/HF inference stack has no equivalent for and
  which unlocks human-in-the-loop active learning + auditable training-data generation.
  Supported by the agentic API (priority #1), model serving + discovery + contributor
  toolkit (composable, self-sustaining AI library), remote data access (data-intensive
  workflows), and registration/4D propagation (real longitudinal reuse). A
  previously-unavailable capability that plays to ITK-SNAP's irreplaceable strength rather
  than competing where the ecosystem is already strong.

---

## Open questions before this is LOI-ready

- Confirm PI maintainer status + roadmap alignment statement.
- Pick host org / fiscal sponsor (single org receives the Track 1 grant).
- Decide how hard to lean on the agent-multiplier argument vs. a more conservative scope
  (could drop to the #3+#2 two-aim spine if reviewers are likely to discount it).
- Confirm the Flywheel access path (official SDK vs. direct REST) and a target user.
- Confirm SegFlow4D/FireANTs integration depth that fits Aim 1.4 without scope creep.
