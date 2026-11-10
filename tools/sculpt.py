"""The sculpted props (tools/blender/sculpt_props.py) turned into blocks: each prop is one block,
ashbound:NAME[facing=..,piece=N], one block model per piece it passes through, greedy-meshed from its voxels in
boxes of one material and one shade (ambient occlusion baked from how buried each voxel is). Writes:

  - the textures (textures/block/sculpt/MAT_T.png, animated where they glow or flow) and the models and blockstates
  - SculptBlocks.java: the blocks, their piece counts, which pieces glow and which give off particles, their use
  - prop_shapes.txt lines: tight hitboxes per piece
  - tools/renders/sculpt_pieces.json: each prop's size and pieces (cell offsets, facing north) for the generators

    blender -b -P tools/blender/sculpt_props.py     then     python tools/sculpt.py
"""
import json
import math
import os
import random
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "src" / "main" / "resources" / "assets" / "ashbound"
TEX = ASSETS / "textures" / "block" / "sculpt"
VOX = ROOT / "tools" / "renders" / "sculpt"
JAVA = ROOT / "src" / "main" / "java" / "com" / "snoringwalrus" / "ashbound" / "SculptBlocks.java"
SHAPES = ROOT / "src" / "main" / "resources" / "ashbound" / "prop_shapes.txt"
PIECES = ROOT / "tools" / "renders" / "sculpt_pieces.json"

# material -> (colour, pattern, glow 0-15, see-through)
MATS = {
    "stone": ((142, 140, 134), "stone", 0, False), "stone_dark": ((92, 90, 88), "stone", 0, False),
    "stone_pale": ((196, 190, 178), "stone", 0, False), "sandstone": ((196, 170, 122), "stone", 0, False),
    "marble": ((222, 218, 208), "marble", 0, False), "marble_dark": ((178, 172, 164), "marble", 0, False),
    "firebrick": ((150, 78, 56), "brick", 0, False), "mortar": ((120, 108, 96), "stone", 0, False),
    "clay_fired": ((160, 96, 64), "stone", 0, False), "tile_blue": ((58, 104, 150), "glaze", 0, False),
    "coal": ((38, 36, 36), "stone", 0, False), "soil": ((70, 50, 36), "stone", 0, False),
    "coals_glow": ((236, 104, 32), "embers", 13, False), "molten": ((255, 168, 48), "molten", 15, False),
    "flame": ((255, 186, 70), "flame", 14, True), "flame_blue": ((90, 160, 255), "flame", 12, True),
    "witchfire": ((176, 96, 255), "flame", 14, True), "sun_glow": ((255, 214, 120), "embers", 15, False),
    "iron": ((112, 114, 118), "metal", 0, False), "iron_dark": ((64, 64, 68), "metal", 0, False),
    "steel": ((182, 188, 194), "metal", 0, False), "steel_dark": ((128, 134, 142), "metal", 0, False),
    "silver": ((196, 200, 210), "metal", 0, False),
    "copper": ((190, 104, 66), "copper", 0, False), "copper_dark": ((142, 76, 50), "copper", 0, False),
    "copper_green": ((86, 160, 130), "stone", 0, False),
    "brass": ((204, 162, 72), "metal", 0, False), "brass_dark": ((150, 112, 52), "metal", 0, False),
    "gold": ((238, 196, 70), "metal", 0, False),
    "bronze": ((150, 104, 56), "copper", 0, False), "bronze_dark": ((104, 72, 44), "copper", 0, False),
    "ore_iron": ((132, 102, 84), "ore", 0, False), "ore_copper": ((112, 132, 104), "ore", 0, False),
    "wood": ((150, 108, 68), "wood", 0, False), "wood_dark": ((96, 66, 44), "wood", 0, False),
    "wood_end": ((176, 136, 92), "rings", 0, False),
    "leather": ((120, 78, 48), "cloth", 0, False), "leather_red": ((122, 42, 36), "cloth", 0, False),
    "leather_blue": ((44, 62, 112), "cloth", 0, False), "leather_green": ((48, 88, 54), "cloth", 0, False),
    "leather_violet": ((86, 52, 112), "cloth", 0, False), "cloth_red": ((150, 40, 36), "cloth", 0, False),
    "towel": ((232, 226, 212), "cloth", 0, False), "towel_blue": ((120, 160, 196), "cloth", 0, False),
    "rope": ((176, 150, 104), "cloth", 0, False), "straw": ((214, 184, 98), "wood", 0, False),
    "paper": ((226, 214, 184), "paper", 0, False), "wax": ((236, 224, 196), "stone", 0, False),
    "bone": ((222, 210, 184), "stone", 0, False), "herb": ((84, 128, 60), "cloth", 0, False),
    "leaf": ((78, 138, 62), "cloth", 0, False), "leaf_dark": ((52, 102, 48), "cloth", 0, False),
    "water": ((70, 130, 210), "water", 0, True), "water_dark": ((40, 70, 96), "water", 0, True),
    "water_hot": ((96, 186, 196), "water", 0, True), "foam": ((220, 236, 244), "water", 0, True),
    "steam": ((236, 240, 244), "steam", 0, True), "glass": ((210, 230, 236), "glass", 0, True),
    "potion_red": ((220, 40, 60), "liquid", 9, False), "potion_green": ((80, 220, 90), "liquid", 9, False),
    "potion_blue": ((60, 120, 255), "liquid", 9, False), "potion_violet": ((180, 80, 255), "liquid", 9, False),
    "crystal": ((150, 80, 240), "crystal", 13, False), "crystal_cyan": ((90, 220, 240), "crystal", 12, False),
    "rune_glow": ((70, 200, 255), "rune", 12, False),
    "world_blue": ((60, 110, 200), "marble", 0, False), "world_red": ((186, 80, 50), "stone", 0, False),
    "world_star": ((30, 44, 96), "stars", 0, False),
    "ink": ((30, 28, 40), "stone", 0, False), "slate": ((48, 56, 58), "stone", 0, False),
    "chalk": ((232, 230, 220), "paper", 0, False), "terracotta": ((176, 94, 62), "stone", 0, False),
    "petal_red": ((196, 36, 44), "cloth", 0, False), "petal_pink": ((232, 128, 160), "cloth", 0, False),
    "petal_white": ((240, 236, 226), "cloth", 0, False), "petal_yellow": ((238, 196, 60), "cloth", 0, False),
    "stew": ((128, 74, 36), "liquid", 0, False), "meat": ((172, 88, 62), "cloth", 0, False),
    "bread": ((200, 142, 70), "wood", 0, False), "hops": ((132, 176, 74), "cloth", 0, False),
    "bottle_green": ((44, 84, 56), "glaze", 0, False),
    "petal_blue": ((96, 132, 220), "cloth", 0, False), "petal_violet": ((150, 100, 210), "cloth", 0, False),
}

# prop -> (sound, use, particles); light comes from the glowing materials
CONFIG = {
    "great_hearth": ("stone", "SMITHING", "EMBERS"), "smith_anvil": ("metal", "ANVIL", "NONE"),
    "quench_trough": ("wood", "NONE", "STEAM"), "grindstone_wheel": ("wood", "GRINDSTONE", "NONE"),
    "crucible_gantry": ("metal", "NONE", "MOLTEN"), "trip_hammer": ("wood", "NONE", "EMBERS"),
    "weapon_rack": ("wood", "NONE", "NONE"), "armour_stand": ("metal", "NONE", "NONE"), "tool_wall": ("wood", "NONE", "NONE"),
    "coal_bin": ("wood", "NONE", "NONE"), "ore_bin": ("wood", "NONE", "NONE"), "ingot_stack": ("metal", "NONE", "NONE"),
    "forge_crest": ("metal", "NONE", "NONE"), "master_anvil": ("metal", "SMITHING", "EMBERS"),
    "great_bellows": ("wood", "NONE", "NONE"), "molten_spout": ("stone", "NONE", "MOLTEN"), "ore_cart": ("metal", "NONE", "NONE"),
    "lion_spout": ("stone", "NONE", "DRIP"), "bath_boiler": ("metal", "NONE", "EMBERS"), "bath_tub": ("wood", "NONE", "STEAM"),
    "towel_bench": ("wood", "NONE", "NONE"), "steam_brazier": ("metal", "NONE", "STEAM"), "bath_plant": ("stone", "NONE", "NONE"),
    "arcane_orrery": ("metal", "NONE", "MAGIC"), "crystal_pylon": ("stone", "NONE", "MAGIC"), "crystal_crown": ("glass", "NONE", "MAGIC"),
    "alchemy_table": ("wood", "CRAFTING", "MAGIC"), "arcane_lectern": ("wood", "ENCHANTING", "MAGIC"),
    "brass_telescope": ("metal", "NONE", "NONE"), "celestial_globe": ("metal", "NONE", "NONE"), "rune_circle": ("stone", "NONE", "MAGIC"),
    "rune_target": ("wood", "NONE", "MAGIC"), "scroll_shelf": ("wood", "NONE", "NONE"), "arcane_brazier": ("metal", "NONE", "MAGIC"),
    # the Hall of Heroes' statues (tools/blender/hero_statues.py)
    "hero_shield": ("stone", "NONE", "NONE"), "hero_hammer": ("stone", "NONE", "NONE"), "hero_bow": ("stone", "NONE", "NONE"),
    "hero_blackmage": ("stone", "NONE", "EMBERS"), "hero_priestess": ("stone", "NONE", "MAGIC"), "hero_rogue": ("stone", "NONE", "NONE"),
    "hero_spear": ("stone", "NONE", "NONE"), "hero_summoner": ("stone", "NONE", "MAGIC"), "hero_paladin": ("stone", "NONE", "NONE"),
    "hero_axe": ("stone", "NONE", "NONE"), "hero_first": ("stone", "NONE", "NONE"),
    "colossus_knight": ("stone", "NONE", "NONE"), "colossus_mage": ("stone", "NONE", "MAGIC"),
    # the guild belfry's clock and the Warden's blade (tools/blender/civic_sculpt.py)
    "clock_face": ("stone", "NONE", "NONE"), "warden_blade": ("metal", "NONE", "EMBERS"),
    "clock_hand_minute": ("metal", "NONE", "NONE"), "clock_hand_hour": ("metal", "NONE", "NONE"),
    "guild_crest": ("metal", "NONE", "NONE"),
    # the shops' hanging signs, one a trade
    **{"sign_" + t: ("metal", "NONE", "NONE") for t in ("general", "baker", "tailor", "apothecary", "grocer", "books", "chandler", "fishmonger")},
    # the guild hall's furniture (tools/blender/civic_sculpt.py)
    "guild_board": ("wood", "NONE", "NONE"), "guild_counter": ("wood", "NONE", "NONE"), "trestle_table": ("wood", "NONE", "NONE"),
    "guild_chair": ("wood", "NONE", "NONE"), "round_table": ("wood", "NONE", "NONE"), "tavern_bar": ("wood", "NONE", "NONE"),
    "keg_rack": ("wood", "NONE", "NONE"), "bar_stool": ("wood", "NONE", "NONE"), "guild_chandelier": ("metal", "NONE", "NONE"),
    "trophy_skull": ("stone", "NONE", "EMBERS"),
    # the Arcanum's classrooms and the city's gardens (tools/blender/school_sculpt.py)
    "school_desk": ("wood", "NONE", "NONE"), "school_chair": ("wood", "NONE", "NONE"), "master_desk": ("wood", "NONE", "NONE"),
    "rune_board": ("wood", "NONE", "NONE"), "topiary_pot": ("stone", "NONE", "NONE"), "flower_tub": ("wood", "NONE", "NONE"),
    "rose_bush": ("grass", "NONE", "NONE"), "hydrangea": ("grass", "NONE", "NONE"),
    # the player's manor (tools/blender/manor_sculpt.py, tools/capital_home.py)
    **{n: ("wood", "NONE", "NONE") for n in ("nightstand", "wardrobe", "washstand", "welsh_dresser", "kitchen_worktable", "pot_rack",
                                            "hearth_armchair")},
    # the Cold Forge in the vault under the Ashforge (ColdForge.java)
    # the homestead's stations and its blocky props (tools/blender/homestead_sculpt.py)
    "manor_cookhearth": ("stone", "MEAL", "EMBERS"), "manor_brewery": ("metal", "BREW", "STEAM"),
    "manor_alembic": ("wood", "ELIXIR", "MAGIC"), "cellar_barrel": ("wood", "NONE", "NONE"), "wine_rack": ("wood", "NONE", "NONE"),
    "field_scarecrow": ("wood", "NONE", "NONE"), "farm_handcart": ("wood", "NONE", "NONE"),
    "cold_forge": ("stone", "NONE", "NONE"), "cold_forge_lit": ("stone", "NONE", "EMBERS"),
}
MODEL_ONLY = {"clock_hand_minute", "clock_hand_hour"}     # models for a renderer (ClockHands), no block of their own
FX_MATS = {"EMBERS": {"coals_glow", "flame", "molten"}, "MOLTEN": {"molten"}, "STEAM": {"water_hot", "steam", "water_dark"},
           "MAGIC": {"crystal", "crystal_cyan", "rune_glow", "witchfire", "sun_glow", "potion_green", "potion_violet"},
           "DRIP": {"foam"}}
SOUND = {"stone": "STONE", "metal": "METAL", "wood": "WOOD", "glass": "AMETHYST", "grass": "AZALEA"}
MAPC = {"stone": "STONE", "metal": "METAL", "wood": "WOOD", "glass": "COLOR_PURPLE", "grass": "PLANT"}
TONES = (1.0, 0.8, 0.62)


# ---------------------------------------------------------------- textures

def clamp(c):
    return tuple(max(0, min(255, int(v))) for v in c)


def texture(name, tone):
    base, pat, glow, see = MATS[name]
    r = random.Random(sum(map(ord, name)) * 7 + tone)
    k0 = 1.0 if glow else TONES[tone]
    frames = 8 if pat in ("embers", "molten", "flame", "water", "rune", "crystal", "liquid") else 1
    img = Image.new("RGBA", (16, 16 * frames))
    for f in range(frames):
        for y in range(16):
            for x in range(16):
                k = k0 * (1 + r.uniform(-0.05, 0.05))
                a = 255
                c = base
                if pat == "stone":
                    k *= 1 + 0.05 * math.sin(x * 1.3 + y * 0.7) * math.sin(y * 1.1)
                elif pat == "marble":
                    k *= 1 + 0.035 * math.sin((x + y * 0.6) * 0.7) + (-0.08 if (x * 7 + y * 3) % 23 == 0 else 0)
                elif pat == "brick":
                    row = y // 4
                    if y % 4 == 3 or (x + (row % 2) * 4) % 8 == 7:
                        c = (110, 96, 86)
                    else:
                        k *= 1 + 0.08 * math.sin(row * 2.1 + (x + (row % 2) * 4) // 8 * 1.7)
                elif pat == "wood":
                    k *= 1 + 0.1 * math.sin(x * 1.9 + math.sin(y * 0.4) * 1.5) - (0.12 if (x * 5 + y // 5) % 11 == 0 else 0)
                elif pat == "rings":
                    d = math.hypot(x - 7.5, y - 7.5)
                    k *= 1 - 0.12 * (int(d) % 2)
                elif pat == "metal":
                    k *= 1 + 0.04 * math.sin(x * 0.9 + y * 0.3) + (0.1 if r.random() < 0.04 else 0)
                elif pat == "copper":
                    k *= 1 + 0.04 * math.sin(x * 0.5 + y * 0.9) + (0.08 if r.random() < 0.05 else 0)
                    if r.random() < 0.02:
                        c = (120, 150, 120)
                elif pat == "ore":
                    if r.random() < 0.18:
                        c = (200, 150, 110) if "iron" in name else (90, 190, 150)
                elif pat == "cloth":
                    k *= 1 - 0.07 * ((x + y) % 2)
                elif pat == "paper":
                    k *= 1 - (0.25 if y % 3 == 0 and 2 < x < 14 and r.random() < 0.7 else 0)
                elif pat == "glaze":
                    k *= 1 + 0.12 * math.sin(y * 0.5) + (0.18 if r.random() < 0.03 else 0)
                elif pat == "embers":
                    t = math.sin(x * 1.7 + y * 2.3 + f * 0.8) * math.sin(x * 0.6 - y * 1.1 - f * 0.5)
                    c = (255, int(110 + 90 * max(0, t)), int(30 + 60 * max(0, t)))
                    if t < -0.55:
                        c = (150, 40, 20)
                    k = 1
                elif pat == "molten":
                    t = math.sin(x * 0.8 + (y + f * 2) * 0.9) + 0.6 * math.sin(x * 2.1 - (y + f * 2) * 0.4)
                    c = (255, int(150 + 50 * t), int(40 + 40 * t))
                    k = 1
                elif pat == "flame":
                    t = math.sin(x * 1.2 + (y + f * 2) * 1.4) * 0.5 + 0.5
                    c = tuple(int(v * (0.85 + 0.25 * t)) for v in base)
                    a, k = 190, 1
                elif pat == "water":
                    t = math.sin(x * 0.7 + (y + f * 2) * 0.6) * 0.5 + 0.5
                    k *= 0.9 + 0.15 * t
                    a = 150 if name != "foam" else 200
                elif pat == "steam":
                    a, k = 70, 1
                elif pat == "glass":
                    a = 90 if 0 < x < 15 and 0 < y < 15 else 150
                elif pat == "liquid":
                    k = 0.9 + 0.15 * math.sin(x + y + f)
                elif pat == "crystal":
                    t = ((x - y + f * 2) % 16) / 16
                    k = 0.8 + 0.4 * (t if t < 0.5 else 1 - t) + (0.25 if (x + y + f) % 9 == 0 else 0)
                elif pat == "rune":
                    k = 0.85 + 0.2 * math.sin(f * 0.8 + x * 0.3)
                elif pat == "stars":
                    if r.random() < 0.07:
                        c, k = (250, 220, 120), 1
                img.putpixel((x, y + 16 * f), clamp(tuple(v * k for v in c)) + (a,))
    return img, frames


def write_textures(used):
    TEX.mkdir(parents=True, exist_ok=True)
    for old in TEX.glob("*"):
        old.unlink()
    for name, tone in sorted(used):
        img, frames = texture(name, tone)
        p = TEX / ("%s_%d.png" % (name, tone))
        img.save(p)
        if frames > 1:
            p.with_suffix(".png.mcmeta").write_text(json.dumps({"animation": {"frametime": 3, "interpolate": True}}), encoding="utf-8")


# ---------------------------------------------------------------- voxels to boxes

N6 = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def shade(vox, mats, V):
    """Tone per voxel: 0 light, 1 mid, 2 dark, from how filled its neighbourhood is (ambient occlusion), a little
    darker low down; interior voxels take a neighbour's tone so the boxes merge."""
    s = max(1, V // 8)
    rays = [(dx * s, dy * s, dz * s) for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2) for dz in (-2, -1, 0, 1, 2)
            if (dx, dy, dz) != (0, 0, 0) and abs(dx) + abs(dy) + abs(dz) > 1]
    solid = {k for k, m in vox.items() if not MATS[mats[m]][3]}
    tone = {}
    for (x, y, z), m in vox.items():
        if MATS[mats[m]][2] or MATS[mats[m]][3]:
            tone[(x, y, z)] = 0
            continue
        if all((x + a, y + b, z + c) in solid for a, b, c in N6):
            continue
        n = sum(1 for a, b, c in rays if (x + a, y + b, z + c) in solid)
        k = n / len(rays) - 0.06 * (y / V < 0.15)
        tone[(x, y, z)] = 2 if k > 0.62 else 1 if k > 0.47 else 0
    # one pass of majority smoothing over the surface (fewer, bigger boxes; no speckle)
    sm = {}
    for p, t in tone.items():
        m = vox[p]
        votes = Counter([t])
        for a, b, c in N6:
            q = (p[0] + a, p[1] + b, p[2] + c)
            if q in tone and vox[q] == m:
                votes[tone[q]] += 1
        sm[p] = votes.most_common(1)[0][0]
    for p in vox:
        if p not in sm:
            above = (p[0], p[1] + 1, p[2])
            sm[p] = sm.get(above, 1) if vox.get(above) == vox[p] else 1
    return sm


def greedy(cells):
    left = dict(cells)
    boxes = []
    for key in sorted(cells):
        if key not in left:
            continue
        t = left[key]
        x, y, z = key
        x1 = x
        while left.get((x1 + 1, y, z)) == t:
            x1 += 1
        z1 = z
        while all(left.get((xx, y, z1 + 1)) == t for xx in range(x, x1 + 1)):
            z1 += 1
        y1 = y
        while all(left.get((xx, y1 + 1, zz)) == t for xx in range(x, x1 + 1) for zz in range(z, z1 + 1)):
            y1 += 1
        for xx in range(x, x1 + 1):
            for yy in range(y, y1 + 1):
                for zz in range(z, z1 + 1):
                    del left[(xx, yy, zz)]
        boxes.append((x, y, z, x1 + 1, y1 + 1, z1 + 1, t))
    return boxes


def uv(face, a, b):
    x1, y1, z1 = a
    x2, y2, z2 = b
    u = {"north": [16 - x2, 16 - y2, 16 - x1, 16 - y1], "south": [x1, 16 - y2, x2, 16 - y1],
         "east": [16 - z2, 16 - y2, 16 - z1, 16 - y1], "west": [z1, 16 - y2, z2, 16 - y1],
         "up": [x1, z1, x2, z2], "down": [x1, 16 - z2, x2, 16 - z1]}[face]
    return [round(max(0.0, min(16.0, v)), 3) for v in u]


FACES = (("north", (0, 0, -1)), ("south", (0, 0, 1)), ("west", (-1, 0, 0)), ("east", (1, 0, 0)), ("down", (0, -1, 0)), ("up", (0, 1, 0)))


def hitboxes(cells, V, solid):
    """Boxes (pixels, facing north) covering a piece's solid voxels on a 2-pixel grid."""
    g = 8
    f = V / g
    grid = {}
    for (x, y, z) in cells:
        if (x, y, z) in solid:
            grid[(int((x % V) // f), int((y % V) // f), int((z % V) // f))] = 1       # within this block, not the whole prop
    out = []
    for (x0, y0, z0, x1, y1, z1, _) in greedy(grid):
        out += [x0 * 2, y0 * 2, z0 * 2, x1 * 2, y1 * 2, z1 * 2]
    return out


def build(name, used, shapes):
    data = json.load(open(VOX / (name + ".json")))
    V, (w, h, d), mats = data["V"], data["size"], data["mats"]
    vox = {(x, y, z): m for x, y, z, m in data["vox"]}
    tone = shade(vox, mats, V)
    see = {k for k, m in vox.items() if MATS[mats[m]][3]}
    solid = set(vox) - see
    s = 16 / V
    cells = {}
    for p, m in vox.items():
        cells.setdefault((p[0] // V, p[1] // V, p[2] // V), {})[p] = (m, tone[p])
    mdir = ASSETS / "models" / "block"
    for old in mdir.glob("%s_*.json" % name):
        old.unlink()
    pieces, glow, fx = [], [], []
    fxm = FX_MATS.get(CONFIG[name][2], set())
    light = 0
    nbox = most = 0
    nglow = sum(1 for m in vox.values() if MATS[mats[m]][2])
    for cell, vs in sorted(cells.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
        cx, cy, cz = cell
        els, keys = [], {}
        trans = False
        for (x0, y0, z0, x1, y1, z1, (m, t)) in greedy(vs):
            mat = mats[m]
            a = [round((x0 - cx * V) * s, 3), round((y0 - cy * V) * s, 3), round((z0 - cz * V) * s, 3)]
            b = [round((x1 - cx * V) * s, 3), round((y1 - cy * V) * s, 3), round((z1 - cz * V) * s, 3)]
            seethru = MATS[mat][3]
            faces = {}
            for fn, (dx, dy, dz) in FACES:
                if dx:
                    xs = x0 - 1 if dx < 0 else x1
                    nb = [(xs, yy, zz) for yy in range(y0, y1) for zz in range(z0, z1)]
                elif dy:
                    ys = y0 - 1 if dy < 0 else y1
                    nb = [(xx, ys, zz) for xx in range(x0, x1) for zz in range(z0, z1)]
                else:
                    zs = z0 - 1 if dz < 0 else z1
                    nb = [(xx, yy, zs) for xx in range(x0, x1) for yy in range(y0, y1)]
                if seethru:
                    cover = all(q in solid or vox.get(q) == m for q in nb)
                else:
                    cover = all(q in solid for q in nb)
                if not cover:
                    tone_ = 0 if MATS[mat][2] or seethru else t
                    key = "%s_%d" % (mat, tone_)
                    used.add((mat, tone_))
                    keys[key] = "ashbound:block/sculpt/" + key
                    faces[fn] = {"texture": "#" + key, "uv": uv(fn, a, b)}
            if not faces:
                continue
            e = {"from": a, "to": b, "faces": faces}
            g = MATS[mat][2]
            if g:
                e["shade"] = False
                e["light_emission"] = 15
                e["neoforge_data"] = {"block_light": 15, "sky_light": 15}
            if seethru:
                trans = True
            els.append(e)
        if not els:
            continue
        idx = len(pieces)
        model = {"ambientocclusion": False, "textures": dict(keys, particle=next(iter(keys.values()))), "elements": els}
        if trans:
            model["render_type"] = "minecraft:translucent"
        (mdir / ("%s_%d.json" % (name, idx))).write_text(json.dumps(model, separators=(",", ":")), encoding="utf-8")
        pieces.append([cx, cy, cz, idx])
        here = {mats[m] for (m, _) in vs.values()}
        gl = max([MATS[mm][2] for mm in here] + [0])
        if gl:
            glow.append(idx)
            light = max(light, gl)
        if here & fxm:
            fx.append(idx)
        if name not in MODEL_ONLY:
            shapes.append("%s %d %s" % (name, idx, " ".join(str(v) for v in hitboxes(vs, V, solid))))
        nbox += len(els)
        most = max(most, len(els))
    if nglow < 150:
        light = min(light, 8)                      # a hot bar or a candle, not a fire
    if name in MODEL_ONLY:
        print("  %-18s model only, %d boxes" % (name, nbox))
        return None
    variants = {}
    for f, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270)):
        for i in range(len(pieces)):
            v = {"model": "ashbound:block/%s_%d" % (name, i)}
            if y:
                v["y"] = y
            variants["facing=%s,piece=%d" % (f, i)] = v
    (ASSETS / "blockstates" / (name + ".json")).write_text(json.dumps({"variants": variants}, separators=(",", ":")), encoding="utf-8")
    print("  %-18s %3d pieces %5d boxes  (%d per piece at most)" % (name, len(pieces), nbox, most))
    return {"size": [w, h, d], "pieces": pieces, "glow": glow, "fx": fx, "light": light}


def java(info):
    lines = []
    for name, i in info.items():
        snd, use, fxk = CONFIG[name]
        props = ("BlockBehaviour.Properties.of().mapColor(MapColor.%s).strength(-1f, 3600000f).sound(SoundType.%s).noOcclusion()"
                 % (MAPC[snd], SOUND[snd]))
        lines.append('\tstatic final DeferredBlock<Block> %s = block("%s", %d, %d, Use.%s, Fx.%s, new int[] {%s}, new int[] {%s},\n\t\t\t%s);'
                     % (name.upper(), name, len(i["pieces"]), i["light"], use, fxk, ", ".join(map(str, i["glow"])),
                        ", ".join(map(str, i["fx"])), props))
    JAVA.write_text('''package com.snoringwalrus.ashbound;

import com.snoringwalrus.ashbound.PropBlock.Sculpt.Fx;
import com.snoringwalrus.ashbound.PropBlock.Sculpt.Use;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.registries.DeferredBlock;

/** The sculpted props (written by tools/sculpt.py: edit that, not this). Placed by the generators, not by hand. */
public final class SculptBlocks {
	private SculptBlocks() {}

	private static DeferredBlock<Block> block(String name, int pieces, int light, Use use, Fx fx, int[] glow, int[] smoke, BlockBehaviour.Properties props) {
		return WorldBlocks.BLOCKS.registerBlock(name, p -> PropBlock.Sculpt.make(p, pieces, light, use, fx, glow, smoke), props);
	}

	/** Loads the class, so its blocks are registered. */
	static void init() {}

%s
}
''' % "\n".join(lines), encoding="utf-8")


def main():
    names = [n for n in CONFIG if (VOX / (n + ".json")).exists()]
    used, shapes, info = set(), [], {}
    print("props:")
    for n in names:
        i = build(n, used, shapes)
        if i:
            info[n] = i
    write_textures(used)
    java(info)
    keep = [ln for ln in SHAPES.read_text(encoding="utf-8").splitlines() if ln.split(" ", 1)[0] not in CONFIG]
    SHAPES.write_text("\n".join(keep + shapes) + "\n", encoding="utf-8")
    json.dump({n: {"size": i["size"], "pieces": i["pieces"]} for n, i in info.items()}, open(PIECES, "w"))
    # the Cold Forge swaps its blocks in the game, so the game needs its layouts (ColdForge.java)
    json.dump({n: {"size": info[n]["size"], "pieces": info[n]["pieces"]} for n in ("cold_forge", "cold_forge_lit")},
              open(ROOT / "src" / "main" / "resources" / "ashbound" / "cold_forge_pieces.json", "w"))
    print("%d props, %d textures" % (len(info), len(used)))


if __name__ == "__main__":
    main()
