"""Armour sets designed one by one, each its own silhouette: nothing here is a class template in new colours. A set's
design builds all its pieces itself (armorforge.build calls it instead of the template) and has one slot the template
never had, `back`: rigid on the chest, free of the arm-swing squeeze in efarmor.fit, for boilers, bellows and hammers.

Player units: feet at 0, facing +z, right hand -x. Head y 24-32, |x|, |z| under 4. Body y 12-24, |x| under 4, |z| under 2.
Arms round x 6, legs round x 2. Keep chest_body within |x| 4.35 or efarmor squeezes it all into the skin.
Anything on an arm is at least 5 wide and deep: the lining under it copies Epic Fight's own, and must not show through.
The elbow is at y 18: hard arm pieces stop at 17.3 and start again at 18.6, with k.elbow's thin soft sleeve across the gap.
Shoulder pieces stay above y 20.4: they stay put while the arm swings under them.
The body is left out under a designed set (AshboundClient), so the lining under these pieces is the arm and the leg.
The sets past the Foundry are in armorsets_*.py, a few gates to a file, registered with `design`.
"""
import math

from voxboss import C
from voxsword import fbm, ramp


# ---------------------------------------------------------------- paint: clean ramps with no dither, strong light and dark

def tone(R, v):
    return R[max(0, min(len(R) - 1, int(v * (len(R) - 1) + 0.5)))]


def mix(a, b, t):
    return tuple(round(a[k] + (b[k] - a[k]) * t) for k in range(3)) + tuple(a[3:])


HOT = ramp("#5a1206", "#a82408", "#ec5410", "#ffa030")


def plate(R, spots=(), heat=HOT):
    """polished plate: lit from above, a bright bevel on the top and left edges, a dark one below, and red-hot near any fire"""
    def sh(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        v = 0.46 + 0.16 * n[1] + 0.08 * (fbm(x * 0.4, y * 0.4, z * 0.4) - 0.5)
        v += 0.1 * (0.5 - j / max(1, h - 1))
        if key == "d":
            v -= 0.2
        if i == 0 or j == 0:
            v += 0.26
        if i == w - 1 or j == h - 1:
            v -= 0.2
        c = tone(R, v)
        t = 0.0
        for (sx, sy, sz), r in spots:
            d = math.sqrt((x - sx) ** 2 + (y - sy) ** 2 + (z - sz) ** 2)
            t = max(t, 1 - d / r)
        if t > 0:
            t = round(min(1.0, t * 1.5) * 3) / 3
            if t > 0:
                c = mix(c, tone(heat, 0.25 + 0.75 * t), 0.35 + 0.55 * t)
        return c
    return sh


def links(R):
    """mail in rows of rings, stitched in soft bands instead of a checker"""
    def sh(p, n, b, key, i, j, w, h, fr):
        v = 0.34 + 0.1 * n[1] + (0.16 if j % 2 == 0 else 0.0) + (0.1 if (i + j // 2) % 3 == 0 and j % 2 == 0 else 0.0)
        if j == 0:
            v += 0.12
        return tone(R, v)
    return sh


def cloth(R):
    """cloth that hangs: vertical folds, a lit edge at the top, a dark hem"""
    def sh(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        v = 0.5 + 0.12 * n[1] + 0.13 * math.sin((x + z) * 1.6) + 0.1 * (fbm(x * 0.5, y * 0.3, z * 0.5) - 0.5)
        if j == 0:
            v += 0.16
        if j == h - 1:
            v -= 0.2
        return tone(R, v)
    return sh


def hide(R):
    """leather: worn pale along the edges, scuffed"""
    def sh(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        v = 0.48 + 0.14 * n[1] + 0.2 * (fbm(x * 0.7, y * 0.7, z * 0.7) - 0.5)
        if i == 0 or j == 0:
            v += 0.2
        if i == w - 1 or j == h - 1:
            v -= 0.16
        return tone(R, v)
    return sh


def flame(R):
    """fire at full brightness, hottest in the middle of each face"""
    def sh(p, n, b, key, i, j, w, h, fr):
        u, t = abs(i - (w - 1) / 2) / max(1, w / 2), abs(j - (h - 1) / 2) / max(1, h / 2)
        return tone(R, 0.98 - 0.42 * max(u, t) + 0.18 * (fbm(p[0], p[1], p[2]) - 0.5))
    return sh


def scales(R):
    """overlapping rows of scales, each row offset from the last"""
    def sh(p, n, b, key, i, j, w, h, fr):
        r, t = j // 3, j % 3
        du = abs((i + (r % 2) * 2) % 4 - 1.5) / 1.5
        return tone(R, 0.38 + 0.14 * n[1] + 0.3 * (1 - du) * (1 - t / 3) - (0.2 if t == 2 and du > 0.6 else 0.0))
    return sh


def fur(R):
    """pelt: long streaks running down, tips catching the light"""
    def sh(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        return tone(R, 0.46 + 0.14 * n[1] + 0.5 * (fbm(x * 2.4, y * 0.45, z * 2.4) - 0.5) + (0.12 if (i * 7 + j // 4 * 3) % 5 == 0 else 0.0))
    return sh


def bone(R):
    """old bone: pale, chalky, a hairline crack here and there"""
    def sh(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        v = 0.6 + 0.16 * n[1] + 0.14 * (fbm(x * 0.5, y * 0.5, z * 0.5) - 0.5)
        if i == 0 or j == 0:
            v += 0.14
        if i == w - 1 or j == h - 1:
            v -= 0.18
        return tone(R, v)
    return sh


def grain(R):
    """wood: long grain, a dark line every few rows"""
    def sh(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        v = 0.46 + 0.12 * n[1] + 0.13 * math.sin((x + z) * 3 + 6 * fbm(x * 0.3, y * 0.1, z * 0.3))
        if i % 5 == 0:
            v -= 0.14
        if j == 0:
            v += 0.14
        return tone(R, v)
    return sh


def stone(R):
    """rock: chipped planes rather than noise"""
    def sh(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        v = 0.44 + 0.18 * n[1] + 0.3 * (round(fbm(x * 0.6, y * 0.6, z * 0.6) * 6) / 6 - 0.5)
        if i == 0 or j == 0:
            v += 0.14
        return tone(R, v)
    return sh


def feather(R):
    """overlapping feathers: chevrons pointing down, a pale quill up the middle"""
    def sh(p, n, b, key, i, j, w, h, fr):
        u = abs(i - (w - 1) / 2)
        t = (j + int(u * 0.8)) % 5
        return tone(R, 0.4 + 0.12 * n[1] + (0.26 if t == 0 else 0.0) - (0.14 if t == 4 else 0.0) + (0.2 if u < 0.6 else 0.0))
    return sh


def gem(R):
    """a cut stone: flat facets, a hard highlight across the corner"""
    def sh(p, n, b, key, i, j, w, h, fr):
        v = 0.56 + 0.1 * n[1] + 0.34 * (((i + j) * 4 // max(1, w + h)) / 3 - 0.5)
        if i == 0 or j == 0:
            v += 0.3
        return tone(R, v)
    return sh


def wax(R):
    """tallow: smooth, with runs of drips growing toward the bottom of each face"""
    def sh(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        return tone(R, 0.62 + 0.12 * n[1] + 0.26 * math.sin(x * 2.1 + z * 1.7) * j / max(1, h - 1))
    return sh


IRON = ramp("#14111a", "#221c28", "#352c3c", "#4c4254", "#6a5e72", "#8e8296", "#b8acbc", "#e6dee8")
BRASS = ramp("#3a1a08", "#6e3a10", "#a8641a", "#d89628", "#f6c648", "#ffe688", "#fff6cc")
FRAMES = 6
FIRE = ramp("#c82a08", "#f05a10", "#ff8c1c", "#ffbc3c", "#ffe27a", "#fff6c8")

# what a set is painted in, material by material; `plate` and `dark` take the heat of the set's fires
PAINT = {
    "kilnplate": dict(blade=IRON, dark=ramp("#0e0b12", "#1a1420", "#2a2230", "#3c3244", "#544a5c", "#74687c"), acc=BRASS,
                      leather=ramp("#2a120a", "#42200f", "#5e3018", "#7c4622", "#9e6030", "#c4844a")),
    "riveter": dict(blade=ramp("#1c2226", "#2e383e", "#445058", "#5e6c74", "#7e8e96", "#a4b4ba", "#d6e2e4"), dark=IRON,
                    leather=ramp("#34100a", "#561c10", "#7c2e16", "#a4441e", "#cc6230", "#ec8c50"), acc=BRASS,
                    wood=ramp("#2a1408", "#46240e", "#663818", "#885024", "#ac6e34")),
    "slagrunner": dict(blade=ramp("#2a1408", "#4e2a12", "#7a4a20", "#a8702e", "#d49c44", "#f6cc70"), dark=ramp("#120e0c", "#221a16", "#342824", "#4a3a32"),
                       cloth=ramp("#2c2420", "#443830", "#5e5044", "#7c6c5c", "#9c8c78"), wrap=ramp("#04303a", "#084a54", "#0e6c74", "#169696", "#2cc4b8", "#7ceccc"),
                       leather=ramp("#2a160c", "#442612", "#62381c", "#845028", "#a86e3a")),
    "bellows": dict(blade=IRON, dark=ramp("#0e0b12", "#1a1420", "#2a2230", "#3c3244", "#544a5c"), acc=BRASS,
                    cloth=ramp("#2e070c", "#500d12", "#7a1616", "#a4241c", "#cc3a24", "#ee6236"), wrap=ramp("#3a1a08", "#6e3a10", "#a8641a", "#d89628", "#f6c648"),
                    leather=ramp("#1c120e", "#2e1e16", "#463022", "#604430"), wood=ramp("#2a1408", "#46240e", "#663818", "#885024", "#ac6e34")),
}


def lining(name):
    """what shows in the gaps: a dark tone of the set's own, never a bright one"""
    return tuple(PAINT[name].get("dark", IRON)[1][:3])


def fire(name):
    """the ramp a set's glowing parts roll through: its gate's element, not always flame"""
    return PAINT[name].get("fire", FIRE)


def robe(name):
    """the skirt efarmor hangs under a robe and its hem, or None for a robe that has none"""
    p = PAINT[name]
    if p.get("no_skirt"):
        return None
    return tuple(tone(p.get("cloth", p.get("blade", IRON)), 0.42)[:3]), tuple(tone(p.get("acc", BRASS), 0.6)[:3])


TEXTURES = {"cloth": cloth, "cloth2": cloth, "wrap": cloth, "leather": hide, "hide2": hide, "fur": fur, "scale": scales, "bone": bone,
            "wood": grain, "stone": stone, "feather": feather, "gem": gem, "wax": wax, "mail": links}
NOT_MATERIAL = ("fire", "hot", "no_skirt")


def shaders(s):
    """a designed set's shaders: anything in a fire's reach heats up"""
    p = PAINT[s.name]
    spots = [(b.world((0.5, 0.5, 0.5)), 1.6 + 0.25 * max(b.size)) for b in s.boxes if b.group == "fire"]
    heat = p.get("hot", HOT)
    out = {"gold": plate(BRASS), "glow": flame(fire(s.name)), "mail": links(p.get("blade", IRON))}
    for m, R in p.items():
        if m not in NOT_MATERIAL:
            out[m] = TEXTURES[m](R) if m in TEXTURES else plate(R, spots if m in ("blade", "dark") else (), heat)
    return out


class Kit:
    def __init__(self, parts, add):
        self.p, self.add = parts, add
        self.h, self.c, self.back = parts["helm_head"], parts["chest_body"], parts["chest_back"]

    def shoulder(self, side):
        """pauldrons go here: on Epic Fight's shoulder joint, so they don't swing into the chest with the arm"""
        return self.p["chest_shoulder_r" if side < 0 else "chest_shoulder_l"]

    def arm(self, side):
        return self.p["chest_arm_r" if side < 0 else "chest_arm_l"]

    def leg(self, side):
        return self.p["legs_leg_r" if side < 0 else "legs_leg_l"]

    def boot(self, side):
        return self.p["boots_leg_r" if side < 0 else "boots_leg_l"]

    def elbow(self, side, mat):
        """thin enough to fold with the arm, and efarmor gives it a ring at y 18 that turns half way with the joint"""
        self.add(self.arm(side), C(side * 6.0, 16.6, 0, 5.0, 2.6, 5.0), mat, tag="elbow")

    def fire(self, part, box, mat="glow", **kw):
        self.add(part, box, mat, group="fire", **kw)

    def tongue(self, part, x, y, z, height=3.0, width=2.2):
        """a flame: blocks narrowing upward, each leaning its own way"""
        for i, (t, dx) in enumerate(((1.0, 0.0), (0.72, 0.3), (0.46, -0.25))):
            self.fire(part, C(x + dx * width, y + i * height / 3, z, width * t, height / 3 + 0.1, width * t))

    def horn(self, part, x, y, z, segs, mat, **kw):
        """a run of boxes, each on the end of the last: (length, lean toward -x in degrees, width)"""
        for ln, ang, w in segs:
            self.add(part, C(x, y, z, w, ln, w), mat, tag="horn", rots=(("z", ang),), pivot=(x, y, z), **kw)
            r = math.radians(ang)
            x, y = x - math.sin(r) * ln, y + math.cos(r) * ln

    def rivets(self, part, spots, z, size=0.8, mat="gold"):
        for x, y in spots:
            self.add(part, C(x, y, z, size, size, 0.4), mat, tag="rivet")

    def spike(self, part, x, y, z, length, width, mat, rx=0, rz=0, steps=3, tag="spike"):
        """a tapering point from (x, y, z), tipped rx degrees backward and rz toward -x"""
        for i in range(steps):
            w = width * (1 - 0.72 * i / max(1, steps - 1))
            self.add(part, C(x, y + i * length / steps, z, w, length / steps + 0.1, w), mat, tag=tag, rots=(("x", rx), ("z", rz)), pivot=(x, y, z))

    def cape(self, mat, width=7.6, top=23.0, length=16.0, lean=8, z=-3.0, tag="cape", hem=None):
        """cloth down the back, leaning out clear of the legs"""
        rots = (("x", lean),)
        self.add(self.back, C(0, top - length, z, width, length, 0.7), mat, tag=tag, rots=rots, pivot=(0, top, z))
        if hem:
            self.add(self.back, C(0, top - length - 0.2, z, width + 0.2, 1.0, 0.8), hem, tag=tag + "_hem", rots=rots, pivot=(0, top, z))

    def tail(self, part, x, y, z, length, width, mat, lean=0, tag="tail"):
        """a strip hanging from (x, y, z): a tabard end, a chain, a strand of weed"""
        self.add(part, C(x, y - length, z, width, length, 0.5), mat, tag=tag, rots=(("x", lean),), pivot=(x, y, z))

    def arms(self, up, low, joint=None, cuff=None, w=5.2, low_h=5.0):
        """the plain run of a sleeve either side of the elbow, for a set whose idea lies elsewhere"""
        for s in SIDES:
            p, x = self.arm(s), s * 6.0
            self.add(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), up, tag="sleeve")
            self.elbow(s, joint or up)
            self.add(p, C(x, 11.4, 0, w, low_h + 0.4, w), low, tag="vambrace")
            if cuff:
                self.add(p, C(x, 11.4 + low_h - 0.2, 0, w + 0.3, 1.0, w + 0.3), cuff, tag="cuff")

    def legs(self, mat, w=4.7, y=2.4):
        for s in SIDES:
            self.add(self.leg(s), C(s * 1.95, y, 0, w, 12.0 - y, w), mat, tag="leg")

    def boots(self, mat, sole="void", h=3.8, w=5.0, cuff=None, toe=None, toe_d=3.0):
        for s in SIDES:
            p, x = self.boot(s), s * 1.95
            self.add(p, C(x, 0, 0.2, w, h, w + 0.4), mat, tag="boot")
            self.add(p, C(x, 0, 0.5, w + 0.3, 0.6, w + 1.4), sole, tag="sole")
            if toe:
                self.add(p, C(x, 0.4, (w + 0.4) / 2 + 0.4, w + 0.2, 1.8, toe_d), toe, tag="toe")
            if cuff:
                self.add(p, C(x, h - 0.4, 0, w + 0.4, 1.0, w + 0.4), cuff, tag="cuff")


SIDES = (-1, 1)


# ---------------------------------------------------------------- the Foundry

def kilnplate(k):
    """a walking furnace: a stove for a head with chimneys for horns, a fire in the chest, anvils on the shoulders"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.4, 0, 10.4, 9.4, 10.4), "blade", tag="stove")
    a(h, C(0, 32.8, 0, 8.6, 1.0, 8.6), "dark", tag="crown")
    a(h, C(0, 30.4, 0, 11.2, 1.2, 11.2), "dark", tag="brow")
    a(h, C(0, 22.2, 0, 10.8, 1.6, 10.8), "dark", tag="gorget")
    a(h, C(0, 24.2, 5.2, 8.0, 5.8, 0.6), "dark", tag="mouth")
    k.fire(h, C(0, 24.8, 5.5, 6.8, 4.6, 0.3))
    for x in (-2.4, -0.8, 0.8, 2.4):
        a(h, C(x, 24.4, 5.7, 0.8, 5.4, 0.5), "void", tag="bar")
    k.rivets(h, [(-4.4, 30.6), (-2.2, 30.6), (0, 30.6), (2.2, 30.6), (4.4, 30.6)], 5.7)
    for s in SIDES:
        a(h, C(s * 2.7, 33.4, -0.8, 2.6, 3.8, 2.6), "blade", tag="chimney")
        a(h, C(s * 2.7, 37.0, -0.8, 3.6, 1.0, 3.6), "dark", tag="chimney_cap")
        k.tongue(h, s * 2.7, 37.9, -0.8, 4.2, 2.2)
        a(h, C(s * 5.3, 25.0, 0, 0.6, 4.4, 5.0), "dark", tag="cheek")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.2), "blade", tag="cuirass")
    a(c, C(0, 22.6, 0, 8.7, 1.8, 6.8), "dark", tag="gorget")
    a(c, C(0, 12.2, 0, 8.7, 1.6, 6.8), "dark", tag="belt")
    a(c, C(0, 12.2, 3.5, 3.0, 1.8, 0.5), "gold", tag="buckle")
    a(c, C(0, 14.6, 3.2, 6.6, 7.2, 0.7), "dark", tag="door")
    k.fire(c, C(0, 15.4, 3.5, 5.2, 5.6, 0.3))
    for x in (-1.6, 0, 1.6):
        a(c, C(x, 15.0, 3.7, 0.7, 6.4, 0.5), "void", tag="bar")
    a(c, C(-3.5, 15.2, 3.7, 0.8, 1.4, 0.6), "gold", tag="hinge")
    a(c, C(-3.5, 19.0, 3.7, 0.8, 1.4, 0.6), "gold", tag="hinge")
    a(c, C(3.3, 17.4, 3.7, 1.0, 1.8, 0.8), "gold", tag="latch")
    a(b, C(0, 13.0, -4.8, 7.8, 10.6, 3.4), "blade", tag="boiler")
    for y in (14.6, 18.0, 21.4):
        a(b, C(0, y, -4.8, 8.2, 0.9, 3.8), "dark", tag="boiler_band")
    a(b, C(0, 16.0, -6.7, 3.2, 3.2, 0.5), "gold", tag="gauge")
    k.fire(b, C(0, 16.6, -7.0, 1.8, 2.0, 0.3))
    for s in SIDES:
        a(b, C(s * 2.7, 22.6, -5.4, 2.0, 9.0, 2.0), "dark", tag="pipe")
        a(b, C(s * 2.7, 31.4, -5.4, 2.8, 0.9, 2.8), "blade", tag="pipe_cap")
        k.tongue(b, s * 2.7, 32.2, -5.4, 3.4, 1.8)
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.2, 5.0), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 11.8, 0, 5.2, 5.0, 5.2), "blade", tag="vambrace")
        a(p, C(x, 16.3, 0, 5.5, 1.0, 5.5), "dark", tag="cuff")
        a(p, C(x, 11.6, 0, 5.5, 0.9, 5.5), "dark", tag="wrist")
        q = k.shoulder(s)
        a(q, C(x + s * 2.2, 20.4, 0, 6.2, 1.3, 7.0), "blade", tag="anvil_waist")
        a(q, C(x + s * 2.4, 21.6, 0, 7.0, 1.8, 8.4), "dark", tag="anvil_face")
        a(q, C(x + s * 7.0, 21.9, 0, 2.6, 1.3, 2.8), "dark", tag="anvil_horn")
        a(q, C(x + s * 8.6, 22.1, 0, 1.4, 0.8, 1.6), "blade", tag="anvil_horn")
        k.fire(q, C(x + s * 2.4, 23.3, 0, 1.6, 0.3, 6.6))
        k.rivets(q, [(x + s * 0.6, 20.6), (x + s * 3.8, 20.6)], 3.7)
        k.horn(q, x + s * 4.6, 23.0, 0, [(3.2, -s * 36, 3.0), (3.2, -s * 16, 2.2), (2.6, s * 10, 1.4), (1.8, s * 32, 0.8)], "blade")
        p = k.leg(s)
        x = s * 1.95
        a(p, C(x, 3.0, 0, 4.7, 9.0, 4.7), "blade", tag="cuisse")
        for y in (10.2, 8.8):
            a(p, C(x, y, 0.2, 5.1, 1.0, 5.1), "dark", tag="lame")
        a(p, C(x, 4.2, 2.5, 3.6, 3.4, 1.1), "dark", tag="knee_door")
        k.fire(p, C(x, 4.8, 3.05, 2.2, 2.2, 0.3))
        p = k.boot(s)
        a(p, C(x, 0, 0.2, 5.0, 3.8, 5.4), "blade", tag="boot")
        a(p, C(x, 3.4, 0, 5.4, 1.1, 5.4), "dark", tag="cuff")
        a(p, C(x, 0.5, 3.4, 5.6, 2.0, 3.0), "dark", tag="toe")
        a(p, C(x, 0, 0.8, 5.8, 0.6, 8.0), "void", tag="sole")
        k.rivets(p, [(x - 1.6, 1.3), (x + 1.6, 1.3)], 5.0)


def riveter(k):
    """a foundry foreman: a welder's mask, a leather apron down to the knees, one huge riveted shoulder, the tools of the trade on his back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.2, -0.6, 9.6, 9.4, 9.2), "leather", tag="coif")
    a(h, C(0, 32.4, -0.4, 8.4, 0.9, 8.4), "leather", tag="coif_top")
    a(h, C(0, 23.8, 4.3, 9.4, 8.6, 1.2), "blade", tag="mask")
    a(h, C(0, 32.0, 4.6, 8.0, 1.2, 1.4), "dark", tag="mask_brow")
    a(h, C(0, 28.0, 5.0, 7.2, 1.7, 0.4), "dark", tag="visor_frame")
    k.fire(h, C(0, 28.4, 5.2, 6.0, 0.9, 0.3))
    a(h, C(0, 24.4, 5.0, 3.2, 2.8, 1.4), "dark", tag="filter")
    for y in (24.9, 26.0):
        a(h, C(0, y, 5.8, 2.4, 0.5, 0.3), "void", tag="vent")
    a(h, C(0, 30.2, 5.0, 2.0, 1.6, 0.8), "gold", tag="lamp")
    k.fire(h, C(0, 30.5, 5.45, 1.2, 1.0, 0.3))
    for s in SIDES:
        a(h, C(s * 5.0, 28.4, 3.4, 0.9, 2.2, 2.2), "gold", tag="hinge")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "mail", tag="mail")
    a(c, C(0, 22.4, 0, 8.7, 1.7, 5.6), "leather", tag="collar")
    a(c, C(0, 12.2, 2.85, 7.4, 10.6, 0.6), "leather", tag="apron")
    a(c, C(0, 12.2, 3.1, 8.0, 1.2, 0.5), "dark", tag="apron_belt")
    for y in (15.0, 17.2, 19.4):
        k.rivets(c, [(-3.0, y), (3.0, y)], 3.3)
    a(c, C(0, 15.4, 3.2, 3.4, 4.2, 0.4), "blade", tag="plate")
    for s in SIDES:
        a(c, C(s * 2.6, 19.0, 3.2, 1.2, 5.2, 0.4), "dark", tag="strap")
    a(b, C(0, 13.0, -3.6, 1.3, 14.0, 1.3), "wood", tag="haft", rots=(("z", 32),), pivot=(0, 18, -3.6))
    a(b, C(0, 25.0, -3.6, 7.0, 4.0, 3.6), "blade", tag="sledge", rots=(("z", 32),), pivot=(0, 18, -3.6))
    a(b, C(0, 26.4, -3.6, 7.3, 1.0, 3.8), "dark", tag="sledge_band", rots=(("z", 32),), pivot=(0, 18, -3.6))
    a(b, C(0, 13.0, -4.6, 0.9, 15.0, 0.9), "dark", tag="tongs", rots=(("z", -30),), pivot=(0, 18, -4.6))
    a(b, C(1.0, 26.6, -4.6, 0.9, 4.4, 0.9), "dark", tag="tongs", rots=(("z", -30),), pivot=(0, 18, -4.6))
    a(b, C(-1.0, 26.6, -4.6, 0.9, 4.4, 0.9), "dark", tag="tongs", rots=(("z", -30),), pivot=(0, 18, -4.6))
    a(b, C(0, 28.0, -4.6, 3.6, 3.0, 2.0), "glow", tag="hot_ingot", group="fire", rots=(("z", -30),), pivot=(0, 18, -4.6))
    a(b, C(0, 25.6, -5.5, 7.4, 0.8, 0.3), "glow", tag="sledge_seam", group="fire", rots=(("z", 32),), pivot=(0, 18, -3.6))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 11.8, 0, 5.2, 4.2, 5.2), "leather", tag="gauntlet")
        a(p, C(x, 15.9, 0, 5.7, 1.4, 5.7), "leather", tag="gauntlet_flare")
        a(p, C(x, 13.0, 2.8, 3.2, 2.4, 0.5), "blade", tag="knuckle")
        p = k.leg(s)
        x = s * 1.95
        a(p, C(x, 2.4, 0, 4.5, 9.6, 4.5), "mail", tag="mail")
        a(p, C(x, 5.8, 2.7, 3.9, 6.4, 0.6), "leather", tag="apron_panel")
        k.rivets(p, [(x - 1.2, 7.0), (x + 1.2, 7.0), (x - 1.2, 9.6), (x + 1.2, 9.6)], 3.1)
        a(p, C(x, 2.6, 2.3, 3.4, 3.0, 0.8), "blade", tag="shin")
        k.rivets(p, [(x - 1.1, 3.0), (x + 1.1, 3.0)], 2.8)
        p = k.boot(s)
        a(p, C(x, 0, 0.3, 4.9, 3.6, 5.2), "leather", tag="boot")
        a(p, C(x, 0.4, 2.2, 5.1, 2.2, 3.0), "blade", tag="toe_cap")
        a(p, C(x, 0, 0.5, 5.3, 0.6, 6.8), "void", tag="sole")
        a(p, C(x, 3.3, 0, 5.3, 0.9, 5.3), "dark", tag="cuff")
    p, x = k.shoulder(1), 6.0
    a(p, C(x + 1.8, 20.9, 0, 7.2, 3.9, 7.6), "blade", tag="shoulder_plate")
    a(p, C(x + 1.8, 24.6, 0, 6.0, 1.0, 6.4), "dark", tag="shoulder_top")
    a(p, C(x + 1.8, 20.4, 0, 7.6, 0.9, 8.0), "dark", tag="shoulder_edge")
    k.rivets(p, [(x + r, y) for r in (-0.6, 1.8, 4.2) for y in (21.6, 23.2)], 3.9, 1.0)
    p, x = k.shoulder(-1), -6.0
    a(p, C(x - 0.4, 21.0, 0, 5.4, 2.8, 5.4), "leather", tag="cop")
    a(p, C(x - 0.4, 20.5, 0, 5.8, 0.8, 5.8), "dark", tag="cop_edge")


def slagrunner(k):
    """a runner who carries coal through the fire: glowing goggles, a scarf streaming behind, a sack on the back, vials of slag on the belt, a heat shield on the forearm"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 26.0, -0.4, 9.0, 7.0, 9.0), "cloth", tag="hood")
    a(h, C(0, 32.8, -0.6, 7.2, 0.9, 7.2), "cloth", tag="hood_top")
    a(h, C(0, 28.4, 0, 9.6, 1.3, 9.6), "dark", tag="strap")
    a(h, C(0, 23.2, 0.2, 9.8, 3.8, 10.0), "wrap", tag="scarf")
    a(h, C(0, 22.4, 0, 10.4, 1.6, 10.4), "wrap", tag="scarf_fold")
    for s in SIDES:
        a(h, C(s * 2.2, 27.4, 5.0, 3.4, 3.2, 1.0), "gold", tag="goggle")
        a(h, C(s * 2.2, 27.8, 5.45, 2.4, 2.4, 0.3), "void", tag="goggle_rim")
        k.fire(h, C(s * 2.2, 28.1, 5.6, 1.8, 1.8, 0.3))
    for z, w, y, r, ln in ((-5.2, 3.0, 26.0, 22, 11.0), (-5.3, 2.4, 24.6, 44, 9.0)):
        a(h, C(0, y - ln, z, w, ln, 0.6), "wrap", tag="scarf_tail", rots=(("x", r),), pivot=(0, y, z))
    a(c, C(0, 12.2, 0, 8.4, 11.8, 4.8), "cloth", tag="shirt")
    a(c, C(0, 14.4, 0, 8.7, 9.6, 5.2), "leather", tag="jerkin")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 5.4), "dark", tag="belt")
    for x, m in ((-3.0, "gold"), (-1.2, "gold"), (2.6, "gold")):
        a(c, C(x, 12.4, 3.0, 1.4, 2.6, 1.2), m, tag="vial_cap")
        k.fire(c, C(x, 12.6, 3.65, 1.0, 1.6, 0.3))
    a(c, C(0, 14.0, 2.75, 1.0, 10.0, 0.4), "dark", tag="strap", rots=(("z", 26),), pivot=(0, 19, 2.75))
    a(c, C(0, 14.0, 2.85, 1.0, 10.0, 0.4), "dark", tag="strap", rots=(("z", -26),), pivot=(0, 19, 2.85))
    a(b, C(0, 13.6, -4.6, 7.6, 8.6, 4.2), "cloth", tag="sack")
    a(b, C(0, 15.0, -6.8, 8.0, 0.9, 0.5), "dark", tag="sack_strap")
    a(b, C(0, 22.2, -4.6, 5.4, 1.2, 3.2), "wrap", tag="sack_neck")
    a(b, C(0, 23.3, -4.6, 4.2, 1.8, 2.6), "void", tag="coal")
    k.fire(b, C(0.8, 24.6, -4.2, 1.4, 0.8, 1.4))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 12.2, 0, 5.0, 5.0, 5.0), "wrap", tag="wraps")
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "wrap", tag="wraps")
        k.elbow(s, "wrap")
        for y in (13.4, 15.6, 19.6):
            a(p, C(x, y, 0, 5.3, 0.6, 5.3), "dark", tag="wrap_bind")
        p = k.leg(s)
        x = s * 1.95
        a(p, C(x, 6.4, 0, 4.9, 5.6, 4.9), "cloth", tag="breeches")
        a(p, C(x, 3.0, 0, 4.4, 3.6, 4.4), "wrap", tag="shin_wrap")
        a(p, C(x, 5.0, 2.3, 3.2, 2.6, 0.8), "leather", tag="knee")
        p = k.boot(s)
        a(p, C(x, 0.9, 0.3, 4.7, 3.8, 5.2), "leather", tag="boot")
        a(p, C(x, 0, 0.4, 5.2, 1.0, 6.4), "void", tag="sole")
        a(p, C(x, 4.4, 0, 5.2, 1.2, 5.2), "leather", tag="cuff")
    p = k.leg(1)
    a(p, C(4.3, 7.0, 0, 1.4, 3.4, 3.2), "leather", tag="pouch")
    p, x = k.arm(1), 6.0
    a(p, C(x + 2.9, 11.6, 0, 1.0, 5.7, 6.0), "blade", tag="heat_shield")
    a(p, C(x + 3.5, 12.0, 0, 0.5, 4.9, 4.8), "dark", tag="heat_shield_face")
    k.fire(p, C(x + 3.8, 13.4, 0, 0.3, 2.0, 2.0))
    a(k.shoulder(1), C(x + 0.6, 20.9, 0, 5.8, 2.6, 5.8), "leather", tag="cop")
    a(k.shoulder(-1), C(-x - 0.2, 21.2, 0, 5.2, 2.2, 5.2), "leather", tag="cop")


def bellows(k):
    """the furnace's priest: a smoking stovepipe mitre over a chain veil, a censer at the hip, the bellows themselves worn on the back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.6, -0.4, 9.4, 8.2, 9.6), "cloth", tag="hood")
    a(h, C(0, 23.0, 4.5, 8.4, 6.0, 0.7), "mail", tag="veil")
    a(h, C(0, 31.4, 0, 9.0, 1.2, 9.0), "acc", tag="mitre_band")
    a(h, C(0, 32.4, 0, 7.8, 6.4, 7.8), "dark", tag="mitre")
    a(h, C(0, 38.6, 0, 9.2, 1.1, 9.2), "blade", tag="mitre_flare")
    k.tongue(h, 0, 39.6, 0, 6.0, 4.4)
    for y in (33.4, 35.2, 37.0):
        k.fire(h, C(0, y, 3.95, 4.6, 0.8, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 21.4, 0, 8.7, 2.8, 6.0), "wrap", tag="mantle")
    a(c, C(0, 19.4, 0, 8.7, 2.2, 5.6), "cloth", tag="mantle_under")
    k.fire(c, C(0, 12.6, 2.75, 2.4, 11.0, 0.3))
    a(c, C(-1.6, 12.2, 2.8, 0.7, 11.6, 0.5), "acc", tag="stole")
    a(c, C(1.6, 12.2, 2.8, 0.7, 11.6, 0.5), "acc", tag="stole")
    a(c, C(0, 12.2, 0, 8.7, 1.4, 5.8), "leather", tag="sash")
    p = k.leg(1)
    a(p, C(3.2, 9.0, 3.4, 0.4, 3.2, 0.4), "acc", tag="censer_chain")
    a(p, C(3.2, 6.4, 3.4, 2.8, 2.6, 2.8), "blade", tag="censer")
    a(p, C(3.2, 9.0, 3.4, 1.6, 0.6, 1.6), "dark", tag="censer_lid")
    k.fire(p, C(3.2, 6.9, 4.9, 1.8, 1.0, 0.3))
    a(b, C(0, 12.0, -4.0, 7.8, 1.2, 4.6), "wood", tag="bellows_board")
    a(b, C(0, 22.4, -5.6, 5.4, 1.2, 3.0), "wood", tag="bellows_board")
    for i, (d, y) in enumerate(((5.0, 13.2), (3.8, 14.8), (5.0, 16.4), (3.8, 18.0), (4.6, 19.6), (3.4, 21.2))):
        a(b, C(0, y, -3.2 - d / 2, 7.4 - i * 0.3, 1.6, d), "leather" if i % 2 else "cloth", tag="pleat")
    a(b, C(0, 23.6, -5.6, 2.0, 3.8, 2.0), "blade", tag="nozzle")
    a(b, C(0, 27.2, -5.6, 3.0, 0.8, 3.0), "dark", tag="nozzle_lip")
    k.tongue(b, 0, 27.9, -5.6, 3.0, 1.6)
    for i in range(16):        # the ember wheel behind the head
        t = i * 22.5
        r = math.radians(t)
        cx, cy = -math.sin(r) * 9.6, 29.0 + math.cos(r) * 9.6
        a(b, C(cx, cy - 1.2, -7.0, 3.6 if i % 2 else 2.4, 2.4, 1.0), "gold", tag="wheel", rots=(("z", t),), pivot=(cx, cy, -7.0))
        if not i % 2:
            k.fire(b, C(-math.sin(r) * 12.0, 29.0 + math.cos(r) * 12.0 - 1.0, -7.0, 1.4, 2.4, 0.7), rots=(("z", t),), pivot=(-math.sin(r) * 12.0, 29.0 + math.cos(r) * 12.0, -7.0))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.2, 5.0), "cloth", tag="sleeve")
        k.elbow(s, "cloth")
        a(p, C(x + s * 0.3, 11.4, 0, 5.4, 4.4, 5.4), "cloth", tag="flare")
        k.fire(p, C(x + s * 0.3, 11.4, 0, 5.6, 0.6, 5.6))
        q = k.shoulder(s)
        a(q, C(x + s * 0.5, 21.0, 0, 5.8, 3.0, 5.8), "blade", tag="coal_plate")
        a(q, C(x + s * 0.5, 23.8, 0, 4.0, 0.9, 4.0), "dark", tag="coal_plate_top")
        p = k.leg(s)
        x = s * 1.95
        a(p, C(x, 2.4, 0, 4.4, 9.4, 4.4), "cloth", tag="wrap")
        p = k.boot(s)
        a(p, C(x, 0, 0.5, 4.6, 3.0, 5.8), "leather", tag="boot")
        a(p, C(x, 1.4, 3.8, 2.2, 1.6, 1.2), "dark", tag="curled_toe")
        a(p, C(x, 0, 0.5, 4.9, 0.5, 6.2), "void", tag="sole")


DESIGNS = {"kilnplate": kilnplate, "riveter": riveter, "slagrunner": slagrunner, "bellows": bellows}


def design(**paint):
    """registers a set's design under its function's name, with what it's painted in"""
    def reg(f):
        DESIGNS[f.__name__] = f
        PAINT[f.__name__] = paint
        return f
    return reg


import armorsets_a  # noqa: E402,F401
import armorsets_b  # noqa: E402,F401
import armorsets_c  # noqa: E402,F401
import armorsets_d  # noqa: E402,F401
import armorsets_e  # noqa: E402,F401
import armorsets_f  # noqa: E402,F401
