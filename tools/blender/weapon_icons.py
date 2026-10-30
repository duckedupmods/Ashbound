"""Menu icons for a batch of chunky weapons (tools/weaponforge.py), in one Blender run: each loaded from the
preview folder, laid on the classic diagonal (melee) or turned a little (shields), or framed on the item square
(bows, so the draw stages line up), lit like Ashbound's other weapon icons, 256 px.

    blender -b -P tools/blender/weapon_icons.py -- BATCH.json      -> E:/Ashbound/tools/renders/vox/icon_<name>_big.png"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, 'E:/Ashbound/tools/blender')
import preview_vox as P  # noqa: E402

batch = json.load(open(sys.argv[sys.argv.index('--') + 1]))
for name, yaw, pitch, fixed, diagonal, _offset in batch:
    P.reset()
    bpy.context.scene.render.resolution_x = bpy.context.scene.render.resolution_y = 256
    root = P.load(name, 0)
    if diagonal:
        root.rotation_euler = (0, math.radians(-45), 0)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in root.children for c in o.bound_box]
    if fixed:
        P.camera(Vector((0.5, -0.5, 0.5)), yaw, pitch, ortho=1.0)
    else:
        lo = Vector([min(p[i] for p in pts) for i in range(3)])
        hi = Vector([max(p[i] for p in pts) for i in range(3)])
        centre = (lo + hi) / 2
        P.camera(centre, yaw, pitch, ortho=1.0)
        cam = bpy.data.objects['cam']
        bpy.context.view_layer.update()
        right, up = cam.matrix_world.to_3x3().col[0], cam.matrix_world.to_3x3().col[1]
        xs = [(p - centre).dot(right) for p in pts]
        ys = [(p - centre).dot(up) for p in pts]
        shift = right * (max(xs) + min(xs)) / 2 + up * (max(ys) + min(ys)) / 2
        P.camera(centre + shift, yaw, pitch, ortho=max(max(xs) - min(xs), max(ys) - min(ys)) * 1.04)
    P.render(os.path.join(P.VOX, 'icon_%s_big.png' % name))
    print('icon', name)
