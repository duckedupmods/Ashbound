"""Gate as a crack in the world (Cycles): a tall jagged tear hanging in the air, its lips burning white-hot into the
rank colour, black depth inside, the air round it shattered like struck glass (glowing fracture lines, floating
shards of reality that bend the world behind them), torn chunks of the dungeon hanging round it.
The tear's shape is a signed distance field (tools/renders/gate/rift_sdf.png) so the game shader can use the same.
  blender -b -P tools/blender/gate_rift.py -- <rank> [shot] [fast]  ->  tools/renders/gate/rift_<rank>_<shot>.png"""
import os, math, random, struct, zlib
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "gate_vfx.py"), encoding="utf-8").read()
exec(_src.split("# ---------------------------------------------------------------- the plasma")[0])

rnd = random.Random(23 + RI)
H = 4.9      # half height of the tear
WMAX = 1.55  # its widest half width
DMAX = 2.0   # the SDF is stored as 0.5 + d / (2 DMAX), d in blocks, + outside
EX, EZ = 3.2, H + 2.2  # half extents of the SDF / glow plane


# ---------------------------------------------------------------- the tear's outline
def outline():
    zs, xs = [], []
    n = 22
    x = 0.0
    for i in range(n + 1):
        t = i / n
        zs.append(-H + 2 * H * t)
        x += rnd.uniform(-0.42, 0.42)
        if rnd.random() < 0.18:
            x += rnd.choice((-1, 1)) * 0.5  # a sharp kink, like glass breaking
        x = max(-0.75, min(0.75, x))
        xs.append(x)
    xs[0] = xs[-1] = (xs[0] + xs[-1]) * 0.25
    right, left = [], []
    for i in range(n + 1):
        t = abs(zs[i]) / H
        w = WMAX * max(0.0, 1 - t) ** 0.75 * (1 - 0.35 * t)
        right.append((xs[i] + w * rnd.uniform(0.6, 1.25), zs[i]))
        left.append((xs[i] - w * rnd.uniform(0.6, 1.25), zs[i]))
    right[0] = left[0] = (xs[0], -H)
    right[-1] = left[-1] = (xs[-1], H)
    # teeth: a jagged point between each pair of edge points, in or out
    def teeth(edge, sgn):
        out = [edge[0]]
        for a, b in zip(edge, edge[1:]):
            m = ((a[0] + b[0]) / 2 + sgn * rnd.uniform(-0.16, 0.22), (a[1] + b[1]) / 2 + rnd.uniform(-0.1, 0.1))
            out += [m, b]
        return out
    r = teeth(right, 1)
    l = teeth(left, -1)
    return r + l[::-1][1:-1]  # counter-clockwise: up the right lip, down the left


POLY = outline()


def sdf_image():
    W, Hh = 256, int(256 * EZ / EX)
    xs = np.linspace(-EX, EX, W)
    zs = np.linspace(-EZ, EZ, Hh)
    X, Z = np.meshgrid(xs, zs)
    P = np.array(POLY)
    A, B = P, np.roll(P, -1, axis=0)
    d = np.full(X.shape, 1e9)
    inside = np.zeros(X.shape, bool)
    for (ax, az), (bx, bz) in zip(A, B):
        ex, ez = bx - ax, bz - az
        t = np.clip(((X - ax) * ex + (Z - az) * ez) / (ex * ex + ez * ez + 1e-12), 0, 1)
        d = np.minimum(d, np.hypot(X - ax - t * ex, Z - az - t * ez))
        cross = ((az > Z) != (bz > Z)) & (X < ax + (Z - az) * ex / (bz - az + 1e-12))
        inside ^= cross
    sd = np.where(inside, -d, d)
    v = np.clip(0.5 + sd / (2 * DMAX), 0, 1)
    print("SDF", v.shape, float(v.min()), float(v.max()), "inside", float(inside.mean()))
    # written by hand as an 8-bit grey PNG (Blender's own save of a generated float image came out blank),
    # row 0 at the top as PNGs go, so the bottom of the tear is the last row
    path = os.path.abspath(os.path.join(OUT, "rift_sdf.png"))
    os.makedirs(OUT, exist_ok=True)
    rows = (np.round(v[::-1] * 255)).astype(np.uint8)
    raw = b"".join(b"\x00" + r.tobytes() for r in rows)
    def chunk(t, data):
        c = struct.pack(">I", len(data)) + t + data
        return c + struct.pack(">I", zlib.crc32(t + data) & 0xFFFFFFFF)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, Hh, 8, 0, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    img = bpy.data.images.load(path, check_existing=False)
    img.colorspace_settings.name = "Non-Color"
    return img


SDF = sdf_image()
Y0 = -0.6  # the tear's plane (a little toward the camera from the old gate's middle)


def sdf_node(nt):
    """d in blocks (+ outside) for the current point, from the SDF image, in the tear's plane (object space)."""
    tc = N(nt, "ShaderNodeTexCoord")
    sp = N(nt, "ShaderNodeSeparateXYZ")
    L(nt, tc.outputs["Object"], sp.inputs[0])
    u = math_n(nt, "ADD", math_n(nt, "DIVIDE", sp.outputs["X"], vb=2 * EX), vb=0.5)
    v = math_n(nt, "ADD", math_n(nt, "DIVIDE", sp.outputs["Z"], vb=2 * EZ), vb=0.5)
    cb = N(nt, "ShaderNodeCombineXYZ")
    L(nt, u, cb.inputs["X"])
    L(nt, v, cb.inputs["Y"])
    im = N(nt, "ShaderNodeTexImage", _interpolation="Cubic", _extension="EXTEND")
    im.image = SDF
    L(nt, cb.outputs[0], im.inputs["Vector"])
    d = math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", im.outputs["Color"], vb=0.5), vb=2 * DMAX)
    return d, tc


# ---------------------------------------------------------------- the void: black depth with a faint far light
m_void, nt, out = nodes_mat("void")
d, tc = sdf_node(nt)
nz = N(nt, "ShaderNodeTexNoise", Scale=1.6, Detail=8.0, Distortion=2.0)
L(nt, tc.outputs["Object"], nz.inputs["Vector"])
far = math_n(nt, "MULTIPLY", smooth(nt, nz.outputs["Fac"], 0.5, 0.78), smooth(nt, d, -0.05, -0.9))
far_e = N(nt, "ShaderNodeEmission")
L(nt, scale_rgb(nt, HOT, math_n(nt, "MULTIPLY", far, vb=0.25 if DARK else 1.6)), far_e.inputs["Color"])
L(nt, far_e.outputs[0], out.inputs["Surface"])
bm = bmesh.new()
vs = [bm.verts.new((x, 0, z)) for x, z in POLY]
bm.faces.new(vs)
void = mesh_obj("void", bm, m_void)
void.location = (0, Y0 + 0.03, C)

# ---------------------------------------------------------------- the burning lips: emission from the SDF
m_lip, nt, out = nodes_mat("lip")
d, tc = sdf_node(nt)
n1 = N(nt, "ShaderNodeTexNoise", Scale=2.2, Detail=10.0, Roughness=0.65)
L(nt, tc.outputs["Object"], n1.inputs["Vector"])
n2 = N(nt, "ShaderNodeTexNoise", Scale=9.0, Detail=6.0)
L(nt, tc.outputs["Object"], n2.inputs["Vector"])
jit = math_n(nt, "ADD", math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", n1.outputs["Fac"], vb=0.5), vb=0.5),
             math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", n2.outputs["Fac"], vb=0.5), vb=0.18))
dj = math_n(nt, "ADD", d, jit)
out_d = math_n(nt, "MAXIMUM", dj, vb=0.0)
in_d = math_n(nt, "MAXIMUM", math_n(nt, "MULTIPLY", dj, vb=-1.0), vb=0.0)
# white-hot right at the lip, a tight band of rank colour, a wide soft halo, a little burn just inside
core = math_n(nt, "POWER", math_n(nt, "SUBTRACT", None, smooth(nt, math_n(nt, "ABSOLUTE", dj), 0.0, 0.05), va=1.0), vb=2.0)
outside = smooth(nt, dj, -0.04, 0.06)
band = math_n(nt, "EXPONENT", math_n(nt, "ADD", math_n(nt, "MULTIPLY", out_d, vb=-8.0), math_n(nt, "MULTIPLY", in_d, vb=-30.0)))
halo = math_n(nt, "MULTIPLY", math_n(nt, "EXPONENT", math_n(nt, "MULTIPLY", out_d, vb=-2.6)), outside)
burn = math_n(nt, "MULTIPLY", math_n(nt, "EXPONENT", math_n(nt, "MULTIPLY", in_d, vb=-22.0)), math_n(nt, "SUBTRACT", None, outside, va=1.0))
# flames: tongues licking off the lip where the noise runs high
tongue = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", smooth(nt, n1.outputs["Fac"], 0.55, 0.75), math_n(nt, "EXPONENT", math_n(nt, "MULTIPLY", out_d, vb=-3.0))), outside)
col_k = math_n(nt, "ADD", math_n(nt, "ADD", math_n(nt, "MULTIPLY", band, vb=26.0), math_n(nt, "MULTIPLY", halo, vb=0.9)),
               math_n(nt, "ADD", math_n(nt, "MULTIPLY", burn, vb=6.0), math_n(nt, "MULTIPLY", tongue, vb=14.0)))
WHITE = tuple(min(1.0, c * 0.25 + 0.78) for c in HOT)
# everything dies out well before the SDF's edge (it clamps at DMAX), so the plane itself never shows
edge_fade = smooth(nt, d, 1.75, 0.9)
col_k = math_n(nt, "MULTIPLY", col_k, edge_fade)
emi = add_v(nt, scale_rgb(nt, HOT, col_k), scale_rgb(nt, WHITE, math_n(nt, "MULTIPLY", core, vb=70.0)))
e = N(nt, "ShaderNodeEmission")
L(nt, emi, e.inputs["Color"])
tr = N(nt, "ShaderNodeBsdfTransparent")
add = N(nt, "ShaderNodeAddShader")
L(nt, tr.outputs[0], add.inputs[0])
L(nt, e.outputs[0], add.inputs[1])
L(nt, add.outputs[0], out.inputs["Surface"])
if os.environ.get("RIFT_DEBUG"):
    dbg = N(nt, "ShaderNodeEmission")
    L(nt, smooth(nt, d, -1.0, 1.0), dbg.inputs["Strength"])
    L(nt, dbg.outputs[0], out.inputs["Surface"])
bm = bmesh.new()
q = [bm.verts.new(v) for v in ((-EX, 0, -EZ), (EX, 0, -EZ), (EX, 0, EZ), (-EX, 0, EZ))]
bm.faces.new(q)
lip = mesh_obj("lip", bm, m_lip)
lip.location = (0, Y0, C)
# the light it throws: warm along its length, hottest at its middle
for i, z in enumerate((-0.6, 0.0, 0.6)):
    point("rift_l%d" % i, (0, Y0 - 0.8, C + z * H), HOT, 9000 if i == 1 else 5000, 0.6)

# ---------------------------------------------------------------- the air shattered round it
bm_c = bmesh.new()


def crack_line(p, ang, length, wid, depth=0):
    steps = max(3, int(length / 0.25))
    for _ in range(steps):
        ang += rnd.uniform(-0.5, 0.5)
        q = p + Vector((math.cos(ang), 0, math.sin(ang))) * (length / steps)
        side = Vector((-math.sin(ang), 0, math.cos(ang))) * wid
        vv = [bm_c.verts.new(v) for v in (p - side, q - side * 0.85, q + side * 0.85, p + side)]
        bm_c.faces.new(vv)
        if depth < 2 and rnd.random() < 0.3:
            crack_line(q, ang + rnd.choice((-1, 1)) * rnd.uniform(0.5, 1.1), length * 0.45, wid * 0.6, depth + 1)
        p = q
        wid *= 0.84


for i in range(10):
    k = rnd.randrange(len(POLY))
    a, b = Vector((POLY[k][0], 0, POLY[k][1])), Vector((POLY[(k + 1) % len(POLY)][0], 0, POLY[(k + 1) % len(POLY)][1]))
    p = a.lerp(b, rnd.random())
    tang = (b - a).normalized()
    nrm = Vector((tang.z, 0, -tang.x))  # outward for a counter-clockwise outline
    ang = math.atan2(nrm.z, nrm.x) + rnd.uniform(-0.5, 0.5)
    crack_line(p, ang, rnd.uniform(0.8, 2.8), 0.022)
CRK = flat_mat("crk", (0, 0, 0), 1.0, tuple(min(1, c * 0.45 + 0.55) for c in HOT), 38.0)
cracks = mesh_obj("cracks", bm_c, CRK)
cracks.location = (0, Y0 - 0.01, C)

# shards of reality knocked loose: thin glass that bends the world behind it, lit at its edges
GLASS, nt, out = nodes_mat("shard")
gb = N(nt, "ShaderNodeBsdfGlass")
gb.inputs["IOR"].default_value = 1.12
gb.inputs["Roughness"].default_value = 0.02
gb.inputs["Color"].default_value = tuple(0.85 + 0.15 * c for c in HOT) + (1,)
L(nt, gb.outputs[0], out.inputs["Surface"])
EDGE = flat_mat("shard_edge", (0, 0, 0), 1.0, tuple(min(1, c * 0.5 + 0.5) for c in HOT), 22.0)
for i in range(18):
    k = rnd.randrange(len(POLY))
    px, pz = POLY[k]
    out_dir = Vector((px, 0, pz * 0.25)).normalized() if abs(px) > 0.05 else Vector((rnd.choice((-1, 1)), 0, 0))
    centre = Vector((px, 0, pz)) + out_dir * rnd.uniform(0.25, 1.8) + Vector((0, rnd.uniform(-0.5, 0.3), 0))
    s = rnd.uniform(0.22, 0.75)
    bm_s = bmesh.new()
    pts = [Vector((math.cos(t) * s * rnd.uniform(0.5, 1.2), 0, math.sin(t) * s * rnd.uniform(0.5, 1.6)))
           for t in sorted(rnd.uniform(0, math.tau) for _ in range(3 + rnd.randint(0, 1)))]
    vv = [bm_s.verts.new(p) for p in pts]
    bm_s.faces.new(vv)
    bmesh.ops.solidify(bm_s, geom=bm_s.faces[:], thickness=0.03)
    ob = mesh_obj("shard%d" % i, bm_s, GLASS)
    ob.data.materials.append(EDGE)
    for f in ob.data.polygons:
        if abs(f.normal.y) < 0.5:
            f.material_index = 1
    ob.location = Vector((0, Y0, C)) + centre
    ob.rotation_euler = (rnd.uniform(-0.5, 0.5), rnd.uniform(-0.6, 0.6), rnd.uniform(-0.4, 0.4))

# ---------------------------------------------------------------- torn chunks of the dungeon hanging round it
WALL = flat_mat("wall", (0.16, 0.16, 0.15), 0.8)
MOSS = flat_mat("moss", (0.07, 0.12, 0.05), 0.9)
WOOD = flat_mat("wood", (0.12, 0.07, 0.04), 0.8)
for i in range(22):
    a = rnd.uniform(0, math.tau)
    rr = rnd.uniform(2.2, 6.5)
    bm_d = bmesh.new()
    nb = rnd.choice((1, 1, 1, 2, 2, 3))
    for k in range(nb):
        box(bm_d, k % 2, (k // 2) % 2, 0, k % 2 + 1, (k // 2) % 2 + 1, 1)
    ob = mesh_obj("chunk%d" % i, bm_d, rnd.choice((WALL, WALL, MOSS, WOOD)))
    ob.location = (math.cos(a) * rr, math.sin(a) * rr * 0.6 + Y0, C + rnd.uniform(-H * 0.8, H * 1.1))
    ob.rotation_euler = (rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, math.tau))
    sz = rnd.uniform(0.35, 0.8)
    ob.scale = (sz, sz, sz)

# sparks and embers drifting off the lips
bm_e = bmesh.new()
for i in range(160):
    k = rnd.randrange(len(POLY))
    p = Vector((POLY[k][0] * rnd.uniform(1.0, 2.6), rnd.uniform(-1.5, 0.6) + Y0, C + POLY[k][1] + rnd.uniform(0, 2.0)))
    bmesh.ops.create_icosphere(bm_e, subdivisions=1, radius=rnd.uniform(0.012, 0.04), matrix=Matrix.Translation(p))
mesh_obj("embers", bm_e, flat_mat("ember", (0, 0, 0), 1.0, tuple(min(1, c * 0.7 + 0.3) for c in HOT), 16.0))

# ---------------------------------------------------------------- shots, bloom, render
SHOTS = {
    "hero": ((-7.5, -19.0, 2.4), (0.3, 0, 5.6), 28),
    "close": ((-2.5, -8.5, 3.6), (0, 0, 5.4), 24),
    "wide": ((-18, -36, 8), (0, 0, 8), 30),
}
loc, aim, lens = SHOTS.get(SHOT, SHOTS["hero"])
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 400
cam.location = loc
cam.data.lens = lens
cam.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
try:
    ng = bpy.data.node_groups.new("comp", "CompositorNodeTree")
    sc.compositing_node_group = ng
    rl = ng.nodes.new("CompositorNodeRLayers")
    gl = ng.nodes.new("CompositorNodeGlare")
    gl.inputs["Type"].default_value = "Bloom"
    gl.inputs["Quality"].default_value = "High"
    gl.inputs["Threshold"].default_value = 2.0
    gl.inputs["Strength"].default_value = 0.22
    gl.inputs["Size"].default_value = 0.45
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    go = ng.nodes.new("NodeGroupOutput")
    ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
    ng.links.new(gl.outputs["Image"], go.inputs[0])
    sc.render.use_compositing = True
except Exception as ex:
    print("COMP FAIL", ex)
sc.render.image_settings.color_depth = "8"
sc.render.filepath = os.path.abspath(os.path.join(OUT, "rift_%s_%s.png" % (RANK, SHOT)))
bpy.ops.render.render(write_still=True)
print("WROTE", sc.render.filepath)
