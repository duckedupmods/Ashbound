"""The Ash Tree overview's painting, rendered in Blender (Cycles): a charred ash tree whose trunk and branches follow
the exact paths in skill_tree.json's "overview" (the game draws the fire and the emblems on top, on the same paths).

    blender -b -P tools/blender/tree_ui.py -- OUT.png [samples]
"""
import json
import math
import random
import sys

import bpy
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = ARGS[0] if ARGS else "E:/EFTest/game/tools/renders/tree_bg.png"
SAMPLES = int(ARGS[1]) if len(ARGS) > 1 else 96
TREE = json.load(open("E:/EFTest/game/src/main/resources/ashbound/skill_tree.json", encoding="utf-8"))["overview"]
rnd = random.Random(7)


def P(x, y, z=0.0):
    """overview space (1600x900, y down) to the scene (x right, z up, 100 px a metre)"""
    return Vector((x / 100, z, -y / 100))


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def node(nt, kind, **kw):
    n = nt.nodes.new(kind)
    for k, v in kw.items():
        setattr(n, k, v)
    return n


def bark_material():
    m = bpy.data.materials.new("bark")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    coord = node(nt, "ShaderNodeTexCoord")
    # long cracked grain: a wave texture stretched along the limb plus noise
    noise = node(nt, "ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 9
    noise.inputs["Detail"].default_value = 8
    nt.links.new(coord.outputs["Object"], noise.inputs["Vector"])
    vor = node(nt, "ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE")
    vor.inputs["Scale"].default_value = 30
    nt.links.new(coord.outputs["Object"], vor.inputs["Vector"])
    ramp = node(nt, "ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.018, 0.014, 0.013, 1)
    ramp.color_ramp.elements[1].color = (0.06, 0.045, 0.038, 1)
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.85
    bump = node(nt, "ShaderNodeBump")
    bump.inputs["Strength"].default_value = 1.0
    mix = node(nt, "ShaderNodeMath", operation="ADD")
    nt.links.new(vor.outputs["Distance"], mix.inputs[0])
    nt.links.new(noise.outputs["Fac"], mix.inputs[1])
    nt.links.new(mix.outputs["Value"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    # embers smouldering in the deepest cracks, a few, more of them low down
    edge = node(nt, "ShaderNodeMath", operation="LESS_THAN")
    edge.inputs[1].default_value = 0.03
    nt.links.new(vor.outputs["Distance"], edge.inputs[0])
    patch = node(nt, "ShaderNodeTexNoise")
    patch.inputs["Scale"].default_value = 2.2
    nt.links.new(coord.outputs["Object"], patch.inputs["Vector"])
    pr = node(nt, "ShaderNodeMapRange")
    pr.inputs["From Min"].default_value = 0.68
    pr.inputs["From Max"].default_value = 0.86
    nt.links.new(patch.outputs["Fac"], pr.inputs["Value"])
    glow = node(nt, "ShaderNodeMath", operation="MULTIPLY")
    nt.links.new(edge.outputs["Value"], glow.inputs[0])
    nt.links.new(pr.outputs["Result"], glow.inputs[1])
    strength = node(nt, "ShaderNodeMath", operation="MULTIPLY")
    strength.inputs[1].default_value = 0.0  # the game draws the fire
    nt.links.new(glow.outputs["Value"], strength.inputs[0])
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.16, 0.02, 1)
    nt.links.new(strength.outputs["Value"], bsdf.inputs["Emission Strength"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m


def limb(name, pts, w0, w1, mat, depth=0.0, gnarl=0.0):
    """a tapered tube along a polyline (overview coords), slightly gnarled"""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 1.0
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new("NURBS")
    sp.points.add(len(pts) - 1)
    for i, (x, y) in enumerate(pts):
        u = i / (len(pts) - 1)
        wob = (rnd.random() - 0.5) * 0.04 * (1 - u) if 0 < i < len(pts) - 1 else 0
        v = P(x, y, depth + wob)
        sp.points[i].co = (v.x, v.y, v.z, 1)
        sp.points[i].radius = (w0 + (w1 - w0) * u) / 200
    sp.use_endpoint_u = True
    sp.order_u = 3
    ob = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    if gnarl:
        cu.resolution_u = 10
        cu.bevel_resolution = 6
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        bpy.ops.object.convert(target="MESH")
        ob.select_set(False)
        tex = bpy.data.textures.get("gnarl") or bpy.data.textures.new("gnarl", "DISTORTED_NOISE")
        tex.noise_scale = 0.4
        tex.distortion = 0.9
        d = ob.modifiers.new("gnarl", "DISPLACE")
        d.texture = tex
        d.strength = gnarl
        d.mid_level = 0.5
        bpy.ops.object.shade_smooth()
    return ob


def twigs(pts, w, mat, n, spread=60, length=90):
    """little side shoots off a limb, burnt bare"""
    for k in range(n):
        i = rnd.randint(2, len(pts) - 3)
        bx, by = pts[i]
        side = rnd.choice((-1, 1))
        a = math.radians(rnd.uniform(25, 70)) * side
        dx, dy = pts[min(len(pts) - 1, i + 1)][0] - bx, pts[min(len(pts) - 1, i + 1)][1] - by
        base = math.atan2(dy, dx)
        L = rnd.uniform(0.5, 1.0) * length
        mid = (bx + math.cos(base + a * 0.6) * L * 0.5, by + math.sin(base + a * 0.6) * L * 0.5 - spread * 0.2)
        end = (bx + math.cos(base + a) * L, by + math.sin(base + a) * L - spread * 0.3)
        limb(f"twig{k}", [(bx, by), mid, end], w, 1.2, mat, depth=rnd.uniform(-0.1, 0.1))


def scene():
    clear()
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for t in ("OPTIX", "CUDA", "HIP"):
            try:
                prefs.compute_device_type = t
                prefs.get_devices()
                if any(d.type == t for d in prefs.devices):
                    for d in prefs.devices:
                        d.use = True
                    sc.cycles.device = "GPU"
                    break
            except TypeError:
                continue
    except Exception:
        pass
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = 2400, 900  # 400 spare each side
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy" if "AgX - Punchy" in [i.identifier for i in sc.view_settings.bl_rna.properties["look"].enum_items] else "None"
    # the sky behind: near black, warmer low down (a world gradient)
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = next(n for n in nt.nodes if n.type == "BACKGROUND")
    bg.inputs["Strength"].default_value = 1
    bg.inputs["Color"].default_value = (0.0012, 0.0009, 0.0008, 1)
    # haze the light can catch in
    vol = bpy.data.materials.new("haze")
    vol.use_nodes = True
    vn = vol.node_tree
    for n in list(vn.nodes):
        if n.type == "BSDF_PRINCIPLED":
            vn.nodes.remove(n)
    pv = vn.nodes.new("ShaderNodeVolumePrincipled")
    pv.inputs["Density"].default_value = 0.006
    pv.inputs["Color"].default_value = (0.9, 0.7, 0.6, 1)
    vn.links.new(pv.outputs["Volume"], next(n for n in vn.nodes if n.type == "OUTPUT_MATERIAL").inputs["Volume"])
    bpy.ops.mesh.primitive_cube_add(size=1, location=P(800, 450, 0))
    box = bpy.context.object
    box.scale = (30, 6, 14)
    box.data.materials.append(vol)
    box.visible_shadow = False


def build():
    scene()
    mat = bark_material()
    for i, b in enumerate(TREE["bark"]):
        limb(f"bark{i}", b["pts"], b["w"][0], b["w"][1], mat, depth=rnd.uniform(-0.2, 0.2), gnarl=0.03 if b["w"][0] > 20 else 0.0)
    t = TREE["trunk"]
    tp = t["pts"] + [(800, 480), (800, 450)]
    limb("trunk", tp, t["w"][0] * 1.15, t["w"][1] * 0.75, mat, gnarl=0.09)
    # a second, twisting strand round the trunk so it reads as a gnarled bole, not a pipe
    for k in range(3):
        strand = [(x + math.sin(i * 0.6 + k * 2.1) * 26 * (1 - i / len(tp)), y) for i, (x, y) in enumerate(tp)]
        limb(f"strand{k}", strand, t["w"][0] * 0.5, t["w"][1] * 0.35, mat, depth=0.18 * math.cos(k * 2.1), gnarl=0.05)
    for aid, b in TREE["branches"].items():
        limb(f"branch_{aid}", b["pts"], b["w"][0] * 1.1, b["w"][1], mat, gnarl=0.035)
        twigs(b["pts"], 7, mat, 5)
    # a mound of ash and coals at the foot
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=160, y_subdivisions=60, size=1, location=P(800, 960, 0))
    heap = bpy.context.object
    heap.scale = (24, 8, 1)
    for v in heap.data.vertices:
        dx, dy = v.co.x * 24 / 6.0, v.co.y * 8 / 2.5  # the grid's own scale (matrix_world isn't updated yet)
        v.co.z += 1.15 * math.exp(-(dx * dx + dy * dy)) / heap.scale.z
    tex = bpy.data.textures.new("ash", "CLOUDS")
    tex.noise_scale = 0.35
    d = heap.modifiers.new("ash", "DISPLACE")
    d.texture = tex
    d.strength = 0.18
    ash = bpy.data.materials.new("ash")
    ash.use_nodes = True
    ab = next(n for n in ash.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    ab.inputs["Base Color"].default_value = (0.022, 0.019, 0.018, 1)
    ab.inputs["Roughness"].default_value = 1.0
    heap.data.materials.append(ash)
    bpy.ops.object.shade_smooth()
    # light: embers at the foot, a cold rim from behind so every branch has an edge, a faint key from above
    bpy.ops.object.light_add(type="POINT", location=P(800, 820, -1.2))
    bpy.context.object.data.energy = 600
    bpy.context.object.data.color = (1.0, 0.42, 0.12)
    bpy.context.object.data.shadow_soft_size = 1.5
    bpy.ops.object.light_add(type="AREA", location=P(800, 300, 4))
    rim = bpy.context.object
    rim.data.energy = 900
    rim.data.size = 4
    rim.data.color = (0.55, 0.6, 0.85)
    rim.rotation_euler = (math.radians(-90), 0, 0)
    bpy.ops.object.light_add(type="AREA", location=P(800, -300, -6))
    key = bpy.context.object
    key.data.energy = 120
    key.data.size = 10
    key.data.color = (1.0, 0.75, 0.55)
    key.rotation_euler = (math.radians(60), 0, 0)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    bpy.context.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 24
    cam.location = P(800, 450, -20)
    cam.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.scene.camera = cam
    bpy.context.scene.render.filepath = OUT
    bpy.ops.render.render(write_still=True)


build()
print("wrote", OUT)
