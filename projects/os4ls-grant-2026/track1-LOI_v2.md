# OS4LS Letter of Intent — Track 1 (v2, from `track1-LOI.md`)

> Drafted to the fields in `LOI_requirements.md`. **Character counts below are verified
> (Python `len()`); re-check in the portal, which may count line breaks differently.**
> Track: **Track 1 — Domain-Specific Tools.**
> Scope: **two aims** — human-in-the-loop core + remote data access/interoperability.
> (Model serving is provided by the already-shipped `itksnap-dls`, leveraged not re-funded.)
>
> **Changes from v1:** (1) narrowed the over-absolute "no way to bring expert judgment in"
> claim so it survives the MONAI Label counter-example; (2) Landscape now names MONAI Label
> head-on, describes it accurately, and draws the distinction; (3) nnInteractive reframed as
> cross-viewer parity, not an ITK-SNAP edge; (4) host org resolved to UPenn/PICSL (no fiscal
> sponsor); (5) flagged the itksnap-dls repo link and live citation count as to-fix.

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
cycles. Critically, no existing tool exposes expert human judgment as a general,
agent-orchestrable step: AI-assisted labeling frameworks bring a human into their own
retraining loop, but not as a callable, resumable pipeline primitive an external agent can
invoke.

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

*(2,726 chars — verified.)*

---

## Expected Value (≤1500 characters)

MONAI and Hugging Face already make models programmable, and our shipped itksnap-dls serves
models into ITK-SNAP; what agentic medical-imaging pipelines lack is expert human judgment
as a general, agent-callable pipeline step — existing labeling tools keep the human inside
their own loop, not a primitive an external agent invokes. Success means ITK-SNAP becomes
that missing piece: the programmable verification, correction, and feedback-capture surface
where the model proposes and the human disposes.

Capabilities unlocked: human review/correction as a callable, resumable step (an agent
routes uncertain cases to an expert and gets structured, corrected results back); expert
interactions captured as machine-consumable labels and provenance; a human-in-the-loop data
engine that turns corrections into training data; and reproducible, scriptable segmentation
/ registration / 4D workflows callable from Python and agents.

Upstream/downstream: the API + MCP endpoint and open formats let other tools reuse ITK-SNAP
as the human checkpoint — e.g. lossless DICOM-SEG interchange with 3D Slicer; greedy,
FireANTs, and SegFlow4D gain a shared scriptable surface; remote/cloud archives become
first-class sources.

AI enablement / large-scale data: making expert judgment orchestrable enables
human-in-the-loop active learning and large-cohort, auditable training-data generation — the
data-prep that underpins model training and evaluation — with remote/partial data access for
scale.

*(1,487 chars — verified; tight, re-check the portal cap.)*

---

## Landscape Analysis (≤1500 characters)

ITK-SNAP's audience — clinical and basic researchers performing 3D biomedical image
segmentation — primarily uses open-source 3D Slicer, ITK-SNAP, and MITK, plus proprietary
suites (Materialise Mimics, Synopsys Simpleware) and vendor workstations (e.g. syngo.via,
MIM). In adjacent microscopy, napari is widely adopted.

On AI specifically, the closest comparator is MONAI Label: an AI-assisted, human-in-the-loop
labeling framework whose active learning ranks uncertain cases for the user, fronted by 3D
Slicer and OHIF, with PACS/XNAT access via DICOMweb. The nnInteractive model (CVPR 2025
interactive-segmentation challenge winner) is now integrated across napari, MITK, 3D Slicer,
and ITK-SNAP — so model-assisted interactive segmentation is becoming common to all of these
tools.

ITK-SNAP is among the most established and most cited tools in the space: ~20 years of
development, thousands of literature citations, a large international user base, and a
reputation as the most approachable tool for fast 3D segmentation. It is fully open source,
cross-platform, and actively maintained.

What no existing tool — MONAI Label included — provides is a general, agent-callable surface
that makes expert verification and correction a first-class, resumable, audited pipeline step
driven by an external agent, not a built-in labeling loop, composable with registration, 4D
propagation, and open formats. This proposal closes that gap, bringing a trusted tool fully
into AI-native research.

*(1,490 chars — verified; tight, re-check the portal cap.)*

---

## Other LOI form fields (per official guide)

- **Funding track:** Track 1 — Domain-Specific Tools (up to $250K / 2 years).
- **Software projects + repositories:**
  - ITK-SNAP — https://github.com/pyushkevich/itksnap (primary)
  - itksnap-dls (AI serving, existing — leveraged) — **[replace with GitHub repo URL; the
    guide asks for repositories, not docs. Docs: itksnap-dls.readthedocs.io]**
  - greedy — https://github.com/pyushkevich/greedy
  - SegFlow4D — https://github.com/jilei-hao/segflow4d
  - *(FireANTs used as an optional dependency/backend, not a funded project.)*
  - *(3D Slicer is an interoperability target via open formats — DICOM-SEG — not a funded project.)*
- **Applicant / host organization:** University of Pennsylvania (Penn Image Computing and
  Science Laboratory) — receives the grant directly; no fiscal sponsor required.
- **Statement of PI involvement:** The PIs are core maintainers of the ITK-SNAP project; the
  proposed work aligns with the project roadmap (AI integration, scripting/automation, remote
  data) and has support from the core maintainer community.

## To confirm before submission

- **Exact ITK-SNAP citation count** (pull live from Google Scholar for Yushkevich et al.,
  NeuroImage 2006) — replace "thousands of citations" with the real figure to strengthen
  Landscape + Existing Impact.
- **itksnap-dls GitHub repository URL** — swap in for the readthedocs link above.
- **License name/version for ITK-SNAP** — state explicitly (eligibility requires an open
  license; confirm GPL + version).
- **Named PI(s) of record** at UPenn/PICSL.
- Whether to name **FireANTs** in the LOI vs. only at full-application stage.
- Confirm **DICOM-SEG round-trip scope** with a 3D Slicer user (gates Aim 2.5
  interoperability).
- Re-verify all four section character counts **in the portal** (Expected Value and
  Landscape sit ~10–13 chars under the cap by my count).
