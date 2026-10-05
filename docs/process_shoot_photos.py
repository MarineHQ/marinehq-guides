#!/usr/bin/env python3
"""Web copies of the professional Marine HQ shoot (114 frames, Canon R6, May 2025) for the Guides site.

Source (originals, never edited):
  ~/Documents/Marine HQ/Marketing/Pics/2026100465467754161cc9a3bb806d05722e1d1eae5eb68f6ee029d19fd32c05d6819b46/
  marine-hq-images-<N>-of-114jpg_*.jpg
Output: site/assets/photos/shoot-*.jpg  (max 1800 px, JPEG q82, EXIF/GPS stripped)

House rules applied here (GUIDES-STYLE.md, Photos):
  - no vessel name or hull lettering: PATCH boxes are filled from their own edges (the lettering sits on
    plain gelcoat), so a named transom or bow becomes a blank one. Frames 95-104 (a client yacht's name
    across the frame) are not used at all.
  - no crew face as the subject: only backs, hands and tools were chosen. Faces need Trish's OK first.
  - no other company's branding: frames 41-53 (contractor shirts) are not used.
Run:  python3 docs/process_shoot_photos.py [--zoom]     (--zoom writes patch close-ups to /tmp for checking)
"""
import glob, os, re, sys
import numpy as np
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.expanduser("~/Documents/Marine HQ/Marketing/Pics/2026100465467754161cc9a3bb806d05722e1d1eae5eb68f6ee029d19fd32c05d6819b46")
OUT  = os.path.join(HERE, "..", "site", "assets", "photos")
FILES = {int(re.search(r"images-(\d+)-of", f).group(1)): f for f in glob.glob(os.path.join(SRC, "*.jpg"))}

# frame -> (output name, [patch boxes in full-res px: x0, y0, x1, y1])
SHOTS = {
    20:  ("shoot-underway",        [(4590, 2460, 4850, 2610)]),   # transom name
    19:  ("shoot-underway-2",      [(5010, 2480, 5270, 2630)]),   # transom name
    5:   ("shoot-dock-crew",       [(1140, 1900, 1545, 2064)]),   # lettering on the bow behind
    7:   ("shoot-dock-hose",       [(520, 1770, 1030, 1960)]),    # same bow
    34:  ("shoot-polisher-deck",   []),
    22:  ("shoot-polisher-close",  []),
    1:   ("shoot-polish-kit",      []),
    38:  ("shoot-hull-polish",     []),
    74:  ("shoot-stainless",       []),
    78:  ("shoot-rail-polish",     []),
    59:  ("shoot-wash-down",       []),
    72:  ("shoot-remote",          []),
    105: ("shoot-tender",          []),
    108: ("shoot-engine-room",     []),
    109: ("shoot-engine-room-2",   []),
    40:  ("shoot-hull-polish-2",   []),
    111: ("shoot-generator",       []),
    106: ("shoot-tender-2",        []),
    75:  ("shoot-stainless-2",     []),
    21:  ("shoot-heading-out",     [(3095, 3195, 3295, 3300)]),   # transom name; portrait frame, cropped to landscape below
}
CROP = {21: (0, 1750, 4000, 4417)}   # frame -> crop box (after patching), for portrait frames used as wide heroes
# Stills taken from the clips with ffmpeg (-ss <t> -frames:v 1): shoot-at-helm (docking 11.8 s), shoot-letting-go (docking 32.4 s),
# shoot-making-ready (general-maintenance 33 s), shoot-berthing-aerial (drone-2 31 s), shoot-marina-aerial (drone-2 1 s), shoot-marina-aerial-2 (drone-1 0.5 s).

def fill_from_edges(a, box, iters=1500):
    """Replace the inside of box with a smooth surface interpolated from its border (Laplace)."""
    x0, y0, x1, y1 = box
    p = a[y0:y1, x0:x1].astype(np.float64)
    inner = np.zeros(p.shape[:2], bool); inner[1:-1, 1:-1] = True
    # start from a bilinear blend of the four edges, then relax
    h, w = p.shape[:2]
    ty = np.linspace(0, 1, h)[:, None, None]; tx = np.linspace(0, 1, w)[None, :, None]
    guess = ((1 - ty) * p[0:1] + ty * p[-1:] + (1 - tx) * p[:, 0:1] + tx * p[:, -1:]) / 2
    p[inner] = guess[inner]
    for _ in range(iters):
        avg = (np.roll(p, 1, 0) + np.roll(p, -1, 0) + np.roll(p, 1, 1) + np.roll(p, -1, 1)) / 4
        p[inner] = avg[inner]
    rng = np.random.default_rng(7)                        # a little grain so the patch is not glassy
    p[inner] += rng.normal(0, 1.2, p.shape)[inner]
    a[y0:y1, x0:x1] = np.clip(p, 0, 255).astype(np.uint8)

# Marine HQ back print added to a plain shirt back (Trish, 5 Oct 2026: "put a blue Marine HQ logo on the back of
# this shirt ... like the others"). The shirt already carries the Marine HQ chest logo; the real back print on the
# navy polos is the MARINE / HQ wordmark without the boat mark, so that is what goes on.
# frame -> quad on the shirt in full-res px: top-left, top-right, bottom-right, bottom-left
BACK_PRINT = {
    # none in use. Tried on frames 38 and 40 (5 Oct 2026) and Trish had it taken off again: the shirt stays plain.
}
LOGO = os.path.join(HERE, "..", "site", "assets", "logo_navy.png")
NAVY = (27, 42, 82)

def _persp(dst, src):
    """coefficients mapping output (dst quad) back to input (src rect) for Image.transform"""
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()

def back_print(a, quad, strength=0.9):
    from PIL import ImageFilter
    logo = Image.open(LOGO).convert("RGBA")
    logo = logo.crop((0, 142, logo.width, logo.height))                    # wordmark only, no boat mark
    alpha = logo.split()[3].resize((logo.width * 4, logo.height * 4), Image.LANCZOS)
    alpha = alpha.point(lambda v: 0 if v < 96 else (255 if v > 160 else int((v - 96) * 255 / 64)))   # re-crisp after upscaling
    h, w = a.shape[:2]
    src = [(0, 0), (alpha.width, 0), (alpha.width, alpha.height), (0, alpha.height)]
    mask = alpha.transform((w, h), Image.PERSPECTIVE, _persp(quad, src), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2.2))
    m = (np.asarray(mask, np.float64) / 255.0 * strength)[..., None]
    base = a.astype(np.float64)
    ink = base * (np.array(NAVY, np.float64) / 255.0) * 1.12 + 6           # multiply: folds and weave show through the print
    a[:] = np.clip(base * (1 - m) + ink * m, 0, 255).astype(np.uint8)

def main():
    zoom = "--zoom" in sys.argv
    for n, (name, boxes) in SHOTS.items():
        im = ImageOps.exif_transpose(Image.open(FILES[n])).convert("RGB")
        a = np.array(im)
        for b in boxes: fill_from_edges(a, b)
        if n in BACK_PRINT: back_print(a, BACK_PRINT[n])
        im = Image.fromarray(a)
        if n in CROP and not zoom: im = im.crop(CROP[n])
        if zoom:
            for i, (x0, y0, x1, y1) in enumerate(boxes):
                m = 260
                im.crop((max(0, x0 - m), max(0, y0 - m), x1 + m, y1 + m)).save("/tmp/zoom_%s_%d.jpg" % (name, i), quality=88)
        im.thumbnail((1800, 1800), Image.LANCZOS)
        out = os.path.join(OUT, name + ".jpg")
        Image.frombytes("RGB", im.size, im.tobytes()).save(out, "JPEG", quality=82, optimize=True, progressive=True)
        print("%-24s frame %-3d %s %d KB%s" % (name + ".jpg", n, im.size, os.path.getsize(out) // 1024, "  patched x%d" % len(boxes) if boxes else ""))

if __name__ == "__main__":
    main()
