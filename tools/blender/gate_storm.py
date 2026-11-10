"""The Gate Storm (concept, Cycles): a wild gate tears open as a storm. A deck of dark cloud rolls in and turns round an
eye; through the eye, far up, the dungeon's first hall; the gate's own colour glows inside the cloud and comes down
the eye in a faint shaft. Ash falls like rain. Lightning in the gate's colour strikes the land: no fire anywhere, a
strike leaves a scorched crater and the dungeon's own monsters climb out of it. Storm spires, jagged pillars of the
dungeon's own blocks, stand where the storm feeds them lightning; they hold the eye open.
  blender -b -P tools/blender/gate_storm.py -- <rank> [wide|crater|far] [fast] [lair]  ->  tools/renders/gate/storm_<rank>_<shot>.png"""
import os, math, random, json
import bpy, bmesh
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "gate_vfx.py"), encoding="utf-8").read()
exec(_src.split("# ---------------------------------------------------------------- the plasma")[0])

rs = random.Random(5 + RI)
LAIR = next((a for a in ARGS if a.startswith("gate_")), "gate_crypt")
STRUCT = "E:/Ashbound/tools/renders/struct"
VOX = "E:/Ashbound/tools/renders/vox"
for o in [o for o in sc.objects if o.type == "LIGHT" and o.name.startswith("gate_")]:
    bpy.data.objects.remove(o, do_unlink=True)

EYE = Vector((6, 64, 0))     # the eye's middle, over the land
BASE_Z, TOP_Z = 46.0, 84.0   # the cloud deck
EYE_R = 22.0                 # the eye's radius at the deck's foot (it opens wider going up)
WHITE = tuple(min(1.0, c * 0.3 + 0.75) for c in HOT)

# ---------------------------------------------------------------- the light under a storm: dim, cold, the gate's colour in it
_sky.sun_elevation = math.radians(20)
_sky.sun_rotation = math.radians(200)
_tint.inputs[7].default_value = (0.5, 0.55, 0.65, 1)
_bg.inputs["Strength"].default_value = 0.2
sun.data.energy = 1.2
sun.data.color = (0.8, 0.82, 0.9)
sun.rotation_euler = (math.radians(65), 0, math.radians(200))
sc.view_settings.exposure = 0.3
sc.cycles.volume_step_rate = 3.0
sc.cycles.volume_bounces = 1

# the land beyond the voxel ground, hills to the horizon
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=160, y_segments=160, size=520)
for v in bm.verts:
    x, y = v.co.x, v.co.y
    d = math.hypot(x, y - 10)
    hills = math.sin(x * 0.021) * 6 + math.cos(y * 0.017 + 1.3) * 7 + math.sin((x + y) * 0.009) * 12
    v.co.z = GROUND - 2.6 + (max(0, d - 60) / 140) ** 1.3 * (8 + hills)
mesh_obj("far_land", bm, grass_mat(False))

# ---------------------------------------------------------------- the cloud deck, turning round the eye
m_cloud, nt, out = nodes_mat("storm_cloud")
tc = N(nt, "ShaderNodeTexCoord")
pos = tc.outputs["Object"]
sp = N(nt, "ShaderNodeSeparateXYZ")
L(nt, pos, sp.inputs[0])
dx = math_n(nt, "SUBTRACT", sp.outputs["X"], vb=EYE.x)
dy = math_n(nt, "SUBTRACT", sp.outputs["Y"], vb=EYE.y)
r = math_n(nt, "SQRT", math_n(nt, "ADD", math_n(nt, "MULTIPLY", dx, dx), math_n(nt, "MULTIPLY", dy, dy)))
# the spiral: the nearer the eye, the more it has turned
twist = math_n(nt, "MULTIPLY", math_n(nt, "EXPONENT", math_n(nt, "MULTIPLY", r, vb=-1 / 110)), vb=6.5)
rot = N(nt, "ShaderNodeVectorRotate", _rotation_type="Z_AXIS")
rot.inputs["Center"].default_value = (EYE.x, EYE.y, 0)
L(nt, pos, rot.inputs["Vector"])
L(nt, twist, rot.inputs["Angle"])
# flattened: clouds are wider than they are tall
squash = N(nt, "ShaderNodeVectorMath", _operation="MULTIPLY")
squash.inputs[1].default_value = (1.0, 1.0, 2.2)
L(nt, rot.outputs[0], squash.inputs[0])
n_big = N(nt, "ShaderNodeTexNoise", Scale=0.011, Detail=7.0, Roughness=0.58, Distortion=0.4)
L(nt, squash.outputs[0], n_big.inputs["Vector"])
n_fine = N(nt, "ShaderNodeTexNoise", Scale=0.06, Detail=4.0, Roughness=0.6)
L(nt, squash.outputs[0], n_fine.inputs["Vector"])
lump = math_n(nt, "ADD", n_big.outputs["Fac"], math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", n_fine.outputs["Fac"], vb=0.5), vb=0.35))
# its foot hangs in lumps; its top rolls
foot = math_n(nt, "ADD", math_n(nt, "MULTIPLY", n_big.outputs["Fac"], vb=-16.0), vb=BASE_Z + 8)
above_foot = smooth(nt, math_n(nt, "SUBTRACT", sp.outputs["Z"], foot), 0.0, 5.0)
below_top = smooth(nt, sp.outputs["Z"], TOP_Z, TOP_Z - 10)
# the eye: a funnel opening wider as it goes up, its wall ragged
zrise = math_n(nt, "SUBTRACT", sp.outputs["Z"], vb=BASE_Z)
wall = math_n(nt, "ADD", math_n(nt, "ADD", math_n(nt, "MULTIPLY", zrise, vb=0.55), vb=EYE_R),
              math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", n_fine.outputs["Fac"], vb=0.5), vb=14.0))
out_eye = smooth(nt, math_n(nt, "SUBTRACT", r, wall), 0.0, 14.0)
# thicker toward the eye wall (the storm piles up round it), thinner far out
pile = math_n(nt, "ADD", math_n(nt, "MULTIPLY", math_n(nt, "EXPONENT", math_n(nt, "MULTIPLY", r, vb=-1 / 140)), vb=0.18), vb=0.0)
dens = math_n(nt, "MULTIPLY", smooth(nt, math_n(nt, "ADD", lump, pile), 0.47, 0.66), above_foot)
dens = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", dens, below_top), out_eye)
vol = N(nt, "ShaderNodeVolumePrincipled")
vol.inputs["Color"].default_value = (0.2, 0.2, 0.22, 1)
vol.inputs["Anisotropy"].default_value = 0.25
L(nt, math_n(nt, "MULTIPLY", dens, vb=0.22), vol.inputs["Density"])
# the gate's colour glowing in the cloud, strongest round the eye, deep inside
glow = math_n(nt, "MULTIPLY", math_n(nt, "EXPONENT", math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", r, wall), vb=-1 / 12)),
              math_n(nt, "MULTIPLY", dens, smooth(nt, n_fine.outputs["Fac"], 0.4, 0.7)))
vol.inputs["Emission Color"].default_value = (*HOT, 1)
L(nt, math_n(nt, "MULTIPLY", glow, vb=0.35), vol.inputs["Emission Strength"])
L(nt, vol.outputs[0], out.inputs["Volume"])
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=64, radius1=620, radius2=620, depth=TOP_Z - BASE_Z + 24)
deck = mesh_obj("storm_deck", bm, m_cloud)
deck.location = (0, 0, (BASE_Z - 16 + TOP_Z + 8) / 2)
# object coords are the deck's own: shift them back to world height
shift = N(nt, "ShaderNodeVectorMath", _operation="ADD")
shift.inputs[1].default_value = (0, 0, deck.location.z)
L(nt, tc.outputs["Object"], shift.inputs[0])
for lk in [lk for lk in nt.links if lk.from_socket == tc.outputs["Object"] and lk.to_node != shift]:
    to = lk.to_socket
    nt.links.remove(lk)
    L(nt, shift.outputs[0], to)

# ---------------------------------------------------------------- through the eye: the dungeon's hall, far up
HALL = os.path.abspath(os.path.join(OUT, "sky3_hall_%s.png" % LAIR))
m_eye, nt, out = nodes_mat("eye_view")
tc2 = N(nt, "ShaderNodeTexCoord")
sp2 = N(nt, "ShaderNodeSeparateXYZ")
L(nt, tc2.outputs["Object"], sp2.inputs[0])
EYE_TOP = TOP_Z + 6
ER = EYE_R + (EYE_TOP - BASE_Z) * 0.55 + 10
uu = math_n(nt, "ADD", math_n(nt, "DIVIDE", sp2.outputs["X"], vb=2 * ER), vb=0.5)
vv = math_n(nt, "ADD", math_n(nt, "DIVIDE", sp2.outputs["Y"], vb=-2 * ER * 0.6), vb=0.5)
cb = N(nt, "ShaderNodeCombineXYZ")
L(nt, uu, cb.inputs["X"])
L(nt, vv, cb.inputs["Y"])
im = N(nt, "ShaderNodeTexImage", _extension="EXTEND")
if os.path.exists(HALL):
    im.image = bpy.data.images.load(HALL, check_existing=True)
L(nt, cb.outputs[0], im.inputs["Vector"])
rr = math_n(nt, "DIVIDE", math_n(nt, "SQRT", math_n(nt, "ADD", math_n(nt, "MULTIPLY", sp2.outputs["X"], sp2.outputs["X"]),
                                                    math_n(nt, "MULTIPLY", sp2.outputs["Y"], sp2.outputs["Y"]))), vb=ER)
em = N(nt, "ShaderNodeEmission")
mixc = N(nt, "ShaderNodeMix", _data_type="RGBA")
L(nt, smooth(nt, rr, 0.55, 0.95), mixc.inputs[0])
L(nt, im.outputs[0], mixc.inputs[6])
mixc.inputs[7].default_value = (*tuple(c * 0.6 for c in HOT), 1)
L(nt, mixc.outputs[2], em.inputs["Color"])
em.inputs["Strength"].default_value = 2.2
L(nt, em.outputs[0], out.inputs["Surface"])
bm = bmesh.new()
bmesh.ops.create_circle(bm, cap_ends=True, segments=64, radius=ER * 1.7)
eye = mesh_obj("eye_view", bm, m_eye)
eye.location = (EYE.x, EYE.y, EYE_TOP)
# a faint shaft of the gate's light down the eye
m_shaft, nt, out = nodes_mat("shaft")
vs_ = N(nt, "ShaderNodeVolumePrincipled")
vs_.inputs["Color"].default_value = (*HOT, 1)
vs_.inputs["Emission Color"].default_value = (*HOT, 1)
# soft all round: thickest down the middle, fading to nothing at its edge and toward the ground
tcs = N(nt, "ShaderNodeTexCoord")
sps = N(nt, "ShaderNodeSeparateXYZ")
L(nt, tcs.outputs["Generated"], sps.inputs[0])
ox = math_n(nt, "SUBTRACT", sps.outputs["X"], vb=0.5)
oy = math_n(nt, "SUBTRACT", sps.outputs["Y"], vb=0.5)
rad_s = math_n(nt, "SQRT", math_n(nt, "ADD", math_n(nt, "MULTIPLY", ox, ox), math_n(nt, "MULTIPLY", oy, oy)))
soft = math_n(nt, "MULTIPLY", smooth(nt, rad_s, 0.42, 0.05), smooth(nt, sps.outputs["Z"], 0.0, 0.6))
L(nt, math_n(nt, "MULTIPLY", soft, vb=0.003), vs_.inputs["Density"])
L(nt, math_n(nt, "MULTIPLY", soft, vb=0.012), vs_.inputs["Emission Strength"])
L(nt, vs_.outputs[0], out.inputs["Volume"])
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=EYE_R * 0.55, radius2=EYE_R * 0.9, depth=BASE_Z - GROUND)
shaft = mesh_obj("shaft", bm, m_shaft)
shaft.location = (EYE.x, EYE.y, GROUND + (BASE_Z - GROUND) / 2)
li = bpy.data.lights.new("eye_light", "SPOT")
li.energy = 5.0e5
li.color = HOT
li.spot_size = math.radians(40)
li.shadow_soft_size = 12
lo = bpy.data.objects.new("eye_light", li)
sc.collection.objects.link(lo)
lo.location = (EYE.x, EYE.y, TOP_Z)

# ---------------------------------------------------------------- lightning in the gate's colour, white at its heart
BOLT = flat_mat("bolt", (0, 0, 0), 1.0, WHITE, 60.0)
BOLT_RIM = flat_mat("bolt_rim", (0, 0, 0), 1.0, HOT, 18.0)
bm_b, bm_r = bmesh.new(), bmesh.new()


def seg(bm, a, b, w):
    d = (b - a)
    if d.length < 1e-4:
        return
    z = d.normalized()
    x = z.cross(Vector((0.3, 0.2, 1)).normalized() if abs(z.z) < 0.9 else Vector((1, 0, 0))).normalized() * w
    y = z.cross(x).normalized() * w
    ring_a = [bm.verts.new(a + x * math.cos(k * math.tau / 5) + y * math.sin(k * math.tau / 5)) for k in range(5)]
    ring_b = [bm.verts.new(b + x * math.cos(k * math.tau / 5) + y * math.sin(k * math.tau / 5)) for k in range(5)]
    for k in range(5):
        bm.faces.new((ring_a[k], ring_a[(k + 1) % 5], ring_b[(k + 1) % 5], ring_b[k]))


def bolt(a, b, w, rough=0.22, depth=0, rnd=rs):
    pts = [a, b]
    for _ in range(6):
        nxt = [pts[0]]
        for p, q in zip(pts, pts[1:]):
            m = (p + q) / 2
            L_ = (q - p).length
            m += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.3, 0.3))) * L_ * rough
            nxt += [m, q]
        pts = nxt
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        t = i / len(pts)
        seg(bm_b, p, q, w * (1.0 - 0.5 * t))
        seg(bm_r, p, q, w * 2.6 * (1.0 - 0.5 * t))
        if depth < 2 and rnd.random() < 0.06:
            d = (q - p).normalized()
            br = q + (d + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.6, 0.1)))).normalized() * (b - a).length * rnd.uniform(0.08, 0.2)
            bolt(q, br, w * 0.5, rough, depth + 1, rnd)
    return pts


STRIKE = Vector((0.5, 0.5, GROUND))
bolt(Vector((-8, 46, BASE_Z + 4)), STRIKE + Vector((0, 0, 0.2)), 0.16)


def plight(name, at, col, power, rad=1.0):
    li = bpy.data.lights.new(name, "POINT")
    li.energy = power
    li.color = col
    li.shadow_soft_size = rad
    ob = bpy.data.objects.new(name, li)
    sc.collection.objects.link(ob)
    ob.location = at


plight("strike", STRIKE + Vector((0, -1, 2.5)), WHITE, 9000, 1.5)
plight("strike_hi", Vector((-4, 24, 24)), HOT, 30000, 6)
# lightning inside the cloud, lighting it from within
for k in range(4):
    a = rs.uniform(0, math.tau)
    rr_ = rs.uniform(EYE_R + 6, 140)
    plight("cloud_flash", Vector((EYE.x + math.cos(a) * rr_, EYE.y + math.sin(a) * rr_, rs.uniform(BASE_Z + 2, BASE_Z + 14))), HOT,
           rs.uniform(1e5, 3e5), 10)

# ---------------------------------------------------------------- the dungeon's blocks, textured like the game's
with open(os.path.join(STRUCT, "sky_%s_tex.json" % LAIR)) as f:
    TEX = json.load(f)


def tex_material(name, meta, glow=0.0):
    m, nt, out = nodes_mat("k_" + name)
    tex = N(nt, "ShaderNodeTexImage", _interpolation="Closest")
    tex.image = bpy.data.images.load(meta["path"], check_existing=True)
    col = tex.outputs[0]
    if meta.get("tint"):
        mul = N(nt, "ShaderNodeMix", _data_type="RGBA", _blend_type="MULTIPLY")
        mul.inputs[0].default_value = 1.0
        L(nt, col, mul.inputs[6])
        mul.inputs[7].default_value = (*meta["tint"], 1)
        col = mul.outputs[2]
    b = N(nt, "ShaderNodeBsdfPrincipled", Roughness=0.9)
    L(nt, col, b.inputs["Base Color"])
    if glow:
        b.inputs["Emission Color"].default_value = (*HOT, 1)
        b.inputs["Emission Strength"].default_value = glow
    L(nt, b.outputs[0], out.inputs["Surface"])
    return m


def tex_of(*names):
    return [k for k in TEX if any(n in k for n in names)]


STONES = tex_of("bricks", "stone", "tiles") or list(TEX)[:3]
MATS = {k: tex_material(k, TEX[k]) for k in STONES}
CORE = flat_mat("spire_core", (0.02, 0.01, 0.01), 0.3, WHITE, 40.0)
GLOWSTONE = {k: tex_material(k + "_lit", TEX[k], 2.5) for k in STONES}


def cube(bm, x, y, z, s=1.0, uv=None):
    vs = [bm.verts.new(p) for p in ((x, y, z), (x + s, y, z), (x + s, y + s, z), (x, y + s, z),
                                    (x, y, z + s), (x + s, y, z + s), (x + s, y + s, z + s), (x, y + s, z + s))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        face = bm.faces.new([vs[i] for i in f])
        for lp, (u, v) in zip(face.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
            lp[uv].uv = (u, v)


class Blocks:
    def __init__(self):
        self.bms = {}

    def put(self, key, x, y, z, s=1.0):
        if key not in self.bms:
            bm = bmesh.new()
            self.bms[key] = (bm, bm.loops.layers.uv.new("uv"))
        bm, uv = self.bms[key]
        cube(bm, x, y, z, s, uv)

    def build(self, name, mats):
        for k, (bm, _) in self.bms.items():
            mesh_obj("%s_%s" % (name, k), bm, mats[k])


def spire(name, bx, by, height, rnd):
    """A jagged pillar of the dungeon's blocks, pushed up out of the ground and leaning, wider at the foot, its top torn
    into chunks hanging round a white-hot core the storm's lightning feeds."""
    gz = hmap.get((bx, by), GROUND)
    blk = Blocks()
    lean = Vector((rnd.uniform(-0.12, 0.12), rnd.uniform(-0.12, 0.12)))
    top = None
    for z in range(height):
        t = z / height
        rad = 2.6 * (1 - t) ** 0.8 + 0.6
        cx, cy = bx + lean.x * z + math.sin(z * 0.5) * 0.6, by + lean.y * z + math.cos(z * 0.4) * 0.6
        for ix in range(-4, 5):
            for iy in range(-4, 5):
                d = math.hypot(ix + 0.5 - (cx - round(cx)), iy + 0.5 - (cy - round(cy)))
                if d < rad + rnd.uniform(-0.6, 0.4):
                    k = rnd.choice(STONES)
                    hot = t > 0.55 and rnd.random() < 0.18
                    blk.put(k + ("_lit" if hot else ""), round(cx) + ix, round(cy) + iy, gz + z)
        top = Vector((round(cx) + 0.5, round(cy) + 0.5, gz + height))
    # torn chunks round the top, hanging in the air
    for k in range(14):
        a = rnd.uniform(0, math.tau)
        rr_ = rnd.uniform(1.8, 4.5)
        p = top + Vector((math.cos(a) * rr_, math.sin(a) * rr_, rnd.uniform(-3, 4)))
        kk = rnd.choice(STONES)
        blk.put(kk + ("_lit" if rnd.random() < 0.4 else ""), p.x, p.y, p.z, rnd.choice((0.5, 1.0, 1.0)))
    # the cracked earth at its foot, pushed up
    for k in range(18):
        a = rnd.uniform(0, math.tau)
        rr_ = rnd.uniform(2.5, 5.5)
        x, y = int(bx + math.cos(a) * rr_), int(by + math.sin(a) * rr_)
        blk.put(rnd.choice(STONES), x, y, hmap.get((x, y), gz), 1.0)
    mats = dict(MATS)
    mats.update({k + "_lit": GLOWSTONE[k] for k in STONES})
    blk.build(name, mats)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
    core = mesh_obj(name + "_core", bm, CORE)
    core.location = top + Vector((0, 0, 1.5))
    plight(name + "_light", top + Vector((0, 0, 1.5)), HOT, 6000, 1.2)
    # the storm feeding it
    bolt(top + Vector((rnd.uniform(-20, 20), rnd.uniform(5, 30), BASE_Z - top.z + 2)), top + Vector((0, 0, 1.5)), 0.09, 0.18, 1, rnd)
    return top


SPIRES = [spire("spire_a", -15, 15, 20, random.Random(3)), spire("spire_b", 25, 42, 26, random.Random(4)),
          spire("spire_c", -34, 78, 30, random.Random(5))]

# ---------------------------------------------------------------- the crater the strike left: torn-up earth, smoke, no fire
DIRT = flat_mat("dirt_clod", (0.05, 0.035, 0.03), 0.95)
blk = Blocks()
for k in range(26):
    a = rs.uniform(0, math.tau)
    rr_ = rs.uniform(1.8, 4.5)
    x, y = STRIKE.x + math.cos(a) * rr_, STRIKE.y + math.sin(a) * rr_
    blk.put("clod", x, y, GROUND + rs.uniform(0, 0.4) - 0.3, rs.choice((0.5, 0.5, 0.5, 1.0)))
blk.build("crater", {"clod": DIRT})
# a black pit in the middle
bm = bmesh.new()
bmesh.ops.create_circle(bm, cap_ends=True, segments=24, radius=1.7)
pit = mesh_obj("pit", bm, flat_mat("pit", (0.004, 0.003, 0.003), 1.0, HOT, 0.6))
pit.location = (STRIKE.x, STRIKE.y, GROUND + 0.02)
# smoke rising off it
m_smoke, nt, out = nodes_mat("crater_smoke")
tc3 = N(nt, "ShaderNodeTexCoord")
n3 = N(nt, "ShaderNodeTexNoise", Scale=0.6, Detail=5.0)
L(nt, tc3.outputs["Object"], n3.inputs["Vector"])
sp3 = N(nt, "ShaderNodeSeparateXYZ")
L(nt, tc3.outputs["Generated"], sp3.inputs[0])
fade = math_n(nt, "MULTIPLY", smooth(nt, sp3.outputs["Z"], 1.0, 0.2), smooth(nt, sp3.outputs["Z"], 0.0, 0.08))
rad3 = math_n(nt, "SQRT", math_n(nt, "ADD", math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", sp3.outputs["X"], vb=0.5), math_n(nt, "SUBTRACT", sp3.outputs["X"], vb=0.5)),
                                  math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", sp3.outputs["Y"], vb=0.5), math_n(nt, "SUBTRACT", sp3.outputs["Y"], vb=0.5))))
col3 = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", smooth(nt, n3.outputs["Fac"], 0.42, 0.7), fade), smooth(nt, rad3, 0.5, 0.15))
v3 = N(nt, "ShaderNodeVolumePrincipled")
v3.inputs["Color"].default_value = (0.12, 0.11, 0.11, 1)
L(nt, math_n(nt, "MULTIPLY", col3, vb=0.9), v3.inputs["Density"])
L(nt, v3.outputs[0], out.inputs["Volume"])
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1)
smk = mesh_obj("crater_smoke", bm, m_smoke)
smk.scale = (9, 9, 16)
smk.location = (STRIKE.x - 1.5, STRIKE.y + 2.0, GROUND + 8)
smk.rotation_euler = (0.25, -0.15, 0)

# ---------------------------------------------------------------- the dungeon's monsters climbing out
def mob(pose, at, yaw, height, sink=0.0):
    path = os.path.join(VOX, pose + "_f0.obj")
    ys = [float(l.split()[2]) for l in open(path) if l.startswith("v ")]
    s = height / (max(ys) - min(ys))
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=path, forward_axis="NEGATIVE_Z", up_axis="Y")
    new = [o for o in set(bpy.data.objects) - before if o.type == "MESH"]
    m, nt, out = nodes_mat("mob_" + pose)
    tex = N(nt, "ShaderNodeTexImage", _interpolation="Closest")
    tex.image = bpy.data.images.load(os.path.join(VOX, pose + "_f0.png"), check_existing=True)
    b = N(nt, "ShaderNodeBsdfPrincipled", Roughness=0.75)
    L(nt, tex.outputs[0], b.inputs["Base Color"])
    L(nt, b.outputs[0], out.inputs["Surface"])
    for o in new:
        o.data.materials.clear()
        o.data.materials.append(m)
        o.scale = (s, s, s)
        o.rotation_euler = (math.pi / 2, 0, math.radians(yaw))
        o.location = (at.x, at.y, at.z - sink - min(ys) * s)
    return new


# one hauling itself out of the pit, one just landed and rising, the rest already loose
mob("coffin_knight_pose_grab", STRIKE + Vector((-1.0, -0.9, 0)), -35, 3.0, sink=1.5)
mob("coffin_knight_pose_kneel", STRIKE + Vector((-4.2, -2.6, 0)), -55, 3.0)
mob("bone_hound_pose_bite_draw", STRIKE + Vector((1.6, -3.4, 0)), -20, 1.5)
mob("gravedigger_pose_lurch", STRIKE + Vector((2.8, 2.2, 0)), -40, 2.3)
plight("mob_fill", STRIKE + Vector((-1, -6, 3)), (0.75, 0.8, 1.0), 900, 3)

SHOTS = {
    "wide": ((-5, -26, GROUND + 2.6), (4, 30, 21), 15),
    "crater": ((-10, -10, GROUND + 1.6), (0, 0.5, 3.2), 20),
    "far": ((-50, -150, GROUND + 14), (4, 40, 34), 22),
}
# ---------------------------------------------------------------- ash falling like rain
ASH = flat_mat("ash", (0.5, 0.48, 0.47), 0.9)
bm = bmesh.new()
slant = Vector((0.18, 0.08, -1)).normalized()
for k in range(3600):
    p = Vector((rs.uniform(-34, 34), rs.uniform(-30, 40), rs.uniform(GROUND, GROUND + 30)))
    if any((p - Vector(c[0])).length < 9 for c in SHOTS.values()):
        continue
    q = p + slant * rs.uniform(0.6, 1.3)
    side = Vector((0.018, 0, 0))
    bm.faces.new([bm.verts.new(v) for v in (p - side, p + side, q + side, q - side)])
mesh_obj("ash_rain", bm, ASH)

bm_bm = mesh_obj("bolts", bm_b, BOLT)
mesh_obj("bolts_rim", bm_r, BOLT_RIM)

# ---------------------------------------------------------------- shots, bloom, render
loc, aim, lens = SHOTS.get(SHOT, SHOTS["wide"])
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 1500
cam.location = loc
cam.data.lens = lens
cam.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
sc.cycles.max_bounces = 6
try:
    ng = bpy.data.node_groups.new("comp", "CompositorNodeTree")
    sc.compositing_node_group = ng
    rl = ng.nodes.new("CompositorNodeRLayers")
    gl = ng.nodes.new("CompositorNodeGlare")
    gl.inputs["Type"].default_value = "Bloom"
    gl.inputs["Quality"].default_value = "High"
    gl.inputs["Threshold"].default_value = 1.2
    gl.inputs["Strength"].default_value = 0.35
    gl.inputs["Size"].default_value = 0.6
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    go = ng.nodes.new("NodeGroupOutput")
    ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
    ng.links.new(gl.outputs["Image"], go.inputs[0])
    sc.render.use_compositing = True
except Exception as ex:
    print("COMP FAIL", ex)
sc.render.image_settings.color_depth = "8"
sc.render.filepath = os.path.abspath(os.path.join(OUT, "storm_%s_%s.png" % (RANK, SHOT)))
bpy.ops.render.render(write_still=True)
print("WROTE", sc.render.filepath)
