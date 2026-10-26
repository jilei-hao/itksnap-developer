# CAIMI26 presentation

Everything for the in-person talk at SIIM-CAIMI26: AI Builder Showcase, Session 1007,
Monday October 26, 2026, 4:30 to 6:00 PM ET, Rubenstein Auditorium, Smilow Center, Penn.

## The rule of this folder

**The `.md` files are the source of truth. The slides and the script are generated from
them.** Edit the `.md`, run the build, and never edit anything in `build/`.

| File | What it holds | What comes out of it |
|---|---|---|
| `talk.md` | the slides (words, numbers, order, timing), the video's place in the talk, and the spoken script | `build/CAIMI26_ITK-SNAP_Hao.pptx` with speaker notes, `build/script.html`, `build/CAIMI26_ITK-SNAP_Hao_script.docx` (the script to edit in Word, with what is on screen in each beat taken from `video.md`), and `build/CAIMI26_ITK-SNAP_Hao_script_phone.pdf` (the script sized for an iPhone screen, one slide per page) |
| `video.md` | the demo MP4's cut list: clips, crops, segments, captions, callouts; and the stills the slides use | `build/CAIMI26_ITK-SNAP_Hao_demo.mp4`, `build/still_*.jpg` |
| `qa.md` | likely questions and the answers to give | `build/CAIMI26_ITK-SNAP_Hao_qa_phone.pdf` (for an iPhone: a tappable list of the questions, each answer whole on its page) |
| `build.py` | the slide layout, and the checks | |
| `build_video.py` | renders the MP4 from `video.md` | |
| `review_comment.py` | adds review comments, each anchored to exact text, to a copy of a Word file | a commented `.docx`, usually in `review/` |
| `review_read.py` | reads a reviewed Word file: pending tracked changes, comment threads, and (with `--against`) every paragraph that differs from what was sent | a report on the terminal |
| `method.md` | how this talk was made (build rule, writing for the ear, timing, Word review rounds, rehearsal), for reuse on another talk | |
| `template/` | SIIM's PowerPoint template. Local only, not in git | |
| `build/` | generated files. Local only, not in git | |
| `review/` | commented copies of the deck and the script from review rounds. Local only, not in git | |
| `frozen.json` | snapshot of the uploaded content and checksums; makes the builds refuse visible changes | written by `python3 build.py --freeze` |
| `final/` | the exact files uploaded to the organisers. Local only, not in git | |

## Frozen since the upload (2026-10-21)

The deck and the video were uploaded to the organisers on 2026-10-21. The exact files are kept
in `final/uploaded_2026-10-21/` (local only), and `frozen.json` records their checksums and a
snapshot of everything the audience sees.

- **Still free to change:** the `### Say` and `### Beat` text, the slide times, and `pace`.
  A rebuild updates `build/script.html` and the speaker notes of the local deck. The uploaded
  deck keeps the notes it had at upload, so rehearse from `build/script.html`.
- **Refused while frozen:** any change to what is on a slide (`build.py` stops with an error),
  and re-rendering the video (`build_video.py` stops; `--stills` still runs).
- **To unfreeze** (for example, if the organisers accept a replacement): delete `frozen.json`,
  make the change, rebuild, re-upload, then run `python3 build.py --freeze` again.

## Build

```bash
python3 build_video.py   # the stills and the demo MP4, from video.md (about a minute)
python3 build.py         # the slides and the script (needs the stills)
```

`python3 build_video.py --stills` makes only the stills, if you only changed slides.

**Rehearsing.** `build/script.html` is also a rehearsal clock. Open it in Safari or Chrome
(`open build/script.html`); the Claude app's browser pane cannot play the local video. Space
starts the run and moves to the next part, and Esc stops it. The bar shows the time in the current part
and how far ahead or behind plan you are. In the video part the MP4 plays in the page and the
current beat is highlighted; the run moves to slide 4 when the video ends. At the end the page
lists your time for each part against the plan, and keeps the totals of earlier runs in that
browser. You can also just press play on the video to practise the narration on its own.

`build_video.py` fails if the segments of a beat do not add up to that beat's time in
`talk.md`. `build.py` prints a timing table and runs four checks. It exits with an error if
any fails:

- no more slides than `max slides` in `talk.md` (the organisers allow 5);
- the planned time fits the `slot` (7:00);
- no slide needs you to speak faster than `pace` (words per minute);
- the beats in `video.md` are the same beats as in `talk.md`, and they add up to the video's time.

It needs `python-pptx`, `Pillow` and `reportlab`, `ffmpeg` with `libx264`, the template in
`template/`, and the July footage (path in `video.md`). On this Mac all of these are present.

## Where to change what

| To change | Edit |
|---|---|
| any word or number on a slide, the slide order, the time per slide | `talk.md` |
| what you say | the `### Say` and `### Beat` blocks in `talk.md` |
| positions, sizes, fonts, colours | `build.py` |
| what the video shows, how it is cut, where the boxes and arrows go | `video.md` |

The video is a `## Video: Title` section between two slides. It is not a slide: it takes
`- time:`, `- file:` and `- attribution:` (burned into the video), then one
`### Beat N: Title (M:SS)` per beat. Its narration goes into the speaker notes of the slide
before it.

`talk.md` uses five slide layouts. Each expects its blocks in this order:

| Layout | Blocks under the slide heading |
|---|---|
| `title` | none; the text comes from `## Meta` |
| `problem-solution` | a numbered list of problems; then a three-row table of boxes, `- arrows:` with four labels, and a `>` takeaway line |
| `context` | `- image:`; then one block per topic, each a list of short lines, and a `>` line under the last |
| `record` | a table and a one-line caption; then lead-in lines (`**Shown in the table:** ...`) and a `>` line on how the record is built |
| `closing` | one numbered list, drawn as cards across the slide (or two lists, drawn as two columns); optionally a block holding a URL, which adds a small QR code |

**Review rounds.** Comment and edit in the built deck if that is easier, then copy it into
`review/` (date in the name) before the next build, which overwrites `build/`. The changes go
back into the `.md` files by hand; then rebuild. For the spoken script, do the same with the
`_script.docx`: it opens with Track Changes on, so the edits come back marked. To send the next
round back as a redline, run `python3 build.py --changes-since <old talk.md or git revision>`: it
also writes `build/<output>_script_changes.docx`, where every change to the spoken text since that
version is a tracked change to accept or reject.

**Hand polish comes last.** Once the content is frozen you can adjust the PPTX in PowerPoint.
Save that copy outside `build/`. After that, a change in `talk.md` does not reach the polished
copy by itself.

## What the organisers require

From the acceptance email (kept out of this public repo; it holds the upload link).

- **Time:** 7 minutes to present, then 5 minutes of Q&A.
- **Machine:** a Penn Medicine Windows PC with Microsoft Office. No Mac, no personal laptop.
- **Demo:** live only if it is web-hosted and opens in a browser. ITK-SNAP is a desktop
  app, so the demo is a **prerecorded MP4**, narrated in person.
- **The MP4 is the main content** (follow-up from the organisers, received 2026-10-16). It is
  loaded on the podium PC and played on its own, not from a slide; the five slides frame it:
  title, context, problem and what we built, then the video, then the record and the future
  directions.
- **Changed on 2026-10-23: the video is inside the deck.** The organisers' final deck,
  `final/uploaded_2026-10-23/1007_Hao.pptx` (local only), has 6 slides: the five here, with the
  video on its own slide 4. It plays **on click**: click once to start it, and not again until it
  ends, because the next click moves to slide 5. The organisers' copy has the speaker notes from
  2026-10-21. To put the current script into it, run
  `python3 build.py --notes-into final/uploaded_2026-10-23/1007_Hao.pptx`. That writes
  `build/1007_Hao.pptx`, a copy whose speaker notes are the only change.
- **Slides:** at most 5, on the official CAIMI26 template. The title slide shows the title,
  presenter name, degree(s) and institution.
- **Upload:** the PowerPoint and the MP4, by end of day **Wednesday October 21, 2026**.
  Then email Anna Zawacki (azawacki@siim.org) with the format: "Prerecorded Demo".

## To do

- [x] Upload the deck and the video (2026-10-21). Frozen 2026-10-22.
- [ ] Confirm the email to Anna Zawacki said "Prerecorded Demo".
- [ ] Play the uploaded deck and MP4 on the Windows machine; practise switching from slide 3
      to the video and back to slide 4.
- [x] Rehearse against `build/script.html` with a timer. Tune the spoken text in `talk.md`
      (`### Say`, `### Beat`), then rebuild.
- [x] Read through `qa.md`; answer the three "Needs your answer" questions.

## Related

- What was submitted: `../caimi-submission/caimi_submitted.md`
- The July footage: `/Users/Shared/Movies/260724_CAIMI-ITKSNAP/`
- The demo data: `~/data/itksnap/caimi-demo-working/`
