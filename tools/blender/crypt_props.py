"""The Crypt's props as real meshes (propkit.py does the baking and writing): the abbey's vigil candles and candle
clusters, its pews, wrought grave railings and vault bars, hanging lanterns and the vault bell, bone piles, a folded
shroud, the reliquary that holds the loot.

  blender -b -P tools/blender/crypt_props.py -- [preview] [fast] [names...]
    preview -> tools/renders/crypt_props.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "propkit.py"), encoding="utf-8").read())

WAX = mottled("crypt_wax", [(0.0, (0.5, 0.46, 0.38)), (0.6, (0.7, 0.66, 0.56)), (1.0, (0.8, 0.77, 0.68))], 12.0, 0.45)
WAX_OLD = mottled("crypt_wax_old", [(0.0, (0.36, 0.32, 0.24)), (1.0, (0.58, 0.53, 0.42))], 9.0, 0.5)
FLAME = glass("crypt_flame", (1.0, 0.7, 0.3), glow=5.0)
LAMP = glass("crypt_lamp_glass", (1.0, 0.66, 0.3), glow=3.5)
WICK = mat("crypt_wick", (0.02, 0.018, 0.016), 0.8)
IRON = rusty("crypt_iron", iron=(0.035, 0.035, 0.04), rust=(0.2, 0.09, 0.04), amount=0.6, rough=0.5)
SILVER = mat("crypt_silver", (0.42, 0.42, 0.44), 0.35, **{"Metallic": 0.9})
BRONZE = mottled("bell_bronze", [(0.0, (0.08, 0.1, 0.07)), (0.5, (0.22, 0.17, 0.08)), (1.0, (0.4, 0.3, 0.14))], 5.0, 0.4, **{"Metallic": 0.8})
PEW = wood("pew_oak", [(0.0, (0.02, 0.013, 0.009)), (0.5, (0.055, 0.035, 0.022)), (1.0, (0.1, 0.066, 0.04))], along="X")
PEW_UP = wood("pew_oak_up", [(0.0, (0.02, 0.013, 0.009)), (0.5, (0.055, 0.035, 0.022)), (1.0, (0.1, 0.066, 0.04))], along="Z")
BONE = mottled("crypt_bone", [(0.0, (0.3, 0.27, 0.2)), (0.6, (0.55, 0.5, 0.4)), (1.0, (0.68, 0.64, 0.53))], 14.0, 0.6)
HOLE = mat("crypt_hole", (0.01, 0.008, 0.008), 0.9)
LINEN = mottled("shroud_linen", [(0.0, (0.38, 0.36, 0.32)), (1.0, (0.6, 0.58, 0.52))], 20.0, 0.9)
STONE = mottled("crypt_stone_prop", [(0.0, (0.12, 0.12, 0.13)), (1.0, (0.3, 0.3, 0.31))], 6.0, 0.8)
GLOWS.update({FLAME, LAMP})
LIFT.update({"crypt_lantern": 1.0, "crypt_bell": 1.2})


def candle(bm, c, h, r, seed, mi_wax=0, mi_flame=2, mi_wick=3, drips=3):
    """one candle: a wax column melted unevenly at the top, runs of wax down its side, a wick and its flame"""
    vs = cyl(bm, c, r, h, mi_wax, seg=12, r2=r * 0.95)
    displace(vs, r * 0.08, 20.0, seed)
    for d in range(drips):
        a = d * 2.3 + seed
        p = c + Vector((math.cos(a) * r, math.sin(a) * r, h * (0.75 + 0.08 * d)))
        tube(bm, [p, p + Vector((math.cos(a) * 0.006, math.sin(a) * 0.006, -h * (0.25 + 0.15 * d)))], lambda t: r * 0.22 * (1.1 - t), mi_wax, sides=5)
    tube(bm, [c + Vector((0, 0, h)), c + Vector((0, 0, h + 0.03))], 0.004, mi_wick, sides=4)
    ellipsoid(bm, c + Vector((0, 0, h + 0.06)), (0.018, 0.018, 0.045), mi_flame, seg=10)


def vigil_candles():
    """a vigil: a mound of old wax built up over years, a crowd of candles of every height burning on it"""
    bm = bmesh.new()
    vs = ellipsoid(bm, O + Vector((0, 0, 0.0)), (0.44, 0.4, 0.14), 1, seg=18)
    displace(vs, 0.03, 6.0, 1)
    spots = [(0.0, 0.0, 0.55, 0.07), (0.18, 0.1, 0.42, 0.06), (-0.16, 0.12, 0.36, 0.06), (0.1, -0.2, 0.3, 0.05), (-0.2, -0.12, 0.46, 0.065),
             (0.28, -0.08, 0.22, 0.05), (-0.04, 0.26, 0.26, 0.05), (-0.3, 0.08, 0.18, 0.045), (0.24, 0.24, 0.16, 0.045)]
    for k, (x, y, h, r) in enumerate(spots):
        candle(bm, O + Vector((x, y, 0.08)), h, r, k, 0, 2, 3)
    return new_obj("vigil_candles", bm, [WAX, WAX_OLD, FLAME, WICK])


def crypt_candles():
    """three tall church candles in an iron pricket stand, wax pooled at their feet"""
    bm = bmesh.new()
    cyl(bm, O, 0.2, 0.03, 1, seg=16)
    for k in range(3):
        a = k * 2 * math.pi / 3 + 0.3
        tube(bm, [O + Vector((math.cos(a) * 0.17, math.sin(a) * 0.17, 0.0)), O + Vector((math.cos(a) * 0.22, math.sin(a) * 0.22, -0.0))], 0.02, 1, sides=5)
        c = O + Vector((math.cos(a) * 0.1, math.sin(a) * 0.1, 0.03))
        cyl(bm, c, 0.04, 0.03, 1, seg=10)
        candle(bm, c + Vector((0, 0, 0.03)), (0.5, 0.36, 0.28)[k], 0.045, k + 3, 0, 2, 3, drips=2)
    vs = ellipsoid(bm, O + Vector((0.05, -0.05, 0.03)), (0.14, 0.11, 0.015), 4, seg=10)
    return new_obj("crypt_candles", bm, [WAX, IRON, FLAME, WICK, WAX_OLD])


def crypt_pew():
    """an abbey pew: a thick seat on carved ends, a high back with a rail, worn pale where hands rested"""
    bm = bmesh.new()
    box(bm, Vector((0.0, -0.62, 0.4)), Vector((1.0, -0.06, 0.47)), 0, bevel=0.012)                # the seat
    box(bm, Vector((0.0, -0.84, 0.47)), Vector((1.0, -0.78, 1.0)), 0, bevel=0.012)                # the back
    box(bm, Vector((0.0, -0.88, 0.96)), Vector((1.0, -0.74, 1.02)), 0, bevel=0.015)               # its rail
    box(bm, Vector((0.0, -0.7, 0.12)), Vector((1.0, -0.66, 0.2)), 0, bevel=0.008)                 # the stretcher
    for k in range(4):   # panels in the back
        x = 0.06 + k * 0.235
        box(bm, Vector((x, -0.775, 0.55)), Vector((x + 0.2, -0.765, 0.92)), 1, bevel=0.004)
    for x in (0.04, 0.96):   # the legs under it, kept inside so a row of pews runs on
        box(bm, Vector((x - 0.035, -0.6, 0.0)), Vector((x + 0.035, -0.1, 0.4)), 1, bevel=0.01)
        box(bm, Vector((x - 0.035, -0.84, 0.0)), Vector((x + 0.035, -0.74, 0.47)), 1, bevel=0.01)
    return new_obj("crypt_pew", bm, [PEW, PEW_UP])


def grave_railing_post():
    """a wrought iron post, square, its head a spear point over a collar"""
    bm = bmesh.new()
    box(bm, O + Vector((-0.04, -0.04, 0)), O + Vector((0.04, 0.04, 0.88)), 0, bevel=0.008)
    cyl(bm, O + Vector((0, 0, 0.84)), 0.06, 0.05, 0, seg=10)
    tube(bm, [O + Vector((0, 0, 0.89)), O + Vector((0, 0, 1.0))], lambda t: 0.05 * (1 - t) + 0.004, 0, sides=4)
    return new_obj("grave_railing_post", bm, [IRON])


def grave_railing_side():
    """the railing to the north edge: two rails, palings between ending in spear points, a scroll at the foot"""
    bm = bmesh.new()
    for z in (0.12, 0.7):
        box(bm, Vector((0.48, -0.5, z - 0.02)), Vector((0.52, 0.0, z + 0.02)), 0, bevel=0.005)
    for y in (-0.38, -0.13):
        box(bm, Vector((0.485, y - 0.015, 0.0)), Vector((0.515, y + 0.015, 0.84)), 0, bevel=0.004)
        tube(bm, [Vector((0.5, y, 0.84)), Vector((0.5, y, 0.94))], lambda t: 0.035 * (1 - t) + 0.003, 0, sides=4)
    tube(bm, [Vector((0.5, -0.26 + 0.07 * math.cos(t), 0.3 + 0.07 * math.sin(t))) for t in (k / 10 * 1.8 * math.pi for k in range(11))], 0.012, 0, sides=4)
    return new_obj("grave_railing_side", bm, [IRON])


def vault_bars_post():
    bm = bmesh.new()
    cyl(bm, O, 0.055, 1.0, 0, seg=10)
    for z in (0.0, 0.47, 0.92):
        cyl(bm, O + Vector((0, 0, z)), 0.075, 0.08, 1, seg=10)
    return new_obj("vault_bars_post", bm, [IRON, SILVER])


def vault_bars_side():
    """the vault's bars to the north edge: two thick uprights banded in silver, a crossbar with silver studs"""
    bm = bmesh.new()
    for y in (-0.34, -0.17):
        cyl(bm, Vector((0.5, y, 0.0)), 0.04, 1.0, 0, seg=8)
        for z in (0.2, 0.8):
            cyl(bm, Vector((0.5, y, z)), 0.05, 0.04, 1, seg=8)
    for z in (0.47,):
        box(bm, Vector((0.47, -0.5, z - 0.04)), Vector((0.53, 0.0, z + 0.04)), 0, bevel=0.008)
        for y in (-0.34, -0.17):
            ellipsoid(bm, Vector((0.5, y, z)), (0.045, 0.035, 0.035), 1, seg=8)
    return new_obj("vault_bars_side", bm, [IRON, SILVER])


def crypt_lantern():
    """an abbey lantern: a pierced iron hood, horn panes glowing, a ring on top"""
    bm = bmesh.new()
    c = O + Vector((0, 0, 0.12))
    box(bm, c + Vector((-0.13, -0.13, 0)), c + Vector((0.13, 0.13, 0.05)), 0, bevel=0.01)
    box(bm, c + Vector((-0.1, -0.1, 0.05)), c + Vector((0.1, 0.1, 0.33)), 1, bevel=0.005)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(bm, c + Vector((sx * 0.12 - 0.015, sy * 0.12 - 0.015, 0.05)), c + Vector((sx * 0.12 + 0.015, sy * 0.12 + 0.015, 0.34)), 0, bevel=0.004)
    lathe(bm, [(0.16, 0.33), (0.16, 0.36), (0.08, 0.46), (0.03, 0.5), (0.0, 0.5)], c, 0, 4)
    tube(bm, ring(c + Vector((0, 0, 0.55)), 0.04, "Y", 12), 0.01, 0, sides=4, closed=True)
    links(bm, c + Vector((0, 0, 0.58)), O + Vector((0, 0, 1.0)), 0, w=0.05, r=0.012)
    return new_obj("crypt_lantern", bm, [IRON, LAMP])


def crypt_bell():
    """the vault bell hung from the ceiling: bronze gone green, a yoke and its clapper"""
    bm = bmesh.new()
    prof = [(0.0, 0.62), (0.12, 0.62), (0.16, 0.58), (0.19, 0.42), (0.24, 0.24), (0.32, 0.1), (0.34, 0.06), (0.32, 0.06), (0.22, 0.12),
            (0.17, 0.28), (0.13, 0.46), (0.1, 0.56), (0.0, 0.57)]
    lathe(bm, prof, O, 0, 28)
    box(bm, O + Vector((-0.2, -0.05, 0.62)), O + Vector((0.2, 0.05, 0.74)), 1, bevel=0.015)
    box(bm, O + Vector((-0.04, -0.04, 0.74)), O + Vector((0.04, 0.04, 1.0)), 1, bevel=0.008)
    tube(bm, [O + Vector((0, 0, 0.56)), O + Vector((0.03, 0, 0.14))], 0.015, 2, sides=5)
    ellipsoid(bm, O + Vector((0.03, 0, 0.11)), (0.045, 0.045, 0.05), 2, seg=10)
    for z in (0.2, 0.45):
        tube(bm, ring(O + Vector((0, 0, z)), 0.235 if z < 0.3 else 0.185, "Z", 28), 0.008, 0, sides=4, closed=True)
    return new_obj("crypt_bell", bm, [BRONZE, PEW_UP, IRON])


def skull(bm, c, s, a, mi_bone, mi_hole):
    rot = Matrix.Rotation(a, 3, "Z")
    vs = ellipsoid(bm, c + Vector((0, 0, 0.07 * s)), (0.09 * s, 0.11 * s, 0.085 * s), mi_bone, seg=14)
    displace(vs, 0.005 * s, 8.0, int(a * 10))
    ellipsoid(bm, c + rot @ Vector((0, 0.07 * s, 0.025 * s)), (0.065 * s, 0.05 * s, 0.035 * s), mi_bone, seg=10)
    for sx in (-1, 1):
        ellipsoid(bm, c + rot @ Vector((sx * 0.035 * s, 0.09 * s, 0.075 * s)), (0.026 * s, 0.02 * s, 0.026 * s), mi_hole, seg=8)
    ellipsoid(bm, c + rot @ Vector((0, 0.11 * s, 0.045 * s)), (0.012 * s, 0.01 * s, 0.018 * s), mi_hole, seg=6)


def bone_pile():
    """a heap of the abbey's dead: long bones crossed every way, skulls on top"""
    bm = bmesh.new()
    for k in range(14):
        a = k * 2.39
        r = 0.08 + (k % 4) * 0.08
        c = O + Vector((math.cos(a) * r, math.sin(a) * r, 0.03 + (k // 4) * 0.045))
        d = Vector((math.cos(a * 1.7 + 1), math.sin(a * 1.7 + 1), 0.1 * ((k % 3) - 1))) * (0.18 + 0.04 * (k % 3))
        tube(bm, [c - d, c + d], 0.022, 0, sides=6)
        for e in (c - d, c + d):
            ellipsoid(bm, e, (0.032, 0.032, 0.03), 0, seg=8)
    for k, (x, y, z, a) in enumerate([(0.0, 0.05, 0.16, 0.2), (0.17, -0.1, 0.1, -0.6), (-0.18, -0.06, 0.08, 0.9)]):
        skull(bm, O + Vector((x, y, z)), 1.2, a, 0, 1)
    return new_obj("bone_pile", bm, [BONE, HOLE])


def burial_shroud():
    """a burial shroud laid out on the floor, a body's shape under the linen, folds at its edges"""
    bm = bmesh.new()
    nu, nv = 10, 16
    grid = []
    for j in range(nv + 1):
        row = []
        for i in range(nu + 1):
            u, v = i / nu - 0.5, j / nv - 0.5
            body = max(0.0, 1 - (u / 0.28) ** 2) * (0.1 + 0.03 * math.cos(v * 9)) * (1 if abs(v) < 0.44 else 0.0)
            head = 0.06 * max(0.0, 1 - ((u / 0.16) ** 2 + ((v - 0.36) / 0.08) ** 2))
            fold = 0.012 * math.sin(u * 30) * abs(u) * 2
            row.append(bm.verts.new(O + Vector((u * 0.62, v * 0.92, 0.006 + body + head + fold))))
        grid.append(row)
    for j in range(nv):
        for i in range(nu):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i])).material_index = 0
    return new_obj("burial_shroud", bm, [LINEN])


def reliquary():
    """the abbey's reliquary: an iron-bound oak chest on stone feet, silver corners, a silver skull on its front"""
    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(bm, O + Vector((sx * 0.36 - 0.06, sy * 0.24 - 0.06, 0)), O + Vector((sx * 0.36 + 0.06, sy * 0.24 + 0.06, 0.08)), 3, bevel=0.01)
    box(bm, O + Vector((-0.43, -0.3, 0.08)), O + Vector((0.43, 0.3, 0.52)), 0, bevel=0.02)
    lid = lathe(bm, [(0.0, -0.44), (0.31, -0.44), (0.31, 0.44), (0.0, 0.44)], O + Vector((0, 0, 0.52)), 0, 4, "X")
    for rg in lid:   # a pitched lid, like a shrine's roof
        for v in rg:
            if v.co.z < O.z + 0.52:
                v.co.z = O.z + 0.52
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(bm, O + Vector((sx * 0.43 - 0.05 * (sx > 0), sy * 0.3 - 0.05 * (sy > 0), 0.08)),
                O + Vector((sx * 0.43 + 0.05 * (sx < 0), sy * 0.3 + 0.05 * (sy < 0), 0.52)), 2, bevel=0.006)
    for x in (-0.2, 0.2):
        box(bm, O + Vector((x - 0.035, -0.31, 0.08)), O + Vector((x + 0.035, 0.31, 0.53)), 1, bevel=0.005)
    skull(bm, O + Vector((0, 0.3, 0.22)), 0.9, 0.0, 2, 4)
    return new_obj("reliquary", bm, [PEW_UP, IRON, SILVER, STONE, HOLE])


MAKE = [(vigil_candles, (256, 256)), (crypt_candles, (128, 128)), (crypt_pew, (256, 256)), (grave_railing_post, (64, 64)),
        (grave_railing_side, (64, 64)), (vault_bars_post, (64, 64)), (vault_bars_side, (64, 64)), (crypt_lantern, (128, 128)),
        (crypt_bell, (256, 256)), (bone_pile, (256, 256)), (burial_shroud, (128, 128)), (reliquary, (256, 256))]
run(MAKE, GLOWS, "crypt_props")
