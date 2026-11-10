"""The Kiln-Father's Hearth (concept, Cycles): Ossric's arena, where Veyra sends a party with the Founder's Brand.
A colossal dead forge floating in an ash-red void: a round hearth floor of black iron plates cracked with glowing seams,
the Brand burned into its middle where the party lands; a channel of molten slag round it; four anvils the size of
houses standing on the hearth (cover, and things to be thrown into); a low kiln-brick rim; beyond it, kiln chimneys
rising off spurs of rock and smoking, slag spilling off the edge in falls; nothing overhead, open to the void. 120 blocks
into the channel; ash and embers falling forever; slag dripping off the island's rock root into nothing. Ossric
(13 blocks tall) for scale, and a party of four.
  blender -b -P tools/blender/ossric_arena.py -- [wide|inside] [fast]  ->  tools/renders/ossric_arena/hearth_<shot>.png"""
import os, sys, math, random
import bpy, bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
_m = open(os.path.join(HERE, "meteor_fall.py"), encoding="utf-8").read()
exec(_m.split("GATE = (0.62")[0])                                    # scene, node helpers, pix/glow/box/point/vol_cube
HEAT = (1.0, 0.36, 0.08)
HEAT_HOT = (1.0, 0.72, 0.38)
rs = random.Random(31)
exec("def smoke_mat" + _m.split("def smoke_mat")[1].split("\n# ================================================================ the crater")[0])
_a = open(os.path.join(HERE, "arena_ring.py"), encoding="utf-8").read()
exec("def pixb" + _a.split("def pixb")[1].split("# ---------------------------------------------------------------- the sky")[0])
exec("def mesh_vox" + _a.split("def mesh_vox")[1].split("MATS = {")[0])

SHOT = next((a for a in ARGS if a in ("wide", "inside")), "inside")
OUT = os.path.join(HERE, "..", "renders", "ossric_arena")
os.makedirs(OUT, exist_ok=True)
sc.view_settings.exposure = -0.2

# ---------------------------------------------------------------- the void: ash-red, darker overhead, a glow far below
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
up = mth(wt, "MINIMUM", mth(wt, "MAXIMUM", mth(wt, "MULTIPLY", zz, vb=2.5), vb=0.0), vb=1.0)
down = mth(wt, "MINIMUM", mth(wt, "MAXIMUM", mth(wt, "MULTIPLY", zz, vb=-2.0), vb=0.0), vb=1.0)
sky = mix(wt, up, (0.035, 0.012, 0.006), (0.006, 0.003, 0.003))
sky = mix(wt, down, sky, (0.14, 0.035, 0.008))
nz = N(wt, "ShaderNodeTexNoise", Scale=3.0, Detail=8.0, Roughness=0.6)
L(wt, tc.outputs["Generated"], nz.inputs["Vector"])
sky = mix(wt, mth(wt, "MULTIPLY", mth(wt, "POWER", nz.outputs["Fac"], vb=3.0), vb=1.2), sky, (0.07, 0.022, 0.01))
bg = N(wt, "ShaderNodeBackground", Strength=1.0)
L(wt, sky, bg.inputs["Color"])
L(wt, bg.outputs[0], wo.inputs["Surface"])
# a dim warm key from above-left, so the iron reads at all
sun = bpy.data.objects.new("key", bpy.data.lights.new("key", "SUN"))
sun.data.energy = 0.35
sun.data.color = (1.0, 0.62, 0.45)
sun.data.angle = math.radians(8)
sun.rotation_euler = (Vector((0.4, 0.6, -0.7))).to_track_quat("-Z", "Y").to_euler()
sc.collection.objects.link(sun)

# ---------------------------------------------------------------- the hearth, block by block
R_FLOOR, R_SLAG, R_RIM = 60, 65, 69
vox = {}
# the fissures: random walks out from near the middle, forking, never a pattern
CRACKS = set()
for i in range(10):
    a = i / 10 * math.tau + rs.uniform(-0.2, 0.2)
    stack = [(math.cos(a) * 7, math.sin(a) * 7, a, 1.0)]
    while stack:
        x, y, a, life = stack.pop()
        for _ in range(int(rs.uniform(28, 52) * life)):
            a += rs.gauss(0, 0.28)
            x, y = x + math.cos(a), y + math.sin(a)
            if math.hypot(x, y) > 58:
                break
            CRACKS.add((int(math.floor(x)), int(math.floor(y))))
            if rs.random() < 0.035 and life > 0.4:
                stack.append((x, y, a + rs.choice((-1, 1)) * rs.uniform(0.5, 1.0), life * 0.6))
SPILLS = (0.6, 2.4, 3.9, 5.3)                                           # where the slag pours off the edge


def put(x, y, z, k):
    vox[(x, y, z)] = k


for x in range(-R_RIM - 1, R_RIM + 2):
    for y in range(-R_RIM - 1, R_RIM + 2):
        r = math.hypot(x + 0.5, y + 0.5)
        a = math.atan2(y + 0.5, x + 0.5)
        if r > R_RIM + 0.5:
            continue
        # the rock root it hangs on: deep in the middle, ragged
        bot = -int(40 * (1 - (r / (R_RIM + 1)) ** 1.5) + 4 * math.sin(a * 5) + rs.random() * 2) - 3
        for z in range(bot, -2):
            put(x, y, z, "rock")
        if r < R_FLOOR:
            # black iron plates, 5 blocks a side, their seams one block of darker iron; glowing cracks running out
            seam = (x % 5 == 0) or (y % 5 == 0)
            crack = (x, y) in CRACKS
            put(x, y, -1, "crack" if crack else "seam" if seam else "plate")
            put(x, y, -2, "rock")
        elif r < R_SLAG:
            put(x, y, -3, "slag")                                     # the channel, two blocks down
            put(x, y, -4, "rock")
            if rs.random() < 0.05:
                put(x, y, -3, "crust")
        else:
            # the kiln-brick rim, waist high, with a coping and gaps
            seg = (a * R_RIM) % 11.0
            spill = any(abs(((a - g) + math.pi) % math.tau - math.pi) * R_RIM < 3 for g in SPILLS)
            if spill:
                put(x, y, -3, "slag")                                  # the channel runs out over the edge here
                put(x, y, -4, "rock")
                continue
            hh = 2 if seg > 1.4 else 4                                 # a pier every 11 blocks
            for z in range(-2, hh):
                put(x, y, z, "trim" if z == hh - 1 else "brick")
# the Brand burned into the middle: a ring and the founder's mark (three bars crossing)
for x in range(-6, 7):
    for y in range(-6, 7):
        r = math.hypot(x + 0.5, y + 0.5)
        a = math.atan2(y + 0.5, x + 0.5)
        bar = any(abs((x + 0.5) * math.sin(t) - (y + 0.5) * math.cos(t)) < 0.6 for t in (0, math.pi / 3, 2 * math.pi / 3)) and r < 4.6
        if abs(r - 5.2) < 0.55 or bar:
            put(x, y, -1, "brand")


def anvil(cx, cy, turn):
    """an anvil the size of a house: a stepped foot, a waist, a long face with a horn; 9 high"""
    ca, sa = math.cos(turn), math.sin(turn)

    def p(u, v, z, k):
        put(int(round(cx + u * ca - v * sa)), int(round(cy + u * sa + v * ca)), z, k)
    for u in range(-5, 6):
        for v in range(-3, 4):
            for z in range(0, 2):
                p(u, v, z, "iron")
    for u in range(-3, 4):
        for v in range(-2, 3):
            for z in range(2, 5):
                p(u, v, z, "iron")
    for u in range(-7, 8):
        for v in range(-3, 4):
            for z in range(5, 9):
                p(u, v, z, "steel" if z == 8 else "iron")
    for u in range(8, 13):                                                # the horn, tapering
        t = (u - 7) / 6
        for v in range(-3, 4):
            for z in range(5, 9):
                if abs(v) <= 3 * (1 - t) + 0.3 and (8 - z) <= 3.5 * (1 - t) + 0.3:
                    p(u, v, z, "steel" if z == 8 else "iron")
    for u in range(-7, -5):                                               # the heel's hardy hole
        p(u, 0, 8, "crack")


for i in range(6):
    a = i / 6 * math.tau + math.pi / 6
    anvil(math.cos(a) * 40, math.sin(a) * 40, a + math.pi / 2 + (0.2 if i % 2 else -0.2))


def chimney(cx, cy, h, base_z):
    """a kiln stack on its rock spur: square, brick, banded, a flared lip, glowing at the mouth"""
    for z in range(base_z - 18, base_z):
        rr = 5 * (1 - (base_z - z) / 20)
        for x in range(int(cx - rr - 2), int(cx + rr + 3)):
            for y in range(int(cy - rr - 2), int(cy + rr + 3)):
                if math.hypot(x - cx, y - cy) < rr + 2:
                    put(x, y, z, "rock")
    for z in range(base_z, base_z + h):
        half = 3 if z < base_z + h - 3 else 4
        if z < base_z + 4:
            half = 4
        for x in range(int(cx) - half, int(cx) + half + 1):
            for y in range(int(cy) - half, int(cy) + half + 1):
                edge = abs(x - int(cx)) == half or abs(y - int(cy)) == half
                if not edge:
                    if z == base_z + h - 1:
                        put(x, y, z - 1, "mouth")
                    continue
                band = (z - base_z) % 12 == 0
                put(x, y, z, "trim" if band or z == base_z + h - 1 else "brick")


STACKS = []
for i in range(9):
    a = i / 9 * math.tau + 0.4 + rs.uniform(-0.15, 0.15)
    d = rs.uniform(84, 100)
    h = rs.randint(55, 90)
    bz = rs.randint(-14, -4)
    cx, cy = math.cos(a) * d, math.sin(a) * d
    chimney(cx, cy, h, bz)
    STACKS.append(Vector((cx + 0.5, cy + 0.5, bz + h)))

MATS = {
    "plate": pixb("plate", (0.055, 0.05, 0.05), (0.10, 0.09, 0.085), rough=0.6),
    "seam": pixb("seam", (0.025, 0.022, 0.022), (0.045, 0.04, 0.04), rough=0.7),
    "iron": pixb("iron", (0.07, 0.065, 0.065), (0.13, 0.12, 0.115), rough=0.55),
    "steel": pixb("steel", (0.32, 0.31, 0.3), (0.46, 0.45, 0.43), rough=0.3),
    "brick": pixb("kbrick", (0.16, 0.07, 0.045), (0.25, 0.11, 0.07), bricks=(0.06, 0.03, 0.02)),
    "trim": pixb("ktrim", (0.08, 0.07, 0.07), (0.13, 0.12, 0.11), bricks=(0.03, 0.03, 0.03)),
    "rock": pixb("rock", (0.05, 0.04, 0.04), (0.11, 0.09, 0.085)),
    "crust": pix("crust", (0.03, 0.02, 0.02), (0.07, 0.05, 0.045), rough=0.95, cracks=(HEAT, 4.0)),
    "slag": glow("slag", HEAT, 9.0),
    "crack": glow("crack", HEAT, 2.2),
    "brand": glow("brand", HEAT_HOT, 14.0),
    "mouth": glow("mouth", HEAT, 12.0),
}
mesh_vox(vox, MATS)
print("voxels", len(vox))

# the slag's light, round the channel
for i in range(24):
    a = i / 24 * math.tau
    point("slag%d" % i, (math.cos(a) * 62.5, math.sin(a) * 62.5, 0.5), HEAT, 12000, 3)
point("brand", (0, 0, 1.0), HEAT_HOT, 2500, 3)
for s in STACKS:
    point("stack", tuple(s + Vector((0, 0, 1))), HEAT, 30000, 4)

# ---------------------------------------------------------------- the slag falls: the channel spilling off the edge
bm = bmesh.new()
for g in SPILLS:
    for k in range(30):
        t = k / 29
        d = R_RIM + 1 + 6 * t ** 0.6
        zt = -3 - 70 * t
        wdt = 2.6 * (1 - 0.5 * t)
        cx, cy = math.cos(g) * d, math.sin(g) * d
        box(bm, cx - wdt, cy - wdt, zt - 1.4, cx + wdt, cy + wdt, zt + 1.4)
    point("fall%.1f" % g, (math.cos(g) * (R_RIM + 4), math.sin(g) * (R_RIM + 4), -12), HEAT_HOT, 40000, 5)
obj("falls", bm, glow("fall", HEAT_HOT, 20))

# smoke off the stacks
for i, s in enumerate(STACKS):
    m = puff_mat()
    for k in range(7):
        t = k / 6
        r = 3 + 9 * t
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        ob = obj("stack%d_%d" % (i, k), bm, m)
        ob.location = s + Vector((10 * t * t, 4 * t, 4 + 30 * t))
        ob.scale = (r, r, r * 0.85)
        ob.color = (0.6 * (1 - t), 0, 0, 1)

# slag dripping off the root into the void
bm = bmesh.new()
for i in range(50):
    a = rs.uniform(0, math.tau)
    d = rs.uniform(30, 66)
    x, y = math.cos(a) * d, math.sin(a) * d
    z0 = -6 - (1 - d / 69) * 36
    ln = rs.uniform(10, 40)
    box(bm, x - 0.25, y - 0.25, z0 - ln, x + 0.25, y + 0.25, z0)
obj("drips", bm, glow("drip", HEAT, 10))

# ash and embers, everywhere
bm_a, bm_e = bmesh.new(), bmesh.new()
for i in range(2500):
    p = Vector((rs.uniform(-140, 140), rs.uniform(-140, 140), rs.uniform(-10, 110)))
    q = rs.uniform(0.04, 0.1)
    box(bm_e if rs.random() < 0.12 else bm_a, p.x - q, p.y - q, p.z - q, p.x + q, p.y + q, p.z + q)
obj("ash", bm_a, pix("ash", (0.25, 0.23, 0.22), (0.35, 0.33, 0.31)))
obj("embers", bm_e, glow("ember", HEAT, 12))

# far forge-wreckage drifting in the void: broken anvils, gears of rock
bm = bmesh.new()
for i in range(16):
    a = rs.uniform(0, math.tau)
    d = rs.uniform(170, 340)
    c = Vector((math.cos(a) * d, math.sin(a) * d, rs.uniform(-50, 50)))
    s = rs.uniform(3, 12)
    for k in range(int(s * 2.5)):
        p = c + Vector((rs.uniform(-s, s), rs.uniform(-s, s), -abs(rs.gauss(0, s * 0.6))))
        q = rs.uniform(1.2, 3.5)
        box(bm, p.x - q, p.y - q, p.z - q, p.x + q, p.y + q, p.z + q)
obj("wreckage", bm, MATS["rock"])

# ---------------------------------------------------------------- Ossric for scale (13 tall), and the party
M_OSS = pix("oss", (0.05, 0.045, 0.045), (0.11, 0.1, 0.095), rough=0.5, cracks=(HEAT, 3.0))
ox, oy = 0.0, 26.0
bm = bmesh.new()
box(bm, ox - 2.6, oy - 1.4, 0, ox - 0.6, oy + 1.4, 5.5)                 # legs
box(bm, ox + 0.6, oy - 1.4, 0, ox + 2.6, oy + 1.4, 5.5)
box(bm, ox - 3.4, oy - 2.2, 5.2, ox + 3.4, oy + 2.0, 10.5)              # the furnace body
box(bm, ox - 5.2, oy - 1.8, 8.6, ox + 5.2, oy + 1.8, 11.4)              # shoulders
box(bm, ox - 1.4, oy - 1.6, 10.6, ox + 1.4, oy + 1.2, 13.0)             # head, sunk between them
box(bm, ox - 6.4, oy - 1.0, 3.4, ox - 4.6, oy + 1.0, 9.6)               # arms
box(bm, ox + 4.6, oy - 1.0, 3.4, ox + 6.4, oy + 1.0, 9.6)
box(bm, ox + 5.0, oy - 0.4, -0.2, ox + 5.8, oy + 0.4, 6.5)              # the hammer's haft, its head on the floor
box(bm, ox + 3.6, oy - 1.6, 0, ox + 7.2, oy + 1.6, 2.6)
obj("ossric", bm, M_OSS)
bm = bmesh.new()
box(bm, ox - 2.2, oy - 2.25, 6.2, ox + 2.2, oy - 2.15, 9.4)             # the furnace door, open and burning
obj("oss_furnace", bm, glow("furnace", HEAT_HOT, 30))
bm = bmesh.new()
box(bm, ox - 0.9, oy - 1.65, 11.8, ox - 0.3, oy - 1.55, 12.2)
box(bm, ox + 0.3, oy - 1.65, 11.8, ox + 0.9, oy - 1.55, 12.2)
obj("oss_eyes", bm, glow("oeyes", HEAT_HOT, 40))
point("furnace", (ox, oy - 4, 7.8), HEAT, 7000, 2)
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

# heat haze over it all
m, nt, out = new_mat("haze")
vol = N(nt, "ShaderNodeVolumePrincipled", Density=0.0011, Anisotropy=0.4)
vol.inputs["Color"].default_value = (1.0, 0.7, 0.55, 1)
L(nt, vol.outputs[0], out.inputs["Volume"])
vol_cube("haze", m, (0, 0, 30), (130, 130, 40))

CAMS = {"wide": ((-95, -187, 120), (0, 4, -8), 30), "inside": ((0.5, -18.0, 2.0), (0.0, 40.0, 12.0), 17)}
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
sc.render.filepath = os.path.abspath(os.path.join(OUT, "hearth_%s%s.png" % (SHOT, "_fast" if FAST else "")))
bpy.ops.render.render(write_still=True)
print("WROTE", sc.render.filepath)
