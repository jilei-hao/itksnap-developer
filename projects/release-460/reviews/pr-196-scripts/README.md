# #196 port

`ts_port.py` carries the translations #196 changed onto master's current `itksnap_zh_CN.ts`, and
keeps master's layout everywhere else.

It expects three files in the directory given as its argument. From the wrapper root:

```bash
D=$(mktemp -d); F=GUI/Qt/Translations/itksnap_zh_CN.ts
git -C itksnap fetch upstream pull/196/head:refs/pr/196
git -C itksnap show eabaa818:$F > $D/zh_base.ts
git -C itksnap show refs/pr/196:$F > $D/zh_pr.ts
git -C itksnap show upstream/master:$F > $D/zh_up.ts
python3 projects/release-460/reviews/pr-196-scripts/ts_port.py $D   # writes $D/itksnap_zh_CN.ported.ts
lrelease $D/itksnap_zh_CN.ported.ts -qm $D/check.qm                  # must compile
```

Expected output: "applied 33". A diff against `zh_up.ts` shows 33 changed lines.
