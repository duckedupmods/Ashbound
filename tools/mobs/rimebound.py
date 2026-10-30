"""The Rimebound: a prison where the cold came in and nobody got out, keepers and kept alike, who hold the world's
frozen prisons and stray forts, built by hand (tools/vox2.py). Black iron and grey wool, prison stripes, chains
and manacles, flesh gone blue-grey, frost-white rime over everything, and a pale violet cold-light in their eyes.
(Not Rimeholt's blue-ice vikings: these are jailers and convicts.)

    crawling_convict  swarm   a convict frozen on all fours, an iron collar and its chain dragging, a cage over his face
    jailer            guard   a turnkey in black iron and grey wool, a barred cage-helm, a ring of keys, a truncheon
                              and a lantern of cold violet fire
    glacier_hulk      brute   a giant convict frozen inside a block of ice that broke at his limbs, chains still on
    cold_chaplain     caster  the prison's priest, frost-bearded, a frozen book chained to him, the cold in his hands
    icicle_shiv       skirm   an escaped convict in rags of stripes, broken manacles, a shiv of ice in each fist
    rime_warden       elite   the warden: black plate rimed white, a long coat, a cage-helm, a great chain with an iron
                              ball wound round his arm

    python tools/monsterforge.py rimebound --preview ; python tools/mobsheet.py rimebound
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import grow
from _folk import lit, eyes, straps, legs, arms, held, quad

IRON = ramp("#060708", "#0c0e10", "#14171a", "#1e2226", "#2a2e34", "#383e46")
WOOL = ramp("#1c1a18", "#2c2926", "#3e3a35", "#524d46", "#68625a", "#807970")
STRIPE_A = ramp("#18181a", "#2a2a2c", "#5a5852", "#86837a", "#aaa69c", "#c8c4b8")
FROST = ramp("#5a6270", "#7a8290", "#9ca4b0", "#bcc4ce", "#dce2ea", "#f4f8fc")
FLESH = ramp("#1a2028", "#26303a", "#34404c", "#44525e", "#566472", "#6c7a88")
ICE = ramp("#4a6078", "#62809c", "#7ea0bc", "#9cbed6", "#bed8ea", "#e4f2fc")
LEATHER = ramp("#0c0a0a", "#161212", "#201a1a", "#2c2424")
BRASS = ramp("#1a1408", "#2e240e", "#483a16", "#64521e", "#806a28")
PARCH = ramp("#3a3430", "#56504a", "#746c64", "#928a80")
COLD = ramp("#2a0a5a", "#4a1a8a", "#7440c0", "#a07ae8", "#cab4ff", "#f0e8ff")


def shaders():
    stripes = lambda p, n, i, j, w, h: -0.55 if (j // 2) % 2 == 0 else 0.08
    return {
        "iron": X.surf(IRON, 0.54, 1.5, 0.12, 0.26, crust=(FROST, 0.26)),
        "wool": X.surf(WOOL, 0.5, 1.0, 0.24, 0.02, crust=(FROST, 0.2)),
        "stripes": X.surf(STRIPE_A, 0.72, 1.0, 0.12, 0.0, holes=True, pattern=stripes),
        "frost": X.facets(FROST, 0.04),
        "flesh": X.wrinkled(FLESH, 0.8),
        "ice": X.facets(ICE, 0.0),
        "leather": X.surf(LEATHER, 0.5, 1.1, 0.2, 0.04, crust=(FROST, 0.2)),
        "brass": X.surf(BRASS, 0.54, 1.4, 0.12, 0.22),
        "parch": X.surf(PARCH, 0.5, 1.0, 0.2, 0.0, stripe=2),
        "steel": X.surf(FROST, 0.6, 1.5, 0.06, 0.3),
        "cold": X.glow(COLD),
        "eye": X.glow(COLD, 0.86, 0.12),
        "dark": X.dark(IRON),
    }


GLOWS = {"cold", "eye"}


def rime(k, part, at, n, L, down=True, seed=1):
    """icicles hanging off an edge"""
    x0, y0, z0 = at
    for i in range(n):
        x = x0 + (i - (n - 1) / 2) * 1.2
        l = L * (0.5 + 0.5 * ((i * 0.618 + seed * 0.37) % 1))
        k.shard(part, (x, y0, z0), (0, -1 if down else 1, 0), l, 0.8, mat="frost", tag="icicle")


def manacle(k, part, x, y, r=2.6, chain_to=None, links=3):
    k.ring(part, x, y, 0, r, 1.2, "iron", "manacle", n=10, axis="y")
    if chain_to:
        k.chain(part, (x, y - 0.4, r * 0.6), chain_to, links, mat="iron", w=1.0)


def cage_helm(k, part, c, s=1.0):
    """an iron cage over the head: a band at the brow and the jaw, bars between, a ring on top"""
    cx, cy, cz = c
    for y in (cy - 3.0 * s, cy + 2.6 * s):
        k.ring(part, cx, y, cz, 3.8 * s, 0.9, "iron", "cage_band", n=14, axis="y")
    for i in range(10):
        a = i * 2 * math.pi / 10
        x, z = math.cos(a) * 3.8 * s, math.sin(a) * 3.8 * s
        k.limb(part, (cx + x, cy - 3.2 * s, cz + z), (cx + x * 0.92, cy + 2.8 * s, cz + z * 0.92), 0.7, "iron", "cage_bar")
        k.limb(part, (cx + x * 0.92, cy + 2.8 * s, cz + z * 0.92), (cx, cy + 5.2 * s, cz), 0.7, "iron", "cage_bar")
    k.ring(part, cx, cy + 5.6 * s, cz, 1.2 * s, 0.6, "iron", "cage_ring", n=8, axis="z")


# ================================================================ the Crawling Convict (swarm)

def crawling_convict():
    """The prisoners the cold took on their knees never got up off them. A convict frozen grey-blue, crawling on his
    hands and feet like a dog, his rags of stripes stiff with frost, an iron collar on his neck with its chain dragging
    behind him, and over his face the cage they put on the biters - the violet light behind the bars."""
    k = X.Kit("crawling_convict")
    body, hd, ab, joints = quad(k, "stripes", y=12, chest=((6, 10, 10), (10, 12, 11), (15, 11, 10)), haunch=((6, 9.6, 8.4), (10, 10.6, 9), (14, 9.6, 8.4)),
                                leg_w=3.0, foot_w=2.6, front_z=5, back_z=-7, x=5.6, leg_mat="flesh", head_at=(0, 13, 8), head_rot=-20, claw="flesh",
                                foot_len=4.0, knees=(-2.0, 3.0))
    k.blob(body, (0, 15.6, 0), (4.6, 2.6, 5.4), "stripes", "hunch", step=0.7)
    k.box(body, C(0, 9.0, 1.0, 9.0, 1.2, 9.4), "flesh", tag="belly")
    k.box(ab, C(0, 8.0, -7.0, 9.6, 3.6, 8.4), "stripes", tag="breeches")
    rime(k, body, (0, 9.0, 5.0), 5, 2.0, seed=2)
    rime(k, ab, (0, 8.0, -11.0), 5, 2.4, seed=5)
    for side in (1, -1):                          # manacles on the wrists and ankles
        for i, z in ((0, 5), (1, -7)):
            manacle(k, k.parts["leg_%s%d" % ("l" if side > 0 else "r", i)], side * 6.2, 3.4, 2.0)
    k.ring(hd, 0, 12.0, 6.0, 3.6, 1.6, "iron", "collar", n=12, axis="z")
    k.chain(body, (0, 11.0, 4.0), (0, 1.0, -16.0), 9, mat="iron", w=1.2)
    k.box(hd, C(0, 9.6, 10.6, 5.6, 6.4, 5.6), "flesh", tag="head")
    k.box(hd, C(0, 15.2, 10.0, 5.4, 1.4, 5.0), "frost", tag="frozen_hair")
    eyes(k, hd, 13.0, 13.45, 1.3, 1.1, h=0.7)
    k.box(hd, C(0, 10.4, 13.45, 3.0, 1.0, 0.3), "dark", tag="mouth")
    for i in range(5):                            # the biter's cage over the face
        x = -2.4 + i * 1.2
        k.limb(hd, (x, 9.0, 14.2), (x, 15.2, 14.2), 0.6, "iron", "face_bar")
    k.box(hd, C(0, 9.0, 13.8, 6.6, 0.8, 1.2), "iron", tag="face_band")
    k.box(hd, C(0, 14.8, 13.8, 6.6, 0.8, 1.2), "iron", tag="face_band")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Jailer (guard)

def jailer():
    """The turnkeys still walk their rounds. Black iron over grey wool gone white with frost, a cage-helm of bars over
    a face gone blue, a ring of keys as big as a man's head at the belt, an iron truncheon studded at the end, and a
    lantern that burns with the cold violet fire that lights the prison now."""
    k = X.Kit("jailer")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(8, 13.0, 10.0), (14, 12.0, 8.8), (20, 11.2, 8.0)], "wool", "greatcoat", step=1.0)
    rime(k, hips, (0, 8.0, 5.0), 7, 2.2, seed=1)
    k.box(hips, C(0, 19.0, 0, 12.0, 2.0, 8.6), "leather", tag="belt")
    k.ring(hips, -6.6, 13.6, 2.6, 3.0, 0.8, "brass", "key_ring", n=12, axis="x")
    for i in range(5):
        a = i * 0.9 - 1.8
        k.box(hips, C(-6.6, 13.6 + math.sin(a) * 3.0 - 3.4, 2.6 + math.cos(a) * 3.0, 0.6, 3.4, 0.8), "brass", tag="key")
    legs(k, hips, 19, 10.4, 3.4, "wool", "iron", knee_mat="iron", lean=-6, bend=8, w=5.2, cuff=True)
    to = k.part("torso", (0, 20, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(20, 11.2, 8.0), (25, 12.6, 8.4), (30, 14.6, 9.0), (34, 14.4, 8.6)], "wool", "coat")
    k.blob(to, (0, 27.6, 2.2), (6.0, 5.6, 3.0), "iron", "breastplate", step=0.7)
    for sx in (-1, 1):
        k.box(to, C(sx * 7.4, 30.6, 0, 4.0, 3.4, 9.0), "iron", tag="spaulder")
        rime(k, to, (sx * 7.4, 30.6, 4.6), 3, 1.6, seed=sx + 3)
    k.box(to, C(0, 33.0, 0, 11.0, 2.0, 9.0), "wool", tag="collar")
    hd = k.part("head", (0, 34, 0.6), (("x", -4),), "torso")
    k.box(hd, C(0, 34.4, 0.6, 6.0, 7.0, 6.0), "flesh", tag="face")
    eyes(k, hd, 37.4, 3.65, 1.3, 1.2, h=0.7)
    k.box(hd, C(0, 35.4, 3.65, 2.0, 0.4, 0.3), "dark", tag="mouth")
    k.box(hd, C(0, 33.4, 3.4, 4.0, 1.6, 0.6), "frost", tag="frost_beard")
    cage_helm(k, hd, (0, 37.6, 0.6), 1.0)
    arms(k, to, 7.8, 32, "wool", {1: ((("x", -50), ("z", -8)), (("x", -30),)), -1: ((("x", -40), ("z", 8)), (("x", -44),))}, glove="iron", w=3.6)
    ln = held(k, "lantern", "l", (7.8, 12.0, 0.4), (("x", 80),))
    k.limb(ln, (7.8, 12.0, 1.6), (7.8, 8.0, 1.6), 0.6, "iron", "lantern_hook")
    k.box(ln, C(7.8, 1.6, 1.6, 4.4, 1.0, 4.4), "iron", tag="lantern")
    k.box(ln, C(7.8, 2.6, 1.6, 3.4, 4.6, 3.4), "cold", tag="lantern_flame")
    for dx in (-1.9, 1.9):
        for dz in (-1.9, 1.9):
            k.box(ln, C(7.8 + dx, 2.6, 1.6 + dz, 0.6, 4.6, 0.6), "iron", tag="lantern_bar")
    k.shard(ln, (7.8, 7.2, 1.6), (0, 1, 0), 1.2, 3.2, mat="iron", tag="lantern_top")
    tr = held(k, "truncheon", "r", (-7.8, 14.0, 0.3), (("x", 84),))
    k.limb(tr, (-7.8, 9.0, 0.3), (-7.8, 15.0, 0.3), 1.4, "leather", "grip")
    k.limb(tr, (-7.8, 15.0, 0.3), (-7.8, 27.0, 0.3), 2.2, "iron", "truncheon")
    k.box(tr, C(-7.8, 24.0, 0.3, 3.4, 4.0, 3.4), "iron", tag="truncheon_head")
    for a in range(0, 360, 60):
        r = math.radians(a)
        k.shard(tr, (-7.8 + math.cos(r) * 1.7, 26.0, 0.3 + math.sin(r) * 1.7), (math.cos(r), 0.2, math.sin(r)), 1.4, 0.8, mat="iron", tag="stud")
    k.ring(tr, -7.8, 15.0, 0.3, 1.4, 0.4, "iron", "wrist_loop", n=8, axis="x")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Glacier Hulk (brute)

def glacier_hulk():
    """The biggest convict they ever held froze in the yard where they'd chained him, and the ice that took him took
    him whole: a block of grey-blue ice round his body, broken where his arms and legs tore free, the chains still
    on him, his face pressed against the inside of it with the violet in his eyes, and fists of ice the size of
    barrels."""
    k = X.Kit("glacier_hulk")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(12, 15, 11), (20, 16, 11.6)], "stripes", "breeches")
    legs(k, hips, 19, 10.6, 4.8, "flesh", "ice", knee_mat=None, lean=-4, bend=6, w=7.0, cuff=False)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        manacle(k, k.parts["shin_" + nm], side * 4.8, 4.0, 4.4)
        k.blob(k.parts["shin_" + nm], (side * 4.8, 4.0, 0), (4.6, 4.0, 4.6), "ice", "ice_boot", step=0.9)
    k.chain(hips, (4.8, 4.6, 3.0), (-4.8, 4.6, 3.0), 6, mat="iron", w=1.2)
    to = k.part("torso", (0, 20, 0), (("x", 10),), "hips")
    # the block of ice round the body: faceted, rough-edged where it broke, the man showing inside
    k.stack(to, 0, 0, [(19, 21, 15), (24, 23, 16), (30, 24, 16.6), (36, 23, 16), (40, 18, 13)], "ice", "ice_block", step=1.6)
    k.box(to, C(0, 22.0, 7.6, 12.0, 14.0, 1.0), "flesh", tag="body_inside")
    k.box(to, C(0, 26.0, 8.2, 8.0, 3.0, 0.4), "stripes", tag="stripes_inside")
    for i, (x, y) in enumerate(((-9.0, 30.0), (8.0, 25.0), (-4.0, 36.0), (10.0, 34.0), (0, 22.0))):     # cracks and broken facets
        k.shard(to, (x, y, 8.0), ((-1) ** i * 0.6, 1, 0.6), 4.0, 2.4, mat="ice", tag="ice_shard")
    for y, t in ((24.0, 2.0), (32.0, -2.0)):      # the chains round it
        for i in range(14):
            a = i * 2 * math.pi / 14
            x, z = math.cos(a) * 12.0, math.sin(a) * 8.6
            k.box(to, C(x, y + math.cos(a) * t * 0.3, z, 2.0, 1.2, 1.2) if i % 2 else C(x, y + math.cos(a) * t * 0.3, z, 1.2, 1.4, 2.0), "iron", tag="chain_round")
    rime(k, to, (0, 19.0, 7.6), 9, 3.0, seed=3)
    hd = k.part("head", (0, 38.0, 3.4), (("x", -10),), "torso")
    k.box(hd, C(0, 38.0, 3.4, 11.0, 10.0, 10.0), "ice", tag="ice_head")
    k.box(hd, C(0, 39.0, 8.0, 7.0, 7.0, 0.8), "flesh", tag="face_inside")        # pressed against the inside
    eyes(k, hd, 43.0, 8.85, 1.8, 1.6, h=0.8)
    k.box(hd, C(0, 40.0, 8.85, 3.6, 1.6, 0.3), "dark", tag="mouth")
    k.shard(hd, (3.0, 47.0, 3.0), (0.4, 1, 0), 4.0, 2.4, mat="ice", tag="ice_spike")
    k.shard(hd, (-3.0, 47.6, 2.0), (-0.3, 1, -0.3), 5.0, 2.6, mat="ice", tag="ice_spike")
    arms(k, to, 13.6, 36, "flesh", {1: ((("x", -30), ("z", -16)), (("x", -40),)), -1: ((("x", -50), ("z", 16)), (("x", -30),))}, w=6.2, long=1.15)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        manacle(k, k.parts["fore_" + nm], side * 13.6, 22.0, 3.8, chain_to=(side * 15.0, 10.0, 4.0), links=4)
        k.box(k.parts["arm_" + nm], C(side * 13.6, 29.0, 0, 7.4, 5.0, 7.4), "ice", tag="ice_shard_arm")
        for b in list(k.s.boxes):
            if b.part is k.parts["hand_" + nm]:
                k.s.boxes.remove(b)
        y = 36 - 8 * 1.15 - 7.6 * 1.15
        k.blob(k.parts["hand_" + nm], (side * 13.6, y - 3.4, 0.4), (5.0, 5.0, 5.0), "ice", "ice_fist", step=0.9)
        k.shard(k.parts["hand_" + nm], (side * 13.6, y - 1.0, 4.4), (0, 0.2, 1), 3.4, 2.0, mat="ice", tag="knuckle_ice")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.25)
    return k.s, k.parts


# ================================================================ the Cold Chaplain (caster)

def cold_chaplain():
    """The prison's priest prayed over the condemned; he prays still, and the cold answers. A long grey cassock white
    at the hem with frost, a beard of icicles, a face blue as slate, the book of the condemned frozen shut and
    chained to his belt, one hand raised with the violet cold pouring out of it."""
    k = X.Kit("cold_chaplain")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(1, 13.0, 11.0), (10, 11.6, 9.4), (21, 10.4, 7.8)], "wool", "cassock", step=1.0)
    k.box(hips, C(0, 1.0, 0, 13.6, 3.6, 11.6), "frost", tag="frost_hem")
    rime(k, hips, (0, 4.6, 5.8), 9, 2.4, seed=4)
    for side, nm in ((1, "l"), (-1, "r")):
        th = k.part("thigh_" + nm, (side * 3.0, 20, 0), (), hips)
        sh = k.part("shin_" + nm, (side * 3.0, 11, 0), (), th)
        ft = k.part("foot_" + nm, (side * 3.0, 2.4, 0), (), sh)
        k.box(ft, C(side * 3.0, 0, 3.0, 3.6, 1.6, 4.4), "leather", tag="foot")
    k.box(hips, C(0, 20.0, 0, 11.0, 1.6, 8.4), "leather", tag="belt")
    # the book chained to his belt, frozen shut
    k.chain(hips, (5.0, 19.6, 3.4), (6.6, 11.0, 4.6), 4, mat="iron", w=0.9)
    k.box(hips, C(6.6, 6.0, 4.6, 5.0, 6.4, 2.4), "leather", tag="book")
    k.box(hips, C(6.6, 6.2, 5.9, 4.4, 5.8, 0.3), "parch", tag="book_edge")
    k.box(hips, C(6.6, 6.0, 4.6, 5.6, 1.0, 2.8), "frost", tag="book_ice")
    k.box(hips, C(6.6, 9.0, 5.9, 1.4, 1.4, 0.4), "cold", tag="book_seal")
    to = k.part("torso", (0, 21, 0), (("x", 8),), "hips")
    k.stack(to, 0, 0, [(21, 10.4, 7.8), (26, 10.8, 7.8), (31, 12.0, 8.0), (34, 11.0, 7.4)], "wool", "cassock")
    for y in (22.0, 24.6, 27.2, 29.8):
        k.box(to, C(0, y, 4.0, 0.8, 0.8, 0.3), "iron", tag="button")
    k.box(to, C(0, 31.4, 0, 12.4, 2.8, 8.8), "wool", tag="mozzetta")
    hd = k.part("head", (0, 34, 0.6), (("x", -6),), "torso")
    k.box(hd, C(0, 34.4, 0.6, 5.8, 7.0, 5.8), "flesh", tag="face")
    eyes(k, hd, 37.4, 3.55, 1.3, 1.2, h=0.7)
    for i in range(7):                            # the icicle beard
        x = -2.4 + i * 0.8
        k.shard(hd, (x, 35.0, 3.4), (0, -1, 0.2), 3.0 + (3 - abs(i - 3)) * 1.4, 0.9, mat="frost", tag="icicle_beard")
    k.blob(hd, (0, 38.8, 0.2), (3.2, 1.6, 3.4), "frost", "frost_hair", step=0.6)
    k.box(hd, C(0, 39.4, 0.4, 4.4, 1.0, 4.4), "wool", tag="skullcap")
    arms(k, to, 6.8, 32, "wool", {1: ((("x", -140), ("z", -10)), (("x", -10),)), -1: ((("x", -20), ("z", 10)), (("x", -40),))}, glove="flesh", w=3.4)
    k.box(k.parts["fore_l"], C(6.8, 15.6, 0, 4.8, 3.0, 4.8), "wool", tag="sleeve_mouth")
    y = 32 - 8 - 7.6 - 2.8
    k.blob(k.parts["hand_l"], (6.8, y - 1.6, 0.6), (2.2, 2.2, 2.2), "cold", "cold_light", step=0.6)
    for d in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, -1, 0)):
        k.shard(k.parts["hand_l"], (6.8, y - 1.6, 0.6), d, 2.6, 0.6, mat="frost", tag="cold_ray")
    st = held(k, "sceptre", "r", (-6.8, 14.4, 0.4), (("x", 50),))
    k.limb(st, (-6.8, -2.0, 0.4), (-6.8, 22.0, 0.4), 1.2, "iron", "sceptre")
    k.box(st, C(-6.8, 22.0, 0.4, 1.0, 5.0, 1.0), "iron", tag="sceptre_cross")
    k.box(st, C(-6.8, 24.0, 0.4, 4.0, 1.0, 1.0), "iron", tag="sceptre_cross")
    k.box(st, C(-6.8, 24.0, 0.4, 1.2, 1.2, 1.2), "cold", tag="sceptre_light")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Icicle Shiv (skirmisher)

def icicle_shiv():
    """Some got out of their cells when the cold came. They never got out of the prison. Lean and starved, the
    stripes in rags, the manacles broken off at the wrists with a link or two still swinging, frostbitten feet bound
    in sacking, and in each fist a shiv broken off an icicle, sharper than iron."""
    k = X.Kit("icicle_shiv")
    hips = k.part("hips", (0, 19, 0))
    k.stack(hips, 0, 0, [(12, 9.8, 7.0), (19, 10.0, 7.2)], "stripes", "breeches")
    k.box(hips, C(0, 18.0, 0, 10.6, 1.4, 7.8), "leather", tag="rope_belt")
    legs(k, hips, 18, 9.8, 3.0, "stripes", "wool", knee_mat=None, lean=-12, bend=20, w=4.4, cuff=False)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        manacle(k, k.parts["shin_" + nm], side * 3.0, 3.6, 2.8, chain_to=(side * 3.6, 0.6, 3.6), links=2)
    to = k.part("torso", (0, 19, 0), (("x", 22),), "hips")
    k.stack(to, 0, 0, [(19, 10.0, 7.2), (24, 10.6, 7.2), (28.6, 12.0, 7.6), (31.6, 11.0, 7.0)], "stripes", "shirt")
    k.box(to, C(3.0, 22.0, 3.6, 3.0, 6.0, 0.4), "flesh", tag="torn_skin")
    k.box(to, C(0, 29.0, 3.8, 0.6, 1.0, 0.3), "dark", tag="prisoner_number")
    k.box(to, C(1.0, 29.0, 3.8, 0.6, 1.0, 0.3), "dark", tag="prisoner_number")
    hd = k.part("head", (0, 31.6, 0.6), (("x", -18),), "torso")
    k.box(hd, C(0, 32.0, 0.6, 5.6, 6.6, 5.6), "flesh", tag="face")
    eyes(k, hd, 35.0, 3.45, 1.3, 1.2, h=0.8)
    k.box(hd, C(0, 33.4, 3.45, 2.6, 0.6, 0.3), "dark", tag="grin")
    k.box(hd, C(-1.6, 35.6, 3.45, 0.4, 2.6, 0.3), "dark", tag="scar")
    k.blob(hd, (0, 37.2, 0.4), (3.2, 1.4, 3.2), "frost", "shaved_frost", step=0.6)
    k.box(hd, C(0, 30.0, 0.6, 7.0, 2.4, 6.4), "wool", tag="rag_scarf")
    arms(k, to, 6.4, 29, "flesh", {1: ((("x", -20), ("z", 30)), (("x", -60),)), -1: ((("x", -60), ("z", -20)), (("x", -40),))}, glove="flesh", w=3.0)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.4
        manacle(k, k.parts["fore_" + nm], x, 15.6, 2.4, chain_to=(x + side * 1.0, 11.0, 2.0), links=2)
        sv = held(k, "shiv_" + nm, nm, (x, 11.6, 0.4), (("x", 70 if side > 0 else 30),))
        k.limb(sv, (x, 9.0, 0.4), (x, 13.0, 0.4), 1.4, "wool", "shiv_wrap")
        k.shard(sv, (x, 13.0, 0.4), (0, 1, 0.05), 9.0, 2.0, mat="ice", tag="ice_shiv")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Rime Warden (elite)

def rime_warden():
    """The warden locked the gates when the cold came, with himself inside. He is still on duty: taller than his
    turnkeys in black plate furred white with rime, a long coat of grey wool to his boots, a cage-helm of heavy bars
    and the violet light behind it, and wound round his right arm the great chain of the yard with the iron ball that
    held the hulks, which he swings."""
    k = X.Kit("rime_warden")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(2, 14.4, 11.6), (10, 13.0, 10.0), (21, 12.0, 8.6)], "wool", "greatcoat", step=1.0)
    k.box(hips, C(0, 2.0, 0, 15.0, 2.4, 12.2), "frost", tag="frost_hem")
    rime(k, hips, (0, 4.4, 6.0), 9, 2.8, seed=6)
    k.box(hips, C(0, 4.0, 5.8, 1.0, 16.0, 0.6), "dark", tag="coat_split")
    k.box(hips, C(0, 20.0, 0, 13.0, 2.4, 9.4), "leather", tag="belt")
    k.box(hips, C(0, 19.8, 4.8, 3.0, 3.0, 0.6), "iron", tag="buckle")
    legs(k, hips, 20, 10.8, 3.6, "wool", "iron", knee_mat="iron", lean=-6, bend=8, w=5.6, cuff=True)
    to = k.part("torso", (0, 21, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(21, 12.0, 8.6), (26, 13.8, 9.2), (31, 16.8, 10.0), (35, 16.4, 9.4)], "wool", "coat")
    k.blob(to, (0, 29.0, 2.6), (7.0, 6.0, 3.6), "iron", "breastplate", step=0.7)
    k.box(to, C(0, 22.4, 4.6, 11.0, 4.0, 1.0), "iron", tag="fauld")
    rime(k, to, (0, 22.4, 5.2), 7, 2.0, seed=7)
    k.box(to, C(0, 30.0, 6.2, 3.0, 3.4, 0.4), "brass", tag="warden_badge")
    for sx in (-1, 1):
        k.blob(to, (sx * 9.6, 33.4, 0), (4.8, 3.2, 5.2), "iron", "pauldron", step=0.7)
        k.box(to, C(sx * 10.0, 30.4, 0, 6.2, 1.4, 9.4), "iron", tag="pauldron_lame")
        rime(k, to, (sx * 10.0, 30.4, 4.8), 4, 2.4, seed=sx + 9)
    k.blob(to, (0, 35.6, -0.4), (9.6, 2.0, 6.0), "frost", "rime_mantle", step=0.7)
    hd = k.part("head", (0, 35.6, 0.6), (("x", -4),), "torso")
    k.box(hd, C(0, 35.8, 0.6, 6.6, 7.4, 6.6), "iron", tag="helm_core")
    eyes(k, hd, 39.4, 3.95, 1.4, 1.4, h=0.9)
    cage_helm(k, hd, (0, 39.2, 0.6), 1.15)
    k.box(hd, C(0, 34.2, 1.0, 9.0, 2.4, 8.4), "iron", tag="gorget")
    arms(k, to, 9.8, 33, "wool", {1: ((("x", -30), ("z", -16)), (("x", -40),)), -1: ((("x", -50), ("z", 14)), (("x", -40),))}, glove="iron", w=4.2)
    for side in (1, -1):
        k.box(k.parts["fore_" + ("l" if side > 0 else "r")], C(side * 9.8, 18.0, 0, 5.0, 5.0, 5.0), "iron", tag="vambrace")
    for y in (19.0, 21.0, 23.0, 25.0):            # the yard chain wound round the right forearm
        k.ring(k.parts["fore_r"], -9.8, y, 0, 3.6, 1.0, "iron", "chain_wound", n=10, axis="y")
    # the free end of it and the ball, swinging out from the fist
    bl = held(k, "ball", "r", (-9.8, 14.0, 0.4), (("x", 120),))
    k.chain(bl, (-9.8, 14.0, 0.4), (-9.8, 28.0, 2.0), 7, mat="iron", w=1.4)
    k.blob(bl, (-9.8, 31.0, 2.4), (4.0, 4.0, 4.0), "iron", "iron_ball", step=0.8)
    for a in range(0, 360, 60):
        r = math.radians(a)
        k.shard(bl, (-9.8 + math.cos(r) * 3.6, 31.0 + math.sin(r) * 3.6, 2.4), (math.cos(r), math.sin(r), 0), 2.4, 1.2, mat="iron", tag="ball_spike")
    rime(k, bl, (-9.8, 27.4, 2.4), 3, 2.0, seed=12)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.15)
    return k.s, k.parts


MOBS = {
    "crawling_convict": dict(make=crawling_convict, rig="crawler", ent=(1.2, 1.4), stats=dict(hp=28, speed=0.32, dmg=7, armor=2, kb=0)),
    "jailer": dict(make=jailer, ent=(0.9, 2.9), stats=dict(hp=62, speed=0.23, dmg=10, armor=9, kb=0.3)),
    "glacier_hulk": dict(make=glacier_hulk, ent=(1.9, 4.0), stats=dict(hp=210, speed=0.17, dmg=19, armor=10, kb=1.0)),
    "cold_chaplain": dict(make=cold_chaplain, ent=(0.9, 2.8), stats=dict(hp=38, speed=0.22, dmg=7, armor=2, kb=0)),
    "icicle_shiv": dict(make=icicle_shiv, ent=(0.8, 2.5), stats=dict(hp=40, speed=0.35, dmg=8, armor=2, kb=0)),
    "rime_warden": dict(make=rime_warden, ent=(1.1, 3.4), stats=dict(hp=340, speed=0.24, dmg=16, armor=13, kb=0.7), key=True),
}
