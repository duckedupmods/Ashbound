"""The second forty's epic and legendary weapons, built by hand (worldarms_hero.py's space and parts): what the factions
of the great ruins carry. Each has its own silhouette: a briar blade with a rose at its heart, a sword bound in chains,
a mantis's foreleg, a void blade broken into floating shards, a steam drill, a basalt column, a bardiche rimed in ice,
a trident in a whirlpool, a chimera's jawbone, a barrow king's greatsword, a beetle's carapace, a gryphon aspis, a
kraken bow, a ram-horn bow, an alembic, a split ring holding the void, a rose of light, an ice crown under the aurora,
a cluster of glowing caps, an arch of bones the dead reach out of.
"""
import math
import os
import sys

sys.path.insert(0, 'E:/Ashbound/tools')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import weaponforge as W  # noqa: E402
from voxsword import Sword  # noqa: E402
from weaponforge import bx, ring_xy, seg, chainp  # noqa: E402
from worldarms_hero import sblade, zig, disc, star4, grip, haft, emblem, shield_rows, shield_handle, staff_base, _bow  # noqa: E402


def links(s, a, b, n, z=0.0, mat="dark", size=1.0):
    """a chain from a to b: n links, each turned a quarter from the last"""
    for k in range(n):
        p = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
        q = (a[0] + (b[0] - a[0]) * (k + 1.15) / n, a[1] + (b[1] - a[1]) * (k + 1.15) / n)
        seg(s, p, q, (1.0 if k % 2 else 0.5) * size, (0.5 if k % 2 else 1.1) * size, mat, z)


def arc(s, cx, cy, r, a0, a1, n, w, d, mat, z=0.0, glow=False, taper=False):
    """an arc of segments from angle a0 to a1 (degrees); taper thins it toward both ends"""
    pts = [(cx + math.cos(math.radians(a0 + (a1 - a0) * k / n)) * r, cy + math.sin(math.radians(a0 + (a1 - a0) * k / n)) * r)
           for k in range(n + 1)]
    for k, (p, q) in enumerate(zip(pts, pts[1:])):
        f = math.sin(math.pi * (k + 0.5) / n) if taper else 1.0
        seg(s, p, q, max(0.4, w * f), d, mat, z, glow)
    return pts


# ---------------------------------------------------------------- swords

def thornheart(th, it):
    """two briar strands braided into a leaf blade, thorns off both edges and rose-light between the strands; a rose
    in full bloom for a guard with leaves either side"""
    s = Sword(it["id"])
    y0, L = 4.6, 21.0
    wf = lambda t: 1.0 + 2.0 * math.sin(math.pi * (0.2 + 0.75 * t))
    sblade(s, y0, y0 + L, lambda t: wf(t) * 0.55, lambda t: wf(t) * 0.55, 0.9, mat="wood", spine=False)
    bx(s, 0, y0 + 0.5, 0, 0.8, L - 1.5, 1.2, "glow", glow=True, tag="sap")
    n = 22
    for ph in (0.0, math.pi):   # the two strands
        pts = [(math.sin(k * 0.62 + ph) * wf(k / n) * 0.75, y0 + L * k / n) for k in range(n + 1)]
        for k, (p, q) in enumerate(zip(pts, pts[1:])):
            seg(s, p, q, 1.3 - 0.5 * k / n, 1.6 - 0.4 * k / n, "blade")
    W.tip(s, 0, y0 + L, 1.4, 1.2, n=2)
    for k in range(9):   # thorns, both edges
        t = 0.08 + 0.1 * k
        side = 1 if k % 2 else -1
        x, y = side * wf(t) * 0.8, y0 + L * t
        seg(s, (x, y), (x + side * 1.7, y + 1.2), 0.7, 0.8, "dark")
    for side in (1, -1):   # leaves
        seg(s, (side * 1.4, 2.6), (side * 5.6, 4.6), 1.8, 0.9, "blade")
        seg(s, (side * 4.6, 4.2), (side * 6.6, 5.6), 1.0, 0.8, "blade")
        seg(s, (side * 1.6, 2.7), (side * 5.0, 4.4), 0.4, 1.1, "glow", glow=True)
    for r, n_, sz, mat in ((2.4, 7, 2.4, "acc"), (1.2, 5, 1.8, "acc")):   # the rose
        for k in range(n_):
            a = 2 * math.pi * k / n_ + r
            bx(s, math.cos(a) * r, 2.0 + math.sin(a) * r, 0, sz, sz, 2.8 - r * 0.3, mat)
    bx(s, 0, 2.2, 0, 1.6, 1.6, 3.4, "glow", glow=True)
    grip(s, 0.8, 6.4, 1.9, "wood")
    for k in range(3):   # a vine round the grip
        seg(s, (-1.2, -5.4 + k * 2.0), (1.2, -4.4 + k * 2.0), 0.5, 2.3, "blade")
    for k, a in enumerate((0, 72, 144, 216, 288)):   # a rosebud pommel
        bx(s, math.cos(math.radians(a)) * 0.6, -7.6 + math.sin(math.radians(a)) * 0.6, 0, 1.4, 1.4, 1.6, "acc")
    bx(s, 0, -7.4, 0, 0.8, 0.8, 1.9, "glow", glow=True)
    return s


def chainsworn(th, it):
    """a broad knightly blade bound in chains, soul-light seeping out of its fuller and off its edges; a reliquary
    lantern for a guard with the soul inside, broken chains hanging off the quillons"""
    s = Sword(it["id"])
    y0, L = 6.0, 23.0
    wf = lambda t: 2.7 - 0.5 * t
    sblade(s, y0, y0 + L, wf, wf, 1.4, edge="white", back="white")
    W.tip(s, 0, y0 + L, 4.4, 1.4, n=3)
    bx(s, 0, y0 + 1.0, 0, 0.9, L - 3.0, 1.7, "glow", glow=True, tag="fuller")
    for (ya, yb) in ((y0 + 3.0, y0 + 7.0), (y0 + 11.0, y0 + 15.0), (y0 + 18.0, y0 + 21.0)):   # chains wound across it
        links(s, (-3.4, ya), (3.4, yb), 6, z=0.9)
        links(s, (3.4, ya + 1.0), (-3.4, yb + 1.0), 6, z=-0.9)
    for (x, y, h) in ((3.6, y0 + 9, 2.2), (-3.6, y0 + 13, 1.8), (3.2, y0 + 17, 1.6), (-3.0, y0 + 5, 1.4)):   # wisps off the edges
        seg(s, (x, y), (x * 1.35, y + h), 0.6, 0.6, "white", glow=True)
    bx(s, 0, 2.6, 0, 12.0, 1.8, 2.6, "dark", tag="guard")
    for side in (1, -1):
        chainp(s, (side * 5.6, 2.6), [(1.8, side * 120, 1.4, 2.4), (1.4, side * 160, 1.0, 1.8)], "dark")
        links(s, (side * 4.4, 2.6), (side * 5.2, -4.0), 5, size=0.8)   # broken chains hanging
        seg(s, (side * 5.2, -4.0), (side * 5.8, -4.9), 0.8, 0.4, "dark")
    bx(s, 0, 1.6, 0, 4.0, 4.6, 3.4, "acc", tag="reliquary")   # the reliquary
    bx(s, 0, 2.2, 0, 2.6, 3.4, 3.7, "glow", glow=True)
    for x in (-1.4, 1.4):
        bx(s, x, 1.6, 0, 0.5, 4.6, 3.8, "dark")
    bx(s, 0, 6.2, 0, 3.0, 0.8, 2.8, "dark")
    emblem("crown", s, 0, 7.4, 3.0, 3.0)
    grip(s, 1.6, 6.8, 2.0)
    bx(s, 0, -7.8, 0, 3.0, 2.6, 3.0, "acc", tag="pommel")
    bx(s, 0, -7.2, 0, 1.6, 1.4, 3.3, "glow", glow=True)
    bx(s, 0, -8.6, 0, 1.6, 0.8, 1.6, "dark")
    return s


# ---------------------------------------------------------------- daggers

def mantis_talon(th, it):
    """a mantis's foreleg: jointed chitin hooking forward into a down-curled point, a saw of teeth on its inner edge,
    venom showing between them; the guard a mantis head with two great eyes"""
    s = Sword(it["id"])
    y0, L = 3.2, 13.0
    cx = lambda t: 3.8 * t ** 2.2
    wf = lambda t: 1.6 * (1 - 0.5 * t)
    sblade(s, y0, y0 + L, wf, wf, 1.4, cx=cx, step=0.9, edge="glow")
    tipp = chainp(s, (cx(1) - 0.3, y0 + L - 0.4), [(2.6, -45, 1.4, 1.3), (2.6, -95, 1.1, 1.2), (2.2, -140, 0.8, 1.0),
                                                    (1.4, -175, 0.5, 0.8)], "blade")
    for t in (0.3, 0.62):   # the joints
        bx(s, cx(t), y0 + L * t, 0, wf(t) * 2 + 0.6, 0.8, 1.8, "dark", tag="joint")
    for k in range(7):   # the saw, inner edge
        t = 0.12 + 0.12 * k
        x, y = cx(t) + wf(t), y0 + L * t
        seg(s, (x - 0.2, y), (x + 1.2, y + 0.8), 0.7, 1.0, "acc")
    for k in range(2):   # spines on the back
        t = 0.35 + 0.3 * k
        x, y = cx(t) - wf(t), y0 + L * t
        seg(s, (x + 0.2, y), (x - 1.4, y + 1.8), 0.8, 1.0, "dark")
    bx(s, 0, 0.2, 0, 4.6, 2.6, 2.6, "acc", tag="head")   # a mantis head
    bx(s, 0, -0.8, 0, 2.2, 1.2, 2.0, "acc")
    for side in (1, -1):
        bx(s, side * 1.9, 1.6, 0, 1.3, 1.3, 2.8, "glow", glow=True, tag="eye")
        chainp(s, (side * 1.0, 2.8), [(2.6, side * 30, 0.4, 0.4), (2.0, side * 60, 0.3, 0.3)], "dark")   # feelers
    grip(s, -0.4, 4.6, 1.9)
    for k in range(3):
        bx(s, 0, -2.0 - k * 1.4, 0, 2.3 - 0.2 * k, 0.6, 2.3 - 0.2 * k, "acc", tag="segment")
    bx(s, 0, -6.2, 0, 1.6, 1.4, 1.6, "acc")
    return s


def void_splinter(th, it):
    """a blade broken into shards that hang in line, each its own floating piece edged in void light, a thread of
    void running through the gaps; a guard of two black crescents round an open eye"""
    s = Sword(it["id"])
    y = 3.4
    for k, (h, w, lean) in enumerate(((3.6, 3.0, 4), (3.2, 2.6, -6), (2.8, 2.2, 5), (2.4, 1.8, -4), (2.6, 1.2, 2))):
        cx = 0.25 * (1 if k % 2 else -1)
        piv = (cx, y + h / 2, 0)
        for j, f in enumerate((1.0, 0.7, 0.4)):   # a diamond: wide in the middle
            yy = y + h * (0.5 - 0.5 * f) if j else y
            bx(s, cx, yy, 0, w * f, h * f if j else h, 1.0 + 0.2 * j, "blade", rots=(("z", lean),), pivot=piv)
        bx(s, cx, y + 0.3, 0, w * 0.35, h - 0.6, 1.5, "glow", glow=True, rots=(("z", lean),), pivot=piv)
        if k < 4:
            bx(s, 0, y + h, 0, 0.35, 1.2, 0.35, "white", glow=True, tag="thread")
        y += h + 1.2
    W.tip(s, 0, y - 1.2, 1.0, 0.9, n=2, step=1.0)
    for (x, yy, sz) in ((3.0, 7.0, 0.9), (-2.8, 10.4, 0.7), (2.4, 14.6, 0.6), (-2.2, 4.8, 0.6)):   # little shards drifting
        bx(s, x, yy, 0, sz, sz * 1.8, 0.6, "blade", rots=(("z", 30),), pivot=(x, yy, 0))
        bx(s, x, yy + sz * 0.4, 0, sz * 0.4, sz, 0.8, "glow", glow=True, rots=(("z", 30),), pivot=(x, yy, 0))
    bx(s, 0, 0.6, 0, 3.2, 1.8, 2.2, "dark", tag="guard")
    for side in (1, -1):   # crescents, horns up
        arc(s, side * 2.4, 3.4, 2.6, 250 if side > 0 else 290, 400 if side > 0 else 140, 7, 1.3, 1.6, "dark", taper=True)
    emblem("eye", s, 0, 2.6, 3.4, 2.6)
    grip(s, 0.6, 4.8, 1.9)
    bx(s, 0, -5.6, 0, 1.8, 1.6, 1.8, "dark", tag="pommel")
    bx(s, 0, -7.6, 0, 1.0, 1.6, 1.0, "blade", rots=(("z", 45),), pivot=(0, -6.8, 0))   # a shard below it
    bx(s, 0, -7.2, 0, 0.5, 0.8, 1.2, "glow", glow=True)
    return s


# ---------------------------------------------------------------- hammers

def rockgrinder(th, it):
    """a steam driller's engine for a head: a riveted boiler with a stepped drill bit out of one end and a piston
    hammer face out of the other, a smokestack breathing fire, a pipe down to the haft"""
    s = Sword(it["id"])
    haft(s, -12.0, 13.0, 2.2)
    grip(s, 1.0, 7.0, 2.6)
    bx(s, 0, -13.6, 0, 3.0, 2.0, 3.0, "dark", tag="pommel")
    cy = 16.0
    bx(s, 0, cy - 3.4, 0, 8.4, 6.8, 6.8, "blade", tag="boiler")
    for x in (-3.6, 0.0, 3.6):
        bx(s, x, cy - 3.8, 0, 1.0, 7.6, 7.6, "dark", tag="band")
        for yy in (cy - 3.0, cy + 2.6):
            for z in (3.9, -3.9):
                bx(s, x + 0.9, yy, z, 0.6, 0.6, 0.3, "acc", tag="rivet")
    for k, w in enumerate((6.0, 5.0, 4.0, 3.0, 2.0, 1.0)):   # the drill
        bx(s, 4.2 + k * 1.3 + 0.65, cy - w / 2, 0, 1.32, w, w, "dark" if k % 2 else "acc", tag="drill",
           rots=(("x", 20 * k),), pivot=(4.2 + k * 1.3 + 0.65, cy, 0))
    for k in range(4):   # its flute, a spiral ridge
        bx(s, 4.8 + k * 1.6, cy + 2.4 - k * 0.6, 0, 0.6, 1.0, 4.6 - k, "acc")
    bx(s, -5.2, cy - 2.6, 0, 1.8, 5.2, 5.2, "dark", tag="piston")
    bx(s, -6.8, cy - 3.2, 0, 1.6, 6.4, 6.4, "blade", tag="face")
    for z in (2.2, -2.2):
        bx(s, -5.2, cy - 0.6, z, 1.9, 1.0, 0.8, "glow", glow=True)
    bx(s, 1.8, cy + 3.4, 0, 1.8, 3.6, 1.8, "dark", tag="stack")
    bx(s, 1.8, cy + 7.0, 0, 2.6, 0.8, 2.6, "dark")
    for k, (x, h) in enumerate(((1.8, 2.4), (1.2, 1.4), (2.4, 1.6))):
        bx(s, x, cy + 7.8 + k * 0.4, 0, 1.0 - 0.2 * k, h, 1.0 - 0.2 * k, "glow", glow=True)
    seg(s, (-2.0, cy - 3.4), (-1.0, cy - 7.0), 1.0, 1.0, "acc")   # a pipe down to the haft
    bx(s, -1.0, cy - 8.0, 0, 2.8, 1.0, 2.8, "acc")
    bx(s, 0, cy - 0.8, 3.6, 2.6, 2.6, 0.4, "dark", tag="gauge")
    bx(s, 0, cy - 0.4, 3.9, 1.6, 1.6, 0.3, "glow", glow=True)
    return s


def legions_pillar(th, it):
    """a cluster of hexagonal basalt columns bound by a gold legion band, teal fire burning out of their joins and
    off the top, embers drifting"""
    s = Sword(it["id"])
    haft(s, -14.0, 13.0, 2.4)
    grip(s, 1.0, 8.0, 2.8)
    bx(s, 0, -15.8, 0, 3.4, 2.4, 3.4, "acc", tag="pommel")
    for y in (4.0, 9.0):
        bx(s, 0, y, 0, 3.0, 1.0, 3.0, "acc", tag="band")
    cy = 15.0
    for (x0, x1, y, h, d) in ((-8.0, 7.0, cy, 4.2, 5.0), (-6.4, 8.6, cy + 4.2, 3.8, 4.6), (-7.2, 5.0, cy - 3.6, 3.6, 4.4),
                              (-4.4, 6.0, cy + 7.8, 2.6, 3.6)):
        n = int((x1 - x0) / 2.6) + 1
        for k in range(n):   # each column in drums, a seam of fire between
            xa = x0 + k * (x1 - x0) / n
            bx(s, xa + (x1 - x0) / n / 2, y, 0, (x1 - x0) / n - 0.4, h - 0.3, d, "blade", tag="basalt")
            bx(s, xa + (x1 - x0) / n / 2, y + 0.4, 0, (x1 - x0) / n - 1.2, h - 1.1, d + 0.3, "dark")
            if k:
                bx(s, xa, y + 0.2, 0, 0.5, h - 0.7, d - 0.4, "glow", glow=True, tag="seam")
        bx(s, x0 - 0.4, y + 0.6, 0, 0.8, h - 1.5, d - 1.0, "glow", glow=True, tag="face")
        bx(s, x1 + 0.4, y + 0.6, 0, 0.8, h - 1.5, d - 1.0, "glow", glow=True, tag="face")
    bx(s, 0, cy - 4.0, 0, 3.4, 16.4, 5.6, "acc", tag="legion_band")
    emblem("horns", s, 0, cy + 5.0, 4.6, 6.2)
    for k, (x, h, lean) in enumerate(((-5.0, 4.6, 10), (-2.0, 6.2, -5), (1.6, 5.4, 8), (4.6, 3.8, -12), (6.8, 2.6, 4))):   # teal fire
        chainp(s, (x, cy + 10.2), [(h * 0.5, lean, 1.8, 1.8), (h * 0.5, -lean * 1.5, 0.9, 0.9)], "glow", glow=True)
    for (x, y) in ((-7.6, cy + 13.6), (3.4, cy + 15.4), (8.4, cy + 11.0), (-3.0, cy + 16.4)):
        bx(s, x, y, 0, 0.7, 0.7, 0.7, "white", glow=True)
    return s


# ---------------------------------------------------------------- spears

def wardens_bardiche(th, it):
    """a great black crescent fixed to the haft at two places, its edge crusted with ice and icicles hanging off its
    beard; a spike on top and the cell keys still hanging on a ring"""
    s = Sword(it["id"])
    top = 14.0
    haft(s, -24.0, top + 8.0, 1.8)
    grip(s, -2.0, 8.0, 2.2)
    bx(s, 0, -25.6, 0, 2.6, 2.0, 2.6, "dark", tag="butt")
    for y in (3.0, top + 7.0):   # the two straps
        bx(s, 0, y, 0, 2.8, 1.4, 2.8, "dark", tag="strap")
    x0 = 1.4   # the crescent: its back on the haft, the bit sweeping out and down to a beard
    for k in range(16):
        t = k / 15
        y = 2.0 + t * (top + 7.0 - 2.0)
        w = 1.6 + 5.0 * math.sin(math.pi * min(1.0, t * 1.1)) ** 0.8
        lift = 2.4 * (1 - t) ** 2
        bx(s, x0 + w / 2, y - lift, 0, w, (top + 5.0) / 15 + 0.1, 1.2, "blade", tag="blade")
        bx(s, x0 + w + 0.35, y - lift, 0, 0.7, (top + 5.0) / 15 + 0.1, 0.9, "glow", glow=True, tag="rime")
    for k, (y, ln) in enumerate(((4.0, 3.0), (7.6, 2.2), (11.0, 3.4), (15.0, 2.0), (18.6, 2.6))):   # ice crust and icicles
        x = x0 + 1.6 + 5.0 * math.sin(math.pi * min(1.0, (y - 2.0) / (top + 5.0) * 1.1)) ** 0.8
        seg(s, (x, y), (x + 1.0, y - ln), 1.0, 1.0, "acc")
        seg(s, (x + 1.0, y - ln), (x + 1.3, y - ln - 1.2), 0.5, 0.6, "acc")
    for z in (0.7, -0.7):
        zig(s, [(x0 + 1.0, 3.0), (x0 + 2.6, 7.0), (x0 + 1.6, 11.0), (x0 + 3.4, 15.0), (x0 + 2.4, 19.0)], 0.5, 0.2, z=z)
    chainp(s, (0, top + 8.0), [(4.0, 0, 1.6, 1.4), (2.4, 0, 0.8, 0.8)], "blade")   # the spike
    chainp(s, (-0.9, top + 4.0), [(2.4, 70, 1.2, 1.2), (1.4, 110, 0.7, 0.7)], "dark")   # a back hook
    ring_xy(s, -1.8, 0.2, 1.5, 0.4, "dark", 10, depth=0.5)   # the keys on their ring
    for k, (x, ln, ang) in enumerate(((-3.0, 3.2, 10), (-1.8, 3.8, 0), (-0.6, 2.8, -12))):
        seg(s, (x, -1.0), (x - math.sin(math.radians(ang)) * ln, -1.0 - ln), 0.5, 0.4, "acc")
        bx(s, x - math.sin(math.radians(ang)) * ln, -1.0 - ln - 0.6, 0, 1.0, 0.8, 0.4, "acc")
    return s


def tidecallers_trident(th, it):
    """three barbed sea-bronze tines on a gold crown, a whirlpool of light turning round them, a pearl at their root,
    a kraken arm coiling up the haft"""
    s = Sword(it["id"])
    top = 15.0
    haft(s, -26.0, top, 1.8)
    grip(s, 1.0, 8.0, 2.2)
    bx(s, 0, -27.6, 0, 2.8, 2.0, 2.8, "gold", tag="butt")
    k, y = 0, -22.0
    while y < top - 3:   # a tentacle coiling up the haft, suckers out
        x = 1.4 * math.sin(k * 0.9)
        z = 1.4 * math.cos(k * 0.9)
        bx(s, x, y, z, 1.4, 1.6, 1.4, "acc", tag="tentacle")
        if k % 2:
            bx(s, x * 1.5, y + 0.4, z * 1.5, 0.6, 0.6, 0.6, "glow", glow=True)
        y += 1.4
        k += 1
        if -12 < y < 3:
            y = 3.0
    bx(s, 0, top, 0, 3.2, 2.0, 3.2, "gold", tag="socket")
    bx(s, 0, top + 2.0, 0, 9.6, 1.6, 2.6, "gold", tag="crown")
    disc(s, 0, top + 3.6, 1.4, 0, 2.6, "white")   # the pearl
    bx(s, 0, top + 3.4, 0, 1.8, 15.0, 1.6, "blade", tag="tine")   # the middle tine, long and barbed
    W.tip(s, 0, top + 18.4, 3.0, 1.6, n=3, step=1.2)
    for j in (1, -1):
        seg(s, (j * 0.7, top + 17.0), (j * 2.2, top + 15.2), 0.8, 1.2, "blade")
    for side in (1, -1):   # the outer tines sweep out then rise
        end = chainp(s, (side * 4.4, top + 3.0), [(3.0, -side * 35, 1.6, 1.5), (4.0, -side * 5, 1.5, 1.5), (3.0, side * 12, 1.3, 1.4)], "blade")
        W.tip(s, end[0], end[1], 2.4, 1.4, n=2, step=1.2)
        seg(s, (end[0] - side * 0.6, end[1] - 1.6), (end[0] - side * 2.0, end[1] - 3.2), 0.8, 1.1, "blade")   # inner barb
    bx(s, 0, top + 6.0, 0, 0.6, 10.0, 1.9, "glow", glow=True, tag="core")
    n = 34   # the whirlpool: a spiral of light winding up round the crown, wide at the bottom
    pts = []
    for j in range(n + 1):
        a = math.radians(j * 32)
        rr = 7.4 - 4.4 * j / n
        pts.append((math.cos(a) * rr, top - 3.0 + 13.0 * j / n, math.sin(a) * rr * 0.55))
    for j, (p, q) in enumerate(zip(pts, pts[1:])):
        seg(s, p[:2], q[:2], 1.0 - 0.4 * j / n, 0.8, "white" if j % 4 == 0 else "glow", p[2], glow=True)
    for (x, y) in ((-7.6, top + 3.0), (7.0, top + 7.4), (-5.4, top + 11.0), (6.0, top - 1.0)):   # spray thrown off it
        bx(s, x, y, 0, 0.7, 0.9, 0.7, "white", glow=True)
    return s


# ---------------------------------------------------------------- two-handers

def chimera_jaw(th, it):
    """a great jawbone for a blade: the hinge knob raking back at its root, fangs down its front edge and smaller
    teeth on its back, acid between them; a brass vat-collar at the guard with a tube feeding it"""
    s = Sword(it["id"])
    y0, L = 6.0, 26.0
    wf = lambda t: 4.0 * (1 - 0.5 * t)
    cx = lambda t: -0.8 * t
    sblade(s, y0, y0 + L, wf, wf, 2.2, cx=cx, step=1.4, spine=False)
    W.tip(s, cx(1), y0 + L, 3.6, 2.0, n=3, step=1.3)
    bx(s, 0, y0 + 1.0, 0, 1.0, L - 4, 2.5, "glow", glow=True, tag="marrow")
    chainp(s, (-3.6, y0 + 1.0), [(4.4, 50, 3.2, 2.0), (2.4, 20, 2.6, 1.8)], "blade")   # the hinge knob
    for k in range(10):   # fangs on the front edge, acid at their roots
        t = 0.06 + 0.095 * k
        x, y = cx(t) + wf(t), y0 + L * t
        big = 1.6 if k in (1, 5) else 1.1
        seg(s, (x - 0.4, y), (x + big * 1.1, y + big * 0.6), 1.0 * big, 1.6, "acc")
        bx(s, x - 0.3, y - 0.6, 0, 0.6, 1.0, 2.5, "glow", glow=True)
    for k in range(6):   # small teeth on the back
        t = 0.3 + 0.11 * k
        x, y = cx(t) - wf(t), y0 + L * t
        seg(s, (x + 0.3, y), (x - 0.9, y + 0.7), 0.8, 1.4, "acc")
    for (x, ln) in ((2.4, 3.0), (3.6, 1.8)):   # acid dripping off a fang
        bx(s, x + 1.8, y0 + 2.6 - ln, 0, 0.6, ln, 0.6, "glow", glow=True)
    bx(s, 0, 2.0, 0, 7.0, 3.6, 3.6, "gold", tag="collar")
    for x in (-2.4, 0.0, 2.4):
        bx(s, x, 2.4, 1.85, 1.2, 2.4, 0.3, "glow", glow=True, tag="window")
    seg(s, (3.4, 3.0), (5.0, 7.6), 1.0, 1.0, "gold")   # a feeding tube
    seg(s, (5.0, 7.6), (cx(0.1) + wf(0.1), y0 + 2.4), 0.9, 0.9, "gold")
    emblem("skull", s, 0, 3.4, 4.2, 4.4)
    grip(s, 2.0, 12.4, 2.4)
    bx(s, 0, -13.6, 0, 3.2, 2.6, 3.2, "acc", tag="pommel")
    for side in (1, -1):
        seg(s, (side * 1.0, -13.0), (side * 2.6, -14.8), 0.8, 1.0, "acc")
    return s


def kingsbarrow(th, it):
    """a wide black leaf greatblade, gold torcs bound round its root, soul-runes down it and the dead streaming off its
    edges like smoke; a crowned skull-helm for a guard, eyes burning; a torc for a pommel"""
    s = Sword(it["id"])
    y0, L = 7.0, 28.0
    wf = lambda t: 3.0 + 1.8 * math.sin(math.pi * min(1.0, 0.25 + t * 0.9)) - 1.6 * t
    sblade(s, y0, y0 + L, wf, wf, 1.8, step=1.4, edge="white", back="white")
    W.tip(s, 0, y0 + L, 3.4, 1.8, n=3, step=1.4)
    yy, k = y0 + 3.0, 0
    while yy < y0 + L - 3:   # runes
        for z in (1.0, -1.0):
            bx(s, 0.4 if k % 2 else -0.4, yy, z, 1.2 if k % 3 else 0.6, 1.4, 0.2, "glow", glow=True)
        yy += 2.2
        k += 1
    for y in (y0 + 0.4, y0 + 2.0):   # gold torcs
        bx(s, 0, y, 0, wf(0) * 2 + 0.8, 0.9, 2.6, "gold", tag="torc")
    for side in (1, -1):   # the dead, streaming off the edges and back
        for k, (t, ln) in enumerate(((0.25, 4.0), (0.5, 5.0), (0.75, 3.6))):
            x, y = side * (wf(t) + 0.4), y0 + L * t
            pts = [(x, y), (x + side * ln * 0.4, y - ln * 0.35), (x + side * ln * 0.7, y - ln * 0.55), (x + side * ln, y - ln * 0.9)]
            for j, (p, q) in enumerate(zip(pts, pts[1:])):
                seg(s, p, q, 1.2 - 0.3 * j, 0.6, "white" if j == 0 else "glow", glow=True)
    bx(s, 0, 1.4, 0, 13.0, 2.0, 2.8, "dark", tag="guard")
    for side in (1, -1):
        chainp(s, (side * 6.0, 2.4), [(2.0, -side * 20, 1.6, 2.4), (1.6, -side * 5, 1.0, 1.6)], "dark")
    bx(s, 0, 1.0, 0, 5.4, 5.6, 4.4, "blade", tag="helm")   # the crowned skull-helm
    bx(s, 0, 1.6, 0, 4.6, 1.0, 4.7, "dark", tag="visor")
    for side in (1, -1):
        bx(s, side * 1.2, 1.8, 0, 1.2, 0.6, 4.8, "glow", glow=True)
    for k in range(5):
        h = 2.6 if k % 2 == 0 else 1.6
        bx(s, -2.4 + k * 1.2, 6.6, 0, 0.9, h, 4.6, "gold", tag="crown")
    bx(s, 0, 6.2, 0, 5.8, 0.8, 4.8, "gold")
    grip(s, 1.0, 12.0, 2.6, "wood")
    for k in range(4):
        bx(s, 0, -10.0 + k * 2.6, 0, 3.0, 0.9, 3.0, "wrap", tag="fur")
    ring_xy(s, 0, -13.4, 1.9, 0.9, "gold", 10, depth=1.4)
    bx(s, 0, -13.9, 0, 1.2, 1.2, 1.8, "glow", glow=True)
    return s


# ---------------------------------------------------------------- shields

def brood_carapace(th, it):
    """a beetle's back-plate: an oval split by a ridge, plated in bands, two mandibles curving out at its brow and a
    cluster of glowing eyes between them, spurs down its edges"""
    s = Sword(it["id"])
    F = 2.4
    rows = []
    for y in range(-14, 10, 2):
        h = (y + 1 + 2.0) / 12.5
        rows.append((y, y + 2, max(3.0, 16.0 * math.sqrt(max(0.0, 1 - h * h)))))
    shield_rows(s, rows, F, "blade")
    bx(s, 0, -14.0, 2.4, 1.6, 23.0, 1.2, "dark", tag="ridge")
    for y in (-9.0, -4.0, 1.0, 6.0):   # the bands
        h = (y + 2.0) / 12.5
        bx(s, 0, y, 2.5, 16.0 * math.sqrt(max(0.0, 1 - h * h)) - 1.0, 0.8, 0.8, "dark", tag="band")
    for side in (1, -1):
        chainp(s, (side * 3.0, 9.2), [(3.0, -side * 20, 2.0, 2.0), (3.0, side * 25, 1.6, 1.6), (2.4, side * 70, 1.0, 1.2),
                                      (1.4, side * 110, 0.6, 0.8)], "acc", z=2.0)   # mandibles
        for k, y in enumerate((-8.0, -2.0, 4.0)):   # spurs off the rim
            h = (y + 2.0) / 12.5
            x = side * 8.0 * math.sqrt(max(0.0, 1 - h * h))
            chainp(s, (x, y), [(2.2, -side * 75, 1.2, 1.4), (1.2, -side * 60, 0.6, 0.8)], "acc", z=1.6)
    for (x, y, sz) in ((-1.4, 7.0, 1.4), (1.4, 7.0, 1.4), (-2.8, 5.6, 1.0), (2.8, 5.6, 1.0), (-0.9, 4.8, 0.8), (0.9, 4.8, 0.8)):
        bx(s, x, y, 3.0, sz + 0.4, sz + 0.4, 0.5, "dark")
        bx(s, x, y + 0.2, 3.3, sz, sz, 0.4, "glow", glow=True, tag="eye")
    shield_handle(s)
    return s


def gryphon_aegis(th, it):
    """a round bronze aspis with a gryphon's head for a boss, hooked beak out, and its wings spread out past the rim;
    lightning cracking across the face"""
    s = Sword(it["id"])
    disc(s, 0, -2.0, 8.6, 1.4, 2.2, "blade")
    ring_xy(s, 0, -2.0, 8.4, 1.2, "acc", depth=2.8, z=1.6)
    ring_xy(s, 0, -2.0, 5.6, 0.5, "acc", depth=0.6, z=2.7)
    for z in (2.65,):
        zig(s, [(-6.6, 2.0), (-4.4, 0.4), (-5.2, -2.4), (-3.0, -4.4)], 0.6, 0.3, z=z)
        zig(s, [(6.4, -5.6), (4.6, -3.8), (5.4, -1.2), (3.2, 1.0)], 0.6, 0.3, z=z)
        zig(s, [(-1.6, -8.4), (0.4, -7.0), (-0.6, -5.4)], 0.6, 0.3, z=z)
    for side in (1, -1):   # the wings, out past the rim
        for k, (ln, ang) in enumerate(((10.0, 50), (9.4, 66), (8.6, 82), (7.6, 98), (6.4, 114), (5.0, 130))):
            a = (side * 6.0, 2.6 - k * 0.5)
            b = (a[0] + side * ln * math.sin(math.radians(ang)), a[1] + ln * math.cos(math.radians(ang)))
            seg(s, a, b, 1.7 - 0.1 * k, 1.2, "acc" if k % 2 == 0 else "blade", z=0.8)
            if k % 2 == 0:
                seg(s, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), b, 0.5, 1.4, "white", z=0.8, glow=True)
    bx(s, 0, -4.8, 3.4, 4.6, 5.2, 3.2, "acc", tag="head")   # the gryphon head
    bx(s, 0, -0.4, 3.0, 3.4, 1.8, 2.4, "acc", tag="crest")
    for side in (1, -1):
        chainp(s, (side * 1.4, 1.0), [(2.0, side * 20, 0.8, 0.8), (1.4, side * 50, 0.5, 0.5)], "acc", z=3.0)   # ear tufts
        bx(s, side * 1.3, -2.4, 5.1, 1.2, 0.8, 0.3, "glow", glow=True)
    for k, (w, d) in enumerate(((3.0, 1.6), (2.4, 1.4), (1.8, 1.2))):   # the hooked beak
        bx(s, 0, -6.0 - k * 1.0, 5.0 + k * 0.9, w, 1.4, d, "gold")
    bx(s, 0, -9.0, 6.6, 1.2, 1.6, 0.9, "gold")
    shield_handle(s)
    return s


# ---------------------------------------------------------------- bows

def kraken_bow(th, it, pull=0.0, arrow=False, name=None):
    """two kraken arms for limbs: suckers down their bellies, their tips curling back, an ink-black eye at the grip"""
    s = _bow(th, it, pull, arrow, name)
    A, U = W.A, W.U
    for sgn in (1, -1):
        for k in range(8):   # suckers on the belly, the string's side
            t = 0.18 + 0.09 * k
            p = W.bow_at(sgn * t, pull)
            bx(s, p[0] - A[0] * 0.9, p[1] - A[1] * 0.9 - 0.4, W.BZ, 0.9 - 0.05 * k, 0.9 - 0.05 * k, 1.9, "acc")
            bx(s, p[0] - A[0] * 1.2, p[1] - A[1] * 1.2 - 0.25, W.BZ, 0.4, 0.4, 2.0, "glow", glow=True)
        tip = W.bow_at(sgn * 1.0, pull)
        ang0 = math.degrees(math.atan2(-U[0] * sgn, U[1] * sgn))
        chainp(s, tip, [(1.6, ang0 - sgn * 40, 1.1, 1.2), (1.4, ang0 - sgn * 100, 0.9, 1.0), (1.2, ang0 - sgn * 160, 0.7, 0.8),
                        (0.9, ang0 - sgn * 220, 0.5, 0.6)], "blade", z=W.BZ)
        for k, t in enumerate((0.4, 0.7)):   # webbing nubs on the back
            p = W.bow_at(sgn * t, pull)
            seg(s, p, (p[0] + A[0] * 1.6, p[1] + A[1] * 1.6), 0.7, 1.0, "blade", W.BZ)
    g = W.bow_at(0.0, pull)
    bx(s, g[0] + A[0] * 1.6, g[1] + A[1] * 1.6 - 1.6, W.BZ, 3.2, 3.2, 2.8, "acc", tag="eye")
    bx(s, g[0] + A[0] * 1.6, g[1] + A[1] * 1.6 - 1.2, W.BZ, 2.2, 2.4, 3.0, "glow", glow=True)
    bx(s, g[0] + A[0] * 1.6, g[1] + A[1] * 1.6 - 1.2, W.BZ, 0.7, 2.2, 3.2, "void")
    return s


def khans_horn(th, it, pull=0.0, arrow=False, name=None):
    """the Salt Khan's horn bow: a ram's horn spiralling at each tip, gold-lacquered bands down the limbs, a sun at
    the grip, sand glittering round the string"""
    s = _bow(th, it, pull, arrow, name)
    A, U = W.A, W.U
    for sgn in (1, -1):
        for t in (0.3, 0.55, 0.8):   # gold bands
            p = W.bow_at(sgn * t, pull)
            bx(s, p[0], p[1] - 0.5, W.BZ, 1.9, 1.0, 1.9, "gold")
        tip = W.bow_at(sgn * 0.92, pull)
        ang0 = math.degrees(math.atan2(-U[0] * sgn, U[1] * sgn))
        segs = [(2.0 - 0.18 * k, ang0 + sgn * 38 * (k + 1), 1.9 - 0.15 * k, 1.9 - 0.12 * k) for k in range(9)]   # the ram's horn
        chainp(s, tip, segs, "blade", z=W.BZ)
        for k in range(3):   # its ridges
            p = W.bow_at(sgn * (0.86 - 0.04 * k), pull)
            bx(s, p[0] + A[0] * 0.8, p[1] + A[1] * 0.8 - 0.3, W.BZ, 0.6, 0.6, 2.2, "acc")
    g = W.bow_at(0.0, pull)
    emblem("sun", s, g[0] + A[0] * 2.2, g[1] + A[1] * 2.2 + 1.2, 3.4, 2.6)
    t0, t1 = W.bow_at(-1, pull), W.bow_at(1, pull)
    if not pull:
        for k in range(7):   # sand glittering along the string
            f = 0.12 + 0.12 * k
            off = 0.9 if k % 2 else -0.7
            bx(s, t0[0] + (t1[0] - t0[0]) * f - A[0] * off, t0[1] + (t1[1] - t0[1]) * f - A[1] * off, W.BZ, 0.45, 0.45, 0.45,
               "white", glow=True)
    return s


# ---------------------------------------------------------------- staffs

def alembic_of_ruin(th, it):
    """a round glass alembic of boiling acid in a brass cage, coils round it, its neck bending off to a drip,
    bubbles rising"""
    s = Sword(it["id"])
    top = 12.0
    staff_base(s, top)
    bx(s, 0, top - 0.6, 0, 4.4, 1.6, 4.4, "acc", tag="cup")
    cy = top + 5.4
    for (w, h) in ((7.4, 4.0), (6.2, 6.6), (4.2, 8.2)):   # the flask
        bx(s, 0, cy - h / 2, 0, w, h, w, "glow", glow=True, tag="flask")
    for k in range(4):   # the brass cage
        a = math.pi / 4 + k * math.pi / 2
        x, z = math.cos(a) * 3.4, math.sin(a) * 3.4
        bx(s, x * 1.12, cy - 4.4, z * 1.12, 0.8, 8.8, 0.8, "acc", tag="cage")
    for y in (cy - 2.6, cy + 1.6):   # coils
        for k in range(10):
            a = 2 * math.pi * k / 10
            bx(s, math.cos(a) * 4.3, y, math.sin(a) * 4.3, 1.6, 0.8, 1.0, "acc", rots=(("y", -math.degrees(a) + 90),),
               pivot=(math.cos(a) * 4.3, y, math.sin(a) * 4.3))
    bx(s, 0, cy + 4.0, 0, 1.8, 2.6, 1.8, "glow", glow=True, tag="neck")
    bx(s, 0, cy + 6.4, 0, 2.4, 0.8, 2.4, "acc")
    chainp(s, (0, cy + 6.8), [(2.0, -30, 1.2, 1.2), (3.0, -80, 1.0, 1.0), (2.4, -130, 0.9, 0.9)], "acc")   # the bent neck
    bx(s, 5.6, cy + 2.2, 0, 0.6, 1.4, 0.6, "glow", glow=True)   # a drip off it
    bx(s, 5.6, cy + 0.6, 0, 0.8, 0.8, 0.8, "glow", glow=True)
    for (x, y, sz) in ((-1.2, cy + 9.6, 0.8), (0.8, cy + 11.4, 0.6), (-0.4, cy + 13.0, 0.5), (1.6, cy + 8.6, 0.5)):   # bubbles
        bx(s, x, y, 0, sz, sz, sz, "white", glow=True)
    return s


def riftcaller(th, it):
    """a great ring broken in two, its halves held apart; between them a tear of void with an eye in it, shards of
    the ring orbiting"""
    s = Sword(it["id"])
    top = 12.0
    staff_base(s, top)
    bx(s, 0, top - 0.8, 0, 3.6, 1.8, 3.6, "dark", tag="collar")
    cy, R = top + 8.0, 6.2
    for side in (1, -1):   # the two halves, pulled apart
        off = side * 1.6
        arc(s, off, cy, R, -70 if side > 0 else 110, 70 if side > 0 else 250, 7, 2.4, 2.2, "blade")
        arc(s, off, cy, R - 1.3, -60 if side > 0 else 120, 60 if side > 0 else 240, 6, 0.5, 2.5, "glow", glow=True)
        for a in (-70, 70):   # broken ends, glowing
            aa = math.radians(a if side > 0 else 180 - a)
            bx(s, off + math.cos(aa) * R, cy + math.sin(aa) * R - 0.8, 0, 1.4, 1.6, 2.6, "glow", glow=True)
    for k in range(7):   # the tear
        y = cy - R + 1.4 + k * (2 * R - 2.8) / 6
        w = 2.8 * math.sin(math.pi * (k + 0.5) / 7) + 0.6
        bx(s, 0.3 * (1 if k % 2 else -1), y, 0, w, (2 * R - 2.8) / 6 + 0.1, 1.2, "void")
        bx(s, 0.3 * (1 if k % 2 else -1), y, 0, w + 0.8, (2 * R - 2.8) / 6 + 0.1, 0.8, "white", glow=True)
    emblem("eye", s, 0, cy + 1.4, 2.8, 2.6)
    for (x, y, ang) in ((-8.6, cy + 4.0, 30), (8.4, cy - 3.4, -20), (-7.0, cy - 6.0, 60), (6.8, cy + 7.0, -45)):   # shards
        bx(s, x, y, 0, 1.4, 2.4, 1.2, "blade", rots=(("z", ang),), pivot=(x, y, 0))
        bx(s, x, y + 0.6, 0, 0.5, 1.2, 1.4, "glow", glow=True, rots=(("z", ang),), pivot=(x, y, 0))
    bx(s, 0, top + 0.6, 0, 1.0, cy - R - top, 1.0, "dark")
    return s


def everbloom(th, it):
    """a rose wide open on a briar staff: outer petals dark red, the inner ones light, sepals cupping it, petals of
    light falling off it and a vine climbing the haft"""
    s = Sword(it["id"])
    top = 12.0
    staff_base(s, top)
    k, y = 0, -16.0
    while y < top:   # the vine up the haft, thorns and leaves
        a = k * 1.1
        x, z = math.cos(a) * 1.3, math.sin(a) * 1.3
        bx(s, x, y, z, 0.8, 1.6, 0.8, "blade", tag="vine")
        if k % 4 == 1:
            bx(s, x * 1.9, y + 0.6, z * 1.9, 1.6, 0.6, 1.2, "blade", tag="leaf")
        y += 1.2
        k += 1
    cy = top + 6.0
    for side in (1, -1):   # sepals
        chainp(s, (side * 1.0, top + 0.6), [(2.4, -side * 60, 1.2, 1.2), (2.0, -side * 20, 0.8, 0.8)], "blade")
    for (r, n, sz, h, mat, dy) in ((4.6, 9, 3.0, 3.6, "acc", 0.0), (3.0, 7, 2.6, 3.4, "acc", 1.0), (1.6, 5, 2.0, 3.0, "glow", 2.2),
                                   (0.0, 1, 1.8, 2.4, "white", 3.4)):
        for j in range(n):
            a = 2 * math.pi * j / n + r
            x, z = math.cos(a) * r, math.sin(a) * r
            bx(s, x, cy - 3.0 + dy + (0.6 if j % 2 else 0), z, sz, h, sz * 0.6, mat, glow=mat in ("glow", "white"),
               rots=(("y", -math.degrees(a) + 90), ("x", 18 if r else 0)), pivot=(x, cy - 3.0 + dy, z))
    for (x, y, sz) in ((-6.0, cy - 4.0, 1.0), (5.4, cy - 6.4, 0.8), (-4.0, cy - 9.0, 0.7), (6.4, cy + 1.0, 0.7)):   # falling light
        bx(s, x, y, 0, sz, sz * 0.6, sz, "white", glow=True, rots=(("z", 35),), pivot=(x, y, 0))
    return s


def auroras_vigil(th, it):
    """a crown of tall icicles on a silver ring, a star of ice at its heart, and over it an arch of the aurora: a
    curtain of light hanging in waving strips"""
    s = Sword(it["id"])
    top = 12.0
    staff_base(s, top)
    cy = top + 1.6
    for k in range(12):   # the ice crown
        a = 2 * math.pi * k / 12
        x, z = math.cos(a) * 4.2, math.sin(a) * 4.2
        h = (8.4 if k % 3 == 0 else 4.6 if k % 3 == 1 else 6.2)
        for j, f in enumerate((1.0, 0.62, 0.3)):
            bx(s, x, cy + h * (1 - f) * 0.85, z, 1.8 * f + 0.2, h * f * 0.55 + 0.6, 1.8 * f + 0.2, "blade",
               rots=(("y", -math.degrees(a)),), pivot=(x, cy, z))
    for k in range(12):
        a = 2 * math.pi * k / 12
        bx(s, math.cos(a) * 4.2, cy - 1.0, math.sin(a) * 4.2, 2.6, 1.4, 1.0, "acc", rots=(("y", -math.degrees(a) + 90),),
           pivot=(math.cos(a) * 4.2, cy - 1.0, math.sin(a) * 4.2))
    star4(s, 0, cy + 4.0, 2.6, 0, 1.8)
    ac, R = cy + 6.0, 9.0   # the aurora: strips hanging from an arch, waving
    for k in range(15):
        ang = math.radians(15 + 150 * k / 14)
        x, y = math.cos(ang) * R, ac + math.sin(ang) * R * 0.8
        ln = 3.6 + 1.8 * math.sin(k * 1.3)
        sway = 0.8 * math.sin(k * 0.9)
        seg(s, (x, y), (x + sway, y - ln * 0.5), 1.5, 0.5, "white" if k % 3 == 0 else "glow", -1.2, glow=True)
        seg(s, (x + sway, y - ln * 0.5), (x - sway * 0.5, y - ln), 1.2, 0.5, "glow", -1.2, glow=True)
    return s


def sporemother(th, it):
    """a twisted stalk ending in a cluster of domed caps glowing pink beneath, spores puffing off them and three
    little spore-children hanging from their gills on threads"""
    s = Sword(it["id"])
    top = 12.0
    staff_base(s, top)
    for k in range(8):   # the stalk twisting up into the cluster
        bx(s, 0.4 * math.sin(k), top + k * 1.0, 0, 2.2, 1.05, 2.2, "wood", rots=(("y", k * 20),), pivot=(0, top + k, 0))
    for (x, y, r, z) in ((0.0, top + 8.0, 4.4, 0.0), (-4.6, top + 4.6, 2.8, 0.6), (4.4, top + 5.4, 3.0, -0.4), (-2.2, top + 12.4, 2.2, 0.0),
                         (2.8, top + 11.2, 1.8, 0.4)):
        seg(s, (x * 0.3, y - 3.2), (x, y), 1.0, 1.0, "wood")
        bx(s, x, y - 0.5, z, r * 2.0, 0.6, r * 2.0, "glow", glow=True, tag="gills")
        for k, f in enumerate((1.0, 0.86, 0.62, 0.34)):   # the dome
            bx(s, x, y + k * r * 0.26, z, r * 2.0 * f + 0.1, r * 0.27, r * 2.0 * f + 0.1, "blade", tag="cap")
        for j in range(3):   # spots
            a = j * 2.1 + x
            bx(s, x + math.cos(a) * r * 0.5, y + r * 0.5, z + math.sin(a) * r * 0.5, r * 0.3, r * 0.3, r * 0.3, "acc")
    for (x, ln) in ((-4.6, 3.6), (4.4, 4.6), (-0.4, 5.6)):   # the spore-children on their threads
        yb = top + (4.6 if x < -1 else 5.4 if x > 1 else 8.0) - 0.6
        bx(s, x, yb - ln, 0, 0.3, ln, 0.3, "glow", glow=True, tag="thread")
        bx(s, x, yb - ln - 1.6, 0, 1.2, 1.6, 1.0, "acc", tag="child")
        bx(s, x, yb - ln - 0.6, 0, 2.0, 0.8, 2.0, "blade")
        bx(s, x, yb - ln - 1.0, 0.55, 0.8, 0.3, 0.2, "glow", glow=True)
    for (x, y, sz) in ((-6.0, top + 9.0, 0.8), (6.4, top + 9.8, 0.7), (-0.8, top + 16.6, 0.9), (3.8, top + 15.0, 0.6),
                       (-4.6, top + 14.6, 0.6)):   # spores
        bx(s, x, y, 0, sz, sz, sz, "glow", glow=True)
    return s


def bone_gate(th, it):
    """a pointed arch of bones on a staff: vertebrae columns, a rib arch, a skull for its keystone, the void of the
    dead inside it and skeletal hands reaching out"""
    s = Sword(it["id"])
    top = 12.0
    staff_base(s, top)
    bx(s, 0, top - 0.6, 0, 9.6, 1.6, 3.2, "blade", tag="sill")
    for side in (1, -1):   # vertebra columns
        for k in range(6):
            bx(s, side * 4.0, top + 1.0 + k * 1.5, 0, 2.2, 1.1, 2.4, "blade", tag="vertebra")
            seg(s, (side * 4.6, top + 1.5 + k * 1.5), (side * 5.8, top + 1.0 + k * 1.5), 0.6, 0.8, "blade")
    cy = top + 10.0
    for side in (1, -1):   # the pointed arch, two ribs meeting
        pts = [(side * 4.0, cy), (side * 3.8, cy + 2.4), (side * 3.0, cy + 4.6), (side * 1.6, cy + 6.4), (0, cy + 7.6)]
        for p, q in zip(pts, pts[1:]):
            seg(s, p, q, 1.8, 2.2, "blade")
    disc(s, 0, top + 1.0 + (cy + 6.0 - top - 1.0) / 2 - 1.0, 3.0, -0.2, 0.6, "glow")
    for k in range(5):   # the void in the arch
        y = top + 1.0 + k * 3.0
        w = 6.0 if y < cy else 6.0 * (1 - (y - cy) / 7.6)
        bx(s, 0, y, -0.2, max(1.0, w), 3.1, 0.8, "glow", glow=True, tag="void")
    bx(s, 0, top + 1.0, 0.25, 4.0, 12.0, 0.2, "void")
    emblem("skull", s, 0, cy + 9.8, 3.6, 3.4)
    for (x, y, ang) in ((-1.4, top + 6.0, 20), (1.8, top + 8.4, -25), (0.2, top + 3.0, 5)):   # hands reaching out
        hx, hy = x, y
        bx(s, hx, hy, 0.8, 1.4, 1.2, 1.8, "acc", tag="palm")
        for j, fa in enumerate((-25, -8, 8, 25)):
            chainp(s, (hx - 0.45 + j * 0.3, hy + 1.0), [(1.2, ang + fa, 0.35, 0.4), (0.8, ang + fa - 25, 0.3, 0.35)], "acc", z=1.2)
        seg(s, (hx, hy), (hx * 0.6, hy - 2.0), 0.6, 0.6, "acc", z=0.6)
    return s


HERO2 = {f.__name__: f for f in (thornheart, chainsworn, mantis_talon, void_splinter, rockgrinder, legions_pillar,
                                 wardens_bardiche, tidecallers_trident, chimera_jaw, kingsbarrow, brood_carapace,
                                 gryphon_aegis, kraken_bow, khans_horn, alembic_of_ruin, riftcaller, everbloom,
                                 auroras_vigil, sporemother, bone_gate)}
