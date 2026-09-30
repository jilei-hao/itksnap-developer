# Carry the translations #196 changed (relative to its base) onto upstream's
# current .ts file, keeping upstream's layout byte-for-byte elsewhere.
import re, sys, html
sp = sys.argv[1]
def raw_messages(text):
    """Map (context, source-raw, comment-raw) -> (start, end) of the <translation ...>...</translation> element."""
    out = {}
    for cm in re.finditer(r'<context>\s*<name>(.*?)</name>(.*?)</context>', text, re.S):
        cname = cm.group(1); cstart = cm.start(2)
        for mm in re.finditer(r'<message[^>]*>(.*?)</message>', cm.group(2), re.S):
            body = mm.group(1); bstart = cstart + mm.start(1)
            src = re.search(r'<source>(.*?)</source>', body, re.S)
            com = re.search(r'<comment>(.*?)</comment>', body, re.S)
            tr = re.search(r'<translation[^>]*?(?:/>|>.*?</translation>)', body, re.S)
            key = (cname, src.group(1) if src else '', com.group(1) if com else '')
            out[key] = (bstart + tr.start(), bstart + tr.end()) if tr else None
    return out
base, pr, up = (open(f'{sp}/zh_{n}.ts', encoding='utf-8').read() for n in ('base', 'pr', 'up'))
mb, mp, mu = raw_messages(base), raw_messages(pr), raw_messages(up)
def tr(text, span): return text[span[0]:span[1]]
import xml.etree.ElementTree as ET
def txt(t, span): return ''.join(ET.fromstring(tr(t, span)).itertext())
changed = [k for k in mb if k in mp and mb[k] and mp[k] and txt(base, mb[k]) != txt(pr, mp[k])]
print('messages whose translation element differs (raw):', len(changed))
edits = []
for k in changed:
    if k not in mu or not mu[k]: print('MISSING upstream:', k[:2]); continue
    if tr(up, mu[k]) != tr(base, mb[k]): print('UPSTREAM CHANGED TOO:', k[:2]); continue
    edits.append((mu[k], tr(pr, mp[k])))
out = up
for (s, e), new in sorted(edits, key=lambda x: -x[0][0]):
    out = out[:s] + new + out[e:]
open(f'{sp}/itksnap_zh_CN.ported.ts', 'w', encoding='utf-8').write(out)
print('applied', len(edits))
