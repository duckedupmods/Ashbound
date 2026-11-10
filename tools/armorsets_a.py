"""The first gates' armour, each set its own idea (see armorsets.py for the units and the fit rules): the Drowned Cellar,
Gallows Hill, the Rotwood."""
from armorsets import BRASS, C, IRON, SIDES, design, ramp

BLACK = ramp("#08070a", "#121016", "#1e1a22", "#2c2730", "#3e3844")
OAK = ramp("#24130a", "#3e2412", "#5c381c", "#7c5028", "#a07038", "#c4944e")
HEMP = ramp("#3a2c18", "#5a4628", "#7c663c", "#a08c56", "#c4b478")
UNDERTOW = ramp("#0a4a4a", "#107a70", "#22a890", "#4cd4b0", "#9cf0d0", "#e2fff0")
WINELIGHT = ramp("#4a0620", "#7a0c34", "#b01c4a", "#e03a64", "#ff7a90", "#ffd0d4")
LANTERN = ramp("#6a2c08", "#a84e0c", "#dc7c18", "#f4ac34", "#ffd86c", "#fff4c0")
SPORE = ramp("#2a5a10", "#4a8c18", "#7cc024", "#b4e03c", "#e0f47c", "#f8ffd0")
AMBER = ramp("#7a2c04", "#b44c08", "#e47c10", "#fcae24", "#ffdc68", "#fff6c4")


# ---------------------------------------------------------------- the Drowned Cellar

@design(cloth=ramp("#22060e", "#3e0c1a", "#5e1428", "#80203a", "#a43450", "#c85470"), wrap=ramp("#3a1a22", "#5c2e36", "#84504e", "#ac7a6c", "#d0ac94"),
        leather=ramp("#1c100a", "#2e1c12", "#44301e", "#5e452c"), wood=OAK, blade=ramp("#10282a", "#1c4242", "#2c6660", "#4a9484", "#86c8ac", "#d0f0dc"),
        dark=BLACK, acc=BRASS, fire=WINELIGHT, hot=WINELIGHT)
def vintner(k):
    """the cellar's master: a broad vintner's hat stained with years of pressing, a crate of the good bottles on his back, a tasting cup at the belt"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.4, 9.2, 7.0, 9.2), "cloth", tag="coif")
    a(h, C(0, 30.4, 0, 16.0, 0.9, 16.0), "wrap", tag="brim")
    a(h, C(0, 30.0, 0, 13.0, 0.5, 13.0), "cloth", tag="brim_under")
    a(h, C(0, 31.2, 0, 9.0, 4.2, 9.0), "wrap", tag="crown")
    a(h, C(0, 31.2, 0, 9.3, 1.3, 9.3), "cloth", tag="hatband")
    a(h, C(0, 35.3, 0, 7.4, 0.7, 7.4), "wrap", tag="crown_top")
    k.fire(h, C(3.2, 31.5, 4.75, 1.8, 0.8, 0.3))
    for x, dz in ((-6.8, 0), (6.8, 2)):
        k.fire(h, C(x, 29.4 - abs(dz) * 0.3, dz, 0.6, 1.0, 0.6))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 12.2, 2.8, 7.4, 9.6, 0.6), "wrap", tag="press_apron")
    k.fire(c, C(-1.6, 12.6, 3.15, 2.8, 4.4, 0.3))
    a(c, C(0, 12.4, 0, 8.7, 1.5, 5.8), "leather", tag="sash")
    a(c, C(0, 21.6, 0, 8.7, 2.6, 6.0), "cloth", tag="mantle")
    a(c, C(3.0, 11.2, 3.4, 1.8, 1.4, 1.8), "acc", tag="tastevin")
    a(c, C(3.0, 12.6, 3.4, 0.4, 1.2, 0.4), "acc", tag="tastevin_chain")
    a(b, C(0, 12.6, -4.8, 8.6, 8.4, 4.4), "wood", tag="crate")
    for y in (12.6, 20.2):
        a(b, C(0, y, -4.8, 8.9, 0.9, 4.7), "dark", tag="crate_band")
    for x, t in ((-2.8, 2.0), (-0.9, 3.4), (1.0, 2.4), (2.9, 3.0)):
        a(b, C(x, 21.0, -4.8, 1.6, t, 1.6), "blade", tag="bottle")
        a(b, C(x, 21.0 + t, -4.8, 0.8, 1.6, 0.8), "blade", tag="bottle_neck")
        a(b, C(x, 22.6 + t, -4.8, 1.0, 0.6, 1.0), "wood", tag="cork")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "cloth", tag="sleeve")
        k.elbow(s, "cloth")
        a(p, C(x, 11.6, 0, 5.2, 5.4, 5.2), "wrap", tag="rolled_sleeve")
        a(p, C(x, 16.4, 0, 5.7, 1.2, 5.7), "cloth", tag="roll")
        a(k.shoulder(s), C(x + s * 0.3, 21.2, 0, 5.6, 2.6, 5.6), "cloth", tag="cape_shoulder")
    k.legs("cloth", w=4.6)
    k.boots("leather", h=2.8, w=4.8)


@design(leather=ramp("#2a1408", "#44240e", "#623818", "#865426", "#a87438", "#d0a05c"), wood=ramp("#5a3c20", "#7c5830", "#a07c48", "#c4a468", "#e4cc94"),
        cloth=ramp("#2a2420", "#403630", "#5a4e44", "#786a5c"), dark=ramp("#100a08", "#1e1612", "#2e241c", "#42362a"), blade=IRON, acc=BRASS,
        fire=UNDERTOW, hot=UNDERTOW)
def corkrunner(k):
    """the cellar's fetch-and-carry: armoured in cork bungs, a keg on his back with the tap still dripping, a sling of corks across the chest"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.4, -0.2, 9.0, 7.4, 9.2), "leather", tag="cap")
    a(h, C(0, 31.6, 0, 9.4, 1.0, 9.4), "wood", tag="cork_brow")
    a(h, C(0, 32.6, 0, 6.0, 2.0, 6.0), "wood", tag="bung")
    a(h, C(0, 34.4, 0, 6.6, 0.6, 6.6), "dark", tag="bung_top")
    a(h, C(0, 22.6, 0.2, 9.8, 3.4, 9.8), "cloth", tag="muffler")
    for s in SIDES:
        a(h, C(s * 2.3, 27.6, 4.6, 3.2, 3.0, 1.0), "dark", tag="lens_rim")
        k.fire(h, C(s * 2.3, 28.0, 5.15, 2.2, 2.2, 0.3))
        a(h, C(s * 5.0, 26.0, 1.0, 0.8, 4.4, 4.0), "wood", tag="ear_cork")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.0), "leather", tag="jerkin")
    for y in (14.4, 17.8, 21.2):
        for x in (-3.0, 0, 3.0):
            a(c, C(x + (0.8 if y == 17.8 else 0), y - 1.2, 2.8, 2.6, 2.6, 0.7), "wood", tag="cork_scale")
    for i in range(6):
        t = i / 5
        a(c, C(-3.6 + 7.2 * t, 23.0 - 9.0 * t - 0.5, 3.4, 1.0, 1.4, 0.8), "wood", tag="sling_cork", rots=(("z", 90),), pivot=(-3.6 + 7.2 * t, 23.0 - 9.0 * t, 3.4))
    a(c, C(0, 12.2, 0, 8.7, 1.4, 5.6), "dark", tag="belt")
    a(b, C(0, 12.4, -5.4, 6.8, 9.6, 5.4), "wood", tag="keg")
    a(b, C(0, 13.6, -5.4, 7.6, 7.2, 6.2), "wood", tag="keg_belly")
    for y in (13.6, 16.8, 20.0):
        a(b, C(0, y, -5.4, 7.9, 0.9, 6.5), "acc", tag="keg_hoop")
    a(b, C(0, 15.2, -8.9, 1.0, 1.0, 1.6), "acc", tag="tap")
    a(b, C(0, 15.4, -9.8, 1.8, 0.6, 0.6), "acc", tag="tap_turn")
    k.fire(b, C(0, 13.2, -9.2, 0.6, 2.0, 0.6))
    k.arms("leather", "cloth", cuff="wood", w=5.0, low_h=4.6)
    for s in SIDES:
        x = s * 6.0
        a(k.arm(s), C(x, 12.0, 0, 5.3, 1.0, 5.3), "wood", tag="cork_cuff")
        a(k.shoulder(s), C(x + s * 0.5, 21.4, 0, 5.8, 2.4, 5.8), "wood", tag="cork_cop")
        a(k.shoulder(s), C(x + s * 0.5, 23.4, 0, 3.4, 1.0, 3.4), "dark", tag="cork_cop_top")
        a(k.leg(s), C(s * 1.95, 2.8, 2.2, 3.2, 3.0, 1.0), "wood", tag="shin_cork")
    k.legs("leather", w=4.6)
    k.boots("leather", h=4.2, w=4.8, cuff="wood")


@design(wood=OAK, blade=ramp("#14181a", "#262e30", "#3e484a", "#5a6668", "#7e8c8e", "#b0bebe"), dark=BLACK, leather=ramp("#2a1408", "#44240e", "#623818", "#865426"),
        mail=ramp("#14181a", "#262e30", "#3e484a", "#5a6668", "#7e8c8e"), acc=BRASS, cloth=ramp("#2a2420", "#403630", "#5a4e44", "#786a5c"), fire=UNDERTOW, hot=UNDERTOW)
def cooper(k):
    """the barrelmaker in his own work: a stave barrel for a breastplate, a half cask for a helm, hoops on the shoulders and a mallet on the back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.6, 0, 10.2, 8.6, 10.2), "wood", tag="cask")
    a(h, C(0, 26.6, 0, 11.0, 3.4, 11.0), "wood", tag="cask_belly")
    for y in (24.2, 31.2):
        a(h, C(0, y, 0, 10.7, 1.0, 10.7), "blade", tag="cask_hoop")
    a(h, C(0, 26.4, 0, 11.3, 0.8, 11.3), "blade", tag="cask_hoop")
    a(h, C(0, 32.2, 0, 8.8, 0.7, 8.8), "wood", tag="cask_lid")
    a(h, C(0, 27.6, 5.5, 8.0, 1.5, 0.3), "void", tag="slit")
    k.fire(h, C(0, 27.9, 5.65, 6.0, 0.8, 0.3))
    a(h, C(0, 32.9, 0, 1.8, 1.6, 1.8), "wood", tag="bung")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.6), "wood", tag="barrel")
    for y in (13.0, 20.8):
        a(c, C(0, y, 0, 8.7, 1.1, 7.0), "blade", tag="hoop")
    a(c, C(0, 16.6, 0, 8.7, 1.4, 7.4), "blade", tag="hoop")
    for x in (-3.0, -1.0, 1.0, 3.0):
        a(c, C(x, 14.2, 3.45, 0.3, 8.4, 0.3), "dark", tag="stave_line")
    k.rivets(c, [(-2.4, 17.2), (2.4, 17.2), (-2.4, 21.2), (2.4, 21.2)], 3.6, mat="acc")
    a(b, C(0, 12.0, -4.0, 1.4, 12.0, 1.4), "wood", tag="haft", rots=(("z", 24),), pivot=(0, 18, -4.0))
    a(b, C(0, 23.6, -4.0, 8.0, 4.6, 4.6), "wood", tag="mallet", rots=(("z", 24),), pivot=(0, 18, -4.0))
    for dx in (-3.2, 3.2):
        a(b, C(dx, 23.5, -4.0, 0.9, 4.8, 4.8), "blade", tag="mallet_hoop", rots=(("z", 24),), pivot=(0, 18, -4.0))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 11.4, 0, 5.4, 5.6, 5.4), "wood", tag="stave_bracer")
        for y in (12.2, 15.4):
            a(p, C(x, y, 0, 5.8, 0.8, 5.8), "blade", tag="hoop")
        q = k.shoulder(s)
        for i, (ww, hh) in enumerate(((7.4, 0.9), (6.2, 0.9), (4.8, 0.9))):
            a(q, C(x + s * 0.8, 20.8 + i * 1.5, 0, ww, hh, ww + 0.6), "blade", tag="shoulder_hoop")
        a(q, C(x + s * 0.8, 21.4, 0, 5.0, 2.8, 5.4), "wood", tag="shoulder_stave")
        p = k.leg(s)
        x = s * 1.95
        a(p, C(x, 2.4, 0, 4.6, 9.6, 4.6), "mail", tag="mail")
        a(p, C(x, 6.8, 0, 5.1, 5.2, 5.1), "wood", tag="half_stave")
        a(p, C(x, 7.0, 0, 5.4, 0.8, 5.4), "blade", tag="hoop")
    k.boots("leather", h=3.6, cuff="blade", toe="blade", toe_d=2.4)


@design(blade=ramp("#2e1a08", "#54320e", "#845418", "#b47c24", "#dcac3c", "#f6dc80"), dark=ramp("#0e1416", "#1a2426", "#2a383a", "#3e5052"),
        leather=ramp("#10201e", "#1c3430", "#2c4c46", "#40665c", "#5a8474"), cloth=ramp("#141c1c", "#202e2e", "#304444", "#445c5a"), acc=IRON,
        wood=OAK, fire=UNDERTOW, hot=UNDERTOW)
def bilgewader(k):
    """an old diver who walks the flooded vaults: a brass bell helm with lit ports, oilskin waders to the chest, an air tank, a lead weight on a chain"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 22.6, 0, 11.6, 10.4, 11.6), "blade", tag="bell")
    a(h, C(0, 24.4, 0, 12.6, 6.8, 12.6), "blade", tag="bell_belly")
    a(h, C(0, 33.0, 0, 8.4, 1.3, 8.4), "blade", tag="bell_top")
    a(h, C(0, 34.2, 0, 3.0, 1.6, 3.0), "dark", tag="valve")
    a(h, C(0, 22.0, 0, 13.0, 1.5, 13.0), "dark", tag="bell_collar")
    a(h, C(0, 25.6, 6.3, 6.4, 6.4, 0.8), "dark", tag="port_rim")
    k.fire(h, C(0, 26.4, 6.75, 4.8, 4.8, 0.3))
    for x in (-1.2, 1.2):
        a(h, C(x, 26.2, 6.95, 0.5, 5.2, 0.3), "void", tag="grille")
    a(h, C(0, 28.4, 6.95, 5.2, 0.5, 0.3), "void", tag="grille")
    for s in SIDES:
        a(h, C(s * 6.3, 26.6, 0, 0.8, 4.4, 4.4), "dark", tag="side_port_rim")
        k.fire(h, C(s * 6.75, 27.3, 0, 0.3, 3.0, 3.0))
    k.rivets(h, [(-5.2, 23.0), (-2.6, 23.0), (0, 23.0), (2.6, 23.0), (5.2, 23.0)], 6.3)
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.2), "leather", tag="oilskin")
    a(c, C(0, 20.8, 0, 8.7, 3.2, 7.0), "blade", tag="breastplate")
    k.rivets(c, [(x, 22.6) for x in (-3.2, -1.1, 1.1, 3.2)], 3.6)
    a(c, C(0, 12.2, 0, 8.7, 1.6, 7.0), "dark", tag="belt")
    for s in SIDES:
        a(c, C(s * 2.6, 13.8, 3.2, 1.2, 7.0, 0.5), "dark", tag="brace")
    a(b, C(0, 12.8, -5.4, 7.4, 11.2, 4.6), "blade", tag="tank")
    a(b, C(0, 24.0, -5.4, 5.4, 1.2, 3.2), "blade", tag="tank_shoulder")
    for y in (14.2, 21.4):
        a(b, C(0, y, -5.4, 7.8, 0.9, 5.0), "dark", tag="tank_band")
    a(b, C(0, 17.0, -7.9, 3.0, 3.0, 0.5), "dark", tag="gauge")
    k.fire(b, C(0, 17.6, -8.2, 1.8, 1.8, 0.3))
    a(b, C(0, 25.2, -5.4, 1.4, 3.4, 1.4), "dark", tag="hose")
    a(b, C(0, 27.8, -3.4, 1.4, 1.4, 4.2), "dark", tag="hose")
    k.tail(c, 3.4, 12.2, 3.5, 5.4, 0.5, "acc", tag="chain")
    a(c, C(3.4, 5.2, 3.5, 2.8, 2.0, 2.2), "acc", tag="lead_weight")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.4, 3.4, 5.4), "leather", tag="sleeve")
        k.elbow(s, "leather")
        a(p, C(x, 11.2, 0, 6.2, 4.8, 6.2), "blade", tag="cuff_glove")
        a(p, C(x, 15.8, 0, 5.4, 1.4, 5.4), "dark", tag="cuff_seal")
        q = k.shoulder(s)
        a(q, C(x + s * 0.4, 20.9, 0, 6.8, 3.2, 6.8), "blade", tag="shoulder_dome")
        a(q, C(x + s * 0.4, 20.5, 0, 7.2, 0.9, 7.2), "dark", tag="shoulder_flange")
        p = k.leg(s)
        x = s * 1.95
        a(p, C(x, 2.0, 0, 5.1, 10.0, 5.1), "leather", tag="wader")
        a(p, C(x, 4.8, 2.6, 3.4, 3.2, 0.8), "blade", tag="knee_cap")
        p = k.boot(s)
        a(p, C(x, 0, 0.4, 6.0, 3.4, 7.0), "blade", tag="lead_boot")
        a(p, C(x, 0, 0.5, 6.4, 1.1, 7.6), "dark", tag="sole")
        a(p, C(x, 3.2, 0, 5.8, 0.9, 5.8), "dark", tag="cuff")


# ---------------------------------------------------------------- Gallows Hill

@design(cloth=ramp("#0c0a0c", "#181418", "#262028", "#382e38", "#4c3f4a"), cloth2=ramp("#120c10", "#1e1620", "#2e2230", "#423242", "#5a4656"),
        blade=ramp("#040304", "#0c0a0c", "#1a1618", "#34302e", "#6a6460", "#b8b0a8"), dark=BLACK, wrap=HEMP, leather=ramp("#1c120e", "#2e1e16", "#463022", "#604430"),
        bone=ramp("#6a5c44", "#8e7e60", "#b4a484", "#d4c8ac", "#ece4d0"), acc=ramp("#3a1a08", "#6e3a10", "#a8641a", "#d89628"), feather=BLACK, fire=LANTERN, hot=LANTERN)
def tarwitch(k):
    """she boils the tar for the gibbets: a bent witch's hat dripping black, the tar still running down her shoulders, a noose for a belt, a poppet on a string"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.2, -0.4, 9.2, 7.0, 9.0), "cloth", tag="hood")
    a(h, C(0, 30.6, 0, 15.0, 0.8, 15.0), "cloth2", tag="brim")
    a(h, C(0, 30.0, 0, 11.0, 0.7, 11.0), "blade", tag="brim_tar")
    k.horn(h, 0, 31.2, -0.6, [(3.4, 0, 8.0), (3.4, 10, 6.0), (3.4, 26, 4.2), (2.8, 54, 2.6), (2.2, 82, 1.4)], "cloth2")
    a(h, C(0, 31.3, -0.6, 8.3, 1.2, 8.3), "wrap", tag="hat_cord")
    for x, ln in ((-6.2, 2.4), (-3.0, 3.6), (4.4, 2.8), (6.6, 1.8)):
        a(h, C(x, 30.2 - ln, 4.8, 0.7, ln + 1.6, 0.7), "blade", tag="tar_drip")
        a(h, C(x, 30.2 - ln - 0.6, 4.8, 1.0, 0.7, 1.0), "blade", tag="tar_bead")
    k.fire(h, C(0, 27.4, 4.55, 5.0, 0.8, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 20.6, 0, 8.7, 3.4, 6.2), "blade", tag="tar_yoke")
    for x, ln in ((-3.4, 5.0), (-1.4, 3.0), (0.8, 6.2), (3.2, 2.6)):
        a(c, C(x, 20.8 - ln, 3.05, 1.2, ln, 0.4), "blade", tag="tar_run")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 6.0), "wrap", tag="noose_belt")
    a(c, C(2.6, 7.0, 3.3, 1.2, 5.4, 1.2), "wrap", tag="noose_end")
    a(c, C(2.6, 6.0, 3.3, 2.2, 1.6, 2.2), "wrap", tag="noose_knot")
    k.tail(c, -3.2, 12.2, 3.4, 2.0, 0.3, "wrap", tag="poppet_string")
    a(c, C(-3.2, 7.2, 3.4, 2.2, 3.2, 1.2), "bone", tag="poppet")
    k.fire(c, C(-3.2, 9.0, 4.05, 1.2, 0.6, 0.3))
    a(b, C(0, 20.6, -3.8, 8.0, 3.0, 2.0), "cloth2", tag="crow_mantle")
    for i, x in enumerate((-3.4, -1.1, 1.1, 3.4)):
        a(b, C(x, 8.0 + i % 2 * 1.4, -4.1, 2.2, 12.6, 0.8), "feather", tag="tar_feather", rots=(("x", 7),), pivot=(x, 20.6, -4.1))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "cloth", tag="sleeve")
        k.elbow(s, "cloth")
        a(p, C(x, 11.0, 0, 6.2, 5.0, 6.2), "cloth2", tag="flare")
        a(p, C(x, 11.0, 0, 6.5, 1.0, 6.5), "blade", tag="flare_tar")
        q = k.shoulder(s)
        a(q, C(x + s * 0.4, 20.8, 0, 6.2, 3.0, 6.2), "blade", tag="tar_cop")
        a(q, C(x + s * 2.9, 19.0, 1.4, 0.8, 1.9, 0.8), "blade", tag="tar_drip")
    k.legs("cloth2", w=4.6)
    k.boots("leather", h=2.6, w=4.8, toe="dark", toe_d=2.6)


@design(blade=ramp("#1e1612", "#3a2a22", "#5a4436", "#7c604c", "#a68870", "#d0b8a0"), dark=BLACK, leather=ramp("#20140e", "#342218", "#4c3424", "#684a32", "#886446"),
        cloth=ramp("#141210", "#22201c", "#34302a", "#4a443c"), wrap=HEMP, mail=ramp("#1e1612", "#3a2a22", "#5a4436", "#7c604c"), acc=IRON, fire=LANTERN, hot=LANTERN)
def gibbet(k):
    """cut down from the cage and still wearing it: rusted gibbet bars round the head, a broken shackle on each wrist, the rope never taken off"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.4, 8.8, 7.8, 8.8), "cloth", tag="hood")
    a(h, C(0, 22.8, 0, 12.4, 1.1, 12.4), "blade", tag="cage_foot")
    a(h, C(0, 27.6, 0, 12.4, 0.8, 12.4), "blade", tag="cage_hoop")
    a(h, C(0, 33.6, 0, 12.4, 1.0, 12.4), "blade", tag="cage_top")
    for s in SIDES:
        for t in (-5.8, -2.0, 2.0, 5.8):
            a(h, C(s * 5.8, 23.8, t, 0.8, 9.8, 0.8), "blade", tag="bar")
            a(h, C(t, 23.8, s * 5.8, 0.8, 9.8, 0.8), "blade", tag="bar")
    a(h, C(0, 34.4, 0, 1.0, 2.6, 12.0), "blade", tag="arch")
    a(h, C(0, 34.4, 0, 12.0, 2.6, 1.0), "blade", tag="arch")
    a(h, C(0, 36.8, 0, 2.6, 1.0, 2.6), "dark", tag="hook_ring")
    a(h, C(0, 37.6, 0, 1.0, 2.2, 1.0), "dark", tag="hook")
    for s in SIDES:
        k.fire(h, C(s * 1.9, 28.4, 4.45, 1.2, 0.9, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.0), "cloth", tag="shirt")
    a(c, C(0, 14.2, 0, 8.7, 8.6, 5.6), "leather", tag="jerkin")
    for y in (15.6, 17.6, 19.6):
        a(c, C(0, y, 2.95, 1.0, 0.6, 0.5), "wrap", tag="lacing")
    a(c, C(0, 22.4, 0, 8.7, 1.7, 6.4), "wrap", tag="noose")
    a(c, C(-1.6, 19.2, 3.3, 1.6, 2.6, 1.3), "wrap", tag="noose_knot")
    k.tail(c, -1.6, 19.4, 3.4, 8.6, 0.9, "wrap", tag="rope_end")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 5.8), "dark", tag="belt")
    a(b, C(0, 13.0, -3.4, 7.0, 0.8, 1.2), "blade", tag="back_bar")
    for x in (-2.8, 2.8):
        a(b, C(x, 13.0, -3.4, 0.8, 10.0, 0.8), "blade", tag="back_bar")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "leather", tag="sleeve")
        k.elbow(s, "cloth")
        a(p, C(x, 11.6, 0, 5.0, 5.6, 5.0), "cloth", tag="wraps")
        a(p, C(x, 12.4, 0, 5.9, 2.0, 5.9), "blade", tag="shackle")
        k.tail(p, x + s * 2.9, 12.8, 0, 6.0, 0.6, "acc", tag="chain")
        a(p, C(x + s * 2.9, 5.8, 0, 1.4, 1.4, 0.6), "acc", tag="broken_link")
    a(k.shoulder(1), C(6.4, 20.9, 0, 6.2, 2.8, 6.2), "blade", tag="cage_shoulder")
    a(k.shoulder(1), C(6.4, 23.3, 0, 4.4, 0.8, 4.4), "dark", tag="cage_shoulder_top")
    k.legs("leather", w=4.6)
    for s in SIDES:
        a(k.leg(s), C(s * 1.95, 5.6, 0, 5.1, 0.8, 5.1), "wrap", tag="rope_tie")
    k.boots("leather", h=3.4, w=4.8, cuff="wrap")


@design(cloth=ramp("#0a0808", "#141010", "#201a1a", "#2e2626", "#40363a"), leather=ramp("#2a0e0a", "#441a10", "#642a18", "#864022", "#a85c30"),
        blade=ramp("#14161a", "#262a30", "#3e4450", "#5e6674", "#8a94a4", "#c8d4e0"), dark=BLACK, wood=OAK, mail=ramp("#14161a", "#262a30", "#3e4450", "#5e6674"), acc=BRASS,
        hide2=ramp("#3e0a0a", "#5e1010", "#841a1a", "#a82a24"), fire=ramp("#5a0808", "#8c0e0e", "#c01a14", "#e83c24", "#ff7c50", "#ffc8a0"))
def headsman(k):
    """the hill's executioner: a black pointed hood with eyes cut in it, a butcher's apron, and the great axe across his back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 22.6, 0, 10.0, 8.6, 10.0), "cloth", tag="hood")
    a(h, C(0, 31.2, -0.4, 8.4, 2.0, 8.4), "cloth", tag="hood_top")
    k.horn(h, 0, 33.2, -0.6, [(2.2, 0, 6.2), (2.2, 8, 4.2), (2.0, 16, 2.4)], "cloth")
    a(h, C(0, 22.0, 0, 11.6, 3.0, 11.6), "cloth", tag="hood_cape")
    for s in SIDES:
        a(h, C(s * 2.4, 27.6, 5.05, 2.4, 1.4, 0.3), "void", tag="eye_hole")
        k.fire(h, C(s * 2.4, 27.9, 5.15, 1.2, 0.7, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.0), "leather", tag="harness")
    a(c, C(0, 12.2, 2.7, 7.6, 10.8, 0.6), "cloth", tag="apron")
    a(c, C(-1.2, 13.2, 3.05, 3.0, 5.6, 0.3), "hide2", tag="blood")
    a(c, C(1.8, 16.8, 3.05, 2.2, 3.0, 0.3), "hide2", tag="blood")
    a(c, C(0, 12.2, 0, 8.7, 1.6, 6.0), "dark", tag="belt")
    a(c, C(0, 11.8, 3.2, 2.8, 2.4, 0.6), "acc", tag="buckle")
    a(b, C(0, 8.0, -3.6, 1.5, 24.0, 1.5), "wood", tag="haft", rots=(("z", -38),), pivot=(0, 18, -3.6))
    a(b, C(3.0, 27.0, -3.6, 6.0, 5.0, 0.9), "blade", tag="axe_head", rots=(("z", -38),), pivot=(0, 18, -3.6))
    a(b, C(7.4, 24.4, -3.6, 3.4, 10.0, 0.9), "blade", tag="axe_head", rots=(("z", -38),), pivot=(0, 18, -3.6))
    a(b, C(9.6, 22.4, -3.6, 1.6, 14.0, 0.7), "blade", tag="axe_edge", rots=(("z", -38),), pivot=(0, 18, -3.6))
    a(b, C(10.5, 23.0, -3.6, 0.6, 12.6, 0.5), "hide2", tag="axe_blood", rots=(("z", -38),), pivot=(0, 18, -3.6))
    k.fire(b, C(3.6, 27.4, -4.1, 2.0, 2.0, 0.3), rots=(("z", -38),), pivot=(0, 18, -3.6))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "leather", tag="sleeve")
        k.elbow(s, "leather")
        a(p, C(x, 11.2, 0, 5.6, 5.4, 5.6), "leather", tag="gauntlet")
        a(p, C(x, 16.0, 0, 6.2, 1.4, 6.2), "dark", tag="gauntlet_flare")
        a(p, C(x, 12.8, 2.9, 3.4, 2.0, 0.5), "hide2", tag="blood")
        p = k.leg(s)
        x = s * 1.95
        a(p, C(x, 2.4, 0, 4.6, 9.6, 4.6), "cloth", tag="leg")
        a(p, C(x, 6.2, 2.5, 3.8, 5.8, 0.6), "cloth", tag="apron_panel")
        a(p, C(x, 8.6, 2.85, 2.8, 2.6, 0.3), "hide2", tag="blood")
    a(k.shoulder(-1), C(-6.4, 21.0, 0, 6.0, 2.8, 6.0), "blade", tag="cop")
    a(k.shoulder(-1), C(-6.4, 20.6, 0, 6.4, 0.8, 6.4), "dark", tag="cop_edge")
    k.boots("leather", h=3.6, cuff="dark", toe="dark", toe_d=2.2)


@design(blade=ramp("#16181a", "#282c30", "#404650", "#5c6470", "#808a96", "#b4bec8", "#e4ecf0"), dark=BLACK, wood=ramp("#14100c", "#241c14", "#382c20", "#4e3e2c", "#6a5640"),
        wrap=HEMP, leather=ramp("#1c120e", "#2e1e16", "#463022", "#604430"), mail=ramp("#16181a", "#282c30", "#404650", "#5c6470", "#808a96"), acc=BRASS, cloth=BLACK,
        fire=LANTERN, hot=LANTERN)
def gallowsguard(k):
    """the watch on the hill: a sallet and bevor, and the gallows itself bolted to his back with its lantern swinging over his shoulder"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 25.6, -0.4, 10.0, 6.8, 10.2), "blade", tag="sallet")
    a(h, C(0, 32.2, -0.4, 7.8, 1.0, 8.0), "blade", tag="sallet_top")
    a(h, C(0, 33.2, -0.4, 1.0, 1.4, 7.0), "dark", tag="ridge")
    a(h, C(0, 25.4, -6.4, 9.4, 1.6, 4.0), "blade", tag="sallet_tail", rots=(("x", -18),), pivot=(0, 26, -4.6))
    a(h, C(0, 22.4, 1.2, 9.8, 4.2, 8.8), "blade", tag="bevor")
    a(h, C(0, 26.5, 5.15, 8.8, 0.9, 0.3), "void", tag="sight")
    a(h, C(0, 26.7, 5.25, 7.2, 0.5, 0.3), "glow", tag="sight")
    k.rivets(h, [(-3.6, 24.0), (3.6, 24.0)], 5.75)
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.2), "blade", tag="cuirass")
    a(c, C(0, 12.2, 3.15, 6.6, 8.4, 0.5), "dark", tag="tabard")
    a(c, C(0, 15.8, 3.45, 0.9, 4.4, 0.3), "wrap", tag="gallows_mark")
    a(c, C(0.9, 19.6, 3.45, 2.8, 0.8, 0.3), "wrap", tag="gallows_mark")
    a(c, C(0, 22.6, 0, 8.7, 1.5, 6.8), "wrap", tag="rope_collar")
    a(b, C(1.6, 8.0, -4.4, 2.0, 35.0, 2.0), "wood", tag="post")
    a(b, C(-3.0, 40.4, -4.4, 11.4, 1.8, 1.8), "wood", tag="beam")
    a(b, C(-1.6, 33.6, -4.4, 1.2, 8.8, 1.0), "wood", tag="brace", rots=(("z", 45),), pivot=(1.6, 34.0, -4.4))
    a(b, C(1.6, 21.0, -4.4, 2.4, 0.9, 2.4), "dark", tag="post_band")
    a(b, C(1.6, 30.0, -4.4, 2.4, 0.9, 2.4), "dark", tag="post_band")
    a(b, C(-7.6, 35.6, -4.4, 0.5, 5.0, 0.5), "wrap", tag="rope")
    a(b, C(-7.6, 32.2, -4.4, 2.8, 3.6, 2.8), "dark", tag="lantern")
    k.fire(b, C(-7.6, 32.8, -4.4, 3.0, 2.4, 1.6))
    a(b, C(-7.6, 35.6, -4.4, 3.4, 0.7, 3.4), "blade", tag="lantern_top")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 11.2, 0, 5.6, 5.8, 5.6), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.0, 1.0, 6.0), "dark", tag="cuff")
        q = k.shoulder(s)
        for i in range(3):
            a(q, C(x + s * (1.0 - i * 0.2), 20.5 + i * 1.5, 0, 7.8 - i * 1.2, 1.3, 8.0 - i * 1.0), "blade" if i != 1 else "dark", tag="lame")
        p = k.leg(s)
        x = s * 1.95
        a(p, C(x, 2.4, 0, 4.9, 9.6, 4.9), "blade", tag="cuisse")
        a(p, C(x, 4.8, 2.5, 3.8, 2.8, 0.9), "dark", tag="poleyn")
    k.boots("blade", h=3.8, cuff="dark", toe="dark", toe_d=2.8)


# ---------------------------------------------------------------- the Rotwood

@design(cloth=ramp("#141c0e", "#20301a", "#2e4620", "#3e5e28", "#527a34"), cloth2=ramp("#1e3a10", "#2e5a16", "#42801e", "#60a42c", "#88c844"),
        wood=ramp("#1a120a", "#2c2014", "#40301e", "#584428", "#745c38"), leather=ramp("#1c120e", "#2e1e16", "#463022", "#604430"), bone=ramp("#6a5c44", "#8e7e60", "#b4a484", "#d4c8ac", "#ece4d0"),
        blade=ramp("#6a1a10", "#9a2a18", "#cc4424", "#ec7240", "#f6b088"), dark=ramp("#0a0c08", "#141810", "#20261a", "#2e3626"), acc=ramp("#c8bc90", "#dcd0a8", "#ece4c4", "#f8f4e0"), fire=SPORE, hot=SPORE)
def rotwarden(k):
    """keeper of the rot: antlers grown through a moss cowl, shelf fungus on the shoulders, spores lit from within"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.6, -0.4, 9.6, 8.4, 9.6), "cloth", tag="cowl")
    a(h, C(0, 22.4, -0.4, 11.0, 3.0, 11.0), "cloth2", tag="moss_ruff")
    a(h, C(0, 31.6, -0.4, 10.2, 1.6, 10.2), "cloth2", tag="moss_cap")
    a(h, C(0, 28.2, 4.4, 8.4, 3.6, 1.0), "dark", tag="cowl_shadow")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 29.2, 4.95, 1.4, 1.0, 0.3))
        k.horn(h, s * 4.2, 31.6, 0, [(3.6, -s * 30, 1.6), (3.6, -s * 12, 1.3), (3.0, s * 14, 1.0)], "wood")
        k.horn(h, s * 6.0, 34.6, 0, [(3.4, -s * 62, 1.0), (2.2, -s * 30, 0.7)], "wood")
        k.horn(h, s * 7.0, 37.0, 0, [(2.8, s * 34, 0.8)], "wood")
    a(h, C(-3.4, 32.6, 3.2, 3.0, 0.8, 3.0), "blade", tag="cap_small")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 19.4, 0, 8.7, 4.8, 6.4), "cloth2", tag="moss_mantle")
    for x, ln in ((-3.2, 2.2), (-1.0, 3.8), (1.4, 1.8), (3.4, 3.0)):
        a(c, C(x, 19.5 - ln, 3.25, 1.4, ln, 0.4), "cloth2", tag="moss_drip")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 5.8), "wood", tag="root_belt")
    for y, x in ((14.2, -2.6), (16.4, 1.2), (14.8, 3.0)):
        a(c, C(x, y, 2.85, 1.6, 1.6, 0.4), "acc", tag="spot")
        k.fire(c, C(x, y + 0.3, 3.05, 1.0, 1.0, 0.3))
    a(b, C(0, 14.0, -3.6, 8.0, 9.4, 1.6), "cloth2", tag="moss_back")
    for i, (x, y, w) in enumerate(((-2.6, 15.0, 5.2), (2.4, 18.6, 6.2), (-1.4, 21.4, 4.4))):
        a(b, C(x, y, -5.4, w, 1.0, 3.4), "blade", tag="shelf")
        a(b, C(x, y - 0.6, -5.2, w - 1.6, 0.7, 2.4), "acc", tag="shelf_gills")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "cloth", tag="sleeve")
        k.elbow(s, "cloth")
        a(p, C(x, 11.2, 0, 6.0, 5.4, 6.0), "cloth", tag="flare")
        a(p, C(x, 11.2, 0, 6.3, 1.2, 6.3), "cloth2", tag="flare_moss")
        q = k.shoulder(s)
        for i, (dy, w) in enumerate(((0, 8.6), (2.0, 6.8))):
            a(q, C(x + s * 1.2, 21.0 + dy, 0, w, 1.2, w), "blade", tag="fungus_cap")
            a(q, C(x + s * 1.2, 20.5 + dy, 0, w - 1.6, 0.6, w - 1.6), "acc", tag="fungus_gills")
        a(q, C(x + s * 0.6, 24.0, 2.0, 1.2, 0.8, 1.2), "acc", tag="fungus_spot")
        k.fire(q, C(x + s * 3.6, 22.3, 0, 0.8, 0.3, 0.8))
    k.legs("cloth", w=4.6)
    k.boots("wood", h=2.8, w=4.8, sole="dark")


@design(leather=ramp("#2a1a10", "#442c18", "#624224", "#845c34", "#a87c4a"), fur=ramp("#1e1208", "#34200e", "#4e3216", "#6c4820", "#8e6430", "#b48a4c"),
        bone=ramp("#6a5c44", "#8e7e60", "#b4a484", "#d4c8ac", "#ece4d0", "#fbf6e6"), cloth=ramp("#141c0e", "#20301a", "#2e4620", "#3e5e28"), dark=BLACK, wood=OAK, blade=IRON, fire=SPORE, hot=SPORE)
def stagrunner(k):
    """a hunter who runs with the herd: a stag's skull for a mask, its antlers spread wide, a pelt over one shoulder with the legs still on it"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 25.4, -0.4, 9.2, 7.0, 9.4), "leather", tag="hood")
    a(h, C(0, 24.6, -3.4, 10.0, 8.0, 3.6), "fur", tag="mane")
    a(h, C(0, 28.0, 3.4, 8.6, 5.2, 2.2), "bone", tag="skull_brow")
    a(h, C(0, 24.0, 4.8, 4.6, 4.6, 2.6), "bone", tag="skull_snout")
    a(h, C(0, 22.6, 5.4, 3.0, 1.8, 2.0), "dark", tag="nose_hole")
    a(h, C(0, 22.4, 5.6, 3.6, 1.0, 2.0), "bone", tag="skull_nose")
    for s in SIDES:
        a(h, C(s * 2.5, 29.4, 4.6, 2.0, 1.6, 1.1), "void", tag="eye_socket")
        k.fire(h, C(s * 2.5, 29.7, 5.0, 1.2, 0.9, 0.3))
        k.horn(h, s * 3.4, 33.0, 1.0, [(4.2, -s * 42, 1.6), (4.0, -s * 22, 1.3), (3.6, -s * 2, 1.0), (2.8, s * 20, 0.7)], "bone")
        k.horn(h, s * 6.2, 36.0, 1.0, [(3.4, s * 16, 1.0), (2.0, s * 30, 0.6)], "bone")
        k.horn(h, s * 8.8, 38.6, 1.0, [(3.2, -s * 56, 0.9), (1.8, -s * 74, 0.5)], "bone")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.8), "leather", tag="jerkin")
    a(c, C(0, 12.2, 0, 8.7, 1.4, 5.6), "dark", tag="belt")
    a(c, C(0, 16.2, 2.55, 1.0, 8.0, 0.5), "dark", tag="strap", rots=(("z", 32),), pivot=(0, 20, 2.55))
    for i in range(4):
        a(c, C(-2.0 + i * 1.2, 17.4 + i * 1.6, 2.95, 0.8, 1.6, 0.4), "bone", tag="tooth")
    a(b, C(1.0, 8.6, -3.4, 8.4, 15.0, 1.2), "fur", tag="pelt", rots=(("x", 6),), pivot=(1, 23.6, -3.4))
    a(b, C(1.0, 6.4, -4.8, 3.6, 2.6, 0.9), "fur", tag="pelt_tail")
    for s in SIDES:
        a(b, C(1.0 + s * 5.2, 16.6, -3.6, 2.2, 6.0, 0.9), "fur", tag="pelt_leg", rots=(("z", s * 26),), pivot=(1.0 + s * 4.2, 22.6, -3.6))
    a(k.shoulder(1), C(6.8, 20.8, 0, 7.2, 3.8, 7.2), "fur", tag="pelt_shoulder")
    a(k.shoulder(1), C(9.6, 19.0, 0, 2.0, 2.2, 3.4), "fur", tag="pelt_shoulder_fringe")
    a(k.shoulder(-1), C(-6.2, 21.0, 0, 5.6, 2.4, 5.6), "leather", tag="cop")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "leather", tag="sleeve")
        k.elbow(s, "leather")
        a(p, C(x, 11.6, 0, 5.2, 5.4, 5.2), "fur", tag="fur_bracer")
        a(p, C(x, 16.6, 0, 5.6, 0.7, 5.6), "dark", tag="tie")
        a(p, C(x, 12.0, 0, 5.6, 0.7, 5.6), "dark", tag="tie")
        p = k.leg(s)
        x = s * 1.95
        a(p, C(x, 2.4, 0, 4.6, 9.6, 4.6), "leather", tag="leg")
        a(p, C(x, 3.0, 0, 5.1, 4.4, 5.1), "fur", tag="shin_fur")
        a(p, C(s * 4.5, 8.6, 1.4, 0.8, 3.0, 0.8), "bone", tag="hoof_charm")
        p = k.boot(s)
        a(p, C(x, 0, 0.2, 4.9, 3.0, 5.4), "fur", tag="boot")
        a(p, C(x, 0, 2.6, 5.2, 1.6, 2.8), "dark", tag="hoof")
        a(p, C(x, 0, 2.9, 0.5, 1.7, 2.8), "void", tag="hoof_split")


@design(wood=ramp("#1a0e08", "#2e1c10", "#46301c", "#60462a", "#7e6038", "#a07e50"), dark=ramp("#0c0806", "#18120c", "#261c14", "#36281c"), mail=ramp("#1a0e08", "#2e1c10", "#46301c", "#60462a"),
        leather=ramp("#1c120e", "#2e1e16", "#463022", "#604430"), cloth=ramp("#16240e", "#243a14", "#34541c", "#4a7226"), cloth2=ramp("#1e3a10", "#2e5a16", "#42801e", "#60a42c", "#88c844"), blade=ramp("#1a0e08", "#2e1c10", "#46301c", "#60462a", "#7e6038"),
        fire=SPORE, hot=SPORE)
def barkwight(k):
    """the dead soldier the wood grew over: bark instead of plate, a knothole for a face, a dead branch breaking out of each shoulder"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.2, 0, 10.2, 9.6, 10.2), "wood", tag="trunk")
    a(h, C(0, 32.6, 0, 7.8, 1.6, 7.8), "wood", tag="trunk_top")
    a(h, C(0, 26.0, 5.0, 6.0, 5.0, 0.8), "dark", tag="knothole")
    a(h, C(0, 26.4, 5.2, 4.2, 4.0, 0.8), "void", tag="knot_deep")
    for s in SIDES:
        k.fire(h, C(s * 1.2, 28.4, 5.55, 1.1, 1.0, 0.3))
        a(h, C(s * 5.2, 23.4, 2.4, 0.9, 7.0, 2.6), "dark", tag="bark_ridge")
    a(h, C(0, 22.4, 0, 11.4, 1.6, 11.4), "cloth2", tag="moss_collar")
    k.spike(h, -3.0, 33.6, 1.0, 5.4, 1.5, "wood", rz=22)
    k.spike(h, 2.4, 33.6, -1.4, 4.2, 1.2, "wood", rz=-30)
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.0), "wood", tag="bark")
    for x, w in ((-3.2, 1.3), (-0.9, 1.7), (1.6, 1.3), (3.5, 1.0)):
        a(c, C(x, 12.8 + abs(x) * 0.6, 3.05, w, 10.2 - abs(x), 0.5), "dark", tag="bark_furrow")
    a(c, C(-1.0, 16.4, 3.35, 2.8, 3.2, 0.5), "dark", tag="wound")
    k.fire(c, C(-1.0, 17.0, 3.6, 1.6, 2.0, 0.3))
    a(c, C(0, 22.6, 0, 8.7, 1.5, 6.6), "cloth2", tag="moss")
    a(b, C(0, 13.0, -3.8, 7.2, 10.0, 1.6), "wood", tag="bark_back")
    k.spike(b, -1.6, 22.0, -4.0, 9.0, 2.0, "wood", rx=24, rz=14, steps=4)
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "wood", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.2, 0, 5.8, 5.8, 5.8), "wood", tag="vambrace")
        a(p, C(x, 16.2, 0, 6.1, 0.8, 6.1), "cloth2", tag="moss_ring")
        for dx, dz in ((-1.4, 2.95), (1.4, 2.95)):
            a(p, C(x + dx, 11.4, dz, 1.0, 5.2, 0.4), "dark", tag="furrow")
        q = k.shoulder(s)
        a(q, C(x + s * 0.8, 20.8, 0, 7.0, 3.2, 7.2), "wood", tag="stump")
        a(q, C(x + s * 0.8, 23.9, 0, 5.2, 0.7, 5.4), "cloth2", tag="stump_moss")
        k.spike(q, x + s * 2.4, 23.6, 0.6, 10.0 if s > 0 else 6.4, 2.4, "wood", rz=-s * 38, steps=4)
        k.spike(q, x + s * 5.0, 26.0, 0.6, 5.0, 1.2, "wood", rz=-s * 8, rx=-20)
        p = k.leg(s)
        x = s * 1.95
        a(p, C(x, 2.2, 0, 5.0, 9.8, 5.0), "wood", tag="bark_leg")
        a(p, C(x, 2.8, 2.5, 1.0, 9.0, 0.4), "dark", tag="furrow")
    k.boots("wood", h=4.0, w=5.4, sole="dark", cuff="cloth2")


@design(wood=ramp("#2a1408", "#46240e", "#66381a", "#885228", "#ac7038", "#d09a58", "#ecc88a"), dark=ramp("#120a06", "#20140c", "#301f12", "#442e1a"), blade=ramp("#2a1408", "#46240e", "#66381a", "#885228", "#ac7038", "#d09a58"),
        cloth2=ramp("#123a14", "#1c5a1c", "#2e8224", "#4ca830", "#80cc44", "#bcea6c"), cloth=ramp("#16240e", "#243a14", "#34541c", "#4a7226"), mail=ramp("#2a1408", "#46240e", "#66381a", "#885228"), acc=BRASS,
        leather=ramp("#1c120e", "#2e1e16", "#463022", "#604430"), gem=AMBER, fire=AMBER, hot=AMBER)
def heartwood(k):
    """the wood's own champion: a living crown of green, a cuirass cut from the tree's rings with its amber heart beating in the middle, roots for boots"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.0, 0, 10.4, 9.0, 10.4), "wood", tag="helm")
    a(h, C(0, 23.0, 4.9, 6.6, 3.6, 1.0), "dark", tag="lower_face")
    a(h, C(0, 27.2, 5.0, 8.6, 1.4, 0.8), "dark", tag="visor")
    k.fire(h, C(0, 27.5, 5.3, 7.0, 0.8, 0.3))
    a(h, C(0, 30.8, 0, 11.4, 1.4, 11.4), "dark", tag="circlet")
    for t, (x, z, ln) in enumerate(((0, 4.4, 6.8), (-3.8, 3.2, 5.6), (3.8, 3.2, 5.6), (-5.0, -1.0, 6.6), (5.0, -1.0, 6.6), (-2.2, -4.0, 5.0), (2.2, -4.0, 5.0))):
        k.spike(h, x, 31.8, z, ln, 2.2, "wood", rx=-z * 2.6, rz=-x * 3.4, steps=3, tag="crown_branch")
    for x, y, z, w, d in ((0, 37.6, 2.4, 11.0, 7.0), (-6.4, 36.0, -1.0, 6.4, 6.4), (6.4, 36.0, -1.0, 6.4, 6.4), (0, 38.4, -3.6, 8.0, 5.0)):
        a(h, C(x, y, z, w, 2.2, d), "cloth2", tag="leaves")
        a(h, C(x + 0.6, y + 2.1, z, w - 3.0, 1.2, d - 2.4), "cloth2", tag="leaves")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.4), "wood", tag="cuirass")
    for r in (7.8, 5.8, 3.8):
        a(c, C(0, 17.8 - r / 2 + 0.6, 3.3, r, r, 0.3), "dark" if r != 5.8 else "wood", tag="tree_ring")
    a(c, C(0, 16.8, 3.5, 2.8, 2.8, 0.5), "dark", tag="heart_seat")
    k.fire(c, C(0, 17.2, 3.75, 2.0, 2.0, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.0), "dark", tag="belt")
    a(c, C(0, 22.6, 0, 8.7, 1.5, 7.0), "cloth2", tag="green_collar")
    a(b, C(0, 13.0, -3.8, 7.6, 10.4, 1.4), "wood", tag="back_plate")
    for s in SIDES:
        a(b, C(s * 1.8, 22.0, -4.0, 2.4, 9.0, 1.8), "dark", tag="back_trunk", rots=(("z", -s * 16),), pivot=(s * 1.8, 22, -4.0))
    for x, y, w in ((-5.0, 30.0, 7.0), (5.0, 30.0, 7.0), (0, 31.6, 7.6)):
        a(b, C(x, y, -4.0, w, 2.6, 3.6), "cloth2", tag="back_leaves")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "mail", tag="sleeve")
        k.elbow(s, "dark")
        a(p, C(x, 11.2, 0, 6.0, 5.6, 6.0), "wood", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.3, 1.0, 6.3), "dark", tag="cuff")
        q = k.shoulder(s)
        a(q, C(x + s * 1.0, 20.7, 0, 8.6, 3.4, 8.6), "wood", tag="stump")
        a(q, C(x + s * 1.0, 24.0, 0, 7.0, 0.5, 7.0), "dark", tag="ring_cut")
        a(q, C(x + s * 1.0, 24.3, 0, 4.2, 0.4, 4.2), "wood", tag="ring_cut")
        a(q, C(x + s * 1.0, 24.5, 0, 1.6, 0.4, 1.6), "dark", tag="ring_cut")
        k.spike(q, x + s * 3.6, 21.4, 3.0, 3.6, 1.2, "wood", rz=-s * 60)
        p = k.leg(s)
        x = s * 1.95
        a(p, C(x, 2.4, 0, 5.1, 9.6, 5.1), "wood", tag="cuisse")
        a(p, C(x, 4.8, 2.6, 3.8, 2.8, 0.9), "dark", tag="knot_knee")
        k.fire(p, C(x, 5.5, 3.1, 1.4, 1.4, 0.3))
        p = k.boot(s)
        a(p, C(x, 0, 0.2, 5.6, 3.6, 6.0), "wood", tag="boot")
        a(p, C(x, 0, 0.5, 5.9, 0.7, 7.4), "dark", tag="sole")
        for dz, dx in ((4.4, 0.0), (3.2, s * 2.8), (-2.6, s * 3.0)):
            a(p, C(x + dx, 0, dz, 1.4, 1.0, 2.2), "dark", tag="root")
