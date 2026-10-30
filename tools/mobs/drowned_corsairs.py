"""The Drowned Corsairs: the crews of every ship the sea took, who hold the world's wrecks, pirate ships, galleys,
lighthouses, sunken cities and ocean monuments, built by hand (tools/vox2.py). Tar-black coats gone green with
weed, salt-white bone, barnacles and red coral grown through them, rusted iron and tarnished brass, kelp for hair,
and the sea-green ghostlight the drowned see by. (No crabs or bells - those are the Tide Chapel's.)

    kraken_spawn       swarm   a young kraken the size of a dog: a mantle, a beak, glowing eyes, tentacles curling
    drowned_corsair    skirm   a pirate dead a hundred years: tricorne, rotten coat, coral through his ribs, a cutlass
                               and a boarding hook
    harpooner          guard   a drowned whaler in a brass diving helm, the porthole full of green light, a harpoon
                               on a rope
    anchor_hauler      brute   a bloated giant of a deckhand dragging a ship's anchor on its chain
    tide_caller        caster  the navigator: kelp hair, a coat of weed, a pearl burning on the end of a spyglass staff
    dread_captain      elite   the captain: a greatcoat with gold gone green, a tricorne with skulls and plumes, a beard
                               of tentacles, a kraken's arm for his left, a cutlass in his right

    python tools/monsterforge.py drowned_corsairs --preview ; python tools/mobsheet.py drowned_corsairs
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import grow
from _folk import lit, eyes, straps, legs, arms, held, quad

COAT = ramp("#060c0c", "#0c1616", "#122020", "#1a2c2a", "#243a36", "#304a44")
WEED = ramp("#0c140a", "#16220e", "#203014", "#2c401a", "#3a5222", "#4c662c")
BONE = ramp("#3a3c36", "#585a52", "#7a7c72", "#9c9e92", "#bec0b2", "#dcdccc")
BARN = ramp("#4a4840", "#6a685e", "#8a887c", "#aaa89a", "#cac8b8")
CORAL = ramp("#3a0a0e", "#601418", "#8a2024", "#b03430", "#d0503e", "#ec7a5a")
DROWN = ramp("#16201e", "#202e2c", "#2c3e3a", "#3a504a", "#4a625a", "#5e7a70")
IRON = ramp("#0e0a08", "#1a120c", "#2a1a10", "#3c2414", "#4e301a", "#643e22")
BRASS = ramp("#160c06", "#2a160a", "#44240e", "#623614", "#80481c", "#a05e28")
GOLD = ramp("#2a1c06", "#4a320a", "#765412", "#a47c20", "#cca232", "#ecc85a")
WOOD = ramp("#0c0a08", "#16120e", "#221a14", "#2e241a", "#3c2e22")
SQUID = ramp("#1a0a14", "#2c1020", "#42182e", "#5a223e", "#742e4e", "#90405e")
GHOST = ramp("#04382a", "#0a6448", "#14966a", "#3ccc96", "#88f4c4", "#dcfff0")
DULL = ramp("#121210", "#22201a", "#363024", "#4c4432", "#665a42", "#827254")
VERDI = ramp("#0c2220", "#14382e", "#1e5040", "#2e6a52", "#468a6a")
TAR = ramp("#040606", "#080c0c", "#0e1212", "#141a1a")


def shaders():
    return {
        "coat": X.surf(COAT, 0.5, 1.1, 0.22, 0.04, holes=True, crust=(WEED, 0.24)),
        "weed": X.surf(WEED, 0.5, 1.0, 0.3, 0.0, stripe=2),
        "bone": X.surf(BONE, 0.55, 1.2, 0.16, 0.12, crust=(BARN, 0.2)),
        "barnacle": X.surf(BARN, 0.56, 1.4, 0.3, 0.2, pattern=lambda p, n, i, j, w, h: 0.2 if (i * 3 + j * 5) % 7 == 0 else -0.04),
        "coral": X.surf(CORAL, 0.55, 1.3, 0.26, 0.16),
        "drowned": X.wrinkled(DROWN, 1.2),
        "iron": X.surf(IRON, 0.5, 1.4, 0.24, 0.2, crust=(BARN, 0.16)),
        "brass": X.surf(BRASS, 0.55, 1.4, 0.16, 0.24, rust=(WEED, 0.24, 0.6)),
        "helm": X.surf(DULL, 0.5, 1.4, 0.14, 0.22, rust=(VERDI, 0.34, 0.45)),
        "gold": X.surf(GOLD, 0.55, 1.4, 0.14, 0.22, rust=(WEED, 0.3, 0.5)),
        "wood": X.surf(WOOD, 0.5, 1.0, 0.22, 0.06, stripe=3),
        "leather": X.surf(TAR, 0.5, 1.1, 0.2, 0.04),
        "squid": X.wrinkled(SQUID, 0.8),
        "steel": X.surf(BONE, 0.62, 1.6, 0.06, 0.3),
        "ghost": X.glow(GHOST),
        "eye": X.glow(GHOST, 0.84, 0.14),
        "dark": X.dark(TAR),
    }


GLOWS = {"ghost", "eye"}


def barnacles(k, part, at, n, r, seed=1):
    """a patch of barnacles round `at`"""
    cx, cy, cz = at
    for i in range(n):
        a = (i * 2.399 + seed) % (2 * math.pi)
        d = r * ((i * 0.618 + seed * 0.1) % 1)
        s = 0.7 + ((i * 7 + seed) % 3) * 0.25
        k.box(part, C(cx + math.cos(a) * d, cy + math.sin(a) * d * 0.7, cz, s, s, 0.6), "barnacle", tag="barnacle")


def coral(k, part, base, d, s=1.0, seed=0):
    """a branch of red coral growing out of something"""
    bx, by, bz = base
    tip = (bx + d[0] * 3.0 * s, by + d[1] * 3.0 * s, bz + d[2] * 3.0 * s)
    k.limb(part, base, tip, 0.9 * s, "coral", "coral")
    for t in (-1, 1):
        k.limb(part, tip, (tip[0] + t * 1.4 * s, tip[1] + 1.8 * s, tip[2] + 0.4 * s * t), 0.7 * s, "coral", "coral")


def tricorne(k, part, c, s=1.0, mat="coat", trim="gold"):
    cx, cy, cz = c
    k.blob(part, (cx, cy + 1.6 * s, cz), (3.6 * s, 1.8 * s, 3.6 * s), mat, "hat_crown", step=0.6)
    for a in (0, 2 * math.pi / 3, 4 * math.pi / 3):   # three turned-up brims, a point at the front
        x, z = math.sin(a) * 4.0 * s, math.cos(a) * 4.0 * s
        k.limb(part, (cx + x * 0.2, cy + 0.8 * s, cz + z * 0.2), (cx + x, cy + 2.0 * s, cz + z), 3.6 * s, mat, "hat_brim", d=0.8)
        k.box(part, C(cx + x, cy + 2.0 * s, cz + z, 1.2 * s, 0.5, 1.2 * s), trim, tag="hat_trim")


def cutlass(k, part, x, y, z, L=14, mat="steel"):
    k.limb(part, (x, y - 4.0, z), (x, y + 1.0, z), 1.2, "leather", "grip")
    k.box(part, C(x, y - 5.0, z, 1.6, 1.2, 1.6), "brass", tag="pommel")
    k.box(part, C(x, y + 0.6, z, 1.2, 1.0, 3.6), "brass", tag="guard")
    k.limb(part, (x, y - 4.0, z + 1.6), (x, y + 0.8, z + 1.8), 0.5, "brass", "knuckle_bow")
    for i in range(int(L / 2)):
        w = 2.4 + (0.6 if i > L / 2 - 4 else 0)
        k.box(part, C(x, y + 1.6 + i * 2.0, z + 0.4 + (i * i) * 0.03, 0.7, 2.05, w), mat, tag="cutlass_blade")
    k.shard(part, (x, y + 1.6 + L, z + 0.4 + (L * L / 4) * 0.03 + 0.8), (0, 0.6, 0.8), 2.2, 1.0, mat=mat, tag="blade_tip")


# ================================================================ the Kraken Spawn (swarm)

def kraken_spawn():
    """The sea's dogs. A kraken still young enough to come up the beach after you: a mantle the size of a barrel,
    two great eyes full of the ghostlight, a parrot's beak, and the arms curling and slapping all round it."""
    k = X.Kit("kraken_spawn")
    body, hd, ab, joints = quad(k, "squid", y=9, chest=((4, 10, 10), (8, 11, 11), (11, 9, 9)), haunch=((4, 9, 8), (8, 10, 9), (11, 8, 8)),
                                leg_w=2.4, foot_w=1.8, front_z=4, back_z=-5, x=4.4, head_at=(0, 12, 2), head_rot=-20, claw="squid", foot_len=4.0)
    # the mantle, tall and swollen, leaning back
    k.blob(ab, (0, 18.0, -4.0), (6.4, 7.6, 6.8), "squid", "mantle", step=0.9)
    k.shard(ab, (0, 24.0, -6.4), (0, 0.6, -1), 4.4, 6.0, mat="squid", tag="mantle_tip")
    for sx in (-1, 1):
        k.box(ab, C(sx * 6.0, 15.6, -5.0, 0.8, 5.4, 6.0), "squid", tag="fin")
    for i, (x, y) in enumerate(((-3, 19), (2, 21), (4, 16), (-1, 23))):
        k.box(ab, C(x, y, 2.2, 1.6, 1.6, 0.4), "ghost", tag="spot")
    for sx in (-1, 1):                            # the eyes, huge, either side of the head
        k.blob(hd, (sx * 4.0, 12.6, 4.0), (1.8, 2.0, 2.0), "squid", "eye_bulb", step=0.6)
        k.box(hd, C(sx * 5.4, 11.8, 4.0, 0.4, 1.8, 2.2), "eye", tag="eye")
        k.box(hd, C(sx * 5.5, 12.2, 4.0, 0.3, 0.8, 0.6), "dark", tag="pupil")
    k.shard(hd, (0, 9.6, 7.0), (0, -0.6, 1), 2.6, 2.0, mat="dark", tag="beak")
    # the arms: eight of them, out and curling up at the tips (on top of the four it walks on)
    for i in range(8):
        a = (i + 0.5) * math.pi / 4
        part = body if math.cos(a) > 0 else ab
        x, z = math.sin(a), math.cos(a)
        p0 = (x * 4.0, 7.0, z * 4.0 + 1.0)
        p1 = (x * 9.0, 2.0, z * 9.0 + 1.0)
        p2 = (x * 13.0, 1.4, z * 13.0 + 1.0)
        p3 = (x * 14.6, 4.6, z * 13.6 + 1.0)
        for (a0, a1), w in zip(((p0, p1), (p1, p2), (p2, p3)), (2.6, 1.8, 1.2)):
            k.limb(part, a0, a1, w, "squid", "arm")
        for t in (0.3, 0.6):
            q = tuple(p1[j] + (p2[j] - p1[j]) * t for j in range(3))
            k.box(part, C(q[0], q[1] - 0.6, q[2], 0.8, 0.5, 0.8), "barnacle", tag="sucker")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Drowned Corsair (skirmisher)

def drowned_corsair():
    """A pirate dead a hundred years who never stopped. A tricorne that has rotted round his skull, a long coat green
    with weed, the shirt gone and the ribs bare with red coral grown up through them, barnacles on his shins, a
    cutlass in one fist and a boarding hook in the other, and the ghostlight in his eyes."""
    k = X.Kit("drowned_corsair")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(13, 10.8, 7.6), (20, 10.6, 7.4)], "coat", "breeches")
    k.box(hips, C(0, 19.0, 0, 11.6, 1.8, 8.2), "leather", tag="belt")
    k.box(hips, C(0, 18.8, 4.2, 2.4, 2.2, 0.6), "brass", tag="buckle")
    k.box(hips, C(4.8, 12.6, 4.0, 2.6, 6.0, 0.6), "coral", tag="sash")
    for i, (x, z, L) in enumerate(((-5.4, 2.0, 15), (5.4, 2.0, 14), (-4.2, -4.0, 17), (0, -4.4, 18), (4.2, -4.0, 16))):
        k.box(hips, C(x, 20 - L, z, 3.0, L - 2.0, 0.7), "coat", tag="coat_tail")
        k.box(hips, C(x + 0.6, 20 - L, z - 0.1, 1.0, 2.4, 0.5), "weed", tag="weed")
    legs(k, hips, 19, 10.4, 3.2, "coat", "leather", knee_mat=None, lean=-8, bend=10, w=5.0)
    for side in (1, -1):
        barnacles(k, k.parts["shin_" + ("l" if side > 0 else "r")], (side * 3.2, 6.0, 2.8), 6, 2.0, seed=side + 3)
    to = k.part("torso", (0, 20, 0), (("x", 12),), "hips")
    k.stack(to, 0, 0, [(20, 10.6, 7.4), (25, 11.6, 7.8), (30, 13.6, 8.4), (34, 13.6, 8.0)], "bone", "ribcage")
    for y in range(22, 33, 2):                    # the ribs, the dark between them
        k.box(to, C(0, y + 0.8, 3.95, 7.4, 0.8, 0.3), "dark", tag="rib_gap")
    coral(k, to, (1.4, 24.0, 3.4), (0.3, 1, 0.5), 1.0)
    coral(k, to, (-2.0, 27.0, 3.4), (-0.4, 1, 0.4), 0.8, seed=2)
    k.box(to, C(0, 25.0, 3.2, 3.0, 3.0, 0.8), "ghost", tag="drowned_light")
    for sx in (-1, 1):                            # the open coat over it
        k.box(to, C(sx * 5.2, 20.0, 1.0, 2.4, 14.0, 7.8), "coat", tag="coat")
        k.box(to, C(sx * 4.2, 22.0, 4.2, 1.2, 12.0, 0.6), "coat", tag="lapel")
        for y in (24, 28):
            k.box(to, C(sx * 4.2, y, 4.6, 0.8, 0.8, 0.3), "gold", tag="button")
        k.blob(to, (sx * 7.0, 32.0, 0), (2.8, 2.0, 3.4), "coat", "shoulder", step=0.7)
    k.box(to, C(0, 20.0, -4.2, 10.4, 14.0, 0.8), "coat", tag="coat_back")
    barnacles(k, to, (3.0, 30.0, -4.7), 7, 2.4, seed=5)
    hd = k.part("head", (0, 34, 0.6), (("x", -6),), "torso")
    k.box(hd, C(0, 34.4, 0.6, 5.6, 6.4, 5.6), "bone", tag="skull")
    k.box(hd, C(0, 33.0, 1.4, 4.4, 2.0, 4.6), "bone", tag="jaw")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.2, 37.0, 3.4, 1.6, 1.6, 0.3), "dark", tag="socket")
        k.box(hd, C(sx * 1.2, 37.4, 3.5, 0.8, 0.8, 0.3), "eye", tag="eye")
    k.box(hd, C(0, 35.6, 3.45, 0.8, 1.0, 0.3), "dark", tag="nose_hole")
    for i in range(5):
        k.box(hd, C(-1.6 + i * 0.8, 34.0, 3.45, 0.5, 0.9, 0.3), "bone" if i != 2 else "gold", tag="teeth")
    for i in range(6):                            # kelp hanging from under the hat
        a = -1.2 + i * 0.48
        k.limb(hd, (math.sin(a) * 3.0, 39.6, math.cos(a) * 3.0 - 1.0), (math.sin(a) * 3.6, 32.0 - (i % 2) * 1.6, math.cos(a) * 3.4 - 2.4), 0.9, "weed", "kelp_hair")
    tricorne(k, hd, (0, 39.6, 0.6), 1.0)
    k.box(hd, C(0, 41.0, 4.2, 1.4, 1.4, 0.4), "bone", tag="hat_skull")
    arms(k, to, 7.2, 32, "coat", {1: ((("x", -16), ("z", 30)), (("x", -60),)), -1: ((("x", -50), ("z", -12)), (("x", -40),))}, glove="bone", w=3.6)
    cl = held(k, "cutlass", "r", (-7.2, 14.2, 0.3), (("x", 70),))
    cutlass(k, cl, -7.2, 14.8, 0.3)
    bh = held(k, "hook", "l", (7.2, 14.2, 0.3), (("x", 60),))
    k.limb(bh, (7.2, 10.0, 0.3), (7.2, 22.0, 0.3), 1.2, "wood", "hook_haft")
    k.limb(bh, (7.2, 22.0, 0.3), (7.2, 25.4, 2.0), 1.0, "iron", "hook")
    k.limb(bh, (7.2, 25.4, 2.0), (7.2, 24.0, 4.6), 0.9, "iron", "hook")
    k.shard(bh, (7.2, 24.0, 4.6), (0, -1, -0.2), 2.0, 0.8, mat="iron", tag="hook_point")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Harpooner (guard)

def harpooner():
    """The whalers went down in their diving gear and stayed down. A brass helm like a bell with three round ports,
    the face behind them gone and only the green light inside, a canvas suit black with tar and crusted with
    barnacles, lead boots, an air-hose torn off and trailing, and a harpoon with its rope coiled on his arm."""
    k = X.Kit("harpooner")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(11, 12.0, 8.6), (20, 12.0, 8.6)], "leather", "suit")
    k.box(hips, C(0, 18.6, 0, 13.0, 2.4, 9.6), "brass", tag="weight_belt")
    for x in (-4.4, 0, 4.4):
        k.box(hips, C(x, 16.0, 4.6, 3.0, 2.6, 1.0), "iron", tag="lead_weight")
    legs(k, hips, 19, 10.4, 3.6, "leather", "iron", knee_mat="brass", lean=-4, bend=6, w=5.8)
    for side in (1, -1):
        barnacles(k, k.parts["thigh_" + ("l" if side > 0 else "r")], (side * 3.6, 15.0, 3.2), 5, 2.0, seed=side)
    to = k.part("torso", (0, 20, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(20, 12.0, 8.6), (26, 13.4, 9.2), (31, 15.4, 9.8), (34, 15.0, 9.4)], "leather", "suit")
    # the corselet: a brass collar on the shoulders, bolted, that the helm screws onto
    k.stack(to, 0, 0, [(30.6, 16.0, 10.4), (33.6, 15.4, 10.0)], "brass", "corselet")
    for a in range(0, 360, 45):
        r = math.radians(a)
        k.box(to, C(math.sin(r) * 7.4, 33.4, math.cos(r) * 4.8, 1.0, 1.0, 1.0), "iron", tag="bolt")
    barnacles(k, to, (-3.0, 25.0, 4.6), 8, 2.6, seed=7)
    coral(k, to, (4.0, 27.0, 4.4), (0.5, 1, 0.3), 0.9)
    k.box(to, C(0, 21.0, -5.2, 7.0, 8.4, 2.4), "brass", tag="air_tank")
    k.limb(to, (3.0, 28.0, -5.0), (7.0, 22.0, -6.4), 1.4, "leather", "air_hose")
    k.limb(to, (7.0, 22.0, -6.4), (8.0, 14.0, -5.0), 1.4, "leather", "air_hose")
    # the helm: a brass bell, a big port at the front and one each side, full of light
    hd = k.part("head", (0, 34, 0.4), (("x", -2),), "torso")
    k.stack(hd, 0, 0.4, [(34.2, 9.8, 9.8), (37.0, 10.8, 10.8), (40.4, 10.6, 10.6), (42.8, 8.8, 8.8), (44.4, 5.6, 5.6)], "helm", "dive_helm", step=1.0)
    k.box(hd, C(0, 35.2, 5.4, 6.6, 6.4, 1.0), "helm", tag="port_frame")       # the square faceplate, bolted
    k.box(hd, C(0, 36.0, 5.6, 4.8, 4.8, 1.0), "ghost", tag="port_glass")
    for x in (-1.2, 1.2):
        k.box(hd, C(x, 35.8, 6.2, 0.5, 5.2, 0.5), "iron", tag="port_grille")
    k.box(hd, C(0, 38.2, 6.2, 5.2, 0.5, 0.5), "iron", tag="port_grille")
    for x, y in ((-2.8, 35.6), (2.8, 35.6), (-2.8, 40.8), (2.8, 40.8)):
        k.box(hd, C(x, y, 6.0, 0.9, 0.9, 0.6), "iron", tag="bolt")
    for sx in (-1, 1):
        k.box(hd, C(sx * 5.3, 36.6, 0.4, 0.8, 3.6, 3.6), "helm", tag="side_port")
        k.box(hd, C(sx * 5.6, 37.2, 0.4, 0.4, 2.4, 2.4), "ghost", tag="port_glass")
    k.box(hd, C(0, 44.8, 0.4, 2.0, 2.0, 2.0), "iron", tag="valve")
    k.box(hd, C(3.0, 41.6, -4.4, 1.6, 1.6, 2.4), "iron", tag="hose_cock")
    barnacles(k, hd, (2.0, 41.4, 4.4), 5, 1.6, seed=2)
    arms(k, to, 9.0, 32, "leather", {1: ((("x", -30), ("z", -6)), (("x", -40),)), -1: ((("x", -44), ("z", 8)), (("x", -40),))}, glove="iron", w=4.6)
    k.ring(k.parts["fore_l"], 9.0, 20.6, 0, 3.6, 1.2, "wood", "rope_coil", n=12, axis="y")
    k.ring(k.parts["fore_l"], 9.0, 22.2, 0, 3.4, 1.2, "wood", "rope_coil", n=12, axis="y")
    hp = held(k, "harpoon", "r", (-9.0, 14.4, 0.4), (("x", 100), ("z", 4)))
    k.limb(hp, (-9.0, -4.0, 0.4), (-9.0, 34.0, 0.4), 1.4, "wood", "harpoon_shaft")
    for y in (6.0, 18.0):
        k.box(hp, C(-9.0, y, 0.4, 1.8, 1.0, 1.8), "iron", tag="shaft_band")
    k.box(hp, C(-9.0, 34.0, 0.4, 1.6, 2.4, 1.6), "iron", tag="socket")
    k.shard(hp, (-9.0, 36.0, 0.4), (0, 1, 0), 6.4, 2.6, mat="steel", tag="harpoon_head")
    for sz in (-1, 1):                            # the barbs, back-swept
        k.shard(hp, (-9.0, 37.6, 0.4 + sz * 0.8), (0, -0.8, sz * 0.6), 3.0, 1.0, mat="steel", tag="barb")
    k.ring(hp, -9.0, -3.0, 0.4, 1.2, 0.5, "iron", "rope_eye", n=8, axis="x")
    k.limb(hp, (-9.0, -3.0, 0.4), (-6.0, 2.0, -2.0), 0.6, "wood", "rope")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Anchor Hauler (brute)

def anchor_hauler():
    """The biggest man on any crew gets the anchor. This one went down with it and came back up dragging it: a
    giant bloated with the sea, skin like wet grey rope, barnacles in great crusts down his back, a sailor's
    stripes rotted off him, chain wound round both arms, and over his shoulder a ship's anchor bigger than a man."""
    k = X.Kit("anchor_hauler")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(12, 15, 10.6), (21, 16, 11.4)], "coat", "trousers")
    k.box(hips, C(0, 20.0, 0, 16.6, 2.4, 12.0), "wood", tag="rope_belt")
    k.box(hips, C(6.0, 13.6, 5.6, 3.0, 6.4, 0.6), "coral", tag="rag")
    legs(k, hips, 20, 11.0, 4.8, "coat", "drowned", knee_mat=None, lean=-4, bend=6, w=7.0, cuff=False)
    for side in (1, -1):
        barnacles(k, k.parts["shin_" + ("l" if side > 0 else "r")], (side * 4.8, 6.0, 3.8), 7, 2.4, seed=side + 9)
    to = k.part("torso", (0, 21, 0), (("x", 14),), "hips")
    k.stack(to, 0, 0, [(21, 16, 11.4), (26, 19, 12.6), (31, 23, 13.4), (35, 24, 13.0), (37.6, 19, 10.6)], "drowned", "chest")
    k.blob(to, (0, 25.4, 3.6), (7.4, 4.6, 4.6), "drowned", "belly", step=0.9)
    for y in (27.0, 30.0, 33.0):                  # the striped shirt, rotted to bands
        k.box(to, C(-4.0, y, 5.4, 9.0, 1.2, 1.0), "coat", tag="shirt_stripe")
    k.box(to, C(5.0, 30.6, 6.2, 3.0, 4.0, 0.4), "dark", tag="tear")
    k.blob(to, (0, 34.0, -4.4), (9.0, 5.0, 3.6), "drowned", "hump", step=0.9)
    for (x, y, n) in ((-5.0, 33.0, 10), (4.0, 30.0, 9), (0, 26.0, 8)):        # crusts of barnacles down his back
        barnacles(k, to, (x, y, -7.4), n, 3.0, seed=int(x + y))
    coral(k, to, (-6.0, 36.0, -5.4), (-0.4, 1, -0.3), 1.3)
    coral(k, to, (5.0, 35.0, -5.6), (0.4, 1, -0.4), 1.1, seed=3)
    hd = k.part("head", (0, 37.0, 3.0), (("x", -14),), "torso")
    k.box(hd, C(0, 37.4, 4.4, 8.0, 7.4, 7.6), "drowned", tag="head")
    k.box(hd, C(0, 36.0, 4.8, 9.0, 3.2, 7.8), "drowned", tag="jowls")
    k.box(hd, C(0, 42.6, 6.8, 8.4, 1.4, 2.4), "drowned", tag="brow")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.0, 40.8, 8.2, 1.8, 1.2, 0.3), "dark", tag="socket")
        k.box(hd, C(sx * 2.0, 41.0, 8.25, 1.0, 0.7, 0.3), "eye", tag="eye")
    k.box(hd, C(0, 37.4, 8.35, 4.4, 1.6, 0.3), "dark", tag="mouth")
    for i in range(5):                            # water still running out of it
        k.box(hd, C(-1.6 + i * 0.8, 35.4 - (i % 2) * 1.2, 8.4, 0.4, 1.6 + (i % 2) * 1.2, 0.3), "ghost", tag="seawater")
    k.blob(hd, (0, 44.6, 4.0), (4.4, 1.6, 4.0), "coat", "knit_cap", step=0.7)
    k.box(hd, C(0, 43.4, 4.0, 9.0, 1.6, 8.4), "coat", tag="cap_roll")
    arms(k, to, 13.0, 34, "drowned", {1: ((("x", -70), ("z", -20)), (("x", -40),)), -1: ((("x", -12), ("z", 12)), (("x", -10),))}, w=6.4, long=1.15)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        for y in (19.0, 21.4, 23.8):
            k.ring(k.parts["fore_" + nm], side * 13.0, y, 0, 3.6, 0.9, "iron", "chain_wrap", n=10, axis="y")
    # the anchor dragged in his right fist: the shank through it, the stock across, the flukes trailing behind
    an = held(k, "anchor", "r", (-13.0, 14.0, 0.4), (("x", 72),))     # dragged behind him, flukes in the dirt
    k.limb(an, (-13.0, -10.0, 0.4), (-13.0, 26.0, 0.4), 3.0, "iron", "shank")
    k.ring(an, -13.0, 28.6, 0.4, 2.6, 1.2, "iron", "anchor_ring", n=10, axis="x")
    k.box(an, C(-13.0, 22.0, 0.4, 2.4, 2.4, 18.0), "wood", tag="stock")
    for sz in (-1, 1):
        k.box(an, C(-13.0, 21.8, 0.4 + sz * 9.2, 3.0, 2.8, 1.4), "iron", tag="stock_cap")
    for sz in (-1, 1):                            # the arms of the anchor and their flukes
        k.limb(an, (-13.0, -10.0, 0.4), (-13.0, -6.0, 0.4 + sz * 8.0), 2.6, "iron", "anchor_arm")
        k.limb(an, (-13.0, -6.0, 0.4 + sz * 8.0), (-13.0, -1.0, 0.4 + sz * 10.0), 2.2, "iron", "anchor_arm")
        k.box(an, C(-13.0, -3.6, 0.4 + sz * 9.6, 1.6, 5.0, 4.0), "iron", tag="fluke")
        k.shard(an, (-13.0, -1.0, 0.4 + sz * 10.0), (0, 1, sz * 0.2), 2.6, 1.6, mat="iron", tag="fluke_point")
    k.box(an, C(-13.0, -12.0, 0.4, 4.0, 2.4, 4.0), "iron", tag="crown")
    barnacles(k, an, (-11.4, -6.0, 6.0), 6, 2.0, seed=4)
    coral(k, an, (-13.0, 2.0, 1.8), (0.1, 1, 0.6), 1.0, seed=6)
    k.chain(an, (-13.0, 28.6, 0.4), (-6.0, 10.0, 6.0), 7, w=1.4)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.35)
    return k.s, k.parts


# ================================================================ the Tide Caller (caster)

def tide_caller():
    """Every ship had a navigator; the drowned ones still steer, and the sea comes when they call it. A long
    weed-green coat with its brass buttons gone to verdigris, kelp hanging off her for hair down to her knees, a
    face drowned white with eyes of ghostlight, and the long brass spyglass she uses for a staff, a pearl burning
    green at its end."""
    k = X.Kit("tide_caller")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(3, 14.4, 11.6), (10, 12.6, 9.6), (20, 11.0, 8.0)], "coat", "long_coat", step=1.0)
    for i in range(9):                            # the coat's hem in tatters, weed trailing off it
        a = i * 2 * math.pi / 9
        k.box(hips, C(math.cos(a) * 6.0, 0.6, math.sin(a) * 5.2, 2.2, 3.0, 0.8), "weed", tag="hem_weed")
    for side, nm in ((1, "l"), (-1, "r")):
        th = k.part("thigh_" + nm, (side * 3.0, 19, 0), (("x", -4),), hips)
        sh = k.part("shin_" + nm, (side * 3.0, 10.4, 0), (("x", 6),), th)
        ft = k.part("foot_" + nm, (side * 3.0, 2.4, 0), (), sh)
        k.box(ft, C(side * 3.0, 0, 1.6, 4.4, 2.4, 7.0), "leather", tag="foot")
    k.box(hips, C(0, 19.0, 0, 11.6, 1.6, 8.4), "brass", tag="sash_buckle")
    to = k.part("torso", (0, 20, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(20, 11.0, 8.0), (25, 11.4, 8.0), (30, 13.0, 8.4), (34, 12.8, 8.0)], "coat", "coat")
    for y in (22, 25, 28, 31):
        for sx in (-1.8, 1.8):
            k.box(to, C(sx, y, 4.15, 0.8, 0.8, 0.3), "brass", tag="button")
    k.box(to, C(0, 31.0, 4.2, 6.0, 3.0, 0.4), "drowned", tag="throat")
    k.box(to, C(0, 22.0, -4.2, 3.0, 11.0, 0.6), "weed", tag="hair_back")
    for sx in (-1, 1):
        k.blob(to, (sx * 6.8, 32.2, 0), (2.6, 2.0, 3.2), "coat", "shoulder", step=0.7)
        k.box(to, C(sx * 7.0, 33.6, 0, 3.4, 0.6, 3.4), "gold", tag="epaulette")
    hd = k.part("head", (0, 34, 0.6), (("x", -6),), "torso")
    k.box(hd, C(0, 34.6, 0.8, 5.6, 6.6, 5.6), "drowned", tag="face")
    k.box(hd, C(0, 37.6, 3.65, 5.6, 1.0, 0.3), "dark", tag="brow_shadow")
    eyes(k, hd, 36.6, 3.7, 1.3, 1.2, h=0.8)
    k.box(hd, C(0, 35.0, 3.65, 1.6, 0.4, 0.3), "dark", tag="mouth")
    k.blob(hd, (0, 39.8, 0.2), (3.8, 2.0, 3.8), "weed", "kelp_scalp", step=0.6)
    for i in range(12):                           # the kelp hair, to her knees
        a = math.radians(-150 + i * 27)
        x, z = math.sin(a) * 3.4, math.cos(a) * 3.4 + 0.2
        if z > 2.6:
            continue
        L = 14.0 + (i % 3) * 4.0
        k.limb(hd, (x, 39.6, z), (x * 1.5, 39.6 - L * 0.5, z * 1.4 - 1.0), 1.2, "weed", "kelp_hair", d=0.6)
        k.limb(hd, (x * 1.5, 39.6 - L * 0.5, z * 1.4 - 1.0), (x * 1.7, 39.6 - L, z * 1.5 - 1.6), 1.0, "weed", "kelp_hair", d=0.6)
    for sx in (-1, 1):                            # a necklace of shells
        k.box(hd, C(sx * 1.6, 32.6, 3.6, 1.0, 1.0, 0.6), "barnacle", tag="shell")
    k.box(hd, C(0, 32.0, 3.8, 1.2, 1.2, 0.5), "ghost", tag="pearl_drop")
    arms(k, to, 7.0, 32, "coat", {1: ((("x", -16), ("z", -6)), (("x", -60),)), -1: ((("x", -56), ("z", -4)), (("x", -30),))}, glove="drowned", w=3.4)
    st = held(k, "spyglass", "r", (-7.0, 14.4, 0.4), (("x", 64), ("z", -6)))
    for i, (y0, y1, w) in enumerate(((-8.0, 6.0, 1.6), (6.0, 18.0, 2.0), (18.0, 28.0, 2.4))):  # the drawn spyglass, three tubes
        k.limb(st, (-7.0, y0, 0.4), (-7.0, y1, 0.4), w, "brass", "spyglass")
        k.box(st, C(-7.0, y1 - 0.6, 0.4, w + 0.6, 1.0, w + 0.6), "gold", tag="spyglass_ring")
    k.ring(st, -7.0, 30.4, 0.4, 2.6, 0.8, "brass", "pearl_claw", n=8, axis="x")
    k.blob(st, (-7.0, 31.0, 0.4), (1.8, 1.8, 1.8), "ghost", "pearl", step=0.5)
    for sz in (-1, 1):
        k.shard(st, (-7.0, 28.4, 0.4 + sz * 1.6), (0, 1, sz * 0.3), 3.6, 0.8, mat="brass", tag="pearl_prong")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Dread Captain (elite)

def dread_captain():
    """The captain made a bargain with the deep and the deep kept its end. A greatcoat stiff with gold braid gone
    green, a tricorne heaped with plumes and the skulls of his officers, a beard of short tentacles that won't keep
    still, his left arm gone to a kraken's arm thick as a mast, and in his right the cutlass he hanged mutineers by."""
    k = X.Kit("dread_captain")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(13, 12.0, 8.6), (21, 12.0, 8.6)], "coat", "breeches")
    for i, (x, z, L) in enumerate(((-6.4, 2.4, 18), (6.4, 2.4, 18), (-5.4, -4.6, 20), (-1.8, -4.8, 21), (1.8, -4.8, 21), (5.4, -4.6, 20))):
        k.box(hips, C(x, 21 - L, z, 3.4, L - 1.0, 0.8), "coat", tag="greatcoat_skirt")
        k.box(hips, C(x, 21 - L, z + (0.45 if z > 0 else -0.45), 3.6, 1.0, 0.3), "gold", tag="skirt_braid")
    k.box(hips, C(0, 20.0, 0, 13.0, 2.2, 9.4), "leather", tag="belt")
    k.box(hips, C(0, 19.8, 4.8, 3.2, 2.8, 0.6), "gold", tag="buckle")
    k.box(hips, C(0, 20.3, 5.15, 1.2, 1.2, 0.3), "ghost", tag="buckle_stone")
    legs(k, hips, 20, 10.8, 3.6, "coat", "leather", knee_mat=None, lean=-6, bend=8, w=5.6)
    for side in (1, -1):
        k.box(k.parts["shin_" + ("l" if side > 0 else "r")], C(side * 3.6, 8.4, 0, 7.2, 3.0, 7.6), "leather", tag="boot_top")
    to = k.part("torso", (0, 21, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(21, 12.4, 8.6), (26, 14.0, 9.2), (31, 17.4, 10.0), (35, 18.0, 9.6)], "coat", "greatcoat")
    k.box(to, C(0, 22.0, 4.5, 6.0, 12.0, 0.6), "leather", tag="waistcoat")
    for sx in (-1, 1):
        k.box(to, C(sx * 4.6, 22.0, 4.8, 2.6, 13.0, 0.6), "coat", tag="lapel")
        for y in (24, 27, 30, 33):
            k.limb(to, (sx * 3.4, y, 5.2), (sx * 6.0, y, 5.2), 0.6, "gold", "braid")
            k.box(to, C(sx * 2.4, y - 0.3, 5.0, 0.9, 0.9, 0.3), "gold", tag="button")
    for sx in (-1, 1):
        k.blob(to, (sx * 9.0, 33.4, 0), (3.4, 2.4, 4.4), "coat", "shoulder", step=0.7)
        k.box(to, C(sx * 9.4, 35.0, 0, 5.4, 0.8, 5.4), "gold", tag="epaulette")
        for i in range(5):
            k.limb(to, (sx * (7.4 + i * 0.9), 35.0, 2.4), (sx * (7.4 + i * 0.9), 32.0, 2.6), 0.5, "gold", "fringe")
    k.box(to, C(0, 21.0, -4.8, 12.6, 14.0, 0.8), "coat", tag="coat_back")
    barnacles(k, to, (-3.4, 31.0, -5.3), 8, 2.8, seed=3)
    coral(k, to, (4.6, 33.0, -5.0), (0.3, 1, -0.5), 1.1)
    k.limb(to, (8.0, 34.6, 4.8), (-6.0, 21.6, 5.4), 1.8, "leather", "bandolier", d=0.6)
    hd = k.part("head", (0, 35.0, 0.6), (("x", -6),), "torso")
    k.box(hd, C(0, 35.4, 0.8, 6.4, 7.0, 6.2), "drowned", tag="face")
    k.box(hd, C(0, 39.6, 4.0, 6.6, 1.2, 1.0), "drowned", tag="brow")
    eyes(k, hd, 38.4, 4.0, 1.5, 1.4, h=0.8)
    k.box(hd, C(-1.5, 38.0, 4.1, 2.4, 2.0, 0.3), "dark", tag="eyepatch")
    k.limb(hd, (-3.2, 39.6, 3.4), (3.2, 38.0, 3.8), 0.4, "dark", "patch_strap")
    for i in range(9):                            # the beard: short tentacles, curling
        x = -2.6 + (i % 5) * 1.3
        y0 = 35.4 - (i // 5) * 1.0
        k.limb(hd, (x, y0, 4.0), (x * 1.1, y0 - 3.4, 4.6), 1.0, "squid", "tentacle_beard")
        k.limb(hd, (x * 1.1, y0 - 3.4, 4.6), (x * 1.2 + (0.8 if i % 2 else -0.8), y0 - 5.4, 4.0), 0.7, "squid", "tentacle_beard")
    tricorne(k, hd, (0, 40.6, 0.6), 1.3)
    for i, x in enumerate((-3.4, 0.0, 3.4)):      # the officers' skulls on the brim
        k.box(hd, C(x, 42.6, 4.6 - abs(x) * 0.3, 1.6, 1.6, 1.0), "bone", tag="hat_skull")
        k.box(hd, C(x, 43.2, 5.15 - abs(x) * 0.3, 1.0, 0.5, 0.3), "eye", tag="skull_eyes")
    for i in range(5):                            # plumes, green-black, up and back
        a = math.radians(-40 + i * 20)
        p0 = (math.sin(a) * 1.4, 44.0, -1.0)
        p1 = (math.sin(a) * 6.0, 48.0 + (2 - abs(i - 2)) * 1.0, -6.0)
        k.limb(hd, p0, p1, 1.8, "weed", "plume", d=0.7)
        k.limb(hd, p1, (math.sin(a) * 8.0, 45.0, -10.0), 1.4, "weed", "plume", d=0.6)
    arms(k, to, 9.4, 33, "coat", {1: ((("x", -20), ("z", -30)), (("x", -30),)), -1: ((("x", -46), ("z", 6)), (("x", -40),))}, glove="leather", w=4.0)
    # the kraken arm: the coat sleeve bursts at the elbow and a tentacle comes out, thick and coiling, suckers under
    fo = k.parts["fore_l"]
    for b in list(k.s.boxes):
        if b.part is fo or b.part is k.parts["hand_l"]:
            k.s.boxes.remove(b)
    k.box(fo, C(9.4, 22.0, 0, 6.0, 3.0, 6.0), "coat", tag="burst_sleeve")
    pts = [(9.4, 23.0, 0), (10.2, 16.0, 1.4), (11.6, 9.0, 3.6), (13.4, 4.0, 7.0), (12.4, 1.4, 11.0), (10.0, 3.4, 13.4)]
    for (a, b), w in zip(zip(pts, pts[1:]), (4.6, 4.0, 3.2, 2.4, 1.6)):
        k.limb(fo, a, b, w, "squid", "kraken_arm")
    for (a, b) in zip(pts[1:4], pts[2:5]):
        for t in (0.25, 0.75):
            q = tuple(a[j] + (b[j] - a[j]) * t for j in range(3))
            k.box(fo, C(q[0] - 1.4, q[1] - 0.5, q[2] + 1.2, 1.0, 1.0, 1.0), "barnacle", tag="sucker")
    k.box(fo, C(11.0, 11.0, 3.0, 1.2, 1.2, 1.2), "ghost", tag="kraken_glow")
    cl = held(k, "cutlass", "r", (-9.4, 13.4, 0.3), (("x", 76),))
    cutlass(k, cl, -9.4, 14.0, 0.3, L=18)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.15)
    return k.s, k.parts


MOBS = {
    "kraken_spawn": dict(make=kraken_spawn, rig="crawler", ent=(1.4, 1.4), stats=dict(hp=28, speed=0.3, dmg=6, armor=2, kb=0)),
    "drowned_corsair": dict(make=drowned_corsair, ent=(0.8, 2.7), stats=dict(hp=44, speed=0.31, dmg=8, armor=3, kb=0)),
    "harpooner": dict(make=harpooner, ent=(1.0, 2.9), stats=dict(hp=64, speed=0.22, dmg=10, armor=9, kb=0.4)),
    "anchor_hauler": dict(make=anchor_hauler, ent=(1.7, 4.0), stats=dict(hp=180, speed=0.19, dmg=18, armor=7, kb=1.0)),
    "tide_caller": dict(make=tide_caller, ent=(0.9, 2.7), stats=dict(hp=36, speed=0.23, dmg=7, armor=2, kb=0)),
    "dread_captain": dict(make=dread_captain, ent=(1.1, 3.4), stats=dict(hp=330, speed=0.25, dmg=15, armor=11, kb=0.6), key=True),
}
