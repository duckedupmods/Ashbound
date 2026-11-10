"""The whole cube cast standing in rows (tools/mcexport.py's meshes at their in-game sizes), one image per row; the
rows are named and stacked into a sheet by tools/mc_cast_sheet.py.

    blender -b -P tools/blender/mc_ef_grid.py -- ROWS.json OUTDIR"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

os.environ["MC_EF_HELPERS"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mc_ef_look as L  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
rows = json.load(open(args[0]))
out = args[1]
GAP, PER = 1.2, int(os.environ.get("MC_GRID_PER", 17))
W, H = 1800, int(os.environ.get("MC_GRID_H", 300))

L.scales.update(json.load(open(L.D + "scales.json")))
if os.path.exists(L.D + "adv_scales.json"):             # tools/adventurers.py's parties
    L.scales.update(json.load(open(L.D + "adv_scales.json")))
rest = L.pose(None, 0)
for n, row in enumerate(rows):
    sc = L.reset()
    for i, id_ in enumerate(row["ids"]):
        L.build(id_, rest, (i - (len(row["ids"]) - 1) / 2) * GAP)
    cd = bpy.data.cameras.new("cam")
    cd.type = "ORTHO"
    cd.ortho_scale = PER * GAP + 1
    co = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(co)
    sc.camera = co
    tgt = Vector((0, 0, 1.05))
    a, e = math.radians(180), math.radians(7)
    co.location = tgt + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * 30
    co.rotation_euler = (tgt - co.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.filepath = os.path.join(out, "row_%02d.png" % n)
    bpy.ops.render.render(write_still=True)
print("rows", len(rows))
