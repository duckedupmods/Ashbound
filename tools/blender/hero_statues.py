"""The Hall of Heroes' statues, sculpted the way the Moonwell Priestess was: real shapes (lathed robes and cuirasses,
ellipsoid pauldrons, a face of cranium, jaw, brow, nose and sunk eyes, hair and beards in locks), sampled 8 voxels to
the block and made into block models by tools/sculpt.py, one block per statue with a piece for every cell it fills.
Pale marble with darker marble armour and hair, gilt trim, steel blades, and the mages' fires glowing.

    blender -b -P tools/blender/hero_statues.py -- [NAME ...]        (none = all)     then  python tools/sculpt.py

Each figure is built in u = H/16 (the head about 2u), stood at the middle of its footprint, facing north (-z).
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import king_sculpt as KS  # noqa: E402
import sculpt_props as SP  # noqa: E402

SKIN, CLOTH, ARM, HAIR, TRIM, BLADE = "marble", "marble", "marble_dark", "marble_dark", "gold", "steel"
HY = 14.55                              # the head's middle, in u


class Fig:
    """A figure H blocks tall stood at (cx, cz), facing north. Points are (x, y, f) in u: x east, y up, f forward."""

    def __init__(self, H, cx, cz, shoulders=1.75):
        self.u, self.cx, self.cz, self.sh = H / 16.0, cx, cz, shoulders

    def p(self, x, y, f=0.0):
        return (self.cx + x * self.u, y * self.u, self.cz - f * self.u)

    def ell(self, c, r, mat, rot=(0, 0, 0), seg=20):
        return SP.ellip(self.p(*c), tuple(v * self.u for v in r), mat, rot=rot, seg=seg)

    def cap(self, a, b, ra, rb, mat, seg=16):
        return SP.caps(self.p(*a), self.p(*b), ra * self.u, rb * self.u, mat, seg=seg)

    def tube(self, pts, radii, mat, seg=12):
        return KS.tube("t", [self.p(*q) for q in pts], [r * self.u for r in radii], mat, seg=seg)

    def box(self, c, h, mat, bevel=0.08, rot=(0, 0, 0)):
        return KS.rbox("b", self.p(*c), tuple(v * self.u for v in h), mat, bevel=max(0.001, bevel * self.u), rot=rot)

    def lathe(self, ys, ring, mat, n=64):
        """ring(y, t) -> (x, f) in u round the figure's axis."""
        def g(yb, t):
            x, f = ring(yb / self.u, t)
            return self.cx + x * self.u, self.cz - f * self.u
        return KS.lathe("l", [y * self.u for y in ys], g, mat, n=n)

    def plate(self, c, a, b, pts, thick, mat):
        """A flat shape: 2D outline pts (s, t) laid out from c along directions a and b (in u), thick along a x b."""
        C, A, B = Vector(self.p(*c)), Vector(_dir(a)), Vector(_dir(b))
        A.normalize()
        B.normalize()
        N = A.cross(B).normalized() * (thick * self.u / 2)
        verts = []
        for s_ in (-1, 1):
            for (s, t) in pts:
                verts.append(tuple(C + A * (s * self.u) + B * (t * self.u) + N * s_))
        n = len(pts)
        faces = [tuple(range(n))[::-1], tuple(range(n, 2 * n))] + [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
        return SP.mesh(verts, faces, mat)

    # ---------------------------------------------------------------- the body

    def legs(self, mat=CLOTH, boot=ARM, armoured=False, spread=0.78):
        for sx in (-1, 1):
            hip, knee, ank = (sx * 0.72, 8.0, 0.0), (sx * spread, 4.4, 0.2), (sx * spread * 1.04, 0.9, 0.05)
            self.cap(hip, knee, 0.68, 0.5, boot if armoured else mat)
            self.ell(knee, (0.52, 0.5, 0.56), boot)
            self.cap(knee, ank, 0.5, 0.34, boot if armoured else mat)
            self.cap((sx * spread, 3.7, 0.18), ank, 0.54, 0.42, boot)            # the boot or greave
            self.ell((sx * spread * 1.04, 0.4, 0.42), (0.44, 0.4, 0.86), boot)    # the foot
            if armoured:
                self.ell((sx * spread, 4.5, 0.55), (0.34, 0.42, 0.22), TRIM)      # the knee cop's boss

    def torso(self, mat, ridge=False, female=False, bare=False):
        w = 0.86 if female else 1.0

        def ring(y, t):
            rx = (1.25 + 0.55 * KS.smooth(8.4, 11.4, y) - 0.62 * KS.smooth(12.0, 13.1, y)) * w
            rf = 0.82 + 0.28 * KS.smooth(8.6, 11.0, y) - 0.45 * KS.smooth(12.0, 13.1, y)
            x, f = rx * math.cos(t), rf * math.sin(t)
            if ridge and f > 0:
                f += 0.14 * math.exp(-(x / 0.35) ** 2) * KS.smooth(9.0, 10.5, y)
            return x, f
        self.lathe([8.2 + i * 0.25 for i in range(20)], ring, mat)
        if bare:                                                                  # chest and belly, carved
            for sx in (-1, 1):
                self.ell((sx * 0.62, 11.0, 0.72), (0.66, 0.5, 0.36), SKIN)
                for k in range(3):
                    self.ell((sx * 0.27, 9.9 - k * 0.48, 0.78), (0.25, 0.2, 0.16), SKIN)
        self.cap((0, 12.8, 0.05), (0, 13.8, 0.12), 0.42, 0.4, SKIN)              # the neck

    def belt(self, mat=ARM, buckle=TRIM):
        self.lathe([8.25, 8.55, 8.85], lambda y, t: (1.34 * math.cos(t), 0.93 * math.sin(t)), mat)
        self.box((0, 8.55, 0.95), (0.28, 0.24, 0.08), buckle)

    def skirt(self, mat, top=8.6, bottom=5.8, flare=1.6, plates=False):
        def ring(y, t):
            k = (top - y) / (top - bottom)
            r = 1.32 + (flare - 1.32) * k
            if plates:
                r += 0.05 * (1 if math.sin(8 * t) > 0 else -1) * k
            else:
                r += 0.06 * math.sin(11 * t) * k
            return r * math.cos(t), r * math.sin(t) * 0.82
        self.lathe([bottom + i * 0.3 for i in range(int((top - bottom) / 0.3) + 1)], ring, mat)
        if plates:
            self.lathe([bottom, bottom + 0.25], lambda y, t: (flare * 1.03 * math.cos(t), flare * 1.03 * math.sin(t) * 0.82), TRIM)

    def robe(self, mat=CLOTH, hem=2.1, waist=1.3, top=9.0, depth=0.85, pleats=7, trim=TRIM):
        def ring(y, t):
            k = KS.smooth(0, top, y)
            r = waist + (hem - waist) * (1 - k) ** 1.4 + 0.16 * (1 - k) ** 0.7 * math.cos(pleats * t)
            return r * math.cos(t), r * math.sin(t) * depth
        self.lathe([0.0, 0.3] + [0.6 + i * 0.6 for i in range(int(top / 0.6))] + [top], ring, mat, n=80)
        self.lathe([0.0, 0.4], lambda y, t: tuple(v * 1.04 for v in ring(y, t)), trim, n=80)

    def pauldrons(self, mat=ARM, big=1.0):
        for sx in (-1, 1):
            for i in range(3):
                self.ell((sx * (self.sh + 0.2 * i), 12.5 - 0.42 * i, 0.0), ((0.95 - 0.05 * i) * big, 0.46 * big, (1.0 - 0.05 * i) * big),
                         mat, rot=(0, 0, sx * (24 + i * 9)))
            self.ell((sx * (self.sh + 0.15), 12.9, 0.0), (0.3, 0.2, 0.3), TRIM)

    def cloak(self, mat=CLOTH, bottom=0.5, depth=1.0, top=12.9):
        """From behind the shoulders down to bottom, pleated, thick."""
        n, ys = 48, [bottom + (top - bottom) * i / 14 for i in range(15)]

        def at(y, i):
            a = math.pi * (1.08 + 0.84 * i / (n - 1))
            k = (top - y) / (top - bottom)
            r = 1.75 + 0.75 * k ** 1.2 + 0.12 * math.sin(9 * a) * k
            return r * math.cos(a), r * math.sin(a) * 0.62 * depth - 0.15
        verts, faces = [], []
        for y in ys:
            for i in range(n):
                x, f = at(y, i)
                verts.append((x, y, f))
        inner = []
        for (x, y, f) in verts:
            l = math.hypot(x, f + 0.15) or 1
            inner.append((x - x / l * 0.22, y, f - (f + 0.15) / l * 0.22))
        allv = [self.p(*v) for v in verts + inner]
        m, off = len(ys), len(verts)
        for j in range(m - 1):
            for i in range(n - 1):
                a, b = j * n + i, j * n + i + 1
                faces += [(a, b, b + n, a + n), (off + a, off + a + n, off + b + n, off + b)]
        for j in range(m - 1):
            for i in (0, n - 1):
                a, b = j * n + i, (j + 1) * n + i
                faces.append((a, b, off + b, off + a) if i == 0 else (a, off + a, off + b, b))
        for i in range(n - 1):
            for a, b in ((i, i + 1), ((m - 1) * n + i, (m - 1) * n + i + 1)):
                faces.append((a, off + a, off + b, b) if a < n else (a, b, off + b, off + a))
        SP.mesh(allv, faces, mat)
        for sx in (-1, 1):
            self.ell((sx * 1.05, 12.6, 0.55), (0.24, 0.24, 0.14), TRIM)          # the clasps

    def arm(self, sh, el, wr, mat=ARM, fore=None, r=1.0, cuff=None):
        self.cap(sh, el, 0.46 * r, 0.38 * r, mat)
        self.ell(el, (0.4 * r, 0.4 * r, 0.4 * r), mat)
        self.cap(el, wr, 0.38 * r, 0.3 * r, fore or mat)
        if cuff:
            d = Vector(wr) - Vector(el)
            c = Vector(wr) - d * 0.12
            self.cap(tuple(c - d * 0.1), tuple(c + d * 0.06), 0.36 * r, 0.38 * r, cuff)

    def fist(self, at, mat=SKIN, r=1.0):
        self.ell(at, (0.34 * r, 0.4 * r, 0.36 * r), mat)

    def open_hand(self, at, up=(0, 1, 0), mat=SKIN):
        """A flat hand, fingers along `up`, palm toward f+ unless up is vertical (then palm up)."""
        U = Vector(up).normalized()
        self.ell(at, (0.3, 0.34, 0.14) if abs(U.y) > 0.7 and up[2] == 0 else (0.3, 0.14, 0.34), mat)
        for k in range(4):
            off = Vector(((k - 1.5) * 0.15, 0, 0))
            a = Vector(at) + off + U * 0.25
            self.cap(tuple(a), tuple(a + U * 0.42), 0.075, 0.065, mat, seg=8)
        side = Vector((-0.28, 0, 0))
        self.cap(tuple(Vector(at) + side), tuple(Vector(at) + side * 1.6 + U * 0.25), 0.085, 0.07, mat, seg=8)

    # ---------------------------------------------------------------- the head

    def face(self, female=False):
        s = 0.92 if female else 1.0
        self.ell((0, HY + 0.15, -0.05), (0.78 * s, 0.95 * s, 0.84 * s), SKIN)              # the cranium
        self.ell((0, HY - 0.45, 0.2), (0.64 * s, 0.6 * s, 0.62 * s), SKIN)                 # the jaw
        self.cap((-0.48 * s, HY + 0.22, 0.72 * s), (0.48 * s, HY + 0.22, 0.72 * s), 0.17, 0.17, SKIN)   # the brow
        self.cap((0, HY + 0.18, 0.82 * s), (0, HY - 0.34, 0.98 * s), 0.12, 0.18, SKIN)     # the nose
        for sx in (-1, 1):
            self.ell((sx * 0.4 * s, HY - 0.25, 0.62 * s), (0.2, 0.17, 0.16), SKIN)         # the cheekbones
            self.ell((sx * 0.76 * s, HY, 0.0), (0.12, 0.28, 0.18), SKIN)                   # the ears
            SP.cut(self.ell((sx * 0.3 * s, HY - 0.02, 0.86 * s), (0.2, 0.15, 0.18), SKIN))  # the eye sockets
        SP.cut(self.box((0, HY - 0.66, 0.8 * s), (0.2, 0.04, 0.12), SKIN))                 # the mouth

    def hair(self, style="short", female=False):
        """Before the face: the face paints over it in front."""
        s = 0.92 if female else 1.0
        self.ell((0, HY + 0.42, -0.22), (0.84 * s, 0.78 * s, 0.82 * s), HAIR)
        if style in ("long", "braids"):
            def ring(y, t):
                k = (HY - y) / (HY - 11.2)
                r = 0.82 + 0.25 * k
                f = (r * math.sin(t) if math.sin(t) < 0 else 0.2 * math.sin(t)) - 0.3
                return r * math.cos(t) + 0.05 * math.sin(7 * t), f + 0.06 * math.sin(11 * t) * k
            self.lathe([11.2 + i * 0.35 for i in range(int((HY + 0.6 - 11.2) / 0.35) + 1)], ring, HAIR, n=48)
        if style == "braids":
            for sx in (-1, 1):
                for k in range(5):
                    self.ell((sx * 0.62, HY - 0.9 - k * 0.45, 0.3 - 0.05 * k), (0.2, 0.26, 0.2), HAIR)
                self.ell((sx * 0.62, HY - 3.2, 0.06), (0.16, 0.14, 0.16), TRIM)

    def beard(self, long=False):
        n = 4.2 if long else 2.0
        self.ell((0, HY - 0.85, 0.42), (0.62, 0.62, 0.42), HAIR)
        for k in range(1, int(n / 0.5)):
            w = 0.58 * (1 - 0.6 * k / (n / 0.5))
            self.ell((0, HY - 0.85 - k * 0.5, 0.55 + 0.08 * min(k, 3)), (w, 0.36, 0.34), HAIR)
        for sx in (-1, 1):                                                                 # the moustache
            self.tube([(sx * 0.08, HY - 0.48, 0.97), (sx * 0.34, HY - 0.56, 0.9), (sx * 0.5, HY - 0.8, 0.78)], [0.1, 0.1, 0.07], HAIR)

    def helm(self, crest="plume", slit=True):
        def ring(y, t):
            k = KS.smooth(HY + 0.4, HY + 1.15, y)
            r = 0.96 * math.sqrt(max(0.0, 1 - k * k)) if y > HY + 0.4 else 0.96
            return r * math.cos(t), r * math.sin(t) * 1.02
        self.lathe([HY - 1.05, HY - 0.6] + [HY + i * 0.12 for i in range(10)] + [HY + 1.16], ring, ARM, n=56)
        if slit:
            SP.cut(self.box((0, HY + 0.02, 0.95), (0.62, 0.07, 0.2), ARM))
            SP.cut(self.box((0, HY - 0.32, 0.95), (0.07, 0.3, 0.2), ARM))
        self.lathe([HY - 1.05, HY - 0.85], lambda y, t: (1.0 * math.cos(t), 1.04 * math.sin(t)), TRIM, n=56)
        if crest == "plume":
            self.tube([(0, HY + 1.05, 0.55), (0, HY + 1.45, 0.0), (0, HY + 1.3, -0.7), (0, HY + 0.6, -1.25)], [0.2, 0.3, 0.28, 0.16], CLOTH)
        elif crest == "across":
            self.tube([(-0.98, HY + 0.4, -0.05), (-0.62, HY + 1.25, -0.05), (0, HY + 1.5, -0.05), (0.62, HY + 1.25, -0.05),
                       (0.98, HY + 0.4, -0.05)], [0.18, 0.24, 0.26, 0.24, 0.18], TRIM)

    def hood(self, up=True):
        """Up: a cowl round the head (made before the face, its front cut open). Down: a collar on the shoulders."""
        self.lathe([12.3, 12.7, 13.1], lambda y, t: ((1.35 - (y - 12.3) * 0.5) * math.cos(t), (1.0 - (y - 12.3) * 0.4) * math.sin(t)), CLOTH)
        if up:
            self.ell((0, HY + 0.12, -0.18), (1.02, 1.18, 1.08), CLOTH)
            self.tube([(0, HY + 1.1, -0.4), (0, HY + 0.9, -1.0), (0, HY + 0.2, -1.25)], [0.3, 0.22, 0.12], CLOTH)
            SP.cut(self.ell((0, HY - 0.12, 0.78), (0.66, 0.86, 0.5), CLOTH))

    def wizard_hat(self):
        self.ell((0, HY + 0.78, -0.05), (1.6, 0.12, 1.55), CLOTH)
        self.lathe([HY + 0.8, HY + 1.0], lambda y, t: (0.9 * math.cos(t), 0.92 * math.sin(t) - 0.05), TRIM, n=48)
        self.tube([(0, HY + 0.85, -0.05), (0, HY + 1.9, -0.22), (0.12, HY + 2.9, -0.62), (0.32, HY + 3.6, -1.15)],
                  [0.88, 0.58, 0.32, 0.1], CLOTH, seg=24)

    def circlet(self, gem="crystal"):
        self.lathe([HY + 0.38, HY + 0.56], lambda y, t: (0.83 * math.cos(t), 0.89 * math.sin(t) - 0.04), TRIM, n=48)
        self.ell((0, HY + 0.5, 0.88), (0.13, 0.15, 0.08), gem)

    def crown(self):
        CY = HY + 0.75
        self.lathe([CY - 0.18, CY + 0.18], lambda y, t: (0.86 * math.cos(t), 0.92 * math.sin(t) - 0.05), TRIM, n=56)
        for i in range(7):
            a = math.pi / 2 + (i - 3) * 0.62
            bx, bf = 0.86 * math.cos(a), 0.92 * math.sin(a) - 0.05
            tip = 0.75 if i == 3 else 0.55 if i in (2, 4) else 0.42
            self.cap((bx, CY + 0.1, bf), (bx * 1.06, CY + 0.1 + tip, bf * 1.06), 0.12, 0.05, TRIM, seg=8)
            self.ell((bx * 1.07, CY + 0.16 + tip, bf * 1.07), (0.1, 0.1, 0.1), TRIM)


def _dir(v):
    """A direction given in (x, y, f) u-space, as a game vector."""
    return (v[0], v[1], -v[2])


# ---------------------------------------------------------------- arms and armaments

def greatsword(F, pommel, down=True, length=8.0, w=0.36, guard=1.15):
    """A greatsword through `pommel`, its blade running down (point to the ground) or up."""
    x, y, f = pommel
    sg = -1 if down else 1
    F.ell((x, y, f), (0.26, 0.22, 0.26), TRIM)
    F.cap((x, y - sg * 0.1, f), (x, y + sg * 1.2, f), 0.15, 0.15, ARM)                    # the grip
    gy = y + sg * 1.3
    F.cap((x - guard, gy, f), (x + guard, gy, f), 0.16, 0.16, TRIM)
    for sx in (-1, 1):
        F.ell((x + sx * guard * 1.05, gy - sg * 0.12, f), (0.18, 0.22, 0.18), TRIM)
    F.ell((x, gy, f + 0.1), (0.18, 0.18, 0.1), TRIM)
    L = length
    F.plate((x, gy + sg * 0.12, f), (0, sg, 0), (1, 0, 0),
            [(0, -w), (L * 0.92, -w * 0.82), (L, 0), (L * 0.92, w * 0.82), (0, w)], 0.16, BLADE)
    SP.cut(F.box((x, gy + sg * L * 0.4, f + 0.08), (0.06, L * 0.32, 0.05), BLADE))       # the fuller


def sword_up(F, grip, length=5.4, w=0.28):
    x, y, f = grip
    F.ell((x, y - 0.65, f), (0.2, 0.18, 0.2), TRIM)
    F.cap((x, y - 0.6, f), (x, y + 0.55, f), 0.13, 0.13, ARM)
    F.cap((x - 0.8, y + 0.65, f), (x + 0.8, y + 0.65, f), 0.13, 0.13, TRIM)
    F.plate((x, y + 0.75, f), (0, 1, 0), (1, 0, 0), [(0, -w), (length * 0.9, -w * 0.8), (length, 0), (length * 0.9, w * 0.8), (0, w)],
            0.13, BLADE)


def kite_shield(F, c, h=5.6, w=2.8, emblem="cross"):
    pts = []
    for k in range(13):                                            # the top, gently curved
        a = math.pi * k / 12
        pts.append((math.cos(a) * w / 2, h * 0.32 + math.sin(a) * 0.35))
    pts = pts[::-1]
    pts = [(-w / 2, h * 0.32), (-w / 2 * 0.92, -h * 0.05), (-w * 0.25, -h * 0.45), (0, -h * 0.68), (w * 0.25, -h * 0.45),
           (w / 2 * 0.92, -h * 0.05), (w / 2, h * 0.32)] + pts[1:-1]
    x, y, f = c
    F.plate((x, y, f - 0.04), (1, 0, 0), (0, 1, 0), [(a * 1.07, b * 1.05) for a, b in pts], 0.2, TRIM)
    F.plate((x, y, f), (1, 0, 0), (0, 1, 0), pts, 0.24, ARM)
    F.ell((x, y + h * 0.05, f + 0.16), (0.42, 0.42, 0.2), TRIM)
    if emblem == "cross":
        F.box((x, y + h * 0.02, f + 0.13), (0.14, h * 0.4, 0.06), TRIM)
        F.box((x, y + h * 0.16, f + 0.13), (w * 0.38, 0.14, 0.06), TRIM)


def round_shield(F, c, r=1.5, back=True):
    x, y, f = c
    d = -0.3 if back else 0.3
    SP.cyl(F.p(x, y, f), F.p(x, y, f + d), r * F.u, TRIM, seg=40)
    SP.cyl(F.p(x, y, f + d * 0.1), F.p(x, y, f + d * 1.15), r * 0.92 * F.u, ARM, seg=40)
    F.ell((x, y, f + d * 1.3), (0.36, 0.36, 0.22), TRIM)


def staff(F, foot, top, mat=ARM):
    a, b = Vector(foot), Vector(top)
    pts = [tuple(a.lerp(b, k / 5) + Vector((0.06 * math.sin(k * 2.1), 0, 0.05 * math.cos(k * 1.7)))) for k in range(6)]
    F.tube(pts, [0.16, 0.15, 0.15, 0.15, 0.16, 0.2], mat)
    return b


def staff_head(F, top, gem="crystal", size=1.0):
    x, y, f = top
    for k in range(4):                                             # a claw of four tines round the stone
        a = k * math.pi / 2 + math.pi / 4
        F.tube([(x, y, f), (x + math.cos(a) * 0.45 * size, y + 0.5 * size, f + math.sin(a) * 0.45 * size),
                (x + math.cos(a) * 0.3 * size, y + 1.15 * size, f + math.sin(a) * 0.3 * size)], [0.12, 0.1, 0.06], TRIM)
    SP.crystal(F.p(x, y + 0.35 * size, f), 1.1 * size * F.u, 0.36 * size * F.u, gem)


def warhammer(F, top, foot):
    x, y, f = top
    F.cap((x, foot, f), (x, y, f), 0.17, 0.17, ARM)
    F.ell((x, y + 0.15, f), (0.22, 0.2, 0.22), TRIM)
    hy = foot + 0.7
    F.box((x, hy, f), (1.15, 0.68, 0.62), ARM, bevel=0.12)
    for sx in (-1, 1):
        F.box((x + sx * 1.05, hy, f), (0.14, 0.74, 0.68), TRIM, bevel=0.05)
    F.lathe([hy + 0.7, hy + 1.6], lambda yy, t: (x + 0.24 * (1 - (yy - hy - 0.7) / 0.9) * math.cos(t),
                                                f + 0.24 * (1 - (yy - hy - 0.7) / 0.9) * math.sin(t)), TRIM)


def longbow(F, x, y0, y1, f0, bulge=0.6):
    pts, radii = [], []
    for k in range(9):
        t = k / 8
        y = y0 + (y1 - y0) * t
        pts.append((x, y, f0 + bulge * math.sin(math.pi * t) ** 0.7))
        radii.append(0.1 + 0.08 * math.sin(math.pi * t))
    F.tube(pts, radii, ARM)
    F.cap((x, y0, f0), (x, y1, f0), 0.08, 0.08, CLOTH, seg=6)                            # the string
    F.cap((x, (y0 + y1) / 2 - 0.4, f0 + bulge), (x, (y0 + y1) / 2 + 0.4, f0 + bulge), 0.16, 0.16, TRIM)


def arrow(F, a, b):
    F.cap(a, b, 0.07, 0.07, ARM, seg=6)
    B, A = Vector(b), Vector(a)
    d = (B - A).normalized()
    F.cap(tuple(B), tuple(B + d * 0.45), 0.16, 0.02, BLADE, seg=6)
    for k in range(3):
        F.box(tuple(A + d * (0.2 + 0.15 * k)), (0.16, 0.12, 0.03), CLOTH, bevel=0.02)


def spear(F, x, f, y0, y1):
    F.cap((x, y0, f), (x, y1 - 1.6, f), 0.13, 0.13, ARM)
    F.lathe([y1 - 1.75, y1 - 1.45], lambda yy, t: (x + 0.2 * math.cos(t), f + 0.2 * math.sin(t)), TRIM)
    F.plate((x, y1 - 1.5, f), (0, 1, 0), (1, 0, 0), [(0, -0.12), (0.5, -0.38), (1.1, -0.3), (1.6, 0), (1.1, 0.3), (0.5, 0.38), (0, 0.12)],
            0.12, BLADE)


def dagger(F, hilt, tip, w=0.17):
    A, B = Vector(hilt), Vector(tip)
    d = B - A
    L = d.length
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 1e-3:
        side = Vector((1, 0, 0))
    F.cap(tuple(A - d.normalized() * 0.55), tuple(A), 0.1, 0.1, ARM, seg=8)
    F.cap(tuple(A - side.normalized() * 0.42), tuple(A + side.normalized() * 0.42), 0.09, 0.09, TRIM, seg=8)
    F.plate(hilt, tuple(d), tuple(side), [(0, -w), (L * 0.85, -w * 0.7), (L, 0), (L * 0.85, w * 0.7), (0, w)], 0.1, BLADE)


def great_axe(F, grip, over, top):
    """A great double axe from the grip, over the shoulder point, its head at top."""
    F.tube([grip, over, top], [0.16, 0.16, 0.17], ARM)
    G_, T_ = Vector(grip), Vector(top)
    d = (T_ - G_).normalized()
    perp = d.cross(Vector((1, 0, 0))).normalized()                 # in the plane of the haft and up/forward
    F.ell(top, (0.24, 0.3, 0.24), TRIM)
    for sg in (-1, 1):
        F.plate(top, tuple(perp * sg), tuple(d), [(0.15, -0.35), (0.7, -0.62), (1.25, -0.95), (1.4, 0), (1.25, 0.95), (0.7, 0.62), (0.15, 0.35)],
                0.14, BLADE)
    F.cap(top, tuple(T_ + d * 0.55), 0.12, 0.04, TRIM)


def open_book(F, c):
    x, y, f = c
    for sx in (-1, 1):
        F.box((x + sx * 0.36, y, f), (0.38, 0.05, 0.3), ARM, bevel=0.02, rot=(0, 0, -sx * 12))
        F.box((x + sx * 0.34, y + 0.07, f), (0.34, 0.04, 0.27), "paper", bevel=0.01, rot=(0, 0, -sx * 12))


def orb(F, c, r, mat):
    F.ell(c, (r, r, r), mat, seg=24)


# ================================================================ the statues

def plate_body(F, cloak=True, tabard=True, helm=None, beard=False, hair="short"):
    F.legs(armoured=True)
    F.skirt(ARM, plates=True)
    F.torso(ARM, ridge=not tabard)
    F.belt()
    if tabard:                                                     # over the breastplate, then over the tassets
        F.box((0, 10.2, 1.18), (0.55, 1.75, 0.08), CLOTH, bevel=0.03)
        F.box((0, 6.5, 1.4), (0.58, 2.1, 0.08), CLOTH, bevel=0.03)
        F.box((0, 4.45, 1.42), (0.62, 0.1, 0.08), TRIM, bevel=0.02)
        F.ell((0, 10.8, 1.28), (0.3, 0.3, 0.08), TRIM)
        for k in range(8):
            a = k * math.pi / 4
            F.cap((0.32 * math.cos(a), 10.8 + 0.32 * math.sin(a), 1.28), (0.62 * math.cos(a), 10.8 + 0.62 * math.sin(a), 1.26), 0.08, 0.05, TRIM, seg=6)
    F.lathe([12.6, 13.0, 13.4], lambda y, t: ((0.95 - (y - 12.6) * 0.45) * math.cos(t), (0.8 - (y - 12.6) * 0.4) * math.sin(t)), ARM)   # gorget
    F.pauldrons()
    if cloak:
        F.cloak()
    if helm:
        F.helm(crest=helm)
    else:
        F.hair(hair)
        F.face()
        if beard:
            F.beard()


def robed_body(F, female=False, hood=None, beard=False, long_beard=False, hair="long", depth=0.85, hem=2.1):
    F.robe(depth=depth, hem=hem)
    F.torso(CLOTH, female=female)
    F.belt(CLOTH)
    F.box((0, 6.0, 1.42 * depth + 0.03), (0.3, 3.0, 0.06), TRIM, bevel=0.02)            # the stole down the front
    if hood == "up":
        F.hood(True)
        F.face(female)
        if beard:
            F.beard(long_beard)
    else:
        if hood == "down":
            F.hood(False)
        F.hair(hair, female)
        F.face(female)
        if beard:
            F.beard(long_beard)


def leather_body(F, hood=None, cape=True):
    F.legs(mat=CLOTH, boot=ARM)
    F.skirt(CLOTH, top=8.6, bottom=6.3, flare=1.5)
    F.torso(CLOTH)
    F.belt()
    for sx in (-1, 1):
        F.box((sx * 0.9, 8.2, 0.85), (0.22, 0.26, 0.14), ARM, bevel=0.05)              # pouches
    F.tube([(-1.2, 12.4, 0.75), (0, 10.8, 1.0), (1.25, 9.0, 0.7)], [0.12, 0.12, 0.12], ARM)   # a strap across
    if cape:
        F.cloak(bottom=6.5)
    if hood == "up":
        F.hood(True)
        F.face()
    else:
        if hood == "down":
            F.hood(False)
        F.hair("short")
        F.face()


@SP.prop("hero_paladin", 5, 14, 4, V=12)
def hero_paladin():
    F = Fig(12, 2.5, 2.0)
    plate_body(F, beard=True)
    for sx in (-1, 1):
        F.arm((sx * 1.75, 12.3, 0), (sx * 2.15, 9.9, 0.55), (sx * 0.45, 9.05, 1.5), cuff=TRIM)
        F.fist((sx * 0.24, 9.05, 1.72), ARM)
    greatsword(F, (0, 9.75, 1.75), down=True, length=8.0)


@SP.prop("hero_shield", 5, 14, 4, V=12)
def hero_shield():
    F = Fig(12, 2.5, 2.0)
    plate_body(F, helm="plume", tabard=False)
    F.arm((-1.75, 12.3, 0), (-2.05, 10.0, 0.85), (-1.05, 9.3, 1.55), cuff=TRIM)
    F.fist((-0.95, 9.35, 1.7), ARM)
    kite_shield(F, (-0.85, 7.7, 2.05))
    F.arm((1.75, 12.3, 0), (2.3, 10.2, 0.6), (1.7, 10.4, 1.45), cuff=TRIM)
    F.fist((1.6, 10.6, 1.62), ARM)
    sword_up(F, (1.6, 10.6, 1.62))


@SP.prop("hero_hammer", 5, 14, 4, V=12)
def hero_hammer():
    F = Fig(12, 2.5, 2.0)
    plate_body(F, cloak=False, tabard=False, beard=True)
    F.arm((1.75, 12.3, 0), (2.0, 10.4, 0.9), (0.35, 9.55, 1.5), cuff=TRIM)
    F.arm((-1.75, 12.3, 0), (-2.0, 10.0, 0.9), (-0.35, 8.85, 1.5), cuff=TRIM)
    F.fist((0.05, 9.6, 1.6), ARM)
    F.fist((-0.05, 8.9, 1.6), ARM)
    warhammer(F, (0, 10.2, 1.6), 0.15)


@SP.prop("hero_bow", 5, 14, 4, V=12)
def hero_bow():
    F = Fig(12, 2.5, 2.0)
    leather_body(F, hood="down")
    SP.cyl(F.p(0.85, 8.6, -1.05), F.p(-0.35, 13.2, -0.95), 0.36 * F.u, ARM, seg=20)     # the quiver
    for k in range(4):
        F.cap((-0.25 + k * 0.14, 13.0, -0.95), (-0.45 + k * 0.16, 14.1, -0.95), 0.06, 0.06, ARM, seg=6)
        F.box((-0.45 + k * 0.16, 14.0, -0.95), (0.05, 0.22, 0.14), CLOTH, bevel=0.02)
    F.arm((-1.75, 12.3, 0), (-2.35, 10.3, 0.4), (-2.25, 8.8, 0.85), mat=CLOTH, cuff=ARM)
    F.fist((-2.25, 8.6, 1.0))
    longbow(F, -2.25, 2.6, 14.4, 0.5, bulge=0.55)
    F.arm((1.75, 12.3, 0), (2.2, 10.0, 0.1), (2.0, 8.1, 0.4), mat=CLOTH, cuff=ARM)
    F.fist((2.0, 7.8, 0.45))
    arrow(F, (2.0, 4.6, 0.65), (2.0, 9.6, 0.3))


@SP.prop("hero_blackmage", 5, 14, 4, V=12)
def hero_blackmage():
    F = Fig(12, 2.5, 2.0)
    robed_body(F, beard=True, long_beard=True, hair="long")
    F.wizard_hat()
    F.arm((1.75, 12.3, 0), (2.25, 10.2, 0.3), (2.0, 9.45, 0.5), mat=CLOTH)
    F.cap((2.1, 9.95, 0.42), (2.0, 9.3, 0.52), 0.42, 0.56, CLOTH)                       # the bell sleeve
    F.fist((1.95, 9.6, 0.55))
    top = staff(F, (1.95, 0.1, 0.5), (1.95, 15.4, 0.5))
    staff_head(F, top, "witchfire")
    F.arm((-1.75, 12.3, 0), (-2.1, 10.6, 0.8), (-1.4, 10.9, 1.85), mat=CLOTH)
    F.cap((-1.85, 10.7, 1.15), (-1.45, 10.9, 1.8), 0.42, 0.55, CLOTH)
    F.open_hand((-1.3, 11.05, 2.05))
    orb(F, (-1.3, 11.95, 2.15), 0.55, "flame")


@SP.prop("hero_priestess", 5, 14, 4, V=12)
def hero_priestess():
    F = Fig(12, 2.5, 2.0, shoulders=1.55)
    robed_body(F, female=True, hair="long")
    F.circlet("sun_glow")
    for sx in (-1, 1):
        F.arm((sx * 1.55, 12.3, 0), (sx * 1.8, 10.0, 0.6), (sx * 0.38, 9.4, 1.25), mat=CLOTH)
        F.cap((sx * 1.2, 9.7, 0.95), (sx * 0.5, 9.4, 1.25), 0.36, 0.48, CLOTH)
        F.fist((sx * 0.22, 9.45 + (0.35 if sx > 0 else 0), 1.38))
    F.cap((0, 5.6, 1.38), (0, 12.0, 1.38), 0.12, 0.12, TRIM)                             # the sceptre
    SP.torus(F.p(0, 12.75, 1.38), 0.6 * F.u, 0.1 * F.u, TRIM, normal=(0, 0, 1))
    orb(F, (0, 12.75, 1.38), 0.36, "sun_glow")
    for k in range(8):
        a = k * math.pi / 4
        F.cap((0.68 * math.cos(a), 12.75 + 0.68 * math.sin(a), 1.38), (0.95 * math.cos(a), 12.75 + 0.95 * math.sin(a), 1.38),
              0.07, 0.03, TRIM, seg=6)


@SP.prop("hero_rogue", 5, 14, 4, V=12)
def hero_rogue():
    F = Fig(12, 2.5, 2.0)
    leather_body(F, hood="up")
    F.arm((1.75, 12.3, 0), (1.6, 10.3, 0.95), (-0.45, 11.2, 1.45), mat=CLOTH, cuff=ARM)
    F.arm((-1.75, 12.3, 0), (-1.6, 10.3, 0.95), (0.45, 11.25, 1.3), mat=CLOTH, cuff=ARM)
    F.fist((-0.62, 11.3, 1.58))
    F.fist((0.62, 11.35, 1.42))
    dagger(F, (-0.62, 11.0, 1.7), (0.95, 10.0, 1.9))                                    # reverse grip, along the forearm
    dagger(F, (0.62, 11.05, 1.55), (-0.95, 10.05, 1.75))
    F.box((1.1, 7.6, 0.75), (0.1, 0.65, 0.12), ARM, bevel=0.03, rot=(0, 0, 18))          # an empty sheath


@SP.prop("hero_spear", 5, 14, 4, V=12)
def hero_spear():
    F = Fig(12, 2.5, 2.0)
    plate_body(F, cloak=False, tabard=False, helm="across")
    round_shield(F, (0, 10.4, -1.15), r=1.5)
    F.arm((1.75, 12.3, 0), (2.3, 10.6, 0.35), (2.05, 11.4, 0.55), cuff=TRIM)
    F.fist((2.0, 11.6, 0.6), ARM)
    spear(F, 2.0, 0.6, 0.05, 18.3)
    F.arm((-1.75, 12.3, 0), (-2.5, 10.4, -0.2), (-1.5, 8.95, 0.3), cuff=TRIM)
    F.fist((-1.35, 8.85, 0.4), ARM)


@SP.prop("hero_summoner", 5, 14, 4, V=12)
def hero_summoner():
    F = Fig(12, 2.5, 2.0)
    robed_body(F, hood="down", hair="long")
    F.circlet("crystal_cyan")
    F.arm((-1.75, 12.3, 0), (-2.0, 10.0, 0.6), (-0.95, 9.9, 1.45), mat=CLOTH)
    F.cap((-1.6, 10.0, 0.95), (-1.0, 9.9, 1.45), 0.4, 0.52, CLOTH)
    F.fist((-0.8, 9.95, 1.6))
    open_book(F, (-0.6, 10.2, 1.75))
    F.arm((1.75, 12.3, 0), (2.3, 13.6, 0.5), (2.0, 15.1, 0.9), mat=CLOTH)
    F.cap((2.25, 14.0, 0.62), (2.05, 15.0, 0.88), 0.38, 0.5, CLOTH)
    F.open_hand((2.0, 15.45, 0.95))
    SP.crystal(F.p(1.95, 16.4, 1.0), 1.2 * F.u, 0.38 * F.u, "crystal_cyan")
    for dx, dy in ((-0.7, 15.9), (0.7, 16.6)):
        SP.crystal(F.p(1.95 + dx, dy, 1.0), 0.5 * F.u, 0.16 * F.u, "crystal_cyan")


@SP.prop("hero_axe", 5, 14, 4, V=12)
def hero_axe():
    F = Fig(12, 2.5, 2.0, shoulders=1.85)
    F.legs(mat=CLOTH, boot=ARM, spread=0.85)
    F.skirt(CLOTH, top=8.6, bottom=5.4, flare=1.7)
    F.torso(SKIN, bare=True)
    F.belt(ARM)
    for sx in (-1, 1):                                             # the fur mantle, in lumps
        for k in range(5):
            a = math.pi * (0.1 + 0.8 * k / 4)
            F.ell((sx * (0.6 + 0.9 * math.sin(a)), 12.6 + 0.25 * math.cos(a * 2), 0.2 - 0.9 * math.cos(a)), (0.5, 0.36, 0.5), HAIR)
    F.hair("braids")
    F.face()
    F.beard(long=True)
    F.arm((1.85, 12.3, 0), (2.25, 10.2, 0.4), (1.55, 9.4, 1.25), mat=SKIN, cuff=ARM, r=1.1)
    F.fist((1.5, 9.3, 1.35), r=1.1)
    great_axe(F, (1.5, 9.0, 1.4), (2.0, 12.95, -0.1), (2.2, 14.5, -0.72))
    F.arm((-1.85, 12.3, 0), (-2.35, 10.1, 0.0), (-2.25, 8.5, 0.3), mat=SKIN, cuff=ARM, r=1.1)
    F.fist((-2.25, 8.2, 0.35), r=1.1)


@SP.prop("hero_first", 7, 16, 4, V=12)
def hero_first():
    F = Fig(14, 3.5, 2.0)
    plate_body(F, beard=True, hair="long")
    F.crown()
    F.arm((1.75, 12.3, 0), (2.15, 10.2, 0.7), (1.25, 10.6, 1.3), cuff=TRIM)            # the sword held up at his right shoulder
    F.arm((-1.75, 12.3, 0), (-1.6, 10.2, 0.9), (0.7, 11.2, 1.35), cuff=TRIM)
    F.fist((1.1, 10.7, 1.42), ARM)
    F.fist((1.1, 11.4, 1.42), ARM)
    sword_up(F, (1.1, 11.15, 1.45), length=5.2, w=0.32)


@SP.prop("colossus_knight", 9, 23, 4, V=8)
def colossus_knight():
    F = Fig(22, 4.5, 2.0)
    plate_body(F, helm="plume", cloak=False)
    for sx in (-1, 1):
        F.arm((sx * 1.75, 12.3, 0), (sx * 2.15, 9.9, 0.5), (sx * 0.45, 9.05, 1.2), cuff=TRIM)
        F.fist((sx * 0.24, 9.05, 1.3), ARM)
    greatsword(F, (0, 9.75, 1.32), down=True, length=8.0)


@SP.prop("colossus_mage", 9, 23, 4, V=8)
def colossus_mage():
    F = Fig(22, 4.5, 2.0)
    robed_body(F, hood="up", beard=True, long_beard=True, depth=0.66)
    F.arm((1.75, 12.3, 0), (2.25, 10.2, 0.2), (2.05, 9.45, 0.45), mat=CLOTH)
    F.cap((2.15, 9.95, 0.35), (2.05, 9.3, 0.45), 0.42, 0.56, CLOTH)
    F.fist((2.05, 9.6, 0.5))
    top = staff(F, (2.05, 0.1, 0.45), (2.05, 14.9, 0.45))
    staff_head(F, top, "crystal", size=1.15)
    F.arm((-1.75, 12.3, 0), (-2.5, 11.0, 0.5), (-2.3, 12.75, 1.0), mat=CLOTH)
    F.cap((-2.45, 11.4, 0.6), (-2.3, 12.6, 0.95), 0.42, 0.56, CLOTH)
    F.open_hand((-2.28, 13.25, 1.08), up=(0, 1, 0))


HEROES = [n for n in SP.PROPS if n.startswith(("hero_", "colossus_"))]

if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for n in (args or HEROES):
        SP.build(n)
