"""The Plague Ward's props as real meshes (propkit.py does the baking and writing): sick cots in two halves, the
apothecary's shelves, jars and alembic, heaps of quicklime, the lime lamps' green glow, verdigris bars, soiled linen.

  blender -b -P tools/blender/plague_props.py -- [preview] [fast] [names...]
    preview -> tools/renders/plague_props.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "propkit.py"), encoding="utf-8").read())

TAR = wood("ward_tar", [(0.0, (0.01, 0.009, 0.008)), (0.5, (0.03, 0.026, 0.021)), (1.0, (0.06, 0.05, 0.04))], along="X", rough=0.5)
TAR_UP = wood("ward_tar_up", [(0.0, (0.01, 0.009, 0.008)), (0.5, (0.03, 0.026, 0.021)), (1.0, (0.06, 0.05, 0.04))], along="Z", rough=0.5)
LINEN = mottled("ward_linen_cloth", [(0.0, (0.38, 0.37, 0.31)), (0.7, (0.56, 0.55, 0.48)), (1.0, (0.62, 0.6, 0.52))], 16.0, 0.9)
STAIN = mottled("ward_stain", [(0.0, (0.22, 0.2, 0.08)), (1.0, (0.36, 0.33, 0.16))], 10.0, 0.9)
STRAW = mottled("ward_straw", [(0.0, (0.3, 0.23, 0.08)), (1.0, (0.52, 0.42, 0.18))], 45.0, 0.9)
LIME = mottled("quicklime_powder", [(0.0, (0.55, 0.56, 0.52)), (1.0, (0.78, 0.79, 0.75))], 22.0, 0.95)
COPPER = mottled("verdigris", [(0.0, (0.06, 0.16, 0.12)), (0.5, (0.12, 0.3, 0.24)), (0.8, (0.2, 0.12, 0.06)), (1.0, (0.3, 0.2, 0.1))], 9.0, 0.5,
                 **{"Metallic": 0.6})
BRASS = mat("ward_brass", (0.35, 0.25, 0.09), 0.35, **{"Metallic": 0.9})
GREEN = glass("lime_glow", (0.5, 1.0, 0.35), glow=4.0)
TONIC = glass("tonic", (0.2, 0.5, 0.12), glow=1.0)
GLASS = glass("ward_glass", (0.25, 0.3, 0.26), rough=0.1)
CLAY = mottled("jar_clay", [(0.0, (0.38, 0.33, 0.25)), (1.0, (0.55, 0.5, 0.4))], 8.0, 0.7)
GLAZE = mottled("jar_glaze", [(0.0, (0.06, 0.14, 0.1)), (1.0, (0.12, 0.26, 0.18))], 6.0, 0.25)
CORK = mottled("ward_cork", [(0.0, (0.25, 0.16, 0.08)), (1.0, (0.42, 0.3, 0.17))], 30.0, 0.9)
PAPER = mottled("ward_label", [(0.0, (0.45, 0.4, 0.3)), (1.0, (0.62, 0.57, 0.45))], 20.0, 0.9)
IRON = rusty("ward_iron", iron=(0.04, 0.04, 0.042), rust=(0.24, 0.1, 0.04), amount=0.55)
BACK = mat("ward_back", (0.01, 0.009, 0.008), 0.9)
GLOWS.update({GREEN, TONIC})
LIFT.update({"lime_lamp": 1.0})


def quicklime():
    """a heap of quicklime shovelled against the wall, crusted and cracked, a wooden shovel left in it"""
    bm = bmesh.new()
    vs = ellipsoid(bm, O + Vector((0, -0.05, 0.0)), (0.44, 0.4, 0.42), 0, seg=20)
    for v in vs:
        if v.co.z < 0:
            v.co.z = 0.0
    displace(vs, 0.04, 5.0, 2)
    for k in range(5):
        a = k * 1.4
        ellipsoid(bm, O + Vector((math.cos(a) * 0.36, math.sin(a) * 0.34, 0.02)), (0.08, 0.07, 0.04), 0, seg=8)
    tube(bm, [O + Vector((0.1, 0.1, 0.25)), O + Vector((0.3, 0.32, 0.85))], 0.02, 1, sides=6)
    box(bm, O + Vector((0.0, 0.0, 0.12)), O + Vector((0.16, 0.06, 0.32)), 1, bevel=0.01, rot=Matrix.Rotation(0.6, 3, "Z"))
    return new_obj("quicklime", bm, [LIME, TAR_UP])


def lime_lamp():
    """a ward lamp burning lime: a squat cage of riveted iron round green-glowing glass, a ring on top to hang it by"""
    bm = bmesh.new()
    c = O + Vector((0, 0, 0.14))
    cyl(bm, c, 0.17, 0.05, 0, seg=8)
    lathe(bm, [(0.0, 0.05), (0.12, 0.05), (0.15, 0.14), (0.14, 0.28), (0.09, 0.36), (0.0, 0.36)], c, 1, 16)
    for k in range(8):
        a = k * math.pi / 4
        tube(bm, [c + Vector((math.cos(a) * 0.16, math.sin(a) * 0.16, 0.05)), c + Vector((math.cos(a) * 0.17, math.sin(a) * 0.17, 0.2)),
                  c + Vector((math.cos(a) * 0.1, math.sin(a) * 0.1, 0.38))], 0.012, 0, sides=4)
    cyl(bm, c + Vector((0, 0, 0.37)), 0.11, 0.04, 0, seg=8, r2=0.06)
    tube(bm, ring(c + Vector((0, 0, 0.5)), 0.05, "Y", 12), 0.013, 0, sides=4, closed=True)
    tube(bm, [c + Vector((0, 0, 0.55)), O + Vector((0, 0, 1.0))], 0.015, 0, sides=5)
    return new_obj("lime_lamp", bm, [IRON, GREEN])


def ward_bars_post():
    bm = bmesh.new()
    box(bm, O + Vector((-0.05, -0.05, 0)), O + Vector((0.05, 0.05, 1.0)), 0, bevel=0.012)
    for z in (0.02, 0.96):
        box(bm, O + Vector((-0.07, -0.07, z)), O + Vector((0.07, 0.07, z + 0.04)), 0, bevel=0.01)
    return new_obj("ward_bars_post", bm, [COPPER])


def ward_bars_side():
    """verdigris bars to the north edge: two twisted uprights, a lattice crossing between them"""
    bm = bmesh.new()
    for y in (-0.36, -0.15):
        tube(bm, [Vector((0.5 + 0.012 * math.sin(t * 20), y + 0.012 * math.cos(t * 20), t)) for t in (k / 20 for k in range(21))], 0.026, 0, sides=6)
    for z in (0.1, 0.9):
        box(bm, Vector((0.475, -0.5, z - 0.025)), Vector((0.525, 0.0, z + 0.025)), 0, bevel=0.006)
    for z0 in (0.2, 0.5):   # the lattice
        tube(bm, [Vector((0.5, -0.5, z0)), Vector((0.5, 0.0, z0 + 0.3))], 0.014, 0, sides=4)
        tube(bm, [Vector((0.5, -0.5, z0 + 0.3)), Vector((0.5, 0.0, z0))], 0.014, 0, sides=4)
    return new_obj("ward_bars_side", bm, [COPPER])


def bottle(bm, c, h, r, mi_glass, mi_fill, mi_cork, fill=0.6):
    lathe(bm, [(0.0, 0.0), (r, 0.0), (r, h * 0.6), (r * 0.4, h * 0.8), (r * 0.35, h), (0.0, h)], c, mi_glass, 10)
    cyl(bm, c + Vector((0, 0, 0.004)), r * 0.9, h * 0.6 * fill, mi_fill, seg=10)
    cyl(bm, c + Vector((0, 0, h)), r * 0.38, 0.03, mi_cork, seg=8)


def apothecary_shelf():
    """the apothecary's shelves: three tarred boards in a frame, crowded with stoppered bottles, jars with paper
    labels, a mortar, a bundle of herbs hung drying"""
    bm = bmesh.new()
    box(bm, Vector((0, -1, 0)), Vector((1, -0.94, 1)), 4)
    for x in (0.0, 0.95):
        box(bm, Vector((x, -1, 0)), Vector((x + 0.05, 0, 1)), 0, bevel=0.008)
    for z in (0.0, 0.32, 0.64, 0.95):
        box(bm, Vector((0, -1, z)), Vector((1, 0, z + 0.05)), 0, bevel=0.008)
    for shelf, z in enumerate((0.05, 0.37, 0.69)):
        x = 0.1
        k = shelf * 5
        while x < 0.88:
            kind = (k * 7 + shelf) % 4
            if kind == 0:
                bottle(bm, Vector((x, -0.3, z)), 0.2, 0.045, 1, 2, 3)
                x += 0.12
            elif kind == 1:
                lathe(bm, [(0.0, 0.0), (0.07, 0.0), (0.075, 0.16), (0.06, 0.18), (0.0, 0.18)], Vector((x + 0.03, -0.45, z)), 5, 12)
                box(bm, Vector((x - 0.02, -0.381, z + 0.05)), Vector((x + 0.08, -0.375, z + 0.12)), 6)
                x += 0.17
            elif kind == 2:
                bottle(bm, Vector((x, -0.6, z)), 0.14, 0.035, 1, 2, 3, fill=0.9)
                bottle(bm, Vector((x + 0.06, -0.25, z)), 0.12, 0.03, 1, 2, 3, fill=0.3)
                x += 0.13
            else:
                lathe(bm, [(0.0, 0.0), (0.06, 0.0), (0.08, 0.08), (0.07, 0.1), (0.0, 0.05)], Vector((x + 0.03, -0.35, z)), 5, 12)
                tube(bm, [Vector((x + 0.02, -0.35, z + 0.06)), Vector((x + 0.1, -0.3, z + 0.16))], 0.012, 0, sides=5)
                x += 0.17
            k += 1
    for k in range(5):   # the herbs, hung under the top board
        a = k * 1.3
        tube(bm, [Vector((0.7 + 0.02 * k, -0.15, 0.95)), Vector((0.7 + 0.04 * k + 0.02 * math.cos(a), -0.13, 0.78))], 0.012, 7, sides=4)
    return new_obj("apothecary_shelf", bm, [TAR, GLASS, TONIC, CORK, BACK, CLAY, PAPER, STRAW])


def apothecary_jar():
    """a great glazed jar of salve, a cloth tied over its mouth, a ladle hooked on its rim"""
    bm = bmesh.new()
    lathe(bm, [(0.0, 0.0), (0.2, 0.0), (0.3, 0.2), (0.32, 0.42), (0.24, 0.62), (0.17, 0.7), (0.19, 0.76), (0.0, 0.76)], O, 0, 24)
    for k in range(2):
        tube(bm, ring(O + Vector((0, 0, 0.3 + k * 0.16)), 0.318 if k == 0 else 0.3, "Z", 28), 0.008, 1, sides=4, closed=True)
    cloth = lathe(bm, [(0.0, 0.83), (0.18, 0.8), (0.23, 0.74), (0.25, 0.64), (0.25, 0.6)], O, 2, 20, cap=False)
    displace([v for rg in cloth for v in rg], 0.012, 12.0, 4)
    tube(bm, ring(O + Vector((0, 0, 0.71)), 0.185, "Z", 20), 0.01, 3, sides=4, closed=True)
    for s in (-1, 1):
        tube(bm, [O + Vector((0.2 * s, 0.05, 0.42)), O + Vector((0.34 * s, 0.05, 0.52)), O + Vector((0.3 * s, 0.05, 0.62))], 0.025, 0, sides=6)
    return new_obj("apothecary_jar", bm, [GLAZE, CLAY, LINEN, STRAW])


def alembic():
    """the alembic on its brass stand: a bulbous flask of green tonic over a spirit lamp, the still-head's long arm
    running down into a receiving bottle"""
    bm = bmesh.new()
    for k in range(3):
        a = k * 2 * math.pi / 3
        tube(bm, [O + Vector((math.cos(a) * 0.24, math.sin(a) * 0.24, 0.0)), O + Vector((math.cos(a) * 0.16, math.sin(a) * 0.16, 0.3))], 0.015, 0, sides=5)
    tube(bm, ring(O + Vector((0, 0, 0.3)), 0.16, "Z", 16), 0.015, 0, sides=5, closed=True)
    lathe(bm, [(0.0, 0.03), (0.05, 0.03), (0.05, 0.1), (0.02, 0.13), (0.0, 0.13)], O, 1, 10)
    ellipsoid(bm, O + Vector((0, 0, 0.17)), (0.02, 0.02, 0.04), 2, seg=8)
    lathe(bm, [(0.0, 0.3), (0.12, 0.31), (0.17, 0.4), (0.15, 0.5), (0.05, 0.56), (0.04, 0.66), (0.0, 0.66)], O, 1, 20)
    ellipsoid(bm, O + Vector((0, 0, 0.4)), (0.14, 0.14, 0.07), 2, seg=14)
    lathe(bm, [(0.0, 0.66), (0.08, 0.66), (0.1, 0.74), (0.06, 0.8), (0.0, 0.81)], O, 1, 14)
    tube(bm, [O + Vector((0.06, 0.0, 0.76)), O + Vector((0.28, 0.06, 0.6)), O + Vector((0.34, 0.12, 0.3))], 0.014, 1, sides=6)
    bottle(bm, O + Vector((0.34, 0.14, 0.0)), 0.3, 0.07, 1, 2, 3, fill=0.4)
    return new_obj("alembic", bm, [BRASS, GLASS, TONIC, CORK])


def _cot(bm, head):
    """a sick cot's half: a low tarred frame, a straw pallet, a stained linen sheet; the head half has the pillow at
    the front (north), the foot half the cot's end at the back; each runs on off its open edge"""
    y0, y1 = (-1.0, -0.06) if head else (-0.94, 0.0)
    for y in ((-0.06,) if head else (-0.94,)):
        for x in (0.1, 0.9):
            box(bm, Vector((x - 0.04, y - 0.04, 0)), Vector((x + 0.04, y + 0.04, 0.5 if head else 0.36)), 0, bevel=0.01)
        box(bm, Vector((0.06, y - 0.03, 0.42 if head else 0.3)), Vector((0.94, y + 0.03, 0.48 if head else 0.34)), 0, bevel=0.008)
    for x in (0.08, 0.92):
        box(bm, Vector((x - 0.03, y0, 0.24)), Vector((x + 0.03, y1, 0.3)), 0, bevel=0.008)
    vs = box(bm, Vector((0.1, y0, 0.26)), Vector((0.9, y1, 0.36)), 1, bevel=0.03)
    displace(vs, 0.01, 8.0, 3 if head else 4)

    def at(u, v):
        y = y0 + (y1 - y0) * v
        x = 0.06 + 0.88 * u
        z = 0.375 + 0.02 * math.sin(v * 7 + u * 3) - (0.12 * (max(0, abs(u - 0.5) - 0.42) / 0.08) if abs(u - 0.5) > 0.42 else 0)
        return Vector((x, y, z))
    sheet(bm, at, 12, 10, 0.012, lambda u: 2 if (head and 0.3 < u < 0.5) else 3)
    if head:
        vs = ellipsoid(bm, Vector((0.5, -0.24, 0.42)), (0.3, 0.13, 0.06), 3, seg=12)
        displace(vs, 0.01, 9.0, 1)


def sheet(bm, at, nu, nv, thick, mi):
    top, bot = [], []
    for j in range(nv + 1):
        rt, rb = [], []
        for i in range(nu + 1):
            p = at(i / nu, j / nv)
            rt.append(bm.verts.new(p + Vector((0, 0, thick / 2))))
            rb.append(bm.verts.new(p - Vector((0, 0, thick / 2))))
        top.append(rt)
        bot.append(rb)
    for j in range(nv):
        for i in range(nu):
            m = mi((i + 0.5) / nu)
            bm.faces.new((top[j][i], top[j][i + 1], top[j + 1][i + 1], top[j + 1][i])).material_index = m
            bm.faces.new((bot[j][i], bot[j + 1][i], bot[j + 1][i + 1], bot[j][i + 1])).material_index = m


def sick_cot_head():
    bm = bmesh.new()
    _cot(bm, True)
    return new_obj("sick_cot_head", bm, [TAR_UP, STRAW, STAIN, LINEN])


def sick_cot_foot():
    bm = bmesh.new()
    _cot(bm, False)
    return new_obj("sick_cot_foot", bm, [TAR_UP, STRAW, STAIN, LINEN])


def ward_linen():
    """soiled linen dropped on the boards: a crumpled sheet, a rolled bandage, stains"""
    bm = bmesh.new()

    def at(u, v):
        x, y = u - 0.5, v - 0.5
        z = 0.012 + 0.03 * max(0, math.sin(u * 9 + 1) * math.cos(v * 7)) + 0.02 * max(0, 1 - (x * x + y * y) * 6)
        return O + Vector((x * 0.82, y * 0.7, z))
    sheet(bm, at, 14, 12, 0.008, lambda u: 1 if 0.55 < u < 0.75 else 0)
    cyl(bm, O + Vector((0.26, 0.22, 0.04)), 0.04, 0.16, 0, seg=12, axis="X")
    return new_obj("ward_linen", bm, [LINEN, STAIN])


MAKE = [(quicklime, (256, 256)), (lime_lamp, (128, 128)), (ward_bars_post, (64, 64)), (ward_bars_side, (64, 64)),
        (apothecary_shelf, (256, 256)), (apothecary_jar, (256, 256)), (alembic, (256, 256)), (sick_cot_head, (256, 256)),
        (sick_cot_foot, (256, 256)), (ward_linen, (128, 128))]
run(MAKE, GLOWS, "plague_props")
