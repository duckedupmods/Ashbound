"""The Ashen Ring (concept, Cycles): the arena's own dimension. A great ruined colosseum of clean pale stone floats on a
broken root of rock over a sea of cloud, under a cold night sky full of stars. Its stands are full of the dead: ghostly
pale-blue spectators on every tier. Spirit braziers burn pale blue round the sand; a rune circle (Veyra's sigil) glows in
the middle where the party arrives; monsters come in through gate-rifts torn in the four arches of the arena wall, each
rift a black hole rimmed in its gate's colour.
  blender -b -P tools/blender/arena_ring.py -- [wide|inside] [fast]  ->  tools/renders/arena/arena_<shot>.png"""
import os, sys, math, random
import bpy, bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
# the shared helpers (materials, boxes, lights, bloom) from the meteor concept; its scene setup comes with them
exec(open(os.path.join(HERE, "meteor_fall.py"), encoding="utf-8").read().split("GATE = (0.62")[0])
_src = open(os.path.join(HERE, "meteor_fall.py"), encoding="utf-8").read()
exec("def bloom():" + _src.split("def bloom():")[1].split("\n# ================================================================ the crater")[0])

SHOT = next((a for a in ARGS if a in ("wide", "inside")), "inside")
OUT = os.path.join(HERE, "..", "renders", "arena")
os.makedirs(OUT, exist_ok=True)
rs = random.Random(12)
sc.view_settings.exposure = -0.6 if SHOT == "inside" else 0.1

SPIRIT = (0.2, 0.68, 1.0)
SPIRIT_HOT = (0.85, 0.97, 1.0)


def pixb(name, c0, c1, bricks=None, rough=0.85):
    """block texture with brick seams (every half block high, a block long, courses offset)"""
    m, nt, out = new_mat(name)
    geo = N(nt, "ShaderNodeNewGeometry")
    nudge = N(nt, "ShaderNodeVectorMath", _operation="SCALE")
    nudge.inputs["Scale"].default_value = -0.01
    L(nt, geo.outputs["Normal"], nudge.inputs[0])
    pos = N(nt, "ShaderNodeVectorMath", _operation="ADD")
    L(nt, geo.outputs["Position"], pos.inputs[0])
    L(nt, nudge.outputs[0], pos.inputs[1])
    snap = N(nt, "ShaderNodeVectorMath", _operation="SNAP")
    snap.inputs[1].default_value = (1 / 16, 1 / 16, 1 / 16)
    L(nt, pos.outputs[0], snap.inputs[0])
    wn = N(nt, "ShaderNodeTexWhiteNoise", _noise_dimensions="3D")
    L(nt, snap.outputs[0], wn.inputs["Vector"])
    col = mix(nt, wn.outputs["Value"], c0, c1)
    if bricks:
        sp = N(nt, "ShaderNodeSeparateXYZ")
        L(nt, snap.outputs[0], sp.inputs[0])
        course = mth(nt, "FLOOR", mth(nt, "MULTIPLY", sp.outputs["Z"], vb=2))
        off = mth(nt, "MULTIPLY", mth(nt, "MODULO", course, vb=2), vb=0.5)
        fz = mth(nt, "FRACT", mth(nt, "MULTIPLY", sp.outputs["Z"], vb=2))
        fx = mth(nt, "FRACT", mth(nt, "ADD", mth(nt, "ADD", sp.outputs["X"], sp.outputs["Y"]), off))
        seam = mth(nt, "MAXIMUM", mth(nt, "LESS_THAN", fz, vb=0.07), mth(nt, "LESS_THAN", fx, vb=0.05))
        col = mix(nt, seam, col, bricks)
    b = N(nt, "ShaderNodeBsdfPrincipled", Roughness=rough)
    L(nt, col, b.inputs["Base Color"])
    L(nt, b.outputs[0], out.inputs["Surface"])
    return m


# ---------------------------------------------------------------- the sky: cold night, stars, a pale moon; a sea of cloud below
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
up = mth(wt, "MAXIMUM", sep.outputs["Z"], vb=0.0)
horizon = mth(wt, "POWER", mth(wt, "SUBTRACT", va=1.0, b=mth(wt, "MINIMUM", mth(wt, "MULTIPLY", up, vb=3.0), vb=1.0)), vb=2.0)
base = mix(wt, horizon, (0.004, 0.006, 0.018), (0.03, 0.05, 0.11))
st = N(wt, "ShaderNodeTexVoronoi", Scale=260.0)
L(wt, tc.outputs["Generated"], st.inputs["Vector"])
star = mth(wt, "MULTIPLY", mth(wt, "LESS_THAN", st.outputs["Distance"], vb=0.045), mth(wt, "GREATER_THAN", sep.outputs["Z"], vb=0.02))
neb = N(wt, "ShaderNodeTexNoise", Scale=2.2, Detail=6.0)
L(wt, tc.outputs["Generated"], neb.inputs["Vector"])
sky = mix(wt, mth(wt, "MULTIPLY", mth(wt, "POWER", neb.outputs["Fac"], vb=4.0), vb=1.6), base, (0.06, 0.05, 0.16))
sky = mix(wt, star, sky, (0.9, 0.95, 1.0))
bg = N(wt, "ShaderNodeBackground", Strength=1.0)
L(wt, sky, bg.inputs["Color"])
L(wt, bg.outputs[0], wo.inputs["Surface"])
MOON_DIR = Vector((-0.5, 0.75, 0.42)).normalized()
bm = bmesh.new()
bmesh.ops.create_circle(bm, cap_ends=True, segments=64, radius=60)
mo = obj("moon", bm, glow("moon", (0.8, 0.88, 1.0), 6.0))
# the disc where each camera sees it, upper left; its light from the camera's side so the stone faces it
MOON_AT = Vector((-0.55, 0.75, 0.45)).normalized() if SHOT == "inside" else Vector((-0.75, 0.55, 0.32)).normalized()
mo.location = MOON_AT * 1800
mo.rotation_euler = (-MOON_AT).to_track_quat("Z", "Y").to_euler()
MOON_DIR = Vector((-0.45, -0.7, 0.55)).normalized()
sun = bpy.data.objects.new("moonlight", bpy.data.lights.new("moonlight", "SUN"))
sun.data.energy = 0.7
sun.data.color = (0.62, 0.72, 1.0)
sun.data.angle = math.radians(2)
sun.rotation_euler = (-MOON_DIR).to_track_quat("-Z", "Y").to_euler()
sc.collection.objects.link(sun)

# the cloud sea far under it: a wide sheet, lumpy, moonlit
m, nt, out = new_mat("clouds")
geo = N(nt, "ShaderNodeNewGeometry")
cn = N(nt, "ShaderNodeTexNoise", Scale=0.004, Detail=8.0, Roughness=0.6)
L(nt, geo.outputs["Position"], cn.inputs["Vector"])
cc = mix(nt, mth(nt, "POWER", cn.outputs["Fac"], vb=2.0), (0.04, 0.05, 0.09), (0.35, 0.4, 0.55))
b = N(nt, "ShaderNodeBsdfDiffuse")
L(nt, cc, b.inputs["Color"])
L(nt, b.outputs[0], out.inputs["Surface"])
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=200, y_segments=200, size=3000)
for v in bm.verts:
    v.co.z = 14 * math.sin(v.co.x * 0.008) * math.cos(v.co.y * 0.006) + 8 * math.sin((v.co.x + v.co.y) * 0.02)
cl = obj("cloud_sea", bm, m)
cl.location = (0, 0, -95)

# ---------------------------------------------------------------- the colosseum, block by block
R_SAND, R_WALL, R_TIERS, R_OUT = 30, 32, 56, 60
WALL_H, TOP = 6, 30
vox = {}


def put(x, y, z, k):
    vox[(x, y, z)] = k


def ruined(a):
    """the outer wall broken down on part of its round: how much is gone (0..1) at this angle"""
    return max(0.0, math.sin(a + 3.5)) ** 3


for x in range(-R_OUT - 2, R_OUT + 3):
    for y in range(-R_OUT - 2, R_OUT + 3):
        r = math.hypot(x + 0.5, y + 0.5)
        a = math.atan2(y + 0.5, x + 0.5)
        if r > R_OUT + 0.5:
            # pilasters between the arches, standing out from the face
            seg = (a * (R_OUT - 2)) % 6.0
            if r < R_OUT + 1.6 and (seg < 0.7 or seg > 5.3):
                hh = int(TOP - ruined(a) * (TOP - 12))
                for z in range(0, hh - 1):
                    put(x, y, z, "trim" if z in (9, 18, 27) else "stone")
            continue
        # the rock it stands on, hanging under it
        bot = -int(46 * (1 - (r / (R_OUT + 1)) ** 1.6) + 6 * math.sin(a * 5) * (1 - r / R_OUT) + rs.uniform(0, 3))
        for z in range(bot, -1):
            put(x, y, z, "rock")
        if r < R_SAND:
            put(x, y, -1, "sand")
            continue
        put(x, y, -1, "stone")
        # the four gates in the arena wall: N E S W, each an arch 7 wide, 8 tall, a tunnel back under the stands
        gate = any(abs(((a - g) + math.pi) % (2 * math.pi) - math.pi) * r < 3.6 for g in (0, math.pi / 2, math.pi, -math.pi / 2))
        if r < R_WALL:
            for z in range(0, WALL_H + 1):
                if gate and z < 8:
                    continue
                put(x, y, z, "trim" if z == WALL_H else "stone")
            continue
        if r < R_TIERS:
            # the stands: a step every 2 blocks out, a seat of trim on each
            h = WALL_H + int((r - R_WALL) // 2) * 1 + int((r - R_WALL) // 2) // 2
            for z in range(0, h + 1):
                if gate and z < 8 and r < R_WALL + 10:
                    continue
                put(x, y, z, "seat" if z == h else "stone")
            continue
        # the outer wall: two storeys of arches, ruined on one side
        hh = int(TOP - ruined(a) * (TOP - 12) - rs.uniform(0, 3) * ruined(a))
        seg = (a * (R_OUT - 2)) % 6.0
        for z in range(0, hh + 1):
            arch = False
            for zb, tall in ((0, 5), (10, 4), (19, 4)):
                # an arcade arch: straight sides, a round head 1.9 across
                if zb <= z < zb + tall and abs(seg - 3) < 1.9:
                    arch = True
                elif z >= zb + tall and (seg - 3) ** 2 + (z - zb - tall) ** 2 < 1.9 ** 2:
                    arch = True
            if arch and z > 0:
                continue
            put(x, y, z, "trim" if z in (9, 18, 27) or z == hh else "stone")


def mesh_vox(vox, mats):
    bms = {k: bmesh.new() for k in mats}
    faces = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    for (x, y, z), k in vox.items():
        b = bms[k]
        for dx, dy, dz in faces:
            if (x + dx, y + dy, z + dz) in vox:
                continue
            if dx:
                xx = x + (1 if dx > 0 else 0)
                q = [(xx, y, z), (xx, y + 1, z), (xx, y + 1, z + 1), (xx, y, z + 1)]
            elif dy:
                yy = y + (1 if dy > 0 else 0)
                q = [(x, yy, z), (x + 1, yy, z), (x + 1, yy, z + 1), (x, yy, z + 1)]
            else:
                zz = z + (1 if dz > 0 else 0)
                q = [(x, y, zz), (x + 1, y, zz), (x + 1, y + 1, zz), (x, y + 1, zz)]
            b.faces.new([b.verts.new(p) for p in q])
    for k, b in bms.items():
        obj("vox_" + k, b, mats[k])


MATS = {
    "sand": pixb("sand", (0.30, 0.29, 0.28), (0.40, 0.38, 0.36)),
    "stone": pixb("stone", (0.36, 0.36, 0.38), (0.46, 0.46, 0.48), bricks=(0.18, 0.18, 0.2)),
    "trim": pixb("trim", (0.16, 0.17, 0.2), (0.24, 0.25, 0.28), bricks=(0.08, 0.08, 0.1)),
    "seat": pixb("seat", (0.5, 0.5, 0.52), (0.62, 0.62, 0.64)),
    "rock": pixb("rock", (0.08, 0.075, 0.08), (0.17, 0.16, 0.17)),
}
mesh_vox(vox, MATS)
print("voxels", len(vox))

# ---------------------------------------------------------------- the crowd: townsfolk from all over, packed on the stands
CLOTH = [(0.45, 0.08, 0.06), (0.1, 0.18, 0.4), (0.12, 0.3, 0.12), (0.5, 0.35, 0.1), (0.3, 0.12, 0.35), (0.55, 0.5, 0.42),
         (0.08, 0.08, 0.1), (0.15, 0.35, 0.4), (0.6, 0.2, 0.1), (0.35, 0.25, 0.18)]
SKINS = [(0.62, 0.45, 0.34), (0.45, 0.3, 0.2), (0.3, 0.2, 0.14), (0.7, 0.55, 0.45)]
HAIR = [(0.08, 0.05, 0.03), (0.3, 0.18, 0.08), (0.55, 0.42, 0.2), (0.6, 0.6, 0.6), (0.4, 0.1, 0.05)]
M_CLOTH = [pixb("cloth%d" % i, c, tuple(min(1, x * 1.25) for x in c)) for i, c in enumerate(CLOTH)]
M_SKINS = [pixb("skin%d" % i, c, tuple(min(1, x * 1.08) for x in c)) for i, c in enumerate(SKINS)]
M_HAIR = [pixb("hair%d" % i, c, tuple(min(1, x * 1.2) for x in c)) for i, c in enumerate(HAIR)]
bm_c = [bmesh.new() for _ in CLOTH]
bm_k = [bmesh.new() for _ in SKINS]
bm_h = [bmesh.new() for _ in HAIR]
n_g = 0
for (x, y, z), k in vox.items():
    if k != "seat" or (x, y, z + 1) in vox or rs.random() > 0.55:
        continue
    r = math.hypot(x + 0.5, y + 0.5)
    a = math.atan2(y + 0.5, x + 0.5)
    if any(abs(((a - g) + math.pi) % (2 * math.pi) - math.pi) * r < 4.5 for g in (0, math.pi / 2, math.pi, -math.pi / 2)) and r < R_WALL + 10:
        continue
    cx, cy, cz = x + 0.5 + rs.uniform(-0.15, 0.15), y + 0.5 + rs.uniform(-0.15, 0.15), z + 1
    standing = rs.random() < 0.35
    tall = (1.3 if standing else 0.95) * rs.uniform(0.75, 1.05)       # kids and grown-ups
    ci, si, hi = rs.randrange(len(CLOTH)), rs.randrange(len(SKINS)), rs.randrange(len(HAIR))
    box(bm_c[ci], cx - 0.3, cy - 0.18, cz, cx + 0.3, cy + 0.18, cz + tall)
    hs = 0.27 * (0.9 + 0.2 * (tall / 1.3))
    box(bm_k[si], cx - hs, cy - hs, cz + tall, cx + hs, cy + hs, cz + tall + hs * 2)
    box(bm_h[hi], cx - hs - 0.02, cy - hs - 0.02, cz + tall + hs * 1.6, cx + hs + 0.02, cy + hs + 0.02, cz + tall + hs * 2 + 0.06)
    if rs.random() < 0.3:
        # an arm up, cheering
        sd = rs.choice((-1, 1))
        box(bm_c[ci], cx + sd * 0.3, cy - 0.08, cz + tall - 0.3, cx + sd * 0.48, cy + 0.08, cz + tall + 0.6)
    n_g += 1
for lst, mats, nm in ((bm_c, M_CLOTH, "crowd_cloth"), (bm_k, M_SKINS, "crowd_skin"), (bm_h, M_HAIR, "crowd_hair")):
    for i, b in enumerate(lst):
        obj("%s%d" % (nm, i), b, mats[i])
print("crowd", n_g)
# torches along the stands so the crowd is seen
for i in range(24):
    a = i / 24 * math.tau
    for rr, zz in ((R_WALL + 6, 10), (R_TIERS - 3, 18)):
        point("stand%d_%d" % (i, rr), (math.cos(a) * rr, math.sin(a) * rr, zz), (1.0, 0.62, 0.32), 900, 1)

# ---------------------------------------------------------------- spirit braziers round the sand, and on the outer wall
M_IRON = pixb("iron", (0.05, 0.05, 0.06), (0.1, 0.1, 0.12))
M_SFIRE = glow("spirit_fire", SPIRIT, 9.0)
bm_i, bm_f = bmesh.new(), bmesh.new()
for i in range(16):
    a = i / 16 * math.tau + math.tau / 32
    x, y = math.cos(a) * (R_SAND - 1.5), math.sin(a) * (R_SAND - 1.5)
    box(bm_i, x - 0.3, y - 0.3, 0, x + 0.3, y + 0.3, 1.8)
    box(bm_i, x - 0.6, y - 0.6, 1.8, x + 0.6, y + 0.6, 2.2)
    for k in range(4):
        h = rs.uniform(0.3, 1.0)
        box(bm_f, x - 0.35 + rs.uniform(-0.15, 0.15), y - 0.35 + rs.uniform(-0.15, 0.15), 2.2, x + 0.35, y + 0.35, 2.2 + h)
    point("braz%d" % i, (x, y, 3.0), SPIRIT, 900, 0.6)
for i in range(10):
    a = i / 10 * math.tau
    if ruined(a) > 0.3:
        continue
    x, y = math.cos(a) * (R_OUT - 1), math.sin(a) * (R_OUT - 1)
    hh = int(TOP - ruined(a) * (TOP - 12))
    box(bm_i, x - 0.6, y - 0.6, hh + 1, x + 0.6, y + 0.6, hh + 1.5)
    box(bm_f, x - 0.4, y - 0.4, hh + 1.5, x + 0.4, y + 0.4, hh + 2.6)
    point("wallfire%d" % i, (x, y, hh + 3), SPIRIT, 2500, 1)
obj("brazier_iron", bm_i, M_IRON)
obj("spirit_flames", bm_f, M_SFIRE)

# ---------------------------------------------------------------- the rune circle in the middle (where Veyra sends you)
M_RUNE = glow("rune", SPIRIT, 6.0)
bm_r = bmesh.new()
for rr, wdt in ((7.0, 0.35), (5.6, 0.2), (2.2, 0.25)):
    n = 96
    for i in range(n):
        a0, a1 = i / n * math.tau, (i + 1) / n * math.tau
        p = [(math.cos(a0) * rr, math.sin(a0) * rr), (math.cos(a1) * rr, math.sin(a1) * rr),
             (math.cos(a1) * (rr - wdt), math.sin(a1) * (rr - wdt)), (math.cos(a0) * (rr - wdt), math.sin(a0) * (rr - wdt))]
        bm_r.faces.new([bm_r.verts.new((x, y, 0.02)) for x, y in p])
for i in range(12):
    # rune marks between the rings
    a = i / 12 * math.tau
    c = Vector((math.cos(a) * 6.3, math.sin(a) * 6.3, 0.02))
    t = Vector((-math.sin(a), math.cos(a), 0)) * 0.25
    rr = Vector((math.cos(a), math.sin(a), 0)) * 0.45
    bm_r.faces.new([bm_r.verts.new(c + v) for v in (-t - rr, t - rr, t + rr, -t + rr)])
for i in range(6):
    a = i / 6 * math.tau
    p0 = Vector((math.cos(a) * 2.2, math.sin(a) * 2.2, 0.02))
    p1 = Vector((math.cos(a + math.tau / 3) * 5.6, math.sin(a + math.tau / 3) * 5.6, 0.02))
    side = (p1 - p0).cross(Vector((0, 0, 1))).normalized() * 0.1
    bm_r.faces.new([bm_r.verts.new(v) for v in (p0 - side, p1 - side, p1 + side, p0 + side)])
obj("runes", bm_r, M_RUNE)
point("rune_glow", (0, 0, 1.5), SPIRIT, 700, 4)

# ---------------------------------------------------------------- the rifts in the four gates: black holes rimmed in a gate's colour
RIFTS = [(math.pi / 2, (0.62, 0.22, 1.0)), (0.0, (1.0, 0.18, 0.18)), (-math.pi / 2, (0.25, 0.55, 1.0)), (math.pi, (0.27, 0.9, 0.47))]


def rift_mat(name, col):
    m, nt, out = new_mat(name)
    tc = N(nt, "ShaderNodeTexCoord")
    sp = N(nt, "ShaderNodeSeparateXYZ")
    L(nt, tc.outputs["Generated"], sp.inputs[0])
    dx = mth(nt, "MULTIPLY", mth(nt, "SUBTRACT", sp.outputs["X"], vb=0.5), vb=2.0)
    dy = mth(nt, "MULTIPLY", mth(nt, "SUBTRACT", sp.outputs["Y"], vb=0.5), vb=2.0)
    nz = N(nt, "ShaderNodeTexNoise", Scale=6.0, Detail=6.0, Distortion=1.2)
    L(nt, tc.outputs["Generated"], nz.inputs["Vector"])
    r = mth(nt, "ADD", mth(nt, "SQRT", mth(nt, "ADD", mth(nt, "MULTIPLY", dx, dx), mth(nt, "MULTIPLY", dy, dy))), mth(nt, "MULTIPLY", nz.outputs["Fac"], vb=0.25))
    rim = mth(nt, "MULTIPLY", mth(nt, "GREATER_THAN", r, vb=0.72), mth(nt, "LESS_THAN", r, vb=0.98))
    hot = mth(nt, "MULTIPLY", mth(nt, "GREATER_THAN", r, vb=0.72), mth(nt, "LESS_THAN", r, vb=0.8))
    inside = mth(nt, "LESS_THAN", r, vb=0.98)
    e = N(nt, "ShaderNodeEmission")
    L(nt, mix(nt, hot, col, tuple(min(1, c * 0.4 + 0.65) for c in col)), e.inputs["Color"])
    L(nt, mth(nt, "MULTIPLY", rim, vb=18.0), e.inputs["Strength"])
    blk = N(nt, "ShaderNodeEmission", Strength=0.0)
    blk.inputs["Color"].default_value = (0, 0, 0, 1)
    mx1 = N(nt, "ShaderNodeMixShader")
    L(nt, rim, mx1.inputs[0])
    L(nt, blk.outputs[0], mx1.inputs[1])
    L(nt, e.outputs[0], mx1.inputs[2])
    tr = N(nt, "ShaderNodeBsdfTransparent")
    mx2 = N(nt, "ShaderNodeMixShader")
    L(nt, inside, mx2.inputs[0])
    L(nt, tr.outputs[0], mx2.inputs[1])
    L(nt, mx1.outputs[0], mx2.inputs[2])
    L(nt, mx2.outputs[0], out.inputs["Surface"])
    return m


for i, (a, col) in enumerate(RIFTS):
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * 4.4, 0, (v.co.y + 1) * 4.6 - 0.6))
    o = obj("rift%d" % i, bm, rift_mat("rift%d" % i, col))
    o.location = (math.cos(a) * (R_SAND + 1.2), math.sin(a) * (R_SAND + 1.2), -0.1)
    o.rotation_euler = (0, 0, a + math.pi / 2)
    point("rift_light%d" % i, (math.cos(a) * (R_SAND - 1), math.sin(a) * (R_SAND - 1), 3.5), col, 5000, 2)

# ---------------------------------------------------------------- the party on the sand, a brute coming through the north rift
M_FIG = [pixb("fig%d" % i, c, tuple(min(1, x * 1.3) for x in c)) for i, c in enumerate(((0.22, 0.04, 0.03), (0.06, 0.07, 0.1), (0.16, 0.13, 0.07), (0.04, 0.09, 0.05)))]
M_SKIN = pixb("skin", (0.55, 0.4, 0.3), (0.62, 0.46, 0.35))
M_STEEL = pixb("steel", (0.45, 0.46, 0.5), (0.6, 0.62, 0.66), rough=0.35)
bm_s, bm_st = bmesh.new(), bmesh.new()
for i, (x, y) in enumerate(((-2.5, -4.0), (1.0, -3.0), (3.8, -5.0), (-0.5, -6.5))):
    bm = bmesh.new()
    box(bm, x - 0.3, y - 0.15, 0, x + 0.3, y + 0.15, 1.5)
    box(bm, x - 0.45, y - 0.2, 0.75, x + 0.45, y + 0.2, 1.5)
    obj("fig%d" % i, bm, M_FIG[i])
    box(bm_s, x - 0.25, y - 0.25, 1.5, x + 0.25, y + 0.25, 2.0)
    box(bm_st, x + 0.45, y - 0.05, 0.9, x + 0.55, y + 0.05, 2.4)       # a blade held up
obj("heads", bm_s, M_SKIN)
obj("blades", bm_st, M_STEEL)
M_BRUTE = pixb("brute", (0.04, 0.035, 0.04), (0.09, 0.08, 0.09))
bm = bmesh.new()
bx, by = 0.0, R_SAND - 1.5
box(bm, bx - 1.2, by - 0.7, 0, bx - 0.3, by + 0.7, 2.2)
box(bm, bx + 0.3, by - 0.7, 0, bx + 1.2, by + 0.7, 2.2)
box(bm, bx - 1.8, by - 1.0, 2.2, bx + 1.8, by + 1.0, 5.0)
box(bm, bx - 2.6, by - 0.9, 3.8, bx + 2.6, by + 0.9, 5.4)
box(bm, bx - 0.7, by - 0.9, 5.0, bx + 0.7, by + 0.6, 6.1)
box(bm, bx - 3.0, by - 0.5, 0.8, bx - 2.2, by + 0.5, 4.0)
box(bm, bx + 2.2, by - 0.5, 0.8, bx + 3.0, by + 0.5, 4.0)
obj("brute", bm, M_BRUTE)
bm = bmesh.new()
box(bm, bx - 0.45, by - 0.95, 5.4, bx - 0.15, by - 0.85, 5.6)
box(bm, bx + 0.15, by - 0.95, 5.4, bx + 0.45, by - 0.85, 5.6)
obj("brute_eyes", bm, glow("eyes", (0.75, 0.3, 1.0), 30.0))

# ---------------------------------------------------------------- broken pieces of the world drifting round it
bm = bmesh.new()
for i in range(14):
    a = rs.uniform(0, math.tau)
    d = rs.uniform(95, 260)
    c = Vector((math.cos(a) * d, math.sin(a) * d, rs.uniform(-60, 30)))
    s = rs.uniform(4, 14)
    for k in range(int(s * 3)):
        p = c + Vector((rs.uniform(-s, s), rs.uniform(-s, s), -abs(rs.gauss(0, s * 0.7))))
        q = rs.uniform(1.5, 4)
        box(bm, p.x - q, p.y - q, p.z - q, p.x + q, p.y + q, p.z + q)
obj("islands", bm, MATS["rock"])

# a thin cold haze in the bowl
m, nt, out = new_mat("haze")
vol = N(nt, "ShaderNodeVolumePrincipled", Density=0.0025, Anisotropy=0.3)
vol.inputs["Color"].default_value = (0.6, 0.75, 1.0, 1)
L(nt, vol.outputs[0], out.inputs["Volume"])
vol_cube("haze", m, (0, 0, 20), (70, 70, 22))

# ---------------------------------------------------------------- camera
CAMS = {"wide": ((-70, -185, 14), (0, 0, 2), 32), "inside": ((-1.5, -13.0, 2.2), (0.0, 34.0, 9.0), 18)}
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
sc.render.filepath = os.path.abspath(os.path.join(OUT, "arena_%s%s.png" % (SHOT, "_fast" if FAST else "")))
bpy.ops.render.render(write_still=True)
print("WROTE", sc.render.filepath)
