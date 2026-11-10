"""Minecraft-style models: plain cubes, 16 texels to a block, flat pixel-art paint lit from the top. The sample the user
asked for (11/2) before the whole cast changes over: a few townsfolk as real 64x64 player skins (the vanilla body,
so Epic Fight's biped animations fit them) plus a few cubes of their own (ears, horns, beards, hats), Hob's wagon and
Bramble the horse.

Units are pixels (1/16 block), y up, the model faces +z, +x is its left. A box's texture is the vanilla net:

        top    bottom
  right front left  back           (right = the model's right side, the -x face)

    python tools/mcstyle.py [names]      -> tools/renders/mc/NAME.obj + .png, for tools/blender/mc_look.py
"""
import colorsys
import json
import math
import os
import random
import sys
from pathlib import Path

from PIL import Image

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
OUT = HERE / "renders" / "mc"
KEPT = Path("E:/Ashbound/tools/npc/kept")
SPECS = HERE / "npc_specs"
sys.path.insert(0, "E:/Ashbound/tools")
from npcparts import LOOKS  # noqa: E402


# ================================================================== colour

def rgb(hx):
    hx = hx.lstrip("#")
    return tuple(int(hx[i:i + 2], 16) for i in (0, 2, 4))


def tint(c, k):
    """lighter (k > 1) or darker (k < 1), warmer as it lightens and cooler as it darkens, like painted light"""
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c[:3]))
    l2 = max(0.0, min(1.0, l * k if k < 1 else l + (1 - l) * (k - 1) * 0.55))
    h2 = (h + (0.012 if k > 1 else -0.015) * abs(k - 1) * 3) % 1.0
    s2 = max(0.0, min(1.0, s * (1.04 if k < 1 else 0.96)))
    return tuple(int(round(v * 255)) for v in colorsys.hls_to_rgb(h2, l2, s2))


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def ramp5(base):
    """a cloth's five steps from one colour: deep shadow, shadow, base, light, highlight"""
    c = rgb(base) if isinstance(base, str) else base
    return [tint(c, 0.55), tint(c, 0.76), c, tint(c, 1.25), tint(c, 1.5)]


def look(table, key):
    v = LOOKS[table].get(key)
    if v is None:
        v = next(iter(LOOKS[table].values()))
    return [rgb(x) for x in v] if isinstance(v, list) else ramp5(v)


# ================================================================== the box kit

FACES = ("top", "bottom", "right", "front", "left", "back")


class Box:
    def __init__(self, lo, size, paint, uv=None, inflate=0.0, rot=(), pivot=None, tex=0, mirror=False):
        self.lo, self.size, self.paint, self.uv, self.inflate = lo, size, paint, uv, inflate
        self.rot, self.pivot, self.tex, self.mirror = rot, pivot if pivot is not None else lo, tex, mirror

    def net(self):
        w, h, d = (int(round(v)) for v in self.size)
        return w, h, d, 2 * d + 2 * w, d + h

    def regions(self):
        w, h, d, _, _ = self.net()
        u, v = self.uv
        return {"top": (u + d, v, w, d), "bottom": (u + d + w, v, w, d), "right": (u, v + d, d, h), "front": (u + d, v + d, w, h),
                "left": (u + d + w, v + d, d, h), "back": (u + 2 * d + w, v + d, w, h)}

    def world(self, p):
        q = [p[i] - self.pivot[i] for i in range(3)]
        for axis, deg in self.rot:
            a = math.radians(deg)
            c, s = math.cos(a), math.sin(a)
            x, y, z = q
            if axis == "x":
                q = [x, y * c - z * s, y * s + z * c]
            elif axis == "y":
                q = [x * c + z * s, y, -x * s + z * c]
            else:
                q = [x * c - y * s, x * s + y * c, z]
        q = [q[i] + self.pivot[i] for i in range(3)]
        st = getattr(self, "stoop", None)
        if st:
            (px_, py, pz), deg = st
            a = math.radians(deg)
            c, s_ = math.cos(a), math.sin(a)
            y, z = q[1] - py, q[2] - pz
            q = [q[0], y * c - z * s_ + py, y * s_ + z * c + pz]
        return q

    def quads(self):
        """(face, four corners, their uv in texels)"""
        x0, y0, z0 = (self.lo[i] - self.inflate for i in range(3))
        x1, y1, z1 = (self.lo[i] + self.size[i] + self.inflate for i in range(3))
        P = {"front": [(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)],
             "right": [(x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x0, y0, z0)],
             "left": [(x1, y1, z1), (x1, y1, z0), (x1, y0, z0), (x1, y0, z1)],
             "back": [(x1, y1, z0), (x0, y1, z0), (x0, y0, z0), (x1, y0, z0)],
             "top": [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
             "bottom": [(x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)]}
        out = []
        for f, (u, v, fw, fh) in self.regions().items():
            if fw == 0 or fh == 0:
                continue
            uv = [(u, v), (u + fw, v), (u + fw, v + fh), (u, v + fh)]
            if self.mirror:
                uv = [uv[1], uv[0], uv[3], uv[2]]
            out.append((f, [self.world(p) for p in P[f]], uv))
        return out


class Model:
    def __init__(self, name, tex_size=None):
        self.name, self.boxes, self.tex_size = name, [], tex_size

    def box(self, lo, size, paint, **kw):
        b = Box(lo, size, paint, **kw)
        self.boxes.append(b)
        return b

    def pack(self):
        """boxes without a fixed place on the sheet get one: shelf-packed nets, tallest first"""
        todo = [b for b in self.boxes if b.uv is None]
        widest = max((b.net()[3] for b in todo), default=16)
        W = self.tex_size[0] if self.tex_size else max(128, 1 << (widest - 1).bit_length(), 256 if len(todo) > 40 else 0)
        x = y = shelf = 0
        if self.tex_size:      # below the fixed ones
            y = max((b.uv[1] + b.net()[4] for b in self.boxes if b.uv is not None), default=0)
        for b in sorted(todo, key=lambda b: -b.net()[4]):
            nw, nh = b.net()[3], b.net()[4]
            if x + nw > W:
                x, y, shelf = 0, y + shelf, 0
            b.uv = (x, y)
            x += nw
            shelf = max(shelf, nh)
        H = y + shelf
        if self.tex_size:
            return self.tex_size
        return W, max(16, 1 << (H - 1).bit_length())

    def build(self, img=None):
        W, H = self.pack()
        if img is None:
            img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        px = img.load()
        for b in self.boxes:
            if b.paint is None:
                continue
            for f, (u, v, fw, fh) in b.regions().items():
                for j in range(fh):
                    for i in range(fw):
                        c = b.paint(f, i, j, fw, fh)
                        if c is not None:
                            px[u + i, v + j] = c if len(c) == 4 else tuple(c) + (255,)
        return img

    def write(self, img=None, scale=1.0, at=(0, 0, 0)):
        OUT.mkdir(parents=True, exist_ok=True)
        img = self.build(img)
        W, H = img.size
        img.save(OUT / (self.name + ".png"))
        vs, vts, fs = [], [], []
        for b in self.boxes:
            for f, ps, uv in b.quads():
                c = [sum(p[i] for p in ps) / 4 for i in range(3)]
                ctr = b.world([b.lo[i] + b.size[i] / 2 for i in range(3)])
                e1 = [ps[1][i] - ps[0][i] for i in range(3)]
                e2 = [ps[2][i] - ps[0][i] for i in range(3)]
                n = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]]
                if sum(n[i] * (c[i] - ctr[i]) for i in range(3)) < 0:
                    ps, uv = ps[::-1], uv[::-1]
                base = len(vs)
                for p, (u, v) in zip(ps, uv):
                    vs.append([(p[i] * scale + at[i]) / 16 for i in range(3)])
                    vts.append((u / W, 1 - v / H))
                fs.append([base + k for k in range(4)])
        with open(OUT / (self.name + ".obj"), "w") as fp:
            fp.write("mtllib %s.mtl\nusemtl %s\n" % (self.name, self.name))
            for v in vs:
                fp.write("v %.4f %.4f %.4f\n" % tuple(v))
            for t in vts:
                fp.write("vt %.5f %.5f\n" % t)
            for f in fs:
                fp.write("f " + " ".join("%d/%d" % (k + 1, k + 1) for k in f) + "\n")
        print(self.name, len(fs), "faces, sheet", img.size)
        return img


# ================================================================== painting helpers

def lit(face, j, fh, R, base=2):
    """vanilla-style light: tops brightest, the front as it is, sides a step down, the back and bottom darker;
    the top row of a side catches a little light, the bottom row sinks into shadow"""
    k = {"top": base + 1, "front": base, "left": base - 0.5, "right": base - 0.5, "back": base - 0.6, "bottom": base - 1}[face]
    if face not in ("top", "bottom"):
        if j == 0:
            k += 0.5
        elif j == fh - 1:
            k -= 0.6
    return R[max(0, min(len(R) - 1, int(round(k))))]


def flat(R, base=2, grain=0.0, seed=1):
    """one material, lit; grain = a few darker and lighter pixels, fixed per spot so it never shimmers"""
    def p(face, i, j, fw, fh):
        c = lit(face, j, fh, R, base)
        if grain:
            r = random.Random(hash((seed, face, i, j)) & 0xffffff).random()
            if r < grain:
                c = tint(c, 0.86)
            elif r > 1 - grain * 0.6:
                c = tint(c, 1.12)
        return c
    return p


def planks(R, run="u", every=4, seed=3):
    """boards: a dark seam every few texels across the run, a light lip above it, knots now and then"""
    def p(face, i, j, fw, fh):
        a, b = (j, i) if run == "u" else (i, j)
        c = lit(face, 0 if face == "top" else min(j, fh - 1), max(fh, 2), R, 2)
        if face in ("top", "bottom"):
            c = R[3] if face == "top" else R[1]
        if a % every == every - 1:
            return tint(c, 0.62)
        if a % every == 0:
            c = tint(c, 1.08)
        rr = random.Random(hash((seed, a // every, b // 5)) & 0xffff).random()
        if rr < 0.08 and (b % 5) == 2:
            return tint(c, 0.78)
        return tint(c, 0.94) if (b + a // every * 3) % 7 == 0 else c
    return p


# ================================================================== the townsfolk as skins

SKIN_EXTRA = {"char": ["#262226", "#36303a", "#4a4250", "#5c5464", "#6e6676", "#82788a"],
              "ash": ["#3a3a40", "#4e4e56", "#64646c", "#7a7a84", "#90909a", "#a4a4ae"],
              "moon": ["#6a7076", "#8a9298", "#a8b0b6", "#c0c8cc", "#d4dade", "#e6eaee"]}


def skin_ramp(name):
    if name in LOOKS["skin"]:
        return [rgb(x) for x in LOOKS["skin"][name]]
    return [rgb(x) for x in SKIN_EXTRA.get(name, LOOKS["skin"]["tan"])]


def hair_ramp(name):
    if name in LOOKS["hair"]:
        r = [rgb(x) for x in LOOKS["hair"][name]]
    else:
        r = ramp5("#6a6a70")
    return r + [tint(r[-1], 1.25)]


# the vanilla layout: (part, origin on the sheet, size); overlay origins second
PARTS = {"head": ((0, 0), (32, 0), (8, 8, 8)), "body": ((16, 16), (16, 32), (8, 12, 4)),
         "arm_r": ((40, 16), (40, 32), (4, 12, 4)), "arm_l": ((32, 48), (48, 48), (4, 12, 4)),
         "leg_r": ((0, 16), (0, 32), (4, 12, 4)), "leg_l": ((16, 48), (0, 48), (4, 12, 4))}
# where each part's box sits on the body, feet at y 0
PLACE = {"head": (-4, 24, -4), "body": (-4, 12, -2), "arm_r": (-8, 12, -2), "arm_l": (4, 12, -2), "leg_r": (-4.02, 0, -2), "leg_l": (0.02, 0, -2)}


def hairy(R, base=2):
    """hair and beards: strands as columns, a lighter top row, a ragged darker tip row"""
    def p(face, i, j, fw, fh):
        if face == "top":
            return R[min(len(R) - 1, base + 1)]
        if face == "bottom":
            return R[max(0, base - 1)]
        k = base if i % 2 == 0 else base - 1
        if j == 0:
            k += 1
        if j == fh - 1 and i % 2:
            k -= 1
        return R[max(0, min(len(R) - 1, k))]
    return p


def glowing(R):
    return lambda face, i, j, fw, fh: R[3] if (i + j) % 3 else R[4]


GOLD = ramp5("#d0a238")
EMBERS = [rgb("#5a1206"), rgb("#b0300a"), rgb("#ff7a1a"), rgb("#ffc04a"), rgb("#fff0b0")]
SCLERA = (238, 236, 230)


# how each kind of body is built, in pixels: body, legs, arms (w, h, d)
PLANS = {
    "adult": dict(body=(8, 12, 4), leg=(4, 12, 4), arm=(4, 12, 4)),
    "teen": dict(body=(8, 11, 4), leg=(4, 10, 4), arm=(4, 11, 4)),
    "kid": dict(body=(7, 7, 4), leg=(3.5, 6, 3.5), arm=(3, 7, 3)),
    "elder": dict(body=(8, 11, 4), leg=(4, 11, 4), arm=(4, 11, 4), hunch=14),
    "dwarf": dict(body=(10, 10, 6), leg=(5, 6, 5), arm=(4, 10, 4)),
    "elf": dict(body=(7, 13, 4), leg=(3.5, 14, 3.5), arm=(3, 13, 3)),
    "demon": dict(body=(9, 12, 5), leg=(4.5, 12, 4.5), arm=(4, 12, 4)),
}


class Folk:
    """one spec (the NPC forge's json) built as cubes with its own proportions: the body plan by race and age, a
    painted skin over it, and the cubes that make the race (ears, horns, tails, beards) or the age (a cane)"""

    def __init__(self, spec):
        self.s = s = spec
        self.race = s.get("race")
        self.age = s.get("age", "adult")
        self.skin = skin_ramp(s.get("skin", "tan"))
        self.hair = hair_ramp(s["hair"]["color"])
        o = s["outfit"]
        c = o["colors"]
        self.top = look("cloth", c.get("top", "brown"))
        self.bot = look("cloth", c.get("bottom", "brown"))
        self.acc = look("cloth", c.get("accent", "cream"))
        self.lea = ramp5(LOOKS["leather"].get(c.get("leather", "dark"), "#342317"))
        self.iris = [rgb(x) for x in LOOKS["iris"].get(s["face"].get("iris", "brown"), LOOKS["iris"]["brown"])]
        self.metal = [rgb(x) for x in LOOKS["metal"]["iron"]]
        self.slim = s.get("sex") == "f"
        if self.race == "elf":
            self.iris = [rgb("#0e4a3a"), rgb("#2aa880"), rgb("#8af0c8")]
        if self.race == "demon":
            g = s["face"].get("iris", "gold")
            self.iris = EMBERS[1:4] if g not in ("violet", "ice") else [rgb("#3a1a7a"), rgb("#9a5af0"), rgb("#e0c0ff")]
        kind = self.race if self.race in ("dwarf", "elf", "demon") and self.age not in ("kid",) else self.age
        self.plan = dict(PLANS.get(kind, PLANS["adult"]))
        if self.race == "demon" and self.age == "elder":
            self.plan["hunch"] = 14
        global G
        import mcgear as G               # what they carry and wear (it imports this module back)
        G.build(self)
        if s.get("upright"):
            self.plan.pop("hunch", None)
        self.boxes = []          # (name, lo, size, paint, inflate, rot, pivot)

    # ================================================================ the head (8 cubed for everyone)
    def head_paint(self):
        S, H, s = self.skin, self.hair, self.s
        st = s["hair"]["style"]
        f_ = s["face"]
        beard = s.get("beard") or ("beard" if self.race == "dwarf" and self.age != "kid" else None)
        side = {"bald": 0, "buzz": 3, "short": 4, "spiky": 4, "shaggy": 5, "topknot": 4, "bob": 7, "long": 8, "braid": 5,
                "ponytail": 5, "bun": 5, "twintails": 5}.get(st, 4)
        back = {"bald": 0, "buzz": 5, "short": 6, "spiky": 6, "shaggy": 7, "bob": 7, "long": 8}.get(st, 6)
        fringe = {"bald": -1, "buzz": 0, "short": 1, "spiky": 1, "shaggy": 2, "topknot": 0, "bob": 2, "long": 1, "braid": 1,
                  "ponytail": 1, "bun": 0, "twintails": 2}.get(st, 1)

        def hairpx(face, i, j):
            if face == "top":
                k = 4 if j in (2, 3) and i % 3 else 3
            elif face == "front":
                k = 3 if j == 0 else 2
            else:
                k = (2 if i % 2 == 0 else 1) + (1 if j == 0 else 0)
            if st == "buzz":
                k -= 1
            return H[max(0, min(len(H) - 1, k))]

        def p(face, i, j, fw, fh):
            c = lit(face, j, fh, S, 3)
            if face == "bottom":
                return S[2]
            if st == "bald":
                if face == "back" and 2 <= j <= 4 or face in ("left", "right") and 3 <= j <= 4 and (i < 3 if face == "right" else i > 4):
                    return hairpx(face, i, j)
                if face == "top":
                    return S[4] if (i + j) % 6 else S[5]
            if face == "top":
                return hairpx(face, i, j)
            elif face == "back" and j < back:
                return hairpx(face, i, j)
            elif face in ("left", "right"):
                frontness = i if face == "right" else 7 - i
                if 4 <= j <= 5 and 3 <= frontness <= 4 and side <= 5 and self.race not in ("elf",):
                    return S[2] if j == 5 else S[3]
                if j < side and not (frontness >= 6 and j >= fringe + 2 and side < 8):
                    return hairpx(face, i, j)
                if beard == "beard" and j >= 5 and frontness >= 4:
                    return H[2] if j < 7 else H[1]
            elif face == "front":
                if j <= fringe and not (j == fringe and fringe > 0 and i in (3, 4) and st in ("short", "long", "braid", "ponytail")):
                    return hairpx(face, i, j)
                if st == "shaggy" and j == fringe + 1 and i in (0, 2, 5, 7):
                    return hairpx(face, i, j)
                if i in (0, 7) and j < side - 1 and side >= 6:
                    return hairpx(face, i, j)
                return self.face(i, j, c, f_, beard)
            return c
        return p

    def face(self, i, j, c, f_, beard):
        S, H, I = self.skin, self.hair, self.iris
        mk = G.face(self, i, j, c)
        if mk is not None and not (j == 4 and i in (1, 2, 5, 6) and not {"patch_r", "blindfold"} & set(f_.get("marks", []))):
            return mk
        r, age = self.race, self.age
        kid = age == "kid"
        cute = kid or age == "teen" or self.slim
        # brows: heavy for dwarves, a slant for demons, a thin arch for elves
        if j == 3:
            if r == "dwarf" and 1 <= i <= 6 and i not in (3, 4):
                return H[1]
            if r == "dwarf" and i in (3, 4):
                return H[2]
            if r == "demon" and i in (1, 2, 5, 6):
                return S[0] if i in (2, 5) else c
            if r == "elf" and i in (1, 6):
                return H[1]
            if i in (1, 2, 5, 6) and not cute:
                return H[1]
        if j == 2 and r == "demon" and i in (1, 6):
            return S[0]
        if j == 2 and age == "elder" and i in (2, 3, 4, 5) and (i % 2):
            return S[2]                                             # a line across the brow
        # eyes
        if j == 4 and i in (1, 2, 5, 6):
            if r == "demon":
                return (18, 12, 14) if i in (1, 6) else I[2]       # black whites, a burning iris
            if r == "elf":
                return SCLERA if i in (1, 6) else I[1]
            return SCLERA if i in (1, 6) else I[1]
        if j == 5 and kid and i in (1, 2, 5, 6):                   # a child's eyes are two rows tall
            return I[0] if i in (2, 5) else SCLERA
        if j == 4 and kid and i in (2, 5):
            return I[2]
        if j == 3 and kid and i in (2, 5):
            return (250, 250, 250)                                  # a shine
        if self.s.get("glasses") and j in (3, 5) and i in (0, 1, 2, 5, 6, 7) or self.s.get("glasses") and j == 4 and i in (0, 3, 4, 7):
            return self.metal[4]
        # cheeks, noses, marks
        if j == 5 and r == "demon" and i in (1, 6):
            return EMBERS[2]
        if j == 5 and (f_.get("blush") or kid) and i in (1, 6):
            return mix(c, (220, 100, 96), 0.5)
        if j == 5 and age == "elder" and i in (1, 6):
            return S[2]
        if j == 5 and i in (3, 4) and (self.s.get("nose") or r == "dwarf"):
            return mix(S[3], (190, 70, 60), 0.4)
        # mouths: fangs for demons, a small smile for kids, hidden under a dwarf's beard
        if r == "demon" and j == 6:
            if i in (2, 3, 4, 5):
                return mix(S[0], (90, 20, 20), 0.4)
        if r == "demon" and j == 7 and i in (2, 5):
            return (240, 236, 226)
        if j == 6 and (i == 3 or i == 4 and not cute):
            return mix(S[1], (120, 40, 40), 0.3)
        if j == 6 and f_.get("mouth") == "smile" and i in (2, 5) and not cute:
            return S[2]
        if f_.get("freckles") and (i, j) in ((1, 5), (6, 5), (2, 6), (5, 6)):
            return S[2]
        if "soot" in f_.get("marks", []) and (i, j) in ((6, 5), (6, 6), (5, 7)):
            return S[0]
        if beard == "beard" and (j >= 6 or j == 5 and i in (0, 7)) and not (j == 6 and i in (3, 4) and r != "dwarf"):
            return H[1] if j == 7 and i % 2 else H[2]
        if beard == "moustache" and j == 5 and i in (2, 3, 4, 5):
            return H[2]
        if beard == "moustache" and j == 6 and i in (2, 5):
            return H[2]
        return c

    # ================================================================ clothes, by proportion so any body plan fits
    def body_paint(self):
        o = self.s["outfit"]
        top, acc, lea, S = self.top, self.acc, self.lea, self.skin
        kind = o.get("top", "tunic")
        overs = o.get("overs", [])
        trim = GOLD if self.race == "elf" else acc

        def p(face, i, j, fw, fh):
            c = lit(face, j, fh, top, 2)
            mid = fw / 2
            belt = round(fh * 0.68)
            if face == "front":
                if j == 0 and mid - 1 <= i < mid + 1:
                    return S[3] if kind not in ("coat", "robe") else trim[2]
                if j == 0 or j == 1 and i in (int(mid) - 2, int(mid) + 1):
                    return trim[3]
                if "apron" in overs and (j >= 2 and mid - 2 <= i < mid + 2 or j < 2 and i in (int(mid) - 2, int(mid) + 1)):
                    lin = look("cloth", "linen")
                    return lin[4] if j == 2 else lin[3]
                if kind in ("coat", "robe", "vest") and mid - 1 <= i < mid + 1 and j > 1:
                    if kind == "vest":
                        return acc[1] if i < mid else acc[2]
                    return top[1] if i < mid else (self.metal[4] if j % 3 == 0 else c)
                if self.race == "elf" and j == fh - 1:
                    return GOLD[3]
                if self.race == "dwarf" and j == belt and mid - 1 <= i < mid + 1:
                    return GOLD[3]
            if face != "top" and face != "bottom" and j == belt and ("belt" in overs or kind in ("tunic", "coat") or self.race == "dwarf"):
                if face == "front" and mid - 1 <= i < mid + 1:
                    return self.metal[4]
                return lea[2] if face != "back" else lea[1]
            if face == "front" and "pouches" in overs and j in (belt + 1, belt + 2) and i == fw - 2:
                return lea[3]
            if face == "back" and self.s.get("shawl") and j < 4:
                return acc[2]
            if face == "front" and self.s.get("shawl") and j < 3 and (i < 2 or i >= fw - 2):
                return acc[3]
            if face == "top":
                return top[3] if not self.s.get("shawl") else acc[3]
            return c
        return p

    def skirt_paint(self, side):
        o = self.s["outfit"]
        kind = o.get("top", "tunic")
        top = self.top
        long_ = 99 if kind in ("robe", "dress") else 0.6

        def p(face, i, j, fw, fh):
            if face in ("top", "bottom"):
                return None
            stop = fh if long_ == 99 else round(fh * long_)
            if j >= stop:
                return None
            return lit(face, j, fh, top, 2) if j < stop - 1 else top[1]
        return p if kind in ("coat", "robe", "dress") else None

    def arm_paint(self):
        o = self.s["outfit"]
        sl = o.get("sleeves", "long")
        top, acc, S, lea = self.top, self.acc, self.skin, self.lea
        gloves = "gloves" in o.get("overs", []) or self.race == "dwarf"
        trim = GOLD if self.race == "elf" else acc

        def p(face, i, j, fw, fh):
            end = {"long": fh - 2, "short": fh // 3, "rolled": fh // 2, "none": 0, "bell": fh - 1}.get(sl, fh - 2)
            if j >= fh - 2 or j >= end:
                if gloves and j >= fh - 3:
                    return lit(face, j, fh, lea, 2)
                return S[3] if face == "top" else lit(face, j, fh, S, 3)
            if face == "bottom":
                return S[2]
            if j == end - 1:
                return trim[3] if sl in ("long", "bell") else top[3]
            if face == "top":
                return top[3]
            return lit(face, j, fh, top, 2)
        return p

    def leg_paint(self):
        o = self.s["outfit"]
        bot, lea = self.bot, self.lea
        kind = o.get("bottom", "trousers")
        skirt = kind in ("skirt", "dress", "robe") or o.get("top") in ("dress", "robe")

        def p(face, i, j, fw, fh):
            boot = fh - max(2, round(fh * (0.42 if self.race == "dwarf" else 0.25)))
            if face == "bottom":
                return lea[0]
            if j >= boot:
                return lea[3] if j == boot and face != "back" else lit(face, j, fh, lea, 2)
            if skirt and j >= fh * 0.5:
                return lit(face, j, fh, look("cloth", "cream") if kind != "robe" else bot, 1)
            if face == "top":
                return bot[3]
            return lit(face, j, fh, bot, 2)
        return p

    # ================================================================ hats, hair past the head, race and age cubes
    def add(self, name, lo, size, paint, inflate=0.0, rot=(), pivot=None, upper=True, bone=None, anchor=None):
        self.boxes.append((name, lo, size, paint, inflate, rot, pivot, upper, bone, anchor))

    def extras(self, hy):
        """hy = the head's bottom; head-relative cubes are placed from it"""
        s, H, S = self.s, self.hair, self.skin
        st = s["hair"]["style"]
        hw = s.get("headwear")
        top = hy + 8
        if hw in ("cap", "bandana", "hood"):
            R = self.acc if hw == "bandana" else self.top if hw == "hood" else self.metal[1:] if hw == "helm" else self.lea
            rows = {"cap": 2, "bandana": 2, "hood": 8, "helm": 3}[hw]

            def hat(face, i, j, fw, fh):
                if face == "top":
                    return R[3]
                if face == "bottom":
                    return None
                if hw == "hood" and face == "front" and 1 <= i <= 6 and j >= 1:
                    return None
                return (lit(face, j, fh, R, 2) if j < rows - 1 else R[1]) if j < rows else None
            self.add("hat", (-4, hy, -4), (8, 8, 8), hat, 0.5)
            if hw == "cap":
                self.add("brim", (-4, top - 1.5, 3.5), (8, 1, 3), flat(R, 2))
        if self.race == "elf" and hw is None:                       # a gold circlet, a green stone on the brow
            def circ(face, i, j, fw, fh):
                if face in ("top", "bottom") or j != 1:
                    return None
                if face == "front" and i in (3, 4):
                    return rgb("#4af0b0")
                return GOLD[3] if i % 3 else GOLD[2]
            self.add("circlet", (-4, hy, -4), (8, 8, 8), circ, 0.5)
        if st == "ponytail":
            self.add("tail", (-1.5, hy + 1, -5.5), (3, 6, 2), hairy(H))
        elif st == "bun":
            self.add("bun", (-2, top - 0.5, -5), (4, 3, 3), hairy(H))
        elif st == "topknot":
            self.add("knot", (-1.5, top, -2), (3, 3, 3), hairy(H))
        elif st == "braid":
            self.add("braid", (-1, hy - 6, -5), (2, 10, 2), hairy(H))
        elif st == "twintails":
            for sx in (-1, 1):
                self.add("twin", (sx * 4.5 - 1, hy - 1, -2), (2, 7, 2), hairy(H))
        elif st == "long" or self.race == "elf" and st not in ("bald", "buzz", "short", "topknot", "bun"):
            self.add("long", (-4.0, hy - 7 if self.race == "elf" else hy - 5, -4.6), (8, 9 if self.race == "elf" else 6, 0.6), hairy(H))
        if self.age == "kid" and self.slim:                          # a bow in her hair
            R = ramp5("#d04050")
            self.add("bow", (3.6, top - 2.5, -1), (1.2, 2, 2), flat(R, 2))
            self.add("bow", (3.6, top - 1.5, -2.5), (1.2, 1, 1), flat(R, 3))
            self.add("bow", (3.6, top - 1.5, 0.5), (1.2, 1, 1), flat(R, 3))
        beard = s.get("beard") or ("beard" if self.race == "dwarf" and self.age != "kid" else None)
        if beard == "beard":
            if self.race == "dwarf":                                 # down to the belt, braided, ringed in gold
                self.add("beard", (-3.5, hy - 7, 3.2), (7, 9, 1.6), hairy(H))
                for sx in (-1, 1):
                    self.add("beard", (sx * 1.6 - 0.75, hy - 10, 3.4), (1.5, 3.5, 1.2), hairy(H))
                    self.add("ring", (sx * 1.6 - 0.9, hy - 8.4, 3.3), (1.8, 0.8, 1.4), flat(GOLD, 3))
            else:
                self.add("beard", (-3, hy - 2.4, 3.4), (6, 2.6, 1.0), hairy(H))
        if self.race == "dwarf":
            self.add("nose", (-1, hy + 2, 4), (2, 2, 1), flat(mix_r(self.skin, (190, 80, 60), 0.3), 3))
        if self.race == "elf":                                       # long ears swept up and back
            for sx in (-1, 1):
                x0 = 4.0 if sx > 0 else -7.5
                self.add("ear", (x0, hy + 3, -0.5), (3.5, 2, 1.2), flat(S, 3), rot=(("z", sx * 32), ("y", sx * 25)), pivot=(sx * 4.0, hy + 4, 0))
                self.add("ear", (x0 + (3.0 if sx > 0 else -1.5), hy + 3.4, -0.4), (2, 1, 1), flat(S, 3), rot=(("z", sx * 46), ("y", sx * 25)), pivot=(sx * 4.0, hy + 4, 0))
            cl = self.acc if self.acc[2] != self.top[2] else ramp5("#2a5a34")
            bw, bh, bd = self.plan["body"]
            self.add("cloak", (-bw / 2 - 0.5, self.plan["leg"][1] - 9, -bd / 2 - 1.2), (bw + 1, bh + 9, 1), flat(cl, 2))
        if self.race == "demon":
            Hn = ramp5("#2a2028")
            for sx in (-1, 1):                                       # ram horns: up off the brow, back, round the ear, forward
                cy, cz, r0 = top + 0.4, -1.2, 2.9            # a curl round a circle beside the head, shrinking as it goes
                for k in range(7):
                    th = math.radians(62 - 48 * k)
                    r_ = r0 * (1 - 0.06 * k)
                    sz = 2.5 - 0.17 * k
                    y, z = cy + r_ * math.cos(th), cz + r_ * math.sin(th)
                    x = sx * (3.2 + 0.32 * k) - sz / 2
                    self.add("horn", (x, y - sz / 2, z - sz / 2), (sz, sz, sz), flat(Hn, 3 if k < 4 else 4),
                             rot=(("x", -math.degrees(th)),), pivot=(x + sz / 2, y, z))
                self.add("ear", (sx * 4 - (0 if sx > 0 else 1), hy + 3, -0.5), (1, 2.5, 1), flat(S, 3), rot=(("z", sx * 20),), pivot=(sx * 4, hy + 3, 0))
            lh = self.plan["leg"][1]
            bd = self.plan["body"][2]
            t = [((-0.75, lh + 1, -bd / 2 - 4), (1.5, 1.5, 4), (("x", 30),)),
                 ((-0.75, lh - 2.5, -bd / 2 - 6.5), (1.5, 1.5, 4), (("x", 70),)),
                 ((-0.6, lh - 6.5, -bd / 2 - 7.2), (1.2, 1.2, 4), (("x", 110),))]
            for lo, size, rot in t:
                self.add("tail", lo, size, flat(self.skin, 2), rot=rot, pivot=(0, lo[1] + 0.75, lo[2] + 4), upper=False)
            self.add("tail", (-1.5, lh - 9.8, -bd / 2 - 6.6), (3, 2, 1), flat(Hn, 3), upper=False)
        if self.age == "elder" and not s.get("upright") and not s.get("weapon"):   # a cane in the right hand
            aw = self.plan["arm"][0]
            bw = self.plan["body"][0]
            self.add("cane", (-bw / 2 - aw / 2 - 0.5, 0, 3), (1, self.plan["leg"][1] + 2, 1), flat(ramp5("#6a4628"), 2), upper=False)
            self.add("cane", (-bw / 2 - aw / 2 - 0.5, self.plan["leg"][1] + 1, 1.5), (1, 1, 2.5), flat(ramp5("#6a4628"), 2), upper=False)
        G.gear(self, hy)

    # ================================================================ assembling
    def model(self, name):
        P = self.plan
        bw, bh, bd = P["body"]
        lw, lh, ld = P["leg"]
        aw, ah, ad = P["arm"]
        if self.slim and self.race != "dwarf":
            aw = min(aw, 3)
        hy = lh + bh
        m = Model(name)
        hunch = P.get("hunch", 0)
        pv = (0, lh, 0)
        up = (("x", hunch),) if hunch else ()

        def box(lo, size, paint, inflate=0.0, rot=(), pivot=None, upper=True, bone="head"):
            b = m.box(lo, size, paint, inflate=inflate, rot=tuple(rot), pivot=pivot)
            b.bone = bone                        # what it moves with on Epic Fight's biped (tools/mcexport.py)
            if hunch and upper:
                b.stoop = (pv, hunch)            # after its own turn, the whole upper body leans forward
            return b
        legp, sk = G.legs(self, self.leg_paint()), None
        # on the biped a short-legged body hangs over its legs (tools/mcexport.py): no leg face may lie in the body's
        lw, ld = min(lw, bw / 2 - 0.06), min(ld, bd - 0.12)
        for side, x in (("r", -lw - 0.02), ("l", 0.02)):
            box((x, 0, -ld / 2), (lw, lh, ld), legp, upper=False, bone="leg_" + side)
            sk = self.skirt_paint(side)
            if sk:                              # and a skirt over them stands clear of the body's faces
                inf = 0.25 if side == "r" else 0.27
                if abs(ld / 2 + inf - bd / 2) < 0.1:
                    inf = bd / 2 - ld / 2 + 0.12 + (0 if side == "r" else 0.02)
                box((x, 0, -ld / 2), (lw, lh, ld), sk, inf, upper=False, bone="leg_" + side)
        box((-bw / 2, lh, -bd / 2), (bw, bh, bd), G.body(self, self.body_paint()), bone="body")
        armp = G.arms(self, self.arm_paint())
        box((-bw / 2 - aw, hy - ah, -ad / 2), (aw, ah, ad), armp, bone="arm_r")
        box((bw / 2, hy - ah, -ad / 2), (aw, ah, ad), armp, bone="arm_l")
        box((-4, hy, -4), (8, 8, 8), self.head_paint())
        self.extras(hy)
        for n, (nm, lo, size, paint, inflate, rot, pivot, upper, bone, anchor) in enumerate(self.boxes):
            inflate += 0.03 * (n % 4)           # cubes that overlap never share a face plane (it flickers in game)
            b = box(lo, size, paint, inflate, rot, pivot, upper, bone or (BONE_OF.get(nm, "head") if upper or nm in BONE_OF else "hips"))
            b.anchor = anchor
        img = m.build()
        k = 1.0
        if self.age == "teen":
            k = 0.95
        return m, img, k


# extras that don't ride the head: name -> bone (the rest follow the head; a lower one with no entry, the hips)
BONE_OF = {"cloak": "body", "scarf": "body", "cane": "cane"}


def mix_r(R, c, t):
    return [mix(x, c, t) for x in R]


# ================================================================== Hob, and the sample cast

HOB = {"id": "hob_tarrant", "name": "Hob Tarrant", "age": "elder", "sex": "m", "skin": "weathered", "race": None, "upright": True,
       "hair": {"style": "shaggy", "color": "grey"}, "headwear": None, "beard": "beard", "nose": True,
       "face": {"eye": "mid", "iris": "hazel", "brows": "thick", "mouth": "smile", "blush": False, "freckles": False, "marks": [], "nose_box": False},
       "outfit": {"top": "coat", "bottom": "trousers", "sleeves": "long", "overs": ["belt", "pouches", "gloves"],
                  "colors": {"top": "brown", "bottom": "charcoal", "accent": "red", "leather": "tan"}}}


def hob_hat(f):
    """Hob's wide, sagging leather hat and the red scarf at his throat"""
    R = ramp5("#4a3220")
    hy = f.plan["leg"][1] + f.plan["body"][1]
    f.add("hat", (-6.5, hy + 7.6, -6.5), (13, 1, 13), flat(R, 2))
    f.add("hat", (-4.5, hy + 8.6, -4.5), (9, 3, 9), flat(R, 2))
    f.add("hat", (-4.6, hy + 9.2, -4.6), (9.2, 1, 9.2), flat(ramp5("#6a2418"), 2))
    f.add("scarf", (-4.5, hy - 1, -2.5), (9, 1.6, 5), flat(f.acc, 2))


HAND = HERE / "npc_specs_hand"          # the hand-made leads (shopkeepers, the guild's Elowen) written as forge specs


def spec(id_):
    if id_ in ("wagoner", "hob_tarrant"):
        return HOB
    for d in (KEPT, SPECS, HAND):
        p = d / (id_ + ".json")
        if p.exists():
            return json.load(open(p, encoding="utf-8"))
    raise KeyError(id_)


def king_crown(f):
    """King Aldric's crown: a gold band round the head, five points standing up off it, a red stone on the brow"""
    hy = f.plan["leg"][1] + f.plan["body"][1]
    top = hy + 8
    G, RED = GOLD, ramp5("#b01c22")
    f.add("crown", (-4.6, top - 1.2, -4.6), (9.2, 2.2, 9.2), flat(G, 2))
    for x, z in ((-4.1, 3.6), (-0.5, 3.6), (3.1, 3.6), (-4.1, -4.6), (3.1, -4.6), (-4.1, -0.5), (3.1, -0.5)):
        f.add("crown", (x, top + 1.0, z), (1.0, 2.0 if x != -0.5 else 2.8, 1.0), flat(G, 3))
    f.add("crown_gem", (-1.0, top - 0.8, 4.4), (2.0, 1.4, 0.6), flat(RED, 3))


def veyra_ring(f):
    """Veyra the Ringkeeper's mark: a great ring of aqua rune-light carried on her back, the colour of her door home"""
    P = f.plan
    bw, bh, bd = P["body"]
    lh = P["leg"][1]
    hy = lh + bh
    zb = -bd / 2
    A = (0.0, hy - 3, zb)
    AQ = ramp5("#3cc8e0")
    rim, rune = flat(AQ, 2), glowing(AQ)
    cy, r, n = hy - 2.0, 7.5, 20
    for i in range(n):
        a = i / n * 2 * math.pi
        x, y = math.sin(a) * r, cy + math.cos(a) * r
        lo = (x - 1.0, y - 1.0, zb - 2.2)
        f.add("ring", lo, (2.0, 2.0, 1.2), rune if i % 5 == 0 else rim, 0, (), None, True, bone="back", anchor=A)
    for x in (-2.0, 1.0):                                      # the straps that hold it to her
        f.add("ring_strap", (x, hy - 9, zb - 1.2), (1.0, 9, 1.2), flat(f.lea, 2), 0, (), None, True, bone="back", anchor=A)


def folk(id_):
    """anyone in the cast by id, Hob with his hat, Veyra with her ring"""
    f = Folk(spec(id_))
    if f.s is HOB:
        hob_hat(f)
    if f.s.get("id") == "veyra":
        veyra_ring(f)
    if f.s.get("id") == "king":
        king_crown(f)
    return f


def sample():
    kid = next(json.load(open(p)) for p in sorted(KEPT.glob("*.json")) if json.load(open(p)).get("age") == "kid")
    girl = next((json.load(open(p)) for p in sorted(KEPT.glob("*.json")) if json.load(open(p)).get("age") == "kid" and json.load(open(p)).get("sex") == "f"), kid)
    elf = next(json.load(open(p)) for p in sorted(SPECS.glob("elf_*.json")) if json.load(open(p)).get("age") == "adult")
    granny = dict(spec("townsfolk_5987000"), shawl=True, glasses=True)
    out = []
    f = Folk(HOB)
    hob_hat(f)
    out.append(("hob_tarrant", f))
    for s in (girl, granny, spec("dwarf_78002"), spec("demon_91004"), elf, spec("demon_91016")):
        out.append((s["id"], Folk(s)))
    return out


if __name__ == "__main__":
    lineup = []
    for nm, f in sample():
        m, img, k = f.model(nm)
        m.write(img, scale=k)
        lineup.append({"name": nm, "who": f.s.get("name", nm)})
    import mcstyle_props
    for nm in ("wagon_horse", "hob_wagon"):
        mcstyle_props.make(nm)
        lineup.append({"name": nm})
    json.dump(lineup, open(OUT / "lineup.json", "w"), indent=1)
