# CAIMI26 Q&A sheet

Source of truth for the five-minute Q&A. Each entry is a likely question, a short answer to
say, and where the fact comes from. Entries marked **needs your answer** have no vetted
answer yet.

## Routing and validation

**How does a case get routed to a person?**
It does not yet. A stability check exists and is unit-tested, but nothing calls it; in the
demo a person picked the case. It is the first future direction on the closing slide.
*Source: `itksnap-mcp/src/itksnap_mcp/confidence.py` (`agreement_gate`), re-checked 2026-10-05; submission field 10.*

**Could a vision-language model decide which cases need a person?**
Possibly, but it is untested. We did not find published work that uses one to judge a
segmentation against the CT. Looking at 2D views of a 3D scan, it would probably catch gross
errors, such as a missing organ or a structure leaking into the wrong region, but likely not
subtle boundary errors. The audit records make it testable: each correction marks a proposal
that was wrong, so we can check whether the model's flags match the cases people corrected.
Simpler signals already help: in the demo, the agent flagged very small structures at the edge
of the scan as worth checking.
*If pressed:* sending clinical images to a hosted model raises data-governance questions; a
locally run model avoids them.
*Source: literature search 2026-10-21. Nearest work: [Quality Sentinel](https://arxiv.org/pdf/2406.00327)
(label-quality estimation with text-conditioned features) and non-VLM segmentation quality
control such as SegQC (Medical Image Analysis, 2025) and
[surface-error detection](https://www.sciencedirect.com/science/article/abs/pii/S0010482523007898).
The small-structure note is on screen in beat 3 of the demo video.*

**Has this been validated clinically?**
No. The agent steps ran end to end on 12 public CT scans. One scan was corrected, by me, a
developer. No clinician has used it and there is no clinical data.
*Source: dry-run notes of 2026-07-24 in `~/data/itksnap/caimi-demo-working/README.md`; submission field 8.*

**Was the model trained on the scan you showed?**
No. The scan is case s1248 of the public TotalSegmentator dataset, and it is in that
dataset's test split.
*Source: `01_s1248/meta.json` in the demo data folder.*

**Your abstract says 48 structures and a lung lobe. The video shows the heart and more than sixty structures.**
They are two different scans. The abstract reports an internal research CT. The video uses a
public CT so that it can be shown.
*Source: `caimi-submission/caimi_submitted.md` field 8; the demo data README.*

## The record

**How is the record produced? Did you change every editing tool?**
No tool was changed. ITK-SNAP already keeps data for undo. The record is built from that at
the one point where every edit is committed, so the paintbrush and the agent report the same
way. A unit test covers it without the user interface.
*Source: submission field 7; `design_docs/IMPLEMENTATION.md` section 4.*

**What is in a record?**
The operation, a timestamp, agent or human, voxels changed, the bounding box, and voxel
counts per label before and after.
*Source: submission field 6.*

**Can a person accept or reject a correction?**
Not yet. Today the outcome is implied by whether the file is saved. It should be a
deliberate, recorded action.
*Source: submission field 10.*

**What happens if the tag says "agent" but a person made the edit?**
The tag is set just before the agent's edit and is used up by the next edit. If the agent's
edit changes nothing, the tag can stick to the following edit. It is a known limit.
*Source: `project_retrospective.md` item 1.3.*

## Design

**Why the Model Context Protocol? Does it only work with Claude?**
MCP is an open standard for an assistant to call tools. We used Claude Code in the demo; any
client that speaks the protocol can drive it.
*Source: submission field 7.*

**Why are there two ways to apply, with and without a window?**
We first built the agent to drive a live window. We then added a path that works on the saved
workspace, because only a file can be put down and picked up later. Both are kept, so one
operation has two implementations that must agree.
*Source: submission field 10.*

**Is the channel to ITK-SNAP secure? What about patient data?**
It is a local socket on the same machine, not a network port. Access control has not been
designed. The work uses no clinical data and has no DICOM or archive connection.
*Source: `QLocalServer` in `GUI/Qt/main.cxx` on `sprint/caimi`; the note at the end of `caimi_submitted.md`. Only the listen call was read; socket permissions were not checked.*

**Can this be used commercially? What about the model licences?**
The prototype is open source. Some model weights are not: the nnInteractive weights and
several TotalSegmentator subtasks are non-commercial. That blocks a product, not the
prototype.
*Source: `project_retrospective.md` item 3.3.*

**Would you need vendor support for anything?**
A connection to a clinical archive and a DICOM pathway do not exist yet, and would likely
need it.
*Source: the note at the end of `caimi_submitted.md`.*

## Needs your answer

- **How is this different from MONAI Label or 3D Slicer?**
- **When will this be in a released ITK-SNAP?** It is not in 4.6 and not on the 4.6 roadmap.
- **Who would run the model server in a hospital?**
