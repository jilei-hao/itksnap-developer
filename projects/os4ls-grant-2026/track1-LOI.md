# OS4LS Letter of Intent — Track 1 (from `track1-candidate.md`)

> Drafted to the fields in `LOI_requirements.md`. Character counts are approximate
> (verify in the portal). Track: **Track 1 — Domain-Specific Tools.**
> Scope: **two aims** — human-in-the-loop core + remote data access/interoperability.
> (Model serving is provided by the already-shipped `itksnap-dls`, leveraged not re-funded.)

---

## Proposal Title (≤60 characters)

**ITK-SNAP: Human-in-the-Loop AI Image Segmentation**

*(49 chars. Alternatives: "Agent-Ready ITK-SNAP for AI-Native Imaging" — 42;
"ITK-SNAP: the Human Checkpoint for Agentic Imaging" — 50.)*

---

## Short Summary (≤3000 characters)

ITK-SNAP is a widely used open-source application for interactive 3D segmentation of
biomedical images, with a ~20-year track record, thousands of citations, and a large
international user base across neuroimaging, radiology, and cardiology. It already
integrates AI: our shipped itksnap-dls server brings foundation-model segmentation
(nnInteractive) into ITK-SNAP. But like many mature tools it was built for manual,
GUI-driven use: its capabilities are hard to call from Python or from AI agents, and
imaging increasingly lives in remote/cloud archives that force inefficient download/upload
cycles. Critically, agentic pipelines have no way to bring *expert human judgment* in.

This proposal addresses that in two tightly-coupled aims — without rewriting the interface.

Aim 1 — Composable human-in-the-loop core. We expose ITK-SNAP's toolkit-independent logic
as a headless, scriptable API with a pip-installable Python wrapper and an agent-facing
(MCP) endpoint, so agents and data pipelines can call ITK-SNAP as a tool. Its distinctive
capability is a set of human-in-the-loop primitives: review/correction as a callable,
resumable step (request_review), and capture of expert interactions (clicks, scribbles,
edits, decisions) as machine-consumable labels and provenance — making expert judgment a
first-class, orchestrable pipeline step (model proposes, human disposes). The same surface
unifies CPU/GPU deformable registration (greedy, FireANTs) and 4D segmentation-and-mesh
propagation (SegFlow4D). Model inference is provided by the already-shipped itksnap-dls,
which this layer builds on.

Aim 2 — Remote data access + open-format interoperability. We add a pluggable explorer for
browsing and segmenting imaging stored in remote/cloud archives (local filesystem, remote
Linux via SSH, Flywheel), with DICOM/BIDS-aware organization, partial reads, and workspaces
that reference remote data without local download. The same data layer reads and writes
standard formats — notably DICOM-SEG with preserved label semantics — so segmentations move
losslessly to and from other tools (e.g. 3D Slicer), making ITK-SNAP the human-in-the-loop
checkpoint inside other pipelines.

The work builds on mature, working components (ITK-SNAP, itksnap-dls, greedy, SegFlow4D)
and is integration-heavy rather than greenfield — well-suited to AI-assisted development
within a focused two-year effort, and validated by ITK-SNAP's existing automated test
harness. The result positions a trusted, widely adopted tool for the AI-native,
data-intensive era.

*(≈2,350 chars.)*

---

## Expected Value (≤1500 characters)

MONAI and Hugging Face already make *models* programmable, and our shipped itksnap-dls
already serves models into ITK-SNAP; what agentic medical-imaging pipelines lack is a way to
bring **expert human judgment** in. Success means ITK-SNAP becomes that missing piece: the
programmable verification, correction, and feedback-capture surface where the **model
proposes and the human disposes**.

Capabilities unlocked: human review/correction as a *callable, resumable pipeline step* (an
agent routes uncertain cases to an expert and gets structured, corrected results back);
expert interactions captured as machine-consumable labels and provenance; a human-in-the-loop
**data engine** that turns corrections into training data; and reproducible, scriptable
segmentation / registration / 4D workflows callable from Python and agents.

Upstream/downstream: the API + MCP endpoint and open formats let other tools reuse ITK-SNAP
as the human checkpoint — e.g. lossless DICOM-SEG interchange with 3D Slicer; greedy,
FireANTs, and SegFlow4D gain a shared scriptable surface; and remote/cloud archives become
first-class data sources.

AI enablement / large-scale data: making expert judgment orchestrable enables
human-in-the-loop active learning and large-cohort, auditable training-data generation — the
data-prep that underpins model training and evaluation — with remote/partial data access for
scale.

*(≈1,450 chars — verify against the 1,500 cap in the portal.)*

---

## Landscape Analysis (≤1500 characters)

ITK-SNAP's audience — clinical and basic researchers performing 3D biomedical image
segmentation — primarily uses 3D Slicer, ITK-SNAP, and MITK (open source), plus proprietary
tools such as Materialise Mimics, Synopsys Simpleware, and vendor workstations (e.g.
syngo.via, MIM). In adjacent microscopy/bioimaging, napari is widely adopted, and MONAI
Label provides AI-assisted labeling.

ITK-SNAP is among the most established and widely cited tools in this space: ~20 years of
development, thousands of literature citations, a large international user base, and a
reputation as the go-to tool for fast, intuitive manual and semi-automatic segmentation. It
is fully open source, cross-platform, and actively maintained.

Relative to alternatives, ITK-SNAP is more focused and approachable than 3D Slicer and far
more accessible than proprietary suites, but historically less scriptable and less
AI-integrated. It already uses AI: the shipped itksnap-dls integration serves the
nnInteractive foundation model (CVPR 2025 interactive-segmentation challenge winner) for
prompt-based 3D segmentation. This proposal closes the remaining gap — making ITK-SNAP
scriptable, agent-ready, and interoperable via open standards, with expert human judgment as
a callable pipeline step — bringing a trusted tool fully into AI-native research.

*(≈1,350 chars.)*

---

## Other LOI form fields (per official guide)

- **Funding track:** Track 1 — Domain-Specific Tools (up to $250K / 2 years).
- **Software projects + repositories:**
  - ITK-SNAP — https://github.com/pyushkevich/itksnap (primary)
  - itksnap-dls (AI serving, existing — leveraged) — readthedocs: itksnap-dls.readthedocs.io
  - greedy — https://github.com/pyushkevich/greedy
  - SegFlow4D — https://github.com/jilei-hao/segflow4d
  - *(FireANTs used as an optional dependency/backend, not a funded project.)*
  - *(3D Slicer is an interoperability target via open formats — DICOM-SEG — not a funded project.)*
- **Applicant / host organization:** [fill in — org that would receive the grant /
  fiscal sponsor].
- **Statement of PI involvement:** The PIs are core maintainers of the ITK-SNAP project; the
  proposed work aligns with the project roadmap (AI integration, scripting/automation, remote
  data) and has support from the core maintainer community.

## To confirm before submission

- Citation/adoption numbers for ITK-SNAP (exact citation count, download/user stats) to
  strengthen Landscape + Existing Impact.
- License name for ITK-SNAP (state explicitly; confirm version).
- Host org / fiscal sponsor and PI(s) of record.
- Whether to name FireANTs at all in the LOI vs. only at full-application stage.
- Confirm DICOM-SEG round-trip scope with a 3D Slicer user (gates Aim 2.5 interoperability).
