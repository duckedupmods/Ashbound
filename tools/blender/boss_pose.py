"""Monsters as the game poses them: the Epic Fight mesh, each vertex carried by its joint through a real Epic Fight clip,
on a ground grid with its hitbox drawn, so anything under the floor or off its limb shows.
  blender -b -P tools/blender/boss_pose.py -- OUT.png COLS id,id,... anim@t,anim@t,...      bind = the rest pose"""
import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import efrig  # noqa: E402

ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT, COLS, IDS, POSES = ARGS[0], int(ARGS[1]), ARGS[2].split(","), ARGS[3].split(",")
GAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
A = os.path.join(GAME, "src/main/resources/assets/ashbound/")
ROWS = {m["id"]: m for m in json.load(open(os.path.join(GAME, "src/main/resources/ashbound/gate_mobs.json"), encoding="utf-8"))}
RES = 420
VIEW = tuple(float(x) for x in os.environ.get("BOSS_VIEW", "0.75,-1,0.16").split(","))
arm = efrig.Armature("biped")


def mesh(m):
    v = json.load(open(A + "animmodels/entity/%s.json" % m["mesh"], encoding="utf-8"))["vertices"]
    a = v["positions"]["array"]
    pos = [Vector(a[i:i + 3]) for i in range(0, len(a), 3)]
    ix = v["vindices"]["array"]
    vc, wt = v["vcounts"]["array"], v["weights"]["array"]
    joint, k = [], 0
    for n in vc:
        joint.append([(arm.joints[ix[k + c * 2]], wt[ix[k + c * 2 + 1]]) for c in range(n)])
        k += n * 2
    u = v["uvs"]["array"]
    tris = []
    for part in v["parts"].values():
        t = part["array"]
        tris += [(t[i], t[i + 3], t[i + 6], t[i + 1], t[i + 4], t[i + 7]) for i in range(0, len(t), 9)]
    return pos, joint, u, tris


def shot(m, data, anim, t):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "FLAT"
    sc.display.shading.color_type = "TEXTURE"
    sc.display.shading.show_shadows = False
    sc.render.resolution_x = sc.render.resolution_y = RES
    sc.render.film_transparent = False
    pos, joint, u, tris = data
    if anim == "trot":   # client/MountPose.java's legs at phase t, the body level
        sw, fo = math.sin(t) * 0.55, math.cos(t) * 0.7
        rx = lambda a: __import__("mathutils").Matrix.Rotation(a, 4, "X")  # noqa: E731
        pose = arm.pose(None, 0, {"Thigh_L": rx(sw), "Leg_L": rx(-max(0, fo)), "Thigh_R": rx(-sw), "Leg_R": rx(-max(0, -fo))})
    else:
        pose = arm.pose(None if anim == "bind" else anim, t)
    sk = {j: pose[j] @ arm.bind[j].inverted() for j in arm.joints}
    s = m["scale"]
    me = bpy.data.meshes.new("m")
    pts = [sum(((sk[j] @ p) * w for j, w in js), Vector()) * s for p, js in zip(pos, joint)]
    keep = [t3 for t3 in tris if t3[0] != t3[1]]
    me.from_pydata([tuple(p) for p in pts], [], [t3[:3] for t3 in keep])
    uv = me.uv_layers.new(name="UV").data
    for k, t3 in enumerate(keep):
        for c in range(3):
            i = t3[3 + c]
            uv[k * 3 + c].uv = (u[i * 2], 1 - u[i * 2 + 1])
    mat = bpy.data.materials.new("t")
    mat.use_nodes = True
    n = mat.node_tree.nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(os.path.abspath(A + "textures/entity/%s.png" % m["mesh"]))
    n.interpolation = "Closest"
    me.materials.append(mat)
    ob = bpy.data.objects.new("m", me)
    sc.collection.objects.link(ob)
    # the ground, a block grid, and the hitbox
    bm = bmesh.new()
    R = 12
    for i in range(-R, R + 1):
        bmesh.ops.create_cube(bm, size=1, matrix=__import__("mathutils").Matrix.Diagonal((0.03, 2 * R, 0.03, 1)).to_4x4() @ __import__("mathutils").Matrix.Translation((i / 0.03, 0, 0)))
        bmesh.ops.create_cube(bm, size=1, matrix=__import__("mathutils").Matrix.Diagonal((2 * R, 0.03, 0.03, 1)).to_4x4() @ __import__("mathutils").Matrix.Translation((0, i / 0.03, 0)))
    w, h = m["w"], m["h"]
    for sx in (-1, 1):
        for sy in (-1, 1):
            bmesh.ops.create_cube(bm, size=1, matrix=__import__("mathutils").Matrix.Translation((sx * w / 2, sy * w / 2, h / 2)) @ __import__("mathutils").Matrix.Diagonal((0.05, 0.05, h, 1)).to_4x4())
    g = bpy.data.meshes.new("g")
    bm.to_mesh(g)
    gm = bpy.data.materials.new("g")
    g.materials.append(gm)
    sc.collection.objects.link(bpy.data.objects.new("g", g))
    pl = bpy.data.meshes.new("p")
    pl.from_pydata([(-R, -R, -0.02), (R, -R, -0.02), (R, R, -0.02), (-R, R, -0.02)], [], [(0, 1, 2, 3)])
    pm = bpy.data.materials.new("p")
    pl.materials.append(pm)
    sc.collection.objects.link(bpy.data.objects.new("p", pl))
    cd = bpy.data.cameras.new("c")
    cam = bpy.data.objects.new("c", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    top = max(max(p.z for p in pts), h)
    cd.type = "ORTHO"
    cd.ortho_scale = top * 1.5
    d = Vector(VIEW).normalized()
    c = Vector((0, 0, top * 0.46))
    cam.location = c + d * 60
    cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    w_ = bpy.data.worlds.new("w")
    w_.color = (0.3, 0.33, 0.38)
    sc.world = w_
    p = OUT + "_tile.png"
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
    return p, min(q.z for q in pts), max((q - Vector((0, 0, q.z))).length for q in pts)


tiles = []
for mid in IDS:
    m = ROWS[mid]
    data = mesh(m)
    for ps in POSES:
        anim, _, t = ps.partition("@")
        path, low, wide = shot(m, data, anim, float(t or 0))
        im = bpy.data.images.load(path)
        tiles.append((list(im.pixels), mid, anim, low))
        bpy.data.images.remove(im)
        print("pose %-16s %-44s lowest %.2f" % (mid, anim, low))
cols = COLS
rows = math.ceil(len(tiles) / cols)
W, H = cols * RES, rows * RES
sheet = [0.0] * (W * H * 4)
for i, (px, _, _, _) in enumerate(tiles):
    ox, oy = (i % cols) * RES, (rows - 1 - i // cols) * RES
    for y in range(RES):
        a = (oy + y) * W * 4 + ox * 4
        sheet[a:a + RES * 4] = px[y * RES * 4:(y + 1) * RES * 4]
img = bpy.data.images.new("sheet", W, H)
img.pixels = sheet
img.filepath_raw = OUT
img.file_format = "PNG"
img.save()
print("sheet", OUT)
