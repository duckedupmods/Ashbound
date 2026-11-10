"""The gate storm's eye, v2 (concept, Cycles): the storm of gate_storm.py with its eye remade so it isn't a flat cut-out.
A funnel of cloud reaches up from the deck into the tear (two nested cones of swirling cloud turning at different
speeds, lit red from above by the tear), the tear sits at the funnel's top with a burning lip, and inside it layers of
dark red swirl hang at different depths in front of the dungeon's hall (parallax), lightning crawls on the funnel wall.
Everything here is what the game can draw: textured cones, a few layered discs, glow lines.
  blender -b -P tools/blender/gate_storm_eye.py -- <rank> [eye|wide|crater] [fast] [lair]  ->  tools/renders/gate/storm_eye_<rank>_<shot>.png"""
import os, math

HERE = os.path.dirname(os.path.abspath(__file__))
_storm = open(os.path.join(HERE, "gate_storm.py"), encoding="utf-8").read()
_eye_a = _storm.index("# ---------------------------------------------------------------- through the eye")
_eye_b = _storm.index("# ---------------------------------------------------------------- lightning in the gate's colour")
_ash = _storm.index("# ---------------------------------------------------------------- ash falling like rain")
_render = _storm.index("# ---------------------------------------------------------------- shots, bloom, render")
# the deck's eye narrows going up (into the funnel) instead of opening out: no sky round the funnel
_head = _storm[:_eye_a].replace('L(nt, math_n(nt, "MULTIPLY", glow, vb=0.35), vol.inputs["Emission Strength"])', 'L(nt, math_n(nt, "MULTIPLY", glow, vb=0.12), vol.inputs["Emission Strength"])').replace('math_n(nt, "MULTIPLY", zrise, vb=0.55)', 'math_n(nt, "MULTIPLY", zrise, vb=-0.4)')
assert _head != _storm[:_eye_a]
exec(_head + _storm[_eye_b:_ash])

# ---------------------------------------------------------------- the funnel: cloud reaching up from the deck into the tear
F_BOT, F_TOP = BASE_Z - 3, TOP_Z - 2      # its foot in the deck, its top at the tear
R_BOT, R_TOP = EYE_R + 6, 13.0
TEAR_Z = F_TOP + 0.5


def funnel_mat(name, twist, speed_seed, alpha, glow, solid=False):
    """Swirling cloud on a cone in its own (angle, height): streaks wound into a spiral, darker low, lit red near the top."""
    m, nt, out = nodes_mat(name)
    tc = N(nt, "ShaderNodeTexCoord")
    sp = N(nt, "ShaderNodeSeparateXYZ")
    L(nt, tc.outputs["Object"], sp.inputs[0])
    ang = math_n(nt, "ARCTAN2", sp.outputs["Y"], sp.outputs["X"])
    h = math_n(nt, "DIVIDE", math_n(nt, "SUBTRACT", sp.outputs["Z"], vb=F_BOT), vb=F_TOP - F_BOT)
    u = math_n(nt, "ADD", math_n(nt, "MULTIPLY", ang, vb=1.0), math_n(nt, "MULTIPLY", h, vb=twist))
    cb = N(nt, "ShaderNodeCombineXYZ")
    # wrap the angle seamlessly: noise on a circle (cos, sin) of the wound angle
    L(nt, math_n(nt, "MULTIPLY", math_n(nt, "COSINE", u), vb=4.0), cb.inputs["X"])
    L(nt, math_n(nt, "MULTIPLY", math_n(nt, "SINE", u), vb=4.0), cb.inputs["Y"])
    L(nt, math_n(nt, "ADD", math_n(nt, "MULTIPLY", h, vb=9.0), vb=speed_seed), cb.inputs["Z"])
    n1 = N(nt, "ShaderNodeTexNoise", Scale=1.4, Detail=10.0, Roughness=0.65, Distortion=1.1)
    L(nt, cb.outputs[0], n1.inputs["Vector"])
    streak = smooth(nt, n1.outputs["Fac"], 0.42, 0.7)
    cover = math_n(nt, "ADD", math_n(nt, "MULTIPLY", streak, vb=0.3), vb=0.7) if solid else streak
    # thinner toward the top where it's torn into the tear
    a = math_n(nt, "MULTIPLY", cover, math_n(nt, "MULTIPLY", smooth(nt, h, 1.02, 0.85), vb=alpha))
    # its foot frays out into the deck: no clean rim
    fray = math_n(nt, "ADD", h, math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", n1.outputs["Fac"], vb=0.5), vb=0.5))
    a = math_n(nt, "MULTIPLY", a, smooth(nt, fray, 0.05, 0.4))
    bsdf = N(nt, "ShaderNodeBsdfPrincipled", Roughness=1.0)
    bsdf.inputs["Base Color"].default_value = (0.17, 0.165, 0.18, 1)
    lit = math_n(nt, "MULTIPLY", math_n(nt, "POWER", h, vb=6.0), math_n(nt, "ADD", streak, vb=0.4))
    bsdf.inputs["Emission Color"].default_value = (*HOT, 1)
    L(nt, math_n(nt, "MULTIPLY", lit, vb=glow), bsdf.inputs["Emission Strength"])
    tr = N(nt, "ShaderNodeBsdfTransparent")
    mix = N(nt, "ShaderNodeMixShader")
    L(nt, a, mix.inputs[0])
    L(nt, tr.outputs[0], mix.inputs[1])
    L(nt, bsdf.outputs[0], mix.inputs[2])
    L(nt, mix.outputs[0], out.inputs["Surface"])
    return m


def cone(name, r0, r1, z0, z1, mat, bulge=0.0):
    bm = bmesh.new()
    rings, segs = 24, 72
    vs = []
    for i in range(rings + 1):
        t = i / rings
        # a flared horn, not a straight cone: wide where it meets the deck, tight into the tear
        r = r1 + (r0 - r1) * (1 - t) ** 1.8 + bulge * math.sin(t * math.pi)
        z = z0 + (z1 - z0) * t
        vs.append([bm.verts.new((EYE.x + r * math.cos(k / segs * math.tau), EYE.y + r * math.sin(k / segs * math.tau), z)) for k in range(segs)])
    for i in range(rings):
        for k in range(segs):
            bm.faces.new((vs[i][k], vs[i][(k + 1) % segs], vs[i + 1][(k + 1) % segs], vs[i + 1][k]))
    ob = mesh_obj(name, bm, mat, smooth=True)
    return ob


# a solid dark wall behind it all, so nothing but cloud shows round the funnel
cone("funnel_back", R_BOT + 2, R_TOP + 1.5, F_BOT, F_TOP + 0.2, funnel_mat("funnel_back", 2.0, 13.0, 1.0, 1.5, solid=True), bulge=1.5)
cone("funnel_outer", R_BOT, R_TOP, F_BOT, F_TOP, funnel_mat("funnel_outer", 3.0, 0.0, 1.0, 3.0), bulge=1.5)
cone("funnel_mid", R_BOT - 4, R_TOP - 1.5, F_BOT + 3, F_TOP + 0.3, funnel_mat("funnel_mid", 5.0, 3.7, 0.75, 5.0), bulge=0.8)
cone("funnel_inner", R_BOT - 8, R_TOP - 3, F_BOT + 8, F_TOP + 0.4, funnel_mat("funnel_inner", 7.5, 8.1, 0.5, 8.0))

# ---------------------------------------------------------------- the tear at its top: a jagged lens, its lip burning
def tear_outline(n=48, a=20.0, b=8.5):
    pts = []
    for k in range(n):
        t = k / n * math.tau
        jag = 1 + 0.1 * math.sin(t * 7 + 1.3) + 0.06 * math.sin(t * 13 + 0.4) + rs.uniform(-0.05, 0.05)
        x, y = math.cos(t) * a, math.sin(t) * b * (1 - 0.35 * abs(math.cos(t)) ** 3)
        pts.append((x * jag, y * jag))
    return pts


TEAR = tear_outline()
TEAR_ROT = math.radians(35)


def tear_xy(x, y, grow=1.0):
    c, s = math.cos(TEAR_ROT), math.sin(TEAR_ROT)
    return EYE.x + (x * c - y * s) * grow, EYE.y + (x * s + y * c) * grow


# the lip: a band round the outline, white-hot at the edge into the gate's colour
LIP_IN = flat_mat("lip_core", (0, 0, 0), 1.0, WHITE, 45.0)
LIP_OUT = flat_mat("lip_glow", (0, 0, 0), 1.0, HOT, 12.0)
for name, g0, g1, z, mat in (("lip_core", 0.97, 1.06, TEAR_Z - 0.05, LIP_IN), ("lip_glow", 1.06, 1.28, TEAR_Z - 0.02, LIP_OUT)):
    bm = bmesh.new()
    a_ = [bm.verts.new((*tear_xy(x, y, g0), z)) for x, y in TEAR]
    b_ = [bm.verts.new((*tear_xy(x, y, g1), z)) for x, y in TEAR]
    for k in range(len(TEAR)):
        bm.faces.new((a_[k], a_[(k + 1) % len(TEAR)], b_[(k + 1) % len(TEAR)], b_[k]))
    mesh_obj(name, bm, mat)
# black where the tear isn't: the funnel's top closed round it (seen only through the cloud)
# inside: swirl layers at depths over the hall, each a disc of red-black streaks with holes in it
HALL = os.path.abspath(os.path.join(OUT, "sky3_hall_%s.png" % LAIR))


def swirl_mat(name, scale, seed, alpha, glow):
    m, nt, out = nodes_mat(name)
    tc = N(nt, "ShaderNodeTexCoord")
    sp = N(nt, "ShaderNodeSeparateXYZ")
    L(nt, tc.outputs["Object"], sp.inputs[0])
    r = math_n(nt, "SQRT", math_n(nt, "ADD", math_n(nt, "MULTIPLY", sp.outputs["X"], sp.outputs["X"]), math_n(nt, "MULTIPLY", sp.outputs["Y"], sp.outputs["Y"])))
    rot = N(nt, "ShaderNodeVectorRotate", _rotation_type="Z_AXIS")
    L(nt, tc.outputs["Object"], rot.inputs["Vector"])
    L(nt, math_n(nt, "MULTIPLY", math_n(nt, "EXPONENT", math_n(nt, "MULTIPLY", r, vb=-0.12)), vb=5.0), rot.inputs["Angle"])
    off = N(nt, "ShaderNodeVectorMath", _operation="ADD")
    off.inputs[1].default_value = (seed, seed * 0.7, 0)
    L(nt, rot.outputs[0], off.inputs[0])
    nz = N(nt, "ShaderNodeTexNoise", Scale=scale, Detail=6.0, Distortion=1.2)
    L(nt, off.outputs[0], nz.inputs["Vector"])
    st = smooth(nt, nz.outputs["Fac"], 0.46, 0.7)
    em = N(nt, "ShaderNodeEmission")
    em.inputs["Color"].default_value = (*HOT, 1)
    L(nt, math_n(nt, "MULTIPLY", st, vb=glow), em.inputs["Strength"])
    dark = N(nt, "ShaderNodeBsdfDiffuse")
    dark.inputs["Color"].default_value = (0.01, 0.005, 0.006, 1)
    body = N(nt, "ShaderNodeAddShader")
    L(nt, em.outputs[0], body.inputs[0])
    L(nt, dark.outputs[0], body.inputs[1])
    tr = N(nt, "ShaderNodeBsdfTransparent")
    mix = N(nt, "ShaderNodeMixShader")
    L(nt, math_n(nt, "MULTIPLY", math_n(nt, "ADD", st, vb=0.15), vb=alpha, clamp=True), mix.inputs[0])
    L(nt, tr.outputs[0], mix.inputs[1])
    L(nt, body.outputs[0], mix.inputs[2])
    L(nt, mix.outputs[0], out.inputs["Surface"])
    return m


def disc(name, z, rad, mat):
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, segments=48, radius=rad)
    ob = mesh_obj(name, bm, mat)
    ob.location = (EYE.x, EYE.y, z)
    return ob


# deeper layers are wider (they fill more of the view through the tear the further back they are)
disc("swirl_1", TEAR_Z + 2.5, 22, swirl_mat("swirl_1", 0.22, 0.0, 0.75, 6.0))
disc("swirl_2", TEAR_Z + 6.0, 30, swirl_mat("swirl_2", 0.15, 4.2, 0.6, 9.0))
disc("swirl_3", TEAR_Z + 11.0, 40, swirl_mat("swirl_3", 0.1, 9.9, 0.5, 12.0))
# furthest: the dungeon's hall, looked down into
m_hall, nt, out = nodes_mat("hall_view")
tc2 = N(nt, "ShaderNodeTexCoord")
sp2 = N(nt, "ShaderNodeSeparateXYZ")
L(nt, tc2.outputs["Object"], sp2.inputs[0])
HR = 46.0
cb = N(nt, "ShaderNodeCombineXYZ")
L(nt, math_n(nt, "ADD", math_n(nt, "DIVIDE", sp2.outputs["X"], vb=2 * HR), vb=0.5), cb.inputs["X"])
L(nt, math_n(nt, "ADD", math_n(nt, "DIVIDE", sp2.outputs["Y"], vb=-2 * HR * 0.6), vb=0.5), cb.inputs["Y"])
im = N(nt, "ShaderNodeTexImage", _extension="EXTEND")
if os.path.exists(HALL):
    im.image = bpy.data.images.load(HALL, check_existing=True)
L(nt, cb.outputs[0], im.inputs["Vector"])
em = N(nt, "ShaderNodeEmission", Strength=2.4)
L(nt, im.outputs[0], em.inputs["Color"])
L(nt, em.outputs[0], out.inputs["Surface"])
hall = disc("hall_view", TEAR_Z + 18.0, HR, m_hall)
hall.rotation_euler = (0, 0, TEAR_ROT)
# a lid over the funnel round the tear so only the tear shows the deep layers: a dark ring with the tear cut out
m_lid = flat_mat("lid", (0.03, 0.025, 0.028), 1.0, HOT, 0.4)
bm = bmesh.new()
inner = [bm.verts.new((*tear_xy(x, y, 1.0), TEAR_Z)) for x, y in TEAR]
outer = []
for k, (x, y) in enumerate(TEAR):
    t = math.atan2(*reversed(tear_xy(x, y, 1.0))) if False else None
    ang = math.atan2(inner[k].co.y - EYE.y, inner[k].co.x - EYE.x)
    outer.append(bm.verts.new((EYE.x + math.cos(ang) * (R_TOP + 30), EYE.y + math.sin(ang) * (R_TOP + 30), TEAR_Z + 0.3)))
for k in range(len(TEAR)):
    bm.faces.new((inner[k], inner[(k + 1) % len(TEAR)], outer[(k + 1) % len(TEAR)], outer[k]))
mesh_obj("lid", bm, m_lid)
# the tear lights the funnel wall from above
li = bpy.data.lights.new("tear_light", "AREA")
li.energy = 6.0e4
li.color = HOT
li.size = 18
lo = bpy.data.objects.new("tear_light", li)
sc.collection.objects.link(lo)
lo.location = (EYE.x, EYE.y, TEAR_Z - 1.5)
lo.rotation_euler = (math.pi, 0, 0)

# lightning crawling down the funnel wall
for k in range(3):
    a0 = rs.uniform(0, math.tau)
    z0 = F_TOP - 1
    z1 = F_BOT + rs.uniform(6, 16)
    def on_wall(a, z):
        t = (z - F_BOT) / (F_TOP - F_BOT)
        r = R_TOP + (R_BOT - R_TOP) * (1 - t) ** 1.8 - 0.6
        return Vector((EYE.x + math.cos(a) * r, EYE.y + math.sin(a) * r, z))
    bolt(on_wall(a0, z0), on_wall(a0 + rs.uniform(0.5, 1.2), z1), 0.07, 0.08, 1, rs)

SHOTS["eye"] = ((0, 30, GROUND + 1.8), tuple(EYE + Vector((0, 4, 70))), 16)
exec(_storm[_ash:_render])
exec(_storm[_render:].replace('"storm_%s_%s.png"', '"storm_eye_%s_%s.png"'))
