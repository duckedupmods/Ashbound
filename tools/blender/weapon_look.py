"""A sheet of new weapons to judge: each stood upright, a quarter turn to show its thickness, big, and under it as the
inventory slot shows it. Dark ground like the armour sheets.

    blender -b -P tools/blender/weapon_look.py -- BATCH.json      -> <out>/<name>.png"""
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, 'E:/Ashbound/tools/blender')
import preview_vox as P  # noqa: E402

spec = json.load(open(sys.argv[sys.argv.index('--') + 1]))
A, OUT = spec["assets"], spec["out"]
TALL, WIDE, SLOT = spec.get("tall", 660), spec.get("wide", 300), 128
# item space (x right, y up, z toward the viewer) into Blender
UP = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


def scene():
    P.reset()
    sc = bpy.context.scene
    sc.render.film_transparent = True
    return sc


def load(iid):
    bpy.ops.wm.obj_import(filepath=os.path.join(A, "models/mesh/%s.obj" % iid), use_split_groups=True, forward_axis="Y", up_axis="Z")
    img = os.path.join(A, "textures/item/%s_3d.png" % iid)
    if os.path.exists(img + ".mcmeta"):      # animated fire: the sheet's first frame (weaponsets.export)
        img = "E:/Ashbound/tools/renders/vox/%s_f0.png" % iid
    mats = {True: P.material(img, True), False: P.material(img, False)}
    objs = list(bpy.context.selected_objects)
    for o in objs:
        glow = "fire" in o.name or "glow" in o.name
        o.data.materials.clear()
        o.data.materials.append(mats[glow])
    return objs


def camera(sc, target, yaw, ortho):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ortho
    a = math.radians(yaw)
    cam.location = target + Vector((math.sin(a) * 5, -math.cos(a) * 5, 0))
    cam.rotation_euler = (math.radians(90), 0, a)


def height(iid):
    ys = [float(l.split()[2]) for l in open(os.path.join(A, "models/mesh/%s.obj" % iid)) if l.startswith("v ")]
    return max(ys) - min(ys)


FIT = max(height(it["id"]) for it in spec["items"]) * 1.06   # one scale for the sheet, so sizes compare
tiles = []
for it in spec["items"]:
    # upright
    sc = scene()
    sc.render.resolution_x, sc.render.resolution_y = WIDE, TALL
    objs = load(it["id"])
    for o in objs:
        o.matrix_world = UP
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    centre = (lo + hi) / 2
    camera(sc, centre, 24, FIT)
    big = os.path.join(OUT, "big_%s.png" % it["id"])
    P.render(big)
    # the slot
    sc = scene()
    sc.render.resolution_x = sc.render.resolution_y = SLOT
    objs = load(it["id"])
    r, s, t = it["r"], it["s"], it["t"]
    M = Matrix(((r[0][0] * s, r[0][1] * s, r[0][2] * s, t[0] / 16),
                (r[1][0] * s, r[1][1] * s, r[1][2] * s, t[1] / 16),
                (r[2][0] * s, r[2][1] * s, r[2][2] * s, t[2] / 16),
                (0, 0, 0, 1))) @ Matrix.Translation((-0.5, -0.5, -0.5))
    for o in objs:
        o.matrix_world = UP @ M
    camera(sc, Vector((0, 0, 0)), 0, 1.0)
    slot = os.path.join(OUT, "slot_%s.png" % it["id"])
    P.render(slot)
    tiles.append((big, slot))

cols = spec.get("cols", 8)
rows = (len(tiles) + cols - 1) // cols
cw, ch = WIDE + 8, TALL + SLOT + 20
W, H = cw * min(cols, len(tiles)), ch * rows
sheet = bpy.data.images.new("sheet", W, H, alpha=True)
buf = [0.0] * (W * H * 4)
for k in range(W * H):
    buf[k * 4:k * 4 + 4] = (0.035, 0.036, 0.042, 1.0)


def paste(path, ox, oy):
    im = bpy.data.images.load(path)
    iw, ih = im.size
    px = list(im.pixels)
    for y in range(ih):
        for x in range(iw):
            a = px[(y * iw + x) * 4 + 3]
            if a < 0.02:
                continue
            q = ((oy + y) * W + ox + x) * 4
            for c in range(3):
                buf[q + c] = buf[q + c] * (1 - a) + px[(y * iw + x) * 4 + c] * a


for k, (big, slot) in enumerate(tiles):
    cx, cy = k % cols * cw + 4, (rows - 1 - k // cols) * ch
    q = cy + 8
    for y in range(SLOT):
        for x in range(SLOT):
            p = ((q + y) * W + cx + (WIDE - SLOT) // 2 + x) * 4
            buf[p:p + 3] = (0.13, 0.13, 0.14)
    paste(slot, cx + (WIDE - SLOT) // 2, q)
    paste(big, cx, cy + SLOT + 16)
sheet.pixels = buf
sheet.filepath_raw = os.path.join(OUT, spec["name"] + ".png")
sheet.file_format = "PNG"
sheet.save()
print("sheet", sheet.filepath_raw)
