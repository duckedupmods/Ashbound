"""render the portrait poses: low three-quarter camera, transparent background, hard warm key light"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, "E:/Ashbound/tools/blender")
import preview_vox as P  # noqa: E402

OUT = sys.argv[sys.argv.index("--") + 1]
for arg in sys.argv[sys.argv.index("--") + 2:]:
    name, h = arg.split("@")
    h = float(h)
    P.reset()
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = 480, 560
    sun = bpy.data.objects["sun"]
    sun.data.energy = 4.0
    sun.rotation_euler = (math.radians(50), math.radians(-35), math.radians(-40))
    P.load(name, 0)
    P.camera(Vector((0.0, 0.0, 0.55 * h)), 28, -2, dist=14, ortho=1.22 * h)
    P.render(os.path.join(OUT, name.replace("_portrait", "") + ".png"))
