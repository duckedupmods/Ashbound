"""Second round of the black school's magic, in Cycles. Nothing round or wet: the first liquid looked like mucus because it
was fat, glossy and blobby, so nothing here has a shine or a drop in it.

    hex    the apprentice's staff: black fire, a dark mass burning only along its torn edge
    tide   the liquid dungeons, drawn in the worst colour they have: a wave round the bolt, one torn skin thrown up, mist

    blender -b -P tools/blender/vfx_black.py -- OUT_DIR [names...]      -> OUT_DIR/<name>.png (OUT_DIR must be a full path)
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import vfx_concepts as V
import vfx_mage as M

HEX = (V.lin(0x3A0408), V.lin(0xB80C14), V.lin(0xF03A18))


def black_fire(at, r, pal=HEX, strength=7, density=170, scale=2.6, seed=0, stretch=(1, 1, 1)):
    """dark energy the way it reads: solid ink in front, and behind it the same torn shape a little bigger in one colour,
    so all that shows of the colour is a rim. Two copies of one flame, which the game can do with its own fire flipbook"""
    halo = M.burn(at, r * 1.22, pal, strength, 5, scale, seed, stretch)
    ink = M.burn(at, r, pal, 0, density, scale, seed, stretch)
    return halo, ink


def tongue(at, d, length, r, seed, **k):
    both = black_fire(Vector(at) + Vector(d).normalized() * length * 0.5, r, seed=seed, stretch=(1, 1, length / r * 0.62), **k)
    for o in both:
        o.rotation_euler = Vector(d).to_track_quat("Z", "Y").to_euler()


def arc(at, r, start, span, wide, tilt, mat, n=48):
    """a thin curved cut of light, both ends needles"""
    rows = [[], []]
    for i in range(n):
        t = i / (n - 1)
        a = start + t * span
        w = wide * math.sin(t * math.pi) ** 1.3
        for row, rr in zip(rows, (r - w, r + w)):
            p = Vector((math.cos(a) * rr, math.sin(a) * rr, 0))
            p.rotate(tilt)
            row.append(Vector(at) + p)
    return grid(rows, mat)


def sheet_mat(rgb, pale, strength, streak=26.0):
    """a skin of liquid with no surface shine: faint where it comes from, torn along its length, brightest at its lip"""
    m = bpy.data.materials.new("sheet")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    xyz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["UV"], xyz.inputs[0])
    sc = nt.nodes.new("ShaderNodeCombineXYZ")
    mu = nt.nodes.new("ShaderNodeMath")
    mu.operation = "MULTIPLY"
    mu.inputs[1].default_value = streak
    nt.links.new(xyz.outputs["X"], mu.inputs[0])
    nt.links.new(mu.outputs[0], sc.inputs["X"])
    nt.links.new(xyz.outputs["Y"], sc.inputs["Y"])
    no = nt.nodes.new("ShaderNodeTexNoise")
    no.inputs["Scale"].default_value = 1.0
    no.inputs["Detail"].default_value = 6
    no.inputs["Roughness"].default_value = 0.65
    nt.links.new(sc.outputs[0], no.inputs["Vector"])
    tear = nt.nodes.new("ShaderNodeMapRange")
    tear.inputs[1].default_value = 0.42
    tear.inputs[2].default_value = 0.56
    nt.links.new(no.outputs[0], tear.inputs[0])
    rise = nt.nodes.new("ShaderNodeMapRange")
    rise.inputs[1].default_value = 0.1
    rise.inputs[2].default_value = 0.75
    nt.links.new(xyz.outputs["Y"], rise.inputs[0])
    lip = nt.nodes.new("ShaderNodeMapRange")
    lip.inputs[1].default_value = 0.84
    lip.inputs[2].default_value = 0.97
    nt.links.new(xyz.outputs["Y"], lip.inputs[0])
    fac = nt.nodes.new("ShaderNodeMath")
    fac.operation = "MULTIPLY"
    nt.links.new(tear.outputs[0], fac.inputs[0])
    nt.links.new(rise.outputs[0], fac.inputs[1])
    fac2 = nt.nodes.new("ShaderNodeMath")
    fac2.operation = "MAXIMUM"
    fac2.use_clamp = True
    nt.links.new(fac.outputs[0], fac2.inputs[0])
    nt.links.new(lip.outputs[0], fac2.inputs[1])
    col = nt.nodes.new("ShaderNodeMix")
    col.data_type = "RGBA"
    col.inputs["A"].default_value = (*rgb, 1)
    col.inputs["B"].default_value = (*pale, 1)
    nt.links.new(lip.outputs[0], col.inputs["Factor"])
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(col.outputs["Result"], em.inputs[0])
    em.inputs[1].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(fac2.outputs[0], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def grid(rows, mat):
    """a sheet through rows of points; u runs along a row, v from the first row to the last"""
    nv, nu = len(rows), len(rows[0])
    me = bpy.data.meshes.new("sheet")
    vs = [tuple(p) for row in rows for p in row]
    fs = [(j * nu + i, j * nu + i + 1, (j + 1) * nu + i + 1, (j + 1) * nu + i) for j in range(nv - 1) for i in range(nu - 1)]
    me.from_pydata(vs, [], fs)
    uv = me.uv_layers.new(name="UV")
    for lo in me.loops:
        k = lo.vertex_index
        uv.uv[lo.index].vector = ((k % nu) / (nu - 1), (k // nu) / (nv - 1))
    for po in me.polygons:
        po.use_smooth = True
    o = bpy.data.objects.new("sheet", me)
    bpy.context.scene.collection.objects.link(o)
    o.visible_shadow = False
    o.data.materials.append(mat)
    return o


def crown(at, r0, r1, high, mat, seed, nu=240, nv=18):
    """one thrown skin of liquid: a wall opening like a flower with a torn, peaked lip, not a bunch of separate blades"""
    R = M.rnd(seed)
    peaks = [(R.randint(5, 13), R.uniform(0, math.tau), R.uniform(0.3, 1.0)) for _ in range(7)]
    rows = []
    for j in range(nv):
        t = j / (nv - 1)
        row = []
        for i in range(nu):
            a = i / (nu - 1) * math.tau
            h = 0.5 + sum(w * max(0, math.sin(a * n + ph)) ** 5 for n, ph, w in peaks) * 0.5
            rr = r0 + (r1 - r0) * t ** 1.7
            row.append(Vector(at) + Vector((math.cos(a) * rr, math.sin(a) * rr, high * h * (t - 0.28 * t * t))))
        rows.append(row)
    return grid(rows, mat)


def curl(head, length, r0, r1, turns, phase, wide, mat, nu=120, nv=8):
    """a wave wrapped round the bolt's path, thin at the head, opening as it trails"""
    rows = []
    for j in range(nv):
        v = j / (nv - 1)
        row = []
        for i in range(nu):
            t = i / (nu - 1)
            a = phase + t * turns * math.tau
            r = r0 + (r1 - r0) * t ** 0.8
            row.append(Vector(head) + Vector((-length * t - v * wide * (1 - t) * 0.5, math.cos(a) * r * (1 + v * wide * 1.6), math.sin(a) * r * (1 + v * wide * 1.6))))
        rows.append(row)
    return grid(rows, mat)


def fx_hex():
    """black fire: ink with a red rim, a black tail, a pillar of it where it lands, and white only as thin cuts"""
    from mathutils import Euler
    rim = V.lin(0xD8140C)
    white = V.glow_mat(V.lin(0xFFF0E8), 9, soft=False)
    tip = M.caster(staff=rim)
    t = M.husk()
    black_fire(tip, 0.26, seed=1)
    head = Vector((0.2, 0, M.HEIGHT + 0.1))
    black_fire(head, 0.46, seed=2, stretch=(1.35, 1, 1))
    R = M.rnd(3)
    for i in range(9):
        k = (i + 1) / 9
        at = head - Vector((k * 3.1, R.uniform(-1, 1) * 0.2 * k, R.uniform(-1, 1) * 0.2 * k - k * k * 0.1))
        black_fire(at, 0.42 * (1 - k * 0.7) * R.uniform(0.85, 1.15), seed=4 + i, stretch=(2.5, 0.8, 0.8))
    M.embers(head - Vector((1.4, 0, 0)), 16, 1.5, rim, 3, up=0.1, length=(0.05, 0.16), strength=9)
    V.light(head, rim, 7, 0.5)
    hit = Vector((M.HIT - 0.2, 0, 0.05))
    black_fire(hit + Vector((0, 0, 1.15)), 0.9, seed=8, stretch=(1, 1, 1.5))
    R = M.rnd(9)
    for i in range(13):
        a = i / 13 * math.tau + R.uniform(-0.2, 0.2)
        lean = R.uniform(0.25, 0.8)
        d = Vector((math.cos(a) * lean, math.sin(a) * lean, 1))
        tongue(hit + Vector((math.cos(a) * 0.45, math.sin(a) * 0.45, 0.5)), d, R.uniform(1.9, 3.2), R.uniform(0.3, 0.44), 20 + i)
    for i in range(5):   # the cuts round the blast: the only white in it
        arc(hit + Vector((0, 0, R.uniform(0.9, 2.3))), R.uniform(1.3, 2.3), R.uniform(0, math.tau), R.uniform(1.8, 3.0), 0.05, Euler((R.uniform(-0.6, 0.6), R.uniform(-0.6, 0.6), 0)), white)
    V.ring(Vector((M.HIT, 0, 0.04)), 2.5, 0.012, V.lin(0xFFF0E8), 10, height=0.01, noise=0)
    M.sigil(Vector((M.HIT, 0, 0.03)), 2.2, V.lin(0x60080C), rim, seed=4, strength=2.5)
    M.embers(hit + Vector((0, 0, 1.2)), 34, 3.1, rim, 5, up=0.8, length=(0.05, 0.18), strength=9)
    V.light(hit + Vector((-1.2, -1.2, 1.2)), rim, 12, 0.9)
    M.scene()


def fx_tide():
    """the liquid family in cellar green, its worst colour: a wave wrapped round the bolt, one torn skin thrown up, mist"""
    c, pale = V.lin(0x7E9A2C), V.lin(0xF0FAC8)
    tip = M.caster(staff=c)
    t = M.husk()
    M.muzzle(tip, c, pale, 2, n=12)
    mat = sheet_mat(c, pale, 11)
    head = Vector((0.5, 0, M.HEIGHT + 0.05))
    for ph in (0.0, 2.1, 4.2):
        curl(head, 3.3, 0.05, 0.42, 1.1, ph, 0.5, mat)
    M.ball(head, 0.09, pale, 18, falloff=3)
    R = M.rnd(3)
    for i in range(30):
        p = head + Vector((R.uniform(-3.2, 0), R.uniform(-1, 1) * 0.5, R.uniform(-1, 1) * 0.5))
        V.streak(p, Vector((1, 0, 0)), R.uniform(0.08, 0.3), 0.003, pale, 10)
    for i in range(6):
        V.puff(head + Vector((-1.0 - i * 0.45, 0, 0)), 0.3 + i * 0.1, c, density=0.5, glow_rgb=c, glow=0.3, seed=i, scale=5)
    V.light(head, c, 30, 0.5)
    hit = Vector((M.HIT - 0.1, 0, 0.04))
    crown(hit, 0.5, 2.3, 3.0, sheet_mat(c, pale, 10), 7)
    crown(hit, 0.3, 1.5, 3.8, sheet_mat(c, pale, 7, streak=40), 11)
    V.ring(Vector((M.HIT, 0, 0.04)), 2.7, 0.04, pale, 12, height=0.02, noise=5, seed=2)
    R = M.rnd(7)
    for i in range(10):
        a = i / 10 * math.tau
        V.puff(hit + Vector((math.cos(a) * 1.8, math.sin(a) * 1.8, R.uniform(0.2, 1.0))), R.uniform(0.5, 0.9), c, density=0.45, glow_rgb=c, glow=0.3, seed=i, scale=5)
    for i in range(40):
        d = V.rdir(R, 0.9)
        V.streak(hit + Vector((0, 0, 1.2)) + d * R.uniform(1.2, 3.2), d, R.uniform(0.1, 0.34), 0.003, pale, 10)
    V.light(hit + Vector((-1.0, -1.0, 1.0)), c, 60, 0.8)
    M.scene()


EFFECTS = {"hex": fx_hex, "tide": fx_tide}

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    os.makedirs(argv[0], exist_ok=True)
    for name, fn in EFFECTS.items():
        if argv[1:] and name not in argv[1:]:
            continue
        sc = V.reset()
        sc.render.resolution_x, sc.render.resolution_y, sc.cycles.samples = M.W, M.H, M.SAMPLES
        fn()
        sc.render.filepath = os.path.join(argv[0], name + ".png")
        bpy.ops.render.render(write_still=True)
        print("rendered", name, flush=True)
