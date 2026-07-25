<!--
⚠️ SUPERSEDED 2026-07-25 — DO NOT SUBMIT THIS FILE.

The actual portal form (docs/caimi_submission_form.pdf) is NOT a single 500-word,
six-section abstract. It is 11 separate fields, each capped at 250 words, and it asks
for three things this draft never contained: a tech stack, known limitations / honest
failures, and a description of the demo.

Current submission text:  docs/caimi_submission.md  (source of truth)
                          docs/caimi_submission.docx (generated — do not hand-edit)
Rebuild the .docx with:   python3 docs/build_caimi_submission.py

Kept for reference: the prose below was the basis for the new fields 5, 6, 9 and 11.

────────────────────────────────────────────────────────────────────────────────
SIIM-CAIMI26 · AI Builder Showcase abstract (≤500 words, six sections in order).
Word count excludes title, section headings, and keywords (per submission rules §4).
Not blind — institution/tool names are allowed and used for credibility.
Presenting author: jilei-hao (confirm affiliation / co-authors with Paul before submit).
Body word count (sections only): ~490 after the 2026-07-25 tone/jargon pass; repo/video URLs moved out of the body into the "Submission links" block below — re-verify in portal before submit (limit 500).
-->

# Title
ITK-SNAP as an Agent-Callable Tool: Expert Human Correction as a Resumable, Audited Pipeline Step

# Keywords
human-in-the-loop; interactive segmentation; agentic AI; Model Context Protocol; provenance; foundation models; TotalSegmentator; open-source toolkits

# Problem Statement
Automatic segmentation models are increasingly accurate but still imperfect, so clinical and research pipelines still rely on expert review and correction. Yet that judgment remains confined to interactive software: a person opens an image, paints a fix, and saves a file, while the reasoning and the exact change are lost. An automated pipeline has no direct way to call on an expert as a defined step and receive a result it can read back. Human review is essential in practice yet largely absent from our software interfaces.

# Approach / What You Built
We made ITK-SNAP — a 20-year-old open-source segmentation application with over a million downloads — callable by an AI agent through the Model Context Protocol (MCP), a standard way to connect programs to external tools. The agent runs a segmentation model (TotalSegmentator, hosted on our open itksnap-dls server) and writes its proposal into a saved ITK-SNAP workspace in the background. When a case needs review, the agent reopens that workspace in an interactive session for a person to correct. Every edit, by agent or person, returns a structured record of what changed, not just a saved file (Table 1). Two decisions make this practical. First, the record is captured once, in one format — whether ITK-SNAP is edited in the background or interactively — so none of its eleven editing tools had to change. Second, because all state lives in the workspace file, the step can be paused and resumed: a pipeline can prepare a case before anyone is involved, and the record persists across sessions.

# Demo or Evidence of Function
The code (two open-source repositories) and a short video walkthrough are linked with the submission. We verified the full sequence on a GPU: the agent ran TotalSegmentator on a body CT (48 anatomically correct thoracic structures), wrote one structure into an ITK-SNAP workspace, and read back the record (Table 1). A person opened that workspace in ITK-SNAP and corrected the proposal with the paintbrush; the agent received an identical record automatically labeled as human-made (`actor: human`) — because the agent reads that label, any edit it did not make is attributed to the person (Figure 1).

# Clinical or Operational Impact
Expert review becomes a pipeline step that can be scheduled, paused, and resumed. In a large automated study, a person reviews only uncertain cases, and each correction is recorded — what changed and who made it — in a form reusable to retrain models and audit quality.

# Current Stage
Prototype, open-source, not a product. The propose–apply–record workflow works from start to finish; the correction in the walkthrough was made by a developer, not a clinician, so it tests the mechanism rather than clinical judgment. Routing only low-confidence cases to a person, and a packaged release, are in progress.

# What Feedback You're Seeking
Which fields in the change record matter most for retraining and record-keeping? What confidence measures would you trust to decide between accepting a result and routing it to a person? And where would a callable expert-correction step fit into your existing annotation and quality-control workflows?

---

<!-- ─────────  NOT part of the ≤500-word submission body  ─────────
     Reference material: links go in the portal's dedicated fields; the
     YouTube block is metadata for the video upload, not the abstract. -->

# Submission links — paste into the portal's demo / repo / video fields
- Agent code (Python): https://github.com/jilei-hao/itksnap-mcp
- Audit engine — ITK-SNAP fork (C++): https://github.com/jilei-hao/itksnap
- Demo video (YouTube): _add URL after upload_

# Demo video (YouTube) — title & description

**Title** — primary (68 chars, displays in full):

```
Auditable Human-in-the-Loop Segmentation with ITK-SNAP and AI Agents
```

**Title** — alternative (mirrors the abstract title, more descriptive):

```
ITK-SNAP as an Agent-Callable Tool: Auditable Human Correction in an AI Pipeline
```

**Description** (copy verbatim into YouTube — paragraphs are unwrapped on purpose; YouTube
does its own wrapping, and hard line breaks look ragged on mobile):

```
An open-source prototype that lets an AI agent call ITK-SNAP as a tool and treats expert human correction as an auditable, resumable step in an automated segmentation pipeline.

In this walkthrough, the agent runs an automatic segmentation model (TotalSegmentator) on a body CT and writes the result into a saved ITK-SNAP workspace in the background — with no window open. A person then opens the same workspace in ITK-SNAP and corrects the result with the paintbrush. Every edit, by agent or human, returns a structured record of what changed and who changed it, so corrections become reusable, attributable data.

Code:
• Agent (Python): https://github.com/jilei-hao/itksnap-mcp
• ITK-SNAP fork (C++): https://github.com/jilei-hao/itksnap

Presented at the SIIM-CAIMI26 AI Builder Showcase.
```
