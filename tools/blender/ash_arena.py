"""The Grey Fold (concept, Cycles): the Ash Shepherd's arena, Act III. A burnt hill-town's square torn up out of the world
and floating in a red ash-sky: a cobbled square 120 blocks across under drifts of grey ash, a dry fountain in the
middle where the party lands; round the edge the roofless shells of burnt houses, their windows still glowing like
embers; dead trees, a shepherd's fold of charred hurdles, lamp posts with ember lanterns; the great fallen bell at the
north end where the Shepherd walks in; the island's edge crumbling, ash pouring off it like falls; other burnt islands
drifting far off; a dim eclipsed sun low on the horizon, ash falling forever. Open to the sky.
  blender -b -P tools/blender/ash_arena.py -- [wide|inside] [fast]  ->  tools/renders/ash_arena/fold_<shot>.png"""
import os, sys, math, random
import bpy, bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
_m = open(os.path.join(HERE, "meteor_fall.py"), encoding="utf-8").read()
exec(_m.split("GATE = (0.62")[0])
rs = random.Random(91)
exec("def smoke_mat" + _m.split("def smoke_mat")[1].split("\n# ================================================================ the crater")[0])
_a = open(os.path.join(HERE, "arena_ring.py"), encoding="utf-8").read()
exec("def pixb" + _a.split("def pixb")[1].split("# ---------------------------------------------------------------- the sky")[0])
exec("def mesh_vox" + _a.split("def mesh_vox")[1].split("MATS = {")[0])

SHOT = next((a for a in ARGS if a in ("wide", "inside")), "inside")
OUT = os.path.join(HERE, "..", "renders", "ash_arena")
os.makedirs(OUT, exist_ok=True)
sc.view_settings.exposure = 0.1
EMBER = (1.0, 0.42, 0.12)
HEAT = EMBER

# ---------------------------------------------------------------- the sky: rust-red low, bruised grey overhead, a dark sun
w = bpy.data.worlds.new("w")
sc.world = w
w.use_nodes = True
wt = w.node_tree
for n in list(wt.nodes):
    wt.nodes.remove(n)
wo = N(wt, "ShaderNodeOutputWorld")
tc = N(wt, "ShaderNodeTexCoord")
sep = N(wt, "ShaderNodeSeparateXYZ")
L(wt, tc.outputs["Generated"], sep.inputs[0])
zz = sep.outputs["Z"]
up = mth(wt, "MINIMUM", mth(wt, "MAXIMUM", mth(wt, "MULTIPLY", zz, vb=2.4), vb=0.0), vb=1.0)
down = mth(wt, "MINIMUM", mth(wt, "MAXIMUM", mth(wt, "MULTIPLY", zz, vb=-2.0), vb=0.0), vb=1.0)
sky = mix(wt, up, (0.16, 0.05, 0.025), (0.035, 0.028, 0.03))
sky = mix(wt, down, sky, (0.05, 0.015, 0.01))
nz = N(wt, "ShaderNodeTexNoise", Scale=2.6, Detail=10.0, Roughness=0.62)
L(wt, tc.outputs["Generated"], nz.inputs["Vector"])
sky = mix(wt, mth(wt, "MULTIPLY", mth(wt, "POWER", nz.outputs["Fac"], vb=3.0), vb=1.4), sky, (0.06, 0.05, 0.05))
bg = N(wt, "ShaderNodeBackground", Strength=1.0)
L(wt, sky, bg.inputs["Color"])
L(wt, bg.outputs[0], wo.inputs["Surface"])
sun = bpy.data.objects.new("key", bpy.data.lights.new("key", "SUN"))
sun.data.energy = 1.1
sun.data.color = (1.0, 0.55, 0.35)
sun.data.angle = math.radians(10)
sun.rotation_euler = (Vector((0.2, -0.9, -0.35))).to_track_quat("-Z", "Y").to_euler()
sc.collection.objects.link(sun)

# ---------------------------------------------------------------- the square, block by block
R_SQ, R_EDGE = 60, 64
vox = {}


def put(x, y, z, k):
    vox[(x, y, z)] = k


def edge_r(a):
    return R_EDGE - 3 * (0.5 + 0.5 * math.sin(a * 5 + 0.7)) - 2 * (0.5 + 0.5 * math.sin(a * 13))


for x in range(-R_EDGE - 1, R_EDGE + 2):
    for y in range(-R_EDGE - 1, R_EDGE + 2):
        r = math.hypot(x + 0.5, y + 0.5)
        a = math.atan2(y + 0.5, x + 0.5)
        er = edge_r(a)
        if r > er:
            continue
        bot = -int(44 * (1 - (r / (R_EDGE + 1)) ** 1.6) + 4 * math.sin(a * 4) + rs.random() * 3) - 2
        for z in range(bot, -1):
            put(x, y, z, "rock" if (z < bot + 3 or r > er - 3 or z > -3) else "rock")
        # cobbles, worn into a ring round the fountain; ash drifted over a lot of it
        ring = abs(r - 18) < 1.2 or abs(r - 34) < 1.0
        put(x, y, -1, "kerb" if ring else ("cobble" if (x * 7 + y * 13) % 5 else "cobble2"))
        drift = (math.sin(x * 0.21 + y * 0.13) + math.sin(x * 0.07 - y * 0.19) * 1.3 + rs.random() * 0.5)
        if drift > 1.0 or r > er - 6 and rs.random() < 0.6:
            put(x, y, 0, "ash")
# the dry fountain where the party lands: a low round basin, a broken pillar in it
for x in range(-10, 11):
    for y in range(-10, 11):
        r = math.hypot(x + 0.5, y + 0.5)
        if 8.2 < r < 9.6:
            put(x, y, 0, "kerb")
            put(x, y, 1, "kerb")
        elif r <= 8.2:
            vox.pop((x, y, 0), None)
            put(x, y, -1, "ash")
for z in range(0, 3):
    for x in (-1, 0):
        for y in (14, 15):
            pass


def house(cx, cy, turn, w_, d_, h_):
    """a burnt house: four stone walls, roofless, broken down along the top, windows glowing, a charred beam or two"""
    ca, sa = math.cos(turn), math.sin(turn)

    def p(u, v, z, k):
        put(int(round(cx + u * ca - v * sa)), int(round(cy + u * sa + v * ca)), z, k)
    for u in range(-w_, w_ + 1):
        for v in range(-d_, d_ + 1):
            wall = abs(u) == w_ or abs(v) == d_
            if not wall:
                if rs.random() < 0.3:
                    p(u, v, 0, "ash")
                continue
            top = h_ - int(abs(math.sin(u * 0.9 + v * 0.7 + cx)) * h_ * 0.6)
            for z in range(0, top):
                win = (z in (2, 3)) and (u % 3 == 0) and abs(u) < w_ and abs(v) == d_
                door = abs(u) <= 1 and v == -d_ and z < 3
                if door:
                    continue
                p(u, v, z, "ember_win" if win else ("timber" if z == top - 1 and rs.random() < 0.3 else "wall"))
    for k in range(2):
        uu = rs.randint(-w_ + 1, w_ - 1)
        for v in range(-d_, d_ + 1):
            p(uu, v, h_ - 2 + (v % 2), "timber")


for i in range(11):
    a = i / 11 * math.tau + rs.uniform(-0.1, 0.1)
    if abs(((a - math.pi / 2) + math.pi) % math.tau - math.pi) < 0.35:
        continue                                                    # leave the north open: the bell and the Shepherd
    d = rs.uniform(47, 53)
    house(math.cos(a) * d, math.sin(a) * d, a + math.pi / 2, rs.randint(4, 6), rs.randint(3, 4), rs.randint(7, 11))


def tree(cx, cy, h):
    for z in range(0, h):
        put(cx, cy, z, "char")
    for k in range(4):
        a = rs.uniform(0, math.tau)
        z0 = rs.randint(h // 2, h - 1)
        L_ = rs.randint(3, 6)
        for s_ in range(1, L_):
            put(int(round(cx + math.cos(a) * s_)), int(round(cy + math.sin(a) * s_)), z0 + s_ // 2, "char")


for i in range(9):
    a = rs.uniform(0, math.tau)
    d = rs.uniform(24, 42)
    tree(int(math.cos(a) * d), int(math.sin(a) * d), rs.randint(8, 13))
# the fold: charred hurdles in arcs
for k in range(3):
    a0 = rs.uniform(0, math.tau)
    d = rs.uniform(24, 38)
    for s_ in range(26):
        a = a0 + s_ / d
        x, y = int(round(math.cos(a) * d)), int(round(math.sin(a) * d))
        if s_ % 7 == 6:
            continue
        put(x, y, 0, "fence")
        if s_ % 3 == 0:
            put(x, y, 1, "fence")
# lamp posts with ember lanterns
LAMPS = []
for i in range(10):
    a = i / 10 * math.tau + 0.3
    d = 26 if i % 2 else 40
    x, y = int(math.cos(a) * d), int(math.sin(a) * d)
    for z in range(0, 4):
        put(x, y, z, "iron")
    put(x, y, 4, "lantern")
    LAMPS.append((x + 0.5, y + 0.5, 4.5))
# the great fallen bell at the north, on its side, cracked
bx, by = 0, 50
for x in range(-7, 8):
    for y in range(-6, 7):
        for z in range(0, 12):
            r = math.hypot(x, z - 5.5)
            prof = 4.5 + (y + 6) / 12 * 3.2
            if prof - 1.4 < r < prof and not (y > 4 and r < prof - 0.4):
                put(bx + x, by + y, z, "bronze")
MATS = {
    "rock": pixb("rock", (0.06, 0.055, 0.055), (0.12, 0.11, 0.105)),
    "cobble": pixb("cobble", (0.16, 0.15, 0.145), (0.25, 0.235, 0.225), bricks=(0.08, 0.075, 0.07)),
    "cobble2": pixb("cobble2", (0.12, 0.11, 0.105), (0.2, 0.19, 0.18), bricks=(0.06, 0.055, 0.05)),
    "kerb": pixb("kerb", (0.2, 0.19, 0.18), (0.3, 0.29, 0.27), bricks=(0.1, 0.1, 0.09)),
    "ash": pixb("ash", (0.3, 0.29, 0.28), (0.42, 0.41, 0.4), rough=0.95),
    "wall": pixb("wall", (0.1, 0.09, 0.085), (0.18, 0.165, 0.155), bricks=(0.05, 0.045, 0.04)),
    "timber": pixb("timber", (0.025, 0.02, 0.018), (0.05, 0.04, 0.035)),
    "char": pixb("char", (0.02, 0.018, 0.016), (0.045, 0.04, 0.035)),
    "fence": pixb("fence", (0.035, 0.03, 0.025), (0.07, 0.06, 0.05)),
    "iron": pixb("iron", (0.03, 0.03, 0.032), (0.06, 0.06, 0.065), rough=0.5),
    "bronze": pixb("bronze", (0.12, 0.08, 0.04), (0.22, 0.15, 0.08), rough=0.4),
    "ember_win": glow("ember_win", EMBER, 6.0),
    "lantern": glow("lantern", EMBER, 18.0),
}
mesh_vox(vox, MATS)
print("voxels", len(vox))
for x, y, z in LAMPS:
    point("lamp", (x, y, z), EMBER, 1500, 0.5)

# ash pouring off the island's edge, like falls, and drifting islands far off
for i in range(9):                                                      # ash spilling off the edge in billows
    a = i / 9 * math.tau + rs.uniform(-0.2, 0.2)
    m = puff_mat()
    for k in range(8):
        t = k / 7
        d = edge_r(a) + 2 + 9 * t
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        ob = obj("spill%d_%d" % (i, k), bm, m)
        ob.location = (math.cos(a) * d, math.sin(a) * d, -2 - 26 * t)
        r_ = 3 + 7 * t
        ob.scale = (r_, r_, r_ * 1.3)
        ob.color = (0.0, 0, 0, 1)
bm = bmesh.new()
for i in range(14):
    a = rs.uniform(0, math.tau)
    d = rs.uniform(150, 320)
    c = Vector((math.cos(a) * d, math.sin(a) * d, rs.uniform(-60, 40)))
    s = rs.uniform(5, 16)
    for k in range(int(s * 2)):
        p = c + Vector((rs.uniform(-s, s), rs.uniform(-s, s), -abs(rs.gauss(0, s * 0.5))))
        q = rs.uniform(1.5, 4)
        box(bm, p.x - q, p.y - q, p.z - q, p.x + q, p.y + q, p.z + q)
obj("islands", bm, MATS["rock"])
# the dark sun, low over the north: a black disc with a thin burning rim
bm = bmesh.new()
bmesh.ops.create_circle(bm, cap_ends=True, segments=64, radius=1.0)
o = obj("sun_disc", bm, pix("sundark", (0.0, 0.0, 0.0), (0.01, 0.005, 0.005)))
o.location = (40, 900, 160)
o.scale = (95, 95, 95)
o.rotation_euler = (math.radians(90), 0, 0)
bm = bmesh.new()
bmesh.ops.create_circle(bm, cap_ends=True, segments=64, radius=1.0)
o = obj("sun_rim", bm, glow("sunrim", (1.0, 0.35, 0.1), 8.0))
o.location = (40, 905, 160)
o.scale = (101, 101, 101)
o.rotation_euler = (math.radians(90), 0, 0)
# ash falling, thick; a few embers
bm_a, bm_e = bmesh.new(), bmesh.new()
for i in range(5000):
    p = Vector((rs.uniform(-150, 150), rs.uniform(-150, 170), rs.uniform(-10, 100)))
    q = rs.uniform(0.05, 0.13)
    box(bm_e if rs.random() < 0.05 else bm_a, p.x - q, p.y - q, p.z - q, p.x + q, p.y + q, p.z + q)
obj("ashfall_air", bm_a, pix("ashp", (0.35, 0.34, 0.33), (0.5, 0.49, 0.48)))
obj("embers", bm_e, glow("ember", EMBER, 10))

# ---------------------------------------------------------------- the Shepherd for scale (18 tall), and the party
M_SH = pix("sh", (0.05, 0.048, 0.046), (0.1, 0.095, 0.09), rough=0.9)
sx, sy = 0.0, 40.0
bm = bmesh.new()
box(bm, sx - 2.6, sy - 2.0, 0, sx + 2.6, sy + 2.0, 13.5)                 # the cloak, a long column
box(bm, sx - 4.0, sy - 2.4, 0, sx + 4.0, sy + 2.4, 4.0)                  # its hem, spread on the ground
box(bm, sx - 4.6, sy - 1.8, 10.5, sx + 4.6, sy + 1.8, 14.0)              # shoulders
box(bm, sx - 2.0, sy - 2.6, 14.0, sx + 2.0, sy + 1.8, 18.0)              # the hood
box(bm, sx + 4.4, sy - 0.4, -0.2, sx + 5.2, sy + 0.4, 24.0)              # the crook's staff
box(bm, sx + 5.2, sy - 0.4, 22.0, sx + 9.0, sy + 0.4, 23.0)              # its hook / blade
box(bm, sx + 8.2, sy - 0.4, 18.0, sx + 9.0, sy + 0.4, 23.0)
obj("shepherd", bm, M_SH)
bm = bmesh.new()
box(bm, sx - 1.2, sy - 2.7, 15.6, sx - 0.4, sy - 2.6, 16.2)
box(bm, sx + 0.4, sy - 2.7, 15.6, sx + 1.2, sy - 2.6, 16.2)
obj("sh_eyes", bm, glow("sheyes", EMBER, 50))
point("sh_glow", (sx, sy - 5, 15), EMBER, 3000, 1)
bm = bmesh.new()
for k in range(120):                                                     # ash streaming off it
    q = Vector((sx + rs.uniform(-5, 5), sy + rs.uniform(-3, 3) + 2, rs.uniform(2, 18)))
    s_ = rs.uniform(0.15, 0.45)
    box(bm, q.x - s_, q.y - s_, q.z - s_, q.x + s_, q.y + s_, q.z + s_)
obj("sh_ash", bm, pix("shash", (0.25, 0.24, 0.23), (0.38, 0.37, 0.36)))
M_FIG = [pixb("fig%d" % i, c, tuple(min(1, x * 1.3) for x in c)) for i, c in
         enumerate(((0.22, 0.04, 0.03), (0.06, 0.07, 0.1), (0.16, 0.13, 0.07), (0.04, 0.09, 0.05)))]
M_SKIN = pixb("skin", (0.55, 0.4, 0.3), (0.62, 0.46, 0.35))
bm_s = bmesh.new()
for i, (x, y) in enumerate(((-2.5, -3.0), (1.0, -2.0), (3.5, -3.6), (-0.6, -5.0))):
    bm = bmesh.new()
    box(bm, x - 0.3, y - 0.15, -1, x + 0.3, y + 0.15, 0.5)
    box(bm, x - 0.45, y - 0.2, -0.25, x + 0.45, y + 0.2, 0.5)
    obj("fig%d" % i, bm, M_FIG[i])
    box(bm_s, x - 0.25, y - 0.25, 0.5, x + 0.25, y + 0.25, 1.0)
obj("heads", bm_s, M_SKIN)

# ash haze over it all
m, nt, out = new_mat("haze")
vol = N(nt, "ShaderNodeVolumePrincipled", Density=0.0018, Anisotropy=0.3)
vol.inputs["Color"].default_value = (0.75, 0.6, 0.55, 1)
L(nt, vol.outputs[0], out.inputs["Volume"])
vol_cube("haze", m, (0, 20, 25), (150, 150, 40))

CAMS = {"wide": ((-100, -150, 95), (0, 10, -6), 28), "inside": ((0.5, -24.0, 2.0), (0.0, 40.0, 10.0), 17)}
loc, aim, lens = CAMS[SHOT]
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 6000
cam.location = loc
cam.data.lens = lens
cam.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
bloom()
sc.render.image_settings.color_depth = "8"
sc.render.filepath = os.path.abspath(os.path.join(OUT, "fold_%s%s.png" % (SHOT, "_fast" if FAST else "")))
bpy.ops.render.render(write_still=True)
print("WROTE", sc.render.filepath)
