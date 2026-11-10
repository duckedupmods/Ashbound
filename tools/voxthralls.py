"""What a Caller calls. Not dungeon monsters: wraiths bound to the summoner, no legs, burning from the waist down in the colour of
the staff that called them (the flame is painted grey here and tinted in the game). Built like the mounts, drawn by client/ThrallRender.java.

    revenant    a skeletal soldier in a torn mantle, horned iron helm, a long notched blade for a right arm
    champion    a colossal armoured knight of the same order, great horned helm with a burning slit, V shoulders, a two-handed blade
    hollow_king the Crown of the Hollow King's Form, risen behind the wearer (client/HollowKing; --export also writes his grey copy)

    python tools/voxthralls.py [names]             previews for blender -b -P E:/Ashbound/tools/blender/preview_mob.py -- mount_revenant@3.6
    python tools/voxthralls.py --export [names]    assets/ashbound/mounts/NAME.json + textures/entity/mount_NAME.png
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import voxmounts as VM  # noqa: E402
from voxmounts import Kit, plate, cloth, flame, eye, fur, IRON, BONE, GOLD, SILVER, LEATHER, C, ramp  # noqa: E402

GHOST = ramp("#585858", "#808080", "#a8a8a8", "#d0d0d0", "#ececec", "#ffffff")
DARK = ramp("#08060c", "#100c16", "#1a1422", "#261e30", "#342a40")
BLACK_IRON = ramp("#0a0a10", "#14141c", "#202030", "#303044", "#464660", "#6a6a88")


def tongues(k, par, name, at, n, ln, wd, spread):
    """tails of soulfire falling away below a part, the long one behind"""
    for i in range(n):
        a = i * 2.4
        x, z = at[0] + math.cos(a) * spread, at[2] + math.sin(a) * spread - 1
        size = 1 - 0.55 * (i % 3) / 2
        k.seg(par, "%s%d" % (name, i), (x, at[1], z),
              [(wd * size, wd * size * 1.1, ln * size * 0.45, (("x", 172 - (i % 4) * 5), ("z", (i % 3 - 1) * 7))), (wd * size * 0.72, wd * size * 0.8, ln * size * 0.35, (("x", -9),)),
               (wd * size * 0.42, wd * size * 0.5, ln * size * 0.3, (("x", -12),))], "soul" if i % 2 else "soul2", tag="tail", group="glow")


def crest(k, par, name, at, n, ln, wd):
    """flame standing off a helm or shoulder"""
    for i in range(n):
        k.seg(par, "%s%d" % (name, i), (at[0] + (i - (n - 1) / 2) * wd * 0.8, at[1], at[2] - abs(i - (n - 1) / 2) * 0.4),
              [(wd, wd * 1.3, ln * 0.5, (("x", -10 - i * 6), ("z", (i - (n - 1) / 2) * 9))), (wd * 0.6, wd * 0.8, ln * 0.45, (("x", -14),)), (wd * 0.3, wd * 0.4, ln * 0.35, (("x", -10),))],
              "soul2" if i % 2 else "soul", tag="crest", group="glow")


def horn(k, par, name, at, sx, base, ln, mat):
    k.seg(par, name, at, [(base, base, ln * 0.4, (("z", -sx * 62), ("x", -8))), (base * 0.74, base * 0.74, ln * 0.35, (("z", sx * 42),)), (base * 0.42, base * 0.42, ln * 0.3, (("z", sx * 34),))], mat, tag="horn")


def revenant():
    k = Kit("revenant")
    s = k.s
    s.shaders = dict(bone=plate(BONE), iron=plate(BLACK_IRON, SILVER), rag=cloth(DARK), soul=flame(GHOST), soul2=flame(GHOST, 9.0), eye=eye(GHOST), blade=plate(SILVER), hilt=plate(LEATHER))
    k.add(k.part("root", (0, 0, 0)), C(0, 0, 0, 0.4, 0.3, 0.4), "soul", tag="boot", group="glow")
    hips = k.part("hips", (0, 15, 0), (), k.parts["root"])
    torso = k.part("torso", (0, 15, 0), (("x", 9),), hips)
    # the spine, the pelvis, a basket of ribs: you see the fire through them
    k.add(torso, C(0, 13.4, -1.2, 2.2, 15, 2.2), "bone", tag="spine")
    k.add(torso, C(0, 14, 0, 8, 2.4, 5), "bone", tag="pelvis")
    for n in range(5):
        w = 7.4 + 3.2 * math.sin((n + 1) / 6 * math.pi)
        y = 18.4 + n * 2.05
        k.add(torso, C(0, y, 2.2, w, 1.1, 0.9), "bone", tag="rib")
        for sx in (1, -1):
            k.add(torso, C(sx * w / 2, y, 0.6, 0.9, 1.1, 4), "bone", tag="rib")
    k.add(torso, C(0, 21, 0.4, 3.2, 8, 3.2), "soul", tag="heart", group="glow")
    # the mantle: a yoke, torn strips hanging behind and off the sides
    k.add(torso, C(0, 29, -0.4, 16.5, 3.2, 8.4), "rag", tag="yoke")
    for i in range(7):
        x = -7 + i * 2.35
        ln = 13 + 6 * math.sin(i * 2.1) ** 2
        k.add(torso, C(x, 29.6 - ln, -3.8 - abs(x) * 0.1, 2.1, ln, 0.7), "rag", tag="mantle")
    for sx in (1, -1):
        p = k.part("guard_" + ("l" if sx > 0 else "r"), (sx * 8.8, 31, 0), (("z", -sx * 10),), torso)
        k.add(p, C(sx * 9.6, 30, -0.3, 7.4, 4.4, 8.4), "iron", tag="pauldron")
        k.add(p, C(sx * 10.4, 34, -0.3, 5.2, 1.6, 6.4), "iron", tag="pauldron")
        k.seg(p, "pspike%d" % (sx + 1), (sx * 11, 35, -0.3), [(1.7, 1.7, 3.4, (("z", -sx * 18),)), (0.8, 0.8, 2.8, (("z", -sx * 8),))], "bone", tag="spike")
    crest(k, torso, "mfire", (0, 31.6, -3), 5, 7, 2.2)
    # the skull, under an iron helm with horns
    head = k.part("head", (0, 32, 1), (("x", 4),), torso)
    k.add(head, C(0, 34.4, 1.2, 6.8, 6.2, 7), "bone", tag="skull")
    k.add(head, C(0, 32.2, 2.2, 5, 2.4, 5.6), "bone", tag="jaw")
    for x in (-1.8, -0.6, 0.6, 1.8):
        k.add(head, C(x, 33.2, 5.1, 0.8, 1.5, 0.5), "bone", tag="teeth")
    k.add(head, C(0, 38.8, 0.8, 8.4, 2.6, 8.6), "iron", tag="helm")
    k.add(head, C(0, 37.2, 1, 8, 1.8, 8.4), "iron", tag="helm")
    k.add(head, C(0, 37.2, 5.1, 1.6, 3.6, 0.8), "iron", tag="nasal")
    for sx in (1, -1):
        k.add(head, C(sx * 1.9, 35.6, 4.8, 1.7, 1.3, 0.5), "eye", tag="eye", group="glow")
        horn(k, head, "horn%d" % (sx + 1), (sx * 3.6, 39.6, 0.6), sx, 2.2, 13, "bone")
    # the right arm ends in a blade: it has no hand left to hold one with
    for sx, nm in ((1, "l"), (-1, "r")):
        x = sx * 10.2
        arm = k.part("arm_" + nm, (x, 30, 0), (("x", -18 if sx < 0 else 8),), torso)
        k.add(arm, C(x, 21.6, 0, 2.2, 8.8, 2.2), "bone", tag="humerus")
        fore = k.part("fore_" + nm, (x, 21.6, 0), (("x", -52 if sx < 0 else -26),), arm)
        k.add(fore, C(x, 13.4, 0, 1.9, 8.4, 1.9), "bone", tag="ulna")
        k.add(fore, C(x, 15.6, 0, 3.0, 4.6, 3.0), "iron", tag="vambrace")
        if sx < 0:
            k.add(fore, C(x, 11.6, 0, 3.4, 2.2, 3.4), "iron", tag="socket")
            for n in range(9):
                w = 1.0 + 2.6 * math.sin((n + 2) / 11 * math.pi) if n < 8 else 0.9
                k.add(fore, C(x, 9.4 - n * 3.1, 0, 0.7, 3.2, w + (0.5 if n % 3 == 1 else 0)), "blade", tag="blade")
            k.add(fore, C(x, -14, 0.3, 0.9, 25, 0.5), "soul2", tag="edge", group="glow")
        else:
            for n in range(4):
                k.seg(fore, "claw%d" % n, (x + (n - 1.5) * 0.9, 13.4, 0.5), [(0.7, 0.7, 2.6, (("x", 180 - 16), ("z", (n - 1.5) * 10))), (0.5, 0.5, 2.2, (("x", 28),))], "bone", tag="claw")
    tongues(k, torso, "tail", (0, 15, 0), 9, 15, 6.4, 3.4)
    return k


def champion():
    k = Kit("champion")
    s = k.s
    s.shaders = dict(iron=plate(BLACK_IRON, GOLD), plain=plate(BLACK_IRON), gold=plate(GOLD), rag=cloth(DARK, GOLD), soul=flame(GHOST), soul2=flame(GHOST, 9.0), eye=eye(GHOST),
                     blade=plate(SILVER), grip=plate(LEATHER), bone=plate(BONE))
    k.add(k.part("root", (0, 0, 0)), C(0, 0, 0, 0.4, 0.3, 0.4), "soul", tag="boot", group="glow")
    hips = k.part("hips", (0, 18, 0), (), k.parts["root"])
    torso = k.part("torso", (0, 18, 0), (("x", 7),), hips)
    # a plated skirt that ends in fire
    for i in range(8):
        a = i / 8 * math.tau
        x, z = math.sin(a) * 6.2, math.cos(a) * 4.6
        k.add(torso, C(x, 8 + (i % 2) * 1.6, z, 5.2, 11, 3.2), "plain", tag="tasset")
    k.add(torso, C(0, 17, 0, 15, 3, 10), "gold", tag="belt")
    k.add(torso, C(0, 16, 5.2, 4.8, 5, 1.2), "gold", tag="buckle")
    # chest: narrow waist, huge V, a burning core behind a grille
    for n in range(7):
        t = n / 6
        w = 14 + 12 * t * t
        k.add(torso, C(0, 20 + n * 2.3, 0, w, 2.6, 9.6 + 2.6 * t), "iron" if n % 3 == 2 else "plain", tag="cuirass")
    k.add(torso, C(0, 26, 5.6, 6, 7, 1.0), "soul", tag="core", group="glow")
    for x in (-2.4, 0, 2.4):
        k.add(torso, C(x, 25.4, 6.3, 1, 8, 0.8), "gold", tag="grille")
    k.add(torso, C(0, 33.6, 5.8, 9, 1.4, 1), "gold", tag="gorget")
    k.add(torso, C(0, 34, -0.6, 17, 3, 10), "plain", tag="gorget")
    # cape in strips
    for i in range(9):
        x = -11 + i * 2.75
        ln = 22 + 7 * math.sin(i * 1.7) ** 2
        k.add(torso, C(x, 36 - ln, -7 - abs(x) * 0.08, 2.5, ln, 0.8), "rag", tag="cape")
    # great stepped pauldrons, each with a rack of spikes and fire off the top
    for sx, nm in ((1, "l"), (-1, "r")):
        p = k.part("guard_" + nm, (sx * 14, 34, 0), (("z", -sx * 12),), torso)
        for n, (w, h, y) in enumerate(((12.6, 4, 31), (11.4, 3.2, 35), (9, 2.6, 38))):
            k.add(p, C(sx * (15.4 - n * 0.4), y, 0, w, h, 13 - n * 1.6), "iron" if n == 0 else "plain", tag="pauldron")
        k.add(p, C(sx * 16, 34.6, 6.4, 8, 1, 0.8), "gold", tag="trim")
        for n in range(3):
            k.seg(p, "gspike%s%d" % (nm, n), (sx * (13 + n * 2.6), 40, -3.6 + n * 3.6), [(2.6, 2.6, 5.4, (("z", -sx * (6 + n * 8)),)), (1.3, 1.3, 4.6, (("z", -sx * 4),))], "bone", tag="spike")
        crest(k, p, "gfire" + nm, (sx * 15, 40, 0), 3, 8, 2.6)
    # the great helm: tall, closed, a burning slit, horns swept up and back
    head = k.part("head", (0, 36, 1.5), (("x", 6),), torso)
    k.add(head, C(0, 37, 1.4, 9, 9, 10), "iron", tag="helm")
    k.add(head, C(0, 45.6, 1.2, 7.4, 3, 8.4), "iron", tag="helm")
    k.add(head, C(0, 48.2, 0.9, 3.4, 3, 5.4), "gold", tag="helm")
    k.add(head, C(0, 37.2, 6.8, 4, 4.6, 1.2), "plain", tag="visor")
    k.add(head, C(0, 42.4, 6.5, 8, 1.3, 0.8), "eye", tag="eye", group="glow")
    k.add(head, C(0, 39.6, 6.7, 1.2, 2.6, 0.5), "eye", tag="eye", group="glow")
    for sx in (1, -1):
        horn(k, head, "horn%d" % (sx + 1), (sx * 5, 44, 1), sx, 3.6, 24, "bone")
    crest(k, head, "hfire", (0, 50.4, 0), 5, 11, 2.6)
    # arms in plate, both hands on one great blade held point down and out
    for sx, nm in ((1, "l"), (-1, "r")):
        x = sx * 18
        arm = k.part("arm_" + nm, (x, 33, 0), (("x", -34), ("z", sx * 14)), torso)
        k.add(arm, C(x, 21, 0, 6.6, 12, 6.6), "iron", tag="rerebrace")
        fore = k.part("fore_" + nm, (x, 21, 0), (("x", -56), ("z", -sx * 26)), arm)
        k.add(fore, C(x, 9, 0, 6, 12, 6), "iron", tag="vambrace")
        k.add(fore, C(x, 16, 0, 7.2, 3, 7.2), "gold", tag="cuff")
        k.add(fore, C(x, 4.4, 0, 6.8, 5, 7), "plain", tag="gauntlet")
    fore = k.parts["fore_r"]
    blade = k.part("blade", (-18, 5, 0), (("x", 74), ("z", 12)), fore)
    k.add(blade, C(-18, -8, 0, 2.2, 18, 2.2), "grip", tag="grip")
    k.add(blade, C(-18, -11.4, 0, 4, 3.4, 4), "gold", tag="pommel")
    k.add(blade, C(-18, 9, 0, 3, 3, 22), "gold", tag="guard")
    for sz in (1, -1):
        k.add(blade, C(-18, 10.6, sz * 12.4, 2, 4.4, 2), "gold", tag="guard")
    for n in range(15):
        w = 11.4 - n * 0.28 - (1.4 if n % 4 == 3 else 0)
        k.add(blade, C(-18, 12 + n * 4.4, 0, 1.5, 4.6, max(1.6, w)), "blade", tag="blade")
    k.add(blade, C(-18, 12, 0, 1.9, 64, 1.4), "soul", tag="edge", group="glow")
    for n in range(4):
        k.add(blade, C(-18, 72 + n * 2.2, 0, 1.1, 2.4, 4.4 - n * 1.3), "blade", tag="blade")
    tongues(k, torso, "tail", (0, 11, 0), 12, 19, 8.6, 5.2)
    return k


def hollow_king():
    """the Crown of the Hollow King's Form: the king himself, risen behind the one who wears it, drawn in soulfire (all of him
    tinted and see-through in the game; the gold and bone here are only so he reads). Gaunt and tall, no legs, a robe that
    burns away; a standing collar of bone, a crown of seven points and a halo; a spirit greatsword in the right hand."""
    k = Kit("hollow_king")
    U = 8
    s = k.s
    s.shaders = dict(gold=plate(GOLD), bone=plate(BONE), robe=cloth(DARK, GOLD), rag=cloth(DARK), iron=plate(BLACK_IRON, GOLD), soul=flame(GHOST),
                     soul2=flame(GHOST, 9.0), eye=eye(GHOST), blade=plate(SILVER), ghostblade=flame(GHOST, 4.0), grip=plate(LEATHER))
    k.add(k.part("root", (0, 0, 0)), C(0, 0, 0, 0.4, 0.3, 0.4), "soul", tag="boot", group="glow")
    hips = k.part("hips", (0, 20 + U, 0), (), k.parts["root"])
    torso = k.part("torso", (0, 20 + U, 0), (("x", 6),), hips)
    # the robe: long panels flaring out from a gold girdle, ragged at the hem where it goes to fire
    for i in range(10):
        a = i / 10 * math.tau
        x, z = math.sin(a) * 6.6, math.cos(a) * 4.8
        k.add(torso, C(x * (1.05 + 0.25 * (i % 2)), 10 + U / 2 + (i % 3) * 1.4, z * (1.05 + 0.25 * (i % 2)), 4.4, 20 + U - (i % 3) * 2.4, 2.4), "robe", tag="robe")
    k.add(torso, C(0, 19.4 + U, 0, 14, 2.4, 9.4), "gold", tag="girdle")
    k.add(torso, C(0, 18 + U, 5, 3.6, 4.6, 1.2), "gold", tag="clasp")
    # a gaunt chest: open robe either side, the ribs and the burning heart between
    for sx in (1, -1):
        k.add(torso, C(sx * 5.6, 27 + U, 0, 5.4, 14, 8.6), "robe", tag="robe")
    for n in range(5):
        w = 5.6 + 2.6 * math.sin((n + 1) / 6 * math.pi)
        k.add(torso, C(0, 22.4 + U + n * 2.2, 2.6, w, 1.1, 1), "bone", tag="rib")
    k.add(torso, C(0, 24 + U, -0.4, 2.2, 14, 2.2), "bone", tag="spine")
    k.add(torso, C(0, 27 + U, 0.8, 4, 6, 3.4), "soul", tag="heart", group="glow")
    for n in range(4):   # a chain of state across the chest
        k.add(torso, C(-4.5 + n * 3, 31.4 + U - abs(n - 1.5) * 0.8, 4.6, 2.4, 1, 0.8), "gold", tag="chain")
    k.add(torso, C(0, 34 + U, -0.4, 16, 2.6, 9.6), "iron", tag="yoke")
    # the standing collar: a fan of bone blades behind the head, gold between
    for i in range(9):
        a = (i - 4) * 19
        k.seg(torso, "collar%d" % i, (math.sin(math.radians(a)) * 6.4, 35 + U, -3.6 - math.cos(math.radians(a)) * 0.8),
              [(2.4, 1.2, 5.6, (("z", -a * 0.9), ("x", -16))), (1.6, 0.9, 4.6, (("x", -6),)), (0.8, 0.6, 3.2, (("x", -4),))], "bone" if i % 2 else "gold", tag="collar")
    # a long cape in torn strips
    for i in range(11):
        x = -11 + i * 2.2
        ln = 26 + 9 * math.sin(i * 1.9) ** 2
        k.add(torso, C(x, 35 + U - ln, -6.4 - abs(x) * 0.1, 2.1, ln, 0.8), "rag", tag="cape")
    # small high pauldrons of gold, each draped
    for sx, nm in ((1, "l"), (-1, "r")):
        p = k.part("guard_" + nm, (sx * 9.4, 34 + U, 0), (("z", -sx * 10),), torso)
        k.add(p, C(sx * 10.2, 33.6 + U, 0, 7.4, 3.6, 9), "iron", tag="pauldron")
        k.add(p, C(sx * 10.6, 36.4 + U, 0, 5.6, 2, 7.4), "gold", tag="pauldron")
        k.add(p, C(sx * 12.4, 28.6 + U, 0, 1.4, 7, 7.8), "robe", tag="drape")
        crest(k, p, "gfire" + nm, (sx * 10.6, 37.6 + U, 0), 3, 6, 1.8)
    # the head: a long skull, sockets with fire in them, a crown of seven points and a halo behind
    head = k.part("head", (0, 36 + U, 1), (("x", 4),), torso)
    k.add(head, C(0, 40 + U, 1, 6.4, 7.4, 7), "bone", tag="skull")
    k.add(head, C(0, 36.4 + U, 2.2, 4.6, 2.8, 5.4), "bone", tag="jaw")
    for x in (-1.6, -0.5, 0.5, 1.6):
        k.add(head, C(x, 37.6 + U, 4.9, 0.8, 1.4, 0.5), "bone", tag="teeth")
    for sx in (1, -1):
        k.add(head, C(sx * 1.6, 40.6 + U, 4.4, 1.9, 1.7, 0.6), "eye", tag="eye", group="glow")
    k.add(head, C(0, 44.4 + U, 1, 7.6, 1.8, 8), "gold", tag="crown")
    for i in range(7):
        a = i / 7 * math.tau
        x, z = math.sin(a) * 3.3, 1 + math.cos(a) * 3.5
        ln = 6.4 if i == 0 else 4.6
        k.seg(head, "point%d" % i, (x, 45 + U, z), [(1.4, 1.4, ln * 0.55, (("x", -math.cos(a) * 8), ("z", -math.sin(a) * 8))), (0.7, 0.7, ln * 0.45, ())], "gold", tag="crown")
    crest(k, head, "cfire", (0, 46 + U, 1), 5, 9, 1.8)
    for i in range(16):   # the halo: a ring of soulfire standing behind the crown
        a = i / 16 * math.tau
        k.add(head, C(math.sin(a) * 9, 46 + U + math.cos(a) * 9, -6, 2.2, 2.2, 1), "soul2" if i % 2 else "soul", tag="halo", group="glow")
    # long arms; the right holds the great blade up and back, the left hand open, clawed
    for sx, nm in ((1, "l"), (-1, "r")):
        x = sx * 11.6
        arm = k.part("arm_" + nm, (x, 33 + U, 0), (("x", -20), ("z", sx * 10)), torso)
        k.add(arm, C(x, 23.6 + U, 0, 3.4, 10, 3.4), "robe", tag="sleeve")
        fore = k.part("fore_" + nm, (x, 23.6 + U, 0), (("x", -50 if sx < 0 else -30),), arm)
        k.add(fore, C(x, 14.6 + U, 0, 2.2, 9, 2.2), "bone", tag="ulna")
        k.add(fore, C(x, 17.6 + U, 0, 3.6, 3.6, 3.6), "gold", tag="cuff")
        k.add(fore, C(x, 12 + U, 0, 3, 2.6, 3.2), "bone", tag="hand")
        if sx > 0:
            for n in range(4):
                k.seg(fore, "claw%d" % n, (x + (n - 1.5) * 0.8, 12.4 + U, 0.6), [(0.7, 0.7, 3, (("x", 180 - 20), ("z", (n - 1.5) * 12))), (0.5, 0.5, 2.6, (("x", 30),))], "bone", tag="claw")
    fore = k.parts["fore_r"]
    blade = k.part("blade", (-11.6, 13.4 + U, 0), (("x", 70), ("z", 10)), fore)
    k.add(blade, C(-11.6, 9.4 + U, 0, 2, 10, 2), "grip", tag="grip")
    k.add(blade, C(-11.6, 6.4 + U, 0, 3.6, 3, 3.6), "gold", tag="pommel")
    k.add(blade, C(-11.6, 19.4 + U, 0, 3, 3, 18), "gold", tag="guard")
    for n in range(12):
        w = 9 - n * 0.4
        k.add(blade, C(-11.6, 22.4 + U + n * 4.4, 0, 1.4, 4.6, max(1.6, w)), "ghostblade", tag="blade", group="glow")
    k.add(blade, C(-11.6, 22.4 + U, 0, 1.8, 53, 1.2), "soul2", tag="edge", group="glow")
    tongues(k, torso, "tail", (0, 4, 0), 12, 20, 5.5, 4.6)
    return k


def ghost(n):
    """the king's grey copy, which client/HollowKing tints and adds on: brightness only, the dark lifted a little so the robe
    still reads as a faint body, not a hole"""
    from PIL import Image
    tex = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src/main/resources/assets/ashbound/textures/entity")
    img = Image.open(os.path.join(tex, "mount_%s.png" % n)).convert("RGBA")
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            v = int(255 * (0.22 + 0.78 * ((0.3 * r + 0.59 * g + 0.11 * b) / 255) ** 0.8))
            px[x, y] = (v, v, v, a)
    img.save(os.path.join(tex, "mount_%s_ghost.png" % n))


OLD_BONE = ramp("#2e261c", "#4a3e2e", "#6c5c44", "#8e7c5e", "#b09c7a", "#cfbc98")
RUST_IRON = ramp("#120e0c", "#1e1814", "#2e2620", "#423630", "#5a4a40", "#7a6656")


def mass(k, part, x, y0, z, w, h, d, mat, tag):
    """a rounded block of body: two boxes crossed, the corners left off"""
    k.add(part, C(x, y0, z, w, h, d * 0.72), mat, tag=tag)
    k.add(part, C(x, y0 + h * 0.06, z, w * 0.72, h * 0.88, d), mat, tag=tag)


def spikes(k, par, name, at, n, ln, wd, lean, mat, step=(0, 0, 3)):
    """a row of spikes standing out of something, leaning out along lean (degrees about z) and back"""
    for i in range(n):
        o = (at[0] + step[0] * i, at[1] + step[1] * i, at[2] + step[2] * i)
        size = 1 - 0.25 * abs(i - (n - 1) / 2) / max(1, (n - 1) / 2)
        k.seg(par, "%s%d" % (name, i), o, [(wd * size, wd * size, ln * size * 0.55, (("z", lean), ("x", -14))), (wd * size * 0.5, wd * size * 0.5, ln * size * 0.45, (("x", -8),))], mat, tag="spike")


def colossus():
    """the Crown of the Hollow King's beast: what the Caller makes of the thralls they feed it. A hunched giant of their
    fused bones that walks on its knuckles: four arms (two vast ones to walk and slam on, two from its ribs to grab and rake),
    a cage of ribs bound in iron with the eaten thralls' skulls burning inside, a skull sunk low between spiked shoulders under
    a crown of iron spikes."""
    k = Kit("colossus")
    s = k.s
    s.shaders = dict(bone=plate(BONE), old=plate(OLD_BONE), iron=plate(RUST_IRON), band=plate(RUST_IRON), sinew=cloth(DARK), void=plate(DARK),
                     soul=flame(GHOST), soul2=flame(GHOST, 9.0), eye=eye(GHOST))
    k.add(k.part("root", (0, 0, 0)), C(0, 0, 0, 0.4, 0.3, 0.4), "soul", tag="boot", group="glow")
    hips = k.part("hips", (0, 26, -6), (), k.parts["root"])
    mass(k, hips, 0, 22, -6, 17, 7, 11, "old", "pelvis")
    k.add(hips, C(0, 24, -1, 12, 2.4, 1.2), "band", tag="belt")
    # short bowed legs, great clawed feet
    for sx, nm in ((1, "l"), (-1, "r")):
        x = sx * 8
        leg = k.part("leg_" + nm, (x, 25, -6), (("x", -18), ("z", -sx * 8)), hips)
        mass(k, leg, x, 13, -6, 7, 13, 7, "bone", "thigh")
        k.add(leg, C(x, 13.4, -2.6, 5, 4, 1.6), "iron", tag="knee")
        shin = k.part("shin_" + nm, (x, 14, -6), (("x", 30),), leg)
        mass(k, shin, x, 2, -6, 6, 12.4, 6, "old", "shin")
        k.add(shin, C(x, 0, -3.4, 8, 3, 10), "bone", tag="foot")
        for n in range(3):
            k.seg(shin, "toe%s%d" % (nm, n), (x + (n - 1) * 2.6, 1.4, 1.4), [(1.6, 1.6, 3.2, (("x", 100), ("z", (n - 1) * 12))), (1, 1, 2.4, (("x", 30),))], "bone", tag="claw")
    # the body: hunched far over; a spine, then a cage of ribs that widens to the shoulders, bound in iron, fire in it
    torso = k.part("torso", (0, 28, -6), (("x", 38),), hips)
    k.add(torso, C(0, 27, -12, 5, 30, 5), "old", tag="spine")
    for n in range(7):
        t = n / 6
        w, d, y = 17 + 15 * t * t, 13 + 6 * t, 30 + n * 3.3
        k.add(torso, C(0, y, d / 2 - 6, w * 0.75, 2.2, 2.2), "bone", tag="rib")
        for sx in (1, -1):
            k.add(torso, C(sx * w / 2, y, -6, 2.4, 2.2, d), "bone", tag="rib")
            k.add(torso, C(sx * w * 0.42, y, d / 2 - 6.8, 2.6, 2.2, 2.6), "bone", tag="rib")
    for y in (36.4, 46.4):
        w = 17 + 15 * ((y - 30) / 20) ** 2
        k.add(torso, C(0, y, 5.2 + (y - 36) * 0.1, w * 0.86, 2.6, 1.2), "iron", tag="band")
        for sx in (1, -1):
            k.add(torso, C(sx * w * 0.5, y, -6, 1.2, 2.6, 15), "band", tag="band")
    k.add(torso, C(0, 33, -6, 14, 18, 12), "soul", tag="core", group="glow")
    for i, (x, y) in enumerate(((-4.2, 35), (4.2, 37), (0, 42))):   # the thralls it ate, still burning in there
        k.add(torso, C(x, y, 1, 4.4, 4, 4.4), "bone", tag="skull")
        for sx in (1, -1):
            k.add(torso, C(x + sx * 1.1, y + 1.8, 3.25, 1.2, 1, 0.3), "eye", tag="eye", group="glow")
    spikes(k, torso, "dorsal", (0, 34, -14), 6, 9, 3, 0, "bone", step=(0, 4, 0))
    # shoulders: masses of fused plate, iron over them, spikes out of the top
    for sx, nm in ((1, "l"), (-1, "r")):
        g = k.part("guard_" + nm, (sx * 15, 52, -4), (("z", -sx * 8),), torso)
        mass(k, g, sx * 18, 48.6, -4, 13, 8, 15, "bone", "pauldron")
        mass(k, g, sx * 19, 55, -4, 9.6, 3.6, 11.4, "iron", "pauldron")
        k.add(g, C(sx * 19, 54.4, 4.6, 12, 1.4, 1), "band", tag="trim")
        spikes(k, g, "gspike" + nm, (sx * 16, 58.6, -8), 3, 11, 2.8, -sx * 22, "bone", step=(sx * 2.4, 0, 4))
        crest(k, g, "gfire" + nm, (sx * 19, 59, -4), 3, 7, 2.2)
    # the skull: low and forward between the shoulders, a heavy jaw, sockets of fire, a crown of iron spikes
    head = k.part("head", (0, 52, 4), (("x", -44),), torso)
    HZ = 4
    mass(k, head, 0, 48, 5, 8, 8, 9, "old", "neck")
    mass(k, head, 0, 50, 8 + HZ, 11, 9.6, 12, "bone", "skull")
    k.add(head, C(0, 57, 8 + HZ, 12, 2.2, 13), "iron", tag="crown")
    for i in range(5):
        a = (i - 2) * 26
        k.seg(head, "crown%d" % i, (math.sin(math.radians(a)) * 5.4, 58.6, 8 + HZ + math.cos(math.radians(a)) * 5.6 - 5),
              [(1.8, 1.8, 4.4, (("z", -a * 0.5), ("x", -10))), (0.9, 0.9, 3.6, ())], "iron", tag="crown")
    # a heavy brow over deep sockets, the fire far back in them; a long snout, horns swept forward like a bull's
    k.add(head, C(0, 53.6, 13.6 + HZ, 12.4, 2.6, 2.4), "old", tag="brow")
    for sx in (1, -1):
        k.add(head, C(sx * 2.7, 51, 13.7 + HZ, 3.4, 2.6, 0.8), "void", tag="socket")
        k.add(head, C(sx * 2.7, 51.5, 13.9 + HZ, 1.6, 1.4, 0.7), "eye", tag="eye", group="glow")
        k.seg(head, "horn%s" % ("l" if sx > 0 else "r"), (sx * 5.6, 55, 6 + HZ), [(3, 3, 6, (("z", -sx * 80), ("x", 10))), (2.2, 2.2, 5, (("z", sx * 50), ("x", 30))), (1.4, 1.4, 4.4, (("x", 40),))], "bone", tag="horn")
    mass(k, head, 0, 47.6, 16 + HZ, 7, 4.4, 5, "bone", "snout")
    k.add(head, C(0, 49.8, 18.6 + HZ, 3.4, 1.6, 0.6), "void", tag="nose")
    jaw = k.part("jaw", (0, 50, 4), (("x", 6),), head)
    mass(k, jaw, 0, 46, 9 + HZ, 10, 4.2, 11, "old", "jaw")
    mass(k, jaw, 0, 45, 15.4 + HZ, 7.4, 3.4, 5, "old", "jaw")
    for n in range(5):
        k.add(jaw, C(-2.8 + n * 1.4, 48.2, 17.6 + HZ, 0.9, 2, 0.6), "bone", tag="teeth")
    for sx in (1, -1):   # tusks up out of the jaw past the snout
        k.seg(jaw, "tusk%s" % ("l" if sx > 0 else "r"), (sx * 3.4, 47.6, 16.6 + HZ), [(1.6, 1.6, 4, (("z", -sx * 14), ("x", -12))), (1, 1, 3, (("x", -24),))], "bone", tag="tusk")
    crest(k, head, "hfire", (0, 59, 4 + HZ), 4, 8, 2.2)
    # the great arms: hang to the ground, it walks on these fists
    for sx, nm in ((1, "l"), (-1, "r")):
        x = sx * 20
        arm = k.part("arm_" + nm, (x, 50, -3), (("x", -20), ("z", sx * 24)), torso)
        mass(k, arm, x, 34, -3, 9, 16, 9, "bone", "humerus")
        k.add(arm, C(x, 40, -3, 10, 2.6, 10), "band", tag="band")
        fore = k.part("fore_" + nm, (x, 35, -3), (("x", -34), ("z", -sx * 26)), arm)
        mass(k, fore, x, 14, -2, 10, 21, 10, "old", "forearm")
        k.add(fore, C(x, 22, -2, 11.4, 6, 11.4), "iron", tag="gauntlet")
        spikes(k, fore, "vspike" + nm, (x + sx * 5, 25, -5), 3, 6, 2, -sx * 70, "bone", step=(0, -3, 0))
        mass(k, fore, x, 6, 0, 12, 8.4, 12, "bone", "fist")
        for n in range(4):
            k.add(fore, C(x + (n - 1.5) * 2.8, 5.2, 5.6, 2.2, 2.4, 1.6), "iron", tag="knuckle")
    # the rib arms: from the cage's sides, shorter, ending in three hooked claws
    for sx, nm in ((1, "l"), (-1, "r")):
        x = sx * 14
        arm = k.part("arm2_" + nm, (x, 40, 0), (("x", -50), ("z", sx * 18)), torso)
        mass(k, arm, x, 30, 0, 4.4, 11, 4.4, "old", "humerus")
        fore = k.part("fore2_" + nm, (x, 31, 0), (("x", -50),), arm)
        mass(k, fore, x, 19, 0, 4, 12.4, 4, "bone", "forearm")
        for n in range(3):
            k.seg(fore, "hook%s%d" % (nm, n), (x + (n - 1) * 1.4, 19.4, 0.6), [(1, 1, 3.6, (("x", 180 - 14), ("z", (n - 1) * 16))), (0.7, 0.7, 3.2, (("x", -38),))], "bone", tag="claw")
    return k


THRALLS = {"revenant": revenant, "champion": champion, "hollow_king": hollow_king, "colossus": colossus}

if __name__ == '__main__':
    VM.V.T = 2
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    for n in names or THRALLS:
        kit = THRALLS[n]()
        if "--export" in sys.argv:
            kit.export(n)
            if n == "hollow_king":
                ghost(n)
        else:
            VM.M.preview(kit.s, "mount_" + n)
