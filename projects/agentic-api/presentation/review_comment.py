#!/usr/bin/env python3
"""Add review comments to a copy of a Word file, each anchored to an exact piece of text.

    python3 review_comment.py IN.docx OUT.docx COMMENTS.json [--author NAME]

COMMENTS.json is a list of [anchor, comment] pairs. Each anchor must occur in exactly one
paragraph of IN.docx (outside tables), within one run of text and not inside a tracked change.
A heading such as "Slide 3: ..." is a good anchor for a comment about a whole slide.

Used in the review rounds (see method.md): build the script .docx, then comment on a copy in
review/. Writes nothing if any anchor is missing or ambiguous. Needs python-docx >= 1.2.
"""

import copy
import json
import sys

from docx import Document
from docx.text.run import Run


def isolate(par, text):
    """Split the run holding `text` so that `text` is a run of its own; return that run."""
    for run in par.runs:
        i = run.text.find(text)
        if i < 0:
            continue
        before, after = run.text[:i], run.text[i + len(text):]
        run.text = text
        if before:
            r = copy.deepcopy(run._r)
            run._r.addprevious(r)
            Run(r, par).text = before
        if after:
            r = copy.deepcopy(run._r)
            run._r.addnext(r)
            Run(r, par).text = after
        return run
    return None


def main():
    args = sys.argv[1:]
    author = "Claude"
    if "--author" in args:
        k = args.index("--author")
        author = args[k + 1]
        del args[k:k + 2]
    if len(args) != 3:
        sys.exit(__doc__.split("\n\n")[1])
    src, out, notes = args
    doc = Document(src)
    comments = json.load(open(notes, encoding="utf-8"))
    for anchor, note in comments:
        hits = [p for p in doc.paragraphs if anchor in p.text]
        if len(hits) != 1:
            sys.exit(f"review_comment.py: anchor found in {len(hits)} paragraphs, need 1: {anchor!r}")
        run = isolate(hits[0], anchor)
        if run is None:
            sys.exit(f"review_comment.py: anchor spans runs or a tracked change: {anchor!r}")
        doc.add_comment(run, text=note, author=author, initials=author[:1])
    doc.save(out)
    print(f"{len(comments)} comments -> {out}")


if __name__ == "__main__":
    main()
