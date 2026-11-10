"""The cube townsfolk as Epic Fight will draw them (tools/mcexport.py's meshes, at their in-game sizes): standing,
mid-stride in Epic Fight's own walk, and mid-swing in its sword attack, skinned here by its own biped armature,
so a bad weight or a cut in the wrong place shows before the game does.

    blender -b -P tools/blender/mc_ef_look.py -- OUT.png [ID ...]"""
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
D = os.environ.get("MC_EF_DIR", "E:/EFTest/game/tools/renders/mc/ef/")   # or the mod's own meshes, to compare
EF = os.environ.get("EF_ASSETS", "ef/assets/epicfight/animmodels/")   # Epic Fight's jar, unzipped
ARM = json.load(open("E:/EFTest/ref/assets/epicfight/animmodels/entity/biped.json"))["armature"]
scales = json.load(open(D + "scales.json" if os.path.exists(D + "scales.json") else "E:/EFTest/game/src/main/resources/assets/ashbound/npc_scales.json"))
ids = argv[1:] or list(scales)
POSES = [(None, 0), ("biped/living/walk", 0.25), ("biped/combat/sword_auto1", 0.3)]


def mat(a):
    return Matrix([a[0:4], a[4:8], a[8:12], a[12:16]])


def worlds(local):
    """each joint's world matrix from its parent's and its own local one"""
    out = {}

    def walk(nodes, parent):
        for n in nodes:
            w = parent @ local(n)
            out[n["name"]] = w
            walk(n["children"], w)
    walk(ARM["hierarchy"], Matrix.Identity(4))
    return out


bind = worlds(lambda n: mat(n["transform"]))


def pose(anim, t):
    if anim is None:
        return {j: Matrix.Identity(4) for j in bind}
    clip = {c["name"]: c for c in json.load(open(EF + "animations/" + anim + ".json"))["animation"]}

    def local(n):
        c = clip.get(n["name"])
        if not c:
            return mat(n["transform"])
        k = min(range(len(c["time"])), key=lambda i: abs(c["time"][i] - t))
        return mat(c["transform"][k])
    w = worlds(local)
    return {j: w[j] @ bind[j].inverted() for j in bind}


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 32
    sc.view_settings.view_transform = "AgX"
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.55, 0.68, 0.86, 1)
    bg.inputs[1].default_value = 0.9
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy, sun.angle, sun.color = 3.6, 0.1, (1.0, 0.94, 0.84)
    so = bpy.data.objects.new("sun", sun)
    so.rotation_euler = (math.radians(42), 0, math.radians(160))
    sc.collection.objects.link(so)
    bpy.ops.mesh.primitive_plane_add(size=80)
    g = bpy.context.active_object
    m = bpy.data.materials.new("grass")
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (0.13, 0.26, 0.07, 1)
    g.data.materials.append(m)
    return sc


def build(id_, skin, at):
    m = json.load(open(D + id_ + ".json"))["vertices"]
    P = m["positions"]["array"]
    U = m["uvs"]["array"]
    W = m["weights"]["array"]
    vc, vi = m["vcounts"]["array"], m["vindices"]["array"]
    s = scales[id_]
    verts, k = [], 0
    for n in range(len(vc)):
        p = Vector((P[3 * n], P[3 * n + 1], P[3 * n + 2], 1))
        q = Vector((0, 0, 0, 0))
        for _ in range(vc[n]):
            q += (skin[ARM["joints"][vi[k]]] @ p) * W[vi[k + 1]]
            k += 2
        verts.append(Vector((q.x * s + at, q.y * s, q.z * s)))
    faces, fuv = [], []
    for part in m["parts"].values():
        a = part["array"]
        for t in range(0, len(a), 9):
            tri = [a[t], a[t + 3], a[t + 6]]
            if len(set(tri)) < 3:
                continue
            faces.append(tri)
            fuv.append([(U[2 * a[t + 1]], 1 - U[2 * a[t + 1] + 1]), (U[2 * a[t + 4]], 1 - U[2 * a[t + 4] + 1]), (U[2 * a[t + 7]], 1 - U[2 * a[t + 7] + 1])])
    me = bpy.data.meshes.new(id_)
    me.from_pydata([v[:] for v in verts], [], faces)
    uvl = me.uv_layers.new()
    for poly, uv in zip(me.polygons, fuv):
        for li, c in zip(poly.loop_indices, uv):
            uvl.data[li].uv = c
    ob = bpy.data.objects.new(id_, me)
    bpy.context.scene.collection.objects.link(ob)
    mt = bpy.data.materials.get(id_)
    if mt is None:
        mt = bpy.data.materials.new(id_)
        mt.use_nodes = True
        nt = mt.node_tree
        b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Roughness"].default_value = 0.9
        tx = nt.nodes.new("ShaderNodeTexImage")
        tx.image = bpy.data.images.load(D.replace("animmodels/entity", "textures/entity") + id_ + ".png")
        tx.interpolation = "Closest"
        nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
        nt.links.new(tx.outputs["Alpha"], b.inputs["Alpha"])
    me.materials.append(mt)


gap = 1.25


def main():
    sc = reset()
    rows = []
    for r, (anim, t) in enumerate(POSES):
        skin = pose(anim, t)
        for i, id_ in enumerate(ids):
            build(id_, skin, (i - (len(ids) - 1) / 2) * gap)
        # front three-quarter view; Epic Fight's meshes face +y
        cd = bpy.data.cameras.new("cam")
        cd.lens = 50
        co = bpy.data.objects.new("cam", cd)
        sc.collection.objects.link(co)
        sc.camera = co
        tgt = Vector((0, 0, 0.8))
        a, e = math.radians(200 if r != 2 else 215), math.radians(6)
        dist = 3.0 + len(ids) * gap * 1.45
        co.location = tgt + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
        co.rotation_euler = (tgt - co.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.resolution_x, sc.render.resolution_y = 1600, 520
        path = OUT.replace(".png", "_%d.png" % r)
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        rows.append(path)
        for o in [o for o in sc.objects if o.type == "MESH" and o.name in ids or o.name.split(".")[0] in ids or o.type == "CAMERA"]:
            bpy.data.objects.remove(o)

    ims = [bpy.data.images.load(p) for p in rows]
    Wd, Hd = 1600, 520 * len(ims)
    px = [0.0] * (Wd * Hd * 4)
    for n, im in enumerate(reversed(ims)):
        src = list(im.pixels)
        px[n * 520 * Wd * 4:(n + 1) * 520 * Wd * 4] = src
    sheet = bpy.data.images.new("sheet", Wd, Hd, alpha=False)
    sheet.pixels = px
    sheet.filepath_raw = OUT
    sheet.file_format = "PNG"
    sheet.save()
    for p in rows:
        os.remove(p)
    print("sheet", OUT)


if __name__ == "__main__" and not os.environ.get("MC_EF_HELPERS"):
    main()
