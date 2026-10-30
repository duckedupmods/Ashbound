"""Gallows Hill's props as real meshes (propkit.py does the baking and writing): tallow lamps on the scaffold posts,
the noose, the gibbet cages' riveted straps and plates, the drop hatches in the deck, hewn rails, the hangman's lever,
the notice post, a tar pot, thorn scrub and a hay bale, the market's counters, canvas awnings and drapes, a coffer.

  blender -b -P tools/blender/gallows_props.py -- [preview] [fast] [names...]
    preview -> tools/renders/gallows_props.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "propkit.py"), encoding="utf-8").read())

TIMBER = wood("gal_timber", [(0.0, (0.03, 0.028, 0.026)), (0.5, (0.085, 0.078, 0.07)), (1.0, (0.15, 0.14, 0.125))], along="Z")
TIMBER_X = wood("gal_timber_x", [(0.0, (0.03, 0.028, 0.026)), (0.5, (0.085, 0.078, 0.07)), (1.0, (0.15, 0.14, 0.125))], along="X")
TAR_WOOD = wood("tar_wood", [(0.0, (0.008, 0.007, 0.006)), (0.5, (0.025, 0.021, 0.017)), (1.0, (0.05, 0.042, 0.032))], along="Y", rough=0.45)
PLANK = wood("stall_plank", [(0.0, (0.04, 0.028, 0.018)), (0.5, (0.11, 0.075, 0.045)), (1.0, (0.19, 0.135, 0.08))], along="X")
IRON = rusty("gal_iron", iron=(0.045, 0.045, 0.045), rust=(0.3, 0.11, 0.035), amount=0.48)
RIVET = rusty("gal_rivet", iron=(0.08, 0.075, 0.07), rust=(0.26, 0.1, 0.035), amount=0.6)
ROPE = mottled("hemp", [(0.0, (0.2, 0.15, 0.08)), (0.6, (0.36, 0.28, 0.15)), (1.0, (0.46, 0.37, 0.21))], 60.0, 0.95)
TALLOW = mottled("tallow", [(0.0, (0.55, 0.47, 0.3)), (1.0, (0.74, 0.66, 0.46))], 14.0, 0.5)
FLAME = glass("tallow_flame", (1.0, 0.62, 0.22), glow=5.0)
TAR = mat("tar", (0.008, 0.007, 0.006), 0.12, **{"Coat Weight": 1.0})
PAPER = mottled("notice_paper", [(0.0, (0.42, 0.37, 0.27)), (1.0, (0.6, 0.55, 0.42))], 20.0, 0.9)
INK = mat("ink", (0.02, 0.018, 0.016), 0.6)
STRAW = mottled("straw", [(0.0, (0.3, 0.22, 0.07)), (0.5, (0.5, 0.4, 0.15)), (1.0, (0.62, 0.52, 0.24))], 45.0, 0.9)
THORN = wood("thorn", [(0.0, (0.03, 0.025, 0.02)), (0.6, (0.09, 0.075, 0.06)), (1.0, (0.16, 0.135, 0.11))], along="Z", grain=40)
TURNIP = mottled("turnip", [(0.0, (0.35, 0.12, 0.2)), (1.0, (0.62, 0.55, 0.45))], 8.0, 0.6)
APPLE = mottled("apple", [(0.0, (0.25, 0.04, 0.03)), (1.0, (0.45, 0.12, 0.05))], 10.0, 0.4)
CLOTH = {"red": ((0.24, 0.035, 0.03), (0.42, 0.38, 0.3)), "grey": ((0.16, 0.16, 0.15), None),
         "black": ((0.025, 0.024, 0.024), None), "brown": ((0.17, 0.09, 0.04), (0.38, 0.26, 0.1)),
         "pale": ((0.42, 0.4, 0.36), (0.3, 0.28, 0.25))}
CANVAS = {}
for c, (main, stripe) in CLOTH.items():
    lo = tuple(v * 0.6 for v in main)
    CANVAS[c] = (mottled("canvas_" + c, [(0.0, lo), (1.0, main)], 9.0, 0.85),
                 mottled("canvas_%s_stripe" % c, [(0.0, tuple(v * 0.65 for v in stripe)), (1.0, stripe)], 9.0, 0.85) if stripe else None)
GLOWS.add(FLAME)
LIFT.update({"hemp_rope": 1.0, "gibbet_plate_top": 0.0})


def sheet(bm, at, nu, nv, thick, mi):
    """a cloth or plate sheet thick enough to have two sides: at(u, v) gives its middle surface, mi(u) its material"""
    top, bot = [], []
    for j in range(nv + 1):
        rt, rb = [], []
        for i in range(nu + 1):
            u, v = i / nu, j / nv
            p = at(u, v)
            du = at(min(1, u + 1e-3), v) - at(max(0, u - 1e-3), v)
            dv = at(u, min(1, v + 1e-3)) - at(u, max(0, v - 1e-3))
            n = du.cross(dv).normalized()
            rt.append(bm.verts.new(p + n * thick / 2))
            rb.append(bm.verts.new(p - n * thick / 2))
        top.append(rt)
        bot.append(rb)
    for j in range(nv):
        for i in range(nu):
            m = mi((i + 0.5) / nu)
            bm.faces.new((top[j][i], top[j][i + 1], top[j + 1][i + 1], top[j + 1][i])).material_index = m
            bm.faces.new((bot[j][i], bot[j + 1][i], bot[j + 1][i + 1], bot[j][i + 1])).material_index = m
    edges = [(top[0][i], top[0][i + 1], bot[0][i + 1], bot[0][i], (i + 0.5) / nu) for i in range(nu)]
    edges += [(top[nv][i + 1], top[nv][i], bot[nv][i], bot[nv][i + 1], (i + 0.5) / nu) for i in range(nu)]
    edges += [(top[j + 1][0], top[j][0], bot[j][0], bot[j + 1][0], 0.0) for j in range(nv)]
    edges += [(top[j][nu], top[j + 1][nu], bot[j + 1][nu], bot[j][nu], 1.0) for j in range(nv)]
    for a, b, c, d, u in edges:
        bm.faces.new((a, b, c, d)).material_index = mi(min(u, 0.999))


# ---------------------------------------------------------------- the scaffold

def tallow_lamp():
    """an iron dish on a spike driven into the post's top: three fat tallow candles guttering in it, wax run over
    the rim, a bent windguard behind"""
    bm = bmesh.new()
    cyl(bm, O, 0.03, 0.12, 0, seg=8, r2=0.018)
    lathe(bm, [(0.0, 0.12), (0.2, 0.12), (0.24, 0.17), (0.215, 0.17), (0.18, 0.14), (0.0, 0.14)], O, 0, 24)
    for k, (dx, dy, h, r) in enumerate([(-0.07, 0.03, 0.34, 0.06), (0.07, 0.05, 0.26, 0.055), (0.0, -0.08, 0.2, 0.065)]):
        c = O + Vector((dx, dy, 0.14))
        vs = cyl(bm, c, r, h, 1, seg=14, r2=r * 0.9)
        displace(vs, 0.008, 18.0, k)
        for d in range(3):   # drips down the side
            a = d * 2.1 + k
            p = c + Vector((math.cos(a) * r, math.sin(a) * r, h * (0.6 + 0.12 * d)))
            tube(bm, [p, p + Vector((math.cos(a) * 0.01, math.sin(a) * 0.01, -h * 0.35))], lambda t: 0.012 * (1.2 - t), 1, sides=5)
        tube(bm, [c + Vector((0, 0, h)), c + Vector((0, 0, h + 0.025))], 0.004, 3, sides=4)   # the wick
        ellipsoid(bm, c + Vector((0, 0, h + 0.07)), (0.022, 0.022, 0.055), 2, seg=10)        # the flame
    ellipsoid(bm, O + Vector((0.14, -0.1, 0.17)), (0.07, 0.05, 0.02), 1, seg=10)              # a pool of run wax
    tube(bm, [O + Vector((-0.17, -0.16, 0.16)), O + Vector((-0.2, -0.2, 0.5)), O + Vector((-0.06, -0.24, 0.62))], 0.014, 0, sides=5)
    box(bm, O + Vector((-0.2, -0.22, 0.3)), O + Vector((0.12, -0.2, 0.58)), 0, bevel=0.004)  # the guard's plate
    return new_obj("tallow_lamp", bm, [IRON, TALLOW, FLAME, INK])


def hemp_rope():
    """a noose hung from the beam's chain: a hangman's knot of wound coils, the loop hanging open below"""
    bm = bmesh.new()
    rope = 0.03
    tube(bm, [O + Vector((0.004 * math.sin(k), 0.004 * math.cos(k), 1.0 - k * 0.04)) for k in range(12)], rope, 0, sides=8)
    for k in range(7):   # the coils of the knot
        z = 0.5 + k * 0.032
        tube(bm, ring(O + Vector((0, 0, z)), 0.045, "Z", 14, 0.08, k), 0.017, 0, sides=6, closed=True)
    pts = []
    for k in range(24):   # the loop: a teardrop, its point in the knot
        t = k / 23 * 2 * math.pi
        x = math.sin(t) * 0.17 * (0.4 + 0.6 * math.sin(t / 2))
        z = 0.5 - (1 - math.cos(t)) / 2 * 0.36
        pts.append(O + Vector((x, 0.02 * math.sin(t * 3), z)))
    tube(bm, pts, rope, 0, sides=8)
    tube(bm, [O + Vector((0.02, 0.02, 0.5)), O + Vector((0.04, 0.03, 0.4)), O + Vector((0.035, 0.05, 0.33))], 0.022, 0, sides=6)   # the tail
    return new_obj("hemp_rope", bm, [ROPE])


def gibbet_bars_post():
    bm = bmesh.new()
    box(bm, O + Vector((-0.05, -0.05, 0)), O + Vector((0.05, 0.05, 1.0)), 0, bevel=0.01)
    for z in (0.05, 0.5, 0.95):
        ellipsoid(bm, O + Vector((0, 0.055, z)), (0.025, 0.012, 0.025), 1, seg=8)
        ellipsoid(bm, O + Vector((0, -0.055, z)), (0.025, 0.012, 0.025), 1, seg=8)
    return new_obj("gibbet_bars_post", bm, [IRON, RIVET])


def gibbet_bars_side():
    """flat forged straps to the north edge: one upright, bands at the foot, the waist and the head, riveted"""
    bm = bmesh.new()
    box(bm, Vector((0.475, -0.27, 0.0)), Vector((0.525, -0.21, 1.0)), 0, bevel=0.008)
    for z in (0.08, 0.5, 0.92):
        box(bm, Vector((0.47, -0.5, z - 0.035)), Vector((0.53, 0.0, z + 0.035)), 0, bevel=0.008)
        for s in (-1, 1):
            ellipsoid(bm, Vector((0.5 + s * 0.03, -0.24, z)), (0.012, 0.022, 0.022), 1, seg=8)
    return new_obj("gibbet_bars_side", bm, [IRON, RIVET])


def _plate(bm, z0, z1, mi_plate, mi_rivet, mi_wood=None):
    """a riveted iron cap for a cage (mi_wood None) or a tarred hatch bound in iron"""
    if mi_wood is None:
        box(bm, (0.02, -0.98, z0), (0.98, -0.02, z1), mi_plate, bevel=0.012)
        for x in (0.25, 0.75):
            box(bm, (x - 0.05, -1.0, z1 - 0.02), (x + 0.05, 0.0, z1 + 0.012), mi_plate, bevel=0.006)
        for y in (-0.25, -0.75):
            box(bm, (0.0, y - 0.05, z1 - 0.02), (1.0, y + 0.05, z1 + 0.012), mi_plate, bevel=0.006)
        pts = [(x, y) for x in (0.25, 0.75) for y in (-0.05, -0.25, -0.5, -0.75, -0.95)]
    else:
        for k in range(4):
            x0 = k * 0.25
            vs = box(bm, (x0 + 0.006, -1.0, z0), (x0 + 0.244, 0.0, z1), mi_wood, bevel=0.01)
            displace(vs, 0.004, 9.0, k)
        for y in (-0.15, -0.85):   # the iron bands across, hinged at the north edge
            box(bm, (0.0, y - 0.055, z1 - 0.01), (1.0, y + 0.055, z1 + 0.012), mi_plate, bevel=0.006)
        pts = [(x, y) for x in (0.125, 0.375, 0.625, 0.875) for y in (-0.15, -0.85)]
    for x, y in pts:
        ellipsoid(bm, Vector((x, y, z1 + 0.014)), (0.02, 0.02, 0.012), mi_rivet, seg=8)


def _opened(bm):
    """swung up against the south side of its block, as vanilla's open trapdoor stands"""
    rot = Matrix.Rotation(math.pi / 2, 4, "X")
    for v in bm.verts:
        p = rot @ v.co
        v.co = Vector((p.x, p.y - 0.8125, p.z + 1.0))


def gibbet_plate_bottom():
    bm = bmesh.new()
    _plate(bm, 0.0, 0.1875, 0, 1)
    return new_obj("gibbet_plate_bottom", bm, [IRON, RIVET])


def gibbet_plate_top():
    bm = bmesh.new()
    _plate(bm, 0.8125, 0.98, 0, 1)
    return new_obj("gibbet_plate_top", bm, [IRON, RIVET])


def gibbet_plate_open():
    bm = bmesh.new()
    _plate(bm, 0.0, 0.1875, 0, 1)
    _opened(bm)
    return new_obj("gibbet_plate_open", bm, [IRON, RIVET])


def gallows_trapdoor_bottom():
    bm = bmesh.new()
    _plate(bm, 0.0, 0.1875, 0, 1, 2)
    return new_obj("gallows_trapdoor_bottom", bm, [IRON, RIVET, TAR_WOOD])


def gallows_trapdoor_top():
    bm = bmesh.new()
    _plate(bm, 0.8125, 0.98, 0, 1, 2)
    return new_obj("gallows_trapdoor_top", bm, [IRON, RIVET, TAR_WOOD])


def gallows_trapdoor_open():
    bm = bmesh.new()
    _plate(bm, 0.0, 0.1875, 0, 1, 2)
    _opened(bm)
    return new_obj("gallows_trapdoor_open", bm, [IRON, RIVET, TAR_WOOD])


def gallows_rail_post():
    """a hewn timber post, adze-faceted, a rusted iron band near its top"""
    bm = bmesh.new()
    vs = box(bm, O + Vector((-0.09, -0.09, 0)), O + Vector((0.09, 0.09, 1.0)), 0, bevel=0.02)
    displace(vs, 0.01, 7.0, 11)
    box(bm, O + Vector((-0.105, -0.105, 0.86)), O + Vector((0.105, 0.105, 0.92)), 1, bevel=0.008)
    return new_obj("gallows_rail_post", bm, [TIMBER, IRON])


def gallows_rail_side():
    bm = bmesh.new()
    for z in (0.35, 0.8):
        vs = box(bm, Vector((0.43, -0.5, z - 0.065)), Vector((0.57, 0.0, z + 0.065)), 0, bevel=0.018)
        displace(vs, 0.007, 8.0, int(z * 10))
    return new_obj("gallows_rail_side", bm, [TIMBER])


def drop_lever():
    """the drop's lever: a heavy iron quadrant bolted to the deck, a long timber haft thrown back, its grip bound
    in rope"""
    bm = bmesh.new()
    box(bm, O + Vector((-0.2, -0.3, 0)), O + Vector((0.2, 0.3, 0.06)), 0, bevel=0.01)
    for s in (-1, 1):
        pts = [O + Vector((s * 0.09, math.sin(t) * 0.28, 0.06 + math.cos(t) * 0.28)) for t in (k / 12 * math.pi - math.pi / 2 for k in range(13))]
        vs = []
        for p in pts:
            vs.append(p)
        tube(bm, vs, 0.02, 0, sides=5)
        for y in (-0.22, 0.0, 0.22):
            ellipsoid(bm, O + Vector((s * 0.15, y, 0.065)), (0.025, 0.025, 0.014), 1, seg=8)
    cyl(bm, O + Vector((-0.12, 0, 0.1)), 0.035, 0.24, 0, seg=10, axis="X")                                 # the pivot pin
    a = math.radians(-30)
    tip = O + Vector((0, math.sin(a) * 0.82, 0.1 + math.cos(a) * 0.82))
    tube(bm, [O + Vector((0, 0, 0.08)), tip], 0.04, 2, sides=8)                                            # the haft
    for k in range(6):
        t = 0.72 + k * 0.035
        tube(bm, ring(O + Vector((0, math.sin(a) * 0.82 * t, 0.1 + math.cos(a) * 0.82 * t)), 0.046, "Z", 10), 0.009, 3, sides=4, closed=True)
    return new_obj("drop_lever", bm, [IRON, RIVET, TIMBER, ROPE])


def gallows_sign():
    """the notice post: a split board nailed to a hewn stake, the sentences pinned on it, a noose hung off its arm"""
    bm = bmesh.new()
    vs = box(bm, O + Vector((-0.06, -0.06, 0)), O + Vector((0.06, 0.06, 0.95)), 0, bevel=0.015)
    displace(vs, 0.008, 8.0, 2)
    vs = box(bm, O + Vector((-0.4, 0.06, 0.42)), O + Vector((0.4, 0.12, 0.86)), 1, bevel=0.012)
    displace(vs, 0.005, 9.0, 6)
    box(bm, O + Vector((-0.42, 0.04, 0.62)), O + Vector((0.42, 0.13, 0.64)), 1)                          # the split
    for k, (x, z, w, h, r) in enumerate([(-0.2, 0.66, 0.24, 0.17, 0.05), (0.12, 0.62, 0.2, 0.22, -0.07), (-0.08, 0.47, 0.18, 0.12, 0.1)]):
        rot = Matrix.Rotation(r, 3, "Y")
        c = O + Vector((x, 0.125, z))
        box(bm, c - Vector((w / 2, 0, h / 2)), c + Vector((w / 2, 0.006, h / 2)), 2, rot=rot)
        for line in range(4 if h > 0.15 else 2):   # the writing, as ink strokes
            lz = h / 2 - 0.035 - line * 0.035
            ll = w * (0.75 if line else 0.5)
            p = c + rot @ Vector((-w / 2 + 0.025, 0.007, lz))
            box(bm, p, p + rot @ Vector((ll, 0.002, 0.012)), 3, rot=None)
        ellipsoid(bm, c + rot @ Vector((0, 0.01, h / 2 - 0.015)), (0.012, 0.01, 0.012), 4, seg=6)          # its nail
    return new_obj("gallows_sign", bm, [TIMBER, TIMBER_X, PAPER, INK, RIVET])


# ---------------------------------------------------------------- the hill

def gallows_thorn():
    """a dead thorn bush: twisted grey branches forking from one root, thorns along them"""
    bm = bmesh.new()

    def branch(p, d, L, r, depth, seed):
        pts = [p]
        for k in range(5):
            n = noise.noise(Vector((seed, k * 0.7, depth)))
            d = (d + Vector((n * 0.6, noise.noise(Vector((k, seed, 3.0))) * 0.6, 0.1))).normalized()
            pts.append(pts[-1] + d * (L / 5))
        tube(bm, pts, lambda t: r * (1 - 0.7 * t), 0, sides=5)
        for k in range(1, 5):   # thorns
            a = seed * 3 + k * 2.3
            q = pts[k]
            tube(bm, [q, q + Vector((math.cos(a), math.sin(a), 0.4)) * 0.045], lambda t: 0.006 * (1 - t), 0, sides=3)
        if depth < 2:
            for j in range(2):
                branch(pts[2 + j], (d + Vector((math.cos(seed + j * 2.5), math.sin(seed + j * 2.5), 0.3))).normalized(), L * 0.6, r * 0.6,
                       depth + 1, seed * 1.7 + j + 1)
    for k in range(4):
        a = k * math.pi / 2 + 0.4
        branch(O + Vector((0, 0, 0)), Vector((math.cos(a) * 0.5, math.sin(a) * 0.5, 0.9)).normalized(), 0.55, 0.03, 0, k + 1.0)
    return new_obj("gallows_thorn", bm, [THORN])


def straw_bale():
    """a bale of old straw tied with two twine bands, its ends ragged"""
    bm = bmesh.new()
    vs = box(bm, O + Vector((-0.47, -0.36, 0)), O + Vector((0.47, 0.36, 0.62)), 0, bevel=0.06)
    displace(vs, 0.02, 14.0, 4)
    for x in (-0.22, 0.22):
        pts = [O + Vector((x, -0.37, 0.005)), O + Vector((x, -0.37, 0.625)), O + Vector((x, 0.37, 0.625)), O + Vector((x, 0.37, 0.005))]
        tube(bm, pts, 0.012, 1, sides=4, closed=True)
    for k in range(18):   # stray straws
        a = k * 2.4
        p = O + Vector((math.cos(a) * 0.45, math.sin(a) * 0.33, 0.1 + (k % 5) * 0.11))
        tube(bm, [p, p + Vector((math.cos(a) * 0.08, math.sin(a) * 0.06, 0.03 * (k % 3 - 1)))], 0.004, 0, sides=3)
    return new_obj("straw_bale", bm, [STRAW, ROPE])


def tar_cauldron():
    """a squat iron pot of hangman's tar on three legs, the tar's skin glossy with a bubble, a stirring stick in it"""
    bm = bmesh.new()
    lathe(bm, [(0.0, 0.1), (0.2, 0.1), (0.36, 0.25), (0.4, 0.45), (0.37, 0.66), (0.4, 0.7), (0.36, 0.72), (0.32, 0.66), (0.33, 0.45),
               (0.28, 0.25), (0.0, 0.2)], O, 0, 28)
    cyl(bm, O + Vector((0, 0, 0.6)), 0.335, 0.012, 1, seg=28)
    ellipsoid(bm, O + Vector((0.1, -0.08, 0.612)), (0.06, 0.06, 0.035), 1, seg=10)
    for k in range(3):
        a = k * 2 * math.pi / 3
        tube(bm, [O + Vector((math.cos(a) * 0.24, math.sin(a) * 0.24, 0.2)), O + Vector((math.cos(a) * 0.32, math.sin(a) * 0.32, 0.0))],
             lambda t: 0.04 * (1 - 0.4 * t), 0, sides=6)
    for s in (-1, 1):   # lugs for its bail
        tube(bm, ring(O + Vector((s * 0.4, 0, 0.66)), 0.04, "X", 10), 0.012, 0, sides=4, closed=True)
    tube(bm, [O + Vector((-0.1, 0.05, 0.4)), O + Vector((0.22, 0.12, 0.98))], 0.022, 2, sides=6)
    return new_obj("tar_cauldron", bm, [IRON, TAR, THORN])


def gallows_coffer():
    """a tarred strongbox bound in iron, its lid bowed, a padlock on the hasp"""
    bm = bmesh.new()
    box(bm, O + Vector((-0.44, -0.32, 0.0)), O + Vector((0.44, 0.32, 0.52)), 0, bevel=0.02)
    lid = lathe(bm, [(0.0, -0.44), (0.32, -0.44), (0.32, 0.44), (0.0, 0.44)], O + Vector((0, 0, 0.52)), 0, 24, "X")
    for rg in lid:
        for v in rg:
            if v.co.z < O.z + 0.52:
                v.co.z = O.z + 0.52
            v.co.z = O.z + 0.52 + (v.co.z - O.z - 0.52) * 0.5
    for x in (-0.34, 0.0, 0.34):
        box(bm, O + Vector((x - 0.045, -0.335, 0.0)), O + Vector((x + 0.045, 0.335, 0.54)), 1, bevel=0.005)
        tube(bm, [O + Vector((x, -0.33 + 0.66 * t, 0.52 + 0.16 * math.sin(t * math.pi) + 0.01)) for t in (k / 10 for k in range(11))], 0.013, 1, sides=4)
        for z in (0.08, 0.26, 0.44):
            ellipsoid(bm, O + Vector((x, 0.34, z)), (0.016, 0.012, 0.016), 2, seg=6)
    box(bm, O + Vector((-0.06, 0.32, 0.34)), O + Vector((0.06, 0.35, 0.52)), 1, bevel=0.008)
    box(bm, O + Vector((-0.06, 0.35, 0.2)), O + Vector((0.06, 0.39, 0.32)), 2, bevel=0.012)   # the padlock
    tube(bm, [O + Vector((-0.035, 0.37, 0.32)), O + Vector((-0.035, 0.37, 0.38)), O + Vector((0.035, 0.37, 0.38)), O + Vector((0.035, 0.37, 0.32))],
         0.01, 2, sides=4)
    return new_obj("gallows_coffer", bm, [TAR_WOOD, IRON, RIVET])


# ---------------------------------------------------------------- the market

def stall_counter():
    """a market counter: planks on two trestles, a cloth runner over it, a basket of turnips and some apples"""
    bm = bmesh.new()
    for k in range(3):
        y0 = -0.95 + k * 0.3
        vs = box(bm, Vector((0.02, y0, 0.8)), Vector((0.98, y0 + 0.29, 0.86)), 0, bevel=0.01)
        displace(vs, 0.004, 9.0, k)
    for x in (0.15, 0.85):
        for s in (-1, 1):
            tube(bm, [Vector((x, -0.5 + s * 0.12, 0.8)), Vector((x, -0.5 + s * 0.38, 0.0))], 0.03, 0, sides=6)
        box(bm, Vector((x - 0.03, -0.8, 0.72)), Vector((x + 0.03, -0.2, 0.8)), 0, bevel=0.008)
    sheet(bm, lambda u, v: Vector((0.3 + u * 0.4, -0.95 + v * 0.95 + 0.0, 0.865)) if v > 0.08 else
          Vector((0.3 + u * 0.4, -0.95, 0.865 - (0.08 - v) * 3)), 6, 12, 0.008, lambda u: 1)
    lathe(bm, [(0.0, 0.865), (0.1, 0.865), (0.14, 0.96), (0.13, 0.96), (0.09, 0.875), (0.0, 0.875)], Vector((0.22, -0.32, 0)), 2, 16)
    for k in range(4):
        a = k * 1.6
        ellipsoid(bm, Vector((0.22 + math.cos(a) * 0.05, -0.32 + math.sin(a) * 0.05, 0.93)), (0.045, 0.045, 0.04), 3, seg=10)
    for k, (x, y) in enumerate([(0.62, -0.25), (0.7, -0.3), (0.66, -0.18), (0.78, -0.62)]):
        ellipsoid(bm, Vector((x, y, 0.9)), (0.04, 0.04, 0.036), 4, seg=10)
    return new_obj("stall_counter", bm, [PLANK, CANVAS["red"][0], THORN, TURNIP, APPLE])


def awning(colour):
    """one block's run of a stall's canvas roof: from the eave at the front edge up to the back at the next step,
    sagging a little between, striped down the slope in two of the colours; the stripes repeat every block so a
    roof reads as one cloth"""
    def make():
        bm = bmesh.new()
        main, stripe = CANVAS[colour]

        def at(u, v):
            return Vector((u, -v, v - 0.03 * math.sin(v * math.pi) + 0.006 * math.sin(u * 4 * math.pi)))
        sheet(bm, at, 16, 10, 0.022, (lambda u: 1 if stripe and int(u * 4) % 2 else 0))
        return new_obj("awning_" + colour, bm, [main, stripe] if stripe else [main])
    make.__name__ = "awning_" + colour
    return make


def drape(colour):
    """the hanging edge under an eave: the cloth falls from the front of the block to a scalloped hem, bellied out a
    little, two scallops a block so they run on from the next"""
    def make():
        bm = bmesh.new()
        main, stripe = CANVAS[colour]

        def at(u, v):
            hem = 0.42 + 0.1 * abs(math.cos(u * 2 * math.pi))
            z = 1.0 - v * (1.0 - hem)
            return Vector((u, -0.015 + 0.03 * math.sin(v * math.pi * 0.8), z))
        sheet(bm, at, 16, 8, 0.02, (lambda u: 1 if stripe and int(u * 4) % 2 else 0))
        return new_obj("drape_" + colour, bm, [main, stripe] if stripe else [main])
    make.__name__ = "drape_" + colour
    return make


MAKE = [(tallow_lamp, (128, 128)), (hemp_rope, (64, 64)), (gibbet_bars_post, (64, 64)), (gibbet_bars_side, (64, 64)),
        (gibbet_plate_bottom, (128, 128)), (gibbet_plate_top, (128, 128)), (gibbet_plate_open, (128, 128)),
        (gallows_trapdoor_bottom, (128, 128)), (gallows_trapdoor_top, (128, 128)), (gallows_trapdoor_open, (128, 128)),
        (gallows_rail_post, (64, 64)), (gallows_rail_side, (64, 64)), (drop_lever, (128, 128)), (gallows_sign, (256, 256)),
        (gallows_thorn, (128, 128)), (straw_bale, (256, 256)), (tar_cauldron, (256, 256)), (gallows_coffer, (256, 256)),
        (stall_counter, (256, 256))]
MAKE += [(awning(c), (256, 256)) for c in CLOTH] + [(drape(c), (256, 256)) for c in CLOTH]
run(MAKE, GLOWS, "gallows_props")
