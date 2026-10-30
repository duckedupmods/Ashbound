"""The Hollow Order: a knightly order that swore to hold its castles forever and is holding them still, though there
is no one left inside the armour, who hold the world's lost castles, citadels and the acropolis, built by hand
(tools/vox2.py). Tarnished silver plate, maroon heraldry rotted to rags, chain gone dark, and where the bodies were
a cold white wisp-fire that shows at every gap - the eye-slits, the neck, the joints.

    hollow_squire   swarm   half a harness - breastplate, sallet, one gauntlet - walking on its own, a dagger
    hollow_knight   guard   full plate, a great helm with a slit full of white fire, a kite shield with the Order's
                            cross, a longsword
    siege_knight    brute   the Order's wall: massive plate, a tower shield as tall as a door, a flanged mace
    hollow_chaplain caster  a mitre-crested helm, vestments over mail, a censer swinging white fire
    hollow_destrier skirm   a warhorse's barding with no horse in it, white fire for a mane, iron-shod hooves
    grand_master    elite   the master of the Order: a crowned great helm with a cross crest, a tattered cape and
                            surcoat, a two-handed sword with the relic set in its pommel

    python tools/monsterforge.py hollow_order --preview ; python tools/mobsheet.py hollow_order
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import grow
from _folk import lit, eyes, legs, arms, held, quad

SILVER = ramp("#0e0f12", "#1a1c20", "#282b30", "#383c42", "#4c5158", "#646a72", "#80868e")
MAROON = ramp("#140406", "#22080a", "#340e10", "#481616", "#5c1e1c")
CHAIN = ramp("#0a0a0c", "#121214", "#1c1c20", "#26262c", "#32323a")
GILT = ramp("#2a1e0a", "#463412", "#68501c", "#8a6c28", "#aa8a36")
LEATHER = ramp("#0e0a08", "#18120e", "#221a14", "#2e241c")
WOOD = ramp("#100c08", "#1a140e", "#261e16", "#34281e")
WISP = ramp("#46505e", "#7a8698", "#aab6c6", "#d4dee8", "#eef4fa", "#ffffff")


def shaders():
    mail = lambda p, n, i, j, w, h: -0.22 if (i + (j % 2)) % 2 == 0 and j % 2 == 0 else 0.04
    return {
        "silver": X.surf(SILVER, 0.56, 1.6, 0.1, 0.3, rust=(CHAIN, 0.18, 0.5)),
        "maroon": X.surf(MAROON, 0.5, 1.0, 0.22, 0.0, holes=True),
        "mail": X.surf(CHAIN, 0.5, 1.2, 0.1, 0.0, pattern=mail),
        "gilt": X.surf(GILT, 0.54, 1.4, 0.14, 0.2),
        "leather": X.surf(LEATHER, 0.5, 1.1, 0.2, 0.04),
        "wood": X.surf(WOOD, 0.5, 1.0, 0.2, 0.06, stripe=3),
        "steel": X.surf(SILVER, 0.7, 1.7, 0.05, 0.34),
        "wisp": X.glow(WISP),
        "eye": X.glow(WISP, 0.9, 0.1),
        "dark": X.dark(CHAIN),
    }


GLOWS = {"wisp", "eye"}


def cross(k, part, c, s=1.0, mat="silver", axis="z"):
    """the Order's cross: a cross with flared arms"""
    cx, cy, cz = c
    if axis == "z":
        k.box(part, C(cx, cy - 3.0 * s, cz, 1.2 * s, 6.0 * s, 0.3), mat, tag="order_cross")
        k.box(part, C(cx, cy + 0.4 * s, cz, 4.6 * s, 1.2 * s, 0.3), mat, tag="order_cross")
        for dx, dy in ((0, 3.0), (0, -3.0), (2.3, 1.0), (-2.3, 1.0)):
            k.box(part, C(cx + dx * s, cy + dy * s - 0.5 * s, cz, 1.8 * s, 1.0 * s, 0.3), mat, tag="cross_flare")
    else:
        k.box(part, C(cx, cy - 3.0 * s, cz, 0.3, 6.0 * s, 1.2 * s), mat, tag="order_cross")
        k.box(part, C(cx, cy + 0.4 * s, cz, 0.3, 1.2 * s, 4.6 * s), mat, tag="order_cross")


def great_helm(k, part, c, s=1.0, crown=False):
    """the flat-topped great helm: a barrel, a slit for the eyes full of fire, breaths in a cross below"""
    cx, cy, cz = c
    k.stack(part, cx, cz, [(cy - 4.0 * s, 7.0 * s, 7.0 * s), (cy + 3.6 * s, 7.4 * s, 7.4 * s), (cy + 4.8 * s, 6.6 * s, 6.6 * s)], "silver", "great_helm", step=1.0)
    k.box(part, C(cx, cy + 0.6 * s, cz + 3.6 * s, 6.0 * s, 0.9 * s, 0.4), "dark", tag="sight")
    k.box(part, C(cx, cy + 0.7 * s, cz + 3.7 * s, 5.4 * s, 0.6 * s, 0.3), "eye", tag="eye")
    k.box(part, C(cx, cy - 3.6 * s, cz + 3.75 * s, 1.0 * s, 4.0 * s, 0.4), "silver", tag="helm_ridge")
    for dy in (-2.6, -1.4):
        for sx in (-1, 1):
            k.box(part, C(cx + sx * 1.6 * s, cy + dy * s, cz + 3.75 * s, 0.6 * s, 0.6 * s, 0.3), "wisp", tag="breath")
    k.box(part, C(cx, cy + 1.6 * s, cz + 3.75 * s, 7.6 * s, 0.6 * s, 0.4), "gilt", tag="helm_band")
    if crown:
        for i in range(8):
            a = i * math.pi / 4
            k.shard(part, (cx + math.sin(a) * 3.4 * s, cy + 5.4 * s, cz + math.cos(a) * 3.4 * s), (0, 1, 0), (2.2 if i % 2 else 3.0) * s, 1.0 * s, mat="gilt", tag="crown_point")


def hollow_gaps(k, part, at, w, d):
    """the white fire showing where a body should be: a neck, a joint"""
    x, y, z = at
    k.box(part, C(x, y, z, w, 1.2, d), "wisp", tag="hollow_fire")


# ================================================================ the Hollow Squire (swarm)

def hollow_squire():
    """The squires' harness was never finished and nobody fills it: a breastplate with nothing above the gorget but a
    sallet floating where a head should be, one gauntlet, mail sleeves hanging empty and swinging, the white fire
    licking out at the neck and the hips - and a long dagger the hand never lets go."""
    k = X.Kit("hollow_squire")
    hips = k.part("hips", (0, 18, 0))
    k.stack(hips, 0, 0, [(11, 10.4, 7.4), (18, 10.0, 7.2)], "mail", "mail_skirt")
    hollow_gaps(k, hips, (0, 17.4, 0), 6.0, 4.0)
    k.box(hips, C(0, 11.0, 3.8, 6.0, 7.0, 0.6), "maroon", tag="tabard")
    legs(k, hips, 17, 9.0, 3.0, "mail", "silver", knee_mat="silver", lean=-6, bend=8, w=4.4, cuff=True)
    to = k.part("torso", (0, 18, 0), (("x", 6),), "hips")
    k.blob(to, (0, 24.0, 0.6), (5.4, 5.0, 4.0), "silver", "breastplate", step=0.7)
    k.box(to, C(0, 19.0, 3.6, 8.0, 2.0, 0.8), "silver", tag="fauld")
    cross(k, to, (0, 24.6, 4.5), 0.7, mat="maroon")
    k.box(to, C(0, 28.6, 0, 7.0, 1.8, 6.0), "silver", tag="gorget")
    hollow_gaps(k, to, (0, 30.4, 0), 4.4, 3.6)
    k.blob(to, (0, 30.6, 0), (2.0, 1.6, 2.0), "wisp", "neck_fire", step=0.5)
    hd = k.part("head", (0, 30, 0.6), (("x", -4),), "torso")
    k.blob(hd, (0, 34.6, 0.0), (3.6, 3.0, 4.4), "silver", "sallet", step=0.6)
    k.shard(hd, (0, 33.4, -3.6), (0, -0.4, -1), 3.4, 3.4, mat="silver", tag="sallet_tail")
    k.box(hd, C(0, 33.0, 2.6, 6.4, 1.6, 2.4), "silver", tag="visor")
    k.box(hd, C(0, 34.2, 3.6, 5.6, 0.7, 0.3), "eye", tag="eye")
    k.box(hd, C(0, 31.2, 0.6, 3.6, 2.4, 3.6), "wisp", tag="hollow_fire")
    arms(k, to, 6.6, 28, "mail", {1: ((("x", -10), ("z", 10)), (("x", -20),)), -1: ((("x", -50), ("z", -10)), (("x", -40),))}, glove="silver", w=2.6)
    for b in list(k.s.boxes):                     # the left sleeve hangs empty: no gauntlet
        if b.part is k.parts["hand_l"]:
            k.s.boxes.remove(b)
    k.box(k.parts["fore_l"], C(6.6, 12.6, 0, 2.6, 1.4, 2.6), "wisp", tag="hollow_fire")
    dg = held(k, "dagger", "r", (-6.6, 12.4, 0.3), (("x", 84),))
    k.limb(dg, (-6.6, 9.0, 0.3), (-6.6, 13.0, 0.3), 1.0, "leather", "grip")
    k.box(dg, C(-6.6, 13.0, 0.3, 1.0, 1.0, 3.4), "gilt", tag="guard")
    k.box(dg, C(-6.6, 14.0, 0.3, 0.6, 8.0, 1.6), "steel", tag="dagger_blade")
    k.shard(dg, (-6.6, 22.0, 0.3), (0, 1, 0), 2.0, 1.0, mat="steel", tag="blade_tip")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Hollow Knight (guard)

def hollow_knight():
    """The brothers of the Order still stand their watches: full plate gone black at the seams, a great helm with the
    white fire burning in its slit, a maroon surcoat rotted to its last threads with the Order's cross on it, the
    kite shield painted with the same cross, and the longsword they swore on."""
    k = X.Kit("hollow_knight")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(12, 11.6, 8.2), (20, 11.2, 8.0)], "mail", "mail_skirt")
    for i, x in enumerate((-3.6, 0, 3.6)):
        k.box(hips, C(x, 6.0 + (i % 2) * 2.0, 4.2, 3.2, 14.0 - (i % 2) * 2.0, 0.6), "maroon", tag="surcoat")
        k.box(hips, C(x, 6.0 + (i % 2) * 2.0, -4.2, 3.2, 14.0 - (i % 2) * 2.0, 0.6), "maroon", tag="surcoat")
    hollow_gaps(k, hips, (0, 19.6, 0), 7.0, 5.0)
    legs(k, hips, 19, 10.4, 3.4, "silver", "silver", knee_mat="silver", lean=-6, bend=8, w=5.0, cuff=True)
    for side in (1, -1):
        hollow_gaps(k, k.parts["thigh_" + ("l" if side > 0 else "r")], (side * 3.4, 11.0, 0), 4.0, 4.0)
    to = k.part("torso", (0, 20, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(20, 11.2, 8.0), (25, 12.6, 8.6), (30, 14.8, 9.2), (33.6, 14.4, 8.8)], "silver", "cuirass")
    k.box(to, C(0, 21.0, 4.4, 10.0, 11.0, 0.6), "maroon", tag="surcoat")
    cross(k, to, (0, 26.4, 4.85), 1.0)
    k.box(to, C(0, 19.4, 0, 12.0, 1.6, 9.0), "leather", tag="sword_belt")
    for sx in (-1, 1):
        k.blob(to, (sx * 7.8, 31.4, 0), (3.6, 2.6, 4.4), "silver", "pauldron", step=0.7)
        k.box(to, C(sx * 8.2, 28.8, 0, 4.8, 1.4, 8.0), "silver", tag="pauldron_lame")
    hollow_gaps(k, to, (0, 33.6, 0), 4.6, 4.0)
    hd = k.part("head", (0, 34, 0.6), (("x", -4),), "torso")
    great_helm(k, hd, (0, 38.4, 0.6))
    arms(k, to, 8.0, 32, "silver", {1: ((("x", -40), ("z", -8)), (("x", -40),)), -1: ((("x", -30), ("z", 8)), (("x", -48),))}, w=3.6)
    for side in (1, -1):
        hollow_gaps(k, k.parts["fore_" + ("l" if side > 0 else "r")], (side * 8.0, 23.6, 0), 3.4, 3.4)
    sh = held(k, "kite_shield", "l", (8.0, 13, 0.4), (("x", 80),))
    for i in range(10):                           # the kite: broad at the top, a point at the foot
        y = 3.0 + i * 2.0
        w = 2.0 + min(i, 6) * 1.4
        k.box(sh, C(7.4, y, 3.0, w, 2.05, 1.2), "silver" if i in (0, 9) else "maroon", tag="kite")
    k.box(sh, C(7.4, 21.0, 3.0, 11.0, 2.0, 1.4), "silver", tag="kite_rim")
    cross(k, sh, (7.4, 14.0, 3.7), 1.3)
    k.shard(sh, (7.4, 3.0, 3.0), (0, -1, 0), 3.0, 2.0, mat="silver", tag="kite_point")
    sw = held(k, "longsword", "r", (-8.0, 14.0, 0.3), (("x", 84),))
    k.limb(sw, (-8.0, 8.0, 0.3), (-8.0, 15.0, 0.3), 1.2, "leather", "grip")
    k.box(sw, C(-8.0, 6.6, 0.3, 2.0, 1.6, 2.0), "gilt", tag="pommel")
    k.box(sw, C(-8.0, 15.0, 0.3, 1.4, 1.2, 7.4), "gilt", tag="crossguard")
    k.box(sw, C(-8.0, 16.2, 0.3, 0.8, 18.0, 2.4), "steel", tag="sword_blade")
    k.box(sw, C(-8.0, 16.4, 0.3, 0.9, 14.0, 0.5), "dark", tag="fuller")
    k.shard(sw, (-8.0, 34.2, 0.3), (0, 1, 0), 2.6, 1.6, mat="steel", tag="blade_tip")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Siege Knight (brute)

def siege_knight():
    """The Order held its breaches with these: the biggest harness its smiths ever made, plates as thick as a door,
    the helm a squat iron pot with a cross-slit, a tower shield as tall as a man planted before it with arrows still
    in it, and a flanged mace whose head is the size of a man's chest."""
    k = X.Kit("siege_knight")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(11, 15.0, 10.6), (20, 15.6, 11.0)], "silver", "plate_skirt")
    hollow_gaps(k, hips, (0, 19.4, 0), 9.0, 6.0)
    legs(k, hips, 19, 10.4, 4.8, "silver", "silver", knee_mat="silver", lean=-4, bend=6, w=7.0, cuff=True)
    to = k.part("torso", (0, 20, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(20, 15.6, 11.0), (25, 18.6, 12.0), (30, 22.0, 13.0), (34, 21.6, 12.6), (36.4, 16.0, 10.0)], "silver", "cuirass")
    k.box(to, C(0, 21.0, 6.0, 13.0, 12.0, 0.8), "maroon", tag="surcoat")
    cross(k, to, (0, 27.0, 6.45), 1.3)
    for sx in (-1, 1):
        k.blob(to, (sx * 11.6, 33.6, 0), (5.4, 3.6, 6.0), "silver", "pauldron", step=0.8)
        for i in range(3):
            k.box(to, C(sx * 12.0, 30.6 - i * 1.8, 0, 7.0 - i * 0.6, 1.6, 11.0 - i * 0.6), "silver", tag="pauldron_lame")
    hollow_gaps(k, to, (0, 36.0, 0), 6.0, 5.0)
    hd = k.part("head", (0, 36, 1.0), (("x", -6),), "torso")
    k.stack(hd, 0, 1.0, [(35.6, 9.0, 9.0), (41.0, 9.4, 9.4), (42.4, 8.0, 8.0)], "silver", "pot_helm", step=1.0)
    k.box(hd, C(0, 38.6, 5.75, 6.6, 0.9, 0.4), "eye", tag="eye")
    k.box(hd, C(0, 35.8, 5.75, 0.9, 5.0, 0.4), "eye", tag="eye")
    k.box(hd, C(0, 41.0, 5.85, 9.6, 0.8, 0.4), "gilt", tag="helm_band")
    arms(k, to, 12.0, 34, "silver", {1: ((("x", -30), ("z", -6)), (("x", -50),)), -1: ((("x", -60), ("z", 14)), (("x", -30),))}, w=5.6, long=1.1)
    sh = held(k, "tower_shield", "l", (12.0, 15.0, 0.4), (("x", 80),))
    k.box(sh, C(10.4, -2.0, 4.0, 14.0, 30.0, 1.6), "wood", tag="tower_shield")
    k.box(sh, C(10.4, -2.0, 4.9, 14.6, 30.4, 0.4), "maroon", tag="shield_face")
    for y in (-1.6, 27.4):
        k.box(sh, C(10.4, y, 4.0, 15.0, 1.2, 2.2), "silver", tag="shield_rim")
    for sx in (-1, 1):
        k.box(sh, C(10.4 + sx * 7.2, -2.0, 4.0, 1.0, 30.6, 2.2), "silver", tag="shield_rim")
    cross(k, sh, (10.4, 15.0, 5.2), 2.0)
    for i, (x, y) in enumerate(((6.0, 22.0), (14.0, 6.0), (8.0, 2.0))):       # the arrows still in it
        k.limb(sh, (x, y, 5.2), (x + 0.6, y + 0.8, 11.0), 0.5, "wood", "arrow_shaft")
        k.box(sh, C(x + 0.6, y + 0.6, 10.4, 0.3, 1.2, 1.4), "maroon", tag="fletching")
    mc = held(k, "mace", "r", (-12.0, 14.0, 0.4), (("x", 110),))
    k.limb(mc, (-12.0, 6.0, 0.4), (-12.0, 30.0, 0.4), 2.0, "steel", "mace_haft")
    for y in (8.0, 11.0):
        k.box(mc, C(-12.0, y, 0.4, 2.6, 1.4, 2.6), "leather", tag="grip_wrap")
    k.box(mc, C(-12.0, 28.0, 0.4, 4.0, 8.0, 4.0), "steel", tag="mace_head")
    for i in range(8):                            # the flanges
        a = i * math.pi / 4
        k.box(mc, C(-12.0 + math.cos(a) * 3.0, 28.4, 0.4 + math.sin(a) * 3.0, 1.0 + abs(math.cos(a)) * 1.6, 7.2, 1.0 + abs(math.sin(a)) * 1.6), "steel", tag="flange")
    k.shard(mc, (-12.0, 36.0, 0.4), (0, 1, 0), 3.0, 1.6, mat="steel", tag="mace_spike")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.25)
    return k.s, k.parts


# ================================================================ the Hollow Chaplain (caster)

def hollow_chaplain():
    """The Order's chaplains blessed the vows the knights still keep. An empty helm crested like a bishop's mitre
    with the white fire in its slit, vestments of rotten maroon and gold thread over mail, a stole hung with tarnished
    medals, and a censer on a chain that swings white fire instead of incense."""
    k = X.Kit("hollow_chaplain")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(1, 13.0, 11.0), (10, 11.6, 9.4), (21, 10.6, 8.0)], "maroon", "vestment", step=1.0)
    k.box(hips, C(0, 1.0, 5.2, 3.0, 20.0, 0.6), "gilt", tag="orphrey")
    k.stack(hips, 0, 0, [(0, 13.6, 11.6), (1.4, 13.6, 11.6)], "mail", "mail_hem")
    for side, nm in ((1, "l"), (-1, "r")):
        th = k.part("thigh_" + nm, (side * 3.0, 20, 0), (), hips)
        sh = k.part("shin_" + nm, (side * 3.0, 11, 0), (), th)
        ft = k.part("foot_" + nm, (side * 3.0, 2.4, 0), (), sh)
        k.box(ft, C(side * 3.0, 0, 3.4, 3.8, 2.0, 5.0), "silver", tag="foot")
    to = k.part("torso", (0, 21, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(21, 10.6, 8.0), (26, 11.0, 8.0), (31, 12.6, 8.4), (34, 11.6, 7.8)], "mail", "hauberk")
    k.box(to, C(0, 21.0, 4.1, 9.0, 12.0, 0.6), "maroon", tag="chasuble")
    cross(k, to, (0, 26.6, 4.5), 1.0, mat="gilt")
    for sx in (-1, 1):                            # the stole and its medals
        k.box(to, C(sx * 3.2, 18.0, 4.6, 1.8, 15.0, 0.4), "gilt", tag="stole")
        for y in (20.0, 23.0):
            k.box(to, C(sx * 3.2, y, 4.9, 1.4, 1.4, 0.3), "silver", tag="medal")
    hollow_gaps(k, to, (0, 33.4, 0), 4.6, 4.0)
    hd = k.part("head", (0, 34, 0.6), (("x", -6),), "torso")
    k.stack(hd, 0, 0.6, [(33.6, 6.6, 6.6), (38.6, 6.8, 6.8)], "silver", "helm", step=1.0)
    k.box(hd, C(0, 36.6, 3.95, 5.4, 0.8, 0.3), "eye", tag="eye")
    k.box(hd, C(0, 34.4, 3.95, 0.8, 2.0, 0.3), "eye", tag="eye")
    for sz in (-1, 1):                            # the mitre: two tall points front and back
        k.shard(hd, (0, 39.4, 0.6 + sz * 1.6), (0, 1, sz * 0.25), 6.0, 5.0, mat="maroon", tag="mitre")
    k.box(hd, C(0, 39.0, 0.6, 7.2, 1.2, 7.2), "gilt", tag="mitre_band")
    k.box(hd, C(0, 41.6, 3.2, 1.0, 3.0, 0.4), "gilt", tag="mitre_cross")
    arms(k, to, 7.0, 32, "mail", {1: ((("x", -60), ("z", -10)), (("x", -30),)), -1: ((("x", -30), ("z", 10)), (("x", -40),))}, glove="silver", w=3.4)
    for side in (1, -1):
        k.box(k.parts["fore_" + ("l" if side > 0 else "r")], C(side * 7.0, 15.4, 0, 4.6, 3.0, 4.6), "maroon", tag="sleeve")
    cs = held(k, "censer", "l", (7.0, 12.0, 0.4), (("x", 90),))
    k.chain(cs, (7.0, 12.0, 1.4), (7.0, 1.0, 1.4), 6, mat="gilt", w=0.8)
    k.blob(cs, (7.0, -1.8, 1.4), (2.4, 2.6, 2.4), "silver", "censer", step=0.6)
    k.blob(cs, (7.0, -1.6, 1.4), (1.8, 1.8, 1.8), "wisp", "censer_fire", step=0.5)
    k.shard(cs, (7.0, 0.6, 1.4), (0, 1, 0), 1.6, 2.6, mat="silver", tag="censer_lid")
    for i in range(3):
        k.blob(cs, (7.0 + i * 0.8, -5.4 - i * 2.0, 1.4), (1.2 + i * 0.3, 0.9, 1.2 + i * 0.3), "wisp", "white_smoke", step=0.5)
    st = held(k, "crozier", "r", (-7.0, 14.4, 0.4), (("x", 70),))
    k.limb(st, (-7.0, -6.0, 0.4), (-7.0, 26.0, 0.4), 1.2, "silver", "crozier")
    pts = [(-7.0, 26.0, 0.4), (-7.0, 29.0, 1.4), (-7.0, 30.0, 3.8), (-7.0, 28.4, 5.6), (-7.0, 26.6, 4.6)]
    for a, b in zip(pts, pts[1:]):
        k.limb(st, a, b, 1.0, "gilt", "crozier_crook")
    k.blob(st, (-7.0, 27.6, 3.2), (0.8, 0.8, 0.8), "wisp", "crook_light", step=0.4)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Hollow Destrier (skirmisher)

def hollow_destrier():
    """The knights' warhorses died under them; their barding didn't stop. A charger's armour with nothing inside it -
    a chanfron with a spike, a crinet down the neck, a caparison of maroon rags with the Order's cross - running on
    iron-shod hooves, the white fire streaming out of the neck for a mane and out of the eye-holes."""
    k = X.Kit("hollow_destrier")
    body, hd, ab, joints = quad(k, "silver", y=20, chest=((12, 12, 16), (18, 14, 18), (25, 12.6, 16)), haunch=((12, 12, 14), (18, 14, 15), (24, 12, 13)),
                                leg_w=3.4, foot_w=2.8, front_z=8, back_z=-12, x=4.8, head_at=(0, 26, 12), head_rot=-30, claw="steel", foot_len=4.4)
    for s in ("l", "r"):                          # iron-shod hooves
        for i in (0, 1):
            lg = k.parts["leg_%s%d" % (s, i)]
            x = (5.4 if s == "l" else -5.4)
            k.box(lg, C(x, 0, (8 if i == 0 else -12) + 1.4, 4.0, 2.4, 4.4), "steel", tag="foot")
            hollow_gaps(k, lg, (x, 9.0, (8 if i == 0 else -12)), 3.6, 3.6)
    for sx in (-1, 1):                            # the caparison, ragged, the cross on each flank
        k.box(body, C(sx * 7.6, 9.0, 0.0, 0.8, 11.0, 18.0), "maroon", tag="caparison")
        k.box(ab, C(sx * 7.4, 9.0, -13.0, 0.8, 10.0, 14.0), "maroon", tag="caparison")
        for z in (-6.0, -1.0, 4.0):
            k.box(body, C(sx * 7.7, 7.6, z, 0.9, 2.0, 2.4), "maroon", tag="caparison_rag")
        cross(k, body, (sx * 8.1, 16.0, 0.0), 1.2, mat="silver", axis="x")
    k.box(body, C(0, 25.6, -1.0, 10.0, 1.6, 12.0), "leather", tag="saddle")
    k.box(body, C(0, 27.2, 4.4, 4.0, 2.6, 1.6), "leather", tag="saddle_pommel")
    hollow_gaps(k, body, (0, 26.4, -2.0), 6.0, 6.0)
    # the neck and the head: crinet plates, the chanfron, fire for a mane
    for i in range(5):
        k.box(hd, C(0, 22.0 + i * 2.0, 12.0 + i * 1.6, 7.0 - i * 0.3, 2.4, 6.0), "silver", tag="crinet")
    k.box(hd, C(0, 28.0, 21.0, 6.0, 6.6, 8.0), "silver", tag="chanfron")
    k.box(hd, C(0, 26.0, 26.4, 5.0, 5.0, 4.0), "silver", tag="chanfron_nose")
    k.shard(hd, (0, 33.4, 21.4), (0, 0.6, 0.8), 5.0, 1.6, mat="steel", tag="chanfron_spike")
    for sx in (-1, 1):
        k.box(hd, C(sx * 3.05, 31.0, 22.0, 0.3, 1.6, 2.0), "eye", tag="eye")
        k.shard(hd, (sx * 2.0, 34.4, 18.6), (sx * 0.2, 1, -0.3), 2.6, 1.6, mat="silver", tag="ear_guard")
    for i in range(7):                            # the mane of fire
        k.shard(hd, (0, 26.0 + i * 1.8, 11.0 + i * 1.4), (0, 0.6, -1), 4.0 + (i % 3), 1.6, mat="wisp", tag="fire_mane")
    tail = [(0, 22, -19), (0, 18, -24), (0, 12, -26)]
    for (a, b), w in zip(zip(tail, tail[1:]), (2.4, 2.0)):
        k.limb(ab, a, b, w, "wisp", "fire_tail")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Grand Master (elite)

def grand_master():
    """The master of the Order swore the oath for all of them, and holds it longest. The finest harness of the
    Order, gilt at every edge though the gilt is going, a great helm crowned and crested with the cross in gilt
    silver, a surcoat and a cape that have rotted to long maroon tatters, the white fire pouring out at the neck and
    the joints, and the two-handed sword of the Order with its relic set in the pommel, burning."""
    k = X.Kit("grand_master")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(12, 12.0, 8.6), (21, 12.0, 8.6)], "mail", "mail_skirt")
    for i, x in enumerate((-4.0, -1.3, 1.3, 4.0)):
        k.box(hips, C(x, 3.0 + (i % 2) * 2.4, 4.6, 2.6, 18.0 - (i % 2) * 2.4, 0.6), "maroon", tag="surcoat_tatter")
    for i, y in enumerate((16.0, 12.6)):
        for sx in (-1, 1):
            k.box(hips, C(sx * 3.6, y, 4.0 + i * 0.3, 5.6, 3.6, 1.0), "silver", tag="tasset")
            k.box(hips, C(sx * 3.6, y, 4.55 + i * 0.3, 5.8, 0.6, 0.4), "gilt", tag="tasset_edge")
    hollow_gaps(k, hips, (0, 20.6, 0), 7.4, 5.4)
    legs(k, hips, 20, 10.8, 3.6, "silver", "silver", knee_mat="gilt", lean=-6, bend=8, w=5.6, cuff=True)
    to = k.part("torso", (0, 21, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(21, 12.0, 8.6), (26, 13.8, 9.2), (31, 16.8, 10.0), (35, 16.4, 9.4)], "silver", "cuirass")
    k.box(to, C(0, 21.6, 4.7, 10.0, 12.0, 0.6), "maroon", tag="surcoat")
    cross(k, to, (0, 27.6, 5.15), 1.2, mat="gilt")
    for sx in (-1, 1):
        k.blob(to, (sx * 9.4, 33.6, 0), (4.6, 3.0, 5.0), "silver", "pauldron", step=0.7)
        for i in range(2):
            k.box(to, C(sx * 10.0, 30.4 - i * 1.8, 0, 6.2 - i * 0.6, 1.4, 9.4 - i * 0.6), "silver", tag="pauldron_lame")
            k.box(to, C(sx * 10.0, 31.6 - i * 1.8, 0, 6.4 - i * 0.6, 0.4, 9.6 - i * 0.6), "gilt", tag="lame_edge")
        k.shard(to, (sx * 10.4, 36.4, 0), (sx * 0.3, 1, 0), 2.6, 1.6, mat="gilt", tag="pauldron_fleur")
    hollow_gaps(k, to, (0, 35.0, 0), 5.0, 4.4)
    cl = k.part("cloak", (0, 35, -5.0), (("x", 5),), to, bone=False)
    for i, x in enumerate((-6.0, -3.0, 0.0, 3.0, 6.0)):
        L = 33.0 - (i * 3 % 4) * 2.4
        k.box(cl, C(x, 35.0 - L, -5.6, 3.0, L, 0.8), "maroon", tag="cape")
        k.box(cl, C(x + 0.8, 35.0 - L, -5.9, 1.0, 4.0, 0.4), "dark", tag="cape_rent")
    cross(k, cl, (0, 24.0, -6.15), 2.0, mat="silver")
    k.box(cl, C(0, 33.6, -5.8, 15.6, 1.6, 1.2), "gilt", tag="cape_bar")
    hd = k.part("head", (0, 35.6, 0.6), (("x", -4),), "torso")
    great_helm(k, hd, (0, 40.0, 0.6), 1.05, crown=True)
    k.box(hd, C(0, 45.6, 0.6, 1.4, 6.0, 1.4), "gilt", tag="crest_cross")          # the cross crest
    k.box(hd, C(0, 48.6, 0.6, 5.0, 1.4, 1.4), "gilt", tag="crest_cross")
    k.blob(hd, (0, 49.4, 0.6), (1.0, 1.0, 1.0), "wisp", "crest_fire", step=0.4)
    arms(k, to, 9.6, 33, "silver", {1: ((("x", -36), ("z", -20)), (("x", -40),)), -1: ((("x", -32), ("z", 18)), (("x", -44),))}, w=3.8)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        k.box(k.parts["fore_" + nm], C(side * 9.6, 23.0, 0, 5.0, 1.8, 5.0), "gilt", tag="couter")
        hollow_gaps(k, k.parts["fore_" + nm], (side * 9.6, 24.6, 0), 3.6, 3.6)
    gs = held(k, "order_sword", "r", (-9.6, 14.0, 0.3), (("x", 78), ("z", -16)))
    k.limb(gs, (-9.6, 4.0, 0.3), (-9.6, 15.8, 0.3), 1.6, "leather", "grip")
    k.blob(gs, (-9.6, 3.0, 0.3), (1.8, 1.8, 1.8), "gilt", "pommel", step=0.5)
    k.box(gs, C(-9.6, 2.6, 1.8, 1.4, 1.4, 0.4), "wisp", tag="relic")
    k.box(gs, C(-9.6, 15.8, 0.3, 11.0, 1.8, 2.0), "gilt", tag="crossguard")
    for sx in (-1, 1):
        k.shard(gs, (-9.6 + sx * 5.4, 16.6, 0.3), (sx * 0.2, 1, 0), 2.0, 1.2, mat="gilt", tag="quillon_tip")
    k.box(gs, C(-9.6, 17.6, 0.3, 4.0, 4.0, 1.4), "steel", tag="ricasso")
    k.box(gs, C(-9.6, 21.6, 0.3, 3.6, 24.0, 1.0), "steel", tag="sword_blade")
    k.box(gs, C(-9.6, 21.6, 0.9, 0.8, 20.0, 0.3), "dark", tag="fuller")
    cross(k, gs, (-9.6, 20.0, 1.05), 0.5, mat="gilt")
    k.shard(gs, (-9.6, 45.6, 0.3), (0, 1, 0), 3.4, 2.4, mat="steel", tag="blade_tip")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.15)
    return k.s, k.parts


MOBS = {
    "hollow_squire": dict(make=hollow_squire, ent=(0.8, 2.4), stats=dict(hp=26, speed=0.33, dmg=6, armor=6, kb=0)),
    "hollow_knight": dict(make=hollow_knight, ent=(0.9, 2.9), stats=dict(hp=64, speed=0.24, dmg=10, armor=11, kb=0.4)),
    "siege_knight": dict(make=siege_knight, ent=(1.8, 3.9), stats=dict(hp=210, speed=0.17, dmg=19, armor=15, kb=1.0)),
    "hollow_chaplain": dict(make=hollow_chaplain, ent=(0.9, 3.1), stats=dict(hp=40, speed=0.22, dmg=7, armor=5, kb=0)),
    "hollow_destrier": dict(make=hollow_destrier, rig="crawler", ent=(1.6, 2.6), stats=dict(hp=60, speed=0.4, dmg=11, armor=8, kb=0.6)),
    "grand_master": dict(make=grand_master, ent=(1.1, 3.6), stats=dict(hp=350, speed=0.24, dmg=16, armor=15, kb=0.7), key=True),
}
