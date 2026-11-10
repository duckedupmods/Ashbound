"""Inventory icons for the armour pieces, rendered from the very meshes Epic Fight draws (the ones tools/efarmor.py
wrote): each piece on its own, turned a little towards the light, at icon size with hard edges so no soft halo
sits round it. `python tools/efarmor.py icons` then outlines them.

  blender -b -P tools/blender/armor_icons.py -- [sets...]     -> tools/renders/icons/<item>.png"""
import json, math, os, sys
import bpy
from mathutils import Vector

GAME = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
A = os.path.join(GAME, "src/main/resources/assets/ashbound")
OUT = os.path.join(GAME, "tools/renders/icons")
sys.path.insert(0, os.path.join(GAME, "tools"))
import efarmor  # noqa: E402

SIZE = int(os.environ.get("ICON_SIZE", 64))          # tools/pixicons.py brings it down to 32 as pixel art
YAW, PITCH = math.radians(28), math.radians(14)    # the piece turned to show its front and one side, seen a little from above


def material(set_name):
    m = bpy.data.materials.new(set_name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(A, "textures/models/armor/%s_layer_1.png" % set_name))
    tex.interpolation = "Closest"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.8
    return m


LININGS = json.load(open(os.path.join(OUT, "linings.json")))
OUT = os.environ.get("ICON_OUT", OUT)


def piece(path, mat, lining, spread=0.0):
    """the piece without its plain lining (it would hide the piece's own shape), robe skirts kept"""
    d = json.load(open(path))["vertices"]
    sx, sy = lining
    P, U = d["positions"]["array"], d["uvs"]["array"]
    # leggings and boots: the two legs drawn a little apart so the icon reads as a pair, each vertex going with
    # the leg whose joints it follows
    side, k = [], 0
    for c in d["vcounts"]["array"]:
        js = [efarmor.JOINTS[d["vindices"]["array"][k + 2 * m]] for m in range(c)]
        k += 2 * c
        side.append(1 if any(j.endswith("_R") for j in js) else -1 if any(j.endswith("_L") for j in js) else 0)
    verts = [Vector((P[3 * n] + spread * side[n], P[3 * n + 1], P[3 * n + 2])) for n in range(len(P) // 3)]
    faces, uvs = [], []
    for part in d["parts"].values():
        a = part["array"]
        for t in range(0, len(a), 9):
            uv = [(U[2 * a[t + o]] * 256, U[2 * a[t + o] + 1] * 256) for o in (1, 4, 7)]
            if all(sx - 0.01 <= u <= sx + efarmor.SW + 0.01 and sy - 0.01 <= v <= sy + efarmor.SW + 0.01 for u, v in uv):
                continue
            faces.append((a[t], a[t + 3], a[t + 6]))
            uvs.append([(U[2 * a[t + o]], 1 - U[2 * a[t + o] + 1]) for o in (1, 4, 7)])
    me = bpy.data.meshes.new(os.path.basename(path))
    used = sorted({i for f in faces for i in f})
    remap = {i: k for k, i in enumerate(used)}
    verts = [verts[i] for i in used]
    faces = [tuple(remap[i] for i in f) for f in faces]
    me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new()
    for f, poly in enumerate(me.polygons):
        for li, l in enumerate(poly.loop_indices):
            uv.data[l].uv = uvs[f][li]
    me.materials.append(mat)
    ob = bpy.data.objects.new(me.name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob, verts


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sc.eevee.taa_render_samples = 1                     # one sample: hard pixel edges, nothing half see-through
sc.render.filter_size = 0.0
sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = SIZE
sc.view_settings.view_transform = "Standard"         # the sheet's own colours, not a film curve
sc.world = bpy.data.worlds.new("w")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.6, 0.64, 1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value = 1.3
sc.view_settings.exposure = 0.5
for rot, e in (((40, 0, -35), 3.4), ((75, 0, 150), 0.8)):
    L = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    L.data.energy = e
    L.rotation_euler = [math.radians(a) for a in rot]
    sc.collection.objects.link(L)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cam.data.type = "ORTHO"
sc.collection.objects.link(cam)
sc.camera = cam

only = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
os.makedirs(OUT, exist_ok=True)
for name, _, _, _, items in efarmor.SETS:
    if only and name not in only:
        continue
    mat = material(name)
    for slot, it in enumerate(items):
        item = "%s_%s" % (name, it)
        legs = slot >= 2
        YAW, PITCH = math.radians(10 if legs else 28), math.radians(8 if legs else 14)
        if "ICON_OUT" in os.environ:
            YAW, PITCH = math.radians(16), math.radians(10)     # the reference to draw from: nearly front on
        ob, verts = piece(os.path.join(A, "animmodels/armor/%s.json" % item), mat, LININGS[name], 0.13 if legs else 0.0)
        # Epic Fight's frame faces +y; look back at the front from in front, off to one side and a little above
        d = Vector((math.sin(YAW) * math.cos(PITCH), math.cos(YAW) * math.cos(PITCH), math.sin(PITCH)))
        c = sum(verts, Vector()) / len(verts)
        lo, hi = Vector([min(v[i] for v in verts) for i in range(3)]), Vector([max(v[i] for v in verts) for i in range(3)])
        c = (lo + hi) / 2
        cam.location = c + d * 6
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        right = Vector((math.cos(YAW), -math.sin(YAW), 0))
        up = d.cross(right).normalized() * -1
        corners = [Vector((x, y, z)) for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]
        w = max(abs((p - c).dot(right)) for p in corners) * 2
        h = max(abs((p - c).dot(up)) for p in corners) * 2
        cam.data.ortho_scale = max(w, h) * 1.06
        sc.render.filepath = os.path.join(OUT, item + ".png")
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(ob)
        print("icon", item)
