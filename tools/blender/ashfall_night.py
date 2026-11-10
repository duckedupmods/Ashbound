"""Ashfall Night (concept, Cycles): a rare night when the far fire-mountain wakes and ash falls on the land. The sky
turns red under a low ash cloud, the moon a dim red coin through it, grey flakes drifting down thick with a few embers
still alight; ash lies on every top face. The town shuts its gate and lights braziers on the wall and down the street.
  blender -b -P tools/blender/ashfall_night.py -- [street|outside] [fast]  ->  tools/renders/ashfall/ashfall_<shot>.png"""
import os, sys, math, random
import bpy, bmesh
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SHOT = next((a for a in ARGS if a in ("street", "outside", "mountain")), "street")
FAST = "fast" in ARGS
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "renders", "ashfall")
os.makedirs(OUT, exist_ok=True)
rs = random.Random(3)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
try:
    cp = bpy.context.preferences.addons["cycles"].preferences
    cp.compute_device_type = "OPTIX"
    cp.get_devices()
    for d in cp.devices:
        d.use = d.type == "OPTIX"
    sc.cycles.device = "GPU"
except Exception as e:
    print("gpu", e)
sc.cycles.samples = 48 if FAST else 192
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 5
sc.cycles.volume_bounces = 1
sc.cycles.volume_step_rate = 2.0
sc.render.resolution_x, sc.render.resolution_y = (1280, 720) if FAST else (1600, 900)
try:
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
except Exception as e:
    print("cm", e)
sc.view_settings.exposure = -0.2


# ---------------------------------------------------------------- helpers
def N(nt, kind, **inputs):
    n = nt.nodes.new(kind)
    for k, v in inputs.items():
        if k.startswith("_"):
            setattr(n, k[1:], v)
        else:
            n.inputs[k].default_value = v
    return n


def L(nt, a, b):
    nt.links.new(a, b)


def mth(nt, op, a=None, b=None, va=0.0, vb=0.0):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    if a is not None:
        L(nt, a, n.inputs[0])
    else:
        n.inputs[0].default_value = va
    if b is not None:
        L(nt, b, n.inputs[1])
    else:
        n.inputs[1].default_value = vb
    return n.outputs[0]


def mix(nt, fac, a, b):
    m = N(nt, "ShaderNodeMix", _data_type="RGBA")
    L(nt, fac, m.inputs[0])
    for sock, v in ((6, a), (7, b)):
        if isinstance(v, tuple):
            m.inputs[sock].default_value = (*v, 1) if len(v) == 3 else v
        else:
            L(nt, v, m.inputs[sock])
    return m.outputs[2]


def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    return m, nt, N(nt, "ShaderNodeOutputMaterial")


def obj(name, bm, mat=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    if mat:
        me.materials.append(mat)
    return ob


ASH = (0.2, 0.19, 0.185)


def pix(name, c0, c1, rough=0.88, ash=0.7, bricks=None, emit=None, estr=0.0):
    """Minecraft-ish block texture: 16 px per block of noise between two colours, optional brick seams; ash lies on top
    faces (in patches, thick where `ash` is high) and greys the sides a little."""
    m, nt, out = new_mat(name)
    geo = N(nt, "ShaderNodeNewGeometry")
    snap = N(nt, "ShaderNodeVectorMath", _operation="SNAP")
    snap.inputs[1].default_value = (1 / 16, 1 / 16, 1 / 16)
    # nudge inward along the normal so a face's pixels belong to its own block
    nudge = N(nt, "ShaderNodeVectorMath", _operation="SCALE")
    nudge.inputs["Scale"].default_value = -0.01
    L(nt, geo.outputs["Normal"], nudge.inputs[0])
    pos = N(nt, "ShaderNodeVectorMath", _operation="ADD")
    L(nt, geo.outputs["Position"], pos.inputs[0])
    L(nt, nudge.outputs[0], pos.inputs[1])
    L(nt, pos.outputs[0], snap.inputs[0])
    wn = N(nt, "ShaderNodeTexWhiteNoise", _noise_dimensions="3D")
    L(nt, snap.outputs[0], wn.inputs["Vector"])
    col = mix(nt, wn.outputs["Value"], c0, c1)
    if bricks:
        # seams: every 1/2 block in z, every block in x/y offset per course
        sp = N(nt, "ShaderNodeSeparateXYZ")
        L(nt, snap.outputs[0], sp.inputs[0])
        course = mth(nt, "FLOOR", mth(nt, "MULTIPLY", sp.outputs["Z"], vb=2))
        off = mth(nt, "MULTIPLY", mth(nt, "MODULO", course, vb=2), vb=0.5)
        fz = mth(nt, "FRACT", mth(nt, "MULTIPLY", sp.outputs["Z"], vb=2))
        fx = mth(nt, "FRACT", mth(nt, "ADD", mth(nt, "ADD", sp.outputs["X"], sp.outputs["Y"]), off))
        seam = mth(nt, "MAXIMUM", mth(nt, "LESS_THAN", fz, vb=0.07), mth(nt, "LESS_THAN", fx, vb=0.05))
        col = mix(nt, seam, col, bricks)
    sn = N(nt, "ShaderNodeSeparateXYZ")
    L(nt, geo.outputs["Normal"], sn.inputs[0])
    top = mth(nt, "GREATER_THAN", sn.outputs["Z"], vb=0.6)
    big = N(nt, "ShaderNodeTexNoise", Scale=0.35, Detail=3.0)
    L(nt, geo.outputs["Position"], big.inputs["Vector"])
    patch = mth(nt, "GREATER_THAN", mth(nt, "ADD", mth(nt, "MULTIPLY", wn.outputs["Value"], vb=0.45),
                                        mth(nt, "MULTIPLY", big.outputs["Fac"], vb=0.55)), vb=1.0 - ash)
    lay = mth(nt, "MAXIMUM", mth(nt, "MULTIPLY", top, patch), vb=0.12 * ash)
    ashc = mix(nt, wn.outputs["Value"], tuple(c * 0.85 for c in ASH), tuple(c * 1.15 for c in ASH))
    col = mix(nt, lay, col, ashc)
    b = N(nt, "ShaderNodeBsdfPrincipled", Roughness=rough)
    L(nt, col, b.inputs["Base Color"])
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = estr
    L(nt, b.outputs[0], out.inputs["Surface"])
    return m


def glow(name, col, strength):
    m, nt, out = new_mat(name)
    e = N(nt, "ShaderNodeEmission", Strength=strength)
    e.inputs["Color"].default_value = (*col, 1)
    L(nt, e.outputs[0], out.inputs["Surface"])
    return m


def box(bm, x0, y0, z0, x1, y1, z1):
    vs = [bm.verts.new(p) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                    (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[i] for i in f])


def point(name, loc, col, power, radius=0.4):
    li = bpy.data.lights.new(name, "POINT")
    li.energy, li.color, li.shadow_soft_size = power, col, radius
    ob = bpy.data.objects.new(name, li)
    ob.location = loc
    sc.collection.objects.link(ob)


FIRE = (1.0, 0.42, 0.12)
FIRE_HOT = (1.0, 0.72, 0.35)
WARM = (1.0, 0.58, 0.28)

# ---------------------------------------------------------------- the sky: red under a low ash cloud
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
# cloud mottling on the dome: flattened directions, so it reads as a low deck
flat = N(wt, "ShaderNodeVectorMath", _operation="DIVIDE")
L(wt, tc.outputs["Generated"], flat.inputs[0])
L(wt, mth(wt, "ADD", up, vb=0.12), flat.inputs[1])
cl = N(wt, "ShaderNodeTexNoise", Scale=1.3, Detail=8.0, Roughness=0.62, Distortion=0.6)
L(wt, flat.outputs[0], cl.inputs["Vector"])
lump = mth(wt, "POWER", cl.outputs["Fac"], vb=2.2)
horizon = mth(wt, "POWER", mth(wt, "SUBTRACT", va=1.0, b=mth(wt, "MINIMUM", mth(wt, "MULTIPLY", up, vb=2.6), vb=1.0)), vb=2.0)
base = mix(wt, horizon, (0.006, 0.0008, 0.0005), (0.13, 0.016, 0.005))
lit = mix(wt, mth(wt, "MULTIPLY", lump, vb=1.6), base, (0.26, 0.035, 0.01))
bg = N(wt, "ShaderNodeBackground", Strength=1.0)
L(wt, lit, bg.inputs["Color"])
L(wt, bg.outputs[0], wo.inputs["Surface"])

# the moon, a dim red coin; a red sun-light for its cast
MOON_DIR = Vector((0.15, 1.0, 0.42)) if SHOT == "street" else Vector((-0.3, -1.0, 0.36))
MOON_DIR.normalize()
bm = bmesh.new()
bmesh.ops.create_circle(bm, cap_ends=True, segments=48, radius=26)
moon = obj("moon_disc", bm, glow("moon", (1.0, 0.28, 0.12), 3.5))
moon.location = MOON_DIR * 900
moon.rotation_euler = (-MOON_DIR).to_track_quat("Z", "Y").to_euler()
sun = bpy.data.objects.new("moon_light", bpy.data.lights.new("moon_light", "SUN"))
sun.data.energy = 0.35
sun.data.color = (1.0, 0.35, 0.22)
sun.data.angle = math.radians(4)
sun.rotation_euler = (-MOON_DIR).to_track_quat("-Z", "Y").to_euler()
sc.collection.objects.link(sun)

# ---------------------------------------------------------------- the land: flat in town, rising to hills beyond the wall
WALL_Y = 44


def height(x, y):
    if y < WALL_Y + 3 and abs(x) < 22:
        return 0
    d = max(0.0, y - (WALL_Y + 3)) + max(0.0, abs(x) - 22)
    h = (d / 26) ** 1.25 * (3 + 2.5 * math.sin(x * 0.11) + 2 * math.cos(y * 0.09 + 1))
    return int(round(min(h, 18)))


hmap = {(x, y): height(x, y) for x in range(-48, 48) for y in range(-24, 120)}


def column(bm, x, y, h):
    v = lambda a, b, c: bm.verts.new((a, b, c))
    bm.faces.new([v(x, y, h), v(x + 1, y, h), v(x + 1, y + 1, h), v(x, y + 1, h)])
    for dx, dy, ((ax, ay), (bx, by)) in ((1, 0, ((1, 0), (1, 1))), (-1, 0, ((0, 1), (0, 0))),
                                         (0, 1, ((1, 1), (0, 1))), (0, -1, ((0, 0), (1, 0)))):
        nh = hmap.get((x + dx, y + dy), h - 3)
        for zz in range(max(nh, h - 3), h):
            bm.faces.new([v(x + ax, y + ay, zz), v(x + bx, y + by, zz), v(x + bx, y + by, zz + 1), v(x + ax, y + ay, zz + 1)])


ROAD_W = 3
bm_g, bm_r = bmesh.new(), bmesh.new()
for (x, y), h in hmap.items():
    road = (-ROAD_W <= x < ROAD_W and y < WALL_Y + 30) or (-ROAD_W - 1 <= x < ROAD_W + 1 and y < WALL_Y - 2 and abs(y % 9) < 1)
    column(bm_r if road and h == 0 else bm_g, x, y, h)
M_GRASS = pix("grass", (0.05, 0.13, 0.03), (0.10, 0.24, 0.05), ash=0.66)
M_ROAD = pix("road", (0.13, 0.12, 0.11), (0.24, 0.22, 0.20), ash=0.55, bricks=(0.06, 0.055, 0.05))
obj("ground", bm_g, M_GRASS)
obj("road", bm_r, M_ROAD)

# ---------------------------------------------------------------- the houses: stone foot, plaster and timber, stepped spruce roofs
M_STONE = pix("stone", (0.20, 0.20, 0.20), (0.33, 0.32, 0.31), bricks=(0.09, 0.09, 0.09), ash=0.75)
M_PLASTER = pix("plaster", (0.55, 0.50, 0.42), (0.66, 0.60, 0.50), ash=0.5)
M_TIMBER = pix("timber", (0.07, 0.04, 0.025), (0.12, 0.07, 0.04), ash=0.6)
M_ROOF = pix("roof", (0.09, 0.05, 0.035), (0.17, 0.10, 0.06), ash=0.9)
M_WIN = glow("window", (1.0, 0.42, 0.14), 1.3)
M_DOOR = pix("door", (0.09, 0.05, 0.03), (0.15, 0.09, 0.05), ash=0.0)
bm_s, bm_p, bm_t, bm_rf, bm_w, bm_d = (bmesh.new() for _ in range(6))
lit_windows = []


def house(x0, y0, wx, dy, floors, face):
    """face +1: door on the +x side (left row faces the street), -1 on the -x side"""
    h = 2 + floors * 3
    box(bm_s, x0, y0, 0, x0 + wx, y0 + dy, 2)
    box(bm_p, x0 + 0.05, y0 + 0.05, 2, x0 + wx - 0.05, y0 + dy - 0.05, h)
    # the frame: corner posts, a beam at every floor, braces on the street side
    for cx in (x0, x0 + wx - 1):
        for cy in (y0, y0 + dy - 1):
            box(bm_t, cx, cy, 2, cx + 1, cy + 1, h)
    for z in range(2, h + 1, 3):
        box(bm_t, x0, y0, z - 0.0, x0 + wx, y0 + dy, z + 0.35 if z < h else z)
    sx = x0 + wx if face > 0 else x0
    for y in range(int(y0) + 2, int(y0 + dy) - 2, 3):
        box(bm_t, sx - 0.12 * face - 0.12, y, 2, sx - 0.12 * face + 0.12, y + 0.35, h)
    # windows on the street side, lit; a door
    for f in range(floors):
        for y in range(int(y0) + 1, int(y0 + dy) - 1, 3):
            if f == 0 and y == int(y0) + 1:
                continue
            z = 3 + f * 3
            if rs.random() < 0.82:
                box(bm_w, sx - 0.06, y + 0.65, z + 0.1, sx + 0.06, y + 1.35, z + 1.1)
                box(bm_t, sx - 0.09, y + 0.96, z + 0.1, sx + 0.09, y + 1.04, z + 1.1)
                box(bm_t, sx - 0.09, y + 0.65, z + 0.56, sx + 0.09, y + 1.35, z + 0.64)
                lit_windows.append(Vector((sx + 0.6 * face, y + 1.0, z + 0.6)))
            box(bm_t, sx - 0.1, y + 0.4, z - 0.15, sx + 0.1, y + 1.6, z)
    box(bm_d, sx - 0.08, y0 + 1.2, 0, sx + 0.08, y0 + 2.8, 2.6)
    # the roof: steps along x, overhanging one block, ridge along y
    half = wx / 2 + 1
    k = 0
    while half - k > 0.5:
        box(bm_rf, x0 - 1 + k, y0 - 1, h + k, x0 + wx + 1 - k, y0 + dy + 1, h + k + 1)
        k += 1
    # a chimney
    cx = x0 + (1 if face < 0 else wx - 2)
    box(bm_s, cx, y0 + dy - 3, h, cx + 1, y0 + dy - 2, h + k + 2)


for i, (y0, dy) in enumerate(((0, 9), (11, 8), (21, 9), (32, 8))):
    house(-6 - 7 - (i % 2), y0, 7 + (i % 2), dy, 2 + (i % 2), +1)
    house(6, y0 + 1, 7 + ((i + 1) % 2), dy - 1, 2 + ((i + 1) % 2), -1)
for b, m in ((bm_s, M_STONE), (bm_p, M_PLASTER), (bm_t, M_TIMBER), (bm_rf, M_ROOF), (bm_w, M_WIN), (bm_d, M_DOOR)):
    obj("house_" + m.name, b, m)
for i, p in enumerate(lit_windows):
    point("win%d" % i, p, WARM, 16, 0.6)

# ---------------------------------------------------------------- the wall and its shut gate
bm_wl, bm_gt, bm_ir = bmesh.new(), bmesh.new(), bmesh.new()
WH = 8
for x in range(-24, 24):
    if -3 <= x < 3:
        box(bm_wl, x, WALL_Y, 6, x + 1, WALL_Y + 3, WH)
    else:
        box(bm_wl, x, WALL_Y, 0, x + 1, WALL_Y + 3, WH)
    if x % 2 == 0:
        box(bm_wl, x, WALL_Y, WH, x + 1, WALL_Y + 0.6, WH + 1)
        box(bm_wl, x, WALL_Y + 2.4, WH, x + 1, WALL_Y + 3, WH + 1)
# gate towers
for tx in (-7, 4):
    box(bm_wl, tx, WALL_Y - 1, 0, tx + 3, WALL_Y + 4, WH + 4)
    for cx in (tx, tx + 2):
        box(bm_wl, cx, WALL_Y - 1, WH + 4, cx + 1, WALL_Y + 4, WH + 5)
# the gate: dark oak leaves, shut, iron bands and a bar across
box(bm_gt, -3, WALL_Y + 1.3, 0, 3, WALL_Y + 1.7, 6)
for z in (1.0, 3.0, 5.0):
    box(bm_ir, -3, WALL_Y + 1.15, z, 3, WALL_Y + 1.3, z + 0.25)
box(bm_ir, -3.4, WALL_Y + 1.0, 2.4, 3.4, WALL_Y + 1.3, 2.9)
obj("wall", bm_wl, M_STONE)
obj("gate", bm_gt, pix("gate_wood", (0.06, 0.035, 0.02), (0.11, 0.065, 0.04), ash=0.0))
M_IRON = pix("iron", (0.05, 0.05, 0.055), (0.10, 0.10, 0.11), rough=0.5, ash=0.4)
obj("iron", bm_ir, M_IRON)

# ---------------------------------------------------------------- braziers: an iron bowl on a stone post, live fire
M_FIRE = None


def fire_mat():
    """a flame as an emitting volume in its own little box (object coords -1..1): hot and thick at the foot, licking
    up into tongues that thin and redden, a wisp of smoke over it"""
    m, nt, out = new_mat("fire")
    tc = N(nt, "ShaderNodeTexCoord")
    sp = N(nt, "ShaderNodeSeparateXYZ")
    L(nt, tc.outputs["Object"], sp.inputs[0])
    h = mth(nt, "MULTIPLY", mth(nt, "ADD", sp.outputs["Z"], vb=1.0), vb=0.5)          # 0 foot .. 1 top
    # stretch the noise upward so it reads as tongues
    st = N(nt, "ShaderNodeVectorMath", _operation="MULTIPLY")
    st.inputs[1].default_value = (1.0, 1.0, 0.45)
    L(nt, tc.outputs["Object"], st.inputs[0])
    rnd = N(nt, "ShaderNodeVectorMath", _operation="ADD")
    L(nt, st.outputs[0], rnd.inputs[0])
    L(nt, tc.outputs["Object"], rnd.inputs[1])
    nz = N(nt, "ShaderNodeTexNoise", Scale=2.4, Detail=6.0, Roughness=0.62, Distortion=0.8)
    L(nt, st.outputs[0], nz.inputs["Vector"])
    r = mth(nt, "SQRT", mth(nt, "ADD", mth(nt, "MULTIPLY", sp.outputs["X"], sp.outputs["X"]), mth(nt, "MULTIPLY", sp.outputs["Y"], sp.outputs["Y"])))
    # the cone a flame may fill narrows as it rises; the noise eats into its edge
    allow = mth(nt, "SUBTRACT", mth(nt, "MULTIPLY", mth(nt, "SUBTRACT", va=1.0, b=h), vb=0.95), mth(nt, "MULTIPLY", nz.outputs["Fac"], vb=0.55))
    core = mth(nt, "MAXIMUM", mth(nt, "MULTIPLY", mth(nt, "SUBTRACT", allow, mth(nt, "MULTIPLY", r, vb=0.6)), vb=3.0), vb=0.0)
    heat = mth(nt, "MINIMUM", core, vb=1.0)
    ramp = N(nt, "ShaderNodeValToRGB")
    L(nt, heat, ramp.inputs[0])
    el = ramp.color_ramp.elements
    el[0].position, el[0].color = 0.0, (0.5, 0.06, 0.01, 1)
    el[1].position, el[1].color = 1.0, (1.0, 0.78, 0.42, 1)
    mid = el.new(0.35)
    mid.color = (1.0, 0.3, 0.05, 1)
    vol = N(nt, "ShaderNodeVolumePrincipled", Density=0.0)
    L(nt, ramp.outputs[0], vol.inputs["Emission Color"])
    L(nt, mth(nt, "MULTIPLY", mth(nt, "POWER", heat, vb=1.4), vb=60.0), vol.inputs["Emission Strength"])
    # smoke above: thin dark, where the flame has ended
    smoke = mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", h, h), mth(nt, "MAXIMUM", mth(nt, "SUBTRACT", nz.outputs["Fac"], vb=0.45), vb=0.0))
    L(nt, mth(nt, "MULTIPLY", smoke, vb=6.0), vol.inputs["Density"])
    vol.inputs["Color"].default_value = (0.05, 0.04, 0.04, 1)
    L(nt, vol.outputs[0], out.inputs["Volume"])
    return m


M_FIRE = fire_mat()
M_COAL = glow("coal", (1.0, 0.3, 0.06), 12.0)
bm_bp, bm_bw, bm_fl, bm_co = bmesh.new(), bmesh.new(), bmesh.new(), bmesh.new()
BRAZIERS = []
FIRES = []


def brazier(x, y, z, post=True):
    if post:
        box(bm_bp, x - 0.4, y - 0.4, z, x + 0.4, y + 0.4, z + 1.4)
        z += 1.4
    # the bowl: an 8-sided tapered ring of iron
    for a in range(8):
        a0, a1 = a * math.pi / 4, (a + 1) * math.pi / 4
        vs = []
        for (r, zz) in ((0.35, z), (0.75, z + 0.55)):
            vs.append((x + math.cos(a0) * r, y + math.sin(a0) * r, zz))
            vs.append((x + math.cos(a1) * r, y + math.sin(a1) * r, zz))
        q = [bm_bw.verts.new(p) for p in (vs[0], vs[1], vs[3], vs[2])]
        bm_bw.faces.new(q)
    box(bm_co, x - 0.5, y - 0.5, z + 0.25, x + 0.5, y + 0.5, z + 0.45)
    FIRES.append(Vector((x, y, z + 0.35)))
    BRAZIERS.append(Vector((x, y, z + 1.1)))


for bx in (-4.5, 4.5):
    brazier(bx, WALL_Y - 2.2, 0)
    brazier(bx, WALL_Y + 4.6, 0)
for tx in (-5.5, 5.5):
    brazier(tx, WALL_Y + 1.5, WH + 5, post=False)
for x in range(-20, 22, 6):
    if abs(x) > 8:
        brazier(x + 0.5, WALL_Y + 1.5, WH, post=False)
for y in (6, 18, 29):
    brazier(-4.2, y, 0)
    brazier(4.2, y + 4, 0)
obj("brazier_post", bm_bp, M_STONE)
obj("brazier_bowl", bm_bw, M_IRON)
obj("brazier_coal", bm_co, M_COAL)
bm_fl.free()
for i, p in enumerate(FIRES):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2)
    f = obj("fire%d" % i, bm, M_FIRE)
    f.location = p + Vector((0, 0, 0.9))
    f.scale = (0.62, 0.62, 0.95)
    f.rotation_euler = (0, 0, rs.uniform(0, 6.28))
for i, p in enumerate(BRAZIERS):
    point("braz%d" % i, p, FIRE, 320, 0.5)

# ---------------------------------------------------------------- far off: the fire-mountain that woke, its plume feeding the cloud
MT = Vector((0, 0, 0)) if SHOT == "mountain" else Vector((-260, 980, 0)) if SHOT == "street" else Vector((280, -900, 0))
bm = bmesh.new()
# a polar grid, jagged: ridges run down from the crater, its rim broken
RA, RR, MR, MH = 72, 26, 300, 190
rows = []
for j in range(RR + 1):
    r = j / RR
    row = []
    for i in range(RA):
        ang = i / RA * 2 * math.pi
        ridge = 0.5 + 0.5 * math.sin(ang * 7 + math.sin(ang * 3) * 2) * math.sin(ang * 13 + 1.3)
        hgt = MH * (1 - r) ** 1.35 * (0.86 + 0.14 * ridge) + rs.uniform(-3, 3) * (1 - r)
        rad = MR * (0.1 + 0.9 * r) * (1 + 0.06 * math.sin(ang * 5 + r * 4))
        if j == 0:
            hgt -= 22
        row.append(bm.verts.new((math.cos(ang) * rad, math.sin(ang) * rad, max(0, hgt))))
    rows.append(row)
for j in range(RR):
    for i in range(RA):
        bm.faces.new([rows[j][i], rows[j][(i + 1) % RA], rows[j + 1][(i + 1) % RA], rows[j + 1][i]])
mt = obj("mountain", bm, pix("mountain", (0.02, 0.016, 0.015), (0.045, 0.035, 0.03), ash=0.0))
mt.location = MT
bm = bmesh.new()
bmesh.ops.create_circle(bm, cap_ends=True, segments=48, radius=MR * 0.1)
cr = obj("crater", bm, glow("crater", (1.0, 0.32, 0.08), 22.0))
cr.location = MT + Vector((0, 0, MH * 0.88 - 20))

m, nt, out = new_mat("plume")
tco = N(nt, "ShaderNodeTexCoord")
sp = N(nt, "ShaderNodeSeparateXYZ")
L(nt, tco.outputs["Object"], sp.inputs[0])
nz = N(nt, "ShaderNodeTexNoise", Scale=2.2, Detail=6.0, Roughness=0.6, Distortion=0.5)
L(nt, tco.outputs["Object"], nz.inputs["Vector"])
r = mth(nt, "SQRT", mth(nt, "ADD", mth(nt, "MULTIPLY", sp.outputs["X"], sp.outputs["X"]), mth(nt, "MULTIPLY", sp.outputs["Y"], sp.outputs["Y"])))
# widening as it rises: radius allowed grows with z (object space -1..1)
allow = mth(nt, "ADD", mth(nt, "MULTIPLY", mth(nt, "ADD", sp.outputs["Z"], vb=1.0), vb=0.42), vb=0.12)
inside = mth(nt, "GREATER_THAN", mth(nt, "SUBTRACT", allow, mth(nt, "SUBTRACT", r, mth(nt, "MULTIPLY", nz.outputs["Fac"], vb=0.35))), vb=0.0)
dens = mth(nt, "MULTIPLY", inside, mth(nt, "MULTIPLY", nz.outputs["Fac"], vb=0.07))
vol = N(nt, "ShaderNodeVolumePrincipled")
vol.inputs["Color"].default_value = (0.03, 0.022, 0.02, 1)
L(nt, dens, vol.inputs["Density"])
vol.inputs["Emission Color"].default_value = (1.0, 0.22, 0.05, 1)
low = mth(nt, "POWER", mth(nt, "SUBTRACT", va=1.0, b=mth(nt, "MULTIPLY", mth(nt, "ADD", sp.outputs["Z"], vb=1.0), vb=0.5)), vb=4.0)
L(nt, mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", low, inside), vb=0.05), vol.inputs["Emission Strength"])
L(nt, vol.outputs[0], out.inputs["Volume"])
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=2)
pl = obj("plume", bm, m)
pl.location = MT + Vector((0, 0, MH * 0.8 + 210))
pl.scale = (170, 170, 220)

# ---------------------------------------------------------------- the air: thin ash haze over the town, lit by the fires
m, nt, out = new_mat("haze")
vol = N(nt, "ShaderNodeVolumePrincipled", Density=0.0045, Anisotropy=0.45)
vol.inputs["Color"].default_value = (0.4, 0.36, 0.34, 1)
L(nt, vol.outputs[0], out.inputs["Volume"])
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=2)
hz = obj("haze", bm, m)
hz.location = (0, 40, 14)
hz.scale = (60, 80, 14)

# ---------------------------------------------------------------- ash flakes drifting down, a few still alight
CAM = {"mountain": ((0, -1500, 190), (0, 0, 190), 50), "street": ((1.6, -7.0, 2.3), (-0.6, 44, 7.2), 22), "outside": ((9, 74, 9.5), (-1, 38, 6.5), 26)}
loc, aim, lens = CAM[SHOT]
camv = Vector(loc)
fwd = (Vector(aim) - camv).normalized()
bm_a, bm_e = bmesh.new(), bmesh.new()
n_a = n_e = 0
while n_a < 26000:
    d = 3.5 + 66 * rs.random() ** (1 / 3)
    p = camv + fwd * d + Vector((rs.uniform(-1, 1) * d * 0.75, rs.uniform(-1, 1) * d * 0.4, rs.uniform(-0.5, 1) * d * 0.5))
    if p.z < hmap.get((int(p.x), int(p.y)), 0) + 0.1:
        continue
    s = rs.uniform(0.016, 0.034) * (1 + d / 35)
    ember = rs.random() < 0.025
    target = bm_e if ember else bm_a
    # a flake: a tumbling quad, a little stretched by its fall
    a, b = Vector((rs.uniform(-1, 1), rs.uniform(-1, 1), rs.uniform(-1, 1))).normalized(), Vector((rs.uniform(-1, 1), rs.uniform(-1, 1), rs.uniform(-1, 1)))
    b = (b - a * a.dot(b)).normalized()
    a *= s
    b *= s * rs.uniform(0.6, 1.0)
    a += Vector((0.03, 0.01, -1)) * s * 0.9
    target.faces.new([target.verts.new(p + v) for v in (-a - b, a - b, a + b, -a + b)])
    n_a += 1
m, nt, out = new_mat("ash_flake")
b = N(nt, "ShaderNodeBsdfPrincipled", Roughness=0.95)
b.inputs["Base Color"].default_value = (0.42, 0.40, 0.39, 1)
tr = N(nt, "ShaderNodeBsdfTranslucent")
tr.inputs["Color"].default_value = (0.5, 0.45, 0.42, 1)
mx = N(nt, "ShaderNodeMixShader", Fac=0.3)
L(nt, b.outputs[0], mx.inputs[1])
L(nt, tr.outputs[0], mx.inputs[2])
L(nt, mx.outputs[0], out.inputs["Surface"])
obj("ash", bm_a, m)
obj("embers", bm_e, glow("ember", (1.0, 0.36, 0.08), 18.0))

# ---------------------------------------------------------------- camera, bloom, render
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 3000
cam.location = loc
cam.data.lens = lens
cam.rotation_euler = (Vector(aim) - camv).to_track_quat("-Z", "Y").to_euler()
try:
    ng = bpy.data.node_groups.new("comp", "CompositorNodeTree")
    sc.compositing_node_group = ng
    rl = ng.nodes.new("CompositorNodeRLayers")
    gl = ng.nodes.new("CompositorNodeGlare")
    gl.inputs["Type"].default_value = "Bloom"
    gl.inputs["Quality"].default_value = "High"
    gl.inputs["Threshold"].default_value = 1.0
    gl.inputs["Strength"].default_value = 0.45
    gl.inputs["Size"].default_value = 0.65
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    go = ng.nodes.new("NodeGroupOutput")
    ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
    ng.links.new(gl.outputs["Image"], go.inputs[0])
    sc.render.use_compositing = True
except Exception as ex:
    print("COMP FAIL", ex)
if SHOT == "mountain":
    # the fire-mountain alone on clear film, flat-on, for the sky in game (client/AshfallSky)
    for ob in list(sc.objects):
        if ob.name not in ("mountain", "crater", "plume", "moon_light", "cam"):
            bpy.data.objects.remove(ob, do_unlink=True)
    sc.render.film_transparent = True
    sc.render.resolution_x, sc.render.resolution_y = 1024, 512
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 760
    sc.render.image_settings.color_mode = "RGBA"
    OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "renders", "ashfall")
sc.render.image_settings.color_depth = "8"
sc.render.filepath = os.path.abspath(os.path.join(OUT, "ashfall_%s.png" % SHOT))
bpy.ops.render.render(write_still=True)
print("WROTE", sc.render.filepath)
