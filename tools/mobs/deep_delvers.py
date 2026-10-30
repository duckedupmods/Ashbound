"""The Deep Delvers: a miners' guild that dug too deep and never came back up, who hold the world's mines, foundries,
factories, bunkers and diggers' camps, built by hand (tools/vox2.py). Squat and broad from a life in the tunnels,
gas masks and smoked goggles, riveted gunmetal, oxide-red guild paint, leather aprons black with oil, and the cold
blue-white of their arc lamps and drills. (Not the Weeping Mine's crystal-sick miners, not the Foundry's fire.)

    drill_mole      swarm   a digging machine the size of a hog: a spinning drill for a nose, claw-feet, lamp eyes
    delver          guard   a guild miner: a hard hat and its lamp, a twin-filter gas mask, a riveted shoulder plate,
                            a mattock
    blaster         ranged  the charge-man: a welding mask, a satchel and a bandolier of blasting sticks, a lit fuse
    tunnel_rat      skirm   bent double: a headlamp, a respirator, rope coiled on him, a climbing pick in each hand
    steam_driller   brute   a giant in boiler-plate with the boiler on his back, a great drill for his right arm and
                            a hydraulic claw for his left
    pit_boss        elite   the guild's master: a riveted iron greatcoat, an iron helm with a T-slit and two lamps,
                            smokestacks over his shoulders, a drill-lance

    python tools/monsterforge.py deep_delvers --preview ; python tools/mobsheet.py deep_delvers
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import grow
from _folk import lit, eyes, straps, legs, arms, held, quad

GUN = ramp("#0a0b0c", "#121416", "#1c1f22", "#282c30", "#363b40", "#484e54", "#60676e")
OXIDE = ramp("#1e0806", "#340e0a", "#4e160e", "#6a2014", "#86301c", "#a04428")
LEATHER = ramp("#0c0806", "#160f0b", "#211710", "#2c2016", "#3a2a1c", "#4a3624")
SOOT = ramp("#060606", "#0c0c0c", "#141414", "#1c1c1c", "#262626")
BRASS = ramp("#1e1406", "#38260c", "#584012", "#7a5a1c", "#9c7628", "#bc9238")
SKIN = ramp("#1e1612", "#2e221c", "#403026", "#544032", "#6a5240")
ROPE = ramp("#1c160c", "#2e2414", "#42341e", "#584628", "#6e5a34")
GLASS = ramp("#081014", "#0e1a20", "#16262e", "#20343e")
ARC = ramp("#0a2a44", "#145078", "#2a80b4", "#64b8e8", "#b4e4ff", "#f0faff")
WICK = ramp("#5a1a04", "#9a3a08", "#e06a14", "#ffa040", "#ffe0a0")
CANVAS = ramp("#1a1a14", "#28281e", "#38382a", "#4a4a38", "#5c5c48")


def shaders():
    return {
        "gun": X.surf(GUN, 0.54, 1.5, 0.12, 0.26, rust=(OXIDE, 0.12, 0.6)),
        "oxide": X.surf(OXIDE, 0.52, 1.3, 0.2, 0.16, rust=(SOOT, 0.22, 0.5)),
        "leather": X.surf(LEATHER, 0.5, 1.2, 0.22, 0.06, drip=(SOOT, 0.14)),
        "soot": X.surf(SOOT, 0.5, 1.0, 0.2, 0.02),
        "brass": X.surf(BRASS, 0.56, 1.4, 0.12, 0.24),
        "skin": X.wrinkled(SKIN, 0.9),
        "rope": X.surf(ROPE, 0.5, 1.1, 0.26, 0.02, stripe=2),
        "glass": X.surf(GLASS, 0.6, 1.6, 0.04, 0.3),
        "canvas": X.surf(CANVAS, 0.5, 1.0, 0.24, 0.0, holes=True),
        "steel": X.surf(GUN, 0.7, 1.6, 0.06, 0.32),
        "iron": X.surf(GUN, 0.5, 1.4, 0.16, 0.2, rust=(OXIDE, 0.3, 0.5)),
        "arc": X.glow(ARC),
        "eye": X.glow(ARC, 0.84, 0.14),
        "wick": X.glow(WICK),
        "dark": X.dark(SOOT),
    }


GLOWS = {"arc", "eye", "wick"}


def rivet_row(k, part, a, b, n, z_off=0.3, mat="brass"):
    for i in range(n):
        t = i / max(1, n - 1)
        k.box(part, C(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t + z_off, 0.7, 0.7, 0.4), mat, tag="rivet")


def gas_mask(k, part, y, z, s=1.0, filters=2):
    """a mask over the lower face facing +z: a snout, the filter cans either side of it, the goggles above"""
    k.box(part, C(0, y, z, 5.6 * s, 3.4 * s, 1.4), "leather", tag="mask")
    k.shard(part, (0, y + 1.2 * s, z + 1.0), (0, -0.2, 1), 2.4 * s, 2.6 * s, mat="leather", tag="mask_snout")
    for sx in ((-1, 1) if filters == 2 else (0,)):
        cx = sx * 2.2 * s
        k.limb(part, (cx, y + 0.6 * s, z + 1.2), (cx * 1.4, y - 0.6 * s, z + 3.4 * s), 2.0 * s, "gun", "filter")
        k.box(part, C(cx * 1.4, y - 1.2 * s, z + 3.0 * s, 2.2 * s, 0.6, 2.2 * s), "oxide", tag="filter_cap")
    for sx in (-1, 1):                            # goggles: brass rims, smoked lenses, the light behind them
        k.box(part, C(sx * 1.5 * s, y + 3.2 * s, z - 0.2, 2.4 * s, 2.2 * s, 1.0), "brass", tag="goggle_rim")
        k.box(part, C(sx * 1.5 * s, y + 3.5 * s, z + 0.5, 1.6 * s, 1.5 * s, 0.4), "eye", tag="eye")
    k.box(part, C(0, y + 3.8 * s, z - 0.6, 7.0 * s, 0.8 * s, 1.0), "leather", tag="goggle_strap")


def hard_hat(k, part, c, s=1.0, lamp=True):
    cx, cy, cz = c
    k.stack(part, cx, cz, [(cy, 7.4 * s, 7.6 * s), (cy + 1.6 * s, 7.0 * s, 7.2 * s), (cy + 3.0 * s, 5.4 * s, 5.6 * s)], "oxide", "hard_hat", step=0.8)
    k.box(part, C(cx, cy - 0.4, cz + 0.6, 9.0 * s, 0.8, 9.6 * s), "oxide", tag="hat_brim")
    k.box(part, C(cx, cy + 3.0 * s, cz, 1.0 * s, 0.8, 6.0 * s), "gun", tag="hat_ridge")
    if lamp:
        k.box(part, C(cx, cy + 0.8 * s, cz + 3.8 * s, 2.6 * s, 2.4 * s, 1.4), "brass", tag="hat_lamp")
        k.box(part, C(cx, cy + 1.2 * s, cz + 4.6 * s, 1.8 * s, 1.6 * s, 0.4), "arc", tag="lamp_lens")


# ================================================================ the Drill Mole (swarm)

def drill_mole():
    """The guild built them to open new seams; down there nobody turned them off. A machine the size of a hog, a
    riveted gunmetal hull painted guild red, a spiralling drill for a nose, four short legs with digging claws,
    two arc lamps for eyes, an exhaust stack coughing on its back."""
    k = X.Kit("drill_mole")
    body, hd, ab, joints = quad(k, "gun", y=10, chest=((4, 10, 11), (8, 12, 12), (12.4, 10.6, 11)), haunch=((4, 9.6, 9), (8, 11, 10), (12, 9.4, 9)),
                                leg_w=3.4, foot_w=2.8, front_z=4, back_z=-6, x=5.4, head_at=(0, 9, 8), head_rot=-2, claw="steel", foot_len=4.6)
    k.box(body, C(0, 12.6, 0.4, 10.4, 1.2, 11.6), "oxide", tag="hull_paint")
    k.box(ab, C(0, 12.0, -6.0, 9.8, 1.2, 9.6), "oxide", tag="hull_paint")
    for sx in (-1, 1):
        rivet_row(k, body, (sx * 5.4, 9.0, -4.0), (sx * 5.4, 9.0, 5.0), 5, 0)
        k.box(body, C(sx * 6.0, 4.6, 0, 0.8, 4.0, 11.0), "gun", tag="skirt_plate")
    k.limb(ab, (2.6, 12.0, -8.0), (2.6, 19.0, -9.4), 2.0, "gun", "exhaust")
    k.box(ab, C(2.6, 18.6, -9.6, 2.8, 1.2, 2.8), "soot", tag="exhaust_mouth")
    k.box(ab, C(-2.6, 12.4, -8.0, 4.0, 3.0, 4.0), "brass", tag="tank")
    # the head: a blunt housing, the lamps, then the drill turning out of it
    k.box(hd, C(0, 4.0, 10.4, 9.6, 9.0, 5.4), "gun", tag="drill_housing")
    k.box(hd, C(0, 4.0, 15.6, 10.2, 9.6, 0.8), "oxide", tag="housing_ring")
    for sx in (-1, 1):
        k.box(hd, C(sx * 3.4, 10.4, 12.6, 2.6, 2.2, 1.6), "brass", tag="lamp")
        k.box(hd, C(sx * 3.4, 10.6, 13.5, 1.8, 1.6, 0.4), "eye", tag="eye")
    for i in range(6):                            # the drill: stepped rings narrowing, a spiral ridge round them
        r = 4.0 - i * 0.62
        z = 16.4 + i * 1.8
        k.box(hd, C(0, 8.6 - r, z, r * 2, r * 2, 1.85), "steel", tag="drill")
        a = i * 1.1
        k.box(hd, C(math.cos(a) * r, 8.6 + math.sin(a) * r - 0.5, z + 0.2, 1.0, 1.0, 1.6), "gun", tag="drill_flute")
    k.shard(hd, (0, 8.6, 27.0), (0, 0, 1), 3.0, 1.2, mat="steel", tag="drill_tip")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Delver (guard)

def delver():
    """The guild's diggers: short, broad as a door, the gas mask on so long it's grown to the face. A red hard hat
    with its lamp, smoked goggles lit from behind, a riveted plate on the shoulder that takes the rockfall, an apron
    of leather, a chain of tags round the neck - and a mattock that has broken more than rock."""
    k = X.Kit("delver")
    hips = k.part("hips", (0, 15, 0))
    k.stack(hips, 0, 0, [(8, 13.0, 9.0), (15, 13.6, 9.4)], "canvas", "trousers")
    k.box(hips, C(0, 14.0, 0, 14.4, 2.2, 10.2), "leather", tag="belt")
    k.box(hips, C(0, 13.8, 5.2, 2.6, 2.6, 0.6), "brass", tag="buckle")
    k.box(hips, C(0, 5.6, 4.6, 8.6, 9.4, 0.8), "leather", tag="apron")
    for sx in (-1, 1):
        k.box(hips, C(sx * 7.0, 9.6, 1.0, 2.0, 4.0, 3.4), "leather", tag="tool_pouch")
    legs(k, hips, 14, 7.4, 3.8, "canvas", "leather", knee_mat="gun", lean=-4, bend=6, w=6.0, toe="steel")
    to = k.part("torso", (0, 15, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(15, 13.6, 9.4), (20, 15.6, 10.4), (25, 18.0, 11.0), (29, 18.4, 10.6)], "canvas", "jacket")
    k.box(to, C(0, 15.4, 4.9, 9.4, 10.0, 0.8), "leather", tag="apron_bib")
    k.box(to, C(0, 22.0, 5.4, 4.6, 3.0, 0.4), "oxide", tag="guild_mark")
    k.box(to, C(0, 22.8, 5.7, 2.0, 1.4, 0.3), "dark", tag="guild_mark")
    k.blob(to, (-8.4, 27.6, 0), (4.6, 3.0, 5.4), "gun", "rock_plate", step=0.8)       # the shoulder plate, right side
    rivet_row(k, to, (-12.0, 26.0, 3.6), (-5.0, 29.0, 3.6), 4, 0.6)
    k.box(to, C(-9.0, 24.4, 0, 6.0, 1.6, 9.6), "gun", tag="plate_lame")
    k.blob(to, (8.0, 27.0, 0), (3.4, 2.4, 4.4), "leather", "shoulder", step=0.7)
    for i in range(4):                            # the tag chain
        k.box(to, C(-1.8 + i * 1.2, 25.4 - abs(i - 1.5) * 0.8, 5.6, 0.8, 1.2, 0.3), "brass", tag="tag")
    k.box(to, C(0, 13.6, -5.2, 8.0, 9.0, 4.0), "leather", tag="pack")
    k.ring(to, 0, 23.6, -6.0, 2.6, 0.9, "rope", "rope_coil", n=10, axis="z")
    hd = k.part("head", (0, 29, 1.6), (("x", -14),), "torso")
    k.box(hd, C(0, 29.4, 1.8, 7.0, 7.0, 6.8), "skin", tag="head")
    gas_mask(k, hd, 29.6, 5.2)
    k.box(hd, C(0, 33.8, -1.0, 7.4, 2.0, 2.4), "leather", tag="neck_flap")
    hard_hat(k, hd, (0, 35.6, 1.8))
    arms(k, to, 10.2, 27, "canvas", {1: ((("x", -40), ("z", -6)), (("x", -40),)), -1: ((("x", -66), ("z", 8)), (("x", -36),))}, glove="leather", w=5.0, long=0.95)
    for side in (1, -1):
        k.box(k.parts["fore_" + ("l" if side > 0 else "r")], C(side * 10.2, 13.8, 0, 5.6, 2.4, 5.6), "leather", tag="gauntlet_cuff")
    mt = held(k, "mattock", "r", (-10.2, 9.6, 0.4), (("x", 110),))
    k.limb(mt, (-10.2, 0.0, 0.4), (-10.2, 26.0, 0.4), 1.8, "rope", "haft")
    for y in (3.0, 6.0):
        k.box(mt, C(-10.2, y, 0.4, 2.4, 1.2, 2.4), "leather", tag="haft_wrap")
    k.box(mt, C(-10.2, 24.4, 0.4, 3.4, 4.0, 3.4), "gun", tag="mattock_eye")
    k.limb(mt, (-10.2, 26.4, 1.8), (-10.2, 24.0, 9.0), 2.2, "steel", "mattock_pick", d=1.8)
    k.shard(mt, (-10.2, 24.0, 9.0), (0, -0.5, 1), 2.6, 1.4, mat="steel", tag="pick_point")
    k.box(mt, C(-10.2, 22.4, -6.4, 1.4, 5.2, 4.8), "steel", tag="mattock_blade")
    k.box(mt, C(-10.2, 25.6, -2.2, 2.6, 1.2, 4.2), "oxide", tag="guild_paint")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Blaster (ranged)

def blaster():
    """The charge-man opens the rock the quick way and the guild still sends him first. A welding mask with one
    blue slit, a canvas coat scorched to the elbows, a satchel and a bandolier of red blasting sticks, a lit fuse
    burning in his fist, and a hand missing two fingers."""
    k = X.Kit("blaster")
    hips = k.part("hips", (0, 16, 0))
    k.stack(hips, 0, 0, [(6, 13.4, 10.0), (16, 12.6, 9.0)], "canvas", "coat_skirt")
    k.box(hips, C(0, 6.0, 5.0, 12.0, 1.0, 0.6), "soot", tag="scorch")
    k.box(hips, C(0, 15.0, 0, 13.4, 2.0, 9.6), "leather", tag="belt")
    k.box(hips, C(-6.4, 9.4, 2.6, 3.6, 5.6, 4.4), "leather", tag="satchel")
    k.box(hips, C(-6.4, 14.4, 2.6, 3.8, 1.4, 4.6), "leather", tag="satchel_flap")
    for i in range(3):
        k.box(hips, C(-7.4 + i * 1.0, 15.4, 2.2 + i * 0.6, 0.8, 3.0, 0.8), "oxide", tag="stick")
    legs(k, hips, 15, 8.0, 3.6, "canvas", "leather", knee_mat="leather", lean=-6, bend=8, w=5.6, toe="steel")
    to = k.part("torso", (0, 16, 0), (("x", 8),), "hips")
    k.stack(to, 0, 0, [(16, 12.6, 9.0), (21, 14.4, 9.8), (26, 16.6, 10.4), (29.4, 16.2, 10.0)], "canvas", "coat")
    for sx in (-1, 1):                            # two bandoliers crossed, red sticks in every loop
        a, b = (sx * 7.4, 29.0, 5.0), (-sx * 6.2, 16.4, 5.0)
        k.limb(to, a, b, 2.2, "leather", "bandolier", d=0.8)
        for t in (0.15, 0.3, 0.45, 0.6, 0.75, 0.9):
            p = tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
            k.box(to, C(p[0], p[1] - 1.6, p[2] + 0.6, 1.0, 3.2, 1.0), "oxide", tag="stick")
            k.box(to, C(p[0], p[1] + 1.6, p[2] + 0.6, 0.3, 0.8, 0.3), "rope", tag="fuse")
    for sx in (-1, 1):
        k.blob(to, (sx * 8.0, 27.6, 0), (3.2, 2.4, 4.2), "canvas", "shoulder", step=0.7)
    k.box(to, C(4.6, 20.0, 5.0, 3.0, 4.0, 0.3), "soot", tag="scorch")
    hd = k.part("head", (0, 29.4, 1.2), (("x", -8),), "torso")
    k.box(hd, C(0, 29.8, 1.2, 6.8, 7.0, 6.6), "skin", tag="head")
    # the welding mask: a flat iron face tipped down over it, one dark slit with the blue behind
    k.box(hd, C(0, 29.4, 4.6, 7.8, 8.6, 1.4), "gun", tag="weld_mask")
    k.box(hd, C(0, 28.4, 5.8, 5.6, 2.4, 1.4), "gun", tag="weld_chin")
    k.box(hd, C(0, 33.6, 6.0, 5.6, 1.4, 0.6), "glass", tag="weld_slit")
    k.box(hd, C(0, 33.8, 6.2, 4.6, 0.9, 0.3), "eye", tag="eye")
    for sx in (-1, 1):
        k.box(hd, C(sx * 4.0, 33.6, 2.0, 1.2, 1.6, 1.6), "brass", tag="mask_pivot")
    k.box(hd, C(0, 37.4, 3.2, 1.2, 1.2, 1.4), "oxide", tag="mask_stripe")
    k.blob(hd, (0, 36.4, 0.4), (3.6, 1.6, 3.6), "leather", "cap", step=0.6)
    arms(k, to, 8.4, 27, "canvas", {1: ((("x", -100), ("z", -10)), (("x", -20),)), -1: ((("x", -30), ("z", 10)), (("x", -40),))}, glove="leather", w=4.0)
    for side in (1, -1):
        k.box(k.parts["fore_" + ("l" if side > 0 else "r")], C(side * 8.4, 13.4, 0, 4.6, 2.0, 4.6), "soot", tag="scorch")
    # the lit stick in his raised left hand, the fuse spitting
    st = held(k, "charge", "l", (8.4, 10.0, 0.4), (("x", 0),))
    k.box(st, C(8.4, 10.0, 2.4, 1.8, 5.6, 1.8), "oxide", tag="charge_stick")
    k.box(st, C(8.4, 12.0, 2.4, 2.0, 0.8, 2.0), "rope", tag="charge_band")
    k.limb(st, (8.4, 15.6, 2.4), (9.0, 17.6, 3.0), 0.4, "rope", "fuse")
    k.blob(st, (9.0, 18.0, 3.0), (0.9, 0.9, 0.9), "wick", "spark", step=0.4)
    for d in ((1, 1, 0), (-1, 1, 0.5), (0.3, 1, -1)):
        k.shard(st, (9.0, 18.0, 3.0), d, 1.4, 0.4, mat="wick", tag="spark")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Tunnel Rat (skirmisher)

def tunnel_rat():
    """The ones who go into the cracks first: bent nearly double from a life in crawlways, a leather cap with a lamp
    strapped to it, a respirator snout, rope coiled over the shoulder, knee pads worn through, and a climbing pick
    in each fist that goes into rock - or anything softer - and holds."""
    k = X.Kit("tunnel_rat")
    hips = k.part("hips", (0, 16, 0))
    k.stack(hips, 0, 0, [(10, 11.0, 8.0), (16, 11.0, 8.0)], "leather", "breeches")
    k.box(hips, C(0, 15.0, 0, 12.0, 1.6, 8.8), "rope", tag="rope_belt")
    for sx in (-1, 1):
        k.box(hips, C(sx * 5.8, 10.4, 0.6, 1.6, 4.0, 2.6), "leather", tag="pouch")
    legs(k, hips, 15, 8.0, 3.2, "leather", "leather", knee_mat="oxide", lean=-22, bend=34, w=5.0, toe="steel")
    to = k.part("torso", (0, 16, 0), (("x", 34),), "hips")
    k.stack(to, 0, 0, [(16, 11.0, 8.0), (21, 12.0, 8.4), (26, 13.4, 8.8), (29, 13.0, 8.4)], "canvas", "shirt")
    k.box(to, C(0, 17.0, 4.3, 10.0, 11.0, 0.6), "leather", tag="harness")
    k.ring(to, -3.0, 24.0, 0, 6.4, 1.6, "rope", "rope_coil", n=16, axis="x")       # the coil over his right shoulder
    k.box(to, C(0, 17.0, -4.8, 7.0, 8.6, 3.0), "leather", tag="bedroll")
    k.box(to, C(0, 25.4, -4.4, 8.0, 2.6, 3.4), "canvas", tag="bedroll_tie")
    hd = k.part("head", (0, 29, 1.2), (("x", -40),), "torso")
    k.box(hd, C(0, 29.4, 1.4, 6.2, 6.4, 6.4), "skin", tag="head")
    k.box(hd, C(0, 29.0, 4.6, 4.6, 3.0, 1.2), "leather", tag="respirator")
    k.limb(hd, (0, 29.6, 5.4), (0, 28.4, 8.0), 2.0, "gun", "respirator_snout")
    k.box(hd, C(0, 27.6, 7.6, 2.4, 1.2, 1.2), "oxide", tag="snout_cap")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.4, 32.4, 4.6, 2.0, 1.6, 0.8), "brass", tag="goggle_rim")
        k.box(hd, C(sx * 1.4, 32.6, 5.2, 1.3, 1.1, 0.3), "eye", tag="eye")
    k.blob(hd, (0, 34.4, 0.6), (3.6, 1.8, 3.8), "leather", "cap", step=0.6)
    k.box(hd, C(0, 34.0, 4.2, 2.4, 2.2, 1.4), "brass", tag="cap_lamp")
    k.box(hd, C(0, 34.4, 5.0, 1.6, 1.4, 0.4), "arc", tag="lamp_lens")
    for sx in (-1, 1):
        k.box(hd, C(sx * 3.4, 29.0, 0.4, 1.4, 4.0, 3.4), "leather", tag="ear_flap")
    arms(k, to, 7.4, 27, "canvas", {1: ((("x", -70), ("z", 20)), (("x", -40),)), -1: ((("x", -40), ("z", -26)), (("x", -60),))}, glove="leather", w=3.6, long=1.1)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.4
        pk = held(k, "pick_" + nm, nm, (x, 9.0, 0.3), (("x", 70 if side > 0 else 40),))
        k.limb(pk, (x, 5.0, 0.3), (x, 17.0, 0.3), 1.4, "rope", "pick_haft")
        k.box(pk, C(x, 4.0, 0.3, 1.8, 1.4, 1.8), "gun", tag="pick_cap")
        k.box(pk, C(x, 16.4, 0.3, 2.0, 2.0, 2.4), "gun", tag="pick_head")
        k.limb(pk, (x, 17.4, 1.4), (x, 15.4, 6.6), 1.4, "steel", "pick_blade", d=1.0)
        k.shard(pk, (x, 15.4, 6.6), (0, -0.7, 0.6), 1.8, 0.9, mat="steel", tag="pick_point")
        k.box(pk, C(x, 16.6, -2.2, 1.2, 1.8, 1.6), "steel", tag="pick_hammer")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Steam Driller (brute)

def steam_driller():
    """When a seam won't give, the guild sends the driller: a giant riveted into boiler-plate with the boiler itself
    on his back, its stack smoking, gauges on his chest, his right arm gone into a great drill as long as he is tall
    and his left into a hydraulic claw that crushes ore - and what else it gets."""
    k = X.Kit("steam_driller")
    hips = k.part("hips", (0, 18, 0))
    k.stack(hips, 0, 0, [(9, 16.0, 11.0), (18, 16.6, 11.6)], "gun", "skirt_plate")
    k.box(hips, C(0, 17.0, 0, 17.4, 2.4, 12.4), "oxide", tag="belt_plate")
    rivet_row(k, hips, (-7.4, 18.2, 6.2), (7.4, 18.2, 6.2), 6, 0.2)
    legs(k, hips, 17, 9.0, 4.8, "gun", "gun", knee_mat="oxide", lean=-4, bend=6, w=7.2, toe="steel")
    to = k.part("torso", (0, 18, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(18, 16.6, 11.6), (23, 20.0, 12.6), (28, 23.0, 13.4), (31.6, 22.0, 12.6), (33.6, 16.0, 10.0)], "gun", "boilerplate")
    k.box(to, C(0, 22.0, 6.8, 13.0, 8.0, 0.8), "oxide", tag="chest_plate")
    for x in (-3.6, 3.6):                         # gauges, the needles in the red
        k.ring(to, x, 26.0, 7.6, 1.8, 0.6, "brass", "gauge", n=10, axis="z")
        k.box(to, C(x, 25.0, 7.4, 2.6, 2.6, 0.4), "glass", tag="gauge_face")
        k.limb(to, (x, 26.0, 7.8), (x + 0.9, 26.8, 7.8), 0.3, "oxide", "needle")
    rivet_row(k, to, (-6.0, 30.0, 6.6), (6.0, 30.0, 6.6), 6, 0.3)
    # the boiler on his back: a drum, its firebox glowing blue, the stack
    k.stack(to, 0, -10.0, [(16, 11.0, 7.0), (30, 11.0, 7.0)], "oxide", "boiler")
    for y in (18.0, 23.0, 28.0):
        k.box(to, C(0, y, -10.0, 11.6, 1.0, 7.6), "gun", tag="boiler_band")
    k.box(to, C(0, 18.6, -13.6, 4.6, 3.4, 0.6), "arc", tag="firebox")
    k.limb(to, (-3.0, 30.0, -10.0), (-3.4, 42.0, -11.0), 3.0, "gun", "stack")
    k.box(to, C(-3.4, 41.6, -11.0, 4.0, 1.4, 4.0), "soot", tag="stack_cap")
    k.limb(to, (3.0, 30.0, -10.0), (3.0, 34.0, -10.0), 1.4, "brass", "whistle")
    for sx in (-1, 1):
        k.limb(to, (sx * 4.0, 26.0, -6.0), (sx * 10.0, 26.0, -1.0), 1.4, "brass", "pipe")
    hd = k.part("head", (0, 33, 2.0), (("x", -10),), "torso")
    k.box(hd, C(0, 33.0, 2.6, 8.0, 7.0, 7.6), "gun", tag="helm")
    k.box(hd, C(0, 33.0, 6.4, 6.6, 3.6, 1.2), "leather", tag="mask")
    for sx in (-1, 1):
        k.limb(hd, (sx * 2.0, 34.0, 7.0), (sx * 3.6, 32.0, 9.4), 1.8, "gun", "filter")
        k.box(hd, C(sx * 1.8, 37.0, 6.4, 2.6, 2.0, 0.8), "brass", tag="goggle_rim")
        k.box(hd, C(sx * 1.8, 37.3, 6.9, 1.8, 1.4, 0.4), "eye", tag="eye")
    k.box(hd, C(0, 39.8, 2.6, 8.6, 1.4, 8.2), "oxide", tag="helm_rim")
    rivet_row(k, hd, (-3.6, 39.0, 6.6), (3.6, 39.0, 6.6), 4, 0.2)
    arms(k, to, 13.0, 31, "gun", {1: ((("x", -40), ("z", -10)), (("x", -40),)), -1: ((("x", -62), ("z", 6)), (("x", -30),))}, w=6.6, long=1.1)
    for side in (1, -1):
        k.blob(to, (side * 13.6, 31.4, 0), (5.0, 3.6, 5.6), "oxide", "pauldron", step=0.8)
    # the drill: the right forearm opens into a motor housing and a great stepped spiral
    for b in list(k.s.boxes):
        if b.part is k.parts["hand_r"]:
            k.s.boxes.remove(b)
    dr = held(k, "drill", "r", (-13.0, 14.0, 0.4), (("x", 0),))
    k.box(dr, C(-13.0, 10.6, 0.4, 7.4, 6.0, 7.4), "gun", tag="drill_motor")
    k.box(dr, C(-13.0, 9.6, 0.4, 8.0, 1.2, 8.0), "oxide", tag="drill_collar")
    for i in range(8):
        r = 3.6 - i * 0.42
        y = 9.4 - (i + 1) * 2.2
        k.box(dr, C(-13.0, y, 0.4, r * 2, 2.25, r * 2), "steel", tag="drill")
        a = i * 1.2
        k.box(dr, C(-13.0 + math.cos(a) * r, y + 0.2, 0.4 + math.sin(a) * r, 1.1, 1.8, 1.1), "gun", tag="drill_flute")
    k.shard(dr, (-13.0, -8.2, 0.4), (0, -1, 0), 3.0, 1.2, mat="steel", tag="drill_tip")
    # the claw: three hooked steel fingers on pistons
    for b in list(k.s.boxes):
        if b.part is k.parts["hand_l"]:
            k.s.boxes.remove(b)
    cw = held(k, "claw", "l", (13.0, 14.0, 0.4), (("x", 0),))
    k.box(cw, C(13.0, 10.4, 0.4, 6.4, 4.6, 6.4), "gun", tag="claw_wrist")
    for a in (0, 2.1, 4.2):
        x, z = math.cos(a) * 2.6, math.sin(a) * 2.6
        k.limb(cw, (13.0 + x, 10.4, 0.4 + z), (13.0 + x * 1.9, 5.4, 0.4 + z * 1.9), 1.6, "steel", "claw_finger")
        k.limb(cw, (13.0 + x * 1.9, 5.4, 0.4 + z * 1.9), (13.0 + x * 1.0, 1.6, 0.4 + z * 1.0), 1.3, "steel", "claw_finger")
        k.limb(cw, (13.0 + x * 0.8, 14.4, 0.4 + z * 0.8), (13.0 + x * 1.6, 9.0, 0.4 + z * 1.6), 0.6, "brass", "piston")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.3)
    return k.s, k.parts


# ================================================================ the Pit Boss (elite)

def pit_boss():
    """The guild-master never comes up and never goes down without his lance. Taller than his diggers by a head and
    twice as heavy in a greatcoat of riveted iron plates, a square iron helm cut with a T and two arc lamps over it,
    a pair of smokestacks rising over his shoulders from the furnace in his chest, and a drill-lance - a spiral of
    steel as long as a spear on a shaft he holds like one."""
    k = X.Kit("pit_boss")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(12, 12.4, 8.8), (20, 12.0, 8.4)], "leather", "breeches")
    for i, (x, z, L) in enumerate(((-6.0, 2.6, 17), (6.0, 2.6, 17), (-5.0, -4.6, 19), (0, -4.8, 19), (5.0, -4.6, 19))):
        k.box(hips, C(x, 20 - L, z, 3.6, L - 1.0, 0.9), "gun", tag="plate_coat")
        rivet_row(k, hips, (x, 20 - L + 2.0, z), (x, 18.0, z), 3, 0.5 if z > 0 else -0.5)
    k.box(hips, C(0, 19.0, 0, 13.0, 2.4, 9.4), "oxide", tag="belt")
    k.box(hips, C(0, 18.8, 4.8, 3.6, 3.0, 0.6), "brass", tag="buckle")
    legs(k, hips, 19, 10.0, 3.6, "leather", "gun", knee_mat="oxide", lean=-6, bend=8, w=5.8, toe="steel")
    to = k.part("torso", (0, 20, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(20, 12.4, 8.8), (25, 14.4, 9.6), (30, 17.6, 10.4), (34, 18.0, 10.0)], "gun", "plate_coat")
    k.box(to, C(0, 24.0, 5.0, 7.4, 7.4, 0.8), "gun", tag="furnace_door")
    k.box(to, C(0, 25.0, 5.6, 5.0, 4.4, 0.4), "arc", tag="furnace_glow")
    for x in (-1.6, 0, 1.6):
        k.box(to, C(x, 24.8, 6.0, 0.6, 4.8, 0.4), "iron", tag="furnace_grate")
    for y in (21.0, 32.0):
        rivet_row(k, to, (-7.0, y, 4.8), (7.0, y, 4.8), 7, 0.3)
    for sx in (-1, 1):
        k.box(to, C(sx * 7.6, 20.0, 1.0, 1.2, 13.0, 8.4), "oxide", tag="guild_stripe")
        k.blob(to, (sx * 9.6, 33.0, 0), (4.4, 3.0, 5.0), "gun", "pauldron", step=0.7)
        k.box(to, C(sx * 10.0, 30.4, 0, 6.0, 1.4, 9.0), "oxide", tag="pauldron_lame")
        k.limb(to, (sx * 6.4, 30.0, -4.4), (sx * 7.4, 46.0, -6.4), 2.6, "gun", "smokestack")       # the stacks
        k.box(to, C(sx * 7.4, 45.6, -6.4, 3.6, 1.6, 3.6), "soot", tag="stack_cap")
        k.box(to, C(sx * 7.2, 38.0, -6.0, 3.2, 0.8, 3.2), "brass", tag="stack_band")
    hd = k.part("head", (0, 34, 1.0), (("x", -4),), "torso")
    k.box(hd, C(0, 34.2, 1.0, 7.6, 8.4, 7.6), "gun", tag="helm")
    k.box(hd, C(0, 42.4, 1.0, 8.4, 1.2, 8.4), "oxide", tag="helm_rim")
    k.box(hd, C(0, 38.4, 4.85, 6.0, 1.0, 0.3), "dark", tag="t_slit")      # the T
    k.box(hd, C(0, 34.8, 4.85, 1.2, 4.0, 0.3), "dark", tag="t_slit")
    eyes(k, hd, 38.6, 4.95, 1.6, 1.6, h=0.6)
    rivet_row(k, hd, (-3.4, 35.0, 4.5), (-3.4, 41.4, 4.5), 4, 0.2)
    rivet_row(k, hd, (3.4, 35.0, 4.5), (3.4, 41.4, 4.5), 4, 0.2)
    for sx in (-1, 1):                            # the two lamps on the helm
        k.box(hd, C(sx * 2.6, 43.4, 3.0, 2.6, 2.4, 2.4), "brass", tag="helm_lamp")
        k.box(hd, C(sx * 2.6, 43.8, 4.3, 1.8, 1.6, 0.4), "arc", tag="lamp_lens")
    arms(k, to, 9.8, 32, "gun", {1: ((("x", -40), ("z", -18)), (("x", -40),)), -1: ((("x", -30), ("z", 14)), (("x", -50),))}, glove="leather", w=4.4)
    for side in (1, -1):
        k.box(k.parts["fore_" + ("l" if side > 0 else "r")], C(side * 9.8, 18.4, 0, 5.0, 4.4, 5.0), "oxide", tag="vambrace")
    dl = held(k, "drill_lance", "r", (-9.8, 14.2, 0.4), (("x", 96), ("z", -8)))
    k.limb(dl, (-9.8, -4.0, 0.4), (-9.8, 24.0, 0.4), 1.8, "gun", "lance_shaft")
    k.box(dl, C(-9.8, -6.0, 0.4, 2.6, 2.0, 2.6), "oxide", tag="lance_butt")
    for y in (6.0, 12.0):
        k.box(dl, C(-9.8, y, 0.4, 2.4, 1.2, 2.4), "leather", tag="lance_wrap")
    k.box(dl, C(-9.8, 22.0, 0.4, 5.6, 4.4, 5.6), "gun", tag="lance_motor")
    k.box(dl, C(-9.8, 23.6, 3.0, 2.0, 1.4, 0.6), "arc", tag="motor_light")
    for i in range(9):
        r = 2.6 - i * 0.26
        y = 26.4 + i * 2.0
        k.box(dl, C(-9.8, y, 0.4, r * 2, 2.05, r * 2), "steel", tag="drill")
        a = i * 1.1
        k.box(dl, C(-9.8 + math.cos(a) * r, y + 0.2, 0.4 + math.sin(a) * r, 0.9, 1.6, 0.9), "gun", tag="drill_flute")
    k.shard(dl, (-9.8, 44.4, 0.4), (0, 1, 0), 3.0, 1.0, mat="steel", tag="drill_tip")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.15)
    return k.s, k.parts


MOBS = {
    "drill_mole": dict(make=drill_mole, rig="crawler", ent=(1.2, 1.2), stats=dict(hp=30, speed=0.3, dmg=7, armor=6, kb=0.2)),
    "delver": dict(make=delver, ent=(1.1, 2.4), stats=dict(hp=62, speed=0.23, dmg=10, armor=8, kb=0.5)),
    "blaster": dict(make=blaster, ent=(1.0, 2.4), stats=dict(hp=38, speed=0.24, dmg=9, armor=3, kb=0)),
    "tunnel_rat": dict(make=tunnel_rat, ent=(0.9, 2.0), stats=dict(hp=36, speed=0.34, dmg=7, armor=2, kb=0)),
    "steam_driller": dict(make=steam_driller, ent=(1.8, 3.6), stats=dict(hp=190, speed=0.18, dmg=18, armor=12, kb=1.0)),
    "pit_boss": dict(make=pit_boss, ent=(1.1, 3.4), stats=dict(hp=330, speed=0.24, dmg=15, armor=13, kb=0.7), key=True),
}
