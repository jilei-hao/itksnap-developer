# RESUME — ITK-SNAP Agentic API · CAIMI26 talk, rehearsal

## Current state (read this paragraph first)

The CAIMI26 talk is **built, uploaded and frozen**. Slot: AI Builder Showcase, Session 1007,
**Mon 2026-10-26, 4:30 PM ET**, Smilow Center, Penn. **7 minutes + 5 minutes Q&A**, run from a
Penn Windows PC. Jilei uploaded the 5-slide deck and the 3:50 demo MP4 on 2026-10-21. The video
plays on its own between slides 3 and 4, not from a slide. Everything lives in
`projects/agentic-api/presentation/`. The `.md` files are the source of truth: `talk.md`
(slides + spoken script) → `build.py` → deck and `build/script.html`; `video.md` →
`build_video.py` → MP4. Since 2026-10-22 `frozen.json` makes the builds refuse any change the
audience would see. **Only the spoken text (`### Say`, `### Beat`), slide times and `pace` may
change.** The plan is 6:50 of 7:00.

## The next goal (Jilei's choice, named 2026-10-22)

**Tweak and rehearse the spoken script.** Work in `talk.md` (`### Say` blocks and the video's
`### Beat` blocks), rebuild with `python3 build.py`, and rehearse from `build/script.html`. Ask
Jilei what to start with: which slide or beat feels off, or a timed run-through first.

## Other open items (reminders, not a priority order)

**Talk logistics**
- Confirm the email to Anna Zawacki said "Prerecorded Demo" (the upload is done).
- Play the uploaded deck and MP4 on the Windows machine. Practise slide 3 → video → slide 4.
- `qa.md` has three "Needs your answer" questions: how this differs from MONAI Label / 3D Slicer;
  when it reaches a released ITK-SNAP (it is not in 4.6); who runs the model server in a hospital.
- Optional: a printable script. Nothing produces a .docx today; `build/script.html` prints
  cleanly. If Word is wanted, generate it from `talk.md` in `build.py`; do not hand-write it.

**Agentic API, after the talk** (from `project_retrospective.md`; none started)
- Wire the confidence gate (`itksnap-mcp/src/itksnap_mcp/confidence.py`, `agreement_gate`); it is
  still called by nothing. This is future direction 1 on the closing slide.
- Explicit accept/discard of a correction (Q&A answer: "not yet").
- A dedicated demo build. `build-release/` is now `staging/v460` and lacks `--agent-listen`, the
  audit code and the `itksnap-wt` label commands, so the live demo cannot run on this Mac
  until `sprint/caimi` (or its six agentic commits, which apply cleanly to `upstream/master`) is
  built in its own directory.
- Repoint or remove the broken `itksnap-wt` MCP registration in `~/.claude.json`; it points at
  a deleted file.

## Files to read first (in order)

1. `presentation/README.md`: the folder's rule, the freeze, the build commands, the organisers'
   requirements, the to-do list.
2. `presentation/talk.md`: the whole talk. `build/script.html` is the same text with a running
   clock.
3. `presentation/qa.md`: the answers to have ready.
4. `PROGRESS_LOG.md`, newest entry (2026-10-05 → 10-22): how the talk got here and what broke.

## Commands

```bash
cd projects/agentic-api/presentation
python3 build.py              # deck + script.html; prints the timing table; fails on frozen-content edits
python3 build_video.py --stills   # only if build/ was cleaned (the slide 2 image); the full video build is refused while frozen
```

`python3` is the default conda base on this Mac; it has `python-pptx`, `Pillow` and
`reportlab`. ffmpeg comes from Homebrew.

## Known traps

- **The slides and video are frozen.** If `build.py` stops with "frozen", the edit touched
  on-slide text: undo it. To truly change a slide, delete `frozen.json`, rebuild, re-upload,
  then run `python3 build.py --freeze` again. The uploaded originals are in
  `presentation/final/uploaded_2026-10-21/`.
- **The uploaded deck keeps the speaker notes from upload day.** Script tweaks reach
  `build/script.html` and the local deck's notes, not the copy on the podium PC. Rehearse from
  `script.html`.
- **Never edit `build/` by hand.** If Jilei comments in or edits the PPTX, a rebuild overwrites
  it. First copy it to `presentation/review/` with the date in the name, diff its text against a
  fresh build, and carry the changes into `talk.md`. Watch for a `~$…pptx` lock file in `build/`:
  it means PowerPoint has the deck open.
- **Pace:** `build.py` fails if any part needs more than `pace` (150) words per minute. Slide 3
  is the densest at about 128.
- **Language is neutral on purpose** (Jilei): no years or download counts, no selling points, no
  questions to the audience. Keep script tweaks in that register.
- **The repo is public.** The acceptance email (it holds a private upload link), the SIIM
  template, `review/` and `final/` stay out of git, enforced by `presentation/.gitignore`.
- **The footage still shows SAM2** in beat 1's model table. SAM2 is being dropped from the DLS;
  the narration avoids naming or counting the models.
- **Poppins (the template font) is not installed on this Mac.** LibreOffice previews use a
  substitute. Check fit with a Verdana-substituted copy, the conservative case.
