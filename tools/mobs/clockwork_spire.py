"""The Clockwork Spire's monsters, the Gearbound, each built by hand (tools/vox2.py). A gearwright's order built the
tower to wind the world's clock; the order is gone and the tower still runs, building more of itself. Blackened iron,
brass gone brown at the rivets, verdigris pipes, oiled leather, and the amber-orange of boiler fire behind every
grille and lens. Every one of them has a wind-up key somewhere on it: the tower winds them.

    cogling             swarm   a dog-sized brass spider: one red lens, two saw-blade mandibles, needle legs, a key in its back
    brass_sentry        guard   a tall brass automaton knight: bucket helm with a burning slit, a gear crest, a riveted
                                tower shield with a cog for a boss, a glaive with a toothed back
    steam_hulk          brute   a walking boiler: firebox in the belly, two smokestacks for shoulders, a head sunk between
                                them like a furnace door, piston arms ending in hammer fists
    tinker_adept        caster  one of the order's living engineers: leather apron and hood, brass goggles and respirator,
                                a mechanical right arm, a coil on its back that arcs, a spark rod
    clockwork_duelist   elite   slender black frame, four arms (two sabres, two daggers), a cracked clock-face mask,
                                a crown of small gears, a tattered red sash
    grand_horologe      boss    the colossus at the top: a clock for a face in a brass case under a crown of gears, a
                                caged chest with the mainspring burning in it, gear pauldrons, a piston hammer for a right
                                arm, a pendulum blade for a left, two stacks and a great key on its back

    python tools/monsterforge.py clockwork_spire --preview ; python tools/mobsheet.py clockwork_spire
"""
import math

import vox2 as X
from vox2 import C, ramp

IRON = ramp("#0a0b0d", "#121418", "#1b1e23", "#262a30", "#33383f", "#434952", "#596069")
BRASS = ramp("#2a1806", "#4a2c0c", "#6e4616", "#966222", "#bc8434", "#dcaa52", "#f2cc7a")
OLD_BRASS = ramp("#1a1008", "#2a1a0c", "#3e2812", "#56391a", "#704c22", "#8c622c")
COPPER = ramp("#0e2620", "#163a30", "#205244", "#2e6e5a", "#448c74", "#62aa90")
LEATHER = ramp("#120c08", "#1c140e", "#281c14", "#36261a", "#463222")
CLOTH = ramp("#1a0806", "#2a0e0a", "#401410", "#581c16", "#74261e", "#90342a")
SKIN = ramp("#2a1e18", "#3e2c22", "#56402e", "#6e523c", "#8a684c")
FIRE = ramp("#5a1606", "#9a2c08", "#d2520e", "#f68a1c", "#ffc24a", "#fff0b0")
LENS = ramp("#4a0404", "#8a0a08", "#d0200e", "#ff4a1c", "#ff9a6a", "#ffe0d0")
PORCELAIN = ramp("#5a5650", "#7c766c", "#9e978a", "#c0b8a8", "#dcd4c4", "#f2ece0")
SOOT = ramp("#0c0a0a", "#161212", "#221c1a", "#2e2624")


def shaders():
    return {
        "iron": X.surf(IRON, 0.5, 1.4, 0.14, 0.2, drip=(SOOT, 0.1)),
        "brass": X.surf(BRASS, 0.46, 1.4, 0.14, 0.22, rust=(COPPER, 0.12, 0.6)),
        "plate": X.surf(OLD_BRASS, 0.5, 1.4, 0.14, 0.24, stripe=6, rust=(COPPER, 0.16, 0.5), drip=(SOOT, 0.1)),
        "copper": X.surf(COPPER, 0.5, 1.3, 0.2, 0.16),
        "leather": X.surf(LEATHER, 0.5, 1.1, 0.2, 0.06),
        "cloth": X.surf(CLOTH, 0.5, 1.0, 0.2, 0.0, holes=True),
        "skin": X.wrinkled(SKIN, 0.8),
        "porcelain": X.surf(PORCELAIN, 0.56, 1.2, 0.1, 0.16, drip=(SOOT, 0.14)),
        "glow": X.glow(FIRE),
        "eye": X.glow(LENS, 0.8, 0.16),
        "lens": X.glow(LENS),
        "dark": X.dark(IRON),
    }


# ================================================================ shared brushes (shapes, not bodies)

def gear(k, part, c, r, axis="z", mat="brass", w=1.2, teeth=None, spokes=4, hub="iron", tag="gear"):
    """a cog: a rim, square teeth round it, spokes, a hub; its face across `axis`"""
    cx, cy, cz = c
    n = teeth or max(6, int(r * 1.6))
    k.ring(part, cx, cy, cz, r, w, mat, tag, n=max(8, n), axis=axis)
    for i in range(n):
        a = (i + 0.5) * 2 * math.pi / n
        u, v = math.cos(a) * (r + w * 0.9), math.sin(a) * (r + w * 0.9)
        t = w * 1.1
        p = {"z": C(cx + u, cy + v - t / 2, cz, t, t, w), "x": C(cx, cy + v - t / 2, cz + u, w, t, t),
             "y": C(cx + u, cy - w / 2, cz + v, t, w, t)}[axis]
        k.box(part, p, mat, tag=tag + "_tooth")
    for i in range(spokes):
        a = i * math.pi / spokes
        u, v = math.cos(a) * r, math.sin(a) * r
        q0 = {"z": (cx - u, cy - v, cz), "x": (cx, cy - v, cz - u), "y": (cx - u, cy, cz - v)}[axis]
        q1 = {"z": (cx + u, cy + v, cz), "x": (cx, cy + v, cz + u), "y": (cx + u, cy, cz + v)}[axis]
        k.limb(part, q0, q1, w * 0.6, mat, tag + "_spoke")
    s = max(1.0, r * 0.4)
    k.box(part, C(cx, cy - s / 2, cz, s, s, s), hub, tag=tag + "_hub")


def key(k, part, base, d, length, bow=3.0, mat="brass", tag="key"):
    """a wind-up key standing out of a back: a shaft, a collar, a butterfly bow at its end"""
    tip = tuple(base[i] + d[i] * length for i in range(3))
    k.limb(part, base, tip, 1.0, "iron", tag + "_shaft")
    k.box(part, C(base[0] + d[0] * 1.2, base[1] + d[1] * 1.2 - 0.8, base[2] + d[2] * 1.2, 2.2, 1.6, 2.2), mat, tag=tag + "_collar")
    for s in (-1, 1):
        k.blob(part, (tip[0] + s * bow * 0.8, tip[1] + bow * 0.5, tip[2]), (bow * 0.75, bow, 0.6), mat, tag + "_bow", step=0.8)
    k.box(part, C(tip[0], tip[1] - 0.4, tip[2], 2.0, 2.4, 1.2), mat, tag=tag + "_boss")


def pipe(k, part, pts, w, mat="copper", tag="pipe"):
    for a, b in zip(pts, pts[1:]):
        k.limb(part, a, b, w, mat, tag)
    for p in pts[1:-1]:
        k.box(part, C(p[0], p[1] - w * 0.7, p[2], w * 1.5, w * 1.4, w * 1.5), "brass", tag=tag + "_collar")


def spring(k, part, c, r0, r1, turns, w, mat="glow", axis="z", tag="mainspring"):
    """a coiled mainspring: a flat spiral from r0 out to r1"""
    cx, cy, cz = c
    n = int(turns * 16)
    pts = []
    for i in range(n + 1):
        t = i / n
        a = t * turns * 2 * math.pi
        r = r0 + (r1 - r0) * t
        u, v = math.cos(a) * r, math.sin(a) * r
        pts.append({"z": (cx + u, cy + v, cz), "x": (cx, cy + v, cz + u)}[axis])
    for a, b in zip(pts, pts[1:]):
        k.limb(part, a, b, w, mat, tag, group="glow" if mat in ("glow", "lens", "eye") else "lit")


def rivet_row(k, part, p0, p1, n, s=0.7, mat="iron"):
    k.rivets(part, [tuple(p0[i] + (p1[i] - p0[i]) * j / max(1, n - 1) for i in range(3)) for j in range(n)], mat, s)


def grow(k, f):
    """scale a whole monster about its feet: every box and every part's pivot"""
    parts = {id(b.part): b.part for b in k.s.boxes}
    for p in list(parts.values()):
        q = p.parent if hasattr(p, "parent") else None
        while q is not None and id(q) not in parts:
            parts[id(q)] = q
            q = getattr(q, "parent", None)
    for p in parts.values():
        p.pivot = tuple(c * f for c in p.pivot)
    for b in k.s.boxes:
        b.lo = tuple(c * f for c in b.lo)
        b.size = tuple(c * f for c in b.size)
        b.pivot = tuple(c * f for c in b.pivot)


def legs(k, nm, x, hip_y, mat_th, mat_sh, th_size, sh_size, foot, side, rots=((), (), ())):
    th = k.part("thigh_" + nm, (x, hip_y, 0), rots[0], "hips")
    knee = hip_y - th_size[1]
    sh = k.part("shin_" + nm, (x, knee, 0), rots[1], th)
    ankle = foot[1] + foot[3]
    ft = k.part("foot_" + nm, (x, ankle, 0), rots[2], sh)
    return th, sh, ft, knee, ankle


# ================================================================ the Cogling (swarm, crawler)

def cogling():
    """The tower's smallest makings swarm its gear halls: a brass spider the size of a dog, its body a riveted dome,
    one red lens in a brass bezel for a face, two saw-blade mandibles that spin, eight needle legs on brass knuckles,
    and a wind-up key turning in its back. They come in a clatter and they come in dozens."""
    k = X.Kit("cogling")
    body = k.part("body", (0, 8, 0))
    k.blob(body, (0, 9, 0), (5.6, 3.6, 6.4), "plate", "dome", step=1.0)
    k.box(body, C(0, 5.4, 0, 9.0, 1.6, 10.0), "iron", tag="belly_ring")
    for a in range(0, 360, 45):
        r = math.radians(a)
        k.box(body, C(math.cos(r) * 4.6, 6.6, math.sin(r) * 5.4, 1.0, 1.0, 1.0), "iron", tag="rivet")
    k.box(body, C(0, 12.2, 0, 1.2, 0.8, 9.0), "iron", tag="spine_seam")
    key(k, body, (0, 12.4, -1.0), (0, 1, -0.25), 3.2, bow=1.8)
    for sx in (-1, 1):                            # exhaust stubs either side, a glow in each
        k.limb(body, (sx * 4.4, 10, -4), (sx * 5.2, 12.6, -6), 1.0, "copper", "stub")
        k.box(body, C(sx * 5.2, 12.6, -6, 0.9, 0.5, 0.9), "glow", group="glow", tag="stub_glow")
    hd = k.part("head", (0, 8, 5), (("x", -6),), "body")
    k.box(hd, C(0, 6.0, 6.8, 6.0, 5.0, 3.6), "iron", tag="face")
    k.ring(hd, 0, 8.6, 8.8, 2.2, 0.9, "brass", "bezel", n=12, axis="z")
    k.box(hd, C(0, 7.2, 8.3, 3.2, 2.8, 0.8), "lens", group="glow", tag="eye")
    k.box(hd, C(0.6, 8.6, 8.75, 0.8, 0.6, 0.3), "porcelain", tag="glint")
    for sx in (-1, 1):                            # the saw mandibles
        gear(k, hd, (sx * 3.2, 5.4, 9.6), 1.8, axis="x", mat="iron", w=0.7, teeth=10, spokes=2, hub="brass", tag="saw")
        k.limb(hd, (sx * 2.4, 6.4, 7.6), (sx * 3.2, 5.4, 9.6), 0.8, "brass", "jaw_arm")
    ab = k.part("abdomen", (0, 8, -4), (), "body")
    k.blob(ab, (0, 8.4, -7.6), (4.0, 3.0, 4.0), "iron", "boiler", step=1.0)
    k.box(ab, C(0, 7.0, -11.2, 2.6, 2.0, 0.8), "glow", group="glow", tag="firebox")
    for x in (-1.2, 0, 1.2):
        k.box(ab, C(x, 6.8, -11.6, 0.4, 2.4, 0.4), "iron", tag="grille")
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, z in enumerate((4.0, 1.4, -1.4, -4.0)):
            nm = "leg_%s%d" % (s, i)
            lg = k.part(nm, (side * 4.0, 7, z), (), body)
            kn = (side * 9.4, 14.0, z * 1.4)
            ft = (side * 13.0, 0.0, z * 2.0)
            k.limb(lg, (side * 4.0, 7, z), kn, 1.1, "iron", "leg")
            k.box(lg, C(kn[0], kn[1] - 0.9, kn[2], 1.8, 1.8, 1.8), "brass", tag="knuckle")
            k.limb(lg, kn, ft, 0.8, "iron", "needle")
            k.shard(lg, (ft[0], 1.2, ft[2]), (0, -1, 0), 1.4, 0.7, mat="brass", tag="foot")
            joints[nm] = ("LL" if side > 0 else "RL") + str(i + 1)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Brass Sentry (guard)

def brass_sentry():
    """The tower's doorwardens: a brass knight seven feet tall that has never been a man. A barrel chest of plate with
    a window of turning cogs in its belly, pistons for thighs and shins, a bucket helm with one burning slit and a half
    gear for a crest; a riveted iron tower shield with a cog for its boss, and a long glaive whose back is toothed like
    a gear. It marches. It does not stop."""
    k = X.Kit("brass_sentry")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(17, 11.6, 7.6), (22, 12.4, 8.0)], "iron", "pelvis")
    k.box(hips, C(0, 21.4, 0, 13.2, 1.6, 8.8), "brass", tag="belt")
    for x in (-4.2, 0, 4.2):
        k.box(hips, C(x, 12.4, 4.4, 3.8, 6.6, 0.8), "plate", tag="tasset")
        k.rivets(hips, [(x, 18.4, 4.9)], "iron", 0.7)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.6
        th = k.part("thigh_" + nm, (x, 21, 0), (("x", -4), ("z", side * 4)), "hips")
        sh = k.part("shin_" + nm, (x, 11.4, 0), (("x", 6),), th)
        ft = k.part("foot_" + nm, (x, 2.8, 0), (("x", -2),), sh)
        k.limb(th, (x, 20, 0), (x, 12.6, 0), 2.2, "iron", "thigh_rod")                # the piston inside
        k.box(th, C(x, 14.4, 0.6, 4.8, 6.2, 5.2), "plate", tag="cuisse")
        k.box(th, C(x, 10.6, 1.2, 5.4, 2.6, 5.0), "brass", tag="knee")
        k.box(th, C(x, 11.2, 3.8, 1.6, 1.6, 0.6), "glow", group="glow", tag="knee_lamp")
        k.limb(sh, (x - side * 1.4, 10.6, -1.6), (x - side * 1.4, 4, -1.6), 1.0, "copper", "shin_piston")
        k.box(sh, C(x, 3.0, 0.4, 5.0, 7.4, 5.4), "plate", tag="greave")
        k.box(ft, C(x, 0, 1.8, 6.0, 2.8, 9.4), "iron", tag="foot")
        k.box(ft, C(x, 0.2, 6.2, 6.2, 1.6, 1.0), "brass", tag="toe_cap")
    # ---------------------------------------------------------------- torso: the barrel chest, cogs in its belly
    to = k.part("torso", (0, 22, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(22, 12.4, 8.6), (26, 15.6, 10.4), (31, 18.6, 11.4), (36, 18.0, 10.6), (38, 14.0, 9.0)], "plate", "barrel")
    k.box(to, C(0, 23.4, 4.4, 8.0, 5.6, 1.6), "dark", tag="gear_window")
    gear(k, to, (-1.6, 26.2, 5.0), 1.8, mat="brass", w=0.6, tag="belly_gear")
    gear(k, to, (2.0, 25.0, 5.0), 1.3, mat="copper", w=0.5, tag="belly_gear")
    for y in (23.0, 29.0):
        k.box(to, C(0, y, 0, 13 + (y - 23) * 0.6, 0.6, 9.4 + (y - 23) * 0.2), "iron", tag="hoop")
    for sx in (-1, 1):
        rivet_row(k, to, (sx * 5.8, 29.4, 5.6), (sx * 5.0, 36.0, 5.4), 5)
        k.box(to, C(sx * 3.2, 31, 5.6, 1.2, 5.6, 0.6), "brass", tag="rib")
    key(k, to, (0, 32, -5.6), (0, 0.35, -1), 4.0, bow=2.6)
    for side in (1, -1):                       # pauldrons: stacked plates, the top one cut like a gear's edge
        k.blob(to, (side * 9.8, 36.4, 0), (5.2, 3.2, 5.6), "plate", "pauldron", step=1.0)
        for i in range(3):
            k.box(to, C(side * (10.4 + i * 0.4), 33.4 - i * 1.7, 0, 6.4, 1.5, 9.4), "iron" if i % 2 else "plate", tag="lame")
        for z in (-3.6, -1.2, 1.2, 3.6):
            k.box(to, C(side * 10.0, 39.2, z, 1.4, 1.6, 1.4), "brass", tag="pauldron_tooth")
    # ---------------------------------------------------------------- the bucket helm, the burning slit, the gear crest
    hd = k.part("head", (0, 38, 0.4), (("x", -4),), "torso")
    k.stack(hd, 0, 0.3, [(37.6, 6.8, 7.0), (44.6, 7.2, 7.4)], "plate", "helm")
    k.box(hd, C(0, 44.4, 0.3, 7.6, 0.8, 7.8), "iron", tag="helm_band")
    k.box(hd, C(0, 41.2, 3.75, 6.4, 1.0, 0.4), "dark", tag="slit")
    k.box(hd, C(0, 41.3, 3.9, 5.2, 0.6, 0.3), "eye", group="glow", tag="eye")
    for i in range(6):
        k.box(hd, C(-2.0 + i * 0.8, 38.6, 3.75, 0.36, 1.6, 0.3), "dark", tag="breath")
    rivet_row(k, hd, (-3.2, 43.4, 3.9), (3.2, 43.4, 3.9), 5, 0.6)
    for i in range(7):                          # the half-gear crest, teeth up
        a = math.radians(i * 30)
        x, y = math.cos(a) * 3.4, 45.0 + math.sin(a) * 3.4
        k.box(hd, C(x, y - 0.7, 0.3, 1.4, 1.4, 1.2), "brass", tag="crest_tooth")
    k.box(hd, C(0, 45.0, 0.3, 6.2, 1.6, 1.0), "brass", tag="crest_base")
    k.box(hd, C(0, 45.6, 0.3, 4.2, 1.6, 1.0), "brass", tag="crest_base")
    # ---------------------------------------------------------------- arms: the tower shield, the glaive
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 10.0
        up = k.part("arm_" + nm, (x, 35, 0), (("x", -40 if side > 0 else -30), ("z", side * 8)), "torso")
        fo = k.part("fore_" + nm, (x, 26, 0), (("x", -50 if side > 0 else -70),), up)
        hn = k.part("hand_" + nm, (x, 17, 0), (), fo)
        k.limb(up, (x, 33.6, 0), (x, 26.6, 0), 2.0, "iron", "arm_rod")
        k.box(up, C(x, 27.6, 0.4, 4.6, 5.8, 4.8), "plate", tag="rerebrace")
        k.box(up, C(x, 26.0, 0, 3.2, 2.0, 3.2), "brass", tag="elbow")
        k.box(fo, C(x, 18.0, 0, 4.6, 8.0, 5.0), "plate", tag="vambrace")
        k.limb(fo, (x + side * 2.4, 24.0, -1.4), (x + side * 2.4, 19.0, -1.4), 0.8, "copper", "fore_piston")
        k.box(hn, C(x, 13.6, 0.4, 4.4, 4.0, 4.6), "iron", tag="gauntlet")
        for f in range(3):
            k.box(hn, C(x - 1.4 + f * 1.4, 12.6, 2.6, 1.0, 1.6, 1.0), "brass", tag="knuckle")
    sh = k.part("shield", (14, 17, 2), (("y", 8),), k.parts["hand_l"])
    k.box(sh, C(14.4, 2.6, 2, 1.8, 31, 15), "iron", tag="tower_shield")
    for z in (-5.4, 2, 9.4):
        k.box(sh, C(15.4, 2.6, z, 0.6, 31, 1.4), "plate", tag="shield_strap")
    for y in (3.4, 32.0):
        k.box(sh, C(15.4, y, 2, 0.6, 1.4, 15.4), "plate", tag="shield_rim")
    for y in range(6, 32, 4):
        for z in (-6.4, 10.4):
            k.box(sh, C(15.5, y, z, 0.6, 0.6, 0.6), "brass", tag="rivet")
    gear(k, sh, (15.8, 18.0, 2.0), 4.4, axis="x", mat="plate", w=1.2, teeth=10, spokes=3, hub="brass", tag="shield_cog")
    k.box(sh, C(16.2, 17.4, 2.0, 0.8, 1.6, 1.6), "glow", group="glow", tag="cog_lamp")
    # the glaive: a long haft, a broad crescent blade, its back cut in gear teeth
    gl = k.part("glaive", (-10.0, 15.6, 0.6), (("x", 80),), k.parts["hand_r"])
    k.limb(gl, (-10.0, -10, 0.6), (-10.0, 40, 0.6), 1.4, "iron", "haft")
    for y in (6, 20, 34):
        k.box(gl, C(-10.0, y, 0.6, 2.0, 1.2, 2.0), "brass", tag="haft_band")
    k.box(gl, C(-10.0, 39.6, 1.6, 1.2, 4, 4.4), "plate", tag="socket")
    for i in range(7):                          # the crescent: offset slices, widest in the middle
        y = 41 + i * 2.0
        w = 5.0 + 2.6 * math.sin(i / 6 * math.pi)
        k.box(gl, C(-10.0, y, 2.4 + w / 2 - 1.4, 1.0, 2.1, w), "iron", tag="blade")
        k.box(gl, C(-10.0, y, 2.4 + w - 1.0, 1.1, 2.1, 0.8), "brass", tag="edge")
        if i % 2 == 0:
            k.box(gl, C(-10.0, y, -0.6, 1.0, 1.2, 1.4), "brass", tag="back_tooth")
    k.shard(gl, (-10.0, 55, 3.0), (0, 1, 0.2), 4.0, 1.6, mat="iron", tag="point")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Steam Hulk (brute)

def steam_hulk():
    """The tower's haulers, a boiler that learned to walk: a riveted drum of a body with the firebox burning in its
    belly behind a grille, two smokestacks rising off its shoulders and smoking, a head sunk low between them that is
    only an iron dome with a furnace slot for a mouth, and arms that are pistons as thick as a man ending in hammer
    fists studded with bolts. The floor shakes where it goes."""
    k = X.Kit("steam_hulk")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(13, 18, 13), (20, 20, 14)], "iron", "pelvis")
    for x in (-6, 0, 6):
        k.box(hips, C(x, 10, 6.6, 5.0, 6.0, 1.0), "plate", tag="apron_plate")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.4
        th = k.part("thigh_" + nm, (x, 18, 0), (("x", -8), ("z", side * 10)), "hips")
        sh = k.part("shin_" + nm, (x, 9.8, 0), (("x", 12),), th)
        ft = k.part("foot_" + nm, (x, 3, 0), (("x", -4),), sh)
        k.stack(th, x, 0, [(9.8, 8.4, 8.6), (18, 9.6, 9.8)], "iron", "thigh")
        k.limb(th, (x + side * 4.6, 17, -2), (x + side * 4.6, 10.4, -2), 1.4, "copper", "thigh_piston")
        k.box(th, C(x, 9.2, 1.2, 8.0, 2.6, 8.0), "brass", tag="knee")
        k.stack(sh, x, 0, [(3, 9.6, 10.4), (9.8, 8.6, 9.2)], "plate", "shin")
        k.box(ft, C(x, 0, 1.4, 11, 3.2, 13.6), "iron", tag="foot")
        for z in (-3.6, 0.4, 4.4):
            k.box(ft, C(x, 3.0, z + 1.4, 11.4, 0.8, 1.0), "brass", tag="stomper_band")
    # ---------------------------------------------------------------- the boiler body
    to = k.part("torso", (0, 20, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(20, 20, 15), (25, 26, 19), (31, 28, 20), (37, 27, 19), (41, 22, 16)], "iron", "boiler", step=1.0)
    for y in (22.6, 28.4, 34.2, 39.6):
        k.box(to, C(0, y, 0, 28.6 - abs(y - 31) * 0.6, 1.0, 20.6 - abs(y - 31) * 0.4), "iron", tag="hoop")
        for a in range(-60, 61, 20):
            r = math.radians(a)
            k.rivets(to, [(math.sin(r) * 13.6, y + 0.4, math.cos(r) * 9.8)], "brass", 0.8)
    k.box(to, C(0, 23.4, 9.0, 11, 7.4, 2.4), "iron", tag="firebox_frame")
    k.box(to, C(0, 24.4, 9.6, 8.6, 5.4, 2.0), "glow", group="glow", tag="firebox")
    for x in (-3.0, -1.0, 1.0, 3.0):
        k.box(to, C(x, 24.0, 10.7, 0.8, 6.2, 0.6), "iron", tag="grille")
    for sx in (-1, 1):                          # gauges and a valve wheel on the chest
        k.ring(to, sx * 7.4, 33.4, 9.9, 1.6, 0.6, "brass", "gauge", n=10, axis="z")
        k.box(to, C(sx * 7.4, 32.8, 9.9, 2.2, 1.6, 0.4), "porcelain", tag="gauge_face")
    gear(k, to, (0, 35.6, 10.0), 2.2, mat="brass", w=0.7, teeth=8, spokes=2, tag="valve")
    # smokestacks off the shoulders, the stack tops glowing
    for sx in (-1, 1):
        k.stack(to, sx * 10, -3, [(38, 5.6, 5.6), (52, 4.6, 4.6), (54, 6.4, 6.4)], "iron", "stack")
        k.box(to, C(sx * 10, 53.6, -3, 4.4, 0.6, 4.4), "glow", group="glow", tag="stack_fire")
        for y in (42, 47):
            k.box(to, C(sx * 10, y, -3, 6.2, 1.0, 6.2), "brass", tag="stack_band")
    pipe(k, to, [(-12, 28, -8), (-14, 34, -10), (-10, 40, -9)], 1.4)
    pipe(k, to, [(12, 26, -8), (15, 31, -9), (13, 38, -9)], 1.4)
    key(k, to, (0, 34, -10), (0, 0.2, -1), 5.0, bow=3.6)
    # ---------------------------------------------------------------- the head: an iron dome, a furnace mouth
    hd = k.part("head", (0, 40, 4), (("x", -10),), "torso")
    k.blob(hd, (0, 43, 5), (6.6, 5.0, 6.0), "plate", "dome", step=0.9)
    for sx in (-1, 1):                          # two horns of bent pipe
        pipe(k, hd, [(sx * 5.0, 46, 3), (sx * 8.0, 50, 2), (sx * 8.6, 55, 4)], 1.2, mat="iron")
    k.box(hd, C(0, 40.2, 8.8, 6.6, 3.0, 1.4), "iron", tag="mouth_frame")
    k.box(hd, C(0, 40.6, 9.3, 5.0, 2.0, 1.0), "glow", group="glow", tag="mouth")
    for x in (-1.6, 0, 1.6):
        k.box(hd, C(x, 40.4, 10.0, 0.5, 2.4, 0.4), "iron", tag="teeth_bar")
    for sx in (-2.0, 2.0):
        k.box(hd, C(sx, 44.2, 9.1, 1.6, 1.0, 0.4), "eye", group="glow", tag="eye")
    rivet_row(k, hd, (-4.4, 46.6, 4), (4.4, 46.6, 4), 5)
    # ---------------------------------------------------------------- piston arms, hammer fists
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 16.6
        up = k.part("arm_" + nm, (x, 37, 0), (("x", -20), ("z", side * 14)), "torso")
        fo = k.part("fore_" + nm, (x, 25, 0), (("x", -40),), up)
        hn = k.part("hand_" + nm, (x, 13, 0), (), fo)
        k.blob(up, (x, 37, 0), (5.4, 4.4, 5.4), "plate", "shoulder", step=1.0)
        k.limb(up, (x, 35, 0), (x, 26, 0), 4.0, "iron", "upper_piston")
        k.limb(up, (x - side * 3.4, 34, -2), (x - side * 3.4, 27, -2), 1.4, "copper", "upper_rod")
        k.box(up, C(x, 25.2, 0, 6.2, 2.4, 6.2), "brass", tag="elbow")
        k.stack(fo, x, 0, [(14, 7.0, 7.2), (25, 6.0, 6.2)], "plate", "fore_cylinder")
        k.limb(fo, (x + side * 4.0, 24, 0), (x + side * 4.0, 15, 0), 1.4, "copper", "fore_rod")
        k.box(hn, C(x, 4.6, 0.6, 10.0, 9.6, 10.4), "iron", tag="hammer_fist")
        for y in (6.4, 10.4):
            k.box(hn, C(x, y, 0.6, 10.6, 1.0, 11.0), "brass", tag="fist_band")
        for (dx, dz) in ((-3, 3), (0, 3), (3, 3), (-3, -2), (3, -2)):
            k.box(hn, C(x + dx, 3.4, 0.6 + dz, 1.6, 1.4, 1.6), "brass", tag="stud")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Tinker Adept (caster)

def tinker_adept():
    """The order's last living engineers serve the thing at the top now. A gaunt figure in a long oiled-leather apron
    and hood, brass goggles burning amber over a respirator; its right arm was given to the tower and replaced with a
    brass one of pistons and claw fingers; on its back a coil that arcs, and in its hand a spark rod with a caged orb
    that throws the lightning down the halls. It mends the automatons as fast as you break them."""
    k = X.Kit("tinker_adept")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(16, 9.4, 6.4), (20, 9.8, 6.6)], "leather", "breeches")
    k.box(hips, C(0, 19.6, 0, 10.6, 1.6, 7.2), "leather", tag="belt")
    k.box(hips, C(0, 19.4, 3.7, 2.0, 2.0, 0.6), "brass", tag="buckle")
    for x, h in ((-4.6, 4.4), (-3.2, 3.4), (4.4, 3.8)):              # tools hung off the belt
        k.box(hips, C(x, 19.6 - h, 3.8, 0.8, h, 0.8), "iron", tag="tool")
        k.box(hips, C(x, 19.6 - h - 0.6, 3.8, 1.8, 1.0, 0.8), "iron", tag="tool_head")
    apron = k.part("apron", (0, 20, 3), (), "hips", bone=False)
    k.stack(apron, 0, 3.8, [(2, 10.4, 0.8), (20, 9.0, 0.8)], "leather", "apron")
    for y in (6, 13):
        k.box(apron, C(0, y, 4.3, 6, 0.6, 0.4), "brass", tag="apron_stud")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.6
        th = k.part("thigh_" + nm, (x, 19, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 10.4, 0), (), th)
        ft = k.part("foot_" + nm, (x, 2.4, 0), (), sh)
        k.box(th, C(x, 10.6, 0, 3.8, 8.6, 4.2), "leather", tag="thigh")
        k.box(sh, C(x, 2.4, 0, 3.6, 8.2, 4.0), "leather", tag="boot")
        k.box(sh, C(x, 8.4, 0, 4.2, 1.6, 4.6), "brass", tag="boot_cuff")
        k.box(ft, C(x, 0, 1.2, 4.0, 2.4, 6.4), "iron", tag="foot")
    # ---------------------------------------------------------------- torso, the coil on its back
    to = k.part("torso", (0, 20, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(20, 9.8, 6.6), (26, 11.4, 7.0), (31, 12.6, 7.4), (34, 10.6, 6.6)], "leather", "jerkin")
    k.box(to, C(0, 22, 3.6, 7.4, 11.4, 0.8), "leather", tag="bib")
    for y in (25, 29):
        k.box(to, C(0, y, 3.9, 9.0, 1.0, 0.6), "brass", tag="strap")
    k.stack(to, 0, -6.4, [(22, 7.0, 4.4), (33, 7.4, 4.6)], "iron", "pack")
    k.box(to, C(0, 26.6, -8.8, 3.6, 4.0, 0.6), "glow", group="glow", tag="pack_window")
    for sx in (-1, 1):
        k.limb(to, (sx * 2.4, 33, -6.4), (sx * 2.4, 43, -7.2), 1.0, "copper", "coil_post")
        for i in range(5):
            k.ring(to, sx * 2.4, 35 + i * 1.6, -6.8 - i * 0.16, 1.4, 0.5, "copper", "coil", n=8, axis="y")
        k.box(to, C(sx * 2.4, 42.8, -7.2, 1.8, 1.8, 1.8), "glow", group="glow", tag="coil_top")
    for i in range(4):                          # the arc jumping between the coil tops
        a, b = (-2.4 + i * 1.2, 44.0 + (0.8 if i % 2 else 0), -7.2), (-1.2 + i * 1.2, 44.0 + (0 if i % 2 else 0.8), -7.2)
        k.limb(to, a, b, 0.5, "lens", "arc", group="glow")
    key(k, to, (0, 29, -9.0), (0, 0.1, -1), 2.6, bow=1.6)
    # ---------------------------------------------------------------- the hood, goggles, respirator
    hd = k.part("head", (0, 34, 0.6), (("x", 12),), "torso")
    k.box(hd, C(0, 34, 0.6, 5.6, 6.4, 5.8), "skin", tag="face")
    k.stack(hd, 0, -0.2, [(35, 7.6, 7.6), (41, 7.8, 7.8), (42.6, 6.0, 6.8)], "leather", "hood")
    k.box(hd, C(0, 36.4, 2.6, 6.2, 5.0, 2.2), "dark", tag="hood_shadow")
    k.box(hd, C(0, 38.4, 3.6, 6.6, 1.2, 0.8), "leather", tag="goggle_strap")
    for sx in (-1.4, 1.4):
        k.ring(hd, sx, 38.9, 4.2, 1.1, 0.5, "brass", "goggle", n=10, axis="z")
        k.box(hd, C(sx, 38.4, 4.1, 1.6, 1.2, 0.4), "eye", group="glow", tag="eye")
    k.box(hd, C(0, 34.8, 3.9, 3.6, 2.8, 1.8), "iron", tag="respirator")
    for sx in (-1, 1):
        k.blob(hd, (sx * 2.6, 35.4, 4.0), (1.0, 1.0, 1.0), "brass", "filter", step=0.6)
        k.limb(hd, (sx * 1.6, 35.0, 4.4), (sx * 3.8, 31.4, 2.0), 0.6, "copper", "air_hose")
    # ---------------------------------------------------------------- arms: the brass arm, the spark rod
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.6
        up = k.part("arm_" + nm, (x, 32, 0), (("x", -60 if side < 0 else -20), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 24.6, 0), (("x", -50 if side < 0 else -10),), up)
        hn = k.part("hand_" + nm, (x, 17.4, 0), (), fo)
        if side > 0:                            # the flesh arm, sleeved
            k.box(up, C(x, 25.0, 0, 3.4, 7.4, 3.6), "leather", tag="sleeve")
            k.box(fo, C(x, 17.8, 0, 3.2, 7.0, 3.4), "leather", tag="sleeve")
            k.box(fo, C(x, 18.0, 0, 3.8, 1.6, 4.0), "brass", tag="cuff")
            k.box(hn, C(x, 14.8, 0.4, 2.6, 3.0, 2.8), "skin", tag="hand")
        else:                                   # the brass arm: pistons and a claw
            k.blob(up, (x, 31.4, 0), (2.8, 2.4, 2.8), "plate", "shoulder_joint", step=0.8)
            k.limb(up, (x, 30, 0), (x, 25.2, 0), 1.6, "iron", "brass_humerus")
            k.limb(up, (x - 1.8, 29, -1), (x - 1.8, 25.6, -1), 0.6, "copper", "piston")
            k.box(up, C(x, 24.2, 0, 2.6, 1.6, 2.6), "brass", tag="elbow")
            k.limb(fo, (x, 24, 0), (x, 18.4, 0), 1.6, "plate", "brass_ulna")
            k.limb(fo, (x + 1.6, 23, 1), (x + 1.6, 19, 1), 0.6, "copper", "piston")
            k.box(hn, C(x, 16.6, 0.4, 2.8, 1.8, 2.8), "brass", tag="wrist")
            for i, (dx, dz) in enumerate(((-1.0, 1.4), (0.2, 1.6), (1.2, 1.2), (0.0, -1.2))):
                k.shard(hn, (x + dx, 16.6, dz), (dx * 0.3, -1, dz * 0.4), 3.4, 0.7, mat="iron", tag="claw")
    rod = k.part("spark_rod", (-6.6, 15.6, 0.4), (("x", 70),), k.parts["hand_r"])
    k.limb(rod, (-6.6, -4, 0.4), (-6.6, 34, 0.4), 1.0, "iron", "rod")
    for y in (4, 14, 24):
        k.box(rod, C(-6.6, y, 0.4, 1.6, 1.0, 1.6), "brass", tag="rod_band")
    for a in range(0, 360, 60):                 # the cage round the orb
        r = math.radians(a)
        k.limb(rod, (-6.6, 34, 0.4), (-6.6 + math.cos(r) * 2.4, 37.4, 0.4 + math.sin(r) * 2.4), 0.5, "brass", "cage")
        k.limb(rod, (-6.6 + math.cos(r) * 2.4, 37.4, 0.4 + math.sin(r) * 2.4), (-6.6, 41, 0.4), 0.5, "brass", "cage")
    k.blob(rod, (-6.6, 37.6, 0.4), (1.6, 1.6, 1.6), "lens", "orb", step=0.6)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Clockwork Duelist (elite)

def clockwork_duelist():
    """The gearwrights' masterpiece and the floor's keeper of the key: a slender frame of black iron and brass ribs,
    taller than a man, with four arms - two long sabres high, two daggers low - so it parries and cuts in the same
    breath. Its face is a clock dial of cracked porcelain whose hands spin when it moves; a crown of small gears turns
    above it; a red sash of the old order hangs in tatters from its waist."""
    k = X.Kit("clockwork_duelist")
    hips = k.part("hips", (0, 23, 0))
    k.box(hips, C(0, 20.6, 0, 7.6, 3.0, 4.6), "iron", tag="pelvis")
    k.box(hips, C(0, 23.0, 0, 8.4, 1.0, 5.2), "brass", tag="hip_ring")
    sash = k.part("sash", (2, 23, 2.6), (("z", -8),), "hips", bone=False)
    for i, (x, l) in enumerate(((-1.4, 20), (0.6, 16), (2.4, 22), (4.0, 14))):
        k.box(sash, C(x, 23 - l, 2.8 + (i % 2) * 0.3, 1.8, l, 0.6), "cloth", tag="sash")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 22, 0), (("x", -18 if side > 0 else 6), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 11.8, 0), (("x", 26 if side > 0 else 6),), th)
        ft = k.part("foot_" + nm, (x, 2.4, 0), (("x", -6),), sh)
        k.limb(th, (x, 21, 0), (x, 12.6, 0), 1.6, "iron", "femur")
        k.box(th, C(x, 15.0, 0.8, 3.0, 5.2, 2.4), "plate", tag="thigh_plate")
        k.box(th, C(x, 11.6, 0, 2.6, 1.8, 2.6), "brass", tag="knee")
        k.limb(sh, (x, 11.4, 0), (x, 3.0, -0.6), 1.4, "iron", "tibia")
        k.box(sh, C(x, 4.6, 1.0, 2.8, 5.6, 1.4), "plate", tag="shin_plate")
        k.box(ft, C(x, 0, 1.4, 2.6, 2.4, 6.6), "iron", tag="foot")
        k.shard(ft, (x, 0.4, 4.6), (0, 0, 1), 2.4, 1.2, mat="brass", tag="toe_spike")
    # ---------------------------------------------------------------- torso: a cage of ribs, a gear heart
    to = k.part("torso", (0, 23, 0), (("x", 6),), "hips")
    k.limb(to, (0, 23.6, -1.4), (0, 36, -1.6), 1.8, "iron", "spine")
    for i, y in enumerate((26, 28.6, 31.2, 33.8)):
        w = 4.4 + i * 0.9
        k.ring(to, 0, y, 0, w, 0.6, "brass", "rib", n=10, axis="y")
    gear(k, to, (0, 30.6, 1.0), 1.8, mat="glow", w=0.6, teeth=8, spokes=2, hub="brass", tag="gear_heart")
    k.box(to, C(0, 35.2, 0, 13.6, 2.2, 5.4), "plate", tag="yoke")
    for side in (1, -1):
        k.blob(to, (side * 7.4, 36.6, 0), (4.4, 2.6, 4.0), "plate", "pauldron", step=0.8)
        for i, a in enumerate((-30, 0, 30)):
            r = math.radians(a)
            k.shard(to, (side * 8.6, 38.4, math.sin(r) * 2.4), (side * 0.7, 1, math.sin(r) * 0.4), 4.4 - abs(a) / 20, 1.3,
                    mat="iron", tag="pauldron_spike")
    # a halo of clock hands fanned out behind its head: its silhouette is a sunburst of knives
    for i in range(9):
        a = math.radians(-80 + i * 20)
        base = (math.sin(a) * 2.4, 43.0 + math.cos(a) * 2.4, -3.6)
        L = 9.0 if i % 2 == 0 else 6.0
        k.shard(to, base, (math.sin(a), math.cos(a), -0.15), L, 1.1 if i % 2 == 0 else 0.8,
                mat="iron" if i % 2 == 0 else "brass", tag="halo_hand")
    k.ring(to, 0, 43.0, -3.6, 2.6, 0.8, "brass", "halo_ring", n=12, axis="z")
    cape = k.part("cape", (0, 36, -2.8), (("x", -8),), to, bone=False)
    for i, (x, l) in enumerate(((-4.6, 20), (-1.6, 26), (1.6, 23), (4.6, 18))):
        k.box(cape, C(x, 36 - l, -3.2 - (i % 2) * 0.3, 2.8, l, 0.6), "cloth", tag="cape")
    key(k, to, (0, 31, -2.2), (0, 0.3, -1), 3.4, bow=2.0)
    # ---------------------------------------------------------------- the clock-face mask, the crown of gears
    hd = k.part("head", (0, 37, 0.2), (("x", -6),), "torso")
    k.limb(hd, (0, 37, 0), (0, 39.4, 0), 1.2, "iron", "neck")
    k.blob(hd, (0, 42.6, 0), (3.2, 3.6, 3.0), "iron", "skull", step=0.8)
    k.box(hd, C(0, 39.4, 2.6, 6.4, 6.4, 0.8), "porcelain", tag="dial")
    k.ring(hd, 0, 42.6, 3.2, 3.2, 0.6, "brass", "bezel", n=14, axis="z")
    for h in range(12):
        a = math.radians(h * 30)
        k.box(hd, C(math.cos(a) * 2.5, 42.4 + math.sin(a) * 2.5, 3.1, 0.4, 0.4, 0.2), "dark", tag="hour_mark")
    k.limb(hd, (0, 42.6, 3.3), (1.6, 44.2, 3.3), 0.36, "dark", "hand")
    k.limb(hd, (0, 42.6, 3.3), (-0.8, 40.2, 3.3), 0.3, "dark", "hand")
    k.limb(hd, (-1.4, 45.2, 3.2), (0.4, 41.0, 3.2), 0.28, "dark", "crack")
    for sx in (-1.2, 1.2):
        k.box(hd, C(sx, 42.8, 3.15, 0.8, 0.5, 0.2), "eye", group="glow", tag="eye")
    for i, (x, r) in enumerate(((-2.4, 1.3), (0, 1.8), (2.4, 1.3))):
        gear(k, hd, (x, 47.0 + (0.4 if i == 1 else 0), -0.4), r, mat="brass", w=0.5, teeth=7, spokes=2, tag="crown_gear")
    # ---------------------------------------------------------------- four arms: sabres high, daggers low
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.0
        up = k.part("arm_" + nm, (x, 35, 0), (("x", -70), ("z", side * 18)), "torso")
        fo = k.part("fore_" + nm, (x, 27, 0), (("x", -40),), up)
        hn = k.part("hand_" + nm, (x, 19, 0), (), fo)
        k.limb(up, (x, 34, 0), (x, 27.6, 0), 1.4, "iron", "humerus")
        k.box(up, C(x, 29.0, 0.6, 2.6, 4.4, 2.0), "plate", tag="arm_plate")
        k.box(up, C(x, 26.8, 0, 2.2, 1.4, 2.2), "brass", tag="elbow")
        k.limb(fo, (x, 26.4, 0), (x, 19.8, 0), 1.2, "iron", "ulna")
        k.box(fo, C(x, 20.8, 0.5, 2.4, 4.4, 1.8), "plate", tag="fore_plate")
        k.box(hn, C(x, 16.6, 0.2, 2.2, 2.6, 2.2), "iron", tag="hand")
        sb = k.part("sabre_" + nm, (x, 17.2, 0.4), (("x", 30),), hn, bone=False)
        k.box(sb, C(x, 15.4, 0.4, 4.6, 0.8, 1.6), "brass", tag="guard")
        k.limb(sb, (x, 13.4, 0.4), (x, 16.6, 0.4), 0.9, "leather", "grip")
        for i in range(10):                      # the curved blade, a slice a step, the curve back
            y = 17.2 + i * 2.6
            z = 0.4 + 0.07 * i * i
            k.box(sb, C(x, y, z, 0.6, 2.7, 2.4 - i * 0.12), "iron", tag="blade")
            k.box(sb, C(x, y, z + 1.2 - i * 0.06, 0.65, 2.7, 0.5), "porcelain", tag="edge")
    for side in (1, -1):                         # the lower pair, off the ribs, each with a dagger
        x0, x1 = side * 4.6, side * 9.4
        lo = k.part("low_arm_" + ("l" if side > 0 else "r"), (x0, 28, 0), (("x", -40), ("z", side * 30)), to, bone=False)
        k.limb(lo, (x0, 28, 0), (x1, 22, 2.0), 1.1, "iron", "low_humerus")
        k.box(lo, C(x1, 21.0, 2.0, 1.8, 1.8, 1.8), "brass", tag="low_elbow")
        k.limb(lo, (x1, 21.6, 2.0), (x1 + side * 0.6, 15.6, 5.0), 1.0, "iron", "low_ulna")
        k.box(lo, C(x1 + side * 0.6, 14.6, 5.0, 1.8, 1.8, 1.8), "iron", tag="low_hand")
        k.box(lo, C(x1 + side * 0.6, 13.8, 6.2, 2.8, 0.6, 1.0), "brass", tag="dagger_guard")
        k.shard(lo, (x1 + side * 0.6, 13.6, 6.6), (0, -0.2, 1), 6.0, 1.3, mat="iron", tag="dagger")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Grand Horologe (boss)

def grand_horologe():
    """What sits at the top of the tower and winds it. Nine blocks of brass and black iron: a clock for a face, a dial
    as wide as a door in a brass case, its hands knives, under a crown of turning gears; a chest that is a cage of
    iron ribs with the mainspring of the whole tower coiled inside it, burning white-gold; pauldrons that are great
    cogs on their sides; its right arm ends in a piston hammer the size of a cart, its left in a pendulum, a long rod
    and a crescent blade it sweeps across the roof. On its back two stacks smoke and a key as tall as a man turns."""
    k = X.Kit("grand_horologe")
    hips = k.part("hips", (0, 30, 0))
    k.stack(hips, 0, 0, [(22, 22, 14), (30, 24, 15)], "iron", "pelvis")
    k.box(hips, C(0, 29.2, 0, 26, 2.0, 16.4), "plate", tag="belt")
    gear(k, hips, (0, 25.4, 8.0), 3.4, mat="brass", w=1.0, teeth=10, spokes=3, tag="belt_gear")
    for x in (-8, -3, 3, 8):                    # a skirt of hanging plates, like weights on chains
        k.box(hips, C(x, 13, 7.6, 4.6, 9, 1.0), "plate", tag="tasset")
        k.box(hips, C(x, 13.4, 8.2, 3.2, 0.8, 0.4), "iron", tag="tasset_band")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.4
        th = k.part("thigh_" + nm, (x, 28, 0), (("x", -6), ("z", side * 8)), "hips")
        sh = k.part("shin_" + nm, (x, 15.6, 0), (("x", 10),), th)
        ft = k.part("foot_" + nm, (x, 4, 0), (("x", -4),), sh)
        k.stack(th, x, 0, [(15.6, 9.0, 9.6), (28, 10.6, 11.2)], "iron", "thigh")
        k.box(th, C(x, 19, 1.0, 10.0, 7.6, 10.4), "plate", tag="cuisse")
        k.limb(th, (x + side * 5.4, 27, -3), (x + side * 5.4, 16.6, -3), 1.8, "copper", "thigh_piston")
        gear(k, th, (x + side * 5.6, 16.4, 0), 2.6, axis="x", mat="brass", w=0.9, teeth=9, spokes=2, tag="knee_gear")
        k.stack(sh, x, 0, [(4, 11.0, 12.0), (15.6, 9.0, 10.0)], "plate", "greave")
        for y in (7, 11):
            k.box(sh, C(x, y, 0, 11.6, 1.0, 12.6), "iron", tag="greave_band")
        k.box(ft, C(x, 0, 2.0, 13.4, 4.0, 18), "iron", tag="foot")
        k.box(ft, C(x, 4.0, 2.0, 11.0, 1.4, 15.6), "brass", tag="anvil_top")
        k.shard(ft, (x, 1.6, 11.0), (0, 0, 1), 4.0, 3.0, mat="iron", tag="anvil_horn")
    # ---------------------------------------------------------------- the chest: a cage with the mainspring in it
    to = k.part("torso", (0, 30, 0), (("x", 8),), "hips")
    k.stack(to, 0, -3.4, [(30, 22, 10), (36, 28, 12), (44, 34, 13), (52, 36, 13), (57, 30, 11)], "iron", "back_shell", step=1.2)
    for i in range(9):                          # the ribs in front, the spring showing between them
        y = 33 + i * 2.6
        w = 22 + 10 * math.sin(min(1.0, i / 6) * math.pi / 2)
        for sx in (-1, 1):
            k.limb(to, (sx * 2.0, y, 9.6), (sx * w / 2, y - 1.4, 4.0), 1.2, "brass" if i % 2 else "iron", "rib")
    k.limb(to, (0, 31, 9.8), (0, 55, 9.8), 2.2, "plate", "sternum")
    k.box(to, C(0, 34, 1.0, 22, 20, 7), "dark", tag="chest_hollow")
    spring(k, to, (0, 45, 6.6), 1.2, 9.0, 3.2, 1.0, mat="glow", axis="z")
    k.blob(to, (0, 45, 6.0), (2.2, 2.2, 1.6), "lens", "spring_arbor", step=0.8)
    for sx in (-1, 1):
        gear(k, to, (sx * 9.6, 37.4, 6.4), 3.2, mat="brass", w=0.9, teeth=10, spokes=3, tag="chest_gear")
    k.box(to, C(0, 55.6, 0, 34, 3.0, 14), "plate", tag="collar")
    rivet_row(k, to, (-15, 57.2, 7.2), (15, 57.2, 7.2), 9, 1.0)
    # the gear pauldrons, on their sides
    for side in (1, -1):
        gear(k, to, (side * 19.6, 56.6, 0), 6.4, axis="x", mat="plate", w=1.6, teeth=14, spokes=4, hub="iron", tag="pauldron_gear")
        k.blob(to, (side * 17.0, 55.4, 0), (5.2, 4.4, 6.0), "iron", "shoulder", step=1.0)
    # the stacks and the great key on its back
    for sx in (-1, 1):
        k.stack(to, sx * 8, -11, [(50, 6, 6), (72, 5, 5), (74, 7.6, 7.6)], "iron", "stack")
        k.box(to, C(sx * 8, 73.6, -11, 5.6, 0.8, 5.6), "glow", group="glow", tag="stack_fire")
        for y in (56, 63, 70):
            k.box(to, C(sx * 8, y, -11, 6.8, 1.2, 6.8), "brass", tag="stack_band")
    key(k, to, (0, 46, -12), (0, 0.15, -1), 9.0, bow=6.0)
    # ---------------------------------------------------------------- the head: a clock in a brass case
    hd = k.part("head", (0, 58, 2), (("x", -6),), "torso")
    k.box(hd, C(0, 57.6, 0.6, 15, 16, 9), "plate", tag="clock_case")
    for sx in (-1, 1):
        k.box(hd, C(sx * 7.6, 57.0, 0.6, 1.6, 17, 10), "brass", tag="case_pillar")
        k.shard(hd, (sx * 7.6, 74, 0.6), (sx * 0.2, 1, 0), 3.6, 1.6, mat="brass", tag="finial")
    k.box(hd, C(0, 59.0, 5.0, 13, 13, 0.8), "porcelain", tag="dial")
    k.ring(hd, 0, 65.5, 5.6, 6.4, 0.9, "brass", "bezel", n=20, axis="z")
    for h in range(12):
        a = math.radians(h * 30)
        long_ = h % 3 == 0
        r0, r1 = (4.0 if long_ else 4.8), 5.6
        k.limb(hd, (math.cos(a) * r0, 65.5 + math.sin(a) * r0, 5.7), (math.cos(a) * r1, 65.5 + math.sin(a) * r1, 5.7),
               0.6 if long_ else 0.4, "dark", "hour_mark")
    k.limb(hd, (0, 65.5, 5.9), (-3.0, 68.6, 5.9), 0.8, "iron", "hour_hand")
    k.limb(hd, (0, 65.5, 6.0), (4.4, 70.0, 6.0), 0.6, "iron", "minute_hand")
    k.shard(hd, (4.4, 70.0, 6.0), (0.7, 1, 0), 1.6, 0.9, mat="iron", tag="hand_tip")
    k.box(hd, C(0, 64.9, 6.0, 1.4, 1.4, 0.6), "brass", tag="arbor")
    for sx in (-2.6, 2.6):                     # two burning eyes set in the dial, behind glass
        k.box(hd, C(sx, 62.6, 5.5, 2.0, 1.2, 0.4), "eye", group="glow", tag="eye")
    k.limb(hd, (-4.0, 70, 5.6), (-1.0, 61, 5.6), 0.4, "dark", "crack")
    for i, (x, r) in enumerate(((-6, 2.6), (0, 3.6), (6, 2.6))):    # the crown of gears
        gear(k, hd, (x, 76.4 + (1.6 if i == 1 else 0), 0.6), r, mat="brass", w=0.8, teeth=9, spokes=2, tag="crown_gear")
    # ---------------------------------------------------------------- arms: the piston hammer, the pendulum blade
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 20.0
        up = k.part("arm_" + nm, (x, 53, 0), (("x", -20), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 37, 0), (("x", -40),), up)
        hn = k.part("hand_" + nm, (x, 22, 0), (), fo)
        k.limb(up, (x, 51, 0), (x, 38, 0), 5.0, "iron", "upper_cylinder")
        k.box(up, C(x, 42, 0.6, 7.0, 7.0, 7.6), "plate", tag="rerebrace")
        k.limb(up, (x - side * 4.0, 50, -2.6), (x - side * 4.0, 39, -2.6), 1.6, "copper", "upper_piston")
        gear(k, up, (x + side * 4.0, 37.0, 0), 3.0, axis="x", mat="brass", w=0.9, teeth=9, spokes=2, tag="elbow_gear")
        k.stack(fo, x, 0, [(23, 7.6, 7.8), (36, 8.6, 8.8)], "plate", "fore_cylinder")
        k.limb(fo, (x + side * 4.6, 35, 0), (x + side * 4.6, 24, 0), 1.6, "copper", "fore_piston")
    # right: the piston hammer, its head by the knee
    hm = k.part("hammer", (-20, 22, 0), (), k.parts["hand_r"], bone=False)
    k.limb(hm, (-20, 22, 0), (-20, 15, 0), 3.4, "iron", "ram")
    k.box(hm, C(-20, 1, 0.0, 17, 15, 17), "iron", tag="hammer_head")
    for y in (3.4, 8.0, 12.6):
        k.box(hm, C(-20, y, 0.0, 18, 1.4, 18), "brass", tag="hammer_band")
    for (dx, dz) in ((-5, 5), (0, 5.8), (5, 5), (-5, -5), (5, -5), (0, 0)):
        k.box(hm, C(-20 + dx, -0.4, dz, 2.6, 1.6, 2.6), "brass", tag="stud")
    k.box(hm, C(-20, 5.0, 8.8, 9, 7, 0.6), "glow", group="glow", tag="hammer_vent")
    for x in (-23, -20, -17):
        k.box(hm, C(x, 4.6, 9.2, 0.8, 7.6, 0.6), "iron", tag="vent_bar")
    # left: the pendulum - a rod to a crescent blade, points up
    pd = k.part("pendulum", (20, 22, 0), (), k.parts["hand_l"], bone=False)
    k.box(pd, C(20, 19.4, 0, 6, 3, 6), "brass", tag="pendulum_clamp")
    k.limb(pd, (20, 20, 0), (20, 9, 0), 1.8, "iron", "pendulum_rod")
    for i in range(10):
        a0, a1 = math.radians(-75 + i * 15), math.radians(-60 + i * 15)
        x0, y0 = 20 + math.sin(a0) * 14, 9 - math.cos(a0) * 8
        x1, y1 = 20 + math.sin(a1) * 14, 9 - math.cos(a1) * 8
        k.limb(pd, (x0, y0, 0), (x1, y1, 0), 3.0 - abs(i - 4.5) * 0.3, "iron", "pendulum_blade")
        k.limb(pd, (x0, y0 - 1.4, 0), (x1, y1 - 1.4, 0), 0.7, "porcelain", "pendulum_edge")
    k.blob(pd, (20, 9, 0), (3.8, 3.8, 2.2), "plate", "bob", step=0.8)
    k.box(pd, C(20, 8, 1.8, 2.4, 2.4, 0.6), "glow", group="glow", tag="bob_lamp")
    grow(k, 1.6)                                # drawn at a hulk's scale, stood up colossal: about eight blocks
    k.s.shaders = shaders()
    return k.s, k.parts


MOBS = {
    "cogling": dict(make=cogling, rig="crawler", ent=(1.0, 0.9), stats=dict(hp=22, speed=0.36, dmg=6, armor=4, kb=0)),
    "brass_sentry": dict(make=brass_sentry, ent=(1.2, 3.3), stats=dict(hp=70, speed=0.22, dmg=11, armor=10, kb=0.5)),
    "steam_hulk": dict(make=steam_hulk, ent=(1.9, 4.0), stats=dict(hp=140, speed=0.18, dmg=18, armor=12, kb=1.0)),
    "tinker_adept": dict(make=tinker_adept, ent=(0.9, 2.8), stats=dict(hp=40, speed=0.22, dmg=7, armor=3, kb=0)),
    "clockwork_duelist": dict(make=clockwork_duelist, ent=(1.0, 3.3), stats=dict(hp=240, speed=0.32, dmg=14, armor=10, kb=0.6), key=True),
    "grand_horologe": dict(make=grand_horologe, texel=1, ent=(3.6, 8.6), stats=dict(hp=900, speed=0.19, dmg=24, armor=14, kb=1.0), boss=True),
}
