# abstract.md — tightened *Demo* and *Current Stage* text

**Why.** The current *Demo or Evidence of Function* sentence — "**The expert** then corrected the
result in the GUI, and the agent received the same structured record tagged `actor: human`" — makes
two claims that the run did not support: that a *paintbrush correction* happened (it was a scripted
`apply_box` stand-in) and that an *expert* made it. A real stroke is now being recorded, by a
developer rather than a clinician, so only the second claim still needs fixing.

Current body: **456 words** (limit 500). Counts exclude title, headings, and keywords.

---

## Where "expert" is and is not a problem

Exactly one sentence in the abstract makes an **evidentiary** claim about who performed an edit.
Everywhere else, "expert" describes **what the pipeline step is for** — a design claim that stays
true regardless of who drove the demo:

| Location | Wording | Verdict |
|---|---|---|
| Title | "Expert Human Correction as a Resumable, Audited Pipeline Step" | ✅ names the capability, not an observed run |
| Problem Statement | "pipelines depend on expert verification"; "call a human expert as a first-class pipeline step" | ✅ general truth + design intent |
| Approach | "routes it to **a human** who corrects it" | ✅ already neutral |
| **Demo** | "**The expert** then corrected the result in the GUI" | ❌ **the one claim to fix** |
| Impact | "turns expert review into an orchestrable step" | ✅ design claim |

So the fix is one word in one sentence, plus a disclosure in *Current Stage*.

---

## Recommended — real stroke, developer operator

The Demo section states what happened without asserting expertise; *Current Stage* discloses the
operator. Keeping the disclosure out of the Demo section leaves the evidence sentence punchy, and
in this track a stated limitation reads as candour rather than weakness. Also drops the inline JSON
in favour of Table 1, which reads better and pays for the added clause.

**Demo or Evidence of Function** *(103 words, +12)*

> GitHub: github.com/jilei-hao/itksnap-mcp (the Python agent glue and a one-command driver) and
> github.com/jilei-hao/itksnap (the C++ audit engine and command channel); a short video
> walkthrough. Verified live end-to-end on a GPU: the agent ran TotalSegmentator on a body CT
> (48 anatomically correct thoracic structures), applied a chosen structure into the live ITK-SNAP,
> and read back the audit record (Table 1). **A human** then corrected that proposal with the
> paintbrush in the same live session, and the agent received the identical record auto-tagged
> `actor: human` — the agent's commit consumes the tag, so any edit it did not make is attributed
> to the person (Figure 1).

**Current Stage** *(46 words, +19 → body 487, headroom 13)*

> Prototype, open-source, not a product. The propose → apply → audit backbone works end-to-end;
> the correction in the walkthrough was made by a developer, not a clinician, so it exercises the
> mechanism rather than clinical judgment. Confidence-gated routing and a packaged MCP distribution
> are in progress.

> ⚠️ **13 words** of headroom. Portal counters vary on `→`, hyphenated tokens, and URLs — re-count
> in the portal's own field before submitting. If it comes back over 500, cut "and a packaged MCP
> distribution" (−5) or the Demo section's trailing clause from "— the agent's commit…" (−22).

**Alternative placement.** Put the disclosure directly in the Demo section ("A developer — not a
clinician — then corrected…") and leave *Current Stage* as it was. Same honesty, ~19 words cheaper,
but it spends the reviewer's attention on a caveat at the exact moment you want them looking at the
evidence. Recommended only if the word count gets tight.

---

## Fallback — if the recording does not happen at all

Retreat to what was already verified: a second, un-armed commit in the same live session returned
the identical record tagged `human`.

**Demo or Evidence of Function** *(92 words, +1)* — replace the final sentence with:

> A second edit committed in the same live session — one the agent did not arm — came back as the
> identical record, auto-tagged `actor: human`, closing the loop in both directions (Figure 1).

**Current Stage** *(53 words, +26 → body 483)*

> Prototype, open-source, not a product. The propose → apply → audit backbone works end-to-end.
> The human-tagged return path is verified, but the correction in the walkthrough is a scripted
> stand-in for a paintbrush stroke; every editing tool commits through the same audited chokepoint.
> Confidence-gated routing and a packaged MCP distribution are in progress.

---

## Figure 1 needs no change

Its "Human expert" lane names the **role the step exposes**, which is what a flow diagram depicts —
the same reason the title keeps the word. The figure asserts nothing about who drove the recording.
