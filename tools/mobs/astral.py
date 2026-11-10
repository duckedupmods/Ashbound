"""Act IV's bosses, the Astral Beings that keep the last two Fires' star-embers, each in its own Astral Ring (Veyra's).
Their look: night-blue and black like the space between stars, pale star-glass, gold that's gone cold, and stars - small
hard points of white-blue light - set in them.

    nebula_moth        boss   a moth the size of a house, its wings a field of stars and drifting nebula-colour, a
                              thorax of black chitin, a crown of feathered antennae, eyes like two moons, legs barbed
    constellation_knight boss Halcyr: a knight whose armour is pricked through with stars joined by thin lines of light,
                              a tall crested helm with a single star for a face, a cloak of night, and a comet for a lance
    orrery_magus       boss   a robed giant with no head: where it should be, a small burning star with brass orbits
                              turning round it, planets on them; a staff topped with a ringed world

    python tools/monsterforge.py astral --preview ; python tools/connect_check.py astral
"""
import math

import vox2 as X
from vox2 import ramp
from serpent_ziggurat import grow
from _folk import lit, legs, arms, held, quad
from tidewrack import Cc

NIGHT = ramp("#03040c", "#070a18", "#0c1226", "#141c38", "#1e284c", "#2a3662")
CHITIN = ramp("#020204", "#06060c", "#0c0c16", "#141422", "#1e1e30")
GLASS = ramp("#30405a", "#465a7a", "#62789a", "#86a0bc", "#b0c6dc", "#dceaf8")
GOLD = ramp("#2a2008", "#463610", "#6a5418", "#927422", "#b89632", "#dcbc5a")
NEBULA = ramp("#1a0830", "#2e1048", "#4a1a66", "#6a2a82", "#8c4aa0", "#b47ac0")
TEAL = ramp("#04202a", "#083640", "#0e5058", "#186c70", "#2a8c88", "#46aca0")
STAR = ramp("#3a5aa0", "#6a8ad0", "#9ab8f0", "#c8dcff", "#ecf4ff", "#ffffff")
SUNC = ramp("#6a2a04", "#a04a08", "#d47414", "#f4a42a", "#ffd25a", "#fff4c0")
TAR = ramp("#010102", "#030308", "#06060c", "#0a0a12")


def shaders():
    return {
        "night": X.surf(NIGHT, 0.45, 1.0, 0.14, 0.1, pattern=lambda p, n, i, j, w, h: 0.8 if (i * 37 + j * 61) % 47 == 0 else 0.0),
        "chitin": X.surf(CHITIN, 0.5, 1.3, 0.12, 0.22),
        "glass": X.facets(GLASS),
        "gold": X.surf(GOLD, 0.55, 1.4, 0.14, 0.24),
        "nebula": X.surf(NEBULA, 0.5, 1.1, 0.2, 0.06, pattern=lambda p, n, i, j, w, h: 0.9 if (i * 29 + j * 17) % 41 == 0 else 0.0),
        "teal": X.surf(TEAL, 0.5, 1.1, 0.2, 0.06, pattern=lambda p, n, i, j, w, h: 0.9 if (i * 23 + j * 31) % 37 == 0 else 0.0),
        "star": X.glow(STAR),
        "eye": X.glow(STAR, 0.86, 0.12),
        "sun": X.glow(SUNC),
        "dark": X.dark(TAR),
    }


GLOWS = {"star", "eye", "sun"}


def spark(k, part, at, s=0.8):
    k.box(part, Cc(*at, s, s, s), "star", tag="star")


# ================================================================ the Nebula Moth

def nebula_moth():
    k = X.Kit("nebula_moth")
    body, hd, ab, joints = quad(k, "chitin", y=14, chest=((6, 9, 9), (10, 11, 10), (14, 10, 9)), haunch=((4, 8, 8), (8, 9, 9), (12, 7.6, 7.6)),
                                leg_w=1.8, foot_w=1.4, front_z=4, back_z=-6, x=4.0, head_at=(0, 15, 8), head_rot=-10, claw="dark", foot_len=4.6)
    # the thorax furred in pale glass, the abdomen long and banded, tipped with a star
    for side, nm in ((1, "l"), (-1, "r")):          # the toes the claws grow from
        for i, z in ((0, 4), (1, -6)):
            k.box(k.parts["leg_%s%d" % (nm, i)], Cc(side * 4.6, 0.6, z + 4.2, 3.4, 1.2, 1.6), "chitin", tag="toe")
    k.blob(body, (0, 18.0, 2), (5.6, 5.2, 6.0), "glass", "fur", step=0.8)
    for i in range(6):
        k.box(ab, Cc(0, 15.0 - i * 0.4, -4 - i * 2.2, 8.0 - i * 0.9, 6.0 - i * 0.6, 2.6), "chitin" if i % 2 else "night", tag="abdomen")
    spark(k, ab, (0, 13.4, -16.4), 1.4)
    # the head: two moon eyes, a crown of feathered antennae
    k.blob(hd, (0, 17.0, 11.0), (3.4, 3.2, 3.0), "chitin", "head", step=0.6)
    for sx in (-1, 1):
        k.blob(hd, (sx * 2.8, 17.6, 12.2), (1.8, 2.0, 1.6), "eye", "moon_eye", step=0.5)
        a0 = (sx * 1.2, 19.6, 11.6)
        tip = (sx * 7.0, 28.0, 15.0)
        k.limb(hd, a0, tip, 0.6, "gold", "antenna")
        for t in range(1, 7):
            q = tuple(a0[j] + (tip[j] - a0[j]) * t / 7 for j in range(3))
            k.limb(hd, q, (q[0] + sx * 2.0, q[1] - 0.6, q[2] - 1.2), 0.4, "gold", "antenna_feather")
            k.limb(hd, q, (q[0] - sx * 0.8, q[1] - 0.4, q[2] + 1.4), 0.4, "gold", "antenna_feather")
    # four great wings: solid panels, a starfield of nebula and teal, edged in night, an eye of stars on each fore wing
    def panel(part, root, sx, span, H, up, back, mat):
        n_u, n_v = int(span / 1.6), int(H / 1.6)
        for iu in range(n_u + 1):
            u = iu * 1.6
            hh = H * math.sin(math.pi * (0.12 + 0.88 * u / span)) * (1.0 - 0.25 * u / span)
            for iv in range(int(hh / 1.6) + 1):
                v = iv * 1.6
                edge = iu == n_u or iv >= int(hh / 1.6) - 0 or iu == 0
                p = (root[0] + sx * u, root[1] + up * u + H * 0.35 - v, root[2] - back * u - 0.15 * v)
                k.box(part, Cc(p[0], p[1], p[2], 2.0, 2.0, 0.6), "night" if edge else mat, tag="wing")
        return n_u
    for sx in (-1, 1):
        panel(body, (sx * 4.0, 20.0, 2.0), sx, 26, 20, 0.45, 0.25, "nebula")
        panel(ab, (sx * 4.0, 16.0, -3.0), sx, 18, 13, 0.1, 0.6, "teal")
        cx, cy, cz = sx * 4.0 + sx * 15.0, 20.0 + 0.45 * 15.0 + 20 * 0.35 - 8.0, 2.0 - 0.25 * 15.0 - 1.2 - 0.35
        for i in range(8):                            # the eye: a ring of stars round a dark pupil
            a_ = i / 8 * 2 * math.pi
            spark(k, body, (cx + math.cos(a_) * 3.0, cy + math.sin(a_) * 3.0, cz), 1.0)
        k.box(body, Cc(cx, cy, cz, 2.6, 2.6, 0.7), "dark", tag="wing_eye")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ Halcyr, the Constellation Knight

def constellation_knight():
    k = X.Kit("constellation_knight")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(15, 12.0, 8.6), (22, 12.4, 8.8)], "night", "faulds")
    for x in (-4.4, -1.5, 1.5, 4.4):
        k.box(hips, Cc(x, 14.4, 4.6, 2.6, 6.0, 0.8), "gold", tag="tasset")
    legs(k, hips, 21, 11, 3.6, "night", "night", knee_mat="gold", lean=-4, bend=6, w=5.4)
    to = k.part("torso", (0, 22, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(22, 12.4, 8.8), (29, 14.4, 9.6), (35, 17.4, 10.2), (39, 15.4, 9.2)], "night", "breastplate")
    # stars on the breastplate, joined by thin lines of light (a constellation)
    pts = [(-4.0, 34.0), (-1.0, 31.0), (2.6, 33.6), (4.4, 28.0), (0.4, 26.0), (-3.4, 25.0)]
    for (x, y) in pts:
        spark(k, to, (x, y, 5.3), 1.0)
    for (a, b) in zip(pts, pts[1:]):
        k.limb(to, (a[0], a[1], 5.2), (b[0], b[1], 5.2), 0.25, "star", "constellation")
    # pauldrons: tall, swept up into points, gold-edged
    for sx in (-1, 1):
        k.blob(to, (sx * 9.6, 37.0, 0), (4.4, 2.8, 5.4), "night", "pauldron", step=0.6)
        k.shard(to, (sx * 11.0, 39.0, 0), (sx * 0.6, 1, 0), 4.0, 1.6, mat="gold", tag="pauldron_spike")
        k.box(to, Cc(sx * 9.6, 35.0, 0, 9.0, 0.8, 11.0), "gold", tag="pauldron_rim")
        spark(k, to, (sx * 10.4, 38.2, 4.6), 0.9)
    # the cloak of night, star-spotted, falling to the heels
    for i in range(8):
        x = -7.0 + i * 2.0
        k.box(to, Cc(x, 22.0, -5.4 - abs(i - 3.5) * 0.2, 2.2, 32.0 - (i % 2) * 2.0, 0.7), "night", tag="cloak")
    hd = k.part("head", (0, 39, 0.4), (("x", -4),), "torso")
    k.limb(hd, (0, 38.0, 0.2), (0, 40.4, 0.4), 5.0, "night", "gorget")
    k.box(hd, Cc(0, 44.0, 0.6, 7.0, 8.0, 7.6), "night", tag="helm")
    k.box(hd, Cc(0, 44.6, 4.45, 1.2, 6.4, 0.3), "gold", tag="helm_ridge")
    k.box(hd, Cc(0, 44.6, 4.6, 2.2, 2.2, 0.3), "eye", tag="star_face")
    for i in range(8):                                # the crest, a fan of gold blades
        a = math.radians(-60 + i * 17)
        k.limb(hd, (0, 48.0, 0.6), (0, 48.0 + math.cos(a) * 7.0, 0.6 - math.sin(a) * 7.0), 0.9, "gold", "crest")
    arms(k, to, 10.4, 36, "night", {1: ((("x", -20), ("z", 20)), (("x", -40),)), -1: ((("x", -70), ("z", -6)), (("x", -20),))}, glove="gold", w=4.6)
    # the comet-lance: a long haft, a burning head of star-glass, a tail streaming back
    ln = held(k, "lance", "r", (-10.4, 15.6, 0.3), (("x", 80),))
    k.limb(ln, (-10.4, -2.0, 0.3), (-10.4, 44.0, 0.3), 1.6, "gold", "haft")
    k.box(ln, Cc(-10.4, 18.0, 0.3, 4.4, 2.0, 4.4), "gold", tag="vamplate")
    k.blob(ln, (-10.4, 48.0, 0.3), (2.6, 4.2, 2.6), "star", "comet_head", step=0.6)
    k.shard(ln, (-10.4, 51.0, 0.3), (0, 1, 0), 5.0, 2.0, mat="glass", tag="comet_point")
    for i in range(6):
        k.limb(ln, (-10.4, 46.0 - i * 3.4, 0.3), (-10.4 + (i % 2 - 0.5) * 1.6, 43.0 - i * 3.4, -1.4 - i * 0.4), 1.6 - i * 0.2, "star" if i < 2 else "glass", "comet_tail")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.1)
    return k.s, k.parts


# ================================================================ the Orrery Magus

def orrery_magus():
    k = X.Kit("orrery_magus")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(1.0, 16.0, 13.0), (8.0, 14.0, 11.0), (16.0, 12.0, 9.4), (22.0, 11.2, 8.4)], "night", "robe", step=1.2)
    for i in range(12):                               # the robe's hem, embroidered with a band of gold and stars
        a = i / 12 * 2 * math.pi
        k.box(hips, Cc(math.sin(a) * 7.6, 2.4, math.cos(a) * 6.2, 3.4, 1.4, 1.4), "gold", tag="hem")
        if i % 3 == 0:
            spark(k, hips, (math.sin(a) * 7.0, 6.0, math.cos(a) * 5.8), 0.8)
    legs(k, hips, 21, 11, 3.0, "night", "night", lean=-2, bend=4, w=4.0, cuff=False)
    to = k.part("torso", (0, 22, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(22, 11.2, 8.4), (29, 12.4, 8.8), (35, 15.4, 9.4), (38, 13.0, 8.4)], "night", "chest")
    k.box(to, Cc(0, 30.0, 4.6, 3.0, 14.0, 0.6), "gold", tag="stole")
    for sx in (-1, 1):
        k.blob(to, (sx * 8.4, 36.4, 0), (3.8, 2.0, 4.6), "gold", "mantle", step=0.6)
        k.box(to, Cc(sx * 8.8, 34.0, 0, 5.0, 3.0, 8.0), "night", tag="mantle_drape")
    # no head: a neck-ring of gold, and over it a small burning star with orbits round it, planets on them
    hd = k.part("head", (0, 38, 0.4), (), "torso")
    k.box(hd, Cc(0, 38.6, 0.4, 6.0, 1.6, 6.0), "gold", tag="neck_ring")
    k.limb(hd, (0, 39.0, 0.4), (0, 42.0, 0.4), 1.2, "gold", "spindle")
    k.blob(hd, (0, 45.0, 0.4), (3.0, 3.0, 3.0), "sun", "star_head", step=0.6)
    for ring, (r, tilt, n) in enumerate(((6.0, 0.25, 36), (9.0, -0.4, 54), (12.0, 0.15, 72))):
        for i in range(n):
            a = i / n * 2 * math.pi
            x, z = math.cos(a) * r, math.sin(a) * r
            y = 45.0 + math.sin(a) * r * tilt
            k.box(hd, Cc(x, y, z + 0.4, 1.4, 0.7, 1.4), "gold", tag="orbit")
        a = ring * 2.1 + 0.6                          # its planet
        x, z = math.cos(a) * r, math.sin(a) * r
        y = 45.0 + math.sin(a) * r * tilt
        k.blob(hd, (x, y, z + 0.4), (1.4 + ring * 0.4, 1.4 + ring * 0.4, 1.4 + ring * 0.4), ("teal", "nebula", "glass")[ring], "planet", step=0.5)
    for i in range(3):                                # spokes holding the orbits to the spindle
        a = i * 2.1
        k.limb(hd, (0, 42.0, 0.4), (math.cos(a) * 12.0, 45.0 + math.sin(a) * 12.0 * 0.15, math.sin(a) * 12.0 + 0.4), 0.4, "gold", "spoke")
    arms(k, to, 9.4, 35, "night", {1: ((("x", -40), ("z", 26)), (("x", -60),)), -1: ((("x", -30), ("z", -10)), (("x", -40),))}, glove="glass", w=4.0, long=1.2)
    st = held(k, "staff", "r", (-9.4, 14.0, 0.3), (("x", 60),))
    k.limb(st, (-9.4, 0.0, 0.3), (-9.4, 44.0, 0.3), 1.3, "gold", "staff")
    k.blob(st, (-9.4, 48.0, 0.3), (3.2, 3.2, 3.2), "teal", "world", step=0.6)
    for i in range(24):
        a = i / 24 * 2 * math.pi
        k.box(st, Cc(-9.4 + math.cos(a) * 5.2, 48.0 + math.sin(a) * 1.2, 0.3 + math.sin(a) * 5.2, 1.0, 0.5, 1.0), "gold", tag="world_ring")
    for i in range(4):
        k.limb(st, (-9.4, 44.0, 0.3), (-9.4 + math.cos(i * 1.57) * 2.6, 45.6, 0.3 + math.sin(i * 1.57) * 2.6), 0.5, "gold", "claw")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.1)
    return k.s, k.parts


MOBS = {
    "nebula_moth": dict(make=nebula_moth, rig="crawler", ent=(5.0, 5.0), boss=True, stats=dict(hp=1500, speed=0.28, dmg=24, armor=10, kb=0.8)),
    "constellation_knight": dict(make=constellation_knight, ent=(2.4, 8.0), boss=True, stats=dict(hp=1700, speed=0.27, dmg=28, armor=18, kb=1.0)),
    "orrery_magus": dict(make=orrery_magus, ent=(2.4, 8.5), boss=True, stats=dict(hp=1500, speed=0.22, dmg=26, armor=12, kb=0.6)),
}
