"""The Salt-Cursed: a desert host that drank from a cursed well and turned half to salt, who hold the world's
pyramids, desert ruins, temples, palaces and occupied villages, built by hand (tools/vox2.py). White salt grown in
crystals over flesh burned black and cracked, crimson rags, bleached bone and black obsidian, and the blood-red
light of the curse in their cracks and eyes. (Not the Sandsunk Tomb's mummies nor the Minaret's turquoise djinn.)

    bone_hyena      swarm   a hyena with its hide split to the bone, salt in the splits, a black bristle mane
    salt_legionary  guard   a soldier crusted in salt, face wrapped, a khopesh and a tall hide shield with a red eye
    dune_behemoth   brute   a giant in a ram's-skull helm, salt crystals down his back, an obelisk for a club
    vulture_priest  caster  gaunt under a vulture-skull headdress and a cloak of black feathers, a censer of red smoke
    sand_reaver     skirm   wrapped head to foot in crimson, salt crystals at the joints, a katar on each fist
    salt_khan       elite   the khan: crimson and gold over cracked black skin, a crown of salt crystals, hyena pelts
                            for a mantle, a great glaive with a blade of red-veined salt

    python tools/monsterforge.py salt_cursed --preview ; python tools/mobsheet.py salt_cursed
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import grow
from _folk import lit, eyes, straps, legs, arms, held, quad

SALT = ramp("#5a5250", "#7c7270", "#a0948e", "#c2b6ae", "#e0d6ce", "#f6f0ea")
CHAR = ramp("#080606", "#100c0a", "#1a1210", "#241816", "#30201c")
CRIMSON = ramp("#1e0406", "#340808", "#4e0c0c", "#6a1210", "#881a14", "#a6261c")
BONE = ramp("#3a3228", "#5c5242", "#80745e", "#a4987c", "#c6bc9e")
OBSID = ramp("#040406", "#0a0a10", "#12121a", "#1c1c26", "#28283a")
GOLD = ramp("#2a1c06", "#4a320a", "#765412", "#a47c20", "#cca232", "#ecc85a")
HIDE = ramp("#1a120a", "#2a1c10", "#3c2a18", "#503820", "#664a2c")
HYENA = ramp("#1e160e", "#302416", "#463420", "#5c462c", "#74583a", "#8c6c48")
FEATH = ramp("#060606", "#0e0c0c", "#161414", "#201c1c", "#2c2626")
CURSE = ramp("#3a0204", "#6a0408", "#a00c10", "#d8241c", "#ff5a40", "#ffb0a0")


def shaders():
    cracks = lambda p, n, i, j, w, h: -0.3 if (i * 3 + j) % 9 == 0 or (i + j * 5) % 13 == 0 else 0.04
    return {
        "salt": X.facets(SALT, 0.06),
        "char": X.veined(CHAR, CURSE, 0.24, 0.018),
        "crimson": X.surf(CRIMSON, 0.5, 1.1, 0.22, 0.04, holes=True, crust=(SALT, 0.22)),
        "bone": X.surf(BONE, 0.56, 1.2, 0.16, 0.12, crust=(SALT, 0.2)),
        "obsidian": X.surf(OBSID, 0.66, 1.6, 0.06, 0.34),
        "gold": X.surf(GOLD, 0.56, 1.5, 0.12, 0.24),
        "hide": X.surf(HIDE, 0.5, 1.1, 0.22, 0.06, crust=(SALT, 0.18)),
        "hyena": X.surf(HYENA, 0.5, 1.1, 0.24, 0.04, pattern=lambda p, n, i, j, w, h: -0.2 if (i * 7 + j * 3) % 10 == 0 else 0.03),
        "feather": X.surf(FEATH, 0.5, 1.1, 0.2, 0.02, pattern=lambda p, n, i, j, w, h: -0.12 if j % 3 == 0 else 0.04),
        "stone": X.surf(BONE, 0.48, 1.2, 0.2, 0.14, pattern=cracks),
        "leather": X.surf(HIDE, 0.48, 1.1, 0.2, 0.04),
        "curse": X.glow(CURSE),
        "eye": X.glow(CURSE, 0.84, 0.14),
        "dark": X.dark(CHAR),
    }


GLOWS = {"curse", "eye"}


def salt_crust(k, part, at, n, L, up=(0, 1, 0), seed=1, spread=0.6):
    """salt crystals growing out of something"""
    k.cluster(part, at, n, L, L * 0.4, mat="salt", seed=seed, spread=spread, up=up)


def wraps(k, part, x, y0, y1, w, d, mat="crimson", step=1.6):
    """cloth wound round a limb in bands"""
    y = y0
    while y < y1:
        k.box(part, C(x, y, 0, w, step * 0.7, d), mat, tag="wrap")
        y += step


# ================================================================ the Bone Hyena (swarm)

def bone_hyena():
    """The curse took the hyenas first. Their hides split along the spine and the ribs and the salt grew in the
    splits; what's left is a hyena's grin, a black bristle mane, a hunch, red light in the eyes and the cracks."""
    k = X.Kit("bone_hyena")
    body, hd, ab, joints = quad(k, "hyena", y=14, chest=((7, 11, 13), (12, 14, 15), (18, 12.6, 13.6)), haunch=((7, 9.6, 9), (11, 10.6, 10), (14.6, 9.4, 9)),
                                leg_w=3.6, foot_w=2.6, front_z=5, back_z=-8, x=4.6, head_at=(0, 15, 8), head_rot=4, claw="bone", foot_len=4.4)
    k.blob(body, (0, 19.6, 0), (4.4, 2.6, 6.4), "hyena", "hunch", step=0.8)
    for z in (-6, -2, 2, 6):                      # the mane, black bristles down the spine
        k.cluster(body if z > -4 else ab, (0, 21.0 - abs(z) * 0.3, z), 3, 3.4, 1.0, mat="dark", seed=z + 20, spread=0.4, up=(0, 1, -0.4))
    for sx in (-1, 1):                            # the ribs split open, salt in the splits
        for z in (-1.0, 2.0, 5.0):
            k.box(body, C(sx * 7.0, 11.0, z, 0.4, 5.0, 1.0), "bone", tag="rib")
            k.box(body, C(sx * 7.1, 11.6, z + 1.2, 0.3, 4.0, 0.6), "curse", tag="crack")
        salt_crust(k, body, (sx * 6.4, 15.0, -2.0), 3, 2.4, up=(sx, 0.6, 0), seed=sx + 3)
    salt_crust(k, ab, (0, 16.0, -9.0), 4, 3.0, up=(0, 1, -0.4), seed=9)
    k.box(hd, C(0, 12.0, 11.4, 7.0, 6.6, 6.4), "hyena", tag="head")
    k.box(hd, C(0, 11.2, 16.8, 4.4, 4.0, 5.0), "hyena", tag="muzzle")
    k.box(hd, C(0, 14.0, 21.0, 2.4, 1.2, 0.6), "dark", tag="nose")
    k.box(hd, C(0, 11.4, 19.4, 4.6, 1.0, 2.8), "dark", tag="grin")
    for t in (-1.6, -0.6, 0.6, 1.6):
        k.shard(hd, (t, 12.4, 20.6 - abs(t) * 0.6), (0, -1, 0.1), 1.6 if abs(t) > 1 else 1.0, 0.6, mat="bone", tag="fang")
    k.box(hd, C(1.8, 11.6, 14.6, 2.0, 4.0, 0.4), "bone", tag="cheek_bone")      # the face split to the bone
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.0, 16.0, 14.7, 1.4, 0.8, 0.4), "eye", tag="eye")
        k.shard(hd, (sx * 2.8, 18.4, 10.0), (sx * 0.3, 1, -0.2), 4.0, 2.4, mat="hyena", tag="ear")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Salt Legionary (guard)

def salt_legionary():
    """The khan's soldiers still stand guard where they drank. Salt has grown over them like frost over a fence -
    in crusts on the shoulders and the arms, in crystals out of the back - their faces are wound in crimson with only
    the red eyes showing, and they carry the khopesh and the tall hide shield with the khan's red eye painted on it."""
    k = X.Kit("salt_legionary")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(12, 11.4, 8.0), (20, 11.0, 7.6)], "crimson", "kilt")
    for x in (-3.6, 0, 3.6):
        k.box(hips, C(x, 11.6, 4.0, 3.0, 8.4, 0.7), "hide", tag="kilt_strap")
    k.box(hips, C(0, 19.0, 0, 12.0, 2.0, 8.4), "gold", tag="belt")
    legs(k, hips, 19, 10.4, 3.2, "char", "char", knee_mat=None, lean=-6, bend=8, w=4.8, cuff=False)
    for side in (1, -1):
        nm = "shin_" + ("l" if side > 0 else "r")
        wraps(k, k.parts[nm], side * 3.2, 3.0, 9.8, 5.4, 5.8)
        salt_crust(k, k.parts["thigh_" + ("l" if side > 0 else "r")], (side * 4.6, 15.0, 1.0), 2, 2.0, up=(side, 0.4, 0.4), seed=side + 5)
    to = k.part("torso", (0, 20, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(20, 11.0, 7.6), (25, 12.4, 8.2), (30, 14.6, 8.8), (34, 14.4, 8.4)], "char", "torso")
    k.box(to, C(0, 21.0, 4.0, 10.6, 10.0, 0.8), "hide", tag="cuirass")
    k.box(to, C(0, 31.0, 4.2, 10.0, 2.6, 0.8), "gold", tag="collar")
    for sx in (-1, 1):
        k.blob(to, (sx * 7.2, 32.0, 0), (3.0, 2.2, 3.6), "salt", "shoulder_salt", step=0.6)
        salt_crust(k, to, (sx * 7.6, 33.0, 0), 4, 3.4, up=(sx * 0.5, 1, 0), seed=sx + 2)
    salt_crust(k, to, (0, 30.0, -4.4), 5, 4.4, up=(0, 0.6, -1), seed=7)
    hd = k.part("head", (0, 34, 0.6), (("x", -4),), "torso")
    k.box(hd, C(0, 34.4, 0.6, 6.2, 7.0, 6.2), "crimson", tag="head_wrap")
    for y in (35.0, 37.2, 39.4):
        k.box(hd, C(0, y, 0.6, 6.6, 0.8, 6.6), "crimson", tag="wrap")
    k.box(hd, C(0, 37.6, 3.75, 5.0, 1.2, 0.3), "dark", tag="eye_slit")
    eyes(k, hd, 37.8, 3.85, 1.3, 1.2)
    k.box(hd, C(0, 41.0, 0.6, 6.6, 1.6, 6.6), "gold", tag="circlet")
    salt_crust(k, hd, (2.0, 41.0, -1.0), 3, 2.6, up=(0.4, 1, -0.4), seed=11)
    arms(k, to, 7.6, 32, "char", {1: ((("x", -40), ("z", -8)), (("x", -40),)), -1: ((("x", -30), ("z", 8)), (("x", -48),))}, w=3.4)
    for side in (1, -1):
        wraps(k, k.parts["fore_" + ("l" if side > 0 else "r")], side * 7.6, 17.0, 23.0, 3.8, 3.8)
    sh = held(k, "shield", "l", (7.6, 13, 0.4), (("x", 80),))          # the tall hide shield, round-topped
    k.box(sh, C(6.8, 2.0, 3.0, 9.0, 18.0, 1.2), "hide", tag="shield")
    k.blob(sh, (6.8, 20.0, 3.0), (4.5, 3.0, 0.6), "hide", "shield_top", step=0.6)
    k.box(sh, C(6.8, 1.6, 3.0, 9.6, 0.8, 1.6), "gold", tag="shield_rim")
    for sx in (-1, 1):
        k.box(sh, C(6.8 + sx * 4.6, 1.6, 3.0, 0.8, 19.0, 1.6), "gold", tag="shield_rim")
    k.blob(sh, (6.8, 13.0, 3.8), (2.8, 1.6, 0.3), "crimson", "painted_eye", step=0.4)
    k.box(sh, C(6.8, 12.4, 4.1, 1.4, 1.4, 0.3), "curse", tag="painted_pupil")
    k.box(sh, C(6.8, 8.0, 3.7, 0.6, 4.0, 0.3), "crimson", tag="painted_tear")
    kh = held(k, "khopesh", "r", (-7.6, 14.0, 0.3), (("x", 84),))
    k.limb(kh, (-7.6, 10.0, 0.3), (-7.6, 15.0, 0.3), 1.2, "leather", "grip")
    k.box(kh, C(-7.6, 9.0, 0.3, 1.6, 1.2, 1.6), "gold", tag="pommel")
    k.limb(kh, (-7.6, 15.0, 0.3), (-7.6, 21.0, 0.3), 1.0, "obsidian", "khopesh_shaft", d=1.8)
    pts = [(-7.6, 21.0, 0.3), (-7.6, 25.0, 2.0), (-7.6, 27.0, 5.4), (-7.6, 25.6, 8.4)]  # the sickle-curve of the blade
    for (a, b), w in zip(zip(pts, pts[1:]), (3.4, 3.6, 3.0)):
        k.limb(kh, a, b, 0.8, "obsidian", "khopesh_blade", d=w)
    k.shard(kh, pts[-1], (0, -0.6, 0.6), 2.2, 0.8, mat="obsidian", tag="blade_tip")
    k.box(kh, C(-7.6, 24.0, 2.6, 0.9, 2.0, 1.0), "curse", tag="blade_vein")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Dune Behemoth (brute)

def dune_behemoth():
    """The khan's giant carried his throne across the desert; it carries an obelisk now. A giant burned black and
    split with red, salt grown in a ridge of crystals down its spine, a ram's skull for a helm with the horns curled
    round its ears, crimson rags at the waist, gold rings round its arms - and in its hands a stone obelisk cut
    with the khan's victories, swung like a club."""
    k = X.Kit("dune_behemoth")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(12, 15, 10.6), (21, 16, 11.4)], "crimson", "loincloth")
    k.box(hips, C(0, 20.0, 0, 16.6, 2.8, 12.0), "gold", tag="belt")
    for i, x in enumerate((-5.4, 0, 5.4)):
        k.box(hips, C(x, 6.0 + i % 2 * 2.0, 5.6, 4.0, 14.0 - i % 2 * 2.0, 0.8), "crimson", tag="rag")
    legs(k, hips, 20, 11.0, 4.8, "char", "char", knee_mat=None, lean=-4, bend=6, w=7.0, cuff=False)
    for side in (1, -1):
        k.box(k.parts["shin_" + ("l" if side > 0 else "r")], C(side * 4.8, 7.0, 0, 8.0, 2.0, 8.4), "gold", tag="ankle_ring")
    to = k.part("torso", (0, 21, 0), (("x", 14),), "hips")
    k.stack(to, 0, 0, [(21, 16, 11.4), (26, 19, 12.6), (31, 23, 13.4), (35, 24, 13.0), (37.6, 19, 10.6)], "char", "chest")
    for sx in (-1, 1):
        k.blob(to, (sx * 4.4, 32.0, 5.0), (4.0, 3.0, 1.4), "char", "pec", step=0.8)
    for z, s in ((-2, 1.0), (-5, 1.2), (-7, 1.0)):    # the salt ridge down the spine
        salt_crust(k, to, (0, 36.0 + z * 1.4, z - 0.4), 4, 5.4 * s, up=(0, 0.7, -1), seed=int(z + 40), spread=0.5)
    for sx in (-1, 1):
        k.blob(to, (sx * 12.4, 35.0, 0), (5.0, 3.6, 5.6), "salt", "shoulder_salt", step=0.8)
        salt_crust(k, to, (sx * 13.0, 37.0, 0), 4, 4.6, up=(sx * 0.5, 1, 0), seed=sx + 14)
    hd = k.part("head", (0, 37.0, 3.0), (("x", -14),), "torso")
    k.box(hd, C(0, 37.4, 4.4, 7.4, 7.4, 7.4), "char", tag="head")
    # the ram skull: a long bone face down over its own, the sockets with the red behind, horns curling round
    k.box(hd, C(0, 38.4, 7.6, 6.4, 6.4, 3.0), "bone", tag="ram_skull")
    k.box(hd, C(0, 36.0, 10.4, 4.0, 3.6, 2.4), "bone", tag="ram_snout")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.8, 41.6, 9.15, 1.8, 1.4, 0.3), "dark", tag="socket")
        k.box(hd, C(sx * 1.8, 41.8, 9.2, 1.0, 0.8, 0.3), "eye", tag="eye")
        pts = [(sx * 3.4, 44.0, 5.0), (sx * 7.0, 45.0, 3.4), (sx * 8.6, 42.0, 1.4), (sx * 7.6, 38.6, 2.4), (sx * 6.4, 37.4, 5.6)]
        for (a, b), w in zip(zip(pts, pts[1:]), (3.4, 3.0, 2.6, 2.0)):
            k.limb(hd, a, b, w, "bone", "ram_horn")
    arms(k, to, 13.0, 34, "char", {1: ((("x", -60), ("z", -18)), (("x", -40),)), -1: ((("x", -70), ("z", 18)), (("x", -30),))}, w=6.4, long=1.15)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        for y in (22.0, 24.0):
            k.ring(k.parts["fore_" + nm], side * 13.0, y, 0, 3.6, 1.0, "gold", "arm_ring", n=10, axis="y")
    ob = held(k, "obelisk", "r", (-13.0, 14.0, 0.4), (("x", 120), ("z", 16)))
    k.limb(ob, (-13.0, 4.0, 0.4), (-13.0, 16.0, 0.4), 2.6, "leather", "grip")
    k.stack(ob, -13.0, 0.4, [(16.0, 7.0, 7.0), (24.0, 6.2, 6.2), (32.0, 5.4, 5.4), (38.0, 4.6, 4.6)], "stone", "obelisk")
    k.shard(ob, (-13.0, 38.0, 0.4), (0, 1, 0), 4.0, 4.6, mat="gold", tag="obelisk_cap")
    for y in (20.0, 26.0, 32.0):                  # the victories cut in it, the curse in the cuts
        k.box(ob, C(-13.0, y, 3.4, 2.0, 2.6, 0.4), "curse", tag="glyph")
        k.box(ob, C(-10.0, y + 1.0, 0.4, 0.4, 2.0, 1.6), "dark", tag="glyph")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.35)
    return k.s, k.parts


# ================================================================ the Vulture Priest (caster)

def vulture_priest():
    """The khan's priests led the host to the well, and the vultures follow them still. Gaunt and black, a vulture's
    skull worn over the head with its beak over the brow and wings spread from its temples, a cloak of black
    feathers to the ground, a gold collar, and a censer on a long chain that pours out red smoke."""
    k = X.Kit("vulture_priest")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(1, 14.0, 12.0), (10, 12.0, 9.6), (21, 10.0, 7.6)], "feather", "feather_cloak", step=1.0)
    for i in range(10):
        a = i * 2 * math.pi / 10
        k.box(hips, C(math.cos(a) * 6.6, 0.2, math.sin(a) * 5.6, 1.4, 4.0 + (i % 3), 1.4), "feather", tag="cloak_feather")
    for side, nm in ((1, "l"), (-1, "r")):
        th = k.part("thigh_" + nm, (side * 3.0, 20, 0), (("x", -4),), hips)
        sh = k.part("shin_" + nm, (side * 3.0, 11, 0), (("x", 6),), th)
        ft = k.part("foot_" + nm, (side * 3.0, 2.4, 0), (), sh)
        k.box(ft, C(side * 3.0, 0, 2.6, 3.4, 1.6, 4.6), "char", tag="foot")
    to = k.part("torso", (0, 21, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(21, 10.0, 7.6), (27, 10.4, 7.4), (32, 11.6, 7.6), (35, 10.4, 7.0)], "char", "torso")
    k.box(to, C(0, 21.0, 3.8, 8.0, 9.0, 0.6), "crimson", tag="sash")
    for i in range(5):                            # the ribs showing
        k.box(to, C(0, 26.0 + i * 1.4, 3.85, 6.0 - abs(i - 2) * 0.6, 0.5, 0.3), "dark", tag="rib_line")
    k.stack(to, 0, 0, [(32.6, 13.4, 9.4), (34.4, 12.4, 8.6)], "gold", "collar")
    for sx in (-1, 1):
        k.blob(to, (sx * 6.6, 32.4, -0.6), (3.6, 3.0, 4.0), "feather", "feather_shoulder", step=0.6)
    k.box(to, C(0, 12.0, -4.6, 12.0, 22.0, 1.2), "feather", tag="cloak_back")
    hd = k.part("head", (0, 35, 0.6), (("x", -16),), "torso")
    k.box(hd, C(0, 35.2, 0.8, 5.4, 6.4, 5.4), "char", tag="face")
    eyes(k, hd, 37.4, 3.55, 1.2, 1.0)
    k.box(hd, C(0, 35.0, 3.55, 1.6, 0.4, 0.3), "dark", tag="mouth")
    # the vulture skull: over the head, the beak hooked over the brow, the wings out from the temples
    k.box(hd, C(0, 39.4, 0.8, 6.4, 3.4, 6.6), "bone", tag="vulture_skull")
    k.shard(hd, (0, 41.6, 3.8), (0, -0.3, 1), 4.0, 2.4, mat="bone", tag="vulture_beak")
    k.shard(hd, (0, 40.4, 7.6), (0, -1, 0.1), 1.8, 1.4, mat="bone", tag="beak_hook")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.4, 41.2, 4.0, 1.2, 1.0, 0.3), "eye", tag="skull_eye")
        for i in range(4):
            k.limb(hd, (sx * 3.4, 41.0, 0.4 - i * 0.6), (sx * (8.0 + i * 0.6), 44.0 - i * 2.0, -1.6 - i * 0.8), 1.6, "feather", "head_wing", d=0.6)
    arms(k, to, 6.6, 33, "char", {1: ((("x", -70), ("z", -10)), (("x", -20),)), -1: ((("x", -20), ("z", 10)), (("x", -40),))}, w=2.8, long=1.1)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        k.box(k.parts["fore_" + nm], C(side * 6.6, 18.4, 0, 3.4, 1.0, 3.4), "gold", tag="armlet")
    cs = held(k, "censer", "l", (6.6, 12.0, 0.4), (("x", 70),))
    k.chain(cs, (6.6, 12.0, 1.4), (6.6, 0.0, 1.4), 6, mat="gold", w=0.8)
    k.blob(cs, (6.6, -2.6, 1.4), (2.4, 2.6, 2.4), "gold", "censer", step=0.6)
    for a in range(0, 360, 60):
        r = math.radians(a)
        k.box(cs, C(6.6 + math.cos(r) * 2.2, -2.4, 1.4 + math.sin(r) * 2.2, 0.6, 1.0, 0.6), "curse", tag="censer_hole")
    for i in range(4):                            # the red smoke pouring off it
        k.blob(cs, (6.6 + (i % 2) * 1.4, -6.0 - i * 2.4, 1.4 + i * 0.6), (1.8 + i * 0.4, 1.2, 1.8 + i * 0.4), "crimson", "red_smoke", step=0.6)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Sand Reaver (skirmisher)

def sand_reaver():
    """The host's outriders: wound head to foot in crimson cloth gone stiff with salt, the cloth split at the joints
    where the salt has grown through in crystals, black skin and the curse's light showing in the splits, and on
    each fist a katar - a punching blade, its grip across the palm, its point a hand's length past the knuckles."""
    k = X.Kit("sand_reaver")
    hips = k.part("hips", (0, 19, 0))
    k.stack(hips, 0, 0, [(12, 10.4, 7.4), (19, 10.4, 7.4)], "crimson", "wraps")
    for i, x in enumerate((-3.6, 0.0, 3.6)):
        k.box(hips, C(x, 6.0 + (i % 2) * 2.0, -3.8, 3.0, 13.0 - (i % 2) * 2.0, 0.6), "crimson", tag="sash_tail")
    k.box(hips, C(0, 18.0, 0, 11.2, 1.6, 8.2), "leather", tag="belt")
    legs(k, hips, 18, 9.8, 3.0, "crimson", "crimson", knee_mat=None, lean=-12, bend=20, w=4.6, cuff=False)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        salt_crust(k, k.parts["thigh_" + nm], (side * 3.0, 10.6, 2.0), 3, 2.2, up=(side * 0.3, 0.2, 1), seed=side + 21)
        k.box(k.parts["thigh_" + nm], C(side * 3.0, 9.8, 2.4, 2.0, 1.0, 0.4), "curse", tag="split")
        wraps(k, k.parts["shin_" + nm], side * 3.0, 2.6, 9.6, 5.0, 5.2)
    to = k.part("torso", (0, 19, 0), (("x", 20),), "hips")
    k.stack(to, 0, 0, [(19, 10.4, 7.4), (24, 11.2, 7.6), (28.6, 13.0, 8.0), (32, 12.4, 7.6)], "crimson", "wraps")
    for y in (21.0, 24.0, 27.0, 30.0):            # the wrapping, wound on the slant
        k.limb(to, (-5.4, y, 4.0), (5.4, y + 1.4, 4.0), 0.8, "crimson", "wrap_band", d=0.4)
    k.box(to, C(-2.0, 25.0, 4.0, 2.4, 1.0, 0.3), "curse", tag="split")
    for sx in (-1, 1):
        salt_crust(k, to, (sx * 6.0, 31.0, 0), 3, 3.0, up=(sx, 0.8, 0), seed=sx + 31)
    hd = k.part("head", (0, 32, 0.6), (("x", -16),), "torso")
    k.box(hd, C(0, 32.4, 0.6, 5.8, 6.6, 5.8), "crimson", tag="head_wrap")
    for y in (33.0, 35.0, 37.0):
        k.box(hd, C(0, y, 0.6, 6.2, 0.7, 6.2), "crimson", tag="wrap")
    k.box(hd, C(0, 35.6, 3.55, 4.6, 1.0, 0.3), "dark", tag="eye_slit")
    eyes(k, hd, 35.75, 3.65, 1.2, 1.1, h=0.5)
    k.limb(hd, (0, 37.6, -2.6), (0.6, 33.0, -6.4), 1.8, "crimson", "wrap_tail", d=0.5)
    k.limb(hd, (0.6, 33.0, -6.4), (1.2, 27.0, -8.4), 1.6, "crimson", "wrap_tail", d=0.5)
    arms(k, to, 6.6, 30, "crimson", {1: ((("x", -30), ("z", 20)), (("x", -70),)), -1: ((("x", -50), ("z", -16)), (("x", -50),))}, w=3.2)
    for side, nm in ((1, "l"), (-1, "r")):        # the katars
        x = side * 6.6
        kt = held(k, "katar_" + nm, nm, (x, 12.6, 0.4), (("x", 90),))
        for sx in (-1, 1):
            k.box(kt, C(x + sx * 1.6, 9.6, 0.4, 0.6, 5.4, 1.4), "gold", tag="katar_bar")
        k.box(kt, C(x, 11.0, 0.4, 3.6, 0.8, 1.0), "gold", tag="katar_grip")
        for i, w in enumerate((3.0, 2.8, 2.4, 2.0, 1.4)):
            k.box(kt, C(x, 14.6 + i * 1.8, 0.4, w, 1.85, 0.8), "obsidian", tag="katar_blade")
        k.shard(kt, (x, 23.6, 0.4), (0, 1, 0), 2.2, 1.2, mat="obsidian", tag="blade_tip")
        k.box(kt, C(x, 15.0, 0.85, 0.5, 7.0, 0.3), "curse", tag="blade_vein")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Salt Khan (elite)

def salt_khan():
    """The khan who led his host to the well drank first and deepest. Taller than any of them, skin burned black and
    split with red light, crimson silk and gold scale over it, the pelts of three hyenas over his shoulders with their
    heads hanging, a crown of salt grown straight up out of his skull in crystals, and a glaive whose blade is a
    single crystal of salt as long as a man's arm, veined with the curse."""
    k = X.Kit("salt_khan")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(4, 14.4, 11.4), (12, 12.6, 9.4), (21, 12.0, 8.6)], "crimson", "robe", step=1.0)
    for x in (-4.4, 0, 4.4):
        k.box(hips, C(x, 4.0, 5.4 - abs(x) * 0.2, 2.4, 14.0, 0.6), "gold", tag="robe_panel")
    k.box(hips, C(0, 20.0, 0, 13.0, 2.4, 9.4), "gold", tag="belt")
    k.box(hips, C(0, 19.8, 4.8, 3.0, 3.0, 0.6), "curse", tag="belt_stone")
    legs(k, hips, 20, 10.8, 3.6, "crimson", "char", knee_mat="gold", lean=-6, bend=8, w=5.6, cuff=False)
    to = k.part("torso", (0, 21, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(21, 12.0, 8.6), (26, 13.8, 9.2), (31, 16.8, 10.0), (35, 16.4, 9.4)], "char", "torso")
    for y in range(22, 32, 2):                    # gold scale over the chest
        for x in range(-4, 5, 2):
            k.box(to, C(x + (y % 4) * 0.5 - 0.5, y, 4.6 + (y - 22) * 0.06, 1.8, 1.8, 0.4), "gold", tag="scale")
    k.limb(to, (7.4, 34.0, 5.0), (-6.4, 21.0, 5.4), 2.6, "crimson", "silk_sash", d=0.8)
    # the hyena pelts over his shoulders, their heads hanging down his chest
    k.blob(to, (0, 35.4, -0.6), (10.0, 2.6, 6.4), "hyena", "pelt_mantle", step=0.8)
    for sx in (-1, 1):
        k.box(to, C(sx * 5.0, 30.0, 5.2, 3.4, 3.4, 3.0), "hyena", tag="pelt_head")
        k.box(to, C(sx * 5.0, 29.0, 7.4, 2.2, 1.8, 1.8), "hyena", tag="pelt_muzzle")
        k.box(to, C(sx * 5.0, 31.6, 6.75, 0.8, 0.5, 0.3), "dark", tag="pelt_eye")
        k.blob(to, (sx * 9.6, 33.6, 0), (4.4, 3.0, 5.0), "gold", "pauldron", step=0.7)
        salt_crust(k, to, (sx * 10.0, 35.0, 0), 3, 3.6, up=(sx * 0.6, 1, 0), seed=sx + 51)
    k.box(to, C(0, 34.0, -6.2, 3.4, 3.4, 3.0), "hyena", tag="pelt_head")
    cl = k.part("cloak", (0, 35, -5.0), (("x", 5),), to, bone=False)
    for i, x in enumerate((-5.0, -1.6, 1.6, 5.0)):
        L = 32.0 - (i % 2) * 2.4
        k.box(cl, C(x, 35.0 - L, -5.6, 3.4, L, 0.8), "crimson", tag="cloak")
    hd = k.part("head", (0, 35.6, 0.6), (("x", -4),), "torso")
    k.box(hd, C(0, 35.8, 0.8, 6.4, 7.2, 6.4), "char", tag="face")
    k.box(hd, C(0, 40.4, 4.0, 6.6, 1.2, 0.8), "char", tag="brow")
    eyes(k, hd, 39.4, 4.05, 1.5, 1.4, h=0.8)
    k.box(hd, C(0, 36.6, 4.05, 2.4, 0.6, 0.3), "curse", tag="mouth")
    for i in range(5):                            # a beard plaited with gold
        x = -1.6 + i * 0.8
        k.box(hd, C(x, 32.0 - (i % 2) * 1.2, 3.8, 0.7, 4.6 + (i % 2) * 1.2, 0.8), "char", tag="beard")
        k.box(hd, C(x, 32.4 - (i % 2) * 1.2, 4.25, 0.8, 0.6, 0.3), "gold", tag="beard_ring")
    k.box(hd, C(0, 42.4, 0.8, 7.0, 1.4, 7.0), "gold", tag="crown_band")
    for i in range(7):                            # the salt crown: crystals grown straight up from the skull
        a = math.radians(-90 + i * 30)
        k.shard(hd, (math.sin(a) * 2.6, 43.4, 0.8 + math.cos(a) * 2.6), (math.sin(a) * 0.25, 1, math.cos(a) * 0.2), 4.4 + (3 - abs(i - 3)) * 1.6, 1.6, mat="salt", tag="salt_crown")
    k.box(hd, C(0, 42.6, 4.35, 1.6, 1.0, 0.3), "curse", tag="crown_stone")
    arms(k, to, 9.6, 33, "char", {1: ((("x", -36), ("z", -20)), (("x", -40),)), -1: ((("x", -32), ("z", 18)), (("x", -44),))}, w=3.8)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        k.box(k.parts["fore_" + nm], C(side * 9.6, 18.0, 0, 4.4, 5.0, 4.4), "gold", tag="vambrace")
        k.box(k.parts["fore_" + nm], C(side * 9.6, 20.6, 2.25, 1.6, 1.6, 0.3), "curse", tag="vambrace_stone")
    gl = held(k, "glaive", "r", (-9.6, 14.0, 0.3), (("x", 82), ("z", -16)))
    k.limb(gl, (-9.6, -8.0, 0.3), (-9.6, 24.0, 0.3), 1.6, "obsidian", "glaive_shaft")
    for y in (0.0, 8.0, 16.0):
        k.box(gl, C(-9.6, y, 0.3, 2.2, 1.0, 2.2), "gold", tag="shaft_ring")
    k.box(gl, C(-9.6, 23.0, 0.3, 3.0, 2.6, 3.0), "gold", tag="glaive_socket")
    for i, w in enumerate((3.0, 4.2, 4.8, 5.0, 4.6, 4.0, 3.2, 2.2)):     # the salt crystal blade, swelling and pointed
        k.box(gl, C(-9.6 + i * 0.25, 25.6 + i * 2.2, 0.3, w, 2.25, 1.6), "salt", tag="salt_blade")
    k.box(gl, C(-9.4, 26.0, 1.15, 0.8, 16.0, 0.3), "curse", tag="blade_vein")
    k.shard(gl, (-7.6, 43.2, 0.3), (0.1, 1, 0), 3.6, 2.0, mat="salt", tag="blade_tip")
    k.shard(gl, (-11.0, 26.0, 0.3), (-1, 0.6, 0), 3.0, 1.2, mat="salt", tag="blade_spur")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.15)
    return k.s, k.parts


MOBS = {
    "bone_hyena": dict(make=bone_hyena, rig="crawler", ent=(1.1, 1.4), stats=dict(hp=28, speed=0.36, dmg=7, armor=2, kb=0)),
    "salt_legionary": dict(make=salt_legionary, ent=(0.9, 2.8), stats=dict(hp=60, speed=0.24, dmg=10, armor=9, kb=0.3)),
    "dune_behemoth": dict(make=dune_behemoth, ent=(1.8, 4.2), stats=dict(hp=200, speed=0.18, dmg=19, armor=8, kb=1.0)),
    "vulture_priest": dict(make=vulture_priest, ent=(0.9, 2.9), stats=dict(hp=38, speed=0.22, dmg=7, armor=2, kb=0)),
    "sand_reaver": dict(make=sand_reaver, ent=(0.8, 2.6), stats=dict(hp=42, speed=0.35, dmg=8, armor=3, kb=0)),
    "salt_khan": dict(make=salt_khan, ent=(1.1, 3.4), stats=dict(hp=340, speed=0.25, dmg=16, armor=12, kb=0.6), key=True),
}
