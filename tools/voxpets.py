"""Pets: small companions worn in the Curios pet slot, each a body plan with its own colours and extras. Same painted boxes as
tools/voxmounts.py. Units: 1 = 1/16 block, facing +z, y up, x to its left.

    quad, newt    trots at your heel     bird, drake, moth, skull, wisp    flies beside you

    python tools/voxpets.py [names]     previews for blender -b -P <scratchpad>/pet_shot.py -- pet_NAME@HEIGHT
    python tools/voxpets.py --bag       the Bottomless Bag's pouch, its box to paste into client/PetRender
    python tools/voxpets.py --export    bones in assets/ashbound/mounts/pet_NAME.json, item models, resources/ashbound/pets.json, the Curios tag
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import voxmounts as VM  # noqa: E402
from voxmounts import Kit, fur, plate, flame, glow, eye, EMBER, GOLD, BONE, SOUL, FROST_FIRE, HOOF, ramp, M, V, C, Part  # noqa: E402

SOOT = ramp("#08070a", "#111015", "#1c1a22", "#2a2732", "#3c3846")
RIME = ramp("#7c93ad", "#a2b8cc", "#c6d8e6", "#e2eef6", "#f6fbff")
TAWNY = ramp("#6a2c0c", "#94420f", "#c05e16", "#e07c24", "#f09a44")
CREAM = ramp("#b09a78", "#cfbb98", "#e6d6b8", "#f4ead6", "#fff8ea")
MOTH = ramp("#6e6250", "#94866e", "#b8aa90", "#d8ccb4", "#efe6d2")
MOSS = ramp("#1c2c14", "#2c4420", "#40602c", "#5a803a", "#7ca24c")
IRONISH = ramp("#2a2a34", "#3c3c4a", "#555566", "#74748a", "#9c9cb0")
BLOOD = ramp("#2a0608", "#4a0c10", "#74141a", "#a02026", "#c83a3a")
LEATHER = ramp("#2c160a", "#46240f", "#643618", "#845024", "#a06a34")
DUSK = ramp("#160c2c", "#261648", "#3a2268", "#50328c", "#6c48b0")


def shaders(s, coat, under, horn, shine, flames=None):
    s.shaders = dict(coat=fur(coat, 0.35, 0.28), under=fur(under, 0.2, 0.2), horn=plate(horn), trim=plate(GOLD), dark=fur(SOOT, 0.1, 0.1), eye=eye(shine), shine=glow(shine, 0.4))
    if flames:
        s.shaders.update(fire=flame(flames), fire2=flame(flames, 7.0))


def bird(name, coat, under, beak, shine, kind="crow", plume=None):
    """Upright as a perched bird stands: slim, leaning forward, wings folded down its sides, a long tail low behind it. An owl
    is a wide round head and a flat face; everything else looks out of the side of a small head over a long beak."""
    k = Kit(name)
    shaders(k.s, coat, under, beak, shine, plume)
    owl = kind == "owl"
    hips = k.part("hips", (0, 1.6, 0))
    torso = k.part("torso", (0, 1.6, 0), (("x", 6 if owl else 20),), hips)
    fat = 1.25 if owl else 1
    k.loaf(torso, "y", 1.4, 7.0, 6, lambda t: (fat * (3.2 + 2.0 * (1 - abs(t - 0.35) * 1.6)), fat * (4.0 + 1.6 * (1 - abs(t - 0.35) * 1.6)), 0), "coat", "body")
    k.add(torso, C(0, 2.2, 1.9 * fat, 3.0 * fat, 4.2, 1.5), "under", tag="chest")
    head = k.part("head", (0, 6.8, 0.5), (("x", -6 if owl else -24),), torso)
    if owl:
        y, z = 6.8, 0.8
        k.add(head, C(0, y, z, 6.6, 3.6, 5.0), "coat", tag="skull")
        k.add(head, C(0, y + 0.5, z, 7.4, 2.6, 4.2), "coat", tag="skull")
        k.add(head, C(0, y + 3.5, z, 5.0, 0.9, 3.6), "coat", tag="skull")
        front = z + 2.5
        for sx in (1, -1):
            k.add(head, C(sx * 1.65, y + 0.4, front + 0.1, 3.0, 3.0, 0.4), "under", tag="disc")
            k.add(head, C(sx * 1.65, y + 1.0, front + 0.35, 1.7, 1.7, 0.3), "eye", tag="eye", group="glow")
            k.add(head, C(sx * 1.65, y + 1.5, front + 0.55, 0.7, 0.7, 0.3), "dark", tag="pupil")
            p = Part("tuft%d" % (sx > 0), (sx * 2.5, y + 3.7, z + 1.0), (("z", sx * -22), ("x", 8)), head)
            k.add(p, C(sx * 2.5, y + 3.7, z + 1.0, 1.5, 1.5, 1.2), "coat", tag="tuft")
            k.add(p, C(sx * 2.5, y + 5.1, z + 1.0, 0.8, 1.0, 0.8), "coat", tag="tuft")
        k.add(head, C(0, y + 0.1, front + 0.2, 1.0, 1.5, 1.0), "horn", tag="beak")
    else:
        y, z = 6.7, 0.9
        k.add(head, C(0, y, z, 3.4, 3.0, 3.8), "coat", tag="skull")
        k.add(head, C(0, y + 0.5, z, 3.9, 2.0, 3.0), "coat", tag="skull")
        k.add(head, C(0, y + 3.0, z, 2.4, 0.5, 2.4), "coat", tag="skull")
        front = z + 1.9
        k.add(head, C(0, y + 0.9, front + 0.9, 1.9, 1.3, 1.9), "horn", tag="beak")
        k.add(head, C(0, y + 1.1, front + 2.4, 1.3, 0.9, 1.5), "horn", tag="beak")
        k.add(head, C(0, y + 1.1, front + 3.4, 0.7, 0.6, 0.8), "horn", tag="beak")
        k.add(head, C(0, y + 0.45, front + 0.9, 1.6, 0.5, 1.9), "dark", tag="beak")
        for sx in (1, -1):
            k.add(head, C(sx * 1.95, y + 1.1, z + 0.7, 0.3, 1.5, 1.5), "dark", tag="socket")
            k.add(head, C(sx * 2.1, y + 1.3, z + 0.8, 0.3, 1.05, 1.05), "eye", tag="eye", group="glow")
        for n in range(3 if plume else 0):
            p = Part("crest%d" % n, (0, y + 3.2, z + 1.2 - n * 1.3), (("x", -24 - n * 18),), head)
            k.add(p, C(0, y + 3.2, z + 1.2 - n * 1.3, 1.1, 3.4 - n * 0.3, 1.1), "fire" if n % 2 else "fire2", tag="crest", group="glow")
    for sx in (1, -1):
        wing = k.part("arm_" + ("l" if sx > 0 else "r"), (sx * 2.4 * fat, 6.2, 0), (("z", sx * 3), ("x", -10)), torso)
        k.add(wing, C(sx * 2.6 * fat, 2.4, -0.4, 0.9, 3.8, 3.4), "coat", tag="wing")
        k.add(wing, C(sx * 2.6 * fat, 1.0, -1.2, 0.8, 2.2, 2.2), "dark", tag="wing")
        tip = k.part("fore_" + ("l" if sx > 0 else "r"), (sx * 2.6 * fat, 1.0, -1.6), (("x", -24),), wing)
        k.add(tip, C(sx * 2.6 * fat, -1.6, -1.8, 0.7, 2.8, 1.4), "fire" if plume else "dark", tag="wing", group="glow" if plume else "lit")
        k.add(hips, C(sx * 1.1, 0, 0.3, 0.9, 1.8, 0.9), "horn", tag="leg")
        k.add(hips, C(sx * 1.1, 0, 0.9, 1.2, 0.5, 2.4), "horn", tag="boot")
    tail = k.part("tail", (0, 2.4, -1.6), (("x", -138),), torso)
    long = 11 if plume else 3.4 if owl else 6.4
    for n, dx in enumerate((-1.0, 0, 1.0)):
        k.add(tail, C(dx, 2.4, -1.6, 1.1, long + (n == 1) * 1.6, 0.6), ("fire" if n != 1 else "fire2") if plume else "coat", tag="tail", group="glow" if plume else "lit")
    return k


def quad(name, coat, under, horn, shine, snout, ears, tailw, flames=None, cracks=False, brush=False, socks=False, tailn=4):
    """On four feet, bones named as the mounts' so the same gaits walk it: a cat's short face, or a pup's long one with a brush."""
    k = Kit(name)
    shaders(k.s, coat, under, horn, shine, flames)
    hips = k.part("hips", (0, 6.6, -3.4))
    torso = k.part("torso", (0, 6.6, -3.4), (("x", -3),), hips)
    k.loaf(torso, "z", -5.4, 3.8, 6, lambda t: (4.6 + 0.7 * t, 4.2 + 0.7 * t, 8.6), "coat", "barrel")
    k.add(torso, C(0, 5.0, -0.8, 3.2, 1.0, 6.4), "under", tag="belly")
    if cracks:
        for n, (x, z) in enumerate(((1.4, -3.4), (-1.0, -1.4), (0.6, 0.8), (-1.5, 2.4))):
            k.add(torso, C(x, 8.9, z, 1.5, 0.3, 0.5), "fire" if flames else "shine", tag="crack", group="glow")
    for sx, nm in ((1, "l"), (-1, "r")):
        for z, a, b, c in ((-3.8, "thigh_", "shin_", "foot_"), (2.6, "arm_", "fore_", "hand_")):
            up, low, ft = k.leg(torso, (a + nm, b + nm, c + nm), sx * 1.8, 6.6, z, (1.9, 2.0, 0.7), ((1.9, 2.4), (1.4, 1.5), (1.7, 2.3)), (0, 0, 0), ("coat", "dark" if socks else "coat", "dark" if socks else "under"), tag="leg")
    neck = k.part("neck", (0, 9.4, 3.6), (("x", 28),), torso)
    k.add(neck, C(0, 8.8, 3.6, 3.6, 3.0, 3.4), "coat", tag="neck")
    head = k.part("head", (0, 11.2, 4.4), (("x", -28),), neck)
    y, z = 10.6, 4.6
    k.add(torso, C(0, 6.2, 3.9, 3.4, 3.0, 0.8), "under", tag="chest")
    k.add(head, C(0, y, z, 6.0, 4.6, 4.8), "coat", tag="skull")
    k.add(head, C(0, y + 0.5, z, 6.8, 3.0, 3.6), "coat", tag="skull")
    k.add(head, C(0, y + 0.1, z + 2.2 + snout / 2, 2.6, 1.9, snout), "under", tag="muzzle")
    k.add(head, C(0, y + 1.6, z + 2.3 + snout, 1.1, 0.7, 0.4), "dark", tag="nose")
    k.add(head, C(0, y - 0.1, z + 2.2 + snout * 0.45, 1.9, 0.5, snout * 0.8), "dark", tag="mouth")
    for sx in (1, -1):
        k.add(head, C(sx * 1.5, y + 2.0, z + 2.05, 1.5, 1.4, 0.3), "dark", tag="socket")
        k.add(head, C(sx * 1.55, y + 2.2, z + 2.2, 0.95, 1.0, 0.3), "eye", tag="eye", group="glow")
        k.add(head, C(sx * 1.5, y + 3.2, z + 1.9, 1.8, 0.4, 0.6), "dark", tag="brow")
        p = Part("ear%d" % (sx > 0), (sx * 1.8, y + 3.9, z - 0.2), (("z", sx * -12), ("x", -6)), head)
        k.add(p, C(sx * 2.0, y + 4.3, z - 0.2, 2.4, ears * 0.42, 1.2), "coat", tag="ear")
        k.add(p, C(sx * 2.0, y + 4.3 + ears * 0.38, z - 0.2, 1.5, ears * 0.36, 1.0), "coat", tag="ear")
        k.add(p, C(sx * 2.0, y + 4.3 + ears * 0.7, z - 0.2, 0.7, ears * 0.3, 0.8), "dark" if socks else "coat", tag="ear")
        k.add(p, C(sx * 2.0, y + 4.4, z + 0.45, 1.2, ears * 0.45, 0.3), "under", tag="ear")
    tail = k.part("tail", (0, 8.6, -5.0), (("x", -96 if brush else -30),), torso)
    k.add(tail, C(0, 8.6, -5.0, tailw * 0.6, 2.4, tailw * 0.6), "coat", tag="tail")
    part, at = tail, (0, 10.6, -5.0)
    for n in range(tailn):
        w = tailw * (0.8 + 0.7 * (1 - abs(n - 1.8) / 1.8)) if brush else tailw * 0.9
        part = k.part("tails%d" % n, at, (("x", -8 if brush else 14),), part)
        last = n == tailn - 1
        k.add(part, C(0, at[1], at[2], w, 2.4, w), ("fire" if flames else "under") if last else "coat", tag="tail", group="glow" if last and flames else "lit")
        at = (0, at[1] + 2.2, at[2])
    return k


def moth(name, coat, under, shine, spots):
    """Four stepped wings held out flat on a furred body, feather feelers, a lit belly: it hovers, so the belly is its floor."""
    k = Kit(name)
    k.s.shaders = dict(coat=fur(coat, 0.3, 0.3), under=fur(under, 0.2, 0.2), dark=fur(SOOT, 0.1, 0.1), eye=eye(shine), shine=glow(shine, 0.3), spot=glow(spots, 0.5))
    body = k.part("hips", (0, 2.4, 0))
    k.loaf(body, "z", -3.6, 2.4, 5, lambda t: (2.0 + 1.5 * t, 2.2 + 1.5 * t, 3.2), "coat", "body")
    k.add(body, C(0, 1.1, -2.0, 1.9, 1.2, 3.0), "shine", tag="boot", group="glow")
    k.add(body, C(0, 2.0, 2.6, 3.8, 2.8, 2.4), "under", tag="ruff")
    k.add(body, C(0, 2.3, 4.0, 2.6, 2.2, 1.4), "coat", tag="head")
    for sx in (1, -1):
        nm = "l" if sx > 0 else "r"
        k.add(body, C(sx * 1.05, 3.0, 4.75, 0.9, 1.0, 0.3), "eye", tag="eye", group="glow")
        up = k.part("arm_" + nm, (sx * 1.2, 3.6, 1.0), (("z", sx * -14),), body)
        for x, z, w, d in ((3.2, 1.6, 5.0, 4.6), (6.0, 2.2, 4.4, 4.6), (8.4, 2.6, 2.6, 3.4)):
            k.add(up, C(sx * x, 3.6, z, w, 0.4, d), "under", tag="wing")
        k.add(up, C(sx * 6.0, 3.65, 3.9, 6.4, 0.4, 0.9), "dark", tag="edge")
        k.add(up, C(sx * 5.4, 3.75, 1.8, 2.0, 0.3, 2.0), "spot", tag="spot", group="glow")
        k.add(up, C(sx * 5.4, 3.8, 1.8, 0.9, 0.3, 0.9), "dark", tag="pupil")
        low = k.part("arm_low_" + nm, (sx * 1.2, 3.4, -0.8), (("z", sx * -8),), body)
        for x, z, w, d in ((2.8, -2.2, 4.4, 4.2), (5.0, -2.6, 3.0, 3.4)):
            k.add(low, C(sx * x, 3.4, z, w, 0.4, d), "coat", tag="wing")
        k.add(low, C(sx * 3.6, 3.5, -2.6, 1.6, 0.3, 1.6), "spot", tag="spot", group="glow")
        for n in range(4):
            p = Part("feel%d%d" % (sx > 0, n), (sx * (0.7 + n * 0.45), 3.4 + n * 0.1, 4.6 + n * 0.8), (("z", sx * -60),), body)
            k.add(p, C(sx * (0.7 + n * 0.45), 3.4 + n * 0.1, 4.6 + n * 0.8, 0.3, 1.4 - n * 0.1, 0.5), "dark", tag="feeler")
    return k


def drake(name, coat, under, horn, shine, flames=None, wings=True):
    """A hatchling: all head and elbows, wing stubs held up, a fat tail wrapped round to one side."""
    k = Kit(name)
    shaders(k.s, coat, under, horn, shine, flames)
    hips = k.part("hips", (0, 3.6, -1.4))
    torso = k.part("torso", (0, 3.6, -1.4), (("x", -24),), hips)
    k.loaf(torso, "z", -3.0, 4.2, 5, lambda t: (4.6 + 1.0 * t, 4.4 + 1.0 * t, 5.6), "coat", "barrel")
    k.add(torso, C(0, 2.9, 0.8, 3.6, 1.0, 5.6), "under", tag="belly")
    for n in range(4):
        k.add(torso, C(0, 7.6 + n * 0.1, -2.2 + n * 1.8, 0.7, 1.2 - n * 0.1, 1.2), "horn", tag="spine")
    for sx, nm in ((1, "l"), (-1, "r")):
        k.leg(hips, ("thigh_" + nm, "shin_" + nm, "foot_" + nm), sx * 2.3, 4.0, -2.0, (2.0, 1.4, 0.7), ((2.4, 3.0), (1.6, 1.8), (2.0, 3.2)), (0, 0, 0), ("coat", "coat", "horn"), feet="boot", tag="leg")
        k.leg(hips, ("foreleg_" + nm, "forelow_" + nm, "forefoot_" + nm), sx * 2.0, 4.2, 2.4, (2.0, 1.6, 0.6), ((1.7, 2.0), (1.3, 1.5), (1.7, 2.2)), (0, 0, 0), ("coat", "coat", "horn"), feet="boot", tag="leg")
        if wings:
            wing = k.part("arm_" + nm, (sx * 2.6, 7.2, 0.2), (("z", sx * -38), ("x", -14)), torso)
            k.add(wing, C(sx * 2.6, 7.2, 0.2, 0.9, 4.2, 1.1), "coat", tag="wing")
            k.add(wing, C(sx * 2.6, 7.6, -1.6, 0.3, 3.4, 3.0), "under", tag="membrane")
            k.add(wing, C(sx * 2.6, 11.2, 0.2, 0.7, 1.4, 0.7), "horn", tag="wing")
    y, z = 8.2, 3.8
    head = k.part("head", (0, 7.4, 3.0), (("x", 16),), torso)
    k.add(head, C(0, y, z, 6.0, 4.6, 5.0), "coat", tag="skull")
    k.add(head, C(0, y + 0.2, z + 3.1, 3.8, 2.4, 2.6), "coat", tag="muzzle")
    k.add(head, C(0, y - 0.2, z + 3.1, 3.2, 0.7, 2.8), "under", tag="jaw")
    for sx in (1, -1):
        k.add(head, C(sx * 1.05, y + 2.0, z + 4.2, 0.6, 0.5, 0.3), "dark", tag="nostril")
        k.add(head, C(sx * 2.05, y + 2.1, z + 2.4, 1.6, 1.7, 0.3), "dark", tag="socket")
        k.add(head, C(sx * 2.1, y + 2.3, z + 2.55, 1.05, 1.2, 0.3), "eye", tag="eye", group="glow")
        k.add(head, C(sx * 2.0, y + 3.7, z + 1.9, 2.2, 0.5, 1.0), "horn", tag="brow")
        if wings:
            k.seg(head, "dhorn%d" % (sx > 0), (sx * 2.1, y + 4.0, z - 1.6), [(1.3, 1.3, 2.2, (("x", -58), ("z", sx * -16))), (0.8, 0.8, 1.8, (("x", 16),)), (0.4, 0.4, 1.2, (("x", 12),))], "horn", tag="horn")
        k.add(head, C(sx * 3.2, y + 1.6, z + 0.2, 0.4, 2.0, 2.0), "under", tag="frill")
    part, at = k.part("tail", (0, 6.0, -4.0), (("x", -112), ("z", 26)), torso), (0, 6.0, -4.0)
    for n in range(5):
        w = 3.2 - n * 0.48
        part = k.part("tails%d" % n, at, (("z", 12),), part)
        last = flames and n == 4
        k.add(part, C(0, at[1], at[2], w, 2.4, w), "fire" if last else "coat", tag="tail", group="glow" if last else "lit")
        at = (0, at[1] + 2.2, at[2])
    return k


def skull(name, bone, shine, flames):
    """A skull with a candle stuck to the crown: it floats, its jaw working slowly."""
    k = Kit(name)
    shaders(k.s, bone, IRONISH, bone, shine, flames)
    head = k.part("head", (0, 2.4, 0))
    k.add(head, C(0, 2.6, 0, 6.6, 4.6, 6.2), "coat", tag="skull")
    k.add(head, C(0, 3.2, 0, 7.2, 3.0, 5.2), "coat", tag="skull")
    k.add(head, C(0, 1.0, 1.4, 4.8, 1.8, 3.4), "coat", tag="cheek")
    for sx in (1, -1):
        k.add(head, C(sx * 1.6, 3.6, 3.0, 2.0, 1.9, 0.3), "dark", tag="socket")
        k.add(head, C(sx * 1.6, 4.0, 3.15, 1.0, 1.0, 0.3), "eye", tag="eye", group="glow")
    k.add(head, C(0, 2.5, 3.05, 1.0, 0.9, 0.3), "dark", tag="nose")
    for x in (-1.6, -0.55, 0.55, 1.6):
        k.add(head, C(x, 1.0, 3.1, 0.7, 0.9, 0.3), "under", tag="tooth")
    jaw = k.part("jaw", (0, 1.2, -0.8), (), head)
    k.add(jaw, C(0, 0, 1.2, 4.4, 1.0, 3.8), "coat", tag="boot")
    for x in (-1.4, 0, 1.4):
        k.add(jaw, C(x, 0.9, 3.0, 0.7, 0.6, 0.3), "under", tag="tooth")
    k.add(head, C(1.2, 7.1, -0.6, 2.2, 0.5, 2.2), "dark", tag="dish")
    k.add(head, C(1.2, 7.5, -0.6, 1.3, 2.4, 1.3), "under", tag="candle")
    k.add(head, C(1.2, 9.8, -0.6, 0.8, 1.6, 0.8), "fire", tag="flame", group="glow")
    return k


def pouch(name):
    """The Bottomless Bag: a fat leather sack, its neck tied in gold, a little fire in its mouth where it doesn't end."""
    k = Kit(name)
    shaders(k.s, LEATHER, CREAM, IRONISH, EMBER, EMBER)
    head = k.part("head", (0, 0, 0))
    k.add(head, C(0, 0, 0, 5.4, 0.6, 4.6), "dark", tag="boot")
    y = 0.4
    for w, h in ((6.4, 0.8), (8.4, 0.8), (9.6, 1.0), (10.0, 1.4), (9.6, 1.0), (8.6, 0.8), (7.2, 0.7), (5.6, 0.6), (4.4, 0.6)):
        k.add(head, C(0, y, 0, w, h, w * 0.62), "coat", tag="belly")
        k.add(head, C(0, y, 0, w * 0.74, h, w * 0.84), "coat", tag="belly")
        y += h
    k.add(head, C(0, y - 0.3, 0, 4.9, 0.7, 4.1), "trim", tag="tie")
    y += 0.3
    for w, h in ((5.0, 0.5), (6.2, 0.6), (7.0, 0.5)):
        k.add(head, C(0, y, 0, w, h, w * 0.78), "coat", tag="lip")
        y += h
    k.add(head, C(0, y - 0.15, 0, 5.2, 0.2, 3.8), "dark", tag="mouth")
    k.add(head, C(0, y - 0.05, 0, 4.0, 0.2, 2.8), "shine", tag="deep", group="glow")
    k.add(head, C(0.4, y, 0.2, 1.4, 1.5, 1.4), "fire", tag="flame", group="glow")
    k.add(head, C(-0.9, y, -0.3, 1.0, 1.0, 1.0), "fire", tag="flame", group="glow")
    k.add(head, C(1.6, y - 3.0, 1.9, 0.5, 1.6, 0.5), "trim", tag="knot")
    k.add(head, C(1.6, y - 3.5, 1.9, 0.9, 0.7, 0.9), "trim", tag="knot")
    k.add(head, C(0, 2.2, 3.9, 1.5, 1.5, 0.4), "trim", tag="clasp")
    k.add(head, C(0, 2.6, 4.2, 0.7, 0.7, 0.2), "shine", tag="rune", group="glow")
    return k


def wisp(name, coat, shine, flames):
    """A little flame with a face, burning down to a tail."""
    k = Kit(name)
    k.s.shaders = dict(coat=glow(coat, 0.2), fire=flame(flames), fire2=flame(flames, 7.0), dark=fur(SOOT, 0.1, 0.1), eye=eye(shine))
    body = k.part("hips", (0, 3, 0))
    k.add(body, C(0, 0, 0, 1.4, 1.4, 1.4), "fire", tag="boot", group="glow")
    k.add(body, C(0, 1.2, 0, 2.6, 1.6, 2.6), "fire2", tag="tail", group="glow")
    k.add(body, C(0, 2.6, 0, 4.0, 3.6, 4.0), "coat", tag="body", group="glow")
    k.add(body, C(0, 3.2, 0, 5.0, 2.4, 5.0), "coat", tag="body", group="glow")
    k.add(body, C(0, 6.0, 0, 2.8, 1.4, 2.8), "fire", tag="top", group="glow")
    k.add(body, C(0.5, 7.2, -0.3, 1.5, 1.6, 1.5), "fire2", tag="top", group="glow")
    k.add(body, C(0.2, 8.6, -0.5, 0.7, 1.4, 0.7), "fire", tag="top", group="glow")
    for sx in (1, -1):
        k.add(body, C(sx * 1.05, 3.9, 2.5, 0.9, 1.3, 0.3), "dark", tag="eye")
    return k


BROWN = ramp("#2a180c", "#422614", "#5e3820", "#7c4e30", "#9c6a48")
SPARROW = ramp("#4a3018", "#6c4a28", "#8e683c", "#ae8a58", "#c8a878")
HAWK = ramp("#2a1a10", "#46301c", "#684a2c", "#8a6a44", "#b08e64")
STORM = ramp("#101a3c", "#1a2c60", "#284488", "#3a62b0", "#5a8ad0")
TIDE = ramp("#0c3040", "#14506a", "#1e7690", "#34a0b4", "#6ccad0")
SILVER = ramp("#6a7078", "#8e949c", "#b2b8be", "#d2d6da", "#eef0f2")
WISP_GREEN = ramp("#10401c", "#1c7030", "#34a84a", "#68d870", "#b0f4a8", "#f0fff0")
GILT = ramp("#6a4410", "#a06c18", "#d09a28", "#f0c850", "#ffe690")
OLD_BONE = ramp("#6a5c44", "#8e8064", "#b4a684", "#d4c8a4", "#efe6c8")
NEWT = ramp("#34160a", "#5a2c10", "#884818", "#b46a24", "#d89038")

HEEL, HOVER = "heel", "hover"
# name, plan, where, how big in the game, tier, buff, the kit
ROSTER = [
    ("ash_crow", "Ash Crow", HOVER, 0.62, "uncommon", {"ash%": 3}, lambda n: bird(n, SOOT, IRONISH, HOOF, EMBER)),
    ("road_sparrow", "Road Sparrow", HOVER, 0.52, "uncommon", {"move%": 2}, lambda n: bird(n, SPARROW, CREAM, HOOF, GOLD)),
    ("barn_owl", "Barn Owl", HOVER, 0.55, "uncommon", {"mining%": 6}, lambda n: bird(n, TAWNY, CREAM, GOLD, GOLD, kind="owl")),
    ("tabby_cat", "Tabby Cat", HEEL, 0.5, "uncommon", {"move%": 2}, lambda n: quad(n, TAWNY, CREAM, HOOF, GOLD, 1.0, 2.8, 1.7)),
    ("smoke_cat", "Smoke Cat", HEEL, 0.5, "uncommon", {"dodge_cost%": 4}, lambda n: quad(n, IRONISH, SILVER, HOOF, FROST_FIRE, 1.0, 2.8, 1.7)),
    ("hill_pup", "Hill Pup", HEEL, 0.52, "uncommon", {"armour%": 2}, lambda n: quad(n, BROWN, CREAM, HOOF, GOLD, 2.0, 2.4, 2.0)),
    ("moss_pup", "Moss Pup", HEEL, 0.52, "uncommon", {"stamina_regen%": 5}, lambda n: quad(n, MOSS, MOTH, HOOF, FROST_FIRE, 2.0, 2.4, 2.0)),
    ("field_rabbit", "Field Rabbit", HEEL, 0.46, "uncommon", {"safe_fall": 2}, lambda n: quad(n, SPARROW, CREAM, HOOF, GOLD, 0.8, 6.4, 3.0, tailn=1)),
    ("cellar_rat", "Cellar Rat", HEEL, 0.4, "uncommon", {"coins%": 3}, lambda n: quad(n, IRONISH, CREAM, HOOF, EMBER, 2.8, 1.8, 0.7, tailn=6)),
    ("lantern_moth", "Lantern Moth", HOVER, 0.42, "uncommon", {"mana_regen%": 5}, lambda n: moth(n, MOTH, CREAM, GOLD, EMBER)),
    ("dust_moth", "Dust Moth", HOVER, 0.42, "uncommon", {"mana": 5}, lambda n: moth(n, BROWN, SPARROW, GOLD, CREAM)),
    ("pond_newt", "Pond Newt", HEEL, 0.42, "uncommon", {"swim%": 8}, lambda n: drake(n, MOSS, GOLD, BONE, GOLD, wings=False)),

    ("rime_owl", "Rime Owl", HOVER, 0.6, "rare", {"elite_dmg%": 3}, lambda n: bird(n, RIME, CREAM, GOLD, FROST_FIRE, kind="owl")),
    ("hunting_hawk", "Hunting Hawk", HOVER, 0.66, "rare", {"arrow%": 4}, lambda n: bird(n, HAWK, CREAM, GOLD, GOLD)),
    ("coin_fox", "Coin Fox", HEEL, 0.5, "rare", {"coins%": 6}, lambda n: quad(n, TAWNY, CREAM, HOOF, GOLD, 2.6, 3.6, 3.2, brush=True, socks=True)),
    ("snow_fox", "Snow Fox", HEEL, 0.5, "rare", {"speed%": 3}, lambda n: quad(n, RIME, CREAM, HOOF, FROST_FIRE, 2.6, 3.6, 3.2, brush=True)),
    ("iron_pup", "Iron Pup", HEEL, 0.54, "rare", {"armour%": 4}, lambda n: quad(n, IRONISH, SILVER, HOOF, EMBER, 2.0, 2.4, 2.0)),
    ("ember_rat", "Ember Rat", HEEL, 0.42, "rare", {"dmg%": 3}, lambda n: quad(n, BLOOD, TAWNY, HOOF, EMBER, 2.8, 1.8, 0.7, EMBER, cracks=True, tailn=6)),
    ("moon_hare", "Moon Hare", HEEL, 0.48, "rare", {"move%": 3}, lambda n: quad(n, SILVER, RIME, HOOF, FROST_FIRE, 0.8, 6.4, 3.0, tailn=1)),
    ("tide_moth", "Tide Moth", HOVER, 0.44, "rare", {"spell%": 3}, lambda n: moth(n, TIDE, RIME, FROST_FIRE, CREAM)),
    ("fire_newt", "Fire Newt", HEEL, 0.44, "rare", {"tough%": 5}, lambda n: drake(n, NEWT, GOLD, BONE, EMBER, EMBER, wings=False)),
    ("marrow_skull", "Marrow Skull", HOVER, 0.5, "rare", {"thrall_dmg%": 6}, lambda n: skull(n, OLD_BONE, SOUL, SOUL)),
    ("bog_wisp", "Bog Wisp", HOVER, 0.5, "rare", {"heal%": 4}, lambda n: wisp(n, WISP_GREEN, GOLD, WISP_GREEN)),
    ("thorn_wisp", "Thorn Wisp", HOVER, 0.5, "rare", {"mana_regen%": 9}, lambda n: wisp(n, GOLD, EMBER, EMBER)),

    ("soot_cat", "Soot Cat", HEEL, 0.5, "epic", {"move%": 4}, lambda n: quad(n, SOOT, IRONISH, HOOF, EMBER, 1.0, 2.8, 1.7, EMBER, cracks=True)),
    ("dusk_moth", "Dusk Moth", HOVER, 0.46, "epic", {"spell%": 5}, lambda n: moth(n, DUSK, SOUL, SOUL, FROST_FIRE)),
    ("hatchling", "Stormling", HOVER, 0.44, "epic", {"dmg%": 4}, lambda n: drake(n, STORM, GOLD, BONE, FROST_FIRE)),
    ("grave_pup", "Grave Pup", HEEL, 0.56, "epic", {"thrall_hp%": 10}, lambda n: quad(n, SOOT, OLD_BONE, HOOF, SOUL, 2.0, 2.4, 2.0, SOUL, cracks=True)),
    ("storm_hawk", "Storm Hawk", HOVER, 0.68, "epic", {"speed%": 5}, lambda n: bird(n, STORM, RIME, GOLD, FROST_FIRE, plume=FROST_FIRE)),
    ("candle_skull", "Candle Skull", HOVER, 0.52, "epic", {"mana": 15}, lambda n: skull(n, OLD_BONE, EMBER, EMBER)),
    ("spirit_fox", "Spirit Fox", HEEL, 0.52, "epic", {"ash%": 7}, lambda n: quad(n, DUSK, SOUL, HOOF, SOUL, 2.6, 3.6, 3.2, SOUL, brush=True)),
    ("frost_wisp", "Frost Wisp", HOVER, 0.52, "epic", {"health%": 4}, lambda n: wisp(n, RIME, FROST_FIRE, FROST_FIRE)),

    ("cinder_phoenix", "Cinder Phoenix", HOVER, 0.7, "legendary", {"dmg%": 5, "health%": 3}, lambda n: bird(n, BLOOD, TAWNY, GOLD, EMBER, plume=EMBER)),
    ("ember_hatchling", "Emberling", HOVER, 0.46, "legendary", {"dmg%": 6, "elite_dmg%": 4}, lambda n: drake(n, BLOOD, TAWNY, BONE, EMBER, EMBER)),
    ("gilded_vixen", "Gilded Vixen", HEEL, 0.54, "legendary", {"coins%": 12, "ash%": 8}, lambda n: quad(n, GILT, CREAM, HOOF, GOLD, 2.6, 3.6, 3.4, EMBER, brush=True)),
    ("hollow_skull", "Hollow Moon Skull", HOVER, 0.56, "legendary", {"spell%": 6, "mana_regen%": 10}, lambda n: skull(n, RIME, SOUL, SOUL)),
]


def save(kit, pid):
    """Bones, texture and item model; gives back the middle and longest side the item's icon is framed by."""
    import json
    A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "resources")
    assets = os.path.join(A, "assets", "ashbound")
    kit.export("pet_" + pid)
    os.remove(os.path.join(assets, "textures", "entity", "mount_pet_%s_hot.png" % pid))
    path = os.path.join(assets, "mounts", "pet_%s.json" % pid)
    data = json.load(open(path, encoding="utf8"))
    v = [[], [], []]
    for b in data["bones"]:
        for kind in ("lit", "glow", "flame"):
            q = b[kind]
            for i in range(0, len(q), 23):
                for c in range(4):
                    for ax in range(3):
                        v[ax].append(q[i + c * 5 + ax])
    lo, hi = [min(a) for a in v], [max(a) for a in v]
    with open(os.path.join(assets, "models", "item", pid + ".json"), "w", encoding="utf8", newline="\n") as fp:
        json.dump({"parent": "builtin/entity", "gui_light": "front", "display": {
            "gui": {"rotation": [18, 145, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]},
            "ground": {"rotation": [0, 0, 0], "translation": [0, 2, 0], "scale": [0.5, 0.5, 0.5]},
            "fixed": {"rotation": [0, 180, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]},
            "thirdperson_righthand": {"rotation": [0, 0, 0], "translation": [0, 3, 1], "scale": [0.5, 0.5, 0.5]},
            "firstperson_righthand": {"rotation": [0, 45, 0], "translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]}}}, fp, indent=1)
    return [round((a + b) / 2, 3) for a, b in zip(lo, hi)] + [round(max(b - a for a, b in zip(lo, hi)), 3)]


def export():
    import json
    A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "resources")
    assets = os.path.join(A, "assets", "ashbound")
    out = []
    for pid, name, where, size, tier, stats, make in ROSTER:
        box = save(make(pid), pid)
        out.append(dict(id=pid, name=name, where=where, size=size, rarity=tier, stats=stats, box=box))
    with open(os.path.join(A, "ashbound", "pets.json"), "w", encoding="utf8", newline="\n") as fp:
        json.dump(out, fp, indent=1)
    with open(os.path.join(A, "data", "curios", "tags", "item", "pet.json"), "w", encoding="utf8", newline="\n") as fp:
        json.dump({"replace": False, "values": ["ashbound:" + r[0] for r in ROSTER]}, fp, indent=1)
    lp = os.path.join(assets, "lang", "en_us.json")
    lang = open(lp, encoding="utf8", newline="").read()
    add = "".join(',\n  "item.ashbound.%s": %s' % (r[0], json.dumps(r[1])) for r in ROSTER if '"item.ashbound.%s"' % r[0] not in lang)
    at = lang.rindex("}")
    while lang[at - 1] in "\r\n ":
        at -= 1
    open(lp, "w", encoding="utf8", newline="").write(lang[:at] + add + lang[at:])
    print(len(out), "pets")


if __name__ == '__main__':
    V.T = 4
    if "--bag" in sys.argv:
        print(save(pouch("bottomless_bag"), "bottomless_bag"))
    elif "--export" in sys.argv:
        export()
    else:
        names = [a for a in sys.argv[1:] if not a.startswith("--")]
        if "bottomless_bag" in names:
            M.preview(pouch("bottomless_bag").s, "pet_bottomless_bag", ("boot",))
        for r in ROSTER:
            if not names or r[0] in names:
                M.preview(r[6](r[0]).s, "pet_" + r[0], ("boot",))
