"""Concept shots of tools/curios.py's curios and relics: each mesh turned a little (rings tipped back so the band reads
as a ring), framed to fill the picture, on a transparent ground.

    blender -b -P tools/blender/curio_shots.py -- BATCH.json     -> <out>/shot_<id>.png
"""
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, "E:/Ashbound/tools/blender")
import preview_vox as P  # noqa: E402

spec = json.load(open(sys.argv[sys.argv.index("--") + 1]))
RES, MESH, OUT = spec["res"], spec["mesh"], spec["out"]
# Minecraft (x right, y up, z towards the viewer) into Blender (x right, z up, -y towards the viewer)
C = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
POSE = {"ring": (-24, 38), "amulet": (-22, 8), "charm": (-28, 12), "relic": (-30, 12)}   # yaw, tip back (deg)

for iid, slot in spec["items"]:
    P.reset()
    sc = bpy.context.scene
    sc.render.resolution_x = sc.render.resolution_y = RES
    sc.render.film_transparent = True
    bpy.ops.wm.obj_import(filepath=os.path.join(MESH, "%s.obj" % iid), use_split_groups=True, forward_axis="Y", up_axis="Z")
    obs = list(bpy.context.selected_objects)
    img = os.path.join(MESH, "%s_3d.png" % iid)
    mats = {True: P.material(img, True), False: P.material(img, False)}
    pts = [o.matrix_world @ v.co for o in obs for v in o.data.vertices]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    yaw, tip = POSE[slot]
    R = Matrix.Rotation(math.radians(tip), 4, "X") @ Matrix.Rotation(math.radians(yaw), 4, "Y")
    M = C @ R @ Matrix.Translation(-(lo + hi) / 2)
    for o in obs:
        glow = "fire" in o.name or "glow" in o.name
        o.data.materials.clear()
        o.data.materials.append(mats[glow])
        o.matrix_world = M @ o.matrix_world
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ v.co for o in obs for v in o.data.vertices]
    xs, zs = [p.x for p in pts], [p.z for p in pts]
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max(max(xs) - min(xs), max(zs) - min(zs)) * 1.12
    cam.location = ((max(xs) + min(xs)) / 2, -10, (max(zs) + min(zs)) / 2)
    cam.rotation_euler = (math.radians(90), 0, 0)
    P.render(os.path.join(OUT, "shot_%s.png" % iid))
print("done")
