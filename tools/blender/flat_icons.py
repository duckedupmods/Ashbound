"""The flat passes tools/aseicons.py draws the pixel-art icons from, for a batch of chunky models (weaponforge's
preview copies): each laid as weapon_icons.py lays it (the classic diagonal, a shield turned a little, a bow on its
item square), seen without light, three hard-edged 112 px passes:

  <name>_alb.png   the model's own colours (its texture, unlit), alpha = the shape
  <name>_nrm.png   which way each pixel faces, seen from the camera (rgb = xyz * 0.5 + 0.5)
  <name>_glw.png   white where the model glows

    blender -b -P tools/blender/flat_icons.py -- BATCH.json OUTDIR"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, 'E:/Ashbound/tools/blender')
import preview_vox as P  # noqa: E402

RES = 112          # 14 cells of 8: the 16 px icon is these 14 inside its outline


def shader(img, mode):
    m = bpy.data.materials.new(mode)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(img, check_existing=True)
    tex.interpolation = "Closest"
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[1].default_value = 1.0
    if mode == "alb":
        nt.links.new(tex.outputs[0], em.inputs[0])
    elif mode == "nrm":
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        vt = nt.nodes.new("ShaderNodeVectorTransform")
        vt.vector_type, vt.convert_from, vt.convert_to = "NORMAL", "WORLD", "CAMERA"
        nt.links.new(geo.outputs["Normal"], vt.inputs[0])
        mad = nt.nodes.new("ShaderNodeVectorMath")
        mad.operation = "MULTIPLY_ADD"
        mad.inputs[1].default_value = (0.5, 0.5, 0.5)
        mad.inputs[2].default_value = (0.5, 0.5, 0.5)
        nt.links.new(vt.outputs[0], mad.inputs[0])
        nt.links.new(mad.outputs[0], em.inputs[0])
    else:
        em.inputs[0].default_value = (1, 1, 1, 1) if mode == "glw1" else (0, 0, 0, 1)
    mix = nt.nodes.new("ShaderNodeMixShader")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    nt.links.new(tex.outputs[1], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    try:
        m.blend_method = "CLIP"
        m.surface_render_method = "DITHERED"
    except Exception:
        pass
    return m


def frame(root, yaw, pitch, fixed):
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in root.children for c in o.bound_box]
    if fixed:
        P.camera(Vector((0.5, -0.5, 0.5)), yaw, pitch, ortho=1.0)
        return
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    centre = (lo + hi) / 2
    P.camera(centre, yaw, pitch, ortho=1.0)
    cam = bpy.data.objects['cam']
    bpy.context.view_layer.update()
    right, up = cam.matrix_world.to_3x3().col[0], cam.matrix_world.to_3x3().col[1]
    xs = [(p - centre).dot(right) for p in pts]
    ys = [(p - centre).dot(up) for p in pts]
    shift = right * (max(xs) + min(xs)) / 2 + up * (max(ys) + min(ys)) / 2
    P.camera(centre + shift, yaw, pitch, ortho=max(max(xs) - min(xs), max(ys) - min(ys)) * 1.02)


def main():
    args = sys.argv[sys.argv.index('--') + 1:]
    batch, outdir = json.load(open(args[0])), args[1]
    os.makedirs(outdir, exist_ok=True)
    for name, yaw, pitch, fixed, diagonal in batch:
        P.reset()
        sc = bpy.context.scene
        sc.render.resolution_x = sc.render.resolution_y = RES
        sc.render.filter_size = 0.0
        try:
            sc.eevee.taa_render_samples = 1
        except AttributeError:
            pass
        sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0
        root = P.load(name, 0)
        if diagonal:
            root.rotation_euler = (0, math.radians(-45), 0)
        frame(root, yaw, pitch, fixed)
        img = os.path.join(P.VOX, "%s_f0.png" % name)
        parts = [(o, "fire" in o.name or "glow" in o.name) for o in root.children]
        for mode in ("alb", "nrm", "glw"):
            mats = {}
            for o, glow in parts:
                key = ("glw1" if glow else "glw0") if mode == "glw" else mode
                if key not in mats:
                    mats[key] = shader(img, key)
                o.data.materials.clear()
                o.data.materials.append(mats[key])
            P.render(os.path.join(outdir, "%s_%s.png" % (name, mode)))
        print("flat", name)


main()
