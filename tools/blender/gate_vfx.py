"""Gate, movie-VFX pass (Cycles): churning volumetric plasma in a torn ellipse, white-hot rim, smoke rolling off it
and lit from inside, spark streaks, torn earth and rock hanging in the air, light spilling on scorched ground.
Reuses the ground, trees, sky and lights from gate_concept.py.
  blender -b -P tools/blender/gate_vfx.py -- <rank> [shot]   ->  tools/renders/gate/vfx_<rank>_<shot>.png"""
import os, sys, math, random
import bpy, bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "gate_concept.py"), encoding="utf-8").read()
exec(_src.split("# ---------------------------------------------------------------- the tear's crystal ring")[0])

rnd = random.Random(11 + RI)

PHASES = {
    "crack": dict(size=(0.035, 0.75), beam=(0, 0), debris=0.55, cracks=7, hot=1.6, smoke=0.12),
    "burst": dict(size=(0.55, 1.0), beam=(0, 0), debris=1.5, flash=1.3, wave=7.0, smoke=2.2),
    "rise": dict(size=(1.0, 1.0), beam=(0, 0.055), debris=1.15, head=True),
    "spin": dict(size=(0.95, 1.0), beam=(0, 1), debris=0.62, hot=1.5),
    "eye": dict(size=(0.12, 0.95), beam=(0.12, 1), debris=0.42, hot=2.5),
    "bang": dict(size=(0.02, 0.12), beam=(0.45, 1), debris=0.3, flash=2.0, wave=11.0, hot=3.0),
}
if SHOT in PHASES and "smoke" in PHASES[SHOT]:
    os.environ["GATE_SMOKE"] = str(PHASES[SHOT]["smoke"])
HOT = RIM if DARK else COL

# ---------------------------------------------------------------- Cycles on the GPU
sc.render.engine = "CYCLES"
cp = bpy.context.preferences.addons["cycles"].preferences
cp.compute_device_type = "OPTIX"
cp.get_devices()
for d in cp.devices:
    d.use = d.type == "OPTIX"
sc.cycles.device = "GPU"
FAST = "fast" in ARGS
sc.cycles.samples = 40 if FAST else 160
sc.cycles.use_denoising = True
sc.cycles.volume_bounces = 1
sc.cycles.max_bounces = 6
sc.cycles.volume_step_rate = 1.0
sc.render.resolution_x, sc.render.resolution_y = (1280, 720) if FAST else (1600, 900)
sc.view_settings.exposure = 0.0
sun.data.energy = 0.8
sun.data.color = (1.0, 0.62, 0.42)
sun.rotation_euler = (math.radians(80), 0, math.radians(200))
el[0].color = (0.9, 0.42, 0.25, 1) if RI != 8 else (0.5, 0.04, 0.03, 1)
el[1].color = (0.08, 0.12, 0.28, 1) if RI != 8 else (0.08, 0.0, 0.01, 1)
el[0].position, el[1].position = 0.5, 0.7
# the concept's haze is too thin for Cycles to matter, and too costly over the whole view: keep it local
_wt = sc.world.node_tree
_wt.links.remove(_wt.nodes["World Output"].inputs["Volume"].links[0])
# a real dusk sky: the sun just under the horizon behind the gate, blood red for the deadliest
_sky = _wt.nodes.new("ShaderNodeTexSky")
_sky.sky_type = "MULTIPLE_SCATTERING"
_sky.sun_elevation = math.radians(1.0)
_sky.sun_rotation = math.radians(15)
_sky.sun_disc = False
_bg = _wt.nodes["Background"]
_tint = _wt.nodes.new("ShaderNodeMix")
_tint.data_type = "RGBA"
_tint.blend_type = "MULTIPLY"
_tint.inputs[0].default_value = 1.0
_tint.inputs[7].default_value = (1.0, 0.18, 0.12, 1) if RI == 8 else (1, 1, 1, 1)
_wt.links.new(_sky.outputs[0], _tint.inputs[6])
_wt.links.new(_tint.outputs[2], _bg.inputs["Color"])
_bg.inputs["Strength"].default_value = 0.07
for ob in list(sc.objects):
    if ob.type == "LIGHT" and ob.name.startswith("gate_"):
        ob.data.energy *= 0.5


def vec_len_xz(nt, v):
    s = N(nt, "ShaderNodeSeparateXYZ")
    L(nt, v, s.inputs[0])
    return math_n(nt, "SQRT", math_n(nt, "ADD", math_n(nt, "MULTIPLY", s.outputs["X"], s.outputs["X"]),
                                      math_n(nt, "MULTIPLY", s.outputs["Z"], s.outputs["Z"]))), s


def smooth(nt, x, a, b):
    m = N(nt, "ShaderNodeMapRange", _interpolation_type="SMOOTHSTEP", **{"From Min": a, "From Max": b})
    L(nt, x, m.inputs["Value"])
    return m.outputs[0]


def scale_rgb(nt, rgb, k):
    v = N(nt, "ShaderNodeVectorMath", _operation="SCALE")
    v.inputs[0].default_value = rgb
    L(nt, k, v.inputs["Scale"])
    return v.outputs[0]


def add_v(nt, a, b):
    v = N(nt, "ShaderNodeVectorMath", _operation="ADD")
    L(nt, a, v.inputs[0])
    L(nt, b, v.inputs[1])
    return v.outputs[0]


# ---------------------------------------------------------------- the plasma: an elliptic slab of glowing volume
K = 1.35  # the domain reaches past the rim so flares can lick outward
def plasma_mat():
    m, nt, out = nodes_mat("plasma")
    tc = N(nt, "ShaderNodeTexCoord")
    p = tc.outputs["Object"]
    r, s = vec_len_xz(nt, p)
    ay = math_n(nt, "ABSOLUTE", s.outputs["Y"])
    rr = math_n(nt, "MULTIPLY", r, vb=K)  # 1.0 at the rim
    # swirl: rotate round the face's axis, harder toward the middle
    twist = math_n(nt, "MULTIPLY", math_n(nt, "POWER", math_n(nt, "MAXIMUM", math_n(nt, "SUBTRACT", None, rr, va=1.15),
                                                               vb=0.0), vb=1.4), vb=7.5)
    rot = N(nt, "ShaderNodeVectorRotate", _rotation_type="Y_AXIS")
    L(nt, p, rot.inputs["Vector"])
    L(nt, twist, rot.inputs["Angle"])
    big = N(nt, "ShaderNodeTexNoise", _noise_dimensions="4D", Scale=2.2, Detail=10.0, Roughness=0.6, Distortion=1.4,
            W=1.7 + RI)
    L(nt, rot.outputs[0], big.inputs["Vector"])
    fine = N(nt, "ShaderNodeTexNoise", _noise_dimensions="4D", Scale=11.0, Detail=12.0, Roughness=0.72, Distortion=0.9,
             W=3.1)
    L(nt, rot.outputs[0], fine.inputs["Vector"])
    turb = math_n(nt, "ADD", math_n(nt, "MULTIPLY", big.outputs["Fac"], vb=0.75), math_n(nt, "MULTIPLY", fine.outputs["Fac"], vb=0.35))
    ang = math_n(nt, "ARCTAN2", s.outputs["Z"], s.outputs["X"])
    polar = N(nt, "ShaderNodeCombineXYZ")
    L(nt, math_n(nt, "MULTIPLY", math_n(nt, "SINE", ang), vb=2.0), polar.inputs["X"])
    L(nt, math_n(nt, "MULTIPLY", math_n(nt, "COSINE", ang), vb=2.0), polar.inputs["Y"])
    L(nt, math_n(nt, "MULTIPLY", rr, vb=0.9), polar.inputs["Z"])
    tn = N(nt, "ShaderNodeTexNoise", _noise_dimensions="4D", Scale=5.5, Detail=12.0, Roughness=0.68, Distortion=1.6, W=5.0)
    L(nt, polar.outputs[0], tn.inputs["Vector"])
    tongue = smooth(nt, math_n(nt, "ADD", tn.outputs["Fac"], math_n(nt, "MULTIPLY", fine.outputs["Fac"], vb=0.25)), 0.6, 0.7)
    # the rim: a ragged band of white-hot plasma round r = 1, frayed by the noise
    rim_d = math_n(nt, "ABSOLUTE", math_n(nt, "SUBTRACT", math_n(nt, "ADD", rr, math_n(nt, "MULTIPLY", turb, vb=0.55)),
                                          vb=1.25))
    rim = math_n(nt, "POWER", smooth(nt, rim_d, 0.11, 0.0), vb=2.2)
    # flares: plasma licking out past the rim where the noise peaks
    flare = math_n(nt, "MULTIPLY", tongue, smooth(nt, rr, 1.33, 0.98))
    flare = math_n(nt, "MULTIPLY", flare, smooth(nt, rr, 0.9, 1.05))
    # the body inside: swirling filaments
    fil = smooth(nt, turb, 0.5, 0.78)
    inside = smooth(nt, rr, 1.08, 0.95)
    thin = smooth(nt, ay, 0.75, 0.05)  # slab thickness fade
    rimk = math_n(nt, "MULTIPLY", math_n(nt, "MAXIMUM", rim, flare), thin)
    body = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", fil, inside), thin)
    if DARK:
        heart = smooth(nt, rr, 0.5, 0.97)  # body fades to nothing at the black heart
        body = math_n(nt, "MULTIPLY", body, heart)
    hot_core = math_n(nt, "POWER", rimk, vb=3.0)
    em = add_v(nt, add_v(nt, scale_rgb(nt, HOT, math_n(nt, "MULTIPLY", rimk, vb=130.0)),
                         scale_rgb(nt, COL, math_n(nt, "MULTIPLY", body, vb=14.0 if not DARK else 9.0))),
               scale_rgb(nt, (1.0, 0.92, 0.82), math_n(nt, "MULTIPLY", hot_core, vb=130.0)))
    v = N(nt, "ShaderNodeVolumePrincipled")
    v.inputs["Color"].default_value = (0.02, 0.02, 0.02, 1)
    L(nt, math_n(nt, "MULTIPLY", math_n(nt, "ADD", rimk, body), vb=6.0), v.inputs["Density"])
    v.inputs["Emission Strength"].default_value = 1.0
    L(nt, em, v.inputs["Emission Color"])
    L(nt, v.outputs[0], out.inputs["Volume"])
    return m


def slab(name, rx, ry, rz, segs=96):
    bm = bmesh.new()
    top, bot = [], []
    for i in range(segs):
        t = i / segs * math.tau
        top.append(bm.verts.new((math.cos(t), 1, math.sin(t))))
        bot.append(bm.verts.new((math.cos(t), -1, math.sin(t))))
    bm.faces.new(top)
    bm.faces.new(list(reversed(bot)))
    for i in range(segs):
        j = (i + 1) % segs
        bm.faces.new([bot[i], bot[j], top[j], top[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = mesh_obj(name, bm)
    ob.scale = (rx, ry, rz)
    return ob


pl = slab("plasma", RX * K, 0.7, RZ * K)
pl.location = (0, 0, C)
pl.data.materials.append(plasma_mat())

# the far side of the tear: a tunnel of light for the low ranks, a starless black for the deadly ones
face = None
bm_v = bmesh.new()
centre = bm_v.verts.new((0, 0, 0))
prev = None
for ri in range(1, 41):
    rr = (ri / 40) ** 1.3
    ring = [bm_v.verts.new((rr * math.cos(t / 128 * math.tau), 0, rr * math.sin(t / 128 * math.tau))) for t in range(128)]
    for t in range(128):
        u = (t + 1) % 128
        bm_v.faces.new([centre, ring[u], ring[t]] if prev is None else [prev[t], prev[u], ring[u], ring[t]])
    prev = ring
m, nt, out = nodes_mat("abyss")
tc = N(nt, "ShaderNodeTexCoord")
r, s = vec_len_xz(nt, tc.outputs["Object"])
rot = N(nt, "ShaderNodeVectorRotate", _rotation_type="Y_AXIS")
L(nt, tc.outputs["Object"], rot.inputs["Vector"])
L(nt, math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", None, r, va=1.0), vb=6.0), rot.inputs["Angle"])
sv = N(nt, "ShaderNodeVectorMath", _operation="SCALE")
L(nt, rot.outputs[0], sv.inputs[0])
L(nt, math_n(nt, "DIVIDE", None, math_n(nt, "ADD", r, vb=0.1), va=1.0), sv.inputs["Scale"])
nz = N(nt, "ShaderNodeTexNoise", Scale=2.0, Detail=10.0, Distortion=0.6)
L(nt, sv.outputs[0], nz.inputs["Vector"])
streak = smooth(nt, nz.outputs["Fac"], 0.5, 0.8)
if DARK:
    k = math_n(nt, "MULTIPLY", streak, math_n(nt, "POWER", r, vb=3.0))
    k = math_n(nt, "MULTIPLY", k, vb=1.5)
else:
    k = math_n(nt, "ADD", math_n(nt, "MULTIPLY", streak, vb=2.0), math_n(nt, "MULTIPLY", smooth(nt, r, 0.6, 0.0), vb=6.0))
em = N(nt, "ShaderNodeEmission")
L(nt, scale_rgb(nt, COL, k), em.inputs["Color"])
L(nt, em.outputs[0], out.inputs["Surface"])
face = mesh_obj("abyss", bm_v, m)
face.scale = (RX * 1.08, 1, RZ * 1.08)
face.location = (0, 0.6, C)

# ---------------------------------------------------------------- smoke rolling off the rim, lit by it
SMOKE = float(os.environ.get("GATE_SMOKE", "0.45"))


def smoke_mat():
    m, nt, out = nodes_mat("smoke")
    tc = N(nt, "ShaderNodeTexCoord")
    geo = N(nt, "ShaderNodeNewGeometry")
    pw = geo.outputs["Position"]
    s = N(nt, "ShaderNodeSeparateXYZ")
    L(nt, pw, s.inputs[0])
    # distance to the rim ellipse (approx) in the face plane, and off it
    ex = math_n(nt, "DIVIDE", s.outputs["X"], vb=RX)
    ez = math_n(nt, "DIVIDE", math_n(nt, "SUBTRACT", s.outputs["Z"], vb=C), vb=RZ)
    er = math_n(nt, "SQRT", math_n(nt, "ADD", math_n(nt, "MULTIPLY", ex, ex), math_n(nt, "MULTIPLY", ez, ez)))
    drim = math_n(nt, "ABSOLUTE", math_n(nt, "SUBTRACT", er, vb=1.1))
    dy = math_n(nt, "ABSOLUTE", s.outputs["Y"])
    # warp the sample point upward over height so the smoke billows and rises
    warp = N(nt, "ShaderNodeTexNoise", Scale=0.35, Detail=3.0)
    L(nt, pw, warp.inputs["Vector"])
    wv = N(nt, "ShaderNodeVectorMath", _operation="ADD")
    L(nt, pw, wv.inputs[0])
    L(nt, warp.outputs["Color"], wv.inputs[1])
    n1 = N(nt, "ShaderNodeTexNoise", Scale=0.45, Detail=8.0, Roughness=0.62, Distortion=0.3)
    L(nt, wv.outputs[0], n1.inputs["Vector"])
    puffs = smooth(nt, n1.outputs["Fac"], 0.40, 0.62)
    plume = math_n(nt, "MULTIPLY", smooth(nt, math_n(nt, "ADD", math_n(nt, "ABSOLUTE", ex), math_n(nt, "MULTIPLY", dy, vb=0.3)), 1.6, 0.3), smooth(nt, ez, 0.7, 1.6))
    near_rim = math_n(nt, "MAXIMUM", smooth(nt, math_n(nt, "ADD", math_n(nt, "MULTIPLY", drim, vb=1.6), math_n(nt, "MULTIPLY", dy, vb=0.4)), 2.2, 0.15), plume)
    # a ground-hugging pool round the foot
    hz = math_n(nt, "SUBTRACT", s.outputs["Z"], vb=GROUND)
    rad = math_n(nt, "SQRT", math_n(nt, "ADD", math_n(nt, "MULTIPLY", s.outputs["X"], s.outputs["X"]),
                                     math_n(nt, "MULTIPLY", s.outputs["Y"], s.outputs["Y"])))
    pool = math_n(nt, "MULTIPLY", smooth(nt, hz, 2.2, 0.0), smooth(nt, rad, 11.0, 3.0))
    dens = math_n(nt, "MULTIPLY", puffs, math_n(nt, "MAXIMUM", near_rim, pool))
    v = N(nt, "ShaderNodeVolumePrincipled", Anisotropy=0.25)
    v.inputs["Color"].default_value = (0.42, 0.40, 0.40, 1) if not DARK else (0.22, 0.19, 0.19, 1)
    back = smooth(nt, s.outputs["Y"], -2.5, 0.8)
    dens = math_n(nt, "MULTIPLY", dens, math_n(nt, "ADD", math_n(nt, "MULTIPLY", back, vb=0.8), vb=0.2))
    dens = math_n(nt, "MULTIPLY", dens, math_n(nt, "MAXIMUM", smooth(nt, er, 0.95, 1.3), smooth(nt, dy, 3.0, 5.0)))  # keep the opening clear
    L(nt, math_n(nt, "MULTIPLY", dens, vb=1.4 * SMOKE), v.inputs["Density"])
    # embers glowing inside the smoke near the rim
    L(nt, math_n(nt, "MULTIPLY", math_n(nt, "POWER", near_rim, vb=3.0), math_n(nt, "MULTIPLY", puffs, vb=0.8 * SMOKE)),
      v.inputs["Emission Strength"])
    v.inputs["Emission Color"].default_value = (*HOT, 1)
    L(nt, v.outputs[0], out.inputs["Volume"])
    return m


bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, GROUND + 8.5))
sm = bpy.context.object
sm.name = "smoke"
sm.scale = (26, 16, 17)
sm.data.materials.append(smoke_mat())

# ---------------------------------------------------------------- torn earth and broken stone hanging in the air
STONE = flat_mat("stone", (0.11, 0.105, 0.1), 0.85)
DIRT = flat_mat("dirt", (0.14, 0.08, 0.045), 0.95)
G2 = grass_mat(False)
for i in range(34):
    a = rnd.uniform(0, math.tau)
    rr = rnd.uniform(3.4, 8.5)
    h = rnd.uniform(0.8, 13.0) * (1.0 if rr < 6 else 0.6)
    bm_d = bmesh.new()
    n = rnd.choice((1, 1, 1, 1, 2, 2, 3, 4))
    for k in range(n):
        ox, oy, oz = (k % 2), (k // 2) % 2, -(k // 4)
        box(bm_d, ox, oy, oz, ox + 1, oy + 1, oz + 1)
    ob = mesh_obj("chunk%d" % i, bm_d, rnd.choice((G2, G2, STONE, DIRT)))
    ob.location = (math.cos(a) * rr, math.sin(a) * rr * 0.7, GROUND + h)
    ob.rotation_euler = (rnd.uniform(-0.9, 0.9), rnd.uniform(-0.9, 0.9), rnd.uniform(0, math.tau))
    sz = rnd.uniform(0.35, 0.9) if rr > 5 else rnd.uniform(0.6, 1.0)
    ob.scale = (sz, sz, sz)
# pebbles and grit pulled toward it
bm_g = bmesh.new()
for i in range(140):
    a = rnd.uniform(0, math.tau)
    rr = rnd.uniform(2.8, 9.0)
    p = Vector((math.cos(a) * rr, math.sin(a) * rr * 0.6, GROUND + rnd.uniform(0.2, 12)))
    s = rnd.uniform(0.03, 0.08)
    box(bm_g, p.x - s, p.y - s, p.z - s, p.x + s, p.y + s, p.z + s)
mesh_obj("grit", bm_g, STONE)

# spark streaks: thin hot slivers sweeping round and into the rim
bm_k = bmesh.new()
for i in range(150):
    a = rnd.uniform(0, math.tau)
    k = rnd.uniform(1.05, 1.9)
    p = Vector((RX * k * math.cos(a), rnd.uniform(-1.6, 0.4), C + RZ * k * math.sin(a)))
    tang = Vector((-math.sin(a) * RX, 0, math.cos(a) * RZ)).normalized()
    inward = (Vector((0, 0, C)) - p).normalized()
    d = (tang * 0.8 + inward * 0.6).normalized()
    ln = rnd.uniform(0.05, 0.45) ** 1.3 * 1.6
    w = rnd.uniform(0.006, 0.016)
    side = d.cross(Vector((0, 1, 0))).normalized() * w
    up = Vector((0, 1, 0)) * w
    q = p + d * ln
    vs = [bm_k.verts.new(v) for v in (p - side - up, q - side - up, q + side - up, p + side - up,
                                      p - side + up, q - side + up, q + side + up, p + side + up)]
    for f in ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm_k.faces.new([vs[j] for j in f])
SPK = flat_mat("spark", (0, 0, 0), 1.0, tuple(min(1, c * 0.35 + 0.65) for c in HOT), 30.0)
mesh_obj("sparks", bm_k, SPK)

# slower embers: glowing motes drifting off the rim, hotter colours, varied sizes
bm_e = bmesh.new()
for i in range(120):
    a = rnd.uniform(0, math.tau)
    k = rnd.uniform(1.1, 2.6)
    p = Vector((RX * k * math.cos(a), rnd.uniform(-2.5, 1.0), C + RZ * k * math.sin(a) + rnd.uniform(0, 3)))
    sz = rnd.uniform(0.015, 0.05)
    bmesh.ops.create_icosphere(bm_e, subdivisions=1, radius=sz, matrix=__import__("mathutils").Matrix.Translation(p))
EMB2 = flat_mat("ember2", (0, 0, 0), 1.0, tuple(min(1, c * 0.8 + 0.2) for c in HOT), 14.0)
mesh_obj("embers2", bm_e, EMB2)

# ground eruption: shattered slabs of the ground tilted up round the foot, lit from beneath
for i in range(16):
    a = rnd.uniform(0, math.tau)
    rr = rnd.uniform(2.4, 5.5)
    bm_d = bmesh.new()
    w, d_, h = rnd.randint(1, 3), rnd.randint(1, 2), 1
    box(bm_d, 0, 0, -1, w, d_, 0)
    ob = mesh_obj("slab%d" % i, bm_d, rnd.choice((G2, STONE)))
    ob.location = (math.cos(a) * rr * 1.2, math.sin(a) * rr * 0.8, GROUND + 0.3)
    ob.rotation_euler = (rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), a)

# the beam: a turbulent column of plasma, white-hot core, energy ribbons spiralling up it, a flare at its root
BTOP = C + RZ * 0.9


def beam_mat():
    m, nt, out = nodes_mat("beam_v")
    tc = N(nt, "ShaderNodeTexCoord")
    ss = N(nt, "ShaderNodeSeparateXYZ")
    L(nt, tc.outputs["Object"], ss.inputs[0])
    rad = math_n(nt, "SQRT", math_n(nt, "ADD", math_n(nt, "MULTIPLY", ss.outputs["X"], ss.outputs["X"]),
                                     math_n(nt, "MULTIPLY", ss.outputs["Y"], ss.outputs["Y"])))
    # stretch the noise up the column and twist it so it reads as rushing, coiling energy
    tw = N(nt, "ShaderNodeVectorRotate", _rotation_type="Z_AXIS")
    L(nt, tc.outputs["Object"], tw.inputs["Vector"])
    L(nt, math_n(nt, "MULTIPLY", ss.outputs["Z"], vb=9.0), tw.inputs["Angle"])
    st = N(nt, "ShaderNodeMapping")
    st.inputs["Scale"].default_value = (1.0, 1.0, 0.06)
    L(nt, tw.outputs[0], st.inputs["Vector"])
    nz = N(nt, "ShaderNodeTexNoise", _noise_dimensions="4D", Scale=3.0, Detail=8.0, Roughness=0.6, Distortion=0.7, W=2.0)
    L(nt, st.outputs[0], nz.inputs["Vector"])
    wobble = math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", nz.outputs["Fac"], vb=0.5), vb=0.9)
    rr = math_n(nt, "ADD", rad, wobble)
    core = math_n(nt, "POWER", smooth(nt, rr, 0.2, 0.0), vb=2.0)
    sheath = math_n(nt, "MULTIPLY", smooth(nt, rr, 1.0, 0.2), smooth(nt, nz.outputs["Fac"], 0.45, 0.7))
    up = smooth(nt, ss.outputs["Z"], 1.0, -0.6)  # thins out high in the sky
    root = math_n(nt, "POWER", smooth(nt, ss.outputs["Z"], -0.93, -1.0), vb=1.5)
    kc = math_n(nt, "MULTIPLY", math_n(nt, "ADD", math_n(nt, "MULTIPLY", core, vb=10.0),
                                       math_n(nt, "MULTIPLY", sheath, vb=1.2)), up)
    em = add_v(nt, scale_rgb(nt, (1.0, 0.93, 0.85), math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", core, up), vb=8.0)),
               scale_rgb(nt, HOT, math_n(nt, "ADD", kc, math_n(nt, "MULTIPLY", root, vb=5.0))))
    v = N(nt, "ShaderNodeVolumePrincipled")
    L(nt, math_n(nt, "MULTIPLY", sheath, vb=0.15), v.inputs["Density"])
    v.inputs["Color"].default_value = (0.05, 0.05, 0.05, 1)
    v.inputs["Emission Strength"].default_value = 1.0
    L(nt, em, v.inputs["Emission Color"])
    L(nt, v.outputs[0], out.inputs["Volume"])
    return m


bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=1.1, depth=220, location=(0, 0.2, BTOP + 110))
bc = bpy.context.object
bc.name = "beam"
bc.data.materials.append(beam_mat())
# ribbons: thin glowing bands coiling up round the beam, widest at its root
RIB = flat_mat("ribbon", (0, 0, 0), 1.0, tuple(min(1, c * 0.5 + 0.5) for c in HOT), 9.0)
for k in range(0):
    bm_r = bmesh.new()
    prev = None
    ph = k / 3 * math.tau
    for i in range(420):
        z = i * 0.12
        a = ph + z * (0.55 + 0.15 * k)
        rad = 0.7 + 0.9 * math.exp(-z * 0.12) + 0.25 * math.sin(z * 0.7 + k * 2.3)
        c = Vector((math.cos(a) * rad, 0.2 + math.sin(a) * rad, BTOP + z))
        w = 0.05 * (1 - i / 420) + 0.01
        pair = (bm_r.verts.new(c + Vector((0, 0, -w))), bm_r.verts.new(c + Vector((0, 0, w))))
        if prev:
            bm_r.faces.new([prev[0], pair[0], pair[1], prev[1]])
        prev = pair
    mesh_obj("ribbon%d" % k, bm_r, RIB)

# arcs crawling up the beam: jagged forks of light hugging its skin
bm_a = bmesh.new()
ARC = flat_mat("arc", (0, 0, 0), 1.0, tuple(min(1, c * 0.3 + 0.7) for c in HOT), 40.0)
def arc(p, d, steps, w, depth=0):
    for _ in range(steps):
        q = p + d * 0.45 + Vector((rnd.uniform(-0.25, 0.25), rnd.uniform(-0.25, 0.25), rnd.uniform(-0.1, 0.1)))
        rel = Vector((q.x, q.y - 0.2, 0))
        if rel.length > 0.01:
            q = Vector((0, 0.2, q.z)) + rel.normalized() * rnd.uniform(0.75, 1.05)
        dv = (q - p).normalized()
        side = dv.cross(Vector((0.3, -1, 0.1))).normalized() * w
        vs = [bm_a.verts.new(v) for v in (p - side, q - side, q + side, p + side)]
        bm_a.faces.new(vs)
        if depth < 1 and rnd.random() < 0.15:
            arc(q, (dv + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0))).normalized(), 4, w * 0.6, depth + 1)
        p = q
for i in range(7):
    a0 = rnd.uniform(0, math.tau)
    z0 = BTOP + rnd.uniform(0.5, 25)
    arc(Vector((math.cos(a0), 0.2 + math.sin(a0), z0)), Vector((0, 0, 1)), rnd.randint(6, 16), 0.025)
mesh_obj("arcs", bm_a, ARC)
point("beam_root", (0, 0.2, BTOP + 1.5), tuple(min(1, c * 0.5 + 0.5) for c in HOT), 500, 1.5)

# heat haze: a sheet of barely-refracting glass round the rim with a noisy surface, bending the world behind it
m, nt, out = nodes_mat("haze")
g = N(nt, "ShaderNodeBsdfRefraction", IOR=1.035, Roughness=0.0)
geo = N(nt, "ShaderNodeNewGeometry")
hn = N(nt, "ShaderNodeTexNoise", Scale=2.5, Detail=6.0)
L(nt, geo.outputs["Position"], hn.inputs["Vector"])
bmp = N(nt, "ShaderNodeBump", Strength=0.9, Distance=0.4)
L(nt, hn.outputs["Fac"], bmp.inputs["Height"])
L(nt, bmp.outputs["Normal"], g.inputs["Normal"])
tr = N(nt, "ShaderNodeBsdfTransparent")
tc = N(nt, "ShaderNodeTexCoord")
rr_, s_ = vec_len_xz(nt, tc.outputs["Object"])
mask = math_n(nt, "MULTIPLY", smooth(nt, rr_, 0.55, 0.75), smooth(nt, rr_, 1.0, 0.82))
mix = N(nt, "ShaderNodeMixShader")
L(nt, mask, mix.inputs[0])
L(nt, tr.outputs[0], mix.inputs[1])
L(nt, g.outputs[0], mix.inputs[2])
L(nt, mix.outputs[0], out.inputs["Surface"])
bm_h = bmesh.new()
for t in range(96):
    pass
ring = [bm_h.verts.new((math.cos(t / 96 * math.tau), 0, math.sin(t / 96 * math.tau))) for t in range(96)]
bm_h.faces.new(ring)
hz = mesh_obj("haze", bm_h, m)
hz.scale = (RX * 2.0, 1, RZ * 1.7)
hz.location = (0, -1.4, C)

# ---------------------------------------------------------------- the timeline: one still per key moment
# crack -> burst -> rise (opening), spin -> eye -> bang (closing). Each sets the tear's width/height, the beam's
# extent, how far the debris has flown, and the flashes.
PH = PHASES.get(SHOT)
if PH:
    sx, sy = PH["size"]
    for name in ("plasma", "abyss", "haze"):
        ob = sc.objects[name]
        ob.scale.x *= sx
        ob.scale.z *= sy
    # beam: keep only the part between lo and hi (fractions of its height)
    lo, hi = PH["beam"]
    for ob in list(sc.objects):
        if ob.name == "beam" or ob.name == "arcs":
            if hi <= lo:
                bpy.data.objects.remove(ob)
            elif ob.name == "beam":
                ob.scale.z = hi - lo
                ob.location.z = BTOP + 220 * (lo + hi) / 2
            elif lo > 0.02:
                bpy.data.objects.remove(ob)
    if hi <= lo and "beam_root" in sc.objects:
        bpy.data.objects.remove(sc.objects["beam_root"])
    if PH.get("head"):  # the beam's leading edge punching skyward
        bm_hd = bmesh.new()
        bmesh.ops.create_icosphere(bm_hd, subdivisions=3, radius=1.0)
        hd = mesh_obj("head", bm_hd, flat_mat("head", (0, 0, 0), 1.0, tuple(min(1, c * 0.4 + 0.6) for c in HOT), 60.0))
        hd.location = (0, 0.2, BTOP + 220 * hi)
        hd.scale = (1.3, 1.3, 2.6)
        point("head_l", (0, -0.5, BTOP + 220 * hi), tuple(min(1, c * 0.5 + 0.5) for c in HOT), 8000, 1.5)
    # debris: pushed out (burst) or drawn in (closing), round the tear's middle
    f = PH["debris"]
    mid = Vector((0, 0, C))
    for ob in sc.objects:
        if ob.name.startswith(("chunk", "grit", "embers", "sparks")):
            if ob.name.startswith("chunk"):
                ob.location = mid + (ob.location - mid) * f
            else:
                ob.scale = (f, f, f)
                ob.location = mid * (1 - f)
    # the rim burns hotter as it closes
    pm = bpy.data.materials["plasma"].node_tree
    if PH.get("hot", 1.0) != 1.0:
        for n in pm.nodes:
            if n.type == "VECT_MATH" and n.operation == "SCALE" and not n.inputs["Scale"].is_linked:
                pass
        pl_vol = next(n for n in pm.nodes if n.type == "PRINCIPLED_VOLUME")
        mult = pm.nodes.new("ShaderNodeVectorMath")
        mult.operation = "SCALE"
        mult.inputs["Scale"].default_value = PH["hot"]
        src = pl_vol.inputs["Emission Color"].links[0].from_socket
        pm.links.new(src, mult.inputs[0])
        pm.links.new(mult.outputs[0], pl_vol.inputs["Emission Color"])
    # flash: a white-hot star at the heart
    if PH.get("flash"):
        k = PH["flash"]
        bm_f = bmesh.new()
        bmesh.ops.create_icosphere(bm_f, subdivisions=3, radius=0.6 * k)
        fl = mesh_obj("flash", bm_f, flat_mat("flash", (0, 0, 0), 1.0, (1, 0.95, 0.9), 400.0))
        fl.location = (0, -0.3, C)
        point("flash_l", (0, -1.0, C), (1, 0.95, 0.9), 60000 * k, 1.0)
        # light streaks: anamorphic-style horizontal flare
        bm_s = bmesh.new()
        box(bm_s, -14 * k, -0.02, -0.03, 14 * k, 0.02, 0.03)
        st = mesh_obj("streak", bm_s, flat_mat("streak", (0, 0, 0), 1.0, tuple(min(1, c * 0.5 + 0.5) for c in HOT), 80.0))
        st.location = (0, -0.6, C)
    # shockwave: a ring of light racing over the ground, kicking up a band of dust
    if PH.get("wave"):
        R = PH["wave"]
        bm_w = bmesh.new()
        segs = 160
        inner, outer = [], []
        for i in range(segs):
            t = i / segs * math.tau
            inner.append(bm_w.verts.new((math.cos(t) * (R - 0.35), math.sin(t) * (R - 0.35), 0)))
            outer.append(bm_w.verts.new((math.cos(t) * (R + 0.35), math.sin(t) * (R + 0.35), 0.0)))
        for i in range(segs):
            j = (i + 1) % segs
            bm_w.faces.new([inner[i], inner[j], outer[j], outer[i]])
        wv = mesh_obj("wave", bm_w, flat_mat("wave", (0, 0, 0), 1.0, tuple(min(1, c * 0.6 + 0.4) for c in HOT), 30.0))
        wv.location = (0, 0, GROUND + 0.15)
        # dust wall riding the ring
        m, nt, out = nodes_mat("dust")
        geo = N(nt, "ShaderNodeNewGeometry")
        sp = N(nt, "ShaderNodeSeparateXYZ")
        L(nt, geo.outputs["Position"], sp.inputs[0])
        rad = math_n(nt, "SQRT", math_n(nt, "ADD", math_n(nt, "MULTIPLY", sp.outputs["X"], sp.outputs["X"]),
                                         math_n(nt, "MULTIPLY", sp.outputs["Y"], sp.outputs["Y"])))
        band = smooth(nt, math_n(nt, "ABSOLUTE", math_n(nt, "SUBTRACT", rad, vb=R - 0.8)), 1.6, 0.0)
        hgt = smooth(nt, math_n(nt, "SUBTRACT", sp.outputs["Z"], vb=GROUND), 2.5, 0.0)
        dn = N(nt, "ShaderNodeTexNoise", Scale=0.8, Detail=6.0)
        L(nt, geo.outputs["Position"], dn.inputs["Vector"])
        dens = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", band, hgt), smooth(nt, dn.outputs["Fac"], 0.35, 0.65))
        v = N(nt, "ShaderNodeVolumePrincipled")
        v.inputs["Color"].default_value = (0.35, 0.3, 0.27, 1)
        L(nt, math_n(nt, "MULTIPLY", dens, vb=3.0), v.inputs["Density"])
        L(nt, v.outputs[0], out.inputs["Volume"])
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, GROUND + 1.5))
        du = bpy.context.object
        du.scale = (2 * R + 4, 2 * R + 4, 3.2)
        du.data.materials.append(m)
    # the crack: before it opens, reality splits like struck glass round a hairline of light
    if PH.get("cracks"):
        bm_c = bmesh.new()
        def crack_line(p, ang, length, wid, depth=0):
            steps = max(3, int(length / 0.3))
            for _ in range(steps):
                ang += rnd.uniform(-0.6, 0.6)
                q = p + Vector((math.cos(ang), 0, math.sin(ang))) * (length / steps)
                side = Vector((-math.sin(ang), 0, math.cos(ang))) * wid
                vs = [bm_c.verts.new(v) for v in (p - side, q - side * 0.85, q + side * 0.85, p + side)]
                bm_c.faces.new(vs)
                if depth < 2 and rnd.random() < 0.25:
                    crack_line(q, ang + rnd.choice((-1, 1)) * rnd.uniform(0.5, 1.1), length * 0.45, wid * 0.6, depth + 1)
                p = q
                wid *= 0.86
        for i in range(PH["cracks"]):
            z = C + rnd.uniform(-RZ * 0.6, RZ * 0.6)
            side = rnd.choice((-1, 1))
            ang = (0 if side > 0 else math.pi) + rnd.uniform(-0.9, 0.9)
            crack_line(Vector((0, -0.75, z)), ang, rnd.uniform(1.5, 4.0), 0.03)
        mesh_obj("cracks", bm_c, flat_mat("crk", (0, 0, 0), 1.0, tuple(min(1, c * 0.4 + 0.6) for c in HOT), 45.0))

# ---------------------------------------------------------------- shots
SHOTS = {
    "hero": ((-10.5, -23.0, 2.6), (0.5, 0, 6.4), 26),
    "close": ((-3.5, -10.0, 2.8), (0, 0, 5.6), 24),
    "wide": ((-22, -42, 10), (0, 0, 10), 30),
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
    gl.inputs["Threshold"].default_value = 1.5
    gl.inputs["Strength"].default_value = 0.4
    gl.inputs["Size"].default_value = 0.6
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    go = ng.nodes.new("NodeGroupOutput")
    ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
    ng.links.new(gl.outputs["Image"], go.inputs[0])
    sc.render.use_compositing = True
except Exception as e:
    print("COMP FAIL", e)

os.makedirs(OUT, exist_ok=True)
sc.render.filepath = os.path.abspath(os.path.join(OUT, "vfx_%s_%s.png" % (RANK, SHOT)))
bpy.ops.render.render(write_still=True)
print("WROTE", sc.render.filepath)
