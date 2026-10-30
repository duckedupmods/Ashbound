"""The Sky Legion: the bronze host of the old sky-gods, who hold the world's heavenly fortresses, aviaries, blimps,
coliseums and the tops of the high places, built by hand (tools/vox2.py). Polished bronze and white marble, royal
blue cloth and horsehair crests, gold leaf, and the white-gold of the sun in their eyes. (Not the Eclipse
Cathedral's angels nor the Storm Bastion's lightning: these are the old heroes' armies, bronze and marble.)

    harpy          swarm   a woman's body gone to bird: wings for arms, a vulture's head in a bronze collar, talons
    hoplite        guard   a Corinthian helm under a tall blue crest, a bronze muscle cuirass, the round aspis with
                           the sun on it, a long spear
    talos          brute   a bronze giant made by the smith-god: seamed plates, a blank calm face, one glowing vein
                           of ichor down its body, fists like anvils
    oracle         caster  a marble-pale seer, blindfolded with gold, a laurel crown, smoke from a sun-disc staff
    peltast        skirm   a light skirmisher: a Thracian helm with its crest curling forward, a crescent shield,
                           a quiver of javelins, a javelin in hand
    gryphon_rider  elite   a gryphon - an eagle's head and wings on a lion's body - and the bronze champion riding
                           it, a lance couched and a blue cloak streaming

    python tools/monsterforge.py sky_legion --preview ; python tools/mobsheet.py sky_legion
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import grow
from _folk import lit, eyes, legs, arms, held, quad, wing

BRONZE = ramp("#170c06", "#2a160a", "#42240e", "#5e3614", "#7c4a1c", "#9a6026", "#b87a36")
MARBLE = ramp("#4a4846", "#6a6866", "#8c8a86", "#aeaca8", "#cecbc6", "#ebe8e2")
BLUE = ramp("#06081e", "#0c1032", "#141a4a", "#1e2664", "#2a3480", "#38449a")
GOLD = ramp("#3a2606", "#62420c", "#906614", "#bc8e22", "#e0b438", "#fcdc6a")
SKIN = ramp("#3a2a20", "#544032", "#705644", "#8c6e58", "#a8886e")
FEATHER = ramp("#0e0c0a", "#1c1814", "#2c2620", "#3e362c", "#524838", "#6a5e4a")
WHITEF = ramp("#5a5650", "#7a766e", "#9a958c", "#bab5aa", "#d8d4c8")
LION = ramp("#2a1a0c", "#422a14", "#5c3c1c", "#785026", "#946832", "#b08240")
LEATHER = ramp("#120c08", "#1c140e", "#281c14", "#36261a")
SUN = ramp("#7a4a04", "#b07a0a", "#e0aa1e", "#ffd250", "#fff0a4", "#fffcec")
ICHOR = ramp("#7a3a04", "#b0600a", "#f09a1e", "#ffc850", "#fff0a0")
SMOKE = ramp("#2a2a30", "#3e3e46", "#56565e", "#70707a")


def shaders():
    return {
        "bronze": X.surf(BRONZE, 0.56, 1.6, 0.1, 0.3),
        "marble": X.surf(MARBLE, 0.56, 1.2, 0.08, 0.12, pattern=lambda p, n, i, j, w, h: -0.12 if (i * 7 + j * 3) % 13 == 0 else 0.0),
        "blue": X.surf(BLUE, 0.52, 1.1, 0.18, 0.04),
        "gold": X.surf(GOLD, 0.58, 1.6, 0.08, 0.3),
        "skin": X.wrinkled(SKIN, 0.5),
        "feather": X.surf(FEATHER, 0.5, 1.1, 0.22, 0.02, pattern=lambda p, n, i, j, w, h: -0.16 if j % 3 == 0 else 0.04),
        "whitef": X.surf(WHITEF, 0.5, 1.1, 0.2, 0.02, pattern=lambda p, n, i, j, w, h: -0.12 if j % 3 == 0 else 0.04),
        "lion": X.surf(LION, 0.5, 1.1, 0.22, 0.04, stripe=3),
        "leather": X.surf(LEATHER, 0.5, 1.1, 0.2, 0.04),
        "horn": X.surf(FEATHER, 0.6, 1.4, 0.08, 0.2),
        "smoke": X.surf(SMOKE, 0.5, 0.9, 0.3, 0.0, holes=True),
        "sun": X.glow(SUN),
        "ichor": X.glow(ICHOR),
        "eye": X.glow(SUN, 0.86, 0.12),
        "dark": X.dark(LEATHER),
    }


GLOWS = {"sun", "ichor", "eye"}


def corinthian(k, part, c, s=1.0, crest="blue", side_crest=False):
    """the Corinthian helm: a bronze bowl down over the face, almond eye-holes, a nose-guard, cheek-pieces, a crest"""
    cx, cy, cz = c
    k.blob(part, (cx, cy + 3.4 * s, cz), (3.8 * s, 4.4 * s, 4.0 * s), "bronze", "helm", step=0.6)
    k.box(part, C(cx, cy - 1.0 * s, cz + 0.6 * s, 7.0 * s, 4.6 * s, 7.2 * s), "bronze", tag="cheek_pieces")
    k.box(part, C(cx, cy - 0.6 * s, cz + 4.0 * s, 1.6 * s, 4.0 * s, 0.4), "dark", tag="mouth_slot")
    for sx in (-1, 1):
        k.box(part, C(cx + sx * 1.5 * s, cy + 3.0 * s, cz + 3.9 * s, 2.0 * s, 1.0 * s, 0.4), "dark", tag="eye_hole")
        k.box(part, C(cx + sx * 1.5 * s, cy + 3.2 * s, cz + 4.0 * s, 1.2 * s, 0.6 * s, 0.3), "eye", tag="eye")
    k.box(part, C(cx, cy + 1.6 * s, cz + 4.2 * s, 0.9 * s, 3.0 * s, 0.6), "bronze", tag="nasal")
    k.box(part, C(cx, cy + 4.4 * s, cz + 3.9 * s, 6.4 * s, 0.6 * s, 0.5), "gold", tag="brow_line")
    if not side_crest:                            # the crest, front to back, standing tall then falling behind
        k.box(part, C(cx, cy + 7.4 * s, cz, 1.0 * s, 1.0 * s, 7.0 * s), "bronze", tag="crest_holder")
        for i in range(9):
            z = cz + 3.6 * s - i * 1.0 * s
            top = cy + (13.0 - abs(i - 3) * 0.7) * s
            k.box(part, C(cx, cy + 8.0 * s, z, 1.6 * s, top - cy - 8.0 * s, 1.05 * s), crest, tag="crest")
        for i in range(4):
            k.box(part, C(cx, cy + (8.0 - i * 2.4) * s, cz - 5.4 * s - i * 0.4, 1.6 * s, 3.0 * s, 1.2 * s), crest, tag="crest_tail")


def sun_disc(k, part, c, r, axis="x", mat="gold"):
    """a sun: a disc and rays"""
    cx, cy, cz = c
    if axis == "x":
        k.box(part, C(cx, cy - r * 0.6, cz, 0.6, r * 1.2, r * 1.2), mat, tag="sun_disc")
        k.box(part, C(cx + 0.2, cy - r * 0.35, cz, 0.6, r * 0.7, r * 0.7), "sun", tag="sun_core")
        for i in range(8):
            a = i * math.pi / 4
            k.shard(part, (cx, cy + math.sin(a) * r * 0.6, cz + math.cos(a) * r * 0.6), (0, math.sin(a), math.cos(a)), r * 0.6, r * 0.25, mat=mat, tag="sun_ray")
    else:
        k.box(part, C(cx, cy - r * 0.6, cz, r * 1.2, r * 1.2, 0.6), mat, tag="sun_disc")
        k.box(part, C(cx, cy - r * 0.35, cz + 0.2, r * 0.7, r * 0.7, 0.6), "sun", tag="sun_core")
        for i in range(8):
            a = i * math.pi / 4
            k.shard(part, (cx + math.cos(a) * r * 0.6, cy + math.sin(a) * r * 0.6, cz), (math.cos(a), math.sin(a), 0), r * 0.6, r * 0.25, mat=mat, tag="sun_ray")


def pteruges(k, hips, y, w, d, n=8, mat="leather", L=7.0):
    """the skirt of hanging leather strips under a cuirass, bronze-tipped"""
    for i in range(n):
        a = i * 2 * math.pi / n
        x, z = math.sin(a) * w * 0.5, math.cos(a) * d * 0.5
        k.box(hips, C(x, y - L, z, 2.2, L, 2.2), mat, tag="pteruges")
        k.box(hips, C(x, y - L, z, 2.4, 0.8, 2.4), "bronze", tag="pteruges_tip")


# ================================================================ the Harpy (swarm)

def harpy():
    """The legion's hounds are harpies: something like a woman that has gone most of the way to a vulture, wings
    where her arms were, legs ending in hooked talons, a bare red-necked vulture's head on a bronze collar, and the
    sun's light in its little eyes."""
    k = X.Kit("harpy")
    hips = k.part("hips", (0, 15, 0))
    k.stack(hips, 0, 0, [(9, 9.0, 7.0), (15, 9.6, 7.4)], "feather", "feather_skirt")
    for i in range(7):
        x = -3.6 + i * 1.2
        k.box(hips, C(x, 5.0 + (i % 2) * 1.4, -3.4, 1.4, 6.0, 0.8), "feather", tag="tail_feather")
    for side, nm in ((1, "l"), (-1, "r")):        # bird legs: a feathered thigh, a scaled shank, talons
        xx = side * 2.6
        th = k.part("thigh_" + nm, (xx, 14, 0), (("x", -20), ("z", side * 4)), hips)
        sh = k.part("shin_" + nm, (xx, 8, 0), (("x", 36),), th)
        ft = k.part("foot_" + nm, (xx, 2.0, 0), (("x", -16),), sh)
        k.stack(th, xx, 0, [(8.2, 4.0, 4.2), (14, 5.0, 5.2)], "feather", "thigh")
        k.limb(sh, (xx, 8.0, 0), (xx, 2.2, 0), 1.6, "horn", "shank")
        k.box(ft, C(xx, 0, 0.6, 2.4, 1.6, 2.4), "horn", tag="foot")
        for t in (-1.0, 0, 1.0):
            k.limb(ft, (xx + t * 0.8, 0.8, 1.4), (xx + t * 1.6, 0.4, 4.4), 0.8, "horn", "talon")
            k.shard(ft, (xx + t * 1.6, 0.4, 4.4), (0, -1, 0.4), 1.2, 0.6, mat="horn", tag="foot")
        k.limb(ft, (xx, 0.8, -0.6), (xx, 0.4, -3.0), 0.8, "horn", "back_talon")
    to = k.part("torso", (0, 15, 0), (("x", 24),), "hips")
    k.stack(to, 0, 0, [(15, 9.6, 7.4), (20, 10.4, 7.6), (24, 12.0, 8.0), (27, 10.6, 7.4)], "feather", "body")
    k.blob(to, (0, 26.6, 0), (5.4, 1.8, 4.4), "whitef", "ruff", step=0.6)
    hd = k.part("head", (0, 27, 1.0), (("x", -30),), "torso")
    k.ring(hd, 0, 27.6, 1.6, 2.8, 1.2, "bronze", "collar", n=12, axis="y")
    k.limb(hd, (0, 27.6, 1.6), (0, 31.0, 3.0), 2.4, "skin", "bare_neck")
    k.box(hd, C(0, 30.4, 3.6, 4.2, 3.6, 4.6), "skin", tag="vulture_head")
    k.box(hd, C(0, 33.0, 3.6, 3.6, 1.2, 4.0), "feather", tag="crown_tuft")
    k.shard(hd, (0, 31.4, 5.8), (0, -0.4, 1), 3.4, 2.0, mat="horn", tag="beak")
    k.shard(hd, (0, 30.4, 8.6), (0, -1, 0.1), 1.2, 1.0, mat="horn", tag="beak_hook")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.15, 31.6, 4.6, 0.3, 0.9, 1.1), "eye", tag="eye")
    # wings for arms
    arms(k, to, 6.0, 25, "feather", {1: ((("x", -30), ("z", 40)), (("x", -20), ("z", 20))), -1: ((("x", -30), ("z", -40)), (("x", -20), ("z", -20)))}, w=2.4, long=1.1)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.0
        for part, (y0, y1), n in ((k.parts["arm_" + nm], (25.0, 16.6), 4), (k.parts["fore_" + nm], (16.4, 9.0), 5)):
            for i in range(n):
                y = y0 + (y1 - y0) * (i + 0.5) / n
                L = 7.0 + i * 1.6 if part is k.parts["fore_" + nm] else 5.0 + i
                k.box(part, C(x + side * 1.2, y - 0.6, -L + 1.0, 0.8, 1.8, L), "feather" if i % 2 else "whitef", tag="wing_feather")
        k.box(k.parts["hand_" + nm], C(x, 4.6, 0.4, 1.6, 2.0, 1.6), "horn", tag="wing_claw")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Hoplite (guard)

def hoplite():
    """The legion's line: a Corinthian helm closed over the face under a tall blue horsehair crest, a bronze cuirass
    beaten into the shape of the muscles under it, a skirt of leather strips, greaves, a blue cloak, the great round
    aspis with the legion's sun on it, and a spear twice as tall as a man."""
    k = X.Kit("hoplite")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(14, 10.8, 7.6), (20, 11.0, 7.8)], "blue", "chiton")
    pteruges(k, hips, 20.0, 11.4, 8.4, n=10)
    legs(k, hips, 19, 10.4, 3.2, "skin", "bronze", knee_mat="bronze", lean=-6, bend=8, w=4.8, cuff=False)
    for side in (1, -1):                          # sandals under the greaves
        k.box(k.parts["foot_" + ("l" if side > 0 else "r")], C(side * 3.2, 0, 1.4, 5.0, 1.0, 7.4), "leather", tag="foot")
    to = k.part("torso", (0, 20, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(20, 11.0, 7.8), (25, 12.4, 8.4), (29.6, 14.6, 9.0), (33, 14.4, 8.6)], "bronze", "cuirass")
    for sx in (-1, 1):                            # the muscles beaten into it
        k.blob(to, (sx * 2.6, 28.4, 3.8), (2.6, 1.8, 0.8), "bronze", "pec", step=0.6)
        for y in (22.0, 24.4):
            k.box(to, C(sx * 1.4, y, 4.0, 2.2, 1.6, 0.6), "bronze", tag="abs")
    k.box(to, C(0, 20.4, 4.2, 0.4, 9.0, 0.4), "gold", tag="center_line")
    for sx in (-1, 1):
        k.box(to, C(sx * 6.8, 31.4, 0, 3.6, 1.6, 8.8), "bronze", tag="shoulder_guard")
    cl = k.part("cloak", (0, 33, -4.4), (("x", 6),), to, bone=False)
    k.box(cl, C(0, 12.0, -4.8, 12.0, 21.0, 0.8), "blue", tag="cloak")
    k.box(cl, C(0, 32.4, -4.6, 13.0, 1.6, 1.2), "blue", tag="cloak_roll")
    hd = k.part("head", (0, 33, 0.6), (("x", -4),), "torso")
    corinthian(k, hd, (0, 35.0, 0.6))
    arms(k, to, 7.6, 31, "skin", {1: ((("x", -40), ("z", -10)), (("x", -40),)), -1: ((("x", -60), ("z", 6)), (("x", -30),))}, w=3.4)
    for side in (1, -1):
        k.box(k.parts["fore_" + ("l" if side > 0 else "r")], C(side * 7.6, 17.0, 0, 3.8, 4.0, 3.8), "bronze", tag="bracer")
    sh = held(k, "aspis", "l", (7.6, 13.0, 0.4), (("x", 80),))      # faces front: turned back against the forearm's lift
    for i, (r, t) in enumerate(((9.4, 1.0), (8.6, 1.2), (7.6, 0.6))):
        k.box(sh, C(6.4, 13.0 - r, 3.0 + i * 0.7, r * 2, r * 2, t), "bronze" if i != 2 else "blue", tag="aspis")
    k.ring(sh, 6.4, 13.0, 3.6, 9.0, 0.8, "gold", "aspis_rim", n=20, axis="z")
    sun_disc(k, sh, (6.4, 13.0, 4.8), 8.0, axis="z")
    sp = held(k, "dory", "r", (-7.6, 14.4, 0.4), (("x", 100),))
    k.limb(sp, (-7.6, -16.0, 0.4), (-7.6, 34.0, 0.4), 1.3, "leather", "dory_shaft")
    k.box(sp, C(-7.6, 4.0, 0.4, 1.8, 3.0, 1.8), "leather", tag="grip_wrap")
    k.shard(sp, (-7.6, 34.0, 0.4), (0, 1, 0), 7.0, 2.6, mat="bronze", tag="dory_head")
    k.box(sp, C(-7.6, 33.0, 0.4, 1.8, 1.6, 1.8), "gold", tag="dory_socket")
    k.shard(sp, (-7.6, -16.0, 0.4), (0, -1, 0), 3.0, 1.4, mat="bronze", tag="sauroter")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Talos (brute)

def talos():
    """The smith-god made the legion's giants out of bronze and filled them with ichor, the gods' own blood, that
    runs in one vein from the neck to the heel. Seamed bronze plates over a body like a statue's, a face as calm and
    blank as a mask, eyes of the sun, the vein glowing down its body, and fists that end the argument."""
    k = X.Kit("talos")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(13, 14.0, 9.6), (21, 15.0, 10.0)], "bronze", "hips")
    for i, x in enumerate((-4.4, 0, 4.4)):
        k.box(hips, C(x, 12.4, 4.8, 3.6, 7.0, 0.8), "bronze", tag="kilt_plate")
        k.box(hips, C(x, 12.4, 5.25, 3.8, 0.6, 0.4), "gold", tag="kilt_edge")
    legs(k, hips, 20, 11.0, 4.6, "bronze", "bronze", knee_mat="gold", lean=-4, bend=6, w=6.6, cuff=False)
    to = k.part("torso", (0, 21, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(21, 15.0, 10.0), (26, 17.4, 11.0), (31, 21.6, 12.0), (35, 22.4, 11.6), (37.4, 16.0, 9.4)], "bronze", "body")
    for sx in (-1, 1):
        k.blob(to, (sx * 4.0, 31.6, 4.8), (3.8, 2.6, 1.2), "bronze", "pec", step=0.7)
        for y in (23.0, 26.0):
            k.box(to, C(sx * 2.2, y, 5.1, 3.4, 2.4, 0.6), "bronze", tag="abs")
        k.blob(to, (sx * 12.0, 35.0, 0), (4.4, 3.4, 5.0), "bronze", "shoulder", step=0.7)
    for y in (24.6, 29.4, 34.0):                  # the seams between the plates
        k.box(to, C(0, y, 5.6, 14.0, 0.4, 0.3), "dark", tag="seam")
    # the vein: a line of ichor down from the neck, across the body, down the right leg to the heel
    k.limb(to, (1.6, 37.0, 5.0), (3.0, 30.0, 5.9), 0.9, "ichor", "vein", d=0.5)
    k.limb(to, (3.0, 30.0, 5.9), (2.6, 21.6, 5.4), 0.9, "ichor", "vein", d=0.5)
    k.limb(k.parts["thigh_l"], (4.6, 20.0, 3.6), (4.6, 11.4, 3.6), 0.9, "ichor", "vein", d=0.5)
    k.limb(k.parts["shin_l"], (4.6, 10.6, 3.6), (4.6, 2.6, -2.6), 0.9, "ichor", "vein", d=0.5)
    k.box(k.parts["foot_l"], C(4.6, 0.4, -3.4, 2.0, 2.0, 1.0), "gold", tag="heel_plug")     # where it can be let out
    hd = k.part("head", (0, 37.0, 1.0), (("x", -4),), "torso")
    k.box(hd, C(0, 37.4, 1.4, 7.0, 8.4, 7.0), "bronze", tag="head")
    k.box(hd, C(0, 37.8, 4.9, 5.6, 7.0, 0.6), "bronze", tag="face_mask")
    k.box(hd, C(0, 42.8, 5.3, 6.0, 0.8, 0.5), "bronze", tag="brow")
    k.box(hd, C(0, 39.6, 5.4, 1.0, 2.6, 0.6), "bronze", tag="nose")
    eyes(k, hd, 41.4, 5.45, 1.5, 1.4, h=0.6)
    k.box(hd, C(0, 38.6, 5.45, 2.2, 0.3, 0.3), "dark", tag="mouth_line")
    for i in range(7):                            # a crown of short bronze rays
        a = math.radians(-60 + i * 20)
        k.shard(hd, (math.sin(a) * 3.0, 45.6, 1.4 + math.cos(a) * 2.6), (math.sin(a) * 0.4, 1, math.cos(a) * 0.3), 2.6 if i % 2 else 3.6, 1.0, mat="gold", tag="ray_crown")
    arms(k, to, 12.6, 34, "bronze", {1: ((("x", -20), ("z", -14)), (("x", -40),)), -1: ((("x", -40), ("z", 12)), (("x", -30),))}, w=6.2, long=1.15)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        for b in list(k.s.boxes):
            if b.part is k.parts["hand_" + nm]:
                k.s.boxes.remove(b)
        y = 34 - 8 * 1.15 - 7.6 * 1.15
        k.box(k.parts["hand_" + nm], C(side * 12.6, y - 6.4, 0.4, 7.6, 6.4, 7.6), "bronze", tag="fist")
        for t in (-2.4, -0.8, 0.8, 2.4):
            k.box(k.parts["hand_" + nm], C(side * 12.6 + t, y - 6.0, 3.9, 1.4, 1.6, 0.6), "dark", tag="knuckle_seam")
        k.box(k.parts["fore_" + nm], C(side * 12.6, y + 1.0, 0, 7.0, 2.0, 7.0), "gold", tag="wrist_band")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.35)
    return k.s, k.parts


# ================================================================ the Oracle (caster)

def oracle():
    """The seers of the legion see without eyes: a woman pale as marble in long blue and white robes, a band of gold
    tied over her eyes, a crown of laurel, the smoke of the sacred vapours always round her, and a staff topped by
    the sun's disc that she points where the legion should go."""
    k = X.Kit("oracle")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(1, 13.0, 11.0), (9, 11.6, 9.4), (20, 10.4, 7.8)], "marble", "peplos", step=1.0)
    for x in (-3.6, -1.2, 1.2, 3.6):              # the pleats
        k.box(hips, C(x, 1.0, 5.2 - abs(x) * 0.25, 0.6, 18.0, 0.4), "dark", tag="pleat")
    k.box(hips, C(0, 1.0, 0, 13.6, 1.6, 11.6), "blue", tag="hem")
    for side, nm in ((1, "l"), (-1, "r")):
        th = k.part("thigh_" + nm, (side * 3.0, 19, 0), (), hips)
        sh = k.part("shin_" + nm, (side * 3.0, 10.4, 0), (), th)
        ft = k.part("foot_" + nm, (side * 3.0, 2.4, 0), (), sh)
        k.box(ft, C(side * 3.0, 0, 3.4, 3.4, 1.4, 3.4), "marble", tag="foot")
    to = k.part("torso", (0, 20, 0), (("x", 2),), "hips")
    k.stack(to, 0, 0, [(20, 10.4, 7.8), (25, 10.6, 7.6), (30, 12.0, 8.0), (33.4, 11.0, 7.4)], "marble", "chiton")
    k.limb(to, (5.4, 33.0, 0), (-5.0, 20.4, 4.0), 3.4, "blue", "himation", d=1.0)
    k.box(to, C(0, 19.6, 0, 11.0, 1.4, 8.4), "gold", tag="girdle")
    hd = k.part("head", (0, 33.4, 0.6), (("x", 6),), "torso")
    k.box(hd, C(0, 33.6, 0.6, 5.6, 7.0, 5.6), "marble", tag="face")
    k.box(hd, C(0, 37.0, 3.45, 6.0, 1.6, 0.5), "gold", tag="blindfold")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.4, 37.2, 3.75, 1.2, 1.0, 0.3), "eye", tag="eye")     # the light through the gold
    k.box(hd, C(0, 34.4, 3.45, 1.4, 0.4, 0.3), "dark", tag="mouth")
    k.blob(hd, (0, 39.0, 0.0), (3.4, 2.0, 3.6), "dark", "hair", step=0.6)
    k.box(hd, C(0, 30.0, -2.6, 5.0, 8.0, 1.6), "dark", tag="hair_fall")
    for i in range(12):                           # the laurel
        a = i * 2 * math.pi / 12
        k.box(hd, C(math.sin(a) * 3.4, 38.6 + (i % 2) * 0.4, 0.6 + math.cos(a) * 3.4, 1.4, 0.7, 1.0), "gold", tag="laurel")
    arms(k, to, 6.6, 31, "marble", {1: ((("x", -20), ("z", -10)), (("x", -40),)), -1: ((("x", -110), ("z", 4)), (("x", 0),))}, w=3.0)
    for side in (1, -1):
        k.box(k.parts["fore_" + ("l" if side > 0 else "r")], C(side * 6.6, 16.6, 0, 3.4, 1.0, 3.4), "gold", tag="armlet")
    st = held(k, "staff", "r", (-6.6, 14.6, 0.4), (("x", 110),))
    k.limb(st, (-6.6, -4.0, 0.4), (-6.6, 26.0, 0.4), 1.2, "bronze", "staff")
    k.box(st, C(-6.6, 25.6, 0.4, 2.0, 1.2, 2.0), "gold", tag="staff_cap")
    sun_disc(k, st, (-6.6, 31.0, 0.4), 6.0, axis="z")
    for i in range(6):                            # the vapours round her
        a = i * 1.1
        k.blob(hips, (math.cos(a) * 7.4, 2.4 + (i % 3) * 2.0, math.sin(a) * 6.4), (2.0, 1.4, 2.0), "smoke", "vapour", step=0.6)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Peltast (skirmisher)

def peltast():
    """The light troops run in, throw, and run out again: a Thracian helm with its crest curling forward like a
    Phrygian cap and cheek-guards painted with eyes, a short tunic, a cloak knotted at the shoulder, the crescent
    pelta on the left arm and javelins - one in hand, five in the quiver on the back."""
    k = X.Kit("peltast")
    hips = k.part("hips", (0, 19, 0))
    k.stack(hips, 0, 0, [(13, 10.4, 7.4), (19, 10.4, 7.4)], "blue", "tunic")
    k.box(hips, C(0, 18.0, 0, 11.2, 1.4, 8.2), "leather", tag="belt")
    legs(k, hips, 18, 9.8, 3.0, "skin", "leather", knee_mat=None, lean=-12, bend=20, w=4.4, cuff=True)
    to = k.part("torso", (0, 19, 0), (("x", 16),), "hips")
    k.stack(to, 0, 0, [(19, 10.4, 7.4), (24, 11.0, 7.6), (28.6, 12.6, 8.0), (32, 12.0, 7.6)], "blue", "tunic")
    k.box(to, C(0, 21.0, 3.9, 9.4, 9.0, 0.6), "leather", tag="linothorax")
    k.limb(to, (-6.0, 32.0, 0), (4.0, 20.0, 4.4), 1.4, "leather", "quiver_strap")
    k.box(to, C(1.0, 19.0, -5.4, 3.4, 13.0, 3.0), "leather", tag="quiver")
    for i in range(5):
        k.limb(to, (-0.4 + i * 0.7, 30.0, -5.4), (-1.0 + i * 1.2, 38.0, -6.6), 0.7, "leather", "javelin")
        k.shard(to, (-1.0 + i * 1.2, 38.0, -6.6), (0, 1, -0.1), 1.6, 0.7, mat="bronze", tag="javelin_tip")
    k.box(to, C(-6.4, 18.0, -3.6, 1.4, 14.0, 6.0), "blue", tag="cloak")
    k.box(to, C(-5.8, 30.6, 2.4, 2.0, 2.0, 0.8), "gold", tag="fibula")
    hd = k.part("head", (0, 32, 0.6), (("x", -14),), "torso")
    k.box(hd, C(0, 32.4, 0.8, 5.6, 6.4, 5.6), "skin", tag="face")
    eyes(k, hd, 35.4, 3.65, 1.3, 1.2)
    # the Thracian helm: a tall cap whose top curls forward into a crest
    k.blob(hd, (0, 37.8, 0.4), (3.4, 2.6, 3.6), "bronze", "helm", step=0.6)
    pts = [(0, 39.4, -0.6), (0, 42.4, -0.2), (0, 44.0, 1.6), (0, 43.4, 4.0), (0, 41.6, 5.0)]
    for (a, b), w in zip(zip(pts, pts[1:]), (3.6, 3.0, 2.4, 1.8)):
        k.limb(hd, a, b, w, "bronze", "phrygian_crest", d=w * 0.8)
    for sx in (-1, 1):
        k.box(hd, C(sx * 3.2, 31.4, 1.4, 0.8, 4.4, 4.0), "bronze", tag="cheek_guard")
        k.box(hd, C(sx * 3.65, 33.0, 2.0, 0.3, 1.0, 1.6), "blue", tag="painted_eye")
    k.box(hd, C(0, 36.2, 3.7, 6.2, 0.6, 0.4), "gold", tag="brow_line")
    arms(k, to, 6.8, 30, "skin", {1: ((("x", -50), ("z", -6)), (("x", -40),)), -1: ((("x", -170), ("z", 10)), (("x", -10),))}, w=3.2)
    sh = held(k, "pelta", "l", (6.8, 12.0, 0.4), (("x", 90),))
    for i in range(5):                            # the crescent: a disc with a bite out of the top, two horns
        y = 4.0 + i * 1.6
        w = 11.0 - abs(i - 2) * 1.8
        k.box(sh, C(6.8, y, 2.6, w, 1.65, 0.8), "leather", tag="pelta")
    for sx in (-1, 1):
        k.box(sh, C(6.8 + sx * 4.0, 12.0, 2.6, 2.4, 3.2, 0.8), "leather", tag="pelta_horn")
        k.shard(sh, (6.8 + sx * 4.4, 15.0, 2.6), (sx * 0.4, 1, 0), 2.0, 1.4, mat="leather", tag="pelta_horn")
    k.box(sh, C(6.8, 6.4, 3.1, 4.0, 4.0, 0.4), "bronze", tag="pelta_boss")
    jv = held(k, "javelin", "r", (-6.8, 14.4, 0.3), (("x", 160),))
    k.limb(jv, (-6.8, 4.0, 0.3), (-6.8, 30.0, 0.3), 1.0, "leather", "javelin")
    k.shard(jv, (-6.8, 30.0, 0.3), (0, 1, 0), 3.4, 1.2, mat="bronze", tag="javelin_tip")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Gryphon Rider (elite)

def gryphon_rider():
    """The legion's champions ride gryphons: an eagle's head with a hooked gold beak, a ruff of white feathers, a
    lion's body the colour of sand, the great wings folded half-open along its back - and on it, in a gold-edged
    saddle, a champion in a crested helm and a blue cloak, a lance couched and the aspis on his arm."""
    k = X.Kit("gryphon_rider")
    body, hd, ab, joints = quad(k, "lion", y=17, chest=((9, 13, 15), (15, 16, 17), (22, 14, 15)), haunch=((9, 12, 12), (15, 14, 13), (21, 12, 12)),
                                leg_w=4.4, foot_w=3.4, front_z=7, back_z=-10, x=5.4, head_at=(0, 22, 11), head_rot=-14, claw="horn", foot_len=5.4)
    # the front legs are an eagle's: scaled, talons
    for s in ("l", "r"):
        lg = k.parts["leg_%s0" % s]
        for b in list(k.s.boxes):
            if b.part is lg and b.tag in ("leg", "foot"):
                b.mat = "horn" if b.tag == "foot" else "whitef"
    k.blob(body, (0, 21.0, 7.0), (7.4, 5.4, 5.4), "whitef", "ruff", step=0.8)
    k.box(body, C(0, 10.0, 1.0, 12.0, 1.4, 14.0), "lion", tag="belly")
    tail = [(0, 18, -16), (0, 15, -22), (0, 13, -27), (0, 14, -31)]
    for (a, b), w in zip(zip(tail, tail[1:]), (2.4, 2.0, 1.6)):
        k.limb(ab, a, b, w, "lion", "tail")
    k.blob(ab, (0, 14.6, -32.0), (2.0, 2.0, 2.4), "lion", "tail_tuft", step=0.6)
    # the wings, half-open, along its back
    for side in (1, -1):
        wing(k, body, (side * 6.0, 23.0, 3.0), side, 20.0, "lion", membrane="whitef", ribs=5, up=0.55, back=0.9, drop=10.0)
    # the eagle head
    k.box(hd, C(0, 20.6, 15.0, 7.0, 7.4, 7.4), "whitef", tag="head")
    k.box(hd, C(0, 26.0, 13.8, 6.0, 1.8, 6.0), "whitef", tag="crown_feathers")
    k.shard(hd, (0, 23.4, 18.4), (0, -0.4, 1), 4.4, 3.0, mat="gold", tag="beak")
    k.shard(hd, (0, 21.6, 22.0), (0, -1, 0.1), 2.0, 1.6, mat="gold", tag="beak_hook")
    for sx in (-1, 1):
        k.box(hd, C(sx * 3.55, 24.0, 16.8, 0.3, 1.2, 1.8), "eye", tag="eye")
        k.limb(hd, (sx * 2.6, 25.6, 15.4), (sx * 3.6, 27.0, 11.0), 1.2, "whitef", "ear_tuft")
    # the saddle and the champion
    k.box(body, C(0, 23.0, -1.0, 9.0, 2.0, 11.0), "leather", tag="saddle")
    k.box(body, C(0, 23.4, -1.0, 9.6, 0.8, 11.6), "gold", tag="saddle_edge")
    k.box(body, C(0, 25.0, 4.0, 5.0, 2.4, 1.6), "leather", tag="pommel")
    k.box(body, C(0, 13.4, -1.0, 13.4, 9.8, 9.0), "blue", tag="saddle_cloth")
    k.stack(body, 0, -1.6, [(25.0, 8.0, 6.0), (27.6, 8.4, 6.0)], "blue", "rider_hips")
    for sx in (-1, 1):
        k.limb(body, (sx * 3.4, 26.4, -0.4), (sx * 8.4, 21.0, 2.4), 2.6, "skin", "rider_thigh")
        k.limb(body, (sx * 8.4, 21.0, 2.4), (sx * 8.6, 14.4, 0.6), 2.2, "bronze", "rider_greave")
        k.box(body, C(sx * 8.6, 13.0, 1.2, 2.6, 1.6, 3.8), "leather", tag="rider_foot")
    k.stack(body, 0, -1.4, [(27.6, 8.4, 6.0), (32, 9.6, 6.4), (36, 11.4, 6.8), (38.4, 10.4, 6.4)], "bronze", "rider_cuirass")
    for sx in (-1, 1):
        k.blob(body, (sx * 1.8, 34.4, 1.8), (1.8, 1.4, 0.6), "bronze", "rider_pec", step=0.5)
    cl = k.part("rider_cloak", (0, 38, -4.6), (("x", 40),), body, bone=False)
    k.box(cl, C(0, 22.0, -5.0, 11.0, 16.0, 0.8), "blue", tag="rider_cloak")
    corinthian(k, body, (0, 40.0, -1.0), 0.85)
    k.limb(body, (5.6, 37.0, -1.4), (7.4, 31.0, 2.4), 2.4, "skin", "rider_arm")
    k.limb(body, (-5.6, 37.0, -1.4), (-7.4, 31.0, 1.6), 2.4, "skin", "rider_arm")
    for i, (r, t) in enumerate(((6.4, 0.8), (5.6, 1.0))):     # the aspis on his left arm
        k.box(body, C(9.0 + i * 0.6, 31.0 - r, 1.6, t, r * 2, r * 2), "bronze", tag="rider_aspis")
    sun_disc(k, body, (10.4, 31.0, 1.6), 5.4, axis="x")
    k.limb(body, (-7.4, 30.4, -6.0), (-7.0, 33.6, 30.0), 1.4, "leather", "lance")       # the lance, couched forward
    k.shard(body, (-7.0, 33.6, 30.0), (0.0, 0.08, 1), 6.0, 2.0, mat="bronze", tag="lance_head")
    k.box(body, C(-7.2, 31.6, 12.0, 0.4, 3.0, 4.0), "blue", tag="pennon")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


MOBS = {
    "harpy": dict(make=harpy, ent=(0.9, 2.2), stats=dict(hp=26, speed=0.36, dmg=6, armor=2, kb=0)),
    "hoplite": dict(make=hoplite, ent=(0.9, 3.0), stats=dict(hp=62, speed=0.24, dmg=10, armor=10, kb=0.4)),
    "talos": dict(make=talos, ent=(1.8, 4.2), stats=dict(hp=210, speed=0.18, dmg=19, armor=14, kb=1.0)),
    "oracle": dict(make=oracle, ent=(0.9, 2.8), stats=dict(hp=36, speed=0.22, dmg=7, armor=2, kb=0)),
    "peltast": dict(make=peltast, ent=(0.8, 2.7), stats=dict(hp=40, speed=0.34, dmg=8, armor=3, kb=0)),
    "gryphon_rider": dict(make=gryphon_rider, rig="crawler", ent=(2.2, 3.4), stats=dict(hp=320, speed=0.38, dmg=15, armor=11, kb=0.7), key=True),
}
