# Demoing remote data access — runbook

For shots 1, 2, 3 and 6 of the ITK-SNAP 4.6 talk. Everything below was checked against the source
and, where noted, run on this machine on 2026-08-06.

---

## 1. Demo the workflow change, not the feature list

The weak version of this demo is "ITK-SNAP supports five URL schemes." Nobody in a cardiac lab
cares. The strong version is a **before/after in the viewer's own working life**:

> Today: find the study in Flywheel → download it → remember where you put it → open it → later,
> wonder whether your copy is still the current one.
>
> In 4.6: paste the URL. That's the whole workflow.

So open on the *contrast*, not on the capability. One sentence of narration before the first click:
*"This is the part where I'd normally go download a file."*

**The single most persuasive shot is not the open dialog — it's the OS handler.** Clicking a link
and having ITK-SNAP come to the front with the study already loaded is the thing people repeat to
their colleagues afterwards. Lead with that if you only have one shot.

---

## 2. What to use as material

### Your own data — for the hero shots

You need a file **big enough that the progress overlay is visible for ~3–6 seconds.** Too small and
there's no progress bar, which kills both the "no download step" beat and the cancel shot. Too big
and the take drags. Pick something in that window and stick with it across takes.

### Public fallback — verified working today

If the Flywheel or SSH take fails on recording day, these are public, need no credentials, and are
exercised by the test suite. **I ran both on this machine today and both passed.**

```
https://raw.githubusercontent.com/pyushkevich/itksnap/refs/heads/master/Testing/TestData/MRIcrop-orig.gipl.gz
```
```
https://raw.githubusercontent.com/pyushkevich/itksnap/refs/heads/master/Testing/TestData/MRIcrop-with-mesh.itksnap
```

The second is a **workspace containing a mesh layer**, which is exactly what shot 3 needs.

Caveat: both are small and download almost instantly, so they make a poor progress/cancel shot.
They are a safety net for "the image loads from a URL", not a substitute for your own data.

---

## 3. URL forms — which one goes where

| Where | Form | Example |
|---|---|---|
| ITK-SNAP's open dialog | plain scheme | `fw://example.flywheel.io/acquisitions/<id>/files/brain.nii.gz` |
| Terminal / a link / an email | `itksnap-` prefixed | `itksnap-fw://…` |
| Command line, image | `-g <url>` | `ITK-SNAP -g "sftp://host/path/img.nii.gz"` |
| Command line, workspace | `-w <url>` | `ITK-SNAP -w "https://…/study.itksnap"` |
| OS handler / single-instance | `--url <url>` | auto-detects workspace vs image |

On macOS the handler shot is simply:

```bash
open "itksnap-fw://example.flywheel.io/acquisitions/<id>/files/brain.nii.gz"
```

`--url` also does **single-instance forwarding**: an *image* URL is sent to an already-running
ITK-SNAP over IPC, while a *workspace* URL always opens a new window. Worth knowing so the shot
behaves the way you expect — if you want a new window, use a workspace.

Flywheel URLs come in two forms. The **ID form** is what workspaces store internally; the
**label form** (`fw://<server>/find/<group>/<project>/<subject>/<session>/acquisitions/<label>/files/<file>`)
is the readable one. For a demo, the label form is far better on screen — a viewer can actually read
the hierarchy and see that it maps to their own study structure.

---

## 4. Before you record

**Authentication — get the dialogs out of the way, or show them deliberately.**

- **SSH**: public-key auth is tried first, then it prompts. **Credentials are not stored between
  sessions**, so if your keys aren't set up you will get a password dialog on *every take*. Either
  fix the keys for a clean run, or decide the prompt is part of the story and show it once.
- **Flywheel**: the key is read from `~/.fw/config.yml`. Run `fw login` beforehand and the dialog
  never appears. If that file is missing, ITK-SNAP prompts — and **your key is on screen as you
  type it.**

**Prime or clear the cache, depending on the shot.**

The cache lives at:

```
~/Library/Application Support/itksnap.org/ITK-SNAP/Cache/
~/Library/Application Support/itksnap.org/ITK-SNAP/CacheMetadata.xml
```

Neither exists on this machine yet, so your first GUI remote open will create them. For the
"first open downloads, second open is instant" pair:

```bash
rm -rf ~/Library/Application\ Support/itksnap.org/ITK-SNAP/Cache \
       ~/Library/Application\ Support/itksnap.org/ITK-SNAP/CacheMetadata.xml
```

Do that **between takes**, or your "first" open will silently be a cache hit and the progress bar
you were counting on won't appear.

**Scrub before you hit record.** Three places the URL is visible, not one:

1. the open dialog / terminal you paste into,
2. the **Remote URL field in General Layer Properties** — new in 4.6, and easy to forget,
3. the window title.

`scp://user@host/...` exposes a username and a hostname in all three. Check filenames for PHI too.

---

## 5. ⚠️ The one thing that will crash the app

**During a remote download, do not touch anything except the X on the progress overlay.**

This is not caution for its own sake — it is a confirmed defect found in this week's audit
(W8 item 30). The progress overlay pumps the event loop while downloading, but it is **not modal**,
so clicks reach the main window underneath. `File ▸ Close All`, unloading a layer, or opening
another workspace mid-download re-enters teardown *inside* the still-running open; when the outer
open resumes, it operates on a layer set that changed underneath it.

The **X button is the supported cancel path and is safe** — that is what shot 2 uses. Everything
else during a download is unsafe until item 30 is fixed.

If you are demoing live rather than from tape, this is the single highest-risk moment in the talk.

---

## 6. Pace the takes

The three remote regression tests fail when run **back-to-back** but pass individually — shared
cache state or server rate limiting (W8 item 3/3b, unresolved). The same shape can bite a demo that
chains several remote opens in quick succession.

Leave a few seconds between remote opens. Don't stack three loads into ten seconds of footage.

---

## 7. Suggested sequence (~2:45)

| # | Shot | Time | The line to say |
|---|---|---|---|
| 1 | Click an `itksnap-fw://` link (browser or `open`) — ITK-SNAP comes forward with the study loaded | 0:45 | "This is the part where I'd normally go download a file." |
| 2 | Start a larger remote load; let the progress overlay run; cancel with the **X** | 0:30 | "It's not frozen, and you can stop it." |
| 3 | Open a **workspace** from a URL — several layers, one authentication | 0:45 | "Four layers, one connection, one login." |
| 4 | Show the **Remote URL** field in layer properties | 0:15 | "The layer remembers where it came from." |
| 5 | Re-open the same image — instant, from cache | 0:20 | "And it doesn't download it twice." |

Shot 4 is worth adding to the original list: it's the answer to *"how do I know my copy is the
current one?"*, which is the first question a careful user asks about this feature.

---

## 8. If someone asks what doesn't work yet

Answer honestly; all three are known and recorded:

- **`RemoteImageLoadTest_Cache` fails on Linux** — the download succeeds but `CacheMetadata.xml` is
  never written. macOS is fine. (W8 item 3.)
- **The three remote tests interfere when run back-to-back** — cause not yet established. (Item 3b.)
- **Clicking in the main window during a download can crash** — item 30 above, found this week, not
  yet fixed.
