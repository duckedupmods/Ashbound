"""A look at the sculpted props as the game will draw them: their block models (boxes, UVs, textures, glow) put back
together piece by piece, in a row on a flagstone floor, lit by a low sun and their own glow.

    blender -b -P tools/blender/sculpt_preview.py -- SHEET NAME [NAME ...] [night]
        -> tools/renders/sculpt_SHEET.png (and _close.png)
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.normpath(os.path.join(HERE, "..", ".."))
ASSETS = os.path.join(GAME, "src", "main", "resources", "assets", "ashbound")
PIECES = json.load(open(os.path.join(GAME, "tools", "renders", "sculpt_pieces.json")))
OUT = os.path.join(GAME, "tools", "renders")
MATS = {}


def material(ref, glow, see):
    key = (ref, glow, see)
    if key in MATS:
        return MATS[key]
    path = os.path.join(ASSETS, "textures", ref.split(":", 1)[1] + ".png")
    m = bpy.data.materials.new(os.path.basename(ref))
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    img = bpy.data.images.load(path, check_existing=True)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    mapn = nt.nodes.new("ShaderNodeMapping")
    uvn = nt.nodes.new("ShaderNodeTexCoord")
    frames = img.size[1] // max(1, img.size[0])
    mapn.inputs["Scale"].default_value = (1, 1 / max(1, frames), 1)      # the first frame of an animation
    mapn.inputs["Location"].default_value = (0, 1 - 1 / max(1, frames), 0)
    nt.links.new(uvn.outputs["UV"], mapn.inputs["Vector"])
    nt.links.new(mapn.outputs[0], tex.inputs[0])
    nt.links.new(tex.outputs[0], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.6
    if any(k in ref for k in ("iron", "steel", "copper", "brass", "gold", "silver")):
        bsdf.inputs["Metallic"].default_value = 0.55
        bsdf.inputs["Roughness"].default_value = 0.4
    if glow:
        nt.links.new(tex.outputs[0], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 1.1
    if see:
        nt.links.new(tex.outputs[1], bsdf.inputs["Alpha"])
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
    MATS[key] = m
    return m


def quad(f, a, b):
    x1, y1, z1 = a
    x2, y2, z2 = b
    return {"north": [(x2, y2, z1), (x1, y2, z1), (x1, y1, z1), (x2, y1, z1)],
            "south": [(x1, y2, z2), (x2, y2, z2), (x2, y1, z2), (x1, y1, z2)],
            "east": [(x2, y2, z2), (x2, y2, z1), (x2, y1, z1), (x2, y1, z2)],
            "west": [(x1, y2, z1), (x1, y2, z2), (x1, y1, z2), (x1, y1, z1)],
            "up": [(x1, y2, z1), (x2, y2, z1), (x2, y2, z2), (x1, y2, z2)],
            "down": [(x1, y1, z2), (x2, y1, z2), (x2, y1, z1), (x1, y1, z1)]}[f]


def G(x, y, z):
    return Vector((x, -z, y))


def place(name, ox, oz):
    verts, faces, uvs, mids = [], [], [], []
    mats = []
    for cx, cy, cz, idx in PIECES[name]["pieces"]:
        m = json.load(open(os.path.join(ASSETS, "models", "block", "%s_%d.json" % (name, idx))))
        tex = m["textures"]
        for e in m["elements"]:
            glow = "light_emission" in e
            for f, fd in e["faces"].items():
                ref = tex[fd["texture"][1:]]
                see = any(k in ref for k in ("water", "steam", "glass", "flame", "foam", "witchfire"))
                mat = material(ref, glow, see)
                if mat not in mats:
                    mats.append(mat)
                q = quad(f, e["from"], e["to"])
                n = len(verts)
                for p in q:
                    verts.append(G(ox + cx + p[0] / 16, cy + p[1] / 16, oz + cz + p[2] / 16))
                faces.append((n, n + 1, n + 2, n + 3))
                u1, v1, u2, v2 = fd["uv"]
                uvs.append([(u1 / 16, 1 - v1 / 16), (u2 / 16, 1 - v1 / 16), (u2 / 16, 1 - v2 / 16), (u1 / 16, 1 - v2 / 16)])
                mids.append(mats.index(mat))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    for mt in mats:
        me.materials.append(mt)
    uvl = me.uv_layers.new()
    for i, p in enumerate(me.polygons):
        p.material_index = mids[i]
        for j, li in enumerate(p.loop_indices):
            uvl.data[li].uv = uvs[i][j]
    # MC quads wind clockwise seen from outside: flip so normals face out
    for p in me.polygons:
        p.flip()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    sheet, names = args[0], [a for a in args[1:] if a not in ("night", "close")]
    night, close = "night" in args, "close" in args
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    x = 0.0
    spans = []
    for n in names:
        w, h, d = PIECES[n]["size"]
        place(n, x, 0)
        spans.append((x, w, h, d))
        x += w + 1.0
    total = x - 1.0
    hmax = max(s[2] for s in spans)
    bpy.ops.mesh.primitive_plane_add(size=1)
    fl = bpy.context.active_object
    fl.scale = (total + 8, 12, 1)
    fl.location = (total / 2, -2, 0)
    fm = bpy.data.materials.new("floor")
    fm.use_nodes = True
    b = next(n for n in fm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (0.16, 0.15, 0.14, 1)
    fl.data.materials.append(fm)
    world = bpy.data.worlds.new("w")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.03, 0.035, 0.06, 1) if night else (0.5, 0.6, 0.75, 1)
    bg.inputs[1].default_value = 0.4 if night else 0.9
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 0.4 if night else 3.2
    sun.rotation_euler = (math.radians(50), 0, math.radians(-35))
    sc.collection.objects.link(sun)
    try:
        sc.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = 1800, 900
    sc.view_settings.view_transform = "AgX"
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam

    def shoot(eye, look, lens, path):
        cam.location = G(*eye)
        cam.rotation_euler = (G(*look) - G(*eye)).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lens
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
    sc.render.resolution_x, sc.render.resolution_y = 640, 640
    tiles = []
    for (x0, w, h, d), n in zip(spans, names):
        r = max(w, h, d) * 1.25 + 1.2
        c = (x0 + w / 2, h * 0.42, d / 2)
        p = os.path.join(OUT, "tile_%s.png" % n)
        shoot((c[0] - r * 0.75, c[1] + r * 0.62, c[2] - r * 1.05), c, 50, p)
        tiles.append(p)
        if close:                                       # a tall statue: the whole of it from the front, and its head
            sc.render.resolution_x, sc.render.resolution_y = 700, 1000
            fc = (x0 + w / 2, h * 0.5, d / 2)
            shoot((fc[0] - h * 0.35, fc[1] + h * 0.05, -h * 1.45), fc, 50, os.path.join(OUT, "front_%s.png" % n))
            hc = (x0 + w / 2, h * 0.86, d / 2)
            shoot((hc[0] - h * 0.12, hc[1] + h * 0.02, -h * 0.42), hc, 50, os.path.join(OUT, "head_%s.png" % n))
            sc.render.resolution_x, sc.render.resolution_y = 640, 640
    with open(os.path.join(OUT, "sculpt_%s_tiles.txt" % sheet), "w") as f:
        f.write(chr(10).join(tiles))


main()
