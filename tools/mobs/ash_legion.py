"""The Ash Legion: a legion that marched into the nether to conquer it and was burned down to the bone, still marching,
who hold the nether's fortresses, keeps, ports, towers, camps and arenas, built by hand (tools/vox2.py). Bones gone
ash-grey and black, basalt, bronze blackened in the heat, crimson cloth scorched to rags, and the warped-teal fire
of the nether's cold side burning in their skulls and their wounds. (Not the forge's orange fire: these burn teal.)

    ash_salamander  swarm   a lizard of ash and bone as long as a man, teal fire running down its spine
    ash_legionary   guard   a burned legionary: a crested galea with teal fire for its crest, segmented plate, a
                            curved scutum and a gladius
    basalt_brute    brute   a giant of basalt columns split with teal fire, a basalt pillar for a hammer
    ash_augur       caster  the legion's augur: a laurel of ash, a scorched toga, a staff with a skull-cage brazier
    ash_lictor      skirm   the magistrate's lictor: a bundle of rods with an axe in it in each hand, a chain belt
    ash_centurion   elite   the centurion: a transverse crest of fire, a phalera-hung harness over black bronze, a
                            crimson cloak in rags, a spatha burning teal

    python tools/monsterforge.py ash_legion --preview ; python tools/mobsheet.py ash_legion
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import grow
from _folk import lit, eyes, legs, arms, held, quad

ASH = ramp("#1a1a1a", "#2c2a28", "#403c38", "#56524c", "#6e6862", "#88827a")
BASALT = ramp("#06060a", "#0c0c12", "#14141c", "#1c1c26", "#262632", "#323240")
BRONZE = ramp("#0e0a06", "#1a120a", "#28190e", "#382214", "#4a2e1a", "#5e3c22")
CRIMSON = ramp("#140406", "#24080a", "#380c0e", "#4e1214", "#661a1a")
LEATHER = ramp("#0c0806", "#16100c", "#201810", "#2c2016")
STEEL = ramp("#1a1c1e", "#2c3034", "#40464c", "#585e66", "#727a84")
TEAL = ramp("#023a34", "#046a5a", "#0aa088", "#20d4b8", "#7af0de", "#d0fff6")


def shaders():
    return {
        "ash": X.surf(ASH, 0.52, 1.2, 0.18, 0.12, drip=(BASALT, 0.16)),
        "basalt": X.veined(BASALT, TEAL, 0.22, 0.016),
        "bronze": X.surf(BRONZE, 0.54, 1.5, 0.12, 0.26, rust=(BASALT, 0.24, 0.6)),
        "crimson": X.surf(CRIMSON, 0.5, 1.0, 0.22, 0.0, holes=True, drip=(BASALT, 0.2)),
        "leather": X.surf(LEATHER, 0.5, 1.1, 0.2, 0.04),
        "steel": X.surf(STEEL, 0.62, 1.6, 0.06, 0.3),
        "bone": X.surf(ASH, 0.6, 1.3, 0.14, 0.14),
        "teal": X.glow(TEAL),
        "eye": X.glow(TEAL, 0.86, 0.12),
        "dark": X.dark(BASALT),
    }


GLOWS = {"teal", "eye"}


def flame(k, part, base, n, L, up=(0, 1, 0), seed=1, spread=0.5):
    """teal fire licking up off something"""
    k.cluster(part, base, n, L, L * 0.36, mat="teal", seed=seed, spread=spread, up=up)


def ash_skull(k, part, c, s=1.0):
    cx, cy, cz = c
    k.blob(part, (cx, cy + 1.2 * s, cz), (2.8 * s, 3.0 * s, 3.0 * s), "bone", "cranium", step=0.6)
    k.box(part, C(cx, cy - 1.6 * s, cz + 0.6 * s, 4.2 * s, 2.4 * s, 4.0 * s), "bone", tag="cheeks")
    for sx in (-1, 1):
        k.box(part, C(cx + sx * 1.2 * s, cy - 0.2 * s, cz + 2.5 * s, 1.5 * s, 1.5 * s, 0.4), "dark", tag="socket")
        k.box(part, C(cx + sx * 1.2 * s, cy + 0.1 * s, cz + 2.6 * s, 0.8 * s, 0.8 * s, 0.3), "eye", tag="eye")
    k.box(part, C(cx, cy - 3.4 * s, cz + 0.8 * s, 3.6 * s, 1.4 * s, 3.4 * s), "bone", tag="jaw")
    for i in range(5):
        k.box(part, C(cx - 1.6 * s + i * 0.8 * s, cy - 2.2 * s, cz + 2.55 * s, 0.5 * s, 0.9 * s, 0.3), "bone", tag="teeth")


def galea(k, part, c, s=1.0, transverse=False):
    """the legion's helm: a bowl, a neck guard, hinged cheek guards, a crest of teal fire"""
    cx, cy, cz = c
    k.blob(part, (cx, cy + 1.6 * s, cz), (3.6 * s, 2.8 * s, 3.8 * s), "bronze", "galea", step=0.6)
    k.box(part, C(cx, cy - 1.0 * s, cz - 3.4 * s, 7.6 * s, 1.6 * s, 2.4 * s), "bronze", tag="neck_guard")
    for sx in (-1, 1):
        k.box(part, C(cx + sx * 3.4 * s, cy - 3.6 * s, cz + 1.0 * s, 0.8, 4.4 * s, 3.4 * s), "bronze", tag="cheek_guard")
    k.box(part, C(cx, cy + 0.2 * s, cz + 3.6 * s, 7.0 * s, 0.6, 0.6), "bronze", tag="brow_ridge")
    if transverse:                                # side to side, the centurion's
        k.box(part, C(cx, cy + 3.8 * s, cz, 9.0 * s, 1.0, 1.4 * s), "bronze", tag="crest_holder")
        for i in range(9):
            x = cx - 4.0 * s + i * 1.0 * s
            k.shard(part, (x, cy + 4.6 * s, cz), (0, 1, 0), (3.6 + (4 - abs(i - 4)) * 0.7) * s, 1.2 * s, mat="teal", tag="fire_crest")
    else:
        k.box(part, C(cx, cy + 3.8 * s, cz, 1.2 * s, 1.0, 7.0 * s), "bronze", tag="crest_holder")
        for i in range(7):
            z = cz + 3.0 * s - i * 1.0 * s
            k.shard(part, (cx, cy + 4.6 * s, z), (0, 1, -0.3), (3.0 + (3 - abs(i - 3)) * 0.6) * s, 1.1 * s, mat="teal", tag="fire_crest")


def segmentata(k, part, y0, y1, w, d):
    """the bands of the lorica, overlapping"""
    y = y0
    i = 0
    while y < y1:
        k.box(part, C(0, y, 0, w + (i % 2) * 0.4, 1.8, d + (i % 2) * 0.4), "bronze", tag="lorica_band")
        y += 1.6
        i += 1


# ================================================================ the Ash Salamander (swarm)

def ash_salamander():
    """What lives in the ash drifts of the legion's camps: a lizard as long as a man, its hide gone to ash over the
    bones, a crest of teal fire running from its skull to the end of its tail, its mouth full of the same fire."""
    k = X.Kit("ash_salamander")
    body, hd, ab, joints = quad(k, "ash", y=6, chest=((2, 7, 9), (5, 8, 10), (7.4, 6.6, 8)), haunch=((2, 6.4, 8), (5, 7.4, 9), (7, 6.0, 7)),
                                leg_w=2.0, foot_w=1.6, front_z=4, back_z=-6, x=5.0, head_at=(0, 6, 8), head_rot=-4, claw="bone", foot_len=3.4,
                                knees=(-1.0, 1.0))
    tail = [(0, 5.6, -10), (0, 5.0, -15), (1.6, 4.0, -20), (3.4, 3.0, -24), (4.2, 2.4, -27)]
    for (a, b), w in zip(zip(tail, tail[1:]), (5.0, 4.0, 3.0, 2.0)):
        k.limb(ab, a, b, w, "ash", "tail", d=w * 0.8)
    for i, z in enumerate((6, 3, 0, -3, -6, -9, -12, -15)):          # the fire down its spine
        part = body if z > -3 else ab
        k.shard(part, (0, 8.6 - max(0, -z - 10) * 0.2, z), (0, 1, -0.3), 3.0 - abs(z + 3) * 0.08, 1.2, mat="teal", tag="spine_fire")
    for sx in (-1, 1):
        for z in (-1, 3):
            k.box(body, C(sx * 4.6, 4.0, z, 0.3, 2.0, 1.0), "bone", tag="rib_showing")
    k.box(hd, C(0, 3.6, 11.4, 7.0, 4.6, 7.0), "ash", tag="head")
    k.box(hd, C(0, 3.2, 15.6, 5.0, 2.6, 4.4), "ash", tag="snout")
    k.box(hd, C(0, 2.6, 15.0, 4.4, 0.8, 5.0), "teal", tag="mouth_fire")
    k.box(hd, C(0, 1.4, 14.0, 5.0, 1.4, 6.0), "bone", tag="jaw")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.6, 7.4, 13.6, 1.4, 0.8, 1.4), "eye", tag="eye")
        k.box(hd, C(sx * 2.6, 8.2, 12.6, 1.8, 0.6, 2.4), "bone", tag="brow_ridge")
    flame(k, hd, (0, 3.6, 19.0), 3, 2.6, up=(0, 0.2, 1), seed=4)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Ash Legionary (guard)

def ash_legionary():
    """The legion's ranks, burned to the bone and still in step: skulls in bronze galeae with crests of teal fire,
    the segmented plate gone black, crimson tunics scorched to rags, the great curved scutum with the legion's
    wings on it, and the short gladius for the work behind it."""
    k = X.Kit("ash_legionary")
    hips = k.part("hips", (0, 20, 0))
    k.box(hips, C(0, 17.4, 0, 6.0, 3.4, 4.0), "bone", tag="pelvis")
    k.stack(hips, 0, 0, [(13, 11.0, 8.0), (20, 10.6, 7.6)], "crimson", "tunic")
    for x in (-3.0, -1.0, 1.0, 3.0):              # the hanging straps of the cingulum
        k.box(hips, C(x, 10.0, 4.2, 1.2, 8.0, 0.6), "leather", tag="cingulum")
        k.box(hips, C(x, 10.0, 4.5, 1.4, 1.0, 0.4), "bronze", tag="strap_end")
    k.box(hips, C(0, 18.6, 0, 11.4, 1.8, 8.4), "leather", tag="belt")
    for side, nm in ((1, "l"), (-1, "r")):        # bone legs, greaves, caligae
        xx = side * 3.0
        th = k.part("thigh_" + nm, (xx, 19, 0), (("x", -6), ("z", side * 3)), hips)
        sh = k.part("shin_" + nm, (xx, 10.4, 0), (("x", 8),), th)
        ft = k.part("foot_" + nm, (xx, 2.4, 0), (("x", -2),), sh)
        k.limb(th, (xx, 19, 0), (xx, 11.0, 0), 2.6, "bone", "femur")
        k.box(th, C(xx, 9.8, 0.2, 3.6, 2.0, 3.6), "bone", tag="knee")
        k.limb(sh, (xx, 9.8, 0), (xx, 2.6, 0), 2.2, "bone", "shin")
        k.box(sh, C(xx, 3.0, 1.0, 3.6, 6.4, 2.6), "bronze", tag="greave")
        k.box(ft, C(xx, 0, 1.4, 4.0, 2.2, 6.4), "leather", tag="foot")
        for z in (0.0, 2.4):
            k.box(ft, C(xx, 1.4, z, 4.4, 0.6, 0.6), "leather", tag="sandal_strap")
    to = k.part("torso", (0, 20, 0), (("x", 4),), "hips")
    segmentata(k, to, 20.0, 31.0, 11.4, 8.0)
    k.stack(to, 0, 0, [(30.6, 13.6, 8.6), (33.4, 12.6, 8.0)], "bronze", "lorica_top")
    for sx in (-1, 1):
        for i in range(3):
            k.box(to, C(sx * 7.2, 31.6 - i * 1.4, 0, 3.6, 1.6, 8.0 - i * 0.4), "bronze", tag="shoulder_band")
    flame(k, to, (2.0, 26.0, 4.6), 2, 2.0, up=(0.2, 1, 0.6), seed=2)
    k.box(to, C(2.0, 25.0, 4.2, 2.0, 2.0, 0.4), "teal", tag="wound")
    hd = k.part("head", (0, 33.4, 0.6), (("x", -4),), "torso")
    ash_skull(k, hd, (0, 36.4, 0.8), 1.0)
    galea(k, hd, (0, 38.0, 0.6))
    arms(k, to, 7.4, 31, "bone", {1: ((("x", -40), ("z", -8)), (("x", -40),)), -1: ((("x", -30), ("z", 8)), (("x", -48),))}, w=2.6)
    for side in (1, -1):
        k.box(k.parts["fore_" + ("l" if side > 0 else "r")], C(side * 7.4, 17.0, 0, 3.4, 3.6, 3.4), "leather", tag="bracer")
    sh = held(k, "scutum", "l", (7.4, 13, 0.4), (("x", 80),))       # the curved scutum, the wings on it
    for i, (x, z) in enumerate(((-4.4, 2.0), (-2.2, 3.0), (0, 3.4), (2.2, 3.0), (4.4, 2.0))):
        k.box(sh, C(7.0 + x, 0.4, z, 2.3, 24.0, 1.0), "crimson", tag="scutum")
    for y in (0.0, 23.4):
        k.box(sh, C(7.0, y, 2.8, 11.6, 1.0, 1.8), "bronze", tag="scutum_rim")
    k.blob(sh, (7.0, 12.4, 4.0), (2.0, 2.0, 0.8), "bronze", "umbo", step=0.5)
    for sx in (-1, 1):                            # the wings either side of the boss
        for i in range(4):
            k.box(sh, C(7.0 + sx * (2.6 + i * 1.0), 13.0 + i * 1.0, 3.9 - abs(sx * (2.6 + i)) * 0.08, 1.0, 1.0 + i * 0.6, 0.3), "bronze", tag="wing_emblem")
        k.box(sh, C(7.0 + sx * 2.2, 5.0, 3.9, 0.6, 5.0, 0.3), "bronze", tag="lightning")
    gl = held(k, "gladius", "r", (-7.4, 14.0, 0.3), (("x", 84),))
    k.limb(gl, (-7.4, 10.0, 0.3), (-7.4, 14.6, 0.3), 1.2, "leather", "grip")
    k.blob(gl, (-7.4, 9.4, 0.3), (1.0, 0.8, 1.0), "bronze", "pommel", step=0.4)
    k.box(gl, C(-7.4, 14.6, 0.3, 1.2, 1.0, 2.8), "bronze", tag="guard")
    k.box(gl, C(-7.4, 15.6, 0.3, 0.8, 10.0, 2.4), "steel", tag="gladius_blade")
    k.shard(gl, (-7.4, 25.6, 0.3), (0, 1, 0), 3.0, 2.2, mat="steel", tag="blade_tip")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Basalt Brute (brute)

def basalt_brute():
    """The nether made its own giants for the legion out of the basalt deltas: a man's shape stacked out of black
    hexagonal columns, cracked through and through with teal fire, legion chains still round its neck from when they
    broke it in, and a basalt pillar for a hammer, its end bound in bronze."""
    k = X.Kit("basalt_brute")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(12, 15, 11), (21, 16, 11.6)], "basalt", "hips")
    legs(k, hips, 20, 11.0, 4.8, "basalt", "basalt", knee_mat=None, lean=-4, bend=6, w=7.0, cuff=False)
    to = k.part("torso", (0, 21, 0), (("x", 10),), "hips")
    # the body built of columns: tall hexagonal prisms side by side, uneven tops
    for i in range(7):
        x = -9.0 + i * 3.0
        top = 34.0 + ((i * 5) % 4) * 1.6 - abs(x) * 0.2
        k.box(to, C(x, 21.0, 0, 3.0, top - 21.0, 12.0 - abs(x) * 0.4), "basalt", tag="column")
        k.box(to, C(x, top, 0, 2.4, 1.0, 10.0 - abs(x) * 0.4), "ash", tag="column_top")
    for (x, y) in ((-4.6, 24.0), (1.6, 28.0), (4.6, 32.0), (-1.4, 33.0)):    # the cracks
        k.box(to, C(x, y, 6.1, 0.6, 4.0, 0.3), "teal", tag="crack")
    k.blob(to, (0, 29.0, 5.6), (2.4, 2.4, 1.0), "teal", "core_fire", step=0.6)
    for i in range(12):                           # the legion chain round its neck
        a = i * 2 * math.pi / 12
        k.box(to, C(math.cos(a) * 8.0, 35.6 + math.sin(a) * 0.8, math.sin(a) * 6.4, 1.8, 1.2, 1.2) if i % 2 else C(math.cos(a) * 8.0, 35.6, math.sin(a) * 6.4, 1.2, 1.4, 1.8), "bronze", tag="chain_collar")
    flame(k, to, (0, 36.0, -2.0), 5, 4.6, up=(0, 1, -0.4), seed=8)
    hd = k.part("head", (0, 37.0, 2.0), (("x", -10),), "torso")
    k.box(hd, C(0, 37.0, 2.6, 7.6, 8.0, 7.6), "basalt", tag="head")
    k.box(hd, C(0, 41.6, 6.4, 8.0, 1.4, 1.2), "basalt", tag="brow")
    k.box(hd, C(0, 39.8, 6.45, 5.0, 1.2, 0.3), "eye", tag="eye")
    k.box(hd, C(0, 37.0, 6.45, 3.4, 0.8, 0.3), "teal", tag="mouth_crack")
    k.box(hd, C(0, 45.0, 2.6, 3.0, 1.4, 6.4), "basalt", tag="head_column")
    arms(k, to, 13.0, 34, "basalt", {1: ((("x", -30), ("z", -14)), (("x", -40),)), -1: ((("x", -70), ("z", 18)), (("x", -30),))}, w=6.6, long=1.15)
    for side in (1, -1):
        k.box(k.parts["arm_" + ("l" if side > 0 else "r")], C(side * 13.0, 27.0, 3.4, 0.6, 3.6, 0.3), "teal", tag="crack")
    hm = held(k, "pillar", "r", (-13.0, 14.0, 0.4), (("x", 120), ("z", 16)))
    k.limb(hm, (-13.0, 2.0, 0.4), (-13.0, 20.0, 0.4), 3.4, "basalt", "pillar_shaft")
    k.box(hm, C(-13.0, 20.0, 0.4, 9.0, 12.0, 9.0), "basalt", tag="pillar_head")
    for y in (20.0, 30.6):
        k.box(hm, C(-13.0, y, 0.4, 9.8, 1.4, 9.8), "bronze", tag="pillar_band")
    k.box(hm, C(-13.0, 23.0, 4.95, 0.6, 6.0, 0.3), "teal", tag="crack")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.3)
    return k.s, k.parts


# ================================================================ the Ash Augur (caster)

def ash_augur():
    """The augurs read the omens that sent the legion in; they read them still, in the fire. A skull crowned with a
    laurel of ash, a toga scorched to the hem and draped crimson, bone hands, a staff topped with a cage of bronze
    with a skull burning teal inside it."""
    k = X.Kit("ash_augur")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(1, 13.0, 11.0), (10, 11.6, 9.4), (21, 10.4, 7.8)], "ash", "toga", step=1.0)
    k.box(hips, C(0, 1.0, 0, 13.6, 2.0, 11.6), "dark", tag="scorched_hem")
    for side, nm in ((1, "l"), (-1, "r")):
        th = k.part("thigh_" + nm, (side * 3.0, 20, 0), (), hips)
        sh = k.part("shin_" + nm, (side * 3.0, 11, 0), (), th)
        ft = k.part("foot_" + nm, (side * 3.0, 2.4, 0), (), sh)
        k.box(ft, C(side * 3.0, 0, 3.4, 3.4, 1.6, 4.4), "bone", tag="foot")
    to = k.part("torso", (0, 21, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(21, 10.4, 7.8), (26, 10.8, 7.8), (31, 12.0, 8.0), (34, 11.0, 7.4)], "ash", "toga")
    k.limb(to, (5.6, 33.6, 0), (-5.2, 18.0, 4.0), 3.4, "crimson", "toga_drape", d=1.0)       # the crimson drape across
    k.limb(to, (5.6, 33.6, 0), (6.0, 18.0, -3.0), 3.0, "crimson", "toga_drape", d=1.0)
    hd = k.part("head", (0, 34, 0.6), (("x", -4),), "torso")
    ash_skull(k, hd, (0, 37.4, 0.8), 1.0)
    for i in range(12):                           # the laurel of ash
        a = i * 2 * math.pi / 12
        k.box(hd, C(math.sin(a) * 3.0, 39.4 + (i % 2) * 0.4, 0.8 + math.cos(a) * 3.0, 1.4, 0.7, 1.0), "ash", tag="laurel")
    flame(k, hd, (0, 41.4, 0.6), 3, 2.6, seed=6)
    arms(k, to, 6.6, 32, "ash", {1: ((("x", -80), ("z", -16)), (("x", -20),)), -1: ((("x", -30), ("z", 10)), (("x", -40),))}, glove="bone", w=3.2)
    y = 32 - 8 - 7.6 - 2.8
    for t in (-0.8, 0, 0.8):
        k.limb(k.parts["hand_l"], (6.6 + t, y, 1.0), (6.6 + t * 1.6, y - 3.4, 2.4), 0.5, "bone", "finger")
    k.blob(k.parts["hand_l"], (6.6, y - 3.0, 4.4), (1.4, 1.6, 1.4), "teal", "omen_fire", step=0.5)
    st = held(k, "staff", "r", (-6.6, 14.4, 0.4), (("x", 70),))
    k.limb(st, (-6.6, -6.0, 0.4), (-6.6, 26.0, 0.4), 1.2, "bronze", "staff")
    for i in range(6):                            # the cage
        a = i * math.pi / 3
        k.limb(st, (-6.6, 26.0, 0.4), (-6.6 + math.cos(a) * 2.8, 29.0, 0.4 + math.sin(a) * 2.8), 0.5, "bronze", "cage_bar")
        k.limb(st, (-6.6 + math.cos(a) * 2.8, 29.0, 0.4 + math.sin(a) * 2.8), (-6.6, 33.0, 0.4), 0.5, "bronze", "cage_bar")
    ash_skull(k, st, (-6.6, 29.6, 0.4), 0.55)
    flame(k, st, (-6.6, 31.0, 0.4), 3, 2.4, seed=3)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Ash Lictor (skirmisher)

def ash_lictor():
    """The lictors walked before the magistrates with the fasces; in the nether they go first into everything. Lean
    and burned black, a hood of scorched crimson, a chain for a belt, and in each fist a fasces - a bundle of rods
    bound in bronze with an axe-head standing out of it - swung like a club and a blade at once."""
    k = X.Kit("ash_lictor")
    hips = k.part("hips", (0, 19, 0))
    k.box(hips, C(0, 16.6, 0, 6.0, 3.4, 4.0), "bone", tag="pelvis")
    k.stack(hips, 0, 0, [(12, 10.0, 7.4), (19, 10.0, 7.2)], "crimson", "tunic")
    for i in range(10):                           # the chain belt
        a = i * 2 * math.pi / 10
        k.box(hips, C(math.cos(a) * 5.4, 18.0, math.sin(a) * 4.0, 1.4, 1.0, 1.0), "bronze", tag="chain_belt")
    legs(k, hips, 18, 9.8, 3.0, "ash", "leather", knee_mat=None, lean=-12, bend=20, w=4.0, cuff=False)
    to = k.part("torso", (0, 19, 0), (("x", 20),), "hips")
    k.stack(to, 0, 0, [(19, 10.0, 7.2), (24, 10.6, 7.2), (28.6, 12.4, 7.8), (31.6, 11.6, 7.2)], "ash", "torso")
    for i in range(5):
        k.box(to, C(0, 21.0 + i * 1.8, 3.65, 7.0 - abs(i - 2) * 0.8, 0.6, 0.3), "dark", tag="rib_line")
    k.box(to, C(-1.4, 23.0, 3.7, 2.2, 3.0, 0.3), "teal", tag="wound")
    k.limb(to, (5.4, 31.0, 0), (-4.0, 20.0, 3.8), 2.4, "crimson", "sash", d=0.6)
    hd = k.part("head", (0, 31.6, 0.6), (("x", -14),), "torso")
    ash_skull(k, hd, (0, 34.6, 0.8), 0.95)
    k.blob(hd, (0, 36.6, -0.2), (3.8, 3.8, 4.0), "crimson", "hood", step=0.6)
    k.box(hd, C(0, 30.6, -1.4, 8.0, 3.4, 6.4), "crimson", tag="hood_drape")
    k.shard(hd, (0, 39.6, -1.6), (0, 0.4, -1), 3.4, 2.0, mat="crimson", tag="hood_point")
    arms(k, to, 6.6, 29, "ash", {1: ((("x", -20), ("z", 30)), (("x", -60),)), -1: ((("x", -70), ("z", -20)), (("x", -30),))}, glove="bone", w=2.8)
    for side, nm in ((1, "l"), (-1, "r")):        # the fasces
        x = side * 6.6
        fs = held(k, "fasces_" + nm, nm, (x, 11.6, 0.4), (("x", 70 if side > 0 else 40),))
        for i in range(6):
            a = i * math.pi / 3
            k.limb(fs, (x + math.cos(a) * 1.0, 6.0, 0.4 + math.sin(a) * 1.0), (x + math.cos(a) * 1.0, 22.0, 0.4 + math.sin(a) * 1.0), 0.8, "leather", "rod")
        for y in (8.0, 14.0, 20.0):
            k.box(fs, C(x, y, 0.4, 3.0, 1.0, 3.0), "bronze", tag="fasces_band")
        k.box(fs, C(x, 18.6, 3.0, 0.8, 5.0, 3.4), "steel", tag="axe_head")
        k.box(fs, C(x, 18.4, 4.6, 0.9, 5.4, 0.6), "steel", tag="axe_edge")
        k.shard(fs, (x, 22.0, 0.4), (0, 1, 0), 2.2, 1.6, mat="bronze", tag="fasces_cap")
        flame(k, fs, (x, 23.6, 0.4), 2, 2.0, seed=side + 10)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Ash Centurion (elite)

def ash_centurion():
    """The centurion carried the legion's standard into the nether and brought it nowhere. Bones black under bronze
    plate edged in teal fire, a harness hung with the phalerae of every victory, a galea with the centurion's
    transverse crest burning side to side, the crimson cloak scorched to a rag, greaves and the vine-staff of rank
    at his belt - and a long spatha whose blade the fire has never left."""
    k = X.Kit("ash_centurion")
    hips = k.part("hips", (0, 21, 0))
    k.box(hips, C(0, 18.4, 0, 7.0, 3.6, 4.4), "bone", tag="pelvis")
    k.stack(hips, 0, 0, [(12, 12.4, 9.0), (21, 12.0, 8.6)], "crimson", "tunic")
    for x in (-4.4, -2.2, 0, 2.2, 4.4):
        k.box(hips, C(x, 10.0, 4.6, 1.8, 10.0, 0.6), "leather", tag="pteruges")
        k.box(hips, C(x, 10.0, 4.95, 2.0, 1.0, 0.4), "bronze", tag="pteruges_tip")
    k.box(hips, C(0, 19.8, 0, 13.0, 2.0, 9.4), "leather", tag="belt")
    k.box(hips, C(-6.6, 8.0, 2.0, 1.2, 14.0, 1.2), "leather", tag="vine_staff")
    legs(k, hips, 20, 10.8, 3.6, "bone", "bronze", knee_mat="bronze", lean=-6, bend=8, w=5.0, cuff=False)
    to = k.part("torso", (0, 21, 0), (("x", 4),), "hips")
    segmentata(k, to, 21.0, 32.0, 13.0, 9.0)
    k.stack(to, 0, 0, [(31.6, 16.4, 9.8), (35.0, 15.6, 9.2)], "bronze", "lorica_top")
    for i, (x, y) in enumerate(((-3.6, 29.6), (0, 30.0), (3.6, 29.6), (-3.6, 25.6), (0, 26.0), (3.6, 25.6), (0, 22.0))):   # the phalerae
        k.ring(to, x, y, 5.4, 1.2, 0.6, "bronze", "phalera_rim", n=8, axis="z")
        k.box(to, C(x, y - 0.6, 5.5, 1.2, 1.2, 0.3), "teal" if i == 1 else "bronze", tag="phalera")
    k.limb(to, (-5.6, 34.6, 4.8), (5.6, 34.6, 4.8), 0.8, "leather", "harness_strap", d=0.4)
    for sx in (-1, 1):
        for i in range(3):
            k.box(to, C(sx * 9.4, 33.6 - i * 1.6, 0, 5.0 - i * 0.4, 1.8, 9.6 - i * 0.4), "bronze", tag="shoulder_band")
            k.box(to, C(sx * 9.4, 35.2 - i * 1.6, 4.85 - i * 0.2, 5.2 - i * 0.4, 0.3, 0.3), "teal", tag="band_fire")
    cl = k.part("cloak", (0, 35, -5.0), (("x", 5),), to, bone=False)
    for i, x in enumerate((-5.0, -1.6, 1.6, 5.0)):
        L = 26.0 - (i % 2) * 5.0
        k.box(cl, C(x, 35.0 - L, -5.6, 3.4, L, 0.8), "crimson", tag="cloak")
        k.box(cl, C(x + 0.4, 35.0 - L, -5.9, 2.2, 2.6, 0.4), "dark", tag="scorched_edge")
    flame(k, cl, (0, 10.0, -6.0), 4, 3.0, up=(0, 1, -0.3), seed=12)
    hd = k.part("head", (0, 35.6, 0.6), (("x", -4),), "torso")
    ash_skull(k, hd, (0, 38.8, 0.8), 1.08)
    galea(k, hd, (0, 40.6, 0.6), 1.1, transverse=True)
    arms(k, to, 9.8, 33, "bone", {1: ((("x", -36), ("z", -20)), (("x", -40),)), -1: ((("x", -32), ("z", 18)), (("x", -44),))}, w=3.2)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        k.box(k.parts["fore_" + nm], C(side * 9.8, 17.6, 0, 4.2, 5.0, 4.2), "bronze", tag="manica")
        for y in (18.6, 20.6):
            k.box(k.parts["fore_" + nm], C(side * 9.8, y, 0, 4.4, 0.4, 4.4), "teal", tag="manica_fire")
    sp = held(k, "spatha", "r", (-9.8, 14.0, 0.3), (("x", 78), ("z", -16)))
    k.limb(sp, (-9.8, 6.0, 0.3), (-9.8, 15.4, 0.3), 1.4, "leather", "grip")
    k.blob(sp, (-9.8, 5.2, 0.3), (1.4, 1.2, 1.4), "bronze", "pommel", step=0.4)
    k.box(sp, C(-9.8, 15.4, 0.3, 5.0, 1.4, 2.2), "bronze", tag="guard")
    k.box(sp, C(-9.8, 16.8, 0.3, 3.0, 26.0, 1.0), "steel", tag="spatha_blade")
    for sx in (-1, 1):
        k.box(sp, C(-9.8 + sx * 1.6, 16.8, 0.3, 0.5, 26.0, 1.1), "teal", tag="blade_fire_edge")
    k.shard(sp, (-9.8, 42.8, 0.3), (0, 1, 0), 3.4, 2.4, mat="steel", tag="blade_tip")
    for i in range(4):
        flame(k, sp, (-9.8, 20.0 + i * 6.0, 0.3), 2, 2.0, up=(0, 1, 0), seed=i + 20, spread=0.8)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.15)
    return k.s, k.parts


MOBS = {
    "ash_salamander": dict(make=ash_salamander, rig="crawler", ent=(1.2, 0.9), stats=dict(hp=30, speed=0.32, dmg=7, armor=3, kb=0)),
    "ash_legionary": dict(make=ash_legionary, ent=(0.9, 2.9), stats=dict(hp=66, speed=0.24, dmg=11, armor=10, kb=0.3)),
    "basalt_brute": dict(make=basalt_brute, ent=(1.9, 4.2), stats=dict(hp=230, speed=0.17, dmg=20, armor=12, kb=1.0)),
    "ash_augur": dict(make=ash_augur, ent=(0.9, 2.8), stats=dict(hp=42, speed=0.22, dmg=9, armor=3, kb=0)),
    "ash_lictor": dict(make=ash_lictor, ent=(0.8, 2.6), stats=dict(hp=46, speed=0.35, dmg=9, armor=3, kb=0)),
    "ash_centurion": dict(make=ash_centurion, ent=(1.1, 3.6), stats=dict(hp=360, speed=0.25, dmg=17, armor=13, kb=0.7), key=True),
}
