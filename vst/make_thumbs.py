#!/usr/bin/env python3
"""Bakes the list's plugin pictures: one 48x48 frame per catalog entry, taken from its screenshot (a square from the
middle of it), or its initials when it has none. Frame 0 is the generic picture for entries newer than this build.
Writes images/thumbs.png (frames stacked down), thumbs.txt (the ids in frame order, read by make_layout.py) and
../src/thumbs.h (the same ids for the engine). Needs Pillow and the network:  python3 vst/make_thumbs.py"""
import io
import json
import os
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG = "https://sd88me.github.io/mpc-vst-plugins/catalog.json"
S = 48
MAX = 127   # the meter's filmstrip holds at most 128 frames (frame 0 + 127 plugins)
BG, EDGE, INK = (36, 38, 42), (52, 54, 59), (236, 236, 237)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "plugin-manager-thumbs"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def font(size):
    for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default(size)


def tile(text):
    im = Image.new("RGB", (S, S), (12, 12, 13))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, S - 1, S - 1), 7, fill=BG, outline=EDGE)
    d.text((S / 2, S / 2), text, font=font(20), fill=INK, anchor="mm")
    return im


def initials(name):
    words = [w for w in name.replace("-", " ").split() if w[:1].isalpha()]
    s = "".join(w[0] for w in words[:2]).upper()
    return s if len(s) > 1 or not name[1:2] else (name[:2]).upper()


def shot(url):
    im = Image.open(io.BytesIO(fetch(url))).convert("RGB")
    w, h = im.size
    side = min(w, h)
    im = im.crop(((w - side) // 2, (h - side) // 2, (w - side) // 2 + side, (h - side) // 2 + side))
    im = im.resize((S, S), Image.LANCZOS)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, S - 1, S - 1), 7, fill=255)
    out = Image.new("RGB", (S, S), (12, 12, 13))
    out.paste(im, (0, 0), mask)
    return out


def main():
    plugins = json.loads(fetch(CATALOG))["plugins"]
    plugins = [p for p in plugins if any(v.get("url") for v in p.get("versions", []))][:MAX]
    frames, ids = [tile("?")], [""]
    for p in plugins:
        pic = None
        if p.get("screenshot"):
            try:
                pic = shot(p["screenshot"])
            except Exception as e:   # a broken link: the initials instead
                print("  %s: %s" % (p["id"], e), file=sys.stderr)
        frames.append(pic or tile(initials(p["name"])))
        ids.append(p["id"])
    strip = Image.new("RGB", (S, S * len(frames)))
    for i, f in enumerate(frames):
        strip.paste(f, (0, i * S))
    strip.save(os.path.join(HERE, "images", "thumbs.png"), optimize=True)
    open(os.path.join(HERE, "thumbs.txt"), "w").write("\n".join(ids[1:]) + "\n")
    with open(os.path.join(HERE, "..", "src", "thumbs.h"), "w") as f:
        f.write("/* written by vst/make_thumbs.py: frame i of images/thumbs.png is THUMB_IDS[i] (0: no picture) */\n")
        f.write("static const char *const THUMB_IDS[] = {\n" + "".join('    "%s",\n' % i for i in ids) + "};\n")
        f.write("#define NTHUMBS %d\n" % len(ids))
    print("%d frames" % len(frames))


if __name__ == "__main__":
    main()
