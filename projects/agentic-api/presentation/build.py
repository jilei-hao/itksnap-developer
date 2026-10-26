#!/usr/bin/env python3
"""Build the CAIMI26 talk from talk.md (the source of truth).

    python3 build.py

Writes build/<output>.pptx (slides + speaker notes), build/script.html (the
spoken script with a running clock), build/<output>_script.docx (the script
to edit and comment on in Word), build/<output>_script_phone.pdf (the
script to read on an iPhone) and build/<output>_qa_phone.pdf (qa.md, the same). Re-run after ANY edit to talk.md; never edit
the files in build/ by hand, they are overwritten.

Also checks the slot rules from the acceptance email -- slide count, total time,
speaking pace -- and that video.md lists the same beats as talk.md. Exits
non-zero if any check fails, so this doubles as the pre-upload check.

talk.md owns the words, numbers, order and timing. This file owns the layout.
Needs python-pptx, Pillow and reportlab (for the QR code).
"""

import glob
import hashlib
import html
import json
import os
import re
import sys

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR as TC
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "talk.md")
VIDEO_MD = os.path.join(HERE, "video.md")
QA_MD = os.path.join(HERE, "qa.md")
FROZEN = os.path.join(HERE, "frozen.json")   # written by `build.py --freeze`; see README
BUILD = os.path.join(HERE, "build")
# The SIIM template is not in git; drop it in template/ or point CAIMI_TEMPLATE at it.
TEMPLATE = os.environ.get("CAIMI_TEMPLATE") or next(
    iter(sorted(glob.glob(os.path.join(HERE, "template", "*.pptx")))), None)

errors = []


def die(msg):
    sys.exit("build.py: " + msg)


# ── parse markdown ──────────────────────────────────────────────────────────
def read_md(path):
    return re.sub(r"<!--.*?-->", "", open(path, encoding="utf-8").read(), flags=re.S)


def split_h(text, level):
    """[(heading, body)] at one heading level; text before the first heading has heading None."""
    out, last, pos = [], None, 0
    for m in re.finditer(rf"^{'#' * level} +(.+?)\s*$", text, flags=re.M):
        out.append((last, text[pos:m.start()]))
        last, pos = m.group(1), m.end()
    out.append((last, text[pos:]))
    return out


def parse_block(body):
    """One block of markdown -> its list items, "- key: value" props, table, quote, paragraphs."""
    blk = {"items": [], "props": {}, "table": [], "quote": "", "paras": [],
           "url": (re.search(r"https?://\S+", body) or [None])[0]}
    para, item = [], None

    def flush():
        if para:
            blk["paras"].append(" ".join(para))
            para.clear()

    for line in body.splitlines():
        s = line.strip()
        if not s:
            flush()
            item = None
            continue
        m = re.match(r"^([-*]|\d+[.)])\s+(.*)$", s)
        if m:
            flush()
            bullet, t = m.groups()
            prop = re.match(r"^([A-Za-z][A-Za-z ]*):(?:\s+(.*))?$", t) if bullet in "-*" else None
            if prop:
                blk["props"][prop.group(1).strip().lower()] = (prop.group(2) or "").strip()
                item = None
            else:
                lead = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", t)
                item = {"lead": lead.group(1).strip(), "text": lead.group(2)} if lead else {"lead": None, "text": t}
                blk["items"].append(item)
        elif s.startswith("|"):
            flush()
            item = None
            cells = [c.strip() for c in s.strip("|").split("|")]
            if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                blk["table"].append(cells)
        elif s.startswith(">"):
            flush()
            item = None
            blk["quote"] = (blk["quote"] + " " + s.lstrip("> ").strip()).strip()
        elif item is not None and line[:1] in " \t":
            item["text"] = (item["text"] + " " + s).strip()      # wrapped list item
        else:
            item = None
            para.append(s)
    flush()
    return blk


def secs(s, where):
    m = re.fullmatch(r"(\d+):([0-5]\d)", s.strip())
    if not m:
        die(f"{where}: a time must look like 0:55, got {s!r}")
    return int(m.group(1)) * 60 + int(m.group(2))


def clock(t):
    return f"{t // 60}:{t % 60:02d}"


def count_words(paras):
    spoken = re.sub(r"\[.*?\]", " ", " ".join(paras))      # [stage directions] are not spoken
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’-]*", spoken))


def parse_talk(path):
    """-> (meta, parts). A part is a slide ('## Slide N: Title') or the video ('## Video: Title'),
    in talk order; the video is played on its own and is not a slide."""
    meta, parts = {}, []
    for head, body in split_h(read_md(path), 2):
        if head is None:
            continue
        if head.lower() == "meta":
            meta = parse_block(body)["props"]
            continue
        m = re.fullmatch(r"Slide (\d+):\s*(.+)", head)
        v = re.fullmatch(r"Video:\s*(.+)", head)
        if not (m or v):
            die(f"talk.md: unexpected '## {head}' (expected '## Meta', '## Slide N: Title' or '## Video: Title')")
        sub = split_h(body, 3)
        p = {"kind": "slide" if m else "video", "num": int(m.group(1)) if m else None,
             "title": (m.group(2) if m else v.group(1)).strip(), "props": parse_block(sub[0][1])["props"],
             "sections": [], "say": [], "beats": []}
        p["where"] = f"talk.md slide {p['num']}" if m else "talk.md video"
        for key in (("layout", "time") if m else ("time", "file")):
            if not p["props"].get(key):
                die(f"{p['where']}: missing '- {key}: ...' under the heading")
        p["layout"] = p["props"]["layout"] if m else "video"
        p["secs"] = secs(p["props"]["time"], p["where"])
        for name, sbody in sub[1:]:
            blk = parse_block(sbody)
            beat = re.fullmatch(r"Beat (\d+):\s*(.+?)\s*\((\d+:\d\d)\)", name)
            if name.lower() == "say":
                p["say"] = blk["paras"]
            elif beat:
                p["beats"].append({"num": int(beat.group(1)), "title": beat.group(2),
                                   "secs": secs(beat.group(3), p["where"]), "say": blk["paras"]})
            elif name.lower().startswith("beat"):
                die(f"{p['where']}: a beat heading must look like '### Beat 1: Title (0:20)', got '### {name}'")
            else:
                p["sections"].append((name, blk))
        parts.append(p)
    if not any(p["kind"] == "slide" for p in parts):
        die("talk.md: no '## Slide N: Title' sections found")
    return meta, parts


def tables(md):
    """{section heading: (list props, [row dicts keyed by lower-case header])} for every ## section.
    Used for video.md, here and in build_video.py."""
    out = {}
    for head, body in split_h(md, 2):
        if head is None:
            continue
        props = dict(re.findall(r"^- ([a-z ]+):\s*(.+?)\s*$", body, flags=re.M))
        rows, header = [], None
        for line in body.splitlines():
            s = line.strip()
            if not s.startswith("|"):
                if header and rows:
                    break
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue
            if header is None:
                header = [c.lower() for c in cells]
            else:
                rows.append(dict(zip(header, cells)))
        out[head.strip().lower()] = (props, rows)
    return out


def tsecs(s, where):
    m = re.fullmatch(r"(\d+):(\d\d(?:\.\d+)?)", s.strip())
    if not m:
        die(f"video.md {where}: a time must look like 1:04.5, got {s!r}")
    return int(m.group(1)) * 60 + float(m.group(2))


def video_cues():
    """{beat: [(seconds into the beat, what is on screen)]}, from video.md's segments and callouts:
    when each segment starts, and when each callout appears."""
    if not os.path.exists(VIDEO_MD):
        return {}
    t = tables(read_md(VIDEO_MD))
    cues, at, segs = {}, {}, []
    for i, r in enumerate(t.get("segments", ({}, []))[1], 1):
        n, a, b = int(r["beat"]), tsecs(r["in"], f"segment {i}"), tsecs(r["out"], f"segment {i}")
        speed, start = float(r["speed"]), at.get(n, 0.0)
        segs.append((n, r["clip"], a, b, speed, start))
        cues.setdefault(n, []).append((start, r.get("note", "") + (f" ({speed:g}x speed)" if speed != 1 else "")))
        at[n] = start + (b - a) / speed + float(r["hold"])
    for i, r in enumerate(t.get("callouts", ({}, []))[1], 1):
        n, f, to = int(r["beat"]), tsecs(r["from"], f"callout {i}"), tsecs(r["to"], f"callout {i}")
        for sn, clip, a, b, speed, start in segs:
            if sn == n and clip == r["clip"] and f < b and to > a:
                cues[n].append((start + (max(f, a) - a) / speed, f"callout: {r.get('label', '')}"))
                break
    return {n: sorted(c, key=lambda x: x[0]) for n, c in cues.items()}


def parse_video_beats(path):
    """(number, title) rows of the beat table in video.md, or None if there is no video.md."""
    if not os.path.exists(path):
        return None
    rows, in_beats = [], False
    for line in read_md(path).splitlines():
        s = line.strip()
        if not s.startswith("|"):
            in_beats = False
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if [c.lower() for c in cells[:2]] == ["beat", "title"]:
            in_beats = True
        elif in_beats and cells[0].isdigit() and len(cells) > 1:
            rows.append((int(cells[0]), cells[1]))
    return rows


# ── checks ──────────────────────────────────────────────────────────────────
def who(p):
    return f"slide {p['num']}" if p["kind"] == "slide" else "the video"


def check(meta, parts):
    slot = secs(meta.get("slot", "7:00"), "talk.md Meta slot")
    max_slides, pace = int(meta.get("max slides", 5)), float(meta.get("pace", 150))
    slides = [p for p in parts if p["kind"] == "slide"]
    videos = [p for p in parts if p["kind"] == "video"]
    if [p["num"] for p in slides] != list(range(1, len(slides) + 1)):
        errors.append("slides must be numbered 1, 2, 3, ... in order")
    if slides[0]["layout"] != "title":
        errors.append("slide 1 must use '- layout: title' (it is the template's title slide)")
    if len(slides) > max_slides:
        errors.append(f"{len(slides)} slides; the organisers allow {max_slides}")
    if len(videos) > 1:
        errors.append("only one '## Video:' section is supported")
    t = 0
    for p in parts:
        p["start"], t = t, t + p["secs"]
        if p["kind"] == "video":
            if not p["beats"]:
                errors.append("the video needs '### Beat N: Title (M:SS)' sections")
            if [b["num"] for b in p["beats"]] != list(range(1, len(p["beats"]) + 1)):
                errors.append("video beats must be numbered 1, 2, 3, ... in order")
            beat_total, bt = sum(b["secs"] for b in p["beats"]), p["start"]
            for b in p["beats"]:
                b["start"], bt = bt, bt + b["secs"]
                b["words"] = count_words(b["say"])
            if beat_total != p["secs"]:
                errors.append(f"video beats add up to {clock(beat_total)}, but the video time is {clock(p['secs'])}")
            p["words"] = sum(b["words"] for b in p["beats"])
            want = [(b["num"], b["title"]) for b in p["beats"]]
            have = parse_video_beats(VIDEO_MD)
            if have is not None and have != want:
                errors.append("video.md beat table does not match the beats in talk.md:\n"
                              f"      talk.md : {want}\n      video.md: {have}")
        else:
            p["words"] = count_words(p["say"])
            if not p["say"]:
                errors.append(f"{who(p)}: no '### Say' text")
        p["wpm"] = p["words"] / (p["secs"] / 60) if p["secs"] else 0
        if p["wpm"] > pace:
            errors.append(f"{who(p)}: {p['words']} words in {clock(p['secs'])} is "
                          f"{p['wpm']:.0f} words/min, over your pace of {pace:.0f}")
    if t > slot:
        errors.append(f"planned time {clock(t)} is over the {clock(slot)} slot")
    return t, slot


# ── slide drawing helpers ───────────────────────────────────────────────────
BODY, HEAD = "Poppins", "Poppins SemiBold"       # the template's own typefaces
INK = RGBColor(0x26, 0x26, 0x26)
MUTED = RGBColor(0x4D, 0x55, 0x58)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
TINT = RGBColor(0xE8, 0xF3, 0xF5)                # light teal panel / agent rows
TINT_HUMAN = RGBColor(0xFD, 0xF0, 0xE4)          # light orange: human rows
TINT_OTHER = RGBColor(0xF3, 0xF5, 0xF5)
HUMAN = RGBColor(0xB8, 0x52, 0x0E)               # dark orange, readable on TINT_HUMAN
LIGHT = RGBColor(0xD5, 0xEE, 0xF2)               # secondary text on the teal slides
LEFT_X, FULL_W = 0.67, 12.0                      # the template's content margins, inches


def color(target, c):
    """Apply an RGBColor or a theme color to a font.color / fill.fore_color / line.color."""
    if isinstance(c, RGBColor):
        target.rgb = c
    else:
        target.theme_color = c


def solid(shape):
    shape.fill.solid()
    return shape.fill.fore_color


def text(slide, x, y, w, h, paras, name=None, anchor=MSO_ANCHOR.TOP):
    """paras: [{t | runs:[{t, bold, color}], size, bold, color, align, after, bullet}]"""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = p.get("align", PP_ALIGN.LEFT)
        if "after" in p:
            para.space_after = Pt(p["after"])
        if "before" in p:
            para.space_before = Pt(p["before"])
        if p.get("bullet"):                      # a real bullet, hanging indent, orange like the template's
            ppr = para._p.get_or_add_pPr()
            ppr.set("marL", str(Inches(0.28)))
            ppr.set("indent", str(-Inches(0.28)))
            etree.SubElement(etree.SubElement(ppr, qn("a:buClr")), qn("a:srgbClr")).set("val", "F87E33")
            etree.SubElement(ppr, qn("a:buFont")).set("typeface", "Arial")
            etree.SubElement(ppr, qn("a:buChar")).set("char", "\u2022")
        for r in p.get("runs") or [p]:
            for k, chunk in enumerate(r["t"].split("\n")):
                if k:
                    para.add_line_break()
                run = para.add_run()
                run.text = chunk
                bold = r.get("bold", p.get("bold", False))
                run.font.size, run.font.bold = Pt(p.get("size", 16)), bold
                run.font.name = HEAD if bold else BODY
                color(run.font.color, r.get("color", p.get("color", INK)))
    return tb


def label(slide, x, y, w, t, fg=TC.ACCENT_3):
    return text(slide, x, y, w, 0.3, [{"t": t.upper(), "size": 12, "bold": True, "color": fg}])


def badge(slide, x, y, n, fill=TC.ACCENT_3, d=0.44, fg=WHITE):
    """Numbered circle: the deck's recurring motif."""
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    s.name = f"Badge {n}"
    color(solid(s), fill)
    s.line.fill.background()
    s.shadow.inherit = False
    tf = s.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = str(n)
    r.font.size, r.font.bold, r.font.name = Pt(15), True, HEAD
    color(r.font.color, fg)
    return s


def box(slide, x, y, w, h, fill, line=None, radius=0.12, name=None):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        s.name = name
    s.adjustments[0] = radius
    color(solid(s), fill)
    if line is None:
        s.line.fill.background()
    else:
        color(s.line.color, line)
        s.line.width = Pt(1.5)
    s.shadow.inherit = False
    return s


def box_text(shape, lines):
    """lines: [(text, size, bold, color)], centred in the shape."""
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Inches(0.12)
    tf.margin_top = tf.margin_bottom = Inches(0.06)
    for i, (t, size, bold, fg) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = t
        r.font.size, r.font.bold, r.font.name = Pt(size), bold, HEAD if bold else BODY
        color(r.font.color, fg)


def arrow(slide, x1, y1, x2, y2, c, width=2.0):
    cn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    color(cn.line.color, c)
    cn.line.width = Pt(width)
    tail = etree.SubElement(cn.line._get_or_add_ln(), qn("a:tailEnd"))
    tail.set("type", "triangle")
    return cn


def lead_list(slide, x, y, w, items, step, fill=TC.ACCENT_3, lead_fg=TC.ACCENT_4, sub_fg=MUTED, num_fg=WHITE):
    """Numbered badges, each with a bold lead and a lighter line under it."""
    for i, it in enumerate(items):
        yy = y + i * step
        badge(slide, x, yy, i + 1, fill, fg=num_fg)
        text(slide, x + 0.6, yy, w - 0.6, step - 0.15, [
            {"t": (it["lead"] or "").rstrip("."), "size": 17, "bold": True, "color": lead_fg, "after": 4},
            {"t": it["text"], "size": 14, "color": sub_fg},
        ], name=f"Item {i + 1}")


def drop_body_placeholders(slide):
    for ph in list(slide.placeholders):
        if ph.placeholder_format.idx != 0:
            ph._element.getparent().remove(ph._element)


def section(sl, i, need):
    """The i-th on-slide block of a slide, with a readable error if it is missing."""
    if i >= len(sl["sections"]):
        die(f"talk.md slide {sl['num']} (layout {sl['layout']}): expected a '### ...' block for {need}")
    return sl["sections"][i]


# ── one function per layout ─────────────────────────────────────────────────
def draw_title(slide, sl, meta):
    text(slide, LEFT_X, 2.5, 8.6, 1.55, [
        {"t": meta.get("title", "").replace(" | ", "\n"), "size": 44, "bold": True, "color": WHITE}], name="Title")
    text(slide, LEFT_X, 4.15, 8.2, 0.85, [
        {"t": meta.get("subtitle", ""), "size": 22, "color": TC.ACCENT_1}], name="Subtitle")
    # author list in submission order; the presenter in bold, with the degree if one is given
    presenter = meta.get("presenter", "")
    authors = [a.strip() for a in meta.get("authors", presenter).split(",") if a.strip()]
    if presenter not in authors:
        die(f"talk.md Meta: the presenter {presenter!r} is not in the authors list")
    runs = []
    for i, name in enumerate(authors):
        if i:
            runs.append({"t": ", "})
        mine = name == presenter
        runs.append({"t": name + (f", {meta['degree']}" if mine and meta.get("degree") else ""), "bold": mine})
    text(slide, LEFT_X, 5.3, 8.2, 1.0, [
        {"runs": runs, "size": 20, "color": WHITE, "after": 6},
        {"t": meta.get("institution", ""), "size": 16, "color": TC.TEXT_2},
    ], name="Authors")
    text(slide, LEFT_X, 6.85, 8.2, 0.3, [
        {"t": meta.get("session", ""), "size": 12, "color": TC.ACCENT_1}], name="Session")


def draw_problem_solution(slide, sl, meta):
    slide.shapes.title.text = sl["title"]
    drop_body_placeholders(slide)

    name, cards = section(sl, 0, "the problem list")
    items = cards["items"]
    label(slide, LEFT_X, 1.58, 4, name)
    gap = 0.375
    col_w = (FULL_W - gap * (len(items) - 1)) / max(len(items), 1)
    for i, it in enumerate(items):
        x = LEFT_X + i * (col_w + gap)
        badge(slide, x, 1.98, i + 1)
        text(slide, x + 0.6, 1.98, col_w - 0.6, 1.5, [
            {"t": (it["lead"] or "").rstrip("."), "size": 17, "bold": True, "color": TC.ACCENT_4, "after": 4},
            {"t": it["text"], "size": 14, "color": MUTED},
        ], name=f"Problem {i + 1}")

    name, dia = section(sl, 1, "the diagram")
    boxes = dia["table"][1:]
    arrows = [a.strip() for a in dia["props"].get("arrows", "").split(",")]
    if len(boxes) != 3 or len(arrows) != 4:
        die(f"talk.md slide {sl['num']}: the diagram needs a 3-row table and '- arrows:' with 4 labels")
    label(slide, LEFT_X, 3.72, 4, name)
    by, bh, bw = 4.12, 1.4, 2.6
    xs = [LEFT_X, LEFT_X + (FULL_W - bw) / 2, LEFT_X + FULL_W - bw]
    for i, (x, row) in enumerate(zip(xs, boxes)):
        centre = i == 1
        b = box(slide, x, by, bw, bh, TC.ACCENT_4 if centre else TINT, None if centre else TC.ACCENT_2, name=row[0])
        box_text(b, [(row[0], 19, True, WHITE if centre else TC.ACCENT_4),
                     (row[1], 13, False, WHITE if centre else MUTED)])
    g1a, g1b = xs[0] + bw + 0.1, xs[1] - 0.1
    g2a, g2b = xs[1] + bw + 0.1, xs[2] - 0.1
    top, bot = by + 0.5, by + 0.95
    arrow(slide, g1b, top, g1a, top, TC.ACCENT_2)
    arrow(slide, g1a, bot, g1b, bot, TC.ACCENT_2)
    arrow(slide, g2a, top, g2b, top, TC.ACCENT_2)
    arrow(slide, g2b, bot, g2a, bot, TC.ACCENT_6, width=3.0)
    # labels above an arrow grow upwards, labels below grow downwards, so two-line labels never cover it
    for x0, x1, y, t, strong, anchor in [(g1a, g1b, top - 0.7, arrows[0], False, MSO_ANCHOR.BOTTOM),
                                         (g1a, g1b, bot + 0.08, arrows[1], False, MSO_ANCHOR.TOP),
                                         (g2a, g2b, top - 0.7, arrows[2], False, MSO_ANCHOR.BOTTOM),
                                         (g2a, g2b, bot + 0.08, arrows[3], True, MSO_ANCHOR.TOP)]:
        text(slide, x0, y, x1 - x0, 0.62, [{"t": t, "size": 12, "bold": strong, "align": PP_ALIGN.CENTER,
                                            "color": TC.ACCENT_4 if strong else MUTED}], anchor=anchor)
    if dia["quote"]:
        text(slide, LEFT_X, 5.82, FULL_W, 0.75, [{"t": dia["quote"], "size": 17, "bold": True,
                                                  "color": TC.ACCENT_3, "align": PP_ALIGN.CENTER}], name="Takeaway")


def draw_record(slide, sl, meta):
    """Left: the demo's audit records as a table. Right: the fields every record carries."""
    slide.shapes.title.text = sl["title"]
    drop_body_placeholders(slide)
    lx, lw, rx, rw = LEFT_X, 6.3, 7.45, 5.2

    name, rec = section(sl, 0, "the record table")
    rows = rec["table"]
    if len(rows) < 2:
        die(f"talk.md slide {sl['num']}: '### {name}' needs a table with a header row")
    label(slide, lx, 1.58, lw, name)
    ncol = len(rows[0])
    row_h = min(0.5, 3.0 / len(rows))
    weights = [max(len(r[c]) for r in rows) + 2 for c in range(ncol)]
    widths = [max(1.0, lw * wt / sum(weights)) for wt in weights]
    widths = [wd * lw / sum(widths) for wd in widths]
    numeric = [all(re.fullmatch(r"[+\-\u2212]?[\d,.]+", r[c]) for r in rows[1:]) for c in range(ncol)]
    gf = slide.shapes.add_table(len(rows), ncol, Inches(lx), Inches(1.98), Inches(lw), Inches(row_h * len(rows)))
    gf.name = "Audit records"
    tbl = gf.table
    tbl.first_row, tbl.horz_banding = True, False
    for c, wd in enumerate(widths):
        tbl.columns[c].width = Inches(wd)
    for r, row in enumerate(rows):
        tbl.rows[r].height = Inches(row_h)
        head, actor = r == 0, row[0].lower()
        tint = TINT if actor == "agent" else TINT_HUMAN if actor == "human" else TINT_OTHER
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_left = cell.margin_right = Inches(0.12)
            color(solid(cell), TC.ACCENT_4 if head else tint)
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.RIGHT if numeric[c] else PP_ALIGN.LEFT
            run = p.add_run()
            run.text = re.sub(r"^-(?=\d)", "\u2212", val)          # a real minus sign
            bold = head or c == 0
            run.font.size, run.font.bold, run.font.name = Pt(13 if head else 14), bold, HEAD if bold else BODY
            color(run.font.color, WHITE if head else (TC.ACCENT_3 if actor == "agent" else HUMAN) if c == 0 else INK)
    if rec["paras"]:
        text(slide, lx, 1.98 + row_h * len(rows) + 0.1, lw, 0.45,
             [{"t": rec["paras"][0], "size": 12, "color": MUTED}], name="Table caption")

    # Right: lead-in panels ("Shown in the table:", "Also recorded:"). The first matches the
    # table header colour, so the reader can see which fields the table shows.
    name, fields = section(sl, 1, "the record fields")
    label(slide, rx, 1.58, rw, name)
    y = 1.98
    for i, it in enumerate(fields["items"]):
        dark = i == 0
        panel = box(slide, rx, y, rw, 1.15, TC.ACCENT_4 if dark else TINT, radius=0.08, name=f"Fields {i + 1}")
        tf = panel.text_frame
        tf.word_wrap, tf.vertical_anchor = True, MSO_ANCHOR.MIDDLE
        tf.margin_left = tf.margin_right = Inches(0.25)
        for j, (t, size, bold) in enumerate([((it["lead"] or "").rstrip(":"), 13, True), (it["text"], 16, False)]):
            para = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            para.alignment = PP_ALIGN.LEFT
            r = para.add_run()
            r.text = t
            r.font.size, r.font.bold, r.font.name = Pt(size), bold, HEAD if bold else BODY
            color(r.font.color, (TC.ACCENT_1 if bold else WHITE) if dark else TC.ACCENT_4)
        y += 1.3
    if fields["quote"]:
        text(slide, rx, y + 0.1, rw, 0.8, [{"t": fields["quote"], "size": 14, "color": MUTED}], name="How it is built")


def draw_context(slide, sl, meta):
    """Left: an image (a still from the demo footage). Right: one block per '### Heading', each a
    heading and bullet lines; an optional '>' line under the last block."""
    slide.shapes.title.text = sl["title"]
    drop_body_placeholders(slide)
    img = sl["props"].get("image", "")
    path = os.path.join(HERE, img) if img else None
    if not path or not os.path.exists(path):
        die(f"{sl['where']}: image not found: {path} (run 'python3 build_video.py --stills' first?)")
    from PIL import Image
    iw, ih = Image.open(path).size
    box_w, box_h = 6.4, 4.9
    w = min(box_w, box_h * iw / ih)
    h = w * ih / iw
    pic = slide.shapes.add_picture(path, Inches(LEFT_X), Inches(1.7 + (box_h - h) / 2), Inches(w), Inches(h))
    pic.name = "ITK-SNAP screenshot"
    pic._element.nvPicPr.cNvPr.set("descr", "ITK-SNAP showing a CT scan with segmented heart and vessels.")
    x = LEFT_X + w + 0.45
    rw = LEFT_X + FULL_W - x
    blocks = [(n, b) for n, b in sl["sections"] if b["items"]]
    paras = []
    for i, (name, blk) in enumerate(blocks):            # one text box, so the blocks flow
        paras.append({"t": name, "size": 20, "bold": True, "color": TC.ACCENT_3, "after": 6,
                      **({"before": 18} if i else {})})
        paras += [{"t": it["text"], "size": 16, "color": INK, "bullet": True, "after": 6} for it in blk["items"]]
    text(slide, x, 1.7, rw, 3.6, paras, name="About")
    if blocks and blocks[-1][1]["quote"]:
        text(slide, x, 5.5, rw, 1.1, [{"t": blocks[-1][1]["quote"], "size": 16, "bold": True, "color": TC.ACCENT_4}],
             name="Bridge", anchor=MSO_ANCHOR.BOTTOM)


def draw_closing(slide, sl, meta):
    """Closing slide; stays up during the Q&A. One numbered list is drawn as cards across the
    slide, two as columns. A block holding only a URL adds a QR code, top right."""
    slide.shapes.title.text = sl["title"]
    drop_body_placeholders(slide)
    lists = [(n, b) for n, b in sl["sections"] if b["items"]]
    if not 1 <= len(lists) <= 2:
        die(f"talk.md slide {sl['num']} (layout closing): expected one or two numbered lists")

    if len(lists) == 1:                          # the slide title already names the list
        items, gap, y, h = lists[0][1]["items"], 0.35, 2.2, 3.2
        w = (FULL_W - gap * (len(items) - 1)) / len(items)
        for i, it in enumerate(items):
            x = LEFT_X + i * (w + gap)
            box(slide, x, y, w, h, TC.ACCENT_4, radius=0.06, name=f"Card {i + 1}")
            badge(slide, x + 0.3, y + 0.3, i + 1, fill=TC.ACCENT_6, d=0.5)
            text(slide, x + 0.3, y + 1.0, w - 0.6, h - 1.2, [
                {"t": (it["lead"] or "").rstrip("."), "size": 20, "bold": True, "color": WHITE, "after": 8},
                {"t": it["text"], "size": 15, "color": LIGHT},
            ], name=f"Card text {i + 1}")
    else:
        columns = [(LEFT_X, 5.55, dict(fill=TC.ACCENT_6)), (6.82, 5.85, dict(fill=WHITE, num_fg=TC.ACCENT_4))]
        for (name, blk), (x, w, badge_style) in zip(lists, columns):
            label(slide, x, 1.58, w, name, fg=TC.ACCENT_1)
            lead_list(slide, x, 1.98, w, blk["items"], min(1.5, 4.7 / len(blk["items"])),
                      lead_fg=WHITE, sub_fg=LIGHT, **badge_style)

    link = next(((n, b) for n, b in sl["sections"] if b["url"] and not b["items"]), None)
    if link:
        name, blk = link
        size = 1.3
        qx = LEFT_X + FULL_W - size
        qr = slide.shapes.add_picture(make_qr(blk["url"]), Inches(qx), Inches(0.2), Inches(size), Inches(size))
        qr.name = "QR code"
        qr._element.nvPicPr.cNvPr.set("descr", f"{name}: QR code linking to {blk['url']}")
        qr.click_action.hyperlink.address = blk["url"]
        # the URL sits under the QR code, so a long slide title has the full width beside it
        text(slide, qx + size - 3.0, 0.2 + size + 0.03, 3.0, 0.25, [
            {"t": re.sub(r"^https?://", "", blk["url"]), "size": 10, "color": LIGHT, "align": PP_ALIGN.RIGHT},
        ], name="QR caption")


def make_qr(url):
    from PIL import Image
    from reportlab.graphics.barcode.qrencoder import QRCode, QRErrorCorrectLevel
    q = QRCode(None, QRErrorCorrectLevel.Q)
    q.addData(url)
    q.make()
    n, px, quiet = q.getModuleCount(), 24, 4
    img = Image.new("RGB", ((n + 2 * quiet) * px,) * 2, "white")
    for r in range(n):
        for c in range(n):
            if q.isDark(r, c):
                img.paste((0, 0, 0), ((c + quiet) * px, (r + quiet) * px, (c + quiet + 1) * px, (r + quiet + 1) * px))
    path = os.path.join(BUILD, "qr.png")
    img.save(path)
    return path


# layout name in talk.md -> (layout name in the SIIM template, drawing function)
LAYOUTS = {
    "title": ("1 Title Slide", draw_title),
    "problem-solution": ("7 Content Slide (White)", draw_problem_solution),
    "context": ("7 Content Slide (White)", draw_context),
    "record": ("8 Content Slide Two Column (White)", draw_record),
    "closing": ("5 Content Slide (Medium)", draw_closing),
}


# ── products ────────────────────────────────────────────────────────────────
def notes_text(p, own_slide=False):
    """Speaker notes for one part. own_slide: the video sits on a slide of its own (the organisers'
    final deck) instead of being played from outside PowerPoint."""
    span = f"[{clock(p['start'])}-{clock(p['start'] + p['secs'])}]"
    if p["kind"] == "slide":
        return span + "\n" + "\n\n".join(p["say"])
    cue = (f"THE DEMO VIDEO ({clock(p['secs'])}) IS ON THIS SLIDE. Click once to start it. Do not click "
           "again until it ends: the next click moves to the next slide. Narrate:" if own_slide else
           f"NOW PLAY THE DEMO VIDEO ({clock(p['secs'])}), from outside PowerPoint. Narrate:")
    out = [f"{span}  {cue}"]
    for b in p["beats"]:
        out.append(f"BEAT {b['num']} - {b['title']} ({clock(b['secs'])})\n" + "\n\n".join(b["say"]))
    return "\n\n".join(out)


def build_pptx(meta, parts, out):
    if not TEMPLATE or not os.path.exists(TEMPLATE):
        die("no template: put the CAIMI26 .pptx template in template/ or set CAIMI_TEMPLATE")
    prs = Presentation(TEMPLATE)
    layouts = {l.name: l for l in prs.slide_layouts}
    ids = prs.slides._sldIdLst
    for sld_id in list(ids)[1:]:                 # keep the template's title slide, drop its other slides
        prs.part.drop_rel(sld_id.rId)
        ids.remove(sld_id)
    for i, p in enumerate(parts):
        if p["kind"] != "slide":
            continue
        if p["layout"] not in LAYOUTS:
            die(f"{p['where']}: unknown layout {p['layout']!r} (known: {', '.join(LAYOUTS)})")
        tmpl_layout, draw = LAYOUTS[p["layout"]]
        slide = prs.slides[0] if p["num"] == 1 else prs.slides.add_slide(layouts[tmpl_layout])
        draw(slide, p, meta)
        notes = notes_text(p)
        if i + 1 < len(parts) and parts[i + 1]["kind"] == "video":   # the video's cue and narration
            notes += "\n\n" + notes_text(parts[i + 1])
        if i > 0 and parts[i - 1]["kind"] == "video":
            notes = "[After the video, back to the slides.]\n" + notes
        slide.notes_slide.notes_text_frame.text = notes
    prs.save(out)


# The rehearsal clock in script.html. Space starts the run and moves to the next part; the video
# plays in the page and its beats light up as it runs. Results stay in this browser only.
REHEARSE_JS = r"""
const D = JSON.parse(document.getElementById("parts").textContent), P = D.parts;
const $ = id => document.getElementById(id), vid = document.querySelector("video");
const now = () => performance.now() / 1000;
const fmt = s => { s = Math.round(Math.abs(s)); return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0"); };
const signed = d => (d < 0 ? "-" : "+") + fmt(d);
let idx = -1, t0 = 0, p0 = 0, laps = [], timer = null;
const playing = () => vid && vid.readyState > 0 && !vid.error;

function under(el) {                     // scroll el to just below the bar (and the player, in the video)
  let top = $("bar").offsetHeight + 8;
  if (el.closest(".video") && !el.classList.contains("video")) top += document.querySelector(".vwrap").offsetHeight;
  window.scrollTo({top: el.getBoundingClientRect().top + window.scrollY - top, behavior: "smooth"});
}
function beats() {                       // light up the beat the video is in; return its label
  const v = P.find(p => p.kind === "video"); if (!v) return "";
  const t = playing() ? vid.currentTime : (P[idx] === v ? now() - p0 : -1);
  let label = "";
  for (const b of v.beats) {
    const el = $("beat-" + b.num), on = t >= b.v0 && t < b.v0 + b.secs;
    if (on && !el.classList.contains("cur")) { el.classList.add("cur"); under(el); }
    if (!on) el.classList.remove("cur");
    if (on) label = `Beat ${b.num}: ${fmt(b.v0 + b.secs - t)} left`;
  }
  return label;
}
function tick() {
  if (idx < 0) { beats(); return; }
  const p = P[idx], t = now(), inPart = t - p0;
  const drift = (p0 - t0 - p.start) + Math.max(0, inPart - p.secs);
  $("part").textContent = `${p.tag} ${fmt(inPart)} of ${fmt(p.secs)}`;
  $("part").className = inPart > p.secs ? "over" : "";
  $("drift").textContent = Math.abs(drift) < 1 ? "on plan" : `${fmt(drift)} ${drift > 0 ? "behind" : "ahead"}`;
  $("drift").className = drift >= 5 ? "over" : "";
  $("now").textContent = p.kind === "video" ? beats() : p.title;
  if (p.kind === "video" && !playing() && inPart >= p.secs) go();     // no MP4: a stand-in clock
}
function go() {                          // start the run, or close this part and open the next
  const t = now();
  if (idx < 0) { t0 = t; laps = []; timer = setInterval(tick, 200); } else laps[idx] = t - p0;
  if (vid && P[idx] && P[idx].kind === "video") vid.pause();
  document.querySelectorAll("section.cur").forEach(s => s.classList.remove("cur"));
  idx++; p0 = t;
  if (idx === P.length) return finish();
  $("part-" + idx).classList.add("cur"); under($("part-" + idx));
  if (P[idx].kind === "video" && vid) { vid.currentTime = 0; vid.play(); }
  $("go").textContent = idx + 1 < P.length ? "Next part" : "Finish";
  tick();
}
function finish() {
  clearInterval(timer); timer = null; idx = -1;
  const total = laps.reduce((a, b) => a + b, 0);
  const rows = P.map((p, i) => `${p.tag.padEnd(8)}${fmt(laps[i]).padStart(6)}  planned ${fmt(p.secs).padStart(5)}  ${signed(laps[i] - p.secs)}`);
  P.forEach((p, i) => { const c = $("act-" + i); c.textContent = fmt(laps[i]); c.className = "live" + (laps[i] > p.secs + 2 ? " over" : ""); });
  let runs = [];
  try { runs = JSON.parse(localStorage.getItem("rehearsal-runs") || "[]"); } catch (e) {}
  runs.push({when: new Date().toLocaleString(), total});
  try { localStorage.setItem("rehearsal-runs", JSON.stringify(runs.slice(-10))); } catch (e) {}
  $("result").textContent = [`Run ${runs.length}, ${runs[runs.length - 1].when}`, ...rows,
    `${"Total".padEnd(8)}${fmt(total).padStart(6)}  planned ${fmt(D.plan).padStart(5)}  ${signed(total - D.plan)}   slot ${fmt(D.slot)}`,
    "", "Earlier runs: " + (runs.slice(0, -1).map(r => fmt(r.total)).join(", ") || "none")].join("\n");
  $("result").hidden = false; under($("result"));
  $("now").textContent = `Done: ${fmt(total)} of ${fmt(D.slot)}`; $("part").textContent = $("drift").textContent = "";
  $("go").textContent = "Start again";
}
function stop() {
  if (idx < 0 || !confirm("Stop this run?")) return;
  clearInterval(timer); timer = null; idx = -1; if (vid) vid.pause();
  document.querySelectorAll(".cur").forEach(s => s.classList.remove("cur"));
  $("go").textContent = "Start"; $("now").textContent = "Stopped"; $("part").textContent = $("drift").textContent = "";
}
$("go").onclick = e => { e.currentTarget.blur(); go(); };
window.addEventListener("keydown", e => {
  if (e.key === " " || e.key === "ArrowRight") { e.preventDefault(); go(); }
  else if (e.key === "Escape") stop();
}, true);
if (vid) {
  vid.addEventListener("ended", () => { if (P[idx] && P[idx].kind === "video") go(); });
  vid.addEventListener("timeupdate", () => { if (idx < 0) beats(); });
  document.querySelector(".vwrap").style.top = $("bar").offsetHeight + "px";
}
"""


def build_phone_pdf(meta, parts, total, slot, out):
    """The spoken script as a PDF to read on an iPhone: the page is 390 x 844 pt, the screen's own
    size in points, so fitted to the width it shows at 100%. Large type, one slide per page."""
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Table, TableStyle
    e = html.escape
    teal, grey, orange = "#1c6a75", "#5f6669", "#b8520e"
    body = ParagraphStyle("body", fontName="Helvetica", fontSize=17, leading=24, spaceAfter=12)
    head = ParagraphStyle("head", fontName="Helvetica-Bold", fontSize=20, leading=25, textColor=teal, spaceAfter=2)
    sub = ParagraphStyle("sub", parent=head, fontSize=17, leading=22, spaceBefore=8)
    small = ParagraphStyle("small", fontName="Helvetica", fontSize=12, leading=16, textColor=grey, spaceAfter=10)

    def say(ps):                                 # [stage directions] in orange italics, not spoken
        return [Paragraph(re.sub(r"(\[.*?\])", rf'<font color="{orange}"><i>\1</i></font>', e(p)), body) for p in ps]

    title = meta.get("title", "").replace(" | ", " ")
    story = [Paragraph(e(title), ParagraphStyle("title", parent=head, fontSize=24, leading=29, spaceAfter=8)),
             Paragraph(e(f"{meta.get('presenter', '')} · {meta.get('session', '')}"), small),
             Paragraph(f"Spoken script. Plan {clock(total)} of a {clock(slot)} slot.", small)]
    rows = [["Part", "Starts", "Length"]] + [
        [f"Slide {p['num']}" if p["kind"] == "slide" else "Video", clock(p["start"]), clock(p["secs"])] for p in parts]
    table = Table(rows, colWidths=[150, 100, 100])
    table.setStyle(TableStyle([("FONT", (0, 0), (-1, -1), "Helvetica", 14), ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 14),
                               ("TEXTCOLOR", (0, 0), (-1, 0), teal), ("LINEBELOW", (0, 0), (-1, -1), 0.5, "#d5dcdd"),
                               ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    story.append(table)
    for p in parts:
        tag = f"Slide {p['num']}" if p["kind"] == "slide" else "Video"
        story += [PageBreak(), Paragraph(e(f"{tag} · {p['title']}"), head),
                  Paragraph(f"{clock(p['start'])}–{clock(p['start'] + p['secs'])} · {p['secs']} s", small)]
        if p["kind"] == "slide":
            story += say(p["say"])
            continue
        story.append(Paragraph("On its own slide. Click once to start it, and not again until it ends.", small))
        for b in p["beats"]:
            v0 = b["start"] - p["start"]
            story.append(KeepTogether([Paragraph(e(f"Beat {b['num']} · {b['title']}"), sub),   # a beat never splits
                                       Paragraph(f"video {clock(v0)}–{clock(v0 + b['secs'])}", small)] + say(b["say"])))

    def footer(canvas, doc):
        canvas.setFont("Helvetica", 10)
        canvas.setFillColor(grey)
        canvas.drawCentredString(doc.pagesize[0] / 2, 16, str(doc.page))

    doc = SimpleDocTemplate(out, pagesize=(390, 844), leftMargin=20, rightMargin=20, topMargin=28, bottomMargin=36,
                            title=f"Script: {title}", author=meta.get("presenter", ""))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def build_qa_pdf(src, out, author=""):
    """qa.md as a PDF to read on an iPhone during Q&A (same page as the script PDF). It opens with
    every question as a link to its answer, and each page links back to that list. Each entry
    is a **question** line, its answer, optional *If pressed:* and *Unsourced:* lines (the latter
    in orange: a claim no source backs) and a *Source:* line. A list of **questions** instead marks
    questions with no vetted answer yet."""
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate
    teal, grey, orange = "#1c6a75", "#5f6669", "#b8520e"
    body = ParagraphStyle("body", fontName="Helvetica", fontSize=17, leading=24, spaceAfter=8)
    quest = ParagraphStyle("quest", parent=body, fontName="Helvetica-Bold", textColor=teal, leading=22, spaceAfter=6)
    head = ParagraphStyle("head", fontName="Helvetica-Bold", fontSize=20, leading=25, textColor=teal, spaceBefore=6, spaceAfter=10)
    link = ParagraphStyle("link", parent=body, fontSize=14, leading=18, spaceAfter=5, leftIndent=10)
    small = ParagraphStyle("small", fontName="Helvetica", fontSize=12, leading=16, textColor=grey, spaceAfter=18)
    warn = ParagraphStyle("warn", parent=small, fontSize=13, leading=17, textColor=orange, spaceAfter=6)

    def inline(s):                               # the markdown qa.md uses -> reportlab markup
        s = html.escape(s, quote=False)
        s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", rf'<a href="\2" color="{teal}">\1</a>', s)
        s = re.sub(r"`([^`]+)`", r'<font face="Courier">\1</font>', s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        return re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<i>\1</i>", s)

    md = read_md(src)
    title = (re.search(r"^# +(.+)$", md, flags=re.M) or [None, "Q&A"])[1].strip()
    sections, n = [], 0             # [(name, [(id, question, answer, pressed, unsourced, source, open)])]
    for name, text in split_h(md, 2)[1:]:
        entries = []
        for block in re.split(r"\n\s*\n", text.strip()):
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if lines and lines[0].startswith("- "):          # questions with no vetted answer yet
                for l in lines:
                    m = re.match(r"- \*\*(.+?)\*\*\s*(.*)", l)
                    if m:
                        n += 1
                        entries.append((f"q{n}", m.group(1), m.group(2), "", "", "", True))
            elif lines and lines[0].startswith("**") and lines[0].endswith("**"):
                seg = {"answer": [], "pressed": [], "unsourced": [], "source": []}
                cur = "answer"
                for l in lines[1:]:
                    if l.startswith("*Source:"):
                        cur = "source"
                    elif l.startswith("*If pressed:*"):
                        cur, l = "pressed", l[len("*If pressed:*"):].strip()
                    elif l.startswith("*Unsourced:*"):
                        cur, l = "unsourced", l[len("*Unsourced:*"):].strip()
                    seg[cur].append(l)
                n += 1
                src_text = " ".join(seg["source"]).strip()
                entries.append((f"q{n}", lines[0].strip("*"), " ".join(seg["answer"]), " ".join(seg["pressed"]),
                                " ".join(seg["unsourced"]), src_text[1:-1] if src_text.startswith("*") and src_text.endswith("*") else src_text, False))
        sections.append((name.strip(), entries))

    story = [Paragraph(f'<a name="index"/>{html.escape(title)}', ParagraphStyle("t", parent=head, fontSize=24, leading=29, spaceBefore=0)),
             Paragraph(f"{n} questions. Tap one to jump to its answer.", small)]
    for name, entries in sections:                # a group's heading stays with its questions
        story.append(KeepTogether(
            [Paragraph(html.escape(name), ParagraphStyle("ih", parent=head, fontSize=15, leading=19, spaceAfter=5))]
            + [Paragraph(f'<a href="#{qid}" color="{orange if unanswered else teal}">{inline(q)}</a>', link)
               for qid, q, *_, unanswered in entries]))
    for name, entries in sections:
        story += [PageBreak(), Paragraph(html.escape(name), head)]
        for qid, q, answer, pressed, unsourced, source, unanswered in entries:
            block = [Paragraph(f'<a name="{qid}"/>{inline(q)}', quest)]
            if unanswered:
                block.append(Paragraph(f'<font color="{orange}"><i>No vetted answer yet.</i></font> {inline(answer)}', body))
            else:
                block.append(Paragraph(inline(answer), body))
                if pressed:
                    block.append(Paragraph(f"<i>If pressed:</i> {inline(pressed)}", body))
                if unsourced:
                    block.append(Paragraph(f"<b>Unsourced:</b> {inline(unsourced)}", warn))
            if source:
                block.append(Paragraph(inline(source), small))
            else:
                block[-1].style = ParagraphStyle("last", parent=block[-1].style, spaceAfter=18)
            story.append(KeepTogether(block))

    def footer(canvas, doc):
        canvas.setFont("Helvetica", 10)
        canvas.setFillColor(grey)
        canvas.drawCentredString(doc.pagesize[0] / 2, 16, str(doc.page))
        if doc.page > 1:                         # a tap target back to the list of questions
            canvas.setFont("Helvetica", 13)
            canvas.setFillColor(teal)
            canvas.drawString(20, 14, "Back to questions")
            canvas.linkAbsolute("", "index", (14, 6, 150, 30))

    doc = SimpleDocTemplate(out, pagesize=(390, 844), leftMargin=20, rightMargin=20, topMargin=28, bottomMargin=40,
                            title=title, author=author)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def notes_into(parts, deck, out):
    """Write the speaker notes from talk.md into a copy of someone else's deck (the organisers'
    final, with the video on a slide of its own), changing nothing else. Its slides map to the
    parts of talk.md in order, one slide per part, the video included."""
    prs = Presentation(deck)
    if len(prs.slides) != len(parts):
        die(f"--notes-into: {deck} has {len(prs.slides)} slides, but talk.md has {len(parts)} parts "
            "(its slides and the video, one slide each)")
    for slide, p in zip(prs.slides, parts):
        slide.notes_slide.notes_text_frame.text = notes_text(p, own_slide=True)
    prs.save(out)


def build_script(meta, slides, total, slot, out):
    e = html.escape
    title = meta.get("title", "").replace(" | ", " ")

    def paras(ps):                               # [stage directions] in italics
        return "".join("<p>" + re.sub(r"(\[.*?\])", r"<i>\1</i>", e(p)) + "</p>" for p in ps)

    rows, body, data = [], [], []
    for i, sl in enumerate(slides):
        end = sl["start"] + sl["secs"]
        tag = f"Slide {sl['num']}" if sl["kind"] == "slide" else "Video"
        data.append({"tag": tag, "title": sl["title"], "kind": sl["kind"], "start": sl["start"], "secs": sl["secs"]})
        rows.append(f"<tr><td>{tag}</td><td>{e(sl['title'])}</td><td>{clock(sl['start'])}</td>"
                    f"<td>{clock(sl['secs'])}</td><td>{sl['words']}</td><td>{sl['wpm']:.0f}</td>"
                    f"<td class=\"live\" id=\"act-{i}\"></td></tr>")
        cls = ' class="video"' if sl["kind"] == "video" else ""
        body.append(f"<section id=\"part-{i}\"{cls}><h2>{tag}: {e(sl['title'])} <span>{clock(sl['start'])}&ndash;{clock(end)}</span></h2>")
        if sl["kind"] == "video":
            src = os.path.relpath(os.path.join(HERE, sl["props"]["file"]), os.path.dirname(out))
            body.append("<p><i>[The video is on its own slide in the organisers' deck. Click once to start it, and not again until it ends.]</i></p>"
                        f"<div class=\"vwrap live\"><video src=\"{e(src)}\" muted playsinline controls preload=\"auto\"></video></div>")
            data[-1]["beats"] = []
            for b in sl["beats"]:
                v0 = b["start"] - sl["start"]
                data[-1]["beats"].append({"num": b["num"], "v0": v0, "secs": b["secs"]})
                body.append(f"<div class=\"beat\" id=\"beat-{b['num']}\"><h3>Beat {b['num']}: {e(b['title'])} "
                            f"<span>video {clock(v0)}&ndash;{clock(v0 + b['secs'])} &middot; talk {clock(b['start'])}</span></h3>"
                            + paras(b["say"]) + "</div>")
        else:
            body.append(paras(sl["say"]))
        body.append("</section>")
    parts_json = json.dumps({"parts": data, "plan": total, "slot": slot}).replace("</", "<\\/")
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Script: {e(title)}</title>
<style>
 body {{ font: 17px/1.55 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; color: #262626;
        max-width: 46em; margin: 2em auto; padding: 0 1.2em; }}
 h1 {{ font-size: 1.5em; margin-bottom: .2em; }}
 .meta {{ color: #4d5558; margin-top: 0; }}
 table {{ border-collapse: collapse; margin: 1.2em 0 2em; font-size: .9em; }}
 th, td {{ text-align: left; padding: .3em .9em .3em 0; border-bottom: 1px solid #d5dcdd; }}
 h2 {{ font-size: 1.15em; color: #1c6a75; border-top: 2px solid #1c6a75; padding-top: .6em; margin-top: 2em; }}
 h3 {{ font-size: 1em; color: #1d5459; margin-bottom: .2em; }}
 h2 span, h3 span {{ float: right; font-weight: normal; color: #4d5558; font-size: .9em; }}
 p {{ margin: .5em 0 .9em; }}
 i {{ color: #b8520e; }}
 footer {{ color: #4d5558; font-size: .85em; margin-top: 3em; }}
 #bar {{ position: sticky; top: 0; z-index: 2; background: #fff; display: flex; gap: 1em; align-items: center;
        padding: .5em 0; border-bottom: 1px solid #d5dcdd; font-size: .9em; }}
 #bar button {{ font: inherit; padding: .2em .9em; }}
 #clocks {{ margin-left: auto; white-space: nowrap; font-variant-numeric: tabular-nums; }}
 #clocks span {{ margin-left: 1em; }}
 .over {{ color: #b8520e; font-weight: 600; }}
 section.cur {{ border-left: 4px solid #1c6a75; padding-left: .8em; margin-left: calc(-.8em - 4px); }}
 .beat {{ padding: 0 .5em; margin: 0 -.5em; }}
 .beat.cur {{ background: #e8f3f5; }}
 .vwrap {{ position: sticky; z-index: 1; background: #fff; padding: .3em 0; }}
 .vwrap video {{ width: 100%; display: block; background: #000; }}
 #result {{ background: #f3f5f5; padding: .8em 1em; font-size: .85em; }}
 @media print {{ body {{ font-size: 13pt; margin: 0; }} section {{ break-inside: avoid; }} .live, #bar, #result {{ display: none; }} }}
</style></head><body>
<div id="bar"><button id="go">Start</button><span id="now">Space starts the clock and moves to the next part. Esc stops.</span>
<span id="clocks"><span id="part"></span><span id="drift"></span></span></div>
<h1>{e(title)}</h1>
<p class="meta">{e(meta.get("presenter", ""))} &middot; {e(meta.get("session", ""))}<br>
Planned {clock(total)} of a {clock(slot)} slot &middot; {sum(s["words"] for s in slides)} spoken words</p>
<table><tr><th>Part</th><th>Title</th><th>Starts</th><th>Length</th><th>Words</th><th>Words/min</th><th class="live">Your run</th></tr>
{"".join(rows)}</table>
<pre id="result" hidden></pre>
{"".join(body)}
<footer>Generated from talk.md by build.py. Do not edit this file; edit talk.md and rebuild.</footer>
<script type="application/json" id="parts">{parts_json}</script>
<script>{REHEARSE_JS}</script>
</body></html>
"""
    open(out, "w", encoding="utf-8").write(page)


def on_slide(p, meta):
    """The audience-facing text of a slide, as (label, [lines]) blocks, for the review document."""
    if p["layout"] == "title":
        return [("", [meta.get("title", "").replace(" | ", " "), meta.get("subtitle", ""),
                      meta.get("authors", ""), meta.get("institution", ""), meta.get("session", "")])]
    out = []
    for name, b in p["sections"]:
        lines = [(f"{i['lead']} {i['text']}" if i["lead"] else i["text"]).strip() for i in b["items"]]
        lines += [" | ".join(r) for r in b["table"]]
        lines += [f"{k.title()}: {v}" for k, v in b["props"].items()]
        lines += [x for x in b["paras"] if x != b["url"]] + ([b["url"]] if b["url"] else [])
        lines += [f"> {b['quote']}"] if b["quote"] else []
        out.append((name, lines))
    return out


def build_docx(meta, parts, total, slot, out, old=None, since=""):
    """The spoken script as a Word file to edit and comment on, with Track Changes on. The grey text
    is what the audience sees, for reference. Changes are carried back into talk.md by hand.
    With `old` (the parts of an earlier talk.md), the spoken text shows every change since that
    version as a tracked change, word by word, so it can be accepted or rejected in Word."""
    from datetime import datetime, timezone
    from difflib import SequenceMatcher
    from itertools import groupby
    from docx import Document
    from docx.oxml import OxmlElement
    from docx.shared import Pt as DPt, RGBColor as DRGB
    teal, grey, orange = DRGB(0x1C, 0x6A, 0x75), DRGB(0x5F, 0x66, 0x69), DRGB(0xB8, 0x52, 0x0E)
    before = {}
    for p in old or []:
        if p["kind"] == "slide":
            before[("slide", p["num"])] = p["say"]
        for b in p["beats"]:
            before[("beat", b["num"])] = b["say"]
    rev, stamp = [0], datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    doc = Document()
    doc.styles["Normal"].font.name, doc.styles["Normal"].font.size = "Calibri", DPt(12)
    for s in ("Heading 1", "Heading 2"):
        doc.styles[s].font.color.rgb = teal

    def line(t, size=10, color=grey, bold=False, after=2):
        par = doc.add_paragraph()
        r = par.add_run(t)
        r.font.size, r.font.color.rgb, r.bold = DPt(size), color, bold
        par.paragraph_format.space_after = DPt(after)
        return par

    def tokens(text):                            # [(word with its trailing space, in a stage direction)]
        out, inside = [], False
        for t in re.findall(r"\S+\s*", text):
            out.append((t, inside or "[" in t))
            inside = (inside or "[" in t) and "]" not in t
        return out

    def put(par, toks, kind=None):               # kind: None, "ins" or "del" (a tracked change)
        for stage, grp in groupby(toks, key=lambda x: x[1]):
            r = par.add_run("".join(t for t, _ in grp))
            if stage:                            # [stage directions] in orange italics, not spoken
                r.italic, r.font.color.rgb = True, orange
            if kind:
                if kind == "del":
                    r._r.find(qn("w:t")).tag = qn("w:delText")
                rev[0] += 1
                w = OxmlElement(f"w:{kind}")
                for k, v in (("id", str(rev[0])), ("author", f"Changes since {since}"), ("date", stamp)):
                    w.set(qn(f"w:{k}"), v)
                r._r.addprevious(w)
                w.append(r._r)

    def spoken(ps, was=None):
        n = max(len(ps), len(was)) if was is not None else len(ps)
        for i in range(n):
            par = doc.add_paragraph()
            par.paragraph_format.space_after, par.paragraph_format.line_spacing = DPt(8), 1.25
            new = tokens(ps[i] if i < len(ps) else "")
            if was is None:
                put(par, new)
                continue
            a = tokens(was[i] if i < len(was) else "")
            ops = SequenceMatcher(None, [t.strip() for t, _ in a], [t.strip() for t, _ in new], autojunk=False).get_opcodes()
            spans = []                           # fold short matches ("the", "a model") into the change around them
            for k, (op, i1, i2, j1, j2) in enumerate(ops):
                change = op != "equal" or (i2 - i1 <= 3 and 0 < k < len(ops) - 1)
                if change and spans and spans[-1][0] == "change":
                    spans[-1] = ("change", spans[-1][1], i2, spans[-1][3], j2)
                else:
                    spans.append(("change" if change else "equal", i1, i2, j1, j2))
            for op, i1, i2, j1, j2 in spans:
                if op == "equal":
                    put(par, new[j1:j2])
                else:
                    put(par, a[i1:i2], "del")
                    put(par, new[j1:j2], "ins")

    title = meta.get("title", "").replace(" | ", " ")
    doc.add_heading(title, 0)
    line(f"{meta.get('presenter', '')} · {meta.get('session', '')}", 11)
    line(f"Spoken script, generated from talk.md on {__import__('datetime').date.today().isoformat()}. "
         f"Planned {clock(total)} of a {clock(slot)} slot, {sum(p['words'] for p in parts)} spoken words.", 11)
    line("Edit the black text freely; Track Changes is on, and comments are welcome. Grey text is what the "
         "audience sees and is frozen since the upload: changing it means re-uploading. In the video, the "
         "On screen times are seconds into the beat.", 11, after=10)
    table = doc.add_table(rows=1, cols=6)
    table.style = "Table Grid"
    for c, h in zip(table.rows[0].cells, ("Part", "Title", "Starts", "Length", "Words", "Words/min")):
        c.text = h
    for p in parts:
        tag = f"Slide {p['num']}" if p["kind"] == "slide" else "Video"
        for c, v in zip(table.add_row().cells, (tag, p["title"], clock(p["start"]), clock(p["secs"]),
                                                  str(p["words"]), f"{p['wpm']:.0f}")):
            c.text = v
    table.autofit, widths = False, (0.8, 3.0, 0.65, 0.7, 0.65, 0.9)
    for col, w in zip(table.columns, widths):       # the grid (LibreOffice) and every cell (Word)
        col.width = Inches(w)
    for i, row in enumerate(table.rows):
        for c, w in zip(row.cells, widths):
            c.width = Inches(w)
            for r in c.paragraphs[0].runs:
                r.font.size, r.bold = DPt(10), i == 0

    for p in parts:
        tag = f"Slide {p['num']}" if p["kind"] == "slide" else "Video"
        doc.add_heading(f"{tag}: {p['title']}", 1)
        line(f"{clock(p['start'])}–{clock(p['start'] + p['secs'])} · {p['secs']} s · "
             f"{p['words']} words · {p['wpm']:.0f} words/min", after=6)
        if p["kind"] == "slide":
            line("On the slide", bold=True)
            for name, lines in on_slide(p, meta):
                if name:
                    line(name, color=teal)
                for t in filter(None, lines):
                    line(t).paragraph_format.left_indent = DPt(14 if name else 0)
            doc.add_paragraph().paragraph_format.space_after = DPt(0)
            spoken(p["say"], before.get(("slide", p["num"]), []) if old else None)
            continue
        cues = video_cues()
        for b in p["beats"]:
            v0 = b["start"] - p["start"]
            doc.add_heading(f"Beat {b['num']}: {b['title']}", 2)
            line(f"video {clock(v0)}–{clock(v0 + b['secs'])} · talk {clock(b['start'])} · {b['secs']} s · "
                 f"{b['words']} words · {b['words'] / (b['secs'] / 60):.0f} words/min", after=6)
            line("On screen", bold=True)
            for t, what in cues.get(b["num"], []):
                line(f"{clock(int(round(t)))}   {what}")
            doc.add_paragraph().paragraph_format.space_after = DPt(0)
            spoken(b["say"], before.get(("beat", b["num"]), []) if old else None)
    settings = doc.settings.element                 # open with Track Changes on
    zoom = settings.find(qn("w:zoom"))              # python-docx's template omits a required attribute
    if zoom is not None and zoom.get(qn("w:percent")) is None:
        zoom.set(qn("w:percent"), "100")
    track = OxmlElement("w:trackRevisions")
    anchor = settings.find(qn("w:defaultTabStop"))
    anchor.addprevious(track) if anchor is not None else settings.append(track)
    doc.save(out)


def visible_content(meta, parts):
    """What the audience sees, and the video's cut: everything except the spoken text, the
    slide times and the pace settings, which rehearsal may still change."""
    out = {"meta": {k: v for k, v in meta.items() if k not in ("pace", "slot", "max slides")}, "parts": []}
    for p in parts:
        if p["kind"] == "slide":
            out["parts"].append({"slide": p["num"], "title": p["title"],
                                 "props": {k: v for k, v in p["props"].items() if k != "time"},
                                 "sections": [[n, {k: b[k] for k in ("items", "props", "table", "quote", "paras", "url")}]
                                              for n, b in p["sections"]]})
        else:
            out["parts"].append({"video": p["title"], "props": p["props"],
                                 "beats": [[b["num"], b["title"], b["secs"]] for b in p["beats"]]})
    return out


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def check_frozen(meta, parts):
    """If frozen.json exists, the audience-facing content must not change."""
    if not os.path.exists(FROZEN):
        return
    frozen = json.load(open(FROZEN))
    now = visible_content(meta, parts)
    if now == frozen["content"]:
        return
    was = {json.dumps(p, sort_keys=True) for p in frozen["content"]["parts"]}
    changed = [f"slide {p['slide']}" if "slide" in p else "the video"
               for p in now["parts"] if json.dumps(p, sort_keys=True) not in was]
    if now["meta"] != frozen["content"]["meta"]:
        changed.insert(0, "title slide (Meta)")
    die(f"the slides and video are frozen since {frozen['frozen']} (uploaded to the organisers), but the "
        f"visible content of {', '.join(changed)} changed in talk.md. Only the Say and Beat text, "
        "slide times and pace may change now. Undo that edit, or delete frozen.json to unfreeze.")


def main():
    meta, slides = parse_talk(SRC)
    if "--freeze" in sys.argv[1:]:
        deck = os.path.join(BUILD, meta.get("output", "talk") + ".pptx")
        video = next((os.path.join(HERE, p["props"]["file"]) for p in slides if p["kind"] == "video"), None)
        record = {"frozen": __import__("datetime").date.today().isoformat(),
                  "note": "Snapshot of what the audience sees, taken when the deck and video were uploaded.",
                  "uploaded": {os.path.basename(f): sha256(f) for f in (deck, video) if f and os.path.exists(f)},
                  "content": visible_content(meta, slides)}
        json.dump(record, open(FROZEN, "w"), indent=1, sort_keys=True)
        print(f"froze the visible content in {os.path.relpath(FROZEN, HERE)}")
        return
    check_frozen(meta, slides)
    total, slot = check(meta, slides)
    os.makedirs(BUILD, exist_ok=True)
    deck = os.path.join(BUILD, meta.get("output", "talk") + ".pptx")
    script = os.path.join(BUILD, "script.html")
    word = os.path.join(BUILD, meta.get("output", "talk") + "_script.docx")
    build_pptx(meta, slides, deck)
    build_script(meta, slides, total, slot, script)
    build_docx(meta, slides, total, slot, word)
    phone = os.path.join(BUILD, meta.get("output", "talk") + "_script_phone.pdf")
    build_phone_pdf(meta, slides, total, slot, phone)
    qa = os.path.join(BUILD, meta.get("output", "talk") + "_qa_phone.pdf")
    if os.path.exists(QA_MD):
        build_qa_pdf(QA_MD, qa, meta.get("presenter", ""))
    if "--notes-into" in sys.argv[1:]:           # the organisers' final deck, video on its own slide
        given = (sys.argv[sys.argv.index("--notes-into") + 1:] or die("--notes-into needs a .pptx"))[0]
        final = os.path.join(BUILD, os.path.basename(given))
        if os.path.abspath(given) == os.path.abspath(final):
            die("--notes-into: pass the original deck, not the copy in build/")
        notes_into(slides, given, final)
        print(f"speaker notes from talk.md -> {os.path.relpath(final, HERE)} (a copy of {given})")
    if "--changes-since" in sys.argv[1:]:        # a file, or a git revision of talk.md
        since = (sys.argv[sys.argv.index("--changes-since") + 1:] or die("--changes-since needs a file or a git revision"))[0]
        if os.path.isfile(since):
            old_md = open(since, encoding="utf-8").read()
        else:
            import subprocess
            got = subprocess.run(["git", "-C", HERE, "show", f"{since}:./talk.md"], capture_output=True, text=True)
            old_md = got.stdout if got.returncode == 0 else die(f"--changes-since: {got.stderr.strip()}")
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(old_md)
        changes = os.path.join(BUILD, meta.get("output", "talk") + "_script_changes.docx")
        build_docx(meta, slides, total, slot, changes, parse_talk(f.name)[1], os.path.basename(since))
        os.unlink(f.name)
        print(f"talk.md changes since {since} -> {os.path.relpath(changes, HERE)}")

    print(f"talk.md -> {os.path.relpath(deck, HERE)}, {os.path.relpath(script, HERE)}, {os.path.relpath(word, HERE)}, "
          f"{os.path.relpath(phone, HERE)}, {os.path.relpath(qa, HERE)}\n")
    print(f"  {'part':<8}{'layout':<18}{'starts':>7}{'length':>8}{'words':>7}{'words/min':>11}")
    for s in slides:
        tag = str(s["num"]) if s["kind"] == "slide" else "video"
        print(f"  {tag:<8}{s['layout']:<18}{clock(s['start']):>7}{clock(s['secs']):>8}{s['words']:>7}{s['wpm']:>11.0f}")
    n_slides = sum(1 for s in slides if s["kind"] == "slide")
    print(f"  {'total':<26}{'':>7}{clock(total):>8}{sum(s['words'] for s in slides):>7}"
          f"   (slot {clock(slot)}, {n_slides} slides + video)\n")
    if errors:
        print("CHECKS FAILED:")
        for msg in errors:
            print("  - " + msg)
        sys.exit(1)
    print("checks: OK")


if __name__ == "__main__":
    main()
