"""Ashbound terrain on 1.21.1: taller, sharper mountains over the vanilla world, the low vales left flat for the towns.
(E:/Ashbound's tools/terrain.py, the same knobs, written for 1.21.1's density-function format.)

    python tools/terrain.py --export          writes the overrides into the mod (data/minecraft/...)
    python tools/terrain.py --off             removes them again (vanilla terrain)

The overrides wrap Minecraft's own density functions (read from the game jar), so the climate, the biomes and
the caves stay vanilla's; only how high the land stands changes:
  * the world goes up to y 447 (dimension and noise height 512),
  * the land's height (offset) is raised above the lowlands, more the higher it already is,
  * the peaks' jaggedness is scaled up,
  * the fade to air at the top of the world moves up with it,
  * high steep ground is bare rock, the tops snow.
A changed world height only takes in a NEW world.
"""
import copy
import json
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JAR = os.path.expanduser("~/.gradle/caches/neoformruntime/artifacts/minecraft_1.21.1_client.jar")
DATA = os.path.join(ROOT, "src", "main", "resources", "data")

# ================================================================ the knobs (as E:/Ashbound's)

MIN_Y, HEIGHT = -64, 512          # vanilla 384: up to y 447
FADE = (400, 432)                 # vanilla 240..256: land thins to air between these heights
LOW = -0.2                        # offset under this (land under y ~102) is left as it is
LIFT = (0.8, 3.2, 1.7)            # offset += min(a*e + b*e*e, c), e = how far over LOW it stands
JAG = 2.2                         # peaks' jaggedness, times vanilla's
SCALE = 0.2                       # vanilla 0.25: continents, erosion and ridges this much wider (bigger ranges)
LAND = 0.10                       # added to continentalness: less sea
RUGGED = -0.06                    # added to erosion: more of the land mountainous
ROCK = 215                        # over this, steep ground is bare stone in every biome
SNOW = 285                        # over this, the ground is snow (steep: stone) where the biome isn't snowy already


def vanilla(rel):
    with zipfile.ZipFile(JAR) as z:
        return json.loads(z.read("data/minecraft/" + rel))


def add(a, b):
    return {"type": "minecraft:add", "argument1": a, "argument2": b}


def mul(a, b):
    return {"type": "minecraft:mul", "argument1": a, "argument2": b}


def gradient():
    """Vanilla's y gradient (1.5 at -64, -1.5 at 320), stretched to the new height at the same slope."""
    top = MIN_Y + HEIGHT - 1
    return {"type": "minecraft:y_clamped_gradient", "from_y": MIN_Y, "from_value": 1.5, "to_y": top,
            "to_value": 1.5 - 3.0 * HEIGHT / 384}


def retop(o):
    """The fade to air at 240..256, moved up."""
    if isinstance(o, list):
        return [retop(v) for v in o]
    if not isinstance(o, dict):
        return o
    o = {k: retop(v) for k, v in o.items()}
    if o.get("type") == "minecraft:y_clamped_gradient" and o.get("from_y") == 240 and o.get("to_y") == 256:
        o["from_y"], o["to_y"] = FADE
    return o


def blended(f):
    """flat_cache(cache_2d(add(...))): the part of vanilla's offset or jaggedness that's the land's own, not its
    blending into old chunks: the mul whose second (or first) half is blend_alpha."""
    return f["argument"]["argument"]["argument2"]


FILES = ["dimension_type/overworld.json", "worldgen/noise_settings/overworld.json"] + [
    "worldgen/density_function/overworld/%s.json" % n for n in ("depth", "offset", "jaggedness", "continents", "erosion", "ridges")]
OWN = ["worldgen/density_function/terrain/offset_raw.json", "worldgen/density_function/terrain/jagged_raw.json"]


def export():
    out = {}
    dim = vanilla("dimension_type/overworld.json")
    dim["height"] = dim["logical_height"] = HEIGHT
    dim["min_y"] = MIN_Y
    out["minecraft/dimension_type/overworld.json"] = dim
    ns = vanilla("worldgen/noise_settings/overworld.json")
    ns["noise"]["height"] = HEIGHT
    ns["noise"]["min_y"] = MIN_Y
    ns["noise_router"] = retop(ns["noise_router"])
    ns["surface_rule"] = material(ns["surface_rule"])
    out["minecraft/worldgen/noise_settings/overworld.json"] = ns
    D = "worldgen/density_function/overworld/"
    out["minecraft/" + D + "depth.json"] = add(gradient(), "minecraft:overworld/offset")
    # the land's height: vanilla's own (add(-0.50375, spline), times blend_alpha), lifted above the lowlands
    off = vanilla(D + "offset.json")
    part = blended(off)
    assert part["argument2"]["argument"]["type"] == "minecraft:blend_alpha", part
    out["ashbound/worldgen/density_function/terrain/offset_raw.json"] = {"type": "minecraft:cache_2d", "argument": part["argument1"]}
    raw = "ashbound:terrain/offset_raw"
    e = {"type": "minecraft:max", "argument1": add(raw, -LOW), "argument2": 0.0}
    lift = {"type": "minecraft:clamp", "min": 0.0, "max": LIFT[2],
            "input": add(mul(e, LIFT[0]), mul({"type": "minecraft:square", "argument": e}, LIFT[1]))}
    part["argument1"] = add(raw, lift)
    out["minecraft/" + D + "offset.json"] = off
    jag = vanilla(D + "jaggedness.json")
    part = blended(jag)
    assert part["argument1"]["type"] == "minecraft:blend_alpha", part
    out["ashbound/worldgen/density_function/terrain/jagged_raw.json"] = {"type": "minecraft:cache_2d", "argument": part["argument2"]}
    part["argument2"] = mul("ashbound:terrain/jagged_raw", JAG)
    out["minecraft/" + D + "jaggedness.json"] = jag
    # the climate the land and the biomes both read: changed here, the biomes still match the land
    for name, shift in (("continents", LAND), ("erosion", RUGGED), ("ridges", 0.0)):
        f = vanilla(D + name + ".json")
        assert f["argument"]["type"] == "minecraft:shifted_noise"
        f["argument"]["xz_scale"] = SCALE
        if shift:
            f["argument"] = add(f["argument"], shift)
        out["minecraft/" + D + name + ".json"] = f
    for rel, obj in out.items():
        p = os.path.join(DATA, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=1)
        print("  " + rel)


def material(rule):
    """Vanilla's ground rules with the heights' own first: bare rock on high cliffs, snow on the tops."""
    def above(y, m):
        return {"type": "minecraft:y_above", "anchor": {"absolute": y}, "surface_depth_multiplier": m, "add_stone_depth": False}

    def block(b):
        return {"type": "minecraft:block", "result_state": {"Name": "minecraft:" + b}}

    def cond(c, then):
        return {"type": "minecraft:condition", "if_true": c, "then_run": then}
    floor = {"type": "minecraft:stone_depth", "offset": 0, "add_surface_depth": False, "secondary_depth_range": 0, "surface_type": "floor"}
    steep = {"type": "minecraft:steep"}
    snowy = {"type": "minecraft:biome", "biome_is": ["minecraft:" + b for b in (
        "frozen_peaks", "jagged_peaks", "snowy_slopes", "grove", "snowy_plains", "ice_spikes", "snowy_taiga", "desert",
        "badlands", "eroded_badlands", "wooded_badlands")]}
    high = {"type": "minecraft:sequence", "sequence": [
        cond(floor, cond(above(SNOW, 3), cond({"type": "minecraft:not", "invert": snowy}, {
            "type": "minecraft:sequence", "sequence": [cond(steep, block("stone")), block("snow_block")]}))),
        cond(floor, cond(above(ROCK, 2), cond(steep, block("stone")))),
    ]}
    rule = copy.deepcopy(rule)
    top = next(r for r in rule["sequence"] if r.get("if_true", {}).get("type") == "minecraft:above_preliminary_surface")
    top["then_run"] = {"type": "minecraft:sequence", "sequence": [high, top["then_run"]]}
    return rule


def off():
    for rel in ["minecraft/" + f for f in FILES] + ["ashbound/" + f for f in OWN]:
        p = os.path.join(DATA, rel)
        if os.path.exists(p):
            os.remove(p)
            print("  removed " + rel)


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--export" in a:
        export()
    elif "--off" in a:
        off()
    else:
        print(__doc__)
