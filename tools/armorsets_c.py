"""The Frozen Procession, the Silk Archive, the Weeping Mine, the Tide Chapel, the Brigand's Gorge and the Rookery
(see armorsets.py for the units and the fit rules)."""
import math

from armorsets import BRASS, C, IRON, SIDES, design, ramp
from armorsets_a import BLACK, HEMP, OAK
from armorsets_b import BONE, GILT, HIDE, PALE

ICE = ramp("#2e5e8a", "#4a86b0", "#70aed0", "#9cd0e6", "#c8e8f4", "#f2fcff")
RIME = ramp("#2a6a9c", "#3c90c0", "#60b8e0", "#94dcf4", "#c8f2fc", "#f4feff")
SNOW = ramp("#7c8a9c", "#9caabc", "#bcc8d6", "#d8e0e8", "#eef2f6", "#ffffff")
GREYCOAT = ramp("#1e2834", "#2e3c4c", "#425468", "#5c7086", "#7c90a4")
SILKRED = ramp("#2a040a", "#420a14", "#5e1220", "#7a1a2c", "#982a3c", "#b84a58")
THREAD = ramp("#7a7470", "#a09a94", "#c4beb8", "#e4dfda", "#fbf8f4")
SILKGLOW = ramp("#6e0e20", "#a01830", "#d42c44", "#f45c68", "#ff9c9c", "#ffe0d8")
PAGE = ramp("#8a7a56", "#a89870", "#c8b890", "#e0d4b0", "#f4eed4")
SOOT = ramp("#0e0e12", "#1a1a20", "#282830", "#383842", "#4c4c58")
VEIN = ramp("#5a0a06", "#8e140a", "#c82810", "#f05420", "#ff9850", "#ffe0a0")
COAL = ramp("#0c0a0a", "#181414", "#262020", "#383030", "#4e4442")
TIMBER = ramp("#2c1c0e", "#463016", "#624822", "#806432", "#a48648")
SEA = ramp("#0a2c30", "#10444a", "#1a6066", "#2a8082", "#46a4a0", "#7ccac0")
BRINE = ramp("#0e5a60", "#148884", "#22b4a4", "#50dcc0", "#a0f4dc", "#e4fff4")
CORAL = ramp("#5a1820", "#8a2830", "#bc4044", "#e0685e", "#f49c84", "#ffd0b8")
WEED = ramp("#0c2410", "#163a18", "#245622", "#3a7430", "#5a9440")
SHELL = ramp("#7a6a58", "#a08e78", "#c4b49c", "#e0d4c0", "#f4ecdc")
DUST = ramp("#2a0e08", "#44180e", "#622416", "#80321e", "#a04428", "#c4663c")
EMBERRED = ramp("#6a0c08", "#a01810", "#d43018", "#f46428", "#ffa050", "#ffe0a0")
CANVAS = ramp("#4a3a24", "#665238", "#84704e", "#a4906a", "#c4b28c")
RAVEN = ramp("#08080e", "#101018", "#1a1a26", "#282838", "#3a3a50", "#565670")
CARRION = ramp("#3a1a5a", "#5a2a8a", "#8444b8", "#b070e0", "#d8acf4", "#f6e6ff")
STEEL = ramp("#14161e", "#262a36", "#3e4454", "#5e6678", "#868ea2", "#b8c0d0", "#eaf0f8")


# ---------------------------------------------------------------- the Frozen Procession

@design(cloth=SNOW, wrap=SNOW, cloth2=GREYCOAT, gem=ICE, dark=ramp("#101820", "#1a2632", "#283a4a"), acc=ICE, leather=GREYCOAT, fire=RIME, hot=RIME)
def snowshroud(k):
    """a corpse that kept walking: wound in a white burial shroud, a crown of icicles, the breath frozen to the face and the mourners' ribbons trailing behind"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.4, -0.2, 9.6, 8.8, 9.6), "cloth", tag="shroud_head")
    for y, t in ((25.0, 6), (27.0, -5), (29.8, 7)):
        a(h, C(0, y, -0.2, 10.0, 0.7, 10.0), "cloth2", tag="wind", rots=(("z", t * 0.5),), pivot=(0, y, 0))
    a(h, C(0, 27.6, 4.75, 7.2, 1.4, 0.4), "void", tag="eye_gap")
    for s in SIDES:
        k.fire(h, C(s * 2.2, 27.9, 4.95, 1.2, 0.7, 0.3))
    a(h, C(0, 31.8, 0, 10.4, 1.0, 10.4), "gem", tag="crown_ring")
    for x, z, ln in ((0, 5, 8.6), (-3.2, 4.2, 5.6), (3.2, 4.2, 5.6), (-5.2, 0.8, 7.2), (5.2, 0.8, 7.2), (-3.4, -4.2, 5.0), (3.4, -4.2, 5.0), (0, -5.0, 6.4)):
        k.spike(h, x, 32.6, z, ln, 1.9, "gem", rz=-x * 1.4, rx=-z * 0.8, tag="icicle")
    for x, ln in ((-2.2, 3.4), (-0.6, 5.0), (1.2, 2.6)):
        k.spike(h, x, 26.0, 5.0, -ln, 0.9, "gem", tag="frozen_breath")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="shroud")
    for y, t in ((14.0, 9), (17.0, -7), (20.0, 8)):
        a(c, C(0, y, 2.75, 8.4, 1.1, 0.5), "cloth2", tag="wind", rots=(("z", t),), pivot=(0, y, 2.75))
    k.fire(c, C(0, 16.6, 3.1, 1.0, 2.2, 0.3))
    for i, x in enumerate((-3.2, -1.0, 1.2, 3.4)):
        ln = (20.0, 15.0, 22.0, 13.0)[i]
        a(b, C(x, 23.0 - ln, -3.6, 1.6, ln, 0.5), "cloth2" if i % 2 else "cloth", tag="ribbon", rots=(("x", 12 + i * 2), ("z", x * 2.0)), pivot=(x, 23, -3.6))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "cloth", tag="sleeve")
        k.elbow(s, "cloth")
        a(p, C(x, 11.4, 0, 5.4, 5.4, 5.4), "cloth", tag="wound_arm")
        for y in (12.6, 14.8):
            a(p, C(x, y, 0, 5.7, 0.6, 5.7), "cloth2", tag="wind")
        q = k.shoulder(s)
        a(q, C(x + s * 0.4, 21.0, 0, 6.0, 2.8, 6.0), "cloth", tag="shoulder")
        k.spike(q, x + s * 1.8, 23.6, 0, 4.2, 1.6, "gem", rz=-s * 24, tag="icicle")
        k.spike(q, x + s * 3.4, 23.0, 1.6, 3.0, 1.2, "gem", rz=-s * 48, tag="icicle")
    k.legs("cloth", w=4.6)
    k.boots("cloth", h=2.4, w=4.8)


@design(fur=ramp("#6c6a68", "#8e8c88", "#b0aea8", "#d0cec8", "#ecebe6", "#ffffff"), leather=ramp("#20160e", "#362618", "#4e3a24", "#6a5034", "#8a6e4a"), wrap=ramp("#5a0f12", "#7e161a", "#a42224", "#cc3a30"), wood=TIMBER, dark=BLACK, cloth=GREYCOAT, blade=STEEL, acc=TIMBER, fire=RIME, hot=RIME)
def hoarstep(k):
    """a scout who walks ahead of the procession: a fur-ringed parka, carved wooden snow goggles, a red scarf, wide snowshoes and two poles on the back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.8, 10.0, 8.4, 9.4), "leather", tag="parka_hood")
    a(h, C(0, 32.0, -1.2, 7.6, 1.2, 7.0), "leather", tag="hood_top")
    for y, x, w, ht in ((31.4, 0, 11.0, 2.2), (23.0, 0, 11.0, 2.0)):
        a(h, C(x, y, 4.1, w, ht, 2.0), "fur", tag="fur_ring")
    for s in SIDES:
        a(h, C(s * 4.8, 24.0, 4.1, 1.8, 8.4, 2.0), "fur", tag="fur_ring")
    a(h, C(0, 26.8, 4.0, 7.4, 2.8, 1.4), "wood", tag="wood_goggles")
    a(h, C(0, 27.8, 4.75, 6.0, 0.6, 0.3), "void", tag="goggle_slit")
    a(h, C(0, 27.9, 4.9, 4.8, 0.3, 0.3), "glow", tag="goggle_light")
    a(h, C(0, 23.8, 3.8, 7.4, 2.8, 1.4), "wrap", tag="scarf_up")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "leather", tag="parka")
    a(c, C(0, 12.2, 0, 8.7, 2.6, 5.8), "fur", tag="parka_hem")
    a(c, C(0, 21.6, 0, 8.7, 2.4, 6.0), "wrap", tag="scarf")
    a(c, C(2.0, 14.8, 3.1, 2.6, 6.8, 0.5), "wrap", tag="scarf_end")
    a(c, C(-2.2, 15.0, 2.8, 2.8, 2.6, 0.7), "leather", tag="pocket")
    a(b, C(0, 13.0, -4.8, 7.0, 9.0, 3.6), "leather", tag="pack")
    a(b, C(0, 22.0, -4.8, 7.4, 2.4, 2.4), "fur", tag="bedroll")
    for s in SIDES:
        rz = (("z", -s * 14),)
        a(b, C(s * 3.0, 4.0, -3.4, 0.7, 30.0, 0.7), "wood", tag="pole", rots=rz, pivot=(s * 3.0, 20, -3.4))
        a(b, C(s * 3.0, 6.0, -3.4, 2.6, 0.4, 2.6), "leather", tag="pole_basket", rots=rz, pivot=(s * 3.0, 20, -3.4))
    k.arms("leather", "leather", cuff="fur", w=5.2)
    for s in SIDES:
        a(k.arm(s), C(s * 6.0, 11.0, 0, 5.8, 1.6, 5.8), "fur", tag="mitten_cuff")
        a(k.shoulder(s), C(s * 6.2, 21.0, 0, 5.6, 2.4, 5.6), "fur", tag="fur_shoulder")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 2.4, 0, 4.6, 9.6, 4.6), "leather", tag="leg")
        for y in (3.0, 5.0):
            a(p, C(x, y, 0, 4.9, 0.7, 4.9), "wrap", tag="legging_tie")
        p = k.boot(s)
        a(p, C(x, 0.3, 0.2, 4.8, 3.2, 5.2), "leather", tag="boot")
        a(p, C(x, 0, 0.4, 6.8, 0.5, 11.0), "wood", tag="snowshoe")
        a(p, C(x, 0, 0.4, 4.8, 0.55, 8.8), "void", tag="snowshoe_web")
        for dz in (-3.0, 3.6):
            a(p, C(x, 0, dz, 6.4, 0.65, 0.6), "wood", tag="snowshoe_bar")


@design(cloth=GREYCOAT, wrap=SNOW, blade=STEEL, dark=ramp("#101820", "#1a2632", "#283a4a", "#3a5064"), acc=GILT, leather=ramp("#0e0e12", "#1a1a20", "#2a2a32"), wood=TIMBER, mail=GREYCOAT, cloth2=ramp("#2c0810", "#48101a", "#681c26", "#8c2c34"), gem=ICE, fire=RIME, hot=RIME)
def marcher(k):
    """the soldier who never stopped marching: a tall shako with a frozen plume, a greatcoat with white cross-belts, and the regiment's ice-stiff colours held up behind him"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.0, 7.4, 9.2), "leather", tag="head_wrap")
    a(h, C(0, 31.0, 0, 9.6, 6.4, 9.6), "cloth", tag="shako")
    a(h, C(0, 37.2, 0, 10.6, 1.0, 10.6), "dark", tag="shako_top")
    a(h, C(0, 30.6, 0.8, 10.4, 0.9, 11.6), "dark", tag="peak")
    a(h, C(0, 33.0, 4.9, 3.0, 3.4, 0.4), "acc", tag="shako_badge")
    k.spike(h, 0, 38.0, 3.0, 8.0, 2.2, "gem", rx=-6, tag="frozen_plume", steps=4)
    a(h, C(0, 22.6, 0.6, 10.2, 3.6, 9.0), "cloth", tag="turned_collar")
    a(h, C(0, 27.2, 4.65, 6.8, 1.2, 0.3), "void", tag="shadow")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 27.5, 4.8, 1.0, 0.6, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.4), "cloth", tag="greatcoat")
    for r in (34, -34):
        a(c, C(0, 12.0, 2.95, 1.3, 13.0, 0.5), "wrap", tag="cross_belt", rots=(("z", r),), pivot=(0, 18.2, 2.95))
    a(c, C(0, 17.0, 3.25, 2.2, 2.2, 0.4), "acc", tag="cross_plate")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 6.0), "wrap", tag="belt")
    a(c, C(-3.6, 7.4, 3.2, 3.4, 3.6, 3.4), "wood", tag="drum")
    a(c, C(-3.6, 11.0, 3.2, 3.6, 0.5, 3.6), "cloth2", tag="drum_rim")
    a(c, C(-3.6, 7.2, 3.2, 3.6, 0.5, 3.6), "cloth2", tag="drum_rim")
    a(b, C(0, 5.0, -3.8, 1.2, 40.0, 1.2), "wood", tag="standard_pole")
    k.spike(b, 0, 45.0, -3.8, 4.0, 1.8, "acc", tag="standard_tip")
    a(b, C(-6.0, 33.6, -3.8, 11.0, 10.4, 0.5), "cloth2", tag="colours")
    a(b, C(-6.0, 30.8, -3.8, 8.0, 3.0, 0.5), "cloth2", tag="colours")
    a(b, C(-6.0, 38.0, -3.5, 4.0, 3.6, 0.3), "acc", tag="colours_badge")
    for x, ln in ((-10.6, 5.2), (-7.4, 7.0), (-3.8, 6.0), (-1.2, 4.2)):
        k.spike(b, x, 33.8, -3.8, -ln, 1.0, "gem", tag="icicle")
    k.arms("cloth", "cloth", cuff="cloth2", w=5.2)
    for s in SIDES:
        q = k.shoulder(s)
        a(q, C(s * 6.4, 21.4, 0, 6.0, 1.6, 6.2), "cloth2", tag="epaulette")
        for t in (-2.0, 0, 2.0):
            a(q, C(s * 9.4, 20.0, t, 0.5, 2.6, 0.5), "acc", tag="fringe")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 2.4, 0, 4.6, 9.6, 4.6), "cloth", tag="leg")
        a(p, C(x, 7.4, 2.5, 3.8, 4.8, 0.6), "cloth", tag="coat_skirt")
    k.boots("leather", h=5.0, w=5.0, cuff="wrap", toe="dark", toe_d=2.0)


@design(blade=ramp("#22344a", "#344e6c", "#4c6c8e", "#6c90b0", "#94b8cc", "#c8e0ec"), dark=ramp("#101820", "#1a2632", "#283a4a", "#3a5064"), gem=ICE, mail=ramp("#22344a", "#344e6c", "#4c6c8e", "#6c90b0"), acc=SNOW, cloth=GREYCOAT, leather=GREYCOAT, fire=RIME, hot=RIME)
def rimeguard(k):
    """an honour guard the cold has been building on for a century: great blue plate under a crust of ice, spines of it breaking from the shoulders and helm"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.0, 0, 10.4, 9.4, 10.4), "blade", tag="helm")
    a(h, C(0, 26.6, 5.0, 8.4, 2.4, 0.8), "dark", tag="visor")
    k.fire(h, C(0, 27.2, 5.35, 6.8, 0.9, 0.3))
    a(h, C(0, 23.2, 5.1, 3.8, 3.2, 0.8), "gem", tag="ice_beard")
    a(h, C(-3.0, 30.0, 5.0, 3.6, 2.4, 0.9), "acc", tag="frost_crust")
    a(h, C(0, 32.0, 1.0, 8.0, 1.4, 6.0), "acc", tag="frost_crust")
    for i, (x, z, ln, r) in enumerate(((0, 2.8, 9.0, 0), (-1.8, 0.0, 7.0, 16), (1.8, 0.0, 7.4, -16), (0, -2.8, 8.0, 0))):
        k.spike(h, x, 33.2, z, ln, 2.6, "gem", rz=r, rx=z * -2, tag="ice_crest", steps=4)
    k.spike(h, -5.0, 29.0, 2.0, 4.6, 2.0, "gem", rz=68, rx=-10)
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.4), "blade", tag="cuirass")
    a(c, C(0, 12.2, 3.25, 7.0, 5.0, 0.5), "dark", tag="fauld")
    a(c, C(-2.0, 17.6, 3.3, 3.6, 3.0, 0.6), "acc", tag="frost_crust")
    a(c, C(2.0, 14.4, 3.3, 3.0, 4.0, 0.6), "gem", tag="ice_crust")
    k.spike(c, -1.0, 21.2, 3.2, 3.0, 2.0, "gem", rx=-52, rz=-20)
    k.fire(c, C(2.0, 15.4, 3.65, 1.6, 2.0, 0.3))
    a(b, C(0, 13.0, -3.8, 7.6, 10.4, 1.6), "blade", tag="back_plate")
    for x, y, ln, r in ((-3.0, 22.0, 8.0, 20), (0, 20.0, 11.0, 28), (3.0, 22.0, 7.0, 16), (-2.0, 15.0, 6.0, 44), (2.4, 16.0, 6.0, 42)):
        k.spike(b, x, y, -4.2, ln, 2.8, "gem", rx=r * 0.5, rz=-x * 5, tag="ice_back", steps=4)
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 11.0, 0, 6.0, 6.0, 6.0), "blade", tag="vambrace")
        a(p, C(x, 16.0, 0, 6.4, 1.0, 6.4), "dark", tag="cuff")
        k.spike(p, x + s * 2.8, 14.8, 0, 4.4, 2.0, "gem", rz=-s * 70, tag="ice_arm")
        q = k.shoulder(s)
        a(q, C(x + s * 1.2, 20.5, 0, 8.6, 3.8, 8.8), "blade", tag="pauldron")
        a(q, C(x + s * 1.2, 24.2, 0, 7.0, 0.9, 7.2), "acc", tag="frost_crust")
        k.spike(q, x + s * 3.0, 24.6, 0.4, 11.0, 4.0, "gem", rz=-s * 26, tag="ice_shoulder", steps=4)
        k.spike(q, x + s * 0.4, 24.8, 2.4, 7.0, 2.8, "gem", rz=-s * 8, rx=-16, tag="ice_shoulder")
        k.spike(q, x + s * 5.2, 23.0, -1.8, 7.0, 2.8, "gem", rz=-s * 58, rx=14, tag="ice_shoulder")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 2.4, 0, 5.1, 9.6, 5.1), "blade", tag="cuisse")
        a(p, C(x, 4.8, 2.6, 4.0, 2.8, 1.0), "dark", tag="poleyn")
        k.spike(p, x, 5.6, 3.0, 2.4, 1.4, "gem", rx=-70, tag="ice_knee")
    k.boots("blade", h=4.2, w=5.4, cuff="acc", toe="gem", toe_d=2.6, sole="dark")


# ---------------------------------------------------------------- the Silk Archive

@design(cloth=SILKRED, wrap=PAGE, leather=ramp("#1a0a0a", "#2c1414", "#442020", "#5e3030"), dark=BLACK, acc=GILT, wood=TIMBER, blade=ramp("#20282c", "#3c4a50", "#70868c", "#b0c8cc", "#e8fafa"), feather=THREAD, fire=SILKGLOW, hot=SILKGLOW)
def archivist(k):
    """keeper of the queen's stacks: spectacles and a scholar's cap with a quill in it, a tall case of scrolls on his back, the robe sleeves ink-stained"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.4, -0.2, 9.0, 7.0, 9.2), "cloth", tag="hood")
    a(h, C(0, 31.2, 0, 9.6, 1.4, 9.6), "dark", tag="cap_band")
    a(h, C(0, 32.6, 0, 11.6, 0.8, 11.6), "cloth", tag="square_cap")
    a(h, C(0, 33.4, 0, 1.6, 0.6, 1.6), "acc", tag="cap_button")
    a(h, C(5.4, 28.4, 0, 0.4, 5.0, 0.4), "acc", tag="tassel")
    a(h, C(3.6, 31.8, -1.0, 0.8, 9.6, 2.0), "feather", tag="quill", rots=(("z", -18),), pivot=(3.6, 32, -1))
    for s in SIDES:
        a(h, C(s * 2.2, 27.0, 4.6, 3.4, 3.2, 0.5), "acc", tag="lens_rim")
        a(h, C(s * 2.2, 27.4, 4.8, 2.6, 2.4, 0.3), "blade", tag="lens")
        k.fire(h, C(s * 2.2, 28.0, 4.95, 0.9, 0.9, 0.3))
    a(h, C(0, 28.2, 4.65, 1.0, 0.6, 0.4), "acc", tag="bridge")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 12.2, 2.75, 3.0, 11.8, 0.5), "wrap", tag="page_stole")
    for y in (13.6, 15.2, 16.8, 18.4, 20.0):
        a(c, C(0, y, 3.05, 2.2, 0.3, 0.3), "dark", tag="writing")
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.8), "dark", tag="belt")
    a(c, C(3.4, 9.6, 3.2, 1.6, 2.6, 1.6), "dark", tag="ink_pot")
    k.fire(c, C(3.4, 11.8, 3.2, 1.0, 0.4, 1.0))
    a(b, C(0, 11.0, -5.4, 8.6, 21.0, 4.6), "wood", tag="scroll_case")
    for y in (11.6, 17.8, 24.0, 30.2):
        a(b, C(0, y, -5.4, 9.0, 0.9, 5.0), "acc", tag="case_band")
    a(b, C(0, 12.6, -7.75, 7.2, 18.4, 0.4), "dark", tag="case_open")
    for i, (x, y) in enumerate(((-2.4, 13.4), (0, 13.4), (2.4, 13.4), (-1.2, 15.8), (1.2, 15.8), (-2.4, 18.4), (0, 18.4), (2.4, 18.4), (-1.2, 20.8), (1.2, 20.8), (0, 23.4), (-2.4, 23.4), (2.4, 23.4), (-1.2, 26.0), (1.2, 26.0))):
        a(b, C(x, y, -7.9, 2.0, 2.0, 0.6), "wrap", tag="scroll_end")
        a(b, C(x, y + 0.8, -8.2, 0.7, 0.5, 0.3), "cloth", tag="scroll_ribbon")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "cloth", tag="sleeve")
        k.elbow(s, "cloth")
        a(p, C(x, 10.8, 0, 6.2, 5.8, 6.2), "cloth", tag="flare")
        a(p, C(x, 10.8, 0, 6.5, 1.6, 6.5), "dark", tag="ink_stain")
        a(k.shoulder(s), C(x + s * 0.2, 21.0, 0, 5.6, 2.6, 5.6), "cloth", tag="shoulder")
    k.legs("cloth", w=4.6)
    k.boots("dark", h=2.6, w=4.8, cuff="wrap")


@design(cloth=SILKRED, wrap=THREAD, leather=BLACK, dark=BLACK, blade=ramp("#120408", "#260810", "#40101a", "#601a28", "#8a2c3c", "#c05a64"), acc=THREAD, gem=SILKGLOW, fire=SILKGLOW, hot=SILKGLOW)
def silkrunner(k):
    """the queen's own courier: bound in her silk, a mandibled mask with a cluster of eyes, and eight long legs folded up from his back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.0, 8.0, 9.2), "wrap", tag="silk_head")
    for y, r in ((25.4, 8), (27.4, -7), (30.4, 9)):
        a(h, C(0, y, -0.2, 9.4, 0.4, 9.6), "leather", tag="silk_turn", rots=(("z", r * 0.5),), pivot=(0, y, 0))
    a(h, C(0, 24.6, 4.4, 7.4, 6.4, 1.0), "blade", tag="mask")
    for x, y, w in ((-2.2, 29.0, 1.4), (2.2, 29.0, 1.4), (-0.8, 29.6, 1.0), (0.8, 29.6, 1.0), (-3.2, 27.8, 0.9), (3.2, 27.8, 0.9), (-1.4, 27.8, 0.9), (1.4, 27.8, 0.9)):
        k.fire(h, C(x, y, 4.95, w, w, 0.3))
    for s in SIDES:
        k.spike(h, s * 1.8, 25.2, 4.8, 3.6, 1.6, "blade", rx=-160, rz=s * 14, tag="mandible")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.0), "leather", tag="under")
    for y, r in ((13.4, 10), (15.2, -9), (17.0, 11), (18.8, -10), (20.6, 9), (22.4, -8)):
        a(c, C(0, y, 2.7, 8.6, 1.1, 0.5), "wrap", tag="silk_band", rots=(("z", r),), pivot=(0, y, 2.7))
    a(c, C(0, 16.8, 3.05, 2.4, 3.0, 0.5), "blade", tag="abdomen_plate")
    a(c, C(0, 17.4, 3.25, 1.2, 1.8, 0.3), "gem", tag="hourglass")
    a(b, C(0, 13.0, -3.8, 6.6, 10.0, 2.6), "blade", tag="carapace")
    a(b, C(0, 21.0, -5.4, 4.0, 2.0, 1.6), "blade", tag="leg_root")
    for s in SIDES:
        for i, (r, l1, r2, l2) in enumerate(((22, 12.0, 96, 13.0), (48, 13.0, 118, 13.0), (76, 13.0, 142, 13.0), (104, 11.0, 168, 11.0))):
            t, u = math.radians(s * r), math.radians(s * r2)
            ox, oy = s * 1.4, 21.0
            z = -5.4 - i * 0.2
            a(b, C(ox, oy, z, 1.5, l1, 1.5), "blade", tag="spider_femur", rots=(("z", -s * r),), pivot=(ox, oy, z))
            kx, ky = ox + math.sin(t) * l1, oy + math.cos(t) * l1
            a(b, C(kx, ky - 0.6, z, 2.0, 1.4, 2.0), "dark", tag="spider_knee")
            for j, w in enumerate((1.2, 0.8, 0.4)):
                d = l2 / 3
                a(b, C(kx, ky + j * d, z, w, d + 0.1, w), "blade", tag="spider_tibia", rots=(("z", -s * r2),), pivot=(kx, ky, z))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "wrap", tag="silk_sleeve")
        k.elbow(s, "wrap")
        a(p, C(x, 11.4, 0, 5.2, 5.6, 5.2), "wrap", tag="silk_arm")
        a(p, C(x, 13.0, 2.8, 2.8, 3.2, 0.5), "blade", tag="forearm_chitin")
        for y in (12.6, 15.0, 19.4):
            a(p, C(x, y, 0, 5.5, 0.4, 5.5), "leather", tag="silk_turn")
        a(k.shoulder(s), C(x + s * 0.2, 21.2, 0, 5.4, 2.0, 5.4), "blade", tag="cop")
    k.legs("wrap", w=4.6)
    for s in SIDES:
        for y in (3.8, 6.4, 9.0):
            a(k.leg(s), C(s * 1.95, y, 0, 4.9, 0.4, 4.9), "leather", tag="silk_turn")
    k.boots("blade", h=3.4, w=4.8, cuff="wrap", toe="leather", toe_d=3.2)


@design(blade=ramp("#22060c", "#3a0c14", "#54141e", "#70202c", "#903648"), mail=ramp("#20282c", "#3c4a50", "#5e6e74", "#869a9e"), wrap=PAGE, cloth=SILKRED, dark=BLACK, acc=GILT, leather=ramp("#2a160c", "#442612", "#62381c", "#845028"), wood=TIMBER, fire=SILKGLOW, hot=SILKGLOW)
def lector(k):
    """he reads the queen's law aloud in the halls: a great tome chained open on his chest, bookmarks streaming from a tall reading crown, a lectern on his back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.4, 8.2, 9.6), "blade", tag="helm")
    a(h, C(0, 26.8, 4.7, 7.4, 2.0, 0.5), "void", tag="visor")
    k.fire(h, C(0, 27.3, 4.9, 6.0, 0.7, 0.3))
    a(h, C(0, 32.0, 0, 10.2, 1.2, 10.2), "acc", tag="crown_rim")
    for x, z in ((-3.6, 3.8), (0, 4.2), (3.6, 3.8), (-3.6, -3.8), (0, -4.2), (3.6, -3.8)):
        a(h, C(x, 33.0, z, 1.8, 3.8, 0.5), "wrap", tag="page_tall")
    for s in SIDES:
        a(h, C(s * 4.8, 33.0, 0, 0.5, 3.8, 7.6), "wrap", tag="page_tall")
    for x, ln, m in ((-3.4, 12.0, "cloth"), (-1.2, 16.0, "acc"), (1.4, 14.0, "cloth"), (3.6, 10.0, "acc")):
        k.tail(h, x, 32.4, -5.4, ln, 1.0, m, lean=10, tag="bookmark")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.6), "mail", tag="hauberk")
    a(c, C(0, 12.8, 3.2, 8.4, 8.8, 1.4), "leather", tag="open_tome")
    a(c, C(0, 13.2, 3.9, 7.6, 8.0, 0.8), "wrap", tag="pages")
    a(c, C(0, 13.2, 4.2, 0.6, 8.0, 0.4), "dark", tag="gutter")
    for x in (-2.2, 2.2):
        for y in (14.4, 15.8, 17.2, 18.6, 20.0):
            a(c, C(x, y, 4.3, 2.6, 0.3, 0.3), "dark", tag="line")
    k.fire(c, C(-2.2, 20.6, 4.35, 2.2, 0.5, 0.3))
    for s in SIDES:
        a(c, C(s * 3.4, 21.4, 3.6, 0.6, 2.8, 0.6), "acc", tag="tome_chain")
    a(c, C(0, 12.2, 0, 8.7, 1.4, 6.2), "dark", tag="belt")
    a(b, C(0, 8.0, -4.4, 2.2, 26.0, 2.2), "wood", tag="lectern_post")
    a(b, C(0, 8.0, -4.4, 6.0, 1.4, 6.0), "wood", tag="lectern_foot")
    a(b, C(0, 33.6, -5.4, 10.0, 7.0, 1.0), "wood", tag="lectern_desk", rots=(("x", -18),), pivot=(0, 34, -4.4))
    a(b, C(0, 34.2, -4.6, 8.4, 5.6, 0.6), "wrap", tag="lectern_page", rots=(("x", -18),), pivot=(0, 34, -4.4))
    k.arms("mail", "blade", cuff="acc", w=5.4)
    for s in SIDES:
        q = k.shoulder(s)
        for i in range(3):
            a(q, C(s * (6.4 + i * 0.4), 20.6 + i * 1.2, 0, 6.8 - i * 1.0, 1.1, 7.2 - i * 0.8), "wrap" if i % 2 else "blade", tag="stacked_book")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 2.4, 0, 4.7, 9.6, 4.7), "mail", tag="mail")
        a(p, C(x, 6.2, 2.5, 3.8, 5.8, 0.6), "blade", tag="tasset")
    k.boots("leather", h=3.8, w=5.0, cuff="acc", toe="blade", toe_d=2.2)


@design(leather=ramp("#340a12", "#50101a", "#701a24", "#92283a", "#b4405a"), blade=ramp("#340a12", "#50101a", "#701a24", "#92283a", "#b4405a"), wrap=PAGE, cloth=THREAD, acc=GILT, gold=GILT, dark=BLACK, mail=ramp("#1a0a0c", "#2c1416", "#442022", "#5e3030"), gem=SILKGLOW, fire=SILKGLOW, hot=SILKGLOW)
def bindplate(k):
    """a living book: tome covers for pauldrons with their gilt corners and clasps, page edges in the plate, silk thread binding him shut and the queen's seal burning on the brow"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.0, 0, 10.2, 9.8, 10.2), "blade", tag="helm")
    a(h, C(0, 26.6, 5.0, 8.4, 1.0, 0.4), "void", tag="slit")
    a(h, C(0, 26.8, 5.2, 7.0, 0.5, 0.3), "glow", tag="slit_light")
    a(h, C(0, 30.2, 5.0, 3.6, 2.6, 0.5), "acc", tag="seal")
    k.fire(h, C(0, 30.8, 5.25, 1.8, 1.4, 0.3))
    for s in SIDES:
        a(h, C(s * 5.2, 23.0, 0, 0.6, 9.8, 10.4), "wrap", tag="page_block")
    for r in (24, -24):
        a(h, C(0, 22.8, 5.0, 11.2, 0.5, 0.5), "cloth", tag="thread", rots=(("z", r),), pivot=(0, 28, 5.0))
    a(h, C(0, 32.8, 0, 8.8, 1.0, 8.8), "acc", tag="spine_cap")
    a(h, C(0, 33.8, 0, 1.6, 2.6, 10.0), "blade", tag="spine_crest")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.6), "blade", tag="cover")
    a(c, C(0, 13.2, 3.3, 7.4, 9.8, 0.5), "dark", tag="tooling")
    a(c, C(0, 14.0, 3.5, 6.0, 8.2, 0.4), "blade", tag="tooling")
    a(c, C(0, 16.0, 3.6, 3.2, 4.2, 0.5), "acc", tag="clasp_plate")
    k.fire(c, C(0, 17.0, 3.9, 1.6, 2.2, 0.3))
    for x in (-3.4, 3.4):
        for y in (13.2, 21.6):
            a(c, C(x, y, 3.5, 1.8, 1.8, 0.5), "acc", tag="gilt_corner")
    for r in (30, -30):
        a(c, C(0, 11.6, 3.85, 0.5, 13.0, 0.3), "cloth", tag="thread", rots=(("z", r),), pivot=(0, 18, 3.85))
    a(b, C(0, 12.6, -4.6, 8.4, 11.0, 2.6), "wrap", tag="page_stack")
    for y in (13.4, 15.4, 17.4, 19.4, 21.4):
        a(b, C(0, y, -6.0, 8.6, 0.3, 0.3), "dark", tag="page_line")
    a(b, C(0, 12.2, -6.3, 9.0, 11.8, 0.7), "blade", tag="back_cover")
    a(b, C(0, 15.8, -6.75, 3.4, 4.6, 0.4), "acc", tag="back_clasp")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "blade", tag="vambrace")
        a(p, C(x, 15.8, 0, 6.4, 1.2, 6.4), "acc", tag="cuff")
        a(p, C(x, 13.0, 0, 6.2, 0.5, 6.2), "cloth", tag="thread")
        q = k.shoulder(s)
        a(q, C(x + s * 1.2, 20.5, 0, 7.2, 1.0, 10.0), "blade", tag="tome_cover")
        a(q, C(x + s * 1.2, 21.5, 0, 6.8, 2.0, 9.4), "wrap", tag="tome_pages")
        a(q, C(x + s * 1.2, 23.5, 0, 7.2, 1.0, 10.0), "blade", tag="tome_cover")
        a(q, C(x + s * 4.6, 20.5, 0, 0.8, 4.0, 10.0), "blade", tag="tome_spine")
        for t in (-4.8, 4.8):
            a(q, C(x - s * 1.6, 23.5, t * 0.9, 1.6, 1.2, 1.6), "acc", tag="gilt_corner")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 2.4, 0, 5.1, 9.6, 5.1), "blade", tag="cuisse")
        a(p, C(x, 6.2, 2.6, 3.8, 5.8, 0.7), "wrap", tag="page_tasset")
        a(p, C(x, 4.8, 2.7, 4.0, 2.6, 0.9), "acc", tag="poleyn")
    k.boots("blade", h=4.2, w=5.2, cuff="acc", toe="dark", toe_d=2.6)


# ---------------------------------------------------------------- the Weeping Mine

@design(cloth=SOOT, wrap=ramp("#3a2a14", "#5a4220", "#7c5e30", "#a07e44"), acc=BRASS, blade=BRASS, dark=COAL, leather=HIDE, wood=TIMBER, fire=VEIN, hot=VEIN)
def lampwright(k):
    """he tends the lamps in the deep galleries: a hoop of six miner's lamps round the hat, a yoke of spare ones over the shoulders, coal black robes"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.2, 7.6, 9.4), "cloth", tag="hood")
    a(h, C(0, 31.2, 0, 7.6, 3.4, 7.6), "leather", tag="hat")
    a(h, C(0, 30.4, 0, 14.4, 0.9, 14.4), "acc", tag="lamp_hoop")
    a(h, C(0, 30.4, 0, 12.4, 1.0, 12.4), "void", tag="hoop_hole")
    for t in range(6):
        r = math.radians(30 + t * 60)
        x, z = math.sin(r) * 7.0, math.cos(r) * 7.0
        a(h, C(x, 31.2, z, 2.2, 2.6, 2.2), "dark", tag="lamp")
        k.fire(h, C(x, 31.6, z, 2.4, 1.6, 1.2))
        a(h, C(x, 33.8, z, 1.6, 0.7, 1.6), "acc", tag="lamp_cap")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 27.4, 4.75, 1.0, 0.7, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 12.2, 2.75, 7.2, 8.4, 0.5), "wrap", tag="leather_apron")
    a(c, C(0, 12.2, 0, 8.7, 1.4, 5.8), "leather", tag="belt")
    for x in (-2.8, 0, 2.8):
        a(c, C(x, 10.6, 3.2, 1.6, 2.2, 1.4), "acc", tag="oil_flask")
    a(b, C(0, 24.4, -2.2, 22.0, 1.3, 1.3), "wood", tag="yoke")
    for s in SIDES:
        for x in (9.8, 7.4):
            ln = 3.0 if x == 9.8 else 5.0
            a(b, C(s * x, 24.4 - ln, -2.2, 0.4, ln, 0.4), "acc", tag="lamp_chain")
            a(b, C(s * x, 21.0 - ln, -2.2, 2.0, 3.0, 2.0), "dark", tag="yoke_lamp")
            k.fire(b, C(s * x, 21.4 - ln, -2.2, 2.2, 1.8, 1.2))
            a(b, C(s * x, 23.8 - ln, -2.2, 1.6, 0.6, 1.6), "acc", tag="lamp_cap")
    k.arms("cloth", "leather", cuff="wrap", w=5.4)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.3, 21.0, 0, 5.8, 2.4, 5.8), "leather", tag="shoulder_pad")
    k.legs("cloth", w=4.6)
    k.boots("leather", h=3.4, w=5.0, cuff="wrap", toe="dark", toe_d=2.4)


@design(fur=ramp("#1c1612", "#30261e", "#46382c", "#5e4c3c", "#7c6650"), leather=HIDE, cloth=SOOT, dark=COAL, blade=ramp("#20242a", "#383e46", "#586068", "#828c94", "#b4bec4"), wood=TIMBER, wrap=HEMP, acc=BRASS, hide2=ramp("#7a4a4a", "#a06a66", "#c48c84", "#e0b0a4"), fire=VEIN, hot=VEIN)
def tunnelrat(k):
    """small, fast, first down every new shaft: a rat-skin cap with the ears and whiskers left on, a tin headlamp, a coil of rope, the tail still hanging off the back of the belt"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.4, -0.2, 9.0, 7.6, 9.4), "fur", tag="rat_cap")
    a(h, C(0, 28.2, 4.2, 6.6, 3.8, 1.4), "fur", tag="rat_brow")
    a(h, C(0, 29.2, 5.8, 4.4, 2.4, 2.4), "fur", tag="rat_snout")
    a(h, C(0, 29.8, 7.2, 1.6, 1.2, 1.0), "hide2", tag="rat_nose")
    a(h, C(0, 31.4, 4.0, 3.6, 2.2, 1.4), "acc", tag="tin_lamp")
    k.fire(h, C(0, 31.8, 4.85, 2.4, 1.4, 0.3))
    for s in SIDES:
        a(h, C(s * 4.4, 32.0, -0.4, 3.6, 3.8, 0.6), "fur", tag="rat_ear")
        a(h, C(s * 4.4, 32.4, -0.05, 2.2, 2.6, 0.3), "hide2", tag="ear_pink")
        a(h, C(s * 2.0, 30.6, 5.2, 0.9, 0.9, 0.5), "void", tag="rat_eye")
        a(h, C(s * 4.0, 29.4, 6.4, 4.8, 0.3, 0.3), "dark", tag="whisker", rots=(("y", s * 12),), pivot=(s * 2, 29.4, 6.4))
    a(h, C(0, 22.8, 0, 9.8, 3.6, 9.8), "cloth", tag="neck_rag")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.8), "leather", tag="jerkin")
    a(c, C(0, 12.2, 0, 8.7, 1.2, 5.6), "dark", tag="belt")
    a(c, C(-2.0, 14.0, 2.6, 3.0, 3.0, 0.6), "cloth", tag="patch")
    a(c, C(2.8, 16.8, 2.6, 2.0, 2.6, 0.6), "fur", tag="patch")
    a(c, C(0, 12.4, 0, 9.4, 0.5, 6.6), "wrap", tag="rope")
    a(b, C(0, 13.2, -3.6, 6.6, 6.6, 1.6), "wrap", tag="rope_coil")
    a(b, C(0, 15.0, -3.6, 3.2, 3.2, 1.7), "dark", tag="rope_coil_hole")
    rz = (("z", 34),)
    a(b, C(0, 8.0, -4.8, 1.0, 19.0, 1.0), "wood", tag="pick_haft", rots=rz, pivot=(0, 16, -4.8))
    a(b, C(0, 26.2, -4.8, 12.0, 1.4, 1.2), "blade", tag="pick_head", rots=rz, pivot=(0, 16, -4.8))
    y, z = 12.0, -3.0
    for w, r in ((1.2, 16), (1.0, 34), (0.8, 54), (0.6, 72)):
        a(b, C(0, y - 3.2, z, w, 3.4, w), "hide2", tag="rat_tail", rots=(("x", r),), pivot=(0, y, z))
        y -= 2.9 * math.cos(math.radians(r))
        z -= 2.9 * math.sin(math.radians(r))
    k.arms("cloth", "leather", cuff="fur", w=5.0, low_h=4.4)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.2, 21.2, 0, 5.2, 2.0, 5.2), "fur", tag="fur_cop")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 4.0, 2.4, 3.4, 3.0, 0.7), "leather", tag="knee_pad")
    k.legs("cloth", w=4.6)
    a(k.leg(1), C(4.2, 8.0, 0, 1.2, 3.0, 2.8), "leather", tag="pouch")
    k.boots("leather", h=3.0, w=4.8, cuff="fur")


@design(blade=ramp("#2a1e12", "#46331e", "#64492c", "#88643e", "#b08658"), dark=COAL, wood=TIMBER, leather=HIDE, cloth=SOOT, mail=ramp("#20242a", "#383e46", "#586068", "#828c94"), acc=IRON, wrap=HEMP, wax=PALE, fire=VEIN, hot=VEIN)
def shaftman(k):
    """he props up the roof: a hard hat with a candle stuck on it, a pit-prop frame strapped to his back with a pulley and rope, a timberman's axe through the belt"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.0, 7.2, 9.2), "cloth", tag="coif")
    a(h, C(0, 30.6, 0, 10.0, 3.6, 10.0), "blade", tag="hard_hat")
    a(h, C(0, 30.0, 0.8, 13.0, 0.8, 13.6), "blade", tag="hard_hat_brim")
    a(h, C(0, 34.2, 0, 2.0, 0.8, 9.0), "blade", tag="hard_hat_ridge")
    a(h, C(0, 33.6, 4.8, 2.6, 1.0, 1.2), "dark", tag="candle_clip")
    a(h, C(0, 34.4, 4.8, 1.4, 2.4, 1.4), "wax", tag="candle")
    k.tongue(h, 0, 36.8, 4.8, 2.0, 1.0)
    a(h, C(0, 22.8, 0.2, 9.8, 4.4, 9.8), "wrap", tag="scarf")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 28.0, 4.75, 1.0, 0.7, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.4), "mail", tag="hauberk")
    a(c, C(0, 13.8, 2.95, 7.6, 8.6, 0.5), "leather", tag="vest")
    for x in (-2.6, 2.6):
        a(c, C(x, 13.8, 3.3, 1.2, 10.0, 0.4), "dark", tag="strap")
    a(c, C(0, 12.2, 0, 8.7, 1.6, 6.0), "dark", tag="belt")
    a(c, C(-3.6, 5.0, 3.3, 0.9, 9.0, 0.9), "wood", tag="axe_haft")
    a(c, C(-3.6, 6.0, 3.3, 3.0, 2.6, 0.7), "acc", tag="axe_head")
    for s in SIDES:
        a(b, C(s * 2.6, 4.0, -4.4, 2.2, 34.0, 2.2), "wood", tag="prop", rots=(("z", s * 18),), pivot=(s * 2.6, 22, -4.4))
    a(b, C(0, 35.4, -4.4, 18.0, 2.2, 2.2), "wood", tag="cap_timber")
    a(b, C(0, 26.0, -4.4, 11.0, 1.6, 1.8), "wood", tag="cross_timber")
    a(b, C(0, 32.0, -4.4, 3.2, 3.2, 1.2), "acc", tag="pulley")
    a(b, C(0, 33.0, -5.2, 1.0, 1.0, 0.5), "dark", tag="pulley_axle")
    k.tail(b, 1.3, 33.2, -4.4, 15.0, 0.5, "wrap", tag="rope")
    k.tail(b, -1.3, 33.2, -4.4, 9.0, 0.5, "wrap", tag="rope")
    a(b, C(-1.3, 22.4, -4.4, 2.4, 1.8, 1.6), "acc", tag="rope_bucket")
    k.arms("mail", "leather", cuff="dark", w=5.2)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.4, 20.9, 0, 6.2, 2.8, 6.4), "blade", tag="pad")
        a(k.leg(s), C(s * 1.95, 4.2, 2.5, 3.8, 2.8, 0.8), "blade", tag="knee_guard")
    k.legs("mail", w=4.7)
    k.boots("leather", h=4.2, w=5.0, cuff="dark", toe="blade", toe_d=2.4)


@design(stone=ramp("#141012", "#241c1e", "#362a2c", "#4a3c3c", "#645050", "#8a7068"), blade=ramp("#141012", "#241c1e", "#362a2c", "#4a3c3c", "#645050"), dark=COAL, acc=BRASS, mail=ramp("#20242a", "#383e46", "#586068"), leather=HIDE, gem=VEIN, fire=VEIN, hot=VEIN)
def deepdelver(k):
    """the last man down: hewn ore for plate with the red vein bleeding through the cracks, a brass helmet of lamps, and his right arm ending in a great drill"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.0, 0, 10.8, 9.8, 10.8), "acc", tag="brass_helm")
    a(h, C(0, 22.4, 0, 12.0, 1.4, 12.0), "dark", tag="helm_ring")
    a(h, C(0, 32.8, 0, 8.0, 1.0, 8.0), "acc", tag="helm_top")
    for x, y, w in ((0, 27.4, 4.6), (-3.8, 25.0, 2.6), (3.8, 25.0, 2.6)):
        a(h, C(x, y, 5.4, w + 1.0, w + 1.0, 0.6), "dark", tag="lamp_rim")
        k.fire(h, C(x, y + 0.5, 5.75, w, w, 0.3))
    a(h, C(0, 33.8, 0, 3.0, 3.0, 3.0), "dark", tag="exhaust")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.8), "stone", tag="ore_plate")
    for x, y, w, ht, r in ((-2.2, 13.0, 0.8, 8.0, 18), (1.6, 15.0, 0.8, 7.0, -24), (-0.2, 19.0, 3.8, 0.7, 12)):
        k.fire(c, C(x, y, 3.45, w, ht, 0.3), rots=(("z", r),), pivot=(x, y, 3.45))
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.2), "dark", tag="belt")
    a(b, C(0, 12.6, -5.2, 8.0, 11.0, 3.8), "dark", tag="power_box")
    a(b, C(0, 14.0, -7.2, 6.0, 8.0, 0.5), "acc", tag="power_door")
    k.fire(b, C(0, 15.0, -7.5, 3.8, 5.6, 0.3))
    for x in (-1.2, 1.2):
        a(b, C(x, 14.6, -7.7, 0.5, 6.8, 0.3), "void", tag="bar")
    for s in SIDES:
        a(b, C(s * 2.6, 23.6, -5.2, 1.6, 6.0, 1.6), "acc", tag="flue")
        k.tongue(b, s * 2.6, 29.6, -5.2, 2.4, 1.2)
    p, x = k.arm(1), 6.0
    a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
    k.elbow(1, "mail")
    a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "stone", tag="vambrace")
    a(p, C(x, 16.0, 0, 6.4, 1.0, 6.4), "acc", tag="cuff")
    p, x = k.arm(-1), -6.0
    a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
    k.elbow(-1, "mail")
    a(p, C(x, 14.0, 0, 7.0, 3.2, 7.0), "acc", tag="drill_collar")
    for i, (w, ht) in enumerate(((6.6, 2.2), (5.2, 2.2), (3.8, 2.2), (2.4, 2.2), (1.2, 2.0))):
        a(p, C(x, 11.8 - i * 2.2, 0, w, ht, w), "stone" if i % 2 else "acc", tag="drill")
    for s in SIDES:
        q, x = k.shoulder(s), s * 6.0
        a(q, C(x + s * 1.0, 20.5, 0, 8.4, 4.4, 8.6), "stone", tag="ore_shoulder")
        a(q, C(x + s * 2.6, 24.8, 1.0, 4.0, 2.4, 4.0), "stone", tag="ore_chunk")
        a(q, C(x - s * 0.4, 24.8, -1.8, 3.0, 1.6, 3.2), "stone", tag="ore_chunk")
        k.fire(q, C(x + s * 1.0, 22.4, 4.45, 5.4, 0.6, 0.3))
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 2.4, 0, 5.2, 9.6, 5.2), "stone", tag="ore_leg")
        k.fire(p, C(x + s * 0.4, 6.6, 2.65, 0.6, 4.0, 0.3), rots=(("z", s * 20),), pivot=(x, 8, 2.65))
    k.boots("stone", h=4.2, w=5.6, cuff="acc", toe="dark", toe_d=3.0)


# ---------------------------------------------------------------- the Tide Chapel

@design(cloth=SEA, wrap=SHELL, acc=CORAL, gem=CORAL, dark=ramp("#061416", "#0c2224", "#143438"), bone=SHELL, cloth2=WEED, leather=WEED, fire=BRINE, hot=BRINE)
def tidepriest(k):
    """she rings the drowned bell: a mitre of branching red coral, a cape of scallop shells, bladder wrack for a stole"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.8, -0.3, 9.4, 8.0, 9.4), "cloth", tag="hood")
    a(h, C(0, 27.2, 4.45, 7.2, 3.0, 0.4), "dark", tag="hood_dark")
    for s in SIDES:
        k.fire(h, C(s * 1.8, 28.3, 4.65, 1.0, 0.7, 0.3))
    a(h, C(0, 31.6, 0, 9.4, 1.0, 9.4), "wrap", tag="shell_band")
    for x, z, ln, r in ((0, 2.2, 10.0, 0), (-2.6, 1.2, 8.0, 18), (2.6, 1.2, 8.0, -18), (-1.4, -2.4, 7.0, 10), (1.4, -2.4, 7.0, -10)):
        k.spike(h, x, 32.4, z, ln, 2.4, "gem", rz=r, tag="coral", steps=4)
        for t in (-1, 1):
            ox = x - math.sin(math.radians(r)) * ln * 0.45
            k.spike(h, ox, 32.4 + ln * 0.45, z, ln * 0.45, 1.2, "gem", rz=r + t * 44, tag="coral_branch", steps=2)
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 12.2, 2.75, 2.8, 11.8, 0.5), "cloth2", tag="wrack_stole")
    for y in (13.4, 15.8, 18.2, 20.6):
        a(c, C(0, y, 3.05, 1.4, 1.2, 0.5), "acc", tag="bladder")
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.8), "wrap", tag="shell_belt")
    for r, x, y, w in ((0, -5.4, 20.0, 3.6), (0, -1.8, 20.0, 3.6), (0, 1.8, 20.0, 3.6), (0, 5.4, 20.0, 3.6)):
        a(c, C(x * 0.8, y, 3.0, w, 3.8, 0.5), "bone", tag="scallop")
    a(b, C(0, 8.0, -3.6, 8.0, 15.0, 0.7), "cloth", tag="cape", rots=(("x", 8),), pivot=(0, 23, -3.6))
    for j, y in enumerate((20.0, 16.4, 12.8, 9.2)):
        for x in ((-3.6, -1.2, 1.2, 3.6) if j % 2 == 0 else (-2.4, 0, 2.4)):
            a(b, C(x, y, -3.6 - (23 - y) * 0.14, 2.6, 3.6, 0.5), "bone", tag="scallop")
    a(c, C(-3.2, 7.4, 3.3, 2.8, 3.0, 2.8), "acc", tag="hand_bell")
    a(c, C(-3.2, 6.8, 3.3, 3.4, 0.9, 3.4), "acc", tag="bell_lip")
    a(c, C(-3.2, 10.4, 3.3, 0.5, 2.0, 0.5), "wrap", tag="bell_cord")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "cloth", tag="sleeve")
        k.elbow(s, "cloth")
        a(p, C(x, 11.0, 0, 6.2, 5.6, 6.2), "cloth", tag="flare")
        a(p, C(x, 11.0, 0, 6.5, 0.8, 6.5), "cloth2", tag="wrack_hem")
        q = k.shoulder(s)
        for t, w in ((-2.6, 3.2), (0, 3.6), (2.6, 3.2)):
            a(q, C(x + s * 0.6, 20.8, t, 6.4, 3.4, w), "bone", tag="scallop")
    k.legs("cloth", w=4.6)
    k.boots("wrap", h=2.4, w=4.8, sole="dark")


@design(leather=ramp("#3a2c08", "#5c4810", "#846c1c", "#ac902e", "#d0b44a"), wrap=HEMP, cloth=SEA, dark=ramp("#061416", "#0c2224", "#143438"), blade=ramp("#20282c", "#3c4a50", "#70868c", "#b0c8cc"), wood=TIMBER, acc=CORAL, mail=HEMP, fire=BRINE, hot=BRINE)
def netrunner(k):
    """the chapel's fisherman: a yellow oilskin sou'wester, a net thrown over one shoulder with its cork floats on, a harpoon on the back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.4, -0.2, 9.0, 7.2, 9.2), "cloth", tag="hood")
    a(h, C(0, 31.2, -0.4, 9.6, 2.8, 9.8), "leather", tag="souwester")
    a(h, C(0, 31.0, 1.4, 12.0, 0.7, 11.6), "leather", tag="souwester_front")
    a(h, C(0, 26.4, -6.0, 11.4, 5.4, 3.0), "leather", tag="souwester_back", rots=(("x", -12),), pivot=(0, 31, -4.6))
    a(h, C(0, 22.8, 0.4, 9.4, 3.6, 9.2), "dark", tag="beard_rag")
    a(h, C(0, 27.6, 4.65, 7.0, 1.0, 0.3), "void", tag="shadow")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 27.8, 4.8, 1.0, 0.6, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "leather", tag="oilskin")
    a(c, C(0, 12.2, 0, 8.7, 1.4, 5.8), "dark", tag="belt")
    a(c, C(-3.2, 7.8, 3.3, 2.6, 3.6, 2.0), "wood", tag="creel")
    a(c, C(-3.2, 11.4, 3.3, 2.8, 0.5, 2.2), "wrap", tag="creel_lid")
    for i in range(6):
        y = 13.0 + i * 1.8
        a(c, C(0, y, 2.85, 8.6, 0.3, 0.5), "wrap", tag="net", rots=(("z", 14),), pivot=(0, y, 2.85))
    for i in range(7):
        x = -4.0 + i * 1.4
        a(c, C(x, 12.4, 2.95, 0.3, 11.2, 0.5), "wrap", tag="net", rots=(("z", -8),), pivot=(x, 18, 2.95))
    a(b, C(1.0, 7.0, -3.6, 8.6, 16.0, 0.5), "mail", tag="net_back", rots=(("x", 8),), pivot=(1, 23, -3.6))
    for y in (8.0, 12.0, 16.0):
        a(b, C(2.0, y, -4.5 + (y - 8) * 0.12, 1.6, 1.6, 1.6), "acc", tag="float")
    a(k.shoulder(1), C(6.6, 20.8, 0, 7.0, 3.4, 7.0), "mail", tag="net_shoulder")
    for t in (-2.6, 0, 2.6):
        a(k.shoulder(1), C(9.9, 19.4, t, 1.4, 1.4, 1.4), "acc", tag="float")
    a(k.shoulder(-1), C(-6.2, 21.2, 0, 5.4, 2.2, 5.4), "leather", tag="oilskin_cape")
    rz = (("z", -18),)
    a(b, C(-2.0, 3.0, -4.6, 1.0, 34.0, 1.0), "wood", tag="harpoon_haft", rots=rz, pivot=(-2, 20, -4.6))
    k.add(b, C(-2.0, 37.0, -4.6, 2.8, 1.6, 0.8), "blade", tag="harpoon_barb", rots=rz, pivot=(-2, 20, -4.6))
    a(b, C(-2.0, 38.6, -4.6, 1.8, 2.0, 0.8), "blade", tag="harpoon_tip", rots=rz, pivot=(-2, 20, -4.6))
    a(b, C(-2.0, 40.6, -4.6, 0.9, 2.0, 0.6), "blade", tag="harpoon_tip", rots=rz, pivot=(-2, 20, -4.6))
    k.arms("leather", "cloth", cuff="leather", w=5.2)
    k.legs("leather", w=4.7)
    k.boots("dark", h=6.4, w=5.2, cuff="leather", sole="void")


@design(mail=ramp("#10262a", "#1a3a3e", "#285458", "#3a7070"), blade=ramp("#10262a", "#1a3a3e", "#285458", "#3a7070", "#569490"), stone=ramp("#4a4a44", "#6a6a60", "#8e8e80", "#b4b4a4", "#d8d8c8"), cloth2=WEED, dark=ramp("#061416", "#0c2224", "#143438"), acc=ramp("#3a1a08", "#6e3a10", "#a8641a", "#c88430"), leather=HIDE, fire=BRINE, hot=BRINE)
def wrackmail(k):
    """dredged up after a century on the sea bed: rusted mail thick with barnacles, wrack hanging from every plate, the ship's anchor still chained to him"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.8, 0, 9.8, 8.8, 9.8), "blade", tag="helm")
    a(h, C(0, 27.0, 4.9, 8.0, 1.0, 0.4), "void", tag="slit")
    k.fire(h, C(0, 27.2, 5.1, 6.4, 0.6, 0.3))
    for x, y, z, w in ((-3.4, 30.0, 4.8, 2.4), (2.6, 31.4, 3.6, 2.8), (3.6, 25.4, 4.8, 2.2), (-3.6, 32.4, -1.0, 3.0), (2.0, 32.4, -2.8, 2.2)):
        a(h, C(x, y, z, w, w * 0.7, w), "stone", tag="barnacle")
        a(h, C(x, y + w * 0.6, z, w * 0.45, 0.3, w * 0.45), "void", tag="barnacle_hole")
    for x, ln in ((-4.0, 6.4), (-1.6, 4.0), (1.0, 7.4), (3.6, 5.0)):
        k.tail(h, x, 32.4, 5.1, ln, 1.1, "cloth2", tag="wrack")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.8), "mail", tag="hauberk")
    a(c, C(0, 16.0, 3.05, 8.0, 6.6, 0.6), "blade", tag="breastplate")
    for x, y, w in ((-3.0, 19.8, 2.4), (2.4, 16.4, 2.8), (-0.6, 15.8, 1.8), (3.2, 20.4, 1.8)):
        a(c, C(x, y, 3.3, w, w, 0.8), "stone", tag="barnacle")
        a(c, C(x, y + w * 0.3, 3.75, w * 0.4, w * 0.4, 0.3), "void", tag="barnacle_hole")
    k.fire(c, C(-0.4, 18.8, 3.5, 1.2, 1.2, 0.3))
    for x, ln in ((-3.4, 7.0), (0.6, 5.0), (3.4, 9.0)):
        k.tail(c, x, 16.2, 3.5, ln, 1.2, "cloth2", tag="wrack")
    a(c, C(0, 12.2, 0, 8.7, 1.4, 6.4), "dark", tag="belt")
    a(b, C(0, 2.0, -4.6, 2.0, 25.0, 1.6), "acc", tag="anchor_shank")
    a(b, C(0, 19.0, -3.9, 3.4, 1.4, 1.4), "acc", tag="anchor_lashing")
    a(b, C(0, 26.0, -4.6, 8.0, 1.5, 1.6), "acc", tag="anchor_stock")
    a(b, C(0, 27.2, -4.6, 3.8, 3.6, 1.2), "acc", tag="anchor_ring")
    a(b, C(0, 28.2, -4.6, 2.0, 1.6, 1.4), "void", tag="anchor_hole")
    a(b, C(0, 2.0, -4.6, 15.0, 2.0, 1.6), "acc", tag="anchor_arm")
    for s in SIDES:
        a(b, C(s * 7.6, 2.8, -4.6, 2.0, 5.0, 1.6), "acc", tag="anchor_fluke", rots=(("z", -s * 20),), pivot=(s * 7.6, 3, -4.6))
        k.spike(b, s * 8.8, 7.0, -4.6, 3.0, 2.2, "acc", rz=-s * 20, tag="anchor_tip")
    for x, y in ((-4.0, 3.4), (1.4, 15.0), (-0.8, 21.4)):
        a(b, C(x, y, -5.3, 2.0, 1.6, 0.8), "stone", tag="barnacle")
    k.tail(b, 2.6, 23.0, -5.0, 11.0, 1.2, "cloth2", tag="wrack")
    k.arms("mail", "blade", cuff="dark", w=5.2)
    for s in SIDES:
        q = k.shoulder(s)
        a(q, C(s * 6.8, 20.8, 0, 7.0, 3.4, 7.2), "blade", tag="pauldron")
        a(q, C(s * 7.8, 24.0, 1.6, 2.8, 1.6, 2.8), "stone", tag="barnacle")
        a(q, C(s * 5.6, 24.0, -2.0, 2.2, 1.2, 2.2), "stone", tag="barnacle")
        a(q, C(s * 9.6, 18.0, 0, 1.2, 3.4, 3.4), "cloth2", tag="wrack")
    k.legs("mail", w=4.8)
    for s in SIDES:
        a(k.leg(s), C(s * 1.95, 6.0, 2.5, 3.8, 6.0, 0.6), "blade", tag="tasset")
        k.tail(k.leg(s), s * 2.6, 6.2, 3.0, 4.2, 1.0, "cloth2", tag="wrack")
    k.boots("blade", h=4.0, w=5.2, cuff="cloth2")


@design(blade=ramp("#3e0e0e", "#621816", "#8e2820", "#b84030", "#dc6448", "#f49c7c"), dark=ramp("#1a0606", "#2c0c0c", "#401412", "#5a1e1a"), mail=SEA, acc=ramp("#7a6a58", "#a08e78", "#c4b49c", "#e0d4c0", "#f4ecdc"), stone=SHELL, cloth=SEA, leather=WEED, gem=BRINE, fire=BRINE, hot=BRINE)
def brineclad(k):
    """a knight grown into a giant crab: a domed shell with eyes on stalks, a broad shell back, and one enormous claw clamped over the right arm"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.4, 11.8, 7.4, 11.8), "blade", tag="shell_dome")
    a(h, C(0, 31.4, -0.4, 9.2, 1.4, 9.2), "blade", tag="shell_top")
    a(h, C(0, 23.0, -0.4, 13.0, 1.6, 13.0), "dark", tag="shell_rim")
    a(h, C(0, 24.8, 5.6, 8.6, 1.2, 0.4), "void", tag="mouth_slit")
    k.fire(h, C(0, 25.1, 5.75, 7.0, 0.5, 0.3))
    for x in (-3.4, -1.7, 0, 1.7, 3.4):
        k.spike(h, x, 23.4, 6.2, 2.6, 1.2, "acc", rx=-168, tag="mouthpart", steps=2)
    for s in SIDES:
        a(h, C(s * 3.0, 31.4, 4.6, 1.2, 6.6, 1.2), "dark", tag="eye_stalk", rots=(("z", -s * 12),), pivot=(s * 3, 31, 4.6))
        a(h, C(s * 4.0, 37.6, 4.6, 2.6, 2.6, 2.6), "dark", tag="stalk_eye")
        k.fire(h, C(s * 4.0, 38.0, 6.05, 1.6, 1.6, 0.3))
        k.spike(h, s * 6.4, 26.0, 2.0, 3.2, 1.8, "blade", rz=-s * 70)
        k.spike(h, s * 6.4, 26.0, -3.0, 3.2, 1.8, "blade", rz=-s * 70)
    a(c, C(0, 12.2, 0, 8.7, 11.8, 7.0), "blade", tag="breast_shell")
    for y in (14.0, 17.0, 20.0):
        a(c, C(0, y, 3.5, 7.6 - (20 - y) * 0.3, 1.8, 0.5), "acc", tag="belly_plate")
    a(c, C(0, 12.2, 0, 8.7, 1.4, 7.6), "dark", tag="belt")
    a(b, C(0, 13.0, -6.2, 16.0, 11.6, 5.4), "blade", tag="back_shell")
    a(b, C(0, 15.0, -6.2, 19.0, 7.6, 4.4), "blade", tag="back_shell_wide")
    a(b, C(0, 24.4, -6.2, 11.0, 1.2, 4.0), "dark", tag="shell_top_rim")
    for s in SIDES:
        for i in range(3):
            k.spike(b, s * 9.5, 16.0 + i * 2.6, -6.2, 4.0, 2.0, "blade", rz=-s * (72 + i * 12), tag="shell_spine")
        a(b, C(s * 3.4, 17.4, -9.0, 3.6, 3.0, 0.6), "dark", tag="shell_mark")
    for s in SIDES:
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 2.4, 0, 5.2, 9.6, 5.2), "blade", tag="leg_shell")
        a(p, C(x, 4.8, 2.6, 4.0, 2.8, 1.0), "acc", tag="knee_shell")
    k.boots("blade", h=4.0, w=5.4, cuff="dark", toe="acc", toe_d=2.4)
    p, x = k.arm(1), 6.0
    a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "mail", tag="sleeve")
    k.elbow(1, "mail")
    a(p, C(x, 11.0, 0, 6.0, 5.8, 6.0), "blade", tag="vambrace")
    a(p, C(x, 16.0, 0, 6.4, 1.0, 6.4), "dark", tag="cuff")
    a(k.shoulder(1), C(6.8, 20.8, 0, 7.4, 3.4, 7.6), "blade", tag="shell_shoulder")
    k.spike(k.shoulder(1), 9.4, 23.8, 0, 3.6, 2.2, "blade", rz=-30)
    p, x = k.arm(-1), -6.0
    a(p, C(x, 18.6, 0, 5.4, 3.4, 5.4), "blade", tag="claw_arm")
    k.elbow(-1, "mail")
    a(p, C(x - 0.4, 10.0, 0, 8.8, 6.4, 9.0), "blade", tag="claw_palm")
    a(p, C(x - 0.4, 15.0, 0, 9.4, 1.6, 9.6), "dark", tag="claw_collar")
    a(p, C(x - 2.6, 4.6, 0, 5.0, 5.8, 5.0), "blade", tag="claw_big_finger")
    k.spike(p, x - 2.6, 4.8, 0, -4.0, 4.4, "blade", tag="claw_big_tip", steps=3)
    a(p, C(x + 3.0, 5.4, 0, 3.0, 5.0, 4.0), "acc", tag="claw_small_finger")
    k.spike(p, x + 3.0, 5.6, 0, -3.2, 2.8, "acc", tag="claw_small_tip", steps=3)
    a(k.shoulder(-1), C(-6.8, 20.8, 0, 7.4, 3.4, 7.6), "blade", tag="shell_shoulder")


# ---------------------------------------------------------------- the Brigand's Gorge

@design(cloth=DUST, wrap=CANVAS, feather=ramp("#101010", "#2a1414", "#7a2018", "#c44020", "#ec8040"), bone=BONE, leather=HIDE, dark=BLACK, acc=ramp("#3a1a08", "#6e3a10", "#a8641a", "#d89628"), wood=OAK, fire=EMBERRED, hot=EMBERRED)
def hexer(k):
    """the gang's bad luck, sold by the curse: a bonnet of red feathers on a bird skull, a shawl of knotted charms, rattles and little bags of grave dust"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 9.2, 7.8, 9.4), "cloth", tag="headscarf")
    a(h, C(0, 28.8, 4.4, 5.4, 3.4, 2.0), "bone", tag="bird_skull")
    a(h, C(0, 28.6, 6.2, 2.4, 1.6, 2.4), "bone", tag="bird_beak")
    a(h, C(0, 28.4, 8.0, 1.2, 1.0, 1.4), "bone", tag="bird_beak")
    for s in SIDES:
        a(h, C(s * 1.5, 30.0, 5.3, 1.2, 1.2, 0.3), "void", tag="socket")
        k.fire(h, C(s * 1.5, 30.2, 5.4, 0.6, 0.6, 0.3))
    a(h, C(0, 31.6, 0, 10.2, 1.2, 10.2), "wrap", tag="headband")
    for i, t in enumerate((-96, -72, -48, -24, 0, 24, 48, 72, 96)):
        ln = 9.0 + (i % 2) * 2.6
        a(h, C(0, 32.0, -3.4, 2.0, ln, 0.6), "feather", tag="red_feather", rots=(("z", t * 0.72),), pivot=(0, 31, -3.4))
    a(h, C(0, 24.4, 4.5, 5.0, 2.6, 0.5), "dark", tag="face_paint")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 18.4, 0, 8.7, 5.6, 6.2), "wrap", tag="shawl")
    for x, ln in ((-3.6, 4.0), (-1.8, 2.4), (0, 5.0), (1.8, 2.8), (3.6, 4.4)):
        k.tail(c, x, 18.6, 3.2, ln, 0.5, "dark", tag="fringe")
        a(c, C(x, 17.8 - ln, 3.2, 1.0, 1.0, 1.0), "bone" if x < 0 else "acc", tag="charm")
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.8), "leather", tag="belt")
    for x, m in ((-3.2, "leather"), (-1.2, "cloth"), (3.2, "leather")):
        a(c, C(x, 9.6, 3.2, 1.8, 2.4, 1.8), m, tag="dust_bag")
        a(c, C(x, 12.0, 3.2, 1.0, 0.5, 1.0), "wrap", tag="bag_tie")
    k.fire(c, C(-3.2, 10.4, 4.15, 0.8, 0.8, 0.3))
    a(b, C(0, 16.0, -3.6, 8.0, 8.0, 1.0), "wrap", tag="shawl_back")
    a(b, C(3.0, 6.0, -4.4, 1.0, 34.0, 1.0), "wood", tag="totem_staff", rots=(("z", 10),), pivot=(3, 20, -4.4))
    a(b, C(3.0, 38.4, -4.4, 4.0, 4.4, 3.4), "bone", tag="totem_skull", rots=(("z", 10),), pivot=(3, 20, -4.4))
    for dy in (34.0, 36.0):
        a(b, C(3.0, dy, -4.4, 2.8, 0.9, 2.4), "feather", tag="totem_tie", rots=(("z", 10),), pivot=(3, 20, -4.4))
    k.arms("cloth", "wrap", cuff="dark", w=5.2)
    for s in SIDES:
        a(k.shoulder(s), C(s * 6.3, 20.8, 0, 6.0, 2.6, 6.0), "wrap", tag="shawl_shoulder")
        for y in (13.0, 14.4, 15.8):
            a(k.arm(s), C(s * 6.0, y, 0, 5.5, 0.5, 5.5), "acc", tag="bangle")
    k.legs("cloth", w=4.6)
    k.boots("leather", h=3.0, w=4.8, cuff="wrap")


@design(leather=ramp("#3a2214", "#5a3820", "#7c5430", "#a07444", "#c49a64"), cloth=DUST, wrap=ramp("#5a0f12", "#7e161a", "#a42224", "#cc3a30"), dark=BLACK, blade=STEEL, wood=OAK, acc=BRASS, hide2=CANVAS, fire=EMBERRED, hot=EMBERRED)
def outlaw(k):
    """a gorge outlaw: a wide flat hat pulled low, a red bandana to the eyes, a dusty poncho and knives on a bandolier"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.2, -0.2, 9.0, 7.6, 9.2), "hide2", tag="head")
    a(h, C(0, 30.6, 0, 16.4, 0.8, 16.4), "leather", tag="hat_brim")
    a(h, C(0, 31.2, 0, 8.6, 3.0, 8.6), "leather", tag="hat_crown")
    a(h, C(0, 31.2, 0, 8.9, 1.0, 8.9), "dark", tag="hatband")
    a(h, C(0, 34.2, 0, 7.0, 0.6, 7.0), "leather", tag="hat_top")
    a(h, C(4.0, 31.4, 3.2, 1.4, 0.8, 0.5), "acc", tag="band_coin")
    a(h, C(0, 23.0, 0.4, 9.8, 4.8, 9.6), "wrap", tag="bandana")
    a(h, C(0, 22.2, 4.8, 4.0, 2.0, 0.5), "wrap", tag="bandana_point")
    a(h, C(0, 28.4, 4.65, 7.0, 1.2, 0.3), "void", tag="eye_shadow")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 28.7, 4.8, 1.0, 0.6, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.0), "leather", tag="vest")
    a(c, C(0, 13.8, 2.8, 8.7, 9.8, 0.5), "cloth", tag="poncho")
    for y in (15.0, 15.8):
        a(c, C(0, y, 3.05, 8.7, 0.5, 0.3), "wrap", tag="poncho_stripe")
    a(c, C(0, 18.0, 3.05, 1.2, 2.6, 0.3), "void", tag="poncho_neck")
    for i in range(7):
        t = i / 6
        x, y = -4.0 + 8.0 * t, 22.8 - 8.2 * t
        a(c, C(x, y, 3.25, 1.2, 0.6, 0.5), "leather", tag="bandolier")
        a(c, C(x, y - 1.2, 3.55, 0.6, 2.4, 0.3), "blade", tag="throwing_knife")
    a(b, C(0, 5.0, -3.4, 9.0, 19.0, 0.7), "cloth", tag="poncho_back", rots=(("x", 5),), pivot=(0, 24, -3.4))
    for y in (8.0, 9.2):
        a(b, C(0, y, -3.95, 9.2, 0.6, 0.4), "wrap", tag="poncho_stripe", rots=(("x", 5),), pivot=(0, 24, -3.4))
    for s in SIDES:
        q = k.shoulder(s)
        a(q, C(s * 6.0, 19.0, 0, 7.0, 5.4, 7.0), "cloth", tag="poncho_fall")
        a(q, C(s * 6.0, 20.0, 0, 7.2, 0.6, 7.2), "wrap", tag="poncho_stripe")
    k.arms("leather", "hide2", cuff="leather", w=5.0, low_h=4.6)
    k.legs("hide2", w=4.6)
    for s in SIDES:
        a(k.leg(s), C(s * 1.95, 6.0, 2.5, 3.6, 5.6, 0.6), "leather", tag="chap")
        a(k.leg(s), C(s * 2.4, 3.2, 2.6, 1.6, 0.9, 0.4), "acc", tag="conch")
    a(k.leg(-1), C(-4.3, 7.4, 0, 0.9, 4.0, 2.2), "blade", tag="boot_knife")
    k.boots("leather", h=4.4, w=4.8, cuff="dark", toe="leather", toe_d=3.4)
    for s in SIDES:
        a(k.boot(s), C(s * 1.95, 0.8, -3.2, 1.2, 1.2, 1.4), "acc", tag="spur")


@design(cloth=ramp("#14060a", "#26101a", "#3e1a2a", "#58283c", "#7a3c52"), cloth2=ramp("#121216", "#20202a", "#30303e", "#444456"), wrap=PALE, leather=HIDE, dark=BLACK, acc=GILT, blade=STEEL, wood=OAK, mail=STEEL, fire=EMBERRED, hot=EMBERRED)
def highwayman(k):
    """stand and deliver: a gilt-edged tricorn, a black half mask, a skirted coat with the collar turned up, a crossbow slung behind"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.2, -0.2, 9.0, 7.0, 9.2), "cloth2", tag="scarf_head")
    a(h, C(0, 27.2, 4.45, 8.0, 2.8, 0.6), "dark", tag="half_mask")
    for s in SIDES:
        a(h, C(s * 2.2, 28.0, 4.7, 2.0, 0.9, 0.3), "void", tag="mask_eye")
        k.fire(h, C(s * 2.2, 28.2, 4.85, 1.0, 0.5, 0.3))
    a(h, C(0, 31.0, 0, 9.6, 2.0, 9.6), "cloth", tag="crown")
    a(h, C(0, 33.0, 0, 8.0, 1.0, 8.0), "cloth", tag="crown_top")
    for t in (0, 120, 240):
        a(h, C(0, 30.6, 6.0, 14.0, 4.2, 0.8), "cloth2", tag="tricorn_side", rots=(("x", -14), ("y", t)), pivot=(0, 31, 0))
        a(h, C(0, 34.5, 6.0, 14.0, 0.5, 0.9), "acc", tag="tricorn_edge", rots=(("x", -14), ("y", t)), pivot=(0, 31, 0))
    a(h, C(0, 22.4, 0, 11.2, 3.4, 10.8), "cloth", tag="collar_up")
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="coat")
    a(c, C(0, 12.2, 2.75, 3.4, 11.4, 0.5), "wrap", tag="waistcoat")
    for y in (14.4, 16.4, 18.4, 20.4):
        a(c, C(0, y, 3.05, 0.9, 0.9, 0.3), "acc", tag="button")
    for s in SIDES:
        a(c, C(s * 3.0, 18.8, 2.95, 2.2, 4.4, 0.4), "cloth2", tag="lapel")
        a(c, C(s * 3.0, 12.2, 2.95, 2.4, 1.4, 0.4), "acc", tag="pocket_flap")
    a(c, C(0, 13.4, 0, 8.7, 1.1, 5.8), "leather", tag="belt")
    a(c, C(-4.0, 4.4, 2.6, 0.9, 9.0, 1.0), "blade", tag="smallsword")
    a(c, C(-4.0, 12.4, 2.6, 1.8, 0.6, 1.8), "acc", tag="sword_guard")
    for s in SIDES:
        a(b, C(s * 2.2, 3.4, -3.4, 3.4, 19.0, 0.7), "cloth", tag="coat_skirt", rots=(("x", 7), ("z", -s * 3)), pivot=(s * 2.2, 22, -3.4))
        a(b, C(s * 2.2, 3.4, -4.6, 3.6, 0.8, 0.4), "acc", tag="coat_hem", rots=(("x", 0),), pivot=(s * 2.2, 22, -3.4))
    a(b, C(0, 16.0, -5.0, 2.0, 10.0, 1.4), "wood", tag="crossbow_stock", rots=(("z", 22),), pivot=(0, 20, -5.0))
    a(b, C(0, 24.2, -5.0, 16.0, 1.0, 1.0), "dark", tag="crossbow_bow", rots=(("z", 22),), pivot=(0, 20, -5.0))
    a(b, C(0, 19.0, -5.6, 14.0, 0.3, 0.3), "wrap", tag="crossbow_string", rots=(("z", 22),), pivot=(0, 20, -5.0))
    k.arms("cloth", "cloth", cuff="wrap", w=5.4)
    for s in SIDES:
        a(k.arm(s), C(s * 6.0, 15.8, 0, 6.2, 1.8, 6.2), "cloth2", tag="turned_cuff")
        a(k.arm(s), C(s * 6.0, 10.8, 0, 5.6, 0.9, 5.6), "wrap", tag="lace")
        a(k.shoulder(s), C(s * 6.2, 21.2, 0, 5.4, 2.0, 5.4), "cloth", tag="shoulder_cape")
    k.legs("cloth2", w=4.6)
    k.boots("dark", h=6.0, w=5.0, cuff="leather", toe="dark", toe_d=2.2)


@design(blade=ramp("#2a1412", "#46221c", "#663428", "#8a4a38", "#b0684e"), dark=BLACK, stone=DUST, cloth=ramp("#5a0f12", "#7e161a", "#a42224", "#cc3a30", "#e8604a"), mail=STEEL, acc=STEEL, leather=HIDE, wrap=HEMP, fire=EMBERRED, hot=EMBERRED)
def gorgeguard(k):
    """Red Jack's bodyguard, as wide as the pass: a bull-barred helm under a blood-red plume, boulders of red sandstone chained to the shoulders"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.0, 0, 10.4, 9.0, 10.4), "blade", tag="helm")
    a(h, C(0, 24.0, 5.05, 7.8, 5.4, 0.6), "void", tag="barred_gap")
    for x in (-3.2, -1.6, 0, 1.6, 3.2):
        a(h, C(x, 23.6, 5.3, 0.9, 6.2, 0.6), "acc", tag="bar")
    k.fire(h, C(0, 27.0, 5.15, 6.4, 0.7, 0.3))
    a(h, C(0, 30.6, 5.0, 11.0, 1.4, 0.9), "dark", tag="brow")
    a(h, C(0, 32.0, 0, 1.8, 2.0, 11.0), "dark", tag="crest_base")
    for i, (z, ln) in enumerate(((5.0, 7.0), (3.0, 8.0), (1.0, 8.8), (-1.0, 8.8), (-3.0, 8.4), (-5.0, 7.4), (-7.0, 6.0))):
        a(h, C(0, 33.8, z, 1.6, ln, 2.2), "cloth", tag="plume", rots=(("x", 8 + i * 5),), pivot=(0, 33.8, z))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.8), "blade", tag="cuirass")
    a(c, C(0, 12.2, 3.45, 7.4, 6.2, 0.5), "cloth", tag="tabard")
    a(c, C(0, 12.2, 0, 8.7, 1.6, 7.2), "dark", tag="belt")
    k.rivets(c, [(-3.0, 21.6), (-1.0, 21.6), (1.0, 21.6), (3.0, 21.6)], 3.6, mat="acc")
    k.fire(c, C(0, 15.0, 3.75, 1.8, 1.8, 0.3))
    for r in (42, -42):
        a(c, C(0, 11.0, 3.7, 1.0, 15.0, 0.5), "acc", tag="chain", rots=(("z", r),), pivot=(0, 18.6, 3.7))
    a(b, C(0, 13.0, -3.8, 7.6, 10.4, 1.6), "blade", tag="back_plate")
    for r in (42, -42):
        a(b, C(0, 11.0, -4.8, 1.0, 15.0, 0.5), "acc", tag="chain", rots=(("z", r),), pivot=(0, 18.6, -4.8))
    a(b, C(0, 8.0, -4.8, 5.0, 12.0, 0.7), "cloth", tag="short_cape", rots=(("x", 8),), pivot=(0, 20, -4.8))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 11.0, 0, 6.2, 6.0, 6.2), "blade", tag="vambrace")
        a(p, C(x, 16.2, 0, 6.6, 1.0, 6.6), "dark", tag="cuff")
        for dz in (-3.4, 0, 3.4):
            k.spike(p, x + s * 3.0, 12.2, dz * 0.7, 2.6, 1.3, "acc", rz=-s * 90, tag="stud")
        q = k.shoulder(s)
        a(q, C(x + s * 2.0, 20.4, 0, 10.0, 7.4, 10.0), "stone", tag="boulder")
        a(q, C(x + s * 2.4, 27.6, 0.6, 6.6, 2.2, 6.4), "stone", tag="boulder_top")
        a(q, C(x + s * 7.0, 22.0, 0, 1.4, 3.6, 5.0), "stone", tag="boulder_side")
        a(q, C(x + s * 2.0, 23.0, 0, 10.4, 0.9, 10.4), "acc", tag="boulder_chain")
        a(q, C(x + s * 2.0, 20.4, 0, 0.9, 7.6, 10.4), "acc", tag="boulder_chain")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 2.4, 0, 5.2, 9.6, 5.2), "blade", tag="cuisse")
        a(p, C(x, 4.6, 2.6, 4.0, 3.0, 1.0), "dark", tag="poleyn")
    k.boots("blade", h=4.4, w=5.4, cuff="dark", toe="acc", toe_d=2.8)


# ---------------------------------------------------------------- the Rookery

@design(cloth=RAVEN, feather=RAVEN, bone=BONE, wrap=ramp("#201428", "#34203e", "#4c3058", "#684478"), dark=BLACK, acc=BONE, leather=HIDE, wood=OAK, fire=CARRION, hot=CARRION)
def augur(k):
    """she reads the flocks: a long crow-skull mask, a tall black crest of feathers, a living raven perched on her shoulder, strings of knuckle bones"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.4, 9.4, 8.2, 9.2), "cloth", tag="hood")
    a(h, C(0, 26.8, 4.0, 7.0, 4.6, 1.4), "bone", tag="skull_mask")
    for z, w, ht, y in ((5.4, 4.0, 3.2, 26.4), (7.4, 2.8, 2.4, 26.0), (9.2, 1.8, 1.6, 25.6), (10.8, 1.0, 1.0, 25.2)):
        a(h, C(0, y, z, w, ht, 2.2), "bone", tag="beak")
    for s in SIDES:
        a(h, C(s * 2.2, 28.4, 4.75, 1.8, 1.4, 0.3), "void", tag="socket")
        k.fire(h, C(s * 2.2, 28.7, 4.9, 0.9, 0.7, 0.3))
    for i, t in enumerate((-30, -15, 0, 15, 30)):
        a(h, C(0, 32.0, -1.0 - abs(i - 2) * 0.4, 2.4, 11.0 - abs(i - 2) * 1.6, 0.6), "feather", tag="crest_feather", rots=(("z", t), ("x", 10)), pivot=(0, 32, -1))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.2), "cloth", tag="robe")
    a(c, C(0, 18.0, 0, 8.7, 6.0, 6.4), "feather", tag="feather_mantle")
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.8), "wrap", tag="sash")
    for x in (-3.2, -1.6, 0, 1.6, 3.2):
        k.tail(c, x, 12.2, 3.1, 2.4 + abs(x) * 0.5, 0.3, "wrap", tag="bone_string")
        a(c, C(x, 11.4 - 2.4 - abs(x) * 0.5, 3.1, 0.7, 1.0, 0.7), "bone", tag="knuckle")
    k.fire(c, C(0, 16.4, 2.9, 1.2, 1.2, 0.3))
    a(b, C(0, 5.0, -3.6, 8.0, 18.0, 0.7), "feather", tag="feather_cape", rots=(("x", 7),), pivot=(0, 23, -3.6))
    q, x = k.shoulder(1), 6.0
    a(q, C(x + 0.3, 21.0, 0, 6.0, 2.6, 6.0), "feather", tag="feather_shoulder")
    a(q, C(x + 0.6, 26.0, -0.4, 3.2, 3.0, 4.6), "feather", tag="raven_body")
    a(q, C(x + 0.6, 28.4, 1.8, 2.4, 2.4, 2.4), "feather", tag="raven_head")
    a(q, C(x + 0.6, 28.8, 3.6, 0.9, 0.8, 1.8), "dark", tag="raven_beak")
    a(q, C(x + 0.6, 26.0, -3.4, 2.0, 0.6, 3.0), "feather", tag="raven_tail")
    k.fire(q, C(x + 1.85, 29.6, 2.2, 0.3, 0.6, 0.6))
    a(q, C(x + 0.6, 23.6, 0, 1.8, 2.4, 0.6), "dark", tag="raven_leg")
    a(k.shoulder(-1), C(-6.3, 21.0, 0, 6.0, 2.6, 6.0), "feather", tag="feather_shoulder")
    k.arms("cloth", "wrap", cuff="feather", w=5.4)
    k.legs("cloth", w=4.6)
    k.boots("leather", h=2.6, w=4.8, toe="bone", toe_d=2.6)


@design(leather=RAVEN, blade=STEEL, feather=STEEL, cloth=ramp("#201428", "#34203e", "#4c3058", "#684478"), dark=BLACK, acc=STEEL, fire=CARRION, hot=CARRION)
def featherblade(k):
    """every feather sharpened: a slim raven-winged duellist, a fan of steel plumes along each forearm that opens like a wing when the arm comes up"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.2, -0.2, 9.0, 7.8, 9.2), "leather", tag="hood")
    a(h, C(0, 22.6, 0.2, 9.8, 3.8, 9.6), "cloth", tag="face_scarf")
    a(h, C(0, 27.4, 4.65, 7.4, 1.4, 0.3), "void", tag="eye_band")
    k.fire(h, C(0, 27.8, 4.8, 5.8, 0.5, 0.3))
    for s in SIDES:
        for i, (t, ln) in enumerate(((32, 7.6), (52, 6.6), (74, 5.4))):
            a(h, C(s * 4.4, 31.0, -1.0 - i * 0.6, 1.4, ln, 0.5), "blade", tag="wing_ear", rots=(("z", -s * t),), pivot=(s * 4.4, 31, -1))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 4.8), "leather", tag="jerkin")
    a(c, C(0, 14.6, 2.6, 8.0, 8.6, 0.5), "cloth", tag="front")
    for y in (15.4, 17.0, 18.6, 20.2):
        a(c, C(0, y, 2.9, 5.0 + (y - 15) * 0.5, 0.5, 0.3), "acc", tag="feather_lace")
    a(c, C(0, 12.2, 0, 8.7, 1.3, 5.6), "dark", tag="belt")
    k.fire(c, C(0, 12.5, 3.0, 1.4, 0.8, 0.3))
    for s in SIDES:
        for i, (t, ln) in enumerate(((10, 14.0), (24, 15.0), (38, 15.0), (52, 13.0), (66, 10.0))):
            a(b, C(s * 1.2, 22.0 - ln, -3.2 - i * 0.2, 1.6, ln, 0.5), "blade", tag="back_plume", rots=(("z", s * t),), pivot=(s * 1.2, 22.0, -3.2))
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "leather", tag="sleeve")
        k.elbow(s, "leather")
        a(p, C(x, 11.4, 0, 5.2, 5.4, 5.2), "cloth", tag="bracer")
        for i in range(6):
            a(p, C(x + s * 3.0, 11.4 + i * 1.0, 0, 0.5, 1.2, 1.4), "blade", tag="plume")
            a(p, C(x + s * 3.0, 15.0 - i * 0.2, -0.2, 7.0 - i * 0.6, 1.0, 0.4), "blade", tag="wrist_plume", rots=(("z", s * (60 + i * 6)),), pivot=(x + s * 3.0, 15.0, -0.2))
        a(k.shoulder(s), C(x + s * 0.2, 21.2, 0, 5.4, 2.2, 5.4), "blade", tag="plume_shoulder")
    k.legs("leather", w=4.6)
    for s in SIDES:
        a(k.leg(s), C(s * 3.8, 3.0, 0, 0.6, 6.0, 3.6), "blade", tag="shin_plume")
    k.boots("leather", h=3.4, w=4.6, cuff="acc", toe="acc", toe_d=3.0)


@design(feather=RAVEN, blade=RAVEN, mail=STEEL, dark=BLACK, acc=ramp("#3a2a4e", "#5a4478", "#7c62a0", "#a48cc4"), cloth=RAVEN, leather=HIDE, bone=BONE, fire=CARRION, hot=CARRION)
def ravenmantle(k):
    """a great black bird walking upright: a beaked helm, a cloak of a hundred feathers folded like closed wings, the wingtips crossing at the heels"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 24.0, -0.2, 10.0, 8.8, 10.2), "feather", tag="feather_cowl")
    a(h, C(0, 26.8, 5.0, 5.4, 4.4, 1.6), "dark", tag="helm_face")
    for z, w, ht, y in ((6.4, 4.0, 3.4, 26.8), (8.4, 3.0, 2.6, 26.2), (10.2, 2.0, 1.8, 25.6), (11.8, 1.2, 1.2, 25.0), (13.0, 0.6, 0.8, 24.6)):
        a(h, C(0, y, z, w, ht, 2.0), "dark", tag="beak")
    for s in SIDES:
        k.fire(h, C(s * 2.0, 29.4, 5.85, 1.2, 1.0, 0.3))
    for i, z in enumerate((3.0, 1.0, -1.0, -3.0, -5.0)):
        k.spike(h, 0, 32.4, z, 3.0 + i * 0.5, 2.2, "feather", rx=20 + i * 10, tag="crest", steps=2)
    a(c, C(0, 12.2, 0, 8.7, 11.8, 5.4), "feather", tag="breast")
    a(c, C(0, 22.0, 0, 8.7, 2.0, 6.0), "acc", tag="collar")
    a(c, C(0, 14.0, 2.95, 2.6, 8.0, 0.4), "mail", tag="breast_plate")
    k.fire(c, C(0, 18.4, 3.2, 1.0, 1.4, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 1.4, 6.0), "dark", tag="belt")
    for s in SIDES:
        for i, (ln, r, ww) in enumerate(((22.0, -1, 3.6), (21.0, 3, 3.4), (19.0, 8, 3.2), (16.0, 14, 3.0))):
            a(b, C(s * (1.4 + i * 1.6), 23.6 - ln, -3.2 - i * 0.25, ww, ln, 0.7), "feather", tag="closed_wing", rots=(("x", 6), ("z", s * r)), pivot=(s * (1.4 + i * 1.6), 23.6, -3.2))
        k.spike(b, s * 1.2, 1.8, -5.2, -5.0, 2.6, "feather", rz=s * 24, tag="wing_tip")
    for s in SIDES:
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.2, 3.4, 5.2), "feather", tag="sleeve")
        k.elbow(s, "feather")
        a(p, C(x, 11.2, 0, 5.6, 5.6, 5.6), "feather", tag="arm_feather")
        a(p, C(x, 16.2, 0, 6.0, 0.8, 6.0), "acc", tag="cuff")
        q = k.shoulder(s)
        a(q, C(x + s * 0.8, 20.4, 0, 8.0, 3.6, 8.4), "feather", tag="wing_shoulder")
        a(q, C(x + s * 0.8, 23.8, -0.4, 6.0, 1.6, 7.0), "feather", tag="wing_arch")
        k.spike(q, x + s * 3.4, 24.0, -1.4, 7.0, 3.0, "feather", rz=-s * 22, rx=14, tag="wing_shoulder_tip")
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 2.4, 0, 4.9, 9.6, 4.9), "feather", tag="feather_leg")
        p = k.boot(s)
        a(p, C(x, 0, 0.2, 4.8, 3.2, 5.0), "dark", tag="boot")
        for dx in (-1.6, 0, 1.6):
            a(p, C(x + dx, 0, 3.4, 1.2, 1.2, 2.6), "dark", tag="talon")
            k.spike(p, x + dx, 0.6, 4.8, 2.4, 1.0, "bone", rx=-100, tag="talon_tip", steps=2)
        a(p, C(x, 0, -3.0, 1.2, 1.0, 2.0), "dark", tag="talon")


@design(blade=STEEL, feather=STEEL, stone=ramp("#26262e", "#3c3c46", "#565660", "#74747e", "#9a9aa4"), dark=BLACK, acc=ramp("#3a2a4e", "#5a4478", "#7c62a0", "#a48cc4"), mail=STEEL, cloth=RAVEN, leather=HIDE, fire=CARRION, hot=CARRION)
def rookplate(k):
    """both kinds of rook: a helm walled like a chess castle with battlements for a crown, and steel wings of forged feathers half open on his back"""
    a, h, c, b = k.add, k.h, k.c, k.back
    a(h, C(0, 23.0, 0, 10.2, 11.0, 10.2), "blade", tag="tower")
    a(h, C(0, 22.6, 0, 11.2, 1.4, 11.2), "dark", tag="tower_foot")
    a(h, C(0, 33.6, 0, 11.8, 1.6, 11.8), "blade", tag="tower_head")
    for t in range(4):
        for u in (-4.4, 0, 4.4):
            a(h, C(u, 35.2, 5.2, 2.2, 2.4, 1.4), "blade", tag="merlon", rots=(("y", t * 90),), pivot=(0, 35, 0))
    a(h, C(0, 26.4, 5.05, 3.4, 5.6, 0.3), "void", tag="arrow_slit")
    a(h, C(0, 28.6, 5.05, 7.8, 1.2, 0.3), "void", tag="arrow_slit")
    k.fire(h, C(0, 28.9, 5.2, 6.0, 0.6, 0.3))
    k.fire(h, C(0, 26.8, 5.2, 1.2, 4.6, 0.3))
    a(c, C(0, 12.2, 0, 8.7, 11.8, 6.6), "blade", tag="cuirass")
    a(c, C(0, 12.2, 3.35, 6.8, 7.0, 0.5), "cloth", tag="raven_tabard")
    a(c, C(0, 13.8, 3.65, 0.9, 4.6, 0.3), "acc", tag="tabard_bird")
    a(c, C(0, 16.0, 3.65, 5.0, 0.9, 0.3), "acc", tag="tabard_bird")
    a(c, C(0, 19.8, 3.4, 8.0, 0.9, 0.4), "dark", tag="band")
    a(c, C(0, 12.2, 0, 8.7, 1.5, 7.2), "dark", tag="belt")
    a(b, C(0, 13.0, -3.8, 7.8, 10.6, 1.6), "blade", tag="back_plate")
    for s in SIDES:
        a(b, C(s * 2.4, 19.0, -5.0, 3.0, 3.0, 1.6), "dark", tag="wing_root")
        for i, (t, ln, w) in enumerate(((18, 19.0, 3.4), (34, 21.0, 3.2), (50, 21.0, 3.0), (66, 19.0, 2.8), (82, 17.0, 2.6), (98, 14.0, 2.4), (114, 10.0, 2.2))):
            a(b, C(s * 2.4, 20.0, -5.4 - i * 0.2, w, ln, 0.6), "blade", tag="steel_feather", rots=(("z", -s * t),), pivot=(s * 2.4, 20, -5.4))
            r = math.radians(s * t)
            a(b, C(s * 2.4 + math.sin(r) * (ln - 0.6), 20 + math.cos(r) * (ln - 0.6), -5.8 - i * 0.2, w, 1.0, 0.3), "glow", group="fire", tag="feather_edge", rots=(("z", -s * t),), pivot=(s * 2.4 + math.sin(r) * (ln - 0.6), 20 + math.cos(r) * (ln - 0.6), -5.8))
        p, x = k.arm(s), s * 6.0
        a(p, C(x, 18.6, 0, 5.0, 3.4, 5.0), "mail", tag="sleeve")
        k.elbow(s, "mail")
        a(p, C(x, 11.0, 0, 6.0, 6.0, 6.0), "blade", tag="vambrace")
        a(p, C(x, 16.2, 0, 6.4, 1.0, 6.4), "dark", tag="cuff")
        q = k.shoulder(s)
        a(q, C(x + s * 0.8, 20.4, 0, 8.0, 3.0, 8.0), "blade", tag="turret")
        a(q, C(x + s * 0.8, 23.2, 0, 8.8, 1.0, 8.8), "dark", tag="turret_head")
        for t in range(4):
            a(q, C(x + s * 0.8, 24.2, 3.8, 2.6, 1.6, 1.2), "blade", tag="merlon", rots=(("y", t * 90),), pivot=(x + s * 0.8, 24, 0))
        p, x = k.leg(s), s * 1.95
        a(p, C(x, 2.4, 0, 5.1, 9.6, 5.1), "blade", tag="cuisse")
        a(p, C(x, 4.6, 2.6, 4.0, 3.0, 1.0), "dark", tag="poleyn")
    k.boots("blade", h=4.2, w=5.2, cuff="dark", toe="dark", toe_d=3.0)
