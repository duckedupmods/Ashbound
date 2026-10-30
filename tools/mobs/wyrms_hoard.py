"""The Wyrm's Hoard's monsters, each built by hand (tools/vox2.py). Everything in the dead volcano lives off the dragon
or the gold: charcoal scales with the fire still glowing between them, grey ash flaking off, rust-red kobold hide,
bone and horn, and gold - coins, crowns, goblets - stuck to everything.

    kobold         swarm   a little rust-red dog-lizard with a candle on its helmet, a coin necklace, a pick, a tail
    hoard_golem    brute   a giant of gold melted together - shields, crowns, goblets, swords sticking out - a molten heart
    ash_cultist    caster  a cultist of the wyrm in ash robes and a drake-skull mask, a mantle of scales, an ember-claw staff
    drake          skirm   a wingless drake on four legs, lean, spined, its throat glowing with the breath (the hound's bones)
    wyrm_priest    elite   a dragon-blooded priest, tall, a drake's long head crowned in gold horns, gold vestments,
                           the priest's scale on his chest (the key), an ember-heart staff, a tail
    ignavar        boss    Ignavar the Ash Wyrm: a dragon on four legs, charcoal scale cracked to fire, ash pouring off him,
                           great swept horns, a jaw of fire, torn grey wings raised, gold crusted into his belly

    python tools/monsterforge.py wyrms_hoard --preview ; python tools/mobsheet.py wyrms_hoard
"""
import math

import vox2 as X
from vox2 import C, ramp

CHAR = ramp("#0e0c0c", "#181514", "#231e1c", "#302824", "#3e342e", "#4e4238")
ASH = ramp("#2a2826", "#3a3734", "#4c4844", "#5e5954", "#706a64")
GOLD = ramp("#3a2604", "#5e400a", "#8a6010", "#b8861c", "#e0ac2c", "#fcd860")
RUST = ramp("#1e0c06", "#34160a", "#4c220e", "#663014", "#80401c", "#9a5226")
BONE = ramp("#3e3628", "#5c5240", "#7c705a", "#9c9076", "#bcb094", "#d8ceb0")
FIRE = ramp("#a02a06", "#e05a0c", "#ff9a20", "#ffd060", "#fff4c0")
MEMB = ramp("#141210", "#201c1a", "#2c2724", "#3a3430", "#48403a")
RED = ramp("#2a0604", "#440a06", "#5e1008", "#7a180c")
WAX = ramp("#6a5a40", "#a08a6a", "#d8c8a0", "#f0e4c0")
IRON = ramp("#0e0c0c", "#1a1716", "#262220", "#34302c", "#443e38")


def scales(p, n, i, j, w, h):
    """overlapping rows of scales: a dark line under each row, the rows offset like brickwork"""
    row = j // 3
    if j % 3 == 2:
        return -0.2
    if (i + (row % 2) * 2) % 4 == 0:
        return -0.12
    return 0.04 if j % 3 == 0 else 0


def shaders():
    return {
        "scale": X.surf(CHAR, 0.5, 1.4, 0.2, 0.2, crust=(ASH, 0.22), pattern=scales),
        "belly": X.surf(BONE, 0.5, 1.2, 0.16, 0.12, crust=(ASH, 0.1), stripe=3),
        "ash": X.surf(ASH, 0.5, 1.0, 0.3, 0.0, holes=True),
        "gold": X.surf(GOLD, 0.55, 1.5, 0.12, 0.26),
        "heap": X.surf(GOLD, 0.52, 1.4, 0.34, 0.0, pattern=lambda p, n, i, j, w, h: 0.16 if (i * 7 + j * 3) % 11 == 0 else 0),
        "hide": X.surf(RUST, 0.5, 1.2, 0.22, 0.12, pattern=scales),
        "bone": X.surf(BONE, 0.5, 1.3, 0.18, 0.18),
        "fire": X.glow(FIRE, 0.7, 0.3),
        "eye": X.glow(FIRE, 0.84, 0.14),
        "membrane": X.surf(MEMB, 0.5, 1.0, 0.2, 0.0, holes=True),
        "robe": X.surf(ASH, 0.46, 1.0, 0.24, 0.0, holes=True, drip=(CHAR, 0.2)),
        "red": X.surf(RED, 0.5, 1.0, 0.2, 0.04, stripe=2),
        "wax": X.surf(WAX, 0.5, 1.0, 0.1, 0.06),
        "iron": X.surf(IRON, 0.5, 1.3, 0.2, 0.14),
        "dark": X.dark(CHAR),
    }


def cracks(k, part, lines, w=1.4):
    """lines of fire showing between the scales"""
    for (a, b) in lines:
        k.limb(part, a, b, w, "fire", "ember_crack", group="glow", d=0.4)


def spines(k, part, pts, L=4.0, w=2.0, mat="bone", back=-0.4):
    for i, (x, y, z) in enumerate(pts):
        k.shard(part, (x, y, z), (0, 1, back), L * (0.7 + 0.3 * (i % 2)), w, mat=mat, tag="spine")


def coins(k, part, pts, s=1.0):
    for i, (x, y, z) in enumerate(pts):
        k.box(part, C(x, y, z, 1.8 * s, 0.5 * s if i % 2 else 1.8 * s, 1.8 * s if i % 2 else 0.5 * s), "gold", tag="coin")


# ================================================================ Ignavar the Ash Wyrm (boss, on the hound's bones)

def ignavar():
    """Ignavar burnt three kingdoms and carried their gold into a volcano and lay down on it, and the volcano died
    under him and he did not. He is the colour of a cold fire: charcoal scale, cracked, the fire still glowing in
    every crack, and ash pouring off him as he moves. His horns sweep back past his neck like a crown of blades.
    His jaw hangs open on the furnace in his throat. His wings are grey and torn, held up over him like the walls
    of a burnt house. He has lain on the gold so long it has melted into his belly - coins, a crown, a sword-hilt."""
    k = X.Kit("ignavar")
    body = k.part("body", (0, 26, 0))
    k.blob(body, (0, 28, 2), (13, 12, 16), "scale", "chest")
    k.blob(body, (0, 21, 4), (10, 6, 13), "belly", "belly")
    coins(k, body, [(-4, 16.4, 6), (2, 16, 2), (5, 16.6, 9), (-1, 16.2, 12), (-6, 17, -2), (3, 16.4, -4), (7, 17.6, 4)], s=1.4)
    k.box(body, C(-2, 15.6, 8, 4.0, 1.2, 4.0), "gold", tag="crown_in_belly")
    for i in range(5):
        k.shard(body, (-2 + (i - 2) * 0.8, 16.8, 8), (0, 1, 0), 1.6, 0.6, mat="gold", tag="crown_in_belly")
    k.limb(body, (6, 17, -1), (9, 15, -6), 1.2, "iron", "sword_in_belly")
    cracks(k, body, [((-10, 30, 12), (-12, 24, 4)), ((10, 32, 8), (12, 26, -2)), ((-6, 38, 6), (-10, 34, -4)),
                     ((6, 38, 10), (9, 34, 2)), ((0, 40, 0), (4, 39, -8)), ((-12, 28, -4), (-11, 32, -10))])
    spines(k, body, [(0, 39.6, z) for z in (12, 7, 2, -3, -8)], L=7, w=3.0)
    # ---------------------------------------------------------------- the wings, grey and torn, raised over him
    wg = k.part("wings", (0, 38, -2), (), body, bone=False)
    for side in (1, -1):
        sh = (side * 10, 36, -2)
        el = (side * 26, 58, -6)
        wr = (side * 36, 74, -10)
        k.limb(wg, sh, el, 4.4, "scale", "wing_arm")
        k.limb(wg, el, wr, 3.4, "scale", "wing_arm")
        k.shard(wg, wr, (side * 0.3, 1, -0.2), 7, 2.4, mat="bone", tag="wing_claw")
        tips = [(side * 54, 64, -14), (side * 56, 44, -14), (side * 48, 28, -12), (side * 34, 22, -10), (side * 12, 26, -6)]
        for tip in tips[:4]:
            k.limb(wg, wr, tip, 1.8, "scale", "wing_finger")
        edge = []
        for (a, b) in zip(tips, tips[1:]):          # the trailing edge, scalloped between the fingers
            for f in (0.0, 0.25, 0.5, 0.75):
                sag = math.sin(f * math.pi) * 5
                edge.append(tuple(a[j] + (b[j] - a[j]) * f for j in range(3)))
                edge[-1] = (edge[-1][0] - side * sag * 0.4, edge[-1][1] + sag, edge[-1][2])
        for i, e in enumerate(edge):
            f = i / (len(edge) - 1)
            hub = wr if f < 0.45 else (el if f < 0.8 else sh)
            torn = i in (5, 9)
            end = e if not torn else tuple(hub[j] + (e[j] - hub[j]) * 0.6 for j in range(3))
            k.limb(wg, hub, end, 7.0, "membrane", "membrane", d=0.6)
        k.limb(wg, el, wr, 9.0, "membrane", "membrane", d=0.5)
    # ---------------------------------------------------------------- the neck and the head, the horns, the jaw of fire
    hd = k.part("head", (0, 34, 16), (("x", -10),), body)
    neck = [(0, 32, 14), (0, 40, 22), (0, 48, 26), (0, 54, 30)]
    for (a, b), w in zip(zip(neck, neck[1:]), (11, 9, 8)):
        k.limb(hd, a, b, w, "scale", "neck")
        k.limb(hd, (a[0], a[1] - 3, a[2] + 3.6), (b[0], b[1] - 3, b[2] + 3.4), w * 0.6, "belly", "throat", d=w * 0.4)
    spines(k, hd, [(0, 39, 18), (0, 46, 22), (0, 52, 25)], L=6, w=2.6, back=-0.6)
    k.box(hd, C(0, 59, 34, 11, 7, 12), "scale", tag="skull")
    k.box(hd, C(0, 59, 46, 8, 5, 12), "scale", tag="snout")
    k.box(hd, C(0, 63.8, 48, 7, 1.2, 8), "scale", tag="snout_ridge")
    k.box(hd, C(0, 54, 40, 7.6, 3.0, 16), "scale", tag="jaw")
    k.box(hd, C(0, 56.4, 41, 7.4, 3.0, 14), "fire", group="glow", tag="mouth_fire")
    k.blob(hd, (0, 55, 54), (3.0, 2.4, 3.0), "fire", "breath", step=0.7)
    for i in range(6):
        z = 38 + i * 2.6
        for sx in (-1, 1):
            k.shard(hd, (sx * 3.2, 59, z), (0, -1, 0), 2.6, 0.9, mat="bone", tag="tooth")
            k.shard(hd, (sx * 3.0, 57, z), (0, 1, 0), 2.0, 0.8, mat="bone", tag="tooth")
    for sx in (-1, 1):
        k.box(hd, C(sx * 4.8, 62.6, 39, 2.0, 1.4, 3.0), "eye", group="glow", tag="eye")
        k.box(hd, C(sx * 4.4, 64.2, 39, 3.0, 1.0, 4.0), "scale", tag="brow")
        horn = [(sx * 4.6, 65, 34), (sx * 8, 69, 28), (sx * 11, 70, 20), (sx * 12, 68, 12)]
        for (a, b), w in zip(zip(horn, horn[1:]), (3.6, 2.8, 2.0)):
            k.limb(hd, a, b, w, "bone", "horn")
        k.shard(hd, horn[-1], (0.2 * sx, -0.4, -1), 5, 1.6, mat="bone", tag="horn")
        k.shard(hd, (sx * 5.6, 63, 30), (sx, 0.4, -1), 6, 1.6, mat="bone", tag="horn_small")
        k.shard(hd, (sx * 5.4, 55, 34), (sx, -0.3, -0.6), 5, 1.4, mat="bone", tag="jaw_spike")
    # ---------------------------------------------------------------- the haunches and the tail, ash pouring off
    ab = k.part("abdomen", (0, 26, -14), (), body)
    k.blob(ab, (0, 26, -22), (12, 11, 12), "scale", "haunch")
    k.blob(ab, (0, 19, -20), (9, 5, 9), "belly", "belly")
    cracks(k, ab, [((-10, 28, -16), (-11, 22, -26)), ((10, 30, -18), (11, 24, -28)), ((0, 36, -16), (-3, 35, -26))])
    spines(k, ab, [(0, 36.4, z) for z in (-14, -20, -26, -31)], L=6, w=2.6)
    tail = [(0, 26, -32), (2, 20, -44), (5, 14, -56), (4, 8, -68), (-2, 5, -78)]
    for i, ((a, b), w) in enumerate(zip(zip(tail, tail[1:]), (9, 7, 5, 3.4))):
        k.limb(ab, a, b, w, "scale", "tail")
        k.shard(ab, (a[0], a[1] + w * 0.5, a[2]), (0, 1, -0.5), 4 - i * 0.6, 1.8, mat="bone", tag="tail_spine")
    k.shard(ab, tail[-1], (-0.5, -0.1, -1), 8, 4, mat="bone", tag="tail_blade")
    for (x, z) in ((-8, -18), (8, -24), (-5, -30), (6, -12)):
        k.limb(ab, (x, 18, z), (x * 1.2, 12, z - 2), 2.4, "ash", "ash_pour", d=1.6)
    # ---------------------------------------------------------------- four legs, gold under the claws
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, (z, j, part) in enumerate(((10, 1, body), (-22, 4, ab))):
            nm = "leg_%s%d" % (s, i)
            x0 = side * 12
            lg = k.part(nm, (x0, 26, z), (), part)
            k.blob(lg, (x0 + side * 1, 26, z), (6, 7, 7), "scale", "shoulder")
            kn = (side * 16, 12, z + (4 if i == 0 else -4))
            k.limb(lg, (x0 + side * 1, 26, z), kn, 8.0, "scale", "leg")
            k.limb(lg, kn, (side * 16, 2, z + 2), 6.0, "scale", "leg")
            k.box(lg, C(side * 16, 0, z + 3, 9, 3, 10), "scale", tag="foot")
            for t in (-3, 0, 3):
                k.shard(lg, (side * 16 + t, 1.4, z + 7.6), (0, -0.4, 1), 4.0, 1.6, mat="bone", tag="foot")
            k.shard(lg, (side * 18, 1.4, z - 2), (side * 0.4, -0.3, -1), 3, 1.4, mat="bone", tag="foot")
            k.box(lg, C(side * 18.4, 18, z, 1.0, 6, 3), "fire", group="glow", tag="ember_crack")
            joints[nm] = ("LL" if side > 0 else "RL") + str(j)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Wyrm Priest (elite, the key)

def wyrm_priest():
    """The high priest of Ignavar's cult drank the wyrm's blood until it changed him: he stands taller than a man, his
    head drawn out into a drake's long skull, scaled, with a crown of gold fitted over his horns. He wears the gold
    vestments of the three kingdoms' churches, sewn together, with red under them; a tail drags behind. On his chest
    hangs one of Ignavar's own scales, shed and set in gold - it opens the crater. His staff holds an ember in a
    cage of claws that beats like a heart."""
    k = X.Kit("wyrm_priest")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(1, 15, 11), (10, 13, 9), (22, 12, 8)], "red", "robe")
    k.stack(hips, 0, 0.6, [(4, 9, 9.6), (22, 9, 8.6)], "gold", "chasuble")
    for x in (-3.6, 0, 3.6):
        k.box(hips, C(x, 3, 5.0, 1.0, 16, 0.4), "fire", tag="embroidery")
    tail = [(0, 16, -4), (0, 9, -10), (2, 3, -16), (4, 1, -22)]
    for (a, b), w in zip(zip(tail, tail[1:]), (4.0, 3.0, 2.0)):
        k.limb(hips, a, b, w, "scale", "tail")
    spines(k, hips, [(0, 13, -8), (1, 7, -13), (3, 3, -18)], L=2.4, w=1.2)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.2
        th = k.part("thigh_" + nm, (x, 22, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 12, 0), (), th)
        ft = k.part("foot_" + nm, (x, 3, 0), (), sh)
        k.box(ft, C(x, 0, 2.4, 4.4, 2.0, 7.0), "scale", tag="foot")
        for t in (-1.2, 1.2):
            k.shard(ft, (x + t, 0.8, 5.8), (0, -0.3, 1), 1.8, 0.8, mat="bone", tag="foot")
    # ---------------------------------------------------------------- torso: vestments, the priest's scale
    to = k.part("torso", (0, 22, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(22, 12, 8), (30, 15, 9), (37, 18, 10), (41, 16, 9)], "red", "robe")
    k.stack(to, 0, 0.6, [(22, 9, 8.6), (36, 13, 9.6), (41, 14, 9.4)], "gold", "chasuble")
    k.blob(to, (0, 41, -0.4), (10, 3.0, 6.4), "gold", "mantle")
    for side in (1, -1):
        k.shard(to, (side * 8, 42, 0), (side * 0.6, 1, 0), 4, 2.4, mat="gold", tag="mantle_spike")
    k.box(to, C(0, 30, 5.4, 6.4, 7.6, 1.2), "gold", tag="scale_setting")
    k.box(to, C(0, 30.6, 6.2, 4.8, 6.0, 0.6), "scale", tag="priest_scale")
    k.box(to, C(0, 33, 6.6, 2.0, 1.4, 0.4), "fire", group="glow", tag="priest_scale_glow")
    k.chain(to, (-3, 37, 5), (0, 37.6, 5.6), 2, mat="gold", w=0.8)
    k.chain(to, (3, 37, 5), (0, 37.6, 5.6), 2, mat="gold", w=0.8)
    # ---------------------------------------------------------------- the head: a drake's long skull, the gold horn-crown
    hd = k.part("head", (0, 41, 0.6), (("x", -6),), "torso")
    k.box(hd, C(0, 41, 0.6, 4.4, 3.6, 4.4), "scale", tag="neck")
    k.box(hd, C(0, 44, 1.0, 6.4, 5.4, 7.0), "scale", tag="skull")
    k.box(hd, C(0, 44, 7.4, 4.4, 3.4, 6.4), "scale", tag="snout")
    k.box(hd, C(0, 42.6, 7.0, 4.0, 1.4, 6.0), "belly", tag="jaw")
    k.box(hd, C(0, 44.0, 10.4, 3.6, 0.6, 1.0), "fire", group="glow", tag="mouth_fire")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.6, 47.0, 3.8, 1.2, 0.8, 1.6), "eye", group="glow", tag="eye")
        horn = [(sx * 2.6, 49, 0), (sx * 4.6, 52, -3), (sx * 5.6, 54, -7)]
        for (a, b), w in zip(zip(horn, horn[1:]), (1.8, 1.2)):
            k.limb(hd, a, b, w, "bone", "horn")
        k.box(hd, C(sx * 3.6, 50, -1.6, 2.4, 1.4, 2.4), "gold", tag="horn_ring")
    k.box(hd, C(0, 49.4, 1.0, 7.0, 1.4, 7.4), "gold", tag="crown")
    for i in range(5):
        k.shard(hd, (-3 + i * 1.5, 50.6, 4.6), (0, 1, 0.2), 3.6 if i == 2 else 2.4, 1.2, mat="gold", tag="crown")
    # ---------------------------------------------------------------- arms: the ember-heart staff
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 9.4
        up = k.part("arm_" + nm, (x, 39, 0), (("x", -30 if side > 0 else -50), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 30, 0), (("x", -40 if side > 0 else -30),), up)
        hn = k.part("hand_" + nm, (x, 21, 0), (), fo)
        k.stack(up, x, 0, [(30, 5.0, 5.2), (39, 5.4, 5.6)], "red", "sleeve")
        k.stack(fo, x, 0, [(21, 7.0, 7.0), (30, 5.4, 5.4)], "gold", "sleeve")
        k.box(hn, C(x, 17.6, 0.4, 3.4, 3.6, 3.0), "scale", tag="hand")
        for t in (-1, 0, 1):
            k.shard(hn, (x + t, 17.8, 1.6), (0, -1, 0.5), 2.2, 0.7, mat="bone", tag="claw")
    st = k.part("ember_staff", (-9.4, 19, 0.6), (("x", 70),), k.parts["hand_r"])
    k.limb(st, (-9.4, -10, 0.6), (-9.4, 40, 0.6), 1.6, "bone", "staff")
    for a in range(0, 360, 72):
        r = math.radians(a)
        k.limb(st, (-9.4 + math.cos(r) * 1.4, 40, 0.6 + math.sin(r) * 1.4), (-9.4 + math.cos(r) * 3.4, 45, 0.6 + math.sin(r) * 3.4), 0.9, "bone", "claw_cage")
        k.limb(st, (-9.4 + math.cos(r) * 3.4, 45, 0.6 + math.sin(r) * 3.4), (-9.4 + math.cos(r) * 1.4, 50, 0.6 + math.sin(r) * 1.4), 0.8, "bone", "claw_cage")
    k.blob(st, (-9.4, 45, 0.6), (2.6, 3.0, 2.6), "fire", "ember_heart", step=0.7)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Hoard Golem (brute)

def hoard_golem():
    """When Ignavar breathes on the hoard, the gold runs, and some of it gets up. A giant of gold melted together and
    set again: a body heaped of coins with shields, goblets, crowns and sword-blades stuck out of it at every angle,
    a molten heart showing white-orange in its chest, a crown pressed into its face for a mouth, eyes of fire. Its
    fists are heaps of coins as big as barrels."""
    k = X.Kit("hoard_golem")
    hips = k.part("hips", (0, 20, 0))
    k.blob(hips, (0, 18, 0), (10, 5, 8), "heap", "hips")
    coins(k, hips, [(-6, 14, 6), (4, 13.6, 7), (0, 16, 8), (7, 18, 5), (-8, 20, 3)])
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.0
        th = k.part("thigh_" + nm, (x, 18, 0), (("z", side * 6),), "hips")
        sh = k.part("shin_" + nm, (x, 10, 0), (), th)
        ft = k.part("foot_" + nm, (x, 3, 0), (), sh)
        k.blob(th, (x, 13, 0), (5.0, 5.4, 5.4), "heap", "thigh")
        k.blob(sh, (x, 6, 0), (5.4, 5.0, 5.6), "heap", "shin")
        coins(k, sh, [(x + side * 4.6, 6, 2), (x, 5, 5.4)])
        k.box(ft, C(x, 0, 1.6, 10, 3.4, 12), "gold", tag="foot")
    # ---------------------------------------------------------------- torso: a heap of treasure, the molten heart
    to = k.part("torso", (0, 20, 0), (("x", 12),), "hips")
    k.blob(to, (0, 31, 0), (16, 12, 11), "heap", "heap")
    k.blob(to, (0, 40, -1), (12, 5, 8), "heap", "shoulders")
    k.blob(to, (0, 30, 9.6), (5.4, 5.6, 2.2), "fire", "molten_heart", step=0.8)
    for (a, b) in (((-4, 30, 10), (-9, 36, 9)), ((4, 28, 10), (9, 24, 8.6)), ((2, 34, 10), (5, 40, 8)), ((-3, 26, 10), (-8, 22, 8.6))):
        k.limb(to, a, b, 1.2, "fire", "molten_run", group="glow", d=0.5)
    coins(k, to, [(x, y, 10.6) for (x, y) in ((-10, 34), (-12, 28), (10, 34), (12, 28), (-6, 22), (7, 22), (0, 40))], s=1.3)
    k.blob(to, (-11, 32, 6), (4.4, 4.4, 1.2), "gold", "shield")          # shields stuck in it
    k.box(to, C(-11, 31.6, 7.2, 1.4, 7, 0.6), "red", tag="shield_cross")
    k.blob(to, (12, 36, -3), (1.2, 4.6, 4.6), "gold", "shield")
    for (p, d, L) in (((6, 40, -6), (0.3, 1, -0.4), 12), ((-8, 38, -7), (-0.4, 1, -0.3), 10), ((14, 26, 2), (1, 0.4, 0), 8),
                      ((-3, 42, -4), (-0.1, 1, -0.6), 9)):
        k.shard(to, p, d, L * 1.4, 2.6, mat="bone", tag="sword_in_it")
        k.box(to, C(p[0], p[1], p[2], 4.0, 1.0, 1.4), "iron", tag="sword_guard")
    for (x, y, z) in ((-14, 38, 0), (9, 42, 4)):        # goblets
        k.box(to, C(x, y, z, 1.0, 2.0, 1.0), "gold", tag="goblet")
        k.box(to, C(x, y + 2, z, 2.4, 2.0, 2.4), "gold", tag="goblet")
    # ---------------------------------------------------------------- head: a lump with a crown for a mouth, eyes of fire
    hd = k.part("head", (0, 42, 4), (("x", -12),), "torso")
    k.blob(hd, (0, 46, 5), (5.6, 5.0, 5.4), "heap", "head")
    k.box(hd, C(0, 42.6, 9.6, 7.0, 2.4, 1.4), "gold", tag="crown_mouth")
    for i in range(6):
        k.shard(hd, (-3 + i * 1.2, 45, 10.2), (0, -1, 0.1), 2.2, 0.9, mat="gold", tag="crown_mouth")
    k.box(hd, C(0, 43.4, 9.8, 5.4, 1.4, 0.6), "fire", group="glow", tag="mouth_glow")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.4, 47.6, 10.0, 1.8, 1.4, 0.6), "eye", group="glow", tag="eye")
    # ---------------------------------------------------------------- arms: barrel fists of coins
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 17
        up = k.part("arm_" + nm, (x, 38, 0), (("x", -20 if side > 0 else -40), ("z", side * 14)), "torso")
        fo = k.part("fore_" + nm, (x, 27, 0), (("x", -20),), up)
        hn = k.part("hand_" + nm, (x, 15, 0), (), fo)
        k.blob(up, (x, 34, 0), (6.4, 6.4, 6.4), "heap", "upper_arm")
        k.blob(fo, (x, 22, 0), (6.8, 6.6, 6.8), "heap", "forearm")
        k.blob(hn, (x, 10, 0.6), (8.0, 6.6, 8.0), "heap", "fist")
        coins(k, hn, [(x + side * 7, 10, 2), (x, 5, 6), (x - side * 4, 12, 7), (x + side * 3, 15, 6)], s=1.3)
        coins(k, fo, [(x + side * 6.6, 22, 0), (x, 24, 6.4)], s=1.2)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Ash Cultist (caster)

def ash_cultist():
    """Men and women who walked into the volcano to worship the wyrm and stayed. Ash-grey robes burnt at the hem, a
    red sash, a mantle of shed drake scales over the shoulders, and over the face the skull of a drake with its horns.
    Their hands are burnt black. They carry staves topped with an ember held in a claw, and they call the fire."""
    k = X.Kit("ash_cultist")
    hips = k.part("hips", (0, 19, 0))
    k.stack(hips, 0, 0, [(0, 13, 10), (8, 10, 7.6), (19, 9, 6.4)], "robe", "robe")
    k.box(hips, C(0, 18, 0, 10, 2.0, 7.4), "red", tag="sash")
    k.limb(hips, (3, 18, 3.6), (4, 8, 4.4), 2.0, "red", "sash_tail", d=0.4)
    for (x, z) in ((-4, 3), (3, 4), (0, -4), (-3, -3), (4, -2)):
        k.limb(hips, (x, 1.6, z), (x * 1.2, -0.4, z * 1.2), 1.8, "ash", "ash_hem", d=1.0)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.2
        th = k.part("thigh_" + nm, (x, 19, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 10, 0), (), th)
        ft = k.part("foot_" + nm, (x, 2, 0), (), sh)
        k.box(ft, C(x, 0, 1.2, 3.0, 1.4, 4.6), "dark", tag="foot")
    to = k.part("torso", (0, 19, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(19, 9, 6.4), (25, 10.4, 6.8), (30, 11.6, 7.0)], "robe", "robe")
    for i in range(9):                     # the mantle of shed scales
        a = math.radians(-120 + i * 30)
        x, z = math.sin(a) * 6.6, math.cos(a) * 4.4
        k.limb(to, (x, 31, z), (x * 1.3, 25, z * 1.3), 3.0, "scale", "scale_mantle", d=0.8)
        k.box(to, C(x * 1.25, 26, z * 1.28, 1.0, 0.6, 1.0), "fire", group="glow", tag="ember_crack")
    hd = k.part("head", (0, 30, 0.6), (("x", -10),), "torso")
    k.stack(hd, 0, -0.6, [(29, 9, 8), (34, 9.4, 8.6), (38, 6, 6)], "robe", "hood")
    k.box(hd, C(0, 33, 4.0, 4.4, 4.0, 3.4), "bone", tag="skull_mask")      # the drake-skull mask
    k.box(hd, C(0, 31.6, 7.0, 3.0, 2.4, 4.0), "bone", tag="skull_snout")
    for i in range(3):
        for sx in (-1, 1):
            k.shard(hd, (sx * 1.2, 31.4, 6.4 + i * 1.2), (0, -1, 0), 1.2, 0.5, mat="bone", tag="tooth")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.2, 34.4, 5.8, 1.2, 1.0, 0.4), "eye", group="glow", tag="eye")
        horn = [(sx * 2, 36.6, 3), (sx * 4.6, 39, 0), (sx * 6, 39, -3.4)]
        for (a, b), w in zip(zip(horn, horn[1:]), (1.4, 1.0)):
            k.limb(hd, a, b, w, "bone", "horn")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.6
        up = k.part("arm_" + nm, (x, 29, 0), (("x", -40 if side > 0 else -30), ("z", side * 8)), "torso")
        fo = k.part("fore_" + nm, (x, 21, 0), (("x", -40 if side > 0 else -50),), up)
        hn = k.part("hand_" + nm, (x, 13, 0), (), fo)
        k.stack(up, x, 0, [(21, 3.6, 3.8), (29, 4.2, 4.4)], "robe", "sleeve")
        k.stack(fo, x, 0, [(13, 5.4, 5.4), (21, 4.0, 4.0)], "robe", "sleeve")
        k.box(hn, C(x, 10.4, 0.4, 2.4, 3.0, 2.2), "dark", tag="hand")
        k.box(hn, C(x, 10.0, 1.4, 1.6, 0.8, 0.4), "fire", group="glow", tag="ember_crack")
    st = k.part("claw_staff", (-6.6, 11, 0.6), (("x", 75),), k.parts["hand_r"])
    k.limb(st, (-6.6, -12, 0.6), (-6.6, 30, 0.6), 1.2, "iron", "staff")
    for a in (0, 120, 240):
        r = math.radians(a)
        k.shard(st, (-6.6, 30, 0.6), (math.cos(r) * 0.6, 1, math.sin(r) * 0.6), 4.0, 1.0, mat="bone", tag="claw")
    k.blob(st, (-6.6, 32.6, 0.6), (1.8, 2.0, 1.8), "fire", "ember", step=0.6)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Kobold (swarm)

def kobold():
    """The wyrm's little servants: dog-snouted lizards no taller than a child, rust-red scale, two short horns, a tin
    helmet with a candle stuck on it, a necklace of stolen coins, a rag, a tail, and a pick for the gold. They come
    in packs and squeal his name."""
    k = X.Kit("kobold")
    hips = k.part("hips", (0, 11, 0))
    k.box(hips, C(0, 9, 0, 5.4, 3.2, 4.0), "hide", tag="hips")
    k.box(hips, C(0, 7, 2.1, 4.0, 4.0, 0.4), "red", tag="rag")
    tail = [(0, 9.6, -2), (0, 6, -6), (1, 2, -9), (2, 0.6, -12)]
    for (a, b), w in zip(zip(tail, tail[1:]), (2.4, 1.8, 1.2)):
        k.limb(hips, a, b, w, "hide", "tail")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 1.8
        th = k.part("thigh_" + nm, (x, 10, 0), (("x", -30),), "hips")
        sh = k.part("shin_" + nm, (x, 6, 0), (("x", 50),), th)
        ft = k.part("foot_" + nm, (x, 1.6, 0), (("x", -20),), sh)
        k.box(th, C(x, 5.8, 0, 2.2, 4.4, 2.6), "hide", tag="thigh")
        k.box(sh, C(x, 1.4, 0, 1.8, 4.6, 2.0), "hide", tag="shin")
        k.box(ft, C(x, 0, 1.0, 2.2, 1.2, 3.8), "hide", tag="foot")
        for t in (-0.6, 0.6):
            k.shard(ft, (x + t, 0.5, 2.8), (0, -0.3, 1), 1.0, 0.5, mat="bone", tag="foot")
    to = k.part("torso", (0, 11, 0), (("x", 20),), "hips")
    k.stack(to, 0, 0, [(11, 5.4, 4.0), (15, 6.4, 4.4), (18, 6.0, 4.0)], "hide", "body")
    k.box(to, C(0, 11, 2.0, 4.0, 6.0, 0.6), "belly", tag="belly")
    halo = [(-2.6, 17.6, 2.6), (-1.4, 16.0, 2.9), (0, 15.6, 3.0), (1.4, 16.0, 2.9), (2.6, 17.6, 2.6)]
    k.chain(to, (-2.6, 18, 2.4), (2.6, 18, 2.4), 3, mat="gold", w=0.5)
    coins(k, to, halo, s=0.7)
    hd = k.part("head", (0, 18, 0.6), (("x", -20),), "torso")
    k.box(hd, C(0, 18, 0.6, 4.4, 4.0, 4.4), "hide", tag="head")
    k.box(hd, C(0, 18.4, 4.6, 2.8, 2.2, 4.0), "hide", tag="snout")
    k.box(hd, C(0, 17.6, 4.6, 2.4, 0.8, 3.6), "belly", tag="jaw")
    k.box(hd, C(0, 18.6, 6.6, 1.4, 0.6, 0.4), "dark", tag="nostrils")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.6, 20.2, 2.8, 1.0, 0.8, 0.4), "eye", group="glow", tag="eye")
        k.shard(hd, (sx * 1.6, 21.8, -0.6), (sx * 0.3, 0.6, -1), 2.4, 0.9, mat="bone", tag="horn")
        k.shard(hd, (sx * 2.4, 19.6, 0.4), (sx, 0.4, -0.4), 2.0, 0.8, mat="hide", tag="ear_frill")
    k.box(hd, C(0, 21.6, 0.6, 5.0, 1.6, 5.0), "iron", tag="tin_helmet")
    k.box(hd, C(0, 23.2, 0.6, 1.2, 2.6, 1.2), "wax", tag="candle")
    k.box(hd, C(0, 23.0, 0.6, 2.2, 0.6, 2.2), "wax", tag="candle_drip")
    k.blob(hd, (0, 26.6, 0.6), (0.7, 1.1, 0.7), "fire", "candle_flame", step=0.4)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 4.0
        up = k.part("arm_" + nm, (x, 17, 0), (("x", -30 if side > 0 else -70), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 13, 0), (("x", -40 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 9, 0), (), fo)
        k.box(up, C(x, 13.2, 0, 1.8, 4.2, 2.0), "hide", tag="arm")
        k.box(fo, C(x, 9.2, 0, 1.8, 4.2, 2.0), "hide", tag="forearm")
        k.box(hn, C(x, 7.6, 0.3, 2.0, 1.8, 1.8), "hide", tag="hand")
    pk = k.part("pick", (-4, 8.4, 0.4), (("x", 70),), k.parts["hand_r"])
    k.limb(pk, (-4, 5, 0.4), (-4, 17, 0.4), 0.9, "iron", "haft")
    k.limb(pk, (-4, 17, -3), (-4, 17.6, 4), 1.2, "iron", "pick_head")
    k.shard(pk, (-4, 17, -3), (0, -0.4, -1), 2.2, 1.0, mat="iron", tag="pick_head")
    k.shard(pk, (-4, 17.6, 4), (0, -0.4, 1), 2.2, 1.0, mat="iron", tag="pick_head")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Drake (skirmisher, on the hound's bones)

def drake():
    """Ignavar's get, or something like it: wingless drakes as big as horses, lean and low, charcoal scale cracked to
    fire, a ridge of bone spines from the skull to the tail, and a throat that swells and glows before they breathe."""
    k = X.Kit("drake")
    body = k.part("body", (0, 12, 0))
    k.stack(body, 0, 2, [(7, 9.6, 12), (12, 10.4, 13), (16, 8.6, 11)], "scale", "chest")
    k.box(body, C(0, 6.6, 3, 7.0, 1.2, 11), "belly", tag="belly")
    spines(k, body, [(0, 16, z) for z in (6, 2, -2)], L=3.4, w=1.6)
    cracks(k, body, [((-5, 13, 6), (-5.4, 9, -1)), ((5, 14, 4), (5.4, 10, -3))], w=0.7)
    hd = k.part("head", (0, 14, 8), (("x", -6),), "body")
    neck = [(0, 13, 7), (0, 16, 12), (0, 18, 15)]
    for (a, b), w in zip(zip(neck, neck[1:]), (6.0, 5.0)):
        k.limb(hd, a, b, w, "scale", "neck")
    k.box(hd, C(0, 13.6, 10, 4.0, 2.0, 6.0), "fire", group="glow", tag="throat_glow")
    k.box(hd, C(0, 18, 17.6, 5.6, 4.0, 6.0), "scale", tag="skull")
    k.box(hd, C(0, 18, 23, 4.0, 3.0, 6.0), "scale", tag="snout")
    k.box(hd, C(0, 16.2, 21, 3.6, 1.6, 7.4), "scale", tag="jaw")
    k.box(hd, C(0, 17.6, 24, 3.2, 0.6, 3.6), "fire", group="glow", tag="mouth_fire")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.2, 20.4, 20, 1.2, 0.8, 1.6), "eye", group="glow", tag="eye")
        k.shard(hd, (sx * 2.2, 21.6, 18), (sx * 0.4, 0.4, -1), 5, 1.4, mat="bone", tag="horn")
    spines(k, hd, [(0, 22, 17), (0, 19, 13)], L=2.6, w=1.2, back=-0.7)
    ab = k.part("abdomen", (0, 12, -6), (), "body")
    k.stack(ab, 0, -10, [(7, 9.0, 10), (12, 9.4, 10), (15, 7.0, 8)], "scale", "haunch")
    spines(k, ab, [(0, 15, z) for z in (-7, -11, -14)], L=3.0, w=1.4)
    tail = [(0, 12, -15), (1, 9, -22), (3, 6, -29), (2, 4, -36)]
    for (a, b), w in zip(zip(tail, tail[1:]), (5.0, 3.6, 2.4)):
        k.limb(ab, a, b, w, "scale", "tail")
    k.shard(ab, tail[-1], (-0.3, 0, -1), 4, 2.4, mat="bone", tag="tail_blade")
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, (z, j, part) in enumerate(((5, 1, body), (-11, 4, ab))):
            nm = "leg_%s%d" % (s, i)
            lg = k.part(nm, (side * 5.0, 11, z), (), part)
            kn = (side * 8.0, 5.6, z + (2.4 if i == 0 else -2.4))
            k.limb(lg, (side * 5.0, 11, z), kn, 3.6, "scale", "leg")
            k.limb(lg, kn, (side * 7.6, 0.8, z + 1.0), 2.6, "scale", "foot")
            k.box(lg, C(side * 7.6, 0, z + 1.6, 3.6, 1.4, 4.6), "scale", tag="foot")
            for t in (-1.0, 0, 1.0):
                k.shard(lg, (side * 7.6 + t, 0.6, z + 3.6), (0, -0.3, 1), 1.6, 0.7, mat="bone", tag="foot")
            joints[nm] = ("LL" if side > 0 else "RL") + str(j)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


MOBS = {
    "kobold": dict(make=kobold, ent=(0.7, 1.5), stats=dict(hp=34, speed=0.36, dmg=8, armor=3, kb=0)),
    "hoard_golem": dict(make=hoard_golem, ent=(2.0, 3.8), stats=dict(hp=160, speed=0.18, dmg=21, armor=18, kb=1.0)),
    "ash_cultist": dict(make=ash_cultist, ent=(0.9, 2.6), stats=dict(hp=54, speed=0.22, dmg=10, armor=4, kb=0)),
    "drake": dict(make=drake, rig="crawler", ent=(1.6, 1.6), stats=dict(hp=52, speed=0.38, dmg=11, armor=8, kb=0.2)),
    "wyrm_priest": dict(make=wyrm_priest, ent=(1.3, 3.6), stats=dict(hp=300, speed=0.24, dmg=17, armor=14, kb=0.6), key=True),
    "ignavar": dict(make=ignavar, rig="crawler", texel=1, ent=(5.0, 5.0), stats=dict(hp=900, speed=0.22, dmg=28, armor=16, kb=1.0), boss=True),
}
