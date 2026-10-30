"""The world's epic and legendary weapons, built by hand: each its own silhouette, not a type template dressed up.
worldarms.py builds these instead of weaponforge's template when the id is in HERO. Same space as the templates:
px, the hand at the origin, the blade up +y, its faces in the x-y plane (shields: face toward +z; bows: Kiln space).
"""
import math
import os
import sys

sys.path.insert(0, 'E:/Ashbound/tools')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import weaponforge as W  # noqa: E402
from voxsword import Sword, C  # noqa: E402
from weaponforge import bx, ring_xy, seg, chainp  # noqa: E402


# ---------------------------------------------------------------- shared parts

def sblade(s, y0, y1, left, right, thick, mat="blade", step=1.2, spine=True, cx=None, edge=None, back=None):
    """a blade whose two edges are drawn separately: left(t)/right(t) = how far each edge stands off the centre
    line cx(t). edge/back = a material run along the right/left edge (a honed or burning edge)."""
    y = y0
    while y < y1 - 0.05:
        h = min(step, y1 - y)
        t = (y + h / 2 - y0) / max(0.01, y1 - y0)
        c = cx(t) if cx else 0.0
        l, r = max(0.15, left(t)), max(0.15, right(t))
        w = l + r
        s.add(C(c + (r - l) / 2, y, 0, w, h + 0.02, thick), mat, tag="blade")
        if spine and w > 1.8:
            s.add(C(c, y, 0, max(0.5, w * 0.2), h + 0.02, thick + 0.3), "dark", tag="spine")
        for side, m in ((1, edge), (-1, back)):
            if m and (r if side > 0 else l) > 0.4:
                s.add(C(c + side * ((r if side > 0 else l) + 0.15), y, 0, 0.55, h + 0.02, thick * 0.55), m,
                      group="fire" if m in ("glow", "white") else "lit")
        y += h


def zig(s, pts, w, d, mat="glow", z=0.0):
    for a, b in zip(pts, pts[1:]):
        seg(s, a, b, w, d, mat, z, glow=mat in ("glow", "white"))


def disc(s, cx, cy, r, z, depth, mat, step=0.8):
    """a round plate in the blade plane, in rows"""
    y = cy - r
    while y < cy + r - 0.05:
        yy = y + step / 2 - cy
        w = 2 * math.sqrt(max(0.0, r * r - yy * yy))
        if w > 0.3:
            bx(s, cx, y, z, w, step + 0.02, depth, mat, glow=mat in ("glow", "white"))
        y += step


def star4(s, cx, cy, r, z, depth, mat="white"):
    """a four-pointed star"""
    for ang in (0, 90):
        for k, f in enumerate((1.0, 0.55)):
            bx(s, cx, cy - r * f, z, r * 0.42 * (1 - 0.4 * k) if ang == 0 else 2 * r * f, (2 * r * f) if ang == 0 else r * 0.42 * (1 - 0.4 * k),
               depth, mat, glow=True)
    bx(s, cx, cy - r * 0.32, z, r * 0.64, r * 0.64, depth + 0.2, mat, glow=True)


def grip(s, y, ln, w, mat="wrap"):
    bx(s, 0, y - ln, 0, w, ln, w, mat, tag="grip")
    for k in range(int(ln / 1.6)):
        bx(s, 0, y - ln + 0.6 + k * 1.6, 0, w + 0.3, 0.5, w + 0.3, "dark", tag="wrap_band")


def haft(s, y0, y1, w=2.0, mat="wood"):
    bx(s, 0, y0, 0, w, y1 - y0, w, mat, tag="haft")


def emblem(name, s, cx, y, size, z):
    import worldarms as WA
    WA.EMBLEMS[name](s, cx, y, size, z)


def shield_rows(s, rows, F, face, rim=True):
    for (y0, y1, w) in rows:
        bx(s, 0, y0, 1.4, w, y1 - y0 + 0.02, F - 0.4, face, tag="plate")
        if rim:
            for side in (1, -1):
                bx(s, side * (w / 2 - 0.6), y0, 1.6, 1.4, y1 - y0 + 0.02, F + 0.4, "dark", tag="rim")
    top = rows[-1]
    if rim:
        bx(s, 0, top[1] - 0.8, 1.6, top[2], 1.4, F + 0.4, "dark", tag="rim")


def shield_handle(s):
    bx(s, 0, -3.0, -5.0, 2.0, 6.0, 1.2, "wrap", tag="handle")
    for y0 in (-3.0, 2.0):
        bx(s, 0, y0, -2.0, 2.0, 1.0, 6.0, "dark", tag="handle_arm")


def staff_base(s, top=12.0, w=2.0):
    haft(s, -18.0, top, w)
    grip(s, 4.0, 8.0, w + 0.4)
    bx(s, 0, -19.8, 0, w + 0.6, 2.0, w + 0.6, "dark", tag="shoe")
    chainp(s, (0, -19.8), [(1.6, 180, 1.4, 1.4), (1.0, 180, 0.7, 0.7)], "dark")
    for y in (-12.0, 5.0):
        bx(s, 0, y, 0, w + 0.6, 1.0, w + 0.6, "dark", tag="band")


# ---------------------------------------------------------------- swords

def emberwake(th, it):
    """a black falchion, its belly widening to a clipped point; molten cracks through it, a burning edge, horns
    curling down off the guard and flame licking up the blade's root"""
    s = Sword(it["id"])
    y0, L = 4.4, 22.0
    bx(s, 0, y0 - 0.6, 0, 3.6, 1.8, 1.8, "dark", tag="ricasso")
    sblade(s, y0 + 1.2, y0 + L, lambda t: 2.0 - 0.5 * t, lambda t: 2.0 + 2.0 * t, 1.3, edge="glow")
    sblade(s, y0 + L, y0 + L + 5.0, lambda t: 1.5 * (1 - t) + 0.1, lambda t: 4.0 * (1 - t) ** 0.7 + 0.1, 1.2,
           cx=lambda t: -0.2 * t, edge="glow", spine=False)
    for k, yy in enumerate((y0 + 13, y0 + 17, y0 + 21)):   # hooked teeth on the back
        seg(s, (-1.8, yy), (-3.2, yy + 1.4 + 0.3 * k), 0.9, 1.1, "blade")
    for z in (0.75, -0.75):   # cracks, both faces
        zig(s, [(0.0, y0 + 2.5), (1.6, y0 + 5.0), (0.4, y0 + 7.5), (2.6, y0 + 10.0), (1.2, y0 + 12.5), (3.4, y0 + 15.5),
                (1.8, y0 + 18.0), (3.6, y0 + 21.5)], 0.55, 0.2, z=z)
        zig(s, [(1.6, y0 + 5.0), (3.4, y0 + 6.2)], 0.45, 0.2, z=z)
        zig(s, [(1.2, y0 + 12.5), (-0.8, y0 + 14.0)], 0.45, 0.2, z=z)
        zig(s, [(1.8, y0 + 18.0), (0.0, y0 + 20.4), (0.6, y0 + 23.6)], 0.45, 0.2, z=z)
    for side in (1, -1):   # flame licking up from the guard
        for k, (x, h) in enumerate(((1.0, 4.8), (2.2, 3.4), (3.2, 2.2))):
            seg(s, (side * x * 0.6, y0 + 0.4), (side * x, y0 + 0.4 + h), 1.0 - 0.15 * k, 1.9, "glow", glow=True)
    bx(s, 0, 2.0, 0, 9.0, 2.0, 2.6, "dark", tag="guard")
    for side in (1, -1):
        chainp(s, (side * 4.2, 2.6), [(2.6, -side * 95, 1.6, 2.0), (2.2, -side * 140, 1.3, 1.6), (1.6, -side * 175, 1.0, 1.2),
                                      (1.0, side * 150, 0.7, 0.8)], "dark")
    emblem("skull", s, 0, 3.6, 4.8, 3.4)
    grip(s, 2.0, 6.8, 2.0)
    bx(s, 0, -7.0, 0, 3.0, 2.2, 3.0, "dark", tag="pommel")
    bx(s, 0, -6.6, 0, 1.8, 1.4, 3.3, "glow", glow=True)
    for side in (1, -1):
        seg(s, (side * 1.2, -6.0), (side * 2.6, -8.4), 0.8, 0.9, "dark")
    return s


def starfall(th, it):
    """a long night-blue blade split by a window where a star burns, held between the rails; a crescent cups the
    guard, starlight down both edges"""
    s = Sword(it["id"])
    y0 = 4.4
    a, b, c, L = y0 + 1.2, y0 + 13.0, y0 + 21.5, 26.0
    bx(s, 0, y0 - 0.6, 0, 3.6, 1.8, 1.8, "dark", tag="ricasso")
    w = lambda t: 2.4 - 0.5 * t
    sblade(s, a, b, w, w, 1.3, edge="white", back="white")
    for side in (1, -1):   # the rails round the window
        sblade(s, b, c, lambda t: 0.75, lambda t: 0.75, 1.3, cx=(lambda sd: lambda t: sd * 1.55)(side), spine=False,
               edge="white" if side > 0 else None, back="white" if side < 0 else None)
    sblade(s, c, y0 + L, lambda t: 2.2 - 0.4 * t, lambda t: 2.2 - 0.4 * t, 1.3, edge="white", back="white")
    W.tip(s, 0, y0 + L, 3.6, 1.3, n=3)
    star4(s, 0, (b + c) / 2, 2.6, 0, 1.6)
    bx(s, 0, b - 0.2, 0, 0.6, c - b + 0.4, 0.6, "white", glow=True)
    for (fx, fy, sz) in ((0.8, a + 2, 0.7), (-0.9, a + 4.4, 0.5), (0.3, a + 7.0, 0.8), (-0.6, a + 9.6, 0.55), (0.0, c + 2.2, 0.6)):
        for z in (0.7, -0.7):
            bx(s, fx, fy, z, sz, sz, 0.2, "white", glow=True)
    n = 11   # the crescent guard, its horns rising either side of the blade
    pts = []
    for k in range(n):
        ang = math.radians(195 + 150 * k / (n - 1))
        pts.append((math.cos(ang) * 6.4, 7.0 + math.sin(ang) * 6.0))
    for k, (p, q) in enumerate(zip(pts, pts[1:])):
        f = math.sin(math.pi * (k + 0.5) / (n - 1))
        seg(s, p, q, 0.6 + 1.6 * f, 2.2, "acc")
    disc(s, 0, 2.6, 1.7, 0, 2.8, "glow")
    grip(s, 1.2, 6.6, 2.0)
    star4(s, 0, -7.4, 2.0, 0, 1.4, "acc")
    bx(s, 0, -7.9, 0, 1.0, 1.0, 1.9, "white", glow=True)
    return s


# ---------------------------------------------------------------- daggers

def shadowfang(th, it):
    """a fang: wide at the root, hooking forward to a point, a saw on its back; batwing guard round a void eye"""
    s = Sword(it["id"])
    y0, L = 3.0, 13.0
    cx = lambda t: 3.0 * t * t
    sblade(s, y0, y0 + L, lambda t: 2.4 * (1 - t) + 0.3, lambda t: 2.2 * (1 - t) ** 1.3 + 0.3, 1.2, cx=cx, edge="glow", step=1.0)
    chainp(s, (cx(1), y0 + L), [(1.6, -40, 0.7, 1.0), (1.0, -70, 0.5, 0.8)], "blade")
    for k in range(5):   # the saw
        t = 0.1 + 0.16 * k
        yy = y0 + t * L
        x = cx(t) - (2.4 * (1 - t) + 0.3)
        seg(s, (x + 0.2, yy), (x - 1.2, yy + 1.0), 0.8, 1.0, "blade")
    for z in (0.7, -0.7):
        for k in range(4):
            t = 0.15 + 0.18 * k
            bx(s, cx(t) - 0.2, y0 + t * L, z, 0.5 if k % 2 else 0.9, 0.9, 0.2, "glow", glow=True)
    bx(s, 0, 0.6, 0, 5.0, 1.8, 2.2, "dark", tag="guard")
    for side in (1, -1):   # bat wings
        tip = chainp(s, (side * 2.2, 1.4), [(2.6, -side * 60, 1.2, 1.4), (2.2, -side * 30, 0.9, 1.2), (1.4, -side * 5, 0.6, 1.0)], "acc")
        chainp(s, (side * 3.6, 1.6), [(1.6, -side * 120, 0.7, 1.0)], "acc")
        chainp(s, (tip[0] - side * 0.3, tip[1] - 0.2), [(1.6, -side * 150, 0.6, 0.9)], "acc")
    emblem("eye", s, 0, 2.6, 3.6, 2.8)
    grip(s, 0.6, 4.8, 1.9)
    bx(s, 0, -5.4, 0, 2.2, 1.2, 2.2, "dark", tag="pommel")
    chainp(s, (0, -5.4), [(1.6, 180, 1.0, 1.0), (1.0, 180, 0.5, 0.5)], "dark")
    bx(s, 0, -5.2, 0, 0.8, 0.8, 2.5, "glow", glow=True)
    return s


def bloodmoon_kris(th, it):
    """a waved crimson kris rising out of a blood-red moon; blood running down the waves"""
    s = Sword(it["id"])
    y0, L = 3.6, 14.0
    cx = lambda t: 1.0 * math.sin(t * 13)
    sblade(s, y0, y0 + L, lambda t: 1.8 * (1 - 0.5 * t), lambda t: 1.8 * (1 - 0.5 * t), 1.1, cx=cx, step=0.9,
           edge="glow", back="glow")
    W.tip(s, cx(1), y0 + L, 1.6, 1.0, n=2, step=1.0)
    bx(s, -0.6, y0 - 0.2, 0, 2.2, 2.4, 1.5, "dark", tag="ganja")
    disc(s, 0, 4.6, 4.6, -1.1, 0.7, "glow")   # the moon behind the blade
    ring_xy(s, 0, 4.6, 4.7, 0.8, "acc", depth=1.2, z=-1.1)
    for k, (x, ln) in enumerate(((-2.6, 2.4), (-1.0, 3.4), (1.4, 2.8), (3.0, 1.8))):   # blood dripping off it
        bx(s, x, 0.4 - ln, -1.1, 0.6, ln, 0.6, "glow", glow=True)
        bx(s, x, 0.4 - ln - 0.6, -1.1, 0.8, 0.7, 0.7, "glow", glow=True)
    bx(s, 0, 0.6, 0, 4.4, 1.6, 2.0, "acc", tag="guard")
    grip(s, 0.6, 4.8, 1.9, "wood")
    n = 7   # a gold crescent for a pommel
    for k in range(n):
        ang = math.radians(200 + 140 * k / (n - 1))
        p = (math.cos(ang) * 2.4, -5.0 + math.sin(ang) * 2.0)
        bx(s, p[0], p[1] - 0.4, 0, 0.9, 0.9, 1.6, "acc")
    bx(s, 0, -5.4, 0, 1.0, 1.0, 2.0, "glow", glow=True)
    return s


# ---------------------------------------------------------------- hammers

def thunderhead(th, it):
    """the head a storm cloud of iron, bolts crawling out of its belly; a storm eye in its brow"""
    s = Sword(it["id"])
    haft(s, -12.0, 13.0, 2.0)
    grip(s, 1.0, 7.0, 2.4)
    bx(s, 0, -13.6, 0, 3.0, 2.0, 3.0, "dark", tag="pommel")
    for y in (4.0, 8.0, 11.0):
        bx(s, 0, y, 0, 2.6, 0.8, 2.6, "acc", tag="band")
    cy = 15.0
    for (x, y, w, h, d) in ((0, cy, 11.0, 6.0, 7.0), (-4.6, cy - 0.6, 5.2, 5.2, 6.0), (4.8, cy - 0.4, 5.0, 5.0, 6.0),
                            (-2.2, cy + 3.6, 6.0, 5.0, 6.4), (2.6, cy + 3.2, 5.4, 4.8, 6.0), (0.2, cy + 6.4, 4.2, 3.4, 5.0),
                            (-6.4, cy + 2.4, 3.2, 3.2, 4.2), (6.8, cy + 2.2, 3.0, 3.0, 4.0)):
        bx(s, x, y, 0, w, h, d, "blade", tag="cloud")
    bx(s, 0, cy - 1.0, 0, 13.4, 1.4, 6.0, "dark", tag="belly")
    for side in (1, -1):
        zig(s, [(side * 5.0, cy - 1.0), (side * 6.6, cy - 3.6), (side * 5.4, cy - 4.4), (side * 7.4, cy - 7.6),
                (side * 6.2, cy - 8.4), (side * 8.4, cy - 11.6)], 0.8, 0.8)
        zig(s, [(side * 6.6, cy - 3.6), (side * 8.6, cy - 4.8)], 0.5, 0.6)
    for z in (1, -1):
        zig(s, [(-3.0, cy + 2.0), (-1.2, cy + 4.2), (0.8, cy + 2.6), (2.8, cy + 4.8)], 0.5, 0.2, z=z * 3.6)
    emblem("eye", s, 0, cy + 3.2, 4.0, 7.6)
    chainp(s, (0, cy + 9.6), [(2.0, 0, 1.6, 1.6), (1.4, 0, 0.8, 0.8)], "acc")
    return s


def worldbreaker(th, it):
    """a mountain of obsidian: a flat striking face on one side, a curved pick on the other, magma in its veins,
    a crown of spikes on top"""
    s = Sword(it["id"])
    haft(s, -14.0, 14.0, 2.4)
    grip(s, 0.0, 8.0, 2.8)
    chainp(s, (0, -14.0), [(2.4, 180, 2.6, 2.6), (1.6, 180, 1.4, 1.4)], "dark")
    for y in (2.0, 6.0, 10.0):
        bx(s, 0, y, 0, 3.0, 1.0, 3.0, "acc", tag="band")
    cy, H, D = 17.5, 10.0, 9.0
    bx(s, 0, cy - H / 2, 0, 10.0, H, D, "blade", tag="head")
    bx(s, 0, cy - H / 2 - 0.6, 0, 4.0, H + 1.2, D + 1.0, "dark", tag="eye")
    bx(s, 5.6, cy - H / 2 + 0.5, 0, 1.6, H - 1.0, D - 1.0, "blade", tag="face")
    bx(s, 6.6, cy - H / 2 + 1.5, 0, 0.8, H - 3.0, D - 3.0, "glow", glow=True, tag="face_glow")
    chainp(s, (-4.8, cy + 1.0), [(4.0, 80, 3.6, 3.6), (3.6, 100, 2.8, 2.8), (3.0, 125, 2.0, 2.0), (2.4, 150, 1.2, 1.2),
                                 (1.2, 170, 0.6, 0.6)], "blade")
    for z in (D / 2 + 0.1, -D / 2 - 0.1):   # magma veins, both faces
        zig(s, [(-4.6, cy - 3.0), (-2.0, cy - 1.0), (-2.8, cy + 1.6), (0.4, cy + 3.4), (3.0, cy + 1.4), (4.6, cy + 3.8)], 0.7, 0.3, z=z)
        zig(s, [(-2.0, cy - 1.0), (1.2, cy - 3.4), (4.2, cy - 2.0)], 0.55, 0.3, z=z)
        zig(s, [(0.4, cy + 3.4), (0.0, cy + 4.9)], 0.5, 0.3, z=z)
    bx(s, 0, cy + H / 2 - 0.2, 0, 11.0, 1.4, D + 1.0, "acc", tag="crown")
    for x, h in ((-4.0, 2.4), (-2.0, 3.4), (0.0, 4.4), (2.0, 3.4), (4.0, 2.4)):
        chainp(s, (x, cy + H / 2 + 1.2), [(h * 0.6, 0, 1.4, 1.4), (h * 0.4, 0, 0.7, 0.7)], "acc")
    bx(s, 0, cy - H / 2 - 1.4, 0, 6.0, 1.0, 6.0, "acc", tag="band")
    return s


# ---------------------------------------------------------------- spears

def wyrmtongue(th, it):
    """the socket a wyrm's head, a forked tongue for a blade, void fire flickering between the tines"""
    s = Sword(it["id"])
    top = 14.0
    haft(s, -24.0, top, 1.8)
    grip(s, 2.0, 8.0, 2.2)
    bx(s, 0, -25.6, 0, 2.6, 2.0, 2.6, "dark", tag="butt")
    for k in range(6):   # scales up the haft
        bx(s, 0, 4.0 + k * 1.6, 0, 2.4 - 0.05 * k, 0.8, 2.4 - 0.05 * k, "acc", tag="scale")
    bx(s, 0, top, 0, 4.6, 5.0, 4.2, "dark", tag="skull")
    bx(s, 0, top + 5.0, 0, 3.8, 1.8, 3.6, "dark", tag="snout")
    for side in (1, -1):
        chainp(s, (side * 2.0, top + 3.6), [(3.4, side * 130, 1.2, 1.2), (2.4, side * 165, 0.8, 0.9)], "dark")   # horns back
        seg(s, (side * 1.8, top + 5.0), (side * 0.8, top + 2.8), 0.7, 0.8, "acc")   # fangs
        bx(s, side * 1.3, top + 3.0, 2.15, 0.9, 0.9, 0.3, "glow", glow=True)
        bx(s, side * 1.3, top + 3.0, -2.15, 0.9, 0.9, 0.3, "glow", glow=True)
    y = top + 6.8
    sblade(s, y, y + 3.0, lambda t: 2.8, lambda t: 2.8, 1.3)
    for side in (1, -1):
        chainp(s, (side * 1.4, y + 3.0), [(6.0, side * 16, 2.8, 1.3), (5.6, side * 2, 2.3, 1.3), (5.0, -side * 15, 1.7, 1.2),
                                          (3.4, -side * 28, 1.0, 1.0)], "blade")
    zig(s, [(0, y + 2.6), (0.8, y + 6.0), (-0.7, y + 9.4), (0.6, y + 13.0), (-0.3, y + 16.6)], 0.8, 0.8)
    for z in (0.7, -0.7):
        bx(s, 0, y + 0.4, z, 0.7, 2.2, 0.2, "glow", glow=True)
    return s


def heavens_lance(th, it):
    """a long spike of white gold out of a socket with angel wings swept up from it, a halo round the blade"""
    s = Sword(it["id"])
    top = 15.0
    haft(s, -26.0, top, 1.8)
    grip(s, 2.0, 8.0, 2.2)
    bx(s, 0, -27.6, 0, 2.6, 2.0, 2.6, "acc", tag="butt")
    for y in (-18.0, 6.0, 11.0):
        bx(s, 0, y, 0, 2.4, 1.0, 2.4, "acc", tag="band")
    bx(s, 0, top, 0, 3.0, 3.0, 3.0, "acc", tag="socket")
    y = top + 3.0
    sblade(s, y, y + 17.0, lambda t: 1.9 * (1 - 0.65 * t), lambda t: 1.9 * (1 - 0.65 * t), 2.0, spine=False,
           edge="white", back="white")
    W.tip(s, 0, y + 17.0, 1.4, 1.6, n=2)
    bx(s, 0, y + 0.5, 0, 0.8, 14.0, 2.3, "white", glow=True, tag="core")
    for side in (1, -1):   # wings
        for k, (ln, ang) in enumerate(((9.5, 22), (8.6, 38), (7.4, 54), (6.0, 70), (4.6, 88))):
            seg(s, (side * 1.2, top + 1.6 - k * 0.3), (side * (1.2 + ln * math.sin(math.radians(ang))),
                                                       top + 1.6 - k * 0.3 + ln * math.cos(math.radians(ang))),
                1.6 - 0.12 * k, 1.0, "acc" if k % 2 == 0 else "white", glow=k % 2 == 1)
    ring_xy(s, 0, y + 9.0, 4.4, 0.6, "white", glow=True, depth=0.5, z=-1.4)
    for side in (1, -1):   # ribbons off the socket
        chainp(s, (side * 1.2, top + 0.2), [(2.4, side * 170, 0.9, 0.3), (2.0, side * 150, 0.8, 0.3), (1.6, side * 175, 0.7, 0.3)], "wrap")
    return s


# ---------------------------------------------------------------- two-handers

def grave_reaver(th, it):
    """a blade of stacked vertebrae, the dead's green fire showing between the bones; a ribcage for a guard"""
    s = Sword(it["id"])
    y0 = 5.0
    bx(s, 0, y0 + 1.0, 0, 1.4, 27.0, 1.2, "glow", glow=True, tag="marrow")
    y, k = y0 + 1.0, 0
    while y < y0 + 26.0:
        w = 6.6 * (1 - 0.55 * (y - y0) / 27.0)
        bx(s, 0, y, 0, w, 2.0, 1.8, "blade", tag="vertebra")
        bx(s, 0, y + 0.4, 0, w * 0.45, 1.2, 2.2, "acc", tag="process")
        seg(s, (-w / 2 + 0.2, y + 1.2), (-w / 2 - 1.6, y - 0.4), 0.8, 1.2, "blade")   # spurs down the back
        y += 2.7
        k += 1
    W.tip(s, 0, y, 2.2, 1.6, n=3, step=1.4)
    for side in (1, -1):   # ribcage
        for r, (ln, h) in enumerate(((5.0, 1.6), (4.2, 3.0), (3.2, 4.2))):
            chainp(s, (side * 1.6, 2.4 + r * 0.9), [(ln * 0.5, -side * 70, 1.0, 1.4), (ln * 0.5, -side * 20, 0.9, 1.2),
                                                    (h * 0.6, side * 25, 0.7, 1.0)], "acc")
    bx(s, 0, 2.0, 0, 4.0, 2.4, 2.4, "dark", tag="guard")
    emblem("skull", s, 0, 4.0, 5.2, 3.0)
    grip(s, 2.0, 12.4, 2.4)
    bx(s, 0, -13.6, 0, 3.4, 3.0, 3.4, "acc", tag="pommel")
    for side in (1, -1):
        bx(s, side * 0.8, -12.4, 0, 0.8, 0.8, 3.6, "glow", glow=True)
    return s


def dragonspine(th, it):
    """a crimson greatblade with a dragon's dorsal spines raking up its back, a burning edge; the guard a dragon's
    skull biting the blade, a tail for a pommel"""
    s = Sword(it["id"])
    y0, L = 6.0, 29.0
    wfn = lambda t: 3.8 * (1 - 0.3 * t)
    cx = lambda t: 1.0 * t * t
    sblade(s, y0 + 1.0, y0 + L, lambda t: wfn(t) * 0.9, wfn, 1.8, cx=cx, step=1.6, edge="glow")
    W.tip(s, cx(1), y0 + L, 5.0, 1.6, n=3, step=1.6, lean=0.3)
    bx(s, 0.6, y0 + 2.0, 0, 1.2, L - 4.0, 2.1, "glow", glow=True, tag="core")
    k, y = 0, y0 + 2.0
    while y < y0 + L - 2:   # dorsal spines, raking back
        t = (y - y0) / L
        x = cx(t) - wfn(t) * 0.9
        ln = 3.4 - 2.0 * t
        seg(s, (x + 0.4, y), (x - ln * 0.7, y + ln), 1.3 - 0.5 * t, 1.4, "dark")
        y += 3.0
        k += 1
    bx(s, 0, 2.4, 0, 6.0, 4.0, 4.0, "dark", tag="skull")   # the dragon's skull
    bx(s, 0, 6.2, 0, 4.4, 1.4, 3.4, "dark", tag="snout")
    for side in (1, -1):
        chainp(s, (side * 2.6, 5.4), [(3.0, side * 120, 1.6, 1.8), (3.0, side * 150, 1.2, 1.4), (2.0, side * 175, 0.8, 1.0)], "dark")
        chainp(s, (side * 2.2, 6.4), [(2.4, -side * 15, 0.9, 1.4), (1.4, side * 15, 0.6, 1.0)], "acc")   # fangs up the blade
        for z in (2.05, -2.05):
            bx(s, side * 1.5, 4.0, z, 1.2, 0.8, 0.3, "glow", glow=True)
    grip(s, 2.4, 12.4, 2.4)
    chainp(s, (0, -10.0), [(2.4, 175, 2.4, 2.4), (2.4, 150, 1.8, 1.8), (2.0, 120, 1.2, 1.2), (1.4, 95, 0.7, 0.7)], "dark")
    return s


# ---------------------------------------------------------------- shields

def mirror_of_ash(th, it):
    """a black kite with an oval of fire for a face and a dark eye in it, cracks running from it to the rim,
    spikes off its shoulders"""
    s = Sword(it["id"])
    F = 2.2
    rows = [(y, y + 2, 15.0 * (1 if y > 3 else max(0.2, 1 - (3 - y) / 16))) for y in range(-14, 11, 2)]
    shield_rows(s, rows, F, "blade")
    for yy in range(-9, 6):   # the oval of fire
        h = (yy + 2.0) / 7.0
        w = 7.0 * math.sqrt(max(0.0, 1 - h * h))
        if w > 0.5:
            bx(s, 0, yy, 2.3, w, 1.02, 0.6, "glow", glow=True)
    ring_xy(s, 0, -1.6, 4.0, 0.9, "acc", depth=1.0, z=2.7)
    bx(s, 0, -4.4, 2.9, 1.6, 5.4, 0.5, "dark", tag="pupil")
    bx(s, 0, -2.6, 2.9, 3.0, 1.6, 0.5, "dark", tag="pupil")
    for a, b in (((-3.6, 1.6), (-6.4, 6.8)), ((3.6, 1.6), (6.4, 6.8)), ((-3.2, -5.2), (-4.6, -9.6)), ((3.0, -5.2), (2.2, -12.0)),
                 ((0, 3.0), (0.6, 9.4))):
        zig(s, [a, ((a[0] + b[0]) / 2 + 0.8, (a[1] + b[1]) / 2), b], 0.6, 0.4, z=2.6)
    for side in (1, -1):
        chainp(s, (side * 6.6, 10.4), [(2.6, -side * 40, 1.6, 1.6), (1.6, -side * 30, 0.8, 0.8)], "acc", z=1.6)
        chainp(s, (side * 7.2, 6.0), [(2.0, -side * 80, 1.2, 1.2), (1.2, -side * 70, 0.6, 0.6)], "acc", z=1.6)
    chainp(s, (0, -14.0), [(2.2, 180, 1.4, 1.4), (1.2, 180, 0.6, 0.6)], "acc", z=1.6)
    shield_handle(s)
    return s


def aegis_of_dawn(th, it):
    """a tower of white gold with the sun rising over its top edge: rays standing out past the rim"""
    s = Sword(it["id"])
    F = 2.4
    rows = [(y, y + 2, 15.0) for y in range(-14, 10, 2)]
    shield_rows(s, rows, F, "blade")
    for y in (-10.0, -4.0):
        bx(s, 0, y, 2.7, 15.0, 1.0, 0.6, "acc", tag="strap")
    for k in range(11):   # rays: the sun is half risen over the top edge
        ang = math.radians(-75 + 15 * k)
        ln = 9.5 if k % 2 == 0 else 6.5
        a = (math.sin(ang) * 4.6, 6.0 + math.cos(ang) * 4.6)
        b = (math.sin(ang) * (4.6 + ln), 6.0 + math.cos(ang) * (4.6 + ln))
        seg(s, a, b, 1.6 if k % 2 == 0 else 1.1, 1.4, "acc", z=2.2)
        seg(s, a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), 0.6, 0.4, "white", z=3.0, glow=True)
    disc(s, 0, 6.0, 4.8, 2.6, 1.2, "white")
    ring_xy(s, 0, 6.0, 4.9, 0.9, "acc", depth=1.6, z=2.8)
    for k, (x, y) in enumerate(((-4.0, -7.0), (4.0, -7.0), (0.0, -1.4))):   # filigree knots
        ring_xy(s, x, y, 1.6, 0.5, "acc", depth=0.6, z=2.8)
        bx(s, x, y - 0.4, 3.0, 0.8, 0.8, 0.4, "white", glow=True)
    shield_handle(s)
    return s


# ---------------------------------------------------------------- bows

def _bow(th, it, pull, arrow, name):
    return W.bow(th, it, 0, True, pull, arrow, name)


def stormstring(th, it, pull=0.0, arrow=False, name=None):
    """lightning for a string, jagged spikes off the back of the limbs, a crystal at the grip"""
    s = _bow(th, it, pull, arrow, name)
    A, U = W.A, W.U
    for sgn in (1, -1):
        for k, t in enumerate((0.35, 0.6, 0.85)):
            p = W.bow_at(sgn * t, pull)
            q = (p[0] + A[0] * 2.4 + U[0] * sgn * 1.4, p[1] + A[1] * 2.4 + U[1] * sgn * 1.4)
            seg(s, p, q, 0.9 - 0.15 * k, 1.2, "acc", W.BZ)
        tip = W.bow_at(sgn * 1.0, pull)
        seg(s, tip, (tip[0] + U[0] * sgn * 2.2 + A[0] * 0.6, tip[1] + U[1] * sgn * 2.2 + A[1] * 0.6), 0.8, 1.0, "acc", W.BZ)
    t0, t1 = W.bow_at(-1, pull), W.bow_at(1, pull)
    if pull:   # drawn, the string is at the nock: the bolt goes with it (the template's string)
        t1 = t0
    pts = []
    for k in range(9):   # the bolt beside the string
        f = k / 8
        off = (0.7 if k % 2 else -0.7) if 0 < k < 8 else 0
        pts.append((t0[0] + (t1[0] - t0[0]) * f - A[0] * off, t0[1] + (t1[1] - t0[1]) * f - A[1] * off))
    zig(s, pts, 0.45, 0.5, z=W.BZ)
    g = W.bow_at(0.0, pull)
    emblem("crystal", s, g[0] + A[0] * 2.2, g[1] + A[1] * 2.2 + 0.6, 2.6, W.BZ * 0 + 2.0)
    return s


def phoenix_wing(th, it, pull=0.0, arrow=False, name=None):
    """a burning wing bent into a bow: feathers fanning off the back of both limbs, flames at the tips"""
    s = _bow(th, it, pull, arrow, name)
    A, U = W.A, W.U
    for sgn in (1, -1):
        for k in range(7):
            t = 0.2 + 0.11 * k
            p = W.bow_at(sgn * t, pull)
            ln = 2.4 + 2.2 * math.sin(t * math.pi)
            q = (p[0] + A[0] * ln + U[0] * sgn * ln * 0.55, p[1] + A[1] * ln + U[1] * sgn * ln * 0.55)
            seg(s, p, q, 1.1, 0.8, "glow" if k % 2 else "acc", W.BZ, glow=bool(k % 2))
        tip = W.bow_at(sgn * 1.0, pull)
        for j, ln in enumerate((2.6, 1.8)):
            seg(s, tip, (tip[0] + U[0] * sgn * ln + A[0] * (j - 0.5), tip[1] + U[1] * sgn * ln + A[1] * (j - 0.5)), 0.7, 0.8,
                "glow", W.BZ, glow=True)
    g = W.bow_at(0.0, pull)
    emblem("gem", s, g[0] + A[0] * 1.8, g[1] + A[1] * 1.8, 2.8, 2.6)
    return s


# ---------------------------------------------------------------- staffs

def void_eye_staff(th, it):
    """a great void eye held in a cage of curling black claws; smaller eyes open down the haft"""
    s = Sword(it["id"])
    top = 12.0
    staff_base(s, top)
    bx(s, 0, top - 1.0, 0, 3.6, 2.2, 3.6, "dark", tag="collar")
    oy = top + 5.0
    for (w, h) in ((6.4, 4.0), (5.0, 6.4), (3.4, 7.6)):
        bx(s, 0, oy - h / 2, 0, w, h, w, "glow", glow=True, tag="orb")
    for z in (3.25, -3.25):
        bx(s, 0, oy - 2.2, z, 1.2, 4.4, 0.3, "dark", tag="pupil")
    ring_xy(s, 0, oy, 3.6, 0.7, "acc", depth=1.2)
    for side in (1, -1):
        for j, lean in enumerate((50, 20)):
            chainp(s, (side * (1.4 + j * 0.6), top + 1.0), [(3.2, side * lean, 1.2, 1.4), (3.0, -side * 15, 1.0, 1.2),
                                                            (2.6, -side * 55, 0.8, 1.0), (1.4, -side * 95, 0.6, 0.8)], "dark")
    chainp(s, (0, oy + 3.8), [(2.0, 0, 1.0, 1.0), (1.4, 25, 0.6, 0.6)], "dark")
    for y in (-8.0, 0.0, 8.0):   # eyes down the haft
        for z in (1.15, -1.15):
            bx(s, 0, y, z, 1.4, 0.9, 0.3, "acc")
            bx(s, 0, y + 0.15, z * 1.08, 0.6, 0.6, 0.3, "glow", glow=True)
    return s


def last_star(th, it):
    """a great crescent moon on a night-blue haft, the last star burning inside its curve"""
    s = Sword(it["id"])
    top = 12.0
    staff_base(s, top)
    cy, R = top + 7.6, 6.6
    n = 15
    pts = [(math.cos(math.radians(150 + 240 * k / (n - 1))) * R, cy + math.sin(math.radians(150 + 240 * k / (n - 1))) * R)
           for k in range(n)]
    for k, (p, q) in enumerate(zip(pts, pts[1:])):
        f = math.sin(math.pi * (k + 0.5) / (n - 1))
        seg(s, p, q, 0.7 + 2.4 * f, 2.0, "acc")
        if k % 3 == 1:
            seg(s, p, q, 0.5, 2.3, "white", glow=True)
    bx(s, 0, top - 0.5, 0, 0.9, cy - top - R + 1.5, 0.9, "dark")
    bx(s, 0, top, 0, 3.0, 1.6, 3.0, "dark", tag="collar")
    bx(s, 0, cy - R - 0.4, 0, 0.8, R - 1.0, 0.8, "dark", tag="spike")
    star4(s, 0, cy + 0.8, 3.0, 0, 1.8)
    for (x, y) in ((-6.0, cy + 6.0), (5.4, cy + 6.4), (-3.4, cy - 2.6), (3.0, cy - 3.0)):
        bx(s, x, y, 0, 0.8, 0.8, 0.8, "white", glow=True)
    return s


def seraph_staff(th, it):
    """a holy flame in a gold cup between two great angel wings, a halo over it"""
    s = Sword(it["id"])
    top = 12.0
    staff_base(s, top)
    bx(s, 0, top, 0, 3.4, 1.2, 3.4, "acc")
    bx(s, 0, top + 1.2, 0, 4.4, 1.4, 4.4, "acc", tag="cup")
    for k, w in enumerate((3.4, 3.0, 2.4, 1.8, 1.2, 0.7)):   # the flame
        bx(s, 0.2 * math.sin(k), top + 2.6 + k * 1.2, 0, w, 1.22, w, "white", glow=True)
    for side in (1, -1):
        for k, (ln, ang) in enumerate(((10.0, 18), (9.2, 32), (8.2, 46), (7.0, 60), (5.6, 76), (4.2, 94))):
            a = (side * 2.0, top + 2.4 - k * 0.5)
            seg(s, a, (a[0] + side * ln * math.sin(math.radians(ang)), a[1] + ln * math.cos(math.radians(ang))),
                1.5 - 0.1 * k, 0.9, "acc" if k % 2 == 0 else "white", glow=k % 2 == 1)
    ring_xy(s, 0, top + 13.2, 2.6, 0.6, "white", glow=True, depth=0.6)
    bx(s, 0, top + 9.6, 0, 0.5, 1.4, 0.5, "acc")
    return s


def sunspire(th, it):
    """a gold obelisk spire carrying the noon sun: a rayed ring round it, a burning gem at its point"""
    s = Sword(it["id"])
    top = 12.0
    staff_base(s, top, 2.2)
    for k, w in enumerate((4.4, 4.0, 3.6, 3.2, 2.8, 2.4, 2.0, 1.6, 1.2)):
        bx(s, 0, top + k * 1.8, 0, w, 1.82, w, "acc", tag="spire")
        if k % 2 == 0:
            bx(s, 0, top + k * 1.8 + 0.6, 0, w + 0.3, 0.5, w + 0.3, "white", glow=True)
    star4(s, 0, top + 18.0, 2.2, 0, 1.6)
    cy = top + 7.0
    ring_xy(s, 0, cy, 5.6, 1.0, "acc", depth=1.6)
    ring_xy(s, 0, cy, 4.4, 0.5, "white", glow=True, depth=1.0)
    for k in range(12):
        ang = math.radians(k * 30 + 15)
        ln = 3.2 if k % 2 == 0 else 2.0
        seg(s, (math.cos(ang) * 6.0, cy + math.sin(ang) * 6.0), (math.cos(ang) * (6.0 + ln), cy + math.sin(ang) * (6.0 + ln)),
            1.0 if k % 2 == 0 else 0.7, 1.0, "acc")
    for side in (1, -1):
        seg(s, (side * 2.0, cy), (side * 4.6, cy), 0.8, 0.8, "acc")
    return s


def lichcaller(th, it):
    """a horned skull with green fire bursting out of its crown, a spine for a haft, little skulls hung on chains"""
    s = Sword(it["id"])
    top = 12.0
    haft(s, -18.0, top, 2.0)
    grip(s, 4.0, 8.0, 2.4)
    y = -16.0
    while y < top - 1:   # vertebrae
        bx(s, 0, y, 0, 2.8, 1.0, 2.8, "acc", tag="vertebra")
        seg(s, (-1.2, y + 0.5), (-2.2, y - 0.4), 0.6, 0.7, "acc")
        y += 2.4 if not (-4.0 < y < 4.0) else 8.0
    sy = top + 1.0
    bx(s, 0, sy, 0, 5.6, 2.6, 5.0, "acc", tag="jaw")
    for x in (-1.8, -0.6, 0.6, 1.8):
        bx(s, x, sy + 2.2, 0, 0.8, 0.9, 5.4, "acc", tag="teeth")
    bx(s, 0, sy + 2.8, 0, 7.4, 6.0, 6.6, "acc", tag="cranium")
    for side in (1, -1):
        for z in (3.35, -3.35):
            bx(s, side * 1.6, sy + 3.8, z, 2.0, 1.6, 0.3, "glow", glow=True)
        chainp(s, (side * 3.6, sy + 5.8), [(3.4, -side * 80, 2.0, 2.0), (3.0, -side * 140, 1.5, 1.5), (2.4, side * 160, 1.0, 1.0),
                                          (1.6, side * 110, 0.6, 0.6)], "dark")
    for k, (x, h) in enumerate(((-2.0, 6.0), (0.2, 8.4), (2.2, 5.4), (-0.8, 4.0), (1.2, 3.6))):
        chainp(s, (x, sy + 8.8), [(h * 0.5, -x * 6, 1.9 - 0.15 * k, 1.9), (h * 0.5, x * 8, 0.9, 0.9)], "glow", glow=True)
    for side, ln in ((1, 3.4), (-1, 5.0)):   # small skulls on chains
        bx(s, side * 2.4, sy + 1.4 - ln, 0, 0.4, ln, 0.4, "dark", tag="chain")
        bx(s, side * 2.4, sy + 1.4 - ln - 1.8, 0, 1.6, 1.8, 1.6, "acc")
        bx(s, side * 2.4, sy + 1.4 - ln - 1.0, 0.82, 0.9, 0.5, 0.2, "glow", glow=True)
    return s


def hollow_kings_crown(th, it):
    """an empty hood with a dead king's crown on it, void eyes burning where his face was, tatters hanging"""
    s = Sword(it["id"])
    top = 12.0
    staff_base(s, top)
    bx(s, 0, top - 1.0, 0, 6.0, 1.4, 3.0, "acc", tag="crossbar")
    hy = top + 0.4
    for k, (w, d) in enumerate(((7.0, 5.6), (7.4, 6.0), (7.0, 6.0), (6.4, 5.6), (5.6, 5.0), (4.4, 4.2))):   # the hood
        bx(s, 0, hy + k * 1.4, -0.3, w, 1.42, d, "wrap", tag="hood")
    bx(s, 0, hy + 1.0, 2.0, 4.2, 4.6, 2.0, "void", tag="face")
    for side in (1, -1):
        bx(s, side * 1.0, hy + 3.4, 3.05, 1.1, 0.7, 0.3, "glow", glow=True)
    for k, (x, ln) in enumerate(((-3.0, 5.0), (-1.6, 3.4), (0.0, 6.0), (1.6, 4.0), (3.0, 5.4))):   # tatters
        bx(s, x, hy - ln, -0.4 - 0.2 * (k % 2), 1.4, ln + 0.2, 0.5, "wrap")
        bx(s, x + 0.3, hy - ln - 0.8, -0.4, 0.7, 0.9, 0.5, "wrap")
    cy = hy + 8.2
    for k in range(10):   # the crown, a ring round the hood's top
        a = 2 * math.pi * k / 10
        x, z = math.cos(a) * 3.0, math.sin(a) * 3.0
        bx(s, x, cy - 0.6, z, 2.2, 2.2, 0.8, "gold", rots=(("y", -math.degrees(a) + 90),), pivot=(x, cy - 0.6, z))
        h = 3.2 if k % 2 == 0 else 2.0
        bx(s, x, cy + 1.6, z, 0.9, h, 0.7, "gold", rots=(("y", -math.degrees(a) + 90),), pivot=(x, cy + 1.6, z))
        if k % 2 == 0:
            bx(s, x * 1.05, cy + 1.6 + h, z * 1.05, 0.9, 0.9, 0.9, "glow", glow=True)
    for k, w in enumerate((3.4, 2.4, 1.4)):
        bx(s, 0, cy + 0.6 + k * 1.4, 0, w, 1.42, w, "glow", glow=True)
    return s


HERO = {f.__name__: f for f in (emberwake, starfall, shadowfang, bloodmoon_kris, thunderhead, worldbreaker, wyrmtongue,
                                heavens_lance, grave_reaver, dragonspine, mirror_of_ash, aegis_of_dawn, stormstring,
                                phoenix_wing, void_eye_staff, last_star, seraph_staff, sunspire, lichcaller,
                                hollow_kings_crown)}


import worldarms_hero2 as _H2  # noqa: E402  (the second forty's)
HERO.update(_H2.HERO2)


def build(th, it, **kw):
    s = HERO[it["id"]](th, it, **kw)
    s.shaders = th.shaders
    return s
