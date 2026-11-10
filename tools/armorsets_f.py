"""The eight sets found out in the world rather than forged (see armorsets.py for the units and the fit rules)."""
from armorsets import BRASS, C, IRON, SIDES, design, ramp
from armorsets_a import BLACK, HEMP, OAK
from armorsets_b import BONE, GILT, HIDE, PALE
from armorsets_c import ICE, RIME, SEA, SNOW, STEEL

TIDE_RED = ramp("#4a0e10", "#6e1618", "#942224", "#bc3632", "#dc5a48")
RUSTED = ramp("#2a160c", "#46260f", "#663a18", "#885424", "#ac7638")
SEAGLOW = ramp("#0e5a60", "#148884", "#22b4a4", "#50dcc0", "#a0f4dc", "#e4fff4")
FADED = ramp("#2a0e0e", "#441818", "#5e2622", "#783a30", "#945444")
EMBERGLOW = ramp("#6a1c06", "#a03408", "#d85c10", "#f48c24", "#ffc060", "#fff0c0")
TOXIN = ramp("#2e6a08", "#4e9a0c", "#7cc818", "#b0ec38", "#dcfa80", "#f8ffd0")
COPPERY = ramp("#3e1c0c", "#6a3214", "#9c5022", "#c87838", "#e8a860", "#f8d09c")
SOUL = ramp("#14388a", "#2058c0", "#3c8ce8", "#74c0f8", "#b8e8ff", "#f0ffff")
GRIMBLUE = ramp("#0e1a34", "#16284c", "#22386a", "#304c8a", "#4466aa")
TARNISH = ramp("#2e3034", "#484a50", "#686a70", "#8c8e94", "#b4b6ba", "#dcdee0")
CHITIN = ramp("#0e2a14", "#16421e", "#20602a", "#308238", "#4aa84c", "#80d070")
GRAVE = ramp("#6a1e9a", "#8c32c4", "#b058e4", "#d290f4", "#ecc8fc", "#fff0ff")
NORTHERN = ramp("#10a878", "#20d090", "#60e8a0", "#a0f0c8", "#b080f0", "#e0a8ff")
BRONZE = ramp("#3a1e0a", "#5e3410", "#8a521c", "#b47830", "#d8a050", "#f0cc88")
EAGLE = ramp("#7c7468", "#9e968a", "#c0b8aa", "#dcd6ca", "#f2eee4", "#ffffff")
SKY = ramp("#7a5008", "#b47c10", "#e8ac24", "#ffd85c", "#fff09c", "#fffce0")


@design(leather=ramp("#1a1612", "#2c261e", "#403628", "#584a36"), cloth=TIDE_RED, wrap=HEMP, dark=BLACK, acc=BRASS, blade=STEEL, mail=SEA, cloth2=SEA, fire=SEAGLOW, hot=SEAGLOW)
def corsair(k):
    """off a crew that drowned: a salt-stained tricorn over a red bandana, a hook for a left hand, a cutlass and a coil of wet rope"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.0, 7.0, 9.2), "cloth", tag="bandana")
    k.tail(h, 2.0, 26.0, -5.0, 6.4, 1.4, "cloth", lean=8, tag="bandana_tail")
    a(h, C(0, 31.0, 0, 9.4, 2.2, 9.4), "leather", tag="hat_crown")
    for t in (0, 120, 240):
        a(h, C(0, 30.4, 6.2, 14.0, 3.8, 0.8), "leather", tag="hat_side", rots=(("x", -18), ("y", t)), pivot=(0, 31, 0))
    a(h, C(0, 32.4, 6.0, 2.8, 2.8, 0.5), "acc", tag="hat_badge")
    a(h, C(0, 27.4, 4.65, 7.0, 1.0, 0.3), "void", tag="shadow")
    k.fire(h, C(2.0, 27.6, 4.8, 1.2, 0.6, 0.3))
    a(h, C(-2.0, 27.0, 4.75, 2.4, 2.0, 0.4), "dark", tag="eye_patch")
    a(h, C(0, 23.6, 4.4, 5.0, 2.4, 0.8), "dark", tag="black_beard")
    a(h, C(0, 21.8, 4.4, 2.4, 2.0, 0.8), "dark", tag="black_beard")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.0), "leather", tag="sea_coat")
    a(c, C(0, 13.0, 2.65, 3.4, 11.0, 0.4), "wrap", tag="linen_shirt")
    for y in (15.0, 17.4, 19.8):
        for s in SIDES:
            a(c, C(s * 2.4, y, 2.85, 0.9, 0.9, 0.3), "acc", tag="button")
    a(c, C(0, 12.4, 0, 8.7, 2.0, 5.6), "cloth", tag="red_sash")
    a(c, C(3.2, 5.8, 3.0, 2.0, 6.8, 0.5), "cloth", tag="sash_end")
    a(c, C(-4.1, 1.0, 1.4, 1.1, 10.6, 1.4), "blade", tag="cutlass", rots=(("x", -8),), pivot=(-4.1, 12, 1.4))
    a(c, C(-4.1, 11.6, 1.4, 2.6, 2.0, 2.6), "acc", tag="cutlass_guard")
    for s in SIDES:
        a(b, C(s * 2.2, 3.0, -3.4, 3.6, 19.0, 0.7), "leather", tag="coat_tail", rots=(("x", 6), ("z", -s * 4)), pivot=(s * 2.2, 22, -3.4))
    a(b, C(0, 14.0, -4.0, 6.6, 6.6, 1.6), "wrap", tag="rope_coil")
    a(b, C(0, 15.8, -4.0, 3.2, 3.2, 1.7), "dark", tag="coil_hole")
    k.fire(b, C(0, 16.8, -4.95, 1.2, 1.2, 0.3))
    a(k.shoulder(1), C(6.2, 21.2, 0, 5.6, 2.2, 5.6), "leather", tag="cop")
    a(k.shoulder(-1), C(-6.2, 21.2, 0, 5.6, 2.2, 5.6), "leather", tag="cop")
    p, x = k.arm(1), 6.0
    a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "leather", tag="sleeve")
    k.elbow(1, "leather")
    a(p, C(x, 11.4, 0, 5.2, 5.0, 5.2), "wrap", tag="shirt_cuff")
    a(p, C(x, 16.2, 0, 5.8, 1.4, 5.8), "leather", tag="turned_cuff")
    p, x = k.arm(-1), -6.0
    a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "leather", tag="sleeve")
    k.elbow(-1, "leather")
    a(p, C(x, 13.0, 0, 5.8, 3.6, 5.8), "leather", tag="stump_socket")
    a(p, C(x, 11.6, 0, 3.8, 1.4, 3.8), "acc", tag="hook_collar")
    a(p, C(x, 8.6, 0, 1.2, 3.2, 1.2), "blade", tag="hook")
    a(p, C(x + 1.4, 7.8, 0, 3.8, 1.2, 1.2), "blade", tag="hook")
    a(p, C(x + 2.9, 8.4, 0, 1.0, 2.4, 1.0), "blade", tag="hook")
    k.legs("cloth2", w=4.6)
    k.boots("leather", h=6.0, w=5.0, cuff="leather", toe="dark", toe_d=2.2)


@design(blade=RUSTED, mail=RUSTED, cloth=FADED, leather=HIDE, wrap=HEMP, dark=BLACK, acc=IRON, wood=OAK, fire=EMBERGLOW, hot=EMBERGLOW)
def deserter(k):
    """a soldier's kit worn by the man who ran: a dented kettle hat, a tabard with the badge cut out of it, a bedroll, and a spear he snapped so nobody could make him use it"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.2, 6.0, 9.4), "mail", tag="coif")
    a(h, C(0, 29.6, 0, 15.0, 0.9, 15.0), "blade", tag="kettle_brim")
    a(h, C(0, 30.4, 0, 9.4, 3.4, 9.4), "blade", tag="kettle_bowl")
    a(h, C(0, 33.8, 0, 6.6, 1.0, 6.6), "blade", tag="kettle_top")
    a(h, C(2.4, 31.4, 4.45, 2.6, 1.8, 0.4), "dark", tag="dent")
    a(h, C(0, 22.6, 0, 10.0, 3.4, 10.0), "wrap", tag="grey_scarf")
    a(h, C(0, 27.2, 4.75, 7.0, 1.0, 0.3), "void", tag="shadow")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 27.4, 4.9, 1.0, 0.6, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "mail", tag="old_hauberk")
    a(c, C(0, 12.2, 2.75, 6.8, 11.4, 0.5), "cloth", tag="tabard")
    a(c, C(0, 16.4, 3.05, 3.4, 3.8, 0.3), "dark", tag="cut_badge")
    a(c, C(1.8, 9.0, 2.75, 3.0, 3.4, 0.5), "cloth", tag="tabard_rag")
    a(c, C(-2.2, 10.2, 2.75, 2.2, 2.2, 0.5), "cloth", tag="tabard_rag")
    a(c, C(0, 12.8, 0, 8.7, 1.3, 6.0), "wrap", tag="rope_for_belt")
    a(b, C(0, 21.0, -4.6, 9.4, 3.2, 3.2), "wrap", tag="bedroll")
    for s in SIDES:
        a(b, C(s * 3.4, 20.8, -4.6, 0.8, 3.6, 3.6), "acc", tag="bedroll_strap")
    a(b, C(0, 12.6, -4.0, 6.8, 7.8, 2.4), "cloth", tag="sack")
    a(b, C(0, 8.0, -3.4, 1.2, 18.0, 1.2), "wood", tag="snapped_spear", rots=(("z", 18),), pivot=(0, 18, -3.4))
    a(b, C(0.2, 26.0, -3.4, 0.9, 2.4, 0.9), "wood", tag="splinter", rots=(("z", 32),), pivot=(0, 26, -3.4))
    k.fire(b, C(0, 14.6, -5.3, 1.4, 1.0, 0.3))
    k.arms("mail", "wrap", cuff="dark", w=5.2)
    for s in SIDES:
        for y in (12.6, 14.6):
            a(k.arm(s), C(s * 6.0, y, 0, 5.5, 0.6, 5.5), "cloth", tag="rag_bind")
    a(k.shoulder(1), C(6.6, 20.8, 0, 6.2, 2.8, 6.4), "blade", tag="dented_pauldron")
    k.legs("cloth", w=4.6)
    for s in SIDES:
        a(k.leg(s), C(s * 1.95, 2.4, 2.3, 3.4, 3.4, 0.7), "blade", tag="greave")
        a(k.leg(s), C(s * 1.95, 6.4, 0, 5.0, 0.8, 5.0), "wrap", tag="knee_rag")
    a(k.leg(1), C(1.95, 8.0, 2.4, 2.8, 2.8, 0.4), "wrap", tag="patch")
    k.boots("leather", h=3.2, w=4.8, cuff="wrap", toe="dark", toe_d=2.0)
    a(k.boot(1), C(2.4, 0.6, 3.0, 1.8, 1.0, 1.8), "void", tag="toe_hole")


@design(cloth=ramp("#14281a", "#203c28", "#305438", "#446e4c", "#5c8c62"), leather=ramp("#2a1a10", "#442c18", "#624224", "#845c34"), acc=COPPERY, blade=COPPERY, dark=BLACK, gem=TOXIN, wrap=ramp("#6a5a44", "#8a7a60", "#ac9c80", "#ccc0a4"), wood=OAK, fire=TOXIN, hot=TOXIN)
def alchemist(k):
    """a Blightkin alchemist: thick green goggles and a leather mask, a working copper still on the back with its coil and drip, racks of flasks crossed on the chest"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.2, 8.2, 9.4), "leather", tag="mask_hood")
    a(h, C(0, 32.0, -0.2, 9.8, 0.9, 9.8), "acc", tag="head_band")
    a(h, C(0, 27.4, 4.4, 9.2, 0.9, 0.6), "dark", tag="goggle_strap")
    for s in SIDES:
        a(h, C(s * 2.3, 26.4, 4.7, 3.6, 3.4, 1.4), "acc", tag="goggle")
        k.fire(h, C(s * 2.3, 26.9, 5.45, 2.4, 2.4, 0.3))
    a(h, C(0, 23.2, 4.6, 4.6, 3.0, 2.2), "dark", tag="filter_mask")
    a(h, C(0, 23.8, 5.75, 3.2, 0.6, 0.3), "acc", tag="filter_slit")
    a(h, C(-3.4, 32.6, 2.0, 2.0, 3.2, 2.0), "gem", tag="brow_vial")
    a(h, C(-3.4, 35.8, 2.0, 1.0, 1.2, 1.0), "wood", tag="vial_cork")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 12.2, 2.75, 7.0, 10.0, 0.5), "leather", tag="stained_apron")
    a(c, C(2.0, 13.0, 3.05, 2.6, 3.8, 0.3), "gem", tag="spill")
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.8), "acc", tag="belt")
    for i in range(5):
        t = i / 4
        x, y = -3.4 + 6.8 * t, 22.0 - 6.4 * t
        a(c, C(x, y, 3.3, 1.2, 2.4, 1.0), "gem", tag="bandolier_flask")
        a(c, C(x, y + 2.4, 3.3, 0.7, 0.7, 0.7), "wood", tag="flask_cork")
    k.fire(c, C(-1.7, 21.0, 3.85, 0.7, 1.4, 0.3))
    a(b, C(0, 12.4, -5.0, 7.6, 7.4, 5.0), "acc", tag="still_pot")
    a(b, C(0, 19.8, -5.0, 5.4, 2.6, 3.8), "acc", tag="still_shoulder")
    a(b, C(0, 22.4, -5.0, 2.2, 5.6, 2.2), "acc", tag="still_neck")
    a(b, C(3.2, 27.2, -5.0, 8.0, 1.2, 1.2), "acc", tag="still_arm")
    for y in (16.0, 18.0, 20.0, 22.0, 24.0):
        a(b, C(7.0, y, -5.0, 3.4, 0.9, 3.4), "acc", tag="worm_coil")
    a(b, C(7.0, 15.0, -5.0, 1.0, 12.0, 1.0), "acc", tag="worm_stem")
    k.fire(b, C(7.0, 12.4, -5.0, 0.8, 2.6, 0.8))
    a(b, C(0, 12.8, -7.65, 3.4, 2.6, 0.4), "dark", tag="still_firebox")
    k.fire(b, C(0, 13.2, -7.9, 2.4, 1.6, 0.3))
    k.arms("cloth", "wrap", cuff="acc", w=5.6, low_h=5.0)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.3, 21.0, 0, 5.6, 2.4, 5.6), "leather", tag="cop")
    k.legs("cloth", w=4.6)
    k.boots("leather", h=3.2, w=4.8, cuff="acc", sole="dark")


@design(blade=TARNISH, dark=ramp("#06080e", "#0e1220", "#181e32", "#242c48"), cloth=GRIMBLUE, acc=TARNISH, gem=SOUL, mail=TARNISH, leather=HIDE, gold=TARNISH, wrap=GILT, fire=SOUL, hot=SOUL)
def hollow_knight(k):
    """the Fallen Order's plate, the knight inside long gone: a tall crowned helm with nothing but two cold sparks in the dark, a torn blue cape, a broken sword run through from behind"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.0, 0, 9.8, 13.0, 9.8), "blade", tag="tall_helm")
    a(h, C(0, 24.4, 4.85, 7.4, 7.6, 0.4), "void", tag="empty_visor")
    for x in (-2.6, -1.3, 0, 1.3, 2.6):
        a(h, C(x, 24.0, 5.05, 0.5, 8.4, 0.4), "dark", tag="visor_bar")
    for s in SIDES:
        a(h, C(s * 2.0, 28.0, 5.05, 1.0, 1.0, 0.3), "glow", group="fire", tag="cold_spark")
    a(h, C(0, 36.0, 0, 10.8, 1.4, 10.8), "wrap", tag="crown_band")
    for t, (x, z) in enumerate(((0, 5.0), (-4.0, 3.2), (4.0, 3.2), (-5.0, -1.0), (5.0, -1.0), (0, -5.0))):
        k.spike(h, x, 37.2, z, 4.0, 2.0, "wrap", tag="crown_point", steps=2)
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.2), "blade", tag="cuirass")
    a(c, C(0, 12.2, 3.15, 6.0, 9.4, 0.5), "cloth", tag="tabard")
    a(c, C(0, 14.0, 3.45, 0.9, 6.4, 0.3), "wrap", tag="order_mark")
    a(c, C(0, 18.0, 3.45, 4.0, 0.9, 0.3), "wrap", tag="order_mark")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 6.8), "dark", tag="belt")
    a(c, C(1.6, 19.0, 3.25, 1.4, 1.4, 0.8), "blade", tag="sword_tip")
    k.spike(c, 1.6, 19.6, 3.4, 4.0, 1.2, "blade", rx=-82, tag="sword_tip", steps=2)
    k.fire(c, C(1.6, 18.0, 3.45, 2.0, 0.5, 0.3))
    a(b, C(1.6, 19.0, -9.4, 3.0, 2.0, 12.0), "blade", tag="broken_sword")
    a(b, C(1.6, 18.6, -15.4, 6.6, 2.6, 1.2), "dark", tag="sword_guard")
    a(b, C(1.6, 19.2, -17.8, 1.4, 1.4, 3.8), "wrap", tag="sword_grip")
    for i, x in enumerate((-3.4, -1.2, 1.0, 3.4)):
        ln = (18.0, 12.0, 20.0, 15.0)[i]
        a(b, C(x, 23.0 - ln, -3.8, 2.2, ln, 0.6), "cloth", tag="torn_cape", rots=(("x", 8 + i), ("z", x)), pivot=(x, 23, -3.8))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.0, 0, 5.8, 5.8, 5.8), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.2, 1.0, 6.2), "dark", tag="cuff")
        q = k.shoulder(s)
        for i in range(3):
            a(q, C(x + s * (1.0 - i * 0.2), 20.5 + i * 1.4, 0, 8.0 - i * 1.2, 1.2, 8.0 - i), "blade" if i != 1 else "dark", tag="lame")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.0, 9.6, 5.0), "blade", tag="cuisse")
        a(p, C(y, 4.6, 2.6, 3.8, 2.8, 0.9), "dark", tag="poleyn")
    k.boots("blade", h=4.0, w=5.2, cuff="dark", toe="dark", toe_d=2.8)


@design(blade=CHITIN, gem=TOXIN, dark=ramp("#060e08", "#0e1c10", "#182c1a"), acc=ramp("#6a7a18", "#8e9e22", "#b4c030", "#d8dc54"), cloth=ramp("#0c1e10", "#142c18", "#1e3e22"), leather=ramp("#0c1e10", "#142c18", "#1e3e22"), mail=CHITIN, fire=TOXIN, hot=TOXIN)
def mantis(k):
    """a brood reaper's shell: a wedge of a head with great compound eyes and long feelers, wing cases on the back, and the true scythes folded down off the forearms"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.6, 0, 8.8, 7.4, 9.0), "blade", tag="wedge_head")
    a(h, C(0, 23.0, 4.2, 6.0, 2.6, 2.6), "blade", tag="wedge_jaw")
    a(h, C(0, 21.6, 5.0, 3.0, 2.0, 2.2), "dark", tag="mouthparts")
    for s in SIDES:
        a(h, C(s * 5.4, 27.6, 0.8, 3.4, 4.8, 5.6), "gem", tag="compound_eye")
        a(h, C(s * 6.0, 28.4, 3.65, 2.2, 3.2, 0.3), "glow", group="fire", tag="eye_shine")
        k.horn(h, s * 1.6, 31.6, 3.0, [(5.0, -s * 18, 0.7), (5.0, -s * 38, 0.6), (5.0, -s * 60, 0.5), (4.0, -s * 86, 0.4)], "acc")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.6), "blade", tag="thorax")
    for y in (14.0, 16.4, 18.8, 21.2):
        a(c, C(0, y, 3.0, 7.4 - (22 - y) * 0.3, 0.8, 0.5), "acc", tag="segment")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 6.2), "dark", tag="belt")
    k.fire(c, C(0, 16.8, 3.1, 1.0, 1.0, 0.3))
    for s in SIDES:
        a(b, C(s * 2.2, 2.0, -3.6, 4.2, 22.0, 0.7), "blade", tag="wing_case", rots=(("x", 6), ("z", -s * 2)), pivot=(s * 2.2, 24, -3.6))
        a(b, C(s * 2.2, 3.0, -4.2, 0.5, 20.0, 0.3), "acc", tag="wing_vein", rots=(("x", 6), ("z", -s * 2)), pivot=(s * 2.2, 24, -3.6))
        a(b, C(s * 3.4, 3.0, -4.2, 0.4, 16.0, 0.3), "acc", tag="wing_vein", rots=(("x", 6), ("z", -s * 2)), pivot=(s * 2.2, 24, -3.6))
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "blade", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.4, 0, 5.4, 5.8, 5.4), "blade", tag="raptor_arm")
        for y in (12.4, 14.0, 15.6):
            k.spike(p, x, y, -2.8, 2.2, 1.0, "acc", rx=118, tag="arm_barb", steps=2)
        a(p, C(x + s * 0.8, 16.6, 3.0, 2.0, 2.0, 2.0), "dark", tag="scythe_joint")
        k.horn(p, x + s * 0.8, 17.4, 3.4, [(-4.0, 0, 2.6), (-4.0, s * 8, 2.2), (-3.6, s * 22, 1.6), (-3.0, s * 40, 1.0), (-2.2, s * 62, 0.5)], "acc")
        q = k.shoulder(s)
        a(q, C(x + s * 0.4, 21.0, 0, 6.2, 2.8, 6.4), "blade", tag="shoulder_shell")
        k.spike(q, x + s * 1.8, 23.4, 0, 4.0, 2.0, "acc", rz=-s * 28, tag="shoulder_barb")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 4.6, 9.6, 4.6), "blade", tag="segment_leg")
        for yy in (4.0, 8.0):
            a(p, C(y, yy, 0, 4.9, 0.6, 4.9), "dark", tag="leg_joint")
        k.spike(p, y + s * 2.4, 4.6, 0, 3.0, 1.2, "acc", rz=-s * 72, tag="leg_barb", steps=2)
    k.boots("blade", h=3.0, w=4.8, cuff="dark", toe="acc", toe_d=3.4)


@design(blade=ramp("#08080c", "#121218", "#1e1e28", "#2e2e3a", "#444452"), dark=BLACK, acc=GILT, gold=GILT, fur=ramp("#141010", "#241c1a", "#382c28", "#4e4038", "#6a584c"), bone=BONE, mail=ramp("#08080c", "#121218", "#1e1e28", "#2e2e3a"), cloth=ramp("#1e0a2e", "#2e1244", "#441c60", "#5e2c80"), gem=GRAVE, leather=HIDE, fire=GRAVE, hot=GRAVE)
def barrow_lord(k):
    """a king who would not lie down: a skull under a green-gold crown still on its brow, a wolf-fur mantle a foot thick, the grave goods sewn to his chest and purple cold in the eye sockets"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.2, 0, 9.8, 8.8, 9.8), "bone", tag="skull")
    a(h, C(0, 22.4, 3.0, 7.0, 2.6, 3.2), "bone", tag="skull_jaw")
    for x in (-2.4, -1.2, 0, 1.2, 2.4):
        a(h, C(x, 23.4, 4.65, 0.3, 1.8, 0.3), "void", tag="teeth")
    a(h, C(0, 25.2, 4.9, 1.4, 1.6, 0.3), "void", tag="nose")
    for s in SIDES:
        a(h, C(s * 2.2, 27.2, 4.85, 2.6, 2.2, 0.3), "void", tag="socket")
        k.fire(h, C(s * 2.2, 27.8, 5.0, 1.2, 1.0, 0.3))
    a(h, C(0, 31.0, 0, 10.6, 1.6, 10.6), "acc", tag="crown_band")
    for x, z, ln in ((0, 5.2, 5.0), (-3.6, 3.8, 3.6), (3.6, 3.8, 3.6), (-5.2, -0.6, 4.0), (5.2, -0.6, 4.0), (-3.4, -4.2, 3.4), (3.4, -4.2, 3.4), (0, -5.2, 4.0)):
        k.spike(h, x, 32.4, z, ln, 2.2, "acc", tag="crown_point", steps=3)
    a(h, C(0, 31.4, 5.4, 2.0, 1.2, 0.4), "gem", tag="crown_jewel")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.2), "blade", tag="grave_plate")
    a(c, C(0, 18.6, 0, 8.7, 5.4, 7.6), "fur", tag="fur_mantle")
    for x, y, m in ((-2.8, 15.0, "acc"), (0, 13.8, "gem"), (2.8, 15.2, "acc"), (-1.4, 17.0, "bone"), (1.4, 17.2, "acc")):
        a(c, C(x, y, 3.25, 1.6, 1.6, 0.5), m, tag="grave_good")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 6.8), "acc", tag="belt")
    a(b, C(0, 2.0, -4.2, 9.6, 21.0, 1.2), "fur", tag="fur_cloak", rots=(("x", 7),), pivot=(0, 23, -4.2))
    a(b, C(0, 14.0, -5.4, 4.2, 4.6, 0.6), "cloth", tag="cloak_sigil", rots=(("x", 7),), pivot=(0, 23, -4.2))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.4, 1.0, 6.4), "acc", tag="cuff")
        for y, dx in ((11.0, 0),):
            a(p, C(x + dx, y - 1.8, 0, 3.8, 2.0, 3.8), "bone", tag="bone_hand")
        q = k.shoulder(s)
        a(q, C(x + s * 1.0, 20.4, 0, 9.0, 4.6, 9.2), "fur", tag="fur_shoulder")
        a(q, C(x + s * 1.2, 24.8, 0, 7.2, 1.8, 7.4), "fur", tag="fur_shoulder_top")
        a(q, C(x + s * 3.4, 23.6, 3.6, 3.2, 3.2, 2.4), "bone", tag="wolf_skull")
        a(q, C(x + s * 3.4, 24.8, 4.85, 2.4, 0.8, 0.3), "void", tag="wolf_eyes")
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 5.1, 9.6, 5.1), "blade", tag="cuisse")
        a(p, C(y, 6.2, 2.6, 3.8, 5.8, 0.6), "cloth", tag="tasset")
        a(p, C(y, 4.6, 2.7, 3.8, 2.6, 0.9), "acc", tag="poleyn")
    k.boots("blade", h=4.2, w=5.2, cuff="acc", toe="dark", toe_d=2.8)


@design(cloth=SNOW, wrap=ramp("#10503a", "#187a58", "#30a880", "#60cca0"), gem=ICE, acc=ICE, dark=ramp("#101820", "#1a2632", "#283a4a"), blade=ICE, leather=SNOW, cloth2=ramp("#3a2a7a", "#5240a8", "#7460cc", "#a090e8"), fire=NORTHERN, hot=RIME)
def aurora(k):
    """vestments of the cold chaplains: a crown of ice, a long white robe, and the northern lights themselves pouring off the shoulders in curtains of green and violet"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.8, -0.3, 9.4, 8.2, 9.4), "cloth", tag="hood")
    a(h, C(0, 27.0, 4.45, 7.0, 3.4, 0.4), "void", tag="hood_dark")
    for s in SIDES:
        k.fire(h, C(s * 1.8, 28.0, 4.65, 1.0, 0.7, 0.3))
    a(h, C(0, 31.4, 0, 10.4, 1.0, 10.4), "gem", tag="crown_ring")
    for x, z, ln in ((0, 5.0, 11.0), (-2.8, 4.4, 7.4), (2.8, 4.4, 7.4), (-5.2, 1.4, 9.0), (5.2, 1.4, 9.0), (-4.2, -3.2, 6.6), (4.2, -3.2, 6.6), (0, -5.0, 8.0)):
        k.spike(h, x, 32.2, z, ln, 2.2, "gem", rz=-x * 1.8, rx=-z * 0.7, tag="ice_crown", steps=4)
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 12.2, 2.75, 3.0, 11.8, 0.5), "wrap", tag="stole")
    k.fire(c, C(0, 12.6, 3.05, 1.2, 11.0, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.8), "gem", tag="ice_belt")
    a(c, C(0, 20.8, 0, 8.7, 3.2, 6.2), "cloth2", tag="mantle")
    for i, (x, ln, z) in enumerate(((-9.0, 16.0, -3.0), (-6.6, 21.0, -3.4), (-4.2, 24.0, -3.8), (-1.8, 22.0, -4.2), (0.6, 25.0, -4.4), (3.0, 21.0, -4.0), (5.4, 24.0, -3.6), (7.8, 19.0, -3.2), (9.8, 14.0, -2.8))):
        a(b, C(x, 23.6 - ln, z, 2.4, ln, 0.4), "glow", group="fire", tag="aurora_curtain", rots=(("x", 6 + (i % 3) * 2),), pivot=(x, 23.6, z))
    a(b, C(0, 21.6, -3.2, 19.0, 2.4, 1.0), "gem", tag="curtain_rail")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "cloth", tag="sleeve")
        k.elbow(s, "cloth")
        a(p, C(x, 10.8, 0, 6.2, 5.8, 6.2), "cloth", tag="flare")
        k.fire(p, C(x, 10.8, 0, 6.5, 0.8, 6.5))
        q = k.shoulder(s)
        a(q, C(x + s * 0.3, 21.0, 0, 5.8, 2.6, 5.8), "cloth2", tag="mantle")
        k.spike(q, x + s * 1.6, 23.4, 0, 5.0, 2.2, "gem", rz=-s * 20, tag="ice_shoulder")
    k.legs("cloth", w=4.6)
    k.boots("gem", h=2.6, w=4.8, sole="dark")


@design(blade=BRONZE, feather=EAGLE, acc=GILT, gold=GILT, cloth=SNOW, wrap=ramp("#2a1408", "#46240e", "#66381a", "#885228"), dark=BLACK, mail=BRONZE, wood=OAK, leather=ramp("#2a1408", "#46240e", "#66381a", "#885228"), fire=SKY, hot=SKY)
def gryphon_rider(k):
    """the Sky Legion's riding armour: an eagle's head helm with the beak for a visor, bronze scaled over white, real gryphon wings spread on the shoulders, a lance strapped behind"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.8, 8.4, 10.0), "feather", tag="eagle_head")
    a(h, C(0, 28.0, 5.0, 4.4, 3.0, 2.0), "acc", tag="beak_root")
    a(h, C(0, 26.6, 6.6, 3.4, 3.0, 2.2), "acc", tag="beak")
    a(h, C(0, 25.2, 7.6, 2.4, 2.6, 1.8), "acc", tag="beak_hook")
    a(h, C(0, 24.4, 8.2, 1.2, 1.6, 1.0), "acc", tag="beak_tip")
    a(h, C(0, 24.4, 5.1, 7.8, 1.6, 0.4), "void", tag="under_beak")
    for s in SIDES:
        k.fire(h, C(s * 3.2, 28.6, 4.95, 1.4, 1.0, 0.3))
        for i, (t, ln) in enumerate(((4, 9.0), (24, 8.0), (44, 7.0))):
            a(h, C(s * 4.4, 30.4, -1.0 - i * 1.0, 0.8, ln, 2.4), "feather", tag="crest_feather", rots=(("x", 44), ("z", -s * t)), pivot=(s * 4.4, 30.4, -1))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.0), "blade", tag="bronze_cuirass")
    a(c, C(0, 13.0, 3.05, 6.0, 8.6, 0.5), "cloth", tag="white_tabard")
    a(c, C(0, 15.2, 3.35, 3.4, 3.4, 0.4), "acc", tag="sky_sun")
    k.fire(c, C(0, 15.8, 3.6, 2.0, 2.0, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 6.6), "leather", tag="riding_belt")
    for r in (30, -30):
        a(c, C(0, 12.8, 3.4, 1.1, 11.0, 0.4), "leather", tag="harness", rots=(("z", r),), pivot=(0, 18, 3.4))
    a(b, C(0, 13.0, -3.6, 7.4, 10.0, 1.2), "blade", tag="back_plate")
    a(b, C(3.6, -2.0, -4.8, 1.2, 46.0, 1.2), "wood", tag="lance", rots=(("z", -12),), pivot=(3.6, 18, -4.8))
    a(b, C(8.6, 40.0, -4.8, 1.8, 5.0, 1.8), "acc", tag="lance_head")
    k.spike(b, 8.6, 45.0, -4.8, 5.0, 1.8, "acc", rz=-12, tag="lance_tip")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "cloth", tag="sleeve")
        k.elbow(s, "wrap")
        a(p, C(x, 11.0, 0, 5.8, 5.8, 5.8), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.2, 1.0, 6.2), "acc", tag="cuff")
        q = k.shoulder(s)
        a(q, C(x + s * 0.8, 20.5, 0, 7.2, 3.2, 7.4), "blade", tag="pauldron")
        a(q, C(x + s * 0.8, 23.6, 0, 5.6, 0.9, 5.8), "acc", tag="pauldron_top")
        for i, (t, ln, w) in enumerate(((8, 15.0, 3.0), (24, 19.0, 3.2), (40, 21.0, 3.2), (56, 21.0, 3.2), (72, 19.0, 3.0), (88, 16.0, 2.8), (104, 12.0, 2.4))):
            a(q, C(x + s * 2.0, 23.0, -2.6 - i * 0.25, w, ln, 0.7), "feather", tag="gryphon_wing", rots=(("z", -s * t),), pivot=(x + s * 2.0, 23, -2.6))
        p, y = k.leg(s), s * 1.95
        a(p, C(y, 2.4, 0, 4.9, 9.6, 4.9), "cloth", tag="riding_leg")
        a(p, C(y, 7.0, 2.5, 3.8, 5.0, 0.6), "blade", tag="tasset")
        a(p, C(y, 2.4, 2.4, 3.4, 3.2, 0.7), "blade", tag="greave")
    k.boots("leather", h=5.4, w=5.0, cuff="acc", toe="blade", toe_d=2.2)
