"""Every staff style with a shape of its own, so it can be told apart by silhouette with the colour taken away (StaffSpells.Style).

    black    hard and directional: thin, angled, a dark core and a rim of one colour
    white    round and rising: soft curves, slow, warm, nothing with a point on it
    summon   a crack in the world: black slits with a rim, and what climbs out of them

Easy on the eyes: nothing large is lit flat, white only as thin lines, the mass of an effect is dark or mid-value and the light sits on
its edges, and the size of an effect goes with what it does.

    blender -b -P tools/blender/vfx_styles.py -- OUT_DIR [names...]      -> OUT_DIR/<name>.png (OUT_DIR must be a full path)
"""
import math
import os
import sys

import bpy
from mathutils import Euler, Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import vfx_black as B
import vfx_concepts as V
import vfx_mage as M

W, H, SAMPLES = 640, 360, 48
GOLD, PALE, LEAF = V.lin(0xD8A850), V.lin(0xFFE8C0), V.lin(0x88D898)
SOUL, SOUL_HOT = V.lin(0x8A28C0), V.lin(0xD8A0F8)


def path(a, b, high, n=40):
    return [Vector(a).lerp(Vector(b), i / (n - 1)) + Vector((0, 0, high * math.sin(i / (n - 1) * math.pi))) for i in range(n)]


def motes(pts, r, rgb, strength=7, every=2):
    for i, p in enumerate(pts):
        if i % every == 0:
            M.ball(p, r * (0.6 + 0.4 * math.sin(i * 1.7) ** 2), rgb, strength)


def fig(x, y, scale=1.0, sink=0.0, yaw=0):
    before = set(bpy.context.scene.objects)
    V.figure((x, y), "mob", yaw)
    for o in set(bpy.context.scene.objects) - before:
        o.scale = tuple(s * scale for s in o.scale)
        l = o.location
        o.location = (x + (l.x - x) * scale, y + (l.y - y) * scale, l.z * scale - sink)


def tear(x, y, high, wide, seed, base=0.0):
    """a rip in the world: a tall thin lens of nothing with a lit edge, leaning a little, torn along both sides"""
    R = M.rnd(seed)
    lean = R.uniform(-0.12, 0.12)
    rows = [[], []]
    for i in range(34):
        t = i / 33
        w = wide * math.sin(t * math.pi) ** 0.8
        for row, side in zip(rows, (-1, 1)):
            row.append(Vector((x + lean * t * high + side * (w + w * 0.28 * R.uniform(-1, 1)), y, base + t * high)))
    B.grid(rows, V.solid("ink", V.lin(0x030205), 1.0))
    for row in rows:
        M.tube(row, 0.011, SOUL_HOT, 6)
        M.tube(row, 0.04, SOUL, 2)
    for i in range(4):
        M.burn((x + R.uniform(-0.1, 0.1), y - 0.1, base + high * (0.12 + i * 0.1)), 0.32, M.SOUL, 5, density=22, scale=3, seed=seed + i)
    V.light((x, y - 0.6, base + high * 0.5), SOUL, 30, 0.4)


def ground_crack(x, y, reach, seed, n=7):
    R = M.rnd(seed)
    for i in range(n):
        a = i / n * math.tau + R.uniform(-0.3, 0.3)
        end = (x + math.cos(a) * reach * R.uniform(0.6, 1), y + math.sin(a) * reach * R.uniform(0.6, 1), 0.03)
        V.bolt((x, y, 0.03), end, SOUL, jag=0.22, segs=9, width=0.03, seed=seed + i, strength=4)


def mist(x, y, wide, rgb, n=5, seed=1, high=0.25, density=1.2):
    R = M.rnd(seed)
    for i in range(n):
        V.puff((x + R.uniform(-wide, wide), y + R.uniform(-wide, wide), high), wide * R.uniform(0.5, 0.8), rgb, density=density, squash=0.35, seed=seed + i)


def ribbon(pts, wide, mat):
    """a flat strip of light that follows a path"""
    up = Vector((0, 0, wide))
    return B.grid([[Vector(q) - up for q in pts], [Vector(q) + up for q in pts]], mat)


def trail(head, pal, n, length, r, seed, stretch=2.5):
    R = M.rnd(seed)
    for i in range(n):
        k = (i + 1) / n
        at = head - Vector((k * length, R.uniform(-1, 1) * 0.16 * k, R.uniform(-1, 1) * 0.16 * k))
        B.black_fire(at, r * (1 - k * 0.7) * R.uniform(0.85, 1.15), pal=pal, strength=5, seed=seed + i, stretch=(stretch, 0.8, 0.8))


# ------------------------------------------------------------------ black

def fx_bolt():
    """a needle: long, thin, fast, a burning point with forks of light running back along it"""
    M.caster(staff=M.STORM[1])
    head = Vector((1.8, 0, M.HEIGHT))
    M.comet(head, M.STORM, r=0.24, length=3.6, strength=12, seed=3, tongues=7)
    R = M.rnd(6)
    for i in range(5):
        a = head - Vector((R.uniform(0.3, 2.8), 0, 0))
        V.bolt(a, a + Vector((-0.8, R.uniform(-0.6, 0.6), R.uniform(-0.6, 0.6))), M.STORM[2], jag=0.1, segs=7, width=0.008, seed=i, strength=5)
    M.embers(head - Vector((1.6, 0, 0)), 14, 1.3, M.STORM[1], 2, up=0, strength=5)
    M.husk()
    V.light(head, M.STORM[1], 10, 0.5)
    M.scene()


def fx_orb():
    """a heavy ball on a slow arc, dark, ringed, a smear of smoke behind it, and the place it will land marked"""
    tip = M.caster(staff=M.FIRE[1])
    land = (3.4, 0, 0.03)
    top = path(tip, land, 1.8)
    at = top[21]
    for i in range(3, 20, 3):
        V.puff(top[i], 0.16 + i * 0.016, V.lin(0x181210), density=5, glow_rgb=M.FIRE[1], glow=0.6, seed=i)
    B.black_fire(at, 0.82, pal=M.FIRE, strength=5, seed=5)
    V.ring(at, 1.25, 0.012, M.FIRE[2], 6, noise=2, rot=(0.5, 0.3, 0))
    V.ring(at, 1.42, 0.008, M.FIRE[1], 5, noise=2, rot=(-0.7, 0.2, 0.4))
    M.embers(at, 22, 1.5, M.FIRE[2], 4, up=0.2, strength=5)
    V.ring(Vector(land), 1.5, 0.012, M.FIRE[1], 5, noise=0)
    V.disc(land, 1.5, M.FIRE[0], 0.25)
    M.husk()
    V.light(at, M.FIRE[1], 12, 0.8)
    M.scene()


def fx_rune():
    """flat and quiet, thin lines under a low mist, and thorns already pushing up through it"""
    M.caster(staff=M.ROT[1])
    M.sigil((1.0, 0, 0.03), 2.1, M.ROT[0], M.ROT[1], seed=7, strength=2.2)
    mist(1.0, 0, 1.3, V.lin(0x223018), 6, 4, 0.2, 1.4)
    mat = M.ice_mat(M.ROT[1], M.ROT[0])
    R = M.rnd(4)
    for i in range(9):
        a = i / 9 * math.tau
        d = Vector((math.cos(a) * 0.25, math.sin(a) * 0.25, 1)).normalized()
        M.shard((1 + math.cos(a) * 1.9, math.sin(a) * 1.9, 0), d, R.uniform(0.35, 0.8), 0.08, mat)
    V.light((1, 0, 0.5), M.ROT[1], 14, 0.9)
    V.camera((0.6, 0, 0.6), -40, 26, 9.5, lens=40)


def fx_lance():
    """one straight line through everything, and a spear of ice growing along it, breaking out of what it passes"""
    M.caster(staff=M.ICE[1])
    a, b = Vector((-2.9, 0, M.HEIGHT)), Vector((6.2, 0, M.HEIGHT))
    M.tube([a, b], 0.13, M.ICE[0], 1.5)
    M.tube([a, b], 0.018, M.ICE[2], 7)
    mat = M.ice_mat(M.ICE[1], M.ICE[0])
    R = M.rnd(5)
    for x in (1.6, 4.2):
        M.husk(x)
        for i in range(11):
            d = Vector((1, R.uniform(-1, 1) * 0.7, R.uniform(-1, 1) * 0.7)).normalized()
            M.shard((x - 0.5, 0, M.HEIGHT), d, R.uniform(0.7, 1.5), R.uniform(0.05, 0.1), mat)
    M.shard((-1.0, 0, M.HEIGHT), Vector((1, 0, 0)), 9.0, 0.09, mat)
    for x in (1.6, 4.2):
        V.puff((x, 0, M.HEIGHT), 0.7, V.lin(0x8AB0D0), density=0.8, seed=int(x), squash=0.8)
    M.embers(Vector((1.6, 0, M.HEIGHT)), 14, 0.9, M.ICE[2], 3, strength=5)
    M.scene(cx=0.6)


def crescent(at, a, pal, seed):
    """a solid curved blade of dark with one lit edge, and torn fire streaming off its back"""
    flat = Euler((0, 0, 0))
    B.arc(at, 1.5, a - 1.2, 2.4, 0.3, flat, V.glow_mat(pal[0], 1.4, soft=False))
    B.arc(at + Vector((math.cos(a), math.sin(a), 0)) * 0.27, 1.5, a - 1.2, 2.4, 0.03, flat, V.glow_mat(pal[2], 5, soft=False))
    R = M.rnd(seed)
    for i in range(7):
        b = a + (i / 6 - 0.5) * 1.9
        p = at + Vector((math.cos(b), math.sin(b), 0)) * 1.15
        M.burn(p, 0.2, pal, 5, density=16, scale=3, seed=seed + i, stretch=(1.8, 0.7, 0.5))


def fx_fan():
    """three torn crescents opening out flat, like a thrown hand of cards"""
    M.caster(staff=M.VOID[1])
    for i, a in enumerate((-0.42, 0, 0.42)):
        d = Vector((math.cos(a), math.sin(a), 0))
        crescent(Vector((-3.2, 0, M.HEIGHT)) + d * 3.0, a, M.VOID, 3 + i * 12)
    M.embers(Vector((1.2, 0, M.HEIGHT)), 18, 2.4, M.VOID[2], 5, up=0.1, strength=5)
    M.husk()
    V.camera((0.4, 0, 1.0), -70, 26, 9.5, lens=38)


def fx_fall():
    """from the sky: a great burning spear coming down, smoke behind it, the ground lit under it, the next two marked"""
    M.caster(staff=M.HOST[1])
    at = Vector((2.5, 0, 3.0))
    M.burn(at, 0.62, M.HOST, 12, density=30, scale=2.6, seed=3, stretch=(1, 1, 3.4))
    B.tongue(at + Vector((0, 0, -1.5)), (0.04, 0, -1), 1.6, 0.34, 4, pal=M.HOST, strength=5)
    for i in range(8):
        V.puff(at + Vector((-0.12 * i, 0, 1.8 + i * 0.5)), 0.55 + i * 0.14, V.lin(0x1A1014), density=4, glow_rgb=M.HOST[1], glow=0.9 / (i + 1), seed=i)
    V.ring(Vector((2.8, 0, 0.03)), 1.3, 0.014, M.HOST[2], 6, noise=0)
    V.disc((2.8, 0, 0.03), 1.3, M.HOST[1], 0.35)
    for x, y in ((1.0, 1.5), (3.2, -1.9)):
        V.ring(Vector((x, y, 0.03)), 0.8, 0.009, M.HOST[1], 4, noise=0)
    M.husk(2.8)
    M.embers(at, 26, 1.8, M.HOST[2], 7, up=0.6, strength=5)
    V.light(at, M.HOST[1], 30, 0.8)
    V.light((2.8, -1, 0.6), M.HOST[1], 16, 0.8)
    V.camera((1.4, 0, 2.0), -40, 8, 10, lens=36)


# ------------------------------------------------------------------ white

def fx_circle():
    """a lotus of soft light opening round the feet, and slow motes turning up out of it"""
    M.caster(0, 0, staff=GOLD)
    B.crown((0, 0, 0.03), 0.5, 1.8, 1.1, B.sheet_mat(GOLD, PALE, 1.6), 3)
    M.shaft((0, 0, 0), 1.0, 3.6, GOLD, 0.8)
    V.ring(Vector((0, 0, 0.03)), 1.85, 0.009, GOLD, 4, noise=0)
    for ph in (0, 2.1, 4.2):
        motes(M.helix((0, 0, 0.5), (0, 0, 3.0), 1.2, 1.0, ph, n=46), 0.032, PALE, 4, every=3)
    V.light((0, -1.2, 1), GOLD, 14, 0.8)
    V.camera((0, 0, 1.0), -30, 14, 7.8, lens=40)


def fx_rain():
    """a soft green-lit cloud overhead and long slow drops under it, landing in rings"""
    M.caster(-3.2, 0, staff=LEAF)
    M.caster(1.2, 0.5, staff=LEAF)
    R = M.rnd(8)
    for i in range(7):
        a, r = i / 7 * math.tau, 1.3
        V.puff((1 + math.cos(a) * r, math.sin(a) * r, 3.9), 1.15, V.lin(0x8AA890), density=2.0, glow_rgb=LEAF, glow=0.5, squash=0.45, seed=i)
    M.shaft((1, 0, 0), 2.0, 3.6, LEAF, 0.35)
    for i in range(52):
        a, r = R.uniform(0, math.tau), 2.1 * math.sqrt(R.random())
        p = Vector((1 + math.cos(a) * r, math.sin(a) * r, R.uniform(0.2, 3.3)))
        V.streak(p, (0, 0, -1), R.uniform(0.25, 0.5), 0.012, LEAF, 4)
        M.ball(p, 0.03, PALE, 4)
    for i in range(7):
        V.ring(Vector((1 + R.uniform(-1.7, 1.7), R.uniform(-1.6, 1.6), 0.03)), R.uniform(0.15, 0.45), 0.006, LEAF, 4, noise=0)
    V.light((1, 0, 2.6), LEAF, 16, 1.2)
    V.camera((0.4, 0, 1.8), -35, 6, 11, lens=38)


def fx_mend():
    """a broad silk ribbon of light from you, winding up the one you're mending"""
    tip = M.caster(-3.0, 0, staff=GOLD)
    M.caster(1.6, 0, staff=PALE)
    wind = M.helix((1.6, 0, 0.1), (1.6, 0, 2.5), 0.66, 2.6, 0, n=120)
    mat = B.sheet_mat(GOLD, PALE, 2.2, streak=14.0)
    ribbon(wind, 0.13, mat)
    ribbon(path(tip, wind[-1], 0.5, 60), 0.04, mat)
    motes(wind, 0.03, PALE, 4, every=11)
    M.shaft((1.6, 0, 0), 0.8, 3.0, GOLD, 0.7)
    V.ring(Vector((1.6, 0, 0.03)), 0.85, 0.009, GOLD, 4, noise=0)
    V.light((1.6, -0.9, 1.2), GOLD, 10, 0.6)
    V.camera((-0.6, 0, 1.2), -36, 10, 8.2, lens=40)


def fx_spring():
    """a low pool of light with mist on it, and soft sheets welling up and folding over"""
    M.caster(-2.8, 0, staff=LEAF)
    V.disc((1, 0, 0.03), 1.5, LEAF, 0.22)
    B.crown((1, 0, 0.03), 0.15, 0.85, 2.0, B.sheet_mat(LEAF, PALE, 1.8), 9)
    B.crown((1, 0, 0.03), 0.6, 1.5, 0.7, B.sheet_mat(LEAF, PALE, 1.2), 4)
    V.ring(Vector((1, 0, 0.04)), 1.55, 0.01, PALE, 4, noise=0)
    mist(1, 0, 1.1, V.lin(0x70A080), 6, 3, 0.25, 0.7)
    for i in range(7):
        a = i / 7 * math.tau
        motes(path((1, 0, 1.2), (1 + math.cos(a) * 1.4, math.sin(a) * 1.4, 0.1), 1.3)[10:], 0.03, PALE, 4, every=5)
    V.light((1, 0, 0.7), LEAF, 12, 0.9)
    V.camera((0.4, 0, 0.9), -35, 13, 8.4, lens=40)


def fx_flask():
    """a real glass flask turning through the air, and where one has landed, a soft opened flower with mist rolling out"""
    tip = M.caster(-3.2, 0, staff=GOLD)
    glass = V.solid("flask", V.lin(0x2A5038), 0.2)
    at = Vector((-0.4, 0, 2.5))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24, location=at)
    bpy.context.object.data.materials.append(glass)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.26, location=at + Vector((0.08, 0, 0.28)), rotation=(0, 0.3, 0))
    bpy.context.object.data.materials.append(glass)
    M.ball(at, 0.18, LEAF, 3)
    ribbon(path(tip, at, 0.5, 50), 0.02, B.sheet_mat(GOLD, PALE, 1.4))
    land = (3.0, 0, 0.04)
    B.crown(land, 0.3, 1.6, 1.3, B.sheet_mat(LEAF, PALE, 1.8), 5)
    mist(3.0, 0, 1.2, V.lin(0x80B090), 6, 5, 0.25, 0.8)
    M.embers(Vector((3, 0, 0.9)), 18, 1.4, PALE, 6, up=1.0, strength=4)
    V.ring(Vector(land), 1.8, 0.009, GOLD, 4, noise=0)
    V.light((3, 0, 0.8), LEAF, 12, 0.9)
    V.camera((0.2, 0, 1.2), -36, 10, 9.5, lens=38)


# ------------------------------------------------------------------ summon

def fx_blades():
    """three tall rips in the air, a fighter stepping through each, blade first"""
    M.caster(-3.4, 0, staff=SOUL)
    for x, y, s in ((0.5, 1.4, 1), (1.3, -1.2, 22), (2.4, 0.1, 43)):
        tear(x + 0.55, y + 0.25, 3.6, 0.42, s)
        fig(x, y, 1, 0.1, -90)
    V.camera((0.4, 0, 1.5), -40, 9, 10, lens=38)


def fx_mages():
    """rings hanging at shoulder height, a caster standing on each, off the ground, soul fire between their hands"""
    M.caster(-3.2, 0, staff=SOUL)
    for x, y, s in ((1.0, 1.3, 2), (1.6, -1.3, 3)):
        M.sigil((x, y, 0.75), 0.9, V.lin(0x301040), SOUL, seed=s, strength=2.2)
        M.burn((x, y, 0.55), 0.55, M.SOUL, 3, density=12, scale=3, seed=s, stretch=(1.3, 1.3, 0.35))
        fig(x, y, 0.85, -0.75, -90)
        B.black_fire((x - 0.6, y, 1.9), 0.2, pal=M.SOUL, strength=5, seed=s)
        V.light((x, y, 0.5), SOUL, 14, 0.4)
    V.camera((0, 0, 1.1), -46, 11, 9.5, lens=38)


def fx_brute():
    """the ground splits under one huge thing: heavy, low, wide, soul fire pouring out of the crack round it"""
    M.caster(-3.8, 0, staff=SOUL)
    ground_crack(1.4, 0, 3.2, 7, n=10)
    fig(1.4, 0, 2.1, 1.0, -90)
    R = M.rnd(3)
    for i in range(14):
        a = R.uniform(0, math.tau)
        M.burn((1.4 + math.cos(a) * 1.0, math.sin(a) * 1.0, R.uniform(0.1, 0.9)), 0.42, M.SOUL, 3.5, density=20, scale=3, seed=i)
    rock = V.solid("rock", V.lin(0x2A2830), 0.9)
    for i in range(14):
        a = R.uniform(0, math.tau)
        x, y, z = 1.4 + math.cos(a) * 1.9, math.sin(a) * 1.9, R.uniform(0.15, 1.9)
        V.box(x, y, z, x + R.uniform(0.12, 0.34), y + R.uniform(0.12, 0.34), z + R.uniform(0.12, 0.34), rock)
    mist(1.4, 0, 2.0, V.lin(0x282030), 6, 7, 0.3, 1.2)
    V.light((0.2, -1, 0.5), SOUL, 40, 0.5)
    V.camera((0.2, 0, 1.5), -46, 8, 10.5, lens=38)


def fx_swarm():
    """a dozen pinpricks in a creeping black mist, something small out of each"""
    M.caster(-3.4, 0, staff=SOUL)
    R = M.rnd(5)
    mist(1.1, 0, 1.9, V.lin(0x141020), 8, 5, 0.18, 2.5)
    for i in range(12):
        x, y = R.uniform(-0.6, 2.8), R.uniform(-2.0, 2.0)
        V.ring(Vector((x, y, 0.2)), 0.17, 0.008, SOUL_HOT, 6, noise=0)
        fig(x, y, 0.42, 0.0, R.uniform(-130, -50))
        M.burn((x, y, 0.3), 0.14, M.SOUL, 4, density=14, scale=4, seed=i, stretch=(1, 1, 2))
    V.light((1, 0, 1), SOUL, 24, 1.0)
    V.camera((0.2, 0, 0.8), -44, 16, 9.5, lens=38)


def fx_band():
    """a straight rank: one rip along the ground, and behind each of them a tear, standing up in line"""
    M.caster(-3.6, 0, staff=SOUL)
    V.bolt((1.0, -2.6, 0.03), (1.0, 2.6, 0.03), SOUL, jag=0.1, segs=18, width=0.03, seed=4, strength=4)
    for i, y in enumerate((-1.9, -0.65, 0.65, 1.9)):
        fig(1.1, y, 1, 0.45 if i % 2 else 0.15, -90)
        tear(1.75, y, 2.9, 0.26, 10 + i * 9)
    mist(1.2, 0, 1.8, V.lin(0x181420), 6, 8, 0.2, 1.5)
    V.camera((0.2, 0, 1.3), -56, 11, 10.5, lens=38)


EFFECTS = {"bolt": fx_bolt, "orb": fx_orb, "rune": fx_rune, "lance": fx_lance, "fan": fx_fan, "fall": fx_fall,
           "circle": fx_circle, "rain": fx_rain, "mend": fx_mend, "spring": fx_spring, "flask": fx_flask,
           "blades": fx_blades, "mages": fx_mages, "brute": fx_brute, "swarm": fx_swarm, "band": fx_band}

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    os.makedirs(argv[0], exist_ok=True)
    for name, fn in EFFECTS.items():
        if argv[1:] and name not in argv[1:]:
            continue
        sc = V.reset()
        sc.render.resolution_x, sc.render.resolution_y, sc.cycles.samples = W, H, SAMPLES
        fn()
        sc.render.filepath = os.path.join(argv[0], name + ".png")
        bpy.ops.render.render(write_still=True)
        print("rendered", name, flush=True)
