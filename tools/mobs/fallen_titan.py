"""The Fallen Titan's monsters, each built by hand (tools/vox2.py). The things that live inside a dead giant: raw red
muscle, pale sinew, yellow fat, ivory bone, the bile-green of its stomach and the dark red of the blood that still
moves in it.

    burrow_leech    swarm   a fat ringed leech, a round mouth of teeth at the front, stubby hooked feet (the spider's bones)
    marrow_brute    brute   a hulk of muscle with bone plates grown out through the skin, a bone shield on each forearm
    bile_priest     caster  a cultist in stitched hide, a gut-sack slung on a pole dripping bile, a mask cut from a cheek
    sinew_stalker   skirm   a lanky thing of bare muscle strands, arms that stretch, a skull with no skin on it
    heart_warden    elite   a knight swallowed long ago and grown into the flesh, arteries plugged into his armour,
                            a shield like a heart valve
    still_heart     boss    the Still Heart: a heart as big as a house, the aorta arching off it, walking on its arteries

    python tools/monsterforge.py fallen_titan --preview ; python tools/mobsheet.py fallen_titan
"""
import math

import vox2 as X
from vox2 import C, ramp

MUSCLE = ramp("#1e0404", "#340808", "#4e0e0e", "#6a1816", "#862420", "#a0342a")
SINEW = ramp("#4a3c32", "#66564a", "#827062", "#9e8c7a", "#baa894", "#d4c4ae")
FAT = ramp("#3a2c0c", "#5a4614", "#7a601e", "#98782a", "#b4943c")
BONE = ramp("#3e382c", "#5e5644", "#7e765e", "#9e967a", "#bcb498", "#d8d2b8")
BILE = ramp("#1a4a0a", "#2a7010", "#44a018", "#78d030", "#b8f080")
BLOOD = ramp("#5a0408", "#8a0a10", "#c01a1a", "#ee3a2a", "#ff7a5a")
HIDE = ramp("#1e120c", "#2e1c12", "#40281a", "#543622", "#68462c")
IRON = ramp("#0c0a0a", "#161212", "#221c1a", "#302724", "#40342e", "#52443c")
RUST = ramp("#2a0c06", "#44140a", "#5e1c10", "#7a2816")
VESSEL = ramp("#2a0610", "#420a18", "#5e1222", "#7a1c2e", "#962a3c")


def shaders():
    return {
        "muscle": X.surf(MUSCLE, 0.52, 1.2, 0.2, 0.0, stripe=2, drip=(BLOOD, 0.08)),
        "sinew": X.surf(SINEW, 0.52, 1.1, 0.2, 0.0, stripe=2),
        "fat": X.wrinkled(FAT, 1.4),
        "bone": X.surf(BONE, 0.6, 1.2, 0.16, 0.12),
        "glow": X.glow(BILE),
        "blood": X.glow(BLOOD),
        "eye": X.glow(BLOOD, 0.82, 0.16),
        "hide": X.surf(HIDE, 0.5, 1.0, 0.22, 0.04, pattern=lambda p, n, i, j, w, h: -0.3 if (i + j * 3) % 9 == 0 else 0),
        "iron": X.surf(IRON, 0.5, 1.4, 0.16, 0.18, rust=(RUST, 0.4, 0.4), drip=(MUSCLE, 0.12)),
        "vessel": X.surf(VESSEL, 0.5, 1.3, 0.2, 0.0, stripe=3),
        "flesh": X.wrinkled(MUSCLE, 0.9),
        "dark": X.dark(MUSCLE),
    }


def plates(k, part, pts, s=1.0):
    """bone plates grown out through the skin: a slab, a ridge, a spur"""
    for (x, y, z, nx, nz) in pts:
        k.box(part, C(x, y, z, 3.4 * s, 2.6 * s, 3.4 * s), "bone", tag="bone_plate")
        k.shard(part, (x, y + 2.0 * s, z), (nx * 0.6, 0.8, nz * 0.6), 2.6 * s, 1.4 * s, mat="bone", tag="bone_spur")


def vessel(k, part, pts, w, mat="vessel", tag="artery", pulse=True):
    """an artery along a path, ringed where it pulses"""
    for (a, b) in zip(pts, pts[1:]):
        k.limb(part, a, b, w, mat, tag)
    if pulse:
        for p in pts[1:-1]:
            k.box(part, C(p[0], p[1] - w * 0.4, p[2], w * 1.3, w * 0.5, w * 1.3), "blood", group="glow", tag="pulse")


# ================================================================ the Still Heart (boss, on the spider)

def still_heart():
    """The titan's heart, as big as a house, that stopped when the titan fell - and started again when the gate
    opened. It hangs in its chamber on arteries thick as trees, and when it is angry it tears them out of the
    walls and walks on them like a spider of vessels: four lobes of dark muscle, the fat on them in yellow seams,
    the coronary arteries glowing as they pump, the great arch of the aorta rising off its top like a crown with
    the torn vessels still open, and on its front the valve - an eye of cartilage that opens on light."""
    k = X.Kit("still_heart")
    body = k.part("body", (0, 22, 0))
    # the heart: two great ventricles low, two atria high, leaning a little, the apex down and forward
    k.blob(body, (-3, 20, 0), (11, 12, 10), "flesh", "ventricle_l", step=1.0)
    k.blob(body, (5, 18, 1), (10, 11, 9), "flesh", "ventricle_r", step=1.0)
    k.blob(body, (1, 9, 3), (6, 5, 6), "flesh", "apex", step=1.0)
    for (x, y, z, r) in ((-6, 30, -2, 7), (7, 29, -1, 6.4)):
        k.blob(body, (x, y, z), (r, r * 0.8, r), "muscle", "atrium", step=1.0)
    for (a, b) in (((-8, 26, 9), (-2, 14, 10)), ((4, 27, 9.4), (9, 16, 9)), ((0, 24, 10), (1, 12, 8))):
        k.limb(body, a, b, 2.4, "fat", "fat_seam")
    # the coronary arteries, glowing as they pump, branching over the front
    vessel(k, body, [(-1, 29, 9.6), (-4, 22, 10.6), (-6, 15, 9), (-4, 10, 7)], 1.6, mat="blood", tag="coronary", pulse=False)
    vessel(k, body, [(2, 29, 9.6), (6, 23, 10), (10, 16, 8)], 1.4, mat="blood", tag="coronary", pulse=False)
    vessel(k, body, [(-4, 22, 10.6), (2, 18, 10.6), (4, 13, 8.6)], 1.0, mat="blood", tag="coronary", pulse=False)
    # the valve on its front: a ring of cartilage with three leaflets, light between them
    hd = k.part("head", (0, 22, 9), (), "body")
    k.ring(hd, 1, 22, 11.6, 4.4, 1.6, "sinew", "valve_ring", n=14)
    k.blob(hd, (1, 22, 11.4), (3.6, 3.6, 1.0), "glow", "valve_light", step=0.8)
    for a in (90, 210, 330):
        r = math.radians(a)
        k.limb(hd, (1, 22, 12.2), (1 + math.cos(r) * 3.6, 22 + math.sin(r) * 3.6, 12.2), 1.4, "sinew", "leaflet", d=0.8)
    k.box(hd, C(1, 21.4, 12.6, 1.4, 1.4, 0.6), "eye", group="glow", tag="eye")
    # the aorta: a great arch off the top, the vessels torn open on it like a crown
    ab = k.part("abdomen", (0, 30, -2), (), "body")
    vessel(k, ab, [(2, 32, 0), (3, 40, -1), (0, 45, -4), (-5, 44, -8), (-7, 37, -10)], 4.6, tag="aorta")
    for (x, z, L, a) in ((1, -3, 7, -0.2), (-2, -5, 8, 0.1), (-4, -7, 6, 0.3)):
        k.limb(ab, (x, 45, z), (x + a * 6, 45 + L, z - 1), 2.4, "vessel", "torn_vessel")
        k.ring(ab, x + a * 6, 45 + L, z - 1, 1.6, 0.8, "blood", "vessel_mouth", n=8, axis="y")
    vessel(k, ab, [(-6, 32, -6), (-12, 38, -6), (-14, 44, -4)], 3.2, tag="pulmonary")
    k.ring(ab, -14, 44.6, -4, 2.2, 1.0, "blood", "vessel_mouth", n=8, axis="y")
    for (x, y, z) in ((8, 33, -6), (-10, 28, -8), (12, 24, -4)):
        k.blob(ab, (x, y, z), (2.4, 2.0, 2.4), "fat", "fat_lump", step=0.8)
    # eight arteries for legs: up off the heart, an arched knee, down to roots torn out of the walls
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, z in enumerate((7.0, 2.4, -2.4, -7.0)):
            nm = "leg_%s%d" % (s, i)
            lg = k.part(nm, (side * 8, 20, z), (("y", -side * (i - 1.5) * 22),), "body")
            knee = (side * 24, 34, z * 1.3)
            foot = (side * 34, 0.6, z * 1.6)
            vessel(k, lg, [(side * 8, 20, z), (side * 16, 30, z * 1.15), knee], 3.2)
            vessel(k, lg, [knee, (side * 31, 18, z * 1.45), foot], 2.6, tag="foot")
            for t in (-1, 0, 1):                     # the torn roots it stands on
                k.limb(lg, foot, (foot[0] + side * 2 + t * 1.4, 0.4, foot[2] + t * 2.4), 1.0, "vessel", "foot")
            joints[nm] = ("LL" if side > 0 else "RL") + str(i + 1)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Heart-Warden (elite, the key)

def heart_warden():
    """A knight who came to kill the titan when it walked, and was swallowed, and did not die. The flesh grew over
    him: his plate is rusted through and the titan's muscle shows in the gaps; arteries run out of the walls of his
    body and plug into his back and his helm, pumping. His shield is a valve of cartilage and bone that opens and
    shuts; his sword is fused to his hand. He holds the valve door, and the clot that seals it is his."""
    k = X.Kit("heart_warden")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(16, 13, 8.6), (22, 13.6, 9)], "iron", "faulds")
    for x in (-4.4, 0, 4.4):
        k.box(hips, C(x, 12.6, 4.8, 4.0, 6.4, 0.8), "iron", tag="tasset")
    k.box(hips, C(0, 14, 5.4, 2.6, 4.0, 0.8), "muscle", tag="flesh_gap")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.6
        th = k.part("thigh_" + nm, (x, 21, 0), (("x", -6), ("z", side * 5)), "hips")
        sh = k.part("shin_" + nm, (x, 11.4, 0), (("x", 10),), th)
        ft = k.part("foot_" + nm, (x, 2.8, 0), (("x", -4),), sh)
        k.box(th, C(x, 11.6, 0, 5.4, 9.6, 5.8), "iron", tag="cuisse")
        k.box(th, C(x + side * 2.4, 14, 1, 1.0, 5.0, 3.0), "muscle", tag="flesh_gap")
        k.box(th, C(x, 10.4, 1.0, 6.0, 3.0, 5.4), "iron", tag="poleyn")
        k.box(sh, C(x, 2.8, 0, 5.4, 8.6, 5.8), "iron", tag="greave")
        k.box(sh, C(x, 5, 3.0, 2.0, 3.0, 0.6), "muscle", tag="flesh_gap")
        k.box(ft, C(x, 0, 1.6, 5.8, 3.0, 8.8), "iron", tag="foot")
    # ---------------------------------------------------------------- torso: rusted plate, flesh through it, arteries in his back
    to = k.part("torso", (0, 22, 0), (("x", 8),), "hips")
    k.stack(to, 0, 0, [(22, 13.6, 9), (28, 17, 10.4), (33, 19, 10.8), (37, 17, 9.8)], "iron", "cuirass")
    for (x, y, w, h) in ((-3.4, 27, 3.6, 5.0), (4.0, 31, 3.0, 3.6), (0.6, 24, 2.4, 2.4)):
        k.box(to, C(x, y, 5.3, w, h, 0.6), "muscle", tag="flesh_gap")
        k.box(to, C(x, y + h * 0.4, 5.5, w * 0.6, 0.6, 0.4), "blood", group="glow", tag="vein")
    for (sx, sy) in ((-5, 34), (5, 34), (-3, 28), (3, 28), (0, 31)):          # arteries plugged into his back
        vessel(k, to, [(sx, sy, -5.2), (sx * 1.3, sy + 2, -9), (sx * 1.6, sy + 1, -14), (sx * 1.8, sy - 6, -17)], 1.8)
        k.ring(to, sx, sy, -5.4, 1.4, 0.8, "iron", "socket", n=8)
    for side in (1, -1):
        k.blob(to, (side * 10.4, 36, 0), (5.6, 3.6, 5.8), "iron", "pauldron")
        k.box(to, C(side * 11, 37.4, 0, 3.0, 2.0, 4.0), "muscle", tag="flesh_gap")
        k.shard(to, (side * 12, 38.6, 0), (side * 0.4, 1, 0), 4.0, 1.8, mat="bone", tag="bone_spur")
    # ---------------------------------------------------------------- the helm: a great helm, an artery in its crown, flesh in the slit
    hd = k.part("head", (0, 37, 0.4), (("x", -8),), "torso")
    k.box(hd, C(0, 37, 0.2, 7.0, 8.0, 7.2), "iron", tag="helm")
    k.box(hd, C(0, 41.2, 3.75, 6.0, 1.0, 0.4), "dark", tag="visor")
    for sx in (-1.4, 1.4):
        k.box(hd, C(sx, 41.3, 3.85, 1.6, 0.7, 0.3), "eye", group="glow", tag="eye")
    for i in range(6):
        k.box(hd, C(-2.0 + i * 0.8, 38.6, 3.85, 0.4, 1.2, 0.3), "muscle", tag="breath")
    vessel(k, hd, [(0, 45, 0), (0, 49, -3), (0, 50, -9), (0, 46, -15)], 2.0)
    k.ring(hd, 0, 45, 0, 1.6, 0.8, "iron", "socket", n=8, axis="y")
    # ---------------------------------------------------------------- arms: the valve shield, the sword grown into his hand
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 10.4
        up = k.part("arm_" + nm, (x, 35, 0), (("x", -40 if side > 0 else -30), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 26, 0), (("x", -50 if side > 0 else -60),), up)
        hn = k.part("hand_" + nm, (x, 17, 0), (), fo)
        k.box(up, C(x, 26.6, 0, 5.0, 8.6, 5.2), "iron", tag="rerebrace")
        k.box(fo, C(x, 17.6, 0, 5.0, 8.6, 5.2), "iron", tag="vambrace")
        k.box(fo, C(x + side * 2.6, 21, 0, 0.6, 4.0, 3.0), "muscle", tag="flesh_gap")
        k.box(hn, C(x, 13.8, 0.4, 4.6, 4.0, 4.6), "iron", tag="gauntlet")
    # the valve shield: three cusps of cartilage in a ring of bone, a red light where they meet
    sh = k.part("shield", (14, 17, 2), (("y", 8),), k.parts["hand_l"])
    k.blob(sh, (14.6, 19, 2), (1.2, 11, 11), "sinew", "shield", step=1.0)
    k.ring(sh, 15.6, 19, 2, 10.6, 2.0, "bone", "valve_rim", n=20, axis="x")
    for a in (90, 210, 330):
        r = math.radians(a)
        k.limb(sh, (15.8, 19, 2), (15.8, 19 + math.sin(r) * 9.6, 2 + math.cos(r) * 9.6), 1.6, "fat", "cusp_seam", d=0.8)
    k.blob(sh, (16.0, 19, 2), (0.8, 2.4, 2.4), "blood", "valve_light", step=0.8)
    for (y, z) in ((27, 7), (11, -6), (14, 9)):
        k.shard(sh, (15.6, y, 2 + z), (0.3, (y - 19) * 0.1, z * 0.1), 3.0, 1.6, mat="bone", tag="rim_spur")
    # the sword, fused to his hand: a long blade grown over with sinew at the hilt
    sw = k.part("sword", (-10.4, 15.6, 0.6), (("x", 80),), k.parts["hand_r"])
    k.stack(sw, -10.4, 0.6, [(12, 3.6, 3.6), (18, 2.4, 2.4)], "sinew", "fused_hilt")
    k.box(sw, C(-10.4, 18, 0.6, 1.8, 1.4, 10), "iron", tag="crossguard")
    k.box(sw, C(-10.4, 19.4, 0.6, 1.0, 24, 4.4), "iron", tag="blade")
    k.shard(sw, (-10.4, 43.4, 0.6), (0, 1, 0), 4.0, 4.4, mat="iron", tag="blade")
    vessel(k, sw, [(-10.4, 18, 2.6), (-10.4, 26, 2.8), (-10.4, 33, 2.6)], 0.8, pulse=False)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Marrow Brute (brute)

def marrow_brute():
    """The titan's flesh makes its own guards: a hulk of raw muscle twice a man's size, no skin on it, the fibres
    showing, with bone grown out through it in plates - over the shoulders, down the spine, and in two great slabs
    on its forearms that it brings together in front of it like a wall. Its head is small and sunk, a jaw of bone."""
    k = X.Kit("marrow_brute")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(15, 15, 11), (22, 16.4, 11.6)], "muscle", "hips")
    plates(k, hips, [(-5, 18, -5.6, 0, -1), (5, 18, -5.6, 0, -1)])
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.0
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -12), ("z", side * 10)), "hips")
        sh = k.part("shin_" + nm, (x, 10.4, 0), (("x", 16),), th)
        ft = k.part("foot_" + nm, (x, 2.6, 0), (("x", -4),), sh)
        k.stack(th, x, 0, [(10.4, 7.4, 7.6), (16, 9.0, 9.2), (20, 8.4, 8.6)], "muscle", "thigh")
        k.box(th, C(x, 10.2, 2.6, 6.0, 3.2, 4.0), "bone", tag="kneecap")
        k.stack(sh, x, 0, [(2.6, 6.8, 7.0), (10.4, 7.6, 7.8)], "muscle", "shin")
        k.box(sh, C(x, 3.4, 3.6, 4.0, 6.4, 1.4), "bone", tag="shin_plate")
        k.box(ft, C(x, 0, 1.8, 8.2, 3.0, 11), "muscle", tag="foot")
        for t in (-2.4, 0, 2.4):
            k.shard(ft, (x + t, 0.8, 7.0), (0, -0.2, 1), 2.0, 1.4, mat="bone", tag="foot")
    # ---------------------------------------------------------------- torso: a slab of muscle, a spine of bone plates
    to = k.part("torso", (0, 22, 0), (("x", 22),), "hips")
    k.stack(to, 0, 0, [(22, 16.4, 11.6), (29, 23, 13.6), (36, 28, 14.6), (40, 26, 13)], "muscle", "torso")
    k.box(to, C(0, 26, 6.8, 12, 9, 1.0), "sinew", tag="abdominal")
    for y in (28.4, 31.4):
        k.box(to, C(0, y, 7.4, 12, 0.6, 0.6), "muscle", tag="abdominal_line")
    plates(k, to, [(0, 24 + i * 3.4, -6.6 - i * 0.2, 0, -1) for i in range(5)], s=1.3)
    for side in (1, -1):
        k.blob(to, (side * 12, 38, 0), (6.6, 4.2, 7.0), "bone", "shoulder_plate")
        for i in range(3):
            k.shard(to, (side * (12 + i * 1.4), 41, -2 + i * 2), (side * 0.5, 1, -0.2), 5.0 - i, 2.2, mat="bone", tag="shoulder_spur")
    # ---------------------------------------------------------------- the head: small and low, a bone jaw
    hd = k.part("head", (0, 38, 4), (("x", -20),), "torso")
    k.box(hd, C(0, 37.4, 5.6, 7.0, 6.4, 6.6), "muscle", tag="head")
    k.box(hd, C(0, 35.6, 8.4, 8.0, 3.0, 3.0), "bone", tag="jaw")
    for t in (-2.6, -1.3, 0, 1.3, 2.6):
        k.shard(hd, (t, 38.4, 9.6), (0, -1, 0.1), 1.6, 0.8, mat="bone", tag="tooth")
    k.box(hd, C(0, 42.2, 8.4, 7.4, 1.6, 1.6), "bone", tag="brow")
    for sx in (-1.6, 1.6):
        k.box(hd, C(sx, 40.6, 8.95, 1.4, 0.8, 0.3), "eye", group="glow", tag="eye")
    # ---------------------------------------------------------------- arms: the bone guard slabs on the forearms
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 14.6
        up = k.part("arm_" + nm, (x, 37, 0), (("x", -50), ("z", side * 8)), "torso")
        fo = k.part("fore_" + nm, (x, 26, 0), (("x", -60), ("y", side * 20)), up)
        hn = k.part("hand_" + nm, (x, 15, 0), (), fo)
        k.stack(up, x, 0, [(26, 7.2, 7.4), (32, 8.6, 8.6), (37, 7.6, 7.8)], "muscle", "upper_arm")
        k.stack(fo, x, 0, [(16, 8.0, 8.0), (22, 9.0, 9.0), (26, 7.6, 7.6)], "muscle", "forearm")
        k.box(fo, C(x - side * 0.2, 13, 4.6, 12, 16, 2.4), "bone", tag="bone_guard")
        k.box(fo, C(x - side * 0.2, 13, 6.0, 10, 1.4, 1.0), "sinew", tag="guard_seam")
        k.box(fo, C(x - side * 0.2, 21, 6.0, 10, 1.4, 1.0), "sinew", tag="guard_seam")
        for y in (15, 23):
            k.shard(fo, (x - side * 0.2 + side * 5, y, 5.8), (side * 0.6, 0, 1), 3.0, 1.6, mat="bone", tag="guard_spur")
        k.box(hn, C(x, 9.6, 0.6, 7.6, 6.4, 7.4), "muscle", tag="fist")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Bile Priest (caster)

def bile_priest():
    """There are men who live in the titan and worship it from the inside. The Bile Priests wear robes of hide
    stitched from what the stomach did not take, and masks cut from the titan's cheek; they carry a stomach on a
    pole like a bag, swollen and dripping, and throw what is in it."""
    k = X.Kit("bile_priest")
    hips = k.part("hips", (0, 19, 0))
    k.stack(hips, 0, 0, [(1, 11.4, 8.6), (10, 10.4, 7.4), (19, 9.2, 6.6)], "hide", "robe")
    for (x, z) in ((-4, 3.6), (3, 3.8), (-1, -3.6)):
        k.box(hips, C(x, 4, z, 0.4, 14, 0.4), "sinew", tag="stitch_line")
    for (x, L) in ((-3.6, 6), (2.4, 9)):
        k.limb(hips, (x, 18, 4), (x * 1.1, 18 - L, 4.4), 0.6, "sinew", "cord")
        k.box(hips, C(x * 1.1, 17 - L, 4.4, 1.4, 1.6, 1.2), "bone", tag="charm")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 19, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 10, 0), (), th)
        ft = k.part("foot_" + nm, (x, 2, 0), (), sh)
        k.box(ft, C(x, 0, 1.8, 3.2, 1.6, 5.4), "flesh", tag="foot")
    # ---------------------------------------------------------------- torso: hunched, the hide stitched in patches
    to = k.part("torso", (0, 19, 0), (("x", 20),), "hips")
    k.stack(to, 0, 0, [(19, 9.2, 6.6), (25, 11.4, 7.2), (31, 12.6, 7.4)], "hide", "robe")
    k.stack(to, 0, -0.4, [(26, 15, 9.6), (31, 15.4, 9.6), (33, 13, 8.6)], "fat", "mantle")
    k.box(to, C(0, 22, 3.85, 6.0, 7.0, 0.4), "muscle", tag="patch")
    k.box(to, C(0, 21.6, 4.0, 6.4, 0.4, 0.4), "sinew", tag="stitch_line")
    k.box(to, C(0, 26.6, 4.0, 6.4, 0.4, 0.4), "sinew", tag="stitch_line")
    # ---------------------------------------------------------------- the head: a hood, the cheek-mask with a ragged mouth
    hd = k.part("head", (0, 32, 0.8), (("x", -14),), "torso")
    k.box(hd, C(0, 31.6, 0.4, 6.4, 7.0, 6.6), "hide", tag="hood")
    k.shard(hd, (0, 38.4, -1.0), (0, 0.4, -1), 4.0, 3.4, mat="hide", tag="hood_peak")
    k.box(hd, C(0, 32.0, 3.6, 4.8, 5.2, 1.2), "flesh", tag="cheek_mask")
    k.box(hd, C(0, 32.6, 4.25, 3.2, 1.2, 0.4), "dark", tag="mask_mouth")
    for t in (-1.2, -0.4, 0.4, 1.2):
        k.box(hd, C(t, 32.6, 4.4, 0.3, 1.2, 0.3), "sinew", tag="stitch")
    for sx in (-1.2, 1.2):
        k.box(hd, C(sx, 35.2, 4.25, 1.2, 1.0, 0.4), "dark", tag="eye_hole")
        k.box(hd, C(sx, 35.4, 4.35, 0.6, 0.6, 0.3), "glow", group="glow", tag="eye")
    # ---------------------------------------------------------------- arms: hide sleeves, the gut on its pole
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.4
        up = k.part("arm_" + nm, (x, 30, 0), (("x", -50 if side > 0 else -30), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 22, 0), (("x", -50 if side > 0 else -60),), up)
        hn = k.part("hand_" + nm, (x, 14, 0), (), fo)
        k.box(up, C(x, 22, 0, 3.8, 8.4, 4.0), "hide", tag="sleeve")
        k.stack(fo, x, 0, [(14, 5.6, 5.6), (22, 4.0, 4.0)], "hide", "sleeve")
        k.box(hn, C(x, 11.4, 0.4, 2.8, 2.8, 2.8), "flesh", tag="hand")
        if side > 0:
            k.blob(hn, (x, 12.6, 2.4), (1.4, 1.4, 1.4), "glow", "bile_in_hand", step=0.6)
    pl = k.part("gut_pole", (-7.4, 12.6, 0.8), (("x", 60),), k.parts["hand_r"])
    k.limb(pl, (-7.4, -8, 0.8), (-7.4, 30, 0.8), 1.2, "bone", "pole")
    k.limb(pl, (-7.4, 30, 0.8), (-7.4, 31, 5.0), 1.0, "bone", "crook")
    k.limb(pl, (-7.4, 31, 5.0), (-7.4, 28, 5.0), 0.8, "sinew", "cord")
    k.blob(pl, (-7.4, 23, 5.4), (4.0, 5.4, 4.0), "fat", "stomach", step=0.8)
    k.box(pl, C(-7.4, 21.6, 7.6, 4.0, 4.0, 1.0), "glow", group="glow", tag="bile_seep")
    for (x, z, L) in ((-1, 6, 5), (1.4, 4.6, 7), (0, 3.4, 4)):
        k.limb(pl, (-7.4 + x, 17.6, z), (-7.4 + x, 17.6 - L, z), 0.6, "glow", "bile_drip", group="glow")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Sinew Stalker (skirmisher)

def sinew_stalker():
    """It was made of what was left over: a lanky thing of bare muscle strands and pale sinew wound round a few
    bones, too tall, too thin, and its arms are longer than it is - the strands in them stretch, and it throws its
    hand eight blocks and pulls itself after. Its head is a skull with the sinews still on it, no skin at all."""
    k = X.Kit("sinew_stalker")
    hips = k.part("hips", (0, 22, 0))
    k.box(hips, C(0, 19.6, 0, 6.0, 3.6, 4.0), "bone", tag="pelvis")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.2
        th = k.part("thigh_" + nm, (x, 22, 0), (("x", -16), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 12, 0), (("x", 28),), th)
        ft = k.part("foot_" + nm, (x, 2.4, 0), (("x", -12),), sh)
        for dz, m in ((-0.6, "muscle"), (0.6, "sinew")):
            k.limb(th, (x, 22, dz), (x, 12, dz), 1.6, m, "strand")
            k.limb(sh, (x, 12, dz), (x, 2.4, dz), 1.4, m, "strand")
        k.box(th, C(x, 11.2, 1.0, 2.2, 1.8, 1.6), "bone", tag="knee")
        k.box(ft, C(x, 0, 1.4, 2.6, 2.4, 5.6), "muscle", tag="foot")
        for t in (-0.8, 0.8):
            k.shard(ft, (x + t, 0.6, 4.0), (0, -0.3, 1), 1.6, 0.6, mat="bone", tag="foot")
    # ---------------------------------------------------------------- torso: a ribcage wound with strands, too tall
    to = k.part("torso", (0, 22, 0), (("x", 24),), "hips")
    k.limb(to, (0, 22, -1.6), (0, 36, -1.6), 1.6, "bone", "spine")
    for i in range(5):
        y = 25 + i * 2.4
        k.ring(to, 0, y, 0, 3.4 - abs(i - 2) * 0.3, 0.7, "bone", "rib", n=10, axis="y")
    for (x, z, ph) in ((-2.6, 1.6, 0.0), (2.4, 1.8, 1.2), (-1.0, -2.4, 2.0), (1.8, -2.2, 0.7), (0, 2.6, 2.6)):
        pts = [(x + 0.8 * math.sin(ph + t * 3), 22 + t * 14, z + 0.6 * math.cos(ph + t * 2)) for t in (0, 0.33, 0.66, 1.0)]
        for (a, b) in zip(pts, pts[1:]):
            k.limb(to, a, b, 1.2, "muscle" if x < 0 else "sinew", "strand")
    k.box(to, C(0, 29, 0, 3.0, 3.0, 2.6), "blood", group="glow", tag="heart_knot")
    # ---------------------------------------------------------------- the head: a skull with the sinews on it
    hd = k.part("head", (0, 37, 0.4), (("x", -30),), "torso")
    k.box(hd, C(0, 37.6, 0.4, 4.8, 5.2, 5.4), "bone", tag="skull")
    k.box(hd, C(0, 36.4, 2.8, 3.6, 2.0, 1.4), "bone", tag="jaw")
    for t in (-1.2, -0.4, 0.4, 1.2):
        k.box(hd, C(t, 37.6, 3.5, 0.5, 0.9, 0.3), "bone", tag="tooth")
    for sx in (-1.1, 1.1):
        k.box(hd, C(sx, 40.0, 3.15, 1.4, 1.2, 0.3), "dark", tag="socket")
        k.box(hd, C(sx, 40.3, 3.25, 0.6, 0.5, 0.2), "eye", group="glow", tag="eye")
    for (x, z) in ((-2.4, 0.4), (2.4, 0.4), (-1.6, -2.6), (1.6, -2.6)):
        k.limb(hd, (x, 42.4, z), (x * 1.1, 36, z * 1.1), 0.8, "muscle", "face_strand")
    # ---------------------------------------------------------------- arms: as long as it is tall, strands that stretch
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.4
        up = k.part("arm_" + nm, (x, 35, 0), (("x", -30 if side > 0 else -80), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 23, 0), (("x", -20 if side > 0 else -10),), up)
        hn = k.part("hand_" + nm, (x, 10, 0), (), fo)
        for dz, m in ((-0.6, "muscle"), (0.6, "sinew")):
            k.limb(up, (x, 35, dz), (x, 23, dz), 1.3, m, "strand")
            k.limb(fo, (x, 23, dz), (x, 10, dz), 1.1, m, "strand")
        k.box(fo, C(x, 22.2, 0, 2.0, 1.6, 2.0), "bone", tag="elbow")
        k.box(hn, C(x, 7.6, 0.3, 2.4, 2.6, 2.0), "muscle", tag="hand")
        for t in (-0.9, 0, 0.9):
            pts = [(x + t, 7.6, 0.8), (x + t * 1.3, 3.0, 1.4), (x + t * 1.4, 0.4, 2.8)]
            for (a, b) in zip(pts, pts[1:]):
                k.limb(hn, a, b, 0.6, "sinew", "finger")
            k.shard(hn, pts[-1], (0, -0.6, 1), 1.4, 0.5, mat="bone", tag="claw")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Burrow Leech (swarm, on the spider)

def burrow_leech():
    """Fat ringed leeches as long as a man, that swim in the titan's flesh the way a fish swims in water and come up
    under your feet: a round mouth at the front full of rings of teeth, the body in fat red rings, stubby hooked
    feet along the belly that grip, a trail of slime."""
    k = X.Kit("burrow_leech")
    body = k.part("body", (0, 4, 0))
    for i in range(5):                              # the rings: fat at the middle, thinner to the ends
        z = 3.4 - i * 2.6
        r = 3.2 + (1.0 - abs(i - 2) * 0.4)
        k.blob(body, (0, 4.0, z), (r, r * 0.8, 1.6), "flesh" if i % 2 else "muscle", "ring", step=0.7)
    hd = k.part("head", (0, 4, 5.4), (), "body")
    k.blob(hd, (0, 4.0, 6.6), (3.6, 3.0, 2.0), "muscle", "head_ring", step=0.7)
    k.ring(hd, 0, 4.2, 8.4, 2.4, 1.2, "flesh", "lip", n=12)
    k.blob(hd, (0, 4.2, 8.2), (1.8, 1.8, 0.6), "dark", "mouth", step=0.6)
    for ring_r, n in ((2.0, 10), (1.2, 7)):         # rings of teeth inside the mouth
        for j in range(n):
            a = j * 2 * math.pi / n
            k.shard(hd, (math.cos(a) * ring_r, 4.2 + math.sin(a) * ring_r, 8.6), (-math.cos(a), -math.sin(a), 0.6), 1.2, 0.5,
                    mat="bone", tag="tooth")
    for sx in (-1.4, 1.4):
        k.box(hd, C(sx, 6.4, 7.0, 0.6, 0.6, 0.4), "eye", group="glow", tag="eye")
    ab = k.part("abdomen", (0, 4, -6), (), "body")
    for i in range(3):
        z = -9.0 - i * 2.4
        r = 2.8 - i * 0.7
        k.blob(ab, (0, 3.6 - i * 0.3, z), (r, r * 0.8, 1.4), "muscle" if i % 2 else "flesh", "tail_ring", step=0.7)
    k.box(ab, C(0, 0.4, -9, 4.0, 0.4, 6.0), "glow", group="glow", tag="slime")
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, z in enumerate((3.0, 0.6, -1.8, -4.2)):
            nm = "leg_%s%d" % (s, i)
            lg = k.part(nm, (side * 2.6, 2.4, z), (), "body")
            k.limb(lg, (side * 2.6, 2.4, z), (side * 4.4, 0.6, z), 1.0, "flesh", "foot")
            k.shard(lg, (side * 4.4, 0.8, z), (side * 0.3, -1, 0.4), 1.0, 0.6, mat="bone", tag="foot")
            joints[nm] = ("LL" if side > 0 else "RL") + str(i + 1)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


MOBS = {
    "burrow_leech": dict(make=burrow_leech, rig="crawler", ent=(1.0, 0.7), stats=dict(hp=26, speed=0.33, dmg=6, armor=3, kb=0)),
    "marrow_brute": dict(make=marrow_brute, ent=(1.7, 4.0), stats=dict(hp=110, speed=0.18, dmg=15, armor=12, kb=1.0)),
    "bile_priest": dict(make=bile_priest, ent=(0.9, 2.9), stats=dict(hp=40, speed=0.21, dmg=7, armor=3, kb=0)),
    "sinew_stalker": dict(make=sinew_stalker, ent=(0.9, 3.2), stats=dict(hp=36, speed=0.35, dmg=8, armor=2, kb=0)),
    "heart_warden": dict(make=heart_warden, ent=(1.3, 3.5), stats=dict(hp=210, speed=0.22, dmg=13, armor=12, kb=0.7), key=True),
    "still_heart": dict(make=still_heart, rig="crawler", texel=1, ent=(4.0, 4.4),
                        stats=dict(hp=600, speed=0.2, dmg=20, armor=10, kb=1.0), boss=True),
}
