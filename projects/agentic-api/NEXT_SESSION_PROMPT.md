# Session goal: PLAN (don't build) a UNIFIED two-layer "agentic API" prototype for
# ITK-SNAP, optimized for a set of short pre-recorded demo videos.
# PLANNING ONLY — no implementation, no scaffolding.

## Context
You're at the root of a WRAPPER workspace containing ITK-SNAP and its sibling projects
(including itksnap-dls, and likely greedy/picsl-greedy, SegFlow4D, c3d, etc.), each in a
subdirectory. ITK-SNAP is a mature C++/Qt app for interactive 3D/4D biomedical image
segmentation. I'm writing a grant to make it the programmable, agent-callable
"human-in-the-loop" surface for agentic medical-imaging pipelines.

Thesis: model proposes, human disposes. AI already segments (our shipped `itksnap-dls`
server serves foundation models such as nnInteractive). What NO tool exposes is EXPERT
HUMAN JUDGMENT as a callable, resumable, audited pipeline step an external agent can
invoke. That primitive is the differentiator — NOT headless inference, which is table
stakes. The prototype must make that differentiator tangible ON SCREEN to grant reviewers.

## Target architecture — ONE UNIFIED surface (two layers, one tool namespace)
- LAYER 1 (foundation) — Python API: ITK-SNAP and relevant sibling components callable
  from plain Python (workspaces, labels, segmentation, registration, I/O) with no GUI.
- LAYER 2 (wraps Layer 1) — a generic MCP server exposing ONE coherent tool namespace that
  includes BOTH the headless Layer-1 operations AND "Chrome-MCP-like" operations that drive
  an ACTIVE, RUNNING ITK-SNAP GUI (enumerate UI state, screenshot, select tool/label, act,
  save). The agent sees a single surface; the Python API is the substrate the MCP wraps.
- SESSION LIFECYCLE is explicit and must be designed: some tools need no GUI (pure headless);
  GUI-driving tools require a live ITK-SNAP process the server LAUNCHES/ATTACHES on demand
  (reuse the itksnap-dls "launch a local server/session on demand" pattern). The plan must
  say how the unified surface represents and manages "headless vs. attached-to-live-session"
  state, and how a human takes over the SAME live session for the review/correction step.

## GUI-driving strategy — semantic-first HYBRID (resolve the details from the code)
Primary: SEMANTIC element addressing — stable references via Qt objectName / findChild-style
lookup (address widgets like a DOM), which survives layout changes far better than pixels.
Secondary/fallback: screenshot + coordinate ("computer use") for anything not semantically
addressable. Plan for BOTH and define how they compose.
CRITICAL nuance to investigate, not assume: the actual segmentation editing (scribbles,
seeds, clicks) happens on the OpenGL image canvas, which is NOT a semantically addressable
widget — those are positions in IMAGE/VOXEL space, not screen pixels. So determine whether
edits can be driven through the DATA/API layer in image coordinates (much more robust and
reproducible) and reserve GUI-canvas coordinate interaction for when showing the live canvas
IS the point. Recommend how semantic addressing, coordinate fallback, and image-space API
editing divide the work.

## Demo assets & reproducibility (this is for VIDEO)
- Demo data and a runnable itksnap-dls / nnInteractive model ARE available; more images may
  be added later, so the plan must parameterize over a small dataset (config/manifest), never
  hardcode filenames. Document the EXACT itksnap-dls run/invocation the demo depends on so a
  recording is reproducible.
- Optimize for RE-RECORDABILITY. A pre-recorded, partly agent-driven, live-GUI demo is
  fragile: agent phrasing varies run-to-run, model inference can vary, and live GUI timing is
  flaky. The plan must address how to make each clip deterministic and repeatable for clean
  retakes — e.g., canned/replayable agent scripts instead of free-form prompting where needed,
  fixed seeds / pinned inputs, a scripted "demo driver," and idempotent setup/teardown. Call
  out anywhere non-determinism threatens a take and how to contain it.

## Deliverables (write to docs/agentic-prototype-plan.md; you MAY sketch interface
## signatures/pseudocode, but DO NOT implement or scaffold anything this session)
1. WORKSPACE MAP. Discover the real layout: which sub-projects exist, where each lives,
   language/build system, rough maturity/build status. Locate the ITK-SNAP and itksnap-dls
   roots explicitly; all paths below are relative to those. Confirm how itksnap-dls is run.
2. ORIENTATION REPORT. With REAL file paths + line references, explain how the code actually
   supports (or doesn't): headless/scriptable operation; workspace/label semantics; the
   itksnap-dls client AND the dls server's own API (read it — it's local); any async
   "submit job → poll → return result" machinery (candidate analog for a resumable
   request_review); undo/edit history (audit-trail material); the property/event system;
   Python-binding infrastructure; and CRUCIALLY the scripted GUI test harness (most likely
   existing foundation for Layer 2 — study HOW it finds widgets and injects events, and
   whether it can address the image canvas / inject image-space edits). Correct my notes.
3. CAPABILITY MAP. For every building block each layer needs, mark exists (cite it) /
   thin-wrapper / net-new. Bias toward composing existing code with minimal new code.
4. PROTOTYPE CONCEPTS. 3–5 distinct concepts that showcase the agentic + human-in-the-loop
   value ON VIDEO, each mapping to ONE short clip. RANK them yourself on impact-per-effort;
   don't assume any particular one is the flagship — justify your ranking. For each: what it
   demonstrates, the single visible "wow" beat, Layer-1 vs Layer-2 usage, existing-vs-net-new,
   rough effort, main risk, and how squarely it lands "expert judgment as a callable/
   resumable/audited step." Penalize any concept whose on-screen payoff is just "a model ran."
5. RECOMMENDED MVP + VIDEO SUITE. From your ranking, PICK the flagship and the thinnest
   vertical slice that tells the whole story end to end (agent calls ITK-SNAP as a tool →
   model proposes via itksnap-dls → uncertain cases routed to a human → expert corrects IN
   THE LIVE ITK-SNAP GUI, on camera → structured, audited result flows back) and is visually
   legible. Then design a SUITE OF SHORT CLIPS, ~30–60s each, one capability per clip, sharing
   a through-line so they play as a set OR stand alone (for slides / the full application).
   For each clip: a shot-by-shot storyboard (what's on screen each beat, the agent
   prompt/action, where the human visibly takes over, the closing "callable + resumable +
   audited" payoff) AND its reproducibility recipe (fixed inputs, scripted driver, retake steps).
6. RISKS & OPEN QUESTIONS. Especially: headless operation without a GL/Qt event loop;
   observing/driving a live Qt+OpenGL GUI (screenshotting GL views, addressing the canvas,
   image-space vs pixel edits); the agent→human handoff on one live session; unified session
   lifecycle; recording determinism; Python/native packaging. List what you'd verify before
   committing to the MVP.

## Where to look (MY NOTES — hypotheses; verify against real code and correct me)
Relative to the ITK-SNAP repo root:
- Headless workspace ops:      Logic/WorkspaceAPI/WorkspaceAPI.{h,cxx}
- Headless proof (itksnap-wt): Utilities/Workspace/WorkspaceTool.cxx
- Remote transport:            Logic/WorkspaceAPI/RESTClient.cxx, SSHTunnel.cxx
- DL-server client:            GUI/Model/DeepLearningSegmentationModel.{h,cxx}
- Async ticket pattern:        GUI/Model/DistributedSegmentationModel.{h,cxx}
- Undo/edit history:           Logic/Framework/UndoDataManager.*, IRISApplication
- Qt-free property/event:      Common/PropertyModel.h, SNAPEvents.h
- GUI test harness (Layer 2!): Testing/GUI/Qt/SNAPTestQt.{h,cxx}; --test/--testdir in GUI/Qt/main.cxx
  → does it address widgets by objectName? can it act on the image canvas / inject image-space edits?
- Existing prototypes:         look in prototype/ (I think there's an early itksnap-wt→MCP
  experiment; assess what it does and whether the MVP should extend it)
- Which GUI-Model headers pull in Qt (I believe only the DL model, for threading) — bounds
  how hard a clean headless Layer-1 build is.
In itksnap-dls: read its actual server API (endpoints, session model, nnInteractive prompt
interface) so the plan calls the real thing.

## Principles & constraints
- Integration, not invention: compose shipped components over new subsystems.
- One local, distributable MCP server the client launches; it can drive a live app. No hosted
  service, no per-user cost. Do NOT rebuild model serving — call itksnap-dls.
- The HUMAN correction step is the visual star and is shown in the real GUI, on camera; a
  concept that only shows automation misses the point.
- Demo-scale data (a handful of images) is fine, but everything shown is a real code path.

## How to work
- Explore before proposing; ground every claim in files you actually read and cite paths.
- Don't fabricate APIs, files, or capabilities — if something isn't there, say so.
- Correct my notes explicitly where wrong; I'd rather know.
- Ask me clarifying questions before any consequential assumption; state assumptions you make.
- Output is the plan doc only. Do not implement or scaffold this session.