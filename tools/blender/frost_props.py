"""The Frozen Procession's props as real meshes (propkit.py does the baking and writing): snow drifted in the glacier's
hollows, and the procession's war banners frozen stiff on their poles.

  blender -b -P tools/blender/frost_props.py -- [preview] [fast] [names...]
    preview -> tools/renders/frost_props.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "propkit.py"), encoding="utf-8").read())

SNOW = mottled("frost_snow", [(0.0, (0.62, 0.68, 0.76)), (1.0, (0.86, 0.9, 0.95))], 10.0, 0.7)
RIME = mottled("frost_rime", [(0.0, (0.5, 0.62, 0.72)), (1.0, (0.78, 0.86, 0.92))], 30.0, 0.5)
CLOTH = mottled("banner_blue", [(0.0, (0.02, 0.05, 0.14)), (0.7, (0.05, 0.12, 0.3)), (1.0, (0.08, 0.16, 0.36))], 9.0, 0.8)
SIGIL = mottled("banner_silver", [(0.0, (0.45, 0.5, 0.55)), (1.0, (0.7, 0.74, 0.78))], 14.0, 0.5)
POLE = wood("banner_pole", [(0.0, (0.02, 0.015, 0.012)), (0.5, (0.05, 0.038, 0.028)), (1.0, (0.09, 0.07, 0.05))], along="Z")
IRON = rusty("frost_iron", iron=(0.05, 0.055, 0.06), rust=(0.2, 0.12, 0.08), amount=0.7, rough=0.45)


def snow_drift():
    """snow drifted into a hollow: a low wind-shaped mound, its crest sharp on one side"""
    bm = bmesh.new()
    n = 14
    grid = []
    for j in range(n + 1):
        row = []
        for i in range(n + 1):
            u, v = i / n - 0.5, j / n - 0.5
            r = math.sqrt(u * u + v * v) * 2
            h = max(0.0, 1 - r ** 2) * (0.14 + 0.06 * math.sin(u * 4 + 1)) + 0.012 * noise.noise(Vector((u * 6, v * 6, 2.0)))
            row.append(bm.verts.new(O + Vector((u * 0.98, v * 0.98, max(0.004, h)))))
        grid.append(row)
    for j in range(n):
        for i in range(n):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i])).material_index = 0
    return new_obj("snow_drift", bm, [SNOW])


def war_banner():
    """a war banner of the procession frozen stiff: an iron-shod pole, a crossbar, the blue cloth hanging in folds
    with a silver star sewn on it and a ragged hem, rime crusted along its top"""
    bm = bmesh.new()
    cyl(bm, O + Vector((0, -0.05, 0)), 0.035, 1.9, 0, seg=10)
    cyl(bm, O + Vector((0, -0.05, 1.9)), 0.05, 0.04, 1, seg=10)
    tube(bm, [O + Vector((0, -0.05, 1.94)), O + Vector((0, -0.05, 2.0))], lambda t: 0.04 * (1 - t) + 0.004, 1, sides=6)
    cyl(bm, O + Vector((-0.42, -0.05, 1.78)), 0.022, 0.84, 0, seg=8, axis="X")
    for x in (-0.42, 0.42):
        ellipsoid(bm, O + Vector((x, -0.05, 1.78)), (0.035, 0.035, 0.035), 1, seg=8)

    def at(u, v):
        x = (u - 0.5) * 0.78
        hem = 0.62 + 0.08 * abs(math.sin(u * 5 * math.pi)) * (1 if v > 0.9 else 0)
        z = 1.76 - v * (1.76 - hem)
        return O + Vector((x, 0.0 + 0.035 * math.sin(u * 4 * math.pi) * (0.3 + v), z))
    nu, nv = 16, 12
    top, bot = [], []
    for j in range(nv + 1):
        rt, rb = [], []
        for i in range(nu + 1):
            p = at(i / nu, j / nv)
            rt.append(bm.verts.new(p + Vector((0, 0.008, 0))))
            rb.append(bm.verts.new(p - Vector((0, 0.008, 0))))
        top.append(rt)
        bot.append(rb)
    for j in range(nv):
        for i in range(nu):
            u, v = (i + 0.5) / nu, (j + 0.5) / nv
            star = abs(u - 0.5) * 2.2 + abs(v - 0.42) * 2.2 < 0.35 + 0.12 * math.cos(math.atan2(v - 0.42, u - 0.5) * 4)
            m = 3 if star else 2
            bm.faces.new((top[j][i], top[j][i + 1], top[j + 1][i + 1], top[j + 1][i])).material_index = m
            bm.faces.new((bot[j][i], bot[j + 1][i], bot[j + 1][i + 1], bot[j][i + 1])).material_index = m
    tube(bm, [O + Vector((x, 0.0, 1.77)) for x in (-0.4, -0.2, 0.0, 0.2, 0.4)], 0.02, 4, sides=5)
    return new_obj("war_banner", bm, [POLE, IRON, CLOTH, SIGIL, RIME])


MAKE = [(snow_drift, (128, 128)), (war_banner, (256, 256))]
run(MAKE, GLOWS, "frost_props")
