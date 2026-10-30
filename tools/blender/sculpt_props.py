"""Highmourn's sculpted props: modelled as real meshes in Blender (bevelled boxes, lathed bowls and tanks, tori,
chains, crystals), then sampled on a fine grid (V voxels per block, 16 = one per pixel) with the material of the
last part that fills each voxel. tools/sculpt.py turns the samples into block models.

    blender -b -P tools/blender/sculpt_props.py -- [NAME ...]        (none = all)

Units are blocks, in game axes: x east, y up, z south. Every prop faces north (-z, its front at z = 0), stands on
y = 0 and fills x 0..w, z 0..d. Writes tools/renders/sculpt/NAME.json.
"""
import json
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import king_sculpt as KS  # noqa: E402
from king_sculpt import G  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "renders", "sculpt")
PROPS = {}                      # name -> (w, h, d, V, builder)


def prop(name, w, h, d, V=16):
    def reg(fn):
        PROPS[name] = (w, h, d, V, fn)
        return fn
    return reg


# ================================================================ shapes (game coords, blocks)

def box(x0, y0, z0, x1, y1, z1, mat, bevel=0.025, rot=(0, 0, 0)):
    c = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    h = ((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2)
    bevel = min(bevel, min(h) * 0.8)
    return KS.rbox("b", c, h, mat, bevel=max(bevel, 0.001), rot=rot)


def _frame(a, b):
    A, B = Vector(a), Vector(b)
    ax = B - A
    L = ax.length
    ax.normalize()
    up = Vector((0, 1, 0)) if abs(ax.y) < 0.9 else Vector((1, 0, 0))
    u = ax.cross(up).normalized()
    v = ax.cross(u).normalized()
    return A, ax, L, u, v


def cyl(a, b, r, mat, r2=None, seg=28):
    """A flat-capped cylinder (or frustum, radius r at a and r2 at b) between game points."""
    r2 = r if r2 is None else r2
    A, ax, L, u, v = _frame(a, b)
    verts, faces = [], []
    for t, rr in ((0, r), (L, r2)):
        for i in range(seg):
            th = 2 * math.pi * i / seg
            verts.append(G(*(A + ax * t + (u * math.cos(th) + v * math.sin(th)) * rr)))
    for i in range(seg):
        j = (i + 1) % seg
        faces.append((i, j, j + seg, i + seg))
    faces.append(tuple(range(seg))[::-1])
    faces.append(tuple(range(seg, 2 * seg)))
    return KS.mesh_obj("c", verts, faces, mat)


def lathe(c, prof, mat, seg=32, axis=None):
    """A solid of revolution about a vertical axis through game point c: prof = [(y, r), ...] bottom to top
    (relative y). Closed at both ends."""
    verts, faces = [], []
    for y, r in prof:
        for i in range(seg):
            th = 2 * math.pi * i / seg
            p = Vector((c[0] + r * math.cos(th), c[1] + y, c[2] + r * math.sin(th)))
            verts.append(G(*p))
    m = len(prof)
    for j in range(m - 1):
        for i in range(seg):
            a, b = j * seg + i, j * seg + (i + 1) % seg
            faces.append((a, b, b + seg, a + seg))
    verts.append(G(c[0], c[1] + prof[0][0], c[2]))
    verts.append(G(c[0], c[1] + prof[-1][0], c[2]))
    cb, ct = len(verts) - 2, len(verts) - 1
    for i in range(seg):
        faces.append((cb, (i + 1) % seg, i))
        faces.append((ct, (m - 1) * seg + i, (m - 1) * seg + (i + 1) % seg))
    ob = KS.mesh_obj("l", verts, faces, mat)
    if axis:                                     # lay it over: rotate about c
        ob.matrix_world = (Matrix.Translation(G(*c)) @ Matrix.Rotation(math.radians(axis[1]), 4, Vector(G(*axis[0]) - G(0, 0, 0)).normalized())
                           @ Matrix.Translation(-G(*c)))
        bpy.context.view_layer.update()
    return ob


def bowl(c, prof, thick, mat, seg=32):
    """A hollow vessel: an outer profile [(y, r)] and the same shrunk by thick inside, open at the top."""
    inner = [(y + thick, max(0.0, r - thick)) for y, r in prof]
    verts, faces = [], []
    rings = prof + inner[::-1]
    for y, r in rings:
        for i in range(seg):
            th = 2 * math.pi * i / seg
            verts.append(G(c[0] + r * math.cos(th), c[1] + y, c[2] + r * math.sin(th)))
    m = len(rings)
    for j in range(m - 1):
        for i in range(seg):
            a, b = j * seg + i, j * seg + (i + 1) % seg
            faces.append((a, b, b + seg, a + seg))
    verts.append(G(c[0], c[1] + prof[0][0], c[2]))
    verts.append(G(c[0], c[1] + inner[0][0], c[2]))
    cb, ci = len(verts) - 2, len(verts) - 1
    for i in range(seg):
        faces.append((cb, (i + 1) % seg, i))
        faces.append((ci, (m - 1) * seg + i, (m - 1) * seg + (i + 1) % seg))
    return KS.mesh_obj("w", verts, faces, mat)


def ball(c, r, mat, seg=24):
    rr = r if isinstance(r, (tuple, list)) else (r, r, r)
    return KS.ellipsoid("e", c, rr, mat, seg=seg)


def ellip(c, r, mat, rot=(0, 0, 0), seg=24):
    return KS.ellipsoid("e", c, r, mat, rot=rot, seg=seg)


def caps(a, b, ra, rb, mat, seg=20):
    return KS.capsule("k", a, b, ra, rb, mat, seg=seg, rings=4)


def torus(c, R, r, mat, normal=(0, 1, 0), seg=48, tseg=12, arc=1.0):
    n = Vector(normal).normalized()
    up = Vector((0, 1, 0)) if abs(n.y) < 0.9 else Vector((1, 0, 0))
    u = n.cross(up).normalized()
    v = n.cross(u).normalized()
    C = Vector(c)
    verts, faces = [], []
    closed = arc >= 1.0
    ns = seg if closed else seg + 1
    for i in range(ns):
        th = 2 * math.pi * arc * i / seg
        d = u * math.cos(th) + v * math.sin(th)
        for j in range(tseg):
            ph = 2 * math.pi * j / tseg
            verts.append(G(*(C + d * (R + r * math.cos(ph)) + n * r * math.sin(ph))))
    for i in range(seg if closed else seg):
        i2 = (i + 1) % ns
        for j in range(tseg):
            j2 = (j + 1) % tseg
            faces.append((i * tseg + j, i2 * tseg + j, i2 * tseg + j2, i * tseg + j2))
    if not closed:
        faces.append(tuple(range(tseg))[::-1])
        faces.append(tuple(range((ns - 1) * tseg, ns * tseg)))
    return KS.mesh_obj("t", verts, faces, mat)


def chain(a, b, mat, link=0.09, r=0.02):
    """Alternating oval links from a to b."""
    A, ax, L, u, v = _frame(a, b)
    n = max(1, int(L / (link * 1.5)))
    for i in range(n):
        c = A + ax * (L * (i + 0.5) / n)
        side = u if i % 2 else v
        # a ring in the plane of ax and side: its normal is their cross
        torus(tuple(c), link * 0.55, r, mat, normal=tuple(ax.cross(side)), seg=16, tseg=6)


def crystal(c, h, r, mat, tilt=(0, 0, 0), sides=6, lo=0.35):
    """A bipyramid shard: a prism of radius r with points top and bottom (the lower point lo of the height)."""
    verts = []
    cx, cy, cz = c
    y0, y1 = -h * lo, h * (1 - lo)
    ring_lo, ring_hi = y0 * 0.35, y1 * 0.45
    R = (Matrix.Rotation(math.radians(tilt[2]), 3, "Z") @ Matrix.Rotation(math.radians(tilt[1]), 3, "Y")
         @ Matrix.Rotation(math.radians(tilt[0]), 3, "X"))
    pts = [Vector((0, y0, 0))]
    for yy in (ring_lo, ring_hi):
        for i in range(sides):
            th = 2 * math.pi * i / sides
            pts.append(Vector((r * math.cos(th), yy, r * math.sin(th))))
    pts.append(Vector((0, y1, 0)))
    verts = [G(*(R @ p + Vector(c))) for p in pts]
    faces = []
    for i in range(sides):
        j = (i + 1) % sides
        faces.append((0, 1 + j, 1 + i))
        faces.append((1 + i, 1 + j, 1 + sides + j, 1 + sides + i))
        faces.append((1 + sides + i, 1 + sides + j, 1 + 2 * sides))
    return KS.mesh_obj("x", verts, faces, mat)


def frustum_shell(x0, z0, x1, z1, y0, y1, top, thick, mat):
    """A hollow four-sided hood: the rim x0..x1, z0..z1 at y0 narrowing to the box `top` (tx0, tz0, tx1, tz1) at y1."""
    tx0, tz0, tx1, tz1 = top
    o = [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), (tx0, y1, tz0), (tx1, y1, tz0), (tx1, y1, tz1), (tx0, y1, tz1)]
    i = [(x0 + thick, y0, z0 + thick), (x1 - thick, y0, z0 + thick), (x1 - thick, y0, z1 - thick), (x0 + thick, y0, z1 - thick),
         (tx0 + thick, y1, tz0 + thick), (tx1 - thick, y1, tz0 + thick), (tx1 - thick, y1, tz1 - thick), (tx0 + thick, y1, tz1 - thick)]
    verts = [G(*p) for p in o + i]
    faces = []
    for k in range(4):
        n = (k + 1) % 4
        faces.append((k, n, 4 + n, 4 + k))                       # outer side
        faces.append((8 + n, 8 + k, 12 + k, 12 + n))             # inner side
        faces.append((n, k, 8 + k, 8 + n))                       # bottom rim
        faces.append((4 + k, 4 + n, 12 + n, 12 + k))             # top rim
    return KS.mesh_obj("h", verts, faces, mat)


def mesh(verts, faces, mat):
    return KS.mesh_obj("m", [G(*p) for p in verts], faces, mat)


def prism(pts2d, z0, z1, mat, plane="xy"):
    """An extruded polygon: pts2d in the (x, y) plane extruded along z (or 'zy': (z, y) extruded along x)."""
    n = len(pts2d)
    verts = []
    for zz in (z0, z1):
        for a, b in pts2d:
            verts.append((a, b, zz) if plane == "xy" else (zz, b, a))
    faces = [tuple(range(n))[::-1], tuple(range(n, 2 * n))]
    for k in range(n):
        j = (k + 1) % n
        faces.append((k, j, n + j, n + k))
    return mesh(verts, faces, mat)


def stretch(ob, c, sx, sz):
    """Scale a made part about game point c along game x and z."""
    C = G(*c)
    ob.matrix_world = Matrix.Translation(C) @ Matrix.Diagonal((sx, sz, 1.0, 1.0)) @ Matrix.Translation(-C) @ ob.matrix_world
    bpy.context.view_layer.update()


def cut(ob):
    """Make an already-made part carve instead of fill."""
    for i, (o, m) in enumerate(KS.PARTS):
        if o is ob:
            KS.PARTS[i] = (o, "~cut")
            break
    return ob


# ================================================================ small kit pieces

def rivets(pts, mat="brass", r=0.025):
    for p in pts:
        ball(p, r, mat, seg=10)


def hammer(x, y, z, ang=0, mat="iron", L=0.42):
    """A smith's hammer lying flat, handle along x turned by ang (degrees about y)."""
    a = math.radians(ang)
    dx, dz = math.cos(a), math.sin(a)
    cyl((x, y + 0.025, z), (x + dx * L, y + 0.025, z + dz * L), 0.022, "wood")
    hx, hz = x + dx * L, z + dz * L
    cyl((hx - dz * 0.09, y + 0.04, hz + dx * 0.09), (hx + dz * 0.07, y + 0.04, hz - dx * 0.07), 0.04, mat)


def tongs(a, b, mat="iron_dark"):
    """Long tongs: two arms from the handle end a to the jaw end b, splayed a little."""
    A, B = Vector(a), Vector(b)
    side = (B - A).cross(Vector((0, 1, 0))).normalized() * 0.03
    m = A + (B - A) * 0.7
    for s in (1, -1):
        cyl(tuple(A + side * s * 1.4), tuple(m), 0.014, mat)
        cyl(tuple(m), tuple(B + side * s), 0.016, mat)
    ball(tuple(m), 0.025, mat, seg=10)


def sword(base, up=0.9, ang=0, blade="steel", grip="leather", guard="iron", w=0.06):
    """A sword standing point-up from base (its pommel), turned ang degrees about y."""
    x, y, z = base
    a = math.radians(ang)
    ux, uz = math.cos(a), math.sin(a)
    cyl((x, y, z), (x, y + 0.04, z), 0.03, guard)                                  # pommel
    cyl((x, y + 0.04, z), (x, y + 0.2, z), 0.022, grip)
    box(x - ux * 0.13 - uz * 0.03, y + 0.2, z - uz * 0.13 - ux * 0.03, x + ux * 0.13 + uz * 0.03, y + 0.24, z + uz * 0.13 + ux * 0.03,
        guard, bevel=0.01)
    pts = [(-w, 0), (w, 0), (w * 0.85, up * 0.8), (0, up), (-w * 0.85, up * 0.8)]
    verts, faces = [], []
    t = 0.014
    for s in (-t, t):
        for px, py in pts:
            verts.append((x + ux * px - uz * s, y + 0.24 + py, z + uz * px + ux * s))
    n = len(pts)
    faces = [tuple(range(n))[::-1], tuple(range(n, 2 * n))] + [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    mesh(verts, faces, blade)


def book(x, y, z, w, h, d, cover, ang=0):
    box(x, y, z, x + w, y + h, z + d, cover, bevel=0.006, rot=(0, ang, 0))
    box(x + 0.008, y + 0.008, z + 0.03, x + w - 0.008, y + h - 0.008, z + d + 0.004, "paper", bevel=0.002, rot=(0, ang, 0))


def candle(x, y, z, h=0.12, r=0.025):
    cyl((x, y, z), (x, y + h, z), r, "wax", seg=12)
    ellip((x, y + h + 0.03, z), (0.012, 0.03, 0.012), "flame", seg=8)


def flask(x, y, z, r, h, liquid):
    lathe((x, y, z), [(0, r * 0.6), (r * 0.3, r), (r * 1.4, r * 0.95), (r * 1.9, r * 0.35), (h, r * 0.3), (h + 0.01, r * 0.38)], "glass", seg=16)
    lathe((x, y + 0.01, z), [(0, r * 0.55), (r * 0.3, r * 0.9), (r * 1.2, r * 0.88)], liquid, seg=16)
    cyl((x, y + h, z), (x, y + h + 0.03, z), r * 0.3, "wood", seg=10)


def plank_wall(x0, x1, y0, y1, z0, z1, mat="wood", n=None):
    n = n or max(1, round((x1 - x0) / 0.25))
    w = (x1 - x0) / n
    for i in range(n):
        box(x0 + i * w + 0.004, y0, z0, x0 + (i + 1) * w - 0.004, y1, z1, mat if i % 3 else mat + "_dark" if mat == "wood" else mat,
            bevel=0.01)


# ================================================================ the forge

@prop("great_hearth", 4, 3, 2)
def great_hearth():
    """The Ashforge's great hearth: a firebrick plinth with an ash-pit arch, a bed of glowing coals in an iron tray,
    a firebrick back, a riveted copper hood on iron posts narrowing into the chimney flue, and leather bellows
    on its right working through an iron tuyere."""
    # plinth and its stepped foot
    box(0.0, 0.0, 0.15, 3.0, 0.12, 2.0, "stone_dark", bevel=0.02)
    box(0.06, 0.12, 0.22, 2.94, 1.0, 1.95, "firebrick", bevel=0.03)
    for x in (0.06, 2.62):                                            # dressed corner quoins
        for k in range(4):
            box(x, 0.12 + k * 0.22, 0.2, x + 0.32, 0.12 + k * 0.22 + 0.2, 0.55 if k % 2 else 0.45, "stone", bevel=0.02)
    box(0.0, 0.98, 0.12, 3.0, 1.1, 2.0, "stone", bevel=0.03)          # the hearth's capstone rim
    # ash-pit arch in the front with embers glowing far back
    cut(box(1.05, 0.12, 0.0, 1.95, 0.55, 0.9, "x", bevel=0.0))
    cut(cyl((1.5, 0.55, 0.0), (1.5, 0.55, 0.9), 0.45, "x"))
    box(1.0, 0.12, 0.85, 2.0, 0.2, 0.95, "coals_glow", bevel=0.0)
    for k in range(5):                                                # voussoirs round the arch
        a = math.pi * (k + 0.5) / 5
        cx, cy = 1.5 + math.cos(a) * 0.52, 0.55 + math.sin(a) * 0.52
        box(cx - 0.07, cy - 0.07, 0.17, cx + 0.07, cy + 0.07, 0.24, "stone", bevel=0.015, rot=(0, 0, math.degrees(a) - 90))
    # the coal bed in its iron tray
    cut(box(0.35, 0.95, 0.4, 2.65, 1.2, 1.65, "x", bevel=0.0))
    box(0.32, 0.9, 0.37, 2.68, 0.98, 1.68, "iron_dark", bevel=0.01)
    rnd = random.Random(4)
    for _ in range(70):
        x, z = rnd.uniform(0.42, 2.58), rnd.uniform(0.45, 1.6)
        hot = math.hypot((x - 1.5) / 1.1, (z - 1.0) / 0.6)
        ball((x, 0.99 + rnd.uniform(0, 0.03), z), (rnd.uniform(0.05, 0.09), rnd.uniform(0.03, 0.06), rnd.uniform(0.05, 0.09)),
             "coals_glow" if hot < 0.75 or rnd.random() < 0.25 else "coal", seg=10)
    # firebrick back wall up into the hood
    box(0.1, 1.0, 1.62, 2.9, 2.05, 1.98, "firebrick", bevel=0.02)
    for k in range(5):
        box(0.1, 1.2 + k * 0.18, 1.6, 2.9, 1.215 + k * 0.18, 1.63, "mortar", bevel=0.0)
    # iron posts holding the hood's front corners
    for x in (0.16, 2.84):
        cyl((x, 1.08, 0.2), (x, 2.0, 0.2), 0.055, "iron_dark")
        cyl((x, 1.08, 0.2), (x, 1.16, 0.2), 0.085, "iron_dark")
    # the copper hood, a riveted band round its rim and seams up its corners
    frustum_shell(-0.02, 0.05, 3.02, 2.0, 1.95, 2.98, (1.05, 0.62, 1.95, 1.62), 0.07, "copper")
    frustum_shell(-0.05, 0.02, 3.05, 2.02, 1.92, 2.1, (-0.03, 0.04, 3.03, 2.0), 0.08, "iron_dark")
    rivets([(0.1 + k * 0.28, 2.01, 0.0) for k in range(11)])
    for (bx, bz, tx, tz) in ((0.0, 0.05, 1.05, 0.62), (3.0, 0.05, 1.95, 0.62)):
        for k in range(1, 5):
            t = k / 5
            rivets([(bx + (tx - bx) * t, 2.0 + t * 0.95, bz + (tz - bz) * t - 0.02)], r=0.022)
    box(1.02, 2.95, 0.6, 1.98, 3.0, 1.64, "iron_dark", bevel=0.01)    # the flue collar
    # bellows on the right: two boards with the leather between, a tuyere into the fire, the lever above
    bx = 3.5
    box(3.06, 0.0, 0.4, 3.94, 0.45, 1.7, "stone_dark", bevel=0.02)                        # its stand
    box(3.1, 0.45, 0.25, 3.9, 0.52, 1.75, "wood_dark", bevel=0.015)                       # lower board
    pleats = [(0.52 + k * 0.05, 0.36 - 0.06 * (k % 2)) for k in range(7)]
    for y, s in pleats:
        box(bx - s, y, 0.35, bx + s, y + 0.05, 1.68, "leather", bevel=0.02)
    box(3.12, 0.86, 0.3, 3.88, 0.93, 1.72, "wood_dark", bevel=0.015, rot=(4, 0, 0))     # upper board, tipped
    for x in (3.2, 3.8):
        box(x - 0.02, 0.86, 0.5, x + 0.02, 0.95, 1.5, "iron_dark", bevel=0.0)
    cyl((3.5, 0.68, 1.75), (3.5, 0.68, 1.95), 0.07, "iron_dark")                          # nozzle out of the back
    cyl((3.5, 0.68, 1.92), (2.94, 0.85, 1.92), 0.05, "iron_dark")                         # tuyere into the hearth side
    box(3.46, 0.93, 0.9, 3.54, 1.6, 0.98, "wood_dark", bevel=0.01)                         # lever post
    cyl((3.5, 1.58, 0.2), (3.5, 1.58, 1.7), 0.035, "wood", seg=12)                         # the lever
    chain((3.5, 1.56, 0.45), (3.5, 0.94, 0.45), "iron_dark")
    # the smith's tools hung off the front
    tongs((0.3, 0.98, 0.12), (0.55, 0.25, 0.1))
    cyl((2.55, 0.98, 0.1), (2.75, 0.2, 0.08), 0.018, "iron_dark")                          # poker
    torus((2.55, 1.0, 0.08), 0.04, 0.012, "iron_dark", normal=(0, 0, 1), seg=12, tseg=6)


@prop("smith_anvil", 1, 1, 1)
def smith_anvil():
    """A horned anvil on an oak stump with iron hoops, a hammer resting on its face and a hardy tool in its hole."""
    lathe((0.5, 0, 0.5), [(0, 0.44), (0.04, 0.42), (0.44, 0.4), (0.48, 0.38)], "wood_dark", seg=28)
    lathe((0.5, 0, 0.5), [(0.47, 0.37), (0.49, 0.37)], "wood_end", seg=28)
    for y in (0.08, 0.36):
        lathe((0.5, y, 0.5), [(0, 0.43), (0.04, 0.43)], "iron_dark", seg=28)
    # the anvil, long along x
    box(0.24, 0.49, 0.3, 0.76, 0.56, 0.7, "iron_dark", bevel=0.015)                   # foot
    box(0.18, 0.49, 0.26, 0.3, 0.53, 0.74, "iron_dark", bevel=0.01)
    box(0.7, 0.49, 0.26, 0.82, 0.53, 0.74, "iron_dark", bevel=0.01)
    box(0.34, 0.56, 0.38, 0.66, 0.74, 0.62, "iron", bevel=0.02)                        # waist
    box(0.22, 0.74, 0.34, 0.78, 0.86, 0.66, "iron", bevel=0.015)                        # body
    box(0.22, 0.86, 0.35, 0.78, 0.885, 0.65, "steel", bevel=0.005)                      # the hardened face
    cut(box(0.68, 0.84, 0.43, 0.72, 0.9, 0.47, "x", bevel=0.0))                         # hardy hole
    caps((0.79, 0.81, 0.5), (0.98, 0.84, 0.5), 0.07, 0.012, "iron", seg=16)             # the horn
    box(0.06, 0.8, 0.4, 0.23, 0.875, 0.6, "iron", bevel=0.01)                           # the heel
    # a hammer on the face and a hot bar cooling on the horn side
    hammer(0.3, 0.885, 0.42, ang=-12, L=0.36)
    box(0.5, 0.885, 0.55, 0.92, 0.91, 0.585, "molten", bevel=0.004, rot=(0, -8, 0))


@prop("quench_trough", 2, 1, 1)
def quench_trough():
    """An iron-banded oak trough of dark water with a blade and tongs left in it to cool."""
    box(0.05, 0.0, 0.08, 1.95, 0.72, 0.92, "wood", bevel=0.03)
    cut(box(0.14, 0.12, 0.17, 1.86, 0.8, 0.83, "x", bevel=0.0))
    box(0.14, 0.12, 0.17, 1.86, 0.6, 0.83, "water_dark", bevel=0.0)
    for x in (0.3, 1.0, 1.7):
        box(x - 0.035, 0.0, 0.06, x + 0.035, 0.73, 0.94, "iron_dark", bevel=0.008)
    for k in range(7):                                                  # stave lines
        box(0.05 + k * 0.27 + 0.13, 0.05, 0.075, 0.05 + k * 0.27 + 0.145, 0.7, 0.085, "wood_dark", bevel=0.0)
    for x in (0.12, 1.88):                                              # legs
        box(x - 0.07, 0.0, 0.1, x + 0.07, 0.08, 0.9, "wood_dark", bevel=0.01)
    sword((0.6, 0.2, 0.5), up=0.55, ang=10)
    tongs((1.35, 0.95, 0.35), (1.25, 0.3, 0.6))


@prop("grindstone_wheel", 2, 2, 1)
def grindstone_wheel():
    """A treadle grindstone: a big sandstone wheel on an iron axle in an oak frame, a crank, a water tray under the
    wheel and the foot treadle with its rod."""
    for x in (0.55, 1.45):                                              # the frame's A-legs
        box(x - 0.05, 0.0, 0.15, x + 0.05, 1.2, 0.25, "wood_dark", bevel=0.01, rot=(-14, 0, 0))
        box(x - 0.05, 0.0, 0.75, x + 0.05, 1.2, 0.85, "wood_dark", bevel=0.01, rot=(14, 0, 0))
        box(x - 0.05, 1.05, 0.3, x + 0.05, 1.18, 0.7, "wood_dark", bevel=0.01)
    box(0.3, 0.12, 0.2, 1.7, 0.22, 0.3, "wood", bevel=0.01)
    box(0.3, 0.12, 0.7, 1.7, 0.22, 0.8, "wood", bevel=0.01)
    cyl((0.9, 1.12, 0.5), (1.1, 1.12, 0.5), 0.62, "sandstone", seg=48)   # the wheel
    cyl((0.88, 1.12, 0.5), (1.12, 1.12, 0.5), 0.14, "iron_dark", seg=20)
    cyl((0.35, 1.12, 0.5), (1.65, 1.12, 0.5), 0.035, "iron_dark")       # axle
    box(1.65, 1.08, 0.46, 1.7, 1.45, 0.54, "iron_dark", bevel=0.005)   # crank
    cyl((1.68, 1.42, 0.5), (1.9, 1.42, 0.5), 0.03, "wood")
    box(0.6, 0.3, 0.25, 1.4, 0.48, 0.75, "wood", bevel=0.015)           # water tray
    cut(box(0.66, 0.36, 0.31, 1.34, 0.5, 0.69, "x", bevel=0.0))
    box(0.66, 0.36, 0.31, 1.34, 0.43, 0.69, "water_dark", bevel=0.0)
    box(0.2, 0.02, 0.35, 1.0, 0.07, 0.65, "wood", bevel=0.01, rot=(0, 0, 4))   # treadle
    cyl((0.4, 0.07, 0.5), (0.4, 1.0, 0.5), 0.016, "iron_dark")
    tool = sword((1.85, 0.0, 0.25), up=0.75, ang=0)                    # a blade waiting its turn


@prop("crucible_gantry", 2, 3, 1)
def crucible_gantry():
    """An iron gantry with a winch: a crucible hung on chains, tipped to pour a glowing stream into a tray of ingot
    moulds."""
    for x in (0.12, 1.88):
        box(x - 0.07, 0.0, 0.42, x + 0.07, 2.85, 0.58, "iron_dark", bevel=0.015)
        box(x - 0.14, 0.0, 0.3, x + 0.14, 0.1, 0.7, "stone_dark", bevel=0.02)
    box(0.0, 2.75, 0.4, 2.0, 2.92, 0.6, "iron_dark", bevel=0.02)
    rivets([(x, 2.84, 0.39) for x in (0.12, 0.6, 1.0, 1.4, 1.88)], "iron", 0.022)
    cyl((0.12, 1.3, 0.62), (0.12, 1.3, 0.85), 0.11, "wood", seg=20)    # winch drum
    torus((0.12, 1.3, 0.86), 0.12, 0.02, "iron_dark", normal=(0, 0, 1), seg=20)
    box(0.1, 1.28, 0.86, 0.14, 1.55, 0.9, "iron_dark", bevel=0.005)
    chain((0.12, 1.4, 0.62), (0.12, 2.74, 0.62), "iron_dark")
    chain((0.9, 2.74, 0.5), (0.9, 1.9, 0.5), "iron_dark")
    chain((1.1, 2.74, 0.5), (1.1, 1.9, 0.5), "iron_dark")
    box(0.8, 1.84, 0.46, 1.2, 1.9, 0.54, "iron_dark", bevel=0.01)       # the yoke
    # the crucible, tipped toward +x about z
    c = (1.0, 1.5, 0.5)
    prof = [(0, 0.12), (0.06, 0.2), (0.3, 0.24), (0.38, 0.25)]
    o = bowl(c, prof, 0.04, "clay_fired", seg=28)
    m = lathe(c, [(0.08, 0.17), (0.3, 0.21)], "molten", seg=24)
    for ob in (o, m):
        ob.matrix_world = Matrix.Translation(G(*c)) @ Matrix.Rotation(math.radians(-35), 4, "Y") @ Matrix.Translation(-G(*c))
    bpy.context.view_layer.update()
    for x in (0.74, 1.26):
        box(x - 0.025, 1.6, 0.47, x + 0.025, 1.86, 0.53, "iron_dark", bevel=0.005)
    # the stream and the moulds
    caps((1.27, 1.62, 0.5), (1.36, 0.28, 0.5), 0.04, 0.03, "molten", seg=12)
    box(0.75, 0.0, 0.15, 1.9, 0.18, 0.85, "iron_dark", bevel=0.015)
    for k in range(4):
        x = 0.82 + k * 0.27
        cut(box(x, 0.12, 0.25, x + 0.2, 0.2, 0.75, "x", bevel=0.0))
        box(x, 0.12, 0.25, x + 0.2, 0.155, 0.75, "molten" if k >= 2 else "iron", bevel=0.0)
    ellip((1.36, 0.2, 0.5), (0.08, 0.04, 0.08), "molten", seg=12)


@prop("trip_hammer", 4, 3, 2, V=12)
def trip_hammer():
    """A great trip hammer: an oak helve pivoted on a post at the back, its iron head over a squat anvil, lifted by
    pegs on the shaft of a big cogged wheel at the right."""
    box(0.0, 0.0, 0.0, 3.0, 0.12, 2.0, "stone_dark", bevel=0.02)
    # the pivot posts at the back
    for z in (1.2, 1.8):
        box(2.3, 0.1, z - 0.1, 2.5, 1.7, z + 0.1, "wood_dark", bevel=0.02)
    cyl((2.4, 1.45, 1.05), (2.4, 1.45, 1.95), 0.05, "iron_dark")
    # the helve from the pivot forward over the anvil
    box(0.45, 1.36, 1.43, 2.75, 1.56, 1.57, "wood", bevel=0.02, rot=(0, 0, -8))
    for x in (1.1, 1.8, 2.4):
        box(x - 0.04, 1.32, 1.4, x + 0.04, 1.62, 1.6, "iron_dark", bevel=0.005, rot=(0, 0, -8))
    box(0.32, 0.92, 1.3, 0.72, 1.5, 1.7, "iron", bevel=0.03)                     # the head
    box(0.36, 0.86, 1.34, 0.68, 0.94, 1.66, "steel", bevel=0.01)
    # its anvil block on a timber bed
    box(0.2, 0.12, 1.15, 0.85, 0.38, 1.85, "wood_dark", bevel=0.02)
    box(0.3, 0.38, 1.25, 0.75, 0.7, 1.75, "iron", bevel=0.02)
    box(0.33, 0.7, 1.28, 0.72, 0.73, 1.72, "steel", bevel=0.005)
    box(0.36, 0.73, 1.45, 0.69, 0.78, 1.55, "molten", bevel=0.01)              # a bloom under the hammer
    # the cog wheel at the right on its shaft
    cyl((2.85, 1.45, 0.1), (2.85, 1.45, 1.95), 0.11, "wood_dark", seg=16)
    for z in (0.1, 1.95):
        box(2.75, 0.1, z - 0.1, 2.95, 1.6, z + 0.1, "wood_dark", bevel=0.02)
    for k in range(4):                                                         # cams lifting the helve's tail
        a = 2 * math.pi * k / 4
        cyl((2.85, 1.45, 1.5), (2.85 + math.cos(a) * 0.3, 1.45 + math.sin(a) * 0.3, 1.5), 0.04, "iron_dark", seg=10)
    zc = 1.0
    torus((3.35, 1.45, zc), 0.95, 0.09, "wood", normal=(1, 0, 0), seg=48, tseg=8)
    for k in range(8):
        a = 2 * math.pi * k / 8
        cyl((3.35, 1.45, zc), (3.35, 1.45 + math.sin(a) * 0.95, zc + math.cos(a) * 0.95), 0.045, "wood_dark", seg=10)
    for k in range(20):                                                        # its teeth
        a = 2 * math.pi * k / 20
        box(3.3, 1.45 + math.sin(a) * 1.04 - 0.04, zc + math.cos(a) * 1.04 - 0.04, 3.4, 1.45 + math.sin(a) * 1.04 + 0.04,
            zc + math.cos(a) * 1.04 + 0.04, "wood_dark", bevel=0.005, rot=(math.degrees(a), 0, 0))
    cyl((3.2, 1.45, zc), (3.5, 1.45, zc), 0.12, "iron_dark", seg=16)
    cyl((2.85, 1.45, zc), (3.35, 1.45, zc), 0.06, "iron_dark", seg=12)
    box(3.25, 0.0, zc - 0.25, 3.45, 0.42, zc + 0.25, "stone_dark", bevel=0.02)


@prop("weapon_rack", 2, 2, 1)
def weapon_rack():
    """A smith's wall rack of finished work: two longswords, a bearded axe, a spear and a round shield."""
    box(0.0, 0.0, 0.82, 2.0, 1.95, 1.0, "wood_dark", bevel=0.02)
    for y in (0.2, 1.0, 1.75):
        box(0.0, y, 0.72, 2.0, y + 0.1, 0.84, "wood", bevel=0.015)
    for x in (0.3, 0.6, 1.3, 1.6):
        for y in (0.3, 1.1):
            cyl((x, y, 0.72), (x, y, 0.55), 0.025, "wood", seg=10)
    sword((0.3, 0.25, 0.62), up=1.2, ang=0)
    sword((0.6, 0.25, 0.62), up=1.15, ang=0, blade="steel_dark", grip="cloth_red")
    # bearded axe
    cyl((1.0, 0.25, 0.64), (1.0, 1.6, 0.64), 0.028, "wood")
    prism([(1.0, 1.35), (1.28, 1.3), (1.32, 1.62), (1.0, 1.58)], 0.62, 0.66, "steel")
    # spear
    cyl((1.6, 0.12, 0.6), (1.6, 1.7, 0.6), 0.022, "wood")
    prism([(1.56, 1.7), (1.64, 1.7), (1.6, 1.95)], 0.585, 0.615, "steel")
    # round shield on the right, painted and bossed
    cyl((1.35, 0.6, 0.58), (1.35, 0.6, 0.66), 0.32, "cloth_red", seg=36)
    torus((1.35, 0.6, 0.58), 0.31, 0.025, "iron_dark", normal=(0, 0, 1), seg=36)
    ball((1.35, 0.6, 0.56), 0.07, "iron", seg=14)
    box(1.33, 0.3, 0.565, 1.37, 0.9, 0.58, "iron_dark", bevel=0.0)


@prop("armour_stand", 1, 2, 1)
def armour_stand():
    """A plate harness on a wooden stand: great helm, breastplate with a ridge, pauldrons, faulds and a sword belt."""
    box(0.2, 0.0, 0.2, 0.8, 0.08, 0.8, "wood_dark", bevel=0.02)
    cyl((0.5, 0.08, 0.5), (0.5, 1.2, 0.5), 0.04, "wood")
    ellip((0.5, 1.2, 0.5), (0.24, 0.3, 0.16), "steel", seg=28)                 # breastplate
    box(0.495, 0.95, 0.33, 0.505, 1.45, 0.36, "steel_dark", bevel=0.0)         # its ridge
    for k in range(3):                                                         # faulds
        lathe((0.5, 0.82 - k * 0.08, 0.5), [(0, 0.2 + k * 0.015), (0.08, 0.19 + k * 0.015)], "steel" if k % 2 else "steel_dark", seg=24)
    for s in (-1, 1):
        ellip((0.5 + s * 0.27, 1.42, 0.5), (0.13, 0.09, 0.13), "steel", seg=20)  # pauldrons
        ellip((0.5 + s * 0.29, 1.36, 0.5), (0.12, 0.08, 0.12), "steel_dark", seg=20)
    cyl((0.5, 1.5, 0.5), (0.5, 1.56, 0.5), 0.06, "leather")
    # the great helm: a flat-topped cylinder with an eye slit and breaths
    cyl((0.5, 1.56, 0.5), (0.5, 1.86, 0.5), 0.13, "steel", seg=24)
    cyl((0.5, 1.86, 0.5), (0.5, 1.89, 0.5), 0.12, "steel_dark", seg=24)
    cut(box(0.39, 1.72, 0.3, 0.61, 1.745, 0.42, "x", bevel=0.0))
    box(0.495, 1.58, 0.36, 0.505, 1.86, 0.38, "brass", bevel=0.0)
    lathe((0.5, 1.05, 0.5), [(0, 0.255), (0.04, 0.255)], "leather", seg=24)   # belt
    box(0.47, 1.05, 0.23, 0.53, 1.09, 0.26, "brass", bevel=0.005)


@prop("tool_wall", 2, 2, 1)
def tool_wall():
    """A pegboard of smithing tools: tongs of three sizes, hammers, files, chisels and a row of horseshoes."""
    plank_wall(0.0, 2.0, 0.1, 1.9, 0.88, 1.0)
    box(0.0, 0.1, 0.84, 2.0, 0.16, 0.9, "wood_dark", bevel=0.01)
    box(0.0, 1.84, 0.84, 2.0, 1.9, 0.9, "wood_dark", bevel=0.01)
    for k, x in enumerate((0.2, 0.42, 0.64)):                                   # tongs hanging jaw-down
        tongs((x, 1.7, 0.84), (x, 0.9 - k * 0.12, 0.82))
        cyl((x, 1.72, 0.88), (x, 1.72, 0.78), 0.015, "wood")
    for k, x in enumerate((0.95, 1.2, 1.45)):                                   # hammers on pegs
        cyl((x, 1.62, 0.84), (x, 1.1 + k * 0.05, 0.84), 0.022, "wood")
        box(x - 0.09, 1.56, 0.8, x + 0.07, 1.66, 0.87, "iron", bevel=0.01)
        cyl((x, 1.7, 0.88), (x, 1.7, 0.78), 0.015, "wood")
    for k in range(3):                                                           # files and chisels
        x = 1.68 + k * 0.1
        box(x - 0.015, 1.05, 0.82, x + 0.015, 1.6, 0.85, "iron_dark", bevel=0.003)
        box(x - 0.02, 1.6, 0.81, x + 0.02, 1.75, 0.86, "wood", bevel=0.004)
    for k in range(5):                                                           # horseshoes
        x = 0.25 + k * 0.33
        torus((x, 0.45, 0.84), 0.1, 0.022, "iron_dark", normal=(0, 0, 1), seg=20, tseg=6, arc=0.75)
        cyl((x, 0.56, 0.88), (x, 0.56, 0.8), 0.012, "iron")


@prop("coal_bin", 1, 1, 1)
def coal_bin():
    """A slatted bin heaped with coal, a shovel stuck in the heap."""
    box(0.05, 0.0, 0.05, 0.95, 0.55, 0.95, "wood", bevel=0.02)
    cut(box(0.12, 0.08, 0.12, 0.88, 0.6, 0.88, "x", bevel=0.0))
    for y in (0.1, 0.45):
        box(0.03, y, 0.03, 0.97, y + 0.05, 0.97, "iron_dark", bevel=0.005)
    rnd = random.Random(9)
    ellip((0.5, 0.5, 0.5), (0.4, 0.18, 0.4), "coal", seg=20)
    for _ in range(26):
        ball((rnd.uniform(0.15, 0.85), rnd.uniform(0.52, 0.66), rnd.uniform(0.15, 0.85)), rnd.uniform(0.04, 0.07), "coal", seg=8)
    cyl((0.62, 0.55, 0.45), (0.85, 1.0, 0.3), 0.02, "wood")
    box(0.5, 0.48, 0.42, 0.68, 0.6, 0.56, "iron_dark", bevel=0.005, rot=(0, 0, -25))


@prop("ore_bin", 1, 1, 1)
def ore_bin():
    """A crate of rough ore: rusty iron lumps, copper ore and a few nuggets of gold."""
    box(0.05, 0.0, 0.05, 0.95, 0.5, 0.95, "wood_dark", bevel=0.02)
    cut(box(0.12, 0.08, 0.12, 0.88, 0.55, 0.88, "x", bevel=0.0))
    for x in (0.05, 0.9):
        box(x, 0.0, 0.03, x + 0.05, 0.52, 0.97, "wood", bevel=0.005)
    rnd = random.Random(12)
    ellip((0.5, 0.42, 0.5), (0.4, 0.14, 0.4), "ore_iron", seg=18)
    for _ in range(22):
        m = rnd.choice(("ore_iron", "ore_iron", "ore_copper", "stone", "gold"))
        ball((rnd.uniform(0.17, 0.83), rnd.uniform(0.47, 0.6), rnd.uniform(0.17, 0.83)), rnd.uniform(0.045, 0.08), m, seg=8)


@prop("ingot_stack", 1, 1, 1)
def ingot_stack():
    """Ingots stacked crosswise on a pallet: iron, a copper course and a gold one on top."""
    box(0.08, 0.0, 0.08, 0.92, 0.08, 0.92, "wood", bevel=0.01)
    for k in range(5):
        y = 0.08 + k * 0.1
        mat = ("iron", "iron", "copper", "iron", "gold")[k]
        for j in range(4):
            o = 0.13 + j * 0.2
            if k % 2:
                box(0.12, y, o, 0.88, y + 0.08, o + 0.13, mat, bevel=0.015)
            else:
                box(o, y, 0.12, o + 0.13, y + 0.08, 0.88, mat, bevel=0.015)


# ================================================================ the baths

@prop("forge_crest", 5, 5, 1, V=12)
def forge_crest():
    """The guild's crest over the Ashforge gate: a heater shield of blackened iron in a bronze rim, an anvil on it
    with two war hammers crossed behind, and a flame rising off the anvil between their heads."""
    def shield(m):
        # the left half from the top corner down the curve to the point, mirrored for the right; m insets the rim
        half = [(0.4 + m, 4.9 - m)]
        for k in range(9):
            t = k / 8
            half.append((0.4 + m + (2.1 - m) * (1 - math.cos(t * math.pi / 2)) ** 1.3, 2.7 - (2.55 - m * 1.4) * math.sin(t * math.pi / 2)))
        right = [(5 - x, y) for x, y in half[::-1]]
        pts = half + right[1:]
        return pts                                                       # counter-clockwise seen from the front
    prism(shield(0.0), 0.55, 0.98, "bronze")
    prism(shield(0.22), 0.45, 0.9, "iron_dark")
    for x in (0.62, 1.5, 2.5, 3.5, 4.38):
        ball((x, 4.78, 0.52), 0.07, "brass", seg=10)
    # the hammers crossed, their heads above the anvil's ends
    for s in (1, -1):
        a = (2.5 - s * 1.55, 0.95)
        b = (2.5 + s * 1.45, 4.05)
        cyl((a[0], a[1], 0.42), (b[0], b[1], 0.42), 0.1, "wood_dark", seg=12)
        cyl((a[0], a[1], 0.42), (a[0] + (b[0] - a[0]) * 0.08, a[1] + (b[1] - a[1]) * 0.08, 0.42), 0.13, "bronze_dark", seg=12)
        ang = math.atan2(b[1] - a[1], b[0] - a[0]) + math.pi / 2
        hx, hy = b
        dx, dy = math.cos(ang), math.sin(ang)
        cyl((hx - dx * 0.55, hy - dy * 0.55, 0.42), (hx + dx * 0.55, hy + dy * 0.55, 0.42), 0.26, "bronze", seg=8)
        for e in (-1, 1):
            cyl((hx + e * dx * 0.5, hy + e * dy * 0.5, 0.42), (hx + e * dx * 0.62, hy + e * dy * 0.62, 0.42), 0.3, "bronze_dark", seg=8)
    # the anvil in front of them
    prism([(1.55, 0.75), (3.45, 0.75), (3.45, 0.95), (3.0, 1.12), (3.0, 1.5), (3.55, 1.56), (3.62, 2.02), (1.9, 2.02),
           (1.05, 1.9), (1.5, 1.68), (2.0, 1.5), (2.0, 1.12), (1.55, 0.95)], 0.18, 0.45, "iron")
    prism([(1.9, 1.94), (3.62, 1.94), (3.62, 2.06), (1.9, 2.06)], 0.16, 0.45, "steel")
    # the flame off its face
    caps((2.5, 2.25, 0.32), (2.5, 3.85, 0.32), 0.48, 0.04, "coals_glow", seg=16)
    caps((2.5, 2.2, 0.24), (2.5, 3.35, 0.24), 0.3, 0.03, "molten", seg=14)
    for s in (1, -1):
        caps((2.5 + s * 0.3, 2.2, 0.3), (2.5 + s * 0.62, 3.05, 0.3), 0.2, 0.03, "coals_glow", seg=12)


@prop("master_anvil", 3, 2, 2)
def master_anvil():
    """The Founders' Anvil on its dais: a great anvil of dark steel with runes burning in its waist, on a carved stone
    pedestal whose rune band glows, a blade on its face with its tip still hot and a sledge leant against it."""
    box(0.0, 0.0, 0.0, 3.0, 0.14, 2.0, "stone_dark", bevel=0.03)
    box(0.15, 0.14, 0.15, 2.85, 0.26, 1.85, "stone", bevel=0.03)
    box(0.35, 0.26, 0.4, 2.65, 0.92, 1.6, "stone", bevel=0.04)
    box(0.3, 0.86, 0.35, 2.7, 0.98, 1.65, "stone_pale", bevel=0.03)
    for k in range(7):                                                   # the rune band round the pedestal
        x = 0.55 + k * 0.32
        for z, z2 in ((0.37, 0.41), (1.59, 1.63)):
            box(x, 0.5, z, x + 0.12, 0.54, z2, "molten", bevel=0.0)
            box(x + 0.04, 0.4, z, x + 0.08, 0.72, z2, "molten", bevel=0.0)
            box(x, 0.62 if k % 2 else 0.42, z, x + 0.12, 0.66 if k % 2 else 0.46, z2, "molten", bevel=0.0)
    # the anvil, long along x
    box(0.6, 0.98, 0.55, 2.4, 1.1, 1.45, "iron_dark", bevel=0.03)
    box(0.45, 0.98, 0.5, 0.75, 1.06, 1.5, "iron_dark", bevel=0.02)
    box(2.25, 0.98, 0.5, 2.55, 1.06, 1.5, "iron_dark", bevel=0.02)
    box(0.95, 1.1, 0.72, 2.05, 1.42, 1.28, "iron", bevel=0.04)
    for x in (1.15, 1.5, 1.85):                                          # runes in its waist
        box(x - 0.05, 1.16, 0.69, x + 0.05, 1.36, 0.73, "molten", bevel=0.0)
        box(x - 0.09, 1.24, 0.69, x + 0.09, 1.27, 0.73, "molten", bevel=0.0)
    box(0.55, 1.42, 0.62, 2.35, 1.66, 1.38, "iron", bevel=0.03)
    box(0.55, 1.66, 0.64, 2.35, 1.7, 1.36, "steel", bevel=0.008)
    caps((2.33, 1.6, 1.0), (2.98, 1.66, 1.0), 0.16, 0.02, "iron", seg=18)       # the horn
    box(0.2, 1.5, 0.75, 0.58, 1.69, 1.25, "iron", bevel=0.02)                     # the heel
    rivets([(x, 1.55, 0.61) for x in (0.7, 1.1, 1.5, 1.9, 2.3)], "brass", 0.03)
    # a blade on the face, its tip glowing; a sledge leant on the pedestal
    box(0.8, 1.7, 0.92, 2.1, 1.73, 1.06, "steel", bevel=0.004)
    box(2.1, 1.7, 0.94, 2.45, 1.73, 1.04, "molten", bevel=0.004)
    box(0.6, 1.7, 0.88, 0.8, 1.76, 1.1, "iron_dark", bevel=0.005)
    cyl((0.45, 1.73, 1.0), (0.6, 1.73, 1.0), 0.03, "leather", seg=10)
    cyl((2.75, 0.14, 0.25), (2.6, 1.15, 0.33), 0.035, "wood_dark", seg=10)
    box(2.48, 1.1, 0.18, 2.86, 1.32, 0.46, "iron_dark", bevel=0.02, rot=(0, 0, 8))


def pear(sc, n=20):
    """A bellows board's outline in the x-z plane round x 1: narrow at the nozzle (z 0.35), round at the back."""
    pts = []
    for k in range(n + 1):
        a = math.pi * k / n                                              # round the back, east to west
        pts.append((1.0 + 0.85 * sc * math.cos(a), 2.15 + 0.7 * sc * math.sin(a)))
    pts.append((1.0 - 0.28 * sc, 0.35))
    pts.append((1.0 + 0.28 * sc, 0.35))
    return pts[::-1]


def tilted(pts, yf, yb, t, mat, zf=0.35, zb=2.85):
    """A plate of thickness t over pts [(x, z)], its underside at yf at the front (zf) rising to yb at the back (zb)."""
    def y(z):
        return yf + (yb - yf) * (z - zf) / (zb - zf)
    verts = [(a, y(b), b) for a, b in pts] + [(a, y(b) + t, b) for a, b in pts]
    n = len(pts)
    faces = [tuple(range(n)), tuple(range(n, 2 * n))[::-1]] + [(n + k, n + (k + 1) % n, (k + 1) % n, k) for k in range(n)]
    return mesh(verts, faces, mat)


@prop("great_bellows", 2, 2, 3)
def great_bellows():
    """Giant forge bellows on a timber cradle, nozzle to the front: two pear-shaped boards, the upper tipped open,
    pleated leather bulging between them, iron straps, a lever beam on a post at the back chained to the upper
    board, a stone counterweight on its end."""
    for z in (0.7, 2.4):                                                             # the cradle
        box(0.05, 0.0, z - 0.14, 1.95, 0.36, z + 0.14, "wood_dark", bevel=0.03)
    box(0.85, 0.0, 0.4, 1.15, 0.3, 2.8, "wood", bevel=0.02)
    tilted(pear(1.0), 0.36, 0.36, 0.08, "wood")                                      # lower board
    for k in range(7):                                                               # leather, pleated and bulging
        t0, t1 = k / 7, (k + 1) / 7
        sc = 1.06 if k % 2 else 0.97
        tilted(pear(sc), 0.44 + 0.2 * t0, 0.44 + 0.75 * t0, 0.2 * (t1 - t0) + 0.04, "leather_red" if k % 2 == 0 else "leather")
    tilted(pear(1.0), 0.64, 1.19, 0.08, "wood")                                      # upper board, tipped open
    for z in (1.0, 1.7, 2.4):                                                        # iron straps over it
        y = 0.72 + 0.55 * (z - 0.35) / 2.5
        box(0.25, y, z - 0.05, 1.75, y + 0.04, z + 0.05, "iron_dark", bevel=0.005)
        rivets([(0.35, y + 0.05, z), (1.65, y + 0.05, z)], "brass", 0.03)
    cyl((1.0, 0.55, 0.45), (1.0, 0.5, 0.0), 0.15, "iron_dark", r2=0.08)              # the nozzle
    torus((1.0, 0.54, 0.32), 0.15, 0.035, "brass", normal=(0, 0, 1), seg=20)
    # the lever post behind and the beam over the top, chained to the upper board
    box(0.88, 0.0, 2.72, 1.12, 1.95, 2.96, "wood_dark", bevel=0.02)
    cyl((0.8, 1.84, 2.84), (1.2, 1.84, 2.84), 0.05, "iron_dark")
    box(0.93, 1.76, 0.3, 1.07, 1.9, 2.99, "wood", bevel=0.02)
    chain((1.0, 1.75, 1.5), (1.0, 1.0, 1.5), "iron_dark")
    chain((1.0, 1.75, 0.45), (1.0, 1.35, 0.45), "iron_dark")
    box(0.78, 1.05, 0.28, 1.22, 1.35, 0.62, "stone_dark", bevel=0.04)


@prop("molten_spout", 3, 4, 2)
def molten_spout():
    """The furnace's pour: an iron-lipped stone spout out of the wall, molten metal running down its channel and
    falling in a glowing stream into a stone basin, ingot moulds set in its back corners."""
    for x in (0.95, 2.05):                                               # the spout on its corbels
        box(x - 0.12, 2.6, 1.3, x + 0.12, 3.1, 2.0, "stone_dark", bevel=0.03)
    box(0.85, 3.05, 0.75, 2.15, 3.45, 2.0, "stone", bevel=0.04)
    cut(box(1.2, 3.25, 0.7, 1.8, 3.5, 2.0, "x", bevel=0.0))
    box(1.2, 3.25, 0.8, 1.8, 3.32, 2.0, "molten", bevel=0.0)
    box(0.8, 3.0, 0.68, 2.2, 3.5, 0.8, "iron_dark", bevel=0.02)
    cut(box(1.2, 3.3, 0.6, 1.8, 3.6, 0.9, "x", bevel=0.0))
    rivets([(x, 3.42, 0.67) for x in (0.9, 2.1)], "iron", 0.035)
    caps((1.5, 3.28, 0.72), (1.5, 0.5, 0.62), 0.1, 0.16, "molten", seg=14)     # the falling stream
    # the basin
    box(0.15, 0.0, 0.0, 2.85, 0.62, 1.7, "stone", bevel=0.05)
    cut(box(0.3, 0.3, 0.15, 2.7, 0.7, 1.55, "x", bevel=0.0))
    box(0.3, 0.3, 0.15, 2.7, 0.5, 1.55, "molten", bevel=0.0)
    box(0.1, 0.56, -0.02, 2.9, 0.66, 0.12, "iron_dark", bevel=0.01)
    for x in (0.4, 1.5, 2.6):
        box(x - 0.05, 0.0, -0.03, x + 0.05, 0.64, 1.72, "iron_dark", bevel=0.008)
    for x in (0.55, 2.2):
        box(x, 0.48, 1.05, x + 0.28, 0.56, 1.45, "iron", bevel=0.01)


@prop("ore_cart", 1, 1, 2)
def ore_cart():
    """An iron-bound mine cart on a stub of rail, heaped with iron and copper ore and coal."""
    for x in (0.18, 0.82):                                               # the rails on sleepers
        box(x - 0.04, 0.02, 0.0, x + 0.04, 0.08, 2.0, "iron", bevel=0.005)
    for z in (0.2, 0.7, 1.2, 1.7):
        box(0.05, 0.0, z - 0.07, 0.95, 0.03, z + 0.07, "wood_dark", bevel=0.005)
    for z in (0.45, 1.55):
        cyl((0.1, 0.18, z), (0.24, 0.18, z), 0.12, "iron_dark", seg=16)
        cyl((0.76, 0.18, z), (0.9, 0.18, z), 0.12, "iron_dark", seg=16)
    frustum_shell(0.14, 0.2, 0.86, 1.8, 0.24, 0.78, (0.06, 0.1, 0.94, 1.9), 0.05, "wood")
    box(0.18, 0.22, 0.24, 0.82, 0.3, 1.76, "wood_dark", bevel=0.01)
    for z in (0.15, 1.0, 1.85):
        box(0.04, 0.3, z - 0.035, 0.96, 0.8, z + 0.035, "iron_dark", bevel=0.006)
    rnd = random.Random(11)
    for _ in range(26):
        x, z = rnd.uniform(0.2, 0.8), rnd.uniform(0.25, 1.75)
        top = 0.78 + 0.16 * (1 - abs(z - 1.0) / 0.9) * (1 - abs(x - 0.5) / 0.4)
        ball((x, top - 0.05, z), (rnd.uniform(0.07, 0.12), rnd.uniform(0.05, 0.09), rnd.uniform(0.07, 0.12)),
             rnd.choice(("ore_iron", "ore_iron", "ore_copper", "coal")), seg=10)


@prop("lion_spout", 1, 2, 1)
def lion_spout():
    """A marble lion's head on the wall, its mane in heavy curls, water pouring from its open jaws into the pool."""
    y0 = 1.0
    box(0.1, y0 + 0.05, 0.86, 0.9, y0 + 0.95, 1.0, "marble", bevel=0.03)                 # its plaque
    torus((0.5, y0 + 0.5, 0.86), 0.33, 0.04, "gold", normal=(0, 0, 1), seg=36)
    rnd = random.Random(2)
    for k in range(14):                                                                   # the mane's curls
        a = 2 * math.pi * k / 14
        ball((0.5 + math.cos(a) * 0.26, y0 + 0.5 + math.sin(a) * 0.26, 0.74), (0.1, 0.1, 0.1), "bronze_dark", seg=12)
    ellip((0.5, y0 + 0.5, 0.7), (0.2, 0.22, 0.16), "bronze", seg=24)                     # face
    ellip((0.5, y0 + 0.42, 0.58), (0.11, 0.08, 0.09), "bronze", seg=18)                  # muzzle
    ball((0.5, y0 + 0.47, 0.5), 0.035, "bronze_dark", seg=10)
    for s in (-1, 1):
        ball((0.5 + s * 0.08, y0 + 0.57, 0.57), 0.03, "bronze_dark", seg=10)
        ellip((0.5 + s * 0.08, y0 + 0.62, 0.57), (0.06, 0.02, 0.03), "bronze", seg=10)
        ball((0.5 + s * 0.17, y0 + 0.72, 0.7), 0.05, "bronze", seg=10)
    cut(ellip((0.5, y0 + 0.33, 0.56), (0.07, 0.04, 0.06), "x", seg=12))                  # open jaws
    cyl((0.5, y0 + 0.33, 0.6), (0.5, y0 + 0.33, 0.46), 0.03, "brass", seg=12)
    caps((0.5, y0 + 0.31, 0.46), (0.5, 0.0, 0.32), 0.04, 0.05, "water", seg=12)          # the stream
    ellip((0.5, 0.02, 0.32), (0.14, 0.03, 0.14), "foam", seg=14)


@prop("bath_boiler", 2, 3, 2)
def bath_boiler():
    """The baths' copper boiler: a brick firebox with a glowing grate, a riveted copper tank with a domed top,
    a pressure gauge, valve wheels and the hot pipe out to the pools, its flue going up."""
    box(0.05, 0.0, 0.1, 1.95, 0.7, 1.9, "firebrick", bevel=0.03)
    box(0.0, 0.65, 0.05, 2.0, 0.75, 1.95, "stone", bevel=0.02)
    box(0.7, 0.12, 0.06, 1.3, 0.5, 0.1, "iron_dark", bevel=0.01)                          # fire door
    for k in range(5):
        box(0.76 + k * 0.11, 0.18, 0.04, 0.8 + k * 0.11, 0.44, 0.08, "coals_glow", bevel=0.0)
    box(0.68, 0.1, 0.03, 1.32, 0.14, 0.09, "iron_dark", bevel=0.005)
    c = (1.0, 0.75, 1.0)
    lathe(c, [(0, 0.8), (1.5, 0.8), (1.62, 0.76), (1.75, 0.66), (1.85, 0.45), (1.9, 0.2), (1.92, 0.0)], "copper", seg=40)
    for y in (0.08, 0.55, 1.05, 1.48):                                                    # riveted bands
        lathe((1.0, 0.75 + y, 1.0), [(0, 0.83), (0.07, 0.83)], "copper_dark", seg=40)
        rivets([(1.0 + math.cos(a) * 0.835, 0.75 + y + 0.035, 1.0 + math.sin(a) * 0.835) for a in
                [2 * math.pi * k / 18 for k in range(18)]], "brass", 0.02)
    for k in range(3):                                                                    # verdigris runs
        a = 1.9 + k * 0.5
        box(1.0 + math.cos(a) * 0.78, 1.2, 1.0 + math.sin(a) * 0.78, 1.0 + math.cos(a) * 0.78 + 0.05, 2.2,
            1.0 + math.sin(a) * 0.78 + 0.05, "copper_green", bevel=0.0)
    # gauge on the front
    cyl((1.35, 1.75, 0.22), (1.35, 1.75, 0.12), 0.12, "brass", seg=24)
    cyl((1.35, 1.75, 0.12), (1.35, 1.75, 0.11), 0.095, "paper", seg=24)
    box(1.34, 1.74, 0.105, 1.42, 1.77, 0.11, "iron_dark", bevel=0.0, rot=(0, 0, 35))
    # valve wheels
    for (x, y) in ((0.6, 1.3), (0.6, 1.85)):
        cyl((x, y, 0.22), (x, y, 0.1), 0.03, "brass", seg=10)
        torus((x, y, 0.1), 0.1, 0.018, "iron_dark", normal=(0, 0, 1), seg=20, tseg=6)
        for a in (0, math.pi / 2):
            cyl((x - math.cos(a) * 0.1, y - math.sin(a) * 0.1, 0.1), (x + math.cos(a) * 0.1, y + math.sin(a) * 0.1, 0.1), 0.012, "iron_dark")
    # the hot pipe: out of the tank's side, down, and away along the floor (west)
    cyl((0.2, 1.4, 1.0), (-0.0, 1.4, 1.0), 0.09, "copper_dark", seg=16)
    cyl((0.02, 1.4, 1.0), (0.08, 1.4, 1.0), 0.12, "brass", seg=16)
    cyl((0.25, 1.4, 1.0), (0.05, 1.4, 1.0), 0.07, "copper", seg=16)
    # the flue up from the top
    cyl((1.0, 2.6, 1.0), (1.0, 3.0, 1.0), 0.14, "iron_dark", seg=20)
    lathe((1.0, 2.6, 1.0), [(0, 0.2), (0.06, 0.2)], "iron_dark", seg=20)


@prop("bath_tub", 2, 1, 1)
def bath_tub():
    """An oval oak tub with iron hoops, full of steaming water, a towel over its rim."""
    o = lathe((1.0, 0.0, 0.5), [(0.0, 0.42), (0.05, 0.46), (0.62, 0.48), (0.66, 0.46)], "wood", seg=40)
    stretch(o, (1.0, 0.0, 0.5), 2.0, 1.0)
    w = lathe((1.0, 0.1, 0.5), [(0.0, 0.41), (0.62, 0.42)], "x", seg=40)
    stretch(w, (1.0, 0.0, 0.5), 2.0, 1.0)
    cut(w)
    s = lathe((1.0, 0.1, 0.5), [(0.0, 0.41), (0.42, 0.42)], "water_hot", seg=40)
    stretch(s, (1.0, 0.0, 0.5), 2.0, 1.0)
    for y in (0.1, 0.5):
        h = lathe((1.0, y, 0.5), [(0, 0.475), (0.05, 0.48)], "iron_dark", seg=40)
        stretch(h, (1.0, 0.0, 0.5), 2.0, 1.0)
    for k in range(24):                                                             # staves
        a = 2 * math.pi * k / 24
        x, z = 1.0 + math.cos(a) * 0.95, 0.5 + math.sin(a) * 0.475
        box(x - 0.012, 0.02, z - 0.012, x + 0.012, 0.64, z + 0.012, "wood_dark", bevel=0.0)
    box(1.55, 0.45, 0.02, 1.75, 0.68, 0.12, "towel", bevel=0.02)                    # towel over the rim
    box(1.55, 0.6, 0.02, 1.75, 0.7, 0.3, "towel", bevel=0.02)


@prop("towel_bench", 2, 1, 1)
def towel_bench():
    """A slatted oak bench with folded towels, a bucket and a ladle."""
    for x in (0.15, 1.85):
        box(x - 0.08, 0.0, 0.2, x + 0.08, 0.4, 0.8, "wood_dark", bevel=0.015)
    for k in range(4):
        z = 0.18 + k * 0.165
        box(0.05, 0.4, z, 1.95, 0.46, z + 0.14, "wood", bevel=0.012)
    for k in range(3):                                                              # folded towels
        col = ("towel", "towel_blue", "towel")[k]
        box(0.2, 0.46 + k * 0.08, 0.25, 0.75, 0.53 + k * 0.08, 0.75, col, bevel=0.03)
    o = bowl((1.4, 0.46, 0.5), [(0, 0.16), (0.32, 0.2)], 0.03, "wood", seg=24)
    lathe((1.4, 0.49, 0.5), [(0, 0.15), (0.22, 0.17)], "water", seg=24)
    for y in (0.52, 0.72):
        lathe((1.4, 0.46 + y - 0.46, 0.5), [(0, 0.19 + (y - 0.52) * 0.18), (0.03, 0.19 + (y - 0.52) * 0.18)], "iron_dark", seg=24)
    cyl((1.4, 0.75, 0.5), (1.72, 1.0, 0.5), 0.015, "wood")
    ball((1.4, 0.72, 0.5), (0.06, 0.03, 0.06), "copper", seg=12)


@prop("steam_brazier", 1, 2, 1)
def steam_brazier():
    """A bronze tripod brazier with coals under a copper bowl of herbs and water: the steam room's heat."""
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.5
        cyl((0.5 + math.cos(a) * 0.35, 0.0, 0.5 + math.sin(a) * 0.35), (0.5 + math.cos(a) * 0.16, 0.7, 0.5 + math.sin(a) * 0.16), 0.03, "brass")
        ball((0.5 + math.cos(a) * 0.36, 0.03, 0.5 + math.sin(a) * 0.36), 0.05, "brass", seg=10)
    bowl((0.5, 0.65, 0.5), [(0, 0.12), (0.08, 0.26), (0.18, 0.3)], 0.03, "iron_dark", seg=28)
    rnd = random.Random(5)
    for _ in range(14):
        ball((0.5 + rnd.uniform(-0.18, 0.18), 0.8, 0.5 + rnd.uniform(-0.18, 0.18)), 0.05, "coals_glow" if rnd.random() < 0.6 else "coal", seg=8)
    for k in range(3):
        a = 2 * math.pi * k / 3
        cyl((0.5 + math.cos(a) * 0.26, 0.82, 0.5 + math.sin(a) * 0.26), (0.5 + math.cos(a) * 0.2, 1.02, 0.5 + math.sin(a) * 0.2), 0.02, "brass")
    bowl((0.5, 1.0, 0.5), [(0, 0.1), (0.06, 0.24), (0.14, 0.28)], 0.025, "copper", seg=28)
    lathe((0.5, 1.03, 0.5), [(0, 0.2), (0.07, 0.24)], "water_hot", seg=24)
    for k in range(5):
        a = 2 * math.pi * k / 5
        ellip((0.5 + math.cos(a) * 0.12, 1.11, 0.5 + math.sin(a) * 0.12), (0.05, 0.012, 0.025), "herb", rot=(0, math.degrees(a), 0), seg=8)


@prop("bath_plant", 1, 2, 1)
def bath_plant():
    """A glazed blue pot with a tall fern."""
    lathe((0.5, 0, 0.5), [(0, 0.18), (0.05, 0.24), (0.35, 0.3), (0.48, 0.27), (0.52, 0.3), (0.56, 0.3)], "tile_blue", seg=28)
    lathe((0.5, 0.0, 0.5), [(0.52, 0.27), (0.54, 0.27)], "soil", seg=24)
    rnd = random.Random(8)
    for k in range(11):
        a = 2 * math.pi * k / 11 + rnd.uniform(-0.2, 0.2)
        L = rnd.uniform(0.55, 0.9)
        pts = []
        for j in range(5):
            t = j / 4
            r = 0.05 + t * L * 0.55
            pts.append((0.5 + math.cos(a) * r, 0.56 + t * L * 0.9 - t * t * L * 0.35, 0.5 + math.sin(a) * r))
        for j in range(4):
            caps(pts[j], pts[j + 1], 0.04 - j * 0.006, 0.034 - j * 0.006, "leaf" if k % 3 else "leaf_dark", seg=8)


# ================================================================ the mage tower and school

@prop("arcane_orrery", 3, 3, 3, V=12)
def arcane_orrery():
    """A great brass orrery: a clawed tripod, a glowing sun at its heart, three tilted rings with their worlds."""
    c = (1.5, 1.55, 1.5)
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.3
        tube_pts = [(1.5 + math.cos(a) * 1.2, 0.0, 1.5 + math.sin(a) * 1.2), (1.5 + math.cos(a) * 0.9, 0.35, 1.5 + math.sin(a) * 0.9),
                    (1.5 + math.cos(a) * 0.25, 0.8, 1.5 + math.sin(a) * 0.25)]
        caps(tube_pts[0], tube_pts[1], 0.07, 0.06, "brass")
        caps(tube_pts[1], tube_pts[2], 0.06, 0.05, "brass")
        ball(tube_pts[0], 0.09, "brass_dark", seg=12)
    lathe((1.5, 0.75, 1.5), [(0, 0.12), (0.1, 0.2), (0.16, 0.08), (0.75, 0.05)], "brass_dark", seg=24)
    ball(c, 0.3, "sun_glow", seg=28)
    rings = [(0.62, (0.3, 1, 0.1), "brass", "world_blue", 0.4), (0.92, (-0.25, 1, 0.35), "brass_dark", "world_red", 2.2),
             (1.25, (0.15, 1, -0.4), "brass", "crystal", 4.0)]
    for R, nrm, mat, world, a in rings:
        torus(c, R, 0.035, mat, normal=nrm, seg=64, tseg=8)
        n = Vector(nrm).normalized()
        up = Vector((0, 1, 0)) if abs(n.y) < 0.9 else Vector((1, 0, 0))
        u = n.cross(up).normalized()
        v = n.cross(u).normalized()
        p = Vector(c) + (u * math.cos(a) + v * math.sin(a)) * R
        ball(tuple(p), 0.13, world, seg=18)
        if world == "world_red":
            torus(tuple(p), 0.2, 0.015, "gold", normal=(0.3, 1, 0.2), seg=28, tseg=6)
    cyl((1.5, 0.95, 1.5), (1.5, 2.85, 1.5), 0.025, "brass_dark", seg=10)   # the axis
    ball((1.5, 2.88, 1.5), 0.06, "gold", seg=12)


@prop("crystal_pylon", 1, 3, 1)
def crystal_pylon():
    """A rune-banded stone pedestal with a great violet crystal floating over it, three shards circling."""
    lathe((0.5, 0, 0.5), [(0, 0.45), (0.12, 0.45), (0.16, 0.36), (0.9, 0.3), (0.95, 0.38), (1.05, 0.42), (1.1, 0.42)], "stone_pale", seg=8)
    for y in (0.35, 0.65):
        lathe((0.5, y, 0.5), [(0, 0.335), (0.05, 0.335)], "rune_glow", seg=8)
    bowl((0.5, 1.1, 0.5), [(0, 0.2), (0.12, 0.36)], 0.04, "silver", seg=24)
    crystal((0.5, 1.95, 0.5), 1.1, 0.2, "crystal", tilt=(4, 20, 3))
    for k in range(3):
        a = 2 * math.pi * k / 3
        crystal((0.5 + math.cos(a) * 0.36, 1.75 + k * 0.18, 0.5 + math.sin(a) * 0.36), 0.28, 0.06, "crystal",
                tilt=(15 * math.cos(a), math.degrees(a), 15 * math.sin(a)))


@prop("crystal_crown", 7, 3, 7, V=8)
def crystal_crown():
    """The tower's crown: a slowly turning ring of great shards round one floating heart-crystal, over a silver
    ring with runes. Sits on the tower's top platform."""
    torus((3.5, 0.25, 3.5), 3.0, 0.12, "silver", seg=96, tseg=10)
    torus((3.5, 0.25, 3.5), 2.75, 0.06, "rune_glow", seg=96, tseg=8)
    for k in range(10):
        a = 2 * math.pi * k / 10
        x, z = 3.5 + math.cos(a) * 3.0, 3.5 + math.sin(a) * 3.0
        crystal((x, 1.15 + 0.35 * math.sin(3 * a), z), 1.3 + 0.3 * (k % 2), 0.22, "crystal", tilt=(12 * math.sin(a), math.degrees(a), -12 * math.cos(a)))
    crystal((3.5, 1.6, 3.5), 2.2, 0.45, "crystal", tilt=(0, 15, 0))
    for k in range(4):
        a = 2 * math.pi * k / 4 + 0.6
        crystal((3.5 + math.cos(a) * 0.9, 1.0, 3.5 + math.sin(a) * 0.9), 0.6, 0.12, "crystal_cyan", tilt=(20 * math.cos(a), 0, 20 * math.sin(a)))


@prop("alchemy_table", 2, 2, 1)
def alchemy_table():
    """An alchemist's bench: a copper alembic over a little burner, flasks of glowing tinctures, a mortar and pestle,
    an open grimoire and candles."""
    box(0.0, 0.78, 0.05, 2.0, 0.86, 0.95, "wood_dark", bevel=0.015)
    for x in (0.1, 1.9):
        for z in (0.15, 0.85):
            box(x - 0.05, 0.0, z - 0.05, x + 0.05, 0.78, z + 0.05, "wood_dark", bevel=0.01)
    box(0.08, 0.15, 0.1, 1.92, 0.2, 0.9, "wood", bevel=0.01)                   # lower shelf
    for k in range(5):
        flask(0.25 + k * 0.33, 0.2, 0.5, 0.06, 0.25, ("potion_red", "potion_green", "potion_blue", "potion_violet", "potion_red")[k])
    # the alembic: a burner, a copper pot, its helm and the arm down to a receiver
    cyl((0.45, 0.86, 0.5), (0.45, 0.94, 0.5), 0.1, "iron_dark")
    ellip((0.45, 0.97, 0.5), (0.03, 0.05, 0.03), "flame_blue", seg=8)
    for k in range(3):
        a = 2 * math.pi * k / 3
        cyl((0.45 + math.cos(a) * 0.14, 0.86, 0.5 + math.sin(a) * 0.14), (0.45 + math.cos(a) * 0.12, 1.06, 0.5 + math.sin(a) * 0.12), 0.012, "iron_dark")
    lathe((0.45, 1.04, 0.5), [(0, 0.06), (0.05, 0.14), (0.16, 0.15), (0.24, 0.1), (0.3, 0.05)], "copper", seg=24)
    lathe((0.45, 1.34, 0.5), [(0, 0.05), (0.06, 0.08), (0.12, 0.07), (0.17, 0.02)], "copper_dark", seg=20)
    caps((0.52, 1.44, 0.5), (0.95, 1.12, 0.5), 0.022, 0.018, "copper")
    flask(1.0, 0.86, 0.5, 0.08, 0.28, "potion_green")
    # the grimoire, open, with a glowing sigil on its page
    box(1.2, 0.86, 0.3, 1.75, 0.9, 0.72, "leather_red", bevel=0.01, rot=(0, -8, 0))
    box(1.22, 0.9, 0.32, 1.47, 0.93, 0.7, "paper", bevel=0.01, rot=(0, -8, -4))
    box(1.48, 0.9, 0.32, 1.73, 0.93, 0.7, "paper", bevel=0.01, rot=(0, -8, 4))
    box(1.55, 0.932, 0.42, 1.66, 0.936, 0.58, "rune_glow", bevel=0.0, rot=(0, -8, 4))
    # mortar and pestle, candles, a skull
    bowl((1.85, 0.86, 0.25), [(0, 0.06), (0.1, 0.09)], 0.02, "stone_pale", seg=16)
    cyl((1.85, 0.9, 0.25), (1.92, 1.05, 0.28), 0.015, "stone_pale", seg=8)
    candle(1.85, 0.86, 0.75, 0.16)
    candle(1.92, 0.86, 0.65, 0.1)
    ellip((0.15, 0.95, 0.2), (0.08, 0.09, 0.1), "bone", seg=14)
    ball((0.12, 0.96, 0.12), 0.02, "coal", seg=6)
    ball((0.18, 0.96, 0.12), 0.02, "coal", seg=6)


@prop("arcane_lectern", 1, 2, 1)
def arcane_lectern():
    """A carved lectern holding an open spellbook whose runes float up off the page."""
    box(0.25, 0.0, 0.25, 0.75, 0.08, 0.75, "wood_dark", bevel=0.02)
    lathe((0.5, 0.08, 0.5), [(0, 0.1), (0.1, 0.08), (0.2, 0.1), (0.6, 0.07), (0.7, 0.1), (0.8, 0.08)], "wood", seg=12)
    box(0.15, 0.88, 0.2, 0.85, 0.96, 0.8, "wood_dark", bevel=0.015, rot=(-22, 0, 0))
    box(0.18, 0.95, 0.24, 0.49, 0.99, 0.76, "paper", bevel=0.01, rot=(-22, 0, -4))
    box(0.51, 0.95, 0.24, 0.82, 0.99, 0.76, "paper", bevel=0.01, rot=(-22, 0, 4))
    box(0.17, 0.92, 0.22, 0.83, 0.95, 0.78, "leather_blue", bevel=0.01, rot=(-22, 0, 0))
    rnd = random.Random(21)
    for k in range(9):                                                            # floating glyphs
        x, y, z = 0.25 + rnd.uniform(0, 0.5), 1.1 + k * 0.07, 0.4 + rnd.uniform(-0.1, 0.15)
        box(x, y, z, x + 0.06, y + 0.06, z + 0.012, "rune_glow", bevel=0.0, rot=(0, rnd.uniform(-30, 30), 0))


@prop("brass_telescope", 2, 3, 2)
def brass_telescope():
    """A great brass telescope on an oak tripod, tilted at the sky, with its finder scope and eyepiece."""
    top = (1.0, 1.25, 1.0)
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.4
        cyl((1.0 + math.cos(a) * 0.8, 0.0, 1.0 + math.sin(a) * 0.8), top, 0.04, "wood")
        box(1.0 + math.cos(a) * 0.8 - 0.05, 0.0, 1.0 + math.sin(a) * 0.8 - 0.05, 1.0 + math.cos(a) * 0.8 + 0.05, 0.06,
            1.0 + math.sin(a) * 0.8 + 0.05, "brass_dark", bevel=0.01)
    lathe(top, [(-0.1, 0.1), (0.05, 0.12), (0.12, 0.06)], "brass_dark", seg=20)
    a, b = (0.35, 1.0, 1.55), (1.75, 2.6, 0.35)
    cyl(a, b, 0.11, "brass", r2=0.16, seg=28)
    cyl(b, tuple(Vector(b) + (Vector(b) - Vector(a)).normalized() * 0.08), 0.18, "brass_dark", seg=28)
    for t in (0.25, 0.55, 0.8):
        p = Vector(a) + (Vector(b) - Vector(a)) * t
        cyl(tuple(p), tuple(p + (Vector(b) - Vector(a)).normalized() * 0.05), 0.12 + 0.05 * t, "brass_dark", seg=28)
    cyl(tuple(Vector(a) - (Vector(b) - Vector(a)).normalized() * 0.15), a, 0.05, "brass_dark", seg=16)   # eyepiece
    fa = Vector(a) + (Vector(b) - Vector(a)) * 0.3 + Vector((0.0, 0.18, 0.1))
    cyl(tuple(fa), tuple(fa + (Vector(b) - Vector(a)) * 0.35), 0.04, "brass", seg=14)


@prop("celestial_globe", 1, 2, 1)
def celestial_globe():
    """A star globe in a brass meridian ring on a turned stand."""
    lathe((0.5, 0, 0.5), [(0, 0.3), (0.06, 0.28), (0.12, 0.12), (0.6, 0.06), (0.7, 0.12), (0.76, 0.1)], "wood_dark", seg=16)
    c = (0.5, 1.18, 0.5)
    ball(c, 0.34, "world_star", seg=32)
    torus(c, 0.38, 0.025, "brass", normal=(1, 0, 0.2), seg=48, tseg=8)
    torus(c, 0.4, 0.02, "brass_dark", normal=(0, 1, 0), seg=48, tseg=8)
    for s in (-1, 1):
        cyl((0.5, 1.18 + s * 0.36, 0.5), (0.5, 1.18 + s * 0.44, 0.5), 0.02, "brass")
    cyl((0.5, 0.76, 0.5), (0.5, 0.8, 0.5), 0.04, "brass")


@prop("rune_circle", 5, 1, 5)
def rune_circle():
    """A summoning circle inlaid in the floor: silver rings with glowing glyphs between them and a star inside."""
    c = (2.5, 0.0, 2.5)
    for R, mat in ((2.3, "silver"), (2.0, "rune_glow"), (1.4, "silver"), (0.5, "rune_glow")):
        torus((2.5, 0.0, 2.5), R, 0.045, mat, seg=96, tseg=8)
    for k in range(16):                                                           # glyphs between the outer rings
        a = 2 * math.pi * k / 16
        x, z = 2.5 + math.cos(a) * 2.15, 2.5 + math.sin(a) * 2.15
        L = 0.12 if k % 2 else 0.08
        box(x - L, -0.03, z - 0.02, x + L, 0.04, z + 0.02, "rune_glow", bevel=0.0, rot=(0, -math.degrees(a) + 90, 0))
        box(x - 0.02, -0.03, z - L * 0.6, x + 0.02, 0.04, z + L * 0.6, "rune_glow", bevel=0.0, rot=(0, -math.degrees(a) + 90, 0))
    pts = [(2.5 + math.cos(-math.pi / 2 + 2 * math.pi * k / 7) * 1.38, 2.5 + math.sin(-math.pi / 2 + 2 * math.pi * k / 7) * 1.38) for k in range(7)]
    for k in range(7):                                                            # the seven-pointed star
        p, q = pts[k], pts[(k + 2) % 7]
        cyl((p[0], 0.0, p[1]), (q[0], 0.0, q[1]), 0.04, "rune_glow", seg=8)


@prop("rune_target", 1, 2, 1)
def rune_target():
    """A spell target: a straw bale on a post, scorched, with a glowing ward sigil pinned on its face."""
    box(0.44, 0.0, 0.44, 0.56, 1.0, 0.56, "wood_dark", bevel=0.01)
    box(0.25, 0.0, 0.3, 0.75, 0.06, 0.7, "wood_dark", bevel=0.01)
    cyl((0.5, 1.3, 0.25), (0.5, 1.3, 0.75), 0.42, "straw", seg=32)
    for z in (0.3, 0.7):
        torus((0.5, 1.3, z), 0.42, 0.02, "rope", normal=(0, 0, 1), seg=32, tseg=6)
    torus((0.5, 1.3, 0.24), 0.28, 0.025, "rune_glow", normal=(0, 0, 1), seg=36, tseg=6)
    torus((0.5, 1.3, 0.24), 0.14, 0.025, "rune_glow", normal=(0, 0, 1), seg=24, tseg=6)
    ball((0.5, 1.3, 0.24), 0.04, "rune_glow", seg=10)
    rnd = random.Random(3)
    for _ in range(4):                                                            # scorch marks
        a, r = rnd.uniform(0, 6.28), rnd.uniform(0.1, 0.38)
        ellip((0.5 + math.cos(a) * r, 1.3 + math.sin(a) * r, 0.245), (0.025, 0.025, 0.008), "coal", seg=8)


@prop("scroll_shelf", 2, 3, 1)
def scroll_shelf():
    """A tall wizard's bookcase: rows of tomes, a rack of scrolls, a crystal ball, a skull and candles."""
    box(0.0, 0.0, 0.05, 0.08, 2.9, 1.0, "wood_dark", bevel=0.01)
    box(1.92, 0.0, 0.05, 2.0, 2.9, 1.0, "wood_dark", bevel=0.01)
    box(0.0, 0.0, 0.92, 2.0, 2.9, 1.0, "wood", bevel=0.005)
    box(-0.03, 2.82, 0.0, 2.03, 2.95, 1.0, "wood_dark", bevel=0.015)
    rnd = random.Random(14)
    cols = ("leather_red", "leather_blue", "leather", "leather_green", "leather_violet", "leather")
    for i, y in enumerate((0.0, 0.7, 1.4, 2.1)):
        box(0.05, y, 0.05, 1.95, y + 0.06, 0.95, "wood_dark", bevel=0.008)
        x = 0.1
        if i == 1:                                                                # a scroll rack
            while x < 1.8:
                cyl((x + 0.06, y + 0.1, 0.12), (x + 0.06, y + 0.1, 0.9), 0.05, "paper", seg=12)
                cyl((x + 0.06, y + 0.2, 0.12), (x + 0.06, y + 0.2, 0.9), 0.05, "paper", seg=12)
                x += 0.13
            continue
        if i == 3:
            ball((0.5, y + 0.2, 0.5), 0.15, "crystal_cyan", seg=20)
            lathe((0.5, y + 0.06, 0.5), [(0, 0.12), (0.06, 0.08)], "brass_dark", seg=16)
            ellip((1.0, y + 0.16, 0.5), (0.09, 0.1, 0.11), "bone", seg=14)
            candle(1.5, y + 0.06, 0.4, 0.2)
            candle(1.62, y + 0.06, 0.55, 0.14)
            x = 1.75
        while x < 1.85:
            w = rnd.uniform(0.06, 0.11)
            h = rnd.uniform(0.42, 0.6)
            lean = 0 if rnd.random() < 0.85 else 10
            book(x, y + 0.06, 0.2, w, h, rnd.uniform(0.55, 0.7), rnd.choice(cols))
            x += w + 0.01


@prop("arcane_brazier", 1, 2, 1)
def arcane_brazier():
    """An iron brazier burning with cold violet witch-fire."""
    for k in range(3):
        a = 2 * math.pi * k / 3
        caps((0.5 + math.cos(a) * 0.32, 0.0, 0.5 + math.sin(a) * 0.32), (0.5 + math.cos(a) * 0.12, 0.8, 0.5 + math.sin(a) * 0.12), 0.035, 0.03, "iron_dark")
    torus((0.5, 0.4, 0.5), 0.22, 0.02, "iron_dark", seg=24, tseg=6)
    bowl((0.5, 0.78, 0.5), [(0, 0.1), (0.08, 0.28), (0.2, 0.34)], 0.03, "iron_dark", seg=28)
    for k in range(8):
        a = 2 * math.pi * k / 8
        crystal((0.5 + math.cos(a) * 0.36, 1.0, 0.5 + math.sin(a) * 0.36), 0.12, 0.03, "iron_dark", tilt=(25 * math.cos(a), 0, 25 * math.sin(a)))
    rnd = random.Random(6)
    for k in range(7):
        a, r = rnd.uniform(0, 6.28), rnd.uniform(0, 0.15)
        ellip((0.5 + math.cos(a) * r, 1.1 + rnd.uniform(0, 0.15), 0.5 + math.sin(a) * r), (0.07, 0.2, 0.07), "witchfire", seg=10)


def _finger(pts, rs, stone, knuckle=True):
    """A stone finger along pts, thinning by rs, a knuckle at each joint."""
    for k in range(len(pts) - 1):
        caps(pts[k], pts[k + 1], rs[k], rs[k + 1], stone, seg=18)
        if knuckle and 0 < k:
            ball(pts[k], rs[k] * 1.12, stone, seg=14)


def _hand(s, stone, rune):
    """One of the two great hands, s = -1 the west one, 1 the east: a forearm out of the dais, a broad palm turned in,
    four fingers rising and curling over the fire, a thumb low across the front."""
    cx = 4.5
    def X(v):
        return cx + s * v
    caps((X(3.3), -0.2, 3.4), (X(3.0), 1.6, 3.4), 0.95, 0.78, stone, seg=24)            # the forearm
    torus((X(3.2), 0.75, 3.4), 0.92, 0.1, "bronze_dark", normal=(0.08 * s, 1, 0))         # its bronze bracers
    torus((X(3.1), 1.25, 3.4), 0.86, 0.08, "bronze_dark", normal=(0.08 * s, 1, 0))
    ellip((X(2.85), 2.3, 3.4), (0.62, 0.95, 1.2), stone, rot=(0, 0, -14 * s), seg=24)     # the palm
    ellip((X(2.42), 1.95, 2.3), (0.42, 0.55, 0.42), stone, seg=16)                        # the heel of the thumb
    for k, (z, reach, th) in enumerate(((2.45, 5.75, 0.27), (3.05, 6.2, 0.3), (3.72, 6.3, 0.3), (4.35, 5.8, 0.26))):
        lean = 0.28 * (z - 3.4)                                                            # fans out, front to back
        pts = [(X(2.72), 3.0, z), (X(3.05), reach * 0.72, z + lean * 0.5), (X(2.65), reach * 0.9, z + lean * 0.9),
               (X(1.72), reach, z + lean * 1.1), (X(1.05), reach - 0.5, z + lean)]
        _finger(pts, (th * 1.15, th * 1.05, th * 0.92, th * 0.8, th * 0.55), stone)
        for j in (1, 2):                                                                  # a rune across each joint
            a, b = Vector(pts[j]), Vector(pts[j + 1])
            mid = a.lerp(b, 0.5)
            ball((mid.x + s * 0.2, mid.y + 0.06, mid.z), 0.1, rune, seg=8)
    _finger([(X(2.4), 1.95, 2.25), (X(2.05), 2.25, 1.65), (X(1.45), 2.35, 1.4), (X(0.95), 2.15, 1.4)], (0.32, 0.29, 0.25, 0.17), stone)
    for y in (0.4, 0.95, 1.5):                                                            # rune strokes up the forearm
        box(X(3.2) - 0.07, y, 2.48, X(3.2) + 0.07, y + 0.3, 2.56, rune, bevel=0.0)
        box(X(3.2) - 0.16, y + 0.12, 2.48, X(3.2) + 0.16, y + 0.17, 2.56, rune, bevel=0.0)


def _cold_forge(lit):
    """The Cold Forge, older than Highmourn: two colossal stone hands risen through a round dais, cupped round a stone
    bowl, their fingertips nearly meeting over it; before them the low altar the work lies on. Dead, its runes are
    soot-black and its bowl is ash. Lit, the runes run molten and the bowl holds a fire."""
    stone, dark, rune = "stone", "stone_dark", "molten" if lit else "coal"
    cx, cz = 4.5, 3.4
    lathe((cx, 0, cz), [(0, 4.45), (0.16, 4.45), (0.2, 4.2), (0.36, 4.2), (0.4, 3.85), (0.56, 3.85), (0.56, 0)], dark, seg=56)
    for k in range(24):                                                                  # the ring of runes on the dais
        a = 2 * math.pi * k / 24
        x, z = cx + math.cos(a) * 4.02, cz + math.sin(a) * 4.02
        if k % 2:
            box(x - 0.1, 0.34, z - 0.1, x + 0.1, 0.42, z + 0.1, rune, bevel=0.0)
        else:
            box(x - 0.04, 0.34, z - 0.16, x + 0.04, 0.42, z + 0.16, rune, bevel=0.0, rot=(0, 0, 0))
    # the bowl on its stem, between the palms
    cyl((cx, 0.5, cz), (cx, 0.7, cz), 1.1, stone, r2=0.95, seg=40)
    cyl((cx, 0.7, cz), (cx, 1.2, cz), 0.62, stone, r2=0.5, seg=36)
    cyl((cx, 1.2, cz), (cx, 1.75, cz), 0.5, stone, r2=1.5, seg=44)
    cyl((cx, 1.75, cz), (cx, 2.25, cz), 1.5, stone, r2=1.86, seg=44)
    torus((cx, 2.2, cz), 1.83, 0.09, "bronze_dark", normal=(0, 1, 0), seg=56)
    cut(lathe((cx, 2.05, cz), [(-0.5, 0.0), (-0.42, 0.9), (0, 1.56), (0.6, 1.62), (0.6, 0)], stone, seg=36))
    if lit:
        ellip((cx, 1.72, cz), (1.5, 0.3, 1.5), "molten", seg=28)
        rnd = random.Random(11)
        for k in range(16):                                                               # tongues of fire, not a ball of it
            a, r = rnd.uniform(0, 6.28), 0.2 + 1.1 * (k / 16) ** 0.5
            h = rnd.uniform(0.7, 1.5) * (1.3 - r * 0.6)
            x, z = cx + math.cos(a) * r, cz + math.sin(a) * r
            sway = (-math.cos(a) * 0.14, -math.sin(a) * 0.14)
            mid = (x + sway[0], 1.95 + h * 0.55, z + sway[1])
            caps((x, 1.8, z), mid, 0.2, 0.11, "flame", seg=10)
            caps(mid, (x + sway[0] * 2.4, 1.95 + h * 1.1, z + sway[1] * 2.4), 0.11, 0.015, "flame", seg=10)
    else:
        ellip((cx, 1.68, cz), (1.5, 0.22, 1.5), "coal", seg=28)
        rnd = random.Random(5)
        for k in range(14):
            a, r = rnd.uniform(0, 6.28), rnd.uniform(0.1, 1.25)
            ball((cx + math.cos(a) * r, 1.86, cz + math.sin(a) * r), rnd.uniform(0.06, 0.14), "stone_dark", seg=8)
    for s in (-1, 1):
        _hand(s, stone, rune)
    # the altar before the bowl, worn hollow where the work lies
    box(cx - 1.5, 0.5, 0.0, cx + 1.5, 0.72, 1.3, dark, bevel=0.04)
    box(cx - 1.32, 0.72, 0.1, cx + 1.32, 0.96, 1.2, stone, bevel=0.05)
    box(cx - 1.42, 0.96, 0.02, cx + 1.42, 1.1, 1.28, dark, bevel=0.03)
    for k in range(-2, 3):
        box(cx + k * 0.46 - 0.07, 0.76, 0.08, cx + k * 0.46 + 0.07, 0.92, 0.12, rune, bevel=0.0)
    # old breaks: a chipped fingertip's worth of age, the dais split
    cut(box(cx - 3.4, 0.2, 7.0, cx - 3.1, 0.7, 7.4, stone, bevel=0.0, rot=(0, 20, 0)))
    cut(box(cx + 2.3, 0.3, 0.3, cx + 2.5, 0.7, 1.1, stone, bevel=0.0, rot=(0, 25, 0)))


@prop("cold_forge", 9, 7, 8, V=12)
def cold_forge():
    _cold_forge(False)


@prop("cold_forge_lit", 9, 7, 8, V=12)
def cold_forge_lit():
    _cold_forge(True)


# ================================================================ sampling

def voxelize(name, w, h, d, V):
    """Parts fill in the order they were made (a later part paints over an earlier one); a cut carves away what was
    made before it, not what comes after (a coal bed laid into a carved tray)."""
    mats, vox = [], {}
    thr = 0.32 / V

    def span(lo, hi):
        # Blender (x, y, z) -> game (x, z, -y)
        return (range(max(0, math.floor(lo.x * V) - 1), min(w * V, math.ceil(hi.x * V) + 1)),
                range(max(0, math.floor(lo.z * V) - 1), min(h * V, math.ceil(hi.z * V) + 1)),
                range(max(0, math.floor(-hi.y * V) - 1), min(d * V, math.ceil(-lo.y * V) + 1)))
    for ob, mat in KS.PARTS:
        if mat == "x":
            continue
        t, lo, hi, _, _ = KS.bvh_of(ob)
        xs, ys, zs = span(lo, hi)
        if mat == "~cut":
            for ix in xs:
                for iy in ys:
                    for iz in zs:
                        k = (ix, iy, iz)
                        if k in vox and KS.signed(t, G((ix + 0.5) / V, (iy + 0.5) / V, (iz + 0.5) / V)) < 0:
                            del vox[k]
            continue
        if mat not in mats:
            mats.append(mat)
        mi = mats.index(mat)
        for ix in xs:
            for iy in ys:
                for iz in zs:
                    if KS.signed(t, G((ix + 0.5) / V, (iy + 0.5) / V, (iz + 0.5) / V)) < thr:
                        vox[(ix, iy, iz)] = mi
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name + ".json"), "w") as f:
        json.dump({"name": name, "V": V, "size": [w, h, d], "mats": mats, "vox": [[*k, m] for k, m in vox.items()]}, f)
    print("%s: %d voxels, %d materials" % (name, len(vox), len(mats)))


def build(name):
    KS.reset()
    KS.PARTS.clear()
    KS.CUTS.clear()
    w, h, d, V, fn = PROPS[name]
    fn()
    voxelize(name, w, h, d, V)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for n in (args or list(PROPS)):
        build(n)
