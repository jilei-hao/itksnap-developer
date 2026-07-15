# Open Source for the Life Sciences (OS4LS) — Work Plan

**Proposal Title:** ITK-SNAP: Human-in-the-Loop AI Image Segmentation

**Applicant Name:** Paul Yushkevich

> Template constraints (for the reviewer/reviser):
> - **Work plan narrative: max 750 words.** Current draft ≈ 400 words.
> - **Goals: up to 5**, not counted in the 750-word limit. Each goal has four fields: Goal, Outcome, Milestones & Deliverables (numbered, tagged Year 1 / Year 2), Success indicators.
> - `[N]` markers are placeholders for concrete numeric targets still to be decided.

---

## Work Plan (narrative — max 750 words)

ITK-SNAP is a widely used open-source application for interactive segmentation of 3D and 4D biomedical images, developed at the Penn Image Computing and Science Laboratory with a more than 20-year track record, over 11,000 citations, and more than 1.1 million downloads. This request supports a 24-month effort to bring ITK-SNAP's expert-in-the-loop capabilities into AI-native research, organized around the two goals below plus a community engagement activity near the end of Year 2.

Goal 1 exposes ITK-SNAP's toolkit-independent segmentation logic as a headless, scriptable API with a pip-installable Python wrapper and an agent-facing (MCP) endpoint, so agents and data pipelines can invoke expert review as a callable, resumable step (`request_review`) and capture expert interactions — clicks, scribbles, edits, decisions — as machine-consumable labels and provenance. Goal 2 adds a pluggable explorer for browsing and segmenting datasets in remote and cloud archives without local download, and strengthens interoperability with standard open formats so segmentations move cleanly to and from other tools.

This work sits within our published roadmap. Goal 1 delivers through the ITK-SNAP 4.8 release and builds on our shipped itksnap-dls server, which already serves foundation-model interactive segmentation into the GUI; the headless API generalizes that integration into a stable, agent-callable surface. Goal 2 delivers across the ITK-SNAP 4.8 (Year 1) and 4.10 (Year 2) releases and extends a working remote-access prototype. The effort is integration-heavy rather than greenfield, well suited to AI-assisted development and validated against ITK-SNAP's existing automated test harness.

Beyond the requested funds, our institution contributes a portion of the lead maintainer's time, existing continuous-integration and test infrastructure, and the mature codebases the work builds on (ITK-SNAP, itksnap-dls, greedy, Convert3D). The team has a proven track record delivering initiatives funded by CZI EOSS and the NIH.

We will pair development with sustained community engagement. Near the end of Year 2, once the new agent-callable and remote-data features have shipped, we will run a single hybrid (in-person and remote) event that combines hands-on training with a contributor hackathon, targeting ITK-SNAP's core audience of clinical and imaging researchers and developers of adjacent pipeline tools. Throughout the grant we will also publish a series of YouTube video tutorials, maintain a frequent social-media presence, and expand developer documentation for the new interfaces — to drive adoption, gather feedback, and onboard new contributors and maintainers.

All code will be developed in the open under ITK-SNAP's existing open-source license (GPL-3.0), with releases published through our established channels and the Python wrapper published to PyPI.

---

## Goals, Outcomes, Milestones and Deliverables

*(up to 5 goals; not included in the 750-word limit)*

### Goal 1: Composable human-in-the-loop core (LOI Aim 1)

**Outcome:** Agents and data pipelines can call ITK-SNAP's expert-review capabilities directly through a stable interface, so expert verification and correction becomes a first-class, resumable, orchestrable pipeline step — the model proposes and the human adjudicates — and the resulting expert judgments feed back into model improvement.

**Milestones & Deliverables:**

- **1.1** Release ITK-SNAP 4.8 with a headless, scriptable API (pip-installable wrapper and agent-facing MCP endpoint) providing agent-callable segmentation and the `request_review` resumable review primitive. **[Year 1]**
- **1.2** Ship the expert-interaction capture format: each `request_review` correction is recorded as a machine-consumable record — the model's proposal, the expert's interactions and corrected label, plus case metadata, identity, and timestamp — using a documented, reusable schema (aligned with established provenance conventions where practical). **[Year 2]**
- **1.3** Using the captured records, evaluate the value of expert-in-the-loop correction on at least one public benchmark dataset: fine-tune a served foundation model on expert-corrected cases and report the change in segmentation accuracy (standard overlap and boundary metrics) relative to the uncorrected baseline; and assess whether routing uncertain cases to the expert improves annotation efficiency versus random case selection. Release the evaluation harness and protocol as open source. **[Year 2]**

**Success indicators:** ITK-SNAP 4.8 released with the headless API and `request_review`; agent-callable segmentation and review pass the existing automated test harness. [Year 1] Expert interactions captured as machine-consumable, provenance-tagged records across a set of reviewed cases spanning at least one anatomy/modality; on at least one public benchmark (e.g., a cardiac CT benchmark such as MM-WHS and/or the Medical Segmentation Decathlon hippocampus task), fine-tuning on expert-corrected cases yields a measurable improvement over the uncorrected baseline on standard overlap and boundary metrics (magnitude reported); routing uncertain cases to the expert shows improved annotation efficiency versus random selection at comparable expert effort; and the evaluation harness, protocol, and record schema are released open source. [Year 2]

---

### Goal 2: Remote data access and open-format interoperability (LOI Aim 2)

**Outcome:** Users and agents browse, segment, and manage imaging datasets that live in remote and cloud archives without lossy manual downloads, and segmentations move faithfully — losslessly where the format allows — between ITK-SNAP and the rest of the ecosystem, making ITK-SNAP the human checkpoint inside larger pipelines.

**Milestones & Deliverables:**

- **2.1** Release ITK-SNAP 4.8 with an agent-callable remote data-access feature and a file-explorer UI (local filesystem, remote Linux via SSH, and Flywheel; DICOM-aware, with BIDS support where applicable). **[Year 1]**
- **2.2** Enable working across multiple datasets/workspaces from the explorer, agent-accessible (e.g., managing and switching among several open or queued workspaces). **[Year 2]**
- **2.3** Release ITK-SNAP 4.10 with improved interoperability for interchange of segmentations with standard open formats (e.g., DICOM-SEG), with round-trip fidelity validated and any limitations documented. **[Year 2]**

**Success indicators:** ITK-SNAP 4.8 released with remote data access; a remote dataset browsed and segmented without local download. [Year 1] ITK-SNAP 4.10 released with agent-accessible management of multiple datasets/workspaces from the explorer, and round-trip interchange of segmentations (e.g. DICOM-SEG) validated against at least one external tool such as 3D Slicer, with fidelity documented. [Year 2]

---

### Goal 3: Community engagement and developer experience

**Outcome:** The community understands and adopts the new agent-callable and remote-data features, developers can build on ITK-SNAP through well-documented interfaces, and sustained outreach grows a pipeline of new users, contributors, and maintainers that strengthens the project's long-term sustainability.

**Milestones & Deliverables:**

- **3.1** Organize and run a single hybrid (in-person and remote) event near the end of Year 2 that combines hands-on training on the new features with a contributor hackathon, with prepared materials and live demos. **[Year 2]**
- **3.2** Produce a series of YouTube video tutorials demonstrating the new agent-callable and remote-data features and common workflows. **[Year 1 & Year 2]**
- **3.3** Maintain a frequent social-media presence (release announcements, feature demos, and tips) to sustain community engagement. **[Year 1 & Year 2]**
- **3.4** Write and publish developer documentation for the headless API, MCP endpoint, and data layer to lower the barrier for external contributors. **[Year 1 & Year 2]**

**Success indicators:** One hybrid event held in Year 2 with at least [N] participants and post-event feedback collected. [Year 2] At least [N] video tutorials published with [N]+ cumulative views, and a regular cadence of social-media posts sustained across both years. [Year 1 & Year 2] Developer documentation covering the new interfaces published, with at least [N] new external contributors or merged community pull requests. [Year 2]

---

## Open items / notes for reviser

- **Applicant name & title** must match the submission form exactly.
- **`[N]` targets** in success indicators need concrete numbers (participants, tutorials, views, contributors).
- **Shared 4.8 release:** ITK-SNAP 4.8 (Year 1) currently carries both Goal 1's headless API (1.1) and Goal 2's remote data access (2.1). Confirm this single release train, or renumber to distinct versions per goal.
- **"Published roadmap"** wording assumes GitHub Milestones (4.8, 4.10) will be created before submission.
- **License:** currently "ITK-SNAP's existing open-source license" — name it explicitly (e.g. GPL/BSD) if desired.
- Final submission format required by OS4LS is **PDF**.