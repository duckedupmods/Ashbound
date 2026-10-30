"""The Sporefolk: the walking fungus that grows in the world's giant mushrooms, mushroom villages and mines, built
by hand (tools/vox2.py). Pale fleshy stalks for bodies, caps in dusky violet and brown, white gills under them,
mycelium in threads over everything, chitin where they need to be hard - and the magenta glow of the spores in
their eyes, their gills, their puffballs. (Not Rotwood's moss and rot: these are alive and growing.)

    spore_tick      swarm   a beetle with a puffball the size of its body on its back, ready to burst
    capguard        guard   a stalk-man under a conical cap, a bracket-fungus shield and a spear of hardened stalk
    sporemaw        brute   a giant toadstool walking: a cap like a roof, a maw of gills in its trunk, root-fists
    morel_shaman    caster  tall and thin under a honeycombed morel cap, a robe of mycelium, a staff of glowing puffs
    inkcap_stalker  skirm   lean under a shaggy inkcap that drips black, chitin blades for hands
    elder_cap       elite   the colony's knight: a cap as wide as a cart wheel glowing at the gills, armour of
                            bark and chitin, a great blade of hardened mycelium

    python tools/monsterforge.py sporefolk --preview ; python tools/mobsheet.py sporefolk
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import grow
from _folk import lit, eyes, legs, arms, held, quad

STALK = ramp("#2a2420", "#443a32", "#625446", "#82705c", "#a28c74", "#bcaa90")
CAP = ramp("#140a14", "#22101e", "#34182a", "#4a2236", "#622e42", "#7c3c4e")
BROWN = ramp("#140c08", "#22140c", "#341e12", "#482a18", "#5e3820", "#784a2c")
GILL = ramp("#3a3430", "#5c544c", "#807666", "#a49a88", "#c8beaa", "#e6dcc8")
CHITIN = ramp("#0a0808", "#141010", "#201818", "#2e2222", "#3e2e2c", "#523c38")
INKCAP = ramp("#0e0c0e", "#1a171a", "#282428", "#383238", "#4a424a", "#5e545c")
INK = ramp("#040306", "#08060c", "#0e0a14", "#16101c")
BARK = ramp("#100c08", "#1a140e", "#261e16", "#34281e", "#443426")
SPORE = ramp("#4a0634", "#800a5a", "#bc1886", "#ec46b4", "#ff92da", "#ffe0f6")
MOSS = ramp("#0e1a10", "#162818", "#203820", "#2c4a2a")


def shaders():
    spots = lambda p, n, i, j, w, h: 0.22 if (i * 5 + j * 3) % 11 == 0 else 0.0
    return {
        "stalk": X.wrinkled(STALK, 0.5),
        "cap": X.surf(CAP, 0.5, 1.3, 0.2, 0.14, pattern=spots),
        "brown": X.surf(BROWN, 0.5, 1.3, 0.2, 0.12, pattern=spots),
        "gill": X.surf(GILL, 0.5, 1.0, 0.1, 0.0, pattern=lambda p, n, i, j, w, h: -0.26 if i % 2 == 0 else 0.04),
        "morel": X.surf(BROWN, 0.5, 1.3, 0.14, 0.1, pattern=lambda p, n, i, j, w, h: -0.3 if (i % 3 == 0 or j % 3 == 0) else 0.06),
        "chitin": X.surf(CHITIN, 0.6, 1.6, 0.08, 0.3),
        "inkcap": X.surf(INKCAP, 0.5, 1.2, 0.24, 0.1),
        "ink": X.surf(INK, 0.6, 1.2, 0.06, 0.1),
        "bark": X.surf(BARK, 0.5, 1.1, 0.24, 0.08, stripe=3),
        "thread": X.surf(GILL, 0.6, 1.0, 0.3, 0.0, holes=True),
        "moss": X.surf(MOSS, 0.5, 1.0, 0.3, 0.0),
        "spore": X.glow(SPORE),
        "eye": X.glow(SPORE, 0.84, 0.14),
        "dark": X.dark(INK),
    }


GLOWS = {"spore", "eye"}


def cap(k, part, c, r, h, mat="cap", gills=True, glow_gills=False, spots=0, cone=False, seed=1):
    """a mushroom cap centred over c (its underside at c's y): flat-ish or conical, gills under it"""
    cx, cy, cz = c
    if cone:
        layers = [(cy + h * t, r * 2 * (1 - t * 0.85), r * 2 * (1 - t * 0.85)) for t in (0, 0.2, 0.4, 0.6, 0.8, 1.0)]
        k.stack(part, cx, cz, layers, mat, "cap", step=0.8)
    else:
        k.blob(part, (cx, cy, cz), (r, h, r), mat, "cap", step=0.7, cut=lambda y: y >= cy)
        k.box(part, C(cx, cy - 1.0, cz, r * 2.0, 1.2, r * 2.0), mat, tag="cap_lip")
    if gills:
        k.box(part, C(cx, cy - 0.6, cz, r * 1.86, 0.7, r * 1.86), "spore" if glow_gills else "gill", tag="gills")
        k.box(part, C(cx, cy - 0.8, cz, r * 1.0, 0.4, r * 1.0), "gill", tag="gills")
    for i in range(spots):                        # pale scales on top
        a = i * 2.399 + seed
        d = r * (0.25 + 0.6 * ((i * 0.618 + seed * 0.1) % 1))
        t = 0.3 + 0.5 * (1 - d / r)
        k.box(part, C(cx + math.cos(a) * d, cy + h * t, cz + math.sin(a) * d, 1.4, 1.0, 1.4), "gill", tag="cap_scale")


def threads(k, part, pts, mat="thread", w=0.5):
    for a, b in zip(pts, pts[1:]):
        k.limb(part, a, b, w, mat, "mycelium", d=0.4)


# ================================================================ the Spore Tick (swarm)

def spore_tick():
    """Ticks that the colony farms: a hard black beetle the size of a dog carrying a puffball as big as itself on its
    back, the skin of it stretched thin and glowing through, ready to split and fill the room."""
    k = X.Kit("spore_tick")
    body, hd, ab, joints = quad(k, "chitin", y=7, chest=((3, 9, 9), (6, 10, 10), (8.6, 8.6, 8.6)), haunch=((3, 8.6, 8), (6, 9.6, 9), (8.4, 8.4, 8)),
                                leg_w=1.6, foot_w=1.2, front_z=3, back_z=-5, x=5.4, head_at=(0, 7, 6), head_rot=4, claw="chitin", foot_len=3.0,
                                knees=(3.0, -3.4))
    k.blob(ab, (0, 14.6, -2.4), (6.4, 6.0, 6.8), "gill", "puffball", step=0.8)
    for i in range(9):                            # the glow coming through its skin, in patches
        a = i * 2.399
        k.box(ab, C(math.cos(a) * 5.4, 12.0 + (i % 3) * 2.6, -2.4 + math.sin(a) * 5.4, 1.6, 1.6, 1.6), "spore", tag="puff_glow")
    k.box(ab, C(0, 20.4, -2.4, 2.0, 0.8, 2.0), "spore", tag="puff_vent")
    threads(k, ab, [(-5, 9.4, 2), (-6.4, 12.0, 0), (-5.6, 16.0, -3)])
    threads(k, ab, [(5, 9.4, -5), (6.6, 12.4, -4), (5.4, 17.0, -1)])
    k.box(body, C(0, 6.6, 1.0, 9.4, 1.2, 9.6), "chitin", tag="carapace_edge")
    k.box(hd, C(0, 4.0, 8.4, 6.0, 4.0, 4.4), "chitin", tag="head")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.0, 6.8, 10.5, 1.4, 1.0, 0.4), "eye", tag="eye")
        k.limb(hd, (sx * 1.6, 4.6, 10.6), (sx * 0.6, 3.4, 13.6), 0.9, "chitin", "mandible")
        k.limb(hd, (sx * 1.8, 7.6, 9.6), (sx * 4.6, 11.4, 12.4), 0.4, "chitin", "antenna")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Capguard (guard)

def capguard():
    """The colony's soldiers: a stalk grown into a man, pale and ridged, mycelium in threads over the joints, a tall
    conical cap pulled low with the gills glowing under its rim and two eyes in the stalk below it, a shield that
    is a slab of bracket fungus off a dead tree, and a spear of a stalk dried hard as bone with a chitin head."""
    k = X.Kit("capguard")
    hips = k.part("hips", (0, 19, 0))
    k.stack(hips, 0, 0, [(12, 10.4, 7.6), (19, 10.6, 7.8)], "stalk", "hips")
    for i, x in enumerate((-4.0, -1.4, 1.4, 4.0)):             # a skirt of gill-frills
        k.box(hips, C(x, 10.6 - (i % 2), 0, 2.6, 3.0, 8.6), "gill", tag="frill")
    k.box(hips, C(0, 17.6, 0, 11.2, 1.6, 8.4), "bark", tag="belt")
    legs(k, hips, 18, 9.8, 3.0, "stalk", "stalk", knee_mat="bark", lean=-6, bend=8, w=4.6, cuff=False)
    for side in (1, -1):
        nm = "shin_" + ("l" if side > 0 else "r")
        k.box(k.parts[nm], C(side * 3.0, 0.6, 0, 6.0, 1.8, 6.4), "stalk", tag="foot_root")
        threads(k, k.parts[nm], [(side * 5.0, 2.0, 1.0), (side * 3.4, 6.0, 2.6), (side * 2.0, 9.0, 1.8)])
    to = k.part("torso", (0, 19, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(19, 10.4, 7.6), (24, 11.4, 8.0), (29, 13.4, 8.6), (32.6, 12.0, 8.0)], "stalk", "torso")
    for y in (21.0, 24.0, 27.0):                  # the stalk's ridges
        k.box(to, C(0, y, 3.9 + (y - 21) * 0.06, 8.6, 0.6, 0.4), "gill", tag="ridge")
    k.box(to, C(0, 22.0, 4.2, 9.4, 9.0, 0.8), "bark", tag="breastplate")
    k.box(to, C(0, 27.0, 4.7, 3.0, 3.0, 0.3), "spore", tag="colony_mark")
    for sx in (-1, 1):
        k.blob(to, (sx * 6.8, 31.4, 0), (2.8, 1.8, 3.4), "brown", "shoulder_cap", step=0.6)
        k.box(to, C(sx * 6.8, 30.4, 0, 4.6, 0.4, 5.4), "gill", tag="shoulder_gill")
    hd = k.part("head", (0, 32.6, 0.6), (("x", -6),), "torso")
    k.stack(hd, 0, 0.6, [(32.6, 6.4, 6.0), (37.0, 6.2, 6.0)], "stalk", "stalk_head")
    eyes(k, hd, 34.8, 3.7, 1.4, 1.2, h=0.8)
    k.box(hd, C(0, 33.4, 3.65, 2.0, 0.6, 0.3), "dark", tag="mouth")
    cap(k, hd, (0, 37.6, 0.6), 7.6, 10.0, mat="brown", cone=True, glow_gills=True, spots=0)
    arms(k, to, 7.4, 30, "stalk", {1: ((("x", -30), ("z", -6)), (("x", -50),)), -1: ((("x", -40), ("z", 6)), (("x", -40),))}, w=3.4)
    sh = held(k, "shield", "l", (7.4, 12.4, 0.4), (("x", 80),))           # the bracket fungus: a half-moon slab, rings on it
    for i, (r, t) in enumerate(((7.4, 1.6), (6.0, 1.4), (4.4, 1.2), (2.6, 1.0))):
        k.box(sh, C(7.0, 12.4 - r * 0.9, 2.8 + i * 0.6, r * 2, r * 1.6, t), "brown" if i % 2 == 0 else "bark", tag="bracket")
    k.box(sh, C(7.0, 12.4 - 7.4 * 0.9, 2.6, 14.8, 0.8, 1.8), "gill", tag="bracket_edge")
    sp = held(k, "spear", "r", (-7.4, 12.4, 0.3), (("x", 92),))
    k.limb(sp, (-7.4, -6.0, 0.3), (-7.4, 30.0, 0.3), 1.4, "stalk", "spear_stalk")
    for y in (2.0, 12.0, 22.0):
        k.box(sp, C(-7.4, y, 0.3, 2.0, 0.8, 2.0), "gill", tag="stalk_ring")
    k.shard(sp, (-7.4, 30.0, 0.3), (0, 1, 0), 7.0, 2.4, mat="chitin", tag="spear_head")
    k.box(sp, C(-7.4, 29.0, 0.3, 2.4, 1.4, 2.4), "spore", tag="spear_glow")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Sporemaw (brute)

def sporemaw():
    """Some of them grow too big to stand straight. A toadstool as tall as a house walking on root-legs, its cap
    a broad violet roof spotted pale, its trunk split down the front into a maw lined with gills like teeth that
    breathes out the glow, two arms of knotted root ending in fists crusted with shelf fungus."""
    k = X.Kit("sporemaw")
    hips = k.part("hips", (0, 18, 0))
    k.stack(hips, 0, 0, [(10, 16.0, 13.0), (18, 17.0, 13.6)], "stalk", "trunk_base")
    for a in range(0, 360, 45):                   # roots spreading at the base
        r = math.radians(a)
        k.limb(hips, (math.cos(r) * 6.0, 11.0, math.sin(r) * 5.0), (math.cos(r) * 9.0, 7.0, math.sin(r) * 7.6), 1.8, "bark", "root")
    legs(k, hips, 16, 8.4, 5.0, "bark", "bark", knee_mat=None, lean=-4, bend=6, w=6.6, cuff=False)
    for side in (1, -1):
        nm = "foot_" + ("l" if side > 0 else "r")
        for t in (-2.4, 0, 2.4):
            k.limb(k.parts[nm], (side * 5.0 + t, 1.0, 3.0), (side * 5.0 + t * 1.6, 0.4, 7.0), 1.4, "bark", "toe_root")
    to = k.part("torso", (0, 18, 0), (("x", 8),), "hips")
    k.stack(to, 0, 0, [(18, 17.0, 13.6), (24, 17.6, 14.0), (30, 16.6, 13.4), (36, 14.0, 11.6)], "stalk", "trunk")
    # the maw: the trunk split open down the front, gill-teeth, the glow breathing out of it
    k.box(to, C(0, 21.0, 6.2, 9.0, 13.0, 1.4), "dark", tag="maw")
    for i in range(8):
        y = 21.6 + i * 1.6
        for sx in (-1, 1):
            k.box(to, C(sx * 3.4, y, 6.8, 2.6, 0.6, 0.8), "gill", tag="gill_teeth")
    k.blob(to, (0, 27.0, 5.8), (2.6, 4.4, 1.0), "spore", "maw_glow", step=0.6)
    for sx in (-1, 1):
        k.box(to, C(sx * 5.4, 19.0, 6.4, 1.6, 17.0, 1.6), "stalk", tag="maw_lip")
    threads(k, to, [(-8, 20, 5), (-7.4, 26, 6.4), (-8.6, 32, 4.6)])
    threads(k, to, [(8, 22, 5), (7.6, 28, 6.2), (8.4, 34, 3.6)])
    hd = k.part("head", (0, 36, 0.4), (("x", -4),), "torso")
    k.stack(hd, 0, 0.4, [(36, 12.0, 10.4), (39, 9.0, 8.4)], "stalk", "neck")
    k.box(hd, C(0, 38.0, 0.4, 13.0, 1.6, 11.4), "gill", tag="ring")            # the ring round the stalk under the cap
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.6, 40.6, 4.4, 1.8, 1.2, 0.4), "eye", tag="eye")
    cap(k, hd, (0, 41.4, 0.4), 15.0, 9.0, mat="cap", glow_gills=True, spots=16, seed=3)
    arms(k, to, 11.6, 33, "bark", {1: ((("x", -30), ("z", -14)), (("x", -40),)), -1: ((("x", -50), ("z", 14)), (("x", -30),))}, w=5.4, long=1.2)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        for b in list(k.s.boxes):
            if b.part is k.parts["hand_" + nm]:
                k.s.boxes.remove(b)
        hn = k.parts["hand_" + nm]
        y = 33 - 8 * 1.2 - 7.6 * 1.2
        k.blob(hn, (side * 11.6, y - 2.6, 0.4), (3.6, 3.4, 3.8), "bark", "root_fist", step=0.7)
        for i in range(3):                        # shelf fungus crusted on the knuckles
            k.box(hn, C(side * 11.6 + (i - 1) * 1.8, y - 1.4 + i * 0.6, 3.8, 2.6, 0.8, 2.0), "brown", tag="knuckle_shelf")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.3)
    return k.s, k.parts


# ================================================================ the Morel Shaman (caster)

def morel_shaman():
    """The colony's mind, if it has one: tall and thin as a reed under a cap like a honeycomb, pitted and folded, a
    robe of mycelium hanging off it in white threads, long fingers, and a staff of twisted stalk crowned with a
    cluster of puffballs that glow and breathe out the spores when it speaks."""
    k = X.Kit("morel_shaman")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(2, 13.0, 11.0), (10, 11.4, 9.4), (21, 10.0, 7.6)], "thread", "robe", step=1.0)
    for i in range(12):                           # threads trailing off the hem onto the ground
        a = i * 2 * math.pi / 12
        k.limb(hips, (math.cos(a) * 6.0, 3.0, math.sin(a) * 5.0), (math.cos(a) * 8.0, 0.4, math.sin(a) * 6.6), 0.6, "thread", "hem_thread")
    for side, nm in ((1, "l"), (-1, "r")):
        th = k.part("thigh_" + nm, (side * 3.0, 20, 0), (("x", -4),), hips)
        sh = k.part("shin_" + nm, (side * 3.0, 11, 0), (("x", 6),), th)
        ft = k.part("foot_" + nm, (side * 3.0, 2.4, 0), (), sh)
        k.box(ft, C(side * 3.0, 0, 1.4, 4.0, 2.0, 6.4), "stalk", tag="foot")
    to = k.part("torso", (0, 21, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(21, 10.0, 7.6), (27, 10.4, 7.6), (32, 11.6, 7.8), (35, 10.0, 7.0)], "thread", "robe")
    k.box(to, C(0, 22.0, 3.9, 3.0, 12.0, 0.4), "stalk", tag="stalk_body")
    for y in (25.0, 29.0):
        k.box(to, C(0, y, 4.0, 1.6, 1.6, 0.4), "spore", tag="spore_bead")
    hd = k.part("head", (0, 35, 0.4), (("x", -4),), "torso")
    k.stack(hd, 0, 0.4, [(35, 5.4, 5.0), (39, 5.0, 4.8)], "stalk", "stalk_head")
    eyes(k, hd, 37.4, 2.6, 1.2, 1.0, h=1.4)
    # the morel: tall, pitted, a rounded cone
    k.stack(hd, 0, 0.4, [(39.6, 8.4, 8.4), (42, 9.0, 9.0), (45, 8.4, 8.4), (48, 7.0, 7.0), (51, 5.0, 5.0), (53, 2.6, 2.6)], "morel", "morel_cap", step=1.0)
    for i in range(6):
        a = i * math.pi / 3
        k.box(hd, C(math.cos(a) * 4.2, 42.0 + (i % 3) * 2.6, 0.4 + math.sin(a) * 4.2, 1.2, 1.2, 1.2), "spore", tag="pit_glow")
    arms(k, to, 6.6, 33, "thread", {1: ((("x", -14), ("z", -8)), (("x", -40),)), -1: ((("x", -58), ("z", 6)), (("x", -24),))}, glove="stalk", w=3.0, long=1.15)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        y = 33 - 8 * 1.15 - 7.6 * 1.15 - 2.6
        for t in (-0.9, 0, 0.9):
            k.limb(k.parts["hand_" + nm], (side * 6.6 + t, y, 1.2), (side * 6.6 + t * 1.4, y - 3.8, 2.0), 0.6, "stalk", "finger")
    st = held(k, "staff", "r", (-6.6, 14.6, 0.4), (("x", 70), ("z", -4)))
    for i in range(6):                            # a twisted stalk
        a = i * 1.0
        k.limb(st, (-6.6 + math.cos(a) * 0.6, -6.0 + i * 6.0, 0.4 + math.sin(a) * 0.6),
               (-6.6 + math.cos(a + 1) * 0.6, i * 6.0, 0.4 + math.sin(a + 1) * 0.6), 1.6, "stalk", "staff")
    for (x, y, z, r) in ((0, 33.0, 0, 2.6), (2.0, 31.4, 1.0, 1.8), (-1.8, 31.0, -0.8, 2.0), (0.6, 35.4, -1.0, 1.6), (-1.0, 34.6, 1.6, 1.4)):
        k.blob(st, (-6.6 + x, y, 0.4 + z), (r, r, r), "gill", "puff", step=0.5)
        k.box(st, C(-6.6 + x, y + r * 0.6, 0.4 + z, r * 0.8, 0.6, r * 0.8), "spore", tag="puff_glow")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Inkcap Stalker (skirmisher)

def inkcap_stalker():
    """Inkcaps melt as they ripen and these never stop ripening. Lean and long-armed, a shaggy cap like a bell over
    the head with its edges dissolving into black ink that runs down the stalk-body, and for hands two long blades
    of chitin, black and wet."""
    k = X.Kit("inkcap_stalker")
    hips = k.part("hips", (0, 19, 0))
    k.stack(hips, 0, 0, [(13, 9.4, 7.0), (19, 9.6, 7.2)], "stalk", "hips")
    legs(k, hips, 18, 9.6, 2.8, "stalk", "stalk", knee_mat="chitin", lean=-14, bend=22, w=4.0, cuff=False)
    for side in (1, -1):
        k.box(k.parts["shin_" + ("l" if side > 0 else "r")], C(side * 2.8, 2.0, 1.6, 3.8, 6.0, 1.4), "chitin", tag="shin_plate")
    to = k.part("torso", (0, 19, 0), (("x", 20),), "hips")
    k.stack(to, 0, 0, [(19, 9.6, 7.2), (24, 10.0, 7.2), (29, 12.0, 7.6), (32, 10.6, 7.0)], "stalk", "torso")
    for x, y0, L in ((-2.6, 31.0, 9.0), (0.4, 31.6, 12.0), (2.8, 30.6, 7.4), (-0.8, 28.0, 5.0)):     # ink running down it
        k.box(to, C(x, y0 - L, 3.7, 0.8, L, 0.3), "ink", tag="ink_run")
    for sx in (-1, 1):
        k.box(to, C(sx * 5.8, 28.4, 0, 2.4, 4.0, 5.0), "chitin", tag="shoulder_plate")
    hd = k.part("head", (0, 32, 0.6), (("x", -16),), "torso")
    k.stack(hd, 0, 0.6, [(32, 5.0, 4.8), (35, 4.8, 4.6)], "stalk", "stalk_head")
    eyes(k, hd, 34.0, 2.65, 1.2, 1.0, h=0.8)
    # the shaggy inkcap: a tall bell, scales curling off it, the rim black and dripping
    k.stack(hd, 0, 0.6, [(33.0, 10.4, 10.4), (35, 10.6, 10.6), (38, 10.0, 10.0), (40.6, 8.8, 8.8), (42.6, 6.8, 6.8), (43.8, 4.0, 4.0)], "inkcap", "inkcap", step=1.0)
    for i in range(14):
        a = i * 2.399
        y = 35.0 + (i * 0.618 % 1) * 7.0
        r = 5.2 - (y - 35.0) * 0.3
        k.box(k.parts["head"], C(math.cos(a) * r, y, 0.6 + math.sin(a) * r, 1.4, 1.6, 1.4), "brown", tag="shag")
    k.box(hd, C(0, 32.6, 0.6, 11.0, 1.6, 11.0), "ink", tag="ink_rim")
    for i in range(12):
        a = i * 2 * math.pi / 12
        L = 1.6 + (i % 3) * 1.6
        k.box(hd, C(math.cos(a) * 5.2, 32.6 - L, 0.6 + math.sin(a) * 5.2, 0.8, L, 0.8), "ink", tag="ink_drip")
    arms(k, to, 6.2, 30, "stalk", {1: ((("x", -10), ("z", 30)), (("x", -60),)), -1: ((("x", -60), ("z", -20)), (("x", -30),))}, glove="chitin", w=3.0, long=1.15)
    for side, nm in ((1, "l"), (-1, "r")):        # blade-hands: long, curved, black
        x = side * 6.2
        bl = held(k, "blade_" + nm, nm, (x, 12.0, 0.4), (("x", 90),))
        pts = [(x, 12.0, 0.4), (x, 18.0, 1.4), (x, 23.0, 3.4), (x, 26.4, 6.4)]
        for (a, b), w in zip(zip(pts, pts[1:]), (2.6, 2.2, 1.6)):
            k.limb(bl, a, b, 0.8, "chitin", "chitin_blade", d=w)
        k.shard(bl, pts[-1], (0, 0.5, 1), 2.4, 0.8, mat="chitin", tag="blade_tip")
        k.box(bl, C(x, 16.0, 1.6, 0.4, 3.0, 0.4), "ink", tag="ink_wet")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Elder Cap (elite)

def elder_cap():
    """The colony's knight is its oldest growth: twice a man's height to the top of a cap as wide as a cart wheel,
    the gills under it glowing like a lantern-roof, its stalk-body armoured in plates of bark and black chitin grown
    to fit, mycelium hanging off it like a cloak, and a great blade of hardened mycelium, white and ridged, that it
    grew itself."""
    k = X.Kit("elder_cap")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(12, 12.0, 8.6), (21, 12.4, 8.8)], "stalk", "hips")
    for i, y in enumerate((16.0, 12.6)):
        for sx in (-1, 1):
            k.box(hips, C(sx * 3.6, y, 4.2 + i * 0.3, 5.6, 3.6, 1.0), "chitin", tag="tasset")
    k.box(hips, C(0, 19.6, 0, 13.0, 2.0, 9.4), "bark", tag="belt")
    legs(k, hips, 20, 10.8, 3.6, "stalk", "chitin", knee_mat="bark", lean=-6, bend=8, w=5.6, cuff=True)
    to = k.part("torso", (0, 21, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(21, 12.4, 8.8), (26, 14.0, 9.4), (31, 17.0, 10.2), (35, 16.0, 9.6)], "stalk", "torso")
    k.blob(to, (0, 29.0, 2.4), (6.6, 5.6, 3.6), "chitin", "breastplate", step=0.7)
    for y in (22.0, 24.6):
        k.box(to, C(0, y, 4.4, 11.6, 1.6, 1.0), "bark", tag="bark_plate")
    k.box(to, C(0, 29.6, 5.7, 3.0, 3.0, 0.4), "spore", tag="heart_glow")
    for sx in (-1, 1):
        k.blob(to, (sx * 9.4, 33.6, 0), (4.6, 3.0, 5.0), "chitin", "pauldron", step=0.7)
        k.blob(to, (sx * 9.8, 36.0, 0), (3.0, 1.4, 3.4), "cap", "shoulder_cap", step=0.6)
        k.box(to, C(sx * 9.8, 35.4, 0, 5.4, 0.5, 6.0), "spore", tag="shoulder_gills")
    cl = k.part("cloak", (0, 34, -5.0), (("x", 4),), to, bone=False)
    for i in range(9):                            # a cloak of hanging mycelium
        x = -6.4 + i * 1.6
        L = 26.0 - (i * 5 % 4) * 2.4
        k.limb(cl, (x, 34.0, -5.4), (x * 1.2, 34.0 - L, -6.4 - (i % 2)), 1.2, "thread", "mycelium_cloak", d=0.6)
    hd = k.part("head", (0, 35, 0.6), (("x", -4),), "torso")
    k.stack(hd, 0, 0.6, [(35, 6.6, 6.2), (40, 6.4, 6.0)], "stalk", "stalk_head")
    k.box(hd, C(0, 36.0, 3.7, 6.4, 2.0, 0.6), "chitin", tag="visor_plate")
    eyes(k, hd, 38.6, 3.75, 1.5, 1.4, h=0.9)
    k.box(hd, C(0, 40.2, 0.6, 9.0, 1.6, 8.6), "gill", tag="ring")
    cap(k, hd, (0, 41.6, 0.6), 13.0, 8.0, mat="cap", glow_gills=True, spots=14, seed=5)
    for i in range(10):                           # glow dripping off the cap's rim
        a = i * 2 * math.pi / 10
        k.box(hd, C(math.cos(a) * 12.0, 39.4, 0.6 + math.sin(a) * 12.0, 0.6, 1.8 + (i % 3) * 0.8, 0.6), "spore", tag="rim_drip")
    arms(k, to, 9.6, 33, "stalk", {1: ((("x", -36), ("z", -20)), (("x", -40),)), -1: ((("x", -32), ("z", 18)), (("x", -44),))}, glove="chitin", w=3.8)
    for side in (1, -1):
        k.box(k.parts["fore_" + ("l" if side > 0 else "r")], C(side * 9.6, 18.0, 0, 4.6, 5.0, 4.6), "chitin", tag="vambrace")
    gs = held(k, "myco_blade", "r", (-9.6, 14.0, 0.3), (("x", 78), ("z", -16)))
    k.limb(gs, (-9.6, 6.0, 0.3), (-9.6, 15.8, 0.3), 1.6, "bark", "grip")
    k.blob(gs, (-9.6, 5.0, 0.3), (1.6, 1.4, 1.6), "spore", "pommel", step=0.5)
    k.box(gs, C(-9.6, 15.8, 0.3, 8.4, 2.0, 2.4), "chitin", tag="guard")
    for sx in (-1, 1):
        k.blob(gs, (-9.6 + sx * 4.2, 16.8, 0.3), (1.6, 1.2, 1.6), "cap", "guard_cap", step=0.5)
    for i in range(11):                           # the blade: white, ridged like gills, a little wavy
        w = 4.6 - abs(i - 4) * 0.2
        k.box(gs, C(-9.6 + math.sin(i * 0.9) * 0.4, 17.8 + i * 2.4, 0.3, w, 2.45, 1.2), "gill", tag="myco_blade")
        k.box(gs, C(-9.6, 17.8 + i * 2.4 + 1.0, 0.9, w - 1.2, 0.5, 0.4), "thread", tag="blade_ridge")
    k.box(gs, C(-9.6, 18.0, 1.0, 1.0, 24.0, 0.3), "spore", tag="blade_vein")
    k.shard(gs, (-9.6, 44.2, 0.3), (0, 1, 0), 4.0, 2.4, mat="gill", tag="blade_tip")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.15)
    return k.s, k.parts


MOBS = {
    "spore_tick": dict(make=spore_tick, rig="crawler", ent=(1.0, 1.4), stats=dict(hp=20, speed=0.3, dmg=5, armor=3, kb=0)),
    "capguard": dict(make=capguard, ent=(0.9, 3.0), stats=dict(hp=58, speed=0.24, dmg=9, armor=7, kb=0.3)),
    "sporemaw": dict(make=sporemaw, ent=(1.9, 4.2), stats=dict(hp=200, speed=0.17, dmg=17, armor=5, kb=1.0)),
    "morel_shaman": dict(make=morel_shaman, ent=(0.9, 3.2), stats=dict(hp=38, speed=0.22, dmg=7, armor=2, kb=0)),
    "inkcap_stalker": dict(make=inkcap_stalker, ent=(0.8, 2.8), stats=dict(hp=42, speed=0.34, dmg=8, armor=3, kb=0)),
    "elder_cap": dict(make=elder_cap, ent=(1.2, 3.8), stats=dict(hp=330, speed=0.24, dmg=15, armor=12, kb=0.6), key=True),
}
