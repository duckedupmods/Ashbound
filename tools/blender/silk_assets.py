"""The Silk Archive's props as real meshes, made the way the concept's are (silk_nest.py / silk_rooms.py): cocoons
built from body-shaped ellipsoids with silk wound round them any old way, papers as bent sheets, the lamp as a
moonglass orb gripped by a pewter cage. Each is baked to its own texture (colour x ambient occlusion) and written
as an OBJ in block space for NeoForge's OBJ loader (assets/ashbound/models/mesh/NAME.obj, textures/block/NAME.png).

  blender -b -P tools/blender/silk_assets.py -- [preview] [fast]
    preview: also renders the lineup with the baked textures -> tools/renders/silk_assets.png

Block space: 1 Blender unit = 1 block, the block's floor at z=0 centred on (0.5, -0.5) (OBJ z = -Blender y), the
front of each prop looking along +y (north in game; the blockstate turns it)."""
import os, sys, math, random
import bpy, bmesh
from mathutils import Vector, Matrix, noise

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PREVIEW, FAST = "preview" in ARGS, "fast" in ARGS
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "..", "src", "main", "resources", "assets", "ashbound"))
RENDERS = os.path.normpath(os.path.join(HERE, "..", "renders"))
rnd = random.Random(11)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
try:
    cp = bpy.context.preferences.addons["cycles"].preferences
    cp.compute_device_type = "OPTIX"
    cp.get_devices()
    for d in cp.devices:
        d.use = d.type == "OPTIX"
    sc.cycles.device = "GPU"
except Exception:
    pass


# ---------------------------------------------------------------- materials (procedural, baked away later)

def links(m):
    return m.node_tree.links


def node(m, t):
    return m.node_tree.nodes.new(t)


def bsdf(m):
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def mat(name, color, rough=0.6, **kw):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = bsdf(m)
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    for k, v in kw.items():
        b.inputs[k].default_value = v
    return m


def ramp_color(m, fac_out, stops):
    """a colour ramp driven by fac_out into the base colour"""
    r = node(m, "ShaderNodeValToRGB")
    els = r.color_ramp.elements
    els[0].position, els[0].color = stops[0][0], (*stops[0][1], 1)
    els[1].position, els[1].color = stops[-1][0], (*stops[-1][1], 1)
    for p, c in stops[1:-1]:
        e = els.new(p)
        e.color = (*c, 1)
    links(m).new(fac_out, r.inputs[0])
    return r


def silk_mat(name, base=(0.74, 0.71, 0.64), stain=None):
    """wound silk: tight bands (wave texture along the body) darker in their grooves, mottled, dirtier low down"""
    m = mat(name, base, 0.55, **{"Sheen Weight": 0.6})
    b = bsdf(m)
    tc = node(m, "ShaderNodeTexCoord")
    w = node(m, "ShaderNodeTexWave")
    w.wave_type, w.bands_direction = "BANDS", "Z"
    w.inputs["Scale"].default_value = 16.0
    w.inputs["Distortion"].default_value = 2.5
    w.inputs["Detail"].default_value = 4.0
    links(m).new(tc.outputs["Object"], w.inputs["Vector"])
    nz = node(m, "ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 7.0
    links(m).new(tc.outputs["Object"], nz.inputs["Vector"])
    mix = node(m, "ShaderNodeMix")
    mix.data_type = "FLOAT"
    mix.inputs["Factor"].default_value = 0.35
    links(m).new(w.outputs["Fac"], mix.inputs["A"])
    links(m).new(nz.outputs["Fac"], mix.inputs["B"])
    lo = tuple(c * 0.8 for c in base)
    hi = tuple(min(1, c * 1.12) for c in base)
    r = ramp_color(m, mix.outputs["Result"], [(0.25, lo), (0.55, base), (0.85, hi)])
    out = r.outputs["Color"]
    # dirt creeping up from the floor, and on some a stain where the mouth is
    sep = node(m, "ShaderNodeSeparateXYZ")
    links(m).new(tc.outputs["Object"], sep.inputs[0])
    mr = node(m, "ShaderNodeMapRange")
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 0.0, 0.5
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 0.55, 1.0
    links(m).new(sep.outputs["Z"], mr.inputs["Value"])
    dm = node(m, "ShaderNodeMix")
    dm.data_type, dm.blend_type = "RGBA", "MULTIPLY"
    links(m).new(mr.outputs["Result"], dm.inputs["Factor"])
    dm.inputs["Factor"].default_value = 1.0
    links(m).new(out, dm.inputs["A"])
    links(m).new(mr.outputs["Result"], dm.inputs["B"])
    out = dm.outputs["Result"]
    if stain:
        at, rad, col = stain
        dist = node(m, "ShaderNodeVectorMath")
        dist.operation = "DISTANCE"
        dist.inputs[1].default_value = at
        links(m).new(tc.outputs["Object"], dist.inputs[0])
        st = node(m, "ShaderNodeMapRange")
        st.inputs["From Min"].default_value, st.inputs["From Max"].default_value = rad, rad * 0.25
        links(m).new(dist.outputs["Value"], st.inputs["Value"])
        sm = node(m, "ShaderNodeMix")
        sm.data_type = "RGBA"
        links(m).new(st.outputs["Result"], sm.inputs["Factor"])
        links(m).new(out, sm.inputs["A"])
        sm.inputs["B"].default_value = (*col, 1)
        out = sm.outputs["Result"]
    links(m).new(out, b.inputs["Base Color"])
    bump = node(m, "ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.5
    links(m).new(w.outputs["Fac"], bump.inputs["Height"])
    links(m).new(bump.outputs[0], b.inputs["Normal"])
    return m


def paper_mat(name, base=(0.66, 0.57, 0.4)):
    """old parchment: blotchy, darker at the edges of each sheet (by the sheet's UV), faint lines of writing"""
    m = mat(name, base, 0.85)
    b = bsdf(m)
    tc = node(m, "ShaderNodeTexCoord")
    nz = node(m, "ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 14.0
    nz.inputs["Detail"].default_value = 6.0
    links(m).new(tc.outputs["Object"], nz.inputs["Vector"])
    r = ramp_color(m, nz.outputs["Fac"], [(0.3, tuple(c * 0.72 for c in base)), (0.5, base), (0.7, tuple(min(1, c * 1.1) for c in base))])
    # writing: thin dark bands across each sheet (generated coords run along the sheet)
    lines = node(m, "ShaderNodeTexWave")
    lines.wave_type, lines.bands_direction = "BANDS", "Y"
    lines.inputs["Scale"].default_value = 40.0
    lines.inputs["Distortion"].default_value = 0.6
    links(m).new(tc.outputs["UV"], lines.inputs["Vector"])
    lr = node(m, "ShaderNodeMapRange")
    lr.inputs["From Min"].default_value, lr.inputs["From Max"].default_value = 0.92, 1.0
    links(m).new(lines.outputs["Fac"], lr.inputs["Value"])
    ink = node(m, "ShaderNodeMix")
    ink.data_type = "RGBA"
    links(m).new(lr.outputs["Result"], ink.inputs["Factor"])
    links(m).new(r.outputs["Color"], ink.inputs["A"])
    ink.inputs["B"].default_value = (0.12, 0.09, 0.07, 1)
    links(m).new(ink.outputs["Result"], b.inputs["Base Color"])
    return m


SILK = silk_mat("silk")
SILK_STAINED = silk_mat("silk_stained", stain=((0.0, 0.31, 1.62), 0.22, (0.28, 0.12, 0.08)))
SILK_OLD = silk_mat("silk_old", base=(0.66, 0.64, 0.58))
STRAND = mat("strand", (0.86, 0.84, 0.78), 0.4, **{"Sheen Weight": 1.0})
PAPER = paper_mat("paper")
PAPER_OLD = paper_mat("paper_old", base=(0.55, 0.46, 0.31))
LEATHER = mat("leather", (0.16, 0.07, 0.05), 0.55)
CORD = mat("cord", (0.32, 0.22, 0.13), 0.8)
WAX = mat("wax", (0.38, 0.04, 0.04), 0.35)
INKPOT = mat("inkpot", (0.03, 0.03, 0.04), 0.15, **{"Coat Weight": 1.0})
FEATHER = mat("feather", (0.78, 0.76, 0.7), 0.7)
PEWTER = mat("pewter", (0.2, 0.21, 0.22), 0.38, **{"Metallic": 1.0})
GLASS = mat("moonglass", (0.62, 0.82, 1.0), 0.1, **{"Emission Strength": 3.0})
bsdf(GLASS).inputs["Emission Color"].default_value = (0.6, 0.8, 1.0, 1)


# ---------------------------------------------------------------- geometry

def new_obj(name, bm, mats, smooth=True):
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


def ellipsoid(bm, c, r, mi=0, rot=None, seg=18):
    m = Matrix.Diagonal((*r, 1.0))
    if rot:
        m = rot.to_4x4() @ m
    ret = bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2 + 2, radius=1.0, matrix=Matrix.Translation(c) @ m)
    for f in {f for v in ret["verts"] for f in v.link_faces}:
        f.material_index = mi
    return ret["verts"]


def displace(verts, amt, scale=3.0, seed=0):
    off = Vector((seed * 13.1, seed * 7.7, seed * 3.3))
    for v in verts:
        v.co += v.normal * noise.noise(v.co * scale + off) * amt


def tube(bm, pts, r, mi=0, sides=5):
    """a thin round tube along pts (a strand of silk, a cord)"""
    rings = []
    for i, p in enumerate(pts):
        p = Vector(p)
        a = Vector(pts[max(0, i - 1)])
        b = Vector(pts[min(len(pts) - 1, i + 1)])
        d = (b - a).normalized()
        side = d.cross(Vector((0, 0, 1)))
        if side.length < 1e-3:
            side = d.cross(Vector((1, 0, 0)))
        side.normalize()
        up = side.cross(d)
        rings.append([bm.verts.new(p + (side * math.cos(t) + up * math.sin(t)) * r)
                      for t in (k * 2 * math.pi / sides for k in range(sides))])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            f = bm.faces.new((r0[k], r0[(k + 1) % sides], r1[(k + 1) % sides], r1[k]))
            f.material_index = mi


def wrap_loops(bm, c, rot, radii, n, r=0.016, mi=0, lo=-0.9, hi=0.9):
    """silk wound round a body any old way: loops round the shape, each tilted at random (the concept's way)"""
    for _ in range(n):
        h = rnd.uniform(lo, hi)
        tilt = Matrix.Rotation(rnd.uniform(-0.6, 0.6), 3, "X") @ Matrix.Rotation(rnd.uniform(-0.6, 0.6), 3, "Y")
        ph, arc, steps = rnd.uniform(0, 6.28), rnd.uniform(0.55, 1.0), 22
        pts = []
        for i in range(steps + 1):
            th = ph + i / steps * 2 * math.pi * arc
            d = tilt @ Vector((math.cos(th), math.sin(th), h))
            dz = max(-0.97, min(0.97, d.z))
            k = math.sqrt(max(0.0, 1 - dz * dz))
            dd = Vector((d.x, d.y, 0))
            dd = dd.normalized() * k if dd.length > 1e-6 else Vector((k, 0, 0))
            pts.append(c + rot @ (Vector((dd.x * radii[0], dd.y * radii[1], dz * radii[2])) * 1.03))
        tube(bm, pts, r, mi)


def body(bm, base, length, rot, seed, mi=0, slump=0.0, hand=True):
    """a person wound in silk: the long bundle, the shoulders, the head; a hand pressing out from inside"""
    c = Vector(base) + rot @ Vector((0, 0, length / 2))
    vs = ellipsoid(bm, c, (0.27, 0.23, length / 2), mi, rot, seg=24)
    vs += ellipsoid(bm, c + rot @ Vector((0, slump * 0.5, length * 0.2)), (0.3, 0.24, 0.24), mi, rot, seg=18)      # shoulders
    head = c + rot @ Vector((0, 0.03 + slump, length * 0.4))
    vs += ellipsoid(bm, head, (0.15, 0.16, 0.19), mi, rot, seg=16)
    vs += ellipsoid(bm, c + rot @ Vector((0, 0.02, -length * 0.3)), (0.2, 0.18, 0.26), mi, rot, seg=14)            # the knees and shins
    if hand:   # fingers pushing the silk out, as if they're still trying
        hc = c + rot @ Vector((0.09, 0.21, length * 0.05))
        for k in range(4):
            vs += ellipsoid(bm, hc + rot @ Vector((-0.04 + k * 0.028, 0.02, 0.05 + 0.012 * (k % 2))), (0.016, 0.03, 0.05), mi, rot, seg=8)
    bm.normal_update()
    displace(vs, 0.018, 4.0, seed)
    return c, head


def silk_foot(bm, at, rad, mi=0, seed=0):
    """silk spread on the floor round where a cocoon is stuck down: a flat lumpy skirt"""
    ret = bmesh.ops.create_circle(bm, cap_ends=True, segments=20, radius=rad, matrix=Matrix.Translation(at))
    vs = ret["verts"]
    for v in vs:
        v.co.z += 0.004 + max(0.0, noise.noise(v.co * 6 + Vector((seed, 0, 0)))) * 0.03
    for f in {f for v in vs for f in v.link_faces}:
        f.material_index = mi


def strands(bm, pairs, r=0.012, mi=0):
    for a, b in pairs:
        a, b = Vector(a), Vector(b)
        tube(bm, [a.lerp(b, t) for t in (0, 0.5, 1)], r, mi, sides=4)


def sheet(bm, c, w, d, yaw, curl=0.0, lift=0.0, mi=0, n=6):
    """one sheet of paper: a thin bent grid, its far end curled up"""
    rot = Matrix.Rotation(yaw, 3, "Z")
    grid = []
    for i in range(n + 1):
        row = []
        for j in range(3):
            u, v = i / n, j / 2
            x, y = (u - 0.5) * w, (v - 0.5) * d
            z = lift + curl * (max(0.0, u - 0.6) / 0.4) ** 2 + noise.noise(Vector((x * 9, y * 9, c.x * 5))) * 0.004
            row.append(bm.verts.new(c + rot @ Vector((x, y, z))))
        grid.append(row)
    for i in range(n):
        for j in range(2):
            f = bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
            f.material_index = mi
    # the sheet's thickness: a thin skirt down from its edges
    edge = [grid[i][0] for i in range(n + 1)] + [grid[n][j] for j in range(1, 3)] + [grid[i][2] for i in range(n - 1, -1, -1)] + [grid[0][1]]
    for a, b in zip(edge, edge[1:] + edge[:1]):
        a2 = bm.verts.new(a.co - Vector((0, 0, 0.006)))
        b2 = bm.verts.new(b.co - Vector((0, 0, 0.006)))
        bm.faces.new((a, b, b2, a2)).material_index = mi


def slab(bm, c, size, yaw=0.0, mi=0, round_=0.0):
    rot = Matrix.Rotation(yaw, 3, "Z")
    ret = bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(c) @ rot.to_4x4() @ Matrix.Diagonal((*size, 1)))
    if round_:
        bmesh.ops.bevel(bm, geom=[e for e in ret["verts"][0].link_edges] and list({e for v in ret["verts"] for e in v.link_edges}),
                        offset=round_, segments=2, affect="EDGES")
    for f in {f for v in ret["verts"] for f in v.link_faces if f.is_valid}:
        f.material_index = mi


def cyl(bm, c, r, h, mi=0, seg=12, r2=None):
    ret = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h,
                                matrix=Matrix.Translation(Vector(c) + Vector((0, 0, h / 2))))
    for f in {f for v in ret["verts"] for f in v.link_faces}:
        f.material_index = mi


def scroll(bm, c, length, r, yaw, mi_p=0, mi_c=1):
    rot = Matrix.Rotation(yaw, 3, "Z") @ Matrix.Rotation(math.pi / 2, 3, "Y")
    ret = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=r, radius2=r, depth=length,
                                matrix=Matrix.Translation(c) @ rot.to_4x4())
    for f in {f for v in ret["verts"] for f in v.link_faces}:
        f.material_index = mi_p
    d = Matrix.Rotation(yaw, 3, "Z") @ Vector((1, 0, 0))
    for t in (-0.18, 0.2):   # the cords tying it
        ret = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=r * 1.12, radius2=r * 1.12, depth=0.012,
                                    matrix=Matrix.Translation(c + d * (length * t)) @ rot.to_4x4())
        for f in {f for v in ret["verts"] for f in v.link_faces}:
            f.material_index = mi_c


# ---------------------------------------------------------------- the props (centred on the block: x 0.5, y -0.5)

O = Vector((0.5, -0.5, 0.0))


def fuse(name, core, extra, skin, strand=None, voxel=0.024, ratio=0.3, seed=0):
    """the body's overlapping shapes melted into one smooth skin (voxel remesh, smoothed, thinned out, a little
    lumpy), then the loose silk wound over it added on"""
    o = new_obj(name, core, [skin])
    bpy.context.view_layer.objects.active = o
    for kind, set_ in (("REMESH", lambda m: (setattr(m, "mode", "VOXEL"), setattr(m, "voxel_size", voxel))),
                       ("SMOOTH", lambda m: (setattr(m, "factor", 0.7), setattr(m, "iterations", 6))),
                       ("DECIMATE", lambda m: setattr(m, "ratio", ratio))):
        m = o.modifiers.new(kind.lower(), kind)
        set_(m)
        bpy.ops.object.modifier_apply(modifier=m.name)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.normal_update()
    displace(bm.verts, 0.012, 5.0, seed)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(o.data)
    bm.free()
    if extra is not None:
        x = new_obj(name + "_silk", extra, [strand or STRAND])
        bpy.ops.object.select_all(action="DESELECT")
        x.select_set(True)
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.join()
    o.name = name
    return o


def cocoon_stand():
    """a visitor still standing in the queue, wound to the floor (two blocks tall)"""
    core, silk = bmesh.new(), bmesh.new()
    rot = Matrix.Rotation(0.08, 3, "X")
    c, head = body(core, O + Vector((0, 0, 0.02)), 1.86, rot, seed=1, slump=0.03)
    wrap_loops(silk, c, rot, (0.27, 0.23, 0.92), 20, r=0.011)
    silk_foot(silk, O, 0.42, seed=1)
    return fuse("silk_cocoon_stand", core, silk, SILK_STAINED, seed=1)


def cocoon_seat():
    """a reader cocooned in the chair: the bundle sat back, the knees forward over the seat (base at the seat top)"""
    core, silk = bmesh.new(), bmesh.new()
    seat = O + Vector((0, -0.04, -0.4375))
    rot = Matrix.Rotation(-0.14, 3, "X")
    c, head = body(core, seat + Vector((0, -0.08, 0.02)), 1.22, rot, seed=2, slump=0.06, hand=False)
    ellipsoid(core, seat + Vector((0, 0.2, 0.14)), (0.25, 0.3, 0.14), 0, None, seg=16)           # the thighs
    ellipsoid(core, seat + Vector((0, 0.44, -0.04)), (0.2, 0.12, 0.22), 0, None, seg=14)         # the shins down the front
    wrap_loops(silk, c, rot, (0.27, 0.23, 0.6), 12, r=0.011)
    wrap_loops(silk, seat + Vector((0, 0.26, 0.08)), Matrix.Rotation(math.pi / 2 - 0.1, 3, "X"), (0.24, 0.22, 0.3), 5, r=0.011)
    return fuse("silk_cocoon_seat", core, silk, SILK, seed=2)


def cocoon_hang():
    """hung from the web on a twisted cable: the body two blocks long, the cable to the top of a third"""
    core, silk = bmesh.new(), bmesh.new()
    rot = Matrix.Rotation(0.06, 3, "Y") @ Matrix.Rotation(-0.05, 3, "X")
    base = O + Vector((0, 0, 0.3))
    c, head = body(core, base, 2.0, rot, seed=3, slump=0.0)
    ellipsoid(core, base + Vector((0, 0, 0.04)), (0.15, 0.13, 0.14), 0, None, seg=12)   # the feet, bundled to a point
    wrap_loops(silk, c, rot, (0.27, 0.23, 1.0), 22, r=0.011)
    top = head + Vector((0, 0, 0.17))
    cable = [top.lerp(O + Vector((0.0, 0.0, 3.0)), t) + Vector((0.012 * math.sin(t * 9), 0.012 * math.cos(t * 9), 0))
             for t in (k / 8 for k in range(9))]
    tube(silk, cable, 0.03, 0, sides=6)
    tube(silk, [p + Vector((0.028, 0, 0)) for p in cable], 0.015, 0, sides=4)
    tube(silk, [base + Vector((0, 0, 0.0)), base + Vector((0.03, 0.02, -0.15)), base + Vector((0.06, 0.01, -0.28))], 0.012, 0, sides=4)
    return fuse("silk_cocoon_hang", core, silk, SILK_OLD, seed=3)


def cocoon_pressed():
    """squeezed in a book press between its iron plates: a flattened bundle, an arm hanging out wrapped"""
    core, silk = bmesh.new(), bmesh.new()
    rot = Matrix.Rotation(math.pi / 2, 3, "Y")
    vs = ellipsoid(core, O + Vector((0, 0, 0.5)), (0.42, 0.44, 0.5), 0, rot, seg=20)
    vs += ellipsoid(core, O + Vector((0.05, 0.2, 0.2)), (0.2, 0.32, 0.14), 0, None, seg=12)
    for v in vs:   # pressed flat top and bottom, bulging out of the sides
        v.co.z = min(0.985, max(0.015, v.co.z))
    tube(core, [O + Vector((-0.2, 0.34, 0.36)), O + Vector((-0.24, 0.47, 0.2)), O + Vector((-0.25, 0.5, 0.03))], 0.065, 0, sides=8)  # the arm
    wrap_loops(silk, O + Vector((0, 0, 0.5)), rot, (0.44, 0.45, 0.47), 10, r=0.011, lo=-0.7, hi=0.7)
    return fuse("silk_cocoon_pressed", core, silk, SILK_STAINED, voxel=0.02, ratio=0.35, seed=4)


def papers(bm, base, n, spread, big=False):
    for k in range(n):
        c = base + Vector((rnd.uniform(-spread, spread), rnd.uniform(-spread, spread), 0.007 * k))
        g = 1.3 if big else 1.0
        sheet(bm, c, rnd.uniform(0.34, 0.42) * g, rnd.uniform(0.25, 0.3) * g, rnd.uniform(-0.6, 0.6),
              curl=rnd.choice((0.0, 0.0, 0.03, 0.06)), mi=rnd.choice((0, 0, 1)))


def parchment_desk():
    """what's left on a reader's desk (base on a slab: half a block down): loose sheets fanned out, a ledger, a tied
    scroll, an ink pot with its quill"""
    bm = bmesh.new()
    top = O + Vector((0, 0, -0.5))
    papers(bm, top + Vector((-0.08, 0.06, 0.003)), 12, 0.1, big=True)
    led = top + Vector((0.18, -0.14, 0))
    slab(bm, led + Vector((0, 0, 0.035)), (0.32, 0.24, 0.07), 0.3, 2)
    slab(bm, led + Vector((0.005, 0.0, 0.035)), (0.3, 0.22, 0.055), 0.3, 0)
    scroll(bm, top + Vector((-0.1, -0.3, 0.035)), 0.42, 0.034, 0.15, 0, 3)
    pot = top + Vector((0.28, 0.24, 0))
    cyl(bm, pot, 0.05, 0.075, 4, 12, 0.035)
    tube(bm, [pot + Vector((0, 0, 0.05)), pot + Vector((0.04, -0.03, 0.2)), pot + Vector((0.07, -0.06, 0.34))], 0.006, 5, sides=4)
    for k in range(6):   # the quill's vane
        t = 0.4 + k * 0.1
        a = pot + Vector((0.04 * t / 0.5, -0.03 * t / 0.5, 0.05 + 0.29 * t))
        tube(bm, [a, a + Vector((0.035, 0.025, -0.02))], 0.008, 5, sides=3)
    slab(bm, top + Vector((-0.02, 0.1, 0.075)), (0.05, 0.05, 0.015), 0.4, 6)   # a wax seal on the pile
    return new_obj("parchment_desk", bm, [PAPER, PAPER_OLD, LEATHER, CORD, INKPOT, FEATHER, WAX], smooth=False)


def parchment_full():
    """a full block of paper: reams stacked crooked and bound with cord, waiting in the press"""
    bm = bmesh.new()
    z = 0.0
    k = 0
    while z < 0.94:
        h = rnd.uniform(0.07, 0.12)
        mi = rnd.choice((0, 0, 1))
        slab(bm, O + Vector((rnd.uniform(-0.03, 0.03), rnd.uniform(-0.03, 0.03), z + h / 2)),
             (rnd.uniform(0.82, 0.9), rnd.uniform(0.82, 0.9), h * 0.96), rnd.uniform(-0.06, 0.06), mi)
        z += h
        k += 1
    for y in (-0.2, 0.22):   # two cords tied round the stack: over the top, down both sides
        slab(bm, O + Vector((0, y, 0.995)), (0.93, 0.022, 0.012), 0.0, 3)
        for x in (-0.462, 0.462):
            slab(bm, O + Vector((x, y, 0.5)), (0.012, 0.022, 0.99), 0.0, 3)
    for p in range(5):        # sheets sticking out of the sides
        papers(bm, O + Vector((rnd.uniform(-0.25, 0.25), rnd.uniform(-0.25, 0.25), rnd.uniform(0.15, 0.85))), 1, 0.12)
    papers(bm, O + Vector((0, 0, 0.955)), 4, 0.08)
    return new_obj("parchment_full", bm, [PAPER, PAPER_OLD, LEATHER, CORD], smooth=False)


def archive_lamp():
    """a moonglass orb gripped by eight pewter legs, like a spider holding an egg, a ring on top for its chain"""
    bm = bmesh.new()
    c = O + Vector((0, 0, 0.48))
    ellipsoid(bm, c, (0.27, 0.27, 0.3), 1, None, seg=20)
    for k in range(8):
        a = k * math.pi / 4 + 0.2
        d = Vector((math.cos(a), math.sin(a), 0))
        pts = [c + Vector((0, 0, 0.36)), c + d * 0.16 + Vector((0, 0, 0.38)), c + d * 0.33 + Vector((0, 0, 0.22)),
               c + d * 0.31 + Vector((0, 0, -0.1)), c + d * 0.16 + Vector((0, 0, -0.33))]
        tube(bm, pts, 0.024, 0, sides=5)
        tube(bm, [pts[2], pts[2] + d * 0.08 + Vector((0, 0, 0.06))], 0.016, 0, sides=4)   # a spur at each knee
    ret = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.09, radius2=0.04, depth=0.12,
                                matrix=Matrix.Translation(c + Vector((0, 0, 0.42))))
    ring = [c + Vector((0.05 * math.cos(t), 0, 0.5 + 0.05 * math.sin(t))) for t in (k * math.pi / 6 for k in range(13))]
    tube(bm, ring, 0.014, 0, sides=4)
    ret2 = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.02, radius2=0.08, depth=0.08,
                                 matrix=Matrix.Translation(c + Vector((0, 0, -0.36))))
    return new_obj("archive_lamp", bm, [PEWTER, GLASS])


# ---------------------------------------------------------------- baking and writing

def bake(o, size):
    """its own texture: base colour times ambient occlusion, onto a fresh smart UV map"""
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.006)
    bpy.ops.object.mode_set(mode="OBJECT")
    w, h = size
    col = bpy.data.images.new(o.name + "_col", w, h)
    ao = bpy.data.images.new(o.name + "_ao", w, h)
    sc.cycles.samples = 16 if FAST else 64
    for img, kind in ((col, "DIFFUSE"), (ao, "AO")):
        for m in o.data.materials:
            n = m.node_tree.nodes.get("bake") or node(m, "ShaderNodeTexImage")
            n.name = "bake"
            n.image = img
            m.node_tree.nodes.active = n
        if kind == "DIFFUSE":
            bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, margin=4)
        else:
            bpy.ops.object.bake(type="AO", margin=4)
    cp_, ap = list(col.pixels), list(ao.pixels)
    out = bpy.data.images.new(o.name, w, h, alpha=True)
    px = [0.0] * len(cp_)
    for i in range(0, len(cp_), 4):
        a = 0.62 + 0.38 * ap[i]        # crevices darker, never black
        px[i], px[i + 1], px[i + 2], px[i + 3] = cp_[i] * a, cp_[i + 1] * a, cp_[i + 2] * a, 1.0
    out.pixels = px
    out.filepath_raw = os.path.join(ASSETS, "textures", "block", o.name + ".png")
    out.file_format = "PNG"
    out.save()
    for m in o.data.materials:
        m.node_tree.nodes.remove(m.node_tree.nodes["bake"])
    return out


def write_obj(o, glow_mat=None):
    """into block space for the OBJ loader (x, z up, -y), one group per material so the glow can be full-bright"""
    path = os.path.join(ASSETS, "models", "mesh", o.name + ".obj")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    me = o.data
    me.calc_loop_triangles()
    uv = me.uv_layers.active.data
    lines = ["mtllib %s.mtl" % o.name, "# Ashbound Silk Archive prop (tools/blender/silk_assets.py); block space"]
    for v in me.vertices:
        lines.append("v %.5f %.5f %.5f" % (v.co.x, v.co.z, -v.co.y))
    uvs, nrm = {}, {}
    faces_by = {}
    for t in me.loop_triangles:
        faces_by.setdefault(t.material_index, []).append(t)
    vt, vn, body_ = [], [], []
    for mi, tris in faces_by.items():
        glow = glow_mat is not None and me.materials[mi] == glow_mat
        body_.append("g %s" % ("fire" if glow else "part%d" % mi))
        body_.append("usemtl %s" % ("glow" if glow else "prop"))
        for t in tris:
            ids = []
            for li, vi in zip(t.loops, t.vertices):
                u = tuple(round(c, 5) for c in uv[li].uv)
                n = me.corner_normals[li].vector if hasattr(me, "corner_normals") else me.loops[li].normal
                n = (round(n.x, 4), round(n.z, 4), round(-n.y, 4))
                if u not in uvs:
                    uvs[u] = len(uvs) + 1
                    vt.append("vt %.5f %.5f" % u)
                if n not in nrm:
                    nrm[n] = len(nrm) + 1
                    vn.append("vn %.4f %.4f %.4f" % n)
                ids.append("%d/%d/%d" % (vi + 1, uvs[u], nrm[n]))
            body_.append("f " + " ".join(ids))
    open(path, "w", encoding="utf-8").write("\n".join(lines + vt + vn + body_) + "\n")
    tex = "ashbound:block/" + o.name
    open(path[:-4] + ".mtl", "w", encoding="utf-8").write(
        "newmtl prop\nKa 0 0 0\nmap_Kd %s\n\nnewmtl glow\nKa 1 1 1\nmap_Kd %s\n" % (tex, tex))
    print("wrote", o.name, len(me.loop_triangles), "tris")


MAKE = [(cocoon_stand, (512, 512)), (cocoon_seat, (512, 512)), (cocoon_hang, (512, 512)), (cocoon_pressed, (256, 256)),
        (parchment_desk, (256, 256)), (parchment_full, (256, 256)), (archive_lamp, (128, 128))]
done = []
for make, size in MAKE:
    o = make()
    img = bake(o, size)
    write_obj(o, GLASS)
    done.append((o, img))


# ---------------------------------------------------------------- the lineup, with the baked textures (what the game gets)

if PREVIEW:
    for i, (o, img) in enumerate(done):
        m = bpy.data.materials.new(o.name + "_baked")
        m.use_nodes = True
        b = bsdf(m)
        b.inputs["Roughness"].default_value = 0.7
        t = node(m, "ShaderNodeTexImage")
        t.image = img
        t.interpolation = "Closest"
        links(m).new(t.outputs["Color"], b.inputs["Base Color"])
        if o.name == "archive_lamp":
            links(m).new(t.outputs["Color"], b.inputs["Emission Color"])
            b.inputs["Emission Strength"].default_value = 1.5
        o.data.materials.clear()
        o.data.materials.append(m)
        o.location.x = i * 1.6 - 0.5
        # a block outline for scale, and the block each sits on
        for z in range(-1 if o.name.startswith("parchment_desk") or o.name == "silk_cocoon_seat" else 0, 0):
            pass
    fl = bpy.data.meshes.new("floor")
    bmf = bmesh.new()
    bmesh.ops.create_grid(bmf, x_segments=1, y_segments=1, size=12, matrix=Matrix.Translation((5, 0, 0)))
    bmf.to_mesh(fl)
    fo = bpy.data.objects.new("floor", fl)
    sc.collection.objects.link(fo)
    fm = mat("floorstone", (0.18, 0.18, 0.2), 0.8)
    fl.materials.append(fm)
    for o, _ in done:   # what they stand on in the dungeon: desks and chairs as plain boxes, half a block high
        if o.name in ("parchment_desk", "silk_cocoon_seat"):
            sb = bmesh.new()
            bmesh.ops.create_cube(sb, size=1.0, matrix=Matrix.Translation(Vector((o.location.x + 0.5, -0.5, -0.25))) @ Matrix.Diagonal((1, 1, 0.5, 1)))
            bmesh.ops.translate(sb, verts=sb.verts, vec=(0, 0, 0.5))
            so = new_obj("stand", sb, [mat("walnut", (0.14, 0.08, 0.05), 0.6)], smooth=False)
            o.location.z = 1.0
        if o.name == "archive_lamp":
            o.location.z = 1.4
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.025, 0.035, 1)
    for loc, en, col in (((-3, -6, 6), 900, (1.0, 0.86, 0.7)), ((12, -4, 4), 400, (0.6, 0.75, 1.0)), ((5, 6, 5), 500, (0.8, 0.85, 1.0))):
        ld = bpy.data.lights.new("l", "AREA")
        ld.energy, ld.color, ld.size = en, col, 5
        lo = bpy.data.objects.new("l", ld)
        lo.location = loc
        lo.rotation_euler = (Vector((5, 0, 1)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(lo)
    cd = bpy.data.cameras.new("cam")
    cd.lens = 36
    co = bpy.data.objects.new("cam", cd)
    co.location = (5.0, -12.5, 3.0)
    co.rotation_euler = (Vector((5.0, 0, 1.1)) - Vector(co.location)).to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(co)
    sc.camera = co
    sc.render.resolution_x, sc.render.resolution_y = 1800, 760
    sc.cycles.samples = 32 if FAST else 128
    sc.view_settings.view_transform = "AgX"
    sc.render.filepath = os.path.join(RENDERS, "silk_assets.png")
    bpy.ops.render.render(write_still=True)
    print("rendered", sc.render.filepath)
