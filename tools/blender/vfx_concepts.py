"""Concept stills of the curio and relic effects (CurioFx, Vfx), rendered in Cycles: Minecraft-sized figures on dark
stone at dusk, the effects built from the same pieces the game draws (soft smoke puffs, hot streaks, glowing rings,
lightning ribbons), so each still can be ported piece by piece.

    blender -b -P tools/blender/vfx_concepts.py -- OUT_DIR [names...]      -> OUT_DIR/<name>.png
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

RES = 640


# ================================================================== scene

def reset():
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
    sc.cycles.samples = 96
    sc.cycles.use_denoising = True
    sc.cycles.volume_step_rate = 0.5
    sc.cycles.max_bounces = 6
    sc.render.resolution_x = sc.render.resolution_y = RES
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast" if "AgX - Medium High Contrast" in [
        i.identifier for i in bpy.types.ColorManagedViewSettings.bl_rna.properties["look"].enum_items] else "None"
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.012, 0.014, 0.022, 1)
    bg.inputs[1].default_value = 1.0
    sc.world = w
    moon = bpy.data.objects.new("moon", bpy.data.lights.new("moon", "SUN"))
    moon.data.energy = 0.35
    moon.data.color = (0.6, 0.7, 1.0)
    moon.rotation_euler = (math.radians(55), 0, math.radians(-35))
    sc.collection.objects.link(moon)
    # dark stone ground
    bpy.ops.mesh.primitive_plane_add(size=40)
    g = bpy.context.active_object
    g.data.materials.append(floor())
    return sc


def floor():
    """dark stone laid in one-block squares, each a little different"""
    m = solid("stone", (0.045, 0.042, 0.04), 0.85)
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Scale"].default_value = 20
    br.inputs["Mortar Size"].default_value = 0.012
    br.offset = 0
    br.inputs["Color1"].default_value = (0.05, 0.047, 0.044, 1)
    br.inputs["Color2"].default_value = (0.034, 0.032, 0.03, 1)
    br.inputs["Mortar"].default_value = (0.012, 0.011, 0.01, 1)
    br.inputs["Brick Width"].default_value = 1.0
    br.inputs["Row Height"].default_value = 1.0
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (2.0, 2.0, 2.0)
    nt.links.new(tc.outputs["Object"], mp.inputs[0])
    nt.links.new(mp.outputs[0], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
    return m


def solid(name, rgb, rough=0.8):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    return m


def lin(c):
    """hex sRGB -> linear rgb"""
    out = []
    for k in (16, 8, 0):
        v = (c >> k & 255) / 255
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return tuple(out)


def box(x0, y0, z0, x1, y1, z1, mat):
    bpy.ops.mesh.primitive_cube_add()
    o = bpy.context.active_object
    o.scale = ((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2)
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    o.data.materials.append(mat)
    return o


def figure(at=(0, 0), kind="mob", yaw=0):
    """a Minecraft-sized body (1/16 block pixels): a hunched husk or a player"""
    x, y = at
    if kind == "mob":
        skin, cloth, dark = solid("husk", (0.11, 0.1, 0.08)), solid("rag", (0.07, 0.06, 0.05)), solid("dk", (0.03, 0.03, 0.03))
    else:
        skin, cloth, dark = solid("skin", (0.3, 0.17, 0.1)), solid("shirt", (0.16, 0.22, 0.24)), solid("pants", (0.08, 0.04, 0.06))
    p = 1 / 16
    parts = [(-4, -2, 24, 4, 2, 32, skin), (-4, -2, 12, 4, 2, 24, cloth), (4, -2, 12, 8, 2, 24, cloth), (-8, -2, 12, -4, 2, 24, cloth),
             (0, -2, 0, 4, 2, 12, dark), (-4, -2, 0, 0, 2, 12, dark)]
    if kind == "mob":   # arms reaching forward
        parts[2] = (4, -12, 20, 8, -2, 24, cloth)
        parts[3] = (-8, -12, 20, -4, -2, 24, cloth)
    for x0, y0, z0, x1, y1, z1, m in parts:
        o = box(x0 * p, y0 * p, z0 * p, x1 * p, y1 * p, z1 * p, m)
        o.location.rotate(__import__("mathutils").Euler((0, 0, math.radians(yaw))))
        o.rotation_euler.z = math.radians(yaw)
        o.location.x += x
        o.location.y += y
    return Vector((x, y, 1.15))


def camera(target, yaw, pitch, dist, lens=50):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    cam.data.lens = lens
    d = Vector((math.sin(math.radians(yaw)) * math.cos(math.radians(pitch)), -math.cos(math.radians(yaw)) * math.cos(math.radians(pitch)),
                math.sin(math.radians(pitch))))
    cam.location = Vector(target) + d * dist
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()


# ================================================================== effect pieces

def glow_mat(rgb, strength, soft=True, noise=0.0, seed=0, falloff=1.0):
    """additive light: emission over transparent, its edge fading (soft) and broken up by noise"""
    m = bpy.data.materials.new("glow")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*rgb, 1)
    em.inputs[1].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    add = nt.nodes.new("ShaderNodeAddShader")
    mix = nt.nodes.new("ShaderNodeMixShader")
    fac = None
    if soft:
        lw = nt.nodes.new("ShaderNodeLayerWeight")
        lw.inputs[0].default_value = 0.35
        inv = nt.nodes.new("ShaderNodeMath")
        inv.operation = "SUBTRACT"
        inv.inputs[0].default_value = 1
        nt.links.new(lw.outputs["Facing"], inv.inputs[1])
        fac = inv.outputs[0]
        if falloff != 1.0:
            pw = nt.nodes.new("ShaderNodeMath")
            pw.operation = "POWER"
            pw.inputs[1].default_value = falloff
            nt.links.new(fac, pw.inputs[0])
            fac = pw.outputs[0]
    if noise:
        tx = nt.nodes.new("ShaderNodeTexNoise")
        tx.inputs["Scale"].default_value = noise
        tx.inputs["Detail"].default_value = 6
        if "W" in tx.inputs:
            tx.noise_dimensions = "4D"
            tx.inputs["W"].default_value = seed * 3.7
        ramp = nt.nodes.new("ShaderNodeMapRange")
        ramp.inputs[1].default_value = 0.45
        ramp.inputs[2].default_value = 0.7
        nt.links.new(tx.outputs[0], ramp.inputs[0])
        if fac is not None:
            mul = nt.nodes.new("ShaderNodeMath")
            mul.operation = "MULTIPLY"
            nt.links.new(fac, mul.inputs[0])
            nt.links.new(ramp.outputs[0], mul.inputs[1])
            fac = mul.outputs[0]
        else:
            fac = ramp.outputs[0]
    nt.links.new(tr.outputs[0], add.inputs[0])
    nt.links.new(em.outputs[0], add.inputs[1])
    if fac is None:
        nt.links.new(add.outputs[0], out.inputs[0])
    else:
        nt.links.new(fac, mix.inputs[0])
        nt.links.new(tr.outputs[0], mix.inputs[1])
        nt.links.new(add.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs[0])
    return m


def smoke_mat(rgb, density, glow_rgb=None, glow=0.0, scale=3.0, seed=0):
    """a soft puff: density falling off to the edge, torn by noise; optionally glowing from inside"""
    m = bpy.data.materials.new("smoke")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (*rgb, 1)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    nt.links.new(tc.outputs["Object"], ln.inputs[0])
    fall = nt.nodes.new("ShaderNodeMapRange")
    fall.inputs[1].default_value = 1.0
    fall.inputs[2].default_value = 0.2
    nt.links.new(ln.outputs["Value"], fall.inputs[0])
    tx = nt.nodes.new("ShaderNodeTexNoise")
    tx.inputs["Scale"].default_value = scale
    tx.inputs["Detail"].default_value = 8
    tx.inputs["Roughness"].default_value = 0.6
    tx.noise_dimensions = "4D"
    tx.inputs["W"].default_value = seed * 1.37
    nt.links.new(tc.outputs["Object"], tx.inputs["Vector"])
    shape = nt.nodes.new("ShaderNodeMapRange")
    shape.inputs[1].default_value = 0.42
    shape.inputs[2].default_value = 0.75
    nt.links.new(tx.outputs[0], shape.inputs[0])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    nt.links.new(fall.outputs[0], mul.inputs[0])
    nt.links.new(shape.outputs[0], mul.inputs[1])
    d = nt.nodes.new("ShaderNodeMath")
    d.operation = "MULTIPLY"
    d.inputs[1].default_value = density * 3
    nt.links.new(mul.outputs[0], d.inputs[0])
    nt.links.new(d.outputs[0], vol.inputs["Density"])
    if glow:
        vol.inputs["Emission Color"].default_value = (*(glow_rgb or rgb), 1)
        e = nt.nodes.new("ShaderNodeMath")
        e.operation = "MULTIPLY"
        e.inputs[1].default_value = glow
        sq = nt.nodes.new("ShaderNodeMath")
        sq.operation = "POWER"
        sq.inputs[1].default_value = 2.0
        nt.links.new(mul.outputs[0], sq.inputs[0])
        nt.links.new(sq.outputs[0], e.inputs[0])
        nt.links.new(e.outputs[0], vol.inputs["Emission Strength"])
    nt.links.new(vol.outputs[0], out.inputs["Volume"])
    return m


def puff(at, r, rgb, density=6, glow_rgb=None, glow=0.0, squash=1.0, seed=None, scale=3.0):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=at)
    o = bpy.context.active_object
    o.scale = (r, r, r * squash)
    o.data.materials.append(smoke_mat(rgb, density, glow_rgb, glow, scale, seed if seed is not None else random.random() * 100))
    return o


def spark_mat(rgb, strength):
    """a spark's light: white-hot at the head (generated z 0), its colour down the body, fading out at the tail"""
    m = bpy.data.materials.new("spark")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1
    nt.links.new(sep.outputs["Z"], inv.inputs[1])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*rgb, 1)
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = tuple(0.7 + 0.3 * c for c in rgb) + (1,)
    nt.links.new(inv.outputs[0], ramp.inputs[0])
    pw = nt.nodes.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 1.6
    nt.links.new(inv.outputs[0], pw.inputs[0])
    st = nt.nodes.new("ShaderNodeMath")
    st.operation = "MULTIPLY"
    st.inputs[1].default_value = strength
    nt.links.new(pw.outputs[0], st.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(ramp.outputs[0], em.inputs[0])
    nt.links.new(st.outputs[0], em.inputs[1])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(tr.outputs[0], add.inputs[0])
    nt.links.new(em.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs[0])
    return m


def streak(at, direction, length, width, rgb, strength=30):
    """a hot spark: a needle along its flight, white-hot head fading down its tail"""
    d = Vector(direction).normalized()
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=width, radius2=width * 0.15, depth=length, location=Vector(at) - d * length / 2)
    o = bpy.context.active_object
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    o.rotation_euler.rotate_axis("X", math.radians(180))
    o.visible_shadow = False
    o.data.materials.append(spark_mat(rgb, strength * 0.14))
    return o


def halo(at, r, rgb, strength=2.0):
    """(the glow round bright things is the bloom pass now)"""
    return None


def ring(at, r, thick, rgb, strength=20, height=None, noise=6.0, seed=0, rot=(0, 0, 0)):
    """a glowing ring (flat on the ground unless turned), broken up by noise"""
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=thick, major_segments=96, minor_segments=12, location=at,
                                     rotation=rot)
    o = bpy.context.active_object
    o.scale.z = (height or thick) / thick if not any(rot) else 1
    o.data.materials.append(glow_mat(rgb, strength, soft=True, noise=noise, seed=seed))
    return o


def bolt(a, b, rgb, jag=0.3, segs=14, width=0.018, seed=1, strength=60):
    """a lightning ribbon from a to b: a jagged white core in a coloured sheath"""
    rnd = random.Random(seed)
    a, b = Vector(a), Vector(b)
    pts = [a]
    for i in range(1, segs):
        t = i / segs
        p = a.lerp(b, t)
        p += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * jag * math.sin(math.pi * t)
        pts.append(p)
    pts.append(b)
    for w, col, s in ((width, (0.85, 0.95, 1.0), strength), (width * 3.5, rgb, strength * 0.25)):
        cu = bpy.data.curves.new("bolt", "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = w
        cu.bevel_resolution = 2
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for i, p in enumerate(pts):
            sp.points[i].co = (*p, 1)
        o = bpy.data.objects.new("bolt", cu)
        bpy.context.scene.collection.objects.link(o)
        o.data.materials.append(glow_mat(col, s, soft=w > width))
    return pts


def disc(at, r, rgb, strength=4):
    """a flat glowing splat on the ground"""
    bpy.ops.mesh.primitive_circle_add(vertices=24, radius=r, fill_type="NGON", location=at)
    o = bpy.context.active_object
    o.data.materials.append(glow_mat(rgb, strength, soft=False))
    return o


def light(at, rgb, power, radius=0.3):
    l = bpy.data.objects.new("l", bpy.data.lights.new("l", "POINT"))
    l.data.energy = power
    l.data.color = rgb
    l.data.shadow_soft_size = radius
    l.location = at
    bpy.context.scene.collection.objects.link(l)


def rdir(rnd, up=0.0):
    v = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1) + up))
    return v.normalized()


# ================================================================== the effects

def fx_blight():
    """Blight Vial: rot seeping off whatever its wearer hit; vapour, a sick inner glow, ichor dripping"""
    rnd = random.Random(3)
    c = figure((0, 0), "mob", 20)
    dark, sick, ichor = lin(0x46601C), lin(0x9CE040), lin(0xB6F04A)
    for i in range(9):
        p = c + Vector((rnd.uniform(-0.35, 0.35), rnd.uniform(-0.3, 0.3), rnd.uniform(-0.7, 0.8)))
        puff(p, rnd.uniform(0.25, 0.42), dark, density=14, glow_rgb=sick, glow=14, seed=i)
    for i in range(5):   # the vapour rising off it
        p = c + Vector((rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), 0.9 + i * 0.22))
        puff(p, 0.3 + i * 0.05, lin(0x3C4A28), density=5, glow_rgb=sick, glow=1.5, seed=20 + i)
    for i in range(7):   # drips: a bright drop with a short trail
        x, y = rnd.uniform(-0.3, 0.3), rnd.uniform(-0.25, 0.25)
        z = rnd.uniform(0.25, 0.9)
        streak((x, y, z), (0, 0, -1), 0.12, 0.018, ichor, 25)
    for i in range(5):
        disc((rnd.uniform(-0.6, 0.6), rnd.uniform(-0.5, 0.5), 0.003), rnd.uniform(0.05, 0.12), ichor, 3)
    halo(c, 0.9, sick, 0.25)
    light(c + Vector((0, -0.6, 0)), sick, 60)
    camera(c + Vector((0, 0, -0.1)), 38, 8, 4.4)


def fx_brand():
    """Legion's Brand: every third blow brands the foe; teal fire bursts from the wound, a sigil ring flares round it"""
    rnd = random.Random(5)
    c = figure((0, 0), "mob", 10)
    teal, white = lin(0x38E0C8), lin(0xC8FFF6)
    hit = c + Vector((0, -0.2, 0.1))
    for i in range(26):
        d = rdir(rnd, 0.4)
        if d.y > 0.3:
            d.y = -d.y
        ln = rnd.uniform(0.25, 0.6)
        streak(hit + d * rnd.uniform(0.25, 0.9), d, ln, 0.012, teal, 40)
    for i in range(6):
        puff(hit + rdir(rnd) * 0.18, rnd.uniform(0.18, 0.3), lin(0x0E5850), density=8, glow_rgb=teal, glow=10, seed=i)
    halo(hit, 0.35, white, 6)
    ring(c + Vector((0, 0, -0.55)), 0.75, 0.025, teal, 30, noise=4, seed=2)
    ring(c + Vector((0, 0, -0.5)), 0.9, 0.012, white, 20, noise=8, seed=3)
    light(hit + Vector((0, -0.3, 0)), teal, 120)
    camera(c, 38, 8, 4.6)


def fx_lightning():
    """Stormspire Lodestone: lightning on the target, then jumping to the next foes"""
    rnd = random.Random(7)
    t1 = figure((0, 0), "mob", 0)
    t2 = figure((1.6, 1.2), "mob", -30)
    t3 = figure((-1.5, 1.6), "mob", 40)
    blue = lin(0x7FC8FF)
    bolt(t1 + Vector((0.4, 0.3, 9)), t1, blue, jag=0.6, segs=24, width=0.03, seed=1, strength=80)
    bolt(t1 + Vector((0, 0, 0.2)), t2, blue, jag=0.35, seed=2)
    bolt(t1 + Vector((0, 0, 0.1)), t3, blue, jag=0.35, seed=3)
    for t in (t1, t2, t3):
        halo(t, 0.6, blue, 1.2)
        for i in range(10):
            d = rdir(rnd, 0.6)
            streak(t + d * rnd.uniform(0.3, 0.6), d, 0.2, 0.008, lin(0xCFF2FF), 50)
        light(t + Vector((0, -0.4, 0.2)), blue, 25)
    ring(Vector((0, 0, 0.02)), 0.6, 0.03, blue, 15, noise=10, seed=4)
    camera((0, 0.6, 1.2), 10, 14, 7.5)


def fx_frost():
    """Rime Band / Hourglass: the foe frozen in a breath of cold; ice glints thrown off, frost spreading on the ground"""
    rnd = random.Random(9)
    c = figure((0, 0), "mob", 15)
    ice, pale = lin(0xBFE4F8), lin(0xE8F8FF)
    for i in range(10):
        p = Vector((rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), rnd.uniform(0.1, 0.5)))
        puff(p, rnd.uniform(0.3, 0.5), ice, density=5, squash=0.6, seed=i)
    for i in range(24):
        d = rdir(rnd, 0.5)
        streak(c + d * rnd.uniform(0.3, 0.8), d, rnd.uniform(0.1, 0.25), 0.01, pale, 30)
    for i in range(14):   # ice shards on the body
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.04, depth=rnd.uniform(0.12, 0.25),
                                        location=c + Vector((rnd.uniform(-0.28, 0.28), -0.14, rnd.uniform(-0.7, 0.5))),
                                        rotation=(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 3)))
        bpy.context.active_object.data.materials.append(glow_mat(ice, 4, soft=True))
    ring(Vector((0, 0, 0.01)), 0.8, 0.12, ice, 4, noise=5, seed=6)
    light(c + Vector((0, -0.6, 0)), ice, 80)
    camera(c, 38, 10, 4.5)


def fx_void():
    """Void Pearl / Rift Key: violet light rushing in where you leave, bursting out where you land"""
    rnd = random.Random(11)
    a = Vector((-1.2, 0, 1.15))
    b = figure((1.2, 0), "player", -20)
    violet, deep = lin(0xB070FF), lin(0x3A1470)
    for i in range(28):   # rushing in to where you were
        d = rdir(rnd)
        streak(a + d * rnd.uniform(0.15, 0.9), -d, rnd.uniform(0.2, 0.5), 0.01, violet, 35)
    puff(a, 0.35, deep, density=20, glow_rgb=violet, glow=6, seed=1)
    halo(a, 0.3, lin(0xE0C8FF), 5)
    for i in range(30):   # bursting out where you land
        d = rdir(rnd, 0.3)
        streak(b + d * rnd.uniform(0.4, 1.0), d, rnd.uniform(0.2, 0.45), 0.01, violet, 35)
    for i in range(6):
        puff(b + rdir(rnd) * 0.35, 0.3, deep, density=10, glow_rgb=violet, glow=3, seed=10 + i)
    for i in range(12):   # the trail between
        t = i / 11
        p = a.lerp(b, t) + Vector((0, 0, math.sin(math.pi * t) * 0.15))
        streak(p, (1, 0, 0), 0.25, 0.008, violet, 25)
    light(a, violet, 100)
    light(b + Vector((0, -0.5, 0)), violet, 100)
    camera((0, 0, 1.1), 0, 6, 5.8)


def fx_coal():
    """Kiln-Father's Coal: the coal flares; a ring of fire runs out from your feet, embers come off you while it burns"""
    rnd = random.Random(13)
    c = figure((0, 0), "player", 15)
    fire, hot, smoke = lin(0xE8742C), lin(0xFFC070), lin(0x1A1210)
    for i in range(22):
        a = i / 22 * math.tau
        p = Vector((math.cos(a) * 1.0, math.sin(a) * 1.0, 0.18))
        puff(p, rnd.uniform(0.18, 0.28), smoke, density=6, glow_rgb=fire, glow=14, squash=1.6, seed=i, scale=4)
    ring(Vector((0, 0, 0.02)), 1.0, 0.05, hot, 25, noise=5, seed=1)
    for i in range(30):
        p = c + Vector((rnd.uniform(-0.35, 0.35), rnd.uniform(-0.3, 0.3), rnd.uniform(-0.9, 1.2)))
        streak(p, (rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), 1), rnd.uniform(0.08, 0.18), 0.008, hot, 40)
    halo(c, 0.7, fire, 0.4)
    light((0, 0, 0.4), fire, 250, 1.0)
    camera(c + Vector((0, 0, -0.3)), 20, 14, 5.0)


def fx_warhorn():
    """Warhorn of the Last Keep: the call rolls out; rings of warm light and dust, allies kindled"""
    rnd = random.Random(15)
    c = figure((0, 0), "player", 0)
    a1 = figure((-1.8, 1.0), "player", 30)
    a2 = figure((1.9, 0.8), "player", -30)
    warm, dust = lin(0xF08A30), lin(0x8A7660)
    ring(Vector((0, 0, 0.15)), 1.5, 0.06, warm, 30, height=0.2, noise=4, seed=1)
    ring(Vector((0, 0, 0.1)), 2.3, 0.04, lin(0xFFD090), 18, height=0.12, noise=6, seed=2)
    for i in range(30):   # the dust wall riding the outer ring
        a = i / 30 * math.tau
        puff(Vector((math.cos(a) * 2.6, math.sin(a) * 2.6, 0.25)), 0.35, dust, density=3, squash=0.8, seed=i)
    for t in (a1, a2):
        for i in range(8):
            p = t + Vector((rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.uniform(-0.8, 0.9)))
            streak(p, (0, 0, 1), 0.12, 0.008, lin(0xFFB050), 40)
        halo(t, 0.55, warm, 0.6)
        light(t + Vector((0, -0.4, 0)), warm, 60)
    light((0, 0, 0.6), warm, 200, 1.0)
    camera((0, 0.5, 0.6), 10, 22, 8.5)


def fx_acorn():
    """Rotwood Acorn: roots burst up where you aim; a ring of green-gold light runs out, leaves and seed-sparks thrown up"""
    rnd = random.Random(17)
    figure((0.5, 0.4), "mob", 0)
    figure((-0.6, 0.2), "mob", 20)
    green, gold, moss = lin(0x7FC23A), lin(0xC8E86A), lin(0x2A3A18)
    ring(Vector((0, 0, 0.02)), 1.6, 0.06, green, 25, height=0.04, noise=4, seed=1)
    ring(Vector((0, 0, 0.02)), 1.0, 0.03, gold, 20, height=0.03, noise=7, seed=2)
    root = solid("root", (0.09, 0.06, 0.035), 0.9)
    for i in range(12):   # roots bursting up through the stone
        a = rnd.uniform(0, math.tau)
        r = rnd.uniform(0.2, 1.3)
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.08, depth=rnd.uniform(0.6, 1.4),
                                        location=(math.cos(a) * r, math.sin(a) * r, 0.25),
                                        rotation=(rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), 0))
        bpy.context.active_object.data.materials.append(root)
    for i in range(30):
        d = rdir(rnd, 1.2)
        streak(Vector((0, 0, 0.3)) + d * rnd.uniform(0.3, 1.4), d, 0.18, 0.01, gold, 30)
    for i in range(8):
        puff(Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0.2)), 0.35, moss, density=4, glow_rgb=green, glow=2, squash=0.6, seed=i)
    light((0, -0.5, 0.5), green, 150, 1.0)
    camera((0, 0.2, 0.6), 15, 20, 6.5)


def fx_holy():
    """Pale Abbot's Wick: a ward of candle-light; a gold circle on the ground, motes rising, the wearer lit"""
    rnd = random.Random(19)
    c = figure((0, 0), "player", 10)
    gold, pale = lin(0xF2B04A), lin(0xFFE7A0)
    ring(Vector((0, 0, 0.02)), 2.2, 0.04, gold, 30, height=0.03, noise=3, seed=1)
    ring(Vector((0, 0, 0.02)), 2.05, 0.015, pale, 25, height=0.015, noise=0, seed=2)
    for i in range(16):   # little flames round the circle
        a = i / 16 * math.tau
        puff(Vector((math.cos(a) * 2.2, math.sin(a) * 2.2, 0.12)), 0.1, lin(0x402008), density=8, glow_rgb=gold, glow=40, squash=1.8, seed=i)
    for i in range(40):
        p = Vector((rnd.uniform(-2, 2), rnd.uniform(-2, 2), rnd.uniform(0.1, 2.4)))
        if p.xy.length < 2.1:
            streak(p, (0, 0, 1), 0.1, 0.007, pale, 35)
    halo(c, 0.75, pale, 0.5)
    light((0, 0, 1.6), gold, 200, 1.5)
    camera((0, 0, 0.8), 15, 22, 8)


def fx_plume():
    """Gryphon Plume: the jump in the air; a ring of wind-dust under you, feathers of light"""
    rnd = random.Random(21)
    c = figure((0, 0), "player", 0)
    for o in bpy.context.scene.objects:   # the player up in the air
        if o.type == "MESH" and o.location.z > 0.01 and o.data.materials and o.data.materials[0].name.startswith(("skin", "shirt", "pants")):
            o.location.z += 1.2
    dust, pale = lin(0xD8D2C4), lin(0xFFF6D8)
    for i in range(16):
        a = i / 16 * math.tau
        puff(Vector((math.cos(a) * 0.7, math.sin(a) * 0.7, 1.15)), 0.22, dust, density=5, squash=0.5, seed=i)
    ring(Vector((0, 0, 1.15)), 0.6, 0.02, pale, 15, height=0.02, noise=5, seed=1)
    for i in range(12):
        d = rdir(rnd)
        d.z = -abs(d.z)
        streak(Vector((0, 0, 1.15)) + d * 0.5, d, 0.2, 0.008, pale, 30)
    light((0, -0.6, 1.4), pale, 60)
    for i in range(10):   # dust kicked off the ground far below
        a = i / 10 * math.tau
        puff(Vector((math.cos(a) * 0.5, math.sin(a) * 0.5, 0.05)), 0.25, dust, density=2, squash=0.4, seed=40 + i)
    camera((0, 0, 1.3), 25, 10, 6.8)


EFFECTS = {"blight": fx_blight, "brand": fx_brand, "lightning": fx_lightning, "frost": fx_frost, "void": fx_void, "coal": fx_coal,
           "warhorn": fx_warhorn, "acorn": fx_acorn, "holy": fx_holy, "plume": fx_plume}

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    OUT, ONLY = argv[0], argv[1:]
    os.makedirs(OUT, exist_ok=True)
    for name, fn in EFFECTS.items():
        if ONLY and name not in ONLY:
            continue
        sc = reset()
        fn()
        sc.render.filepath = os.path.join(OUT, name + ".png")
        bpy.ops.render.render(write_still=True)
        print("rendered", name)
