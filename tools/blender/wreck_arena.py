"""The Graveyard of Ships (concept, Cycles): the Wreck-Mother's arena, where Veyra sends a party for the Drowned Fire.
A floor 124 blocks across made of a dozen wrecked decks the sea has jammed together: each wreck's planks run their own
way, hull rails between them, holes stove in where the black water shows, masts lying across it for cover, cannons
and capstans; round its edge the broken hull sides, low, with gaps where the waves wash in. Four masts still stand at
the rim with torn sails and cold lanterns. Out in the black storm-sea a ring of ship's ribs sticks up out of the water
like a fence (nothing overhead: open to the storm). The Wreck-Mother, a colossal crab-thing wearing an upturned galleon
for a shell, rises out of the sea at the north edge with its claws on the rim. A party of four on the compass rose in
the middle, for scale.
  blender -b -P tools/blender/wreck_arena.py -- [wide|inside] [fast]  ->  tools/renders/wreck_arena/wreck_<shot>.png"""
import os, sys, math, random
import bpy, bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
_m = open(os.path.join(HERE, "meteor_fall.py"), encoding="utf-8").read()
exec(_m.split("GATE = (0.62")[0])                                    # scene, node helpers, pix/glow/box/point/vol_cube
rs = random.Random(53)
exec("def smoke_mat" + _m.split("def smoke_mat")[1].split("\n# ================================================================ the crater")[0])
_a = open(os.path.join(HERE, "arena_ring.py"), encoding="utf-8").read()
exec("def pixb" + _a.split("def pixb")[1].split("# ---------------------------------------------------------------- the sky")[0])
exec("def mesh_vox" + _a.split("def mesh_vox")[1].split("MATS = {")[0])

SHOT = next((a for a in ARGS if a in ("wide", "inside")), "inside")
OUT = os.path.join(HERE, "..", "renders", "wreck_arena")
os.makedirs(OUT, exist_ok=True)
sc.view_settings.exposure = 0.3
COLD = (0.45, 0.78, 1.0)
FOAM = (0.85, 0.9, 0.95)

# ---------------------------------------------------------------- the storm sky: slate and bruise, a pale tear near the horizon
w = bpy.data.worlds.new("w")
sc.world = w
w.use_nodes = True
wt = w.node_tree
for n in list(wt.nodes):
    wt.nodes.remove(n)
wo = N(wt, "ShaderNodeOutputWorld")
tc = N(wt, "ShaderNodeTexCoord")
sep = N(wt, "ShaderNodeSeparateXYZ")
L(wt, tc.outputs["Generated"], sep.inputs[0])
zz = sep.outputs["Z"]
up = mth(wt, "MINIMUM", mth(wt, "MAXIMUM", mth(wt, "MULTIPLY", zz, vb=2.2), vb=0.0), vb=1.0)
sky = mix(wt, up, (0.05, 0.065, 0.085), (0.012, 0.016, 0.024))
nz = N(wt, "ShaderNodeTexNoise", Scale=2.2, Detail=10.0, Roughness=0.62)
L(wt, tc.outputs["Generated"], nz.inputs["Vector"])
sky = mix(wt, mth(wt, "MULTIPLY", mth(wt, "POWER", nz.outputs["Fac"], vb=4.0), vb=2.2), sky, (0.09, 0.11, 0.14))
bg = N(wt, "ShaderNodeBackground", Strength=1.0)
L(wt, sky, bg.inputs["Color"])
L(wt, bg.outputs[0], wo.inputs["Surface"])
sun = bpy.data.objects.new("key", bpy.data.lights.new("key", "SUN"))
sun.data.energy = 0.9
sun.data.color = (0.62, 0.72, 0.9)
sun.data.angle = math.radians(12)
sun.rotation_euler = (Vector((-0.3, 0.7, -0.55))).to_track_quat("-Z", "Y").to_euler()
sc.collection.objects.link(sun)

# ---------------------------------------------------------------- the deck of wrecks, block by block
R_DECK, R_RIM = 62, 66
SEA = -4
vox = {}


def put(x, y, z, k):
    vox[(x, y, z)] = k


# a dozen wrecks jammed together: each owns a wedge-ish patch (nearest of 12 seeds), its planks running its own way
SEEDS = [(rs.uniform(-50, 50), rs.uniform(-50, 50), rs.uniform(0, math.pi)) for _ in range(12)]
SEEDS[0] = (0.0, 0.0, 0.0)


def wreck(x, y):
    d = sorted(((x - sx) ** 2 + (y - sy) ** 2, i) for i, (sx, sy, _) in enumerate(SEEDS))
    return d[0][1], math.sqrt(d[1][0]) - math.sqrt(d[0][0])


HOLES = [(rs.uniform(-48, 48), rs.uniform(-48, 48), rs.uniform(2.0, 4.2)) for _ in range(10)]
HOLES = [h for h in HOLES if math.hypot(h[0], h[1]) > 14]
GAPS = (0.9, 2.2, 3.4, 4.6, 5.7)                                          # where the waves wash in over the rim

for x in range(-R_RIM - 1, R_RIM + 2):
    for y in range(-R_RIM - 1, R_RIM + 2):
        r = math.hypot(x + 0.5, y + 0.5)
        a = math.atan2(y + 0.5, x + 0.5)
        if r > R_RIM + 0.5:
            continue
        # the hulls under it all, down into the sea
        for z in range(SEA - 8 + int(3 * math.sin(a * 3 + r * 0.1)), -1):
            if z < -2 and r < R_RIM - 3 and z > SEA - 6:
                continue                                                   # hollow inside (only the skin shows)
            put(x, y, z, "hull")
        hole = any(math.hypot(x - hx, y - hy) < hr for hx, hy, hr in HOLES)
        if r < R_DECK:
            if hole:
                put(x, y, SEA, "water")
                for z in range(SEA + 1, -1):
                    vox.pop((x, y, z), None)
                vox.pop((x, y, -2), None)
                continue
            i, edge = wreck(x, y)
            if edge < 1.2 and i != 0 and (int(r) % 9) > 1:
                put(x, y, -1, "rail")
                put(x, y, 0, "rail")                                       # a hull rail between two decks, gaps to cross
                continue
            t = SEEDS[i][2]
            stripe = int(math.floor((x + 0.5) * math.cos(t) + (y + 0.5) * math.sin(t)))
            put(x, y, -1, ("plank", "plank2", "plank3")[(stripe + i) % 3])
        else:
            gap = any(abs(((a - g) + math.pi) % math.tau - math.pi) * R_RIM < 4 for g in GAPS)
            if gap:
                put(x, y, -1, "plank3")
                continue
            hh = int(2 + 5 * (0.5 + 0.5 * math.sin(a * 7 + 1.3)) + 2 * (0.5 + 0.5 * math.sin(a * 19)))
            for z in range(-1, hh):
                put(x, y, z, "rail" if z == hh - 1 else "hull")
# the compass rose where the party lands: brass inlay, eight points
for x in range(-7, 8):
    for y in range(-7, 8):
        r = math.hypot(x + 0.5, y + 0.5)
        a = math.atan2(y + 0.5, x + 0.5)
        pt = abs(((a * 4 / math.pi) + 0.5) % 1 - 0.5)                 # 0 on each of the 8 points
        if abs(r - 6.2) < 0.55 or (r < 6.0 and pt < 0.12 * (6.0 - r) / 6.0 + 0.02):
            put(x, y, -1, "brass")


def log(p0, p1, rad, k):
    """a mast lying across the deck: a round log of blocks"""
    p0, p1 = Vector(p0), Vector(p1)
    n = int((p1 - p0).length)
    for i in range(n + 1):
        c = p0.lerp(p1, i / max(1, n))
        for dx in range(-int(rad) - 1, int(rad) + 2):
            for dz in range(-int(rad) - 1, int(rad) + 2):
                if dx * dx + dz * dz <= rad * rad + 0.3:
                    d = (p1 - p0).normalized()
                    side = Vector((-d.y, d.x, 0))
                    q = c + side * dx + Vector((0, 0, dz))
                    put(int(round(q.x)), int(round(q.y)), int(round(q.z)), k)


for i in range(3):
    a = rs.uniform(0, math.tau)
    c = Vector((math.cos(a) * rs.uniform(22, 40), math.sin(a) * rs.uniform(22, 40), 1))
    d = Vector((math.cos(a + 1.6), math.sin(a + 1.6), 0)) * rs.uniform(12, 16)
    log(c - d, c + d, 1.4, "mast")


def cannon(cx, cy, turn):
    ca, sa = math.cos(turn), math.sin(turn)
    for u in range(-2, 5):
        for v in (-1, 0, 1):
            for z in (0, 1):
                if u > 1 and (abs(v) > 0 or z > 1):
                    continue
                put(int(round(cx + u * ca - v * sa)), int(round(cy + u * sa + v * ca)), z, "iron" if u > -1 else "hull")


def capstan(cx, cy):
    for x in range(-2, 3):
        for y in range(-2, 3):
            if x * x + y * y <= 5:
                for z in range(0, 3):
                    put(cx + x, cy + y, z, "hull" if z < 2 else "rail")


for i in range(8):
    a = i / 8 * math.tau + rs.uniform(-0.2, 0.2)
    d = rs.uniform(30, 48)
    (cannon if i % 2 else (lambda cx, cy, t: capstan(int(cx), int(cy))))(math.cos(a) * d, math.sin(a) * d, a + math.pi)

# the masts still standing at the rim, with their yards
MASTS = []
for i in range(4):
    a = i / 4 * math.tau + 0.5
    d = 57
    cx, cy = int(math.cos(a) * d), int(math.sin(a) * d)
    h = rs.randint(40, 55)
    lean = Vector((math.cos(a), math.sin(a), 0)) * 0.08
    for z in range(-1, h):
        o = lean * z
        for dx in (0, 1):
            for dy in (0, 1):
                put(cx + dx + int(o.x), cy + dy + int(o.y), z, "mast")
    for yz in (int(h * 0.55), int(h * 0.85)):
        o = lean * yz
        side = Vector((-math.sin(a), math.cos(a), 0))
        for k in range(-9, 10):
            q = Vector((cx + o.x, cy + o.y, 0)) + side * k
            put(int(round(q.x)), int(round(q.y)), yz, "mast")
    MASTS.append((Vector((cx + lean.x * h, cy + lean.y * h, h)), a))
    # the crow's nest
    o = lean * int(h * 0.92)
    for dx in range(-2, 4):
        for dy in range(-2, 4):
            if dx in (-2, 3) or dy in (-2, 3):
                put(cx + dx + int(o.x), cy + dy + int(o.y), int(h * 0.92), "rail")

# the ring of ship's ribs out in the sea, curving up and out (never over the arena)
for i in range(16):
    a = i / 16 * math.tau + rs.uniform(-0.08, 0.08)
    d0 = rs.uniform(84, 100)
    h = rs.randint(18, 34)
    for side in (-0.06, 0.06):
        for z in range(SEA - 2, SEA + h):
            t = (z - SEA) / h
            d = d0 + 10 * t * t                                             # curls outward as it rises
            aa = a + side * (1 - 0.6 * t)
            for k in (0, 1):
                put(int(math.cos(aa) * (d + k)), int(math.sin(aa) * (d + k)), z, "rib")

MATS = {
    "plank": pixb("plank", (0.13, 0.1, 0.07), (0.2, 0.155, 0.11), bricks=(0.06, 0.045, 0.03)),
    "plank2": pixb("plank2", (0.09, 0.08, 0.065), (0.15, 0.13, 0.1), bricks=(0.045, 0.04, 0.03)),
    "plank3": pixb("plank3", (0.11, 0.075, 0.05), (0.17, 0.12, 0.08), bricks=(0.05, 0.035, 0.025)),
    "rail": pixb("rail", (0.04, 0.035, 0.03), (0.07, 0.06, 0.05)),
    "hull": pixb("hull", (0.045, 0.045, 0.042), (0.085, 0.085, 0.08), bricks=(0.025, 0.025, 0.025)),
    "mast": pixb("mast", (0.06, 0.05, 0.04), (0.1, 0.085, 0.065)),
    "rib": pixb("rib", (0.12, 0.12, 0.11), (0.2, 0.2, 0.18)),
    "iron": pixb("iron", (0.03, 0.03, 0.035), (0.06, 0.06, 0.07), rough=0.5),
    "brass": pixb("brass", (0.3, 0.2, 0.07), (0.45, 0.32, 0.12), rough=0.35),
    "water": pixb("pool", (0.004, 0.008, 0.012), (0.01, 0.02, 0.028), rough=0.08),
}
mesh_vox(vox, MATS)
print("voxels", len(vox))

# ---------------------------------------------------------------- the sea: black, heaving, lit cold
bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, SEA + 0.6))
sea = bpy.context.active_object
try:
    om = sea.modifiers.new("ocean", "OCEAN")
    om.geometry_mode = "GENERATE"
    om.resolution = 10 if FAST else 16
    om.spatial_size = 220
    om.repeat_x = om.repeat_y = 4
    om.wave_scale = 2.4
    om.choppiness = 1.4
    om.wind_velocity = 26
    sea.location = (-440, -440, SEA + 0.6)
except Exception as ex:
    print("ocean", ex)
    sea.scale = (600, 600, 1)
m, nt, out = new_mat("sea")
bs = N(nt, "ShaderNodeBsdfPrincipled", Roughness=0.08)
bs.inputs["Base Color"].default_value = (0.004, 0.01, 0.016, 1)
L(nt, bs.outputs[0], out.inputs["Surface"])
sea.data.materials.append(m)

# foam where the waves wash over the gaps, and breaking round the hull
bm = bmesh.new()
for g in GAPS:
    for k in range(60):
        d = rs.uniform(R_RIM - 2, R_RIM + 6)
        aa = g + rs.uniform(-4, 4) / R_RIM
        z = rs.uniform(-1, 1.5)
        q = rs.uniform(0.2, 0.7)
        box(bm, math.cos(aa) * d - q, math.sin(aa) * d - q, z, math.cos(aa) * d + q, math.sin(aa) * d + q, z + q * 0.6)
for k in range(500):
    aa = rs.uniform(0, math.tau)
    d = rs.uniform(R_RIM + 0.5, R_RIM + 5)
    z = SEA + rs.uniform(0.2, 1.4)
    q = rs.uniform(0.15, 0.5)
    box(bm, math.cos(aa) * d - q, math.sin(aa) * d - q, z, math.cos(aa) * d + q, math.sin(aa) * d + q, z + q * 0.5)
obj("foam", bm, pix("foam", (0.5, 0.55, 0.6), (0.75, 0.8, 0.85), rough=0.6))

# torn sails on the standing masts, cold lanterns
SAIL = pix("sail", (0.12, 0.12, 0.11), (0.22, 0.21, 0.19), rough=0.95)
for top, a in MASTS:
    side = Vector((-math.sin(a), math.cos(a), 0))
    bm = bmesh.new()
    for k in range(-8, 9):
        L_ = rs.uniform(4, 14) if abs(k) < 7 else rs.uniform(2, 6)       # ragged hem
        c = Vector((top.x, top.y, 0)) + side * k
        z0 = top.z * 0.85 / 0.92 * 0.92
        box(bm, c.x - 0.5, c.y - 0.5, top.z * 0.85 - L_, c.x + 0.5, c.y + 0.5, top.z * 0.85 - 0.5)
    obj("sail", bm, SAIL)
    point("lantern", (top.x, top.y, top.z * 0.6), COLD, 9000, 1.0)
    bm = bmesh.new()
    box(bm, top.x - 0.6, top.y - 0.6, top.z * 0.6 - 0.8, top.x + 0.6, top.y + 0.6, top.z * 0.6 + 0.8)
    obj("lantern_glass", bm, glow("lantern", COLD, 30))
for i in range(10):                                                         # lanterns along the rails
    a = rs.uniform(0, math.tau)
    d = rs.uniform(20, 58)
    point("deck_lamp", (math.cos(a) * d, math.sin(a) * d, 1.5), COLD, 1800, 0.5)
    bm = bmesh.new()
    box(bm, math.cos(a) * d - 0.4, math.sin(a) * d - 0.4, 0, math.cos(a) * d + 0.4, math.sin(a) * d + 0.4, 1.0)
    obj("deck_lamp", bm, glow("dlamp", COLD, 20))

# ---------------------------------------------------------------- the Wreck-Mother rising at the north edge
WM = pix("wm", (0.03, 0.035, 0.04), (0.07, 0.08, 0.09), rough=0.45)
SHELL = pixb("shell", (0.05, 0.045, 0.04), (0.09, 0.08, 0.065), bricks=(0.03, 0.025, 0.02))
BARN = pix("barn", (0.25, 0.26, 0.25), (0.4, 0.41, 0.38), rough=0.8)
cx, cy = 0.0, 100.0
G = 1.6                                                                     # her size
bm = bmesh.new()                                                            # the upturned galleon: keel up
for i in range(70):
    u = -35 + i
    t = abs(u) / 35.0
    half = 21 * math.sqrt(max(0.0, 1 - t ** 2.4))
    for j in range(int(half * 2)):
        v = -half + j
        top = SEA + 8 + 40 * math.sqrt(max(0.0, 1 - (v / max(half, 0.1)) ** 2)) * (1 - 0.35 * t)
        box(bm, cx + u, cy + v - 0.5, SEA + 2, cx + u + 1, cy + v + 0.5, top)
obj("wm_shell", bm, SHELL)
bm = bmesh.new()
for i in range(70):
    box(bm, cx - 35 + i, cy - 1.0, SEA + 47 - 14 * (abs(i - 35) / 35) ** 2, cx - 34 + i, cy + 1.0, SEA + 50 - 14 * (abs(i - 35) / 35) ** 2)
for k in range(600):
    u = rs.uniform(-32, 32)
    v = rs.uniform(-18, 18)
    z = SEA + 8 + rs.uniform(6, 38) * (1 - abs(u) / 40)
    q = rs.uniform(0.5, 1.6)
    box(bm, cx + u - q, cy + v - q, z, cx + u + q, cy + v + q, z + q)
obj("wm_keel_barnacles", bm, BARN)
bm = bmesh.new()
for side in (-1, 1):                                                        # the legs, bent, coming out under the hull
    for k in range(3):
        root = Vector((cx + side * 19, cy - 10 + k * 10, SEA + 6))
        knee = root + Vector((side * 18, -6 + k * 3, 20))
        foot = knee + Vector((side * 9, -9, -24))
        for p0, p1, w_ in ((root, knee, 2.8), (knee, foot, 2.0)):
            n = int((p1 - p0).length)
            for s_ in range(n + 1):
                c = p0.lerp(p1, s_ / max(1, n))
                box(bm, c.x - w_, c.y - w_, c.z - w_, c.x + w_, c.y + w_, c.z + w_)
for side in (-1, 1):                                                        # the claws, on the rim
    root = Vector((cx + side * 14, cy - 18, SEA + 14))
    elbow = Vector((side * 30, 76, 22))
    hand = Vector((side * 18, 66, 5))
    for p0, p1, w_ in ((root, elbow, 4.0), (elbow, hand, 3.4)):
        n = int((p1 - p0).length)
        for s_ in range(n + 1):
            c = p0.lerp(p1, s_ / max(1, n))
            box(bm, c.x - w_, c.y - w_, c.z - w_, c.x + w_, c.y + w_, c.z + w_)
    box(bm, hand.x - 7, hand.y - 9, hand.z - 4, hand.x + 7, hand.y + 3, hand.z + 5)          # the claw's palm
    box(bm, hand.x - 6, hand.y - 20, hand.z + 1, hand.x + 6, hand.y - 9, hand.z + 5)         # upper pincer
    box(bm, hand.x - 4.5, hand.y - 17, hand.z - 4, hand.x + 4.5, hand.y - 9, hand.z - 1)     # lower pincer
obj("wm_limbs", bm, WM)
bm = bmesh.new()
for side in (-1, 1):                                                        # eyes on stalks, under the hull's lip
    p = Vector((cx + side * 8, cy - 21, SEA + 12))
    for s_ in range(9):
        box(bm, p.x - 0.5, p.y - 0.5, p.z + s_, p.x + 0.5, p.y + 0.5, p.z + s_ + 1)
obj("wm_stalks", bm, WM)
bm = bmesh.new()
for side in (-1, 1):
    p = Vector((cx + side * 8, cy - 21, SEA + 22))
    box(bm, p.x - 1.6, p.y - 1.6, p.z - 1.6, p.x + 1.6, p.y + 1.6, p.z + 1.6)
obj("wm_eyes", bm, glow("wm_eyes", COLD, 60))
point("wm_eye_light", (cx, cy - 28, SEA + 22), COLD, 40000, 3)
bm = bmesh.new()
box(bm, cx - 10, cy - 21.3, SEA + 3, cx + 10, cy - 20.6, SEA + 10)              # the maw under the lip, glowing within
obj("wm_maw", bm, glow("wm_maw", (0.2, 0.6, 0.9), 6))

# ---------------------------------------------------------------- a far lightning bolt and the storm's rain
bm = bmesh.new()
p = Vector((-160, 260, 150))
for k in range(24):
    q = p + Vector((rs.uniform(-6, 6), rs.uniform(-3, 3), -7))
    n = int((q - p).length)
    for s_ in range(n):
        c = p.lerp(q, s_ / n)
        box(bm, c.x - 0.3, c.y - 0.3, c.z - 0.3, c.x + 0.3, c.y + 0.3, c.z + 0.3)
    p = q
obj("bolt", bm, glow("bolt", (0.8, 0.9, 1.0), 80))
point("flash", (-150, 240, 60), (0.75, 0.85, 1.0), 4.0e6, 20)
bm = bmesh.new()
for i in range(3500):
    x, y, z = rs.uniform(-130, 130), rs.uniform(-130, 160), rs.uniform(-4, 90)
    box(bm, x - 0.03, y - 0.03, z, x + 0.03, y + 0.03, z + rs.uniform(1.0, 2.2))
obj("rain", bm, pix("rain", (0.3, 0.33, 0.38), (0.45, 0.48, 0.55), rough=0.2))

# ---------------------------------------------------------------- the party on the compass rose
M_FIG = [pixb("fig%d" % i, c, tuple(min(1, x * 1.3) for x in c)) for i, c in
         enumerate(((0.22, 0.04, 0.03), (0.06, 0.07, 0.1), (0.16, 0.13, 0.07), (0.04, 0.09, 0.05)))]
M_SKIN = pixb("skin", (0.55, 0.4, 0.3), (0.62, 0.46, 0.35))
bm_s = bmesh.new()
for i, (x, y) in enumerate(((-2.5, -3.0), (1.0, -2.0), (3.5, -3.6), (-0.6, -5.0))):
    bm = bmesh.new()
    box(bm, x - 0.3, y - 0.15, 0, x + 0.3, y + 0.15, 1.5)
    box(bm, x - 0.45, y - 0.2, 0.75, x + 0.45, y + 0.2, 1.5)
    obj("fig%d" % i, bm, M_FIG[i])
    box(bm_s, x - 0.25, y - 0.25, 1.5, x + 0.25, y + 0.25, 2.0)
obj("heads", bm_s, M_SKIN)

# sea mist, low
m, nt, out = new_mat("mist")
vol = N(nt, "ShaderNodeVolumePrincipled", Density=0.0016, Anisotropy=0.3)
vol.inputs["Color"].default_value = (0.7, 0.8, 0.9, 1)
L(nt, vol.outputs[0], out.inputs["Volume"])
vol_cube("mist", m, (0, 30, 10), (170, 170, 22))

CAMS = {"wide": ((-110, -150, 95), (0, 20, -4), 28), "inside": ((0.5, -22.0, 2.2), (0.0, 70.0, 14.0), 18)}
loc, aim, lens = CAMS[SHOT]
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 6000
cam.location = loc
cam.data.lens = lens
cam.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
bloom()
sc.render.image_settings.color_depth = "8"
sc.render.filepath = os.path.abspath(os.path.join(OUT, "wreck_%s%s.png" % (SHOT, "_fast" if FAST else "")))
bpy.ops.render.render(write_still=True)
print("WROTE", sc.render.filepath)
