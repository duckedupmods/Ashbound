"""The Storm Bastion's monsters, each built by hand (tools/vox2.py). The order that held the spire swore to the storm
and the storm kept them: rain-black steel, copper gone green, tarred leather, slate-blue cloth, and the white-blue
of the lightning that lives in them now.

    spark_hound     swarm   a hound of iron plates with the lightning showing between them, a mane of sparks (the spider's bones)
    thunder_ogre    brute   an ogre in copper plate with a war drum on its back and a maul with a lightning rod in it
    storm_caller    caster  a robed caller with a crown of copper rods, a storm caught between her hands, her cloak blown up
    gale_knight     skirm   a light knight in a winged helm, a long blown cloak, a curved gale sabre and a buckler fan
    storm_captain   elite   the captain of the spire: blue steel and copper, a horned helm crackling, a tower shield, a halberd
    thunder_abbess  boss    the Thunder Abbess: a giant armoured abbess, a veil of steel, a halo of lightning rods, the
                            storm itself for a skirt, the great bell in one hand and a bolt of lightning in the other

    python tools/monsterforge.py storm_bastion --preview ; python tools/mobsheet.py storm_bastion
"""
import math

import vox2 as X
from vox2 import C, ramp

STEEL = ramp("#0c0e12", "#151920", "#20262e", "#2c343e", "#3a4450", "#4c5866", "#647280")
COPPER = ramp("#0e2a24", "#16403a", "#225a4e", "#2e7462", "#3e8c74", "#5aa88e")
BRASS = ramp("#2a1e10", "#44301a", "#644824", "#866232", "#a87e42", "#c89c58")
CLOTH = ramp("#0a0e16", "#121a26", "#1c283a", "#283850", "#364a68", "#466084")
LEATHER = ramp("#0e0a08", "#18120e", "#241a14", "#32241a", "#402e20")
STORM = ramp("#1a3a7a", "#2a5ab0", "#4a86e0", "#7ab0ff", "#c8e0ff", "#ffffff")
CLOUD = ramp("#1e242c", "#2c343e", "#3c4652", "#4e5a68", "#64707e", "#7e8a98")
SKIN = ramp("#2a2a2e", "#3c3c42", "#505058", "#66666e", "#7e7e86")
OGRE = ramp("#1a1e22", "#262c32", "#343c44", "#444e58", "#56626e")
BONE = ramp("#3a3a34", "#5a5a50", "#7a7a6c", "#9c9a8a", "#bcbaa8")


def shaders():
    return {
        "steel": X.surf(STEEL, 0.54, 1.5, 0.12, 0.24, drip=(CLOUD, 0.12)),
        "copper": X.surf(COPPER, 0.52, 1.3, 0.2, 0.16, rust=(BRASS, 0.12, 0.5)),
        "brass": X.surf(BRASS, 0.56, 1.4, 0.12, 0.2),
        "iron": X.surf(STEEL, 0.5, 1.4, 0.16, 0.18),
        "cloth": X.surf(CLOTH, 0.5, 1.0, 0.2, 0.0, holes=True),
        "robe": X.surf(CLOTH, 0.5, 1.0, 0.2, 0.0),
        "leather": X.surf(LEATHER, 0.5, 1.1, 0.2, 0.06),
        "glow": X.glow(STORM),
        "eye": X.glow(STORM, 0.86, 0.12),
        "cloud": X.surf(CLOUD, 0.5, 1.4, 0.4, 0.0),
        "skin": X.wrinkled(SKIN, 0.7),
        "ogre": X.wrinkled(OGRE, 0.9),
        "bone": X.surf(BONE, 0.6, 1.1, 0.16, 0.12),
        "dark": X.dark(STEEL),
    }


def bolt(k, part, p0, p1, w=0.8, n=4, seed=1):
    """a jagged lightning bolt from p0 to p1, glowing"""
    pts = [p0]
    for i in range(1, n):
        t = i / n
        off = 1.6 * (X.h3(i, seed, 1) - 0.5) * 2
        pts.append((p0[0] + (p1[0] - p0[0]) * t + off, p0[1] + (p1[1] - p0[1]) * t + off * 0.4,
                    p0[2] + (p1[2] - p0[2]) * t - off * 0.6))
    pts.append(p1)
    for (a, b) in zip(pts, pts[1:]):
        k.limb(part, a, b, w, "glow", "bolt", group="glow")


# ================================================================ the Thunder Abbess (boss)

def thunder_abbess():
    """The abbess of the spire rang the great bell to call the storm down on the order's enemies, and one day she
    called it down on herself and kept it. She stands six blocks high in armour of blue-black steel and copper; her
    face is hidden in a wimple and veil of steel plates, only the white eyes showing; behind her head stands a halo
    of iron lightning rods with the bolts arcing between them. Below the waist there is no robe any more: the storm
    is her skirt, a churning wall of cloud with the lightning in it, dragging on the ground. In her right hand the
    great bell of the spire on a chain, in her left a bolt of lightning held like a spear."""
    k = X.Kit("thunder_abbess")
    hips = k.part("hips", (0, 38, 0))
    k.stack(hips, 0, 0, [(32, 18, 13), (38, 19, 13.4)], "steel", "faulds")
    k.box(hips, C(0, 36.6, 0, 20, 2.6, 14.4), "copper", tag="belt")
    # the storm for a skirt: a swollen wall of cloud from the waist to the ground, lightning in it
    k.stack(hips, 0, 0, [(0, 40, 34), (6, 42, 36), (14, 38, 32), (24, 30, 24), (33, 21, 15)], "cloud", "storm_skirt", step=1.2)
    for a in range(0, 360, 30):
        r = math.radians(a)
        k.blob(hips, (math.sin(r) * 18, 10 + (a % 60) * 0.1, math.cos(r) * 15), (5.4, 4.6, 5.4), "cloud", "cloud_billow", step=1.2)
    for i, a in enumerate(range(15, 360, 45)):
        r = math.radians(a)
        bolt(k, hips, (math.sin(r) * 16, 26, math.cos(r) * 13), (math.sin(r) * 21, 1, math.cos(r) * 18), w=2.2, seed=i + 3)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6
        th = k.part("thigh_" + nm, (x, 32, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 18, 0), (), th)
        ft = k.part("foot_" + nm, (x, 4, 0), (), sh)
        k.box(ft, C(x, 0, 2, 8, 2, 10), "cloud", tag="foot")
    # ---------------------------------------------------------------- torso: blue-black plate, copper, a bell on the breast
    to = k.part("torso", (0, 39, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(38, 19, 13.4), (46, 22, 14), (54, 28, 15), (60, 27, 14)], "steel", "cuirass")
    k.box(to, C(0, 42, 7.2, 1.6, 16, 1.0), "copper", tag="ridge")
    k.box(to, C(0, 49, 7.6, 6.0, 6.4, 1.4), "copper", tag="breast_bell")
    k.box(to, C(0, 48.4, 8.4, 2.4, 1.6, 0.6), "glow", group="glow", tag="breast_bell_light")
    for side in (1, -1):         # great layered pauldrons, rods standing off them
        k.blob(to, (side * 14, 58, 0), (7, 4.4, 7.6), "steel", "pauldron")
        for i in range(3):
            k.box(to, C(side * (15 + i * 0.6), 55.4 - i * 2.2, 0, 9.4, 1.8, 13.6), "copper" if i % 2 else "steel", tag="lame")
        k.limb(to, (side * 16, 62, -2), (side * 19, 72, -4), 1.0, "copper", "shoulder_rod")
        k.box(to, C(side * 19, 72, -4, 1.6, 1.6, 1.6), "glow", group="glow", tag="rod_tip")
    # the cape, long, torn by the wind
    for i, x in enumerate((-9, -4.5, 0, 4.5, 9)):
        cp = k.part("cape%d" % i, (x, 58, -7.4), (("x", -14 - (i % 2) * 6),), to, bone=False)
        k.box(cp, C(x, 18 + (i % 2) * 4, -8, 4.6, 40 - (i % 2) * 4, 1.0), "cloth", tag="cape")
    # the halo of lightning rods, arcs between them
    hl = k.part("halo", (0, 72, -9), (), to, bone=False)
    k.limb(hl, (0, 58, -7.4), (0, 63, -9), 3.0, "brass", "halo_mount")
    tips = []
    for i in range(11):
        a = math.radians(-190 + i * 20)
        p0 = (math.cos(a) * 9, 72 + math.sin(a) * 9, -9)
        p1 = (math.cos(a) * 28, 72 + math.sin(a) * 28, -10)
        k.limb(hl, p0, p1, 2.2, "brass", "halo_rod")
        k.box(hl, C(p1[0], p1[1] - 1.6, p1[2], 3.2, 3.2, 3.2), "glow", group="glow", tag="rod_knob")
        tips.append(p1)
    for i, (a, b) in enumerate(zip(tips, tips[1:])):
        bolt(k, hl, a, b, w=1.4, n=3, seed=i + 20)
    k.ring(hl, 0, 72, -9, 9, 2.4, "brass", "halo_hub", n=16)
    k.ring(hl, 0, 72, -9.4, 22, 1.4, "brass", "halo_rim", n=34)
    # ---------------------------------------------------------------- the head: wimple and veil of steel plates, white eyes
    hd = k.part("head", (0, 60, 1), (("x", -6),), "torso")
    k.box(hd, C(0, 60, 0.6, 9.0, 11, 9.2), "steel", tag="wimple")
    k.box(hd, C(0, 63.6, 5.15, 6.4, 2.6, 0.6), "dark", tag="face_slot")
    for sx in (-1.6, 1.6):
        k.box(hd, C(sx, 64.2, 5.3, 2.0, 1.0, 0.4), "eye", group="glow", tag="eye")
    for i in range(4):           # the veil: steel plates down over the mouth and chest
        k.box(hd, C(0, 61.8 - i * 2.0, 5.2 + i * 0.3, 7.4 - i * 0.6, 1.8, 0.8), "steel" if i % 2 else "copper", tag="veil_plate")
    k.box(hd, C(0, 71, 0.6, 10.4, 2.0, 10.6), "steel", tag="coif_top")
    k.stack(hd, 0, -4.8, [(48, 12, 2), (60, 10, 2.4), (70, 9, 2)], "cloth", "veil_back")
    # ---------------------------------------------------------------- arms: the bell and the bolt
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 16
        up = k.part("arm_" + nm, (x, 58, 0), (("x", -60 if side > 0 else -30), ("z", side * 14)), "torso")
        fo = k.part("fore_" + nm, (x, 44, 0), (("x", -40 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 30, 0), (), fo)
        k.stack(up, x, 0, [(44, 7.4, 7.6), (52, 8.4, 8.6), (58, 9.0, 9.2)], "steel", "rerebrace")
        k.stack(fo, x, 0, [(31, 8.0, 8.2), (44, 8.4, 8.6)], "steel", "vambrace")
        k.box(fo, C(x, 32, 0, 9.2, 2.4, 9.4), "copper", tag="cuff")
        k.box(hn, C(x, 25, 0.6, 7.0, 6.4, 7.0), "steel", tag="gauntlet")
    # the great bell, on a chain from the right hand
    bl = k.part("bell", (-16, 26, 1), (("x", 30),), k.parts["hand_r"])
    k.chain(bl, (-16, 26, 1), (-16, 12, 4), 5, w=2.0)
    k.stack(bl, -16, 4, [(-14, 24, 24), (-11, 23, 23), (-3, 18, 18), (5, 15, 15), (10, 12, 12), (12, 6, 6)], "copper", "bell", step=1.0)
    k.box(bl, C(-16, -14, 4, 25, 2.0, 25), "brass", tag="bell_lip")
    k.box(bl, C(-16, 2, 4, 13.4, 1.2, 13.4), "brass", tag="bell_band")
    k.box(bl, C(-16, -13, 4, 20, 0.6, 20), "glow", group="glow", tag="bell_mouth")
    for a in range(0, 360, 90):
        r = math.radians(a)
        bolt(k, bl, (-16 + math.cos(r) * 8, -6, 4 + math.sin(r) * 8), (-16 + math.cos(r) * 12, -12, 4 + math.sin(r) * 12), w=0.8, n=3, seed=a)
    # the bolt of lightning in the left hand, held like a spear
    bt = k.part("spear_bolt", (16, 27, 1), (("x", 80),), k.parts["hand_l"])
    bolt(k, bt, (16, 6, 1), (16, 58, 1), w=2.4, n=7, seed=9)
    bolt(k, bt, (16, 40, 1), (19, 50, 3), w=1.0, n=3, seed=10)
    bolt(k, bt, (16, 20, 1), (13, 12, 0), w=1.0, n=3, seed=11)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Storm Captain (elite, the key)

def storm_captain():
    """The captain of the spire's guard keeps the rod that locks the stair. Blue-black plate with copper at every
    edge, a great helm with two horns of copper rod that crackle, a tower shield with a lightning bolt across it in
    storm glass, a halberd whose spike is a lightning rod, and the bolts walk up and down it."""
    k = X.Kit("storm_captain")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(16, 13, 8.6), (22, 13.6, 9)], "steel", "faulds")
    for x in (-4.4, 0, 4.4):
        k.box(hips, C(x, 12.6, 4.8, 4.0, 6.4, 0.8), "steel", tag="tasset")
        k.box(hips, C(x, 12.6, 5.25, 4.2, 0.8, 0.4), "copper", tag="tasset_edge")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.6
        th = k.part("thigh_" + nm, (x, 21, 0), (("x", -6), ("z", side * 5)), "hips")
        sh = k.part("shin_" + nm, (x, 11.4, 0), (("x", 10),), th)
        ft = k.part("foot_" + nm, (x, 2.8, 0), (("x", -4),), sh)
        k.box(th, C(x, 11.6, 0, 5.4, 9.6, 5.8), "steel", tag="cuisse")
        k.box(th, C(x, 10.4, 1.0, 6.0, 3.0, 5.4), "copper", tag="poleyn")
        k.box(sh, C(x, 2.8, 0, 5.4, 8.6, 5.8), "steel", tag="greave")
        k.box(ft, C(x, 0, 1.6, 5.8, 3.0, 8.8), "steel", tag="foot")
    cl = k.part("cloak", (0, 37, -5), (("x", -6),), "hips", bone=False)
    for i, x in enumerate((-5, -1.6, 1.8, 5.2)):
        k.box(cl, C(x, 3 + (i % 2) * 2, -5.4, 3.6, 33 - (i % 2) * 2, 0.8), "cloth", tag="cloak")
    # ---------------------------------------------------------------- torso
    to = k.part("torso", (0, 22, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(22, 13.6, 9), (28, 17, 10.4), (33, 19, 10.8), (37, 17, 9.8)], "steel", "cuirass")
    k.box(to, C(0, 23, 5.3, 1.4, 12, 0.8), "copper", tag="ridge")
    bolt(k, to, (2.4, 34, 5.6), (-2.4, 25, 5.6), w=1.0, n=3, seed=4)
    for side in (1, -1):
        k.blob(to, (side * 10.4, 36, 0), (6.0, 3.8, 6.2), "steel", "pauldron")
        for i in range(3):
            k.box(to, C(side * (11 + i * 0.4), 33.6 - i * 1.8, 0, 7.0, 1.6, 10), "copper" if i % 2 == 0 else "steel", tag="lame")
    # ---------------------------------------------------------------- the great helm, two copper rods for horns
    hd = k.part("head", (0, 37, 0.4), (("x", -6),), "torso")
    k.box(hd, C(0, 37, 0.2, 7.0, 8.0, 7.2), "steel", tag="helm")
    k.box(hd, C(0, 41.2, 3.75, 6.0, 1.0, 0.4), "dark", tag="visor")
    for sx in (-1.4, 1.4):
        k.box(hd, C(sx, 41.3, 3.85, 1.6, 0.7, 0.3), "eye", group="glow", tag="eye")
    for i in range(5):
        k.box(hd, C(-1.6 + i * 0.8, 38.6, 3.85, 0.4, 1.2, 0.3), "dark", tag="breath")
    for sx in (-1, 1):
        pts = [(sx * 3.4, 43, 0), (sx * 6, 46, -1), (sx * 7, 50, 0), (sx * 6.4, 53, 1.6)]
        for (a, b) in zip(pts, pts[1:]):
            k.limb(hd, a, b, 1.2, "copper", "horn_rod")
        k.box(hd, C(sx * 6.4, 52.4, 1.6, 1.4, 1.4, 1.4), "glow", group="glow", tag="rod_tip")
        bolt(k, hd, (sx * 6.4, 53, 1.6), (sx * 2, 47, 0.4), w=0.5, n=3, seed=sx + 30)
    # ---------------------------------------------------------------- arms: the tower shield, the halberd
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 10.4
        up = k.part("arm_" + nm, (x, 35, 0), (("x", -40 if side > 0 else -30), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 26, 0), (("x", -50 if side > 0 else -70),), up)
        hn = k.part("hand_" + nm, (x, 17, 0), (), fo)
        k.box(up, C(x, 26.6, 0, 5.0, 8.6, 5.2), "steel", tag="rerebrace")
        k.box(fo, C(x, 17.6, 0, 5.0, 8.6, 5.2), "steel", tag="vambrace")
        k.box(hn, C(x, 13.8, 0.4, 4.6, 4.0, 4.6), "steel", tag="gauntlet")
    sh = k.part("shield", (14, 17, 2), (("y", 8),), k.parts["hand_l"])
    k.box(sh, C(14.4, 4, 2, 1.6, 30, 15), "steel", tag="tower_shield")
    k.box(sh, C(15.3, 4, 2, 0.6, 30, 1.2), "copper", tag="shield_rim")
    for z in (-6.6, 10.6):
        k.box(sh, C(15.3, 4, z, 0.6, 30, 1.0), "copper", tag="shield_rim")
    for y in (4, 33):
        k.box(sh, C(15.3, y, 2, 0.6, 1.0, 15.4), "copper", tag="shield_rim")
    bolt(k, sh, (15.6, 30, 6), (15.6, 8, -2), w=1.6, n=4, seed=7)
    # the halberd: a lightning rod for a spike
    hb = k.part("halberd", (-10.4, 15.6, 0.6), (("x", 80),), k.parts["hand_r"])
    k.limb(hb, (-10.4, -12, 0.6), (-10.4, 42, 0.6), 1.4, "leather", "haft")
    k.box(hb, C(-10.4, 34, 3.0, 1.2, 8, 5.4), "steel", tag="axe_blade")
    k.box(hb, C(-10.4, 33, 7.8, 1.4, 10, 1.2), "steel", tag="axe_edge")
    k.shard(hb, (-10.4, 37, -2.4), (0, 0, -1), 4.0, 2.0, mat="steel", tag="back_spike")
    k.limb(hb, (-10.4, 42, 0.6), (-10.4, 52, 0.6), 0.8, "copper", "rod_spike")
    k.box(hb, C(-10.4, 51.4, 0.6, 1.4, 1.4, 1.4), "glow", group="glow", tag="rod_tip")
    bolt(k, hb, (-10.4, 52, 0.6), (-10.4, 36, 4), w=0.6, n=3, seed=12)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Thunder Ogre (brute)

def thunder_ogre():
    """The order kept ogres to haul the guns up the spire; the storm got into them too. A blue-grey ogre in plates
    of green copper riveted onto leather, a war drum strapped to its back that it beats with its free fist so the
    thunder rolls, and a great maul with a lightning rod set in its head that calls the bolt down where it lands."""
    k = X.Kit("thunder_ogre")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(15, 16, 11), (22, 17, 11.6)], "leather", "loin")
    for x in (-5, 0, 5):
        k.box(hips, C(x, 11, 6, 4.6, 8, 0.8), "copper", tag="tasset")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.4
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -10), ("z", side * 10)), "hips")
        sh = k.part("shin_" + nm, (x, 10.6, 0), (("x", 14),), th)
        ft = k.part("foot_" + nm, (x, 2.6, 0), (("x", -4),), sh)
        k.stack(th, x, 0, [(10.6, 7.6, 7.8), (16, 9.0, 9.2), (20, 8.4, 8.6)], "ogre", "thigh")
        k.stack(sh, x, 0, [(2.6, 7.0, 7.2), (10.6, 7.8, 8.0)], "ogre", "shin")
        k.box(sh, C(x, 5, 3.8, 5.6, 6.0, 1.0), "copper", tag="greave")
        k.box(ft, C(x, 0, 1.8, 8.4, 3.0, 11), "leather", tag="foot")
    # ---------------------------------------------------------------- torso: copper plates on leather; the war drum on its back
    to = k.part("torso", (0, 22, 0), (("x", 18),), "hips")
    k.blob(to, (0, 26, 2.6), (10, 7, 8), "ogre", "belly")
    k.stack(to, 0, -1, [(27, 21, 13), (33, 27, 14), (38, 25, 12.6)], "ogre", "chest")
    for (x, y) in ((-6, 30), (6, 30), (-6, 35), (6, 35), (0, 33)):
        k.box(to, C(x, y, 7.0, 5.0, 4.4, 0.8), "copper", tag="chest_plate")
        k.rivets(to, [(x - 2, y + 3.8, 7.5), (x + 2, y + 3.8, 7.5)], "brass", 0.7)
    k.limb(to, (-12, 38, 4), (10, 24, 9), 2.0, "leather", "strap", d=0.6)
    dr = (0, 30, -11)
    k.stack(to, 0, -11, [(22, 14, 14), (24, 15, 15), (36, 15, 15), (38, 14, 14)], "leather", "drum")
    k.box(to, C(0, 38, -11, 13, 0.6, 13), "bone", tag="drum_skin")
    for y in (24, 31, 37):
        k.ring(to, 0, y, -11, 7.6, 0.8, "brass", "drum_hoop", n=16, axis="y")
    for a in range(0, 360, 45):
        r = math.radians(a)
        k.limb(to, (math.cos(r) * 7.4, 24, -11 + math.sin(r) * 7.4), (math.cos(r) * 7.4, 37, -11 + math.sin(r) * 7.4), 0.4, "leather", "drum_cord")
    bolt(k, to, (-4, 39, -9), (-6, 46, -10), w=0.8, n=3, seed=2)
    bolt(k, to, (4, 39, -12), (7, 45, -13), w=0.8, n=3, seed=5)
    # ---------------------------------------------------------------- the head: low, a copper helmet bolted on, a jaw like a step
    hd = k.part("head", (0, 37, 4), (("x", -20),), "torso")
    k.box(hd, C(0, 36, 5.4, 9.0, 7.6, 8.2), "ogre", tag="head")
    k.box(hd, C(0, 34.4, 8.6, 10.0, 3.6, 4.4), "ogre", tag="jaw")
    k.blob(hd, (0, 43, 5.4), (5.6, 2.4, 5.4), "copper", "helmet")
    k.box(hd, C(0, 41.6, 9.6, 9.0, 1.2, 1.4), "copper", tag="helmet_rim")
    for sx in (-2.4, 2.4):
        k.box(hd, C(sx, 40.0, 9.5, 1.6, 0.8, 0.4), "eye", group="glow", tag="eye")
        k.shard(hd, (sx * 1.1, 37.4, 10.4), (sx * 0.15, 1, 0.2), 4.0, 1.4, mat="bone", tag="tusk")
    k.limb(hd, (0, 45, 5.4), (0, 50, 4.4), 0.8, "copper", "helmet_rod")
    k.box(hd, C(0, 49.6, 4.4, 1.2, 1.2, 1.2), "glow", group="glow", tag="rod_tip")
    # ---------------------------------------------------------------- arms: the maul with a rod in its head
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 14
        up = k.part("arm_" + nm, (x, 36, 0), (("x", -20 if side > 0 else -100), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 25, 0), (("x", -40 if side > 0 else -30),), up)
        hn = k.part("hand_" + nm, (x, 14, 0), (), fo)
        k.blob(up, (x, 34, 0), (6.0, 5.0, 6.2), "copper", "pauldron")
        k.stack(up, x, 0, [(25, 7.0, 7.2), (31, 8.0, 8.2)], "ogre", "upper_arm")
        k.stack(fo, x, 0, [(15, 8.0, 8.0), (20, 8.6, 8.6), (25, 7.4, 7.4)], "ogre", "forearm")
        k.box(fo, C(x, 16, 0, 9.0, 3.4, 9.0), "copper", tag="bracer")
        k.box(hn, C(x, 9.0, 0.6, 7.4, 6.4, 7.4), "ogre", tag="fist")
    mt = k.part("maul", (-14, 11, 0.6), (("x", 20),), k.parts["hand_r"])
    k.limb(mt, (-14, 2, 0.6), (-14, 36, 0.6), 2.2, "leather", "haft")
    k.box(mt, C(-14, 32, 0.6, 10, 9, 9), "steel", tag="maul_head")
    for y in (33, 39):
        k.box(mt, C(-14, y, 0.6, 10.6, 1.4, 9.6), "copper", tag="maul_band")
    k.limb(mt, (-14, 41, 0.6), (-14, 50, 0.6), 1.0, "copper", "maul_rod")
    k.box(mt, C(-14, 49.4, 0.6, 1.8, 1.8, 1.8), "glow", group="glow", tag="rod_tip")
    bolt(k, mt, (-14, 50, 0.6), (-18, 41, 4), w=0.7, n=3, seed=8)
    bolt(k, mt, (-14, 50, 0.6), (-10, 42, -3), w=0.7, n=3, seed=13)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Storm Caller (caster)

def storm_caller():
    """The callers stand on the ramparts in the rain and pull the lightning down. Long slate-blue robes soaked
    through and blown up behind them, a crown of copper rods, a face pale as a drowned woman's, and between her
    raised hands a storm held in a knot - a ball of cloud with the bolts crawling over it."""
    k = X.Kit("storm_caller")
    hips = k.part("hips", (0, 19, 0))
    k.stack(hips, 0, 0, [(1, 11, 8.6), (10, 10, 7.4), (19, 9, 6.6)], "robe", "robe")
    for i, (x, L) in enumerate(((-4, 18), (-1.4, 22), (1.4, 20), (4, 16))):     # the robe blown out behind
        k.limb(hips, (x, 16, -3), (x * 1.3, 16 - L * 0.5, -3 - L * 0.7), 3.0, "cloth", "robe_blown", d=0.6)
    k.box(hips, C(0, 18.6, 0, 9.8, 1.8, 7.0), "copper", tag="belt")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 19, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 10, 0), (), th)
        ft = k.part("foot_" + nm, (x, 2, 0), (), sh)
        k.box(ft, C(x, 0, 1.8, 3.0, 1.4, 5.0), "leather", tag="foot")
    # ---------------------------------------------------------------- torso
    to = k.part("torso", (0, 19, 0), (("x", -6),), "hips")
    k.stack(to, 0, 0, [(19, 9, 6.6), (25, 10.6, 7.0), (31, 11.6, 7.0)], "robe", "robe")
    k.box(to, C(0, 21, 3.6, 3.0, 10, 0.6), "copper", tag="stole")
    for (x, y) in ((-1.4, 24), (1.4, 28)):
        k.box(to, C(x, y, 4.0, 1.0, 1.0, 0.4), "glow", group="glow", tag="stud")
    k.stack(to, 0, -0.4, [(27, 14, 9), (31, 14.4, 9.2), (33, 12, 8)], "cloth", "mantle")
    # ---------------------------------------------------------------- the head: pale, the crown of rods, hair blown up
    hd = k.part("head", (0, 31.4, 0.6), (("x", 8),), "torso")
    k.box(hd, C(0, 31.4, 0.6, 5.0, 6.0, 5.4), "skin", tag="face")
    for sx in (-1.1, 1.1):
        k.box(hd, C(sx, 34.4, 3.35, 1.2, 0.6, 0.3), "eye", group="glow", tag="eye")
    k.box(hd, C(0, 32.4, 3.35, 1.6, 0.5, 0.3), "dark", tag="mouth")
    for (x, z) in ((-2, -1), (0, -2), (2, -1), (-1, -2.6), (1, -2.6)):
        k.limb(hd, (x, 36, z), (x * 1.6, 40, z - 3), 1.2, "cloth", "hair_blown", d=0.6)
    k.ring(hd, 0, 36.6, 0.6, 3.0, 0.6, "copper", "crown_band", n=12, axis="y")
    for i in range(7):
        a = math.radians(-90 + i * 30)
        x, z = math.sin(a) * 3.0, 0.6 + math.cos(a) * 3.0
        L = 5 if i == 3 else 3.4
        k.limb(hd, (x, 36.6, z), (x * 1.2, 36.6 + L, z * 1.1), 0.5, "copper", "crown_rod")
        k.box(hd, C(x * 1.2, 36.2 + L, z * 1.1, 0.8, 0.8, 0.8), "glow", group="glow", tag="rod_tip")
    # ---------------------------------------------------------------- arms raised, the storm between her hands
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.6
        up = k.part("arm_" + nm, (x, 29.6, 0), (("x", -110), ("z", side * 20)), "torso")
        fo = k.part("fore_" + nm, (x, 21.6, 0), (("x", -20), ("z", -side * 30)), up)
        hn = k.part("hand_" + nm, (x, 13.8, 0), (), fo)
        k.box(up, C(x, 21.4, 0, 3.6, 8.4, 3.8), "robe", tag="sleeve")
        k.stack(fo, x, 0, [(13.4, 5.6, 5.6), (21.6, 3.8, 3.8)], "cloth", "sleeve")
        k.box(hn, C(x, 11.4, 0.4, 2.4, 2.8, 2.4), "skin", tag="hand")
    sb = k.part("storm_ball", (0, 44, 6), (), to, bone=False)
    k.blob(sb, (0, 44, 6), (4.0, 3.6, 4.0), "cloud", "storm_ball", step=0.8)
    k.blob(sb, (0, 44, 6), (2.0, 2.0, 2.0), "glow", "storm_core", step=0.6)
    for i in range(5):
        a = i * 1.26
        bolt(k, sb, (math.cos(a) * 2, 44 + math.sin(a) * 2, 6), (math.cos(a) * 6, 44 + math.sin(a) * 6, 6 + (i % 2) * 2), w=0.5, n=3, seed=i + 40)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Gale Knight (skirmisher)

def gale_knight():
    """The gale knights ride the wind off the ramparts. Light plate over blue cloth, a cloak three times their
    length that the wind always has hold of, a helm with copper wings swept back; a long curved sabre and on the
    other arm a buckler like a fan of steel blades that opens."""
    k = X.Kit("gale_knight")
    hips = k.part("hips", (0, 20, 0))
    k.box(hips, C(0, 17.4, 0, 8.4, 3.6, 5.4), "steel", tag="faulds")
    k.box(hips, C(0, 20, 0, 9.0, 1.4, 6.0), "copper", tag="belt")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.6
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -30 if side > 0 else 10), ("z", side * 8)), "hips")
        sh = k.part("shin_" + nm, (x, 10.8, 0), (("x", 40 if side > 0 else 10),), th)
        ft = k.part("foot_" + nm, (x, 2.4, 0), (("x", -10),), sh)
        k.box(th, C(x, 11, 0, 3.8, 9.2, 4.0), "robe", tag="thigh")
        k.box(th, C(x, 12, 1.2, 4.0, 6.0, 2.0), "steel", tag="cuisse")
        k.box(sh, C(x, 2.4, 0, 3.8, 8.4, 4.0), "steel", tag="greave")
        k.box(ft, C(x, 0, 1.4, 3.8, 2.4, 6.2), "steel", tag="foot")
    # the long cloak, streaming back in the wind
    cl = k.part("cloak", (0, 30, -3), (("x", -60),), hips, bone=False)
    for i, x in enumerate((-4.4, -1.4, 1.6, 4.6)):
        k.box(cl, C(x, -6 - (i % 2) * 4, -3.4, 3.2, 36 + (i % 2) * 4, 0.6), "cloth", tag="cloak")
    # ---------------------------------------------------------------- torso
    to = k.part("torso", (0, 20, 0), (("x", 24), ("y", -14)), "hips")
    k.stack(to, 0, 0, [(20, 8.4, 5.4), (25, 10, 6.0), (30, 11.6, 6.2)], "steel", "cuirass")
    k.box(to, C(0, 21, 3.2, 1.0, 9, 0.6), "copper", tag="ridge")
    for side in (1, -1):
        k.blob(to, (side * 6, 29.6, 0), (3.2, 2.2, 3.4), "steel", "pauldron")
    # ---------------------------------------------------------------- the winged helm
    hd = k.part("head", (0, 30, 0.4), (("x", -20), ("y", 14)), "torso")
    k.box(hd, C(0, 30.2, 0.2, 5.2, 6.0, 5.4), "steel", tag="helm")
    k.box(hd, C(0, 33.4, 2.85, 4.4, 0.8, 0.4), "dark", tag="visor")
    for sx in (-1.1, 1.1):
        k.box(hd, C(sx, 33.5, 2.95, 1.2, 0.5, 0.3), "eye", group="glow", tag="eye")
    for sx in (-1, 1):
        for i in range(4):
            k.shard(hd, (sx * 2.6, 34.4 - i * 1.0, 0.4 - i * 0.6), (sx * 0.5, 0.5 - i * 0.12, -1), 5.0 - i * 0.6, 1.2,
                    mat="copper", tag="helm_wing")
    # ---------------------------------------------------------------- arms: the sabre and the fan-buckler
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.2
        up = k.part("arm_" + nm, (x, 28.4, 0), (("x", -40 if side > 0 else -100), ("z", side * 20)), "torso")
        fo = k.part("fore_" + nm, (x, 21, 0), (("x", -60 if side > 0 else -10),), up)
        hn = k.part("hand_" + nm, (x, 13.8, 0), (), fo)
        k.box(up, C(x, 21.2, 0, 3.2, 7.4, 3.4), "robe", tag="sleeve")
        k.box(fo, C(x, 14, 0, 3.4, 7.2, 3.6), "steel", tag="vambrace")
        k.box(hn, C(x, 11.4, 0.3, 2.6, 2.6, 2.6), "steel", tag="gauntlet")
    fb = k.part("fan_buckler", (8, 15, 1), (("y", 10),), k.parts["fore_l"])
    for i in range(7):
        a = math.radians(-60 + i * 20)
        k.limb(fb, (9.4, 15, 1), (9.6, 15 + math.cos(a) * 7, 1 + math.sin(a) * 7), 1.6, "steel", "fan_blade", d=0.4)
    k.ring(fb, 9.6, 15, 1, 2.0, 0.8, "copper", "fan_hub", n=8, axis="x")
    sb = k.part("sabre", (-6.2, 12.6, 0.6), (("x", 80),), k.parts["hand_r"])
    k.box(sb, C(-6.2, 9.8, 0.6, 1.0, 4.6, 1.0), "leather", tag="grip")
    k.box(sb, C(-6.2, 14.2, 0.6, 1.2, 0.8, 4.0), "copper", tag="guard")
    for i, (dy, dz, wd) in enumerate(((0, 0, 2.6), (5, 0.6, 2.8), (10, 1.6, 2.6), (14, 3.0, 2.0), (17, 4.6, 1.2))):
        k.box(sb, C(-6.2, 15 + dy, 0.6 + dz, 0.6, 5.0, wd), "steel", tag="blade")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Spark Hound (swarm, on the spider)

def spark_hound():
    """The spire's hounds were iron before the storm took them: a lean dog built of black plates with the lightning
    showing in every gap, a mane of sparks standing off its neck, eyes like arc-lamps, iron teeth. They run on the
    walls in the rain and the bolts follow them."""
    k = X.Kit("spark_hound")
    body = k.part("body", (0, 9, 0))
    k.stack(body, 0, 0, [(6, 6.0, 9), (9, 7.4, 10), (12, 6.4, 9)], "steel", "chest")
    k.box(body, C(0, 7, 0, 4.4, 4.4, 8.4), "glow", group="glow", tag="core")
    for z in (-3, 0, 3):
        k.box(body, C(0, 12.4, z, 6.8, 0.8, 2.0), "copper", tag="spine_plate")
    hd = k.part("head", (0, 11, 5), (("x", -10),), "body")
    k.box(hd, C(0, 10, 6.6, 4.4, 4.0, 4.4), "steel", tag="head")
    k.box(hd, C(0, 9.4, 10.4, 3.0, 2.6, 4.0), "steel", tag="muzzle")
    k.box(hd, C(0, 8.4, 10.6, 2.6, 0.8, 3.6), "glow", group="glow", tag="mouth_light")
    for t in (-0.8, 0.8):
        k.shard(hd, (t, 9.0, 13.6), (0, -1, 0.2), 1.4, 0.5, mat="steel", tag="tooth")
    for sx in (-1.4, 1.4):
        k.box(hd, C(sx, 12.0, 8.85, 1.2, 0.8, 0.3), "eye", group="glow", tag="eye")
        k.shard(hd, (sx * 1.4, 14, 6.4), (sx * 0.2, 1, -0.4), 2.6, 1.2, mat="steel", tag="ear")
    for i in range(9):           # the mane of sparks off its neck
        a = math.radians(-80 + i * 20)
        bolt(k, hd, (math.sin(a) * 2.6, 13, 5.4), (math.sin(a) * 5.4, 16 + (i % 2) * 1.6, 3.4), w=0.5, n=2, seed=i + 50)
    ab = k.part("abdomen", (0, 9, -4.4), (), "body")
    k.stack(ab, 0, -7, [(6.4, 5.0, 6.0), (9, 5.6, 6.4), (11.4, 5.0, 6.0)], "steel", "haunch")
    k.box(ab, C(0, 7.4, -7, 3.0, 3.0, 5.0), "glow", group="glow", tag="core")
    tail = [(0, 11, -10.4), (0, 13, -14), (0, 16, -16)]
    for (a, b) in zip(tail, tail[1:]):
        k.limb(ab, a, b, 1.0, "steel", "tail")
    bolt(k, ab, (0, 16, -16), (0, 19, -17), w=0.6, n=2, seed=60)
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, (z, j, part) in enumerate(((3.0, 1, body), (-7.0, 4, ab))):
            nm = "leg_%s%d" % (s, i)
            lg = k.part(nm, (side * 3.0, 8, z), (), part)
            kn = (side * 3.4, 4.0, z + (1.4 if i == 0 else -1.4))
            k.limb(lg, (side * 3.0, 8, z), kn, 2.0, "steel", "leg")
            k.limb(lg, kn, (side * 3.4, 0.4, z + (0.4 if i == 0 else 0.6)), 1.6, "steel", "foot")
            k.box(lg, C(side * 3.4, 0, z + 1.0, 2.4, 1.0, 2.8), "copper", tag="foot")
            k.box(lg, C(side * 3.8, 3.8, z, 0.6, 1.0, 1.0), "glow", group="glow", tag="joint_spark")
            joints[nm] = ("LL" if side > 0 else "RL") + str(j)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


MOBS = {
    "spark_hound": dict(make=spark_hound, rig="crawler", ent=(1.0, 1.2), stats=dict(hp=30, speed=0.38, dmg=7, armor=5, kb=0)),
    "thunder_ogre": dict(make=thunder_ogre, ent=(1.7, 4.0), stats=dict(hp=130, speed=0.19, dmg=17, armor=12, kb=1.0)),
    "storm_caller": dict(make=storm_caller, ent=(0.9, 2.9), stats=dict(hp=48, speed=0.21, dmg=8, armor=3, kb=0)),
    "gale_knight": dict(make=gale_knight, ent=(0.9, 2.9), stats=dict(hp=42, speed=0.37, dmg=9, armor=6, kb=0)),
    "storm_captain": dict(make=storm_captain, ent=(1.3, 3.5), stats=dict(hp=250, speed=0.23, dmg=15, armor=14, kb=0.7), key=True),
    "thunder_abbess": dict(make=thunder_abbess, texel=1, ent=(3.2, 6.8), stats=dict(hp=700, speed=0.2, dmg=22, armor=12, kb=1.0), boss=True),
}
