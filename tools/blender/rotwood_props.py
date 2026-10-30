"""The Rotwood's props as real meshes (propkit.py does the baking and writing): glowcap clusters on the forest floor
and glowing brackets on the trunks, woody shelf fungus, the dead hunters' camp (a cold fire ring, a skull on a stake,
a root-bound coffer, gnarled rails).

  blender -b -P tools/blender/rotwood_props.py -- [preview] [fast] [names...]
    preview -> tools/renders/rotwood_props.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "propkit.py"), encoding="utf-8").read())

STEM = mottled("glow_stem", [(0.0, (0.3, 0.26, 0.3)), (1.0, (0.55, 0.5, 0.52))], 18.0, 0.7)
CAP = mottled("glow_cap", [(0.0, (0.18, 0.06, 0.32)), (0.6, (0.36, 0.14, 0.6)), (1.0, (0.5, 0.26, 0.78))], 7.0, 0.5)
GLOW = glass("glow_gills", (0.72, 0.42, 1.0), glow=4.0)
SPOT = glass("glow_spots", (0.85, 0.7, 1.0), glow=4.0)
SHELF = mottled("shelf", [(0.0, (0.12, 0.06, 0.025)), (0.5, (0.3, 0.15, 0.05)), (1.0, (0.5, 0.32, 0.12))], 22.0, 0.75)
SHELF_RIM = mottled("shelf_rim", [(0.0, (0.5, 0.42, 0.28)), (1.0, (0.72, 0.62, 0.42))], 30.0, 0.7)
BARK = wood("rot_bark", [(0.0, (0.02, 0.018, 0.017)), (0.5, (0.06, 0.055, 0.05)), (1.0, (0.13, 0.12, 0.11))], along="Z", grain=40)
BARK_X = wood("rot_bark_x", [(0.0, (0.02, 0.018, 0.017)), (0.5, (0.06, 0.055, 0.05)), (1.0, (0.13, 0.12, 0.11))], along="X", grain=40)
ROOT = wood("rot_root", [(0.0, (0.03, 0.022, 0.016)), (0.5, (0.08, 0.06, 0.042)), (1.0, (0.15, 0.115, 0.08))], along="X", grain=30)
MOSS = mottled("rot_moss", [(0.0, (0.07, 0.05, 0.08)), (1.0, (0.2, 0.15, 0.22))], 40.0, 0.95)
STONE = mottled("glade_stone", [(0.0, (0.07, 0.07, 0.075)), (0.6, (0.16, 0.16, 0.165)), (1.0, (0.26, 0.255, 0.25))], 6.0, 0.8)
CHAR = mottled("char", [(0.0, (0.01, 0.01, 0.01)), (1.0, (0.06, 0.05, 0.045))], 30.0, 0.9)
ASH = mottled("ash", [(0.0, (0.18, 0.18, 0.18)), (1.0, (0.36, 0.35, 0.34))], 25.0, 0.95)
BONE = mottled("bone", [(0.0, (0.35, 0.31, 0.24)), (0.6, (0.58, 0.53, 0.42)), (1.0, (0.7, 0.66, 0.55))], 14.0, 0.6)
HOLE = mat("hole", (0.01, 0.008, 0.008), 0.9)
ROPE = mottled("snare_rope", [(0.0, (0.15, 0.12, 0.07)), (1.0, (0.33, 0.27, 0.15))], 60.0, 0.95)
IRON = rusty("rot_iron", iron=(0.05, 0.05, 0.05), rust=(0.24, 0.1, 0.04), amount=0.5)
GLOWS.update({GLOW, SPOT})


def mushroom(bm, base, h, r, lean=(0.0, 0.0), seed=0):
    """a glowcap: a pale stem swelling at its foot, the domed cap glowing underneath, pale glowing spots on top"""
    top = base + Vector((lean[0], lean[1], h))
    pts = [base + (top - base) * t + Vector((0.02 * math.sin(t * 3 + seed), 0.0, 0.0)) for t in (k / 6 for k in range(7))]
    tube(bm, pts, lambda t: r * (0.32 - 0.1 * t) + r * 0.14 * (1 - t) ** 3, 0, sides=10)
    lathe(bm, [(0.0, 0.0), (r * 0.25, 0.0), (r * 0.95, 0.03 * r / 0.2), (r, 0.06 * r / 0.2)], top - Vector((0, 0, 0.02)), 2, 20, cap=False)
    cap = lathe(bm, [(r, 0.06 * r / 0.2), (r * 1.02, 0.1 * r / 0.2), (r * 0.85, 0.24 * r / 0.2), (r * 0.5, 0.33 * r / 0.2), (0.0, 0.36 * r / 0.2)],
                top - Vector((0, 0, 0.02)), 1, 20, cap=False)
    displace([v for rg in cap for v in rg], 0.012 * r / 0.2, 6.0, seed)
    for k in range(5):
        a = seed * 1.3 + k * 2.4
        rr = r * (0.3 + 0.12 * (k % 3))
        p = top + Vector((math.cos(a) * rr, math.sin(a) * rr, 0.3 * r / 0.2 - rr * 0.35))
        ellipsoid(bm, p, (0.02 * r / 0.2, 0.02 * r / 0.2, 0.01 * r / 0.2), 3, seg=8)


def glowcap_cluster():
    """a clump of glowcaps sprung from the threads: one tall, the rest crowding its foot"""
    bm = bmesh.new()
    for k, (x, y, h, r, lx, ly) in enumerate([(0.0, -0.05, 0.62, 0.2, 0.04, 0.02), (0.2, 0.12, 0.38, 0.14, 0.08, 0.04),
                                               (-0.2, 0.14, 0.3, 0.12, -0.07, 0.05), (0.14, -0.24, 0.22, 0.09, 0.05, -0.06),
                                               (-0.24, -0.18, 0.16, 0.07, -0.05, -0.03)]):
        mushroom(bm, O + Vector((x, y, 0)), h, r, (lx, ly), k + 1)
    return new_obj("glowcap_cluster", bm, [STEM, CAP, GLOW, SPOT])


def _bracket(bm, tiers, mi_top, mi_rim, mi_under=None):
    """bracket shelves growing out of the trunk at the back of the block (y=-1), tier upon tier"""
    for k, (x, z, w, d) in enumerate(tiers):
        c = Vector((x, -1.0, z))
        prof = []
        rings = []
        for j in range(9):   # a half-disc, thick at the trunk and thinning to its rim
            t = j / 8
            a = math.pi * t
            rings.append((math.cos(a) * w, math.sin(a) * d))
        top = [bm.verts.new(c + Vector((px, py, 0.05 * (1 - py / d) + 0.02))) for px, py in rings]
        mid = [bm.verts.new(c + Vector((px * 1.04, py * 1.04, 0.0))) for px, py in rings]
        bot = [bm.verts.new(c + Vector((px, py, -0.04 * (1 - py / d) - 0.005))) for px, py in rings]
        cen_t = bm.verts.new(c + Vector((0, 0, 0.07)))
        cen_b = bm.verts.new(c + Vector((0, 0, -0.045)))
        for j in range(8):
            bm.faces.new((cen_t, top[j + 1], top[j])).material_index = mi_top
            bm.faces.new((top[j], top[j + 1], mid[j + 1], mid[j])).material_index = mi_rim
            bm.faces.new((mid[j], mid[j + 1], bot[j + 1], bot[j])).material_index = mi_rim
            bm.faces.new((cen_b, bot[j], bot[j + 1])).material_index = mi_under if mi_under is not None else mi_top
        bm.faces.new((cen_t, top[0], mid[0], bot[0], cen_b)).material_index = mi_top
        bm.faces.new((cen_b, bot[8], mid[8], top[8], cen_t)).material_index = mi_top
        displace(top + mid, 0.01, 9.0, k)


def shelf_bracket():
    """woody shelf fungus on a trunk: three brown tiers ringed in pale growth, stepping down"""
    bm = bmesh.new()
    _bracket(bm, [(0.45, 0.72, 0.36, 0.5), (0.62, 0.45, 0.28, 0.38), (0.36, 0.22, 0.22, 0.3)], 0, 1)
    return new_obj("shelf_bracket", bm, [SHELF, SHELF_RIM])


def glow_bracket():
    """glowcap brackets on a trunk: purple shelves glowing from their gills beneath, a few small caps above"""
    bm = bmesh.new()
    _bracket(bm, [(0.5, 0.62, 0.32, 0.42), (0.3, 0.36, 0.22, 0.3)], 0, 0, 1)
    for k, (x, z) in enumerate([(0.62, 0.66), (0.42, 0.7), (0.26, 0.4)]):
        mushroom(bm, Vector((x, -0.8, z)), 0.12, 0.05, (0.02, 0.03), k)
    return new_obj("glow_bracket", bm, [CAP, GLOW, STEM, SPOT])


def dead_campfire():
    """the hunters' last fire, long cold: a ring of glade stones, charred logs fallen in, grey ash, a pot's tripod"""
    bm = bmesh.new()
    for k in range(9):
        a = k * 2 * math.pi / 9
        vs = ellipsoid(bm, O + Vector((math.cos(a) * 0.36, math.sin(a) * 0.36, 0.04)), (0.09, 0.075, 0.07), 0,
                       rot=Matrix.Rotation(a, 3, "Z"), seg=10)
        displace(vs, 0.015, 8.0, k)
    ellipsoid(bm, O + Vector((0, 0, -0.01)), (0.3, 0.3, 0.04), 2, seg=16)
    for k, (a, l) in enumerate([(0.3, 0.5), (1.9, 0.44), (3.6, 0.48), (5.0, 0.36)]):   # charred logs fallen in
        d = Vector((math.cos(a), math.sin(a), 0))
        c = O + Vector((0, 0, 0.06 + 0.035 * k))
        tube(bm, [c - d * l / 2, c, c + d * l / 2 + Vector((0, 0, 0.04))], 0.045, 1, sides=8)
    for k in range(3):   # the tripod
        a = k * 2 * math.pi / 3 + 0.5
        tube(bm, [O + Vector((math.cos(a) * 0.42, math.sin(a) * 0.42, 0.0)), O + Vector((0, 0, 0.82))], 0.018, 3, sides=5)
    links(bm, O + Vector((0, 0, 0.8)), O + Vector((0, 0, 0.5)), 4, w=0.04, r=0.01)
    tube(bm, ring(O + Vector((0, 0, 0.46)), 0.05, "Y", 12), 0.01, 4, sides=4, closed=True)
    return new_obj("dead_campfire", bm, [STONE, CHAR, ASH, BARK, IRON])


def skull(bm, c, s, mi_bone, mi_hole):
    """a stag's skull: long snout, eye holes, branching antlers"""
    vs = ellipsoid(bm, c, (0.1 * s, 0.13 * s, 0.09 * s), mi_bone, seg=14)
    displace(vs, 0.006 * s, 8.0, 3)
    tube(bm, [c + Vector((0, 0.06, -0.02)) * s, c + Vector((0, 0.24, -0.07)) * s], lambda t: (0.07 - 0.035 * t) * s, mi_bone, sides=8)
    for sx in (-1, 1):
        ellipsoid(bm, c + Vector((sx * 0.065, 0.07, 0.02)) * s, (0.03 * s, 0.03 * s, 0.03 * s), mi_hole, seg=8)
        base = c + Vector((sx * 0.06, -0.02, 0.07)) * s
        mid = base + Vector((sx * 0.14, -0.04, 0.16)) * s
        tip = mid + Vector((sx * 0.1, 0.02, 0.18)) * s
        tube(bm, [base, mid, tip], lambda t: (0.022 - 0.012 * t) * s, mi_bone, sides=6)
        for t, d in ((0.5, Vector((sx * 0.02, 0.12, 0.1))), (0.9, Vector((sx * 0.1, -0.06, 0.08)))):
            p = base.lerp(mid, t) if t < 0.6 else mid.lerp(tip, 0.4)
            tube(bm, [p, p + d * s], lambda q: 0.013 * s * (1 - 0.6 * q), mi_bone, sides=5)


def hunter_stake():
    """a sharpened stake driven into the loam, a stag's skull set on it, a snare cord wound under the skull"""
    bm = bmesh.new()
    vs = cyl(bm, O, 0.05, 0.62, 0, seg=8, r2=0.04)
    displace(vs, 0.008, 9.0, 1)
    skull(bm, O + Vector((0, 0.02, 0.68)), 1.0, 1, 2)
    for k in range(4):
        tube(bm, ring(O + Vector((0, 0, 0.5 + k * 0.025)), 0.055, "Z", 10, 0.1, k), 0.008, 3, sides=4, closed=True)
    tube(bm, [O + Vector((0.05, 0, 0.5)), O + Vector((0.12, 0.05, 0.35)), O + Vector((0.1, 0.08, 0.2))], 0.008, 3, sides=4)
    return new_obj("hunter_stake", bm, [BARK, BONE, HOLE, ROPE])


def rot_coffer():
    """a hunter's chest the forest has taken: old boards, roots grown over it and down into the ground, moss on the lid"""
    bm = bmesh.new()
    box(bm, O + Vector((-0.42, -0.3, 0.0)), O + Vector((0.42, 0.3, 0.5)), 0, bevel=0.02)
    vs = box(bm, O + Vector((-0.44, -0.32, 0.5)), O + Vector((0.44, 0.32, 0.6)), 0, bevel=0.025)
    displace(vs, 0.006, 8.0, 2)
    for x in (-0.3, 0.3):
        box(bm, O + Vector((x - 0.035, -0.31, 0.0)), O + Vector((x + 0.035, 0.31, 0.52)), 3, bevel=0.005)
    box(bm, O + Vector((-0.05, 0.3, 0.38)), O + Vector((0.05, 0.33, 0.52)), 3, bevel=0.006)
    for k in range(3):   # roots over it
        a = 0.6 + k * 1.9
        pts = [O + Vector((math.cos(a) * 0.6, math.sin(a) * 0.45, 0.0)), O + Vector((math.cos(a) * 0.46, math.sin(a) * 0.34, 0.45)),
               O + Vector((math.cos(a) * 0.2, math.sin(a) * 0.15, 0.63)), O + Vector((-math.cos(a) * 0.2, -math.sin(a) * 0.1, 0.62)),
               O + Vector((-math.cos(a) * 0.44, -math.sin(a) * 0.3, 0.3))]
        tube(bm, pts, lambda t: 0.04 * (1 - 0.6 * t), 1, sides=6)
    vs = ellipsoid(bm, O + Vector((0.1, -0.05, 0.6)), (0.26, 0.2, 0.03), 2, seg=12)
    displace(vs, 0.012, 10.0, 4)
    return new_obj("rot_coffer", bm, [BARK_X, ROOT, MOSS, IRON])


def rotwood_rail_post():
    """a gnarled stake of rotwood, a knot halfway up, its top split"""
    bm = bmesh.new()
    vs = cyl(bm, O, 0.085, 1.0, 0, seg=10, r2=0.07)
    displace(vs, 0.014, 6.0, 5)
    ellipsoid(bm, O + Vector((0.07, 0.02, 0.5)), (0.04, 0.05, 0.06), 0, seg=8)
    return new_obj("rotwood_rail_post", bm, [BARK])


def rotwood_rail_side():
    bm = bmesh.new()
    for z, s in ((0.38, 2), (0.82, 7)):
        pts = [Vector((0.5, -0.5 * t, z + 0.02 * math.sin(t * 5 + s))) for t in (k / 6 for k in range(7))]
        tube(bm, pts, 0.045, 0, sides=7)
    return new_obj("rotwood_rail_side", bm, [BARK_X])


MAKE = [(glowcap_cluster, (128, 128)), (glow_bracket, (128, 128)), (shelf_bracket, (128, 128)), (dead_campfire, (256, 256)),
        (hunter_stake, (128, 128)), (rot_coffer, (256, 256)), (rotwood_rail_post, (64, 64)), (rotwood_rail_side, (64, 64))]
run(MAKE, GLOWS, "rotwood_props")
