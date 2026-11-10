"""Renders tools/gate_window.py's concept: the gate you can see into (and out of).
  blender -b -P tools/blender/gate_window.py -- struct <scene> <shot>   block scene (E:/Ashbound/tools/renders/struct)
  blender -b -P tools/blender/gate_window.py -- rift <rank> <shot>      the tear alone (Cycles, see-through EXR) + mask
  blender -b -P tools/blender/gate_window.py -- comp <rank> <shot>      base + what's through the tear + the tear
Passes and results go to tools/renders/gate/gw/."""
import json
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
GW = os.path.abspath(os.path.join(HERE, "..", "renders", "gate", "gw"))
os.makedirs(GW, exist_ok=True)
ARGS = sys.argv[sys.argv.index("--") + 1:]
MODE = ARGS[0]
SHOTS = json.load(open(os.path.join(GW, "..", "gw_shots.json")))
WIDE = 2.0      # the tear's width over gate_rift's
RANKS = ["F", "E", "D", "C", "B", "A", "S", "SS", "SSS"]
COLOUR = [0xCDD2DC, 0x46E678, 0x3C8CFF, 0xA55AFF, 0xFFA01E, 0xFF2D2D, 0xFF1E1E, 0xBE46FF, 0xFFECBE]


def lin(c):
    return c / 12.92 if c < 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(h):
    return tuple(lin(((h >> s) & 255) / 255) for s in (16, 8, 0))


def struct(scene, shot, rank="F"):
    src = open("E:/Ashbound/tools/blender/preview_struct.py", encoding="utf-8").read()
    src = src.replace("\nmain()\n", "\n")
    g = {"__file__": "E:/Ashbound/tools/blender/preview_struct.py", "__name__": "ps"}
    exec(compile(src, "preview_struct.py", "exec"), g)
    cfg = json.load(open(os.path.join(g["DIR"], scene + "_shots.json")))
    g["setup"](cfg)
    g["load"](scene)
    sc = bpy.context.scene
    hot = rgb(COLOUR[RANKS.index(rank)])
    dark = scene in ("gw_in", "gw_cel")
    w = sc.world.node_tree.nodes["Background"]
    if dark:
        # the vaults: a little cold air light, the lamps carry it
        w.inputs[0].default_value = (0.09, 0.085, 0.1, 1)
        w.inputs[1].default_value = 1.0
        bpy.data.objects["sun"].data.energy = 0.0
        sc.view_settings.exposure = 1.6
    L = json.load(open(os.path.join(g["DIR"], scene + "_lights.json")))
    for kind, x, y, z in L:
        col, power = {"lamp": ((1.0, 0.7, 0.42), 700), "fis": (hot, 160)}.get(kind, ((1, 0.7, 0.4), 40))
        ld = bpy.data.lights.new(kind, "POINT")
        ld.color = col
        ld.energy = power
        ld.shadow_soft_size = 0.4
        o = bpy.data.objects.new(kind, ld)
        o.location = g["mc"](x, y, z)
        sc.collection.objects.link(o)
    # the tear's own light on whatever stands round it
    if scene in ("gw_out", "gw_cel") and (scene == "gw_out" or shot == "exit"):
        o_ = SHOTS["o_out"] if scene == "gw_out" else SHOTS["o_exit"]
        for i, dy in enumerate((2.0, 5.0, 8.0)):
            ld = bpy.data.lights.new("rift%d" % i, "POINT")
            ld.color = hot
            ld.energy = 2600 if i == 1 else 1500
            ld.shadow_soft_size = 1.0
            o = bpy.data.objects.new("rift%d" % i, ld)
            o.location = g["mc"](o_[0], o_[1] + dy, o_[2] + 0.8)
            sc.collection.objects.link(o)
    # the fissure's floor burns
    for m in bpy.data.materials:
        if "magma" in m.name and m.use_nodes:
            nt = m.node_tree
            e = nt.nodes.new("ShaderNodeEmission")
            e.inputs["Color"].default_value = (*[min(1, c * 0.6 + 0.4) for c in hot], 1)
            e.inputs["Strength"].default_value = 9.0
            out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
            nt.links.new(e.outputs[0], out.inputs["Surface"])
    at, look, lens = cfg["shots"][shot][:3]
    sc.render.resolution_x, sc.render.resolution_y = 1600, 900
    g["camera"](at, look, lens)
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = os.path.join(GW, "%s_%s.png" % (scene, shot))
    bpy.ops.render.render(write_still=True)
    print("WROTE", sc.render.filepath)


def rift(rank, shot):
    sys.argv = [sys.argv[0], "--", rank, "hero"] + (["fast"] if "fast" in ARGS else [])
    src = open(os.path.join(HERE, "gate_rift.py"), encoding="utf-8").read()
    src = src.split("# ---------------------------------------------------------------- shots, bloom, render")[0]
    g = {"__file__": os.path.join(HERE, "gate_rift.py"), "__name__": "gr"}
    exec(compile(src, "gate_rift.py", "exec"), g)
    sc = bpy.context.scene
    for ob in list(sc.objects):
        if ob.name.startswith(("ground_", "trunks", "leaves", "shard")):
            bpy.data.objects.remove(ob)
    # the torn chunks wear the dungeon's own bricks
    tex = {}
    for t in ("cellar_brick", "wet_cellar_brick", "cellar_flags", "cask_oak"):
        p = "E:/Ashbound/src/main/resources/assets/ashbound/textures/block/%s.png" % t
        if os.path.exists(p):
            m = bpy.data.materials.new("chunk_" + t)
            m.use_nodes = True
            nt = m.node_tree
            bs = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
            im = nt.nodes.new("ShaderNodeTexImage")
            im.image = bpy.data.images.load(p)
            im.interpolation = "Closest"
            nt.links.new(im.outputs["Color"], bs.inputs["Base Color"])
            bs.inputs["Roughness"].default_value = 0.9
            tex[t] = m
    mats = list(tex.values())
    # wider, so there's something to see through it; the lips a little calmer (the glow swallowed the view)
    for ob in sc.objects:
        if ob.name in ("void", "lip", "cracks"):
            ob.scale.x = WIDE
    for n in bpy.data.materials["lip"].node_tree.nodes:
        if n.type == "EMISSION":
            n.inputs["Strength"].default_value = 0.35
    i = 0
    for ob in list(sc.objects):
        if ob.name.startswith("chunk"):
            loc, rot, s = ob.location.copy(), ob.rotation_euler.copy(), ob.scale[0]
            bpy.data.objects.remove(ob)
            bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
            c = bpy.context.active_object
            c.scale = (s * 0.8,) * 3
            c.data.materials.append(mats[i % len(mats)])
            uv = c.data.uv_layers.active.data
            for poly in c.data.polygons:
                for k, li in enumerate(poly.loop_indices):
                    uv[li].uv = ((0, 0), (1, 0), (1, 1), (0, 1))[k]
            c.location.x *= WIDE
            i += 1
    wt = sc.world.node_tree
    for n in wt.nodes:
        if n.type == "BACKGROUND":
            n.inputs["Strength"].default_value = 0.6     # only lights the floating bricks: the film is see-through
            n.inputs["Color"].default_value = (0.55, 0.58, 0.7, 1)
            for l in list(n.inputs["Color"].links):
                wt.links.remove(l)
    for ob in sc.objects:
        if ob.type == "LIGHT" and ob.data.type == "SUN":
            ob.data.energy = 0.0
    sc.render.film_transparent = True
    sc.render.resolution_x, sc.render.resolution_y = 1600, 900
    cam, look, lens = SHOTS["shots"][shot]
    o = SHOTS["o_out"]
    from mathutils import Vector

    def mc(p):
        return Vector((o[0] + p[0], -(o[2] + p[2]), o[1] + p[1]))
    cobj = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cobj)
    sc.camera = cobj
    cobj.data.lens = lens
    cobj.data.clip_end = 400
    cobj.location = mc(cam)
    cobj.rotation_euler = (mc(look) - cobj.location).to_track_quat("-Z", "Y").to_euler()
    try:
        ng = bpy.data.node_groups.new("comp", "CompositorNodeTree")
        sc.compositing_node_group = ng
        rl = ng.nodes.new("CompositorNodeRLayers")
        gl = ng.nodes.new("CompositorNodeGlare")
        gl.inputs["Type"].default_value = "Bloom"
        gl.inputs["Quality"].default_value = "High"
        gl.inputs["Threshold"].default_value = 2.0
        gl.inputs["Strength"].default_value = 0.22
        gl.inputs["Size"].default_value = 0.45
        ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        go = ng.nodes.new("NodeGroupOutput")
        ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
        ng.links.new(gl.outputs["Image"], go.inputs[0])
        sc.render.use_compositing = True
    except Exception as ex:
        print("COMP FAIL", ex)
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "16"
    bpy.data.objects["void"].hide_render = True      # the comp puts the far side there instead
    sc.render.filepath = os.path.join(GW, "rift_%s_%s.exr" % (rank, shot))
    bpy.ops.render.render(write_still=True)
    print("WROTE", sc.render.filepath)
    # the mask: the void alone, white
    sc.render.use_compositing = False
    void = bpy.data.objects["void"]
    for ob in sc.objects:
        if ob.type == "MESH":
            ob.hide_render = ob is not void
    void.hide_render = False
    m = bpy.data.materials.new("mask")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Strength"].default_value = 1.0
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    void.data.materials.clear()
    void.data.materials.append(m)
    sc.cycles.samples = 16
    sc.render.filepath = os.path.join(GW, "mask_%s.exr" % shot)
    bpy.ops.render.render(write_still=True)
    print("WROTE", sc.render.filepath)


def comp(rank, shot):
    import numpy as np

    def img(name):
        im = bpy.data.images.load(os.path.join(GW, name))
        a = np.array(im.pixels[:], dtype=np.float32).reshape(im.size[1], im.size[0], 4)
        return a
    if shot == "exit":
        base, thru = img("gw_cel_exit.png"), img("gw_back_exit.png")
    else:
        base, thru = img("gw_out_%s.png" % shot), img("gw_in_%s.png" % shot)
    rf = img("rift_%s_%s.exr" % (rank, shot))
    mk = img("mask_%s.exr" % shot)[..., 3:4]
    # PNGs load as sRGB-encoded floats; work in linear
    def to_lin(a):
        return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    def to_srgb(a):
        a = np.clip(a, 0, 1)
        return np.where(a <= 0.0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - 0.055)
    b = to_lin(base[..., :3])
    t = to_lin(thru[..., :3])

    def blur(a, r):
        for _ in range(3):
            a = (np.cumsum(np.pad(a, ((r + 1, r), (0, 0), (0, 0)), mode="edge"), 0)[2 * r + 1:] -
                 np.cumsum(np.pad(a, ((r + 1, r), (0, 0), (0, 0)), mode="edge"), 0)[:-2 * r - 1]) / (2 * r + 1)
            a = (np.cumsum(np.pad(a, ((0, 0), (r + 1, r), (0, 0)), mode="edge"), 1)[:, 2 * r + 1:] -
                 np.cumsum(np.pad(a, ((0, 0), (r + 1, r), (0, 0)), mode="edge"), 1)[:, :-2 * r - 1]) / (2 * r + 1)
        return a
    deep = np.clip((blur(mk, 14) - 0.5) * 2.2, 0, 1) * mk
    hot = np.array(rgb(COLOUR[RANKS.index(rank)]), dtype=np.float32)
    # through the tear: the other side, dimmed and tinted toward the lips, a faint ripple of the rank colour
    seen = t * (0.25 + 0.75 * deep) + hot * (1 - deep) * 0.18 * mk
    out = b * (1 - mk) + seen * mk
    # the lips' glow stays on the lips: deep inside the tear it would wash out the view
    out = out * (1 - rf[..., 3:4]) + rf[..., :3] * (1 - 0.92 * deep)
    o = np.concatenate([to_srgb(out), np.ones_like(mk)], axis=2)
    im = bpy.data.images.new("comp", o.shape[1], o.shape[0])
    im.pixels[:] = o.ravel()
    im.filepath_raw = os.path.join(GW, "gate_%s_%s.png" % (rank, shot))
    im.file_format = "PNG"
    im.save()
    print("WROTE", im.filepath_raw)


if MODE == "struct":
    struct(ARGS[1], ARGS[2], ARGS[3] if len(ARGS) > 3 else "F")
elif MODE == "rift":
    rift(ARGS[1], ARGS[2])
elif MODE == "comp":
    comp(ARGS[1], ARGS[2])
