"""Block palettes measured off the real textures: each block's mean colour, its lightness (CIE L*), how grainy its
texture is (the spread of lightness across its pixels) and its saturation. Statue shading ramps are picked from these
numbers, not by eye: evenly spaced in lightness, smooth textures preferred (gritty ones speckle a shaded surface).

    python tools/blockpal.py                 prints the measured table, light to dark
    python tools/blockpal.py ramp 6          a 6-step grey ramp, smooth blocks only

    import blockpal; blockpal.ramp(6, family="grey", max_grain=9)
"""
import colorsys
import math
import os
import sys

sys.path.insert(0, "E:/Ashbound/tools")
import structkit as K  # noqa: E402
from PIL import Image  # noqa: E402

GREY = ["calcite", "white_concrete", "smooth_quartz", "quartz_block", "ashbound:statue_stone", "polished_diorite", "diorite",
        "smooth_stone", "stone", "polished_andesite", "andesite", "stone_bricks", "light_gray_concrete", "tuff", "polished_tuff",
        "tuff_bricks", "cobbled_deepslate", "polished_deepslate", "deepslate_tiles", "deepslate_bricks", "gray_concrete",
        "smooth_basalt", "blackstone", "polished_blackstone", "polished_blackstone_bricks", "dripstone_block", "clay",
        "light_gray_terracotta", "gray_terracotta", "white_terracotta", "snow_block", "iron_block", "mud_bricks",
        "packed_mud", "dead_brain_coral_block", "dead_tube_coral_block", "light_gray_wool", "gray_wool", "white_wool"]
GOLD = ["gold_block", "raw_gold_block", "ashbound:gilded_tiles", "yellow_terracotta", "honeycomb_block", "smooth_sandstone",
        "cut_sandstone", "orange_terracotta", "yellow_concrete", "yellow_wool", "bamboo_planks", "stripped_bamboo_block"]
FAMILIES = {"grey": GREY, "gold": GOLD}

_CACHE = {}


def _lstar(r, g, b):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    y = 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
    return 116 * (y ** (1 / 3) if y > 0.008856 else 7.787 * y + 16 / 116) - 16


def measure(block):
    """{rgb, L, grain, sat} of a block's side face."""
    if block in _CACHE:
        return _CACHE[block]
    ns = "ashbound" if block.startswith("ashbound:") else "minecraft"
    name = block.split(":")[-1]
    side = K.textures_of(name, {}, ns)[1]
    if ns == "ashbound" and not side.startswith("ashbound:"):
        side = "ashbound:" + side.split(":")[-1]
    meta = K.fetch([side])[side]
    im = Image.open(meta["path"]).convert("RGB")
    px = list(im.getdata())
    ls = [_lstar(*p) for p in px]
    L = sum(ls) / len(ls)
    grain = math.sqrt(sum((v - L) ** 2 for v in ls) / len(ls))
    r, g, b = (sum(p[i] for p in px) / len(px) for i in range(3))
    sat = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)[1]
    out = {"rgb": (round(r), round(g), round(b)), "L": round(L, 1), "grain": round(grain, 1), "sat": round(sat, 2)}
    _CACHE[block] = out
    return out


def table(family="grey"):
    rows = []
    for b in FAMILIES[family]:
        try:
            rows.append((b, measure(b)))
        except Exception as e:                       # a texture that isn't there: skip it
            print("  (no texture for %s: %s)" % (b, e))
    return sorted(rows, key=lambda r: -r[1]["L"])


def ramp(steps, family="grey", max_grain=9.0, max_sat=0.18, lo=None, hi=None, avoid=()):
    """`steps` blocks from light to dark, as evenly spaced in L* as the smooth blocks allow."""
    rows = [(b, m) for b, m in table(family) if m["grain"] <= max_grain and (family != "grey" or m["sat"] <= max_sat)
            and b not in avoid]
    if hi is not None:
        rows = [r for r in rows if r[1]["L"] <= hi]
    if lo is not None:
        rows = [r for r in rows if r[1]["L"] >= lo]
    if len(rows) <= steps:
        return [b for b, _ in rows]
    top, bot = rows[0][1]["L"], rows[-1][1]["L"]
    out = []
    for i in range(steps):
        want = top + (bot - top) * i / (steps - 1)
        best = min((r for r in rows if r[0] not in out), key=lambda r: abs(r[1]["L"] - want) + 0.15 * r[1]["grain"])
        out.append(best[0])
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "ramp":
        print(ramp(int(sys.argv[2]) if len(sys.argv) > 2 else 6, sys.argv[3] if len(sys.argv) > 3 else "grey"))
    else:
        for fam in ("grey", "gold"):
            print("== %s: block, L*, grain, saturation, rgb" % fam)
            for b, m in table(fam):
                print("  %-30s L %5.1f  grain %4.1f  sat %.2f  %s" % (b, m["L"], m["grain"], m["sat"], m["rgb"]))
