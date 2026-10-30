"""The Jade Monastery's monsters, each built by hand (tools/vox2.py). The monks sat so long at their prayers on the
mountain that the jade grew into them, and they got up again: green jade gone glassy, red lacquer, saffron and
black robes, gold leaf, bronze gone green, granite, and the cold green light of the prayer that holds them.

    jade_acolyte     swarm   a young monk turned to jade, cracked, the light inside, prayer beads, a staff
    stone_lion       brute   the temple's guardian lion off its plinth: curled mane, open jaws, a stone ball under its paw
    incense_monk     caster  a monk with a great censer on his back, burning sticks in his hat, the smoke a green glow
    shadow_monk      skirm   the black-robed monks who kept the doors: a mask, a sash, two hook swords
    fist_abbot       elite   the Abbot: arms like temple beams, iron bracers, a beard to his belt, beads as big as fists
    thousand_hands   boss    the Thousand Hands: a gold statue come alive, a halo of a hundred arms each with a blade,
                             a third eye, a jade crown

    python tools/monsterforge.py jade_monastery --preview ; python tools/mobsheet.py jade_monastery
"""
import math

import vox2 as X
from vox2 import C, ramp

JADE = ramp("#0a2a1a", "#124228", "#1c5c38", "#2a784a", "#3e9660", "#5ab47a", "#8ad6a4")
JGLOW = ramp("#0a4a2a", "#127a44", "#22aa60", "#46d080", "#9af0c0", "#e0fff0")
LACQUER = ramp("#2a0606", "#460a08", "#64120c", "#821c12", "#9e2a1a")
SAFFRON = ramp("#3a1c06", "#5e2e0a", "#8a4610", "#b0601a", "#d07c28", "#e89a40")
BLACK = ramp("#08080a", "#101014", "#18181e", "#22222a", "#2e2e38")
GOLD = ramp("#3a2606", "#5e400c", "#8a6214", "#b48a24", "#dab43c", "#f4d870")
GRANITE = ramp("#2a2a26", "#3e3c36", "#504e48", "#68665e", "#828076", "#9c9a8e")
BRONZE = ramp("#10201a", "#1a3428", "#264a38", "#346048", "#46785c")
SKIN = ramp("#2a1a10", "#422a1a", "#5a3c26", "#744e32", "#8c6240")
IRON = ramp("#0e0e10", "#18181c", "#26262c", "#36363e", "#4a4a52")
WOOD = ramp("#1a1008", "#2a1a0e", "#3c2614", "#50341c", "#664426")
BEARD = ramp("#3a3a3a", "#585858", "#787876", "#9a9a96", "#bcbcb6")
SMOKE = ramp("#4a5a52", "#6a7c74", "#8ea098", "#b4c4bc")


def shaders():
    return {
        "jade": X.surf(JADE, 0.55, 1.5, 0.18, 0.0, pattern=lambda p, n, i, j, w, h: 0.3 if abs(X.fbm(p[0] * 0.4, p[1] * 0.4, p[2] * 0.4) - 0.5) < 0.02 else 0),
        "glow": X.glow(JGLOW),
        "eye": X.glow(JGLOW, 0.82, 0.16),
        "lacquer": X.surf(LACQUER, 0.52, 1.4, 0.12, 0.2),
        "saffron": X.surf(SAFFRON, 0.5, 1.0, 0.2, 0.0, holes=True),
        "robe": X.surf(SAFFRON, 0.5, 1.0, 0.2, 0.0),
        "black": X.surf(BLACK, 0.5, 1.1, 0.2, 0.0, holes=True),
        "gold": X.surf(GOLD, 0.56, 1.4, 0.12, 0.22),
        "granite": X.surf(GRANITE, 0.5, 1.2, 0.3, 0.0, crust=(JADE, 0.06)),
        "bronze": X.surf(BRONZE, 0.52, 1.3, 0.16, 0.18),
        "skin": X.wrinkled(SKIN, 0.7),
        "iron": X.surf(IRON, 0.52, 1.4, 0.16, 0.18),
        "wood": X.surf(WOOD, 0.5, 1.0, 0.2, 0.06, stripe=3),
        "beard": X.surf(BEARD, 0.5, 0.9, 0.3, 0.0, stripe=2),
        "smoke": X.surf(SMOKE, 0.6, 0.6, 0.3, 0.0),
        "dark": X.dark(BLACK),
    }


def beads(k, part, cx, cy, cz, r, n, s, mat="wood", axis="z", tag="beads"):
    """a string of prayer beads in a loop"""
    for j in range(n):
        a = j * 2 * math.pi / n
        u, v = math.cos(a) * r, math.sin(a) * r
        x, y, z = {"z": (cx + u, cy + v, cz), "x": (cx, cy + v, cz + u), "y": (cx + u, cy, cz + v)}[axis]
        k.box(part, C(x, y - s / 2, z, s, s, s), mat, tag=tag)


# ================================================================ the Thousand Hands (boss)

def thousand_hands():
    """In the Lotus Throne hall the monks raised a gold image of the Thousand-Handed One, and prayed to it for a
    thousand years, and the jade that took them took it too - and when the gate opened, it stood up. A gold figure
    six blocks high in a jade-green robe with a lacquer sash, a crown of jade and gold, the face serene and terrible,
    the third eye open in its brow. Behind it, fanned out like a halo, a hundred gold arms, each hand holding a
    blade, a bell, a lotus or a bead; and in its own two hands two long jian swords. It does not hurry."""
    k = X.Kit("thousand_hands")
    hips = k.part("hips", (0, 38, 0))
    k.stack(hips, 0, 0, [(28, 18, 13), (38, 19, 13)], "jade", "robe")
    k.box(hips, C(0, 36, 0, 21, 3.0, 15), "lacquer", tag="sash")
    k.box(hips, C(0, 34.4, 7.8, 4.0, 4.0, 1.0), "gold", tag="sash_knot")
    k.limb(hips, (-1.4, 34, 8.0), (-3, 18, 8.6), 2.0, "lacquer", "sash_tail", d=0.6)
    k.limb(hips, (1.4, 34, 8.0), (3, 20, 8.6), 2.0, "lacquer", "sash_tail", d=0.6)
    for i in range(10):          # the robe falling in folds to the feet
        a = math.radians(-150 + i * 33)
        k.box(hips, C(math.sin(a) * 10, 4, math.cos(a) * 7, 5.6, 26, 1.2), "jade", tag="robe_fold",
              rots=(("y", -math.degrees(a)),), pivot=(math.sin(a) * 10, 18, math.cos(a) * 7))
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.4
        th = k.part("thigh_" + nm, (x, 34, 0), (("x", -4), ("z", side * 4)), "hips")
        sh = k.part("shin_" + nm, (x, 18, 0), (("x", 6),), th)
        ft = k.part("foot_" + nm, (x, 4, 0), (), sh)
        k.box(th, C(x, 18, 0, 8.6, 16, 9.0), "jade", tag="robe_leg")
        k.box(sh, C(x, 4, 0, 9.4, 14, 10), "jade", tag="robe_leg")
        k.box(ft, C(x, 0, 2.4, 7.4, 4, 11), "gold", tag="foot")
        for t in (-2.4, -0.8, 0.8, 2.4):
            k.box(ft, C(x + t, 0, 8.0, 1.4, 2.2, 1.6), "gold", tag="foot")
    # ---------------------------------------------------------------- torso: gold, bare-chested, jade necklaces
    to = k.part("torso", (0, 39, 0), (("x", 2),), "hips")
    k.stack(to, 0, 0, [(38, 20, 13.6), (46, 25, 14), (54, 32, 15), (60, 32, 14)], "gold", "torso")
    k.box(to, C(0, 38, 0, 19, 4, 13.4), "jade", tag="robe_top")
    k.limb(to, (12, 60, 0), (-9, 39, 6.8), 3.4, "jade", "robe_drape", d=1.0)
    for r, n in ((7.0, 14), (9.6, 18)):
        beads(k, to, 0, 56, 6.8, r, n, 1.6, mat="jade", axis="z", tag="necklace")
    k.box(to, C(0, 48, 7.2, 4.0, 4.0, 1.2), "glow", group="glow", tag="pendant")
    # the halo of arms: a hundred gold arms fanned behind it, each hand holding something
    halo = k.part("halo", (0, 56, -9), (), to, bone=False)
    k.ring(halo, 0, 60, -9.6, 26, 2.0, "gold", "halo_ring", n=36)
    k.ring(halo, 0, 60, -9.4, 16, 1.4, "gold", "halo_ring", n=28)
    held = ["blade", "blade", "bell", "lotus", "blade", "bead", "blade", "blade", "bell", "lotus"]
    for i in range(28):
        a = math.radians(-200 + i * (220 / 27))
        r0, r1 = 10, 25 + (i % 3) * 2
        p0 = (math.cos(a) * r0, 60 + math.sin(a) * r0, -9 - (i % 2) * 0.6)
        p1 = (math.cos(a) * r1, 60 + math.sin(a) * r1, -10 - (i % 2) * 0.6)
        k.limb(halo, p0, p1, 2.6, "gold", "halo_arm", d=2.2)
        hx, hy, hz = math.cos(a) * (r1 + 1.6), 60 + math.sin(a) * (r1 + 1.6), p1[2]
        k.box(halo, C(hx, hy - 1.6, hz, 3.2, 3.2, 2.4), "gold", tag="halo_hand")
        what = held[i % len(held)]
        if what == "blade":
            k.shard(halo, (hx, hy, hz), (math.cos(a), math.sin(a), 0), 7, 1.2, mat="iron", tag="halo_blade")
        elif what == "bell":
            k.box(halo, C(hx + math.cos(a) * 2.4, hy + math.sin(a) * 2.4 - 1.4, hz, 2.6, 2.8, 2.6), "bronze", tag="halo_bell")
        elif what == "lotus":
            k.blob(halo, (hx + math.cos(a) * 2.4, hy + math.sin(a) * 2.4, hz), (1.8, 1.2, 1.8), "glow", "halo_lotus", step=0.6)
        else:
            k.box(halo, C(hx + math.cos(a) * 2.2, hy + math.sin(a) * 2.2 - 0.9, hz, 1.8, 1.8, 1.8), "jade", tag="halo_bead")
    k.blob(halo, (0, 60, -10.6), (9, 9, 0.8), "glow", "halo_light", step=1.0)
    # ---------------------------------------------------------------- the head: serene and terrible, the third eye, the crown
    hd = k.part("head", (0, 60, 1), (), "torso")
    k.box(hd, C(0, 60.4, 1.0, 8.4, 10, 8.6), "gold", tag="face")
    k.box(hd, C(0, 66.4, 5.35, 7.0, 0.8, 0.5), "dark", tag="brow")
    for sx in (-2.0, 2.0):
        k.box(hd, C(sx, 64.6, 5.3, 2.4, 0.8, 0.4), "dark", tag="eye_lid")
        k.box(hd, C(sx, 64.6, 5.45, 1.8, 0.5, 0.3), "eye", group="glow", tag="eye")
        k.box(hd, C(sx * 2.2, 60.0, 0.6, 1.4, 6.0, 1.6), "gold", tag="long_ear")
    k.box(hd, C(0, 66.8, 5.45, 1.0, 1.8, 0.4), "eye", group="glow", tag="third_eye")
    k.box(hd, C(0, 62.4, 5.6, 1.6, 2.4, 1.0), "gold", tag="nose")
    k.box(hd, C(0, 61.4, 5.35, 2.6, 0.5, 0.4), "lacquer", tag="lips")
    for i in range(5):           # the crown: five jade petals in a gold band
        a = math.radians(-60 + i * 30)
        k.shard(hd, (math.sin(a) * 4.2, 70, 1 + math.cos(a) * 4.0), (math.sin(a) * 0.3, 1, math.cos(a) * 0.3), 6 if i == 2 else 4.6, 3.0,
                mat="jade", tag="crown_petal")
    k.box(hd, C(0, 69.6, 1.0, 9.4, 1.6, 9.4), "gold", tag="crown_band")
    k.box(hd, C(0, 72.6, 1.0, 3.0, 4.4, 3.0), "gold", tag="topknot")
    # ---------------------------------------------------------------- its own two arms and the two jian
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 15
        up = k.part("arm_" + nm, (x, 58, 0), (("x", -50), ("z", side * 20)), "torso")
        fo = k.part("fore_" + nm, (x, 44, 0), (("x", -40),), up)
        hn = k.part("hand_" + nm, (x, 30, 0), (), fo)
        k.blob(up, (x, 57, 0), (5.4, 4.4, 5.6), "gold", "shoulder")
        k.stack(up, x, 0, [(44, 6.6, 6.8), (58, 7.6, 7.8)], "gold", "upper_arm")
        k.stack(fo, x, 0, [(31, 6.0, 6.2), (44, 6.8, 7.0)], "gold", "forearm")
        for y in (34, 36.4):
            k.box(fo, C(x, y, 0, 7.6, 1.4, 7.8), "jade", tag="bangle")
        k.box(hn, C(x, 25, 0.6, 5.8, 6.0, 5.8), "gold", tag="hand")
        jn = k.part("jian_" + nm, (x, 26, 0.6), (("x", 80),), hn)
        k.box(jn, C(x, 21, 0.6, 2.0, 7.0, 2.0), "lacquer", tag="grip")
        k.box(jn, C(x, 27.6, 0.6, 2.6, 1.6, 7.0), "gold", tag="guard")
        k.box(jn, C(x, 29.2, 0.6, 1.0, 34, 3.4), "iron", tag="blade")
        k.box(jn, C(x, 29.2, 0.6, 1.2, 34, 0.6), "jade", tag="blade_ridge")
        k.shard(jn, (x, 63.2, 0.6), (0, 1, 0), 3.4, 3.4, mat="iron", tag="blade")
        k.limb(jn, (x, 20, 0.6), (x + side * 0.6, 12, 2.0), 1.0, "lacquer", "tassel")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Fist Abbot (elite, the key)

def fist_abbot():
    """The Abbot taught the fist, and took the jade into himself on purpose: his arms are jade from the elbow, as
    thick as temple beams, bound in iron bracers. A saffron robe tied off at the waist, his chest bare and heavy
    with prayer beads the size of fists, a beard to his belt, burn scars of the vows on his bald head. The prayer
    that binds the stair to heaven is his, and it is in the bead he wears at his throat."""
    k = X.Kit("fist_abbot")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(12, 14, 9.6), (21, 13, 9)], "robe", "robe")
    k.box(hips, C(0, 20.6, 0, 14, 2.4, 9.8), "lacquer", tag="sash")
    k.limb(hips, (3, 20, 4.8), (5, 9, 5.4), 1.8, "lacquer", "sash_tail", d=0.5)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.6
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -6), ("z", side * 10)), "hips")
        sh = k.part("shin_" + nm, (x, 10.6, 0), (("x", 10),), th)
        ft = k.part("foot_" + nm, (x, 2.4, 0), (("x", -4),), sh)
        k.box(th, C(x, 10.8, 0, 6.0, 9.4, 6.6), "robe", tag="trouser")
        k.box(sh, C(x, 2.4, 0, 5.8, 8.4, 6.4), "robe", tag="trouser")
        for y in (3.2, 5.0, 6.8):
            k.box(sh, C(x, y, 0, 6.2, 0.8, 6.8), "black", tag="leg_wrap")
        k.box(ft, C(x, 0, 1.4, 5.0, 2.4, 7.8), "skin", tag="foot")
    # ---------------------------------------------------------------- torso: bare, heavy, the beads
    to = k.part("torso", (0, 21, 0), (("x", 8),), "hips")
    k.stack(to, 0, 0, [(21, 13, 9), (27, 18, 10.6), (33, 22, 11.4), (37, 20, 10.4)], "skin", "chest")
    k.box(to, C(-5.4, 22, 0, 6.0, 15, 10.8), "robe", tag="robe_half")          # the robe off one shoulder
    k.limb(to, (-9, 36, 0), (6, 21, 5.6), 3.4, "robe", "robe_drape", d=0.8)
    beads(k, to, 0, 31, 5.6, 6.0, 14, 2.2, mat="wood", tag="great_beads")
    k.box(to, C(0, 33.6, 5.6, 2.6, 2.6, 2.4), "glow", group="glow", tag="prayer_bead")
    for (x, y) in ((4, 26), (6, 30), (-2, 25)):
        k.box(to, C(x, y, 5.3, 1.4, 1.4, 0.4), "dark", tag="tattoo")
    # ---------------------------------------------------------------- the head: bald, scarred, a beard to the belt
    hd = k.part("head", (0, 37, 0.6), (("x", -8),), "torso")
    k.box(hd, C(0, 37, 0.6, 7.0, 7.8, 7.4), "skin", tag="head")
    for (x, z) in ((-1.6, 1), (0, 0), (1.6, 1), (-0.8, -1.4), (0.8, -1.4)):
        k.box(hd, C(x, 44.8, 0.6 + z, 0.9, 0.3, 0.9), "dark", tag="vow_scar")
    k.box(hd, C(0, 42.0, 4.35, 6.4, 1.2, 0.4), "beard", tag="brow")
    for sx in (-1.6, 1.6):
        k.box(hd, C(sx, 40.6, 4.35, 1.4, 0.7, 0.3), "eye", group="glow", tag="eye")
        k.box(hd, C(sx * 2.4, 39.2, 0.6, 1.0, 3.0, 1.6), "skin", tag="ear")
    k.stack(hd, 0, 4.2, [(24, 3, 2), (30, 6, 2.6), (35, 7, 2.8), (38, 6.6, 2.4)], "beard", "beard")
    k.box(hd, C(0, 38.4, 4.6, 5.4, 1.0, 0.8), "beard", tag="mustache")
    # ---------------------------------------------------------------- arms: jade from the elbow, as thick as beams, iron bracers
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 12.4
        up = k.part("arm_" + nm, (x, 34, 0), (("x", -40 if side > 0 else -70), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 24, 0), (("x", -70 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 13, 0), (), fo)
        k.blob(up, (x, 33, 0), (5.4, 4.4, 5.6), "skin", "shoulder")
        k.stack(up, x, 0, [(24, 6.8, 7.0), (32, 7.6, 7.8)], "skin", "upper_arm")
        k.stack(fo, x, 0, [(14, 9.4, 9.4), (20, 10.0, 10.0), (24, 8.4, 8.4)], "jade", "jade_forearm")
        for y in (15, 18, 21):
            k.box(fo, C(x, y, 0, 10.6, 1.6, 10.6), "iron", tag="bracer")
        k.rivets(fo, [(x + side * 5.4, 18.8, -2), (x + side * 5.4, 18.8, 2)], "iron", 0.9)
        k.box(hn, C(x, 8.6, 0.6, 9.0, 7.0, 9.0), "jade", tag="fist")
        k.box(hn, C(x, 10.6, 5.2, 8.4, 2.4, 1.0), "glow", group="glow", tag="knuckle_glow")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Stone Lion (brute)

def stone_lion():
    """The two lions that sat at the monastery gate came down off their plinths: great granite beasts, the mane in
    tight carved curls, the jaws open on a jade pearl, a stone ball under one paw that it now swings on a chain.
    It walks upright when it fights, like the temple guardians it was carved to be, and the jade has veined it."""
    k = X.Kit("stone_lion")
    hips = k.part("hips", (0, 21, -1))
    k.stack(hips, 0, -1, [(14, 15, 12), (21, 16, 12.4)], "granite", "haunch")
    tail = [(0, 18, -7), (0, 15, -11), (0, 17, -15)]
    for (a, b) in zip(tail, tail[1:]):
        k.limb(hips, a, b, 2.4, "granite", "tail")
    k.blob(hips, (0, 18, -16), (2.6, 2.6, 2.6), "granite", "tail_curl", step=0.9)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.0
        th = k.part("thigh_" + nm, (x, 19, -1), (("x", -30), ("z", side * 10)), "hips")
        sh = k.part("shin_" + nm, (x, 11, -1), (("x", 50),), th)
        ft = k.part("foot_" + nm, (x, 3, -1), (("x", -20),), sh)
        k.blob(th, (x, 15, -1), (4.6, 5.4, 5.0), "granite", "thigh")
        k.box(sh, C(x, 3, -1.6, 5.0, 8.4, 5.4), "granite", tag="shin")
        k.box(ft, C(x, 0, 0.6, 6.4, 3.4, 8.6), "granite", tag="foot")
        for t in (-2, 0, 2):
            k.shard(ft, (x + t, 1.0, 4.6), (0, -0.4, 1), 1.6, 1.2, mat="jade", tag="foot")
    # ---------------------------------------------------------------- torso: a deep chest, a carved collar with a bell
    to = k.part("torso", (0, 21, -1), (("x", 26),), "hips")
    k.stack(to, 0, 0, [(21, 16, 12.4), (28, 20, 14), (35, 22, 14)], "granite", "chest")
    k.ring(to, 0, 35, 2, 9.0, 1.6, "lacquer", "collar", n=16, axis="y")
    k.box(to, C(0, 31, 9.6, 3.6, 3.6, 3.0), "bronze", tag="collar_bell")
    for (x, y) in ((-5, 26), (4, 30), (-2, 32)):
        k.box(to, C(x, y, 7.1, 0.6, 4.0, 0.4), "glow", group="glow", tag="jade_vein")
    # the mane: tight carved curls all round the head and shoulders
    for r, n, y in ((10, 16, 34), (8, 12, 38), (6, 10, 41)):
        for j in range(n):
            a = j * 2 * math.pi / n
            k.blob(to, (math.sin(a) * r, y, 2 + math.cos(a) * r * 0.8), (2.0, 2.0, 2.0), "granite", "mane_curl", step=0.8)
            k.box(to, C(math.sin(a) * r, y - 0.2, 2 + math.cos(a) * r * 0.8 + (1.6 if math.cos(a) > 0 else -1.6), 1.0, 0.4, 0.4),
                  "dark", tag="curl_line")
    # ---------------------------------------------------------------- the head: open jaws on a jade pearl, bulging eyes
    hd = k.part("head", (0, 36, 6), (("x", -24),), "torso")
    k.box(hd, C(0, 35, 7, 10, 9, 9), "granite", tag="head")
    k.box(hd, C(0, 34, 12, 8, 3.6, 4.6), "granite", tag="muzzle")
    k.box(hd, C(0, 30.4, 11.4, 7.4, 2.6, 4.4), "granite", tag="jaw")
    k.box(hd, C(0, 32.8, 12.6, 6.0, 1.4, 3.6), "dark", tag="mouth")
    k.blob(hd, (0, 33.4, 13.4), (1.8, 1.8, 1.8), "glow", "pearl", step=0.7)
    for sx in (-2.4, 2.4):
        k.shard(hd, (sx, 34.2, 15.6), (0, -1, 0.1), 2.0, 1.0, mat="granite", tag="fang")
        k.blob(hd, (sx, 41.4, 11.6), (1.6, 1.6, 1.2), "granite", "brow_bulge", step=0.6)
        k.box(hd, C(sx, 40.6, 12.6, 1.6, 1.2, 0.6), "eye", group="glow", tag="eye")
    k.box(hd, C(0, 37.6, 14.4, 3.4, 2.0, 1.4), "granite", tag="nose")
    # ---------------------------------------------------------------- arms: forelegs, great paws; the ball on its chain
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 12
        up = k.part("arm_" + nm, (x, 33, 0), (("x", -30 if side > 0 else -60), ("z", side * 14)), "torso")
        fo = k.part("fore_" + nm, (x, 23, 0), (("x", -30),), up)
        hn = k.part("hand_" + nm, (x, 13, 0), (), fo)
        k.blob(up, (x, 31, 0), (5.0, 5.0, 5.4), "granite", "shoulder")
        k.stack(fo, x, 0, [(14, 6.4, 6.6), (23, 6.8, 7.0)], "granite", "foreleg")
        k.box(hn, C(x, 8.6, 1.2, 8.0, 5.4, 8.6), "granite", tag="paw")
        for t in (-2.6, -0.9, 0.9, 2.6):
            k.shard(hn, (x + t, 9.6, 5.6), (0, -0.6, 1), 2.0, 1.2, mat="jade", tag="claw")
    bl = k.part("ball", (-12, 9, 2), (("x", 30),), k.parts["hand_r"])
    k.chain(bl, (-12, 9, 2), (-12, -4, 6), 5, w=1.6)
    k.blob(bl, (-12, -9, 7), (6.0, 6.0, 6.0), "granite", "stone_ball", step=1.0)
    for a in range(0, 360, 60):
        r = math.radians(a)
        k.box(bl, C(-12 + math.cos(r) * 5.2, -9.6 + math.sin(r) * 5.2, 7 + 0, 1.0, 1.0, 6.0), "dark", tag="ball_carving")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Incense Monk (caster)

def incense_monk():
    """The monks who kept the incense burning carry it with them still: a bronze censer as big as a barrel on a
    frame on their backs, smoking green; a broad straw hat stuck full of burning incense sticks; prayer beads
    wound round both wrists. They breathe in the smoke, and breathe it out at you."""
    k = X.Kit("incense_monk")
    hips = k.part("hips", (0, 19, 0))
    k.stack(hips, 0, 0, [(1, 11, 8.4), (10, 10, 7.2), (19, 9, 6.4)], "saffron", "robe")
    k.box(hips, C(0, 18.6, 0, 9.8, 1.8, 7.0), "lacquer", tag="sash")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 19, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 10, 0), (), th)
        ft = k.part("foot_" + nm, (x, 2, 0), (), sh)
        k.box(ft, C(x, 0, 1.6, 3.0, 1.4, 5.4), "wood", tag="foot")
    # ---------------------------------------------------------------- torso: the censer on its frame
    to = k.part("torso", (0, 19, 0), (("x", 16),), "hips")
    k.stack(to, 0, 0, [(19, 9, 6.4), (25, 11, 7.0), (31, 12, 7.0)], "saffron", "robe")
    k.limb(to, (5, 31, 3.6), (-4, 20, 3.8), 2.4, "lacquer", "stole", d=0.6)
    for sx in (-4.4, 4.4):
        k.limb(to, (sx, 32, -3.4), (sx, 14, -6), 1.0, "wood", "frame")
    k.blob(to, (0, 26, -9), (5.6, 6.4, 5.0), "bronze", "censer", step=0.9)
    k.box(to, C(0, 31.6, -9, 10, 1.4, 9), "bronze", tag="censer_rim")
    k.box(to, C(0, 26, -3.8, 6.0, 4.0, 0.6), "glow", group="glow", tag="censer_grille")
    for (x, z, L, lean) in ((-1.4, -9, 8, -0.3), (1.4, -10, 9, 0.3), (0, -8, 11, 0.0)):
        pts = [(x, 32, z), (x + lean * 3 + 0.8, 32 + L * 0.4, z - 0.6), (x + lean * 5 - 0.8, 32 + L * 0.75, z - 1.4), (x + lean * 6, 32 + L, z - 2)]
        for (a, b), w in zip(zip(pts, pts[1:]), (1.6, 1.2, 0.8)):
            k.limb(to, a, b, w, "glow", "smoke", group="glow")
    k.box(to, C(0, 33, -9, 6.0, 1.4, 5.0), "glow", group="glow", tag="censer_coals")
    # ---------------------------------------------------------------- the head: the straw hat stuck with incense
    hd = k.part("head", (0, 31, 0.6), (("x", -12),), "torso")
    k.box(hd, C(0, 31, 0.6, 5.4, 6.0, 5.6), "skin", tag="face")
    for sx in (-1.2, 1.2):
        k.box(hd, C(sx, 34.0, 3.45, 1.2, 0.5, 0.3), "dark", tag="closed_eye")
    k.box(hd, C(0, 32.4, 3.45, 1.6, 0.5, 0.3), "dark", tag="mouth")
    k.box(hd, C(0, 37.0, 0.6, 15, 0.8, 15), "wood", tag="hat_brim")
    k.stack(hd, 0, 0.6, [(37.8, 10, 10), (39.4, 6, 6), (40.4, 2, 2)], "wood", "hat")
    for i in range(10):
        a = i * 2.4
        r = 2.0 + (i % 3) * 1.4
        x, z = math.cos(a) * r, 0.6 + math.sin(a) * r
        k.limb(hd, (x, 38.4, z), (x * 1.1, 43 + (i % 2), z * 1.1), 0.4, "wood", "incense_stick")
        k.box(hd, C(x * 1.1, 43 + (i % 2), z * 1.1, 0.6, 0.6, 0.6), "glow", group="glow", tag="incense_tip")
    # ---------------------------------------------------------------- arms: beads at the wrists, palms pressed
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.0
        up = k.part("arm_" + nm, (x, 29.6, 0), (("x", -60), ("z", side * 6)), "torso")
        fo = k.part("fore_" + nm, (x, 21.6, 0), (("x", -50), ("y", side * 50)), up)
        hn = k.part("hand_" + nm, (x, 13.8, 0), (), fo)
        k.box(up, C(x, 21.4, 0, 3.8, 8.4, 4.0), "saffron", tag="sleeve")
        k.stack(fo, x, 0, [(13.4, 6.0, 6.0), (21.6, 4.0, 4.0)], "saffron", "sleeve")
        beads(k, fo, x, 14.6, 0, 2.6, 10, 1.0, mat="jade", axis="y", tag="wrist_beads")
        k.box(hn, C(x, 11.4, 0.4, 2.6, 3.0, 2.0), "skin", tag="hand")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Shadow Monk (skirmisher)

def shadow_monk():
    """The door-keepers of the monastery wore black and kept no names. They still keep the doors: lean, wrapped in
    black, a black cloth mask with only the eyes showing and those gone jade-green, a long sash, and two hook
    swords - straight blades with a hook at the tip and a crescent guard - held low."""
    k = X.Kit("shadow_monk")
    hips = k.part("hips", (0, 19, 0))
    k.box(hips, C(0, 16.6, 0, 7.6, 3.6, 5.0), "black", tag="hips")
    k.box(hips, C(0, 19.0, 0, 8.4, 1.8, 5.6), "lacquer", tag="sash")
    k.limb(hips, (3.6, 19, -2), (6, 4, -6), 2.0, "lacquer", "sash_tail", d=0.4)
    k.limb(hips, (3.0, 19, -2.4), (4, 6, -8), 1.6, "lacquer", "sash_tail", d=0.4)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 19, 0), (("x", -30 if side > 0 else 10), ("z", side * 12)), "hips")
        sh = k.part("shin_" + nm, (x, 10.2, 0), (("x", 40 if side > 0 else 10),), th)
        ft = k.part("foot_" + nm, (x, 2.2, 0), (("x", -10),), sh)
        k.box(th, C(x, 10.4, 0, 3.6, 8.8, 3.8), "black", tag="thigh")
        k.box(sh, C(x, 2.2, 0, 3.0, 8.2, 3.2), "black", tag="shin")
        for y in (3.2, 5.0, 6.8):
            k.box(sh, C(x, y, 0, 3.4, 0.6, 3.6), "dark", tag="wrap")
        k.box(ft, C(x, 0, 1.2, 3.2, 2.0, 5.6), "black", tag="foot")
    # ---------------------------------------------------------------- torso
    to = k.part("torso", (0, 19, 0), (("x", 24), ("y", -16)), "hips")
    k.stack(to, 0, 0, [(19, 7.6, 5.0), (24, 8.6, 5.4), (29, 10.4, 5.6)], "black", "torso")
    k.limb(to, (4.4, 29, 2.9), (-3.4, 20, 2.9), 1.0, "lacquer", "cross_strap", d=0.4)
    beads(k, to, 0, 26, 3.0, 2.6, 10, 0.9, mat="jade", tag="beads")
    # ---------------------------------------------------------------- the head: the black mask, the jade eyes
    hd = k.part("head", (0, 29.6, 0.4), (("x", -20), ("y", 14)), "torso")
    k.box(hd, C(0, 29.8, 0.4, 5.0, 5.6, 5.2), "black", tag="mask")
    k.box(hd, C(0, 32.6, 2.95, 4.0, 1.2, 0.3), "dark", tag="eye_slit")
    for sx in (-1.0, 1.0):
        k.box(hd, C(sx, 32.8, 3.05, 1.0, 0.6, 0.3), "eye", group="glow", tag="eye")
    k.limb(hd, (0, 34.6, -2.4), (-2, 31, -7), 1.2, "black", "mask_tail", d=0.4)
    k.limb(hd, (0, 34.6, -2.4), (1.4, 30, -6.6), 1.2, "black", "mask_tail", d=0.4)
    # ---------------------------------------------------------------- arms and the hook swords
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.0
        up = k.part("arm_" + nm, (x, 28, 0), (("x", -20 if side > 0 else -80), ("z", side * 26)), "torso")
        fo = k.part("fore_" + nm, (x, 20.8, 0), (("x", -70 if side > 0 else -20),), up)
        hn = k.part("hand_" + nm, (x, 13.6, 0), (), fo)
        k.box(up, C(x, 21.0, 0, 2.8, 7.4, 3.0), "black", tag="sleeve")
        k.box(fo, C(x, 13.8, 0, 2.6, 7.0, 2.8), "black", tag="sleeve")
        k.box(hn, C(x, 11.2, 0.3, 2.4, 2.6, 2.4), "black", tag="hand")
        hs = k.part("hook_" + nm, (x, 12.4, 0.4), (("x", 80),), hn)
        k.box(hs, C(x, 9.6, 0.4, 0.9, 4.4, 0.9), "lacquer", tag="grip")
        pts = [(x, 14.0, -1.6), (x, 15.4, 0.4), (x, 14.0, 2.4)]
        for (a, b) in zip(pts, pts[1:]):
            k.limb(hs, a, b, 0.8, "iron", "crescent_guard", d=0.4)
        k.box(hs, C(x, 14.4, 0.4, 0.5, 13.0, 1.4), "iron", tag="blade")
        hook = [(x, 27.4, 0.4), (x, 29.0, 1.6), (x, 28.6, 3.4), (x, 26.8, 3.8)]
        for (a, b) in zip(hook, hook[1:]):
            k.limb(hs, a, b, 1.2, "iron", "hook", d=0.4)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Jade Acolyte (swarm)

def jade_acolyte():
    """The novices were youngest and the jade took them fastest: small monks of green jade, glassy, cracked through
    with the prayer's light, still in the stiff folds of their robes as the jade caught them - shaved heads, prayer
    beads in their hands, a short staff. They move together and chant without mouths."""
    k = X.Kit("jade_acolyte")
    hips = k.part("hips", (0, 17, 0))
    k.stack(hips, 0, 0, [(1, 9, 7), (9, 8, 6), (17, 7.4, 5.4)], "jade", "robe")
    for (x, z) in ((-3.0, 3.0), (2.6, 3.2), (0, -3.2)):
        k.box(hips, C(x, 2, z, 0.4, 12, 0.4), "glow", group="glow", tag="crack")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.0
        th = k.part("thigh_" + nm, (x, 17, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 9, 0), (), th)
        ft = k.part("foot_" + nm, (x, 1.6, 0), (), sh)
        k.box(ft, C(x, 0, 1.2, 2.6, 1.4, 4.6), "jade", tag="foot")
    # ---------------------------------------------------------------- torso: a robe over one shoulder, all jade
    to = k.part("torso", (0, 17, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(17, 7.4, 5.4), (22, 9.0, 6.0), (27, 10.4, 6.2)], "jade", "robe")
    k.limb(to, (-4.6, 27, 0), (3.6, 18, 3.2), 2.6, "jade", "robe_drape", d=0.6)
    k.limb(to, (2, 26, 3.2), (-1, 20, 3.4), 0.5, "glow", "crack", group="glow")
    # ---------------------------------------------------------------- the head: shaved, serene, cracked
    hd = k.part("head", (0, 27.4, 0.4), (("x", -4),), "torso")
    k.blob(hd, (0, 30.0, 0.4), (2.6, 3.0, 2.8), "jade", "head", step=0.6)
    for sx in (-0.9, 0.9):
        k.box(hd, C(sx, 30.8, 3.0, 1.0, 0.4, 0.3), "eye", group="glow", tag="eye")
    k.box(hd, C(0.8, 29.2, 3.0, 0.3, 3.4, 0.3), "glow", group="glow", tag="crack")
    for (x, z) in ((-0.8, 0.4), (0.8, 0.4), (0, -0.8)):
        k.box(hd, C(x, 32.8, 0.4 + z, 0.6, 0.3, 0.6), "dark", tag="vow_dot")
    # ---------------------------------------------------------------- arms: beads in one hand, a staff in the other
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.4
        up = k.part("arm_" + nm, (x, 26, 0), (("x", -40), ("z", side * 8)), "torso")
        fo = k.part("fore_" + nm, (x, 19.6, 0), (("x", -50),), up)
        hn = k.part("hand_" + nm, (x, 13.4, 0), (), fo)
        k.box(up, C(x, 19.8, 0, 2.8, 6.6, 3.0), "jade", tag="sleeve")
        k.stack(fo, x, 0, [(13.4, 4.4, 4.4), (19.6, 3.0, 3.0)], "jade", "sleeve")
        k.box(hn, C(x, 11.4, 0.3, 2.2, 2.4, 2.2), "jade", tag="hand")
        if side > 0:
            beads(k, hn, x, 10.0, 1.2, 1.6, 8, 0.7, mat="glow", axis="x", tag="beads")
    st = k.part("staff", (-5.4, 12.2, 0.6), (("x", 80),), k.parts["hand_r"])
    k.limb(st, (-5.4, -4, 0.6), (-5.4, 24, 0.6), 1.0, "jade", "staff")
    for y in (-3, 23):
        k.box(st, C(-5.4, y, 0.6, 1.6, 1.4, 1.6), "gold", tag="staff_cap")
    k.s.shaders = shaders()
    return k.s, k.parts


MOBS = {
    "jade_acolyte": dict(make=jade_acolyte, ent=(0.8, 2.3), stats=dict(hp=26, speed=0.3, dmg=6, armor=4, kb=0)),
    "stone_lion": dict(make=stone_lion, ent=(1.8, 3.6), stats=dict(hp=110, speed=0.22, dmg=15, armor=12, kb=1.0)),
    "incense_monk": dict(make=incense_monk, ent=(0.9, 2.8), stats=dict(hp=40, speed=0.21, dmg=7, armor=3, kb=0)),
    "shadow_monk": dict(make=shadow_monk, ent=(0.8, 2.7), stats=dict(hp=36, speed=0.36, dmg=8, armor=3, kb=0)),
    "fist_abbot": dict(make=fist_abbot, ent=(1.3, 3.2), stats=dict(hp=210, speed=0.25, dmg=14, armor=10, kb=0.7), key=True),
    "thousand_hands": dict(make=thousand_hands, texel=1, ent=(3.0, 6.6), stats=dict(hp=600, speed=0.2, dmg=20, armor=12, kb=1.0), boss=True),
}
