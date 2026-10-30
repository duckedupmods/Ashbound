"""The Slag Foundry's props as real meshes (propkit.py does the baking and writing): fire baskets on tall iron legs,
heaped coal fires, the smiths' anvils, squat bloomery furnaces glowing at the mouth, an iron strongbox.

  blender -b -P tools/blender/foundry_props.py -- [preview] [fast] [names...]
    preview -> tools/renders/foundry_props.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "propkit.py"), encoding="utf-8").read())

IRON = rusty("foundry_iron", iron=(0.03, 0.03, 0.032), rust=(0.22, 0.08, 0.03), amount=0.62, rough=0.5)
FORGED = mat("forged_iron", (0.05, 0.05, 0.055), 0.35, **{"Metallic": 0.9})
COAL = mottled("coal", [(0.0, (0.008, 0.008, 0.008)), (1.0, (0.05, 0.045, 0.04))], 20.0, 0.6)
EMBER = glass("ember", (1.0, 0.32, 0.06), glow=5.0)
FIRE = glass("forge_flame", (1.0, 0.55, 0.12), glow=6.0)
BRICK = mottled("furnace_brick", [(0.0, (0.025, 0.013, 0.009)), (0.6, (0.07, 0.033, 0.02)), (1.0, (0.12, 0.06, 0.035))], 7.0, 0.85)
SOOT = mottled("furnace_soot", [(0.0, (0.01, 0.01, 0.01)), (1.0, (0.05, 0.045, 0.04))], 9.0, 0.9)
WOOD = wood("foundry_log", [(0.0, (0.03, 0.02, 0.012)), (0.5, (0.08, 0.05, 0.03)), (1.0, (0.14, 0.09, 0.05))], along="X")
GLOWS.update({EMBER, FIRE})


def brazier():
    """a fire basket of forged straps on three tall legs, heaped with coals burning white at the heart, flames
    licking up over the rim"""
    bm = bmesh.new()
    for k in range(3):
        a = k * 2 * math.pi / 3
        tube(bm, [O + Vector((math.cos(a) * 0.36, math.sin(a) * 0.36, 0.0)), O + Vector((math.cos(a) * 0.22, math.sin(a) * 0.22, 0.7)),
                  O + Vector((math.cos(a) * 0.3, math.sin(a) * 0.3, 1.0))], 0.035, 0, sides=6)
        cyl(bm, O + Vector((math.cos(a) * 0.36, math.sin(a) * 0.36, 0.0)), 0.06, 0.04, 0, seg=8)
    tube(bm, ring(O + Vector((0, 0, 0.62)), 0.24, "Z", 18), 0.02, 0, sides=5, closed=True)
    for k in range(12):   # the basket's straps
        a = k * math.pi / 6
        tube(bm, [O + Vector((math.cos(a) * 0.12, math.sin(a) * 0.12, 0.74)), O + Vector((math.cos(a) * 0.34, math.sin(a) * 0.34, 1.0)),
                  O + Vector((math.cos(a) * 0.38, math.sin(a) * 0.38, 1.12))], 0.018, 0, sides=4)
    tube(bm, ring(O + Vector((0, 0, 1.08)), 0.37, "Z", 24), 0.022, 0, sides=5, closed=True)
    vs = ellipsoid(bm, O + Vector((0, 0, 1.0)), (0.32, 0.32, 0.12), 1, seg=16)
    displace(vs, 0.03, 9.0, 1)
    for k in range(9):
        a = k * 2.4
        r = 0.08 + (k % 3) * 0.08
        ellipsoid(bm, O + Vector((math.cos(a) * r, math.sin(a) * r, 1.08)), (0.06, 0.06, 0.04), 2, seg=8)
    for k, (dx, dy, h) in enumerate([(0.0, 0.0, 0.42), (0.12, 0.06, 0.3), (-0.1, 0.09, 0.26), (0.04, -0.13, 0.32), (-0.13, -0.06, 0.22)]):
        c = O + Vector((dx, dy, 1.08))
        lathe(bm, [(0.0, 0.0), (0.09, 0.02), (0.07, h * 0.4), (0.03, h * 0.8), (0.0, h)], c, 3, 8)
    return new_obj("brazier", bm, [IRON, COAL, EMBER, FIRE])


def coal_fire():
    """a forge-hand's fire on the floor: a ring of slag lumps round a heap of coal glowing through, split logs on it"""
    bm = bmesh.new()
    for k in range(8):
        a = k * 2 * math.pi / 8
        vs = ellipsoid(bm, O + Vector((math.cos(a) * 0.38, math.sin(a) * 0.38, 0.05)), (0.1, 0.08, 0.08), 0, seg=10)
        displace(vs, 0.02, 7.0, k)
    vs = ellipsoid(bm, O, (0.3, 0.3, 0.14), 0, seg=16)
    displace(vs, 0.025, 10.0, 3)
    for k in range(10):
        a = k * 2.4
        r = 0.05 + (k % 4) * 0.06
        ellipsoid(bm, O + Vector((math.cos(a) * r, math.sin(a) * r, 0.11)), (0.05, 0.05, 0.035), 1, seg=8)
    for k, a in enumerate((0.4, 2.0, 3.8)):
        d = Vector((math.cos(a), math.sin(a), 0))
        tube(bm, [O + d * 0.3 + Vector((0, 0, 0.08)), O + Vector((0, 0, 0.3)) - d * 0.05], 0.045, 2, sides=7)
    for k, (dx, dy, h) in enumerate([(0.0, 0.0, 0.5), (0.1, 0.05, 0.36), (-0.08, 0.07, 0.3), (0.03, -0.1, 0.34)]):
        lathe(bm, [(0.0, 0.0), (0.1, 0.02), (0.08, h * 0.4), (0.03, h * 0.8), (0.0, h)], O + Vector((dx, dy, 0.14)), 3, 8)
    return new_obj("coal_fire", bm, [COAL, EMBER, WOOD, FIRE])


def foundry_anvil():
    """a smith's anvil on its oak block: a long horn, a heel with the hardy hole, a hammer left on the face"""
    bm = bmesh.new()
    vs = cyl(bm, O, 0.26, 0.42, 2, seg=14, r2=0.24)
    displace(vs, 0.01, 8.0, 2)
    box(bm, O + Vector((-0.18, -0.13, 0.42)), O + Vector((0.18, 0.13, 0.5)), 0, bevel=0.015)       # its foot
    box(bm, O + Vector((-0.1, -0.08, 0.5)), O + Vector((0.1, 0.08, 0.64)), 0, bevel=0.01)          # the waist
    box(bm, O + Vector((-0.28, -0.13, 0.64)), O + Vector((0.2, 0.13, 0.78)), 0, bevel=0.015)       # the face
    tube(bm, [O + Vector((0.2, 0, 0.73)), O + Vector((0.32, 0, 0.73)), O + Vector((0.44, 0, 0.7))], lambda t: 0.08 * (1 - t) + 0.008, 0, sides=10)
    box(bm, O + Vector((-0.22, -0.03, 0.775)), O + Vector((-0.17, 0.03, 0.785)), 3)
    tube(bm, [O + Vector((-0.05, 0.05, 0.8)), O + Vector((0.12, -0.18, 0.8))], 0.018, 2, sides=6)    # the hammer's haft
    box(bm, O + Vector((-0.09, 0.02, 0.78)), O + Vector((-0.01, 0.11, 0.84)), 1, bevel=0.008)
    return new_obj("foundry_anvil", bm, [FORGED, IRON, WOOD, SOOT])


def bloomery():
    """a squat brick bloomery, soot-black, its mouth glowing with the bloom inside, an iron door hung open, a chimney
    stub on top"""
    bm = bmesh.new()
    vs = lathe(bm, [(0.0, 0.0), (0.46, 0.0), (0.47, 0.1), (0.44, 0.55), (0.32, 0.8), (0.18, 0.88), (0.18, 1.0), (0.0, 1.0)], O, 0, 20)
    displace([v for rg in vs for v in rg], 0.012, 7.0, 3)
    box(bm, O + Vector((-0.16, 0.38, 0.1)), O + Vector((0.16, 0.48, 0.42)), 2)                      # the glowing mouth
    box(bm, O + Vector((-0.2, 0.42, 0.06)), O + Vector((0.2, 0.47, 0.1)), 3, bevel=0.01)             # its sill
    box(bm, O + Vector((-0.2, 0.42, 0.42)), O + Vector((0.2, 0.47, 0.47)), 3, bevel=0.01)
    box(bm, O + Vector((0.2, 0.42, 0.08)), O + Vector((0.24, 0.72, 0.44)), 3, bevel=0.01, rot=Matrix.Rotation(-0.3, 3, "Z"))
    for k in range(5):
        a = k * 1.25 + 0.3
        r = 0.45 - 0.02 * k
        ellipsoid(bm, O + Vector((math.cos(a) * r, math.sin(a) * r, 0.2 + 0.1 * k)), (0.06, 0.04, 0.05), 1, seg=8)
    tube(bm, ring(O + Vector((0, 0, 0.5)), 0.43, "Z", 24), 0.02, 3, sides=5, closed=True)
    return new_obj("bloomery", bm, [BRICK, SOOT, EMBER, IRON])


def kiln_coffer():
    """a strongbox of riveted kiln iron, its lid ridged, a heavy ring for a handle at each end"""
    bm = bmesh.new()
    box(bm, O + Vector((-0.43, -0.3, 0.0)), O + Vector((0.43, 0.3, 0.5)), 0, bevel=0.02)
    box(bm, O + Vector((-0.45, -0.32, 0.5)), O + Vector((0.45, 0.32, 0.62)), 0, bevel=0.025)
    for x in (-0.25, 0.0, 0.25):
        box(bm, O + Vector((x - 0.02, -0.33, 0.6)), O + Vector((x + 0.02, 0.33, 0.66)), 1, bevel=0.008)
    for x in (-0.43, 0.43):
        for y in (-0.3, 0.3):
            for z in (0.08, 0.3, 0.46):
                ellipsoid(bm, O + Vector((x * 0.95, y * 1.02, z)), (0.018, 0.018, 0.018), 1, seg=6)
    for s in (-1, 1):
        tube(bm, ring(O + Vector((s * 0.46, 0, 0.3)), 0.07, "X", 12), 0.014, 1, sides=4, closed=True)
    box(bm, O + Vector((-0.07, 0.3, 0.3)), O + Vector((0.07, 0.34, 0.52)), 1, bevel=0.008)
    return new_obj("kiln_coffer", bm, [IRON, FORGED])


MAKE = [(brazier, (256, 256)), (coal_fire, (256, 256)), (foundry_anvil, (256, 256)), (bloomery, (256, 256)), (kiln_coffer, (256, 256))]
run(MAKE, GLOWS, "foundry_props")
