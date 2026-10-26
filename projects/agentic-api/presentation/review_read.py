#!/usr/bin/env python3
"""Report what came back in a reviewed Word file: tracked changes, comments, and decisions.

    python3 review_read.py REVIEWED.docx [--against BUILT.docx]

Prints, for each paragraph that still has tracked changes, who made them and the text with all
changes accepted and with all rejected; then every comment with the text it is anchored to,
whether it is resolved, and replies under their parent.

A change that was accepted or rejected leaves no trace in the file. To see those decisions, pass
--against with a fresh build of the version that was sent out: every body paragraph whose text
(all pending changes accepted) differs from it is listed. See method.md, "Review rounds in Word".
"""

import difflib
import re
import sys
import zipfile
from collections import Counter

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
W15 = "http://schemas.microsoft.com/office/word/2012/wordml"


def q(tag, ns=W):
    return f"{{{ns}}}{tag}"


def norm(s):
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("“", '"').replace("”", '"')).strip()


def part(z, name):
    return etree.fromstring(z.read(name)) if name in z.namelist() else None


def view(p):
    """(text with every change accepted, text with every change rejected, Counter of authors)"""
    acc, rej, who = [], [], Counter()
    for el in p.iter():
        if el.tag == q("t"):
            ins = next((a for a in el.iterancestors() if a.tag == q("ins")), None)
            acc.append(el.text or "")
            if ins is None:
                rej.append(el.text or "")
            else:
                who[ins.get(q("author"))] += 1
        elif el.tag == q("delText"):
            d = next((a for a in el.iterancestors() if a.tag == q("del")), None)
            rej.append(el.text or "")
            who[d.get(q("author")) if d is not None else "?"] += 1
        elif el.tag in (q("ins"), q("del")) and el.getparent().tag == q("rPr"):
            who[f"{el.get(q('author'))} (paragraph mark)"] += 1
    return "".join(acc), "".join(rej), who


def body_text(path):
    """Accepted text of each top-level body paragraph (tables and comments left out)."""
    body = etree.fromstring(zipfile.ZipFile(path).read("word/document.xml")).find(q("body"))
    return [norm(view(p)[0]) for p in body.iterchildren(q("p"))]


def main():
    args = sys.argv[1:]
    against = None
    if "--against" in args:
        k = args.index("--against")
        against = args[k + 1]
        del args[k:k + 2]
    if len(args) != 1:
        sys.exit(__doc__.split("\n\n")[1])
    z = zipfile.ZipFile(args[0])
    paras = list(part(z, "word/document.xml").iter(q("p")))

    print("=== Pending tracked changes ===")
    for i, p in enumerate(paras):
        acc, rej, who = view(p)
        if who:
            print(f"\n[paragraph {i}] by {dict(who)}\n  accept all: {acc}\n  reject all: {rej}")

    anchors, open_ = {}, {}
    for i, p in enumerate(paras):
        for el in p.iter():
            if el.tag == q("commentRangeStart"):
                open_[el.get(q("id"))] = []
            elif el.tag in (q("t"), q("delText")):
                for k in open_:
                    open_[k].append(el.text or "")
            elif el.tag == q("commentRangeEnd"):
                cid = el.get(q("id"))
                anchors[cid] = "".join(open_.pop(cid, []))

    print("\n=== Comments ===")
    cm, ext = part(z, "word/comments.xml"), part(z, "word/commentsExtended.xml")
    ex = list(ext.iter(q("commentEx", W15))) if ext is not None else []
    parent = {e.get(q("paraId", W15)): e.get(q("paraIdParent", W15)) for e in ex}
    done = {e.get(q("paraId", W15)): e.get(q("done", W15)) for e in ex}
    comments = list(cm.iter(q("comment"))) if cm is not None else []
    last_para = {c.get(q("id")): (c.findall(q("p")) or [None])[-1] for c in comments}
    pid = {cid: (p.get(q("paraId", W14)) if p is not None else None) for cid, p in last_para.items()}
    by_pid = {v: k for k, v in pid.items()}
    for c in comments:
        cid = c.get(q("id"))
        text = " / ".join("".join(t.text or "" for t in p.iter(q("t"))) for p in c.findall(q("p")))
        up = parent.get(pid[cid])
        where = f"reply to #{by_pid.get(up)}" if up else f"on {anchors.get(cid, '?')[:100]!r}"
        state = "resolved" if done.get(pid[cid]) == "1" else "open"
        print(f"\n#{cid} {c.get(q('author'))} [{state}] {where}\n   {text}")

    if against:
        sent, back = body_text(against), body_text(args[0])
        print(f"\n=== Differences from {against} ===")
        found = False
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, sent, back, autojunk=False).get_opcodes():
            if op != "equal":
                found = True
                for t in sent[i1:i2]:
                    print(f"  sent    : {t}")
                for t in back[j1:j2]:
                    print(f"  returned: {t}")
        if not found:
            print("  none: every paragraph matches")


if __name__ == "__main__":
    main()
