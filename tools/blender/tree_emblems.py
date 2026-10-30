"""The Ash Tree's emblems: real weapon models of the mod (models/mesh/<id>.obj + textures/item/<id>_3d.png) rendered
large on the diagonal, lit warm from the front and cold from behind, on a transparent ground.

    blender -b -P tools/blender/tree_emblems.py -- OUTDIR SIZE id [id ...]   -> OUTDIR/<id>.png
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, "E:/Ashbound/tools/blender")
import preview_vox as P  # noqa: E402

ARGS = sys.argv[sys.argv.index("--") + 1:]
OUTDIR, SIZE, IDS = ARGS[0], int(ARGS[1]), ARGS[2:]
A = "E:/EFTest/game/src/main/resources/assets/ashbound"
os.makedirs(OUTDIR, exist_ok=True)

def ember_heart():
    """the Core's emblem: a lump of coal split by fire from inside"""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=1)
    ob = bpy.context.object
    ob.scale = (0.85, 0.8, 1.15)
    tex = bpy.data.textures.new("lump", "VORONOI")
    tex.noise_scale = 0.5
    d = ob.modifiers.new("lump", "DISPLACE")
    d.texture = tex
    d.strength = 0.25
    bpy.ops.object.shade_smooth()
    m = bpy.data.materials.new("coal")
    m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (0.03, 0.025, 0.022, 1)
    b.inputs["Roughness"].default_value = 0.6
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.feature = "DISTANCE_TO_EDGE"
    vor.inputs["Scale"].default_value = 3.2
    ramp = nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["From Min"].default_value = 0.06
    ramp.inputs["From Max"].default_value = 0.0
    ramp.inputs["To Max"].default_value = 4.0
    nt.links.new(vor.outputs["Distance"], ramp.inputs["Value"])
    b.inputs["Emission Color"].default_value = (1.0, 0.22, 0.02, 1)
    nt.links.new(ramp.outputs["Result"], b.inputs["Emission Strength"])
    ob.data.materials.append(m)
    return ob


for item in IDS:
    P.reset()
    sc = bpy.context.scene
    sc.render.resolution_x = sc.render.resolution_y = SIZE
    sc.render.film_transparent = True
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    if item == "core":
        obs = [ember_heart()]
    else:
        bpy.ops.wm.obj_import(filepath=f"{A}/models/mesh/{item}.obj", use_split_groups=True, forward_axis="Y", up_axis="Z")
        obs = list(bpy.context.selected_objects)
        img = f"{A}/textures/item/{item}_3d.png"
        mats = {True: P.material(img, True), False: P.material(img, False)}
        for o in obs:
            glow = "fire" in o.name or "glow" in o.name
            o.data.materials.clear()
            o.data.materials.append(mats[glow])
    # centre it, its longest side on the diagonal (grip bottom left, tip top right), turned so its edge shows
    pts = [o.matrix_world @ v.co for o in obs for v in o.data.vertices]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    mid, size = (lo + hi) / 2, hi - lo
    long_axis = max(range(3), key=lambda i: size[i])
    # bring the long axis to Blender Z (up), then lay it on the diagonal in the camera plane (x/z)
    to_up = {0: Matrix.Rotation(math.radians(90), 4, "Y"), 1: Matrix.Rotation(math.radians(-90), 4, "X"), 2: Matrix()}[long_axis]
    M = Matrix.Rotation(math.radians(-135), 4, "Y") @ Matrix.Rotation(math.radians(20), 4, "Z") @ to_up @ Matrix.Translation(-mid)
    for o in obs:
        o.matrix_world = M @ o.matrix_world
    pts = [o.matrix_world @ v.co for o in obs for v in o.data.vertices]
    span = max(max(p.x for p in pts) - min(p.x for p in pts), max(p.z for p in pts) - min(p.z for p in pts))
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = span * 1.08
    cx = (max(p.x for p in pts) + min(p.x for p in pts)) / 2
    cz = (max(p.z for p in pts) + min(p.z for p in pts)) / 2
    cam.location = (cx, -10, cz)
    cam.rotation_euler = (math.radians(90), 0, 0)
    P.render(f"{OUTDIR}/{item}.png")
print("done")
