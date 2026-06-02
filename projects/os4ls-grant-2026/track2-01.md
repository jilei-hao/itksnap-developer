# OS4LS Track 2 Sketch — ITK-SNAP Ecosystem Interoperability for AI-Native Imaging

**Status:** draft sketch (companion to `ideas.md`). Track 2 = Foundational Libraries &
Ecosystem Initiatives, **up to $1,000,000 over 2 years** ($500K/yr max, ≤10% indirects).

---

## One-line pitch

Turn the ITK-SNAP ecosystem (ITK-SNAP + greedy + Convert3D/c3d + GPU registration via
FireANTs + 4D propagation via SegFlow4D) into a **composable, AI-native hub** for
biomedical image segmentation and longitudinal/4D analysis — driven by agents and Python,
GPU-accelerated, serving AI models to multiple frontends, and interoperating cleanly with
the tools researchers use downstream (3D Slicer, FEBio/OpenSim, napari/MONAI).

> **Core thesis.** MONAI and Hugging Face already make *models* programmable; agentic
> medical-imaging pipelines lack a way to bring *expert human judgment* in. The ecosystem's
> irreplaceable asset is the expert at the screen making spatial judgments — so the goal is
> **not** "let agents run segmentation" (the ecosystem does that headlessly) but to make
> **expert verification, correction, and interaction-capture a first-class, orchestrable
> step.** *Model proposes, human disposes.*

## Why Track 2 (not Track 1)

- The RFA explicitly invites Track 2 proposals "developing shared interoperability,
  integrations, or common interfaces ... across a set of related tools within the same
  software ecosystem" and encourages spanning **up to 5 projects**.
- The full ambition (agentic API + model serving + interop bridges + adaptation) is
  ~4+ FTE-years — over a Track 1 budget. Track 2's $1M / 2yr can credibly staff it.
- It tells an ecosystem story, not a single-feature story, which is what Track 2 rewards.

## Projects in scope (with repos to list in the LOI)

Track 2 allows up to 5 projects. Candidate set (PICSL/Yushkevich family + the new
registration/4D members):

- **ITK-SNAP** — interactive 3D segmentation (core; mature, widely cited/adopted).
- **greedy** — CPU diffeomorphic registration (propagation, longitudinal).
- **Convert3D / c3d** — scriptable image/mesh conversion (the CLI substrate).
- **SegFlow4D** (`jilei-hao/segflow4d`) — 4D segmentation+mesh propagation over pluggable
  registration backends. *Your project → buy-in trivial.* Position as an **integration
  target / deliverable** within the mature ecosystem, not a project claiming independent
  traction (it's new).
- **FireANTs** (`jilei-hao/FireANTs`, fork of `rohitrango/fireants`) — GPU/PyTorch
  registration engine. ⚠️ **Two eligibility flags** (see below) — likely safest as a
  **funded-integration dependency / optional backend**, not a co-funded project, unless
  the license + upstream buy-in are resolved.
- *(Reference-integration partners, not funded line items):* 3D Slicer, FEBio/OpenSim,
  napari/MONAI — engaged for interop validation, not paid from this grant.

> **Maintainer buy-in is required** (RFA eligibility): PI must be a core maintainer and
> the work must align with each project's roadmap. ITK-SNAP/greedy/c3d share maintainers
> (Yushkevich et al.); SegFlow4D is the applicant's own. **FireANTs caveats:** (1) it
> ships a **custom "FireANTs License v1.0 (Modified Apache)"** — OS4LS excludes
> custom/restrictive licenses, so confirm OSI-standard licensing or scope FireANTs as a
> dependency; (2) upstream author (rohitrango) is external — co-funding would need their
> buy-in. The applicant maintains a fork, which supports using/extending it either way.

---

## Aims

### Aim 1 — Composable human-in-the-loop core (the connective tissue)
*Builds directly on the Track 1 spine; here it's the foundation the rest stands on. The
distinctive value is not headless inference (MONAI/HF do that) but making **expert
verification, correction, and interaction-capture** an orchestrable pipeline step —
"model proposes, human disposes."*
- **1.1 Headless, scriptable core API** over ITK-SNAP's toolkit-independent layer
  (workspace I/O, image/label ops, segmentation) — no GUI dependency.
- **1.2 Python wrapper** (pip-installable) + **agent-facing endpoint** (MCP/tool-style)
  so agents and pipelines call ITK-SNAP as a tool. Unify with the existing c3d/greedy
  Python surfaces (`greedy_python`) so the ecosystem presents one coherent API. Shipped
  as a **distributable local (stdio) MCP server** (client-launched, **no indefinite
  hosting obligation**); optional remote (HTTP) mode for cloud/multi-user use. Software,
  not hosted infrastructure.
- **1.3 Human-in-the-loop primitives** *(the differentiator).* Expose the human checkpoint
  as callable operations: review/correction as a step (`request_review(image, seg) →
  {corrected seg, decision, provenance}`), escalation/triage of uncertain cases, and
  capture of expert interactions (clicks/scribbles/edits/decisions) as machine-consumable
  labels, prompts, and preference signals (no MONAI/HF equivalent) with audit logging.
  Enables a human-in-the-loop **data engine** feeding active learning + the adaptation
  work (Aim 5) and curating SegFlow4D-propagated candidates (Aim 3).
- **1.4 Human-interaction surfaces** *(reference clients; see ideas #7/#8).* A web
  viewer/QC panel with a **URL-handoff** model (deep-linked local session + inline triage
  thumbnail + submit→callback), shippable standalone and as a **VS Code/Cursor webview**;
  and an in-app **"bring your own agent"** panel (MCP server + shared GUI-context, *not* a
  rebuilt agent harness) so the human checkpoint is reachable from browser, IDE, and
  in-app alike.
- **1.5 Scripted behavioral-regression harness** (`--test`) pinning API/GUI behavior —
  the progress-tracking/validation mechanism.

### Aim 2 — Shared AI model serving (one backend, many frontends)
- **2.1 DLE serving layer** — **FastAPI REST** service on MONAI bundles + Hugging Face;
  model-agnostic wrappers (prompt→input, output→native objects); generalizes the shipped
  `itksnap-dls` (nnInteractive) server, which is already REST. Keep REST as the baseline
  transport; add **WebSocket/SSE only as a future increment** for server-push features
  (live interaction streaming, GPU-queue notifications) — layered alongside REST, not a
  rewrite.
- **2.2 Dynamic model discovery** — no hardcoded model list; clients query server for
  available models + capabilities. **One open, documented protocol** consumed by the
  ITK-SNAP GUI, the Python wrapper, agents — **and external tools (Slicer/napari).**
- **2.3 Agent-assisted contributor toolkit** (vendor-neutral) — wrapper spec + scaffolding
  + CI conformance harness + a coding-agent front-end (a Claude skill as one instance).
  Local experimentation → PR → merge on conformance. The **scaling/sustainability engine.**
- **2.4 Remote-GPU execution** via lightweight SSH agent; start single-user, then lean on
  an existing scheduler (Ray Serve / Triton / MONAI Deploy) for allocation/queueing.

### Aim 3 — GPU-accelerated registration & 4D/longitudinal propagation *(new pillar)*
*Hardware-acceleration priority, made concrete; the registration/4D backbone of the family.*
- **3.1 Unified, backend-agnostic registration surface** — one Python/agent-callable API
  spanning **greedy (CPU/C++)** and **FireANTs (GPU/PyTorch)**, reusing SegFlow4D's proven
  pluggable handler-factory pattern (greedy / ANTs / FireANTs). Backend + device (CPU/GPU,
  local/remote) routed through the same remote-agent / GPU path as Aim 2.
- **3.2 4D segmentation+mesh propagation in the ecosystem** — integrate **SegFlow4D**:
  propagate a reference-frame segmentation (and surface meshes) across all frames of a 4D
  image. Expose **from inside ITK-SNAP** (propagate across a 4D workspace) and via the
  agent endpoint for batch/pipeline use. This is the real **within-subject longitudinal**
  capability (ARIA monitoring, training-data generation) — registration-based, no model
  retraining, low risk.
- **3.3 4D mesh output → biomechanics** — time-resolved warped meshes feed the Aim 4 mesh
  bridge (dynamic biomechanics, e.g. mitral valve over the cardiac cycle).

### Aim 4 — Interoperability bridges (the Track 2 differentiator)
- **4.1 Standardized segmentation interchange** — preserve label name / color / hierarchy
  / anatomical coding (SNOMED/FMA) across ITK-SNAP ↔ 3D Slicer Segmentation nodes, with
  **DICOM-SEG** as the lingua franca. Reference integration + open spec.
- **4.2 Segmentation → simulation-ready mesh bridge** — multi-label segmentation → clean
  surface → **tetrahedral volume mesh** (TetGen/CGAL/gmsh) with per-label material tags →
  export to **FEBio (`.feb`) / OpenSim**. A *previously-unavailable capability* for the
  cardiac / mitral-valve / musculoskeletal biomechanics audience. Leverages existing
  greedy/c3d/VTK + cm-rep/ConvertMesh mesh work, and consumes Aim 3.3's 4D meshes for
  dynamic simulation.
- **4.3 Pipeline interop** — reference recipes for ITK-SNAP as a node in napari / MONAI
  pipelines via the Aim 1 API + Aim 2 serving protocol.

### Aim 5 — Cross-domain model adaptation as an enabling feature *(stretch / lower priority)*
- LoRA corrections→training-data→adapter→serve **pipeline** as a reusable feature, with
  light feature-validation only (no method bake-off). Framed strictly as
  training-*enablement* (in scope), not model development.
- **Scoped against Aim 3:** within-subject/time-series reuse is handled by registration
  **propagation (Aim 3.2)**; LoRA targets **cross-subject/cross-domain** adaptation only.
  Propagation (Aim 3) can *generate the training data* this pipeline consumes.
- Verify architecture fit (nnInteractive is CNN-based; standard LoRA targets transformer
  layers — confirm a conv-adapter recipe or target a SAM/MedSAM2-style backbone).

---

## Scope discipline (what we deliberately do NOT promise)

- **No pairwise connector zoo.** Deliver open protocols/formats (DICOM-SEG, documented
  DLE API, Python wrapper) + **one or two reference integrations** (Slicer, FEBio). Other
  tools integrate against the open spec.
- **No GUI rewrite.** The Qt→web/Electron modernization stays out (RFA out-of-scope:
  "AI-assisted rewrite of a legacy tool"). The headless API de-risks any future UI work
  regardless.
- **No new models / no benchmark study.** Aim 5 ships a feature, not a model or a result.
- **No new registration algorithm research.** FireANTs/greedy are used and integrated as
  engines; the funded work is the *composable surface + ecosystem integration*, not novel
  registration methods (avoids the "model/method development" scope edge).
- **No data hosting / repository infrastructure** (RFA out-of-scope).

## Indicative budget shape (illustrative, ~$1M / 2yr)

| Area | Rough effort |
|------|--------------|
| Aim 1 — API + Python wrapper + agent endpoint + human-in-the-loop primitives + interaction surfaces (web viewer/webview, in-app agent panel) | ~1.5 FTE-yr |
| Aim 2 — serving + discovery + contributor toolkit + remote GPU | ~1.25 FTE-yr |
| Aim 3 — unified registration surface (greedy+FireANTs) + SegFlow4D 4D propagation | ~1.0 FTE-yr |
| Aim 4 — Slicer interchange + FEBio mesh bridge + pipeline recipes | ~1.0 FTE-yr |
| Aim 5 — LoRA pipeline (stretch) | ~0.5 FTE-yr |
| Cloud/GPU/storage, coordination, docs/tutorials | operational |

≈ 5–5.5 FTE-years total, near the top of what $1M/2yr can staff — Aim 5 (LoRA) and Aim
1.4's fuller interaction surfaces are the relief valves if effort runs over. (≤10%
indirects; detailed budget only at full-application stage.)

## How it scores against the RFA criteria

- **Existing impact:** ITK-SNAP's adoption + citations; greedy/c3d as ecosystem
  dependencies; FireANTs published (arXiv 2404.01249) with strong speed/accuracy results;
  shipped nnInteractive integration → not a prototype, not a rewrite.
- **Quality:** shared maintainer team across ITK-SNAP/greedy/c3d/SegFlow4D; public GitHub
  issues/PRs; existing CI and test harness; SegFlow4D's pluggable-backend factory as
  evidence of composable design; roadmap alignment.
- **Feasibility:** ~5–5.5 FTE-yr work for ~$1M/2yr; each aim has a discrete, testable
  deliverable; Aim 5 and Aim 1.4's fuller surfaces labeled as stretch / relief valves.
- **Value / AI-native:** the differentiator is **programmable expert judgment** — making
  verification/correction/interaction-capture orchestrable ("model proposes, human
  disposes"), reachable from browser/IDE-webview/in-app, which the MONAI/HF inference stack
  has no equivalent for. Supported by the agentic API (priority #1) + GPU-accelerated
  registration (hardware-acceleration priority, via FireANTs) + shared serving (composable
  AI) + longitudinal/4D propagation (real same-domain reuse) + interop bridges (downstream
  biomechanics/bioimaging). Contributor toolkit answers sustainability.

---

## Open questions before this is LOI-ready

- Confirm maintainer buy-in + roadmap alignment across ITK-SNAP, greedy, c3d (+ SegFlow4D,
  applicant-owned).
- **Resolve FireANTs licensing** — confirm the custom "FireANTs License v1.0" is
  OSI-standard, or scope FireANTs strictly as a dependency/optional backend. Confirm
  upstream (rohitrango) buy-in if co-funding.
- **Decide SegFlow4D positioning** — integration target/deliverable (recommended, given it
  is new) vs. a headline project (would need adoption evidence).
- Pick the host org / fiscal sponsor for fund dispersal (single org coordinates Track 2).
- Decide reference-integration partners (Slicer + FEBio assumed) and confirm willingness
  on their side (even informal).
- Validate the FEBio/OpenSim mesh requirements (incl. 4D meshes) with a target
  biomechanics user.
- Confirm LoRA architecture-fit decision (conv-adapter vs transformer backbone).
