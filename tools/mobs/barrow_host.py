"""The Barrow Host: the dead of the old kings' barrows, who hold the world's crypts, graveyards, strongholds and
the dungeons under them, built by hand (tools/vox2.py). Buried with their grave goods three thousand years ago -
bronze gone green as moss, gold masks hammered over their faces, purple cloth rotted to cobweb - and woken with a
pale soul-light in their eyes and their ribs. Nothing of wax and candles (the Crypt's) or the rope (Gallows Hill).

    ossipede        swarm   a centipede of fused vertebrae and rib-legs, a skull for a head, rib mandibles
    barrow_wight    guard   a skeleton in green bronze scale, a gold death mask, a crested helm, a round shield and
                            a leaf-bladed sword
    mound_brute     brute   a giant corpse dug out of its mound, bound in grave chains, swinging its own headstone
    wailing_shroud  caster  a grave-shroud with nothing in it but two eyes, skeletal hands, a soul lantern on a chain
    barrow_reaper   skirm   a stooped skeleton under a stag-skull helm, a bronze sickle in each hand
    barrow_king     elite   the king of the mound: gold and bronze plate, a tall gold mask and a horned crown, soul
                            fire burning in his ribs, a purple cloak gone to rags, a great bronze leaf-sword

    python tools/monsterforge.py barrow_host --preview ; python tools/mobsheet.py barrow_host
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import grow
from _folk import lit, eyes, straps, legs, arms, held, quad

BRONZE = ramp("#0e1a14", "#16281e", "#1e3a2a", "#2a5038", "#3a6a4a", "#5a8a64", "#86b090")
GOLD = ramp("#2a1c06", "#4a320a", "#765412", "#a47c20", "#cca232", "#ecc85a", "#fff0a0")
BONE = ramp("#2e2a22", "#4a443a", "#6a6252", "#8c846e", "#aea68c", "#ccc6ac")
SHROUD = ramp("#16161c", "#22222a", "#32323c", "#46464f", "#5c5c64", "#76767c")
PURPLE = ramp("#100814", "#1a0e20", "#26142e", "#341c3e", "#44264e")
CORPSE = ramp("#141a16", "#1e2620", "#2a342c", "#38443a", "#48564a", "#5c6a5c")
STONE = ramp("#1a1a1c", "#262628", "#343436", "#444446", "#565658", "#6c6c6e")
IRON = ramp("#0c0c0e", "#161618", "#202024", "#2c2c32", "#3a3a42")
EARTH = ramp("#0e0a08", "#18120e", "#221a14", "#2e241c")
SOUL = ramp("#0a3a4a", "#14607a", "#2a90b0", "#5ac4e0", "#a0eaff", "#e8fcff")


def shaders():
    return {
        "bronze": X.surf(BRONZE, 0.52, 1.4, 0.18, 0.2, rust=(EARTH, 0.18, 0.5)),
        "gold": X.surf(GOLD, 0.56, 1.5, 0.12, 0.26),
        "bone": X.surf(BONE, 0.55, 1.2, 0.16, 0.12, drip=(EARTH, 0.12)),
        "shroud": X.surf(SHROUD, 0.5, 1.0, 0.24, 0.0, holes=True, drip=(EARTH, 0.1)),
        "purple": X.surf(PURPLE, 0.5, 1.0, 0.22, 0.0, holes=True),
        "corpse": X.wrinkled(CORPSE, 1.1),
        "stone": X.surf(STONE, 0.5, 1.2, 0.2, 0.14, crust=(BRONZE, 0.2)),
        "iron": X.surf(IRON, 0.5, 1.3, 0.16, 0.18, rust=(EARTH, 0.3, 0.5)),
        "leather": X.surf(EARTH, 0.5, 1.1, 0.2, 0.04),
        "soul": X.glow(SOUL),
        "eye": X.glow(SOUL, 0.84, 0.14),
        "dark": X.dark(EARTH),
    }


GLOWS = {"soul", "eye"}


def skull(k, part, c, s=1.0, mat="bone", jaw=True):
    """a skull facing +z: cranium, cheekbones, sockets with the light in them, teeth"""
    cx, cy, cz = c
    k.blob(part, (cx, cy + 1.2 * s, cz), (3.0 * s, 3.0 * s, 3.2 * s), mat, "cranium", step=0.6)
    k.box(part, C(cx, cy - 1.6 * s, cz + 0.6 * s, 4.6 * s, 2.4 * s, 4.4 * s), mat, tag="cheeks")
    for sx in (-1, 1):
        k.box(part, C(cx + sx * 1.3 * s, cy - 0.2 * s, cz + 2.7 * s, 1.6 * s, 1.6 * s, 0.4), "dark", tag="socket")
        k.box(part, C(cx + sx * 1.3 * s, cy + 0.2 * s, cz + 2.8 * s, 0.8 * s, 0.8 * s, 0.3), "eye", tag="eye")
    k.box(part, C(cx, cy - 1.4 * s, cz + 2.8 * s, 0.8 * s, 1.0 * s, 0.3), "dark", tag="nose_hole")
    if jaw:
        k.box(part, C(cx, cy - 3.6 * s, cz + 0.8 * s, 3.8 * s, 1.6 * s, 3.6 * s), mat, tag="jaw")
        for i in range(5):
            k.box(part, C(cx - 1.6 * s + i * 0.8 * s, cy - 2.4 * s, cz + 2.7 * s, 0.5 * s, 0.9 * s, 0.3), mat, tag="teeth")


def ribs(k, part, y0, y1, w, d, glow=False, mat="bone"):
    """a rib cage: a spine, ribs curving round, the soul-light inside if glow"""
    k.limb(part, (0, y0, -d * 0.4), (0, y1, -d * 0.4), 1.6, mat, "spine")
    n = int((y1 - y0) / 2.2)
    for i in range(n):
        y = y1 - 1.0 - i * 2.2
        ww = w * (0.75 + 0.25 * math.sin(math.pi * (i + 1) / (n + 1)))
        k.box(part, C(0, y, 0, ww, 0.9, d), mat, tag="rib")
        k.box(part, C(0, y + 0.05, 0, ww - 1.6, 0.95, d - 1.6), "dark" if not glow else "soul", tag="rib_hollow")
    k.box(part, C(0, y0 + (y1 - y0) * 0.45, d * 0.5 - 0.2, 1.4, (y1 - y0) * 0.5, 0.6), mat, tag="sternum")
    if glow:
        k.blob(part, (0, y0 + (y1 - y0) * 0.55, 0), (w * 0.24, (y1 - y0) * 0.22, d * 0.24), "soul", "soul_fire", step=0.7)


def bone_legs(k, hips, top=19, knee=10.4, x=3.0, w=2.6):
    """a skeleton's legs: bare thigh and shin bones, knobs at the knees, bony feet"""
    for side, nm in ((1, "l"), (-1, "r")):
        xx = side * x
        th = k.part("thigh_" + nm, (xx, top, 0), (("x", -6), ("z", side * 3)), hips)
        sh = k.part("shin_" + nm, (xx, knee, 0), (("x", 8),), th)
        ft = k.part("foot_" + nm, (xx, 2.4, 0), (("x", -2),), sh)
        k.limb(th, (xx, top, 0), (xx, knee + 0.6, 0), w, "bone", "femur")
        k.box(th, C(xx, knee - 0.4, 0.2, w + 1.0, 2.0, w + 1.0), "bone", tag="knee")
        k.limb(sh, (xx, knee - 0.4, 0), (xx, 2.6, 0), w - 0.4, "bone", "shin")
        k.box(ft, C(xx, 0, 1.4, w + 1.2, 2.2, w + 4.0), "bone", tag="foot")
        for t in (-0.9, 0, 0.9):
            k.box(ft, C(xx + t, 0, w * 0.5 + 3.2, 0.6, 1.2, 1.4), "bone", tag="foot")


# ================================================================ the Ossipede (swarm)

def ossipede():
    """What crawls in the barrows: a centipede made of the vertebrae of the dead, fused end to end, each joint
    putting out a pair of rib-legs, a man's skull for its head and two ribs either side of it for mandibles."""
    k = X.Kit("ossipede")
    body, hd, ab, joints = quad(k, "bone", y=7, chest=((3, 6, 7), (6, 7, 8), (9.6, 6, 7)), haunch=((3, 5, 6), (6, 6, 7), (9, 5, 6)),
                                leg_w=1.6, foot_w=1.2, front_z=3, back_z=-9, x=4.0, head_at=(0, 8, 6), head_rot=-4, claw="bone", foot_len=3.0)
    for i, z in enumerate((5, 1, -3, -7, -11, -15, -19)):     # the vertebrae down its length, each with a pair of rib-legs
        part = body if z > -4 else ab
        r = 1.0 - max(0, -z - 6) * 0.03
        k.blob(part, (0, 7.4, z), (3.4 * r, 2.4 * r, 2.0), "bone", "vertebra", step=0.6)
        k.shard(part, (0, 9.4, z), (0, 1, -0.4), 2.6 * r, 1.2, mat="bone", tag="spine_spur")
        k.box(part, C(0, 7.2, z + 1.6, 2.0, 1.4, 1.4), "dark", tag="joint")
        for sx in (-1, 1):
            if z in (3, -9):
                continue
            k.limb(part, (sx * 2.6, 7.6, z), (sx * 6.4, 6.0, z + 0.6), 1.0, "bone", "rib_leg")
            k.limb(part, (sx * 6.4, 6.0, z + 0.6), (sx * 7.4, 0.4, z + 1.2), 0.8, "bone", "rib_leg")
    k.box(ab, C(0, 6.6, -21.6, 1.4, 1.4, 4.0), "bone", tag="tail")
    k.shard(ab, (0, 7.2, -23.4), (0, 0.6, -1), 4.4, 1.2, mat="bone", tag="tail_hook")
    skull(k, hd, (0, 9.4, 10.0), 1.0)
    for sx in (-1, 1):                            # rib mandibles, curving in
        k.limb(hd, (sx * 2.4, 6.4, 11.4), (sx * 3.6, 6.0, 14.6), 0.9, "bone", "mandible")
        k.limb(hd, (sx * 3.6, 6.0, 14.6), (sx * 1.6, 5.6, 17.0), 0.8, "bone", "mandible")
    k.blob(hd, (0, 7.6, 11.2), (1.4, 1.0, 1.4), "soul", "soul_breath", step=0.6)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Barrow Wight (guard)

def barrow_wight():
    """The king's housecarls, buried round him with their arms: skeletons in coats of green bronze scale, gold
    masks with shut eyes hammered over their skulls (the soul-light shows through the slits), crested helms with
    cheek-guards, a round bronze shield with a boss like a fist, and the leaf-bladed swords of the first smiths."""
    k = X.Kit("barrow_wight")
    hips = k.part("hips", (0, 20, 0))
    k.box(hips, C(0, 17.6, 0, 6.4, 3.4, 4.0), "bone", tag="pelvis")
    for i in range(4):                            # the scale skirt, rows of bronze scales
        k.box(hips, C(0, 11.0 + i * 2.2, 0, 11.4 - i * 0.3, 2.4, 8.0 - i * 0.2), "bronze", tag="scale_skirt")
        k.box(hips, C(0, 11.0 + i * 2.2, 3.9 - i * 0.1, 11.6 - i * 0.3, 0.5, 0.3), "dark", tag="scale_line")
    k.box(hips, C(0, 19.2, 0, 11.8, 1.6, 8.4), "leather", tag="belt")
    k.box(hips, C(0, 19.0, 4.3, 2.6, 2.0, 0.6), "gold", tag="buckle")
    bone_legs(k, hips)
    for side in (1, -1):                          # bronze greaves strapped to bare shins
        k.box(k.parts["shin_" + ("l" if side > 0 else "r")], C(side * 3.0, 3.4, 1.0, 3.6, 6.4, 2.6), "bronze", tag="greave")
    to = k.part("torso", (0, 20, 0), (("x", 5),), "hips")
    k.stack(to, 0, 0, [(20, 10.4, 7.2), (24, 11.6, 7.6), (29, 13.8, 8.4), (33.4, 14.0, 8.0)], "bronze", "scale_coat")
    for y in (21, 23.4, 25.8, 28.2, 30.6):        # the scales: offset rows
        for x in range(-5, 6, 2):
            k.box(to, C(x + (0.9 if int(y) % 2 else 0), y, 4.0 + (y - 21) * 0.08, 1.6, 1.6, 0.3), "bronze", tag="scale")
            k.box(to, C(x + (0.9 if int(y) % 2 else 0), y, 4.1 + (y - 21) * 0.08, 1.6, 0.3, 0.3), "dark", tag="scale_line")
    k.box(to, C(0, 26.0, 4.6, 3.6, 3.6, 0.6), "gold", tag="pectoral")
    k.box(to, C(0, 26.6, 4.9, 1.4, 1.4, 0.4), "soul", tag="pectoral_stone")
    for sx in (-1, 1):
        k.box(to, C(sx * 7.4, 31.0, 0, 3.6, 2.6, 7.4), "bronze", tag="shoulder_scale")
        k.box(to, C(sx * 7.6, 29.4, 0, 4.0, 1.6, 7.8), "bronze", tag="shoulder_scale")
    k.box(to, C(0, 21.4, -4.2, 12.0, 11.0, 0.6), "purple", tag="cloak")
    hd = k.part("head", (0, 33.4, 0.6), (("x", -4),), "torso")
    skull(k, hd, (0, 37.0, 0.8), 1.0)
    # the gold mask over the face: brows, a long nose, shut eyes with slits, a closed mouth
    k.box(hd, C(0, 33.6, 3.4, 5.4, 6.4, 0.7), "gold", tag="mask")
    k.box(hd, C(0, 38.4, 3.9, 5.8, 0.9, 0.6), "gold", tag="mask_brow")
    k.box(hd, C(0, 35.0, 3.9, 1.2, 3.0, 0.8), "gold", tag="mask_nose")
    eyes(k, hd, 37.5, 4.15, 1.4, 1.4, h=0.4)
    k.box(hd, C(0, 34.2, 4.1, 2.4, 0.4, 0.3), "dark", tag="mask_mouth")
    # the helm: a bronze cap, cheek-guards, a horsehair crest gone grey
    k.blob(hd, (0, 39.4, 0.6), (3.6, 2.6, 3.8), "bronze", "helm", step=0.6)
    for sx in (-1, 1):
        k.box(hd, C(sx * 3.4, 33.4, 1.6, 0.8, 5.4, 3.6), "bronze", tag="cheek_guard")
    k.box(hd, C(0, 41.6, -0.6, 1.0, 2.0, 8.4), "bronze", tag="crest_holder")
    for i in range(6):
        z = 3.4 - i * 1.6
        k.limb(hd, (0, 42.6, z), (0, 43.6 - abs(i - 2) * 0.5 - (i > 3) * 2.0, z - 1.4 - (i > 3) * 2.0), 1.4, "shroud", "crest", d=1.0)
    arms(k, to, 7.6, 31, "bone", {1: ((("x", -40), ("z", -8)), (("x", -40),)), -1: ((("x", -30), ("z", 8)), (("x", -46),))}, w=2.8)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        k.box(k.parts["fore_" + nm], C(side * 7.6, 17.0, 0, 3.6, 4.0, 3.6), "bronze", tag="bracer")
    sh = held(k, "shield", "l", (7.6, 13, 0.4), (("x", 80),))       # the round shield, boss out, facing front
    for i, (r, t) in enumerate(((7.4, 1.0), (6.6, 1.2), (4.0, 1.6))):
        k.box(sh, C(7.0, 13.0 - r, 2.8 + i * 0.6, r * 2, r * 2, t), "bronze" if i < 2 else "gold", tag="shield")
    for a in range(0, 360, 30):
        rr = math.radians(a)
        k.box(sh, C(7.0 + math.cos(rr) * 5.4, 13.0 + math.sin(rr) * 5.4 - 0.4, 4.0, 0.8, 0.8, 0.4), "gold", tag="shield_stud")
    k.shard(sh, (7.0, 13.0, 4.8), (0, 0, 1), 2.6, 2.4, mat="gold", tag="shield_boss")
    for sx in (-1, 1):
        k.box(sh, C(7.0 + sx * 3.4, 12.4 + sx * 3.0, 4.0, 0.6, 2.6, 0.5), "soul", tag="shield_rune")
    sw = held(k, "sword", "r", (-7.6, 13.6, 0.3), (("x", 84),))     # the leaf blade
    k.limb(sw, (-7.6, 9.6, 0.3), (-7.6, 15.2, 0.3), 1.2, "leather", "grip")
    k.box(sw, C(-7.6, 8.4, 0.3, 2.0, 1.4, 2.0), "gold", tag="pommel")
    k.box(sw, C(-7.6, 15.2, 0.3, 1.4, 1.2, 4.6), "gold", tag="guard")
    for i, w in enumerate((1.8, 2.4, 2.9, 3.2, 3.2, 2.9, 2.4, 1.6)):
        k.box(sw, C(-7.6, 16.4 + i * 2.0, 0.3, 0.8, 2.05, w), "bronze", tag="leaf_blade")
    k.box(sw, C(-7.6, 16.4, 0.3, 0.9, 15.0, 0.5), "gold", tag="midrib")
    k.shard(sw, (-7.6, 32.4, 0.3), (0, 1, 0), 2.6, 1.4, mat="bronze", tag="blade_tip")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Mound Brute (brute)

def mound_brute():
    """Some of the old kings buried giants with them. This one comes up out of the mound with the earth still in
    its mouth: grey-green dead flesh, a burial shroud in strips, grave chains wound round and round it with the
    lock still on, and in its fists its own headstone, cut with runes that burn."""
    k = X.Kit("mound_brute")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(13, 14.4, 10.0), (21, 15.4, 10.6)], "shroud", "loin")
    for i, x in enumerate((-5.4, -1.8, 1.8, 5.4)):
        k.box(hips, C(x, 6.0 + (i % 2) * 2.4, 5.0, 3.2, 8.0 - (i % 2) * 2.0, 0.6), "shroud", tag="shroud_strip")
    legs(k, hips, 20, 11.0, 4.6, "corpse", "corpse", knee_mat=None, lean=-4, bend=8, w=6.8, cuff=False)
    for side in (1, -1):
        sh = k.parts["shin_" + ("l" if side > 0 else "r")]
        for y in (4.0, 7.0):
            k.box(sh, C(side * 4.6, y, 0, 7.8, 1.0, 8.4), "shroud", tag="leg_wrap")
    to = k.part("torso", (0, 21, 0), (("x", 16),), "hips")
    k.stack(to, 0, 0, [(21, 15, 10.4), (26, 18, 11.6), (31, 22, 12.6), (35, 23, 12.4), (37.6, 18, 10)], "corpse", "chest")
    k.blob(to, (0, 34.0, -3.6), (8.4, 4.4, 4.0), "corpse", "hump", step=0.9)
    for y, tilt in ((24, 3.0), (28.6, -2.4), (33, 2.0)):       # grave chains wound round it
        for i in range(12):
            a = i * math.pi / 6
            x, z = math.cos(a) * (9.6 + (y - 24) * 0.25), math.sin(a) * 6.4
            k.box(to, C(x, y + math.cos(a) * tilt * 0.3, z, 2.0, 1.2, 1.2) if i % 2 else C(x, y + math.cos(a) * tilt * 0.3, z, 1.2, 1.4, 2.0), "iron", tag="grave_chain")
    k.box(to, C(4.0, 26.0, 6.8, 3.0, 3.6, 1.4), "iron", tag="padlock")
    k.box(to, C(4.0, 26.6, 7.6, 0.8, 1.2, 0.3), "dark", tag="keyhole")
    for x, y in ((-5, 30), (3, 31.6), (-2, 23.6)):
        k.box(to, C(x, y, 6.2, 2.0, 0.6, 0.4), "dark", tag="wound")
    k.box(to, C(0, 22.4, -6.2, 14.0, 13.0, 0.6), "shroud", tag="shroud_back")
    hd = k.part("head", (0, 37.0, 3.0), (("x", -18),), "torso")
    k.box(hd, C(0, 37.4, 4.4, 7.4, 7.6, 7.0), "corpse", tag="head")
    k.box(hd, C(0, 42.6, 6.6, 8.0, 1.6, 2.4), "corpse", tag="brow")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.8, 40.6, 7.8, 2.0, 1.6, 0.4), "dark", tag="socket")
        k.box(hd, C(sx * 1.8, 41.0, 7.9, 1.0, 0.8, 0.3), "eye", tag="eye")
    k.box(hd, C(0, 37.2, 7.4, 5.0, 2.6, 0.8), "dark", tag="maw")             # the mouth hanging open, earth in it
    k.box(hd, C(0, 37.0, 7.5, 3.0, 1.0, 0.6), "leather", tag="grave_earth")
    for x in (-2.0, -0.6, 0.8, 2.0):
        k.box(hd, C(x, 38.8, 7.7, 0.6, 1.0, 0.3), "bone", tag="teeth")
    k.box(hd, C(0, 36.2, 4.4, 8.4, 2.6, 7.6), "corpse", tag="jaw")
    k.box(hd, C(0, 40.2, 0.6, 8.0, 5.0, 6.0), "shroud", tag="shroud_hood")
    k.box(hd, C(0, 43.4, 2.6, 6.0, 1.6, 6.0), "shroud", tag="shroud_hood")
    arms(k, to, 12.6, 34, "corpse", {1: ((("x", -70), ("z", -16)), (("x", -30),)), -1: ((("x", -76), ("z", 16)), (("x", -24),))}, w=6.2, long=1.15)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        k.ring(k.parts["fore_" + nm], side * 12.6, 22.0, 0, 3.6, 1.0, "iron", "manacle", n=10, axis="y")
        k.chain(k.parts["fore_" + nm], (side * 12.6, 21.0, 2.0), (side * 13.4, 12.0, 4.0), 4, w=1.2)
    # the headstone, held up over its head in both hands: a round-topped slab, runes cut in it burning
    gs = held(k, "headstone", "r", (-6.0, 14.0, 0.4), (("x", 96), ("z", -10)))
    k.box(gs, C(0, 12.0, 0.4, 16.0, 20.0, 3.4), "stone", tag="headstone")
    k.blob(gs, (0, 32.0, 0.4), (8.0, 3.4, 1.7), "stone", "headstone_top", step=0.7)
    k.box(gs, C(0, 11.4, 0.4, 17.6, 1.6, 4.4), "stone", tag="headstone_foot")
    for x, y, w, h in ((-4.0, 26, 3.0, 0.8), (-4.0, 22, 0.8, 4.8), (1.0, 25, 4.4, 0.8), (3.0, 19, 0.8, 7.0), (-2.0, 16, 6.0, 0.8)):
        k.box(gs, C(x, y, 2.15, w, h, 0.3), "soul", tag="rune")
    k.box(gs, C(5.4, 14.0, 2.15, 0.4, 9.0, 0.3), "dark", tag="crack")
    k.box(gs, C(-6.4, 27.0, 2.1, 2.4, 3.4, 0.4), "bronze", tag="lichen")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.35)
    return k.s, k.parts


# ================================================================ the Wailing Shroud (caster)

def wailing_shroud():
    """The barrow-women who sang the kings down are still singing. A grave-shroud standing upright with nothing in
    it: its hood empty but for two eyes, its hem rotted to rags that don't touch the ground, two skeletal hands out
    of its sleeves, one holding up a lantern on a chain with a soul burning in it."""
    k = X.Kit("wailing_shroud")
    hips = k.part("hips", (0, 18, 0))
    for side, nm in ((1, "l"), (-1, "r")):        # legs it hasn't got (bones for the rig, nothing on them)
        th = k.part("thigh_" + nm, (side * 2.8, 18, 0), (), hips)
        sh = k.part("shin_" + nm, (side * 2.8, 10, 0), (), th)
        k.part("foot_" + nm, (side * 2.8, 3, 0), (), sh)
    k.stack(hips, 0, 0, [(5, 15.0, 13.0), (10, 13.4, 11.4), (18, 11.4, 9.0)], "shroud", "shroud_skirt", step=1.0)
    for i in range(14):                           # the rags of the hem, every length
        a = i * 2 * math.pi / 14
        L = 3.0 + (i * 7 % 5) * 1.0
        k.box(hips, C(math.cos(a) * 6.6, 5.2 - L, math.sin(a) * 5.6, 2.0, L, 0.6 + abs(math.cos(a)) * 1.0), "shroud", tag="hem_rag")
    k.box(hips, C(0, 2.0, 0, 4.0, 1.0, 4.0), "soul", tag="foot")       # a glow pooled under it (the ground marker)
    to = k.part("torso", (0, 18, 0), (("x", 8),), "hips")
    k.stack(to, 0, 0, [(18, 11.4, 9.0), (24, 11.0, 8.4), (30, 12.4, 8.8), (33, 11.0, 8.2)], "shroud", "shroud_body")
    k.box(to, C(0, 22.0, 4.6, 2.4, 9.0, 0.6), "purple", tag="burial_band")
    for y in (24.0, 28.0):
        k.box(to, C(0, y, 4.8, 3.0, 1.0, 0.4), "gold", tag="burial_gold")
    hd = k.part("head", (0, 33, 0.4), (("x", 6),), "torso")
    k.blob(hd, (0, 37.4, 0.0), (4.8, 5.4, 5.0), "shroud", "hood", step=0.7)
    k.shard(hd, (0, 41.4, -2.0), (0, 0.6, -1), 5.0, 3.0, mat="shroud", tag="hood_point")
    k.box(hd, C(0, 33.4, 3.4, 6.0, 7.0, 2.4), "dark", tag="hood_void")            # nothing in the hood
    eyes(k, hd, 37.4, 4.95, 1.4, 1.2, h=0.9)
    for i, (x, y) in enumerate(((-1.8, 33.6), (0, 32.8), (1.8, 33.6))):       # its wail: the light running out of it
        k.box(hd, C(x * 0.5, y + 1.0, 4.95, 0.5, 1.4, 0.3), "soul", tag="wail")
    k.box(hd, C(0, 37.8, 5.0, 6.2, 0.6, 0.4), "gold", tag="circlet")
    arms(k, to, 7.0, 31, "shroud", {1: ((("x", -70), ("z", -10)), (("x", -30),)), -1: ((("x", -20), ("z", 20)), (("x", -60),))}, w=3.6, glove="bone")
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        k.box(k.parts["fore_" + nm], C(side * 7.0, 13.6, 0, 5.2, 3.6, 5.2), "shroud", tag="sleeve_mouth")
        for t in (-1.0, 0, 1.0):                  # finger bones
            k.limb(k.parts["hand_" + nm], (side * 7.0 + t, 13.0, 1.4), (side * 7.0 + t * 1.3, 10.0, 2.4), 0.6, "bone", "finger")
    ln = held(k, "lantern", "l", (7.0, 12.0, 0.4), (("x", 0),))
    k.chain(ln, (7.0, 12.0, 1.6), (7.0, 5.0, 1.6), 4, mat="bronze", w=1.0)
    k.box(ln, C(7.0, -1.0, 1.6, 4.4, 1.0, 4.4), "bronze", tag="lantern")
    k.box(ln, C(7.0, 0.0, 1.6, 3.4, 4.6, 3.4), "soul", tag="lantern_flame")
    for dx in (-1.9, 1.9):
        for dz in (-1.9, 1.9):
            k.box(ln, C(7.0 + dx, 0.0, 1.6 + dz, 0.6, 4.6, 0.6), "bronze", tag="lantern_bar")
    k.box(ln, C(7.0, 4.6, 1.6, 4.4, 1.0, 4.4), "bronze", tag="lantern")
    k.shard(ln, (7.0, 5.6, 1.6), (0, 1, 0), 1.6, 2.0, mat="bronze", tag="lantern_top")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Barrow Reaper (skirmisher)

def barrow_reaper():
    """The ones who hunted for the old kings still hunt: stooped skeletons gone brown as roots, a stag's skull for a
    helm with the antlers still on it, a hunter's cape of rotten hide, and a bronze sickle in each hand, the edges
    worn bright."""
    k = X.Kit("barrow_reaper")
    hips = k.part("hips", (0, 19, 0))
    k.box(hips, C(0, 16.6, 0, 6.0, 3.4, 4.0), "bone", tag="pelvis")
    k.box(hips, C(0, 18.2, 0, 10.6, 1.6, 7.6), "leather", tag="belt")
    for i, x in enumerate((-3.8, -1.2, 1.4, 3.8)):
        k.box(hips, C(x, 9.0 + (i % 2) * 1.6, 3.6, 2.4, 9.0 - (i % 2) * 1.6, 0.6), "leather", tag="hide_flap")
    bone_legs(k, hips, top=18, knee=9.8, x=2.8, w=2.4)
    to = k.part("torso", (0, 19, 0), (("x", 26),), "hips")
    ribs(k, to, 19.0, 31.0, 9.4, 6.0)
    for sx in (-1, 1):
        k.box(to, C(sx * 5.6, 30.0, -0.6, 3.0, 2.0, 4.6), "bone", tag="shoulder_blade")
    # the cape of hide over its back, ragged, a bronze clasp
    k.box(to, C(0, 17.0, -4.0, 12.0, 15.6, 0.8), "leather", tag="cape")
    for i in range(5):
        k.box(to, C(-4.8 + i * 2.4, 13.6 + (i % 2) * 1.4, -4.0, 1.8, 3.6, 0.8), "leather", tag="cape_rag")
    k.blob(to, (0, 31.0, -1.6), (6.4, 1.6, 4.4), "leather", "cape_collar", step=0.7)
    k.box(to, C(0, 31.0, 3.0, 2.4, 2.4, 0.8), "bronze", tag="clasp")
    hd = k.part("head", (0, 31.0, 1.4), (("x", -22),), "torso")
    skull(k, hd, (0, 34.0, 2.0), 0.9)
    # the stag skull over it: a long face down past its own, antlers branching up and back
    k.box(hd, C(0, 36.4, 3.6, 4.0, 3.4, 5.6), "bone", tag="stag_skull")
    k.box(hd, C(0, 35.0, 7.4, 2.6, 2.0, 3.4), "bone", tag="stag_snout")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.8, 37.6, 6.4, 1.0, 1.2, 0.3), "dark", tag="stag_socket")
        base = (sx * 1.8, 39.4, 2.4)
        tines = [(sx * 4.4, 43.0, 0.4), (sx * 6.0, 47.0, -1.6), (sx * 7.0, 50.0, -3.4)]
        prev = base
        for i, t in enumerate(tines):
            k.limb(hd, prev, t, 1.2 - i * 0.2, "bone", "antler")
            k.limb(hd, t, (t[0] - sx * 0.6, t[1] + 2.6, t[2] + 1.6), 0.8, "bone", "tine")
            prev = t
    arms(k, to, 6.4, 30, "bone", {1: ((("x", -10), ("z", 34)), (("x", -60),)), -1: ((("x", 10), ("z", -40)), (("x", -50),))}, w=2.4, long=1.12)
    for side, nm in ((1, "l"), (-1, "r")):        # the sickles: a short grip, a crescent of bronze
        x = side * 6.4
        sk = held(k, "sickle_" + nm, nm, (x, 11.4, 0.3), (("x", 66 if side > 0 else 30),))
        k.limb(sk, (x, 7.0, 0.3), (x, 14.0, 0.3), 1.2, "leather", "grip")
        k.box(sk, C(x, 14.0, 0.3, 1.6, 1.2, 1.6), "gold", tag="ferrule")
        pts = [(x, 15.0, 0.3), (x, 19.4, 1.6), (x, 22.0, 4.4), (x, 22.0, 8.0), (x, 19.6, 10.4)]
        for (a, b), w in zip(zip(pts, pts[1:]), (2.0, 2.2, 2.0, 1.4)):
            k.limb(sk, a, b, 0.7, "bronze", "sickle_blade", d=w)
        k.shard(sk, pts[-1], (0, -0.8, 0.3), 2.2, 0.8, mat="gold", tag="sickle_point")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Barrow King (elite)

def barrow_king():
    """In the heart of every great mound sits a king who didn't stay down. Plate of bronze worked with gold, a cloak
    of royal purple rotted to cobwebs, a tall gold mask with the face of the man he was - calm, terrible - under a
    crown of bronze horns, his ribs bare at the breast where the soul burns, and across his knees the great leaf-
    bladed sword his housecarls carried before him."""
    k = X.Kit("barrow_king")
    hips = k.part("hips", (0, 21, 0))
    k.box(hips, C(0, 18.4, 0, 7.0, 3.6, 4.4), "bone", tag="pelvis")
    for i, y in enumerate((16.0, 12.6)):
        for sx in (-1, 1):
            k.box(hips, C(sx * 3.6, y, 4.0 + i * 0.3, 5.6, 3.6, 1.0), "bronze", tag="tasset")
            k.box(hips, C(sx * 3.6, y, 4.55 + i * 0.3, 5.8, 0.6, 0.4), "gold", tag="tasset_edge")
    k.stack(hips, 0, 0, [(8, 13.0, 9.6), (21, 12.0, 8.4)], "purple", "royal_skirt")
    k.box(hips, C(0, 20.0, 0, 12.6, 1.8, 9.2), "gold", tag="belt")
    bone_legs(k, hips, top=20, knee=10.8, x=3.4, w=2.8)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        k.box(k.parts["shin_" + nm], C(side * 3.4, 3.0, 0.6, 4.4, 7.4, 3.6), "bronze", tag="greave")
        k.box(k.parts["shin_" + nm], C(side * 3.4, 9.6, 1.2, 4.6, 1.4, 2.6), "gold", tag="greave_edge")
        k.box(k.parts["thigh_" + nm], C(side * 3.4, 12.6, 1.2, 4.0, 6.4, 2.4), "bronze", tag="cuisse")
    to = k.part("torso", (0, 21, 0), (("x", 4),), "hips")
    ribs(k, to, 21.0, 30.0, 10.6, 7.0, glow=True)
    # the breastplate opened at the middle, the ribs and the soul fire showing through
    for sx in (-1, 1):
        k.box(to, C(sx * 4.8, 21.0, 0.4, 3.4, 10.0, 7.8), "bronze", tag="breastplate")
        k.box(to, C(sx * 3.2, 21.0, 4.0, 0.6, 10.0, 0.6), "gold", tag="breastplate_edge")
    k.stack(to, 0, 0, [(30, 15.4, 9.0), (34, 17.0, 9.4), (36, 14.0, 8.4)], "bronze", "gorget_plate")
    for x in range(-6, 7, 3):
        k.box(to, C(x, 32.0, 4.6, 1.2, 1.2, 0.4), "gold", tag="gorget_stud")
    for sx in (-1, 1):
        k.blob(to, (sx * 9.4, 34.4, 0), (4.6, 3.4, 5.2), "bronze", "pauldron", step=0.7)
        k.box(to, C(sx * 10.0, 31.0, 0, 6.0, 1.4, 9.0), "gold", tag="pauldron_edge")
        k.shard(to, (sx * 10.4, 37.0, 0), (sx * 0.6, 1, 0), 3.4, 1.6, mat="gold", tag="pauldron_horn")
    cl = k.part("cloak", (0, 35, -5.0), (("x", 5),), to, bone=False)
    for i, x in enumerate((-6.0, -3.0, 0.0, 3.0, 6.0)):
        L = 32.0 - (i * 3 % 4) * 2.0
        k.box(cl, C(x, 35.0 - L, -5.6, 3.0, L, 0.8), "purple", tag="cloak")
        k.box(cl, C(x + 0.6, 35.0 - L, -5.9, 1.0, 3.0, 0.4), "dark", tag="cloak_hole")
    k.box(cl, C(0, 33.6, -6.0, 15.0, 1.4, 1.0), "gold", tag="cloak_bar")
    hd = k.part("head", (0, 36.0, 0.6), (("x", -4),), "torso")
    skull(k, hd, (0, 39.4, 0.6), 1.1)
    # the tall mask: a long gold face, eyes shut, a beard of gold wire under it
    k.box(hd, C(0, 34.4, 3.6, 6.0, 8.6, 0.8), "gold", tag="mask")
    k.box(hd, C(0, 41.4, 4.1, 6.4, 1.0, 0.6), "gold", tag="mask_brow")
    k.box(hd, C(0, 37.4, 4.2, 1.2, 3.6, 0.8), "gold", tag="mask_nose")
    eyes(k, hd, 40.5, 4.45, 1.5, 1.6, h=0.4)
    k.box(hd, C(0, 36.0, 4.4, 2.6, 0.4, 0.3), "dark", tag="mask_mouth")
    for x in (-2.0, -0.7, 0.7, 2.0):
        k.box(hd, C(x, 30.6, 3.8 + (2.0 - abs(x)) * 0.3, 0.8, 4.4 - abs(x) * 0.6, 0.6), "gold", tag="mask_beard")
    # the crown: a bronze band, gold points, two great horns sweeping up
    k.box(hd, C(0, 42.6, 0.6, 8.4, 1.8, 8.4), "bronze", tag="crown_band")
    for i in range(8):
        a = i * math.pi / 4
        k.shard(hd, (math.sin(a) * 4.0, 44.2, 0.6 + math.cos(a) * 4.0), (0, 1, 0), 2.4 if i % 2 else 3.4, 1.2, mat="gold", tag="crown_point")
    for sx in (-1, 1):
        pts = [(sx * 4.0, 43.6, 0.4), (sx * 7.4, 46.0, -0.4), (sx * 8.6, 50.4, -1.4), (sx * 7.4, 54.0, -1.0)]
        for (a, b), w in zip(zip(pts, pts[1:]), (2.4, 1.9, 1.4)):
            k.limb(hd, a, b, w, "bronze", "crown_horn")
        k.shard(hd, pts[-1], (-sx * 0.3, 1, 0.2), 2.4, 1.1, mat="gold", tag="crown_horn_tip")
    k.box(hd, C(0, 43.0, 4.8, 1.6, 1.6, 0.4), "soul", tag="crown_stone")
    arms(k, to, 9.6, 33, "bone", {1: ((("x", -36), ("z", -20)), (("x", -40),)), -1: ((("x", -32), ("z", 18)), (("x", -44),))}, w=3.0)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        k.box(k.parts["fore_" + nm], C(side * 9.6, 17.8, 0, 4.4, 5.0, 4.4), "bronze", tag="vambrace")
        k.box(k.parts["fore_" + nm], C(side * 9.6, 22.4, 0, 4.6, 0.8, 4.6), "gold", tag="vambrace_edge")
        k.box(k.parts["hand_" + nm], C(side * 9.6, 13.4, 0.3, 3.8, 3.6, 4.2), "bronze", tag="gauntlet")
    gs = held(k, "greatsword", "r", (-9.6, 14.0, 0.3), (("x", 78), ("z", -16)))
    k.limb(gs, (-9.6, 6.0, 0.3), (-9.6, 15.8, 0.3), 1.6, "leather", "grip")
    k.box(gs, C(-9.6, 4.4, 0.3, 2.6, 2.2, 2.6), "gold", tag="pommel")
    k.box(gs, C(-9.6, 15.8, 0.3, 9.0, 1.6, 2.0), "gold", tag="guard")
    for sx in (-1, 1):
        k.shard(gs, (-9.6 + sx * 4.4, 16.4, 0.3), (sx * 0.4, 1, 0), 2.6, 1.0, mat="gold", tag="guard_horn")
    for i, w in enumerate((2.6, 3.4, 4.2, 4.8, 5.2, 5.2, 4.8, 4.2, 3.4, 2.4)):    # the leaf blade, broad at two-thirds
        k.box(gs, C(-9.6, 17.4 + i * 2.4, 0.3, w, 2.45, 1.0), "bronze", tag="leaf_blade")
    k.box(gs, C(-9.6, 17.4, 0.9, 0.8, 22.0, 0.3), "gold", tag="midrib")
    for y in (21.0, 26.0, 31.0):
        k.box(gs, C(-9.6, y, 0.95, 1.6, 1.6, 0.3), "soul", tag="blade_rune")
    k.shard(gs, (-9.6, 41.4, 0.3), (0, 1, 0), 3.4, 2.0, mat="bronze", tag="blade_tip")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.15)
    return k.s, k.parts


MOBS = {
    "ossipede": dict(make=ossipede, rig="crawler", ent=(1.0, 0.9), stats=dict(hp=24, speed=0.34, dmg=6, armor=3, kb=0)),
    "barrow_wight": dict(make=barrow_wight, ent=(0.9, 2.8), stats=dict(hp=56, speed=0.24, dmg=9, armor=9, kb=0.3)),
    "mound_brute": dict(make=mound_brute, ent=(1.7, 4.0), stats=dict(hp=180, speed=0.19, dmg=18, armor=6, kb=1.0)),
    "wailing_shroud": dict(make=wailing_shroud, ent=(0.9, 2.7), stats=dict(hp=38, speed=0.22, dmg=7, armor=2, kb=0)),
    "barrow_reaper": dict(make=barrow_reaper, ent=(0.8, 2.6), stats=dict(hp=40, speed=0.33, dmg=8, armor=3, kb=0)),
    "barrow_king": dict(make=barrow_king, ent=(1.1, 3.4), stats=dict(hp=340, speed=0.24, dmg=15, armor=13, kb=0.6), key=True),
}
