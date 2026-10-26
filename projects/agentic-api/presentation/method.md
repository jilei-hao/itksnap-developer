# How the CAIMI26 agentic-API talk was built: the method

Written 2026-10-23 for a second talk at SIIM-CAIMI26. That talk has more slides and less video, so
the video section is marked optional. Everything here comes from this folder: read `README.md`
(files, build, the organisers' rules), `talk.md` (the source format) and `build.py` (the checks)
for the details.

## 1. The rule: markdown is the source, everything else is built

- **One `.md` per product.** `talk.md` holds the slides, their times and the spoken script.
  `video.md` holds the video's cut list (optional). `qa.md` holds likely questions and vetted
  answers.
- **`python3 build.py` builds everything else:**
  - the deck, with speaker notes;
  - `build/script.html`, the script plus a rehearsal clock;
  - `build/<name>_script.docx`, the script for review in Word.

  Never edit `build/` by hand.
- **The build fails on:** more slides than allowed, a plan over the slot, any part that needs
  faster speech than `pace`, and (with a video) beats that don't match the cut. These checks
  kept the timing honest.
- **Edits made in PowerPoint or Word:** first copy the file into `review/` with the date in its
  name, because the next build overwrites `build/`. Then carry the changes into the `.md` and
  rebuild. A `~$…` file in `build/` means PowerPoint has the deck open.
- **After the upload:** `python3 build.py --freeze` writes `frozen.json`. From then on the build
  refuses any change the audience would see. Only the spoken text, slide times and pace can
  still change.
- **To reuse:** copy `build.py`, `.gitignore` and the format of `talk.md` (the comment block at
  its top explains it). The five slide layouts in `build.py` were written for this deck on the
  SIIM template. A slide-heavy talk will probably need new layouts. The checks, the rehearsal
  clock, the Word export and the redline work for any number of slides. You need `python-pptx`,
  `python-docx`, `Pillow` and `reportlab`.

## 2. Writing the spoken script

Apply these from the first draft. Here they arrived round by round, and each round cost a full
review pass.

**Register (Jilei's rules for scientific talks)**
- Neutral and factual, not promotional. No years, download counts or selling points. Describe
  features, and let the audience judge.
- No questions to the audience, including rhetorical ones ("Where do we go from here?"). The
  closing slide states future directions as plain statements.
- Plain, literal words rather than jargon or metaphor.
- Co-authors in submission order.
- Say "can", not "does", for anything the talk doesn't show, and put the honest answer in
  `qa.md`.

**Write for the ear.** Jilei's comment: "When spoken, the sentence is less clear than written."
- One idea per sentence, with the subject and verb early.
- Nothing inserted mid-sentence that the listener must hold. For example, "make ITK-SNAP,
  open-source software for…, callable by AI agents" failed. It became "This talk is about
  ITK-SNAP, open-source software for segmenting medical images. We made it a tool that AI agents
  can call."
- No colons, semicolons or lists after a colon. Break them into short sentences.
- Spoken signposts: "Here is what already exists." "This work adds two things. First… Second…"
- One word per idea, used every time, and the same word as on the slides. This talk says "case"
  throughout, because the slides do.
- Spell out an acronym once ("the Model Context Protocol, or MCP"), then use it.
- Use contractions where they sound natural.
- Don't read the slide's list aloud. Say the point and let the slide carry the details. These
  are also the first words to cut when time is short.
- Watch for sounds that blur. "AI agents" runs three vowel sounds together; "can call" puts two
  hard k sounds side by side. Mark where to pause and what to stress, or reword.

## 3. Timing

- **Plan at the speaker's measured pace, not a guess.** Jilei's pace on slides in a full timed
  run on 2026-10-22 was **about 118 words/min** (111–137 depending on the slide). Planning at 132
  put that run 22 seconds over the plan.
- **Word budget** = (slot − video − switching buffer) × pace / 60. Leave about 10 seconds for
  each switch between PowerPoint and a video, and about 5 seconds even with no video.
- **Set each slide's `- time:`** from its word count at the measured pace. The rehearsal clock
  then measures against what the speaker will really do.
- **Content requests add words.** Agree the word budget before review rounds start, and say what
  each addition costs. In round 2 here, the requests added about 80 words to the slides.
- **Cut in this order:** words that repeat the slide; ideas said twice; then ask.

## 4. Review rounds in Word

What worked:
1. **Build the Word script.** `build/<name>_script.docx` shows the spoken text in black and what
   the audience sees in grey, for reference: the slide text, and for a video, what is on screen
   and when. It opens with Track Changes on.
2. **Claude comments first.** Claude adds its findings as Word comments on the exact sentences,
   in a copy in `review/` (git-ignored), with `review_comment.py`:

   ```bash
   python3 review_comment.py build/<name>_script.docx review/<name>_review_<date>.docx notes.json
   ```

   `notes.json` is a list of `[anchor text, comment]` pairs. Each anchor must appear in exactly
   one paragraph; if any doesn't, nothing is written. A slide heading is a good anchor for a
   comment about a whole slide.
3. **Jilei reviews in Word,** editing with Track Changes, commenting, and replying in comment
   threads.
4. **Claude reads the result** with `review_read.py`:

   ```bash
   python3 review_read.py review/<file>.docx --against build/<name>_script.docx
   ```

   It lists every paragraph with pending tracked changes: the text if all are accepted, the text
   if all are rejected, and who made which change. Then it lists every comment thread, with its
   anchor and replies. An accepted or rejected change leaves no mark in the file, so
   `--against` also lists every paragraph that differs from a fresh build of the version that was
   sent. That is how the decisions show up. Build it from the same `talk.md` before changing
   anything. For a redline round, the plain build equals the redline with all changes accepted,
   so it works there too. Claude then carries the result into `talk.md` and rebuilds.
5. **Claude sends back a redline.** `python3 build.py --changes-since <old talk.md or git
   revision>` writes `build/<name>_script_changes.docx`, where every change since that version is
   a tracked change. Claude copies it into `review/` with `review_comment.py`, adding a short
   comment per slide saying why it changed. Check that accepting all changes gives the new text
   and rejecting all gives the old.

Habits that helped:
- Save a copy of `talk.md` before each round, so the next redline shows only that round.
- If a file comes back with nothing accepted or rejected, say so. Here, "accept all" equalled
  the current text, so it was taken as accepted and the note said that.
- Repeat open questions until they're answered. The spoken co-author credit was asked twice and
  is still open.
- The rounds on 2026-10-22 were: (1) Claude's findings as comments; (2) Jilei's content
  requests; (3) a full rewrite for the ear; (4) cuts after a timed run. Doing the ear rewrite in
  the first draft would have saved round 3.

## 5. Rehearsal

- **Use the clock.** Open `build/script.html` in Safari or Chrome. The Claude app's browser pane
  can't play a local video.
  - Space starts the run and moves to the next part; Esc stops it.
  - The bar shows the time in the current part and how far ahead or behind plan you are.
  - At the end, the page lists each part against the plan. Paste that list back to Claude, which
    cuts or re-times from it.
- **Practise without memorizing.** Learn the order of the ideas, each slide's first and last
  sentence, and the numbers that must be exact.
  - Say each slide three different ways.
  - Practise out loud, standing.
  - Get each slide fluent, then practise the joins between them.
  - Record one run and listen to it once.
  - Do two or three runs a day, spread over several days.
  - Stop changing the script the day before.
- **The podium deck has old notes.** The uploaded deck keeps its speaker notes from upload day,
  so don't count on presenter view. A printed cue card is safer.

## 6. Video (optional; small part of a slide-heavy talk)

- **Check the narration against the real frames** (ffmpeg stills at the cue times), not from
  memory. The first draft here said "on the left" while the terminal filled the screen.
- **Narration follows the picture.** Put cues in brackets, like `[0:18: ITK-SNAP appears]`. They
  show in the script and aren't counted as spoken words.
- **Use long silences for a point the picture supports.** Keep lines short where a shot is short.

## 7. The venue and the repo

- **Check your own acceptance email.** Ours (AI Builder Showcase): 7 min + 5 min Q&A, a Penn
  Windows PC with Office only, at most 5 slides on the SIIM template, any demo as a prerecorded
  MP4 played outside PowerPoint, and an upload deadline before the talk. Other session types
  may have other rules. `README.md` lists ours in full.
- **The organisers may change the deck after upload.** Ours came back with the video on a slide
  of its own (play on click), the speaker notes from upload day, and one slide edited. Diff
  their copy against yours: every slide's text and geometry, and the embedded media checksum.
  Then write the current script into their copy with `python3 build.py --notes-into <their
  deck>`.
- **Poppins (the template's font) isn't installed on the Mac.** Check text fit with a
  Verdana-substituted copy, the conservative case.
- **The repo is public.** The acceptance email (it holds a private upload link), the SIIM
  template, `review/` and `final/` stay out of git, enforced by `.gitignore`.
