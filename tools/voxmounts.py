"""The five mounts a new player picks from with their class. Built like the hand-made monsters (E:/Ashbound/tools/vox*.py):
painted boxes on named parts. Units: 1 = 1/16 block, facing +z, y up, x to its left.

    ashmane     a burning warhorse: charcoal hide cracked over embers, iron barding, a mane and tail of fire
    rimehorn    a great stag: frost-white, deep ruff, a crown of ice antlers
    gravefang   a dire wolf: black fur, the bones worn outside, a skull for a face, soulfire
    thornback   a giant old boar: moss and flowers on its back, bark for armour, tusks as long as a man's arm
    stormdrake  a wyvern: indigo scales, gold belly, lightning in its crest and wings

    python tools/voxmounts.py [names]             previews for blender -b -P E:/Ashbound/tools/blender/preview_mob.py -- mount_ashmane@3.6
    python tools/voxmounts.py --export [names]    assets/ashbound/mounts/NAME.json + textures/entity/mount_NAME.png, drawn by client/MountRender.java

The export keeps every named part as a bone, in blocks at the model's size, with its pivot in the bind pose, so the game turns
bones about world axes. Quads come as lit, glow (drawn full bright) and flame (full bright, and the texture cycles FRAMES frames).
"""
import json
import math
import os
import sys

sys.path.insert(0, 'E:/Ashbound/tools')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import voxsword as V  # noqa: E402
from voxsword import Sword, ramp, shade, fbm, h3  # noqa: E402
from voxboss import Part, PB, C  # noqa: E402
import voxmob as M  # noqa: E402

IRON = ramp("#14141c", "#20202c", "#30303f", "#454556", "#5e5e72", "#808094", "#a8a8ba")
GOLD = ramp("#3a2408", "#6a4410", "#a06c18", "#d09a28", "#f0c850", "#ffe690")
SILVER = ramp("#2a3448", "#46566e", "#6c8098", "#9ab0c6", "#c8dae8", "#f0f8ff")
LEATHER = ramp("#180c06", "#2a160c", "#402414", "#58341e", "#74482c")
HOOF = ramp("#0e0c0c", "#1c1816", "#2e2622", "#443a32")
BONE = ramp("#4a3c2a", "#74644a", "#a0906c", "#c8ba92", "#e6dcb8", "#fbf6e0")
EMBER = ramp("#5a0c04", "#a82006", "#e84a0a", "#ff8a1c", "#ffc850", "#fff2b0")
FROST_FIRE = ramp("#10407a", "#1a78c0", "#30b4ec", "#74e4ff", "#c0f6ff", "#ffffff")
SOUL = ramp("#2a0a5a", "#5a18b0", "#8a3cec", "#b878ff", "#e0c0ff", "#ffffff")
SAP = ramp("#6a3a04", "#b07008", "#f0a818", "#ffd84a", "#fff6a0")
BOLT = ramp("#1830a0", "#2c5cf0", "#4c9cff", "#90e0ff", "#e0ffff", "#ffffff")
UNIT = 16.0
FRAMES = 4
FLAMES = ("fire", "fire2", "soul", "soul2")
HOT = {c[:3] for c in EMBER[1:] + SAP[1:]}


class Kit:
    def __init__(self, name):
        self.s = Sword("mount_" + name)
        self.parts = {}
        self.n = 0

    def part(self, name, pivot, rots=(), parent=None):
        p = self.parts[name] = Part(name, pivot, rots, parent)
        return p

    def add(self, part, box, mat, tag=None, group="lit", skip=()):
        b = PB(part, box[0], box[1], mat, tag=tag or part.name, group=group, skip=skip)
        self.s.boxes.append(b)
        return b

    def seg(self, parent, nm, base, specs, mat, group="lit", tag=None):
        """a chain of boxes, each turned from the last; returns the last part and where it ends"""
        part, at = parent, base
        for k, (w, d, ln, rots) in enumerate(specs):
            part = Part("%s%d" % (nm, k), at, rots, part)
            self.add(part, C(at[0], at[1], at[2], w, ln + 0.25, d), mat, tag=tag or nm, group=group)
            at = (at[0], at[1] + ln, at[2])
        return part, at

    def loaf(self, part, axis, a, b, steps, prof, mat, tag=None):
        """a body laid along z (or y) in slices, each slice two boxes crossed so it rounds off; prof(t) = width, height, centre"""
        d = (b - a) / steps
        for k in range(steps):
            t = (k + 0.5) / steps
            w, h, c = prof(t)
            at = a + (k + 0.5) * d
            if axis == "z":
                self.add(part, C(0, c - h / 2, at, w * 0.7, h, d + 0.1), mat, tag=tag)
                self.add(part, C(0, c - h * 0.36, at, w, h * 0.72, d + 0.1), mat, tag=tag)
            else:
                self.add(part, C(0, at - d / 2, c, w * 0.7, d + 0.1, h), mat, tag=tag)
                self.add(part, C(0, at - d / 2, c, w, d + 0.1, h * 0.7), mat, tag=tag)

    def leg(self, parent, names, x, top, z, lens, widths, rots, mats, feet="boot", tag=None):
        """three parts down to the ground; widths (x, z) per part; returns the three parts"""
        out = []
        y = top
        par = parent
        for k, nm in enumerate(names):
            p = self.part(nm, (x, y, z), ((("x", rots[k]),)), par)
            w, d = widths[k]
            self.add(p, C(x, y - lens[k], z, w, lens[k] + 0.3, d), mats[k], tag=feet if k == 2 else tag or nm)
            y -= lens[k]
            par = p
            out.append(p)
        return out

    def bone(self, part):
        while part.name not in self.parts:
            part = part.parent
        return part

    def export(self, name):
        s = self.s
        s.frames = FRAMES
        order = list(self.parts)
        for b in s.boxes:
            kind = "flame" if b.mat in FLAMES else "glow" if b.group == "glow" else "lit"
            b.group = "%s|%s" % (self.bone(b.part).name, kind)
        lo = min(b.world((a, 0, c))[1] for b in s.boxes if b.tag == "boot" for a in (0, 1) for c in (0, 1))
        seat = [b.world((0.5, 1, 0.5)) for b in s.boxes if b.tag == "saddle"]
        seat = (sum(p[1] for p in seat) / len(seat), sum(p[2] for p in seat) / len(seat)) if seat else (lo, 0)
        img, tris = s.build()
        height = img.size[1] // FRAMES
        out = {"frames": FRAMES, "bones": []}

        def q(v):
            return round(v, 3)

        for nm in order:
            part = self.parts[nm]
            parent = self.bone(part.parent).name if part.parent else None
            pv = part.apply(part.pivot)
            bone = {"name": nm, "parent": parent, "pivot": [q(pv[0] / UNIT), q((pv[1] - lo) / UNIT), q(pv[2] / UNIT)]}
            for kind in ("lit", "glow", "flame"):
                flat = []
                ts = tris.get("%s|%s" % (nm, kind), [])
                for i in range(0, len(ts), 2):
                    a, b, c = ts[i]
                    d = ts[i + 1][2]
                    for p, uv, n in (a, b, c, d):
                        flat += [q(p[0] / UNIT), q((p[1] - lo) / UNIT), q(p[2] / UNIT), round(uv[0], 5), round((1 - uv[1]) / FRAMES, 5)]
                    flat += [q(a[2][0]), q(a[2][1]), q(a[2][2])]
                bone[kind] = flat
            out["bones"].append(bone)
        A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "resources", "assets", "ashbound")
        os.makedirs(os.path.join(A, "mounts"), exist_ok=True)
        with open(os.path.join(A, "mounts", name + ".json"), "w", encoding="utf-8", newline="\n") as fp:
            json.dump(out, fp, separators=(",", ":"))
        img.save(os.path.join(A, "textures", "entity", "mount_%s.png" % name))
        # what burns under the hide: a second texture, only the hot pixels, laid over the lit quads additively
        hot = img.copy().convert("RGBA")
        px = hot.load()
        for y in range(hot.size[1]):
            for x in range(hot.size[0]):
                if px[x, y][:3] not in HOT:
                    px[x, y] = (0, 0, 0, 0 if px[x, y][3] == 0 else 255)
        hot.save(os.path.join(A, "textures", "entity", "mount_%s_hot.png" % name))
        print(name, "seat y %.3f z %.3f blocks at model size, %d quads, atlas %s" % ((seat[0] - lo) / UNIT, seat[1] / UNIT, sum(len(v) for v in tris.values()) // 2, img.size))


# ------------------------------------------------------------------ paint

def tone(n, j, h):
    return 0.15 * n[1] + 0.05 * n[2] - 0.1 * (j / max(1, h - 1))


def fur(R, streak=0.3, spot=0.28):
    def paint(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        v = 0.42 + tone(n, j, h) * 1.3 + spot * (fbm(x * 0.28, y * 0.28, z * 0.28) - 0.5) + streak * (h3(i // 2, j // 3, int(z)) - 0.5) * 0.5
        return shade(R, v, i, j)
    return paint


def plate(R, trim=None):
    def paint(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        if trim and key in "nsew" and (j <= 1 or j >= h - 2):
            return shade(trim, 0.7, i, j)
        v = 0.45 + tone(n, j, h) * 1.6 + 0.2 * (fbm(x * 0.6, y * 0.6, z * 0.6) - 0.5)
        if key in "nsew" and (i == 0 or i == w - 1):
            v += 0.16
        return shade(R, v, i, j)
    return paint


def cracked(R, hot, wide=0.032):
    """a hide split over something burning"""
    base = fur(R, 0.2, 0.2)

    def paint(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        c = abs(fbm(x * 0.16 + 4, y * 0.2, z * 0.16) - 0.5)
        if c < wide:
            return shade(hot, 0.95 - c / wide * 0.7, i, j)
        if c < wide * 1.8:
            return shade(hot, 0.1, i, j)
        return base(p, n, b, key, i, j, w, h, fr)
    return paint


def flame(R, seed=1.0):
    """a tongue of fire: the sides are cut to a ragged top, hottest at the root"""
    def paint(p, n, b, key, i, j, w, h, fr):
        if key in "ud":
            return shade(R, 0.5, i, j)
        t = j / max(1, h - 1)
        edge = 0.62 * fbm(i * 0.38 + seed + ord(key) % 7, b.lo[2] * 0.3, b.lo[0] * 0.3 + fr * 2)
        if t < edge:
            return None
        return shade(R, 0.15 + 0.85 * (t - edge) / max(0.05, 1 - edge), i, j)
    return paint


def glow(R, at=0.7):
    def paint(p, n, b, key, i, j, w, h, fr):
        return shade(R, at + 0.3 * (fbm(p[0] * 0.5, p[1] * 0.5, p[2] * 0.5) - 0.3), i, j)
    return paint


def ice(R):
    def paint(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        v = 0.5 + 0.3 * (n[0] * 0.4 + n[1] * 0.8) + 0.3 * (fbm(x * 0.5, y * 0.25, z * 0.5) - 0.5) + (0.22 if i == 0 else 0)
        return shade(R, v, i, j)
    return paint


def cloth(R, band=None):
    def paint(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        if key in "nsew" and h > 8 and j > h - 1 - 3 * h3(i // 3, 7, 3):
            return None
        if band and key in "nsew" and h - 7 < j < h - 3:
            return shade(band, 0.65, i, j)
        v = 0.5 + tone(n, j, h) + 0.2 * (fbm(x * 0.4, y * 0.2, z * 0.4) - 0.5) - (0.08 if i % 5 == 0 else 0)
        return shade(R, v, i, j)
    return paint


def eye(R):
    return lambda p, n, b, key, i, j, w, h, fr: shade(R, 0.85, i, j)


# ------------------------------------------------------------------ Ashmane

def saddle(k, part, z, y, w, mats=("leather", "gold")):
    k.add(part, C(0, y, z, w, 1.6, 11), mats[0], tag="saddle")
    k.add(part, C(0, y + 1.2, z + 5, w * 0.62, 2.8, 1.8), mats[0], tag="saddle")
    k.add(part, C(0, y + 1.2, z - 5.4, w * 0.8, 3.6, 1.8), mats[0], tag="saddle")
    k.add(part, C(0, y + 3.8, z + 5, w * 0.68, 0.7, 2.1), mats[1], tag="saddle")
    k.add(part, C(0, y + 4.6, z - 5.4, w * 0.88, 0.7, 2.1), mats[1], tag="saddle")


def ashmane():
    k = Kit("ashmane")
    s = k.s
    s.shaders = dict(hide=cracked(ramp("#08070a", "#12101a", "#1c1824", "#2a2430", "#3a3240"), EMBER, 0.014), iron=plate(IRON, GOLD), bare=plate(IRON), gold=plate(GOLD),
                     hoof=fur(HOOF, 0.1, 0.1), fire=flame(EMBER), fire2=flame(EMBER, 9.0), cloth=cloth(ramp("#2a0408", "#4a0810", "#74101a", "#a01c20", "#c43224"), GOLD),
                     leather=fur(LEATHER, 0.1, 0.2), eye=eye(EMBER), horn=plate(ramp("#0e0c10", "#1e1a20", "#322c32", "#4c4448", "#6c6060")))
    hips = k.part("hips", (0, 27, -11))
    torso = k.part("torso", (0, 27, -11), (), hips)
    k.loaf(torso, "z", -19, 18, 14, lambda t: (10.5 + 3 * math.sin(t * math.pi), 12.5 + 3.2 * math.sin(t * math.pi) + 2.2 * t, 27.4 - 1.3 * t), "hide", "barrel")
    # rump and shoulder muscle
    for sx in (1, -1):
        k.add(torso, C(sx * 3.4, 22, -14, 6.4, 13, 10), "hide", tag="haunch")
        k.add(torso, C(sx * 3.2, 20, 13, 6.4, 13, 8), "hide", tag="shoulder")
    # the skirts of the barding, the plates over the rump, the breast
    for sx in (1, -1):
        k.add(torso, C(sx * 7.6, 18.6, -1, 0.9, 11, 22), "cloth", tag="skirt")
        k.add(torso, C(sx * 7.9, 26.8, -1, 0.6, 1.6, 22.6), "gold", tag="skirt")
        for z in (-7, 5):
            k.add(torso, C(sx * 8.1, 24, z, 0.4, 2.4, 2.4), "gold", tag="stud")
    for n, (y, dz, w) in enumerate(((35.0, -19, 8.6), (33.6, -14.6, 11.6), (34.6, -10.2, 10.6))):
        k.add(torso, C(0, y - 2, dz, w, 3.8, 5.0), "iron", tag="crupper")
    k.add(torso, C(0, 18.6, 21, 11.4, 15, 1.8), "iron", tag="peytral")
    k.add(torso, C(0, 23, 22, 4, 6, 0.6), "gold", tag="sigil")
    for x in (-4.4, 0, 4.4):
        k.seg(torso, "pspike%d" % (x + 9), (x, 31, 21), [(1.5, 1.5, 3.2, (("x", 66),)), (0.8, 0.8, 2.4, ())], "horn", tag="spike")
    saddle(k, torso, -2, 34.6, 11.4)
    # legs
    for sx, nm in ((1, "l"), (-1, "r")):
        x = sx * 4.4
        up, low, ft = k.leg(torso, ("thigh_" + nm, "shin_" + nm, "foot_" + nm), x, 24.4, -15, (10.4, 10.2, 3.8), ((5.2, 6.6), (3.2, 3.8), (4.2, 4.8)), (10, -18, 8), ("hide", "hide", "hoof"))
        k.add(low, C(x, 14.0, -15, 4.0, 3, 4.6), "iron", tag="hock")
        k.add(low, C(x, 4.0, -15, 5.0, 3.4, 5.4), "fire", tag="fetlock", group="glow")
        up, low, ft = k.leg(torso, ("arm_" + nm, "fore_" + nm, "hand_" + nm), x, 24.4, 13, (10.4, 10.2, 3.8), ((4.8, 6.0), (3.2, 3.6), (4.2, 4.8)), (-6, 6, 0), ("hide", "hide", "hoof"))
        k.add(up, C(x, 16.4, 13, 5.2, 8, 6.6), "iron", tag="pauldron")
        k.add(low, C(x, 13.8, 13.2, 4.0, 3.2, 4.4), "iron", tag="knee")
        k.add(low, C(x, 4.0, 13, 5.0, 3.4, 5.4), "fire2", tag="fetlock", group="glow")
    # neck, crinet, the fire: an arched neck in two joints, tongues standing off its crest
    neck = k.part("neck", (0, 31, 16), (("x", 30),), torso)
    k.loaf(neck, "y", 29, 42, 6, lambda t: (8.0 - 1.4 * t, 11.6 - 2.6 * t, 16.2), "hide", "neck")
    for n in range(4):
        k.add(neck, C(0, 30.5 + n * 3, 20.6 - n * 0.3, 7.4 - n * 0.4, 3.4, 1.4), "iron", tag="crinet")
    neck2 = k.part("neck2", (0, 42, 16.2), (("x", 16),), neck)
    k.loaf(neck2, "y", 41, 53, 5, lambda t: (6.6 - 1.2 * t, 9.0 - 2.4 * t, 16.2), "hide", "neck")
    for n in range(4):
        k.add(neck2, C(0, 41.5 + n * 3, 20.2 - n * 0.5, 6.4 - n * 0.4, 3.4, 1.4), "iron", tag="crinet")

    def tongue(par, y, z, ln, tilt, roll, wd):
        k.seg(par, "fire%d" % len(s.boxes), (0, y, z), [(wd, wd * 1.5, ln * 0.45, (("x", tilt), ("z", roll))), (wd * 0.72, wd * 1.1, ln * 0.33, (("x", 14),)), (wd * 0.42, wd * 0.6, ln * 0.3, (("x", 18),))],
              "fire" if len(s.boxes) % 2 else "fire2", tag="mane", group="glow")

    for n in range(6):
        tongue(neck, 30 + n * 2.3, 10.8, 10 + 5 * math.sin(n * 1.9) ** 2, -84 - n * 3, (n % 3 - 1) * 12, 2.4)
    for n in range(6):
        tongue(neck2, 41.6 + n * 2.1, 12.2, 11 + 6 * math.sin(n * 2.3 + 1) ** 2, -92 - n * 4, ((n + 1) % 3 - 1) * 12, 2.2)
    tongue(neck2, 52, 15, 10, -40, 0, 2.0)
    # the head hangs from the poll; local +y runs down the face to the muzzle, -z is the top of the face
    head = k.part("head", (0, 52.6, 16.2), (("x", 92),), neck2)
    k.add(head, C(0, 50.4, 16.2, 6.0, 7.4, 7.4), "hide", tag="skull")
    k.add(head, C(0, 57.4, 15.6, 4.4, 5.0, 5.4), "hide", tag="muzzle")
    k.add(head, C(0, 62.0, 15.5, 3.8, 3.6, 4.6), "hide", tag="muzzle")
    k.add(head, C(0, 50.6, 19.8, 4.4, 5.4, 1.4), "hide", tag="jaw")
    k.add(head, C(0, 64.8, 15.5, 4.4, 2.0, 5.0), "iron", tag="nose")
    k.add(head, C(0, 49.8, 12.2, 6.4, 8, 1.0), "iron", tag="chanfron")
    k.add(head, C(0, 57.6, 12.6, 4.8, 6.6, 1.0), "iron", tag="chanfron")
    k.add(head, C(0, 53.2, 11.5, 1.8, 2.6, 0.5), "gold", tag="sigil")
    for sx in (1, -1):
        k.add(head, C(sx * 3.15, 51.6, 13.8, 0.9, 2.0, 2.2), "bare", tag="brow")
        k.add(head, C(sx * 3.3, 52.0, 13.8, 0.3, 1.2, 1.6), "eye", tag="eye", group="glow")
        k.seg(head, "ear%d" % (sx > 0), (sx * 2.2, 50.6, 15), [(1.5, 1.2, 2.6, (("x", 180), ("z", sx * -12))), (0.8, 0.7, 1.6, ())], "hide", tag="ear")
        k.seg(head, "ahorn%d" % (sx > 0), (sx * 2.4, 50.6, 12.4), [(1.9, 1.9, 5.0, (("x", 150), ("z", sx * -34))), (1.5, 1.5, 5.2, (("x", 6), ("z", sx * 6))), (1.1, 1.1, 5.0, (("x", -14),)), (0.7, 0.7, 4.4, (("x", -26),)), (0.35, 0.35, 3.0, (("x", -30),))], "horn", tag="horn")
        k.add(head, C(sx * 2.0, 64.0, 13.4, 0.6, 1.2, 1.0), "eye", tag="nostril", group="glow")
    # the tail: a sheaf of long fires streaming back
    tail = k.part("tail", (0, 34, -19), (("x", -122),), hips)
    k.add(tail, C(0, 33.4, -19, 2.6, 3.4, 2.6), "bare", tag="tail_ring")
    for dx, tilt, ln, wd in ((0, 0, 30, 3.6), (1.4, 10, 22, 2.6), (-1.4, 14, 24, 2.6), (0, -14, 20, 2.4)):
        k.seg(tail, "fire%d" % len(s.boxes), (dx, 36, -19), [(wd, wd, ln * 0.32, (("x", tilt), ("z", dx * -8))), (wd * 0.8, wd * 0.8, ln * 0.28, (("x", 8),)), (wd * 0.55, wd * 0.55, ln * 0.24, (("x", 10),)), (wd * 0.3, wd * 0.3, ln * 0.2, (("x", 12),))],
              "fire" if len(s.boxes) % 2 else "fire2", tag="tail", group="glow")
    return k


# ------------------------------------------------------------------ Rimehorn

def rimehorn():
    k = Kit("rimehorn")
    s = k.s
    WHITE = ramp("#7a90aa", "#9ab2c8", "#bcd0e0", "#d8e6f0", "#ecf4fa", "#fbfdff")
    s.shaders = dict(hide=fur(WHITE, 0.32, 0.26), ruff=fur(ramp("#a4bcd0", "#c4d8e6", "#dcebf4", "#f0f8fc", "#ffffff"), 0.5, 0.2), ice=ice(FROST_FIRE), silver=plate(SILVER), hoof=plate(SILVER),
                     cloth=cloth(ramp("#081438", "#0c2054", "#143074", "#1e4498", "#2c5cc0"), SILVER), leather=fur(ramp("#101a30", "#1a2844", "#26395c", "#345078"), 0.1, 0.2), gold=plate(SILVER),
                     eye=eye(FROST_FIRE), snout=fur(ramp("#3a4a60", "#5a6e88", "#8096b0"), 0.1, 0.2))
    hips = k.part("hips", (0, 30, -10))
    torso = k.part("torso", (0, 30, -10), (("x", -3),), hips)
    k.loaf(torso, "z", -18, 17, 13, lambda t: (11 + 2.6 * math.sin(t * math.pi), 13 + 3 * t + 1.8 * math.sin(t * math.pi), 30 - 0.6 * t), "hide", "barrel")
    for sx in (1, -1):
        k.add(torso, C(sx * 2.8, 26, -12, 5.2, 10, 9), "hide", tag="haunch")
    k.add(torso, C(0, 38.2, -13, 7, 0.8, 7), "hide", tag="rump")
    for sx, nm in ((1, "l"), (-1, "r")):
        x = sx * 3.8
        up, low, ft = k.leg(torso, ("thigh_" + nm, "shin_" + nm, "foot_" + nm), x, 25, -14, (11.2, 10.6, 3.4), ((5.4, 7.2), (2.8, 3.4), (3.4, 4.2)), (14, -26, 12), ("hide", "hide", "hoof"))
        k.add(low, C(x, 12.6, -14.4, 3.6, 2.2, 3.8), "silver", tag="hock")
        k.add(low, C(x, 3.4, -14, 4.2, 2.6, 4.6), "ruff", tag="fetlock")
        up, low, ft = k.leg(torso, ("arm_" + nm, "fore_" + nm, "hand_" + nm), x, 25, 11, (11.2, 10.6, 3.4), ((5.0, 6.4), (2.8, 3.4), (3.4, 4.2)), (-5, 6, 0), ("hide", "hide", "hoof"))
        k.add(low, C(x, 9.8, 11.2, 3.6, 2.6, 3.8), "silver", tag="knee")
        k.add(low, C(x, 3.4, 11, 4.2, 2.6, 4.6), "ruff", tag="fetlock")
    # the blanket, its crystals, the saddle
    for sx in (1, -1):
        k.add(torso, C(sx * 7.0, 26, -1, 0.8, 12, 15), "cloth", tag="blanket")
        for z in (-6, -1.5, 3):
            k.seg(torso, "crys%d%d" % (sx > 0, z + 9), (sx * 7.5, 26, z), [(1.2, 1.2, 3.0, (("x", 180),)), (0.6, 0.6, 2.0, ())], "ice", tag="crystal")
    k.add(torso, C(0, 37.8, -1, 14.4, 0.8, 15.4), "cloth", tag="blanket")
    saddle(k, torso, -1, 38.4, 11, ("leather", "silver"))
    # chest ruff: layers of long fur
    neck = k.part("neck", (0, 35, 13), (("x", 38),), torso)
    k.loaf(neck, "y", 33, 52, 8, lambda t: (10.2 - 2.4 * t, 14.0 - 3.6 * t, 13.4 + 0.4 * t), "hide", "neck")
    for n, (y, w, d) in enumerate(((24, 14, 15), (29, 13, 14), (33, 11, 12), (38, 9.6, 10.5), (43, 8, 9))):
        for dx in (-w * 0.27, w * 0.27):
            k.add(neck, C(dx, y, 17.6 - n * 0.7, w * 0.54, 8.5, d * 0.55), "ruff", tag="ruff")
        k.add(neck, C(0, y - 1.4, 18.2 - n * 0.7, w * 0.5, 8.5, d * 0.55), "ruff", tag="ruff")
    for n in range(6):
        k.add(neck, C(0, 34 + n * 3.2, 7.2 + n * 0.6, 1.4, 3.6, 3.0), "ruff", tag="mane")
    head = k.part("head", (0, 51, 14), (("x", 74),), neck)
    k.add(head, C(0, 48.4, 14, 7.0, 8.4, 8.0), "hide", tag="skull")
    k.add(head, C(0, 56, 13.4, 4.6, 5.0, 5.4), "hide", tag="muzzle")
    k.add(head, C(0, 60.6, 13.3, 3.8, 3.6, 4.4), "hide", tag="muzzle")
    k.add(head, C(0, 64, 13.2, 4.0, 1.8, 4.6), "snout", tag="nose")
    k.add(head, C(0, 47.4, 9.6, 7.6, 1.0, 1.2), "silver", tag="circlet")
    k.add(head, C(0, 48.6, 9.6, 2.0, 7.6, 0.8), "silver", tag="circlet")
    k.add(head, C(0, 54.2, 9.2, 1.1, 1.5, 0.6), "ice", tag="gem", group="glow")
    # the crown: each beam goes out sideways, then up and back, every tine thrown forward and out
    for sx in (1, -1):
        k.add(head, C(sx * 3.6, 50.6, 11.4, 0.4, 1.5, 2.0), "eye", tag="eye", group="glow")
        k.seg(head, "ear%d" % (sx > 0), (sx * 3.2, 48, 13), [(2.4, 1.3, 4.6, (("z", sx * -112),)), (1.4, 0.8, 3.0, ())], "hide", tag="ear")
        part, at = head, (sx * 2.6, 48.4, 10.4)
        beam = [(3.0, 214, -60), (2.6, -6, 10), (2.2, -8, 16), (1.9, 2, 16), (1.6, 8, 12), (1.2, 10, 10), (0.8, 12, 8)]
        for n, (w, tilt, roll) in enumerate(beam):
            r = (("x", tilt), ("z", sx * roll))
            part = Part("beam%d%d" % (sx > 0, n), at, r, part)
            ln = 7.0 - n * 0.4
            k.add(part, C(at[0], at[1], at[2], w, ln + 0.4, w), "ice", tag="antler", group="glow")
            if n in (1, 2, 3, 4, 5):
                ln2 = 7.0 - abs(n - 3) * 1.2
                k.seg(part, "tine%d%d" % (sx > 0, n), (at[0], at[1] + ln * 0.5, at[2]), [(1.5, 1.5, ln2, (("x", 62), ("z", sx * -16))), (1.0, 1.0, ln2 * 0.8, (("x", -38),)), (0.5, 0.5, ln2 * 0.6, (("x", -30),))], "ice", tag="antler", group="glow")
            if n in (2, 4):
                k.seg(part, "btine%d%d" % (sx > 0, n), (at[0], at[1] + ln * 0.7, at[2]), [(1.2, 1.2, 4.4, (("x", -56), ("z", sx * -22))), (0.6, 0.6, 3.2, (("x", 28),))], "ice", tag="antler", group="glow")
            at = (at[0], at[1] + ln, at[2])
    tail = k.part("tail", (0, 37, -17), (("x", -150),), hips)
    k.add(tail, C(0, 37, -17, 3.6, 5.2, 2.6), "ruff", tag="tail")
    return k


# ------------------------------------------------------------------ Gravefang

def gravefang():
    k = Kit("gravefang")
    s = k.s
    BLACK = ramp("#07060c", "#0e0c16", "#171424", "#221c34", "#30284a", "#443862")
    s.shaders = dict(hide=fur(BLACK, 0.5, 0.3), ruff=fur(ramp("#0a0814", "#14102a", "#20183e", "#2e2458", "#403474"), 0.6, 0.25), bone=plate(BONE), iron=plate(IRON), gold=plate(BONE),
                     leather=fur(ramp("#0c0810", "#18121c", "#241c28", "#32283a"), 0.1, 0.2), soul=flame(SOUL), soul2=flame(SOUL, 7.0), eye=eye(SOUL), claw=plate(HOOF), maw=glow(SOUL, 0.35))
    hips = k.part("hips", (0, 21, -13))
    torso = k.part("torso", (0, 21, -13), (("x", -7),), hips)
    k.loaf(torso, "z", -18, 17, 13, lambda t: (9.0 + 6.2 * t, 10 + 7.6 * t, 26 - 0.6 * t), "hide", "barrel")
    # hackles: shards of fur standing from the shoulders down the spine
    for n in range(11):
        t = n / 10
        h = 3 + 6.4 * math.sin(t * math.pi * 0.9 + 0.5)
        z = -14 + 32 * t
        for dx in (-2.4, 0, 2.4):
            p = Part("hack%d%d" % (n, dx + 3), (dx, 30 + 4.6 * t, z), (("x", -32), ("z", -dx * 6)), torso)
            k.add(p, C(dx, 30 + 4.6 * t, z, 1.9, h * (0.75 if dx else 1), 2.8), "ruff", tag="hackle")
    # the bones worn outside: spine knuckles, ribs over the flanks
    for sx in (1, -1):
        for n in range(6):
            p = Part("rib%d%d" % (sx > 0, n), (sx * 5.4, 31 - n * 0.2, -9 + n * 4.4), (("z", sx * (-158 + n * 3)),), torso)
            k.add(p, C(sx * 5.4, 31 - n * 0.2, -9 + n * 4.4, 1.5, 10.8 + n * 1.0, 1.7), "bone", tag="rib")
        k.add(torso, C(sx * 8.6, 25, 14, 1.0, 7, 7), "bone", tag="shoulder_bone")
        k.seg(torso, "spur%d" % (sx > 0), (sx * 9, 31, 15), [(2.0, 2.0, 4.2, (("x", -30), ("z", sx * -30))), (1.2, 1.2, 3.4, (("x", 8),)), (0.6, 0.6, 2.4, ())], "bone", tag="spur")
    saddle(k, torso, -3, 31.2, 10.4, ("leather", "bone"))
    k.add(torso, C(0, 26.6, -3, 12.6, 5, 7), "leather", tag="girth")
    for sx, nm in ((1, "l"), (-1, "r")):
        x = sx * 4.8
        up, low, ft = k.leg(torso, ("thigh_" + nm, "shin_" + nm, "foot_" + nm), x, 20, -13, (8.4, 7.8, 3.0), ((5.4, 7.6), (3.2, 3.6), (4.6, 7.0)), (22, -38, 22), ("hide", "hide", "hide"))
        k.add(ft, C(x, 0, -9.6, 4.8, 2.0, 1.6), "claw", tag="boot")
        k.add(up, C(x, 12.8, -9, 5.8, 6.4, 1.2), "bone", tag="thigh_plate")
        x = sx * 6.0
        up, low, ft = k.leg(torso, ("arm_" + nm, "fore_" + nm, "hand_" + nm), x, 24, 12, (10, 10.4, 3.2), ((6.4, 8.0), (4.4, 4.8), (5.4, 7.4)), (3, 8, 0), ("hide", "hide", "hide"))
        k.add(ft, C(x, 0, 15.6, 5.6, 2.2, 1.8), "claw", tag="boot")
        k.add(low, C(x, 8.6, 14.8, 4.4, 5.4, 0.9), "bone", tag="bracer")
    # neck ruff, the skull on its face
    neck = k.part("neck", (0, 30, 18), (("x", 54),), torso)
    k.loaf(neck, "y", 24, 38, 6, lambda t: (13 - 3.4 * t, 15 - 4.6 * t, 18), "ruff", "neck")
    for n in range(5):
        for dx in (-3, 0, 3):
            p = Part("ruff%d%d" % (n, dx + 3), (dx, 27 + n * 2.6, 12.2), (("x", -60), ("z", dx * 7)), neck)
            k.add(p, C(dx, 27 + n * 2.6, 12.2, 2.2, 7 - n * 0.3, 3.2), "ruff", tag="hackle")
    # the head reaches forward and low: local +y runs out along the snout, -z is the top of the skull
    head = k.part("head", (0, 38, 18), (("x", 40),), neck)
    k.add(head, C(0, 36.6, 18, 9.4, 6.4, 8.4), "hide", tag="skull")
    k.add(head, C(0, 42.6, 17.6, 6.6, 3.6, 6.6), "hide", tag="snout")
    k.add(head, C(0, 45.8, 17.2, 4.8, 4.0, 4.8), "hide", tag="snout")
    k.add(head, C(0, 49.4, 17.0, 3.8, 4.4, 3.6), "hide", tag="snout")
    # the skull worn over it: brow, the long nose bone
    k.add(head, C(0, 37.4, 13.6, 10.2, 5.4, 1.2), "bone", tag="brow")
    k.add(head, C(0, 42.4, 13.9, 7.2, 3.6, 1.2), "bone", tag="brow")
    k.add(head, C(0, 45.6, 14.5, 5.4, 4.2, 1.2), "bone", tag="brow")
    k.add(head, C(0, 49.4, 15.0, 4.2, 4.8, 1.0), "bone", tag="brow")
    k.add(head, C(0, 54.0, 15.8, 3.2, 1.2, 1.8), "claw", tag="nose")
    # the jaw hangs open on the soulfire
    jaw = k.part("jaw", (0, 40, 22), (("x", -16),), head)
    k.add(jaw, C(0, 40, 21.6, 6.0, 12.6, 1.8), "bone", tag="jaw")
    k.add(head, C(0, 39, 20.4, 5.4, 11, 2.2), "maw", tag="maw", group="glow")
    for sx in (1, -1):
        k.add(head, C(sx * 3.2, 39.6, 12.8, 2.6, 2.0, 0.4), "eye", tag="eye", group="glow")
        k.seg(head, "ear%d" % (sx > 0), (sx * 3.4, 36.6, 15), [(3.4, 1.8, 5.6, (("x", 196), ("z", sx * -12))), (2.0, 1.2, 4.4, (("x", 2),)), (0.8, 0.6, 2.8, ())], "hide", tag="ear")
        k.seg(head, "khorn%d" % (sx > 0), (sx * 4.8, 37, 13.6), [(2.0, 2.0, 5.0, (("x", 186), ("z", sx * -48))), (1.3, 1.3, 4.6, (("x", 26), ("z", sx * 10))), (0.6, 0.6, 3.4, (("x", 28),))], "bone", tag="horn")
        for n in range(4):
            k.add(head, C(sx * (2.1 - n * 0.2), 44 + n * 2.6, 19.4 - n * 0.2, 0.9, 0.9, 2.8 - n * 0.3), "bone", tag="fang")
            k.add(jaw, C(sx * (2.1 - n * 0.2), 44 + n * 2.4, 20.4, 0.8, 0.8, 1.8), "bone", tag="fang")
    # the soulfire tail
    tail = k.part("tail", (0, 27, -18), (("x", -128),), torso)
    k.add(tail, C(0, 27, -18, 3.2, 5, 3.2), "ruff", tag="tail")
    for n in range(5):
        w = 5.4 - n * 0.7
        p = Part("tailsoul%d" % n, (0, 31 + n * 4, -18), (("x", -7 - n * 5),), tail)
        k.add(p, C(0, 31 + n * 4, -18, w, 5.0 + n, w), "soul" if n % 2 else "soul2", tag="tail", group="glow")
    return k


# ------------------------------------------------------------------ Thornback

def thornback():
    k = Kit("thornback")
    s = k.s
    RUST = ramp("#1e0e08", "#34180c", "#4e2612", "#6a3618", "#8a4a22", "#a8622e")
    MOSS = ramp("#16300e", "#265216", "#3a7620", "#58a02c", "#82c440", "#b4e060")
    moss = fur(MOSS, 0.5, 0.5)
    bristle = fur(RUST, 0.6, 0.3)

    def hide(p, n, b, key, i, j, w, h, fr):
        # moss grows down from the back, ragged
        if n[1] > 0.5 or (key in "nsew" and j / max(1, h - 1) < 0.35 + 0.5 * (fbm(p[0] * 0.3, p[1] * 0.3, p[2] * 0.3) - 0.5)):
            return moss(p, n, b, key, i, j, w, h, fr)
        return bristle(p, n, b, key, i, j, w, h, fr)

    s.shaders = dict(hide=hide, moss=moss, bark=cracked(ramp("#120a08", "#20120c", "#301c12", "#442a1a", "#5a3a24"), SAP, 0.012), tusk=plate(ramp("#7a6a4c", "#a89670", "#d2c49a", "#ece2c0", "#fffaea")),
                     gold=plate(GOLD), hoof=plate(HOOF), leather=fur(ramp("#1c120a", "#2e1e10", "#42301a", "#5a4426"), 0.3, 0.3), eye=eye(SAP), sap=glow(SAP, 0.75),
                     petal=glow(ramp("#b0186a", "#e02c8c", "#ff5cb0", "#ffa0d4"), 0.5), petal2=glow(ramp("#d07010", "#f0a020", "#ffd040", "#fff090"), 0.5), cap=glow(ramp("#6a0e12", "#a81c1c", "#e03c28", "#ff7a4a"), 0.5), stem=fur(ramp("#a89a7a", "#c8bc9c", "#e8e0c8"), 0, 0.1),
                     snout=fur(ramp("#3a1c18", "#5a2c24", "#7a4034", "#9c5a48"), 0.2, 0.2))
    hips = k.part("hips", (0, 18, -11))
    torso = k.part("torso", (0, 18, -11), (("x", -5),), hips)
    k.loaf(torso, "z", -19, 19, 13, lambda t: (15 + 5.5 * math.sin(t * math.pi * 0.9), 15 + 7.6 * math.sin(t * math.pi * 0.72), 20 + 1.2 * math.sin(t * math.pi)), "hide", "barrel")
    k.loaf(torso, "z", 2, 19, 6, lambda t: (13 - 2 * t, 8, 31.4 - 1.6 * t), "hide", "hump")
    # bark plates, a mantle at the shoulders
    for sx in (1, -1):
        for n, z in enumerate((-9, -2, 6, 13)):
            p = Part("bark%d%d" % (sx > 0, n), (sx * 10, 25, z), (("z", sx * -10),), torso)
            k.add(p, C(sx * 10.8, 15 - n * 0.3, z, 1.6, 11 + n, 6.6), "bark", tag="bark")
        k.seg(torso, "thorn%d" % (sx > 0), (sx * 8, 34, 11), [(2.6, 2.6, 5, (("x", -24), ("z", sx * -30))), (1.7, 1.7, 4.2, (("x", 12),)), (0.8, 0.8, 3.2, ())], "bark", tag="thorn")
    for n in range(8):
        z = -14 + n * 4.2
        h = 4 + 3 * math.sin(n * 2.4) ** 2
        dx = 3.6 * math.sin(n * 2.1)
        k.seg(torso, "spine%d" % n, (dx, 29 + n * 0.9, z), [(1.8, 1.8, h, (("x", -22), ("z", dx * -3))), (0.8, 0.8, h * 0.7, (("x", 6),))], "bark", tag="thorn")
    # moss cushions, flowers, toadstools
    for dx, z, w, d in ((-5, -9, 8, 9), (5, -7, 7, 10), (0, -13, 8, 6), (5.6, 10, 6, 6), (-5.6, 12, 6, 7)):
        k.add(torso, C(dx, 28 + (z + 13) * 0.2, z, w, 3 + (w % 3), d), "moss", tag="cushion")
    for n, (x, z, m) in enumerate(((-7, -10, "petal"), (-3, -14, "petal2"), (7, -5, "petal"), (3.5, -11, "petal2"), (8, 8, "petal2"), (-8, 9, "petal"), (-2, 15, "petal2"), (7.4, 14, "petal"))):
        y = 32.4 + (z + 13) * 0.16
        k.add(torso, C(x, y, z, 0.7, 2.2, 0.7), "stem", tag="flower")
        k.add(torso, C(x, y + 2, z, 2.6, 0.9, 2.6), m, tag="flower", group="glow")
    for x, z, h, w in ((-8, -4, 3.4, 4.4), (-5.2, -3, 2.4, 3.2), (8.4, -11, 3, 3.6)):
        y = 31 + (z + 13) * 0.16
        k.add(torso, C(x, y, z, 1.3, h, 1.3), "stem", tag="shroom")
        k.add(torso, C(x, y + h, z, w, 1.3, w), "cap", tag="shroom", group="glow")
        k.add(torso, C(x, y + h + 1.1, z, w * 0.6, 0.8, w * 0.6), "cap", tag="shroom", group="glow")
    # a saddle of woven root
    saddle(k, torso, 0, 34.0, 11.6, ("bark", "gold"))
    for sx in (1, -1):
        k.add(torso, C(sx * 6.8, 21, 0, 1.2, 14, 2), "leather", tag="girth")
    for sx, nm in ((1, "l"), (-1, "r")):
        x = sx * 6.6
        up, low, ft = k.leg(torso, ("thigh_" + nm, "shin_" + nm, "foot_" + nm), x, 15, -13, (6.6, 5.4, 3), ((7.6, 9.6), (5.0, 5.6), (6.0, 6.8)), (10, -14, 4), ("hide", "hide", "hoof"))
        x = sx * 7.6
        up, low, ft = k.leg(torso, ("arm_" + nm, "fore_" + nm, "hand_" + nm), x, 15, 12, (6.6, 5.4, 3), ((8.4, 10), (5.4, 6.0), (6.4, 7.2)), (-3, 3, 0), ("hide", "hide", "hoof"))
        k.add(low, C(x, 4.4, 12, 6.4, 3.4, 7), "bark", tag="bracer")
    # the head: low, wide, a wall of bone-hard brow; +y runs forward along the snout
    neck = k.part("neck", (0, 24, 19), (("x", 84),), torso)
    k.loaf(neck, "y", 20, 29, 4, lambda t: (17 - 3 * t, 15 - 2 * t, 24), "hide", "neck")
    head = k.part("head", (0, 29, 24), (("x", 30),), neck)
    k.add(head, C(0, 27.6, 24, 16.6, 9, 14.4), "hide", tag="skull")
    k.add(head, C(0, 28.6, 16.6, 17.4, 7.6, 1.8), "bark", tag="brow")
    k.add(head, C(0, 36, 17.6, 9, 5, 1.4), "bark", tag="brow")
    k.add(head, C(0, 36, 23.4, 11.6, 4.0, 10.4), "hide", tag="muzzle")
    k.add(head, C(0, 39.8, 23.0, 9.8, 4.0, 8.8), "hide", tag="muzzle")
    k.add(head, C(0, 43.6, 22.8, 9.0, 2.8, 7.6), "snout", tag="nose")
    for sx in (1, -1):
        k.add(head, C(sx * 2.2, 46.3, 21.8, 2.4, 0.3, 1.8), "hoof", tag="nostril")
        k.add(head, C(sx * 8.45, 32.6, 19.2, 0.3, 2.0, 2.0), "eye", tag="eye", group="glow")
        k.seg(head, "ear%d" % (sx > 0), (sx * 7.6, 28, 19), [(3.8, 2.0, 4.6, (("z", sx * -74), ("x", -24))), (2.2, 1.2, 2.8, (("x", 14),)), (1.2, 0.8, 1.8, ())], "hide", tag="ear")
        # the tusks: out of the jaw, round, up, a gold ring on each
        tusk, at = k.seg(head, "tusk%d" % (sx > 0), (sx * 4.6, 38, 26.4), [(3.4, 3.4, 5.4, (("x", -64), ("z", sx * -46))), (3.0, 3.0, 5.4, (("x", -22),)), (2.5, 2.5, 5.2, (("x", -22),)), (2.0, 2.0, 4.8, (("x", -20),)), (1.4, 1.4, 4.2, (("x", -18),)), (0.7, 0.7, 3.2, (("x", -14),))], "tusk", tag="tusk")
        k.add(head, C(sx * 4.6, 37.4, 26.4, 4.4, 1.6, 4.4), "gold", tag="tusk_ring")
    for n in range(5):
        k.seg(head, "bristle%d" % n, (-3.2 + n * 1.6, 28 + (n % 2), 15.6), [(1.2, 1.8, 3.6 + (n % 2) * 1.6, (("x", 196), ("z", (2 - n) * 8))), (0.6, 0.8, 2.2, ())], "bark", tag="thorn")
    for sx in (1, -1):
        k.add(head, C(sx * 7.0, 33, 25, 3.4, 5, 8.6), "hide", tag="jowl")
    tail = k.part("tail", (0, 25, -19), (("x", -140),), hips)
    k.add(tail, C(0, 25, -19, 1.4, 6, 1.4), "hide", tag="tail")
    k.add(tail, C(0, 31, -19, 3.2, 3.6, 3.2), "moss", tag="tail")
    return k


# ------------------------------------------------------------------ Stormdrake

def membrane(R, vein):
    def paint(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        c = abs(fbm(x * 0.13, y * 0.13 + 3, z * 0.13) - 0.5)
        if c < 0.02:
            return shade(vein, 0.8, i, j)
        return shade(R, 0.38 + 0.4 * (fbm(x * 0.2, y * 0.2, z * 0.2) - 0.3) + 0.2 * j / max(1, h), i, j)
    return paint


def stormdrake():
    k = Kit("stormdrake")
    s = k.s
    SCALE = ramp("#0a0c2c", "#121648", "#1c2268", "#2a3290", "#3c48b8", "#5a6ce0")
    scale_fur = fur(SCALE, 0.1, 0.3)

    def scales(p, n, b, key, i, j, w, h, fr):
        # rows of scales: a dark rim on every second tile
        if key in "nsewu" and (j + (i // 4 % 2) * 2) % 4 == 0:
            return shade(SCALE, 0.12, i, j)
        return scale_fur(p, n, b, key, i, j, w, h, fr)

    def belly(p, n, b, key, i, j, w, h, fr):
        return shade(GOLD, 0.55 + 0.2 * ((j // 3) % 2) - 0.1 * (j / max(1, h)), i, j)

    s.shaders = dict(hide=scales, belly=belly, wing=membrane(ramp("#120a3a", "#1e1464", "#2e2096", "#4230c0"), BOLT), bone=plate(ramp("#0e1030", "#1a1e50", "#2a3078", "#3e48a4")), bolt=glow(BOLT, 0.72),
                     gold=plate(GOLD), leather=fur(ramp("#1a0c10", "#2e1a1c", "#442a28"), 0.1, 0.2), eye=eye(BOLT), claw=plate(ramp("#403a30", "#6c6450", "#a89c80", "#d8d0b8")), horn=plate(ramp("#1a1c30", "#3a3c54", "#6a6c88", "#a4a6c0", "#dcdcec")))
    hips = k.part("hips", (0, 25, -10))
    torso = k.part("torso", (0, 25, -10), (("x", -10),), hips)
    k.loaf(torso, "z", -16, 15, 12, lambda t: (10 + 3.4 * math.sin(t * math.pi), 11 + 2.6 * math.sin(t * math.pi), 24.4), "hide", "barrel")
    k.add(torso, C(0, 17.4, 1, 8.6, 1.4, 25), "belly", tag="belly")
    k.add(torso, C(0, 17, 9, 7.4, 3, 11), "belly", tag="belly")
    saddle(k, torso, 4, 31, 11, ("leather", "gold"))
    for sx in (1, -1):
        k.add(torso, C(sx * 6.4, 22, 4, 0.9, 9, 2.6), "leather", tag="girth")
    # crest of lightning down the back
    for n in range(7):
        if -3 < -11 + n * 4 < 11:
            continue
        k.seg(torso, "crest%d" % n, (0, 30.4, -13 + n * 4), [(1.0, 3.4, 3.4, (("x", -14),)), (0.6, 1.8, 2.2, ())], "bolt", tag="crest", group="glow")
    for sx, nm in ((1, "l"), (-1, "r")):
        x = sx * 5.8
        up, low, ft = k.leg(hips, ("thigh_" + nm, "shin_" + nm, "foot_" + nm), x, 24, -8, (11, 10.4, 3.2), ((6.6, 9.4), (3.8, 4.4), (5.4, 8.6)), (26, -44, 18), ("hide", "hide", "hide"))
        k.add(ft, C(x, 0, -3.6, 5.0, 2.0, 1.8), "claw", tag="boot")
        for dx in (-1.6, 0, 1.6):
            k.seg(ft, "talon%d%d" % (sx > 0, dx + 2), (x + dx, 1.0, -3.2), [(1.1, 1.1, 2.4, (("x", 100),)), (0.6, 0.6, 1.6, (("x", 30),))], "claw", tag="boot")
    # wings: drawn flat in a plane, y along the span, z along the chord, then the plane is thrown out and up from the shoulder.
    # A bat's wing: arm to the wrist, three fingers, the sail scalloped between them.
    for sx, nm in ((1, "l"), (-1, "r")):
        x = sx * 6.4
        root = k.part("arm_" + nm, (x, 29, 8), (("z", sx * -58), ("x", -10)), torso)
        y0 = 29
        hand = k.part("hand_" + nm, (x, y0 + 30, 18), (), root)

        def lerp(pts, y):
            for (a, za), (b, zb) in zip(pts, pts[1:]):
                if a <= y <= b:
                    return za + (zb - za) * (y - a) / (b - a)
            return pts[-1][1]

        front = [(0, 8), (30, 18), (72, -10)]
        tips = [(0, -16), (34, -36), (56, -30), (72, -10)]
        for n in range(36):
            sp = n * 2.0
            zf = lerp(front, sp + 1)
            zb = lerp(tips, sp + 1)
            for (a, za), (b, zb2) in zip(tips, tips[1:]):
                if a <= sp + 1 <= b:
                    zb += 6.5 * math.sin((sp + 1 - a) / (b - a) * math.pi)      # the scallop, pulled in between the fingers
            k.add(hand if sp >= 30 else root, ((x - 0.2, y0 + sp, zb), (0.4, 2.1, max(1.0, zf - zb))), "wing", tag="sail", skip=("u", "d", "n", "s"))

        def spar(on, a, b, wd, mat, group="lit"):
            steps = int(math.dist(a, b) / 2.0) + 1
            for q in range(steps):
                t = q / steps
                k.add(on, C(x, y0 + a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, wd * (1 - 0.5 * t) + 0.3, 2.6, wd * (1 - 0.5 * t) + 0.3), mat, tag="finger", group=group)

        spar(root, (0, 8), (30, 18), 3.8, "hide")
        for t in tips[1:]:
            spar(hand, (30, 18), t, 1.5, "bone")
        k.add(hand, C(x, y0 + 29, 18, 4.4, 4, 5), "bone", tag="wrist")
        k.seg(hand, "wclaw%d" % (sx > 0), (x, y0 + 32, 19), [(2.0, 2.0, 3.4, (("x", 40),)), (1.0, 1.0, 3.0, (("x", 30),))], "claw", tag="claw")
        # lightning running out along the fingers
        for t in tips[1:]:
            for q in range(3):
                u = (0.25 + q * 0.27)
                k.add(hand, C(x + sx * 0.3, y0 + 30 + (t[0] - 30) * u, 18 + (t[1] - 18) * u + (-1) ** q, 0.9, 3.2, 1.2), "bolt", tag="vein", group="glow")
    neck = k.part("neck", (0, 28, 14), (("x", 36),), torso)
    part, at = neck, (0, 28, 14)
    for n, (w, bend) in enumerate(((8.2, 16), (7.2, 4), (6.2, -14), (5.6, -22), (5.2, -24))):
        part = k.part("neck%d" % n, at, (("x", bend),), part)
        k.add(part, C(at[0], at[1], at[2], w, 6.2, w + 1), "hide", tag="neck")
        k.add(part, C(at[0], at[1], at[2] + (w + 1) / 2, w * 0.7, 6, 0.8), "belly", tag="belly")
        k.seg(part, "ncrest%d" % n, (0, at[1] + 2, at[2] - w / 2 - 0.3), [(0.9, 3.0, 3.0 - n * 0.2, (("x", -94),)), (0.5, 1.6, 2.0, ())], "bolt", tag="crest", group="glow")
        at = (at[0], at[1] + 5.6, at[2])
    head = k.part("head", at, (("x", 110),), part)
    y = at[1]
    z = at[2]
    k.add(head, C(0, y - 2.4, z, 8.4, 7.4, 7.4), "hide", tag="skull")
    k.add(head, C(0, y + 4.4, z - 0.6, 6.0, 9.4, 4.0), "hide", tag="muzzle")
    k.add(head, C(0, y + 4.4, z + 2.8, 5.2, 8.6, 1.8), "belly", tag="jaw")
    k.add(head, C(0, y + 3.8, z + 1.8, 4.0, 8.8, 1.0), "bolt", tag="maw", group="glow")
    for sx in (1, -1):
        k.add(head, C(sx * 3.9, y - 0.6, z - 1.8, 0.3, 2.2, 1.6), "eye", tag="eye", group="glow")
        k.add(head, C(sx * 3.4, y - 2.0, z - 3.2, 1.6, 4.4, 1.0), "bone", tag="brow")
        k.seg(head, "dhorn%d" % (sx > 0), (sx * 3, y - 2.4, z - 2.4), [(2.4, 2.4, 6.4, (("x", 168), ("z", sx * -20))), (1.7, 1.7, 6, (("x", -14),)), (1.1, 1.1, 5.4, (("x", -18),)), (0.5, 0.5, 4, (("x", -20),))], "horn", tag="horn")
        k.seg(head, "dhornb%d" % (sx > 0), (sx * 3.8, y - 1.2, z), [(1.4, 1.4, 4.4, (("x", 176), ("z", sx * -44))), (0.7, 0.7, 3.4, (("x", -14),))], "horn", tag="horn")
    for sx in (1, -1):
        for n in range(4):
            k.add(head, C(sx * 1.9, y + 2.4 + n * 1.9, z + 1.2, 0.6, 0.7, 1.4), "claw", tag="fang")
    # the tail, a whip, a blade of lightning
    part, at = k.part("tail", (0, 24, -16), (("x", -106),), torso), (0, 24, -16)
    k.add(part, C(0, 24, -16, 7.6, 4, 7.6), "hide", tag="tail")
    for n in range(7):
        w = 6.6 - n * 0.85
        part = k.part("tails%d" % n, at, (("x", -7 if n < 3 else 10),), part)
        k.add(part, C(0, at[1], at[2], w, 6.8, w), "hide", tag="tail")
        at = (0, at[1] + 6.4, at[2])
    k.add(part, ((-0.4, at[1], at[2] - 3.4), (0.8, 7, 6.8)), "bolt", tag="fin", group="glow")
    k.add(part, ((-0.4, at[1] + 7, at[2] - 1.6), (0.8, 4, 3.2)), "bolt", tag="fin", group="glow")
    return k


MOUNTS = dict(ashmane=ashmane, rimehorn=rimehorn, gravefang=gravefang, thornback=thornback, stormdrake=stormdrake)


if __name__ == '__main__':
    V.T = 2
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    for n in names or MOUNTS:
        kit = MOUNTS[n]()
        if "--export" in sys.argv:
            kit.export(n)
        else:
            M.preview(kit.s, "mount_" + n)
