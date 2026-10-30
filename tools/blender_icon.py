"""Renders one chunky model for its inventory icon, lit like Ashbound's other weapon icons (preview_vox's
light and materials), seen from yaw/pitch degrees and fitted to the frame, or framed on the item's 16x16
square when a fixed frame is asked for (so a bow's draw stages line up).

    blender -b -P tools/blender_icon.py -- NAME YAW PITCH OUT.png [fixed]
"""
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, 'E:/Ashbound/tools/blender')
import preview_vox as P  # noqa: E402


def main():
    args = sys.argv[sys.argv.index('--') + 1:]
    name, yaw, pitch, out = args[0], float(args[1]), float(args[2]), args[3]
    fixed = 'fixed' in args[4:]
    P.reset()
    root = P.load(name, 0)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in root.children for c in o.bound_box]
    centre = sum(pts, Vector()) / len(pts)
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
    P.render(out)


main()
