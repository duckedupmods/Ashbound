"""Weapon themes for the Roster v2 dungeons (weaponforge.py's Theme: ramps, an emblem, a trim), added to its THEMES.
Each dungeon's look carried onto its blades, hafts and shields; HINTS picks shapes from the names."""
from voxsword import ramp
from weaponforge import Theme, bx, ring_xy, seg


class WeepingMine(Theme):
    def __init__(self):
        super().__init__("weeping_mine",
                         blade=ramp("#1a1c20", "#2a2e34", "#3c424a", "#525a64", "#6c7680", "#8c96a0", "#b4bcc4", "#dce2e6"),
                         dark=ramp("#120c08", "#22160e", "#3a2414", "#5a361c", "#7c4a24", "#a0622e"),
                         wrap=ramp("#140e0a", "#22180f", "#342416", "#4a3420", "#60442a"),
                         wood=ramp("#1a120c", "#281b11", "#382617", "#4a331f", "#5e4229", "#74532f"),
                         glow=ramp("#0c4a48", "#1a7e78", "#34b8aa", "#5cd8c8", "#8ceee2", "#c4fff6", "#f0fffc"),
                         acc=ramp("#3a2410", "#5a361c", "#7c4a24", "#a0622e", "#c88444", "#e8aa66"))

    def crystal(self, s, cx, y, size, z):
        for k, (dx, a, h) in enumerate(((0, 0, 1.0), (-0.3, 22, 0.7), (0.3, -22, 0.75))):
            bx(s, cx + dx * size, y, 0, size * 0.28, size * h, z, "glow", glow=True, rots=(("z", a),), pivot=(cx + dx * size, y, 0))

    def emblem(self, s, cx, y, size, z, boss):
        # a miner's lamp: a copper body, its teal flame, a ring on top
        bx(s, cx, y - size * 0.5, 0, size * 0.8, size * 0.2, z, "acc")
        bx(s, cx, y - size * 0.3, 0, size * 0.6, size * 0.6, z * 0.9, "glow", glow=True)
        bx(s, cx, y + size * 0.3, 0, size * 0.8, size * 0.2, z, "acc")
        ring_xy(s, cx, y + size * 0.6, size * 0.2, size * 0.1, "dark", 8, depth=z * 0.5)
        if boss:
            self.crystal(s, cx, y + size * 0.7, size * 0.6, z * 0.7)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # crystal grown through the metal, copper bands where it was mended
        bx(s, 0, y0 + (y1 - y0) * 0.2, 0, half * 2 + 0.4, 0.8, thick + 0.3, "acc", tag="band")
        if where in ("blade", "head"):
            self.crystal(s, half * 0.6, y0 + (y1 - y0) * 0.45, 2.2 if boss else 1.6, thick + 0.4)
        else:
            self.crystal(s, half + 0.3, y0 + (y1 - y0) * 0.6, 1.4, thick + 0.3)


class TideChapel(Theme):
    def __init__(self):
        super().__init__("tide_chapel",
                         blade=ramp("#16201e", "#22302c", "#30423e", "#425852", "#58726a", "#74908a", "#9cb4ac", "#c8dad4"),
                         dark=ramp("#10140c", "#1e2414", "#2e3420", "#42462a", "#5a5a36", "#7a7444"),
                         wrap=ramp("#0e1e10", "#1a3018", "#284822", "#36602e", "#487a3c"),
                         wood=ramp("#2a2622", "#3a3530", "#4c4640", "#5e5850", "#726a60", "#8a8276"),
                         glow=ramp("#2a6a70", "#4a9aa0", "#7cc0c4", "#a4dcde", "#c8eef0", "#e6fafa", "#ffffff"),
                         acc=ramp("#6a6656", "#8a8672", "#aaa692", "#c8c4b0", "#e2dece", "#f4f2e8"))

    def emblem(self, s, cx, y, size, z, boss):
        # a little chapel bell, its clapper a pearl
        bx(s, cx, y - size * 0.45, 0, size * 0.9, size * 0.2, z, "dark")
        bx(s, cx, y - size * 0.3, 0, size * 0.7, size * 0.6, z * 0.9, "dark")
        bx(s, cx, y + size * 0.3, 0, size * 0.45, size * 0.25, z * 0.8, "dark")
        bx(s, cx, y - size * 0.62, 0, size * 0.25, size * 0.25, z * 0.6, "glow", glow=True)
        if boss:
            ring_xy(s, cx, y + size * 0.65, size * 0.22, size * 0.1, "acc", 8, depth=z * 0.5)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # barnacles crusted up one edge, a strand of kelp wound round
        for k in range(3):
            bx(s, half - 0.2, y0 + 1 + k * (y1 - y0) * 0.18, 0, 1.0, 1.0, thick + 0.4, "acc", tag="barnacle")
        seg(s, (-half - 0.3, y0 + 0.6), (half + 0.3, y0 + 2.2), 0.5, thick + 0.25, "wrap")
        seg(s, (-half - 0.3, y0 + 2.4), (half + 0.3, y0 + 4.0), 0.5, thick + 0.25, "wrap")


class BrigandsGorge(Theme):
    def __init__(self):
        super().__init__("brigands_gorge",
                         blade=ramp("#16161a", "#24242a", "#36363e", "#4a4a54", "#62626c", "#7e7e88", "#a0a0aa", "#cacad2"),
                         dark=ramp("#120a06", "#1e120a", "#2e1c10", "#402818", "#543622", "#6a462c"),
                         wrap=ramp("#2a0806", "#44100a", "#621a10", "#82261a", "#a03424"),
                         wood=ramp("#1e140c", "#2e1f12", "#40301c", "#544026", "#6a5232", "#82683e"),
                         glow=ramp("#6a1a04", "#a83a0a", "#e06a1a", "#ffa04a", "#ffc87a", "#ffe6c0", "#fff8ee"),
                         acc=ramp("#4a2e08", "#7a4c10", "#a87018", "#d0961f", "#ecbc34", "#ffdc6a"))

    def emblem(self, s, cx, y, size, z, boss):
        # a stolen coin, a red tassel hanging off it
        ring_xy(s, cx, y, size * 0.45, size * 0.18, "acc", 10, depth=z)
        bx(s, cx, y - size * 0.1, 0, size * 0.3, size * 0.3, z * 0.8, "acc")
        bx(s, cx, y - size * 1.0, 0, size * 0.2, size * 0.6, z * 0.6, "wrap", tag="tassel")
        if boss:
            for k in (-1, 0, 1):
                bx(s, cx + k * size * 0.25, y + size * 0.5, 0, size * 0.14, size * 0.3, z * 0.6, "acc", tag="crown")

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # a red rag knotted round it, notches hacked in the edge
        seg(s, (-half - 0.3, y0 + 0.6), (half + 0.3, y0 + 1.6), 0.7, thick + 0.3, "wrap")
        seg(s, (half + 0.2, y0 + 1.2), (half + 1.4, y0 - 1.4), 0.5, 0.5, "wrap")
        if where == "blade":
            for k in range(2):
                bx(s, half - 0.2, y0 + (y1 - y0) * (0.4 + 0.2 * k), 0, 0.6, 0.6, thick + 0.1, "dark", tag="notch")


class Rookery(Theme):
    def __init__(self):
        super().__init__("rookery",
                         blade=ramp("#0c0c10", "#16161c", "#22222a", "#30303a", "#42424e", "#5a5a68", "#7a7a88", "#a2a2b0"),
                         dark=ramp("#06060a", "#0e0e14", "#18182a", "#24243e", "#343456", "#4a4a74"),
                         wrap=ramp("#120c1a", "#1e1428", "#2c1e3c", "#3c2a52", "#4e386a"),
                         wood=ramp("#0c0a0a", "#161212", "#201a1a", "#2c2424", "#3a3030", "#4a3e3e"),
                         glow=ramp("#34205e", "#4e3488", "#7056b0", "#9a84d4", "#bcaee6", "#dcd4f6", "#f6f2ff"),
                         acc=ramp("#5a5446", "#7a7260", "#9a927c", "#bab29a", "#d8d0b8", "#eee8d6"))

    def emblem(self, s, cx, y, size, z, boss):
        # an eye of omen set in black pinions
        for a in (-35, 0, 35):
            bx(s, cx, y, 0, size * 0.22, size * 1.1, z * 0.6, "dark", rots=(("z", a),), pivot=(cx, y, 0))
        bx(s, cx, y + size * 0.1, 0, size * 0.5, size * 0.3, z, "glow", glow=True)
        bx(s, cx, y + size * 0.15, 0, size * 0.16, size * 0.16, z + 0.2, "void")
        if boss:
            ring_xy(s, cx, y + size * 0.15, size * 0.45, size * 0.08, "acc", 10, depth=z * 0.6)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # black feathers bound on with bone beads
        for k in range(3):
            seg(s, (half, y0 + 1 + k * 1.2), (half + 2.0, y0 - 1.0 + k * 1.2), 0.8, 0.4, "dark")
        bx(s, 0, y0 + 0.4, 0, half * 2 + 0.6, 0.8, thick + 0.3, "acc", tag="bead")


class HollowCircus(Theme):
    def __init__(self):
        super().__init__("hollow_circus",
                         blade=ramp("#1a1418", "#2a2028", "#3c2e3a", "#50404e", "#665466", "#80708a", "#a496ae", "#d0c6d8"),
                         dark=ramp("#0e0a0e", "#181218", "#221a22", "#2e242e", "#3c303c", "#4c3e4c"),
                         wrap=ramp("#3a0810", "#561018", "#741a24", "#922432", "#b03242"),
                         wood=ramp("#3a2a1a", "#544028", "#6e5638", "#8a6e4a", "#a6885e", "#c2a274"),
                         glow=ramp("#a8601a", "#e09a3a", "#ffc870", "#ffe0a0", "#fff0c8", "#fffaf0", "#ffffff"),
                         acc=ramp("#4a2e08", "#7a4c10", "#a87018", "#d0961f", "#ecbc34", "#ffdc6a"))

    def emblem(self, s, cx, y, size, z, boss):
        # a jester's mask: half white, half black, a gilt bell under it
        bx(s, cx - size * 0.2, y, 0, size * 0.4, size * 0.6, z, "glow")
        bx(s, cx + size * 0.2, y, 0, size * 0.4, size * 0.6, z, "dark")
        bx(s, cx, y - size * 0.55, 0, size * 0.3, size * 0.3, z * 0.8, "acc")
        if boss:
            for k in (-1, 1):
                bx(s, cx + k * size * 0.4, y + size * 0.55, 0, size * 0.2, size * 0.4, z * 0.6, "wrap")

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # red and gilt spiral bands, the way a showman's cane is painted
        for k in range(4):
            seg(s, (-half - 0.2, y0 + 0.4 + k * 1.6), (half + 0.2, y0 + 1.2 + k * 1.6), 0.6, thick + 0.25, "wrap" if k % 2 else "acc")


class MirefenCoven(Theme):
    def __init__(self):
        super().__init__("mirefen_coven",
                         blade=ramp("#101010", "#1a1a18", "#262622", "#34342e", "#44443c", "#58584e", "#76766a", "#9a9a8c"),
                         dark=ramp("#0a0c08", "#10140c", "#161c10", "#1e2616", "#28321c", "#344024"),
                         wrap=ramp("#1e3410", "#2c4a16", "#3e621e", "#527c28", "#6a9634"),
                         wood=ramp("#1e1a12", "#2c261a", "#3c3424", "#4e4430", "#62563c", "#786a4a"),
                         glow=ramp("#1a4a10", "#2a7a1a", "#44b02a", "#7ce04a", "#a8f07a", "#d4ffb8", "#f4fff0"),
                         acc=ramp("#3a3424", "#544c34", "#6e6446", "#8a7e5a", "#a69a70", "#c2b68a"))

    def emblem(self, s, cx, y, size, z, boss):
        # a hex-knot of twigs, a witchlight bead caught in it
        for a in (0, 60, 120):
            bx(s, cx, y - size * 0.5, 0, size * 0.14, size * 1.0, z * 0.6, "acc", rots=(("z", a),), pivot=(cx, y, 0))
        bx(s, cx, y - size * 0.1, 0, size * 0.32, size * 0.32, z, "glow", glow=True)
        if boss:
            ring_xy(s, cx, y, size * 0.5, size * 0.08, "wrap", 10, depth=z * 0.5)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # moss wound on, a toad-bone charm hung off it
        seg(s, (-half - 0.3, y0 + 0.4), (half + 0.3, y0 + 1.6), 0.8, thick + 0.3, "wrap")
        seg(s, (half + 0.2, y0 + 1.0), (half + 1.0, y0 - 1.6), 0.3, 0.3, "acc")
        bx(s, half + 1.0, y0 - 2.6, 0, 1.0, 1.0, 1.0, "acc", tag="charm")


THEMES = {t.gate: t for t in (WeepingMine(), TideChapel(), BrigandsGorge(), Rookery(), HollowCircus(), MirefenCoven())}

HINTS = {
    'seam_cutter': {'shape': 'straight', 'guard': 'cross'}, 'pick_knife': {'shape': 'straight'}, 'ore_hammer': {'shape': 'block'},
    'drill_lance': {'shape': 'spike'}, 'tunnel_cleaver': {'shape': 'cleaver'}, 'minecart_shield': {'shape': 'tower'},
    'veinsplitter': {'shape': 'falchion', 'guard': 'emblem'}, 'bedrock_aegis': {'shape': 'heater'}, 'motherlode': {'shape': 'spiked'},
    'shardfang': {'shape': 'curved'},
    'wreck_cutlass': {'shape': 'curved', 'guard': 'swept'}, 'barnacle_shiv': {'shape': 'wavy'}, 'anchor_maul': {'shape': 'block'},
    'tide_harpoon': {'shape': 'hook'}, 'keel_greatblade': {'shape': 'straight', 'guard': 'emblem'}, 'bell_shield': {'shape': 'round'},
    'longmourn': {'shape': 'straight', 'guard': 'emblem'}, 'bellwall': {'shape': 'tower'}, 'toll_of_the_deep': {'shape': 'bell'},
    'pearl_stiletto': {'shape': 'stiletto'},
    'highwayman_sabre': {'shape': 'curved', 'guard': 'swept'}, 'cutthroat_knife': {'shape': 'curved'}, 'gorge_club': {'shape': 'spiked'},
    'pike_of_the_pass': {'shape': 'glaive'}, 'ogre_cleaver': {'shape': 'cleaver'}, 'toll_gate_shield': {'shape': 'heater'},
    'red_jacks_sabre': {'shape': 'curved', 'guard': 'emblem'}, 'kingshield': {'shape': 'kite'}, 'ransom': {'shape': 'axe'},
    'purse_slitter': {'shape': 'straight'},
    'rook_sabre': {'shape': 'curved'}, 'talon_knife': {'shape': 'curved'}, 'beak_hammer': {'shape': 'spiked'},
    'rookery_spear': {'shape': 'glaive'}, 'wingblade': {'shape': 'flamberge'}, 'rook_kite_shield': {'shape': 'kite'},
    'mothers_pinion': {'shape': 'leaf', 'guard': 'emblem'}, 'black_wing_aegis': {'shape': 'heater'}, 'nevermore': {'shape': 'halberd'},
    'eyepick': {'shape': 'stiletto'},
    'ringmaster_rapier': {'shape': 'straight', 'guard': 'swept'}, 'juggling_knives': {'shape': 'straight'},
    'strongman_mallet': {'shape': 'barrel'}, 'lion_tamer_lance': {'shape': 'spike'}, 'big_top_cleaver': {'shape': 'cleaver'},
    'target_shield': {'shape': 'round'}, 'showstopper': {'shape': 'straight', 'guard': 'emblem'}, 'grand_ring': {'shape': 'round'},
    'final_act': {'shape': 'flamberge'}, 'knife_thrower_pick': {'shape': 'stiletto'},
    'reedblade': {'shape': 'leaf'}, 'toad_knife': {'shape': 'wavy'}, 'bog_oak_maul': {'shape': 'barrel'}, 'eel_spear': {'shape': 'hook'},
    'mirecleaver': {'shape': 'cleaver'}, 'coracle_shield': {'shape': 'round'}, 'matrons_sickle': {'shape': 'curved', 'guard': 'emblem'},
    'cauldron_lid': {'shape': 'round'}, 'drowning_pool': {'shape': 'pestle'}, 'hags_nail': {'shape': 'curved'},
}


# ---------------------------------------------------------------- the drops' item models (weaponforge mat_models)

from voxsword import Sword  # noqa: E402


def m_weeping_crystal():
    s = Sword('weeping_crystal')                 # a weeping crystal pried off a miner, a tear of light down it
    for (x, z, h, w, lean) in ((0, 0, 10, 2.6, 0), (-2.4, 0.5, 6, 1.9, 24), (2.2, -0.4, 7, 2.0, -18)):
        bx(s, x, 0, z, w, h, w, "glow", glow=True, rots=(("z", lean),), pivot=(x, 0, z))
    bx(s, 0.4, 2, 0, 0.7, 6, 2.8, "white", glow=True)
    bx(s, 0, -1.2, 0, 6.4, 1.6, 4.0, "dark")
    return s


def m_foremans_lamp():
    s = Sword('foremans_lamp')                   # the Foreman's lamp: copper, its teal flame, a bail
    bx(s, 0, 0, 0, 6.0, 1.4, 6.0, "acc")
    bx(s, 0, 1.4, 0, 4.4, 5.0, 4.4, "glow", glow=True)
    for x in (-2.2, 2.2):
        bx(s, x, 1.4, 0, 0.8, 5.0, 4.8, "dark")
    bx(s, 0, 6.4, 0, 5.4, 1.4, 5.4, "acc")
    bx(s, 0, 7.8, 0, 2.6, 1.2, 2.6, "acc")
    ring_xy(s, 0, 10.4, 2.0, 0.6, "dark", 10)
    return s


def m_heart_of_the_vein():
    s = Sword('heart_of_the_vein')               # the Vein's heart: a crystal heart still beating in its rock
    bx(s, 0, 0, 0, 8.0, 7.0, 5.0, "dark")
    bx(s, 0, 1.0, 0, 5.6, 5.4, 5.4, "glow", glow=True)
    for side in (1, -1):
        bx(s, side * 1.6, 6.0, 0, 2.6, 2.6, 4.4, "glow", glow=True)
    bx(s, 0, 2.4, 0, 2.4, 2.6, 5.8, "white", glow=True)
    for (x, h, a) in ((-3.2, 4, 20), (3.0, 5, -24), (0.6, 6, -6)):
        bx(s, x, 6.6, 0, 1.2, h, 1.2, "glow", glow=True, rots=(("z", a),), pivot=(x, 6.6, 0))
    return s


def m_barnacle_crust():
    s = Sword('barnacle_crust')                  # a crust of barnacles prised off a pew
    bx(s, 0, 0, 0, 9.0, 1.6, 6.0, "dark")
    for (x, z, h) in ((-2.8, 0, 3.0), (0, 0.6, 4.0), (2.6, -0.4, 3.4), (-1.0, -1.6, 2.4), (1.4, 1.8, 2.6)):
        bx(s, x, 1.6, z, 2.2, h, 2.2, "acc")
        bx(s, x, 1.6 + h - 0.6, z, 1.0, 0.8, 1.0, "dark")
    return s


def m_choir_pearl():
    s = Sword('choir_pearl')                     # a pearl the Barnacle Choir sang into: it still hums with light
    bx(s, 0, 0, 0, 7.0, 7.0, 7.0, "glow", glow=True)
    bx(s, 0, 1.0, 0, 5.0, 5.0, 7.4, "white", glow=True)
    bx(s, 0, -1.4, 0, 9.0, 1.6, 6.0, "acc")
    return s


def m_drowned_bells_clapper():
    s = Sword('drowned_bells_clapper')           # the Drowned Bell's clapper: a bronze ball on its iron tongue
    bx(s, 0, 6.0, 0, 1.6, 9.0, 1.6, "dark")
    ring_xy(s, 0, 15.4, 1.6, 0.6, "dark", 10)
    bx(s, 0, 0, 0, 6.4, 6.4, 6.4, "dark")
    bx(s, 0, 1.2, 0, 4.0, 4.0, 6.8, "glow", glow=True)
    return s


def m_stolen_coin():
    s = Sword('stolen_coin')                     # a fistful of stolen coin
    for k, (x, y) in enumerate(((0, 0), (-2.4, 1.6), (2.2, 2.4), (0.4, 4.0))):
        ring_xy(s, x, y + 2.4, 2.2, 1.0, "acc", 10)
        bx(s, x, y + 1.6, 0, 1.8, 1.6, 0.8, "acc")
    return s


def m_lieutenants_seal():
    s = Sword('lieutenants_seal')                # the lieutenant's seal-ring on its red cord
    ring_xy(s, 0, 3.0, 3.0, 1.0, "acc", 12)
    bx(s, 0, 5.4, 0, 3.0, 2.6, 1.6, "acc")
    bx(s, 0, 5.8, 0, 1.6, 1.6, 1.8, "glow", glow=True)
    seg(s, (2.6, 1.4), (5.0, -3.0), 0.6, 0.6, "wrap")
    return s


def m_bandit_kings_crown():
    s = Sword('bandit_kings_crown')              # Red Jack's crown, every point a different king's
    bx(s, 0, 0, 0, 10.0, 3.0, 4.0, "acc")
    for k, (x, h) in enumerate(((-4.0, 4.0), (-2.0, 3.0), (0, 5.0), (2.0, 3.0), (4.0, 4.0))):
        bx(s, x, 3.0, 0, 1.4, h, 1.6, "acc")
        bx(s, x, 3.0 + h, 0, 1.0, 1.0, 1.8, "glow" if k % 2 == 0 else "wrap", glow=k % 2 == 0)
    bx(s, 0, 1.0, 0, 2.0, 1.4, 4.4, "wrap")
    return s


def m_black_pinion():
    s = Sword('black_pinion')                    # a crow-man's flight feather, blue-black
    bx(s, 0, -4, 0, 0.8, 16, 0.8, "acc")
    for k in range(6):
        for side in (1, -1):
            seg(s, (0, -2 + k * 2.0), (side * (2.4 - k * 0.2), -3.4 + k * 2.0), 1.6, 0.4, "dark")
    return s


def m_captains_talon():
    s = Sword('captains_talon')                  # the Rook Captain's talon, hooked and bound in iron
    for k, (x, y, w) in enumerate(((0, 0, 3.0), (0.8, 3.0, 2.4), (1.8, 5.6, 1.8), (3.0, 7.4, 1.2))):
        bx(s, x, y, 0, w, 3.2, w, "acc")
    bx(s, 0, -1.0, 0, 3.6, 1.6, 3.6, "blade")
    return s


def m_raven_mothers_eye():
    s = Sword('raven_mothers_eye')               # the Raven Mother's eye: an omen still looking at you
    bx(s, 0, 0, 0, 7.0, 6.0, 5.0, "glow", glow=True)
    bx(s, 0, 1.6, 0, 2.4, 2.4, 5.4, "void")
    for a in (-30, 0, 30):
        bx(s, 0, 4.0, 0, 1.4, 6.0, 1.0, "dark", rots=(("z", a),), pivot=(0, 4.0, 0))
    return s


def m_greasepaint():
    s = Sword('greasepaint')                     # a pot of white greasepaint, a red thumbprint in it
    bx(s, 0, 0, 0, 7.0, 4.0, 7.0, "dark")
    bx(s, 0, 4.0, 0, 6.0, 0.8, 6.0, "glow")
    bx(s, 1.0, 4.4, 0, 2.0, 0.6, 2.0, "wrap")
    bx(s, 0, 4.8, 0, 7.4, 1.0, 1.0, "acc")
    return s


def m_harlequins_bell():
    s = Sword('harlequins_bell')                 # the Harlequin's bell off its cap
    bx(s, 0, 0, 0, 6.0, 5.0, 6.0, "acc")
    bx(s, 0, 5.0, 0, 3.6, 1.6, 3.6, "acc")
    bx(s, 0, 0.6, 0, 6.4, 0.8, 1.0, "dark")
    ring_xy(s, 0, 7.6, 1.2, 0.5, "acc", 8)
    seg(s, (0, 8.4), (3.0, 12.0), 0.8, 0.8, "wrap")
    return s


def m_ringmasters_top_hat():
    s = Sword('ringmasters_top_hat')             # the Ringmaster's hat, still warm
    bx(s, 0, 0, 0, 12.0, 1.2, 5.0, "dark")
    bx(s, 0, 1.2, 0, 7.6, 8.0, 4.6, "dark")
    bx(s, 0, 1.8, 0, 7.8, 1.6, 4.8, "wrap")
    bx(s, 2.4, 2.0, 0, 1.4, 1.4, 5.0, "acc")
    return s


def m_bog_myrtle():
    s = Sword('bog_myrtle')                      # a sprig of bog myrtle, its berries glowing faintly
    bx(s, 0, -4, 0, 0.8, 14, 0.8, "wood")
    for k in range(4):
        for side in (1, -1):
            seg(s, (0, -1 + k * 2.4), (side * 2.8, 0.2 + k * 2.4), 1.4, 0.5, "wrap")
    for (x, y) in ((-1.2, 9.4), (1.0, 10.0), (0, 10.8)):
        bx(s, x, y, 0, 1.2, 1.2, 1.2, "glow", glow=True)
    return s


def m_matrons_hex_knot():
    s = Sword('matrons_hex_knot')                # the Matron's hex-knot: twigs bound in her hair, still binding
    for a in (0, 45, 90, 135):
        bx(s, 0, -1, 0, 1.0, 11.0, 1.0, "acc", rots=(("z", a),), pivot=(0, 4.5, 0))
    ring_xy(s, 0, 4.5, 3.2, 0.8, "wrap", 12)
    bx(s, 0, 3.8, 0, 2.0, 2.0, 2.0, "glow", glow=True)
    return s


def m_mother_mires_cauldron_heart():
    s = Sword('mother_mires_cauldron_heart')     # the heart of Mother Mire's cauldron: a lump of iron, the brew still in it
    bx(s, 0, 0, 0, 8.0, 6.0, 6.0, "dark")
    bx(s, 0, 6.0, 0, 9.0, 1.2, 6.6, "dark")
    bx(s, 0, 5.4, 0, 6.6, 1.0, 4.4, "glow", glow=True)
    for (x, h) in ((-2.0, 3.0), (1.6, 4.0), (0, 2.2)):
        bx(s, x, 6.6, 0, 1.0, h, 1.0, "glow", glow=True)
    return s


MATS = [("mirefen_coven", m_bog_myrtle), ("mirefen_coven", m_matrons_hex_knot), ("mirefen_coven", m_mother_mires_cauldron_heart),
        ("hollow_circus", m_greasepaint), ("hollow_circus", m_harlequins_bell), ("hollow_circus", m_ringmasters_top_hat),
        ("rookery", m_black_pinion), ("rookery", m_captains_talon), ("rookery", m_raven_mothers_eye),
        ("brigands_gorge", m_stolen_coin), ("brigands_gorge", m_lieutenants_seal), ("brigands_gorge", m_bandit_kings_crown),
        ("weeping_mine", m_weeping_crystal), ("weeping_mine", m_foremans_lamp), ("weeping_mine", m_heart_of_the_vein),
        ("tide_chapel", m_barnacle_crust), ("tide_chapel", m_choir_pearl), ("tide_chapel", m_drowned_bells_clapper)]

import math  # noqa: E402


# ================================================================ the last nine (C, B, A, S)

class SandsunkTomb(Theme):
    def __init__(self):
        super().__init__("sandsunk_tomb",
                         blade=ramp("#2a1a08", "#4a3010", "#6a4818", "#8a6420", "#ae842c", "#d0a840", "#ecc860", "#fff0a0"),
                         dark=ramp("#060c22", "#0c1838", "#142650", "#1e386e", "#2c4e90", "#4068b0"),
                         wrap=ramp("#2e2214", "#42321e", "#58442a", "#6e5838", "#867048"),
                         wood=ramp("#2a160a", "#3e2210", "#563018", "#6e4020", "#86522a", "#a06a36"),
                         glow=ramp("#8a4a0a", "#c4720e", "#f0a020", "#ffc040", "#ffd060", "#ffe8a0", "#fff8e0"),
                         acc=ramp("#3a2606", "#5e400c", "#8a6214", "#b48a24", "#dab43c", "#f4d870"))

    def emblem(self, s, cx, y, size, z, boss):
        # a sun disc between two horns, a lapis ring round it
        ring_xy(s, cx, y, size * 0.45, size * 0.12, "dark", 12, depth=z * 0.6)
        bx(s, cx, y - size * 0.3, 0, size * 0.6, size * 0.6, z, "glow", glow=True)
        for sx in (-1, 1):
            seg(s, (cx + sx * size * 0.3, y + size * 0.2), (cx + sx * size * 0.55, y + size * 0.75), size * 0.12, z * 0.6, "acc")
        if boss:
            for k in range(8):
                a = k * math.pi / 4
                seg(s, (cx + math.cos(a) * size * 0.5, y + math.sin(a) * size * 0.5),
                    (cx + math.cos(a) * size * 0.8, y + math.sin(a) * size * 0.8), size * 0.1, z * 0.5, "acc")

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # linen wound on, a lapis band, a gold bead
        seg(s, (-half - 0.3, y0 + 0.4), (half + 0.3, y0 + 1.6), 0.8, thick + 0.3, "wrap")
        bx(s, 0, y0 + (y1 - y0) * 0.3, 0, half * 2 + 0.4, 0.8, thick + 0.3, "dark", tag="band")


class FallenTitan(Theme):
    def __init__(self):
        super().__init__("fallen_titan",
                         blade=ramp("#3a3026", "#54463a", "#6e5e4e", "#8a7864", "#a6947c", "#c2b096", "#dccab0", "#f0e4cc"),
                         dark=ramp("#1a0606", "#2e0a0a", "#4a1010", "#661a18", "#842620", "#a03428"),
                         wrap=ramp("#3a0e10", "#5a1a1a", "#7a2a26", "#9a3c34", "#b45246"),
                         wood=ramp("#2e2418", "#463828", "#5e4c38", "#786248", "#927a5a", "#ac946e"),
                         glow=ramp("#5a0a0a", "#8a1414", "#c42020", "#ee3a2a", "#ff6a4a", "#ffa08a", "#ffd8cc"),
                         acc=ramp("#4a3a20", "#6a5430", "#8a7044", "#a88c5a", "#c4aa76", "#dcc896"))

    def emblem(self, s, cx, y, size, z, boss):
        # a heart, still beating: a lump of red with veins out of it
        bx(s, cx, y - size * 0.4, 0, size * 0.7, size * 0.8, z, "dark")
        bx(s, cx, y - size * 0.2, 0, size * 0.4, size * 0.4, z * 1.1, "glow", glow=True)
        for a in (40, 140, 260):
            r = math.radians(a)
            seg(s, (cx, y), (cx + math.cos(r) * size * 0.7, y + math.sin(r) * size * 0.7), size * 0.12, z * 0.5, "wrap")
        if boss:
            ring_xy(s, cx, y, size * 0.6, size * 0.1, "acc", 10, depth=z * 0.5)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # sinew lashed round, a knuckle of bone
        seg(s, (-half - 0.3, y0 + 0.4), (half + 0.3, y0 + 2.0), 0.9, thick + 0.3, "wrap")
        bx(s, half + 0.6, y0 + (y1 - y0) * 0.5, 0, 1.4, 1.4, thick + 0.4, "acc", tag="knuckle")


class JadeMonastery(Theme):
    def __init__(self):
        super().__init__("jade_monastery",
                         blade=ramp("#1a2a26", "#2a3e38", "#3e5650", "#567068", "#728c84", "#94aca4", "#bcd0c8", "#e4f0ea"),
                         dark=ramp("#06180e", "#0c2a18", "#144226", "#1e5c36", "#2c7a4a", "#3e9a60"),
                         wrap=ramp("#3a0806", "#5a0e0a", "#7a1810", "#9a2618", "#b83824"),
                         wood=ramp("#1a1008", "#2a1a0e", "#3c2614", "#50341c", "#664426", "#7e5632"),
                         glow=ramp("#0a4a2a", "#127a44", "#22aa60", "#46d080", "#7ae8a6", "#b4f8d0", "#e8fff2"),
                         acc=ramp("#3a2606", "#5e400c", "#8a6214", "#b48a24", "#dab43c", "#f4d870"))

    def emblem(self, s, cx, y, size, z, boss):
        # a jade disc with a hole, a red tassel
        ring_xy(s, cx, y, size * 0.4, size * 0.2, "dark", 12, depth=z)
        seg(s, (cx, y - size * 0.4), (cx, y - size * 1.1), size * 0.14, z * 0.5, "wrap")
        if boss:
            ring_xy(s, cx, y, size * 0.62, size * 0.08, "acc", 14, depth=z * 0.6)
            bx(s, cx, y - size * 0.12, 0, size * 0.24, size * 0.24, z * 1.1, "glow", glow=True)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # red silk cord, a gold cap
        seg(s, (-half - 0.3, y0 + 0.4), (half + 0.3, y0 + 1.4), 0.7, thick + 0.3, "wrap")
        bx(s, 0, y0 + (y1 - y0) * 0.25, 0, half * 2 + 0.4, 0.8, thick + 0.3, "acc", tag="band")


class StormBastion(Theme):
    def __init__(self):
        super().__init__("storm_bastion",
                         blade=ramp("#14181e", "#222830", "#323a44", "#46505c", "#5c6876", "#788694", "#9cabb8", "#cad6e0"),
                         dark=ramp("#0a0e16", "#121a26", "#1c283a", "#283850", "#364a68", "#466084"),
                         wrap=ramp("#141210", "#221e1a", "#322c26", "#443c34", "#584e44"),
                         wood=ramp("#14100c", "#201a14", "#2e261c", "#3e3426", "#504432", "#64563e"),
                         glow=ramp("#1a3a7a", "#2a5ab0", "#4a86e0", "#7ab0ff", "#a8ccff", "#d4e6ff", "#f4faff"),
                         acc=ramp("#2a1e10", "#44301a", "#644824", "#866232", "#a87e42", "#c89c58"))

    def emblem(self, s, cx, y, size, z, boss):
        # a lightning bolt in a brass ring
        ring_xy(s, cx, y, size * 0.5, size * 0.1, "acc", 12, depth=z * 0.6)
        seg(s, (cx + size * 0.15, y + size * 0.4), (cx - size * 0.1, y), size * 0.16, z, "glow", glow=True)
        seg(s, (cx - size * 0.1, y), (cx + size * 0.1, y - size * 0.05), size * 0.16, z, "glow", glow=True)
        seg(s, (cx + size * 0.1, y - size * 0.05), (cx - size * 0.15, y - size * 0.45), size * 0.16, z, "glow", glow=True)
        if boss:
            for sx in (-1, 1):
                seg(s, (cx + sx * size * 0.5, y), (cx + sx * size * 0.85, y + size * 0.2), size * 0.1, z * 0.5, "glow", glow=True)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # copper wire coiled round, a glass stud with a spark in it
        for k in range(3):
            seg(s, (-half - 0.2, y0 + k * 0.9), (half + 0.2, y0 + k * 0.9 + 0.6), 0.4, thick + 0.3, "acc")
        bx(s, half * 0.4, y0 + (y1 - y0) * 0.5, 0, 1.2, 1.2, thick + 0.4, "glow", glow=True)


class BloodmoonCourt(Theme):
    def __init__(self):
        super().__init__("bloodmoon_court",
                         blade=ramp("#14101a", "#221c28", "#342c3a", "#4a4050", "#625868", "#7e7484", "#a49aa8", "#d4ccd6"),
                         dark=ramp("#100206", "#20040c", "#360814", "#520e1e", "#701628", "#902034"),
                         wrap=ramp("#1a0408", "#30080e", "#4a0e16", "#661620", "#82202a"),
                         wood=ramp("#100808", "#1c0e0e", "#2a1414", "#3a1c1c", "#4c2626", "#603030"),
                         glow=ramp("#5a0010", "#8a0a1a", "#c0142a", "#e8283e", "#ff5a6a", "#ff9aa4", "#ffdade"),
                         acc=ramp("#3a2606", "#5e400c", "#8a6214", "#b48a24", "#dab43c", "#f4d870"))

    def emblem(self, s, cx, y, size, z, boss):
        # a blood moon in a gilt bat-wing frame
        bx(s, cx, y - size * 0.3, 0, size * 0.6, size * 0.6, z, "glow", glow=True)
        for sx in (-1, 1):
            seg(s, (cx + sx * size * 0.3, y + size * 0.1), (cx + sx * size * 0.8, y + size * 0.4), size * 0.12, z * 0.6, "acc")
            seg(s, (cx + sx * size * 0.8, y + size * 0.4), (cx + sx * size * 0.7, y - size * 0.1), size * 0.1, z * 0.6, "acc")
        if boss:
            ring_xy(s, cx, y, size * 0.4, size * 0.08, "acc", 10, depth=z * 0.6)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # red velvet wrapped, a gilt cap, a drop of blood
        seg(s, (-half - 0.3, y0 + 0.4), (half + 0.3, y0 + 1.6), 0.8, thick + 0.3, "wrap")
        bx(s, 0, y0 + (y1 - y0) * 0.2, 0, half * 2 + 0.4, 0.8, thick + 0.3, "acc", tag="band")
        bx(s, half * 0.3, y0 + (y1 - y0) * 0.6, 0, 0.8, 1.4, thick + 0.4, "glow", glow=True)


class ObsidianLabyrinth(Theme):
    def __init__(self):
        super().__init__("obsidian_labyrinth",
                         blade=ramp("#06040a", "#0e0a14", "#18121e", "#22192a", "#2e2238", "#3e3048", "#56465e", "#786a80"),
                         dark=ramp("#0e0a08", "#1a1410", "#28201a", "#382e24", "#4a3e32", "#5e5042"),
                         wrap=ramp("#1e0e06", "#341a0a", "#4c2810", "#663816", "#80481e"),
                         wood=ramp("#140c08", "#20140c", "#2e1e12", "#3e2a18", "#50381e", "#644826"),
                         glow=ramp("#8a1a04", "#c43a08", "#f06a10", "#ff9a28", "#ffc05a", "#ffe0a0", "#fff6e0"),
                         acc=ramp("#3a2010", "#5a3418", "#7c4a22", "#a0622e", "#c47e3c", "#e09c50"))

    def emblem(self, s, cx, y, size, z, boss):
        # a bull's horns over a square maze knot, the ember in its heart
        for k in range(4):
            a = k * math.pi / 2 + math.pi / 4
            seg(s, (cx, y), (cx + math.cos(a) * size * 0.45, y + math.sin(a) * size * 0.45), size * 0.14, z * 0.7, "dark")
        bx(s, cx, y - size * 0.15, 0, size * 0.3, size * 0.3, z, "glow", glow=True)
        for sx in (-1, 1):
            seg(s, (cx + sx * size * 0.3, y + size * 0.3), (cx + sx * size * 0.7, y + size * 0.7), size * 0.14, z * 0.6, "acc")
        if boss:
            ring_xy(s, cx, y, size * 0.55, size * 0.08, "glow", 12, glow=True, depth=z * 0.5)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # a cracked seam of ember up the glass, a bronze collar
        bx(s, 0, y0 + 0.4, 0, half * 2 + 0.4, 1.0, thick + 0.3, "acc", tag="band")
        if where in ("blade", "head"):
            seg(s, (-half * 0.3, y0 + 2), (half * 0.2, y1 - 2), 0.5, thick + 0.1, "glow", glow=True)


class AbyssalLighthouse(Theme):
    def __init__(self):
        super().__init__("abyssal_lighthouse",
                         blade=ramp("#0e1416", "#182226", "#243238", "#32444c", "#445a62", "#5a727a", "#7a9298", "#a8bec2"),
                         dark=ramp("#02060a", "#060e16", "#0a1622", "#102030", "#182c40", "#223a52"),
                         wrap=ramp("#1a1a12", "#2a2a1c", "#3c3c28", "#505034", "#646442"),
                         wood=ramp("#14120e", "#201c16", "#2e2820", "#3c362a", "#4c4436", "#5e5444"),
                         glow=ramp("#6a6a2a", "#a0a040", "#d0d060", "#f0f090", "#fafac0", "#fffff0", "#ffffff"),
                         acc=ramp("#1e2a24", "#2e4038", "#40584e", "#547266", "#6a8c7e", "#84a698"))

    def emblem(self, s, cx, y, size, z, boss):
        # a lighthouse lens: a brass ring, a pale light, a beam out of it
        ring_xy(s, cx, y, size * 0.45, size * 0.12, "acc", 12, depth=z * 0.6)
        bx(s, cx, y - size * 0.25, 0, size * 0.5, size * 0.5, z, "glow", glow=True)
        if boss:
            seg(s, (cx + size * 0.4, y), (cx + size * 1.1, y + size * 0.2), size * 0.3, z * 0.4, "glow", glow=True)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # tarred rope, a barnacle, a hook
        seg(s, (-half - 0.3, y0 + 0.4), (half + 0.3, y0 + 1.6), 0.8, thick + 0.3, "wrap")
        bx(s, half + 0.4, y0 + (y1 - y0) * 0.4, 0, 1.2, 1.0, thick + 0.4, "acc", tag="barnacle")


class EclipseCathedral(Theme):
    def __init__(self):
        super().__init__("eclipse_cathedral",
                         blade=ramp("#0a0a0c", "#141418", "#202026", "#2e2e36", "#40404a", "#585862", "#7a7a84", "#a8a8b0"),
                         dark=ramp("#060606", "#0c0c0e", "#141416", "#1e1e22", "#2a2a30", "#383840"),
                         wrap=ramp("#3a3a3e", "#545458", "#6e6e74", "#8a8a90", "#a6a6ac"),
                         wood=ramp("#100e0c", "#1a1814", "#26221c", "#342e26", "#423a30", "#52483c"),
                         glow=ramp("#5a3a0a", "#a06a14", "#e0a020", "#ffd050", "#fff0a0", "#fffad8", "#ffffff"),
                         acc=ramp("#3a2606", "#5e400c", "#8a6214", "#b48a24", "#dab43c", "#f4d870"))

    def emblem(self, s, cx, y, size, z, boss):
        # the eclipse: a black disc with a ring of gold fire round it
        ring_xy(s, cx, y, size * 0.48, size * 0.12, "glow", 14, glow=True, depth=z * 0.7)
        bx(s, cx, y - size * 0.36, 0, size * 0.72, size * 0.72, z, "dark")
        if boss:
            for k in range(12):
                a = k * math.pi / 6
                seg(s, (cx + math.cos(a) * size * 0.55, y + math.sin(a) * size * 0.55),
                    (cx + math.cos(a) * size * 0.85, y + math.sin(a) * size * 0.85), size * 0.08, z * 0.5, "glow", glow=True)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # black-gold leaf, a white feather tied on
        bx(s, 0, y0 + 0.4, 0, half * 2 + 0.4, 1.0, thick + 0.3, "acc", tag="band")
        seg(s, (half + 0.2, y0 + 0.8), (half + 1.6, y0 - 3.0), 0.8, 0.4, "wrap")


class WyrmsHoard(Theme):
    def __init__(self):
        super().__init__("wyrms_hoard",
                         blade=ramp("#1a0e0a", "#2e1810", "#462416", "#62341e", "#824628", "#a45c34", "#c47a48", "#e4a068"),
                         dark=ramp("#0e0606", "#1c0a08", "#2e100c", "#441812", "#5c2218", "#762e20"),
                         wrap=ramp("#1a120a", "#2a1e12", "#3c2c1a", "#503c24", "#664e30"),
                         wood=ramp("#2e2a22", "#46403a", "#605a50", "#7c7468", "#988f82", "#b4ac9e"),
                         glow=ramp("#8a1e04", "#c43c08", "#f06a10", "#ff9a28", "#ffc05a", "#ffe8b0", "#fffbe8"),
                         acc=ramp("#3a2606", "#5e400c", "#8a6214", "#b48a24", "#dab43c", "#f4d870"))

    def emblem(self, s, cx, y, size, z, boss):
        # a dragon's eye in gold: the slit pupil, the ember round it
        bx(s, cx, y - size * 0.35, 0, size * 0.9, size * 0.7, z * 0.8, "acc")
        bx(s, cx, y - size * 0.25, 0, size * 0.6, size * 0.5, z, "glow", glow=True)
        bx(s, cx, y - size * 0.3, 0, size * 0.12, size * 0.6, z * 1.1, "dark")
        if boss:
            for sx in (-1, 1):
                seg(s, (cx + sx * size * 0.45, y + size * 0.2), (cx + sx * size * 0.75, y + size * 0.85), size * 0.14, z * 0.6, "wood")

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # scales overlapping up the grip, a coin set in
        for k in range(3):
            bx(s, 0, y0 + k * 1.2, 0, half * 2 + 0.4 - k * 0.2, 1.0, thick + 0.3, "dark", tag="scale")
        bx(s, half * 0.3, y0 + (y1 - y0) * 0.5, 0, 1.2, 1.2, thick + 0.4, "acc", tag="coin")


THEMES.update({t.gate: t for t in (SandsunkTomb(), FallenTitan(), JadeMonastery(), StormBastion(), BloodmoonCourt(),
                                   ObsidianLabyrinth(), AbyssalLighthouse(), EclipseCathedral(), WyrmsHoard())})

HINTS.update({
    'khopesh': {'shape': 'curved'}, 'scarab_dagger': {'shape': 'leaf'}, 'obelisk_maul': {'shape': 'block'},
    'sunspear': {'shape': 'leaf'}, 'sickle_greatblade': {'shape': 'falchion'}, 'sun_disc_shield': {'shape': 'round'},
    'sunflayer': {'shape': 'curved', 'guard': 'emblem'}, 'solar_aegis': {'shape': 'round'}, 'scarab_fang': {'shape': 'curved'},
    'rib': {'shape': 'curved'}, 'fangs': {'shape': 'curved'}, 'knuckle': {'shape': 'barrel'}, 'femur_spear': {'shape': 'spike'},
    'jawbone': {'shape': 'cleaver'}, 'valve_shield': {'shape': 'round'}, 'aorta': {'shape': 'wavy', 'guard': 'emblem'},
    'heart_valve': {'shape': 'heater'}, 'systole': {'shape': 'spiked'}, 'fang_of_the_titan': {'shape': 'curved'},
    'jade_jian': {'shape': 'straight', 'guard': 'cross'}, 'mantis_knife': {'shape': 'curved'}, 'prayer_hammer': {'shape': 'bell'},
    'crescent_spear': {'shape': 'glaive'}, 'guandao': {'shape': 'falchion'}, 'lotus_shield': {'shape': 'round'},
    'thousand_hand_jian': {'shape': 'straight', 'guard': 'emblem'}, 'lotus_throne': {'shape': 'round'},
    'heavens_guandao': {'shape': 'halberd'}, 'jade_fang': {'shape': 'stiletto'},
    'gale_sabre': {'shape': 'curved', 'guard': 'swept'}, 'spark_knife': {'shape': 'stiletto'}, 'thunder_maul': {'shape': 'block'},
    'lightning_rod_spear': {'shape': 'needle'}, 'stormcleaver': {'shape': 'cleaver'}, 'bastion_shield': {'shape': 'tower'},
    'abbesss_verdict': {'shape': 'straight', 'guard': 'emblem'}, 'lightning_rod_aegis': {'shape': 'kite'},
    'skybreaker': {'shape': 'spiked'}, 'static_fang': {'shape': 'wavy'},
    'court_rapier': {'shape': 'straight', 'guard': 'swept'}, 'fang_dagger': {'shape': 'stiletto'}, 'gilded_mace': {'shape': 'spiked'},
    'partisan': {'shape': 'leaf'}, 'executioners_claymore': {'shape': 'straight'}, 'crest_shield': {'shape': 'heater'},
    'countesss_rapier': {'shape': 'straight', 'guard': 'emblem'}, 'velvet_aegis': {'shape': 'kite'},
    'kingsplitter': {'shape': 'axe'}, 'vaels_fang': {'shape': 'curved'},
    'obsidian_blade': {'shape': 'leaf'}, 'glass_shiv': {'shape': 'wavy'}, 'basalt_maul': {'shape': 'block'},
    'labyrinth_pike': {'shape': 'spike'}, 'ninth_gate_axe': {'shape': 'cleaver'}, 'maze_wall_shield': {'shape': 'tower'},
    'thread_of_the_maze': {'shape': 'straight', 'guard': 'emblem'}, 'ninth_gate': {'shape': 'tower'}, 'labrys': {'shape': 'axe'},
    'horn_shard': {'shape': 'curved'},
    'lightkeeper_sword': {'shape': 'straight', 'guard': 'cross'}, 'lure_knife': {'shape': 'curved'}, 'foghorn_hammer': {'shape': 'bell'},
    'angler_spear': {'shape': 'hook'}, 'leviathan_cleaver': {'shape': 'cleaver'}, 'lens_shield': {'shape': 'round'},
    'lighthouse_edge': {'shape': 'straight', 'guard': 'emblem'}, 'lens_of_the_keeper': {'shape': 'round'},
    'pale_lantern': {'shape': 'barrel'}, 'lure_fang': {'shape': 'curved'},
    'seraph_blade': {'shape': 'straight', 'guard': 'cross'}, 'black_feather': {'shape': 'leaf'}, 'censer_maul': {'shape': 'barrel'},
    'halo_lance': {'shape': 'spike'}, 'eclipse_greatsword': {'shape': 'flamberge'}, 'cathedral_shield': {'shape': 'kite'},
    'fallen_grace': {'shape': 'straight', 'guard': 'emblem'}, 'black_sun_aegis': {'shape': 'round'},
    'ashveil_requiem': {'shape': 'spiked'}, 'last_feather': {'shape': 'stiletto'},
    'drakefang_sword': {'shape': 'falchion'}, 'kobold_shiv': {'shape': 'wavy'}, 'hoard_hammer': {'shape': 'block'},
    'drake_lance': {'shape': 'spike'}, 'wyrmcleaver': {'shape': 'cleaver'}, 'gold_heap_shield': {'shape': 'round'},
    'ignavars_claw': {'shape': 'curved', 'guard': 'emblem'}, 'scale_of_ignavar': {'shape': 'heater'},
    'hoardbreaker': {'shape': 'spiked'}, 'wyrm_tooth': {'shape': 'curved'},
})


# ---------------------------------------------------------------- the last nine's drops

def _m(name):
    return Sword(name)


def m_tomb_linen():
    s = _m('tomb_linen')                         # a fold of tomb linen, resin-stiff, a gold thread through it
    for k in range(4):
        bx(s, 0, -4 + k * 2.6, 0, 9.0 - k * 0.6, 2.2, 1.4, "wrap")
    seg(s, (-4, -3), (4, 6), 0.5, 1.6, "acc")
    return s


def m_guardians_ankh():
    s = _m('guardians_ankh')                     # the Guardian's ankh, still warm
    bx(s, 0, -6, 0, 2.0, 9.0, 1.6, "acc")
    bx(s, 0, 2.2, 0, 8.0, 1.8, 1.6, "acc")
    ring_xy(s, 0, 6.2, 2.4, 1.0, "acc", 12)
    bx(s, 0, 5.6, 0, 1.6, 1.6, 1.8, "glow", glow=True)
    return s


def m_sun_kings_scarab():
    s = _m('sun_kings_scarab')                   # the Sun-King's scarab: lapis and gold, a sun burning in its claws
    bx(s, 0, -4, 0, 7.0, 7.0, 2.4, "dark")
    bx(s, 0, -4, 0, 0.6, 7.0, 2.6, "acc")
    for sx in (-1, 1):
        seg(s, (sx * 3.4, 0), (sx * 6, 3), 1.6, 1.6, "acc")
    bx(s, 0, 3.6, 0, 4.0, 4.0, 2.0, "glow", glow=True)
    return s


def m_titan_sinew():
    s = _m('titan_sinew')                        # a coil of the titan's sinew, still twitching
    ring_xy(s, 0, 0, 4.0, 1.6, "wrap", 14)
    ring_xy(s, 0.6, 0.4, 2.4, 1.2, "wrap", 10)
    bx(s, 3.6, -1.0, 0, 1.6, 2.0, 1.6, "glow", glow=True)
    return s


def m_valve_shard():
    s = _m('valve_shard')                        # a shard of heart valve, bone-white, a red seam
    seg(s, (-4, -5), (3, 6), 4.0, 1.4, "blade")
    seg(s, (-2, -3), (2, 4), 0.6, 1.6, "glow", glow=True)
    return s


def m_heartstring():
    s = _m('heartstring')                        # the Still Heart's last string, pulled taut and glowing
    seg(s, (-5, -5), (5, 5), 0.8, 0.8, "glow", glow=True)
    for (x, y) in ((-5, -5), (5, 5)):
        bx(s, x, y - 1.4, 0, 2.6, 2.6, 2.0, "dark")
    return s


def m_jade_bead():
    s = _m('jade_bead')                          # a prayer bead of jade on a red cord
    ring_xy(s, 0, 0, 3.0, 2.4, "dark", 12)
    seg(s, (0, 3), (0, 8), 0.6, 0.6, "wrap")
    return s


def m_abbots_prayer_wheel():
    s = _m('abbots_prayer_wheel')                # the Abbot's prayer wheel: a gold drum on a handle, the sutra glowing
    bx(s, 0, -8, 0, 1.2, 8.0, 1.2, "wood")
    bx(s, 0, 0, 0, 7.0, 7.0, 4.0, "acc")
    for y in (1.6, 3.6, 5.2):
        bx(s, 0, y, 0, 7.4, 0.6, 4.2, "glow", glow=True)
    return s


def m_thousand_hands_seal():
    s = _m('thousand_hands_seal')                # the seal of the Thousand Hands: a jade block, a hand carved in it
    bx(s, 0, -5, 0, 8.0, 8.0, 3.0, "dark")
    for x in (-2.4, -0.8, 0.8, 2.4):
        bx(s, x, -1, 0, 1.0, 4.0, 3.2, "glow", glow=True)
    bx(s, 0, -3.6, 0, 6.0, 2.4, 3.2, "glow", glow=True)
    return s


def m_storm_glass():
    s = _m('storm_glass')                        # a vial of storm glass, a bolt caught in it
    bx(s, 0, -5, 0, 4.0, 10.0, 4.0, "blade")
    seg(s, (0.6, 4), (-0.6, 0), 0.8, 4.2, "glow", glow=True)
    seg(s, (-0.6, 0), (0.6, -4), 0.8, 4.2, "glow", glow=True)
    bx(s, 0, 5, 0, 3.0, 1.6, 3.0, "acc")
    return s


def m_captains_rod():
    s = _m('captains_rod')                       # the Storm Captain's rod: brass, a copper coil, a spark at the tip
    bx(s, 0, -8, 0, 1.4, 14.0, 1.4, "acc")
    for y in (-2, -1, 0, 1):
        bx(s, 0, y, 0, 2.6, 0.5, 2.6, "wrap")
    bx(s, 0, 6, 0, 2.0, 2.0, 2.0, "glow", glow=True)
    return s


def m_abbesss_bell():
    s = _m('abbesss_bell')                       # the Thunder Abbess's handbell, ringing still
    bx(s, 0, -6, 0, 8.0, 2.0, 4.0, "acc")
    bx(s, 0, -4, 0, 6.0, 5.0, 3.6, "acc")
    bx(s, 0, 1, 0, 4.0, 2.0, 3.0, "acc")
    bx(s, 0, 3, 0, 1.2, 4.0, 1.2, "wood")
    bx(s, 0, -7, 0, 1.6, 1.6, 1.6, "glow", glow=True)
    return s


def m_blood_velvet():
    s = _m('blood_velvet')                       # a fold of blood-red velvet, a gilt fringe
    for k in range(3):
        bx(s, 0, -4 + k * 3, 0, 9.0 - k, 2.8, 1.4, "wrap")
    bx(s, 0, -5, 0, 9.0, 0.8, 1.6, "acc")
    return s


def m_hounds_collar():
    s = _m('hounds_collar')                      # the Count's hound's collar: black leather, gilt spikes
    ring_xy(s, 0, 0, 4.0, 1.4, "dark", 14)
    for k in range(6):
        a = k * math.pi / 3
        seg(s, (math.cos(a) * 4.0, math.sin(a) * 4.0), (math.cos(a) * 6.0, math.sin(a) * 6.0), 0.8, 1.2, "acc")
    return s


def m_countess_vaels_heart():
    s = _m('countess_vaels_heart')               # the Countess's heart, in a gilt cage, still beating
    bx(s, 0, -4, 0, 6.0, 7.0, 4.0, "glow", glow=True)
    for x in (-3.4, 0, 3.4):
        bx(s, x, -5, 0, 0.6, 9.0, 4.6, "acc")
    bx(s, 0, 4.4, 0, 2.0, 2.0, 2.0, "acc")
    return s


def m_obsidian_shard():
    s = _m('obsidian_shard')                     # a knapped shard of obsidian, an ember in its heart
    seg(s, (-2, -6), (2, 6), 4.0, 2.0, "blade")
    bx(s, 0, -1, 0, 1.4, 2.0, 2.2, "glow", glow=True)
    return s


def m_gatekeepers_key():
    s = _m('gatekeepers_key')                    # the Gatekeeper's key: black bronze, a maze for its bit
    bx(s, 0, -6, 0, 1.4, 10.0, 1.4, "acc")
    ring_xy(s, 0, 6, 2.6, 1.0, "acc", 12)
    for (x, y) in ((1.6, -6), (2.6, -5), (1.6, -3.6)):
        bx(s, x, y, 0, 1.2, 1.0, 1.4, "acc")
    bx(s, 0, 5.4, 0, 1.4, 1.4, 1.6, "glow", glow=True)
    return s


def m_minotaurs_horn():
    s = _m('minotaurs_horn')                     # the Minotaur's horn, ember-cracked
    seg(s, (-4, -5), (0, 2), 3.0, 3.0, "wood")
    seg(s, (0, 2), (3, 7), 2.0, 2.0, "wood")
    seg(s, (-3, -3), (1, 3), 0.5, 3.2, "glow", glow=True)
    return s


def m_deep_pearl():
    s = _m('deep_pearl')                         # a pearl from the abyss, faintly lit
    bx(s, 0, -3, 0, 6.0, 6.0, 6.0, "glow", glow=True)
    bx(s, 0, -3.6, 0, 7.0, 1.0, 7.0, "acc")
    return s


def m_anglers_lure():
    s = _m('anglers_lure')                       # the Angler Knight's lure: a stalk, a bulb of light
    seg(s, (-3, -6), (0, 4), 1.2, 1.2, "wrap")
    seg(s, (0, 4), (3, 5), 1.0, 1.0, "wrap")
    bx(s, 3.4, 2.4, 0, 3.0, 3.0, 3.0, "glow", glow=True)
    return s


def m_keepers_lens():
    s = _m('keepers_lens')                       # the Keeper's lens: brass-rimmed glass, the light still in it
    ring_xy(s, 0, 0, 5.0, 1.4, "acc", 16)
    bx(s, 0, -3.6, 0, 7.0, 7.0, 1.0, "glow", glow=True)
    return s


def m_black_gold_leaf():
    s = _m('black_gold_leaf')                    # a sheet of black gold leaf, scorched at the edges
    bx(s, 0, -5, 0, 8.0, 10.0, 0.6, "acc")
    bx(s, 0, -5.2, 0, 8.4, 1.0, 0.8, "dark")
    bx(s, 3.6, -4, 0, 1.0, 8.0, 0.8, "dark")
    return s


def m_seraph_feather():
    s = _m('seraph_feather')                     # a seraph's feather, ash-white, burning at the tip
    seg(s, (0, -7), (0, 7), 0.6, 0.6, "wrap")
    for k in range(5):
        for sx in (-1, 1):
            seg(s, (0, -4 + k * 2.4), (sx * 2.6, -2 + k * 2.4), 1.2, 0.5, "wrap")
    bx(s, 0, 6.4, 0, 1.8, 1.8, 1.0, "glow", glow=True)
    return s


def m_fallen_seraphs_halo():
    s = _m('fallen_seraphs_halo')                # the Fallen Seraph's halo, broken, still burning
    ring_xy(s, 0, 0, 5.4, 1.2, "glow", 18, glow=True)
    bx(s, 4.0, -1, 0, 2.0, 2.0, 1.6, "dark")
    return s


def m_hoard_gold():
    s = _m('hoard_gold')                         # a fistful of hoard coin, fused by dragonfire
    for (x, y) in ((-2, -3), (1.6, -2.4), (-0.4, 0.4), (2.2, 1.6), (-2.4, 2.0)):
        bx(s, x, y, 0, 3.6, 1.0, 3.6, "acc")
    bx(s, 0, -1, 0, 1.4, 1.4, 4.0, "glow", glow=True)
    return s


def m_wyrm_priests_scale():
    s = _m('wyrm_priests_scale')                 # a scale the Wyrm Priest wore as a mask
    seg(s, (0, -6), (0, 6), 8.0, 1.2, "dark")
    seg(s, (0, -4), (0, 4), 4.0, 1.4, "blade")
    return s


def m_ignavars_heart_ember():
    s = _m('ignavars_heart_ember')               # an ember from Ignavar's heart, too hot to hold for long
    bx(s, 0, -4, 0, 7.0, 7.0, 5.0, "dark")
    bx(s, 0, -3, 0, 5.0, 5.0, 5.4, "glow", glow=True)
    for (x, y) in ((-3, 3), (2, 4)):
        bx(s, x, y, 0, 1.0, 2.0, 1.0, "glow", glow=True)
    return s


MATS += [("sandsunk_tomb", m_tomb_linen), ("sandsunk_tomb", m_guardians_ankh), ("sandsunk_tomb", m_sun_kings_scarab),
         ("fallen_titan", m_titan_sinew), ("fallen_titan", m_valve_shard), ("fallen_titan", m_heartstring),
         ("jade_monastery", m_jade_bead), ("jade_monastery", m_abbots_prayer_wheel), ("jade_monastery", m_thousand_hands_seal),
         ("storm_bastion", m_storm_glass), ("storm_bastion", m_captains_rod), ("storm_bastion", m_abbesss_bell),
         ("bloodmoon_court", m_blood_velvet), ("bloodmoon_court", m_hounds_collar), ("bloodmoon_court", m_countess_vaels_heart),
         ("obsidian_labyrinth", m_obsidian_shard), ("obsidian_labyrinth", m_gatekeepers_key), ("obsidian_labyrinth", m_minotaurs_horn),
         ("abyssal_lighthouse", m_deep_pearl), ("abyssal_lighthouse", m_anglers_lure), ("abyssal_lighthouse", m_keepers_lens),
         ("eclipse_cathedral", m_black_gold_leaf), ("eclipse_cathedral", m_seraph_feather), ("eclipse_cathedral", m_fallen_seraphs_halo),
         ("wyrms_hoard", m_hoard_gold), ("wyrms_hoard", m_wyrm_priests_scale), ("wyrms_hoard", m_ignavars_heart_ember)]


# ================================================================ world towers (docs/TOWERS.md)

class ClockworkSpire(Theme):
    def __init__(self):
        super().__init__("clockwork_spire",
                         blade=ramp("#0e1012", "#1a1d22", "#282c32", "#383e46", "#4c535c", "#666e78", "#8a929c", "#b8c0c8"),
                         dark=ramp("#0a0b0d", "#121418", "#1b1e23", "#262a30", "#33383f", "#434952"),
                         wrap=ramp("#120c08", "#1c140e", "#281c14", "#36261a", "#463222"),
                         wood=ramp("#1a1008", "#2a1a0c", "#3e2812", "#56391a", "#704c22", "#8c622c"),
                         glow=ramp("#7a3a08", "#b45c10", "#e08a1e", "#ffb53a", "#ffd77a", "#fff2c4", "#fffbee"),
                         acc=ramp("#2a1806", "#4a2c0c", "#6e4616", "#966222", "#bc8434", "#dcaa52"))

    def emblem(self, s, cx, y, size, z, boss):
        # a cog in brass round a burning hub
        ring_xy(s, cx, y, size * 0.45, size * 0.12, "acc", 12, depth=z * 0.7)
        for k in range(8):
            a = k * math.pi / 4
            bx(s, cx + math.cos(a) * size * 0.6, y + math.sin(a) * size * 0.6 - size * 0.08, 0, size * 0.16, size * 0.16, z * 0.7, "acc")
        bx(s, cx, y - size * 0.12, 0, size * 0.24, size * 0.24, z * 1.1, "glow", glow=True)
        if boss:
            seg(s, (cx, y), (cx + size * 0.3, y + size * 0.35), size * 0.07, z * 1.2, "dark")
            seg(s, (cx, y), (cx - size * 0.2, y + size * 0.15), size * 0.09, z * 1.2, "dark")

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # brass collars with rivets, a gauge lamp
        for k in range(2):
            bx(s, 0, y0 + k * 1.6, 0, half * 2 + 0.6, 0.7, thick + 0.4, "acc", tag="band")
        bx(s, half * 0.4, y0 + (y1 - y0) * 0.55, 0, 1.0, 1.0, thick + 0.4, "glow", glow=True)


THEMES["clockwork_spire"] = ClockworkSpire()

HINTS.update({
    'cogblade': {'shape': 'straight', 'guard': 'emblem'}, 'escapement_dagger': {'shape': 'stiletto'},
    'piston_maul': {'shape': 'block'}, 'governor_pike': {'shape': 'halberd'}, 'gearbreaker': {'shape': 'cleaver'},
    'riveted_bulwark': {'shape': 'tower'}, 'horologes_hand': {'shape': 'needle', 'guard': 'emblem'},
    'dial_of_hours': {'shape': 'round'}, 'mainspring_hammer': {'shape': 'spiked'}, 'second_hand': {'shape': 'stiletto'},
})


def m_brass_cog():
    s = _m('brass_cog')                          # a brass cog off a broken automaton, a tooth or two missing
    ring_xy(s, 0, 0, 4.4, 1.4, "acc", 12, depth=2.0)
    for k in range(10):
        if k in (3, 7):
            continue
        a = k * 2 * math.pi / 10
        bx(s, math.cos(a) * 5.6, math.sin(a) * 5.6 - 0.8, 0, 1.6, 1.6, 2.0, "acc")
    bx(s, 0, -1.2, 0, 2.4, 2.4, 2.4, "dark")
    return s


def m_mainspring():
    s = _m('mainspring')                         # a coiled mainspring from a Duelist's chest, still taut and warm
    n = 40
    for i in range(n):
        a0, a1 = i * 0.42, (i + 1) * 0.42
        r0, r1 = 1.0 + i * 0.13, 1.0 + (i + 1) * 0.13
        seg(s, (math.cos(a0) * r0, math.sin(a0) * r0), (math.cos(a1) * r1, math.sin(a1) * r1), 0.8, 1.6,
            "glow" if i > n - 8 else "blade", glow=i > n - 8)
    bx(s, 0, -0.8, 0, 1.6, 1.6, 2.0, "acc")
    return s


def m_horologes_heart():
    s = _m('horologes_heart')                    # the Grand Horologe's heart: an escapement in a brass cage, burning
    bx(s, 0, -4, 0, 7.0, 7.0, 5.0, "dark")
    bx(s, 0, -3, 0, 5.0, 5.0, 5.4, "glow", glow=True)
    ring_xy(s, 0, -0.5, 4.6, 0.8, "acc", 14, depth=5.8)
    for sx in (-1, 1):
        seg(s, (sx * 4.6, -0.5), (sx * 1.0, 5.0), 0.8, 2.0, "acc")
    bx(s, 0, 4.6, 0, 2.0, 2.0, 2.0, "acc")
    return s


MATS += [("clockwork_spire", m_brass_cog), ("clockwork_spire", m_mainspring), ("clockwork_spire", m_horologes_heart)]


# ================================================================ the four towers after the Spire (docs/TOWERS.md)

class SerpentZiggurat(Theme):
    def __init__(self):
        super().__init__("serpent_ziggurat",
                         blade=ramp("#060608", "#0e0e16", "#181826", "#242436", "#32324a", "#464660", "#62627e", "#8c8caa"),
                         dark=ramp("#070c0a", "#0e1712", "#16231a", "#203222", "#2c442c", "#3c5a36"),
                         wrap=ramp("#1a0606", "#2c0a08", "#44100c", "#5e1a12", "#78261a"),
                         wood=ramp("#04140e", "#0a2418", "#123a26", "#1c5636", "#2a7446", "#42945a"),
                         glow=ramp("#063a16", "#0e6a28", "#1ea840", "#4ae064", "#a0ff90", "#d8ffd0", "#f4fff0"),
                         acc=ramp("#2a1804", "#4c300a", "#7a5014", "#a87422", "#d0a034", "#f0cc5a"))

    def emblem(self, s, cx, y, size, z, boss):
        # a cobra's hood in jade round a venom eye, gold at its rim
        for k in range(6):
            t = k / 5
            w = size * (0.5 + 0.5 * math.sin(t * math.pi * 0.8))
            bx(s, cx, y - size * 0.5 + k * size * 0.2, 0, w, size * 0.21, z * 0.8, "wood" if k % 2 else "acc")
        bx(s, cx, y - size * 0.05, 0, size * 0.24, size * 0.3, z * 1.1, "glow", glow=True)
        if boss:
            for sx in (-1, 1):
                seg(s, (cx + sx * size * 0.2, y - size * 0.55), (cx + sx * size * 0.12, y - size * 0.95), size * 0.08, z * 0.8, "white")

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # a serpent wound round the grip in jade, a gold band at the top
        for k in range(4):
            bx(s, 0, y0 + k * 1.3, 0, half * 2 + 0.5 - (k % 2) * 0.3, 0.8, thick + 0.4, "wood" if k % 2 else "dark", tag="coil")
        bx(s, 0, y1 - 0.8, 0, half * 2 + 0.6, 0.7, thick + 0.5, "acc", tag="band")


class Rimeholt(Theme):
    def __init__(self):
        super().__init__("rimeholt",
                         blade=ramp("#0e1218", "#1a2028", "#28303a", "#3a4450", "#506070", "#6c8092", "#94aabe", "#c8dcec"),
                         dark=ramp("#08090c", "#101318", "#191d24", "#232831", "#2e343f", "#3c4350"),
                         wrap=ramp("#1a1a1e", "#2a2a30", "#3c3c44", "#52525c", "#6c6c76"),
                         wood=ramp("#0c0a08", "#16110d", "#211913", "#2d2219", "#3b2d21", "#4c3a2a"),
                         glow=ramp("#0a2a5a", "#14508e", "#2a84c8", "#5ab8f4", "#a0e0ff", "#d8f4ff", "#f4fcff"),
                         acc=ramp("#1e1206", "#34200c", "#523414", "#704a1e", "#8e6228", "#ae7e38"))

    def emblem(self, s, cx, y, size, z, boss):
        # a rune burned in black iron: a stave and two arms up, ice in the cut
        bx(s, cx, y - size * 0.5, 0, size * 0.2, size, z * 0.8, "dark")
        bx(s, cx, y - size * 0.45, 0, size * 0.1, size * 0.9, z * 1.0, "glow", glow=True)
        for sx in (-1, 1):
            seg(s, (cx, y + size * 0.15), (cx + sx * size * 0.4, y + size * 0.45), size * 0.1, z * 0.9, "glow", glow=True)
        if boss:
            for sx in (-1, 1):
                seg(s, (cx + sx * size * 0.3, y - size * 0.3), (cx + sx * size * 0.6, y + size * 0.6), size * 0.14, z * 0.7, "blade")

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # leather wraps, frost at the top
        for k in range(3):
            bx(s, 0, y0 + k * 1.4, 0, half * 2 + 0.4, 0.7, thick + 0.3, "wrap", tag="wrap")
        bx(s, 0, y1 - 0.6, 0, half * 2 + 0.6, 0.6, thick + 0.5, "white", tag="frost")


class GlassMinaret(Theme):
    def __init__(self):
        super().__init__("glass_minaret",
                         blade=ramp("#1c222c", "#343c4a", "#545e6e", "#7c8a9a", "#a8b6c6", "#d4e0ec", "#eef6fc", "#ffffff"),
                         dark=ramp("#04282a", "#0a4446", "#106464", "#1a8682", "#2aaaa0", "#52ccbe"),
                         wrap=ramp("#200408", "#3a080e", "#5a0e16", "#7e1620", "#a42230"),
                         wood=ramp("#4a3a24", "#6a5434", "#8a7048", "#a88c5e", "#c4a878", "#dcc496"),
                         glow=ramp("#5a1a04", "#9a3a08", "#d8680e", "#ff9a1c", "#ffd04a", "#fff4c0", "#fffcee"),
                         acc=ramp("#2a1804", "#4c300a", "#7a5014", "#a87422", "#d0a034", "#f0cc5a"))

    def emblem(self, s, cx, y, size, z, boss):
        # a sun in gold, its rays round it
        ring_xy(s, cx, y, size * 0.36, size * 0.1, "acc", 12, depth=z * 0.8)
        bx(s, cx, y - size * 0.18, 0, size * 0.36, size * 0.36, z * 1.1, "glow", glow=True)
        for k in range(8):
            a = k * math.pi / 4
            bx(s, cx + math.cos(a) * size * 0.55, y + math.sin(a) * size * 0.55 - size * 0.06, 0, size * 0.12, size * 0.12, z * 0.7, "acc")
        if boss:
            for k in range(5):
                a = math.pi * (1.1 + k * 0.2)
                bx(s, cx + math.cos(a) * size * 0.8, y + math.sin(a) * size * 0.8, 0, size * 0.18, size * 0.18, z * 0.8, "dark")

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # crimson silk wound tight, a turquoise bead, a gold cap
        for k in range(3):
            bx(s, 0, y0 + k * 1.2, 0, half * 2 + 0.4, 0.8, thick + 0.3, "wrap", tag="silk")
        bx(s, half * 0.4, y0 + (y1 - y0) * 0.5, 0, 1.0, 1.0, thick + 0.5, "dark", tag="bead")
        bx(s, 0, y1 - 0.7, 0, half * 2 + 0.6, 0.7, thick + 0.5, "acc", tag="cap")


class WarlordsFang(Theme):
    def __init__(self):
        super().__init__("warlords_fang",
                         blade=ramp("#100a08", "#1e120c", "#2e1a12", "#402418", "#542e1c", "#6c3c22", "#885030", "#a8683e"),
                         dark=ramp("#0a0a0c", "#141418", "#1e1e24", "#2a2a32", "#383842", "#4a4a56"),
                         wrap=ramp("#1e140c", "#2e1e12", "#40281a", "#543622", "#6a462c"),
                         wood=ramp("#3a3428", "#5c5444", "#827a64", "#a8a088", "#cec6ac", "#ece6d0"),   # bone
                         glow=ramp("#4a0e04", "#8a1e06", "#c83a0a", "#ff6a1a", "#ffa040", "#ffe0a0", "#fff4e0"),
                         acc=ramp("#3a0604", "#5a0a06", "#7e1208", "#a01c0c", "#c02a12", "#d84a26"))

    def emblem(self, s, cx, y, size, z, boss):
        # a tusked skull, embers in its eyes
        bx(s, cx, y - size * 0.45, 0, size * 0.7, size * 0.6, z * 0.8, "wood")
        for sx in (-1, 1):
            bx(s, cx + sx * size * 0.17, y - size * 0.2, 0, size * 0.16, size * 0.16, z * 1.0, "glow", glow=True)
            seg(s, (cx + sx * size * 0.2, y - size * 0.45), (cx + sx * size * 0.3, y - size * 0.1), size * 0.08, z * 1.0, "wood")
        bx(s, cx, y - size * 0.62, 0, size * 0.5, size * 0.08, z * 1.0, "dark")
        if boss:
            for k in range(4):
                seg(s, (cx - size * 0.3 + k * size * 0.2, y + size * 0.15), (cx - size * 0.35 + k * size * 0.23, y + size * 0.6), size * 0.1, z * 1.1, "acc")

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # raw hide lashed on, a red rag knotted round, a nail through it
        for k in range(3):
            bx(s, 0, y0 + k * 1.3, 0, half * 2 + 0.5 - (k % 2) * 0.3, 0.8, thick + 0.3, "wrap", tag="hide")
        bx(s, half * 0.5, y0 + (y1 - y0) * 0.45, 0, 1.2, 1.6, thick + 0.4, "acc", tag="rag")
        bx(s, -half * 0.3, y1 - 1.0, 0, 0.6, 0.6, thick + 0.8, "dark", tag="nail")


THEMES.update({t.gate: t for t in (SerpentZiggurat(), Rimeholt(), GlassMinaret(), WarlordsFang())})

HINTS.update({
    'scaleblade': {'shape': 'leaf', 'guard': 'emblem'}, 'jaguar_claw': {'shape': 'hook'}, 'obsidian_club': {'shape': 'spiked'},
    'coil_spear': {'shape': 'leaf'}, 'macuahuitl': {'shape': 'cleaver'}, 'feathered_shield': {'shape': 'round'},
    'kings_fang': {'shape': 'curved', 'guard': 'emblem'}, 'disc_of_the_coil': {'shape': 'round'},
    'serpent_glaive': {'shape': 'glaive'}, 'venom_kiss': {'shape': 'wavy'},
    'rimeblade': {'shape': 'straight', 'guard': 'cross'}, 'icefang_knife': {'shape': 'stiletto'}, 'hoarfrost_maul': {'shape': 'block'},
    'huskarl_spear': {'shape': 'leaf'}, 'frostbeard_axe': {'shape': 'axe'}, 'huskarl_roundshield': {'shape': 'round'},
    'jarls_edge': {'shape': 'straight', 'guard': 'emblem'}, 'rimewall': {'shape': 'tower'},
    'hrimgars_greataxe': {'shape': 'axe'}, 'icicle': {'shape': 'needle'},
    'sunscimitar': {'shape': 'curved', 'guard': 'swept'}, 'dancers_kris': {'shape': 'wavy'}, 'glass_maul': {'shape': 'bell'},
    'minaret_lance': {'shape': 'spike'}, 'dune_cleaver': {'shape': 'falchion'}, 'mirror_shield': {'shape': 'round'},
    'sultans_scimitar': {'shape': 'curved', 'guard': 'emblem'}, 'mirror_of_noon': {'shape': 'round'},
    'djinnblade': {'shape': 'curved'}, 'four_fangs': {'shape': 'curved'},
    'orc_cleaver': {'shape': 'falchion'}, 'goblin_shank': {'shape': 'hook'}, 'spiked_club': {'shape': 'spiked'},
    'warg_spear': {'shape': 'halberd'}, 'tusk_greataxe': {'shape': 'axe'}, 'bone_shield': {'shape': 'kite'},
    'gorraks_chopper': {'shape': 'cleaver', 'guard': 'emblem'}, 'war_door': {'shape': 'tower'},
    'skullsplitter': {'shape': 'spiked'}, 'backstabber': {'shape': 'stiletto'},
})


def m_jade_scale():
    s = _m('jade_scale')                         # a scale off a Scaleguard, jade-green, its edge gone gold
    for k, w in enumerate((3.0, 6.0, 7.4, 7.0, 5.6, 3.4)):
        bx(s, 0, -6 + k * 2.0, 0, w, 2.05, 1.6, "wood" if k % 2 else "dark")
    seg(s, (0, -6), (0, 5), 0.6, 1.8, "acc")
    return s


def m_champions_plume():
    s = _m('champions_plume')                    # a quetzal plume from the Feathered Champion's wings
    seg(s, (-3, -7), (3, 7), 0.8, 0.8, "acc")
    for k in range(7):
        t = k / 6
        x, y = -3 + 6 * t, -7 + 14 * t
        seg(s, (x, y), (x - 2.4 + t, y + 1.6), 1.6 - t * 0.6, 0.8, "wood" if k < 5 else "wrap")
        seg(s, (x, y), (x + 2.4 - t, y - 0.6), 1.6 - t * 0.6, 0.8, "wood" if k < 5 else "wrap")
    return s


def m_coiled_kings_fang():
    s = _m('coiled_kings_fang')                  # a fang out of the Coiled King's jaws, venom still beading on it
    for k, w in enumerate((4.0, 3.6, 3.0, 2.4, 1.6, 1.0)):
        bx(s, k * 0.4, 6 - k * 2.2, 0, w, 2.25, w, "white")
    bx(s, 0, 6, 0, 4.6, 2.0, 4.6, "acc")
    bx(s, 2.2, -6, 0, 1.4, 1.4, 1.4, "glow", glow=True)
    return s


def m_hrimstone():
    s = _m('hrimstone')                          # a crystal of hrimstone grown out of the keep's walls
    for k, (x, h, w) in enumerate(((0, 12, 3.6), (-3.0, 8, 2.6), (3.0, 7, 2.4))):
        bx(s, x, -6, 0, w, h, w, "glow", glow=True)
        bx(s, x, -6 + h, 0, w * 0.6, 1.6, w * 0.6, "white")
    bx(s, 0, -7, 0, 9.0, 1.6, 4.0, "dark")
    return s


def m_winter_wolf_pelt():
    s = _m('winter_wolf_pelt')                   # a fold of the Winter Wolf's pelt, frost in the fur
    for k in range(5):
        bx(s, 0, -6 + k * 2.6, 0, 10 - abs(k - 2) * 1.4, 2.7, 2.4, "blade" if k % 2 else "wrap")
    for x in (-3, 0, 3):
        bx(s, x, 5.4, 0, 1.0, 2.0, 2.6, "glow", glow=True)
    return s


def m_hrimgars_frozen_heart():
    s = _m('hrimgars_frozen_heart')              # the frost giant's heart, frozen solid, a rune still burning in it
    bx(s, 0, -5, 0, 8.0, 9.0, 6.0, "blade")
    bx(s, 0, -3, 0, 5.0, 5.4, 6.4, "glow", glow=True)
    seg(s, (0, -2), (0, 3), 0.8, 6.8, "dark")
    for sx in (-1, 1):
        seg(s, (0, 1.5), (sx * 2.0, 3.0), 0.7, 6.8, "dark")
        seg(s, (sx * 2.4, 4.0), (sx * 3.4, 7.4), 1.4, 2.0, "white")
    return s


def m_sun_glass():
    s = _m('sun_glass')                          # a lump of sun glass, lightning-fused, the sun still in it
    for (x, y, w, h) in ((0, -5, 7, 8), (-3, -2, 4, 7), (3, -3, 4, 6)):
        bx(s, x, y, 0, w, h, 3.6, "glow", glow=True)
    bx(s, 0, -6, 0, 8.4, 1.6, 4.0, "wood")
    return s


def m_dancers_bell():
    s = _m('dancers_bell')                       # a gold bell off the Blade Dancer's anklet, on a scrap of crimson silk
    seg(s, (-2, 7), (2, 4), 1.4, 1.0, "wrap")
    for k, w in enumerate((2.4, 4.0, 5.4, 6.4)):
        bx(s, 0, 2 - k * 1.8, 0, w, 1.9, w, "acc")
    bx(s, 0, -5.6, 0, 1.4, 1.4, 1.4, "glow", glow=True)
    return s


def m_sultans_lamp():
    s = _m('sultans_lamp')                       # the Sultan's Lamp, emptied - but warm, and humming
    bx(s, 0, -6, 0, 4.0, 1.6, 4.0, "acc")
    for k, w in enumerate((6.0, 9.0, 10.0, 8.0)):
        bx(s, 0, -4.4 + k * 1.6, 0, w, 1.65, w * 0.7, "acc")
    seg(s, (4.4, -1.0), (8.0, 2.4), 1.6, 1.6, "acc")
    bx(s, 0, 2.0, 0, 3.0, 2.0, 3.0, "acc")
    bx(s, 8.0, 2.4, 0, 1.4, 1.4, 1.4, "glow", glow=True)
    bx(s, 0, -2.4, 0, 2.0, 1.4, 7.6, "dark")
    return s


def m_orc_tusk():
    s = _m('orc_tusk')                           # an orc's tusk, a brass ring still on it
    for k, w in enumerate((3.6, 3.2, 2.8, 2.2, 1.6, 1.0)):
        bx(s, -k * 0.5, -6 + k * 2.2, 0, w, 2.25, w, "wood")
    bx(s, -0.6, -2.6, 0, 3.8, 1.2, 3.8, "acc")
    return s


def m_warg_fang():
    s = _m('warg_fang')                          # a warg's fang on a thong of hide
    seg(s, (-4, 6), (4, 6), 0.8, 0.8, "wrap")
    for k, w in enumerate((3.0, 2.4, 1.8, 1.2)):
        bx(s, 0, 4 - k * 2.6, 0, w, 2.65, w, "wood")
    bx(s, 0, 5.0, 0, 3.6, 1.4, 3.6, "wrap")
    return s


def m_gorraks_war_crown():
    s = _m('gorraks_war_crown')                  # Gorrak's war crown: a ring of black spikes, a skull on its front
    bx(s, 0, -4, 0, 12.0, 3.0, 4.0, "dark")
    for k, x in enumerate((-5, -2.5, 0, 2.5, 5)):
        seg(s, (x, -1), (x * 1.1, 5 - abs(x) * 0.5 + (2 if k == 2 else 0)), 1.6, 1.6, "dark")
    bx(s, 0, -4.6, 0, 3.0, 3.0, 4.6, "wood")
    for sx in (-1, 1):
        bx(s, sx * 0.7, -3.4, 0, 0.8, 0.8, 4.8, "glow", glow=True)
    return s


MATS += [("serpent_ziggurat", m_jade_scale), ("serpent_ziggurat", m_champions_plume), ("serpent_ziggurat", m_coiled_kings_fang),
         ("rimeholt", m_hrimstone), ("rimeholt", m_winter_wolf_pelt), ("rimeholt", m_hrimgars_frozen_heart),
         ("glass_minaret", m_sun_glass), ("glass_minaret", m_dancers_bell), ("glass_minaret", m_sultans_lamp),
         ("warlords_fang", m_orc_tusk), ("warlords_fang", m_warg_fang), ("warlords_fang", m_gorraks_war_crown)]
