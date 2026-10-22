#!/usr/bin/env python3
"""Build the CAIMI26 talk from talk.md (the source of truth).

    python3 build.py

Writes build/<output>.pptx (slides + speaker notes) and build/script.html (the
spoken script with a running clock). Re-run after ANY edit to talk.md; never
edit the files in build/ by hand, they are overwritten.

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
def notes_text(p):
    span = f"[{clock(p['start'])}-{clock(p['start'] + p['secs'])}]"
    if p["kind"] == "slide":
        return span + "\n" + "\n\n".join(p["say"])
    out = [f"{span}  NOW PLAY THE DEMO VIDEO ({clock(p['secs'])}), from outside PowerPoint. Narrate:"]
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


def build_script(meta, slides, total, slot, out):
    e = html.escape
    title = meta.get("title", "").replace(" | ", " ")

    def paras(ps):                               # [stage directions] in italics
        return "".join("<p>" + re.sub(r"(\[.*?\])", r"<i>\1</i>", e(p)) + "</p>" for p in ps)

    rows, body = [], []
    for sl in slides:
        end = sl["start"] + sl["secs"]
        tag = f"Slide {sl['num']}" if sl["kind"] == "slide" else "Video"
        rows.append(f"<tr><td>{tag}</td><td>{e(sl['title'])}</td><td>{clock(sl['start'])}</td>"
                    f"<td>{clock(sl['secs'])}</td><td>{sl['words']}</td><td>{sl['wpm']:.0f}</td></tr>")
        body.append(f"<section><h2>{tag}: {e(sl['title'])} "
                    f"<span>{clock(sl['start'])}&ndash;{clock(end)}</span></h2>")
        if sl["kind"] == "video":
            body.append("<p><i>[Play the MP4 from outside PowerPoint.]</i></p>")
            for b in sl["beats"]:
                v0 = b["start"] - sl["start"]
                body.append(f"<h3>Beat {b['num']}: {e(b['title'])} <span>video {clock(v0)}&ndash;"
                            f"{clock(v0 + b['secs'])} &middot; talk {clock(b['start'])}</span></h3>" + paras(b["say"]))
        else:
            body.append(paras(sl["say"]))
        body.append("</section>")
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
 @media print {{ body {{ font-size: 13pt; margin: 0; }} section {{ break-inside: avoid; }} }}
</style></head><body>
<h1>{e(title)}</h1>
<p class="meta">{e(meta.get("presenter", ""))} &middot; {e(meta.get("session", ""))}<br>
Planned {clock(total)} of a {clock(slot)} slot &middot; {sum(s["words"] for s in slides)} spoken words</p>
<table><tr><th>Part</th><th>Title</th><th>Starts</th><th>Length</th><th>Words</th><th>Words/min</th></tr>
{"".join(rows)}</table>
{"".join(body)}
<footer>Generated from talk.md by build.py. Do not edit this file; edit talk.md and rebuild.</footer>
</body></html>
"""
    open(out, "w", encoding="utf-8").write(page)


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
    build_pptx(meta, slides, deck)
    build_script(meta, slides, total, slot, script)

    print(f"talk.md -> {os.path.relpath(deck, HERE)}, {os.path.relpath(script, HERE)}\n")
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
