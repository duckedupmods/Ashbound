"""The king of the gorge, sculpted as a mesh in Blender and turned into blocks.

    blender -b -P tools/blender/king_sculpt.py -- [render]

Builds the figure out of real 3D parts (a lathed robe with its folds, an armoured cuirass with lames, stacked
pauldrons, a face with brow, nose, cheekbones and sunk eyes, a beard of separate strands and braids, fingers, a
greatsword with its fuller), then samples it on the block grid: each block that the mesh fills takes the part of the
highest-priority piece there and a shade baked from ambient occlusion (rays cast round its surface normal) and the
sky light; slabs go on top where the surface crosses a block's lower half. Writes
tools/renders/king_cells.json for capital_kings.py; with "render", also renders the smooth sculpt to
E:/Ashbound/tools/renders/struct/king_sculpt_*.png.

Units are blocks: his soles at y 0 (Blender z), facing +z in the game (Blender -y), the raised hand on +x.
"""
import json
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "renders", "king_cells.json")
RENDERS = "E:/Ashbound/tools/renders/struct"
random.seed(7)

PRIO = {"gilt": 9, "hair": 8, "skin": 7, "blade": 6, "armour": 5, "robe": 4, "cloak": 3}
PARTS = []          # (object, part)
CUTS = []           # objects that carve away what's under them (eye sockets, the fuller)


def G(x, y, z):
    """Game coords (x east, y up, z toward the viewer) -> Blender (x, -z, y)."""
    return Vector((x, -z, y))


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mesh_obj(name, verts, faces, part):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.validate()
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    if part == "cut":
        CUTS.append(ob)
    else:
        PARTS.append((ob, part))
    return ob


def lathe(name, ys, ring, part, n=96):
    """A closed shell from rings: ring(y, theta) -> (x, z) in game coords, one ring per y in ys (bottom to top)."""
    verts, faces = [], []
    for y in ys:
        for i in range(n):
            t = 2 * math.pi * i / n
            x, z = ring(y, t)
            verts.append(G(x, y, z))
    m = len(ys)
    for j in range(m - 1):
        for i in range(n):
            a, b = j * n + i, j * n + (i + 1) % n
            faces.append((a, b, b + n, a + n))
    # caps
    cb = len(verts)
    verts.append(sum((verts[i] for i in range(n)), Vector()) / n)
    ct = len(verts)
    verts.append(sum((verts[(m - 1) * n + i] for i in range(n)), Vector()) / n)
    for i in range(n):
        faces.append((cb, (i + 1) % n, i))
        faces.append((ct, (m - 1) * n + i, (m - 1) * n + (i + 1) % n))
    return mesh_obj(name, verts, faces, part)


def ellipsoid(name, c, r, part, rot=(0, 0, 0), seg=40):
    """An ellipsoid at game coords c, radii r (game x, y, z), rotated by rot (degrees about game x, y, z)."""
    verts, faces = [], []
    rings = seg // 2
    for j in range(rings + 1):
        ph = math.pi * j / rings - math.pi / 2
        for i in range(seg):
            th = 2 * math.pi * i / seg
            verts.append(Vector((r[0] * math.cos(ph) * math.cos(th), r[1] * math.sin(ph), r[2] * math.cos(ph) * math.sin(th))))
    for j in range(rings):
        for i in range(seg):
            a, b = j * seg + i, j * seg + (i + 1) % seg
            faces.append((a, b, b + seg, a + seg))
    R = (Matrix.Rotation(math.radians(rot[2]), 3, "Z") @ Matrix.Rotation(math.radians(rot[1]), 3, "Y")
         @ Matrix.Rotation(math.radians(rot[0]), 3, "X"))
    verts = [G(*(R @ v + Vector(c))) for v in verts]
    return mesh_obj(name, verts, faces, part)


def capsule(name, a, b, ra, rb, part, seg=24, rings=8):
    """A capsule (rounded cone) from game point a (radius ra) to b (radius rb)."""
    A, B = Vector(a), Vector(b)
    ax = (B - A)
    L = ax.length
    ax.normalize()
    up = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
    u = ax.cross(up).normalized()
    v = ax.cross(u).normalized()
    prof = []
    for j in range(rings + 1):                       # the cap at a
        ph = math.pi / 2 * (1 - j / rings)
        prof.append((-ra * math.sin(ph), ra * math.cos(ph)))
    for j in range(rings + 1):                       # the cap at b
        ph = math.pi / 2 * j / rings
        prof.append((L + rb * math.sin(ph), rb * math.cos(ph)))
    verts, faces = [], []
    for t, rr in prof:
        for i in range(seg):
            th = 2 * math.pi * i / seg
            p = A + ax * t + (u * math.cos(th) + v * math.sin(th)) * rr
            verts.append(G(*p))
    m = len(prof)
    for j in range(m - 1):
        for i in range(seg):
            a_, b_ = j * seg + i, j * seg + (i + 1) % seg
            faces.append((a_, b_, b_ + seg, a_ + seg))
    return mesh_obj(name, verts, faces, part)


def tube(name, pts, radii, part, seg=16):
    """A tube through game points pts with a radius at each (ends capped with a dome)."""
    obs = []
    for i in range(len(pts) - 1):
        obs.append(capsule("%s_%d" % (name, i), pts[i], pts[i + 1], radii[i], radii[i + 1], part, seg=seg, rings=4))
    return obs


def rbox(name, c, h, part, bevel=0.6, rot=(0, 0, 0)):
    """A rounded box at game c with half-sizes h."""
    bpy.ops.mesh.primitive_cube_add(size=2)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (h[0], h[2], h[1])
    bpy.ops.object.transform_apply(scale=True)
    md = ob.modifiers.new("b", "BEVEL")
    md.width = bevel
    md.segments = 3
    bpy.ops.object.modifier_apply(modifier="b")
    ob.rotation_euler = (math.radians(rot[0]), math.radians(-rot[2]), math.radians(rot[1]))
    ob.location = G(*c)
    bpy.ops.object.transform_apply(location=True, rotation=True)
    for p in ob.data.polygons:
        p.use_smooth = True
    if part == "cut":
        CUTS.append(ob)
    else:
        PARTS.append((ob, part))
    return ob


# ================================================================ the figure

def smooth(e0, e1, v):
    t = max(0.0, min(1.0, (v - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def build():
    # ---- the robe: hem on the ground, flaring, deep pleats that soften toward the waist
    def robe(y, t):
        r = 10.4 + 5.2 * (1 - smooth(0, 46, y)) ** 1.3
        fold = (0.9 + 1.5 * (1 - smooth(4, 44, y))) * math.sin(13 * t + 0.6 * math.sin(3 * t)) * (1 - 0.35 * max(0, math.sin(t)))
        rz = 0.86
        rr = r + fold
        x, z = rr * math.cos(t), rr * math.sin(t) * rz
        return x, z
    lathe("robe", [0.0, 0.8, 1.6] + [2 + i * 2 for i in range(23)] + [47.5], robe, "robe", n=128)
    # the hem's heavy border
    lathe("hem", [0.0, 1.0, 2.4], lambda y, t: tuple(v * 1.035 for v in robe(y, t)), "armour", n=128)
    # the tabard down the front, a raised panel with a gilt edge
    rbox("tabard", (0, 25, 11.0), (4.2, 21, 1.4), "robe", bevel=0.8)
    for sx in (-1, 1):
        rbox("tab_edge", (sx * 4.3, 25, 11.4), (0.7, 21, 1.2), "armour", bevel=0.3)
    # armoured feet out under the hem
    for sx in (-1, 1):
        ellipsoid("foot", (sx * 5.4, 1.6, 10.5), (3.0, 2.0, 5.0), "armour")
        ellipsoid("toe", (sx * 5.4, 1.4, 14.0), (2.4, 1.5, 2.2), "armour")

    # ---- the cuirass: waist to shoulders, a ridge down the breastplate, lames over the belly
    def cuirass(y, t):
        rx = 10.2 + 2.8 * smooth(46, 60, y) - 5.6 * smooth(66, 77, y)
        rz = 7.4 + 1.9 * smooth(48, 61, y) - 3.8 * smooth(65, 77, y)
        c, s_ = math.cos(t), math.sin(t)
        x, z = rx * c, rz * s_
        if s_ > 0:                                               # the front
            z += 0.9 * math.exp(-(x / 2.2) ** 2) * smooth(52, 60, y) * s_     # the ridge
            if y < 57:
                band = (y - 46) % 3.4
                z += 0.7 * smooth(2.2, 3.3, band) * s_            # each lame's lower edge stands proud
        return x, z
    lathe("cuirass", [45 + i * 0.85 for i in range(38)], cuirass, "armour", n=112)
    # the belt and its buckle
    lathe("belt", [48.6, 49.4, 50.2, 51.0], lambda y, t: (11.0 * math.cos(t), 8.3 * math.sin(t)), "gilt", n=96)
    rbox("buckle", (0, 49.8, 8.6), (2.0, 1.6, 0.8), "gilt", bevel=0.4)
    # the city's sign raised on the breastplate: a gilt sunburst, and clasps holding the cloak at the shoulders
    ellipsoid("emblem", (0, 62.5, 9.9), (2.4, 2.4, 0.9), "gilt")
    for k in range(8):
        a = k * math.pi / 4
        capsule("ray%d" % k, (1.8 * math.cos(a), 62.5 + 1.8 * math.sin(a), 9.8),
                (4.2 * math.cos(a), 62.5 + 4.2 * math.sin(a), 9.2), 0.75, 0.45, "gilt", seg=10, rings=3)
    for sx in (-1, 1):
        ellipsoid("clasp", (sx * 9.5, 70.5, 5.6), (1.9, 1.9, 1.1), "gilt")
    # the gorget round the neck
    lathe("gorget", [71.0, 72.5, 74.0, 75.0], lambda y, t: ((7.2 - (y - 71) * 0.7) * math.cos(t), (6.0 - (y - 71) * 0.6) * math.sin(t)), "armour")

    # ---- pauldrons: three stacked plates each side, a gilt rim on the lowest
    for sx in (-1, 1):
        for i in range(3):
            ellipsoid("paul%d" % i, (sx * (13.6 + i * 1.5), 72.0 - i * 2.9, 0.0), (6.6 - i * 0.3, 3.0, 7.6 - i * 0.4), "armour",
                      rot=(0, 0, sx * (24 + i * 9)))
        ellipsoid("paulboss", (sx * 15.0, 74.6, 0.0), (2.0, 1.4, 2.0), "gilt")

    # ---- the cloak: from behind the shoulders down to the ground, pleated, flaring out on the raised arm's side
    def cloak(y, t):
        # t runs round the back half only (mapped below)
        a = math.pi * (1.05 + 0.9 * (t / (2 * math.pi)))           # 189 to 351 degrees: behind him
        r = 14.0 + 7.5 * (1 - smooth(0, 70, y)) ** 1.2
        r += 1.4 * math.sin(9 * a) * (1 - smooth(10, 68, y)) + 0.6 * math.sin(23 * a)
        x, z = r * math.cos(a), r * math.sin(a) * 0.82
        x += 4.5 * (1 - smooth(0, 70, y)) * max(0.0, math.cos(a))   # the flare
        return x, z - 1.0
    ys = [0.0] + [1.5 + i * 3 for i in range(23)] + [70.0, 72.0]
    n = 96
    verts, faces = [], []
    for j, y in enumerate(ys):
        for i in range(n):
            x, z = cloak(y, 2 * math.pi * i / (n - 1))
            verts.append((x, y, z))
    # solidify by hand: an inner surface 1.6 in toward the body
    inner = []
    for (x, y, z) in verts:
        l = math.hypot(x, z) or 1
        inner.append((x - x / l * 1.6, y, z - z / l * 1.6))
    allv = [G(*v) for v in verts] + [G(*v) for v in inner]
    m, off = len(ys), len(verts)
    for j in range(m - 1):
        for i in range(n - 1):
            a, b = j * n + i, j * n + i + 1
            faces.append((a, b, b + n, a + n))
            faces.append((off + a, off + a + n, off + b + n, off + b))
    for j in range(m - 1):                                         # the side edges
        for i in (0, n - 1):
            a, b = j * n + i, (j + 1) * n + i
            faces.append((a, b, off + b, off + a) if i == 0 else (a, off + a, off + b, b))
    for i in range(n - 1):                                         # bottom and top edges
        a, b = i, i + 1
        faces.append((a, off + a, off + b, b))
        a, b = (m - 1) * n + i, (m - 1) * n + i + 1
        faces.append((a, b, off + b, off + a))
    mesh_obj("cloak", allv, faces, "cloak")

    # ---- the head
    HY = 82.0
    ellipsoid("cranium", (0, HY + 1.5, 0.3), (5.7, 6.8, 6.3), "skin")
    ellipsoid("jaw", (0, HY - 2.4, 1.9), (5.1, 4.0, 4.7), "skin")
    capsule("brow", (-4.2, HY + 1.9, 5.3), (4.2, HY + 1.9, 5.3), 1.25, 1.25, "skin")
    capsule("brow_mid", (0, HY + 1.6, 6.0), (0, HY + 2.6, 5.6), 1.2, 1.0, "skin")
    capsule("nose", (0, HY + 1.2, 6.6), (0, HY - 2.0, 8.0), 1.0, 1.45, "skin")
    for sx in (-1, 1):
        ellipsoid("nostril", (sx * 1.1, HY - 2.0, 7.2), (1.0, 0.8, 0.9), "skin")
        ellipsoid("cheek", (sx * 3.7, HY - 0.8, 4.9), (1.8, 1.5, 1.6), "skin")
        ellipsoid("ear", (sx * 5.7, HY, 0.6), (0.9, 2.2, 1.4), "skin")
        ellipsoid("eye", (sx * 2.2, HY + 0.4, 6.7), (1.35, 0.95, 1.3), "cut")      # sunk sockets
        ellipsoid("lid", (sx * 2.2, HY + 0.2, 5.6), (1.2, 0.8, 0.8), "skin")       # the eyeball back in the socket
    # moustache sweeping out and down
    for sx in (-1, 1):
        tube("moust", [(sx * 0.4, HY - 3.0, 7.6), (sx * 2.2, HY - 3.4, 7.2), (sx * 3.6, HY - 4.6, 6.4), (sx * 4.2, HY - 6.6, 5.6)],
             [1.0, 1.05, 0.9, 0.6], "hair")
    # the beard: a full mass from the jaw to mid-chest, strands over it, two braids at its tip with gold beads
    def beard(y, t):
        k = (HY - 4 - y) / 15.0                                     # 0 at the chin, 1 at the tip
        w = 5.6 * (1 - 0.45 * k ** 1.4)
        d = 3.4 + 2.6 * math.sin(min(1.0, k) * 2.2)
        c, s_ = math.cos(t), math.sin(t)
        return w * c, (d if s_ > 0 else 2.2) * s_ + 4.2 + 1.4 * k
    lathe("beard", [HY - 19.5 + i * 0.75 for i in range(21)], beard, "hair", n=64)
    for i in range(9):
        fx = -4.4 + i * 1.1
        pts, rad = [], []
        for j in range(7):
            k = j / 6.0
            y = HY - 3.5 - k * 15.0
            w = 1 - 0.45 * k ** 1.4
            x = fx * w + 0.5 * math.sin(k * 4 + i)
            zf = 4.2 + 1.4 * k + (3.4 + 2.6 * math.sin(k * 2.2)) * math.sqrt(max(0.0, 1 - (x / (5.6 * w)) ** 2)) + 0.35
            pts.append((x, y, zf))
            rad.append(0.95 - 0.3 * k)
        tube("strand%d" % i, pts, rad, "hair", seg=12)
    pts = [(0, HY - 17.0, 9.0), (0.3, HY - 20.5, 8.9), (0.1, HY - 24.0, 8.7), (-0.2, HY - 27.0, 8.6)]
    for j in range(len(pts) - 1):
        for q in range(3):                                          # braided: bumps down it
            a = Vector(pts[j]).lerp(Vector(pts[j + 1]), q / 3.0)
            ellipsoid("braid", tuple(a), (2.0 - 0.15 * j, 1.1, 1.6), "hair")
    ellipsoid("bead", (-0.2, HY - 28.6, 8.6), (1.6, 1.3, 1.5), "gilt")
    ellipsoid("beadring", (0.2, HY - 17.6, 9.1), (2.3, 0.9, 1.8), "gilt")
    # the hair down his back and over the shoulders, in thick locks
    def hair(y, t):
        k = (HY + 6 - y) / 18.0
        c, s_ = math.cos(t), math.sin(t)
        r = 6.2 + 1.8 * k
        z = (r * s_ if s_ < 0 else 0.6 * s_) - 1.2
        return r * c * (1.0 if s_ < 0 else 0.97) + 0.5 * math.sin(7 * t), z + 0.6 * math.sin(11 * t) * k
    lathe("hair", [HY + 7 - i * 1.2 for i in range(16)][::-1], hair, "hair", n=72)

    # ---- the crown: a band round the brow, seven points with ball tips, gems on the band
    CY = HY + 5.6
    def band(y, t):
        return 6.5 * math.cos(t), 6.9 * math.sin(t) + 0.4
    lathe("crown", [CY - 1.4, CY, CY + 1.4], band, "gilt", n=72)
    for i in range(7):
        a = math.pi / 2 + (i - 3) * 0.62                           # round the front and sides
        bx, bz = 6.6 * math.cos(a), 7.0 * math.sin(a) + 0.4
        tip = 5.6 if i == 3 else 4.2 if i in (2, 4) else 3.4
        capsule("pt%d" % i, (bx, CY + 1.0, bz), (bx * 1.06, CY + 1.0 + tip, bz * 1.06), 1.15, 0.45, "gilt", seg=12, rings=3)
        ellipsoid("ball%d" % i, (bx * 1.07, CY + 1.4 + tip, bz * 1.07), (0.9, 0.9, 0.9), "gilt")
    capsule("crown_arch", (0, CY + 1, 6.8), (0, CY + 4.5, -2.0), 0.8, 0.8, "gilt")

    # ---- the raised arm (+x): pauldron to elbow, vambrace up to the wrist, the hand open, palm out
    SH, EL, WR = (13.6, 69.0, 0.0), (21.0, 74.0, 7.0), (21.6, 85.5, 12.0)
    capsule("uparm_r", SH, EL, 4.4, 3.8, "armour")
    ellipsoid("elbow_r", EL, (3.9, 3.7, 3.9), "armour")
    ellipsoid("elbowfan_r", (EL[0] + 1.2, EL[1] - 0.6, EL[2] - 1.6), (2.6, 2.2, 1.2), "gilt")
    capsule("vamb_r", EL, WR, 3.6, 3.0, "armour")
    for q in (0.35, 0.7):
        p = Vector(EL).lerp(Vector(WR), q)
        lathe("vband", [p.y - 0.5, p.y + 0.5], (lambda px, pz: (lambda y, t: (px + 3.5 * math.cos(t), pz + 3.6 * math.sin(t))))(p.x, p.z), "gilt", n=40)
    capsule("cuff_r", (21.6, 84.0, 12.0), (21.8, 88.0, 13.0), 3.2, 3.6, "armour")
    # the hand: palm toward the viewer, fingers up and a little spread, thumb out to the side
    PC = (21.8, 91.4, 14.2)
    rbox("palm", PC, (3.6, 3.4, 1.5), "skin", bevel=1.0)
    for i, (fx, ln, sp) in enumerate(((-2.7, 5.6, -0.7), (-0.9, 6.6, -0.2), (0.9, 6.3, 0.25), (2.7, 5.0, 0.8))):
        k0 = (PC[0] + fx, PC[1] + 3.0, PC[2] + 0.2)
        k1 = (k0[0] + sp * 0.6, k0[1] + ln * 0.55, k0[2] + 0.3)
        k2 = (k0[0] + sp * 1.1, k0[1] + ln, k0[2] + 0.1)
        tube("finger%d" % i, [k0, k1, k2], [1.05, 0.95, 0.8], "skin", seg=12)
    tube("thumb", [(PC[0] - 3.0, PC[1] - 1.5, PC[2] + 0.6), (PC[0] - 5.0, PC[1] + 0.5, PC[2] + 1.6), (PC[0] - 6.0, PC[1] + 2.6, PC[2] + 1.8)],
         [1.25, 1.05, 0.85], "skin", seg=12)

    # ---- the sword arm (-x): down and forward to the hand on the pommel
    SH2, EL2, WR2 = (-13.6, 69.0, 0.0), (-17.0, 57.5, 5.5), (-6.5, 53.0, 13.5)
    capsule("uparm_l", SH2, EL2, 4.4, 3.8, "armour")
    ellipsoid("elbow_l", EL2, (3.9, 3.7, 3.9), "armour")
    capsule("vamb_l", EL2, WR2, 3.6, 3.0, "armour")
    capsule("cuff_l", (-6.5, 53.0, 13.5), (-4.0, 53.0, 14.6), 3.2, 3.4, "armour")
    # the gauntleted fist over the pommel, knuckles forward
    rbox("fist", (-1.2, 53.6, 15.6), (3.0, 2.6, 2.6), "armour", bevel=1.1)
    for i in range(4):
        capsule("knuckle%d" % i, (-3.2 + i * 1.4, 54.6, 18.0), (-3.2 + i * 1.4, 52.0, 18.2), 0.75, 0.7, "armour", seg=10, rings=3)

    # ---- the greatsword, point down before his feet
    BZ = 16.0
    verts, faces = [], []
    for y, hw, ht in ((0.4, 0.2, 0.3), (3.0, 2.3, 0.8), (6.0, 2.7, 0.85), (42.6, 2.6, 0.85)):
        for (x, z) in ((-hw, 0), (0, ht), (hw, 0), (0, -ht)):       # a diamond section
            verts.append(G(x, y, BZ + z))
    for j in range(3):
        for i in range(4):
            a, b = j * 4 + i, j * 4 + (i + 1) % 4
            faces.append((a, b, b + 4, a + 4))
    faces.append((0, 3, 2, 1))
    faces.append((12, 13, 14, 15))
    mesh_obj("blade", verts, faces, "blade")
    rbox("fuller", (0, 25, BZ + 0.9), (0.55, 16, 0.45), "cut", bevel=0.2)
    capsule("guard", (-8.8, 43.6, BZ), (8.8, 43.6, BZ), 1.3, 1.3, "gilt")
    for sx in (-1, 1):
        ellipsoid("quillon", (sx * 9.4, 42.4, BZ), (1.5, 1.9, 1.5), "gilt")
    ellipsoid("guardgem", (0, 43.6, BZ + 1.2), (1.4, 1.4, 0.7), "gilt")
    capsule("grip", (0, 44.6, BZ), (0, 50.6, BZ), 1.35, 1.35, "armour")
    ellipsoid("pommel", (0, 51.6, BZ), (2.1, 1.8, 2.1), "gilt")


# ================================================================ into blocks

def evaluated(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    e = ob.evaluated_get(dg)
    me = e.to_mesh()
    verts = [e.matrix_world @ v.co for v in me.vertices]
    polys = [tuple(p.vertices) for p in me.polygons]
    e.to_mesh_clear()
    return verts, polys


def bvh_of(ob):
    v, p = evaluated(ob)
    lo = Vector((min(a.x for a in v), min(a.y for a in v), min(a.z for a in v)))
    hi = Vector((max(a.x for a in v), max(a.y for a in v), max(a.z for a in v)))
    return BVHTree.FromPolygons(v, p), lo, hi, v, p


def signed(t, p):
    hit = t.find_nearest(p)
    if hit[0] is None:
        return 99.0
    loc, nrm, _, dist = hit
    return -dist if (p - loc).dot(nrm) < 0 else dist


FLOOD = False                   # fill by flood from outside (for hollow generated meshes), not by the normals


def voxelize(out=OUT, prio=None, uncut=("gilt", "hair")):
    """Each piece fills the cells inside it (within 0.3, so thin parts survive), the highest-priority part winning;
    then the cuts carve (except through the `uncut` parts). Loops over each piece's own box, so a figure with
    hundreds of feathers costs what its pieces' volume costs."""
    prio = prio or PRIO
    pieces = []
    allv, allp = [], []
    for ob, part in PARTS:
        t, lo, hi, v, p = bvh_of(ob)
        pieces.append((t, lo, hi, part))
        o = len(allv)
        allv += v
        allp += [tuple(i + o for i in f) for f in p]
    whole = BVHTree.FromPolygons(allv, allp)

    def span(lo, hi):                               # the game cells a Blender box touches
        return (range(math.floor(lo.x - 0.5), math.ceil(hi.x + 0.5)),
                range(max(0, math.floor(lo.z - 0.5)), math.ceil(hi.z + 0.5)),
                range(math.floor(-hi.y - 0.5), math.ceil(-lo.y + 0.5)))
    cells = {}
    for t, lo, hi, part in pieces:
        xs, ys, zs = span(lo, hi)
        for gx in xs:
            for gy in ys:
                for gz in zs:
                    c = (gx, gy, gz)
                    have = cells.get(c)
                    if have is not None and prio[have] >= prio[part]:
                        continue
                    d = signed(t, G(gx + 0.5, gy + 0.5, gz + 0.5))
                    if d < 0.3 or FLOOD and abs(d) < 0.62:
                        cells[c] = part
    if FLOOD:
        # a hollow or inside-out mesh: the skin's cells above, then whatever the outside can't reach is inside too
        xs = [c[0] for c in cells]; ys = [c[1] for c in cells]; zs = [c[2] for c in cells]
        lo, hi = (min(xs) - 1, min(ys) - 1, min(zs) - 1), (max(xs) + 1, max(ys) + 1, max(zs) + 1)
        out_ = {lo}
        stack = [lo]
        while stack:
            x, y, z = stack.pop()
            for a, b, d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                n = (x + a, y + b, z + d)
                if (lo[0] <= n[0] <= hi[0] and lo[1] <= n[1] <= hi[1] and lo[2] <= n[2] <= hi[2]
                        and n not in out_ and n not in cells):
                    out_.add(n)
                    stack.append(n)
        part0 = pieces[0][3]
        for x in range(lo[0], hi[0] + 1):
            for y in range(max(0, lo[1]), hi[1] + 1):
                for z in range(lo[2], hi[2] + 1):
                    if (x, y, z) not in out_ and (x, y, z) not in cells:
                        cells[(x, y, z)] = part0
    for ob in CUTS:
        t, lo, hi = bvh_of(ob)[:3]
        xs, ys, zs = span(lo, hi)
        for gx in xs:
            for gy in ys:
                for gz in zs:
                    c = (gx, gy, gz)
                    if c in cells and cells[c] not in uncut and signed(t, G(gx + 0.5, gy + 0.5, gz + 0.5)) < 0:
                        del cells[c]
    print("filled", len(cells))
    # keep a shell: blocks within two of an empty one
    def empty(c):
        return c not in cells
    N6 = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    surf = {c for c in cells if any(empty((c[0] + a, c[1] + b, c[2] + d)) for a, b, d in N6)}
    ring2 = {(c[0] + a, c[1] + b, c[2] + d) for c in surf for a, b, d in N6} & set(cells)
    keep = surf | ring2
    # shade the surface: ambient occlusion from rays round the normal, plus light from the sky and the front
    dirs = []                                       # a fixed, evenly spread cosine-weighted set (no speckle)
    NR = 64
    for i in range(NR):
        u, v = (i * 0.618034) % 1.0, (i + 0.5) / NR
        th, r = 2 * math.pi * u, math.sqrt(v)
        dirs.append((r * math.cos(th), r * math.sin(th), math.sqrt(1 - v)))
    out_path, out = out, []
    for c in keep:
        part = cells[c]
        shade, ny = 0.5, 0.0
        if c in surf:
            p = G(c[0] + 0.5, c[1] + 0.5, c[2] + 0.5)
            loc, nrm, _, _ = whole.find_nearest(p)
            n = nrm.normalized()
            if (p - loc).dot(n) < -0.6:
                pass
            t1 = n.orthogonal().normalized()
            t2 = n.cross(t1)
            occ = 0.0
            start = loc + n * 0.35
            for a, b, w in dirs:
                d = (t1 * a + t2 * b + n * w).normalized()
                h = whole.ray_cast(start, d, 16.0)
                if h[0] is not None:
                    occ += 1.0 - h[3] / 16.0
            ao = 1.0 - occ / len(dirs)
            ny = n.z                                   # Blender z is up
            front = -n.y                               # toward the viewer (game +z)
            shade = max(0.0, min(1.0, ao * (0.62 + 0.24 * ny + 0.14 * front)))
        top = (c[0], c[1] + 1, c[2]) not in cells
        slab = False
        if top and c in surf:
            q = G(c[0] + 0.5, c[1] + 1.25, c[2] + 0.5)
            for t, lo, hi, prt in pieces:
                if prt == part and lo.x <= q.x <= hi.x and lo.y <= q.y <= hi.y and lo.z <= q.z <= hi.z and signed(t, q) < 0:
                    slab = True
                    break
        out.append([c[0], c[1], c[2], part, round(shade, 3), round(ny, 2), 1 if slab else 0])
    print("kept", len(out))
    with open(out_path, "w") as f:
        json.dump({"cells": out}, f)
    print("wrote", out_path)


# ================================================================ a look at the sculpt itself

def render_sculpt():
    sc = bpy.context.scene
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            pass
    sc.render.resolution_x, sc.render.resolution_y = 900, 1200
    cols = {"skin": (0.86, 0.84, 0.8), "hair": (0.78, 0.77, 0.74), "robe": (0.7, 0.69, 0.66), "armour": (0.42, 0.43, 0.45),
            "cloak": (0.3, 0.3, 0.32), "blade": (0.8, 0.82, 0.85), "gilt": (0.85, 0.66, 0.25)}
    mats = {}
    for k, c in cols.items():
        m = bpy.data.materials.new(k)
        m.use_nodes = True
        m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*c, 1)
        m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
        mats[k] = m
    for ob, part in PARTS:
        ob.data.materials.append(mats[part])
    for ob in CUTS:
        ob.hide_render = True
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.45, 0.5, 0.58, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.5
    sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
    sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    os.makedirs(RENDERS, exist_ok=True)
    for name, eye, look, lens in (("front", (6, 55, 120), (0, 52, 0), 40), ("face", (8, 86, 34), (2, 84, 0), 45),
                                  ("three", (60, 60, 95), (2, 52, 0), 40), ("hand", (36, 92, 40), (21, 90, 13), 50)):
        cam.location = G(*eye)
        d = G(*look) - G(*eye)
        cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lens
        sc.render.filepath = os.path.join(RENDERS, "king_sculpt_%s.png" % name)
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    reset()
    build()
    if "render" in args:
        render_sculpt()
    if "novox" not in args:
        voxelize()
