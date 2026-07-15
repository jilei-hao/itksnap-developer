# Open Source for the Life Sciences (OS4LS) — Work Plan

**Proposal Title:** ITK-SNAP: Human-in-the-Loop AI Image Segmentation

**Applicant Name:** Paul Yushkevich

> Template constraints (for the reviewer/reviser):
> - **Work plan narrative: max 750 words.** Current draft ≈ 415 words.
> - **Goals: up to 5**, not counted in the 750-word limit. Each goal has four fields: Goal, Outcome, Milestones & Deliverables (numbered, tagged Year 1 / Year 2), Success indicators.
> - This revision (v6) incorporates Paul's v5 review comments; see the change-log note at the end.

---

## Work Plan (narrative — max 750 words)

ITK-SNAP is a widely used open-source application for interactive segmentation of 3D and 4D biomedical images, developed at the Penn Image Computing and Science Laboratory with a more than 20-year track record, over 11,000 citations, and more than 1.1 million downloads. This request supports a 24-month effort to bring ITK-SNAP's expert-in-the-loop capabilities into AI-native research, organized around the two goals below plus a community engagement activity near the end of Year 2.

Goal 1 exposes ITK-SNAP's toolkit-independent segmentation logic as a headless, scriptable API with a pip-installable Python wrapper and an agent-facing (MCP) endpoint, so agents and data pipelines can invoke expert review as a callable, resumable step (`request_review`) and capture expert interactions — clicks, scribbles, edits, decisions — as machine-consumable labels and provenance. Goal 2 adds a pluggable explorer for browsing and segmenting datasets in remote and cloud archives without local download, and strengthens interoperability with standard open formats so segmentations move cleanly to and from other tools.

This work sits within our published roadmap. Goal 1 delivers through the ITK-SNAP 4.8 release and builds on our shipped itksnap-dls server, which already serves foundation-model interactive segmentation into the GUI; the headless API generalizes that integration into a stable, agent-callable surface. Goal 2 delivers across the ITK-SNAP 4.8 (Year 1) and 4.10 (Year 2) releases and extends a working remote-access prototype. The effort extends and connects mature, already-shipping components rather than building from scratch, is well suited to AI-assisted development, and is validated against ITK-SNAP's existing automated test harness.

The work builds on substantial existing foundations — the lead maintainer's established role in the project, mature continuous-integration and test infrastructure, and the codebases the effort extends (ITK-SNAP, itksnap-dls, greedy, Convert3D). The team has a proven track record delivering initiatives funded by CZI EOSS and the NIH.

We will pair development with sustained community engagement. Near the end of Year 2, once the new agent-callable and remote-data features have shipped, we will run one or more hybrid (in-person and remote) events that combine hands-on training with a contributor hackathon, targeting ITK-SNAP's core audience of clinical and imaging researchers and developers of adjacent pipeline tools. Throughout the grant we will also publish a series of YouTube video tutorials, maintain a frequent social-media presence, and expand developer documentation for the new interfaces — to drive adoption, gather feedback, and onboard new contributors and maintainers.

All code will be developed in the open under ITK-SNAP's existing open-source license (GPL-3.0), with releases published through our established channels and the Python wrapper published to PyPI.

---

## Goals, Outcomes, Milestones and Deliverables

*(up to 5 goals; not included in the 750-word limit)*

### Goal 1: Composable human-in-the-loop core (LOI Aim 1)

**Outcome:** Agents and data pipelines can call ITK-SNAP's expert-review capabilities directly through a stable interface, so expert verification and correction becomes a first-class, resumable, orchestrable pipeline step — the model proposes and the human adjudicates — and the resulting expert judgments feed back into model improvement.

In practice, an agent processing a dataset runs ITK-SNAP's segmentation headlessly and, when a case needs human judgment, calls `request_review` — launching ITK-SNAP on the user's machine with the images and the model's proposed segmentation loaded; the expert accepts or corrects it, and the agent resumes with the corrected label and a record of what changed. The same mechanism serves lighter-weight inspection: an agent that suspects misregistration between a subject's T1 and FLAIR can open both, correctly overlaid with the cursor at the location of interest, for a quick human look — extending ITK-SNAP's existing workspace and URL concepts into an agent-callable surface.

**Milestones & Deliverables:**

- **1.1** Release ITK-SNAP 4.8 with a headless, scriptable API (pip-installable wrapper and agent-facing MCP endpoint) providing agent-callable segmentation and the `request_review` resumable review primitive. **[Year 1]**
- **1.2** Ship the expert-interaction capture format: each `request_review` correction is recorded as a machine-consumable record — the model's proposal, the expert's interactions and corrected label, plus case metadata, identity, and timestamp — using a documented, reusable schema (aligned with established provenance conventions where practical). **[Year 2]**
- **1.3** Using the captured records, evaluate the value of expert-in-the-loop correction on at least one public benchmark dataset: fine-tune a served foundation model on expert-corrected cases and report the change in segmentation accuracy (standard overlap and boundary metrics) relative to the uncorrected baseline; and assess whether routing uncertain cases to the expert improves annotation efficiency versus random case selection. Release the evaluation harness and protocol as open source. **[Year 2]**

**Success indicators:**
- **[Year 1]** ITK-SNAP 4.8 released; agent-callable segmentation and `request_review` pass the existing automated test harness.
- **[Year 2]** Expert interactions captured as provenance-tagged records spanning at least one anatomy/modality; on at least one public benchmark (e.g., MM-WHS cardiac CT and/or the Medical Segmentation Decathlon hippocampus task), fine-tuning on expert-corrected cases yields a measurable improvement over the uncorrected baseline (overlap and boundary metrics, magnitude reported), and routing uncertain cases to the expert shows improved annotation efficiency versus random selection; evaluation harness, protocol, and record schema released open source.

---

### Goal 2: Remote data access and open-format interoperability (LOI Aim 2)

**Outcome:** Users and agents browse and segment imaging datasets where they live — in remote and cloud archives — without downloading and manually rearranging files, and segmentations move faithfully between ITK-SNAP and the rest of the ecosystem, making ITK-SNAP the human checkpoint inside larger pipelines. This spans institutional platforms such as Flywheel — a data-management system used widely across imaging research, where studies sit behind an API rather than as loose files — and public repositories: a dataset published on OpenNeuro or Dryad could be opened in ITK-SNAP from a single URL, replacing today's download-and-arrange workflow.

**Milestones & Deliverables:**

- **2.1** Release ITK-SNAP 4.8 with an agent-callable remote data-access feature and a file-explorer UI (local filesystem, remote Linux via SSH, and Flywheel; DICOM-aware, with BIDS support where applicable). **[Year 1]**
- **2.2** Add explorer- and agent-driven workspace navigation: opening a workspace from the explorer prompts to save the current one, then unloads and loads the selected workspace (one active workspace per instance), so a reviewer or agent can move through a queue of cases without hunting through file dialogs. As an exploratory stretch, evaluate keeping multiple workspaces resident for fast switching, contingent on relaxing the single-active-session assumption. **[Year 2]**
- **2.3** Release ITK-SNAP 4.10 with improved interoperability for interchange of segmentations with standard open formats (e.g., DICOM-SEG), with round-trip fidelity validated and any limitations documented. **[Year 2]**

**Success indicators:**
- **[Year 1]** ITK-SNAP 4.8 released with remote data access; a remote dataset browsed and segmented without local download, and a public dataset (e.g., OpenNeuro or Dryad) opened from a single URL.
- **[Year 2]** ITK-SNAP 4.10 released with explorer- and agent-driven workspace navigation (queue-style case switching), and round-trip interchange of segmentations (e.g., DICOM-SEG) validated against at least one external tool such as 3D Slicer, with fidelity documented.

---

### Goal 3: Community engagement and developer experience

**Outcome:** The community understands and adopts the new agent-callable and remote-data features, developers can build on ITK-SNAP through well-documented interfaces, and sustained outreach grows a pipeline of new users, contributors, and maintainers that strengthens the project's long-term sustainability.

**Milestones & Deliverables:**

- **3.1** Organize and run one or more hybrid (in-person and remote) events in Year 2 — at least one full event combining hands-on training on the new features with a contributor hackathon — with prepared materials and live demos. **[Year 2]**
- **3.2** Produce a series of YouTube video tutorials demonstrating the new agent-callable and remote-data features and common workflows. **[Year 1 & Year 2]**
- **3.3** Maintain a frequent social-media presence (release announcements, feature demos, and tips) to sustain community engagement. **[Year 1 & Year 2]**
- **3.4** Write and publish developer documentation for the headless API, MCP endpoint, and data layer to lower the barrier for external contributors. **[Year 1 & Year 2]**
- **3.5** Prototype community-support agents built on the new agent-callable interfaces — for example, drafting release and feature announcements, and monitoring the user mailing list and issue tracker to summarize community feedback and open well-formed GitHub issues for maintainer triage. **[Year 2]**

**Success indicators:**
- **[Year 2]** At least one hybrid event held with at least 20 participants and post-event feedback collected.
- **[Year 1 & Year 2]** At least 5 video tutorials published with 10,000+ cumulative views, and a regular cadence of social-media posts sustained across both years.
- **[Year 2]** Developer documentation covering the new interfaces published, with at least 5 merged community pull requests or new external contributors.
- **[Year 2]** At least one community-support agent prototyped and used on the project's own channels (e.g., release announcements drafted, or mailing-list feedback triaged into GitHub issues).

---

## Open items / notes for reviser

- **Applicant name & title** must match the submission form exactly.
- **Shared 4.8 release:** ITK-SNAP 4.8 (Year 1) carries both Goal 1's headless API (1.1) and Goal 2's remote data access (2.1). Confirm this single release train, or renumber to distinct versions per goal.
- **"Published roadmap"** wording assumes GitHub Milestones (4.8, 4.10) will be created before submission.
- Final submission format required by OS4LS is **PDF**.

### v6 change-log — Paul's v5 comments, resolved

- **C0 ("greenfield" unfamiliar):** replaced with "extends and connects mature, already-shipping components rather than building from scratch."
- **C1 (don't commit institution):** reframed the cost-share sentence as existing foundations/leverage, not a forward institutional commitment.
- **C2 (vague on event count):** narrative and 3.1 now read "one or more" events; indicator reads "at least one."
- **C3 + C4 (illustrative use cases):** added the Goal 1 "In practice" paragraph covering the review/correction case and the T1/FLAIR inspection case; confirms the headless-until-human MCP model Paul described.
- **C5 (de-emphasize lossless; access-in-place; public data):** dropped "losslessly where the format allows" from the Goal 2 outcome and added the access-in-place + OpenNeuro/Dryad single-URL framing.
- **C6 (explain Flywheel):** added a one-line gloss of what Flywheel is and why it matters, in the Goal 2 outcome.
- **C7 (2.2 ambition + user impact):** rescoped 2.2 to the sequential prompt-save/unload/load design (one active workspace per instance) with the concurrent-in-memory version booked as an exploratory stretch; added the queue-review user impact.
- **C8 (cut repetition):** tightened the success indicators so they state checkable deltas rather than restating milestone text.
- **C9 (community agents):** added milestone 3.5 and a matching success indicator.
- **C10 / C11 (numbers):** kept 20 participants / 5 contributor-PRs / 10,000 views; framed the contributor bar as "merged community pull requests or new external contributors."
- **Note on benchmark:** Paul's v5 said "ACDC"; kept **MM-WHS** here (matches the team's CT+TEE data and the TotalSegmentator served model). Paul did not flag the benchmark.
