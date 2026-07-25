# Agentic API sprint — retrospective

**Sprint:** ITK-SNAP as an agent-callable tool (grant Goal 1 prototype)
**Ran:** 2026-07-16 → 2026-07-25 · **Outcome:** submitted to SIIM-CAIMI26 AI Builder
Showcase, ID 2480386, status Complete, preferred presentation Oral.
**Shipped:** `itksnap-mcp` (Python agent server, 9 MCP tools), an ITK-SNAP fork carrying
the audit record and a JSON-RPC socket channel, a demo video, and a submission.

Written after submission, from the repo, the git history, `PROGRESS_LOG.md`, the design
docs, and the submission drafts. Claims about code were re-verified against the source
rather than taken from the log — which turned out to matter (see §4).

---

## 1. Limitations and known issues → next steps

Ordered by how much each one costs us. Tier 1 items undercut a claim we have now made in
public; Tier 2 items are real engineering debt; Tier 3 is what blocks anyone else using this.

### Tier 1 — the gap between what we claim and what runs

**1.1 The confidence gate is not wired to anything.** `agreement_gate` is defined at
`itksnap-mcp/src/itksnap_mcp/confidence.py:54` and is imported nowhere outside its own
test. It is not an MCP tool and no demo path calls it. Verified by grep across `src/` and
`demo/`, not inferred. The routing decision — "call a person only for the uncertain cases"
— is the premise of the whole design, and in the demo a human picks the case.
*Next:* expose it as an MCP tool (`assess` / `route`), have `propose` optionally run the
two-pass perturbation and return a per-label score, and make the demo branch on it. Until
that exists the pitch is a design, not a system.

**1.2 Corrections are never explicitly committed.** After correcting, the operator has no
accept/reject; the outcome is implied by whether the file is saved. This is now in the
submitted limitations and is the most user-visible gap.
*Next:* an explicit commit/discard action in the GUI that writes a terminal record
(`accepted` / `discarded`) into the audit log, so the log states an outcome rather than
leaving it inferred from file mtime.

**1.3 The actor tag can attach to the wrong commit.** The agent-vs-human label is armed
immediately before an edit commits, so a genuine no-op in between carries the tag to the
next commit (`design_docs/IMPLEMENTATION.md` §7). Every provenance claim rests on this field.
*Next:* thread the actor through `StoreUndoPoint`/`Finalize` as an argument, so the tag is
bound to the commit that consumes it rather than to a mutable piece of session state.

**1.4 One structure per apply.** `apply` writes a single structure under a single label;
TotalSegmentator returns 48. The gap between "the model produced a segmentation" and "the
workspace contains it" is currently closed by hand.
*Next:* multi-label apply in one commit — and note this interacts with 1.5, because the
undo-delta reconstruction assumes one constant label per commit.

**1.5 Reconstruction is correct only under an undocumented precondition.** One constant
label per commit; a multi-label overwrite in a single commit would mis-reconstruct
(`IMPLEMENTATION.md` §7). This is a silent-wrong-answer failure, not a crash.
*Next:* assert the precondition at the commit point and fail loudly, before 1.4 makes it
reachable.

### Tier 2 — engineering debt

**2.1 Two implementations of the same operation.** The C++ live path and the Python
headless path both produce the audit record and must stay in agreement. We named this in
the submission; nothing enforces it.
*Next:* a contract test that runs the same edit through both paths and asserts
field-by-field equality of the records. This is the single highest-value test we do not have.

**2.2 The audit log is a 4096-entry ring whose wrap breaks the `since` cursor.** Eviction
of the oldest entries desynchronizes the cursor from the workspace log (`IMPLEMENTATION.md` §7).
*Next:* either persist without a bound, or make the cursor generation-aware so a wrapped
reader gets an explicit "you missed N records" rather than silently skewed results.

**2.3 Geometry is dropped in transport.** `upload_raw` moves voxels without
spacing/origin/direction, worked around client-side with `CopyInformation`. The failure
mode is `changed_voxels: 0` — a silent no-op, documented as a troubleshooting step in
`docs/demo_runbook.md:267`. Cross-grid proposals need resampling that does not exist.
*Next:* carry geometry in the DLS payload; resample when grids differ; make a mismatch an
error rather than a zero.

**2.4 Async inference path never built.** Full-resolution TotalSegmentator is
multi-minute; only the synchronous fast (3 mm) path is demoable, and only on the 8 GB card.
*Next:* move inference onto the existing DLS async-job API.

**2.5 The agent cannot see or enumerate state.** No screenshot binding
(`SaveScreenshot` exists but is not exposed to the JS engine) and no generic state
reflection — an agent reads named getters and cannot ask "what is loaded?".
*Next:* a `describe_state` tool; screenshot binding if we want visual verification.

**2.6 Demo is not reproducible by construction.** No pinned inference seed, `sleep()`-based
waits, hardcoded `/tmp` paths and one absolute home directory in the MCP config.
*Next:* pin the seed, replace sleeps with readiness polls, move paths into config.

### Tier 3 — blocks anyone else running this

**3.1 Install and scope configuration are error-prone** (now in the submitted limitations):
project vs user scope, a fresh session required to see the tools, and a hard trap —
installing the MCP SDK into the DLS environment breaks the server, because `fastapi`
pins `starlette<0.47` and `mcp` needs newer. *Next:* one setup command; separate
environments by default; a preflight that detects the collision and refuses.

**3.2 Reproducibility gap in the repo.** The `itksnap-dls` submodule pointer is
deliberately not recorded in the wrapper, so a fresh clone lands on the wrong branch.
*Next:* record it, or document the switch in the runbook's first step.

**3.3 Model licensing.** nnInteractive weights are CC BY-NC-SA; several TotalSegmentator
subtasks are non-commercial; VISTA3D public weights are NCLS. This blocks productization,
not the prototype. *Next:* decide the commercial path before the tool is promoted.

**3.4 Desktop distribution through pip is unsolved** — PyPI file-size limit, Qt plugin
discovery after relocation, macOS notarization. 3D Slicer deliberately does not ship on
PyPI. *Next:* treat this as a research question, not a packaging chore.

**3.5 No clinical exposure at all.** One research CT, one machine, no DICOM, no imaging
archive, no clinical operator, no IRB. *Next:* a second dataset and a second machine are
cheap and would catch most of the above; a clinical collaborator is the actual ask, and is
now an explicit request in the submission.

---

## 2. Lessons learned — development

**Instrument at the chokepoint, not at the producers.** The best decision in the sprint was
reconstructing the audit record once, at the commit point, from the undo data ITK-SNAP
already maintains. Eleven editing tools produce identical records and not one of them was
modified. The general form: when you need provenance over N producers, find the point they
all funnel through and instrument that; instrumenting N producers is N times the work and
N places to drift. The cost is a precondition (1.5) that must be asserted rather than assumed.

**Independent review earns its keep, and only because it is uncontaminated.** The
`code-reviewer` agent — given the requirement, not our reasoning — found four real defects
in the `actor` field after the author's own verification had passed: actor reset decoupled
from commit creation, stale record after undo, unbounded log, and an over-strong comment.
The isolation is the mechanism, not a formality. Any review that can see the author's
rationale can be talked into agreeing with it.

**Unit tests confirmed the mechanism; only realistic use found the design error.**
`read_audit` answered "what was the last edit?" — which silently hid every correction but
the last when a person fixed several structures in one sitting. The tests passed
throughout, because we had encoded the same wrong assumption (one correction per case) into
them. Tests inherit the author's model of the problem; a session of realistic use is a
different instrument, and we should schedule one per feature rather than relying on the demo.

**Pick the unit of exchange before building the hard part.** We gated the sprint on
"can an external process drive a live GUI?" — genuinely the hardest piece — proved it, then
demoted it when the workspace file turned out to be the better unit, because only a file can
be put down and picked up. The gate answered a feasibility question we did need, but the
architectural question (*what is exchanged?*) was never gated and should have been asked
first. It would have cost an afternoon of thinking and saved the reversal.

**Environment collisions are a first-class design constraint in this ecosystem.** The MCP
SDK and a FastAPI server cannot share a Python environment. Nothing warned us; the model
server simply stopped starting. Agent-side and service-side dependencies should be
separated from day one, by default, on the assumption that they will conflict eventually.

**Tooling hygiene we relearned the hard way.** Backgrounded builds report success
instantly, so smoke tests ran against a not-yet-relinked binary and produced false green —
diagnosed only by noticing the binary's mtime had not moved. `pkill -f <pattern>`
self-matches the invoking shell. Both now live in `NEXT_SESSION_PROMPT.md` as standing
rules, which is the correct home for them.

**"Static-verified only" should be a state a component can be blocked in.** The
TotalSegmentator wrapper was implemented, pushed, and honestly logged as read-but-never-run.
That honesty is good; the gap is that nothing prevented it from being treated as done.

---

## 3. Lessons learned — abstract writing

**Get the actual submission form before writing a word.** We drafted a 500-word,
six-section abstract against `docs/caimi-submission-requirements.md` §4, derived from the
call-for-submissions page. The real form was eleven fields at 250 words each — roughly
2,400 words available, and three required fields we had never drafted: tech stack, known
limitations, and a demo description. A full draft cycle was spent on the wrong shape. The
call page describes the track; only the form defines the submission. Capture it first, even
if it means creating a throwaway submission to see the fields.

**The fields we would not have written ourselves were the strongest.** "Known Limitations &
Honest Failures" produced the most compelling content in the submission — the unwired
confidence gate, the architectural reversal, the four review-caught defects, the dependency
collision. Left to our own structure we would have written none of it. When a venue asks for
candor, take it literally; it differentiates far more than another paragraph of capability.

**The engineering journal is the raw material for the hardest field.** That limitations
section was assembled almost entirely from `PROGRESS_LOG.md`, the design docs' §7 sections,
and commit messages. This is the strongest practical argument for keeping the log current:
it is not bookkeeping, it is the only durable record of the failures that later become the
most credible part of a submission. Where the log had lapsed (§4), the material had to be
recovered from code and commit messages instead.

**Separate what the design does from what the run showed.** `docs/abstract_revisions.md`
exists solely because one sentence claimed an expert had corrected the result when the run
had used a scripted stand-in performed by a developer. The fix was a single word plus a
disclosure. Worth generalizing into a habit: before submitting, mark every sentence as
either a design claim or an evidentiary claim, and check the evidentiary ones against what
was actually executed. Reviewers open linked demos.

**Register is set by the audience, not the venue's self-description.** The track is a
"showcase" and the form invites rough edges, so the first rewrite adopted a candid builder
voice. The actual readers — and the PIs — read as scientists, and the boastful register had
to come out in a later pass. The venue tells you what to include; the audience tells you how
to say it.

**Make the constraint machine-checkable.** Word limits were enforced by a build script that
prints per-field counts and exits non-zero when any field is over. It caught a 266/250
overflow that would otherwise have been trimmed by the portal or by hand at 2 a.m. Anything
a submission portal will silently truncate should be checked locally.

**Keep one source of truth and generate the rest.** Markdown was authoritative; `.docx` was
generated. Review comments arrive in `.docx` and do not survive regeneration, so each round
was: extract comments → apply to markdown → rebuild → archive the commented copy
(`caimi_submission.REVIEW*.docx`). Worth keeping as the standard loop for any
review-by-Word document.

**Record what was actually submitted, separately.** Final edits were made in the portal, so
the draft and the submission diverged. `caimi-submission/caimi_submitted.md` now holds the
as-sent text, verified field-by-field against the portal preview, with the draft marked
superseded. Without that, in six months the draft would be mistaken for the submission.

---

## 4. Does the sprint system need improving?

Short answer: **the pattern is sound and it worked; one thing needs to change, and
metronome's own conventions already say what it is.**

### What worked, on the evidence

The three-file pattern carried a nine-day, many-session sprint across context resets. The
log is 29 KB of dated entries with commit hashes, decisions and their reasons — and it was
directly mineable months-later, which is exactly the promised benefit (§3). The traps
captured in `NEXT_SESSION_PROMPT.md` ("never `pip install mcp` into the DLS base env";
"never `pkill -f` a pattern that matches your own shell") are precisely the artifacts that
justify the ritual. The `code-reviewer` subagent, isolated by design per `conventions.md`,
found four real defects. None of this needs changing.

### The one real failure: the ritual is advisory, so it stopped exactly when it mattered

Verified from git, not from impression:

- Every `checkpoint:` commit from 2026-07-18 through 07-20 also updated `PROGRESS_LOG.md`.
  The ritual was running.
- The five commits on 2026-07-24 — `629ba9b`, `16d82be`, `b8f4599`, `acaaaa6`, `af11bd9` —
  used the `checkpoint:` message convention and touched **zero** sprint-state files.

So the *convention* survived the deadline crunch and the *ritual* did not. The cost is
concrete: `629ba9b` is the workspace-first pivot, the single most consequential design
decision of the sprint, and it appears in no log entry. I recovered it from a commit message
and the code. `PROGRESS_LOG.md`'s "known residuals" still lists a `Redo` issue that
`acaaaa6` fixed, and `docs/sprint_caimi.md`'s status table still reads "not started" for work
that shipped.

This is not a discipline problem to be solved with more discipline. `conventions.md` states
the rule already: *"Any 'must' — commit gates, handoff gates, review gates — is a hook, or
it is a hope."* `/handoff` is a skill — advisory — and it was skipped under deadline
pressure, which is precisely when losing context is most expensive. The system diagnoses its
own gap and has not applied the remedy to itself.

**Recommendation.** A `SessionEnd` (or pre-commit) hook that fails when a `checkpoint:`
commit does not also touch `PROGRESS_LOG.md`. Cheap, deterministic, dependency-free — the
properties `conventions.md` asks of hooks. Not a hook that runs the handoff for you; one
that refuses the checkpoint commit until it has been run.

### Three smaller things

**The fixed filenames are not actually fixed.** `sprint-workflow.md` specifies three files
with fixed names in `projects/<sprint>/`. There is no `SPRINT_PLAN.md` here — the plan lives
at `docs/sprint_caimi.md`. Start-ritual step 2 ("skim `SPRINT_PLAN.md`") therefore silently
no-ops for any session that follows the ritual literally. Either hold the name, or let the
plan be a pointer file. A silent no-op in a start ritual is worse than a missing file.

**Test-as-ratchet has a reachability blind spot.** The rule asks for a test that "would fail
on regression". `agreement_gate` has exactly that — a green unit test that would fail if the
function broke. The function is called by nothing. The ratchet was satisfied while the
feature did not exist in any executable path, and that is the sprint's largest gap (§1.1).
Suggested amendment: a sprint item is done when its behavior is reachable from the product's
entry point *and* covered by a test that fails on regression. Reachability is cheap to check
and would have flagged this on day one.

**Staleness is invisible, and the log's length hides current state.** An append-only 29 KB
journal is right for history and wrong for "where are we now" — the pivot was invisible
because current state lives only in the newest entry, and the newest entry was three days
old. `NEXT_SESSION_PROMPT.md` is meant to carry current state, and it went stale on the same
day for the same reason. A one-line staleness check at handoff — *are there commits newer
than the newest log entry?* — would have caught this and costs nothing.

### Verdict

Keep the pattern. Make the handoff a hook rather than a hope, fix the `SPRINT_PLAN.md`
name mismatch, and add reachability to the done-criterion. Those three changes address every
failure observed in this sprint; nothing else in the system misbehaved.

---

## 5. Carry forward

- [ ] Wire the confidence gate into the MCP surface and the demo (§1.1)
- [ ] Contract test asserting the C++ and Python paths emit identical records (§2.1)
- [ ] Thread the actor through the commit rather than arming it beforehand (§1.3)
- [ ] Explicit accept/discard for corrections (§1.2)
- [ ] One-command install, with a preflight for the MCP/FastAPI environment collision (§3.1)
- [ ] Run the whole flow on a second dataset and a second machine (§3.5)
- [ ] `SessionEnd` hook enforcing the handoff before a `checkpoint:` commit (§4)
- [ ] Rename or redirect `SPRINT_PLAN.md`; add the staleness check to `/handoff` (§4)
- [ ] Before the talk: rehearse the live-apply path end to end; confirm the recorded
      correction shows a real paintbrush stroke, not the scripted stand-in
