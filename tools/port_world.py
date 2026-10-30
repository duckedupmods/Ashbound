"""Brings Ashbound's forests (E:/Ashbound, Minecraft 26.3) over to the Epic Fight add-on (1.21.1):

  * the wildwood blocks the trees are built from (blockstates, models, textures, names),
  * every tree template (structure/tree/*.nbt), its blocks renamed to ones 1.21.1 has,
  * the forests: our tree features in place of vanilla's per-biome trees and its saplings' trees,
    the giant trees and the highwoods as structures, written in 1.21.1's data format.

    python tools/port_world.py
"""
import glob
import json
import os
import shutil
import zipfile

import nbtio
import port_weapons as P

SRC = "E:/Ashbound/src/main/resources/"
JAR = os.path.expanduser("~/.gradle/caches/neoformruntime/artifacts/minecraft_1.21.1_client.jar")
DATA_VERSION = 3955          # 1.21.1's: stamped so, the game reads our templates as they are

BLOCKS = ["wildwood_log", "wildwood_wood", "mossy_wildwood_wood", "wildwood_leaves", "wildwood_leaves_sunlit",
          "wildwood_leaves_shade", "wildwood_blossom", "wildwood_leaves_amber", "wildwood_leaves_crimson",
          "wildwood_leaves_rose", "wildwood_needles", "wildwood_leaves_lilac", "mossy_fieldstone", "mossy_fieldstone_slab",
          "vigil_candles"]
# blocks 26.3 has and 1.21.1 doesn't
RENAME = {"minecraft:iron_chain": "minecraft:chain", "minecraft:stripped_pale_oak_wood": "minecraft:stripped_birch_wood"}


def vanilla_names(folder):
    with zipfile.ZipFile(JAR) as z:
        return {n.split("/")[-1][:-5] for n in z.namelist() if n.startswith(folder) and n.endswith(".json")}


# ================================================================ blocks

def blocks():
    A = SRC + "assets/ashbound/"
    models, textures = set(), set()

    def model(ref):
        if not ref.startswith("ashbound:") or ref in models:
            return
        models.add(ref)
        m = json.load(open(A + "models/" + ref[9:] + ".json", encoding="utf-8"))
        if "parent" in m:
            model(m["parent"])
        for t in m.get("textures", {}).values():
            if t.startswith("ashbound:"):
                textures.add(t[9:])
    for b in BLOCKS:
        st = json.load(open(A + "blockstates/%s.json" % b, encoding="utf-8"))
        P.dump(P.ASSETS + "blockstates/%s.json" % b, st)
        for v in st.get("variants", {}).values():
            for one in v if isinstance(v, list) else [v]:
                model(one["model"])
        # 1.21.1's items take their block's model
        P.dump(P.ASSETS + "models/item/%s.json" % b, {"parent": "ashbound:block/" + b})
    for ref in models:
        m = json.load(open(A + "models/" + ref[9:] + ".json", encoding="utf-8"))
        if "leaves" in ref or "needles" in ref or "blossom" in ref:
            m["render_type"] = "minecraft:cutout_mipped"     # see-through between the leaves
        P.dump(P.ASSETS + "models/" + ref[9:] + ".json", m)
    for t in textures:
        for ext in (".png", ".png.mcmeta"):
            if os.path.exists(A + "textures/" + t + ext):
                os.makedirs(os.path.dirname(P.ASSETS + "textures/" + t + ext), exist_ok=True)
                shutil.copy(A + "textures/" + t + ext, P.ASSETS + "textures/" + t + ext)
    # vanilla's tags they're in (logs, leaves, which tool mines them...), only ours
    ids = {"ashbound:" + b for b in BLOCKS}
    for path in glob.glob(SRC + "data/minecraft/tags/**/*.json", recursive=True):
        vals = [v for v in json.load(open(path, encoding="utf-8")).get("values", []) if v in ids]
        if vals:
            rel = os.path.relpath(path, SRC + "data/minecraft").replace("\\", "/")
            P.dump(P.GAME + "src/main/resources/data/minecraft/" + rel, {"replace": False, "values": vals})
    lang = json.load(open(A + "lang/en_us.json", encoding="utf-8"))
    ours = json.load(open(P.ASSETS + "lang/en_us.json", encoding="utf-8"))
    ours.update({"block.ashbound." + b: lang["block.ashbound." + b] for b in BLOCKS})
    P.dump(P.ASSETS + "lang/en_us.json", ours)
    print("blocks: %d, %d models, %d textures" % (len(BLOCKS), len(models), len(textures)))


# ================================================================ templates

def templates():
    have = vanilla_names("assets/minecraft/blockstates/")
    out = P.DATA + "structure/tree/"
    os.makedirs(out, exist_ok=True)
    unknown = set()
    n = 0
    for path in glob.glob(SRC + "data/ashbound/structure/tree/*.nbt"):
        root = nbtio.read(path)
        root["DataVersion"] = nbtio.Tag(3, DATA_VERSION)
        for e in root["palette"][2]:
            name = RENAME.get(e["Name"], e["Name"])
            ns, short = name.split(":")
            if ns == "minecraft" and short not in have or ns == "ashbound" and short not in BLOCKS:
                unknown.add(name)
            e["Name"] = name
        nbtio.write(out + os.path.basename(path), root)
        n += 1
    os.makedirs(P.DATA + "tree", exist_ok=True)
    shutil.copy(SRC + "data/ashbound/tree/offsets.json", P.DATA + "tree/offsets.json")
    print("templates: %d" % n, "  UNKNOWN BLOCKS: %s" % sorted(unknown) if unknown else "")


# ================================================================ the forests

def forest_tables():
    """forest.py's tables, read from its source (importing it would load the 26.3 game jar)."""
    src = open("E:/Ashbound/tools/forest.py", encoding="utf-8").read()
    ns = {"os": os, "K": type("K", (), {"ROOT": "E:/Ashbound"})}
    exec(src[src.index("SIZES = "):src.index("\n", src.index("SIZES = "))], ns)
    exec(src[src.index("VARIANTS = "):src.index("def write")], ns)
    exec(src[src.index("HIGHWOODS = "):src.index("def export")], ns)
    return ns


def forests():
    T = forest_tables()
    feats = vanilla_names("data/minecraft/worldgen/configured_feature/")
    placed = vanilla_names("data/minecraft/worldgen/placed_feature/")
    biomes = vanilla_names("data/minecraft/worldgen/biome/")
    # 26.3 renamed some of vanilla's placements; the rest of the missing ones are 26.3's own biomes' (the pale garden)
    old_name = {"trees_birch_and_oak_leaf_litter": "trees_birch_and_oak"}
    D = P.DATA + "worldgen/"
    V = P.GAME + "src/main/resources/data/minecraft/worldgen/"

    def entries(mix):
        out = []
        for kind, weights in T["MIXES"][mix]:
            for s, w in enumerate(weights):
                if w:
                    out += [{"template": "ashbound:tree/%s_%s_%d" % (kind, T["SIZES"][s], i), "weight": w}
                            for i in range(T["VARIANTS"])]
        for prefix, n, w in T["FLOOR"].get(mix, ()):
            out += [{"template": "ashbound:tree/%s_%d" % (prefix, i), "weight": w} for i in range(n)]
        cfg = {"trees": out}
        if mix in T["HARDY"]:
            cfg["hardy"] = True
        return {"type": "ashbound:tree", "config": cfg}
    skipped = []
    for mix in T["MIXES"]:
        P.dump(D + "configured_feature/%s.json" % mix, entries(mix))
    for v, mix in T["VANILLA_FEATURES"].items():
        if v in feats:
            P.dump(V + "configured_feature/%s.json" % v, entries(mix))
        else:
            skipped.append(v)
    for v, (mix, counts, *depth) in T["PLACED"].items():
        v = old_name.get(v, v)
        if v not in placed:
            skipped.append(v)
            continue
        P.dump(V + "placed_feature/%s.json" % v, {
            "feature": "ashbound:" + mix,
            "placement": [
                {"type": "minecraft:count", "count": {"type": "minecraft:weighted_list",
                                                       "distribution": [{"data": c, "weight": w} for c, w in counts]}},
                {"type": "minecraft:in_square"},
                {"type": "minecraft:surface_water_depth_filter", "max_water_depth": depth[0] if depth else 0},
                {"type": "minecraft:heightmap", "heightmap": "OCEAN_FLOOR"},
                {"type": "minecraft:biome"}]})
    tags = P.DATA + "tags/worldgen/biome/has_structure/"

    def structure(name, template, tag):
        P.dump(D + "structure/%s.json" % name, {
            "type": "ashbound:giant_tree", "template": template, "biomes": "#ashbound:has_structure/" + tag,
            "spawn_overrides": {}, "step": "surface_structures", "terrain_adaptation": "none"})
    for name, bs in T["GIANTS"].items():
        P.dump(tags + "giant_%s.json" % name, {"values": ["minecraft:" + b for b in bs if b in biomes]})
        structure("giant_" + name, "ashbound:tree/" + name, "giant_" + name)
    P.dump(D + "structure_set/giant_trees.json", {
        "placement": {"type": "minecraft:random_spread", "salt": 48120577, "separation": 14, "spacing": 36},
        "structures": [{"structure": "ashbound:giant_" + n, "weight": w} for n, w in (("elder", 4), ("weeper", 3), ("husk", 3))]})
    P.dump(tags + "highwood.json", {"values": ["minecraft:" + b for b in T["WILDWOOD_BIOMES"]]})
    for i in range(T["HIGHWOODS"]):
        structure("highwood_%d" % i, "ashbound:tree/highwood_%d" % i, "highwood")
    # two offset grids of them: the wildwood thick
    for set_name, salt in (("highwoods", 71203311), ("highwoods_dense", 91733021)):
        P.dump(D + "structure_set/%s.json" % set_name, {
            "placement": {"type": "minecraft:random_spread", "salt": salt, "separation": 1, "spacing": 2},
            "structures": [{"structure": "ashbound:highwood_%d" % i, "weight": 1} for i in range(T["HIGHWOODS"])]})
    print("forests: %d features, %d giants, %d highwoods; not in 1.21.1: %s"
          % (len(T["MIXES"]), len(T["GIANTS"]), T["HIGHWOODS"], ", ".join(skipped)))


if __name__ == "__main__":
    blocks()
    templates()
    forests()
