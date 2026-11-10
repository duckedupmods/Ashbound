"""The Bloodmoon Court, the Obsidian Labyrinth, the Abyssal Lighthouse, the Eclipse Cathedral, the Wyrm's Hoard, the Clockwork
Spire, the Coiled Spire, Rimeholt, the Glass Minaret and the Warlord's Fang (see armorsets.py for the units and the fit rules)."""
import math

from armorsets import BRASS, C, IRON, SIDES, design, ramp
from armorsets_a import BLACK, HEMP, OAK
from armorsets_b import BONE, GILT, HIDE, PALE
from armorsets_c import ICE, RAVEN, STEEL
from armorsets_d import BOLT, COPPER

NIGHT = ramp("#0a0810", "#14101c", "#201a2c", "#2e2640", "#403656")
GORE = ramp("#2a0408", "#4a0810", "#6e0e18", "#961824", "#c02a34", "#e8505a")
BLOODMOON = ramp("#6a0810", "#a01018", "#d01c24", "#f04438", "#ff8868", "#ffd0b0")
BASALT = ramp("#0c0c10", "#18181e", "#26262e", "#363640", "#4a4a56", "#666672")
EMBERS = ramp("#7a1a04", "#b03006", "#e0540c", "#f88820", "#ffc050", "#fff0b0")
TERRACOTTA = ramp("#3a180c", "#5a2614", "#7e3a1e", "#a4522c", "#c87040")
ABYSS = ramp("#04081a", "#0a1230", "#121e48", "#1c2e66", "#2c4488")
WATCHGLOW = ramp("#0a5a7a", "#1088a8", "#24b4cc", "#58dce4", "#a8f4f0", "#e8fffa")
WHITEWASH = ramp("#8a8e94", "#aeb2b8", "#ccd0d4", "#e4e6e8", "#f6f6f6")
ASH = ramp("#26262a", "#3a3a40", "#52525a", "#6e6e76", "#92929a", "#bcbcc2")
CORONA = ramp("#b04a08", "#e07c10", "#f8b028", "#ffd860", "#fff0a0", "#ffffff")
VOIDGOLD = ramp("#2a1c06", "#4a3208", "#70500e", "#9c741a", "#c89c30", "#ecc860")
WYRM = ramp("#2a0806", "#46100a", "#681a10", "#8e2818", "#b83e24", "#dc6438")
WYRMFIRE = ramp("#b01c04", "#e04808", "#f87c10", "#ffb024", "#ffe060", "#fff8c0")
CLOCK = ramp("#3a2008", "#5e3810", "#8a581c", "#b47e30", "#dcaa50", "#f6d88c")
STEAM = ramp("#4a7a80", "#6ea0a4", "#98c4c4", "#c0e0dc", "#e4f6f0", "#ffffff")
SERPENT = ramp("#0a2a18", "#124226", "#1c5e36", "#2a7e4a", "#3ea262", "#60c684")
VENOM = ramp("#2e6a08", "#4e9a0c", "#7cc818", "#b0ec38", "#dcfa80", "#f8ffd0")
JAGUAR = ramp("#4a2c08", "#74480e", "#a06a18", "#c88e28", "#e8b440", "#f8d878")
QUETZAL = ramp("#04382e", "#085a48", "#0e8466", "#1cb088", "#40d8a8", "#90f4cc")
NORSEFUR = ramp("#1e1610", "#32261c", "#4a3a2c", "#665240", "#866e58", "#aa9078")
RUNE = ramp("#1a4a9a", "#2c74d0", "#4ca4f0", "#84d0fc", "#c0f0ff", "#f0ffff")
TURQUOISE = ramp("#0a4a50", "#106c70", "#189494", "#30bcb4", "#68dcd0", "#b0f4e8")
MIRROR = ramp("#3a4a5a", "#5a7084", "#84a0b4", "#b4ccdc", "#dcecf4", "#ffffff")
SUNFIRE = ramp("#c05006", "#e88010", "#fcb024", "#ffd85c", "#fff4a0", "#ffffe8")
ROYAL = ramp("#3a0a4e", "#561470", "#762096", "#9a34bc", "#c05ce0")
RUST = ramp("#2a120a", "#44200e", "#623014", "#84461e", "#a8602c")
FURY = ramp("#6a0a04", "#a01208", "#d42410", "#f44c1c", "#ff8c40", "#ffd090")
GREEN_HIDE = ramp("#1e2a12", "#2e401a", "#425a24", "#587630", "#749440")


# ---------------------------------------------------------------- the Bloodmoon Court

@design(cloth=NIGHT, cloth2=GORE, wrap=GORE, dark=BLACK, acc=GILT, gem=GORE, leather=NIGHT, blade=GILT, fire=BLOODMOON, hot=BLOODMOON)
def sanguine(k):
    """the Countess's cupbearer: a collar standing higher than the head, a red chalice held at the belt, bat wings folded into a cape"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.2, -0.2, 9.0, 7.6, 9.2), "cloth", tag="cowl")
    a(h, C(0, 27.4, 4.45, 6.8, 2.6, 0.4), "void", tag="shadow")
    for s in SIDES:
        k.fire(h, C(s * 1.8, 28.2, 4.65, 1.0, 0.7, 0.3))
        a(h, C(s * 5.2, 22.4, 1.2, 0.8, 15.0, 7.6), "cloth2", tag="high_collar", rots=(("z", -s * 16),), pivot=(s * 5.2, 22.4, 1.2))
        a(h, C(s * 7.2, 36.2, 1.2, 1.0, 1.6, 7.8), "acc", tag="collar_tip")
    a(h, C(0, 22.4, -3.8, 12.0, 14.0, 0.8), "cloth2", tag="high_collar_back", rots=(("x", 8),), pivot=(0, 22.4, -3.8))
    a(h, C(0, 31.6, 4.4, 2.4, 1.6, 0.5), "gem", tag="brow_jewel")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 12.2, 2.75, 3.0, 11.8, 0.5), "cloth2", tag="stole")
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.8), "acc", tag="belt")
    a(c, C(0, 6.0, 3.6, 3.4, 2.4, 3.2), "acc", tag="chalice_cup")
    k.fire(c, C(0, 8.4, 3.6, 2.6, 0.5, 2.4))
    a(c, C(0, 3.6, 3.6, 1.0, 2.4, 1.0), "acc", tag="chalice_stem")
    for s in SIDES:
        for i, (ln, r) in enumerate(((20.0, 3), (19.0, 11), (16.0, 20))):
            a(b, C(s * (1.6 + i * 2.2), 23.0 - ln, -3.4 - i * 0.2, 2.6, ln, 0.6), "cloth", tag="bat_wing_panel", rots=(("x", 7), ("z", s * r)), pivot=(s * (1.6 + i * 2.2), 23, -3.4))
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "cloth", tag="sleeve")
        k.elbow(s, "cloth")
        a(p, C(x, 10.6, 0, 6.4, 6.0, 6.4), "cloth", tag="flare")
        a(p, C(x, 10.6, 0, 6.7, 0.9, 6.7), "cloth2", tag="hem")
        a(k.shoulder(s), C(x + s * 0.3, 21.0, 0, 5.8, 2.6, 5.8), "cloth2", tag="mantle")
    k.legs("cloth", w=4.6)
    k.boots("dark", h=2.8, w=4.8, toe="dark", toe_d=3.0)


@design(leather=GORE, cloth=NIGHT, wrap=PALE, dark=BLACK, acc=GILT, blade=STEEL, feather=PALE, fire=BLOODMOON, hot=BLOODMOON)
def fencer(k):
    """a duellist of the Court: a wide hat swept up with a long white plume, a lace ruff, a short cape over one shoulder and a basket-hilted rapier"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.2, -0.2, 9.0, 7.0, 9.2), "cloth", tag="head")
    a(h, C(0, 31.0, 0, 14.6, 0.8, 14.0), "leather", tag="hat_brim")
    a(h, C(-5.0, 31.4, 0, 4.2, 3.6, 13.6), "leather", tag="hat_swept", rots=(("z", 52),), pivot=(-3, 31, 0))
    a(h, C(0, 31.6, 0, 8.4, 3.4, 8.4), "leather", tag="hat_crown")
    a(h, C(0, 31.6, 0, 8.7, 0.9, 8.7), "acc", tag="hat_band")
    k.horn(h, 3.6, 33.4, 3.0, [(5.0, 58, 3.0), (5.0, 92, 2.6), (5.0, 124, 2.0), (3.6, 150, 1.2)], "feather")
    a(h, C(0, 27.2, 4.45, 7.4, 2.2, 0.5), "dark", tag="eye_mask")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 27.8, 4.75, 1.0, 0.7, 0.3))
    a(h, C(0, 24.0, 4.45, 1.6, 1.8, 0.5), "dark", tag="goatee")
    a(h, C(0, 22.4, 0, 12.6, 1.6, 12.6), "wrap", tag="ruff")
    for t in range(4):
        a(h, C(0, 22.6, 0, 13.2, 1.2, 1.6), "wrap", tag="ruff_pleat", rots=(("y", t * 45),), pivot=(0, 23, 0))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.8), "leather", tag="doublet")
    a(c, C(0, 13.0, 2.65, 3.0, 11.0, 0.4), "cloth", tag="placket")
    for y in (14.2, 16.0, 17.8, 19.6, 21.4):
        a(c, C(0, y, 2.9, 0.8, 0.8, 0.4), "acc", tag="button")
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.6), "dark", tag="belt")
    a(c, C(-4.1, -1.0, 1.0, 0.7, 13.4, 0.7), "blade", tag="rapier_blade", rots=(("x", -14),), pivot=(-4.1, 12, 1.0))
    a(c, C(-4.1, 12.2, 1.0, 3.0, 2.6, 3.0), "acc", tag="basket_hilt")
    a(c, C(-4.1, 14.8, 1.0, 1.2, 1.2, 1.2), "acc", tag="pommel")
    a(b, C(2.2, 12.0, -3.2, 6.6, 11.6, 0.6), "cloth", tag="short_cape", rots=(("x", 5),), pivot=(2.2, 23.6, -3.2))
    a(b, C(2.2, 11.6, -3.6, 6.8, 1.0, 0.7), "acc", tag="cape_hem", rots=(("x", 5),), pivot=(2.2, 23.6, -3.2))
    a(k.shoulder(1), C(6.8, 19.0, 0, 7.0, 5.4, 7.0), "cloth", tag="shoulder_cape")
    a(k.shoulder(1), C(6.8, 19.0, 0, 7.2, 0.8, 7.2), "acc", tag="cape_hem")
    a(k.shoulder(-1), C(-6.2, 21.2, 0, 5.4, 2.0, 5.4), "leather", tag="puff")
    k.arms("leather", "cloth", cuff="wrap", w=5.0)
    for s in SIDES:
        for dz in (-1.6, 0, 1.6):
            a(k.arm(s), C(s * 6.0 + dz, 18.6, 2.65, 0.4, 3.4, 0.3), "wrap", tag="slash")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 6.4, 0, 5.2, 5.6, 5.2), "leather", tag="breeches")
        a(p, C(x, 6.4, 2.65, 0.9, 5.6, 0.3), "wrap", tag="slash")
    k.legs("cloth", w=4.5)
    k.boots("dark", h=6.2, w=5.0, cuff="leather", toe="dark", toe_d=2.4)


@design(cloth=GORE, cloth2=NIGHT, wrap=WHITEWASH, acc=GILT, gold=GILT, dark=BLACK, mail=GILT, leather=GORE, blade=GILT, gem=BLOODMOON, wood=NIGHT, fire=BLOODMOON, hot=BLOODMOON)
def courtier(k):
    """the Countess's favourite: a towering powdered wig with a tiny bat in it, a mask on a stick, a coat so stiff with gold that it passes for armour"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.4, 9.6, 8.0, 9.6), "wrap", tag="wig_sides")
    for s in SIDES:
        for y in (25.0, 27.6):
            a(h, C(s * 5.2, y, 0, 2.2, 2.4, 7.0), "wrap", tag="wig_roll")
    a(h, C(0, 32.0, -0.4, 9.0, 3.6, 9.0), "wrap", tag="wig_tower")
    a(h, C(0, 35.6, -0.4, 7.4, 3.6, 7.4), "wrap", tag="wig_tower")
    a(h, C(0, 39.2, -0.4, 5.4, 3.0, 5.4), "wrap", tag="wig_tower")
    a(h, C(0, 42.2, -0.4, 3.0, 2.0, 3.0), "wrap", tag="wig_tower")
    for y in (34.6, 38.0, 41.4):
        a(h, C(0, y, -0.4, 9.2 - (y - 34) * 0.6, 0.5, 9.2 - (y - 34) * 0.6), "cloth", tag="wig_ribbon")
    a(h, C(0, 44.0, -0.4, 2.0, 1.4, 1.4), "cloth2", tag="wig_bat")
    for s in SIDES:
        a(h, C(s * 2.2, 44.4, -0.4, 2.8, 1.2, 0.6), "cloth2", tag="wig_bat_wing", rots=(("z", -s * 18),), pivot=(s, 44.8, -0.4))
    a(h, C(0, 24.4, 4.45, 7.2, 6.4, 0.5), "wrap", tag="powdered_face")
    a(h, C(0, 27.2, 4.75, 7.6, 2.6, 0.4), "acc", tag="domino")
    for s in SIDES:
        a(h, C(s * 2.0, 27.8, 4.95, 1.6, 1.0, 0.3), "void", tag="eye")
        k.fire(h, C(s * 2.0, 28.0, 5.05, 0.9, 0.6, 0.3))
    a(h, C(4.8, 21.4, 4.75, 0.5, 6.0, 0.5), "acc", tag="mask_stick")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.6), "cloth", tag="brocade_coat")
    a(c, C(0, 12.2, 3.05, 3.8, 11.0, 0.4), "wrap", tag="waistcoat")
    for s in SIDES:
        a(c, C(s * 3.2, 12.4, 3.05, 1.4, 11.0, 0.5), "acc", tag="gold_edge")
        for y in (14.0, 17.0, 20.0):
            a(c, C(s * 2.4, y, 3.25, 1.2, 1.2, 0.4), "gem", tag="ruby_button")
    a(c, C(0, 21.8, 3.2, 3.0, 2.2, 0.5), "wrap", tag="jabot")
    a(c, C(0, 12.2, 0, 8.7, 1.3, 6.2), "acc", tag="belt")
    for s in SIDES:
        a(b, C(s * 2.2, 3.0, -3.4, 4.0, 20.0, 0.8), "cloth", tag="coat_skirt", rots=(("x", 10), ("z", -s * 8)), pivot=(s * 2.2, 23, -3.4))
        a(b, C(s * 2.2, 3.0, -4.3, 4.2, 1.0, 0.5), "acc", tag="coat_hem", rots=(("x", 10), ("z", -s * 8)), pivot=(s * 2.2, 23, -3.4))
    for t in range(9):
        a(b, C(0, 20.0, -4.8, 2.0, 15.0, 0.5), "cloth2" if t % 2 else "acc", tag="great_fan", rots=(("z", -72 + t * 18),), pivot=(0, 20.0, -4.8))
    k.arms("cloth", "cloth", cuff="wrap", w=5.4)
    for s in SIDES:
        a(k.arm(s), C(s * 6.0, 15.0, 0, 6.2, 2.6, 6.2), "acc", tag="great_cuff")
        q = k.shoulder(s)
        a(q, C(s * 6.3, 20.8, 0, 6.2, 2.8, 6.4), "cloth", tag="shoulder")
        for t in (-2.2, 0, 2.2):
            a(q, C(s * 9.6, 18.4, t, 0.6, 3.4, 0.6), "acc", tag="bullion")
    k.legs("wrap", w=4.6)
    k.boots("cloth2", h=2.4, w=4.8, toe="acc", toe_d=2.0)


@design(blade=ramp("#0c0a14", "#1a1626", "#2a2438", "#3e3650", "#5a4e70", "#847ca0"), dark=BLACK, acc=GORE, mail=NIGHT, cloth=GORE, leather=NIGHT, gem=BLOODMOON, wrap=GORE, fire=BLOODMOON, hot=BLOODMOON)
def nightguard(k):
    """the Court's knight of the watch: a bat-eared helm with a crescent standing on it, the red moon on the breast, plated wings folded at the back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.0, 0, 10.2, 9.4, 10.2), "blade", tag="helm")
    a(h, C(0, 24.4, 5.0, 3.2, 3.6, 2.4), "blade", tag="snout")
    a(h, C(0, 25.0, 6.25, 1.8, 1.2, 0.3), "void", tag="nostrils")
    a(h, C(0, 28.0, 5.0, 8.4, 1.0, 0.4), "void", tag="slit")
    k.fire(h, C(0, 28.2, 5.2, 6.8, 0.5, 0.3))
    for s in SIDES:
        a(h, C(s * 4.4, 32.4, 0, 3.2, 8.4, 1.4), "blade", tag="bat_ear", rots=(("z", -s * 16),), pivot=(s * 4.4, 32.4, 0))
        a(h, C(s * 4.4, 33.4, 0.75, 1.6, 5.0, 0.3), "acc", tag="ear_inner", rots=(("z", -s * 16),), pivot=(s * 4.4, 32.4, 0))
    for t in range(9):
        r = math.radians(-96 + t * 24)
        x, y = math.sin(r) * 4.6, 37.0 + math.cos(r) * -4.6 + 2.0
        a(h, C(x, y, 0, 1.8 - abs(t - 4) * 0.25, 1.8, 1.2), "blade", tag="crescent")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.4), "blade", tag="cuirass")
    a(c, C(0, 14.0, 3.3, 7.0, 7.0, 0.5), "dark", tag="moon_field")
    a(c, C(0, 15.0, 3.55, 5.0, 5.0, 0.4), "acc", tag="red_moon")
    k.fire(c, C(0, 15.6, 3.8, 3.8, 3.8, 0.3))
    a(c, C(1.0, 16.0, 4.0, 2.6, 2.6, 0.3), "dark", tag="moon_bite")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.0), "dark", tag="belt")
    a(b, C(0, 13.0, -3.8, 7.6, 10.4, 1.6), "blade", tag="back_plate")
    for s in SIDES:
        a(b, C(s * 3.0, 21.0, -4.8, 2.0, 11.0, 1.4), "blade", tag="wing_arm", rots=(("z", -s * 30),), pivot=(s * 3, 21, -4.8))
        tx, ty = s * (3.0 + math.sin(math.radians(30)) * 11), 21 + math.cos(math.radians(30)) * 11
        k.spike(b, tx, ty, -4.8, 4.0, 1.6, "blade", rz=-s * 14, tag="wing_thumb")
        for i, (r, ln) in enumerate(((172, 24.0), (158, 21.0), (144, 17.0))):
            a(b, C(tx, ty, -5.0, 1.0, ln, 0.8), "blade", tag="wing_finger", rots=(("z", -s * r),), pivot=(tx, ty, -5.0))
        a(b, C(s * 7.0, 8.0, -5.0, 6.4, 15.0, 0.5), "acc", tag="wing_web")
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.4, 1.0, 6.4), "acc", tag="cuff")
        k.spike(p, x + s * 2.8, 13.0, 0, 3.0, 1.6, "blade", rz=-s * 74)
        q = k.shoulder(s)
        a(q, C(x + s * 1.2, 20.5, 0, 8.0, 3.6, 8.4), "blade", tag="pauldron")
        a(q, C(x + s * 1.2, 24.0, 0, 6.2, 0.9, 6.6), "acc", tag="pauldron_top")
        k.spike(q, x + s * 3.0, 24.4, 0, 5.4, 2.6, "blade", rz=-s * 26)
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.1, 9.6, 5.1), "blade", tag="cuisse")
        a(p, C(y, 4.6, 2.6, 4.0, 3.0, 1.0), "acc", tag="poleyn")
    k.boots("blade", h=4.2, w=5.2, cuff="dark", toe="dark", toe_d=3.2)


# ---------------------------------------------------------------- the Obsidian Labyrinth

@design(cloth=TERRACOTTA, wrap=PALE, dark=BLACK, gem=BASALT, acc=GILT, leather=HIDE, blade=BASALT, wood=OAK, cloth2=ramp("#2a0c06", "#44140a", "#642010", "#882e18"), fire=EMBERS, hot=EMBERS)
def oracle(k):
    """she knows the way through: eyes bound in white, a maze painted on her robe, the great red spindle of thread on her back with the end trailing out behind"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.0, 8.4, 9.2), "cloth2", tag="veil_hair")
    a(h, C(0, 27.0, 0, 9.8, 2.6, 9.8), "wrap", tag="blindfold")
    a(h, C(0, 26.0, -6.2, 2.2, 3.0, 2.2), "wrap", tag="blindfold_knot")
    k.tail(h, -1.0, 26.4, -6.6, 8.0, 1.2, "wrap", lean=10, tag="blindfold_tail")
    k.tail(h, 1.0, 26.4, -6.6, 11.0, 1.2, "wrap", lean=14, tag="blindfold_tail")
    k.fire(h, C(0, 27.8, 4.95, 2.4, 1.0, 0.3))
    a(h, C(0, 32.0, 0, 9.8, 1.0, 9.8), "acc", tag="diadem")
    for x in (-3.4, 0, 3.4):
        k.spike(h, x, 33.0, 4.0, 4.2 - abs(x) * 0.3, 1.8, "gem", rx=-6, tag="obsidian_shard")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    for x, y, w, ht in ((0, 13.0, 7.0, 0.6), (-3.2, 13.0, 0.6, 7.0), (3.2, 13.0, 0.6, 9.0), (0.2, 19.6, 6.0, 0.6), (-1.4, 15.0, 0.6, 3.0), (0.8, 15.0, 3.4, 0.6), (1.6, 15.0, 0.6, 3.4), (-1.0, 17.8, 4.0, 0.6)):
        a(c, C(x, y, 2.85, w, ht, 0.3), "dark", tag="maze_line")
    k.fire(c, C(0.2, 16.0, 2.95, 1.0, 1.0, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.8), "wrap", tag="sash")
    a(b, C(0, 10.0, -5.0, 1.4, 22.0, 1.4), "wood", tag="spindle_rod")
    for y, w in ((14.0, 7.4), (15.8, 8.8), (17.6, 9.4), (19.4, 8.8), (21.2, 7.4), (23.0, 5.4)):
        a(b, C(0, y, -5.0, w, 1.8, w), "cloth2" if int(y) % 2 else "cloth", tag="thread_spool")
    a(b, C(0, 11.2, -5.0, 6.0, 1.2, 6.0), "wood", tag="spindle_whorl")
    a(b, C(0, 32.0, -5.0, 3.2, 1.0, 3.2), "wood", tag="spindle_top")
    k.fire(b, C(0, 18.0, -9.8, 3.0, 0.6, 0.3))
    k.tail(b, 4.4, 19.0, -7.2, 18.0, 0.5, "cloth2", lean=4, tag="thread_end")
    k.arms("cloth", "wrap", cuff="acc", w=5.2)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.3, 21.0, 0, 5.8, 2.4, 5.8), "wrap", tag="mantle")
        k.spike(k.shoulder(s), s * 7.0, 23.2, 0, 3.4, 1.8, "gem", rz=-s * 14, tag="obsidian_shard")
    k.legs("cloth", w=4.6)
    k.boots("leather", h=2.6, w=4.8, cuff="acc")


@design(leather=TERRACOTTA, blade=GILT, bone=BONE, cloth=ramp("#6a1408", "#8e1e0c", "#b43014", "#d84a20"), dark=BLACK, wrap=PALE, acc=GILT, gold=GILT, hide2=BASALT, fire=EMBERS, hot=EMBERS)
def hornrunner(k):
    """the bull-leapers of the old maze: a gilded half mask of a bull with short horns, red ribbons, a kilt of tooled leather, the bull's tail worn behind"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.2, -0.2, 9.0, 7.8, 9.2), "dark", tag="curled_hair")
    for x in (-3.4, -1.2, 1.2, 3.4):
        a(h, C(x, 31.2, 3.6, 2.2, 1.4, 2.2), "dark", tag="curl")
    a(h, C(0, 27.2, 4.2, 8.4, 4.2, 1.4), "blade", tag="bull_half_mask")
    a(h, C(0, 26.0, 5.2, 3.8, 2.6, 1.8), "blade", tag="bull_nose")
    for s in SIDES:
        a(h, C(s * 2.2, 28.8, 4.95, 1.6, 1.0, 0.3), "void", tag="eye")
        k.fire(h, C(s * 2.2, 29.0, 5.05, 0.9, 0.6, 0.3))
        k.horn(h, s * 4.2, 29.4, 2.0, [(3.0, -s * 72, 2.2), (2.8, -s * 26, 1.6), (2.2, s * 16, 0.9)], "blade")
        a(h, C(s * 1.0, 26.2, 6.1, 0.5, 0.5, 0.3), "void", tag="nostril")
    k.tail(h, 0, 26.0, -5.0, 14.0, 1.4, "cloth", lean=16, tag="ribbon")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.6), "wrap", tag="body_paint")
    for r in (30, -30):
        a(c, C(0, 12.4, 2.45, 1.2, 12.0, 0.4), "leather", tag="strap", rots=(("z", r),), pivot=(0, 18, 2.45))
    a(c, C(0, 16.6, 2.7, 2.8, 2.8, 0.4), "blade", tag="bull_disc")
    k.fire(c, C(0, 17.2, 2.95, 1.4, 1.4, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 2.2, 5.4), "leather", tag="wide_belt")
    a(c, C(0, 12.6, 2.8, 8.0, 1.4, 0.4), "cloth", tag="belt_stripe")
    a(b, C(0, 12.0, -3.0, 7.2, 10.0, 0.6), "wrap", tag="back")
    a(b, C(0, 3.0, -3.8, 1.2, 9.4, 1.0), "leather", tag="bull_tail", rots=(("x", 18),), pivot=(0, 12.4, -3.0))
    a(b, C(0, 0.0, -4.8, 2.2, 3.4, 1.8), "hide2", tag="tail_tuft")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "wrap", tag="arm")
        k.elbow(s, "wrap")
        a(p, C(x, 11.4, 0, 5.2, 5.4, 5.2), "leather", tag="bracer")
        a(p, C(x, 19.6, 0, 5.4, 0.9, 5.4), "blade", tag="armlet")
        k.tail(p, x + s * 2.8, 19.8, 0, 7.0, 1.0, "cloth", tag="ribbon")
        a(k.shoulder(s), C(x, 21.4, 0, 5.2, 1.6, 5.2), "leather", tag="strap_shoulder")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 7.0, 0, 5.2, 5.0, 5.2), "leather", tag="kilt")
        for dx in (-1.4, 0.4, 2.0):
            a(p, C(y + dx - 0.3, 6.6, 2.65, 1.3, 5.0, 0.3), "cloth", tag="kilt_tongue")
        a(p, C(y, 2.0, 0, 4.4, 5.0, 4.4), "wrap", tag="bare_shin")
    k.boots("leather", h=3.4, w=4.6, cuff="cloth")


@design(blade=TERRACOTTA, bone=ramp("#3a342c", "#5a5244", "#7e7460", "#a49a80", "#ccc4a8"), dark=BLACK, mail=BASALT, leather=HIDE, wrap=HEMP, acc=BASALT, wood=OAK, gem=EMBERS, cloth=TERRACOTTA, fire=EMBERS, hot=EMBERS)
def hornbreaker(k):
    """he hunts the things in the maze: a bandolier of sawn-off horns, a great horn lashed to each shoulder, a stone maul on his back with the marks of skulls on it"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.6, 0, 9.8, 8.6, 9.8), "blade", tag="helm")
    a(h, C(0, 26.6, 4.9, 3.6, 5.6, 0.4), "void", tag="t_slit")
    a(h, C(0, 29.4, 4.9, 8.2, 1.2, 0.4), "void", tag="t_slit")
    k.fire(h, C(0, 29.7, 5.1, 6.4, 0.5, 0.3))
    a(h, C(0, 32.2, 0, 7.6, 1.0, 7.6), "dark", tag="helm_top")
    for s in SIDES:
        a(h, C(s * 5.0, 26.6, 2.0, 0.6, 3.2, 3.6), "dark", tag="horn_stump_seat")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.0), "mail", tag="hauberk")
    a(c, C(0, 16.0, 3.05, 7.6, 7.0, 0.5), "blade", tag="breastplate")
    for i in range(6):
        t = i / 5
        x, y = -3.8 + 7.6 * t, 22.6 - 9.0 * t
        a(c, C(x, y, 3.4, 1.2, 0.5, 0.6), "dark", tag="horn_strap")
        k.spike(c, x, y - 0.2, 3.6, -3.0, 1.4, "bone", tag="sawn_horn", steps=2)
    a(c, C(0, 12.2, 0, 8.7, 1.6, 6.6), "dark", tag="belt")
    a(b, C(0, 13.0, -3.8, 7.4, 10.0, 1.4), "blade", tag="back_plate")
    rz = (("z", 34),)
    a(b, C(0, 4.0, -5.2, 1.6, 26.0, 1.6), "wood", tag="maul_haft", rots=rz, pivot=(0, 18, -5.2))
    a(b, C(0, 29.0, -5.2, 12.0, 7.0, 7.0), "acc", tag="maul_head", rots=rz, pivot=(0, 18, -5.2))
    a(b, C(0, 28.0, -5.2, 8.0, 9.0, 5.0), "acc", tag="maul_head", rots=rz, pivot=(0, 18, -5.2))
    for x in (-3.6, 3.6):
        a(b, C(x, 28.6, -5.2, 1.0, 7.8, 7.8), "wrap", tag="maul_band", rots=rz, pivot=(0, 18, -5.2))
    a(b, C(0, 31.6, -8.85, 1.2, 1.2, 0.3), "glow", group="fire", tag="maul_crack", rots=rz, pivot=(0, 18, -5.2))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 11.0, 0, 5.8, 5.8, 5.8), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.2, 1.0, 6.2), "wrap", tag="cord_cuff")
        q = k.shoulder(s)
        a(q, C(x + s * 0.8, 20.6, 0, 7.0, 3.0, 7.2), "blade", tag="pauldron")
        k.horn(q, x + s * 1.6, 22.6, 1.2, [(5.4, -s * 74, 3.8), (5.4, -s * 48, 3.0), (5.0, -s * 14, 2.2), (4.2, s * 22, 1.4), (2.8, s * 44, 0.7)], "bone")
        a(q, C(x + s * 2.4, 22.0, 1.2, 1.0, 3.6, 4.2), "wrap", tag="horn_lash")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 4.9, 9.6, 4.9), "mail", tag="mail")
        a(p, C(y, 6.2, 2.6, 3.8, 5.8, 0.6), "blade", tag="tasset")
    k.boots("blade", h=4.2, w=5.2, cuff="wrap", toe="dark", toe_d=2.6)


@design(stone=BASALT, blade=BASALT, dark=BLACK, gem=EMBERS, bone=ramp("#1a1a20", "#30303a", "#4a4a56", "#6a6a78", "#9090a0"), mail=BASALT, leather=HIDE, acc=TERRACOTTA, fire=EMBERS, hot=EMBERS)
def basaltplate(k):
    """the Minotaur's own shape in cooled lava: a bull's helm with vast black horns, shoulders of six-sided basalt columns, the fire still running in the joints"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.0, 0, 11.0, 9.4, 11.0), "stone", tag="bull_helm")
    a(h, C(0, 23.4, 5.8, 7.6, 5.0, 3.0), "stone", tag="bull_muzzle")
    a(h, C(0, 28.2, 5.6, 11.6, 2.0, 1.2), "stone", tag="bull_brow")
    a(h, C(0, 26.4, 5.8, 9.0, 1.6, 0.3), "void", tag="eye_seam")
    k.fire(h, C(0, 26.8, 5.95, 7.4, 0.8, 0.3))
    a(h, C(0, 24.2, 7.45, 5.0, 2.8, 0.3), "void", tag="nostrils")
    k.fire(h, C(-1.4, 24.8, 7.6, 1.2, 1.0, 0.3))
    k.fire(h, C(1.4, 24.8, 7.6, 1.2, 1.0, 0.3))
    a(h, C(0, 23.0, 7.5, 1.6, 2.6, 1.4), "acc", tag="nose_ring")
    for s in SIDES:
        k.horn(h, s * 5.4, 29.4, 1.0, [(6.0, -s * 80, 4.4), (6.0, -s * 58, 3.6), (6.0, -s * 26, 2.8), (5.4, s * 8, 2.0), (4.6, s * 34, 1.2)], "bone")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 7.0), "stone", tag="cuirass")
    for x, y, r, ln in ((-1.8, 13.4, 14, 9.6), (2.2, 15.0, -18, 8.2), (0, 18.8, 80, 6.0)):
        k.fire(c, C(x, y, 3.55, 0.8, ln, 0.3), rots=(("z", r),), pivot=(x, y, 3.55))
    a(c, C(0, 12.2, 0, 8.7, 1.6, 7.6), "dark", tag="belt")
    a(b, C(0, 13.0, -4.2, 7.8, 10.6, 2.0), "stone", tag="back_plate")
    k.fire(b, C(0, 15.0, -5.3, 1.4, 7.0, 0.3))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.fire(p, C(x, 16.6, 0, 5.1, 2.6, 5.1), tag="lava_joint")
        a(p, C(x, 11.0, 0, 6.2, 5.8, 6.2), "stone", tag="vambrace")
        q = k.shoulder(s)
        for dx, dz, ht, w in ((1.0, 0, 9.0, 3.8), (4.2, 1.4, 7.0, 3.4), (4.0, -2.0, 5.4, 3.2), (0.8, 3.4, 6.2, 3.2), (0.8, -3.4, 7.4, 3.2), (-2.0, 0, 5.0, 3.0), (7.0, -0.4, 4.0, 3.0)):
            a(q, C(x + s * dx, 20.5, dz, w, ht, w), "stone", tag="basalt_column")
            a(q, C(x + s * dx, 20.5 + ht, dz, w - 0.6, 0.3, w - 0.6), "bone", tag="column_top")
        k.fire(q, C(x + s * 2.6, 20.8, 0, 7.4, 0.6, 7.4))
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.3, 9.6, 5.3), "stone", tag="cuisse")
        k.fire(p, C(y, 5.0, 2.7, 3.8, 0.8, 0.3))
    for s in SIDES:
        p, x = k.boot(s), s * 1.95
        a(p, C(x, 0, 0.3, 5.8, 3.8, 6.4), "stone", tag="boot")
        a(p, C(x, 0, 0.5, 6.0, 0.7, 7.0), "dark", tag="sole")
        a(p, C(x, 0, 3.6, 0.6, 1.4, 1.0), "void", tag="hoof_split")


# ---------------------------------------------------------------- the Abyssal Lighthouse

@design(cloth=ABYSS, wrap=ramp("#10304a", "#184a66", "#226a84", "#3090a4"), dark=BLACK, acc=WATCHGLOW, gem=WATCHGLOW, leather=ABYSS, bone=PALE, fire=WATCHGLOW, hot=WATCHGLOW)
def abysswatch(k):
    """it watches back: a deep hood crowded with lidless eyes, a dozen more down the stole, tentacles lifting off the shoulders"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.6, -0.6, 9.8, 9.4, 9.6), "cloth", tag="hood")
    a(h, C(0, 33.0, -1.4, 7.4, 1.4, 7.0), "cloth", tag="hood_top")
    a(h, C(0, 24.4, 4.3, 7.2, 7.0, 0.5), "void", tag="hood_dark")
    for x, y, w in ((0, 28.0, 2.0), (-2.4, 29.4, 1.3), (2.4, 29.4, 1.3), (-2.8, 26.6, 1.0), (2.8, 26.6, 1.0), (-1.2, 25.6, 1.0), (1.2, 25.6, 1.0), (0, 30.2, 1.0)):
        k.fire(h, C(x, y, 4.65, w, w, 0.3))
        a(h, C(x, y + w * 0.3, 4.8, w * 0.4, w * 0.4, 0.3), "void", tag="pupil")
    for x, y in ((-3.4, 32.4), (0.8, 33.4), (3.2, 32.0), (-1.6, 33.6)):
        a(h, C(x, y, 3.2 if y < 33 else 2.6, 1.4, 1.4, 0.6), "bone", tag="hood_eye")
        a(h, C(x, y + 0.3, 3.6 if y < 33 else 3.0, 0.7, 0.7, 0.3), "void", tag="pupil")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 12.2, 2.75, 3.4, 11.8, 0.5), "wrap", tag="stole")
    for y in (13.6, 16.0, 18.4, 20.8):
        a(c, C(0, y, 3.05, 1.8, 1.8, 0.4), "bone", tag="stole_eye")
        k.fire(c, C(0, y + 0.4, 3.3, 1.0, 1.0, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.8), "wrap", tag="sash")
    for i, (x, r, l) in enumerate(((-3.0, 18, 6.0), (0.6, -6, 7.0), (3.2, -22, 5.6))):
        k.horn(b, x, 22.6, -3.6, [(l, r, 2.2), (l * 0.8, r + (24 if x <= 0 else -24), 1.6), (l * 0.7, r + (54 if x <= 0 else -54), 1.0), (l * 0.5, r + (90 if x <= 0 else -90), 0.6)], "wrap")
    a(b, C(0, 5.0, -3.6, 8.0, 18.0, 0.7), "cloth", tag="back_robe", rots=(("x", 7),), pivot=(0, 23, -3.6))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "cloth", tag="sleeve")
        k.elbow(s, "cloth")
        a(p, C(x, 10.8, 0, 6.2, 5.8, 6.2), "cloth", tag="flare")
        for y in (11.2, 12.2, 13.2):
            k.spike(p, x + s * 3.0, y, 3.0 - (y - 11) * 2.2, 2.6, 1.0, "wrap", rz=-s * 78, tag="sucker_tendril", steps=2)
        q = k.shoulder(s)
        a(q, C(x + s * 0.3, 21.0, 0, 5.8, 2.6, 5.8), "wrap", tag="mantle")
        k.horn(q, x + s * 1.6, 23.4, 1.0, [(3.4, -s * 26, 2.0), (3.0, s * 8, 1.5), (2.6, s * 44, 1.0), (2.0, s * 84, 0.6)], "wrap")
        k.horn(q, x + s * 2.4, 22.6, -1.8, [(3.0, -s * 56, 1.8), (2.6, -s * 18, 1.3), (2.2, s * 22, 0.8)], "wrap")
    k.legs("cloth", w=4.6)
    k.boots("leather", h=2.6, w=4.8, sole="dark")


@design(leather=ramp("#0c1a2a", "#142a40", "#1e3e5a", "#2c5674"), blade=ramp("#0c1a2a", "#142a40", "#1e3e5a", "#2c5674", "#407a98"), acc=COPPER, dark=BLACK, gem=WATCHGLOW, cloth=ABYSS, wrap=ramp("#10304a", "#184a66", "#226a84", "#3090a4"), fire=WATCHGLOW, hot=WATCHGLOW)
def deepsight(k):
    """he looked down too long: one vast glass eye for a helm, set in copper, feeding tendrils where the mouth was"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.8, 10.0, 8.8, 9.0), "blade", tag="helm_back")
    a(h, C(0, 24.4, 4.0, 9.4, 8.0, 1.8), "acc", tag="lens_collar")
    a(h, C(0, 25.0, 5.0, 7.8, 6.8, 0.9), "dark", tag="lens_rim")
    a(h, C(0, 25.6, 5.5, 6.4, 5.6, 0.5), "glow", group="fire", tag="great_eye")
    a(h, C(0, 27.2, 5.9, 2.2, 2.4, 0.3), "void", tag="great_pupil")
    for s in SIDES:
        a(h, C(s * 5.0, 26.4, 3.6, 1.0, 4.0, 2.4), "acc", tag="side_bolt")
    for x in (-3.0, -1.2, 0.8, 2.8):
        k.horn(h, x, 24.6, 4.4, [(-3.0, (x * 2), 1.4), (-2.8, (x * 7), 1.0), (-2.4, (x * 14), 0.6)], "wrap")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.8), "leather", tag="jerkin")
    a(c, C(0, 13.0, 2.6, 7.0, 9.0, 0.5), "blade", tag="breast_strap_plate")
    a(c, C(0, 15.8, 2.9, 3.2, 3.2, 0.4), "acc", tag="small_lens_rim")
    k.fire(c, C(0, 16.4, 3.1, 2.0, 2.0, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.6), "dark", tag="belt")
    a(b, C(0, 13.0, -3.2, 7.2, 10.0, 1.0), "blade", tag="back")
    a(b, C(0, 22.6, -4.6, 3.2, 3.2, 2.0), "acc", tag="hose_root")
    for s in SIDES:
        k.horn(b, s * 1.6, 23.0, -5.0, [(5.0, -s * 40, 1.4), (5.0, -s * 90, 1.2), (5.0, -s * 130, 1.0), (4.4, -s * 165, 0.8)], "wrap")
    k.arms("leather", "cloth", cuff="acc", w=5.0)
    for s in SIDES:
        q = k.shoulder(s)
        a(q, C(s * 6.3, 21.0, 0, 5.8, 2.4, 5.8), "blade", tag="cop")
        a(q, C(s * 6.3, 22.0, 2.95, 2.4, 1.8, 0.4), "acc", tag="small_lens_rim")
        k.fire(q, C(s * 6.3, 22.3, 3.15, 1.4, 1.2, 0.3))
    k.legs("leather", w=4.6)
    k.boots("blade", h=3.8, w=4.8, cuff="acc", sole="dark")


@design(wrap=WHITEWASH, cloth=ramp("#6a0e10", "#8e1618", "#b82420", "#dc3a30"), blade=WHITEWASH, dark=BLACK, acc=BRASS, mail=ABYSS, gem=WATCHGLOW, leather=ABYSS, fire=ramp("#d09010", "#f0b828", "#fcd850", "#ffee88", "#fff8c0", "#ffffff"), hot=ramp("#d09010", "#f0b828", "#fcd850"))
def lampkeeper(k):
    """the Keeper's man, and the lighthouse itself: red and white bands up the body, a lantern room for a head with its railed gallery, a beam thrown out front and back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 22.6, 0, 11.0, 1.6, 11.0), "dark", tag="gallery_floor")
    for t in range(4):
        for u in (-5.0, -2.5, 0, 2.5, 5.0):
            a(h, C(u, 24.2, 5.2, 0.5, 2.0, 0.5), "dark", tag="rail", rots=(("y", t * 90),), pivot=(0, 24, 0))
        a(h, C(0, 26.0, 5.2, 11.0, 0.5, 0.5), "dark", tag="rail", rots=(("y", t * 90),), pivot=(0, 26, 0))
    a(h, C(0, 24.2, 0, 8.2, 8.0, 8.2), "glow", group="fire", tag="lamp_room")
    for sx in SIDES:
        for sz in SIDES:
            a(h, C(sx * 3.9, 24.2, sz * 3.9, 1.0, 8.0, 1.0), "dark", tag="lantern_mullion")
    a(h, C(0, 27.8, 4.3, 8.2, 0.4, 0.3), "dark", tag="lantern_bar")
    a(h, C(0, 32.2, 0, 10.0, 1.0, 10.0), "cloth", tag="lantern_roof")
    a(h, C(0, 33.2, 0, 7.4, 1.4, 7.4), "cloth", tag="lantern_roof")
    a(h, C(0, 34.6, 0, 4.4, 1.2, 4.4), "cloth", tag="lantern_roof")
    a(h, C(0, 35.8, 0, 1.6, 2.4, 1.6), "acc", tag="lantern_vent")
    a(h, C(0, 38.2, 0, 2.4, 0.9, 2.4), "acc", tag="lantern_finial")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.0), "wrap", tag="tower_white")
    for y in (12.2, 18.2):
        a(c, C(0, y, 0, 8.7, 3.0, 6.4), "cloth", tag="tower_red")
    a(c, C(0, 22.4, 0, 8.7, 1.6, 7.0), "dark", tag="collar")
    a(c, C(0, 15.4, 3.15, 2.2, 2.6, 0.4), "dark", tag="tower_window")
    k.fire(c, C(0, 15.8, 3.35, 1.4, 1.8, 0.3))
    a(c, C(0, 20.6, 3.35, 1.6, 2.0, 0.4), "dark", tag="tower_window")
    a(b, C(0, 12.8, -3.5, 7.8, 10.8, 1.0), "wrap", tag="tower_back")
    a(b, C(0, 18.2, -3.6, 8.0, 3.0, 1.2), "cloth", tag="tower_red")
    a(b, C(0, 13.2, -3.6, 8.0, 3.0, 1.2), "cloth", tag="tower_red")
    a(b, C(0, 12.0, -6.0, 6.0, 7.0, 3.0), "acc", tag="oil_tank")
    a(b, C(0, 19.0, -6.0, 1.0, 5.0, 1.0), "acc", tag="oil_pipe")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "cloth", tag="sleeve_red")
        k.elbow(s, "wrap")
        a(p, C(x, 11.0, 0, 5.8, 5.8, 5.8), "wrap", tag="sleeve_white")
        a(p, C(x, 13.0, 0, 6.1, 1.8, 6.1), "cloth", tag="sleeve_red")
        q = k.shoulder(s)
        a(q, C(x + s * 0.8, 20.6, 0, 7.4, 3.2, 7.6), "wrap", tag="pauldron")
        a(q, C(x + s * 0.8, 23.6, 0, 8.4, 0.9, 8.6), "dark", tag="pauldron_gallery")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.1, 9.6, 5.1), "wrap", tag="tower_leg")
        a(p, C(y, 7.0, 0, 5.4, 3.0, 5.4), "cloth", tag="tower_red")
    k.boots("cloth", h=3.8, w=5.4, cuff="dark", sole="dark")


@design(blade=ramp("#04101a", "#0a1c2e", "#122c46", "#1c4260", "#2c6080", "#4a8aa4"), dark=BLACK, bone=PALE, acc=ramp("#0a2a34", "#124452", "#1c6470", "#308890"), gem=WATCHGLOW, mail=ABYSS, leather=ABYSS, cloth=ABYSS, fire=WATCHGLOW, hot=WATCHGLOW)
def anglerplate(k):
    """the thing that hunts by the Keeper's light: a jaw of needle teeth for a visor, a long rod arching over the head with the lure glowing in front of your eyes, fins down the back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 26.0, -0.4, 12.0, 8.4, 12.0), "blade", tag="upper_head")
    a(h, C(0, 21.6, 1.4, 11.6, 3.4, 10.4), "blade", tag="lower_jaw")
    a(h, C(0, 24.8, 5.8, 10.6, 1.8, 0.4), "void", tag="maw")
    a(h, C(0, 23.6, 4.8, 10.8, 1.4, 1.6), "void", tag="maw")
    for x in (-4.6, -3.2, -1.8, -0.4, 1.0, 2.4, 3.8, 5.0):
        k.spike(h, x, 26.2, 5.9, -3.0 - (x * 7 % 2), 1.0, "bone", tag="upper_needle", steps=2)
        k.spike(h, x - 0.5, 24.2, 6.2, 2.6 + (x * 5 % 2), 0.9, "bone", tag="lower_needle", steps=2, rx=-8)
    for s in SIDES:
        a(h, C(s * 5.2, 29.4, 5.4, 2.0, 2.0, 0.6), "dark", tag="dead_eye")
        k.fire(h, C(s * 5.2, 29.8, 5.75, 1.0, 1.0, 0.3))
        k.spike(h, s * 6.2, 27.0, -2.0, 4.0, 3.0, "acc", rz=-s * 76, tag="gill_fin", steps=2)
    px, py, pz = 0.0, 34.0, -1.0
    for ln, r, w in ((4.0, -14, 1.2), (4.4, 18, 1.1), (4.4, 46, 1.0), (4.0, 74, 0.9), (3.6, 104, 0.7), (3.2, 132, 0.5)):
        a(h, C(0, py, pz, 0.8 + w * 0.3, ln + 0.2, w), "acc", tag="lure_rod", rots=(("x", r),), pivot=(0, py, pz))
        t = math.radians(r)
        py, pz = py + math.cos(t) * ln, pz + math.sin(t) * ln
    a(h, C(0, py - 3.0, pz, 3.2, 3.4, 3.2), "glow", group="fire", tag="lure")
    a(h, C(0, py - 3.0 + 0.8, pz, 3.8, 1.8, 3.8), "glow", tag="lure")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 7.0), "blade", tag="cuirass")
    a(c, C(0, 12.2, 3.55, 6.6, 8.0, 0.5), "bone", tag="pale_belly")
    k.fire(c, C(0, 14.6, 3.85, 2.2, 2.2, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.6), "dark", tag="belt")
    a(b, C(0, 13.0, -4.2, 7.8, 10.6, 2.0), "blade", tag="back_plate")
    for i, y in enumerate((23.0, 20.0, 17.0, 14.0)):
        for s in SIDES:
            k.spike(b, s * 1.6, y, -5.4, 7.0 - i, 2.0, "acc", rz=-s * 20, rx=52, tag="back_fin")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.4, 1.0, 6.4), "acc", tag="cuff")
        k.spike(p, x + s * 3.0, 13.0, -1.4, 4.0, 3.0, "acc", rz=-s * 72, rx=20, tag="arm_fin", steps=2)
        q = k.shoulder(s)
        a(q, C(x + s * 1.2, 20.5, 0, 8.2, 3.6, 8.4), "blade", tag="pauldron")
        for t in (-3.0, -1.0, 1.0, 3.0):
            k.spike(q, x + s * 5.2, 20.8, t, -3.0, 0.9, "bone", tag="shoulder_needle", steps=2)
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.1, 9.6, 5.1), "blade", tag="cuisse")
        a(p, C(y, 4.6, 2.6, 4.0, 3.0, 1.0), "acc", tag="poleyn")
    k.boots("blade", h=4.0, w=5.2, cuff="acc", toe="dark", toe_d=2.8)


# ---------------------------------------------------------------- the Eclipse Cathedral

@design(cloth=ASH, wrap=ramp("#0e0e12", "#1a1a20", "#2a2a32", "#3c3c46"), dark=BLACK, acc=VOIDGOLD, gem=CORONA, leather=ASH, blade=BLACK, wood=BLACK, fire=CORONA, hot=CORONA)
def ashchoir(k):
    """the choir that goes on singing in the dark: ash grey robes still smouldering at the hem, a ring of black sun standing behind the bowed head, a hymnal open at the chest"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.8, -0.3, 9.4, 8.4, 9.4), "cloth", tag="choir_hood")
    a(h, C(0, 26.8, 4.45, 7.0, 3.8, 0.4), "void", tag="hood_dark")
    a(h, C(0, 26.2, 4.65, 2.0, 1.8, 0.3), "glow", tag="singing_mouth")
    a(h, C(0, 22.4, 0, 11.4, 2.4, 11.4), "wrap", tag="collar")
    for t in range(16):
        a(b, C(0, 28.6 + 11.0, -5.8, 4.2, 2.4, 0.9), "blade", tag="black_ring", rots=(("z", t * 22.5),), pivot=(0, 28.6, -5.8))
        a(b, C(0, 28.6 + 13.4, -5.9, 3.4, 0.7, 0.6), "glow", group="fire", tag="ring_rim", rots=(("z", t * 22.5),), pivot=(0, 28.6, -5.8))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 13.2, 2.8, 6.8, 5.0, 0.9), "wrap", tag="hymnal")
    a(c, C(0, 13.4, 3.3, 6.2, 4.6, 0.3), "cloth", tag="hymnal_pages")
    a(c, C(0, 13.4, 3.45, 0.4, 4.6, 0.3), "dark", tag="hymnal_gutter")
    for y in (14.2, 15.4, 16.6):
        for s in SIDES:
            a(c, C(s * 1.7, y, 3.45, 2.2, 0.3, 0.3), "dark", tag="hymnal_line")
    a(c, C(0, 12.0, 0, 8.7, 0.9, 5.8), "acc", tag="sash")
    a(c, C(0, 20.8, 0, 8.7, 3.2, 6.0), "wrap", tag="yoke")
    a(b, C(0, 5.0, -3.6, 8.0, 18.0, 0.7), "cloth", tag="back_robe", rots=(("x", 7),), pivot=(0, 23, -3.6))
    a(b, C(0, 5.0, -4.6, 8.2, 1.2, 0.6), "glow", group="fire", tag="smoulder_hem", rots=(("x", 7),), pivot=(0, 23, -3.6))
    a(b, C(0, 21.0, -3.8, 1.4, 8.0, 1.2), "blade", tag="ring_post")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "cloth", tag="sleeve")
        k.elbow(s, "cloth")
        a(p, C(x, 10.8, 0, 6.2, 5.8, 6.2), "cloth", tag="flare")
        k.fire(p, C(x, 10.8, 0, 6.5, 0.7, 6.5))
        a(k.shoulder(s), C(x + s * 0.3, 21.0, 0, 5.8, 2.6, 5.8), "wrap", tag="mantle")
    k.legs("cloth", w=4.6)
    k.boots("wrap", h=2.4, w=4.8)


@design(leather=BLACK, blade=ramp("#7a7c84", "#9a9ca4", "#bcbec4", "#dcdde0", "#f4f4f6"), feather=ramp("#7a7c84", "#9a9ca4", "#bcbec4", "#dcdde0", "#f4f4f6"), cloth=RAVEN, dark=BLACK, acc=VOIDGOLD, gem=CORONA, wrap=ASH, fire=CORONA, hot=CORONA)
def fallenblade(k):
    """the seraph's squire, after the fall: one white wing whole, the other burned to its bones, a cracked halo slipped sideways over the brow"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.2, -0.2, 9.0, 7.8, 9.2), "leather", tag="hood")
    a(h, C(0, 24.4, 4.4, 7.4, 6.8, 0.7), "blade", tag="serene_mask")
    a(h, C(0, 28.0, 4.85, 6.6, 0.7, 0.3), "void", tag="closed_eyes")
    a(h, C(1.8, 24.4, 4.85, 0.6, 7.0, 0.3), "void", tag="mask_crack")
    k.fire(h, C(1.8, 25.4, 4.95, 0.3, 4.8, 0.3))
    for t in range(14):
        if t in (4, 5):
            continue
        r = math.radians(t * 25.7)
        a(h, C(math.sin(r) * 6.8, 34.0 + math.sin(r) * 2.2, math.cos(r) * 6.8, 3.0, 0.8, 1.2), "glow", group="fire", tag="slipped_halo", rots=(("y", t * 25.7), ("z", -18)), pivot=(math.sin(r) * 6.8, 34.0, math.cos(r) * 6.8))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.8), "leather", tag="jerkin")
    a(c, C(0, 13.8, 2.6, 8.0, 9.4, 0.5), "cloth", tag="front")
    for r in (24, -24):
        a(c, C(0, 13.6, 2.95, 1.1, 10.0, 0.4), "acc", tag="strap", rots=(("z", r),), pivot=(0, 18.6, 2.95))
    k.fire(c, C(0, 18.2, 3.2, 1.2, 1.2, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.6), "dark", tag="belt")
    a(b, C(0, 13.0, -3.2, 7.0, 10.0, 1.0), "leather", tag="back")
    for i, (t, ln, w) in enumerate(((12, 25.0, 3.6), (26, 28.0, 3.6), (40, 28.0, 3.4), (54, 26.0, 3.2), (68, 23.0, 3.0), (82, 19.0, 2.8), (98, 15.0, 2.6), (114, 11.0, 2.4))):
        a(b, C(2.0, 20.0, -4.0 - i * 0.2, w, ln, 0.7), "feather", tag="white_wing", rots=(("z", -t),), pivot=(2.0, 20, -4.0))
    k.horn(b, -2.0, 20.0, -4.2, [(9.0, 44, 2.0), (9.0, 66, 1.6), (7.0, 100, 1.2)], "dark")
    for x, y, l, r in ((-8.4, 26.0, 13.0, 150), (-13.0, 26.0, 11.0, 140), (-18.0, 24.0, 9.0, 132)):
        a(b, C(x, y, -4.2, 0.9, l, 0.9), "dark", tag="burned_wing_bone", rots=(("z", r),), pivot=(x, y, -4.2))
        k.fire(b, C(x, y - 0.4, -4.75, 1.0, 1.0, 0.3))
    k.arms("leather", "cloth", cuff="acc", w=5.0)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.2, 21.2, 0, 5.4, 2.2, 5.4), "wrap", tag="cop")
    a(k.shoulder(1), C(6.2, 23.2, 0, 4.0, 1.0, 4.0), "blade", tag="cop_white")
    k.legs("leather", w=4.6)
    k.boots("leather", h=4.0, w=4.8, cuff="acc", toe="dark", toe_d=2.8)


@design(blade=ramp("#8a8678", "#aca898", "#ccc8b8", "#e6e2d4", "#f8f6ec", "#ffffff"), feather=ramp("#8a8678", "#aca898", "#ccc8b8", "#e6e2d4", "#f8f6ec", "#ffffff"), acc=GILT, gold=GILT, dark=ramp("#2a1c06", "#4a3208", "#70500e"), mail=GILT, cloth=GILT, leather=HIDE, gem=CORONA, fire=CORONA, hot=CORONA)
def haloguard(k):
    """the cathedral's sentinels from before the dark: white and gold, a winged helm, and a true halo, burning, carried on a gold ring behind the head"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.2, 0, 10.0, 9.0, 10.0), "blade", tag="helm")
    a(h, C(0, 26.6, 4.95, 8.0, 0.9, 0.4), "void", tag="slit")
    k.fire(h, C(0, 26.8, 5.15, 6.4, 0.5, 0.3))
    a(h, C(0, 28.0, 4.95, 1.0, 4.4, 0.4), "acc", tag="brow_cross")
    a(h, C(0, 31.4, 0, 10.8, 1.1, 10.8), "acc", tag="brow")
    for s in SIDES:
        for i, (t, ln, w) in enumerate(((24, 9.0, 2.4), (44, 8.0, 2.2), (64, 6.6, 2.0))):
            a(h, C(s * 5.2, 27.0 + i * 0.6, 1.0 - i * 1.2, 0.7, ln, w), "feather", tag="helm_wing", rots=(("z", -s * t),), pivot=(s * 5.2, 27, 1))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.4), "blade", tag="cuirass")
    a(c, C(0, 13.2, 3.3, 6.2, 9.6, 0.5), "acc", tag="sun_tabard")
    a(c, C(0, 15.4, 3.6, 3.8, 3.8, 0.4), "blade", tag="sun_seat")
    k.fire(c, C(0, 16.2, 3.85, 2.2, 2.2, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.0), "acc", tag="belt")
    a(b, C(0, 13.0, -3.8, 7.6, 10.4, 1.6), "blade", tag="back_plate")
    a(b, C(0, 21.0, -4.6, 1.4, 9.0, 1.2), "acc", tag="halo_post")
    for t in range(20):
        a(b, C(0, 28.6 + 11.6, -5.4, 3.6, 1.4, 1.0), "acc", tag="halo_ring", rots=(("z", t * 18),), pivot=(0, 28.6, -5.4))
        a(b, C(0, 28.6 + 13.0, -5.4, 2.4, 0.8, 0.7), "glow", group="fire", tag="halo_fire", rots=(("z", t * 18),), pivot=(0, 28.6, -5.4))
    for t in range(4):
        a(b, C(0, 28.6, -5.4, 0.7, 11.6, 0.7), "acc", tag="halo_spoke", rots=(("z", 45 + t * 90),), pivot=(0, 28.6, -5.4))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.4, 1.0, 6.4), "acc", tag="cuff")
        q = k.shoulder(s)
        a(q, C(x + s * 1.2, 20.5, 0, 8.4, 3.6, 8.6), "blade", tag="pauldron")
        a(q, C(x + s * 1.2, 20.3, 0, 8.8, 0.9, 9.0), "acc", tag="pauldron_rim")
        for i, (t, ln) in enumerate(((16, 7.0), (36, 6.0), (56, 5.0))):
            a(q, C(x + s * 2.6, 23.6, -1.0 - i * 0.2, 1.8, ln, 0.6), "feather", tag="shoulder_wing", rots=(("z", -s * t),), pivot=(x + s * 2.6, 23.6, -1))
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.1, 9.6, 5.1), "blade", tag="cuisse")
        a(p, C(y, 6.2, 2.6, 3.8, 5.8, 0.6), "acc", tag="tasset")
        a(p, C(y, 4.4, 2.7, 4.0, 2.6, 1.0), "blade", tag="poleyn")
    k.boots("blade", h=4.2, w=5.2, cuff="acc", toe="acc", toe_d=2.8)


@design(blade=ramp("#040406", "#0a0a10", "#14141c", "#20202c", "#303040", "#4c4c60"), dark=BLACK, acc=VOIDGOLD, gold=VOIDGOLD, mail=RAVEN, cloth=RAVEN, leather=HIDE, gem=CORONA, fire=CORONA, hot=CORONA)
def eclipse(k):
    """the last set of the last cathedral: black plate with a crown of sun's rays, and behind it the eclipse itself, a disc of nothing with the corona streaming off its edge"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.0, 0, 10.4, 9.4, 10.4), "blade", tag="helm")
    a(h, C(0, 26.8, 5.05, 8.4, 0.9, 0.4), "void", tag="slit")
    k.fire(h, C(0, 27.0, 5.25, 6.8, 0.5, 0.3))
    a(h, C(0, 28.4, 5.0, 1.4, 4.4, 0.5), "acc", tag="nasal_ray")
    a(h, C(0, 31.6, 0, 11.4, 1.2, 11.4), "acc", tag="crown_band")
    for i, (x, z, ln) in enumerate(((0, 5.2, 10.0), (-2.8, 4.8, 7.4), (2.8, 4.8, 7.4), (-5.2, 2.8, 8.4), (5.2, 2.8, 8.4), (-5.4, -1.6, 7.0), (5.4, -1.6, 7.0))):
        k.spike(h, x, 32.8, z, ln, 2.2, "acc", rz=-x * 3.0, rx=-z * 0.6, tag="sun_ray", steps=4)
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.8), "blade", tag="cuirass")
    a(c, C(0, 13.6, 3.45, 7.0, 7.4, 0.5), "acc", tag="corona_ring")
    a(c, C(0, 14.4, 3.7, 5.4, 5.8, 0.4), "void", tag="black_sun")
    k.fire(c, C(0, 14.2, 3.55, 6.2, 0.5, 0.3))
    k.fire(c, C(0, 20.4, 3.55, 6.2, 0.5, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.4), "acc", tag="belt")
    a(b, C(0, 2.0, -3.8, 8.0, 21.0, 0.8), "cloth", tag="night_cape", rots=(("x", 8),), pivot=(0, 23, -3.8))
    k.fire(b, C(0, 2.0, -4.6, 8.2, 0.9, 0.3), rots=(("x", 8),), pivot=(0, 23, -3.8))
    a(b, C(0, 21.8, -4.4, 2.0, 7.0, 1.4), "acc", tag="disc_post")
    a(b, C(0, 22.0, -6.2, 20.0, 20.0, 1.0), "void", tag="eclipse_disc")
    a(b, C(0, 19.0, -6.2, 13.0, 26.0, 1.0), "void", tag="eclipse_disc")
    a(b, C(0, 25.0, -6.2, 26.0, 14.0, 1.0), "void", tag="eclipse_disc")
    for t in range(24):
        ln = 6.0 + 4.0 * ((t * 7) % 3 == 0) + 2.4 * (t % 2)
        a(b, C(0, 32.0 + 13.0, -6.4, 3.2, 1.0, 0.7), "acc", tag="corona_rim", rots=(("z", t * 15),), pivot=(0, 32.0, -6.2))
        a(b, C(0, 32.0 + 13.6, -6.4, 1.6, ln, 0.5), "glow", group="fire", tag="corona", rots=(("z", t * 15),), pivot=(0, 32.0, -6.2))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.5, 1.1, 6.5), "acc", tag="cuff")
        k.spike(p, x + s * 2.9, 13.0, 0, 3.4, 1.8, "acc", rz=-s * 76, tag="sun_ray")
        q = k.shoulder(s)
        a(q, C(x + s * 1.2, 20.5, 0, 8.8, 3.8, 9.0), "blade", tag="pauldron")
        a(q, C(x + s * 1.2, 20.3, 0, 9.2, 0.9, 9.4), "acc", tag="pauldron_rim")
        a(q, C(x + s * 1.2, 24.2, 0, 6.8, 0.9, 7.0), "acc", tag="pauldron_top")
        for t, ln in ((-34, 6.0), (-12, 8.4), (10, 8.0), (32, 6.0), (54, 4.8)):
            k.spike(q, x + s * 1.6, 25.0, 0, ln, 2.2, "acc", rz=-s * (t + 16), tag="sun_ray", steps=3)
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.1, 9.6, 5.1), "blade", tag="cuisse")
        a(p, C(y, 4.6, 2.6, 4.0, 3.0, 1.0), "acc", tag="poleyn")
    k.boots("blade", h=4.2, w=5.2, cuff="acc", toe="acc", toe_d=3.0)


# ---------------------------------------------------------------- the Wyrm's Hoard

@design(cloth=ASH, wrap=WYRM, bone=BONE, dark=BLACK, acc=GILT, gold=GILT, gem=GILT, leather=HIDE, blade=GILT, fire=WYRMFIRE, hot=WYRMFIRE)
def ashcultist(k):
    """they feed the wyrm and take the ash for payment: a young dragon's skull for a hood, grey robes, gold coins sewn into every hem"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.2, 7.8, 9.4), "cloth", tag="hood")
    a(h, C(0, 28.4, 0.6, 10.4, 5.4, 10.8), "bone", tag="dragon_cranium")
    a(h, C(0, 29.0, 6.8, 6.4, 3.4, 4.0), "bone", tag="dragon_snout")
    a(h, C(0, 29.4, 9.0, 4.4, 2.4, 2.0), "bone", tag="dragon_snout_tip")
    for x in (-2.8, -1.4, 0, 1.4, 2.8):
        k.spike(h, x, 29.2, 7.8, -1.8, 0.9, "bone", tag="dragon_tooth", steps=2)
    for s in SIDES:
        a(h, C(s * 3.8, 30.2, 5.4, 2.2, 2.0, 0.6), "void", tag="socket")
        k.fire(h, C(s * 3.8, 30.6, 5.75, 1.2, 1.0, 0.3))
        k.spike(h, s * 4.0, 33.0, -2.6, 8.0, 2.2, "bone", rx=44, rz=-s * 14, tag="dragon_horn", steps=4)
    a(h, C(0, 27.2, 4.45, 6.4, 1.2, 0.3), "void", tag="shadow")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 12.2, 2.75, 3.0, 11.8, 0.5), "wrap", tag="stole")
    a(c, C(0, 12.2, 0, 8.7, 1.4, 5.8), "wrap", tag="sash")
    for x in (-3.6, -2.2, -0.8, 0.8, 2.2, 3.6):
        a(c, C(x, 11.0, 3.05, 1.1, 1.1, 0.4), "acc", tag="sewn_coin")
    k.fire(c, C(0, 16.4, 3.05, 1.0, 3.4, 0.3))
    a(b, C(0, 5.0, -3.6, 8.0, 18.0, 0.7), "cloth", tag="back_robe", rots=(("x", 7),), pivot=(0, 23, -3.6))
    for x, y in ((-3.0, 6.0), (-1.0, 7.0), (1.0, 6.0), (3.0, 7.0), (-2.0, 9.0), (2.0, 9.0)):
        a(b, C(x, y, -5.7 + (y - 6) * 0.1, 1.2, 1.2, 0.3), "acc", tag="sewn_coin")
    k.arms("cloth", "cloth", cuff="acc", w=5.6, low_h=5.2)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.3, 21.0, 0, 5.8, 2.6, 5.8), "wrap", tag="mantle")
        a(k.arm(s), C(s * 6.0, 10.8, 0, 6.2, 0.8, 6.2), "acc", tag="coin_hem")
    k.legs("cloth", w=4.6)
    k.boots("wrap", h=2.8, w=4.8, cuff="acc")


@design(scale=WYRM, leather=WYRM, cloth=ramp("#100806", "#1e0e0a", "#301610", "#462218"), dark=BLACK, acc=GILT, bone=BONE, blade=WYRM, fire=WYRMFIRE, hot=WYRMFIRE)
def scalehide(k):
    """cut from a drake he killed himself: a hood of red scale with spines running down the back into a long stiff tail"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.4, 8.4, 9.6), "scale", tag="scale_hood")
    a(h, C(0, 27.0, 4.65, 7.2, 3.0, 0.4), "void", tag="hood_dark")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 27.8, 4.85, 1.2, 0.7, 0.3))
    a(h, C(0, 30.4, 4.6, 8.8, 1.2, 1.0), "scale", tag="brow")
    a(h, C(0, 23.2, 2.6, 9.0, 2.4, 5.2), "cloth", tag="face_wrap")
    for i, z in enumerate((3.4, 1.2, -1.0, -3.2, -5.0)):
        k.spike(h, 0, 32.4 - (i > 3) * 1.4, z, 3.6 - abs(i - 2) * 0.5, 1.6, "bone", rx=24, tag="spine", steps=2)
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.8), "scale", tag="scale_jerkin")
    a(c, C(0, 13.0, 2.6, 5.4, 9.0, 0.4), "cloth", tag="pale_belly_strip")
    for y in (14.0, 16.0, 18.0, 20.0):
        a(c, C(0, y, 2.85, 5.4, 0.5, 0.3), "bone", tag="belly_scute")
    k.fire(c, C(0, 16.8, 2.95, 1.2, 1.2, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.6), "dark", tag="belt")
    a(b, C(0, 13.0, -3.0, 7.2, 10.2, 0.8), "scale", tag="scale_back")
    for y in (14.0, 17.0, 20.0, 23.0):
        k.spike(b, 0, y, -3.4, 4.0, 2.0, "bone", rx=62, tag="back_spine")
    for i, (ln, r, w) in enumerate(((6.0, 42, 4.4), (6.0, 58, 3.4), (6.0, 70, 2.6), (6.0, 80, 1.8), (5.0, 88, 1.1))):
        y0, z0 = 13.0 - sum((6.0 * math.cos(math.radians(q)) for q in (42, 58, 70, 80)[:i])), -3.4 - sum((6.0 * math.sin(math.radians(q)) for q in (42, 58, 70, 80)[:i]))
        a(b, C(0, y0 - ln, z0, w, ln + 0.2, w * 0.8), "scale", tag="long_tail", rots=(("x", r),), pivot=(0, y0, z0))
        k.spike(b, 0, y0 - 2.0, z0 - 0.0, 2.0, 1.2, "bone", rx=r - 70, tag="tail_spine", steps=2)
    k.arms("scale", "scale", joint="cloth", cuff="dark", w=5.0)
    for s in SIDES:
        k.spike(k.arm(s), s * 6.0, 12.8, -2.6, 3.6, 1.4, "bone", rx=120, tag="fin_spine", steps=2)
        k.spike(k.arm(s), s * 6.0, 14.8, -2.6, 3.0, 1.2, "bone", rx=120, tag="fin_spine", steps=2)
        a(k.shoulder(s), C(s * 6.2, 21.2, 0, 5.4, 2.2, 5.4), "scale", tag="scale_cop")
        k.spike(k.shoulder(s), s * 7.0, 23.2, 0, 3.4, 1.6, "bone", rz=-s * 22, tag="spine")
    k.legs("scale", w=4.6)
    k.boots("cloth", h=3.8, w=4.8, cuff="scale", toe="dark", toe_d=3.0)


@design(scale=WYRM, blade=WYRM, dark=BLACK, acc=GILT, bone=ramp("#2a1a10", "#46301e", "#66482e", "#8c6a48", "#b49068"), mail=ramp("#100806", "#1e0e0a", "#301610", "#462218"), cloth=WYRM, leather=HIDE, gem=WYRMFIRE, wrap=ramp("#5a1608", "#8a2a10", "#bc4a1c"), fire=WYRMFIRE, hot=WYRMFIRE)
def wyrmscale(k):
    """a drake knight: a dragon's head for a helm, its mouth lit from inside, wings spread stiff on the shoulders, every plate scaled"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.6, -0.2, 10.4, 8.0, 10.4), "scale", tag="dragon_head")
    a(h, C(0, 27.4, 6.0, 7.0, 4.0, 3.0), "scale", tag="dragon_upper_jaw")
    a(h, C(0, 28.0, 8.8, 5.0, 3.0, 3.0), "scale", tag="dragon_upper_jaw")
    a(h, C(0, 23.0, 3.8, 8.6, 2.2, 7.6), "scale", tag="dragon_lower_jaw")
    a(h, C(0, 25.2, 5.4, 7.8, 2.2, 5.2), "dark", tag="dragon_mouth")
    a(h, C(0, 25.6, 5.8, 6.4, 1.4, 5.0), "glow", group="fire", tag="dragon_throat")
    for x in (-3.0, -1.5, 0, 1.5, 3.0):
        k.spike(h, x, 27.4, 8.0, -1.8, 0.9, "acc", tag="dragon_tooth", steps=2)
    for s in SIDES:
        a(h, C(s * 3.2, 29.8, 5.2, 1.8, 1.4, 0.7), "gem", tag="dragon_eye")
        a(h, C(s * 1.2, 30.4, 10.05, 0.8, 0.6, 0.3), "void", tag="dragon_nostril")
        k.spike(h, s * 3.4, 31.4, -4.0, 10.0, 2.6, "bone", rx=58, rz=-s * 12, tag="dragon_horn", steps=4)
        k.spike(h, s * 5.4, 28.0, -2.8, 6.0, 1.8, "bone", rz=-s * 66, rx=32, tag="dragon_cheek_horn")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.4), "scale", tag="cuirass")
    a(c, C(0, 13.6, 3.3, 6.6, 8.0, 0.5), "dark", tag="plastron")
    for y in (14.4, 16.4, 18.4, 20.4):
        a(c, C(0, y, 3.55, 6.0, 0.9, 0.4), "acc", tag="scute")
    k.fire(c, C(0, 12.8, 3.55, 1.6, 1.2, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.0), "dark", tag="belt")
    a(b, C(0, 13.0, -3.8, 7.6, 10.4, 1.6), "scale", tag="back_plate")
    for s in SIDES:
        k.spike(b, 0, 14.0 + s + 1, -4.6, 4.0, 2.0, "bone", rx=58, tag="back_spine")
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "scale", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.4, 1.0, 6.4), "acc", tag="cuff")
        for dz in (-1.8, 0, 1.8):
            k.spike(p, x + dz, 11.0, 2.9, -2.6, 1.1, "bone", tag="talon", steps=2)
        q = k.shoulder(s)
        a(q, C(x + s * 1.0, 20.5, 0, 8.0, 3.6, 8.2), "scale", tag="pauldron")
        a(q, C(x + s * 2.0, 23.6, -1.4, 2.0, 11.0, 2.0), "bone", tag="wing_arm", rots=(("z", -s * 42),), pivot=(x + s * 2, 23.6, -1.4))
        tx, ty = x + s * 2.0 + s * math.sin(math.radians(42)) * 11, 23.6 + math.cos(math.radians(42)) * 11
        k.spike(q, tx, ty, -1.4, 3.6, 1.6, "bone", rz=-s * 10, tag="wing_claw")
        for i, (r, ln) in enumerate(((80, 11.0), (112, 12.0), (146, 13.0))):
            a(q, C(tx, ty, -1.4, 1.0, ln, 1.0), "bone", tag="wing_finger", rots=(("z", -s * r),), pivot=(tx, ty, -1.4))
            for j, t in enumerate((0.4, 0.75)):
                ang = math.radians(r)
                px, py = tx + s * math.sin(ang) * ln * t, ty + math.cos(ang) * ln * t
                a(q, C(px - s * 0.0, py - (ln * t * 0.55), -1.4, ln * 0.42 * (1 - j * 0.3), ln * t * 0.7, 0.4), "wrap", tag="wing_web", rots=(("z", -s * (r - 22)),), pivot=(px, py, -1.4))
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.1, 9.6, 5.1), "scale", tag="cuisse")
        a(p, C(y, 4.6, 2.6, 4.0, 3.0, 1.0), "dark", tag="poleyn")
        k.spike(p, y, 5.4, 3.0, 3.0, 1.4, "bone", rx=-54, tag="knee_spike")
    k.boots("scale", h=4.2, w=5.2, cuff="dark", toe="acc", toe_d=3.2)


@design(blade=GILT, acc=WYRM, gold=GILT, gem=ramp("#6a0a2a", "#a0143e", "#d42a56", "#f0607c", "#ffa8b0"), stone=ramp("#0e2a6a", "#183c92", "#2858bc", "#4078dc", "#80b0f0"), dark=BLACK, mail=GILT, cloth=WYRM, leather=HIDE, wood=OAK, fire=WYRMFIRE, hot=WYRMFIRE)
def hoardplate(k):
    """you robbed the wyrm and wore the proceeds: plate of hammered gold crusted with every gem in the pile, a stolen crown, and a whole treasure chest open on your back, spilling coin"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.0, 0, 10.2, 9.0, 10.2), "blade", tag="gold_helm")
    a(h, C(0, 26.6, 5.0, 8.2, 0.9, 0.4), "void", tag="slit")
    k.fire(h, C(0, 26.8, 5.2, 6.6, 0.5, 0.3))
    a(h, C(0, 31.6, 0, 11.4, 1.8, 11.4), "acc", tag="crown_cap")
    a(h, C(0, 32.0, 0, 12.0, 2.0, 12.0), "blade", tag="crown_band")
    for t in range(8):
        k.spike(h, math.sin(math.radians(t * 45)) * 5.2, 33.8, math.cos(math.radians(t * 45)) * 5.2, 4.6 if t % 2 == 0 else 3.0, 2.4, "blade", tag="crown_point", steps=3)
    for t, m in enumerate(("gem", "stone", "gem", "stone")):
        x, z = math.sin(math.radians(t * 90)) * 6.1, math.cos(math.radians(t * 90)) * 6.1
        a(h, C(x, 32.4, z, 1.6, 1.4, 1.6), m, tag="crown_gem")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.8), "blade", tag="cuirass")
    for x, y, w, m in ((-3.0, 20.4, 2.0, "gem"), (0.2, 21.0, 1.6, "stone"), (3.2, 19.8, 2.2, "gem"), (-1.8, 17.0, 2.6, "stone"), (2.0, 16.2, 1.8, "gem"), (-3.4, 14.0, 1.6, "gem"), (0.4, 13.6, 2.2, "stone"), (3.2, 13.8, 1.4, "stone")):
        a(c, C(x, y, 3.5, w + 0.5, w + 0.5, 0.5), "acc", tag="gem_seat")
        a(c, C(x, y + 0.25, 3.75, w, w, 0.5), m, tag="set_gem")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.4), "acc", tag="belt")
    for x in (-3.4, -1.8, 1.8, 3.4):
        a(c, C(x, 10.8, 3.8, 1.4, 1.4, 0.4), "blade", tag="coin")
    a(b, C(0, 13.0, -6.2, 11.0, 8.2, 6.2), "wood", tag="chest_box")
    a(b, C(0, 12.6, -6.2, 11.4, 1.1, 6.6), "blade", tag="chest_band")
    a(b, C(0, 19.6, -6.2, 11.4, 1.1, 6.6), "blade", tag="chest_band")
    a(b, C(0, 21.4, -9.4, 11.0, 6.0, 1.4), "wood", tag="chest_lid", rots=(("x", 24),), pivot=(0, 21, -9.2))
    a(b, C(0, 21.6, -9.8, 11.4, 1.0, 1.6), "blade", tag="chest_band", rots=(("x", 24),), pivot=(0, 21, -9.2))
    a(b, C(0, 20.8, -6.2, 9.6, 1.6, 5.0), "blade", tag="coin_pile")
    a(b, C(1.0, 22.2, -6.0, 6.0, 1.6, 3.6), "blade", tag="coin_pile")
    a(b, C(-0.6, 23.6, -6.0, 3.0, 1.4, 2.2), "blade", tag="coin_pile")
    k.fire(b, C(3.4, 22.0, -3.9, 1.0, 1.0, 0.3))
    a(b, C(-3.6, 21.8, -3.9, 1.6, 1.4, 0.5), "gem", tag="pile_gem")
    a(b, C(2.6, 23.4, -7.6, 1.4, 1.4, 1.0), "stone", tag="pile_gem")
    a(b, C(-1.0, 25.0, -6.0, 3.4, 0.9, 3.4), "blade", tag="goblet_base")
    a(b, C(-1.0, 25.8, -6.0, 2.2, 2.8, 2.2), "blade", tag="goblet")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.4, 1.0, 6.4), "acc", tag="cuff")
        a(p, C(x, 13.0, 3.05, 1.8, 1.8, 0.5), "stone" if s > 0 else "gem", tag="set_gem")
        for i in range(3):
            a(p, C(x, 11.4 + i * 1.4, 0, 6.4, 0.6, 6.4), "dark" if i == 1 else "blade", tag="stolen_rings")
        q = k.shoulder(s)
        a(q, C(x + s * 1.2, 20.5, 0, 8.8, 3.6, 9.0), "blade", tag="pauldron")
        a(q, C(x + s * 1.2, 24.0, 0, 7.0, 1.0, 7.2), "acc", tag="pauldron_top")
        for t, m in ((-3.2, "gem"), (0, "stone"), (3.2, "gem")):
            a(q, C(x + s * 5.5, 21.4, t, 0.5, 1.8, 1.8), m, tag="set_gem")
        a(q, C(x + s * 1.2, 25.0, 0, 5.2, 1.2, 5.2), "blade", tag="coin_stack")
        a(q, C(x + s * 1.6, 26.2, 0.4, 3.4, 1.2, 3.4), "blade", tag="coin_stack")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.1, 9.6, 5.1), "blade", tag="cuisse")
        a(p, C(y, 4.6, 2.6, 4.0, 3.0, 1.0), "acc", tag="poleyn")
        a(p, C(y, 5.3, 3.15, 1.8, 1.6, 0.4), "stone", tag="set_gem")
    k.boots("blade", h=4.0, w=5.2, cuff="acc", toe="dark", toe_d=2.8)


# ---------------------------------------------------------------- the Clockwork Spire

@design(cloth=ramp("#0e2030", "#163246", "#22485e", "#30627a", "#467e96"), wrap=WHITEWASH, acc=CLOCK, blade=CLOCK, dark=BLACK, leather=HIDE, gem=STEAM, wood=OAK, fire=STEAM, hot=STEAM)
def horologist(k):
    """the Grand Horologe's servant: a monocle and a clock's whole dial standing behind his head with the hands set, a pendulum swinging low down his back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.2, -0.2, 9.0, 7.6, 9.2), "cloth", tag="hood")
    a(h, C(0, 31.4, 0, 8.6, 1.4, 8.6), "acc", tag="circlet")
    a(h, C(0, 22.6, 0, 10.8, 2.0, 10.8), "acc", tag="gear_collar")
    a(h, C(-2.2, 27.0, 4.5, 3.4, 3.4, 0.6), "acc", tag="monocle_rim")
    k.fire(h, C(-2.2, 27.6, 4.85, 2.2, 2.2, 0.3))
    a(h, C(2.2, 27.8, 4.65, 2.2, 0.7, 0.3), "void", tag="squint")
    a(h, C(-4.6, 22.0, 4.6, 0.3, 5.6, 0.3), "acc", tag="monocle_chain")
    a(b, C(0, 18.0, -4.4, 6.0, 5.0, 1.4), "acc", tag="dial_mount")
    a(b, C(0, 21.6, -5.2, 19.0, 19.0, 1.0), "acc", tag="dial_case")
    a(b, C(0, 18.6, -5.2, 12.0, 25.0, 1.0), "acc", tag="dial_case")
    a(b, C(0, 24.8, -5.2, 25.0, 12.0, 1.0), "acc", tag="dial_case")
    a(b, C(0, 22.6, -4.6, 17.0, 17.0, 0.5), "wrap", tag="dial_face")
    a(b, C(0, 20.0, -4.6, 11.0, 22.4, 0.5), "wrap", tag="dial_face")
    a(b, C(0, 25.4, -4.6, 22.4, 11.0, 0.5), "wrap", tag="dial_face")
    a(b, C(0, 22.6, -5.85, 17.0, 17.0, 0.5), "wrap", tag="dial_face")
    a(b, C(0, 20.0, -5.85, 11.0, 22.4, 0.5), "wrap", tag="dial_face")
    a(b, C(0, 25.4, -5.85, 22.4, 11.0, 0.5), "wrap", tag="dial_face")
    for t in range(12):
        a(b, C(0, 31.2 + 9.2, -6.15, 1.0, 1.8, 0.3), "dark", tag="dial_mark", rots=(("z", t * 30),), pivot=(0, 31.2, -6.15))
        a(b, C(0, 31.2 + 9.2, -4.25, 1.0, 1.8, 0.3), "dark", tag="dial_mark", rots=(("z", t * 30),), pivot=(0, 31.2, -4.25))
    for z in (-6.3, -4.1):
        a(b, C(0, 31.2, z, 1.0, 8.0, 0.3), "dark", tag="dial_hand", rots=(("z", 50),), pivot=(0, 31.2, z))
        a(b, C(0, 31.2, z, 1.0, 6.0, 0.3), "dark", tag="dial_hand", rots=(("z", -70),), pivot=(0, 31.2, z))
    a(b, C(0, 30.6, -6.4, 1.6, 1.6, 0.3), "acc", tag="dial_hub")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    for x, y, w in ((-1.8, 17.0, 3.8), (1.8, 14.0, 3.0)):
        a(c, C(x, y, 2.85, w, w, 0.4), "acc", tag="chest_cog")
        a(c, C(x, y + w * 0.3, 3.1, w * 0.4, w * 0.4, 0.3), "dark", tag="cog_hole")
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.8), "acc", tag="belt")
    a(b, C(0, 5.0, -3.4, 0.7, 16.0, 0.7), "acc", tag="pendulum_rod")
    a(b, C(0, 2.0, -3.4, 4.0, 4.0, 1.6), "acc", tag="pendulum_bob")
    k.fire(b, C(0, 3.0, -4.35, 1.8, 1.8, 0.3))
    k.arms("cloth", "cloth", cuff="acc", w=5.6, low_h=5.2)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.3, 21.0, 0, 5.8, 2.6, 5.8), "acc", tag="brass_cop")
    k.legs("cloth", w=4.6)
    k.boots("leather", h=2.8, w=4.8, cuff="acc", toe="acc", toe_d=2.0)


@design(leather=ramp("#2a160c", "#442612", "#62381c", "#845028", "#a86e3a"), cloth=ramp("#2c2420", "#443830", "#5e5044", "#7c6c5c"), acc=CLOCK, blade=STEEL, dark=BLACK, wrap=COPPER, wood=OAK, gem=STEAM, fire=STEAM, hot=STEAM)
def tinker(k):
    """the Spire's odd-job man: brass goggles with extra lenses swung down, every pocket full of tools, a wind-up key turning in his back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.2, -0.2, 9.0, 7.6, 9.2), "cloth", tag="head")
    a(h, C(0, 30.4, 0, 9.6, 2.8, 9.6), "leather", tag="leather_cap")
    a(h, C(0, 30.0, 1.4, 11.0, 0.7, 10.6), "leather", tag="cap_peak")
    a(h, C(0, 27.2, 4.3, 9.4, 1.0, 0.6), "dark", tag="goggle_strap")
    for s in SIDES:
        a(h, C(s * 2.2, 26.6, 4.7, 3.4, 3.2, 1.2), "acc", tag="goggle")
        k.fire(h, C(s * 2.2, 27.1, 5.35, 2.2, 2.2, 0.3))
        a(h, C(s * 5.2, 26.8, 2.8, 0.7, 2.0, 2.0), "acc", tag="goggle_pivot")
    a(h, C(-3.8, 29.6, 5.0, 2.2, 2.2, 0.6), "acc", tag="swing_lens", rots=(("x", -30),), pivot=(-3.8, 30, 4.4))
    a(h, C(0, 23.4, 4.4, 7.2, 2.2, 0.5), "dark", tag="soot_beard")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.8), "cloth", tag="shirt")
    a(c, C(0, 12.8, 2.6, 8.0, 10.4, 0.5), "leather", tag="tool_apron")
    for x, w, ht, tag, m in ((-3.0, 0.7, 4.2, "screwdriver", "blade"), (-1.6, 1.0, 3.0, "file", "acc"), (2.8, 1.4, 3.6, "spanner", "blade"), (0.8, 0.5, 3.2, "probe", "wrap")):
        a(c, C(x, 16.0, 3.0, w, ht, 0.4), m, tag=tag)
    a(c, C(0, 13.4, 3.0, 8.0, 3.6, 0.5), "leather", tag="pocket")
    a(c, C(0, 16.6, 3.2, 8.0, 0.5, 0.3), "dark", tag="pocket_edge")
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.6), "dark", tag="belt")
    a(c, C(-3.8, 8.4, 2.9, 1.4, 3.6, 1.4), "wrap", tag="oil_can")
    a(c, C(-3.8, 12.0, 2.9, 0.5, 1.8, 0.5), "wrap", tag="oil_spout", rots=(("x", -30),), pivot=(-3.8, 12, 2.9))
    a(b, C(0, 13.0, -3.2, 7.0, 10.0, 1.0), "leather", tag="back_strap")
    a(b, C(0, 18.0, -3.8, 4.0, 4.0, 1.0), "acc", tag="key_box")
    a(b, C(0, 19.6, -7.6, 1.2, 1.2, 7.0), "acc", tag="key_shaft")
    for t in (0, 90, 180, 270):
        a(b, C(0, 19.6, -11.2, 1.8, 6.0, 1.0), "acc", tag="key_wing", rots=(("z", t + 45),), pivot=(0, 20.2, -11.2))
    k.arms("cloth", "leather", cuff="acc", w=5.2)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.2, 21.2, 0, 5.4, 2.2, 5.4), "leather", tag="cop")
    a(k.arm(-1), C(-6.0, 11.0, 2.8, 3.0, 2.0, 1.0), "acc", tag="wrist_gadget")
    k.fire(k.arm(-1), C(-6.0, 11.6, 3.35, 1.2, 1.0, 0.3))
    k.legs("cloth", w=4.6)
    for s in SIDES:
        a(k.leg(s), C(s * 4.2, 7.0, 0, 1.2, 3.6, 2.6), "leather", tag="thigh_pouch")
    k.boots("leather", h=4.0, w=4.8, cuff="acc", toe="blade", toe_d=2.4)


@design(blade=CLOCK, dark=BLACK, acc=STEEL, gold=CLOCK, mail=ramp("#1a1208", "#2e2210", "#46361c", "#5e4a28"), gem=STEAM, leather=HIDE, cloth=CLOCK, fire=STEAM, hot=STEAM)
def brasswork(k):
    """nobody remembers if there was a man in it: a riveted brass automaton, a slit and a grille for a face, pistons working on the arms, cogs turning in the open chest"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.2, 0, 9.8, 9.4, 9.8), "blade", tag="drum_head")
    a(h, C(0, 22.6, 0, 11.0, 1.2, 11.0), "dark", tag="neck_ring")
    a(h, C(0, 32.6, 0, 11.0, 0.9, 11.0), "dark", tag="head_flange")
    a(h, C(0, 33.4, 0, 3.0, 2.0, 3.0), "acc", tag="steam_whistle")
    a(h, C(0, 28.4, 4.9, 7.6, 0.9, 0.4), "void", tag="eye_slit")
    k.fire(h, C(0, 28.6, 5.1, 6.0, 0.5, 0.3))
    a(h, C(0, 24.2, 4.9, 5.4, 2.6, 0.4), "dark", tag="grille")
    for x in (-1.8, -0.6, 0.6, 1.8):
        a(h, C(x, 24.2, 5.15, 0.5, 2.6, 0.3), "blade", tag="grille_bar")
    k.rivets(h, [(x, 31.4) for x in (-3.6, -1.8, 0, 1.8, 3.6)], 5.0, mat="acc")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.6), "blade", tag="boiler_body")
    a(c, C(0, 14.4, 3.35, 7.0, 7.6, 0.4), "dark", tag="open_chest")
    for x, y, w, m in ((-1.6, 16.8, 3.8, "acc"), (1.8, 15.0, 3.0, "gem"), (1.0, 18.6, 2.0, "acc")):
        for t in (0, 45):
            a(c, C(x, y, 3.55, w, w, 0.4), m, tag="open_cog", rots=(("z", t),), pivot=(x, y + w / 2, 3.55))
        a(c, C(x, y + w * 0.32, 3.8, w * 0.36, w * 0.36, 0.3), "dark", tag="cog_hole")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.2), "dark", tag="belt")
    k.rivets(c, [(x, 22.8) for x in (-3.4, -1.2, 1.2, 3.4)], 3.4, mat="acc")
    a(b, C(0, 13.0, -5.0, 8.0, 10.8, 4.0), "blade", tag="main_spring_case")
    a(b, C(0, 15.0, -7.1, 5.6, 6.4, 0.4), "dark", tag="spring_window")
    k.fire(b, C(0, 15.8, -7.35, 3.8, 4.8, 0.3))
    a(b, C(0, 17.8, -7.5, 3.8, 0.5, 0.3), "acc", tag="spring_coil")
    a(b, C(0, 16.2, -7.5, 3.8, 0.5, 0.3), "acc", tag="spring_coil")
    a(b, C(0, 19.4, -7.5, 3.8, 0.5, 0.3), "acc", tag="spring_coil")
    for s in SIDES:
        a(b, C(s * 2.8, 23.8, -5.0, 1.8, 5.0, 1.8), "dark", tag="exhaust")
        a(b, C(s * 2.8, 28.8, -5.0, 2.6, 0.9, 2.6), "blade", tag="exhaust_cap")
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.4, 1.0, 6.4), "dark", tag="cuff")
        a(p, C(x + s * 3.2, 11.4, 0, 1.2, 8.0, 1.2), "acc", tag="piston_rod")
        a(p, C(x + s * 3.2, 17.0, 0, 2.2, 4.0, 2.2), "dark", tag="piston_case")
        q = k.shoulder(s)
        a(q, C(x + s * 0.8, 20.5, 0, 7.6, 3.8, 7.8), "blade", tag="pauldron")
        a(q, C(x + s * 0.8, 24.0, 0, 3.6, 1.2, 3.6), "acc", tag="shoulder_bolt")
        k.rivets(q, [(x + s * (0.8 + t), 22.4) for t in (-2.0, 0, 2.0)], 3.95, mat="acc")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.0, 9.6, 5.0), "blade", tag="cuisse")
        a(p, C(y + s * 2.7, 3.0, 0, 1.0, 7.0, 1.0), "acc", tag="knee_piston")
        a(p, C(y, 4.8, 2.6, 3.8, 2.6, 0.8), "dark", tag="knee_joint")
    k.boots("blade", h=3.8, w=5.2, cuff="dark", sole="dark")


@design(blade=ramp("#14161a", "#262a30", "#3e444e", "#5a626e", "#808a96"), acc=CLOCK, gold=CLOCK, dark=BLACK, mail=ramp("#1a1208", "#2e2210", "#46361c", "#5e4a28"), gem=STEAM, leather=HIDE, wrap=COPPER, fire=STEAM, hot=STEAM)
def gearwright(k):
    """master of the great wheels: a smokestack helm, a gear as big as a shield on one shoulder and a bigger one behind him, cranked by a crank on the other"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.0, 0, 10.0, 8.6, 10.0), "blade", tag="helm")
    a(h, C(0, 26.4, 4.95, 8.0, 0.9, 0.4), "void", tag="slit")
    k.fire(h, C(0, 26.6, 5.15, 6.4, 0.5, 0.3))
    a(h, C(0, 22.8, 5.0, 5.0, 2.8, 0.6), "acc", tag="jaw_plate")
    for x, w, ht in ((-3.0, 3.0, 8.0), (3.0, 2.4, 5.6)):
        a(h, C(x, 31.6, -1.0, w, ht, w), "dark", tag="smokestack")
        a(h, C(x, 31.6 + ht, -1.0, w + 1.0, 0.9, w + 1.0), "acc", tag="smokestack_lip")
    a(h, C(0, 31.4, 0, 10.4, 1.0, 10.4), "acc", tag="brow")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.8), "blade", tag="cuirass")
    a(c, C(0, 13.4, 3.45, 6.0, 8.0, 0.5), "acc", tag="front_plate")
    for t in (0, 45):
        a(c, C(0, 15.6, 3.75, 4.6, 4.6, 0.4), "dark", tag="chest_gear", rots=(("z", t),), pivot=(0, 17.9, 3.75))
    k.fire(c, C(0, 17.2, 4.0, 1.4, 1.4, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.4), "dark", tag="belt")
    a(b, C(0, 13.0, -3.8, 7.6, 10.4, 1.6), "blade", tag="back_plate")
    cx, cy, cz = 0.0, 22.0, -6.2
    for t in range(12):
        a(b, C(cx, cy + 9.0, cz, 3.4, 4.4, 2.0), "acc", tag="great_gear_tooth", rots=(("z", t * 30),), pivot=(cx, cy, cz))
    a(b, C(cx, cy - 10, cz, 13.0, 20.0, 1.6), "acc", tag="great_gear")
    a(b, C(cx, cy - 6.6, cz, 20.0, 13.2, 1.6), "acc", tag="great_gear")
    a(b, C(cx, cy - 8.4, cz, 17.0, 16.8, 1.6), "acc", tag="great_gear")
    a(b, C(cx, cy - 5.4, cz, 9.6, 10.8, 1.7), "dark", tag="gear_well")
    for t in range(4):
        a(b, C(cx, cy, cz - 0.1, 1.6, 7.0, 1.8), "acc", tag="gear_spoke", rots=(("z", 45 + t * 90),), pivot=(cx, cy, cz))
    a(b, C(cx, cy - 1.8, cz, 3.6, 3.6, 2.0), "blade", tag="gear_hub")
    k.fire(b, C(cx, cy - 0.8, cz - 1.15, 1.6, 1.6, 0.3))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.0, 0, 6.2, 5.8, 6.2), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.6, 1.0, 6.6), "acc", tag="cuff")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.1, 9.6, 5.1), "blade", tag="cuisse")
        a(p, C(y + s * 2.8, 3.0, 0, 1.0, 7.0, 1.0), "acc", tag="knee_piston")
        a(p, C(y, 4.8, 2.6, 4.0, 2.8, 1.0), "dark", tag="poleyn")
    q, x = k.shoulder(1), 6.0
    a(q, C(x + 1.0, 20.5, 0, 7.8, 3.4, 8.0), "blade", tag="pauldron")
    for t in range(8):
        a(q, C(x + 4.4, 27.2, 0, 0.9 + 0.8, 3.6, 2.4), "acc", tag="shoulder_gear_tooth", rots=(("x", t * 45),), pivot=(x + 4.4, 25.4 - 0.0, 0))
    a(q, C(x + 4.4, 21.6, 0, 1.4, 7.4, 7.4), "acc", tag="shoulder_gear")
    a(q, C(x + 4.4, 23.8, 0, 1.6, 3.2, 3.2), "dark", tag="shoulder_gear_hub")
    q, x = k.shoulder(-1), -6.0
    a(q, C(x - 1.0, 20.5, 0, 7.8, 3.4, 8.0), "blade", tag="pauldron")
    a(q, C(x - 1.0, 23.9, 0, 1.4, 3.2, 1.4), "dark", tag="crank_shaft")
    a(q, C(x - 2.4, 27.0, 0, 4.2, 1.4, 1.4), "acc", tag="crank_arm")
    a(q, C(x - 4.0, 27.0, 0, 1.4, 4.0, 1.4), "dark", tag="crank_handle")
    k.boots("blade", h=4.2, w=5.4, cuff="acc", sole="dark", toe="dark", toe_d=2.6)


# ---------------------------------------------------------------- the Coiled Spire

@design(scale=SERPENT, cloth=SERPENT, wrap=GILT, dark=BLACK, acc=GILT, gold=GILT, gem=VENOM, leather=HIDE, blade=SERPENT, fire=VENOM, hot=VENOM)
def scaleguard(k):
    """the priest of the Coiled King: a cobra's hood spread around the head, gold banding down its throat, a robe that sheds in long strips"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.0, 8.0, 9.2), "scale", tag="hood")
    a(h, C(0, 26.6, 4.45, 6.8, 3.4, 0.4), "void", tag="face_dark")
    for s in SIDES:
        k.fire(h, C(s * 1.8, 28.0, 4.65, 1.2, 0.7, 0.3))
        for i, (dx, y0, ht) in enumerate(((6.4, 23.0, 14.0), (9.4, 24.6, 11.0), (12.2, 26.4, 7.4))):
            a(h, C(s * dx, y0, -1.0 - i * 0.2, 3.2, ht, 1.0), "scale", tag="cobra_hood")
        a(h, C(s * 7.0, 28.2, -0.4, 2.4, 4.0, 0.4), "wrap", tag="hood_eye")
        a(h, C(s * 7.0, 29.0, -0.15, 1.2, 2.4, 0.3), "dark", tag="hood_eye_core")
    a(h, C(0, 32.0, -1.0, 11.6, 5.2, 1.0), "scale", tag="cobra_hood")
    a(h, C(0, 37.0, -1.0, 8.0, 1.4, 1.0), "scale", tag="cobra_hood")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    for y in (13.2, 15.2, 17.2, 19.2, 21.2):
        a(c, C(0, y, 2.75, 4.2, 1.0, 0.5), "wrap", tag="throat_band")
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.8), "wrap", tag="sash")
    k.fire(c, C(0, 11.8, 3.05, 1.6, 1.6, 0.3))
    for i, x in enumerate((-3.4, -1.2, 1.2, 3.4)):
        ln = (16.0, 21.0, 18.0, 14.0)[i]
        a(b, C(x, 23.0 - ln, -3.4, 1.8, ln, 0.5), "scale", tag="shed_strip", rots=(("x", 7 + i), ("z", x)), pivot=(x, 23, -3.4))
    k.arms("cloth", "scale", cuff="wrap", w=5.4)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.3, 21.0, 0, 5.8, 2.4, 5.8), "scale", tag="mantle")
    k.legs("cloth", w=4.6)
    k.boots("scale", h=2.8, w=4.8, cuff="wrap")


@design(fur=JAGUAR, leather=JAGUAR, blade=ramp("#0c0c10", "#1e1e24", "#34343c", "#50505a", "#7a7a86"), wood=OAK, dark=BLACK, acc=QUETZAL, gem=QUETZAL, bone=BONE, cloth=ramp("#6a1408", "#8e1e0c", "#b43014", "#d84a20"), feather=QUETZAL, fire=VENOM, hot=VENOM)
def jaguar(k):
    """a jaguar knight: his face looking out of the cat's open jaws, spotted pelt to the wrists, and a wooden club edged with black glass"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 22.8, -0.2, 9.6, 2.6, 9.8), "fur", tag="lower_jaw")
    a(h, C(0, 28.8, -0.2, 10.8, 5.4, 11.2), "fur", tag="cat_head")
    a(h, C(0, 30.4, 6.0, 7.0, 3.6, 3.0), "fur", tag="cat_muzzle")
    a(h, C(0, 32.0, 7.6, 2.4, 1.2, 0.5), "dark", tag="cat_nose")
    a(h, C(0, 25.0, -2.0, 9.0, 3.8, 6.6), "fur", tag="cat_neck")
    a(h, C(0, 25.0, 3.6, 7.4, 4.0, 0.4), "cloth", tag="face")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 27.2, 3.85, 1.4, 0.7, 0.3))
        a(h, C(s * 3.4, 32.2, 5.6, 1.6, 1.2, 0.5), "gem", tag="cat_eye")
        a(h, C(s * 4.2, 33.8, -1.0, 2.4, 2.4, 1.4), "fur", tag="cat_ear")
        a(h, C(s * 2.8, 29.0, 5.8, 1.4, 1.0, 2.4), "bone", tag="cat_fang_root")
        k.spike(h, s * 2.8, 29.4, 6.8, -3.4, 1.2, "bone", tag="cat_fang", steps=2)
        k.spike(h, s * 2.8, 24.8, 4.0, 2.2, 1.0, "bone", tag="cat_fang", steps=2)
    for x, y, z in ((-3.4, 34.2, 1.0), (2.4, 34.2, 3.4), (0.4, 34.2, -2.0), (5.4, 31.0, 1.6), (-5.4, 30.0, 3.6)):
        a(h, C(x, y, z, 1.2, 0.3, 1.2), "dark", tag="rosette") if y > 33 else a(h, C(x, y, z, 0.3, 1.2, 1.2), "dark", tag="rosette")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.8), "fur", tag="pelt_tunic")
    for x, y in ((-2.8, 21.0), (0.8, 20.0), (3.0, 17.6), (-1.6, 17.0), (2.0, 14.4), (-3.0, 14.0), (0, 14.8)):
        a(c, C(x, y, 2.55, 1.5, 1.5, 0.3), "dark", tag="rosette")
        a(c, C(x, y + 0.4, 2.7, 0.7, 0.7, 0.3), "fur", tag="rosette_core")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 5.6), "cloth", tag="sash")
    a(c, C(0, 6.0, 2.8, 3.0, 6.2, 0.5), "cloth", tag="loin_panel")
    a(c, C(0, 6.0, 3.1, 3.0, 0.9, 0.3), "gem", tag="loin_stripe")
    a(b, C(0, 13.0, -3.0, 7.2, 10.0, 0.8), "fur", tag="pelt_back")
    k.tail(b, 0, 13.0, -3.4, 12.0, 2.0, "fur", lean=10, tag="jaguar_tail")
    rz = (("z", -30),)
    a(b, C(0, 8.0, -4.2, 3.0, 26.0, 1.0), "wood", tag="macuahuitl", rots=rz, pivot=(0, 18, -4.2))
    for y in (17.0, 19.6, 22.2, 24.8, 27.4, 30.0):
        for s in SIDES:
            a(b, C(s * 2.1, y, -4.2, 1.6, 2.2, 0.5), "blade", tag="glass_blade", rots=rz, pivot=(0, 18, -4.2))
    for i, (t, ln) in enumerate(((-30, 7.0), (-12, 9.0), (8, 9.0), (28, 7.0))):
        a(b, C(0, 22.8, -3.8, 1.4, ln, 0.5), "feather", tag="plume", rots=(("z", t),), pivot=(0, 22.8, -3.8))
    k.arms("fur", "fur", joint="fur", cuff="cloth", w=5.0)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.2, 21.2, 0, 5.4, 2.2, 5.4), "fur", tag="pelt_shoulder")
        a(k.arm(s), C(s * 6.0, 13.0, 2.65, 1.5, 1.5, 0.3), "dark", tag="rosette")
    k.legs("fur", w=4.6)
    for s in SIDES:
        a(k.leg(s), C(s * 1.95, 8.0, 2.45, 1.5, 1.5, 0.3), "dark", tag="rosette")
        a(k.leg(s), C(s * 2.8, 4.2, 2.45, 1.5, 1.5, 0.3), "dark", tag="rosette")
    k.boots("cloth", h=2.0, w=4.8, cuff="gem", sole="dark")


@design(scale=SERPENT, blade=SERPENT, dark=BLACK, acc=GILT, gold=GILT, mail=SERPENT, leather=HIDE, wrap=ramp("#5a4408", "#8c6c10", "#c49c20", "#ecc848"), gem=VENOM, bone=BONE, cloth=SERPENT, fire=VENOM, hot=VENOM)
def venomweave(k):
    """he let them nest: fanged mouth open across the visor, two live pit vipers wound round the arms, and a third lifting from the shoulders to look over his head"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.6, 0, 10.0, 8.8, 10.0), "scale", tag="helm")
    a(h, C(0, 25.0, 4.95, 8.4, 4.4, 0.4), "void", tag="maw")
    a(h, C(0, 27.8, 5.0, 8.8, 1.6, 0.7), "scale", tag="upper_lip")
    k.fire(h, C(0, 25.8, 5.15, 5.4, 1.4, 0.3))
    for s in SIDES:
        k.spike(h, s * 3.0, 27.8, 5.2, -4.4, 1.6, "bone", tag="viper_fang", steps=3)
        a(h, C(s * 3.0, 30.0, 5.0, 2.2, 1.4, 0.6), "gem", tag="slit_eye")
    a(h, C(0, 32.2, 0, 8.0, 1.0, 8.0), "wrap", tag="top_band")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.0), "scale", tag="hauberk")
    a(c, C(0, 13.6, 3.05, 6.4, 8.8, 0.5), "dark", tag="diamond_field")
    for y in (14.0, 16.4, 18.8):
        a(c, C(0, y, 3.35, 2.4, 2.4, 0.4), "wrap", tag="rattle_diamond", rots=(("z", 45),), pivot=(0, y + 1.2, 3.35))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 6.6), "wrap", tag="belt")
    for x in (-3.2, -1.6, 1.6, 3.2):
        a(c, C(x, 11.0, 3.4, 1.1, 2.6, 1.1), "wrap", tag="vial_cap")
        k.fire(c, C(x, 11.3, 3.95, 0.8, 1.8, 0.3))
    a(b, C(0, 13.0, -3.4, 7.2, 10.0, 1.2), "scale", tag="back")
    path = [(0, 13.0, -4.6, 3.0), (2.4, 16.0, -5.0, 2.8), (-2.2, 18.6, -5.0, 2.8), (2.0, 21.0, -5.0, 2.6), (-1.4, 24.0, -5.2, 2.4), (0.8, 27.0, -5.2, 2.2), (-0.4, 30.0, -4.8, 2.2), (0, 33.0, -4.2, 2.2), (0, 35.4, -2.8, 2.2), (0, 36.8, -0.8, 2.2), (0, 37.4, 1.2, 2.4)]
    for x, y, z, w in path:
        a(b, C(x, y, z, w, 3.2, w), "scale", tag="viper_coil")
    for (x0, y0, z0, w0), (x1, y1, z1, _) in zip(path, path[1:]):
        a(b, C((x0 + x1) / 2, y1 - 0.4, (z0 + z1) / 2, abs(x0 - x1) + w0 * 0.8, 2.0, w0 * 0.9 + abs(z0 - z1)), "scale", tag="viper_coil")
    a(b, C(0, 36.6, 3.2, 4.2, 2.4, 4.4), "scale", tag="viper_head")
    a(b, C(0, 37.0, 5.45, 3.2, 0.8, 0.3), "void", tag="viper_mouth")
    k.fire(b, C(0, 37.2, 5.6, 2.2, 0.4, 0.3))
    for s in SIDES:
        a(b, C(s * 1.8, 38.4, 4.0, 0.9, 0.7, 0.8), "gem", tag="viper_eye")
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.0, 0, 5.4, 5.8, 5.4), "leather", tag="bracer")
        for i, y in enumerate((11.2, 12.4, 13.6, 14.8, 16.0)):
            t = i * 70 + (0 if s > 0 else 180)
            a(p, C(x, y, 0, 6.6, 1.3, 2.6), "scale", tag="arm_viper", rots=(("y", t),), pivot=(x, y, 0))
            a(p, C(x, y, 0, 2.6, 1.3, 6.6), "scale", tag="arm_viper", rots=(("y", t),), pivot=(x, y, 0))
        a(p, C(x + s * 0.8, 9.2, 3.4, 3.0, 2.0, 3.6), "scale", tag="arm_viper_head")
        a(p, C(x + s * 0.8, 9.8, 5.25, 2.0, 0.4, 0.3), "void", tag="viper_mouth")
        q = k.shoulder(s)
        a(q, C(x + s * 0.8, 20.6, 0, 7.0, 3.2, 7.2), "scale", tag="pauldron")
        a(q, C(x + s * 0.8, 20.3, 0, 7.4, 0.9, 7.6), "wrap", tag="pauldron_rim")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 4.9, 9.6, 4.9), "scale", tag="scale_leg")
        a(p, C(y, 6.2, 2.5, 3.8, 5.8, 0.6), "wrap", tag="tasset")
    k.boots("leather", h=4.2, w=5.0, cuff="wrap", toe="dark", toe_d=2.6)


@design(feather=QUETZAL, blade=GILT, acc=QUETZAL, gold=GILT, gem=QUETZAL, stone=ramp("#0c2a20", "#124034", "#1a5e4a", "#267e62", "#38a080"), dark=BLACK, mail=QUETZAL, cloth=ramp("#6a1408", "#8e1e0c", "#b43014", "#d84a20"), leather=HIDE, wrap=GILT, fire=VENOM, hot=VENOM)
def plumed(k):
    """the feathered serpent's champion: a vast fan of quetzal plumes taller than a man's arm, a gold and jade mask, a serpent's coil carved around the chest"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.2, 0, 10.0, 8.8, 10.0), "blade", tag="gold_helm")
    a(h, C(0, 23.6, 4.95, 8.0, 7.6, 0.6), "stone", tag="jade_mask")
    a(h, C(0, 26.6, 5.3, 1.6, 2.8, 0.7), "blade", tag="mask_nose")
    a(h, C(0, 24.6, 5.3, 4.2, 0.7, 0.3), "void", tag="mask_mouth")
    for s in SIDES:
        a(h, C(s * 2.2, 28.2, 5.3, 2.0, 1.0, 0.3), "void", tag="mask_eye")
        k.fire(h, C(s * 2.2, 28.4, 5.45, 1.2, 0.6, 0.3))
        a(h, C(s * 5.6, 26.0, 1.4, 1.2, 3.4, 3.4), "stone", tag="ear_spool")
        a(h, C(s * 6.25, 26.8, 1.4, 0.3, 1.8, 1.8), "blade", tag="ear_spool_core")
    a(h, C(0, 31.6, 0, 11.2, 2.0, 11.2), "blade", tag="crown_band")
    for i in range(8):
        a(h, C(-4.9 + i * 1.4, 32.0, 5.7, 1.0, 1.2, 0.4), "cloth" if i % 2 else "stone", tag="crown_tile")
    for i, t in enumerate(range(-96, 97, 12)):
        ln = 21.0 - abs(t) * 0.05 + (i % 2) * 2.6
        a(h, C(0, 33.2, -3.2, 2.6, ln, 0.6), "feather", tag="quetzal_plume", rots=(("z", t),), pivot=(0, 33.0, -3.2))
        a(h, C(0, 33.2 + ln - 1.4, -3.5, 2.4, 1.4, 0.3), "cloth", tag="plume_tip", rots=(("z", t),), pivot=(0, 33.0, -3.2))
    for i, t in enumerate(range(-84, 85, 14)):
        a(h, C(0, 33.2, -2.6, 2.0, 7.4, 0.5), "cloth", tag="plume_inner", rots=(("z", t),), pivot=(0, 33.0, -3.2))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.4), "blade", tag="cuirass")
    for i in range(6):
        r = math.radians(i * 60)
        x, y = math.sin(r) * 2.6, 17.8 + math.cos(r) * 2.6
        a(c, C(x, y - 0.8, 3.3, 1.8, 1.8, 0.5), "stone", tag="serpent_coil")
    a(c, C(0, 16.8, 3.6, 2.0, 2.0, 0.4), "wrap", tag="serpent_eye_seat")
    k.fire(c, C(0, 17.2, 3.85, 1.2, 1.2, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.6, 7.0), "cloth", tag="sash")
    a(c, C(0, 5.4, 3.4, 3.4, 6.8, 0.5), "cloth", tag="loin_panel")
    a(b, C(0, 13.0, -3.8, 7.6, 10.4, 1.6), "blade", tag="back_plate")
    k.cape("feather", width=8.0, top=23.0, length=19.0, lean=8, z=-4.6, tag="feather_cape")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "blade", tag="vambrace")
        for y in (11.8, 14.2):
            a(p, C(x, y, 0, 6.3, 1.0, 6.3), "stone", tag="jade_band")
        q = k.shoulder(s)
        a(q, C(x + s * 1.0, 20.5, 0, 7.8, 3.6, 8.0), "blade", tag="pauldron")
        for i, (t, ln) in enumerate(((26, 10.0), (50, 9.0), (74, 8.0))):
            a(q, C(x + s * 3.0, 21.6, -0.4 - i * 0.6, 2.2, ln, 0.6), "feather", tag="shoulder_plume", rots=(("z", -s * t),), pivot=(x + s * 3, 21.6, -0.4))
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.1, 9.6, 5.1), "blade", tag="cuisse")
        a(p, C(y, 4.8, 2.6, 3.8, 2.6, 0.9), "stone", tag="poleyn")
        a(p, C(y, 8.0, 0, 5.4, 1.2, 5.4), "cloth", tag="thigh_band")
    k.boots("blade", h=4.0, w=5.2, cuff="stone", toe="dark", toe_d=2.6)


# ---------------------------------------------------------------- Rimeholt

@design(cloth=ramp("#1a2230", "#283444", "#3a4a5c", "#506474", "#6c8294"), fur=NORSEFUR, stone=ramp("#34383e", "#4e545a", "#6e7478", "#92989a"), wood=OAK, wrap=HEMP, dark=BLACK, acc=RUNE, gem=RUNE, leather=HIDE, blade=IRON, fire=RUNE, hot=RUNE)
def runeseer(k):
    """the jarl's seer: a heavy fur mantle, a bone blindfold of carved rune staves, a staff hung with stones, each stone's rune lit from inside"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.4, 9.4, 8.2, 9.2), "cloth", tag="hood")
    a(h, C(0, 26.8, 4.25, 8.0, 2.4, 0.6), "stone", tag="rune_band")
    for x in (-2.8, -0.9, 0.9, 2.8):
        k.fire(h, C(x, 27.2, 4.65, 0.5, 1.4, 0.3))
    a(h, C(0, 22.8, 4.4, 5.0, 3.6, 0.9), "wrap", tag="grey_beard")
    a(h, C(0, 20.8, 4.4, 3.0, 2.2, 0.9), "wrap", tag="grey_beard")
    a(h, C(0, 22.4, 0, 11.8, 3.6, 11.4), "fur", tag="fur_collar")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 18.4, 0, 8.7, 5.6, 6.2), "fur", tag="fur_mantle")
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.8), "wrap", tag="rope_belt")
    for x, ln in ((-3.0, 2.6), (-1.0, 4.0), (1.0, 2.0), (3.0, 3.4)):
        k.tail(c, x, 12.2, 3.1, ln, 0.3, "wrap", tag="string")
        a(c, C(x, 12.2 - ln - 2.0, 3.1, 1.6, 2.2, 0.7), "stone", tag="rune_stone")
        k.fire(c, C(x, 12.2 - ln - 1.6, 3.55, 0.4, 1.4, 0.3))
    a(b, C(0, 4.0, -3.6, 9.0, 19.0, 1.0), "fur", tag="fur_cloak", rots=(("x", 6),), pivot=(0, 23, -3.6))
    rz = (("z", -10),)
    a(b, C(-3.0, 2.0, -5.0, 1.2, 40.0, 1.2), "wood", tag="staff", rots=rz, pivot=(-3, 20, -5.0))
    for y, l in ((40.0, 3.0), (36.0, 4.0), (32.0, 3.4)):
        a(b, C(-3.0, y - l, -5.0, 3.2, l, 1.0), "stone", tag="staff_stone", rots=rz, pivot=(-3, 20, -5.0))
        a(b, C(-3.0, y - l + 0.4, -5.6, 0.6, l - 0.8, 0.3), "glow", group="fire", tag="staff_rune", rots=rz, pivot=(-3, 20, -5.0))
    k.arms("cloth", "wrap", cuff="fur", w=5.4)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.4, 20.6, 0, 6.8, 3.4, 7.0), "fur", tag="fur_shoulder")
    k.legs("cloth", w=4.6)
    k.boots("fur", h=3.8, w=5.0, sole="dark")


@design(fur=ramp("#3a3a40", "#56565c", "#74747a", "#94949a", "#b8b8be", "#dcdce0"), leather=HIDE, dark=BLACK, blade=STEEL, wood=OAK, bone=BONE, acc=ramp("#3e0a0a", "#5e1010", "#841a1a", "#a82a24"), wrap=PALE, fire=RUNE, hot=RUNE)
def wolfskin(k):
    """a berserker under a whole wolf: the head worn as a hood with the jaws over the brow, the paws crossed on the chest, blood-painted arms and a pair of axes"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.8, 9.2, 7.0, 8.6), "dark", tag="under_hood")
    a(h, C(0, 30.2, -0.6, 10.4, 4.8, 11.0), "fur", tag="wolf_head")
    a(h, C(0, 30.6, 6.0, 5.4, 3.0, 4.4), "fur", tag="wolf_muzzle")
    a(h, C(0, 32.4, 8.2, 1.8, 1.0, 0.5), "dark", tag="wolf_nose")
    a(h, C(0, 29.6, 6.6, 5.0, 1.0, 3.6), "void", tag="wolf_mouth")
    for s in SIDES:
        a(h, C(s * 3.0, 33.8, 5.4, 1.4, 0.9, 0.3), "glow", group="fire", tag="wolf_eye")
        a(h, C(s * 4.0, 34.8, -1.2, 2.6, 3.8, 1.4), "fur", tag="wolf_ear")
        k.spike(h, s * 2.2, 30.6, 7.6, -3.0, 1.0, "bone", tag="wolf_fang", steps=2)
        k.fire(h, C(s * 2.0, 28.0, 3.5, 1.2, 0.7, 0.3))
    a(h, C(0, 26.4, 3.4, 7.6, 3.4, 0.4), "acc", tag="war_paint")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.6), "wrap", tag="bare_chest")
    a(c, C(0, 21.6, 0, 8.7, 2.4, 5.8), "fur", tag="fur_shoulders")
    for s in SIDES:
        a(c, C(s * 2.4, 13.4, 2.45, 1.4, 8.4, 0.4), "acc", tag="blood_stripe")
        a(c, C(s * 1.2, 16.8, 2.75, 5.6, 2.2, 0.6), "fur", tag="wolf_paw", rots=(("z", s * 28),), pivot=(s * 1.2, 18, 2.75))
    a(c, C(0, 12.2, 0, 8.7, 2.0, 5.4), "leather", tag="wide_belt")
    a(b, C(0, 6.0, -3.2, 9.4, 17.0, 1.2), "fur", tag="wolf_back", rots=(("x", 5),), pivot=(0, 23, -3.2))
    k.spike(b, 0, 7.4, -4.0, -8.0, 3.2, "fur", rx=-6, tag="wolf_tail", steps=4)
    for s in SIDES:
        rz = (("z", -s * 34),)
        a(b, C(s * 1.6, 8.0, -5.2, 1.2, 22.0, 1.2), "wood", tag="axe_haft", rots=rz, pivot=(s * 1.6, 18, -5.2))
        a(b, C(s * 3.4, 26.0, -5.2, 5.0, 4.4, 0.7), "blade", tag="axe_head", rots=rz, pivot=(s * 1.6, 18, -5.2))
        a(b, C(s * 5.8, 24.4, -5.2, 1.4, 7.6, 0.6), "blade", tag="axe_edge", rots=rz, pivot=(s * 1.6, 18, -5.2))
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "wrap", tag="bare_arm")
        k.elbow(s, "wrap")
        a(p, C(x, 11.4, 0, 5.2, 5.4, 5.2), "acc", tag="blood_forearm")
        a(p, C(x, 16.4, 0, 5.5, 0.9, 5.5), "leather", tag="tie")
        a(k.shoulder(s), C(x + s * 0.4, 21.0, 0, 6.2, 3.0, 6.2), "fur", tag="fur_shoulder")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 4.6, 9.6, 4.6), "leather", tag="leg")
        a(p, C(y, 7.6, 0, 5.2, 4.4, 5.2), "fur", tag="fur_skirt")
        for yy in (3.2, 4.8):
            a(p, C(y, yy, 0, 4.9, 0.6, 4.9), "wrap", tag="legging_tie")
    k.boots("fur", h=3.4, w=4.8, sole="dark")


@design(blade=STEEL, mail=STEEL, dark=BLACK, wood=ramp("#3a1608", "#5a240e", "#7e3618", "#a44c24"), fur=NORSEFUR, cloth=ramp("#0c2a4a", "#163e68", "#22568c", "#3272b0"), leather=HIDE, acc=BRASS, wrap=WHITEWASH, gem=RUNE, fire=RUNE, hot=RUNE)
def huskarl(k):
    """the jarl's sworn man: a spectacle helm with a mail curtain, a painted round shield slung on his back, a thick fur over the mail"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 28.0, 0, 9.8, 4.8, 9.8), "blade", tag="bowl_helm")
    a(h, C(0, 32.8, 0, 6.8, 1.2, 6.8), "blade", tag="helm_cap")
    a(h, C(0, 33.8, 0, 1.2, 1.2, 1.2), "acc", tag="helm_finial")
    a(h, C(0, 31.6, 0, 1.0, 1.6, 10.2), "acc", tag="helm_ridge")
    a(h, C(0, 22.8, 0, 10.0, 5.2, 10.0), "mail", tag="mail_curtain")
    a(h, C(0, 28.0, 5.0, 10.0, 1.0, 0.5), "acc", tag="brow_band")
    a(h, C(0, 24.4, 5.1, 1.2, 4.6, 0.6), "blade", tag="nasal")
    for s in SIDES:
        a(h, C(s * 2.5, 26.2, 5.05, 3.6, 2.8, 0.5), "blade", tag="spectacle")
        a(h, C(s * 2.5, 26.7, 5.2, 2.4, 1.8, 0.4), "void", tag="spectacle_hole")
        k.fire(h, C(s * 2.5, 27.0, 5.35, 1.2, 0.8, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.6), "mail", tag="hauberk")
    a(c, C(0, 19.2, 0, 8.7, 4.8, 6.4), "fur", tag="fur_over")
    a(c, C(0, 12.2, 0, 8.7, 1.6, 6.2), "leather", tag="belt")
    a(c, C(0, 11.6, 3.1, 2.8, 2.6, 0.7), "acc", tag="buckle")
    a(c, C(3.8, 2.0, 1.4, 1.0, 10.0, 2.0), "wood", tag="scabbard")
    a(b, C(0, 13.2, -3.4, 7.0, 9.8, 1.0), "fur", tag="fur_back")
    cy = 17.4
    for w, ht in ((17.0, 8.0), (14.0, 12.0), (10.0, 15.0), (6.0, 17.0)):
        a(b, C(0, cy - ht / 2, -5.0, w, ht, 1.0), "wood", tag="round_shield")
    for t in range(8):
        a(b, C(0, cy, -5.6, 1.6 if t % 2 else 1.0, 8.4, 0.3), "cloth" if t % 2 == 0 else "wrap", tag="shield_paint", rots=(("z", t * 45),), pivot=(0, cy, -5.6))
    for t in range(16):
        a(b, C(0, cy + 8.2, -5.0, 3.6, 0.9, 1.2), "blade", tag="shield_rim", rots=(("z", t * 22.5),), pivot=(0, cy, -5.0))
    a(b, C(0, cy - 2.0, -5.8, 4.0, 4.0, 1.0), "blade", tag="shield_boss")
    a(b, C(0, cy - 1.0, -6.4, 2.0, 2.0, 0.5), "acc", tag="shield_boss_top")
    k.arms("mail", "leather", cuff="acc", w=5.2)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.4, 20.6, 0, 6.6, 3.2, 6.8), "fur", tag="fur_shoulder")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 6.2, 0, 5.1, 5.8, 5.1), "mail", tag="mail_skirt")
        a(p, C(x, 2.2, 0, 4.7, 4.0, 4.7), "cloth", tag="leg_wrap")
        for yy in (3.0, 4.6):
            a(p, C(x, yy, 0, 5.0, 0.6, 5.0), "leather", tag="winnegans")
    k.legs("cloth", w=4.5)
    k.boots("leather", h=2.8, w=4.8, cuff="fur")


@design(stone=ramp("#2a3440", "#42505e", "#5e7080", "#8096a4", "#a8bcc8", "#d0e0e8"), blade=ramp("#2a3440", "#42505e", "#5e7080", "#8096a4", "#a8bcc8"), dark=BLACK, gem=ICE, bone=ramp("#6a7078", "#8c949c", "#b0b8c0", "#d4dce0", "#f0f4f6"), mail=STEEL, fur=NORSEFUR, leather=HIDE, acc=RUNE, fire=RUNE, hot=RUNE)
def giantplate(k):
    """a frost giant's child's armour, far too big for you: a horned stone helm, slabs of rune-cut rock on the shoulders, chained with iron rings as thick as your wrist"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 22.8, 0, 11.4, 10.6, 11.4), "stone", tag="great_helm")
    a(h, C(0, 33.2, 0, 8.4, 1.4, 8.4), "stone", tag="helm_top")
    a(h, C(0, 26.4, 5.65, 9.4, 1.4, 0.5), "void", tag="slit")
    k.fire(h, C(0, 26.8, 5.85, 7.6, 0.7, 0.3))
    a(h, C(0, 22.8, 5.65, 1.6, 3.4, 0.5), "dark", tag="chin_rune")
    k.fire(h, C(0, 29.0, 5.8, 0.7, 3.6, 0.3))
    k.fire(h, C(0, 30.2, 5.8, 3.0, 0.6, 0.3))
    for s in SIDES:
        k.horn(h, s * 5.6, 30.4, 0, [(6.0, -s * 80, 4.2), (6.0, -s * 34, 3.4), (6.0, s * 4, 2.6), (5.0, s * 26, 1.6), (3.4, s * 36, 0.8)], "bone")
        a(h, C(s * 6.0, 29.0, 0, 1.2, 4.0, 5.4), "dark", tag="horn_collar")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 7.2), "stone", tag="breast_slab")
    for x, y, w, ht in ((0, 19.4, 0.8, 3.6), (0, 21.0, 3.4, 0.7), (-2.4, 14.0, 0.7, 4.4), (-1.6, 15.8, 1.8, 0.7), (2.4, 14.0, 0.7, 4.4), (1.6, 16.4, 1.8, 0.7)):
        k.fire(c, C(x, y, 3.65, w, ht, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.6, 7.8), "dark", tag="belt")
    a(b, C(0, 13.0, -4.2, 7.8, 10.6, 2.0), "stone", tag="back_slab")
    for s in SIDES:
        for i in range(5):
            a(b, C(s * (2.4 + i * 0.3), 13.0 + i * 2.4, -5.4, 2.4, 1.6, 1.0), "dark", tag="chain_ring")
            a(b, C(s * (2.4 + i * 0.3), 13.4 + i * 2.4, -5.5, 1.0, 0.8, 1.2), "void", tag="chain_hole")
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 10.6, 0, 6.6, 6.2, 6.6), "stone", tag="forearm_slab")
        a(p, C(x, 16.4, 0, 7.0, 1.0, 7.0), "dark", tag="cuff")
        k.fire(p, C(x, 12.4, 3.35, 0.6, 2.8, 0.3))
        q = k.shoulder(s)
        a(q, C(x + s * 1.8, 20.5, 0, 10.4, 5.4, 11.0), "stone", tag="shoulder_slab")
        a(q, C(x + s * 1.8, 25.8, 0, 8.6, 2.2, 9.0), "stone", tag="shoulder_slab")
        a(q, C(x + s * 1.8, 27.9, 0, 5.8, 1.2, 6.2), "dark", tag="shoulder_cap")
        k.fire(q, C(x + s * 1.8, 21.8, 5.55, 0.7, 3.4, 0.3))
        k.fire(q, C(x + s * 1.8, 23.2, 5.55, 3.0, 0.6, 0.3))
        a(q, C(x + s * 7.2, 21.0, 0, 1.4, 1.4, 4.0), "dark", tag="shoulder_ring")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.4, 9.6, 5.4), "stone", tag="cuisse")
        a(p, C(y, 4.6, 2.8, 4.2, 3.0, 1.0), "dark", tag="poleyn")
    k.boots("stone", h=4.4, w=5.8, cuff="dark", sole="dark")


# ---------------------------------------------------------------- the Glass Minaret

@design(cloth=ramp("#6a5a44", "#8a7a60", "#ac9c80", "#ccc0a4", "#e8e0cc"), cloth2=TURQUOISE, wrap=TURQUOISE, dark=BLACK, acc=GILT, gold=GILT, gem=SUNFIRE, leather=HIDE, blade=MIRROR, fire=SUNFIRE, hot=SUNFIRE)
def sandwraith(k):
    """nothing is under the veils: wind-blown layers of pale silk, a hanging glass lamp with a sliver of the sun in it, the eyes just a shimmer"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.2, -0.4, 9.8, 9.6, 9.6), "cloth", tag="veil_head")
    a(h, C(0, 26.8, 4.45, 7.8, 2.0, 0.4), "void", tag="eye_gap")
    a(h, C(0, 27.2, 4.65, 6.0, 0.8, 0.3), "glow", tag="eye_shimmer")
    a(h, C(0, 22.6, 3.6, 9.8, 4.2, 1.4), "cloth2", tag="face_veil")
    a(h, C(0, 30.6, 0, 10.6, 1.4, 10.6), "acc", tag="head_chain")
    k.tail(h, 0, 30.8, 5.0, 3.0, 1.0, "acc", tag="brow_drop")
    for i, (x, r, ln) in enumerate(((-3.4, 46, 16.0), (0.0, 54, 18.0), (3.4, 62, 16.0))):
        a(h, C(x, 31.6 - ln, -4.6, 3.0, ln, 0.5), "cloth2" if i == 1 else "cloth", tag="streaming_veil", rots=(("x", r),), pivot=(x, 31.6, -4.6))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="silk_robe")
    for r in (22, -22):
        a(c, C(0, 12.2, 2.75, 8.2, 11.4, 0.4), "cloth2", tag="wrapped_silk", rots=(("z", r),), pivot=(0, 18, 2.75))
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.8), "acc", tag="belt")
    a(b, C(0, 24.0, -3.4, 13.0, 1.0, 1.0), "acc", tag="lamp_yoke")
    a(b, C(0, 2.0, -3.6, 8.2, 20.0, 0.6), "cloth", tag="back_silk", rots=(("x", 16),), pivot=(0, 22, -3.6))
    for i, (x, r, ln) in enumerate(((-4.0, 36, 20.0), (0, 28, 24.0), (4.0, 40, 18.0))):
        a(b, C(x, 22.0 - ln, -4.6, 2.6, ln, 0.5), "cloth2", tag="streaming_silk", rots=(("x", r), ("z", -x)), pivot=(x, 22, -4.6))
    a(c, C(3.6, 4.8, 3.6, 0.4, 7.4, 0.4), "acc", tag="lamp_chain")
    a(c, C(3.6, 1.6, 3.6, 3.0, 3.4, 3.0), "blade", tag="glass_lamp")
    k.fire(c, C(3.6, 2.2, 3.6, 3.2, 2.0, 1.4))
    a(c, C(3.6, 4.8, 3.6, 2.2, 0.7, 2.2), "acc", tag="lamp_cap")
    k.arms("cloth", "cloth", cuff="acc", w=5.8, low_h=5.2)
    for s in SIDES:
        a(k.arm(s), C(s * 6.0 + s * 3.4, 5.0, 0, 0.5, 11.0, 4.0), "cloth2", tag="sleeve_veil", rots=(("z", s * 8),), pivot=(s * 9, 16, 0))
        a(k.shoulder(s), C(s * 6.3, 21.0, 0, 5.8, 2.4, 5.8), "cloth2", tag="mantle")
    k.legs("cloth", w=4.6)
    k.boots("acc", h=1.8, w=4.8, toe="cloth2", toe_d=2.8)


@design(cloth=TURQUOISE, cloth2=ROYAL, wrap=PALE, acc=GILT, gold=GILT, dark=BLACK, leather=HIDE, blade=STEEL, gem=SUNFIRE, fire=SUNFIRE, hot=SUNFIRE, no_skirt=True)
def dancer(k):
    """a blade dancer of the Sultan's hall: rows of gold coins that shiver on the hips, sheer veils from the wrists, twin curved knives at the small of the back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.4, -0.2, 9.0, 7.4, 9.2), "cloth2", tag="head_scarf")
    a(h, C(0, 24.0, 4.45, 7.4, 3.6, 0.4), "cloth", tag="face_veil")
    for x in (-3.0, -1.5, 0, 1.5, 3.0):
        a(h, C(x, 23.2, 4.75, 1.1, 1.1, 0.3), "acc", tag="coin")
    a(h, C(0, 31.0, 0, 10.0, 1.2, 10.0), "acc", tag="circlet")
    a(h, C(0, 31.2, 5.1, 1.8, 2.8, 0.5), "gem", tag="brow_gem")
    for x in (-3.6, -1.8, 1.8, 3.6):
        k.tail(h, x, 31.2, 5.1, 1.4, 0.4, "acc", tag="brow_chain")
        a(h, C(x, 29.2, 5.1, 0.9, 0.9, 0.3), "acc", tag="coin")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 28.2, 4.75, 1.2, 0.7, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.6), "wrap", tag="bare_midriff")
    a(c, C(0, 19.0, 0, 8.7, 4.6, 5.6), "cloth2", tag="silk_top")
    a(c, C(0, 18.8, 2.85, 8.6, 0.9, 0.4), "acc", tag="top_coin_row")
    for x in (-3.4, -1.7, 0, 1.7, 3.4):
        a(c, C(x, 17.4, 2.95, 1.1, 1.4, 0.3), "acc", tag="coin")
    a(c, C(0, 12.2, 0, 8.7, 1.8, 5.2), "cloth", tag="hip_sash")
    for x, r in ((-3.6, 0), (-1.8, 0), (0, 0), (1.8, 0), (3.6, 0)):
        for y in (11.4, 12.6):
            a(c, C(x + (0.9 if y > 12 else 0), y, 2.85, 1.3, 1.3, 0.3), "acc", tag="coin")
    for s in SIDES:
        a(b, C(s * 2.0, 8.0, -3.6, 1.0, 7.4, 0.5), "blade", tag="curved_knife", rots=(("z", -s * 38),), pivot=(s * 2, 12, -3.6))
        a(b, C(s * 4.6, 6.0, -3.6, 0.9, 3.4, 0.5), "blade", tag="curved_knife_tip", rots=(("z", s * 8),), pivot=(s * 4.6, 7.6, -3.6))
        a(b, C(s * 1.4, 12.0, -3.6, 1.3, 2.4, 1.1), "acc", tag="knife_hilt")
    a(b, C(0, 12.0, -2.8, 7.4, 2.4, 0.6), "cloth", tag="back_sash")
    a(b, C(0, 16.0, -2.8, 7.4, 8.0, 0.6), "cloth2", tag="back_top")
    k.cape("cloth", width=2.4, top=12.0, length=11.0, lean=14, z=-3.0, tag="sash_end")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "wrap", tag="bare_arm")
        k.elbow(s, "wrap")
        a(p, C(x, 11.4, 0, 5.0, 5.4, 5.0), "wrap", tag="bare_arm")
        for y in (11.8, 12.8, 13.8):
            a(p, C(x, y, 0, 5.4, 0.6, 5.4), "acc", tag="bangle")
        a(p, C(x, 19.4, 0, 5.3, 0.9, 5.3), "acc", tag="armlet")
        a(p, C(x + s * 2.9, 5.0, 0, 0.4, 7.8, 4.4), "cloth", tag="wrist_veil", rots=(("z", s * 10),), pivot=(x + s * 2.9, 13, 0))
        a(k.shoulder(s), C(x, 22.6, 0, 5.0, 1.0, 5.0), "cloth2", tag="silk_strap")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.0, 0, 5.6, 10.0, 5.6), "cloth2", tag="harem_leg")
        a(p, C(y, 2.4, 0, 4.8, 1.2, 4.8), "acc", tag="ankle_band")
    k.boots("wrap", h=1.8, w=4.6, sole="dark", toe="acc", toe_d=3.2)


@design(blade=MIRROR, gem=MIRROR, acc=GILT, gold=GILT, dark=ramp("#20344a", "#2e4a66", "#40648a"), mail=TURQUOISE, cloth=TURQUOISE, wrap=PALE, leather=HIDE, fire=SUNFIRE, hot=SUNFIRE)
def mirrorguard(k):
    """the Minaret's guards throw the sun at you: helm and breastplate polished to a mirror, a burning glass on the back that gathers the light, great round mirrors on each shoulder"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.6, 0, 9.8, 7.8, 9.8), "blade", tag="mirror_helm")
    a(h, C(0, 22.8, 0, 11.0, 1.6, 11.0), "acc", tag="neck_guard")
    for w, y in ((9.0, 31.4), (7.0, 33.0), (4.6, 34.6), (2.4, 36.2)):
        a(h, C(0, y, 0, w, 1.8, w), "blade", tag="onion_top")
    k.spike(h, 0, 38.0, 0, 4.0, 1.2, "acc", tag="helm_spike")
    a(h, C(0, 26.4, 4.95, 8.0, 0.9, 0.4), "void", tag="slit")
    k.fire(h, C(0, 26.6, 5.15, 6.4, 0.5, 0.3))
    a(h, C(0, 28.2, 4.95, 7.4, 1.0, 0.5), "acc", tag="brow_band")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.0), "blade", tag="mirror_breast")
    a(c, C(0, 14.0, 3.1, 6.6, 7.6, 0.4), "acc", tag="mirror_rim")
    a(c, C(0, 14.6, 3.3, 5.6, 6.4, 0.4), "gem", tag="chest_mirror")
    k.fire(c, C(-1.2, 18.2, 3.55, 1.4, 1.4, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 6.6), "cloth", tag="sash")
    a(b, C(0, 13.0, -3.6, 7.4, 10.0, 1.2), "blade", tag="back_plate")
    a(b, C(0, 13.0, -4.8, 1.4, 19.0, 1.0), "acc", tag="glass_post")
    for w, ht in ((13.0, 6.0), (10.0, 10.0), (6.0, 13.0)):
        a(b, C(0, 30.0 - ht / 2, -5.4, w, ht, 0.8), "gem", tag="burning_glass")
    a(b, C(0, 28.2, -6.0, 3.0, 3.6, 0.3), "glow", group="fire", tag="gathered_sun")
    k.arms("mail", "blade", joint="mail", cuff="acc", w=5.6)
    for s in SIDES:
        q, x = k.shoulder(s), s * 6.0
        a(q, C(x + s * 1.0, 20.5, 0, 6.2, 2.8, 6.4), "blade", tag="pauldron")
        cx = x + s * 4.4
        for w, ht in ((9.0, 4.4), (7.4, 7.4), (4.4, 9.0)):
            a(q, C(cx, 26.0 - ht / 2, 0, 1.0, ht, w), "gem", tag="shoulder_mirror")
        a(q, C(cx, 21.0, 0, 1.2, 0.9, 4.8), "acc", tag="mirror_rim")
        a(q, C(cx, 30.1, 0, 1.2, 0.9, 4.8), "acc", tag="mirror_rim")
        a(q, C(cx + s * 0.55, 24.8, 0, 0.3, 2.4, 2.4), "glow", tag="mirror_flash")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 4.9, 9.6, 4.9), "mail", tag="mail")
        a(p, C(y, 6.2, 2.5, 3.8, 5.8, 0.6), "blade", tag="tasset")
        a(p, C(y, 2.4, 2.4, 3.2, 3.0, 0.6), "blade", tag="greave")
    k.boots("blade", h=3.8, w=5.0, cuff="acc", toe="acc", toe_d=3.0)


@design(blade=GILT, acc=ROYAL, gold=GILT, cloth=ROYAL, wrap=PALE, gem=SUNFIRE, stone=TURQUOISE, dark=BLACK, mail=GILT, leather=HIDE, fire=SUNFIRE, hot=SUNFIRE)
def sultan(k):
    """the Djinn Sultan's own panoply: a jewelled onion-domed turban with a crescent on top, wide gold shoulders curled up at the ends, a great scimitar at the back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.2, 0, 9.8, 7.6, 9.8), "blade", tag="gold_mask_helm")
    a(h, C(0, 26.0, 4.95, 8.0, 0.8, 0.4), "void", tag="slit")
    k.fire(h, C(0, 26.2, 5.15, 6.4, 0.5, 0.3))
    a(h, C(0, 22.2, 4.8, 3.2, 3.6, 0.9), "blade", tag="false_beard")
    for w, y, m in ((11.8, 30.6, "wrap"), (13.4, 32.0, "cloth"), (14.0, 33.8, "wrap"), (13.0, 35.6, "cloth"), (10.6, 37.2, "wrap"), (7.4, 38.8, "cloth"), (4.2, 40.2, "blade"), (2.0, 41.6, "blade")):
        a(h, C(0, y, 0, w, 1.9, w), m, tag="onion_turban")
    a(h, C(0, 33.4, 7.0, 3.6, 4.0, 0.7), "blade", tag="turban_brooch")
    a(h, C(0, 34.2, 7.3, 2.2, 2.4, 0.5), "stone", tag="turban_jewel")
    k.fire(h, C(0, 34.8, 7.55, 1.2, 1.2, 0.3))
    k.spike(h, 0, 37.0, 7.0, 5.4, 1.6, "wrap", rx=-4, tag="turban_plume", steps=3)
    for t in range(9):
        r = math.radians(-100 + t * 25)
        a(h, C(math.sin(r) * 2.8, 44.6 + math.cos(r) * -2.8 + 1.4, 0, 1.3, 1.3, 0.8), "blade", tag="crescent")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.6), "blade", tag="cuirass")
    a(c, C(0, 13.2, 3.35, 6.8, 9.0, 0.5), "cloth", tag="silk_panel")
    a(c, C(0, 15.0, 3.65, 4.4, 5.0, 0.4), "blade", tag="sun_plaque")
    a(c, C(0, 15.8, 3.9, 2.6, 3.0, 0.4), "stone", tag="great_jewel")
    k.fire(c, C(0, 16.4, 4.15, 1.2, 1.4, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.6, 7.2), "blade", tag="belt")
    a(c, C(0, 22.4, 0, 8.7, 1.6, 7.2), "stone", tag="collar")
    a(b, C(0, 13.0, -3.8, 7.6, 10.4, 1.6), "blade", tag="back_plate")
    k.cape("cloth", width=8.0, top=23.0, length=19.0, lean=8, z=-4.8, tag="royal_cape", hem="blade")
    rz = (("z", 40),)
    a(b, C(0, 8.0, -6.2, 1.2, 8.0, 1.0), "stone", tag="scimitar_grip", rots=rz, pivot=(0, 18, -6.2))
    a(b, C(0, 15.6, -6.2, 5.0, 1.0, 1.2), "blade", tag="scimitar_guard", rots=rz, pivot=(0, 18, -6.2))
    for i, (ln, r2, w) in enumerate(((8.0, 0, 2.6), (7.0, 8, 3.0), (6.0, 18, 3.2), (5.0, 30, 2.8), (3.6, 46, 1.6))):
        y0, x0 = 16.6 + sum((8.0, 7.0, 6.0, 5.0)[:i]) * 0.96, -sum((0.0, 1.0, 2.8, 5.2)[:i + 1]) * 0.5
        a(b, C(x0, y0, -6.2, w, ln + 0.2, 0.6), "wrap", tag="scimitar_blade", rots=rz, pivot=(0, 18, -6.2))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "cloth", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.4, 1.0, 6.4), "stone", tag="cuff")
        q = k.shoulder(s)
        a(q, C(x + s * 1.4, 20.5, 0, 9.0, 2.8, 9.6), "blade", tag="wide_shoulder")
        a(q, C(x + s * 1.4, 23.2, 0, 7.0, 1.0, 7.6), "cloth", tag="shoulder_top")
        k.horn(q, x + s * 5.6, 20.8, 0, [(3.0, -s * 86, 3.0), (3.0, -s * 40, 2.4), (2.6, s * 4, 1.8), (2.0, s * 48, 1.2)], "blade")
        a(q, C(x + s * 1.4, 22.0, 4.85, 2.2, 2.2, 0.5), "stone", tag="shoulder_jewel")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.0, 0, 5.6, 10.0, 5.6), "cloth", tag="silk_leg")
        a(p, C(y, 2.2, 0, 5.0, 1.4, 5.0), "blade", tag="ankle_band")
        a(p, C(y, 6.2, 2.9, 3.8, 5.6, 0.6), "blade", tag="tasset")
    k.boots("blade", h=2.6, w=5.0, toe="blade", toe_d=3.0)
    for s in SIDES:
        a(k.boot(s), C(s * 1.95, 1.8, 5.2, 1.8, 1.8, 1.6), "blade", tag="toe_curl")


# ---------------------------------------------------------------- the Warlord's Fang

@design(fur=NORSEFUR, cloth=RUST, bone=BONE, wrap=FURY, dark=BLACK, leather=HIDE, wood=OAK, acc=ramp("#3a1a08", "#6e3a10", "#a8641a", "#d89628"), blade=IRON, hide2=GREEN_HIDE, fire=FURY, hot=FURY)
def shaman(k):
    """the warband's voice: a ram's skull with the horns curling, green skin painted red, a rack of little skulls and rattling teeth"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.4, -0.4, 9.2, 7.0, 9.2), "hide2", tag="head")
    a(h, C(0, 24.0, 4.2, 5.6, 2.0, 0.7), "wrap", tag="war_paint")
    a(h, C(0, 26.0, 2.6, 8.2, 6.8, 4.0), "bone", tag="ram_skull")
    a(h, C(0, 24.2, 4.4, 4.6, 3.6, 2.2), "bone", tag="ram_snout")
    for s in SIDES:
        a(h, C(s * 2.4, 29.0, 4.55, 2.0, 1.8, 0.3), "void", tag="socket")
        k.fire(h, C(s * 2.4, 29.4, 4.7, 1.2, 1.0, 0.3))
        k.horn(h, s * 4.2, 30.8, 0.6, [(3.6, -s * 84, 3.2), (3.4, -s * 130, 2.8), (3.0, -s * 186, 2.2), (2.6, -s * 240, 1.6), (1.8, -s * 296, 1.0)], "bone")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.8), "hide2", tag="green_chest")
    for x, r in ((-2.4, 14), (2.4, -14)):
        a(c, C(x, 13.0, 2.55, 1.6, 9.0, 0.4), "wrap", tag="red_paint", rots=(("z", r),), pivot=(x, 18, 2.55))
    a(c, C(0, 20.4, 0, 8.7, 3.6, 6.0), "fur", tag="fur_collar")
    for i in range(7):
        r = math.radians(-60 + i * 20)
        a(c, C(math.sin(r) * 4.2, 20.0 - math.cos(r) * 3.0, 3.1, 0.8, 1.6, 0.6), "bone", tag="tooth_necklace")
    a(c, C(0, 12.2, 0, 8.7, 1.4, 5.6), "leather", tag="belt")
    a(b, C(0, 5.0, -3.2, 8.0, 18.0, 0.9), "cloth", tag="ragged_robe", rots=(("x", 6),), pivot=(0, 23, -3.2))
    a(b, C(0, 18.0, -4.2, 1.2, 22.0, 1.2), "wood", tag="totem_pole")
    a(b, C(0, 28.0, -4.2, 11.0, 1.0, 1.0), "wood", tag="totem_beam")
    for x, y in ((-5.0, 25.0), (0, 40.0), (5.0, 25.0)):
        a(b, C(x, y, -4.2, 2.6, 2.8, 2.6), "bone", tag="small_skull")
        k.fire(b, C(x, y + 1.2, -5.55, 1.6, 0.7, 0.3))
    for x in (-3.0, 3.0):
        k.tail(b, x, 28.0, -4.2, 6.0, 0.8, "wrap", tag="red_tail")
    k.arms("hide2", "hide2", cuff="fur", w=5.2)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.4, 20.8, 0, 6.2, 2.8, 6.2), "fur", tag="fur_shoulder")
        for y in (12.2, 13.8):
            a(k.arm(s), C(s * 6.0, y, 0, 5.5, 0.6, 5.5), "wrap", tag="red_paint")
        a(k.arm(s), C(s * 6.0, 17.4 + 2.2, 2.8, 2.6, 1.6, 0.3), "bone", tag="arm_bone")
    k.legs("cloth", w=4.6)
    k.boots("fur", h=3.0, w=4.8, sole="dark")


@design(leather=ramp("#1c120c", "#2e1e14", "#46301e", "#60442a"), hide2=GREEN_HIDE, blade=IRON, dark=BLACK, wrap=FURY, acc=IRON, cloth=RUST, bone=BONE, wood=OAK, fire=FURY, hot=FURY)
def cutthroat(k):
    """nobody likes him, even here: a strap across one eye, a harness of rusty knives pointing every way, a bloody rag and a chain with a hook on it"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.0, 8.0, 9.2), "hide2", tag="head")
    a(h, C(0, 23.8, 3.8, 7.0, 2.0, 1.4), "hide2", tag="underbite")
    for s in SIDES:
        k.spike(h, s * 2.4, 25.4, 4.2, 2.4, 1.2, "bone", tag="tusk", steps=2)
    a(h, C(0, 31.2, -0.2, 3.0, 2.6, 9.0), "wrap", tag="mohawk")
    for z in (-3.0, 0, 3.0):
        k.spike(h, 0, 33.6, z, 2.6, 2.0, "wrap", tag="mohawk_spike", steps=2)
    a(h, C(-1.6, 27.0, 4.65, 8.4, 1.0, 0.3), "dark", tag="eye_strap", rots=(("z", -24),), pivot=(0, 28, 4.65))
    a(h, C(-2.2, 27.4, 4.75, 2.4, 2.2, 0.4), "leather", tag="eye_patch")
    k.fire(h, C(2.2, 28.0, 4.75, 1.4, 0.8, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.8), "hide2", tag="green_chest")
    for r in (34, -34):
        a(c, C(0, 11.6, 2.55, 1.6, 13.0, 0.5), "leather", tag="harness", rots=(("z", r),), pivot=(0, 18, 2.55))
    a(c, C(0, 16.6, 2.85, 2.8, 2.8, 0.5), "acc", tag="harness_ring")
    for x, y, r in ((-3.4, 20.0, 50), (3.4, 20.0, -50), (-3.0, 14.6, 130), (3.0, 14.6, -130), (-1.4, 21.6, 20), (1.4, 21.6, -20)):
        a(c, C(x, y, 3.0, 0.8, 3.6, 0.3), "blade", tag="rusty_knife", rots=(("z", r),), pivot=(x, y, 3.0))
    a(c, C(0, 12.2, 0, 8.7, 1.4, 5.6), "leather", tag="belt")
    a(c, C(2.4, 6.4, 3.0, 2.6, 5.8, 0.5), "wrap", tag="bloody_rag")
    a(b, C(0, 13.0, -2.9, 6.6, 10.0, 0.7), "hide2", tag="back")
    for r in (34, -34):
        a(b, C(0, 11.6, -3.4, 1.6, 13.0, 0.5), "leather", tag="harness", rots=(("z", r),), pivot=(0, 18, -3.4))
    for y, x in ((22.0, -3.0), (20.0, -1.6), (18.0, 0.0), (16.0, 1.4), (14.0, 2.8), (12.0, 3.6), (10.0, 3.0), (8.0, 2.0), (6.0, 1.4)):
        a(b, C(x, y, -3.7, 1.2, 2.3, 0.5), "acc", tag="hook_chain")
    a(b, C(1.4, 3.6, -3.7, 1.2, 2.4, 0.7), "blade", tag="big_hook")
    a(b, C(0.0, 3.0, -3.7, 3.2, 1.0, 0.7), "blade", tag="big_hook")
    a(b, C(-1.4, 3.6, -3.7, 1.0, 2.6, 0.7), "blade", tag="big_hook")
    k.arms("hide2", "leather", cuff="acc", w=5.0)
    for s in SIDES:
        k.spike(k.shoulder(s), s * 6.6, 22.4, 0, 5.0, 2.2, "acc", rz=-s * 26, tag="pauldron_spike")
        a(k.shoulder(s), C(s * 6.3, 21.0, 0, 5.4, 2.2, 5.4), "leather", tag="cop")
        k.spike(k.arm(s), s * 8.8, 13.6, 0, 3.0, 1.2, "acc", rz=-s * 86, tag="stud")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 8.2, 0, 5.0, 0.9, 5.0), "acc", tag="thigh_strap")
    a(k.leg(1), C(4.4, 6.4, 0, 0.8, 5.0, 1.0), "blade", tag="rusty_knife")
    k.legs("leather", w=4.6)
    k.boots("leather", h=4.0, w=4.8, cuff="acc", toe="acc", toe_d=2.2)


@design(blade=RUST, mail=IRON, leather=HIDE, dark=BLACK, cloth=ramp("#5a0e08", "#7c160c", "#a42212", "#cc3a1e"), wood=OAK, bone=BONE, wrap=HEMP, acc=IRON, fur=NORSEFUR, hide2=GREEN_HIDE, fire=FURY, hot=FURY)
def raider(k):
    """the warband in full cry: two tall red war banners on his back, a string of skulls for the count, a horned iron cap and a big square jaw of a guard"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 28.0, 0, 9.8, 4.8, 9.8), "blade", tag="iron_cap")
    a(h, C(0, 22.8, 0.8, 10.0, 5.2, 9.0), "acc", tag="jaw_guard")
    a(h, C(0, 26.4, 4.9, 8.0, 1.6, 0.4), "void", tag="gap")
    k.fire(h, C(0, 26.8, 5.1, 6.4, 0.6, 0.3))
    a(h, C(0, 28.0, 5.0, 10.0, 1.1, 0.5), "dark", tag="brow")
    a(h, C(0, 32.8, 0, 7.0, 1.0, 7.0), "dark", tag="cap_top")
    for s in SIDES:
        k.horn(h, s * 5.0, 29.4, 0, [(3.4, -s * 74, 2.8), (3.2, -s * 30, 2.2), (2.6, s * 6, 1.4)], "bone")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.8), "mail", tag="hauberk")
    a(c, C(0, 14.4, 3.05, 7.6, 8.6, 0.6), "blade", tag="breastplate")
    k.rivets(c, [(-3.0, 21.8), (0, 21.8), (3.0, 21.8), (-3.0, 15.0), (3.0, 15.0)], 3.4, mat="dark")
    a(c, C(0, 12.2, 0, 8.7, 1.6, 6.4), "leather", tag="belt")
    for x, ln in ((-3.2, 2.0), (0, 3.4), (3.2, 1.6)):
        a(c, C(x, 12.2 - ln, 3.3, 0.5, ln, 0.5), "wrap", tag="skull_cord")
        a(c, C(x, 12.2 - ln - 2.2, 3.3, 2.0, 2.2, 2.0), "bone", tag="trophy_skull")
        a(c, C(x, 12.2 - ln - 1.2, 4.35, 1.2, 0.6, 0.3), "void", tag="trophy_eyes")
    a(b, C(0, 13.0, -3.6, 7.4, 10.0, 1.2), "blade", tag="back_plate")
    for s in SIDES:
        x = s * 3.0
        a(b, C(x, 10.0, -4.6, 1.2, 36.0, 1.2), "wood", tag="banner_pole")
        a(b, C(x + s * 3.2, 45.0, -4.6, 7.4, 1.0, 1.0), "wood", tag="banner_arm")
        a(b, C(x + s * 3.8, 31.0, -4.6, 6.4, 14.0, 0.4), "cloth", tag="war_banner")
        k.spike(b, x, 46.0, -4.6, 3.6, 1.6, "acc", tag="pole_tip")
        a(b, C(x + s * 3.8, 36.4, -4.9, 3.6, 3.6, 0.3), "bone", tag="banner_mark")
        a(b, C(x + s * 3.8, 37.2, -5.1, 2.4, 0.9, 0.3), "void", tag="banner_mark_eyes")
    k.arms("mail", "blade", cuff="dark", w=5.4)
    for s in SIDES:
        q = k.shoulder(s)
        a(q, C(s * 6.8, 20.6, 0, 7.0, 3.2, 7.2), "blade", tag="pauldron")
        a(q, C(s * 6.8, 20.3, 0, 7.4, 0.8, 7.6), "dark", tag="pauldron_rim")
        k.spike(q, s * 8.0, 23.6, 0, 4.6, 2.2, "acc", rz=-s * 16, tag="pauldron_spike")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 6.2, 2.5, 3.8, 5.8, 0.6), "cloth", tag="tasset")
    k.legs("mail", w=4.8)
    k.boots("blade", h=4.0, w=5.0, cuff="fur", toe="dark", toe_d=2.4)


@design(blade=ramp("#100e10", "#1e1a1e", "#322c30", "#4a4246", "#665c60", "#8a8084"), dark=BLACK, acc=RUST, bone=BONE, mail=IRON, cloth=ramp("#5a0e08", "#7c160c", "#a42212", "#cc3a1e"), fur=NORSEFUR, wood=OAK, leather=HIDE, wrap=HEMP, fire=FURY, hot=FURY)
def warplate(k):
    """Gorrak's chosen: a slab of black iron with a tusked jaw for a visor, a rack of spikes across the shoulders, hooks and the heads of those who said no"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.0, 0, 11.0, 9.8, 11.0), "blade", tag="great_helm")
    a(h, C(0, 32.8, 0, 8.4, 1.0, 8.4), "dark", tag="helm_top")
    a(h, C(0, 28.0, 5.5, 11.2, 1.6, 0.7), "dark", tag="brow")
    a(h, C(0, 26.6, 5.55, 9.0, 1.3, 0.4), "void", tag="slit")
    k.fire(h, C(0, 26.9, 5.75, 7.4, 0.6, 0.3))
    a(h, C(0, 21.8, 5.8, 10.4, 4.6, 1.8), "blade", tag="iron_jaw")
    for x in (-3.4, -1.2, 1.2, 3.4):
        k.spike(h, x, 25.8, 6.3, -2.0, 1.2, "acc", tag="jaw_tooth", steps=2)
    for s in SIDES:
        k.spike(h, s * 4.2, 23.0, 6.4, 8.4, 3.0, "bone", rz=-s * 10, rx=-12, tag="great_tusk", steps=4)
        k.spike(h, s * 5.6, 30.6, 0, 6.4, 3.0, "acc", rz=-s * 52, tag="helm_spike", steps=4)
    a(c, C(0, 12.2, 0, 8.7, 11.8, 7.0), "blade", tag="cuirass")
    a(c, C(0, 14.0, 3.55, 6.8, 7.4, 0.5), "dark", tag="fang_field")
    a(c, C(0, 15.0, 3.8, 3.4, 5.6, 0.4), "cloth", tag="fang_sigil")
    a(c, C(0, 13.4, 3.8, 1.8, 1.8, 0.4), "cloth", tag="fang_sigil")
    k.fire(c, C(0, 16.4, 4.05, 1.4, 3.4, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.8, 7.6), "dark", tag="belt")
    a(c, C(0, 11.4, 3.9, 3.4, 3.0, 0.7), "acc", tag="skull_buckle")
    a(b, C(0, 13.0, -4.2, 7.8, 10.6, 2.0), "blade", tag="back_plate")
    a(b, C(0, 24.0, -4.2, 22.0, 1.6, 1.6), "acc", tag="trophy_rack")
    for x, ln in ((-10.6, 7.0), (-7.6, 9.0), (-4.6, 8.0), (-1.6, 10.0), (1.6, 10.0), (4.6, 8.0), (7.6, 9.0), (10.6, 7.0)):
        k.spike(b, x, 25.4, -4.2, ln, 2.0, "acc", tag="rack_spike", steps=3)
    for x in (-7.6, 7.6):
        a(b, C(x, 27.4, -4.2, 3.0, 3.2, 3.0), "bone", tag="spiked_head")
        a(b, C(x, 28.6, -5.75, 2.0, 0.8, 0.3), "void", tag="head_eyes")
    a(b, C(0, 4.0, -5.4, 7.0, 19.0, 0.6), "cloth", tag="red_cape", rots=(("x", 7),), pivot=(0, 23, -5.4))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 10.8, 0, 6.6, 6.0, 6.6), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 7.0, 1.0, 7.0), "dark", tag="cuff")
        for t in (-2.2, 0, 2.2):
            k.spike(p, x + s * 3.3, 13.0, t, 3.4, 1.4, "acc", rz=-s * 88, tag="stud")
        q = k.shoulder(s)
        a(q, C(x + s * 1.6, 20.5, 0, 9.4, 4.0, 10.0), "blade", tag="pauldron")
        a(q, C(x + s * 1.6, 24.4, 0, 7.6, 1.0, 8.2), "dark", tag="pauldron_top")
        for dz, dx, ln in ((-3.4, 0.4, 5.0), (0, 2.0, 6.6), (3.4, 0.4, 5.0)):
            k.spike(q, x + s * (1.6 + dx), 25.2, dz, ln, 2.6, "acc", rz=-s * 14, tag="pauldron_spike", steps=3)
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.3, 9.6, 5.3), "blade", tag="cuisse")
        a(p, C(y, 4.6, 2.8, 4.2, 3.0, 1.0), "dark", tag="poleyn")
        k.spike(p, y, 5.6, 3.2, 3.4, 1.8, "acc", rx=-62, tag="knee_spike")
    k.boots("blade", h=4.4, w=5.6, cuff="dark", toe="acc", toe_d=3.0)
