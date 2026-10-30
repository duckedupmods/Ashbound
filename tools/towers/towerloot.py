"""Every tower's two loot tables: its floor coffers (its own drops, plain goods and a small chance at a world weapon) and its boss's hoard
(the heart, enough drops to make armour, the world's weapons tilted rare).
No dungeon gear: the weapons come from the world's own (worldarms.py, world_arms.json)."""
import json
import os

GAME = "E:/EFTest/game/src/main/resources/"


def item(n, w, lo=1, hi=1):
    e = {"type": "minecraft:item", "name": n, "weight": w}
    if hi > 1:
        e["functions"] = [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}}]
    return e


def arms(weights, empty=0, chance=None):
    """one roll over the world's weapons; chance (0-1) sets the empty weight so that's how often one comes up"""
    world = json.load(open(GAME + "ashbound/world_arms.json", encoding="utf-8"))
    if chance:
        total = sum(weights[a["rarity"]] for a in world)
        empty = round(total * (1 - chance) / chance)
    return {"rolls": 1, "entries": ([{"type": "minecraft:empty", "weight": empty}] if empty else []) +
            [item("ashbound:" + a["id"], weights[a["rarity"]]) for a in world]}


def write(short, gate, goods=()):
    """short: the tables' name (tower_<short>); gate: its gear.json entry (its drops)"""
    g = json.load(open(GAME + "ashbound/gear.json", encoding="utf-8"))
    me = next(d for d in g if d["gate"] == gate)
    mats = [m["id"] for m in me["mats"]]
    plain = [item("minecraft:gold_ingot", 5, 1, 4), item("minecraft:iron_ingot", 6, 2, 6), item("minecraft:diamond", 1),
             item("minecraft:golden_apple", 1), item("minecraft:experience_bottle", 3, 1, 4), item("minecraft:cooked_beef", 4, 2, 6)]
    plain += [item(n, w, lo, hi) for (n, w, lo, hi) in goods]
    t = {"type": "minecraft:chest", "pools": [
        {"rolls": {"type": "minecraft:uniform", "min": 1, "max": 3}, "entries": [item("ashbound:" + mats[0], 6, 2, 6), item("ashbound:" + mats[1], 1)]},
        {"rolls": {"type": "minecraft:uniform", "min": 2, "max": 5}, "entries": plain},
        arms({"uncommon": 12, "rare": 6, "epic": 2, "legendary": 1}, chance=0.02)]}           # once in a while a world weapon
    os.makedirs(GAME + "data/ashbound/loot_table/chests", exist_ok=True)
    json.dump(t, open(GAME + "data/ashbound/loot_table/chests/tower_%s.json" % short, "w"), indent=1)
    t = {"type": "minecraft:chest", "pools": [
        {"rolls": 1, "entries": [item("ashbound:" + mats[2], 1)]},                       # the boss's heart, always
        {"rolls": 1, "entries": [item("ashbound:" + mats[1], 1, 3, 5)]},                 # enough to make armour
        {"rolls": 1, "entries": [item("ashbound:" + mats[0], 1, 14, 22)]},
        arms({"uncommon": 2, "rare": 6, "epic": 6, "legendary": 3}),                      # a world weapon, tilted rare
        arms({"uncommon": 12, "rare": 6, "epic": 2, "legendary": 1}, chance=0.15),        # and now and then another
        {"rolls": {"type": "minecraft:uniform", "min": 3, "max": 6}, "entries": [
            item("minecraft:gold_ingot", 5, 3, 8), item("minecraft:diamond", 3, 1, 3), item("minecraft:emerald", 3, 2, 6),
            item("minecraft:golden_apple", 2), item("minecraft:experience_bottle", 4, 3, 8), item("minecraft:iron_ingot", 4, 4, 10)]}]}
    json.dump(t, open(GAME + "data/ashbound/loot_table/chests/tower_%s_boss.json" % short, "w"), indent=1)
    print("loot: tower_%s + boss hoard (world weapons only)" % short)
