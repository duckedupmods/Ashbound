"""The Crypt, the Plague Ward, the Faceless Temple and the Ossuary Engine (see armorsets.py for the units and the fit rules)."""
from armorsets import BRASS, C, IRON, SIDES, design, ramp
from armorsets_a import BLACK, HEMP, OAK

WAXEN = ramp("#7a6a4c", "#a08e68", "#c4b48a", "#e0d4ac", "#f2eace", "#fdf8ea")
CANDLE = ramp("#a84808", "#dc7c10", "#f8ac28", "#ffd45c", "#fff09c", "#fffce0")
HIDE = ramp("#1c120e", "#2e1e16", "#463022", "#604430", "#7e5c42")
PALE = ramp("#6a6258", "#8c8478", "#b0a89c", "#d0cabe", "#ece8de", "#fcfaf4")
FEVER = ramp("#2a5206", "#4a8008", "#74b010", "#a6dc24", "#d6f464", "#f6ffc4")
LEAD = ramp("#101416", "#1e2428", "#30383c", "#465054", "#606c70", "#8a9698")
CRYSTAL = ramp("#2a1a6a", "#3e2ca0", "#5a46d0", "#8470ec", "#b4a4f8", "#ece6ff")
GILT = ramp("#3e2206", "#6e420c", "#a8701a", "#d8a430", "#f6d468", "#fff4c0")
BONE = ramp("#5c4e38", "#847458", "#ac9c7c", "#d0c4a4", "#ecE4cc", "#fbf7ea")
TOLL = ramp("#5a2c08", "#8e4c0e", "#c47c18", "#e8ac34", "#fbd870", "#fff2bc")


# ---------------------------------------------------------------- the Crypt

@design(cloth=BLACK, wax=WAXEN, wrap=WAXEN, dark=BLACK, acc=BRASS, leather=HIDE, blade=ramp("#2e2a26", "#4c4640", "#6e665c", "#948a7c"), fire=CANDLE, hot=CANDLE)
def abbot(k):
    """the Pale Abbot's own habit: a mitre of poured wax with candles burning on it, more of them on a rack behind the head, wax run down the robe"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.6, -0.4, 9.4, 7.8, 9.4), "cloth", tag="cowl")
    a(h, C(0, 27.2, 4.45, 7.4, 3.2, 0.5), "void", tag="cowl_dark")
    for s in SIDES:
        k.fire(h, C(s * 1.8, 28.4, 4.75, 1.0, 0.7, 0.3))
    a(h, C(0, 31.2, 0, 9.0, 1.2, 9.0), "acc", tag="mitre_band")
    for w, y, ht in ((8.6, 32.4, 2.8), (7.0, 35.2, 2.6), (5.0, 37.8, 2.4), (2.6, 40.2, 2.0)):
        a(h, C(0, y, 0, w, ht, w), "wax", tag="mitre")
    a(h, C(0, 33.0, 4.4, 1.2, 7.0, 0.5), "acc", tag="mitre_cross")
    for x, z, ln, y in ((-4.0, 3.0, 2.6, 32.4), (4.0, 3.0, 3.4, 32.4), (-3.4, -3.4, 3.0, 35.0), (3.4, -3.4, 2.2, 35.0)):
        a(h, C(x, y, z, 1.4, ln, 1.4), "wax", tag="candle")
        k.tongue(h, x, y + ln, z, 1.8, 0.9)
    k.tongue(h, 0, 42.2, 0, 2.6, 1.4)
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="habit")
    a(c, C(0, 12.2, 2.75, 3.4, 11.8, 0.5), "wax", tag="stole")
    a(c, C(0, 20.8, 0, 8.7, 3.2, 6.2), "wax", tag="wax_yoke")
    for x, ln in ((-3.4, 4.6), (-2.2, 2.8), (2.4, 5.4), (3.4, 3.0)):
        a(c, C(x, 20.9 - ln, 3.05, 1.0, ln, 0.4), "wax", tag="wax_run")
    a(c, C(0, 15.4, 3.1, 2.4, 3.0, 0.5), "acc", tag="reliquary")
    k.fire(c, C(0, 16.0, 3.4, 1.4, 1.8, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.8), "wax", tag="cord")
    for t in range(9):
        rz = -80 + t * 20
        px, py = 0.0, 29.0
        a(b, C(px, py + 6.6, -6.2, 0.9, 4.4, 0.9), "acc", tag="rack_arm", rots=(("z", rz),), pivot=(px, py, -6.2))
        a(b, C(px, py + 11.0, -6.2, 1.5, 3.0 + (t % 2) * 1.4, 1.5), "wax", tag="rack_candle", rots=(("z", rz),), pivot=(px, py, -6.2))
        a(b, C(px, py + 14.2 + (t % 2) * 1.4, -6.2, 0.9, 1.8, 0.9), "glow", group="fire", tag="rack_flame", rots=(("z", rz),), pivot=(px, py, -6.2))
    a(b, C(0, 15.0, -3.8, 2.0, 12.0, 1.6), "dark", tag="rack_post")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "cloth", tag="sleeve")
        k.elbow(s, "cloth")
        a(p, C(x, 11.0, 0, 6.2, 5.6, 6.2), "cloth", tag="flare")
        a(p, C(x, 11.0, 0, 6.5, 0.8, 6.5), "wax", tag="wax_hem")
        q = k.shoulder(s)
        a(q, C(x + s * 0.3, 21.0, 0, 5.8, 2.8, 5.8), "wax", tag="wax_shoulder")
        a(q, C(x + s * 1.6, 23.7, 1.0, 1.2, 1.6, 1.2), "wax", tag="candle")
        k.tongue(q, x + s * 1.6, 25.3, 1.0, 1.6, 0.8)
    k.legs("cloth", w=4.6)
    k.boots("dark", h=2.8, w=4.8)


@design(cloth=ramp("#0a080c", "#141018", "#201a26", "#2e2636", "#403648"), cloth2=ramp("#0e0c12", "#1a161e", "#28222e", "#3a3242"), leather=HIDE, dark=BLACK, wax=WAXEN, acc=ramp("#3a3a44", "#5a5a66", "#84848e", "#b4b4bc", "#e0e0e6"), blade=IRON, fire=CANDLE, hot=CANDLE)
def mourner(k):
    """she follows every coffin in: a veil to the waist under a small black hat, a long funeral coat with tails, her lantern kept lit for the one she lost, wax tears down the cheeks"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.0, 7.6, 9.2), "cloth", tag="hood")
    a(h, C(0, 31.2, -0.2, 11.6, 0.7, 11.6), "cloth2", tag="hat_brim")
    a(h, C(0, 31.8, -0.2, 7.0, 2.8, 7.0), "cloth2", tag="hat")
    a(h, C(0, 31.8, -0.2, 7.3, 0.9, 7.3), "acc", tag="hat_band")
    a(h, C(3.4, 34.6, 2.4, 0.8, 3.6, 0.8), "acc", tag="hat_pin")
    a(h, C(0, 19.4, 5.2, 8.6, 12.0, 0.4), "cloth2", tag="veil")
    a(h, C(0, 18.6, 5.2, 7.0, 0.9, 0.5), "acc", tag="veil_hem")
    for s in SIDES:
        a(h, C(s * 5.0, 21.0, 0.8, 0.5, 10.4, 7.8), "cloth2", tag="veil_side")
        k.fire(h, C(s * 2.0, 27.8, 5.45, 1.2, 0.6, 0.3))
        k.fire(h, C(s * 2.4, 24.6, 5.45, 0.5, 3.2, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.0), "cloth", tag="coat")
    a(c, C(0, 21.6, 0, 8.7, 2.4, 6.0), "cloth2", tag="high_collar")
    for y in (14.0, 16.0, 18.0, 20.0):
        a(c, C(0, y, 2.65, 0.8, 0.8, 0.5), "acc", tag="jet_button")
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.6), "acc", tag="belt")
    a(c, C(-3.4, 5.8, 3.5, 2.8, 3.4, 2.8), "dark", tag="lantern")
    k.fire(c, C(-3.4, 6.3, 3.5, 3.0, 2.4, 1.8))
    a(c, C(-3.4, 9.2, 3.5, 3.2, 0.7, 3.2), "acc", tag="lantern_top")
    a(c, C(-3.4, 9.8, 3.5, 0.5, 2.6, 0.5), "acc", tag="lantern_chain")
    a(c, C(-3.4, 12.0, 3.1, 0.9, 0.9, 1.3), "acc", tag="lantern_hook")
    for s in SIDES:
        a(b, C(s * 2.2, 4.2, -3.4, 3.2, 18.0, 0.8), "cloth", tag="coat_tail", rots=(("x", 9), ("z", -s * 4)), pivot=(s * 2.2, 22.2, -3.4))
    a(b, C(0, 19.6, -3.5, 4.8, 3.6, 0.9), "cloth2", tag="bow")
    a(b, C(0, 20.8, -4.1, 1.6, 1.4, 0.7), "acc", tag="bow_knot")
    k.arms("cloth", "cloth2", cuff="acc", w=5.0)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.2, 21.0, 0, 5.4, 2.2, 5.4), "cloth2", tag="cap_sleeve")
        a(k.shoulder(s), C(s * 6.2, 20.8, 0, 5.8, 0.6, 5.8), "acc", tag="lace")
    k.legs("cloth2", w=4.6)
    k.boots("dark", h=4.6, w=4.8, cuff="acc", sole="void")


@design(blade=ramp("#20222a", "#343844", "#4c5262", "#6c7486", "#949eb0", "#c8d0dc"), dark=BLACK, stone=ramp("#2e2c2c", "#484444", "#666060", "#88807e", "#ac a4a0".replace(" ", "")), leather=HIDE, wood=OAK,
        cloth=ramp("#141418", "#202026", "#2e2e36", "#404048"), bone=BONE, mail=ramp("#20222a", "#343844", "#4c5262", "#6c7486"), acc=BRASS, wrap=HEMP, fire=CANDLE, hot=CANDLE)
def gravewarden(k):
    """he digs and he guards: a skull-faced helm under a sexton's hood, spade and pick crossed on his back, a headstone for a pauldron"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.6, -0.8, 10.2, 8.4, 9.6), "cloth", tag="sexton_hood")
    a(h, C(0, 32.8, -1.4, 7.6, 1.4, 7.0), "cloth", tag="hood_peak")
    a(h, C(0, 24.4, 3.6, 7.8, 7.2, 2.2), "bone", tag="skull_face")
    a(h, C(0, 22.4, 3.8, 6.0, 2.2, 2.2), "bone", tag="skull_jaw")
    a(h, C(0, 24.4, 4.9, 1.2, 1.2, 0.4), "void", tag="nose")
    for x in (-2.0, -0.7, 0.7, 2.0):
        a(h, C(x, 22.6, 4.95, 0.3, 1.6, 0.3), "void", tag="teeth")
    for s in SIDES:
        a(h, C(s * 2.0, 27.0, 4.8, 2.2, 2.0, 0.3), "void", tag="eye")
        k.fire(h, C(s * 2.0, 27.5, 4.95, 1.0, 1.0, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.8), "blade", tag="breastplate")
    a(c, C(0, 12.2, 3.0, 8.0, 6.4, 0.5), "cloth", tag="grave_coat")
    a(c, C(0, 16.4, 3.3, 1.4, 5.6, 0.4), "bone", tag="rib_mark")
    for y in (17.2, 18.8, 20.4):
        a(c, C(0, y, 3.3, 5.0, 0.7, 0.4), "bone", tag="rib_mark")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 6.4), "leather", tag="belt")
    a(c, C(3.4, 6.8, 3.5, 2.4, 3.0, 2.4), "dark", tag="lantern")
    k.fire(c, C(3.4, 7.2, 3.5, 2.6, 2.0, 1.4))
    a(c, C(3.4, 9.6, 3.5, 0.5, 2.8, 0.5), "acc", tag="lantern_chain")
    r1, r2 = (("z", 28),), (("z", -28),)
    a(b, C(0, 4.0, -3.6, 1.2, 26.0, 1.2), "wood", tag="spade_haft", rots=r1, pivot=(0, 18, -3.6))
    a(b, C(0, 29.4, -3.6, 4.8, 6.2, 0.7), "blade", tag="spade", rots=r1, pivot=(0, 18, -3.6))
    a(b, C(0, 35.2, -3.6, 2.6, 1.0, 0.6), "blade", tag="spade_tip", rots=r1, pivot=(0, 18, -3.6))
    a(b, C(0, 5.0, -4.6, 1.2, 25.0, 1.2), "wood", tag="pick_haft", rots=r2, pivot=(0, 18, -4.6))
    a(b, C(0, 29.4, -4.6, 13.0, 1.6, 1.4), "blade", tag="pick", rots=r2, pivot=(0, 18, -4.6))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 11.2, 0, 5.6, 5.8, 5.6), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.0, 1.0, 6.0), "leather", tag="cuff")
    q = k.shoulder(-1)
    a(q, C(-7.4, 20.6, 0, 5.4, 7.4, 8.0), "stone", tag="headstone")
    a(q, C(-7.4, 28.0, 0, 5.4, 1.4, 5.4), "stone", tag="headstone_arch")
    a(q, C(-7.4, 23.4, 4.05, 0.8, 3.2, 0.3), "dark", tag="stone_cut")
    a(q, C(-7.4, 25.0, 4.05, 2.6, 0.8, 0.3), "dark", tag="stone_cut")
    a(k.shoulder(1), C(6.6, 21.0, 0, 6.4, 3.0, 6.6), "blade", tag="pauldron")
    a(k.shoulder(1), C(6.6, 20.5, 0, 6.8, 0.8, 7.0), "dark", tag="pauldron_edge")
    for s in SIDES:
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 2.4, 0, 4.8, 9.6, 4.8), "blade", tag="cuisse")
        a(p, C(x, 6.2, 2.5, 3.8, 5.8, 0.6), "cloth", tag="coat_panel")
    k.boots("leather", h=4.4, w=5.0, cuff="dark", toe="blade", toe_d=2.2)


@design(wood=ramp("#0c0806", "#181010", "#26191a", "#362426", "#4a3234", "#6a4a4c"), blade=ramp("#0c0806", "#181010", "#26191a", "#362426", "#4a3234", "#6a4a4c"), dark=BLACK, acc=GILT, gold=GILT,
        cloth=ramp("#3a0c18", "#5a1424", "#7e2034", "#a43248"), leather=HIDE, mail=ramp("#14141a", "#24242c", "#383842", "#50505c"), wax=WAXEN, fire=CANDLE, hot=CANDLE)
def coffinplate(k):
    """a knight sealed in with his dead: a gilded death mask, a coffin lid for a breastplate, the coffin itself stood upright on his back with the handles still on"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.4, 0, 10.0, 9.0, 10.0), "wood", tag="helm")
    a(h, C(0, 32.2, 0, 8.0, 1.0, 8.0), "wood", tag="helm_top")
    a(h, C(0, 23.8, 4.9, 7.8, 8.2, 0.9), "acc", tag="death_mask")
    a(h, C(0, 26.0, 5.5, 1.5, 3.0, 0.9), "acc", tag="mask_nose")
    a(h, C(0, 24.8, 5.4, 3.6, 0.5, 0.3), "void", tag="mask_mouth")
    for s in SIDES:
        a(h, C(s * 2.2, 28.0, 5.4, 2.2, 0.7, 0.3), "void", tag="closed_eye")
        a(h, C(s * 5.2, 23.4, 0, 0.5, 8.0, 7.0), "acc", tag="cheek_strip")
    k.rivets(h, [(x, 32.4) for x in (-3.6, -1.2, 1.2, 3.6)], 4.2, 0.9)
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.4), "wood", tag="cuirass")
    a(c, C(0, 16.0, 3.3, 6.8, 8.0, 0.5), "dark", tag="lid_inlay")
    a(c, C(0, 12.2, 3.3, 3.4, 3.8, 0.5), "dark", tag="lid_inlay")
    a(c, C(0, 13.4, 3.55, 1.4, 9.6, 0.4), "acc", tag="lid_cross")
    a(c, C(0, 19.4, 3.55, 5.4, 1.4, 0.4), "acc", tag="lid_cross")
    k.rivets(c, [(-3.6, 22.8), (3.6, 22.8), (-3.8, 16.2), (3.8, 16.2), (-1.8, 12.6), (1.8, 12.6)], 3.7)
    a(c, C(0, 12.2, 0, 8.7, 1.4, 7.0), "dark", tag="belt")
    a(b, C(0, 18.0, -6.0, 10.4, 17.0, 3.8), "wood", tag="coffin")
    a(b, C(0, 12.6, -6.0, 8.2, 6.0, 3.8), "wood", tag="coffin_foot")
    a(b, C(0, 7.8, -6.0, 5.8, 5.0, 3.8), "wood", tag="coffin_foot")
    a(b, C(0, 34.8, -6.0, 7.4, 2.8, 3.8), "wood", tag="coffin_head")
    a(b, C(0, 9.0, -8.1, 1.4, 25.0, 0.5), "acc", tag="coffin_cross")
    a(b, C(0, 27.4, -8.1, 7.6, 1.4, 0.5), "acc", tag="coffin_cross")
    k.fire(b, C(0, 26.6, -8.4, 3.0, 3.0, 0.3))
    for s in SIDES:
        a(b, C(s * 5.5, 18.0, -6.0, 0.6, 3.4, 1.4), "acc", tag="coffin_handle")
        a(b, C(s * 5.5, 28.4, -6.0, 0.6, 3.4, 1.4), "acc", tag="coffin_handle")
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 11.2, 0, 5.8, 5.8, 5.8), "wood", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.2, 1.0, 6.2), "acc", tag="cuff")
        q = k.shoulder(s)
        a(q, C(x + s * 1.2, 20.6, 0, 8.2, 3.2, 8.6), "wood", tag="lid_shoulder")
        a(q, C(x + s * 1.2, 23.7, 0, 6.6, 1.0, 7.0), "dark", tag="lid_top")
        a(q, C(x + s * 1.2, 20.6, 4.35, 8.2, 1.0, 0.3), "acc", tag="lid_edge")
        k.rivets(q, [(x + s * 0.0, 22.4), (x + s * 2.4, 22.4)], 4.3)
        p = k.leg(s)
        x = s * 1.95
        a(p, C(x, 2.4, 0, 5.0, 9.6, 5.0), "wood", tag="cuisse")
        a(p, C(x, 4.8, 2.6, 3.8, 2.8, 0.8), "acc", tag="poleyn")
    k.boots("wood", h=4.2, cuff="acc", toe="dark", toe_d=2.8)


# ---------------------------------------------------------------- the Plague Ward

@design(cloth=ramp("#14100a", "#221c12", "#34281a", "#483824", "#604c30"), leather=ramp("#201408", "#34220e", "#4c3416", "#664a20"), bone=ramp("#8a7a56", "#a89870", "#c8b890", "#e0d4b0", "#f4eed4"), dark=BLACK, acc=BRASS, wood=OAK, blade=ramp("#20281c", "#344030", "#4c5c44", "#6c8060"), fire=FEVER, hot=FEVER)
def beakmask(k):
    """the plague doctor: a broad hat, a long waxed beak stuffed with herbs, green glass eyes, the waxed coat to the ankles and a rack of remedies on the belt"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.8, -0.4, 9.2, 7.6, 9.2), "leather", tag="hood")
    a(h, C(0, 31.2, 0, 15.0, 0.8, 15.0), "cloth", tag="hat_brim")
    a(h, C(0, 31.8, 0, 8.4, 4.0, 8.4), "cloth", tag="hat")
    a(h, C(0, 31.8, 0, 8.7, 1.0, 8.7), "acc", tag="hat_band")
    for z, w, ht, y in ((5.2, 5.4, 4.8, 25.0), (7.4, 4.0, 3.6, 24.6), (9.4, 2.8, 2.6, 24.2), (11.2, 1.8, 1.8, 23.8), (12.8, 1.0, 1.0, 23.6)):
        a(h, C(0, y, z, w, ht, 2.4), "bone", tag="beak")
    a(h, C(0, 26.6, 7.0, 0.5, 1.4, 4.0), "leather", tag="beak_strap")
    for s in SIDES:
        a(h, C(s * 2.5, 28.0, 4.6, 3.2, 3.2, 0.8), "acc", tag="lens_rim")
        k.fire(h, C(s * 2.5, 28.5, 5.05, 2.2, 2.2, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="waxed_coat")
    a(c, C(0, 20.4, 0, 8.7, 3.6, 6.2), "leather", tag="cape_collar")
    for y in (14.0, 16.2, 18.4):
        a(c, C(0, y, 2.75, 1.0, 1.0, 0.5), "acc", tag="clasp")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 5.8), "leather", tag="belt")
    for x in (-3.2, -1.6, 1.6, 3.2):
        a(c, C(x, 11.0, 3.2, 1.2, 2.8, 1.2), "acc", tag="vial_cap")
        k.fire(c, C(x, 11.3, 3.85, 0.9, 1.8, 0.3))
    a(b, C(0, 17.2, -3.8, 8.0, 6.6, 1.2), "leather", tag="back_cape")
    a(b, C(-2.6, 13.0, -4.0, 5.0, 4.6, 2.6), "leather", tag="satchel")
    a(b, C(-2.6, 17.4, -4.0, 5.4, 0.8, 3.0), "cloth", tag="satchel_flap")
    a(b, C(3.0, 8.0, -3.6, 0.9, 24.0, 0.9), "wood", tag="cane", rots=(("z", 8),), pivot=(3, 20, -3.6))
    a(b, C(3.0, 31.6, -3.6, 1.8, 1.8, 1.8), "acc", tag="cane_knob", rots=(("z", 8),), pivot=(3, 20, -3.6))
    k.arms("cloth", "leather", cuff="acc", w=5.2)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.3, 21.0, 0, 5.8, 2.6, 5.8), "leather", tag="cape_shoulder")
    k.legs("cloth", w=4.6)
    k.boots("leather", h=3.2, w=4.8, cuff="cloth", toe="dark", toe_d=3.0)


@design(cloth=ramp("#5e6862", "#7c8880", "#9ca89e", "#bcc6ba", "#dce2d6"), wrap=PALE, leather=ramp("#1c2420", "#2c3832", "#405048", "#586a60"), dark=BLACK, blade=ramp("#2c3432", "#485452", "#6c7a78", "#98a8a4", "#ccdcd8", "#f0fcf8"), acc=BRASS, wood=OAK,
        hide2=ramp("#3e0a0a", "#5e1010", "#841a1a", "#a82a24"), fire=FEVER, hot=FEVER)
def orderly(k):
    """the ward's runner: bandaged head, a surgeon's mirror on the brow, a rubber apron with the day's work on it, needles in a bandolier and a bone saw on the back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.0, 8.2, 9.2), "wrap", tag="bandage_head")
    for y, t in ((25.0, 8), (27.0, -6), (29.6, 10), (31.4, -8)):
        a(h, C(0, y, -0.2, 9.5, 0.7, 9.7), "cloth", tag="bandage_turn", rots=(("z", t * 0.4),), pivot=(0, y, 0))
    a(h, C(0, 23.2, 4.3, 7.4, 3.8, 0.7), "cloth", tag="face_mask")
    for s in SIDES:
        a(h, C(s * 4.0, 25.6, 3.4, 0.7, 0.5, 2.6), "dark", tag="mask_tie")
    a(h, C(0, 29.2, 4.6, 9.4, 1.0, 0.6), "dark", tag="mirror_band")
    a(h, C(1.6, 29.0, 5.2, 3.6, 3.6, 0.5), "blade", tag="head_mirror")
    k.fire(h, C(1.6, 30.0, 5.5, 1.2, 1.2, 0.3))
    k.fire(h, C(-2.2, 27.8, 4.65, 1.2, 0.7, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.8), "cloth", tag="smock")
    a(c, C(0, 12.2, 2.6, 7.6, 11.0, 0.6), "leather", tag="rubber_apron")
    a(c, C(1.8, 14.6, 2.95, 2.8, 3.8, 0.3), "hide2", tag="stain")
    a(c, C(-2.4, 18.2, 2.95, 1.8, 2.0, 0.3), "hide2", tag="stain")
    for i in range(6):
        t = i / 5
        x, y = -3.8 + 7.6 * t, 22.0 - 8.4 * t
        a(c, C(x, y, 3.1, 1.2, 0.5, 0.5), "dark", tag="bandolier")
        a(c, C(x, y + 0.4, 3.45, 0.7, 2.2, 0.5), "blade", tag="syringe")
        k.fire(c, C(x, y + 0.9, 3.75, 0.5, 1.2, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.6), "dark", tag="belt")
    a(b, C(0, 13.0, -3.2, 7.0, 3.0, 0.6), "dark", tag="strap")
    rz = (("z", 40),)
    a(b, C(0, 8.0, -3.4, 4.6, 16.0, 0.5), "blade", tag="saw", rots=rz, pivot=(0, 16, -3.4))
    a(b, C(0, 7.0, -3.4, 2.0, 1.4, 0.4), "wood", tag="saw_handle", rots=rz, pivot=(0, 16, -3.4))
    a(b, C(-2.6, 24.0, -3.4, 0.5, 0.5, 0.5), "dark", tag="saw", rots=rz, pivot=(0, 16, -3.4))
    for i in range(7):
        a(b, C(2.5, 9.0 + i * 2.2, -3.4, 0.8, 1.2, 0.4), "blade", tag="saw_tooth", rots=rz, pivot=(0, 16, -3.4))
    k.arms("cloth", "wrap", cuff="dark", w=5.0)
    for s in SIDES:
        for y in (12.6, 14.4):
            a(k.arm(s), C(s * 6.0, y, 0, 5.3, 0.6, 5.3), "cloth", tag="bandage_turn")
        a(k.shoulder(s), C(s * 6.2, 21.2, 0, 5.4, 2.0, 5.4), "leather", tag="cop")
        a(k.leg(s), C(s * 1.95, 6.2, 2.5, 3.8, 5.8, 0.6), "leather", tag="apron_panel")
        a(k.leg(s), C(s * 3.8 if s > 0 else -3.8, 8.0, 0.6, 1.2, 3.4, 2.4), "dark", tag="scalpel_roll")
    k.legs("cloth", w=4.6)
    k.boots("leather", h=4.0, w=4.8, cuff="wrap")


@design(cloth=ramp("#2a2014", "#3e3020", "#54442c", "#6e5a3c", "#8a7450"), wood=ramp("#3a2a14", "#5a4220", "#7c5e30", "#a07e44", "#c4a260"), wrap=HEMP, leather=ramp("#1c120e", "#2e1e16", "#463022", "#604430"), dark=BLACK,
        mail=ramp("#242018", "#3a3428", "#54503e", "#726c56"), acc=BRASS, blade=ramp("#242018", "#3a3428", "#54503e", "#726c56", "#969078"), gem=FEVER, fire=FEVER, hot=FEVER)
def friar(k):
    """a begging friar who stayed with the dying: habit and rope over old mail, a leper's bell at the hip, a wicker pack of clean rags, a bare tonsured hood thrown back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, 0, 9.4, 8.0, 9.4), "mail", tag="coif")
    a(h, C(0, 32.0, 0, 6.4, 0.7, 6.4), "dark", tag="tonsure")
    a(h, C(0, 22.4, -2.8, 10.4, 4.6, 6.2), "cloth", tag="thrown_hood")
    a(h, C(0, 22.4, 0.6, 11.0, 2.0, 10.0), "cloth", tag="hood_collar")
    a(h, C(0, 26.4, 4.8, 7.6, 2.2, 0.4), "wrap", tag="fever_rag")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 28.8, 4.85, 1.2, 0.6, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="habit")
    a(c, C(0, 12.2, 2.75, 3.4, 11.8, 0.5), "cloth", tag="scapular")
    a(c, C(0, 12.4, 0, 8.7, 1.1, 5.8), "wrap", tag="rope")
    for i, y in enumerate((10.6, 8.4, 6.2)):
        a(c, C(1.6, y, 3.4, 1.4, 1.4, 1.4), "wrap", tag="rope_knot")
        a(c, C(1.6, y, 3.4, 0.6, 2.4, 0.6), "wrap", tag="rope_end")
    a(c, C(-3.3, 8.8, 3.5, 2.8, 2.8, 2.8), "acc", tag="leper_bell")
    a(c, C(-3.3, 8.0, 3.5, 3.4, 0.9, 3.4), "acc", tag="bell_lip")
    a(c, C(-3.3, 11.6, 3.5, 0.6, 1.2, 0.6), "dark", tag="bell_strap")
    k.fire(c, C(0, 16.2, 3.1, 1.2, 3.6, 0.3))
    k.fire(c, C(0, 18.0, 3.1, 2.8, 1.0, 0.3))
    a(b, C(0, 12.0, -5.0, 8.4, 12.0, 5.2), "wood", tag="wicker_pack")
    for y in (13.4, 16.4, 19.4, 22.4):
        a(b, C(0, y, -5.0, 8.8, 0.8, 5.6), "wrap", tag="wicker_band")
    for x in (-3.0, 0, 3.0):
        a(b, C(x, 12.2, -7.8, 0.8, 11.6, 0.4), "wrap", tag="wicker_rib")
    a(b, C(0, 24.0, -5.0, 7.0, 2.2, 4.0), "cloth", tag="rags")
    a(b, C(2.0, 25.8, -5.0, 3.0, 1.6, 2.6), "wrap", tag="rags")
    k.arms("cloth", "mail", cuff="cloth", w=5.2)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.3, 20.8, 0, 6.0, 2.8, 6.0), "cloth", tag="habit_shoulder")
        a(k.arm(s), C(s * 6.0, 13.6, 0, 5.5, 2.4, 5.5), "wrap", tag="rag_bandage")
    k.legs("cloth", w=4.7)
    for s in SIDES:
        a(k.leg(s), C(s * 1.95, 2.2, 2.2, 3.6, 7.4, 0.8), "mail", tag="mail_shin")
    k.boots("leather", h=1.6, w=5.0, toe="wood", toe_d=2.4, sole="wood")


@design(blade=LEAD, dark=BLACK, acc=ramp("#6a5206", "#a07c0c", "#d4ac18", "#f4d034", "#ffec7c"), leather=ramp("#10201a", "#1a3228", "#284a3a", "#3a6450"), mail=LEAD, gem=ramp("#143c1a", "#1e6226", "#329a34", "#58cc50", "#a0f088", "#e4ffd0"), cloth=ramp("#10201a", "#1a3228", "#284a3a"), fire=FEVER, hot=FEVER)
def quarantine(k):
    """no air gets in: a sealed lead suit, a glass dome with the fever-fog swirling in it, twin scrubber tanks, warning stripes on every plate"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 22.6, 0, 10.8, 2.4, 10.8), "blade", tag="neck_ring")
    a(h, C(0, 25.0, -0.8, 10.0, 8.4, 8.8), "blade", tag="helm_back")
    a(h, C(0, 26.0, 3.8, 8.0, 5.8, 1.6), "dark", tag="dome_frame")
    k.fire(h, C(0, 26.6, 4.7, 6.8, 4.6, 0.3))
    for x in (-2.2, 2.2):
        a(h, C(x, 26.2, 4.95, 0.5, 5.2, 0.3), "dark", tag="dome_bar")
    a(h, C(0, 33.4, -0.8, 7.0, 1.0, 6.0), "blade", tag="helm_top")
    a(h, C(0, 22.4, 5.4, 4.2, 2.6, 2.0), "dark", tag="filter")
    a(h, C(0, 22.8, 6.5, 3.2, 1.6, 0.3), "acc", tag="filter_stripe")
    for s in SIDES:
        a(h, C(s * 5.3, 26.0, 0, 1.4, 3.0, 3.0), "acc", tag="ear_seal")
        a(h, C(s * 4.0, 34.2, -0.8, 1.2, 1.8, 1.2), "dark", tag="vent")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.4), "blade", tag="sealed_plate")
    for x in (-3.0, -1.0, 1.0, 3.0):
        a(c, C(x, 20.2, 3.3, 1.1, 2.6, 0.3), "acc" if x in (-3.0, 1.0) else "dark", tag="stripe")
    a(c, C(0, 13.6, 3.3, 5.0, 5.4, 0.5), "dark", tag="glass_port")
    k.fire(c, C(0, 14.2, 3.6, 3.6, 4.0, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.0), "dark", tag="belt")
    for s in SIDES:
        a(b, C(s * 2.3, 12.4, -5.2, 3.8, 12.0, 3.8), "blade", tag="tank")
        a(b, C(s * 2.3, 24.4, -5.2, 2.2, 1.2, 2.2), "dark", tag="tank_valve")
        a(b, C(s * 2.3, 16.0, -7.25, 2.4, 5.0, 0.4), "gem", tag="tank_gauge")
        a(b, C(s * 2.3, 14.0, -5.2, 4.1, 0.8, 4.1), "acc", tag="tank_stripe")
        a(b, C(s * 2.3, 22.2, -5.2, 4.1, 0.8, 4.1), "acc", tag="tank_stripe")
        a(b, C(s * 2.3, 25.6, -5.2, 1.0, 2.2, 1.0), "dark", tag="hose")
        a(b, C(s * 2.3, 27.0, -3.0, 1.0, 1.0, 3.6), "dark", tag="hose")
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "leather", tag="sleeve")
        k.elbow(s, "leather")
        a(p, C(x, 11.0, 0, 6.2, 5.8, 6.2), "blade", tag="glove")
        a(p, C(x, 16.0, 0, 6.5, 1.0, 6.5), "acc", tag="seal")
        q = k.shoulder(s)
        a(q, C(x + s * 0.8, 20.6, 0, 7.6, 3.6, 7.8), "blade", tag="plate_shoulder")
        for t in (-2.4, 0.0, 2.4):
            a(q, C(x + s * 0.8, 24.1, t, 7.8, 0.5, 1.1), "acc", tag="stripe")
        p = k.leg(s)
        x = s * 1.95
        a(p, C(x, 2.4, 0, 5.0, 9.6, 5.0), "leather", tag="suit_leg")
        a(p, C(x, 6.6, 0, 5.3, 4.6, 5.3), "blade", tag="cuisse")
        a(p, C(x, 2.4, 2.4, 3.6, 3.6, 0.8), "blade", tag="shin")
    k.boots("blade", h=3.8, w=5.4, cuff="acc", sole="dark")


# ---------------------------------------------------------------- the Faceless Temple

@design(cloth=ramp("#14143a", "#1e1e56", "#2c2c7a", "#3e3ea0", "#5656c0"), wrap=PALE, bone=PALE, gem=CRYSTAL, dark=ramp("#0e0e1c", "#18182c", "#242440", "#343458"), acc=GILT, leather=ramp("#101028", "#1a1a3c", "#262654"), blade=CRYSTAL, fire=CRYSTAL, hot=CRYSTAL, no_skirt=False)
def acolyte(k):
    """a novice who gave up his face: a smooth white mask, nothing behind it, a broken halo of crystal shards standing round the head"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.6, -0.6, 9.6, 9.0, 9.2), "cloth", tag="hood")
    a(h, C(0, 32.6, -1.0, 6.8, 1.0, 6.8), "cloth", tag="hood_peak")
    a(h, C(0, 24.0, 3.9, 7.4, 7.8, 1.0), "bone", tag="blank_mask")
    a(h, C(0, 22.0, 0, 11.0, 2.6, 11.0), "wrap", tag="collar")
    k.fire(h, C(0, 27.4, 4.45, 0.5, 3.2, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 12.2, 2.75, 2.6, 11.8, 0.5), "wrap", tag="stole")
    a(c, C(0, 12.2, 0, 8.7, 1.4, 5.8), "wrap", tag="sash")
    a(c, C(0, 16.4, 3.1, 2.0, 3.0, 0.6), "gem", tag="chest_shard")
    a(c, C(0, 19.2, 3.1, 1.2, 1.4, 0.6), "gem", tag="chest_shard")
    for t, ln, w in ((-96, 5.0, 2.0), (-68, 3.4, 1.6), (-40, 6.0, 2.2), (-14, 3.6, 1.6), (14, 5.4, 2.0), (42, 3.0, 1.4), (70, 6.4, 2.2), (98, 3.8, 1.6)):
        a(b, C(0, 37.8, -6.2, w, ln, w), "gem", tag="halo_shard", rots=(("z", t),), pivot=(0, 28.5, -6.2))
    k.fire(b, C(0, 27.6, -6.2, 1.2, 1.8, 0.3))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "cloth", tag="sleeve")
        k.elbow(s, "cloth")
        a(p, C(x, 10.8, 0, 6.4, 5.8, 6.4), "cloth", tag="flare")
        a(p, C(x, 10.8, 0, 6.7, 0.9, 6.7), "wrap", tag="hem")
        a(k.shoulder(s), C(x + s * 0.3, 21.0, 0, 5.8, 2.6, 5.8), "wrap", tag="mantle")
    k.legs("cloth", w=4.6)
    k.boots("wrap", h=2.2, w=4.8)


@design(cloth=ramp("#08081a", "#10102a", "#1a1a3e", "#262654", "#343470"), bone=PALE, gem=CRYSTAL, leather=ramp("#101028", "#1a1a3c", "#262654", "#343468"), dark=ramp("#0e0e1c", "#18182c", "#242440"), blade=CRYSTAL, fire=CRYSTAL, hot=CRYSTAL)
def faceless(k):
    """the crystal is taking him: a blank mask split down the middle with light behind it, one arm and shoulder already grown over, the cloak cut to ribbons"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.2, -0.6, 9.2, 8.2, 9.2), "cloth", tag="hood")
    a(h, C(0, 24.0, 3.9, 7.8, 8.2, 1.0), "bone", tag="blank_mask")
    a(h, C(0.8, 24.0, 4.35, 0.7, 8.2, 0.3), "void", tag="split")
    k.fire(h, C(0.8, 25.0, 4.5, 0.4, 6.2, 0.3))
    k.spike(h, -3.6, 31.6, 2.0, 5.4, 2.6, "gem", rz=20, rx=-14)
    k.spike(h, -1.6, 32.0, 3.0, 3.2, 1.6, "gem", rz=-6, rx=-20)
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.0), "leather", tag="jerkin")
    a(c, C(0, 12.2, 0, 8.7, 1.4, 5.6), "dark", tag="belt")
    for y in (15.0, 18.0):
        a(c, C(0, y, 2.65, 7.4, 0.8, 0.5), "dark", tag="wrap_strap")
    for x, y, l in ((-2.6, 21.6, 2.8), (-3.6, 18.2, 3.6)):
        k.spike(c, x, y, 2.9, l, 2.0, "gem", rx=-44, rz=26)
    for i, x in enumerate((-3.4, -1.1, 1.2, 3.5)):
        ln = (17.0, 13.0, 19.0, 10.0)[i]
        a(b, C(x, 23.0 - ln, -3.4, 1.8, ln, 0.6), "cloth", tag="cloak_ribbon", rots=(("x", 8 + i), ("z", (x * 1.4))), pivot=(x, 23.0, -3.4))
    p, x = k.arm(-1), -6.0
    a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "gem", tag="crystal_arm")
    a(p, C(x, 18.4, 0, 5.8, 3.6, 5.8), "gem", tag="crystal_arm")
    k.elbow(-1, "dark")
    k.spike(p, x - 2.4, 15.2, 1.6, 4.4, 2.0, "gem", rz=52, rx=-14)
    k.spike(p, x - 2.2, 12.0, -1.8, 3.6, 1.8, "gem", rz=64, rx=24)
    k.spike(p, x + 0.6, 12.6, 2.8, 3.0, 1.6, "gem", rx=-66)
    q = k.shoulder(-1)
    a(q, C(x - 1.0, 20.8, 0, 7.4, 3.2, 7.4), "gem", tag="crystal_shoulder")
    k.spike(q, x - 2.4, 23.6, 0.6, 8.6, 3.4, "gem", rz=30, rx=6, steps=4)
    k.spike(q, x + 0.8, 23.8, -2.0, 5.8, 2.4, "gem", rz=8, rx=22)
    k.spike(q, x - 3.6, 22.4, 2.4, 4.8, 2.0, "gem", rz=62, rx=-16)
    p, x = k.arm(1), 6.0
    a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "leather", tag="sleeve")
    k.elbow(1, "cloth")
    a(p, C(x, 11.4, 0, 5.2, 5.4, 5.2), "cloth", tag="wraps")
    a(k.shoulder(1), C(6.2, 21.0, 0, 5.4, 2.2, 5.4), "leather", tag="cop")
    k.legs("leather", w=4.6)
    k.boots("leather", h=3.4, w=4.8, cuff="cloth")
    k.spike(k.leg(-1), -3.6, 7.0, 1.0, 3.2, 1.6, "gem", rz=48)


@design(stone=ramp("#26263a", "#3a3a52", "#54546e", "#74748e", "#9a9ab0", "#c8c8d6"), blade=ramp("#26263a", "#3a3a52", "#54546e", "#74748e", "#9a9ab0"), dark=ramp("#0e0e1c", "#18182c", "#242440", "#343458"), gem=CRYSTAL, mail=ramp("#26263a", "#3a3a52", "#54546e", "#74748e"), acc=GILT, leather=ramp("#101028", "#1a1a3c", "#262654"), fire=CRYSTAL, hot=CRYSTAL)
def sentinel(k):
    """the temple's door-ward, more statue than man: a tall slab of a head with no features at all, a crystal let into the chest, shoulders of cut stone like lintels"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.0, 0, 9.8, 16.0, 7.6), "stone", tag="slab")
    a(h, C(0, 38.8, 0, 11.4, 1.6, 8.8), "stone", tag="slab_cap")
    a(h, C(0, 23.0, 0, 11.0, 1.4, 9.0), "dark", tag="slab_foot")
    a(h, C(0, 30.2, 3.85, 0.8, 7.6, 0.3), "dark", tag="groove")
    a(h, C(0, 28.0, 3.85, 7.8, 0.8, 0.3), "dark", tag="groove")
    k.fire(h, C(0, 28.2, 4.05, 6.2, 0.5, 0.3))
    k.fire(h, C(0, 30.6, 4.05, 0.5, 7.0, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.4), "stone", tag="torso_block")
    a(c, C(0, 14.0, 3.3, 5.6, 7.6, 0.5), "dark", tag="niche")
    a(c, C(0, 15.0, 3.5, 3.2, 5.4, 1.2), "gem", tag="heart_crystal")
    a(c, C(0, 16.2, 4.0, 1.6, 2.8, 0.8), "gem", tag="heart_crystal")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.0), "dark", tag="belt")
    a(b, C(0, 13.0, -4.0, 7.0, 10.0, 1.8), "stone", tag="back_block")
    for y in (15.0, 19.0):
        a(b, C(0, y, -5.0, 7.4, 0.8, 0.5), "dark", tag="back_groove")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 10.8, 0, 6.2, 6.2, 6.2), "stone", tag="forearm_block")
        a(p, C(x, 16.0, 0, 6.6, 1.0, 6.6), "dark", tag="cuff")
        k.fire(p, C(x, 13.4, 3.15, 2.8, 0.5, 0.3))
        q = k.shoulder(s)
        a(q, C(x + s * 1.8, 20.5, 0, 10.0, 2.0, 8.0), "stone", tag="lintel")
        a(q, C(x + s * 1.8, 22.4, 0, 8.4, 2.0, 7.0), "stone", tag="lintel")
        a(q, C(x + s * 1.8, 24.3, 0, 6.2, 1.2, 5.4), "dark", tag="lintel_top")
        p = k.leg(s)
        x = s * 1.95
        a(p, C(x, 2.4, 0, 5.1, 9.6, 5.1), "stone", tag="leg_block")
        a(p, C(x, 6.6, 2.6, 3.6, 0.7, 0.4), "dark", tag="groove")
    k.boots("stone", h=4.0, w=5.8, cuff="dark", sole="dark")


@design(blade=ramp("#161434", "#22205a", "#322e80", "#4a46a8", "#6c68cc", "#a09ce8"), acc=GILT, gold=GILT, dark=ramp("#0a0a18", "#14142a", "#20203e", "#2e2e58"), gem=CRYSTAL, cloth=ramp("#2a0a44", "#3e1064", "#5a1a8c", "#7a2cb4"), mail=ramp("#161434", "#22205a", "#322e80", "#4a46a8"), bone=PALE, leather=ramp("#101028", "#1a1a3c", "#262654"), fire=CRYSTAL, hot=CRYSTAL)
def sovereign(k):
    """the temple's god-king, the bar for the rank: a gold mask under a crown of crystal spires, and a great fan of crystal wings behind him"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.0, 0, 10.4, 8.6, 10.4), "blade", tag="helm")
    a(h, C(0, 23.4, 4.9, 8.0, 7.6, 1.0), "acc", tag="gold_mask")
    k.fire(h, C(0, 27.4, 5.45, 6.0, 0.6, 0.3))
    a(h, C(0, 31.2, 0, 11.4, 1.8, 11.4), "acc", tag="crown_band")
    for t, (x, z, ln) in enumerate(((0, 4.8, 12.0), (-3.0, 4.2, 8.0), (3.0, 4.2, 8.0), (-5.4, 1.0, 9.4), (5.4, 1.0, 9.4), (-4.2, -3.6, 6.4), (4.2, -3.6, 6.4), (0, -5.0, 7.6))):
        k.spike(h, x, 32.8, z, ln, 2.8, "gem", rz=-x * 2.2, rx=-z * 1.0, tag="crown_spire", steps=4)
    for s in SIDES:
        a(h, C(s * 5.6, 24.0, 1.0, 0.8, 7.0, 6.0), "acc", tag="cheek")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.6), "blade", tag="cuirass")
    a(c, C(0, 20.6, 0, 8.7, 3.4, 7.2), "acc", tag="gorget")
    a(c, C(0, 14.6, 3.4, 5.4, 6.0, 0.5), "acc", tag="sun_plate")
    a(c, C(0, 15.4, 3.6, 3.8, 4.2, 1.0), "gem", tag="sun_gem")
    k.fire(c, C(0, 16.4, 4.2, 1.8, 2.0, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.2), "acc", tag="belt")
    a(b, C(0, 8.0, -3.8, 7.4, 15.0, 0.7), "cloth", tag="short_cape", rots=(("x", 10),), pivot=(0, 23, -3.8))
    for s in SIDES:
        for i, (t, ln, w) in enumerate(((26, 13.0, 3.0), (46, 17.0, 3.2), (66, 19.0, 3.2), (88, 19.0, 3.0), (110, 15.0, 2.8), (130, 10.0, 2.4))):
            k.spike(b, s * 1.8, 20.0, -5.4 - i * 0.2, ln, w, "gem", rz=-s * t, steps=4, tag="crystal_wing")
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 10.8, 0, 6.0, 6.0, 6.0), "blade", tag="vambrace")
        a(p, C(x, 15.8, 0, 6.5, 1.2, 6.5), "acc", tag="cuff")
        k.spike(p, x + s * 3.0, 13.4, 0, 3.6, 1.8, "gem", rz=-s * 56)
        q = k.shoulder(s)
        a(q, C(x + s * 1.4, 20.5, 0, 8.8, 3.8, 9.0), "blade", tag="pauldron")
        a(q, C(x + s * 1.4, 20.3, 0, 9.2, 1.0, 9.4), "acc", tag="pauldron_rim")
        a(q, C(x + s * 1.4, 24.2, 0, 6.6, 0.8, 6.8), "acc", tag="pauldron_top")
        k.spike(q, x + s * 2.0, 24.8, 0, 7.4, 3.4, "gem", rz=-s * 22, steps=4)
        k.spike(q, x + s * 4.6, 23.6, 0, 4.6, 2.2, "gem", rz=-s * 54)
        p = k.leg(s)
        x = s * 1.95
        a(p, C(x, 2.4, 0, 5.1, 9.6, 5.1), "blade", tag="cuisse")
        a(p, C(x, 4.6, 2.6, 4.0, 3.0, 1.0), "acc", tag="poleyn")
        a(p, C(x, 5.2, 3.15, 1.6, 1.6, 0.4), "gem", tag="knee_gem")
    k.boots("blade", h=4.0, w=5.2, cuff="acc", toe="acc", toe_d=3.0)


# ---------------------------------------------------------------- the Ossuary Engine

@design(cloth=ramp("#1a0e08", "#2c1a10", "#42281a", "#5a3a26", "#785034"), wrap=PALE, bone=BONE, acc=ramp("#3e2206", "#6e420c", "#a8701a", "#d8a430", "#f6d468"), dark=BLACK, leather=HIDE, blade=ramp("#3e2206", "#6e420c", "#a8701a", "#d8a430"), fire=TOLL, hot=TOLL)
def cantor(k):
    """he sings the engine's hours: a ruff like a choirboy's, a real ribcage worn over the robe, and the toll bell slung in a frame above his head"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.2, -0.2, 9.0, 8.0, 9.2), "cloth", tag="hood")
    a(h, C(0, 22.6, 0, 12.6, 2.2, 12.6), "wrap", tag="ruff")
    for t in range(4):
        a(h, C(0, 22.8, 0, 13.2, 1.8, 2.0), "wrap", tag="ruff_pleat", rots=(("y", t * 45),), pivot=(0, 23, 0))
    a(h, C(0, 27.0, 4.3, 7.2, 3.8, 0.8), "dark", tag="singing_dark")
    a(h, C(0, 26.2, 4.6, 2.6, 2.4, 0.5), "void", tag="open_mouth")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 29.2, 4.8, 1.0, 0.7, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 12.2, 0, 8.7, 1.4, 5.8), "wrap", tag="sash")
    a(c, C(0, 13.6, 3.0, 1.2, 9.0, 0.7), "bone", tag="sternum")
    for i, y in enumerate((14.4, 16.2, 18.0, 19.8, 21.6)):
        a(c, C(0, y, 3.05, 8.2 - abs(i - 3) * 0.6, 0.9, 0.6), "bone", tag="rib")
    a(c, C(2.8, 8.8, 3.3, 2.6, 2.8, 2.6), "bone", tag="belt_skull")
    a(c, C(2.8, 11.4, 3.3, 0.5, 1.0, 0.5), "dark", tag="belt_skull_cord")
    for s in SIDES:
        a(b, C(s * 5.4, 23.0, -6.0, 1.2, 18.0, 1.2), "bone", tag="bell_frame", rots=(("z", -s * 6),), pivot=(s * 5.4, 23, -6.0))
    a(b, C(0, 13.0, -3.8, 8.0, 10.4, 1.2), "bone", tag="backbone_plate")
    a(b, C(0, 22.6, -5.2, 13.0, 1.6, 2.4), "bone", tag="bell_yoke")
    a(b, C(0, 40.2, -6.0, 13.0, 1.4, 1.4), "bone", tag="bell_beam")
    a(b, C(0, 32.0, -6.0, 6.4, 8.2, 5.4), "acc", tag="toll_bell")
    a(b, C(0, 37.6, -6.0, 4.4, 2.6, 3.8), "acc", tag="toll_bell_top")
    a(b, C(0, 30.8, -6.0, 8.0, 1.6, 7.0), "acc", tag="toll_bell_lip")
    a(b, C(0, 31.6, -8.8, 3.2, 3.2, 0.3), "dark", tag="bell_mark")
    k.fire(b, C(0, 29.0, -6.0, 1.6, 1.8, 1.6))
    k.arms("cloth", "cloth", cuff="wrap", w=5.6, low_h=5.2)
    for s in SIDES:
        q = k.shoulder(s)
        a(q, C(s * 6.3, 20.8, 0, 6.0, 2.6, 6.0), "cloth", tag="choir_shoulder")
        a(q, C(s * 6.3, 23.0, 0, 4.8, 1.0, 4.8), "wrap", tag="choir_shoulder_lace")
    k.legs("cloth", w=4.6)
    k.boots("dark", h=2.8, w=4.8)


@design(leather=ramp("#3a1e14", "#5c3020", "#82482e", "#a86644", "#cc8c64"), hide2=ramp("#3e2a1c", "#5c422c", "#806040", "#a48458", "#c8ac7c"), wrap=ramp("#0e0806", "#1a120e", "#2a1e18", "#3a2c24"), dark=BLACK, blade=ramp("#1a1412", "#32282a", "#544846", "#7e706a", "#b0a498"), bone=BONE, cloth=ramp("#1c120e", "#2e1e16", "#463022"), acc=IRON, fire=TOLL, hot=TOLL)
def stitchhide(k):
    """made from what was left over: patchwork skins sewn with black thread, a stitched sack face with one button eye, meat hooks swinging from the back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.8, 0, 9.4, 8.6, 9.4), "hide2", tag="sack_head")
    a(h, C(1.8, 28.0, 0, 6.0, 4.6, 9.7), "leather", tag="patch")
    a(h, C(0, 32.4, 0, 3.6, 1.8, 3.6), "wrap", tag="sack_tie")
    a(h, C(-0.6, 23.8, 4.8, 0.5, 8.6, 0.3), "wrap", tag="seam")
    for y in (25.0, 26.8, 28.6, 30.4):
        a(h, C(-0.6, y, 4.85, 2.0, 0.4, 0.3), "wrap", tag="stitch")
    a(h, C(-2.8, 28.0, 4.8, 2.6, 2.6, 0.4), "dark", tag="button")
    k.fire(h, C(-2.8, 28.6, 5.0, 1.4, 1.4, 0.3))
    a(h, C(2.4, 28.6, 4.85, 2.2, 0.5, 0.3), "wrap", tag="sewn_eye")
    a(h, C(0, 25.0, 4.85, 5.4, 0.5, 0.3), "wrap", tag="sewn_mouth")
    for x in (-2.0, -0.6, 0.8, 2.2):
        a(h, C(x, 24.4, 4.9, 0.4, 1.6, 0.3), "wrap", tag="stitch")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.0), "leather", tag="patchwork")
    a(c, C(-2.4, 16.2, 2.6, 3.8, 6.2, 0.4), "hide2", tag="patch")
    a(c, C(2.2, 12.8, 2.6, 4.0, 5.2, 0.4), "hide2", tag="patch")
    for y in (13.4, 15.2, 17.0):
        a(c, C(0.0, y, 2.85, 1.6, 0.4, 0.3), "wrap", tag="stitch")
    for y in (19.2, 21.0):
        a(c, C(-0.4, y, 2.85, 1.6, 0.4, 0.3), "wrap", tag="stitch")
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.6), "wrap", tag="belt")
    a(b, C(0, 22.6, -3.4, 9.0, 1.2, 1.2), "blade", tag="hook_bar")
    for x, ln in ((-3.6, 8.0), (-0.2, 13.0), (3.4, 6.0)):
        a(b, C(x, 22.6 - ln, -3.4, 0.5, ln, 0.5), "acc", tag="hook_chain")
        a(b, C(x, 21.0 - ln, -3.4, 0.9, 2.0, 0.9), "blade", tag="meat_hook")
        a(b, C(x - 0.8, 20.6 - ln, -3.4, 2.4, 0.8, 0.9), "blade", tag="meat_hook")
        a(b, C(x - 1.8, 20.8 - ln, -3.4, 0.8, 1.6, 0.8), "blade", tag="meat_hook")
    k.arms("leather", "hide2", cuff="wrap", w=5.0)
    for s in SIDES:
        a(k.arm(s), C(s * 6.0, 14.0, 2.7, 3.0, 0.5, 0.3), "wrap", tag="seam")
    a(k.shoulder(1), C(6.5, 20.8, 0, 6.2, 3.4, 6.2), "hide2", tag="stuffed_shoulder")
    a(k.shoulder(1), C(6.5, 22.2, 3.15, 3.6, 0.4, 0.3), "wrap", tag="seam")
    a(k.shoulder(-1), C(-6.2, 21.0, 0, 5.4, 2.4, 5.4), "leather", tag="cop")
    k.legs("hide2", w=4.6)
    a(k.leg(1), C(1.95, 6.0, 0, 4.9, 3.6, 4.9), "leather", tag="patch")
    k.boots("leather", h=3.6, w=4.8, cuff="wrap")


@design(bone=BONE, blade=BONE, dark=BLACK, leather=HIDE, mail=ramp("#2a2218", "#443a2a", "#62563e", "#847658"), acc=ramp("#3e2206", "#6e420c", "#a8701a", "#d8a430"), cloth=ramp("#1c120e", "#2e1e16", "#463022"), fire=TOLL, hot=TOLL)
def bonewright(k):
    """the engine's mechanic builds in bone: a great skull helm with a crest of vertebrae, ribs for a cuirass, a thigh bone on each shoulder, a bone cog turning behind him"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 25.0, -0.4, 10.4, 8.0, 10.4), "bone", tag="cranium")
    a(h, C(0, 22.6, 3.4, 8.0, 3.2, 3.6), "bone", tag="jaw")
    for x in (-3.0, -1.5, 0, 1.5, 3.0):
        a(h, C(x, 21.6, 5.0, 1.0, 1.8, 0.7), "bone", tag="tooth")
    a(h, C(0, 27.6, 4.9, 8.4, 2.0, 0.6), "dark", tag="sockets")
    a(h, C(0, 24.8, 5.05, 1.6, 1.8, 0.4), "void", tag="nose")
    for s in SIDES:
        k.fire(h, C(s * 2.4, 27.9, 5.25, 1.8, 1.2, 0.3))
    for i in range(6):
        z = 4.0 - i * 1.9
        ht = (1.4, 2.0, 2.4, 2.4, 2.0, 1.4)[i]
        a(h, C(0, 33.0, z, 2.4, 0.9, 1.5), "bone", tag="vertebra")
        k.spike(h, 0, 33.8, z, ht + 1.4, 1.3, "bone", steps=2, rx=14, tag="vertebra_spine")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.0), "dark", tag="under")
    a(c, C(0, 12.6, 2.9, 1.6, 10.6, 0.7), "bone", tag="sternum")
    for i, y in enumerate((14.0, 15.8, 17.6, 19.4, 21.2)):
        a(c, C(0, y, 2.9, 8.6, 1.0, 0.6), "bone", tag="rib")
    k.fire(c, C(0, 16.6, 2.65, 7.0, 3.6, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.4, 5.8), "leather", tag="belt")
    a(b, C(0, 13.0, -3.4, 1.6, 10.0, 1.4), "bone", tag="spine")
    for y in (14.0, 16.0, 18.0, 20.0, 22.0):
        a(b, C(0, y, -3.4, 8.2, 0.9, 0.9), "bone", tag="back_rib")
    for t in range(8):
        a(b, C(0, 17.8, -6.0, 2.4, 4.8 if t % 2 else 2.6, 1.2), "bone", tag="cog_tooth", rots=(("z", t * 45),), pivot=(0, 17.8, -6.0))
        a(b, C(0, 21.8 if t % 2 else 20.4, -6.0, 2.6, 2.0, 1.2), "bone", tag="cog_tooth", rots=(("z", t * 45),), pivot=(0, 17.8, -6.0))
    a(b, C(0, 15.4, -5.2, 5.0, 5.0, 1.0), "acc", tag="cog_hub")
    k.fire(b, C(0, 17.0, -6.9, 1.8, 1.8, 0.3))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 11.2, 0, 5.4, 5.6, 5.4), "bone", tag="ulna_bracer")
        for dz in (-1.3, 1.3):
            a(p, C(x, 11.2, dz + 2.0 * (1 if dz > 0 else -1), 5.0, 5.6, 0.5), "dark", tag="groove")
        q = k.shoulder(s)
        a(q, C(x + s * 0.8, 20.6, 0, 6.4, 2.6, 6.4), "bone", tag="scapula")
        a(q, C(x + s * 0.8, 23.4, 0, 1.8, 1.8, 11.0), "bone", tag="femur")
        a(q, C(x + s * 0.8, 22.8, 5.8, 3.0, 3.0, 2.6), "bone", tag="femur_head")
        a(q, C(x + s * 0.8, 22.8, -5.8, 3.0, 3.0, 2.6), "bone", tag="femur_head")
        p = k.leg(s)
        x = s * 1.95
        a(p, C(x, 2.4, 0, 4.6, 9.6, 4.6), "mail", tag="mail")
        a(p, C(x, 7.0, 2.4, 3.2, 5.0, 0.7), "bone", tag="thigh_bone")
        a(p, C(x, 4.4, 2.5, 3.8, 2.6, 1.2), "bone", tag="kneecap")
        a(p, C(x, 1.8, 2.3, 2.0, 2.8, 0.7), "bone", tag="shin_bone")
    k.boots("bone", h=3.6, w=5.0, sole="dark", cuff="dark", toe="dark", toe_d=2.0)


@design(blade=ramp("#2a2012", "#44361e", "#62502c", "#84703e", "#a89458"), dark=BLACK, wood=ramp("#14100c", "#241c14", "#382c20", "#4e3e2c", "#6a5640"), cloth=PALE, cloth2=ramp("#2a0c14", "#441420", "#621e2e", "#842c40"), acc=ramp("#3e2206", "#6e420c", "#a8701a", "#d8a430", "#f6d468"), bone=BONE, mail=ramp("#2a2012", "#44361e", "#62503c", "#84703e"), leather=HIDE, fire=TOLL, hot=TOLL)
def pallbearer(k):
    """he carries the engine's dead: a yoke across the shoulders with the bier poles running out front and back, a white shroud thrown over them, a bronze bell for a chest"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.2, 0, 10.2, 8.8, 10.2), "blade", tag="helm")
    a(h, C(0, 22.8, 0, 11.6, 1.6, 11.6), "dark", tag="helm_rim")
    a(h, C(0, 32.0, 0, 11.4, 1.3, 11.4), "dark", tag="brow")
    a(h, C(0, 33.2, 0, 7.6, 2.4, 7.6), "blade", tag="crown")
    a(h, C(0, 25.4, 5.05, 8.0, 1.0, 0.3), "void", tag="slit")
    k.fire(h, C(0, 25.6, 5.2, 6.4, 0.6, 0.3))
    for x in (-3.4, -1.7, 0, 1.7, 3.4):
        a(h, C(x, 26.4, 5.1, 0.5, 5.4, 0.3), "void", tag="bar")
    a(h, C(0, 35.6, 0, 11.0, 0.9, 1.2), "acc", tag="pall_cross")
    a(h, C(0, 35.6, 0, 1.2, 0.9, 11.0), "acc", tag="pall_cross")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 7.0), "blade", tag="cuirass")
    a(c, C(0, 13.6, 3.6, 7.4, 9.0, 0.7), "acc", tag="bell_front")
    a(c, C(0, 13.0, 3.6, 8.4, 1.2, 1.0), "acc", tag="bell_lip")
    a(c, C(0, 15.4, 4.05, 3.4, 3.4, 0.3), "dark", tag="bell_mark")
    k.fire(c, C(0, 16.0, 4.25, 2.2, 2.2, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.6), "dark", tag="belt")
    for s in SIDES:
        a(b, C(s * 8.0, 25.6, -5.0, 1.6, 1.6, 24.0), "wood", tag="bier_pole")
        a(b, C(s * 8.0, 25.2, 7.2, 2.4, 2.4, 0.8), "acc", tag="pole_cap")
        a(b, C(s * 8.0, 25.2, -17.2, 2.4, 2.4, 0.8), "acc", tag="pole_cap")
    a(b, C(0, 26.4, -8.0, 17.6, 1.0, 14.0), "cloth", tag="shroud")
    for s in SIDES:
        a(b, C(s * 8.9, 19.6, -8.0, 0.7, 7.4, 14.0), "cloth", tag="shroud_fall")
    a(b, C(0, 27.4, -8.0, 12.0, 2.6, 11.0), "cloth", tag="shrouded_form")
    a(b, C(0, 27.4, -11.0, 7.0, 3.6, 4.0), "cloth", tag="shrouded_head")
    a(b, C(0, 13.0, -3.8, 8.0, 12.0, 1.6), "blade", tag="back_plate")
    a(b, C(0, 19.6, -8.0, 17.6, 0.5, 0.5), "cloth2", tag="shroud_tie")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 11.0, 0, 6.0, 6.0, 6.0), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.4, 1.0, 6.4), "acc", tag="cuff")
        q = k.shoulder(s)
        a(q, C(x + s * 1.0, 20.6, 0, 8.0, 3.8, 8.6), "blade", tag="pauldron")
        a(q, C(x + s * 1.0, 20.2, 0, 8.4, 0.9, 9.0), "acc", tag="pauldron_rim")
        p = k.leg(s)
        x = s * 1.95
        a(p, C(x, 2.4, 0, 5.2, 9.6, 5.2), "blade", tag="cuisse")
        a(p, C(x, 6.4, 2.6, 4.2, 5.6, 0.6), "cloth2", tag="tabard_panel")
        a(p, C(x, 4.4, 2.6, 4.0, 2.6, 1.0), "acc", tag="poleyn")
    k.boots("blade", h=4.2, w=5.4, cuff="dark", toe="dark", toe_d=3.0)
