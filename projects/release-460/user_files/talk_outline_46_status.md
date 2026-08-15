# ITK-SNAP 4.6 — status update to the lab (v2)

**Audience:** cardiac-focused **users**. Not developers. No engineering content except where it
changes what they can do.
**Format:** ~25 min slides + ~5 min pre-recorded demo, then a 2 min "one more thing" · **14 slides**
**Runs long:** the closer adds ~4 min, so budget ~34 min or cut per the last section.

---

## Arc in one line

*4.6 already lets you open data straight from a URL and gives you two AI segmentation models today —
and the next wave of work is aimed squarely at cardiac.*

---

## S1 — Title (0:00–0:30)

ITK-SNAP 4.6 — where it stands. Version on trunk is `4.6.0-alpha.1`.

## S2 — The one-slide answer (0:30–3:00)

Three bullets, user-facing, no hedging:
- **What's already in:** open images and workspaces straight from a URL, and two AI-assisted
  segmentation models.
- **What's coming, cardiac-first:** propagation across phases, 4D cardiac I/O, one-button automatic
  segmentation, mesh tooling.
- **No release date yet.** Say it plainly here so nobody spends the talk waiting for one.

> **Note:** the old version of this slide counted workstreams. Users don't care how the work is
> organised — they care what they'll be able to do. Same honesty, user's vocabulary.

---

## S3 — Headline: open data straight from a URL (3:00–8:00)

The biggest block of work in 4.6, and it's **done and merged**. ITK-SNAP opens images *and whole
workspaces* from a URL:
- `scp://` / `sftp://` — with a connection pool, so a multi-layer workspace doesn't re-authenticate
  once per layer
- `http(s)://` — public datasets, with caching
- **`fw://` — Flywheel**, with API-key auto-load
- Persistent local cache — the second open is instant
- Click a `itksnap-fw://` link in a browser or email and it opens in a running ITK-SNAP

**The point for this room:** your study data stays where it lives. No download step, no local copy
that drifts out of sync with the server.

> Spend real time here. It's the most immediately useful thing in the release for anyone whose data
> is on a server or in Flywheel.

---

## S4 — AI-assisted segmentation: what you have today (8:00–13:00)

**Two models ship today. They are not interchangeable — this is the "which do I use?" slide.**

| | **nnInteractive** | **SAM2** |
|---|---|---|
| Works in | **3D** — scribble one slice, get the whole structure | **2D** — one slice at a time |
| You give it | point, box, **scribble** (paintbrush), **lasso** (polygon) | a **point** |
| Image type | grayscale | grayscale or colour |
| Trained on | **medical images** (DKFZ, nnU-Net lineage) | natural images and video (Meta) |
| Origin | Isensee et al., 2025 | `sam2.1-hiera-large` |

**Recommendation, say it outright: for cardiac chambers and myocardium, use nnInteractive.** It is
3D-native and medically trained — a scribble on one short-axis slice propagates through the stack.
SAM2 is a 2D point-prompt model; it's the right tool for colour or essentially-2D data, not for a
3D chamber.

How you actually use nnInteractive: draw with the **AI paintbrush** (left button = include, right
button = exclude), or turn on **AI mode for the polygon tool** and your outline becomes a lasso
prompt. Changing the active label resets the interaction — as if starting a new structure.

> If you show one screenshot on this slide, make it the scribble→3D one from the DLS docs.

---

## S5 — Everything else that landed (13:00–15:00)

Fast, one line each:
- **Window menu** listing every running ITK-SNAP; **Send to Other Window** between instances
- **Cancel** a running task from the X in the progress overlay
- `.vti` / `.vtp` I/O and **`.seq.nrrd` export** — contributed from our fork
- A clear **out-of-memory dialog** on oversized images instead of a hard failure

## S6 — Stability (15:00–16:30)

Since 4.4: **24 bugfixes**, including 9 memory leaks, a DLS server connection race, and two
long-standing DICOM crash/hang bugs. Two crashes found and fixed in the last week alone, one of them
a regression that had been hiding since March.

**One bullet on the engineering, no more:** a lot of this was found by pointing AI coding agents at
the codebase and at our own crash logs — including a bug that had been dormant for years. Then move
on.

---

## S7 — What's coming: cardiac first (16:30–21:00)

**This is the slide the room came for.** Lead with the four that matter to them, then round out the
list. Say for each: what it does, and what it's waiting on.

**Cardiac-relevant, in priority order:**

1. **Segmentation propagation across phases** — segment one cardiac phase, propagate to the rest.
   *Waiting on: the segmentation server refactor.*
2. **4D cardiac I/O** — proper phase/time handling for cine CTA and echo, and sequence export.
   *Status: written and working on a branch; merge decisions pending.* **Do not say "shipping."**
3. **cmesh integration** — the mesh library becomes a proper dependency, so mesh operations get
   faster and more consistent. *Waiting on: a release tag.*
4. **One-button automatic segmentation** — pick a model, press once, get labeled cardiac anatomy
   with no prompts at all. *Waiting on: the same server refactor as (1).*

**Also on the list, briefly:** free-rotation 2D/3D sync (a bug — clicking the 3D mesh should move
the 2D cursor to the right voxel), developer documentation and governance, and a rolling bugfix
stream.

**The one dependency worth stating out loud:** propagation and automatic segmentation are both
waiting on the same piece of server work. It's already written — it needs promoting, not inventing.
That single item unblocks the two most visible cardiac features.

---

## S8 — What propagation will look like (21:00–22:30)

Show `mockup_propagation.svg`. Talk over it:

> "Segment phase 1 by hand. Press Propagate. Every remaining phase is filled in — running on the
> server, with progress, and you can cancel it."

Keep the **CONCEPT MOCK-UP** banner visible. Do not let anyone leave thinking this exists.

## S9 — What automatic segmentation will look like (22:30–24:00)

Show `mockup_auto_segmentation.svg`. Talk over it:

> "Open the image. Pick a model. Press Segment. You get labeled cardiac anatomy with real names and
> colours — LV myocardium, LV blood pool, RV, atria, aorta — no scribbles, no seed points."

The model behind this is **TotalSegmentator**, which is written and on a branch today.

---

## S10 — Demo intro (24:00–24:30)

Say it's pre-recorded **because it's a network feature** — you're not gambling a live SSH handshake
on room wifi. Reads as judgment, not evasion.

## S11 — Play the recording (24:30–29:30)

Shot list below.

## S12 — Close (29:30–30:00)

- Next up: the server refactor, which unblocks propagation and automatic segmentation.
- **Asks of the room:** anyone using Flywheel — try the `fw://` path and tell me what breaks; and
  I want cardiac datasets to test propagation against.
- No date; next checkpoint is that server work landing.

---

## S13 — "One more thing…" (30:00–30:15)

A single line on a cherry field. **Pause. Do not talk over it.** The whole value of the beat is the
silence before the reveal.

## S14 — ITK-SNAP, callable by an AI agent (30:15–34:00)

*Model proposes, human disposes.* An AI agent drives ITK-SNAP over the Model Context Protocol —
opens a study, runs a model, applies a segmentation, hands the uncertain cases to a person. And
every edit comes back as a structured record of **what changed and who changed it** — the agent, or
you.

Then play the demo (~2 min, three clips):

| | Clip | Time |
|---|---|---|
| 1 | The agent calls ITK-SNAP as a tool | 45 s |
| 2 | **Model proposes, human disposes — the live handoff** | 60 s |
| 3 | The correction is a return value | 30 s |

**Clip 2 is the star.** If you are short on time, play only that one.

### Accuracy — this slide has three ways to go wrong

1. **It is submitted, not accepted.** Notification is 26 August, *after* this talk. Never say
   "accepted" or "we're presenting at CAIMI."
2. **It is not in 4.6 and not on the 4.6 roadmap.** Say so out loud, or the room will read it as a
   competing priority against the cardiac features you just promised.
3. **If asked how a case gets routed to a human:** the confidence gate is implemented and
   unit-tested but **not yet wired into the flow** — today a person still chooses. That is the next
   increment. Say it plainly; it is the question the work invites.

---

# Demo shot list (~5 min)

Record readable, cursor highlighting on, and **cut the dead time** — nobody should watch a real
download bar.

| # | Shot | Time | Point |
|---|---|---|---|
| 1 | Paste an `itksnap-fw://` (or `sftp://`) URL — image opens, no download step | 1:15 | The headline. Strongest shot first. |
| 2 | Progress overlay during load; hit **X** to cancel mid-download | 0:30 | New in 4.6; UI never freezes |
| 3 | Open a *workspace* from a URL — several layers, one connection | 0:45 | The real clinical case |
| 4 | **nnInteractive**: scribble on one short-axis slice → 3D chamber | 1:30 | The AI story as it exists today. **Make this cardiac data.** |
| 5 | Second instance; **Window** menu; *Send to Other Window* | 0:30 | Multi-instance |
| 6 | Re-open the same remote image — instant, from cache | 0:20 | Nice closing beat |

**Recording notes**
- Scrub credentials and PHI: Flywheel API key, hostnames, patient IDs in filenames or layer nicknames.
- Shot 4 carries the talk for this audience — use real cardiac data and rehearse it twice.
- If a shot fails on recording day, cut it rather than shipping a slow take.

---

# Accuracy traps — things not to say

1. **4D cardiac I/O is not in 4.6 yet.** It's on a branch; merge decisions are pending. Highlight it
   as coming, never as shipping. This is the easiest slip to make with this audience.
2. **Automatic segmentation (TotalSegmentator) is not available today.** nnInteractive and SAM2 are;
   TotalSegmentator is on a branch. Don't blur the three together.
3. **Don't promise dates for propagation or automatic segmentation.** Both wait on the same
   unstarted server work.
4. **Keep the MOCK-UP banners on S8 and S9.** Mock-ups shown to users become expectations.
5. **Count the memory-leak fixes once** — 9, not 11; two pairs are duplicates from a rebase.
6. **Don't quote a test pass rate.** Three runs on the same code gave three different numbers
   because a network test flakes. If it comes up: "no failure that isn't a known flake."

---

# If you're short on time

With the closer the deck runs ~34 min. To get back to 30: cut **S5** entirely, **S6** to a single
line, and play only clip 2 of the agentic demo. Do not cut S4 (the model comparison) or S7 (cardiac
roadmap) — those carry information this room can't get anywhere else. And do not cut S13; a reveal
without the pause is just another slide.
