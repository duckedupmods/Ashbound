"""The Thornborn: briar-folk grown out of the jungle's old sanctuaries, who hold the world's tree houses, thorn
towers, jungle keeps and sanctuaries, built by hand (tools/vox2.py). Dark bark and black-green briar, thorns pale
at their tips, blooms the red of blood, and the amber of the sap that runs in them in their eyes and their hearts.
(Not Rotwood's moss and rot, not the Ziggurat's jaguar-men: these are the jungle's own thorns, grown into people.)

    thorn_beetle   swarm   a beetle whose shell is a knot of briar, a red rose open on its back
    briar_warden   guard   briars woven into a man, bark plates, a carved wooden mask, a thorn spear and a wicker shield
    bramble_brute  brute   a giant tangle of bramble in a man's shape, its chest hollow and full of glowing sap,
                           thorn clubs for fists
    bloom_witch    caster  a woman whose head is a great red flower, the face in its heart, a gown of vines
    thorn_dancer   skirm   lean and quick, a thorn whip in each hand trailing to the ground
    rose_knight    elite   armour of bark and black thorns, a helm like a closed rosebud, a cape of red petals, a
                           greatsword of thorn-wood with a rose for a guard

    python tools/monsterforge.py thornborn --preview ; python tools/mobsheet.py thornborn
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import grow
from _folk import lit, eyes, legs, arms, held, quad

BARK = ramp("#0c0806", "#160f0a", "#22170f", "#2e2014", "#3c2a1a", "#4c3622")
BRIAR = ramp("#060a06", "#0c140c", "#122014", "#1a2c1a", "#243a22", "#30482a")
LEAF = ramp("#0a1a0a", "#122a10", "#1c3c16", "#28501e", "#366628", "#467e34")
THORN = ramp("#2a2618", "#4a4430", "#6e6648", "#948a64", "#b8ae84", "#d8d0a8")
ROSE = ramp("#1a0206", "#32040c", "#520814", "#740e1e", "#98182a", "#ba283a")
WICKER = ramp("#1a120a", "#2c2012", "#40301c", "#564226", "#6c5430")
SAP = ramp("#4a2002", "#7a3a04", "#b8640a", "#ea9a1e", "#ffc860", "#fff0b8")
POLLEN = ramp("#5a4a04", "#8a760a", "#c0a81a", "#e8d23e", "#fff08a")


def shaders():
    return {
        "bark": X.surf(BARK, 0.5, 1.2, 0.22, 0.1, stripe=3),
        "briar": X.surf(BRIAR, 0.5, 1.1, 0.24, 0.06, pattern=lambda p, n, i, j, w, h: -0.2 if (i + j * 2) % 5 == 0 else 0.04),
        "leaf": X.surf(LEAF, 0.5, 1.1, 0.2, 0.04, pattern=lambda p, n, i, j, w, h: 0.14 if (i - j) % 4 == 0 else 0.0),
        "thorn": X.surf(THORN, 0.56, 1.3, 0.12, 0.16),
        "rose": X.surf(ROSE, 0.54, 1.2, 0.14, 0.08, pattern=lambda p, n, i, j, w, h: -0.18 if (i + j) % 3 == 0 else 0.04),
        "wicker": X.surf(WICKER, 0.5, 1.1, 0.2, 0.04, pattern=lambda p, n, i, j, w, h: -0.24 if (i % 2) != (j % 2) else 0.06),
        "wood": X.surf(WICKER, 0.5, 1.0, 0.18, 0.06, stripe=4),
        "sap": X.glow(SAP),
        "eye": X.glow(SAP, 0.84, 0.14),
        "pollen": X.glow(POLLEN, 0.7, 0.3),
        "dark": X.dark(BRIAR),
    }


GLOWS = {"sap", "eye", "pollen"}


def thorns(k, part, at, n, L, up=(0, 1, 0), seed=1, spread=0.7):
    k.cluster(part, at, n, L, L * 0.34, mat="thorn", seed=seed, spread=spread, up=up)


def rose(k, part, c, s=1.0, axis="y", mat="rose"):
    """a red rose, open: rings of petals round a dark heart, facing along axis"""
    cx, cy, cz = c
    for i, r in enumerate((2.2, 1.6, 1.0)):
        for j in range(5):
            a = j * 2 * math.pi / 5 + i * 0.6
            dx, dz = math.cos(a) * r * s, math.sin(a) * r * s
            if axis == "y":
                k.box(part, C(cx + dx, cy + i * 0.5 * s, cz + dz, 1.6 * s, 1.0 * s, 1.6 * s), mat, tag="petal")
            else:
                k.box(part, C(cx + dx, cy + dz - 0.8 * s, cz + i * 0.5 * s, 1.6 * s, 1.6 * s, 1.0 * s), mat, tag="petal")
    if axis == "y":
        k.box(part, C(cx, cy + 1.4 * s, cz, 0.8 * s, 0.6 * s, 0.8 * s), "dark", tag="rose_heart")
    else:
        k.box(part, C(cx, cy - 0.4 * s, cz + 1.4 * s, 0.8 * s, 0.8 * s, 0.6 * s), "dark", tag="rose_heart")


def briar_wrap(k, part, x, y0, y1, r, seed=0):
    """briar wound round a limb in a spiral, thorns standing off it"""
    n = int((y1 - y0) / 1.6)
    for i in range(n):
        a = i * 1.3 + seed
        y = y0 + i * 1.6
        k.box(part, C(x + math.cos(a) * r, y, math.sin(a) * r, 1.0, 1.0, 1.0), "briar", tag="briar_coil")
        if i % 2 == 0:
            k.shard(part, (x + math.cos(a) * (r + 0.4), y + 0.5, math.sin(a) * (r + 0.4)), (math.cos(a), 0.3, math.sin(a)), 1.4, 0.5, mat="thorn", tag="thorn")


# ================================================================ the Thorn Beetle (swarm)

def thorn_beetle():
    """The Thornborn's beetles carry their roses for them: a beetle as big as a hound whose shell is a knot of black
    briar grown tight, thorns all over it, a red rose wide open on its back and the sap glowing in its joints."""
    k = X.Kit("thorn_beetle")
    body, hd, ab, joints = quad(k, "bark", y=8, chest=((3, 10, 10), (6, 11, 11), (9, 9.4, 9.4)), haunch=((3, 10, 9), (6, 11.6, 10), (9.6, 10, 9)),
                                leg_w=1.8, foot_w=1.4, front_z=3, back_z=-5, x=6.0, head_at=(0, 7, 6), head_rot=6, claw="thorn", foot_len=3.0,
                                knees=(3.0, -3.0))
    k.blob(ab, (0, 11.4, -2.6), (7.0, 4.6, 8.4), "briar", "briar_shell", step=0.8)
    for i in range(10):
        a = i * 2.399
        k.shard(ab, (math.cos(a) * 5.0, 12.0 + (i % 3) * 1.4, -2.6 + math.sin(a) * 6.0), (math.cos(a) * 0.6, 1, math.sin(a) * 0.6), 2.4, 0.8, mat="thorn", tag="thorn")
    rose(k, ab, (0, 15.4, -2.0), 1.4)
    for sx in (-1, 1):
        k.box(body, C(sx * 4.4, 5.6, 2.6, 1.0, 1.0, 1.0), "sap", tag="joint_glow")
    k.box(hd, C(0, 4.0, 8.4, 6.4, 4.0, 4.4), "bark", tag="head")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.0, 6.6, 10.5, 1.4, 1.0, 0.4), "eye", tag="eye")
        k.limb(hd, (sx * 2.0, 4.6, 10.4), (sx * 2.6, 5.4, 14.6), 1.2, "thorn", "pincer")
        k.limb(hd, (sx * 2.6, 5.4, 14.6), (sx * 0.8, 5.2, 16.4), 1.0, "thorn", "pincer")
    k.shard(hd, (0, 8.0, 9.0), (0, 0.8, 0.6), 4.4, 1.6, mat="thorn", tag="horn")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Briar Warden (guard)

def briar_warden():
    """The sanctuaries' guards were grown, not born: briars woven tight into the shape of a man and plated with bark,
    leaves for a mantle, a mask carved from heartwood with the sap glowing behind its eyes, a wicker shield thick
    with thorns and a spear of black thorn-wood."""
    k = X.Kit("briar_warden")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(12, 11.0, 7.8), (20, 11.0, 7.8)], "briar", "hips")
    for i, x in enumerate((-4.2, -1.4, 1.4, 4.2)):            # a skirt of hanging leaves
        k.box(hips, C(x, 10.0 + (i % 2), 3.6, 2.6, 6.0, 0.6), "leaf", tag="leaf_skirt")
        k.box(hips, C(x, 10.0 + (i % 2), -3.6, 2.6, 6.0, 0.6), "leaf", tag="leaf_skirt")
    k.box(hips, C(0, 18.4, 0, 11.6, 2.0, 8.4), "bark", tag="belt")
    legs(k, hips, 19, 10.4, 3.2, "briar", "bark", knee_mat="bark", lean=-6, bend=8, w=4.8, cuff=False)
    for side in (1, -1):
        briar_wrap(k, k.parts["shin_" + ("l" if side > 0 else "r")], side * 3.2, 3.0, 9.6, 2.8, seed=side)
    to = k.part("torso", (0, 20, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(20, 11.0, 7.8), (25, 12.4, 8.2), (30, 14.4, 8.8), (34, 14.0, 8.4)], "briar", "torso")
    for i, (y, w) in enumerate(((21.0, 9.6), (24.4, 10.4), (27.8, 11.4))):     # bark plates overlapping
        k.box(to, C(0, y, 4.0 + i * 0.1, w, 3.8, 0.9), "bark", tag="bark_plate")
    k.box(to, C(0, 30.0, 4.6, 2.4, 2.4, 0.4), "sap", tag="heart_sap")
    k.blob(to, (0, 33.4, -0.4), (9.0, 2.4, 6.0), "leaf", "leaf_mantle", step=0.7)
    for sx in (-1, 1):
        thorns(k, to, (sx * 7.4, 33.0, 0), 4, 3.0, up=(sx * 0.6, 1, 0), seed=sx + 3)
    hd = k.part("head", (0, 34, 0.6), (("x", -4),), "torso")
    k.box(hd, C(0, 34.4, 0.6, 6.4, 7.0, 6.4), "briar", tag="head")
    k.box(hd, C(0, 33.8, 3.6, 6.0, 7.4, 1.2), "wood", tag="mask")              # the carved mask
    k.box(hd, C(0, 38.6, 4.3, 6.4, 1.0, 0.6), "wood", tag="mask_brow")
    k.box(hd, C(0, 35.6, 4.3, 1.2, 2.6, 0.8), "wood", tag="mask_nose")
    eyes(k, hd, 37.4, 4.3, 1.4, 1.4, h=0.8)
    for x in (-1.6, 0, 1.6):
        k.box(hd, C(x, 34.2, 4.3, 0.5, 0.8, 0.3), "dark", tag="mask_teeth")
    for i in range(7):                            # a crown of thorns grown out of the head
        a = math.radians(-90 + i * 30)
        k.shard(hd, (math.sin(a) * 3.0, 41.0, 0.6 + math.cos(a) * 3.0), (math.sin(a) * 0.5, 1, math.cos(a) * 0.4), 3.4, 0.9, mat="thorn", tag="thorn_crown")
    arms(k, to, 7.6, 32, "briar", {1: ((("x", -40), ("z", -8)), (("x", -40),)), -1: ((("x", -30), ("z", 8)), (("x", -48),))}, glove="bark", w=3.4)
    for side in (1, -1):
        briar_wrap(k, k.parts["fore_" + ("l" if side > 0 else "r")], side * 7.6, 17.0, 23.0, 2.0, seed=side + 4)
    sh = held(k, "shield", "l", (7.6, 13, 0.4), (("x", 80),))
    k.box(sh, C(7.0, 4.0, 3.0, 10.0, 16.0, 1.4), "wicker", tag="wicker_shield")
    k.box(sh, C(7.0, 3.6, 3.0, 10.8, 1.0, 1.8), "bark", tag="shield_rim")
    k.box(sh, C(7.0, 19.6, 3.0, 10.8, 1.0, 1.8), "bark", tag="shield_rim")
    for i in range(10):
        k.shard(sh, (7.0 + ((i * 3) % 9 - 4.0), 5.0 + (i * 7 % 13), 3.8), (0, 0.1, 1), 2.4, 0.8, mat="thorn", tag="shield_thorn")
    rose(k, sh, (7.0, 12.0, 3.8), 1.2, axis="z")
    sp = held(k, "spear", "r", (-7.6, 14.0, 0.3), (("x", 100),))
    k.limb(sp, (-7.6, -6.0, 0.3), (-7.6, 30.0, 0.3), 1.4, "bark", "thorn_shaft")
    for y in (2.0, 10.0, 18.0, 26.0):
        k.shard(sp, (-7.6, y, 1.0), (0, 0.4, 1), 1.4, 0.6, mat="thorn", tag="shaft_thorn")
    k.shard(sp, (-7.6, 30.0, 0.3), (0, 1, 0), 8.0, 2.0, mat="thorn", tag="spear_thorn")
    k.box(sp, C(-7.6, 29.0, 0.3, 2.0, 1.2, 2.0), "sap", tag="sap_drop")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Bramble Brute (brute)

def bramble_brute():
    """Where a sanctuary's hedge grew wild for a thousand years it got up and walked. A giant tangle of bramble as
    thick as a man's arm in a man's shape, its chest open like a cage with the sap pooled and glowing inside it,
    leaves and roses caught in it, and fists that are clubs of knotted thorn."""
    k = X.Kit("bramble_brute")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(12, 14.0, 10.0), (21, 15.0, 10.6)], "briar", "hips")
    legs(k, hips, 20, 11.0, 4.8, "briar", "briar", knee_mat="bark", lean=-4, bend=6, w=7.0, cuff=False)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        briar_wrap(k, k.parts["thigh_" + nm], side * 4.8, 12.0, 19.6, 4.0, seed=side + 1)
        briar_wrap(k, k.parts["shin_" + nm], side * 4.8, 2.4, 10.4, 3.8, seed=side + 2)
        for t in (-2.4, 0, 2.4):
            k.limb(k.parts["foot_" + nm], (side * 4.8 + t, 1.0, 3.0), (side * 4.8 + t * 1.6, 0.4, 7.4), 1.4, "bark", "root_toe")
    to = k.part("torso", (0, 21, 0), (("x", 14),), "hips")
    # the chest: a cage of thick bramble round a pool of sap
    for i in range(10):
        a = i * 2 * math.pi / 10
        x, z = math.cos(a) * 10.0, math.sin(a) * 6.4
        k.limb(to, (x * 0.7, 21.0, z * 0.7), (x, 30.0, z), 2.6, "briar", "cage_bramble")
        k.limb(to, (x, 30.0, z), (x * 0.8, 37.0, z * 0.8), 2.4, "briar", "cage_bramble")
    k.blob(to, (0, 27.0, 0), (6.4, 5.4, 4.0), "sap", "sap_heart", step=0.8)
    for y in (24.0, 31.0):
        k.ring(to, 0, y, 0, 10.4, 2.0, "bark", "bramble_band", n=16, axis="y")
    for i in range(14):
        a = i * 2.399
        k.shard(to, (math.cos(a) * 10.4, 22.0 + (i * 0.618 % 1) * 14.0, math.sin(a) * 6.6), (math.cos(a), 0.3, math.sin(a)), 3.0, 1.0, mat="thorn", tag="thorn")
    for (x, y, z) in ((-8.0, 34.0, 4.4), (6.4, 26.0, 5.6), (9.0, 33.0, -3.0)):
        rose(k, to, (x, y, z), 1.1)
    k.blob(to, (0, 36.6, 0), (9.0, 2.4, 6.0), "leaf", "leaf_shoulders", step=0.7)
    hd = k.part("head", (0, 37.0, 3.0), (("x", -14),), "torso")
    k.blob(hd, (0, 40.4, 3.4), (4.4, 4.0, 4.0), "briar", "head_tangle", step=0.7)
    k.box(hd, C(0, 39.4, 6.8, 6.0, 3.0, 1.2), "dark", tag="face_hollow")
    eyes(k, hd, 40.4, 7.5, 1.8, 1.4, h=0.9)
    thorns(k, hd, (0, 43.6, 2.6), 6, 4.0, up=(0, 1, -0.3), seed=17)
    arms(k, to, 12.6, 34, "briar", {1: ((("x", -50), ("z", -18)), (("x", -40),)), -1: ((("x", -66), ("z", 18)), (("x", -30),))}, w=6.0, long=1.15)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        briar_wrap(k, k.parts["arm_" + nm], side * 12.6, 26.0, 33.0, 3.4, seed=side + 6)
        for b in list(k.s.boxes):
            if b.part is k.parts["hand_" + nm]:
                k.s.boxes.remove(b)
        y = 34 - 8 * 1.15 - 7.6 * 1.15
        k.blob(k.parts["hand_" + nm], (side * 12.6, y - 3.4, 0.4), (4.4, 4.4, 4.4), "bark", "thorn_club", step=0.8)
        for i in range(9):
            a = i * 2.399
            k.shard(k.parts["hand_" + nm], (side * 12.6 + math.cos(a) * 4.0, y - 3.4 + math.sin(a) * 3.6, 0.4 + math.cos(a * 1.7) * 3.6),
                    (math.cos(a), math.sin(a), math.cos(a * 1.7)), 3.4, 1.2, mat="thorn", tag="club_thorn")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.3)
    return k.s, k.parts


# ================================================================ the Bloom Witch (caster)

def bloom_witch():
    """The sanctuaries' priestesses gave their heads to the flower. A woman's body in a gown of vines and leaves,
    long green arms, and where her head was a great red bloom, the petals curling back, and in its heart her face,
    small and calm, the sap shining in her eyes; the pollen hangs round her, gold and glowing."""
    k = X.Kit("bloom_witch")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(1, 13.4, 11.4), (9, 11.6, 9.4), (20, 10.2, 7.6)], "leaf", "vine_gown", step=1.0)
    for i in range(12):                           # vines trailing from the hem
        a = i * 2 * math.pi / 12
        k.limb(hips, (math.cos(a) * 6.4, 2.0, math.sin(a) * 5.4), (math.cos(a) * 8.6, 0.4, math.sin(a) * 7.4), 0.8, "briar", "trailing_vine")
    for i in range(6):
        a = i * 1.1
        rose(k, hips, (math.cos(a) * 5.6, 6.0 + i * 2.0, math.sin(a) * 4.6), 0.7)
    for side, nm in ((1, "l"), (-1, "r")):
        th = k.part("thigh_" + nm, (side * 3.0, 19, 0), (), hips)
        sh = k.part("shin_" + nm, (side * 3.0, 10.4, 0), (), th)
        ft = k.part("foot_" + nm, (side * 3.0, 2.4, 0), (), sh)
        k.box(ft, C(side * 3.0, 0, 3.0, 3.4, 1.4, 4.0), "bark", tag="foot")
    to = k.part("torso", (0, 20, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(20, 10.2, 7.6), (25, 10.4, 7.4), (30, 11.6, 7.6), (33, 10.4, 7.0)], "leaf", "bodice")
    for y in (22.0, 25.4, 28.8):
        k.limb(to, (-5.0, y, 3.8), (5.0, y + 1.6, 3.8), 0.7, "briar", "vine_lace", d=0.4)
    hd = k.part("head", (0, 33, 0.6), (("x", -6),), "torso")
    k.limb(hd, (0, 33.0, 0.6), (0, 36.0, 1.0), 2.4, "leaf", "stem_neck")
    for i in range(10):                           # the bloom: two rings of great petals curling back, the face in the heart
        a = i * 2 * math.pi / 10
        r0 = 3.0 if i % 2 else 3.4
        p0 = (math.cos(a) * r0, 39.4 + math.sin(a) * r0, 2.0)
        p1 = (math.cos(a) * (r0 + 4.4), 39.4 + math.sin(a) * (r0 + 4.4), 0.4)
        k.limb(hd, p0, p1, 3.6 if i % 2 else 3.0, "rose", "great_petal", d=0.8)
        k.limb(hd, p1, (math.cos(a) * (r0 + 6.0), 39.4 + math.sin(a) * (r0 + 6.0), -1.8), 2.4, "rose", "petal_curl", d=0.6)
    k.box(hd, C(0, 37.0, 1.2, 4.4, 5.0, 1.8), "dark", tag="bloom_heart")
    k.box(hd, C(0, 37.6, 2.2, 3.2, 3.6, 1.0), "leaf", tag="face")
    eyes(k, hd, 39.6, 3.25, 0.8, 0.9, h=0.6)
    k.box(hd, C(0, 37.8, 3.25, 1.0, 0.4, 0.3), "dark", tag="mouth")
    for i in range(6):                            # stamens
        a = i * math.pi / 3
        k.limb(hd, (math.cos(a) * 2.0, 39.4 + math.sin(a) * 2.0, 2.6), (math.cos(a) * 2.6, 39.4 + math.sin(a) * 2.6, 4.2), 0.4, "leaf", "stamen")
        k.box(hd, C(math.cos(a) * 2.6, 39.4 + math.sin(a) * 2.6 - 0.3, 4.2, 0.7, 0.7, 0.7), "pollen", tag="anther")
    arms(k, to, 6.6, 31, "leaf", {1: ((("x", -80), ("z", -20)), (("x", -10),)), -1: ((("x", -80), ("z", 20)), (("x", -10),))}, w=2.8, long=1.15)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        briar_wrap(k, k.parts["fore_" + nm], side * 6.6, 15.0, 22.0, 1.6, seed=side + 9)
        y = 31 - 8 * 1.15 - 7.6 * 1.15
        for t in (-0.8, 0, 0.8):
            k.limb(k.parts["hand_" + nm], (side * 6.6 + t, y - 2.6, 1.0), (side * 6.6 + t * 1.6, y - 6.4, 1.8), 0.5, "leaf", "finger")
        k.blob(k.parts["hand_" + nm], (side * 6.6, y - 6.0, 4.0), (1.4, 1.4, 1.4), "pollen", "pollen_ball", step=0.5)
    for i in range(8):                            # the pollen hanging round her
        a = i * 2.399
        k.box(to, C(math.cos(a) * 9.0, 20.0 + (i * 0.618 % 1) * 16.0, math.sin(a) * 7.0, 0.8, 0.8, 0.8), "pollen", tag="pollen_mote")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Thorn Dancer (skirmisher)

def thorn_dancer():
    """They fight like the jungle grows, never still. Lean and long-limbed, briar for sinew and bark for skin, a
    mantle of long leaves that whips round as they turn, a thorn mask, and a whip of thorned vine in each hand,
    longer than they are tall, trailing on the ground behind them."""
    k = X.Kit("thorn_dancer")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(14, 9.6, 7.0), (20, 9.8, 7.2)], "bark", "hips")
    for i in range(8):                            # long leaves for a skirt, swirling
        a = i * 2 * math.pi / 8
        k.limb(hips, (math.cos(a) * 4.6, 18.0, math.sin(a) * 3.6), (math.cos(a + 0.5) * 7.4, 8.0, math.sin(a + 0.5) * 6.0), 2.4, "leaf", "leaf_skirt", d=0.5)
    legs(k, hips, 19, 10.4, 2.8, "briar", "bark", knee_mat="bark", lean=-14, bend=22, w=4.2, cuff=False)
    to = k.part("torso", (0, 20, 0), (("x", 14), ("y", 20)), "hips")
    k.stack(to, 0, 0, [(20, 9.8, 7.2), (25, 10.2, 7.0), (29.6, 12.4, 7.6), (32.6, 11.4, 7.0)], "briar", "torso")
    k.box(to, C(0, 22.0, 3.6, 7.0, 8.4, 0.6), "bark", tag="bark_plate")
    for sx in (-1, 1):
        thorns(k, to, (sx * 5.6, 31.0, -1.0), 3, 2.6, up=(sx * 0.4, 0.6, -0.8), seed=sx + 21)
    hd = k.part("head", (0, 32.6, 0.6), (("x", -14),), "torso")
    k.box(hd, C(0, 33.0, 0.6, 5.6, 6.6, 5.8), "bark", tag="head")
    k.box(hd, C(0, 35.6, 3.5, 5.0, 1.0, 0.4), "dark", tag="eye_slit")
    eyes(k, hd, 35.75, 3.6, 1.2, 1.1, h=0.5)
    for i in range(5):                            # the thorn mask: spines swept back
        a = math.radians(-60 + i * 30)
        k.shard(hd, (math.sin(a) * 2.6, 38.6, 1.4), (math.sin(a) * 0.4, 0.5, -1), 4.4, 0.9, mat="thorn", tag="swept_thorn")
    k.limb(hd, (0, 39.0, -1.6), (0, 32.0, -6.6), 3.0, "leaf", "leaf_hair", d=0.5)
    arms(k, to, 6.4, 30, "briar", {1: ((("x", -20), ("z", 50)), (("x", -40),)), -1: ((("x", -60), ("z", -40)), (("x", -20),))}, glove="bark", w=2.8, long=1.1)
    for side, nm in ((1, "l"), (-1, "r")):        # the whips: a short handle, then the thorned vine whipping out
        x = side * 6.4
        wp = held(k, "whip_" + nm, nm, (x, 11.8, 0.4), (("x", 30 if side > 0 else 70),))
        k.limb(wp, (x, 9.0, 0.4), (x, 14.6, 0.4), 1.4, "bark", "whip_handle")
        pts = [(x, 14.6, 0.4), (x + side * 2.0, 20.0, 2.0), (x + side * 5.0, 23.0, 6.0), (x + side * 8.4, 22.0, 11.0), (x + side * 10.4, 17.0, 15.0), (x + side * 10.0, 11.0, 17.4)]
        for (a, b), w in zip(zip(pts, pts[1:]), (1.2, 1.1, 1.0, 0.9, 0.8)):
            k.limb(wp, a, b, w, "briar", "whip_vine")
            m = tuple((a[j] + b[j]) * 0.5 for j in range(3))
            k.shard(wp, m, (side * 0.4, 0.6, 0.3), 1.4, 0.5, mat="thorn", tag="whip_thorn")
        k.shard(wp, pts[-1], (0, -1, 0.2), 1.8, 0.6, mat="thorn", tag="whip_tip")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Rose Knight (elite)

def rose_knight():
    """The sanctuaries' champion was grown in armour. Plates of bark edged in black thorn, a helm shaped like a
    rosebud not yet open, its sepals curled round the face and the sap glowing through the slit, a cape of red
    petals overlapping like scales, and a greatsword of black thorn-wood grown straight and sharp, a red rose open
    where the guard should be."""
    k = X.Kit("rose_knight")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(12, 12.0, 8.6), (21, 12.0, 8.6)], "briar", "hips")
    for i, y in enumerate((16.0, 12.6)):
        for sx in (-1, 1):
            k.box(hips, C(sx * 3.6, y, 4.2 + i * 0.3, 5.6, 3.6, 1.0), "bark", tag="tasset")
            k.shard(hips, (sx * 6.2, y + 0.4, 4.4), (sx, -0.3, 0.3), 1.8, 0.6, mat="thorn", tag="tasset_thorn")
    k.box(hips, C(0, 19.6, 0, 13.0, 2.0, 9.4), "bark", tag="belt")
    legs(k, hips, 20, 10.8, 3.6, "briar", "bark", knee_mat="bark", lean=-6, bend=8, w=5.6, cuff=True)
    for side in (1, -1):
        k.shard(k.parts["thigh_" + ("l" if side > 0 else "r")], (side * 3.6, 10.4, 3.4), (0, 0.3, 1), 2.4, 1.0, mat="thorn", tag="knee_thorn")
    to = k.part("torso", (0, 21, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(21, 12.0, 8.6), (26, 13.8, 9.2), (31, 16.8, 10.0), (35, 16.4, 9.4)], "bark", "cuirass")
    k.blob(to, (0, 29.4, 2.4), (6.6, 5.4, 3.4), "bark", "breastplate", step=0.7)
    rose(k, to, (0, 29.0, 5.4), 1.2, axis="z")
    for sx in (-1, 1):
        k.blob(to, (sx * 9.4, 33.6, 0), (4.6, 3.0, 5.0), "bark", "pauldron", step=0.7)
        thorns(k, to, (sx * 10.4, 35.6, 0), 5, 3.6, up=(sx * 0.5, 1, 0), seed=sx + 41)
    cl = k.part("cloak", (0, 34, -5.0), (("x", 5),), to, bone=False)
    for row in range(7):                          # the cape of petals, overlapping like scales
        y = 34.0 - row * 4.2
        for i in range(5 - (row > 4)):
            x = -6.0 + i * 3.0 + (row % 2) * 1.5
            k.box(cl, C(x, y - 4.8, -5.4 - row * 0.12, 3.4, 5.0, 0.7), "rose", tag="petal_cape")
    hd = k.part("head", (0, 35.6, 0.6), (("x", -4),), "torso")
    # the rosebud helm: a tall closed bud, the sepals curled round it, a slit
    k.stack(hd, 0, 0.6, [(35.6, 7.4, 7.4), (38, 8.2, 8.2), (41, 7.8, 7.8), (43.6, 6.2, 6.2), (45.6, 4.0, 4.0), (46.8, 2.0, 2.0)], "rose", "bud_helm", step=1.0)
    for i in range(5):                            # the sepals: green leaves up the sides of the bud
        a = i * 2 * math.pi / 5 + 0.3
        k.limb(hd, (math.cos(a) * 3.8, 35.8, 0.6 + math.sin(a) * 3.8), (math.cos(a) * 4.4, 43.0, 0.6 + math.sin(a) * 4.4), 2.6, "leaf", "sepal", d=0.6)
        k.shard(hd, (math.cos(a) * 4.4, 43.0, 0.6 + math.sin(a) * 4.4), (math.cos(a) * 0.4, 1, math.sin(a) * 0.4), 2.0, 1.2, mat="leaf", tag="sepal_tip")
    k.box(hd, C(0, 39.6, 4.5, 5.4, 0.9, 0.4), "dark", tag="slit")
    eyes(k, hd, 39.7, 4.75, 1.4, 1.4, h=0.6)
    arms(k, to, 9.6, 33, "bark", {1: ((("x", -36), ("z", -20)), (("x", -40),)), -1: ((("x", -32), ("z", 18)), (("x", -44),))}, glove="bark", w=3.8)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        briar_wrap(k, k.parts["fore_" + nm], side * 9.6, 17.0, 24.0, 2.4, seed=side + 13)
    gs = held(k, "thorn_sword", "r", (-9.6, 14.0, 0.3), (("x", 78), ("z", -16)))
    k.limb(gs, (-9.6, 6.0, 0.3), (-9.6, 15.8, 0.3), 1.6, "briar", "grip")
    k.shard(gs, (-9.6, 6.0, 0.3), (0, -1, 0), 2.6, 1.6, mat="thorn", tag="pommel_thorn")
    rose(k, gs, (-9.6, 15.6, 0.3), 1.6)           # the rose for a guard
    for sx in (-1, 1):
        k.limb(gs, (-9.6, 16.4, 0.3), (-9.6 + sx * 5.0, 18.0, 0.3), 1.0, "leaf", "guard_leaf", d=0.4)
    for i in range(12):                           # the thorn-wood blade, black, thorns along both edges
        y = 18.6 + i * 2.4
        w = 3.6 - i * 0.16
        k.box(gs, C(-9.6, y, 0.3, w, 2.45, 1.1), "bark", tag="thorn_blade")
        if i % 2 == 0 and i < 10:
            for sx in (-1, 1):
                k.shard(gs, (-9.6 + sx * w * 0.5, y + 1.0, 0.3), (sx, 0.5, 0), 1.6, 0.6, mat="thorn", tag="blade_thorn")
    k.box(gs, C(-9.6, 19.0, 0.9, 0.6, 24.0, 0.3), "sap", tag="blade_sap")
    k.shard(gs, (-9.6, 47.4, 0.3), (0, 1, 0), 4.0, 2.0, mat="thorn", tag="blade_tip")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.15)
    return k.s, k.parts


MOBS = {
    "thorn_beetle": dict(make=thorn_beetle, rig="crawler", ent=(1.2, 1.1), stats=dict(hp=26, speed=0.32, dmg=6, armor=4, kb=0)),
    "briar_warden": dict(make=briar_warden, ent=(0.9, 2.9), stats=dict(hp=60, speed=0.24, dmg=10, armor=8, kb=0.3)),
    "bramble_brute": dict(make=bramble_brute, ent=(1.8, 4.1), stats=dict(hp=200, speed=0.18, dmg=18, armor=6, kb=1.0)),
    "bloom_witch": dict(make=bloom_witch, ent=(0.9, 3.0), stats=dict(hp=38, speed=0.22, dmg=7, armor=2, kb=0)),
    "thorn_dancer": dict(make=thorn_dancer, ent=(0.8, 2.7), stats=dict(hp=42, speed=0.35, dmg=8, armor=3, kb=0)),
    "rose_knight": dict(make=rose_knight, ent=(1.1, 3.6), stats=dict(hp=330, speed=0.25, dmg=15, armor=12, kb=0.6), key=True),
}
