"""The Coiled Spire's monsters, the Coilborn, each built by hand (tools/vox2.py). The serpent coiled round the tower
was a god once, and its temple still breeds for it: scaled things that walk like men, its priests in jade masks, and
the jaguar knights and plumed champions who sold themselves to it. Olive-black scales banded jade, cream bellies,
beaten gold, obsidian edges, quetzal green and scarlet feathers, and the green of venom glowing in every fang.

    coilspawn           swarm   a man-long hooded serpent on four splayed lizard legs, venom on its fangs, the spectacle
                                mark on its hood glowing
    scaleguard          guard   a serpent-man warrior: a cobra's head with its hood flared, jade lamellar, gold serpent-head
                                pauldrons, a feather-fringed round shield and an obsidian-bladed spear, a tail behind
    jaguar_stalker      brute   a hulking jaguar knight in the whole pelt of the beast, his face in its jaws, the paws
                                over his chest, a two-handed macuahuitl edged with obsidian teeth
    venom_priest        caster  a gaunt priest in a jade death mask under a fan of quetzal plumes, ribs painted on bare
                                skin, a live serpent across its shoulders, a serpent staff with a smoking venom censer
    feathered_champion  elite   a plumed knight in white war-cotton and gold: a serpent-jaw helm, a sunburst of plumes
                                behind, a mantle of feathers, two obsidian swords
    coiled_king         boss    a naga lord: a great coiled tail on the roof, a scaled torso in a gold collar, a crowned
                                serpent head under a vast hood with seven hooded heads round its rim, four arms: a
                                serpent glaive, the Disc of the Coil, two venom knives

    python tools/monsterforge.py serpent_ziggurat --preview ; python tools/mobsheet.py serpent_ziggurat
"""
import math

import vox2 as X
from vox2 import C, ramp

SCALE = ramp("#070c0a", "#0e1712", "#16231a", "#203222", "#2c442c", "#3c5a36", "#507244")
JADE = ramp("#04140e", "#0a2418", "#123a26", "#1c5636", "#2a7446", "#42945a", "#68b478")
BELLY = ramp("#2c2410", "#4a3c1a", "#6c5a28", "#8e7a38", "#b09a4c", "#cebc6a")
GOLD = ramp("#2a1804", "#4c300a", "#7a5014", "#a87422", "#d0a034", "#f0cc5a", "#fff0a0")
OBSID = ramp("#040408", "#0a0a12", "#12121e", "#1c1c2c", "#28283c", "#3a3a54")
PLUME = ramp("#032016", "#063a26", "#0a5636", "#107446", "#1a9a56", "#3ec46e", "#86e8a0")
SCARLET = ramp("#2a0404", "#4a0808", "#721210", "#9c1e16", "#c4321e", "#e65230")
SKIN = ramp("#180e0a", "#26160e", "#3a2214", "#50301c", "#683e24", "#80502e")
FUR = ramp("#2a1606", "#4a280c", "#6e3e14", "#92561c", "#b67026", "#d48e36", "#ecb256")
COTTON = ramp("#3a342a", "#5a5244", "#7c7260", "#9e947e", "#beb49c", "#dad2ba")
CLOTH = ramp("#1a0606", "#2c0a08", "#44100c", "#5e1a12", "#78261a")
WOOD = ramp("#140c08", "#21140c", "#301e12", "#422a18", "#56381e")
BONE = ramp("#3a3428", "#5c5444", "#827a64", "#a8a088", "#cec6ac", "#ece6d0")
VENOM = ramp("#063a16", "#0e6a28", "#1ea840", "#4ae064", "#a0ff90", "#e8ffe0")
EYE = ramp("#4a3404", "#8a6206", "#d09a0c", "#ffcc28", "#fff080", "#fffde0")
GORE = ramp("#100406", "#1e080a", "#2e0e10", "#401416")


def scales(p, n, i, j, w, h):
    """overlapping rows of scales, offset like brickwork, a dark line under each row"""
    row = j // 3
    if j % 3 == 2:
        return -0.2
    if (i + (row % 2) * 2) % 4 == 0:
        return -0.12
    return 0.05 if j % 3 == 0 else 0


def scutes(p, n, i, j, w, h):
    return -0.22 if j % 3 == 2 else 0.04


def rosettes(p, n, i, j, w, h):
    """a jaguar's coat: broken rings of black, a darker heart in some"""
    a, b = i % 6, (j + (i // 6) * 3) % 6
    if X.h3(i // 6, (j + (i // 6) * 3) // 6, 7) < 0.25:
        return 0
    r = (a - 2.5) ** 2 + (b - 2.5) ** 2
    if 2.2 <= r <= 6.3 and (a + b) % 5:
        return -0.62
    return -0.14 if r < 2.2 else 0


def vanes(p, n, i, j, w, h):
    return -0.16 if i % 2 == 0 else 0.03


def shaders():
    return {
        "scale": X.surf(SCALE, 0.5, 1.4, 0.16, 0.16, pattern=scales),
        "band": X.surf(JADE, 0.56, 1.4, 0.16, 0.16, pattern=scales),
        "belly": X.surf(BELLY, 0.52, 1.2, 0.12, 0.0, pattern=scutes),
        "jade": X.surf(JADE, 0.56, 1.5, 0.16, 0.2, pattern=lambda p, n, i, j, w, h: 0.3 if abs(X.fbm(p[0] * 0.4, p[1] * 0.4, p[2] * 0.4) - 0.5) < 0.02 else 0),
        "gold": X.surf(GOLD, 0.5, 1.5, 0.12, 0.24, rust=(JADE, 0.08, 0.7)),
        "obsidian": X.surf(OBSID, 0.5, 1.6, 0.1, 0.34),
        "plume": X.surf(PLUME, 0.5, 1.3, 0.1, 0.1, pattern=vanes),
        "plume_r": X.surf(SCARLET, 0.5, 1.3, 0.1, 0.1, pattern=vanes),
        "skin": X.wrinkled(SKIN, 0.8),
        "fur": X.surf(FUR, 0.52, 1.3, 0.2, 0.06, pattern=rosettes),
        "fur_pale": X.surf(BELLY, 0.62, 1.1, 0.2, 0.0, pattern=rosettes),
        "cotton": X.surf(COTTON, 0.5, 1.2, 0.12, 0.06, stripe=3),
        "cloth": X.surf(CLOTH, 0.5, 1.0, 0.2, 0.0, holes=True),
        "wood": X.surf(WOOD, 0.5, 1.1, 0.2, 0.08, stripe=4),
        "bone": X.surf(BONE, 0.54, 1.2, 0.14, 0.12),
        "mouth": X.dark(GORE),
        "venom": X.glow(VENOM),
        "eye": X.glow(EYE, 0.8, 0.16),
        "dark": X.dark(OBSID),
    }


# ================================================================ shared brushes (shapes, not bodies)

def _along(pts):
    seg = [(a, b, math.dist(a, b)) for a, b in zip(pts, pts[1:])]
    total = sum(s[2] for s in seg)

    def at(d):
        for a, b, L in seg:
            if d <= L or (a, b, L) == seg[-1]:
                t = min(1.0, d / L) if L else 0
                return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
            d -= L
    return at, total


def tube(k, part, pts, r, mat="scale", belly="belly", under=(0, -1, 0), band=None, step=1.0, tag="coil"):
    """a serpent's body swept along pts: a round section every `step`, r a number or r(t), the pale belly scutes on
    the `under` side (a vector, or under(t)), a jade band every `band` sections"""
    at, total = _along(pts)
    n = max(2, int(total / step))
    for i in range(n + 1):
        t = i / n
        p = at(t * total)
        rr = r(t) if callable(r) else r
        m = "band" if band and i % band < 1 else mat
        k.blob(part, p, (rr, rr * 0.92, rr), m, tag, step=max(0.7, rr * 0.55))
        if belly:
            u = under(t) if callable(under) else under
            o = rr * 0.5
            k.box(part, C(p[0] + u[0] * o, p[1] + u[1] * o - rr * 0.38, p[2] + u[2] * o, rr * 1.2, rr * 0.76, rr * 1.2), belly, tag="belly")


def snake_head(k, part, c, s, open_=0.35, mat="scale", tag="snake"):
    """a serpent's head facing +z from c (the back of the skull, at the jaw line): a broad wedge of a skull over heavy
    brows, slit eyes burning yellow, an open mouth, the lower jaw dropped, two long fangs wet with venom"""
    cx, cy, cz = c
    L = 6.0 * s
    n = 6
    for i in range(n):
        t = i / n
        w = (4.6 - 2.2 * t) * s
        h = (2.9 - 1.2 * t) * s
        k.box(part, C(cx, cy - 0.2 * s, cz + L * t + L / n / 2, w, h, L / n + 0.05), mat, tag=tag + "_skull")
    for sx in (-1, 1):
        k.box(part, C(cx + sx * 1.5 * s, cy + 2.5 * s, cz + 1.9 * s, 1.5 * s, 0.9 * s, 3.0 * s), mat, tag="brow")
        k.box(part, C(cx + sx * 1.6 * s, cy + 2.2 * s, cz + 4.2 * s, 1.0 * s, 0.6 * s, 1.6 * s), mat, tag="brow")
        k.box(part, C(cx + sx * 2.05 * s, cy + 1.45 * s, cz + 2.0 * s, 0.6 * s, 0.75 * s, 1.5 * s), "eye", group="glow", tag="eye")
        k.box(part, C(cx + sx * 2.12 * s, cy + 1.5 * s, cz + 2.4 * s, 0.6 * s, 0.6 * s, 0.25 * s), "dark", tag="pupil")
        k.box(part, C(cx + sx * 0.7 * s, cy + 1.2 * s, cz + L - 0.2 * s, 0.5 * s, 0.4 * s, 0.4 * s), "dark", tag="nostril")
    drop = open_ * L
    k.limb(part, (cx, cy - 0.3 * s, cz + 0.6 * s), (cx, cy - 0.4 * s - drop * 0.6, cz + L * 0.8), 2.6 * s, "mouth", "mouth")
    for i in range(5):
        t = i / 5
        w = (4.0 - 2.0 * t) * s
        k.box(part, C(cx, cy - 1.2 * s - drop * t, cz + L * 0.9 * t + L * 0.09, w, 1.0 * s, L * 0.19), mat, tag=tag + "_jaw")
        k.box(part, C(cx, cy - 1.25 * s - drop * t, cz + L * 0.9 * t + L * 0.09, w * 0.6, 0.4 * s, L * 0.19), "belly", tag="chin")
    for sx in (-1, 1):
        f = 1.0 + open_ * 1.4
        k.shard(part, (cx + sx * 1.0 * s, cy - 0.4 * s, cz + L * 0.84), (0, -1, 0.18), 1.9 * s * f, 0.6 * s, mat="bone", tag="fang")
        k.box(part, C(cx + sx * 1.0 * s, cy - 0.5 * s - 1.9 * s * f, cz + L * 0.84 + 0.3 * s, 0.4 * s, 0.6 * s, 0.4 * s), "venom", group="glow", tag="venom")
        for z in (0.4, 0.62):                     # the lower teeth, small and back-curved
            k.shard(part, (cx + sx * 1.3 * s, cy - 1.0 * s - drop * (z + 0.1), cz + L * z), (0, 1, -0.2), 0.8 * s, 0.35 * s, mat="bone", tag="tooth")


def hood(k, part, cx, y0, y1, cz, w, thick=1.2, tag="hood", mark=True):
    """a cobra's hood behind a neck: flat, cupped forward at its edges, widest two-thirds up and round over the top;
    pale ribbed scutes in front with two dark bands, the spectacle mark glowing on its back"""
    n = max(4, int((y1 - y0) / 1.0))
    for i in range(n):
        t = (i + 0.5) / n
        y = y0 + (y1 - y0) * i / n
        ww = w * (math.sin(t / 0.66 * math.pi / 2) if t < 0.66 else math.sqrt(max(0.0, math.cos((t - 0.66) / 0.34 * math.pi / 2))))
        ww = max(ww, w * 0.3)
        hh = (y1 - y0) / n + 0.05
        k.box(part, C(cx, y, cz - thick * 0.25, ww * 0.56, hh, thick * 0.5), "scale", tag=tag)
        front = "scale" if abs(t - 0.32) < 0.04 or abs(t - 0.44) < 0.04 else "belly"
        k.box(part, C(cx, y, cz + thick * 0.25, ww * 0.5, hh, thick * 0.5), front, tag=tag)
        for sx in (-1, 1):                        # the cupped wings
            k.box(part, C(cx + sx * ww * 0.39, y, cz + thick * 0.45, ww * 0.24, hh, thick * 0.8), "scale", tag=tag)
            k.box(part, C(cx + sx * ww * 0.44, y, cz + thick * 1.0, ww * 0.12, hh, thick * 0.7), "band", tag=tag)
    if mark:                                      # the spectacle, burning on the back
        ym = y0 + (y1 - y0) * 0.6
        for sx in (-1, 1):
            r = w * 0.12
            for a in range(10):
                a0, a1 = a * math.pi / 5, (a + 1) * math.pi / 5
                k.limb(part, (cx + sx * w * 0.16 + math.cos(a0) * r, ym + math.sin(a0) * r, cz - thick * 0.55),
                       (cx + sx * w * 0.16 + math.cos(a1) * r, ym + math.sin(a1) * r, cz - thick * 0.55), max(0.5, w * 0.03), "venom", "spectacle", group="glow")
        k.limb(part, (cx - w * 0.04, ym - w * 0.12, cz - thick * 0.55), (cx + w * 0.04, ym - w * 0.12, cz - thick * 0.55), max(0.5, w * 0.03), "venom", "spectacle", group="glow")


def feather(k, part, base, d, L, w, mat="plume", tip="gold", flat="z", tag="feather"):
    """a long plume from base along d: a broad vane narrowing to a tip; flat across z (a fan) or across x (hanging)"""
    n = math.sqrt(sum(c * c for c in d))
    d = tuple(c / n for c in d)
    m = tuple(base[i] + d[i] * L * 0.78 for i in range(3))
    e = tuple(base[i] + d[i] * L for i in range(3))
    if flat == "z":
        k.limb(part, base, m, w, mat, tag, d=0.5)
        k.limb(part, m, e, w * 0.62, tip, tag + "_tip", d=0.5)
    else:
        k.limb(part, base, m, 0.5, mat, tag, d=w)
        k.limb(part, m, e, 0.5, tip, tag + "_tip", d=w * 0.62)


def disc(k, part, c, r, axis, mat, tag, thick=1.0):
    """a filled disc of slices"""
    cx, cy, cz = c
    n = max(3, int(r * 2 / 1.0))
    for i in range(n):
        y = -r + (i + 0.5) * 2 * r / n
        w = 2 * math.sqrt(max(0.0, r * r - y * y))
        if axis == "z":
            k.box(part, C(cx, cy + y - r / n, cz, w, 2 * r / n + 0.05, thick), mat, tag=tag)
        else:
            k.box(part, C(cx, cy + y - r / n, cz, thick, 2 * r / n + 0.05, w), mat, tag=tag)


def obsidian_teeth(k, part, x, y0, y1, cz, half, every=2.0, size=2.0):
    """a macuahuitl's edges: obsidian flakes set in both edges of a flat wooden paddle"""
    y = y0
    while y < y1:
        for sz in (-1, 1):
            k.shard(part, (x, y, cz + sz * half), (0, 0.3, sz), size, 1.0, mat="obsidian", tag="flake")
        y += every


# ================================================================ the Coilspawn (swarm, crawler)

def coilspawn():
    """The temple's young: a serpent as long as a man on four short splayed legs, low and quick as a lizard, its front
    reared up into a hooded neck. Olive-black scales banded jade, a cream belly, the spectacle on the back of its hood
    burning green, two fangs wet with venom. They pour out of the coil's scales in nests of twenty."""
    k = X.Kit("coilspawn")
    body = k.part("body", (0, 7, 0))
    tube(k, body, [(0, 6.2, -3), (0, 6.6, 3), (0, 9, 6.6)], 3.2, band=5, under=(0, -1, 0))
    for z in range(-2, 6, 2):                     # a ridge of small scutes down the back
        k.shard(body, (0, 9.4, z), (0, 1, -0.4), 1.4, 1.0, mat="band", tag="ridge")
    hd = k.part("head", (0, 9, 6.6), (("x", 8),), "body")
    tube(k, hd, [(0, 9, 6.6), (0, 13.5, 8.4), (0, 17, 8.6)], lambda t: 2.9 - 0.6 * t, band=4, under=(0, 0, 1))
    hood(k, hd, 0, 11.5, 21, 7.4, 11.0, thick=1.0)
    snake_head(k, hd, (0, 18.0, 8.0), 0.95, open_=0.45)
    ab = k.part("abdomen", (0, 6.6, -3), (), "body")
    tube(k, ab, [(0, 6.4, -3), (0, 5.4, -9), (2, 4.2, -14), (6, 3.4, -17), (10, 3.0, -16), (12, 4.0, -12)],
         lambda t: 3.0 - 2.2 * t, band=5)
    k.shard(ab, (12, 4.0, -12), (0.2, 0.5, 1), 2.4, 1.2, mat="band", tag="tail_spike")
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, (z, j, part) in enumerate(((3.6, 1, body), (-6.6, 4, ab))):
            nm = "leg_%s%d" % (s, i)
            lg = k.part(nm, (side * 2.8, 6.0, z), (), part)
            kn = (side * 7.6, 7.4, z + (1.2 if i == 0 else -1.0))
            ft = (side * 9.4, 0.8, z + (2.4 if i == 0 else 0.6))
            k.limb(lg, (side * 2.8, 6.0, z), kn, 2.2, "scale", "leg")
            k.limb(lg, kn, ft, 1.6, "scale", "shin")
            k.box(lg, C(ft[0], 0, ft[2] + 0.4, 2.8, 1.2, 3.2), "scale", tag="foot")
            for t in (-0.9, 0, 0.9):
                k.shard(lg, (ft[0] + t, 0.6, ft[2] + 1.8), (side * 0.2, -0.4, 1), 1.6, 0.55, mat="bone", tag="claw")
            joints[nm] = ("LL" if side > 0 else "RL") + str(j)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Scaleguard (guard)

def scaleguard():
    """The temple's spearmen were men once; the serpent has had them a long time. A cobra's head on a man's frame,
    its hood flared wide behind the skull, yellow eyes under heavy brows, a mouth that does not close. Jade lamellar
    over a scaled chest, the cream belly showing between the plates, gold pauldrons cast as serpents' heads, a round
    war-shield fringed with plumes and a spear with an obsidian leaf of a blade. A tail drags behind it."""
    k = X.Kit("scaleguard")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(16, 10.6, 7.2), (22, 11.8, 7.8)], "scale", "pelvis")
    k.box(hips, C(0, 20.8, 0, 12.8, 1.8, 8.6), "gold", tag="belt")
    k.box(hips, C(0, 19.6, 4.4, 3.4, 3.4, 0.8), "jade", tag="belt_plaque")
    flap = k.part("flap", (0, 20, 4), (), "hips", bone=False)
    k.stack(flap, 0, 4.4, [(8, 4.4, 0.8), (20, 5.2, 0.8)], "cloth", "loincloth")
    for y in (10, 13, 16):
        k.box(flap, C(0, y, 4.9, 4.8, 0.6, 0.4), "gold", tag="flap_stripe")
    tail = k.part("tail", (0, 18, -3), (("x", 6),), "hips", bone=False)
    tube(k, tail, [(0, 18, -3), (0, 13, -8.6), (0, 7, -13), (2, 3, -18), (5, 1.8, -23), (8, 1.6, -26)],
         lambda t: 3.4 - 2.6 * t, band=4)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.4
        th = k.part("thigh_" + nm, (x, 21, 0), (("x", -4), ("z", side * 4)), "hips")
        sh = k.part("shin_" + nm, (x, 11.4, 0), (("x", 6),), th)
        ft = k.part("foot_" + nm, (x, 2.8, 0), (("x", -2),), sh)
        k.stack(th, x, 0, [(11.6, 5.0, 5.4), (20.4, 6.2, 6.6)], "scale", "thigh")
        k.box(th, C(x, 10.8, 1.4, 4.8, 2.4, 4.4), "gold", tag="knee")
        k.stack(sh, x, 0, [(3, 4.2, 4.6), (11.4, 5.0, 5.4)], "scale", "shin")
        k.box(sh, C(x, 4.0, 2.4, 4.4, 6.8, 1.0), "jade", tag="greave")
        k.box(sh, C(x, 3.0, 0, 5.0, 1.0, 5.4), "gold", tag="anklet")
        k.box(ft, C(x, 0, 1.6, 5.2, 2.8, 7.6), "scale", tag="foot")
        for t in (-1.6, 0, 1.6):
            k.shard(ft, (x + t, 1.2, 5.2), (0, -0.5, 1), 2.4, 0.9, mat="bone", tag="claw")
    # ---------------------------------------------------------------- torso: scaled, jade lamellar, the belly showing
    to = k.part("torso", (0, 22, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(22, 11.8, 7.8), (27, 13.8, 8.4), (32, 17.4, 9.4), (37, 19.6, 9.8), (39.4, 15.4, 8.2)], "scale", "chest")
    for y in range(23, 31, 2):
        k.box(to, C(0, y, 3.9 + (y - 23) * 0.06, 6.4, 1.7, 1.0), "belly", tag="belly")
    for r, y in enumerate((30.6, 32.6, 34.6)):    # three rows of jade lamellar, each row offset
        for i in range(-3, 4):
            x = i * 2.3 + (1.15 if r % 2 else 0)
            if abs(x) > 7.4 - r * 0.2 or (r == 0 and abs(x) < 2):
                continue
            k.box(to, C(x, y, 4.5 + r * 0.25, 2.1, 2.2, 0.9), "jade", tag="lamellar")
            k.box(to, C(x, y + 2.0, 4.6 + r * 0.25, 2.1, 0.3, 1.0), "gold", tag="lace")
    disc(k, to, (0, 34.8, 5.6), 2.4, "z", "gold", "pectoral", thick=0.8)
    disc(k, to, (0, 34.8, 6.0), 1.2, "z", "venom", "pectoral_stone", thick=0.4)
    for side in (1, -1):                          # gold pauldrons cast as serpents' heads, jaws out over the arms
        k.blob(to, (side * 9.8, 36.6, 0), (4.6, 3.0, 5.0), "gold", "pauldron", step=0.9)
        for i in range(3):
            k.box(to, C(side * (10.4 + i * 0.3), 33.8 - i * 1.6, 0, 5.8, 1.4, 8.4), "jade" if i % 2 else "scale", tag="lame")
        ph = k.part("pauldron_" + ("l" if side > 0 else "r"), (side * 10, 38, 0), (("y", side * 90),), to, bone=False)
        snake_head(k, ph, (side * 10, 38.4, -2.6), 0.62, open_=0.3, mat="gold", tag="pauldron")
    k.limb(to, (0, 38, 0.4), (0, 42.6, 1.8), 5.0, "scale", "neck")
    k.box(to, C(0, 38.6, 1.6, 4.0, 3.4, 1.4), "belly", tag="throat")
    # ---------------------------------------------------------------- the cobra's head, its hood flared
    hd = k.part("head", (0, 40, 1), (("x", -6),), "torso")
    hood(k, hd, 0, 36.4, 52.4, -1.6, 15.0, thick=1.4)
    snake_head(k, hd, (0, 42.4, 0.4), 1.3, open_=0.32)
    k.box(hd, C(0, 45.8, 2.6, 2.4, 0.8, 3.4), "gold", tag="diadem")
    k.box(hd, C(0, 46.4, 3.4, 1.2, 1.0, 1.2), "venom", group="glow", tag="diadem_stone")
    # ---------------------------------------------------------------- arms: the plumed shield, the obsidian spear
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 10.4
        up = k.part("arm_" + nm, (x, 36, 0), (("x", -30 if side > 0 else -25), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 27, 0), (("x", -55 if side > 0 else -70),), up)
        hn = k.part("hand_" + nm, (x, 18, 0), (), fo)
        k.limb(up, (x, 35, 0), (x, 27.6, 0), 4.2, "scale", "upper_arm")
        k.box(up, C(x, 30.4, 0, 4.8, 1.4, 4.8), "gold", tag="armband")
        k.limb(fo, (x, 26.6, 0), (x, 19.4, 0), 3.8, "scale", "forearm")
        k.box(fo, C(x, 19.6, 0.2, 4.6, 5.2, 4.6), "jade", tag="bracer")
        k.box(fo, C(x, 24.4, 0.2, 4.8, 0.8, 4.8), "gold", tag="bracer_rim")
        k.box(hn, C(x, 15.4, 0.4, 3.8, 3.6, 4.0), "scale", tag="hand")
        for t in (-1.2, 0, 1.2):
            k.shard(hn, (x + t, 15.6, 2.4), (0, -0.6, 1), 1.8, 0.7, mat="bone", tag="claw")
    sh = k.part("shield", (14, 17, 2), (("y", 10),), k.parts["hand_l"], bone=False)
    disc(k, sh, (15.0, 17.5, 2.0), 8.4, "x", "cotton", "shield", thick=1.4)
    for r, m, w in ((8.4, "gold", 1.0), (6.0, "jade", 1.2), (3.4, "gold", 0.9)):
        for a in range(18):
            a0, a1 = a * math.pi / 9, (a + 1) * math.pi / 9
            k.limb(sh, (15.9, 17.5 + math.sin(a0) * r, 2.0 + math.cos(a0) * r), (15.9, 17.5 + math.sin(a1) * r, 2.0 + math.cos(a1) * r), w, m, "shield_ring")
    for a in range(0, 360, 45):                   # a serpent's coil inlaid: jade scales round the boss
        rr = math.radians(a)
        k.box(sh, C(16.1, 17.0 + math.sin(rr) * 4.7, 2.0 + math.cos(rr) * 4.7, 0.6, 1.2, 1.2), "scale", tag="inlay")
    disc(k, sh, (16.2, 17.5, 2.0), 1.8, "x", "venom", "boss", thick=0.6)
    for i, z in enumerate((-6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0, 8.0, 10.0)):
        top = 17.5 - math.sqrt(max(0.0, 8.4 ** 2 - (z - 2.0) ** 2)) + 0.6
        feather(k, sh, (15.4, top, z), (0.15, -1, 0), 7.0 + (i % 2) * 1.6, 1.5, "plume_r" if i % 2 else "plume", "gold", flat="x")
    sp = k.part("spear", (-10.4, 15.6, 0.6), (("x", 78),), k.parts["hand_r"], bone=False)
    k.limb(sp, (-10.4, -12, 0.6), (-10.4, 41, 0.6), 1.3, "wood", "haft")
    for y in (-10, 4, 18):
        k.box(sp, C(-10.4, y, 0.6, 1.9, 1.2, 1.9), "gold", tag="haft_band")
    for i in range(20):                           # a serpent coiled up the top of the haft
        a, y = i * 0.9, 30 + i * 0.55
        k.box(sp, C(-10.4 + math.cos(a) * 1.0, y, 0.6 + math.sin(a) * 1.0, 1.1, 0.8, 1.1), "band", tag="haft_snake")
    k.box(sp, C(-10.4, 40.6, 0.6, 2.2, 2.0, 2.4), "gold", tag="socket")
    for i in range(9):                            # the obsidian leaf: widest a third of the way up
        y = 42.4 + i * 1.5
        t = i / 8
        w = 1.2 + 3.4 * math.sin(min(1, t / 0.4) * math.pi / 2) * (1 - max(0, t - 0.4) / 0.6 * 0.9)
        k.box(sp, C(-10.4, y, 0.6, 0.8, 1.55, w), "obsidian", tag="blade")
    k.shard(sp, (-10.4, 55.6, 0.6), (0, 1, 0), 2.6, 0.9, mat="obsidian", tag="point")
    for z in (-0.6, 0.6, 1.8):
        feather(k, sp, (-10.4, 40.6, z - 0.6), (0, -1, 0.15 * z), 5.0, 1.0, "plume_r", "gold", flat="x", tag="tassel")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Jaguar Stalker (brute)

def jaguar_stalker():
    """The temple's knights went into the jungle and came back wearing the whole of the beast: the pelt over every
    limb, the paws crossed on the chest, the head worn as a helm with the knight's face in its open jaws and his eyes
    burning out of the dark there. Hunched and huge, gold at the throat and wrists, he swings a macuahuitl as long
    as a man, its edges set with obsidian teeth."""
    k = X.Kit("jaguar_stalker")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(15, 13.6, 9.4), (22, 14.6, 10)], "fur", "pelvis")
    k.box(hips, C(0, 20.6, 0, 15.6, 2.0, 11), "gold", tag="belt")
    flap = k.part("flap", (0, 20, 5), (), "hips", bone=False)
    k.stack(flap, 0, 5.4, [(7, 5.6, 0.9), (20.6, 6.4, 0.9)], "cloth", "loincloth")
    for y in (9, 12):
        k.box(flap, C(0, y, 6.0, 6.0, 0.8, 0.4), "gold", tag="flap_stripe")
    tail = k.part("tail", (0, 16, -5), (), "hips", bone=False)
    tube(k, tail, [(0, 17, -5), (0, 11, -10), (2, 5, -14), (5, 2.4, -19), (8, 3.2, -23), (9, 6, -25)],
         lambda t: 2.2 - 1.0 * t, mat="fur", belly=None)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 4.6
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -10), ("z", side * 8)), "hips")
        sh = k.part("shin_" + nm, (x, 11, 0), (("x", 16),), th)
        ft = k.part("foot_" + nm, (x, 2.8, 0), (("x", -6),), sh)
        k.stack(th, x, 0, [(11, 7.4, 7.8), (20, 9.0, 9.4)], "fur", "thigh")
        k.stack(sh, x, 0, [(3, 6.2, 6.6), (8, 7.4, 7.6), (11, 7.0, 7.4)], "fur", "calf")
        k.box(sh, C(x, 9.6, 0, 7.8, 1.4, 8.0), "gold", tag="garter")
        k.box(ft, C(x, 0, 2.0, 6.8, 3.0, 10.0), "fur", tag="foot")
        for t in (-2.0, -0.7, 0.7, 2.0):
            k.shard(ft, (x + t, 1.0, 7.0), (0, -0.4, 1), 2.0, 0.9, mat="bone", tag="claw")
    # ---------------------------------------------------------------- torso: hunched, the pelt's paws over his chest
    to = k.part("torso", (0, 22, 0), (("x", 16),), "hips")
    k.stack(to, 0, 0, [(22, 14.6, 10), (27, 17.6, 11.4), (33, 23.4, 12.8), (38, 25.6, 12.6), (41.4, 20, 10.6)], "fur", "chest", step=1.2)
    k.box(to, C(0, 23, 5.4, 10, 10, 1.0), "fur_pale", tag="belly")
    k.box(to, C(0, 39.4, 0.4, 21.6, 2.0, 13.4), "gold", tag="collar")
    for i in range(-4, 5):                        # a row of jade beads hanging off the collar
        k.box(to, C(i * 2.1, 37.6 - abs(i) * 0.2, 6.6, 1.4, 1.4, 1.2), "jade", tag="bead")
    k.limb(to, (9, 39, 6.4), (-8, 24, 6.4), 2.6, "cloth", "sash", d=1.0)
    for sx in (-1, 1):                            # the pelt's forelegs over his shoulders, paws hanging on his chest
        k.limb(to, (sx * 7.4, 41, 3.4), (sx * 4.6, 32, 7.6), 3.4, "fur", "pelt_leg")
        k.box(to, C(sx * 4.4, 29.6, 7.6, 4.2, 3.0, 3.4), "fur", tag="pelt_paw")
        for t in (-1.2, 0, 1.2):
            k.shard(to, (sx * 4.4 + t, 30.0, 9.0), (0, -1, 0.3), 1.8, 0.6, mat="bone", tag="pelt_claw")
    for sx in (-1, 1):                            # plumes at the back of the shoulders
        for i in range(4):
            feather(k, to, (sx * (6 + i * 1.6), 40.6, -5.4), (sx * (0.3 + i * 0.2), 1, -0.5), 8.0 - i * 0.8, 1.6,
                    "plume" if i % 2 == 0 else "plume_r", "gold")
    # ---------------------------------------------------------------- the jaguar's head, his face in its jaws
    hd = k.part("head", (0, 40, 3), (("x", -16),), "torso")
    k.box(hd, C(0, 39.6, 4.0, 6.4, 6.2, 5.2), "skin", tag="face")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.5, 43.0, 6.65, 1.5, 0.8, 0.3), "eye", group="glow", tag="eye")
        k.box(hd, C(sx * 1.5, 41.0, 6.65, 0.5, 1.6, 0.3), "bone", tag="warpaint")
    k.box(hd, C(0, 39.8, 6.65, 3.2, 0.6, 0.3), "bone", tag="warpaint")
    k.blob(hd, (0, 47.6, 1.4), (6.8, 4.8, 7.0), "fur", "jaguar_skull", step=0.9)
    k.box(hd, C(0, 44.4, 6.2, 7.4, 4.6, 6.0), "fur", tag="jaguar_muzzle")
    k.box(hd, C(0, 47.6, 10.4, 3.0, 1.6, 1.6), "dark", tag="jaguar_nose")
    k.box(hd, C(0, 44.0, 6.4, 6.2, 1.0, 5.4), "mouth", tag="jaguar_palate")
    for sx in (-1, 1):
        k.shard(hd, (sx * 2.6, 44.6, 10.6), (0, -1, 0.05), 4.4, 1.2, mat="bone", tag="jaguar_fang")
        k.shard(hd, (sx * 1.2, 44.4, 11.0), (0, -1, 0.1), 1.6, 0.6, mat="bone", tag="jaguar_tooth")
        k.box(hd, C(sx * 3.2, 49.2, 7.0, 2.2, 1.6, 1.0), "gold", tag="jaguar_eye_rim")
        k.box(hd, C(sx * 3.2, 49.5, 7.4, 1.4, 1.0, 0.8), "obsidian", tag="jaguar_eye")
        k.shard(hd, (sx * 4.8, 51.0, 0.0), (sx * 0.3, 1, -0.2), 3.0, 2.4, mat="fur", tag="ear")
        k.limb(hd, (sx * 3.2, 38.6, 0), (sx * 2.8, 36.6, 5.2), 1.6, "fur", "jaguar_jaw")
        k.shard(hd, (sx * 2.4, 37.0, 5.6), (0, 1, 0.2), 2.4, 0.9, mat="bone", tag="jaguar_fang")
    # ---------------------------------------------------------------- arms: huge, clawed, the macuahuitl
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 13.6
        up = k.part("arm_" + nm, (x, 38, 0), (("x", -34 if side > 0 else -28), ("z", side * 14)), "torso")
        fo = k.part("fore_" + nm, (x, 27, 0), (("x", -56 if side > 0 else -52),), up)
        hn = k.part("hand_" + nm, (x, 18, 0), (), fo)
        k.blob(up, (x - side * 0.6, 38.4, 0), (5.6, 4.6, 6.0), "fur", "shoulder", step=0.9)
        k.limb(up, (x, 36, 0), (x, 27.6, 0), 6.2, "fur", "upper_arm")
        k.box(up, C(x, 31, 0, 6.8, 1.6, 6.8), "gold", tag="armband")
        k.limb(fo, (x, 26.6, 0), (x, 19.4, 0), 5.6, "fur", "forearm")
        k.box(fo, C(x, 19.6, 0, 6.4, 3.6, 6.4), "gold", tag="bracer")
        k.box(fo, C(x, 21.0, 3.3, 2.0, 1.2, 0.4), "jade", tag="bracer_stone")
        k.box(hn, C(x, 14.8, 0.6, 5.6, 4.6, 5.6), "fur", tag="paw")
        for t in (-1.8, -0.6, 0.6, 1.8):
            k.shard(hn, (x + t, 15.0, 3.2), (0, -0.7, 1), 2.4, 0.9, mat="bone", tag="claw")
    mc = k.part("macuahuitl", (-13.6, 16.4, 0.6), (("x", 62),), k.parts["hand_r"], bone=False)
    k.limb(mc, (-13.6, 8, 0.6), (-13.6, 21, 0.6), 1.8, "wood", "grip")
    k.box(mc, C(-13.6, 7, 0.6, 2.6, 1.6, 2.6), "gold", tag="pommel")
    k.box(mc, C(-13.6, 21, 0.6, 1.6, 30, 6.0), "wood", tag="paddle")
    k.box(mc, C(-13.6, 50.6, 0.6, 1.6, 1.4, 4.4), "wood", tag="paddle_tip")
    for y in range(24, 50, 6):
        k.box(mc, C(-13.6, y, 0.6, 1.8, 1.6, 1.6), "jade", tag="inlay")
        k.box(mc, C(-13.6, y + 2.6, 0.6, 1.8, 0.6, 3.8), "gold", tag="inlay_band")
    obsidian_teeth(k, mc, -13.6, 22.6, 50, 0.6, 3.0, every=2.2, size=2.6)
    for z in (-0.8, 0.8):
        feather(k, mc, (-13.6, 7.4, 0.6 + z), (0, -1, z * 0.3), 6.0, 1.2, "plume_r", "plume", flat="x", tag="tassel")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Venom Priest (caster)

def venom_priest():
    """The serpent's priests are thin as the reeds by the temple pools. A jade mosaic death-mask with green fire
    behind its eyes, a fan of quetzal plumes taller than the priest standing behind its head, the ribs painted white on
    its bare grey-brown chest, a robe to the floor. A live serpent lies across its shoulders and lifts its head when the
    priest speaks; its staff is a serpent climbing a pole to a censer of gold, and the smoke it pours is venom."""
    k = X.Kit("venom_priest")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(16, 10.4, 7.2), (20, 10.6, 7.2)], "cloth", "waist")
    k.box(hips, C(0, 19.0, 0, 11.6, 1.6, 8.2), "gold", tag="belt")
    robe = k.part("robe", (0, 20, 0), (), "hips", bone=False)
    k.stack(robe, 0, -0.4, [(1.2, 15.4, 11.6), (8, 13.4, 9.8), (16, 11.0, 7.8), (20, 10.6, 7.4)], "cloth", "robe")
    k.box(robe, C(0, 1.2, -0.4, 15.8, 1.4, 12.0), "gold", tag="hem")
    k.box(robe, C(0, 2.6, -0.4, 15.6, 0.6, 11.8), "jade", tag="hem")
    for i in range(-2, 3):                        # strings of jade beads hanging down the front of the robe
        x = i * 2.2
        for y in range(16, 4, -2):
            k.box(robe, C(x, y - abs(i) * 0.6, 4.6 + (16 - y) * 0.13, 1.1, 1.1, 1.0), "jade" if (y // 2) % 2 else "gold", tag="beads")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.8
        th = k.part("thigh_" + nm, (x, 19, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 10.4, 0), (), th)
        ft = k.part("foot_" + nm, (x, 2.4, 0), (), sh)
        k.box(ft, C(x, 0, 2.6, 3.8, 1.8, 5.4), "skin", tag="foot")
        k.box(ft, C(x, 1.4, 2.0, 4.0, 0.8, 4.4), "gold", tag="anklet")
    # ---------------------------------------------------------------- torso: gaunt, the ribs painted, a mantle of plumes
    to = k.part("torso", (0, 20, 0), (("x", 8),), "hips")
    k.stack(to, 0, 0, [(20, 10.4, 7.0), (25, 10.8, 6.8), (30, 13.6, 7.6), (34, 12.4, 7.0)], "skin", "chest")
    k.box(to, C(0, 22.4, 3.4, 1.0, 10, 0.4), "bone", tag="painted_spine")
    for y, w in ((24.4, 6.4), (26.4, 7.6), (28.4, 8.6), (30.4, 9.0)):
        for sx in (-1, 1):
            k.box(to, C(sx * (w / 4 + 0.4), y, 3.6 + (y - 24) * 0.05, w / 2 - 0.4, 0.8, 0.4), "bone", tag="painted_rib")
    for i, a in enumerate(range(-150, 151, 20)):  # the mantle: plumes hanging off the shoulders all round
        r = math.radians(a)
        bx, bz = math.sin(r) * 7.2, math.cos(r) * 4.6
        if abs(a) < 30:
            continue
        feather(k, to, (bx, 34.6, bz), (math.sin(r) * 0.5, -1, math.cos(r) * 0.3), 9.0 - (i % 2) * 1.6, 1.8,
                "plume" if i % 2 else "plume_r", "gold", flat="x")
    k.box(to, C(0, 33.4, 0, 14, 1.6, 9.0), "gold", tag="collar")
    # the serpent across its shoulders: tail down the front on the left, head reared beside the priest's on the right
    tube(k, to, [(4.4, 22, 4.6), (5.6, 28, 4.8), (6.6, 34, 2.0), (4, 36.4, -3.4), (-3, 36.4, -3.6), (-6.8, 35, 0.4),
                 (-7.6, 37.6, 4.4), (-8.4, 42.4, 5.6)], lambda t: 0.8 + 0.8 * t, band=4, under=(0, -1, 0))
    hood(k, to, -8.4, 40.0, 47.0, 5.0, 5.6, thick=0.7, mark=False)
    snake_head(k, to, (-8.4, 45.4, 5.6), 0.5, open_=0.5)
    # ---------------------------------------------------------------- the jade death-mask, the plume fan
    hd = k.part("head", (0, 34, 0.6), (("x", -6),), "torso")
    k.box(hd, C(0, 34.2, 0.4, 5.4, 6.4, 5.4), "skin", tag="head")
    k.box(hd, C(0, 34.4, 3.0, 5.8, 6.2, 0.9), "jade", tag="mask")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.3, 37.4, 3.3, 1.8, 1.4, 0.8), "dark", tag="socket")
        k.box(hd, C(sx * 1.3, 37.6, 3.55, 1.0, 0.8, 0.6), "venom", group="glow", tag="eye")
        k.box(hd, C(sx * 2.7, 35.2, 3.2, 0.8, 1.8, 0.8), "gold", tag="mask_inlay")
    k.box(hd, C(0, 36.0, 3.6, 1.0, 1.4, 0.8), "jade", tag="nose")
    k.box(hd, C(0, 34.6, 3.5, 3.4, 1.0, 0.6), "dark", tag="mouth")
    for x in (-1.2, -0.4, 0.4, 1.2):
        k.box(hd, C(x, 34.7, 3.85, 0.5, 0.8, 0.4), "bone", tag="teeth")
    k.box(hd, C(0, 40.2, 0.4, 6.6, 1.8, 6.4), "gold", tag="headband")
    snake_head(k, hd, (0, 41.0, 2.2), 0.55, open_=0.5, mat="gold", tag="brow_serpent")
    for i, a in enumerate(range(-84, 85, 12)):    # the fan of plumes: long green over a shorter scarlet row
        r = math.radians(a)
        feather(k, hd, (math.sin(r) * 2.4, 40.6 + math.cos(r) * 1.4, -2.6), (math.sin(r), math.cos(r), -0.12),
                21.0 - abs(a) * 0.06, 2.2, "plume", "gold")
        if i % 2 == 0:
            feather(k, hd, (math.sin(r) * 2.4, 40.6 + math.cos(r) * 1.4, -1.8), (math.sin(r), math.cos(r), -0.08),
                    12.0 - abs(a) * 0.03, 1.8, "plume_r", "gold")
    # ---------------------------------------------------------------- arms: thin, the serpent staff, a venom orb
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.2
        up = k.part("arm_" + nm, (x, 32, 0), (("x", -50 if side > 0 else -20), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 25, 0), (("x", -40 if side > 0 else -60),), up)
        hn = k.part("hand_" + nm, (x, 18, 0), (), fo)
        k.limb(up, (x, 31.4, 0), (x, 25.6, 0), 2.4, "skin", "upper_arm")
        k.box(up, C(x, 28.0, 0, 3.0, 1.0, 3.0), "gold", tag="armband")
        k.limb(fo, (x, 25, 0), (x, 19, 0), 2.2, "skin", "forearm")
        for y in (19.2, 20.4, 21.6):
            k.box(fo, C(x, y, 0, 2.8, 0.9, 2.8), "jade" if y != 20.4 else "gold", tag="wrist_beads")
        k.box(hn, C(x, 15.8, 0.4, 2.4, 3.0, 2.6), "skin", tag="hand")
    k.blob(k.parts["hand_l"], (7.2, 14.0, 2.8), (2.0, 2.0, 2.0), "venom", "venom_orb", step=0.7)
    for b in k.s.boxes:
        if b.tag == "venom_orb":
            b.group = "glow"
    st = k.part("staff", (-7.2, 15.6, 0.6), (("x", 80),), k.parts["hand_r"], bone=False)
    k.limb(st, (-7.2, -6, 0.6), (-7.2, 44, 0.6), 1.2, "wood", "pole")
    for i in range(44):                           # the serpent climbing the pole
        a, y = i * 0.62, -2 + i * 1.0
        k.box(st, C(-7.2 + math.cos(a) * 1.1, y, 0.6 + math.sin(a) * 1.1, 1.3, 1.1, 1.3), "band" if i % 6 == 0 else "scale", tag="staff_snake")
    snake_head(k, st, (-7.2, 44.6, -0.6), 0.55, open_=0.7, tag="staff_head")
    for a in range(4):                            # the censer hung from its jaws: a gold cage, venom burning in it
        r = math.radians(a * 90 + 45)
        k.limb(st, (-7.2 + math.cos(r) * 2.0, 37.0, 3.6 + math.sin(r) * 2.0), (-7.2 + math.cos(r) * 1.4, 42.6, 3.6 + math.sin(r) * 1.4), 0.5, "gold", "censer_bar")
    k.box(st, C(-7.2, 36.4, 3.6, 4.4, 1.0, 4.4), "gold", tag="censer_dish")
    k.blob(st, (-7.2, 39.4, 3.6), (1.6, 2.0, 1.6), "venom", "censer_fire", step=0.6)
    for i in range(4):
        k.box(st, C(-7.2 + (i % 2) * 0.8 - 0.4, 42.6 + i * 1.8, 3.6 - i * 0.4, 1.4 - i * 0.25, 1.6, 1.4 - i * 0.25), "venom", tag="smoke")
    for b in k.s.boxes:
        if b.tag in ("censer_fire", "smoke"):
            b.group = "glow"
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Feathered Champion (elite)

def feathered_champion():
    """The serpent's chosen fighter keeps the sixth floor. White war-cotton quilted thick under plates of gold and
    jade, a mantle of feathers on its shoulders, and behind it a sunburst of quetzal plumes taller than a man round a
    golden sun. It wears the jaws of the plumed serpent as a helm: the fangs come down past its cheeks and its eyes
    burn in the dark of the mouth. Two obsidian swords; it dances between them."""
    k = X.Kit("feathered_champion")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(16, 11.4, 7.6), (22, 12.2, 8.0)], "cotton", "pelvis")
    k.box(hips, C(0, 20.8, 0, 13.2, 1.8, 8.8), "gold", tag="belt")
    for x in (-4.0, 0, 4.0):
        k.box(hips, C(x, 12.0, 4.4, 3.6, 8.6, 0.8), "jade" if x else "gold", tag="tasset")
        k.box(hips, C(x, 12.0, 4.9, 3.6, 0.8, 0.4), "gold", tag="tasset_rim")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.4
        th = k.part("thigh_" + nm, (x, 21, 0), (("x", -12), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 11.4, 0), (("x", 18),), th)
        ft = k.part("foot_" + nm, (x, 2.8, 0), (("x", -6),), sh)
        k.stack(th, x, 0, [(11.6, 4.8, 5.2), (20.4, 5.8, 6.2)], "cotton", "thigh")
        k.box(th, C(x, 10.6, 1.4, 4.8, 2.6, 4.6), "gold", tag="knee")
        for t in (-1, 0, 1):                      # a tuft of plumes at the knee
            feather(k, th, (x + t * 1.2, 12.0, -2.0), (t * 0.3, 1, -0.6), 4.0, 1.0, "plume_r" if t else "plume", "gold")
        k.stack(sh, x, 0, [(3, 4.0, 4.4), (11.4, 4.8, 5.2)], "skin", "shin")
        k.box(sh, C(x, 3.6, 0.6, 5.0, 7.4, 5.0), "jade", tag="greave")
        k.box(sh, C(x, 10.0, 0.6, 5.2, 0.8, 5.2), "gold", tag="greave_rim")
        k.box(ft, C(x, 0, 1.6, 5.0, 2.6, 7.8), "gold", tag="foot")
    # ---------------------------------------------------------------- torso: war-cotton, the sun on its chest
    to = k.part("torso", (0, 22, 0), (("x", 8),), "hips")
    k.stack(to, 0, 0, [(22, 12.2, 8.0), (27, 13.6, 8.4), (32, 17.2, 9.4), (37, 19.0, 9.6), (39.4, 15, 8.2)], "cotton", "chest")
    disc(k, to, (0, 31.8, 4.9), 4.0, "z", "gold", "sun", thick=0.9)
    disc(k, to, (0, 31.8, 5.4), 2.2, "z", "jade", "sun_stone", thick=0.6)
    disc(k, to, (0, 31.8, 5.8), 0.9, "z", "venom", "sun_heart", thick=0.4)
    for a in range(0, 360, 30):
        r = math.radians(a)
        k.limb(to, (math.cos(r) * 4.2, 31.8 + math.sin(r) * 4.2, 4.9), (math.cos(r) * 6.2, 31.8 + math.sin(r) * 6.2, 4.6), 0.9, "gold", "sun_ray")
    k.box(to, C(0, 37.4, 0, 15.6, 1.8, 9.8), "gold", tag="collar")
    for side in (1, -1):                          # the mantle: three rows of plumes off each shoulder
        for row in range(3):
            for z in (-3.2, -1.6, 0, 1.6, 3.2):
                feather(k, to, (side * (7.8 + row * 0.9), 38.6 - row * 1.8, z), (side * (0.5 + row * 0.15), -1, z * 0.04),
                        6.4 - row * 0.6, 1.5, ("plume", "plume_r", "plume")[row], "gold", flat="x")
    # great feathered wings off its back, half open: a gold-bound wing bone, scarlet coverts, long green primaries
    for side in (1, -1):
        wg = k.part("wing_" + ("l" if side > 0 else "r"), (side * 3.6, 37, -5), (("y", -side * 18),), to, bone=False)
        bone_pts = [(side * 3.6, 37, -5), (side * 13, 46, -8), (side * 24, 50, -9), (side * 32, 47, -9.6)]
        for p0, p1 in zip(bone_pts, bone_pts[1:]):
            k.limb(wg, p0, p1, 2.4, "gold", "wing_bone")
        at, total = _along(bone_pts)
        n = 16
        for i in range(n):
            f = (i + 0.5) / n
            p = at(f * total)
            L = 9.0 + 22.0 * f ** 1.3
            d = (side * (0.15 + 0.55 * f), -1, -0.05)
            feather(k, wg, (p[0], p[1] + 0.6, p[2] - 0.4), d, L, 3.0, "plume", "gold", tag="primary")
            if i % 2 == 0:
                feather(k, wg, (p[0], p[1] + 0.4, p[2] + 0.2), d, L * 0.45, 2.8, "plume_r", "plume_r", tag="covert")
    disc(k, to, (0, 34.0, -5.4), 3.6, "z", "gold", "back_sun", thick=1.0)
    disc(k, to, (0, 34.0, -5.9), 2.0, "z", "jade", "back_sun_stone", thick=0.6)
    # ---------------------------------------------------------------- the serpent-jaw helm
    hd = k.part("head", (0, 39, 0.6), (("x", -8),), "torso")
    k.box(hd, C(0, 38.6, 0.6, 5.4, 6.0, 5.4), "skin", tag="face")
    k.box(hd, C(0, 39.0, 3.35, 4.6, 4.6, 0.3), "dark", tag="shadow")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.3, 41.2, 3.5, 1.4, 0.7, 0.3), "eye", group="glow", tag="eye")
    for i in range(7):                            # the upper jaw: a gold-and-jade snout over the head, reaching forward
        t = i / 6
        z = -3.6 + t * 11.4
        w = 8.0 - 3.6 * t
        k.box(hd, C(0, 43.8 - t * 0.8, z, w, 3.0 - t * 0.8, 1.7), "gold" if i % 2 else "jade", tag="helm_jaw")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.6, 46.2, 0.8, 2.2, 1.2, 3.0), "jade", tag="helm_brow")
        k.box(hd, C(sx * 2.9, 45.6, 2.0, 1.0, 0.8, 1.4), "venom", group="glow", tag="helm_eye")
        k.shard(hd, (sx * 2.2, 43.4, 6.6), (0, -1, -0.05), 5.0, 1.2, mat="bone", tag="helm_fang")
        k.limb(hd, (sx * 3.4, 42, -2), (sx * 3.0, 36.4, 4.8), 1.4, "gold", "helm_lower_jaw")
        k.shard(hd, (sx * 2.8, 37.0, 4.4), (0, 1, 0.1), 2.0, 0.8, mat="bone", tag="helm_tooth")
    for i in range(7):                            # the crest: a tall comb of plumes up and back off the helm
        feather(k, hd, (0, 46.0, 3.0 - i * 1.1), (0, 1, -0.25 - i * 0.22), 13.0 - abs(i - 2) * 0.9, 2.4,
                "plume" if i % 2 == 0 else "plume_r", "gold")
    k.blob(hd, (0, 45.0, 1.0), (4.6, 2.4, 5.4), "gold", "helm_cap", step=0.8)
    # ---------------------------------------------------------------- arms: two obsidian swords
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 9.6
        up = k.part("arm_" + nm, (x, 36, 0), (("x", -62), ("z", side * 20)), "torso")
        fo = k.part("fore_" + nm, (x, 27, 0), (("x", -36),), up)
        hn = k.part("hand_" + nm, (x, 18, 0), (), fo)
        k.limb(up, (x, 35, 0), (x, 27.6, 0), 3.8, "cotton", "upper_arm")
        k.box(up, C(x, 30, 0, 4.4, 1.6, 4.4), "gold", tag="armband")
        k.limb(fo, (x, 26.6, 0), (x, 19.4, 0), 3.4, "skin", "forearm")
        k.box(fo, C(x, 19.6, 0, 4.2, 5.0, 4.2), "gold", tag="bracer")
        k.box(fo, C(x, 21.4, 2.2, 1.6, 1.6, 0.4), "jade", tag="bracer_stone")
        k.box(hn, C(x, 15.6, 0.4, 3.2, 3.0, 3.2), "skin", tag="hand")
        bl = k.part("blade_" + nm, (x, 16.2, 0.4), (("x", 34),), hn, bone=False)
        k.limb(bl, (x, 13.6, 0.4), (x, 17.6, 0.4), 1.2, "wood", "grip")
        k.box(bl, C(x, 17.4, 0.4, 1.4, 1.0, 3.6), "gold", tag="guard")
        k.box(bl, C(x, 18.2, 0.4, 1.0, 17, 3.4), "wood", tag="paddle")
        k.box(bl, C(x, 35.0, 0.4, 1.0, 1.2, 2.2), "wood", tag="paddle_tip")
        obsidian_teeth(k, bl, x, 19.4, 35, 0.4, 1.7, every=1.9, size=1.9)
        k.box(bl, C(x, 22, 0.4, 1.2, 10, 0.8), "jade", tag="inlay")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Coiled King (boss)

def coiled_king():
    """What sleeps on the roof under the stone serpent's head is its son. A naga lord ten blocks high: a tail as
    thick as an ox coiled twice on the stones with its tip raised behind like a scorpion's; a man's torso armoured in
    scales and a collar of beaten gold; a crowned serpent's head under a hood as wide as a house, and round the rim of
    the hood seven more heads, each hooded, each with its own eyes and its own venom. Four arms: a serpent glaive, the
    Disc of the Coil, and two obsidian knives dripping green."""
    k = X.Kit("coiled_king")
    hips = k.part("hips", (0, 30, 0))

    def under(t):
        return (0, 0, 1) if t < 0.14 else (0, -1, 0)

    def rad(t):
        return 8.4 - 4.6 * t
    # off the waist it bellies forward and down, then lies in a great loop round the king, one arch lifted off the
    # stones, and the tail comes up behind his left shoulder with a blade on its tip
    coil = [(0, 32, 0), (0, 25, 3.6), (0.6, 18, 7.6), (2.4, 11, 10.6)]
    turns = 1.2
    for i in range(1, 49):
        t = i / 48
        a = math.pi * 0.42 - t * turns * 2 * math.pi
        R = 14.0 + t * 13.0
        lift = 7.0 * max(0.0, math.sin((t - 0.3) / 0.3 * math.pi)) if 0.3 < t < 0.6 else 0.0
        r = rad(0.14 + 0.66 * t)
        coil.append((math.cos(a) * R + 1.0, r * 0.9 + lift, -5 + math.sin(a) * R))
    tube(k, hips, coil, lambda t: rad(min(1.0, t * 1.1)), band=6, step=1.6, under=under)
    for b in k.s.boxes:                           # what it rests on
        if b.tag == "belly" and b.lo[1] < 3:
            b.tag = "foot"
    end = coil[-1]
    tail = [end, (end[0] + 2, end[1] + 6, end[2] - 4), (end[0] + 3, end[1] + 18, end[2] - 4), (end[0] + 1, end[1] + 30, end[2]),
            (end[0] - 2, end[1] + 36, end[2] + 4)]
    tube(k, hips, tail, lambda t: 4.4 - 2.6 * t, band=3, step=1.2, under=(0, 0, 1))
    tip = tail[-1]
    k.shard(hips, tip, (-0.3, 0.2, 1), 8.0, 3.0, mat="obsidian", tag="tail_blade")
    for sx in (-1, 1):
        k.shard(hips, (tip[0], tip[1] + sx * 1.6, tip[2]), (0, sx, 0.4), 4.0, 1.6, mat="gold", tag="tail_barb")
    k.box(hips, C(0, 28.4, 0, 21, 2.6, 15.6), "gold", tag="belt")
    disc(k, hips, (0, 29.6, 7.6), 2.4, "z", "jade", "belt_stone", thick=0.8)
    for side, nm in ((1, "l"), (-1, "r")):       # the legs a biped's bones want, lost inside the coil
        x = side * 5.0
        th = k.part("thigh_" + nm, (x, 28, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 18, 0), (), th)
        k.part("foot_" + nm, (x, 8, 0), (), sh)
    # ---------------------------------------------------------------- torso: scaled, the gold collar
    to = k.part("torso", (0, 30, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(30, 20, 13.4), (36, 24, 15), (43, 30, 16.6), (50, 34, 16.8), (55, 28, 14)], "scale", "chest", step=1.2)
    for y in range(31, 49, 2):
        f = (y - 30) / 25
        k.box(to, C(0, y, 6.8 + f * 1.6, 11.6 - f * 2, 1.8, 1.4), "belly", tag="belly")
    for row in range(3):                          # the collar: three rings of gold and jade plates over the chest
        for a in range(-72, 73, 12):
            r = math.radians(a)
            R = 9.4 + row * 2.6
            k.box(to, C(math.sin(r) * R, 53.6 - row * 2.4 - (1 - math.cos(r)) * 3.0, 8.0 + math.cos(r) * 0.8, 2.6, 2.6, 1.2),
                  ("gold", "jade", "gold")[row], tag="collar")
    disc(k, to, (0, 42.6, 9.0), 3.8, "z", "gold", "pendant", thick=1.0)
    disc(k, to, (0, 42.6, 9.6), 2.4, "z", "jade", "pendant_stone", thick=0.6)
    disc(k, to, (0, 42.6, 10.0), 1.2, "z", "venom", "pendant_heart", thick=0.5)
    for side in (1, -1):                          # gold pauldrons, flared like small hoods
        k.blob(to, (side * 16.4, 54.6, 0), (6.4, 4.4, 6.8), "gold", "pauldron", step=1.0)
        for i in range(3):
            k.box(to, C(side * (17.2 + i * 0.4), 50.6 - i * 2.0, 0, 7.4, 1.8, 11.4), "jade" if i % 2 else "scale", tag="lame")
        k.shard(to, (side * 18.4, 57.8, 0), (side * 0.6, 1, -0.2), 5.6, 2.2, mat="gold", tag="pauldron_spike")
    # ---------------------------------------------------------------- the head, the crown, the hood of seven heads
    hd = k.part("head", (0, 55, 1), (("x", -4),), "torso")
    k.limb(hd, (0, 54, 0.6), (0, 60, 1.6), 9.0, "scale", "neck")
    k.box(hd, C(0, 54.4, 4.8, 6.4, 5.6, 1.4), "belly", tag="throat")
    snake_head(k, hd, (0, 60.6, 0.4), 2.6, open_=0.42, mat="band")
    k.box(hd, C(0, 67.2, 2.6, 9.6, 2.0, 7.2), "gold", tag="crown")
    for i, x in enumerate((-4.0, -2.0, 0, 2.0, 4.0)):
        k.shard(hd, (x, 69.0, 2.6 + (0.6 if i == 2 else 0)), (x * 0.06, 1, -0.1), 7.0 - abs(x) * 0.6, 1.6, mat="gold", tag="crown_spike")
        k.box(hd, C(x, 68.2, 6.1, 1.2, 1.2, 0.5), "venom" if i == 2 else "jade", tag="crown_stone")
    hood(k, hd, 0, 48, 90, -5.0, 48.0, thick=2.6)
    hc = (0, 64, -3.0)
    for i, a in enumerate(range(-90, 91, 30)):   # seven hooded heads round the rim, each its own, reaching out
        r = math.radians(a)
        base = (hc[0] + math.sin(r) * 16.0, hc[1] + math.cos(r) * 14.0, hc[2] - 0.6)
        tip = (hc[0] + math.sin(r) * 25.0, hc[1] + math.cos(r) * 22.0 + 2.0, hc[2] + 4.0)
        tube(k, hd, [base, tip], 2.4, band=3, under=(0, 0, 1), step=1.2)
        hood(k, hd, tip[0], tip[1] - 4.0, tip[1] + 6.0, tip[2] - 1.2, 9.0, thick=1.0, mark=False)
        snake_head(k, hd, (tip[0], tip[1] + 0.2, tip[2]), 1.05, open_=0.35 + 0.2 * (i % 2))
        k.limb(hd, (hc[0] + math.sin(r) * 4.0, hc[1] + math.cos(r) * 4.0, hc[2] - 1.9), (base[0], base[1], hc[2] - 1.9), 0.9, "venom", "vein", group="glow")
    # ---------------------------------------------------------------- four arms: glaive, disc, two venom knives
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 19.6
        up = k.part("arm_" + nm, (x, 52, 0), (("x", -30 if side > 0 else -20), ("z", side * 16)), "torso")
        fo = k.part("fore_" + nm, (x, 38, 0), (("x", -50 if side > 0 else -60),), up)
        hn = k.part("hand_" + nm, (x, 25, 0), (), fo)
        k.limb(up, (x, 51, 0), (x, 39, 0), 6.6, "scale", "upper_arm")
        k.box(up, C(x, 44, 0, 7.4, 2.0, 7.4), "gold", tag="armband")
        k.limb(fo, (x, 37.6, 0), (x, 26.4, 0), 6.0, "scale", "forearm")
        k.box(fo, C(x, 26.6, 0, 7.2, 6.4, 7.2), "gold", tag="bracer")
        k.box(fo, C(x, 29.0, 3.7, 2.4, 2.4, 0.6), "jade", tag="bracer_stone")
        k.box(hn, C(x, 21.2, 0.6, 6.0, 5.2, 6.4), "scale", tag="hand")
        for t in (-2.0, -0.7, 0.7, 2.0):
            k.shard(hn, (x + t, 21.6, 3.6), (0, -0.8, 1), 3.0, 1.0, mat="bone", tag="claw")
    gl = k.part("glaive", (-19.6, 22.8, 0.6), (("x", 74),), k.parts["hand_r"], bone=False)
    k.limb(gl, (-19.6, -10, 0.6), (-19.6, 52, 0.6), 2.2, "wood", "haft")
    for y in (-8, 10, 30):
        k.box(gl, C(-19.6, y, 0.6, 3.0, 1.6, 3.0), "gold", tag="haft_band")
    snake_head(k, gl, (-19.6, 52.4, -2.6), 0.9, open_=0.6, mat="gold", tag="glaive_head")
    for i in range(14):                           # the blade: a wavy obsidian tongue out of the gold serpent's jaws
        y = 54 + i * 2.0
        off = math.sin(i * 0.9) * 1.4
        w = 5.4 - i * 0.28
        k.box(gl, C(-19.6, y, 2.6 + off, 1.4, 2.05, w), "obsidian", tag="blade")
        k.box(gl, C(-19.6, y, 2.6 + off + w / 2, 1.5, 2.05, 0.6), "venom", tag="edge")
    for b in k.s.boxes:
        if b.tag == "edge":
            b.group = "glow"
    k.shard(gl, (-19.6, 82, 2.6), (0, 1, 0.1), 4.0, 1.6, mat="obsidian", tag="point")
    dc = k.part("disc", (24, 22, 1), (("y", 6),), k.parts["hand_l"], bone=False)
    disc(k, dc, (24.6, 22.0, 1.0), 9.6, "x", "gold", "disc", thick=1.6)
    disc(k, dc, (25.4, 22.0, 1.0), 6.6, "x", "jade", "disc_inner", thick=0.8)
    for i in range(36):                           # a serpent spiralled in, head at the heart
        a = i * 0.42
        r = 1.4 + i * 0.14
        k.box(dc, C(25.9, 22.0 + math.sin(a) * r - 0.4, 1.0 + math.cos(a) * r, 0.6, 0.9, 0.9), "venom" if i < 4 else "scale", tag="disc_coil")
    for a in range(0, 360, 30):
        r = math.radians(a)
        k.shard(dc, (24.6, 22.0 + math.sin(r) * 9.4, 1.0 + math.cos(r) * 9.4), (0, math.sin(r), math.cos(r)), 3.4, 1.4, mat="obsidian", tag="disc_tooth")
    for side in (1, -1):                          # the lower arms, each a venom knife
        x0, x1 = side * 12.4, side * 18.0
        lo = k.part("low_arm_" + ("l" if side > 0 else "r"), (x0, 40, 0), (("x", -50), ("z", side * 24)), to, bone=False)
        k.limb(lo, (x0, 40, 0), (x1, 32, 3.0), 4.6, "scale", "low_upper")
        k.box(lo, C(x1, 30.6, 3.0, 5.0, 3.0, 5.0), "gold", tag="low_elbow")
        k.limb(lo, (x1, 31, 3.0), (x1 + side * 0.6, 23, 7.4), 4.0, "scale", "low_fore")
        k.box(lo, C(x1 + side * 0.6, 20.6, 7.6, 4.4, 3.6, 4.4), "scale", tag="low_hand")
        k.box(lo, C(x1 + side * 0.6, 20.2, 9.8, 4.4, 0.9, 1.4), "gold", tag="knife_guard")
        k.shard(lo, (x1 + side * 0.6, 20.6, 10.2), (0, -0.25, 1), 10.0, 2.2, mat="obsidian", tag="knife")
        k.box(lo, C(x1 + side * 0.6, 19.4, 15.6, 0.8, 1.4, 0.8), "venom", group="glow", tag="knife_venom")
    grow(k, 1.5)
    k.s.shaders = shaders()
    return k.s, k.parts


def grow(k, f):
    """scale a whole monster about its feet: every box and every part's pivot"""
    parts = {id(b.part): b.part for b in k.s.boxes}
    for p in list(parts.values()):
        q = getattr(p, "parent", None)
        while q is not None and id(q) not in parts:
            parts[id(q)] = q
            q = getattr(q, "parent", None)
    for p in k.parts.values():
        parts.setdefault(id(p), p)
    for p in parts.values():
        p.pivot = tuple(c * f for c in p.pivot)
    for b in k.s.boxes:
        b.lo = tuple(c * f for c in b.lo)
        b.size = tuple(c * f for c in b.size)
        b.pivot = tuple(c * f for c in b.pivot)


MOBS = {
    "coilspawn": dict(make=coilspawn, rig="crawler", ent=(1.2, 1.3), stats=dict(hp=24, speed=0.36, dmg=6, armor=3, kb=0)),
    "scaleguard": dict(make=scaleguard, ent=(1.2, 3.4), stats=dict(hp=72, speed=0.23, dmg=11, armor=9, kb=0.5)),
    "jaguar_stalker": dict(make=jaguar_stalker, ent=(1.7, 3.8), stats=dict(hp=130, speed=0.27, dmg=17, armor=7, kb=0.8)),
    "venom_priest": dict(make=venom_priest, ent=(0.9, 3.0), stats=dict(hp=42, speed=0.22, dmg=7, armor=2, kb=0)),
    "feathered_champion": dict(make=feathered_champion, ent=(1.1, 3.4), stats=dict(hp=250, speed=0.33, dmg=14, armor=9, kb=0.6), key=True),
    "coiled_king": dict(make=coiled_king, texel=1, ent=(3.8, 9.0), stats=dict(hp=950, speed=0.2, dmg=24, armor=12, kb=1.0), boss=True),
}
