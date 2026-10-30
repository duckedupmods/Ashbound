"""The Drowned Cellar's props as real meshes (propkit.py does the baking and writing): rotten wine casks lying on
chocks and standing on end, the rack walls of casks and of bottles, the vintners' caged amber lamps, rusted chain,
grille and sluice grate, cask-oak rails, the cooper's bench, a coffer, wine spilt from a broken bottle.

  blender -b -P tools/blender/cellar_props.py -- [preview] [fast] [names...]
    preview -> tools/renders/cellar_props.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "propkit.py"), encoding="utf-8").read())

STAVE = [(0.0, (0.025, 0.017, 0.012)), (0.45, (0.075, 0.045, 0.028)), (0.75, (0.11, 0.07, 0.04)), (1.0, (0.15, 0.1, 0.06))]
OAK = wood("cask_oak", STAVE, along="Y")
OAK_UP = wood("cask_oak_up", STAVE, along="Z")
HEAD = wood("cask_head", [(0.0, (0.03, 0.02, 0.014)), (0.5, (0.09, 0.058, 0.035)), (1.0, (0.16, 0.11, 0.07))], along="X", grain=18)
RACK = wood("rack_oak", [(0.0, (0.015, 0.012, 0.01)), (0.5, (0.045, 0.032, 0.022)), (1.0, (0.08, 0.058, 0.04))], along="X")
POST = wood("post_oak", [(0.0, (0.02, 0.015, 0.011)), (0.5, (0.06, 0.042, 0.028)), (1.0, (0.1, 0.075, 0.05))], along="Z")
IRON = rusty("rust_iron", amount=0.42)
HOOP = rusty("hoop_iron", iron=(0.07, 0.06, 0.05), rust=(0.3, 0.1, 0.035), amount=0.5)
CORK = mottled("cork", [(0.0, (0.25, 0.16, 0.08)), (1.0, (0.42, 0.3, 0.17))], 30.0, 0.9)
BOTTLE = glass("bottle", (0.04, 0.12, 0.06), rough=0.12)
BOTTLE_DARK = glass("bottle_dark", (0.03, 0.06, 0.035), rough=0.12)
SEAL = mat("seal_wax", (0.25, 0.03, 0.03), 0.4)
WINE = mat("wine", (0.12, 0.01, 0.02), 0.05, **{"Coat Weight": 1.0})
AMBER = glass("amber", (1.0, 0.55, 0.16), glow=4.0)
BACK = mat("back", (0.012, 0.009, 0.007), 0.9)
CHALK = mat("chalk", (0.62, 0.6, 0.55), 0.9)
GLOWS.add(AMBER)
LIFT.update({"cellar_lamp": 1.2, "sluice_grate_top": 0.0})


def staves(bm, verts, c, axis, n=16, depth=0.008):
    """the seams between the staves: every vertex on a seam pushed in a little"""
    ax = {"Y": 1, "Z": 2}[axis]
    for v in verts:
        p = v.co - Vector(c)
        a, b = (p.x, p.z) if axis == "Y" else (p.x, p.y)
        t = math.atan2(b, a) / (2 * math.pi) * n
        if abs(t - round(t)) < 0.12:
            r = Vector((a, b)).length
            if r > 1e-3:
                k = (r - depth) / r
                if axis == "Y":
                    v.co.x, v.co.z = c[0] + a * k, c[2] + b * k
                else:
                    v.co.x, v.co.y = c[0] + a * k, c[1] + b * k


def cask_body(bm, c, length, r_end, r_mid, axis, mi_oak, mi_head, mi_hoop, hoops=(0.08, 0.27, 0.73, 0.92), seg=48):
    """a cask: staves bulging to the bilge, the chime standing proud of each sunk head, rusted hoops round it"""
    L2, lip, sink = length / 2, 0.028, 0.035
    prof = [(r_end - lip, -L2 + sink), (r_end - lip, -L2)]
    for k in range(13):
        t = k / 12
        prof.append((r_end + (r_mid - r_end) * math.sin(t * math.pi), -L2 + t * length))
    prof += [(r_end - lip, L2), (r_end - lip, L2 - sink)]
    rings = lathe(bm, prof, c, mi_oak, seg, axis, cap=False)
    staves(bm, [v for rg in rings[2:-2] for v in rg], c, axis)
    for side in (-1, 1):   # the heads, sunk inside the chime
        h = side * (L2 - sink) - (0.006 if side > 0 else 0)
        d = {"Y": Vector((0, h, 0)), "Z": Vector((0, 0, h))}[axis]
        cyl(bm, Vector(c) + d, r_end - lip + 0.002, 0.006, mi_head, seg=32, axis=axis)
    for t in hoops:
        h = -L2 + t * length
        r = r_end + (r_mid - r_end) * math.sin(t * math.pi) + 0.006
        pts = ring(Vector(c) + {"Y": Vector((0, h, 0)), "Z": Vector((0, 0, h))}[axis], r, "Y" if axis == "Y" else "Z", 40)
        tube(bm, pts, 0.012, mi_hoop, sides=6, closed=True)


def cellar_cask():
    """a wine cask on its side on two chocks, a cork bung in the top stave"""
    bm = bmesh.new()
    c = O + Vector((0, 0, 0.47))
    cask_body(bm, c, 0.88, 0.34, 0.42, "Y", 0, 1, 2)
    cyl(bm, c + Vector((0.0, 0.0, 0.405)), 0.035, 0.035, 3, seg=10)
    for y in (-0.27, 0.27):   # the chocks: wedges of oak under the bilge
        box(bm, O + Vector((-0.42, y - 0.06, 0.0)), O + Vector((0.42, y + 0.06, 0.12)), 4, bevel=0.012)
    return new_obj("cellar_cask", bm, [OAK, HEAD, HOOP, CORK, POST])


def cellar_cask_upright():
    """a cask stood on end, its bung up and the vintage chalked on its head"""
    bm = bmesh.new()
    c = O + Vector((0, 0, 0.46))
    cask_body(bm, c, 0.92, 0.34, 0.41, "Z", 0, 1, 2)
    cyl(bm, c + Vector((0.14, 0.05, 0.43)), 0.04, 0.03, 3, seg=10)
    for k in range(3):   # chalk strokes: the year
        box(bm, c + Vector((-0.18 + k * 0.07, -0.14, 0.425)), c + Vector((-0.165 + k * 0.07, -0.02, 0.432)), 4)
    return new_obj("cellar_cask_upright", bm, [OAK_UP, HEAD, HOOP, CORK, CHALK])


def cask_rack():
    """a cask laid in the rack wall: its head flush with the front, cradled on beams, dark behind"""
    bm = bmesh.new()
    c = O + Vector((0, -0.02, 0.5))
    cask_body(bm, c, 0.96, 0.4, 0.46, "Y", 0, 1, 2, hoops=(0.06, 0.3))
    cyl(bm, c + Vector((0.0, 0.47, -0.22)), 0.03, 0.025, 3, seg=10, axis="Y")   # the tap hole, plugged
    for x in (0.02, 0.98):   # the rack's posts and cradle rails
        box(bm, Vector((x - 0.025, -1, 0)), Vector((x + 0.025, 0, 0.06)), 4, bevel=0.008)
    box(bm, Vector((0.0, -1, 0)), Vector((1.0, -0.96, 1.0)), 4)
    return new_obj("cask_rack", bm, [OAK, HEAD, HOOP, CORK, RACK, BACK])


def bottle(bm, base, mi_glass, mi_seal, length=0.6, r=0.075, broken=False):
    """a wine bottle lying neck out along +y from `base` (the punt end)"""
    prof = [(0.0, 0.0), (r * 0.85, 0.0), (r, 0.03), (r, length * 0.62), (r * 0.62, length * 0.74), (r * 0.36, length * 0.82)]
    if broken:
        prof += [(r * 0.33, length * 0.86)]
    else:
        prof += [(r * 0.33, length * 0.97), (r * 0.4, length * 0.98), (r * 0.4, length)]
    lathe(bm, prof, base, mi_glass, 16, "Y")
    if not broken:
        cyl(bm, Vector(base) + Vector((0, length - 0.03, 0)), r * 0.43, 0.04, mi_seal, seg=12, axis="Y")


def bottle_rack():
    """a rack of laid-down bottles, three by three in a dark oak lattice: green glass necks, wax seals, one empty
    cell, one broken neck"""
    bm = bmesh.new()
    box(bm, Vector((0, -1, 0)), Vector((1, -0.94, 1)), 4)                      # dark behind
    for k in range(4):   # the lattice
        t = 0.02 + k * 0.32
        box(bm, Vector((t - 0.02, -0.96, 0)), Vector((t + 0.02, -0.0, 1)), 0, bevel=0.006)
        box(bm, Vector((0, -0.96, t - 0.02)), Vector((1, -0.0, t + 0.02)), 0, bevel=0.006)
    cells = [(i, j) for i in range(3) for j in range(3)]
    empty, broke = (2, 0), (0, 2)
    for i, j in cells:
        if (i, j) == empty:
            continue
        x, z = 0.18 + i * 0.32, 0.18 + j * 0.32
        g = 1 if (i * 7 + j * 3) % 4 == 0 else 2
        bottle(bm, Vector((x + 0.01 * ((i + j) % 2), -0.93, z - 0.07 + 0.075)), g, 3, length=0.88, r=0.072, broken=(i, j) == broke)
    return new_obj("bottle_rack", bm, [RACK, BOTTLE_DARK, BOTTLE, SEAL, BACK])


def lamp_body(bm, c, top):
    """amber glass in an iron cage, a stepped cap, a ring on top, its chain up to `top`"""
    cyl(bm, c + Vector((0, 0, 0.04)), 0.11, 0.3, 1, seg=16)                       # the glass
    cyl(bm, c, 0.16, 0.04, 0, seg=16)                                           # the foot
    cyl(bm, c + Vector((0, 0, 0.34)), 0.17, 0.04, 0, seg=16, r2=0.13)            # the cap, stepped
    cyl(bm, c + Vector((0, 0, 0.38)), 0.12, 0.06, 0, seg=16, r2=0.05)
    for k in range(6):   # the cage bars
        a = k * math.pi / 3
        p = c + Vector((math.cos(a) * 0.14, math.sin(a) * 0.14, 0.03))
        tube(bm, [p, p + Vector((math.cos(a) * 0.015, math.sin(a) * 0.015, 0.16)), p + Vector((0, 0, 0.32))], 0.012, 0, sides=5)
    tube(bm, ring(c + Vector((0, 0, 0.19)), 0.145, "Z", 24), 0.01, 0, sides=5, closed=True)
    tube(bm, [c + Vector((0, 0, 0.42)), c + Vector((0, 0, 0.49))], 0.018, 0, sides=6)      # the finial into the ring
    tube(bm, ring(c + Vector((0, 0, 0.53)), 0.05, "Y", 16), 0.012, 0, sides=5, closed=True)   # the ring
    tube(bm, [c + Vector((0, 0, 0.58)), c + Vector((0, 0, 0.62))], 0.015, 0, sides=5)       # the hook up to the chain
    if top.z - c.z > 0.66:
        links(bm, c + Vector((0, 0, 0.6)), top, 0, w=0.06, r=0.014)


def cellar_lamp():
    """a vintner's lamp hanging on its chain"""
    bm = bmesh.new()
    lamp_body(bm, O + Vector((0, 0, 0.22)), O + Vector((0, 0, 1.0)))
    return new_obj("cellar_lamp", bm, [IRON, AMBER])


def cellar_sconce():
    """the same lamp on a wall bracket: a riveted iron plate on the wall, a scrolled arm out over the lamp, a stay
    under it back to the plate"""
    bm = bmesh.new()
    wall = O + Vector((0, -0.47, 0))
    box(bm, wall + Vector((-0.1, -0.03, 0.37)), wall + Vector((0.1, 0.01, 0.87)), 0, bevel=0.012)   # the plate
    for z in (0.42, 0.82):
        for x in (-0.06, 0.06):
            ellipsoid(bm, wall + Vector((x, 0.005, z)), (0.018, 0.012, 0.018), 0, seg=8)
    tip = O + Vector((0, 0.05, 0.9))
    tube(bm, [wall + Vector((0, 0, 0.78)), wall + Vector((0, 0.2, 0.86)), wall + Vector((0, 0.4, 0.9)), tip], 0.02, 0, sides=6)
    tube(bm, [wall + Vector((0, 0, 0.48)), wall + Vector((0, 0.16, 0.6)), wall + Vector((0, 0.3, 0.78)), wall + Vector((0, 0.38, 0.88))], 0.014, 0, sides=6)
    tube(bm, ring(wall + Vector((0, 0.14, 0.72)), 0.05, "X", 14), 0.01, 0, sides=5, closed=True)    # the scroll
    tube(bm, [tip, tip + Vector((0, 0.06, 0.0)), tip + Vector((0, 0.08, 0.05))], 0.018, 0, sides=6)
    lamp_body(bm, tip + Vector((0, 0, -0.85)), tip)
    return new_obj("cellar_sconce", bm, [IRON, AMBER])


def cellar_chain():
    bm = bmesh.new()
    links(bm, O + Vector((0, 0, 0)), O + Vector((0, 0, 1.0)), 0, w=0.075, r=0.02)
    return new_obj("cellar_chain", bm, [IRON])


def cellar_grille_post():
    bm = bmesh.new()
    cyl(bm, O, 0.04, 1.0, 0, seg=10)
    for z in (0.0, 0.94):
        cyl(bm, O + Vector((0, 0, z)), 0.06, 0.06, 0, seg=10)
    return new_obj("cellar_grille_post", bm, [IRON])


def cellar_grille_side():
    """bars from the post to the north edge: two uprights, rails at the foot, the waist and the head, a rivet at
    each crossing"""
    bm = bmesh.new()
    for y in (-0.33, -0.16):
        cyl(bm, Vector((0.5, y, 0.0)), 0.028, 1.0, 0, seg=8)
    for z in (0.08, 0.5, 0.9):
        box(bm, Vector((0.48, -0.5, z - 0.025)), Vector((0.52, 0.0, z + 0.025)), 0, bevel=0.006)
        for y in (-0.33, -0.16):
            ellipsoid(bm, Vector((0.5, y, z)), (0.04, 0.03, 0.03), 0, seg=8)
    return new_obj("cellar_grille_side", bm, [IRON])


def cask_fence_post():
    """a rough-hewn oak post, its top cut on a slant"""
    bm = bmesh.new()
    vs = box(bm, O + Vector((-0.08, -0.08, 0)), O + Vector((0.08, 0.08, 1.0)), 0, bevel=0.018)
    displace(vs, 0.008, 9.0, 3)
    box(bm, O + Vector((-0.095, -0.095, 0.9)), O + Vector((0.095, 0.095, 0.95)), 1, bevel=0.008)   # an iron cap band
    return new_obj("cask_fence_post", bm, [POST, HOOP])


def cask_fence_side():
    bm = bmesh.new()
    for z in (0.3, 0.75):
        vs = box(bm, Vector((0.44, -0.5, z - 0.06)), Vector((0.56, 0.0, z + 0.06)), 0, bevel=0.015)
        displace(vs, 0.006, 9.0, int(z * 10))
    return new_obj("cask_fence_side", bm, [OakRail])


def _grate(bm, z0, z1, mi_frame, mi_rivet):
    """a riveted iron grate three pixels thick: a frame round five slots"""
    def B(lo, hi, mi, bv=0.006):
        box(bm, lo, hi, mi, bevel=bv)
    B((0, -1, z0), (1, -0.92, z1), mi_frame)
    B((0, -0.08, z0), (1, 0, z1), mi_frame)
    B((0, -1, z0), (0.08, 0, z1), mi_frame)
    B((0.92, -1, z0), (1, 0, z1), mi_frame)
    for k in range(5):
        x = 0.17 + k * 0.165
        B((x - 0.03, -0.92, z0 + 0.02), (x + 0.03, -0.08, z1 - 0.02), mi_frame, 0.008)
    for x in (0.04, 0.96):
        for y in (-0.96, -0.5, -0.04):
            B((x - 0.018, y - 0.018, z1 - 0.004), (x + 0.018, y + 0.018, z1 + 0.012), mi_rivet, 0.006)


def sluice_grate_bottom():
    bm = bmesh.new()
    _grate(bm, 0.0, 0.1875, 0, 1)
    return new_obj("sluice_grate_bottom", bm, [IRON, HOOP])


def sluice_grate_top():
    bm = bmesh.new()
    _grate(bm, 0.8125, 1.0, 0, 1)
    return new_obj("sluice_grate_top", bm, [IRON, HOOP])


def sluice_grate_open():
    """swung up against the south side of its block, as vanilla's open trapdoor stands"""
    bm = bmesh.new()
    _grate(bm, 0.0, 0.1875, 0, 1)
    rot = Matrix.Rotation(math.pi / 2, 4, "X")
    for v in bm.verts:
        p = rot @ v.co            # (y, z) -> (-z, y)
        v.co = Vector((p.x, p.y - 0.8125, p.z + 1.0))
    return new_obj("sluice_grate_open", bm, [IRON, HOOP])


def cellar_coffer():
    """a cask-oak coffer bound in rusted iron: a rounded lid, studded straps, a heavy hasp"""
    bm = bmesh.new()
    box(bm, O + Vector((-0.44, -0.33, 0.0)), O + Vector((0.44, 0.33, 0.56)), 0, bevel=0.02)
    lid = lathe(bm, [(0.0, -0.44), (0.33, -0.44), (0.33, 0.44), (0.0, 0.44)], O + Vector((0, 0, 0.56)), 0, 24, "X")
    for rg in lid:   # half a cylinder: the lower half flattened onto the box
        for v in rg:
            if v.co.z < O.z + 0.56:
                v.co.z = O.z + 0.56
            v.co.z = O.z + 0.56 + (v.co.z - O.z - 0.56) * 0.55
    for x in (-0.3, 0.0, 0.3):   # the straps, over the lid and down the front
        box(bm, O + Vector((x - 0.04, -0.345, 0.0)), O + Vector((x + 0.04, 0.345, 0.58)), 1, bevel=0.005)
        tube(bm, [O + Vector((x, -0.34 + 0.68 * t, 0.56 + 0.18 * math.sin(t * math.pi) + 0.01)) for t in (k / 10 for k in range(11))],
             0.012, 1, sides=4)
        for z in (0.1, 0.3, 0.5):
            ellipsoid(bm, O + Vector((x, 0.35, z)), (0.016, 0.012, 0.016), 1, seg=6)
    box(bm, O + Vector((-0.07, 0.33, 0.36)), O + Vector((0.07, 0.36, 0.56)), 1, bevel=0.008)   # the hasp
    tube(bm, ring(O + Vector((0, 0.39, 0.33)), 0.035, "X", 12), 0.01, 1, sides=4, closed=True)
    return new_obj("cellar_coffer", bm, [OAK_UP, HOOP])


def cooper_bench():
    """the cooper's bench: a heavy split-log top on splayed legs, a hoop driver and mallet on it, a hoop leaning"""
    bm = bmesh.new()
    vs = box(bm, O + Vector((-0.46, -0.2, 0.42)), O + Vector((0.46, 0.2, 0.52)), 0, bevel=0.025)
    displace(vs, 0.006, 8.0, 5)
    for sx in (-1, 1):
        for sy in (-1, 1):
            tube(bm, [O + Vector((sx * 0.36, sy * 0.12, 0.44)), O + Vector((sx * 0.43, sy * 0.19, 0.0))], 0.035, 0, sides=7)
    tube(bm, [O + Vector((-0.2, 0.0, 0.54)), O + Vector((0.12, 0.05, 0.56))], 0.022, 0, sides=6)       # the mallet's haft
    cyl(bm, O + Vector((0.12, -0.04, 0.56)), 0.05, 0.16, 0, seg=12, axis="Y")                            # its head
    box(bm, O + Vector((-0.38, -0.12, 0.52)), O + Vector((-0.22, -0.06, 0.55)), 1, bevel=0.004)          # the hoop driver
    tube(bm, [O + Vector((-0.3, -0.09, 0.55)), O + Vector((-0.3, -0.09, 0.66))], 0.014, 0, sides=5)
    tube(bm, ring(O + Vector((0.3, 0.24, 0.29)), 0.27, "X", 28), 0.012, 2, sides=5, closed=True)  # a hoop stood against it
    return new_obj("cooper_bench", bm, [POST, IRON, HOOP])


def wine_spill():
    """wine run out across the flags from a dropped bottle: a thin glossy pool, the bottle's neck and shards"""
    bm = bmesh.new()
    pts = []
    for k in range(28):
        t = k * 2 * math.pi / 28
        r = 0.36 + 0.09 * noise.noise(Vector((math.cos(t) * 1.7, math.sin(t) * 1.7, 4.0))) + 0.05 * math.sin(3 * t)
        pts.append(O + Vector((math.cos(t) * r, math.sin(t) * r * 0.85, 0.004)))
    vs = [bm.verts.new(p) for p in pts]
    bm.faces.new(vs).material_index = 0
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bottle(bm, O + Vector((0.12, -0.02, 0.05)), 1, 2, length=0.42, r=0.05, broken=True)
    for k in range(5):   # shards
        a = k * 1.3
        c = O + Vector((math.cos(a) * 0.22, math.sin(a) * 0.18, 0.006))
        box(bm, c - Vector((0.025, 0.012, 0)), c + Vector((0.025, 0.012, 0.006)), 1, rot=Matrix.Rotation(a, 3, "Z"))
    return new_obj("wine_spill", bm, [WINE, BOTTLE, SEAL])


OakRail = POST
MAKE = [(cellar_cask, (256, 256)), (cellar_cask_upright, (256, 256)), (cask_rack, (256, 256)), (bottle_rack, (256, 256)),
        (cellar_lamp, (128, 128)), (cellar_sconce, (128, 128)), (cellar_chain, (64, 64)), (cellar_grille_post, (64, 64)), (cellar_grille_side, (64, 64)),
        (cask_fence_post, (64, 64)), (cask_fence_side, (64, 64)), (sluice_grate_bottom, (128, 128)), (sluice_grate_top, (128, 128)),
        (sluice_grate_open, (128, 128)), (cellar_coffer, (256, 256)), (cooper_bench, (256, 256)), (wine_spill, (128, 128))]
run(MAKE, GLOWS, "cellar_props")
