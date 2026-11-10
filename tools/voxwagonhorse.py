"""Bramble, Hob Tarrant's draught horse (Intro.java): a heavy bay in harness between the wagon's shafts. Built with the
mounts' kit (tools/voxmounts.py), so client/MountRender draws it and its bones can idle: head down to graze and up,
ears, a tail swish, a hind hoof rested and stamped.

A big plain working horse, not a monster: bay coat, black points, a white blaze, white feathers over its hooves, a thick
arched neck with the mane falling to the off side. The harness: a padded collar with brass hames, a back pad with the
tugs, a breeching round the rump, a bridle with blinkers, reins back to the driver.

    python tools/voxwagonhorse.py             preview for blender -b -P E:/Ashbound/tools/blender/preview_mob.py -- mount_wagon_horse@3.6
    python tools/voxwagonhorse.py --export    assets/ashbound/mounts/wagon_horse.json + textures/entity/mount_wagon_horse.png
"""
import math
import sys

import voxmounts as VM
from voxmounts import Kit, C, ramp, shade, fbm, h3, fur, plate, eye, tone, HOOF, LEATHER

BAY = ramp("#1e0e08", "#33180c", "#4a2412", "#62321a", "#7a4424", "#94582e")
POINT = ramp("#0a0808", "#141010", "#1e1816", "#2a221e", "#382e28")
WHITE = ramp("#6a6258", "#968c80", "#bcb4a6", "#dcd6ca", "#f2eee6")
BRASS = ramp("#3a2a0c", "#6a4e18", "#9a7426", "#c69a3a", "#e6c464", "#fae6a0")
COLLAR = ramp("#120a06", "#1e120a", "#2c1a10", "#3c2418", "#4e3020")
PAD = ramp("#3a1410", "#5a2016", "#78301e", "#964228")


def hair(R, ragged=True):
    """mane, tail and feathers: long strands down the face, the end ragged"""
    def paint(p, n, b, key, i, j, w, h, fr):
        if ragged and key in "nsew" and h > 4 and j < 2 * h3(i, 3, int(b.lo[1])):
            return None
        v = 0.42 + tone(n, j, h) + 0.34 * (h3(i, 1, int(b.lo[2] * 3)) - 0.5) + 0.12 * (j / max(1, h - 1))
        return shade(R, v, i, j)
    return paint


def blaze(R, W):
    """the bay face with a white blaze down its front (the -z face of the head, the top as it hangs)"""
    base = fur(R, 0.15, 0.2)

    def paint(p, n, b, key, i, j, w, h, fr):
        if key == "n" and abs(i - (w - 1) / 2) < max(1.0, w * 0.18 + 0.6 * math.sin(j * 0.7)):
            return shade(W, 0.75, i, j)
        return base(p, n, b, key, i, j, w, h, fr)
    return paint


def wagon_horse():
    k = Kit("wagon_horse")
    s = k.s
    s.shaders = dict(hide=fur(BAY, 0.18, 0.22), point=fur(POINT, 0.15, 0.2), face=blaze(BAY, WHITE), feather=hair(WHITE), mane=hair(POINT),
                     hoof=fur(HOOF, 0.1, 0.1), collar=plate(COLLAR), pad=plate(PAD, BRASS), brass=plate(BRASS), strap=fur(LEATHER, 0.08, 0.1),
                     eye=eye(ramp("#0a0606", "#1a1210", "#2a1e18")))
    hips = k.part("hips", (0, 26, -11))
    torso = k.part("torso", (0, 26, -11), (), hips)
    # a deep heavy barrel, a broad rump and chest
    k.loaf(torso, "z", -19, 18, 14, lambda t: (12.0 + 3 * math.sin(t * math.pi), 13.4 + 3.4 * math.sin(t * math.pi) + 1.6 * t, 26.6 - 0.8 * t), "hide", "barrel")
    for sx in (1, -1):
        k.add(torso, C(sx * 3.8, 21, -14.5, 7.0, 13.6, 10.5), "hide", tag="haunch")
        k.add(torso, C(sx * 3.6, 19, 13.5, 6.8, 13.6, 8.4), "hide", tag="shoulder")
    k.add(torso, C(0, 20.5, 18.6, 10.6, 11.5, 3.0), "hide", tag="chest")
    # harness: the back pad with a brass terret on top and the tugs, the belly band, the breeching round the rump
    k.add(torso, C(0, 33.6, 2, 9.6, 2.0, 6.4), "pad", tag="saddle")
    for sx in (1, -1):
        k.add(torso, C(sx * 4.6, 30.4, 2, 1.6, 4.4, 6.0), "pad", tag="pad")
        k.add(torso, C(sx * 7.6, 17.0, 2, 0.6, 15.4, 2.2), "strap", tag="girth")
        k.add(torso, C(sx * 7.6, 24.0, 2.0, 1.0, 2.0, 2.6), "brass", tag="tug")
        k.add(torso, C(sx * 8.0, 25.0, -8, 0.5, 1.2, 20), "strap", tag="trace")       # traces back to the shafts' line
        k.add(torso, C(sx * 7.4, 22.6, -15.5, 0.5, 2.0, 9.0), "strap", tag="breeching")
        k.add(torso, C(sx * 4.2, 32.6, -15.0, 4.0, 1.0, 1.4), "strap", tag="hip_strap")
        for z in (-12, -18):
            k.add(torso, C(sx * 7.0, 26.6, z, 0.4, 7.0, 1.0), "strap", tag="hip_drop")
    k.add(torso, C(0, 16.2, 2, 15.6, 1.4, 2.4), "strap", tag="girth")
    k.add(torso, C(0, 22.6, -20.0, 13.0, 2.0, 0.6), "strap", tag="breeching")
    k.add(torso, C(0, 35.6, 2, 1.6, 2.2, 1.6), "brass", tag="terret")
    k.add(torso, C(0, 33.2, -7, 1.2, 0.8, 18), "strap", tag="crupper")
    # legs: heavy, black from the knee, white feathers over big hooves
    for sx, nm in ((1, "l"), (-1, "r")):
        x = sx * 4.8
        up, low, ft = k.leg(torso, ("thigh_" + nm, "shin_" + nm, "foot_" + nm), x, 23.6, -15, (10.2, 9.6, 3.8),
                            ((6.0, 7.2), (3.8, 4.4), (5.2, 5.8)), (10, -18, 8), ("hide", "point", "hoof"))
        k.add(low, C(x, 2.6, -15, 5.6, 5.4, 6.2), "feather", tag="feather")
        k.add(low, C(x, 3.6, -15.6, 4.6, 4.0, 5.8), "feather", tag="feather")
        up, low, ft = k.leg(torso, ("arm_" + nm, "fore_" + nm, "hand_" + nm), x, 23.6, 13, (10.2, 9.6, 3.8),
                            ((5.4, 6.6), (3.8, 4.2), (5.2, 5.8)), (-6, 6, 0), ("hide", "point", "hoof"))
        k.add(low, C(x, 2.6, 13, 5.6, 5.4, 6.2), "feather", tag="feather")
        k.add(low, C(x, 3.6, 13.6, 4.6, 4.0, 5.8), "feather", tag="feather")
    # the neck: thick and arched, the collar round its base, the mane falling to the off side
    neck = k.part("neck", (0, 30, 16), (("x", 34),), torso)
    k.loaf(neck, "y", 28, 41, 6, lambda t: (9.6 - 1.4 * t, 13.0 - 2.4 * t, 16.4), "hide", "neck")
    neck2 = k.part("neck2", (0, 41, 16.4), (("x", 22),), neck)
    k.loaf(neck2, "y", 40, 51, 5, lambda t: (8.0 - 1.4 * t, 10.4 - 2.8 * t, 16.4), "hide", "neck")
    # the collar: a thick padded ring standing round the neck where it meets the chest, brass hames up its front
    k.add(neck, C(0, 27.4, 22.6, 12.4, 3.4, 3.4), "collar", tag="collar")              # the bottom of the ring, at the chest
    for sx in (1, -1):
        k.add(neck, C(sx * 5.6, 28, 16.4, 2.6, 9.6, 12.0), "collar", tag="collar")    # its sides
        k.add(neck, C(sx * 6.9, 29, 21.0, 0.8, 8.6, 1.2), "brass", tag="hames")
        k.add(neck, C(sx * 7.0, 33.6, 21.4, 1.4, 1.4, 1.4), "brass", tag="hame_knob")
    k.add(neck, C(0, 36.6, 15.6, 10.2, 2.6, 6.2), "collar", tag="collar")              # over the crest
    for sx in (1, -1):
        k.add(neck, C(sx * 2.6, 38.4, 14.4, 1.0, 2.6, 1.0), "brass", tag="hame_top")
    for n in range(5):
        k.add(neck, C(-4.0, 29 + n * 2.6, 11.0 + n * 0.2, 1.4, 3.2, 3.6), "mane", tag="mane")
        k.add(neck, C(-5.0, 28.4 + n * 2.6, 11.6, 1.0, 4.4 + 1.2 * (n % 2), 2.6), "mane", tag="mane")
    for n in range(4):
        k.add(neck2, C(-3.4, 40.5 + n * 2.6, 11.4 + n * 0.3, 1.3, 3.0, 3.0), "mane", tag="mane")
        k.add(neck2, C(-4.2, 40.0 + n * 2.6, 12.0, 0.9, 4.0 + 1.2 * (n % 2), 2.4), "mane", tag="mane")
    k.add(neck2, C(0, 40.0, 11.8, 2.4, 12, 1.6), "mane", tag="mane")
    # the head hangs from the poll: +y runs down the face; a big plain face with a blaze, blinkers, a bridle
    head = k.part("head", (0, 51.4, 16.4), (("x", 98),), neck2)
    k.add(head, C(0, 49.4, 16.4, 7.0, 8.0, 7.8), "face", tag="skull")
    k.add(head, C(0, 56.4, 15.8, 5.4, 5.4, 6.0), "face", tag="muzzle")
    k.add(head, C(0, 61.4, 15.7, 5.0, 4.0, 5.6), "face", tag="muzzle")
    k.add(head, C(0, 49.6, 20.2, 5.4, 6.0, 1.6), "hide", tag="jaw")
    k.add(head, C(0, 64.6, 15.7, 5.2, 1.2, 5.2), "point", tag="nose")
    k.add(head, C(0, 47.8, 12.2, 2.6, 3.4, 1.2), "mane", tag="forelock")
    for sx in (1, -1):
        k.add(head, C(sx * 3.6, 51.8, 14.8, 0.3, 1.2, 1.6), "eye", tag="eye")
        k.add(head, C(sx * 4.0, 51.2, 14.4, 0.6, 3.6, 3.8), "collar", tag="blinker")   # the blinkers, cupped beside the eyes
        k.add(head, C(sx * 4.2, 52.4, 14.4, 0.4, 0.8, 0.8), "brass", tag="rosette")
        k.add(head, C(sx * 3.6, 49.0, 16.4, 0.4, 0.8, 8.0), "strap", tag="browband")   # the cheek straps and noseband
        k.add(head, C(sx * 3.7, 51.0, 18.6, 0.4, 9.0, 0.8), "strap", tag="cheek")
        k.add(head, C(sx * 2.8, 60.0, 15.7, 0.4, 1.0, 6.0), "strap", tag="noseband")
        k.add(head, C(sx * 2.9, 62.4, 18.0, 0.8, 0.8, 0.8), "brass", tag="bit")
        k.add(head, C(sx * 2.0, 64.0, 13.8, 0.6, 1.0, 0.8), "point", tag="nostril")
        k.seg(head, "ear%d" % (sx > 0), (sx * 2.4, 49.4, 15.2), [(1.8, 1.4, 2.8, (("x", 180), ("z", sx * -14))), (1.0, 0.8, 1.8, ())], "hide", tag="ear")
    k.add(head, C(0, 48.6, 12.4, 6.0, 0.8, 0.5), "strap", tag="browband")
    k.add(head, C(0, 60.0, 12.6, 5.4, 1.0, 0.4), "strap", tag="noseband")
    # the reins, from the bit back over the collar's terrets (on the neck, so they follow the head's nod a little)
    for sx in (1, -1):
        k.add(neck2, C(sx * 3.4, 46.0, 21.0, 0.4, 8.0, 0.5), "strap", tag="rein")
        k.add(neck, C(sx * 5.0, 33.0, 22.0, 0.4, 10.0, 0.5), "strap", tag="rein")
    # the tail: a thick black switch hanging, the dock lifted a little
    tail = k.part("tail", (0, 33, -20), (("x", -158),), hips)
    k.add(tail, C(0, 32.6, -20, 3.2, 4.0, 3.2), "mane", tag="dock")
    for dx, tilt, ln, wd in ((0, 0, 20, 3.8), (1.2, 6, 17, 2.6), (-1.2, -6, 18, 2.6), (0, 12, 15, 2.2)):
        k.seg(tail, "hair%d" % len(s.boxes), (dx, 35, -20), [(wd, wd, ln * 0.4, (("x", tilt), ("z", dx * -6))), (wd * 0.85, wd * 0.85, ln * 0.34, (("x", 4),)),
                                                          (wd * 0.6, wd * 0.6, ln * 0.26, (("x", 4),))], "mane", tag="tail")
    return k


if __name__ == '__main__':
    VM.V.T = 2
    kit = wagon_horse()
    if "--export" in sys.argv:
        kit.export("wagon_horse")
    else:
        VM.M.preview(kit.s, "mount_wagon_horse")
