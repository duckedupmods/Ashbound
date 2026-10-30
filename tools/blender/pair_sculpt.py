"""The angel and the devil at the valley's throat, sculpted as meshes in Blender and turned into blocks.

    blender -b -P tools/blender/pair_sculpt.py -- angel|devil [render] [novox]

Built the same way as the king (king_sculpt.py, whose shapes and voxelizer this uses): real 3D parts - feathers laid
in rows like a bird's (primaries, secondaries, tertials, two rows of coverts), a bat wing of finger bones with a
scalloped, torn membrane between them, ram horns curling round, muscles, a broken greatsword - sampled on the block
grid with ambient occlusion baked into each block. Both are built with the wing that reaches over the road on +x,
facing +z; the devil is mirrored when he's placed (capital_pair.py). Writes tools/renders/<who>_cells.json; with
"render", the smooth sculpt to E:/Ashbound/tools/renders/struct/<who>_sculpt_*.png.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import king_sculpt as KS  # noqa: E402
from king_sculpt import G, capsule, ellipsoid, lathe, mesh_obj, rbox, smooth, tube  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PRIO = {
    "angel": {"gilt": 9, "hair": 8, "skin": 7, "blade": 6, "robe": 4, "feather": 3},
    "devil": {"eye": 12, "vein": 11, "ember": 11, "tooth": 10, "horn": 9, "iron": 8, "hide": 6, "cloth": 5, "membrane": 3},
}
UNCUT = {"angel": ("gilt", "hair"), "devil": ("eye", "vein", "ember", "tooth")}


# ================================================================ more shapes

def leaf(name, base, dirv, length, hw, ht, nrm, part, cup=0.0, rings=12, seg=10):
    """A feather / spike / ear: narrow at the base, widest past a third, closing to a point; `nrm` is the side its
    flat face looks to, `cup` bends it that way toward the tip."""
    B, u = Vector(base), Vector(dirv).normalized()
    t = Vector(nrm)
    t = (t - u * t.dot(u)).normalized()
    w = u.cross(t)
    verts, faces = [], []
    for j in range(rings + 1):
        s = j / rings
        wid = hw * min(1.0, 0.4 + 1.8 * s) * math.sqrt(max(0.0, 1 - max(0.0, (s - 0.4) / 0.6) ** 2))
        wid = max(wid, 0.04)
        th = ht * (wid / hw) ** 0.5
        c = B + u * (s * length) + t * (cup * s * s * length)
        for i in range(seg):
            a = 2 * math.pi * i / seg
            verts.append(G(*(c + w * (wid * math.cos(a)) + t * (th * math.sin(a)))))
    for j in range(rings):
        for i in range(seg):
            a, b = j * seg + i, j * seg + (i + 1) % seg
            faces.append((a, b, b + seg, a + seg))
    cb, ct = len(verts), len(verts) + 1
    verts.append(sum(verts[:seg], Vector()) / seg)
    verts.append(sum(verts[rings * seg:rings * seg + seg], Vector()) / seg)
    for i in range(seg):
        faces.append((cb, (i + 1) % seg, i))
        faces.append((ct, rings * seg + i, rings * seg + (i + 1) % seg))
    return mesh_obj(name, verts, faces, part)


def sheet(name, grid, nrm, thick, part):
    """A thin closed solid through a grid of game points grid[i][j], `thick` across along nrm."""
    n = Vector(nrm).normalized()
    ni, nj = len(grid), len(grid[0])
    top = [G(*(Vector(p) + n * thick / 2)) for row in grid for p in row]
    bot = [G(*(Vector(p) - n * thick / 2)) for row in grid for p in row]
    off = len(top)

    def ix(i, j):
        return i * nj + j
    faces = []
    for i in range(ni - 1):
        for j in range(nj - 1):
            a, b, c, d = ix(i, j), ix(i + 1, j), ix(i + 1, j + 1), ix(i, j + 1)
            faces.append((a, b, c, d))
            faces.append((off + d, off + c, off + b, off + a))
    border = ([ix(i, 0) for i in range(ni)] + [ix(ni - 1, j) for j in range(1, nj)]
              + [ix(i, nj - 1) for i in range(ni - 2, -1, -1)] + [ix(0, j) for j in range(nj - 2, 0, -1)])
    for k in range(len(border)):
        a, b = border[k], border[(k + 1) % len(border)]
        faces.append((a, b, off + b, off + a))
    return mesh_obj(name, top + bot, faces, part)


def polyline(pts):
    P = [Vector(p) for p in pts]
    acc = [0.0]
    for a, b in zip(P, P[1:]):
        acc.append(acc[-1] + (b - a).length)

    def at(s):
        d = s * acc[-1]
        for k in range(len(P) - 1):
            if d <= acc[k + 1] or k == len(P) - 2:
                f = (d - acc[k]) / max(1e-6, acc[k + 1] - acc[k])
                return P[k].lerp(P[k + 1], max(0.0, min(1.0, f)))
    return at


def feathered(name, pts, nrm, groups, edge_r):
    """A bird's wing along the leading edge pts (root, elbow, wrist, hand): each group is a row of feathers
    (s0, s1, count, dir0, dir1, len0, len1, half-width, row), row 0 the flight feathers, 1 and 2 the coverts laid
    over their bases toward the viewer."""
    at = polyline(pts)
    n = Vector(nrm).normalized()
    tube(name + "_edge", pts, edge_r, "feather", seg=14)
    for g, (s0, s1, cnt, d0, d1, l0, l1, hw, row) in enumerate(groups):
        for k in range(cnt):
            f = k / (cnt - 1) if cnt > 1 else 0.0
            d = Vector(d0).lerp(Vector(d1), f).normalized()
            base = at(s0 + (s1 - s0) * f) + n * (row * 0.95 - (k % 2) * 0.45) - d * 0.6
            leaf("%s_f%d_%d" % (name, g, k), base, d, l0 + (l1 - l0) * f, hw, 0.55, n, "feather", cup=0.035)


def bat_wing(name, root, elbow, wrist, tips, body, nrm, holes):
    """A bat's wing: arm bones root-elbow-wrist, finger bones from the wrist to each tip, a membrane between them
    with a scalloped, ragged trailing edge, and holes torn through it."""
    R, E, W = Vector(root), Vector(elbow), Vector(wrist)
    T = [Vector(t) for t in tips]
    n = Vector(nrm).normalized()
    tube(name + "_arm", [R, E, W], [3.0, 2.4, 1.9], "hide", seg=16)
    for i, t in enumerate(T):
        mid = W.lerp(t, 0.45) + Vector((0, 1.0, 0)) + n * 0.4
        tube("%s_fin%d" % (name, i), [W, mid, t], [1.6, 1.1, 0.55], "hide", seg=12)
    NU, NV = 11, 15

    def edge(a, b, v, pull, seed):
        e = a.lerp(b, v)
        s = pull * (a - b).length * math.sin(math.pi * v) * (1 + 0.3 * math.sin(v * 19 + seed))
        return e, s
    for k in range(len(T) - 1):
        grid = []
        for i in range(NU):
            u = 0.06 + 0.94 * i / (NU - 1)
            row = []
            for j in range(NV):
                v = j / (NV - 1)
                e, s = edge(T[k], T[k + 1], v, 0.2, k * 3.1)
                e = e + (W - e).normalized() * s
                row.append(W + (e - W) * u + n * (1.3 * math.sin(math.pi * v) * u))
            grid.append(row)
        sheet("%s_mem%d" % (name, k), grid, n, 1.2, "membrane")
    # the panel between the arm and the last finger, down to the flank
    arm = polyline([R, E, W])
    B = Vector(body)
    grid = []
    for i in range(NU):
        u = i / (NU - 1)
        row = []
        for j in range(NV):
            v = 0.03 + 0.97 * j / (NV - 1)
            a = arm(v)
            e, s = edge(B, T[-1], v, 0.16, 7.7)
            e = e + (a - e).normalized() * s
            row.append(a.lerp(e, u) + n * (1.2 * math.sin(math.pi * u) * math.sin(math.pi * v)))
        grid.append(row)
    sheet(name + "_memarm", grid, n, 1.2, "membrane")
    for i, (c, r) in enumerate(holes):
        ellipsoid("%s_tear%d" % (name, i), c, r, "cut")


def surface_z(x, y):
    """Where a ray from the front first meets what's built so far (game z), or None."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    hit, loc, *_ = bpy.context.scene.ray_cast(dg, G(x, y, 80), Vector((0, 1, 0)), distance=200)
    return -loc.y if hit else None


# ================================================================ the angel

def angel():
    HY = 80.0
    # ---- the robe, the hem gilt, toes peeking out
    def robe(y, t):
        r = 9.0 + 4.6 * (1 - smooth(0, 46, y)) ** 1.4
        fold = (0.7 + 1.4 * (1 - smooth(4, 44, y))) * math.sin(11 * t + 0.5 * math.sin(2 * t))
        rr = r + fold
        return rr * math.cos(t), rr * math.sin(t) * 0.85 + 1.2 * (1 - smooth(0, 30, y))
    lathe("robe", [0.0, 0.8, 1.6] + [2 + i * 2 for i in range(23)] + [47.5], robe, "robe", n=128)
    lathe("hem", [0.0, 0.9, 2.0], lambda y, t: tuple(v * 1.03 for v in robe(y, t)), "gilt", n=128)
    for sx in (-1, 1):
        ellipsoid("toe", (sx * 3.6, 1.3, 12.6), (2.2, 1.5, 3.2), "skin")
        # gilt trims down the robe's front opening
        ta = math.pi / 2 + sx * 0.28
        tube("trim", [(robe(y, ta)[0] * 1.03, y, robe(y, ta)[1] * 1.03) for y in (46, 34, 22, 11, 2.5)], [0.75] * 5, "gilt", seg=10)

    # ---- the bodice, the cord at the waist, the capelet over the shoulders
    def bodice(y, t):
        rx = 8.6 + 2.0 * smooth(48, 62, y) - 4.2 * smooth(64, 73, y)
        rz = 6.4 + 1.6 * smooth(50, 61, y) - 2.6 * smooth(65, 73, y)
        x, z = rx * math.cos(t), rz * math.sin(t)
        if math.sin(t) > 0:
            z += 0.5 * math.sin(t) * math.sin(9 * t) * (1 - smooth(50, 60, y))
        return x, z
    lathe("bodice", [44 + i * 0.8 for i in range(37)], bodice, "robe", n=112)
    lathe("cord", [46.9, 47.7, 48.5], lambda y, t: (9.4 * math.cos(t), 7.1 * math.sin(t)), "gilt", n=96)
    tube("cordend", [(1.2, 47.4, 7.8), (2.0, 41, 9.6), (1.6, 33, 10.6)], [0.8, 0.7, 0.6], "gilt", seg=10)
    ellipsoid("tassel", (1.6, 31.6, 10.8), (1.3, 2.0, 1.3), "gilt")

    def cape(y, t):
        r = 12.4 - 4.8 * smooth(66, 75, y) + 0.55 * math.sin(14 * t) * (1 - smooth(61, 70, y))
        return r * math.cos(t), r * math.sin(t) * 0.74 - 0.4
    lathe("capelet", [59.0, 60.0] + [61 + i * 1.0 for i in range(15)], cape, "robe", n=112)
    lathe("capehem", [59.0, 60.2], lambda y, t: tuple(v * 1.02 for v in cape(y, t)), "gilt", n=112)
    capsule("neck", (0, 71, 0.4), (0, 77, 1.0), 2.6, 2.4, "skin")

    # ---- the head, calm, eyes cast down, under a deep hood with a halo disc behind
    ellipsoid("cranium", (0, HY + 1, 0.3), (4.8, 6.0, 5.4), "skin")
    ellipsoid("jaw", (0, HY - 2.4, 1.8), (3.9, 3.4, 4.0), "skin")
    capsule("brow", (-3.4, HY + 1.6, 4.7), (3.4, HY + 1.6, 4.7), 1.0, 1.0, "skin")
    capsule("nose", (0, HY + 1.0, 5.6), (0, HY - 1.8, 6.8), 0.8, 1.1, "skin")
    ellipsoid("lips", (0, HY - 3.0, 5.2), (1.6, 0.6, 0.8), "skin")
    ellipsoid("chin", (0, HY - 4.6, 4.4), (1.7, 1.2, 1.2), "skin")
    for sx in (-1, 1):
        ellipsoid("cheek", (sx * 3.0, HY - 0.6, 4.1), (1.5, 1.3, 1.4), "skin")
        ellipsoid("eye", (sx * 1.9, HY + 0.3, 5.8), (1.25, 0.85, 1.1), "cut")
        ellipsoid("lid", (sx * 1.9, HY - 0.05, 4.9), (1.15, 0.75, 0.8), "skin")
        # locks falling from the hood over the chest
        tube("lock", [(sx * 3.9, HY + 3, 3.6), (sx * 4.8, HY - 4, 3.4), (sx * 5.4, HY - 10, 4.6), (sx * 5.0, HY - 15, 6.8)],
             [1.3, 1.25, 1.1, 0.7], "hair", seg=12)
        tube("lock2", [(sx * 3.0, HY + 3.4, 4.2), (sx * 3.6, HY - 4.5, 4.4), (sx * 3.9, HY - 9.5, 5.8)],
             [0.9, 0.9, 0.6], "hair", seg=12)

    def hood(y, t):
        rr = 7.4 * math.sqrt(max(0.03, 1 - ((y - (HY + 0.5)) / 9.2) ** 2)) + 0.35 * math.sin(9 * t)
        rr += max(0.0, HY - 4 - y) * 0.9
        x, z = rr * math.cos(t), rr * math.sin(t) * 1.05 - 1.0
        return x, min(z, 2.6 + 0.2 * max(0.0, HY + 3 - y))
    lathe("hood", [HY - 9 + i * 0.75 for i in range(25)], hood, "robe", n=96)
    rim = []
    for i in range(29):
        a = -math.pi / 2 + 2 * math.pi * i / 28
        y = HY + 0.6 + 7.2 * math.sin(a)
        rim.append((5.9 * math.cos(a), y, 2.9 + 0.2 * max(0.0, HY + 3 - y)))
    tube("hoodrim", rim, [1.0] * len(rim), "robe", seg=10)
    HZ = -8.4
    ellipsoid("halo", (0, HY + 2, HZ), (10.6, 10.6, 0.6), "gilt", seg=64)
    ring = [(10.6 * math.cos(2 * math.pi * i / 40), HY + 2 + 10.6 * math.sin(2 * math.pi * i / 40), HZ + 0.4) for i in range(41)]
    tube("halorim", ring, [0.9] * len(ring), "gilt", seg=10)
    for k in range(16):
        a = 2 * math.pi * k / 16
        ln = 13.8 if k % 2 == 0 else 12.4
        capsule("ray%d" % k, (11.0 * math.cos(a), HY + 2 + 11.0 * math.sin(a), HZ),
                (ln * math.cos(a), HY + 2 + ln * math.sin(a), HZ), 0.85, 0.4, "gilt", seg=10, rings=3)

    # ---- arms in bell sleeves, the hands one over the other on the pommel
    for sx in (-1, 1):
        sh, el, wr = (sx * 10.4, 68.5, 0.0), (sx * 12.6, 57.0, 5.0), (sx * 3.2, 56.4, 13.4)
        capsule("upsleeve", sh, el, 2.9, 3.2, "robe")
        capsule("sleeve", el, wr, 3.1, 4.5, "robe")
        ellipsoid("drape", (sx * 7.6, 50.8, 10.2), (3.2, 5.4, 2.5), "robe", rot=(0, 0, sx * 22))
        p0, p1 = Vector(el).lerp(Vector(wr), 0.9), Vector(el).lerp(Vector(wr), 0.97)
        capsule("cuff", tuple(p0), tuple(p1), 4.6, 4.6, "gilt")
    rbox("hand_l", (-1.0, 55.5, 15.0), (2.7, 1.3, 2.6), "skin", bevel=0.9, rot=(0, 0, 12))
    rbox("hand_r", (0.9, 57.0, 15.3), (2.7, 1.3, 2.6), "skin", bevel=0.9, rot=(0, 0, -10))
    for i in range(4):
        fx = -1.3 + i * 1.45
        tube("finger%d" % i, [(fx, 57.6, 17.3), (fx + 0.1, 56.6, 18.4), (fx + 0.1, 55.0, 18.2)], [0.85, 0.8, 0.7], "skin", seg=10)
    tube("thumb", [(-1.8, 57.4, 13.2), (-3.0, 57.0, 15.0), (-3.2, 56.2, 16.6)], [0.95, 0.85, 0.75], "skin", seg=10)

    # ---- the sword, point down before her feet, its guard two small wings
    BZ = 15.4
    verts, faces = [], []
    for y, hw, ht in ((0.4, 0.2, 0.3), (3.6, 2.2, 0.8), (6.5, 2.5, 0.85), (44.0, 2.4, 0.85)):
        for (x, z) in ((-hw, 0), (0, ht), (hw, 0), (0, -ht)):
            verts.append(G(x, y, BZ + z))
    for j in range(3):
        for i in range(4):
            a, b = j * 4 + i, j * 4 + (i + 1) % 4
            faces.append((a, b, b + 4, a + 4))
    faces.append((0, 3, 2, 1))
    faces.append((12, 13, 14, 15))
    mesh_obj("blade", verts, faces, "blade")
    rbox("fuller", (0, 26, BZ + 0.9), (0.55, 16, 0.45), "cut", bevel=0.2)
    capsule("guard", (-3.2, 45.0, BZ), (3.2, 45.0, BZ), 1.4, 1.4, "gilt")
    for sx in (-1, 1):
        leaf("guardwing", (sx * 2.4, 45.0, BZ), (sx * 1.0, 0.5, 0), 8.5, 1.6, 0.8, (0, 0, 1), "gilt", cup=0.0)
    ellipsoid("gem", (0, 45.0, BZ + 1.2), (1.3, 1.3, 0.7), "gilt")
    capsule("grip", (0, 46.2, BZ), (0, 53.0, BZ), 1.3, 1.3, "robe")
    ellipsoid("pommel", (0, 53.8, BZ), (1.9, 1.5, 1.9), "gilt")

    # ---- the wings: the near one raised high and reaching out over the road, the far one lowered round her
    feathered("wing_in", [(4, 66, -7), (19, 86, -7), (35, 98, -3), (46, 101, 1)], (-0.12, 0.1, 1.0), [
        (0.02, 0.30, 6, (-0.15, -1, -0.1), (0.0, -1, 0), 14, 20, 2.2, 0),        # tertials
        (0.30, 0.74, 12, (0.02, -1, 0), (0.3, -1, 0.02), 21, 20, 2.3, 0),        # secondaries
        (0.74, 1.00, 10, (0.45, -1, 0.03), (1.0, -0.1, 0.1), 20, 29, 1.8, 0),    # primaries, the last the tip
        (0.04, 0.74, 16, (-0.1, -1, 0), (0.3, -1, 0), 10, 10, 2.4, 1),           # greater coverts
        (0.74, 0.98, 6, (0.45, -1, 0), (0.95, -0.2, 0.05), 11, 12, 2.2, 1),
        (0.05, 0.95, 18, (-0.05, -1, 0), (0.8, -0.6, 0), 5.5, 5.5, 2.2, 2),      # lesser coverts
    ], [2.6, 2.2, 1.8, 1.2])
    feathered("wing_out", [(-4, 66, -7), (-17, 80, -9), (-25, 66, -8), (-25, 52, -6)], (-0.5, 0.0, 1.0), [
        (0.02, 0.30, 6, (0.2, -1, -0.05), (0.25, -1, 0), 24, 30, 2.2, 0),
        (0.30, 0.72, 10, (0.3, -1, 0.05), (0.15, -1, 0.05), 34, 40, 2.3, 0),
        (0.72, 1.00, 8, (0.12, -1, 0.05), (0.02, -1, 0.06), 44, 48, 1.9, 0),
        (0.04, 0.96, 18, (0.25, -1, 0), (0.05, -1, 0), 11, 12, 2.4, 1),
        (0.05, 0.95, 16, (0.2, -1, 0), (0.05, -1, 0), 5.5, 5.5, 2.2, 2),
    ], [2.6, 2.2, 1.8, 1.4])


# ================================================================ the devil

def devil():
    # ---- goat legs, the near one forward as if he's stepping off, cloven hooves
    for sx, hip, knee, hock, hoof in ((1, (6.5, 38, 0), (9, 25, 9), (9, 11, 3), (9, 2.2, 9)),
                                      (-1, (-6.5, 38, 0), (-9, 24, 5), (-9, 10, -5), (-9, 2.2, 0))):
        capsule("thigh", hip, knee, 6.4, 4.0, "hide")
        capsule("shin", knee, hock, 3.9, 2.7, "hide")
        capsule("cannon", hock, (hoof[0], hoof[1] + 2.2, hoof[2] - 0.6), 2.5, 2.3, "hide")
        ellipsoid("hoof", hoof, (2.8, 2.0, 3.3), "horn")
        rbox("cleft", (hoof[0], hoof[1], hoof[2] + 2.4), (0.35, 2.4, 1.4), "cut", bevel=0.1)
        leaf("kneespike", knee, (0, 0.5, 1), 5.0, 1.2, 0.9, (1, 0, 0), "horn", cup=-0.05)
        leaf("hockspur", hock, (0, 0.2, -1), 4.0, 1.0, 0.8, (1, 0, 0), "horn")
        H, K = Vector(hip), Vector(knee)
        for ring_i, f in enumerate((0.25, 0.55, 0.85)):           # shaggy goat fur round the thigh, in three tiers
            c = H.lerp(K, f)
            rr = 6.0 - 1.8 * f
            for q in range(9):
                a = 2 * math.pi * (q + 0.5 * ring_i) / 9
                out = Vector((math.cos(a), 0, math.sin(a)))
                leaf("fur", c + out * (rr - 0.6), out * 0.45 + Vector((0, -1, 0)), 8.0 - ring_i, 1.9, 0.7, out, "hide", cup=0.06)
        Kc = Vector(hock)
        for q in range(7):                                         # and a ruff at the hock
            a = 2 * math.pi * q / 7
            out = Vector((math.cos(a), 0, math.sin(a)))
            leaf("ruff", Kc + out * 2.2 + Vector((0, 1.5, 0)), out * 0.5 + Vector((0, -1, 0)), 4.5, 1.3, 0.6, out, "hide", cup=0.06)

    # ---- hips, a belt of iron with a skull, a ragged loincloth
    ellipsoid("pelvis", (0, 40, 0), (9.0, 6.0, 7.0), "hide")
    lathe("belt", [39.0, 40.2, 41.4, 42.4], lambda y, t: (9.8 * math.cos(t), 7.8 * math.sin(t) + 0.3), "iron", n=96)
    ellipsoid("skull", (0, 40.2, 8.6), (2.6, 2.8, 2.0), "tooth")
    for sx in (-1, 1):
        ellipsoid("skullsocket", (sx * 1.0, 40.8, 10.2), (0.9, 0.8, 0.9), "eye")
    for i, x in enumerate((-3.6, 0.2, 3.8)):
        leaf("cloth_f%d" % i, (x, 39.5, 8.4 - abs(x) * 0.25), (0.05 * x, -1, 0.2), 19 + (i % 2) * 4, 2.3, 0.5, (0, 0.1, 1), "cloth", cup=0.04)
    for i, x in enumerate((-4.5, 0, 4.5)):
        leaf("cloth_b%d" % i, (x, 39.5, -6.8), (0.05 * x, -1, -0.25), 20 - (i % 2) * 3, 2.6, 0.5, (0, 0.1, -1), "cloth", cup=0.04)

    # ---- the torso, hunched forward: belly, ribcage, chest, the hump of muscle behind the neck
    ellipsoid("belly", (0, 48, 3), (7.6, 8.2, 6.2), "hide", rot=(20, 0, 0))
    ellipsoid("ribs", (0, 60, 6), (11.5, 10.0, 8.5), "hide", rot=(25, 0, 0))
    for sx in (-1, 1):
        ellipsoid("pec", (sx * 5.2, 63, 12.4), (6.0, 4.2, 3.0), "hide", rot=(25, 0, sx * 8))
        for k, (y, z) in enumerate(((44.5, 9.0), (48.2, 9.6), (52.0, 10.4))):
            ellipsoid("ab", (sx * 2.3, y, z), (2.3, 1.6, 1.3), "hide")
        ellipsoid("oblique", (sx * 7.6, 50, 4.5), (2.4, 6.0, 3.6), "hide", rot=(20, 0, -sx * 10))
        ellipsoid("delt", (sx * 14.6, 69.0, 6.0), (5.2, 6.0, 5.4), "hide", rot=(0, 0, -sx * 20))
    ellipsoid("hump", (0, 71, 2), (13.0, 6.5, 8.0), "hide", rot=(30, 0, 0))
    capsule("neck", (0, 68, 8), (0, 71, 13), 4.6, 3.9, "hide")

    # ---- the cracks in his chest, burning: a heart of light at the sternum, veins of magma out from it
    veins = [[(0, 64), (0.8, 61.5), (-0.4, 59), (0.5, 56.5), (0, 54)],
             [(0.8, 61.5), (3.5, 63), (6, 62.4), (8.2, 64.5)],
             [(-0.4, 59), (-3.2, 60.5), (-5.5, 59.6), (-8, 61.4)],
             [(0.5, 56.5), (3.4, 55), (5.2, 52.5)],
             [(-0.2, 63.5), (-2.6, 66), (-4.6, 66.8)],
             [(0, 54), (-2.4, 51.5), (-3.0, 48.6)],
             [(3.5, 63), (4.2, 66.5)]]
    for i, path in enumerate(veins):
        pts = []
        for x, y in path:
            z = surface_z(x, y)
            if z is not None:
                pts.append((x, y, z - 0.25))
        if len(pts) >= 2:
            tube("vein%d" % i, pts, [0.8] * len(pts), "vein", seg=10)
    zc = surface_z(0, 60.5)
    ellipsoid("heart", (0, 60.5, (zc or 13) - 0.7), (1.7, 2.6, 1.3), "eye")
    for i in range(6):                                            # spines down the back between the wings
        y, z = (73, 68, 63, 58, 53, 48)[i], (-5.5, -5.8, -4.0, -3.4, -2.4, -2.6)[i]
        leaf("spine%d" % i, (0, y, z), (0, 0.45, -1), 6.2 - i * 0.6, 1.4, 1.0, (1, 0, 0), "horn")

    # ---- the head, thrust forward and low between the shoulders
    ellipsoid("cranium", (0, 74.5, 13.5), (5.6, 5.8, 6.4), "hide")
    capsule("brow", (-4.6, 75.6, 18.8), (4.6, 75.6, 18.8), 1.6, 1.6, "hide")
    for sx in (-1, 1):
        capsule("browv", (0, 74.8, 20.0), (sx * 4.4, 76.8, 18.6), 1.3, 1.2, "hide")
        ellipsoid("cheekbone", (sx * 4.2, 72.6, 17.6), (1.9, 1.4, 1.8), "hide")
        ellipsoid("socket", (sx * 2.4, 74.1, 20.3), (1.5, 1.0, 1.4), "cut")
        ellipsoid("eye", (sx * 2.4, 74.0, 19.5), (1.1, 0.75, 0.9), "eye")
        ellipsoid("nostril", (sx * 1.1, 70.9, 22.2), (0.9, 0.7, 0.8), "hide")
        leaf("ear", (sx * 5.2, 74.0, 13.0), (sx * 1.0, 0.35, -0.5), 7.0, 1.6, 0.6, (0, 0.3, 1), "hide")
        leaf("fang", (sx * 2.2, 69.7, 21.4), (0, -1, 0.1), 3.2, 0.75, 0.6, (0, 0, 1), "tooth")
        leaf("lowfang", (sx * 1.5, 67.6, 20.6), (0, 1, 0.15), 2.4, 0.6, 0.5, (0, 0, 1), "tooth")
        for k in range(3):                                         # a crown of small horns along the brow
            leaf("browhorn", (sx * (2.0 + k * 1.5), 78.0, 17.4 - k * 1.2), (sx * 0.2, 1, -0.6), 3.2 + k, 0.9, 0.8,
                 (0, 0, 1), "horn")
    ellipsoid("snout", (0, 70.6, 19.6), (3.6, 2.8, 3.6), "hide")
    capsule("nose", (0, 73.5, 21.0), (0, 71.0, 22.6), 1.1, 1.5, "hide")
    ellipsoid("jaw", (0, 67.2, 17.0), (4.6, 2.6, 4.4), "hide")
    ellipsoid("mouth", (0, 69.0, 21.2), (3.0, 1.0, 2.0), "cut")
    ellipsoid("maw", (0, 69.0, 19.6), (2.8, 0.9, 2.0), "vein")
    leaf("goatee", (0, 65.6, 19.0), (0, -1, 0.3), 6.0, 1.5, 0.9, (0, 0.2, 1), "horn")
    # the horns: up from the temples high over the head, back, then curling down and round to point forward
    for sx in (-1, 1):
        ctrl = [Vector((sx * x, y, z)) for x, y, z in ((4.6, 78.5, 14.5), (7.5, 85.5, 12.5), (11.0, 91.5, 8.0), (14.5, 93.0, 2.5),
                                                       (18.0, 89.0, -1.0), (19.5, 83.0, 1.0), (18.5, 78.5, 5.0), (16.5, 78.5, 10.0),
                                                       (14.8, 81.0, 13.0))]
        pts = []
        for i in range(len(ctrl) - 1):                           # Catmull-Rom through the control points
            p0, p1, p2, p3 = ctrl[max(0, i - 1)], ctrl[i], ctrl[i + 1], ctrl[min(len(ctrl) - 1, i + 2)]
            for q in range(5):
                t = q / 5
                pts.append(tuple(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                                        + (3 * p1 - p0 - 3 * p2 + p3) * t ** 3)))
        pts.append(tuple(ctrl[-1]))
        N = len(pts) - 1
        rad = [(3.9 - 3.3 * (i / N)) * (1 + 0.1 * math.sin(i * 2.3)) for i in range(N + 1)]
        tube("horn", pts, rad, "horn", seg=14)

    # ---- the near arm reaching, claws open; the far one holding the broken greatsword
    sh, el, wr = (15.5, 68, 6), (23, 52, 12), (22, 43, 25)
    capsule("uparm_r", sh, el, 5.0, 3.9, "hide")
    ellipsoid("bicep_r", Vector(sh).lerp(Vector(el), 0.5) + Vector((0, 0, 2.4)), (3.6, 6.5, 3.4), "hide", rot=(-20, 0, 25))
    capsule("forearm_r", el, wr, 4.9, 3.1, "hide")
    for k in range(3):
        leaf("armspike", Vector(el).lerp(Vector(wr), 0.15 + k * 0.25) + Vector((1.5, 1.2, -0.5)), (0.4, 0.5, -1), 5.0 - k, 1.1, 0.8,
             (1, 0, 0), "horn")
    ellipsoid("palm", (22, 41.2, 27.6), (3.4, 2.2, 3.0), "hide")
    for i in range(4):
        sxp = (i - 1.5)
        k0 = Vector((22 + sxp * 1.8, 40.6, 29.4))
        k1 = k0 + Vector((sxp * 0.6, -2.0, 3.0))
        k2 = k1 + Vector((sxp * 0.4, -3.5, 1.6))
        tube("claw%d" % i, [k0, k1, k2], [1.0, 0.85, 0.65], "hide", seg=10)
        leaf("talon%d" % i, k2, (0, -1, 0.35), 3.4, 0.7, 0.6, (0, 0.3, 1), "tooth")
    tube("thumb", [(19.2, 41.6, 26.0), (17.8, 39.0, 28.4), (17.8, 36.6, 29.4)], [1.2, 1.0, 0.75], "hide", seg=10)
    leaf("thumbtalon", (17.8, 36.6, 29.4), (0, -1, 0.3), 3.0, 0.7, 0.6, (0, 0, 1), "tooth")

    sh, el, wr = (-15.5, 68, 6), (-24, 52, 4), (-26, 40, 9)
    capsule("uparm_l", sh, el, 5.0, 3.9, "hide")
    ellipsoid("bicep_l", Vector(sh).lerp(Vector(el), 0.5) + Vector((0, 0, 2.2)), (3.6, 6.5, 3.4), "hide", rot=(-10, 0, -25))
    capsule("forearm_l", el, wr, 4.9, 3.3, "hide")
    for k in range(3):
        leaf("armspike_l", Vector(el).lerp(Vector(wr), 0.15 + k * 0.25) + Vector((-1.6, 1.2, -0.6)), (-0.4, 0.5, -1), 5.0 - k, 1.1, 0.8,
             (1, 0, 0), "horn")
    F = Vector((-26, 37, 10.5))
    rbox("fist", tuple(F), (3.2, 3.4, 3.2), "hide", bevel=1.2)
    for i in range(4):
        capsule("knuckle%d" % i, (-24.6, 39.4 - i * 1.5, 13.6), (-27.4, 39.4 - i * 1.5, 13.8), 0.8, 0.8, "hide", seg=10, rings=3)
    # the sword: dragged, the blade broken off a third of the way down, a burning crack through what's left
    a = Vector((-0.18, -1, 0.25)).normalized()
    w = a.cross(Vector((0, 0, 1))).normalized()
    if w.x < 0:
        w = -w
    th = a.cross(w).normalized()
    if th.z < 0:
        th = -th
    guard = F + a * 4.2
    L = 33.0
    verts, faces = [], []
    rings = [(0.6, 3.4, 0.95), (3.0, 3.6, 1.0), (26.0, 3.3, 0.95)]
    for s, hw, ht in rings:
        c = guard + a * s
        for (u, v) in ((-hw, 0), (0, ht), (hw, 0), (0, -ht)):
            verts.append(G(*(c + w * u + th * v)))
    for s, (u, v) in zip((L - 3.2, L - 0.4, L, L - 1.6), ((-3.2, 0), (0, 0.9), (3.2, 0), (0, -0.9))):   # the jagged break
        verts.append(G(*(guard + a * s + w * u + th * v)))
    for j in range(3):
        for i in range(4):
            p, q = j * 4 + i, j * 4 + (i + 1) % 4
            faces.append((p, q, q + 4, p + 4))
    faces.append((0, 3, 2, 1))
    faces.append((12, 13, 14, 15))
    mesh_obj("blade", verts, faces, "iron")
    crack = []
    for i in range(12):
        s = 2.5 + i * (L - 5.0) / 11
        crack.append(tuple(guard + a * s + w * (0.9 * math.sin(i * 2.1)) + th * 0.75))
    tube("crack", crack, [0.6] * len(crack), "ember", seg=8)
    tube("crack2", [crack[5], tuple(Vector(crack[5]) + w * 2.2 + a * 1.5 + th * 0.0)], [0.5, 0.4], "ember", seg=8)
    capsule("guard", tuple(guard - w * 4.0), tuple(guard + w * 4.0), 1.5, 1.5, "iron")
    for sg in (-1, 1):
        leaf("quillon", tuple(guard + w * sg * 3.6), tuple(w * sg + a * 0.7), 6.5, 1.3, 1.0, tuple(th), "iron", cup=0.06)
    ellipsoid("guardgem", tuple(guard + th * 1.3), (1.2, 1.2, 0.8), "eye")
    capsule("grip", tuple(F - a * 5.0), tuple(guard), 1.4, 1.4, "iron")
    pom = F - a * 6.0
    ellipsoid("pommel", tuple(pom), (2.0, 1.8, 2.0), "iron")
    leaf("pommelspike", tuple(pom - a * 1.2), tuple(-a), 3.6, 1.0, 0.9, (0, 0, 1), "iron")
    # the broken-off point lying flat on the plinth by his hoof
    tip, dirv = Vector((-11.0, 1.0, 21.0)), Vector((-1, 0, 0.35)).normalized()
    side = dirv.cross(Vector((0, 1, 0))).normalized()
    verts = []
    for s, hw in ((0.0, 3.2), (2.0, 3.2), (9.5, 0.2)):
        c = tip + dirv * s
        for (u, v) in ((-hw, 0), (0, 0.9), (hw, 0), (0, -0.9)):
            verts.append(G(*(c + side * u + Vector((0, v, 0)))))
    faces = [(j * 4 + i, j * 4 + (i + 1) % 4, j * 4 + (i + 1) % 4 + 4, j * 4 + i + 4) for j in range(2) for i in range(4)]
    faces += [(0, 3, 2, 1), (8, 9, 10, 11)]
    mesh_obj("shard", verts, faces, "iron")
    tube("shardcrack", [tuple(tip + dirv * 0.6 + Vector((0, 0.8, 0))), tuple(tip + dirv * 4.5 + side * 0.7 + Vector((0, 0.8, 0)))],
         [0.5, 0.4], "ember", seg=8)

    # ---- the tail, curling round the plinth to the front, a spade at its tip
    tube("tail", [(0, 38, -6), (0, 33, -12), (-5, 22, -17), (-14, 10, -17), (-22, 3, -9), (-20, 2.2, 3), (-13, 2.2, 10)],
         [3.6, 3.2, 2.8, 2.4, 2.0, 1.6, 1.2], "hide", seg=14)
    leaf("spade", (-13.5, 2.2, 9.6), (0.6, 0, 1), 5.5, 2.6, 0.7, (0, 1, 0), "hide")

    # ---- the wings: the near one up and over the road, the far one folded tall behind him like a cloak
    bat_wing("wing_in", (6, 71, -5), (22, 90, -9), (39, 101, -7),
             [(78, 98, -5), (70, 80, -6), (58, 64, -7), (44, 56, -7)], (9, 50, -4), (0, 0.05, 1),
             [((56, 88, -5), (2.6, 1.8, 3.0)), ((57, 70, -6), (2.2, 3.0, 3.0)), ((27, 66, -6), (2.0, 2.8, 3.0))])
    bat_wing("wing_out", (-6, 71, -5), (-19, 88, -10), (-24, 99, -12),
             [(-31, 30, -13), (-27, 22, -11), (-21, 26, -9), (-15, 38, -7)], (-9, 50, -4), (-0.4, 0.0, 1),
             [((-26, 45, -11), (1.8, 2.6, 3.0))])
    for sx, el, wrist in ((1, (22, 90, -9), (39, 101, -7)), (-1, (-19, 88, -10), (-24, 99, -12))):
        leaf("elbowspike", el, (sx * -0.2, 1, -0.3), 6.5, 1.3, 1.0, (0, 0, 1), "horn")
        leaf("wristclaw", wrist, (sx * 0.2, 0.7, 0.7), 4.5, 0.9, 0.8, (1, 0, 0), "horn", cup=0.1)
    leaf("tipclaw", (78, 98, -5), (1, -0.4, 0.1), 3.5, 0.7, 0.6, (0, 0, 1), "horn", cup=0.1)


# ================================================================ a look at the sculpt itself

COLS = {"skin": (0.86, 0.84, 0.8), "hair": (0.8, 0.79, 0.76), "robe": (0.72, 0.71, 0.68), "feather": (0.9, 0.9, 0.88),
        "blade": (0.82, 0.84, 0.88), "gilt": (0.85, 0.66, 0.25),
        "hide": (0.13, 0.12, 0.13), "horn": (0.28, 0.22, 0.18), "membrane": (0.22, 0.08, 0.06), "cloth": (0.17, 0.12, 0.1),
        "iron": (0.2, 0.21, 0.23), "tooth": (0.85, 0.82, 0.72), "eye": (1.0, 0.75, 0.3), "vein": (1.0, 0.35, 0.05),
        "ember": (1.0, 0.4, 0.05)}
SHOTS = {"angel": (("front", (12, 62, 175), (22, 64, 0), 30), ("face", (5, 82, 32), (0, 80, 0), 45),
                   ("three", (85, 60, 120), (18, 62, 0), 32), ("under", (58, 40, 45), (48, 95, 0), 26)),
         "devil": (("front", (12, 62, 175), (22, 64, 0), 30), ("face", (8, 74, 48), (0, 73, 15), 45),
                   ("three", (85, 55, 120), (15, 55, 0), 32), ("under", (58, 40, 45), (52, 92, 0), 26))}


def render_sculpt(who):
    sc = bpy.context.scene
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            pass
    sc.render.resolution_x, sc.render.resolution_y = 1000, 1100
    mats = {}
    for k, c in COLS.items():
        m = bpy.data.materials.new(k)
        m.use_nodes = True
        bs = m.node_tree.nodes["Principled BSDF"]
        bs.inputs["Base Color"].default_value = (*c, 1)
        bs.inputs["Roughness"].default_value = 0.6
        if k in ("eye", "vein", "ember"):
            bs.inputs["Emission Color"].default_value = (*c, 1)
            bs.inputs["Emission Strength"].default_value = 4.0
        mats[k] = m
    for ob, part in KS.PARTS:
        ob.data.materials.append(mats[part])
    for ob in KS.CUTS:
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
    cam.data.clip_end = 1000
    os.makedirs(KS.RENDERS, exist_ok=True)
    for name, eye, look, lens in SHOTS[who]:
        cam.location = G(*eye)
        d = G(*look) - G(*eye)
        cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lens
        sc.render.filepath = os.path.join(KS.RENDERS, "%s_sculpt_%s.png" % (who, name))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    who = args[0] if args else "angel"
    KS.reset()
    {"angel": angel, "devil": devil}[who]()
    print("pieces", len(KS.PARTS), "cuts", len(KS.CUTS))
    if "render" in args:
        render_sculpt(who)
    if "novox" not in args:
        KS.voxelize(out=os.path.join(HERE, "..", "renders", "%s_cells.json" % who), prio=PRIO[who], uncut=UNCUT[who])
