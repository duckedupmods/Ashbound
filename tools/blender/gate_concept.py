"""Gate concept render: a tear in the world ringed by black crystal shards erupting from scorched ground, a swirling
vortex surface (tunnel depth, white-hot rim, black core from S up), torn earth floating round it, a beam to the sky.
1 unit = 1 block. Background render:
  blender -b -P tools/blender/gate_concept.py -- <rank> [shot]
Writes tools/renders/gate/gate_<rank>_<shot>.png"""
import bpy, bmesh, math, random, sys, os
from mathutils import Vector, Matrix

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RANK = ARGS[0] if ARGS else "S"
SHOT = ARGS[1] if len(ARGS) > 1 else "hero"
RANKS = ["F", "E", "D", "C", "B", "A", "S", "SS", "SSS"]
COLOUR = [0xCDD2DC, 0x46E678, 0x3C8CFF, 0xA55AFF, 0xFFA01E, 0xFF2D2D, 0xFF1E1E, 0xBE46FF, 0xFFECBE]
RI = RANKS.index(RANK)
DARK = RI >= 6
OUT = os.path.join(os.path.dirname(__file__), "..", "renders", "gate")

RX, RZ, C = 2.8, 4.4, 5.0  # opening half-width, half-height, centre height


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(hexv):
    return tuple(lin(((hexv >> s) & 255) / 255) for s in (16, 8, 0))


COL = rgb(COLOUR[RI])
RIM = rgb({6: 0xFF2A10, 7: 0xC050FF, 8: 0xFFF4DC}.get(RI, COLOUR[RI]))

# ---------------------------------------------------------------- scene
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1600, 900
sc.eevee.taa_render_samples = 64
for k, v in (("use_raytracing", True), ("volumetric_tile_size", "4"), ("volumetric_samples", 96),
             ("volumetric_end", 120.0), ("use_shadows", True)):
    try:
        setattr(sc.eevee, k, v)
    except Exception as e:
        print("eevee", k, e)
try:
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
except Exception as e:
    print("cm", e)
sc.view_settings.exposure = -0.6


def nodes_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    return m, nt, out


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


def math_n(nt, op, a=None, b=None, va=0.0, vb=0.0, clamp=False):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    n.use_clamp = clamp
    n.inputs[0].default_value = va
    n.inputs[1].default_value = vb
    if a is not None:
        L(nt, a, n.inputs[0])
    if b is not None:
        L(nt, b, n.inputs[1])
    return n.outputs[0]


def mesh_obj(name, bm, mat=None, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = smooth
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    if mat:
        me.materials.append(mat)
    return ob


# ---------------------------------------------------------------- world: dusk sky + thin glowing haze
w = bpy.data.worlds.new("w")
sc.world = w
w.use_nodes = True
wt = w.node_tree
for n in list(wt.nodes):
    wt.nodes.remove(n)
wo = wt.nodes.new("ShaderNodeOutputWorld")
tc = wt.nodes.new("ShaderNodeTexCoord")
sep = wt.nodes.new("ShaderNodeSeparateXYZ")
L(wt, tc.outputs["Generated"], sep.inputs[0])
ramp = wt.nodes.new("ShaderNodeValToRGB")
L(wt, sep.outputs["Z"], ramp.inputs[0])
el = ramp.color_ramp.elements
sky_lo = (0.32, 0.03, 0.03, 1) if RI == 8 else (0.45, 0.25, 0.22, 1)
sky_hi = (0.06, 0.0, 0.01, 1) if RI == 8 else (0.05, 0.07, 0.16, 1)
el[0].position, el[0].color = 0.5, sky_lo
el[1].position, el[1].color = 0.62, sky_hi
bg = wt.nodes.new("ShaderNodeBackground")
bg.inputs["Strength"].default_value = 1.0
L(wt, ramp.outputs["Color"], bg.inputs["Color"])
L(wt, bg.outputs[0], wo.inputs["Surface"])
vol = wt.nodes.new("ShaderNodeVolumePrincipled")
vol.inputs["Density"].default_value = 0.0035
vol.inputs["Anisotropy"].default_value = 0.35
L(wt, vol.outputs[0], wo.inputs["Volume"])

sun = bpy.data.objects.new("moon", bpy.data.lights.new("moon", "SUN"))
sun.data.energy = 5.0
sun.data.color = (0.55, 0.65, 1.0)
sun.rotation_euler = (math.radians(55), 0, math.radians(150))
sc.collection.objects.link(sun)


def point(name, loc, col, power, radius=1.0, vol=1.0):
    li = bpy.data.lights.new(name, "POINT")
    li.energy = power
    li.color = col
    li.shadow_soft_size = radius
    try:
        li.volume_factor = vol
    except Exception:
        pass
    ob = bpy.data.objects.new(name, li)
    ob.location = loc
    sc.collection.objects.link(ob)


lc = tuple(min(1, c * 1.0) for c in (RIM if DARK else COL))
point("gate_core", (0, -0.6, C), lc, 2500, 2.5, 0.4)
point("gate_l", (-RX - 0.5, -1.0, C - 1), lc, 900, 0.6, 0.3)
point("gate_r", (RX + 0.5, -1.0, C - 1), lc, 900, 0.6, 0.3)
point("gate_foot", (0, -2.0, 1.2), lc, 1200, 1.5, 0.3)
point("gate_back", (0, 3.0, C), lc, 1500, 2.0, 0.3)

# ---------------------------------------------------------------- shared shader bits
rnd = random.Random(7 + RI)


def grass_mat(scorched):
    """Voxel grass block look from object coords: green top, dirt sides with a grass fringe, 16-px noise;
    near the gate it chars black with cracks glowing in the gate's colour."""
    m, nt, out = nodes_mat("grass_scorch" if scorched else "grass")
    tc = N(nt, "ShaderNodeTexCoord")
    snap = N(nt, "ShaderNodeVectorMath", _operation="SNAP")
    snap.inputs[1].default_value = (1 / 16, 1 / 16, 1 / 16)
    L(nt, tc.outputs["Object"], snap.inputs[0])
    px = N(nt, "ShaderNodeTexWhiteNoise", _noise_dimensions="3D")
    L(nt, snap.outputs[0], px.inputs["Vector"])
    nz = N(nt, "ShaderNodeSeparateXYZ")
    L(nt, tc.outputs["Normal"], nz.inputs[0])
    top = math_n(nt, "GREATER_THAN", nz.outputs["Z"], vb=0.5)
    pz = N(nt, "ShaderNodeSeparateXYZ")
    L(nt, snap.outputs[0], pz.inputs[0])
    fr = math_n(nt, "FRACT", pz.outputs["Z"])
    fringe = math_n(nt, "GREATER_THAN", fr, vb=0.76)
    jag = math_n(nt, "MULTIPLY", px.outputs["Value"], vb=0.18)
    fringe2 = math_n(nt, "GREATER_THAN", math_n(nt, "ADD", fr, jag), vb=0.84)
    green = math_n(nt, "MAXIMUM", top, math_n(nt, "MAXIMUM", fringe, fringe2))
    gcol = N(nt, "ShaderNodeMix", _data_type="RGBA")
    gcol.inputs[6].default_value = (0.055, 0.16, 0.03, 1)
    gcol.inputs[7].default_value = (0.11, 0.30, 0.05, 1)
    L(nt, px.outputs["Value"], gcol.inputs[0])
    dcol = N(nt, "ShaderNodeMix", _data_type="RGBA")
    dcol.inputs[6].default_value = (0.11, 0.06, 0.03, 1)
    dcol.inputs[7].default_value = (0.21, 0.12, 0.065, 1)
    L(nt, px.outputs["Value"], dcol.inputs[0])
    base = N(nt, "ShaderNodeMix", _data_type="RGBA")
    L(nt, green, base.inputs[0])
    L(nt, dcol.outputs[2], base.inputs[6])
    L(nt, gcol.outputs[2], base.inputs[7])
    bsdf = N(nt, "ShaderNodeBsdfPrincipled", Roughness=0.92)
    colour_out = base.outputs[2]
    if scorched:
        geo = N(nt, "ShaderNodeNewGeometry")
        ps = N(nt, "ShaderNodeSeparateXYZ")
        L(nt, geo.outputs["Position"], ps.inputs[0])
        d = math_n(nt, "SQRT", math_n(nt, "ADD", math_n(nt, "MULTIPLY", ps.outputs["X"], ps.outputs["X"]),
                                       math_n(nt, "MULTIPLY", ps.outputs["Y"], ps.outputs["Y"])))
        n2 = N(nt, "ShaderNodeTexNoise", Scale=0.35, Detail=4.0)
        L(nt, geo.outputs["Position"], n2.inputs["Vector"])
        dd = math_n(nt, "ADD", d, math_n(nt, "MULTIPLY", n2.outputs["Fac"], vb=5.0))
        burn = N(nt, "ShaderNodeMapRange", **{"From Min": 10.0, "From Max": 5.5})
        L(nt, dd, burn.inputs["Value"])
        char = N(nt, "ShaderNodeMix", _data_type="RGBA")
        char.inputs[6].default_value = (0.012, 0.010, 0.010, 1)
        char.inputs[7].default_value = (0.035, 0.028, 0.026, 1)
        L(nt, px.outputs["Value"], char.inputs[0])
        mixc = N(nt, "ShaderNodeMix", _data_type="RGBA")
        L(nt, burn.outputs[0], mixc.inputs[0])
        L(nt, base.outputs[2], mixc.inputs[6])
        L(nt, char.outputs[2], mixc.inputs[7])
        colour_out = mixc.outputs[2]
        # cracks: voronoi edges, pixel-snapped, fading out with distance
        vor = N(nt, "ShaderNodeTexVoronoi", _feature="DISTANCE_TO_EDGE", Scale=0.55, Randomness=1.0)
        L(nt, snap.outputs[0], vor.inputs["Vector"])
        line = N(nt, "ShaderNodeMapRange", **{"From Min": 0.05, "From Max": 0.0})
        L(nt, vor.outputs["Distance"], line.inputs["Value"])
        reach = N(nt, "ShaderNodeMapRange", **{"From Min": 9.0, "From Max": 2.5})
        L(nt, dd, reach.inputs["Value"])
        glow = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", line.outputs[0], reach.outputs[0]), top)
        L(nt, glow, bsdf.inputs["Emission Strength"])
        bsdf.inputs["Emission Color"].default_value = (*[c * 14 for c in (RIM if DARK else COL)], 1)
    L(nt, colour_out, bsdf.inputs["Base Color"])
    L(nt, bsdf.outputs[0], out.inputs["Surface"])
    return m


def leaves_mat():
    m, nt, out = nodes_mat("leaves")
    tc = N(nt, "ShaderNodeTexCoord")
    snap = N(nt, "ShaderNodeVectorMath", _operation="SNAP")
    snap.inputs[1].default_value = (1 / 8, 1 / 8, 1 / 8)
    L(nt, tc.outputs["Object"], snap.inputs[0])
    px = N(nt, "ShaderNodeTexWhiteNoise", _noise_dimensions="3D")
    L(nt, snap.outputs[0], px.inputs["Vector"])
    c = N(nt, "ShaderNodeMix", _data_type="RGBA")
    c.inputs[6].default_value = (0.012, 0.05, 0.012, 1)
    c.inputs[7].default_value = (0.04, 0.13, 0.03, 1)
    L(nt, px.outputs["Value"], c.inputs[0])
    b = N(nt, "ShaderNodeBsdfPrincipled", Roughness=0.8)
    L(nt, c.outputs[2], b.inputs["Base Color"])
    L(nt, b.outputs[0], out.inputs["Surface"])
    return m


def flat_mat(name, col, rough=0.8, emit=None, strength=0.0):
    m, nt, out = nodes_mat(name)
    b = N(nt, "ShaderNodeBsdfPrincipled", Roughness=rough)
    b.inputs["Base Color"].default_value = (*col, 1)
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    L(nt, b.outputs[0], out.inputs["Surface"])
    return m


def obsidian_mat():
    """Black glassy crystal; glows in the rank colour where it meets the tear ('glow' attribute), with veins."""
    m, nt, out = nodes_mat("obsidian")
    at = N(nt, "ShaderNodeAttribute", _attribute_name="glow")
    g2 = math_n(nt, "POWER", at.outputs["Fac"], vb=9.0)
    geo = N(nt, "ShaderNodeNewGeometry")
    wv = N(nt, "ShaderNodeTexWave", Scale=1.3, Distortion=9.0, Detail=6.0)
    L(nt, geo.outputs["Position"], wv.inputs["Vector"])
    vein = N(nt, "ShaderNodeMapRange", **{"From Min": 0.12, "From Max": 0.0})
    L(nt, wv.outputs["Fac"], vein.inputs["Value"])
    veins = math_n(nt, "MULTIPLY", vein.outputs[0], math_n(nt, "ADD", at.outputs["Fac"], vb=0.15))
    strength = math_n(nt, "ADD", math_n(nt, "MULTIPLY", g2, vb=14.0), math_n(nt, "MULTIPLY", veins, vb=0.0))
    b = N(nt, "ShaderNodeBsdfPrincipled", Roughness=0.06)
    b.inputs["Base Color"].default_value = (0.004, 0.003, 0.006, 1)
    b.inputs["Specular IOR Level"].default_value = 0.9
    b.inputs["Coat Weight"].default_value = 0.6
    b.inputs["Coat Roughness"].default_value = 0.05
    b.inputs["Emission Color"].default_value = (*(RIM if DARK else COL), 1)
    L(nt, strength, b.inputs["Emission Strength"])
    L(nt, b.outputs[0], out.inputs["Surface"])
    return m


def vortex_mat():
    """The tear itself, in unit-disc object coords (x, z in -1..1): spiral noise pulled into a tunnel, rings
    receding inward, white-hot rim. Light ranks blaze from the middle; dark ranks are black at the heart."""
    m, nt, out = nodes_mat("vortex")
    tc = N(nt, "ShaderNodeTexCoord")
    s = N(nt, "ShaderNodeSeparateXYZ")
    L(nt, tc.outputs["Object"], s.inputs[0])
    r = math_n(nt, "SQRT", math_n(nt, "ADD", math_n(nt, "MULTIPLY", s.outputs["X"], s.outputs["X"]),
                                   math_n(nt, "MULTIPLY", s.outputs["Z"], s.outputs["Z"])))
    inv = math_n(nt, "SUBTRACT", None, r, va=1.0)
    twist = math_n(nt, "MULTIPLY", math_n(nt, "POWER", math_n(nt, "MAXIMUM", inv, vb=0.0), vb=1.6), vb=9.0)
    rot = N(nt, "ShaderNodeVectorRotate", _rotation_type="Y_AXIS")
    L(nt, tc.outputs["Object"], rot.inputs["Vector"])
    L(nt, twist, rot.inputs["Angle"])
    # tunnel: stretch coordinates toward the middle so the noise rushes inward
    depth = math_n(nt, "DIVIDE", None, math_n(nt, "ADD", math_n(nt, "POWER", r, vb=0.8), vb=0.12), va=1.6)
    sc_v = N(nt, "ShaderNodeVectorMath", _operation="SCALE")
    L(nt, rot.outputs[0], sc_v.inputs[0])
    L(nt, depth, sc_v.inputs["Scale"])
    nz = N(nt, "ShaderNodeTexNoise", Scale=1.6, Detail=12.0, Roughness=0.62, Distortion=0.8)
    L(nt, sc_v.outputs[0], nz.inputs["Vector"])
    streak = N(nt, "ShaderNodeMapRange", **{"From Min": 0.48, "From Max": 0.78})
    L(nt, nz.outputs["Fac"], streak.inputs["Value"])
    sharp = math_n(nt, "POWER", streak.outputs[0], vb=2.0)
    rings = math_n(nt, "SINE", math_n(nt, "MULTIPLY", math_n(nt, "LOGARITHM", math_n(nt, "ADD", r, vb=0.02), vb=2.718),
                                      vb=14.0))
    rings = math_n(nt, "MULTIPLY", math_n(nt, "ADD", rings, vb=1.0), vb=0.5)
    rim = math_n(nt, "POWER", math_n(nt, "MINIMUM", r, vb=1.0), vb=9.0)
    hot = math_n(nt, "POWER", math_n(nt, "MINIMUM", r, vb=1.0), vb=40.0)
    if DARK:
        core = N(nt, "ShaderNodeMapRange", **{"From Min": 0.32, "From Max": 0.95})  # black heart
    else:
        core = N(nt, "ShaderNodeMapRange", **{"From Min": 1.0, "From Max": 0.0, "To Min": 0.35, "To Max": 1.6})
    L(nt, r, core.inputs["Value"])
    body = math_n(nt, "MULTIPLY", math_n(nt, "ADD", math_n(nt, "MULTIPLY", sharp, vb=3.2),
                                         math_n(nt, "MULTIPLY", rings, vb=0.5)), core.outputs[0])
    col_a = N(nt, "ShaderNodeRGB")
    col_a.outputs[0].default_value = (*COL, 1)
    col_r = N(nt, "ShaderNodeRGB")
    col_r.outputs[0].default_value = (*RIM, 1)
    e1 = N(nt, "ShaderNodeVectorMath", _operation="SCALE")
    L(nt, col_a.outputs[0], e1.inputs[0])
    L(nt, math_n(nt, "MULTIPLY", body, vb=2.5), e1.inputs["Scale"])
    e2 = N(nt, "ShaderNodeVectorMath", _operation="SCALE")
    L(nt, col_r.outputs[0], e2.inputs[0])
    L(nt, math_n(nt, "MULTIPLY", rim, vb=14.0), e2.inputs["Scale"])
    e3 = N(nt, "ShaderNodeVectorMath", _operation="SCALE")
    e3.inputs[0].default_value = (1.0, 0.93, 0.85)
    L(nt, math_n(nt, "MULTIPLY", hot, vb=30.0), e3.inputs["Scale"])
    add = N(nt, "ShaderNodeVectorMath", _operation="ADD")
    L(nt, e1.outputs[0], add.inputs[0])
    L(nt, e2.outputs[0], add.inputs[1])
    add2 = N(nt, "ShaderNodeVectorMath", _operation="ADD")
    L(nt, add.outputs[0], add2.inputs[0])
    L(nt, e3.outputs[0], add2.inputs[1])
    em = N(nt, "ShaderNodeEmission", Strength=1.0)
    L(nt, add2.outputs[0], em.inputs["Color"])
    L(nt, em.outputs[0], out.inputs["Surface"])
    return m


def beam_mat():
    m, nt, out = nodes_mat("beam")
    m.surface_render_method = "BLENDED"
    lw = N(nt, "ShaderNodeLayerWeight", Blend=0.35)
    fac = math_n(nt, "POWER", math_n(nt, "SUBTRACT", None, lw.outputs["Facing"], va=1.0), vb=1.5)
    tc = N(nt, "ShaderNodeTexCoord")
    s = N(nt, "ShaderNodeSeparateXYZ")
    L(nt, tc.outputs["Generated"], s.inputs[0])
    fade = math_n(nt, "SUBTRACT", None, math_n(nt, "POWER", s.outputs["Z"], vb=0.7), va=1.0)
    k = math_n(nt, "MULTIPLY", fac, fade)
    em = N(nt, "ShaderNodeEmission")
    em.inputs["Color"].default_value = (*(RIM if DARK else COL), 1)
    L(nt, math_n(nt, "MULTIPLY", k, vb=9.0), em.inputs["Strength"])
    tr = N(nt, "ShaderNodeBsdfTransparent")
    add = N(nt, "ShaderNodeAddShader")
    L(nt, em.outputs[0], add.inputs[0])
    L(nt, tr.outputs[0], add.inputs[1])
    L(nt, add.outputs[0], out.inputs["Surface"])
    return m


# ---------------------------------------------------------------- ground: voxel terrain, cratered at the gate
def height(x, y):
    h = math.sin(x * 0.21) * 1.2 + math.cos(y * 0.17 + 1) * 1.0 + math.sin((x + y) * 0.09) * 1.5
    h = round(h * 0.6)
    d = math.hypot(x + 0.5, y + 0.5)
    return h


def cube_faces(bm, x, y, z0, z1, hmap):
    """Top face plus the side faces neighbours don't hide, from z0 to z1."""
    v = lambda a, b, c: bm.verts.new((a, b, c))
    top = [v(x, y, z1), v(x + 1, y, z1), v(x + 1, y + 1, z1), v(x, y + 1, z1)]
    bm.faces.new(top)
    for dx, dy, quad in ((1, 0, ((1, 0), (1, 1))), (-1, 0, ((0, 1), (0, 0))), (0, 1, ((1, 1), (0, 1))),
                         (0, -1, ((0, 0), (1, 0)))):
        nh = hmap.get((x + dx, y + dy), -99)
        if nh >= z1:
            continue
        lo = max(nh, z0)
        (ax, ay), (bx, by) = quad
        for zz in range(int(lo), int(z1)):
            bm.faces.new([v(x + ax, y + ay, zz), v(x + bx, y + by, zz), v(x + bx, y + by, zz + 1),
                          v(x + ax, y + ay, zz + 1)])


SPAN = 34
hmap = {(x, y): height(x, y) for x in range(-SPAN, SPAN) for y in range(-SPAN, SPAN + 20)}
bm_near, bm_far = bmesh.new(), bmesh.new()
for (x, y), h in hmap.items():
    cube_faces(bm_near if math.hypot(x, y) < 14 else bm_far, x, y, h - 3, h, hmap)
ground_near = mesh_obj("ground_near", bm_near, grass_mat(True))
ground_far = mesh_obj("ground_far", bm_far, grass_mat(False))
GROUND = hmap[(0, 0)]

# voxel trees for scale and place
bm_t, bm_l = bmesh.new(), bmesh.new()


def box(bm, x0, y0, z0, x1, y1, z1, glow=None, layer=None):
    vs = [bm.verts.new(p) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                    (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[i] for i in f])
    return vs


for tx, ty in ((-15, 9), (-19, 16), (13, 12), (18, 4), (-11, 22), (7, 25), (22, 19), (-24, 3), (-6, 30)):
    gz = hmap.get((tx, ty), 0)
    th = rnd.randint(5, 7)
    box(bm_t, tx, ty, gz, tx + 1, ty + 1, gz + th)
    for (a, b, lo, hi) in ((2, 2, th - 2, th), (1, 1, th, th + 2)):
        box(bm_l, tx - a, ty - b, gz + lo, tx + 1 + a, ty + 1 + b, gz + hi)
mesh_obj("trunks", bm_t, flat_mat("bark", (0.06, 0.035, 0.02), 0.9))
mesh_obj("leaves", bm_l, leaves_mat())

# ---------------------------------------------------------------- the tear's crystal ring
OBS = obsidian_mat()
bm_s = bmesh.new()
glow_l = bm_s.verts.layers.float.new("glow")


def shard(base, d, length, w, glow_base=1.0, glow_tip=0.0, sides=5):
    d = d.normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    a = d.cross(up).normalized()
    b = d.cross(a).normalized()
    tw = rnd.uniform(0, math.tau)
    r0, r1 = [], []
    k_mid = rnd.uniform(0.4, 0.62)
    for i in range(sides):
        t = tw + i / sides * math.tau + rnd.uniform(-0.3, 0.3)
        rr = w * rnd.uniform(0.7, 1.2)
        off = a * math.cos(t) + b * math.sin(t)
        r0.append(base - d * 0.5 * w + off * rr)
        r1.append(base + d * length * k_mid + off * rr * rnd.uniform(0.55, 0.85))
    tip = base + d * length + (a * rnd.uniform(-1, 1) + b * rnd.uniform(-1, 1)) * w * 0.25
    v0 = [bm_s.verts.new(p) for p in r0]
    v1 = [bm_s.verts.new(p) for p in r1]
    vt = bm_s.verts.new(tip)
    gm = glow_base * 0.35 + glow_tip * 0.65
    for v in v0:
        v[glow_l] = glow_base
    for v in v1:
        v[glow_l] = gm
    vt[glow_l] = glow_tip
    bm_s.faces.new(list(reversed(v0)))
    for i in range(sides):
        j = (i + 1) % sides
        bm_s.faces.new([v0[i], v0[j], v1[j], v1[i]])
        bm_s.faces.new([v1[i], v1[j], vt])


def on_rim(a, k=1.0):
    return Vector((RX * k * math.cos(a), 0, C + RZ * k * math.sin(a)))


def rim_normal(a):
    return Vector((math.cos(a) / RX, 0, math.sin(a) / RZ)).normalized()


# outer crown: big shards bursting outward from the edge, longest at the top and shoulders
for i in range(24):
    a = i / 24 * math.tau + rnd.uniform(-0.05, 0.05)
    s = math.sin(a)
    if s < -0.82:
        continue  # the foot is the ground's job
    n = rim_normal(a)
    d = (n + Vector((rnd.uniform(-0.35, 0.35), rnd.uniform(-0.55, 0.45), rnd.uniform(-0.25, 0.3)))).normalized()
    length = rnd.uniform(2.0, 3.6) * (1.0 + max(0, s) * 0.8)
    if rnd.random() < 0.18:
        length *= 1.7
    shard(on_rim(a, 1.02) + Vector((0, rnd.uniform(-0.4, 0.4), 0)), d, length, rnd.uniform(0.45, 0.8))
# second layer, behind, darker and longer: gives the crown depth
for i in range(12):
    a = rnd.uniform(-0.4, math.pi + 0.4)
    n = rim_normal(a)
    d = (n + Vector((rnd.uniform(-0.3, 0.3), rnd.uniform(0.2, 0.9), rnd.uniform(-0.1, 0.4)))).normalized()
    shard(on_rim(a, 1.08) + Vector((0, 0.5, 0)), d, rnd.uniform(2.5, 5.5), rnd.uniform(0.35, 0.7), 0.7, 0.0)
# teeth: short shards jutting into the opening, glowing all over, so the edge reads torn not drawn
for i in range(70):
    a = i / 70 * math.tau + rnd.uniform(-0.04, 0.04)
    n = rim_normal(a)
    d = (-n + Vector((rnd.uniform(-0.3, 0.3), rnd.uniform(-0.5, 0.2), rnd.uniform(-0.3, 0.3)))).normalized()
    shard(on_rim(a, 1.1), d, rnd.uniform(0.35, 1.0), rnd.uniform(0.1, 0.22), 1.0, 0.75, 4)
# ground eruption: crystals tearing out of the earth round the foot, leaning away
for i in range(30):
    a = rnd.uniform(0, math.tau)
    rr = rnd.uniform(2.2, 7.5)
    x, y = math.cos(a) * rr * 1.1, math.sin(a) * rr * 0.75
    gz = hmap.get((math.floor(x), math.floor(y)), GROUND) + 0.0
    out_d = Vector((math.cos(a), math.sin(a), 0))
    d = (Vector((0, 0, 1.0)) + out_d * rnd.uniform(0.3, 1.0)).normalized()
    big = max(0.0, 1 - rr / 8)
    shard(Vector((x, y, gz)), d, rnd.uniform(0.8, 2.0) + big * rnd.uniform(1.5, 4.5), rnd.uniform(0.2, 0.5) + big * 0.4,
          0.9 * big + 0.2, 0.0)
crystal = mesh_obj("crystal", bm_s, OBS)

# cracks in the air: reality splitting round the tear like struck glass, glowing jagged lines with branches
bm_c = bmesh.new()
CRK = flat_mat("crack", (0, 0, 0), 1.0, (1.0, 0.9, 0.85), 1.0)
CRK.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (*[min(1, c * 0.6 + 0.4) for c in (RIM if DARK else COL)], 1)
CRK.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 30.0


def crack_line(p, ang, length, wid, depth=0):
    steps = max(3, int(length / 0.35))
    for _ in range(steps):
        ang += rnd.uniform(-0.55, 0.55)
        q = p + Vector((math.cos(ang), 0, math.sin(ang))) * (length / steps)
        side = Vector((-math.sin(ang), 0, math.cos(ang))) * wid
        vs = [bm_c.verts.new(v) for v in (p - side, q - side * 0.85, q + side * 0.85, p + side)]
        bm_c.faces.new(vs)
        if depth < 2 and rnd.random() < 0.22:
            crack_line(q, ang + rnd.choice((-1, 1)) * rnd.uniform(0.5, 1.1), length * 0.45, wid * 0.6, depth + 1)
        p = q
        wid *= 0.88


for i in range(16):
    a = i / 16 * math.tau + rnd.uniform(-0.15, 0.15)
    if math.sin(a) < -0.75:
        continue
    start = on_rim(a, 1.05) + Vector((0, -0.25, 0))
    n = rim_normal(a)
    crack_line(start, math.atan2(n.z, n.x), rnd.uniform(2.5, 6.5), 0.07)
mesh_obj("air_cracks", bm_c, CRK)

# ---------------------------------------------------------------- the tear's face
bm_v = bmesh.new()
rings, seg = 48, 160
centre = bm_v.verts.new((0, 0, 0))
prev = None
for ri in range(1, rings + 1):
    rr = (ri / rings) ** 1.3
    ring = [bm_v.verts.new((rr * math.cos(t / seg * math.tau), 0, rr * math.sin(t / seg * math.tau))) for t in range(seg)]
    for t in range(seg):
        u = (t + 1) % seg
        if prev is None:
            bm_v.faces.new([centre, ring[u], ring[t]])
        else:
            bm_v.faces.new([prev[t], prev[u], ring[u], ring[t]])
    prev = ring
face = mesh_obj("vortex", bm_v, vortex_mat())
face.scale = (RX * 1.1, 1, RZ * 1.1)
face.location = (0, 0.15, C)

# ---------------------------------------------------------------- torn earth hanging in the air round it
G2 = grass_mat(False)
for i in range(22):
    a = rnd.uniform(0, math.tau)
    rr = rnd.uniform(3.6, 7.0)
    bm_d = bmesh.new()
    n = rnd.choice((1, 1, 1, 2, 3))
    for k in range(n):
        ox, oy = (k % 2), (k // 2)
        box(bm_d, ox, oy, 0, ox + 1, oy + 1, 1)
        box(bm_d, ox, oy, -1, ox + 1, oy + 1, 0) if rnd.random() < 0.4 else None
    ob = mesh_obj("rock%d" % i, bm_d, G2)
    ob.location = (math.cos(a) * rr, math.sin(a) * rr * 0.8, rnd.uniform(1.5, 11.0))
    ob.rotation_euler = (rnd.uniform(-0.7, 0.7), rnd.uniform(-0.7, 0.7), rnd.uniform(0, math.tau))
    sz = rnd.uniform(0.5, 1.0)
    ob.scale = (sz, sz, sz)

# sparks spiralling into the tear
EMB = flat_mat("ember", (0, 0, 0), 1.0, RIM if DARK else COL, 18.0)
WHITE = flat_mat("spark", (0, 0, 0), 1.0, (1, 0.95, 0.85), 25.0)
bm_p, bm_w = bmesh.new(), bmesh.new()
for i in range(220):
    t = rnd.random()
    a = rnd.uniform(0, math.tau)
    k = 1.15 + t * 2.2
    p = Vector((RX * k * math.cos(a + t * 2.5), rnd.uniform(-1.5, 0.3) * t, C + RZ * k * math.sin(a + t * 2.5)))
    s = rnd.uniform(0.02, 0.05)
    box(bm_w if rnd.random() < 0.25 else bm_p, p.x - s, p.y - s, p.z - s, p.x + s, p.y + s, p.z + s)
for i in range(90):  # embers drifting up off the scorch
    x, y = rnd.uniform(-8, 8), rnd.uniform(-6, 6)
    z = GROUND + rnd.uniform(0.2, 12) ** 1.0
    s = rnd.uniform(0.025, 0.06)
    box(bm_p, x - s, y - s, z - s, x + s, y + s, z + s)
mesh_obj("embers", bm_p, EMB)
mesh_obj("sparks", bm_w, WHITE)

# beam to the sky
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.18, depth=160, location=(0, 0.2, C + RZ + 80))
beam = bpy.context.object
beam.data.materials.append(beam_mat())
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.9, depth=160, location=(0, 0.2, C + RZ + 80))
halo = bpy.context.object
hm = beam_mat()
hm.node_tree.nodes["Emission"].inputs["Strength"].default_value = 3
halo.data.materials.append(hm)

# a player for scale: 2 blocks tall, looking at it
bm_h = bmesh.new()
px, py, pz = 1.6, -7.5, GROUND
box(bm_h, px - 0.25, py - 0.125, pz, px + 0.25, py + 0.125, pz + 0.75)  # legs
box(bm_h, px - 0.25, py - 0.125, pz + 0.75, px + 0.25, py + 0.125, pz + 1.5)  # body
box(bm_h, px - 0.5, py - 0.125, pz + 0.75, px - 0.25, py + 0.125, pz + 1.5)
box(bm_h, px + 0.25, py - 0.125, pz + 0.75, px + 0.5, py + 0.125, pz + 1.5)
box(bm_h, px - 0.25, py - 0.25, pz + 1.5, px + 0.25, py + 0.25, pz + 2.0)  # head
mesh_obj("player", bm_h, flat_mat("player", (0.05, 0.05, 0.06), 0.7))

# ---------------------------------------------------------------- camera
SHOTS = {
    "hero": ((-11.0, -25.0, 3.4), (0.5, 0, 6.0), 28),
    "close": ((-3.0, -8.5, 3.2), (0, 0, 5.4), 24),
    "wide": ((-20, -38, 9), (0, 0, 10), 30),
}
loc, aim, lens = SHOTS[SHOT]
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cam.location = loc
cam.data.lens = lens
cam.data.clip_end = 400
d = Vector(aim) - Vector(loc)
cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
sc.collection.objects.link(cam)
sc.camera = cam

# ---------------------------------------------------------------- bloom in the compositor
try:
    ng = bpy.data.node_groups.new("comp", "CompositorNodeTree")
    sc.compositing_node_group = ng
    rl = ng.nodes.new("CompositorNodeRLayers")
    gl = ng.nodes.new("CompositorNodeGlare")
    gl.inputs["Type"].default_value = "Bloom"
    gl.inputs["Quality"].default_value = "High"
    gl.inputs["Threshold"].default_value = 2.0
    gl.inputs["Strength"].default_value = 0.35
    gl.inputs["Size"].default_value = 0.85
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    go = ng.nodes.new("NodeGroupOutput")
    ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
    ng.links.new(gl.outputs["Image"], go.inputs[0])
    sc.render.use_compositing = True
except Exception as e:
    print("COMP FAIL", e)

os.makedirs(OUT, exist_ok=True)
sc.render.filepath = os.path.abspath(os.path.join(OUT, "gate_%s_%s.png" % (RANK, SHOT)))
bpy.ops.render.render(write_still=True)
print("WROTE", sc.render.filepath)
