"""The Abyssal Lighthouse's monsters, each built by hand (tools/vox2.py). What lives under the lighthouse on the black
reef: pale flesh that never saw the sun, rusted brass and iron diving gear, rotten teal wood, barnacles, kelp, the
cold sea-glow of the deep, and the gold of the lamp they hate and want.

    deep_thing       swarm   pale, eyeless, too many limbs, a mouth of needles - fast in the dark (the spider's bones)
    drowned_keeper   brute   a giant in a rusted diving suit, the glass helmet full of water and a face, an anchor on a chain
    lamp_siren       caster  a pale drowned woman whose head is a lure-light on a stalk, kelp for hair, a torn shift
    eyeless          skirm   a blind hunter, lanky, a head of sound-frills and no eyes, long hooked claws
    angler_knight    elite   barnacled plate, a great angler-fish head with the lure over it, a harpoon on a chain
    keeper_in_light  boss    the Keeper in the Light: tall and robed, its head a burning lighthouse lens throwing its beam,
                             a lantern staff, the oil-black robe hung with chains and barnacles

    python tools/monsterforge.py abyssal_lighthouse --preview ; python tools/mobsheet.py abyssal_lighthouse
"""
import math

import vox2 as X
from vox2 import C, ramp

PALE = ramp("#3a3c3e", "#585c5e", "#7a7e80", "#9ca0a0", "#bcc0be", "#dadcd8")
BRASS = ramp("#1e1608", "#34260e", "#4c3816", "#664c20", "#80622c", "#a07c3a", "#c49a50")
VERD = ramp("#0e2a24", "#16403a", "#225a4e", "#2e7462")
RUSTI = ramp("#0e0a08", "#1a120c", "#2a1a10", "#3c2414", "#4e2e18")
TEAL = ramp("#061412", "#0a201c", "#102c28", "#183a34", "#204840")
BARN = ramp("#22241e", "#34362e", "#48493e", "#5c5c4e", "#706e5e")
STEEL = ramp("#080c10", "#10161a", "#182026", "#222c34", "#2e3a42", "#3e4c56", "#56666e")
LINEN = ramp("#1a201c", "#2a322c", "#3a443c", "#4c5848", "#5e6a58")
KELP = ramp("#0a140a", "#122010", "#1a2e16", "#24401c", "#305224")
SEA = ramp("#2a4a4a", "#4a7a78", "#7ab0aa", "#b4e4dc", "#e8fff8")
LAMP = ramp("#8a5a0a", "#c88a1a", "#f0b840", "#ffd870", "#fff0b0", "#ffffff")
ROBE = ramp("#040506", "#08090c", "#0e1014", "#14171c", "#1c2026")
WATER = ramp("#0a2a3a", "#124050", "#1c5868", "#287080")
GUM = ramp("#3a1418", "#5a2026", "#7a3038", "#9a4448")


def shaders():
    return {
        "pale": X.wrinkled(PALE, 0.6),
        "brass": X.surf(BRASS, 0.52, 1.4, 0.16, 0.18, rust=(VERD, 0.36, 0.4), crust=(BARN, 0.1)),
        "iron": X.surf(RUSTI, 0.5, 1.3, 0.24, 0.12, crust=(BARN, 0.16)),
        "teal": X.surf(TEAL, 0.5, 1.0, 0.24, 0.04, stripe=3),
        "barnacle": X.surf(BARN, 0.5, 1.2, 0.5, 0.16),
        "kelp": X.surf(KELP, 0.5, 1.0, 0.24, 0.0, stripe=2),
        "glow": X.glow(SEA),
        "lamp": X.glow(LAMP, 0.7, 0.3),
        "eye": X.glow(SEA, 0.84, 0.14),
        "robe": X.surf(ROBE, 0.5, 1.1, 0.2, 0.0, holes=True, drip=(KELP, 0.16)),
        "water": X.glow(WATER, 0.5, 0.3),
        "gum": X.surf(GUM, 0.5, 1.0, 0.2, 0.0),
        "dark": X.dark(ROBE),
        "plate": X.surf(STEEL, 0.52, 1.4, 0.18, 0.2, rust=(VERD, 0.3, 0.5), crust=(BARN, 0.12)),
        "linen": X.surf(LINEN, 0.5, 1.0, 0.24, 0.0, holes=True, drip=(KELP, 0.3)),
    }


def barnacles(k, part, pts, s=1.2):
    for (x, y, z) in pts:
        k.box(part, C(x, y, z, s * 1.6, s * 1.0, s * 1.6), "barnacle", tag="barnacle")
        k.box(part, C(x, y + s * 0.9, z, s * 0.9, s * 0.4, s * 0.9), "dark", tag="barnacle")


def needles(k, part, cx, cy, cz, w, h, n=6, s=1.0):
    """a gaping mouth ringed with needle teeth"""
    k.box(part, C(cx, cy - h / 2, cz, w, h, 0.6), "gum", tag="mouth")
    k.box(part, C(cx, cy - h / 2 + 0.3, cz + 0.1, w - 0.8, h - 0.6, 0.6), "dark", tag="mouth")
    for i in range(n):
        x = cx - w / 2 + (i + 0.5) * w / n
        k.shard(part, (x, cy + h / 2 - 0.2, cz + 0.4), (0, -1, 0.2), 1.6 * s, 0.4 * s, mat="pale", tag="needle")
        k.shard(part, (x + 0.3, cy - h / 2 + 0.2, cz + 0.4), (0, 1, 0.2), 1.4 * s, 0.4 * s, mat="pale", tag="needle")


# ================================================================ the Keeper in the Light (boss)

def keeper_in_light():
    """The last keeper of the lighthouse went down into the rock to find where the light went at night, and found
    it, and wears it. It stands six blocks high, thin as a mast, in a robe black with oil and sea, hung with the
    keeper's chains and crusted with barnacles at the hem. Its head is the lighthouse lens: tier on tier of brass
    rings and glass prisms round a flame that burns white, and the beam comes out of the front of it as a solid
    shaft of light. Its hands are long and pale. It carries the keeper's lantern on a staff, and the lantern swings."""
    k = X.Kit("keeper_in_light")
    hips = k.part("hips", (0, 38, 0))
    k.stack(hips, 0, 0, [(0, 26, 22), (10, 22, 18), (24, 17, 13), (38, 14, 10)], "robe", "robe", step=1.2)
    for i in range(10):
        a = math.radians(i * 36 + 10)
        k.limb(hips, (math.sin(a) * 9, 30, math.cos(a) * 7), (math.sin(a) * 14, 0.6, math.cos(a) * 12), 3.0, "robe", "robe_rag", d=0.6)
    barnacles(k, hips, [(math.sin(math.radians(a)) * 12, 2, math.cos(math.radians(a)) * 10) for a in range(0, 360, 40)], s=1.6)
    for (x, z, L) in ((-9, 6, 18), (9, 4, 22), (0, -10, 20), (-6, -8, 14)):
        k.limb(hips, (x, 34, z), (x * 1.1, 34 - L, z * 1.2), 1.4, "kelp", "kelp")
    k.chain(hips, (-6, 36, 6), (4, 24, 9), 6, w=1.4)
    k.chain(hips, (6, 36, 6), (-3, 20, 8), 7, w=1.4)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 4
        th = k.part("thigh_" + nm, (x, 34, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 18, 0), (), th)
        ft = k.part("foot_" + nm, (x, 4, 0), (), sh)
        k.box(ft, C(x, 0, 2.6, 5, 2, 7), "robe", tag="foot")
    # ---------------------------------------------------------------- torso: thin as a mast, a mantle, a brass oil-lamp pack
    to = k.part("torso", (0, 38, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(38, 14, 10), (48, 15, 10), (56, 20, 11), (60, 18, 10)], "robe", "robe")
    k.stack(to, 0, -0.4, [(50, 24, 14), (57, 26, 15), (61, 20, 12)], "robe", "mantle")
    for (x, z) in ((-10, 4), (8, 5), (-4, 7), (11, -2)):
        k.limb(to, (x, 52, z), (x * 1.1, 40, z * 1.1), 1.6, "kelp", "kelp")
    k.stack(to, 0, -9, [(42, 10, 6), (56, 10, 6)], "brass", "oil_tank")
    for y in (45, 50, 55):
        k.box(to, C(0, y, -9, 11, 1.0, 7), "iron", tag="tank_band")
    k.limb(to, (3, 56, -9), (2, 62, -5), 1.2, "brass", "oil_pipe")
    # ---------------------------------------------------------------- the head: the lighthouse lens, burning, the beam
    hd = k.part("head", (0, 60, 0), (("x", -4),), "torso")
    k.box(hd, C(0, 60, 0, 4, 3, 4), "brass", tag="neck")
    for i, (y, r) in enumerate(((63, 6.0), (66, 7.4), (69, 8.0), (72, 7.4), (75, 6.0), (78, 4.2))):
        k.ring(hd, 0, y, 0, r, 1.6, "brass", "lens_ring", n=18, axis="y")
        k.blob(hd, (0, y + 0.8, 0), (r - 0.6, 1.2, r - 0.6), "glow", "lens_prism", step=0.8)
    k.blob(hd, (0, 70, 0), (4.0, 5.0, 4.0), "lamp", "flame", step=0.8)
    k.box(hd, C(0, 80, 0, 7, 1.2, 7), "brass", tag="lens_cap")
    k.shard(hd, (0, 81, 0), (0, 1, 0), 5, 3, mat="brass", tag="lens_spire")
    for side in (1, -1):         # the brass frame struts
        k.limb(hd, (side * 7, 62, 0), (side * 6, 79, 0), 1.2, "brass", "strut")
        k.limb(hd, (0, 62, side * 7), (0, 79, side * 6), 1.2, "brass", "strut")
    for (dy, L, w) in ((0, 34, 6.0), (1.6, 26, 3.6), (-1.6, 22, 3.0)):   # the beam: a shaft of light out of the front
        k.limb(hd, (0, 70 + dy, 6), (0, 68 + dy * 2, 6 + L), w, "lamp", "beam", group="glow", d=w)
    k.box(hd, C(0, 66.4, 7.6, 3.0, 1.6, 0.6), "eye", group="glow", tag="eye")
    # ---------------------------------------------------------------- arms: long and pale, the lantern staff
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 12
        up = k.part("arm_" + nm, (x, 57, 0), (("x", -40 if side > 0 else -60), ("z", side * 14)), "torso")
        fo = k.part("fore_" + nm, (x, 43, 0), (("x", -40 if side > 0 else -30),), up)
        hn = k.part("hand_" + nm, (x, 29, 0), (), fo)
        k.stack(up, x, 0, [(43, 5.6, 5.8), (57, 6.6, 6.8)], "robe", "sleeve")
        k.stack(fo, x, 0, [(30, 7.4, 7.4), (36, 6.0, 6.0), (43, 4.8, 4.8)], "robe", "sleeve")
        k.box(hn, C(x, 25, 0.6, 3.6, 5.0, 3.0), "pale", tag="hand")
        for t in (-1.2, -0.4, 0.4, 1.2):
            k.limb(hn, (x + t, 25, 1.4), (x + t * 1.4, 18, 2.6), 0.7, "pale", "finger")
    st = k.part("lantern_staff", (-12, 27, 1), (("x", 50),), k.parts["hand_r"])
    k.limb(st, (-12, -8, 1), (-12, 52, 1), 1.8, "teal", "staff")
    k.limb(st, (-12, 52, 1), (-12, 55, 6), 1.6, "brass", "crook")
    k.chain(st, (-12, 55, 6), (-12, 46, 6), 4, mat="brass", w=1.0)
    k.box(st, C(-12, 38, 6, 6.0, 8.0, 6.0), "brass", tag="lantern")
    k.box(st, C(-12, 39, 6, 6.4, 6.0, 4.4), "lamp", group="glow", tag="lantern_glass")
    k.box(st, C(-12, 46, 6, 4.0, 1.4, 4.0), "brass", tag="lantern_cap")
    barnacles(k, st, [(-11, 10, 2), (-13, 24, 2)], s=1.0)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Angler Knight (elite, the key)

def angler_knight():
    """A knight who went down with his ship and was taken in by the deep: his plate is barnacled solid, his helm is
    gone into the head of a great angler fish - a jaw of glass needles under a visor slit, the lure on its stalk
    hanging over in front of him - and he hunts with a harpoon on a chain. His lure is the only light that opens
    the last door."""
    k = X.Kit("angler_knight")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(16, 13.6, 9), (22, 14.4, 9.4)], "plate", "faulds")
    for x in (-4.4, 0, 4.4):
        k.box(hips, C(x, 12.6, 4.8, 4.0, 6.4, 0.8), "plate", tag="tasset")
    barnacles(k, hips, [(-5, 18, 4.8), (4, 15, 5)], s=1.0)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.8
        th = k.part("thigh_" + nm, (x, 21, 0), (("x", -6), ("z", side * 5)), "hips")
        sh = k.part("shin_" + nm, (x, 11.4, 0), (("x", 10),), th)
        ft = k.part("foot_" + nm, (x, 2.8, 0), (("x", -4),), sh)
        k.box(th, C(x, 11.6, 0, 5.6, 9.6, 6.0), "plate", tag="cuisse")
        k.box(sh, C(x, 2.8, 0, 5.6, 8.6, 6.0), "plate", tag="greave")
        barnacles(k, sh, [(x + side * 2.6, 6, 1)], s=0.9)
        k.box(ft, C(x, 0, 1.6, 6.0, 3.0, 9.0), "plate", tag="foot")
    # ---------------------------------------------------------------- torso
    to = k.part("torso", (0, 22, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(22, 14.4, 9.4), (28, 18, 10.6), (33, 20, 11), (37, 18, 10)], "plate", "cuirass")
    barnacles(k, to, [(-5, 26, 5.4), (5, 30, 5.6), (-2, 33, 5.4), (6, 24, 5.2), (-6, 34, -5), (3, 28, -5.4)], s=1.3)
    for (x, L) in ((-6, 12), (0, 16), (6, 10)):
        k.limb(to, (x, 36, -5), (x * 1.1, 36 - L, -7), 1.6, "kelp", "kelp")
    for side in (1, -1):
        k.blob(to, (side * 10.6, 36, 0), (6.0, 3.8, 6.2), "plate", "pauldron")
        barnacles(k, to, [(side * 11, 39, 1), (side * 12, 38, -2)], s=1.1)
        for dz in (-2.4, 0.6, 3.4):
            k.shard(to, (side * 12, 39.4, dz), (side * 0.5, 1, 0), 3.6, 1.4, mat="plate", tag="spike")
    # ---------------------------------------------------------------- the head: the angler fish swallowed his helm
    hd = k.part("head", (0, 37, 1), (("x", -10),), "torso")
    k.blob(hd, (0, 40, 2), (6.6, 5.6, 7.4), "teal", "angler_head")
    k.box(hd, C(0, 35.4, 6.4, 12, 3.4, 6.6), "teal", tag="angler_jaw")
    for i in range(7):                  # the jaw of glass needles, jutting up
        x = -5 + i * 1.66
        k.shard(hd, (x, 38.4, 9.4), (0, 1, 0.3), 3.4 if i % 2 else 2.4, 0.7, mat="glow", tag="needle", group="glow")
    for i in range(5):
        x = -4 + i * 2
        k.shard(hd, (x, 43.4, 8.6), (0, -1, 0.3), 2.0, 0.6, mat="glow", tag="needle", group="glow")
    k.box(hd, C(0, 40.4, 9.0, 8.0, 2.4, 0.8), "dark", tag="maw")
    for sx in (-4.0, 4.0):
        k.box(hd, C(sx, 43.6, 6.6, 1.4, 1.4, 1.4), "eye", group="glow", tag="eye")
    lure = [(0, 46, 2), (0, 54, 4), (0, 56, 10), (0, 51, 13)]
    for (a, b), w in zip(zip(lure, lure[1:]), (1.2, 1.0, 0.8)):
        k.limb(hd, a, b, w, "teal", "lure_stalk")
    k.blob(hd, (0, 47, 13), (3.0, 3.2, 3.0), "lamp", "lure", step=0.7)
    for sx in (-1, 1):
        k.shard(hd, (sx * 6, 40, -1), (sx * 1, 0, -0.6), 4.0, 3.0, mat="teal", tag="fin")
    # ---------------------------------------------------------------- arms: the harpoon on its chain
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 10.6
        up = k.part("arm_" + nm, (x, 35, 0), (("x", -40 if side > 0 else -40), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 26, 0), (("x", -50 if side > 0 else -60),), up)
        hn = k.part("hand_" + nm, (x, 17, 0), (), fo)
        k.box(up, C(x, 26.6, 0, 5.0, 8.6, 5.2), "plate", tag="rerebrace")
        k.box(fo, C(x, 17.6, 0, 5.0, 8.6, 5.2), "plate", tag="vambrace")
        barnacles(k, fo, [(x + side * 2.6, 21, 1)], s=0.9)
        k.box(hn, C(x, 13.8, 0.4, 4.6, 4.0, 4.6), "plate", tag="gauntlet")
    hp = k.part("harpoon", (-10.6, 15.6, 0.6), (("x", 80),), k.parts["hand_r"])
    k.limb(hp, (-10.6, -10, 0.6), (-10.6, 36, 0.6), 1.6, "teal", "shaft")
    k.limb(hp, (-10.6, 36, 0.6), (-10.6, 40, 0.6), 1.8, "iron", "socket")
    k.shard(hp, (-10.6, 40, 0.6), (0, 1, 0), 8.0, 3.0, mat="iron", tag="harpoon_head")
    for sz in (-1, 1):
        k.shard(hp, (-10.6, 43, 0.6), (0, -1, sz * 0.7), 4.0, 1.0, mat="iron", tag="barb")
    k.chain(hp, (-10.6, -8, 0.6), (-6, -2, 4), 5, w=1.0)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Drowned Keeper (brute)

def drowned_keeper():
    """The lighthouse keepers who went down to mend the foundations in diving suits never came up. One of them got
    big down there. A giant in a rusted canvas-and-iron diving suit gone teal and barnacled, the round brass helmet
    full of black water - and there is a face in it, pressed to the glass. Weighted boots, a hose torn off that
    trails behind, and the lighthouse anchor swung on its chain."""
    k = X.Kit("drowned_keeper")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(15, 16, 11), (22, 17, 11.6)], "teal", "suit")
    k.box(hips, C(0, 21, 0, 18, 2.8, 12.6), "brass", tag="weight_belt")
    for x in (-6, -2, 2, 6):
        k.box(hips, C(x, 16.4, 6.4, 3.0, 4.0, 1.4), "iron", tag="lead_weight")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.0
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -8), ("z", side * 8)), "hips")
        sh = k.part("shin_" + nm, (x, 11, 0), (("x", 12),), th)
        ft = k.part("foot_" + nm, (x, 3, 0), (("x", -4),), sh)
        k.stack(th, x, 0, [(11, 7.4, 7.6), (20, 8.4, 8.6)], "teal", "suit_leg")
        k.ring(th, x, 11.4, 0, 4.4, 1.0, "brass", "knee_band", n=10, axis="y")
        k.stack(sh, x, 0, [(3, 7.0, 7.2), (11, 7.6, 7.8)], "teal", "suit_leg")
        k.box(ft, C(x, 0, 1.8, 9.0, 4.4, 12), "iron", tag="foot")
        k.box(ft, C(x, 3.6, 1.8, 9.4, 1.2, 12.4), "brass", tag="boot_band")
    # ---------------------------------------------------------------- torso: the suit, the brass corselet, a torn hose
    to = k.part("torso", (0, 22, 0), (("x", 14),), "hips")
    k.stack(to, 0, 0, [(22, 17, 11.6), (29, 23, 13.6), (35, 27, 14.4), (39, 25, 13)], "teal", "suit")
    k.box(to, C(0, 34, 0, 26, 6, 15), "brass", tag="corselet")
    k.rivets(to, [(x, 39, 7.6) for x in (-10, -5, 0, 5, 10)], "iron", 1.0)
    barnacles(k, to, [(-6, 26, 6.6), (5, 29, 6.8), (8, 24, 6.0), (-9, 31, -6), (4, 27, -6.8)], s=1.4)
    pts = [(4, 37, -7), (6, 32, -11), (3, 24, -13), (6, 16, -14)]
    for (a, b) in zip(pts, pts[1:]):
        k.limb(to, a, b, 1.8, "iron", "hose")
    # ---------------------------------------------------------------- the helmet: brass, round, full of water and a face
    hd = k.part("head", (0, 39, 2), (("x", -14),), "torso")
    k.blob(hd, (0, 44, 3), (7.4, 7.0, 7.4), "brass", "helmet")
    k.blob(hd, (0, 44, 9.4), (4.4, 4.4, 1.2), "water", "porthole_water", step=0.8)
    k.ring(hd, 0, 44, 10.0, 4.6, 1.2, "brass", "porthole_rim", n=14)
    k.box(hd, C(-1.4, 45.4, 9.9, 1.2, 1.0, 0.6), "pale", tag="face_eye")
    k.box(hd, C(1.4, 45.4, 9.9, 1.2, 1.0, 0.6), "pale", tag="face_eye")
    k.box(hd, C(0, 42.6, 9.9, 2.6, 1.4, 0.6), "pale", tag="face_mouth")
    for sx in (-1.4, 1.4):
        k.box(hd, C(sx, 45.6, 10.2, 0.6, 0.6, 0.4), "eye", group="glow", tag="eye")
    for a in (90, 270):
        r = math.radians(a)
        k.ring(hd, math.sin(r) * 7.2, 44, 3, 2.4, 0.8, "brass", "side_port", n=10, axis="x")
    k.box(hd, C(0, 51, 3, 3.0, 1.6, 3.0), "brass", tag="helmet_valve")
    # ---------------------------------------------------------------- arms: the anchor on its chain
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 14
        up = k.part("arm_" + nm, (x, 37, 0), (("x", -20 if side > 0 else -60), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 26, 0), (("x", -30 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 15, 0), (), fo)
        k.blob(up, (x, 35, 0), (6.0, 5.0, 6.2), "teal", "shoulder")
        k.stack(up, x, 0, [(26, 7.0, 7.2), (33, 8.0, 8.2)], "teal", "sleeve")
        k.stack(fo, x, 0, [(16, 7.6, 7.6), (26, 7.2, 7.2)], "teal", "sleeve")
        k.box(fo, C(x, 16, 0, 8.6, 2.8, 8.6), "brass", tag="cuff")
        k.box(hn, C(x, 9.6, 0.6, 7.4, 6.4, 7.4), "iron", tag="glove")
    an = k.part("anchor", (-14, 10, 1), (("x", 30),), k.parts["hand_r"])
    k.chain(an, (-14, 10, 1), (-14, -2, 5), 5, w=1.8)
    k.limb(an, (-14, -2, 5), (-14, -22, 8), 3.0, "iron", "shank", d=2.6)
    k.limb(an, (-20, -5, 5.4), (-8, -5, 5.4), 2.2, "iron", "stock")
    for sx in (-1, 1):
        k.limb(an, (-14, -22, 8), (-14 + sx * 9, -16, 8), 2.8, "iron", "fluke_arm")
        k.shard(an, (-14 + sx * 9, -16, 8), (sx * 0.4, 1, 0), 5, 3.4, mat="iron", tag="fluke")
    barnacles(k, an, [(-13, -12, 9), (-15, -18, 9)], s=1.1)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Lamp Siren (caster)

def lamp_siren():
    """She was a keeper's wife who walked into the sea with a lamp to find him. Now she walks out of it: a pale
    woman in a shift gone to rags, kelp for hair, her arms long and her fingers webbed - and where her head should
    be, a stalk of pale flesh bends up and over and hangs a lure of light in front of her, warm and gold like a
    lamp in a window. If you look at it you walk to her."""
    k = X.Kit("lamp_siren")
    hips = k.part("hips", (0, 19, 0))
    k.stack(hips, 0, 0, [(1, 9.4, 7.6), (10, 8.6, 6.6), (19, 8.4, 6.0)], "linen", "shift")
    for (x, z, L) in ((-3.6, 3.2, 6), (3.2, 3.4, 8), (0, -3.4, 7), (-3, -3, 5)):
        k.limb(hips, (x, 3, z), (x * 1.1, 3 - L * 0.4, z * 1.3), 2.0, "linen", "rag", d=0.4)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.0
        th = k.part("thigh_" + nm, (x, 19, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 10, 0), (), th)
        ft = k.part("foot_" + nm, (x, 2, 0), (), sh)
        k.box(ft, C(x, 0, 1.2, 2.4, 1.2, 4.4), "pale", tag="foot")
    # ---------------------------------------------------------------- torso: thin, pale, the shift off one shoulder
    to = k.part("torso", (0, 19, 0), (("x", -4),), "hips")
    k.stack(to, 0, 0, [(19, 8.4, 6.0), (24, 9.4, 6.2), (29, 10.4, 6.0)], "pale", "body")
    k.stack(to, 0, 0, [(19, 8.8, 6.4), (26, 9.8, 6.6)], "linen", "shift")
    k.limb(to, (-4.4, 29, 0), (2.4, 25, 3.0), 1.6, "linen", "shift_strap", d=0.4)
    k.box(to, C(0, 28.6, 0, 3.4, 2.6, 3.0), "pale", tag="neck_stump")
    # the lure: a stalk up out of the neck, bending over in front, the lamp-light hanging
    hd = k.part("head", (0, 30, 0), (), "torso")
    stalk = [(0, 30, 0), (0, 35, -1), (0, 39, 1), (0, 39.6, 5), (0, 36.6, 8)]
    for (a, b), w in zip(zip(stalk, stalk[1:]), (2.0, 1.6, 1.2, 1.0)):
        k.limb(hd, a, b, w, "pale", "lure_stalk")
    k.blob(hd, (0, 34.0, 8.4), (3.2, 3.6, 3.2), "lamp", "lure", step=0.7)
    k.box(hd, C(0, 33.0, 10.6, 1.0, 1.0, 0.6), "eye", group="glow", tag="eye")
    for (x, z, L) in ((-2, -1, 16), (-0.8, -2.4, 20), (0.8, -2.4, 18), (2, -1, 15), (0, -1.8, 22)):
        k.limb(hd, (x, 31, z), (x * 1.6, 31 - L * 0.6, z - 3), 1.0, "kelp", "kelp_hair")
    # ---------------------------------------------------------------- arms: long, webbed, reaching
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.0
        up = k.part("arm_" + nm, (x, 28, 0), (("x", -70), ("z", side * 16)), "torso")
        fo = k.part("fore_" + nm, (x, 19.6, 0), (("x", -20),), up)
        hn = k.part("hand_" + nm, (x, 11.6, 0), (), fo)
        k.box(up, C(x, 19.8, 0, 2.2, 8.4, 2.4), "pale", tag="arm")
        k.box(fo, C(x, 12.0, 0, 2.0, 8.0, 2.2), "pale", tag="forearm")
        k.box(hn, C(x, 9.4, 0.3, 2.4, 2.6, 1.6), "pale", tag="hand")
        for t in (-0.9, -0.3, 0.3, 0.9):
            k.limb(hn, (x + t, 9.4, 0.8), (x + t * 1.6, 5.6, 1.6), 0.4, "pale", "finger")
        k.box(hn, C(x, 6.6, 1.2, 3.2, 2.6, 0.3), "glow", group="glow", tag="web")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Eyeless (skirmisher)

def eyeless():
    """It hunts by sound. Long-limbed and hunched, grey-white, no eyes at all - the front of its head is a cluster of
    pale frills that open and flutter at every footstep, round a jaw that splits three ways. Its arms end in hooked
    claws as long as knives. It waits in the dark until you make a noise."""
    k = X.Kit("eyeless")
    hips = k.part("hips", (0, 20, 0))
    k.box(hips, C(0, 17.6, 0, 6.4, 3.6, 4.4), "pale", tag="hips")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -40), ("z", side * 10)), "hips")
        sh = k.part("shin_" + nm, (x, 12, 0), (("x", 70),), th)
        ft = k.part("foot_" + nm, (x, 3, 0), (("x", -30),), sh)
        k.box(th, C(x, 12.2, 0, 2.8, 8.0, 3.0), "pale", tag="thigh")
        k.box(sh, C(x, 3.0, 0, 2.2, 9.0, 2.4), "pale", tag="shin")
        k.box(ft, C(x, 0, 1.0, 2.6, 2.0, 5.0), "pale", tag="foot")
        for t in (-0.7, 0.7):
            k.shard(ft, (x + t, 0.6, 3.4), (0, -0.3, 1), 1.6, 0.6, mat="dark", tag="foot")
    # ---------------------------------------------------------------- torso: hunched, ribs, a ridge of spines
    to = k.part("torso", (0, 20, 0), (("x", 40),), "hips")
    k.stack(to, 0, 0, [(20, 6.4, 4.4), (25, 8.0, 5.0), (31, 9.4, 5.4)], "pale", "body")
    for y in (23, 25, 27):
        k.box(to, C(0, y, 2.55, 7.0, 0.6, 0.4), "dark", tag="rib_gap")
    for i in range(5):
        k.shard(to, (0, 21 + i * 2.2, -2.6), (0, 0.4, -1), 2.0 + i * 0.3, 1.0, mat="pale", tag="spine")
    # ---------------------------------------------------------------- the head: no eyes, a cluster of frills, a jaw in three
    hd = k.part("head", (0, 31.4, 1.4), (("x", -36),), "torso")
    k.blob(hd, (0, 33.4, 2.0), (2.8, 2.6, 3.2), "pale", "skull", step=0.6)
    for i in range(10):
        a = i * 2 * math.pi / 10
        k.limb(hd, (math.cos(a) * 1.4, 33.6 + math.sin(a) * 1.4, 4.8), (math.cos(a) * 3.6, 33.6 + math.sin(a) * 3.6, 6.0), 1.6, "gum", "frill", d=0.4)
    for a in (90, 210, 330):        # the three-way jaw
        r = math.radians(a)
        k.shard(hd, (0, 33.6, 5.0), (math.cos(r) * 0.6, math.sin(r) * 0.6, 1), 3.0, 1.2, mat="pale", tag="jaw_split")
    k.box(hd, C(0, 33.2, 5.2, 1.2, 1.2, 0.4), "glow", group="glow", tag="throat_light")
    # ---------------------------------------------------------------- arms: long, the hooked claws
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.6
        up = k.part("arm_" + nm, (x, 29, 0), (("x", -60), ("z", side * 18)), "torso")
        fo = k.part("fore_" + nm, (x, 20, 0), (("x", -40),), up)
        hn = k.part("hand_" + nm, (x, 11, 0), (), fo)
        k.box(up, C(x, 20.4, 0, 2.2, 9.0, 2.4), "pale", tag="arm")
        k.box(fo, C(x, 11.4, 0, 2.0, 9.0, 2.2), "pale", tag="forearm")
        k.box(hn, C(x, 9.0, 0.3, 2.4, 2.4, 2.0), "pale", tag="hand")
        for t in (-0.8, 0.8):
            pts = [(x + t, 9.0, 1.0), (x + t, 4.0, 2.4), (x + t, 1.8, 5.0)]
            for (a, b), w in zip(zip(pts, pts[1:]), (0.9, 0.6)):
                k.limb(hn, a, b, w, "dark", "claw")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Deep Thing (swarm, on the spider)

def deep_thing():
    """What crawls up out of the dark under the reef: a pale soft body like a skinned hand, no eyes, eight long thin
    legs that bend too many ways, and on the front a round mouth of needles that opens wider than the body. They
    shrivel in the light. In the dark they are very fast."""
    k = X.Kit("deep_thing")
    body = k.part("body", (0, 6, 0))
    k.blob(body, (0, 6, 0), (4.6, 2.6, 5.0), "pale", "body", step=0.6)
    for (x, z) in ((-2, -2), (1.6, 1), (0, 3), (2.4, -3)):
        k.box(body, C(x, 8.4, z, 0.8, 0.4, 1.6), "gum", tag="vein")
    hd = k.part("head", (0, 6, 4.6), (), "body")
    k.blob(hd, (0, 6.0, 6.4), (3.4, 3.0, 2.0), "pale", "head", step=0.6)
    needles(k, hd, 0, 6.4, 8.2, 4.8, 3.6, n=6, s=1.0)
    k.box(hd, C(0, 5.4, 8.0, 1.6, 1.4, 0.4), "glow", group="glow", tag="throat_light")
    ab = k.part("abdomen", (0, 6, -4), (("x", -10),), "body")
    k.blob(ab, (0, 6.4, -8.0), (4.0, 3.0, 4.6), "pale", "abdomen", step=0.6)
    k.box(ab, C(0, 8.4, -8, 3.0, 0.6, 5.0), "gum", tag="vein")
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, z in enumerate((2.6, 0.9, -0.9, -2.6)):
            nm = "leg_%s%d" % (s, i)
            lg = k.part(nm, (side * 3.6, 6, z), (("y", -side * (i - 1.5) * 24),), "body")
            k1 = (side * 8.0, 11.0, z)
            k2 = (side * 12.0, 7.0, z * 1.2)
            k.limb(lg, (side * 3.6, 6.4, z), k1, 1.0, "pale", "leg")
            k.limb(lg, k1, k2, 0.8, "pale", "leg")
            k.limb(lg, k2, (side * 13.6, 0.4, z * 1.3), 0.6, "pale", "foot")
            joints[nm] = ("LL" if side > 0 else "RL") + str(i + 1)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


MOBS = {
    "deep_thing": dict(make=deep_thing, rig="crawler", ent=(1.0, 0.8), stats=dict(hp=34, speed=0.4, dmg=8, armor=3, kb=0)),
    "drowned_keeper": dict(make=drowned_keeper, ent=(1.8, 4.0), stats=dict(hp=150, speed=0.18, dmg=19, armor=14, kb=1.0)),
    "lamp_siren": dict(make=lamp_siren, ent=(0.9, 2.8), stats=dict(hp=55, speed=0.22, dmg=9, armor=3, kb=0)),
    "eyeless": dict(make=eyeless, ent=(0.9, 2.8), stats=dict(hp=48, speed=0.4, dmg=10, armor=4, kb=0)),
    "angler_knight": dict(make=angler_knight, ent=(1.4, 3.7), stats=dict(hp=290, speed=0.23, dmg=17, armor=15, kb=0.7), key=True),
    "keeper_in_light": dict(make=keeper_in_light, texel=1, ent=(2.6, 6.8), stats=dict(hp=800, speed=0.22, dmg=24, armor=12, kb=1.0), boss=True),
}
