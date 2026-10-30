"""The Voidborn: what came through from the black between the stars and settled in the End's castles, lighthouses
and ships, built by hand (tools/vox2.py). Bodies of void - a black full of stars that moves when they move - long
and too thin, armoured in pearly purpur shell, end-crystal in shards, and the electric purple of the rifts they
walk through in their eyes and their seams.

    void_mite     swarm   a shrimp-thing of void and purpur plates, feelers, a tail that curls over it
    void_sentinel guard   long-limbed and too tall, a blank starfield face with two eyes, a shell shield and a
                          spear of end-crystal
    shulk_brute   brute   a giant whose chest is a great shell split open on the starfield inside, and an eye
    rift_seer     caster  a robe of void, a cracked white mask with a rift of light through it, shards circling
    phase_blade   skirm   thin as a shadow, curved crystal blades, the shards of itself trailing behind
    void_herald   elite   the herald: a horned crown of end-crystal, wings of starry void, a mantle of shell, a
                          great crystal glaive

    python tools/monsterforge.py voidborn --preview ; python tools/mobsheet.py voidborn
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import grow
from _folk import lit, eyes, legs, arms, held, quad, wing

VOID = ramp("#020206", "#06060e", "#0a0a16", "#10101e", "#161628", "#1e1e34")
STARS = ramp("#8a86a8", "#b4b0d0", "#dcdaf0", "#ffffff")
PURPUR = ramp("#1e1024", "#322040", "#4a3058", "#644474", "#7e5a8e", "#9a74a8")
PEARL = ramp("#3a3640", "#58525e", "#78727e", "#9a94a0", "#bcb6c2", "#dcd6e2")
CRYSTAL = ramp("#2a1a40", "#46306a", "#684e94", "#8c72bc", "#b49ade", "#dccaf6")
RIFT = ramp("#3a0670", "#6010b0", "#8e2ae6", "#b660ff", "#d8a8ff", "#f6eaff")


def shaders():
    stars = lambda p, n, i, j, w, h: 0.9 if (i * 7 + j * 13) % 37 == 0 else (0.5 if (i * 11 + j * 3) % 53 == 0 else 0.0)
    return {
        "void": X.surf(VOID, 0.36, 1.0, 0.04, 0.0, pattern=stars),
        "purpur": X.surf(PURPUR, 0.54, 1.5, 0.12, 0.24, pattern=lambda p, n, i, j, w, h: -0.18 if (i % 4 == 0 or j % 4 == 0) else 0.03),
        "pearl": X.surf(PEARL, 0.58, 1.6, 0.08, 0.3),
        "crystal": X.facets(CRYSTAL, 0.04),
        "rift": X.glow(RIFT),
        "eye": X.glow(RIFT, 0.86, 0.12),
        "dark": X.dark(VOID),
    }


GLOWS = {"rift", "eye"}


def shards(k, part, c, r, n, seed=1, L=2.2):
    """end-crystal shards hanging in the air round a point"""
    cx, cy, cz = c
    for i in range(n):
        a = i * 2 * math.pi / n + seed
        y = cy + math.sin(a * 2.3) * 1.6
        k.shard(part, (cx + math.cos(a) * r, y, cz + math.sin(a) * r), (math.cos(a) * 0.2, 1, math.sin(a) * 0.2), L, 0.9, mat="crystal", tag="floating_shard")


def blank_face(k, part, c, s=1.0):
    """a face of starfield and nothing else but two long eyes"""
    cx, cy, cz = c
    k.box(part, C(cx, cy, cz, 6.0 * s, 7.6 * s, 6.0 * s), "void", tag="void_head")
    for sx in (-1, 1):
        k.box(part, C(cx + sx * 1.6 * s, cy + 4.4 * s, cz + 3.05 * s, 2.0 * s, 0.6 * s, 0.3), "eye", tag="eye")


# ================================================================ the Void Mite (swarm)

def void_mite():
    """The End is crawling with them: a shrimp-thing as big as a cat, its body void, its back plated in purpur shell
    in overlapping bands, feelers longer than it is, and a segmented tail curled over its back with a crystal
    sting."""
    k = X.Kit("void_mite")
    body, hd, ab, joints = quad(k, "void", y=5, chest=((1.6, 6, 7), (4, 7, 8), (6, 6, 7)), haunch=((1.6, 5.4, 6), (4, 6, 7), (5.6, 5, 6)),
                                leg_w=1.2, foot_w=0.9, front_z=3, back_z=-4, x=3.4, head_at=(0, 5, 5), head_rot=0, claw="purpur", foot_len=2.2)
    for i, z in enumerate((4, 1.6, -0.8, -3.2, -5.6)):        # the shell bands
        part = body if z > -1 else ab
        k.blob(part, (0, 6.6 - abs(z) * 0.1, z), (3.8 - abs(z + 1) * 0.15, 1.6, 1.4), "purpur", "shell_band", step=0.5)
    tail = [(0, 6.0, -7.0), (0, 9.0, -9.4), (0, 12.6, -9.0), (0, 14.4, -6.0)]       # the tail curled over
    for (a, b), w in zip(zip(tail, tail[1:]), (2.4, 2.0, 1.6)):
        k.limb(ab, a, b, w, "purpur", "tail")
    k.shard(ab, tail[-1], (0, -0.4, 1), 2.6, 1.0, mat="crystal", tag="sting")
    k.box(hd, C(0, 3.4, 8.0, 4.4, 3.6, 3.6), "void", tag="head")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.4, 5.8, 9.85, 1.0, 0.6, 0.3), "eye", tag="eye")
        k.limb(hd, (sx * 1.0, 6.4, 9.0), (sx * 4.0, 10.0, 14.0), 0.4, "purpur", "feeler")
        k.limb(hd, (sx * 4.0, 10.0, 14.0), (sx * 6.4, 9.0, 18.0), 0.3, "purpur", "feeler")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Void Sentinel (guard)

def void_sentinel():
    """The castles' guards are taller than a door and too thin for it: limbs of starry void as long as spears,
    armoured at the joints and the chest in plates of pearly purpur shell, a head with no face but the stars and two
    long purple eyes, a shield that is half a shell and a spear of end-crystal."""
    k = X.Kit("void_sentinel")
    hips = k.part("hips", (0, 26, 0))
    k.stack(hips, 0, 0, [(21, 8.4, 5.6), (26, 8.0, 5.4)], "void", "hips")
    for x in (-2.6, 0, 2.6):
        k.box(hips, C(x, 17.0, 2.8, 2.2, 8.0, 0.6), "purpur", tag="fauld")
    legs(k, hips, 25, 13.4, 2.6, "void", "void", knee_mat="pearl", lean=-6, bend=8, w=2.8, cuff=False)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        k.box(k.parts["shin_" + nm], C(side * 2.6, 4.0, 1.0, 3.2, 7.0, 1.6), "pearl", tag="greave")
        k.box(k.parts["foot_" + nm], C(side * 2.6, 0, 1.6, 3.4, 1.6, 5.6), "purpur", tag="foot")
    to = k.part("torso", (0, 26, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(26, 8.0, 5.4), (31, 8.6, 5.6), (36, 11.4, 6.6), (40, 11.0, 6.2)], "void", "torso")
    k.blob(to, (0, 35.0, 1.8), (5.2, 4.6, 2.6), "pearl", "chest_shell", step=0.6)
    for y in (29.0, 31.4):
        k.box(to, C(0, y, 2.6, 7.4, 1.6, 0.8), "purpur", tag="abdomen_band")
    k.box(to, C(0, 34.0, 4.35, 1.4, 4.0, 0.3), "rift", tag="seam")
    for sx in (-1, 1):
        k.blob(to, (sx * 6.0, 39.0, 0), (2.8, 2.2, 3.2), "purpur", "pauldron", step=0.6)
    hd = k.part("head", (0, 40, 0.4), (("x", -6),), "torso")
    k.limb(hd, (0, 40.0, 0.4), (0, 42.0, 0.6), 2.0, "void", "neck")
    blank_face(k, hd, (0, 42.0, 0.6), 1.0)
    k.box(hd, C(0, 49.4, 0.6, 6.4, 1.0, 6.4), "purpur", tag="crown_band")
    for sx in (-1, 1):
        k.shard(hd, (sx * 2.4, 50.0, 0.6), (sx * 0.3, 1, -0.2), 3.4, 1.0, mat="crystal", tag="crest_shard")
    arms(k, to, 6.0, 38, "void", {1: ((("x", -40), ("z", -8)), (("x", -40),)), -1: ((("x", -30), ("z", 8)), (("x", -48),))}, glove="void", w=2.4, long=1.4)
    for side in (1, -1):
        k.box(k.parts["fore_" + ("l" if side > 0 else "r")], C(side * 6.0, 18.0, 0, 3.2, 5.0, 3.2), "pearl", tag="vambrace")
    y = 38 - 8 * 1.4 - 7.6 * 1.4
    sh = held(k, "shell_shield", "l", (6.0, y, 0.4), (("x", 80),))
    k.blob(sh, (6.0, y, 3.0), (5.6, 7.0, 1.6), "purpur", "shell_shield", step=0.6, cut=lambda yy: True)
    k.blob(sh, (6.0, y, 4.0), (4.4, 5.6, 0.8), "pearl", "shield_pearl", step=0.6)
    k.box(sh, C(6.0, y - 1.0, 4.85, 1.2, 2.0, 0.3), "eye", tag="shield_eye")
    sp = held(k, "crystal_spear", "r", (-6.0, y, 0.3), (("x", 100),))
    k.limb(sp, (-6.0, y - 14.0, 0.3), (-6.0, y + 26.0, 0.3), 1.2, "void", "spear_shaft")
    for t in (-8.0, 4.0, 16.0):
        k.box(sp, C(-6.0, y + t, 0.3, 1.8, 1.0, 1.8), "purpur", tag="shaft_band")
    k.shard(sp, (-6.0, y + 26.0, 0.3), (0, 1, 0), 9.0, 2.4, mat="crystal", tag="crystal_head")
    k.box(sp, C(-6.0, y + 26.4, 0.3, 1.0, 2.0, 1.0), "rift", tag="spear_glow")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Shulk Brute (brute)

def shulk_brute():
    """The ships' holds hold these: a giant whose chest is one great purpur shell, split open down the middle the
    way the shulkers open, and inside it nothing but the stars - and one eye, purple, the size of a fist, looking
    out. Arms long enough to reach across a deck, plated in shell, and fists like anchors."""
    k = X.Kit("shulk_brute")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(13, 13.0, 9.0), (21, 13.4, 9.4)], "void", "hips")
    k.box(hips, C(0, 19.6, 0, 14.6, 2.4, 10.4), "purpur", tag="shell_belt")
    legs(k, hips, 20, 11.0, 4.6, "void", "purpur", knee_mat="pearl", lean=-4, bend=6, w=6.4, cuff=False)
    to = k.part("torso", (0, 21, 0), (("x", 10),), "hips")
    # the shell: two halves open like a clam, the starfield between them, the eye
    for sx in (-1, 1):
        k.blob(to, (sx * 6.0, 30.0, 0), (6.6, 9.6, 8.6), "purpur", "shell_half", step=0.9)
        k.box(to, C(sx * 1.4, 21.4, 4.6, 1.2, 17.0, 1.6), "pearl", tag="shell_lip")
        for y in (24.0, 28.0, 32.0, 36.0):
            k.box(to, C(sx * 8.6, y, 0, 3.0, 0.8, 15.6), "pearl", tag="shell_ridge")
    k.box(to, C(0, 21.4, 2.0, 4.4, 17.0, 6.0), "void", tag="inside_void")
    k.blob(to, (0, 30.0, 5.0), (1.8, 1.8, 0.8), "eye", "great_eye", step=0.5)
    k.box(to, C(0, 29.4, 5.85, 0.8, 1.2, 0.3), "dark", tag="pupil")
    hd = k.part("head", (0, 39.6, 2.0), (("x", -10),), "torso")
    k.box(hd, C(0, 39.6, 2.0, 6.0, 6.0, 6.0), "void", tag="small_head")
    k.box(hd, C(0, 42.0, 5.05, 3.6, 0.6, 0.3), "eye", tag="eye")
    k.blob(hd, (0, 45.6, 2.0), (4.0, 1.4, 4.0), "purpur", "head_shell", step=0.6)
    arms(k, to, 13.4, 38, "void", {1: ((("x", -30), ("z", -12)), (("x", -40),)), -1: ((("x", -50), ("z", 14)), (("x", -30),))}, w=5.0, long=1.4)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        k.blob(k.parts["arm_" + nm], (side * 14.0, 34.0, 0), (4.6, 4.0, 5.0), "purpur", "shoulder_shell", step=0.7)
        k.box(k.parts["fore_" + nm], C(side * 13.4, 17.0, 0, 6.0, 6.0, 6.0), "pearl", tag="fore_shell")
        for b in list(k.s.boxes):
            if b.part is k.parts["hand_" + nm]:
                k.s.boxes.remove(b)
        y = 38 - 8 * 1.4 - 7.6 * 1.4
        k.blob(k.parts["hand_" + nm], (side * 13.4, y - 3.4, 0.4), (4.4, 4.2, 4.6), "purpur", "shell_fist", step=0.8)
        k.box(k.parts["hand_" + nm], C(side * 13.4, y - 4.0, 4.6, 6.0, 1.2, 0.6), "rift", tag="knuckle_seam")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.25)
    return k.s, k.parts


# ================================================================ the Rift Seer (caster)

def rift_seer():
    """The seers walk in and out of the world through rifts they open with their hands. A long robe of void that
    trails into nothing at the hem, a mask of cracked white shell where the face should be with a line of purple light
    splitting it top to bottom, long bone-white fingers, and the shards of end-crystal circling it slowly."""
    k = X.Kit("rift_seer")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(3, 13.0, 11.0), (12, 11.4, 9.0), (22, 10.0, 7.4)], "void", "void_robe", step=1.0)
    for i in range(10):                           # the hem trailing off into shards
        a = i * 2 * math.pi / 10
        k.shard(hips, (math.cos(a) * 6.0, 3.4, math.sin(a) * 5.0), (math.cos(a) * 0.3, -1, math.sin(a) * 0.3), 2.6, 1.4, mat="void", tag="hem_shard")
    for side, nm in ((1, "l"), (-1, "r")):
        th = k.part("thigh_" + nm, (side * 3.0, 21, 0), (), hips)
        sh = k.part("shin_" + nm, (side * 3.0, 12, 0), (), th)
        ft = k.part("foot_" + nm, (side * 3.0, 2.4, 0), (), sh)
        k.box(ft, C(side * 3.0, 0, 0, 3.0, 1.2, 3.0), "rift", tag="foot")
    k.box(hips, C(0, 4.0, 5.0, 1.0, 18.0, 0.6), "rift", tag="robe_seam")
    to = k.part("torso", (0, 22, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(22, 10.0, 7.4), (28, 10.4, 7.2), (33, 12.0, 7.6), (36, 10.6, 7.0)], "void", "void_robe")
    k.blob(to, (0, 35.4, -0.4), (8.0, 1.8, 5.4), "pearl", "shell_mantle", step=0.6)
    hd = k.part("head", (0, 36, 0.6), (("x", -2),), "torso")
    k.blob(hd, (0, 40.4, 0.2), (4.0, 4.6, 4.2), "void", "hood", step=0.6)
    k.shard(hd, (0, 44.6, -1.0), (0, 0.8, -0.6), 3.6, 2.6, mat="void", tag="hood_point")
    k.box(hd, C(0, 36.6, 2.8, 5.4, 7.4, 1.2), "pearl", tag="mask")
    k.box(hd, C(0, 36.6, 3.45, 0.7, 7.4, 0.3), "rift", tag="mask_rift")       # the rift through it
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.4, 40.0, 3.45, 1.2, 0.8, 0.3), "dark", tag="mask_eye")
        k.box(hd, C(sx * 1.4, 40.2, 3.5, 0.6, 0.4, 0.3), "eye", tag="eye")
        k.box(hd, C(sx * 1.8, 37.0, 3.45, 0.3, 2.0, 0.3), "dark", tag="mask_crack")
    arms(k, to, 6.4, 34, "void", {1: ((("x", -90), ("z", -20)), (("x", -10),)), -1: ((("x", -90), ("z", 20)), (("x", -10),))}, glove="pearl", w=2.8, long=1.15)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        y = 34 - 8 * 1.15 - 7.6 * 1.15 - 2.8
        for t in (-0.9, 0, 0.9):
            k.limb(k.parts["hand_" + nm], (side * 6.4 + t, y, 1.0), (side * 6.4 + t * 1.6, y - 4.6, 1.6), 0.5, "pearl", "long_finger")
    # the rift it is opening between its hands
    k.box(to, C(0, 22.0, 13.0, 1.2, 10.0, 0.6), "rift", tag="rift_tear")
    k.box(to, C(0, 24.0, 13.0, 3.0, 6.0, 0.4), "rift", tag="rift_tear")
    shards(k, to, (0, 30.0, 0), 9.0, 7, seed=0.4)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Phase Blade (skirmisher)

def phase_blade():
    """They don't walk across a room; they're on the far side of it. Thin as a shadow and taller than a man, limbs of
    void plated in strips of purpur, a narrow head of shell with one slit of light, two curved blades of end-crystal,
    and behind it, the shards of the place it just was, falling."""
    k = X.Kit("phase_blade")
    hips = k.part("hips", (0, 23, 0))
    k.stack(hips, 0, 0, [(17, 7.4, 5.0), (23, 7.6, 5.0)], "void", "hips")
    k.box(hips, C(0, 13.0, -2.6, 3.0, 10.0, 0.6), "purpur", tag="tail_cloth")
    legs(k, hips, 22, 12.0, 2.4, "void", "void", knee_mat="purpur", lean=-14, bend=24, w=2.6, cuff=False)
    for side in (1, -1):
        k.box(k.parts["foot_" + ("l" if side > 0 else "r")], C(side * 2.4, 0, 2.0, 2.8, 1.6, 6.0), "purpur", tag="foot")
    to = k.part("torso", (0, 23, 0), (("x", 22),), "hips")
    k.stack(to, 0, 0, [(23, 7.6, 5.0), (29, 8.0, 5.0), (34, 10.0, 5.6), (37, 9.0, 5.2)], "void", "torso")
    for y in (25.0, 28.0, 31.0):
        k.box(to, C(0, y, 2.6, 6.0 + (y - 25) * 0.3, 0.8, 0.4), "purpur", tag="plate_strip")
    k.box(to, C(0, 26.0, 2.85, 0.6, 9.0, 0.3), "rift", tag="seam")
    hd = k.part("head", (0, 37, 0.6), (("x", -16),), "torso")
    k.limb(hd, (0, 37.0, 0.6), (0, 39.0, 1.0), 1.8, "void", "neck")
    k.box(hd, C(0, 39.0, 1.0, 4.0, 7.0, 5.6), "pearl", tag="narrow_head")
    k.shard(hd, (0, 45.6, 0.0), (0, 0.6, -1), 4.4, 2.4, mat="pearl", tag="head_crest")
    k.box(hd, C(0, 42.6, 3.85, 3.0, 0.6, 0.3), "eye", tag="eye")
    arms(k, to, 5.4, 35, "void", {1: ((("x", -10), ("z", 40)), (("x", -60),)), -1: ((("x", -60), ("z", -30)), (("x", -30),))}, glove="void", w=2.2, long=1.3)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.4
        y = 35 - 8 * 1.3 - 7.6 * 1.3
        bl = held(k, "crystal_blade_" + nm, nm, (x, y, 0.4), (("x", 80 if side > 0 else 50),))
        k.limb(bl, (x, y - 2.0, 0.4), (x, y + 2.0, 0.4), 1.0, "void", "grip")
        pts = [(x, y + 2.0, 0.4), (x, y + 8.0, 1.6), (x, y + 13.0, 4.0), (x, y + 16.0, 7.4)]
        for (a, b), w in zip(zip(pts, pts[1:]), (2.6, 2.4, 1.8)):
            k.limb(bl, a, b, 0.7, "crystal", "crystal_blade", d=w)
        k.shard(bl, pts[-1], (0, 0.6, 0.8), 2.4, 0.8, mat="crystal", tag="blade_tip")
        k.box(bl, C(x, y + 4.0, 1.0, 0.8, 6.0, 0.4), "rift", tag="blade_rift")
    for i in range(6):                            # the shards of where it was, falling behind it
        k.shard(hips, (-2.0 + (i % 3) * 2.0, 8.0 + i * 4.0, -8.0 - (i % 2) * 2.0), (0.2, -1, 0.1), 2.4, 1.2, mat="void" if i % 2 else "crystal", tag="afterimage_shard")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Void Herald (elite)

def void_herald():
    """The herald announces the void to the places it is going to take. Taller than the sentinels, robed in void with
    a mantle of pearl shell over the shoulders, a crown of end-crystal horns sweeping back off a blank starry head,
    wings of void with the stars in them spread behind it, and a great glaive of crystal with a rift running through
    its blade."""
    k = X.Kit("void_herald")
    hips = k.part("hips", (0, 25, 0))
    k.stack(hips, 0, 0, [(2, 14.4, 12.0), (12, 12.6, 10.0), (25, 10.4, 7.6)], "void", "void_robe", step=1.0)
    for x in (-4.4, 0, 4.4):
        k.box(hips, C(x, 2.0, 5.6 - abs(x) * 0.3, 2.0, 22.0, 0.6), "purpur", tag="robe_panel")
    k.box(hips, C(0, 24.0, 0, 11.4, 2.0, 8.4), "pearl", tag="belt")
    for side, nm in ((1, "l"), (-1, "r")):
        th = k.part("thigh_" + nm, (side * 3.2, 24, 0), (), hips)
        sh = k.part("shin_" + nm, (side * 3.2, 13, 0), (), th)
        ft = k.part("foot_" + nm, (side * 3.2, 2.4, 0), (), sh)
        k.box(ft, C(side * 3.2, 0, 3.6, 3.6, 1.6, 5.0), "purpur", tag="foot")
    to = k.part("torso", (0, 25, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(25, 10.4, 7.6), (31, 11.0, 7.6), (36, 13.6, 8.4), (40, 12.4, 7.8)], "void", "torso")
    k.blob(to, (0, 40.0, -0.4), (10.4, 2.4, 6.6), "pearl", "shell_mantle", step=0.7)
    for sx in (-1, 1):
        k.blob(to, (sx * 8.6, 39.0, 0), (3.6, 3.0, 4.0), "pearl", "pauldron", step=0.6)
        k.shard(to, (sx * 9.6, 41.0, 0), (sx * 0.6, 1, -0.2), 3.4, 1.2, mat="crystal", tag="shoulder_shard")
    k.box(to, C(0, 28.0, 3.85, 1.2, 10.0, 0.3), "rift", tag="seam")
    for side in (1, -1):                          # the wings of void
        wing(k, to, (side * 3.0, 38.0, -3.6), side, 22.0, "void", membrane="void", ribs=5, up=0.6, back=0.5, drop=16.0, feather=False)
    hd = k.part("head", (0, 40.4, 0.6), (("x", -4),), "torso")
    blank_face(k, hd, (0, 41.0, 0.8), 1.05)
    for sx in (-1, 1):                            # the crown of crystal horns
        pts = [(sx * 2.6, 49.0, 0.4), (sx * 4.6, 52.0, -2.0), (sx * 5.8, 54.0, -6.0), (sx * 5.4, 55.0, -10.0)]
        for (a, b), w in zip(zip(pts, pts[1:]), (1.8, 1.4, 1.0)):
            k.limb(hd, a, b, w, "crystal", "crown_horn")
        k.shard(hd, (sx * 1.0, 49.0, 2.4), (sx * 0.2, 1, 0.2), 3.0, 1.0, mat="crystal", tag="crown_shard")
    k.box(hd, C(0, 48.6, 0.8, 6.8, 1.0, 6.8), "pearl", tag="crown_band")
    k.box(hd, C(0, 48.8, 4.25, 1.4, 1.2, 0.3), "rift", tag="crown_stone")
    arms(k, to, 8.4, 38, "void", {1: ((("x", -36), ("z", -20)), (("x", -40),)), -1: ((("x", -32), ("z", 18)), (("x", -44),))}, glove="pearl", w=3.0, long=1.2)
    y = 38 - 8 * 1.2 - 7.6 * 1.2
    gl = held(k, "crystal_glaive", "r", (-8.4, y, 0.3), (("x", 82), ("z", -16)))
    k.limb(gl, (-8.4, y - 12.0, 0.3), (-8.4, y + 20.0, 0.3), 1.4, "void", "glaive_shaft")
    for t in (-6.0, 4.0, 14.0):
        k.box(gl, C(-8.4, y + t, 0.3, 2.0, 1.0, 2.0), "pearl", tag="shaft_band")
    k.box(gl, C(-8.4, y + 19.0, 0.3, 3.0, 2.6, 3.0), "purpur", tag="glaive_socket")
    for i, w in enumerate((3.0, 4.2, 4.8, 4.8, 4.2, 3.4, 2.4)):
        k.box(gl, C(-8.4 + i * 0.3, y + 21.6 + i * 2.2, 0.3, w, 2.25, 1.4), "crystal", tag="crystal_blade")
    k.box(gl, C(-8.0, y + 22.0, 1.05, 0.8, 14.0, 0.3), "rift", tag="blade_rift")
    k.shard(gl, (-6.6, y + 37.0, 0.3), (0.1, 1, 0), 3.6, 2.0, mat="crystal", tag="blade_tip")
    shards(k, to, (0, 30.0, 0), 11.0, 6, seed=1.2, L=2.8)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.1)
    return k.s, k.parts


MOBS = {
    "void_mite": dict(make=void_mite, rig="crawler", ent=(0.8, 0.9), stats=dict(hp=22, speed=0.36, dmg=6, armor=3, kb=0)),
    "void_sentinel": dict(make=void_sentinel, ent=(0.9, 3.4), stats=dict(hp=70, speed=0.26, dmg=11, armor=10, kb=0.3)),
    "shulk_brute": dict(make=shulk_brute, ent=(1.9, 4.2), stats=dict(hp=240, speed=0.18, dmg=20, armor=14, kb=1.0)),
    "rift_seer": dict(make=rift_seer, ent=(0.9, 3.0), stats=dict(hp=44, speed=0.24, dmg=9, armor=3, kb=0)),
    "phase_blade": dict(make=phase_blade, ent=(0.8, 3.0), stats=dict(hp=48, speed=0.37, dmg=10, armor=3, kb=0)),
    "void_herald": dict(make=void_herald, ent=(1.1, 3.8), stats=dict(hp=380, speed=0.25, dmg=18, armor=13, kb=0.7), key=True),
}
