"""The colour palette for painted statues: every solid, non-falling, non-burning 1.21.1 block worth building a figure
from, with its texture's mean colour in CIE Lab (measured, blockpal.measure), and a matcher that turns a wanted
colour into a block the way the map-art and ObjToSchematic tools do: nearest in Lab, an ordered (Bayer) dither so a
colour between two blocks becomes an even mix of both, never random speckle, and same-colour blocks of different
texture swapped in broad patches so a big area isn't one flat block.

    python tools/colourpal.py          prints the palette, light to dark, with Lab and grain
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blockpal  # noqa: E402

# nothing flammable (the devil stands by lava), nothing that falls, melts, oxidises or makes noise
STONE = ["smooth_quartz", "quartz_block", "quartz_bricks", "calcite", "bone_block", "snow_block", "white_concrete",
         "ashbound:pale_limestone", "diorite", "polished_diorite", "ashbound:statue_stone", "clay", "smooth_stone",
         "andesite", "polished_andesite", "stone", "tuff", "polished_tuff", "dead_tube_coral_block",
         "dead_brain_coral_block", "dead_horn_coral_block", "dead_bubble_coral_block", "deepslate", "cobbled_deepslate",
         "polished_deepslate", "deepslate_tiles", "smooth_basalt", "basalt", "blackstone", "polished_blackstone",
         "gray_concrete", "light_gray_concrete", "black_concrete", "coal_block", "obsidian", "mud", "packed_mud",
         "mud_bricks", "dripstone_block", "granite", "polished_granite", "end_stone", "end_stone_bricks"]
WARM = ["sandstone", "smooth_sandstone", "cut_sandstone", "red_sandstone", "smooth_red_sandstone", "bricks", "terracotta",
        "white_terracotta", "light_gray_terracotta", "gray_terracotta", "black_terracotta", "brown_terracotta",
        "red_terracotta", "orange_terracotta", "yellow_terracotta", "pink_terracotta", "magenta_terracotta",
        "purple_terracotta", "lime_terracotta", "green_terracotta", "cyan_terracotta", "light_blue_terracotta",
        "blue_terracotta", "netherrack", "nether_bricks", "red_nether_bricks", "nether_wart_block", "warped_wart_block",
        "crimson_hyphae", "stripped_crimson_hyphae", "warped_hyphae", "stripped_warped_hyphae", "honeycomb_block"]
CONCRETE = ["%s_concrete" % c for c in ("brown", "red", "orange", "yellow", "lime", "green", "cyan", "light_blue", "blue",
                                         "purple", "magenta", "pink")]
METAL = ["gold_block", "raw_gold_block", "ashbound:gilded_tiles", "iron_block", "raw_iron_block", "netherite_block",
         "waxed_copper_block", "waxed_cut_copper", "waxed_exposed_copper", "waxed_weathered_copper",
         "waxed_oxidized_copper", "raw_copper_block", "lapis_block", "prismarine", "prismarine_bricks", "dark_prismarine",
         "purpur_block", "amethyst_block"]
GLOW = ["shroomlight", "ochre_froglight", "pearlescent_froglight", "verdant_froglight", "glowstone", "sea_lantern",
        "magma_block", "crying_obsidian"]
ALL = STONE + WARM + CONCRETE + METAL + GLOW
GRITTY = 15.0                       # grain above this speckles - kept out of the match except as a deliberate accent

_PAL = None


def lab(rgb):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(float(c)) for c in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return (116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z)))


def palette():
    """[(block, (L, a, b), grain, glows)] for every block whose texture could be read."""
    global _PAL
    if _PAL is None:
        _PAL = []
        for b in ALL:
            try:
                m = blockpal.measure(b)
            except Exception as e:                  # a texture that isn't there: skip it
                print("  (no texture for %s: %s)" % (b, e))
                continue
            _PAL.append((b, lab(m["rgb"]), m["grain"], b in GLOW))
    return _PAL


def de(p, q):
    # lightness counts a little more than hue on a statue: the shading reads first, the colour second
    return math.sqrt(1.6 * (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 + (p[2] - q[2]) ** 2)


_MEMO = {}


def match(want, pick=0.0, glow=False, avoid=(), only=None):
    """The block for a wanted Lab colour. `pick` (0-1, from a broad noise) chooses among the blocks within a few ΔE of
    the best, so near-equal blocks of different texture take turns in patches. Glowing blocks only when `glow`."""
    key = (round(want[0]), round(want[1] / 2), round(want[2] / 2), int(pick * 8), glow, avoid, only)
    if key in _MEMO:
        return _MEMO[key]
    if only:
        rows = [r for r in palette() if r[0] in only]
    else:
        rows = [r for r in palette() if (glow or not r[3]) and r[0] not in avoid and r[2] <= GRITTY
                and (r[1][1] > -8 or want[1] < -10)]        # no green block in a colour that isn't green
    # texture: a little grain reads as stone; flat concrete/terracotta and gritty blocks both cost a bit
    def cost(r):
        return de(want, r[1]) + 0.35 * abs(r[2] - 5.5)
    rows.sort(key=cost)
    best = cost(rows[0])
    close = [r for r in rows[:4] if cost(r) <= best + 4.0]
    _MEMO[key] = close[min(len(close) - 1, int(pick * len(close)))][0]
    return _MEMO[key]


if __name__ == "__main__":
    for b, (L, a, bb), g, gl in sorted(palette(), key=lambda r: -r[1][0]):
        print("  %-28s L %5.1f a %6.1f b %6.1f  grain %4.1f%s" % (b, L, a, bb, g, "  glow" if gl else ""))
