# Section 4 — Project Details, fields 1–3 (paste-ready)

These are the three character-limited fields that open Section 4, pre-filled from the LOI and edited
per the instructions ("Edit as needed from LOI"). Each is a clean, paste-ready plain-text block.

**Status:** all three already fit (they were submitted and accepted in the LOI at identical limits:
3,000 / 1,500 / 1,500). Short Summary and Expected Value sat right at the ceiling, so I applied a few
**pure tightenings** (no change to scope or claims) to create a small safety margin — noted under each.
Exact counts (including single paragraph-break newlines, i.e. how they'd paste) are given per field.

> **Two cautions from the instructions:** (1) the form may count newlines — keep a margin; (2) *significant*
> changes from the LOI (especially to scope) can flag the application for extra review, so these edits stay
> within the submitted scope.

---

## 1. Short Summary — limit 3,000 characters · measured **2,945 / 3,000** ✅ (~55 to spare)

<!--FIELD1-->
ITK-SNAP is a widely used open-source application for interactive segmentation of 3D and 4D biomedical images, with a >20-year track record, >11K citations, including in top-tier Science and Nature journals, >1.1M downloads, and a large international user base across neuroimaging, radiology, and cardiology. One main way ITK-SNAP supports science in the AI era is letting experts supervise automated segmentation of complex medical image datasets — guiding the segmentation process, and visualizing and correcting the results of fully autonomous pipelines. Indeed, ITK-SNAP already integrates with modern AI frameworks through a Python/PyTorch-based itksnap-dls server that exposes foundation-model interactive segmentation (nnInteractive) in the ITK-SNAP GUI. But ITK-SNAP was built mainly for GUI-driven use, and many of its capabilities are hidden in C++ libraries, out of reach of emerging agentic AI workflows. Exposing ITK-SNAP's expert-in-the-loop functionality to AI agents would enable new medical image analysis paradigms that combine advanced dynamic pipelines with expert user supervision. Imaging datasets also increasingly live in remote/cloud archives, forcing inefficient download/upload cycles; robust remote data access would facilitate use across large multi-site studies.
The specific aims of this proposal address these needs:
Aim 1 — Composable human-in-the-loop core. We will expose ITK-SNAP's toolkit-independent logic as a headless, scriptable API with a pip-installable Python wrapper and an agent-facing (MCP) endpoint, so agents and data pipelines can call ITK-SNAP and the underlying C++ libraries as tools. Its distinctive capability is a set of human-review primitives: review/correction as a callable, resumable step (request_review), and capture of expert interactions (clicks, scribbles, edits, decisions) as machine-consumable labels and provenance — making expert judgment a first-class, orchestrable pipeline step.
Aim 2 — Remote data access + open-format interoperability. We will add a pluggable explorer for browsing and segmenting imaging datasets stored in remote/cloud archives (local filesystem, remote Linux via SSH, Flywheel), with DICOM/BIDS-aware organization, partial reads, and workspaces that reference remote data without local download. The same data layer reads and writes standard formats so segmentations move losslessly to and from other tools (e.g. 3D Slicer), making ITK-SNAP the human checkpoint inside other pipelines.
The work builds on mature, working components (ITK-SNAP, itksnap-dls, greedy, SegFlow4D) and is integration-heavy rather than greenfield — well-suited to AI-assisted development within a focused two-year effort, and validated by ITK-SNAP's existing automated test harness. The team has a proven track record delivering initiatives funded by CZI EOSS and the NIH. The result positions a trusted, widely adopted tool for the AI-native, data-intensive era.
<!--/FIELD1-->

*Tightening applied:* "One of the main ways in which ITK-SNAP supports science in the AI era is to provide a
way for experts to supervise … by providing guidance in the process of segmentation, and by visualizing and
correcting" → "One main way ITK-SNAP supports science in the AI era is letting experts supervise … guiding
the segmentation process, and visualizing and correcting". Scope and every claim preserved.

---

## 2. Expected Value — limit 1,500 characters · measured **1,485 / 1,500** ✅ (~15 to spare)

<!--FIELD2-->
MONAI and Hugging Face already make models programmable, and our itksnap-dls serves models into ITK-SNAP; what agentic medical-imaging pipelines lack is expert human judgment as a general, agent-callable pipeline step — existing labeling tools keep the human inside their own loop, not a primitive that an external agent invokes. Success means ITK-SNAP becomes the missing layer for verification, correction, and feedback capture — a programmable interface where the model proposes and the human adjudicates.
Capabilities unlocked: human review/correction as a callable, resumable step (an agent routes uncertain cases to an expert and gets structured, corrected results back); expert interactions captured as machine-consumable labels and provenance; a data engine that turns corrections into training data; and reproducible, scriptable image analysis workflows callable from Python and agents.
Upstream and downstream improvements: the API + MCP endpoint and open formats let other tools reuse ITK-SNAP as the human checkpoint — e.g. lossless DICOM-SEG interchange with 3D Slicer; image registration tools like FireANTs gain a shared scriptable surface; remote/cloud archives become first-class data sources.
AI enablement and large-scale data analysis: making expert judgment orchestrable enables active learning and large-cohort, auditable training-data generation — the data-prep that underpins model training and evaluation — with remote/partial data access for scale.
<!--/FIELD2-->

*Tightening applied:* "our shipped itksnap-dls" → "our itksnap-dls"; "fills the gap as the missing layer" →
"becomes the missing layer". Scope and claims preserved.

---

## 3. Landscape Analysis — limit 1,500 characters · measured **1,490 / 1,500** ✅ (~10 to spare)

<!--FIELD3-->
ITK-SNAP's audience — clinical and basic researchers performing 3D biomedical image segmentation — primarily uses open-source 3D Slicer, ITK-SNAP, and MITK, plus proprietary suites (Materialise Mimics, Synopsys Simpleware) and vendor workstations (syngo.via, MIM). In adjacent microscopy, napari is widely used.
On AI specifically, the closest comparator is MONAI Label: an AI-assisted interactive labeling framework whose active learning ranks uncertain cases for the user, fronted by 3D Slicer and OHIF, with PACS/XNAT access via DICOMweb. The nnInteractive model (CVPR 2025 interactive-segmentation challenge winner) is now integrated across napari, MITK, 3D Slicer, and ITK-SNAP — so model-assisted interactive segmentation is becoming common across these tools.
ITK-SNAP is among the most established and most cited tools in the space: ~20 years of development, 11,082 citations of its methods paper, 1.16M+ SourceForge downloads, a large international user base, and a reputation as the most approachable tool for fast 3D segmentation. It is fully open source, cross-platform, and actively maintained.
What no existing tool provides is a general, agent-callable surface that makes expert verification and correction a first-class, resumable, audited pipeline step driven by an external agent (not a labeling loop), composable with registration, 4D segmentation propagation, and open formats. This proposal closes that gap, bringing a trusted tool fully into AI-native research.
<!--/FIELD3-->

*No change from the LOI* (fits with margin as submitted).

---

## Optional consistency edit (your call)

The submitted Short Summary and Expected Value use **"losslessly" / "lossless DICOM-SEG interchange."** The
work plan now uses the softer, sharper **"validated round-trip fidelity, limitations documented."** Leaving
the summary's aspirational "lossless" is fine (it reads as the vision; the work plan carries the precision),
but if you want strict consistency, change "move losslessly" → "move faithfully" (Short Summary) and
"lossless DICOM-SEG interchange" → "faithful DICOM-SEG interchange" (Expected Value). Both are character-
neutral or shorter, so they won't break the limits.
