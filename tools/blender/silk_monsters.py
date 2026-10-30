"""The Silk Archive's monsters (Cycles concepts), each sculpted on Epic Fight's own skeleton and posed with one of
Epic Fight's animations (efrig.py), so what you see is what the game can play. Sets and materials from
silk_rooms.py / silk_nest.py.
  blender -b -P tools/blender/silk_monsters.py -- <monster> <shot> [fast]  ->  tools/renders/dungeon/<monster>_<shot>.png
monsters: scholar (the Bound Scholar, greatsword_slam windup)"""
import os, sys, math
import bpy, bmesh
from mathutils import Vector, Matrix, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import efrig
import monster_tex as T

g = globals()
_ns = {"__name__": "silk_lib2", "__file__": os.path.join(HERE, "silk_rooms.py")}
exec(open(os.path.join(HERE, "silk_rooms.py"), encoding="utf-8").read(), _ns)
for k_, v_ in list(_ns.items()):
    if not k_.startswith("__") and k_ not in ("g", "_ns", "HERE"):
        g[k_] = v_
MON = ARGS[0] if ARGS else "scholar"
SHOT = ARGS[1] if len(ARGS) > 1 else "hero"
_ns["_ns"]["SHOT"] = SHOT    # render() lives in silk_nest's namespace
BIPED = efrig.Armature("biped")
# the bones the biped's skin follows; the shin and the head run further than Epic Fight's stubs
BODY = ["Root", "Torso", "Chest", "Head", "Shoulder_R", "Arm_R", "Hand_R", "Shoulder_L", "Arm_L", "Hand_L",
        "Thigh_R", "Leg_R", "Thigh_L", "Leg_L"]
SEGS = {"Leg_R": (Vector((0.125, 0, 0.386)), Vector((0.125, 0.03, 0.02))),
        "Leg_L": (Vector((-0.125, 0, 0.386)), Vector((-0.125, 0.03, 0.02))),
        "Head": (Vector((0, 0, 1.514)), Vector((0, 0.05, 1.85)))}


# ---------------------------------------------------------------- materials
def skin_mat(name, base, ink=(0.004, 0.004, 0.006)):
    """dead skin with a little subsurface, blotched, ink veins under it; the 'ink' attribute blackens it (hands)"""
    m, b = mat(name, base, 0.42, **{"Subsurface Weight": 0.12, "Subsurface Scale": 0.03, "Coat Weight": 0.15})
    nt = m.node_tree
    L = nt.links.new
    tc = node(m, "ShaderNodeTexCoord")
    ns = node(m, "ShaderNodeTexNoise")
    ns.inputs["Scale"].default_value = 9.0
    ns.inputs["Detail"].default_value = 6.0
    L(tc.outputs["Object"], ns.inputs["Vector"])
    blot = node(m, "ShaderNodeMix")
    blot.data_type = "RGBA"
    blot.inputs["A"].default_value = (*base, 1)
    blot.inputs["B"].default_value = (base[0] * 0.55, base[1] * 0.6, base[2] * 0.72, 1)
    L(ns.outputs["Fac"], blot.inputs["Factor"])
    vo = node(m, "ShaderNodeTexVoronoi")
    vo.feature = "DISTANCE_TO_EDGE"
    vo.inputs["Scale"].default_value = 5.0
    L(tc.outputs["Object"], vo.inputs["Vector"])
    vr = node(m, "ShaderNodeMapRange")
    vr.inputs["From Min"].default_value = 0.0
    vr.inputs["From Max"].default_value = 0.012
    vr.inputs["To Min"].default_value = 0.0
    vr.inputs["To Max"].default_value = 0.0
    L(vo.outputs["Distance"], vr.inputs["Value"])
    vein = node(m, "ShaderNodeMix")
    vein.data_type = "RGBA"
    vein.inputs["B"].default_value = (*ink, 1)
    L(vr.outputs["Result"], vein.inputs["Factor"])
    L(blot.outputs["Result"], vein.inputs["A"])
    at = node(m, "ShaderNodeAttribute")
    at.attribute_name = "ink"
    stain = node(m, "ShaderNodeMix")
    stain.data_type = "RGBA"
    stain.inputs["B"].default_value = (*ink, 1)
    L(at.outputs["Fac"], stain.inputs["Factor"])
    L(vein.outputs["Result"], stain.inputs["A"])
    L(stain.outputs["Result"], b.inputs["Base Color"])
    rr = node(m, "ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = 0.42
    rr.inputs["To Max"].default_value = 0.12
    L(at.outputs["Fac"], rr.inputs["Value"])
    L(rr.outputs["Result"], b.inputs["Roughness"])
    bp = node(m, "ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.35
    bp.inputs["Distance"].default_value = 0.004
    pores = node(m, "ShaderNodeTexNoise")
    pores.inputs["Scale"].default_value = 120.0
    L(tc.outputs["Object"], pores.inputs["Vector"])
    add = node(m, "ShaderNodeMath")
    add.operation = "ADD"
    L(pores.outputs["Fac"], add.inputs[0])
    L(vr.outputs["Result"], add.inputs[1])
    L(add.outputs["Value"], bp.inputs["Height"])
    L(bp.outputs["Normal"], b.inputs["Normal"])
    return m


SKIN = T.skin("scholar_skin")
SILK = T.silk("old_silk")
SHELL = SILK
ROBE = T.cloth("robe")
IRON = T.iron("iron")
TOMEHIDE = T.leather("tomehide")
STRAP = T.leather("strap", base=(0.04, 0.025, 0.015))
TEETH = T.teeth("teeth")
GUM, _ = mat("gum", (0.04, 0.01, 0.012), 0.3, **{"Coat Weight": 0.6})
LENS = T.glow_glass("lens")
BACKLEG = T.chitin("backleg")


# ---------------------------------------------------------------- building helpers
FIELD = 1 / 0.575    # a metaball's surface sits at ~0.575 of its radius (stiffness 2, threshold 0.6)


def flesh(name, parts, mats, res=0.011):
    """one smooth body from metaball parts: ("b", c, r) ball, ("e", c, (rx, ry, rz), rot) ellipsoid,
    ("c", a, b, r) capsule, ("-", c, r) carved out; sizes are where the surface ends up"""
    mb = bpy.data.metaballs.new(name)
    mb.resolution = mb.render_resolution = res
    o = bpy.data.objects.new(name, mb)
    sc.collection.objects.link(o)
    for p in parts:
        k = p[0]
        if k in ("b", "-"):
            e = mb.elements.new(type="BALL")
            e.co = p[1]
            e.radius = p[2] * FIELD
            e.use_negative = k == "-"
        elif k == "e":
            e = mb.elements.new(type="ELLIPSOID")
            e.co = p[1]
            e.radius = FIELD
            e.size_x, e.size_y, e.size_z = p[2]
            if len(p) > 3 and p[3] is not None:
                e.rotation = p[3]
        elif k == "c":
            a, b = Vector(p[1]), Vector(p[2])
            e = mb.elements.new(type="CAPSULE")
            e.co = (a + b) / 2
            e.radius = p[3] * FIELD
            e.size_x = (b - a).length / 2
            e.rotation = (b - a).to_track_quat("X", "Z")
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    bpy.data.objects.remove(o)
    me.name = name
    for m in mats:
        me.materials.append(m)
    for pl in me.polygons:
        pl.use_smooth = True
    out = bpy.data.objects.new(name, me)
    sc.collection.objects.link(out)
    return out


def bumpy(o, amt, scale, seed=0):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    displace(bm, amt, scale, seed)
    bm.to_mesh(o.data)
    bm.free()


def rest(o):
    """remember where every vertex sat before posing: the textures are pinned to that"""
    a = o.data.attributes.new("rest", "FLOAT_VECTOR", "POINT")
    a.data.foreach_set("vector", [c for v in o.data.vertices for c in v.co])


def carry(o, joints, pose, segs=SEGS, power=6.0):
    """skin a bind-pose mesh onto the pose, weighted to the nearest of these joints (or rigid to one)"""
    rest(o)
    if isinstance(joints, str):
        efrig.rigid(o, BIPED, pose, joints)
        return None
    ws = efrig.auto_weights([v.co for v in o.data.vertices], BIPED, joints, power=power, segs=segs)
    efrig.skin(o, BIPED, pose, ws)
    return ws


def carried_threads(name, lines, pose, joints, r, m):
    out = []
    for ln in lines:
        if isinstance(joints, str):
            sk = pose[joints] @ BIPED.bind[joints].inverted()
            out.append([tuple(sk @ Vector(p)) for p in ln])
        else:
            ws = efrig.auto_weights([Vector(p) for p in ln], BIPED, joints, segs=SEGS)
            out.append([tuple(p) for p in efrig.skin_points(ln, BIPED, pose, ws)])
    threads(name, out, r=r, m=m)


def lathe(bm, prof, seg=40, mi=0, rim=None):
    """a surface of revolution about z: prof = [(z, r), ...]; rim(theta, i) -> (dr, dz) bends each ring"""
    rings = []
    for i, (z, r) in enumerate(prof):
        ring = []
        for j in range(seg):
            th = j / seg * 2 * math.pi
            dr, dz = rim(th, i) if rim else (0, 0)
            ring.append(bm.verts.new((math.cos(th) * (r + dr), math.sin(th) * (r + dr) * 0.8, z + dz)))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for j in range(seg):
            bm.faces.new((a[j], a[(j + 1) % seg], b[(j + 1) % seg], b[j])).material_index = mi


def chitin_leg(bm, pts, r0, rnd_spines=6):
    """a jointed spider leg through pts, tapering from r0, spines raked toward the tip, a knob at every joint"""
    n = len(pts) - 1
    for i in range(n):
        a, b = Vector(pts[i]), Vector(pts[i + 1])
        ra, rb = r0 * (1 - i / n * 0.75), r0 * (1 - (i + 1) / n * 0.75) * (0.3 if i == n - 1 else 1)
        limb(bm, a, b, ra, rb, seg=12)
        ellipsoid(bm, (a + b) / 2, (ra * 1.15, ra * 1.15, (b - a).length * 0.32),
                  rot=(b - a).to_track_quat("Z", "Y").to_matrix(), seg=12)
        d = (b - a).normalized()
        for k in range(rnd_spines):
            t = (k + 0.5) / rnd_spines
            p = a.lerp(b, t)
            side = d.cross(Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)))).normalized()
            limb(bm, p + side * ra * 0.8, p + side * ra * rnd.uniform(1.8, 3.0) + d * ra * 1.5, ra * 0.16, 0.001, seg=4)
        if i:
            ellipsoid(bm, a, (ra * 1.25,) * 3, seg=12)


# ---------------------------------------------------------------- the Bound Scholar
def scholar(pose, S=1.45):
    """a big man cocooned to the waist, spider legs burst from his back, swinging an iron-bound tome on a chain"""
    made = []
    # ---- the body, sculpted round the biped's bind pose (it faces +y)
    P = []
    P += [("e", (0, -0.01, 0.82), (0.22, 0.16, 0.13), None),                 # pelvis
          ("e", (0, 0.0, 0.98), (0.24, 0.18, 0.16), None),                   # belly
          ("e", (0, 0.01, 1.2), (0.33, 0.22, 0.19), None),                   # ribcage, barrel
          ("e", (0, -0.06, 1.24), (0.34, 0.15, 0.22), None)]                 # the back, broad
    for s in (-1, 1):
        P += [("e", (0.13 * s, 0.11, 1.28), (0.15, 0.08, 0.1), Quaternion((0, 1, 0), 0.25 * s)),   # pecs
              ("e", (0.2 * s, -0.02, 1.45), (0.2, 0.13, 0.08), Quaternion((0, 1, 0), -0.35 * s)),  # traps
              ("e", (0.25 * s, -0.08, 1.14), (0.1, 0.1, 0.2), None),                              # lats
              ("e", (0.4 * s, 0.0, 1.37), (0.15, 0.14, 0.14), None),                              # shoulder
              ("c", (0.4 * s, 0.0, 1.32), (0.4 * s, 0.0, 1.12), 0.105),                           # upper arm
              ("e", (0.4 * s, 0.05, 1.22), (0.075, 0.07, 0.1), None),                             # biceps
              ("e", (0.41 * s, -0.04, 1.24), (0.07, 0.065, 0.11), None),                          # triceps
              ("c", (0.4 * s, 0.0, 1.06), (0.4 * s, -0.01, 0.86), 0.09),                          # forearm
              ("e", (0.4 * s, 0.0, 1.02), (0.11, 0.1, 0.08), None),                               # forearm bulk
              ("e", (0.4 * s, -0.03, 0.77), (0.075, 0.085, 0.1), None),                           # fist
              ("e", (0.4 * s, 0.03, 0.72), (0.065, 0.06, 0.05), None)]                            # knuckles
    P += [("c", (0, 0.02, 1.47), (0, 0.06, 1.58), 0.095),                    # neck, thick
          ("e", (0, 0.08, 1.67), (0.12, 0.13, 0.14), None),                  # cranium, small for the body
          ("e", (0, 0.15, 1.6), (0.09, 0.07, 0.07), None),                   # jaw
          ("e", (0, 0.17, 1.7), (0.1, 0.04, 0.025), None)]                   # brow ridge
    for s in (-1, 1):
        P += [("-", (0.045 * s, 0.215, 1.67), 0.028)]                        # eye sockets
    body = flesh("scholar_body", P, [SKIN])
    bumpy(body, 0.006, 22, 3)
    ws = efrig.auto_weights([v.co for v in body.data.vertices], BIPED, BODY, segs=SEGS)
    # the hands and forearms ink-black, fading up to the elbow
    at = body.data.attributes.new("ink", "FLOAT", "POINT")
    for i, w in enumerate(ws):
        z = body.data.vertices[i].co.z
        at.data[i].value = max(0.0, min(1.0, (1.02 - z) / 0.16)) if abs(body.data.vertices[i].co.x) > 0.3 else 0.0
    rest(body)
    efrig.skin(body, BIPED, pose, ws)
    made.append(body)

    # ---- the scholar's gown over his torso, sleeves torn off at the shoulder, folds hanging from the chest
    RP = [p_ for p_ in P[:4]] + [("e", (0.2 * s, -0.02, 1.43), (0.21, 0.14, 0.09), Quaternion((0, 1, 0), -0.35 * s))
                                for s in (-1, 1)] + [("e", (0.39 * s, 0.0, 1.36), (0.16, 0.15, 0.15), None) for s in (-1, 1)]
    RP = [(k[0], k[1], tuple(r * 1.07 for r in k[2]), k[3]) for k in RP]
    robe = flesh("scholar_robe", RP, [ROBE], res=0.014)
    from mathutils import noise as _nz
    rbm = bmesh.new()
    rbm.from_mesh(robe.data)
    kill = []
    for v in rbm.verts:
        c = v.co
        n_ = _nz.noise(c * 9.0) * 0.05
        if (c.z > 1.47 + n_ and abs(c.x) < 0.2) or c.z < 0.9 + n_ * 2 or (abs(c.x) > 0.43 + n_ and c.z < 1.36) \
                or (c.y > 0.05 and abs(c.x) < 0.07 + n_ + max(0.0, c.z - 1.0) * 0.25):   # open down the front
            kill.append(v)
    bmesh.ops.delete(rbm, geom=kill, context="VERTS")
    rbm.normal_update()
    for v in rbm.verts:
        a_ = math.atan2(v.co.y, v.co.x)
        hang = max(0.0, min(1.0, (1.35 - v.co.z) / 0.35))
        v.co += v.normal * (0.012 * math.sin(a_ * 22 + _nz.noise(v.co * 4) * 3) * hang + 0.045)
    rbm.to_mesh(robe.data)
    rbm.free()
    robe.modifiers.new("solid", "SOLIDIFY").thickness = 0.008
    carry(robe, BODY, pose)
    made.append(robe)

    # ---- the legs, wound tight in silk
    LP = []
    for s in (-1, 1):
        LP += [("c", (0.13 * s, 0.0, 0.78), (0.13 * s, 0.02, 0.42), 0.13),
               ("c", (0.13 * s, 0.02, 0.4), (0.13 * s, 0.0, 0.1), 0.095),
               ("e", (0.13 * s, 0.07, 0.05), (0.075, 0.15, 0.055), None)]
    legs = flesh("scholar_legs", LP, [SILK])
    bumpy(legs, 0.012, 14, 5)
    made.append(legs)
    lines = []
    for s in (-1, 1):
        wrap_loops(Vector((0.13 * s, 0.01, 0.6)), Matrix.Identity(3), (0.135, 0.13, 0.2), 26, lines)
        wrap_loops(Vector((0.13 * s, 0.01, 0.25)), Matrix.Identity(3), (0.1, 0.1, 0.17), 22, lines)
    carry(legs, BODY, pose)
    carried_threads("leg_wraps", lines, pose, BODY, 0.004, LOOSE)

    # ---- the cocoon he burst out of the top of: a torn shell round the hips, petals curling out
    bm = bmesh.new()
    from mathutils import noise as _nz

    def rim(th, i):
        if i < 4:
            return (0, 0)
        k = (i - 3) / 3
        n_ = _nz.noise(Vector((math.cos(th) * 2.2, math.sin(th) * 2.2, 0.7)))
        return (k * 0.035 * (1 + n_), -k * 0.02 + n_ * k * 0.16)
    lathe(bm, [(0.42, 0.2), (0.52, 0.235), (0.64, 0.26), (0.76, 0.255), (0.86, 0.245), (0.93, 0.25), (0.98, 0.265)],
          seg=64, rim=rim)
    displace(bm, 0.008, 9, 9)
    shell = obj("scholar_shell", bm, [SHELL], smooth=True)
    bpy.context.view_layer.objects.active = shell
    so = shell.modifiers.new("solid", "SOLIDIFY")
    so.thickness = 0.012
    carry(shell, ["Root", "Torso", "Thigh_R", "Thigh_L"], pose)
    made.append(shell)
    # strands from the torn shell down to the floor behind him
    lines = []
    for i in range(14):
        th = rnd.uniform(0, 2 * math.pi)
        a = Vector((math.cos(th) * 0.3, math.sin(th) * 0.24, rnd.uniform(0.55, 0.95)))
        lines.append([tuple(a.lerp(Vector((a.x * 2.2, a.y * 2.2 - 0.3, 0.0)), t / 6)) for t in range(7)])
    carried_threads("shell_strands", lines, pose, ["Root", "Thigh_R", "Thigh_L"], 0.005, LOOSE)

    # ---- the head: wrapped in silk to the lip, the jaw bare, iron spectacles bolted on
    bm = bmesh.new()
    ellipsoid(bm, Vector((0, 0.085, 1.69)), (0.135, 0.145, 0.15), seg=28)
    for v in [v for v in bm.verts if v.co.z < 1.64 - (v.co.y - 0.1) * 0.6]:
        bm.verts.remove(v)
    displace(bm, 0.008, 18, 11)
    hood = obj("scholar_hood", bm, [SILK], smooth=True)
    hood.modifiers.new("solid", "SOLIDIFY").thickness = 0.006
    hl = []
    wrap_loops(Vector((0, 0.085, 1.71)), Matrix.Identity(3), (0.14, 0.15, 0.12), 30, hl)
    bm = bmesh.new()                       # teeth bared in the torn jaw
    for i in range(14):
        a = math.radians(-55 + i * 110 / 13)
        for up in (0, 1):
            if rnd.random() < 0.15:
                continue
            c = Vector((math.sin(a) * 0.075, 0.12 + math.cos(a) * 0.09, 1.607 - up * 0.034 + rnd.uniform(-0.004, 0.004)))
            h = rnd.uniform(0.018, 0.03) + (0.014 if i in (2, 11) else 0)
            limb(bm, c + Vector((0, 0, 0.012 if up == 0 else -0.012)), c + Vector((rnd.uniform(-0.004, 0.004), 0, -h / 2 if up == 0 else h / 2)),
                 rnd.uniform(0.006, 0.009), 0.002, seg=6)
    teeth = obj("scholar_teeth", bm, [TEETH], smooth=True)
    bm = bmesh.new()
    ellipsoid(bm, Vector((0, 0.15, 1.59)), (0.075, 0.075, 0.03), seg=16)
    gum = obj("scholar_gum", bm, [GUM], smooth=True)
    bm = bmesh.new()
    bml = bmesh.new()
    for s in (-1, 1):
        c = Vector((0.05 * s, 0.235, 1.675))
        q = Matrix.Rotation(math.pi / 2, 4, "X")
        bmesh.ops.create_cone(bm, cap_ends=False, segments=24, radius1=0.036, radius2=0.036, depth=0.012,
                              matrix=Matrix.Translation(c) @ q)
        ret = bmesh.ops.create_circle(bml, cap_ends=True, segments=24, radius=0.033, matrix=Matrix.Translation(c + Vector((0, 0.002, 0))) @ q)
        limb(bm, c + Vector((0.036 * s, 0, 0)), Vector((0.13 * s, 0.1, 1.69)), 0.005, 0.005)       # the arms, into the wraps
        for k in range(3):                                                                         # the bolts
            a = k * 2.1 + 0.4
            ellipsoid(bm, c + Vector((math.cos(a) * 0.045, -0.005, math.sin(a) * 0.045)), (0.008,) * 3, seg=8)
    limb(bm, Vector((-0.016, 0.24, 1.68)), Vector((0.016, 0.24, 1.68)), 0.005, 0.005)
    specs = obj("scholar_specs", bm, [IRON], smooth=True)
    lenses = obj("scholar_lenses", bml, [LENS])
    for o in (hood, teeth, gum, specs, lenses):
        carry(o, "Head", pose)
        made.append(o)
    carried_threads("head_wraps", hl, pose, "Head", 0.003, LOOSE)

    # ---- the high scholar's collar framing the head, and the gown's torn mantle down his back
    bm = bmesh.new()
    rings = []
    for i in range(6):
        t = i / 5
        z = 1.44 + t * 0.26
        r = 0.21 + t * t * 0.13
        ring = []
        for j in range(25):
            th = math.radians(5 - j * 190 / 24)
            ring.append(bm.verts.new((math.cos(th) * r, math.sin(th) * r * 0.9 - 0.06 + t * -0.04, z + (abs(math.cos(th)) * 0.04 * t))))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for j in range(24):
            bm.faces.new((a[j], a[j + 1], b[j + 1], b[j]))
    collar = obj("scholar_collar", bm, [ROBE], smooth=True)
    collar.modifiers.new("solid", "SOLIDIFY").thickness = 0.02
    bm = bmesh.new()
    for j in range(25):                     # an iron rim on the collar's edge
        th0, th1 = math.radians(5 - j * 190 / 24), math.radians(5 - (j + 1) * 190 / 24)
        if j < 24:
            p0 = Vector((math.cos(th0) * 0.34, math.sin(th0) * 0.306 - 0.05, 1.7 + abs(math.cos(th0)) * 0.04))
            p1 = Vector((math.cos(th1) * 0.34, math.sin(th1) * 0.306 - 0.05, 1.7 + abs(math.cos(th1)) * 0.04))
            limb(bm, p0, p1, 0.011, 0.011, seg=6)
            if j % 4 == 2:
                limb(bm, p0, p0 + Vector((p0.x * 0.25, (p0.y + 0.05) * 0.25, 0.1)), 0.012, 0.001, seg=6)  # spikes
    rimo = obj("collar_rim", bm, [IRON], smooth=True)
    for o in (collar, rimo):
        carry(o, "Chest", pose)
        made.append(o)
    bm = bmesh.new()                        # the mantle: from the shoulders down the back, the hem in tatters
    cols, rows = 22, 18
    grid = []
    hems = [0.55 + 0.45 * abs(math.sin(c_ * 1.3 + 2)) * rnd.uniform(0.55, 1.0) for c_ in range(cols + 1)]
    for c_ in range(1, cols, 2):
        hems[c_] = min(hems[c_ - 1], hems[c_ + 1]) * rnd.uniform(0.5, 0.8)   # torn up between the points
    for r_ in range(rows + 1):
        row = []
        for c_ in range(cols + 1):
            t = r_ / rows * hems[c_]
            u = c_ / cols * 2 - 1
            w = 0.36 + t * 0.2
            x = u * w
            y = -0.2 - t * 0.12 - (1 - u * u) * 0.05 + math.sin(u * 9 + t * 3) * 0.02 * t
            z = 1.5 - t * 1.05
            row.append(Vector((x, y, z)))
        grid.append(row)
    vs = [[bm.verts.new(p) for p in row] for row in grid]
    for r_ in range(rows):
        for c_ in range(cols):
            bm.faces.new((vs[r_][c_], vs[r_][c_ + 1], vs[r_ + 1][c_ + 1], vs[r_ + 1][c_]))
    mantle = obj("scholar_mantle", bm, [ROBE], smooth=True)
    mantle.modifiers.new("solid", "SOLIDIFY").thickness = 0.01
    carry(mantle, ["Chest", "Torso", "Root", "Shoulder_R", "Shoulder_L"], pose)
    made.append(mantle)

    # ---- straps across the chest, an iron key ring hanging; manacles at the wrists
    bm = bmesh.new()
    for s in (-1, 1):
        pts = []
        for i in range(33):
            th = i / 32 * 2 * math.pi
            d = Vector((math.cos(th), math.sin(th), 0))
            tilt = Matrix.Rotation(0.55 * s, 3, "Y")
            p = tilt @ Vector((d.x * 0.33, d.y * 0.235, 0)) + Vector((0, 0.005, 1.2))
            pts.append(p)
        for a, b in zip(pts, pts[1:]):
            limb(bm, a, b, 0.016, 0.016, seg=4)
        box(bm, Vector((0.14 * s, 0.22, 1.2 + 0.1 * s)), (0.05, 0.02, 0.05), 0)
    straps = obj("scholar_straps", bm, [STRAP], smooth=True)
    carry(straps, ["Chest", "Torso"], pose)
    made.append(straps)
    bm = bmesh.new()
    for s in (-1, 1):
        bmesh.ops.create_cone(bm, cap_ends=False, segments=20, radius1=0.1, radius2=0.1, depth=0.07,
                              matrix=Matrix.Translation((0.4 * s, -0.005, 0.89)))
        for k in range(4):                                                         # a broken chain hanging off it
            c = Vector((0.4 * s + 0.02 * k * s, 0.06, 0.84 - k * 0.045))
            bmesh.ops.create_cone(bm, cap_ends=False, segments=10, radius1=0.016, radius2=0.016, depth=0.012,
                                  matrix=Matrix.Translation(c) @ Matrix.Rotation(math.pi / 2 * (k % 2), 4, "Z") @ Matrix.Rotation(math.pi / 2, 4, "X"))
    manacles = obj("scholar_manacles", bm, [IRON], smooth=True)
    carry(manacles, ["Hand_R", "Hand_L"], pose)
    made.append(manacles)

    # ---- the spider legs burst out of his back
    bm = bmesh.new()
    bmw = bmesh.new()
    for s in (-1, 1):
        for root, knee, ank, tip, r0 in (
                ((0.11 * s, -0.17, 1.34), (0.5 * s, -0.55, 2.3), (1.0 * s, -0.1, 2.45), (1.25 * s, 0.55, 1.85), 0.085),
                ((0.15 * s, -0.16, 1.17), (0.75 * s, -0.6, 1.75), (1.3 * s, -0.25, 1.35), (1.45 * s, 0.4, 0.6), 0.075)):
            chitin_leg(bm, [root, Vector(root) + Vector((0.1 * s, -0.15, 0.12)), knee, ank, tip], r0)
            ellipsoid(bmw, Vector(root) + Vector((0, 0.03, 0)), (0.075, 0.03, 0.075), seg=14)  # the wound
    legs_b = obj("scholar_backlegs", bm, [BACKLEG], smooth=True)
    wound = obj("scholar_wounds", bmw, [INK], smooth=True)
    for o in (legs_b, wound):
        carry(o, "Chest", pose)
        made.append(o)

    # ---- the tome on its chain, swung from the right fist (the tool joint's -z runs out along the weapon)
    bm = bmesh.new()
    links_n = 9
    for k in range(links_n):
        c = Vector((0, 0, -0.03 - k * 0.05))
        bmesh.ops.create_cone(bm, cap_ends=False, segments=10, radius1=0.02, radius2=0.02, depth=0.014,
                              matrix=Matrix.Translation(Vector((0.375, -0.029, 0.822)) + c) @ Matrix.Rotation(math.pi / 2 * (k % 2), 4, "Z") @ Matrix.Rotation(math.pi / 2, 4, "Y"))
    tc = Vector((0.375, -0.029, 0.822)) + Vector((0, 0, -0.03 - links_n * 0.05 - 0.27))
    W, H, T = 0.4, 0.52, 0.17               # the tome: wide (x), long (along the chain), thick (y)
    bmt = bmesh.new()
    box(bmt, tc, (W, T, H))
    bmp = bmesh.new()
    box(bmp, tc + Vector((0.012, 0, 0)), (W - 0.01, T - 0.04, H - 0.025))
    for sx in (-1, 1):                      # iron corners with spikes, bands over the spine, a boss and a lock
        for sz in (-1, 1):
            cc = tc + Vector((sx * (W / 2 - 0.035), 0, sz * (H / 2 - 0.035)))
            box(bm, cc, (0.08, T + 0.016, 0.08))
            limb(bm, cc + Vector((sx * 0.03, 0, sz * 0.03)), cc + Vector((sx * 0.09, 0, sz * 0.09)), 0.018, 0.001, seg=6)
    for sz in (-0.16, 0.0, 0.16):
        box(bm, tc + Vector((-W / 2 - 0.004, 0, sz)), (0.02, T + 0.02, 0.035))
    for sy in (-1, 1):
        bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=0.08, radius2=0.05, depth=0.03,
                              matrix=Matrix.Translation(tc + Vector((0, sy * (T / 2 + 0.012), 0))) @ Matrix.Rotation(math.pi / 2 * sy, 4, "X"))
        limb(bm, tc + Vector((0, sy * (T / 2 + 0.02), 0)), tc + Vector((0, sy * (T / 2 + 0.09), 0)), 0.025, 0.002, seg=8)
    box(bm, tc + Vector((W / 2 + 0.01, 0, 0)), (0.04, 0.06, 0.09))
    bmesh.ops.create_cone(bm, cap_ends=False, segments=12, radius1=0.035, radius2=0.035, depth=0.016,
                          matrix=Matrix.Translation(tc + Vector((0, 0, H / 2 + 0.03))) @ Matrix.Rotation(math.pi / 2, 4, "Y"))
    chain = obj("tome_iron", bm, [IRON], smooth=True)
    tome = obj("tome", bmt, [TOMEHIDE])
    pages = obj("tome_pages", bmp, [PAGE])
    for o in (chain, tome, pages):
        bev = o.modifiers.new("bev", "BEVEL")
        bev.width = 0.006
        bev.segments = 2
        carry(o, "Tool_R", pose)
        made.append(o)
    for o in bpy.data.objects:
        if o.type == "CURVE" and o.name.startswith(("leg_wraps", "shell_strands", "head_wraps")):
            made.append(o)
    # stood on the floor: the lowest point of the feet at z 0
    low = min((legs.matrix_world @ v.co).z for v in legs.data.vertices)
    for o in made:
        o.matrix_world = Matrix.Scale(S, 4) @ Matrix.Translation((0, 0, -low)) @ o.matrix_world
    return made


# ---------------------------------------------------------------- the set: a corner of the Reading Hall
def reading_corner():
    bm = bmesh.new()
    box(bm, (0, 4, -0.1), (24, 24, 0.2))
    obj("floor", bm, [floor_mat()])
    bm, bm_b = bmesh.new(), bmesh.new()
    shelf_wall(-7.0, -6, 14, 8, 1, bm, bm_b)
    obj("shelves", bm, [WALNUT])
    obj("books", bm_b, LEATHER)
    bm, bm_b = bmesh.new(), bmesh.new()
    for x in (-3.4, 3.6):                    # long reading tables behind him, the readers wrapped in their chairs
        box(bm, (x, 8.0, 0.78), (1.4, 9.0, 0.08))
        for y in (4.0, 12.0):
            box(bm, (x, y, 0.38), (1.2, 0.12, 0.76))
        for y in (5.0, 7.2, 9.4, 11.4):
            for s in (-1, 1):
                cx = x + s * 1.15
                box(bm, (cx, y, 0.45), (0.5, 0.5, 0.06))
                box(bm, (cx + s * 0.25, y, 0.95), (0.06, 0.5, 1.0))
                if rnd.random() < 0.8:
                    cocoon(Vector((cx + s * 0.05, y, 1.0)), length=1.15, tilt=Matrix.Rotation(-s * 0.25, 3, "Y"))
    obj("tables", bm, [WALNUT])
    threads("wraps", WRAPS, r=0.007, m=LOOSE)
    WRAPS.clear()
    sheet("canopy1", Vector((-7, 2, 7)), Vector((-7, 13, 7.5)), Vector((-2.4, 2, 3.4)), Vector((-2.6, 13, 3.6)),
          droop=1.0, m=CANOPY)
    sheet("canopy2", Vector((7, 2, 7)), Vector((7, 13, 7)), Vector((3.0, 2, 3.0)), Vector((3.2, 13, 3.2)),
          droop=1.0, m=CANOPY)
    bm = bmesh.new()                         # ink spilt round his feet, papers
    for _ in range(9):
        c = Vector((rnd.uniform(-1.6, 1.6), rnd.uniform(-1.0, 2.0), 0.002))
        ellipsoid(bm, c, (rnd.uniform(0.2, 0.6), rnd.uniform(0.2, 0.5), 0.004), seg=16)
    obj("ink_spill", bm, [INK], smooth=True)
    bm = bmesh.new()
    for _ in range(40):
        c = Vector((rnd.uniform(-3, 3), rnd.uniform(-2, 6), 0.005))
        box(bm, c, (0.21, 0.3, 0.004), rnd.uniform(0, 6.28))
    obj("papers", bm, [PAGE])
    moon_sun((0.55, 0.75, -0.55), 4.0)       # the moon from behind him: rim light
    chandelier(Vector((0, 8, 7.0)), rad=1.6, top=Vector((0, 8, 9.5)))
    fog_box((-8, -6, 0), (8, 16, 9), 0.012)
    for loc, en, col, size in (((2.6, -3.0, 1.2), 140, (0.55, 0.7, 1.0), 2.5),     # a cold key from the lamp, low
                               ((-3.0, 1.0, 5.0), 110, (0.5, 0.62, 0.95), 3.0)):    # top fill
        ld = bpy.data.lights.new("key", "AREA")
        ld.energy = en
        ld.size = size
        ld.color = col
        lo = bpy.data.objects.new("key", ld)
        lo.location = loc
        lo.rotation_euler = (Vector((0, 0.3, 1.8)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(lo)


def studio():
    bm = bmesh.new()
    box(bm, (0, 0, -0.1), (30, 30, 0.2))
    obj("floor", bm, [mat("studio_floor", (0.05, 0.05, 0.055), 0.6)[0]])
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.022, 0.03, 1)
    for loc, en, col, size in (((3.0, -4.0, 4.0), 900, (1.0, 0.96, 0.9), 3.0),
                               ((-4.0, -2.0, 2.5), 250, (0.6, 0.7, 1.0), 4.0),
                               ((0.5, 4.0, 4.5), 1200, (0.6, 0.75, 1.0), 2.0)):
        ld = bpy.data.lights.new("l", "AREA")
        ld.energy = en
        ld.size = size
        ld.color = col
        lo = bpy.data.objects.new("l", ld)
        lo.location = loc
        lo.rotation_euler = (Vector((0, 0, 1.6)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(lo)


POSES = {"scholar": ("biped/living/hold_greatsword", 0.0)}
SHOTS = {
    "scholar": {
        "hero": ((2.6, -5.4, 1.3), (0.0, 0.3, 1.75), 30),
        "front": ((0.0, -6.0, 1.6), (0.0, 0.0, 1.6), 35),
        "side": ((6.0, 0.0, 1.6), (0.0, 0.0, 1.6), 35),
        "face": ((0.9, -1.7, 2.3), (0.0, 0.3, 2.3), 45),
    },
}

if __name__ == "__main__":
    anim, t = POSES[MON]
    pose = BIPED.pose(anim, float(ARGS[2]) if len(ARGS) > 2 and ARGS[2] != "fast" else t)
    # he faces the camera: turn the whole figure (built facing +y) to face -y
    made = {"scholar": scholar}[MON](pose)
    # turned to face the camera (-y): the way his face looks, measured from the spectacles to the middle of the head
    def centre(name):
        o = bpy.data.objects[name]
        return sum((o.matrix_world @ v.co for v in o.data.vertices), Vector()) / len(o.data.vertices)
    f = centre("scholar_lenses") - centre("scholar_hood")
    turn = Matrix.Rotation(-math.pi / 2 - math.atan2(f.y, f.x) + math.radians(float(os.environ.get("YAW", "25"))), 4, "Z")
    for o in made:
        o.matrix_world = turn @ o.matrix_world
    hp = centre("scholar_lenses")
    SHOTS[MON]["face"] = (tuple(hp + Vector((0.7, -1.5, 0.05))), tuple(hp + Vector((0, 0, -0.15))), 50)
    SHOTS[MON]["bust"] = (tuple(hp + Vector((1.3, -3.0, -0.5))), tuple(hp + Vector((0, 0, -0.55))), 40)
    if "studio" in ARGS:
        studio()
    else:
        reading_corner()
    render(SHOTS[MON], MON + ("_studio" if "studio" in ARGS else ""))
