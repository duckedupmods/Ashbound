"""The Hollow Circus, the Mirefen Coven, the Sandsunk Tomb, the Fallen Titan, the Jade Monastery and the Storm Bastion
(see armorsets.py for the units and the fit rules)."""
import math

from armorsets import BRASS, C, IRON, SIDES, design, ramp
from armorsets_a import BLACK, HEMP, OAK
from armorsets_b import BONE, GILT, HIDE, PALE
from armorsets_c import STEEL

BIGTOP = ramp("#2a0610", "#4a0c1c", "#6e142a", "#94203a", "#bc3050", "#e0586a")
CREAM = ramp("#7a6a4c", "#a08e68", "#c4b48a", "#e0d4ac", "#f2eace")
TENTGLOW = ramp("#a02808", "#d44c0c", "#f88018", "#ffb82c", "#ffe476", "#fff8d0")
JOKE = ramp("#3a0a4a", "#5c1270", "#8220a0", "#ac40cc", "#d484ec", "#f6d4ff")
MIRE = ramp("#10180c", "#1c2a14", "#2c401c", "#3e5826", "#547432")
REED = ramp("#3a3414", "#5a5220", "#7c7230", "#a09844", "#c4bc60")
HEXGLOW = ramp("#1e4a1a", "#2e7c22", "#4cb030", "#88dc48", "#c8f47c", "#f4ffd0")
FROG = ramp("#1a3a12", "#2a5a1a", "#3e7e24", "#58a230", "#82c448", "#b8e470")
PEAT = ramp("#140e08", "#241a10", "#382a1a", "#4e3c26", "#685236")
LINEN = ramp("#6e6048", "#90806a", "#b4a488", "#d0c4a8", "#e8dec8")
SAND = ramp("#6a4a1e", "#8e682c", "#b48a40", "#d4ae5c", "#ecd084")
LAPIS = ramp("#0c1a4a", "#142a70", "#1e3e9c", "#3058c4", "#5880e4")
SUN = ramp("#a85808", "#dc8810", "#f8b82c", "#ffdc60", "#fff29c", "#fffce0")
FLESH = ramp("#3a0e12", "#5e1a1c", "#86282a", "#ac4040", "#d06c60", "#ec9c88")
BILE = ramp("#3a4408", "#5a6a0c", "#849a14", "#b0c82a", "#d8e860", "#f6ffb0")
MARROW = ramp("#a02050", "#d03868", "#f0647c", "#ff9c94", "#ffd0b0", "#fff4e0")
JADE = ramp("#0c3a2a", "#145a40", "#1e7e58", "#2ea474", "#58cc98", "#a0f0c4")
JADEGLOW = ramp("#0e6a4a", "#169a68", "#2cc888", "#64eaac", "#b0f8d4", "#eafff4")
LACQUER = ramp("#0e0606", "#1c0c0c", "#301414", "#481c1c", "#642828")
VERMILION = ramp("#5a1006", "#8a1c0a", "#bc2e12", "#e04a1e", "#f47a3c")
STORM = ramp("#141a34", "#1e2a50", "#2c3c70", "#405494", "#5c74b8")
BOLT = ramp("#3a4ad0", "#5c78f0", "#8cb0ff", "#b8dcff", "#e4f8ff", "#ffffff")
COPPER = ramp("#3e1c0c", "#6a3214", "#9c5022", "#c87838", "#e8a860", "#f8d09c")
GRANITE = ramp("#20222a", "#343842", "#4c525e", "#6a727e", "#8e96a0")


# ---------------------------------------------------------------- the Hollow Circus

@design(cloth=BIGTOP, wrap=CREAM, leather=HIDE, dark=BLACK, acc=GILT, gold=GILT, wood=OAK, blade=STEEL, no_skirt=True, fire=TENTGLOW, hot=TENTGLOW)
def fireeater(k):
    """the sideshow's main draw: a striped turban with a flame stood in it, bare of everything but a gold harness, a wheel of burning torches behind him"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.0, 7.0, 9.2), "dark", tag="head")
    a(h, C(0, 30.0, 0, 11.4, 3.0, 11.4), "cloth", tag="turban")
    a(h, C(0, 32.8, 0, 9.4, 2.2, 9.4), "wrap", tag="turban")
    a(h, C(0, 34.8, 0, 6.4, 1.6, 6.4), "cloth", tag="turban")
    a(h, C(0, 30.4, 5.5, 3.2, 3.2, 0.7), "acc", tag="turban_brooch")
    k.tongue(h, 0, 36.4, 0, 7.0, 3.4)
    a(h, C(0, 24.0, 4.45, 7.0, 4.6, 0.4), "wrap", tag="veil")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 28.8, 4.75, 1.2, 0.7, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.6), "wrap", tag="body_paint")
    for r in (33, -33):
        a(c, C(0, 12.0, 2.45, 1.3, 13.0, 0.5), "acc", tag="harness", rots=(("z", r),), pivot=(0, 18.4, 2.45))
    a(c, C(0, 16.6, 2.75, 3.4, 3.4, 0.5), "acc", tag="sun_plate")
    k.fire(c, C(0, 17.4, 3.0, 1.8, 1.8, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 2.2, 5.4), "cloth", tag="sash")
    a(c, C(3.0, 5.4, 2.9, 2.0, 7.0, 0.6), "cloth", tag="sash_end")
    for t in range(9):
        a(b, C(0, 16.0, -3.6, 1.0, 12.0, 1.0), "wood", tag="torch_spoke", rots=(("z", -100 + t * 25),), pivot=(0, 16.0, -3.6))
        a(b, C(0, 28.0, -3.6, 1.8, 2.0, 1.8), "dark", tag="torch_head", rots=(("z", -100 + t * 25),), pivot=(0, 16.0, -3.6))
        a(b, C(0, 30.0, -3.6, 1.6, 3.0, 1.6), "glow", tag="torch_flame", rots=(("z", -100 + t * 25),), pivot=(0, 16.0, -3.6))
    a(b, C(0, 13.8, -3.4, 4.6, 4.6, 1.0), "acc", tag="wheel_hub")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "wrap", tag="arm")
        k.elbow(s, "wrap")
        a(p, C(x, 11.4, 0, 5.2, 5.6, 5.2), "wrap", tag="arm")
        for y in (12.6, 14.2):
            a(p, C(x, y, 0, 5.6, 0.7, 5.6), "acc", tag="bracelet")
        a(p, C(x, 19.6, 0, 5.4, 0.8, 5.4), "acc", tag="armband")
        k.tongue(k.shoulder(s), x + s * 0.4, 23.0, 0, 3.6, 2.6)
        a(k.shoulder(s), C(x + s * 0.4, 21.6, 0, 5.4, 1.5, 5.4), "dark", tag="fire_pan")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 4.4, 0, 5.6, 7.6, 5.6), "cloth", tag="baggy_trouser")
        a(p, C(x, 3.0, 0, 4.6, 1.6, 4.6), "acc", tag="ankle_band")
        a(p, C(x, 5.6, 2.85, 1.0, 6.0, 0.3), "wrap", tag="trouser_stripe")
    k.boots("wrap", h=2.2, w=4.8, toe="acc", toe_d=3.6)


@design(cloth=BIGTOP, cloth2=ramp("#0c0a10", "#1a161e", "#2a2430", "#3c3442"), wrap=CREAM, dark=BLACK, acc=GILT, gold=GILT, leather=HIDE, blade=PALE, gem=JOKE, fire=JOKE, hot=JOKE)
def motley(k):
    """the Ringmaster's fool: half red and half black, a three-horned cap with its bells on, a porcelain smile, a slapstick on the back and curled shoes"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(-2.4, 24.0, -0.2, 4.6, 8.0, 9.2), "cloth", tag="hood")
    a(h, C(2.4, 24.0, -0.2, 4.6, 8.0, 9.2), "cloth2", tag="hood")
    a(h, C(0, 24.4, 4.4, 7.4, 6.6, 0.7), "blade", tag="porcelain_mask")
    a(h, C(0, 25.4, 4.8, 5.0, 0.6, 0.3), "void", tag="smile")
    for s in SIDES:
        a(h, C(s * 2.4, 26.0, 4.8, 0.7, 0.8, 0.3), "void", tag="smile")
        a(h, C(s * 2.0, 28.2, 4.8, 1.4, 1.2, 0.3), "void", tag="eye")
        k.fire(h, C(s * 2.0, 28.4, 4.9, 0.7, 0.7, 0.3))
        for y in (29.6, 30.0):
            a(h, C(s * 2.0, y + 0.8, 4.8, 0.5, 0.3, 0.3), "dark", tag="eye_paint")
    for s, m in ((-1, "cloth"), (1, "cloth2")):
        a(h, C(s * 5.0, 31.4, -0.2, 5.0, 3.2, 3.4), m, tag="cap_horn")
    k.horn(h, -6.4, 31.6, -0.2, [(3.4, 50, 3.2), (3.0, 86, 2.4), (3.0, 130, 1.8), (2.4, 166, 1.2)], "cloth")
    k.horn(h, 6.4, 31.6, -0.2, [(3.4, -50, 3.2), (3.0, -86, 2.4), (3.0, -130, 1.8), (2.4, -166, 1.2)], "cloth2")
    k.horn(h, 0, 32.0, -1.0, [(3.0, 0, 3.4), (3.0, 12, 2.4), (2.8, 30, 1.8), (2.4, 58, 1.2)], "wrap")
    for x, y, z in ((-13.2, 30.2, -0.2), (13.2, 30.2, -0.2), (-4.0, 42.0, -1.0)):
        a(h, C(x, y, z, 1.8, 1.8, 1.8), "acc", tag="bell")
    a(h, C(0, 22.2, 0, 11.4, 2.2, 11.4), "wrap", tag="ruff")
    a(c, C(-2.2, 12.2, 0, 4.4, 11.8, 5.0), "cloth", tag="half_red")
    a(c, C(2.2, 12.2, 0, 4.4, 11.8, 5.0), "cloth2", tag="half_black")
    for x, y, m in ((-2.4, 15.2, "cloth2"), (2.4, 15.2, "cloth"), (-2.4, 19.8, "cloth2"), (2.4, 19.8, "cloth")):
        a(c, C(x, y, 2.65, 2.4, 2.4, 0.4), m, tag="diamond", rots=(("z", 45),), pivot=(x, y + 1.2, 2.65))
    for y in (14.0, 17.2, 20.4):
        a(c, C(0, y, 2.85, 1.2, 1.2, 0.5), "acc", tag="pompom")
    a(c, C(0, 12.2, 0, 8.7, 1.1, 5.6), "acc", tag="belt")
    a(b, C(0, 8.0, -3.4, 1.2, 12.0, 1.0), "leather", tag="slapstick_grip", rots=(("z", 26),), pivot=(0, 18, -3.4))
    a(b, C(0, 19.0, -3.4, 3.2, 14.0, 0.5), "wrap", tag="slapstick", rots=(("z", 26),), pivot=(0, 18, -3.4))
    a(b, C(0, 19.0, -3.9, 3.2, 14.0, 0.5), "cloth", tag="slapstick", rots=(("z", 26),), pivot=(0, 18, -3.4))
    for s, m, n in ((1, "cloth2", "cloth"), (-1, "cloth", "cloth2")):
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), m, tag="sleeve")
        k.elbow(s, m)
        a(p, C(x, 11.2, 0, 5.2, 5.8, 5.2), n, tag="sleeve")
        a(p, C(x, 16.6, 0, 5.8, 1.2, 5.8), "wrap", tag="ruffle")
        q = k.shoulder(s)
        for t in (-2.6, 0, 2.6):
            k.spike(q, x + s * 0.6, 22.6, t, -4.0, 2.4, n, tag="dag")
        a(q, C(x + s * 0.2, 21.8, 0, 5.8, 1.8, 6.0), m, tag="dag_top")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 7.0, 0, 4.6, 5.0, 4.6), m, tag="leg")
        a(p, C(y, 2.4, 0, 4.6, 4.8, 4.6), n, tag="leg")
        p = k.boot(s)
        a(p, C(y, 0, 0.2, 4.8, 2.6, 5.2), m, tag="boot")
        a(p, C(y, 0, 0.4, 5.0, 0.6, 6.2), "void", tag="sole")
        a(p, C(y, 0.8, 3.0, 3.0, 1.6, 2.6), m, tag="toe")
        a(p, C(y, 1.6, 4.6, 2.0, 2.0, 1.6), m, tag="toe_curl")
        a(p, C(y, 3.0, 5.0, 1.4, 1.4, 1.4), "acc", tag="bell")


@design(cloth=BIGTOP, cloth2=ramp("#0c0a10", "#1a161e", "#2a2430", "#3c3442"), wrap=CREAM, leather=HIDE, dark=BLACK, acc=GILT, gold=GILT, mail=STEEL, wood=OAK, blade=STEEL, fire=TENTGLOW, hot=TENTGLOW)
def ringhand(k):
    """the master of the ring's right hand: a tall striped top hat, a great waxed moustache, a tailcoat with brass buttons, the whip coiled at his hip and a tent stake in his belt"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.0, 7.0, 9.2), "cloth2", tag="head")
    a(h, C(0, 31.0, 0, 13.4, 0.9, 13.4), "cloth2", tag="hat_brim")
    a(h, C(0, 31.8, 0, 8.4, 9.0, 8.4), "cloth", tag="top_hat")
    for x in (-2.8, 0, 2.8):
        a(h, C(x, 33.0, 4.25, 1.2, 7.8, 0.3), "wrap", tag="hat_stripe")
    a(h, C(0, 31.8, 0, 8.7, 1.2, 8.7), "acc", tag="hat_band")
    a(h, C(0, 40.8, 0, 9.0, 0.7, 9.0), "cloth2", tag="hat_top")
    a(h, C(0, 25.0, 4.5, 3.6, 1.0, 0.8), "dark", tag="moustache")
    for s in SIDES:
        a(h, C(s * 3.4, 25.0, 4.5, 3.6, 0.9, 0.8), "dark", tag="moustache", rots=(("z", s * 20),), pivot=(s * 2, 25.4, 4.5))
        a(h, C(s * 5.4, 26.0, 4.5, 1.2, 1.2, 0.6), "dark", tag="moustache_curl")
        k.fire(h, C(s * 2.0, 27.8, 4.75, 1.0, 0.7, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="tailcoat")
    a(c, C(0, 13.0, 2.75, 3.6, 11.0, 0.5), "wrap", tag="shirt_front")
    a(c, C(0, 21.6, 3.05, 2.8, 1.2, 0.4), "cloth2", tag="bow_tie")
    for s in SIDES:
        a(c, C(s * 3.2, 18.4, 2.85, 2.2, 5.4, 0.5), "cloth2", tag="lapel")
        for y in (14.0, 16.4):
            a(c, C(s * 2.6, y, 2.95, 0.9, 0.9, 0.4), "acc", tag="button")
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.8), "acc", tag="belt")
    a(c, C(3.4, 9.2, 2.95, 3.2, 3.6, 1.2), "leather", tag="whip_coil")
    a(c, C(3.4, 10.2, 2.95, 1.6, 1.6, 1.3), "void", tag="whip_coil_hole")
    a(c, C(-3.8, 3.0, 3.2, 1.2, 10.0, 1.2), "wood", tag="tent_stake")
    a(c, C(-3.8, 13.0, 3.2, 1.8, 0.9, 1.8), "blade", tag="stake_cap")
    for s in SIDES:
        a(b, C(s * 2.0, 3.0, -3.4, 3.4, 19.0, 0.7), "cloth", tag="tail", rots=(("x", 6), ("z", -s * 5)), pivot=(s * 2, 22, -3.4))
        a(b, C(s * 2.0, 21.0, -3.9, 1.0, 1.0, 0.4), "acc", tag="button")
    k.arms("cloth", "cloth", cuff="cloth2", w=5.2)
    for s in SIDES:
        q = k.shoulder(s)
        a(q, C(s * 6.3, 21.0, 0, 5.8, 2.0, 6.0), "cloth", tag="epaulette")
        for t in (-2.4, -0.8, 0.8, 2.4):
            a(q, C(s * 9.2, 19.4, t, 0.5, 2.2, 0.5), "acc", tag="fringe")
        a(k.arm(s), C(s * 6.0, 10.8, 0, 5.4, 0.8, 5.4), "wrap", tag="white_glove")
    a(k.arm(1), C(6.0, 11.4, 0, 5.4, 3.0, 5.4), "wrap", tag="white_glove")
    a(k.arm(-1), C(-6.0, 11.4, 0, 5.4, 3.0, 5.4), "wrap", tag="white_glove")
    k.legs("cloth2", w=4.6)
    for s in SIDES:
        a(k.leg(s), C(s * 3.9, 2.4, 0, 0.5, 9.6, 1.2), "acc", tag="trouser_stripe")
    k.boots("cloth2", h=5.2, w=5.0, cuff="acc", toe="dark", toe_d=2.2)


@design(blade=ramp("#1a1a1e", "#2c2c32", "#44444c", "#5e5e68", "#84848e", "#b8b8c0"), wrap=CREAM, cloth=BIGTOP, dark=BLACK, acc=GILT, gold=GILT, leather=HIDE, mail=STEEL, fire=TENTGLOW, hot=TENTGLOW)
def ringiron(k):
    """the circus strongman in a suit of iron: striped leotard, a walrus moustache forged on the visor, the ring itself hung around him and a two-ball barbell on the shoulders"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.2, 0, 10.0, 8.8, 10.0), "blade", tag="iron_head")
    a(h, C(0, 32.0, 0, 7.0, 0.8, 7.0), "dark", tag="bald_top")
    a(h, C(0, 26.8, 4.95, 7.8, 1.0, 0.5), "void", tag="slit")
    k.fire(h, C(0, 27.0, 5.15, 6.2, 0.6, 0.3))
    a(h, C(0, 24.4, 5.0, 8.8, 1.6, 0.9), "dark", tag="iron_moustache")
    for s in SIDES:
        a(h, C(s * 5.0, 23.6, 5.0, 1.6, 2.8, 0.9), "dark", tag="moustache_drop")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 7.0), "cloth", tag="leotard")
    for y in (13.6, 16.4, 19.2, 22.0):
        a(c, C(0, y, 0, 8.7, 1.4, 7.2), "wrap", tag="leotard_stripe")
    a(c, C(0, 13.0, 3.7, 4.8, 3.6, 0.6), "acc", tag="champion_belt")
    a(c, C(0, 12.2, 0, 8.7, 1.8, 7.6), "dark", tag="belt")
    k.fire(c, C(0, 13.8, 4.1, 2.0, 2.0, 0.3))
    for t in range(16):
        r = math.radians(t * 22.5)
        x, z = math.sin(r) * 11.0, math.cos(r) * 11.0
        a(b, C(x, 13.4, z - 0.0, 4.6, 1.8, 1.8), "acc" if t % 4 == 0 else "blade", tag="hoop", rots=(("y", t * 22.5),), pivot=(x, 13.4, z))
    a(b, C(0, 25.0, -3.6, 28.0, 1.4, 1.4), "blade", tag="bar")
    a(b, C(0, 22.8, -3.4, 8.0, 2.4, 1.6), "blade", tag="bar_saddle")
    for s in SIDES:
        a(b, C(s * 15.0, 21.4, -3.6, 8.4, 8.4, 8.4), "dark", tag="bell_ball")
        a(b, C(s * 15.0, 22.6, -3.6, 9.0, 6.0, 9.0), "dark", tag="bell_ball")
        a(b, C(s * 15.0, 25.0, 1.0, 3.0, 1.4, 0.4), "acc", tag="bell_weight")
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.6, 3.4, 5.6), "cloth", tag="bulging_arm")
        k.elbow(s, "wrap")
        a(p, C(x, 11.0, 0, 6.2, 5.8, 6.2), "blade", tag="iron_forearm")
        a(p, C(x, 16.2, 0, 6.6, 1.0, 6.6), "acc", tag="cuff")
        a(k.shoulder(s), C(x + s * 0.4, 21.0, 0, 7.2, 3.2, 7.2), "blade", tag="iron_deltoid")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 2.4, 0, 5.2, 9.6, 5.2), "blade", tag="iron_leg")
        a(p, C(x, 7.0, 0, 5.5, 5.0, 5.5), "cloth", tag="shorts")
        a(p, C(x, 7.0, 0, 5.7, 1.0, 5.7), "wrap", tag="shorts_hem")
    k.boots("blade", h=3.8, w=5.4, cuff="acc", sole="dark")


# ---------------------------------------------------------------- the Mirefen Coven

@design(cloth=MIRE, cloth2=REED, wrap=REED, wood=PEAT, dark=BLACK, acc=ramp("#20242a", "#383e46", "#586068", "#828c94"), bone=BONE, leather=HIDE, blade=ramp("#101214", "#1e2226", "#30363c", "#464e56"), fire=HEXGLOW, hot=HEXGLOW)
def hexweave(k):
    """a marsh hag: a tall cone of bound reeds for a hat, stick poppets strung from her belt, and the family cauldron carried on her back with something still boiling in it"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.2, 7.2, 9.4), "cloth", tag="hood")
    a(h, C(0, 28.0, 4.5, 6.8, 2.6, 0.4), "void", tag="hood_dark")
    for s in SIDES:
        k.fire(h, C(s * 1.8, 28.8, 4.7, 1.0, 0.7, 0.3))
    a(h, C(0, 24.6, 4.6, 1.4, 3.6, 1.6), "bone", tag="hook_nose")
    for w, y in ((13.0, 30.8), (10.2, 32.0), (8.0, 34.0), (6.0, 36.0), (4.2, 38.0), (2.6, 40.0)):
        a(h, C(0, y, 0, w, 2.2, w), "wrap", tag="reed_cone")
    a(h, C(0, 33.6, 0, 8.6, 0.6, 8.6), "dark", tag="cone_tie")
    a(h, C(0, 38.4, 0, 4.6, 0.6, 4.6), "dark", tag="cone_tie")
    for x in (-5.4, 5.2):
        k.tail(h, x, 30.8, 3.6, 5.0, 1.0, "cloth2", tag="reed_fringe")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 19.0, 0, 8.7, 5.0, 6.2), "wrap", tag="reed_shawl")
    for x in (-3.4, -1.4, 0.6, 2.6):
        k.tail(c, x, 19.2, 3.2, 2.8 + (x % 2), 1.0, "wrap", tag="reed_fringe")
    a(c, C(0, 12.2, 0, 8.7, 1.2, 5.8), "dark", tag="belt")
    for x, ln in ((-3.0, 3.0), (0, 1.8), (3.0, 3.6)):
        a(c, C(x, 12.2 - ln, 3.1, 0.4, ln, 0.4), "wrap", tag="string")
        a(c, C(x, 12.2 - ln - 2.4, 3.1, 1.4, 2.4, 0.7), "wood", tag="poppet_body")
        a(c, C(x, 12.2 - ln - 1.2, 3.1, 2.8, 0.5, 0.5), "wood", tag="poppet_arm")
        a(c, C(x, 12.2 - ln, 3.1, 1.0, 1.0, 1.0), "bone", tag="poppet_head")
    a(b, C(0, 12.0, -6.4, 10.0, 8.6, 8.0), "blade", tag="cauldron")
    a(b, C(0, 20.2, -6.4, 11.0, 1.4, 9.0), "blade", tag="cauldron_rim")
    a(b, C(0, 20.8, -6.4, 8.6, 1.0, 6.8), "glow", group="fire", tag="brew")
    for s in SIDES:
        k.tongue(b, s * 2.2, 21.6, -6.4 - s, 3.0, 1.4)
        a(b, C(s * 5.6, 18.0, -6.4, 1.0, 2.0, 1.0), "acc", tag="cauldron_ear")
    k.arms("cloth", "wood", cuff="wrap", w=5.0)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.3, 20.8, 0, 6.2, 2.8, 6.2), "wrap", tag="reed_shoulder")
    k.legs("cloth", w=4.6)
    k.boots("wood", h=2.6, w=4.8, sole="dark")


@design(leather=FROG, cloth=REED, wrap=ramp("#a0a858", "#b8c070", "#d0d690", "#e4e8b0", "#f4f6d0"), dark=BLACK, gem=ramp("#a07808", "#d4a810", "#f8d830", "#fff07c", "#fffcc8"), cloth2=ramp("#0e3a18", "#14582a", "#1e7a3a", "#2c9c4a"), fire=HEXGLOW, hot=HEXGLOW)
def bogrunner(k):
    """the coven's messenger, half frog by now: a frog-skin hood with the great gold eyes still on top, lily pads for pauldrons and webbed feet"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 11.0, 7.0, 10.8), "leather", tag="frog_head")
    a(h, C(0, 24.0, 4.6, 11.4, 2.6, 2.4), "wrap", tag="frog_lower_lip")
    a(h, C(0, 26.4, 5.8, 11.2, 0.5, 0.4), "void", tag="frog_mouth")
    a(h, C(0, 30.8, -0.2, 8.6, 1.0, 8.4), "leather", tag="frog_top")
    for s in SIDES:
        a(h, C(s * 3.6, 30.6, 3.0, 4.2, 3.6, 4.2), "leather", tag="eye_bulge")
        a(h, C(s * 3.6, 31.2, 4.95, 3.0, 2.6, 0.5), "gem", tag="frog_eye")
        a(h, C(s * 3.6, 31.8, 5.15, 2.2, 0.8, 0.3), "void", tag="frog_pupil")
        a(h, C(s * 5.6, 27.6, 3.8, 0.4, 0.4, 0.3), "dark", tag="wart")
    k.fire(h, C(0, 27.2, 5.45, 4.4, 0.7, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.8), "leather", tag="frog_skin")
    a(c, C(0, 12.8, 2.55, 6.4, 9.0, 0.4), "wrap", tag="pale_belly")
    a(c, C(0, 12.2, 0, 8.7, 1.2, 5.6), "cloth", tag="reed_belt")
    for x in (-3.0, -1.0, 1.0, 3.0):
        k.tail(c, x, 12.2, 2.9, 3.6, 1.2, "cloth", tag="reed_kilt")
    for x, y, z in ((-3.2, 17.8, 2.6), (2.8, 19.2, 2.6), (3.0, 14.4, 2.6)):
        a(c, C(x, y, z, 1.0, 1.0, 0.4), "cloth2", tag="spot")
    a(b, C(0, 13.0, -3.4, 7.4, 10.0, 1.2), "leather", tag="frog_back")
    for x, y in ((-2.0, 15.0), (2.0, 17.0), (-1.0, 20.0), (2.4, 21.6)):
        a(b, C(x, y, -4.1, 1.8, 1.8, 0.4), "cloth2", tag="spot")
    a(b, C(-1.0, 8.0, -4.6, 4.2, 6.4, 3.2), "cloth", tag="message_creel")
    a(b, C(-1.0, 14.4, -4.6, 4.6, 0.7, 3.6), "dark", tag="creel_lid")
    k.fire(b, C(-1.0, 10.0, -6.25, 1.4, 1.4, 0.3))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "leather", tag="sleeve")
        k.elbow(s, "leather")
        a(p, C(x, 11.4, 0, 5.2, 5.6, 5.2), "leather", tag="forearm")
        a(p, C(x, 16.8, 0, 5.5, 0.6, 5.5), "cloth", tag="reed_tie")
        q = k.shoulder(s)
        a(q, C(x + s * 0.8, 23.0, 0, 9.6, 0.7, 9.6), "cloth2", tag="lily_pad")
        a(q, C(x + s * 0.8, 23.1, 4.4, 1.4, 0.8, 1.4), "void", tag="lily_notch")
        a(q, C(x + s * 0.8, 21.2, 0, 5.2, 1.9, 5.2), "leather", tag="pad_stem")
        k.spike(q, x + s * 2.8, 23.6, 1.8, 2.4, 1.8, "wrap", tag="lily_flower", steps=2)
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 4.7, 9.6, 4.7), "leather", tag="leg")
        a(p, C(y, 7.6, 2.5, 3.2, 4.0, 0.4), "wrap", tag="pale_thigh")
        p = k.boot(s)
        a(p, C(y, 0, 0.2, 4.8, 2.4, 5.2), "leather", tag="boot")
        a(p, C(y, 0, 3.4, 7.0, 0.6, 5.0), "leather", tag="sole")
        for dx in (-2.8, 0, 2.8):
            a(p, C(y + dx, 0, 5.8, 1.6, 0.9, 1.4), "cloth2", tag="toe_pad")


@design(blade=PEAT, stone=PEAT, cloth=MIRE, wrap=REED, wood=ramp("#1c1208", "#30200e", "#483218", "#624824", "#806434"), leather=HIDE, dark=BLACK, acc=ramp("#20242a", "#383e46", "#586068", "#828c94"), mail=MIRE, cloth2=ramp("#10301a", "#1a4a26", "#2a6a36"), gem=HEXGLOW, fire=HEXGLOW, hot=HEXGLOW)
def fenwarden(k):
    """he walks the safe paths through the mire: a helm crowned with cattails, armour cut from black peat, a long hooked pole on his back with a will-o'-the-wisp caged over his head"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.6, 0, 9.8, 8.8, 9.8), "blade", tag="helm")
    a(h, C(0, 26.8, 4.9, 8.0, 1.0, 0.4), "void", tag="slit")
    k.fire(h, C(0, 27.0, 5.1, 6.4, 0.6, 0.3))
    a(h, C(0, 22.6, 0.2, 10.8, 3.4, 10.6), "cloth", tag="moss_gorget")
    a(h, C(0, 32.2, 0, 10.2, 1.0, 10.2), "wrap", tag="reed_wreath")
    for x, z, ln, t in ((-3.6, 3.4, 9.0, 8), (0.0, 4.2, 11.0, 0), (3.6, 3.4, 8.0, -8), (-4.4, -1.8, 10.0, 12), (4.4, -1.8, 9.0, -12), (0, -4.2, 12.0, 0)):
        a(h, C(x, 33.0, z, 0.7, ln, 0.7), "wrap", tag="cattail_stem", rots=(("z", t),), pivot=(x, 33, z))
        a(h, C(x, 33.0 + ln * 0.62, z, 1.6, 3.0, 1.6), "wood", tag="cattail_head", rots=(("z", t),), pivot=(x, 33, z))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.0), "blade", tag="peat_plate")
    for x, w in ((-3.0, 1.4), (-0.6, 1.6), (2.0, 1.4)):
        a(c, C(x, 13.0, 3.05, w, 9.6, 0.4), "wrap", tag="reed_stave")
    a(c, C(0, 14.4, 3.3, 8.6, 0.8, 0.4), "dark", tag="tie")
    a(c, C(0, 19.2, 3.3, 8.6, 0.8, 0.4), "dark", tag="tie")
    a(c, C(0, 12.2, 0, 8.7, 1.3, 6.6), "dark", tag="belt")
    rz = (("z", -14),)
    a(b, C(0, 2.0, -3.8, 1.2, 40.0, 1.2), "wood", tag="pole", rots=rz, pivot=(0, 20, -3.8))
    for dy, dx, w, ht in ((41.6, 1.0, 5.4, 1.0), (40.6, 4.0, 1.0, 1.8), (37.4, 4.0, 0.5, 3.4)):
        a(b, C(dx, dy, -3.8, w, ht, 1.0), "wood" if ht < 3 else "acc", tag="hook", rots=rz, pivot=(0, 20, -3.8))
    a(b, C(4.0, 33.4, -3.8, 4.4, 4.0, 4.4), "acc", tag="wisp_cage", rots=rz, pivot=(0, 20, -3.8))
    a(b, C(4.0, 34.0, -3.8, 4.8, 2.8, 2.0), "glow", group="fire", tag="wisp", rots=rz, pivot=(0, 20, -3.8))
    a(b, C(4.0, 34.0, -3.8, 2.0, 2.8, 4.8), "glow", group="fire", tag="wisp", rots=rz, pivot=(0, 20, -3.8))
    k.arms("mail", "blade", joint="mail", cuff="wrap", w=5.4)
    for s in SIDES:
        q = k.shoulder(s)
        a(q, C(s * 6.6, 20.8, 0, 6.6, 3.2, 6.8), "blade", tag="pauldron")
        for t in (-2.6, -0.9, 0.9, 2.6):
            a(q, C(s * 9.9, 17.4, t, 0.5, 6.2, 1.2), "wrap", tag="reed_fringe")
        a(k.leg(s), C(s * 1.95, 6.0, 2.5, 3.8, 6.0, 0.6), "wrap", tag="reed_tasset")
        a(k.leg(s), C(s * 1.95, 7.0, 2.8, 4.0, 0.7, 0.4), "dark", tag="tie")
    k.legs("blade", w=4.8)
    k.boots("wood", h=6.0, w=5.2, cuff="wrap", sole="dark")


@design(leather=ramp("#1c2e18", "#2c4422", "#40602e", "#587c3c", "#769a52"), fur=ramp("#141a10", "#20281a", "#303c24", "#445430"), bone=ramp("#8a7a56", "#a89870", "#c8b890", "#e0d4b0", "#f4eed4"), wood=PEAT, dark=BLACK, stone=MIRE, wrap=HEMP, acc=IRON, blade=PEAT, fire=HEXGLOW, hot=HEXGLOW)
def trollhide(k):
    """the skin of the bog troll he killed, worn with the head on: great yellow tusks, warts and all, a mossy mane, and the troll's own club"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.6, 0, 11.4, 10.6, 11.4), "leather", tag="troll_head")
    a(h, C(0, 28.8, 5.6, 11.8, 2.4, 1.6), "leather", tag="troll_brow")
    a(h, C(0, 23.0, 6.0, 9.4, 3.2, 2.6), "leather", tag="troll_jaw")
    a(h, C(0, 26.2, 5.8, 8.8, 2.4, 0.5), "void", tag="troll_maw")
    a(h, C(0, 26.8, 6.2, 2.8, 2.2, 1.6), "leather", tag="troll_nose")
    for s in SIDES:
        k.fire(h, C(s * 3.2, 27.4, 6.1, 1.6, 0.9, 0.3))
        k.spike(h, s * 3.8, 24.4, 7.0, 7.4, 2.6, "bone", rz=-s * 8, rx=-14, tag="tusk", steps=4)
        k.spike(h, s * 5.8, 31.0, 0, 5.0, 2.8, "leather", rz=-s * 62, tag="troll_ear")
    for x, y, z in ((-3.4, 33.4, 2.4), (2.0, 34.0, 4.0), (4.4, 33.2, -1.0), (-1.4, 34.0, -2.8)):
        a(h, C(x, y, z, 1.8, 1.0, 1.8), "leather", tag="wart")
    a(h, C(0, 26.0, -5.6, 9.4, 8.4, 1.6), "fur", tag="mane")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.4), "leather", tag="troll_hide")
    a(c, C(0, 20.0, 0, 8.7, 4.0, 7.0), "fur", tag="mossy_mane")
    for x, y in ((-2.4, 17.2), (2.8, 15.0), (-1.0, 13.6), (3.0, 18.4)):
        a(c, C(x, y, 3.3, 1.8, 1.8, 0.6), "stone", tag="wart")
    a(c, C(0, 12.2, 0, 8.7, 1.8, 7.0), "wrap", tag="rope_belt")
    k.fire(c, C(0, 16.2, 3.35, 1.0, 3.0, 0.3))
    a(b, C(0, 4.0, -3.8, 9.4, 20.0, 0.9), "fur", tag="troll_back", rots=(("x", 4),), pivot=(0, 24, -3.8))
    rz = (("z", -30),)
    a(b, C(0, 6.0, -5.2, 1.8, 18.0, 1.8), "wood", tag="club_grip", rots=rz, pivot=(0, 18, -5.2))
    a(b, C(0, 22.0, -5.2, 5.0, 12.0, 5.0), "wood", tag="club_head", rots=rz, pivot=(0, 18, -5.2))
    a(b, C(0, 24.0, -5.2, 6.0, 6.0, 6.0), "wood", tag="club_knot", rots=rz, pivot=(0, 18, -5.2))
    for dy, dz in ((30.0, 2.8), (28.0, -2.8), (26.0, 2.8)):
        k.spike(b, 0, dy - 4, -5.2 + dz, 3.4, 1.2, "bone", tag="club_tooth")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.6, 3.4, 5.6), "leather", tag="arm_hide")
        k.elbow(s, "leather")
        a(p, C(x, 10.8, 0, 6.4, 6.2, 6.4), "leather", tag="troll_hand")
        a(p, C(x, 16.4, 0, 6.6, 1.0, 6.6), "fur", tag="fur_cuff")
        for dz in (-2.0, 0, 2.0):
            k.spike(p, x + dz * 0.8, 11.2, 2.8, -2.6, 1.0, "bone", tag="claw", steps=2)
        q = k.shoulder(s)
        a(q, C(x + s * 0.8, 20.6, 0, 7.8, 3.8, 8.0), "fur", tag="fur_shoulder")
        a(q, C(x + s * 1.0, 23.8, 0, 6.4, 1.6, 6.6), "fur", tag="fur_top")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.2, 0, 5.2, 9.8, 5.2), "leather", tag="troll_leg")
        a(p, C(y, 8.0, 0, 5.5, 4.0, 5.5), "fur", tag="fur_thigh")
        p = k.boot(s)
        a(p, C(y, 0, 0.2, 5.6, 3.2, 6.4), "leather", tag="boot")
        a(p, C(y, 0, 0.4, 5.9, 0.5, 7.0), "void", tag="sole")
        for dx in (-1.8, 0, 1.8):
            k.spike(p, y + dx, 0.6, 3.2, 2.8, 1.2, "bone", rx=-82, tag="toe_claw", steps=2)


# ---------------------------------------------------------------- the Sandsunk Tomb

@design(cloth=LINEN, wrap=LINEN, acc=GILT, gold=GILT, gem=LAPIS, dark=ramp("#1c1408", "#30220e", "#463218"), leather=SAND, blade=GILT, stone=SAND, fire=SUN, hot=SUN, no_skirt=False)
def linenwrap(k):
    """a priest embalmed alive: linen bandage from crown to foot, a gold sun collar and canopic jars at the belt, one strip always coming loose"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.8, -0.2, 9.4, 8.6, 9.6), "cloth", tag="bandage_head")
    for y, t in ((25.0, 5), (26.8, -4), (29.6, 6), (31.2, -5)):
        a(h, C(0, y, -0.2, 9.8, 0.6, 10.0), "leather", tag="turn", rots=(("z", t * 0.6),), pivot=(0, y, 0))
    a(h, C(0, 27.6, 4.65, 7.0, 1.4, 0.3), "void", tag="eye_gap")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 27.9, 4.85, 1.2, 0.7, 0.3))
    a(h, C(0, 32.4, 4.2, 2.4, 3.6, 1.0), "acc", tag="brow_cobra")
    a(h, C(0, 33.4, 4.8, 1.2, 1.6, 0.5), "gem", tag="cobra_jewel")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="bandage_body")
    for y, t in ((13.6, 8), (15.6, -7), (17.6, 8)):
        a(c, C(0, y, 2.75, 8.6, 0.8, 0.5), "leather", tag="turn", rots=(("z", t),), pivot=(0, y, 2.75))
    a(c, C(0, 19.6, 0, 8.7, 4.4, 6.2), "acc", tag="broad_collar")
    for y, m in ((19.8, "gem"), (21.4, "dark"), (23.0, "gem")):
        a(c, C(0, y, 3.15, 7.8, 0.7, 0.3), m, tag="collar_row")
    k.fire(c, C(0, 19.0, 3.05, 2.0, 2.0, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.4, 6.0), "acc", tag="belt")
    for x, m in ((-3.2, "gem"), (0, "acc"), (3.2, "gem")):
        a(c, C(x, 8.6, 3.3, 2.0, 3.4, 2.0), "stone", tag="canopic_jar")
        a(c, C(x, 12.0, 3.3, 1.6, 1.0, 1.6), m, tag="jar_lid")
    a(b, C(0, 14.0, -3.8, 7.6, 9.4, 1.2), "leather", tag="back_panel")
    for x, ln, r in ((-2.8, 18.0, 6), (0.6, 12.0, 10), (3.0, 20.0, 4)):
        a(b, C(x, 23.0 - ln, -3.6, 1.6, ln, 0.5), "cloth", tag="trailing_bandage", rots=(("x", r), ("z", x * 2)), pivot=(x, 23, -3.6))
    a(k.shoulder(1), C(6.6, 21.0, 0, 6.0, 2.6, 6.0), "acc", tag="wide_collar_shoulder")
    a(k.shoulder(-1), C(-6.6, 21.0, 0, 6.0, 2.6, 6.0), "acc", tag="wide_collar_shoulder")
    k.arms("cloth", "cloth", cuff="acc", w=5.2)
    for s in SIDES:
        for y, t in ((12.8, 12), (14.4, -10)):
            a(k.arm(s), C(s * 6.0, y, 0, 5.5, 0.6, 5.5), "leather", tag="turn")
    a(k.arm(-1), C(-8.8, 3.0, 0, 1.2, 10.0, 0.4), "cloth", tag="trailing_bandage")
    k.legs("cloth", w=4.6)
    k.boots("cloth", h=2.6, w=4.8, cuff="leather", sole="dark")


@design(blade=ramp("#100c08", "#1e1810", "#30261a", "#463826", "#604e36"), acc=GILT, gold=GILT, gem=LAPIS, cloth=LINEN, wrap=LINEN, leather=SAND, dark=BLACK, fire=SUN, hot=SUN)
def jackalrunner(k):
    """he guards the dead's road: a black jackal's head with tall gold-tipped ears and a long muzzle, a gold pectoral, a pleated white kilt"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.6, 9.2, 8.0, 9.0), "blade", tag="jackal_head")
    a(h, C(0, 26.0, 5.4, 4.8, 3.8, 3.4), "blade", tag="muzzle_root")
    a(h, C(0, 25.6, 8.2, 3.4, 2.8, 3.0), "blade", tag="muzzle")
    a(h, C(0, 25.4, 10.4, 2.4, 2.0, 2.0), "blade", tag="muzzle_tip")
    a(h, C(0, 26.6, 11.3, 1.4, 1.0, 0.5), "void", tag="nose")
    a(h, C(0, 25.0, 7.8, 3.5, 0.5, 5.0), "void", tag="jaw_line")
    for s in SIDES:
        a(h, C(s * 3.0, 32.0, -0.6, 2.8, 8.0, 1.6), "blade", tag="tall_ear", rots=(("z", -s * 8),), pivot=(s * 3, 32, -0.6))
        a(h, C(s * 3.6, 37.4, -0.6, 2.0, 2.8, 1.8), "acc", tag="ear_tip", rots=(("z", -s * 8),), pivot=(s * 3, 32, -0.6))
        a(h, C(s * 3.0, 32.4, 0.25, 1.4, 5.0, 0.3), "acc", tag="ear_inner", rots=(("z", -s * 8),), pivot=(s * 3, 32, -0.6))
        k.fire(h, C(s * 2.8, 28.6, 3.95, 1.4, 0.8, 0.3))
    a(h, C(0, 22.4, 0, 10.8, 2.0, 10.8), "acc", tag="neck_ring")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.8), "leather", tag="tanned_body")
    a(c, C(0, 19.4, 0, 8.7, 4.6, 5.8), "acc", tag="broad_collar")
    for y, m in ((19.8, "gem"), (21.4, "blade"), (23.0, "gem")):
        a(c, C(0, y, 2.95, 8.0, 0.7, 0.3), m, tag="collar_row")
    a(c, C(0, 14.6, 2.6, 3.4, 3.6, 0.5), "acc", tag="pectoral")
    k.fire(c, C(0, 15.4, 2.85, 1.8, 1.8, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.4, 5.6), "acc", tag="belt")
    a(b, C(0, 13.0, -3.0, 7.0, 10.0, 0.7), "leather", tag="back")
    k.spike(b, 0, 12.4, -3.2, -9.0, 2.6, "blade", rx=-14, tag="jackal_tail", steps=4)
    for s in SIDES:
        rz = (("z", -s * 20),)
        a(b, C(s * 4.0, 4.0, -3.6, 0.9, 28.0, 0.9), "dark", tag="was_sceptre", rots=rz, pivot=(s * 4, 18, -3.6))
        a(b, C(s * 4.0, 32.0, -3.6, 2.6, 1.4, 1.0), "acc", tag="was_head", rots=rz, pivot=(s * 4, 18, -3.6))
    k.arms("leather", "leather", cuff="acc", w=5.0, low_h=4.6)
    for s in SIDES:
        for y in (12.6, 14.0):
            a(k.arm(s), C(s * 6.0, y, 0, 5.4, 0.6, 5.4), "gem" if y > 13 else "acc", tag="bangle")
        a(k.arm(s), C(s * 6.0, 19.6, 0, 5.4, 0.9, 5.4), "acc", tag="armlet")
        a(k.shoulder(s), C(s * 6.2, 21.4, 0, 5.4, 1.8, 5.4), "acc", tag="collar_shoulder")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 6.2, 0, 5.2, 5.8, 5.2), "cloth", tag="pleated_kilt")
        for dx in (-1.6, 0, 1.6):
            a(p, C(x + dx, 6.2, 2.65, 0.4, 5.8, 0.3), "leather", tag="pleat")
        a(p, C(x, 2.2, 0, 4.4, 4.2, 4.4), "leather", tag="bare_shin")
        a(p, C(x, 2.6, 2.3, 2.6, 2.8, 0.5), "acc", tag="greave")
    a(c, C(0, 6.4, 2.95, 2.6, 5.8, 0.5), "gem", tag="kilt_panel")
    k.boots("blade", h=2.0, w=4.8, sole="void", toe="acc", toe_d=2.4)


@design(scale=GILT, blade=GILT, acc=LAPIS, gem=LAPIS, gold=GILT, dark=ramp("#1c1408", "#30220e", "#463218"), cloth=LINEN, wrap=LINEN, leather=SAND, mail=GILT, fire=SUN, hot=SUN)
def sunscale(k):
    """the Sun King's captain: gold scale from neck to knee, a helm with the rearing cobra, and the disc of the sun standing behind his head, its rays cut out in gold"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.6, -0.2, 9.8, 9.0, 10.0), "scale", tag="scale_helm")
    a(h, C(0, 26.6, 4.85, 8.0, 3.4, 0.4), "void", tag="face_gap")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 27.8, 5.05, 1.2, 0.7, 0.3))
        a(h, C(s * 5.3, 24.0, 2.0, 0.6, 7.0, 4.4), "acc", tag="cheek_stripe")
    a(h, C(0, 31.2, 4.8, 8.8, 1.2, 0.8), "acc", tag="brow_band")
    a(h, C(0, 32.4, 4.8, 2.0, 3.0, 1.0), "gem", tag="cobra_neck")
    a(h, C(0, 35.2, 5.2, 3.2, 2.0, 1.4), "blade", tag="cobra_hood")
    a(h, C(0, 35.8, 6.0, 1.2, 0.8, 0.5), "void", tag="cobra_eye")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.0), "scale", tag="scale_coat")
    a(c, C(0, 20.8, 0, 8.7, 3.2, 6.8), "gem", tag="lapis_collar")
    for y in (21.2, 22.8):
        a(c, C(0, y, 3.45, 8.0, 0.5, 0.3), "blade", tag="collar_row")
    a(c, C(0, 14.8, 3.1, 3.6, 3.6, 0.5), "dark", tag="sun_seat")
    k.fire(c, C(0, 15.6, 3.35, 2.2, 2.2, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.4, 6.6), "acc", tag="belt")
    a(b, C(0, 13.0, -3.6, 7.8, 10.4, 1.4), "scale", tag="back_scale")
    a(b, C(0, 20.0, -4.6, 6.0, 5.0, 1.4), "acc", tag="sun_mount")
    a(b, C(0, 22.4, -5.4, 16.0, 16.0, 0.9), "blade", tag="sun_disc")
    a(b, C(0, 20.4, -5.4, 11.0, 20.0, 0.9), "blade", tag="sun_disc")
    a(b, C(0, 24.8, -5.4, 20.0, 11.0, 0.9), "blade", tag="sun_disc")
    a(b, C(0, 26.0, -5.9, 10.0, 8.8, 0.4), "acc", tag="sun_ring")
    a(b, C(0, 27.2, -6.1, 6.8, 6.4, 0.4), "glow", group="fire", tag="sun_face")
    for t in range(12):
        a(b, C(0, 40.0, -5.4, 1.6, 6.4 if t % 2 else 4.0, 0.7), "blade", tag="sun_ray", rots=(("z", t * 30 + 15),), pivot=(0, 30.4, -5.4))
    k.arms("scale", "scale", joint="dark", cuff="gem", w=5.4)
    for s in SIDES:
        q = k.shoulder(s)
        a(q, C(s * 6.6, 20.6, 0, 7.2, 3.4, 7.4), "scale", tag="scale_pauldron")
        a(q, C(s * 6.6, 20.3, 0, 7.6, 0.9, 7.8), "gem", tag="pauldron_rim")
        a(q, C(s * 6.6, 23.8, 0, 5.6, 0.8, 5.8), "acc", tag="pauldron_top")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 5.6, 0, 5.0, 6.4, 5.0), "scale", tag="scale_skirt")
        a(p, C(x, 2.2, 0, 4.4, 3.6, 4.4), "wrap", tag="shin_wrap")
        a(p, C(x, 2.4, 2.3, 3.2, 3.2, 0.6), "blade", tag="greave")
    k.boots("blade", h=2.4, w=5.0, cuff="gem", sole="dark", toe="acc", toe_d=2.0)


@design(blade=GILT, acc=LAPIS, gem=LAPIS, gold=GILT, dark=ramp("#100c08", "#1e1810", "#30261a", "#463826"), cloth=LAPIS, wrap=LINEN, leather=SAND, mail=GILT, stone=SAND, fire=SUN, hot=SUN)
def tombguard(k):
    """the last guard of the Sun King: a blue and gold striped nemes, a false beard, a painted coffin face for a breastplate and the crook and flail crossed behind him"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.4, 9.8, 8.0, 9.8), "blade", tag="gold_face")
    a(h, C(0, 26.8, 4.55, 7.4, 1.2, 0.4), "void", tag="kohl")
    for s in SIDES:
        k.fire(h, C(s * 2.2, 27.0, 4.75, 1.4, 0.7, 0.3))
    a(h, C(0, 21.4, 4.8, 1.6, 4.2, 1.2), "acc", tag="false_beard")
    a(h, C(0, 31.0, -0.4, 11.6, 3.0, 11.0), "acc", tag="nemes_top")
    a(h, C(0, 33.6, -0.4, 9.6, 1.4, 9.4), "acc", tag="nemes_crown")
    for y in (31.4, 33.0, 34.4):
        a(h, C(0, y, -0.4, 11.8 if y < 33 else 9.8, 0.6, 11.2 if y < 33 else 9.6), "blade", tag="nemes_stripe")
    a(h, C(0, 31.2, 5.3, 8.6, 1.0, 0.5), "blade", tag="nemes_band")
    a(h, C(0, 32.2, 5.4, 1.8, 3.2, 1.0), "blade", tag="uraeus")
    for s in SIDES:
        a(h, C(s * 7.0, 19.0, 1.6, 2.8, 12.4, 3.4), "acc", tag="nemes_lappet", rots=(("z", s * 8),), pivot=(s * 5.4, 31, 1.6))
        for y in (20.4, 22.6, 24.8, 27.0, 29.2):
            a(h, C(s * 7.0 - s * (31 - y) * 0.14, y, 1.6, 3.0, 0.7, 3.6), "blade", tag="nemes_stripe")
    a(h, C(0, 24.0, -5.8, 8.8, 7.4, 1.6), "acc", tag="nemes_tail")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.8), "blade", tag="coffin_breast")
    a(c, C(0, 14.2, 3.45, 6.4, 7.6, 0.5), "acc", tag="wings_field")
    a(c, C(0, 15.8, 3.75, 3.2, 3.2, 0.3), "blade", tag="sun_plate")
    k.fire(c, C(0, 16.4, 3.95, 2.0, 2.0, 0.3))
    for s in SIDES:
        for i in range(3):
            a(c, C(s * 2.6, 19.0 + i * 0.9 - 1.8, 3.8, 2.2, 0.5, 0.3), "blade", tag="painted_wing")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.4), "dark", tag="belt")
    a(b, C(0, 13.0, -3.8, 7.8, 10.4, 1.6), "blade", tag="back_plate")
    r1, r2 = (("z", 30),), (("z", -30),)
    a(b, C(0, 4.0, -5.0, 1.3, 28.0, 1.3), "acc", tag="crook", rots=r1, pivot=(0, 18, -5.0))
    for y in (10.0, 16.0, 22.0, 28.0):
        a(b, C(0, y, -5.0, 1.5, 1.2, 1.5), "blade", tag="crook_band", rots=r1, pivot=(0, 18, -5.0))
    a(b, C(1.8, 32.0, -5.0, 4.4, 1.3, 1.3), "acc", tag="crook_hook", rots=r1, pivot=(0, 18, -5.0))
    a(b, C(3.6, 29.6, -5.0, 1.3, 3.4, 1.3), "acc", tag="crook_hook", rots=r1, pivot=(0, 18, -5.0))
    a(b, C(0, 4.0, -6.2, 1.3, 26.0, 1.3), "blade", tag="flail", rots=r2, pivot=(0, 18, -6.2))
    for dx in (-1.8, 0, 1.8):
        for i in range(4):
            a(b, C(dx, 29.4 + i * 1.4, -6.2, 1.1, 1.2, 1.1), "acc" if i % 2 else "blade", tag="flail_bead", rots=r2, pivot=(0, 18, -6.2))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "blade", tag="vambrace")
        for y in (12.4, 14.2):
            a(p, C(x, y, 0, 6.3, 0.8, 6.3), "acc", tag="stripe")
        q = k.shoulder(s)
        for i in range(3):
            a(q, C(x + s * (1.2 - i * 0.2), 20.5 + i * 1.3, 0, 8.4 - i * 1.2, 1.2, 8.4 - i), "blade" if i % 2 == 0 else "acc", tag="lame")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 2.4, 0, 5.1, 9.6, 5.1), "blade", tag="cuisse")
        a(p, C(x, 8.2, 0, 5.4, 0.9, 5.4), "acc", tag="stripe")
        a(p, C(x, 4.8, 2.6, 3.8, 2.6, 0.9), "acc", tag="poleyn")
    k.boots("blade", h=4.0, w=5.2, cuff="acc", toe="dark", toe_d=2.8)


# ---------------------------------------------------------------- the Fallen Titan

@design(cloth=ramp("#2a2c08", "#42440e", "#5e6014", "#7c8020", "#a0a434"), leather=FLESH, bone=BONE, dark=BLACK, wrap=FLESH, gem=BILE, acc=BONE, fire=BILE, hot=BILE)
def bilepriest(k):
    """he tends what still drips in the titan's belly: gut-rope belts, a hood cut from stomach lining, and the great gall bladders hung swollen and lit on his back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.6, -0.6, 9.8, 9.4, 9.6), "wrap", tag="stomach_hood")
    a(h, C(0, 33.0, -2.0, 5.4, 2.0, 5.0), "wrap", tag="hood_peak")
    a(h, C(0, 27.4, 4.3, 7.0, 3.0, 0.6), "void", tag="hood_dark")
    for s in SIDES:
        k.fire(h, C(s * 1.8, 28.4, 4.65, 1.0, 0.7, 0.3))
    for x, ln in ((-3.4, 3.2), (-1.0, 4.6), (1.6, 3.0), (3.6, 4.0)):
        a(h, C(x, 26.0 - ln, 4.8, 1.0, ln, 0.5), "glow", group="fire", tag="bile_drip")
    a(h, C(0, 22.4, 0, 11.0, 2.4, 11.0), "acc", tag="rib_collar")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 12.2, 2.75, 3.0, 11.8, 0.5), "wrap", tag="gut_stole")
    for y, t in ((14.0, 12), (17.0, -12), (20.0, 12)):
        a(c, C(0, y, 3.05, 8.4, 1.3, 0.6), "wrap", tag="gut_rope", rots=(("z", t),), pivot=(0, y, 3.05))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 6.0), "wrap", tag="gut_belt")
    k.tail(c, 2.8, 12.2, 3.2, 6.4, 1.4, "wrap", tag="gut_end")
    for x, y, w, ht in ((-2.6, 13.4, 6.4, 8.4), (3.0, 15.2, 5.0, 7.0), (0.0, 21.0, 4.0, 5.0)):
        a(b, C(x, y, -5.8, w, ht, w), "glow", group="fire", tag="gall_sac")
        a(b, C(x, y + 1.0, -5.8, w + 0.6, ht - 2.0, w + 0.6), "gem", tag="gall_wall")
        a(b, C(x, y + ht, -5.8, 1.6, 1.0, 1.6), "wrap", tag="sac_neck")
        a(b, C(x, y + ht * 0.6, -5.8 - w / 2 - 0.4, w * 0.5, 1.0, 0.3), "void", tag="sac_vein")
    a(b, C(0, 13.0, -3.4, 7.0, 10.0, 1.0), "wrap", tag="sac_harness")
    k.arms("cloth", "wrap", cuff="acc", w=5.4)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.3, 20.8, 0, 6.0, 2.8, 6.0), "wrap", tag="shoulder")
        k.spike(k.shoulder(s), s * 7.6, 23.2, 0, 4.4, 1.8, "acc", rz=-s * 28, tag="rib_tip")
    k.legs("cloth", w=4.6)
    k.boots("wrap", h=2.8, w=4.8, sole="dark")


@design(leather=FLESH, wrap=ramp("#7a5a4c", "#a07c6a", "#c4a48c", "#e0c8b0", "#f4e4d0"), bone=BONE, dark=ramp("#180606", "#2a0c0c", "#401212"), blade=FLESH, acc=BONE, cloth=ramp("#1c0808", "#2e1010", "#461a1a"), fire=MARROW, hot=MARROW)
def sinewrunner(k):
    """he wears the titan's tendons: long pale strands binding bare red muscle, no skin at all, shards of jaw for a mask and bone spurs at every joint"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.0, 8.0, 9.2), "leather", tag="muscle_head")
    for x in (-3.2, -1.2, 1.0, 3.2):
        a(h, C(x, 24.0, 4.45, 1.0, 8.0, 0.3), "wrap", tag="strand")
    a(h, C(0, 23.4, 4.4, 7.8, 3.0, 1.0), "bone", tag="jaw_mask")
    for x in (-2.6, -1.3, 0, 1.3, 2.6):
        k.spike(h, x, 26.2, 4.9, 1.6, 0.8, "bone", tag="tooth", steps=2)
    for s in SIDES:
        a(h, C(s * 2.2, 28.2, 4.65, 2.0, 1.2, 0.3), "void", tag="eye")
        k.fire(h, C(s * 2.2, 28.4, 4.8, 1.2, 0.7, 0.3))
        k.spike(h, s * 3.4, 32.0, 0, 5.0, 1.8, "bone", rz=-s * 18, rx=20, tag="skull_spur")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.8), "leather", tag="muscle")
    for x, r in ((-3.0, 4), (-1.2, -3), (1.0, 3), (3.0, -4)):
        a(c, C(x, 12.4, 2.55, 1.0, 11.4, 0.4), "wrap", tag="strand", rots=(("z", r),), pivot=(x, 18, 2.55))
    for y in (14.6, 18.0, 21.0):
        a(c, C(0, y, 2.8, 8.4, 0.7, 0.4), "wrap", tag="tendon_wrap")
    k.fire(c, C(0, 16.0, 2.95, 1.4, 1.4, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.6), "dark", tag="belt")
    a(b, C(0, 13.2, -2.9, 2.0, 10.4, 1.2), "bone", tag="spine")
    for y in (14.0, 17.0, 20.0, 23.0):
        k.spike(b, 0, y, -3.4, 3.2, 1.6, "bone", rx=56, tag="spine_spur")
    for x, r in ((-3.0, 10), (3.0, -10)):
        for i in range(3):
            a(b, C(x + i * 0.6 * (1 if x > 0 else -1), 23.0 - 20.0, -3.2 - i * 0.2, 0.7, 20.0, 0.4), "wrap", tag="strand_trail", rots=(("x", 4 + i * 5), ("z", r)), pivot=(x, 23, -3.2))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "leather", tag="sleeve")
        k.elbow(s, "leather")
        a(p, C(x, 11.4, 0, 5.2, 5.6, 5.2), "leather", tag="forearm")
        for y in (12.4, 14.0, 15.6):
            a(p, C(x, y, 0, 5.5, 0.6, 5.5), "wrap", tag="tendon_wrap")
        k.spike(p, x, 16.6, -2.8, 4.4, 2.0, "bone", rx=132, tag="elbow_spur")
        q = k.shoulder(s)
        a(q, C(x + s * 0.2, 21.2, 0, 5.4, 2.2, 5.4), "bone", tag="scapula")
        k.spike(q, x + s * 1.6, 23.2, 0, 5.2, 2.2, "bone", rz=-s * 34, tag="shoulder_spur")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 4.6, 9.6, 4.6), "leather", tag="leg")
        for yy in (3.4, 8.0, 9.8):
            a(p, C(y, yy, 0, 4.9, 0.6, 4.9), "wrap", tag="tendon_wrap")
        k.spike(p, y, 5.2, 2.4, 3.6, 1.6, "bone", rx=-52, tag="knee_spur")
    k.boots("bone", h=2.6, w=4.8, cuff="wrap", toe="bone", toe_d=3.0)


@design(bone=BONE, blade=BONE, dark=ramp("#180606", "#2a0c0c", "#401212", "#5a1c1c"), mail=FLESH, leather=HIDE, acc=FLESH, gem=MARROW, cloth=FLESH, fire=MARROW, hot=MARROW)
def marrowplate(k):
    """plate sawn out of the titan's thigh bone, the marrow still alive and shining through the honeycomb where it was cut"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.2, 0, 10.2, 9.2, 10.2), "bone", tag="helm")
    a(h, C(0, 32.2, 0, 7.8, 1.2, 7.8), "bone", tag="helm_top")
    a(h, C(0, 26.6, 5.0, 8.4, 1.0, 0.4), "void", tag="slit")
    k.fire(h, C(0, 26.8, 5.2, 6.8, 0.6, 0.3))
    for x, y, w in ((-3.0, 30.0, 1.6), (-1.0, 29.0, 1.2), (1.2, 30.2, 1.6), (3.2, 29.0, 1.2), (-2.2, 24.0, 1.4), (0.6, 23.8, 1.6), (3.0, 24.4, 1.2)):
        k.fire(h, C(x, y, 5.2, w, w, 0.3))
    a(h, C(0, 33.2, 0, 3.0, 2.4, 8.0), "bone", tag="crest")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.6), "bone", tag="cuirass")
    for x, y, w in ((-3.0, 19.0, 1.8), (-1.0, 20.4, 1.4), (1.2, 18.6, 1.8), (3.2, 20.2, 1.4), (-2.0, 15.6, 1.6), (0.0, 16.6, 2.0), (2.2, 15.2, 1.6), (-3.2, 13.6, 1.2), (3.0, 13.2, 1.4)):
        a(c, C(x, y, 3.3, w + 0.5, w + 0.5, 0.4), "dark", tag="marrow_pit")
        k.fire(c, C(x, y + 0.25, 3.55, w, w, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.2), "dark", tag="belt")
    a(b, C(0, 13.0, -3.8, 7.6, 10.4, 1.6), "bone", tag="back_plate")
    for x, y in ((-2.4, 15.0), (0.4, 17.2), (2.6, 14.4), (-1.6, 20.0), (2.0, 20.6)):
        k.fire(b, C(x, y, -4.7, 1.6, 1.6, 0.3))
    a(b, C(0, 21.4, -5.6, 2.6, 24.0, 2.6), "bone", tag="back_femur", rots=(("z", 36),), pivot=(0, 22, -5.6))
    a(b, C(0, 44.0, -5.6, 5.4, 4.4, 4.0), "bone", tag="femur_knob", rots=(("z", 36),), pivot=(0, 22, -5.6))
    a(b, C(0, 45.0, -8.0, 2.6, 2.6, 0.3), "glow", group="fire", tag="femur_cut", rots=(("z", 36),), pivot=(0, 22, -5.6))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "bone", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.4, 1.0, 6.4), "dark", tag="cuff")
        for y, dx in ((12.0, -1.4), (14.0, 1.2), (13.0, 0.0)):
            k.fire(p, C(x + dx, y, 3.1, 1.2, 1.2, 0.3))
        q = k.shoulder(s)
        a(q, C(x + s * 1.2, 20.5, 0, 8.6, 4.0, 8.8), "bone", tag="sawn_shoulder")
        a(q, C(x + s * 1.2, 24.5, 0, 7.0, 0.5, 7.2), "dark", tag="saw_cut")
        k.fire(q, C(x + s * 1.2, 24.8, 0, 5.4, 0.3, 5.6))
        for t, d in ((-2.2, 1.2), (0.6, -1.4), (2.4, 1.0)):
            a(q, C(x + s * 1.2 + d, 24.9, t, 1.2, 0.4, 1.2), "void", tag="honeycomb")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.1, 9.6, 5.1), "bone", tag="cuisse")
        a(p, C(y, 4.6, 2.6, 4.0, 3.0, 1.0), "dark", tag="poleyn")
        k.fire(p, C(y, 5.4, 3.15, 1.8, 1.4, 0.3))
    k.boots("bone", h=4.0, w=5.2, cuff="dark", toe="dark", toe_d=2.8)


@design(bone=BONE, blade=BONE, dark=BLACK, mail=FLESH, leather=HIDE, acc=FLESH, cloth=FLESH, fire=MARROW, hot=MARROW)
def titanbone(k):
    """the Still Heart's own skull on your shoulders: a huge horned jaw for a helm, and a pair of the titan's ribs sweeping up and over the back like a great cage"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 25.4, -0.6, 12.8, 8.8, 13.0), "bone", tag="titan_cranium")
    a(h, C(0, 28.0, 5.8, 13.0, 2.8, 1.4), "bone", tag="brow_ridge")
    a(h, C(0, 22.2, 2.8, 11.0, 3.4, 7.4), "bone", tag="titan_jaw")
    a(h, C(0, 25.2, 5.8, 9.4, 2.4, 0.5), "void", tag="maw")
    for x in (-4.0, -2.4, -0.8, 0.8, 2.4, 4.0):
        k.spike(h, x, 25.0, 6.1, 2.6, 1.2, "bone", tag="fang", steps=2)
        k.spike(h, x + 0.4, 27.8, 6.1, -2.2, 1.0, "bone", tag="fang", steps=2)
    for s in SIDES:
        a(h, C(s * 3.6, 28.4, 6.3, 3.0, 1.8, 0.4), "void", tag="socket")
        k.fire(h, C(s * 3.6, 28.8, 6.5, 1.6, 1.0, 0.3))
        k.horn(h, s * 6.0, 31.0, 0, [(5.0, -s * 66, 3.4), (5.0, -s * 40, 2.8), (5.0, -s * 8, 2.2), (4.4, s * 22, 1.5), (3.0, s * 42, 0.8)], "bone")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 7.0), "dark", tag="under")
    a(c, C(0, 13.0, 3.55, 2.0, 10.4, 0.7), "bone", tag="sternum")
    for y in (14.0, 16.4, 18.8, 21.2):
        a(c, C(0, y, 3.55, 8.6, 1.3, 0.7), "bone", tag="rib_plate")
    k.fire(c, C(0, 15.8, 3.25, 7.4, 4.8, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.6), "bone", tag="belt")
    a(b, C(0, 13.0, -4.2, 3.0, 10.6, 2.4), "bone", tag="spine")
    for y in (14.0, 17.0, 20.0):
        a(b, C(0, y, -4.8, 5.0, 1.6, 2.4), "bone", tag="vertebra")
    for s in SIDES:
        for i, (y0, r0, l0) in enumerate(((22.4, 34, 13.0), (19.0, 44, 15.0), (15.6, 54, 15.0), (12.6, 64, 12.0))):
            k.horn(b, s * 1.6, y0, -5.4 - i * 0.3, [(l0 * 0.5, -s * r0, 2.8 - i * 0.2), (l0 * 0.4, -s * (r0 - 34), 2.2 - i * 0.2), (l0 * 0.32, -s * (r0 - 64), 1.6), (l0 * 0.24, -s * (r0 - 92), 0.9)], "bone")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.0, 0, 6.2, 6.0, 6.2), "bone", tag="vambrace")
        a(p, C(x, 16.2, 0, 6.6, 1.0, 6.6), "dark", tag="cuff")
        q = k.shoulder(s)
        a(q, C(x + s * 1.2, 20.5, 0, 8.4, 3.6, 9.0), "bone", tag="scapula")
        a(q, C(x + s * 1.2, 24.0, 0, 6.2, 1.2, 7.0), "bone", tag="scapula_top")
        k.spike(q, x + s * 3.6, 24.2, 2.6, 7.0, 2.8, "bone", rz=-s * 22, rx=-10, tag="shoulder_horn")
        k.spike(q, x + s * 3.6, 24.2, -2.6, 6.0, 2.4, "bone", rz=-s * 30, rx=12, tag="shoulder_horn")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.1, 9.6, 5.1), "bone", tag="cuisse")
        a(p, C(y, 4.6, 2.6, 4.2, 3.2, 1.2), "bone", tag="kneecap")
        a(p, C(y, 5.4, 3.25, 1.8, 1.4, 0.3), "void", tag="knee_hole")
    k.boots("bone", h=4.2, w=5.4, cuff="dark", toe="dark", toe_d=3.2)


# ---------------------------------------------------------------- the Jade Monastery

@design(cloth=ramp("#2a0c08", "#44140e", "#642014", "#882e1c", "#ac4228"), cloth2=ramp("#6a4410", "#8e5e16", "#b47c20", "#d8a030", "#f0c858"), dark=LACQUER, acc=JADE, gem=JADE, wrap=ramp("#6a4410", "#8e5e16", "#b47c20", "#d8a030"), leather=HIDE, wood=LACQUER, blade=JADE, fire=ramp("#a04808", "#d87810", "#f8ac28", "#ffd868", "#fff4b0", "#fffde8"), hot=ramp("#a04808", "#d87810", "#f8ac28"))
def incenserobe(k):
    """the master of ceremonies: a tall black lacquer court hat, a saffron kasaya over dark red, and coils of burning incense turning on a rack behind him, smoke lines up to the sky"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.2, 7.2, 9.4), "cloth", tag="head")
    a(h, C(0, 31.0, 0, 9.0, 3.0, 9.0), "dark", tag="lacquer_hat")
    a(h, C(0, 34.0, -1.4, 6.6, 7.0, 4.0), "dark", tag="lacquer_tall")
    a(h, C(0, 31.0, 4.5, 3.0, 2.4, 0.6), "gem", tag="hat_jade")
    for s in SIDES:
        a(h, C(s * 7.0, 33.2, -1.4, 7.0, 0.8, 1.6), "dark", tag="hat_wing")
        k.fire(h, C(s * 2.0, 27.4, 4.75, 1.0, 0.6, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 12.2, 2.75, 8.0, 11.8, 0.5), "cloth2", tag="kasaya", rots=(("z", 22),), pivot=(0, 18, 2.75))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 5.8), "dark", tag="sash")
    for i in range(10):
        r = math.radians(-70 + i * 15.5)
        a(c, C(math.sin(r) * 4.0, 22.2 - math.cos(r) * 7.0 + 2.0, 3.3, 1.2, 1.2, 1.0), "gem" if i == 4 or i == 5 else "wood", tag="bead")
    a(b, C(0, 13.0, -4.0, 1.4, 22.0, 1.4), "wood", tag="rack_post")
    a(b, C(0, 34.0, -4.0, 16.0, 1.0, 1.0), "wood", tag="rack_beam")
    a(b, C(0, 27.0, -4.0, 12.0, 0.9, 0.9), "wood", tag="rack_beam")
    for x, y, r in ((-6.6, 29.0, 3.8), (6.6, 29.0, 3.8), (0, 21.0, 4.4)):
        for rr, m in ((r, "wrap"), (r - 1.2, "void"), (r - 2.0, "wrap"), (r - 3.0, "void")):
            a(b, C(x, y - rr / 2 + 2.0, -4.0, rr, rr, 0.5), m, tag="coil")
        k.fire(b, C(x + r * 0.42, y + 1.8, -4.3, 0.7, 0.7, 0.3))
        a(b, C(x + r * 0.42, y + 2.4, -4.3, 0.3, 11.0, 0.3), "wrap", tag="smoke")
    k.arms("cloth", "cloth", cuff="cloth2", w=6.4, low_h=4.6)
    for s in SIDES:
        a(k.arm(s), C(s * 6.0, 9.6, 0, 7.0, 3.4, 7.0), "cloth", tag="wide_sleeve")
        a(k.arm(s), C(s * 6.0, 9.6, 0, 7.3, 0.8, 7.3), "cloth2", tag="wide_sleeve_hem")
        a(k.shoulder(s), C(s * 6.2, 21.0, 0, 5.6, 2.4, 5.6), "cloth2", tag="kasaya_shoulder")
    k.legs("cloth", w=4.6)
    k.boots("dark", h=3.2, w=4.8, toe="wrap", toe_d=2.2)


@design(blade=JADE, scale=JADE, wrap=REED, leather=LACQUER, cloth=ramp("#141008", "#241c10", "#382c1a", "#4e3e26"), acc=VERMILION, dark=LACQUER, wood=LACQUER, gem=GILT, gold=GILT, fire=JADEGLOW, hot=JADEGLOW)
def jadeguard(k):
    """a wandering lay guard: a wide conical straw hat, jade lamellar vest laced in red, a ringed monk's staff on the back that chimes as he walks"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.2, -0.2, 9.0, 7.2, 9.2), "cloth", tag="head")
    for w, y in ((18.0, 30.2), (14.4, 31.0), (11.0, 31.8), (7.8, 32.6), (4.8, 33.4), (2.0, 34.2)):
        a(h, C(0, y, 0, w, 0.9, w), "wrap", tag="straw_cone")
    a(h, C(0, 30.0, 0, 18.4, 0.5, 18.4), "dark", tag="cone_rim")
    a(h, C(0, 23.4, 4.4, 7.4, 3.0, 0.6), "acc", tag="face_cloth")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 28.0, 4.75, 1.0, 0.7, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.8), "cloth", tag="under")
    a(c, C(0, 13.6, 2.6, 8.4, 9.6, 0.5), "scale", tag="lamellar")
    for y in (15.4, 17.8, 20.2):
        a(c, C(0, y, 2.9, 8.4, 0.4, 0.3), "acc", tag="lacing")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 5.6), "acc", tag="sash")
    a(c, C(2.8, 5.0, 2.9, 2.0, 7.4, 0.5), "acc", tag="sash_end")
    a(c, C(-2.6, 9.4, 3.0, 1.8, 2.8, 0.7), "gem", tag="jade_token")
    a(b, C(0, 13.0, -3.0, 7.4, 10.0, 0.7), "scale", tag="back_lamellar")
    rz = (("z", -16),)
    a(b, C(0, 2.0, -3.8, 1.1, 38.0, 1.1), "wood", tag="staff", rots=rz, pivot=(0, 20, -3.8))
    a(b, C(0, 40.0, -3.8, 5.4, 6.0, 0.8), "gem", tag="staff_head", rots=rz, pivot=(0, 20, -3.8))
    a(b, C(0, 41.2, -3.8, 3.4, 3.8, 0.9), "void", tag="staff_head_hole", rots=rz, pivot=(0, 20, -3.8))
    for dx, dy in ((-3.2, 39.0), (3.2, 39.0), (-3.2, 41.6), (3.2, 41.6)):
        a(b, C(dx, dy, -3.8, 1.8, 1.8, 0.5), "gem", tag="staff_ring", rots=rz, pivot=(0, 20, -3.8))
    k.arms("cloth", "wrap", cuff="acc", w=5.0)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.3, 21.0, 0, 6.0, 2.4, 6.0), "scale", tag="shoulder_lamellar")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 6.2, 2.5, 3.8, 5.8, 0.5), "scale", tag="tasset")
        a(p, C(x, 2.0, 0, 4.8, 4.2, 4.8), "wrap", tag="shin_wrap")
        for y in (2.8, 4.4):
            a(p, C(x, y, 0, 5.1, 0.5, 5.1), "acc", tag="shin_tie")
    k.legs("cloth", w=4.6)
    k.boots("wrap", h=1.6, w=4.8, sole="wood")


@design(blade=JADE, stone=JADE, dark=LACQUER, acc=GILT, gold=GILT, mail=VERMILION, cloth=VERMILION, wrap=VERMILION, leather=HIDE, gem=GILT, fire=JADEGLOW, hot=JADEGLOW)
def lionward(k):
    """the gate lion come down from its plinth: a snarling foo-dog helm with a curled mane, a jade ball under each paw-pauldron"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.6, 0.4, 10.2, 9.0, 10.8), "blade", tag="lion_head")
    a(h, C(0, 24.0, 5.8, 8.0, 3.4, 2.6), "blade", tag="lion_muzzle")
    a(h, C(0, 26.8, 5.8, 3.4, 2.8, 2.8), "blade", tag="lion_nose")
    a(h, C(0, 28.2, 7.0, 2.2, 1.2, 0.8), "acc", tag="lion_nose_tip")
    a(h, C(0, 25.4, 7.05, 6.4, 0.9, 0.4), "void", tag="lion_mouth")
    for s in SIDES:
        a(h, C(s * 3.2, 29.0, 5.8, 2.6, 2.2, 0.6), "acc", tag="lion_eye")
        k.fire(h, C(s * 3.2, 29.4, 6.15, 1.4, 1.2, 0.3))
        k.spike(h, s * 2.6, 25.8, 7.0, -2.4, 1.2, "acc", tag="lion_fang", steps=2)
    for x, y, z, w in ((-5.8, 30.0, 0, 3.6), (5.8, 30.0, 0, 3.6), (-5.8, 26.0, 0, 3.6), (5.8, 26.0, 0, 3.6), (-3.0, 32.4, 0, 3.6), (3.0, 32.4, 0, 3.6), (0, 33.2, 0, 3.6), (-3.6, 32.0, -4.0, 3.6), (3.6, 32.0, -4.0, 3.6), (0, 30.0, -5.6, 4.0), (-5.0, 28.0, -4.0, 3.6), (5.0, 28.0, -4.0, 3.6)):
        a(h, C(x, y, z, w, w, w), "cloth", tag="mane_curl")
        a(h, C(x, y + w * 0.3, z + (w / 2 + 0.05 if z >= 0 else -w / 2 - 0.05), w * 0.45, w * 0.45, 0.3), "acc", tag="curl_eye")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.2), "blade", tag="cuirass")
    a(c, C(0, 13.4, 3.15, 6.6, 7.8, 0.5), "dark", tag="lion_plate")
    a(c, C(0, 14.6, 3.45, 4.0, 5.0, 0.4), "acc", tag="lion_plate_gold")
    a(c, C(0, 15.2, 3.65, 2.4, 3.2, 0.3), "void", tag="lion_mouth")
    k.fire(c, C(0, 15.6, 3.8, 1.4, 2.0, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 6.8), "mail", tag="sash")
    a(b, C(0, 13.0, -3.8, 7.6, 10.0, 1.4), "blade", tag="back_plate")
    a(b, C(0, 2.0, -4.0, 2.6, 11.0, 0.6), "cloth", tag="lion_tail", rots=(("x", 16),), pivot=(0, 13, -4.0))
    for t, (x, z) in enumerate(((0, -6.8), (-2.2, -6.4), (2.2, -6.4), (0, -8.4))):
        a(b, C(x, 0.6 + t % 2, z - 0.6, 3.0, 3.0, 2.8), "cloth", tag="tail_tuft")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "blade", tag="paw_gauntlet")
        a(p, C(x, 16.0, 0, 6.4, 1.2, 6.4), "cloth", tag="cuff_curl")
        for dx in (-1.8, 0, 1.8):
            a(p, C(x + dx, 10.6, 2.9, 1.4, 1.4, 1.2), "acc", tag="claw")
        q = k.shoulder(s)
        a(q, C(x + s * 1.4, 20.4, 0, 6.8, 6.8, 6.8), "stone", tag="jade_ball")
        a(q, C(x + s * 1.4, 21.6, 0, 7.6, 4.4, 7.6), "stone", tag="jade_ball")
        a(q, C(x + s * 1.4, 23.2, 0, 7.8, 0.6, 7.8), "dark", tag="ball_groove")
        a(q, C(x + s * 1.4, 26.8, 0, 7.2, 1.8, 7.8), "acc", tag="paw")
        for t in (-2.6, 0, 2.6):
            a(q, C(x + s * 1.4, 25.2, t + 1.0 * (1 if t > 0 else -1 if t < 0 else 0), 1.8, 2.4, 1.8), "acc", tag="paw_toe")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.0, 9.6, 5.0), "blade", tag="cuisse")
        a(p, C(y, 6.2, 2.6, 3.8, 5.8, 0.6), "mail", tag="tasset")
    k.boots("blade", h=4.0, w=5.2, cuff="cloth", toe="acc", toe_d=2.6)


@design(blade=VERMILION, wood=LACQUER, dark=LACQUER, acc=JADE, gem=JADE, gold=GILT, stone=JADE, mail=GILT, cloth=JADE, leather=HIDE, wrap=GILT, fire=JADEGLOW, hot=JADEGLOW)
def templeguard(k):
    """the monastery itself, walking: a helm under a little curved temple roof, the same tiled eaves stacked on his shoulders, red lacquer plate and a plaque of carved jade"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.2, 0, 10.0, 8.8, 10.0), "blade", tag="helm")
    a(h, C(0, 27.0, 4.9, 8.0, 0.9, 0.4), "void", tag="slit")
    k.fire(h, C(0, 27.2, 5.1, 6.4, 0.5, 0.3))
    a(h, C(0, 23.6, 5.0, 7.6, 3.0, 0.5), "acc", tag="jade_mask")
    for i, (w, y) in enumerate(((15.6, 32.2), (11.4, 33.4), (7.0, 34.6))):
        a(h, C(0, y, 0, w, 1.2, w), "stone", tag="roof_tile")
    a(h, C(0, 32.0, 0, 16.2, 0.6, 16.2), "wrap", tag="roof_eave")
    a(h, C(0, 35.8, 0, 3.0, 1.2, 3.0), "wrap", tag="roof_finial")
    k.spike(h, 0, 37.0, 0, 3.6, 1.4, "wrap", tag="roof_finial")
    for s in SIDES:
        for t in (-1, 1):
            k.spike(h, s * 7.8, 32.4, t * 7.8, 3.0, 1.6, "wrap", rz=-s * 22, rx=-t * 22, tag="eave_tip", steps=2)
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.4), "blade", tag="lacquer_cuirass")
    a(c, C(0, 14.4, 3.3, 5.6, 7.6, 0.6), "gem", tag="jade_plaque")
    a(c, C(0, 15.2, 3.65, 3.6, 6.0, 0.3), "dark", tag="plaque_carve")
    k.fire(c, C(0, 15.8, 3.85, 2.0, 4.8, 0.3))
    a(c, C(0, 22.6, 0, 8.7, 1.5, 7.0), "wrap", tag="gold_collar")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.0), "wrap", tag="belt")
    a(b, C(0, 13.0, -3.8, 7.6, 10.0, 1.6), "blade", tag="back_plate")
    a(b, C(0, 8.0, -3.6, 6.4, 15.0, 0.6), "cloth", tag="jade_tabard", rots=(("x", 8),), pivot=(0, 23, -3.6))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.4, 1.0, 6.4), "wrap", tag="cuff")
        q = k.shoulder(s)
        for i, (w, y) in enumerate(((10.4, 20.5), (8.0, 22.2), (5.6, 23.8))):
            a(q, C(x + s * 1.0, y, 0, w, 1.3, w + 0.6), "stone", tag="roof_tile")
            a(q, C(x + s * 1.0, y, 0, w + 0.5, 0.4, w + 1.1), "wrap", tag="roof_eave")
        for t in (-1, 1):
            k.spike(q, x + s * 5.8, 20.8, t * 5.6, 2.8, 1.4, "wrap", rz=-s * 28, rx=-t * 28, tag="eave_tip", steps=2)
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.1, 9.6, 5.1), "blade", tag="cuisse")
        a(p, C(y, 6.0, 2.6, 4.0, 6.0, 0.7), "gem", tag="tasset")
        a(p, C(y, 6.0, 2.95, 4.2, 0.6, 0.4), "wrap", tag="tasset_hem")
    k.boots("blade", h=4.0, w=5.2, cuff="wrap", toe="dark", toe_d=2.8)


# ---------------------------------------------------------------- the Storm Bastion

@design(cloth=STORM, wrap=ramp("#7a8aa0", "#9cacc0", "#bccada", "#dce4ee", "#f4f8fc"), acc=COPPER, blade=COPPER, dark=ramp("#0c1020", "#161c30", "#222c48"), gem=BOLT, leather=HIDE, fire=BOLT, hot=BOLT)
def stormcaller(k):
    """she calls it down on purpose: copper rods standing from a coil crown, glass jars of captured lightning on her back, a robe that never quite settles"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.4, 9.4, 7.8, 9.4), "cloth", tag="hood")
    a(h, C(0, 27.4, 4.4, 7.2, 3.0, 0.5), "void", tag="hood_dark")
    for s in SIDES:
        k.fire(h, C(s * 1.8, 28.4, 4.65, 1.0, 0.7, 0.3))
    for y in (31.6, 32.8, 34.0):
        a(h, C(0, y, 0, 10.6 - (y - 31.6), 0.8, 10.6 - (y - 31.6)), "acc", tag="coil_crown")
    for x, z, ln in ((0, 4.0, 13.0), (-4.0, 1.0, 11.0), (4.0, 1.0, 11.0), (-2.4, -3.4, 9.0), (2.4, -3.4, 9.0)):
        a(h, C(x, 31.4, z, 1.0, ln + 1.6, 1.0), "acc", tag="rod")
        a(h, C(x, 33.0 + ln, z, 1.8, 1.8, 1.8), "acc", tag="rod_ball")
        k.fire(h, C(x, 33.0 + ln + 1.8, z, 0.7, 2.2, 0.7), rots=(("z", 14),), pivot=(x, 33 + ln, z))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 12.2, 2.75, 3.0, 11.8, 0.5), "wrap", tag="stole")
    for x, y, r in ((0.3, 19.0, 20), (-0.4, 15.6, -20), (0.3, 12.6, 20)):
        k.fire(c, C(x, y, 3.05, 0.9, 3.8, 0.3), rots=(("z", r),), pivot=(x, y, 3.05))
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.8), "acc", tag="copper_belt")
    for x, w in ((-2.8, 3.6), (2.8, 3.6)):
        a(b, C(x, 12.4, -5.4, w + 0.6, 1.2, w + 0.6), "acc", tag="jar_base")
        a(b, C(x, 13.6, -5.4, w, 8.0, w), "gem", tag="lightning_jar")
        a(b, C(x, 15.0, -5.4, w - 1.8, 5.0, w + 0.2), "glow", group="fire", tag="caught_bolt")
        a(b, C(x, 21.6, -5.4, w + 0.6, 1.2, w + 0.6), "acc", tag="jar_cap")
        a(b, C(x, 22.8, -5.4, 0.9, 5.0, 0.9), "acc", tag="jar_rod")
    a(b, C(0, 24.0, -5.4, 7.0, 0.9, 0.9), "acc", tag="jar_link")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "cloth", tag="sleeve")
        k.elbow(s, "cloth")
        a(p, C(x, 11.0, 0, 6.0, 5.6, 6.0), "cloth", tag="flare")
        for y in (12.0, 13.4, 14.8):
            a(p, C(x, y, 0, 6.3, 0.6, 6.3), "acc", tag="wrist_coil")
        q = k.shoulder(s)
        a(q, C(x + s * 0.3, 21.0, 0, 5.8, 2.6, 5.8), "wrap", tag="mantle")
        a(q, C(x + s * 1.6, 23.6, 0, 0.9, 5.4, 0.9), "acc", tag="rod")
        a(q, C(x + s * 1.6, 29.0, 0, 1.5, 1.5, 1.5), "acc", tag="rod_ball")
    k.legs("cloth", w=4.6)
    k.boots("acc", h=2.8, w=4.8, sole="dark")


@design(leather=STORM, cloth=ramp("#7a8aa0", "#9cacc0", "#bccada", "#dce4ee", "#f4f8fc"), wrap=ramp("#1a3a9c", "#2850c0", "#3c70e0", "#6c98f4"), acc=COPPER, dark=ramp("#0c1020", "#161c30", "#222c48"), blade=STEEL, feather=ramp("#7a8aa0", "#9cacc0", "#bccada", "#dce4ee", "#f4f8fc"), gem=BOLT, fire=BOLT, hot=BOLT)
def galerunner(k):
    """always running ahead of the front: a copper weathervane on the helm, long blue scarves blown out behind, little wings at the heels"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.2, -0.2, 9.0, 7.8, 9.2), "leather", tag="hood")
    a(h, C(0, 26.8, 4.1, 8.0, 3.2, 1.2), "acc", tag="flying_goggles")
    for s in SIDES:
        a(h, C(s * 2.2, 27.0, 4.75, 3.0, 2.8, 0.4), "dark", tag="lens_rim")
        k.fire(h, C(s * 2.2, 27.5, 4.95, 2.0, 1.8, 0.3))
    a(h, C(0, 22.6, 0.2, 10.0, 3.6, 10.0), "wrap", tag="scarf")
    a(h, C(0, 32.0, 0, 3.0, 1.2, 3.0), "acc", tag="vane_base")
    a(h, C(0, 33.2, 0, 0.9, 7.4, 0.9), "acc", tag="vane_rod")
    a(h, C(0, 36.0, 0, 8.0, 0.5, 0.5), "acc", tag="vane_cross")
    a(h, C(0, 36.0, 0, 0.5, 0.5, 8.0), "acc", tag="vane_cross")
    a(h, C(0, 38.6, 1.6, 0.5, 0.7, 11.0), "acc", tag="vane_arrow")
    a(h, C(0, 38.0, 7.2, 0.5, 1.8, 1.8), "acc", tag="vane_arrow_head")
    a(h, C(0, 37.4, -4.4, 0.5, 3.2, 2.6), "acc", tag="vane_tail")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.8), "leather", tag="jerkin")
    a(c, C(0, 20.8, 0, 8.7, 3.2, 5.8), "wrap", tag="scarf_turn")
    for y in (14.6, 16.8, 19.0):
        a(c, C(0, y, 2.6, 7.6, 0.7, 0.4), "cloth", tag="strap")
    k.fire(c, C(0, 16.8, 2.85, 1.2, 1.2, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.6), "acc", tag="belt")
    for i, (x, y, ln, r, m) in enumerate(((-2.4, 22.6, 22.0, 58, "wrap"), (2.0, 21.6, 24.0, 66, "wrap"), (0, 20.6, 18.0, 72, "cloth"))):
        a(b, C(x, y - ln, -3.2, 2.2, ln, 0.5), m, tag="scarf_tail", rots=(("x", r), ("z", x * 2)), pivot=(x, y, -3.2))
    k.arms("leather", "cloth", cuff="acc", w=5.0)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.2, 21.2, 0, 5.4, 2.2, 5.4), "cloth", tag="cop")
        for i in range(3):
            a(k.arm(s), C(s * 8.6, 16.0 - i * 2.0, 0, 0.5, 3.0, 3.4 + i * 0.6), "feather", tag="arm_vane")
    k.legs("leather", w=4.6)
    for s in SIDES:
        p, x = k.boot(s), s * 1.95
        for i, (t, ln) in enumerate(((10, 6.0), (30, 5.0), (52, 4.0))):
            a(p, C(x + s * 2.9, 2.0, -1.4, 0.5, ln, 1.4), "feather", tag="heel_wing", rots=(("x", 62 - i * 22 + 20),), pivot=(x + s * 2.9, 2.0, -1.4))
    k.boots("leather", h=3.6, w=4.8, cuff="acc")


@design(stone=GRANITE, blade=GRANITE, dark=ramp("#0c1020", "#161c30", "#222c48", "#303c5c"), mail=STEEL, acc=COPPER, cloth=ramp("#0e2a6a", "#1a3e92", "#2858bc", "#4078dc"), leather=HIDE, wood=OAK, gem=BOLT, fire=BOLT, hot=BOLT)
def bastionmail(k):
    """the wall that holds the sea wind: a keep for a helm with a pennant flying, round bastion towers on the shoulders with their arrow slits lit"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.2, 0, 10.0, 9.6, 10.0), "stone", tag="keep")
    a(h, C(0, 32.8, 0, 11.4, 1.4, 11.4), "stone", tag="keep_head")
    for t in range(4):
        for u in (-4.0, 0, 4.0):
            a(h, C(u, 34.2, 5.0, 2.2, 1.8, 1.4), "stone", tag="merlon", rots=(("y", t * 90),), pivot=(0, 34, 0))
    a(h, C(0, 27.0, 5.05, 8.0, 0.9, 0.3), "void", tag="slit")
    k.fire(h, C(0, 27.2, 5.2, 6.4, 0.5, 0.3))
    a(h, C(-2.4, 34.4, -2.4, 0.7, 11.0, 0.7), "wood", tag="flagpole")
    a(h, C(1.4, 40.6, -2.4, 7.0, 3.4, 0.4), "cloth", tag="pennant", rots=(("y", -8),), pivot=(-2.4, 42, -2.4))
    k.spike(h, 5.0, 41.4, -2.9, 2.4, 2.8, "cloth", rz=-90, steps=2, tag="pennant_tail")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.4), "stone", tag="wall_breast")
    for y in (14.6, 17.0, 19.4, 21.8):
        a(c, C(0, y, 3.25, 8.7, 0.4, 0.4), "dark", tag="mortar")
    for x, y in ((-2.0, 13.0), (2.0, 15.4), (-2.0, 17.8), (2.0, 20.2)):
        a(c, C(x, y, 3.25, 0.4, 1.8, 0.4), "dark", tag="mortar")
    a(c, C(0, 15.4, 3.4, 3.6, 4.6, 0.5), "dark", tag="portcullis_arch")
    k.fire(c, C(0, 15.8, 3.65, 2.4, 3.4, 0.3))
    for x in (-1.0, 0, 1.0):
        a(c, C(x, 15.6, 3.85, 0.4, 3.8, 0.3), "void", tag="portcullis_bar")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.0), "dark", tag="belt")
    a(b, C(0, 13.0, -3.8, 7.8, 10.4, 1.6), "stone", tag="back_wall")
    a(b, C(0, 6.0, -3.8, 6.0, 17.0, 0.6), "cloth", tag="banner", rots=(("x", 8),), pivot=(0, 23, -3.8))
    a(b, C(0, 13.0, -5.0, 2.8, 4.8, 0.3), "acc", tag="banner_bolt", rots=(("x", 8),), pivot=(0, 23, -3.8))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "stone", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.4, 1.0, 6.4), "dark", tag="cuff")
        q = k.shoulder(s)
        a(q, C(x + s * 1.2, 20.5, 0, 7.8, 7.4, 7.8), "stone", tag="bastion_tower")
        a(q, C(x + s * 1.2, 21.4, 0, 8.6, 5.6, 8.6), "stone", tag="bastion_tower")
        a(q, C(x + s * 1.2, 27.8, 0, 9.4, 1.2, 9.4), "stone", tag="tower_head")
        for t in range(4):
            for u in (-3.2, 3.2):
                a(q, C(x + s * 1.2 + u, 29.0, 4.0, 2.0, 1.6, 1.2), "stone", tag="merlon", rots=(("y", t * 90),), pivot=(x + s * 1.2, 29, 0))
        a(q, C(x + s * 1.2, 23.0, 4.35, 1.0, 3.0, 0.3), "void", tag="arrow_slit")
        k.fire(q, C(x + s * 1.2, 23.4, 4.5, 0.5, 2.2, 0.3))
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.1, 9.6, 5.1), "stone", tag="cuisse")
        a(p, C(y, 6.8, 2.6, 4.2, 0.4, 0.4), "dark", tag="mortar")
        a(p, C(y, 3.6, 2.6, 4.2, 0.4, 0.4), "dark", tag="mortar")
    k.boots("stone", h=4.2, w=5.4, cuff="dark", sole="dark")


@design(blade=ramp("#0e1430", "#18224c", "#26346e", "#384c94", "#5470c0", "#8ca8e8"), dark=ramp("#0c1020", "#161c30", "#222c48", "#303c5c"), acc=COPPER, wood=ramp("#3a1608", "#60280e", "#8a3e18", "#b45824"), wrap=ramp("#7a8aa0", "#9cacc0", "#bccada", "#dce4ee", "#f4f8fc"), mail=STEEL, gem=BOLT, cloth=STORM, leather=HIDE, fire=BOLT, hot=BOLT)
def stormhelm(k):
    """the thunder itself in armour: lightning bolts for horns and a great ring of war drums standing behind him, each with a spark on its skin"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.0, 0, 10.4, 9.2, 10.4), "blade", tag="helm")
    a(h, C(0, 27.0, 5.05, 8.4, 0.9, 0.4), "void", tag="slit")
    k.fire(h, C(0, 27.2, 5.25, 6.8, 0.5, 0.3))
    a(h, C(0, 23.2, 5.1, 3.0, 3.6, 0.7), "acc", tag="nasal")
    a(h, C(0, 31.6, 0, 11.4, 1.3, 11.4), "acc", tag="brow")
    a(h, C(0, 33.0, 0, 7.0, 1.0, 7.0), "dark", tag="helm_cap")
    for s in SIDES:
        bx, by = s * 5.2, 31.4
        for (l, r) in ((5.4, -s * 34), (4.2, s * 24), (6.0, -s * 40), (3.4, s * 18)):
            a(h, C(bx, by, 0, 1.8, l, 1.8), "glow", group="fire", tag="bolt_horn", rots=(("z", r),), pivot=(bx, by, 0))
            t = math.radians(r)
            bx, by = bx - math.sin(t) * l, by + math.cos(t) * l
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.6), "blade", tag="cuirass")
    for x, y, w, ht, r in ((0.6, 19.0, 1.6, 4.6, 24), (-0.6, 15.8, 1.6, 4.4, -24), (0.6, 12.8, 1.4, 3.4, 24)):
        k.fire(c, C(x, y, 3.35, w, ht, 0.3), rots=(("z", r),), pivot=(x, y, 3.35))
    a(c, C(0, 22.6, 0, 8.7, 1.5, 7.2), "acc", tag="collar")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.2), "acc", tag="belt")
    a(b, C(0, 13.0, -3.8, 7.6, 10.4, 1.6), "blade", tag="back_plate")
    for i in range(8):
        r = math.radians(22.5 + i * 45)
        x, y = math.sin(r) * 12.0, 26.0 + math.cos(r) * 12.0
        a(b, C(x, y - 2.6, -6.4, 5.6, 5.2, 2.4), "wood", tag="thunder_drum")
        a(b, C(x, y - 2.0, -6.4, 5.9, 0.5, 2.7), "acc", tag="drum_band")
        a(b, C(x, y + 1.4, -6.4, 5.9, 0.5, 2.7), "acc", tag="drum_band")
        a(b, C(x, y - 1.8, -5.1, 4.4, 3.8, 0.3), "wrap", tag="drum_skin")
        a(b, C(x, y - 1.8, -7.7, 4.4, 3.8, 0.3), "wrap", tag="drum_skin")
        a(b, C(x, y - 1.2, -7.9, 1.6, 2.6, 0.3), "glow", group="fire", tag="drum_spark")
        a(b, C(x, y - 1.2, -4.95, 1.6, 2.6, 0.3), "glow", tag="drum_spark")
    for i in range(16):
        r = math.radians(i * 22.5)
        x, y = math.sin(r) * 12.0, 26.0 + math.cos(r) * 12.0
        a(b, C(x, y - 0.5, -6.4, 3.4, 1.0, 1.0), "acc", tag="drum_ring", rots=(("z", -i * 22.5 - 90),), pivot=(x, y, -6.4))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.4, 1.0, 6.4), "acc", tag="cuff")
        k.fire(p, C(x, 12.6, 3.1, 1.0, 2.6, 0.3), rots=(("z", 22),), pivot=(x, 13, 3.1))
        q = k.shoulder(s)
        a(q, C(x + s * 1.2, 20.5, 0, 8.4, 4.0, 8.6), "blade", tag="pauldron")
        a(q, C(x + s * 1.2, 24.4, 0, 6.8, 1.0, 7.0), "acc", tag="pauldron_top")
        k.fire(q, C(x + s * 1.2, 21.6, 4.35, 1.2, 2.4, 0.3), rots=(("z", 22),), pivot=(x, 22, 4.35))
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.1, 9.6, 5.1), "blade", tag="cuisse")
        a(p, C(y, 4.6, 2.6, 4.0, 3.0, 1.0), "acc", tag="poleyn")
    k.boots("blade", h=4.2, w=5.2, cuff="acc", toe="dark", toe_d=2.8)
