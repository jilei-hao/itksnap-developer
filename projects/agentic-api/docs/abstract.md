<!--
SIIM-CAIMI26 · AI Builder Showcase abstract (≤500 words, six sections in order).
Word count excludes title, section headings, and keywords (per submission rules §4).
Not blind — institution/tool names are allowed and used for credibility.
Presenting author: jilei-hao (confirm affiliation / co-authors with Paul before submit).
Body word count (sections only): ~470 — re-verify before submit (limit 500).
-->

# Title
ITK-SNAP as an Agent-Callable Tool: Expert Human Correction as a Resumable, Audited Pipeline Step

# Keywords
human-in-the-loop; interactive segmentation; agentic AI; Model Context Protocol; provenance; foundation models; TotalSegmentator; open-source toolkits

# Problem Statement
Automatic segmentation models are increasingly capable but still imperfect, so clinical and research pipelines depend on expert verification and correction. Yet that expert judgment is trapped inside interactive GUIs: a person opens an image, paints a fix, and saves a file — the reasoning and the exact change evaporate. An automated pipeline or AI agent has no clean way to *call* a human expert as a first-class pipeline step and receive a machine-consumable answer back. The human-in-the-loop is real in practice but missing from our software interfaces.

# Approach / What You Built
We exposed ITK-SNAP — a 20-year, open-source segmentation application with over a million downloads — as an agent-callable tool via the Model Context Protocol (MCP). An external agent runs automatic segmentation (TotalSegmentator, served by our open itksnap-dls model server) and, for a case that needs review, routes it to a human who corrects it in the running ITK-SNAP. The correction returns not as an opaque file but as a structured audit record: operation, actor (agent vs. human), changed-voxel count, bounding box, before/after label counts, and timestamp. Two design choices make this practical. First, the audit record is *reconstructed* from ITK-SNAP's existing undo delta at commit time (old = new − delta), so provenance is captured in one place with no change to the eleven editing tools. Second, a new live command channel — a local-socket JSON-RPC server running on the GUI thread — drives the same live ITK-SNAP the human sees, so every agent action takes the identical code path a mouse click would.

# Demo or Evidence of Function
GitHub: github.com/jilei-hao/itksnap-mcp (the Python agent glue and a one-command driver) and github.com/jilei-hao/itksnap (the C++ audit engine and command channel); a short video walkthrough. Verified live end-to-end on a GPU: the agent ran TotalSegmentator on a body CT (48 anatomically correct thoracic structures), applied a chosen structure into the live ITK-SNAP, and read back the audit record — for example `{actor: agent, changed_voxels: 1169665, bbox: [[84,2,0],[247,189,180]], before: {0: …}, after: {1: …}}`. The expert then corrected the result in the GUI, and the agent received the same structured record tagged `actor: human`.

# Clinical or Operational Impact
This turns expert review into an orchestrable, resumable pipeline step. Inside a large automated cohort, a human becomes a callable checkpoint invoked only for uncertain cases, and every correction is captured as reusable, attributable provenance — labeled by who made it — that can feed model fine-tuning and quality auditing.

# Current Stage
Prototype. The propose → apply → audit backbone works and is open-source; it is not a product. Confidence-gated routing and a packaged MCP distribution are in progress.

# What Feedback You're Seeking
Which audit-record fields matter most for downstream model fine-tuning and provenance? What confidence signals do you trust to decide auto-accept versus route-to-human? And where would a callable expert-correction step plug into your existing annotation and quality-assurance workflows?
