"""Meteor Fall (concept, Cycles): a shard of a broken gate's crystal ring comes down out of the sky. A white-hot head in
a fireball, a long burning trail going to smoke behind it, pieces breaking off; it lights the land orange as it goes.
Where it lands: a crater of scorched blocks, the middle glassed black and cracked with heat, trees knocked flat and
burnt round it, rock thrown out over the grass. The shard stands leaning in the middle, dark crystal with the gate's
colour moving in its veins, its foot still red-hot, smoke climbing off it for the whole region to see.
  blender -b -P tools/blender/meteor_fall.py -- [fall|crater] [fast]  ->  tools/renders/meteor/meteor_<shot>.png"""
import os, sys, math, random
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SHOT = next((a for a in ARGS if a in ("fall", "crater")), "crater")
FAST = "fast" in ARGS
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "renders", "meteor")
os.makedirs(OUT, exist_ok=True)
rs = random.Random(7)

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
sc.view_settings.exposure = 0.0


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


def ramp(nt, fac, stops):
    r = N(nt, "ShaderNodeValToRGB")
    L(nt, fac, r.inputs[0])
    el = r.color_ramp.elements
    el[0].position, el[0].color = stops[0][0], (*stops[0][1], 1)
    el[1].position, el[1].color = stops[-1][0], (*stops[-1][1], 1)
    for p, c in stops[1:-1]:
        e = el.new(p)
        e.color = (*c, 1)
    return r.outputs[0]


def pix(name, c0, c1, rough=0.88, soot=0.0, cracks=None, emit=None, estr=0.0):
    """Minecraft-ish block texture: 16 px per block of noise between two colours. `soot` greys/blackens in patches;
    `cracks` = (colour, strength): glowing heat cracks along cell edges in world xy."""
    m, nt, out = new_mat(name)
    geo = N(nt, "ShaderNodeNewGeometry")
    snap = N(nt, "ShaderNodeVectorMath", _operation="SNAP")
    snap.inputs[1].default_value = (1 / 16, 1 / 16, 1 / 16)
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
    if soot:
        big = N(nt, "ShaderNodeTexNoise", Scale=0.3, Detail=3.0)
        L(nt, snap.outputs[0], big.inputs["Vector"])
        patch = mth(nt, "GREATER_THAN", mth(nt, "ADD", mth(nt, "MULTIPLY", wn.outputs["Value"], vb=0.4),
                                            mth(nt, "MULTIPLY", big.outputs["Fac"], vb=0.6)), vb=1.0 - soot)
        col = mix(nt, patch, col, mix(nt, wn.outputs["Value"], (0.02, 0.018, 0.017), (0.06, 0.05, 0.045)))
    b = N(nt, "ShaderNodeBsdfPrincipled", Roughness=rough)
    L(nt, col, b.inputs["Base Color"])
    if cracks:
        vo = N(nt, "ShaderNodeTexVoronoi", _feature="DISTANCE_TO_EDGE", Scale=0.32)
        L(nt, snap.outputs[0], vo.inputs["Vector"])
        line = mth(nt, "LESS_THAN", vo.outputs["Distance"], vb=0.03)
        b.inputs["Emission Color"].default_value = (*cracks[0], 1)
        L(nt, mth(nt, "MULTIPLY", line, vb=cracks[1]), b.inputs["Emission Strength"])
        col = mix(nt, line, col, cracks[0])
        L(nt, col, b.inputs["Base Color"])
    elif emit:
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


def tbox(bm, c, s, rot):
    """a cube of side s at centre c, turned by the Euler rot"""
    mt = rot.to_matrix()
    h = s / 2
    vs = [bm.verts.new(Vector(c) + mt @ Vector((x * h, y * h, z * h))) for (x, y, z) in
          ((-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[i] for i in f])


def point(name, loc, col, power, radius=0.4):
    li = bpy.data.lights.new(name, "POINT")
    li.energy, li.color, li.shadow_soft_size = power, col, radius
    ob = bpy.data.objects.new(name, li)
    ob.location = loc
    ob.visible_glossy = False
    sc.collection.objects.link(ob)
    return ob


def vol_cube(name, mat, loc, scale, rot=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2)
    o = obj(name, bm, mat)
    o.location = loc
    o.scale = scale
    if rot is not None:
        o.rotation_euler = rot
    return o


GATE = (0.62, 0.22, 1.0)          # the gate's own colour in the shard (violet; in game: the rank's colour)
GATE_HOT = (0.85, 0.65, 1.0)
HEAT = (1.0, 0.36, 0.08)
HEAT_HOT = (1.0, 0.72, 0.38)

# ---------------------------------------------------------------- the sky: dusk, the sun gone, deep blue over a red rim
w = bpy.data.worlds.new("w")
sc.world = w
w.use_nodes = True
wt = w.node_tree
for n in list(wt.nodes):
    wt.nodes.remove(n)
wo = N(wt, "ShaderNodeOutputWorld")
bg = N(wt, "ShaderNodeBackground", Strength=0.2 if SHOT == "fall" else 0.5)
try:
    sky = wt.nodes.new("ShaderNodeTexSky")
    for t in ("MULTIPLE_SCATTERING", "NISHITA"):
        try:
            sky.sky_type = t
            break
        except TypeError:
            pass
    sky.sun_elevation = math.radians(-1.5 if SHOT == "fall" else 1.0)
    sky.sun_rotation = math.radians(250)
    sky.sun_disc = False
    tint = N(wt, "ShaderNodeMix", _data_type="RGBA", _blend_type="MULTIPLY")
    tint.inputs[0].default_value = 1.0
    tint.inputs[7].default_value = (0.85, 0.8, 1.0, 1)
    L(wt, sky.outputs[0], tint.inputs[6])
    L(wt, tint.outputs[2], bg.inputs["Color"])
except Exception as e:
    print("sky", e)
    bg.inputs["Color"].default_value = (0.02, 0.025, 0.06, 1)
L(wt, bg.outputs[0], wo.inputs["Surface"])
moon = bpy.data.objects.new("sky_fill", bpy.data.lights.new("sky_fill", "SUN"))
moon.data.energy = 0.25
moon.data.color = (0.55, 0.62, 1.0)
moon.data.angle = math.radians(8)
moon.rotation_euler = (math.radians(55), 0, math.radians(120))
sc.collection.objects.link(moon)

# ---------------------------------------------------------------- the land: rolling block hills
if SHOT == "crater":
    XR, YR = range(-70, 71), range(-70, 90)
else:
    XR, YR = range(-120, 121), range(-90, 200)
CR = 11.0                  # the crater's radius
BASE = 64


def base_h(x, y):
    h = 2.6 * math.sin(x * 0.07) + 2.0 * math.cos(y * 0.05 + 1) + 1.5 * math.sin((x + y) * 0.11)
    if SHOT == "fall":
        # the camera stands on a rise at the near edge; the land falls away in front then swells to far ridges
        h += 9 * math.exp(-((x - 4) ** 2 + (y + 70) ** 2) / 900) + max(0, y - 60) * 0.12 * (1 + 0.6 * math.sin(x * 0.03))
    return BASE + int(round(h))


hmap, kind = {}, {}
for x in XR:
    for y in YR:
        h = base_h(x, y)
        k = "grass"
        if SHOT == "crater":
            r = math.hypot(x + 0.5, y + 0.5)
            if r < CR:
                h = base_h(0, 0) - int(round(5.5 * (1 - (r / CR) ** 2)))
                k = "glass" if r < 4.5 else "scorch"
            elif r < CR + 3.5:
                h += int(round(max(0.0, 2.2 - abs(r - (CR + 1.2)) * 1.1)))
                k = "rim"
            elif r < CR * 2.3 + rs.uniform(-2, 2):
                k = "burnt" if rs.random() < 0.75 - (r - CR) / (CR * 2.6) else "grass"
        hmap[(x, y)], kind[(x, y)] = h, k


def column(bm, x, y, h):
    v = lambda a, b, c: bm.verts.new((a, b, c))
    bm.faces.new([v(x, y, h), v(x + 1, y, h), v(x + 1, y + 1, h), v(x, y + 1, h)])
    for dx, dy, ((ax, ay), (bx, by)) in ((1, 0, ((1, 0), (1, 1))), (-1, 0, ((0, 1), (0, 0))),
                                         (0, 1, ((1, 1), (0, 1))), (0, -1, ((0, 0), (1, 0)))):
        nh = hmap.get((x + dx, y + dy), h - 3)
        for zz in range(max(nh, h - 3), h):
            bm.faces.new([v(x + ax, y + ay, zz), v(x + bx, y + by, zz), v(x + bx, y + by, zz + 1), v(x + ax, y + ay, zz + 1)])


MATS = {
    "grass": pix("grass", (0.07, 0.20, 0.035), (0.13, 0.32, 0.05)),
    "burnt": pix("burnt", (0.06, 0.10, 0.025), (0.12, 0.12, 0.05), soot=0.35),
    "rim": pix("rim", (0.06, 0.045, 0.035), (0.13, 0.10, 0.075), soot=0.5),
    "scorch": pix("scorch", (0.035, 0.03, 0.03), (0.08, 0.07, 0.065), soot=0.45, cracks=(HEAT, 2.5)),
    "glass": pix("glass", (0.008, 0.006, 0.012), (0.03, 0.022, 0.04), rough=0.18, cracks=(HEAT_HOT, 9.0)),
}
bms = {k: bmesh.new() for k in MATS}
for (x, y), h in hmap.items():
    column(bms[kind[(x, y)]], x, y, h)
for k, b in bms.items():
    obj("ground_" + k, b, MATS[k])

# beyond the blocks: smooth land to the horizon
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=140, y_segments=140, size=1400)
for v in bm.verts:
    x, y = v.co.x, v.co.y
    d = max(abs(x) - XR.stop, y - YR.stop, YR.start - y, 0)
    v.co.z = BASE - 3 + (d / 160) ** 1.2 * (14 + 9 * math.sin(x * 0.006) + 11 * math.cos(y * 0.005 + 1)) * (1 if SHOT == "fall" else 0.35) + \
        (max(0, y - 60) * 0.12 if SHOT == "fall" else 0)
far = obj("far_land", bm, MATS["grass"])

# ---------------------------------------------------------------- trees: wildwood-coloured, knocked flat and burnt near the crater
M_LOG = pix("log", (0.16, 0.09, 0.05), (0.26, 0.15, 0.08))
M_CHAR = pix("char", (0.02, 0.016, 0.014), (0.05, 0.04, 0.035))
LEAVES = [pix("leaf_a", (0.06, 0.26, 0.05), (0.16, 0.42, 0.08)),
          pix("leaf_b", (0.12, 0.30, 0.04), (0.26, 0.46, 0.06)),
          pix("leaf_c", (0.40, 0.16, 0.05), (0.62, 0.30, 0.08))]
M_SCORCH_LEAF = pix("leaf_scorch", (0.18, 0.08, 0.02), (0.34, 0.16, 0.04), soot=0.35)
bm_log, bm_char, bm_sl = bmesh.new(), bmesh.new(), bmesh.new()
bm_lv = [bmesh.new() for _ in LEAVES]


def tree(x, y, burnt=0, fall_dir=None):
    gz = hmap.get((x, y), BASE)
    tall = rs.randint(4, 7)
    if fall_dir is not None:
        # knocked flat, pointing away from the blast, charred
        for i in range(tall):
            p = Vector((x + 0.5, y + 0.5, gz + 0.5)) + fall_dir * (i + 0.5)
            tbox(bm_char, p, 1.0, Euler((0, 0, math.atan2(fall_dir.y, fall_dir.x))))
        return
    for z in range(tall):
        box(bm_char if burnt == 2 else bm_log, x, y, gz + z, x + 1, y + 1, gz + z + 1)
    if burnt == 2:
        # a stripped snag, a couple of charred stubs
        box(bm_char, x + 1, y, gz + tall - 2, x + 2, y + 1, gz + tall - 1)
        return
    target = bm_sl if burnt == 1 else rs.choice(bm_lv[:2] if rs.random() < 0.85 else bm_lv)
    rad = rs.uniform(2.0, 3.0)
    cz = gz + tall
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            for dz in range(-2, 3):
                if dx * dx + dy * dy + (dz * 1.3) ** 2 <= rad * rad + rs.uniform(-1, 1):
                    box(target, x + dx, y + dy, cz + dz, x + dx + 1, y + dy + 1, cz + dz + 1)


spots = []
for _ in range(900 if SHOT == "fall" else 420):
    x, y = rs.choice(XR), rs.choice(YR)
    if any(abs(x - a) < 5 and abs(y - b) < 5 for a, b in spots):
        continue
    if SHOT == "fall" and math.hypot(x - 4, y + 70) < 16:
        continue      # the camera's rise stays open
    spots.append((x, y))
    r = math.hypot(x, y)
    if SHOT == "crater" and r < CR + 3:
        continue
    if SHOT == "crater" and r < CR * 2.0:
        tree(x, y, fall_dir=Vector((x, y, 0)).normalized())
    elif SHOT == "crater" and r < CR * 2.6:
        tree(x, y, burnt=2)
    elif SHOT == "crater" and r < CR * 3.3:
        tree(x, y, burnt=1)
    else:
        tree(x, y)
obj("logs", bm_log, M_LOG)
obj("charred", bm_char, M_CHAR)
obj("leaves_scorched", bm_sl, M_SCORCH_LEAF)
for i, b in enumerate(bm_lv):
    obj("leaves_%d" % i, b, LEAVES[i])


# ---------------------------------------------------------------- the shard: dark crystal off a gate's ring, veins of the gate's colour
def crystal_mat(name, heat_at_foot=True):
    m, nt, out = new_mat(name)
    tc = N(nt, "ShaderNodeTexCoord")
    sp = N(nt, "ShaderNodeSeparateXYZ")
    L(nt, tc.outputs["Object"], sp.inputs[0])
    b = N(nt, "ShaderNodeBsdfPrincipled", Roughness=0.12)
    b.inputs["Base Color"].default_value = (0.004, 0.003, 0.008, 1)
    b.inputs["Roughness"].default_value = 0.22
    try:
        b.inputs["Coat Weight"].default_value = 0.25
    except KeyError:
        pass
    # veins: warped noise turned into thin bright bands
    nz = N(nt, "ShaderNodeTexNoise", Scale=0.22, Detail=4.0, Roughness=0.5, Distortion=1.1)
    L(nt, tc.outputs["Object"], nz.inputs["Vector"])
    band = mth(nt, "ABSOLUTE", mth(nt, "SUBTRACT", nz.outputs["Fac"], vb=0.5))
    vein = mth(nt, "POWER", mth(nt, "MAXIMUM", mth(nt, "SUBTRACT", va=1.0, b=mth(nt, "MULTIPLY", band, vb=22.0)), vb=0.0), vb=2.0)
    # a deeper glow from inside, seen through the facets (stronger at grazing angles)
    fr = N(nt, "ShaderNodeLayerWeight", Blend=0.5)
    inner = mth(nt, "MULTIPLY", mth(nt, "POWER", mth(nt, "SUBTRACT", va=1.0, b=fr.outputs["Facing"]), vb=3.0), vb=0.9)
    gate_e = mth(nt, "ADD", mth(nt, "MULTIPLY", vein, vb=5.0), inner)
    col = mix(nt, mth(nt, "MINIMUM", vein, vb=1.0), GATE, GATE_HOT)
    if heat_at_foot:
        # still red-hot where it hit: the foot (object z low) glows the heat's colour over the gate's
        foot = mth(nt, "MINIMUM", mth(nt, "MAXIMUM", mth(nt, "MULTIPLY", mth(nt, "SUBTRACT", va=3.0, b=sp.outputs["Z"]), vb=0.25), vb=0.0), vb=1.0)
        hot = mth(nt, "POWER", foot, vb=1.3)
        col = mix(nt, hot, col, HEAT)
        gate_e = mth(nt, "ADD", gate_e, mth(nt, "MULTIPLY", hot, vb=6.0))
    L(nt, col, b.inputs["Emission Color"])
    L(nt, gate_e, b.inputs["Emission Strength"])
    L(nt, b.outputs[0], out.inputs["Surface"])
    return m


def crystal(bm, root, axis, length, rad, sides=6, rnd=rs):
    """a hex prism with a pointed tip and a broken (flat, ragged) root, built along `axis` from `root`"""
    axis = axis.normalized()
    q = axis.to_track_quat("Z", "Y")
    rings = []
    for z, rr in ((0.0, rad * 1.05), (0.72, rad * 0.92), (0.86, rad * 0.55)):
        ring = []
        for i in range(sides):
            a = i / sides * math.tau + rnd.uniform(-0.12, 0.12)
            p = Vector((math.cos(a) * rr * rnd.uniform(0.85, 1.1), math.sin(a) * rr * rnd.uniform(0.85, 1.1), z * length + rnd.uniform(-0.1, 0.1) * rad))
            ring.append(bm.verts.new(root + q @ p))
        rings.append(ring)
    tip = bm.verts.new(root + q @ Vector((rnd.uniform(-0.15, 0.15) * rad, rnd.uniform(-0.15, 0.15) * rad, length)))
    for j in range(len(rings) - 1):
        for i in range(sides):
            bm.faces.new([rings[j][i], rings[j][(i + 1) % sides], rings[j + 1][(i + 1) % sides], rings[j + 1][i]])
    for i in range(sides):
        bm.faces.new([rings[-1][i], rings[-1][(i + 1) % sides], tip])
    bm.faces.new(list(reversed(rings[0])))


def rock(bm, c, r, rnd=rs):
    """a lump of the burnt crust it came down in"""
    t = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in t["verts"]:
        v.co = Vector(c) + Vector((v.co.x * rnd.uniform(0.75, 1.25), v.co.y * rnd.uniform(0.75, 1.25), v.co.z * rnd.uniform(0.55, 1.0)))


M_SHARD = crystal_mat("shard")
M_CRUST = pix("crust", (0.02, 0.016, 0.015), (0.06, 0.045, 0.04), rough=0.95, cracks=(HEAT, 4.0))


def shard(at, lean, scale=1.0, crust=True):
    """the whole shard: a main crystal and a spray of smaller ones from one broken root, crust round the root"""
    bm_c, bm_k = bmesh.new(), bmesh.new()
    main = Vector((0, 0, 1))
    main.rotate(Euler(lean))
    crystal(bm_c, Vector((0, 0, -1.5)) * scale, main, 12.5 * scale, 2.2 * scale)
    for i in range(6):
        ax = main.copy()
        ax.rotate(Euler((rs.uniform(-0.9, 0.9), rs.uniform(-0.9, 0.9), rs.uniform(0, math.tau))))
        off = Vector((rs.uniform(-1.4, 1.4), rs.uniform(-1.4, 1.4), rs.uniform(-0.8, 0.4))) * scale
        crystal(bm_c, off, ax, rs.uniform(3.5, 7.5) * scale, rs.uniform(0.6, 1.3) * scale)
    if crust:
        for i in range(10):
            a = rs.uniform(0, math.tau)
            rr = rs.uniform(1.2, 3.4) * scale
            rock(bm_k, (math.cos(a) * rr, math.sin(a) * rr, rs.uniform(-0.6, 1.2) * scale), rs.uniform(0.7, 1.6) * scale)
        # crust still stuck on the side that led the fall
        for i in range(5):
            p = main * rs.uniform(1.5, 6.0) * scale + Vector((rs.uniform(-1, 1), rs.uniform(-1, 1), 0)) * 1.4 * scale
            rock(bm_k, p, rs.uniform(0.5, 1.0) * scale)
    oc = obj("shard", bm_c, M_SHARD)
    ok = obj("shard_crust", bm_k, M_CRUST)
    for o in (oc, ok):
        o.location = at
    return oc


# ---------------------------------------------------------------- smoke: a volume that climbs and widens, lit from below
def smoke_mat(name, density, warm, warm_k=3.0):
    m, nt, out = new_mat(name)
    tc = N(nt, "ShaderNodeTexCoord")
    sp = N(nt, "ShaderNodeSeparateXYZ")
    L(nt, tc.outputs["Object"], sp.inputs[0])
    t = mth(nt, "MULTIPLY", mth(nt, "ADD", sp.outputs["Z"], vb=1.0), vb=0.5)          # 0 foot .. 1 top
    # drift: the column bends downwind as it rises
    drift = mth(nt, "SUBTRACT", sp.outputs["X"], mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", t, t), vb=0.9))
    r = mth(nt, "SQRT", mth(nt, "ADD", mth(nt, "MULTIPLY", drift, drift), mth(nt, "MULTIPLY", sp.outputs["Y"], sp.outputs["Y"])))
    st = N(nt, "ShaderNodeVectorMath", _operation="MULTIPLY")
    st.inputs[1].default_value = (1.0, 1.0, 1.3)
    L(nt, tc.outputs["Object"], st.inputs[0])
    nz = N(nt, "ShaderNodeTexNoise", Scale=2.6, Detail=8.0, Roughness=0.68, Distortion=0.35)
    L(nt, st.outputs[0], nz.inputs["Vector"])
    allow = mth(nt, "ADD", mth(nt, "MULTIPLY", t, vb=0.42), vb=0.1)
    edge = mth(nt, "SUBTRACT", allow, mth(nt, "SUBTRACT", r, mth(nt, "MULTIPLY", nz.outputs["Fac"], vb=0.32)))
    inside = mth(nt, "MINIMUM", mth(nt, "MAXIMUM", mth(nt, "MULTIPLY", edge, vb=8.0), vb=0.0), vb=1.0)
    fade = mth(nt, "SUBTRACT", va=1.0, b=mth(nt, "POWER", t, vb=3.0))
    puff = mth(nt, "POWER", mth(nt, "MAXIMUM", mth(nt, "SUBTRACT", nz.outputs["Fac"], vb=0.38), vb=0.0), vb=1.4)
    dens = mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", inside, fade), mth(nt, "MULTIPLY", puff, vb=density * 4))
    vol = N(nt, "ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (0.3, 0.29, 0.3, 1)
    L(nt, dens, vol.inputs["Density"])
    vol.inputs["Emission Color"].default_value = (*warm, 1)
    low = mth(nt, "POWER", mth(nt, "SUBTRACT", va=1.0, b=t), vb=14.0)
    L(nt, mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", low, inside), vb=warm_k), vol.inputs["Emission Strength"])
    L(nt, vol.outputs[0], out.inputs["Volume"])
    return m


def puff_mat():
    """one billow: a ball of smoke, ragged at the edge, its own detail per puff (object random), lit warm low down"""
    m, nt, out = new_mat("puff")
    tc = N(nt, "ShaderNodeTexCoord")
    oi = N(nt, "ShaderNodeObjectInfo")
    sh = N(nt, "ShaderNodeVectorMath", _operation="ADD")
    L(nt, tc.outputs["Object"], sh.inputs[0])
    L(nt, mth(nt, "MULTIPLY", oi.outputs["Random"], vb=97.0), sh.inputs[1])
    nz = N(nt, "ShaderNodeTexNoise", Scale=1.7, Detail=8.0, Roughness=0.66, Distortion=0.25)
    L(nt, sh.outputs[0], nz.inputs["Vector"])
    ln = N(nt, "ShaderNodeVectorMath", _operation="LENGTH")
    L(nt, tc.outputs["Object"], ln.inputs[0])
    edge = mth(nt, "SUBTRACT", mth(nt, "ADD", mth(nt, "MULTIPLY", nz.outputs["Fac"], vb=1.05), vb=0.38), ln.outputs["Value"])
    dens = mth(nt, "MULTIPLY", mth(nt, "MINIMUM", mth(nt, "MAXIMUM", mth(nt, "MULTIPLY", edge, vb=5.0), vb=0.0), vb=1.0), vb=0.7)
    vol = N(nt, "ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (0.45, 0.43, 0.43, 1)
    L(nt, dens, vol.inputs["Density"])
    # glow from the fire inside it (object colour's red = how hot this puff is)
    sc_ = N(nt, "ShaderNodeSeparateColor")
    L(nt, oi.outputs["Color"], sc_.inputs[0])
    vol.inputs["Emission Color"].default_value = (*HEAT, 1)
    L(nt, mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", dens, sc_.outputs[0]), vb=2.0), vol.inputs["Emission Strength"])
    L(nt, vol.outputs[0], out.inputs["Volume"])
    return m


def smoke_puffs(foot, n, height):
    """the column: billows climbing from the foot, growing and drifting downwind as they rise"""
    m = puff_mat()
    for i in range(n):
        t = i / (n - 1)
        r = 3.0 + 16 * t ** 1.1
        p = foot + Vector((14 * t ** 1.8 + rs.uniform(-0.3, 0.3) * r, 5 * t ** 2 + rs.uniform(-0.3, 0.3) * r, height * t ** 1.1))
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        o = obj("puff%d" % i, bm, m)
        o.location = p
        o.scale = (r, r, r * rs.uniform(0.75, 1.0))
        o.rotation_euler = (rs.uniform(0, 6), rs.uniform(0, 6), rs.uniform(0, 6))
        o.color = (0.0, 0, 0, 1)


def bloom():
    try:
        ng = bpy.data.node_groups.new("comp", "CompositorNodeTree")
        sc.compositing_node_group = ng
        rl = ng.nodes.new("CompositorNodeRLayers")
        gl = ng.nodes.new("CompositorNodeGlare")
        gl.inputs["Type"].default_value = "Bloom"
        gl.inputs["Quality"].default_value = "High"
        gl.inputs["Threshold"].default_value = 1.0
        gl.inputs["Strength"].default_value = 0.5
        gl.inputs["Size"].default_value = 0.7
        ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        go = ng.nodes.new("NodeGroupOutput")
        ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
        ng.links.new(gl.outputs["Image"], go.inputs[0])
        sc.render.use_compositing = True
    except Exception as ex:
        print("COMP FAIL", ex)


# ================================================================ the crater
if SHOT == "crater":
    floor = base_h(0, 0) - 5.5
    s = shard(Vector((0.5, 0.5, floor + 0.6)), (math.radians(26), math.radians(-8), math.radians(-35)), scale=1.4)
    point("shard_in", Vector((4.5, 5.5, floor + 6)), GATE, 3500, 2.5)
    point("shard_foot", Vector((0.5, 0.5, floor + 1.4)), HEAT, 6000, 2.0)
    point("shard_top", Vector((-3, 4, floor + 11)), GATE_HOT, 2500, 1.5)
    for i in range(5):
        a = i / 5 * math.tau
        point("crack%d" % i, Vector((math.cos(a) * 6, math.sin(a) * 6, floor + 3.2)), HEAT, 700, 1.5)
    # rock thrown out over the grass: scorched blocks, some landed turned, a few still glowing
    bm_e, bm_g = bmesh.new(), bmesh.new()
    for i in range(140):
        a = rs.uniform(0, math.tau)
        rr = CR + 2 + abs(rs.gauss(0, CR * 0.55))
        x, y = math.cos(a) * rr, math.sin(a) * rr
        gz = hmap.get((int(math.floor(x)), int(math.floor(y))), BASE)
        sz = rs.choice((1.0, 1.0, 0.75, 0.5))
        tbox(bm_g if rs.random() < 0.07 else bm_e, (x, y, gz + sz * 0.35),
             sz, Euler((rs.uniform(-0.5, 0.5), rs.uniform(-0.5, 0.5), rs.uniform(0, 6))))
    obj("ejecta", bm_e, pix("ejecta", (0.03, 0.026, 0.025), (0.09, 0.075, 0.065), soot=0.4))
    obj("ejecta_hot", bm_g, M_CRUST)
    # small shards thrown off on impact, stuck in the ground round the rim
    for i in range(7):
        a = rs.uniform(0, math.tau)
        rr = rs.uniform(CR - 2, CR + 7)
        x, y = math.cos(a) * rr, math.sin(a) * rr
        gz = hmap.get((int(math.floor(x)), int(math.floor(y))), BASE)
        bm = bmesh.new()
        ax = Vector((math.cos(a), math.sin(a), 1.4))
        crystal(bm, Vector((0, 0, 0)), ax, rs.uniform(1.6, 3.2), rs.uniform(0.35, 0.6))
        o = obj("chip%d" % i, bm, crystal_mat("chip%d" % i, heat_at_foot=False))
        o.location = (x, y, gz - 0.3)
    # the smoke column off the shard, and low smoke curling out of the cracks
    smoke_puffs(Vector((0.5, 0.5, floor + 2)), 34, 70.0)
    vol_cube("smoke_low", smoke_mat("smoke_low", 0.3, HEAT, 0.4), (0.5, 0.5, floor + 3), (14, 14, 4))
    # the party come to see it, for scale: three figures at the rim
    M_FIG = pix("figure", (0.05, 0.05, 0.06), (0.09, 0.08, 0.09))
    bm_f = bmesh.new()
    for fx, fy in ((-9.5, -9.0), (-11.5, -6.5), (-7.0, -11.6)):
        gz = hmap[(int(math.floor(fx)), int(math.floor(fy)))]
        box(bm_f, fx - 0.3, fy - 0.15, gz, fx + 0.3, fy + 0.15, gz + 1.4)
        box(bm_f, fx - 0.25, fy - 0.25, gz + 1.4, fx + 0.25, fy + 0.25, gz + 1.9)
    obj("party", bm_f, M_FIG)
    CAM = ((-24.0, -27.0, floor + 15.0), (2.0, 3.0, floor + 8.0), 20)

# ================================================================ the fall
if SHOT == "fall":
    sc.view_settings.exposure = 0.2
    HEAD = Vector((-24, 230, 128))
    DIR = Vector((0.42, -0.08, -0.55)).normalized()           # where it is heading
    TAIL_LEN = 520
    # the burning trail: a long volume behind the head, white-hot at the front, going to smoke behind
    m, nt, out = new_mat("trail")
    tc = N(nt, "ShaderNodeTexCoord")
    sp = N(nt, "ShaderNodeSeparateXYZ")
    L(nt, tc.outputs["Object"], sp.inputs[0])
    t = mth(nt, "MULTIPLY", mth(nt, "ADD", sp.outputs["Z"], vb=1.0), vb=0.5)          # 0 tail .. 1 head
    r = mth(nt, "SQRT", mth(nt, "ADD", mth(nt, "MULTIPLY", sp.outputs["X"], sp.outputs["X"]), mth(nt, "MULTIPLY", sp.outputs["Y"], sp.outputs["Y"])))
    st = N(nt, "ShaderNodeVectorMath", _operation="MULTIPLY")
    st.inputs[1].default_value = (1.0, 1.0, 9.0)
    L(nt, tc.outputs["Object"], st.inputs[0])
    nz = N(nt, "ShaderNodeTexNoise", Scale=2.2, Detail=7.0, Roughness=0.62, Distortion=0.9)
    L(nt, st.outputs[0], nz.inputs["Vector"])
    allow = mth(nt, "ADD", mth(nt, "MULTIPLY", mth(nt, "POWER", mth(nt, "SUBTRACT", va=1.0, b=t), vb=0.6), vb=0.9), vb=0.04)
    edge = mth(nt, "SUBTRACT", allow, mth(nt, "SUBTRACT", r, mth(nt, "MULTIPLY", nz.outputs["Fac"], vb=0.35)))
    inside = mth(nt, "MINIMUM", mth(nt, "MAXIMUM", mth(nt, "MULTIPLY", edge, vb=6.0), vb=0.0), vb=1.0)
    hot = mth(nt, "POWER", t, vb=16.0)
    vol = N(nt, "ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (0.1, 0.09, 0.09, 1)
    smoke = mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", inside, mth(nt, "SUBTRACT", va=1.0, b=mth(nt, "POWER", t, vb=2.0))), mth(nt, "MULTIPLY", nz.outputs["Fac"], vb=0.12))
    tailfade = mth(nt, "MINIMUM", mth(nt, "MULTIPLY", t, vb=5.0), vb=1.0)
    L(nt, mth(nt, "MULTIPLY", smoke, tailfade), vol.inputs["Density"])
    L(nt, ramp(nt, hot, [(0.0, (0.5, 0.06, 0.01)), (0.4, HEAT), (0.8, HEAT_HOT), (1.0, (1, 0.95, 0.85))]), vol.inputs["Emission Color"])
    L(nt, mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", inside, hot), vb=55.0), vol.inputs["Emission Strength"])
    L(nt, vol.outputs[0], out.inputs["Volume"])
    tr = vol_cube("trail", m, HEAD - DIR * (TAIL_LEN / 2), (7, 7, TAIL_LEN / 2), DIR.to_track_quat("Z", "Y").to_euler())
    # the fireball at the head, the crystal inside it, its light on the land
    m, nt, out = new_mat("fireball")
    tc = N(nt, "ShaderNodeTexCoord")
    nz = N(nt, "ShaderNodeTexNoise", Scale=3.0, Detail=5.0, Distortion=0.6)
    L(nt, tc.outputs["Object"], nz.inputs["Vector"])
    vm = N(nt, "ShaderNodeVectorMath", _operation="LENGTH")
    L(nt, tc.outputs["Object"], vm.inputs[0])
    core = mth(nt, "MAXIMUM", mth(nt, "SUBTRACT", va=1.0, b=mth(nt, "ADD", vm.outputs["Value"], mth(nt, "MULTIPLY", nz.outputs["Fac"], vb=0.45))), vb=0.0)
    vol = N(nt, "ShaderNodeVolumePrincipled", Density=0.0)
    L(nt, ramp(nt, core, [(0.0, HEAT), (0.5, HEAT_HOT), (1.0, (1, 0.97, 0.9))]), vol.inputs["Emission Color"])
    L(nt, mth(nt, "MULTIPLY", mth(nt, "POWER", core, vb=1.5), vb=90.0), vol.inputs["Emission Strength"])
    L(nt, vol.outputs[0], out.inputs["Volume"])
    fb = bmesh.new()
    bmesh.ops.create_icosphere(fb, subdivisions=3, radius=1.0)
    o = obj("fireball", fb, m)
    o.location = HEAD
    o.scale = (12, 12, 12)
    shard(HEAD, (0.0, 0.0, 0.0), scale=0.45, crust=True)
    point("head", HEAD, HEAT_HOT, 1.4e6, 6)
    point("trail_glow", HEAD - DIR * 30, HEAT, 1.5e5, 10)
    # pieces breaking off, each with its own short trail
    for i in range(6):
        p = HEAD - DIR * rs.uniform(25, 110) + Vector((rs.uniform(-14, 14), rs.uniform(-14, 14), rs.uniform(-10, 10)))
        d2 = (DIR + Vector((rs.uniform(-0.15, 0.15), rs.uniform(-0.15, 0.15), rs.uniform(-0.1, 0.1)))).normalized()
        ln = rs.uniform(18, 46)
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.0, radius2=0.7, depth=ln)
        o = obj("bit%d" % i, bm, glow("bit%d" % i, HEAT_HOT, 25.0))
        o.location = p - d2 * ln / 2
        o.rotation_euler = d2.to_track_quat("Z", "Y").to_euler()
    # the smoke it leaves: billows along the path, thin and fire-lit at the head, fat and grey far back
    pm = puff_mat()
    n = 120
    for i in range(n):
        d = (i / (n - 1)) ** 1.3 * TAIL_LEN
        r = (4 + 26 * (d / TAIL_LEN) ** 0.8) * rs.uniform(0.6, 1.2)
        p = HEAD - DIR * (d + 8) + Vector((rs.uniform(-1, 1), rs.uniform(-1, 1), rs.uniform(-1, 1))) * r * 0.55
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        o = obj("tpuff%d" % i, bm, pm)
        o.location = p
        o.scale = (r, r, r * 0.85)
        o.rotation_euler = (rs.uniform(0, 6), rs.uniform(0, 6), rs.uniform(0, 6))
        o.color = (10 * math.exp(-d / 22), 0, 0, 1)
    # sparks shed round the head
    bm = bmesh.new()
    for i in range(160):
        p = HEAD - DIR * abs(rs.gauss(0, 50)) + Vector((rs.gauss(0, 1), rs.gauss(0, 1), rs.gauss(0, 1))) * 10
        d2 = -DIR + Vector((rs.uniform(-0.25, 0.25), rs.uniform(-0.25, 0.25), rs.uniform(-0.25, 0.25)))
        ln = rs.uniform(1.5, 6)
        q = d2.normalized().to_track_quat("Z", "Y")
        a, b2, c = (q @ Vector(v) + p for v in ((-0.15, 0, 0), (0.15, 0, 0), (0, 0, ln)))
        bm.faces.new([bm.verts.new(a), bm.verts.new(b2), bm.verts.new(c)])
    obj("sparks", bm, glow("spark", HEAT_HOT, 30.0))
    CAM = ((4.0, -72.0, hmap.get((4, -70), BASE) + 3.5), (-10.0, 200.0, 120.0), 18)

# ---------------------------------------------------------------- haze: depth over the land, a little blue
m, nt, out = new_mat("haze")
vol = N(nt, "ShaderNodeVolumePrincipled", Density=0.006 if SHOT == "crater" else 0.0025, Anisotropy=0.4)
vol.inputs["Color"].default_value = (0.55, 0.6, 0.75, 1)
L(nt, vol.outputs[0], out.inputs["Volume"])
if SHOT == "crater":
    vol_cube("haze", m, (0, 60, BASE + 40), (700, 700, 45))

# ---------------------------------------------------------------- camera, bloom, render
loc, aim, lens = CAM
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 4000
cam.location = loc
cam.data.lens = lens
cam.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
bloom()
sc.render.image_settings.color_depth = "8"
sc.render.filepath = os.path.abspath(os.path.join(OUT, "meteor_%s%s.png" % (SHOT, "_fast" if FAST else "")))
bpy.ops.render.render(write_still=True)
print("WROTE", sc.render.filepath)
