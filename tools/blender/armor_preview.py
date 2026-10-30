"""Renders the armour sets exactly as Epic Fight will skin them (the meshes tools/efarmor.py wrote), on a grey
stand-in body: each set standing, and below it bent at the elbows and knees the way Epic Fight bends the joints,
to catch pieces that tear or float.

  blender -b -P tools/blender/armor_preview.py -- [sets...]     -> tools/renders/armor_sets.png"""
import json, math, os, sys
import bpy
from mathutils import Matrix, Vector

GAME = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
A = os.path.join(GAME, "src/main/resources/assets/ashbound")
sys.path.insert(0, os.path.join(GAME, "tools"))
import efarmor  # noqa: E402

JOINTS = efarmor.JOINTS
# where Epic Fight bends: the elbow and knee pivots (x right, y forward, z up), and how far for the bent row
BEND = {"Hand_R": (Vector((0.375, 0, 1.125)), 70), "Hand_L": (Vector((-0.375, 0, 1.125)), 70),
        "Leg_R": (Vector((0.125, 0, 0.375)), -60), "Leg_L": (Vector((-0.125, 0, 0.375)), -60),
        "Thigh_R": (Vector((0.125, 0, 0.75)), 35), "Thigh_L": (Vector((-0.125, 0, 0.75)), 35),
        "Arm_R": (Vector((0.375, 0, 1.375)), 25), "Arm_L": (Vector((-0.375, 0, 1.375)), 25)}
CHAIN = {"Hand_R": ["Arm_R"], "Hand_L": ["Arm_L"], "Leg_R": ["Thigh_R"], "Leg_L": ["Thigh_L"]}

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene


SWING = {"Arm_R": (Vector((0.375, 0, 1.375)), 75), "Arm_L": (Vector((-0.375, 0, 1.375)), -60),
         "Thigh_R": (Vector((0.125, 0, 0.75)), -30), "Thigh_L": (Vector((-0.125, 0, 0.75)), 30)}
SCHAIN = {"Hand_R": "Arm_R", "Hand_L": "Arm_L", "Leg_R": "Thigh_R", "Leg_L": "Thigh_L"}


def joint_full(j, bent):
    if bent == "swing":
        k = SCHAIN.get(j, j)
        if k not in SWING:
            return Matrix.Identity(4)
        p, a = SWING[k]
        return Matrix.Translation(p) @ Matrix.Rotation(math.radians(a), 4, "X") @ Matrix.Translation(-p)
    if not bent:
        return Matrix.Identity(4)
    m = Matrix.Identity(4)
    if j in BEND:
        p, a = BEND[j]
        m = Matrix.Translation(p) @ Matrix.Rotation(math.radians(a), 4, "X") @ Matrix.Translation(-p)
    for par in CHAIN.get(j, []):
        p, a = BEND[par]
        m = Matrix.Translation(p) @ Matrix.Rotation(math.radians(a), 4, "X") @ Matrix.Translation(-p) @ m
    return m


def texture(set_name):
    m = bpy.data.materials.new(set_name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(A, "textures/models/armor/%s_layer_1.png" % set_name))
    tex.interpolation = "Closest"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    bsdf.inputs["Roughness"].default_value = 0.7
    return m


def piece(path, mat, at, bent):
    d = json.load(open(path))["vertices"]
    P = d["positions"]["array"]
    U = d["uvs"]["array"]
    vc = d["vcounts"]["array"]
    vi = d["vindices"]["array"]
    W = d["weights"]["array"]
    verts, k = [], 0
    for n, c in enumerate(vc):
        p = Vector(P[3 * n:3 * n + 3])
        q = Vector((0, 0, 0))
        for m in range(c):
            j, w = JOINTS[vi[k]], W[vi[k + 1]]
            k += 2
            q += (joint_full(j, bent) @ p) * w
        verts.append(q + at)
    faces, uvs = [], []
    for part in d["parts"].values():
        a = part["array"]
        for t in range(0, len(a), 9):
            faces.append((a[t], a[t + 3], a[t + 6]))
            uvs.append([(U[2 * a[t + o]], 1 - U[2 * a[t + o] + 1]) for o in (1, 4, 7)])
    me = bpy.data.meshes.new(os.path.basename(path))
    me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new()
    for f, poly in enumerate(me.polygons):
        for li, l in enumerate(poly.loop_indices):
            uv.data[l].uv = uvs[f][li]
    me.materials.append(mat)
    ob = bpy.data.objects.new(me.name, me)
    sc.collection.objects.link(ob)


def body(at, bent, mat):
    """a vanilla-sized player in grey boxes, bent with the same joints"""
    parts = [((-0.25, -0.25, 1.5), (0.25, 0.25, 2.0), "Head"), ((-0.25, -0.125, 0.75), (0.25, 0.125, 1.5), "Chest"),
             ((0.25, -0.125, 1.125), (0.5, 0.125, 1.5), "Arm_R"), ((0.25, -0.125, 0.75), (0.5, 0.125, 1.125), "Hand_R"),
             ((-0.5, -0.125, 1.125), (-0.25, 0.125, 1.5), "Arm_L"), ((-0.5, -0.125, 0.75), (-0.25, 0.125, 1.125), "Hand_L"),
             ((0.0, -0.125, 0.375), (0.25, 0.125, 0.75), "Thigh_R"), ((0.0, -0.125, 0.0), (0.25, 0.125, 0.375), "Leg_R"),
             ((-0.25, -0.125, 0.375), (0.0, 0.125, 0.75), "Thigh_L"), ((-0.25, -0.125, 0.0), (0.0, 0.125, 0.375), "Leg_L")]
    for lo, hi, j in parts:
        vs = [Vector((x, y, z)) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
        vs = [joint_full(j, bent) @ v + at for v in vs]
        me = bpy.data.meshes.new("body")
        me.from_pydata(vs, [], [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)])
        me.materials.append(mat)
        ob = bpy.data.objects.new("body", me)
        sc.collection.objects.link(ob)


grey = bpy.data.materials.new("skin")
grey.use_nodes = True
next(n for n in grey.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = (0.32, 0.32, 0.34, 1)

only = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
sets = [s for s in efarmor.SETS if not only or s[0] in only]
GAP = 1.6
YAW = float(os.environ.get("YAW", 25))
for i, (name, _, _, _, items) in enumerate(sets):
    mat = texture(name)
    for row, bent in ((0, False), (1, True), (2, "swing")):
        at = Vector((-i * GAP, 0, -row * 2.6))
        body(at, bent, grey)
        for it in items:
            piece(os.path.join(A, "animmodels/armor/%s_%s.json" % (name, it)), mat, at, bent)

w = (len(sets) - 1) * GAP
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
cam.data.type = "ORTHO"
cam.data.ortho_scale = max(w + 1.9, 8.4)
cam.data.shift_y = 0.0
cam.location = (-w / 2 - 9 * math.sin(math.radians(YAW)), 9 * math.cos(math.radians(YAW)), -1.6)
cam.rotation_euler = (math.radians(90), 0, math.radians(180 + YAW))
sc.camera = cam
for rot, e in (((50, 0, 160), 3.5), ((70, 0, -30), 1.2)):
    L = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    L.data.energy = e
    L.rotation_euler = [math.radians(a) for a in rot]
    sc.collection.objects.link(L)
sc.world = bpy.data.worlds.new("w")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.05, 0.06, 1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 2400, int(2400 * 8.4 / max(w + 1.9, 8.4))
sc.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in bpy.types.ColorManagedViewSettings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
sc.render.filepath = os.path.join(GAME, "tools/renders/armor_sets.png")
bpy.ops.render.render(write_still=True)
print("wrote", sc.render.filepath)
