"""The Ossuary Engine's props as real meshes (propkit.py does the baking and writing): soul lamps of bone and brass,
skulls with candles on their crowns, the pale-blue soul fire in the pits, a pyre of bones burning blue, the engine's
lanterns, the bone saw and the grinding wheel.

  blender -b -P tools/blender/ossuary_props.py -- [preview] [fast] [names...]
    preview -> tools/renders/ossuary_props.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "propkit.py"), encoding="utf-8").read())

BONE = mottled("oss_bone", [(0.0, (0.3, 0.26, 0.19)), (0.6, (0.55, 0.49, 0.38)), (1.0, (0.68, 0.63, 0.52))], 14.0, 0.6)
HOLE = mat("oss_hole", (0.01, 0.008, 0.008), 0.9)
BRASS = mottled("oss_brass", [(0.0, (0.12, 0.08, 0.03)), (0.6, (0.32, 0.22, 0.08)), (1.0, (0.45, 0.33, 0.13))], 7.0, 0.35, **{"Metallic": 0.85})
IRON = rusty("oss_iron", iron=(0.035, 0.035, 0.04), rust=(0.2, 0.09, 0.04), amount=0.6, rough=0.5)
SOUL = glass("soul_glow", (0.35, 0.85, 1.0), glow=4.5)
SOUL_DEEP = glass("soul_deep", (0.12, 0.45, 0.9), glow=3.0)
WAX = mottled("oss_wax", [(0.0, (0.45, 0.42, 0.34)), (1.0, (0.7, 0.66, 0.56))], 12.0, 0.45)
FLAME = glass("oss_flame", (1.0, 0.68, 0.3), glow=5.0)
STONE = mottled("oss_wheel", [(0.0, (0.14, 0.13, 0.12)), (1.0, (0.32, 0.3, 0.27))], 12.0, 0.85)
WOOD = wood("oss_wood", [(0.0, (0.02, 0.015, 0.011)), (0.5, (0.05, 0.035, 0.024)), (1.0, (0.09, 0.065, 0.045))], along="X")
GLOWS.update({SOUL, SOUL_DEEP, FLAME})
LIFT.update({"ossuary_lantern": 1.0})


def skull(bm, c, s, a, mi_bone, mi_hole):
    rot = Matrix.Rotation(a, 3, "Z")
    vs = ellipsoid(bm, c + Vector((0, 0, 0.07 * s)), (0.09 * s, 0.11 * s, 0.085 * s), mi_bone, seg=14)
    displace(vs, 0.005 * s, 8.0, int(a * 10) + 3)
    ellipsoid(bm, c + rot @ Vector((0, 0.07 * s, 0.025 * s)), (0.065 * s, 0.05 * s, 0.035 * s), mi_bone, seg=10)
    for sx in (-1, 1):
        ellipsoid(bm, c + rot @ Vector((sx * 0.035 * s, 0.09 * s, 0.075 * s)), (0.026 * s, 0.02 * s, 0.026 * s), mi_hole, seg=8)
    ellipsoid(bm, c + rot @ Vector((0, 0.11 * s, 0.045 * s)), (0.012 * s, 0.01 * s, 0.018 * s), mi_hole, seg=6)


def flame(bm, c, h, r, mi, seed=0):
    """a tongue of flame: a lathe that leans and flickers to a point"""
    rings = lathe(bm, [(0.0, 0.0), (r, h * 0.12), (r * 0.85, h * 0.4), (r * 0.45, h * 0.75), (0.0, h)], c, mi, 10)
    for k, rg in enumerate(rings):
        t = k / (len(rings) - 1)
        for v in rg:
            v.co.x += math.sin(seed * 2.1 + t * 3) * 0.04 * t
            v.co.y += math.cos(seed * 1.7 + t * 2.5) * 0.04 * t


def soul_lamp():
    """a soul lamp: a cage of rib bones bound with brass rings round a pale-blue soul flame, a hook on top"""
    bm = bmesh.new()
    c = O + Vector((0, 0, 0.12))
    cyl(bm, c, 0.17, 0.05, 1, seg=12)
    for k in range(6):
        a = k * math.pi / 3
        tube(bm, [c + Vector((math.cos(a) * 0.15, math.sin(a) * 0.15, 0.05)), c + Vector((math.cos(a) * 0.19, math.sin(a) * 0.19, 0.25)),
                  c + Vector((math.cos(a) * 0.06, math.sin(a) * 0.06, 0.52))], lambda t: 0.022 * (1 - 0.4 * t), 0, sides=5)
    for z in (0.12, 0.38):
        tube(bm, ring(c + Vector((0, 0, z)), 0.18 if z < 0.2 else 0.13, "Z", 18), 0.012, 1, sides=4, closed=True)
    ellipsoid(bm, c + Vector((0, 0, 0.2)), (0.1, 0.1, 0.13), 3, seg=12)
    flame(bm, c + Vector((0, 0, 0.12)), 0.32, 0.07, 2, 1)
    tube(bm, ring(c + Vector((0, 0, 0.6)), 0.045, "Y", 12), 0.012, 1, sides=4, closed=True)
    return new_obj("soul_lamp", bm, [BONE, BRASS, SOUL, SOUL_DEEP])


def skull_lamp():
    """a skull set up as a lamp: a fat candle fixed on its crown with old wax run down over the brow, a brass ring
    through the top to hang it by"""
    bm = bmesh.new()
    skull(bm, O, 2.2, 0.0, 0, 1)
    c = O + Vector((0, -0.02, 0.36))
    vs = cyl(bm, c, 0.06, 0.18, 2, seg=12, r2=0.055)
    displace(vs, 0.006, 18.0, 2)
    for k in range(4):
        a = k * 1.7
        p = O + Vector((math.cos(a) * 0.12, math.sin(a) * 0.14, 0.32))
        tube(bm, [p, p + Vector((math.cos(a) * 0.04, math.sin(a) * 0.04, -0.12))], lambda t: 0.018 * (1.1 - t), 2, sides=5)
    ellipsoid(bm, c + Vector((0, 0, 0.24)), (0.024, 0.024, 0.055), 3, seg=10)
    tube(bm, ring(O + Vector((0.0, -0.13, 0.42)), 0.05, "X", 12), 0.01, 4, sides=4, closed=True)
    return new_obj("skull_lamp", bm, [BONE, HOLE, WAX, FLAME, BRASS])


def soul_flame():
    """soul fire burning on the ash: low pale-blue tongues, a few taller"""
    bm = bmesh.new()
    for k, (x, y, h) in enumerate([(0.0, 0.0, 0.7), (0.22, 0.15, 0.45), (-0.2, 0.18, 0.5), (0.18, -0.22, 0.4), (-0.22, -0.16, 0.55),
                                   (0.32, -0.02, 0.3), (-0.05, 0.32, 0.35), (-0.32, 0.0, 0.3), (0.05, -0.32, 0.32)]):
        flame(bm, O + Vector((x, y, 0.0)), h, 0.1 if h > 0.5 else 0.08, 0 if h > 0.5 else 1, k)
    return new_obj("soul_flame", bm, [SOUL, SOUL_DEEP])


def soul_pyre():
    """a pyre of bones stacked crosswise like logs, burning in soul fire, a skull on top"""
    bm = bmesh.new()
    for layer in range(3):
        for k in range(3):
            d = (k - 1) * 0.22
            a, b = (Vector((d, -0.36, 0.04 + layer * 0.08)), Vector((d, 0.36, 0.04 + layer * 0.08))) if layer % 2 == 0 else \
                (Vector((-0.36, d, 0.04 + layer * 0.08)), Vector((0.36, d, 0.04 + layer * 0.08)))
            tube(bm, [O + a, O + b], 0.03, 0, sides=6)
            for e in (a, b):
                ellipsoid(bm, O + e, (0.045, 0.045, 0.04), 0, seg=8)
    skull(bm, O + Vector((0.05, 0.0, 0.24)), 1.3, 0.4, 0, 1)
    for k, (x, y, h) in enumerate([(0.0, 0.0, 0.75), (0.18, 0.12, 0.5), (-0.16, 0.14, 0.45), (0.12, -0.18, 0.5), (-0.18, -0.12, 0.4)]):
        flame(bm, O + Vector((x, y, 0.12)), h, 0.09, 2 if k else 3, k + 3)
    return new_obj("soul_pyre", bm, [BONE, HOLE, SOUL, SOUL_DEEP])


def ossuary_lantern():
    """the engine's lantern: a brass drum with slots glowing soul-blue, a domed cap, hung by its ring"""
    bm = bmesh.new()
    c = O + Vector((0, 0, 0.12))
    cyl(bm, c, 0.15, 0.04, 0, seg=16)
    cyl(bm, c + Vector((0, 0, 0.04)), 0.11, 0.28, 1, seg=16)
    for k in range(8):
        a = k * math.pi / 4
        box(bm, c + Vector((math.cos(a) * 0.12 - 0.015, math.sin(a) * 0.12 - 0.015, 0.04)),
            c + Vector((math.cos(a) * 0.12 + 0.015, math.sin(a) * 0.12 + 0.015, 0.32)), 0, bevel=0.004)
    lathe(bm, [(0.15, 0.32), (0.15, 0.35), (0.09, 0.43), (0.03, 0.47), (0.0, 0.47)], c, 0, 16)
    tube(bm, ring(c + Vector((0, 0, 0.52)), 0.04, "Y", 12), 0.01, 0, sides=4, closed=True)
    links(bm, c + Vector((0, 0, 0.56)), O + Vector((0, 0, 1.0)), 2, w=0.05, r=0.012)
    return new_obj("ossuary_lantern", bm, [BRASS, SOUL, IRON])


def grind_wheel():
    """the engine's grinding wheel: a stone wheel on a brass axle between bone uprights, a crank, a trough below"""
    bm = bmesh.new()
    cyl(bm, O + Vector((-0.08, 0, 0.5)), 0.32, 0.16, 0, seg=24, axis="X")
    cyl(bm, O + Vector((-0.34, 0, 0.5)), 0.035, 0.68, 1, seg=10, axis="X")
    for x in (-0.24, 0.2):
        tube(bm, [O + Vector((x, -0.2, 0.0)), O + Vector((x, 0, 0.52)), O + Vector((x, 0.2, 0.0))], 0.035, 2, sides=6)
    tube(bm, [O + Vector((0.34, 0, 0.5)), O + Vector((0.38, 0.0, 0.5)), O + Vector((0.38, 0.0, 0.3)), O + Vector((0.44, 0.0, 0.3))], 0.02, 1, sides=5)
    box(bm, O + Vector((-0.3, -0.18, 0.0)), O + Vector((0.26, 0.18, 0.1)), 3, bevel=0.012)
    return new_obj("grind_wheel", bm, [STONE, BRASS, BONE, WOOD])


def bone_saw():
    """the bone saw bench: a heavy table, a toothed iron blade standing up through its slot, a femur half sawn"""
    bm = bmesh.new()
    box(bm, O + Vector((-0.44, -0.3, 0.46)), O + Vector((0.44, 0.3, 0.56)), 0, bevel=0.015)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(bm, O + Vector((sx * 0.38 - 0.045, sy * 0.24 - 0.045, 0)), O + Vector((sx * 0.38 + 0.045, sy * 0.24 + 0.045, 0.46)), 0, bevel=0.01)
    blade = cyl(bm, O + Vector((-0.012, 0, 0.5)), 0.26, 0.024, 1, seg=32, axis="X")
    rim = [v for v in blade if Vector((0, v.co.y - O.y, v.co.z - O.z - 0.5)).length > 0.2]
    for v in rim:   # the teeth: every other rim point pushed out
        r = Vector((0, v.co.y - O.y, v.co.z - O.z - 0.5))
        if int(round(math.atan2(r.z, r.y) / (2 * math.pi) * 32)) % 2:
            v.co += r.normalized() * 0.03
    cyl(bm, O + Vector((-0.03, 0, 0.5)), 0.05, 0.06, 2, seg=10, axis="X")
    tube(bm, [O + Vector((-0.1, 0.1, 0.6)), O + Vector((0.3, 0.16, 0.6))], 0.03, 3, sides=7)
    for e in (O + Vector((-0.1, 0.1, 0.6)), O + Vector((0.3, 0.16, 0.6))):
        ellipsoid(bm, e, (0.05, 0.045, 0.045), 3, seg=8)
    return new_obj("bone_saw", bm, [WOOD, IRON, BRASS, BONE])


MAKE = [(soul_lamp, (128, 128)), (skull_lamp, (128, 128)), (soul_flame, (128, 128)), (soul_pyre, (256, 256)), (ossuary_lantern, (128, 128)),
        (grind_wheel, (256, 256)), (bone_saw, (256, 256))]
run(MAKE, GLOWS, "ossuary_props")
