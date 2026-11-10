"""Hob's wagon and Bramble his horse as Minecraft-style cube models (tools/mcstyle.py's kit): 16 texels a block, flat
pixel paint lit from the top. The horse is written standing between the wagon's shafts (HORSE_AT), so both line up.

Wagon: an oxblood box bed with ochre trim on four spoked wheels, a canvas tilt on hoops rolled up at the back over
crates, sacks and a keg, the driver's bench, a lantern on a crook, pots and a coiled rope on one side, the water cask on
the other, shafts out front. Horse: a heavy bay, black legs, white feathers, a blaze; padded collar with brass hames,
back pad, girth, breeching and traces, a bridle with blinkers."""
import math

from mcstyle import Model, ramp5, rgb, tint, mix, lit, flat, planks

HORSE_AT = (0, 0, 64)

BAY = ramp5("#6a3a1e")
POINT = ramp5("#262020")
WHITE = ramp5("#d8d2c6")
HOOF = ramp5("#3a3634")
COLLAR = ramp5("#2a1c14")
BRASS = ramp5("#c49a3a")
STRAP = ramp5("#3a2416")
PAD = ramp5("#7a2e1e")
OX = ramp5("#6a2c1c")
OCHRE = ramp5("#a87e2c")
WOOD = ramp5("#7a5634")
DWOOD = ramp5("#4a3220")
IRON = ramp5("#3a3a40")
CANVAS = ramp5("#d4c8a8")
PATCHC = ramp5("#8a7a58")
SACKC = ramp5("#a89674")
LAMP = [rgb("#ffe6a0")] * 5
RED = ramp5("#a83420")
TIN = ramp5("#8e9096")


# ================================================================== the horse

def hide(R=BAY, strap_z=None, breech=False, trace=False, top_pad=False):
    """the barrel: bay, the harness painted on where it wraps the body. Faces know their place: on the right side
    u runs back to front, on the left front to back; the top runs back to front down its rows"""
    def p(face, i, j, fw, fh):
        c = lit(face, j, fh, R, 2)
        if face in ("right", "left"):
            z = -13 + i if face == "right" else 13 - 1 - i
            if 0 <= z <= 2:
                return STRAP[2] if j > 0 else PAD[2]
            if breech and z < -5 and j == 6:
                return STRAP[2]
            if breech and z in (-9, -6) and j < 6:
                return STRAP[1]
            if trace and z > -4 and j == 5:
                return STRAP[1] if z % 4 else BRASS[3]
            if (i * 7 + j * 3) % 11 == 0:
                return tint(c, 0.92)
        if face == "top":
            z = -13 + j
            if -2 <= z <= 4:
                return PAD[3] if 0 < i < fw - 1 else PAD[1]
            if i == fw // 2 and z < -2:
                return STRAP[2]
        if face == "bottom":
            z = -13 + j
            if 0 <= z <= 2:
                return STRAP[1]
        if face == "back" and j == 6:
            return STRAP[2]
        return c
    return p


def leg(face, i, j, fw, fh):
    if face == "bottom":
        return HOOF[1]
    if j >= fh - 2:
        return HOOF[2] if face != "back" else HOOF[1]
    if j >= 6:
        return lit(face, j, fh, POINT, 2)
    return lit(face, j, fh, BAY, 2)


def feather(face, i, j, fw, fh):
    if face in ("top", "bottom"):
        return None
    if j == fh - 1 and (i % 2 == 0):
        return None
    return WHITE[3] if (i + j) % 3 else WHITE[2]


def head(face, i, j, fw, fh):
    c = lit(face, j, fh, BAY, 2)
    if face == "front":                    # the muzzle's end
        return POINT[2] if j > 1 else BAY[2]
    if face == "top":                      # the face as it points forward: the blaze, browband, noseband
        z = j
        if z in (2,):
            return STRAP[2]
        if z == 9:
            return STRAP[2]
        if i == fw // 2 and z >= 1 or (i in (2, 4) and 4 <= z <= 7):
            return WHITE[3]
        if z >= 11:
            return POINT[2]
        return BAY[3]
    if face in ("left", "right"):
        z = i if face == "right" else fw - 1 - i
        if z == 3 and j == 1:
            return (16, 12, 10)
        if z == 3 and j == 2:
            return BAY[1]
        if z in (2, 9) and j <= 4:
            return STRAP[2]
        if z == 11 and j in (2, 3):
            return BRASS[3]
        if z >= 10 and j >= 3:
            return POINT[2]
    if face == "bottom":
        return BAY[1]
    return c


def mane(face, i, j, fw, fh):
    if face == "bottom" and False:
        return None
    k = 2 if (i + j * 2) % 5 else 1
    return POINT[k + (1 if face == "top" else 0)]


def wagon_horse():
    m = Model("wagon_horse")
    # legs and feathers
    for x in (-6.5, 1.5):
        for z in (7, -12):
            part = "leg_" + ("f" if z > 0 else "b") + ("r" if x < 0 else "l")
            m.box((x, 0, z), (5, 14, 5), leg).part = part
            m.box((x - 0.5, 0, z - 0.5), (6, 4, 6), feather).part = part
    m.box((-6.5, 13, -13), (13, 13, 26), hide(breech=True, trace=True))
    # neck, head and its gear all turn 30 degrees about the withers' front
    pv = (0, 22, 10)
    R = (("x", 30),)

    def at(lo, size, paint):
        b = m.box((lo[0] + pv[0], lo[1] + pv[1], lo[2] + pv[2]), size, paint, rot=R, pivot=pv)
        b.part = "neck"
        return b
    at((-3.5, -2, -4.5), (7, 15, 9), flat(BAY, 2))
    at((-3.5, 9, -3), (7, 7, 13), head)
    at((-3, 16, -2), (2, 3, 1), flat(BAY, 2))
    at((1, 16, -2), (2, 3, 1), flat(BAY, 2))
    at((-1.5, 2, -6.5), (3, 15, 2), mane)                     # mane down the crest
    at((-4.4, 3, -5), (1, 11, 7), mane)                       # falling to the off side
    at((-1.5, 13.5, 9.6), (3, 3, 1), mane)                    # forelock
    # the collar round the neck's base, brass hames up its front, the blinkers
    at((-5, -2, -5.5), (10, 3, 11), flat(COLLAR, 2))
    at((-5, 1, -5.5), (2, 8, 11), flat(COLLAR, 2))
    at((3, 1, -5.5), (2, 8, 11), flat(COLLAR, 2))
    at((-4.5, 8, -5.5), (9, 2, 11), flat(COLLAR, 2))
    at((-5.6, -1, 4.6), (1, 10, 1), flat(BRASS, 2))
    at((4.6, -1, 4.6), (1, 10, 1), flat(BRASS, 2))
    at((-4.4, 11.5, 3), (1, 2.5, 2.5), flat(COLLAR, 2))
    at((3.4, 11.5, 3), (1, 2.5, 2.5), flat(COLLAR, 2))
    # back pad with its terret, tail
    m.box((-7, 25.5, -2), (14, 2, 6), flat(PAD, 2))
    m.box((-1, 27.5, 0), (2, 2, 2), flat(BRASS, 2))
    m.box((-1.5, 9, -16), (3, 16, 3), mane, rot=(("x", 14),), pivot=(0, 24, -13)).part = "tail"
    m.box((-1, 22, -14), (2, 3, 2), mane).part = "tail"
    return m


# where each of Bramble's moving parts turns, in px before HORSE_AT
PIVOTS = {"body": (0, 0, 0), "neck": (0, 22, 10), "tail": (0, 24, -13),
          "leg_fr": (-4, 14, 9.5), "leg_fl": (4, 14, 9.5), "leg_br": (-4, 14, -9.5), "leg_bl": (4, 14, -9.5)}


def game(m, name, at=(0, 0, 0)):
    """into the mod for client/WagonRender: parts of quads (four corners of x y z u v in blocks, then the normal),
    each with the pivot it turns about, and the texture"""
    import json
    import os
    import port_weapons as P
    img = m.build()
    W, H = img.size
    parts = {}
    for b in m.boxes:
        nm = getattr(b, "part", "body")
        q = parts.setdefault(nm, [])
        for f, ps, uv in b.quads():
            c = [sum(p[i] for p in ps) / 4 for i in range(3)]
            ctr = b.world([b.lo[i] + b.size[i] / 2 for i in range(3)])
            e1 = [ps[1][i] - ps[0][i] for i in range(3)]
            e2 = [ps[2][i] - ps[0][i] for i in range(3)]
            n = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]]
            if sum(n[i] * (c[i] - ctr[i]) for i in range(3)) < 0:
                ps, uv, n = ps[::-1], uv[::-1], [-a for a in n]
            ln = math.sqrt(sum(a * a for a in n)) or 1
            for p_, (u, v) in zip(ps, uv):
                q += [round((p_[i] + at[i]) / 16, 5) for i in range(3)] + [round(u / W, 6), round(v / H, 6)]
            q += [round(a / ln, 4) for a in n]
    out = {"parts": [{"name": k, "pivot": [round((PIVOTS.get(k, (0, 0, 0))[i] + (at[i] if k in PIVOTS else 0)) / 16, 5) for i in range(3)], "quads": v}
                     for k, v in parts.items()]}
    os.makedirs(P.ASSETS + "cubes", exist_ok=True)
    P.dump(P.ASSETS + "cubes/%s.json" % name, out)
    img.save(P.ASSETS + "textures/entity/%s.png" % name)
    print(name, {k: len(v) // 23 for k, v in parts.items()}, img.size)


# ================================================================== the wagon

def side_boards(face, i, j, fw, fh):
    """oxblood planks with a seam every 3 rows, ochre along the top"""
    if face == "top":
        return OCHRE[3]
    if face == "bottom":
        return OX[0]
    if j == 0:
        return OCHRE[3]
    if j == 1:
        return OCHRE[1]
    if j % 3 == 1:
        return OX[1]
    c = lit(face, j, fh, OX, 2)
    return tint(c, 0.92) if (i + j * 5) % 13 == 0 else c


def canvas(hoop_every=9, patch=None):
    def p(face, i, j, fw, fh):
        c = CANVAS[3] if face == "top" else CANVAS[2] if face in ("front", "left", "right") else CANVAS[1]
        if face in ("top", "bottom"):
            z = j
            if z % hoop_every == 0:
                return CANVAS[1]
            if patch and patch[0] <= z <= patch[1] and patch[2] <= i <= patch[3]:
                return PATCHC[2] if (i + z) % 4 else PATCHC[1]
            if (i * 5 + z * 3) % 17 == 0:
                return CANVAS[2]
        return c
    return p


def barrel(face, i, j, fw, fh):
    if face in ("top", "bottom"):
        return DWOOD[2] if (i + j) % 3 else DWOOD[1]
    if j in (1, fh - 2):
        return IRON[2]
    c = lit(face, j, fh, WOOD, 2)
    return WOOD[1] if i % 3 == 2 else c


def crate(face, i, j, fw, fh):
    edge = i in (0, fw - 1) or j in (0, fh - 1)
    if edge:
        return DWOOD[2]
    if face != "top" and (i == j or i == fw - 1 - j):
        return DWOOD[3]
    return lit(face, j, fh, WOOD, 3)


def sack(face, i, j, fw, fh):
    c = lit(face, j, fh, SACKC, 2)
    if face != "top" and j == 1:
        return STRAP[3]
    return tint(c, 0.9) if (i * 3 + j) % 5 == 0 else c


def lamp(face, i, j, fw, fh):
    if i in (0, fw - 1) or j in (0, fh - 1):
        return IRON[1]
    return (255, 214, 120) if (i + j) % 3 else (255, 238, 180)


def wheel(m, x, y, z, r, side):
    """rim of eight cubes round the axle, four crossed spokes, a hub; x is the wheel's outer face"""
    seg = 2 * r * math.tan(math.radians(22.5)) + 0.6
    for k in range(8):
        m.box((x, y + r - 2, z - seg / 2), (2, 2, seg), flat(DWOOD, 2) if k % 2 else flat(IRON, 2), rot=(("x", 45 * k),), pivot=(x, y, z))
    for k in range(4):
        m.box((x + 0.25, y - r + 1.5, z - 0.75), (1.5, 2 * r - 3, 1.5), flat(WOOD, 2), rot=(("x", 45 * k),), pivot=(x, y, z))
    m.box((x - 0.5 * side, y - 1.5, z - 1.5), (3, 3, 3), flat(IRON, 2))


def hob_wagon():
    m = Model("hob_wagon")
    BED, L, W = 17, 54, 26
    hw, hl = W / 2, L / 2
    m.box((-hw, BED - 2, -hl), (W, 2, L), planks(WOOD, "v", 3))                       # floor
    for sx in (-1, 1):
        m.box((sx * hw - (1 if sx > 0 else 0), BED, -hl), (1, 8, L), side_boards)
        for z in (-18, 0, 18):                                                        # stakes and iron straps
            m.box((sx * (hw + 0.5) - 0.5, BED - 3, z - 0.5), (1, 11, 1), flat(DWOOD, 2))
    for sz in (-1, 1):
        m.box((-hw, BED, sz * hl - (1 if sz > 0 else 0)), (W, 8, 1), side_boards)
    m.box((-7, BED - 5, -hl), (2, 3, L), flat(DWOOD, 2))                               # sills
    m.box((5, BED - 5, -hl), (2, 3, L), flat(DWOOD, 2))
    # wheels and axles
    for z, r in ((-17, 12), (18, 9.5)):
        for sx in (-1, 1):
            wheel(m, sx * (hw + 2) - (2 if sx > 0 else 0) + (0 if sx > 0 else 0), r, z, r, sx)
        m.box((-hw - 3, r - 1, z - 1), (W + 6, 2, 2), flat(IRON, 2))
    # the tilt: hoops of six cubes round a half circle, rolled up off the last bay
    yc, rr = BED + 8, 15
    z0, z1 = -hl + 9, hl - 2
    for k in range(6):
        th = 15 + 30 * k
        chord = 2 * rr * math.sin(math.radians(15)) + 0.4
        m.box((-chord / 2, yc + rr - 1, z0), (chord, 1, z1 - z0), canvas(patch=(14, 22, 1, 5) if k == 4 else None),
              rot=(("z", th - 90),), pivot=(0, yc, 0))
        m.box((-chord / 2, yc + rr - 1.6, z0 - 2.5), (chord, 2.2, 2.5), flat(CANVAS, 2), rot=(("z", th - 90),), pivot=(0, yc, 0))   # the roll
        m.box((-chord / 2, yc + rr - 1.2, z0 - 8), (chord, 0.8, 0.8), flat(DWOOD, 2), rot=(("z", th - 90),), pivot=(0, yc, 0))      # bare hoop
    for sx in (-1, 1):
        m.box((sx * (hw + 0.5) - 0.5, BED + 7, -hl + 9), (1, 2, L - 11), flat(OCHRE, 2))
    # goods under the roll
    for (x, z, s) in ((-8, -22, 7), (2, -23, 6), (-8, -15, 6)):
        m.box((x, BED, z), (s, s, s), crate)
    m.box((4, BED, -16), (6, 8, 6), barrel)
    m.box((-3, BED, -18), (5, 7, 4), sack)
    m.box((-1, BED + 6, -24), (5, 4, 6), sack, rot=(("z", 70),), pivot=(1, BED + 6, -21))
    m.box((-9.5, BED + 7, -21.5), (5, 2, 5), flat(ramp5("#9a3020"), 3))                # apples heaped on the crate
    # driver's bench, backrest, footboard, whip
    fz = hl
    m.box((-11, BED + 8, fz - 7), (22, 2, 6), planks(WOOD, "u", 3))
    m.box((-11, BED + 10, fz - 8), (22, 5, 1), side_boards)
    m.box((-12, BED + 1, fz), (24, 1, 7), planks(WOOD, "u", 3))
    m.box((10, BED + 10, fz - 2), (1, 14, 1), flat(DWOOD, 2), rot=(("x", 25),), pivot=(10, BED + 10, fz - 2))
    # the lantern on its crook at the front left corner
    lx = hw + 1
    m.box((lx, BED + 4, fz - 2), (1, 22, 1), flat(IRON, 2))
    m.box((lx, BED + 25, fz - 2), (1, 1, 6), flat(IRON, 2))
    m.box((lx - 1, BED + 19, fz + 2), (3, 5, 3), lamp)
    m.box((lx - 1.5, BED + 24, fz + 1.5), (4, 1, 4), flat(IRON, 2))
    # the right side: pots on a rail, a coil of rope; the left: the water cask in its cradle
    rx = -hw - 2
    m.box((rx + 1, BED + 6, -6), (1, 1, 16), flat(IRON, 2))
    for z, s in ((-4, 4), (1, 3), (5, 4)):
        m.box((rx - s + 1.5, BED + 6 - s, z - s / 2), (s, s, s), flat(TIN, 2))
    m.box((rx - 1, BED - 2, -14), (2, 6, 6), flat(STRAP, 2))
    m.box((hw + 1, BED - 4, -6), (6, 6, 10), barrel, rot=(("x", 90),), pivot=(hw + 4, BED - 1, -1))
    # under the bed a toolbox; the feed bag on the tail; the shafts out front
    m.box((-5, BED - 8, 4), (10, 5, 8), flat(DWOOD, 2))
    m.box((6, BED - 6, -hl - 3), (4, 6, 3), sack)
    for sx in (-1, 1):
        m.box((sx * 8.5 - 0.75, 11, fz - 4), (1.5, 1.5, 52), flat(WOOD, 2), rot=(("x", -9),), pivot=(sx * 8.5, 11.75, fz - 4))
    m.box((-9, 13, fz + 8), (18, 1.5, 1.5), flat(WOOD, 2))
    return m


def install():
    game(hob_wagon(), "hob_wagon")
    game(wagon_horse(), "bramble", HORSE_AT)


def make(name):
    if name == "wagon_horse":
        wagon_horse().write(at=HORSE_AT)
    else:
        hob_wagon().write()


if __name__ == "__main__":
    import sys
    if sys.argv[1:2] == ["--install"]:
        install()
