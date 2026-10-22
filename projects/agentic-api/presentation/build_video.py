#!/usr/bin/env python3
"""Render the demo MP4 and the slide stills from video.md (the cut list) and talk.md (the beat times).

    python3 build_video.py            # stills, then the MP4 (about a minute)
    python3 build_video.py --stills   # stills only, for build.py

Writes the MP4 named by '- file:' in talk.md's '## Video' section, and build/still_<name>.jpg for
each row of the Stills table. Never edit them by hand: change video.md and re-run.

Fails, writing nothing, if the segments of a beat do not add up to that beat's time in talk.md.
Needs ffmpeg (with libx264) on the PATH, and Pillow.
"""

import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

from build import BUILD, HERE, VIDEO_MD, SRC, clock, die, parse_talk, read_md, split_h

W, H, FPS = 1920, 1080, 30
PAD = "0x0B2B30"                       # dark teal bands, matching the slides
CAPTION_SECS = 5
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
TOLERANCE = 0.05                       # seconds a beat may differ from talk.md
ORANGE = (248, 126, 51, 255)           # the slides' accent colour
HALO = (0, 0, 0, 150)                  # keeps orange marks visible on white ITK-SNAP panels


def tables(md):
    """{section heading: (list props, [row dicts keyed by lower-case header])} for every ## section."""
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


def tag_size(text, size, pad):
    x0, y0, x1, y1 = ImageFont.truetype(FONT, size).getbbox(text)
    return x1 - x0 + 2 * pad[0], y1 - y0 + 2 * pad[1]


def draw_tag(d, x, y, text, size, fill, pad=(20, 10)):
    font = ImageFont.truetype(FONT, size)
    x0, y0, _, _ = font.getbbox(text)
    tw, th = tag_size(text, size, pad)
    d.rounded_rectangle([x, y, x + tw, y + th], radius=12, fill=fill)
    d.text((x + pad[0] - x0, y + pad[1] - y0), text, font=font, fill="white")


def label_png(path, text, size, fill, pad=(26, 14)):
    img = Image.new("RGBA", tag_size(text, size, pad), (0, 0, 0, 0))
    draw_tag(ImageDraw.Draw(img), 0, 0, text, size, fill, pad)
    img.save(path)
    return path


def callout_png(path, shape, pts, label):
    """A transparent full frame with one box or arrow (output pixels) and its orange label."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    tw, th = tag_size(label, 32, (20, 10)) if label else (0, 0)
    if shape == "box":
        x0, y0, x1, y1 = pts
        d.rounded_rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], radius=14, outline=HALO, width=12)
        d.rounded_rectangle([x0, y0, x1, y1], radius=10, outline=ORANGE, width=6)
        if label:
            ty = y0 - th - 12 if y0 - th - 12 >= 8 else (y1 + 12 if y1 + 12 + th <= H - 8 else y0 + 12)
            draw_tag(d, max(8, min(x0, W - tw - 8)), ty, label, 32, ORANGE)
    else:                                            # arrow: tail (x0, y0) -> head (x1, y1); label at the tail
        x0, y0, x1, y1 = pts
        ang = math.atan2(y1 - y0, x1 - x0)
        hx, hy = x1 - 26 * math.cos(ang), y1 - 26 * math.sin(ang)
        d.line([(x0, y0), (hx, hy)], fill=HALO, width=14)
        d.line([(x0, y0), (hx, hy)], fill=ORANGE, width=8)
        head = [(x1, y1), (x1 - 40 * math.cos(ang - 0.45), y1 - 40 * math.sin(ang - 0.45)),
                (x1 - 40 * math.cos(ang + 0.45), y1 - 40 * math.sin(ang + 0.45))]
        d.polygon(head, fill=ORANGE, outline=HALO)
        if label:
            draw_tag(d, max(8, min(x0 - tw / 2, W - tw - 8)), max(8, min(y0 - th / 2, H - th - 8)), label, 32, ORANGE)
    img.save(path)
    return path


def ffmpeg(args):
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", *args], capture_output=True, text=True)
    if r.returncode:
        die("ffmpeg failed:\n" + r.stderr[-2000:])


def render_segment(seg, src, fr, out, caption, credit, callouts, tmp):
    x, y, w, h = fr["box"]
    scale = min(W / w, H / h)
    sw, sh = int(w * scale) // 2 * 2, int(h * scale) // 2 * 2
    px, py = (W - sw) / 2, (H - sh) / 2

    def to_out(sx, sy):                          # source pixel -> output pixel
        return px + (sx - x) * sw / w, py + (sy - y) * sh / h

    inputs = ["-ss", f"{seg['in']:.3f}", "-t", f"{seg['out'] - seg['in']:.3f}", "-i", src]
    g = [f"[0:v]crop={w}:{h}:{x}:{y}[c0]"]
    if fr["blur"]:
        bx, by, bw, bh = fr["blur"]
        bx, by = max(bx - x, 0), max(by - y, 0)
        bw, bh = min(bw, w - bx), min(bh, h - by)
        g.append(f"[c0]split[a][b];[b]crop={bw}:{bh}:{bx}:{by},boxblur=24:4[bb];[a][bb]overlay={bx}:{by}[c0]")
    moving = (seg["out"] - seg["in"]) / seg["speed"]
    # Screen recordings have a variable frame rate: on a still screen one frame can last for
    # seconds past the out point. trim cuts the segment to its exact planned length.
    g.append(f"[c0]scale={sw}:{sh}:flags=lanczos,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={PAD},"
             f"setpts=(PTS-STARTPTS)/{seg['speed']},fps={FPS},trim=duration={moving:.3f},setpts=PTS-STARTPTS"
             + (f",tpad=stop_mode=clone:stop_duration={seg['hold']}" if seg["hold"] else "") + "[v0]")
    last, n = "v0", 1

    def overlay(png, pos, enable=None):
        nonlocal last, n
        inputs.extend(["-i", png])
        g.append(f"[{last}][{n}:v]overlay={pos}" + (f":enable='{enable}'" if enable else "") + f"[v{n}]")
        last, n = f"v{n}", n + 1

    for k, (t0, t1, c) in enumerate(callouts):
        a = to_out(*c["where"][:2])
        b = to_out(c["where"][0] + c["where"][2], c["where"][1] + c["where"][3]) if c["shape"] == "box" \
            else to_out(*c["where"][2:])
        overlay(callout_png(os.path.join(tmp, f"callout{k}.png"), c["shape"], (*a, *b), c["label"]), "0:0",
                f"between(t,{t0:.3f},{t1:.3f})")
    if seg["speed"] != 1:
        overlay(label_png(os.path.join(tmp, "badge.png"), f"{seg['speed']:g}x speed", 30, ORANGE[:3] + (235,),
                          pad=(18, 10)), "W-w-32:32", f"lt(t,{moving:.3f})")
    if credit:
        overlay(label_png(os.path.join(tmp, "credit.png"), credit, 18, (2, 44, 50, 200), pad=(12, 6)), "W-w-12:H-h-10")
    if caption:
        overlay(label_png(os.path.join(tmp, "caption.png"), caption, 40, (2, 44, 50, 225)), "40:H-h-56",
                f"lt(t,{CAPTION_SECS})")
    ffmpeg([*inputs, "-filter_complex", ";".join(g), "-map", f"[{last}]", "-an",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), out])


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def main():
    if not shutil.which("ffmpeg"):
        die("ffmpeg not found on the PATH")
    frozen = os.path.join(HERE, "frozen.json")
    if os.path.exists(frozen) and "--stills" not in sys.argv[1:]:
        die("the video is frozen (it was uploaded to the organisers). Only `--stills` may run now; "
            "delete frozen.json to unfreeze.")
    meta, parts = parse_talk(SRC)
    videos = [p for p in parts if p["kind"] == "video"]
    if len(videos) != 1:
        die("talk.md needs exactly one '## Video: Title' section")
    video = videos[0]
    beats = {b["num"]: b for b in video["beats"]}

    t = tables(read_md(VIDEO_MD))
    for need in ("clips", "framings", "beats", "segments"):
        if need not in t:
            die(f"video.md: missing a '## {need.title()}' section with a table")
    footage = t["clips"][0].get("footage", "")
    clips = {r["clip"]: os.path.join(footage, r["file"]) for r in t["clips"][1]}
    for c, path in clips.items():
        if not os.path.exists(path):
            die(f"video.md: clip {c} not found: {path}")
    framings = {}
    for r in t["framings"][1]:
        box = tuple(int(r[k]) for k in ("x", "y", "w", "h"))
        blur = tuple(int(v) for v in r["blur"].split()) if r.get("blur", "-") != "-" else None
        framings[r["framing"]] = {"clip": r["clip"], "box": box, "blur": blur}
    captions = {int(r["beat"]): r["caption"] for r in t["beats"][1]}

    os.makedirs(BUILD, exist_ok=True)
    for i, r in enumerate(t.get("stills", ({}, []))[1], 1):
        fr = framings.get(r["framing"])
        if not fr or fr["clip"] != r["clip"]:
            die(f"video.md still {i}: framing {r['framing']!r} is not defined for clip {r['clip']}")
        x, y, w, h = fr["box"]
        still = os.path.join(BUILD, f"still_{r['still']}.jpg")
        ffmpeg(["-ss", f"{tsecs(r['at'], f'still {i}'):.3f}", "-i", clips[r["clip"]], "-frames:v", "1",
                "-vf", f"crop={w}:{h}:{x}:{y},scale='min(iw,2000)':-2", "-q:v", "2", still])
        print(f"video.md -> {os.path.relpath(still, HERE)}")
    if "--stills" in sys.argv[1:]:
        return

    segs = []
    for i, r in enumerate(t["segments"][1], 1):
        where = f"segment {i}"
        seg = {"beat": int(r["beat"]), "clip": r["clip"], "in": tsecs(r["in"], where), "out": tsecs(r["out"], where),
               "speed": float(r["speed"]), "hold": float(r["hold"]), "framing": r["framing"]}
        if seg["beat"] not in beats:
            die(f"video.md {where}: beat {seg['beat']} is not in talk.md")
        if seg["framing"] not in framings or framings[seg["framing"]]["clip"] != seg["clip"]:
            die(f"video.md {where}: framing {seg['framing']!r} is not defined for clip {seg['clip']}")
        if seg["out"] <= seg["in"] or seg["speed"] <= 0:
            die(f"video.md {where}: needs Out after In and a positive speed")
        seg["length"] = (seg["out"] - seg["in"]) / seg["speed"] + seg["hold"]
        segs.append(seg)

    callouts = []
    for i, r in enumerate(t.get("callouts", ({}, []))[1], 1):
        where = f"callout {i}"
        c = {"beat": int(r["beat"]), "clip": r["clip"], "from": tsecs(r["from"], where), "to": tsecs(r["to"], where),
             "shape": r["shape"].lower(), "where": tuple(int(v) for v in r["where"].split()), "label": r.get("label", "")}
        if c["shape"] not in ("box", "arrow") or len(c["where"]) != 4:
            die(f"video.md {where}: shape must be box (x y w h) or arrow (x1 y1 x2 y2)")
        if not any(s["beat"] == c["beat"] and s["clip"] == c["clip"] and c["from"] < s["out"] and c["to"] > s["in"]
                   for s in segs):
            die(f"video.md {where}: {r['from']}-{r['to']} is not inside any segment of beat {c['beat']}")
        callouts.append(c)

    bad = []
    for n, b in beats.items():
        got = sum(s["length"] for s in segs if s["beat"] == n)
        if abs(got - b["secs"]) > TOLERANCE:
            bad.append(f"beat {n} ({b['title']}): segments give {got:.2f} s, talk.md says {clock(b['secs'])}")
    if bad:
        die("the cut does not match talk.md:\n  " + "\n  ".join(bad))

    out = os.path.join(HERE, video["props"]["file"])
    credit = video["props"].get("attribution", "")
    with tempfile.TemporaryDirectory() as tmp:
        files, seen = [], set()
        for i, seg in enumerate(segs):
            caption = captions.get(seg["beat"]) if seg["beat"] not in seen else None
            seen.add(seg["beat"])
            active = []                          # (start, end in segment time, callout)
            for c in callouts:
                if c["beat"] == seg["beat"] and c["clip"] == seg["clip"] and c["from"] < seg["out"] and c["to"] > seg["in"]:
                    t0 = (max(c["from"], seg["in"]) - seg["in"]) / seg["speed"]
                    t1 = seg["length"] if c["to"] >= seg["out"] else (c["to"] - seg["in"]) / seg["speed"]
                    active.append((t0, t1, c))
            part = os.path.join(tmp, f"seg{i:02d}.mp4")
            print(f"  segment {i + 1:2d}  beat {seg['beat']}  {seg['clip']} {clock(int(seg['in']))}"
                  f"-{clock(int(seg['out']))}  x{seg['speed']:g}  -> {seg['length']:.2f} s"
                  + (f"  ({len(active)} callouts)" if active else ""), flush=True)
            render_segment(seg, clips[seg["clip"]], framings[seg["framing"]], part, caption, credit, active, tmp)
            got = duration(part)
            if abs(got - seg["length"]) > 0.1:
                print(f"     rendered {got:.2f} s, planned {seg['length']:.2f} s", flush=True)
            files.append(part)
        listing = os.path.join(tmp, "list.txt")
        open(listing, "w").write("".join(f"file '{p}'\n" for p in files))
        ffmpeg(["-f", "concat", "-safe", "0", "-i", listing, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "96k", "-shortest",
                "-movflags", "+faststart", out])

    total = duration(out)
    print(f"\nvideo.md -> {os.path.relpath(out, HERE)} ({total:.1f} s, {os.path.getsize(out) / 1e6:.0f} MB)")
    if abs(total - video["secs"]) > 0.5:
        die(f"rendered length {total:.1f} s differs from the video time {clock(video['secs'])}")
    print("checks: OK")


if __name__ == "__main__":
    main()
