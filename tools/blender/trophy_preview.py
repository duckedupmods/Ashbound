"""Trophy previews (tools/trophies.py preview): each trophy alone, three-quarter, on transparent ground, warm key light."""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, "E:/Ashbound/tools/blender")
import preview_vox as P  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
for name in args[1:]:
    P.reset()
    sc = bpy.context.scene
    sc.render.resolution_x = sc.render.resolution_y = 480
    sun = bpy.data.objects["sun"]
    sun.data.energy = 3.6
    sun.rotation_euler = (math.radians(50), math.radians(-30), math.radians(-35))
    P.load(name, 0)
    # one block = 16 model pixels = 1 Blender unit after the importer's scale? measure it
    objs = [o for o in bpy.data.objects if o.type == "MESH"]
    lo = Vector((min(min((o.matrix_world @ Vector(c)).x for c in o.bound_box) for o in objs),
                 min(min((o.matrix_world @ Vector(c)).y for c in o.bound_box) for o in objs),
                 min(min((o.matrix_world @ Vector(c)).z for c in o.bound_box) for o in objs)))
    hi = Vector((max(max((o.matrix_world @ Vector(c)).x for c in o.bound_box) for o in objs),
                 max(max((o.matrix_world @ Vector(c)).y for c in o.bound_box) for o in objs),
                 max(max((o.matrix_world @ Vector(c)).z for c in o.bound_box) for o in objs)))
    mid = (lo + hi) / 2
    size = max(hi - lo)
    P.camera(mid, 30, 18, dist=size * 6 + 4, ortho=size * 1.35)
    P.render(os.path.join(OUT, name + ".png"))
