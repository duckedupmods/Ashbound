"""The Bloodmoon Court's monsters, each built by hand (tools/vox2.py). The vampire Countess's household on the night
that never ends: black velvet and crimson, tarnished silver, white lace gone grey, skin like candle wax, and the red
of the blood - dark where it dries, bright where it moves.

    blood_thrall     swarm   a pale servant in livery, a silver tray held up, knives hidden under it, eyes red
    gorged_butler    brute   the butler, bloated with blood until his coat splits, a carving knife and fork like weapons
    blood_mage       caster  a noble in a collar as high as his head, a lance of blood hanging in the air over his hand
    duelist          skirm   a fencer in a short cape and a feathered hat, rapier and main-gauche, the guard always up
    counts_hound     elite   the Count's hound, a gaunt black wolf as big as a horse, a silver collar and chains (spider's bones)
    countess_vael    boss    Countess Vael: tall and pale, a gown of blood that runs off her into a spreading pool with
                             spikes rising out of it, a bat-wing collar, a blade of hardened blood and a whip of it

    python tools/monsterforge.py bloodmoon_court --preview ; python tools/mobsheet.py bloodmoon_court
"""
import math

import vox2 as X
from vox2 import C, ramp

VELVET = ramp("#0a0206", "#16040c", "#240812", "#360c1a", "#4a1224", "#5e1a2e")
CRIMSON = ramp("#2a0206", "#46040c", "#6a0814", "#92101e", "#b81e2a", "#dc3a3e")
BLOOD = ramp("#3a0006", "#6a000e", "#a00818", "#d01c26", "#ff4a44", "#ff9a8a")
SILVER = ramp("#2a2a30", "#44444c", "#606068", "#7e7e86", "#a0a0a8", "#c4c4cc")
WAX = ramp("#4a4448", "#6a6266", "#8a8286", "#aaa2a4", "#ccc4c4", "#e8e2e0")
LACE = ramp("#5a5654", "#7a7672", "#9a9690", "#bab6ae", "#d6d2c8")
BLACK = ramp("#060506", "#0e0c0e", "#18141a", "#221d24", "#2e2830")
FUR = ramp("#060606", "#0e0d0e", "#181618", "#222024", "#2e2a30")
GOLD = ramp("#3a2606", "#5e400c", "#8a6214", "#b48a24", "#dab43c")
HAIR = ramp("#060406", "#0e0a0e", "#181218", "#221a22")


def shaders():
    return {
        "velvet": X.surf(VELVET, 0.5, 1.2, 0.16, 0.0),
        "crimson": X.surf(CRIMSON, 0.5, 1.3, 0.16, 0.06),
        "blood": X.glow(BLOOD, 0.5, 0.4),
        "gore": X.surf(BLOOD, 0.4, 1.6, 0.2, 0.2),
        "eye": X.glow(BLOOD, 0.86, 0.12),
        "silver": X.surf(SILVER, 0.56, 1.5, 0.12, 0.24, rust=(BLACK, 0.2, 0.5)),
        "wax": X.wrinkled(WAX, 0.4),
        "lace": X.surf(LACE, 0.56, 1.0, 0.2, 0.0, pattern=lambda p, n, i, j, w, h: -0.2 if (i + j) % 3 == 0 else 0),
        "black": X.surf(BLACK, 0.52, 1.3, 0.14, 0.12),
        "fur": X.surf(FUR, 0.5, 1.0, 0.3, 0.0, stripe=2),
        "gold": X.surf(GOLD, 0.56, 1.4, 0.12, 0.2),
        "hair": X.surf(HAIR, 0.5, 1.2, 0.2, 0.0, stripe=2),
        "swollen": X.wrinkled(ramp("#1e0408", "#34080e", "#4c0e16", "#64161e", "#7c2028"), 0.6),
        "dark": X.dark(BLACK),
    }


def drip(k, part, x, y, z, L, w=0.8):
    """a run of blood down from a point, a bead at its end"""
    k.box(part, C(x, y - L, z, w, L, w), "gore", tag="drip")
    k.box(part, C(x, y - L - w * 0.8, z, w * 1.4, w, w * 1.4), "gore", tag="drip")


def batwing(k, part, at, side, s=1.0, mat="velvet"):
    """a bat's wing: three finger bones out from a wrist, the membrane between them"""
    x, y, z = at
    fingers = [(side * 7 * s, 4 * s), (side * 9 * s, -1 * s), (side * 6 * s, -6 * s)]
    tips = []
    for (dx, dy) in fingers:
        tip = (x + dx, y + dy, z - 1)
        k.limb(part, at, tip, 0.8 * s, "black", "wing_bone")
        tips.append(tip)
    for (a, b) in zip([at] + tips, tips):
        mid = tuple((a[i] + b[i]) / 2 for i in range(3))
        k.limb(part, at, mid, 3.2 * s, mat, "membrane", d=0.4)


# ================================================================ Countess Vael (boss)

def countess_vael():
    """Countess Vael has held the court for four hundred years of one night. She is tall - three men tall when she
    rises in her hall - and as pale as wax, black hair piled high under a silver tiara with a blood ruby, a collar
    of black velvet stiffened into bat wings standing behind her head. Her gown is blood: it holds its shape at the
    bodice but below the waist it is running, falling off her in sheets, and it spreads round her across the floor
    in a pool, and out of the pool spikes of hardened blood stand up. In her right hand a long blade of the same
    blood, hardened and glassy; from her left a whip of it runs and coils."""
    k = X.Kit("countess_vael")
    hips = k.part("hips", (0, 40, 0))
    k.stack(hips, 0, 0, [(34, 13, 9), (40, 12, 8.6)], "crimson", "bodice_low")
    # the gown, running: sheets of blood from the waist down, flaring, into a pool on the floor
    k.stack(hips, 0, 0, [(0.6, 40, 36), (4, 34, 30), (12, 26, 22), (24, 19, 15), (34, 14, 10)], "crimson", "gown", step=1.2)
    for i in range(12):
        a = math.radians(i * 30 + 10)
        k.limb(hips, (math.sin(a) * 7, 34, math.cos(a) * 5), (math.sin(a) * 18, 4, math.cos(a) * 16), 2.0, "blood", "gown_sheet", d=0.8, group="glow")
    k.blob(hips, (0, 0.6, 0), (26, 0.8, 24), "blood", "blood_pool", step=0.8)
    for i, (a, r, L) in enumerate(((20, 20, 10), (75, 23, 14), (130, 19, 8), (190, 24, 12), (250, 21, 9), (310, 23, 13), (350, 18, 7))):
        ra = math.radians(a)
        k.shard(hips, (math.sin(ra) * r, 0.4, math.cos(ra) * r), (math.sin(ra) * 0.2, 1, math.cos(ra) * 0.2), L, 2.6, mat="gore", tag="blood_spike")
    for (x, z) in ((-6, 7), (5, 7.4), (0, 8), (-9, 3), (9, 2)):
        drip(k, hips, x, 34, z, 6, w=1.0)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 4
        th = k.part("thigh_" + nm, (x, 34, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 18, 0), (), th)
        ft = k.part("foot_" + nm, (x, 4, 0), (), sh)
        k.box(ft, C(x, 0, 2, 5, 2, 7), "gore", tag="foot")
    # ---------------------------------------------------------------- torso: the bodice, lace, a ruby at the breast
    to = k.part("torso", (0, 40, 0), (("x", -2),), "hips")
    k.stack(to, 0, 0, [(40, 12, 8.6), (46, 14, 9.6), (52, 18, 10.4), (56, 17, 9.6)], "crimson", "bodice")
    k.box(to, C(0, 41, 4.8, 3.0, 13, 0.6), "black", tag="lacing")
    for y in (43, 46, 49, 52):
        k.box(to, C(0, y, 5.2, 4.4, 0.4, 0.4), "silver", tag="lace_x")
    k.box(to, C(0, 53.4, 5.0, 10, 2.6, 1.0), "lace", tag="neckline")
    k.box(to, C(0, 50.6, 5.6, 2.4, 2.4, 1.0), "blood", group="glow", tag="ruby")
    k.box(to, C(0, 55, 0, 6.0, 4.0, 5.0), "wax", tag="throat")
    # the bat-wing collar, standing behind her head
    for side in (1, -1):
        batwing(k, to, (side * 3, 58, -3.6), side, s=1.6)
    # and the great wings behind her: a bat's, black velvet, the span of the hall
    wg = k.part("wings", (0, 52, -6), (), to, bone=False)
    for side in (1, -1):
        root, elbow, wrist = (side * 4, 52, -6), (side * 16, 64, -10), (side * 30, 70, -12)
        k.limb(wg, root, elbow, 2.4, "black", "wing_arm")
        k.limb(wg, elbow, wrist, 1.8, "black", "wing_arm")
        k.shard(wg, wrist, (side * 0.2, 1, 0), 4, 1.4, mat="black", tag="wing_claw")
        tips = [(side * 40, 54, -13), (side * 36, 38, -12), (side * 26, 28, -10), (side * 14, 30, -8)]
        for tip in tips:
            k.limb(wg, wrist, tip, 1.2, "black", "wing_finger")
        for (a, b) in zip([elbow] + tips, tips):
            for f in (0.15, 0.27, 0.39, 0.51, 0.63, 0.75, 0.87):
                m = tuple(wrist[i] + (a[i] - wrist[i]) * f for i in range(3))
                n = tuple(wrist[i] + (b[i] - wrist[i]) * f for i in range(3))
                k.limb(wg, m, n, 2.2, "velvet", "membrane", d=0.4)
            k.limb(wg, a, b, 2.4, "velvet", "membrane", d=0.4)
    # ---------------------------------------------------------------- the head: wax-pale, black hair piled high, the tiara
    hd = k.part("head", (0, 58, 0.6), (("x", -4),), "torso")
    k.box(hd, C(0, 58.6, 0.6, 6.4, 8.0, 6.6), "wax", tag="face")
    k.box(hd, C(0, 62.0, 4.0, 5.4, 0.6, 0.4), "black", tag="brow")
    for sx in (-1.5, 1.5):
        k.box(hd, C(sx, 61.0, 3.95, 1.6, 0.7, 0.3), "eye", group="glow", tag="eye")
    k.box(hd, C(0, 59.4, 4.1, 1.0, 1.4, 0.6), "wax", tag="nose")
    k.box(hd, C(0, 58.2, 3.95, 2.4, 0.5, 0.3), "crimson", tag="lips")
    for sx in (-0.6, 0.6):
        k.shard(hd, (sx, 58.0, 4.0), (0, -1, 0.1), 1.0, 0.4, mat="lace", tag="fang")
    k.stack(hd, 0, -0.4, [(62, 7.4, 7.6), (66, 8.0, 8.0), (70, 6.0, 6.0), (73, 3.6, 3.6)], "hair", "hair_piled")
    k.box(hd, C(0, 54, -3.4, 6.0, 8, 1.6), "hair", tag="hair_back")
    k.ring(hd, 0, 66.4, 0.4, 4.2, 0.8, "silver", "tiara", n=14, axis="y")
    for i in range(5):
        a = math.radians(-50 + i * 25)
        k.shard(hd, (math.sin(a) * 4.0, 66.4, 0.4 + math.cos(a) * 4.0), (0, 1, 0.2), 2.4 if i == 2 else 1.6, 0.8, mat="silver", tag="tiara_point")
    k.box(hd, C(0, 66.8, 4.6, 1.4, 1.4, 0.6), "blood", group="glow", tag="tiara_ruby")
    # ---------------------------------------------------------------- arms: long white gloves to the elbow, the blade and the whip
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 9.4
        up = k.part("arm_" + nm, (x, 55, 0), (("x", -40 if side > 0 else -60), ("z", side * 18)), "torso")
        fo = k.part("fore_" + nm, (x, 44, 0), (("x", -30 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 33, 0), (), fo)
        k.box(up, C(x, 44.6, 0, 3.4, 10.4, 3.6), "wax", tag="arm")
        k.box(up, C(x, 52, 0, 4.6, 3.4, 4.8), "crimson", tag="puff_sleeve")
        k.box(fo, C(x, 34, 0, 3.4, 10.4, 3.6), "black", tag="glove")
        k.box(hn, C(x, 30.6, 0.4, 3.2, 3.6, 3.0), "black", tag="hand")
        for t in (-1.0, 0, 1.0):
            k.shard(hn, (x + t, 30.6, 0.8), (0, -1, 0.3), 2.4, 0.6, mat="gore", tag="nail")
    bl = k.part("blood_blade", (-9.4, 32, 0.6), (("x", 80),), k.parts["hand_r"])
    k.box(bl, C(-9.4, 28, 0.6, 1.6, 5.0, 1.6), "black", tag="grip")
    k.box(bl, C(-9.4, 32.8, 0.6, 1.8, 1.2, 6.4), "silver", tag="guard")
    k.box(bl, C(-9.4, 34, 0.6, 1.0, 34, 2.4), "blood", group="glow", tag="blade")
    k.shard(bl, (-9.4, 68, 0.6), (0, 1, 0), 4.0, 2.4, mat="blood", tag="blade", group="glow")
    for y in (40, 50, 58):
        k.shard(bl, (-9.4, y, -0.6), (0, -0.4, -1), 2.4, 1.0, mat="gore", tag="blade_thorn")
    wp = k.part("blood_whip", (9.4, 32, 0.6), (), k.parts["hand_l"])
    pts = [(9.4, 30, 1), (12, 22, 4), (10, 14, 9), (14, 8, 14), (20, 6, 16), (24, 10, 12), (22, 14, 8)]
    for (a, b), w in zip(zip(pts, pts[1:]), (1.6, 1.4, 1.3, 1.1, 0.9, 0.7)):
        k.limb(wp, a, b, w, "blood", "whip", group="glow")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Count's Hound (elite, the key, on the spider)

def counts_hound():
    """The Count is long dead; his hound is not. A gaunt black wolf as big as a horse, ribs showing through the fur,
    a spine of bristles, jaws that hang open, red eyes, a collar of tarnished silver with the key to the Moon Hall
    on it and broken chains trailing from it. It howls and the thralls come running."""
    k = X.Kit("counts_hound")
    body = k.part("body", (0, 16, 0))
    k.stack(body, 0, 0, [(10, 10, 16), (16, 12, 18), (21, 10, 16)], "fur", "chest")
    for z in (-4, -1, 2, 5):
        k.box(body, C(0, 12, z, 11, 1.0, 1.4), "dark", tag="rib_gap")
    for z in range(-7, 9, 2):
        k.shard(body, (0, 21, z), (0, 1, -0.3), 3.0 + (z % 4) * 0.4, 1.4, mat="fur", tag="bristle")
    hd = k.part("head", (0, 18, 9), (("x", -10),), "body")
    k.box(hd, C(0, 16, 10, 7.0, 7.0, 6.0), "fur", tag="head")
    k.box(hd, C(0, 15.6, 16, 4.6, 3.6, 7.0), "fur", tag="muzzle")
    k.box(hd, C(0, 12.4, 15.4, 4.0, 2.0, 6.0), "fur", tag="jaw")
    k.box(hd, C(0, 14.4, 16, 4.0, 1.4, 6.4), "gore", tag="mouth")
    for t in (-1.4, -0.5, 0.5, 1.4):
        k.shard(hd, (t, 15.4, 20.0), (0, -1, 0.1), 1.6, 0.6, mat="lace", tag="tooth")
        k.shard(hd, (t, 14.0, 19.6), (0, 1, 0.1), 1.2, 0.5, mat="lace", tag="tooth")
    drip(k, hd, 0.8, 12.4, 18, 3, w=0.6)
    k.box(hd, C(0, 18.4, 22.8, 1.8, 1.2, 0.8), "dark", tag="nose")
    for sx in (-2.2, 2.2):
        k.box(hd, C(sx, 20.0, 13.05, 1.4, 0.8, 0.4), "eye", group="glow", tag="eye")
        k.shard(hd, (sx * 1.2, 23, 9), (sx * 0.2, 1, -0.3), 4.0, 2.0, mat="fur", tag="ear")
    k.ring(hd, 0, 14, 7.6, 6.0, 1.6, "silver", "collar", n=16, axis="z")
    for a in range(0, 360, 45):
        r = math.radians(a)
        k.shard(hd, (math.cos(r) * 6.4, 14 + math.sin(r) * 6.4, 7.6), (math.cos(r), math.sin(r), 0), 1.6, 0.8, mat="silver", tag="collar_spike")
    k.box(hd, C(0, 6.4, 8.4, 1.4, 3.4, 0.8), "gold", tag="key")
    k.box(hd, C(0.8, 6.4, 8.4, 1.2, 0.8, 0.8), "gold", tag="key_bit")
    k.chain(hd, (-5, 12, 7), (-8, 2, 2), 5, mat="silver", w=1.2)
    k.chain(hd, (5, 12, 7), (8, 4, -2), 4, mat="silver", w=1.2)
    ab = k.part("abdomen", (0, 16, -8), (), "body")
    k.stack(ab, 0, -11, [(10, 8, 9), (15, 9.6, 10), (19, 8, 9)], "fur", "haunch")
    tail = [(0, 18, -16), (0, 16, -21), (0, 12, -25), (0, 9, -27)]
    for (a, b), w in zip(zip(tail, tail[1:]), (2.4, 2.0, 1.4)):
        k.limb(ab, a, b, w, "fur", "tail")
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, (z, j, part) in enumerate(((5, 1, body), (-11, 4, ab))):
            nm = "leg_%s%d" % (s, i)
            lg = k.part(nm, (side * 4.6, 13, z), (), part)
            kn = (side * 5.0, 6.4, z + (1.6 if i == 0 else -2.4))
            k.limb(lg, (side * 4.6, 13, z), kn, 3.0, "fur", "leg")
            k.limb(lg, kn, (side * 5.0, 0.6, z + (0.6 if i == 0 else 0.4)), 2.2, "fur", "foot")
            k.box(lg, C(side * 5.0, 0, z + 1.2, 3.4, 1.4, 4.4), "fur", tag="foot")
            for t in (-1.0, 0, 1.0):
                k.shard(lg, (side * 5.0 + t, 0.6, z + 3.2), (0, -0.3, 1), 1.4, 0.6, mat="dark", tag="foot")
            joints[nm] = ("LL" if side > 0 else "RL") + str(j)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Gorged Butler (brute)

def gorged_butler():
    """The butler has served the Countess for two hundred years and eaten from every plate he carried away. He is
    swollen with blood until his tailcoat has split down the back and his waistcoat buttons are gone, the skin
    taut and purple-red and showing through, veins lit dark red. He still wears his white gloves; he carries a
    carving knife as long as a sword and a carving fork, and when he bursts, everything near him is drenched."""
    k = X.Kit("gorged_butler")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(15, 16, 12), (21, 18, 13)], "black", "trousers")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 4.6
        th = k.part("thigh_" + nm, (x, 19, 0), (("x", -6), ("z", side * 8)), "hips")
        sh = k.part("shin_" + nm, (x, 10.4, 0), (("x", 10),), th)
        ft = k.part("foot_" + nm, (x, 2.6, 0), (("x", -4),), sh)
        k.stack(th, x, 0, [(10.4, 7.0, 7.2), (19, 8.0, 8.2)], "black", "thigh")
        k.stack(sh, x, 0, [(2.6, 6.0, 6.2), (10.4, 6.8, 7.0)], "black", "shin")
        k.box(ft, C(x, 0, 1.8, 6.4, 2.8, 9.4), "black", tag="foot")
        k.box(ft, C(x, 2.2, 1.8, 6.6, 0.6, 9.6), "silver", tag="buckle")
    # ---------------------------------------------------------------- torso: the swollen belly bursting the waistcoat
    to = k.part("torso", (0, 21, 0), (("x", -6),), "hips")
    k.blob(to, (0, 28, 2), (13, 11, 11), "swollen", "belly", step=1.0)
    for (a, b) in (((-6, 34, 10), (-3, 24, 12)), ((5, 33, 10.4), (8, 23, 10)), ((0, 30, 12.6), (2, 20, 11))):
        k.limb(to, a, b, 1.0, "blood", "vein", group="glow")
    for sx in (-1, 1):          # the waistcoat, burst open either side of the belly
        k.box(to, C(sx * 9.4, 22, 4, 5.0, 14, 8), "crimson", tag="waistcoat")
        for y in (24, 28, 32):
            k.box(to, C(sx * 7.2, y, 8.2, 0.8, 0.8, 0.6), "silver", tag="button_hole")
    k.stack(to, 0, -2, [(34, 22, 15), (40, 22, 14), (43, 18, 12)], "black", "tailcoat")
    k.box(to, C(0, 40, 6.2, 4.6, 3.0, 1.6), "lace", tag="cravat")
    for sx in (-1, 1):
        k.box(to, C(sx * 5, 6, -7.4, 6.0, 30, 1.0), "black", tag="coat_tail")
    k.box(to, C(0, 26, -7.0, 3.0, 14, 1.0), "gore", tag="split_back")
    # ---------------------------------------------------------------- the head: small on the bulk, a bald waxen head, a thin mustache
    hd = k.part("head", (0, 43, 1), (("x", 4),), "torso")
    k.box(hd, C(0, 43, 1, 6.4, 7.0, 6.6), "wax", tag="head")
    k.box(hd, C(0, 46, 4.4, 2.0, 1.0, 0.6), "wax", tag="nose")
    k.box(hd, C(0, 44.4, 4.35, 4.4, 0.6, 0.3), "hair", tag="mustache")
    k.box(hd, C(0, 43.4, 4.35, 2.6, 0.6, 0.3), "gore", tag="mouth")
    for sx in (-1.4, 1.4):
        k.box(hd, C(sx, 47.4, 4.35, 1.2, 0.6, 0.3), "eye", group="glow", tag="eye")
    k.box(hd, C(0, 49.6, 1, 6.6, 0.6, 6.8), "hair", tag="combover")
    # ---------------------------------------------------------------- arms: white gloves, the carving knife and fork
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 14
        up = k.part("arm_" + nm, (x, 39, 0), (("x", -40 if side > 0 else -70), ("z", side * 16)), "torso")
        fo = k.part("fore_" + nm, (x, 29, 0), (("x", -50 if side > 0 else -30),), up)
        hn = k.part("hand_" + nm, (x, 19, 0), (), fo)
        k.stack(up, x, 0, [(29, 7.0, 7.2), (39, 8.0, 8.2)], "black", "sleeve")
        k.stack(fo, x, 0, [(20, 6.4, 6.6), (29, 7.0, 7.2)], "black", "sleeve")
        k.box(fo, C(x, 20, 0, 7.4, 1.6, 7.6), "lace", tag="cuff")
        k.box(hn, C(x, 14.4, 0.6, 5.6, 5.4, 5.6), "lace", tag="glove")
    kf = k.part("carving_knife", (-14, 16, 0.6), (("x", 80),), k.parts["hand_r"])
    k.box(kf, C(-14, 12, 0.6, 2.0, 6.0, 2.4), "black", tag="handle")
    k.box(kf, C(-14, 18, 0.6, 1.0, 24, 5.0), "silver", tag="blade")
    k.shard(kf, (-14, 42, 1.6), (0, 1, -0.3), 4.0, 3.0, mat="silver", tag="blade")
    k.box(kf, C(-14, 26, 3.4, 1.2, 10, 0.8), "gore", tag="blade_blood")
    fk = k.part("carving_fork", (14, 16, 0.6), (("x", 80),), k.parts["hand_l"])
    k.box(fk, C(14, 12, 0.6, 2.0, 6.0, 2.4), "black", tag="handle")
    k.limb(fk, (14, 18, 0.6), (14, 24, 0.6), 1.2, "silver", "fork_neck")
    for dz in (-1.4, 1.4):
        k.limb(fk, (14, 24, 0.6), (14, 24, 0.6 + dz), 1.0, "silver", "fork_neck")
        k.shard(fk, (14, 24, 0.6 + dz), (0, 1, 0), 9.0, 0.9, mat="silver", tag="tine")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Blood Mage (caster)

def blood_mage():
    """A noble of the court who learned the old art: a long black coat with silver frogging, a collar so high and
    stiff it stands above his head like a fan of black velvet lined red, a waxen face with hollow cheeks, and over
    his raised hand a lance of blood hangs in the air, turning, drawn out of the thrall he just opened."""
    k = X.Kit("blood_mage")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(2, 11, 8), (11, 10, 7), (20, 9, 6.4)], "black", "coat")
    k.box(hips, C(0, 4, 3.6, 2.0, 15, 0.6), "crimson", tag="coat_lining")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 20, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 10.6, 0), (), th)
        ft = k.part("foot_" + nm, (x, 2.4, 0), (), sh)
        k.box(sh, C(x, 0, 0, 3.4, 4, 4.0), "black", tag="boot")
        k.box(ft, C(x, 0, 1.6, 3.4, 1.6, 5.6), "black", tag="foot")
    # ---------------------------------------------------------------- torso: silver frogging
    to = k.part("torso", (0, 20, 0), (("x", -4),), "hips")
    k.stack(to, 0, 0, [(20, 9, 6.4), (26, 11, 7.0), (32, 12.4, 7.2)], "black", "coat")
    for y in (22, 24.6, 27.2, 29.8):
        k.box(to, C(0, y, 3.65, 6.6, 0.6, 0.4), "silver", tag="frogging")
        for sx in (-3.6, 3.6):
            k.box(to, C(sx, y - 0.2, 3.75, 1.0, 1.0, 0.4), "silver", tag="frog_knot")
    k.box(to, C(0, 31.4, 3.8, 3.0, 2.0, 0.8), "lace", tag="cravat")
    k.box(to, C(0, 30.0, 4.3, 1.2, 1.2, 0.4), "blood", group="glow", tag="pin")
    # the collar: high and stiff, a fan of velvet above his head, lined red
    for i in range(9):
        a = math.radians(-80 + i * 20)
        k.limb(to, (math.sin(a) * 4.0, 31.6, -1.0 + math.cos(a) * 1.2), (math.sin(a) * 8.0, 42 - abs(i - 4) * 0.8, -3.0), 2.8, "velvet", "collar_rib", d=0.5)
        k.limb(to, (math.sin(a) * 3.8, 31.6, -0.6 + math.cos(a) * 1.2), (math.sin(a) * 7.6, 41.4 - abs(i - 4) * 0.8, -2.4), 2.4, "crimson", "collar_lining", d=0.3)
    # ---------------------------------------------------------------- the head
    hd = k.part("head", (0, 32, 0.6), (("x", 4),), "torso")
    k.box(hd, C(0, 32, 0.6, 5.0, 6.4, 5.4), "wax", tag="face")
    for sx in (-1.2, 1.2):
        k.box(hd, C(sx, 35.4, 3.35, 1.2, 0.6, 0.3), "eye", group="glow", tag="eye")
        k.box(hd, C(sx * 1.6, 33.6, 3.35, 0.6, 1.6, 0.3), "dark", tag="hollow_cheek")
    k.box(hd, C(0, 33.2, 3.35, 1.8, 0.4, 0.3), "crimson", tag="mouth")
    k.stack(hd, 0, -0.2, [(37, 5.6, 5.8), (38.6, 5.0, 5.2)], "hair", "hair")
    k.shard(hd, (0, 38.4, 3.0), (0, -1, 0.3), 2.0, 1.4, mat="hair", tag="widows_peak")
    # ---------------------------------------------------------------- arms: one raised, the lance of blood above it
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.0
        up = k.part("arm_" + nm, (x, 30.4, 0), (("x", -150 if side > 0 else -20), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 22, 0), (("x", -20 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 14, 0), (), fo)
        k.box(up, C(x, 22.2, 0, 3.6, 8.4, 3.8), "black", tag="sleeve")
        k.box(fo, C(x, 14.4, 0, 3.4, 7.6, 3.6), "black", tag="sleeve")
        k.box(fo, C(x, 14.0, 0, 4.2, 1.6, 4.4), "lace", tag="cuff")
        k.box(hn, C(x, 11.4, 0.4, 2.6, 2.8, 2.4), "wax", tag="hand")
    ln = k.part("blood_lance", (7, 6, 0.6), (("x", 90),), k.parts["hand_l"])
    k.shard(ln, (7, -6, 0.6), (0, -1, 0), 4.0, 2.4, mat="blood", tag="lance", group="glow")
    k.limb(ln, (7, -6, 0.6), (7, 8, 0.6), 2.4, "blood", "lance", group="glow")
    k.shard(ln, (7, 8, 0.6), (0, 1, 0), 8.0, 2.4, mat="blood", tag="lance", group="glow")
    for (dx, dz) in ((-1.6, 1.0), (1.4, -1.2), (0.4, 1.8)):
        k.box(ln, C(7 + dx, 2 + dz * 2, 0.6 + dz, 0.8, 0.8, 0.8), "blood", group="glow", tag="droplet")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Duelist (skirmisher)

def duelist():
    """The Countess's duelists fight for her amusement, every night, forever. A slim fencer in a black doublet slashed
    to show crimson, a short cape off one shoulder, a broad hat with a red feather, a white mask over the upper face,
    a long rapier in one hand and a main-gauche in the other, the guard always up."""
    k = X.Kit("duelist")
    hips = k.part("hips", (0, 20, 0))
    k.box(hips, C(0, 17.4, 0, 8.0, 3.6, 5.4), "black", tag="breeches")
    k.box(hips, C(0, 20, 0, 8.6, 1.4, 6.0), "silver", tag="belt")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -30 if side > 0 else 10), ("z", side * 8)), "hips")
        sh = k.part("shin_" + nm, (x, 10.8, 0), (("x", 30 if side > 0 else 6),), th)
        ft = k.part("foot_" + nm, (x, 2.4, 0), (("x", -6),), sh)
        k.box(th, C(x, 11, 0, 3.6, 9.2, 3.8), "black", tag="thigh")
        k.box(sh, C(x, 2.4, 0, 3.4, 8.4, 3.6), "black", tag="boot")
        k.box(sh, C(x, 9.0, 0, 4.4, 2.4, 4.6), "black", tag="boot_cuff")
        k.box(ft, C(x, 0, 1.4, 3.4, 2.2, 6.2), "black", tag="foot")
    # ---------------------------------------------------------------- torso: slashed doublet, a short cape off one shoulder
    to = k.part("torso", (0, 20, 0), (("x", 10), ("y", -24)), "hips")
    k.stack(to, 0, 0, [(20, 8.4, 5.4), (25, 10, 6.0), (30, 11.4, 6.2)], "black", "doublet")
    for (x, y) in ((-2.6, 22), (2.6, 22), (-2.6, 26), (2.6, 26), (0, 24)):
        k.box(to, C(x, y, 3.15, 0.8, 2.6, 0.3), "crimson", tag="slash")
    k.box(to, C(0, 30, 0.4, 7.0, 1.4, 6.4), "lace", tag="collar")
    cp = k.part("cape", (-4, 30, 0), (("z", 20), ("x", -10)), to, bone=False)
    k.box(cp, C(-6, 16, -1, 8, 14, 7.6), "velvet", tag="cape")
    k.box(cp, C(-6, 16, -1, 8.4, 1.0, 8.0), "silver", tag="cape_hem")
    # ---------------------------------------------------------------- the head: hat, red feather, white half-mask
    hd = k.part("head", (0, 30.4, 0.4), (("x", -10), ("y", 20)), "torso")
    k.box(hd, C(0, 30.4, 0.4, 5.0, 6.0, 5.2), "wax", tag="face")
    k.box(hd, C(0, 33.0, 3.05, 5.2, 2.6, 0.5), "lace", tag="half_mask")
    for sx in (-1.1, 1.1):
        k.box(hd, C(sx, 33.6, 3.35, 1.2, 0.6, 0.3), "eye", group="glow", tag="eye")
    k.box(hd, C(0, 31.4, 3.0, 1.6, 0.3, 0.3), "dark", tag="mouth")
    k.box(hd, C(0, 30.0, 2.9, 1.0, 1.2, 0.6), "hair", tag="goatee")
    k.box(hd, C(0, 36.4, 0.4, 10, 0.6, 10), "black", tag="hat_brim")
    k.stack(hd, 0, 0.4, [(37, 5.6, 5.8), (39, 5.0, 5.2)], "black", "hat")
    pts = [(2, 38, -1), (4, 41, -3), (5, 42, -7), (4, 40, -10)]
    for (a, b), w in zip(zip(pts, pts[1:]), (1.6, 1.4, 1.0)):
        k.limb(hd, a, b, w, "crimson", "feather", d=0.4)
    # ---------------------------------------------------------------- arms: rapier forward, main-gauche back
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.0
        up = k.part("arm_" + nm, (x, 28.4, 0), (("x", -30 if side > 0 else -80), ("z", side * 20)), "torso")
        fo = k.part("fore_" + nm, (x, 21, 0), (("x", -70 if side > 0 else -10),), up)
        hn = k.part("hand_" + nm, (x, 13.8, 0), (), fo)
        k.box(up, C(x, 21.2, 0, 3.2, 7.4, 3.4), "black", tag="sleeve")
        k.box(up, C(x, 25, 0, 3.6, 2.0, 3.8), "crimson", tag="puff")
        k.box(fo, C(x, 14, 0, 3.0, 7.2, 3.2), "black", tag="sleeve")
        k.box(hn, C(x, 11.4, 0.3, 2.6, 2.6, 2.6), "black", tag="glove")
    rp = k.part("rapier", (-6, 12.6, 0.6), (("x", 80),), k.parts["hand_r"])
    k.box(rp, C(-6, 10.0, 0.6, 1.0, 4.6, 1.0), "black", tag="grip")
    k.ring(rp, -6, 14.6, 0.6, 1.8, 0.4, "silver", "swept_hilt", n=10, axis="x")
    k.box(rp, C(-6, 14.4, 0.6, 0.6, 0.8, 5.0), "silver", tag="quillon")
    k.box(rp, C(-6, 15, 0.6, 0.4, 24, 0.7), "silver", tag="blade")
    mg = k.part("main_gauche", (6, 12.6, 0.6), (("x", 60),), k.parts["hand_l"])
    k.box(mg, C(6, 10.0, 0.6, 1.0, 4.0, 1.0), "black", tag="grip")
    k.box(mg, C(6, 13.8, 0.6, 1.0, 1.0, 6.0), "silver", tag="quillon")
    k.box(mg, C(6, 14, 0.6, 0.6, 9, 1.4), "silver", tag="blade")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Blood Thrall (swarm)

def blood_thrall():
    """The Countess's servants: drained pale as paper and fed on her blood until they would die for her, which they
    did. Livery of black and crimson, white gloves, a powdered wig gone grey, and a silver tray held up on one
    hand as if serving - under it, in the other hand, the knife. Their eyes are red and their mouths are wet."""
    k = X.Kit("blood_thrall")
    hips = k.part("hips", (0, 18, 0))
    k.box(hips, C(0, 15.6, 0, 7.0, 3.6, 4.8), "crimson", tag="breeches")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.0
        th = k.part("thigh_" + nm, (x, 18, 0), (("x", -6 if side > 0 else 4), ("z", side * 4)), "hips")
        sh = k.part("shin_" + nm, (x, 9.6, 0), (("x", 8),), th)
        ft = k.part("foot_" + nm, (x, 2.0, 0), (("x", -4),), sh)
        k.box(th, C(x, 9.8, 0, 3.0, 8.4, 3.2), "crimson", tag="thigh")
        k.box(sh, C(x, 2.0, 0, 2.6, 7.8, 2.8), "lace", tag="stocking")
        k.box(ft, C(x, 0, 1.2, 2.8, 2.0, 5.0), "black", tag="foot")
        k.box(ft, C(x, 1.8, 2.6, 1.6, 0.6, 0.8), "silver", tag="buckle")
    # ---------------------------------------------------------------- torso: the livery coat
    to = k.part("torso", (0, 18, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(18, 7.4, 5.0), (23, 8.6, 5.4), (28, 9.6, 5.6)], "velvet", "livery")
    for sx in (-1, 1):
        k.box(to, C(sx * 2.4, 9, 2.6, 2.8, 10, 0.6), "velvet", tag="coat_tail")
        k.box(to, C(sx * 2.4, 9, -2.6, 2.8, 10, 0.6), "velvet", tag="coat_tail")
        for y in (20, 22.6, 25.2):
            k.box(to, C(sx * 1.8, y, 2.85, 0.8, 0.8, 0.4), "silver", tag="button")
    k.box(to, C(0, 26.6, 3.0, 2.6, 1.6, 0.6), "lace", tag="jabot")
    # ---------------------------------------------------------------- the head: paper-pale, a grey wig, a wet red mouth
    hd = k.part("head", (0, 28.4, 0.4), (("x", -10), ("z", 10)), "torso")
    k.box(hd, C(0, 28.4, 0.4, 4.6, 5.4, 4.8), "wax", tag="face")
    for sx in (-1.0, 1.0):
        k.box(hd, C(sx, 31.0, 2.85, 1.0, 0.6, 0.3), "eye", group="glow", tag="eye")
        k.box(hd, C(sx * 1.4, 30.2, 2.85, 0.8, 0.4, 0.3), "dark", tag="eye_bag")
    k.box(hd, C(0, 29.4, 2.85, 2.0, 0.6, 0.3), "gore", tag="mouth")
    drip(k, hd, 0.4, 29.2, 2.9, 1.4, w=0.4)
    k.box(hd, C(0, 33.2, -0.2, 5.6, 2.2, 5.6), "lace", tag="wig")
    for sx in (-1, 1):
        k.blob(hd, (sx * 2.8, 30.6, -0.4), (0.9, 1.4, 1.4), "lace", "wig_curl", step=0.6)
    k.box(hd, C(0, 28, -3.2, 1.6, 4, 1.0), "lace", tag="queue")
    k.box(hd, C(0, 30.6, -3.8, 2.0, 1.0, 0.6), "black", tag="ribbon")
    # ---------------------------------------------------------------- arms: the tray held up, the knife under it
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.6
        up = k.part("arm_" + nm, (x, 26.6, 0), (("x", -60 if side > 0 else -40), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 19.6, 0), (("x", -60 if side > 0 else -50),), up)
        hn = k.part("hand_" + nm, (x, 12.6, 0), (), fo)
        k.box(up, C(x, 19.8, 0, 2.8, 7.0, 3.0), "velvet", tag="sleeve")
        k.box(fo, C(x, 12.8, 0, 2.6, 7.0, 2.8), "velvet", tag="sleeve")
        k.box(fo, C(x, 13.0, 0, 3.2, 1.2, 3.4), "silver", tag="cuff")
        k.box(hn, C(x, 10.4, 0.3, 2.4, 2.4, 2.4), "lace", tag="glove")
    tr = k.part("tray", (5.6, 10, 2), (("x", 90),), k.parts["hand_l"])
    k.box(tr, C(5.6, 9.4, 2, 9, 0.6, 9), "silver", tag="tray")
    k.ring(tr, 5.6, 10.0, 2, 4.6, 0.6, "silver", "tray_rim", n=14, axis="y")
    k.box(tr, C(5.6, 10.0, 2, 2.0, 2.6, 2.0), "crimson", tag="goblet")
    kn = k.part("knife", (-5.6, 11.6, 0.6), (("x", 100),), k.parts["hand_r"])
    k.box(kn, C(-5.6, 9.6, 0.6, 0.9, 3.0, 0.9), "black", tag="grip")
    k.box(kn, C(-5.6, 12.6, 0.6, 0.5, 6.0, 1.4), "silver", tag="blade")
    k.box(kn, C(-5.6, 15, 1.2, 0.6, 3.0, 0.4), "gore", tag="blade_blood")
    k.s.shaders = shaders()
    return k.s, k.parts


MOBS = {
    "blood_thrall": dict(make=blood_thrall, ent=(0.8, 2.5), stats=dict(hp=30, speed=0.3, dmg=7, armor=3, kb=0)),
    "gorged_butler": dict(make=gorged_butler, ent=(1.7, 3.6), stats=dict(hp=130, speed=0.19, dmg=17, armor=8, kb=0.9)),
    "blood_mage": dict(make=blood_mage, ent=(0.9, 2.9), stats=dict(hp=48, speed=0.22, dmg=8, armor=3, kb=0)),
    "duelist": dict(make=duelist, ent=(0.8, 2.9), stats=dict(hp=42, speed=0.36, dmg=9, armor=5, kb=0)),
    "counts_hound": dict(make=counts_hound, rig="crawler", ent=(2.0, 2.4), stats=dict(hp=250, speed=0.34, dmg=15, armor=8, kb=0.7), key=True),
    "countess_vael": dict(make=countess_vael, texel=1, ent=(2.6, 6.4), stats=dict(hp=700, speed=0.24, dmg=22, armor=10, kb=0.9), boss=True),
}
