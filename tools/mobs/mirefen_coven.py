"""The Mirefen Coven's monsters, each built by hand (tools/vox2.py). The drowned fen where the hags keep their huts:
black mud and peat, moss and reeds, the tanned leather of bodies the bog kept, grey hag-hair, willow bark, bone
charms, and the witchlight - a sour green that burns in cauldrons and in eyes.

    mire_thrall     swarm   a bog body walking: tanned leather skin, the noose still on, a hex stake glowing through the chest
    bog_troll       brute   a troll with a mound of bog on its back and a dead willow growing out of it, a root-club
    hag_sister      caster  a crook-backed hag: a nose like a hook, a cage with a will-o'-the-wisp in it, a ladle
    fen_crawler     skirm   a moss-backed bog spider with a toad's face, egg sacs glowing on its back (the spider's bones)
    coven_matron    elite   the matron: a hat with candles on the brim, a bark mask, a toad familiar, a cauldron-spoon staff
    mother_mire     boss    Mother Mire: risen out of the bog to the waist, moss hair, a crown of antler-branches and charms,
                            three eyes, her cauldron chained on her back, a staff with a skull lantern

    python tools/monsterforge.py mirefen_coven --preview ; python tools/mobsheet.py mirefen_coven
"""
import math

import vox2 as X
from vox2 import C, ramp

MUD = ramp("#0a0906", "#12100a", "#1c180e", "#282214", "#342c1a", "#423822")
MOSS = ramp("#0e1a08", "#16280c", "#203812", "#2c4a18", "#3a5e20", "#4a7228")
BOGSKIN = ramp("#1a0e06", "#2a180a", "#3c240e", "#4e3214", "#62421c", "#785426")
TROLL = ramp("#141a10", "#1e2616", "#2a341e", "#384428", "#465432")
HAIR = ramp("#2a2a26", "#3e3e38", "#56564e", "#706e64", "#8a887c")
BARK = ramp("#100a06", "#1a120a", "#261a10", "#342416", "#44301c")
BONE = ramp("#3a3428", "#5a5240", "#7c7258", "#9e9476", "#c0b896")
WITCH = ramp("#1a4a10", "#2a7a1a", "#44b02a", "#7ce04a", "#c4ff9a")
CLOTH = ramp("#16120c", "#221c14", "#2e261c", "#3a3024", "#463c2e")
IRON = ramp("#0c0c0c", "#161616", "#222220", "#30302c", "#40403a")
RUST = ramp("#2a1408", "#44200c", "#5e2e12", "#7a3e18")
WAX = ramp("#4a4434", "#6a6248", "#8a8060", "#aaa07c", "#c8be98")
FLAME = ramp("#5a7a0a", "#8ab014", "#bce040", "#e4ff90", "#faffe0")
TOAD = ramp("#1a1e08", "#2a3010", "#3c4418", "#505a22", "#66722e")
REED = ramp("#2a2a12", "#3a3a18", "#4e4e20", "#64642a", "#7a7a34")


def shaders():
    return {
        "mud": X.surf(MUD, 0.5, 1.2, 0.34, 0.0, crust=(MOSS, 0.2), drip=(MUD, 0.3)),
        "moss": X.surf(MOSS, 0.5, 1.1, 0.34, 0.0, stripe=2),
        "bogskin": X.wrinkled(BOGSKIN, 1.0),
        "troll": X.surf(TROLL, 0.5, 1.2, 0.34, 0.0, crust=(MOSS, 0.26), rust=(MUD, 0.16, 0.4)),
        "hair": X.surf(HAIR, 0.5, 1.0, 0.3, 0.0, stripe=2),
        "bark": X.surf(BARK, 0.5, 1.1, 0.24, 0.06, stripe=3, crust=(MOSS, 0.14)),
        "bone": X.surf(BONE, 0.6, 1.1, 0.16, 0.12),
        "glow": X.glow(WITCH),
        "eye": X.glow(WITCH, 0.82, 0.16),
        "cloth": X.surf(CLOTH, 0.48, 1.0, 0.24, 0.0, holes=True, drip=(MUD, 0.24)),
        "iron": X.surf(IRON, 0.5, 1.3, 0.16, 0.14, rust=(RUST, 0.36, 0.4)),
        "wax": X.surf(WAX, 0.6, 0.8, 0.1, 0.1),
        "flame": X.glow(FLAME, 0.7, 0.3),
        "toad": X.wrinkled(TOAD, 1.2),
        "reed": X.surf(REED, 0.5, 1.0, 0.2, 0.0, stripe=2),
        "rope": X.surf(REED, 0.42, 1.0, 0.2, 0.0, stripe=2),
        "dark": X.dark(MUD),
    }


def strands(k, part, root_pts, L, w=1.2, mat="moss", tag="moss", sway=0.3):
    """hanging moss / hair: a strand down from each point, two segments with a little sway"""
    for i, (x, y, z) in enumerate(root_pts):
        s = sway * (1 if i % 2 else -1)
        mid = (x + s, y - L * 0.5, z + abs(s) * 0.5)
        k.limb(part, (x, y, z), mid, w, mat, tag, d=w * 0.6)
        k.limb(part, mid, (x - s * 0.5, y - L * (0.8 + 0.2 * (i % 3) / 2), z + abs(s)), w * 0.7, mat, tag, d=w * 0.5)


def branch(k, part, base, d, length, w, mat="bark", tag="branch", forks=2, seed=1):
    """a dead branch: a crooked limb that forks twice"""
    n = math.sqrt(sum(c * c for c in d))
    d = [c / n for c in d]
    tip = tuple(base[i] + d[i] * length for i in range(3))
    k.limb(part, base, tip, w, mat, tag)
    if forks > 0:
        for s in (-1, 1):
            nd = (d[0] + s * 0.6 * math.cos(seed), d[1] + 0.3, d[2] + s * 0.6 * math.sin(seed))
            branch(k, part, tip, nd, length * 0.6, w * 0.65, mat, tag, forks - 1, seed + 1.3)


# ================================================================ Mother Mire (boss)

def mother_mire():
    """The first of the coven, who drowned herself in the fen to live forever and did. She rises out of it to the
    waist - below that she is bog, a great skirt of mud and roots that drags and drips - a gaunt, long-armed hag
    six blocks high. Her hair is the moss of the fen hanging to the ground; her crown is dead willow branches and
    elk antlers, hung with charms, bones and little lanterns. Her face is long, a nose like a hook, a mouth sewn
    shut with root, and three eyes in a row that burn witch-green. Her cauldron is chained to her back, still
    bubbling. She leans on a crooked staff with a skull lantern, and reaches with the other hand - fingers like
    roots, a yard long."""
    k = X.Kit("mother_mire")
    hips = k.part("hips", (0, 36, 0))
    # the skirt of bog: a great mound of mud and roots from the waist to the ground, wider at the bottom
    k.stack(hips, 0, 0, [(0, 46, 40), (6, 42, 36), (14, 34, 28), (24, 26, 21), (36, 20, 15)], "mud", "bog_skirt", step=1.2)
    for a in range(0, 360, 24):          # roots spilling out of it over the ground
        r = math.radians(a)
        k.limb(hips, (math.sin(r) * 12, 12, math.cos(r) * 10), (math.sin(r) * 26, 1.0, math.cos(r) * 22), 2.4, "bark", "root")
    for a in range(10, 360, 40):         # reeds growing out of the mud
        r = math.radians(a)
        for dz in (-1, 1):
            k.limb(hips, (math.sin(r) * 16 + dz, 8, math.cos(r) * 14), (math.sin(r) * 18 + dz, 22, math.cos(r) * 15.4), 0.8, "reed", "reed")
    for (x, z) in ((-12, 14), (10, 15), (16, -6), (-15, -10), (2, 18)):
        k.box(hips, C(x, 3, z, 3.0, 1.6, 3.0), "glow", group="glow", tag="bog_light")
    for side, nm in ((1, "l"), (-1, "r")):   # the legs are inside the bog: bones for the rig, nothing to see
        x = side * 6
        th = k.part("thigh_" + nm, (x, 32, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 18, 0), (), th)
        ft = k.part("foot_" + nm, (x, 4, 0), (), sh)
        k.box(ft, C(x, 0, 2, 8, 2, 10), "mud", tag="foot")
    # ---------------------------------------------------------------- torso: gaunt, bent, ribs under the bog-skin, a shawl
    to = k.part("torso", (0, 36, 0), (("x", 22),), "hips")
    k.stack(to, 0, 0, [(36, 16, 11), (44, 15, 10), (52, 19, 11), (58, 22, 12)], "bogskin", "torso")
    for y in (44, 47, 50):
        k.box(to, C(0, y, 5.4, 12, 1.0, 0.8), "dark", tag="rib")
    k.stack(to, 0, -0.4, [(46, 24, 14), (54, 26, 15), (59, 23, 14)], "cloth", "shawl")
    for (x, z, L) in ((-11, 4, 10), (-6, 7, 14), (6, 7, 12), (11, 4, 9), (-9, -7, 12), (9, -7, 14)):
        k.limb(to, (x, 46, z), (x * 1.1, 46 - L, z * 1.1), 3.0, "cloth", "shawl_rag", d=0.6)
    k.box(to, C(0, 52, 7.6, 3.0, 3.0, 1.0), "bone", tag="brooch_skull")
    # the cauldron chained on her back, still bubbling
    k.blob(to, (0, 50, -14), (9, 7, 8), "iron", "cauldron", step=1.0)
    k.box(to, C(0, 56.4, -14, 17, 1.6, 15), "iron", tag="cauldron_rim")
    k.box(to, C(0, 57.0, -14, 14, 0.8, 12), "glow", group="glow", tag="brew")
    for (x, z, s) in ((-3, -13, 1.8), (2, -16, 1.4), (4, -12, 1.0)):
        k.blob(to, (x, 58.4, z), (s, s, s), "glow", "bubble", step=0.6)
    for sx in (-1, 1):
        k.chain(to, (sx * 8, 56, -10), (sx * 10, 58, -1), 4, w=1.4)
    k.limb(to, (-6, 58, -16), (-8, 72, -20), 1.4, "glow", "steam", group="glow", d=0.4)
    k.limb(to, (3, 58, -12), (4, 70, -18), 1.2, "glow", "steam", group="glow", d=0.4)
    # ---------------------------------------------------------------- the head: long face, hook nose, sewn mouth, three eyes
    hd = k.part("head", (0, 58, 3), (("x", -24),), "torso")
    k.box(hd, C(0, 58.6, 3, 9.0, 12.0, 9.0), "bogskin", tag="face")
    k.box(hd, C(0, 66.6, 7.8, 9.4, 2.0, 1.6), "bogskin", tag="brow")
    k.shard(hd, (0, 65.6, 7.6), (0, -0.7, 1), 9.0, 2.6, mat="bogskin", tag="nose")
    k.box(hd, C(0, 61.0, 7.6, 5.4, 1.0, 0.4), "dark", tag="mouth")
    for t in range(5):
        k.box(hd, C(-2.0 + t, 60.4, 7.8, 0.4, 2.2, 0.4), "bark", tag="stitch")
    for sx in (-2.8, 0, 2.8):
        k.box(hd, C(sx, 65.0 if sx else 64.4, 7.6, 2.0, 1.2, 0.5), "dark", tag="socket")
        k.box(hd, C(sx, 65.2 if sx else 64.6, 7.9, 1.4, 0.8, 0.3), "eye", group="glow", tag="eye")
    # the moss hair, to the ground behind and over the shoulders
    strands(k, hd, [(x, 70, z) for x in (-5, -3, -1, 1, 3, 5) for z in (-3, 0)], 30, w=2.4, sway=1.6)
    strands(k, hd, [(sx * 5, 66, 6) for sx in (-1, 1)], 22, w=2.0, sway=0.8)
    # the crown: dead willow branches and antlers, hung with charms and lanterns
    for i, (sx, lean) in enumerate(((-1, -0.7), (1, 0.7), (-1, -0.3), (1, 0.3))):
        branch(k, hd, (sx * 3, 70, 1 + (i // 2) * -2), (lean, 1, -0.2), 9 + 2 * (i % 2), 1.6, mat="bone" if i < 2 else "bark", seed=i)
    for (x, y, z, L, lit) in ((-9, 82, 0, 4, True), (8, 84, -1, 6, False), (-4, 86, -2, 3, False), (11, 80, 1, 5, True)):
        k.limb(hd, (x, y, z), (x, y - L, z), 0.3, "rope", "cord")
        if lit:
            k.box(hd, C(x, y - L - 2.4, z, 2.0, 2.4, 2.0), "iron", tag="lantern")
            k.box(hd, C(x, y - L - 2.0, z, 2.2, 1.6, 1.6), "glow", group="glow", tag="lantern_glass")
        else:
            k.box(hd, C(x, y - L - 1.6, z, 1.6, 1.8, 1.4), "bone", tag="charm_skull")
    # ---------------------------------------------------------------- arms: a yard long, root fingers
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 13
        up = k.part("arm_" + nm, (x, 56, 0), (("x", -60 if side > 0 else -30), ("z", side * 18)), "torso")
        fo = k.part("fore_" + nm, (x, 40, 0), (("x", -30 if side > 0 else -50),), up)
        hn = k.part("hand_" + nm, (x, 24, 0), (), fo)
        k.stack(up, x, 0, [(40, 4.4, 4.6), (48, 5.0, 5.2), (56, 6.0, 6.0)], "bogskin", "upper_arm")
        k.stack(fo, x, 0, [(24, 4.0, 4.0), (32, 4.6, 4.6), (40, 4.4, 4.4)], "bogskin", "forearm")
        k.box(fo, C(x, 30, 0, 7.4, 6.0, 7.4), "cloth", tag="sleeve_rag")
        k.box(hn, C(x, 20, 0.6, 5.4, 4.6, 4.4), "bogskin", tag="hand")
        for t in (-2.0, -0.7, 0.7, 2.0):
            pts = [(x + t, 20, 1.6), (x + t * 1.3, 13, 2.8), (x + t * 1.5, 6, 2.0), (x + t * 1.4, 2, 4.0)]
            for (a, b), w in zip(zip(pts, pts[1:]), (1.4, 1.1, 0.8)):
                k.limb(hn, a, b, w, "bark", "root_finger")
    # the staff in her right: a crooked willow, a skull lantern hung from the crook
    st = k.part("staff", (-13, 22, 1), (("x", 50),), k.parts["hand_r"])
    pts = [(-13, -14, 1), (-12, 6, 2), (-14, 24, 0), (-12, 42, 1), (-13, 50, 4), (-13, 48, 9)]
    for (a, b), w in zip(zip(pts, pts[1:]), (2.6, 2.4, 2.2, 2.0, 1.6)):
        k.limb(st, a, b, w, "bark", "staff")
    k.chain(st, (-13, 48, 9), (-13, 42, 9), 3, w=1.0)
    k.box(st, C(-13, 36, 9, 5.0, 5.6, 5.4), "bone", tag="skull_lantern")
    k.box(st, C(-13, 37.6, 11.75, 3.4, 1.6, 0.4), "glow", group="glow", tag="skull_eyes")
    k.box(st, C(-13, 35.6, 11.75, 2.6, 1.0, 0.4), "dark", tag="skull_teeth")
    k.box(st, C(-13, 36.4, 9, 4.0, 3.4, 4.6), "glow", group="glow", tag="skull_fire")
    strands(k, st, [(-12, 44, 2), (-14, 30, 0)], 8, w=1.2)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Coven Matron (elite, the key)

def coven_matron():
    """The eldest of the living hags, who keeps the hut and the door. Tall and bent under a broad witch's hat whose
    brim is set with candles; her face hidden behind a mask of willow bark with two holes; a robe sewn from old
    sacks and nets, weighted with stones; a great warty toad on her shoulder that is also watching. Her staff is
    the cauldron spoon, long as she is tall. The hex-knot that holds the door hangs at her belt."""
    k = X.Kit("coven_matron")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(0, 15, 12), (8, 13, 10), (14, 11, 8), (20, 9.6, 6.6)], "cloth", "robe")
    for (x, z) in ((-6, 5.4), (6, 5.0), (0, -5.6), (-5, -4.6)):
        k.limb(hips, (x, 20, z), (x * 1.1, 3, z * 1.1), 0.5, "rope", "net")
        k.box(hips, C(x * 1.1, 2.0, z * 1.1, 1.8, 1.8, 1.8), "mud", tag="weight_stone")
    k.box(hips, C(4.8, 14.4, 4.0, 2.6, 3.4, 1.0), "glow", group="glow", tag="hex_knot")
    for sx in (-0.8, 0.8):
        k.limb(hips, (4.8 + sx, 14.4, 4.6), (4.8 - sx, 17.4, 4.6), 0.4, "rope", "hex_knot")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.6
        th = k.part("thigh_" + nm, (x, 19, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 10, 0), (), th)
        ft = k.part("foot_" + nm, (x, 2, 0), (), sh)
        k.box(ft, C(x, 0, 2.4, 3.4, 1.6, 5.0), "bogskin", tag="foot")
    # ---------------------------------------------------------------- torso: bent, the toad on her shoulder
    to = k.part("torso", (0, 20, 0), (("x", 24),), "hips")
    k.stack(to, 0, 0, [(20, 9.6, 6.6), (26, 11, 7.0), (32, 13, 7.4)], "cloth", "robe")
    k.stack(to, 0, -0.4, [(26, 15, 9), (32, 16, 9.4), (34, 13, 8)], "hair", "shawl")
    for i, x in enumerate((-3, -1, 1, 3)):
        k.box(to, C(x, 26.6 + abs(x) * 0.4, 4.0, 0.8, 1.6, 0.6), "bone", tag="finger_bone")
    tt = (8.6, 35.0, 0)                  # the toad
    k.blob(to, (tt[0], tt[1] + 1.6, tt[2]), (3.2, 2.0, 3.6), "toad", "toad")
    k.box(to, C(tt[0], tt[1] + 2.0, tt[2] + 3.2, 4.8, 1.6, 1.4), "toad", tag="toad_mouth")
    for sx in (-1.4, 1.4):
        k.box(to, C(tt[0] + sx, tt[1] + 3.4, tt[2] + 2.4, 1.2, 1.2, 1.2), "eye", group="glow", tag="toad_eye")
        k.box(to, C(tt[0] + sx * 2.2, tt[1], tt[2] + 1.6, 1.4, 1.0, 2.0), "toad", tag="toad_foot")
    for (x, z) in ((-1.2, 0.8), (1.0, -1.4), (0, 1.6)):
        k.box(to, C(tt[0] + x, tt[1] + 3.4, tt[2] + z, 0.8, 0.6, 0.8), "mud", tag="wart")
    # ---------------------------------------------------------------- the head: the bark mask, the candle-brimmed hat
    hd = k.part("head", (0, 33, 1), (("x", -20),), "torso")
    k.box(hd, C(0, 32.6, 0.8, 6.0, 6.4, 6.0), "hair", tag="hair")
    k.box(hd, C(0, 33.0, 3.9, 4.6, 5.8, 1.0), "bark", tag="mask")
    for sx in (-1.0, 1.0):
        k.box(hd, C(sx, 36.0, 4.45, 1.2, 1.2, 0.3), "dark", tag="mask_hole")
        k.box(hd, C(sx, 36.2, 4.55, 0.6, 0.6, 0.2), "eye", group="glow", tag="eye")
    k.box(hd, C(0, 33.6, 4.45, 2.0, 0.6, 0.3), "dark", tag="mask_mouth")
    strands(k, hd, [(x, 37, -2.4) for x in (-2.4, -0.8, 0.8, 2.4)] + [(sx * 3.2, 37, 1) for sx in (-1, 1)], 12, w=1.2, mat="hair", tag="hair")
    k.box(hd, C(0, 38.6, 0.8, 18, 0.8, 18), "cloth", tag="hat_brim")
    pts = [(0, 39.4, 0.8), (0, 44, 0.2), (0.6, 48, -1.0), (2.0, 51, -3.0), (4.0, 51.4, -5.0)]
    for (a, b), w in zip(zip(pts, pts[1:]), (8.6, 6.0, 3.6, 2.0)):
        k.limb(hd, a, b, w, "cloth", "hat_cone")
    k.box(hd, C(0, 39.4, 0.8, 9.2, 1.4, 9.2), "rope", tag="hat_band")
    for a in range(0, 360, 45):          # candles on the brim
        r = math.radians(a + 20)
        x, z = math.sin(r) * 7.6, 0.8 + math.cos(r) * 7.6
        h = 1.6 + (a // 45) % 3
        k.box(hd, C(x, 39.0, z, 1.0, h, 1.0), "wax", tag="candle")
        k.box(hd, C(x, 39.0 + h, z, 0.6, 1.0, 0.6), "flame", group="glow", tag="flame")
        k.box(hd, C(x, 38.4, z, 1.6, 0.6, 1.6), "wax", tag="wax_drip")
    # ---------------------------------------------------------------- arms: thin, the cauldron-spoon staff
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.0
        up = k.part("arm_" + nm, (x, 31, 0), (("x", -60 if side > 0 else -40), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 23, 0), (("x", -60 if side > 0 else -50),), up)
        hn = k.part("hand_" + nm, (x, 15, 0), (), fo)
        k.box(up, C(x, 23, 0, 3.8, 8, 4.0), "cloth", tag="sleeve")
        k.stack(fo, x, 0, [(15, 5.6, 5.6), (19, 4.4, 4.4), (23, 3.8, 3.8)], "cloth", "sleeve")
        k.box(hn, C(x, 12.4, 0.4, 2.6, 2.8, 2.6), "bogskin", tag="hand")
        for t in (-0.8, 0, 0.8):
            k.shard(hn, (x + t, 12.4, 1.0), (0, -1, 0.4), 3.0, 0.6, mat="bark", tag="nail")
    sp = k.part("spoon", (-7, 13.6, 0.8), (("x", 70),), k.parts["hand_r"])
    k.limb(sp, (-7, -10, 0.8), (-7, 32, 0.8), 1.4, "bark", "haft")
    k.blob(sp, (-7, 36, 0.8), (3.0, 4.0, 1.6), "bark", "spoon_bowl", step=0.8)
    k.box(sp, C(-7, 35, 1.8, 3.6, 4.4, 0.6), "glow", group="glow", tag="spoon_brew")
    for (y, L) in ((26, 5), (20, 4)):
        k.limb(sp, (-7, y, 0.8), (-8.6, y - L, 0.8), 0.3, "rope", "cord")
        k.box(sp, C(-8.6, y - L - 1.2, 0.8, 1.2, 1.4, 1.0), "bone", tag="charm")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Bog Troll (brute)

def bog_troll():
    """It sleeps in the fen so long the fen grows on it: a mound of peat and moss on its back with a dead willow
    standing out of it, reeds round the roots, a glow of fungus. Under that a great grey-green troll, arms to the
    ground, a jaw like a shovel with the tusks pointing up, a nose like a root, little eyes. It swings a log with
    the roots still on, packed with stones."""
    k = X.Kit("bog_troll")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(15, 15, 11), (21, 16, 11.4)], "troll", "hips")
    for x in (-5, 0, 5):
        k.box(hips, C(x, 8, 5.6, 4.6, 9, 0.8), "moss", tag="moss_rag")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.0
        th = k.part("thigh_" + nm, (x, 19, 0), (("x", -12), ("z", side * 12)), "hips")
        sh = k.part("shin_" + nm, (x, 10, 0), (("x", 18),), th)
        ft = k.part("foot_" + nm, (x, 2.6, 0), (("x", -6),), sh)
        k.stack(th, x, 0, [(10, 7.4, 7.4), (15, 8.6, 8.6), (19, 8.2, 8.2)], "troll", "thigh")
        k.stack(sh, x, 0, [(2.6, 7.0, 7.2), (10, 7.4, 7.4)], "troll", "shin")
        k.box(ft, C(x, 0, 1.8, 8.4, 3.0, 11), "troll", tag="foot")
        for t in (-2.6, 0, 2.6):
            k.shard(ft, (x + t, 1.0, 7.0), (0, -0.3, 1), 2.4, 1.4, mat="bone", tag="foot")
    # ---------------------------------------------------------------- torso: hunched far over; the bog mound and the willow
    to = k.part("torso", (0, 21, 0), (("x", 32),), "hips")
    k.stack(to, 0, 0, [(21, 16, 11.4), (28, 22, 13), (35, 26, 14), (39, 24, 13)], "troll", "torso")
    k.blob(to, (0, 36, -5), (13, 6, 10), "mud", "bog_mound")
    k.blob(to, (2, 40, -6), (9, 4, 7), "moss", "moss_mound")
    branch(k, to, (-2, 42, -7), (-0.2, 1, -0.3), 12, 2.6, forks=2, seed=2)
    for (x, z) in ((-8, -2), (-6, -10), (7, -9), (9, -3), (4, -12)):
        k.limb(to, (x, 40, z), (x * 1.1, 48, z * 1.1), 0.7, "reed", "reed")
        k.limb(to, (x + 0.8, 40, z), (x * 1.2 + 0.8, 46, z * 1.1), 0.7, "reed", "reed")
    for (x, z) in ((-9, -6), (6, -2), (10, -8)):
        k.box(to, C(x, 41, z, 2.2, 1.0, 2.2), "glow", group="glow", tag="fungus_cap")
        k.box(to, C(x, 40, z, 0.8, 1.2, 0.8), "wax", tag="fungus_stalk")
    strands(k, to, [(sx, 34, -14) for sx in (-8, -4, 0, 4, 8)], 10, w=2.0)
    # ---------------------------------------------------------------- the head: low and forward, shovel jaw, tusks up
    hd = k.part("head", (0, 35, 6), (("x", -30),), "torso")
    k.box(hd, C(0, 34.6, 7.4, 9.0, 7.0, 8.0), "troll", tag="head")
    k.box(hd, C(0, 32.4, 10.6, 11, 3.6, 5.0), "troll", tag="jaw")
    for sx in (-3.4, 3.4):
        k.shard(hd, (sx, 35.6, 12.6), (sx * 0.06, 1, 0.3), 4.6, 1.6, mat="bone", tag="tusk")
        k.box(hd, C(sx * 0.6, 39.4, 11.2, 1.4, 0.8, 0.4), "eye", group="glow", tag="eye")
    k.shard(hd, (0, 39.0, 11.4), (0, -0.6, 1), 4.6, 2.4, mat="troll", tag="nose")
    k.box(hd, C(0, 41.0, 10.6, 9.0, 1.6, 2.0), "troll", tag="brow")
    strands(k, hd, [(sx * 4.4, 40, 8) for sx in (-1, 1)], 6, w=1.0)
    # ---------------------------------------------------------------- arms: to the ground, knuckles of stone
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 14
        up = k.part("arm_" + nm, (x, 36, 0), (("x", -10 if side > 0 else -50), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 24, 0), (("x", -10 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 12, 0), (), fo)
        k.blob(up, (x, 34, 0), (6, 5, 6), "troll", "shoulder")
        k.stack(up, x, 0, [(24, 6.6, 6.8), (32, 7.6, 7.8)], "troll", "upper_arm")
        k.stack(fo, x, 0, [(13, 8.4, 8.4), (19, 8.8, 8.8), (24, 7.2, 7.2)], "troll", "forearm")
        k.box(hn, C(x, 6.4, 0.6, 8.0, 6.4, 8.0), "troll", tag="fist")
        for t in (-2.6, 0, 2.6):
            k.box(hn, C(x + t, 6.0, 4.8, 2.0, 2.4, 1.4), "mud", tag="knuckle_stone")
    # the root-club: a log, its roots still on, stones packed in them
    cl = k.part("club", (-14, 10, 0.6), (("x", 60),), k.parts["hand_r"])
    k.stack(cl, -14, 0.6, [(2, 4.4, 4.4), (16, 6.0, 6.0), (30, 8.0, 8.0)], "bark", "log")
    for a in range(0, 360, 60):
        r = math.radians(a)
        k.limb(cl, (-14, 30, 0.6), (-14 + math.cos(r) * 7, 37, 0.6 + math.sin(r) * 7), 1.6, "bark", "root")
        k.box(cl, C(-14 + math.cos(r) * 4, 31, 0.6 + math.sin(r) * 4, 3.0, 3.0, 3.0), "mud", tag="packed_stone")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Hag Sister (caster)

def hag_sister():
    """One of the sisters: crook-backed so far her face is at your chest, grey hair to her knees, a nose like a hook
    and a chin to meet it, one eye milky and one witch-green. A shawl of moss, a necklace of frogs on a string, a
    ladle on her belt, and a birdcage on a pole with a will-o'-the-wisp in it, that she lets out."""
    k = X.Kit("hag_sister")
    hips = k.part("hips", (0, 17, -1))
    k.stack(hips, 0, -1, [(0, 12, 10), (8, 11, 9), (17, 9, 6.6)], "cloth", "skirt")
    k.box(hips, C(-4.6, 10, 2.6, 1.2, 6, 1.2), "bark", tag="ladle")
    k.box(hips, C(-4.6, 8.4, 3.4, 2.4, 1.6, 2.4), "bark", tag="ladle_bowl")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 16, -1), (), "hips")
        sh = k.part("shin_" + nm, (x, 9, -1), (), th)
        ft = k.part("foot_" + nm, (x, 2, -1), (), sh)
        k.box(ft, C(x, 0, 1.4, 3.0, 1.4, 4.6), "bogskin", tag="foot")
    # ---------------------------------------------------------------- torso: bent double, a hump, the moss shawl
    to = k.part("torso", (0, 17, -1), (("x", 50),), "hips")
    k.stack(to, 0, -1, [(17, 9, 6.6), (22, 10, 7.0), (27, 10.6, 7.2)], "cloth", "body")
    k.blob(to, (0, 25, -4.6), (5.4, 4.4, 3.6), "cloth", "hump")
    k.stack(to, 0, -1.4, [(25, 11.6, 8.6), (28, 12.4, 9.0), (29.4, 10, 8.0)], "moss", "shawl")
    strands(k, to, [(x, 22, 3.6) for x in (-4, -1.4, 1.4, 4)], 6, w=1.6)
    for i, x in enumerate((-2.6, -0.8, 1.0, 2.8)):       # a necklace of frogs
        k.box(to, C(x, 25.4 - abs(x) * 0.6, 3.4, 1.4, 1.2, 1.4), "toad", tag="frog")
    # ---------------------------------------------------------------- the head: hook nose to chin, wild hair
    hd = k.part("head", (0, 28, 0), (("x", -44),), "torso")
    k.box(hd, C(0, 27.6, 0.4, 5.2, 5.8, 5.2), "bogskin", tag="face")
    k.shard(hd, (0, 31.0, 3.0), (0, -0.9, 1), 6.4, 2.0, mat="bogskin", tag="nose")
    k.shard(hd, (0, 28.0, 2.8), (0, 0.4, 1), 2.6, 1.6, mat="bogskin", tag="chin")
    k.box(hd, C(0, 29.6, 3.05, 2.4, 0.5, 0.3), "dark", tag="mouth")
    k.box(hd, C(-1.4, 31.6, 3.05, 1.2, 0.8, 0.3), "eye", group="glow", tag="eye")
    k.box(hd, C(1.4, 31.6, 3.05, 1.2, 0.8, 0.3), "bone", tag="milk_eye")
    k.box(hd, C(0.8, 31.0, 3.4, 0.6, 0.6, 0.4), "dark", tag="wart")
    strands(k, hd, [(x, 33.6, z) for x in (-2.4, -0.8, 0.8, 2.4) for z in (-2.0, 0.4)], 16, w=1.2, mat="hair", tag="hair", sway=0.8)
    strands(k, hd, [(sx * 2.8, 32, 2) for sx in (-1, 1)], 10, w=1.0, mat="hair", tag="hair")
    # ---------------------------------------------------------------- arms: the cage-pole and a beckoning claw
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.0
        up = k.part("arm_" + nm, (x, 26, 0), (("x", -30 if side > 0 else -10), ("z", side * 8)), "torso")
        fo = k.part("fore_" + nm, (x, 19, 0), (("x", -60 if side > 0 else -30),), up)
        hn = k.part("hand_" + nm, (x, 12, 0), (), fo)
        k.box(up, C(x, 19.2, 0, 3.2, 7, 3.4), "cloth", tag="sleeve")
        k.box(fo, C(x, 12.4, 0, 2.2, 6.8, 2.4), "bogskin", tag="forearm")
        k.box(hn, C(x, 10.0, 0.3, 2.4, 2.4, 2.4), "bogskin", tag="hand")
        for t in (-0.8, 0, 0.8):
            k.shard(hn, (x + t, 10.0, 0.8), (0, -1, 0.6), 3.2, 0.6, mat="bark", tag="nail")
    cg = k.part("cage_pole", (-6, 11, 0.6), (("x", 30),), k.parts["hand_r"])
    k.limb(cg, (-6, -6, 0.6), (-6, 30, 0.6), 1.0, "bark", "pole")
    k.limb(cg, (-6, 30, 0.6), (-6, 31, 4.6), 0.8, "bark", "crook")
    k.limb(cg, (-6, 31, 4.6), (-6, 28, 4.6), 0.4, "rope", "cord")
    for a in range(0, 360, 60):
        r = math.radians(a)
        k.box(cg, C(-6 + math.sin(r) * 2.0, 22, 4.6 + math.cos(r) * 2.0, 0.5, 6, 0.5), "iron", tag="cage_bar")
    k.box(cg, C(-6, 21.6, 4.6, 4.6, 0.6, 4.6), "iron", tag="cage_floor")
    k.blob(cg, (-6, 28, 4.6), (2.4, 1.2, 2.4), "iron", "cage_dome", step=0.6)
    k.blob(cg, (-6, 25, 4.6), (1.5, 1.8, 1.5), "glow", "wisp", step=0.6)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Mire Thrall (swarm)

def mire_thrall():
    """The fen keeps what drowns in it, and the coven wakes it: a bog body, skin tanned to brown leather and shrunk
    to the bone, hair gone red-black, the noose it was hanged with still round its neck, moss in its ribs - and a
    hex stake of willow driven through its chest, the rune on it burning green. That is what moves it."""
    k = X.Kit("mire_thrall")
    hips = k.part("hips", (0, 18, 0))
    k.box(hips, C(0, 15.6, 0, 7.0, 3.6, 4.6), "bogskin", tag="pelvis")
    k.box(hips, C(0, 14.0, 0, 8.4, 4.4, 5.6), "cloth", tag="rag")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.2
        th = k.part("thigh_" + nm, (x, 18, 0), (("x", -10 if side > 0 else 6), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 9.8, 0), (("x", 14),), th)
        ft = k.part("foot_" + nm, (x, 2, 0), (("x", -6),), sh)
        k.box(th, C(x, 10.0, 0, 2.6, 8.4, 2.8), "bogskin", tag="thigh")
        k.box(sh, C(x, 2.0, 0, 2.2, 8.0, 2.4), "bogskin", tag="shin")
        k.box(sh, C(x, 9.4, 0.8, 3.0, 1.6, 2.4), "bogskin", tag="knee")
        k.box(ft, C(x, 0, 1.2, 2.8, 1.8, 5.0), "bogskin", tag="foot")
    # ---------------------------------------------------------------- torso: shrunken, ribs, moss, the hex stake
    to = k.part("torso", (0, 18, 0), (("x", 20), ("z", -8)), "hips")
    k.stack(to, 0, 0, [(18, 6.4, 4.2), (23, 8.4, 5.0), (28, 9.4, 5.2)], "bogskin", "torso")
    for y in (21.6, 23.4, 25.2):
        k.box(to, C(0, y, 2.55, 7.4, 0.8, 0.5), "dark", tag="rib_gap")
    k.box(to, C(-2.4, 22.4, 2.4, 2.4, 3.0, 0.6), "moss", tag="moss_ribs")
    k.limb(to, (1.0, 24, 6.4), (1.0, 24, -6.4), 1.4, "bark", "hex_stake")
    k.box(to, C(1.0, 24, 7.2, 1.8, 1.8, 1.0), "glow", group="glow", tag="hex_rune")
    k.box(to, C(1.0, 24, 2.9, 2.4, 2.4, 0.4), "glow", group="glow", tag="hex_wound")
    strands(k, to, [(-3, 27, -2.6), (2.6, 26, -2.6)], 6, w=1.2)
    # ---------------------------------------------------------------- the head: a tanned skull face, the noose
    hd = k.part("head", (0, 28.4, 0.4), (("x", -6), ("z", 22)), "torso")
    k.box(hd, C(0, 28.6, 0.4, 4.8, 5.6, 4.8), "bogskin", tag="face")
    k.box(hd, C(0, 28.0, 2.85, 3.2, 1.4, 0.3), "dark", tag="mouth")
    for t in (-1.0, -0.3, 0.4, 1.1):
        k.box(hd, C(t, 28.6, 2.9, 0.4, 0.6, 0.2), "bone", tag="tooth")
    for sx in (-1.1, 1.1):
        k.box(hd, C(sx, 31.4, 2.85, 1.2, 1.0, 0.3), "dark", tag="socket")
        k.box(hd, C(sx, 31.6, 2.95, 0.6, 0.5, 0.2), "eye", group="glow", tag="eye")
    k.box(hd, C(0, 33.6, -0.2, 5.0, 1.0, 4.6), "bark", tag="hair")
    strands(k, hd, [(x, 34, -2) for x in (-1.6, 0, 1.6)], 6, w=1.0, mat="bark", tag="hair")
    k.ring(hd, 0, 28.0, 0.4, 2.8, 0.8, "rope", "noose", n=10, axis="y")
    k.limb(hd, (1.6, 28.0, -2.2), (2.6, 22, -3.4), 0.8, "rope", "noose_end")
    # ---------------------------------------------------------------- arms: reaching, twig fingers
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.6
        up = k.part("arm_" + nm, (x, 26.6, 0), (("x", -80 if side > 0 else -60), ("z", side * 6)), "torso")
        fo = k.part("fore_" + nm, (x, 19.6, 0), (("x", -10 if side > 0 else -30),), up)
        hn = k.part("hand_" + nm, (x, 12.6, 0), (), fo)
        k.box(up, C(x, 19.8, 0, 2.2, 7.0, 2.4), "bogskin", tag="arm")
        k.box(fo, C(x, 12.8, 0, 2.0, 7.0, 2.2), "bogskin", tag="forearm")
        k.box(hn, C(x, 10.6, 0.3, 2.2, 2.2, 2.0), "bogskin", tag="hand")
        for t in (-0.7, 0, 0.7):
            k.limb(hn, (x + t, 10.6, 0.6), (x + t * 1.5, 7.0, 1.4), 0.5, "bark", "twig_finger")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Fen Crawler (skirmisher, on the spider)

def fen_crawler():
    """A bog spider as big as a pony, built low: its back a mat of moss and reeds like the bank it waits under,
    its face a toad's - wide mouth, bulging eyes, more eyes in a row above - and its egg sacs on its back, glowing
    witch-green through the moss. Long legs that stand it in the water and walk it across the top of the mud."""
    k = X.Kit("fen_crawler")
    body = k.part("body", (0, 6, 0))
    k.blob(body, (0, 6, 0), (5.4, 2.6, 5.4), "toad", "thorax")
    k.box(body, C(0, 8.0, 0, 9.0, 1.0, 9.0), "moss", tag="moss_mat")
    hd = k.part("head", (0, 6, 4.6), (), "body")
    k.blob(hd, (0, 6.0, 7.0), (4.0, 2.4, 2.8), "toad", "head")
    k.box(hd, C(0, 4.6, 9.4, 7.0, 0.8, 1.0), "dark", tag="mouth")
    for sx in (-2.6, 2.6):
        k.blob(hd, (sx, 8.2, 7.4), (1.2, 1.2, 1.2), "eye", "eye_bulge", step=0.6)
    for sx in (-1.4, -0.5, 0.5, 1.4):
        k.box(hd, C(sx, 8.2, 9.3, 0.6, 0.6, 0.3), "eye", group="glow", tag="eye")
    for sx in (-1, 1):
        k.shard(hd, (sx * 1.8, 4.4, 9.6), (sx * 0.4, -0.6, 1), 3.0, 1.0, mat="bone", tag="fang")
    ab = k.part("abdomen", (0, 6, -4), (("x", -10),), "body")
    k.blob(ab, (0, 7.0, -9.0), (6.4, 4.6, 7.0), "toad", "abdomen")
    k.blob(ab, (0, 10.0, -9.0), (5.8, 2.0, 6.4), "moss", "moss_back")
    for (x, z, s) in ((-2.4, -8, 1.8), (2.2, -10.4, 1.6), (0, -12.4, 1.4), (2.6, -6.6, 1.2)):
        k.blob(ab, (x, 11.6, z), (s, s, s), "glow", "egg_sac", step=0.6)
    for (x, z) in ((-4, -6), (-3, -12), (4, -12), (3.6, -4), (0, -14.6)):
        k.limb(ab, (x, 11, z), (x * 1.1, 16, z * 1.05), 0.6, "reed", "reed")
    strands(k, ab, [(-5, 8, -12), (5, 8, -12), (0, 8, -15)], 4, w=1.2)
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, z in enumerate((3.0, 1.0, -1.2, -3.4)):
            nm = "leg_%s%d" % (s, i)
            lg = k.part(nm, (side * 4.4, 6, z), (("y", -side * (i - 1.5) * 24),), "body")
            knee = (side * 12.0, 14.0, z)
            k.limb(lg, (side * 4.4, 6.4, z), knee, 1.4, "toad", "femur")
            k.box(lg, C(knee[0], knee[1] - 1.0, z, 2.0, 2.0, 2.0), "moss", tag="knee")
            k.limb(lg, knee, (side * 17.0, 0.6, z), 1.0, "toad", "tibia")
            k.shard(lg, (side * 17.0, 1.2, z), (side * 0.2, -1, 0), 1.6, 0.8, mat="bark", tag="foot")
            joints[nm] = ("LL" if side > 0 else "RL") + str(i + 1)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


MOBS = {
    "mire_thrall": dict(make=mire_thrall, ent=(0.8, 2.6), stats=dict(hp=20, speed=0.24, dmg=5, armor=1, kb=0)),
    "bog_troll": dict(make=bog_troll, ent=(1.6, 3.8), stats=dict(hp=80, speed=0.19, dmg=12, armor=4, kb=0.8)),
    "hag_sister": dict(make=hag_sister, ent=(0.9, 2.5), stats=dict(hp=28, speed=0.21, dmg=5, armor=1, kb=0)),
    "fen_crawler": dict(make=fen_crawler, rig="crawler", ent=(1.4, 0.9), stats=dict(hp=24, speed=0.34, dmg=6, armor=2, kb=0)),
    "coven_matron": dict(make=coven_matron, ent=(1.1, 3.4), stats=dict(hp=150, speed=0.21, dmg=10, armor=6, kb=0.5), key=True),
    "mother_mire": dict(make=mother_mire, texel=1, ent=(2.4, 6.2), stats=dict(hp=470, speed=0.21, dmg=16, armor=8, kb=0.9), boss=True),
}
