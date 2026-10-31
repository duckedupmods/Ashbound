"""What a Caller calls. Not dungeon monsters: wraiths bound to the summoner, no legs, burning from the waist down in the colour of
the staff that called them (the flame is painted grey here and tinted in the game). Built like the mounts, drawn by client/ThrallRender.java.

    revenant    a skeletal soldier in a torn mantle, horned iron helm, a long notched blade for a right arm
    champion    a colossal armoured knight of the same order, great horned helm with a burning slit, V shoulders, a two-handed blade

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


THRALLS = {"revenant": revenant, "champion": champion}

if __name__ == '__main__':
    VM.V.T = 2
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    for n in names or THRALLS:
        kit = THRALLS[n]()
        if "--export" in sys.argv:
            kit.export(n)
        else:
            VM.M.preview(kit.s, "mount_" + n)
