# OS4LS Letter of Intent — Track 1 (from `track1-01.md`)

> Drafted to the fields in `LOI_requirements.md`. Character counts are approximate
> (verify in the portal). Track: **Track 1 — Domain-Specific Tools.**

---

## Proposal Title (≤60 characters)

**ITK-SNAP: AI-Native, Agent-Ready Image Segmentation**

*(51 chars. Alternatives: "Agent-Ready ITK-SNAP for AI-Driven Segmentation" — 47;
"Making ITK-SNAP Composable for AI-Native Imaging" — 48.)*

---

## Short Summary (≤3000 characters)

ITK-SNAP is a widely used open-source application for interactive 3D segmentation of
biomedical images, with a ~20-year track record, thousands of citations, and a large
international user base across neuroimaging, radiology, cardiology, and biomechanics
research. Like many mature scientific tools, it was built for manual, GUI-driven
workflows and is not yet designed for AI-native or agentic use: its capabilities are
hard to call from Python or from AI agents; state-of-the-art segmentation models remain
out of reach for users without coding expertise or local GPUs; and imaging increasingly
lives in remote and cloud archives that force inefficient download/upload cycles.

This proposal modernizes ITK-SNAP along three tightly-coupled axes — without rewriting
its interface.

Aim 1 — Composable core. We expose ITK-SNAP's toolkit-independent logic as a headless,
scriptable API with a pip-installable Python wrapper and an agent-facing (MCP-style)
endpoint, so AI agents and data pipelines can drive segmentation, workspace operations,
registration, and longitudinal analysis programmatically. The same surface unifies
CPU/GPU deformable registration (greedy, FireANTs) and 4D segmentation-and-mesh
propagation (SegFlow4D), giving one composable interface across segmentation,
registration, and longitudinal/4D workflows.

Aim 2 — AI model serving. We generalize our already-shipped itksnap-dls server — which
serves the nnInteractive foundation model over a REST API today — into a model-agnostic
serving layer built on MONAI and Hugging Face. Models are discovered dynamically (no
hardcoded list), wrapped behind a common contract mapping ITK-SNAP prompts to model
inputs and model outputs to native objects, and run locally, on a remote GPU, or in the
cloud. An agent-assisted contributor toolkit lets the community add new models through a
templated, test-gated pull-request workflow.

Aim 3 — Remote data access. We add a pluggable explorer for browsing and segmenting
imaging stored in remote/cloud archives (local filesystem, remote Linux via SSH,
Flywheel), with DICOM/BIDS-aware organization, partial reads, and workspaces that
reference remote data without local download.

Aim 4 — Interoperability. Via open formats and reference integrations, ITK-SNAP becomes
composable with the tools researchers use downstream: standardized segmentation
interchange with 3D Slicer (preserving label semantics via DICOM-SEG), and a bridge that
turns segmentations into simulation-ready meshes for biomechanics (FEBio/OpenSim).

The work builds on mature, working components (ITK-SNAP, itksnap-dls, greedy, SegFlow4D)
and is integration-heavy rather than greenfield — well-suited to AI-assisted development
within a focused two-year effort, and validated by ITK-SNAP's existing automated test
harness. The result positions a trusted, widely adopted tool for the AI-native,
data-intensive era.

*(≈2,500 chars.)*

---

## Expected Value (≤1500 characters)

MONAI and Hugging Face already make *models* programmable; what agentic medical-imaging
pipelines lack is a way to bring **expert human judgment** in. Success means ITK-SNAP
becomes that missing piece: the programmable verification, correction, and
feedback-capture surface where the **model proposes and the human disposes**.

Capabilities unlocked: human review/correction as a *callable pipeline step* (an agent
can route uncertain cases to an expert in ITK-SNAP and get structured, corrected results
back); expert interactions (clicks, scribbles, edits, accept/reject) captured as
machine-consumable labels and feedback; a human-in-the-loop **data engine** that turns
expert corrections into training data; and access to AI models from local/remote/cloud
GPUs without coding.

Upstream/downstream: the API + MCP endpoint and open formats let other tools reuse
ITK-SNAP as the human checkpoint — standardized DICOM-SEG interchange with 3D Slicer,
node in napari/MONAI pipelines, and a segmentation→mesh bridge feeding biomechanics
(FEBio/OpenSim); greedy, FireANTs, and SegFlow4D gain a shared scriptable surface.

AI enablement / large-scale data: making expert judgment orchestrable enables
human-in-the-loop active learning and large-cohort, auditable training-data generation —
the data-prep that underpins model training and evaluation — with remote/partial data
access for scale.

*(≈1,480 chars — verify against the 1,500 cap in the portal.)*

---

## Landscape Analysis (≤1500 characters)

ITK-SNAP's audience — clinical and basic researchers performing 3D biomedical image
segmentation — primarily uses 3D Slicer, ITK-SNAP, and MITK (open source), plus
proprietary tools such as Materialise Mimics, Synopsys Simpleware, and vendor
workstations (e.g. syngo.via, MIM). In adjacent microscopy/bioimaging, napari is widely
adopted, and MONAI Label provides AI-assisted labeling.

ITK-SNAP is among the most established and widely cited tools in this space: ~20 years of
development, thousands of literature citations, a large international user base, and a
reputation as the go-to tool for fast, intuitive manual and semi-automatic segmentation.
It is fully open source, cross-platform, and actively maintained.

Relative to alternatives, ITK-SNAP is more focused and approachable than 3D Slicer and
far more accessible than proprietary suites, but historically less scriptable and less
AI-integrated. It already uses AI: the shipped itksnap-dls integration serves the
nnInteractive foundation model (CVPR 2025 interactive-segmentation challenge winner) for
prompt-based 3D segmentation. This proposal closes the remaining gap — making ITK-SNAP
scriptable, agent-ready, and a hub for a broad AI model library — bringing a trusted tool
fully into AI-native research.

*(≈1,350 chars.)*

---

## Other LOI form fields (per official guide)

- **Funding track:** Track 1 — Domain-Specific Tools (up to $250K / 2 years).
- **Software projects + repositories:**
  - ITK-SNAP — https://github.com/pyushkevich/itksnap (primary)
  - itksnap-dls (AI serving) — readthedocs: itksnap-dls.readthedocs.io
  - greedy — https://github.com/pyushkevich/greedy
  - SegFlow4D — https://github.com/jilei-hao/segflow4d
  - *(FireANTs used as an optional dependency/backend, not a funded project.)*
  - *(3D Slicer and FEBio/OpenSim are interoperability targets via open formats, not
    funded projects.)*
- **Applicant / host organization:** [fill in — org that would receive the grant /
  fiscal sponsor].
- **Statement of PI involvement:** The PI is a core maintainer of ITK-SNAP; the proposed
  work aligns with the project roadmap (AI integration, scripting/automation, remote
  data) and has support from the core maintainer community.

## To confirm before submission

- Citation/adoption numbers for ITK-SNAP (exact citation count, download/user stats) to
  strengthen Landscape + Existing Impact.
- License name for ITK-SNAP (state explicitly; confirm GPL/version).
- Host org / fiscal sponsor and PI of record.
- Whether to name FireANTs at all in the LOI vs. only at full-application stage.
- Confirm DICOM-SEG round-trip scope with a 3D Slicer user, and (for the FEBio stretch)
  validate mesh requirements with a biomechanics user — even informal partner interest
  strengthens the interop claim.
