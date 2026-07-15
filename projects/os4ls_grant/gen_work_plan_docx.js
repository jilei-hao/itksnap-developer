const {
  Document, Packer, Paragraph, TextRun, AlignmentType, BorderStyle,
  LevelFormat, LineRuleType,
} = require("docx");
const fs = require("fs");

// OS4LS template palette
const CORAL = "e8705a"; // accent — title, field labels, goal titles
const INK = "1c3a3a";   // dark teal — section headings/rules, body, inline labels
const GRAY = "6e6e6e";  // muted — parenthetical notes

// ---- helpers ----
const body = (text) => new Paragraph({
  alignment: AlignmentType.JUSTIFIED,
  spacing: { after: 160, line: 276, lineRule: LineRuleType.AUTO },
  children: [new TextRun({ text })],
});

const sectionHeading = (text, note) => new Paragraph({
  spacing: { before: 320, after: 140 },
  border: { bottom: { style: BorderStyle.SINGLE, color: INK, size: 6, space: 4 } },
  children: [
    new TextRun({ text, bold: true, color: INK, size: 28 }),
    ...(note ? [new TextRun({ text: " " + note, color: GRAY, size: 18 })] : []),
  ],
});

const goalHeading = (text) => new Paragraph({
  spacing: { before: 260, after: 100 },
  children: [new TextRun({ text, bold: true, color: CORAL, size: 24 })],
});

const labelPara = (label, rest) => new Paragraph({
  alignment: AlignmentType.JUSTIFIED,
  spacing: { after: 120, line: 276, lineRule: LineRuleType.AUTO },
  children: [
    new TextRun({ text: label, bold: true }),
    new TextRun({ text: rest }),
  ],
});

const boldLabelOnly = (label, after = 60) => new Paragraph({
  spacing: { after, line: 276, lineRule: LineRuleType.AUTO },
  children: [new TextRun({ text: label, bold: true })],
});

const milestone = (num, text, year) => new Paragraph({
  alignment: AlignmentType.JUSTIFIED,
  spacing: { after: 100, line: 276, lineRule: LineRuleType.AUTO },
  indent: { left: 720, hanging: 360 },
  children: [
    new TextRun({ text: `${num}  `, bold: true }),
    new TextRun({ text }),
    new TextRun({ text: `  ${year}`, bold: true }),
  ],
});

const bullet = (lead, text) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  alignment: AlignmentType.JUSTIFIED,
  spacing: { after: 100, line: 276, lineRule: LineRuleType.AUTO },
  children: [
    new TextRun({ text: lead, bold: true }),
    new TextRun({ text }),
  ],
});

// ---- content ----
const narrative = [
  "ITK-SNAP is a widely used open-source application for interactive segmentation of 3D and 4D biomedical images, developed at the Penn Image Computing and Science Laboratory with a more than 20-year track record, over 11,000 citations, and more than 1.1 million downloads. This request supports a 24-month effort to bring ITK-SNAP's expert-in-the-loop capabilities into AI-native research, organized around the two goals below plus a community engagement activity near the end of Year 2.",
  "Goal 1 exposes ITK-SNAP's toolkit-independent segmentation logic as a headless, scriptable API with a pip-installable Python wrapper and an agent-facing (MCP) endpoint, so agents and data pipelines can invoke expert review as a callable, resumable step (request_review) and capture expert interactions — clicks, scribbles, edits, decisions — as machine-consumable labels and provenance. Goal 2 adds a pluggable explorer for browsing and segmenting datasets in remote and cloud archives without local download, and strengthens interoperability with standard open formats so segmentations move cleanly to and from other tools.",
  "This work sits within our published roadmap. Goal 1 delivers through the ITK-SNAP 4.8 release and builds on our shipped itksnap-dls server, which already serves foundation-model interactive segmentation into the GUI; the headless API generalizes that integration into a stable, agent-callable surface. Goal 2 delivers across the ITK-SNAP 4.8 (Year 1) and 4.10 (Year 2) releases and extends a working remote-access prototype. The effort extends and connects mature, already-shipping components rather than building from scratch, is well suited to AI-assisted development, and is validated against ITK-SNAP's existing automated test harness.",
  "The work builds on substantial existing foundations — the lead maintainer's established role in the project, mature continuous-integration and test infrastructure, and the codebases the effort extends (ITK-SNAP, itksnap-dls, greedy, Convert3D). The team has a proven track record delivering initiatives funded by CZI EOSS and the NIH.",
  "We will pair development with sustained community engagement. Near the end of Year 2, once the new agent-callable and remote-data features have shipped, we will run one or more hybrid (in-person and remote) events that combine hands-on training with a contributor hackathon, targeting ITK-SNAP's core audience of clinical and imaging researchers and developers of adjacent pipeline tools. Throughout the grant we will also publish a series of YouTube video tutorials, maintain a frequent social-media presence, and expand developer documentation for the new interfaces — to drive adoption, gather feedback, and onboard new contributors and maintainers.",
  "All code will be developed in the open under ITK-SNAP's existing open-source license (GPL-3.0), with releases published through our established channels and the Python wrapper published to PyPI.",
];

const children = [];

// Title block
children.push(new Paragraph({
  spacing: { after: 80 },
  children: [new TextRun({ text: "Open Source for the Life Sciences (OS4LS)", bold: true, color: CORAL, size: 28 })],
}));
children.push(new Paragraph({
  spacing: { after: 40 },
  children: [new TextRun({ text: "Proposal Title: ", bold: true, color: CORAL }), new TextRun({ text: "ITK-SNAP: Human-in-the-Loop AI Image Segmentation" })],
}));
children.push(new Paragraph({
  spacing: { after: 120 },
  children: [new TextRun({ text: "Applicant Name: ", bold: true, color: CORAL }), new TextRun({ text: "Paul Yushkevich" })],
}));

// Work Plan narrative
children.push(sectionHeading("Work Plan", "(max 750 words)"));
narrative.forEach((p) => children.push(body(p)));

// Goals
children.push(sectionHeading("Goals, Outcomes, Milestones and Deliverables"));
children.push(new Paragraph({
  spacing: { after: 120 },
  children: [new TextRun({ text: "(up to 5 goals; not included in the 750-word limit)", italics: true, color: GRAY })],
}));

// Goal 1
children.push(goalHeading("Goal 1: Composable human-in-the-loop core (LOI Aim 1)"));
children.push(labelPara("Outcome: ", "Agents and data pipelines can call ITK-SNAP's expert-review capabilities directly through a stable interface, so expert verification and correction becomes a first-class, resumable, orchestrable pipeline step — the model proposes and the human adjudicates — and the resulting expert judgments feed back into model improvement."));
children.push(body("In practice, an agent processing a dataset runs ITK-SNAP's segmentation headlessly and, when a case needs human judgment, calls request_review — launching ITK-SNAP on the user's machine with the images and the model's proposed segmentation loaded; the expert accepts or corrects it, and the agent resumes with the corrected label and a record of what changed. The same mechanism serves lighter-weight inspection: an agent that suspects misregistration between a subject's T1 and FLAIR can open both, correctly overlaid with the cursor at the location of interest, for a quick human look — extending ITK-SNAP's existing workspace and URL concepts into an agent-callable surface."));
children.push(boldLabelOnly("Milestones & Deliverables:"));
children.push(milestone("1.1", "Release ITK-SNAP 4.8 with a headless, scriptable API (pip-installable wrapper and agent-facing MCP endpoint) providing agent-callable segmentation and the request_review resumable review primitive.", "[Year 1]"));
children.push(milestone("1.2", "Ship the expert-interaction capture format: each request_review correction is recorded as a machine-consumable record — the model's proposal, the expert's interactions and corrected label, plus case metadata, identity, and timestamp — using a documented, reusable schema (aligned with established provenance conventions where practical).", "[Year 2]"));
children.push(milestone("1.3", "Using the captured records, evaluate the value of expert-in-the-loop correction on at least one public benchmark dataset: fine-tune a served foundation model on expert-corrected cases and report the change in segmentation accuracy (standard overlap and boundary metrics) relative to the uncorrected baseline; and assess whether routing uncertain cases to the expert improves annotation efficiency versus random case selection. Release the evaluation harness and protocol as open source.", "[Year 2]"));
children.push(boldLabelOnly("Success indicators:", 100));
children.push(bullet("[Year 1]  ", "ITK-SNAP 4.8 released; agent-callable segmentation and request_review pass the existing automated test harness."));
children.push(bullet("[Year 2]  ", "Expert interactions captured as provenance-tagged records spanning at least one anatomy/modality; on at least one public benchmark (e.g., MM-WHS cardiac CT and/or the Medical Segmentation Decathlon hippocampus task), fine-tuning on expert-corrected cases yields a measurable improvement over the uncorrected baseline (overlap and boundary metrics, magnitude reported), and routing uncertain cases to the expert shows improved annotation efficiency versus random selection; evaluation harness, protocol, and record schema released open source."));

// Goal 2
children.push(goalHeading("Goal 2: Remote data access and open-format interoperability (LOI Aim 2)"));
children.push(labelPara("Outcome: ", "Users and agents browse and segment imaging datasets where they live — in remote and cloud archives — without downloading and manually rearranging files, and segmentations move faithfully between ITK-SNAP and the rest of the ecosystem, making ITK-SNAP the human checkpoint inside larger pipelines. This spans institutional platforms such as Flywheel — a data-management system used widely across imaging research, where studies sit behind an API rather than as loose files — and public repositories: a dataset published on OpenNeuro or Dryad could be opened in ITK-SNAP from a single URL, replacing today's download-and-arrange workflow."));
children.push(boldLabelOnly("Milestones & Deliverables:"));
children.push(milestone("2.1", "Release ITK-SNAP 4.8 with an agent-callable remote data-access feature and a file-explorer UI (local filesystem, remote Linux via SSH, and Flywheel; DICOM-aware, with BIDS support where applicable).", "[Year 1]"));
children.push(milestone("2.2", "Add explorer- and agent-driven workspace navigation: opening a workspace from the explorer prompts to save the current one, then unloads and loads the selected workspace (one active workspace per instance), so a reviewer or agent can move through a queue of cases without hunting through file dialogs. As an exploratory stretch, evaluate keeping multiple workspaces resident for fast switching, contingent on relaxing the single-active-session assumption.", "[Year 2]"));
children.push(milestone("2.3", "Release ITK-SNAP 4.10 with improved interoperability for interchange of segmentations with standard open formats (e.g., DICOM-SEG), with round-trip fidelity validated and any limitations documented.", "[Year 2]"));
children.push(boldLabelOnly("Success indicators:", 100));
children.push(bullet("[Year 1]  ", "ITK-SNAP 4.8 released with remote data access; a remote dataset browsed and segmented without local download, and a public dataset (e.g., OpenNeuro or Dryad) opened from a single URL."));
children.push(bullet("[Year 2]  ", "ITK-SNAP 4.10 released with explorer- and agent-driven workspace navigation (queue-style case switching), and round-trip interchange of segmentations (e.g., DICOM-SEG) validated against at least one external tool such as 3D Slicer, with fidelity documented."));

// Goal 3
children.push(goalHeading("Goal 3: Community engagement and developer experience"));
children.push(labelPara("Outcome: ", "The community understands and adopts the new agent-callable and remote-data features, developers can build on ITK-SNAP through well-documented interfaces, and sustained outreach grows a pipeline of new users, contributors, and maintainers that strengthens the project's long-term sustainability."));
children.push(boldLabelOnly("Milestones & Deliverables:"));
children.push(milestone("3.1", "Organize and run one or more hybrid (in-person and remote) events in Year 2 — at least one full event combining hands-on training on the new features with a contributor hackathon — with prepared materials and live demos.", "[Year 2]"));
children.push(milestone("3.2", "Produce a series of YouTube video tutorials demonstrating the new agent-callable and remote-data features and common workflows.", "[Year 1 & Year 2]"));
children.push(milestone("3.3", "Maintain a frequent social-media presence (release announcements, feature demos, and tips) to sustain community engagement.", "[Year 1 & Year 2]"));
children.push(milestone("3.4", "Write and publish developer documentation for the headless API, MCP endpoint, and data layer to lower the barrier for external contributors.", "[Year 1 & Year 2]"));
children.push(milestone("3.5", "Prototype community-support agents built on the new agent-callable interfaces — for example, drafting release and feature announcements, and monitoring the user mailing list and issue tracker to summarize community feedback and open well-formed GitHub issues for maintainer triage.", "[Year 2]"));
children.push(boldLabelOnly("Success indicators:", 100));
children.push(bullet("[Year 2]  ", "At least one hybrid event held with at least 20 participants and post-event feedback collected."));
children.push(bullet("[Year 1 & Year 2]  ", "At least 5 video tutorials published with 10,000+ cumulative views, and a regular cadence of social-media posts sustained across both years."));
children.push(bullet("[Year 2]  ", "Developer documentation covering the new interfaces published, with at least 5 merged community pull requests or new external contributors."));
children.push(bullet("[Year 2]  ", "At least one community-support agent prototyped and used on the project's own channels (e.g., release announcements drafted, or mailing-list feedback triaged into GitHub issues)."));

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22, color: INK } } },
  },
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: "●", alignment: AlignmentType.LEFT,
        style: { paragraphProperties: { indent: { left: 720, hanging: 360 } } },
        run: { font: "Arial", size: 22, color: INK },
      }],
    }],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("OS4LS_Work_Plan_ITK-SNAP_v6.docx", buf);
  console.log("wrote OS4LS_Work_Plan_ITK-SNAP_v6.docx", buf.length, "bytes");
});
