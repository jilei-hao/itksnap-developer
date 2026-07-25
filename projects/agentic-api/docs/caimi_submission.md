<!--
⚠️ SUBMITTED 2026-07-25 — this is now the pre-submission DRAFT, not the record.

The submission is complete (ID 2480386). The author made further edits in the portal, so
this file no longer matches what was sent. The authoritative record is:

    ../caimi-submission/caimi_submitted.md    (verified against the portal preview)
    ../caimi-submission/caimi_submitted.docx  (generated from it)

Portal edits not reflected below: original title retained; "Three components, in three
languages." dropped from Tech Stack; bold lead-ins renumbered 1)–4) in fields 9–11; the
last two limitations (dependency conflict; non-commercial weights / no clinical data)
dropped from field 10; "corrections" → "correction records" in field 11.

Keep this file only as the drafting history.
────────────────────────────────────────────────────────────────────────────────
SIIM-CAIMI26 · AI Builder Showcase — submission text, mapped to the ACTUAL portal form
(docs/caimi_submission_form.pdf, captured 2026-07-25).

SOURCE OF TRUTH. caimi_submission.docx is generated from this file — edit here, then run
  python3 build_caimi_submission.py

Form structure differs from docs/caimi-submission-requirements.md §4 (which described a
single 500-word, six-section abstract). The real form is 11 separate fields, each capped at
250 words, in the order below. There is no overall word limit.

Fields marked * are required. "Validation & Evidence" is the only optional one.

Register: objective and measured, per author direction 2026-07-25 — the audience and the
PIs read as scientists, so claims are stated plainly and without promotion, even though the
track is called a "showcase". Avoid superlatives and self-assessment.

Revision 2026-07-25b — incorporates 8 author comments from
caimi_submission.REVIEW-2026-07-25.docx (preserved; comments are not carried into
regenerated .docx files). Notable consequences of those comments:
  · demo is LIVE, not pre-recorded, and applies into a running ITK-SNAP session
  · both operating modes (background workspace + live session) now described in field 6
  · input is any format ITK-SNAP reads, not 3D CT/MR; records are JSON but images are not
    restricted to NIfTI
  · the "most pleased with" paragraph removed from field 6

Revision 2026-07-25c — incorporates 8 further author comments from
caimi_submission.REVIEW2-2026-07-25.docx (preserved). Changes:
  · field 10: opening paragraph rewritten in plainer terms; provenance-tag paragraph
    removed; two new limitations added (no explicit commit/discard of a correction;
    awkward install and scope configuration of the agent server)
  · field 11: restructured as three named beneficiary groups for readability; the
    "for the reviewer" and "none of this requires a change" paragraphs removed;
    "the group" disambiguated; two new impact points added (ITK-SNAP as a step inside
    agent-driven analysis pipelines; the socket and headless interfaces opening the
    application to outside developers)
  · the architecture-reversal paragraph in field 10 was compressed to fit the 250-word
    cap after the two additions — it was the least-requested item in that field

Superseded: docs/abstract.md (the 500-word six-section draft).
-->

# 1. Proposal Title *
<!-- Max 300 characters / 30 words. Form says: "short, specific ... containing no
     abbreviations ... indicates the nature of the presentation."
     19 words / 126 characters. See open item 2 on "ITK-SNAP" and "AI". -->

Making ITK-SNAP Callable by an AI Agent: Expert Correction as a Recorded, Resumable Step in an Automated Segmentation Pipeline

# 2. Current State of Readiness *
<!-- DROPDOWN — options not visible in the captured form. Select the entry closest to: -->

**Working prototype** — demonstrated end to end, open-source, not deployed.

# 3. The Demo: How do you plan to demonstrate this at CAIMI26? *
<!-- DROPDOWN — options not visible in the captured form. Select the entry closest to: -->

**Live demonstration**, with a recorded walkthrough retained as a fallback.

# 4. Briefly describe what attendees will see during your demo. *
<!-- No word counter was visible on this field in the form; kept short deliberately. -->

A live demonstration of a single case, in six steps. First, a chat session with an agent is opened. Second, the agent creates an ITK-SNAP workspace from a selected image. Third, it opens that workspace in an interactive ITK-SNAP session. Fourth, it requests an automatic segmentation from our model server and applies the returned structure into the live session, where the result appears in the image views. Fifth, the proposal is corrected manually with the paintbrush. Sixth, the agent queries the audit records and reports what changed at each step, distinguishing the changes it made from those made by the operator. A recorded walkthrough of the same sequence is available as a fallback.

# 5. Problem & Motivation: What clinical or operational problem does your MVP address? *
<!-- Max 250 words. -->

Automatic segmentation models are increasingly accurate but remain imperfect, so research and clinical pipelines continue to depend on a person to review and correct their output. That review takes place inside an interactive program: the operator opens the image, paints a correction, saves a file, and moves on. The corrected file persists; little else does. No durable record is kept of what was changed, by how much, or by whom.

This has two consequences. First, an automated pipeline has no mechanism for handing a case to a person and receiving a machine-readable result in return. The human step is a discontinuity in the workflow, bridged manually and tracked outside the imaging software. Second, expert corrections are a valuable training signal, and they are routinely discarded: the edit is flattened into a new mask that cannot be distinguished from the model's own output.

We set out to determine whether the human step could be made callable — invoked by a pipeline on the cases that require it, suspended, resumed, and answered in a structured form — without requiring any change to how segmentation is actually performed.

# 6. What You Built: Describe your MVP, tool, or workflow in plain language *
<!-- Max 250 words. -->

We made ITK-SNAP — a 20-year-old open-source segmentation application with over a million downloads — callable by an AI agent, and arranged for every edit to return a structured record of what changed.

It accepts any image format ITK-SNAP can read. It produces an ITK-SNAP workspace containing the segmentation, together with a log of every change made to it.

The agent has roughly a dozen commands: list the available models, create a workspace, request an automatic segmentation, write a proposed structure into the segmentation, open a workspace for a person, set label names and colors, and read back the change log.

It operates in either of two modes. In the first, it works on the saved workspace with no window open, so a pipeline can prepare cases before anyone is involved, and work can be suspended and resumed because all state resides on disk. In the second, it connects to a running ITK-SNAP over a local channel and applies changes into the open session, where the result appears immediately in the image views and can be corrected in place. The same commands are available and the same record is produced in both modes.

Each committed edit returns the same fields: the operation, a timestamp, whether an agent or a person made it, the number of voxels changed, the bounding box of the change, and the voxel counts per label before and after.

# 7. Tech Stack & Development Approach: What tools, frameworks, or methods did you use to build it? *
<!-- Max 250 words. Form asks to be specific and honest. -->

Three components, in three languages.

The agent layer is Python 3.10 or later, packaged as a server for the Model Context Protocol — a standard that allows an assistant to call external tools — using the official SDK. Any client implementing the protocol can drive it; in our demonstration the client is Claude Code. Runtime dependencies are limited to requests, numpy, SimpleITK and PyYAML.

The model layer is a FastAPI server hosting TotalSegmentator, nnInteractive and SAM2 on a CUDA GPU under PyTorch. The agent communicates with it over HTTP.

The application layer is ITK-SNAP itself: C++17, Qt6, ITK and VTK. Two additions were required: a Unix-domain socket carrying newline-delimited JSON-RPC, which allows an external process to communicate with a running window, and the audit record, which resides in the interface-independent logic layer and is covered by a unit test that links against that layer alone. The record is reconstructed at a single commit point from the undo data ITK-SNAP already maintains, so no editing tool required modification.

Workspaces are written by ITK-SNAP's own command-line tool rather than composed in Python. Images may use any format ITK-SNAP supports; records are JSON.

Development followed a timeboxed sprint using Claude Code, gated on two empirical checkpoints before the design was fixed: serving the segmentation model, and demonstrating that an external process could drive a live window. An adversarial code review, supplied with the requirement but not our reasoning, identified four defects in the provenance field.

# 8. Validation & Evidence: Have you done any informal testing or validation? If so, what did you find?
<!-- OPTIONAL field. Max 250 words. -->

No clinical validation has been performed. What follows is bench testing of the mechanism on a single dataset.

The full sequence was executed on a GPU. TotalSegmentator applied to a body CT returned 48 anatomically correct structures. The agent wrote one of them, the left upper lung lobe, into a workspace and read back the record: 1,169,665 voxels changed, bounding box [84,2,0] to [247,189,180], attributed to the agent. A person then opened that workspace and corrected the proposal with the paintbrush. The record returned for the correction carried the same fields with its own values, and differed in the actor field, which read human rather than agent. What was tested is that both producers emit the same schema, not the same measurements.

Two results are worth reporting. First, the single-capture-point design held. A unit test exercises the audit engine against both a plain image type and the run-length-encoded type used in production, and links against the logic layer alone, confirming the record carries no dependency on the user interface. Headless tests over the socket assert exact voxel counts.

Second, the design failed under realistic use in a way we had not anticipated. The initial read-back command reported only the most recent edit, concealing all but the final correction when a person fixed several structures in one session; we had implicitly assumed one correction per case. Records also did not persist when the window was closed. Both have since been corrected.

# 9. Feedback You're Seeking: What specific feedback, help, or collaboration are you hoping to get from the CAIMI26 community? *
<!-- Max 250 words. -->

We are seeking input in four areas.

**Routing.** The system records what changed but does not yet determine which cases require a person. A stability heuristic has been written and unit-tested but is not connected to the pipeline, because we do not know which signal would be trusted in practice. For those who triage automatic segmentations today: what causes you to open a case?

**Record contents.** The record currently carries the operation, timestamp, actor, voxels changed, bounding box, and per-label counts before and after. These fields were chosen by judgment rather than by stated requirement. For retraining or quality auditing, what is missing, and what could be removed?

**Integration.** We would welcome comment from groups running annotation or quality-control workflows at scale on where a callable correction step would sit relative to existing tooling, and whether a workspace file is an appropriate unit of exchange.

**Clinical collaboration.** The correction in our demonstration was made by a developer. The mechanism has been exercised; clinical judgment has not. We are seeking a collaborator who performs this work routinely and can identify failure modes we are not positioned to see.

We would also welcome experience with distributing a Qt-based desktop application through the Python package index.

# 10. Known Limitations & Honest Failures: What isn't working yet, or what have you already tried that failed? *
<!-- Max 250 words. The form calls this "one of the most valuable things you can share." -->

The system cannot yet decide which cases need a person. That decision is the point of the design, but the code for it — a measure of the model's confidence — exists only as a tested function that nothing calls. In the demonstration, a person picks the case.

Corrections are not explicitly committed. After correcting a proposal, the operator has no way to accept or reject it: the outcome is implied by whether the file is saved. Accepting and discarding should be deliberate, recorded actions, and are not yet.

Installing and configuring the agent server is awkward. It can be registered at either project or user scope, and choosing correctly is a manual step most people will get wrong at least once. This should reduce to a single setup command.

The architecture reversed during development. We first built the agent to drive a live ITK-SNAP window, then added the background workspace path and made it the default, because only a saved file can be suspended and resumed. Both are retained, so one operation has two implementations that must stay in agreement.

Installing the Model Context Protocol SDK into the same Python environment as the model server broke the server: the two require incompatible versions of a shared dependency and cannot coexist.

Several of the strongest model weights carry non-commercial licenses. The work involves no clinical data, imaging archive connection, or DICOM pathway, and has been tested on one research CT on one machine.

# 11. Potential for Impact: If this MVP were fully developed and deployed, who would benefit and how? *
<!-- Max 250 words. -->

Three groups would benefit.

**Research groups and clinical services that segment more images than they can inspect.** Their corrections would stop being discarded. At present an expert fix is saved as a new mask, indistinguishable from model output. If every correction records who made it, how large it was, and where, a year of routine review becomes a labeled record of the cases the model gets wrong — training data that is expensive to obtain and seldom collected. The same record answers quality questions that are currently difficult to ask: how often the model is corrected, on which structures, and whether that is changing over time. For trainees, an attributable record of corrections is also a teaching record.

**Groups building agent-driven analysis pipelines.** Automated agents are increasingly used to run image analysis. ITK-SNAP can now sit inside such a pipeline as a step the agent calls directly, rather than a manual detour at the end of it.

**Developers building on ITK-SNAP.** The socket interface and the headless commands open the application to outside control. Others can drive its interface, reuse its logic components, or build tools that work alongside it — which previously meant modifying and rebuilding the application itself.

---

<!-- ─────────  NOT part of any form field  ───────── -->

# Submission links — for the portal's link fields

- Agent code (Python): https://github.com/jilei-hao/itksnap-mcp
- ITK-SNAP fork, audit engine and command channel (C++): https://github.com/jilei-hao/itksnap
- Demo video (YouTube): *[add URL after upload]*

# Demo video (YouTube) — title & description
<!-- Now the fallback recording rather than the primary demo, but still worth publishing
     as supporting material with the submission. -->

**Title** — primary (68 chars, displays in full):

```
Auditable Human-in-the-Loop Segmentation with ITK-SNAP and AI Agents
```

**Description** (copy verbatim into YouTube — paragraphs are unwrapped on purpose; YouTube
does its own wrapping, and hard line breaks look ragged on mobile):

```
An open-source prototype that lets an AI agent call ITK-SNAP as a tool and treats expert human correction as an auditable, resumable step in an automated segmentation pipeline.

In this walkthrough, an agent creates an ITK-SNAP workspace, opens it in a live ITK-SNAP session, requests an automatic segmentation from a model server (TotalSegmentator), and applies the returned structure into the open session. A person then corrects the result with the paintbrush. Every edit, by agent or human, returns a structured record of what changed and who changed it, so corrections become reusable, attributable data.

Code:
• Agent (Python): https://github.com/jilei-hao/itksnap-mcp
• ITK-SNAP fork (C++): https://github.com/jilei-hao/itksnap

Presented at the SIIM-CAIMI26 AI Builder Showcase.
```

# Open items before submitting

1. **Two dropdowns** (fields 2 and 3) — options were not visible in the captured form. Select
   the entries closest to "Working prototype" and "Live demonstration".
2. **"No abbreviations" in the title.** Two remain: *ITK-SNAP* (the software's proper name, not
   an abbreviation of a phrase — defensible) and *AI* (widely understood, and the conference's
   own name expands it). Swap "AI Agent" → "Automated Agent" if a reviewer is likely to be strict.
3. **Rehearse the live path end to end.** Field 4 now describes a live demonstration in which the
   agent applies into a running ITK-SNAP session. Confirm that path runs on the presentation
   machine: `docs/demo_runbook.md` notes the default `apply` is headless, so the live apply must
   go over the socket channel, and no pinned inference seed exists.
4. **Verify the paintbrush claim.** Field 8 states that a person corrected the proposal with the
   paintbrush. `design_docs/media/README.md` still describes the *sample* video's correction as a
   scripted stand-in; `docs/abstract_revisions.md` says a real stroke was being recorded.
5. **Co-authors / affiliation** still marked TO CONFIRM.
6. **Figure and table uploads** — the form captured here has no figure-upload field. Check whether
   uploads live on a later page of the portal before discarding `docs/figures/`.
