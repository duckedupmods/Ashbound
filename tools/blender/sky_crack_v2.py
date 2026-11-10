"""The sky cracks (concept, Cycles): a wild gate tearing open high over the land. The rift from gate_rift.py, grown to
some seventy blocks and laid across the sky, its burning lips and black depth over everything, the air round it
shattered; a column of its light down to a crater, and burning things falling out of it with trails behind them.
  blender -b -P tools/blender/sky_crack.py -- <rank> [wide|under|far] [fast]  ->  tools/renders/gate/sky_<rank>_<shot>.png"""
import os, math, random
import bpy, bmesh
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "gate_rift.py"), encoding="utf-8").read()
_before = set()
exec(_src.split("# ---------------------------------------------------------------- shots, bloom, render")[0])

rs = random.Random(91 + RI)
BASE = {"ground_near", "ground_far", "trunks", "leaves"}
rift = [o for o in sc.objects if o.type == "MESH" and o.name not in BASE]
print("RIFT", [o.name for o in rift])

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
# lying nearly along the horizon, a little askew, and its face turned down toward whoever's under it
hub.rotation_euler = (math.radians(28), math.radians(70), 0)
# what's torn loose of the gate's world: rocks, not boxes the size of houses
for o in rift:
    if o.name.startswith("chunk"):
        o.scale = tuple(v * 0.45 for v in o.scale)
for o in sc.objects:
    if o.type == "LIGHT" and o.name.startswith("gate_"):
        o.location = SKY + (o.location - Vector((0, Y0, C))) * GROW
        o.data.energy *= GROW * GROW * 0.6
        if o.data.type in ("POINT", "SPOT", "AREA"):
            o.data.shadow_soft_size = max(getattr(o.data, "shadow_soft_size", 1), 6)

# night coming on: the crack is the light
_bg.inputs["Strength"].default_value = 0.035
sun.data.energy = 0.35

# ---------------------------------------------------------------- the land beyond the voxel ground, dark hills to the horizon
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=160, y_segments=160, size=420)
for v in bm.verts:
    x, y = v.co.x, v.co.y
    d = math.hypot(x, y - 10)
    hills = math.sin(x * 0.021) * 6 + math.cos(y * 0.017 + 1.3) * 7 + math.sin((x + y) * 0.009) * 12
    v.co.z = GROUND - 2.6 + (max(0, d - 60) / 140) ** 1.3 * (8 + hills)
far_land = mesh_obj("far_land", bm, grass_mat(False))

# ---------------------------------------------------------------- the column of its light, down to a crater
def glow_volume(name, colour, density, emit):
    m, nt, out = nodes_mat(name)
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (*colour, 1)
    vol.inputs["Density"].default_value = density
    vol.inputs["Emission Strength"].default_value = emit
    vol.inputs["Emission Color"].default_value = (*colour, 1)
    nt.links.new(vol.outputs[0], out.inputs["Volume"])
    return m


top, foot = SKY + Vector((0, 0, -4)), Vector((0, 0, GROUND))
axis = top - foot
col = bpy.data.meshes.new("pillar")
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=2.2, radius2=5.5, depth=axis.length)
bm.to_mesh(col)
pillar = bpy.data.objects.new("pillar", col)
# (a column of light read as a solid tube: the glow on the ground says it instead)
land = bpy.data.lights.new("impact", "POINT")
land.energy = 60000
land.color = tuple(min(1, c * 0.7 + 0.3) for c in HOT)
land.shadow_soft_size = 3
li = bpy.data.objects.new("impact", land)
sc.collection.objects.link(li)
li.location = foot + Vector((0, 0, 2.5))

# ---------------------------------------------------------------- the sky's own glass, breaking off and falling
# each shard: a jagged sliver of the broken sky, its faces dark mirror (they catch the tear's light), its broken edges
# burning like the tear's lips. Big ones breaking off the rim, smaller ones tumbling down, a few already in the ground.
bpy.context.view_layer.update()
rot = hub.matrix_world.to_3x3().normalized()
ALONG = (rot @ Vector((0, 0, 1))).normalized()     # the tear's length
ACROSS = (rot @ Vector((1, 0, 0))).normalized()    # its width
FACING = (rot @ Vector((0, -1, 0))).normalized()   # where it looks
TEAR = next(o for o in rift if o.name == "void").matrix_world.translation.copy()   # its middle, where it really hangs


def glass_mat():
    m, nt, out = nodes_mat("sky_glass")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bs.inputs["Base Color"].default_value = (0.012, 0.01, 0.014, 1)
    bs.inputs["Metallic"].default_value = 0.85
    bs.inputs["Roughness"].default_value = 0.06
    # a faint ember of the void deep in the glass
    bs.inputs["Emission Color"].default_value = (*tuple(c * 0.5 for c in HOT), 1)
    bs.inputs["Emission Strength"].default_value = 0.25
    nt.links.new(bs.outputs[0], out.inputs["Surface"])
    return m


GLASS = glass_mat()
EDGE = flat_mat("shard_edge", (0, 0, 0), 1.0, tuple(min(1, c * 0.7 + 0.3) for c in HOT), 14.0)


def shard(name, at, size, normal, spin):
    """One sliver: a jagged outline with one long point, a little thickness, mirror faces, burning edges."""
    n = rs.randint(4, 6)
    angs = sorted(rs.uniform(0, 2 * math.pi) for _ in range(n))
    tip = rs.randrange(n)
    pts = []
    for i, ang in enumerate(angs):
        r = size * (rs.uniform(1.6, 2.6) if i == tip else rs.uniform(0.35, 1.0))
        pts.append((math.cos(ang) * r, math.sin(ang) * r * rs.uniform(0.35, 0.7)))
    bm = bmesh.new()
    face = bm.faces.new([bm.verts.new((x, y, 0)) for x, y in pts])
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    th = max(0.06, size * rs.uniform(0.05, 0.1))
    bmesh.ops.translate(bm, verts=[e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)], vec=(0, 0, th))
    bm.normal_update()
    for f in bm.faces:
        f.material_index = 0 if abs(f.normal.z) > 0.9 else 1
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    me.materials.append(GLASS)
    me.materials.append(EDGE)
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    ob.location = at
    q = normal.to_track_quat("Z", "Y")
    ob.rotation_euler = (q.to_matrix().to_4x4() @ Matrix.Rotation(spin[0], 4, "X") @ Matrix.Rotation(spin[1], 4, "Y") @ Matrix.Rotation(spin[2], 4, "Z")).to_euler()
    return ob


def tear_point(u, v):
    """A point on the tear's plane: u along its length (-1..1), v across it (-1..1)."""
    return TEAR + ALONG * u * 34 + ACROSS * v * 9


# breaking off the rim: big, still nearly in the tear's plane
for k in range(22):
    u, side = rs.uniform(-0.9, 0.9), rs.choice((-1, 1))
    at = tear_point(u, side * rs.uniform(0.8, 1.4)) + FACING * rs.uniform(0.5, 3) + Vector((0, 0, -rs.uniform(0, 4)))
    shard("rim", at, rs.uniform(3.5, 8.0), FACING, (rs.uniform(-0.5, 0.5), rs.uniform(-0.5, 0.5), rs.uniform(0, 6.3)))

# falling: tumbling more the further they've come, smaller the further from the tear
for k in range(40):
    t = rs.uniform(0.04, 1.0) ** 0.8
    src = tear_point(rs.uniform(-1, 1), rs.uniform(-1.2, 1.2))
    land_at = Vector((rs.uniform(-45, 45), rs.uniform(-25, 60), GROUND))
    at = src.lerp(land_at, t * 0.92)
    size = rs.uniform(1.4, 4.5) * (1.25 - 0.5 * t)
    tumble = 0.4 + 2.5 * t
    shard("fall", at, size, FACING, (rs.uniform(-tumble, tumble), rs.uniform(-tumble, tumble), rs.uniform(0, 6.3)))

# already down: driven into the ground at an angle, burning where they broke
for k in range(9):
    a, d = rs.uniform(0, 2 * math.pi), rs.uniform(2, 22)
    x, y = int(math.cos(a) * d), int(math.sin(a) * d) + 4
    gz = hmap.get((x, y), GROUND)
    size = rs.uniform(1.2, 3.2)
    lean = Vector((rs.uniform(-0.6, 0.6), rs.uniform(-0.6, 0.6), 1)).normalized()
    ob = shard("down", Vector((x + 0.5, y + 0.5, gz + size * 0.8)), size, Vector((lean.x, lean.y, 0.15)).normalized(), (0, 0, rs.uniform(0, 6.3)))
    l = bpy.data.lights.new("down_glow", "POINT")
    l.energy = 1500 * size
    l.color = tuple(min(1, c * 0.7 + 0.3) for c in HOT)
    lo = bpy.data.objects.new("down_glow", l)
    sc.collection.objects.link(lo)
    lo.location = (x + 0.5, y + 0.5, gz + 1.0)

# ---------------------------------------------------------------- shots, bloom, render
SHOTS = {
    "wide": ((-14, -62, GROUND + 4), tuple(TEAR + Vector((-8, 0, -18))), 20),
    "under": ((TEAR.x + 6, TEAR.y - 34, GROUND + 2), tuple(TEAR + Vector((0, 0, -6))), 16),
    "far": ((-60, -170, GROUND + 18), (0, 10, 30), 30),
}
loc, aim, lens = SHOTS.get(SHOT, SHOTS["wide"])
if "probe" in ARGS:
    bpy.context.view_layer.update()
    for o in sc.objects:
        if o.type == "MESH":
            dims = max(o.dimensions)
            if dims > 25 or (o.matrix_world.translation - Vector(loc)).length < 20:
                print("BIG", o.name, o.parent.name if o.parent else "-", tuple(round(c, 1) for c in o.location), round(dims, 1), tuple(round(c, 1) for c in o.matrix_world.translation))
    raise SystemExit
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 1200
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
    gl.inputs["Threshold"].default_value = 1.6
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
sc.render.filepath = os.path.abspath(os.path.join(OUT, "sky_%s_%s.png" % (RANK, SHOT)))
bpy.ops.render.render(write_still=True)
print("WROTE", sc.render.filepath)
