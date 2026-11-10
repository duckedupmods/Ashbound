"""The Minecraft-style sample (tools/mcstyle.py): the townsfolk in a row from the front and from behind, the wagon with
its horse from two sides, on grass under a high sun. Crisp texels (Closest), alpha for the skins' outer layer.

    blender -b -P tools/blender/mc_look.py -- OUT.png"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

OUT = sys.argv[sys.argv.index("--") + 1]
D = "E:/EFTest/game/tools/renders/mc/"
lineup = json.load(open(D + "lineup.json"))


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 48
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
    so.rotation_euler = (math.radians(42), 0, math.radians(-30))
    sc.collection.objects.link(so)
    bpy.ops.mesh.primitive_plane_add(size=80)
    g = bpy.context.active_object
    m = bpy.data.materials.new("grass")
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (0.13, 0.26, 0.07, 1)
    b.inputs["Roughness"].default_value = 1
    g.data.materials.append(m)
    return sc


def load(name, x=0.0, y=0.0, turn=0.0):
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=D + name + ".obj", use_split_groups=False)
    obs = [o for o in bpy.data.objects if o not in before]
    img = bpy.data.images.load(D + name + ".png")
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Roughness"].default_value = 0.9
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = img
    t.interpolation = "Closest"
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(t.outputs["Alpha"], b.inputs["Alpha"])
    if "wagon" in name:     # the lantern's glass glows
        pass
    for o in obs:
        o.data.materials.clear()
        o.data.materials.append(m)
        o.location = (x, y, 0)
        o.rotation_euler[2] = math.radians(turn)
    return obs


def shoot(sc, path, tgt, yaw, el, dist, lens=50, size=(1000, 700)):
    cd = bpy.data.cameras.new("cam")
    cd.lens = lens
    co = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(co)
    sc.camera = co
    a, e = math.radians(yaw), math.radians(el)
    co.location = tgt + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    co.rotation_euler = (tgt - co.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return path


folk = [e["name"] for e in lineup if e["name"] not in ("wagon_horse", "hob_wagon")]
shots = []
sc = reset()
for k, n in enumerate(folk):
    load(n, (k - (len(folk) - 1) / 2) * 1.35)
mid = Vector((0, 0, 0.95))
n = len(folk)
xs = [(k - (n - 1) / 2) * 1.35 for k in range(n)]
for half, sl in (("a", slice(0, 4)), ("e", slice(4, 7))):
    c = Vector((sum(xs[sl]) / len(xs[sl]), 0, 1.15))
    shots.append(shoot(sc, OUT.replace(".png", "_%s.png" % half), c, 10, 4, 7.6, 50, (1400, 560)))
shots.append(shoot(sc, OUT.replace(".png", "_b.png"), mid, 196, 6, 14.5, 50, (1400, 560)))
sc = reset()
load("hob_wagon")
load("wagon_horse")
c = Vector((0, -2.2, 1.2))
shots.append(shoot(sc, OUT.replace(".png", "_c.png"), c, 52, 18, 10.5, 45, (700, 560)))
shots.append(shoot(sc, OUT.replace(".png", "_d.png"), c, 210, 22, 10.5, 45, (700, 560)))

# stack: the two close rows, the backs, then the two wagon shots side by side
ims = [bpy.data.images.load(p) for p in shots]
W = 1400
H = 560 * 4
px = [0.0] * (W * H * 4)


def put(im, ox, oy):
    w, h = im.size
    src = list(im.pixels)
    for y in range(h):
        i = ((oy + y) * W + ox) * 4
        px[i:i + w * 4] = src[y * w * 4:(y + 1) * w * 4]


put(ims[3], 0, 0)
put(ims[4], 700, 0)
put(ims[2], 0, 560)
put(ims[1], 0, 1120)
put(ims[0], 0, 1680)
sheet = bpy.data.images.new("sheet", W, H, alpha=False)
sheet.pixels = px
sheet.filepath_raw = OUT
sheet.file_format = "PNG"
sheet.save()
for p in shots:
    os.remove(p)
print("sheet", OUT)
