"""Concept stills of the mage's magic (Spells), in Cycles: one bolt in flight and one landing for each family of elements,
the white school, the summoners, and the Joined staffs' R skills. Built from the same pieces as vfx_concepts.py, plus the
things those lacked: comet tails, crystal, liquid, spell circles on the ground, shafts of light.

    blender -b -P tools/blender/vfx_mage.py -- OUT_DIR [names...]      -> OUT_DIR/<name>.png
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import vfx_concepts as V

W, H, SAMPLES = 960, 540, 64
FEET = -3.4
HIT = 3.4
HEIGHT = 1.3


def rnd(seed):
    return random.Random(seed)


def smooth(o):
    for p in o.data.polygons:
        p.use_smooth = True


def ball(at, r, rgb, strength, falloff=1.0, squash=1.0):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=r, location=at)
    o = bpy.context.active_object
    o.scale.z = squash
    smooth(o)
    o.visible_shadow = False
    o.data.materials.append(V.glow_mat(rgb, strength, soft=True, falloff=falloff))
    return o


def fire_mat(pal, strength, density, scale, seed):
    """a volume that burns: heat falls off from the middle and is torn by noise, and heat picks the colour, from the
    smoke at the edge through pal (deep, mid, hot) to white; only the hot part gives light"""
    m = bpy.data.materials.new("fire")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (0.012, 0.01, 0.012, 1)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    nt.links.new(tc.outputs["Object"], ln.inputs[0])
    warp = nt.nodes.new("ShaderNodeTexNoise")
    warp.inputs["Scale"].default_value = scale * 0.6
    warp.inputs["Detail"].default_value = 3
    warp.noise_dimensions = "4D"
    warp.inputs["W"].default_value = seed * 2.1
    nt.links.new(tc.outputs["Object"], warp.inputs["Vector"])
    mixv = nt.nodes.new("ShaderNodeVectorMath")
    mixv.operation = "ADD"
    nt.links.new(tc.outputs["Object"], mixv.inputs[0])
    sc = nt.nodes.new("ShaderNodeVectorMath")
    sc.operation = "SCALE"
    sc.inputs["Scale"].default_value = 0.8
    nt.links.new(warp.outputs["Color"], sc.inputs[0])
    nt.links.new(sc.outputs[0], mixv.inputs[1])
    tx = nt.nodes.new("ShaderNodeTexNoise")
    tx.inputs["Scale"].default_value = scale
    tx.inputs["Detail"].default_value = 10
    tx.inputs["Roughness"].default_value = 0.62
    tx.noise_dimensions = "4D"
    tx.inputs["W"].default_value = seed * 1.3
    nt.links.new(mixv.outputs[0], tx.inputs["Vector"])
    a = nt.nodes.new("ShaderNodeMapRange")
    a.inputs[1].default_value = 1.0
    a.inputs[2].default_value = 0.3
    nt.links.new(ln.outputs["Value"], a.inputs[0])
    b = nt.nodes.new("ShaderNodeMapRange")
    b.inputs[1].default_value = 0.34
    b.inputs[2].default_value = 0.66
    b.inputs[3].default_value = -0.9
    b.inputs[4].default_value = 0.7
    nt.links.new(tx.outputs[0], b.inputs[0])
    heat = nt.nodes.new("ShaderNodeMath")
    heat.operation = "ADD"
    heat.use_clamp = True
    nt.links.new(a.outputs[0], heat.inputs[0])
    nt.links.new(b.outputs[0], heat.inputs[1])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position, cr.elements[0].color = 0.0, (0, 0, 0, 1)
    cr.elements[1].position, cr.elements[1].color = 1.0, (1, 1, 1, 1)
    for t, c in ((0.3, pal[0]), (0.55, pal[1]), (0.78, pal[2])):
        cr.elements.new(t).color = (*c, 1)
    nt.links.new(heat.outputs[0], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], vol.inputs["Emission Color"])
    d = nt.nodes.new("ShaderNodeMapRange")
    d.inputs[1].default_value = 0.04
    d.inputs[2].default_value = 0.3
    d.inputs[4].default_value = density * 0.1
    nt.links.new(heat.outputs[0], d.inputs[0])
    nt.links.new(d.outputs[0], vol.inputs["Density"])
    e = nt.nodes.new("ShaderNodeMapRange")
    e.inputs[1].default_value = 0.12
    e.inputs[2].default_value = 0.9
    e.inputs[4].default_value = strength * 0.55
    e.interpolation_type = "SMOOTHERSTEP"
    nt.links.new(heat.outputs[0], e.inputs[0])
    nt.links.new(e.outputs[0], vol.inputs["Emission Strength"])
    nt.links.new(vol.outputs[0], out.inputs["Volume"])
    return m


def burn(at, r, pal, strength=30, density=30, scale=2.4, seed=0, stretch=(1, 1, 1)):
    """a mass of fire in pal's colours, longer along an axis if stretched"""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=at)
    o = bpy.context.active_object
    o.scale = (r * stretch[0], r * stretch[1], r * stretch[2])
    o.data.materials.append(fire_mat(pal, strength, density, scale, seed))
    return o


def tube(pts, width, rgb, strength, soft=True):
    cu = bpy.data.curves.new("tube", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = width
    cu.bevel_resolution = 2
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*p, 1)
    o = bpy.data.objects.new("tube", cu)
    bpy.context.scene.collection.objects.link(o)
    o.visible_shadow = False
    o.data.materials.append(V.glow_mat(rgb, strength, soft=soft))
    return o


def beam_mat(rgb, strength, rim=False):
    """light with no surface: only along the edge of a dome (rim), or thickest through the middle of a shaft and gone at its top"""
    m = bpy.data.materials.new("beam")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs[0].default_value = 0.5
    edge = nt.nodes.new("ShaderNodeMath")
    edge.operation = "POWER"
    edge.inputs[1].default_value = 3.0
    if rim:
        nt.links.new(lw.outputs["Facing"], edge.inputs[0])
    else:
        inv = nt.nodes.new("ShaderNodeMath")
        inv.operation = "SUBTRACT"
        inv.inputs[0].default_value = 1
        nt.links.new(lw.outputs["Facing"], inv.inputs[1])
        nt.links.new(inv.outputs[0], edge.inputs[0])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    up = nt.nodes.new("ShaderNodeMath")
    up.operation = "SUBTRACT"
    up.inputs[0].default_value = 1
    nt.links.new(sep.outputs["Z"], up.inputs[1])
    pw = nt.nodes.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 0.0 if rim else 1.5
    nt.links.new(up.outputs[0], pw.inputs[0])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    nt.links.new(edge.outputs[0], mul.inputs[0])
    nt.links.new(pw.outputs[0], mul.inputs[1])
    st = nt.nodes.new("ShaderNodeMath")
    st.operation = "MULTIPLY"
    st.inputs[1].default_value = strength
    nt.links.new(mul.outputs[0], st.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*rgb, 1)
    nt.links.new(st.outputs[0], em.inputs[1])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(tr.outputs[0], add.inputs[0])
    nt.links.new(em.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs[0])
    return m


def shaft(at, r, h, rgb, strength=8):
    """a shaft of light standing on the ground, hottest at its foot, gone at its top"""
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r, depth=h, end_fill_type="NOTHING", location=(at[0], at[1], at[2] + h / 2))
    o = bpy.context.active_object
    smooth(o)
    o.visible_shadow = False
    o.data.materials.append(beam_mat(rgb, strength))
    return o


SOUL = (V.lin(0x2A0A50), V.lin(0x9A28C8), V.lin(0xE8A0FF))


def tick(at, a, r0, r1, wide, rgb, strength):
    """one block of a spell circle's writing, flat on the ground"""
    c = (r0 + r1) / 2
    bpy.ops.mesh.primitive_plane_add(size=1, location=(at[0] + math.cos(a) * c, at[1] + math.sin(a) * c, at[2] + 0.015), rotation=(0, 0, a))
    o = bpy.context.active_object
    o.scale = (r1 - r0, wide, 1)
    o.visible_shadow = False
    o.data.materials.append(V.glow_mat(rgb, strength, soft=False))


def sigil(at, r, rgb, hot, seed=1, strength=26):
    """a spell circle: rings, a band of writing between them, spokes, and a star"""
    R = rnd(seed)
    at = Vector(at)
    for k, t in ((1.0, 0.03), (0.86, 0.016), (0.58, 0.02), (0.22, 0.014)):
        V.ring(at + Vector((0, 0, 0.02)), r * k, t, hot if k == 1.0 else rgb, strength, height=0.012, noise=0)
    n = int(44 * r / 3.5)
    for i in range(n):   # the writing
        a = i / n * math.tau
        if R.random() < 0.82:
            tick(at, a, r * (0.885 + R.random() * 0.02), r * (0.945 + R.random() * 0.03), r * R.uniform(0.012, 0.03), rgb, strength * 0.8)
    pts = [(at.x + math.cos(i * 3 / 7 * math.tau) * r * 0.86, at.y + math.sin(i * 3 / 7 * math.tau) * r * 0.86, at.z + 0.02) for i in range(8)]
    tube(pts, 0.012, rgb, strength * 0.7, soft=False)   # the seven-point star
    for i in range(7):
        a = i / 7 * math.tau + 0.2
        V.ring(at + Vector((math.cos(a) * r * 0.72, math.sin(a) * r * 0.72, 0.02)), r * 0.07, 0.01, hot, strength, height=0.01, noise=0)
    V.light(at + Vector((0, 0, 0.5)), rgb, 90 * r, r)


def caster(x=FEET, y=0.0, staff=(0.25, 0.2, 0.25)):
    """a robed player facing +x, their staff thrust out; returns the staff's tip"""
    V.figure((x, y), "player", 90)
    wood = V.solid("staff", (0.05, 0.03, 0.02), 0.5)
    a, b = Vector((x + 0.3, y + 0.25, 0.25)), Vector((x + 0.72, y + 0.25, 1.75))
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.035, depth=d.length, location=(a + b) / 2)
    o = bpy.context.active_object
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    o.data.materials.append(wood)
    V.box(x + 0.15, y + 0.2, 1.05, x + 0.62, y + 0.32, 1.2, V.solid("sleeve", (0.16, 0.22, 0.24)))   # the arm out
    ball(b, 0.09, staff, 20)
    return b


def husk(x=HIT, y=0.0, yaw=-90):
    return V.figure((x, y), "mob", yaw)


def muzzle(tip, rgb, hot, seed=1, n=10, pal=None):
    """the flash at the staff as it throws"""
    R = rnd(seed)
    if pal:
        burn(tip, 0.42, pal, 26, seed=seed)
    else:
        ball(tip, 0.16, hot, 16, falloff=3)
    for i in range(n):
        d = V.rdir(R)
        d.x = abs(d.x) + 0.2
        d.normalize()
        V.streak(tip + d * R.uniform(0.2, 0.5), d, R.uniform(0.05, 0.14), 0.005, rgb, 18)
    V.light(tip, rgb, 25)


def tail(head, n, length, r0, r1, smoke, glow, heat, density=8, seed=0, spread=0.1, rise=0.0):
    """a comet's tail, back along -x: hot and tight at the head, cold and wide at the end"""
    R = rnd(seed)
    for i in range(n):
        t = (i + 1) / n
        p = Vector(head) + Vector((-length * t, R.uniform(-1, 1) * spread * (0.3 + t * 2), R.uniform(-1, 1) * spread * (0.3 + t * 2) + rise * t * t))
        V.puff(p, r0 + (r1 - r0) * t, smoke, density=density * (1 - t * 0.7), glow_rgb=glow, glow=heat * (1 - t) ** 2, seed=seed + i, scale=4)


def embers(at, n, reach, rgb, seed=1, up=0.3, length=(0.04, 0.16), strength=16):
    """sparks: mostly small and dim, a few bright, in their own colour rather than white"""
    R = rnd(seed)
    for i in range(n):
        d = V.rdir(R, up)
        big = R.random() < 0.15
        V.streak(Vector(at) + d * R.uniform(reach * 0.2, reach) * R.random() ** 0.5, d, R.uniform(*length) * (1.8 if big else 1), 0.008 if big else 0.004, rgb, strength * (2.2 if big else 1))


def scene(cx=0.0, zoom=9.2, yaw=-48, pitch=10):
    """third person: behind and to one side of the caster, looking down the bolt's path"""
    V.camera((cx + 0.7, 0.3, 1.5), yaw, pitch, zoom, lens=28)


# ================================================================== black staffs: a family of elements each

FIRE = (V.lin(0x7A1006), V.lin(0xE8501A), V.lin(0xFFB040))
ROT = (V.lin(0x1E3A0A), V.lin(0x6AB020), V.lin(0xC8F060))
VOID = (V.lin(0x1A0640), V.lin(0x6A20D0), V.lin(0xC080FF))
ICE = (V.lin(0x0E3A68), V.lin(0x3A9AE0), V.lin(0xA8E8FF))
STORM = (V.lin(0x102A80), V.lin(0x3A70F0), V.lin(0xA0D0FF))
HOST = (V.lin(0x3A0208), V.lin(0xB01828), V.lin(0xFF7050))


def comet(head, pal, r=0.4, length=2.8, strength=24, seed=1, tongues=9):
    """a bolt of fire: a hot head, and behind it a tail that thins and tears into separate tongues"""
    R = rnd(seed)
    head = Vector(head)
    burn(head, r, pal, strength * 1.5, seed=seed, stretch=(1.3, 1, 1))
    for i in range(tongues):
        k = (i + 1) / tongues
        at = head - Vector((k * length, R.uniform(-1, 1) * 0.16 * k, R.uniform(-1, 1) * 0.16 * k - k * k * 0.15))
        burn(at, r * (1 - k * 0.72) * R.uniform(0.8, 1.15), pal, strength * (1 - k * 0.6), density=20, scale=3, seed=seed + i, stretch=(2.4, 0.8, 0.8))


def blast(at, pal, r=1.1, strength=20, seed=1, tongues=12):
    """a burst: a broken core with tongues thrown out of it, each pointing the way it's going"""
    R = rnd(seed)
    at = Vector(at)
    burn(at, r * 0.8, pal, strength * 1.3, scale=1.8, seed=seed)
    for i in range(tongues):
        d = V.rdir(R, 0.5)
        o = burn(at + d * r * R.uniform(0.65, 1.1), r * R.uniform(0.26, 0.42), pal, strength * 0.7, density=20, scale=2.6, seed=seed + 10 + i, stretch=(1, 1, 2.3))
        o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()


def fx_flame():
    """Brand, Ember, Wyrmfire, Sunfire, Wax, Fury: a torn comet of fire, a fireball where it lands"""
    fire, hot, smoke = V.lin(0xE8602A), V.lin(0xFF9A40), V.lin(0x0E0A08)
    tip = caster(staff=fire)
    t = husk()
    muzzle(tip, fire, hot, 1, pal=FIRE)
    head = Vector((0.5, 0, HEIGHT + 0.1))
    comet(head, FIRE, seed=2)
    tail(head - Vector((1.8, 0, 0)), 7, 1.6, 0.2, 0.5, smoke, fire, 1, density=4, seed=3, rise=0.6)
    embers(head - Vector((1.2, 0, 0)), 30, 1.6, hot, 3, up=0.6)
    V.light(head, fire, 150, 0.5)
    hit = t + Vector((-0.2, 0, 0.1))
    blast(hit, FIRE, 1.25, seed=8, tongues=15)
    R = rnd(5)
    for i in range(7):
        V.puff(hit + Vector((R.uniform(-1, 1), R.uniform(-1, 1), R.uniform(1.3, 2.3))), R.uniform(0.5, 0.8), smoke, density=5, glow_rgb=fire, glow=1, seed=i, scale=3)
    embers(hit, 60, 3.4, hot, 5, up=0.5, length=(0.06, 0.24))
    V.ring(Vector((HIT, 0, 0.03)), 2.0, 0.05, hot, 20, height=0.02, noise=4, seed=2)
    V.light(hit - Vector((0.8, 0.8, 0)), fire, 420, 1.0)
    scene()


def shard(at, d, length, r, mat):
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=r, depth=length, location=Vector(at) + Vector(d).normalized() * length / 2)
    o = bpy.context.active_object
    o.rotation_euler = Vector(d).to_track_quat("Z", "Y").to_euler()
    o.data.materials.append(mat)


def ice_mat(rgb, inner):
    m = V.solid("ice", rgb, 0.08)
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Transmission Weight"].default_value = 0.85
    b.inputs["Emission Color"].default_value = (*inner, 1)
    b.inputs["Emission Strength"].default_value = 1.6
    return m


def fx_shard():
    """Rime, Crystallize, Jade, Vein, Marrow: a lance of crystal in a wake of cold, a thicket of spikes where it lands"""
    ice, pale, deep = V.lin(0x8CD8F8), V.lin(0xE8F8FF), V.lin(0x2A6A98)
    tip = caster(staff=ice)
    t = husk()
    muzzle(tip, ice, pale, 2)
    mat = ice_mat(ice, deep)
    head = Vector((0.5, 0, HEIGHT + 0.1))
    R = rnd(7)
    shard(head - Vector((1.0, 0, 0)), (1, 0, 0), 1.05, 0.14, mat)
    for i in range(6):   # splinters flying with it
        a = i / 6 * math.tau
        shard(head - Vector((1.1 + R.random() * 0.5, -math.cos(a) * 0.24, -math.sin(a) * 0.24)), (1, 0, 0), R.uniform(0.3, 0.5), 0.05, mat)
    comet(head - Vector((1.1, 0, 0)), ICE, r=0.26, length=2.2, strength=12, seed=9, tongues=7)
    embers(head - Vector((1.6, 0, 0)), 22, 1.0, pale, 8, up=0)
    V.light(head - Vector((0.8, 0, 0)), ice, 90, 0.4)
    for i in range(22):   # the thicket
        a, r = R.uniform(0, math.tau), R.uniform(0.15, 1.5)
        at = Vector((HIT + math.cos(a) * r, math.sin(a) * r, 0))
        shard(at, (math.cos(a) * 0.5, math.sin(a) * 0.5, 1), (1.7 - r) * R.uniform(0.7, 1.3) + 0.2, 0.09 + 0.1 * (1.5 - r) / 1.5, mat)
    for i in range(9):
        V.puff(Vector((HIT + R.uniform(-1.3, 1.3), R.uniform(-1.3, 1.3), 0.2)), R.uniform(0.35, 0.6), pale, density=2, squash=0.5, seed=i)
    embers(t, 30, 1.7, pale, 9, length=(0.1, 0.3))
    blast(t + Vector((0, 0, -0.5)), ICE, 0.9, strength=9, seed=6, tongues=7)
    V.ring(Vector((HIT, 0, 0.02)), 1.7, 0.1, ice, 5, height=0.01, noise=5, seed=6)
    V.light(t + Vector((-0.5, -0.8, 0)), ice, 220, 0.8)
    scene()


def fx_lightning():
    """Thunder, Steam, Toll: a held ball of plasma spitting forks, one thrown bolt the whole way to the target"""
    blue, pale = V.lin(0x7FB0FF), V.lin(0xD8ECFF)
    tip = caster(staff=blue)
    t = husk()
    muzzle(tip, blue, pale, 3, n=18)
    head = Vector((0.1, 0, HEIGHT + 0.2))
    burn(head, 0.5, STORM, 34, seed=3, scale=3.4)
    V.bolt(tip, head, blue, jag=0.3, segs=18, width=0.012, seed=2, strength=70)
    V.bolt(tip, head, blue, jag=0.5, segs=16, width=0.01, seed=8, strength=60)
    V.bolt(head, t, blue, jag=0.4, segs=22, width=0.014, seed=3, strength=90)
    R = rnd(4)
    for i in range(9):   # forks off the ball
        d = V.rdir(R)
        V.bolt(head, head + d * R.uniform(0.6, 1.2), blue, jag=0.14, segs=7, width=0.008, seed=20 + i, strength=60)
    for i in range(5):   # down into the ground round the target
        a = R.uniform(0, math.tau)
        V.bolt(t, Vector((HIT + math.cos(a) * 1.5, math.sin(a) * 1.5, 0.02)), blue, jag=0.25, segs=9, width=0.012, seed=40 + i, strength=70)
    V.bolt(t + Vector((0.3, 0.2, 9)), t, blue, jag=0.6, segs=26, width=0.016, seed=5, strength=100)
    blast(t, STORM, 0.8, strength=20, seed=4, tongues=8)
    embers(t, 44, 2.2, pale, 6, length=(0.06, 0.22), strength=30)
    V.ring(Vector((HIT, 0, 0.02)), 1.4, 0.03, blue, 18, noise=10, seed=4)
    V.light(head, blue, 70, 0.4)
    V.light(t + Vector((-0.6, -0.6, 0)), blue, 90, 0.5)
    scene()


def goo(rgb, inner, rough=0.12):
    m = V.solid("goo", rgb, rough)
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Emission Color"].default_value = (*inner, 1)
    b.inputs["Emission Strength"].default_value = 0.12
    b.inputs["Specular IOR Level"].default_value = 0.8
    b.inputs["Coat Weight"].default_value = 1.0
    return m


def blobs(items, mat):
    mb = bpy.data.metaballs.new("goo")
    mb.resolution = 0.05
    mb.render_resolution = 0.018
    mb.threshold = 0.5
    o = bpy.data.objects.new("goo", mb)
    bpy.context.scene.collection.objects.link(o)
    for at, r in items:
        e = mb.elements.new()
        e.co = at
        e.radius = r
    mb.materials.append(mat)


def fx_liquid():
    """Blood, Undertow, Brine, Fever: a heavy flying gout, drawn out and dripping, a crown of splash where it lands"""
    deep, glow, hot = V.lin(0x6A0810), V.lin(0xD01828), V.lin(0xFF6A5A)
    tip = caster(staff=glow)
    t = husk()
    muzzle(tip, glow, hot, 4)
    mat = goo(deep, glow)
    head = Vector((0.2, 0, HEIGHT + 0.15))
    R = rnd(11)
    items = [(head, 0.5)]
    for i in range(24):   # drawn out behind, breaking into beads
        k = i / 24
        items.append((head + Vector((-0.2 - k * 2.5, R.uniform(-1, 1) * 0.05, math.sin(k * 7) * 0.05 - k * k * 0.5)), 0.34 * (1 - k) + 0.05))
    for i in range(16):
        k = R.random()
        items.append((head + Vector((-0.5 - k * 2.2, R.uniform(-0.25, 0.25), R.uniform(-0.25, 0.1) - k * 0.6)), R.uniform(0.04, 0.09)))
    # the splash: a torn crown
    for i in range(30):
        a = i / 30 * math.tau + R.random() * 0.1
        h = R.uniform(0.2, 1.4)
        for j in range(10):
            s = (j + 1) / 10
            r = 0.5 + s * 1.1
            items.append((Vector((HIT + math.cos(a) * r, math.sin(a) * r, 0.1 + math.sin(s * math.pi * 0.8) * h)), 0.24 * (1.1 - s) + 0.04))
    for i in range(30):
        a, r = R.uniform(0, math.tau), R.uniform(0.3, 2.4)
        items.append((Vector((HIT + math.cos(a) * r, math.sin(a) * r, R.uniform(0.2, 2.1))), R.uniform(0.04, 0.1)))
    for i in range(20):
        a, r = R.uniform(0, math.tau), R.uniform(0.2, 1.7)
        items.append((Vector((HIT + math.cos(a) * r, math.sin(a) * r, 0.015)), R.uniform(0.15, 0.3)))
    blobs(items, mat)
    blast(t + Vector((-0.2, 0, -0.1)), HOST, 0.8, strength=14, seed=12, tongues=8)
    V.light(head + Vector((-0.6, -1.2, 1.0)), hot, 140, 0.3)
    V.light(t + Vector((-1.4, -1.4, 1.4)), hot, 200, 0.3)
    V.light(t + Vector((0.8, 1.2, 0.6)), V.lin(0xFFD0C0), 90, 0.3)
    scene()


def fx_rot():
    """Bloom, Venom, Hex, Carrion: a bolt of sick light in a boil of spores, a cloud that keeps opening where it lands"""
    dark, sick, spore = V.lin(0x38501A), V.lin(0x9CE040), V.lin(0xE0F890)
    tip = caster(staff=sick)
    t = husk()
    muzzle(tip, sick, spore, 5)
    head = Vector((0.1, 0, HEIGHT))
    R = rnd(13)
    comet(head, ROT, r=0.42, strength=18, seed=15)
    tail(head - Vector((0.8, 0, 0)), 8, 2.0, 0.3, 0.55, dark, sick, 1, density=4, seed=15, spread=0.16)
    embers(head - Vector((1.2, 0, 0)), 40, 1.5, spore, 7, up=0.8, length=(0.03, 0.08))
    murk = (V.lin(0x16280A), V.lin(0x4A8818), V.lin(0xB0E850))
    for i in range(16):   # the stalk, boiling upward
        k = i / 15
        a, r = R.uniform(0, math.tau), R.uniform(0, 0.35) * (1 - k * 0.3)
        burn(Vector((HIT + math.cos(a) * r, math.sin(a) * r, 0.2 + k * 2.1)), 0.46 - k * 0.1, murk, 9 * (1 - k * 0.5), density=30, scale=2.4, seed=30 + i)
    for i in range(20):   # the head, rolling out and over
        a, r = i / 20 * math.tau, R.uniform(0.7, 1.5)
        burn(Vector((HIT + math.cos(a) * r, math.sin(a) * r, 2.5 + R.uniform(-0.3, 0.4))), R.uniform(0.5, 0.75), murk, 5, density=34, scale=2.2, seed=60 + i)
    for i in range(10):   # what rolls along the ground
        a = i / 10 * math.tau
        V.puff((HIT + math.cos(a) * 1.7, math.sin(a) * 1.7, 0.3), 0.6, dark, density=4, glow_rgb=sick, glow=1, squash=0.6, seed=90 + i)
    embers(t + Vector((0, 0, 0.8)), 70, 3.2, spore, 8, up=0.8, length=(0.02, 0.06))
    V.light(t + Vector((-0.8, -1.0, 1.2)), sick, 90, 1)
    V.light(head, sick, 60, 0.5)
    scene()


def disc(at, r, tilt, pal, strength, seed, n=20):
    """a burning disc round a point, thinning outward, dragged round it"""
    R = rnd(seed)
    for i in range(n):
        a = i / n * math.tau
        rr = r * R.uniform(0.75, 1.3)
        p = Vector((math.cos(a) * rr, math.sin(a) * rr, R.uniform(-0.05, 0.05) * r))
        p.rotate(tilt)
        o = burn(Vector(at) + p, r * 0.3, pal, strength * R.uniform(0.6, 1.2), density=18, scale=3, seed=seed + i, stretch=(2.6, 0.7, 0.4))
        o.rotation_euler = tilt
        o.rotation_euler.rotate_axis("Z", a + 1.57)


def fx_void():
    """Abyss, Eclipse, Strangle, Ambush: a hole in the air with fire dragged round it, and the target going in"""
    from mathutils import Euler
    violet, pale = V.lin(0xA060FF), V.lin(0xE8D0FF)
    tip = caster(staff=violet)
    t = husk()
    muzzle(tip, violet, pale, 6)
    head = Vector((0.2, 0, HEIGHT + 0.1))
    black = V.solid("hole", (0.0, 0.0, 0.0), 1.0)
    tilt = Euler((1.15, 0.25, 0))
    for at, r in ((head, 0.26), (t + Vector((-0.1, 0, 0.4)), 0.85)):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=r, location=at)
        smooth(bpy.context.active_object)
        bpy.context.active_object.data.materials.append(black)
        V.ring(at, r * 1.04, r * 0.03, pale, 40, noise=0, rot=(1.57, 0, 0.9))   # the bright edge of the hole
    disc(head, 0.62, tilt, VOID, 15, 70, n=12)
    comet(head - Vector((0.7, 0, 0)), VOID, r=0.2, length=2.0, strength=12, seed=20, tongues=6)
    hole = t + Vector((-0.1, 0, 0.4))
    disc(hole, 1.7, tilt, VOID, 14, 90, n=24)
    R = rnd(17)
    for i in range(60):   # everything near rushing in
        d = V.rdir(R)
        p = hole + d * R.uniform(1.4, 3.4)
        V.streak(p, -d, R.uniform(0.2, 0.55), 0.006, violet, 22)
    V.light(hole + Vector((-1.4, -1.2, 0.2)), violet, 150, 0.6)
    V.light(head, violet, 50, 0.4)
    scene()


def helix(a, b, radius, turns, phase, n=90, wrap=0.0):
    a, b = Vector(a), Vector(b)
    pts = []
    for i in range(n + 1):
        t = i / n
        p = a.lerp(b, t)
        r = radius * math.sin(math.pi * min(1, t * 1.05)) ** 0.5
        pts.append(p + Vector((0, math.cos(phase + t * turns * math.tau) * r, math.sin(phase + t * turns * math.tau) * r)))
    return pts


def fx_thread():
    """Bind, Jest: threads of bright silk thrown in a spiral, the target wound up in them"""
    pink, pale = V.lin(0xE070C8), V.lin(0xFFE8F8)
    tip = caster(staff=pink)
    t = husk()
    muzzle(tip, pink, pale, 7)
    for i in range(5):
        p = i / 5 * math.tau
        tube(helix(tip, t + Vector((-0.3, 0, 0)), 0.26, 0.9, p), 0.006, pale, 20)
        tube(helix(tip, t + Vector((-0.3, 0, 0)), 0.36, 0.7, p + 0.4), 0.02, pink, 3)
    for i in range(16):   # bound
        z = 0.25 + i * 0.13
        V.ring(Vector((HIT, 0, z)), 0.42 + math.sin(i * 1.4) * 0.05, 0.006, pale, 18, noise=4, seed=i, rot=(0.34 * math.sin(i * 2.3), 0.38 * math.cos(i * 1.7), 0))
    R = rnd(19)
    for i in range(10):   # strands pinning it to the ground
        a = R.uniform(0, math.tau)
        tube([t + Vector((0, 0, R.uniform(-0.6, 0.6))), Vector((HIT + math.cos(a) * 2, math.sin(a) * 2, 0.02))], 0.006, pink, 22)
    burn(t + Vector((0, 0, -0.1)), 0.75, (V.lin(0x400A38), V.lin(0xA02888), V.lin(0xFFA0E0)), 7, density=14, scale=3.2, seed=19, stretch=(0.75, 0.75, 1.3))
    embers(t, 26, 1.8, pale, 10, length=(0.04, 0.14))
    V.light(t + Vector((-0.5, -0.7, 0)), pink, 200, 0.5)
    V.light((0, -0.6, 1.5), pink, 70, 0.5)
    scene()


# ================================================================== white staffs

def allies(c, gold, pale, seed):
    R = rnd(seed)
    for at in c:
        shaft((at[0], at[1], 0), 0.62, 5.5, gold, 3)
        shaft((at[0], at[1], 0), 0.3, 4.5, pale, 5)
        V.ring(Vector((at[0], at[1], 0.03)), 0.62, 0.02, pale, 26, noise=0)
        for i in range(16):
            p = Vector((at[0] + R.uniform(-0.45, 0.45), at[1] + R.uniform(-0.45, 0.45), R.uniform(0.1, 2.6)))
            V.streak(p, (0, 0, 1), R.uniform(0.08, 0.2), 0.007, pale, 40)


def fx_heal():
    """A white staff: the circle opens under the healer, a shaft of light stands on everyone in it"""
    gold, pale = V.lin(0xF2C050), V.lin(0xFFF0C0)
    tip = caster(-1.2, 0.2, staff=gold)
    V.figure((1.8, 1.0), "player", -70)
    V.figure((1.3, -1.5), "player", -40)
    sigil((0, 0, 0), 4.3, gold, pale, 2)
    allies([(-1.2, 0.2), (1.8, 1.0), (1.3, -1.5)], gold, pale, 21)
    ball(tip, 0.3, pale, 26, falloff=2)
    R = rnd(23)
    for i in range(70):   # motes rising through the whole circle
        a, r = R.uniform(0, math.tau), R.uniform(0, 4.2)
        V.streak((math.cos(a) * r, math.sin(a) * r, R.uniform(0.1, 3.0)), (0, 0, 1), R.uniform(0.06, 0.14), 0.006, pale, 30)
    for i in range(10):   # the air lit
        a, r = R.uniform(0, math.tau), R.uniform(0, 3.6)
        V.puff((math.cos(a) * r, math.sin(a) * r, 0.25), 0.7, gold, density=0.8, glow_rgb=gold, glow=1.5, squash=0.4, seed=i)
    V.light((0, -1, 3), gold, 240, 2)
    V.camera((0, 0, 0.9), 12, 22, 11, lens=35)


def fx_radiance():
    """Radiance (the tree): the same light, but monsters in the circle get it as lances from above"""
    gold, pale = V.lin(0xF2C050), V.lin(0xFFF0C0)
    caster(-2.2, 0, staff=gold)
    foes = [(1.2, 0.8), (2.4, -0.8), (0.4, -1.8)]
    sigil((-0.2, 0, 0), 4.3, gold, pale, 3)
    for f in foes:
        c = husk(f[0], f[1], -90)
        shaft((f[0], f[1], 0), 0.1, 10, pale, 22)
        shaft((f[0], f[1], 0), 0.42, 10, gold, 3)
        V.ring(Vector((f[0], f[1], 0.03)), 0.8, 0.03, pale, 28, noise=6, seed=int(f[0] * 7))
        embers(c, 26, 1.3, pale, int(f[1] * 3) + 11, length=(0.1, 0.35))
        for i in range(4):
            V.puff(c + Vector((0, 0, -0.2 + i * 0.3)), 0.3, V.lin(0x402010), density=4, glow_rgb=gold, glow=8, seed=i)
        V.light(c + Vector((-0.4, -0.5, 0)), gold, 130, 0.4)
    V.camera((0, 0, 1.1), 10, 16, 10, lens=35)


# ================================================================== summoners

def rising(x, y, sink, rgb, hot, seed, yaw=0, pal=SOUL):
    """a thrall coming up out of the circle, a column of its dungeon's smoke round it"""
    before = set(bpy.context.scene.objects)
    V.figure((x, y), "mob", yaw)
    for o in set(bpy.context.scene.objects) - before:
        o.location.z -= sink
    R = rnd(seed)
    for i in range(10):
        a = R.uniform(0, math.tau)
        burn((x + math.cos(a) * 0.5, y + math.sin(a) * 0.5, 0.2 + i * 0.36), 0.42 - i * 0.022, pal, 18 * (1 - i / 12), density=18, scale=2.8, seed=seed + i, stretch=(0.8, 0.8, 1.9))
    for i in range(22):
        a, r = R.uniform(0, math.tau), R.uniform(0.2, 0.75)
        V.streak((x + math.cos(a) * r, y + math.sin(a) * r, R.uniform(0.1, 3.2)), (0, 0, 1), R.uniform(0.15, 0.4), 0.009, hot, 40)
    V.ring(Vector((x, y, 0.03)), 0.85, 0.03, hot, 30, noise=4, seed=seed)
    V.light((x, y - 0.7, 0.8), rgb, 90, 0.5)


def fx_summon():
    """A summoner's staff: the circle tears open, the dungeon's own dwellers climb out through a column of soul fire"""
    red, hot = V.lin(0x9A28C8), V.lin(0xE8A0FF)
    caster(-2.8, 0, staff=red)
    sigil((0.5, 0, 0), 3.6, red, hot, 4)
    rising(1.0, 1.2, 0.75, red, hot, 40, -60)
    rising(1.3, -1.2, 0.3, red, hot, 60, -110)
    V.camera((0, 0, 1.1), 14, 15, 9.5, lens=35)


# ================================================================== the Joined staffs' R skills

def fx_accord_bolts():
    """Three bolts at once, each twice a staff's: three comets braided round each other, a far bigger blast"""
    fire, hot, smoke = V.lin(0xFF7A20), V.lin(0xFFE0A0), V.lin(0x1A1210)
    tip = caster(staff=fire)
    t = husk()
    muzzle(tip, fire, hot, 8, n=24)
    for i in range(3):
        p = i / 3 * math.tau
        line = helix(tip, Vector((0.9, 0, HEIGHT + 0.2)), 0.42, 1.2, p, n=70)
        head = Vector(line[-1])
        tube(line, 0.05, fire, 14)
        tube(line, 0.018, hot, 40, soft=False)
        burn(head, 0.36, FIRE, 36, seed=i)
        for k in range(0, 68, 6):
            burn(line[k], 0.1 + k * 0.0028, FIRE, 12 + k * 0.18, density=18, scale=3, seed=k + i)
    R = rnd(31)
    c = t + Vector((0, 0, 0.3))
    blast(c, FIRE, 2.0, strength=22, seed=32, tongues=18)
    embers(c, 90, 4.2, hot, 12, length=(0.1, 0.4))
    V.ring(Vector((HIT, 0, 0.02)), 2.2, 0.06, hot, 26, height=0.04, noise=4, seed=2)
    V.ring(Vector((HIT, 0, 0.02)), 3.1, 0.03, fire, 18, height=0.03, noise=6, seed=3)
    V.light(c + Vector((-1, -1, 0)), fire, 500, 1)
    scene(cx=0.4)


def fx_accord_heal():
    """Everyone back up by a third, and a guard: the great circle, and a dome of gold over all of them"""
    gold, pale = V.lin(0xFFC840), V.lin(0xFFF4D0)
    caster(-1.2, 0.2, staff=gold)
    V.figure((1.8, 1.0), "player", -70)
    V.figure((1.3, -1.5), "player", -40)
    sigil((0, 0, 0), 4.8, gold, pale, 5, strength=34)
    allies([(-1.2, 0.2), (1.8, 1.0), (1.3, -1.5)], gold, pale, 33)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=4.8, location=(0, 0, 0))
    d = bpy.context.active_object
    smooth(d)
    d.visible_shadow = False
    d.data.materials.append(beam_mat(gold, 5, rim=True))
    R = rnd(35)
    for i in range(16):   # ribs of the guard
        a = i / 16 * math.tau
        pts = [(math.cos(a) * math.cos(k / 20 * 1.57) * 4.8, math.sin(a) * math.cos(k / 20 * 1.57) * 4.8, math.sin(k / 20 * 1.57) * 4.8) for k in range(21)]
        tube(pts, 0.005, pale, 10)
    for i in range(50):
        d2 = V.rdir(R)
        d2.z = abs(d2.z)
        V.streak(d2 * R.uniform(1.5, 4.7), (0, 0, 1), 0.12, 0.007, pale, 34)
    V.light((0, -1, 4), gold, 400, 3)
    V.camera((0, 0, 1.6), 12, 18, 14.5, lens=35)


def fx_accord_summon():
    """Twice the usual host: the circle opens wide and they come up in a line"""
    red, hot = V.lin(0xC02040), V.lin(0xFFA080)
    caster(-3.8, 0, staff=red)
    sigil((1.0, 0, 0), 4.9, red, hot, 6, strength=32)
    for i, (x, y, sink) in enumerate(((-1, 1.8, 0.2), (0.6, 2.7, 0.5), (2.6, 2.2, 0.15), (3.5, 0, 0.6), (2.5, -2.2, 0.1), (0.5, -2.6, 0.4))):
        rising(x, y, sink, red, hot, 70 + i * 13, -90, HOST)
    V.camera((0.4, 0, 1.2), 16, 20, 12.5, lens=35)


def fx_overload():
    """Overload (the tree): the sixth bolt goes off over everything near what it hit"""
    fire, hot, smoke = V.lin(0xFF7A20), V.lin(0xFFE8C0), V.lin(0x181210)
    tip = caster(-5.2, staff=fire)
    husk(0.4)
    husk(1.7, 1.4, -110)
    husk(1.4, -1.5, -60)
    R = rnd(41)
    c = Vector((1.1, 0, 1.0))
    blast(c, FIRE, 2.2, strength=22, seed=42, tongues=20)
    for i in range(10):
        V.puff(c + Vector((R.uniform(-2, 2), R.uniform(-2, 2), R.uniform(2.2, 3.6))), R.uniform(0.7, 1.1), smoke, density=5, glow_rgb=fire, glow=1, seed=i, scale=2.5)
    for i in range(36):   # the ground blast
        a = i / 36 * math.tau
        V.puff((1.1 + math.cos(a) * 4, math.sin(a) * 4, 0.35), 0.62, V.lin(0x4A3E32), density=3, squash=0.7, seed=100 + i)
    V.ring(Vector((1.1, 0, 0.03)), 3.6, 0.08, hot, 30, height=0.05, noise=4, seed=2)
    embers(c, 120, 4.4, hot, 13, length=(0.25, 0.9))
    V.light(c + Vector((-1.6, -2, 0)), fire, 900, 1.5)
    muzzle(tip, fire, hot, 9)
    V.camera((-0.4, 0, 1.5), 10, 9, 10.5, lens=35)


EFFECTS = {"flame": fx_flame, "shard": fx_shard, "lightning": fx_lightning, "liquid": fx_liquid, "rot": fx_rot, "void": fx_void, "thread": fx_thread,
           "overload": fx_overload, "heal": fx_heal, "radiance": fx_radiance, "summon": fx_summon, "accord_bolts": fx_accord_bolts,
           "accord_heal": fx_accord_heal, "accord_summon": fx_accord_summon}

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    os.makedirs(argv[0], exist_ok=True)
    for name, fn in EFFECTS.items():
        if argv[1:] and name not in argv[1:]:
            continue
        sc = V.reset()
        sc.render.resolution_x, sc.render.resolution_y, sc.cycles.samples = W, H, SAMPLES
        fn()
        sc.render.filepath = os.path.join(argv[0], name + ".png")
        bpy.ops.render.render(write_still=True)
        print("rendered", name, flush=True)
