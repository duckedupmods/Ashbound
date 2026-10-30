"""The Silk Archive's rooms on the way to the Great Index (Cycles concepts, the same nest look as silk_nest.py, whose
materials and helpers this borrows).
  blender -b -P tools/blender/silk_rooms.py -- <room> <shot> [fast]   ->  tools/renders/dungeon/<room>_<shot>.png
rooms: lobby (cocooned visitors still queueing at the desk, the turnstile into the stacks)"""
import os, sys, math
import bpy, bmesh
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
g = globals()
_ns = {"__name__": "silk_lib", "__file__": os.path.join(HERE, "silk_nest.py")}
exec(open(os.path.join(HERE, "silk_nest.py"), encoding="utf-8").read(), _ns)
for k_, v_ in _ns.items():
    if not k_.startswith("__"):
        g[k_] = v_

ROOM = ARGS[0] if ARGS else "lobby"
SHOT = ARGS[1] if len(ARGS) > 1 else "hero"
_ns["SHOT"] = SHOT


def stone_mat():
    """the archive's sage ashlar: big dressed blocks, fine joints"""
    m, b = mat("ashlar", (0.2, 0.22, 0.21), 0.75)
    tc = node(m, "ShaderNodeTexCoord")
    mp = node(m, "ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (math.pi / 2, 0, 0)
    br = node(m, "ShaderNodeTexBrick")
    br.inputs["Scale"].default_value = 1.6
    br.inputs["Mortar Size"].default_value = 0.008
    br.inputs["Brick Width"].default_value = 1.2
    br.inputs["Row Height"].default_value = 0.5
    br.inputs["Color1"].default_value = (0.2, 0.23, 0.22, 1)
    br.inputs["Color2"].default_value = (0.15, 0.17, 0.16, 1)
    br.inputs["Mortar"].default_value = (0.05, 0.055, 0.05, 1)
    links(m).new(tc.outputs["Object"], mp.inputs[0])
    links(m).new(mp.outputs[0], br.inputs[0])
    nz = node(m, "ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    nz.inputs["Detail"].default_value = 8.0
    mx = node(m, "ShaderNodeMix")
    mx.data_type = "RGBA"
    mx.blend_type = "MULTIPLY"
    mx.inputs[0].default_value = 0.6
    links(m).new(br.outputs[0], mx.inputs[6])
    links(m).new(nz.outputs[1], mx.inputs[7])
    links(m).new(mx.outputs[2], b.inputs["Base Color"])
    bump = node(m, "ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.5
    links(m).new(br.outputs["Fac"], bump.inputs["Height"])
    links(m).new(bump.outputs[0], b.inputs["Normal"])
    return m


STONE = stone_mat()
CANOPY = silk_mat("canopy", holes=0.4, translucent=0.85, gauze=0.7)


def shelf_wall(x, y0, y1, z1, face, bm, bm_b):
    """a flat wall of bookcases at x, from y0 to y1, up to z1; face = +1 or -1 (which way the books look)"""
    yaw = math.pi / 2 if face > 0 else -math.pi / 2
    n = int((y1 - y0) / 2.4)
    for b_ in range(n + 1):
        box(bm, (x, y0 + b_ * (y1 - y0) / n, z1 / 2), (0.6, 0.35, z1), 0)
    for row in range(int(z1)):
        z = row
        box(bm, (x, (y0 + y1) / 2, z + 0.04), (0.55, y1 - y0, 0.08), 0)
        y = y0 + 0.2
        while y < y1 - 0.2:
            w = rnd.uniform(0.05, 0.13)
            h = rnd.uniform(0.55, 0.86)
            box(bm_b, (x + face * 0.02, y + w / 2, z + 0.08 + h / 2), (0.36, w, h), 0, mi=rnd.randrange(len(LEATHER)))
            y += w + (0.01 if rnd.random() > 0.05 else rnd.uniform(0.1, 0.4))
    box(bm, (x - face * 0.3, (y0 + y1) / 2, z1 / 2), (0.1, y1 - y0, z1), 0)


def vault(x0, x1, y0, y1, spring, apex, mats, ribs=3.0):
    """a pointed barrel vault from spring to apex over x0..x1, with transverse ribs every `ribs`"""
    bm = bmesh.new()
    w = (x1 - x0) / 2
    cx = (x0 + x1) / 2
    prof = []
    for i in range(17):
        t = i / 16
        # two arcs meeting at a point: each centred on the far springer line (an equilateral-ish pointed arch)
        side = -1 if t < 0.5 else 1
        u = (t if t < 0.5 else 1 - t) * 2                 # 0 at the springer, 1 at the apex
        ang = u * math.acos(max(-1.0, min(1.0, (w * 2 - w) / (w * 2))))
        r = w * 2
        px = cx + side * (r * math.cos(ang) - w)
        pz = spring + (apex - spring) * math.sin(ang) / math.sin(math.acos(0.5))
        prof.append((px, pz))
    rows = []
    n = int((y1 - y0) / 0.5)
    for j in range(n + 1):
        y = y0 + (y1 - y0) * j / n
        rows.append([bm.verts.new((px, y, pz)) for px, pz in prof])
    for j in range(n):
        for i in range(16):
            bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
    obj("vault", bm, [mats[0]], smooth=True)
    bm = bmesh.new()
    y = y0
    while y <= y1 + 1e-3:
        for (ax, az), (bx, bz) in zip(prof, prof[1:]):
            limb(bm, (ax, y, az - 0.15), (bx, y, bz - 0.15), 0.22, 0.22, seg=6)
        y += ribs
    obj("vault_ribs", bm, [mats[1]])
    return prof


def chandelier(c, rad=2.0, drop=4.0, top=None):
    bm = bmesh.new()
    n = 16
    for i in range(n):
        a0, a1 = i / n * 2 * math.pi, (i + 1) / n * 2 * math.pi
        limb(bm, c + Vector((math.cos(a0) * rad, math.sin(a0) * rad, 0)), c + Vector((math.cos(a1) * rad, math.sin(a1) * rad, 0)), 0.07, 0.07, seg=6)
    for i in range(4):
        a = i / 4 * 2 * math.pi
        limb(bm, c + Vector((math.cos(a) * rad, math.sin(a) * rad, 0)), c + Vector((0, 0, 1.6)), 0.04, 0.04, seg=5)
    limb(bm, c + Vector((0, 0, 1.6)), top or c + Vector((0, 0, drop)), 0.05, 0.05, seg=5)
    obj("chandelier", bm, [PEWTER])
    for i in range(8):
        a = (i + 0.5) / 8 * 2 * math.pi
        p = c + Vector((math.cos(a) * rad, math.sin(a) * rad, 0.25))
        bm = bmesh.new()
        box(bm, p, (0.2, 0.2, 0.32), a)
        obj("chand_glass", bm, [LAMPGLASS])
        ld = bpy.data.lights.new("chand", "POINT")
        ld.energy = 60
        ld.color = (0.55, 0.72, 1.0)
        ld.shadow_soft_size = 0.15
        lo = bpy.data.objects.new("chand", ld)
        lo.location = p - Vector((0, 0, 0.3))
        sc.collection.objects.link(lo)


def fog_box(lo, hi, density=0.016):
    bm = bmesh.new()
    c = (Vector(lo) + Vector(hi)) / 2
    box(bm, c, tuple(Vector(hi) - Vector(lo)))
    m = bpy.data.materials.new("fog")
    m.use_nodes = True
    nt = m.node_tree
    for n_ in list(nt.nodes):
        if n_.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n_)
    pv = nt.nodes.new("ShaderNodeVolumePrincipled")
    pv.inputs["Density"].default_value = density
    pv.inputs["Anisotropy"].default_value = 0.6
    pv.inputs["Color"].default_value = (0.8, 0.85, 0.9, 1)
    nt.links.new(pv.outputs[0], next(n_ for n_ in nt.nodes if n_.type == "OUTPUT_MATERIAL").inputs["Volume"])
    obj("fog", bm, [m])


def moon_sun(direction, strength=4.0):
    ld = bpy.data.lights.new("moon", "SUN")
    ld.energy = strength
    ld.angle = math.radians(1.5)
    ld.color = (0.58, 0.72, 1.0)
    lo = bpy.data.objects.new("moon", ld)
    lo.rotation_euler = Vector(direction).to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(lo)


def standing_cocoon(p, h=1.8, lean=0.0, yaw=0.0):
    """a person wrapped where they stood, strands staking them to the floor"""
    tilt = Matrix.Rotation(yaw, 3, "Z") @ Matrix.Rotation(lean, 3, "X")
    c = Vector(p) + Vector((0, 0, h / 2 + 0.02))
    cocoon(c, length=h, tilt=tilt)
    lines = []
    for i in range(7):
        a = i / 7 * 2 * math.pi + rnd.uniform(-0.3, 0.3)
        top = c + tilt @ Vector((0, 0, -h * rnd.uniform(0.05, 0.4))) + Vector((math.cos(a), math.sin(a), 0)) * 0.3
        foot = Vector(p) + Vector((math.cos(a), math.sin(a), 0)) * rnd.uniform(0.6, 1.4)
        lines.append(sag(top, foot, 0.03, n=4))
    threads("stakes", lines, r=0.006, m=LOOSE)


# ---------------------------------------------------------------- the lobby
def lobby():
    W, L, H = 7.0, 34.0, 9.0            # half width, length, wall height (the vault rises to 16)
    bm, bm_b = bmesh.new(), bmesh.new()
    # floor
    fb = bmesh.new()
    box(fb, (0, L / 2, -0.05), (2 * W + 2, L + 2, 0.1))
    obj("floor", fb, [floor_mat()])
    # the window wall (+x): stone piers between tall lancets, the moon behind
    wb = bmesh.new()
    wins = [5.0, 11.0, 17.0, 23.0]
    box(wb, (W + 0.6, L / 2, 1.5), (1.2, L, 3.0))
    y = 0.0
    for wy in wins + [L + 1.2]:
        box(wb, (W + 0.6, (y + wy - 1.2) / 2, H / 2 + 1.5), (1.2, max(0.1, wy - 1.2 - y), H - 3.0))
        y = wy + 1.2
    for wy in wins:                                     # each lancet's pointed head
        for i in range(6):
            t = i / 6
            box(wb, (W + 0.6, wy - 1.2 * (1 - t) - 0.1, H - 1.2 + t * 1.2), (1.2, 0.25, 0.4))
            box(wb, (W + 0.6, wy + 1.2 * (1 - t) + 0.1, H - 1.2 + t * 1.2), (1.2, 0.25, 0.4))
    # the shelf wall (-x)
    shelf_wall(-W, 1.0, L - 6.0, 8, 1, bm, bm_b)
    obj("walls", wb, [STONE])
    obj("cases", bm, [WALNUT])
    obj("books", bm_b, LEATHER)
    # the back wall with the arch into the stacks, and the entrance wall
    bk = bmesh.new()
    box(bk, (-W / 2 - 1.2, L, H), (W - 2.4, 1.0, 2 * H))
    box(bk, (W / 2 + 1.2, L, H), (W - 2.4, 1.0, 2 * H))
    box(bk, (0, L, H + 6.0), (4.8, 1.0, 2 * H - 12))
    for i in range(8):
        t = (i + 1) / 8
        wdt = 2.4 * (1 - math.cos(t * math.pi / 2) ** 0.6 * 0) * t
        box(bk, (-2.4 + wdt / 2, L, 6.0 + t * 3.0 - 0.2), (wdt, 1.0, 0.4))
        box(bk, (2.4 - wdt / 2, L, 6.0 + t * 3.0 - 0.2), (wdt, 1.0, 0.4))
    box(bk, (0, -0.5, H), (2 * W, 1.0, 2 * H))
    obj("ends", bk, [STONE])
    vault(-W, W, 0, L, H, 16.0, (STONE, WALNUT))
    # beyond the arch: the stacks, rows of shelves going off into blue dark
    st, st_b = bmesh.new(), bmesh.new()
    for i in range(5):
        x = -6 + i * 3
        shelf_wall(x, L + 1.5, L + 14, 7, 1 if i % 2 else -1, st, st_b)
    obj("stacks", st, [WALNUT])
    obj("stack_books", st_b, LEATHER)
    for y in (5.0, 11.0, 17.0, 23.0):                  # wall lamps along the cases and on the piers
        for x in (-W + 0.75, W - 0.15):
            yy = y - 3.0 if x > 0 else y
            gb = bmesh.new()
            box(gb, (x, yy, 3.6), (0.22, 0.22, 0.34))
            obj("walllamp", gb, [LAMPGLASS])
            ld = bpy.data.lights.new("walllamp", "POINT")
            ld.energy = 90
            ld.color = (0.55, 0.72, 1.0)
            lo = bpy.data.objects.new("walllamp", ld)
            lo.location = (x + (0.4 if x < 0 else -0.4), yy, 3.6)
            sc.collection.objects.link(lo)
    lb = bmesh.new()
    box(lb, (0, L + 9, 6.5), (0.3, 0.3, 0.4))
    obj("stack_lamp", lb, [LAMPGLASS])
    ld = bpy.data.lights.new("stacklamp", "POINT")
    ld.energy = 2500
    ld.color = (0.55, 0.72, 1.0)
    lo = bpy.data.objects.new("stacklamp", ld)
    lo.location = (0, L + 9, 6.0)
    sc.collection.objects.link(lo)
    # the desk across the hall, the turnstile in its middle, the clerk wrapped in his chair behind it
    dk = bmesh.new()
    for side in (-1, 1):
        box(dk, (side * 3.9, L - 5.0, 0.55), (5.4, 1.1, 1.1))
        box(dk, (side * 3.9, L - 5.0, 1.13), (5.6, 1.3, 0.06))
    obj("desk", dk, [WALNUT])
    tb = bmesh.new()
    limb(tb, (0, L - 5.0, 0), (0, L - 5.0, 1.0), 0.12, 0.12, seg=10)
    for i in range(3):
        a = i / 3 * 2 * math.pi + 0.4
        limb(tb, (0, L - 5.0, 0.9), (math.cos(a) * 0.6, L - 5.0 + math.sin(a) * 0.6, 0.9 - 0.2 * (i == 0)), 0.035, 0.035, seg=6)
    for side in (-1, 1):
        limb(tb, (side * 1.2, L - 5.6, 1.0), (side * 1.2, L - 4.4, 1.0), 0.05, 0.05, seg=6)
        limb(tb, (side * 1.2, L - 5.6, 0), (side * 1.2, L - 5.6, 1.0), 0.05, 0.05, seg=6)
        limb(tb, (side * 1.2, L - 4.4, 0), (side * 1.2, L - 4.4, 1.0), 0.05, 0.05, seg=6)
    obj("turnstile", tb, [PEWTER])
    led = bmesh.new()
    box(led, (-3.2, L - 5.0, 1.2), (0.9, 0.6, 0.06), 0.15)            # the open ledger
    box(led, (-3.2, L - 5.0, 1.23), (0.84, 0.56, 0.04), 0.15)
    obj("ledger", led, [PAGE])
    cocoon(Vector((-3.4, L - 3.9, 1.15)), length=1.6, tilt=Matrix.Rotation(-0.35, 3, "X"))   # the clerk
    lb = bmesh.new()
    limb(lb, (3.6, L - 5.0, 1.16), (3.6, L - 5.0, 1.7), 0.03, 0.03, seg=6)
    obj("desklamp_post", lb, [PEWTER])
    lg = bmesh.new()
    box(lg, (3.6, L - 5.0, 1.85), (0.22, 0.22, 0.3))
    obj("desklamp", lg, [LAMPGLASS])
    ld = bpy.data.lights.new("desklamp", "POINT")
    ld.energy = 120
    ld.color = (0.55, 0.72, 1.0)
    lo = bpy.data.objects.new("desklamp", ld)
    lo.location = (3.6, L - 5.4, 1.85)
    sc.collection.objects.link(lo)
    # the queue: pewter posts, the ropes between them replaced with silk, and the visitors wrapped where they waited
    post = bmesh.new()
    rope = []
    lanes = [(-1.0, 6.0, L - 7.5), (1.0, 6.0, L - 7.5)]
    for x, ya, yb in lanes:
        prev = None
        y = ya
        while y <= yb + 1e-3:
            limb(post, (x, y, 0), (x, y, 1.0), 0.05, 0.05, seg=8)
            ellipsoid(post, Vector((x, y, 1.02)), (0.08, 0.08, 0.08), seg=8)
            if prev is not None:
                rope.append(sag(prev, (x, y, 1.0), 0.25, n=8))
            prev = (x, y, 1.0)
            y += 2.5
    obj("posts", post, [PEWTER])
    threads("ropes", rope, r=0.03, m=LOOSE)
    for i, y in enumerate((8.0, 10.6, 13.1, 15.9, 18.3, 21.0, 23.6, 26.2)):
        standing_cocoon((rnd.uniform(-0.3, 0.3), y, 0), h=rnd.uniform(1.65, 1.95), lean=rnd.uniform(-0.12, 0.08),
                        yaw=rnd.uniform(-0.3, 0.3))
    # benches along the shelves with people still sat on them, wrapped
    bn = bmesh.new()
    for y in (6.0, 14.0, 22.0):
        box(bn, (-W + 1.6, y, 0.45), (0.6, 3.0, 0.08))
        for dy in (-1.3, 1.3):
            box(bn, (-W + 1.6, y + dy, 0.22), (0.5, 0.08, 0.44))
        for dy in (-0.8, 0.6):
            cocoon(Vector((-W + 1.55, y + dy, 1.15)), length=1.3, tilt=Matrix.Rotation(rnd.uniform(-0.2, 0.2), 3, "Y"))
    obj("benches", bn, [WALNUT])
    # silk: gauze stretched over two of the lancets, sheet webs up in the vault, strands everywhere
    for wy in (11.0, 23.0):
        sheet("winveil%.0f" % wy, (W + 0.05, wy - 1.3, 3.0), (W + 0.05, wy + 1.3, 3.0), (W + 0.05, wy - 1.3, H),
              (W + 0.05, wy + 1.3, H), droop=-0.4, noise=0.05, n=24)
    for k in range(5):
        y = 3 + k * 6.5
        tangle("vweb%d" % k, (-W + 0.4, y, H + 3.5), (W - 0.4, y + 1.5, H + 3.0), (-W + 1.5, y + 4.5, H + 5.8),
               (W - 1.5, y + 5.5, H + 6.2), droop=0.4, n=360)
    lines = []
    for _ in range(120):
        y = rnd.uniform(1, L - 1)
        p = Vector((rnd.choice((-W + 0.4, W - 0.2)), y, rnd.uniform(0.5, H + 4)))
        q = Vector((rnd.uniform(-W + 0.5, W - 0.5), y + rnd.uniform(-3, 3), H + rnd.uniform(1, 5)))
        if rnd.random() < 0.6:                          # most stay on their own wall
            q = Vector((p.x * rnd.uniform(0.75, 1.0), y + rnd.uniform(-2.5, 2.5), rnd.uniform(0, H)))
        lines.append(sag(p, q, (p - q).length * rnd.uniform(0.02, 0.1), n=8))
    threads("strands", lines, r=0.004, m=LOOSE)
    # silk trails across the floor from every cocoon toward the desk (they were dragged)
    trails = []
    for _ in range(26):
        a = Vector((rnd.uniform(-5, 5), rnd.uniform(3, L - 8), 0.01))
        b = Vector((rnd.uniform(-1.0, 1.0), L - 5.5, 0.01))
        trails.append([tuple(a.lerp(b, t / 10) + Vector((rnd.uniform(-0.1, 0.1), 0, 0))) for t in range(11)])
    threads("trails", trails, r=0.012, m=LOOSE)
    # papers and fallen books
    fl, pp = bmesh.new(), bmesh.new()
    for _ in range(80):
        p = Vector((rnd.uniform(-W + 1, W - 1), rnd.uniform(1, L - 6), 0))
        if rnd.random() < 0.3:
            box(fl, p + Vector((0, 0, 0.04)), (0.28, 0.2, 0.08), rnd.uniform(0, 6.28), mi=rnd.randrange(len(LEATHER)))
        else:
            box(pp, p + Vector((0, 0, 0.004)), (0.22, 0.3, 0.006), rnd.uniform(0, 6.28))
    obj("fallen", fl, LEATHER)
    obj("papers", pp, [PAGE])
    # egg sacs hung under the vault
    sacs = bmesh.new()
    hangs = []
    for k in range(7):
        top = Vector((rnd.uniform(-4, 4), rnd.uniform(4, L - 8), H + 4.5))
        for j in range(rnd.randint(1, 3)):
            r = rnd.uniform(0.35, 0.6)
            c = top + Vector((rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), -rnd.uniform(2.0, 4.5)))
            ellipsoid(sacs, c, (r, r, r * 1.15), seg=18)
            wrap_loops(c, Matrix.Identity(3), (r, r, r * 1.15), 18, WRAPS)
            hangs.append(sag(c + Vector((0, 0, r * 1.1)), top, 0.0, n=1))
    displace(sacs, 0.07, 2.5, seed=4)
    obj("sacs", sacs, [WRAP], smooth=True)
    threads("sac_threads", hangs, r=0.012, m=LOOSE)
    threads("wraps", WRAPS, r=0.007, m=LOOSE)
    WRAPS.clear()
    for k in range(11):
        y = k * 3.0 + rnd.uniform(-0.2, 0.2)
        if rnd.random() < 0.25:
            continue
        sheet("canopy%d" % k, (-W + 0.3, y, H + 0.6), (W - 0.3, y, H + 0.6), (-W + 0.3, y + 3.0, H + 0.8), (W - 0.3, y + 3.0, H + 0.8),
              droop=rnd.uniform(1.5, 3.2), noise=0.12, n=30, m=CANOPY)
    for side in (-1, 1):
        sheet("archveil%d" % side, (side * 2.5, L - 0.6, 0.0), (side * 1.6, L - 0.8, 0.6), (side * 2.5, L - 0.6, 9.0),
              (side * 0.6, L - 0.6, 9.0), droop=-0.4, noise=0.1, n=24)
    chandelier(Vector((0, 12.0, H + 1.0)), top=Vector((0, 12.0, 16.0)))
    chandelier(Vector((0, 24.0, H + 1.5)), top=Vector((0, 24.0, 16.0)))
    # two spiders the size of hounds on the vault, watching
    spider(at=(-3.0, 18.0, H + 4.6), size=0.22, yaw=math.radians(200), pitch=math.radians(-150))
    spider(at=(4.6, 27.0, H + 2.2), size=0.18, yaw=math.radians(120), pitch=math.radians(-130))
    # the moon slants in through the lancets
    moon_sun((-1.0, 0.35, -0.75), 5.0)
    fog_box((-W, 0, 0), (W, L, 16), 0.02)
    fog_box((-7, L + 0.6, 0), (7, L + 14, 8), 0.03)
    ld = bpy.data.lights.new("fill", "AREA")
    ld.energy = 300
    ld.size = 10
    ld.color = (0.4, 0.5, 0.75)
    lo = bpy.data.objects.new("fill", ld)
    lo.location = (0, 6, 0.3)
    lo.rotation_euler = (math.pi, 0, 0)
    sc.collection.objects.link(lo)


ROOMS = {
    "lobby": (lobby, {
        "hero": ((3.4, 1.5, 1.8), (-0.8, 26.0, 3.6), 20),
        "queue": ((3.8, 9.5, 1.4), (-0.5, 20.0, 1.6), 24),
        "desk": ((2.5, 20.5, 2.0), (0.0, 33.0, 2.6), 22),
    }),
}
if __name__ == "__main__":
    build, shots = ROOMS[ROOM]
    build()
    render(shots, ROOM)
