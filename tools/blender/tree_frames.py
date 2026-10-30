"""The Ash Tree's node frames, rendered in Blender (Cycles), top down: a riveted iron ring (stat), a blackened ring with
an ember inlay (ember), a gold diamond (gold), a spiked crimson octagon (key), the big emblem medallion (emblem); each
locked (dull), open (warm rim) and taken (lit). Writes 256px renders to OUTDIR/<role>_<state>.png; skilltree.py packs
them into textures/gui/tree_frames.png.

    blender -b -P tools/blender/tree_frames.py -- OUTDIR [samples]
"""
import math
import sys

import bmesh
import bpy

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUTDIR = ARGS[0] if ARGS else "E:/EFTest/game/tools/renders/frames"
SAMPLES = int(ARGS[1]) if len(ARGS) > 1 else 48


def mat(name, colour, metal=1.0, rough=0.45, emit=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*colour, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    # a little hammered unevenness in the metal
    nt = m.node_tree
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 40
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.25
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def prism(name, sides, r_out, r_in, z0, z1, m, rot=0.0, bevel=0.03):
    """a flat ring with `sides` corners (48 = round), from z0 to z1, bevelled"""
    bm = bmesh.new()
    outer, inner = [], []
    for k in range(sides):
        a = rot + 2 * math.pi * k / sides
        outer.append(bm.verts.new((r_out * math.cos(a), r_out * math.sin(a), z0)))
        inner.append(bm.verts.new((r_in * math.cos(a), r_in * math.sin(a), z0)))
    for k in range(sides):
        bm.faces.new((outer[k], outer[(k + 1) % sides], inner[(k + 1) % sides], inner[k]))
    geom = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    for v in [e for e in geom["geom"] if isinstance(e, bmesh.types.BMVert)]:
        v.co.z = z1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    me.materials.append(m)
    if bevel:
        bv = ob.modifiers.new("bevel", "BEVEL")
        bv.width = bevel
        bv.segments = 3
        bv.limit_method = "ANGLE"
    for p in me.polygons:
        p.use_smooth = True
    return ob


def disc(name, sides, r, z, m, rot=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides, radius=r, depth=0.02, location=(0, 0, z - 0.01), rotation=(0, 0, rot))
    bpy.context.object.data.materials.append(m)
    return bpy.context.object


def stud(x, y, z, r, m):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, z), segments=16, ring_count=8)
    ob = bpy.context.object
    ob.scale.z = 0.6
    ob.data.materials.append(m)
    bpy.ops.object.shade_smooth()


def spike(a, r0, r1, z, m):
    bm = bmesh.new()
    w = 0.09
    pts = [(r0 * math.cos(a - w), r0 * math.sin(a - w)), (r1 * math.cos(a), r1 * math.sin(a)), (r0 * math.cos(a + w), r0 * math.sin(a + w))]
    vs = [bm.verts.new((x, y, 0)) for x, y in pts]
    f = bm.faces.new(vs)
    geom = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in geom["geom"] if isinstance(e, bmesh.types.BMVert)]:
        v.co.z = z
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new("spike")
    bm.to_mesh(me)
    ob = bpy.data.objects.new("spike", me)
    bpy.context.collection.objects.link(ob)
    me.materials.append(m)
    bv = ob.modifiers.new("bevel", "BEVEL")
    bv.width = 0.015
    bv.segments = 2


# per state: how bright the metal is, how hot the inlay/glow is
STATE = {"locked": (0.45, 0.0), "open": (0.85, 0.5), "taken": (1.0, 1.6)}


def frame(role, state):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    lum, heat = STATE[state]
    iron = mat("iron", (0.11 * lum, 0.1 * lum, 0.095 * lum), 1, 0.5)
    dark = mat("dark", (0.025, 0.02, 0.018), 0.2, 0.8)
    if role == "stat":
        ring = mat("ring", (0.32 * lum, 0.3 * lum, 0.28 * lum), 1, 0.38)
        prism("rim", 48, 1.0, 0.72, 0, 0.16, ring)
        prism("lip", 48, 0.74, 0.66, 0, 0.1, iron)
        hot = mat("hot", (0.1, 0.05, 0.02), 0, 0.6, (1.0, 0.75, 0.45), heat * 0.35)
        prism("glow", 48, 0.69, 0.665, 0.02, 0.11, hot, bevel=0)
        for k in range(8):
            a = 2 * math.pi * k / 8 + math.pi / 8
            stud(0.86 * math.cos(a), 0.86 * math.sin(a), 0.16, 0.045, ring)
    elif role == "ember":
        ring = mat("ring", (0.13 * lum, 0.08 * lum, 0.05 * lum), 1, 0.42)
        prism("rim", 48, 1.0, 0.68, 0, 0.18, ring)
        inlay = mat("inlay", (0.15, 0.04, 0.01), 0, 0.5, (1.0, 0.35, 0.05), max(0.2, heat * 1.2))
        prism("inlay", 48, 0.88, 0.8, 0.12, 0.2, inlay, bevel=0.008)
        prism("lip", 48, 0.7, 0.62, 0, 0.1, iron)
        for k in range(12):  # flame-tongue notches round the rim
            spike(2 * math.pi * k / 12, 0.97, 1.06, 0.1, ring)
    elif role == "gold":
        g = mat("gold", (0.75 * lum, 0.52 * lum, 0.2 * lum), 1, 0.28)
        prism("rim", 4, 1.02, 0.7, 0, 0.18, g, rot=math.pi / 4 * 0 + math.pi / 2 * 0)
        prism("inner", 4, 0.74, 0.64, 0, 0.11, iron)
        gem = mat("gem", (0.6, 0.35, 0.05), 0, 0.15, (1.0, 0.7, 0.2), max(0.1, heat * 1.0))
        for k in range(4):
            a = 2 * math.pi * k / 4
            stud(0.86 * math.cos(a), 0.86 * math.sin(a), 0.18, 0.07, gem)
    elif role == "key":
        red = mat("red", (0.32 * lum, 0.05 * lum, 0.05 * lum), 1, 0.35)
        prism("rim", 8, 0.94, 0.66, 0, 0.2, red, rot=math.pi / 8)
        prism("inner", 8, 0.69, 0.6, 0, 0.12, iron, rot=math.pi / 8)
        hot = mat("hot", (0.2, 0.02, 0.02), 0, 0.5, (1.0, 0.12, 0.08), max(0.15, heat * 0.9))
        prism("seam", 8, 0.82, 0.78, 0.15, 0.22, hot, rot=math.pi / 8, bevel=0)
        for k in range(8):
            spike(math.pi / 8 * 0 + 2 * math.pi * k / 8, 0.85, 1.08, 0.14, iron)
    else:  # emblem: a double ring with notches, deep socket
        ring = mat("ring", (0.2 * lum, 0.17 * lum, 0.14 * lum), 1, 0.4)
        prism("outer", 64, 1.0, 0.86, 0, 0.18, ring)
        prism("mid", 64, 0.86, 0.8, 0, 0.1, iron)
        hot = mat("hot", (0.15, 0.05, 0.01), 0, 0.5, (1.0, 0.45, 0.1), max(0.1, heat * 0.7))
        prism("glow", 64, 0.8, 0.77, 0.02, 0.12, hot, bevel=0)
        prism("inner", 64, 0.77, 0.7, 0, 0.14, ring)
        for k in range(16):
            a = 2 * math.pi * k / 16
            stud(0.93 * math.cos(a), 0.93 * math.sin(a), 0.18, 0.028, iron)
    sides = {"gold": 4, "key": 8}.get(role, 64)
    disc("socket", sides, 0.72 if role != "key" else 0.66, -0.0, dark, rot=math.pi / 8 if role == "key" else 0)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = 256
    sc.view_settings.view_transform = "AgX"
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (0.02, 0.018, 0.016, 1)
    bpy.ops.object.light_add(type="AREA", location=(-2.5, 2.5, 4))
    key = bpy.context.object
    key.data.energy = 220
    key.data.size = 3
    key.data.color = (1.0, 0.86, 0.72)
    key.rotation_euler = (math.radians(35), 0, math.radians(-135 + 180))
    key.rotation_euler = (0.55, -0.55, 0)
    bpy.ops.object.light_add(type="AREA", location=(2.5, -2.5, 2))
    fill = bpy.context.object
    fill.data.energy = 60 + 120 * (heat > 0)
    fill.data.size = 3
    fill.data.color = (1.0, 0.5, 0.2)
    fill.rotation_euler = (-0.7, 0.7, 0)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    bpy.context.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 2.3
    cam.location = (0, 0, 10)
    sc.camera = cam
    sc.render.filepath = f"{OUTDIR}/{role}_{state}.png"
    bpy.ops.render.render(write_still=True)


for role in ("stat", "ember", "gold", "key", "emblem"):
    for state in ("locked", "open", "taken"):
        frame(role, state)
print("wrote frames to", OUTDIR)
