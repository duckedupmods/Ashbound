"""The Glass Minaret's monsters, the Sunbound, each built by hand (tools/vox2.py). A sultan who bargained with a
djinn for a tower that would touch the sun got his tower and lost his court to it: his guards still keep it in their
mirror mail, his dancers still dance on its balconies, the sand that buried his city walks its stairs, and the djinn
sits on the roof in his lamp. Sandstone and turquoise glaze, beaten gold and polished silver, white silk, crimson and
indigo; amber glass, and the white-gold of sunfire in their eyes and their wounds.

    dune_scorpion   swarm   a scorpion the size of a hound, amber chitin banded dark, a glass sting full of sunfire
    glass_golem     brute   a giant of desert glass fused by lightning, sunfire in its cracks, a sandstone core, fists
                            of raw glass
    mirror_guard    guard   the sultan's guard: a spiked helm wound in a turban, a veil, scale mail polished to mirrors,
                            a round mirror shield that throws the sun, a crescent-bladed lance
    sandwraith      caster  a hooded robe with no one in it, its body a whirl of sand down to the floor, a gold mask, a
                            sunfire censer swung on chains
    blade_dancer    elite   the sultan's dancer: crimson silk and gold, a veil of coins, bells at wrist and ankle,
                            sashes streaming, two scimitars and a ring of knives on her back
    djinn_sultan    boss    the djinn: a giant of bronze skin seamed with sunfire rising in a twisting tail of fire from a
                            brass lamp the size of a cart; turbaned and horned, a beard of fire, gold at arm and throat,
                            the Djinnblade in one hand and a sun in the other

    python tools/monsterforge.py glass_minaret --preview ; python tools/mobsheet.py glass_minaret
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import tube, disc, _along, grow

AMBER = ramp("#2a1404", "#4a2408", "#743c0e", "#9c5614", "#c2741e", "#e09a34", "#f6c25a")
CHITIN = ramp("#140a04", "#24120a", "#3a1e0e", "#542c12", "#704018", "#8e5620")
GLASS = ramp("#3a2a10", "#6a4c18", "#a0761e", "#d4a030", "#f2c858", "#fff0b0")
TGLASS = ramp("#0a3a3c", "#126060", "#1c8884", "#30aea4", "#5ad0c2", "#a0f0e2")
TURQ = ramp("#04282a", "#0a4446", "#106464", "#1a8682", "#2aaaa0", "#52ccbe", "#8ae8d8")
SILVER = ramp("#1c222c", "#343c4a", "#545e6e", "#7c8a9a", "#a8b6c6", "#d4e0ec", "#f6fbff")
GOLD = ramp("#2a1804", "#4c300a", "#7a5014", "#a87422", "#d0a034", "#f0cc5a", "#fff0a0")
BRASS = ramp("#1e1206", "#382208", "#583810", "#7a5218", "#9c6c22", "#be8a30", "#dcae4c")
SILK = ramp("#4a4440", "#6e6660", "#948a82", "#b8aea4", "#d8d0c6", "#f2ece4")
CRIMSON = ramp("#200408", "#3a080e", "#5a0e16", "#7e1620", "#a42230", "#c8323e")
INDIGO = ramp("#080a1e", "#0e1230", "#161c48", "#202a62", "#2c3a80")
SAND = ramp("#4a3a24", "#6a5434", "#8a7048", "#a88c5e", "#c4a878", "#dcc496")
SUN = ramp("#5a1a04", "#9a3a08", "#d8680e", "#ff9a1c", "#ffd04a", "#fff4c0")
SKIN = ramp("#2e1a10", "#4a2c1a", "#684026", "#865634", "#a46e44", "#c08a5a")
DJINN = ramp("#1a0806", "#2c0e08", "#44160c", "#5e2010", "#7a2c16", "#96381c")
SMOKE = ramp("#100a08", "#1c120e", "#2a1c16", "#3a2820")
GORE = ramp("#100406", "#1e080a", "#2e0e10", "#401416")


def plates(p, n, i, j, w, h):
    """scale mail: rows of small plates, each bright at its top and dark at its foot"""
    row = j // 3
    if j % 3 == 2:
        return -0.3
    if (i + (row % 2) * 2) % 4 == 3:
        return -0.16
    return 0.14 if j % 3 == 0 else 0.02


def weave(p, n, i, j, w, h):
    return -0.12 if (i + j) % 4 == 0 else (0.04 if (i - j) % 4 == 0 else 0)


def shaders():
    return {
        "chitin": X.surf(CHITIN, 0.5, 1.5, 0.12, 0.22, stripe=5),
        "amber": X.surf(AMBER, 0.52, 1.5, 0.12, 0.24),
        "glass": X.facets(GLASS),
        "tglass": X.facets(TGLASS),
        "turq": X.surf(TURQ, 0.56, 1.4, 0.12, 0.2, pattern=lambda p, n, i, j, w, h: -0.14 if (i % 4 == 0 or j % 4 == 0) else 0),
        "silver": X.surf(SILVER, 0.58, 1.8, 0.08, 0.3),
        "mail": X.surf(SILVER, 0.54, 1.6, 0.08, 0.0, pattern=plates),
        "gold": X.surf(GOLD, 0.5, 1.5, 0.12, 0.24),
        "brass": X.surf(BRASS, 0.5, 1.5, 0.14, 0.24, drip=(SMOKE, 0.08)),
        "silk": X.surf(SILK, 0.54, 1.1, 0.12, 0.04, pattern=weave),
        "crimson": X.surf(CRIMSON, 0.5, 1.1, 0.14, 0.04, pattern=weave),
        "indigo": X.surf(INDIGO, 0.5, 1.0, 0.18, 0.0, holes=True),
        "sand": X.surf(SAND, 0.5, 1.2, 0.3, 0.04),
        "sandstone": X.surf(SAND, 0.5, 1.3, 0.2, 0.14, stripe=4),
        "skin": X.wrinkled(SKIN, 0.8),
        "djinn": X.veined(DJINN, SUN, 0.16, 0.014),
        "flame": X.glow(SUN),
        "band": X.glow(SUN, 0.42, 0.3),
        "sun": X.glow(SUN, 0.8, 0.16),
        "eye": X.glow(SUN, 0.86, 0.12),
        "smoke": X.surf(SMOKE, 0.5, 1.0, 0.2, 0.0),
        "mouth": X.dark(GORE),
        "dark": X.dark(INDIGO),
    }


GLOWS = {"flame", "band", "sun", "eye"}


def lit(k):
    """everything in a glowing material glows"""
    for b in k.s.boxes:
        if b.mat in GLOWS:
            b.group = "glow"


# ================================================================ shared brushes

def scimitar(k, part, x, y0, L, w, curve=0.06, edge="silver", tag="scimitar"):
    """a scimitar standing up from y0 along +y, curving back toward -z and widening toward the tip before the point"""
    n = int(L / 2.0)
    for i in range(n):
        t = i / n
        y = y0 + i * 2.0
        z = -curve * i * i
        ww = w * (0.8 + 0.5 * math.sin(t * math.pi * 0.85)) * (1 - max(0, t - 0.85) * 4)
        if ww < 0.6:
            continue
        k.box(part, C(x, y, z - ww * 0.2, 0.6, 2.1, ww), "silver", tag=tag)
        k.box(part, C(x, y, z + ww * 0.3 + 0.2, 0.65, 2.1, 0.5), edge, tag=tag + "_edge")
    k.shard(part, (x, y0 + n * 2.0, -curve * n * n), (0, 1, -curve * 2 * n / 2.0), 3.0, 1.0, mat="silver", tag=tag + "_point")


def turban(k, part, c, r, h, mat="silk", band="crimson", gem="sun"):
    """a wound turban: stacked wraps each a little offset, a band of another cloth, a jewel at the front"""
    cx, cy, cz = c
    n = int(h / 1.2)
    for i in range(n):
        t = i / n
        rr = r * (0.92 + 0.42 * math.sin(min(1.0, t / 0.55) * math.pi / 2)) if t < 0.55 else r * 1.34 * math.cos((t - 0.55) / 0.45 * math.pi / 2) ** 0.8
        rr = max(rr, r * 0.18)
        off = 0.35 * math.sin(i * 1.7)
        k.box(part, C(cx + off, cy + i * 1.2, cz, rr * 2, 1.25, rr * 2.05), band if i in (1, n // 3) else mat, tag="turban")
        if 0 < i < n - 2 and i % 2 == 0:            # the wraps crossing over the front
            k.limb(part, (cx - rr * 0.9, cy + i * 1.2, cz + rr * 0.95), (cx + rr * 0.9, cy + i * 1.2 + 1.8, cz + rr * 0.95), 0.6, band, "turban_wrap", d=0.5)
    k.shard(part, (cx, cy + n * 1.2, cz), (0, 1, 0), r * 0.6, r * 0.3, mat="gold", tag="turban_finial")
    k.box(part, C(cx, cy + h * 0.3, cz + r * 1.05, r * 0.5, r * 0.5, 0.6), "gold", tag="turban_jewel_set")
    k.box(part, C(cx, cy + h * 0.3 + r * 0.08, cz + r * 1.05 + 0.3, r * 0.3, r * 0.34, 0.5), gem, tag="turban_jewel")


# ================================================================ the Dune Scorpion (swarm, crawler)

def dune_scorpion():
    """The sand round the Minaret is full of them, and the stairs. A scorpion the size of a hound: amber chitin
    banded dark brown, claws that can take a man's leg off, eight quick legs, and a tail curled over its back ending in
    a sting of glass with sunfire in it, so that they light the dark halls where they come."""
    k = X.Kit("dune_scorpion")
    body = k.part("body", (0, 7, 0))
    for i, (z, w) in enumerate(((5, 9.0), (2, 10.4), (-1, 10.6), (-4, 9.8))):
        k.blob(body, (0, 7.2, z), (w / 2, 2.6, 2.0), "amber" if i % 2 else "chitin", "carapace", step=0.8)
    k.box(body, C(0, 4.4, 0.4, 8.6, 1.6, 11.0), "chitin", tag="belly")
    hd = k.part("head", (0, 7, 7), (), "body")
    k.box(hd, C(0, 5.6, 8.6, 7.4, 3.6, 4.0), "amber", tag="head")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.0, 8.8, 9.4, 0.8, 0.8, 0.8), "eye", tag="eye")
        k.box(hd, C(sx * 2.6, 7.6, 10.2, 0.6, 0.6, 0.6), "eye", tag="eye")
        k.box(hd, C(sx * 1.0, 4.8, 10.8, 1.0, 1.0, 2.0), "chitin", tag="mandible")
        # the claws: an arm forward, the great pincer
        sh = (sx * 4.0, 6.4, 8.6)
        el = (sx * 8.6, 7.8, 12.0)
        wr = (sx * 7.4, 6.4, 17.0)
        k.limb(hd, sh, el, 2.2, "amber", "claw_arm")
        k.limb(hd, el, wr, 2.6, "chitin", "claw_arm")
        k.blob(hd, (wr[0], 6.6, 18.6), (2.6, 2.0, 2.8), "amber", "pincer_hand", step=0.7)
        k.limb(hd, (wr[0] - sx * 0.6, 7.0, 20.4), (wr[0] - sx * 1.6, 7.4, 24.6), 1.4, "chitin", "pincer_finger")
        k.limb(hd, (wr[0] + sx * 0.8, 6.0, 20.4), (wr[0] - sx * 0.4, 5.8, 24.0), 1.2, "amber", "pincer_finger")
    ab = k.part("abdomen", (0, 7, -5), (), "body")
    pts = [(0, 8, -6), (0, 10, -10.6), (0, 14.4, -13.4), (0, 19.4, -12.8), (0, 22.6, -9.4), (0, 22.8, -5.6)]
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        w = 4.0 - i * 0.4
        k.limb(ab, a, b, w, "amber" if i % 2 == 0 else "chitin", "tail_seg")
        k.box(ab, C(b[0], b[1] - w * 0.6, b[2], w * 1.15, w * 1.15, w * 1.15), "chitin", tag="tail_joint")
    k.blob(ab, (0, 22.0, -3.6), (1.8, 1.8, 2.2), "glass", "venom_bulb", step=0.6)
    k.blob(ab, (0, 22.0, -3.6), (1.0, 1.0, 1.4), "sun", "venom_light", step=0.5)
    k.shard(ab, (0, 21.4, -2.0), (0, -0.7, 1), 3.4, 1.0, mat="glass", tag="sting")
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, z in enumerate((4.0, 1.4, -1.2, -3.8)):
            nm = "leg_%s%d" % (s, i)
            lg = k.part(nm, (side * 4.2, 6.6, z), (), body)
            kn = (side * 9.0, 10.4, z * 1.3 + 0.6)
            ft = (side * 11.6, 0.0, z * 1.7 + 1.0)
            k.limb(lg, (side * 4.2, 6.6, z), kn, 1.4, "amber", "leg")
            k.box(lg, C(kn[0], kn[1] - 0.8, kn[2], 1.6, 1.6, 1.6), "chitin", tag="knee")
            k.limb(lg, kn, ft, 1.1, "chitin", "leg")
            k.shard(lg, (ft[0], 1.4, ft[2]), (0, -1, 0), 1.6, 0.8, mat="chitin", tag="foot")
            joints[nm] = ("LL" if side > 0 else "RL") + str(i + 1)
    lit(k)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Glass Golem (brute)

def glass_golem():
    """When the djinn walks the tower in a temper the lightning comes down on the dunes, and some of what it melts
    gets up. A giant of fused desert glass, amber and turquoise, its body a heap of slabs and shards round a core of
    sandstone, sunfire burning down every crack in it; a head that is one great faceted stone with a sun for an eye,
    and fists of raw glass the size of barrels."""
    k = X.Kit("glass_golem")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(14, 16, 12), (22, 19, 13)], "sandstone", "core")
    for x, z, s in ((-6, 4, 1.0), (5, 5, 0.8), (0, -6, 1.1)):
        k.box(hips, C(x, 13 + s, z, 6 * s, 8 * s, 4 * s), "glass", tag="slab")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.4
        th = k.part("thigh_" + nm, (x, 19, 0), (("x", -8), ("z", side * 10)), "hips")
        sh = k.part("shin_" + nm, (x, 10, 0), (("x", 12),), th)
        ft = k.part("foot_" + nm, (x, 3.2, 0), (("x", -4),), sh)
        k.stack(th, x, 0, [(10, 8.4, 8.6), (19, 10, 10)], "glass", "thigh")
        k.box(th, C(x + side * 2.0, 12, 3.0, 4.0, 6.0, 3.0), "tglass", tag="facet")
        k.stack(sh, x, 0, [(3, 9.6, 10), (10, 8.6, 9.0)], "tglass", "shin")
        k.box(sh, C(x, 6.0, 4.6, 0.8, 4.0, 0.6), "sun", tag="crack")
        k.box(ft, C(x, 0, 1.8, 11.4, 3.6, 13.6), "glass", tag="foot")
    # ---------------------------------------------------------------- torso: slabs of glass round a sandstone core
    to = k.part("torso", (0, 22, 0), (("x", 12),), "hips")
    k.stack(to, 0, 0, [(22, 18, 12), (30, 22, 14), (38, 26, 15)], "sandstone", "core")
    k.blob(to, (0, 31.6, 6.6), (4.0, 4.0, 2.0), "sun", "heart", step=0.6)
    for (x, y, z, sx, sy, sz, m) in ((-7, 24, 6.4, 7, 10, 3, "glass"), (6, 23, 6.6, 6, 8, 3, "tglass"),
                                     (-8, 34, 6.0, 8, 9, 3.4, "tglass"), (7, 33, 6.4, 7, 10, 3.4, "glass"),
                                     (0, 40, 5, 12, 5, 4, "glass"), (-12, 30, 0, 5, 12, 10, "glass"),
                                     (12, 29, 0, 5, 13, 10, "tglass"), (0, 26, -7.4, 16, 14, 3, "glass")):
        k.box(to, C(x, y, z, sx, sy, sz), m, tag="slab")
    for (p0, p1) in (((-3, 25, 8.4), (-1, 37, 8.2)), ((3, 24, 8.4), (5, 36, 8.6)), ((-10, 33, 7.8), (-6, 41, 7.4))):
        k.limb(to, p0, p1, 0.8, "sun", "crack")
    for sx in (-1, 1):                            # shards grown from its shoulders, the way lightning glass grows
        k.cluster(to, (sx * 12, 41, 0), 4, 10, 3.2, mat="glass" if sx > 0 else "tglass", seed=3 + sx, spread=0.6, up=(sx * 0.4, 1, -0.2))
    k.cluster(to, (0, 41, -5), 3, 12, 3.4, mat="tglass", seed=7, spread=0.5, up=(0, 0.9, -0.6))
    # ---------------------------------------------------------------- the head: one faceted stone, a sun for an eye
    hd = k.part("head", (0, 42, 3), (("x", -12),), "torso")
    for i, (w, h) in enumerate(((7.4, 2.4), (9.0, 2.6), (8.6, 2.4), (6.6, 2.2), (4.0, 1.6))):
        k.box(hd, C(0, 41.6 + sum(x[1] for x in ((7.4, 2.4), (9.0, 2.6), (8.6, 2.4), (6.6, 2.2))[:i]), 4.4, w, h + 0.05, w * 0.9), "tglass", tag="head")
    k.box(hd, C(0, 45.6, 8.6, 5.4, 3.0, 0.8), "dark", tag="brow_shadow")
    k.box(hd, C(0, 45.8, 9.0, 3.4, 2.4, 0.8), "eye", tag="eye")
    k.box(hd, C(0, 46.3, 9.3, 1.4, 1.2, 0.6), "sun", tag="eye_core")
    k.cluster(hd, (0, 51.4, 4.4), 3, 6, 2.0, mat="glass", seed=11, spread=0.4, up=(0, 1, -0.1))
    # ---------------------------------------------------------------- arms: shards to fists of raw glass
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 17.0
        up = k.part("arm_" + nm, (x, 38, 0), (("x", -18), ("z", side * 14)), "torso")
        fo = k.part("fore_" + nm, (x, 26, 0), (("x", -34),), up)
        hn = k.part("hand_" + nm, (x, 14, 0), (), fo)
        k.blob(up, (x - side * 1.0, 38.0, 0), (6.4, 5.0, 6.6), "glass" if side > 0 else "tglass", "shoulder", step=1.0)
        k.limb(up, (x, 36, 0), (x, 27, 0), 6.0, "sandstone", "upper_arm")
        k.box(up, C(x + side * 2.4, 29, 1.0, 4.0, 7.0, 6.0), "tglass", tag="slab")
        k.stack(fo, x, 0, [(15, 8.4, 8.6), (25, 7.0, 7.2)], "glass", "forearm")
        k.limb(fo, (x - side * 3.6, 24, 3.2), (x - side * 3.0, 16, 4.0), 0.7, "sun", "crack")
        k.blob(hn, (x, 9.0, 0.6), (7.0, 6.0, 7.0), "glass" if side < 0 else "tglass", "fist", step=1.0)
        k.cluster(hn, (x, 5.0, 2.0), 3, 5.4, 2.2, mat="glass", seed=13 + side, spread=0.9, up=(0, -1, 0.8))
    lit(k)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Mirror Guard (guard)

def mirror_guard():
    """The sultan's guard still stands at every door of his tower: tall men in scale mail polished until every plate
    is a mirror, a spiked helm wound round with a white turban, a veil of mail across the face so that only the eyes
    burn through; a round shield of polished silver that throws the sun into your eyes, and a long lance with a
    crescent blade."""
    k = X.Kit("mirror_guard")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(10, 12.4, 8.8), (22, 12.2, 8.2)], "mail", "mail_skirt")
    k.box(hips, C(0, 20.4, 0, 13.4, 2.2, 9.0), "crimson", tag="sash")
    k.box(hips, C(-4.4, 12.6, 4.4, 2.6, 8.0, 0.6), "crimson", tag="sash_end")
    k.box(hips, C(0, 20.6, 4.6, 3.0, 1.8, 0.6), "gold", tag="buckle")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.4
        th = k.part("thigh_" + nm, (x, 21, 0), (("x", -4), ("z", side * 4)), "hips")
        sh = k.part("shin_" + nm, (x, 11.4, 0), (("x", 6),), th)
        ft = k.part("foot_" + nm, (x, 2.8, 0), (("x", -2),), sh)
        k.stack(th, x, 0, [(11.6, 5.4, 5.8), (20, 6.2, 6.6)], "indigo", "trouser")
        k.stack(sh, x, 0, [(3, 4.6, 5.0), (11.4, 5.0, 5.4)], "silver", "greave")
        k.box(sh, C(x, 10.6, 0, 5.6, 1.0, 6.0), "gold", tag="greave_rim")
        k.box(ft, C(x, 0, 1.6, 5.2, 2.6, 8.0), "crimson", tag="foot")
        k.shard(ft, (x, 1.4, 5.4), (0, 0.8, 1), 2.0, 1.2, mat="crimson", tag="toe")
    # ---------------------------------------------------------------- torso: mirror mail
    to = k.part("torso", (0, 22, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(22, 12.2, 8.2), (27, 14, 8.6), (32, 17.6, 9.6), (37, 19.6, 9.8), (39.4, 15, 8.2)], "mail", "cuirass")
    disc(k, to, (0, 32.0, 5.0), 3.0, "z", "silver", "chest_mirror", thick=0.8)
    disc(k, to, (0, 32.0, 5.4), 1.4, "z", "sun", "chest_glint", thick=0.4)
    for sx in (-1, 1):
        k.blob(to, (sx * 10.0, 36.6, 0), (4.6, 3.0, 5.0), "silver", "pauldron", step=0.8)
        for i in range(2):
            k.box(to, C(sx * (10.4 + i * 0.4), 33.4 - i * 1.8, 0, 6.0, 1.6, 9.0), "mail", tag="lame")
        k.shard(to, (sx * 10.6, 39.2, 0), (sx * 0.4, 1, 0), 3.0, 1.4, mat="gold", tag="pauldron_spike")
    cape = k.part("cape", (0, 39, -5), (("x", 5),), to, bone=False)
    k.stack(cape, 0, -5.4, [(6, 15, 1.0), (24, 16, 1.0), (39, 15, 1.2)], "indigo", "cape")
    k.box(cape, C(0, 6, -5.4, 15.4, 1.2, 1.3), "gold", tag="cape_hem")
    # ---------------------------------------------------------------- helm: spiked, a turban wound round it, a mail veil
    hd = k.part("head", (0, 39, 0.6), (("x", -4),), "torso")
    k.box(hd, C(0, 38.4, 0.6, 5.6, 6.4, 5.6), "dark", tag="face")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.3, 41.6, 3.45, 1.6, 0.6, 0.3), "eye", tag="eye")
    k.box(hd, C(0, 37.4, 3.4, 6.0, 3.8, 0.8), "mail", tag="veil")
    for x in (-2.4, -0.8, 0.8, 2.4):
        k.box(hd, C(x, 36.4, 3.9, 0.6, 0.6, 0.4), "gold", tag="veil_coin")
    turban(k, hd, (0, 42.2, 0.6), 3.6, 4.8)
    k.blob(hd, (0, 47.4, 0.6), (2.6, 1.6, 2.6), "silver", "helm_dome", step=0.5)
    k.shard(hd, (0, 48.6, 0.6), (0, 1, 0), 5.4, 1.4, mat="silver", tag="helm_spike")
    k.stack(hd, 0, -0.6, [(34.6, 7.0, 6.8), (40, 7.4, 7.0)], "mail", "aventail")
    # ---------------------------------------------------------------- arms: the mirror shield, the crescent lance
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 10.4
        up = k.part("arm_" + nm, (x, 36, 0), (("x", -34 if side > 0 else -24), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 27, 0), (("x", -56 if side > 0 else -72),), up)
        hn = k.part("hand_" + nm, (x, 18, 0), (), fo)
        k.limb(up, (x, 35, 0), (x, 27.6, 0), 4.0, "mail", "upper_arm")
        k.limb(fo, (x, 26.6, 0), (x, 19.4, 0), 3.6, "indigo", "forearm")
        k.box(fo, C(x, 19.6, 0, 4.4, 5.4, 4.4), "silver", tag="vambrace")
        k.box(fo, C(x, 24.2, 0, 4.6, 0.8, 4.6), "gold", tag="vambrace_rim")
        k.box(hn, C(x, 15.6, 0.4, 3.6, 3.2, 3.8), "silver", tag="gauntlet")
    sh = k.part("shield", (14, 17, 2), (("y", 8),), k.parts["hand_l"], bone=False)
    disc(k, sh, (15.0, 17.5, 2.0), 9.0, "x", "silver", "mirror", thick=1.4)
    disc(k, sh, (15.6, 17.5, 2.0), 7.4, "x", "silver", "mirror_face", thick=0.6)
    for a in range(24):
        a0, a1 = a * math.pi / 12, (a + 1) * math.pi / 12
        k.limb(sh, (15.8, 17.5 + math.sin(a0) * 9.0, 2.0 + math.cos(a0) * 9.0), (15.8, 17.5 + math.sin(a1) * 9.0, 2.0 + math.cos(a1) * 9.0), 1.2, "gold", "rim")
    for a in range(0, 360, 30):                   # a sunburst engraved round the boss
        r = math.radians(a)
        k.limb(sh, (16.0, 17.5 + math.sin(r) * 2.4, 2.0 + math.cos(r) * 2.4), (16.0, 17.5 + math.sin(r) * 5.6, 2.0 + math.cos(r) * 5.6), 0.5, "gold", "ray")
    disc(k, sh, (16.2, 17.5, 2.0), 2.0, "x", "sun", "glint", thick=0.6)
    for sx_, sy_ in ((1, 1), (-1, -1)):           # the sun caught in it
        k.box(sh, C(16.1, 17.5 + sy_ * 4.0, 2.0 + sx_ * 3.6, 0.3, 2.4, 0.6), "sun", tag="glare")
    ln = k.part("lance", (-10.4, 15.6, 0.6), (("x", 78),), k.parts["hand_r"], bone=False)
    k.limb(ln, (-10.4, -12, 0.6), (-10.4, 44, 0.6), 1.3, "brass", "haft")
    for y in (-10, 6, 22, 38):
        k.box(ln, C(-10.4, y, 0.6, 1.9, 1.2, 1.9), "turq", tag="haft_band")
    k.box(ln, C(-10.4, 43.6, 0.6, 2.2, 2.2, 2.2), "gold", tag="socket")
    for i in range(11):                           # the crescent: two horns out to the sides, a long point up the middle
        a = math.radians(-80 + i * 16)
        k.limb(ln, (-10.4, 47 + math.cos(a) * 2.0 - 1.6, 0.6 + math.sin(a) * 5.4), (-10.4, 47 + math.cos(a + 0.28) * 2.0 - 1.6, 0.6 + math.sin(a + 0.28) * 5.4), 1.6, "silver", "crescent")
    k.shard(ln, (-10.4, 47, 0.6), (0, 1, 0), 9.0, 1.8, mat="silver", tag="point")
    k.box(ln, C(-10.4, 44.6, 0.6, 1.0, 3.4, 1.0), "sun", tag="crescent_gem")
    for z in (-0.6, 0.6):
        k.limb(ln, (-10.4, 43.6, 0.6 + z), (-10.4, 36, 0.6 + z * 4), 1.2, "crimson", "pennon", d=0.4)
    lit(k)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Sandwraith (caster)

def sandwraith():
    """The sand that buried the sultan's city came up the Minaret looking for him. A hooded robe of tattered indigo
    with no one inside it, its hem coming apart into a whirl of sand that spins down to the floor; a gold mask hung in
    the dark of the hood with sunfire for eyes, hands of wrapped linen, and a censer of brass it swings on chains,
    burning, so the sand storms where it walks."""
    k = X.Kit("sandwraith")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(16, 10.4, 7.2), (20, 10.6, 7.2)], "indigo", "waist")
    whirl = k.part("whirl", (0, 20, 0), (), "hips", bone=False)
    for i in range(16):                           # the whirl: rings of sand spun narrower toward the floor
        y = 17.4 - i * 1.1
        r = 8.4 - i * 0.42
        a0 = i * 0.7
        for s in range(5):
            a = a0 + s * 2 * math.pi / 5
            k.box(whirl, C(math.cos(a) * r * 0.5, y, math.sin(a) * r * 0.5, r * 0.95, 1.2, r * 0.7), "sand", tag="whirl")
    k.blob(whirl, (0, 1.0, 0), (3.0, 1.0, 3.0), "sand", "pool", step=0.5)
    for i in range(8):                            # sand spat off the edge of the whirl
        a = i * 0.8
        k.box(whirl, C(math.cos(a) * 7.6, 4 + i * 1.6, math.sin(a) * 7.6, 0.8, 0.8, 0.8), "sand", tag="grain")
    robe = k.part("robe", (0, 20, 0), (), "hips", bone=False)
    k.stack(robe, 0, -0.4, [(11, 13.4, 10.6), (16, 11.6, 8.6), (20, 10.6, 7.4)], "indigo", "robe")
    for i in range(-5, 6):                        # the hem in streamers, unravelling into the sand
        a = math.radians(i * 30)
        k.shard(robe, (math.sin(a) * 6.0, 11.4, math.cos(a) * 4.8), (math.sin(a) * 0.4, -1, math.cos(a) * 0.3), 4.0 + (i % 3) * 1.6, 1.8, mat="indigo", tag="streamer")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.8
        th = k.part("thigh_" + nm, (x, 19, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 10.4, 0), (), th)
        ft = k.part("foot_" + nm, (x, 2.4, 0), (), sh)
        k.box(ft, C(x, 0, 0, 0.4, 0.4, 0.4), "sand", tag="foot")
    to = k.part("torso", (0, 20, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(20, 10.6, 7.4), (26, 12.4, 7.8), (31, 14.6, 8.4), (35, 12, 7.6)], "indigo", "robe_top")
    k.box(to, C(0, 33.8, 0, 15.4, 1.6, 9.0), "gold", tag="collar")
    for i in range(-3, 4):
        k.box(to, C(i * 1.8, 31.6 - abs(i) * 0.4, 4.4, 1.2, 1.6, 0.6), "gold", tag="coin")
    k.box(to, C(-2.2, 22, 3.9, 1.2, 8.0, 0.6), "silk", tag="wrap")
    # ---------------------------------------------------------------- the hood, a gold mask in its dark
    hd = k.part("head", (0, 35, 0.6), (("x", -8),), "torso")
    k.stack(hd, 0, 0.0, [(33.6, 9.0, 8.6), (40, 9.4, 9.0), (43.6, 6.6, 7.4), (45.6, 2.4, 4.0)], "indigo", "hood")
    k.box(hd, C(0, 35.0, 3.6, 6.4, 7.2, 1.4), "dark", tag="hood_dark")
    k.box(hd, C(0, 35.8, 4.2, 4.6, 5.0, 0.6), "gold", tag="mask")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.2, 38.2, 4.5, 1.4, 0.6, 0.4), "eye", tag="eye")
        k.box(hd, C(sx * 1.2, 37.0, 4.5, 0.4, 1.2, 0.4), "dark", tag="tear")
    k.box(hd, C(0, 36.0, 4.5, 2.0, 0.5, 0.4), "dark", tag="mask_mouth")
    k.box(hd, C(0, 40.4, 4.6, 1.2, 1.2, 0.5), "sun", tag="mask_jewel")
    # ---------------------------------------------------------------- arms: wrapped linen, the burning censer
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 8.0
        up = k.part("arm_" + nm, (x, 32, 0), (("x", -60 if side > 0 else -40), ("z", side * 20)), "torso")
        fo = k.part("fore_" + nm, (x, 25, 0), (("x", -20 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 18, 0), (), fo)
        k.limb(up, (x, 31.4, 0), (x, 25.6, 0), 3.6, "indigo", "sleeve")
        k.stack(fo, x, 0, [(19.6, 5.4, 5.4), (25, 4.2, 4.2)], "indigo", "cuff")
        for i in range(3):
            k.shard(fo, (x, 19.6, -1.6 + i * 1.6), (0, -1, 0.1), 3.0 + i, 1.0, mat="indigo", tag="cuff_tatter")
        k.limb(hn, (x, 19, 0.4), (x, 14.6, 0.8), 1.8, "silk", "wrapped_hand")
        for t in (-0.6, 0.6):
            k.limb(hn, (x + t, 14.8, 0.8), (x + t, 12.6, 1.6), 0.6, "silk", "finger")
    k.box(k.parts["hand_l"], C(8.0, 9.8, 2.2, 2.6, 2.6, 2.6), "sun", tag="sand_flame")
    for i in range(5):
        a = i * 1.2
        k.box(k.parts["hand_l"], C(8.0 + math.cos(a) * 2.6, 9.0 + i * 1.0, 2.2 + math.sin(a) * 2.6, 0.7, 0.7, 0.7), "sand", tag="grain")
    cs = k.part("censer", (-8.0, 13, 0.6), (), k.parts["hand_r"], bone=False)
    for z in (-1.2, 1.2):
        k.chain(cs, (-8.0, 13, 0.6), (-8.0, 4.4, 0.6 + z * 1.4), 4, mat="brass", w=0.7)
    k.blob(cs, (-8.0, 2.4, 0.6), (2.8, 2.6, 2.8), "brass", "censer_body", step=0.6)
    k.box(cs, C(-8.0, 2.6, 0.6, 6.0, 1.0, 6.0), "brass", tag="censer_rim")
    for a in range(0, 360, 60):
        r = math.radians(a)
        k.box(cs, C(-8.0 + math.cos(r) * 2.8, 1.6, 0.6 + math.sin(r) * 2.8, 0.8, 1.4, 0.8), "sun", tag="censer_vent")
    k.shard(cs, (-8.0, 4.6, 0.6), (0, 1, 0), 2.4, 2.4, mat="brass", tag="censer_lid")
    for i in range(5):
        k.box(cs, C(-8.0 - i * 0.8, 6.8 + i * 1.4, 0.6 + (i % 2) * 0.8, 1.8 - i * 0.2, 1.4, 1.8 - i * 0.2), "sand", tag="smoke")
    lit(k)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Blade Dancer (elite)

def blade_dancer():
    """The last of the sultan's dancers keeps the court below the dome, and she has not stopped dancing. Crimson silk
    and beaten gold, bells at wrist and ankle, a tall gold crown and a veil of coins over her face with sunfire for
    eyes over it; long sashes stream out behind her when she turns, two scimitars in her hands, and a fan of knives
    stands on her back for when she throws."""
    k = X.Kit("blade_dancer")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(17, 9.6, 6.6), (22, 8.6, 6.0)], "crimson", "pelvis")
    k.box(hips, C(0, 19.4, 0, 10.6, 1.6, 7.4), "gold", tag="girdle")
    for i in range(-4, 5):                        # coins hung from the girdle
        k.box(hips, C(i * 1.3, 18.8 - abs(i) * 0.3, 4.1, 1.0, 1.4, 0.5), "gold", tag="coin")
    skirt = k.part("skirt", (0, 20, 0), (), "hips", bone=False)
    for i in range(10):                           # split panels of silk to the ankle, flaring
        a = math.radians(i * 36 + 18)
        k.limb(skirt, (math.sin(a) * 5.0, 19.6, math.cos(a) * 3.6), (math.sin(a) * 8.4, 2.4, math.cos(a) * 6.4), 0.6, "crimson" if i % 2 else "silk", "skirt_panel", d=3.0)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.8
        th = k.part("thigh_" + nm, (x, 21, 0), (("x", -16), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 11.4, 0), (("x", 22),), th)
        ft = k.part("foot_" + nm, (x, 2.6, 0), (("x", -6),), sh)
        k.stack(th, x, 0, [(11.6, 4.0, 4.4), (20, 5.0, 5.4)], "indigo", "trouser")
        k.stack(sh, x, 0, [(3, 3.6, 3.8), (11.4, 4.2, 4.6)], "indigo", "trouser")
        k.box(sh, C(x, 2.8, 0, 4.4, 1.2, 4.6), "gold", tag="anklet")
        for a in range(0, 360, 90):
            r = math.radians(a)
            k.box(sh, C(x + math.cos(r) * 2.4, 2.4, math.sin(r) * 2.4, 0.9, 0.9, 0.9), "gold", tag="bell")
        k.box(ft, C(x, 0, 1.6, 3.8, 2.0, 6.4), "gold", tag="foot")
        k.shard(ft, (x, 1.2, 4.6), (0, 1, 0.6), 2.2, 1.0, mat="gold", tag="slipper_toe")
    to = k.part("torso", (0, 22, 0), (("x", -2), ("y", 10)), "hips")
    k.stack(to, 0, 0, [(22, 8.0, 5.6), (25.4, 6.6, 5.0), (29, 8.6, 5.8), (33, 10.4, 6.2), (36.4, 8.0, 5.4)], "skin", "body")
    k.stack(to, 0, 0.2, [(29.4, 9.0, 6.2), (33.4, 10.6, 6.5)], "gold", "bodice")
    k.box(to, C(0, 29.0, 0.2, 10.4, 0.8, 7.0), "crimson", tag="bodice_hem")
    k.box(to, C(0, 26.0, 2.8, 1.0, 1.0, 0.4), "sun", tag="navel_jewel")
    k.box(to, C(0, 30.2, 3.5, 3.6, 3.0, 0.5), "crimson", tag="bodice_inset")
    disc(k, to, (0, 31.6, 3.9), 0.9, "z", "sun", "bodice_gem", thick=0.4)
    for sx in (-1, 1):                            # the sashes, streaming out behind as she turns
        pts = [(sx * (5.0 + i * 2.4), 21 - i * 0.9 + math.sin(i * 0.9) * 1.6, -3.4 - i * 2.6) for i in range(10)]
        for i, (p0, p1) in enumerate(zip(pts, pts[1:])):
            k.limb(to, p0, p1, 3.0 - i * 0.18, "crimson" if sx > 0 else "silk", "sash", d=0.4)
    for i, a in enumerate(range(-60, 61, 20)):   # the fan of knives on her back
        r = math.radians(a)
        base = (math.sin(r) * 2.0, 32.0 + math.cos(r) * 1.4, -4.4)
        k.box(to, C(base[0], base[1] - 0.6, base[2], 1.4, 1.2, 1.2), "gold", tag="knife_grip")
        k.shard(to, (base[0], base[1] + 0.4, base[2]), (math.sin(r), math.cos(r), -0.15), 8.0 - abs(a) * 0.03, 1.4, mat="silver", tag="knife")
    hd = k.part("head", (0, 37, 0.4), (), "torso")
    k.box(hd, C(0, 37.0, 0.4, 4.2, 5.4, 4.6), "skin", tag="face")
    k.stack(hd, 0, -1.6, [(33.6, 5.6, 3.0), (42, 6.0, 4.4)], "dark", "hair")
    for i in range(5):                            # a long black braid swung out behind
        k.limb(hd, (0, 40 - i * 2.6, -3.6 - i * 1.6), (i * 0.8, 37.4 - i * 2.6, -5.2 - i * 1.6), 1.6 - i * 0.15, "dark", "braid")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.1, 40.0, 2.95, 1.4, 0.6, 0.3), "eye", tag="eye")
        k.box(hd, C(sx * 1.1, 40.7, 2.95, 1.6, 0.3, 0.3), "dark", tag="kohl")
    for x in (-1.8, -0.9, 0, 0.9, 1.8):           # the veil of coins
        for y in (38.4, 37.2, 36.0):
            k.box(hd, C(x + (0.45 if y == 37.2 else 0), y, 3.1, 0.7, 0.8, 0.3), "gold", tag="veil")
    k.box(hd, C(0, 42.6, 0.4, 5.6, 1.4, 5.6), "gold", tag="crown_band")
    for i, x in enumerate((-2.2, -1.1, 0, 1.1, 2.2)):
        k.shard(hd, (x, 43.8, 1.8 - abs(x) * 0.2), (x * 0.1, 1, 0), 3.4 + (2.6 if i == 2 else 0) - abs(x) * 0.4, 1.0, mat="gold", tag="crown_spike")
    k.box(hd, C(0, 44.4, 3.2, 1.0, 1.0, 0.4), "sun", tag="crown_gem")
    for sx in (-1, 1):
        k.ring(hd, sx * 2.6, 36.0, 0.6, 0.9, 0.3, "gold", "earring", n=8, axis="x")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.6
        up = k.part("arm_" + nm, (x, 34, 0), (("x", -150 if side > 0 else -70), ("z", side * (24 if side > 0 else 30))), "torso")
        fo = k.part("fore_" + nm, (x, 27, 0), (("x", -10 if side > 0 else -20),), up)
        hn = k.part("hand_" + nm, (x, 20, 0), (), fo)
        k.limb(up, (x, 33.6, 0), (x, 27.4, 0), 2.6, "skin", "upper_arm")
        k.box(up, C(x, 30.4, 0, 3.2, 1.0, 3.2), "gold", tag="armlet")
        k.limb(fo, (x, 27, 0), (x, 20.6, 0), 2.4, "skin", "forearm")
        for y in (21.0, 22.2, 23.4):
            k.box(fo, C(x, y, 0, 3.0, 0.7, 3.0), "gold", tag="bangle")
        k.box(fo, C(x + side * 1.6, 21.6, 0, 0.9, 0.9, 0.9), "gold", tag="bell")
        k.box(hn, C(x, 17.8, 0.3, 2.4, 2.6, 2.6), "skin", tag="hand")
        bl = k.part("scimitar_" + nm, (x, 18.4, 0.3), (("x", 20),), hn, bone=False)
        k.limb(bl, (x, 15.4, 0.3), (x, 19.2, 0.3), 1.0, "crimson", "grip")
        k.box(bl, C(x, 19.0, 0.3, 1.2, 0.8, 4.0), "gold", tag="guard")
        k.shard(bl, (x, 15.2, 0.3), (0, -1, 0), 1.4, 1.2, mat="gold", tag="pommel")
        scimitar(k, bl, x, 19.8, 20, 2.6, curve=0.07)
    lit(k)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Djinn Sultan (boss)

def djinn_sultan():
    """The djinn the sultan bound is the one who sits on the roof now, and the sultan is the lamp. A giant of dark
    bronze skin seamed with sunfire rising out of a brass lamp the size of a cart in a twisting tail of fire and smoke;
    a turban as big as a tent with a sun-stone in it and two black horns through it, a beard of fire, gold at his
    throat and arms and ears; the Djinnblade in his right hand, a scimitar as long as a ship's mast, and in his left a
    small sun he will throw."""
    k = X.Kit("djinn_sultan")
    hips = k.part("hips", (0, 30, 0))
    # ---------------------------------------------------------------- the lamp on the ground, the tail of fire out of it
    lc = (0, 0, -6)
    k.stack(hips, lc[0], lc[2], [(0, 14, 12), (2.0, 10, 8), (3.4, 12, 10)], "brass", "lamp_foot")
    for i in range(9):                            # the lamp's belly: a squat oval of brass
        y = 3.4 + i * 1.2
        f = math.sin((i + 0.5) / 9 * math.pi)
        k.box(hips, C(lc[0], y, lc[2], 10 + 22 * f, 1.25, 8 + 16 * f), "brass", tag="lamp_body")
    k.box(hips, C(lc[0], 9.0, lc[2], 33, 1.2, 25), "gold", tag="lamp_band")
    for a in range(0, 360, 30):
        r = math.radians(a)
        k.box(hips, C(lc[0] + math.cos(r) * 16.4, 8.6, lc[2] + math.sin(r) * 12.4, 1.4, 2.0, 1.4), "sun", tag="lamp_jewel")
    k.stack(hips, lc[0], lc[2], [(13.6, 12, 9), (15, 6, 5), (18, 3, 3)], "brass", "lamp_lid")
    k.shard(hips, (lc[0], 18, lc[2]), (0, 1, 0), 4.0, 2.0, mat="gold", tag="lamp_finial")
    for a in range(12):                           # the handle, a loop off the back
        a0, a1 = math.pi * a / 12, math.pi * (a + 1) / 12
        k.limb(hips, (lc[0], 9 + math.sin(a0) * 6, lc[2] - 15 - math.cos(a0) * 5), (lc[0], 9 + math.sin(a1) * 6, lc[2] - 15 - math.cos(a1) * 5), 2.0, "brass", "lamp_handle")
    spout = [(lc[0], 8, lc[2] + 11), (lc[0], 10, lc[2] + 19), (lc[0], 14.6, lc[2] + 25), (lc[0], 17.4, lc[2] + 27)]
    tube(k, hips, spout, lambda t: 3.6 - 1.6 * t, mat="brass", belly=None, step=0.9, tag="spout")
    tail = []
    for i in range(25):                           # out of the spout, twisting up into his waist
        t = i / 24
        r = 3.0 * (1 - t)
        a = t * 3 * math.pi
        tail.append((math.cos(a) * r, 18 + t * 14 + math.sin(t * math.pi) * 3, lc[2] + 27 - t * 25 + math.sin(t * math.pi) * 6 + math.sin(a) * r))
    tube(k, hips, tail, lambda t: 2.6 + 6.0 * t, mat="flame", belly=None, band=3, step=1.2, tag="fire_tail")
    for i in range(10):                           # licks of fire and smoke peeling off the tail
        t = 0.2 + i * 0.07
        p = tail[int(t * 24)]
        a = i * 2.2
        k.shard(hips, p, (math.cos(a), 0.9, math.sin(a)), 5.0 + i * 0.5, 2.0 + i * 0.15, mat="flame" if i % 3 else "smoke", tag="lick")
    k.box(hips, C(0, 27.6, 0, 22, 4.0, 15), "crimson", tag="sash")
    k.box(hips, C(0, 26.6, 0, 22.6, 1.2, 15.6), "gold", tag="sash_rim")
    disc(k, hips, (0, 29.6, 7.8), 2.6, "z", "gold", "sash_boss", thick=0.8)
    disc(k, hips, (0, 29.6, 8.2), 1.4, "z", "sun", "sash_gem", thick=0.4)
    k.limb(hips, (5, 26, 7.0), (8, 16, 9), 3.0, "crimson", "sash_end", d=0.6)
    for side, nm in ((1, "l"), (-1, "r")):       # the legs a biped's bones want, gone into the fire
        x = side * 5.0
        th = k.part("thigh_" + nm, (x, 28, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 18, 0), (), th)
        k.part("foot_" + nm, (x, 8, 0), (), sh)
    for b in k.s.boxes:                           # what it stands on
        if b.tag == "lamp_foot" and b.lo[1] < 1:
            b.tag = "foot"
    # ---------------------------------------------------------------- torso: bare, sunfire in its seams, gold at the throat
    to = k.part("torso", (0, 30, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(30, 22, 14), (36, 26, 15), (44, 34, 17), (52, 38, 17.4), (57, 31, 14.6)], "djinn", "chest", step=1.2)
    k.box(to, C(0, 41.2, 8.4, 18, 0.8, 0.8), "dark", tag="pec_line")
    for y in (33, 36.4):
        k.box(to, C(0, y, 7.6, 9.6, 0.6, 0.8), "dark", tag="ab_line")
    for row in range(3):                          # a collar of gold plates and sunstones
        for a in range(-80, 81, 16):
            r = math.radians(a)
            R = 9.4 + row * 2.4
            k.box(to, C(math.sin(r) * R, 54.6 - row * 2.2 - (1 - math.cos(r)) * 2.6, 8.2 + math.cos(r) * 0.6, 2.4, 2.4, 1.0),
                  "sun" if (row == 1 and a % 32 == 0) else "gold", tag="collar")
    for sx in (-1, 1):
        k.blob(to, (sx * 17.6, 54.6, 0), (6.4, 4.6, 7.0), "gold", "pauldron", step=1.0)
        k.box(to, C(sx * 18.4, 50.6, 0, 7.6, 1.6, 12.4), "crimson", tag="pauldron_silk")
        for i in range(4):
            k.shard(to, (sx * (16 + i * 1.6), 58.6, -2.6 + i * 1.6), (sx * 0.3, 1, 0), 3.0, 1.4, mat="gold", tag="pauldron_spike")
    # ---------------------------------------------------------------- head: the turban and its horns, the beard of fire
    hd = k.part("head", (0, 56, 2), (("x", -4),), "torso")
    k.blob(hd, (0, 62.4, 1.8), (6.0, 7.0, 6.2), "djinn", "skull", step=0.9)
    k.box(hd, C(0, 56.4, 3.0, 9.6, 4.4, 8.4), "djinn", tag="jaw")
    k.limb(hd, (-5.6, 65.4, 7.4), (5.6, 65.4, 7.4), 2.2, "djinn", "brow", d=2.6)
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.6, 62.8, 7.6, 3.2, 2.0, 0.6), "dark", tag="socket")
        k.box(hd, C(sx * 2.6, 63.2, 8.0, 2.4, 1.0, 0.5), "eye", tag="eye")
        k.shard(hd, (sx * 5.8, 62, 1.6), (sx, 0.5, -0.4), 4.0, 2.2, mat="djinn", tag="ear")
        k.ring(hd, sx * 6.6, 57.4, 1.6, 1.8, 0.6, "gold", "earring", n=10, axis="x")
    k.box(hd, C(0, 59.6, 7.8, 3.2, 4.4, 2.6), "djinn", tag="nose")
    k.box(hd, C(0, 57.4, 7.4, 5.0, 1.0, 0.8), "mouth", tag="mouth")
    for i in range(7):                            # the beard of fire: tongues curling down and forward
        x = -3.6 + i * 1.2
        L = 9.0 + (3 - abs(i - 3)) * 2.4
        k.shard(hd, (x, 56.0, 6.6), (x * 0.06, -1, 0.35), L, 2.2, mat="flame", tag="fire_beard")
    turban(k, hd, (0, 64.4, 1.4), 7.6, 10.0, mat="silk", band="crimson")
    k.limb(hd, (-3.0, 75.4, 1.4), (3.0, 75.4, 1.4), 1.0, "gold", "turban_chain")
    for sx in (-1, 1):                            # black horns curving out through the turban and up
        pts = [(sx * 6.6, 70, 0), (sx * 11, 73, -1), (sx * 13.6, 78, -1.6), (sx * 13.0, 84, -0.6)]
        for (p0, p1), w in zip(zip(pts, pts[1:]), (3.0, 2.4, 1.8)):
            k.limb(hd, p0, p1, w, "dark", "horn")
        k.shard(hd, pts[-1], (sx * -0.2, 1, 0.2), 4.0, 1.4, mat="dark", tag="horn_tip")
    for i in range(5):                            # a plume of fire off the turban's jewel
        k.shard(hd, (0, 70, 9.0), (math.sin(i - 2) * 0.3, 1, -0.4 - i * 0.1), 8.0 - abs(i - 2) * 1.4, 2.0, mat="flame", tag="plume")
    # ---------------------------------------------------------------- arms: the Djinnblade, the sun in his palm
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 21.0
        up = k.part("arm_" + nm, (x, 53, 0), (("x", -70 if side > 0 else -24), ("z", side * (34 if side > 0 else 12))), "torso")
        fo = k.part("fore_" + nm, (x, 38, 0), (("x", -40 if side > 0 else -60),), up)
        hn = k.part("hand_" + nm, (x, 24, 0), (), fo)
        k.limb(up, (x, 51, 0), (x, 39, 0), 7.6, "djinn", "upper_arm")
        k.box(up, C(x, 44, 0, 8.4, 2.4, 8.4), "gold", tag="armlet")
        disc(k, up, (x, 45.2, 4.4), 1.4, "z", "sun", "armlet_gem", thick=0.6)
        k.limb(fo, (x, 37.6, 0), (x, 25.4, 0), 7.0, "djinn", "forearm")
        for y in (26.6, 28.6, 30.6):
            k.box(fo, C(x, y, 0, 8.0, 1.0, 8.0), "gold", tag="bangle")
        k.box(hn, C(x, 19.4, 0.6, 6.4, 5.6, 6.8), "djinn", tag="hand")
    k.blob(k.parts["hand_l"], (21.0, 13.6, 3.0), (4.6, 4.6, 4.6), "sun", "sun_orb", step=0.9)
    for a in range(0, 360, 45):
        r = math.radians(a)
        k.shard(k.parts["hand_l"], (21.0 + math.cos(r) * 4.2, 13.6 + math.sin(r) * 4.2, 3.0), (math.cos(r), math.sin(r), 0), 3.4, 1.6, mat="flame", tag="sun_ray")
    bl = k.part("djinnblade", (-21, 21.6, 0.6), (("x", 64),), k.parts["hand_r"], bone=False)
    k.limb(bl, (-21, 12, 0.6), (-21, 24, 0.6), 2.4, "crimson", "grip")
    k.shard(bl, (-21, 12, 0.6), (0, -1, 0), 4.0, 3.0, mat="gold", tag="pommel")
    k.box(bl, C(-21, 23.6, 0.6, 3.0, 2.4, 12.0), "gold", tag="guard")
    for sz in (-1, 1):
        k.shard(bl, (-21, 24.6, 0.6 + sz * 6.0), (0, 0.6, sz), 4.0, 1.8, mat="gold", tag="quillon")
    disc(k, bl, (-21, 24.8, 0.6), 1.6, "x", "sun", "guard_gem", thick=3.2)
    scimitar(k, bl, -21, 26.0, 60, 8.4, curve=0.02, edge="flame", tag="djinnblade")
    lit(k)
    grow(k, 1.5)
    k.s.shaders = shaders()
    return k.s, k.parts


MOBS = {
    "dune_scorpion": dict(make=dune_scorpion, rig="crawler", ent=(1.2, 1.1), stats=dict(hp=30, speed=0.36, dmg=8, armor=6, kb=0)),
    "glass_golem": dict(make=glass_golem, ent=(2.0, 4.0), stats=dict(hp=210, speed=0.19, dmg=22, armor=16, kb=1.0)),
    "mirror_guard": dict(make=mirror_guard, ent=(1.2, 3.4), stats=dict(hp=100, speed=0.24, dmg=14, armor=14, kb=0.6)),
    "sandwraith": dict(make=sandwraith, ent=(1.0, 3.0), stats=dict(hp=54, speed=0.25, dmg=9, armor=2, kb=0)),
    "blade_dancer": dict(make=blade_dancer, ent=(1.0, 3.0), stats=dict(hp=330, speed=0.36, dmg=17, armor=8, kb=0.4), key=True),
    "djinn_sultan": dict(make=djinn_sultan, texel=1, ent=(3.8, 9.4), stats=dict(hp=1300, speed=0.21, dmg=30, armor=14, kb=1.0), boss=True),
}
