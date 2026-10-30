"""Concept of the curios worn on a player (client/WornCurios.java): a Minecraft body in pixels with the amulet lying on
the chest, a ring round each fist, the charm strapped to the outside of the right thigh, the relic the left.

    blender -b -P tools/blender/curio_worn.py -- JOB.json     -> <out>/worn_<view>.png
JOB: {"res", "out", "pieces": [{"obj", "png", "slot", "scale", "index"}]}
"""
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, "E:/Ashbound/tools/blender")
import preview_vox as P  # noqa: E402

job = json.load(open(sys.argv[sys.argv.index("--") + 1]))
P.RES = job["res"]
P.reset()
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = job["res"], int(job["res"] * 1.25)
# Minecraft pixels (x the body's left, y up, z out of the chest) into Blender (x, z up, -y out of the chest)
C = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


def flat(name, rgb):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = 0.95
    return m


def box(x0, y0, z0, x1, y1, z1, mat):
    bpy.ops.mesh.primitive_cube_add()
    o = bpy.context.active_object
    o.scale = ((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2)
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    bpy.ops.object.transform_apply(location=True, scale=True)
    o.matrix_world = C @ o.matrix_world
    o.data.materials.append(mat)


skin, shirt, pants, boots, hair = (flat("skin", (0.36, 0.2, 0.12)), flat("shirt", (0.55, 0.68, 0.66)),
                                   flat("pants", (0.17, 0.08, 0.13)), flat("boots", (0.03, 0.03, 0.03)), flat("hair", (0.45, 0.32, 0.55)))
box(-4, 24, -4, 4, 32, 4, skin)
box(-4.2, 28, -4.2, 4.2, 32.2, 4.2, hair)
box(-4, 12, -2, 4, 24, 2, shirt)
for sx in (-1, 1):
    box(sx * 4, 16, -2, sx * 8, 24, 2, shirt) if sx > 0 else box(-8, 16, -2, -4, 24, 2, shirt)
    box(min(sx * 4, sx * 8), 12, -2, max(sx * 4, sx * 8), 16, 2, skin)
    box(min(0, sx * 4), 3, -2, max(0, sx * 4), 12, 2, pants)
    box(min(0, sx * 4), 0, -2, max(0, sx * 4), 3, 2, boots)


def to_px(v):
    """item space (voxsword.to_item) back to model pixels"""
    return Vector(((v.x - 0.5) * 16, (v.y - 6.25 / 16) * 16 + 0.8, (v.z - 0.5) * 16))


def place(piece):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.obj_import(filepath=piece["obj"], use_split_groups=True, forward_axis="Y", up_axis="Z")
    obs = list(bpy.context.selected_objects)
    mats = {True: P.material(piece["png"], True), False: P.material(piece["png"], False)}
    for o in obs:
        o.data.materials.clear()
        o.data.materials.append(mats["fire" in o.name or "glow" in o.name])
        for v in o.data.vertices:
            v.co = to_px(o.matrix_world @ v.co)
        o.matrix_world = Matrix.Identity(4)
    pts = [v.co for o in obs for v in o.data.vertices]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    k, slot = piece["scale"], piece["slot"]
    S = Matrix.Scale(k, 4)
    if slot == "amulet":     # the bail on the chest's upper middle, the chain up under the head
        M = Matrix.Translation((0, 24 - 4.0, 2.35)) @ S
    elif slot == "ring":     # the band round the fist, its setting to the front
        x = -6 if piece["index"] == 0 else 6
        M = Matrix.Translation((x, 12.9, 0)) @ Matrix.Rotation(math.radians(90), 4, "X") @ S
    elif slot == "charm":    # strapped to the outside of the right thigh, facing out (it swings with the leg)
        top = Vector(((lo.x + hi.x) / 2, hi.y, (lo.z + hi.z) / 2))
        M = (Matrix.Translation((-4.0 - (hi.z - lo.z) * k / 2 - 0.1, 11.8, 0)) @ Matrix.Rotation(math.radians(-90), 4, "Y")
             @ S @ Matrix.Translation(-top))
    else:                    # the relic on the belt at the outer left hip, facing out, just below the hand
        top = Vector(((lo.x + hi.x) / 2, hi.y, (lo.z + hi.z) / 2))
        M = (Matrix.Translation((4.0 + (hi.z - lo.z) * k / 2 + 0.1, 11.4, -0.3)) @ Matrix.Rotation(math.radians(90), 4, "Y")
             @ S @ Matrix.Translation(-top))
    for o in obs:
        o.matrix_world = C @ M


for piece in job["pieces"]:
    place(piece)

target = Vector((0, 0, 17))
for name, yaw, pitch, ortho, tz in (("front", 20, 8, 38, 17), ("side", 70, 6, 38, 17), ("close", 25, 10, 20, 17)):
    P.camera(Vector((0, 0, tz)), yaw, pitch, dist=60, ortho=ortho)
    P.render(os.path.join(job["out"], "worn_%s.png" % name))
print("done")
