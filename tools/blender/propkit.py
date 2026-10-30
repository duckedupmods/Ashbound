"""Shared bits for the gates' sculpted props (exec'd by tools/blender/<gate>_props.py): procedural Cycles materials,
mesh helpers, the bake (colour x ambient occlusion onto a fresh UV map), the OBJ writer for NeoForge's loader and a
lineup render to judge them by. The same pipeline as silk_assets.py.

Block space: 1 Blender unit = 1 block, the block's floor at z=0 centred on O = (0.5, -0.5) (OBJ z = -Blender y),
each prop's front looking along +y (north in game; the blockstate turns it)."""
import os, sys, math, random
import bpy, bmesh
from mathutils import Vector, Matrix, noise

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PREVIEW, FAST = "preview" in ARGS, "fast" in ARGS
ONLY = [a for a in ARGS if a not in ("preview", "fast")]
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "..", "src", "main", "resources", "assets", "ashbound"))
RENDERS = os.path.normpath(os.path.join(HERE, "..", "renders"))
rnd = random.Random(11)
O = Vector((0.5, -0.5, 0.0))

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


# ---------------------------------------------------------------- materials

def node(m, t, x=0, y=0):
    n = m.node_tree.nodes.new(t)
    n.location = (x, y)
    return n


def bsdf(m):
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def link(m, a, b):
    m.node_tree.links.new(a, b)


def mat(name, color, rough=0.6, **kw):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = bsdf(m)
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    for k, v in kw.items():
        b.inputs[k].default_value = v
    return m


def ramp(m, fac, stops):
    r = node(m, "ShaderNodeValToRGB", -300, 0)
    els = r.color_ramp.elements
    els[0].position, els[0].color = stops[0][0], (*stops[0][1], 1)
    els[1].position, els[1].color = stops[-1][0], (*stops[-1][1], 1)
    for p, c in stops[1:-1]:
        e = els.new(p)
        e.color = (*c, 1)
    link(m, fac, r.inputs["Fac"])
    return r.outputs["Color"]


def coords(m, scale=(1, 1, 1)):
    tc = node(m, "ShaderNodeTexCoord", -1100, 0)
    mp = node(m, "ShaderNodeMapping", -950, 0)
    mp.inputs["Scale"].default_value = scale
    link(m, tc.outputs["Object"], mp.inputs["Vector"])
    return mp.outputs["Vector"]


def noise_tex(m, vec, scale, detail=4.0, rough=0.55, distort=0.0):
    n = node(m, "ShaderNodeTexNoise", -700, 0)
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    n.inputs["Roughness"].default_value = rough
    n.inputs["Distortion"].default_value = distort
    link(m, vec, n.inputs["Vector"])
    return n.outputs["Fac"]


def wood(name, stops, along="Z", grain=26.0, rough=0.7):
    """wood: long streaks of grain along one axis, knots of darker mottling, the colour from stops"""
    m = mat(name, stops[1][1], rough)
    sx = {"X": (1, grain, grain), "Y": (grain, 1, grain), "Z": (grain, grain, 1)}[along]
    g = noise_tex(m, coords(m, sx), 3.0, 6.0, 0.6, 1.5)
    mot = noise_tex(m, coords(m), 5.0, 3.0, 0.5)
    mx = node(m, "ShaderNodeMath", -450, 0)
    mx.operation = "MULTIPLY_ADD"
    mx.inputs[1].default_value = 0.6
    link(m, g, mx.inputs[0])
    link(m, mot, mx.inputs[2])
    link(m, ramp(m, mx.outputs[0], stops), bsdf(m).inputs["Base Color"])
    return m


def rusty(name, iron=(0.06, 0.055, 0.05), rust=(0.36, 0.13, 0.04), amount=0.5, rough=0.55, metal=0.7):
    """iron gone to rust in blooms: dark metal, orange-brown scale where the noise rises over `amount`"""
    m = mat(name, iron, rough, Metallic=metal)
    n = noise_tex(m, coords(m), 9.0, 8.0, 0.65, 0.4)
    c = ramp(m, n, [(0.0, iron), (amount - 0.08, iron), (amount + 0.06, rust), (1.0, tuple(v * 0.7 for v in rust))])
    link(m, c, bsdf(m).inputs["Base Color"])
    r = ramp(m, n, [(0.0, (0.35, 0.35, 0.35)), (amount, (0.9, 0.9, 0.9)), (1.0, (0.95, 0.95, 0.95))])
    link(m, r, bsdf(m).inputs["Roughness"])
    return m


def mottled(name, stops, scale=6.0, rough=0.6, **kw):
    m = mat(name, stops[0][1], rough, **kw)
    link(m, ramp(m, noise_tex(m, coords(m), scale, 5.0, 0.6), stops), bsdf(m).inputs["Base Color"])
    return m


def glass(name, color, glow=0.0, rough=0.08):
    """glass for the bake: its colour as diffuse (the game draws it flat); glow for the lamps' full-bright group"""
    kw = {"Coat Weight": 1.0}
    if glow:
        kw.update({"Emission Color": (*color, 1), "Emission Strength": glow})
    return mat(name, color, rough, **kw)


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


def _mi(ret, mi):
    for f in {f for v in ret["verts"] for f in v.link_faces}:
        f.material_index = mi
    return ret["verts"]


def box(bm, lo, hi, mi=0, bevel=0.0, rot=None):
    """a box from corner lo to corner hi (block units), its edges rounded by `bevel`"""
    before = set(bm.verts)
    lo, hi = Vector(lo), Vector(hi)
    c, s = (lo + hi) / 2, hi - lo
    m = Matrix.Translation(c) @ ((rot.to_4x4() if rot else Matrix()) @ Matrix.Diagonal((*s, 1)))
    ret = bmesh.ops.create_cube(bm, size=1.0, matrix=m)
    vs = _mi(ret, mi)
    if bevel:
        es = list({e for v in vs for e in v.link_edges})
        bmesh.ops.bevel(bm, geom=es, offset=bevel, segments=2, affect="EDGES", profile=0.5)
        for f in {f for v in bm.verts if v not in before for f in v.link_faces}:
            f.material_index = mi
    return [v for v in bm.verts if v not in before]


def cyl(bm, c, r, h, mi=0, seg=16, r2=None, axis="Z", cap=True):
    """a cylinder of radius r (r2 at the far end) and length h starting at c along axis"""
    rot = {"Z": Matrix(), "X": Matrix.Rotation(math.pi / 2, 4, "Y"), "Y": Matrix.Rotation(-math.pi / 2, 4, "X")}[axis]
    d = {"Z": Vector((0, 0, h / 2)), "X": Vector((h / 2, 0, 0)), "Y": Vector((0, h / 2, 0))}[axis]
    ret = bmesh.ops.create_cone(bm, cap_ends=cap, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h,
                                matrix=Matrix.Translation(Vector(c) + d) @ rot)
    return _mi(ret, mi)


def ellipsoid(bm, c, r, mi=0, rot=None, seg=18):
    m = Matrix.Diagonal((*r, 1.0))
    if rot:
        m = rot.to_4x4() @ m
    ret = bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2 + 2, radius=1.0, matrix=Matrix.Translation(c) @ m)
    return _mi(ret, mi)


def tube(bm, pts, r, mi=0, sides=6, closed=False):
    """a round tube along pts"""
    pts = [Vector(p) for p in pts]
    if closed:
        pts = pts + [pts[0]]
    rings = []
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)] if not closed or i else pts[-2]
        b = pts[min(len(pts) - 1, i + 1)]
        d = (b - a).normalized()
        side = d.cross(Vector((0, 0, 1)))
        if side.length < 1e-3:
            side = d.cross(Vector((1, 0, 0)))
        side.normalize()
        up = side.cross(d)
        rr = r(i / max(1, len(pts) - 1)) if callable(r) else r
        rings.append([bm.verts.new(p + (side * math.cos(t) + up * math.sin(t)) * rr)
                      for t in (k * 2 * math.pi / sides for k in range(sides))])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            bm.faces.new((r0[k], r0[(k + 1) % sides], r1[(k + 1) % sides], r1[k])).material_index = mi
    if not closed:
        for ring in (rings[0], rings[-1][::-1]):
            bm.faces.new(ring[::-1] if ring is rings[0] else ring).material_index = mi


def ring(c, r, axis="Z", n=24, wobble=0.0, seed=0):
    """points round a circle about c, for a hoop or a link"""
    out = []
    for k in range(n):
        t = k * 2 * math.pi / n
        rr = r * (1 + wobble * noise.noise(Vector((math.cos(t) * 2, math.sin(t) * 2, seed))))
        p = {"Z": (math.cos(t) * rr, math.sin(t) * rr, 0), "Y": (math.cos(t) * rr, 0, math.sin(t) * rr),
             "X": (0, math.cos(t) * rr, math.sin(t) * rr)}[axis]
        out.append(Vector(c) + Vector(p))
    return out


def lathe(bm, profile, axis_c, mi=0, seg=24, axis="Z", cap=True):
    """a turned shape: profile is [(radius, height)], spun round the axis through axis_c"""
    rings = []
    for (r, h) in profile:
        pts = ring(Vector(axis_c) + {"Z": Vector((0, 0, h)), "Y": Vector((0, h, 0)), "X": Vector((h, 0, 0))}[axis], r, axis, seg)
        rings.append([bm.verts.new(p) for p in pts])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(seg):
            bm.faces.new((r0[k], r0[(k + 1) % seg], r1[(k + 1) % seg], r1[k])).material_index = mi
    for rg in ((rings[0][::-1], rings[-1]) if cap else ()):
        if profile[0][0] > 1e-4 or rg is rings[-1]:
            try:
                bm.faces.new(rg).material_index = mi
            except ValueError:
                pass
    return rings


def displace(verts, amt, scale=3.0, seed=0):
    off = Vector((seed * 13.1, seed * 7.7, seed * 3.3))
    for v in verts:
        v.co += v.normal * noise.noise(v.co * scale + off) * amt


def links(bm, a, b, mi=0, w=0.07, r=0.018, gap=0.0):
    """chain links from point a to point b, each an oval loop turned 90 degrees from the last"""
    a, b = Vector(a), Vector(b)
    d = b - a
    L = d.length
    n = max(1, round(L / (w * 2.2)))
    step = L / n
    dn = d.normalized()
    side = dn.cross(Vector((0, 0, 1)))
    if side.length < 1e-3:
        side = dn.cross(Vector((1, 0, 0)))
    side.normalize()
    up = side.cross(dn)
    for k in range(n):
        c = a + dn * (step * (k + 0.5))
        s = side if k % 2 == 0 else up
        pts = [c + dn * (math.sin(t) * step * 0.62) + s * (math.cos(t) * w * 0.55) for t in (j * 2 * math.pi / 14 for j in range(14))]
        tube(bm, pts, r, mi, sides=5, closed=True)


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
        for m in set(o.data.materials):
            n = m.node_tree.nodes.get("bake") or node(m, "ShaderNodeTexImage")
            n.name = "bake"
            n.image = img
            m.node_tree.nodes.active = n
        if kind == "DIFFUSE":                     # metal has no diffuse colour, so it'd bake black: bake it as paint
            kept = []
            for m in set(o.data.materials):
                for b in (n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"):
                    mi = b.inputs["Metallic"]
                    kept.append((m, mi, mi.default_value, [l.from_socket for l in mi.links]))
                    for l in list(mi.links):
                        m.node_tree.links.remove(l)
                    mi.default_value = 0.0
            bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, margin=4)
            for m, mi, v, src in kept:
                mi.default_value = v
                for f in src:
                    m.node_tree.links.new(f, mi)
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
    for m in set(o.data.materials):
        m.node_tree.nodes.remove(m.node_tree.nodes["bake"])
    return out


def write_obj(o, glow=(), tag="gate prop"):
    """into block space for the OBJ loader (x, z up, -y), one group per material; materials in `glow` full-bright"""
    path = os.path.join(ASSETS, "models", "mesh", o.name + ".obj")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    me = o.data
    me.calc_loop_triangles()
    uv = me.uv_layers.active.data
    lines = ["mtllib %s.mtl" % o.name, "# Ashbound %s (tools/blender); block space" % tag]
    for v in me.vertices:
        lines.append("v %.5f %.5f %.5f" % (v.co.x, v.co.z, -v.co.y))
    uvs, nrm, faces_by = {}, {}, {}
    for t in me.loop_triangles:
        faces_by.setdefault(t.material_index, []).append(t)
    vt, vn, body_ = [], [], []
    for mi, tris in faces_by.items():
        lit = me.materials[mi] in glow
        body_.append("g %s" % ("fire" if lit else "part%d" % mi))
        body_.append("usemtl %s" % ("glow" if lit else "prop"))
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


def run(make, glow=(), out="gate_props"):
    """make: [(builder, texture size)]. Builds, bakes and writes each (or only the ones named on the command line),
    then with `preview` renders them in a row on a stone floor with the baked textures -> tools/renders/OUT.png"""
    done = []
    for fn, size in make:
        if ONLY and fn.__name__ not in ONLY:
            continue
        o = fn()
        img = bake(o, size)
        write_obj(o, glow)
        done.append((o, img))
    if PREVIEW:
        lineup(done, out)
    return done


def lineup(done, out, per_row=None):
    """the props in rows on a dark floor, seen from their fronts (+y) a little above, as a player meets them"""
    per_row = per_row or max(6, math.ceil(math.sqrt(len(done) * 2.2)))
    rows = (len(done) + per_row - 1) // per_row
    for i, (o, img) in enumerate(done):
        lit = any(m in GLOWS for m in o.data.materials)
        m = bpy.data.materials.new(o.name + "_baked")
        m.use_nodes = True
        b = bsdf(m)
        b.inputs["Roughness"].default_value = 0.7
        t = node(m, "ShaderNodeTexImage")
        t.image = img
        t.interpolation = "Closest"
        link(m, t.outputs["Color"], b.inputs["Base Color"])
        if lit:
            link(m, t.outputs["Color"], b.inputs["Emission Color"])
            b.inputs["Emission Strength"].default_value = 1.2
        o.data.materials.clear()
        o.data.materials.append(m)
        r, c = divmod(i, per_row)
        o.location = (c * 1.7 - 0.5, -(rows - 1 - r) * 2.2 + 0.5, LIFT.get(o.name, 0.0))
    span = (min(per_row, len(done)) - 1) * 1.7
    cx = span / 2
    fl = bpy.data.meshes.new("floor")
    bmf = bmesh.new()
    bmesh.ops.create_grid(bmf, x_segments=1, y_segments=1, size=span + 8, matrix=Matrix.Translation((cx, -2, 0)))
    bmf.to_mesh(fl)
    fo = bpy.data.objects.new("floor", fl)
    sc.collection.objects.link(fo)
    fl.materials.append(mat("floorstone", (0.09, 0.085, 0.08), 0.8))
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.03, 0.032, 0.04, 1)
    tgt = Vector((cx, -(rows - 1) * 1.1, 0.5))
    for loc, en, col in (((cx - 5, 6, 6), 1400, (1.0, 0.84, 0.66)), ((cx + 6, 4, 4), 600, (0.62, 0.74, 1.0)), ((cx, -8, 5), 500, (0.85, 0.85, 1.0))):
        ld = bpy.data.lights.new("l", "AREA")
        ld.energy, ld.color, ld.size = en, col, 6
        lo = bpy.data.objects.new("l", ld)
        lo.location = loc
        lo.rotation_euler = (tgt - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(lo)
    cd = bpy.data.cameras.new("cam")
    cd.lens = 42
    co = bpy.data.objects.new("cam", cd)
    dist = max(span * 0.95 + 2.5, rows * 2.6 + 2.0)
    co.location = (cx, tgt.y + dist, dist * 0.55)
    co.rotation_euler = (tgt - Vector(co.location)).to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(co)
    sc.camera = co
    sc.render.resolution_x, sc.render.resolution_y = 1800, 1000 if rows > 1 else 700
    sc.cycles.samples = 32 if FAST else 128
    sc.view_settings.view_transform = "AgX"
    sc.render.filepath = os.path.join(RENDERS, out + ".png")
    bpy.ops.render.render(write_still=True)
    print("rendered", sc.render.filepath)


GLOWS = set()   # materials drawn full-bright (lamps' flames), set by the gate's script
LIFT = {}       # prop name -> height it is shown at in the lineup (hanging lamps)
