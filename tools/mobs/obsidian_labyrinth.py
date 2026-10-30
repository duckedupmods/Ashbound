"""The Obsidian Labyrinth's monsters, each built by hand (tools/vox2.py). The maze in the nether and the things it
was built to hold: black glass gone purple at the edges, basalt, old bronze, ash, horn, and the magma that shows
through every crack in them.

    labyrinth_imp   swarm   a small horned imp of cracked obsidian, little wings, a barbed tail, ember eyes
    basalt_ogre     brute   an ogre grown of basalt columns, magma in the joints, a basalt column for a club
    ember_oracle    caster  the blind oracle: eyes bound in a cloth with burning runes, a bowl of embers on a tripod staff
    horned_runner   skirm   goat-legged and bull-horned, a mane, two bronze hand-axes, running the turns of the maze
    gatekeeper      elite   the warden of the ninth door: bronze plate cast with the maze, a door for a shield, a key-blade
    minotaur        boss    the Minotaur of the Ninth Gate: an obsidian bull giant, magma in his cracks, horns burning,
                            chains on his wrists, a double-headed axe as tall as a man

    python tools/monsterforge.py obsidian_labyrinth --preview ; python tools/mobsheet.py obsidian_labyrinth
"""
import math

import vox2 as X
from vox2 import C, ramp

OBSID = ramp("#04020a", "#0a0614", "#120c1e", "#1a1228", "#241a34", "#302442", "#46365c")
BASALT = ramp("#0e0c0c", "#181514", "#221e1c", "#2e2826", "#3a3330", "#48403c")
BRONZE = ramp("#2a1608", "#442410", "#62361a", "#824a24", "#a2602e", "#c07a3c", "#dc9a5a")
MAGMA = ramp("#6a1004", "#b02a06", "#e05a0c", "#ff8a20", "#ffc860", "#fff0c0")
ASH = ramp("#1a1716", "#2a2624", "#3a3532", "#4c4642", "#5e5752")
HORN = ramp("#0e0a08", "#1a1410", "#2a2018", "#3c2e22", "#504030")
FUR = ramp("#100806", "#1c0e0a", "#2a160e", "#3a2014", "#4a2a1a")
CLOTH = ramp("#1a0806", "#2e0e0a", "#461610", "#5e2016", "#762a1c")
BONE = ramp("#3a3428", "#5a5240", "#7c7258", "#9e9476", "#c0b896")
IRON = ramp("#0e0c0c", "#181414", "#241e1e", "#322a2a", "#423838")


def shaders():
    return {
        "obsidian": X.surf(OBSID, 0.5, 1.7, 0.12, 0.28),
        "basalt": X.surf(BASALT, 0.5, 1.3, 0.3, 0.06, stripe=4, crust=(ASH, 0.1)),
        "bronze": X.surf(BRONZE, 0.54, 1.4, 0.14, 0.2, rust=(OBSID, 0.16, 0.5)),
        "glow": X.glow(MAGMA),
        "eye": X.glow(MAGMA, 0.86, 0.12),
        "ash": X.surf(ASH, 0.5, 1.0, 0.3, 0.0),
        "horn": X.surf(HORN, 0.5, 1.4, 0.16, 0.14, stripe=3),
        "fur": X.surf(FUR, 0.5, 1.0, 0.3, 0.0, stripe=2),
        "cloth": X.surf(CLOTH, 0.5, 1.0, 0.2, 0.0, holes=True),
        "bone": X.surf(BONE, 0.6, 1.1, 0.16, 0.12),
        "iron": X.surf(IRON, 0.5, 1.4, 0.16, 0.18),
        "dark": X.dark(OBSID),
    }


def cracks(k, part, segs, w=0.7):
    """magma showing through cracks: a list of (p0, p1)"""
    for (a, b) in segs:
        k.limb(part, a, b, w, "glow", "crack", group="glow", d=0.5)


def horns(k, part, at, side, s=1.0, mat="horn", burning=False):
    """a bull's horn: out, then forward and up, tapering; a fire at the tip if it burns"""
    x, y, z = at
    pts = [(x, y, z), (x + side * 4 * s, y + 0.6 * s, z - 0.6 * s), (x + side * 7 * s, y + 2.6 * s, z + 0.6 * s), (x + side * 8 * s, y + 5.6 * s, z + 2.6 * s)]
    for (a, b), w in zip(zip(pts, pts[1:]), (2.4 * s, 1.8 * s, 1.1 * s)):
        k.limb(part, a, b, w, mat, "horn")
    if burning:
        k.shard(part, pts[-1], (0, 1, 0.2), 3.0 * s, 1.6 * s, mat="glow", tag="horn_fire", group="glow")


# ================================================================ the Minotaur (boss)

def minotaur():
    """They built the labyrinth to hold him and he outgrew it. A bull-headed giant six blocks high, his hide black
    obsidian cracked all over with the magma glowing in the cracks; a shaggy mane of ash-black hair over his
    shoulders; a bronze ring through his nose; horns as long as spears, burning at the tips. Bronze war-belt, a
    kilt of chain and leather, cloven hooves that crack the floor. Iron cuffs on both wrists with the broken
    chains that held him still hanging off them. He carries the labrys, the great double-headed axe of the
    labyrinth's builders, as tall as a man."""
    k = X.Kit("minotaur")
    hips = k.part("hips", (0, 38, 0))
    k.stack(hips, 0, 0, [(30, 22, 15), (38, 23, 15.6)], "obsidian", "hips")
    k.box(hips, C(0, 35.6, 0, 25, 3.4, 17.6), "bronze", tag="war_belt")
    k.box(hips, C(0, 35.2, 8.9, 6.0, 4.4, 1.0), "bronze", tag="belt_plate")
    k.box(hips, C(0, 36.0, 9.5, 3.0, 2.6, 0.6), "glow", group="glow", tag="belt_ember")
    for i in range(9):           # a kilt of chain-mail strips and leather
        a = math.radians(-120 + i * 30)
        k.box(hips, C(math.sin(a) * 11, 22, math.cos(a) * 7.6, 5.0, 13, 1.2), "iron" if i % 2 else "cloth", tag="kilt",
              rots=(("y", -math.degrees(a)),), pivot=(math.sin(a) * 11, 30, math.cos(a) * 7.6))
    for side, nm in ((1, "l"), (-1, "r")):       # bull's legs: thick thigh, reversed hock, a cloven hoof
        x = side * 7
        th = k.part("thigh_" + nm, (x, 34, 0), (("x", -20), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 20, 0), (("x", 34),), th)
        ft = k.part("foot_" + nm, (x, 6, 0), (("x", -14),), sh)
        k.stack(th, x, 0, [(20, 11, 11.6), (27, 13, 13.4), (34, 12, 12.6)], "fur", "thigh")
        k.stack(sh, x, -1, [(6, 7.4, 7.6), (13, 8.4, 8.6), (20, 9.4, 9.6)], "obsidian", "shank")
        cracks(k, sh, [((x + side * 4, 16, 1), (x + side * 3, 9, 2)), ((x - side * 2, 18, 4.4), (x, 12, 4.4))])
        for sx in (-2.4, 2.4):
            k.box(ft, C(x + sx, 0, 1.6, 4.4, 6.4, 8.4), "horn", tag="foot")
        k.box(ft, C(x, 4.4, 1.0, 9.6, 2.0, 9.0), "fur", tag="fetlock")
    # ---------------------------------------------------------------- torso: a slab of black glass, cracked with fire
    to = k.part("torso", (0, 39, 0), (("x", 16),), "hips")
    k.stack(to, 0, 0, [(38, 23, 15.6), (46, 30, 17), (54, 38, 18), (59, 36, 17)], "obsidian", "torso")
    cracks(k, to, [((-8, 54, 9), (-3, 46, 9.6)), ((-3, 46, 9.6), (-6, 40, 8.6)), ((6, 52, 9.2), (10, 44, 8.4)),
                   ((2, 56, 9), (4, 49, 9.6)), ((-12, 50, 6), (-14, 44, 4)), ((-3, 46, 9.6), (3, 42, 8.6)),
                   ((10, 44, 8.4), (14, 40, 5)), ((-6, 58, -8), (-2, 48, -9)), ((5, 56, -8.6), (9, 46, -8))], w=1.8)
    k.box(to, C(0, 41, 8.4, 14, 1.2, 1.0), "bronze", tag="belt_strap")
    k.limb(to, (-17, 57, 4), (13, 38, 8.6), 2.8, "bronze", "baldric", d=0.8)
    for side in (1, -1):         # a bronze pauldron on one side, a mane on both
        if side > 0:
            k.blob(to, (side * 17, 57, 0), (8, 4.6, 8.4), "bronze", "pauldron")
            for i in range(3):
                k.box(to, C(side * (18 + i * 0.6), 54 - i * 2.2, 0, 10, 1.8, 14), "bronze", tag="lame")
    k.blob(to, (0, 60, -2), (17, 6, 11), "fur", "mane")
    for i in range(14):
        a = math.radians(-130 + i * 20)
        k.shard(to, (math.sin(a) * 14, 58, -2 + math.cos(a) * 9), (math.sin(a) * 0.6, -1, math.cos(a) * 0.6), 9 + (i % 3) * 2, 3.0,
                mat="fur", tag="mane_lock")
    # ---------------------------------------------------------------- the head: a bull's, the nose ring, the burning horns
    hd = k.part("head", (0, 60, 6), (("x", -14),), "torso")
    k.box(hd, C(0, 60, 6, 12, 11, 11), "obsidian", tag="skull")
    k.box(hd, C(0, 58, 15, 9.4, 7.4, 7.0), "obsidian", tag="muzzle")
    k.box(hd, C(0, 55.6, 15, 8.4, 2.4, 6.4), "obsidian", tag="jaw")
    for sx in (-2.2, 2.2):
        k.box(hd, C(sx, 61.2, 18.55, 2.0, 1.6, 0.4), "dark", tag="nostril")
        k.box(hd, C(sx * 1.8, 67.4, 11.6, 2.4, 1.2, 0.5), "eye", group="glow", tag="eye")
    k.ring(hd, 0, 58.8, 19.0, 2.6, 0.9, "bronze", "nose_ring", n=12, axis="x")
    k.box(hd, C(0, 69.4, 10, 11.6, 2.0, 3.6), "obsidian", tag="brow")
    cracks(k, hd, [((-3, 69, 11.8), (-1, 64, 11.8)), ((4, 66, 11.8), (3, 62, 11.8))])
    for side in (1, -1):
        horns(k, hd, (side * 5.6, 69, 6), side, s=3.0, burning=True)
        k.shard(hd, (side * 6.4, 64, 4.4), (side * 1, 0.2, -0.4), 3.0, 2.4, mat="obsidian", tag="ear")
    for (x, z, L) in ((-2, 18, 4), (2, 18, 5)):          # smoke from the nostrils
        k.limb(hd, (x, 61, z + 1), (x * 1.6, 63, z + 1 + L), 1.6, "ash", "smoke", d=1.2)
    # ---------------------------------------------------------------- arms: iron cuffs, broken chains, the labrys
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 19
        up = k.part("arm_" + nm, (x, 56, 0), (("x", -40 if side > 0 else -70), ("z", side * 14)), "torso")
        fo = k.part("fore_" + nm, (x, 42, 0), (("x", -40 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 28, 0), (), fo)
        k.blob(up, (x, 55, 0), (7.4, 6.0, 7.6), "obsidian", "shoulder")
        k.stack(up, x, 0, [(42, 9.4, 9.6), (50, 10.6, 10.8), (56, 11, 11.2)], "obsidian", "upper_arm")
        k.stack(fo, x, 0, [(29, 9.4, 9.6), (36, 10.2, 10.4), (42, 9.6, 9.8)], "obsidian", "forearm")
        cracks(k, up, [((x + side * 5, 52, 1), (x + side * 4.4, 45, 2))])
        k.box(fo, C(x, 30, 0, 11.6, 4.4, 11.8), "iron", tag="cuff")
        k.chain(fo, (x, 30, 5.6), (x + side * 3, 18, 9), 5, w=1.8)
        k.box(hn, C(x, 22, 0.6, 9.6, 7.4, 9.6), "obsidian", tag="fist")
    # the labrys: a long bronze-bound haft, two crescent heads, a spike between
    lb = k.part("labrys", (-19, 24, 0.6), (("x", 100), ("z", -20)), k.parts["hand_r"])
    k.limb(lb, (-19, 0, 0.6), (-19, 64, 0.6), 2.8, "horn", "haft")
    for y in (10, 22, 34, 46):
        k.box(lb, C(-19, y, 0.6, 3.6, 1.6, 3.6), "bronze", tag="haft_band")
    for sz in (-1, 1):
        pts = [(-19, 62, 0.6 + sz * 2), (-19, 68, 0.6 + sz * 11), (-19, 60, 0.6 + sz * 15), (-19, 52, 0.6 + sz * 11), (-19, 50, 0.6 + sz * 2)]
        for (a, b) in zip(pts, pts[1:]):
            k.limb(lb, a, b, 3.0, "bronze", "axe_head", d=2.0)
        for f in (0.3, 0.55, 0.8):
            k.limb(lb, (-19, 56, 0.6 + sz * 2), (-19, 59 + 4 * f, 0.6 + sz * (2 + 11 * f)), 3.4, "bronze", "axe_web", d=1.8)
        k.box(lb, C(-19, 52, 0.6 + (2 if sz > 0 else -13), 1.8, 14, 11), "bronze", tag="axe_blade")
        k.box(lb, C(-19, 54, 0.6 + (13 if sz > 0 else -15), 1.6, 10, 2), "bronze", tag="axe_blade")
        k.limb(lb, (-19, 68, 0.6 + sz * 11), (-19, 52, 0.6 + sz * 11), 1.0, "glow", "axe_edge", group="glow", d=2.2)
    k.shard(lb, (-19, 64, 0.6), (0, 1, 0), 7, 2.6, mat="bronze", tag="axe_spike")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Gatekeeper (elite, the key)

def gatekeeper():
    """The builders set a warden at the ninth door and cast him in bronze so he would last: a giant in bronze plate
    with the maze itself cast into it, a helm with a bull's horns and a grille for a face, a shield that is a
    bronze door off its hinges, and a sword whose blade is cut like a key. He has stood there a thousand years and
    the key to the ninth gate hangs at his throat."""
    k = X.Kit("gatekeeper")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(16, 14, 9.4), (22, 14.6, 9.8)], "bronze", "faulds")
    for x in (-4.6, 0, 4.6):
        k.box(hips, C(x, 12.4, 5.2, 4.2, 6.8, 1.0), "bronze", tag="tasset")
        k.box(hips, C(x, 14.4, 5.75, 2.4, 2.4, 0.3), "dark", tag="maze_cast")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.8
        th = k.part("thigh_" + nm, (x, 21, 0), (("x", -6), ("z", side * 5)), "hips")
        sh = k.part("shin_" + nm, (x, 11.4, 0), (("x", 10),), th)
        ft = k.part("foot_" + nm, (x, 2.8, 0), (("x", -4),), sh)
        k.box(th, C(x, 11.6, 0, 5.8, 9.6, 6.2), "bronze", tag="cuisse")
        k.box(th, C(x, 10.4, 1.0, 6.4, 3.0, 5.8), "bronze", tag="poleyn")
        k.box(sh, C(x, 2.8, 0, 5.8, 8.6, 6.2), "bronze", tag="greave")
        k.box(sh, C(x, 6, 3.15, 3.0, 3.0, 0.3), "dark", tag="maze_cast")
        k.box(ft, C(x, 0, 1.6, 6.2, 3.0, 9.0), "bronze", tag="foot")
    # ---------------------------------------------------------------- torso: the maze cast in the breastplate, the key at the throat
    to = k.part("torso", (0, 22, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(22, 14.6, 9.8), (28, 18, 11), (33, 20, 11.4), (37, 18, 10.4)], "bronze", "cuirass")
    for r in (5.0, 3.4, 1.8):                # the maze in the breastplate: three square rings, gaps cut
        for (dx, dy, w, h) in ((0, r, r * 2, 0.5), (0, -r, r * 2, 0.5), (r, 0, 0.5, r * 2), (-r, 0, 0.5, r * 2)):
            k.box(to, C(dx, 29 + dy - h / 2, 5.65, w, h, 0.4), "dark", tag="maze_cast")
    k.box(to, C(0, 28.8, 5.8, 1.2, 1.2, 0.5), "glow", group="glow", tag="maze_heart")
    k.limb(to, (-3, 36.6, 4.6), (0, 33, 6.4), 0.5, "iron", "key_chain")
    k.limb(to, (3, 36.6, 4.6), (0, 33, 6.4), 0.5, "iron", "key_chain")
    k.box(to, C(0, 30.4, 6.4, 1.2, 2.8, 0.6), "glow", group="glow", tag="key")
    for side in (1, -1):
        k.blob(to, (side * 11, 36.4, 0), (6.4, 4.0, 6.6), "bronze", "pauldron")
        for i in range(3):
            k.box(to, C(side * (11.6 + i * 0.4), 33.6 - i * 2.0, 0, 7.6, 1.8, 11), "bronze", tag="lame")
    # ---------------------------------------------------------------- the helm: horns, a grille for a face
    hd = k.part("head", (0, 37, 0.4), (("x", -6),), "torso")
    k.box(hd, C(0, 37, 0.2, 7.4, 8.4, 7.6), "bronze", tag="helm")
    k.box(hd, C(0, 38.6, 3.95, 5.4, 5.0, 0.4), "dark", tag="grille_back")
    for x in (-2, -1, 0, 1, 2):
        k.box(hd, C(x, 38.6, 4.1, 0.4, 5.0, 0.4), "bronze", tag="grille")
    for sx in (-1.4, 1.4):
        k.box(hd, C(sx, 41.4, 4.0, 1.4, 0.6, 0.3), "eye", group="glow", tag="eye")
    for side in (1, -1):
        horns(k, hd, (side * 3.6, 43, 0.2), side, s=1.0, mat="bronze")
    # ---------------------------------------------------------------- arms: the door shield, the key-blade
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 11
        up = k.part("arm_" + nm, (x, 35, 0), (("x", -40 if side > 0 else -30), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 26, 0), (("x", -50 if side > 0 else -60),), up)
        hn = k.part("hand_" + nm, (x, 17, 0), (), fo)
        k.box(up, C(x, 26.6, 0, 5.4, 8.6, 5.6), "bronze", tag="rerebrace")
        k.box(fo, C(x, 17.6, 0, 5.4, 8.6, 5.6), "bronze", tag="vambrace")
        k.box(hn, C(x, 13.8, 0.4, 5.0, 4.0, 5.0), "bronze", tag="gauntlet")
    dr = k.part("door_shield", (14.6, 17, 2), (("y", 8),), k.parts["hand_l"])
    k.box(dr, C(15, 2, 2, 1.6, 34, 16), "bronze", tag="door")
    for y in (6, 18, 30):
        k.box(dr, C(15.9, y, 2, 0.6, 2.0, 16.4), "iron", tag="door_band")
    for z in (-5.4, 9.4):
        k.ring(dr, 15.9, 12 if z < 0 else 26, z, 1.6, 0.5, "iron", "hinge", n=8, axis="x")
    k.box(dr, C(16.0, 15, 2, 0.4, 6, 6), "dark", tag="maze_cast")
    k.box(dr, C(16.1, 17, 4, 0.4, 2, 2), "glow", group="glow", tag="keyhole")
    kb = k.part("key_blade", (-11, 15.6, 0.6), (("x", 80),), k.parts["hand_r"])
    k.ring(kb, -11, 9.6, 0.6, 2.4, 0.8, "bronze", "key_bow", n=10, axis="x")
    k.box(kb, C(-11, 12, 0.6, 1.6, 6.0, 1.6), "bronze", tag="grip")
    k.box(kb, C(-11, 18, 0.6, 1.8, 1.4, 8.0), "bronze", tag="guard")
    k.box(kb, C(-11, 19.4, 0.6, 1.0, 26, 3.6), "bronze", tag="blade")
    for (y, dz, h) in ((38, 3.2, 3), (40.6, 2.6, 2), (43, 3.6, 2.6)):        # the key bits cut in the blade's end
        k.box(kb, C(-11, y, 0.6 + dz, 1.0, h, 3.4), "bronze", tag="key_bit")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Basalt Ogre (brute)

def basalt_ogre():
    """The maze grew its own guards out of the rock: an ogre made of basalt columns, the six-sided stone stacked
    and fused into a body, the magma glowing in every joint between them. Its head is a broken column with two
    coals in it; its fists are column-ends. It tears a column out of the maze wall to use as a club."""
    k = X.Kit("basalt_ogre")
    hips = k.part("hips", (0, 22, 0))
    for (x, z, h) in ((-4, 2, 7), (0, -2, 8), (4, 2, 7), (0, 3, 6)):
        k.box(hips, C(x, 15, z, 5.4, h, 5.4), "basalt", tag="column")
    k.box(hips, C(0, 21, 0, 15, 1.4, 11), "glow", group="glow", tag="joint")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.0
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -10), ("z", side * 10)), "hips")
        sh = k.part("shin_" + nm, (x, 11, 0), (("x", 16),), th)
        ft = k.part("foot_" + nm, (x, 3, 0), (("x", -6),), sh)
        k.box(th, C(x, 11.6, 0, 7.4, 8.6, 7.4), "basalt", tag="column")
        k.box(th, C(x, 11.0, 0, 6.6, 0.8, 6.6), "glow", group="glow", tag="joint")
        k.box(sh, C(x, 3.4, 0, 7.0, 7.6, 7.0), "basalt", tag="column")
        k.box(ft, C(x, 0, 1.8, 8.6, 3.4, 11), "basalt", tag="foot")
        k.box(ft, C(x, 3.0, 1.8, 7.6, 0.6, 10), "glow", group="glow", tag="joint")
    # ---------------------------------------------------------------- torso: a cluster of columns, glowing at the joins
    to = k.part("torso", (0, 22, 0), (("x", 18),), "hips")
    for (x, z, y0, h, w) in ((-6, 0, 22, 14, 7), (0, 1, 22, 17, 8), (6, 0, 22, 15, 7), (-3, -4, 24, 14, 6), (3, -4, 24, 15, 6),
                             (-9, -2, 30, 10, 6), (9, -2, 30, 10, 6), (0, 5, 26, 10, 6)):
        k.box(to, C(x, y0, z, w, h, w), "basalt", tag="column")
        k.box(to, C(x, y0 + h - 0.6, z, w + 0.2, 0.8, w + 0.2), "glow", group="glow", tag="joint")
    for (x, z, L) in ((-4, -6, 8), (2, -7, 11), (7, -5, 6)):          # columns standing up off its back
        k.box(to, C(x, 36, z, 4.0, L, 4.0), "basalt", tag="back_column")
    # ---------------------------------------------------------------- the head: a broken column, two coals
    hd = k.part("head", (0, 38, 3), (("x", -16),), "torso")
    k.box(hd, C(0, 37, 4, 8, 9, 8), "basalt", tag="head_column")
    k.box(hd, C(1, 46, 3, 5, 2, 5), "basalt", tag="broken_top")
    k.box(hd, C(0, 37.6, 8.05, 6.0, 1.6, 0.4), "glow", group="glow", tag="mouth_crack")
    for sx in (-1.8, 1.8):
        k.box(hd, C(sx, 41.6, 8.1, 1.8, 1.4, 0.4), "eye", group="glow", tag="eye")
    # ---------------------------------------------------------------- arms: columns, the column club
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 14
        up = k.part("arm_" + nm, (x, 36, 0), (("x", -10 if side > 0 else -80), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 25, 0), (("x", -20 if side > 0 else -30),), up)
        hn = k.part("hand_" + nm, (x, 14, 0), (), fo)
        k.box(up, C(x, 25.4, 0, 7.6, 10, 7.6), "basalt", tag="column")
        k.box(up, C(x, 25, 0, 7.0, 0.8, 7.0), "glow", group="glow", tag="joint")
        k.box(fo, C(x, 14.4, 0, 8.4, 10, 8.4), "basalt", tag="column")
        k.box(hn, C(x, 7.4, 0.6, 9.4, 7.0, 9.4), "basalt", tag="fist")
        k.box(hn, C(x, 13.6, 0.6, 8.8, 0.8, 8.8), "glow", group="glow", tag="joint")
    cl = k.part("column_club", (-14, 10, 0.6), (("x", 60),), k.parts["hand_r"])
    k.box(cl, C(-14, 2, 0.6, 5.6, 34, 5.6), "basalt", tag="club_column")
    k.box(cl, C(-14, 34, 0.6, 7.0, 6, 7.0), "basalt", tag="club_column")
    for y in (12, 22, 33.6):
        k.box(cl, C(-14, y, 0.6, 6.2, 0.6, 6.2), "glow", group="glow", tag="joint")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Ember Oracle (caster)

def ember_oracle():
    """The oracles of the maze see the way through it with their eyes burned out: a cloth bound round the face with
    runes glowing on it, small curled horns through a hood of ash-grey, a robe singed at the hem, and a tripod staff
    with a bronze bowl of embers at its top that they read the turns in - and throw."""
    k = X.Kit("ember_oracle")
    hips = k.part("hips", (0, 19, 0))
    k.stack(hips, 0, 0, [(1, 11, 8.4), (10, 10, 7.2), (19, 9, 6.4)], "ash", "robe")
    k.box(hips, C(0, 1.4, 0, 11.4, 2.0, 8.8), "dark", tag="singed_hem")
    for (x, z) in ((-4, 3.8), (3, 4), (0, -4)):
        k.box(hips, C(x, 2.6, z, 1.6, 0.8, 0.6), "glow", group="glow", tag="ember_spot")
    k.box(hips, C(0, 18.6, 0, 9.8, 1.8, 7.0), "bronze", tag="belt")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 19, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 10, 0), (), th)
        ft = k.part("foot_" + nm, (x, 2, 0), (), sh)
        k.box(ft, C(x, 0, 1.8, 3.0, 1.4, 5.0), "horn", tag="foot")
    # ---------------------------------------------------------------- torso
    to = k.part("torso", (0, 19, 0), (("x", 12),), "hips")
    k.stack(to, 0, 0, [(19, 9, 6.4), (25, 11, 7.0), (31, 12, 7.0)], "ash", "robe")
    k.stack(to, 0, -0.4, [(26, 14.4, 9), (31, 14.8, 9.2), (33, 12, 8)], "cloth", "mantle")
    for i, x in enumerate((-3, -1, 1, 3)):
        k.box(to, C(x, 26.6 + abs(x) * 0.4, 4.0, 1.0, 1.6, 0.6), "bone", tag="charm")
    # ---------------------------------------------------------------- the head: the hood, horns, the burning blindfold
    hd = k.part("head", (0, 31, 0.8), (("x", -12),), "torso")
    k.box(hd, C(0, 30.6, 0.4, 6.4, 7.0, 6.6), "ash", tag="hood")
    k.box(hd, C(0, 31.0, 3.6, 4.6, 5.0, 0.8), "obsidian", tag="face")
    k.box(hd, C(0, 33.4, 3.95, 5.0, 1.6, 0.6), "cloth", tag="blindfold")
    for x in (-1.6, -0.4, 0.8, 1.8):
        k.box(hd, C(x, 33.6, 4.3, 0.6, 1.0, 0.3), "glow", group="glow", tag="rune")
    k.box(hd, C(0, 31.6, 3.95, 1.8, 0.5, 0.3), "dark", tag="mouth")
    for side in (1, -1):
        pts = [(side * 2.8, 36.4, 0.4), (side * 4.4, 37.6, -0.6), (side * 5.0, 36.4, -1.8), (side * 4.4, 35.0, -1.0)]
        for (a, b), w in zip(zip(pts, pts[1:]), (1.4, 1.1, 0.8)):
            k.limb(hd, a, b, w, "horn", "horn")
    # ---------------------------------------------------------------- arms and the tripod staff with the bowl of embers
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.0
        up = k.part("arm_" + nm, (x, 29.6, 0), (("x", -60 if side > 0 else -40), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 21.6, 0), (("x", -50 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 13.8, 0), (), fo)
        k.box(up, C(x, 21.4, 0, 3.8, 8.4, 4.0), "ash", tag="sleeve")
        k.stack(fo, x, 0, [(13.4, 6.0, 6.0), (21.6, 4.0, 4.0)], "ash", "sleeve")
        k.box(hn, C(x, 11.4, 0.4, 2.6, 2.8, 2.6), "obsidian", tag="hand")
        if side > 0:
            k.blob(hn, (x, 12.6, 2.4), (1.2, 1.2, 1.2), "glow", "ember_in_hand", step=0.6)
    st = k.part("tripod_staff", (-7, 12.6, 0.8), (("x", 70),), k.parts["hand_r"])
    k.limb(st, (-7, -8, 0.8), (-7, 28, 0.8), 1.2, "horn", "staff")
    for a in (0, 120, 240):
        r = math.radians(a)
        k.limb(st, (-7, 26, 0.8), (-7 + math.cos(r) * 2.4, 31, 0.8 + math.sin(r) * 2.4), 0.6, "bronze", "tripod_leg")
    k.blob(st, (-7, 31.6, 0.8), (3.0, 1.4, 3.0), "bronze", "ember_bowl", step=0.6)
    k.blob(st, (-7, 32.6, 0.8), (2.4, 1.0, 2.4), "glow", "embers", step=0.6)
    for (x, z, L) in ((-0.6, 0.4, 4), (0.8, -0.4, 5)):
        k.shard(st, (-7 + x, 33, 0.8 + z), (x * 0.2, 1, z * 0.2), L, 1.0, mat="glow", tag="flame", group="glow")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Horned Runner (skirmisher)

def horned_runner():
    """The runners hunt the maze for whoever gets lost in it: goat-legged, bull-horned, a mane down the spine,
    bronze bands on the arms, a leather harness, and two short bronze axes - little labryses - that they throw
    round corners and catch again."""
    k = X.Kit("horned_runner")
    hips = k.part("hips", (0, 19, 0))
    k.box(hips, C(0, 16.6, 0, 7.6, 3.6, 5.0), "fur", tag="hips")
    k.box(hips, C(0, 18.8, 0, 8.2, 1.4, 5.6), "bronze", tag="belt")
    k.box(hips, C(0, 12.6, 2.6, 5.6, 6, 0.8), "cloth", tag="loincloth")
    tail = [(0, 17, -2.6), (0, 14, -5), (0, 10, -6)]
    for (a, b) in zip(tail, tail[1:]):
        k.limb(hips, a, b, 1.0, "fur", "tail")
    k.blob(hips, (0, 9.4, -6.2), (1.0, 1.4, 1.0), "fur", "tail_tuft", step=0.6)
    for side, nm in ((1, "l"), (-1, "r")):       # goat's legs: back-bent hocks, hooves
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 19, 0), (("x", -34), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 12, 0), (("x", 64),), th)
        ft = k.part("foot_" + nm, (x, 5, 0), (("x", -36),), sh)
        k.stack(th, x, 0, [(12, 3.4, 3.8), (16, 4.4, 4.8), (19, 4.0, 4.4)], "fur", "thigh")
        k.box(sh, C(x, 5, -0.4, 2.4, 7.0, 2.6), "fur", tag="shin")
        k.box(ft, C(x, 0, 0.4, 2.4, 5.0, 2.4), "fur", tag="foot")
        k.box(ft, C(x, 0, 1.0, 2.8, 1.6, 3.0), "horn", tag="foot")
    # ---------------------------------------------------------------- torso: lean, a harness, a mane down the spine
    to = k.part("torso", (0, 19, 0), (("x", 26),), "hips")
    k.stack(to, 0, 0, [(19, 7.6, 5.0), (24, 9.2, 5.8), (29, 11, 6.0)], "obsidian", "torso")
    for sx in (-1, 1):
        k.limb(to, (sx * 4.8, 29, 3.0), (-sx * 3.4, 20, 3.0), 1.0, "cloth", "harness", d=0.4)
    for i in range(6):
        k.shard(to, (0, 20 + i * 1.8, -2.8), (0, 0.4, -1), 2.6, 1.6, mat="fur", tag="mane")
    cracks(k, to, [((-2, 27, 3.0), (-1, 22, 3.0))], w=0.5)
    # ---------------------------------------------------------------- the head: a bull's snout, the horns
    hd = k.part("head", (0, 29.6, 0.8), (("x", -22),), "torso")
    k.box(hd, C(0, 30.0, 1.0, 4.8, 5.0, 5.0), "obsidian", tag="head")
    k.box(hd, C(0, 29.4, 4.6, 3.6, 2.8, 3.0), "obsidian", tag="snout")
    k.ring(hd, 0, 29.4, 6.2, 0.9, 0.4, "bronze", "nose_ring", n=8, axis="x")
    for sx in (-1.2, 1.2):
        k.box(hd, C(sx, 33.0, 3.55, 1.0, 0.6, 0.3), "eye", group="glow", tag="eye")
    for side in (1, -1):
        horns(k, hd, (side * 2.4, 34, 1.0), side, s=0.7)
    # ---------------------------------------------------------------- arms and the two hand-axes
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.8
        up = k.part("arm_" + nm, (x, 27.4, 0), (("x", -40 if side > 0 else -110), ("z", side * 20)), "torso")
        fo = k.part("fore_" + nm, (x, 20.6, 0), (("x", -60 if side > 0 else -10),), up)
        hn = k.part("hand_" + nm, (x, 13.6, 0), (), fo)
        k.box(up, C(x, 20.8, 0, 3.0, 7.0, 3.2), "obsidian", tag="arm")
        k.box(fo, C(x, 13.8, 0, 2.8, 7.2, 3.0), "obsidian", tag="forearm")
        k.box(fo, C(x, 17.0, 0, 3.4, 1.4, 3.6), "bronze", tag="arm_band")
        k.box(hn, C(x, 11.2, 0.3, 2.6, 2.6, 2.6), "obsidian", tag="hand")
        ax = k.part("axe_" + nm, (x, 12.2, 0.4), (("x", 80),), hn)
        k.limb(ax, (x, 9, 0.4), (x, 20, 0.4), 0.9, "horn", "axe_haft")
        for sz in (-1, 1):
            k.box(ax, C(x, 16.4, 0.4 + sz * 2.2, 0.6, 4.4, 3.0), "bronze", tag="axe_head")
            k.box(ax, C(x, 15.8, 0.4 + sz * 3.8, 0.7, 5.6, 0.8), "bronze", tag="axe_edge")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Labyrinth Imp (swarm)

def labyrinth_imp():
    """The maze breeds imps in its cracks: knee-high things of black glass, the magma showing through every crack
    in their skin, little curled horns, bat-wings too small to fly with, a barbed tail, and a grin of glass teeth.
    They come screaming round the corners in packs."""
    k = X.Kit("labyrinth_imp")
    hips = k.part("hips", (0, 9, 0))
    k.box(hips, C(0, 7.6, 0, 4.4, 2.6, 3.4), "obsidian", tag="hips")
    tail = [(0, 8.6, -1.6), (0, 7, -4), (0, 8, -7), (0, 10.6, -8.4)]
    for (a, b), w in zip(zip(tail, tail[1:]), (0.9, 0.7, 0.6)):
        k.limb(hips, a, b, w, "obsidian", "tail")
    k.shard(hips, (0, 10.6, -8.4), (0, 0.6, -0.4), 2.4, 1.6, mat="glow", tag="tail_barb", group="glow")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 1.4
        th = k.part("thigh_" + nm, (x, 8.6, 0), (("x", -30), ("z", side * 10)), "hips")
        sh = k.part("shin_" + nm, (x, 5, 0), (("x", 50),), th)
        ft = k.part("foot_" + nm, (x, 1.4, 0), (("x", -20),), sh)
        k.box(th, C(x, 5.2, 0, 1.8, 3.6, 2.0), "obsidian", tag="thigh")
        k.box(sh, C(x, 1.4, 0, 1.4, 3.8, 1.6), "obsidian", tag="shin")
        k.box(ft, C(x, 0, 0.8, 1.8, 1.4, 3.0), "obsidian", tag="foot")
        k.shard(ft, (x, 0.4, 2.2), (0, -0.3, 1), 1.0, 0.5, mat="glow", tag="foot", group="glow")
    # ---------------------------------------------------------------- torso: hunched, cracked, the little wings
    to = k.part("torso", (0, 9, 0), (("x", 20),), "hips")
    k.blob(to, (0, 12, 0.4), (3.0, 3.4, 2.6), "obsidian", "body", step=0.6)
    cracks(k, to, [((-1.2, 14, 2.4), (0, 11, 2.8)), ((1.4, 13, 2.2), (0.6, 10, 2.6))], w=0.4)
    for side in (1, -1):
        root = (side * 1.4, 14, -2)
        for (dx, dy) in ((4.0, 3.0), (5.0, 0.4), (3.4, -2.0)):
            k.limb(to, root, (root[0] + side * dx, root[1] + dy, -3.4), 0.5, "obsidian", "wing_bone")
        k.limb(to, root, (root[0] + side * 4.0, root[1] + 0.6, -3.4), 2.4, "cloth", "wing_membrane", d=0.3)
    # ---------------------------------------------------------------- the head: a big grin, curled horns
    hd = k.part("head", (0, 15, 0.8), (("x", -16),), "torso")
    k.box(hd, C(0, 15, 1.0, 4.4, 3.8, 4.0), "obsidian", tag="head")
    k.box(hd, C(0, 15.6, 3.05, 3.4, 1.0, 0.4), "glow", group="glow", tag="grin")
    for t in (-1.2, -0.6, 0, 0.6, 1.2):
        k.box(hd, C(t, 16.0, 3.2, 0.3, 0.5, 0.2), "obsidian", tag="tooth")
    for sx in (-1.0, 1.0):
        k.box(hd, C(sx, 17.6, 3.05, 0.9, 0.6, 0.3), "eye", group="glow", tag="eye")
    for side in (1, -1):
        pts = [(side * 1.6, 18.6, 1.0), (side * 2.8, 20.0, 0.4), (side * 3.0, 21.0, -0.8)]
        for (a, b) in zip(pts, pts[1:]):
            k.limb(hd, a, b, 0.8, "horn", "horn")
    # ---------------------------------------------------------------- arms: long, clawed
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.4
        up = k.part("arm_" + nm, (x, 14, 0), (("x", -60), ("z", side * 20)), "torso")
        fo = k.part("fore_" + nm, (x, 10.4, 0), (("x", -30),), up)
        hn = k.part("hand_" + nm, (x, 6.8, 0), (), fo)
        k.box(up, C(x, 10.6, 0, 1.4, 3.6, 1.6), "obsidian", tag="arm")
        k.box(fo, C(x, 7.0, 0, 1.3, 3.6, 1.5), "obsidian", tag="forearm")
        k.box(hn, C(x, 5.6, 0.2, 1.6, 1.6, 1.6), "obsidian", tag="hand")
        for t in (-0.5, 0.5):
            k.shard(hn, (x + t, 5.6, 0.6), (0, -1, 0.4), 1.8, 0.5, mat="glow", tag="claw", group="glow")
    k.s.shaders = shaders()
    return k.s, k.parts


MOBS = {
    "labyrinth_imp": dict(make=labyrinth_imp, ent=(0.6, 1.4), stats=dict(hp=30, speed=0.36, dmg=7, armor=4, kb=0)),
    "basalt_ogre": dict(make=basalt_ogre, ent=(1.7, 4.0), stats=dict(hp=130, speed=0.18, dmg=17, armor=14, kb=1.0)),
    "ember_oracle": dict(make=ember_oracle, ent=(0.9, 2.9), stats=dict(hp=48, speed=0.21, dmg=8, armor=3, kb=0)),
    "horned_runner": dict(make=horned_runner, ent=(0.9, 2.8), stats=dict(hp=42, speed=0.38, dmg=9, armor=4, kb=0)),
    "gatekeeper": dict(make=gatekeeper, ent=(1.4, 3.6), stats=dict(hp=250, speed=0.2, dmg=15, armor=16, kb=0.6), key=True),
    "minotaur": dict(make=minotaur, texel=1, ent=(3.0, 6.8), stats=dict(hp=700, speed=0.25, dmg=24, armor=12, kb=1.2), boss=True),
}
