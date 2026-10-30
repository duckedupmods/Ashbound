"""Puts a Roster v2 dungeon into the add-on, every part made here rather than ported from E:/Ashbound:

    blocks   blockforge.py paints its masonry (gate_blocks.json)
    props    the meshes from blender/kit_props.py (run it first) registered (gate_blocks.json)
    mobs     monsterforge.py builds each monster into tools/mob_src, efmob fits it to Epic Fight's skeleton
             (gate_mobs.json)
    lair     lairs/forge_lair.py stages the layout, port_gate swaps in nothing (it's all ours) and writes it
    loot     its coffers' loot table (its own drops and some treasure)

    blender -b -P tools/blender/kit_props.py -- <gate>
    python tools/newgate.py <gate> [blocks] [props] [mobs] [lair] [loot]      (all when none is named)
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "lairs"))
sys.path.insert(0, "E:/Ashbound/tools")

import port_weapons as P  # noqa: E402
import port_gate as PG  # noqa: E402
import dforge  # noqa: E402
import forge_specs as FS  # noqa: E402
import gear as G  # noqa: E402


def gear_of(gate):
    """its gear.json entry; a world faction (tools/mobs/black_banner.py) has none"""
    return next((d for d in G.D if d["gate"] == gate), {})


def mobs(gate):
    import monsterforge as MF
    d = gear_of(gate)
    spec = {}
    for mid in FS.by_gate(gate):
        s = FS.SPECS[mid]
        B = MF.export(mid, s)
        w, h = s.get("ent", (1.0, 2.8))
        e = dict(entity=(mid, w, h, s.get("fire", False)), stats=s.get("stats", {}))
        if mid == d.get("elite") or s.get("key"):
            e["key"] = True
        if mid == d.get("boss") or s.get("boss"):
            e["boss"] = True
        if hasattr(B, "joints"):
            e.update(rig="spider", joints=B.joints, root="body")
        spec[mid] = e
    PG.port_mobs({"mobs": spec})


def lair(gate):
    subprocess.run([sys.executable, os.path.join(HERE, "lairs", "forge_lair.py"), gate, "--game"], check=True,
                   env=dict(os.environ, PYTHONPATH=os.pathsep.join([os.path.join(HERE, "lairs"), HERE, "E:/Ashbound/tools"])))
    PG.port_lair(gate, {"lair": "gate_" + gate, "swap": {}})


def loot(gate):
    d = next(g for g in json.load(open(P.GAME + "src/main/resources/ashbound/gear.json", encoding="utf-8")) if g["gate"] == gate)
    common, elite = d["mats"][0]["id"], d["mats"][1]["id"]
    rank = "FEDCBAS".index(d["rank"])
    t = {"type": "minecraft:chest", "pools": [
        {"rolls": {"type": "minecraft:uniform", "min": 2, "max": 4}, "entries": [
            {"type": "minecraft:item", "name": "ashbound:" + common, "weight": 6,
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 2, "max": 5}}]},
            {"type": "minecraft:item", "name": "ashbound:" + elite, "weight": 2}]},
        {"rolls": {"type": "minecraft:uniform", "min": 2, "max": 4}, "entries": [
            {"type": "minecraft:item", "name": "minecraft:gold_ingot", "weight": 5,
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 1, "max": 3 + rank}}]},
            {"type": "minecraft:item", "name": "minecraft:iron_ingot", "weight": 6,
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 2, "max": 5}}]},
            {"type": "minecraft:item", "name": "minecraft:diamond", "weight": 1 + rank},
            {"type": "minecraft:item", "name": "minecraft:golden_apple", "weight": 1 + rank // 2},
            {"type": "minecraft:item", "name": "minecraft:experience_bottle", "weight": 3,
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 1, "max": 4}}]},
            {"type": "minecraft:item", "name": "minecraft:cooked_beef", "weight": 4,
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 2, "max": 6}}]}]}]}
    P.dump(P.DATA + "loot_table/chests/gate_%s.json" % gate, t)


def main():
    gate = sys.argv[1]
    steps = sys.argv[2:] or ["blocks", "props", "mobs", "lair", "loot"]
    if "blocks" in steps:
        import blockforge
        blockforge.forge(gate)
    if "props" in steps:
        PG.port_props({"props": dforge.DUNGEONS[gate]["props"]})
    if "mobs" in steps:
        mobs(gate)
    if "lair" in steps:
        lair(gate)
    if "loot" in steps:
        loot(gate)


if __name__ == "__main__":
    main()
