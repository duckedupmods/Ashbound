"""Two of Highmourn's set pieces, sculpted like the statues and made into blocks by tools/sculpt.py:

  - clock_face: the guild belfry's dial, 9 blocks across. A dark frame with gilt bosses, a gilt bezel, a pale chapter
    ring with Roman numerals and a minute track, a starry field round a gilt sun. Its hands (clock_hand_minute,
    clock_hand_hour) are models only, turned by ClockHands' renderer to the world's time.
  - warden_blade: the greatsword driven into the Ash Warden's plinth, its point buried in heaved stone; a dark blade
    with bright edges and a molten fuller, a heavy guard with drooping quillons and an ember set in it, a wrapped grip,
    a caged ember for a pommel.

    blender -b -P tools/blender/civic_sculpt.py -- [NAME ...]        (none = all)     then  python tools/sculpt.py

Game axes in blocks, each prop facing north (its front at z = 0); seen from the front the viewer's right is -x.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import king_sculpt as KS  # noqa: E402
import sculpt_props as SP  # noqa: E402

# ================================================================ the clock

CX, CY = 4.5, 4.5                       # the dial's middle
HAND_PIVOT = (0.5, 0.2)                 # where the hands turn in their own cell (ClockHands renders them 4.5x)


def flat(pts, z0, z1, mat, c=(CX, CY)):
    """A flat shape from points in the viewer's plane (s right, t up, from c), z0..z1 deep."""
    return SP.prism([(c[0] - s, c[1] + t) for s, t in pts], z0, z1, mat)


def stroke(a, b, w, z0, z1, mat, c=(CX, CY)):
    (s0, t0), (s1, t1) = a, b
    L = math.hypot(s1 - s0, t1 - t0) or 1
    ns, nt = -(t1 - t0) / L * w / 2, (s1 - s0) / L * w / 2
    return flat([(s0 + ns, t0 + nt), (s1 + ns, t1 + nt), (s1 - ns, t1 - nt), (s0 - ns, t0 - nt)], z0, z1, mat, c)


def glyphs(text, h, w):
    """Strokes of a Roman numeral, centred on 0, in (s, t)."""
    out, x = [], 0.0
    lw = {"I": w, "V": 0.36 + w, "X": 0.36 + w}
    gap = 0.07
    total = sum(lw[ch] for ch in text) + gap * (len(text) - 1)
    x = -total / 2
    for ch in text:
        m = x + lw[ch] / 2
        if ch == "I":
            out.append(((m, -h / 2), (m, h / 2)))
        elif ch == "V":
            out += [((m - 0.18, h / 2), (m, -h / 2)), ((m + 0.18, h / 2), (m, -h / 2))]
        else:
            out += [((m - 0.18, -h / 2), (m + 0.18, h / 2)), ((m - 0.18, h / 2), (m + 0.18, -h / 2))]
        x += lw[ch] + gap
    out += [((-total / 2 - 0.04, h / 2), (total / 2 + 0.04, h / 2)), ((-total / 2 - 0.04, -h / 2), (total / 2 + 0.04, -h / 2))]
    return out


def on_ring(s, t, r, th):
    """Glyph point (s, t) set at radius r, clock angle th (clockwise from twelve), its top pointing outwards."""
    return (r * math.sin(th) + s * math.cos(th) + t * math.sin(th), r * math.cos(th) - s * math.sin(th) + t * math.cos(th))


@SP.prop("clock_face", 9, 9, 1, V=16)
def clock_face():
    SP.box(0.05, 0.05, 0.55, 8.95, 8.95, 1.0, "stone_dark", bevel=0.12)                  # the frame
    for x0, x1, y0, y1 in ((0.15, 8.85, 0.15, 0.42), (0.15, 8.85, 8.58, 8.85), (0.15, 0.42, 0.15, 8.85), (8.58, 8.85, 0.15, 8.85)):
        SP.box(x0, y0, 0.42, x1, y1, 0.62, "gold", bevel=0.05)
    for sx in (-1, 1):                                                                      # the spandrels' bosses
        for sy in (-1, 1):
            SP.ellip((CX + sx * 3.75, CY + sy * 3.75, 0.5), (0.42, 0.42, 0.18), "gold", seg=16)
            for a in range(4):
                th = math.pi / 4 + a * math.pi / 2
                SP.ellip((CX + sx * 3.75 + 0.5 * math.cos(th), CY + sy * 3.75 + 0.5 * math.sin(th), 0.52), (0.16, 0.16, 0.08), "brass_dark", seg=10)
    SP.cyl((CX, CY, 1.0), (CX, CY, 0.42), 4.05, "marble", seg=96)                          # the chapter ring
    SP.cut(SP.cyl((CX, CY, 0.47), (CX, CY, 0.3), 2.45, "x", seg=72))
    SP.cyl((CX, CY, 1.0), (CX, CY, 0.47), 2.45, "world_star", seg=72)                      # the starry field, sunk
    SP.torus((CX, CY, 0.45), 4.12, 0.33, "gold", normal=(0, 0, 1), seg=120, tseg=12)       # the bezel
    SP.torus((CX, CY, 0.6), 4.5, 0.16, "brass_dark", normal=(0, 0, 1), seg=120, tseg=10)
    SP.torus((CX, CY, 0.44), 2.52, 0.08, "gold", normal=(0, 0, 1), seg=96, tseg=8)
    for r in (3.58, 3.9):                                                                   # the minute track
        SP.torus((CX, CY, 0.42), r, 0.045, "iron_dark", normal=(0, 0, 1), seg=120, tseg=8)
    for m in range(60):
        th = m / 60 * 2 * math.pi
        big = m % 5 == 0
        r0, r1 = (3.45, 3.98) if big else (3.6, 3.88)
        stroke(on_ring(0, 0, r0, th), on_ring(0, 0, r1, th), 0.15 if big else 0.07, 0.32, 0.43, "iron_dark")
    for k, text in enumerate(("XII", "I", "II", "III", "IIII", "V", "VI", "VII", "VIII", "IX", "X", "XI")):
        th = k / 12 * 2 * math.pi
        for a, b in glyphs(text, 0.6, 0.11):
            stroke(on_ring(*a, 2.98, th), on_ring(*b, 2.98, th), 0.11, 0.32, 0.43, "iron_dark")
    for k in range(16):                                                                     # the gilt sun
        th = k / 16 * 2 * math.pi
        L = 1.75 if k % 2 == 0 else 1.25
        flat([on_ring(-0.17, 0, 0.5, th), on_ring(0, L - 0.5, 0.5, th), on_ring(0.17, 0, 0.5, th)], 0.4, 0.47, "gold")
    SP.cyl((CX, CY, 0.47), (CX, CY, 0.36), 0.62, "gold", seg=40)
    SP.cyl((CX, CY, 0.37), (CX, CY, 0.33), 0.3, "brass_dark", seg=24)


def hand_shape(L, w, tip):
    """A hand pointing up from the pivot: a tail and its counterweight, a tapering shaft, its tip."""
    c = HAND_PIVOT
    stroke((0, -0.15), (0, L * 0.8), w, 0.0, 0.094, "gold", c)
    stroke((0, L * 0.8), (0, L), w * 0.5, 0.0, 0.094, "gold", c)
    SP.cyl((c[0], c[1], 0.0), (c[0], c[1], 0.094), 0.055, "gold", seg=24)
    SP.cyl((c[0], c[1] - 0.15, 0.0), (c[0], c[1] - 0.15, 0.094), w * 1.1, "gold", seg=20)
    tip(c, L)


@SP.prop("clock_hand_minute", 1, 1, 1, V=32)
def clock_hand_minute():
    def tip(c, L):
        flat([(0, L * 0.68), (0.06, L * 0.8), (0, L * 0.9), (-0.06, L * 0.8)], 0.0, 0.094, "gold", c)
    hand_shape(0.78, 0.045, tip)


@SP.prop("clock_hand_hour", 1, 1, 1, V=32)
def clock_hand_hour():
    def tip(c, L):
        SP.torus((c[0], c[1] + L * 0.72, 0.047), 0.07, 0.03, "gold", normal=(0, 0, 1), seg=32, tseg=8)
        flat([(0, L * 0.82), (0.09, L * 0.9), (0, L * 1.06), (-0.09, L * 0.9)], 0.0, 0.094, "gold", c)
    hand_shape(0.5, 0.07, tip)


# ================================================================ the Warden's blade

@SP.prop("warden_blade", 11, 28, 5, V=8)
def warden_blade():
    cx, cz = 5.5, 2.5
    rnd = random.Random(7)

    def blade(hw0, hw1, ht, mat, y0=-0.6, y1=17.2):
        """The blade from its buried point to the guard: a diamond section, half width hw0 at the foot, hw1 at the top."""
        rows = 24
        verts, faces = [], []
        for i in range(rows + 1):
            y = y0 + (y1 - y0) * i / rows
            f = i / rows
            hw = hw0 + (hw1 - hw0) * f if y > 0.4 else hw0 * max(0.05, (y - y0) / (0.4 - y0))
            verts += [(cx - hw, y, cz), (cx, y, cz - ht), (cx + hw, y, cz), (cx, y, cz + ht)]
        for i in range(rows):
            for k in range(4):
                a, b = i * 4 + k, i * 4 + (k + 1) % 4
                faces.append((a, b, b + 4, a + 4))
        faces += [(0, 1, 2, 3), tuple(range(rows * 4, rows * 4 + 4))]
        return SP.mesh(verts, faces, mat)

    blade(1.1, 1.45, 0.34, "steel")                        # the bright edges
    blade(0.8, 1.1, 0.44, "steel_dark")                    # the blade's flats, standing proud of the bevels
    SP.cut(SP.box(cx - 0.26, 1.2, cz - 0.7, cx + 0.26, 15.6, cz - 0.17, "x"))      # the fuller, both faces
    SP.cut(SP.box(cx - 0.26, 1.2, cz + 0.17, cx + 0.26, 15.6, cz + 0.7, "x"))
    SP.box(cx - 0.2, 1.1, cz - 0.24, cx + 0.2, 15.7, cz + 0.24, "molten", bevel=0.05)
    # the heave of broken stone round where it went in
    for k in range(16):
        a = k / 16 * 2 * math.pi + rnd.uniform(-0.15, 0.15)
        r = rnd.uniform(1.2, 2.1)
        x, z = cx + r * math.cos(a) * 1.25, cz + r * math.sin(a) * 0.9
        s = rnd.uniform(0.35, 0.6)
        SP.box(x - s, -0.1, z - s * 0.8, x + s, rnd.uniform(0.35, 0.8), z + s * 0.8, ("stone", "stone_dark")[k % 2],
               bevel=0.12, rot=(rnd.uniform(-18, 18), rnd.uniform(0, 90), rnd.uniform(-18, 18)))
    SP.ellip((cx, 0.05, cz), (1.6, 0.45, 1.3), "stone_dark", seg=24)
    SP.box(cx - 1.05, 0.0, cz - 0.4, cx + 1.05, 0.25, cz + 0.4, "coals_glow", bevel=0.05)      # the crack, glowing
    # the ricasso's langets and the guard
    SP.box(cx - 1.1, 15.8, cz - 0.5, cx + 1.1, 17.2, cz + 0.5, "iron_dark", bevel=0.12)
    SP.box(cx - 1.55, 17.0, cz - 0.75, cx + 1.55, 18.6, cz + 0.75, "iron_dark", bevel=0.2)
    for s in (-1, 1):
        KS.tube("q", [SP_p(cx + s * 1.4, 17.85, cz), SP_p(cx + s * 3.1, 17.95, cz), SP_p(cx + s * 4.4, 17.45, cz),
                      SP_p(cx + s * 5.1, 16.45, cz)], [0.52, 0.42, 0.33, 0.22], "iron_dark", seg=16)
        SP.caps((cx + s * 5.1, 16.45, cz), (cx + s * 5.3, 15.5, cz), 0.22, 0.05, "iron_dark", seg=12)
        SP.torus((cx + s * 2.3, 17.9, cz), 0.46, 0.11, "gold", normal=(1, 0, 0), seg=24, tseg=8)
        SP.torus((cx + s * 4.0, 17.65, cz), 0.38, 0.09, "gold", normal=(0.6, 0.6 * s, 0), seg=24, tseg=8)
    for f in (-1, 1):                                       # the ember set in the guard, front and back
        SP.ellip((cx, 17.8, cz + f * 0.72), (0.48, 0.48, 0.22), "coals_glow", seg=16)
        SP.torus((cx, 17.8, cz + f * 0.74), 0.55, 0.11, "gold", normal=(0, 0, 1), seg=32, tseg=8)
    # the grip, wrapped, and the caged ember of the pommel
    SP.cyl((cx, 18.6, cz), (cx, 23.4, cz), 0.42, "leather", seg=20)
    y = 18.85
    while y < 23.2:
        SP.torus((cx, y, cz), 0.42, 0.1, "leather_red", normal=(0, 1, 0), seg=24, tseg=8)
        y += 0.55
    SP.torus((cx, 23.55, cz), 0.5, 0.15, "gold", normal=(0, 1, 0), seg=28, tseg=8)
    SP.cyl((cx, 23.4, cz), (cx, 23.95, cz), 0.56, "iron_dark", seg=20)
    SP.ball((cx, 24.95, cz), 0.62, "molten", seg=20)
    SP.torus((cx, 24.95, cz), 0.86, 0.19, "iron_dark", normal=(0, 0, 1), seg=36, tseg=10)
    SP.torus((cx, 24.95, cz), 0.86, 0.15, "iron_dark", normal=(1, 0, 0), seg=36, tseg=10)
    SP.caps((cx, 25.75, cz), (cx, 27.7, cz), 0.3, 0.04, "iron_dark", seg=14)


def SP_p(x, y, z):
    return (x, y, z)


CIVIC = ["clock_face", "clock_hand_minute", "clock_hand_hour", "warden_blade"]


# ================================================================ the shops' signs and the guild's crest

def ring(cx, cy, rx, ry, n=24, a0=0.0, a1=2 * math.pi):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * k / n), cy + ry * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1 if a1 - a0 < 6.28 else n)]


class Board:
    """A trade sign hung from an iron bracket off a wall: the board edge-on to the street, read from along it.
    Emblem points (u, v) in -1..1 on the board's face, cut through it so it shows on both sides."""
    ZC, YC, R = 0.98, 0.99, 0.46

    def zy(self, pts):
        return [(self.ZC - u * self.R, self.YC + v * self.R) for u, v in pts]

    def shape(self, pts, mat, t=0.14):
        return SP.prism(self.zy(pts), 0.5 - t, 0.5 + t, mat, plane="zy")

    def bar(self, a, b, w, mat, t=0.14):
        (u0, v0), (u1, v1) = a, b
        L = math.hypot(u1 - u0, v1 - v0) or 1
        nu, nv = -(v1 - v0) / L * w / 2, (u1 - u0) / L * w / 2
        return self.shape([(u0 + nu, v0 + nv), (u1 + nu, v1 + nv), (u1 - nu, v1 - nv), (u0 - nu, v0 - nv)], mat, t)

    def disc(self, cu, cv, ru, rv, mat, t=0.14, n=24, a0=0.0, a1=2 * math.pi):
        return self.shape(ring(cu, cv, ru, rv, n, a0, a1), mat, t)


def bracket_and_board(field):
    SP.box(0.36, 1.25, 1.86, 0.64, 1.98, 2.0, "iron_dark", bevel=0.03)                     # the wall plate
    SP.box(0.44, 1.74, 0.12, 0.56, 1.84, 1.95, "iron_dark", bevel=0.02)                    # the arm
    SP.caps((0.5, 1.79, 0.12), (0.5, 1.92, 0.05), 0.05, 0.03, "iron_dark", seg=8)           # its curled end
    KS.tube("brace", [(0.5, 1.3, 1.9), (0.5, 1.45, 1.5), (0.5, 1.62, 1.1), (0.5, 1.74, 0.85)], [0.035] * 4, "iron_dark", seg=8)
    SP.torus((0.5, 1.52, 1.62), 0.13, 0.03, "iron_dark", normal=(1, 0, 0), seg=20, tseg=6)
    for z in (0.5, 1.46):                                                                    # the rings it hangs from
        SP.torus((0.5, 1.68, z), 0.07, 0.022, "iron", normal=(0, 0, 1), seg=16, tseg=6)
    SP.box(0.43, 0.38, 0.38, 0.57, 1.6, 1.58, "wood_dark", bevel=0.03)                     # the board, framed
    SP.box(0.41, 0.46, 0.46, 0.59, 1.52, 1.5, field, bevel=0.02)
    return Board()


SIGNS = {}


def sign(trade, field):
    def reg(fn):
        name = "sign_" + trade

        @SP.prop(name, 1, 2, 2, V=16)
        def build():
            fn(bracket_and_board(field))
        SIGNS[name] = build
        return fn
    return reg


@sign("general", "leather_blue")
def _(B):
    B.bar((0, -0.8), (0, 0.55), 0.13, "gold")
    B.bar((-0.4, -0.8), (0.4, -0.8), 0.14, "gold")
    B.bar((-0.75, 0.5), (0.75, 0.5), 0.12, "gold")
    for s in (-1, 1):
        B.bar((s * 0.72, 0.5), (s * 0.5, -0.05), 0.05, "gold")
        B.bar((s * 0.72, 0.5), (s * 0.94, -0.05), 0.05, "gold")
        B.disc(s * 0.72, -0.05, 0.3, 0.2, "gold", a0=math.pi, a1=2 * math.pi, n=12)
    B.disc(0, 0.62, 0.1, 0.1, "gold", n=12)


@sign("baker", "leather_red")
def _(B):
    B.disc(0, -0.35, 0.85, 0.75, "wood_end", n=24, a0=0, a1=math.pi)              # a loaf: domed, flat below
    B.shape([(-0.85, -0.35), (0.85, -0.35), (0.78, -0.55), (-0.78, -0.55)], "wood")
    for k in (-1, 0, 1):
        B.bar((k * 0.42 - 0.14, -0.12), (k * 0.42 + 0.14, 0.24), 0.09, "wood_dark", t=0.15)


@sign("tailor", "leather_violet")
def _(B):
    for s in (-1, 1):
        SP.torus((0.5, B.YC - 0.48 * B.R, B.ZC - s * 0.4 * B.R), 0.2 * B.R, 0.07 * B.R, "steel", normal=(1, 0, 0), seg=20, tseg=6)
        B.bar((s * 0.32, -0.3), (-s * 0.4, 0.85), 0.15, "steel")
    B.disc(0, 0.12, 0.08, 0.08, "brass", t=0.16, n=10)


@sign("apothecary", "leather_green")
def _(B):
    B.disc(0, -0.3, 0.5, 0.48, "glass", n=28)
    B.disc(0, -0.36, 0.42, 0.36, "potion_green", t=0.15, n=24, a0=math.pi * 1.05, a1=math.pi * 1.95)
    B.shape([(-0.42, -0.36), (0.42, -0.36), (0.38, -0.12), (-0.38, -0.12)], "potion_green", t=0.15)
    B.shape([(-0.14, 0.12), (0.14, 0.12), (0.14, 0.62), (-0.14, 0.62)], "glass")
    B.shape([(-0.18, 0.62), (0.18, 0.62), (0.15, 0.84), (-0.15, 0.84)], "wood")


@sign("grocer", "wood")
def _(B):
    B.disc(0, -0.15, 0.6, 0.55, "cloth_red", n=28)
    B.bar((0, 0.3), (0.12, 0.72), 0.08, "wood_dark", t=0.15)
    B.disc(-0.25, 0.6, 0.26, 0.12, "leaf", t=0.15, n=14)


@sign("books", "leather_blue")
def _(B):
    B.shape([(-0.88, 0.5), (0, 0.32), (0.88, 0.5), (0.88, -0.48), (0, -0.62), (-0.88, -0.48)], "leather_red")
    B.shape([(-0.78, 0.44), (-0.04, 0.3), (-0.04, -0.5), (-0.78, -0.38)], "paper", t=0.16)
    B.shape([(0.78, 0.44), (0.04, 0.3), (0.04, -0.5), (0.78, -0.38)], "paper", t=0.16)


@sign("chandler", "leather_blue")
def _(B):
    B.shape([(-0.17, -0.62), (0.17, -0.62), (0.17, 0.3), (-0.17, 0.3)], "wax")
    B.shape([(0, 0.36), (0.13, 0.55), (0, 0.9), (-0.13, 0.55)], "sun_glow", t=0.15)
    B.disc(0, -0.7, 0.5, 0.1, "brass", n=16)


@sign("fishmonger", "leather_blue")
def _(B):
    B.disc(-0.15, 0, 0.6, 0.32, "silver", n=28)
    B.shape([(0.35, 0), (0.85, 0.38), (0.85, -0.38)], "silver")
    B.disc(-0.52, 0.08, 0.07, 0.07, "iron_dark", t=0.16, n=10)


@SP.prop("guild_crest", 5, 4, 1, V=16)
def guild_crest():
    """The Adventurers' Guild: a red heater shield in a gilt rim, a sword down it, crossed blades behind it and a crown
    over it. Viewer's right is -x."""
    cx = 2.5

    def shield(k):
        pts = [(-1.15 * k, 3.15 - (1 - k) * 0.4), (1.15 * k, 3.15 - (1 - k) * 0.4)]
        for a in range(1, 12):
            t = a / 12
            pts.append((1.15 * k * math.cos(t * math.pi / 2) ** 0.7, 3.15 - (1 - k) * 0.4 - t * 2.75 * k))
        pts.append((0, 3.15 - 2.95 * k - (1 - k) * 0.4))
        for a in range(11, 0, -1):
            t = a / 12
            pts.append((-1.15 * k * math.cos(t * math.pi / 2) ** 0.7, 3.15 - (1 - k) * 0.4 - t * 2.75 * k))
        return [(cx - x, y) for x, y in pts]
    for s in (-1, 1):                                    # the crossed swords behind: hilts up at the corners
        stroke((s * 1.4, 3.2 - CY), (-s * 0.75, 1.2 - CY), 0.2, 0.55, 0.85, "steel", c=(cx, CY))
        stroke((s * 1.4, 3.2 - CY), (s * 1.62, 3.72 - CY), 0.14, 0.5, 0.85, "leather", c=(cx, CY))
        stroke((s * 1.12, 3.5 - CY), (s * 1.72, 2.92 - CY), 0.13, 0.45, 0.85, "gold", c=(cx, CY))
    SP.prism(shield(1.0), 0.25, 0.9, "gold")
    SP.cut(SP.prism(shield(0.86), 0.2, 0.35, "x"))
    SP.prism(shield(0.86), 0.35, 0.9, "cloth_red")
    stroke((0, 2.75 - CY), (0, 0.75 - CY), 0.26, 0.2, 0.36, "steel", c=(cx, CY))           # the sword down it
    stroke((-0.55, 2.4 - CY), (0.55, 2.4 - CY), 0.18, 0.18, 0.36, "gold", c=(cx, CY))
    stroke((0, 2.4 - CY), (0, 2.95 - CY), 0.14, 0.18, 0.36, "leather", c=(cx, CY))
    SP.prism([(cx + 0.7, 3.25), (cx + 0.7, 3.95), (cx + 0.35, 3.62), (cx, 3.98), (cx - 0.35, 3.62), (cx - 0.7, 3.95),
              (cx - 0.7, 3.25)], 0.2, 0.8, "gold")       # the crown


CIVIC += ["guild_crest"] + sorted(SIGNS)


# ================================================================ the guild hall's furniture

def quad(cx, cy, w, h, ang=0.0):
    """A w x h rectangle about (cx, cy) in the prop's xy plane, turned ang degrees."""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + dx * ca - dy * sa, cy + dx * sa + dy * ca) for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]


LETTERS = {          # rank letters as strokes in a 1 x 2 box about 0 (s to the viewer's right, t up)
    "F": [((-.5, -1), (-.5, 1)), ((-.5, 1), (.5, 1)), ((-.5, 0), (.3, 0))],
    "E": [((-.5, -1), (-.5, 1)), ((-.5, 1), (.5, 1)), ((-.5, 0), (.3, 0)), ((-.5, -1), (.5, -1))],
    "D": [((-.5, -1), (-.5, 1)), ((-.5, 1), (.15, 1)), ((.15, 1), (.5, .5)), ((.5, .5), (.5, -.5)), ((.5, -.5), (.15, -1)), ((.15, -1), (-.5, -1))],
    "C": [((.5, 1), (-.25, 1)), ((-.25, 1), (-.5, .55)), ((-.5, .55), (-.5, -.55)), ((-.5, -.55), (-.25, -1)), ((-.25, -1), (.5, -1))],
    "B": [((-.5, -1), (-.5, 1)), ((-.5, 1), (.25, 1)), ((.25, 1), (.45, .55)), ((.45, .55), (.25, 0)), ((-.5, 0), (.3, 0)),
          ((.3, 0), (.5, -.5)), ((.5, -.5), (.3, -1)), ((.3, -1), (-.5, -1))],
    "A": [((-.55, -1), (0, 1)), ((0, 1), (.55, -1)), ((-.3, -.15), (.3, -.15))],
    "S": [((.5, 1), (-.3, 1)), ((-.3, 1), (-.5, .55)), ((-.5, .55), (-.3, .05)), ((-.3, .05), (.3, -.05)), ((.3, -.05), (.5, -.55)),
          ((.5, -.55), (.3, -1)), ((.3, -1), (-.5, -1))],
}


@SP.prop("guild_board", 10, 6, 1, V=16)
def guild_board():
    """The guild's gate board: a timber frame on the wall under a little slate roof, a column a rank (F to S, read
    from the viewer's left) under a gilt plaque, each pinned with notices, writs and wanted bills; the S rank's on black
    with gold ink. A lantern hung either side."""
    rnd = random.Random(31)
    SP.box(0.05, 0.0, 0.55, 0.45, 5.62, 1.0, "wood_dark", bevel=0.03)               # the posts
    SP.box(9.55, 0.0, 0.55, 9.95, 5.62, 1.0, "wood_dark", bevel=0.03)
    SP.box(0.3, 0.3, 0.8, 9.7, 5.4, 1.0, "wood_dark", bevel=0.02)                    # the backboard
    SP.box(0.45, 0.55, 0.7, 9.55, 5.1, 0.82, "leather", bevel=0.01)                  # the cork
    SP.box(0.3, 5.08, 0.62, 9.7, 5.4, 0.84, "wood", bevel=0.02)                      # the rails
    SP.box(0.3, 0.3, 0.62, 9.7, 0.56, 0.84, "wood", bevel=0.02)
    for x in (0.25, 9.75):                                                           # knee braces under the roof
        SP.box(x - 0.1, 4.9, 0.45, x + 0.1, 5.5, 0.6, "wood_dark", bevel=0.02)
    SP.prism([(0.0, 5.48), (1.0, 5.86), (1.0, 6.0), (0.0, 5.64)], -0.1, 10.1, "stone_dark", plane="zy")   # the pent roof
    for k, z in enumerate((0.18, 0.45, 0.72)):
        y = 5.48 + 0.38 * z + 0.15
        SP.box(0.0, y, z - 0.03, 10.0, y + 0.05, z + 0.03, "iron_dark", bevel=0.0)
    SP.box(-0.05, 5.42, 0.0, 10.05, 5.52, 0.14, "wood_dark", bevel=0.02)            # its fascia
    for x in (0.25, 9.75):                                                           # the lanterns
        SP.box(x - 0.03, 4.55, 0.2, x + 0.03, 4.62, 0.58, "iron_dark", bevel=0.0)
        SP.box(x - 0.13, 4.0, 0.12, x + 0.13, 4.06, 0.38, "iron_dark", bevel=0.01)
        SP.box(x - 0.11, 4.06, 0.14, x + 0.11, 4.42, 0.36, "glass", bevel=0.0)
        SP.ellip((x, 4.2, 0.25), (0.06, 0.11, 0.06), "flame", seg=10)
        SP.prism([(x - 0.15, 4.42), (x + 0.15, 4.42), (x, 4.56)], 0.1, 0.4, "iron_dark")
    n = len("FEDCBAS")
    cw = 9.1 / n
    for k, rank in enumerate("FEDCBAS"):
        x = 9.55 - cw * (k + 0.5)                                                    # the viewer's left is +x
        SP.box(x - 0.5, 4.42, 0.6, x + 0.5, 4.98, 0.7, "gold", bevel=0.01)          # the plaque
        SP.box(x - 0.43, 4.48, 0.56, x + 0.43, 4.92, 0.66, "wood_dark", bevel=0.0)
        for a, b in LETTERS[rank]:
            stroke((a[0] * 0.15, a[1] * 0.17), (b[0] * 0.15, b[1] * 0.17), 0.085, 0.5, 0.58, "gold", c=(x, 4.7))
        top = 4.3
        sheets = rnd.choice((2, 3, 3))
        for j in range(sheets):
            h = (top - 0.65) / sheets - 0.12
            h *= rnd.uniform(0.8, 1.0)
            w = rnd.uniform(0.85, 1.12)
            cy = top - 0.06 - h / 2
            cx = x + rnd.uniform(-0.06, 0.06)
            ang = rnd.uniform(-5, 5)
            black = rank == "S"
            paper, ink = ("iron_dark", "gold") if black else ("paper", "wood_dark")
            if rank in "BA":
                SP.prism(quad(cx, cy, w + 0.08, h + 0.08, ang), 0.64, 0.7, "gold")
            SP.prism(quad(cx, cy, w, h, ang), 0.6, 0.7, paper)
            wanted = not black and rnd.random() < 0.4
            lines = []
            t = h / 2 - 0.12
            if wanted:                                                               # a sketch of the quarry
                SP.prism(quad(cx + math.sin(math.radians(-ang)) * 0, cy + t - 0.22, w * 0.55, 0.36, ang), 0.56, 0.62, "leather_red")
                SP.ellip((cx, cy + t - 0.22, 0.56), (0.1, 0.09, 0.04), "wood_dark", seg=12)
                t -= 0.5
            lines.append((t, w * 0.7, 0.1))
            t -= 0.16
            while t > -h / 2 + 0.16:
                lines.append((t, w * rnd.uniform(0.45, 0.78), 0.065))
                t -= 0.13
            a = math.radians(ang)
            for ty, lw, th in lines:
                px, py = cx - ty * math.sin(a), cy + ty * math.cos(a)
                SP.prism(quad(px, py, lw, th, ang), 0.56, 0.64, ink)
            sx, sy = cx - w * 0.3, cy - h / 2 + 0.12
            SP.cyl((sx, sy, 0.62), (sx, sy, 0.54), 0.075, "cloth_red", seg=14)       # the seal
            SP.ball((cx, cy + h / 2 - 0.05, 0.56), 0.045, "iron", seg=10)           # the pin
            top = cy - h / 2 - 0.08


@SP.prop("guild_counter", 6, 1, 1, V=16)
def guild_counter():
    """The clerks' counter, a long panelled desk waist high (the top at 0.9, so a clerk is spoken to across it): dark
    oak stiles and rails, raised panels with a gilt lozenge, a moulded top; on it the open register, an inkwell and
    quill, a bell, a pile of writs and a stack of coin."""
    SP.box(0.02, 0.0, 0.12, 5.98, 0.1, 1.0, "wood_dark", bevel=0.02)                 # the kick
    SP.box(0.04, 0.1, 0.16, 5.96, 0.82, 1.0, "wood", bevel=0.01)
    for x in (0.08, 1.5, 3.0, 4.5, 5.92):
        SP.box(x - 0.08, 0.1, 0.1, x + 0.08, 0.82, 0.2, "wood_dark", bevel=0.015)
    SP.box(0.04, 0.1, 0.1, 5.96, 0.22, 0.2, "wood_dark", bevel=0.01)
    SP.box(0.04, 0.7, 0.1, 5.96, 0.82, 0.2, "wood_dark", bevel=0.01)
    for xa, xb in ((0.08, 1.5), (1.5, 3.0), (3.0, 4.5), (4.5, 5.92)):
        SP.box(xa + 0.16, 0.3, 0.12, xb - 0.16, 0.62, 0.18, "wood", bevel=0.03)
        m = (xa + xb) / 2
        SP.prism([(m, 0.36), (m + 0.12, 0.46), (m, 0.56), (m - 0.12, 0.46)], 0.08, 0.12, "gold")
    SP.box(0.0, 0.82, 0.0, 6.0, 0.9, 1.0, "wood_dark", bevel=0.025)                 # the top
    SP.box(0.0, 0.8, 0.02, 6.0, 0.84, 0.08, "wood", bevel=0.01)
    SP.box(1.05, 0.9, 0.32, 1.95, 0.92, 0.78, "leather_red", bevel=0.005)          # the register, open
    SP.box(1.08, 0.92, 0.35, 1.48, 0.96, 0.75, "paper", bevel=0.01)
    SP.box(1.52, 0.92, 0.35, 1.92, 0.96, 0.75, "paper", bevel=0.01)
    for k in range(4):
        z = 0.42 + k * 0.08
        SP.box(1.14, 0.955, z, 1.42, 0.965, z + 0.03, "wood_dark", bevel=0.0)
        SP.box(1.58, 0.955, z, 1.84, 0.965, z + 0.03, "wood_dark", bevel=0.0)
    SP.cyl((2.35, 0.9, 0.55), (2.35, 0.98, 0.55), 0.055, "iron_dark", seg=14)     # inkwell and quill
    KS.tube("quill", [(2.36, 0.95, 0.56), (2.45, 1.0, 0.62), (2.55, 1.0, 0.7)], [0.02, 0.03, 0.015], "towel", seg=8)
    for k in range(4):                                                               # the writs
        SP.box(3.2 + k * 0.03, 0.9 + k * 0.018, 0.28 + k * 0.02, 3.62 + k * 0.03, 0.918 + k * 0.018, 0.76 + k * 0.02, "paper", bevel=0.0)
    SP.lathe((4.7, 0.9, 0.5), [(0, 0.08), (0.02, 0.08), (0.05, 0.06), (0.07, 0.03), (0.09, 0.012)], "brass", seg=20)  # the bell
    for k, (x, z) in enumerate(((5.25, 0.4), (5.4, 0.55), (5.2, 0.62))):
        SP.cyl((x, 0.9, z), (x, 0.92 + 0.02 * (3 - k), z), 0.05, "gold", seg=14)


@SP.prop("trestle_table", 3, 1, 2, V=16)
def trestle_table():
    """A long trestle table of heavy boards on crossed legs, a stretcher pegged through them; laid with a platter of
    bread and cheese, tankards, a candle in a brass stick and a rolled map."""
    for k in range(4):                                                               # the boards
        z0 = 0.04 + k * 0.48
        SP.box(0.0, 0.72, z0, 3.0, 0.82, z0 + 0.46, "wood", bevel=0.02)
    for x in (0.0, 2.92):
        SP.box(x, 0.71, 0.02, x + 0.08, 0.83, 1.98, "wood_dark", bevel=0.015)       # breadboard ends
    for x in (0.42, 2.58):
        SP.box(x - 0.07, 0.0, 0.12, x + 0.07, 0.1, 1.88, "wood_dark", bevel=0.02)  # the feet
        SP.box(x - 0.07, 0.62, 0.18, x + 0.07, 0.72, 1.82, "wood_dark", bevel=0.02)
        SP.cyl((x, 0.08, 0.3), (x, 0.64, 1.7), 0.065, "wood_dark", seg=10)
        SP.cyl((x, 0.08, 1.7), (x, 0.64, 0.3), 0.065, "wood_dark", seg=10)
    SP.box(0.3, 0.34, 0.94, 2.7, 0.46, 1.06, "wood_dark", bevel=0.02)               # the stretcher, wedged
    for x in (0.25, 2.75):
        SP.box(x - 0.03, 0.3, 0.9, x + 0.03, 0.5, 1.1, "wood", bevel=0.005)
    SP.cyl((1.5, 0.82, 1.0), (1.5, 0.845, 1.0), 0.28, "iron", seg=28)               # the platter
    SP.ellip((1.42, 0.88, 0.95), (0.14, 0.06, 0.09), "straw", seg=16)
    SP.prism([(1.55, 0.845), (1.75, 0.845), (1.55, 0.93)], 1.02, 1.18, "wax")
    for x, z in ((0.55, 0.45), (2.3, 1.55), (0.9, 1.5), (2.45, 0.5)):               # the tankards
        SP.cyl((x, 0.82, z), (x, 0.97, z), 0.065, "wood", r2=0.06, seg=14)
        SP.cyl((x, 0.84, z), (x, 0.86, z), 0.07, "iron_dark", seg=14)
        SP.cyl((x, 0.93, z), (x, 0.95, z), 0.066, "iron_dark", seg=14)
        SP.torus((x + 0.08, 0.9, z), 0.04, 0.014, "iron_dark", normal=(0, 0, 1), seg=12, tseg=6)
    SP.cyl((1.95, 0.82, 0.45), (1.95, 0.84, 0.45), 0.07, "brass", seg=14)          # the candle
    SP.cyl((1.95, 0.84, 0.45), (1.95, 0.98, 0.45), 0.035, "wax", seg=10)
    SP.cyl((0.6, 0.865, 1.05), (1.15, 0.865, 1.05), 0.045, "paper", seg=12)         # the map
    SP.cyl((0.58, 0.865, 1.05), (0.62, 0.865, 1.05), 0.05, "leather_red", seg=12)


@SP.prop("guild_chair", 1, 2, 1, V=16)
def guild_chair():
    """A high-backed oak chair, the seat and back padded in red leather with brass studs, turned finials."""
    for x in (0.12, 0.8):
        SP.box(x, 0.0, 0.1, x + 0.08, 0.44, 0.18, "wood_dark", bevel=0.012)        # front legs
        SP.box(x, 0.0, 0.78, x + 0.08, 1.38, 0.87, "wood_dark", bevel=0.012)       # back posts
        SP.ball((x + 0.04, 1.43, 0.825), 0.055, "wood", seg=12)
        SP.box(x + 0.01, 0.14, 0.18, x + 0.07, 0.19, 0.78, "wood", bevel=0.005)    # side stretchers
    SP.box(0.2, 0.14, 0.12, 0.8, 0.19, 0.17, "wood", bevel=0.005)
    SP.box(0.1, 0.42, 0.08, 0.9, 0.5, 0.88, "wood", bevel=0.02)                     # the seat
    SP.box(0.16, 0.5, 0.13, 0.84, 0.56, 0.82, "leather_red", bevel=0.03)
    SP.box(0.2, 0.6, 0.8, 0.8, 1.2, 0.86, "leather_red", bevel=0.03)                # the back
    SP.prism([(0.14, 1.2), (0.86, 1.2), (0.86, 1.3), (0.5, 1.38), (0.14, 1.3)], 0.77, 0.88, "wood_dark")
    SP.box(0.14, 0.56, 0.78, 0.86, 0.62, 0.88, "wood_dark", bevel=0.01)
    for x in (0.24, 0.37, 0.5, 0.63, 0.76):
        SP.ball((x, 1.16, 0.79), 0.022, "brass", seg=8)
        SP.ball((x, 0.64, 0.79), 0.022, "brass", seg=8)


@SP.prop("round_table", 2, 1, 2, V=16)
def round_table():
    """A round tavern table on a turned pedestal and four splayed feet; a map spread on it under a dagger, tankards,
    dice and a candle stub."""
    SP.lathe((1.0, 0.0, 1.0), [(0.7, 0.86), (0.74, 0.92), (0.8, 0.93), (0.82, 0.9)], "wood", seg=40)
    SP.lathe((1.0, 0.0, 1.0), [(0.62, 0.3), (0.7, 0.8), (0.72, 0.3)], "wood_dark", seg=28)
    SP.lathe((1.0, 0.0, 1.0), [(0.08, 0.14), (0.16, 0.1), (0.3, 0.08), (0.36, 0.11), (0.42, 0.08), (0.6, 0.075),
                               (0.66, 0.12), (0.7, 0.1)], "wood_dark", seg=20)
    for a in range(4):
        th = math.radians(45 + 90 * a)
        SP.cyl((1.0, 0.16, 1.0), (1.0 + 0.72 * math.cos(th), 0.05, 1.0 + 0.72 * math.sin(th)), 0.06, "wood_dark", r2=0.05, seg=10)
    SP.box(0.52, 0.82, 0.82, 1.28, 0.84, 1.38, "paper", bevel=0.0)                  # the map
    for ax, az, bx, bz in ((0.62, 0.98, 1.05, 1.02), (0.8, 0.9, 0.95, 1.3), (1.0, 1.2, 1.18, 1.18)):
        SP.box(min(ax, bx), 0.834, min(az, bz), max(ax, bx) + 0.03, 0.842, max(az, bz) + 0.03, "leather_red", bevel=0.0)
    SP.box(0.75, 0.84, 1.15, 1.2, 0.86, 1.19, "steel", bevel=0.005)                # the dagger
    SP.box(0.68, 0.835, 1.12, 0.75, 0.87, 1.22, "iron_dark", bevel=0.005)
    SP.box(0.55, 0.84, 1.15, 0.68, 0.865, 1.19, "leather", bevel=0.005)
    for x, z in ((1.45, 0.7), (0.55, 0.65)):
        SP.cyl((x, 0.82, z), (x, 0.97, z), 0.065, "wood", r2=0.06, seg=14)
        SP.cyl((x, 0.85, z), (x, 0.87, z), 0.07, "iron_dark", seg=14)
        SP.torus((x + 0.08, 0.9, z), 0.04, 0.014, "iron_dark", normal=(0, 0, 1), seg=12, tseg=6)
    for x, z in ((1.4, 1.35), (1.5, 1.28)):
        SP.box(x, 0.82, z, x + 0.06, 0.88, z + 0.06, "bone", bevel=0.01)
    SP.cyl((1.25, 0.82, 0.55), (1.25, 0.84, 0.55), 0.07, "iron_dark", seg=14)
    SP.cyl((1.25, 0.84, 0.55), (1.25, 0.92, 0.55), 0.04, "wax", seg=10)


@SP.prop("tavern_bar", 4, 1, 1, V=16)
def tavern_bar():
    """The Rest's bar: an upright-boarded front bound in iron, a brass foot rail on brackets, a thick dark top with a
    drip edge; tankards, a stoneware jug and a bottle on it."""
    SP.box(0.02, 0.0, 0.16, 3.98, 0.1, 1.0, "wood_dark", bevel=0.02)
    SP.box(0.02, 0.1, 0.2, 3.98, 0.8, 1.0, "wood", bevel=0.01)
    for k in range(16):                                                              # the boards
        x = k * 0.25
        SP.box(x + 0.01, 0.1, 0.13, x + 0.24, 0.8, 0.2, "wood" if k % 3 else "wood_dark", bevel=0.01)
    for y in (0.22, 0.66):                                                           # iron straps, riveted
        SP.box(0.0, y, 0.11, 4.0, y + 0.06, 0.14, "iron_dark", bevel=0.0)
        for k in range(8):
            SP.ball((0.25 + k * 0.5, y + 0.03, 0.11), 0.022, "iron", seg=8)
    SP.box(0.0, 0.8, 0.0, 4.0, 0.88, 1.0, "wood_dark", bevel=0.025)                # the top
    SP.box(0.0, 0.77, 0.02, 4.0, 0.81, 0.1, "wood", bevel=0.01)
    SP.cyl((0.0, 0.2, 0.06), (4.0, 0.2, 0.06), 0.035, "brass", seg=14)            # the foot rail
    for x in (0.5, 2.0, 3.5):
        SP.box(x - 0.02, 0.18, 0.06, x + 0.02, 0.24, 0.15, "brass", bevel=0.0)
    for x, z in ((0.6, 0.4), (1.3, 0.55), (2.7, 0.35), (3.4, 0.6)):
        SP.cyl((x, 0.88, z), (x, 1.0, z), 0.06, "wood", r2=0.055, seg=14)
        SP.cyl((x, 0.9, z), (x, 0.92, z), 0.065, "iron_dark", seg=14)
        SP.cyl((x, 0.975, z), (x, 1.0, z), 0.058, "towel", seg=14)
        SP.torus((x + 0.075, 0.94, z), 0.035, 0.013, "iron_dark", normal=(0, 0, 1), seg=12, tseg=6)
    SP.lathe((2.0, 0.88, 0.5), [(0, 0.05), (0.04, 0.08), (0.09, 0.07), (0.11, 0.035)], "clay_fired", seg=18)   # the jug
    SP.lathe((1.9, 0.88, 0.75), [(0, 0.04), (0.06, 0.045), (0.08, 0.02), (0.12, 0.015)], "leaf_dark", seg=14)  # a bottle


@SP.prop("keg_rack", 4, 2, 1, V=16)
def keg_rack():
    """Kegs on their sides in a cradle against the wall, ends out, brass taps in them; over them a shelf of bottles
    and a rail of tankards hung on pegs."""
    SP.box(0.0, 0.0, 0.85, 4.0, 2.0, 1.0, "wood", bevel=0.01)                       # the back boards
    for x in (0.0, 1.96, 3.9):
        SP.box(x, 0.0, 0.08, x + 0.1, 1.95, 0.98, "wood_dark", bevel=0.015)
    for z in (0.18, 0.78):
        SP.box(0.0, 0.06, z - 0.06, 4.0, 0.18, z + 0.06, "wood_dark", bevel=0.02)  # the cradle
    for x in (0.5, 1.5, 2.5, 3.5):
        xc = x + (0.03 if x < 2 else -0.03)
        y = 0.6
        SP.cyl((xc, y, 0.08), (xc, y, 0.48), 0.37, "wood", r2=0.42, seg=28)
        SP.cyl((xc, y, 0.48), (xc, y, 0.88), 0.42, "wood", r2=0.37, seg=28)
        SP.cyl((xc, y, 0.07), (xc, y, 0.09), 0.34, "wood_end", seg=28)
        for z, r in ((0.14, 0.395), (0.36, 0.425), (0.6, 0.425), (0.82, 0.395)):
            SP.torus((xc, y, z), r, 0.02, "iron_dark", normal=(0, 0, 1), seg=32, tseg=6)
        SP.cyl((xc, y - 0.18, 0.08), (xc, y - 0.18, 0.0), 0.035, "brass", seg=10)   # the tap
        SP.cyl((xc, y - 0.18, 0.02), (xc, y - 0.28, 0.02), 0.025, "brass", seg=8)
        SP.box(xc - 0.03, y - 0.14, 0.0, xc + 0.03, y - 0.06, 0.04, "brass", bevel=0.005)
    SP.box(0.0, 1.12, 0.3, 4.0, 1.2, 0.86, "wood_dark", bevel=0.02)                # the shelf
    rnd = random.Random(5)
    x = 0.25
    while x < 3.8:
        mat = rnd.choice(("leaf_dark", "leaf_dark", "clay_fired", "glass", "leather_red"))
        r = rnd.uniform(0.045, 0.07)
        SP.lathe((x, 1.2, 0.6), [(0, r * 0.9), (r * 2.6, r), (r * 3.2, r * 0.45), (r * 4.4, r * 0.35), (r * 4.6, r * 0.4)], mat, seg=14)
        x += rnd.uniform(0.17, 0.3)
    SP.box(0.0, 1.72, 0.74, 4.0, 1.8, 0.86, "wood_dark", bevel=0.01)               # the peg rail
    for k in range(7):
        x = 0.35 + k * 0.55
        SP.cyl((x, 1.76, 0.74), (x, 1.76, 0.62), 0.02, "wood", seg=8)
        SP.cyl((x, 1.5, 0.62), (x, 1.66, 0.62), 0.06, "wood", r2=0.055, seg=14)
        SP.cyl((x, 1.53, 0.62), (x, 1.55, 0.62), 0.065, "iron_dark", seg=14)
        SP.torus((x, 1.66, 0.62), 0.035, 0.012, "iron_dark", normal=(1, 0, 0), seg=12, tseg=6)


@SP.prop("bar_stool", 1, 1, 1, V=16)
def bar_stool():
    """A tall stool: a round seat padded in red leather, four splayed legs, a foot ring."""
    SP.cyl((0.5, 0.62, 0.5), (0.5, 0.68, 0.5), 0.3, "wood_dark", seg=28)
    SP.lathe((0.5, 0.68, 0.5), [(0, 0.27), (0.03, 0.27), (0.06, 0.2)], "leather_red", seg=28)
    for a in range(4):
        th = math.radians(45 + 90 * a)
        SP.cyl((0.5 + 0.17 * math.cos(th), 0.62, 0.5 + 0.17 * math.sin(th)),
               (0.5 + 0.33 * math.cos(th), 0.0, 0.5 + 0.33 * math.sin(th)), 0.04, "wood_dark", seg=10)
    SP.torus((0.5, 0.25, 0.5), 0.265, 0.025, "iron_dark", normal=(0, 1, 0), seg=28, tseg=6)


@SP.prop("guild_chandelier", 3, 2, 3, V=16)
def guild_chandelier():
    """An iron wheel of candles hung by four chains from a ring: the rim and a gilt inner ring on eight spokes, a drip
    cup and a candle at each of twelve points round it, a pendant finial under the hub. The candles light the hall."""
    c = 1.5
    SP.torus((c, 0.42, c), 1.22, 0.075, "iron_dark", normal=(0, 1, 0), seg=64, tseg=10)
    SP.torus((c, 0.42, c), 0.55, 0.05, "gold", normal=(0, 1, 0), seg=40, tseg=8)
    for a in range(8):
        th = math.radians(22.5 + 45 * a)
        SP.cyl((c + 0.12 * math.cos(th), 0.42, c + 0.12 * math.sin(th)), (c + 1.2 * math.cos(th), 0.42, c + 1.2 * math.sin(th)),
               0.04, "iron_dark", seg=8)
    SP.lathe((c, 0.0, c), [(0.05, 0.0), (0.1, 0.06), (0.2, 0.09), (0.3, 0.06), (0.38, 0.1), (0.48, 0.12), (0.56, 0.07),
                           (0.62, 0.04)], "iron_dark", seg=20)
    SP.ball((c, 0.07, c), 0.06, "gold", seg=12)
    for a in range(12):
        th = math.radians(30 * a)
        x, z = c + 1.22 * math.cos(th), c + 1.22 * math.sin(th)
        SP.cyl((x, 0.47, z), (x, 0.52, z), 0.08, "brass", seg=12)
        SP.cyl((x, 0.52, z), (x, 0.74, z), 0.045, "wax", seg=10)
        SP.ellip((x, 0.8, z), (0.045, 0.075, 0.045), "flame", seg=10)
    for a in range(4):
        th = math.radians(45 + 90 * a)
        SP.chain((c + 1.15 * math.cos(th), 0.48, c + 1.15 * math.sin(th)), (c + 0.1 * math.cos(th), 1.82, c + 0.1 * math.sin(th)),
                 "iron_dark", link=0.13, r=0.03)
    SP.torus((c, 1.85, c), 0.13, 0.04, "iron_dark", normal=(0, 1, 0), seg=20, tseg=6)
    SP.cyl((c, 1.85, c), (c, 2.0, c), 0.045, "iron_dark", seg=10)


@SP.prop("trophy_skull", 2, 2, 1, V=16)
def trophy_skull():
    """A trophy for the wall: the horned skull of something the guild killed, on an iron-rimmed oak shield, embers
    still in its eyes."""
    cx = 1.0

    def shield(k):
        pts = []
        for a in range(13):
            t = a / 12
            pts.append((cx + 0.86 * k * math.cos(t * math.pi / 2) ** 0.7, 1.92 - (1 - k) * 0.12 - t * 1.6 * k))
        pts.append((cx, 1.92 - 1.82 * k - (1 - k) * 0.12))
        for a in range(12, -1, -1):
            t = a / 12
            pts.append((cx - 0.86 * k * math.cos(t * math.pi / 2) ** 0.7, 1.92 - (1 - k) * 0.12 - t * 1.6 * k))
        return pts
    SP.prism(shield(1.0), 0.86, 1.0, "iron_dark")
    SP.prism(shield(0.9), 0.8, 0.98, "wood_dark")
    for k in range(5):
        SP.box(cx - 0.75 + k * 0.3, 0.3, 0.78, cx - 0.74 + k * 0.3 + 0.01, 1.82, 0.8, "wood", bevel=0.0)
    for x, y in ((cx - 0.72, 1.82), (cx + 0.72, 1.82), (cx - 0.6, 0.85), (cx + 0.6, 0.85), (cx, 0.22)):
        SP.ball((x, y, 0.84), 0.04, "brass", seg=8)
    SP.ellip((cx, 1.18, 0.5), (0.34, 0.32, 0.32), "bone", seg=28)                  # the cranium
    SP.ellip((cx, 1.2, 0.24), (0.33, 0.09, 0.1), "bone", seg=20)                    # the brow
    SP.ellip((cx, 0.9, 0.22), (0.2, 0.17, 0.22), "bone", seg=20)                    # the snout
    for s in (-1, 1):
        SP.ellip((cx + s * 0.24, 0.98, 0.32), (0.11, 0.1, 0.14), "bone", seg=16)   # cheekbones
    for s in (-1, 1):
        SP.cut(SP.ellip((cx + s * 0.14, 1.07, 0.18), (0.09, 0.075, 0.12), "x", seg=14))   # the sockets
    SP.cut(SP.ellip((cx, 0.88, 0.02), (0.05, 0.05, 0.08), "x", seg=10))
    for s in (-1, 1):
        SP.ellip((cx + s * 0.14, 1.06, 0.27), (0.045, 0.04, 0.03), "coals_glow", seg=10)  # the embers
    SP.box(cx - 0.17, 0.62, 0.12, cx + 0.17, 0.72, 0.42, "bone", bevel=0.04)        # the jaw, a little open
    for s in (-1, 1):                                                                # the fangs
        SP.prism([(cx + s * 0.13, 0.8), (cx + s * 0.07, 0.8), (cx + s * 0.1, 0.62)], 0.06, 0.12, "bone")
        SP.prism([(cx + s * 0.12, 0.66), (cx + s * 0.06, 0.66), (cx + s * 0.09, 0.8)], 0.1, 0.15, "bone")
    for k in range(-2, 3):
        SP.box(cx + k * 0.05 - 0.018, 0.74, 0.04, cx + k * 0.05 + 0.018, 0.8, 0.1, "bone", bevel=0.0)
    for s in (-1, 1):                                                                # the horns
        KS.tube("horn", [(cx + s * 0.26, 1.36, 0.45), (cx + s * 0.55, 1.5, 0.42), (cx + s * 0.78, 1.72, 0.32),
                         (cx + s * 0.8, 1.97, 0.18)], [0.12, 0.09, 0.06, 0.025], "stone_dark", seg=14)
        for k in range(3):
            t = 0.2 + k * 0.2
            SP.torus((cx + s * (0.3 + t * 0.6), 1.38 + t * 0.25, 0.44 - t * 0.05), 0.1 - t * 0.06, 0.012, "iron_dark",
                     normal=(1, 0.5 * s, 0), seg=14, tseg=5)


GUILD = ["guild_board", "guild_counter", "trestle_table", "guild_chair", "round_table", "tavern_bar", "keg_rack",
         "bar_stool", "guild_chandelier", "trophy_skull"]
CIVIC += GUILD


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for n in (args or CIVIC):
        SP.build(n)
