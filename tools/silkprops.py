"""The Silk Archive's own fittings, so nothing in the dungeon is a vanilla block: block models (boxes in pixels) and
16x16 textures in the archive's palettes (tools/silkblocks.py in E:/Ashbound), written straight into the add-on.

  silk_web         a sagging orb web, ivory and dusty, a dew bead or two (slows like a cobweb)
  silk_cable       a strand of the great web: three plies of silk twisted tight
  archive_chain    pewter links, silk wound round them where the spider climbed
  archive_lantern  a pewter cage of cold moonglass, a stepped roof with four spider-leg brackets (stands or hangs)
  archive_grille   pewter bars with rails and a lozenge, silk caught in them (joins like iron bars)
  archive_iron     riveted pewter plate (the presses)
  walnut_fence     turned walnut balusters under a moulded rail (the gallery rails)
  walnut_beam      a squared walnut beam strapped with pewter (the presses, the sewing frame)
  archive_lectern  a walnut lectern on a ringed column, an open book chained to it
  archive_coffer   a walnut coffer bound in pewter, a spider on its lock plate (holds the loot)
  archive_chair    a high-backed walnut reading chair with an oxblood cushion

Every facing model looks north (-z): its front, the side you stand at. The chair's back is at the north.

    python tools/silkprops.py        -> assets + data in src/main/resources
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, "E:/Ashbound/tools")
from PIL import Image, ImageDraw  # noqa: E402

import silkblocks as SB  # noqa: E402
from siteblocks import img, smooth, grain, col, fill, put, get, blend  # noqa: E402
from lampmodel import box, element, rbox  # noqa: E402
import port_weapons as P  # noqa: E402

A = P.ASSETS
TEXDIR = A + "textures/block/"
TEX = {"pewter": "archive_pewter", "glass": "archive_moonglass", "walnut": "walnut_wood", "silk": "silk_wall",
       "pages": "archive_pages", "leather": "archive_leather", "lock": "coffer_lock", "velvet": "archive_velvet"}
FACING_Y = {"north": 0, "east": 90, "south": 180, "west": 270}

# ---------------------------------------------------------------- textures


def pewter(seed=901):
    """Dull pewter: soft mottling, a few bright scratches, green-grey tarnish in patches."""
    r = random.Random(seed)
    im = img()
    g, sm = grain(seed), smooth(seed + 1, 4)
    fill(im, SB.PEWTER, lambda x, y: 0.42 + (sm[y][x] - 0.5) * 0.35 + (g[y][x] - 0.5) * 0.12)
    for _ in range(3):
        x, y, n = r.randrange(16), r.randrange(16), r.randrange(3, 7)
        for k in range(n):
            put(im, x + k, y + k // 3, col(SB.PEWTER, 0.86))
    for y in range(16):
        for x in range(16):
            if sm[(y + 5) % 16][(x + 3) % 16] > 0.72:
                blend(im, x, y, (70, 86, 74), 0.25)
    return im


def moonglass(seed=902):
    """Cold blue glass behind a thin leaded frame, the pale flame showing through its middle."""
    im = img()
    g = grain(seed)
    for y in range(16):
        for x in range(16):
            d = math.hypot((x - 7.5) / 1.0, (y - 9) / 1.6)
            v = 0.9 - d * 0.075 + (g[y][x] - 0.5) * 0.08
            put(im, x, y, col(SB.MOON, v))
            if x in (0, 15) or y in (0, 15):
                put(im, x, y, col(SB.PEWTER, 0.3))
    for y in range(6, 13):                                       # the flame: a tall white tongue
        w = 1.4 - abs(y - 10) * 0.25
        for x in range(16):
            if abs(x - 7.5) < w:
                put(im, x, y, (250, 253, 255, 255))
    return im


def walnut_wood(seed=903):
    """Dark walnut, its grain running up: wavy dark streaks, a lit fleck here and there."""
    r = random.Random(seed)
    im = img()
    g = grain(seed)
    lines = [r.uniform(0, 16) for _ in range(5)]
    def v(x, y):
        s = 0.48 + (g[y][x] - 0.5) * 0.1
        for L in lines:
            if abs(x - L - 0.8 * math.sin(y * 0.5 + L)) < 0.6:
                s -= 0.2
        return s
    fill(im, SB.WALNUT, v)
    return im


def walnut_beam(seed=904):
    """A squared beam's side: the grain up it, dark arrises down both edges, a lit chamfer beside them, one
    pewter bolt head."""
    im = walnut_wood(seed)
    for y in range(16):
        put(im, 0, y, col(SB.WALNUT, 0.06))
        put(im, 1, y, col(SB.WALNUT, 0.74))
        put(im, 15, y, col(SB.WALNUT, 0.04))
        put(im, 14, y, col(SB.WALNUT, 0.22))
    put(im, 7, 7, col(SB.PEWTER, 0.9))
    put(im, 8, 7, col(SB.PEWTER, 0.6))
    put(im, 7, 8, col(SB.PEWTER, 0.45))
    put(im, 8, 8, col(SB.PEWTER, 0.15))
    return im


def walnut_beam_top(seed=905):
    """The cut end: growth rings round a dark heart, a lit chamfer."""
    im = img()
    g = grain(seed)
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 6.8, y - 8.4)
            v = 0.46 + 0.14 * math.sin(d * 2.1) + (g[y][x] - 0.5) * 0.08
            if min(x, y, 15 - x, 15 - y) == 0:
                v = 0.72
            put(im, x, y, col(SB.WALNUT, v))
    return im


def archive_iron(seed=906):
    """Riveted pewter plate: a bevelled sheet, rivets round its edge, a seam across the middle."""
    im = pewter(seed)
    for k in range(16):
        put(im, k, 0, col(SB.PEWTER, 0.8))
        put(im, 0, k, col(SB.PEWTER, 0.75))
        put(im, k, 15, col(SB.PEWTER, 0.08))
        put(im, 15, k, col(SB.PEWTER, 0.12))
        put(im, k, 7, col(SB.PEWTER, 0.12))
        put(im, k, 8, col(SB.PEWTER, 0.7))
    for x in (2, 7, 12):
        for y in (2, 5, 10, 13):
            put(im, x, y, col(SB.PEWTER, 0.97))
            put(im, x + 1, y + 1, col(SB.PEWTER, 0.05))
    return im


def silk_web(seed=907):
    """An orb web, clear between its threads: eight spokes from a knot, a sagging spiral, dust on it, two dew
    beads; heavier where it grips the corners."""
    r = random.Random(seed)
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = 7.5 + r.uniform(-1, 1), 7.5 + r.uniform(-1, 1)
    spokes = [i * math.pi / 4 + r.uniform(-0.15, 0.15) for i in range(8)]
    for a in spokes:
        d.line([(cx, cy), (cx + 11 * math.cos(a), cy + 11 * math.sin(a))], fill=SB.SILK[5] + (255,))
    for k, rad in enumerate((2.4, 4.4, 6.6)):
        pts = [(cx + rad * math.cos(a), cy + rad * math.sin(a) + (0.6 if math.sin(a) > 0 else 0)) for a in spokes]
        for i in range(8):
            if r.random() < 0.88:
                d.line([pts[i], pts[(i + 1) % 8]], fill=SB.SILK[4 + k % 2] + (255,))
    for (x, y) in ((0, 0), (15, 0), (0, 15), (15, 15)):                  # the anchors: clumps of silk
        for dx in range(2):
            for dy in range(2):
                im.putpixel((abs(x - dx), abs(y - dy)), SB.SILK[6] + (255,))
    im.putpixel((int(cx), int(cy)), SB.SILK[6] + (255,))
    for _ in range(5):                                                     # dust caught on it
        x, y = r.randrange(16), r.randrange(16)
        if im.getpixel((x, y))[3]:
            im.putpixel((x, y), SB.SILK[2] + (255,))
    for _ in range(2):
        x, y = r.randrange(3, 13), r.randrange(3, 13)
        if im.getpixel((x, y))[3]:
            im.putpixel((x, y), SB.MOON[4] + (255,))
    return im


def silk_cable(seed=908):
    """Three plies of silk twisted tight: diagonal bands, each lit along its crown, dark in the lay between."""
    im = img()
    g = grain(seed)
    for y in range(16):
        for x in range(16):
            t = ((x + y * 0.75) % 5.33) / 5.33
            v = 0.25 + 0.7 * math.sin(t * math.pi) ** 0.7 + (g[y][x] - 0.5) * 0.08
            put(im, x, y, col(SB.SILK, v))
    r = random.Random(seed)
    for _ in range(4):                                                     # loose fibres
        x, y = r.randrange(16), r.randrange(16)
        for k in range(3):
            put(im, x + k, y, col(SB.SILK, 0.98))
    return im


def pages(seed=909):
    """An open page: yellowed paper, the archive's close script in lines, a rubricated capital."""
    r = random.Random(seed)
    im = img()
    g = grain(seed)
    fill(im, SB.PAPER, lambda x, y: 0.72 + (g[y][x] - 0.5) * 0.1 - (0.15 if min(x, y, 15 - x, 15 - y) == 0 else 0))
    for y in range(2, 15, 2):
        x0 = 4 if y < 6 else 2
        for x in range(x0, 14):
            if r.random() < 0.8:
                put(im, x, y, SB.INK[2])
    for (x, y) in ((2, 2), (3, 2), (2, 3), (3, 3), (2, 4)):
        put(im, x, y, (128, 26, 24))
    return im


def leather(seed=910):
    """Oxblood binding, worn paler on its edges, two gilt tooling lines."""
    im = img()
    g, sm = grain(seed), smooth(seed + 2, 4)
    ox = SB.LEATHER[0]
    fill(im, ox, lambda x, y: 0.45 + (sm[y][x] - 0.5) * 0.3 + (g[y][x] - 0.5) * 0.15 + (0.25 if min(x, y, 15 - x, 15 - y) == 0 else 0))
    for k in range(2, 14):
        for (a, b) in ((k, 2), (k, 13), (2, k), (13, k)):
            put(im, a, b, col(SB.GILT, 0.6))
    return im


def velvet(seed=911):
    """Crushed oxblood velvet: soft, uneven sheen, buttoned in the middle."""
    im = img()
    sm, g = smooth(seed, 3), grain(seed)
    ramp = [(30, 6, 10), (48, 10, 16), (68, 16, 22), (90, 24, 30), (112, 36, 40)]
    fill(im, ramp, lambda x, y: 0.4 + (sm[y][x] - 0.5) * 0.5 + (g[y][x] - 0.5) * 0.1)
    for (x, y) in ((4, 4), (11, 4), (4, 11), (11, 11), (7, 7)):
        put(im, x, y, col(SB.GILT, 0.55))
        put(im, x + 1, y + 1, ramp[0])
    return im


def coffer_lock(seed=912):
    """A pewter lock plate with a spider sunk into it: a round body and eight bent legs, the keyhole its mouth."""
    im = pewter(seed)
    for k in range(16):
        put(im, k, 0, col(SB.PEWTER, 0.85))
        put(im, 0, k, col(SB.PEWTER, 0.8))
        put(im, k, 15, col(SB.PEWTER, 0.05))
        put(im, 15, k, col(SB.PEWTER, 0.08))
    ink = SB.INK[1]
    for y in range(16):
        for x in range(16):
            if math.hypot(x - 7.5, (y - 7) * 1.1) < 2.6 or math.hypot(x - 7.5, y - 10.5) < 1.6:
                put(im, x, y, ink)
    for s in (-1, 1):
        for (a, b) in (((3, 4), (1, 1)), ((3, 6), (1, 5)), ((3, 8), (1, 10)), ((4, 10), (2, 14))):
            x0, y0 = 7.5 + s * a[0], a[1]
            x1, y1 = 7.5 + s * (a[0] + 2.5), b[1]
            for t in range(6):
                f = t / 5
                put(im, int(round(x0 + (x1 - x0) * f)), int(round(y0 + (y1 - y0) * f)), ink)
    put(im, 7, 7, col(SB.MOON, 0.6))
    put(im, 8, 7, col(SB.MOON, 0.6))
    put(im, 7, 11, col(SB.PEWTER, 0.0))
    put(im, 7, 12, col(SB.PEWTER, 0.0))
    return im


TEXTURES = {"archive_pewter": pewter, "archive_moonglass": moonglass, "walnut_wood": walnut_wood,
            "walnut_beam": walnut_beam, "walnut_beam_top": walnut_beam_top, "archive_iron": archive_iron,
            "silk_web": silk_web, "silk_cable": silk_cable, "archive_pages": pages, "archive_leather": leather,
            "archive_velvet": velvet, "coffer_lock": coffer_lock}

# ---------------------------------------------------------------- models (pixels, 16 a block)


def cube(cx, y0, cz, hw, h, tex, hd=None, glow=0):
    hd = hw if hd is None else hd
    return box((cx - hw, y0, cz - hd), (cx + hw, y0 + h, cz + hd), tex, glow=glow)


def links(x, z, y0, y1, w=1.5, t=0.5, wrap=()):
    """Chain links from y0 up to y1, turned alternately, each an open loop; silk bound round them at the heights
    in wrap."""
    B, y, k = [], y0, 0
    while y < y1 - 0.5:
        h = min(4.5, y1 - y)
        if k % 2 == 0:
            B += [box((x - w, y, z - t / 2), (x - w + t, y + h, z + t / 2), "pewter"),
                  box((x + w - t, y, z - t / 2), (x + w, y + h, z + t / 2), "pewter"),
                  box((x - w, y, z - t / 2), (x + w, y + t, z + t / 2), "pewter"),
                  box((x - w, y + h - t, z - t / 2), (x + w, y + h, z + t / 2), "pewter")]
        else:
            B += [box((x - t / 2, y, z - w), (x + t / 2, y + h, z - w + t), "pewter"),
                  box((x - t / 2, y, z + w - t), (x + t / 2, y + h, z + w), "pewter"),
                  box((x - t / 2, y, z - w), (x + t / 2, y + t, z + w), "pewter"),
                  box((x - t / 2, y + h - t, z - w), (x + t / 2, y + h, z + w), "pewter")]
        y += h - t
        k += 1
    for wy in wrap:
        B.append(box((x - w - 0.3, wy, z - w - 0.3), (x + w + 0.3, wy + 1.2, z + w + 0.3), "silk"))
    return B


def chain():
    B = links(8, 8, 0, 16, wrap=(5.5,))
    B.append(box((9.4, 1.5, 7.8), (9.8, 6.5, 8.2), "silk"))                    # a wisp hanging off the wrap
    return B


def lantern(hang):
    y0 = 2.5 if hang else 0
    B = [cube(8, y0, 8, 3, 1.2, "pewter"), cube(8, y0 + 1.2, 8, 2.2, 6.3, "glass", glow=15)]
    for sx in (-1, 1):
        for sz in (-1, 1):
            B.append(cube(8 + sx * 2.5, y0 + 1.2, 8 + sz * 2.5, 0.5, 6.3, "pewter"))
    B.append(cube(8, y0 + 4.2, 8, 2.6, 0.6, "pewter"))                        # a band round the glass
    for k, (hw, h) in enumerate(((3.6, 1), (2.8, 1), (1.9, 1), (1.0, 1.2))):    # the stepped roof
        B.append(cube(8, y0 + 7.5 + k, 8, hw, h, "pewter"))
    B += [box((7.6, y0 + 11.7, 7), (8.4, y0 + 13.3, 9), "pewter"), box((7, y0 + 12.9, 7.6), (9, y0 + 13.5, 8.4), "pewter")]
    for sx, sz in ((1, 1), (1, -1), (-1, 1), (-1, -1)):                          # four spider-leg brackets
        x, z = 8 + sx * 3.4, 8 + sz * 3.4
        B.append(rbox((x - 0.3, y0 + 4.5, z - 0.3), (x + 0.3, y0 + 8.5, z + 0.3), (x, y0 + 8.5, z), "z", -22.5 * sx, "pewter"))
        B.append(cube(8 + sx * 3.9, y0 + 3.6, 8 + sz * 3.4, 0.35, 1.2, "pewter"))
    if hang:
        B += links(8, 8, y0 + 13.3, 16, w=1.0, t=0.45)
    else:
        B += [cube(8 + sx * 2.4, 0, 8 + sz * 2.4, 0.6, 0.4, "pewter") for sx in (-1, 1) for sz in (-1, 1)]
    return B


def grille_post():
    return [cube(8, 0, 8, 1, 16, "pewter"), cube(8, 0, 8, 1.5, 1, "pewter"), cube(8, 15, 8, 1.5, 1, "pewter")]


def grille_side():
    B = [box((7.5, 1, 0), (8.5, 2, 7), "pewter"), box((7.5, 14, 0), (8.5, 15, 7), "pewter"),
         box((7.5, 7.5, 0), (8.5, 8.5, 7), "pewter")]
    for z in (1.2, 4.2):
        B.append(box((7.6, 2, z), (8.4, 14, z + 0.8), "pewter"))
    B.append(rbox((7.55, 6.2, 2.6), (8.45, 9.8, 3.6), (8, 8, 3.1), "x", 45, "pewter"))      # the lozenge
    return B


def grille_silk():
    """Threads of silk strung across the bars, sagging a little."""
    return [box((7.85, 10.2, 0), (8.15, 10.5, 7), "silk"), box((7.85, 4.6, 0.5), (8.15, 4.9, 6.5), "silk")]


def fence_post():
    return [cube(8, 0, 8, 3, 1.5, "walnut"), cube(8, 1.5, 8, 2.5, 1, "walnut"), cube(8, 2.5, 8, 1.5, 4, "walnut"),
            cube(8, 6.5, 8, 2, 3.5, "walnut"), cube(8, 10, 8, 1.25, 3, "walnut"), cube(8, 13, 8, 2.5, 2, "walnut"),
            cube(8, 15, 8, 1.5, 1, "walnut")]


def fence_side():
    return [box((7, 12.5, 0), (9, 15, 6), "walnut"), box((7, 3, 0), (9, 5, 6), "walnut"),
            box((7.25, 5, 2.2), (8.75, 12.5, 3.8), "walnut"), box((6.9, 7.5, 2), (9.1, 9, 4), "walnut")]


def lectern():
    B = [cube(8, 0, 8, 6, 1.5, "walnut"), cube(8, 1.5, 8, 5, 1.5, "walnut"), cube(8, 3, 8.5, 2.5, 8, "walnut")]
    B += [cube(8, 5, 8.5, 3, 1, "pewter"), cube(8, 9, 8.5, 3, 1, "pewter")]
    for sx, sz in ((1, 1), (1, -1), (-1, 1), (-1, -1)):                          # claw feet at the corners
        B.append(cube(8 + sx * 6.2, 0, 8 + sz * 6.2, 0.9, 1.0, "pewter"))
    o = (8, 11.8, 8)
    for a, b, t in (((1, 11, 2), (15, 12.5, 14), "walnut"), ((1, 12.5, 2), (15, 13.3, 3), "walnut"),
                    ((2, 12.5, 3.2), (14, 12.8, 13.2), "leather"), ((2.5, 12.8, 3.6), (7.7, 13.8, 12.8), "pages"),
                    ((8.3, 12.8, 3.6), (13.5, 13.8, 12.8), "pages"), ((7.6, 12.6, 3.4), (8.4, 13.3, 13), "leather")):
        B.append(box(a, b, t, rot={"origin": list(o), "axis": "x", "angle": -22.5}))
    B.append(box((9.3, 6.5, 1.6), (10.1, 10.6, 1.9), "leather"))                  # the bookmark ribbon
    B += links(12.5, 9.5, 3, 11.2, w=0.7, t=0.35)                                  # the chain to the book
    return B


def coffer():
    B = [cube(8, 1, 8, 6.5, 9, "walnut", hd=5.5), cube(8, 10, 8, 7, 2.5, "walnut", hd=6), cube(8, 12.5, 8, 6, 1, "walnut", hd=5)]
    for x0 in (3.3, 11.2):
        B += [box((x0, 0.8, 2.2), (x0 + 1.5, 10, 13.8), "pewter"), box((x0, 10, 1.7), (x0 + 1.5, 12.8, 14.3), "pewter"),
              box((x0, 12.8, 2.7), (x0 + 1.5, 13.8, 13.3), "pewter")]
    for sx, sz in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        B.append(cube(8 + sx * 6, 0, 8 + sz * 4.8, 1.0, 1.0, "pewter"))
    lock = box((6, 5.5, 1.9), (10, 10.5, 2.5), "lock")
    lock["full"] = True
    B += [lock, box((7.2, 10, 1.4), (8.8, 12, 2), "pewter")]
    for sx in (-1, 1):
        x = 8 + sx * 7
        B.append(box((min(x, x + sx * 0.8), 6, 6), (max(x, x + sx * 0.8), 7, 10), "pewter"))
    return B


def chair():
    B = []
    for sx in (-1, 1):
        for z in (2.75, 13.25):
            B.append(cube(8 + sx * 5.75, 0, z, 0.75, 7, "walnut"))
    B += [cube(8, 7, 8, 6.5, 1.5, "walnut"), cube(8, 8.5, 8.25, 5.5, 0.8, "velvet", hd=5.25)]
    for sx in (-1, 1):
        x = 8 + sx * 5.5
        B += [cube(x, 8.5, 2.5, 1, 16.5, "walnut"), cube(x, 25, 2.5, 0.7, 1.5, "pewter"),
              box((x - 0.75, 12, 3.5), (x + 0.75, 13.2, 14.5), "walnut"), cube(x, 8.5, 13, 0.5, 3.5, "walnut")]
    B += [box((3.5, 10, 2), (12.5, 22, 3), "walnut"), box((4.5, 11, 3), (11.5, 21, 3.5), "velvet"),
          box((1.5, 22, 1.5), (14.5, 24, 3.5), "walnut"), box((6, 24, 2), (10, 25.5, 3), "walnut"),
          box((7.2, 25.5, 2.2), (8.8, 26.5, 2.8), "walnut")]
    return B


def web_model():
    """Two crossed planes, like vanilla's cross but ours: the web texture both ways."""
    els = []
    for ang in (45, -45):
        els.append({"from": [0.8, 0, 8], "to": [15.2, 16, 8], "shade": False,
                    "rotation": {"origin": [8, 8, 8], "axis": "y", "angle": ang, "rescale": True},
                    "faces": {f: {"uv": [0, 0, 16, 16], "texture": "#web"} for f in ("north", "south")}})
    return {"ambientocclusion": False, "render_type": "minecraft:cutout", "textures": {"web": "ashbound:block/silk_web",
            "particle": "ashbound:block/silk_web"}, "elements": els}


# ---------------------------------------------------------------- writing


def el(bx):
    e = element(bx)
    if bx.get("full") or bx["tex"] == "glass":
        for f in ("north", "south", "east", "west"):
            e["faces"][f]["uv"] = [0, 0, 16, 16]
    return e


def model(name, boxes, cutout=False, particle="walnut"):
    used = sorted(set(b["tex"] for b in boxes))
    tex = {t: "ashbound:block/" + TEX[t] for t in used}
    tex["particle"] = "ashbound:block/" + TEX[particle]
    for b in boxes:
        for v in b["from"] + b["to"]:
            assert -16 <= v <= 32, (name, b)
        if b["rot"]:
            assert b["rot"]["angle"] in (-45, -22.5, 0, 22.5, 45), (name, b["rot"])
    m = {"ambientocclusion": False, "textures": tex, "elements": [el(b) for b in boxes]}
    if cutout:
        m["render_type"] = "minecraft:cutout"
    P.dump(A + "models/block/%s.json" % name, m)


def facing_states(name, model_name=None):
    return {"variants": {"facing=%s" % f: dict({"model": "ashbound:block/" + (model_name or name)}, **({"y": y} if y else {}))
                         for f, y in FACING_Y.items()}}


def multipart(post, side, extra=None):
    parts = [{"apply": {"model": "ashbound:block/" + post}}]
    for f, y in FACING_Y.items():
        a = {"model": "ashbound:block/" + side, "uvlock": False}
        if y:
            a["y"] = y
        parts.append({"when": {f: "true"}, "apply": a})
        if extra:
            parts.append({"when": {f: "true"}, "apply": dict(a, model="ashbound:block/" + extra)})
    return {"multipart": parts}


NAMES = {"silk_web": "Silk Web", "silk_cable": "Silk Cable", "archive_chain": "Archive Chain",
         "archive_lantern": "Archive Lantern", "archive_grille": "Archive Grille", "archive_iron": "Archive Iron",
         "walnut_fence": "Walnut Rail", "walnut_beam": "Walnut Beam", "archive_lectern": "Archive Lectern",
         "archive_coffer": "Archive Coffer", "archive_chair": "Reading Chair"}
TOOLS = {"pickaxe": ["archive_chain", "archive_lantern", "archive_grille", "archive_iron"],
         "axe": ["walnut_fence", "walnut_beam", "archive_lectern", "archive_coffer", "archive_chair"],
         "sword": ["silk_web"], "hoe": ["silk_cable"]}
ITEM_MODEL = {"archive_lantern": "archive_lantern", "walnut_fence": "walnut_fence_inventory",
              "archive_grille": "archive_grille_inventory"}


def main():
    for n, fn in TEXTURES.items():
        fn().save(TEXDIR + n + ".png")
    BS = A + "blockstates/%s.json"
    # cubes
    for n in ("silk_cable", "archive_iron"):
        P.dump(A + "models/block/%s.json" % n, {"parent": "minecraft:block/cube_all", "textures": {"all": "ashbound:block/" + n}})
        P.dump(BS % n, {"variants": {"": {"model": "ashbound:block/" + n}}})
    P.dump(A + "models/block/walnut_beam.json", {"parent": "minecraft:block/cube_column", "textures": {
        "side": "ashbound:block/walnut_beam", "end": "ashbound:block/walnut_beam_top"}})
    P.dump(BS % "walnut_beam", {"variants": {"axis=y": {"model": "ashbound:block/walnut_beam"},
                                             "axis=z": {"model": "ashbound:block/walnut_beam", "x": 90},
                                             "axis=x": {"model": "ashbound:block/walnut_beam", "x": 90, "y": 90}}})
    # the web
    P.dump(A + "models/block/silk_web.json", web_model())
    P.dump(BS % "silk_web", {"variants": {"": {"model": "ashbound:block/silk_web"}}})
    # chain, lanterns
    model("archive_chain", chain(), cutout=True, particle="pewter")
    P.dump(BS % "archive_chain", {"variants": {"axis=y": {"model": "ashbound:block/archive_chain"},
                                               "axis=z": {"model": "ashbound:block/archive_chain", "x": 90},
                                               "axis=x": {"model": "ashbound:block/archive_chain", "x": 90, "y": 90}}})
    model("archive_lantern", lantern(False), particle="pewter")
    model("archive_lantern_hanging", lantern(True), particle="pewter")
    P.dump(BS % "archive_lantern", {"variants": {"hanging=false": {"model": "ashbound:block/archive_lantern"},
                                                 "hanging=true": {"model": "ashbound:block/archive_lantern_hanging"}}})
    # grille and rail
    model("archive_grille_post", grille_post(), particle="pewter")
    model("archive_grille_side", grille_side(), particle="pewter")
    model("archive_grille_silk", grille_silk(), particle="pewter")
    model("archive_grille_inventory", grille_post() + grille_side() + [dict(b, **{"from": [b["from"][0], b["from"][1], 16 - b["to"][2]],
                                                                                  "to": [b["to"][0], b["to"][1], 16 - b["from"][2]]}) for b in grille_side()],
          particle="pewter")
    P.dump(BS % "archive_grille", multipart("archive_grille_post", "archive_grille_side", "archive_grille_silk"))
    model("walnut_fence_post", fence_post())
    model("walnut_fence_side", fence_side())
    model("walnut_fence_inventory", fence_post() + fence_side() + [dict(b, **{"from": [b["from"][0], b["from"][1], 16 - b["to"][2]],
                                                                              "to": [b["to"][0], b["to"][1], 16 - b["from"][2]]}) for b in fence_side()])
    P.dump(BS % "walnut_fence", multipart("walnut_fence_post", "walnut_fence_side"))
    # the facing props
    for n, fn in (("archive_lectern", lectern), ("archive_coffer", coffer), ("archive_chair", chair)):
        model(n, fn())
        P.dump(BS % n, facing_states(n))
    # items, loot, names, tools
    for n in NAMES:
        P.dump(A + "models/item/%s.json" % n, {"parent": "ashbound:block/" + ITEM_MODEL.get(n, n)})
        if n != "silk_web":
            P.dump(P.DATA + "loot_table/blocks/%s.json" % n, {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [
                {"type": "minecraft:item", "name": "ashbound:" + n}], "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
    lang = json.load(open(A + "lang/en_us.json", encoding="utf-8"))
    lang.update({"block.ashbound." + n: t for n, t in NAMES.items()})
    lang["container.ashbound.archive_coffer"] = "Archive Coffer"
    P.dump(A + "lang/en_us.json", lang)
    tag = P.GAME + "src/main/resources/data/minecraft/tags/block/mineable/%s.json"
    for tool, names in TOOLS.items():
        if tool == "sword":
            continue
        path = tag % tool
        have = json.load(open(path, encoding="utf-8"))["values"] if os.path.exists(path) else []
        P.dump(path, {"replace": False, "values": have + ["ashbound:" + n for n in names if "ashbound:" + n not in have]})
    print("silk props: %d blocks, %d textures" % (len(NAMES), len(TEXTURES)))


if __name__ == "__main__":
    main()
