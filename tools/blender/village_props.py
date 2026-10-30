"""The villages' props as real meshes (propkit.py bakes and writes them, docs/VILLAGES.md): what moves (windmill sails,
the water wheel, the bell - drawn turning by a renderer in game), the carts and wagons, and the life round the houses.
Warm, worn, lived-in: grey-brown weathered wood, rusted iron tyres, sailcloth, straw.

  blender -b -P tools/blender/village_props.py -- [preview] [fast] [names...]
    preview -> tools/renders/village_props.png (+ village_props_big.png for the sails and the wheel)
1 unit = 1 block, the ground at z = 0, each prop's front looking along +y."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "propkit.py"), encoding="utf-8").read())


def lin(c):
    c = c.lstrip("#")
    return tuple(((int(c[i:i + 2], 16) / 255) ** 2.2) for i in (0, 2, 4))


def stops(*hs):
    n = len(hs) - 1
    return [(k / n, lin(h)) for k, h in enumerate(hs)]


WOOD = wood("vil_wood", stops("#4a3020", "#7a5634", "#9a7448"), "Z", 22.0)
WOODX = wood("vil_woodx", stops("#4a3020", "#7a5634", "#9a7448"), "X", 22.0)
WOODY = wood("vil_woody", stops("#4a3020", "#7a5634", "#9a7448"), "Y", 22.0)
GREY = wood("vil_grey", stops("#5a4a3a", "#806c58", "#a48e74"), "X", 26.0)       # weathered boards
DARK = wood("vil_dark", stops("#1e1610", "#33261a", "#4a3828"), "Z", 20.0)
IRON = rusty("vil_iron", (0.05, 0.048, 0.045), (0.30, 0.12, 0.05), 0.6)
CLOTH = mottled("vil_cloth", stops("#c4b496", "#ddd0b0", "#ece2c8"), 14.0, 0.85)
RED = mottled("vil_red", stops("#5a1410", "#8e2418", "#a83020"), 10.0, 0.8)
CREAM = mottled("vil_cream", stops("#c8b896", "#e0d4b4", "#ece4cc"), 10.0, 0.8)
BLUE = mottled("vil_blue", stops("#1c2c48", "#2e4670", "#46608a"), 10.0, 0.8)
GREEN = mottled("vil_green", stops("#1e3a1c", "#2e5428", "#4a7038"), 10.0, 0.8)
def straw_mat(name, st):
    """straw: wave bands warped by noise into a mess of strands, dark gaps between them"""
    m = mat(name, st[1][1], 0.9)
    w = node(m, "ShaderNodeTexWave", -700, 0)
    w.wave_type = "BANDS"
    w.bands_direction = "Y"
    w.inputs["Scale"].default_value = 18.0
    w.inputs["Distortion"].default_value = 14.0
    w.inputs["Detail"].default_value = 6.0
    w.inputs["Detail Scale"].default_value = 2.0
    link(m, coords(m, (1.0, 0.35, 1.0)), w.inputs["Vector"])
    link(m, ramp(m, w.outputs["Fac"], st), bsdf(m).inputs["Base Color"])
    return m


HAY = straw_mat("vil_hay", stops("#3a2a0a", "#7a5a1a", "#b08a34", "#d8bc66", "#b08a34"))
HAYX = mottled("vil_hayx", stops("#8a6a24", "#c4a24c", "#e4cc84"), 30.0, 0.9)
REED = wood("vil_reed", stops("#5a4a24", "#8a7438", "#b49a58"), "Z", 60.0, 0.9)
CORK = mottled("vil_cork", stops("#5a3a1c", "#8a5c2c", "#a8743a"), 18.0, 0.9)
FISH = mottled("vil_fish", stops("#3a3e3e", "#7a8484", "#b8c0bc"), 14.0, 0.4)
NET = mottled("vil_net", stops("#4a4232", "#6e6448", "#8a7e5c"), 30.0, 0.9)
WICKER = wood("vil_wicker", stops("#4a3218", "#7a5a2c", "#a07c44"), "Z", 50.0, 0.9)
LAMP = glass("vil_lamp", lin("#ffb54a"), 6.0)
STRAW = straw_mat("vil_straw", stops("#4a3610", "#8a6a28", "#b8944a", "#d4b46a"))
STONE = mottled("vil_stone", stops("#4e4c48", "#76736c", "#9a968c"), 5.0, 0.85)
ROPE = mottled("vil_rope", stops("#5c4a2c", "#86704a", "#a48c60"), 40.0, 0.9)
BRONZE = mat("vil_bronze", lin("#7a5a24"), 0.35, Metallic=1.0)
TIN = mat("vil_tin", lin("#9a9a94"), 0.4, Metallic=0.9)
APPLE = mottled("vil_apple", stops("#6a1008", "#a42014", "#c84a1c"), 12.0, 0.5)
CABBAGE = mottled("vil_cabbage", stops("#3a5a1c", "#6a8a34", "#9ab45a"), 9.0, 0.7)
SACK = mottled("vil_sack", stops("#7a6a4c", "#a08e68", "#bcac86"), 20.0, 0.95)
SHINGLE = mottled("vil_shingle", stops("#2e221a", "#4a3a2c", "#62503c"), 16.0, 0.85)


def V(x, y, z):
    return Vector((x, y, z))


def wheel(bm, c, r, w, axis="X", spokes=10, wood_mi=0, iron_mi=1):
    """a cart wheel: an iron tyre on a felloe of wood, turned spokes, a hub"""
    ax = {"X": (1, 0, 0), "Y": (0, 1, 0)}[axis]
    c = Vector(c)
    for rr, mi, th in ((r, iron_mi, 0.045), (r - 0.07, wood_mi, 0.06)):
        pts = [c + (V(0, math.cos(t), math.sin(t)) if axis == "X" else V(math.cos(t), 0, math.sin(t))) * rr
               for t in (k * 2 * math.pi / 32 for k in range(32))]
        tube(bm, pts, th if mi == wood_mi else w * 0.5, mi, sides=6, closed=True)
    cyl(bm, c - Vector(ax) * w * 0.9, r * 0.17, w * 1.8, wood_mi, seg=12, axis=axis)
    cyl(bm, c - Vector(ax) * w * 1.0, r * 0.09, w * 2.0, iron_mi, seg=10, axis=axis)
    for k in range(spokes):
        t = k * 2 * math.pi / spokes
        d = V(0, math.cos(t), math.sin(t)) if axis == "X" else V(math.cos(t), 0, math.sin(t))
        tube(bm, [c + d * r * 0.15, c + d * (r - 0.1)], lambda u: 0.035 - 0.012 * u, wood_mi, sides=6)


def sheet(bm, o, u, v, nu, nv, mi, bend=lambda a, b: V(0, 0, 0)):
    """a cloth or straw surface from corner o along u and v, bent per (a, b) in 0..1"""
    o, u, v = Vector(o), Vector(u), Vector(v)
    rows = [[bm.verts.new(o + u * (i / nu) + v * (j / nv) + bend(i / nu, j / nv)) for i in range(nu + 1)] for j in range(nv + 1)]
    for j in range(nv):
        for i in range(nu):
            bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i])).material_index = mi
    return rows


def thick(bm, rows, t, mi):
    """give a sheet a back face (so cloth reads from both sides in game)"""
    back = [[bm.verts.new(p.co + V(0, 0, 0)) for p in row] for row in rows]
    for j in range(len(rows) - 1):
        for i in range(len(rows[0]) - 1):
            bm.faces.new((back[j][i], back[j + 1][i], back[j + 1][i + 1], back[j][i + 1])).material_index = mi


def sack(bm, c, h, r, mi, rope_mi, seed, tilt=0.0, turn=0.0):
    """a grain sack: full belly, the neck gathered and tied, the mouth flaring over the tie; lying over by `tilt`"""
    before = set(bm.verts)
    prof = [(0.0, 0.0), (r * 0.75, 0.01), (r * 0.97, 0.12 * h), (r * 1.02, 0.45 * h), (r * 0.9, 0.72 * h), (r * 0.42, 0.88 * h),
            (r * 0.26, 0.95 * h), (r * 0.36, 1.03 * h), (r * 0.48, 1.1 * h), (0.0, 1.06 * h)]
    rings = lathe(bm, prof, V(0, 0, 0), mi, seg=16)
    vs = [v for rg in rings for v in rg]
    displace(vs, 0.025 * r / 0.25, 7.0, seed)
    tie = ring(V(0, 0, 0.93 * h), r * 0.3, "Z", 12)
    tube(bm, tie, 0.018, rope_mi, sides=4, closed=True)
    new = set(bm.verts) - before
    R = Matrix.Rotation(turn, 3, "Z") @ Matrix.Rotation(tilt, 3, "X")
    for v in new:
        v.co = R @ v.co + Vector(c)


def heap(bm, c, r, mi, seed, amt=0.12, scale=3.0):
    vs = ellipsoid(bm, c, r, mi, seg=20)
    displace(vs, amt, scale, seed)
    return vs


# ================================================================ what moves

def windmill_sails():
    """four sails 24 blocks across on their stocks: whips, sail bars, hemlaths, the cloth spread on the lattice; the
    windshaft's iron poll end in the middle. Drawn turning by its renderer (pivot at the origin)."""
    bm = bmesh.new()
    cyl(bm, V(0, -1.2, 0), 0.55, 1.4, 1, seg=16, axis="Y")                       # the poll end
    cyl(bm, V(0, 0.1, 0), 0.3, 0.35, 1, seg=12, axis="Y")
    for k in range(4):
        a = math.radians(45 + 90 * k)
        d, s = V(math.cos(a), 0, math.sin(a)), V(-math.sin(a), 0, math.cos(a))
        tube(bm, [d * 0.4, d * 12.2], lambda u: 0.22 - 0.08 * u, 0, sides=4)      # the whip
        for i in range(17):                                                      # sail bars across it
            r = 2.6 + i * 0.6
            tube(bm, [d * r - s * 0.2 + V(0, -0.15, 0), d * r + s * 2.9 + V(0, -0.15, 0)], 0.05, 0, sides=4)
        tube(bm, [d * 2.6 + s * 2.9 + V(0, -0.15, 0), d * 12.2 + s * 2.9 + V(0, -0.15, 0)], 0.07, 0, sides=4)  # hemlath
        tube(bm, [d * 2.6 + s * 0.9 + V(0, -0.15, 0), d * 12.2 + s * 0.9 + V(0, -0.15, 0)], 0.04, 0, sides=4)
        tube(bm, [d * 2.6 + s * 1.9 + V(0, -0.15, 0), d * 12.2 + s * 1.9 + V(0, -0.15, 0)], 0.04, 0, sides=4)
        rows = sheet(bm, d * 2.7 + s * 0.15, d * 9.3, s * 2.65, 12, 4, 2,
                     lambda a, b: V(0, -0.05 - 0.12 * math.sin(math.pi * b) * (0.6 + 0.4 * math.sin(math.pi * a)), 0))
        thick(bm, rows, 0.02, 2)
    return new_obj("windmill_sails", bm, [WOOD, IRON, CLOTH])


def water_wheel():
    """an undershot wheel 9 across: two rims on 12 spokes each side, 16 paddles between, the axle through a hub"""
    bm = bmesh.new()
    R, W = 4.4, 1.6
    for y in (-W / 2, W / 2):
        pts = [V(math.cos(t) * R, y, math.sin(t) * R) for t in (k * 2 * math.pi / 48 for k in range(48))]
        tube(bm, pts, 0.14, 0, sides=6, closed=True)
        pts = [V(math.cos(t) * (R - 0.9), y, math.sin(t) * (R - 0.9)) for t in (k * 2 * math.pi / 48 for k in range(48))]
        tube(bm, pts, 0.1, 0, sides=6, closed=True)
        for k in range(8):
            t = k * 2 * math.pi / 8
            tube(bm, [V(0, y, 0), V(math.cos(t) * R, y, math.sin(t) * R)], 0.11, 0, sides=4)
        cyl(bm, V(0, y - 0.25, 0), 0.6, 0.5, 0, seg=16, axis="Y")
    for k in range(16):
        t = k * 2 * math.pi / 16
        d = V(math.cos(t), 0, math.sin(t))
        rot = Matrix.Rotation(-t, 3, "Y")
        c = d * (R - 0.15)
        box(bm, c - V(0.5, W / 2 + 0.1, 0.04), c + V(0.5, W / 2 + 0.1, 0.04), 3, bevel=0.01, rot=rot) if False else None
        p0, p1 = d * (R - 0.95), d * (R + 0.35)
        n = V(-d.z, 0, d.x) * 0.05
        vs = [bm.verts.new(p) for p in (p0 - n + V(0, -W / 2 - 0.1, 0), p1 - n + V(0, -W / 2 - 0.1, 0), p1 - n + V(0, W / 2 + 0.1, 0), p0 - n + V(0, W / 2 + 0.1, 0),
                                       p0 + n + V(0, -W / 2 - 0.1, 0), p1 + n + V(0, -W / 2 - 0.1, 0), p1 + n + V(0, W / 2 + 0.1, 0), p0 + n + V(0, W / 2 + 0.1, 0))]
        for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
            bm.faces.new([vs[i] for i in f]).material_index = 3
    cyl(bm, V(0, -W / 2 - 1.2, 0), 0.32, W + 2.4, 1, seg=12, axis="Y")
    return new_obj("water_wheel", bm, [WOOD, IRON, WOODY, GREY])


def village_bell():
    """a bronze bell on its oak yoke, iron straps over it; swings about the yoke's axis"""
    bm = bmesh.new()
    lathe(bm, [(0.0, 1.02), (0.12, 1.02), (0.2, 1.0), (0.26, 0.9), (0.28, 0.7), (0.31, 0.52), (0.38, 0.38), (0.46, 0.3),
               (0.48, 0.26), (0.42, 0.25), (0.3, 0.32)], V(0.5, -0.5, 0.0), 0, seg=28)
    box(bm, V(0.0, -0.62, 1.02), V(1.0, -0.38, 1.24), 1, bevel=0.03)
    for x in (0.38, 0.62):
        tube(bm, [V(x, -0.52, 1.0), V(x, -0.52, 1.26)], 0.02, 2, sides=4)
    ellipsoid(bm, V(0.5, -0.5, 0.28), (0.06, 0.06, 0.06), 2, seg=8)
    tube(bm, [V(0.5, -0.5, 0.9), V(0.5, -0.5, 0.3)], 0.015, 2, sides=4)
    cyl(bm, V(-0.15, -0.5, 1.13), 0.05, 1.3, 2, seg=8, axis="X")
    return new_obj("village_bell", bm, [BRONZE, DARK, IRON])


# ================================================================ carts and wagons

def hay_cart():
    """a two-wheeled cart heaped with hay, slatted sides, its shafts down on the ground in front"""
    bm = bmesh.new()
    box(bm, V(-0.75, -1.4, 0.72), V(0.75, 1.2, 0.82), 2, bevel=0.02)             # the bed
    for x in (-0.75, 0.75):
        for z in (0.95, 1.2):
            box(bm, V(x - 0.04, -1.4, z - 0.04), V(x + 0.04, 1.2, z + 0.04), 2, bevel=0.01)
        for y in (-1.3, -0.6, 0.1, 0.8, 1.15):
            box(bm, V(x - 0.04, y - 0.04, 0.72), V(x + 0.04, y + 0.04, 1.3), 0, bevel=0.01)
    for x in (-0.55, 0.55):                                                     # the shafts
        tube(bm, [V(x, 0.9, 0.75), V(x * 0.8, 2.4, 0.38), V(x * 0.7, 3.1, 0.06)], 0.05, 0, sides=6)
    wheel(bm, V(-0.92, -0.2, 0.68), 0.68, 0.08)
    wheel(bm, V(0.92, -0.2, 0.68), 0.68, 0.08)
    cyl(bm, V(-0.95, -0.2, 0.68), 0.06, 1.9, 1, seg=8, axis="X")
    def hay(c, r, seed):                                                        # lumps, and the strands combed through
        vs = ellipsoid(bm, c, r, 3, seg=30)
        bm.normal_update()
        o = Vector((seed * 3.1, seed * 1.7, 0))
        for v in vs:
            lump = noise.noise(v.co * 2.6 + o)
            comb = noise.noise(Vector((v.co.x * 3.0, v.co.y * 26.0, v.co.z * 3.0)) + o)
            fine = noise.noise(Vector((v.co.x * 40.0, v.co.y * 6.0, v.co.z * 40.0)) + o)
            v.co += v.normal * (0.1 * lump + 0.045 * comb + 0.018 * fine)
    hay(V(0, -0.1, 1.1), (0.84, 1.42, 0.55), 1)
    for k in range(6):                                                          # forkfuls heaped on top
        a = k * 2.1
        hay(V(0.4 * math.cos(a), -0.1 + 0.85 * math.sin(a * 0.7), 1.42 + 0.06 * (k % 3)), (0.42, 0.58, 0.2), 5 + k)
    import random as _r
    rr = _r.Random(5)
    for k in range(16):                                                         # a few wisps hanging over the sides
        y = rr.uniform(-1.3, 1.1)
        sx = rr.choice((-1, 1))
        tube(bm, [V(sx * 0.7, y, 1.25), V(sx * 0.86, y + rr.uniform(-0.1, 0.1), 1.05), V(sx * 0.9, y + rr.uniform(-0.15, 0.15), 0.85)],
             0.03, 6, sides=4)
    tube(bm, [V(-0.8, -0.6, 1.3), V(0, -0.6, 1.72), V(0.8, -0.6, 1.3)], 0.025, 4, sides=4)
    tube(bm, [V(-0.8, 0.5, 1.3), V(0, 0.5, 1.72), V(0.8, 0.5, 1.3)], 0.025, 4, sides=4)
    return new_obj("hay_cart", bm, [WOOD, IRON, GREY, HAY, ROPE, ROPE, HAYX])


def handcart():
    """a small barrow-cart pushed by hand: two wheels, a box of grey boards, sacks and a keg in it"""
    bm = bmesh.new()
    box(bm, V(-0.55, -0.7, 0.5), V(0.55, 0.6, 0.56), 2, bevel=0.015)
    for x in (-0.55, 0.55):
        box(bm, V(x - 0.03, -0.7, 0.56), V(x + 0.03, 0.6, 0.85), 2, bevel=0.01)
    box(bm, V(-0.55, -0.73, 0.56), V(0.55, -0.67, 0.85), 2, bevel=0.01)
    box(bm, V(-0.55, 0.57, 0.56), V(0.55, 0.63, 0.75), 2, bevel=0.01)
    for x in (-0.4, 0.4):
        tube(bm, [V(x, 0.5, 0.55), V(x, 1.5, 0.78)], 0.035, 0, sides=6)
        tube(bm, [V(x, -0.55, 0.5), V(x, -0.62, 0.0)], 0.035, 0, sides=6)
    tube(bm, [V(-0.42, 1.5, 0.78), V(0.42, 1.5, 0.78)], 0.035, 0, sides=6)
    wheel(bm, V(-0.66, 0.05, 0.42), 0.42, 0.06, spokes=8)
    wheel(bm, V(0.66, 0.05, 0.42), 0.42, 0.06, spokes=8)
    sack(bm, V(-0.2, -0.35, 0.56), 0.6, 0.22, 3, 4, 1, tilt=0.15)
    sack(bm, V(0.2, -0.3, 0.56), 0.55, 0.21, 3, 4, 2, tilt=-0.2, turn=0.6)
    sack(bm, V(0.0, 0.25, 0.68), 0.6, 0.21, 3, 4, 4, tilt=1.35, turn=1.4)
    lathe(bm, [(0.0, 0.0), (0.17, 0.0), (0.2, 0.15), (0.21, 0.24), (0.2, 0.33), (0.17, 0.48), (0.0, 0.48)], V(0.25, 0.35, 0.56), 2, seg=16, axis="Z")
    return new_obj("handcart", bm, [WOOD, IRON, GREY, SACK, ROPE])


def covered_wagon():
    """a four-wheeled wagon under a canvas tilt on five hoops, the tongue out front"""
    bm = bmesh.new()
    L, Wd = 3.6, 1.5
    box(bm, V(-Wd / 2, -L / 2, 0.85), V(Wd / 2, L / 2, 0.95), 2, bevel=0.02)
    for x in (-Wd / 2, Wd / 2):
        box(bm, V(x - 0.04, -L / 2, 0.95), V(x + 0.04, L / 2, 1.45), 2, bevel=0.015)
    for y in (-L / 2, L / 2):
        box(bm, V(-Wd / 2, y - 0.04, 0.95), V(Wd / 2, y + 0.04, 1.45), 2, bevel=0.015)
    for k in range(5):                                                          # the hoops and the tilt over them
        y = -L / 2 + 0.2 + k * (L - 0.4) / 4
        pts = [V(math.cos(t) * (Wd / 2 + 0.02), y, 1.45 + math.sin(t) * 1.05) for t in (j * math.pi / 14 for j in range(15))]
        tube(bm, pts, 0.035, 0, sides=5)
    rows = sheet(bm, V(0, -L / 2 + 0.15, 0), V(0, L - 0.3, 0), V(0, 0, 0), 10, 16, 3,
                 lambda a, b: V(math.cos(math.pi * b) * (Wd / 2 + 0.07), 0, 1.45 + math.sin(math.pi * b) * (1.12 - 0.05 * math.sin(a * math.pi * 4) ** 2)))
    thick(bm, rows, 0.02, 3)
    for y, r in ((-1.1, 0.72), (1.15, 0.55)):
        wheel(bm, V(-Wd / 2 - 0.16, y, r), r, 0.08, spokes=12)
        wheel(bm, V(Wd / 2 + 0.16, y, r), r, 0.08, spokes=12)
        cyl(bm, V(-Wd / 2 - 0.2, y, r), 0.07, Wd + 0.4, 1, seg=8, axis="X")
    tube(bm, [V(0, L / 2, 0.6), V(0, L / 2 + 1.2, 0.35), V(0, L / 2 + 2.0, 0.08)], 0.06, 0, sides=6)
    tube(bm, [V(-0.4, L / 2 + 1.2, 0.35), V(0.4, L / 2 + 1.2, 0.35)], 0.05, 0, sides=6)
    box(bm, V(-0.6, L / 2 - 0.35, 1.45), V(0.6, L / 2 - 0.05, 1.55), 2, bevel=0.02)     # the driver's bench
    for k, x in enumerate((-0.4, 0.05, 0.42)):
        lathe(bm, [(0.0, 0.0), (0.18, 0.0), (0.21, 0.14), (0.22, 0.25), (0.21, 0.36), (0.18, 0.5), (0.0, 0.5)],
              V(x, -L / 2 - 0.3 + 0.0, 0.0), 2, seg=14)
    return new_obj("covered_wagon", bm, [WOOD, IRON, GREY, CLOTH])


def wheelbarrow():
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in (V(-0.3, -0.45, 0.42), V(0.3, -0.45, 0.42), V(0.3, 0.3, 0.42), V(-0.3, 0.3, 0.42),
                                    V(-0.4, -0.6, 0.72), V(0.4, -0.6, 0.72), V(0.4, 0.45, 0.72), V(-0.4, 0.45, 0.72))]
    for f in ((3, 2, 1, 0), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[i] for i in f]).material_index = 2
    for x in (-0.25, 0.25):
        tube(bm, [V(x * 0.6, -0.75, 0.26), V(x, 0.3, 0.45), V(x * 1.4, 1.1, 0.62)], 0.035, 0, sides=6)
        tube(bm, [V(x, 0.2, 0.44), V(x, 0.28, 0.0)], 0.03, 0, sides=5)
    wheel(bm, V(-0.04, -0.75, 0.26), 0.26, 0.05, spokes=6)
    heap(bm, V(0, -0.1, 0.68), (0.3, 0.42, 0.14), 3, 5, 0.04)
    return new_obj("wheelbarrow", bm, [WOOD, IRON, GREY, mottled("vil_soil", stops("#2a1c10", "#4a3420", "#5c4428"), 12.0, 0.95)])


# ================================================================ round the houses

def well():
    """a round well of rough stones under a little shingled roof, the winch with its crank, rope and bucket"""
    bm = bmesh.new()
    for k in range(3):
        for j in range(14):
            t = (j + 0.5 * (k % 2)) * 2 * math.pi / 14
            c = V(math.cos(t) * 0.95, math.sin(t) * 0.95, 0.15 + k * 0.28)
            vs = ellipsoid(bm, c, (0.24, 0.24, 0.15), 0, seg=8, rot=Matrix.Rotation(t, 3, "Z"))
            displace(vs, 0.04, 6.0, j + 14 * k)
    cyl(bm, V(0, 0, 0.7), 1.1, 0.1, 0, seg=20, r2=1.1)
    cyl(bm, V(0, 0, 0.0), 0.75, 0.72, 5, seg=16)
    for x in (-1.0, 1.0):
        box(bm, V(x - 0.08, -0.08, 0.6), V(x + 0.08, 0.08, 2.2), 1, bevel=0.02)
    for s in (-1, 1):                                                           # the roof
        rows = sheet(bm, V(-1.4, 0, 2.55), V(2.8, 0, 0), V(0, s * 0.95, -0.6), 6, 4, 4)
        thick(bm, rows, 0.02, 4)
        for i in range(6):                                               # shingle courses lapping down the slope
            t0 = i / 6
            for j in range(12):
                x0 = -1.4 + j * 2.8 / 12 + (0.1 if i % 2 else 0)
                if x0 + 2.8 / 12 > 1.42:
                    continue
                a = V(x0, s * 0.95 * t0, 2.58 - 0.6 * t0)
                rows2 = sheet(bm, a, V(2.8 / 12 - 0.015, 0, 0), V(0, s * 0.95 / 5.2, -0.6 / 5.2 - 0.02), 1, 1, 4)
    box(bm, V(-1.45, -0.06, 2.5), V(1.45, 0.06, 2.62), 1, bevel=0.02)
    cyl(bm, V(-1.0, 0, 1.75), 0.11, 2.0, 1, seg=10, axis="X")
    tube(bm, [V(1.0, 0, 1.75), V(1.25, 0, 1.75), V(1.25, 0, 1.45), V(1.38, 0, 1.45)], 0.025, 2, sides=5)
    tube(bm, [V(0.0, 0.1, 1.72), V(0.0, 0.1, 1.15)], 0.02, 3, sides=4)
    lathe(bm, [(0.0, 0.92), (0.14, 0.92), (0.15, 0.94), (0.17, 1.15), (0.0, 1.15)], V(0.0, 0.1, 0.0), 1, seg=12)
    tube(bm, [V(-0.17, 0.1, 1.15), V(0, 0.1, 1.28), V(0.17, 0.1, 1.15)], 0.012, 2, sides=4)
    return new_obj("well", bm, [STONE, WOOD, IRON, ROPE, SHINGLE, mat("vil_dark_water", lin("#0c1418"), 0.1)])


def market_stall():
    """a stall of four posts, a counter of boards heaped with apples and cabbages, a striped awning over it"""
    bm = bmesh.new()
    for x in (-1.1, 1.1):
        for y in (-0.6, 0.6):
            box(bm, V(x - 0.06, y - 0.06, 0), V(x + 0.06, y + 0.06, 2.0 if y < 0 else 2.3), 0, bevel=0.015)
    box(bm, V(-1.2, -0.65, 0.85), V(1.2, 0.55, 0.95), 2, bevel=0.02)
    box(bm, V(-1.2, 0.5, 0.0), V(1.2, 0.58, 0.85), 2, bevel=0.01)
    for i in range(8):                                                          # the striped awning, sagging
        x0 = -1.35 + i * 2.7 / 8
        rows = sheet(bm, V(x0, -0.9, 2.0), V(2.7 / 8, 0, 0), V(0, 1.85, 0.4), 2, 6, 3 + i % 2,
                     lambda a, b: V(0, 0, -0.08 * math.sin(math.pi * b)))
        thick(bm, rows, 0.01, 3 + i % 2)
    for i in range(8):                                                          # the scalloped valance
        x0 = -1.35 + i * 2.7 / 8
        sheet(bm, V(x0, -0.9, 2.0), V(2.7 / 8, 0, 0), V(0, 0, -0.22), 2, 2, 3 + i % 2, lambda a, b: V(0, 0, 0.1 * b * math.sin(math.pi * a)))
    for k in range(3):                                                          # baskets of produce
        x = -0.7 + k * 0.7
        lathe(bm, [(0.0, 0.95), (0.22, 0.95), (0.28, 1.12), (0.25, 1.12), (0.0, 1.0)], V(x, -0.15, 0), 2, seg=14)
        for j in range(7):
            a = j * 0.9
            ellipsoid(bm, V(x + 0.13 * math.cos(a) * (j > 0), -0.15 + 0.13 * math.sin(a) * (j > 0), 1.13 + 0.06 * (j == 0)),
                      (0.075, 0.075, 0.07), 5 if k != 1 else 6, seg=8)
    box(bm, V(-1.0, 0.0, 0.0), V(-0.45, 0.45, 0.4), 2, bevel=0.02)             # crates under it
    box(bm, V(0.3, 0.05, 0.0), V(0.9, 0.45, 0.35), 2, bevel=0.02)
    return new_obj("market_stall", bm, [WOOD, IRON, GREY, RED, CREAM, APPLE, CABBAGE])


def signpost():
    """a post with three arrow boards pointing off to the roads, a little cap on top"""
    bm = bmesh.new()
    box(bm, V(-0.08, -0.08, 0), V(0.08, 0.08, 2.5), 0, bevel=0.02)
    for x in (-0.18, 0.18):
        box(bm, V(x - 0.04, -0.2, 2.5), V(x + 0.04, 0.2, 2.62), 0) if False else None
    vs = [bm.verts.new(p) for p in (V(-0.17, -0.17, 2.5), V(0.17, -0.17, 2.5), V(0.17, 0.17, 2.5), V(-0.17, 0.17, 2.5), V(0, 0, 2.75))]
    for f in ((0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (3, 2, 1, 0)):
        bm.faces.new([vs[i] for i in f]).material_index = 2
    for k, (z, ang, L) in enumerate(((2.15, 20, 1.0), (1.8, 150, 0.9), (1.45, 260, 0.95))):
        a = math.radians(ang)
        rot = Matrix.Rotation(a, 3, "Z")
        d = rot @ V(1, 0, 0)
        n = rot @ V(0, 1, 0)
        p0 = d * 0.08
        pts = [p0 + n * 0.035 + V(0, 0, z + 0.12), p0 + d * L + n * 0.035 + V(0, 0, z + 0.12), p0 + d * (L + 0.18) + n * 0.035 + V(0, 0, z),
               p0 + d * L + n * 0.035 + V(0, 0, z - 0.12), p0 + n * 0.035 + V(0, 0, z - 0.12)]
        f_ = [bm.verts.new(p) for p in pts]
        b_ = [bm.verts.new(p - n * 0.07) for p in pts]
        bm.faces.new(f_).material_index = 1
        bm.faces.new(b_[::-1]).material_index = 1
        for i in range(5):
            bm.faces.new((f_[i], b_[i], b_[(i + 1) % 5], f_[(i + 1) % 5])).material_index = 1
    return new_obj("signpost", bm, [WOOD, GREY, SHINGLE])


def washing_line():
    """two T-posts, a sagging line, sheets and shirts pegged to it in the breeze"""
    bm = bmesh.new()
    for x in (-1.4, 1.4):
        box(bm, V(x - 0.05, -0.05, 0), V(x + 0.05, 0.05, 2.0), 0, bevel=0.015)
        box(bm, V(x - 0.05, -0.25, 1.9), V(x + 0.05, 0.25, 1.98), 0, bevel=0.01)
    sag = lambda x: 1.92 - 0.18 * (1 - (x / 1.4) ** 2)
    tube(bm, [V(x, 0.0, sag(x)) for x in [-1.4 + i * 0.2 for i in range(15)]], 0.012, 1, sides=4)
    for k, (x0, w, h, mi) in enumerate(((-1.25, 0.7, 0.9, 2), (-0.45, 0.45, 0.55, 3), (0.1, 0.6, 1.0, 4), (0.8, 0.45, 0.5, 5))):
        rows = sheet(bm, V(x0, 0, 0), V(w, 0, 0), V(0, 0, -h), 6, 6, mi,
                     lambda a, b, x0=x0, w=w, k=k: V(0, 0.12 * b * math.sin(a * 5 + k) + 0.05 * b, sag(x0 + a * w)))
        thick(bm, rows, 0.01, mi)
    return new_obj("washing_line", bm, [WOOD, ROPE, CREAM, BLUE, CLOTH, RED])


def scarecrow():
    """a scarecrow on its cross: sack head stitched, a wide straw hat, a ragged coat, straw out of the cuffs"""
    bm = bmesh.new()
    box(bm, V(-0.05, -0.05, 0), V(0.05, 0.05, 2.1), 0, bevel=0.015)
    box(bm, V(-0.8, -0.05, 1.45), V(0.8, 0.05, 1.53), 0, bevel=0.015)
    heap(bm, V(0, 0, 1.85), (0.2, 0.18, 0.22), 1, 7, 0.03)
    tube(bm, [V(-0.12, 0.17, 1.86), V(0.12, 0.17, 1.86)], 0.012, 2, sides=4)
    lathe(bm, [(0.0, 2.15), (0.16, 2.15), (0.18, 2.02), (0.42, 2.0), (0.44, 1.96), (0.0, 1.98)], V(0, 0, 0), 3, seg=18)
    rows = sheet(bm, V(-0.75, 0.08, 1.58), V(1.5, 0, 0), V(0, 0, -0.95), 10, 8, 4,
                 lambda a, b: V(0, 0.06 * math.sin(a * 7) * b, (0.25 * b if abs(a - 0.5) > 0.3 else 0) - 0.05 * math.sin(a * 13) * (b > 0.9)))
    thick(bm, rows, 0.01, 4)
    for s in (-1, 1):
        for k in range(4):
            tube(bm, [V(s * 0.78, 0.0, 1.5), V(s * (0.9 + 0.05 * k), 0.03 * k, 1.4 - 0.06 * k)], 0.02, 3, sides=3)
    return new_obj("scarecrow", bm, [WOOD, SACK, IRON, STRAW, mottled("vil_coat", stops("#2c2a20", "#4a4430", "#5e5640"), 8.0, 0.9)])


def skeps():
    """three straw beehives on a plank bench under a board roof"""
    bm = bmesh.new()
    box(bm, V(-1.1, -0.35, 0.5), V(1.1, 0.35, 0.58), 2, bevel=0.02)
    for x in (-0.95, 0.95):
        box(bm, V(x - 0.05, -0.3, 0), V(x + 0.05, 0.3, 0.5), 0, bevel=0.01)
        box(bm, V(x - 0.05, -0.38, 0.58), V(x + 0.05, -0.3, 1.45), 0, bevel=0.01)
    rows = sheet(bm, V(-1.25, -0.6, 1.45), V(2.5, 0, 0), V(0, 1.05, -0.25), 4, 3, 2)
    thick(bm, rows, 0.02, 2)
    for x in (-0.65, 0.0, 0.65):
        prof = []
        for i in range(10):
            z = i * 0.06
            r = 0.3 * math.cos((i / 9) ** 1.6 * math.pi / 2) + (0.015 if i % 2 else 0)
            prof.append((max(r, 0.0), 0.58 + z))
        prof.append((0.0, 0.58 + 0.58))
        lathe(bm, prof, V(x, 0, 0), 1, seg=18)
        box(bm, V(x - 0.05, 0.27, 0.58), V(x + 0.05, 0.31, 0.62), 0)
    return new_obj("skeps", bm, [WOOD, STRAW, GREY])


def woodpile():
    """split logs stacked between two stakes, the chopping block with the axe in it"""
    bm = bmesh.new()
    for x in (-1.0, 1.0):
        box(bm, V(x - 0.05, -0.05, 0), V(x + 0.05, 0.05, 1.0), 0, bevel=0.01)
    for r in range(4):
        for i in range(6 - (r == 3)):
            x = -0.85 + i * 0.33 + 0.16 * (r % 2)
            cyl(bm, V(x, -0.32, 0.13 + r * 0.24), 0.13, 0.64, 2, seg=8, axis="Y")
    cyl(bm, V(1.6, 0.3, 0.0), 0.32, 0.5, 2, seg=14)
    box(bm, V(1.55, 0.15, 0.5), V(1.65, 0.45, 0.62), 1)
    tube(bm, [V(1.6, 0.3, 0.6), V(1.6, 0.85, 1.05)], 0.03, 0, sides=5)
    for k in range(4):
        cyl(bm, V(1.2 + 0.2 * k, 0.9, 0.0), 0.08, 0.2, 2, seg=6)
    return new_obj("woodpile", bm, [WOOD, IRON, wood("vil_log", stops("#4a3420", "#7a5a38", "#c8a46e"), "Y", 8.0)])


def churns_sacks():
    """milk churns of tinned iron and a heap of grain sacks by a door"""
    bm = bmesh.new()
    for x, y in ((-0.5, 0.0), (-0.1, -0.15), (-0.32, -0.45)):
        lathe(bm, [(0.0, 0.0), (0.2, 0.0), (0.21, 0.05), (0.2, 0.42), (0.13, 0.55), (0.1, 0.62), (0.12, 0.65), (0.0, 0.67)], V(x, y, 0), 0, seg=16)
        tube(bm, [V(x - 0.14, y, 0.5), V(x, y, 0.58), V(x + 0.14, y, 0.5)], 0.015, 0, sides=4)
    for i, (x, y, z, tl, tn) in enumerate(((0.45, 0.0, 0.0, 0.0, 0.0), (0.85, -0.1, 0.0, 0.1, 0.8), (0.62, 0.35, 0.22, 1.4, 0.3),
                                         (0.3, 0.5, 0.2, 1.45, -0.4))):
        sack(bm, V(x, y, z), 0.7, 0.24, 1, 2, 10 + i, tilt=tl, turn=tn)
    return new_obj("churns_sacks", bm, [TIN, SACK, ROPE])


def punt():
    """a flat-bottomed punt for the lake, its pole laid along it, a net heaped at the stern"""
    bm = bmesh.new()
    L, W = 3.8, 1.0
    prof = lambda y: 1.0 - max(0, abs(y) - L / 2 + 0.6) * 0.25
    box(bm, V(-W / 2, -L / 2, 0.0), V(W / 2, L / 2, 0.06), 0, bevel=0.02)
    for s in (-1, 1):
        box(bm, V(s * W / 2 - 0.04, -L / 2, 0.0), V(s * W / 2 + 0.04, L / 2, 0.35), 0, bevel=0.015)
    for y in (-L / 2, L / 2):
        box(bm, V(-W / 2, y - 0.04, 0.05), V(W / 2, y + 0.04, 0.3), 0, bevel=0.015)
    for y in (-0.6, 0.6):
        box(bm, V(-W / 2, y - 0.12, 0.25), V(W / 2, y + 0.12, 0.3), 2, bevel=0.01)
    tube(bm, [V(0.3, -2.4, 0.33), V(0.25, 2.6, 0.36)], 0.03, 2, sides=5)
    heap(bm, V(-0.15, -1.4, 0.15), (0.32, 0.38, 0.12), 1, 8, 0.05, 8.0)
    return new_obj("punt", bm, [GREY, ROPE, WOOD])


# ================================================================ the lake village's own

def net_rack():
    """two posts and a pole, a fishing net hung over it to dry, cork floats along its foot"""
    bm = bmesh.new()
    for x in (-1.3, 1.3):
        box(bm, V(x - 0.06, -0.06, 0), V(x + 0.06, 0.06, 2.3), 0, bevel=0.015)
    cyl(bm, V(-1.5, 0, 2.2), 0.05, 3.0, 0, seg=8, axis="X")
    drape = lambda x, z: V(x, 0.05 * math.sin(x * 3) + 0.25 * (2.2 - z) / 2.0 * (1 if x > 0 else -0.5), z + 0.12 * (1 - (x / 1.3) ** 2) * (z < 1.0))
    for i in range(15):                                                         # the mesh: strands down, rows across
        x = -1.2 + i * 2.4 / 14
        tube(bm, [drape(x, 2.2 - j * 0.2) for j in range(10)], 0.009, 1, sides=3)
    for j in range(10):
        z = 2.2 - j * 0.2
        tube(bm, [drape(-1.2 + i * 2.4 / 14, z) for i in range(15)], 0.009, 1, sides=3)
    for i in range(8):
        x = -1.15 + i * 2.3 / 7
        ellipsoid(bm, drape(x, 0.4), (0.07, 0.05, 0.05), 2, seg=8)
    return new_obj("net_rack", bm, [WOOD, NET, CORK])


def fish_rack():
    """an A-frame of poles, three rails, the catch hung by the tail in rows to dry"""
    bm = bmesh.new()
    for x in (-1.1, 1.1):
        tube(bm, [V(x, -0.55, 0), V(x, 0, 1.9)], 0.045, 0, sides=6)
        tube(bm, [V(x, 0.55, 0), V(x, 0, 1.9)], 0.045, 0, sides=6)
    for z, y in ((1.85, 0.0), (1.2, 0.2), (1.2, -0.2)):
        tube(bm, [V(-1.25, y, z), V(1.25, y, z)], 0.035, 0, sides=6)
    import random as _r
    rr = _r.Random(3)
    for z, y in ((1.85, 0.0), (1.2, 0.2), (1.2, -0.2)):
        for i in range(9):
            x = -0.95 + i * 0.24 + rr.uniform(-0.03, 0.03)
            L = rr.uniform(0.3, 0.42)
            tube(bm, [V(x, y, z), V(x, y, z - 0.08)], 0.006, 1, sides=3)
            ellipsoid(bm, V(x, y, z - 0.08 - L / 2), (0.035, 0.06, L / 2), 2, seg=8)
            vs = [bm.verts.new(p) for p in (V(x, y, z - 0.1 - L * 0.95), V(x, y - 0.07, z - 0.04 - L * 0.95 + 0.0), V(x, y + 0.07, z - 0.04 - L * 0.95))]
            bm.faces.new(vs).material_index = 2
    return new_obj("fish_rack", bm, [WOOD, ROPE, FISH])


def eel_traps():
    """wicker traps: long cones of withies with a funnel mouth, two lying, one stood on end"""
    bm = bmesh.new()
    for k, (c, tilt, turn) in enumerate(((V(-0.5, 0, 0.22), 1.5708, 0.2), (V(0.5, 0.1, 0.22), 1.5708, -0.4), (V(0.0, -0.6, 0.0), 0.0, 0.0))):
        before = set(bm.verts)
        prof = [(0.0, 0.0), (0.2, 0.0), (0.22, 0.2), (0.2, 0.5), (0.15, 0.8), (0.08, 1.0), (0.03, 1.1), (0.0, 1.1)]
        rings = lathe(bm, prof, V(0, 0, 0), 0, seg=14)
        vs = [v for rg in rings for v in rg]
        for j in range(6):                                                      # the hoops binding it
            z = 0.12 + j * 0.16
            r = 0.22 - 0.12 * (z / 1.0) ** 1.5
            tube(bm, ring(V(0, 0, z), r + 0.012, "Z", 14), 0.012, 1, sides=3, closed=True)
        moved = set(bm.verts) - before
        R = Matrix.Rotation(turn, 3, "Z") @ Matrix.Rotation(tilt, 3, "X")
        for v in moved:
            v.co = R @ v.co + c
    return new_obj("eel_traps", bm, [WICKER, DARK])


def reed_sheaves():
    """bundles of cut reed tied at the waist, leaned against a post to dry"""
    bm = bmesh.new()
    box(bm, V(-0.06, -0.06, 0), V(0.06, 0.06, 1.8), 0, bevel=0.015)
    for k, (x, lean) in enumerate(((-0.45, 0.25), (-0.2, 0.15), (0.25, -0.18), (0.5, -0.28))):
        base = V(x, 0.25, 0)
        top = V(x * 0.4, 0.05, 2.1 - abs(lean))
        d = (top - base).normalized()
        cyl(bm, base, 0.13, 0.0001, 1, seg=10) if False else None
        tube(bm, [base, base + d * 0.9, top], lambda u: 0.13 - 0.05 * math.sin(u * math.pi) * 0.9, 1, sides=10)
        tube(bm, ring(base + d * 0.9, 0.095, "Z", 10), 0.02, 2, sides=4, closed=True)
        for j in range(6):                                                      # the plumes at the top
            a = j * 1.05
            tube(bm, [top, top + V(0.12 * math.cos(a), 0.12 * math.sin(a), 0.25)], 0.015, 3, sides=3)
    return new_obj("reed_sheaves", bm, [WOOD, REED, ROPE, mottled("vil_plume", stops("#6a5a3a", "#9a8458", "#c8b484"), 20.0, 0.9)])


def lake_lantern():
    """a boardwalk post with an arm, the lantern hung from it on a short chain"""
    bm = bmesh.new()
    box(bm, V(-0.07, -0.07, 0), V(0.07, 0.07, 2.4), 0, bevel=0.02)
    box(bm, V(-0.05, -0.05, 2.25), V(0.05, 0.75, 2.33), 0, bevel=0.01)
    tube(bm, [V(0, 0.05, 1.9), V(0, 0.45, 2.27)], 0.025, 0, sides=5)
    links(bm, V(0, 0.65, 2.25), V(0, 0.65, 1.98), 1, w=0.035, r=0.008)
    for x in (-0.1, 0.1):
        for y in (0.55, 0.75):
            box(bm, V(x - 0.012, y - 0.012, 1.58), V(x + 0.012, y + 0.012, 1.93), 1)
    box(bm, V(-0.12, 0.53, 1.92), V(0.12, 0.77, 1.97), 1, bevel=0.01)
    vs = [bm.verts.new(p) for p in (V(-0.12, 0.53, 1.97), V(0.12, 0.53, 1.97), V(0.12, 0.77, 1.97), V(-0.12, 0.77, 1.97), V(0, 0.65, 2.06))]
    for f in ((0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)):
        bm.faces.new([vs[i] for i in f]).material_index = 1
    box(bm, V(-0.12, 0.53, 1.55), V(0.12, 0.77, 1.59), 1, bevel=0.01)
    box(bm, V(-0.085, 0.565, 1.59), V(0.085, 0.735, 1.92), 2)
    return new_obj("lake_lantern", bm, [WOOD, IRON, LAMP])


def dugout():
    """a dugout canoe hollowed from one log, a paddle laid in it"""
    bm = bmesh.new()
    L = 3.2
    prof = [(0.0, -L / 2), (0.12, -L / 2 + 0.15), (0.3, -L / 2 + 0.6), (0.34, 0.0), (0.3, L / 2 - 0.6), (0.12, L / 2 - 0.15), (0.0, L / 2)]
    rings = lathe(bm, prof, V(0, 0, 0.3), 0, seg=18, axis="Y")
    for v in [v for rg in rings for v in rg]:
        if v.co.z > 0.42:                                                       # cut the top off, hollowed
            v.co.z = 0.42 - (0.18 if abs(v.co.x) < 0.22 and abs(v.co.y) < L / 2 - 0.4 else 0)
    tube(bm, [V(0.05, -1.2, 0.33), V(0.05, 0.9, 0.36)], 0.025, 1, sides=5)
    box(bm, V(-0.04, 0.9, 0.33), V(0.14, 1.35, 0.37), 1, bevel=0.02)
    return new_obj("dugout", bm, [wood("vil_dug", stops("#3a2414", "#5e3c22", "#7a5432"), "Y", 14.0), WOOD])


def mooring_post():
    """a thick mooring post, iron-capped, a hawser looped round it and coiled at its foot"""
    bm = bmesh.new()
    cyl(bm, V(0.5, -0.5, 0), 0.2, 1.2, 0, seg=14)
    cyl(bm, V(0.5, -0.5, 1.2), 0.22, 0.08, 1, seg=14)
    for k in range(3):
        tube(bm, ring(V(0.5, -0.5, 0.75 + k * 0.07), 0.23, "Z", 14), 0.03, 2, sides=5, closed=True)
    for k in range(4):
        tube(bm, ring(V(0.95, -0.15, 0.03 + k * 0.05), 0.25 - k * 0.03, "Z", 16), 0.03, 2, sides=5, closed=True)
    return new_obj("mooring_post", bm, [DARK, IRON, ROPE])


def catch_basket():
    """a creel of the day's catch, a coil of rope and two floats by it"""
    bm = bmesh.new()
    lathe(bm, [(0.0, 0.0), (0.22, 0.0), (0.27, 0.15), (0.3, 0.35), (0.27, 0.37), (0.0, 0.3)], V(0.3, -0.5, 0), 0, seg=16)
    for i in range(7):
        a = i * 0.9
        ellipsoid(bm, V(0.3 + 0.12 * math.cos(a), -0.5 + 0.12 * math.sin(a), 0.36), (0.04, 0.13, 0.035), 1, seg=8,
                  rot=Matrix.Rotation(a, 3, "Z"))
    for k in range(4):
        tube(bm, ring(V(0.85, -0.3, 0.03 + k * 0.05), 0.22 - k * 0.025, "Z", 16), 0.028, 2, sides=5, closed=True)
    ellipsoid(bm, V(0.7, -0.85, 0.08), (0.08, 0.08, 0.08), 3, seg=10)
    ellipsoid(bm, V(0.9, -0.8, 0.08), (0.08, 0.08, 0.08), 3, seg=10)
    return new_obj("catch_basket", bm, [WICKER, FISH, ROPE, CORK])


# ================================================================ the cliff's and the gorge's own

def hoist_crane():
    """a timber crane on the lip: mast, raking jib, a pulley at its head, the winch drum and crank, a crate on the rope"""
    bm = bmesh.new()
    box(bm, V(-0.7, -0.7, 0), V(0.7, 0.7, 0.2), 0, bevel=0.02)
    box(bm, V(-0.12, -0.12, 0.2), V(0.12, 0.12, 3.6), 0, bevel=0.02)
    tube(bm, [V(0, 0, 3.3), V(0, 3.6, 4.3)], 0.1, 0, sides=6)
    tube(bm, [V(0, 0, 1.6), V(0, 2.2, 3.85)], 0.07, 0, sides=6)
    for x in (-0.12, 0.12):
        tube(bm, [V(x, 3.5, 4.35), V(x, 3.75, 4.35)], 0.02, 1, sides=4)
    cyl(bm, V(-0.08, 3.62, 4.3), 0.16, 0.16, 1, seg=14, axis="X")
    cyl(bm, V(-0.35, 0.3, 0.6), 0.18, 0.7, 0, seg=14, axis="X")
    for x in (-0.4, 0.4):
        box(bm, V(x - 0.04, 0.2, 0.2), V(x + 0.04, 0.4, 0.75), 0)
    tube(bm, [V(0.4, 0.3, 0.6), V(0.55, 0.3, 0.6), V(0.55, 0.3, 0.3), V(0.7, 0.3, 0.3)], 0.025, 1, sides=5)
    tube(bm, [V(0, 0.3, 0.75), V(0, 0.9, 2.3), V(0, 3.5, 4.4)], 0.018, 2, sides=4)
    tube(bm, [V(0, 3.78, 4.3), V(0, 3.78, 1.6)], 0.018, 2, sides=4)
    for dx, dy in ((-0.3, -0.3), (0.3, -0.3), (0.3, 0.3), (-0.3, 0.3)):
        tube(bm, [V(0, 3.78, 1.6), V(dx, 3.78 + dy, 1.2)], 0.012, 2, sides=4)
    box(bm, V(-0.35, 3.43, 0.6), V(0.35, 4.13, 1.2), 3, bevel=0.03)
    for z in (0.62, 1.18):
        box(bm, V(-0.37, 3.41, z - 0.03), V(0.37, 4.15, z + 0.03), 1)
    return new_obj("hoist_crane", bm, [WOOD, IRON, ROPE, GREY])


def rope_ladder():
    """a rope ladder hung from two iron hooks: twisted side ropes, wooden rungs, a slight sway"""
    bm = bmesh.new()
    for x in (-0.3, 0.3):
        tube(bm, [V(x, 0, 6.0), V(x, 0.1, 6.0), V(x, 0.1, 5.85)], 0.03, 1, sides=5)
        tube(bm, [V(x, 0.1, 5.85 - z) + V(0.03 * math.sin(z * 1.3), 0.04 * math.sin(z * 0.9), 0) for z in [i * 0.25 for i in range(24)]], 0.025, 2, sides=5)
    for i in range(18):
        z = 5.6 - i * 0.32
        sw = V(0.03 * math.sin((5.85 - z) * 1.3), 0.1 + 0.04 * math.sin((5.85 - z) * 0.9), 0)
        cyl(bm, V(-0.32, 0, z) + sw, 0.03, 0.64, 0, seg=6, axis="X")
    return new_obj("rope_ladder", bm, [WOOD, IRON, ROPE])


def lift_basket():
    """the cliff lift: a gantry of two posts and a beam, a big wicker basket slung under the pulley"""
    bm = bmesh.new()
    for x in (-1.2, 1.2):
        box(bm, V(x - 0.1, -0.1, 0), V(x + 0.1, 0.1, 3.4), 0, bevel=0.02)
        tube(bm, [V(x, -0.8, 0), V(x, 0, 2.6)], 0.05, 0, sides=5)
    box(bm, V(-1.4, -0.12, 3.4), V(1.4, 0.12, 3.62), 0, bevel=0.02)
    cyl(bm, V(-0.1, 0.3, 3.3), 0.22, 0.2, 1, seg=16, axis="X")
    box(bm, V(-0.12, 0.05, 3.3), V(0.12, 0.3, 3.4), 1)
    tube(bm, [V(0, 0.5, 3.3), V(0, 0.5, 1.75)], 0.02, 2, sides=4)
    for a in range(4):
        t = a * math.pi / 2 + math.pi / 4
        tube(bm, [V(0, 0.5, 1.75), V(0.6 * math.cos(t), 0.5 + 0.6 * math.sin(t), 1.2)], 0.015, 2, sides=4)
    lathe(bm, [(0.0, 0.25), (0.5, 0.25), (0.62, 0.45), (0.68, 0.85), (0.72, 1.2), (0.66, 1.2), (0.6, 0.85), (0.52, 0.5), (0.0, 0.32)],
          V(0, 0.5, 0), 3, seg=20)
    tube(bm, ring(V(0, 0.5, 1.2), 0.72, "Z", 20), 0.03, 4, sides=5, closed=True)
    return new_obj("lift_basket", bm, [WOOD, IRON, ROPE, WICKER, DARK])


def toll_barrier():
    """the bridge's toll: a striped pole on a post, its counterweight of stones in a cage, the tollkeeper's box"""
    bm = bmesh.new()
    box(bm, V(-0.12, -0.12, 0), V(0.12, 0.12, 1.2), 0, bevel=0.02)
    cyl(bm, V(-0.2, 0, 1.1), 0.05, 0.4, 1, seg=8, axis="X")
    for i in range(10):
        box(bm, V(-0.05, -0.05 - 0 + 0, 1.05), V(0.05, 0.05, 1.15), 0) if False else None
    for i in range(8):
        y0 = 0.0 + i * 0.45
        tube(bm, [V(0, y0 + 0.1, 1.12), V(0, y0 + 0.55, 1.12)], 0.06, 2 if i % 2 == 0 else 3, sides=8)
    box(bm, V(-0.18, -0.9, 0.85), V(0.18, -0.2, 1.3), 1, bevel=0.01)
    for k in range(4):
        ellipsoid(bm, V(0.0, -0.55 + 0.1 * (k % 2), 0.95 + 0.1 * (k // 2)), (0.13, 0.14, 0.1), 4, seg=8)
    box(bm, V(0.8, -0.5, 0), V(1.6, 0.3, 1.0), 0, bevel=0.02)
    box(bm, V(0.75, -0.55, 1.0), V(1.65, 0.35, 1.08), 0, bevel=0.02)
    box(bm, V(0.9, 0.3, 0.6), V(1.5, 0.36, 0.65), 1)
    return new_obj("toll_barrier", bm, [WOOD, IRON, RED, CREAM, STONE])



# ================================================================ the elves' (Lumenhollow, rings of decks round a giant tree)

PALE = wood("elf_pale", stops("#7a6e5a", "#b0a48a", "#d6ccb2"), "Z", 30.0, 0.6)
PALEX = wood("elf_palex", stops("#7a6e5a", "#b0a48a", "#d6ccb2"), "X", 30.0, 0.6)
LEAF = mottled("elf_leaf", stops("#1e4a20", "#3a7a2e", "#6aa83e"), 9.0, 0.6)
SILVER = mat("elf_silver", lin("#b8c0c4"), 0.25, Metallic=1.0)
ELFGLOW = glass("elf_glow", lin("#f4f0b0"), 7.0)
MOONWATER = glass("elf_water", lin("#8ae0d8"), 3.0)
SILK = mottled("elf_silk", stops("#2e5a3a", "#4a8a54", "#7ab878"), 12.0, 0.7)
MOSSY = mottled("elf_moss", stops("#2a3a1a", "#4a6028", "#6a8034"), 8.0, 0.9)
ELFSTONE = mottled("elf_stone", stops("#7a7a70", "#a8a698", "#cac8ba"), 5.0, 0.7)


def curve(a, b, bulge, n=12):
    """points on a soft arc from a to b, bowed out by the vector bulge"""
    a, b, bulge = Vector(a), Vector(b), Vector(bulge)
    return [a.lerp(b, t) + bulge * math.sin(math.pi * t) for t in (i / n for i in range(n + 1))]


def leafy(bm, c, d, size, mi):
    """one carved leaf: a pointed blade along d, bent a little"""
    d = Vector(d).normalized()
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 1e-3:
        side = Vector((1, 0, 0))
    side.normalize()
    up = side.cross(d)
    pts = []
    for i in range(7):
        t = i / 6
        w = math.sin(math.pi * t) * size * 0.35
        pts.append((Vector(c) + d * size * t + up * 0.05 * size * math.sin(math.pi * t), w))
    for flip in (False, True):                                                  # its own verts each side, so both faces draw
        vs = [[bm.verts.new(p + side * w + up * (0.004 if flip else 0)), bm.verts.new(p - side * w + up * (0.004 if flip else 0))]
              for p, w in pts]
        for i in range(6):
            q = (vs[i][0], vs[i + 1][0], vs[i + 1][1], vs[i][1])
            bm.faces.new(q[::-1] if flip else q).material_index = mi


def elf_lantern():
    """a lantern of leaf-shaped glass panes held in silver ribs, hung from a curling bracket"""
    bm = bmesh.new()
    box(bm, V(-0.06, -0.06, 0.0), V(0.06, 0.06, 0.08), 0) if False else None
    tube(bm, curve(V(0, -0.45, 1.9), V(0, 0.0, 1.55), V(0, 0.05, 0.25)) + [V(0, 0.02, 1.48)], 0.02, 1, sides=5)
    tube(bm, [V(0, -0.45, 1.9), V(0, -0.5, 1.95), V(0, -0.45, 2.0)], 0.02, 1, sides=5)
    prof = [(0.0, 0.6), (0.05, 0.62), (0.13, 0.75), (0.17, 0.95), (0.14, 1.15), (0.06, 1.3), (0.03, 1.36), (0.0, 1.4)]
    lathe(bm, prof, V(0, 0, 0), 2, seg=12)
    for k in range(6):
        a = k * math.pi / 3
        tube(bm, [V(r * math.cos(a), r * math.sin(a), z) for r, z in ((0.06, 0.6), (0.15, 0.76), (0.185, 0.95), (0.155, 1.15), (0.07, 1.3), (0.035, 1.38))], 0.012, 1, sides=4)
    for k in range(5):
        a = k * 1.256
        leafy(bm, V(0.05 * math.cos(a), 0.05 * math.sin(a), 0.6), V(0.4 * math.cos(a), 0.4 * math.sin(a), -1), 0.18, 3)
    tube(bm, [V(0, 0, 1.4), V(0, 0, 1.5)], 0.012, 1, sides=4)
    return new_obj("elf_lantern", bm, [PALE, SILVER, ELFGLOW, LEAF])


def rope_bridge():
    """a span of the walkways between the trees: planks on two foot ropes, rope handrails, netting between"""
    bm = bmesh.new()
    L = 6.0
    sag = lambda y: -0.35 * math.sin(math.pi * (y + L / 2) / L)
    for i in range(20):
        y = -L / 2 + 0.15 + i * (L - 0.3) / 19
        z = 1.0 + sag(y)
        box(bm, V(-0.55, y - 0.11, z - 0.04), V(0.55, y + 0.11, z + 0.02), 0 if i % 3 else 2, bevel=0.012,
            rot=Matrix.Rotation(0.03 * math.sin(i * 2.3), 3, "Y"))
    for x in (-0.5, 0.5):
        tube(bm, [V(x, y, 0.97 + sag(y)) for y in [-L / 2 + i * L / 16 for i in range(17)]], 0.025, 1, sides=5)
        tube(bm, [V(x * 1.15, y, 1.95 + sag(y) * 0.7) for y in [-L / 2 + i * L / 16 for i in range(17)]], 0.03, 1, sides=5)
        for i in range(13):
            y = -L / 2 + 0.25 + i * (L - 0.5) / 12
            tube(bm, [V(x, y, 0.98 + sag(y)), V(x * 1.15, y, 1.95 + sag(y) * 0.7)], 0.012, 1, sides=3)
    for y in (-L / 2, L / 2):
        for x in (-0.6, 0.6):
            cyl(bm, V(x, y, 0), 0.08, 2.15, 2, seg=8)
            leafy(bm, V(x, y, 2.15), V(0.2 * x, 0, 1), 0.3, 3)
    return new_obj("rope_bridge", bm, [PALEX, ROPE, PALE, LEAF])


def wind_chimes():
    """silver tubes and pale crystals on threads from a carved hoop, a leaf for the wind to catch"""
    bm = bmesh.new()
    tube(bm, ring(V(0, 0, 1.6), 0.22, "Z", 18), 0.018, 0, sides=5, closed=True)
    for k in range(3):
        a = k * 2.094
        tube(bm, [V(0.22 * math.cos(a), 0.22 * math.sin(a), 1.6), V(0, 0, 1.85)], 0.006, 3, sides=3)
    tube(bm, [V(0, 0, 1.85), V(0, 0, 2.0)], 0.006, 3, sides=3)
    for k in range(7):
        a = k * 0.9
        x, y = 0.18 * math.cos(a), 0.18 * math.sin(a)
        L = 0.3 + 0.05 * (k % 4)
        tube(bm, [V(x, y, 1.6), V(x, y, 1.5)], 0.004, 3, sides=3)
        if k % 2:
            cyl(bm, V(x, y, 1.5 - L), 0.018, L, 1, seg=8)
        else:
            ellipsoid(bm, V(x, y, 1.42), (0.035, 0.035, 0.07), 2, seg=6)
    tube(bm, [V(0, 0, 1.6), V(0, 0, 1.15)], 0.004, 3, sides=3)
    leafy(bm, V(0, 0, 1.15), V(0.2, 0, -1), 0.22, 4)
    return new_obj("wind_chimes", bm, [PALE, SILVER, ELFGLOW, ROPE, LEAF])


def elf_arch():
    """the way in: two living branches rising and twining into a pointed arch, carved leaves, a vine hanging"""
    bm = bmesh.new()
    for s_ in (-1, 1):
        pts = [V(s_ * (1.3 - 0.15 * math.sin(t * 3)), 0.06 * math.sin(t * 7), 0) + V(0, 0, 0) for t in [0]]
        path = []
        for i in range(25):
            t = i / 24
            ang = t * math.pi / 2
            x = s_ * (1.3 * math.cos(ang) ** 0.9 + 0.05 * math.sin(t * 9))
            z = 3.6 * math.sin(ang) ** 1.1 + 0.25 * t
            path.append(V(x, 0.08 * math.sin(t * 6 + s_), z))
        tube(bm, path, lambda u: 0.22 - 0.13 * u, 0, sides=8)
        for k in range(3):                                                      # roots splaying at the foot
            a = s_ * 0.5 + (k - 1) * 0.7
            tube(bm, [V(s_ * 1.3, 0, 0.3), V(s_ * 1.3 + 0.45 * math.cos(a) * s_, 0.45 * math.sin(a), 0.0)], lambda u: 0.12 - 0.08 * u, 0, sides=6)
        for k in range(6):
            t = 0.25 + k * 0.12
            p = path[int(t * 24)]
            leafy(bm, p + V(0, 0.15, 0), V(-s_ * 0.3, 0.6, 0.4 - 0.2 * k), 0.35, 1)
    tube(bm, [V(0, 0, 3.85), V(0.15, 0.1, 3.5), V(-0.1, 0.12, 3.1), V(0.05, 0.1, 2.7)], 0.02, 2, sides=4)
    for k in range(5):
        leafy(bm, V(0.05 * math.sin(k), 0.12, 3.6 - k * 0.22), V(0.5 * (-1) ** k, 0.4, -0.5), 0.14, 1)
    lantern = ellipsoid(bm, V(0, 0.05, 3.25), (0.07, 0.07, 0.1), 3, seg=8)
    return new_obj("elf_arch", bm, [PALE, LEAF, mottled("elf_vine", stops("#2a3a1a", "#3e5a24", "#5a7a30"), 8.0, 0.8), ELFGLOW])


def moon_basin():
    """a carved stone basin on a root-wrapped pedestal, its water glowing faintly"""
    bm = bmesh.new()
    lathe(bm, [(0.0, 0.0), (0.45, 0.0), (0.4, 0.1), (0.2, 0.25), (0.16, 0.6), (0.24, 0.75), (0.55, 0.85), (0.62, 1.0), (0.56, 1.02), (0.0, 0.92)],
          V(0, 0, 0), 0, seg=24)
    cyl(bm, V(0, 0, 0.9), 0.54, 0.06, 1, seg=24)
    for k in range(5):
        a = k * 1.256
        tube(bm, [V(0.5 * math.cos(a + 0.4), 0.5 * math.sin(a + 0.4), 0.0), V(0.24 * math.cos(a), 0.24 * math.sin(a), 0.3),
                  V(0.19 * math.cos(a - 0.6), 0.19 * math.sin(a - 0.6), 0.6), V(0.3 * math.cos(a - 0.9), 0.3 * math.sin(a - 0.9), 0.82)],
             lambda u: 0.06 - 0.03 * u, 2, sides=6)
    for k in range(8):
        a = k * 0.785
        leafy(bm, V(0.6 * math.cos(a), 0.6 * math.sin(a), 0.97), V(math.cos(a), math.sin(a), 0.1), 0.16, 3)
    return new_obj("moon_basin", bm, [ELFSTONE, MOONWATER, PALE, LEAF])


def herb_rack():
    """a bent branch frame hung with bundles of drying herbs and flowers"""
    bm = bmesh.new()
    for x in (-0.9, 0.9):
        tube(bm, curve(V(x, 0, 0), V(x * 0.95, 0, 1.8), V(x * 0.1, 0.1, 0)), 0.04, 0, sides=6)
    tube(bm, curve(V(-0.95, 0, 1.75), V(0.95, 0, 1.75), V(0, 0, 0.15)), 0.035, 0, sides=6)
    cols = [4, 5, 6, 4, 5, 6, 4]
    for k in range(7):
        x = -0.72 + k * 0.24
        z = 1.75 + 0.15 * math.sin(math.pi * (x + 0.95) / 1.9)
        tube(bm, [V(x, 0, z), V(x, 0, z - 0.12)], 0.006, 1, sides=3)
        tube(bm, [V(x, 0, z - 0.12), V(x, 0, z - 0.5)], lambda u: 0.02 + 0.07 * u, 2, sides=6)
        heap(bm, V(x, 0, z - 0.55), (0.09, 0.08, 0.08), cols[k], k, 0.03, 8.0)
    return new_obj("herb_rack", bm, [PALE, ROPE, MOSSY, mottled("elf_lav", stops("#3a2a5a", "#6a4a8a", "#9a7ab8"), 20.0, 0.8),
                                     mottled("elf_marig", stops("#8a4a10", "#c87a1a", "#e8a83a"), 20.0, 0.8),
                                     mottled("elf_sage", stops("#4a5a3a", "#7a8a5a", "#a8b484"), 20.0, 0.8),
                                     mottled("elf_rose", stops("#6a1a2a", "#a83040", "#d86070"), 20.0, 0.8)])


def elf_banner():
    """a tall curved standard, a long silk banner flowing from it, the tree sigil stitched in silver"""
    bm = bmesh.new()
    tube(bm, curve(V(0, 0, 0), V(0, 0.4, 4.2), V(0, -0.25, 0)), lambda u: 0.07 - 0.03 * u, 0, sides=8)
    tube(bm, [V(0, 0.4, 4.0), V(0.0, 0.4, 4.0) + V(0.9, 0, 0.1)], 0.025, 2, sides=5)
    rows = sheet(bm, V(0.02, 0.4, 4.0), V(0.85, 0, 0), V(0, 0, -2.6), 6, 12, 1,
                 lambda a, b: V(0.1 * b * math.sin(b * 4), 0.15 * math.sin(b * 5 + a * 2) * b, 0) + V(0, 0, -0.3 * b * b * (a - 0.5) if b > 0.85 else 0))
    thick(bm, rows, 0.01, 1)
    for k in range(3):                                                          # the sigil: a stitched tree
        tube(bm, [V(0.42, 0.37, 3.1 - 0.0), V(0.42 + 0.18 * (k - 1), 0.37, 3.45)], 0.012, 2, sides=3)
    tube(bm, [V(0.42, 0.37, 2.8), V(0.42, 0.37, 3.1)], 0.015, 2, sides=3)
    leafy(bm, V(0, 0.4, 4.2), V(0, 0.2, 1), 0.3, 3)
    return new_obj("elf_banner", bm, [PALE, SILK, SILVER, LEAF])


def archery_butts():
    """an archer's mark: a woven straw target on a tripod, a rack of longbows and a quiver beside it"""
    bm = bmesh.new()
    for a in (0.0, 2.2, 4.1):
        tube(bm, [V(0, 0, 1.8), V(0.7 * math.cos(a), 0.7 * math.sin(a) - 0.2, 0)], 0.035, 0, sides=5)
    cyl(bm, V(0, 0.25, 1.15), 0.6, 0.18, 1, seg=24, axis="Y")
    for r, mi in ((0.45, 4), (0.3, 5), (0.15, 4), (0.06, 6)):
        cyl(bm, V(0, 0.44, 1.15), r, 0.005 + 0.002 * (0.6 - r), mi, seg=24, axis="Y")
    for k in range(3):
        tube(bm, [V(0.1 * (k - 1), 0.44, 1.15 + 0.08 * k), V(0.1 * (k - 1) + 0.05, 0.95, 1.2 + 0.08 * k)], 0.008, 0, sides=3)
    box(bm, V(1.0, -0.05, 0), V(1.08, 0.05, 1.5), 0, bevel=0.01)
    box(bm, V(1.9, -0.05, 0), V(1.98, 0.05, 1.5), 0, bevel=0.01)
    box(bm, V(1.0, -0.05, 1.3), V(1.98, 0.05, 1.36), 0, bevel=0.01)
    for k in range(3):
        x = 1.2 + k * 0.3
        tube(bm, curve(V(x, 0.08, 0.05), V(x, 0.08, 1.6), V(0, 0.18, 0)), 0.018, 2, sides=5)
        tube(bm, [V(x, 0.08, 0.05), V(x, 0.08, 1.6)], 0.004, 3, sides=3)
    lathe(bm, [(0.0, 0.0), (0.09, 0.0), (0.1, 0.6), (0.0, 0.6)], V(2.2, 0.0, 0.0), 7, seg=10)
    for k in range(5):
        tube(bm, [V(2.2 + 0.04 * math.cos(k), 0.04 * math.sin(k), 0.55), V(2.2 + 0.05 * math.cos(k), 0.05 * math.sin(k), 0.9)], 0.008, 0, sides=3)
    return new_obj("archery_butts", bm, [PALE, STRAW, PALEX, ROPE, CREAM, SILK, mat("elf_gold", lin("#c8a040"), 0.3, Metallic=1.0), mottled("elf_leather", stops("#3a2414", "#5a3a20", "#7a5434"), 10.0, 0.7)])


# ================================================================ the dwarfs' (Anvilgate, a carved gate in a mountain's face)

DSTONE = mottled("dw_stone", stops("#24262a", "#3a3d42", "#555960"), 4.0, 0.8)
DGOLD = mat("dw_gold", lin("#c08a2a"), 0.3, Metallic=1.0)
BRASS = mat("dw_brass", lin("#8a6a2a"), 0.35, Metallic=1.0)
DIRON = rusty("dw_iron", (0.035, 0.035, 0.038), (0.22, 0.1, 0.05), 0.75, 0.5, 0.85)
LEATHER = mottled("dw_leather", stops("#2a1810", "#4a2c18", "#6a4228"), 10.0, 0.6)
EMBER = glass("dw_ember", lin("#ff7a20"), 8.0)
COAL = mottled("dw_coal", stops("#0c0c0c", "#1c1a1a", "#2c2828"), 12.0, 0.9)
ORE = mottled("dw_ore", stops("#3a2a24", "#6a4a3a", "#8a6a54"), 6.0, 0.8)
GEMC = glass("dw_gem", lin("#4ad8e8"), 2.5)
RUNE = glass("dw_rune", lin("#ffb840"), 5.0)
DWOOD = wood("dw_wood", stops("#2a1a10", "#46301e", "#5e4430"), "Z", 20.0)
DWOODY = wood("dw_woody", stops("#2a1a10", "#46301e", "#5e4430"), "Y", 20.0)


def mine_cart():
    """a dwarven ore cart: an iron-banded tub with riveted corners and a gold-rimmed lip, heaped with ore and a gem"""
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in (V(-0.42, -0.6, 0.25), V(0.42, -0.6, 0.25), V(0.42, 0.6, 0.25), V(-0.42, 0.6, 0.25),
                                    V(-0.52, -0.72, 0.95), V(0.52, -0.72, 0.95), V(0.52, 0.72, 0.95), V(-0.52, 0.72, 0.95))]
    for f in ((3, 2, 1, 0), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[i] for i in f]).material_index = 0
    for z in (0.35, 0.65):
        w = 0.42 + (z - 0.25) / 0.7 * 0.1
        d = 0.6 + (z - 0.25) / 0.7 * 0.12
        tube(bm, [V(-w - 0.01, -d - 0.01, z), V(w + 0.01, -d - 0.01, z), V(w + 0.01, d + 0.01, z), V(-w - 0.01, d + 0.01, z)], 0.025, 1, sides=4, closed=True)
    tube(bm, [V(-0.53, -0.73, 0.95), V(0.53, -0.73, 0.95), V(0.53, 0.73, 0.95), V(-0.53, 0.73, 0.95)], 0.035, 2, sides=5, closed=True)
    for x in (-0.36, 0.36):
        for y in (-0.42, 0.42):
            cyl(bm, V(x + (0.08 if x > 0 else -0.14), y, 0.17), 0.16, 0.06, 1, seg=14, axis="X")
            cyl(bm, V(x + (0.08 if x > 0 else -0.14) - 0.01, y, 0.17), 0.05, 0.08, 2, seg=8, axis="X")
    for k in range(9):
        a = k * 0.8
        vs2 = ellipsoid(bm, V(0.25 * math.cos(a) * (k > 0), 0.4 * math.sin(a) * (k > 0), 0.95 + 0.08 * (k == 0)), (0.16, 0.16, 0.12), 3, seg=8)
        displace(vs2, 0.04, 5.0, k)
    for k in range(3):
        tube(bm, [V(0.05, 0.1, 1.0), V(0.05 + 0.08 * (k - 1), 0.1 + 0.05 * k, 1.28)], lambda u: 0.05 - 0.04 * u, 4, sides=6)
    tube(bm, [V(0, 0.73, 0.75), V(0, 0.95, 0.75), V(0, 0.95, 0.55)], 0.03, 1, sides=5)
    return new_obj("mine_cart", bm, [DIRON, DIRON, DGOLD, ORE, GEMC])


def rails():
    """a straight run of dwarven track: oak sleepers on gravel, iron rails spiked down"""
    bm = bmesh.new()
    for i in range(6):
        y = -1.25 + i * 0.5
        box(bm, V(-0.55, y - 0.1, 0.0), V(0.55, y + 0.1, 0.1), 0, bevel=0.01)
        for x in (-0.36, 0.36):
            box(bm, V(x - 0.07, y - 0.03, 0.1), V(x - 0.04, y + 0.03, 0.15), 1)
    for x in (-0.36, 0.36):
        box(bm, V(x - 0.03, -1.5, 0.1), V(x + 0.03, 1.5, 0.18), 1, bevel=0.005)
        box(bm, V(x - 0.05, -1.5, 0.1), V(x + 0.05, 1.5, 0.12), 1)
    for k in range(30):
        import random as _r
        rr = _r.Random(k)
        ellipsoid(bm, V(rr.uniform(-0.6, 0.6), rr.uniform(-1.45, 1.45), 0.01), (0.06, 0.06, 0.03), 2, seg=6)
    return new_obj("rails", bm, [DWOODY, DIRON, DSTONE])


def forge_anvil():
    """the forge yard's heart: a stone hearth glowing with coals under its hood, the great bellows, the anvil on its stump"""
    bm = bmesh.new()
    box(bm, V(-0.9, -0.6, 0), V(0.9, 0.6, 0.9), 0, bevel=0.03)
    box(bm, V(-0.95, -0.65, 0.85), V(0.95, 0.65, 0.95), 1, bevel=0.02)
    for k in range(18):
        import random as _r
        rr = _r.Random(k)
        vs = ellipsoid(bm, V(rr.uniform(-0.6, 0.6), rr.uniform(-0.35, 0.35), 0.97), (0.1, 0.1, 0.06), 2 if k % 3 else 3, seg=6)
    vs = [bm.verts.new(p) for p in (V(-0.95, -0.65, 1.9), V(0.95, -0.65, 1.9), V(0.95, 0.65, 1.9), V(-0.95, 0.65, 1.9),
                                    V(-0.3, -0.3, 2.6), V(0.3, -0.3, 2.6), V(0.3, 0.3, 2.6), V(-0.3, 0.3, 2.6))]
    for f in ((0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[i] for i in f]).material_index = 0
    for x in (-0.9, 0.9):
        box(bm, V(x - 0.07, 0.48, 0.9), V(x + 0.07, 0.62, 1.9), 0)
    box(bm, V(-0.3, -0.3, 2.6), V(0.3, 0.3, 3.4), 0)
    box(bm, V(-0.35, -0.35, 3.4), V(0.35, 0.35, 3.48), 1)
    # the bellows, its nozzle to the fire
    vs = [bm.verts.new(p) for p in (V(1.0, -0.35, 0.6), V(2.1, -0.15, 0.6), V(2.1, 0.15, 0.6), V(1.0, 0.35, 0.6),
                                    V(1.0, -0.35, 0.85), V(2.1, -0.15, 0.95), V(2.1, 0.15, 0.95), V(1.0, 0.35, 0.85))]
    for f in ((0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)):
        bm.faces.new([vs[i] for i in f]).material_index = 4
    box(bm, V(1.0, -0.38, 0.55), V(2.2, 0.38, 0.6), 5)
    tube(bm, [V(1.0, 0, 0.72), V(0.85, 0, 0.75)], 0.05, 6, sides=6)
    box(bm, V(1.4, -0.4, 0), V(1.5, -0.3, 0.55), 5)
    box(bm, V(1.4, 0.3, 0), V(1.5, 0.4, 0.55), 5)
    tube(bm, [V(2.1, 0, 0.95), V(2.3, 0, 1.4)], 0.025, 5, sides=5)
    # the anvil on its stump
    cyl(bm, V(0.0, 1.5, 0.0), 0.35, 0.55, 5, seg=14)
    box(bm, V(-0.12, 1.4, 0.55), V(0.12, 1.6, 0.75), 6, bevel=0.01)
    box(bm, V(-0.3, 1.38, 0.75), V(0.3, 1.62, 0.9), 6, bevel=0.015)
    tube(bm, [V(0.3, 1.5, 0.85), V(0.55, 1.5, 0.83)], lambda u: 0.07 - 0.065 * u, 6, sides=8)
    box(bm, V(-0.22, 1.42, 0.9), V(0.15, 1.58, 0.92), 7)
    tube(bm, [V(-0.1, 1.75, 0.0), V(-0.1, 1.75, 0.45)], 0.02, 5, sides=5)
    box(bm, V(-0.16, 1.7, 0.45), V(-0.04, 1.8, 0.55), 6)
    return new_obj("forge_anvil", bm, [DSTONE, DIRON, COAL, EMBER, LEATHER, DWOOD, DIRON, EMBER])


def ore_pile():
    """a heap of broken ore by the mine's mouth: rock, rusty lumps, gold glints and a cyan crystal growing out"""
    bm = bmesh.new()
    import random as _r
    rr = _r.Random(4)
    for k in range(26):
        a, r = rr.uniform(0, 6.28), rr.uniform(0, 0.8)
        z = 0.12 + (0.8 - r) * 0.55 + rr.uniform(-0.05, 0.05)
        vs = ellipsoid(bm, V(r * math.cos(a), r * math.sin(a), z), (rr.uniform(0.14, 0.24),) * 2 + (0.13,), rr.choice((0, 0, 1, 2)), seg=8)
        displace(vs, 0.05, 4.0, k)
    for k in range(4):
        a = k * 1.57 + 0.3
        tube(bm, [V(0.15 * math.cos(a), 0.15 * math.sin(a), 0.5), V(0.4 * math.cos(a), 0.4 * math.sin(a), 0.95 + 0.1 * k)],
             lambda u: 0.07 - 0.06 * u, 3, sides=6)
    tube(bm, [V(0.9, 0.3, 0.0), V(0.75, 0.2, 0.9)], 0.025, 4, sides=5)
    vs = [bm.verts.new(p) for p in (V(0.72, 0.18, 0.88), V(0.95, 0.25, 0.95), V(0.72, 0.18, 0.98))]
    bm.faces.new(vs).material_index = 4
    return new_obj("ore_pile", bm, [ORE, DSTONE, DGOLD, GEMC, DIRON])


def lift_cage():
    """the hold's lift: an iron cage on chains under a pulley beam, its gate folded open, a brass lever"""
    bm = bmesh.new()
    for x in (-0.75, 0.75):
        for y in (-0.75, 0.75):
            box(bm, V(x - 0.05, y - 0.05, 0.1), V(x + 0.05, y + 0.05, 2.3), 0)
    box(bm, V(-0.8, -0.8, 0), V(0.8, 0.8, 0.12), 1, bevel=0.01)
    box(bm, V(-0.8, -0.8, 2.3), V(0.8, 0.8, 2.4), 0)
    for k in range(7):
        t = -0.6 + k * 0.2
        for side in ((t, -0.75), (t, 0.75)):
            tube(bm, [V(side[0], side[1], 0.12), V(side[0], side[1], 2.3)], 0.015, 0, sides=4)
        tube(bm, [V(-0.75, t, 0.12), V(-0.75, t, 2.3)], 0.015, 0, sides=4)
    for z in (0.8, 1.6):
        tube(bm, [V(-0.75, -0.75, z), V(0.75, -0.75, z), V(0.75, 0.75, z) if False else V(0.75, -0.75, z)], 0.02, 0, sides=4) if False else None
        tube(bm, [V(0.75, 0.75, z), V(-0.75, 0.75, z), V(-0.75, -0.75, z), V(0.75, -0.75, z)], 0.02, 0, sides=4)
    for k in range(4):                                                          # the gate, folded back against the side
        tube(bm, [V(0.78 + 0.05 * k, 0.75 - 0.0, 0.15), V(0.78 + 0.05 * k, 0.75, 2.2)], 0.012, 0, sides=4)
    for x, y in ((-0.75, -0.75), (0.75, -0.75), (0.75, 0.75), (-0.75, 0.75)):
        links(bm, V(x, y, 2.4), V(0, 0, 3.4), 0, w=0.05, r=0.01)
    box(bm, V(-1.3, -0.1, 3.4), V(1.3, 0.1, 3.6), 3, bevel=0.02)
    cyl(bm, V(-0.08, 0, 3.4), 0.25, 0.16, 2, seg=16, axis="X")
    tube(bm, [V(0.5, -0.6, 0.12), V(0.5, -0.6, 1.0)], 0.02, 2, sides=5)
    ellipsoid(bm, V(0.5, -0.6, 1.02), (0.05, 0.05, 0.05), 2, seg=8)
    return new_obj("lift_cage", bm, [DIRON, DSTONE, BRASS, DSTONE])


GLYPHS = [  # our own angular runes: strokes in a 1 x 2 cell, (x0, z0, x1, z1)
    [(0, 0, 0, 2), (0, 2, 0.8, 1.4), (0, 1.3, 0.8, 0.7)],
    [(0, 0, 0, 2), (0.8, 0, 0.8, 2), (0, 2, 0.8, 1.2)],
    [(0.4, 0, 0.4, 2), (0, 1.6, 0.4, 2), (0.8, 1.6, 0.4, 2), (0, 0.4, 0.8, 0.4)],
    [(0, 0, 0, 2), (0, 2, 0.8, 1.0), (0.8, 1.0, 0, 0)],
    [(0.4, 0, 0.4, 2), (0, 1.2, 0.8, 1.8), (0.8, 1.2, 0, 1.8)],
    [(0, 0, 0.4, 2), (0.4, 2, 0.8, 0), (0.15, 0.8, 0.65, 0.8)],
]


def rune(bm, x, y, z, k, size, mi):
    """one glyph cut into a face at (x, y, z), its strokes as little bars"""
    for (a, b, c, d) in GLYPHS[k % len(GLYPHS)]:
        p0, p1 = V(x + (a - 0.4) * size, y, z + b * size), V(x + (c - 0.4) * size, y, z + d * size)
        tube(bm, [p0, p1], size * 0.09, mi, sides=4)


def rune_door():
    """a hold door three blocks wide: two stone leaves under a carved lintel, runes inlaid glowing, iron studs and rings"""
    bm = bmesh.new()
    box(bm, V(-1.8, -0.25, 0), V(-1.4, 0.25, 4.0), 0, bevel=0.03)
    box(bm, V(1.4, -0.25, 0), V(1.8, 0.25, 4.0), 0, bevel=0.03)
    vs = [bm.verts.new(p) for p in (V(-1.95, -0.3, 4.0), V(1.95, -0.3, 4.0), V(1.95, 0.3, 4.0), V(-1.95, 0.3, 4.0),
                                    V(-1.5, -0.3, 4.7), V(1.5, -0.3, 4.7), V(1.5, 0.3, 4.7), V(-1.5, 0.3, 4.7))]
    for f in ((0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7), (3, 2, 1, 0)):
        bm.faces.new([vs[i] for i in f]).material_index = 0
    for s_ in (-1, 1):
        box(bm, V(s_ * 1.4 if s_ < 0 else 0.02, -0.12, 0), V(-0.02 if s_ < 0 else 1.4, 0.12, 3.9), 1, bevel=0.02)
        for r in range(5):
            for c in range(2):
                ellipsoid(bm, V(s_ * (0.35 + c * 0.7), 0.13, 0.5 + r * 0.75), (0.05, 0.03, 0.05), 2, seg=6)
        tube(bm, ring(V(s_ * 0.25, 0.18, 1.6), 0.12, "Y", 14), 0.022, 2, sides=5, closed=True)
        for k in range(3):                                                      # runes cut down each leaf
            rune(bm, s_ * 0.7, 0.14, 2.25 + k * 0.5, k * 2 + (s_ > 0), 0.18, 3)
    for k in range(7):                                                          # the runes down the jambs and on the lintel
        z = 0.45 + k * 0.48
        for j, x in enumerate((-1.6, 1.6)):
            rune(bm, x, 0.27, z, k + 3 * j, 0.17, 3)
    for k in range(9):
        if k != 4:
            rune(bm, -1.2 + k * 0.3, 0.32, 4.15, k * 2 + 1, 0.15, 3)
    box(bm, V(-0.35, 0.3, 4.1), V(0.35, 0.32, 4.6), 4)
    return new_obj("rune_door", bm, [DSTONE, mottled("dw_door", stops("#2e3034", "#46494e", "#5e6268"), 3.0, 0.75), DIRON, RUNE, DGOLD])


def ale_cask():
    """a great ale cask on a stone cradle, brass tap and a row of tankards on the board below"""
    bm = bmesh.new()
    prof = [(0.0, -0.8), (0.55, -0.8), (0.62, -0.5), (0.66, 0.0), (0.62, 0.5), (0.55, 0.8), (0.0, 0.8)]
    lathe(bm, prof, V(0, 0, 0.95), 0, seg=24, axis="Y")
    for y in (-0.62, -0.25, 0.25, 0.62):
        r = 0.66 - 0.11 * (abs(y) / 0.8) ** 2
        tube(bm, ring(V(0, y, 0.95), r + 0.015, "Y", 24), 0.025, 1, sides=4, closed=True)
    for y in (-0.5, 0.5):
        box(bm, V(-0.55, y - 0.15, 0), V(0.55, y + 0.15, 0.35), 2, bevel=0.02)
    tube(bm, [V(0, 0.8, 0.6), V(0, 0.98, 0.6), V(0, 0.98, 0.5)], 0.035, 3, sides=6)
    box(bm, V(-0.9, 0.95, 0.0), V(0.9, 1.35, 0.06), 4, bevel=0.01)
    for k in range(4):
        x = -0.6 + k * 0.4
        lathe(bm, [(0.0, 0.06), (0.1, 0.06), (0.11, 0.25), (0.0, 0.25)], V(x, 1.15, 0), 5, seg=12)
        tube(bm, [V(x + 0.1, 1.15, 0.2), V(x + 0.17, 1.15, 0.17), V(x + 0.1, 1.15, 0.1)], 0.015, 5, sides=4)
    return new_obj("ale_cask", bm, [DWOODY, DIRON, DSTONE, BRASS, DWOOD, BRASS])


def tool_rack():
    """a rack of the hold's tools: two picks, a sledge, a shovel, a lantern hung on its peg"""
    bm = bmesh.new()
    for x in (-0.9, 0.9):
        box(bm, V(x - 0.05, -0.05, 0), V(x + 0.05, 0.05, 1.8), 0, bevel=0.01)
    for z in (0.3, 1.5):
        box(bm, V(-0.95, -0.06, z), V(0.95, 0.06, z + 0.08), 0, bevel=0.01)
    tools = [(-0.6, "pick"), (-0.25, "sledge"), (0.1, "pick"), (0.45, "shovel")]
    for x, kind in tools:
        tube(bm, [V(x, 0.1, 0.25), V(x, 0.1, 1.65)], 0.025, 0, sides=6)
        if kind == "pick":
            tube(bm, curve(V(x - 0.32, 0.1, 1.55), V(x + 0.32, 0.1, 1.55), V(0, 0, 0.1)), lambda u: 0.035 * (1 - abs(u - 0.5) * 1.6) + 0.006, 1, sides=5)
        elif kind == "sledge":
            box(bm, V(x - 0.15, 0.02, 1.58), V(x + 0.15, 0.18, 1.78), 1, bevel=0.02)
        else:
            box(bm, V(x - 0.13, 0.08, 0.05), V(x + 0.13, 0.12, 0.35), 1, bevel=0.02)
    tube(bm, [V(0.75, 0.05, 1.5), V(0.75, 0.2, 1.5)], 0.015, 1, sides=4)
    box(bm, V(0.67, 0.13, 1.1), V(0.83, 0.29, 1.4), 2)
    box(bm, V(0.65, 0.11, 1.4), V(0.85, 0.31, 1.45), 1)
    box(bm, V(0.65, 0.11, 1.06), V(0.85, 0.31, 1.1), 1)
    return new_obj("tool_rack", bm, [DWOOD, DIRON, EMBER])


def stone_brazier():
    """a squat dwarven brazier: a carved stone bowl on three feet, gold-banded, coals burning in it"""
    bm = bmesh.new()
    lathe(bm, [(0.0, 0.35), (0.3, 0.35), (0.55, 0.5), (0.65, 0.75), (0.6, 0.82), (0.0, 0.7)], V(0, 0, 0), 0, seg=20)
    tube(bm, ring(V(0, 0, 0.62), 0.62, "Z", 20), 0.03, 1, sides=4, closed=True)
    for k in range(3):
        a = k * 2.094
        box(bm, V(0.32 * math.cos(a) - 0.1, 0.32 * math.sin(a) - 0.1, 0), V(0.32 * math.cos(a) + 0.1, 0.32 * math.sin(a) + 0.1, 0.42), 0, bevel=0.02)
    for k in range(10):
        a = k * 0.63
        ellipsoid(bm, V(0.28 * math.cos(a) * (k > 0), 0.28 * math.sin(a) * (k > 0), 0.76), (0.12, 0.12, 0.07), 2 if k % 2 else 3, seg=6)
    for k in range(3):
        tube(bm, [V(0.1 * math.cos(k * 2), 0.1 * math.sin(k * 2), 0.78), V(0.05 * math.cos(k * 2), 0.05 * math.sin(k * 2), 1.15 + 0.08 * k)],
             lambda u: 0.07 * (1 - u), 3, sides=5)
    return new_obj("stone_brazier", bm, [DSTONE, DGOLD, COAL, EMBER])

SETS = {
    "lake": [(net_rack, (512, 512)), (fish_rack, (256, 256)), (eel_traps, (256, 256)), (reed_sheaves, (256, 256)),
             (lake_lantern, (128, 128)), (dugout, (256, 256)), (mooring_post, (128, 128)), (catch_basket, (256, 256))],
    "elf": [(elf_arch, (512, 512)), (rope_bridge, (512, 512)), (elf_banner, (256, 256)), (archery_butts, (256, 256)),
            (elf_lantern, (128, 128)), (wind_chimes, (128, 128)), (moon_basin, (256, 256)), (herb_rack, (256, 256))],
    "dwarf": [(rune_door, (512, 512)), (forge_anvil, (512, 512)), (lift_cage, (256, 256)), (ale_cask, (256, 256)),
              (mine_cart, (256, 256)), (rails, (256, 256)), (ore_pile, (256, 256)), (tool_rack, (256, 256)), (stone_brazier, (256, 256))],
    "cliff": [(hoist_crane, (512, 512)), (rope_ladder, (256, 256)), (lift_basket, (512, 512)), (toll_barrier, (256, 256))],
}

MAKE = [(hay_cart, (512, 512)), (covered_wagon, (512, 512)), (handcart, (256, 256)), (wheelbarrow, (256, 256)),
        (well, (512, 512)), (market_stall, (512, 512)), (signpost, (256, 256)), (washing_line, (256, 256)),
        (scarecrow, (256, 256)), (skeps, (256, 256)), (woodpile, (256, 256)), (churns_sacks, (256, 256)),
        (punt, (256, 256)), (village_bell, (256, 256))]
BIG = [(windmill_sails, (1024, 1024)), (water_wheel, (512, 512))]


def scene(done, out, gap=0.8, cam_h=0.55, lens=40, rows=2):
    """props stood in rows on a grass-green floor, spaced by their own widths, lit like a summer afternoon"""
    for o, img in done:
        m = bpy.data.materials.new(o.name + "_baked")
        m.use_nodes = True
        b = bsdf(m)
        b.inputs["Roughness"].default_value = 0.75
        t = node(m, "ShaderNodeTexImage")
        t.image = img
        t.interpolation = "Closest"
        link(m, t.outputs["Color"], b.inputs["Base Color"])
        o.data.materials.clear()
        o.data.materials.append(m)
    per = math.ceil(len(done) / rows)
    width = 0
    for r in range(rows):
        part = done[r * per:(r + 1) * per]
        x = 0.0
        for o, img in part:
            bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
            mnx, mxx = min(v.x for v in bb), max(v.x for v in bb)
            mnz = min(v.z for v in bb)
            o.location = (x - mnx, -r * 4.6, -mnz if o.name not in ("windmill_sails", "water_wheel") else -mnz)
            x += (mxx - mnx) + gap
        width = max(width, x)
    cx = width / 2
    fl = bpy.data.meshes.new("floor")
    bmf = bmesh.new()
    bmesh.ops.create_grid(bmf, x_segments=1, y_segments=1, size=width + 20, matrix=Matrix.Translation((cx, -4, 0)))
    bmf.to_mesh(fl)
    fo = bpy.data.objects.new("floor", fl)
    sc.collection.objects.link(fo)
    fl.materials.append(mottled("grass", stops("#2c4a1c", "#3e6226", "#52762e"), 3.0, 0.9))
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.62, 0.8, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy, sun.color, sun.angle = 3.2, (1.0, 0.9, 0.76), 0.08
    so = bpy.data.objects.new("sun", sun)
    so.rotation_euler = (math.radians(50), 0, math.radians(-35))
    sc.collection.objects.link(so)
    sails = any(o.name == "windmill_sails" for o, _ in done)
    tgt = Vector((cx, -(rows - 1) * 4.6 / 2, 11.0 if sails else 0.8))
    cd = bpy.data.cameras.new("cam")
    cd.lens = lens
    co = bpy.data.objects.new("cam", cd)
    tall = max(max((o.matrix_world @ Vector(c)).z for c in o.bound_box) for o, _ in done)
    tgt.z = max(tgt.z, tall * 0.4)
    need = max((width / 2 + 2.0) / (18 / lens), (tall * 0.6 + 1.0) / (9 / lens), (13.5 if sails else 0) / (9 / lens))
    elev = math.radians(8 if sails else 26)
    co.location = tgt + Vector((0, math.cos(elev), math.sin(elev))) * need * 1.02
    co.rotation_euler = (tgt - Vector(co.location)).to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(co)
    sc.camera = co
    sc.render.resolution_x, sc.render.resolution_y = 1800, 900
    sc.cycles.samples = 32 if FAST else 96
    sc.view_settings.view_transform = "AgX"
    sc.render.filepath = os.path.join(RENDERS, out + ".png")
    bpy.ops.render.render(write_still=True)
    print("rendered", sc.render.filepath)


_SHOW = PREVIEW
PREVIEW = False                 # run() mustn't draw its own lineup; scene() below does
SET = next((a for a in ARGS if a in SETS), None)
if SET:
    ONLY = [a for a in ONLY if a != SET]
    done = run(SETS[SET], {LAMP, ELFGLOW, MOONWATER, EMBER, RUNE, GEMC}, "x")
    if _SHOW:
        scene(done, "village_props_" + SET, rows=1 if len(done) < 6 else 2)
elif "big" in ARGS:
    ONLY = [a for a in ONLY if a != "big"]
    done = run(BIG, set(), "x")
    if _SHOW:
        scene(done, "village_props_big", gap=2.0, cam_h=0.25, lens=35, rows=1)
else:
    done = run(MAKE, set(), "x")
    if _SHOW:
        scene(done, "village_props", rows=3 if len(done) > 6 else 1)
