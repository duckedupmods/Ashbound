"""The Silk Archive concept (Cycles): the Great Index as a spider's nest. A rotunda of shelves choked with silk, an orb
web strung across the dome, cocoons hanging on threads, egg sacs heaped on the floor, funnel webs tunnelling into
the stacks, moonlight falling through the oculus into fog, and the spider waiting at the hub.
  blender -b -P tools/blender/silk_nest.py -- <shot> [fast]   ->  tools/renders/dungeon/silk_<shot>.png
shots: hero (from the door), up (under the web), funnel (a funnel web in the stacks)"""
import os, sys, math, random
import bpy, bmesh
from mathutils import Vector, Matrix

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SHOT = ARGS[0] if ARGS else "hero"
FAST = "fast" in ARGS
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "renders", "dungeon")
rnd = random.Random(7)

R = 14.0          # the rotunda's inner radius
SHELF_TOP = 12.0  # shelves up to here, index drawers above
DOME = 18.0       # the dome springs here
BAYS = 32

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
cp = bpy.context.preferences.addons["cycles"].preferences
cp.compute_device_type = "OPTIX"
cp.get_devices()
for d in cp.devices:
    d.use = d.type == "OPTIX"
sc.cycles.device = "GPU"
sc.cycles.samples = 48 if FAST else 200
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 6
sc.cycles.volume_bounces = 1
sc.cycles.volume_step_rate = 1.0 if FAST else 0.5
sc.render.resolution_x, sc.render.resolution_y = (1280, 720) if FAST else (1920, 1080)
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast" if "AgX - Medium High Contrast" in [
    i.identifier for i in bpy.types.ColorManagedViewSettings.bl_rna.properties["look"].enum_items] else "None"
world = bpy.data.worlds.new("w")
sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.004, 0.006, 0.012, 1)


# ---------------------------------------------------------------- materials
def mat(name, color, rough=0.6, **kw):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    for k, v in kw.items():
        b.inputs[k].default_value = v
    return m, b


def links(m):
    return m.node_tree.links


def node(m, t):
    return m.node_tree.nodes.new(t)


WALNUT, _ = mat("walnut", (0.045, 0.024, 0.013), 0.5, **{"Coat Weight": 0.25})
LEATHER = [mat("leather%d" % i, c, 0.55)[0] for i, c in enumerate(
    [(0.12, 0.018, 0.015), (0.02, 0.06, 0.03), (0.08, 0.045, 0.02), (0.018, 0.025, 0.07), (0.16, 0.12, 0.07)])]
GILT, _ = mat("gilt", (0.6, 0.42, 0.16), 0.35, **{"Metallic": 1.0})


def math_n(m, op, a, b=None, va=None, vb=None):
    n = node(m, "ShaderNodeMath")
    n.operation = op
    if a is not None:
        links(m).new(a, n.inputs[0])
    else:
        n.inputs[0].default_value = va
    if b is not None:
        links(m).new(b, n.inputs[1])
    elif vb is not None:
        n.inputs[1].default_value = vb
    return n.outputs[0]


def silk_mat(name, holes=0.0, glow=0.0, translucent=0.45, gauze=0.0, inner=False):
    m, b = mat(name, (0.78, 0.8, 0.79), 0.42, **{"Sheen Weight": 0.8, "Sheen Roughness": 0.3, "Subsurface Weight": 0.25,
                                                  "Subsurface Radius": Vector((0.2, 0.2, 0.18))})
    b.inputs["Sheen Tint"].default_value = (0.85, 0.9, 1.0, 1)
    tr = node(m, "ShaderNodeBsdfTranslucent")
    tr.inputs[0].default_value = (0.82, 0.85, 0.82, 1)
    mix = node(m, "ShaderNodeMixShader")
    mix.inputs[0].default_value = translucent
    out = next(n for n in m.node_tree.nodes if n.type == "OUTPUT_MATERIAL")
    links(m).new(b.outputs[0], mix.inputs[1])
    links(m).new(tr.outputs[0], mix.inputs[2])
    sh = mix.outputs[0]
    if inner:                                       # the inside of a funnel: dark, only a glint of silk
        geo = node(m, "ShaderNodeNewGeometry")
        dk, _d = mat(name + "_in", (0.01, 0.01, 0.012), 0.6)
        dkb = node(m, "ShaderNodeBsdfDiffuse")
        dkb.inputs[0].default_value = (0.02, 0.02, 0.024, 1)
        mi = node(m, "ShaderNodeMixShader")
        links(m).new(geo.outputs["Backfacing"], mi.inputs[0])
        links(m).new(sh, mi.inputs[1])
        links(m).new(dkb.outputs[0], mi.inputs[2])
        sh = mi.outputs[0]
    # streaks: long strands of silk in the sheet, as a stretched noise bump
    tc = node(m, "ShaderNodeTexCoord")
    mp = node(m, "ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 22.0, 1.0)
    nz = node(m, "ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    nz.inputs["Detail"].default_value = 6.0
    bump = node(m, "ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    links(m).new(tc.outputs["Object"], mp.inputs[0])
    links(m).new(mp.outputs[0], nz.inputs[0])
    links(m).new(nz.outputs[0], bump.inputs["Height"])
    links(m).new(bump.outputs[0], b.inputs["Normal"])
    if glow:
        b.inputs["Emission Color"].default_value = (0.7, 0.85, 1.0, 1)
        b.inputs["Emission Strength"].default_value = glow
    if holes:
        hn = node(m, "ShaderNodeTexNoise")
        hn.inputs["Scale"].default_value = 0.9
        hn.inputs["Detail"].default_value = 3.0
        hn.inputs["Roughness"].default_value = 0.45
        hm = node(m, "ShaderNodeMapping")
        hm.inputs["Scale"].default_value = (1.0, 1.0, 0.3)
        cr = node(m, "ShaderNodeValToRGB")
        cr.color_ramp.elements[0].position = holes
        cr.color_ramp.elements[1].position = holes + 0.08
        links(m).new(tc.outputs["Object"], hm.inputs[0])
        links(m).new(hm.outputs[0], hn.inputs[0])
        links(m).new(hn.outputs[0], cr.inputs[0])
        tp = node(m, "ShaderNodeBsdfTransparent")
        mix2 = node(m, "ShaderNodeMixShader")
        fac = cr.outputs[0]
        if gauze:
            uv = node(m, "ShaderNodeTexCoord").outputs["UV"]
            sep = node(m, "ShaderNodeSeparateXYZ")
            links(m).new(uv, sep.inputs[0])
            u, v = sep.outputs[0], sep.outputs[1]
            e = math_n(m, "MINIMUM", math_n(m, "MINIMUM", u, v), math_n(m, "MINIMUM", math_n(m, "SUBTRACT", None, u, va=1.0),
                                                                     math_n(m, "SUBTRACT", None, v, va=1.0)))
            en = node(m, "ShaderNodeTexNoise")
            en.inputs["Scale"].default_value = 2.5
            en.inputs["Detail"].default_value = 6.0
            links(m).new(tc.outputs["Object"], en.inputs[0])
            e = math_n(m, "ADD", e, math_n(m, "MULTIPLY", en.outputs[0], None, vb=0.35))
            er = node(m, "ShaderNodeMapRange")
            er.inputs[1].default_value = 0.2
            er.inputs[2].default_value = 0.42
            links(m).new(e, er.inputs[0])
            fac = math_n(m, "MULTIPLY", math_n(m, "MULTIPLY", fac, er.outputs[0]), None, vb=gauze)
        links(m).new(fac, mix2.inputs[0])
        links(m).new(tp.outputs[0], mix2.inputs[1])
        links(m).new(sh, mix2.inputs[2])
        sh = mix2.outputs[0]
    links(m).new(sh, out.inputs[0])
    return m


SHEET = silk_mat("silk_sheet", holes=0.3, translucent=0.7, gauze=0.95)
GAUZE = silk_mat("gauze", holes=0.25, translucent=0.8, gauze=0.4)
WRAP = silk_mat("silk_wrap", translucent=0.2)
THREAD, _tb = mat("thread", (0.85, 0.88, 0.9), 0.3, **{"Emission Strength": 0.12})
LOOSE, _ = mat("loose", (0.7, 0.72, 0.74), 0.4, **{"Sheen Weight": 1.0})
_tb.inputs["Emission Color"].default_value = (0.75, 0.85, 1.0, 1)

# cocoons: tight spiral bands as a bump
for n_ in ("ShaderNodeTexWave",):
    _w = node(WRAP, n_)
    _w.wave_type = "BANDS"
    _w.bands_direction = "Z"
    _w.inputs["Scale"].default_value = 6.0
    _w.inputs["Distortion"].default_value = 4.0
    _w.inputs["Detail"].default_value = 3.0
    _wb = node(WRAP, "ShaderNodeBump")
    _wb.inputs["Strength"].default_value = 0.6
    _bs = next(n for n in WRAP.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    links(WRAP).new(_w.outputs[1], _wb.inputs["Height"])
    links(WRAP).new(_wb.outputs[0], _bs.inputs["Normal"])

EGG, _eb = mat("egg", (0.6, 0.62, 0.55), 0.25, **{"Subsurface Weight": 1.0, "Subsurface Scale": 0.5,
                                                  "Transmission Weight": 0.4, "Emission Strength": 0.6, "Coat Weight": 0.6})
_eb.inputs["Emission Color"].default_value = (0.35, 0.55, 0.65, 1)
CHITIN, _cb = mat("chitin", (0.012, 0.011, 0.012), 0.32, **{"Coat Weight": 0.8, "Coat Roughness": 0.15})
EYE, _ = mat("eye", (0.0, 0.0, 0.0), 0.02, **{"Coat Weight": 1.0})
INK, _ = mat("ink", (0.002, 0.002, 0.004), 0.04, **{"Coat Weight": 1.0})
PAGE, _ = mat("page", (0.55, 0.48, 0.34), 0.8)
LAMPGLASS, _lb = mat("lampglass", (0.6, 0.8, 1.0), 0.1, **{"Emission Strength": 25.0})
_lb.inputs["Emission Color"].default_value = (0.55, 0.75, 1.0, 1)
PEWTER, _ = mat("pewter", (0.18, 0.19, 0.2), 0.4, **{"Metallic": 1.0})


def floor_mat():
    m, b = mat("marble", (0.5, 0.5, 0.5), 0.18, **{"Coat Weight": 0.3})
    tc = node(m, "ShaderNodeTexCoord")
    ck = node(m, "ShaderNodeTexChecker")
    ck.inputs["Scale"].default_value = 1.0
    ck.inputs["Color1"].default_value = (0.012, 0.022, 0.02, 1)
    ck.inputs["Color2"].default_value = (0.55, 0.54, 0.48, 1)
    mp = node(m, "ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.5, 0.5, 0.5)
    nz = node(m, "ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 0.8
    nz.inputs["Detail"].default_value = 10
    dust = node(m, "ShaderNodeMix")
    dust.data_type = "RGBA"
    dust.inputs["B"].default_value = (0.25, 0.25, 0.24, 1)
    links(m).new(tc.outputs["Object"], mp.inputs[0])
    links(m).new(mp.outputs[0], ck.inputs[0])
    links(m).new(nz.outputs[0], dust.inputs[0])
    links(m).new(ck.outputs[0], dust.inputs["A"])
    links(m).new(dust.outputs[2], b.inputs["Base Color"])
    return m


def drawer_mat():
    """the index drawers: walnut fronts in a brick grid, a pale label on each"""
    m, b = mat("drawers", (0.05, 0.03, 0.016), 0.5)
    tc = node(m, "ShaderNodeTexCoord")
    br = node(m, "ShaderNodeTexBrick")
    br.offset = 0.0
    br.inputs["Scale"].default_value = 3.0
    br.inputs["Mortar Size"].default_value = 0.03
    br.inputs["Brick Width"].default_value = 0.6
    br.inputs["Row Height"].default_value = 0.3
    br.inputs["Color1"].default_value = (0.055, 0.032, 0.017, 1)
    br.inputs["Color2"].default_value = (0.04, 0.022, 0.012, 1)
    br.inputs["Mortar"].default_value = (0.003, 0.002, 0.001, 1)
    links(m).new(tc.outputs["Object"], br.inputs[0])
    links(m).new(br.outputs[0], b.inputs["Base Color"])
    bump = node(m, "ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.6
    links(m).new(br.outputs["Fac"], bump.inputs["Height"])
    links(m).new(bump.outputs[0], b.inputs["Normal"])
    return m


# ---------------------------------------------------------------- geometry helpers
def obj(name, bm, mats, smooth=False):
    me = bpy.data.meshes.new(name)
    if smooth:
        for f in bm.faces:
            f.smooth = True
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    return o


def box(bm, c, size, yaw=0.0, mi=0):
    rot = Matrix.Rotation(yaw, 3, "Z")
    sx, sy, sz = size[0] / 2, size[1] / 2, size[2] / 2
    vs = [bm.verts.new(Vector(c) + rot @ Vector((x, y, z))) for x in (-sx, sx) for y in (-sy, sy) for z in (-sz, sz)]
    for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        bm.faces.new([vs[i] for i in f]).material_index = mi


def displace(bm, amt, scale=1.6, seed=0):
    """a little lumpy noise on every vertex, along its normal (so wraps and sacs aren't perfect balls)"""
    from mathutils import noise
    bm.normal_update()
    off = Vector((seed * 13.1, seed * 7.7, seed * 3.3))
    for v in bm.verts:
        v.co += v.normal * noise.noise(v.co * scale + off) * amt


def ellipsoid(bm, c, r, mi=0, rot=None, seg=16):
    m = Matrix.Diagonal((*r, 1.0))
    if rot:
        m = rot.to_4x4() @ m
    ret = bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2 + 2, radius=1.0, matrix=Matrix.Translation(c) @ m)
    for f in {f for v in ret["verts"] for f in v.link_faces}:
        f.material_index = mi


def limb(bm, a, b, ra, rb, mi=0, seg=8):
    """a tapered tube from a to b, capped"""
    a, b = Vector(a), Vector(b)
    d = (b - a)
    q = d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    ret = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=ra, radius2=rb, depth=d.length,
                                matrix=Matrix.Translation((a + b) / 2) @ q)
    for f in {f for v in ret["verts"] for f in v.link_faces}:
        f.material_index = mi


def thread(name, pts, r=0.012, m=THREAD):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 1
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts):
        p.co = (*q, 1)
    cu.materials.append(m)
    o = bpy.data.objects.new(name, cu)
    sc.collection.objects.link(o)
    return o


def threads(name, lines, r=0.012, m=THREAD):
    """many polylines in one curve object"""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 0
    for pts in lines:
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for p, q in zip(sp.points, pts):
            p.co = (*q, 1)
    cu.materials.append(m)
    o = bpy.data.objects.new(name, cu)
    sc.collection.objects.link(o)
    return o


def sag(a, b, droop, n=14, wob=0.0):
    a, b = Vector(a), Vector(b)
    out = []
    for i in range(n + 1):
        t = i / n
        p = a.lerp(b, t)
        p.z -= droop * 4 * t * (1 - t)
        if wob and 0 < i < n:
            p += Vector((rnd.uniform(-wob, wob), rnd.uniform(-wob, wob), rnd.uniform(-wob, wob)))
        out.append(tuple(p))
    return out


def sheet(name, p00, p10, p01, p11, droop=0.5, n=28, noise=0.15, m=SHEET):
    """a sheet of silk strung between four corners, sagging in the middle, rippled"""
    bm = bmesh.new()
    P = [Vector(p) for p in (p00, p10, p01, p11)]
    grid = []
    for j in range(n + 1):
        row = []
        for i in range(n + 1):
            u, v = i / n, j / n
            p = P[0] * (1 - u) * (1 - v) + P[1] * u * (1 - v) + P[2] * (1 - u) * v + P[3] * u * v
            p.z -= droop * 16 * u * (1 - u) * v * (1 - v)
            p += Vector((math.sin(u * 9 + j * 0.4) * noise, math.cos(v * 7 + i * 0.3) * noise, math.sin(u * 13 + v * 5) * noise * 0.5))
            row.append(bm.verts.new(p))
        grid.append(row)
    uvl = bm.loops.layers.uv.new("UVMap")
    for j in range(n):
        for i in range(n):
            f = bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
            for lp, (a, b) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
                lp[uvl].uv = (a / n, b / n)
    return obj(name, bm, [m], smooth=True)


def tangle(name, p00, p10, p01, p11, droop=1.5, n=520, near=3):
    """a sheet web: hundreds of short threads knotted across a slung surface, each point tied to its nearest few"""
    P = [Vector(p) for p in (p00, p10, p01, p11)]
    pts = []
    for _ in range(n):
        u, v = rnd.random(), rnd.random()
        p = P[0] * (1 - u) * (1 - v) + P[1] * u * (1 - v) + P[2] * (1 - u) * v + P[3] * u * v
        p.z -= droop * 16 * u * (1 - u) * v * (1 - v) + rnd.uniform(0, 0.25)
        pts.append(p)
    lines = []
    for i, p in enumerate(pts):
        for j in sorted(range(len(pts)), key=lambda j: (pts[j] - p).length)[1:near + 1]:
            if j > i:
                lines.append([tuple(p), tuple(pts[j])])
    threads(name, lines, r=0.004, m=LOOSE)
    sheet(name + "_gauze", p00, p10, p01, p11, droop=droop, noise=0.08, n=20, m=GAUZE)
    # the anchor lines to the walls
    anchors = [sag(P[k], P[k] + (P[k] - (P[0] + P[3]) / 2).normalized() * 0.1, 0.0, n=1) for k in range(4)]
    threads(name + "_guys", anchors, r=0.01, m=LOOSE)


def ring_pt(ang, rad, z):
    return Vector((math.cos(ang) * rad, math.sin(ang) * rad, z))


# ---------------------------------------------------------------- the rotunda
def rotunda():
    bm = bmesh.new()
    bm_b = bmesh.new()
    chord = 2 * R * math.sin(math.pi / BAYS)
    for k in range(BAYS):
        a = (k + 0.5) / BAYS * 2 * math.pi
        yaw = a + math.pi / 2
        inward = -Vector((math.cos(a), math.sin(a), 0))
        base = ring_pt(a, R * math.cos(math.pi / BAYS), 0)
        # pilaster at the bay's edge
        pa = (k / BAYS) * 2 * math.pi
        for zz in range(12):                       # in 1-block lengths, so a funnel can eat through it
            if not in_funnel(ring_pt(pa, R, zz + 0.5)):
                box(bm, ring_pt(pa, R - 0.25, zz + 0.5), (0.5, 0.7, 1.0), pa + math.pi / 2)
        box(bm, base - inward * 3.8 + Vector((0, 0, SHELF_TOP / 2)), (chord, 0.2, SHELF_TOP), yaw)  # back wall, behind the tunnels
        for row in range(12):
            z = row * 1.0
            if not in_funnel(base + Vector((0, 0, z))):
                box(bm, base + inward * 0.05 + Vector((0, 0, z + 0.04)), (chord, 0.55, 0.08), yaw)  # the shelf board
            if (k * 7 + row * 3) % 23 == 0:
                continue                                   # an empty shelf
            t = -chord / 2 + 0.3
            while t < chord / 2 - 0.3:
                w = rnd.uniform(0.05, 0.13)
                h = rnd.uniform(0.55, 0.86)
                lean = rnd.random() < 0.06
                c = base + inward * 0.02 + Vector((math.cos(yaw), math.sin(yaw), 0)) * (t + w / 2) + Vector((0, 0, z + 0.08 + h / 2))
                if not in_funnel(c):
                    box(bm_b, c, (w, 0.36, h), yaw + (0.15 if lean else 0), mi=rnd.randrange(len(LEATHER)))
                t += w + (0.01 if rnd.random() > 0.05 else rnd.uniform(0.1, 0.4))
    obj("shelves", bm, [WALNUT])
    obj("books", bm_b, LEATHER)
    # index drawers band and the dome, with the oculus open
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=False, segments=96, radius=R)
    ret = bmesh.ops.extrude_edge_only(bm, edges=bm.edges[:])
    for v in [e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)]:
        v.co.z = DOME - SHELF_TOP
    bmesh.ops.translate(bm, verts=bm.verts[:], vec=(0, 0, SHELF_TOP))
    o = obj("drawers", bm, [drawer_mat()])
    bm = bmesh.new()
    rings = 14
    prev = None
    for i in range(rings + 1):
        phi = i / rings * math.radians(82)
        rr, zz = R * math.cos(phi), DOME + R * 0.7 * math.sin(phi)
        cur = [bm.verts.new(ring_pt(j / 96 * 2 * math.pi, rr, zz)) for j in range(96)]
        if prev:
            for j in range(96):
                bm.faces.new((prev[j], prev[(j + 1) % 96], cur[(j + 1) % 96], cur[j]))
        prev = cur
    obj("dome", bm, [drawer_mat()], smooth=True)
    # ribs down the dome
    bm = bmesh.new()
    for k in range(16):
        a = k / 16 * 2 * math.pi
        for i in range(12):
            p0 = (i / 12) * math.radians(82)
            p1 = ((i + 1) / 12) * math.radians(82)
            a0 = ring_pt(a, R * math.cos(p0) - 0.2, DOME + R * 0.7 * math.sin(p0))
            a1 = ring_pt(a, R * math.cos(p1) - 0.2, DOME + R * 0.7 * math.sin(p1))
            limb(bm, a0, a1, 0.28, 0.28, seg=6)
        limb(bm, ring_pt(a, R - 0.3, SHELF_TOP), ring_pt(a, R - 0.3, DOME), 0.35, 0.35, seg=6)
    obj("ribs", bm, [WALNUT])
    # the floor
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, segments=96, radius=R + 0.5)
    obj("floor", bm, [floor_mat()])


# ---------------------------------------------------------------- the web and the nest
HUB = Vector((0.6, 1.2, 15.5))


def orb_web():
    spokes = 30
    ends = []
    for i in range(spokes):
        a = i / spokes * 2 * math.pi + rnd.uniform(-0.05, 0.05)
        ends.append(ring_pt(a, R - 0.6, 13.0 + 4.0 * (0.5 + 0.5 * math.sin(a * 2 + 1)) + rnd.uniform(-0.6, 0.6)))
    radials = [sag(HUB, e, 0.6, n=24) for e in ends]
    threads("web_radials", radials, r=0.028)
    spiral = []
    for ring in range(1, 34):
        t = ring / 34.5
        pts = []
        for i in range(spokes + 1):
            rad = radials[i % spokes]
            f = t * 24
            lo, hi = int(f), min(24, int(f) + 1)
            p = Vector(rad[lo]).lerp(Vector(rad[hi]), f - lo)
            pts.append(tuple(p))
        # a gap in the spiral where it was torn
        if ring % 9 == 4:
            pts = pts[:spokes - 7]
        sp = []
        for a, b in zip(pts, pts[1:]):
            sp += sag(a, b, 0.05 + t * 0.12, n=4)[:-1]
        sp.append(pts[-1])
        spiral.append(sp)
    threads("web_spiral", spiral, r=0.011)
    return ends


def cobwebs():
    """loose strands everywhere: shelf to shelf, shelf to floor, dome to shelf"""
    lines = []
    for _ in range(140):
        a1 = rnd.uniform(0, 2 * math.pi)
        a2 = a1 + rnd.uniform(-0.35, 0.35)
        p = ring_pt(a1, R - 0.55, rnd.uniform(0.2, SHELF_TOP + 4))
        q = ring_pt(a2, R - rnd.uniform(0.55, 2.5), rnd.uniform(0.0, SHELF_TOP + 6))
        lines.append(sag(p, q, (p - q).length * rnd.uniform(0.03, 0.12), n=10))
    threads("cobwebs", lines, r=0.004, m=LOOSE)


def drapes():
    """silk sheets hung over the shelves and slung between bays; corners anchored on pilasters"""
    for k in range(8):
        a = k / 8 * 2 * math.pi + rnd.uniform(-0.15, 0.15)
        if abs(math.sin(a) + 1) < 0.25:
            continue                                   # keep the door side open
        w = rnd.uniform(0.18, 0.4)
        top = rnd.uniform(SHELF_TOP - 1, SHELF_TOP + 4)
        z0 = rnd.uniform(1.0, top - 5)
        r0 = R - 0.6
        sheet("drape%d" % k, ring_pt(a, r0 - 0.7, z0), ring_pt(a + w, r0 - 0.9, z0 + rnd.uniform(-1.5, 1.5)),
              ring_pt(a - 0.05, r0, top), ring_pt(a + w + 0.05, r0, top), droop=rnd.uniform(-0.4, 0.4), noise=0.06)
    # hammocks slung low across the room between the walls (the nest's floor sheets)
    for k in range(5):
        a = rnd.uniform(0, 2 * math.pi)
        b = a + rnd.uniform(0.6, 1.2)
        z = rnd.uniform(7, 11)
        tangle("tangle%d" % k, ring_pt(a, R - 0.6, z), ring_pt(b, R - 0.6, z + 0.5), ring_pt(a, R - 5.0, z + 2.5),
               ring_pt(b, R - 5.0, z + 3.0), droop=1.8)


FUNNELS = [(math.radians(70), 3.2, 2.0), (math.radians(128), 7.0, 1.6), (math.radians(28), 8.8, 1.3),
           (math.radians(200), 4.5, 1.5)]


def in_funnel(p):
    """is this point of the shelving where a funnel has eaten through it?"""
    for a, z, mouth in FUNNELS:
        c = ring_pt(a, R, z)
        if (Vector((p.x, p.y, p.z * 1.2)) - Vector((c.x, c.y, c.z * 1.2))).length < mouth * 1.05:
            return True
    return False


def funnel(a, z, mouth):
    """a funnel web opening in the shelf wall: the lip spread flat over the books round the hole, the tube running
    back into the dark behind them"""
    out = Vector((math.cos(a), math.sin(a), 0))
    side = Vector((-out.y, out.x, 0))
    up = Vector((0, 0, 1))
    face = R - 0.7                                    # the shelves' front
    rings, seg = 20, 40

    def ring(t, shrink=1.0):
        # t = 0: the lip, spread on the shelves; t = 0.25: the mouth; t = 1: deep in the wall, narrow
        if t < 0.25:
            k = t / 0.25
            rr = mouth * (1.9 - 0.9 * k)
            d = face - 0.15 + 0.25 * (1 - k) ** 2 * 0 + 0.35 * k * k
        else:
            k = (t - 0.25) / 0.75
            rr = mouth * (1 - 0.6 * k ** 0.7)
            d = face + 0.35 + k * 3.2
        c = Vector((0, 0, z - (0.5 * k * k if t >= 0.25 else 0))) + out * d
        pts = []
        for j in range(seg):
            th = j / seg * 2 * math.pi
            wob = 1 + (0.18 * math.sin(th * 5 + a * 7) + rnd.uniform(-0.05, 0.05)) * (1.0 if t < 0.25 else 0.3)
            p = c + (side * math.cos(th) + up * math.sin(th) * 0.85) * rr * wob * shrink
            if t < 0.25:
                h = Vector((p.x, p.y, 0))
                want = face - 0.1 - 0.45 * math.sin(math.pi * min(1.0, k * 1.1)) * shrink
                p = h.normalized() * want + Vector((0, 0, p.z))
            pts.append(p)
        return pts

    for name, shrink, lo, m in (("funnel", 1.0, 0, silk_mat("funnel_silk", holes=0.22, translucent=0.6, gauze=1.0)),
                                ("throat", 0.9, int(rings * 0.4), mat("throat", (0.003, 0.003, 0.004), 0.9)[0])):
        bm = bmesh.new()
        prev = None
        uvl = bm.loops.layers.uv.new("UVMap")
        for i in range(lo, rings + 1):
            cur = [bm.verts.new(p) for p in ring(i / rings, shrink)]
            if prev:
                for j in range(seg):
                    f = bm.faces.new((prev[j], prev[(j + 1) % seg], cur[(j + 1) % seg], cur[j]))
                    for lp, vv in zip(f.loops, ((i - 1) / rings, (i - 1) / rings, i / rings, i / rings)):
                        lp[uvl].uv = (0.5, min(0.5, vv * 1.6))
            prev = cur
        obj("%s%.1f" % (name, a), bm, [m], smooth=True)
    # guy lines from the lip out over the shelves
    lines = []
    for p in ring(0.0)[::2]:
        q = p + (p - (out * face + Vector((0, 0, z)))).normalized() * rnd.uniform(0.8, 2.2)
        q = ring_pt(math.atan2(q.y, q.x), face + 0.05, max(0.0, q.z))
        lines.append(sag(p, q, 0.05, n=4))
    threads("guys%.1f" % a, lines, r=0.007, m=LOOSE)


def wrap_loops(c, rot, radii, n, out):
    """silk wound round a body any old way: loops round the shape, each tilted at random, at random heights"""
    for _ in range(n):
        h = rnd.uniform(-0.9, 0.9)
        tilt = Matrix.Rotation(rnd.uniform(-0.7, 0.7), 3, "X") @ Matrix.Rotation(rnd.uniform(-0.7, 0.7), 3, "Y")
        pts = []
        steps = 26
        ph = rnd.uniform(0, 6.28)
        arc = rnd.uniform(0.6, 1.0)                        # most loops go most of the way round
        for i in range(steps + 1):
            th = ph + i / steps * 2 * math.pi * arc
            d = tilt @ Vector((math.cos(th), math.sin(th), h))
            dz = max(-0.98, min(0.98, d.z))
            k = math.sqrt(max(0.0, 1 - dz * dz))
            dd = Vector((d.x, d.y, 0))
            dd = dd.normalized() * k if dd.length > 1e-6 else Vector((k, 0, 0))
            p = Vector((dd.x * radii[0], dd.y * radii[1], dz * radii[2])) * 1.04
            pts.append(tuple(c + rot @ p))
        out.append(pts)


WRAPS = []


def cocoon(c, length=1.9, tilt=None, hang=None):
    bm = bmesh.new()
    rot = tilt or Matrix.Identity(3)
    c = Vector(c)
    ellipsoid(bm, c, (0.34, 0.3, length / 2), rot=rot, seg=24)
    ellipsoid(bm, c + rot @ Vector((0, 0, length * 0.22)), (0.42, 0.32, 0.3), rot=rot, seg=16)  # shoulders
    ellipsoid(bm, c + rot @ Vector((0, 0.03, length * 0.43)), (0.2, 0.22, 0.26), rot=rot, seg=14)  # the head
    displace(bm, 0.05, 3.0, seed=len(WRAPS))
    o = obj("cocoon", bm, [WRAP], smooth=True)
    wrap_loops(c, rot, (0.36, 0.33, length / 2), 30, WRAPS)
    if hang:
        top = Vector(c) + rot @ Vector((0, 0, length / 2 + 0.1))
        thread("hang", sag(top, hang, 0.0, n=2), r=0.02)
    return o


def cocoons(ends):
    _cocoons(ends)
    threads("wraps", WRAPS, r=0.007, m=LOOSE)
    WRAPS.clear()


def _cocoons(ends):
    # hanging from the web
    for i in range(16):
        e = Vector(ends[rnd.randrange(len(ends))])
        p = HUB.lerp(e, rnd.uniform(0.25, 0.85))
        drop = rnd.uniform(2.5, 7.5)
        tilt = Matrix.Rotation(rnd.uniform(-0.12, 0.12), 3, "X") @ Matrix.Rotation(rnd.uniform(-0.12, 0.12), 3, "Y")
        cocoon(p - Vector((0, 0, drop)), length=rnd.uniform(1.6, 2.1), tilt=tilt, hang=p)
    # bundled against the shelves, stuck up in the silk
    for i in range(10):
        a = rnd.uniform(0, 2 * math.pi)
        z = rnd.uniform(1.2, 10)
        tilt = Matrix.Rotation(rnd.uniform(-0.3, 0.3), 3, "X")
        cocoon(ring_pt(a, R - 0.85, z), length=rnd.uniform(1.5, 2.0), tilt=tilt)
    # lying on the floor at the edge
    for i in range(5):
        a = rnd.uniform(0, 2 * math.pi)
        cocoon(ring_pt(a, R - 2.0, 0.36), tilt=Matrix.Rotation(math.pi / 2, 3, "X") @ Matrix.Rotation(a, 3, "Y"))


def egg_sacs():
    bm = bmesh.new()
    hangs = []
    for k in range(9):
        a = rnd.uniform(0, 2 * math.pi)
        if math.sin(a) < -0.7:
            continue
        top = ring_pt(a, R - 0.7, rnd.uniform(6, SHELF_TOP + 2))
        for j in range(rnd.randint(2, 5)):
            r = rnd.uniform(0.35, 0.7)
            c = top + Vector((rnd.uniform(-0.8, 0.8), rnd.uniform(-0.8, 0.8), 0)) - Vector((math.cos(a), math.sin(a), 0)) * rnd.uniform(0.4, 1.4)
            c.z -= rnd.uniform(1.0, 3.5)
            ellipsoid(bm, c, (r, r, r * 1.15), seg=20)
            wrap_loops(c, Matrix.Identity(3), (r, r, r * 1.15), 22, WRAPS)
            hangs.append(sag(c + Vector((0, 0, r * 1.1)), top, 0.0, n=1))
    displace(bm, 0.08, 2.5, seed=3)
    obj("sacs", bm, [WRAP], smooth=True)
    threads("sac_threads", hangs, r=0.014, m=LOOSE)
    bm = bmesh.new()
    spots = [(ring_pt(a, R - 2.6, 0), 0.6) for a in (0.5, 2.3)]
    torn = bmesh.new()
    for c, s_ in spots:                              # the torn sac they spilled from
        ellipsoid(torn, c + Vector((0, 0, 0.6)), (0.8, 0.8, 0.7), seg=20)
    displace(torn, 0.12, 2.0, seed=5)
    bmesh.ops.delete(torn, geom=[f for f in torn.faces if f.calc_center_median().z > 0.95 and
                                 f.calc_center_median().x * 0.3 + f.calc_center_median().y > 0], context="FACES")
    obj("torn_sacs", torn, [silk_mat("sac_silk", translucent=0.3, inner=True)], smooth=True)
    for c, s in spots:
        for _ in range(90):
            off = Vector((rnd.gauss(0, 0.9), rnd.gauss(0, 0.9), abs(rnd.gauss(0, 0.12))))
            r = rnd.uniform(0.07, 0.12)
            ellipsoid(bm, c + off + Vector((0, 0, r * 0.8)), (r, r, r * 0.9), seg=12)
    obj("eggs", bm, [EGG], smooth=True)
    # silk netting over each clutch
    for i, (c, s) in enumerate(spots):
        lines = []
        for _ in range(20):
            p = c + Vector((rnd.gauss(0, 0.7 * s), rnd.gauss(0, 0.7 * s), rnd.uniform(0.3, 0.9) * s))
            q = c + Vector((rnd.gauss(0, 1.4 * s), rnd.gauss(0, 1.4 * s), 0.0))
            lines.append(sag(p, q, 0.05, n=4))
        threads("eggnet%d" % i, lines, r=0.006)


def floor_litter():
    bm = bmesh.new()
    bmp = bmesh.new()
    for _ in range(90):
        p = Vector((rnd.uniform(-R, R), rnd.uniform(-R, R), 0))
        if p.length > R - 0.8:
            continue
        if rnd.random() < 0.4:
            box(bm, p + Vector((0, 0, 0.04)), (0.28, 0.2, 0.08), rnd.uniform(0, 6.28), mi=rnd.randrange(len(LEATHER)))
        else:
            box(bmp, p + Vector((0, 0, 0.004)), (0.22, 0.3, 0.006), rnd.uniform(0, 6.28))
    obj("fallen_books", bm, LEATHER)
    obj("pages", bmp, [PAGE])
    # an ink pool spreading from the middle
    bm = bmesh.new()
    pts = []
    for j in range(48):
        a = j / 48 * 2 * math.pi
        rr = 3.2 + 0.9 * math.sin(a * 3 + 1) + 0.5 * math.sin(a * 7)
        pts.append(bm.verts.new((math.cos(a) * rr + 1.2, math.sin(a) * rr + 2.5, 0.01)))
    bm.faces.new(pts)
    obj("ink", bm, [INK])
    # drifts of silk banked against the shelves' feet
    for k in range(10):
        a = rnd.uniform(0, 2 * math.pi)
        w = rnd.uniform(0.2, 0.45)
        sheet("drift%d" % k, ring_pt(a, R - 2.8, 0.02), ring_pt(a + w, R - 2.6, 0.02), ring_pt(a, R - 0.6, 1.8),
              ring_pt(a + w, R - 0.6, 2.2), droop=-0.3, noise=0.1, n=16)


def lamps():
    for k in range(12):
        a = (k + 0.5) / 12 * 2 * math.pi
        p = ring_pt(a, R - 0.9, 4.5)
        bm = bmesh.new()
        box(bm, p, (0.3, 0.3, 0.45), a)
        obj("lamp_glass", bm, [LAMPGLASS])
        bm = bmesh.new()
        box(bm, p + Vector((0, 0, 0.27)), (0.38, 0.38, 0.06), a)
        box(bm, p - Vector((0, 0, 0.27)), (0.38, 0.38, 0.06), a)
        obj("lamp_cage", bm, [PEWTER])
        ld = bpy.data.lights.new("lamp", "POINT")
        ld.energy = 140
        ld.color = (0.55, 0.72, 1.0)
        ld.shadow_soft_size = 0.2
        lo = bpy.data.objects.new("lamp", ld)
        lo.location = p - Vector((math.cos(a), math.sin(a), 0)) * 0.25
        sc.collection.objects.link(lo)


# ---------------------------------------------------------------- the spider
def spider(at=None, size=1.0, yaw=0.0, pitch=0.0):
    """the spider, built under the web's hub; with at, moved there, scaled by size, turned by yaw and pitched (a wall
    crawler is pitched up 90 degrees)"""
    bm = bmesh.new()
    body = HUB + Vector((0, 0, -1.2))
    face = Vector((0, -1, -0.12)).normalized()       # under the web, head toward the door
    rot = face.to_track_quat("Y", "Z").to_matrix()
    ellipsoid(bm, body - rot @ Vector((0, 3.0, 0)), (2.3, 3.2, 2.1), rot=rot, seg=24)    # abdomen
    ellipsoid(bm, body, (1.35, 1.6, 0.95), rot=rot, seg=20)                              # cephalothorax
    ellipsoid(bm, body + rot @ Vector((0, 1.5, 0.15)), (0.8, 0.7, 0.6), rot=rot, seg=16)  # head
    for s in (-1, 1):                                                                   # fangs
        limb(bm, body + rot @ Vector((0.35 * s, 2.0, -0.2)), body + rot @ Vector((0.3 * s, 2.5, -1.1)), 0.18, 0.03)
    for i in range(4):
        for s in (-1, 1):
            root = body + rot @ Vector((1.1 * s, 0.9 - i * 0.6, 0.1))
            out = rot @ Vector((s * math.cos(math.radians(30 + i * 35 - 50)), math.sin(math.radians(60 - i * 40)), 0)).normalized()
            knee = root + out * 3.6 + Vector((0, 0, -1.9 + i * 0.2))
            ankle = root + out * 6.4 + Vector((0, 0, -0.4))
            foot = root + out * 8.2 + Vector((0, 0, 1.15))
            for a_, b_, ra, rb in ((root, knee, 0.34, 0.24), (knee, ankle, 0.24, 0.15), (ankle, foot, 0.15, 0.04)):
                limb(bm, a_, b_, ra, rb, seg=10)
                for k in range(7):                     # spines along each segment, raked toward the foot
                    t = (k + 0.5) / 7
                    p = a_.lerp(b_, t)
                    d = (b_ - a_).normalized()
                    side = d.cross(Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)))).normalized()
                    limb(bm, p, p + side * rnd.uniform(0.25, 0.5) * (ra + 0.1) * 3 + d * 0.25, 0.035, 0.002, seg=4)
            for j_ in (knee, ankle):
                ellipsoid(bm, j_, (0.27, 0.27, 0.27), seg=10)
    # bristles all over the abdomen: backlit, they make the silhouette
    ab_c, ab_r = body - rot @ Vector((0, 3.0, 0)), Vector((2.3, 3.2, 2.1))
    for _ in range(420):
        d = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1))).normalized()
        p = ab_c + rot @ Vector((d.x * ab_r.x, d.y * ab_r.y, d.z * ab_r.z))
        n = rot @ Vector((d.x / ab_r.x, d.y / ab_r.y, d.z / ab_r.z)).normalized()
        limb(bm, p, p + (n + rot @ Vector((0, -0.6, 0))).normalized() * rnd.uniform(0.25, 0.6), 0.03, 0.002, seg=4)
    so = obj("spider", bm, [CHITIN], smooth=True)
    bm = bmesh.new()
    head = body + rot @ Vector((0, 1.95, 0.4))
    for (x, y, r) in ((-0.22, 0.05, 0.13), (0.22, 0.05, 0.13), (-0.48, -0.08, 0.08), (0.48, -0.08, 0.08),
                      (-0.12, 0.25, 0.07), (0.12, 0.25, 0.07), (-0.34, 0.22, 0.05), (0.34, 0.22, 0.05)):
        ellipsoid(bm, head + rot @ Vector((x, 0, y)), (r, r, r), seg=10)
    eo = obj("eyes", bm, [EYE], smooth=True)
    if at is not None:
        m = (Matrix.Translation(Vector(at)) @ Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(pitch, 4, "X")
             @ Matrix.Scale(size, 4) @ Matrix.Translation(-body))
        for o in (so, eo):
            o.data.transform(m)


# ---------------------------------------------------------------- light
def light():
    # moonlight through the oculus, into the fog
    ld = bpy.data.lights.new("moon", "SPOT")
    ld.energy = 900000
    ld.spot_size = math.radians(9)
    ld.spot_blend = 0.4
    ld.color = (0.58, 0.72, 1.0)
    ld.shadow_soft_size = 0.6
    lo = bpy.data.objects.new("moon", ld)
    lo.location = (-1.0, 3.0, 45.0)
    lo.rotation_euler = (Vector((3.0, -5.0, 0)) - Vector(lo.location)).to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(lo)
    bm = bmesh.new()
    rr = R * math.cos(math.radians(82))
    bmesh.ops.create_circle(bm, cap_ends=True, segments=48, radius=rr + 0.2,
                            matrix=Matrix.Translation((0, 0, DOME + R * 0.7 * math.sin(math.radians(82)) + 0.5)))
    sky, sb = mat("sky", (0, 0, 0), 1.0, **{"Emission Strength": 9.0})
    sb.inputs["Emission Color"].default_value = (0.55, 0.7, 1.0, 1)
    oc = obj("oculus", bm, [sky])
    oc.visible_shadow = False
    # the fog filling the hall
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=R - 0.1, radius2=R - 0.1, depth=DOME + 12,
                          matrix=Matrix.Translation((0, 0, (DOME + 12) / 2)))
    m = bpy.data.materials.new("fog")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    pv = nt.nodes.new("ShaderNodeVolumePrincipled")
    pv.inputs["Density"].default_value = 0.014
    pv.inputs["Anisotropy"].default_value = 0.55
    pv.inputs["Color"].default_value = (0.8, 0.85, 0.9, 1)
    nt.links.new(pv.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Volume"])
    obj("fog", bm, [m])
    # a faint bounce from below so the shelves don't sink to black
    ld = bpy.data.lights.new("fill", "AREA")
    ld.energy = 500
    ld.size = 16
    ld.color = (0.4, 0.5, 0.75)
    lo = bpy.data.objects.new("fill", ld)
    lo.location = (0, 0, 0.3)
    lo.rotation_euler = (math.pi, 0, 0)
    sc.collection.objects.link(lo)


def render(SHOTS, prefix):
    """the camera for SHOT, bloom, and the render to tools/renders/dungeon/<prefix>_<shot>.png"""
    loc, aim, lens = SHOTS[SHOT]
    cd = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cd.lens = lens
    cd.clip_end = 300
    cam.location = loc
    cam.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()

    try:
        ng = bpy.data.node_groups.new("comp", "CompositorNodeTree")
        sc.compositing_node_group = ng
        rl = ng.nodes.new("CompositorNodeRLayers")
        gl = ng.nodes.new("CompositorNodeGlare")
        gl.inputs["Type"].default_value = "Bloom"
        gl.inputs["Quality"].default_value = "High"
        gl.inputs["Threshold"].default_value = 1.2
        gl.inputs["Strength"].default_value = 0.3
        gl.inputs["Size"].default_value = 0.6
        ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        go = ng.nodes.new("NodeGroupOutput")
        ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
        ng.links.new(gl.outputs["Image"], go.inputs[0])
        sc.render.use_compositing = True
    except Exception as e:
        print("COMP FAIL", e)

    os.makedirs(OUT, exist_ok=True)
    sc.render.filepath = os.path.abspath(os.path.join(OUT, "%s_%s.png" % (prefix, SHOT)))
    bpy.ops.render.render(write_still=True)
    print("WROTE", sc.render.filepath)


if __name__ == "__main__":
    rotunda()
    ends = orb_web()

    cobwebs()
    drapes()
    for f_ in FUNNELS:
        funnel(*f_)
    cocoons(ends)
    egg_sacs()
    threads("sac_wraps", WRAPS, r=0.007, m=LOOSE)
    floor_litter()
    lamps()
    spider()
    light()

    SHOTS = {
        "hero": ((0.5, -12.6, 1.7), (0.6, 2.0, 9.0), 16),
        "up": ((-1.5, -5.0, 1.2), (0.5, 1.5, 15.5), 14),
        "funnel": ((-1.0, 2.0, 2.4), (4.8, 13.0, 3.4), 22),
    }
    render(SHOTS, "silk")
