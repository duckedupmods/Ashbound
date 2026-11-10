"""The Ashen Ring's own pictures and data (Arena.java, ArenaShape.java): its sand and rune blocks, the dimension (night
fixed at midnight, open sky over the clouds), Veyra the Ringkeeper (her talk; her look, for now, borrowed from a black
mage of the forge's cast) and the names.
    python tools/arena_assets.py
The look is tools/blender/arena_ring.py (renders in tools/renders/arena)."""
import json
import random
import shutil
from pathlib import Path

from PIL import Image

GAME = Path(__file__).resolve().parent.parent
A = GAME / "src/main/resources/assets/ashbound"
D = GAME / "src/main/resources/data/ashbound"
LOOK_FROM = "adventurer_b_63795002"      # Isra Cinder, B-rank black mage


def clamp(v):
    return max(0, min(255, int(v)))


def wj(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1), encoding="utf-8")


def textures():
    r = random.Random(7)
    sand = Image.new("RGBA", (16, 16))
    px = sand.load()
    for y in range(16):
        for x in range(16):
            v = r.choice((92, 98, 104, 110, 116, 100))
            if r.random() < 0.06:
                v = 70
            px[x, y] = (clamp(v * 1.02), clamp(v * 0.99), clamp(v * 0.97), 255)
    sand.save(A / "textures/block/arena_sand.png")
    # the rune: the sand, cut with a glowing pale-blue mark (lines across and a ring)
    rune = sand.copy()
    rp = rune.load()
    for y in range(16):
        for x in range(16):
            d = ((x - 7.5) ** 2 + (y - 7.5) ** 2) ** 0.5
            line = abs(d - 5.5) < 0.7 or (abs(x - y) < 0.7 and 3 < d < 5) or (abs(x + y - 15) < 0.7 and 3 < d < 5) or d < 1.2
            if line:
                rp[x, y] = (110, 220, 255, 255)
            elif abs(d - 5.5) < 1.6:
                b = rp[x, y]
                rp[x, y] = (clamp(b[0] * 0.8), clamp(b[1] * 0.95 + 20), clamp(b[2] * 1.1 + 30), 255)
    rune.save(A / "textures/block/arena_rune.png")
    for name in ("arena_sand", "arena_rune"):
        wj(A / "blockstates" / (name + ".json"), {"variants": {"": {"model": "ashbound:block/" + name}}})
        wj(A / "models/block" / (name + ".json"), {"parent": "minecraft:block/cube_all", "textures": {"all": "ashbound:block/" + name}})
        wj(A / "models/item" / (name + ".json"), {"parent": "ashbound:block/" + name})


def dimension():
    wj(D / "dimension_type/ashen_ring.json", {
        "ultrawarm": False, "natural": False, "piglin_safe": False, "respawn_anchor_works": False, "bed_works": False,
        "has_raids": False, "has_skylight": True, "has_ceiling": False, "coordinate_scale": 1.0, "ambient_light": 0.0,
        "fixed_time": 18000, "logical_height": 384, "effects": "minecraft:overworld", "infiniburn": "#minecraft:infiniburn_overworld",
        "min_y": 0, "height": 384, "monster_spawn_light_level": 0, "monster_spawn_block_light_limit": 0})
    wj(D / "dimension/ashen_ring.json", {"type": "ashbound:ashen_ring", "generator": {"type": "minecraft:flat", "settings": {
        "biome": "ashbound:ashen_ring", "features": False, "lakes": False, "layers": [{"block": "minecraft:air", "height": 1}],
        "structure_overrides": []}}})
    wj(D / "worldgen/biome/ashen_ring.json", {
        "has_precipitation": False, "temperature": 0.5, "downfall": 0.0,
        "effects": {"fog_color": 0x0D1426, "sky_color": 0x0A1230, "water_color": 4159204, "water_fog_color": 329011,
                    "mood_sound": {"sound": "minecraft:ambient.cave", "tick_delay": 6000, "block_search_extent": 8, "offset": 2.0}},
        "spawners": {}, "spawn_costs": {}, "carvers": {}, "features": []})


def hearth():
    """The Kiln-Father's Hearth (BossArenas, HearthShape): a red-black void at night, ash falling, the deltas' roar."""
    wj(D / "dimension_type/kiln_hearth.json", {
        "ultrawarm": True, "natural": False, "piglin_safe": False, "respawn_anchor_works": False, "bed_works": False,
        "has_raids": False, "has_skylight": True, "has_ceiling": False, "coordinate_scale": 1.0, "ambient_light": 0.0,
        "fixed_time": 18000, "logical_height": 384, "effects": "minecraft:overworld", "infiniburn": "#minecraft:infiniburn_overworld",
        "min_y": 0, "height": 384, "monster_spawn_light_level": 0, "monster_spawn_block_light_limit": 0})
    wj(D / "dimension/kiln_hearth.json", {"type": "ashbound:kiln_hearth", "generator": {"type": "minecraft:flat", "settings": {
        "biome": "ashbound:kiln_hearth", "features": False, "lakes": False, "layers": [{"block": "minecraft:air", "height": 1}],
        "structure_overrides": []}}})
    wj(D / "worldgen/biome/kiln_hearth.json", {
        "has_precipitation": False, "temperature": 2.0, "downfall": 0.0,
        "effects": {"fog_color": 0x2A0C05, "sky_color": 0x3A1206, "water_color": 4159204, "water_fog_color": 329011,
                    "particle": {"options": {"type": "minecraft:ash"}, "probability": 0.012},
                    "ambient_sound": "minecraft:ambient.basalt_deltas.loop",
                    "mood_sound": {"sound": "minecraft:ambient.basalt_deltas.mood", "tick_delay": 6000, "block_search_extent": 8, "offset": 2.0}},
        "spawners": {}, "spawn_costs": {}, "carvers": {}, "features": []})


def wreck():
    """The Graveyard of Ships (BossArenas, WreckShape): a storm-night over a black sea, mist, the rain's hiss."""
    wj(D / "dimension_type/ship_graveyard.json", {
        "ultrawarm": False, "natural": False, "piglin_safe": False, "respawn_anchor_works": False, "bed_works": False,
        "has_raids": False, "has_skylight": True, "has_ceiling": False, "coordinate_scale": 1.0, "ambient_light": 0.0,
        "fixed_time": 18000, "logical_height": 384, "effects": "minecraft:overworld", "infiniburn": "#minecraft:infiniburn_overworld",
        "min_y": 0, "height": 384, "monster_spawn_light_level": 0, "monster_spawn_block_light_limit": 0})
    wj(D / "dimension/ship_graveyard.json", {"type": "ashbound:ship_graveyard", "generator": {"type": "minecraft:flat", "settings": {
        "biome": "ashbound:ship_graveyard", "features": False, "lakes": False, "layers": [{"block": "minecraft:air", "height": 1}],
        "structure_overrides": []}}})
    wj(D / "worldgen/biome/ship_graveyard.json", {
        "has_precipitation": False, "temperature": 0.5, "downfall": 0.9,
        "effects": {"fog_color": 0x1A222C, "sky_color": 0x10161E, "water_color": 0x0E1A24, "water_fog_color": 0x050A10,
                    "particle": {"options": {"type": "minecraft:falling_water"}, "probability": 0.02},
                    "ambient_sound": "minecraft:weather.rain",
                    "mood_sound": {"sound": "minecraft:ambient.underwater.loop.additions.rare", "tick_delay": 6000, "block_search_extent": 8, "offset": 2.0}},
        "spawners": {}, "spawn_costs": {}, "carvers": {}, "features": []})


def fold():
    """The Grey Fold (BossArenas, GreyFoldShape): a burnt town floating in a rust-red ash sky, ash falling forever."""
    wj(D / "dimension_type/grey_fold.json", {
        "ultrawarm": False, "natural": False, "piglin_safe": False, "respawn_anchor_works": False, "bed_works": False,
        "has_raids": False, "has_skylight": True, "has_ceiling": False, "coordinate_scale": 1.0, "ambient_light": 0.0,
        "fixed_time": 13000, "logical_height": 384, "effects": "minecraft:overworld", "infiniburn": "#minecraft:infiniburn_overworld",
        "min_y": 0, "height": 384, "monster_spawn_light_level": 0, "monster_spawn_block_light_limit": 0})
    wj(D / "dimension/grey_fold.json", {"type": "ashbound:grey_fold", "generator": {"type": "minecraft:flat", "settings": {
        "biome": "ashbound:grey_fold", "features": False, "lakes": False, "layers": [{"block": "minecraft:air", "height": 1}],
        "structure_overrides": []}}})
    wj(D / "worldgen/biome/grey_fold.json", {
        "has_precipitation": False, "temperature": 1.0, "downfall": 0.0,
        "effects": {"fog_color": 0x3A1A12, "sky_color": 0x4A1C10, "water_color": 4159204, "water_fog_color": 329011,
                    "particle": {"options": {"type": "ashbound:ash_flake"}, "probability": 0.03},
                    "ambient_sound": "minecraft:ambient.soul_sand_valley.loop",
                    "mood_sound": {"sound": "minecraft:ambient.soul_sand_valley.mood", "tick_delay": 6000, "block_search_extent": 8, "offset": 2.0}},
        "spawners": {}, "spawn_costs": {}, "carvers": {}, "features": []})


def astral():
    """Veyra's Astral Rings (BossArenas, AstralShape): out past the sky, black and full of stars, always night."""
    for ring, fog in (("moth", 0x140A20), ("knight", 0x080C1C), ("magus", 0x0C0A18)):
        wj(D / ("dimension_type/astral_%s.json" % ring), {
            "ultrawarm": False, "natural": False, "piglin_safe": False, "respawn_anchor_works": False, "bed_works": False,
            "has_raids": False, "has_skylight": True, "has_ceiling": False, "coordinate_scale": 1.0, "ambient_light": 0.0,
            "fixed_time": 18000, "logical_height": 384, "effects": "minecraft:overworld", "infiniburn": "#minecraft:infiniburn_overworld",
            "min_y": 0, "height": 384, "monster_spawn_light_level": 0, "monster_spawn_block_light_limit": 0})
        wj(D / ("dimension/astral_%s.json" % ring), {"type": "ashbound:astral_" + ring, "generator": {"type": "minecraft:flat", "settings": {
            "biome": "ashbound:astral_" + ring, "features": False, "lakes": False, "layers": [{"block": "minecraft:air", "height": 1}],
            "structure_overrides": []}}})
        wj(D / ("worldgen/biome/astral_%s.json" % ring), {
            "has_precipitation": False, "temperature": 0.5, "downfall": 0.0,
            "effects": {"fog_color": fog, "sky_color": 0x000000, "water_color": 4159204, "water_fog_color": 329011,
                        "particle": {"options": {"type": "minecraft:end_rod"}, "probability": 0.002},
                        "ambient_sound": "minecraft:ambient.basalt_deltas.additions",
                        "mood_sound": {"sound": "minecraft:ambient.cave", "tick_delay": 6000, "block_search_extent": 8, "offset": 2.0}},
            "spawners": {}, "spawn_costs": {}, "carvers": {}, "features": []})


def crown():
    """The Crown Gate (BossArenas, CrownShape): beyond the oldest crack, a dark red night, embers drifting."""
    wj(D / "dimension_type/crown_gate.json", {
        "ultrawarm": True, "natural": False, "piglin_safe": False, "respawn_anchor_works": False, "bed_works": False,
        "has_raids": False, "has_skylight": True, "has_ceiling": False, "coordinate_scale": 1.0, "ambient_light": 0.0,
        "fixed_time": 18000, "logical_height": 384, "effects": "minecraft:overworld", "infiniburn": "#minecraft:infiniburn_overworld",
        "min_y": 0, "height": 384, "monster_spawn_light_level": 0, "monster_spawn_block_light_limit": 0})
    wj(D / "dimension/crown_gate.json", {"type": "ashbound:crown_gate", "generator": {"type": "minecraft:flat", "settings": {
        "biome": "ashbound:crown_gate", "features": False, "lakes": False, "layers": [{"block": "minecraft:air", "height": 1}],
        "structure_overrides": []}}})
    wj(D / "worldgen/biome/crown_gate.json", {
        "has_precipitation": False, "temperature": 2.0, "downfall": 0.0,
        "effects": {"fog_color": 0x200808, "sky_color": 0x140404, "water_color": 4159204, "water_fog_color": 329011,
                    "particle": {"options": {"type": "ashbound:ash_ember"}, "probability": 0.01},
                    "ambient_sound": "minecraft:ambient.nether_wastes.loop",
                    "mood_sound": {"sound": "minecraft:ambient.nether_wastes.mood", "tick_delay": 6000, "block_search_extent": 8, "offset": 2.0}},
        "spawners": {}, "spawn_costs": {}, "carvers": {}, "features": []})


def king():
    """The King in the Lord's Keep (Act V): Aldric, last of the Founder's line. His look borrowed from an old townsman for now."""
    wj(D / "npc/king.json", {
        "name": "King Aldric", "title": "of Highmourn", "start": "start",
        "nodes": {
            "start": {
                "go_if": [["flag:ch:act5_crown_gate", "after"]],
                "text": ["You're the one the Guild talks about. The one who goes into the cracks and comes back.",
                         "Sit, if you like. Not many people sit in this room any more."],
                "options": [{"text": "Open the Crown Gate.", "if": "has:ashbound:crown_key:1", "do": "bossarena:enter:crown"},
                            {"text": "Tell me about the keep.", "go": "keep"},
                            {"text": "Your Majesty.", "do": "close"}]},
            "keep": {
                "text": ["My family built it over the oldest crack in the world, and told everybody it was to guard the city.",
                         "It was. Just not from what they thought."],
                "options": [{"text": "Your Majesty.", "do": "close"}]},
            "after": {
                "text": ["The Founder's gone, and the gates are only gates now. Cracks, not a prison door.",
                         "Highmourn owes you more than I can pay. Come and sit in this room whenever you like."],
                "options": [{"text": "Open the Crown Gate.", "if": "has:ashbound:crown_key:1", "do": "bossarena:enter:crown"},
                            {"text": "Your Majesty.", "do": "close"}]},
        },
        "tags": ["lead", "elder", "m"]})
    # his look is his own now (11/7): tools/npc_specs_hand/king.json + mcstyle.king_crown, `python tools/mcexport.py king --install`


def veyra():
    wj(D / "npc/veyra.json", {
        "name": "Veyra", "title": "the Ringkeeper", "start": "start",
        "nodes": {
            "start": {
                "go_if": [["flag:ring_proved", "menu"], ["flag:ring_mark", "proof"], ["flag:ring_asked", "waiting"]],
                "text": ["You have the look of someone who's been through a gate or two. Not enough of them, maybe.",
                         "I keep the Ashen Ring. A colosseum that hangs over the clouds, somewhere that isn't anywhere. The whole city goes to watch."],
                "options": [{"text": "Wendel says you can send us to the Kiln-Father.", "if": "cold_brand", "do": "bossarena:enter:hearth"},
                            {"text": "The Archmage gave me the Drowned Sigil. Send us to the Wreck-Mother.", "if": "has:ashbound:drowned_sigil:1", "do": "bossarena:enter:wreck"},
                            {"text": "I have the Ashen Sigil. Send us to the Ash Shepherd.", "if": "has:ashbound:ashen_sigil:1", "do": "bossarena:enter:fold"},
                            {"text": "Open the Moth's Ring.", "if": "has:ashbound:sigil_moth:1", "do": "bossarena:enter:moth"},
                            {"text": "Open the Knight's Ring.", "if": "has:ashbound:sigil_knight:1", "do": "bossarena:enter:knight"},
                            {"text": "Open the Magus's Ring.", "if": "has:ashbound:sigil_magus:1", "do": "bossarena:enter:magus"},
                            {"text": "What happens in the Ring?", "go": "about"},
                            {"text": "I want to fight there.", "go": "ask"},
                            {"text": "Who's gone deepest?", "do": "arena:records"},
                            {"text": "Another time.", "do": "close"}]},
            "about": {
                "text": ["Monsters come through its four gates, wave after wave, out of every dungeon the Guild has charted. Each wave harder than the last. Every tenth, something that rules a gate.",
                         "Every five waves I give you a breath, and the crowd throws down what you've earned. Then you choose: on, or out with it. Reach the tenth, the twentieth, the thirtieth, and I'll remember. Next time you can start from there."],
                "options": [{"text": "I want to fight there.", "go": "ask", "if": "!ring_asked"},
                            {"text": "Goodbye.", "do": "close"}]},
            "ask": {
                "text": ["Not yet. The crowd wants to see blood that means something.",
                         "Go through a gate of E rank or worse. Kill what rules it. Come back to me with its blood still on you, and I'll open the Ring for you and anyone who fights at your side."],
                "options": [{"text": "I'll be back.", "do": "flag:ring_asked"}]},
            "waiting": {
                "text": ["No blood on you yet. An E-rank gate or worse, and what rules it. I'll be here."],
                "options": [{"text": "Wendel says you can send us to the Kiln-Father.", "if": "cold_brand", "do": "bossarena:enter:hearth"},
                            {"text": "The Archmage gave me the Drowned Sigil. Send us to the Wreck-Mother.", "if": "has:ashbound:drowned_sigil:1", "do": "bossarena:enter:wreck"},
                            {"text": "I have the Ashen Sigil. Send us to the Ash Shepherd.", "if": "has:ashbound:ashen_sigil:1", "do": "bossarena:enter:fold"},
                            {"text": "Open the Moth's Ring.", "if": "has:ashbound:sigil_moth:1", "do": "bossarena:enter:moth"},
                            {"text": "Open the Knight's Ring.", "if": "has:ashbound:sigil_knight:1", "do": "bossarena:enter:knight"},
                            {"text": "Open the Magus's Ring.", "if": "has:ashbound:sigil_magus:1", "do": "bossarena:enter:magus"},
                            {"text": "Who's gone deepest?", "do": "arena:records"},
                            {"text": "I'm going.", "do": "close"}]},
            "proof": {
                "text": ["There it is. I can smell the gate on you.",
                         "Good. The Ring is open to you now, and to your party. Bring them here when you're ready: I send everyone standing near you."],
                "options": [{"text": "Then send us.", "go": "menu", "do": "flag:ring_proved"}]},
            "menu": {
                "text": ["The stands are already full. They've heard about you.",
                         "Everyone of your party standing near you goes in with you. Ready?"],
                "options": [{"text": "Send us in, from the first wave.", "do": "arena:start"},
                            {"text": "Send us in from our milestone.", "if": "ring_m10", "do": "arena:best"},
                            {"text": "Wendel says you can send us to the Kiln-Father.", "if": "cold_brand", "do": "bossarena:enter:hearth"},
                            {"text": "The Archmage gave me the Drowned Sigil. Send us to the Wreck-Mother.", "if": "has:ashbound:drowned_sigil:1", "do": "bossarena:enter:wreck"},
                            {"text": "I have the Ashen Sigil. Send us to the Ash Shepherd.", "if": "has:ashbound:ashen_sigil:1", "do": "bossarena:enter:fold"},
                            {"text": "Open the Moth's Ring.", "if": "has:ashbound:sigil_moth:1", "do": "bossarena:enter:moth"},
                            {"text": "Open the Knight's Ring.", "if": "has:ashbound:sigil_knight:1", "do": "bossarena:enter:knight"},
                            {"text": "Open the Magus's Ring.", "if": "has:ashbound:sigil_magus:1", "do": "bossarena:enter:magus"},
                            {"text": "Who's gone deepest?", "do": "arena:records"},
                            {"text": "Not yet.", "do": "close"}]},
        },
        "tags": ["lead"]})
    # her look is her own now (11/7): tools/npc_specs_hand/veyra.json + mcstyle.veyra_ring, `python tools/mcexport.py veyra --install`


def lang():
    lp = A / "lang/en_us.json"
    lang = json.load(open(lp, encoding="utf-8"))
    lang.update({"block.ashbound.arena_sand": "Ring Sand", "block.ashbound.arena_rune": "Ring Rune"})
    json.dump(lang, open(lp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    textures()
    dimension()
    hearth()
    wreck()
    fold()
    astral()
    crown()
    king()
    veyra()
    lang()
    print("done")
