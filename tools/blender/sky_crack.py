"""The sky cracks, v3 (concept, Cycles): a wild gate torn open high over the land in full daylight, and through it the
dungeon itself: a gate's first hall (tools/sky_dungeon.py) seen as if it hung right behind the tear, its stone and its
light, the lips burning round it. Shards of the broken sky fall out of it: thick slabs of dark crystal with burning
broken edges, each face a piece of the window, showing the same dungeon.
The dungeon is drawn with Cycles' ray portal: rays that reach the tear (or a shard's face) go on from the hall, which
stands far off where the camera can't see it.
  python tools/sky_dungeon.py gate_crypt
  blender -b -P tools/blender/sky_crack.py -- <rank> [wide|under|far] [fast] [lair]  ->  tools/renders/gate/sky3_<rank>_<shot>.png
(v2, the dusk one with see-through shards and a black void: sky_crack_v2.py)"""
import os, math, random, json
import bpy, bmesh
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "gate_rift.py"), encoding="utf-8").read()
exec(_src.split("\n# ---------------------------------------------------------------- shots, bloom, render")[0])

rs = random.Random(91 + RI)
LAIR = next((a for a in ARGS if a.startswith("gate_")), "gate_crypt")
STRUCT = "E:/Ashbound/tools/renders/struct"
BASE = {"ground_near", "ground_far", "trunks", "leaves"}
# the torn chunks hanging round a ground gate read as boxes up there: gone
for o in [o for o in sc.objects if o.name.startswith("chunk")]:
    bpy.data.objects.remove(o, do_unlink=True)
rift = [o for o in sc.objects if o.type == "MESH" and o.name not in BASE]

# ---------------------------------------------------------------- the rift, grown and laid across the sky
SKY = Vector((-16, 22, 50))
GROW = 7.0
hub = bpy.data.objects.new("sky_hub", None)
sc.collection.objects.link(hub)
hub.location = (0, Y0, C)
for o in rift:
    o.parent = hub
    o.matrix_parent_inverse = hub.matrix_world.inverted()
hub.location = SKY
hub.scale = (GROW, GROW, GROW)
hub.rotation_euler = (math.radians(28), math.radians(70), 0)
for o in sc.objects:
    if o.type == "LIGHT" and o.name.startswith("gate_"):
        o.location = SKY + (o.location - Vector((0, Y0, C))) * GROW
        o.data.energy *= GROW * GROW * 0.6
        if o.data.type in ("POINT", "SPOT", "AREA"):
            o.data.shadow_soft_size = max(getattr(o.data, "shadow_soft_size", 1), 6)

bpy.context.view_layer.update()
rot = hub.matrix_world.to_3x3().normalized()
ALONG = (rot @ Vector((0, 0, 1))).normalized()     # the tear's length
ACROSS = (rot @ Vector((1, 0, 0))).normalized()    # its width
FACING = (rot @ Vector((0, -1, 0))).normalized()   # where it looks (down toward the land)
void = next(o for o in rift if o.name == "void")
TEAR = void.matrix_world.translation.copy()

SHOTS = {
    "wide": ((-14, -62, GROUND + 4), tuple(TEAR + Vector((-8, 0, -18))), 20),
    "under": ((TEAR.x + 6, TEAR.y - 34, GROUND + 2), tuple(TEAR + Vector((0, 0, -6))), 16),
    "far": ((-60, -170, GROUND + 18), tuple(TEAR + Vector((0, 0, -10))), 30),
}
loc, aim, lens = SHOTS.get(SHOT, SHOTS["wide"])
LOOK = (TEAR - Vector(loc)).normalized()

# ---------------------------------------------------------------- daylight, as you'll mostly see it
_sky.sun_elevation = math.radians(38)
_sky.sun_rotation = math.radians(205)
_bg.inputs["Strength"].default_value = 0.55
_tint.inputs[7].default_value = (0.75, 0.9, 1.25, 1)
sun.data.energy = 4.0
sun.data.color = (1.0, 0.95, 0.88)
sun.rotation_euler = (math.radians(52), 0, math.radians(205))
sc.view_settings.exposure = -0.2

# ---------------------------------------------------------------- the land beyond the voxel ground, hills to the horizon
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=160, y_segments=160, size=420)
for v in bm.verts:
    x, y = v.co.x, v.co.y
    d = math.hypot(x, y - 10)
    hills = math.sin(x * 0.021) * 6 + math.cos(y * 0.017 + 1.3) * 7 + math.sin((x + y) * 0.009) * 12
    v.co.z = GROUND - 2.6 + (max(0, d - 60) / 140) ** 1.3 * (8 + hills)
mesh_obj("far_land", bm, grass_mat(False))

# ---------------------------------------------------------------- the dungeon, far off where only the portal sees it
OFFSET = Vector((4000, 0, 0))
DS = 1.6   # its blocks a little bigger than life: the tear's 70 blocks long, the hall 50 across


def tex_material(name, meta):
    m = bpy.data.materials.new("k_" + name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(meta["path"], check_existing=True)
    tex.interpolation = "Closest"
    col = tex.outputs[0]
    if meta.get("tint"):
        mul = nt.nodes.new("ShaderNodeMix")
        mul.data_type = "RGBA"
        mul.blend_type = "MULTIPLY"
        mul.inputs[0].default_value = 1.0
        nt.links.new(col, mul.inputs[6])
        mul.inputs[7].default_value = (*meta["tint"], 1)
        col = mul.outputs[2]
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.9
    nt.links.new(col, bsdf.inputs["Base Color"])
    if meta.get("glow"):
        nt.links.new(col, bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = meta["glow"] * 1.5
    sh = bsdf
    if meta.get("alpha"):
        mix = nt.nodes.new("ShaderNodeMixShader")
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        nt.links.new(tex.outputs[1], mix.inputs[0])
        nt.links.new(tr.outputs[0], mix.inputs[1])
        nt.links.new(bsdf.outputs[0], mix.inputs[2])
        sh = mix
    nt.links.new(sh.outputs[0], out.inputs[0])
    return m


with open(os.path.join(STRUCT, "sky_%s_tex.json" % LAIR)) as f:
    meta = json.load(f)
before = set(bpy.data.objects)
bpy.ops.wm.obj_import(filepath=os.path.join(STRUCT, "sky_%s.obj" % LAIR), forward_axis="NEGATIVE_Z", up_axis="Y")
dng = bpy.data.objects.new("dungeon", None)
sc.collection.objects.link(dng)
mats = {}
for o in set(bpy.data.objects) - before:
    if o.type != "MESH":
        continue
    t = o.name.split(".")[0]
    if t in meta:
        mats.setdefault(t, tex_material(t, meta[t]))
        o.data.materials.clear()
        o.data.materials.append(mats[t])
    o.parent = dng
# upright where it stands, far off: a view down its first hall is rendered first, by its own candlelight, and that view
# is what the tear shows (the way the game's gate windows draw a gate's far side into a texture)
dng.matrix_world = Matrix.Translation(OFFSET) @ Matrix.Scale(DS, 4)
bpy.context.view_layer.update()
lamps = []
for k in range(16):
    lp = dng.matrix_world @ Vector((rs.uniform(-18, 18), rs.uniform(2, 42), rs.uniform(1.5, 7)))
    ld = bpy.data.lights.new("dng_lamp", "POINT")
    ld.color = (1.0, 0.66, 0.36)
    ld.energy = 6000 * DS * DS
    ld.shadow_soft_size = 1.0
    lo = bpy.data.objects.new("dng_lamp", ld)
    sc.collection.objects.link(lo)
    lo.location = lp
    lamps.append(lo)
# the dark of the gates' own world round it, where its roof was cut away
bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=300)
bmesh.ops.reverse_faces(bm, faces=bm.faces)
m_dark_world, nt, out = nodes_mat("gate_dark")
em = N(nt, "ShaderNodeEmission")
em.inputs["Color"].default_value = (*tuple(0.015 + c * 0.03 for c in HOT), 1)
em.inputs["Strength"].default_value = 1.0
L(nt, em.outputs[0], out.inputs["Surface"])
backdrop = mesh_obj("gate_dark", bm, m_dark_world)
backdrop.location = OFFSET

HALL = os.path.abspath(os.path.join(OUT, "sky3_hall_%s.png" % LAIR))
if not os.path.exists(HALL) or "rehall" in ARGS:
    hcam = bpy.data.objects.new("hall_cam", bpy.data.cameras.new("hall_cam"))
    sc.collection.objects.link(hcam)
    hcam.data.lens = 15
    hcam.location = dng.matrix_world @ Vector((0, -3, 9))
    hcam.rotation_euler = ((dng.matrix_world @ Vector((0, 26, 0))) - hcam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = hcam
    keep = (sun.data.energy, _bg.inputs["Strength"].default_value, sc.render.resolution_x, sc.render.resolution_y, sc.render.filepath)
    sun.data.energy = 0
    _bg.inputs["Strength"].default_value = 0
    sc.render.resolution_x, sc.render.resolution_y = 1280, 640
    sc.render.filepath = HALL
    ex = sc.view_settings.exposure
    sc.view_settings.exposure = 1.2
    bpy.ops.render.render(write_still=True)
    sc.view_settings.exposure = ex
    print("WROTE", HALL)
    sun.data.energy, _bg.inputs["Strength"].default_value, sc.render.resolution_x, sc.render.resolution_y, sc.render.filepath = keep
for o in lamps:
    o.hide_render = True
HALL_IMG = bpy.data.images.load(HALL, check_existing=True)


def hall_tex(nt, u, v):
    cb = N(nt, "ShaderNodeCombineXYZ")
    L(nt, u, cb.inputs["X"])
    L(nt, v, cb.inputs["Y"])
    im = N(nt, "ShaderNodeTexImage", _extension="EXTEND")
    im.image = HALL_IMG
    L(nt, cb.outputs[0], im.inputs["Vector"])
    return im.outputs["Color"]


# the tear's inside: the hall, its length along the tear's, darkening and burning toward the lips
m_win, nt, out = nodes_mat("window")
d, tc = sdf_node(nt)
sp = N(nt, "ShaderNodeSeparateXYZ")
L(nt, tc.outputs["Object"], sp.inputs[0])
u = math_n(nt, "ADD", math_n(nt, "DIVIDE", sp.outputs["Z"], vb=2 * H * 0.92), vb=0.5)
v = math_n(nt, "ADD", math_n(nt, "MULTIPLY", math_n(nt, "DIVIDE", sp.outputs["X"], vb=2 * 2.4), vb=0.72), vb=0.36)
seen = N(nt, "ShaderNodeEmission")
L(nt, hall_tex(nt, u, v), seen.inputs["Color"])
seen.inputs["Strength"].default_value = 3.0
deep = smooth(nt, d, -0.02, -0.3)
rim = N(nt, "ShaderNodeEmission")
rim.inputs["Color"].default_value = (*tuple(c * 0.5 for c in HOT), 1)
rim.inputs["Strength"].default_value = 2.5
mix = N(nt, "ShaderNodeMixShader")
L(nt, deep, mix.inputs[0])
L(nt, rim.outputs[0], mix.inputs[1])
L(nt, seen.outputs[0], mix.inputs[2])
L(nt, mix.outputs[0], out.inputs["Surface"])
void.data.materials.clear()
void.data.materials.append(m_win)

# ---------------------------------------------------------------- shards: thick dark crystal, burning edges, pieces of the window
m_face, nt, out = nodes_mat("shard_face")
glass = N(nt, "ShaderNodeBsdfPrincipled")
glass.inputs["Base Color"].default_value = (0.02, 0.012, 0.018, 1)
glass.inputs["Metallic"].default_value = 0.0
glass.inputs["Roughness"].default_value = 0.22
if "Coat Weight" in glass.inputs:
    glass.inputs["Coat Weight"].default_value = 0.35
# each a piece of the hall: its face's own coordinates, scaled down, at a place of its own in the view
tcf = N(nt, "ShaderNodeTexCoord")
oi = N(nt, "ShaderNodeObjectInfo")
spf = N(nt, "ShaderNodeSeparateXYZ")
L(nt, tcf.outputs["Generated"], spf.inputs[0])
uu = math_n(nt, "ADD", math_n(nt, "MULTIPLY", spf.outputs["X"], vb=0.32), math_n(nt, "MULTIPLY", oi.outputs["Random"], vb=0.66))
vv = math_n(nt, "ADD", math_n(nt, "MULTIPLY", spf.outputs["Y"], vb=0.3), math_n(nt, "MULTIPLY", math_n(nt, "FRACT", math_n(nt, "MULTIPLY", oi.outputs["Random"], vb=7.3)), vb=0.4))
piece = N(nt, "ShaderNodeEmission")
L(nt, hall_tex(nt, uu, vv), piece.inputs["Color"])
piece.inputs["Strength"].default_value = 4.0
add = N(nt, "ShaderNodeAddShader")
L(nt, glass.outputs[0], add.inputs[0])
L(nt, piece.outputs[0], add.inputs[1])
lw = N(nt, "ShaderNodeLayerWeight")
lw.inputs["Blend"].default_value = 0.35
# square on: the hall in it; at a slant: the dark glass, catching the light
win = math_n(nt, "SUBTRACT", va=1.0, b=lw.outputs["Facing"])
mixf = N(nt, "ShaderNodeMixShader")
L(nt, smooth(nt, win, 0.15, 0.75), mixf.inputs[0])
L(nt, glass.outputs[0], mixf.inputs[1])
L(nt, add.outputs[0], mixf.inputs[2])
L(nt, mixf.outputs[0], out.inputs["Surface"])

m_dark, nt, out = nodes_mat("shard_dark")
g2 = N(nt, "ShaderNodeBsdfPrincipled")
g2.inputs["Base Color"].default_value = (0.02, 0.012, 0.018, 1)
g2.inputs["Metallic"].default_value = 0.0
g2.inputs["Roughness"].default_value = 0.22
L(nt, g2.outputs[0], out.inputs["Surface"])

EDGE = flat_mat("shard_edge", (0, 0, 0), 1.0, tuple(min(1, c * 0.75 + 0.25) for c in HOT), 18.0)


def shard(name, at, size, normal, spin, window=True):
    """A slab of the broken sky: a jagged outline with one long point, thick, its broken edges burning."""
    n = rs.randint(5, 7)
    angs = sorted(rs.uniform(0, 2 * math.pi) for _ in range(n))
    tip = rs.randrange(n)
    pts = []
    for i, ang in enumerate(angs):
        r = size * (rs.uniform(1.5, 2.3) if i == tip else rs.uniform(0.55, 1.0))
        pts.append((math.cos(ang) * r, math.sin(ang) * r * rs.uniform(0.45, 0.75)))
    bm = bmesh.new()
    face = bm.faces.new([bm.verts.new((x, y, 0)) for x, y in pts])
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    th = max(0.2, size * rs.uniform(0.16, 0.26))
    top = [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]
    # the broken face isn't flat: one side tipped, like a break
    for v in top:
        v.co.z = th * rs.uniform(0.75, 1.25)
    bm.normal_update()
    for f in bm.faces:
        f.material_index = 0 if abs(f.normal.z) > 0.8 else 1
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    me.materials.append(m_face if window else m_dark)
    me.materials.append(EDGE)
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    bev = ob.modifiers.new("bevel", "BEVEL")
    bev.width = th * 0.18
    bev.segments = 2
    bev.limit_method = "ANGLE"
    ob.location = at
    q = normal.to_track_quat("Z", "Y")
    ob.rotation_euler = (q.to_matrix().to_4x4() @ Matrix.Rotation(spin[0], 4, "X") @ Matrix.Rotation(spin[1], 4, "Y") @ Matrix.Rotation(spin[2], 4, "Z")).to_euler()
    return ob


def tear_point(u, v):
    return TEAR + ALONG * u * 34 + ACROSS * v * 9


for k in range(18):
    u, side = rs.uniform(-0.9, 0.9), rs.choice((-1, 1))
    at = tear_point(u, side * rs.uniform(0.85, 1.4)) + FACING * rs.uniform(0.5, 3) + Vector((0, 0, -rs.uniform(0, 4)))
    shard("rim", at, rs.uniform(3.0, 6.5), FACING, (rs.uniform(-0.5, 0.5), rs.uniform(-0.5, 0.5), rs.uniform(0, 6.3)))

for k in range(30):
    t = rs.uniform(0.05, 1.0) ** 0.8
    src = tear_point(rs.uniform(-1, 1), rs.uniform(-1.2, 1.2))
    land_at = Vector((rs.uniform(-45, 45), rs.uniform(-25, 60), GROUND))
    at = src.lerp(land_at, t * 0.92)
    size = rs.uniform(1.4, 3.8) * (1.25 - 0.5 * t)
    tumble = 0.4 + 2.5 * t
    shard("fall", at, size, FACING, (rs.uniform(-tumble, tumble), rs.uniform(-tumble, tumble), rs.uniform(0, 6.3)), window=rs.random() < 0.7)

for k in range(8):
    a, dd = rs.uniform(0, 2 * math.pi), rs.uniform(3, 22)
    x, y = int(math.cos(a) * dd), int(math.sin(a) * dd) + 4
    gz = hmap.get((x, y), GROUND)
    size = rs.uniform(1.4, 3.2)
    lean = Vector((rs.uniform(-0.6, 0.6), rs.uniform(-0.6, 0.6), 1)).normalized()
    shard("down", Vector((x + 0.5, y + 0.5, gz + size * 0.8)), size, Vector((lean.x, lean.y, 0.15)).normalized(), (0, 0, rs.uniform(0, 6.3)))
    l = bpy.data.lights.new("down_glow", "POINT")
    l.energy = 1200 * size
    l.color = tuple(min(1, c * 0.7 + 0.3) for c in HOT)
    lo = bpy.data.objects.new("down_glow", l)
    sc.collection.objects.link(lo)
    lo.location = (x + 0.5, y + 0.5, gz + 1.0)

# ---------------------------------------------------------------- shots, bloom, render
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 1200
cam.location = loc
cam.data.lens = lens
cam.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
sc.cycles.max_bounces = 10
sc.cycles.transparent_max_bounces = 12
try:
    ng = bpy.data.node_groups.new("comp", "CompositorNodeTree")
    sc.compositing_node_group = ng
    rl = ng.nodes.new("CompositorNodeRLayers")
    gl = ng.nodes.new("CompositorNodeGlare")
    gl.inputs["Type"].default_value = "Bloom"
    gl.inputs["Quality"].default_value = "High"
    gl.inputs["Threshold"].default_value = 1.4
    gl.inputs["Strength"].default_value = 0.3
    gl.inputs["Size"].default_value = 0.6
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    go = ng.nodes.new("NodeGroupOutput")
    ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
    ng.links.new(gl.outputs["Image"], go.inputs[0])
    sc.render.use_compositing = True
except Exception as ex:
    print("COMP FAIL", ex)
sc.render.image_settings.color_depth = "8"
sc.render.filepath = os.path.abspath(os.path.join(OUT, "sky3_%s_%s.png" % (RANK, SHOT)))
bpy.ops.render.render(write_still=True)
print("WROTE", sc.render.filepath)
