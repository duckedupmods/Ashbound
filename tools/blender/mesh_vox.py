"""A generated or scanned mesh (TRELLIS output, an OBJ) turned into statue blocks, the same way the sculpts are.

    blender -b -P tools/blender/mesh_vox.py -- IN.obj NAME HEIGHT [render] [novox] [flood] [yaw=DEG]

Imports the mesh, stands it up (its lowest point at y 0, centred, facing +z after `yaw`), scales it to HEIGHT blocks,
remeshes it watertight (generated meshes have holes and flipped faces the inside test would trip on), then samples
it on the block grid with ambient occlusion baked in (king_sculpt.voxelize). Every cell gets part "stone"; the
palette split comes after, in the placing code. Writes tools/renders/NAME_cells.json.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import king_sculpt as KS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FLOOD_ONLY = "flood" in sys.argv                                            # no remesh (it drops thin parts like a flat base)
PAINT = None                                                                # the coloured copy of the mesh, if it has colours


def paint(path):
    """Give every cell the colour of the painted surface nearest its centre (sRGB 0-255), into the cells file."""
    import json
    from mathutils.bvhtree import BVHTree
    me = PAINT.data
    vs = [PAINT.matrix_world @ v.co for v in me.vertices]
    ca = me.color_attributes[0]
    if ca.domain == "POINT":
        vcol = [tuple(d.color_srgb[:3]) for d in ca.data]
        pcol = None
    else:                                                                   # per face corner: average a face's corners
        vcol = None
        pcol = [tuple(sum(ca.data[li].color_srgb[i] for li in p.loop_indices) / p.loop_total for i in range(3))
                for p in me.polygons]
    polys = [tuple(p.vertices) for p in me.polygons]
    t = BVHTree.FromPolygons(vs, polys)
    with open(path) as f:
        data = json.load(f)
    for c in data["cells"]:
        loc, _, fi, _ = t.find_nearest(KS.G(c[0] + 0.5, c[1] + 0.5, c[2] + 0.5))
        if fi is None:
            c.append([128, 128, 128])
            continue
        if pcol:
            rgb = pcol[fi]
        else:                                                               # inverse-distance blend of the face's corners
            ws = [1.0 / (0.05 + (vs[i] - loc).length) for i in polys[fi]]
            rgb = [sum(w * vcol[i][k] for w, i in zip(ws, polys[fi])) / sum(ws) for k in range(3)]
        c.append([round(255 * max(0.0, min(1.0, x))) for x in rgb])
    with open(path, "w") as f:
        json.dump(data, f)
    print("painted", len(data["cells"]), "cells")


def load(path, height, yaw):
    if path.endswith(".ply"):                                               # a repainted mesh: carries vertex colours
        bpy.ops.wm.ply_import(filepath=path, forward_axis="Y", up_axis="Z")
    else:
        bpy.ops.wm.obj_import(filepath=path, forward_axis="Y", up_axis="Z")  # TRELLIS meshes are z-up as written
    ob = bpy.context.selected_objects[0]
    bpy.context.view_layer.objects.active = ob
    ob.rotation_euler = (0, 0, math.radians(yaw))
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    vs = [v.co for v in ob.data.vertices]
    lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
    hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    k = height / (hi.z - lo.z)
    c = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    ob.data.transform(Matrix.Scale(k, 4) @ Matrix.Translation(-c))
    ob.data.update()
    print("size (blocks): %.0f wide, %.0f deep, %.0f tall" % ((hi.x - lo.x) * k, (hi.y - lo.y) * k, height))
    global PAINT
    if ob.data.color_attributes:                                            # keep the painted surface before the remesh
        PAINT = ob.copy()
        PAINT.data = ob.data.copy()
        bpy.context.scene.collection.objects.link(PAINT)
        PAINT.hide_render = True
    if FLOOD_ONLY:                                                          # flood fill copes with holes: keep every thin part
        KS.PARTS.append((ob, "stone"))
        return ob
    # close the generator's open edges first (an open base remeshes to a thin skin with nothing inside), normals out
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.02)
    open_edges = [e for e in bm.edges if e.is_boundary]
    bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    print("closed %d open edges" % len(open_edges))
    bm.to_mesh(ob.data)
    bm.free()
    # watertight: a fine voxel remesh, then smooth the remesher's steps a little
    md = ob.modifiers.new("r", "REMESH")
    md.mode = "VOXEL"
    md.voxel_size = 0.35
    md.use_smooth_shade = True
    bpy.ops.object.modifier_apply(modifier="r")
    md = ob.modifiers.new("s", "SMOOTH")
    md.iterations = 2
    bpy.ops.object.modifier_apply(modifier="s")
    print("remeshed:", len(ob.data.polygons), "faces")
    KS.PARTS.append((ob, "stone"))
    return ob


def render(name, height):
    sc = bpy.context.scene
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            pass
    sc.render.resolution_x, sc.render.resolution_y = 1000, 1100
    m = bpy.data.materials.new("stone")
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.75, 0.73, 0.7, 1)
    for ob, _ in KS.PARTS:
        ob.data.materials.append(m)
    if PAINT:                                                               # show the painted copy instead
        nt = m.node_tree
        a = nt.nodes.new("ShaderNodeVertexColor")
        a.layer_name = PAINT.data.color_attributes[0].name
        nt.links.new(a.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
        PAINT.data.materials.append(m)
        PAINT.hide_render = False
        for ob, _ in KS.PARTS:
            ob.hide_render = True
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.45, 0.5, 0.58, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.5
    sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
    sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.clip_end = 2000
    h = height
    for shot, eye, look, lens in (("front", (0, h * 0.55, h * 2.0), (0, h * 0.5, 0), 35),
                                  ("three", (h * 1.3, h * 0.6, h * 1.5), (0, h * 0.5, 0), 35),
                                  ("side", (h * 2.0, h * 0.55, 0), (0, h * 0.5, 0), 35)):
        cam.location = KS.G(*eye)
        d = KS.G(*look) - KS.G(*eye)
        cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lens
        sc.render.filepath = os.path.join(KS.RENDERS, "%s_mesh_%s.png" % (name, shot))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    path, name, height = args[0], args[1], float(args[2])
    yaw = next((float(a[4:]) for a in args if a.startswith("yaw=")), 0.0)
    KS.reset()
    load(path, height, yaw)
    if "render" in args:
        render(name, height)
    if "novox" not in args:
        cells = os.path.join(HERE, "..", "renders", "%s_cells.json" % name)
        KS.FLOOD = "flood" in args
        KS.voxelize(out=cells, prio={"stone": 1}, uncut=())
        if PAINT:
            paint(cells)
