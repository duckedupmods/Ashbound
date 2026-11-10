"""The Bound: what the summon staffs call, one kind to each style (StaffSpells.Style), each with its own body. Things from the far side of a gate
that have been made to serve. All their fire is painted grey and takes the colour of the staff in the game.

    riftblade    Blades: tall and thin, no head, a rip burning where it should be, four long arms that end in blades held like a mantis
    cantor       Mages: a great hood with nothing in it but one burning eye, a bell of a robe, a ring of runes behind it, a book that floats
    gatebreaker  Brute: bent double under its own back, one arm a slab of gate-stone in chains, the head sunk between the shoulders
    riftling     Swarm: a low armoured crawler on six legs, one eye in a skull shell, mandibles, a burning sting over its back
    oathwarden   Warband: a knight of no country: tower shield, spear, a banner on its back, a horned closed helm

    python tools/voxbound.py [names]             previews for blender -b -P E:/Ashbound/tools/blender/preview_mob.py -- mount_riftblade@3.6
    python tools/voxbound.py --export [names]    assets/ashbound/mounts/NAME.json + textures/entity/mount_NAME.png
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import voxmounts as VM  # noqa: E402
from voxmounts import Kit, plate, cloth, flame, eye, cracked, GOLD, SILVER, LEATHER, BONE, C, ramp  # noqa: E402
from voxthralls import GHOST, DARK, BLACK_IRON, tongues, crest, horn  # noqa: E402

STONE = ramp("#16141a", "#24222a", "#34323c", "#484650", "#62606c", "#807e8c")
CHITIN = ramp("#0a080e", "#14101a", "#201a2a", "#30283c", "#443a52", "#62566e")
ROBE = ramp("#0c0a12", "#16121e", "#221c2e", "#30283e", "#403650")


def fire(k, torso):
    k.add(k.parts["root"], C(0, 0, 0, 0.4, 0.3, 0.4), "soul", tag="boot", group="glow")


def riftblade():
    k = Kit("riftblade")
    s = k.s
    s.shaders = dict(iron=plate(BLACK_IRON, SILVER), plain=plate(BLACK_IRON), rag=cloth(DARK), bone=plate(BONE), soul=flame(GHOST), soul2=flame(GHOST, 9.0), eye=eye(GHOST), blade=plate(SILVER), hilt=plate(LEATHER))
    k.part("root", (0, 0, 0))
    fire(k, None)
    hips = k.part("hips", (0, 20, 0), (), k.parts["root"])
    torso = k.part("torso", (0, 20, 0), (("x", 16),), hips)
    # a wasp waist, a long ribbed back, a chest like an upturned keel
    for n in range(10):
        t = n / 9
        w = 3.6 + 13 * t ** 1.6
        k.add(torso, C(0, 19 + n * 2.2, 0, w, 2.3, 3.2 + 6 * t), "plain" if n % 2 else "iron", tag="ribs")
    k.add(torso, C(0, 33, 4.6, 1.8, 12, 1.6), "iron", tag="keel")
    for n in range(6):
        k.add(torso, C(0, 21 + n * 3, -3.6 - n * 0.3, 1.6, 2.2, 2.4), "bone", tag="spine")
        k.seg(torso, "sp%d" % n, (0, 22 + n * 3, -4.6 - n * 0.3), [(1.3, 1.3, 3.2 + n * 0.4, (("x", -120),)), (0.6, 0.6, 2.6, (("x", 22),))], "bone", tag="spike")
    # the neck stops, and the world is torn open above it
    head = k.part("head", (0, 41, 0), (("x", -6),), torso)
    k.add(head, C(0, 40.6, 0, 7.4, 1.8, 5.4), "iron", tag="collar")
    k.add(head, C(0, 41.4, 0, 4, 2, 4), "plain", tag="collar")
    for n in range(10):
        w = 0.8 + 3.6 * math.sin((n + 0.5) / 10 * math.pi)
        k.add(head, C((n % 3 - 1) * 0.22, 42.6 + n * 1.8, 0, w, 2, 1.2), "soul", tag="rip", group="glow")
    k.add(head, C(0, 42.6, 0, 1.0, 18, 1.5), "eye", tag="rip", group="glow")
    crest(k, head, "rf", (0, 46, 0), 3, 13, 2.2)
    # four arms, the long upper pair raised, the lower pair folded in: every one a blade from the elbow on
    for sx, nm in ((1, "l"), (-1, "r")):
        for lvl, (y, up, fold, ln) in enumerate(((37.4, -128, -34, 30), (31, -46, -74, 24))):
            x = sx * (8.4 - lvl)
            tag = "%s%d" % (nm, lvl)
            arm = k.part("arm_" + nm if lvl == 0 else "arm2_" + nm, (x, y, 0), (("x", up), ("z", sx * (22 - lvl * 8))), torso)
            k.add(arm, C(x, y - 12, 0, 2.6, 12.4, 2.6), "bone", tag="upper")
            k.add(arm, C(x, y - 4, 0, 4.2, 5, 4.4), "iron", tag="shoulder")
            k.seg(arm, "ks" + tag, (x, y - 3, -1.8), [(1.5, 1.5, 3, (("x", -140),))], "bone", tag="spike")
            fore = k.part("fore_" + nm if lvl == 0 else "fore2_" + nm, (x, y - 12, 0), (("x", fold),), arm)
            k.add(fore, C(x, y - 14.5, 0, 3.6, 3, 3.8), "iron", tag="elbow")
            for n in range(int(ln / 3)):
                t = n / (ln / 3)
                w = 2 + 7.4 * math.sin((t + 0.14) * 2.7) ** 0.8 * (1 - t * 0.3)
                k.add(fore, C(x, y - 17 - n * 3, 0.2 + w * 0.2, 1.1, 3.2, w), "blade", tag="blade")
                if n % 3 == 1:
                    k.add(fore, C(x, y - 17 - n * 3, 0.2 - w * 0.5, 0.9, 1.4, 1.2), "iron", tag="notch")
            k.add(fore, C(x, y - 17 - ln, 0.6, 1.0, ln, 0.5), "soul2", tag="edge", group="glow")
    # a torn mantle off the shoulders, and plates over them like folded wings
    k.add(torso, C(0, 39.4, -1, 24, 3, 11), "iron", tag="yoke")
    for sx in (1, -1):
        for n in range(3):
            k.add(torso, C(sx * (11 + n * 3), 41 + n * 2.4, -1 - n, 9 - n * 1.6, 2.2, 12 - n * 2), "iron" if n % 2 else "plain", tag="plate")
        k.seg(torso, "wing%d" % (sx + 1), (sx * 17, 46, -3), [(3.4, 3.4, 8, (("z", -sx * 30), ("x", -20))), (1.8, 1.8, 7, (("z", sx * 12),)), (0.8, 0.8, 5, (("z", sx * 10),))], "bone", tag="spike")
    for i in range(9):
        x = -10 + i * 2.5
        ln = 20 + 11 * math.sin(i * 2.2) ** 2
        k.add(torso, C(x, 40 - ln, -5.4 - abs(x) * 0.1, 2.3, ln, 0.8), "rag", tag="mantle")
    # what's left below the waist is rags and fire
    for i in range(9):
        a = i / 9 * math.tau
        ln = 11 + 6 * math.sin(i * 2.3) ** 2
        k.add(torso, C(math.sin(a) * 3.2, 19 - ln, math.cos(a) * 2.6 - 1, 1.9, ln, 0.8), "rag", tag="rag")
    tongues(k, torso, "tail", (0, 18, 0), 13, 22, 7.4, 4.6)
    return k


def cantor():
    k = Kit("cantor")
    s = k.s
    s.shaders = dict(robe=cloth(ROBE, GOLD), plain=cloth(ROBE), gold=plate(GOLD), bone=plate(BONE), iron=plate(BLACK_IRON), soul=flame(GHOST), soul2=flame(GHOST, 9.0), eye=eye(GHOST), page=plate(BONE), hide=plate(LEATHER, GOLD))
    k.part("root", (0, 0, 0))
    fire(k, None)
    hips = k.part("hips", (0, 18, 0), (), k.parts["root"])
    torso = k.part("torso", (0, 18, 0), (("x", 6),), hips)
    # a bell of a robe in long hanging panels, open at the front on nothing
    for r, (ring, y, ln, wd) in enumerate(((12, 9.4, 22, 5), (9, 15, 18, 4.4), (8, 21, 14, 3.6))):
        for i in range(ring):
            a = (i + 0.5) / ring * math.tau
            if r == 0 and abs(a - math.pi * 2) < 0.5 or r == 0 and a < 0.5:
                continue
            rad = (15 - r * 3.6)
            drop = 2.4 * math.sin(i * 2.7) ** 2
            k.add(torso, C(math.sin(a) * rad, y - ln * 0.42 + drop, math.cos(a) * rad * 0.82, wd, ln, 2.0), "robe" if i % 3 == 0 else "plain", tag="robe")
    k.add(torso, C(0, 22, 0, 13, 15, 9), "plain", tag="body")
    k.add(torso, C(0, 13, 4, 8, 12, 1), "eye", tag="inside", group="glow")
    # a stole of gold plates down the front
    for n in range(6):
        for sx in (1, -1):
            k.add(torso, C(sx * 3.6, 34 - n * 4.2, 5.2 - n * 0.3, 2.6, 3.6, 1), "gold", tag="stole")
    # shoulders, high and sharp, like a coffin
    k.add(torso, C(0, 36, 0, 27, 3, 11), "robe", tag="yoke")
    for sx in (1, -1):
        k.add(torso, C(sx * 12.6, 38.6, 0, 6, 3, 9), "gold", tag="mantle")
        k.seg(torso, "sh%d" % (sx + 1), (sx * 14, 39.8, 0), [(2.8, 2.8, 6, (("z", -sx * 26),)), (1.3, 1.3, 5, (("z", sx * 8),))], "gold", tag="spike")
    # a deep tall hood, a point at the top, and only an eye in the dark of it
    head = k.part("head", (0, 38, 0), (("x", 9),), torso)
    for n, (w, d, y, z) in enumerate(((15, 15, 42.5, 0), (14, 14.6, 47, -0.6), (12, 13, 51, -1.4), (9, 10.4, 54.6, -2.2), (5.6, 7, 58, -3.2), (2.8, 4, 61, -4.2))):
        k.add(head, C(0, y, z, w, 4.8, d), "plain", tag="hood")
    k.add(head, C(0, 47, 7.6, 16.6, 16, 1.6), "robe", tag="hoodlip")
    k.add(head, C(0, 47.4, 7.2, 10.4, 11.4, 2.6), "iron", tag="dark")
    k.add(head, C(0, 48, 8.4, 5, 2.6, 1), "soul2", tag="eye", group="glow")
    k.add(head, C(0, 48, 8.8, 2.2, 1.8, 0.6), "eye", tag="eye", group="glow")
    # the ring behind it: a wheel of rune-plates in the air
    wheel = k.part("wheel", (0, 50, -10), (), head)
    for i in range(14):
        a = i / 14 * math.tau
        k.add(wheel, C(math.sin(a) * 21, 50 + math.cos(a) * 21, -10, 3.4, 4.6, 1), "gold" if i % 2 else "iron", tag="wheel")
        k.add(wheel, C(math.sin(a) * 21, 50 + math.cos(a) * 21, -9.2, 1.4, 2.4, 0.6), "eye", tag="wheelrune", group="glow")
    # long thin hands, no arms between them and the sleeves
    for sx, nm in ((1, "l"), (-1, "r")):
        arm = k.part("arm_" + nm, (sx * 13, 35, 1), (("x", -26 if sx < 0 else -40), ("z", sx * 12)), torso)
        for n, (w, y) in enumerate(((7, 31), (8.4, 26.4), (10.4, 21), (12.6, 15.4))):
            k.add(arm, C(sx * 14, y, 1, w, 5.6, w), "robe", tag="sleeve")
        fore = k.part("fore_" + nm, (sx * 14, 15, 1), (("x", -36),), arm)
        k.add(fore, C(sx * 14, 8, 1, 3.2, 7, 2.4), "bone", tag="hand")
        for n in range(4):
            k.seg(fore, "fg%s%d" % (nm, n), (sx * 14 + (n - 1.5) * 0.9, 8.2, 1.4), [(0.7, 0.7, 5, (("x", 170), ("z", (n - 1.5) * 8))), (0.5, 0.5, 4, (("x", 24),))], "bone", tag="claw")
    # the book that reads itself, open in the left hand's air
    book = k.part("book", (20, 26, 14), (("x", 58), ("y", -18)), torso)
    k.add(book, C(20, 26, 14, 1.6, 12, 16), "hide", tag="spine")
    for sz in (1, -1):
        k.add(book, C(20 + 1.1, 26, 14 + sz * 8, 1.4, 11, 8), "page", tag="page")
    k.add(book, C(22, 26, 14, 0.5, 8, 12), "eye", tag="pagefire", group="glow")
    tongues(k, torso, "tail", (0, 6, 0), 10, 9, 6.6, 7.4)
    return k


def gatebreaker():
    k = Kit("gatebreaker")
    s = k.s
    s.shaders = dict(hide=cracked(STONE, GHOST, 0.016), stone=plate(STONE), iron=plate(BLACK_IRON, SILVER), chain=plate(BLACK_IRON), bone=plate(BONE), rag=cloth(DARK), soul=flame(GHOST), soul2=flame(GHOST, 9.0), eye=eye(GHOST))
    k.part("root", (0, 0, 0))
    fire(k, None)
    hips = k.part("hips", (0, 25, 0), (), k.parts["root"])
    torso = k.part("torso", (0, 25, 0), (("x", 22),), hips)
    # a hill of a back: wide low hips, then the mass of it going up and forward
    for n in range(9):
        t = n / 8
        w = 22 + 34 * math.sin(t * 2.0) ** 1.3
        k.add(torso, C(0, 22 + n * 4, 0, w, 4.6, 16 + 12 * math.sin(t * 2.4)), "hide", tag="back")
    # the gate it carried out with it, still set in its spine: stone uprights with a rip between
    k.add(torso, C(0, 45, -18, 26, 4, 5), "stone", tag="lintel")
    for sx in (1, -1):
        k.add(torso, C(sx * 12, 32, -17, 6, 22, 6), "stone", tag="upright")
        k.seg(torso, "gs%d" % (sx + 1), (sx * 12, 47, -18), [(5, 5, 6, (("z", -sx * 18),)), (2.6, 2.6, 6, (("z", -sx * 8),))], "stone", tag="spike")
    for n in range(8):
        w = 1 + 6 * math.sin((n + 0.5) / 8 * math.pi)
        k.add(torso, C((n % 3 - 1) * 0.6, 26 + n * 2.6, -17, w, 2.8, 1.4), "soul", tag="rip", group="glow")
    # slag plates and chains hung off it
    for i, (x, y) in enumerate(((-16, 38), (17, 36), (-23, 30), (23, 28), (0, 28))):
        k.add(torso, C(x, y, 13 if i == 4 else 8, 12, 9, 2.4), "iron", tag="plate")
    for sx in (1, -1):
        for n in range(7):
            k.add(torso, C(sx * (26 - n * 0.5), 46 - n * 3, 3 + n * 0.8, 1.6 + (n % 2) * 1.2, 3.2, 2.8 - (n % 2) * 1.2), "chain", tag="chain")
    # a great ridge of bone plates up the spine, and the head thrust out low from under them
    for n in range(6):
        k.seg(torso, "ridge%d" % n, (0, 26 + n * 4, -16 + n * 0.6), [(6 - n * 0.4, 3, 5 + n, (("x", -44),)), (3, 1.6, 4 + n * 0.5, (("x", 14),))], "bone", tag="spike")
    for sx in (1, -1):
        for n in range(4):
            k.add(torso, C(sx * (18 + n * 3), 47 + n * 1.6, 0, 14 - n * 2.2, 3, 22 - n * 3), "stone", tag="ridge")
    head = k.part("head", (0, 46, 14), (("x", 8),), torso)
    k.add(head, C(0, 45, 20, 15, 10, 15), "hide", tag="skull")
    k.add(head, C(0, 50.6, 18, 11, 3.4, 11), "stone", tag="crown")
    k.add(head, C(0, 49.4, 28, 16, 2.6, 3), "stone", tag="brow")
    k.add(head, C(0, 41, 26, 19, 6, 14), "bone", tag="jaw")
    k.add(head, C(0, 45.4, 28, 11, 4.6, 2), "iron", tag="dark")
    for x in (-7.5, -4.5, -1.5, 1.5, 4.5, 7.5):
        k.seg(head, "tu%d" % int(x + 8), (x, 43.6, 32), [(2, 2, 4.4 + abs(x) * 0.5, (("x", 12),)), (0.9, 0.9, 2.4, (("x", -10),))], "bone", tag="tusk")
    for sx in (1, -1):
        k.add(head, C(sx * 3.8, 46.4, 29.2, 3.4, 2.2, 0.6), "eye", tag="eye", group="glow")
        horn(k, head, "horn%d" % (sx + 1), (sx * 8, 48, 22), sx, 4.4, 22, "bone")
    # the right arm long enough to reach the ground, the left ended in the slab
    arm = k.part("arm_r", (-30, 47, 2), (("x", -16), ("z", -16)), torso)
    k.add(arm, C(-30, 44, 2, 22, 11, 22), "iron", tag="pauldron")
    k.add(arm, C(-30, 28, 2, 14, 20, 14), "hide", tag="upper")
    fore = k.part("fore_r", (-30, 18, 2), (("x", -18),), arm)
    k.add(fore, C(-30, 3, 2, 16, 16, 16), "hide", tag="fore")
    k.add(fore, C(-30, -6, 2, 19, 7, 17), "bone", tag="fist")
    for n in range(4):
        k.seg(fore, "cl%d" % n, (-36 + n * 4, -9, 8), [(2.6, 2.6, 5, (("x", 160),))], "bone", tag="claw")
    arm = k.part("arm_l", (30, 47, 2), (("x", 8), ("z", 14)), torso)
    k.add(arm, C(30, 42, 2, 24, 14, 24), "stone", tag="pauldron")
    k.add(arm, C(30, 27, 2, 15, 18, 15), "hide", tag="upper")
    fore = k.part("fore_l", (30, 18, 2), (("x", -26),), arm)
    k.add(fore, C(30, 8, 2, 14, 12, 14), "hide", tag="fore")
    for n, (w, h) in enumerate(((34, 12), (38, 16), (34, 14), (24, 8))):
        k.add(fore, C(30, -3 - n * 12, 2, 9, h, w), "stone", tag="slab")
    for n in range(4):
        k.add(fore, C(35, -8 - n * 10, 2 + (n % 2 - 0.5) * 9, 1, 8, 2), "eye", tag="glyph", group="glow")
    # short thick legs, hooves of stone
    for sx, nm in ((1, "l"), (-1, "r")):
        leg = k.part("leg_" + nm, (sx * 14, 25, 0), (("x", -10),), hips)
        k.add(leg, C(sx * 14, 12, 0, 15, 14, 16), "hide", tag="thigh")
        foot = k.part("shin_" + nm, (sx * 14, 12, 0), (("x", 16),), leg)
        k.add(foot, C(sx * 14, 1, 1, 14, 12, 14), "hide", tag="shin")
        k.add(foot, C(sx * 14, -2, 3, 17, 5, 21), "stone", tag="boot")
    for i in range(10):
        a = i / 10 * math.tau
        k.add(torso, C(math.sin(a) * 15, 18, math.cos(a) * 11, 5, 9 + 3 * (i % 2), 1.4), "rag", tag="rag")
    return k


def riftling():
    k = Kit("riftling")
    s = k.s
    s.shaders = dict(shell=plate(CHITIN, SILVER), plain=plate(CHITIN), bone=plate(BONE), soul=flame(GHOST), soul2=flame(GHOST, 9.0), eye=eye(GHOST))
    k.part("root", (0, 0, 0))
    fire(k, None)
    hips = k.part("hips", (0, 9, 0), (), k.parts["root"])
    torso = k.part("torso", (0, 9, 0), (), hips)
    # a domed segmented back, each plate over the next
    for n in range(7):
        t = n / 6
        w = 10 + 7 * math.sin(t * math.pi)
        k.add(torso, C(0, 8.4 + 3.4 * math.sin(t * math.pi), -9 + n * 3, w, 5 + 3 * math.sin(t * math.pi), 3.4), "shell" if n % 2 else "plain", tag="shell")
        k.seg(torso, "dorsal%d" % n, (0, 13 + 3.4 * math.sin(t * math.pi), -9 + n * 3), [(1.4, 1.8, 2.4 + 1.6 * math.sin(t * math.pi), (("x", -22),)), (0.7, 0.8, 1.6, (("x", -16),))], "bone", tag="spike")
    # a skull for a head, narrow and long, one great socket, mandibles out ahead of it
    head = k.part("head", (0, 10, 10), (("x", 8),), torso)
    for n, (w, h, z) in enumerate(((10, 7, 11), (11.6, 8.4, 13.4), (10.4, 7.4, 15.8), (7.4, 5, 18), (4.4, 3.4, 19.8))):
        k.add(head, C(0, 9.4 + (4 - n) * 0.24, z, w, h, 2.6), "bone", tag="skull")
    k.add(head, C(0, 14.2, 13, 7, 1.8, 6), "shell", tag="crest")
    for sx in (1, -1):
        k.seg(head, "brow%d" % (sx + 1), (sx * 4.2, 13.4, 13), [(1.4, 1.4, 4.4, (("x", -60), ("z", -sx * 26))), (0.7, 0.7, 3, (("x", -18),))], "bone", tag="spike")
    k.add(head, C(0, 11, 18.4, 6.4, 5.4, 1.2), "shell", tag="socket")
    k.add(head, C(0, 11, 19, 4.4, 3.6, 0.8), "soul", tag="eye", group="glow")
    k.add(head, C(0, 11, 19.4, 2, 2, 0.6), "eye", tag="eye", group="glow")
    for x in (-1.4, 0, 1.4):
        k.add(head, C(x, 6.6, 19.6, 0.9, 1.6, 0.8), "bone", tag="teeth")
    for sx in (1, -1):
        k.seg(head, "mand%d" % (sx + 1), (sx * 4, 7.4, 17), [(2.2, 2.8, 6, (("x", 88), ("z", -sx * 26))), (1.6, 1.9, 5.4, (("z", sx * 46),)), (0.8, 1, 3.8, (("z", sx * 40),))], "bone", tag="mandible")
    # six legs out wide and arched high, like something that's hurrying
    for i, z in enumerate((6, -1, -8)):
        for sx, nm in ((1, "l"), (-1, "r")):
            leg = k.part("leg_%s%d" % (nm, i), (sx * 7, 9, z), (("z", -sx * 62), ("x", (i - 1) * 16)), torso)
            k.add(leg, C(sx * 7, 9, z, 2.2, 12, 2.2), "shell", tag="thigh")
            foot = k.part("shin_%s%d" % (nm, i), (sx * 7, 21, z), (("z", -sx * 88),), leg)
            k.add(foot, C(sx * 7, 21, z, 1.5, 13, 1.5), "plain", tag="shin")
            k.add(foot, C(sx * 7, 33, z, 0.7, 3.4, 0.7), "bone", tag="boot")
    # a jointed sting over the back with the fire at its tip
    sting = k.part("sting", (0, 11, -11), (), torso)
    p, at = k.seg(sting, "tail", (0, 11, -11), [(4.6, 4.6, 5.4, (("x", -62),)), (3.8, 3.8, 5.4, (("x", 26),)), (3.2, 3.2, 5, (("x", 34),)), (2.6, 2.6, 4.6, (("x", 36),)), (1.9, 1.9, 3.8, (("x", 36),))], "shell", tag="tail")
    k.add(p, C(at[0], at[1], at[2], 3.2, 4, 3.2), "bone", tag="sting")
    k.add(p, C(at[0], at[1] + 3.6, at[2], 1.2, 5, 1.2), "soul2", tag="stingfire", group="glow")
    crest(k, p, "stf", (at[0], at[1] + 3, at[2]), 3, 7, 1.6)
    return k


def oathwarden():
    k = Kit("oathwarden")
    s = k.s
    s.shaders = dict(iron=plate(BLACK_IRON, SILVER), plain=plate(BLACK_IRON), silver=plate(SILVER), rag=cloth(DARK, SILVER), banner=cloth(DARK, GOLD), gold=plate(GOLD), grip=plate(LEATHER), bone=plate(BONE), soul=flame(GHOST), soul2=flame(GHOST, 9.0), eye=eye(GHOST))
    k.part("root", (0, 0, 0))
    fire(k, None)
    hips = k.part("hips", (0, 19, 0), (), k.parts["root"])
    torso = k.part("torso", (0, 19, 0), (("x", 4),), hips)
    for n in range(7):
        t = n / 6
        k.add(torso, C(0, 20 + n * 2.5, 0, 18 + 16 * t ** 1.5, 2.8, 11 + 5 * t), "plain" if n % 2 else "iron", tag="cuirass")
    k.add(torso, C(0, 18, 0, 15, 3, 10), "iron", tag="belt")
    k.add(torso, C(0, 29, 6.6, 8, 11, 1.2), "silver", tag="breast")
    k.add(torso, C(0, 29, 7.4, 2, 9, 0.8), "soul", tag="seam", group="glow")
    for i in range(8):
        a = i / 8 * math.tau
        k.add(torso, C(math.sin(a) * 7, 10.4, math.cos(a) * 5, 4.6, 11, 2.4), "iron" if i % 2 else "plain", tag="tasset")
    for i in range(7):
        x = -9 + i * 3
        ln = 15 + 6 * math.sin(i * 1.9) ** 2
        k.add(torso, C(x, 36 - ln, -7, 2.8, ln, 0.8), "rag", tag="cape")
    # a banner on a tall pole across the back, torn, past the height of the helm
    k.add(torso, C(9, 52, -8.6, 2, 44, 2), "grip", tag="pole")
    k.add(torso, C(9, 73, -8.6, 3, 3, 3), "gold", tag="finial")
    k.seg(torso, "fin", (9, 75, -8.6), [(1.6, 1.6, 6, ()), (0.7, 0.7, 4, ())], "gold", tag="spike")
    k.add(torso, C(9, 71, -8.6, 22, 1.8, 1.6), "grip", tag="crossbar")
    for i in range(7):
        x = -9 + i * 3
        ln = 22 - abs(i - 3) * 2 + 3 * math.sin(i * 2.4)
        k.add(torso, C(x + 9, 71 - ln, -9.8, 2.9, ln, 0.7), "banner", tag="banner")
    k.add(torso, C(9, 61, -10.4, 7, 9, 0.5), "soul", tag="sigil", group="glow")
    for sx, nm in ((1, "l"), (-1, "r")):
        p = k.part("guard_" + nm, (sx * 16, 36, 0), (("z", -sx * 14),), torso)
        for n, (w, h, y) in enumerate(((18, 5, 33), (15, 4, 37.6), (11, 3, 41))):
            k.add(p, C(sx * (15.6 - n * 0.6), y, 0, w, h, 17 - n * 2.4), "iron", tag="pauldron")
        k.seg(p, "gs" + nm, (sx * 16, 42, 0), [(3, 3, 5, (("z", -sx * 22),)), (1.3, 1.3, 5, (("z", -sx * 8),))], "bone", tag="spike")
    # the great closed helm, one vertical burning slit, horns low and forward like a bull's
    head = k.part("head", (0, 38, 1), (("x", 6),), torso)
    k.add(head, C(0, 39, 1.2, 12, 11, 12), "iron", tag="helm")
    k.add(head, C(0, 46, 1, 10, 3, 10), "silver", tag="helm")
    k.add(head, C(0, 47.4, 0.8, 1.6, 3, 8), "gold", tag="crest")
    k.add(head, C(0, 40, 7.5, 1.5, 8, 0.6), "eye", tag="eye", group="glow")
    for sx in (1, -1):
        k.seg(head, "horn%d" % (sx + 1), (sx * 4.6, 43, 2), [(3.4, 3.4, 7, (("z", -sx * 82),)), (2.3, 2.3, 7, (("x", 54),)), (1, 1, 6, (("x", 38),))], "bone", tag="horn")
    crest(k, head, "hf", (0, 49, 0), 3, 10, 2.4)
    # left: the wall of a shield. right: the spear, level.
    arm = k.part("arm_l", (22, 34, 0), (("x", -28), ("z", 12)), torso)
    k.add(arm, C(23, 25, 0, 8.4, 11, 8.4), "iron", tag="rerebrace")
    fore = k.part("fore_l", (23, 24, 0), (("x", -44),), arm)
    k.add(fore, C(23, 16, 0, 8, 10, 8), "iron", tag="vambrace")
    shield = k.part("shield", (24, 14, 0), (("x", 72), ("y", 10)), fore)
    k.add(shield, C(25, -17, 0, 1.8, 62, 26), "iron", tag="shield")
    k.add(shield, C(26.2, -14, 0, 1, 56, 21), "plain", tag="shield")
    for n in range(4):
        k.add(shield, C(26.8, -12 + n * 15, 0, 0.7, 2, 22), "silver", tag="band")
    k.add(shield, C(27.2, -6, 0, 0.7, 40, 2.4), "soul", tag="seam", group="glow")
    k.add(shield, C(27.4, 8, 0, 1, 12, 12), "gold", tag="boss")
    k.seg(shield, "sp", (26, 14, 0), [(5, 5, 6, (("z", -90),)), (2, 2, 6, ())], "bone", tag="spike")
    arm = k.part("arm_r", (-22, 34, 0), (("x", -30), ("z", -8)), torso)
    k.add(arm, C(-23, 25, 0, 8.4, 11, 8.4), "iron", tag="rerebrace")
    fore = k.part("fore_r", (-23, 24, 0), (("x", -62),), arm)
    k.add(fore, C(-23, 16, 0, 8, 10, 8), "iron", tag="vambrace")
    spear = k.part("spear", (-23, 10, 0), (("x", 4),), fore)
    k.add(spear, C(-23, 18, 0, 1.8, 74, 1.8), "grip", tag="shaft")
    k.add(spear, C(-23, 54, 0, 3.4, 3, 3.4), "gold", tag="socket")
    for n in range(8):
        w = 6.4 * math.sin((n + 1.4) / 9.4 * math.pi)
        k.add(spear, C(-23, 57 + n * 3, 0, w, 3.2, 1.1), "silver", tag="head")
    k.add(spear, C(-23, 57, 0, 0.9, 24, 1.3), "soul2", tag="edge", group="glow")
    tongues(k, torso, "tail", (0, 10, 0), 10, 16, 7.4, 4.2)
    return k


BOUND = {"riftblade": riftblade, "cantor": cantor, "gatebreaker": gatebreaker, "riftling": riftling, "oathwarden": oathwarden}

if __name__ == '__main__':
    VM.V.T = 2
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--export" not in sys.argv:
        GHOST = VM.SOUL
    VM.HOT |= {c[:3] for c in GHOST}   # what burns in a hide: drawn again in the staff's colour
    for n in names or BOUND:
        kit = BOUND[n]()
        if "--export" in sys.argv:
            kit.export(n)
        else:
            VM.M.preview(kit.s, "mount_" + n)
