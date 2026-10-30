"""The monster forge: every Roster v2 dungeon's monsters and bosses built from one set of parts, the way the Frostbound
were built by hand (E:/Ashbound/tools/voxfrost.py) - boxes with pixel shaders on the biped bones Epic Fight fits
(efmob.biped), or on a crawler/beast body that rides Epic Fight's spider. A monster is a spec: its dungeon's theme
(ramps), its build (size, bulk, hunch), and one choice per region (legs, torso, shoulders, back, head, each hand),
plus `extra` for what only it has. Bosses are the same, bigger, with more on them.

    python tools/monsterforge.py <gate|name...> [--preview]     -> tools/mob_src (efmob reads it), or renders/vox
    blender -b -P E:/Ashbound/tools/blender/preview_mob.py -- <name>@<height> ...
    python tools/port_gate.py <gate> mobs                       (its GATES spec lists them; forge_specs.py)
"""
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, 'E:/Ashbound/tools')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import voxsword as V  # noqa: E402
from voxsword import Sword, ramp, shade, fbm, h3  # noqa: E402
from voxboss import Part, PB, C  # noqa: E402
import voxmob as M  # noqa: E402

OUT = Path(os.path.dirname(os.path.abspath(__file__))) / 'mob_src'
BONES = ["hips", "thigh_l", "shin_l", "foot_l", "thigh_r", "shin_r", "foot_r", "torso", "head",
         "arm_l", "fore_l", "hand_l", "arm_r", "fore_r", "hand_r"]
UNIT = 15.0     # pixels to a block at scale 1 (the Frostbound: 42 px, 2.8 blocks)


# ================================================================ shaders

def mk(R, base=0.5, light=1.0, grain=0.18, edge=0.14, stripe=None, crust=None, holes=False, scale=1.0, pattern=None):
    """a material from a ramp: lit from above and in front, mottled, a bright rim on its top edge. stripe: darker
    lines every n texels (planks, plates, ribs); crust: (ramp, how much) patches on what faces up (frost, crystal,
    barnacles, moss); holes: a torn hem on long hanging cloth; pattern(p, n, i, j, w, h) -> value offset or None."""
    def f(p, n, b, key, i, j, w, h, fr):
        x, y, z = (c * scale for c in p)
        if holes and key in ("n", "s", "e", "w") and h > 6 and j > h - 2 - 5 * h3(i // 2, int(b.size[1] * 3), 5):
            return None
        if crust and n[1] > 0.3 and fbm(x * 0.6, y * 0.6, z * 0.6) > 1 - crust[1]:
            return shade(crust[0], 0.45 + 0.4 * fbm(x, y, z), i, j)
        v = base + light * (0.14 * n[1] + 0.06 * n[2] - 0.08 * (j / max(1, h - 1))) + grain * (fbm(x * 0.7, y * 0.7, z * 0.7) - 0.5)
        if edge and key not in ("u", "d") and (j == 0 or i == 0):
            v += edge
        if stripe and i % stripe == 0:
            v -= 0.12
        if pattern:
            d = pattern(p, n, i, j, w, h)
            if d is None:
                return None
            if d >= 0.9 and hasattr(pattern, "glow"):
                return shade(pattern.glow, 0.7, i, j)
            v += d
        return shade(R, v, i, j)
    return f


def glow(R):
    def f(p, n, b, key, i, j, w, h, fr):
        return shade(R, 0.62 + 0.34 * fbm(p[0] * 0.8, p[1] * 0.8, p[2] * 0.8), i, j)
    return f


def facets(R):
    """crystal: flat facets in bands of light, a bright rim"""
    def f(p, n, b, key, i, j, w, h, fr):
        v = 0.45 + 0.3 * (n[0] * 0.4 + n[1] * 0.7 + n[2] * 0.3) + (0.22 if i == 0 or j == 0 else 0) + 0.12 * (((i + j) // 3) % 2)
        return shade(R, v, i, j)
    return f


def scales(R):
    def f(p, n, b, key, i, j, w, h, fr):
        rim = j % 3 == 0 and (i + (j // 3) * 2) % 4 != 0          # the lower edge of each overlapping scale
        v = 0.5 + 0.14 * n[1] + (0.12 if rim else 0) - (0.1 if j % 3 == 1 and i % 4 == (j // 3 * 2) % 4 else 0)
        return shade(R, v + 0.16 * (fbm(p[0] * 0.6, p[1] * 0.6, p[2] * 0.6) - 0.5), i, j)
    return f


def feathers(R):
    def f(p, n, b, key, i, j, w, h, fr):
        v = 0.42 + 0.14 * n[1] + (0.18 if (i + j) % 4 == 0 else 0) - (0.12 if (j + abs(i - w // 2)) % 5 == 0 else 0)
        return shade(R, v + 0.1 * (fbm(p[0], p[1] * 0.5, p[2]) - 0.5), i, j)
    return f


def fur(R):
    def f(p, n, b, key, i, j, w, h, fr):
        v = 0.45 + 0.14 * n[1] + 0.3 * (h3(i, int(p[1] * 0.5), 9) - 0.5) * 0.6 - (0.1 if i % 3 == 0 else 0)
        return shade(R, v, i, j)
    return f


def flesh(R, vein):
    def f(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        if abs(fbm(x * 0.5, y * 0.5, z * 0.5) - 0.5) < 0.03:
            return shade(vein, 0.6, i, j)
        return shade(R, 0.5 + 0.14 * n[1] + 0.25 * (fbm(x * 0.9, y * 0.9, z * 0.9) - 0.5), i, j)
    return f


def veins(T):
    """thin glowing seams through rock or flesh (shade() takes the value past the ramp's top: the glow ramp instead)"""
    G = T["glow"]

    def f(p, n, i, j, w, h):
        x, y, z = p
        return 0.9 if abs(fbm(x * 0.22 + 7, y * 0.22, z * 0.22) - 0.5) < 0.011 else 0
    f.glow = G
    return f


def shaders(T):
    """a theme's ramps -> the shader table every part names its material from"""
    E = T.get("edge", 0.14)
    sh = {
        "metal": mk(T["metal"], 0.5, 1.4, 0.18, E + 0.04, crust=T.get("crust")),
        "plate": mk(T["metal"], 0.55, 1.4, 0.14, E + 0.06, stripe=5, crust=T.get("crust")),
        "cloth": mk(T["cloth"], 0.5, 1.0, 0.25, 0, crust=T.get("crust_cloth")),
        "rag": mk(T["cloth"], 0.46, 1.0, 0.25, 0, holes=True),
        "leather": mk(T["leather"], 0.5, 1.0, 0.2, 0.08),
        "skin": mk(T["skin"], 0.52, 1.0, 0.22, 0.04),
        "bone": mk(T.get("bone", T["skin"]), 0.62, 1.0, 0.14, 0.1),
        "wood": mk(T.get("wood", T["leather"]), 0.5, 1.0, 0.2, 0.06, stripe=3),
        "accent": mk(T["accent"], 0.55, 1.4, 0.14, 0.14),
        "dark": mk(T["metal"], 0.03, 0.2, 0.03, 0),
        "glow": glow(T["glow"]),
        "crystal": facets(T.get("crystal", T["glow"])),
        "scale": scales(T.get("scale", T["skin"])),
        "feather": feathers(T.get("feather", T["cloth"])),
        "fur": fur(T.get("fur", T["leather"])),
        "flesh": flesh(T.get("flesh", T["skin"]), T.get("vein", T["glow"])),
        "rock": mk(T.get("rock", T["metal"]), 0.5, 1.2, 0.3, 0.1, crust=T.get("crust"), pattern=veins(T) if T.get("veins") else None),
        "eye": glow(T.get("eye", T["glow"])),
    }
    sh.update(T.get("extra_shaders", {}))
    return sh


# ================================================================ the builder

class Build:
    """one monster under construction: its Sword (boxes), its parts (bones), and the proportions every region reads"""

    def __init__(self, name, spec):
        self.name, self.spec = name, spec
        self.s = Sword(name)
        self.parts = {}
        g = spec.get("build", {})
        self.bulk = g.get("bulk", 1.0)          # widths
        self.sw = 6.6 * g.get("shoulders", 1.0) * self.bulk ** 0.5
        self.lw = 3.0 * self.bulk ** 0.5
        self.hunch = g.get("hunch", 4)
        self.arm_t = 3.2 * g.get("arms", 1.0)
        self.leg_t = 3.8 * g.get("legs", 1.0)

    def add(self, part, box, mat, **kw):
        lo, size = box
        b = PB(part, lo, size, mat, tag=kw.pop("tag", part.name), **kw)
        self.s.boxes.append(b)
        return b

    def P(self, name, pivot, rots=(), parent=None):
        return Part(name, pivot, rots, self.parts[parent] if isinstance(parent, str) else parent)

    def icicles(self, part, x0, x1, y, z, n, longest=2.6, seed=0, mat="crystal", up=False):
        for k in range(n):
            x = x0 + (x1 - x0) * (k + 0.5) / n
            ln = longest * (0.4 + 0.6 * h3(k, seed, 3))
            self.add(part, C(x, y if up else y - ln, z, 0.6, ln, 0.6), mat, tag="spike")

    def spikes(self, part, at, n, length=3.0, mat="crystal", seed=1, spread=1.6, tilt=None):
        """a cluster of shards (crystals, bone, quills) grown out of a point, leaning outward"""
        x, y, z = at
        for k in range(n):
            a = k * 2.4 + seed
            dx, dz = math.cos(a) * spread * h3(k, seed, 1), math.sin(a) * spread * h3(k, seed, 2)
            ln = length * (0.5 + 0.5 * h3(k, seed, 4))
            w = 0.7 + 0.8 * h3(k, seed, 5)
            sp = Part("spk", (x + dx, y, z + dz), tilt or (("x", dz * 9), ("z", -dx * 9)), part)
            self.add(sp, C(x + dx, y, z + dz, w, ln, w), mat, tag="spike")
            self.add(sp, C(x + dx, y + ln, z + dz, w * 0.5, ln * 0.35, w * 0.5), mat, tag="spike")


def legs(B, kind):
    hips = B.parts["hips"] = Part("hips", (0, 21, 0))
    t = B.leg_t
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * B.lw
        th = B.parts["thigh_" + nm] = Part("thigh_" + nm, (x, 21, 0), (("x", -4), ("z", side * 3)), hips)
        sh = B.parts["shin_" + nm] = Part("shin_" + nm, (x, 11.4, 0), (("x", 6),), th)
        ft = B.parts["foot_" + nm] = Part("foot_" + nm, (x, 2.2, 0), (("x", -2),), sh)
        if kind == "plate":
            B.add(th, C(x, 11.8, 0, t, 9.4, t + 0.2), "plate", tag="cuisse")
            B.add(th, C(x + side * 0.4, 16.0, 0.3, t + 0.4, 4.4, t + 0.6), "metal", tag="cuisse")
            B.add(sh, C(x, 2.4, 0.2, t - 0.4, 9.2, t - 0.2), "plate", tag="greave")
            B.add(sh, C(x, 9.6, 0.6, t + 0.4, 2.8, t + 0.6), "metal", tag="knee")
            B.add(ft, C(x, 0, 1.0, t, 2.4, 6.4), "metal", tag="boot")
            B.add(ft, C(x, 0, 3.6, t - 0.4, 1.4, 2.2), "metal", tag="boot")
        elif kind in ("cloth", "robe"):
            B.add(th, C(x, 11.6, 0, t - 0.2, 9.6, t), "cloth", tag="trouser")
            B.add(sh, C(x, 2.6, 0, t - 0.6, 9.0, t - 0.4), "cloth", tag="trouser")
            B.add(sh, C(x, 2.2, 0.2, t - 0.2, 4.6, t + 0.2), "leather", tag="boot_top")
            B.add(ft, C(x, 0, 1.0, t - 0.2, 2.4, 6.0), "leather", tag="boot")
            B.add(sh, C(x, 9.8, 0.4, t, 1.6, t + 0.4), "leather", tag="knee")
        elif kind == "bare":
            B.add(th, C(x, 11.4, 0, t, 10.0, t + 0.4), "skin", tag="thigh")
            B.add(sh, C(x, 2.2, 0.2, t - 0.8, 9.4, t - 0.6), "skin", tag="shin")
            B.add(sh, C(x, 9.6, 0.6, t - 0.4, 2.4, t), "skin", tag="knee")
            B.add(ft, C(x, 0, 1.4, t - 0.4, 2.2, 6.0), "skin", tag="boot")
            for k in (-1, 0, 1):
                B.add(ft, C(x + k * 1.1, 0, 4.6, 0.8, 1.0, 1.2), "bone", tag="claw")
        elif kind == "beast":    # thick haunches, a reversed hock, cloven or clawed feet
            B.add(th, C(x, 12.0, -0.6, t + 1.2, 9.4, t + 1.6), "fur", tag="haunch")
            B.add(sh, C(x, 2.4, -1.0, t - 1.0, 9.0, t - 0.8), "fur", tag="hock")
            B.add(ft, C(x, 0, 0.6, t, 2.6, 5.0), B.spec.get("hoof", "dark"), tag="boot")
            B.add(ft, C(x, 0, 2.6, t - 0.6, 1.4, 2.4), B.spec.get("hoof", "dark"), tag="boot")
        elif kind == "rock":
            B.add(th, C(x, 11.0, 0, t + 1.4, 10.4, t + 1.4), "rock", tag="thigh")
            B.add(sh, C(x, 2.0, 0, t + 0.8, 9.4, t + 1.0), "rock", tag="shin")
            B.add(ft, C(x, 0, 0.8, t + 1.6, 2.6, 7.0), "rock", tag="boot")
        elif kind == "chitin":
            B.add(th, C(x, 11.8, 0, t - 0.4, 9.4, t), "scale", tag="thigh")
            B.add(sh, C(x, 2.4, 0.2, t - 1.0, 9.2, t - 0.6), "scale", tag="shin")
            B.add(sh, C(x, 8.6, 1.8, 1.2, 3.6, 1.0), "accent", tag="spur")
            B.add(ft, C(x, 0, 1.0, t, 2.4, 6.0), "scale", tag="boot")
    return hips


def hips_dress(B, kind):
    hips = B.parts["hips"]
    w = 8.0 * B.bulk ** 0.6
    if kind in ("plate", "leather", "cloth", "bare", "robe", "rock", "chitin", "beast"):
        mat = {"plate": "metal", "leather": "leather", "cloth": "cloth", "bare": "leather", "robe": "cloth",
               "rock": "rock", "chitin": "scale", "beast": "fur"}[kind]
        B.add(hips, C(0, 18.8, 0, w, 3.2, 4.8 * B.bulk ** 0.5), mat, tag="fauld")
        B.add(hips, C(0, 20.6, 0, w + 0.8, 1.4, 5.4 * B.bulk ** 0.5), "leather" if kind != "rock" else "rock", tag="belt")
        if kind != "rock":
            B.add(hips, C(0, 20.4, 2.9 * B.bulk ** 0.5, 1.8, 1.8, 0.4), "accent", tag="buckle")
    if kind in ("plate", "cloth", "robe"):
        long = kind == "robe"
        for z, lean in ((2.6, -4), (-2.6, 5)):
            tb = Part("tabard%d" % (z > 0), (0, 20.4, z * B.bulk ** 0.5), (("x", lean),), hips)
            B.add(tb, C(0, 2.2 if long else 9.0, z * B.bulk ** 0.5, w - 1.0, 18.4 if long else 11.6, 0.6), "rag", tag="tabard")
        if long:
            for side in (1, -1):
                v = Part("robe_side%d" % (side > 0), (side * 4.4, 20.4, 0), (("z", side * 6),), hips)
                B.add(v, C(side * 4.6 * B.bulk ** 0.5, 4.0, 0, 0.7, 16.6, 5.2 * B.bulk ** 0.5), "rag", tag="robe")


def torso(B, kind):
    hips = B.parts["hips"]
    to = B.parts["torso"] = Part("torso", (0, 21.4, 0), (("x", B.hunch),), hips)
    w, d = 8.2 * B.bulk, 5.2 * B.bulk ** 0.7
    top = 32.4
    if kind == "plate":
        B.add(to, C(0, 21.4, 0, w, 11.0, d), "metal", tag="cuirass")
        B.add(to, C(0, 24.0, d / 2 - 0.2, w - 1.2, 7.0, 1.2), "plate", tag="breast")
        B.add(to, C(0, 32.0, -0.2, w + 3.4, 2.4, d + 0.6), "metal", tag="gorget")
    elif kind == "leather":
        B.add(to, C(0, 21.4, 0, w, 11.0, d), "leather", tag="jerkin")
        B.add(to, C(0, 21.6, d / 2 + 0.05, w - 2.4, 9.8, 0.4), "cloth", tag="shirt")
        for k, sx in enumerate((-1.6, 1.6)):
            strap = Part("strap%d" % k, (0, 27, 0), (("z", 32 if k else -32),), to)
            B.add(strap, C(0, 21.0, d / 2 + 0.25, 1.2, 12.0, 0.4), "accent" if B.spec.get("bandolier") else "leather", tag="strap")
        B.add(to, C(0, 31.6, -0.2, w + 2.0, 2.0, d + 0.4), "fur" if B.spec.get("fur_collar") else "leather", tag="collar")
    elif kind == "robe":
        B.add(to, C(0, 21.4, 0, w, 11.0, d), "cloth", tag="robe")
        B.add(to, C(0, 22.0, d / 2 + 0.05, 2.4, 10.0, 0.4), "accent", tag="stole")
        B.add(to, C(0, 31.0, -0.2, w + 3.0, 2.0, d + 1.0), "cloth", tag="mantle")
    elif kind == "bare":
        B.add(to, C(0, 21.4, 0, w - 0.6, 11.0, d - 0.4), "skin", tag="chest")
        for sx in (-1.9, 1.9):
            B.add(to, C(sx * B.bulk, 27.4, d / 2 - 0.4, 3.4 * B.bulk, 3.6, 1.0), "skin", tag="pec")
        for k in range(3):
            B.add(to, C(0, 21.8 + k * 1.8, d / 2 - 0.5, 3.6, 1.4, 0.9), "skin", tag="abs")
        B.add(to, C(0, 31.4, -0.4, w + 1.2, 2.6, d), "skin", tag="traps")
    elif kind == "gut":
        B.add(to, C(0, 21.4, 0, w, 11.0, d), B.spec.get("gut_mat", "cloth"), tag="chest")
        B.add(to, C(0, 21.0, d / 2 - 0.4, w - 1.0, 7.4, 3.4), "skin", tag="belly")
        B.add(to, C(0, 31.4, -0.4, w + 1.2, 2.6, d), B.spec.get("gut_mat", "cloth"), tag="collar")
    elif kind == "rock":
        B.add(to, C(0, 21.0, 0, w + 1.2, 11.8, d + 1.0), "rock", tag="chest")
        B.add(to, C(0, 28.0, d / 2 + 0.2, w - 1.0, 4.4, 1.4), "rock", tag="slab")
        B.add(to, C(0, 31.6, -0.6, w + 4.4, 3.0, d + 1.6), "rock", tag="shoulders")
    elif kind == "chitin":
        B.add(to, C(0, 21.4, 0, w, 11.0, d), "scale", tag="carapace")
        for k in range(4):
            B.add(to, C(0, 22.0 + k * 2.6, d / 2, w - 1.4 - k * 0.4, 1.6, 0.8), "accent", tag="segment")
        B.add(to, C(0, 31.6, -0.2, w + 2.8, 2.2, d + 0.4), "scale", tag="collar")
    elif kind == "feather":
        B.add(to, C(0, 21.4, 0, w, 11.0, d), "feather", tag="breast")
        B.add(to, C(0, 29.6, -0.2, w + 3.6, 3.6, d + 1.6), "feather", tag="ruff")
    return to, top


def shoulders(B, kind, size=1.0):
    to = B.parts["torso"]
    if not kind:
        return
    for side in (1, -1):
        sx = side * B.sw
        pl = Part("pauldron%d" % (side > 0), (sx * 0.85, 33.6, -0.2), (("z", side * -18),), to)
        if kind == "plate":
            B.add(pl, C(sx, 31.0, -0.2, 5.4 * size, 3.6 * size, 6.4 * size), "metal", tag="pauldron")
            B.add(pl, C(sx, 31.0 + 3.2 * size, -0.2, 4.6 * size, 1.2, 5.6 * size), "plate", tag="pauldron")
        elif kind == "spiked":
            B.add(pl, C(sx, 31.0, -0.2, 5.4 * size, 3.6 * size, 6.4 * size), "metal", tag="pauldron")
            for k in range(3):
                B.add(pl, C(sx + side * (k - 1) * 1.4, 31.0 + 3.6 * size, -0.2 + (k - 1) * 1.2, 0.9, 1.6 + k * 0.9, 0.9), B.spec.get("spike_mat", "bone"), tag="spike")
        elif kind == "fur":
            B.add(pl, C(sx * 0.9, 30.8, -0.4, 6.0 * size, 3.4 * size, 7.0 * size), "fur", tag="pelt")
        elif kind == "leather":
            B.add(pl, C(sx, 31.0, -0.2, 4.8 * size, 2.8 * size, 5.6 * size), "leather", tag="pauldron")
        elif kind == "rock":
            B.add(pl, C(sx * 1.05, 30.4, -0.4, 6.4 * size, 4.6 * size, 7.0 * size), "rock", tag="boulder")
        elif kind == "feather":
            B.add(pl, C(sx, 30.0, -0.6, 5.6 * size, 4.0 * size, 6.8 * size), "feather", tag="pinion")
        elif kind == "crystal":
            B.add(pl, C(sx, 31.0, -0.2, 5.0 * size, 3.0 * size, 6.0 * size), "rock", tag="pauldron")
            B.spikes(pl, (sx, 33.6, -0.2), 4, 3.4 * size, mat="crystal", seed=3 + side)


def head(B, kind):
    to = B.parts["torso"]
    hd = B.parts["head"] = Part("head", (0, 33.6, 0.2), (("x", -B.hunch),), to)
    s = B.spec.get("head_size", 1.0)
    eye = B.spec.get("eye", "eye")
    hw, hh, hd_ = 5.8 * s, 7.4 * s, 6.2 * s
    fz = 0.2 + hd_ / 2              # the face plane
    y0 = 33.4
    if kind == "helm":
        B.add(hd, C(0, y0, 0.2, hw, hh, hd_), "metal", tag="helm")
        B.add(hd, C(0, y0 + hh, 0.2, hw - 1.2, 1.2, hd_ - 1.2), "metal", tag="helm")
        B.add(hd, C(0, y0 + hh * 0.48, fz + 0.12, hw - 1.4, 0.9, 0.3), "dark", tag="visor")
        B.add(hd, C(0, y0 + 1.2, fz + 0.12, 0.9, hh * 0.4, 0.3), "dark", tag="visor")
        for sx in (-1.2, 1.2):
            B.add(hd, C(sx * s, y0 + hh * 0.5, fz + 0.2, 1.2, 0.6, 0.3), eye, group="glow", tag="eye")
        B.add(hd, C(0, y0 + hh * 0.65, fz + 0.1, hw - 0.4, 0.8, 0.5), "metal", tag="brow")
    elif kind == "hood":
        B.add(hd, C(0, y0 - 0.4, -0.2, hw + 1.2, hh + 1.4, hd_ + 1.4), "cloth", tag="hood")
        B.add(hd, C(0, y0 + hh + 0.8, -1.2, hw - 1.4, 1.6, hd_ - 2), "cloth", tag="hood")
        B.add(hd, C(0, y0, fz + 0.45, hw - 1.2, hh - 1.2, 0.3), "dark", tag="cowl")
        for sx in (-1.1, 1.1):
            B.add(hd, C(sx * s, y0 + hh * 0.5, fz + 0.62, 1.0, 0.7, 0.3), eye, group="glow", tag="eye")
    elif kind == "skull":
        B.add(hd, C(0, y0 + 1.6, 0.2, hw - 0.4, hh - 1.6, hd_ - 0.4), "bone", tag="skull")
        B.add(hd, C(0, y0, 0.8, hw - 1.8, 2.0, hd_ - 1.6), "bone", tag="jaw")
        for sx in (-1.3, 1.3):
            B.add(hd, C(sx * s, y0 + hh * 0.48, fz - 0.1, 1.6, 1.4, 0.3), "dark", tag="socket")
            B.add(hd, C(sx * s, y0 + hh * 0.52, fz, 0.8, 0.6, 0.3), eye, group="glow", tag="eye")
        for k in range(4):
            B.add(hd, C(-1.5 + k, y0 + 1.6, fz - 0.6, 0.6, 0.8, 0.4), "bone", tag="teeth")
    elif kind in ("beast", "bull", "jackal", "lion", "mole"):
        long = {"beast": 4.0, "bull": 3.4, "jackal": 5.2, "lion": 3.0, "mole": 5.0}[kind]
        B.add(hd, C(0, y0, 0.2, hw, hh - 0.6, hd_), "fur", tag="skull")
        B.add(hd, C(0, y0 + 0.4, fz + long / 2 - 0.2, hw - 2.2, 2.8, long), "fur" if kind != "mole" else "skin", tag="muzzle")
        B.add(hd, C(0, y0 - 0.6, fz + long / 2 - 0.6, hw - 2.6, 1.2, long - 0.8), "skin", tag="jaw")
        B.add(hd, C(0, y0 + 2.8, fz + long - 0.4, 1.6 if kind != "mole" else 2.4, 1.0 if kind != "mole" else 1.8, 0.6),
              "dark" if kind != "mole" else "flesh", tag="nose")
        for k in range(3):
            B.add(hd, C(-1.0 + k, y0 + 0.2, fz + long - 0.8 - k * 0.3, 0.5, 0.9, 0.5), "bone", tag="fang")
        if kind != "mole":
            for sx in (-1.4, 1.4):
                B.add(hd, C(sx * s, y0 + hh * 0.55, fz + 0.1, 1.0, 0.7, 0.3), eye, group="glow", tag="eye")
        else:
            for sx in (-1.4, 1.4):
                B.add(hd, C(sx * s, y0 + hh * 0.55, fz + 0.1, 1.2, 0.5, 0.3), "dark", tag="sealed_eye")
        if kind == "jackal":
            for sx in (-1.6, 1.6):
                B.add(hd, C(sx * s, y0 + hh - 0.6, 0.0, 1.4, 4.6, 1.2), "fur", tag="ear")
        if kind == "lion":
            B.add(hd, C(0, y0 - 2.0, -0.6, hw + 4.0, hh + 3.0, hd_ + 1.0), B.spec.get("mane", "fur"), tag="mane")
        if kind == "bull":
            for side in (1, -1):
                hn = Part("horn%d" % (side > 0), (side * hw / 2, y0 + hh - 1.6, 0.4), (("z", side * -70),), hd)
                B.add(hn, C(side * hw / 2, y0 + hh - 2.4, 0.4, 1.8, 4.4, 1.8), "bone", tag="horn")
                hn2 = Part("horn_tip%d" % (side > 0), (side * hw / 2, y0 + hh + 1.8, 0.4), (("z", side * 60),), hn)
                B.add(hn2, C(side * hw / 2, y0 + hh + 1.6, 0.6, 1.2, 4.0, 1.2), "bone", tag="horn")
    elif kind == "bird":
        B.add(hd, C(0, y0, 0.2, hw - 0.8, hh - 0.8, hd_ - 0.4), "feather", tag="skull")
        beak = Part("beak", (0, y0 + 2.6, fz), (("x", 14),), hd)
        B.add(beak, C(0, y0 + 1.8, fz + 2.6, 2.0, 2.0, 5.4), B.spec.get("beak", "bone"), tag="beak")
        B.add(beak, C(0, y0 + 1.2, fz + 5.0, 1.2, 1.4, 1.4), B.spec.get("beak", "bone"), tag="beak")
        for sx in (-2.1, 2.1):
            B.add(hd, C(sx * s, y0 + hh * 0.56, fz - 1.0, 0.4, 0.9, 1.0), eye, group="glow", tag="eye")
        for k in range(4):
            B.add(hd, C(0, y0 + hh - 1.2 - k * 0.4, -1.0 - k * 1.4, 0.8, 2.0 + k * 0.6, 1.2), "feather", tag="crest")
    elif kind == "mask":
        B.add(hd, C(0, y0, 0.0, hw, hh, hd_ - 0.4), B.spec.get("hair", "cloth"), tag="hair")
        B.add(hd, C(0, y0 + 0.4, fz + 0.05, hw - 0.6, hh - 0.6, 0.6), B.spec.get("mask_mat", "bone"), tag="mask")
        for sx in (-1.2, 1.2):
            B.add(hd, C(sx * s, y0 + hh * 0.5, fz + 0.4, 1.4, 0.8, 0.3), "dark", tag="socket")
            B.add(hd, C(sx * s, y0 + hh * 0.52, fz + 0.5, 0.6, 0.4, 0.3), eye, group="glow", tag="eye")
        B.add(hd, C(0, y0 + 1.6, fz + 0.4, 2.8, 0.6, 0.3), "dark", tag="mouth")
    elif kind == "face":
        B.add(hd, C(0, y0, 0.2, hw - 0.6, hh - 0.8, hd_ - 0.6), "skin", tag="face")
        B.add(hd, C(0, y0 + hh - 1.6, -0.2, hw - 0.2, 2.0, hd_ - 0.2), B.spec.get("hair", "dark"), tag="hair")
        B.add(hd, C(0, y0 + 2.0, -hd_ / 2 + 0.2, hw - 0.2, hh - 2.4, 1.2), B.spec.get("hair", "dark"), tag="hair")
        for sx in (-1.2, 1.2):
            B.add(hd, C(sx * s, y0 + hh * 0.48, fz - 0.15, 1.2, 0.6, 0.3), eye, group="glow", tag="eye")
        B.add(hd, C(0, y0 + hh * 0.56, fz - 0.1, hw - 1.4, 0.6, 0.4), "skin", tag="brow")
        B.add(hd, C(0, y0 + 2.0, fz - 0.15, 2.0, 0.5, 0.3), "dark", tag="mouth")
        B.add(hd, C(0, y0 + 2.8, fz - 0.05, 0.8, 1.6, 0.6), "skin", tag="nose")
    elif kind == "miner":
        B.add(hd, C(0, y0, 0.2, hw - 0.6, hh - 1.6, hd_ - 0.6), "skin", tag="face")
        B.add(hd, C(0, y0 + hh - 2.4, 0.2, hw + 1.6, 1.0, hd_ + 1.6), "metal", tag="brim")
        B.add(hd, C(0, y0 + hh - 1.6, 0.0, hw, 2.8, hd_), "metal", tag="hat")
        B.add(hd, C(0, y0 + hh - 1.4, fz + 0.2, 1.8, 1.8, 0.8), "accent", tag="lamp")
        B.add(hd, C(0, y0 + hh - 1.0, fz + 0.6, 1.2, 1.0, 0.4), "glow", group="glow", tag="lamp_glass")
        for sx in (-1.2, 1.2):
            B.add(hd, C(sx * s, y0 + hh * 0.42, fz - 0.15, 1.1, 0.6, 0.3), eye, group="glow", tag="eye")
        B.add(hd, C(0, y0 - 0.6, fz - 0.6, hw - 1.2, 2.4, 1.6), B.spec.get("hair", "fur"), tag="beard")
    elif kind == "crown_face":     # a noble's face under a crown or circlet
        head(B, "face")
        return hd
    elif kind == "golem":          # a rock head sunk between the shoulders: a deep brow, a slit of light, a jaw
        B.add(hd, C(0, y0 - 1.0, 0.6, hw + 1.0, hh - 0.6, hd_ + 0.4), "rock", tag="head")
        B.add(hd, C(0, y0 + hh * 0.55, fz + 0.9, hw + 1.4, 1.6, 1.4), "rock", tag="brow")
        B.add(hd, C(0, y0 + hh * 0.38, fz + 1.05, hw - 0.6, 1.0, 0.3), "dark", tag="socket")
        for sx in (-1.4, 1.4):
            B.add(hd, C(sx * s, y0 + hh * 0.4, fz + 1.15, 1.6, 0.6, 0.3), eye, group="glow", tag="eye")
        B.add(hd, C(0, y0 - 1.6, fz - 0.2, hw - 1.0, 2.4, 2.6), "rock", tag="jaw")
    elif kind == "bell":
        B.add(hd, C(0, y0 - 1.0, 0.2, hw + 2.6, hh + 1.8, hd_ + 2.6), "accent", tag="bell")
        B.add(hd, C(0, y0 + hh + 0.8, 0.2, hw - 1.0, 1.6, hd_ - 1.0), "accent", tag="bell")
        B.add(hd, C(0, y0 - 1.4, 0.2, hw + 3.2, 0.8, hd_ + 3.2), "accent", tag="lip")
        for sx in (-1.4, 1.4):
            B.add(hd, C(sx * s, y0 + hh * 0.42, fz + 1.35, 1.2, 1.4, 0.3), eye, group="glow", tag="eye")
    if B.spec.get("horns"):
        L = B.spec["horns"]
        for side in (1, -1):
            hn = Part("horn%d" % (side > 0), (side * hw / 2, y0 + hh * 0.8, 0.4), (("z", side * -40), ("x", -20)), hd)
            B.add(hn, C(side * hw / 2, y0 + hh * 0.8, 0.4, 1.6, L * 0.4, 1.6), B.spec.get("horn_mat", "bone"), tag="horn")
            B.add(hn, C(side * hw / 2, y0 + hh * 0.8 + L * 0.4, 0.0, 1.1, L * 0.35, 1.1), B.spec.get("horn_mat", "bone"), tag="horn")
            B.add(hn, C(side * hw / 2, y0 + hh * 0.8 + L * 0.75, -0.4, 0.7, L * 0.3, 0.7), B.spec.get("horn_mat", "bone"), tag="horn")
    if B.spec.get("crown"):
        mat = B.spec["crown"]
        for k, (x, z) in enumerate(((-2.4, 2.6), (0, 2.9), (2.4, 2.6), (-2.8, 0), (2.8, 0), (-2.4, -2.6), (2.4, -2.6))):
            B.add(hd, C(x * s, y0 + hh + 0.4, z * s + 0.2, 0.9, 2.2 + 1.4 * h3(k, 2, 3), 0.9), mat, tag="crown")
        B.add(hd, C(0, y0 + hh - 0.4, 0.2, hw + 0.6, 1.2, hd_ + 0.6), "accent", tag="circlet")
    if B.spec.get("head_spikes"):
        B.spikes(hd, (0, y0 + hh, 0), B.spec["head_spikes"], 3.2, mat=B.spec.get("spike_mat", "crystal"), seed=11)
    return hd


def arms(B, kind):
    to = B.parts["torso"]
    big = B.spec.get("big_arm", 1.0)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * B.sw
        k = big if (nm == "r" and big > 1) else 1.0
        t = B.arm_t * k
        up = B.parts["arm_" + nm] = Part("arm_" + nm, (x, 31.6, 0), (("x", -26), ("z", side * 6)), to)
        fore = B.parts["fore_" + nm] = Part("fore_" + nm, (x, 22.4, 0), (("x", -56 if side < 0 else -64),), up)
        hand = B.parts["hand_" + nm] = Part("hand_" + nm, (x, 14.0, 0), (), fore)
        if kind == "plate":
            B.add(up, C(x, 22.6, 0, t, 9.4, t + 0.2), "plate", tag="rerebrace")
            B.add(fore, C(x, 14.4, 0, t - 0.2, 8.4, t), "plate", tag="vambrace")
            B.add(fore, C(x, 21.0, -0.6, t + 0.4, 2.6, t + 0.4), "metal", tag="couter")
            B.add(hand, C(x, 11.0, 0.2, t + 0.2, 3.4, t + 0.2), "metal", tag="gauntlet")
            B.add(hand, C(x, 15.0, 0.2, t + 0.6, 1.6, t + 0.6), "metal", tag="cuff")
        elif kind in ("cloth", "robe"):
            B.add(up, C(x, 22.6, 0, t + 0.2, 9.4, t + 0.4), "cloth", tag="sleeve")
            B.add(fore, C(x, 14.4, 0, t + 0.6 if kind == "robe" else t, 8.4, t + 0.8 if kind == "robe" else t), "cloth", tag="sleeve")
            B.add(hand, C(x, 11.0, 0.2, t - 0.4, 3.2, t - 0.4), "skin" if kind == "cloth" else B.spec.get("hand_mat", "skin"), tag="hand")
            B.add(fore, C(x, 14.0, 0, t + 0.8, 1.4, t + 1.0), "leather" if kind == "cloth" else "accent", tag="cuff")
        elif kind == "leather":
            B.add(up, C(x, 22.6, 0, t, 9.4, t + 0.2), "cloth", tag="sleeve")
            B.add(fore, C(x, 14.4, 0, t, 8.4, t + 0.2), "leather", tag="bracer")
            B.add(hand, C(x, 11.0, 0.2, t - 0.2, 3.2, t), "leather", tag="glove")
        elif kind == "bare":
            B.add(up, C(x, 22.2, 0, t + 0.4, 9.8, t + 0.6), "skin", tag="bicep")
            B.add(fore, C(x, 14.2, 0, t + 0.2, 8.8, t + 0.4), "skin", tag="forearm")
            B.add(hand, C(x, 11.0, 0.2, t, 3.4, t + 0.2), "skin", tag="fist")
            if B.spec.get("bracers"):
                B.add(fore, C(x, 16.0, 0, t + 0.8, 3.0, t + 1.0), B.spec["bracers"], tag="bracer")
        elif kind == "rock":
            B.add(up, C(x, 21.8, 0, t + 1.6, 10.2, t + 1.8), "rock", tag="arm")
            B.add(fore, C(x, 13.8, 0, t + 2.0, 9.2, t + 2.2), "rock", tag="forearm")
            B.add(hand, C(x, 9.6, 0.2, t + 2.6, 4.6, t + 2.8), "rock", tag="fist")
        elif kind == "chitin":
            B.add(up, C(x, 22.6, 0, t - 0.2, 9.4, t), "scale", tag="arm")
            B.add(fore, C(x, 14.4, 0, t, 8.4, t + 0.2), "scale", tag="forearm")
            B.add(hand, C(x, 11.0, 0.2, t - 0.2, 3.2, t), "scale", tag="hand")
        elif kind == "fur":
            B.add(up, C(x, 22.2, 0, t + 0.6, 9.8, t + 0.8), "fur", tag="arm")
            B.add(fore, C(x, 14.2, 0, t + 0.4, 8.8, t + 0.6), "fur", tag="forearm")
            B.add(hand, C(x, 11.0, 0.2, t + 0.2, 3.4, t + 0.4), "skin", tag="paw")
        elif kind == "feather":
            B.add(up, C(x, 22.6, 0, t + 0.6, 9.4, t + 1.6), "feather", tag="wingarm")
            B.add(fore, C(x, 14.4, 0, t, 8.4, t + 0.6), "feather", tag="wingarm")
            B.add(fore, C(x + side * 1.2, 10.0, -1.6, 0.6, 12.0, 4.4), "feather", tag="flight")
            B.add(hand, C(x, 11.0, 0.2, t - 0.6, 3.2, t - 0.4), "skin", tag="talon_hand")
        if B.spec.get("claws") and nm in B.spec.get("claw_hands", "lr"):
            for c in (-1, 0, 1):
                B.add(hand, C(x + c * 1.0, 8.0, 1.0, 0.6, 3.6, 0.6), B.spec.get("claw_mat", "bone"), tag="claw")


# ---------------------------------------------------------------- what they hold

GRIP = {"r": (-1, 12.6, 1.4), "l": (1, 12.6, 1.0)}


def hold(B, nm, kind, opt=None):
    """a weapon or tool in a hand: built along +y from the grip, the whole thing turned up and forward like the
    Frostbound's halberd; opt: per kind (len, head size, mats)"""
    o = opt or {}
    sx, gy, gz = GRIP[nm]
    x = sx * B.sw
    big = B.spec.get("big_arm", 1.0) if nm == "r" else 1.0
    gy = 14.0 - 1.4 * big
    hand = B.parts["hand_" + nm]
    S = o.get("size", 1.0)
    shaft = o.get("shaft", "wood")
    head = o.get("head", "metal")
    tilt = o.get("tilt", 78 if kind in ("halberd", "spear", "staff", "pick2", "maul", "greatsword", "banner", "scythe") else 72)
    if kind in ("lantern", "censer", "chain_ball", "orb"):
        w = Part("held_" + nm, (x, 12.0, 0.4), (("x", 86),), hand)
        B.add(w, C(x, 12.0 - 7.4 * S, 0.4, 0.3, 7.4 * S, 0.3), o.get("chain", "metal"), tag="chain")
        if kind == "lantern":
            B.add(w, C(x, 12.0 - 11.0 * S, 0.4, 3.2 * S, 3.6 * S, 3.2 * S), head, tag="lantern")
            B.add(w, C(x, 12.0 - 10.6 * S, 0.4, 3.4 * S, 2.6 * S, 2.6 * S), "glow", group="glow", tag="flame")
            B.add(w, C(x, 12.0 - 7.8 * S, 0.4, 2.0 * S, 0.8, 2.0 * S), head, tag="lantern")
        elif kind == "censer":
            B.add(w, C(x, 12.0 - 11.0 * S, 0.4, 3.2 * S, 3.6 * S, 3.2 * S), head, tag="censer")
            B.add(w, C(x, 12.0 - 10.4 * S, 0.4, 3.4 * S, 2.2 * S, 2.4 * S), "glow", group="glow", tag="ember")
        elif kind == "chain_ball":
            B.add(w, C(x, 12.0 - 12.4 * S, 0.4, 4.6 * S, 4.6 * S, 4.6 * S), head, tag="ball")
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                B.add(w, C(x + d[0] * 2.6 * S, 12.0 - 10.8 * S, 0.4 + d[1] * 2.6 * S, 1.0, 1.4, 1.0), "accent", tag="spike")
        else:
            B.add(w, C(x, 12.0 - 12.0 * S, 0.4, 4.0 * S, 4.0 * S, 4.0 * S), "glow", group="glow", tag="orb")
        return w
    if kind == "shield":
        sh = Part("shield_" + nm, (x, 18.0, 0), (), B.parts["fore_" + nm])
        w, h = o.get("w", 10.0) * S, o.get("h", 16.0) * S
        out = x + sx * 2.6
        B.add(sh, C(out, 18.0 - h / 2 - 2, 0.4, 1.0, h, w), head, tag="shield")
        B.add(sh, C(out + sx * 0.6, 18.0 - h / 2 - 1.4, 0.4, 0.5, h - 1.2, w - 1.2), o.get("face", "cloth"), tag="shield_face")
        B.add(sh, C(out + sx * 1.0, 18.0 - 3, 0.4, 0.5, 4.0, 2.0), o.get("boss", "accent"), tag="emblem")
        B.add(sh, C(out + sx * 1.0, 18.0 - 1.6, 0.4, 0.5, 1.4, 5.0), o.get("boss", "accent"), tag="emblem")
        B.add(sh, C(out + sx * 0.5, 18.0 - 2 + 0.2 - 0.8, 0.4, 1.6, 0.8, w + 0.4), "accent", tag="rim")
        B.add(sh, C(out + sx * 0.5, 18.0 - h - 2, 0.4, 1.6, 0.8, w + 0.4), "accent", tag="rim")
        return sh
    if kind == "claws_long":
        w = Part("held_" + nm, (x, gy, gz), (("x", 70),), hand)
        for c in (-1, 0, 1):
            B.add(w, C(x + c * 1.2, gy, gz, 0.6, 7.0 * S, 1.0), head, tag="claw")
        return w
    w = Part("held_" + nm, (x, gy, gz), (("x", tilt), ("z", 6 * -sx)), hand)
    L = o.get("len", {"sword": 16, "dagger": 7, "greatsword": 24, "spear": 40, "halberd": 40, "staff": 34, "pick": 16,
                      "pick2": 26, "hammer": 16, "maul": 26, "axe": 18, "cleaver": 16, "scythe": 34, "club": 16,
                      "rapier": 18, "banner": 44, "harpoon": 34, "whip": 12, "book": 0, "bow": 0, "trident": 34,
                      "torch": 12, "anchor": 26, "net": 0, "flail": 14}.get(kind, 16)) * S
    if kind in ("sword", "greatsword", "dagger", "rapier", "cleaver"):
        bw = {"sword": 2.4, "greatsword": 4.2, "dagger": 1.8, "rapier": 1.0, "cleaver": 5.0}[kind] * S
        grip = (5 if kind == "greatsword" else 3.4) * S
        B.add(w, C(x, gy - grip, gz, 1.2, grip, 1.2), o.get("grip", "leather"), tag="grip")
        B.add(w, C(x, gy - grip - 1.2, gz, 1.8, 1.4, 1.8), "accent", tag="pommel")
        B.add(w, C(x, gy + 0.6, gz, 1.6, 1.2, (6.0 if kind != "dagger" else 3.6) * S), o.get("guard", "accent"), tag="guard")
        B.add(w, C(x, gy + 1.8, gz + (bw / 2 - 1.2 if kind == "cleaver" else 0), 0.8, L, bw), head, tag="blade")
        B.add(w, C(x, gy + 1.8 + L, gz, 0.7, 1.6 * S, max(0.6, bw * 0.55)), head, tag="tip")
        if o.get("glow_edge"):
            B.add(w, C(x, gy + 3.0, gz + bw / 2 + 0.1, 0.5, L - 2, 0.4), "glow", group="glow", tag="edge")
        if kind == "greatsword":
            B.add(w, C(x, gy + 1.8, gz, 1.2, L * 0.8, 1.2), "dark", tag="fuller")
    elif kind in ("spear", "halberd", "harpoon", "trident", "banner", "scythe", "staff"):
        B.add(w, C(x, gy - L * 0.42, gz, 1.2 * S, L, 1.2 * S), shaft, tag="haft")
        top = gy + L * 0.58
        if kind == "spear":
            B.add(w, C(x, top - 0.6, gz, 1.8, 1.4, 1.8), "accent", tag="collar")
            B.add(w, C(x, top + 0.6, gz, 0.9, 6.0 * S, 2.6 * S), head, tag="spearhead")
            B.add(w, C(x, top + 6.4 * S, gz, 0.8, 2.0 * S, 1.2), head, tag="tip")
        elif kind == "halberd":
            B.add(w, C(x, top - 1.0, gz, 1.8, 1.4, 1.8), "accent", tag="collar")
            B.add(w, C(x, top, gz, 0.9, 7.0 * S, 0.9), head, tag="spike")
            B.add(w, ((x - 0.4, top - 3.6, gz + 0.6), (0.8, 6.0 * S, 4.6 * S)), head, tag="axe")
            B.add(w, ((x - 0.4, top - 1.6, gz - 2.8), (0.8, 2.0, 2.8)), head, tag="beak")
        elif kind == "harpoon" or kind == "trident":
            for dz in ((-1.6, 0, 1.6) if kind == "trident" else (0,)):
                B.add(w, C(x, top, gz + dz, 0.8, 5.0 * S, 0.8), head, tag="tine")
                B.add(w, C(x, top + 3.0 * S, gz + dz + 0.6, 0.6, 1.2, 1.2), head, tag="barb")
            B.add(w, C(x, top - 0.6, gz, 1.2, 1.0, 4.0 if kind == "trident" else 1.6), head, tag="crossbar")
        elif kind == "banner":
            B.add(w, C(x, top - 3.0, gz + 6.0, 1.0, 1.0, 13.0), shaft, tag="crossbar")
            B.add(w, ((x - 0.3, top - 21.0, gz + 0.8), (0.6, 18.0, 11.2)), o.get("cloth", "rag"), tag="flag")
            B.add(w, ((x - 0.45, top - 13.0, gz + 4.0), (0.9, 6.0, 4.8)), "accent", tag="flag_sigil")
            B.add(w, C(x, top + 1.0, gz, 0.9, 5.0, 0.9), head, tag="finial")
        elif kind == "scythe":
            B.add(w, ((x - 0.4, top - 1.0, gz), (0.8, 2.4, 14.0 * S)), head, tag="blade")
            B.add(w, ((x - 0.4, top - 2.6, gz + 10.0 * S), (0.8, 2.0, 4.0 * S)), head, tag="blade")
        elif kind == "staff":
            topk = o.get("top", "crystal")
            B.add(w, C(x, top - 1.0, gz, 2.0, 1.4, 2.0), "accent", tag="collar")
            if topk == "crystal":
                for dx, dz in ((-1.1, 0), (1.1, 0), (0, -1.1), (0, 1.1)):
                    B.add(w, C(x + dx, top, gz + dz, 0.6, 3.0, 0.6), "accent", tag="claw")
                B.add(w, C(x, top + 0.4, gz, 2.2 * S, 6.0 * S, 2.2 * S), "crystal", group="glow", tag="crystal")
            elif topk == "skull":
                B.add(w, C(x, top + 0.2, gz, 3.0 * S, 3.4 * S, 3.2 * S), "bone", tag="skull")
                B.add(w, C(x, top + 1.6 * S, gz + 1.65 * S, 2.0 * S, 0.8, 0.2), "glow", group="glow", tag="eyes")
            elif topk == "lantern":
                B.add(w, C(x, top + 0.4, gz, 3.0 * S, 3.6 * S, 3.0 * S), "accent", tag="lantern")
                B.add(w, C(x, top + 0.8, gz, 3.2 * S, 2.4 * S, 2.2 * S), "glow", group="glow", tag="flame")
            elif topk == "orb":
                B.add(w, C(x, top + 0.4, gz, 3.4 * S, 3.4 * S, 3.4 * S), "glow", group="glow", tag="orb")
                for dx, dz in ((-1.8, 0), (1.8, 0), (0, -1.8), (0, 1.8)):
                    B.add(w, C(x + dx, top - 0.4, gz + dz, 0.6, 4.2 * S, 0.6), "accent", tag="claw")
            elif topk == "hook":
                B.add(w, C(x, top, gz, 1.0, 5.0 * S, 1.0), shaft, tag="haft")
                B.add(w, ((x - 0.5, top + 5.0 * S, gz - 3.0), (1.0, 1.0, 4.0)), shaft, tag="hook")
                B.add(w, C(x, top + 1.6 * S, gz - 2.6, 2.0, 2.4, 2.0), "glow", group="glow", tag="lamp")
    elif kind in ("hammer", "maul", "pick", "pick2", "axe", "club", "anchor", "flail"):
        B.add(w, C(x, gy - L * (0.42 if kind in ("maul", "pick2", "anchor") else 0.2), gz, 1.2 * S, L, 1.2 * S), shaft, tag="haft")
        top = gy + L * (0.58 if kind in ("maul", "pick2", "anchor") else 0.8)
        hs = o.get("head_size", 1.0) * S
        if kind in ("hammer", "maul"):
            B.add(w, C(x, top - 2.0 * hs, gz, 4.0 * hs, 4.6 * hs, 7.0 * hs), head, tag="hammerhead")
            B.add(w, C(x, top - 2.4 * hs, gz, 4.4 * hs, 1.0, 7.4 * hs), "accent", tag="band")
            B.add(w, C(x, top + 2.4 * hs, gz, 1.2, 2.0 * hs, 1.2), head, tag="spike")
        elif kind in ("pick", "pick2"):
            B.add(w, C(x, top - 1.6 * hs, gz, 2.0 * hs, 2.6 * hs, 3.0 * hs), "accent", tag="eye")
            B.add(w, ((x - 0.6 * hs, top - 1.0 * hs, gz + 1.4 * hs), (1.2 * hs, 1.6 * hs, 7.0 * hs)), head, tag="pick")
            B.add(w, ((x - 0.4 * hs, top - 1.6 * hs, gz + 7.6 * hs), (0.8 * hs, 1.4 * hs, 1.4 * hs)), head, tag="pick")
            B.add(w, ((x - 0.6 * hs, top - 1.0 * hs, gz - 7.4 * hs), (1.2 * hs, 1.6 * hs, 6.0 * hs)), head, tag="pick")
        elif kind == "axe":
            B.add(w, ((x - 0.5, top - 4.6 * hs, gz + 0.6), (1.0, 7.0 * hs, 5.6 * hs)), head, tag="axehead")
            B.add(w, ((x - 0.5, top - 5.6 * hs, gz + 5.6 * hs), (1.0, 9.0 * hs, 1.2)), head, tag="edge")
        elif kind == "club":
            B.add(w, C(x, top - 4.0 * hs, gz, 3.4 * hs, 7.0 * hs, 3.4 * hs), shaft, tag="club")
            for k in range(5):
                a = k * 1.25
                B.add(w, C(x + math.cos(a) * 1.9 * hs, top - 3.0 * hs + k * 1.2, gz + math.sin(a) * 1.9 * hs, 0.8, 0.8, 0.8), head, tag="nail")
        elif kind == "anchor":
            B.add(w, C(x, top - 2.0, gz, 1.6, 2.0, 7.0 * hs), head, tag="stock")
            B.add(w, ((x - 0.7, gy - L * 0.42 - 1.0, gz - 6.0 * hs), (1.4, 1.6, 12.0 * hs)), head, tag="arms")
            for dz in (-6.0, 4.6):
                B.add(w, ((x - 0.7, gy - L * 0.42 - 1.0, gz + dz * hs), (1.4, 4.0, 1.4 * hs)), head, tag="fluke")
        elif kind == "flail":
            B.add(w, C(x, top, gz, 0.4, 5.0, 0.4), "metal", tag="chain")
            B.add(w, C(x, top + 5.0, gz, 3.4 * hs, 3.4 * hs, 3.4 * hs), head, tag="ball")
    elif kind == "bow":
        bw = Part("bow_" + nm, (x, 12.6, 1.0), (("x", -90),), hand)
        B.add(bw, C(x, 11.2, 1.0, 1.4, 3.0, 1.6), "leather", tag="grip")
        for side in (1, -1):
            for k, (ln, dz) in enumerate(((5.0, 0.6), (5.0, 1.8), (4.0, 3.4))):
                y0 = 12.6 + side * (1.4 + k * 4.6) - (ln if side < 0 else 0)
                B.add(bw, C(x, y0, 1.0 - dz, 1.1 - k * 0.2, ln, 1.2 - k * 0.2), shaft, tag="limb")
        B.add(bw, C(x, 12.6 - 15.0, 1.0 - 4.6, 0.3, 30.0, 0.3), "accent", tag="string")
        return bw
    elif kind == "book":
        bk = Part("book_" + nm, (x, 11.0, 1.0), (("x", 80),), hand)
        B.add(bk, C(x, 8.0, 2.0, 1.4, 6.4, 5.0), o.get("cover", "leather"), tag="tome")
        B.add(bk, C(x, 8.3, 2.0, 1.6, 5.8, 4.4), "bone", tag="pages")
        B.add(bk, C(x, 10.6, 4.6, 1.8, 1.2, 0.4), "glow", group="glow", tag="rune")
        return bk
    elif kind == "torch":
        B.add(w, C(x, gy - 4.0, gz, 1.2, L, 1.2), shaft, tag="haft")
        B.add(w, C(x, gy + L - 4.0, gz, 2.0, 2.6, 2.0), "glow", group="glow", tag="flame")
    elif kind == "net":
        nt = Part("net_" + nm, (x, 12.0, 0.4), (("x", 86),), hand)
        for k in range(5):
            B.add(nt, C(x + (k - 2) * 1.6, 12.0 - 12.0, 0.4, 0.3, 12.0, 0.3), "rag", tag="net")
        for k in range(4):
            B.add(nt, C(x, 12.0 - 2.4 - k * 3.0, 0.4, 7.0, 0.3, 0.3), "rag", tag="net")
        for k in (-2, 2):
            B.add(nt, C(x + k * 1.6, 12.0 - 13.2, 0.4, 1.0, 1.2, 1.0), "metal", tag="weight")
        return nt
    return w


def back(B, kind, opt=None):
    o = opt or {}
    to = B.parts["torso"]
    d = 5.2 * B.bulk ** 0.7
    if kind == "cape":
        cp = Part("cape", (0, 33.0, -d / 2 - 0.4), (("x", 16),), to)
        B.add(cp, C(0, 14.0, -d / 2 - 0.4, 10.4 * B.bulk ** 0.5, 19.0, 0.7), o.get("mat", "rag"), tag="cape")
    elif kind == "cloak":
        cp = Part("cloak", (0, 33.0, -d / 2 - 0.4), (("x", 8),), to)
        B.add(cp, C(0, 8.0, -d / 2 - 0.4, 12.0 * B.bulk ** 0.5, 25.0, 0.8), o.get("mat", "rag"), tag="cloak")
    elif kind == "wings":       # folded: they never fly, they mantle
        for side in (1, -1):
            wg = Part("wing%d" % (side > 0), (side * 3.0, 31.0, -d / 2), (("z", side * -14), ("y", side * 18)), to)
            B.add(wg, C(side * 4.0, 18.0, -d / 2 - 1.0, 3.0, 16.0, 1.2), o.get("mat", "feather"), tag="wing")
            B.add(wg, C(side * 6.0, 10.0, -d / 2 - 1.4, 3.6, 22.0, 0.9), o.get("mat", "feather"), tag="wing")
            B.add(wg, C(side * 4.0, 31.0, -d / 2 - 1.0, 4.0, 4.0, 1.6), o.get("bone", "bone"), tag="wing_arm")
    elif kind == "crystals":
        B.spikes(to, (0, 30.0, -d / 2), o.get("n", 6), o.get("len", 5.0), mat=o.get("mat", "crystal"), seed=5, spread=3.0,
                 tilt=(("x", -30),))
    elif kind == "pack":
        B.add(to, C(0, 22.4, -d / 2 - 2.0, 6.6, 8.6, 3.8), o.get("mat", "leather"), tag="pack")
        B.add(to, C(0, 31.0, -d / 2 - 2.0, 7.4, 1.2, 4.0), "wood", tag="pack_roll")
        if o.get("lamp"):
            B.add(to, C(2.6, 31.4, -d / 2 - 2.2, 2.0, 2.4, 2.0), "glow", group="glow", tag="lamp")
    elif kind == "quiver":
        q = Part("quiver", (2.6, 30.0, -d / 2 - 1.0), (("z", -24),), to)
        B.add(q, C(2.6, 21.0, -d / 2 - 1.0, 2.6, 9.0, 2.6), "leather", tag="quiver")
        for k, dx in enumerate((-0.6, 0.4, 1.2)):
            B.add(q, C(2.6 + dx, 30.0, -d / 2 - 1.0 + (k - 1) * 0.6, 0.4, 3.2, 0.4), "wood", tag="arrow")
    elif kind == "shell":
        B.add(to, C(0, 21.0, -d / 2 - 1.8, 9.4 * B.bulk, 12.4, 3.4), o.get("mat", "scale"), tag="shell")
        B.add(to, C(0, 23.0, -d / 2 - 3.0, 7.0 * B.bulk, 8.4, 1.6), o.get("mat", "scale"), tag="shell")
        if o.get("barnacles"):
            B.spikes(to, (0, 28.0, -d / 2 - 3.6), 5, 1.6, mat=o.get("barnacles"), seed=8, spread=3.4, tilt=(("x", -70),))
    elif kind == "cart":
        B.add(to, C(0, 19.4, -d / 2 - 3.6, 9.6, 8.0, 6.4), "metal", tag="cart")
        B.add(to, C(0, 26.4, -d / 2 - 3.6, 8.4, 1.4, 5.2), "rock", tag="ore")
        B.spikes(to, (0, 27.6, -d / 2 - 3.6), 5, 3.6, mat="crystal", seed=21, spread=2.4)
    elif kind == "chimney":
        for k, sx in enumerate((-2.4, 2.4)):
            B.add(to, C(sx, 28.0, -d / 2 - 1.4, 2.0, 12.0 + k * 2, 2.0), "metal", tag="flue")
            B.add(to, C(sx, 40.0 + k * 2, -d / 2 - 1.4, 2.4, 1.4, 2.4), "glow", group="glow", tag="ember")
    elif kind == "tail":
        tl = Part("tail", (0, 19.4, -2.6), (("x", -40),), B.parts["hips"])
        for k in range(4):
            B.add(tl, C(0, 19.4 - 4.0 * (k + 1), -2.6 - k * 0.4, 2.6 - k * 0.5, 4.2, 2.6 - k * 0.5), o.get("mat", "scale"), tag="tail")
    elif kind == "halo":
        hd = B.parts["head"]
        for k in range(12):
            a = k * math.pi / 6
            B.add(hd, C(math.cos(a) * 5.2, 39.0 + math.sin(a) * 5.2, -3.6, 1.2, 1.2, 0.6), o.get("mat", "glow"), group="glow", tag="halo")


def biped(name, spec):
    """the whole two-legged monster from its spec"""
    B = Build(name, spec)
    legs(B, spec.get("legs", "plate"))
    hips_dress(B, spec.get("hips", spec.get("legs", "plate")))
    torso(B, spec.get("torso", "plate"))
    shoulders(B, spec.get("shoulders"), spec.get("shoulder_size", 1.0))
    head(B, spec.get("head", "helm"))
    arms(B, spec.get("arms", "plate"))
    for kind in ([spec["back"]] if isinstance(spec.get("back"), str) else spec.get("back", [])):
        back(B, kind, spec.get("back_opt", {}).get(kind) if isinstance(spec.get("back_opt"), dict) else None)
    if spec.get("right"):
        hold(B, "r", spec["right"], spec.get("right_opt"))
    if spec.get("left"):
        hold(B, "l", spec["left"], spec.get("left_opt"))
    for fn in spec.get("extra", []):
        fn(B)
    for b in B.s.boxes:                       # a monster's own take on a material (a puppet's skin is painted wood)
        b.mat = spec.get("extra_mats", {}).get(b.mat, b.mat)
    B.s.shaders = shaders(spec["theme"])
    scale_all(B, spec.get("build", {}).get("size", 1.0))
    return B


def scale_all(B, k):
    """grow (or shrink) the whole monster about its feet: every box and every pivot"""
    if k == 1.0:
        return
    seen = set()
    for b in B.s.boxes:
        b.lo = tuple(c * k for c in b.lo)
        b.size = tuple(c * k for c in b.size)
        b.pivot = tuple(c * k for c in b.pivot)
        p = b.part
        while p is not None and id(p) not in seen:
            seen.add(id(p))
            p.pivot = tuple(c * k for c in p.pivot)
            p.move = tuple(c * k for c in p.move)
            p = p.parent
    for p in B.parts.values():
        if id(p) not in seen:
            seen.add(id(p))
            p.pivot = tuple(c * k for c in p.pivot)


# ---------------------------------------------------------------- crawlers and beasts (Epic Fight's spider)

def crawler(name, spec):
    """a many-legged thing: body, head with mandibles, an abdomen, n legs (8, 6 or 4), each leg one bone (the spider's
    legs have no knee), the far part of each leg bent down so it stands"""
    B = Build(name, spec)
    sz = spec.get("size", 1.0)
    L = spec.get("leg_len", 1.0)
    bm, hm, am = spec.get("body_mat", "scale"), spec.get("head_mat", spec.get("body_mat", "scale")), spec.get("abdomen_mat", spec.get("body_mat", "scale"))
    body = B.parts["body"] = Part("body", (0, 8, 0))
    B.add(body, C(0, 6.0, 0, 7.0, 4.0, 7.0), bm, tag="thorax")
    hd = B.parts["head"] = Part("head", (0, 8, 3.6), (), body)
    B.add(hd, C(0, 5.6, 5.4, 5.0, 3.6, 4.0), hm, tag="head")
    for sx in (-1.2, -0.4, 0.4, 1.2):
        B.add(hd, C(sx, 8.0, 7.45, 0.6, 0.6, 0.2), "eye", group="glow", tag="eye")
    for sx in (-1, 1):
        B.add(hd, C(sx * 1.4, 4.4, 7.8, 0.9, 2.6, 1.6), spec.get("fang_mat", "bone"), tag="fang")
    if spec.get("pincers"):           # a crab's claws out in front of its face
        for sx in (-1, 1):
            pc = Part("pincer%d" % (sx > 0), (sx * 2.2, 6.0, 7.0), (("y", -sx * 20),), hd)
            B.add(pc, C(sx * 3.4, 4.6, 9.6, 2.2, 3.0, 5.6), spec.get("pincer_mat", hm), tag="pincer")
            B.add(pc, C(sx * 3.4, 6.6, 11.4, 1.6, 1.4, 3.6), spec.get("pincer_mat", hm), tag="pincer")
            B.add(pc, C(sx * 3.4, 4.2, 11.6, 1.4, 1.0, 3.0), spec.get("pincer_mat", hm), tag="pincer")
    ab = B.parts["abdomen"] = Part("abdomen", (0, 8, -3.4), (("x", -12),), body)
    B.add(ab, C(0, 5.4, -7.6, 8.6, 6.4, 9.0), am, tag="abdomen")
    B.add(ab, C(0, 11.6, -7.6, 6.6, 1.4, 7.0), am, tag="abdomen")
    n = spec.get("legs", 8)
    pairs = {8: (2.6, 0.9, -0.9, -2.6), 6: (2.4, 0, -2.4), 4: (2.4, -2.4)}[n]
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    j_of = {8: (1, 2, 3, 4), 6: (1, 2, 4), 4: (1, 4)}[n]
    for side, s in ((1, "l"), (-1, "r")):
        for k, z in enumerate(pairs):
            nm = "leg_%s%d" % (s, k)
            spread = (k - (len(pairs) - 1) / 2) * 22
            lg = B.parts[nm] = Part(nm, (side * 3.0, 7.2, z), (("y", -side * spread),), body)
            fem = Part(nm + "_f", (side * 3.0, 7.6, z), (("z", side * 34),), lg)        # up and out to the knee
            B.add(fem, C(side * (3.0 + 4.0 * L), 7.0, z, 8.0 * L, 1.6, 1.6), spec.get("leg_mat", bm), tag="femur")
            kx = 3.0 + 8.0 * L * math.cos(math.radians(34))
            ky = 7.6 + 8.0 * L * math.sin(math.radians(34))
            B.add(lg, C(side * kx, ky - 0.8, z, 1.9, 1.9, 1.9), spec.get("joint_mat", "accent"), tag="knee")
            tib = Part(nm + "_t", (side * kx, ky, z), (("z", side * -28),), lg)          # and down, splayed, to the ground
            ln = ky / math.cos(math.radians(28))
            B.add(tib, C(side * kx, ky - ln, z, 1.3, ln, 1.3), spec.get("leg_mat", bm), tag="boot")
            B.add(tib, C(side * kx, ky - ln - 0.6, z, 0.8, 1.2, 0.8), spec.get("joint_mat", "accent"), tag="boot")
            joints[nm] = ("LL" if side > 0 else "RL") + str(j_of[k])
    for fn in spec.get("extra", []):
        fn(B)
    B.s.shaders = shaders(spec["theme"])
    scale_all(B, sz)
    B.bones = list(B.parts)
    B.joints = joints
    return B


def beast(name, spec):
    """a four-legged beast on the spider: body, neck and head, a tail, four legs (front LL1/RL1, back LL4/RL4)"""
    B = Build(name, spec)
    sz = spec.get("size", 1.0)
    bm = spec.get("body_mat", "fur")
    body = B.parts["body"] = Part("body", (0, 14, 0))
    B.add(body, C(0, 11.0, -1.0, 7.0, 7.6, 15.0), bm, tag="body")
    B.add(body, C(0, 12.0, 5.2, 7.8, 8.0, 5.0), bm, tag="chest")
    nk = B.parts["neck"] = Part("neck", (0, 16, 7.4), (("x", -24),), body)
    B.add(nk, C(0, 13.6, 9.0, 4.4, 5.4, 4.6), bm, tag="neck")
    B.add(nk, C(0, 13.0, 13.4, 5.0, 4.6, 6.0), spec.get("head_mat", bm), tag="head")
    B.add(nk, C(0, 12.6, 17.4, 3.2, 2.6, 3.4), spec.get("head_mat", bm), tag="muzzle")
    B.add(nk, C(0, 11.8, 17.2, 2.8, 1.0, 3.0), "skin", tag="jaw")
    for k in range(3):
        B.add(nk, C(-0.8 + k * 0.8, 11.6, 18.9, 0.4, 1.0, 0.4), "bone", tag="fang")
    for sx in (-1.6, 1.6):
        B.add(nk, C(sx, 15.6, 16.2, 0.9, 0.7, 0.3), "eye", group="glow", tag="eye")
    tl = B.parts["tail"] = Part("tail", (0, 15.0, -8.4), (("x", 30),), body)
    for k in range(3):
        B.add(tl, C(0, 15.0, -9.4 - k * 3.0, 1.8 - k * 0.4, 1.6 - k * 0.3, 3.2), spec.get("tail_mat", bm), tag="tail")
    joints = {"body": "Root", "neck": "Head", "tail": "Stomach"}
    for nm, (x, z, j) in {"leg_fl": (2.6, 5.0, "LL1"), "leg_fr": (-2.6, 5.0, "RL1"), "leg_bl": (2.6, -6.4, "LL4"),
                          "leg_br": (-2.6, -6.4, "RL4")}.items():
        lg = B.parts[nm] = Part(nm, (x, 12.0, z), (), body)
        B.add(lg, C(x, 4.0, z, 2.6, 9.0, 3.0), spec.get("leg_mat", bm), tag="leg")
        B.add(lg, C(x, 0.0, z + 0.4, 2.4, 4.0, 2.4), spec.get("leg_mat", bm), tag="shank")
        B.add(lg, C(x, 0.0, z + 1.0, 2.8, 1.4, 3.6), spec.get("paw_mat", "dark"), tag="boot")
        joints[nm] = j
    for fn in spec.get("extra", []):
        fn(B)
    B.s.shaders = shaders(spec["theme"])
    scale_all(B, sz)
    B.bones = list(B.parts)
    B.joints = joints
    return B


# ================================================================ export

POINTS = {"eyes": ("head", (0, 37.2, 3.6))}


class Made:
    """a hand-built monster (tools/mobs/<gate>.py): its make() gives the boxes and the bones"""
    def __init__(self, spec):
        r = spec["make"]()
        self.s, self.parts = r[0], r[1]
        self.bones = list(self.parts)
        used = {id(b.part) for b in self.s.boxes}
        for p in self.parts.values():        # a bone with nothing on it (legs under a robe) still needs a mesh: a speck at its pivot
            if id(p) not in used:
                self.s.boxes.append(PB(p, tuple(c - 0.15 for c in p.pivot), (0.3, 0.3, 0.3), self.s.boxes[0].mat, tag="speck"))
        eyes = [b for b in self.s.boxes if b.tag == "eye" and b.part is self.parts.get("head")]
        if eyes:
            c = [sum(b.lo[i] + b.size[i] / 2 for b in eyes) / len(eyes) for i in range(3)]
            self.points = {"eyes": ("head", tuple(c))}
        if spec.get("rig") == "crawler":
            self.joints = r[2] if len(r) > 2 else self._joints()

    def _joints(self):
        j = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
        for n in self.parts:
            if n.startswith("leg_"):
                j[n] = ("LL" if n[4] == "l" else "RL") + str(int(n[5:]) + 1)
        return j


def build(name, spec):
    if "make" in spec:
        return Made(dict(spec, name=name))
    if spec.get("rig") == "crawler":
        return crawler(name, spec)
    if spec.get("rig") == "beast":
        return beast(name, spec)
    return biped(name, spec)


def export(name, spec, preview=False):
    V.T = spec.get("texel", 2)
    M.ASSETS = OUT
    B = build(name, spec)
    ground = ("boot", "foot")
    if preview:
        M.preview(B.s, name, ground_tags=ground)
        return B
    bones = B.bones if hasattr(B, "bones") else BONES
    pts = getattr(B, "points", {} if hasattr(B, "bones") else POINTS)
    M.export(B.s, B.parts, name, bones, pts, ground_tags=ground)
    return B


def main():
    import forge_specs as FS
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    names = []
    for a in args:
        names += FS.by_gate(a) if a in FS.GATES else [a]
    for n in names:
        spec = FS.SPECS[n]
        B = export(n, spec, preview="--preview" in sys.argv)
        print("%-18s %3d boxes  %s" % (n, len(B.s.boxes), spec.get("rig", "biped")))


if __name__ == "__main__":
    main()
