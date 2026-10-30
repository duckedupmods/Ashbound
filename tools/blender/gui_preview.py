"""How tools/gui3d.py's weapons sit in an inventory slot: each item's mesh put through its gui transform
(Minecraft's v' = T + R S (v - 0.5)), seen as the slot sees it, on the slot's grey; one sheet per gate.

    blender -b -P tools/blender/gui_preview.py -- BATCH.json      -> <out>/sheet_<gate>.png"""
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, 'E:/Ashbound/tools/blender')
import preview_vox as P  # noqa: E402

spec = json.load(open(sys.argv[sys.argv.index('--') + 1]))
RES = spec.get("res", 96)             # a slot's pixels; bigger for concept sheets
COLS = spec.get("cols", 8)
A, OUT = spec["assets"], spec["out"]
# Minecraft (x right, y up, z towards the viewer) into Blender (x right, z up, -y towards the viewer)
C = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))

tiles = {}
for it in spec["items"]:
    P.reset()
    sc = bpy.context.scene
    sc.render.resolution_x = sc.render.resolution_y = RES
    sc.render.film_transparent = True
    for o in list(bpy.data.objects):
        if o.type == "MESH":
            bpy.data.objects.remove(o)
    bpy.ops.wm.obj_import(filepath=os.path.join(A, "models/mesh/%s.obj" % it["id"]), use_split_groups=True,
                          forward_axis="Y", up_axis="Z")
    img = os.path.join(A, "textures/item/%s_3d.png" % it["id"])
    mats = {True: P.material(img, True), False: P.material(img, False)}
    r, s, t = it["r"], it["s"], it["t"]
    M = Matrix(((r[0][0] * s, r[0][1] * s, r[0][2] * s, t[0] / 16),
                (r[1][0] * s, r[1][1] * s, r[1][2] * s, t[1] / 16),
                (r[2][0] * s, r[2][1] * s, r[2][2] * s, t[2] / 16),
                (0, 0, 0, 1))) @ Matrix.Translation((-0.5, -0.5, -0.5))
    for o in bpy.context.selected_objects:
        glow = "fire" in o.name or "glow" in o.name
        o.data.materials.clear()
        o.data.materials.append(mats[glow])
        o.matrix_world = C @ M
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 1.0
    cam.location = (0, -5, 0)
    cam.rotation_euler = (math.radians(90), 0, 0)
    out = os.path.join(OUT, "slot_%s.png" % it["id"])
    P.render(out)
    tiles.setdefault(it["gate"], []).append(out)

# one sheet per gate: each slot big, then a hotbar at GUI scale 3
for gate, paths in tiles.items():
    cols, step = COLS, RES + 8
    rows = (len(paths) + cols - 1) // cols
    W, H = cols * step + 8, rows * step + 8
    sheet = bpy.data.images.new("sheet", W, H, alpha=True)
    px = [0.0] * (W * H * 4)
    for i in range(W * H):
        px[i * 4:i * 4 + 4] = [0.12, 0.11, 0.12, 1]
    for k, p in enumerate(paths):
        im = bpy.data.images.load(p)
        src = im.pixels[:]
        ox, oy = 8 + (k % cols) * step, H - step - (k // cols) * step
        for y in range(RES):
            for x in range(RES):
                j = ((oy + y) * W + ox + x) * 4
                a = src[(y * RES + x) * 4 + 3]
                bg = 0.545 if 1 < x < RES - 2 and 1 < y < RES - 2 else 0.22
                for c in range(3):
                    px[j + c] = src[(y * RES + x) * 4 + c] * a + bg * (1 - a)
    sheet.pixels[:] = px
    sheet.filepath_raw = os.path.join(OUT, "sheet_%s.png" % gate)
    sheet.file_format = "PNG"
    sheet.save()
    print("sheet", gate)
