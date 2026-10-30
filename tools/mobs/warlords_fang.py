"""The Warlord's Fang's monsters, the Fanghorde, each built by hand (tools/vox2.py). Gorrak took the crag with a
horde of orcs and goblins and built his crooked tower on it out of everything he burned: his brutes and raiders hold
its floors, the goblins swarm its stairs, his shamans keep the bonefires and his warg riders run its ramps. Olive and
yellow-green hides, rusted scrap iron, raw leather and furs, red war paint and red rags, bone everywhere, and the
orange of the bonefires in their eyes.

    goblin_cutthroat  swarm   a hunched goblin in a ragged black hood, ears like knives, a grin of needle teeth, two
                              rusty shanks
    orc_brute         brute   a hulking bare-chested orc, red hand-paint over his scars, tusks with rings in them, a
                              spiked pauldron of scrap and a club studded with nails as big as he is
    orc_raider        guard   an orc in scrap plate and a bull-horned helm, the skull of some great beast for a shield,
                              a cleaver as long as his arm
    goblin_shaman     caster  a goblin under a horned beast-skull headdress hung with feathers and bones, glowing
                              paint, a bonefire staff of skulls
    warg_rider        elite   a black warg as big as a horse, mangy and spiked, with a goblin rider in a skull saddle
                              and a barbed spear, trophies flying off the saddle-pole
    gorrak            boss    the warlord: a giant orc in black spiked scrap plate, a war crown of spikes and skulls,
                              gold rings in his tusks, two trophy banners on his back and a cleaver like a door

    python tools/monsterforge.py warlords_fang --preview ; python tools/mobsheet.py warlords_fang
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import tube, disc, _along, grow

ORC = ramp("#0e160a", "#182410", "#223218", "#2e4220", "#3a5228", "#4a6432")
GOB = ramp("#1a1e0a", "#2a3010", "#3c4418", "#525c20", "#6a742a", "#848e36")
RUST = ramp("#100a08", "#1e120c", "#2e1a12", "#402418", "#542e1c", "#6c3c22", "#88502c")
IRON = ramp("#0a0a0c", "#141418", "#1e1e24", "#2a2a32", "#383842", "#4a4a56")
HIDE = ramp("#1e140c", "#2e1e12", "#40281a", "#543622", "#6a462c", "#845a38")
FUR = ramp("#100c0a", "#1a1410", "#261e18", "#342a20", "#44362a")
RAG = ramp("#1e0404", "#340806", "#4e0c08", "#6a120c", "#881c12")
BLACK = ramp("#08080a", "#0e0e12", "#16161a", "#1e1e24", "#28282e")
BONE = ramp("#3a3428", "#5c5444", "#827a64", "#a8a088", "#cec6ac", "#ece6d0")
WOOD = ramp("#140c08", "#21140c", "#301e12", "#422a18", "#56381e")
GOLD = ramp("#2a1804", "#4c300a", "#7a5014", "#a87422", "#d0a034", "#f0cc5a")
FIRE = ramp("#4a0e04", "#8a1e06", "#c83a0a", "#ff6a1a", "#ffa040", "#ffe0a0")
PAINT = ramp("#3a0604", "#5a0a06", "#7e1208", "#a01c0c", "#c02a12")
GORE = ramp("#100406", "#1e080a", "#2e0e10", "#401416")


def shaders():
    return {
        "orc": X.wrinkled(ORC, 0.8),
        "gob": X.wrinkled(GOB, 1.0),
        "rust": X.surf(RUST, 0.5, 1.4, 0.2, 0.2, rust=(PAINT, 0.1, 0.5)),
        "iron": X.surf(IRON, 0.5, 1.4, 0.16, 0.22, rust=(RUST, 0.22, 0.6)),
        "hide": X.surf(HIDE, 0.5, 1.1, 0.22, 0.06, stripe=5),
        "fur": X.surf(FUR, 0.5, 1.1, 0.26, 0.02, pattern=lambda p, n, i, j, w, h: -0.16 if i % 3 == 0 else 0.04),
        "rag": X.surf(RAG, 0.5, 1.0, 0.22, 0.0, holes=True),
        "black": X.surf(BLACK, 0.5, 1.0, 0.18, 0.0, holes=True),
        "bone": X.surf(BONE, 0.54, 1.2, 0.16, 0.12),
        "wood": X.surf(WOOD, 0.5, 1.1, 0.2, 0.08, stripe=4),
        "gold": X.surf(GOLD, 0.5, 1.5, 0.12, 0.22),
        "paint": X.surf(PAINT, 0.55, 1.0, 0.1, 0.0),
        "fire": X.glow(FIRE),
        "eye": X.glow(FIRE, 0.86, 0.12),
        "mouth": X.dark(GORE),
        "dark": X.dark(BLACK),
    }


GLOWS = {"fire", "eye"}


def lit(k):
    for b in k.s.boxes:
        if b.mat in GLOWS:
            b.group = "glow"


# ================================================================ shared brushes

def tusks(k, part, x, y, z, L, w=1.0, ring=False):
    for sx in (-1, 1):
        k.shard(part, (x + sx * 1.6 * w, y, z), (sx * 0.25, 1, 0.3), L, 1.1 * w, mat="bone", tag="tusk")
        if ring:
            k.box(part, C(x + sx * (1.6 * w + 0.4), y + L * 0.3, z + L * 0.12, 1.6 * w, 0.8, 1.6 * w), "gold", tag="tusk_ring")


def orc_face(k, part, c, s=1.0, mat="orc", tusk=3.0, ring=False):
    """a heavy orc's face facing +z: a jutting jaw, a brow like a shelf over small burning eyes, a flat nose, tusks"""
    cx, cy, cz = c
    k.box(part, C(cx, cy, cz, 6.4 * s, 7.0 * s, 6.0 * s), mat, tag="head")
    k.box(part, C(cx, cy - 1.0 * s, cz + 1.4 * s, 7.0 * s, 3.0 * s, 5.4 * s), mat, tag="jaw")
    k.box(part, C(cx, cy + 4.4 * s, cz + 2.6 * s, 7.0 * s, 1.4 * s, 1.6 * s), mat, tag="brow")
    for sx in (-1, 1):
        k.box(part, C(cx + sx * 1.6 * s, cy + 3.4 * s, cz + 3.0 * s, 1.6 * s, 0.9 * s, 0.3), "dark", tag="socket")
        k.box(part, C(cx + sx * 1.6 * s, cy + 3.5 * s, cz + 3.1 * s, 1.0 * s, 0.6 * s, 0.3), "eye", tag="eye")
        k.shard(part, (cx + sx * 3.2 * s, cy + 3.4 * s, cz), (sx, 0.5, -0.5), 3.0 * s, 1.4 * s, mat=mat, tag="ear")
    k.box(part, C(cx, cy + 2.2 * s, cz + 3.0 * s, 2.2 * s, 1.6 * s, 1.2 * s), mat, tag="nose")
    k.box(part, C(cx, cy + 0.6 * s, cz + 4.1 * s, 4.2 * s, 0.8 * s, 0.4), "mouth", tag="mouth")
    tusks(k, part, cx, cy + 0.2 * s, cz + 4.0 * s, tusk * s, w=s, ring=ring)


def spiked(k, part, at, d, n, L, w, mat="iron", spread=0.5, seed=1):
    k.cluster(part, at, n, L, w, mat=mat, seed=seed, spread=spread, up=d)


def nails(k, part, x, y0, y1, z, r, n=8, seed=0):
    """nails driven through a club's head, sticking out all round"""
    for i in range(n):
        a = i * 2.399 + seed
        y = y0 + (y1 - y0) * ((i * 0.618) % 1)
        k.shard(part, (x + math.cos(a) * r, y, z + math.sin(a) * r), (math.cos(a), 0.1, math.sin(a)), 2.6, 0.7, mat="iron", tag="nail")


def skull(k, part, c, s=1.0, mat="bone", eyes="dark"):
    """a small skull facing +z, for hanging on things"""
    cx, cy, cz = c
    k.box(part, C(cx, cy, cz, 2.4 * s, 2.4 * s, 2.4 * s), mat, tag="skull")
    k.box(part, C(cx, cy - 0.8 * s, cz + 0.4 * s, 1.8 * s, 0.9 * s, 1.8 * s), mat, tag="skull_jaw")
    for sx in (-1, 1):
        k.box(part, C(cx + sx * 0.55 * s, cy + 0.9 * s, cz + 1.05 * s, 0.7 * s, 0.7 * s, 0.4), eyes, tag="skull_eye")


def banner(k, part, base, h, cloth="rag", skulls=2, side=1, s=1.0):
    """a pole with a ragged flag, skulls lashed to it"""
    bx, by, bz = base
    k.limb(part, (bx, by, bz), (bx, by + h, bz), 1.4 * s, "wood", "pole")
    k.limb(part, (bx - 2.6 * s, by + h - 1.0, bz), (bx + 2.6 * s, by + h - 1.0, bz), 1.0 * s, "wood", "crossbar")
    for i in range(3):                            # a ragged flag hung from the crossbar, torn at its foot
        k.box(part, C(bx + (-2.4 + i * 1.6) * s, by + h - (9.0 + (i % 2) * 1.4) * s, bz - 0.2, 1.6 * s, (8.0 + (i % 2) * 1.4) * s, 0.4), cloth, tag="flag")
    k.box(part, C(bx, by + h - 6.0 * s, bz + 0.1, 2.2 * s, 2.0 * s, 0.4), "paint", tag="flag_mark")
    for i in range(skulls):
        skull(k, part, (bx, by + h - (13 + i * 4.0) * s, bz + 0.6 * s), 0.9 * s)
    k.shard(part, (bx, by + h, bz), (0, 1, 0), 2.6 * s, 1.0 * s, mat="iron", tag="pole_spike")


# ================================================================ the Goblin Cutthroat (swarm)

def goblin_cutthroat():
    """The Fang's stairs crawl with them. A goblin as high as a man's chest, hunched in a ragged black hood with its
    ears poking through, a long hooked nose and a grin of needle teeth under eyes that burn like coals; scraps of hide
    and a belt of stolen things, bound feet, and a rusty shank in each hand. They come in fast and low, a dozen at once."""
    k = X.Kit("goblin_cutthroat")
    hips = k.part("hips", (0, 14, 0))
    k.stack(hips, 0, 0, [(10, 7.4, 5.6), (14, 7.8, 5.6)], "hide", "loin")
    k.box(hips, C(0, 13.0, 0, 8.4, 1.2, 6.2), "hide", tag="belt")
    for x, m in ((-3.2, "bone"), (2.8, "gold"), (3.8, "rust")):     # the belt of stolen things
        k.box(hips, C(x, 11.2, 3.2, 1.0, 1.8, 0.8), m, tag="trinket")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.2
        th = k.part("thigh_" + nm, (x, 13, 0), (("x", -24), ("z", side * 10)), "hips")
        sh = k.part("shin_" + nm, (x, 7.4, 0), (("x", 34),), th)
        ft = k.part("foot_" + nm, (x, 2.0, 0), (("x", -10),), sh)
        k.limb(th, (x, 12.6, 0), (x, 7.8, 0), 2.4, "gob", "thigh")
        k.limb(sh, (x, 7.4, 0), (x, 2.2, 0), 2.0, "gob", "shin")
        for y in (3.0, 4.6):
            k.box(sh, C(x, y, 0, 2.4, 0.7, 2.4), "hide", tag="wrap")
        k.box(ft, C(x, 0, 1.0, 2.6, 1.8, 4.4), "gob", tag="foot")
        for t in (-0.7, 0.7):
            k.shard(ft, (x + t, 0.6, 3.0), (0, -0.3, 1), 1.2, 0.5, mat="bone", tag="toe")
    to = k.part("torso", (0, 14, 0), (("x", 30),), "hips")
    k.stack(to, 0, 0, [(14, 7.6, 5.4), (19, 8.4, 5.6), (23, 9.6, 6.0)], "gob", "chest")
    k.stack(to, 0, -0.4, [(15, 10.6, 7.0), (23.6, 11.4, 7.4)], "black", "cloak")
    for i in range(-3, 4):                        # the cloak's ragged hem
        k.shard(to, (i * 1.5, 15.4, -3.6), (0, -1, -0.2), 2.6 + (i % 2) * 1.6, 1.4, mat="black", tag="hem")
    for i in range(5):                            # a string of teeth across its chest
        a = math.radians(-50 + i * 25)
        k.box(to, C(math.sin(a) * 3.2, 20.4 - math.cos(a) * 1.0, 3.2, 0.6, 1.0, 0.5), "bone", tag="teeth")
    hd = k.part("head", (0, 23, 1.2), (("x", -26),), "torso")
    k.box(hd, C(0, 22.6, 1.4, 5.4, 4.8, 5.0), "gob", tag="head")
    k.stack(hd, 0, 0.2, [(21.6, 7.0, 6.8), (25.4, 7.2, 7.0), (27.0, 5.6, 5.8)], "black", "hood")
    k.limb(hd, (0, 26.6, -0.6), (0, 24.4, -6.0), 3.0, "black", "hood_tip")
    k.shard(hd, (0, 24.4, -6.0), (0, -0.6, -1), 3.0, 2.0, mat="black", tag="hood_tip")
    k.box(hd, C(0, 23.0, 3.6, 4.4, 4.0, 0.8), "dark", tag="hood_dark")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.2, 25.0, 3.95, 1.2, 0.7, 0.3), "eye", tag="eye")
        k.limb(hd, (sx * 3.0, 25.2, 0.6), (sx * 8.6, 27.0, -1.0), 1.6, "gob", "ear", d=0.6)
        k.shard(hd, (sx * 8.6, 27.0, -1.0), (sx, 0.3, -0.3), 2.0, 1.0, mat="gob", tag="ear_tip")
    k.limb(hd, (0, 24.2, 4.0), (0, 22.2, 7.2), 1.2, "gob", "nose")
    k.box(hd, C(0, 22.0, 4.0, 3.8, 1.0, 0.4), "mouth", tag="grin")
    for x in (-1.4, -0.7, 0, 0.7, 1.4):
        k.shard(hd, (x, 23.0, 4.2), (0, -1, 0.1), 0.9, 0.35, mat="bone", tag="needle_tooth")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.4
        up = k.part("arm_" + nm, (x, 21.6, 0), (("x", -40), ("z", side * 18)), "torso")
        fo = k.part("fore_" + nm, (x, 16.6, 0), (("x", -50),), up)
        hn = k.part("hand_" + nm, (x, 11.6, 0), (), fo)
        k.limb(up, (x, 21.2, 0), (x, 17, 0), 2.0, "gob", "upper_arm")
        k.limb(fo, (x, 16.6, 0), (x, 12.2, 0), 1.8, "gob", "forearm")
        k.box(fo, C(x, 12.6, 0, 2.2, 1.8, 2.2), "hide", tag="bracer")
        k.box(hn, C(x, 10.0, 0.3, 2.0, 2.0, 2.2), "gob", tag="hand")
        sk = k.part("shank_" + nm, (x, 10.6, 0.4), (("x", 70),), hn, bone=False)
        k.limb(sk, (x, 8.6, 0.4), (x, 11.6, 0.4), 0.9, "hide", "grip")
        for i in range(5):                        # a hooked rusty blade
            k.box(sk, C(x, 11.6 + i * 1.3, 0.4 + 0.08 * i * i, 0.5, 1.35, 1.6 - i * 0.18), "rust", tag="shank")
        k.shard(sk, (x, 18.0, 2.4), (0, 0.6, 1), 1.6, 0.6, mat="rust", tag="hook")
    lit(k)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Orc Brute (brute)

def orc_brute():
    """The horde's front rank: an orc a head taller than a door and twice as wide, bare to the waist so the scars
    show, a red hand painted over his heart, a topknot, tusks with iron rings through them, one shoulder under a
    spiked pauldron of scrap; he carries a club studded with nails as long as he is tall and does not need it."""
    k = X.Kit("orc_brute")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(14, 15, 11), (22, 16, 11.6)], "hide", "breeches")
    k.box(hips, C(0, 20.6, 0, 17, 2.2, 12.4), "hide", tag="belt")
    k.box(hips, C(0, 20.2, 6.2, 3.6, 3.0, 0.8), "iron", tag="buckle")
    k.stack(hips, 0, 5.8, [(8, 6.0, 1.0), (20, 7.0, 1.0)], "rag", "loin_flap")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 4.8
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -8), ("z", side * 8)), "hips")
        sh = k.part("shin_" + nm, (x, 11, 0), (("x", 12),), th)
        ft = k.part("foot_" + nm, (x, 3.0, 0), (("x", -4),), sh)
        k.stack(th, x, 0, [(11, 7.6, 8.0), (20, 9.0, 9.4)], "hide", "thigh")
        k.stack(sh, x, 0, [(3, 7.0, 7.4), (11, 7.6, 8.0)], "fur", "boot")
        for y in (5, 8):
            k.box(sh, C(x, y, 0, 8.0, 0.8, 8.4), "hide", tag="boot_strap")
        k.box(ft, C(x, 0, 1.8, 8.0, 3.0, 11), "hide", tag="foot")
    to = k.part("torso", (0, 22, 0), (("x", 14),), "hips")
    k.stack(to, 0, 0, [(22, 16, 11.6), (27, 19, 12.4), (33, 25, 13.4), (38, 27, 13.0), (41.4, 21, 11)], "orc", "chest", step=1.2)
    k.box(to, C(0, 34.8, 6.6, 15, 0.8, 0.8), "dark", tag="pec_line")
    for y in (27, 30):
        k.box(to, C(0, y, 6.0, 7.6, 0.6, 0.8), "dark", tag="ab_line")
    for (p0, p1) in (((-6, 37, 6.8), (2, 29, 6.6)), ((5, 31, 6.4), (9, 25, 6.0))):
        k.limb(to, p0, p1, 0.6, "bone", "scar")
    k.box(to, C(-4.4, 34.6, 6.8, 3.4, 3.6, 0.4), "paint", tag="hand_paint")
    for f in range(4):
        k.box(to, C(-5.6 + f * 0.8, 38.2, 6.75, 0.6, 1.8, 0.4), "paint", tag="hand_paint")
    k.limb(to, (10, 40, 5.4), (-8, 23, 6.4), 2.0, "hide", "strap", d=0.8)
    # one shoulder in scrap: a spiked pauldron, a chain over it
    k.blob(to, (-13.6, 40, 0), (6.4, 4.4, 7.0), "rust", "pauldron", step=1.0)
    for i in range(2):
        k.box(to, C(-14.4 - i * 0.4, 36.2 - i * 2.0, 0, 8.0, 1.8, 11.6), "iron", tag="lame")
    for z in (-3.6, 0, 3.6):
        k.shard(to, (-15.6, 43.4, z), (-0.5, 1, 0), 5.0, 1.8, mat="iron", tag="pauldron_spike")
    k.chain(to, (-12, 41, 6.4), (8, 28, 7.0), 7, mat="iron", w=1.2)
    k.blob(to, (13.6, 39.6, 0), (6.0, 4.2, 6.4), "orc", "shoulder", step=1.0)
    hd = k.part("head", (0, 41, 3), (("x", -14),), "torso")
    orc_face(k, hd, (0, 41.4, 3.2), 1.15, tusk=4.0)
    for t in (-1, 1):                             # rings through the tusks
        k.box(hd, C(t * 2.2, 42.6, 8.6, 1.6, 0.8, 1.6), "iron", tag="tusk_ring")
    k.stack(hd, 0, 1.6, [(49.2, 3.6, 3.6), (52, 2.6, 2.6)], "dark", "topknot")
    k.limb(hd, (0, 52, 1.6), (0, 47, -4.4), 2.0, "dark", "topknot_tail")
    k.box(hd, C(0, 50.4, 1.6, 4.0, 0.8, 4.0), "bone", tag="topknot_ring")
    k.box(hd, C(1.6, 46.0, 6.8, 0.6, 3.6, 0.4), "paint", tag="face_paint")
    k.box(hd, C(-1.6, 46.0, 6.8, 0.6, 3.6, 0.4), "paint", tag="face_paint")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 15.0
        up = k.part("arm_" + nm, (x, 38, 0), (("x", -20 if side > 0 else -40), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 26, 0), (("x", -30 if side > 0 else -60),), up)
        hn = k.part("hand_" + nm, (x, 15, 0), (), fo)
        k.limb(up, (x, 37, 0), (x, 26.6, 0), 6.6, "orc", "upper_arm")
        k.box(up, C(x, 31, 0, 7.2, 1.4, 7.2), "iron", tag="arm_ring")
        k.stack(fo, x, 0, [(16, 6.6, 6.8), (22, 7.8, 8.0), (26, 6.8, 7.0)], "orc", "forearm")
        k.box(fo, C(x, 16.4, 0, 7.6, 3.6, 7.8), "hide", tag="wrist_wrap")
        k.box(hn, C(x, 10.6, 0.6, 6.6, 5.6, 7.0), "orc", tag="fist")
        for t in (-2.2, -0.7, 0.7, 2.2):
            k.box(hn, C(x + t, 10.6, 4.2, 1.4, 1.6, 0.8), "iron", tag="knuckle_stud")
    cl = k.part("club", (-15.0, 12.6, 0.6), (("x", 70),), k.parts["hand_r"], bone=False)
    k.limb(cl, (-15.0, 4, 0.6), (-15.0, 22, 0.6), 2.6, "wood", "handle")
    k.stack(cl, -15.0, 0.6, [(20, 4.6, 4.6), (36, 7.6, 7.6), (44, 8.0, 8.0), (46, 6.0, 6.0)], "wood", "club_head")
    for y in (24, 34):
        k.box(cl, C(-15.0, y, 0.6, 6.0 + (y - 24) * 0.18, 1.2, 6.0 + (y - 24) * 0.18), "rust", tag="band")
    nails(k, cl, -15.0, 26, 44, 0.6, 3.8, n=14, seed=1)
    skull(k, cl, (-15.0, 47.6, 0.6), 1.2)
    lit(k)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Orc Raider (guard)

def orc_raider():
    """Gorrak's raiders hold the Fang's doors: orcs in plate beaten out of everything they took, a bull-horned helm
    with a grille across the face and the eyes burning behind it, red rags knotted at every joint, a cleaver as long
    as a man's arm and, for a shield, the skull of some great horned beast with a grip lashed inside it."""
    k = X.Kit("orc_raider")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(12, 13.4, 9.6), (22, 13.0, 9.0)], "hide", "skirt")
    for x in (-4.4, 0, 4.4):
        k.box(hips, C(x, 11.6, 4.8, 4.0, 9.0, 1.0), "rust", tag="tasset")
    k.box(hips, C(0, 20.6, 0, 14.4, 2.0, 10.2), "hide", tag="belt")
    k.box(hips, C(-6.4, 16, 4.0, 2.0, 5.0, 0.6), "rag", tag="rag")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.8
        th = k.part("thigh_" + nm, (x, 21, 0), (("x", -4), ("z", side * 4)), "hips")
        sh = k.part("shin_" + nm, (x, 11.4, 0), (("x", 6),), th)
        ft = k.part("foot_" + nm, (x, 2.8, 0), (("x", -2),), sh)
        k.stack(th, x, 0, [(11.6, 6.0, 6.4), (20, 7.0, 7.4)], "hide", "thigh")
        k.box(th, C(x, 10.6, 1.6, 5.6, 2.8, 5.4), "iron", tag="knee")
        k.shard(th, (x, 12.0, 4.4), (0, 0.3, 1), 2.4, 1.2, mat="iron", tag="knee_spike")
        k.stack(sh, x, 0, [(3, 5.4, 5.8), (11.4, 6.0, 6.4)], "rust", "greave")
        k.box(ft, C(x, 0, 1.6, 6.0, 2.8, 8.6), "iron", tag="foot")
    to = k.part("torso", (0, 22, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(22, 13.0, 9.0), (27, 15.4, 9.6), (32, 19.6, 10.6), (37, 21.6, 10.8), (39.6, 17, 9.2)], "rust", "cuirass")
    for y in (25, 29, 33):                        # the plates riveted over each other, badly
        k.box(to, C((y % 3) * 0.6 - 0.6, y, 5.0 + (y - 25) * 0.08, 12.0 + (y - 25) * 0.6, 1.0, 1.0), "iron", tag="plate_edge")
        for x in (-5, 0, 5):
            k.box(to, C(x, y + 0.2, 5.7 + (y - 25) * 0.08, 0.7, 0.7, 0.6), "iron", tag="rivet")
    k.box(to, C(0, 34.0, 5.9, 4.0, 4.0, 0.5), "paint", tag="skull_mark")
    for sx in (-1, 1):
        k.blob(to, (sx * 11.0, 37.6, 0), (5.4, 3.4, 5.8), "iron", "pauldron", step=0.9)
        for i in range(3):
            k.shard(to, (sx * (10 + i * 1.6), 40.4, -2.0 + i * 2.0), (sx * 0.5, 1, 0), 3.4, 1.4, mat="iron", tag="pauldron_spike")
        k.box(to, C(sx * 11.6, 33.6, 0, 6.6, 1.6, 10.4), "rust", tag="lame")
        k.box(to, C(sx * 12.8, 31.0, 2.0, 1.4, 4.4, 1.0), "rag", tag="rag")
    hd = k.part("head", (0, 40, 1), (("x", -6),), "torso")
    orc_face(k, hd, (0, 40.4, 1.2), 1.0, tusk=3.0)
    k.blob(hd, (0, 45.6, 1.0), (4.4, 3.4, 4.6), "iron", "helm", step=0.7)
    k.box(hd, C(0, 43.0, 1.0, 9.0, 1.4, 9.4), "rust", tag="helm_rim")
    for x in (-2.4, -0.8, 0.8, 2.4):              # a grille across the face
        k.box(hd, C(x, 40.4, 5.6, 0.6, 3.6, 0.6), "iron", tag="grille")
    k.box(hd, C(0, 40.4, 5.6, 6.4, 0.6, 0.6), "iron", tag="grille")
    for sx in (-1, 1):                            # bull horns, out and up
        pts = [(sx * 4.0, 46.0, 0.4), (sx * 8.4, 47.0, 1.6), (sx * 11.0, 50.0, 2.4), (sx * 11.4, 54.0, 1.6)]
        for (p0, p1), w in zip(zip(pts, pts[1:]), (2.4, 1.9, 1.4)):
            k.limb(hd, p0, p1, w, "bone", "horn")
        k.shard(hd, pts[-1], (0, 1, -0.2), 2.4, 1.1, mat="bone", tag="horn_tip")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 11.0
        up = k.part("arm_" + nm, (x, 36, 0), (("x", -34 if side > 0 else -24), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 27, 0), (("x", -56 if side > 0 else -72),), up)
        hn = k.part("hand_" + nm, (x, 18, 0), (), fo)
        k.limb(up, (x, 35, 0), (x, 27.6, 0), 4.8, "orc", "upper_arm")
        k.limb(fo, (x, 26.6, 0), (x, 19.4, 0), 4.4, "orc", "forearm")
        k.box(fo, C(x, 19.6, 0, 5.2, 5.4, 5.2), "rust", tag="vambrace")
        k.box(hn, C(x, 15.4, 0.4, 4.4, 3.8, 4.6), "hide", tag="glove")
    sh = k.part("shield", (14.6, 17, 2), (("y", 10),), k.parts["hand_l"], bone=False)
    # the beast skull: a broad brow plate facing out, sockets, a snout, horns sweeping forward off it
    sx0 = 16.0
    for i, (w, h) in enumerate(((16.0, 3.0), (17.0, 3.0), (15.4, 3.0), (12.0, 3.0), (9.0, 3.0), (7.0, 3.0))):
        k.box(sh, C(sx0, 26.0 - i * 3.0, 2.0, 2.4, h + 0.05, w), "bone", tag="skull_shield")
    for z in (-3.4, 3.4):
        k.box(sh, C(sx0 + 1.0, 20.6, 2.0 + z, 0.6, 3.6, 3.4), "dark", tag="socket")
        k.box(sh, C(sx0 + 1.1, 21.6, 2.0 + z, 0.4, 1.2, 1.4), "eye", tag="socket_ember")
    for z in (-1.0, 1.0):
        k.box(sh, C(sx0 + 1.0, 11.6, 2.0 + z, 0.6, 1.6, 0.8), "dark", tag="nostril")
    for sz in (-1, 1):
        pts = [(sx0, 27.0, 2.0 + sz * 7.0), (sx0 + 3.0, 29.0, 2.0 + sz * 11.0), (sx0 + 6.0, 27.0, 2.0 + sz * 13.0), (sx0 + 8.0, 23.0, 2.0 + sz * 12.0)]
        for (p0, p1), w in zip(zip(pts, pts[1:]), (3.0, 2.4, 1.8)):
            k.limb(sh, p0, p1, w, "bone", "shield_horn")
        k.shard(sh, pts[-1], (0.4, -1, -sz * 0.2), 2.6, 1.4, mat="bone", tag="shield_horn")
    k.box(sh, C(sx0 + 0.9, 16.6, 2.0, 0.4, 5.0, 0.6), "paint", tag="war_stripe")
    cv = k.part("cleaver", (-11.0, 15.6, 0.6), (("x", 82),), k.parts["hand_r"], bone=False)
    k.limb(cv, (-11.0, 10, 0.6), (-11.0, 20, 0.6), 1.6, "hide", "grip")
    k.box(cv, C(-11.0, 20, 0.6, 2.4, 1.4, 3.2), "iron", tag="guard")
    k.box(cv, C(-11.0, 21.4, 2.4, 1.0, 16.0, 7.6), "rust", tag="cleaver")
    k.box(cv, C(-11.0, 21.4, 6.0, 1.1, 16.0, 0.8), "iron", tag="edge")
    k.box(cv, C(-11.0, 35.4, 2.4, 1.0, 2.0, 5.4), "rust", tag="cleaver_tip")
    for y in (24, 28, 32):
        k.box(cv, C(-11.0, y, 6.2, 1.2, 1.0, 0.6), "dark", tag="notch")
    k.box(cv, C(-11.0, 33, -0.4, 1.2, 1.2, 1.2), "dark", tag="hole")
    lit(k)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Goblin Shaman (caster)

def goblin_shaman():
    """The shamans keep the bonefires burning in the Fang. A goblin bent nearly double under a headdress made of a
    great horned skull, hung with black feathers, bones and little bells, its own face painted in a glowing white
    skull; a cloak of patched hides, and a staff of lashed thighbones with three skulls at its head and fire in their
    eyes. When it shakes the staff the brutes go mad."""
    k = X.Kit("goblin_shaman")
    hips = k.part("hips", (0, 14, 0))
    k.stack(hips, 0, 0, [(10, 7.6, 5.8), (14, 7.8, 5.8)], "hide", "loin")
    robe = k.part("robe", (0, 14, 0), (), "hips", bone=False)
    k.stack(robe, 0, -0.4, [(3, 11.4, 9.0), (8, 10.4, 8.0), (14, 8.6, 6.6)], "hide", "cloak")
    for i in range(-4, 5):
        k.shard(robe, (i * 1.3, 3.4, 4.0 if abs(i) < 3 else 2.6), (0, -1, 0.1), 2.0 + (i % 3), 1.4, mat="fur", tag="hem")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.2
        th = k.part("thigh_" + nm, (x, 13, 0), (("x", -16),), "hips")
        sh = k.part("shin_" + nm, (x, 7.4, 0), (("x", 24),), th)
        ft = k.part("foot_" + nm, (x, 2.0, 0), (("x", -8),), sh)
        k.limb(sh, (x, 7.0, 0), (x, 2.2, 0), 1.8, "gob", "shin")
        k.box(ft, C(x, 0, 1.0, 2.6, 1.8, 4.4), "gob", tag="foot")
    to = k.part("torso", (0, 14, 0), (("x", 40),), "hips")
    k.stack(to, 0, 0, [(14, 7.8, 5.6), (19, 8.4, 5.8), (23, 9.0, 6.0)], "gob", "chest")
    k.stack(to, 0, -0.6, [(15, 11, 7.6), (23.6, 12, 8.0)], "hide", "mantle")
    for i in range(7):                            # necklaces: finger bones, a fang, a little skull
        a = math.radians(-60 + i * 20)
        k.box(to, C(math.sin(a) * 3.6, 20.6 - math.cos(a) * 1.4, 3.6, 0.6, 1.4, 0.5), "bone", tag="bones")
    skull(k, to, (0, 17.0, 4.4), 0.7)
    for i in range(5):                            # feathers off the mantle
        a = math.radians(-60 + i * 30)
        k.limb(to, (math.sin(a) * 5.4, 23.0, -2.0), (math.sin(a) * 7.6, 18.0, -4.6), 1.4, "dark", "feather", d=0.4)
    hd = k.part("head", (0, 23, 1.2), (("x", -40),), "torso")
    k.box(hd, C(0, 22.6, 1.6, 5.2, 4.6, 4.8), "gob", tag="head")
    for sx in (-1, 1):                            # its face painted in a white skull that glows
        k.box(hd, C(sx * 1.2, 24.6, 4.05, 1.6, 1.4, 0.3), "bone", tag="paint_socket")
        k.box(hd, C(sx * 1.2, 24.7, 4.2, 0.9, 0.7, 0.3), "eye", tag="eye")
        k.limb(hd, (sx * 2.4, 24.8, 1.6), (sx * 7.4, 26.0, 0.0), 1.4, "gob", "ear", d=0.6)
    k.limb(hd, (0, 24.0, 4.0), (0, 22.4, 6.4), 1.0, "gob", "nose")
    for x in (-1.2, -0.4, 0.4, 1.2):
        k.box(hd, C(x, 22.0, 4.05, 0.4, 1.2, 0.3), "bone", tag="paint_teeth")
    # the headdress: a great horned skull worn over its head, feathers and bells hung off it
    k.box(hd, C(0, 26.6, 1.6, 7.0, 3.6, 7.0), "bone", tag="beast_skull")
    k.box(hd, C(0, 27.0, 5.6, 4.6, 2.6, 3.6), "bone", tag="beast_snout")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.0, 28.4, 5.15, 1.6, 1.2, 0.4), "dark", tag="beast_socket")
        pts = [(sx * 3.0, 29.6, 0.6), (sx * 7.4, 32.0, -0.6), (sx * 9.6, 36.6, -0.4), (sx * 8.4, 40.6, 0.8)]
        for (p0, p1), w in zip(zip(pts, pts[1:]), (2.0, 1.6, 1.2)):
            k.limb(hd, p0, p1, w, "bone", "horn")
        for i in range(3):
            k.limb(hd, (sx * (3.0 + i * 1.2), 26.6, -1.4), (sx * (4.0 + i * 1.6), 19.6 - i, -2.4), 1.2, "dark", "feather", d=0.4)
        k.box(hd, C(sx * 4.6, 25.0, 1.6, 0.8, 0.8, 0.8), "gold", tag="bell")
    for t in (-1.2, 1.2):
        k.shard(hd, (t, 26.0, 7.0), (0, -1, 0.1), 1.8, 0.6, mat="bone", tag="beast_fang")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.6
        up = k.part("arm_" + nm, (x, 21.6, 0), (("x", -70 if side > 0 else -40), ("z", side * 14)), "torso")
        fo = k.part("fore_" + nm, (x, 16.6, 0), (("x", -20 if side > 0 else -60),), up)
        hn = k.part("hand_" + nm, (x, 11.6, 0), (), fo)
        k.limb(up, (x, 21.2, 0), (x, 17, 0), 2.0, "gob", "upper_arm")
        k.limb(fo, (x, 16.6, 0), (x, 12.2, 0), 1.8, "gob", "forearm")
        for y in (12.6, 13.8):
            k.box(fo, C(x, y, 0, 2.4, 0.6, 2.4), "bone", tag="bangle")
        k.box(hn, C(x, 10.0, 0.3, 2.0, 2.0, 2.2), "gob", tag="hand")
    rt = k.part("rattle", (5.6, 9.6, 1.0), (), k.parts["hand_l"], bone=False)
    k.limb(rt, (5.6, 10.6, 1.0), (5.6, 5.6, 1.0), 0.8, "bone", "rattle_handle")
    k.blob(rt, (5.6, 4.0, 1.0), (1.8, 2.0, 1.8), "hide", "rattle_gourd", step=0.6)
    k.box(rt, C(5.6, 3.4, 2.6, 1.2, 1.2, 0.4), "fire", tag="rattle_rune")
    st = k.part("staff", (-5.6, 10.6, 0.6), (("x", 80),), k.parts["hand_r"], bone=False)
    for i in range(4):                            # lashed thighbones
        y0 = -4 + i * 8
        k.limb(st, (-5.6, y0, 0.6), (-5.6, y0 + 8.4, 0.6), 1.4, "bone", "bone_shaft")
        k.box(st, C(-5.6, y0 + 7.6, 0.6, 2.4, 1.6, 2.4), "bone", tag="knuckle")
        k.box(st, C(-5.6, y0 + 3.6, 0.6, 1.8, 1.0, 1.8), "hide", tag="lashing")
    for (dx, dy, dz) in ((0, 32.6, 0.6), (-2.2, 29.6, 0.6), (2.2, 29.6, 0.6)):
        skull(k, st, (-5.6 + dx, dy, dz + 0.4), 1.2, eyes="fire")
    k.blob(st, (-5.6, 37.6, 0.6), (1.8, 2.6, 1.8), "fire", "bonefire", step=0.6)
    for i in range(3):
        k.shard(st, (-5.6 + (i - 1) * 0.9, 38.6, 0.6), ((i - 1) * 0.3, 1, 0), 3.4 - abs(i - 1), 1.2, mat="fire", tag="flame")
    lit(k)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Warg Rider (elite, crawler)

def warg_rider():
    """Gorrak's best goblin rides the biggest warg in the Fang. The warg is black and mangy, as big as a horse, a
    hyena's sloping back and a wolf's jaws, a spiked iron collar, its eyes and its open throat burning orange; on its
    back a saddle of hides with a pole of skulls and a red rag flying off it, and in the saddle a goblin in a horned
    helm with a barbed spear as long as the warg."""
    k = X.Kit("warg_rider")
    body = k.part("body", (0, 18, 0))
    k.stack(body, 0, 1, [(10, 13, 17), (17, 16, 19), (24, 13, 15)], "fur", "chest", step=1.2)
    for z in range(-6, 9, 2):                     # a ragged mane down the hackles
        k.shard(body, (0, 24, z), (0, 1, -0.5), 3.4 + (z % 4) * 0.5, 1.6, mat="fur", tag="mane")
    for sx in (-1, 1):
        k.box(body, C(sx * 7.0, 16, 2.0, 1.0, 3.0, 4.0), "orc", tag="mange")
    hd = k.part("head", (0, 20, 10), (("x", -16),), "body")
    k.ring(hd, 0, 17.6, 9.0, 6.4, 1.8, "rust", "collar", n=16, axis="z")
    for a in range(0, 360, 45):
        r = math.radians(a)
        k.shard(hd, (math.cos(r) * 7.0, 17.6 + math.sin(r) * 7.0, 9.0), (math.cos(r), math.sin(r), 0.2), 2.6, 1.0, mat="iron", tag="collar_spike")
    k.box(hd, C(0, 15.6, 13.8, 8.4, 7.6, 7.6), "fur", tag="head")
    k.box(hd, C(0, 16.4, 21.4, 5.0, 3.6, 8.0), "fur", tag="muzzle")
    k.box(hd, C(0, 19.0, 25.2, 2.2, 1.4, 0.8), "dark", tag="nose")
    k.limb(hd, (0, 13.6, 15.4), (0, 10.0, 25.0), 4.0, "fur", "jaw", d=4.4)
    k.limb(hd, (0, 14.6, 16.0), (0, 13.0, 25.0), 3.6, "fire", "throat", d=3.8)
    for t in (-1.6, -0.6, 0.6, 1.6):
        k.shard(hd, (t, 16.6, 25.0 - abs(t) * 0.8), (0, -1, 0.05), 2.8 if abs(t) > 1 else 1.6, 0.7, mat="bone", tag="fang")
        k.shard(hd, (t, 11.0, 24.0 - abs(t) * 0.8), (0, 1, 0.1), 1.6, 0.6, mat="bone", tag="fang")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.6, 19.4, 17.65, 1.8, 0.8, 0.4), "eye", tag="eye")
        k.limb(hd, (sx * 1.0, 20.4, 18.0), (sx * 3.8, 21.4, 17.2), 1.0, "fur", "brow")
        k.shard(hd, (sx * 3.0, 22.4, 11.6), (sx * 0.3, 0.7, -0.8), 4.6, 2.2, mat="fur", tag="ear")
    ab = k.part("abdomen", (0, 17, -8), (), "body")
    k.stack(ab, 0, -11, [(9, 9, 10), (14, 10.6, 11), (18, 9, 10)], "fur", "haunch")
    for (a, b), w in zip(zip([(0, 16, -16), (0, 13, -20), (0, 9, -23)], [(0, 13, -20), (0, 9, -23), (0, 6, -24)]), (2.6, 2.2, 1.6)):
        k.limb(ab, a, b, w, "fur", "tail")
    # the saddle, the pole of skulls, the goblin in it
    k.box(body, C(0, 23.6, -3.0, 13.6, 2.0, 12.0), "hide", tag="saddle")
    k.box(body, C(0, 25.0, -8.6, 9.0, 3.0, 1.6), "hide", tag="cantle")
    for sx in (-1, 1):
        k.box(body, C(sx * 7.0, 15.0, -3.0, 1.0, 9.0, 8.0), "hide", tag="saddle_skirt")
        skull(k, body, (sx * 7.6, 16.6, -1.0), 1.0)
    banner(k, body, (-4.4, 25, -9.2), 26, skulls=2)
    r_hips = (0, 25.6, -2.6)
    k.stack(body, 0, -2.6, [(25.4, 7.4, 5.6), (28.6, 7.6, 5.6)], "hide", "rider_hips")
    for sx in (-1, 1):                            # its legs down the warg's flanks
        k.limb(body, (sx * 3.0, 27, -2.0), (sx * 7.8, 22, 1.6), 2.4, "gob", "rider_thigh")
        k.limb(body, (sx * 7.8, 22, 1.6), (sx * 8.4, 16.4, -0.4), 2.0, "gob", "rider_shin")
        k.box(body, C(sx * 8.4, 15.0, 0.4, 2.4, 1.8, 3.6), "hide", tag="rider_foot")
    k.stack(body, 0, -2.0, [(28.6, 7.6, 5.4), (33, 8.4, 5.6), (37, 9.6, 6.0)], "rust", "rider_chest")
    k.box(body, C(0, 31.4, 0.8, 4.0, 3.2, 0.5), "paint", tag="rider_mark")
    k.box(body, C(0, 37.0, -1.6, 5.4, 4.8, 5.0), "gob", tag="rider_head")
    k.blob(body, (0, 41.4, -1.6), (3.2, 2.0, 3.2), "iron", "rider_helm", step=0.6)
    for sx in (-1, 1):
        k.box(body, C(sx * 1.2, 39.2, 0.95, 1.2, 0.7, 0.3), "eye", tag="rider_eye")
        k.limb(body, (sx * 2.6, 39.6, -1.6), (sx * 7.4, 41.0, -2.6), 1.4, "gob", "rider_ear", d=0.6)
        k.limb(body, (sx * 2.8, 42.0, -1.6), (sx * 4.6, 46.4, -0.6), 1.2, "bone", "rider_horn")
    k.box(body, C(0, 37.0, 0.95, 3.4, 0.8, 0.3), "mouth", tag="rider_grin")
    k.limb(body, (4.6, 36, -2), (8.0, 31, 2.0), 1.8, "gob", "rider_arm")
    k.limb(body, (-4.6, 36, -2), (-6.6, 31, 3.0), 1.8, "gob", "rider_arm")
    k.limb(body, (-8.0, 26, -8.0), (-5.6, 34, 10.0), 1.2, "wood", "spear_haft")    # the barbed spear, couched forward
    k.limb(body, (-5.6, 34, 10.0), (-3.6, 40.4, 24.0), 1.2, "wood", "spear_haft")
    k.shard(body, (-3.6, 40.4, 24.0), (0.13, 0.4, 0.9), 7.0, 2.0, mat="rust", tag="spear_head")
    for t in (0.3, 0.6):
        k.shard(body, (-3.6 + 0.13 * 7 * t, 40.4 + 0.4 * 7 * t, 24.0 + 0.9 * 7 * t), (0, -0.5, -1), 2.2, 0.8, mat="rust", tag="barb")
    k.box(body, C(-4.6, 36.4, 17.0, 0.4, 3.4, 4.0), "rag", tag="spear_rag")
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, (z, j, part) in enumerate(((6, 1, body), (-11, 4, ab))):
            nm = "leg_%s%d" % (s, i)
            lg = k.part(nm, (side * 5.4, 15, z), (), part)
            kn = (side * 6.0, 7.4, z + (1.6 if i == 0 else -2.8))
            k.limb(lg, (side * 5.4, 15, z), kn, 3.8, "fur", "leg")
            k.limb(lg, kn, (side * 6.0, 0.8, z + (0.8 if i == 0 else 0.4)), 2.8, "fur", "foot")
            k.box(lg, C(side * 6.0, 0, z + 1.4, 4.2, 1.8, 5.4), "fur", tag="foot")
            for t in (-1.2, 0, 1.2):
                k.shard(lg, (side * 6.0 + t, 0.6, z + 3.8), (0, -0.3, 1), 1.8, 0.7, mat="bone", tag="foot")
            joints[nm] = ("LL" if side > 0 else "RL") + str(j)
    lit(k)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ Gorrak (boss)

def gorrak():
    """The warlord who built the Fang waits at its top by his war drum. Eleven blocks of orc in black plate beaten
    out of a hundred stolen shields and studded with spikes, a war crown of iron spikes with skulls on them, gold rings
    through tusks as long as daggers, red paint across his eyes; a cloak of hides, two trophy banners on his back hung
    with the skulls of the chiefs he broke, and a cleaver as big as a door."""
    k = X.Kit("gorrak")
    hips = k.part("hips", (0, 30, 0))
    k.stack(hips, 0, 0, [(20, 24, 16), (30, 25, 16.6)], "hide", "breeches")
    k.box(hips, C(0, 28.0, 0, 27, 3.0, 18), "hide", tag="belt")
    skull(k, hips, (0, 28.6, 9.6), 2.2)
    for x in (-9, -4.5, 4.5, 9):                  # a skirt of black plates
        k.box(hips, C(x, 14, 8.4, 4.6, 14, 1.4), "iron", tag="tasset")
        k.shard(hips, (x, 14.0, 9.2), (0, -1, 0.3), 2.4, 1.2, mat="iron", tag="tasset_spike")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.6
        th = k.part("thigh_" + nm, (x, 28, 0), (("x", -6), ("z", side * 8)), "hips")
        sh = k.part("shin_" + nm, (x, 15.6, 0), (("x", 10),), th)
        ft = k.part("foot_" + nm, (x, 4, 0), (("x", -4),), sh)
        k.stack(th, x, 0, [(15.6, 10.4, 10.8), (28, 12.4, 12.8)], "hide", "thigh")
        k.box(th, C(x, 14.0, 2.4, 10.0, 4.4, 9.6), "iron", tag="knee")
        k.shard(th, (x, 16.4, 7.2), (0, 0.3, 1), 4.0, 2.2, mat="iron", tag="knee_spike")
        k.stack(sh, x, 0, [(4, 10.4, 11.0), (15.6, 10.4, 11.0)], "iron", "greave")
        for y in (7, 11):
            k.box(sh, C(x, y, 5.6, 2.0, 1.4, 1.0), "rust", tag="rivet_strip")
        k.box(ft, C(x, 0, 2.4, 12.4, 4.4, 17), "iron", tag="foot")
        for t in (-3.6, 0, 3.6):
            k.shard(ft, (x + t, 2.0, 10.6), (0, 0.2, 1), 3.0, 1.8, mat="iron", tag="toe_spike")
    # ---------------------------------------------------------------- torso: black plate, a cloak of hides, the banners
    to = k.part("torso", (0, 30, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(30, 25, 16.6), (36, 29, 17.6), (44, 38, 19.4), (52, 42, 19.4), (57, 34, 16.6)], "iron", "cuirass", step=1.2)
    for y in (36, 41, 46):                        # plates hammered over plates
        k.box(to, C((y % 2) * 1.2, y, 9.4 + (y - 36) * 0.06, 22 + (y - 36) * 0.9, 1.2, 1.2), "rust", tag="plate_edge")
    k.blob(to, (0, 47.4, 9.8), (5.6, 4.4, 1.6), "rust", "boss_plate", step=0.8)
    skull(k, to, (0, 45.8, 11.0), 2.2, eyes="fire")
    for (x, y) in ((-12, 40), (12, 40), (-8, 34), (8, 34)):
        k.shard(to, (x, y, 9.4), (x * 0.03, 0.2, 1), 3.4, 1.8, mat="iron", tag="chest_spike")
    for sx in (-1, 1):                            # spiked pauldrons, layered like scales
        k.blob(to, (sx * 21.4, 55.4, 0), (8.0, 5.4, 9.0), "iron", "pauldron", step=1.0)
        for i in range(3):
            k.box(to, C(sx * (22.4 + i * 0.5), 50.4 - i * 2.4, 0, 9.4, 2.2, 16.4), "rust" if i % 2 else "iron", tag="lame")
        for z in (-5, -1.6, 1.6, 5):
            k.shard(to, (sx * 23.6, 60.0, z), (sx * 0.5, 1, 0), 7.0 - abs(z) * 0.4, 2.6, mat="iron", tag="pauldron_spike")
        skull(k, to, (sx * 21.4, 52.6, 9.6), 1.6)
    k.stack(to, 0, -0.8, [(52, 44, 22), (58, 34, 19)], "fur", "mantle")
    k.limb(to, (17, 55, 10.4), (-14, 31, 10.4), 3.6, "rag", "sash", d=1.0)
    for x in (-14, 14):
        k.box(to, C(x, 34, 9.6, 1.4, 10, 0.6), "paint", tag="war_stripe")
    cape = k.part("cape", (0, 57, -10), (("x", 6),), to, bone=False)
    k.stack(cape, 0, -10.6, [(12, 34, 1.8), (36, 36, 1.8), (57, 34, 2.0)], "hide", "cape")
    for i in range(-7, 8):
        k.shard(cape, (i * 2.3, 12.4, -10.6), (0, -1, 0), 3.0 + (i % 3) * 1.6, 2.4, mat="hide", tag="hem")
    for sx in (-1, 1):                            # the trophy banners on his back
        banner(k, to, (sx * 9.0, 46, -12.6), 50, skulls=3, side=sx, s=2.0)
    # ---------------------------------------------------------------- head: tusks ringed in gold, the war crown
    hd = k.part("head", (0, 57, 3), (("x", -10),), "torso")
    orc_face(k, hd, (0, 56.0, 2.6), 2.5, tusk=4.0, ring=True)
    for sx in (-1, 1):
        k.box(hd, C(sx * 4.0, 64.6, 10.2, 4.4, 2.2, 0.4), "paint", tag="war_paint")
    k.box(hd, C(0, 73.6, 2.6, 17.0, 3.0, 15.4), "iron", tag="crown")
    for i, x in enumerate((-7.0, -3.5, 0, 3.5, 7.0)):
        h = 10.0 - abs(x) * 0.5 + (4 if i == 2 else 0)
        k.shard(k.parts["head"], (x, 76.4, 9.4 - abs(x) * 0.3), (x * 0.05, 1, 0.05), h, 2.6, mat="iron", tag="crown_spike")
        if i % 2 == 0:
            skull(k, hd, (x, 76.4 + h * 0.4, 10.8 - abs(x) * 0.3), 1.1)
    for z in (-2.0, -5.6):
        for x in (-7.6, 7.6):
            k.shard(hd, (x, 76.4, z), (x * 0.06, 1, -0.1), 7.0, 2.2, mat="iron", tag="crown_spike")
    k.stack(hd, 0, -3.6, [(70, 3.4, 3.4), (82, 2.6, 2.6)], "dark", "topknot")
    k.limb(hd, (0, 82, -3.6), (0, 66, -12), 2.6, "dark", "topknot_tail")
    # ---------------------------------------------------------------- arms: the cleaver like a door, a spiked fist
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 23.0
        up = k.part("arm_" + nm, (x, 53, 0), (("x", -24 if side > 0 else -30), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 38, 0), (("x", -40 if side > 0 else -60),), up)
        hn = k.part("hand_" + nm, (x, 23, 0), (), fo)
        k.limb(up, (x, 51, 0), (x, 39, 0), 9.0, "orc", "upper_arm")
        k.box(up, C(x, 44, 0, 9.8, 2.0, 9.8), "gold", tag="arm_ring")
        k.stack(fo, x, 0, [(24, 9.4, 9.6), (32, 11.0, 11.2), (38, 9.4, 9.6)], "iron", "vambrace")
        for z in (-3, 3):
            k.shard(fo, (x + side * 5.0, 31, z), (side, 0.2, 0), 4.0, 1.8, mat="iron", tag="vambrace_spike")
        k.box(hn, C(x, 16.0, 0.6, 9.0, 7.6, 9.4), "iron", tag="gauntlet")
        for t in (-3.0, -1.0, 1.0, 3.0):
            k.shard(hn, (x + t, 19.0, 5.0), (0, 0.2, 1), 2.6, 1.4, mat="iron", tag="knuckle_spike")
    cv = k.part("chopper", (-23.0, 19.6, 0.6), (("x", 70),), k.parts["hand_r"], bone=False)
    k.limb(cv, (-23.0, 8, 0.6), (-23.0, 24, 0.6), 3.0, "hide", "grip")
    k.box(cv, C(-23.0, 6, 0.6, 4.4, 2.6, 4.4), "iron", tag="pommel")
    k.box(cv, C(-23.0, 23.6, 0.6, 4.0, 2.6, 6.0), "iron", tag="guard")
    for i in range(22):                           # a butcher's chopper: the blade widening to a square, slanted tip
        y = 25 + i * 1.9
        w = 12.0 + i * 0.42
        top = i >= 19
        k.box(cv, C(-23.0, y, -1.4 + w / 2 - (2.0 * (i - 18) if top else 0) / 2, 2.0, 1.95, w - (2.0 * (i - 18) if top else 0)), "rust", tag="chopper")
        k.box(cv, C(-23.0, y, -1.4 + w + 0.4, 2.3, 1.95, 1.6), "iron", tag="edge")
        if i % 5 == 2:
            k.box(cv, C(-23.0, y, -1.4 + w + 1.0, 2.4, 1.2, 1.0), "dark", tag="notch")
    k.limb(cv, (-23.0, 27, -1.6), (-23.0, 66, -1.6), 2.4, "iron", "spine")
    disc(k, cv, (-23.0, 60.0, 3.0), 2.4, "x", "dark", "hang_hole", thick=2.6)
    for (y, z) in ((30, 0.6), (40, 0.6), (50, 0.6)):
        k.box(cv, C(-23.0, y, z, 2.6, 1.2, 1.2), "iron", tag="rivet")
    k.box(cv, C(-23.0, 36, 7.0, 2.4, 7.0, 7.0), "paint", tag="war_mark")
    skull(k, cv, (-23.0, 20.0, -3.0), 1.4)
    lit(k)
    grow(k, 1.5)
    k.s.shaders = shaders()
    return k.s, k.parts


MOBS = {
    "goblin_cutthroat": dict(make=goblin_cutthroat, ent=(0.8, 2.0), stats=dict(hp=22, speed=0.34, dmg=6, armor=2, kb=0)),
    "orc_brute": dict(make=orc_brute, ent=(1.8, 3.8), stats=dict(hp=150, speed=0.22, dmg=18, armor=8, kb=1.0)),
    "orc_raider": dict(make=orc_raider, ent=(1.3, 3.4), stats=dict(hp=80, speed=0.25, dmg=12, armor=10, kb=0.5)),
    "goblin_shaman": dict(make=goblin_shaman, ent=(0.8, 2.2), stats=dict(hp=36, speed=0.24, dmg=7, armor=2, kb=0)),
    "warg_rider": dict(make=warg_rider, rig="crawler", ent=(2.2, 3.4), stats=dict(hp=260, speed=0.4, dmg=15, armor=8, kb=0.7), key=True),
    "gorrak": dict(make=gorrak, texel=1, ent=(4.0, 9.8), stats=dict(hp=1000, speed=0.21, dmg=26, armor=13, kb=1.0), boss=True),
}
