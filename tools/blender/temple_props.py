"""The Faceless Temple's props as real meshes (propkit.py does the baking and writing): mana crystals growing up from
the floor, down from the vault and out of the walls, heaps of the faceless dead's skulls, stalagmites.

  blender -b -P tools/blender/temple_props.py -- [preview] [fast] [names...]
    preview -> tools/renders/temple_props.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "propkit.py"), encoding="utf-8").read())

CRYSTAL = glass("mana_crystal_glass", (0.45, 0.35, 1.0), glow=3.5)
CORE = glass("mana_core", (0.75, 0.7, 1.0), glow=5.0)
ROCK = mottled("crystal_rock", [(0.0, (0.03, 0.03, 0.04)), (1.0, (0.1, 0.1, 0.12))], 8.0, 0.85)
BONE = mottled("temple_bone", [(0.0, (0.3, 0.27, 0.21)), (0.6, (0.52, 0.48, 0.38)), (1.0, (0.64, 0.6, 0.5))], 14.0, 0.6)
HOLE = mat("temple_hole", (0.01, 0.008, 0.008), 0.9)
GOLD = mat("temple_gilt", (0.45, 0.32, 0.08), 0.35, **{"Metallic": 0.9})
DRIP = mottled("drip_rock_prop", [(0.0, (0.12, 0.08, 0.05)), (0.6, (0.24, 0.17, 0.11)), (1.0, (0.34, 0.25, 0.16))], 12.0, 0.75)
GLOWS.update({CRYSTAL, CORE})
LIFT.update({"mana_crystal_hanging": 1.0})


def prism(bm, base, d, length, r, mi, sides=6, seed=0):
    """one crystal: a hexagonal prism from base along d, ending in a pointed facet"""
    d = d.normalized()
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 1e-3:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize()
    up = side.cross(d)
    rings = []
    for t, rr in ((0.0, r * 0.9), (0.72, r), (1.0, 0.0)):
        c = base + d * length * t
        if rr == 0:
            rings.append([bm.verts.new(c)])
            continue
        rings.append([bm.verts.new(c + (side * math.cos(a) + up * math.sin(a)) * rr)
                      for a in (k * 2 * math.pi / sides + seed for k in range(sides))])
    bm.faces.new(rings[0][::-1]).material_index = mi
    for k in range(sides):
        bm.faces.new((rings[0][k], rings[0][(k + 1) % sides], rings[1][(k + 1) % sides], rings[1][k])).material_index = mi
        bm.faces.new((rings[1][k], rings[1][(k + 1) % sides], rings[2][0])).material_index = mi


def cluster(bm, base, axis, spread, n, scale=1.0, seed=0):
    """crystals sprung from one bed: the tallest at the middle, the rest leaning out from it"""
    axis = axis.normalized()
    side = axis.cross(Vector((0, 0, 1)))
    if side.length < 1e-3:
        side = axis.cross(Vector((1, 0, 0)))
    side.normalize()
    up = side.cross(axis)
    vs = ellipsoid(bm, base, (0.3 * scale, 0.3 * scale, 0.3 * scale), 2, seg=12)
    for v in vs:   # the rock bed, flattened against the surface
        off = v.co - base
        h = off.dot(axis)
        v.co = base + (off - axis * h) + axis * max(0.0, h) * 0.35
    displace(vs, 0.03 * scale, 6.0, seed)
    for k in range(n):
        a = k * 2.4 + seed
        lean = 0.0 if k == 0 else 0.35 + 0.1 * (k % 3)
        d = axis + (side * math.cos(a) + up * math.sin(a)) * lean
        off = (side * math.cos(a) + up * math.sin(a)) * (0.0 if k == 0 else spread * (0.4 + 0.2 * (k % 2)))
        L = (0.75 if k == 0 else 0.35 + 0.08 * (k % 3)) * scale
        prism(bm, base + off, d, L, (0.1 if k == 0 else 0.06) * scale, 0 if k % 3 else 1, seed=k * 0.4)


def mana_crystal():
    bm = bmesh.new()
    cluster(bm, O + Vector((0, 0, 0.02)), Vector((0, 0, 1)), 0.22, 7)
    return new_obj("mana_crystal", bm, [CRYSTAL, CORE, ROCK])


def mana_crystal_hanging():
    bm = bmesh.new()
    cluster(bm, O + Vector((0, 0, 0.98)), Vector((0, 0, -1)), 0.22, 7, seed=2)
    return new_obj("mana_crystal_hanging", bm, [CRYSTAL, CORE, ROCK])


def mana_crystal_wall():
    """crystals grown out of the wall at the back of the block, reaching into the room"""
    bm = bmesh.new()
    cluster(bm, Vector((0.5, -0.98, 0.45)), Vector((0, 1, 0.25)), 0.2, 6, 0.9, seed=4)
    return new_obj("mana_crystal_wall", bm, [CRYSTAL, CORE, ROCK])


def skull(bm, c, s, a, tilt, mi_bone, mi_hole):
    rot = Matrix.Rotation(a, 3, "Z") @ Matrix.Rotation(tilt, 3, "X")
    vs = ellipsoid(bm, c + rot @ Vector((0, 0, 0.07 * s)), (0.09 * s, 0.11 * s, 0.085 * s), mi_bone, seg=12)
    displace(vs, 0.005 * s, 8.0, int(a * 10) + 5)
    ellipsoid(bm, c + rot @ Vector((0, 0.07 * s, 0.025 * s)), (0.065 * s, 0.05 * s, 0.035 * s), mi_bone, seg=8)
    for sx in (-1, 1):
        ellipsoid(bm, c + rot @ Vector((sx * 0.035 * s, 0.09 * s, 0.075 * s)), (0.026 * s, 0.02 * s, 0.026 * s), mi_hole, seg=6)


def skull_pile():
    """a heap of the temple's faceless dead filling the block: skulls packed in tiers, most staring out at the front,
    a gilded mask fallen among them"""
    bm = bmesh.new()
    vs = ellipsoid(bm, O + Vector((0, -0.08, 0.0)), (0.48, 0.44, 0.62), 1, seg=14)
    for v in vs:
        if v.co.z < 0:
            v.co.z = 0.0
    k = 0
    for tier, (z, r, n) in enumerate([(0.02, 0.36, 9), (0.22, 0.3, 7), (0.42, 0.2, 5), (0.6, 0.04, 1)]):
        for j in range(n):
            a = j * 2 * math.pi / n + tier * 0.4
            c = O + Vector((math.cos(a) * r, math.sin(a) * r * 0.9 - 0.04, z))
            face = math.atan2(math.sin(a), math.cos(a)) - math.pi / 2 if r > 0.1 else 0.0
            skull(bm, c, 1.5, face, 0.15 * ((k % 3) - 1), 0, 2)
            k += 1
    vs = ellipsoid(bm, O + Vector((0.18, 0.3, 0.12)), (0.1, 0.03, 0.13), 3, rot=Matrix.Rotation(0.5, 3, "Z"), seg=10)
    return new_obj("skull_pile", bm, [BONE, ROCK, HOLE, GOLD])


def stalagmite():
    """a stalagmite: drip rock rising to a point in rings, a smaller one leaning on it"""
    bm = bmesh.new()
    prof = [(0.0, 0.0)] + [(0.3 * (1 - t) ** 1.4 + 0.02 * math.sin(t * 20), t * 0.95) for t in (k / 10 for k in range(11))]
    rings = lathe(bm, prof, O + Vector((0.04, 0.0, 0)), 0, 14)
    displace([v for rg in rings for v in rg], 0.015, 8.0, 2)
    prof = [(0.0, 0.0)] + [(0.14 * (1 - t) ** 1.3, t * 0.45) for t in (k / 6 for k in range(7))]
    lathe(bm, prof, O + Vector((-0.24, 0.16, 0)), 0, 10)
    return new_obj("stalagmite", bm, [DRIP])


MAKE = [(mana_crystal, (128, 128)), (mana_crystal_hanging, (128, 128)), (mana_crystal_wall, (128, 128)), (skull_pile, (256, 256)),
        (stalagmite, (128, 128))]
run(MAKE, GLOWS, "temple_props")
