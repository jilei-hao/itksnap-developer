#!/usr/bin/env python3
"""Build caimi_submission.docx from caimi_submission.md (the source of truth).

    python3 build_caimi_submission.py

Standard library only — no pip install, no node_modules. Re-run after ANY edit to
caimi_submission.md; never edit the .docx by hand, it is overwritten.

Also prints a per-field word count against the form's 250-word cap, and exits
non-zero if any field is over, so this doubles as the pre-submit check.
"""

import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
# Optional args:  build_caimi_submission.py [source.md] [output.docx]
# Defaults to the working draft in this directory. Used with explicit paths to
# regenerate ../caimi-submission/caimi_submitted.docx (the as-submitted record).
SRC = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, "caimi_submission.md")
OUT = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.splitext(SRC)[0] + ".docx"

NAVY, GREY, DARK, RED = "1F3864", "595959", "333333", "C00000"
LIMIT = 250

# ── parse markdown ──────────────────────────────────────────────────────────
raw = open(SRC, encoding="utf-8").read()
md = re.sub(r"<!--.*?-->", "", raw, flags=re.S)

sections = []
for part in re.split(r"^# ", md, flags=re.M)[1:]:
    head, _, body = part.partition("\n")
    sections.append((head.strip(), re.split(r"^---$", body, flags=re.M)[0].strip()))

is_field = lambda h: bool(re.match(r"^\d+\.", h))
# fields 1-4 are the title and the two dropdowns + the uncapped demo blurb
is_capped = lambda h: is_field(h) and not re.match(r"^[1-4]\.", h)


def wc(t):
    t = re.sub(r"\*\*(.*?)\*\*", r"\1", t).replace("`", "")
    return len([w for w in t.split() if w])


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ── XML helpers ─────────────────────────────────────────────────────────────
def rpr(size=22, bold=False, italic=False, color=None, mono=False):
    x = ""
    if mono:
        x += ('<w:rFonts w:ascii="Consolas" w:cs="Consolas" '
              'w:eastAsia="Consolas" w:hAnsi="Consolas"/>')
    if bold:
        x += "<w:b/><w:bCs/>"
    if italic:
        x += "<w:i/><w:iCs/>"
    if color:
        x += f'<w:color w:val="{color}"/>'
    x += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
    return f"<w:rPr>{x}</w:rPr>"


def run(text, **kw):
    return f'<w:r>{rpr(**kw)}<w:t xml:space="preserve">{esc(text)}</w:t></w:r>'


def para(runs_xml, style=None, before=0, after=160, line=None, ind=None,
         shade=None, tabs=None, border=False):
    # CT_PPr child order is schema-enforced: pStyle, pBdr, shd, tabs, spacing, ind
    p = "<w:pPr>"
    if style:
        p += f'<w:pStyle w:val="{style}"/>'
    if border:
        p += ('<w:pBdr><w:bottom w:val="single" w:sz="6" w:space="8" '
              'w:color="BFBFBF"/></w:pBdr>')
    if shade:
        p += f'<w:shd w:val="clear" w:fill="{shade}"/>'
    if tabs:
        p += f'<w:tabs><w:tab w:val="right" w:pos="{tabs}"/></w:tabs>'
    sp = f'<w:spacing w:after="{after}" w:before="{before}"'
    if line:
        sp += f' w:line="{line}"'
    p += sp + "/>"
    if ind:
        p += f"<w:ind {ind}/>"
    p += "</w:pPr>"
    return f"<w:p>{p}{runs_xml}</w:p>"


def inline(text, size=22):
    """Render **bold**, *italic* and `code` inside a line."""
    out, last = "", 0
    for m in re.finditer(r"(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|`[^`]+`)", text):
        if m.start() > last:
            out += run(text[last:m.start()], size=size)
        tok = m.group(0)
        if tok.startswith("**"):
            out += run(tok[2:-2], size=size, bold=True)
        elif tok.startswith("*"):
            out += run(tok[1:-1], size=size, italic=True)
        else:
            out += run(tok[1:-1], size=19, mono=True)
        last = m.end()
    if last < len(text):
        out += run(text[last:], size=size)
    return out or run(text, size=size)


# ── build body ──────────────────────────────────────────────────────────────
body_xml = []
A = body_xml.append

title = next(b for h, b in sections if h.startswith("1."))
# A "meta:" block of "- key: value" bullets marks an as-submitted record and supplies the
# header lines; without it this is the working draft.
meta = next((b for h, b in sections if h.strip().lower() == "meta"), None)
subtitle = ("As submitted — text verified against the portal preview"
            if meta else "Submission text, mapped to the portal form")
A(para(run("SIIM-CAIMI26 · AI Builder Showcase", size=18, bold=True, color=GREY), after=40))
A(para(run(subtitle, size=18, italic=True, color=GREY), after=60, border=True))
A(para(run(title, size=26, bold=True, color=NAVY), before=200, after=40))
if meta:
    hdr = [re.sub(r"^\s*[-•]\s*", "", l).strip() for l in meta.split("\n") if l.strip()]
else:
    hdr = [
        "Presenting author: Jilei Hao   ·   Co-authors / affiliation: TO CONFIRM",
        "Portal EventKey: QRFBVSUS   ·   Each field is capped at 250 words; there is no overall limit.",
    ]
hdr.append(f"Generated from {os.path.basename(SRC)} — edit the markdown, then rebuild. "
           "Do not edit this file directly.")
for line in hdr:
    A(para(inline(line, size=17) if "**" in line or "*" in line
           else run(line, size=17, color=GREY), after=40))
A(para(run("", size=12), after=160, border=True))

over = []
for head, body in sections:
    if head.strip().lower() == "meta":      # consumed above as header lines
        continue
    words = wc(body)
    if is_capped(head) and words > LIMIT:
        over.append((head, words))

    # Word count goes on its own line: a right-tabbed count overflows and wraps
    # awkwardly whenever the heading itself nearly fills the line.
    A(para(run(head, size=23, bold=True, color=NAVY),
           style="Heading1", before=300, after=20 if is_capped(head) else 100))
    if is_capped(head):
        A(para(run(f"{words} / {LIMIT} words", size=16, italic=True,
                   color=RED if words > LIMIT else GREY), after=100))

    # Split fenced blocks out FIRST — a fenced block may contain blank lines, so
    # splitting on blank lines first would strand the closing ``` as its own block.
    for seg in re.split(r"(```.*?```)", body, flags=re.S):
        if not seg.strip():
            continue
        if seg.startswith("```"):
            lines = seg.strip()[3:-3].split("\n")
            while lines and not lines[0].strip():
                lines.pop(0)
            while lines and not lines[-1].strip():
                lines.pop()
            for i, l in enumerate(lines):
                A(para(run(l or " ", size=19, mono=True), shade="F5F5F5", line=240,
                       after=200 if i == len(lines) - 1 else 0,
                       ind='w:left="288" w:right="288"'))
            continue
        for block in re.split(r"\n{2,}", seg.strip()):
            for line in block.split("\n"):
                mli = re.match(r"^\s*[-•]\s+(.*)$", line)
                mnum = re.match(r"^(\d+)\.\s+(.*)$", line)
                if mli:
                    A(para(run("• ") + inline(mli.group(1)), after=60,
                           ind='w:left="432" w:hanging="216"'))
                elif mnum:
                    A(para(run(f"{mnum.group(1)}. ") + inline(mnum.group(2)), after=60,
                           ind='w:left="432" w:hanging="216"'))
                else:
                    A(para(inline(line), after=160, line=276))

NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')

document = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    f"<w:document {NS}><w:body>" + "".join(body_xml) +
    '<w:sectPr><w:footerReference w:type="default" r:id="rId1"/>'
    '<w:pgSz w:w="12240" w:h="15840" w:orient="portrait"/>'
    '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
    'w:header="708" w:footer="708" w:gutter="0"/>'
    "</w:sectPr></w:body></w:document>"
)

styles = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    f"<w:styles {NS}>"
    "<w:docDefaults><w:rPrDefault><w:rPr>"
    '<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/>'
    '<w:sz w:val="22"/><w:szCs w:val="22"/>'
    "</w:rPr></w:rPrDefault></w:docDefaults>"
    '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
    '<w:name w:val="Normal"/></w:style>'
    '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/>'
    '<w:basedOn w:val="Normal"/><w:pPr><w:outlineLvl w:val="0"/></w:pPr>'
    f'<w:rPr><w:b/><w:color w:val="{NAVY}"/><w:sz w:val="23"/></w:rPr></w:style>'
    "</w:styles>"
)

footer = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    f"<w:ftr {NS}><w:p><w:pPr><w:jc w:val=\"right\"/></w:pPr>"
    + run("SIIM-CAIMI26 · AI Builder Showcase — page ", size=16, color=GREY)
    + f'<w:fldSimple w:instr=" PAGE ">{run("1", size=16, color=DARK)}</w:fldSimple>'
    + "</w:p></w:ftr>"
)

content_types = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
    '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
    '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
    "</Types>"
)

root_rels = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
    "</Relationships>"
)

doc_rels = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    "</Relationships>"
)

core = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
    'xmlns:dc="http://purl.org/dc/elements/1.1/">'
    "<dc:title>SIIM-CAIMI26 AI Builder Showcase submission</dc:title>"
    "<dc:creator>Jilei Hao</dc:creator>"
    "</cp:coreProperties>"
)

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", content_types)
    z.writestr("_rels/.rels", root_rels)
    z.writestr("word/document.xml", document)
    z.writestr("word/styles.xml", styles)
    z.writestr("word/footer1.xml", footer)
    z.writestr("word/_rels/document.xml.rels", doc_rels)
    z.writestr("docProps/core.xml", core)

print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)\n")
print(f"{'words':>6}  field")
for head, body in sections:
    if not is_field(head):
        continue
    n = wc(body)
    flag = f"   *** OVER by {n - LIMIT} ***" if (is_capped(head) and n > LIMIT) else ""
    print(f"{n:>6}  {head[:70]}{flag}")

if over:
    print("\nFAIL: {} field(s) over the 250-word cap".format(len(over)), file=sys.stderr)
    sys.exit(1)
print("\nAll fields within limits.")
