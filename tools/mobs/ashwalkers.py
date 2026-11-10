"""The Ashwalkers: what walks on an ashfall night (Ashfall.java), and only then. When the fire-mountain wakes and the
ash comes down, the dead of the old burnings get up out of it: the ones the ash buried where they stood, the stone
that came down burning, and the one who walks ahead of them ringing them on. Ash-grey crust cracked over ember (the
mountain's orange, not the legion's teal), char, black iron; smoke coming off them all.

    ashwalker      skirm   a cast of someone the ash caught: hunched, its mouth open on the scream it died with,
                           cracked through to the ember inside, a guard's broken spear still through its chest
    cinder_hulk    brute   a hulk of fallen burning stone: a molten heart behind a cage of crust, a vent on its back
                           still smoking, fists like boulders
    ash_herald     caster  tall, robed in ash that falls off it as it walks, a black iron bell for a head with an
                           ember slit for a face, a crook with a censer of embers swinging from it

    python tools/monsterforge.py ashwalkers --preview ; python tools/mobsheet.py ashwalkers
"""
import vox2 as X
from vox2 import C, ramp
from _folk import lit, legs, arms, held

ASH = ramp("#1c1a19", "#2e2b29", "#45413e", "#5e5955", "#7a746e", "#968f88")
SMOKE = ramp("#2a2726", "#3c3836", "#524c49", "#6a6460", "#857e79")
CINDER = ramp("#08070a", "#110e10", "#1c1618", "#271e1e", "#342624", "#44302a")
CHAR = ramp("#060504", "#0e0b09", "#17120e", "#211913")
IRON = ramp("#0c0c0e", "#18181c", "#25252a", "#34343b", "#46464e")
CLOTH = ramp("#141210", "#211e1b", "#302c28", "#423d38", "#57514b")
EMBER = ramp("#3a0a02", "#7a1a04", "#c23a08", "#f06a14", "#ffa040", "#ffe0a0")


def shaders():
    return {
        "ash": X.surf(ASH, 0.5, 1.15, 0.2, 0.14, drip=(CINDER, 0.22), crust=(SMOKE, 0.3)),
        "smoke": X.surf(SMOKE, 0.5, 1.0, 0.24, 0.06),
        "cinder": X.surf(CINDER, 0.5, 1.25, 0.2, 0.2, crust=(ASH, 0.22)),
        "magma": X.veined(CINDER, EMBER, 0.26, 0.03),
        "char": X.surf(CHAR, 0.5, 1.1, 0.18, 0.1),
        "iron": X.surf(IRON, 0.58, 1.5, 0.08, 0.26, rust=(CINDER, 0.3, 0.5)),
        "cloth": X.surf(CLOTH, 0.5, 1.0, 0.22, 0.0, holes=True, drip=(ASH, 0.3)),
        "ember": X.glow(EMBER),
        "eye": X.glow(EMBER, 0.86, 0.12),
        "dark": X.dark(CINDER),
    }


GLOWS = {"ember", "eye"}


def smoke(k, part, at, n, L, up=(0, 1, -0.5), seed=1, spread=0.45):
    """ash and smoke streaming up off it"""
    k.cluster(part, at, n, L, L * 0.4, mat="smoke", seed=seed, spread=spread, up=up)


def crack(k, part, pts, w=0.5, face=None):
    """an ember fissure: a zigzag of glowing lines through the crust"""
    for a, b in zip(pts, pts[1:]):
        k.limb(part, a, b, w, "ember", "fissure", d=w * 0.8)


# ================================================================ the Ashwalker (skirmisher)

def ashwalker():
    """Someone the ash caught where they stood, a hundred years back, gone to a cast of themselves: grey crust over
    nothing but ember. Hunched, long in the arm, fingers fused into hooks, its head bowed and its mouth wide on the
    scream it died with; the crust split open down its chest and back with the mountain's fire showing through; a
    town guard's spear still through it from the night it came at the walls. Ash streams off its shoulders."""
    k = X.Kit("ashwalker")
    hips = k.part("hips", (0, 18, 0))
    k.stack(hips, 0, 0, [(15, 7.0, 5.0), (19, 8.6, 5.8)], "ash", "pelvis")
    legs(k, hips, 18, 10.0, 2.8, "ash", "ash", lean=-18, bend=22, w=3.8, cuff=False, splay=5)
    to = k.part("torso", (0, 18, 0), (("x", 42),), "hips")
    k.stack(to, 0, 0, [(18, 8.0, 5.6), (24, 9.6, 6.6), (29, 13.0, 7.6), (31.4, 12.0, 7.0)], "ash", "ribcage")
    # the crust split open down its front, ember in the gap
    crack(k, to, [(0.6, 30.2, 3.9), (-0.8, 27.6, 3.8), (0.9, 25.0, 3.6), (-0.4, 22.0, 3.3), (0.5, 19.4, 3.0)], 0.9)
    crack(k, to, [(-0.8, 27.6, 3.8), (-3.4, 26.4, 3.6), (-4.6, 24.0, 3.2)], 0.5)
    crack(k, to, [(0.9, 25.0, 3.6), (3.6, 23.8, 3.3)], 0.5)
    # its back: a hole broken through the crust over the spine, the ember core inside
    k.box(to, C(0, 26.6, -3.7, 4.0, 3.6, 0.6), "ember", tag="core")
    for x, y, w, h in ((-2.6, 26.6, 1.2, 4.4), (2.6, 26.6, 1.2, 4.4), (0, 29.0, 5.0, 1.0), (0, 24.2, 4.4, 1.0)):
        k.box(to, C(x, y, -4.1, w, h, 1.0), "ash", tag="hole_rim")
    # shoulders: crust heaped high, a V over the hunch
    for sx in (-1, 1):
        k.blob(to, (sx * 6.2, 31.0, -0.6), (3.0, 2.2, 3.4), "ash", "shoulder_crust", step=0.6)
        crack(k, to, [(sx * 5.0, 33.0, 1.4), (sx * 6.6, 32.0, 2.2), (sx * 7.8, 30.4, 2.0)], 0.4)
        smoke(k, to, (sx * 6.0, 32.4, -1.6), 3, 4.0, up=(sx * 0.2, 1, -0.7), seed=3 + sx)
    smoke(k, to, (0, 30.0, -3.6), 3, 5.0, up=(0, 1, -0.9), seed=7)
    for i, y in enumerate((21.0, 23.6, 30.6)):
        k.shard(to, (0, y, -3.0), (0, 0.4, -1), 2.6 + i * 0.4, 1.6, mat="ash", tag="back_crag")
    # the guard's spear, through it: in under the ribs at the front, out high at the back
    k.limb(to, (2.6, 19.0, 9.0), (-1.6, 32.0, -8.0), 0.9, "char", "spear_shaft")
    k.shard(to, (-1.6, 32.0, -8.0), (-0.32, 1.0, -1.32), 4.0, 1.8, mat="iron", tag="spear_head")
    k.box(to, C(2.6, 18.6, 9.4, 1.6, 1.2, 1.6), "char", tag="shaft_splinters")
    # the head, bowed: a cast of a face screaming
    hd = k.part("head", (0, 31.4, 1.0), (("x", -34),), "torso")
    k.blob(hd, (0, 35.4, 1.2), (3.0, 3.2, 3.2), "ash", "cranium", step=0.6)
    k.box(hd, C(0, 31.8, 2.2, 4.4, 2.4, 3.6), "ash", tag="cheeks")
    k.box(hd, C(0, 28.4, 2.8, 3.6, 2.4, 3.2), "ash", tag="jaw")
    k.box(hd, C(0, 29.8, 4.0, 2.8, 4.6, 0.6), "dark", tag="mouth")
    k.box(hd, C(0, 30.4, 3.9, 1.6, 2.2, 0.4), "ember", tag="throat_glow")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.25, 34.4, 3.95, 1.9, 2.0, 0.5), "dark", tag="socket")
        k.box(hd, C(sx * 1.2, 34.5, 4.0, 0.6, 0.6, 0.4), "eye", tag="eye")
        k.box(hd, C(sx * 1.3, 35.8, 3.9, 2.0, 0.6, 0.8), "ash", tag="brow")
    crack(k, hd, [(-1.8, 38.2, 1.4), (-0.4, 37.4, 3.0), (0.8, 38.4, 2.0), (1.6, 37.0, 3.2)], 0.4)
    # long arms hanging low, the hands fused into hooks
    arms(k, to, 7.0, 31, "ash", {1: ((("x", -30), ("z", -12)), (("x", -34),)), -1: ((("x", -6), ("z", 14)), (("x", -20),))},
         w=3.0, long=1.32)
    for side, nm in ((1, "l"), (-1, "r")):
        hn = k.parts["hand_" + nm]
        y = 31 - 8 * 1.32 - 7.6 * 1.32
        for i, dx in enumerate((-1.0, 0.0, 1.0)):
            k.shard(hn, (side * 7.0 + dx, y - 3.8, 1.0), (dx * 0.2, -1, 0.7), 4.2 - abs(dx) * 0.6, 1.0, mat="char", tag="hook")
        crack(k, k.parts["fore_" + nm], [(side * 7.0, y + 6.0, 1.3), (side * 7.6, y + 3.6, 1.5), (side * 7.0, y + 1.2, 1.4)], 0.35)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Cinder Hulk (brute)

def cinder_hulk():
    """Stone that came down out of the sky burning, and got up: a hulk of black cinder crust, its heart a ball of
    molten rock behind a cage of crust you can see it beat through, a vent split open across its back still
    smoking from the fall, magma dripping off its shoulders, fists like the boulders it came down as."""
    k = X.Kit("cinder_hulk")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(12, 15, 11), (20, 17, 12)], "cinder", "hips")
    legs(k, hips, 19, 10.0, 5.0, "cinder", "cinder", knee_mat="char", lean=-4, bend=8, w=7.4, cuff=False, splay=4)
    to = k.part("torso", (0, 20, 0), (("x", 16),), "hips")
    k.stack(to, 0, 0, [(19, 15, 11), (26, 21, 14), (33, 27, 16), (36, 25, 15)], "cinder", "chest")
    # the heart: molten, behind bars of crust
    k.blob(to, (0, 28.4, 6.0), (4.6, 4.4, 2.6), "ember", "heart", step=0.6)
    for x in (-3.4, -1.1, 1.1, 3.4):
        k.box(to, C(x, 28.4, 8.0, 1.4, 10.0, 1.6), "cinder", tag="rib_bar")
    k.box(to, C(0, 33.0, 7.6, 11.0, 1.6, 2.0), "cinder", tag="cage_top")
    k.box(to, C(0, 23.8, 7.2, 9.0, 1.4, 2.0), "cinder", tag="cage_foot")
    crack(k, to, [(-9.0, 22.0, 6.0), (-6.4, 25.6, 7.0), (-7.6, 30.0, 7.4)], 0.6)
    crack(k, to, [(9.0, 22.6, 6.0), (7.0, 26.0, 7.0), (8.8, 30.6, 7.2)], 0.6)
    # the vent across its back: a crater rim of crust round a pool of fire, smoke pouring off it
    k.blob(to, (0, 32.0, -7.4), (7.0, 3.0, 3.0), "cinder", "vent_rim", step=0.6)
    k.box(to, C(0, 32.6, -9.4, 9.0, 2.2, 1.0), "ember", tag="vent_fire")
    for x in (-5.0, -1.6, 1.6, 5.0):
        k.shard(to, (x, 33.0, -8.4), (x * 0.05, 1, -0.4), 4.0 + abs(x) * 0.2, 2.2, mat="cinder", tag="vent_crag")
    smoke(k, to, (0, 34.0, -9.6), 5, 9.0, up=(0, 1, -0.5), seed=5, spread=0.35)
    # shoulders: boulders, cracked, dripping
    for sx in (-1, 1):
        k.blob(to, (sx * 13.4, 33.4, 0), (5.4, 4.8, 6.0), "magma", "shoulder", step=0.7)
        k.shard(to, (sx * 14.6, 36.6, -1.0), (sx * 0.4, 1, -0.3), 5.0, 2.8, mat="cinder", tag="shoulder_spike")
        crack(k, to, [(sx * 10.0, 36.6, 3.0), (sx * 13.0, 35.0, 5.0), (sx * 16.4, 33.0, 4.0)], 0.6)
        for z in (-2.0, 2.4):
            k.shard(to, (sx * 16.8, 30.0, z), (0, -1, 0), 2.6, 1.0, mat="ember", tag="magma_drip")
    # the head, sunk low between the shoulders: a slab brow, an ember slit, a jaw of broken rock
    hd = k.part("head", (0, 35.4, 3.0), (("x", -14),), "torso")
    for sx in (-1, 1):
        k.shard(hd, (sx * 4.0, 39.8, 4.0), (sx * 0.7, 1, -0.4), 4.6, 2.2, mat="cinder", tag="horn_crag")
    k.box(hd, C(0, 35.8, 4.4, 9.0, 6.0, 8.0), "cinder", tag="skull")
    k.box(hd, C(0, 39.4, 6.0, 10.4, 2.0, 7.6), "cinder", tag="brow_slab")
    k.box(hd, C(0, 37.6, 8.5, 6.4, 1.0, 0.5), "eye", tag="eye_slit")
    k.box(hd, C(0, 33.4, 6.4, 7.6, 2.6, 6.4), "char", tag="jaw")
    for x in (-2.6, -0.8, 1.0, 2.8):
        k.shard(hd, (x, 34.8, 9.4), (0, 1, 0.2), 1.6, 1.0, mat="cinder", tag="fang")
    k.box(hd, C(0, 34.8, 8.9, 5.0, 1.0, 0.4), "ember", tag="mouth_glow")
    # arms like pillars, fists of boulder
    arms(k, to, 13.4, 31, "cinder", {1: ((("x", -16), ("z", -16)), (("x", -30),)), -1: ((("x", -10), ("z", 16)), (("x", -24),))},
         w=6.8, long=1.5)
    for side, nm in ((1, "l"), (-1, "r")):
        hn = k.parts["hand_" + nm]
        y = 31 - 8 * 1.5 - 7.6 * 1.5
        k.blob(hn, (side * 13.4, y - 3.4, 0.6), (5.4, 4.8, 5.4), "magma", "fist", step=0.7)
        crack(k, hn, [(side * 11.2, y - 1.6, 4.6), (side * 13.4, y - 3.8, 5.0), (side * 15.4, y - 2.2, 4.4)], 0.5)
        for dz in (-1.6, 1.6):
            k.shard(hn, (side * (13.4 + 3.6), y - 2.6, dz), (side, 0.3, 0), 2.4, 1.6, mat="cinder", tag="knuckle_crag")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Ash Herald (caster)

def ash_herald():
    """The one who walks ahead of them: tall and thin under a robe of ash that falls away off its hem as it walks
    and never runs out, a head that is a black iron bell gone cracked in the heat, a slit down its face with the
    mountain's fire in it and a crown of iron spikes over; a shepherd's crook of black iron, and from it on a chain
    a censer of embers that it swings to throw the fire. Chains and little bells round its waist."""
    k = X.Kit("ash_herald")
    hips = k.part("hips", (0, 22, 0))
    legs(k, hips, 22, 12.0, 2.6, "char", "char", lean=-4, bend=6, w=3.2, cuff=False, splay=2)
    # the robe: hips to the ground, flaring, hem torn and falling into ash
    k.stack(hips, 0, 0, [(1.6, 15.0, 12.0), (8, 12.0, 9.4), (16, 9.6, 7.2), (22.6, 9.0, 6.6)], "cloth", "robe")
    for i in range(9):
        x = -6.4 + i * 1.6
        k.shard(hips, (x, 1.8, 4.0 + (i % 3) * 0.6), (x * 0.06, -1, 0.3), 1.6 + (i % 2), 1.2, mat="smoke", tag="falling_hem")
        k.shard(hips, (x, 1.8, -4.6), (x * 0.06, -1, -0.3), 1.4 + (i % 3) * 0.4, 1.2, mat="smoke", tag="falling_hem")
    k.box(hips, C(0, 21.0, 0, 10.4, 1.4, 7.6), "iron", tag="belt_chain")
    for x, z in ((-4.0, 3.6), (-1.2, 4.0), (2.4, 3.8), (4.6, 2.0)):
        k.limb(hips, (x, 20.6, z), (x, 17.6, z + 0.2), 0.6, "iron", "bell_chain")
        k.blob(hips, (x, 16.8, z + 0.2), (0.9, 0.9, 0.9), "iron", "little_bell", step=0.4)
    to = k.part("torso", (0, 22, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(22, 9.0, 6.4), (30, 10.0, 6.8), (35, 13.6, 7.6)], "cloth", "robe_top")
    # a high collar of rags and a mantle over the shoulders, ash pouring up off it
    k.stack(to, 0, -0.6, [(33, 16.0, 9.6), (36.4, 17.0, 10.4), (38.6, 12.0, 8.6)], "cloth", "mantle")
    for sx in (-1, 1):
        k.shard(to, (sx * 7.4, 37.6, -2.0), (sx * 0.5, 1, -0.2), 3.4, 1.8, mat="cloth", tag="collar_point")
    smoke(k, to, (0, 38.0, -3.6), 5, 6.0, up=(0, 1, -0.8), seed=11, spread=0.55)
    # the bell for a head, cracked, an ember slit; a crown of iron spikes
    hd = k.part("head", (0, 38.4, 0.4), (("x", -6),), "torso")
    k.stack(hd, 0, 0.4, [(37.8, 8.2, 8.2), (40.0, 7.6, 7.6), (43.0, 6.6, 6.6), (45.4, 5.0, 5.0)], "iron", "bell")
    k.box(hd, C(0, 38.2, 0.4, 9.2, 1.0, 9.2), "iron", tag="bell_lip")
    k.box(hd, C(0, 41.2, 4.6, 1.0, 5.6, 0.5), "eye", tag="face_slit")
    crack(k, hd, [(-2.4, 44.6, 3.2), (-1.4, 42.4, 3.9), (-2.8, 40.2, 4.0)], 0.35)
    for i in range(7):
        import math
        a = -1.2 + i * 0.4
        x, z = math.sin(a) * 3.0, 0.4 + math.cos(a) * 3.0
        k.shard(hd, (x, 45.0, z - 1.0), (x * 0.12, 1, (z - 0.4) * 0.12), 3.4 - abs(i - 3) * 0.5, 0.9, mat="iron", tag="crown_spike")
    k.box(hd, C(0, 45.0, 0.4, 1.6, 2.4, 1.6), "iron", tag="bell_crown_loop")
    # arms in long sleeves; the right holds the crook, the left an ember in its palm
    arms(k, to, 7.4, 35, "char", {1: ((("x", -36), ("z", -10)), (("x", -40),)), -1: ((("x", -14), ("z", 6)), (("x", -40),))},
         sleeve="cloth", w=3.0, long=1.1)
    y_hand = 35 - 8 * 1.1 - 7.6 * 1.1
    k.shard(k.parts["hand_l"], (7.4, y_hand - 3.4, 2.4), (0, 1, 0.2), 2.2, 1.6, mat="ember", tag="palm_ember")
    cr = held(k, "crook", "r", (-7.4, y_hand - 1.4, 0.4), (("x", 80),))
    k.limb(cr, (-7.4, y_hand - 12.0, 0.4), (-7.4, y_hand + 22.0, 0.4), 1.0, "iron", "crook_staff")
    hook = [(-7.4, y_hand + 22.0, 0.4), (-7.4, y_hand + 25.0, 1.6), (-7.4, y_hand + 26.0, 4.2), (-7.4, y_hand + 24.4, 6.6), (-7.4, y_hand + 21.6, 7.0)]
    for a, b in zip(hook, hook[1:]):
        k.limb(cr, a, b, 1.0, "iron", "crook_hook")
    # the censer: on a chain from the hook's end, an iron cage of embers, smoking
    k.chain(cr, (-7.4, y_hand + 21.6, 7.0), (-7.4, y_hand + 15.0, 7.0), 4, mat="iron", tag="censer_chain", w=0.9)
    cy = y_hand + 13.2
    k.blob(cr, (-7.4, cy, 7.0), (1.6, 1.6, 1.6), "ember", "censer_fire", step=0.4)
    for dx, dz in ((-1.8, 0), (1.8, 0), (0, -1.8), (0, 1.8)):
        k.box(cr, C(-7.4 + dx, cy - 2.0, 7.0 + dz, 0.5, 4.0, 0.5), "iron", tag="censer_bar")
    k.box(cr, C(-7.4, cy - 2.4, 7.0, 4.0, 0.6, 4.0), "iron", tag="censer_base")
    k.box(cr, C(-7.4, cy + 1.8, 7.0, 3.0, 0.6, 3.0), "iron", tag="censer_lid")
    smoke(k, cr, (-7.4, cy + 2.2, 7.0), 3, 3.6, up=(0, 1, -0.3), seed=13, spread=0.4)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


MOBS = {
    "ashwalker": dict(make=ashwalker, ent=(0.8, 2.6), stats=dict(hp=40, speed=0.31, dmg=8, armor=3, kb=0)),
    "cinder_hulk": dict(make=cinder_hulk, ent=(1.9, 4.0), stats=dict(hp=210, speed=0.18, dmg=18, armor=10, kb=1.0)),
    "ash_herald": dict(make=ash_herald, ent=(0.9, 3.2), stats=dict(hp=52, speed=0.22, dmg=9, armor=4, kb=0)),
}
