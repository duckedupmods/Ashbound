"""The spell particles' flipbooks, in Cycles: sixteen frames each of a blast, a tongue of flame and a roll of smoke. Fire is
rendered as heat in plain grey (white hottest) on black, so one sheet serves every element: the game's shader
(spell_fx.fsh) colours it. Smoke is lit grey on nothing. tools/vfx_atlas.py lays them out.

    blender -b -P tools/blender/vfx_flip.py -- OUT_DIR [blast flame smoke]      -> OUT_DIR/<sheet>_NN.png
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import vfx_concepts as V
import vfx_mage as M

FRAMES, RES = 16, 256
GREY = ((0.12, 0.12, 0.12), (0.4, 0.4, 0.4), (0.78, 0.78, 0.78))


def stage(transparent):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    pr = bpy.context.preferences.addons["cycles"].preferences
    try:
        pr.compute_device_type = "OPTIX"
        pr.get_devices()
        for d in pr.devices:
            d.use = d.type == "OPTIX"
        sc.cycles.device = "GPU"
    except Exception:
        pass
    sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    sc.cycles.volume_step_rate = 0.5
    sc.render.resolution_x = sc.render.resolution_y = RES
    sc.render.film_transparent = transparent
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 2.5
    cam.location = (0, -6, 0)
    cam.rotation_euler = (math.pi / 2, 0, 0)
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs[1].default_value = 0
    sc.world = w
    return sc


def blast(t):
    """a core that opens and cools, tongues thrown out of it"""
    R = M.rnd(5)
    grow = 1 - (1 - t) ** 2.4
    heat = (1 - t) ** 1.3
    M.burn((0, 0, 0), 0.34 + 0.34 * grow, GREY, 9 * heat + 0.5, density=26, scale=2.2, seed=3 + t * 1.6)
    for i in range(11):
        d = V.rdir(R, 0.2)
        o = M.burn(d * (0.2 + 0.72 * grow * R.uniform(0.75, 1.1)), (0.17 + 0.13 * grow) * R.uniform(0.8, 1.2), GREY, 6 * heat + 0.3, density=20, scale=2.8,
                   seed=20 + i + t * 1.6, stretch=(1, 1, 1.5 + grow))
        o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()


def flame(t):
    """a tongue licking upward: fat and hot, then thin and torn"""
    R = M.rnd(9)
    heat = (1 - t) ** 1.1
    for i in range(5):
        k = i / 4
        at = Vector((math.sin(k * 3 + t * 5) * 0.08 * (1 + t * 2), 0, -0.75 + k * (0.55 + t * 1.15)))
        M.burn(at, (0.36 - k * 0.2) * (1 - t * 0.45), GREY, (8 - k * 3) * heat + 0.3, density=20, scale=3, seed=i + t * 2.2, stretch=(0.85, 0.85, 1.5 + t))


def smoke(t):
    """a roll of smoke opening and thinning"""
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3
    sun.rotation_euler = (math.radians(40), math.radians(25), 0)
    bpy.context.scene.collection.objects.link(sun)
    R = M.rnd(13)
    for i in range(6):
        d = V.rdir(R)
        V.puff(d * (0.15 + 0.4 * t), 0.42 + 0.32 * t, (0.5, 0.5, 0.5), density=12 * (1 - t) ** 0.8 + 1, seed=i + t * 1.2, scale=2.6)


SHEETS = {"blast": (blast, False), "flame": (flame, False), "smoke": (smoke, True)}

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    os.makedirs(argv[0], exist_ok=True)
    for name, (fn, transparent) in SHEETS.items():
        if argv[1:] and name not in argv[1:]:
            continue
        for f in range(FRAMES):
            sc = stage(transparent)
            fn(f / (FRAMES - 1))
            sc.render.filepath = os.path.join(argv[0], "%s_%02d.png" % (name, f))
            bpy.ops.render.render(write_still=True)
        print("rendered", name, flush=True)
