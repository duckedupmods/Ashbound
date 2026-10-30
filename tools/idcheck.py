"""Every id the add-on registers, from every data file, checked for clashes (two things under one name crash the game)."""
import collections
import json
import glob
import os
import re

GAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
R = GAME + "src/main/resources/ashbound/"
ids = collections.defaultdict(list)
gb = json.load(open(R + "gate_blocks.json", encoding="utf-8"))
for b in gb["blocks"] + gb["props"]:
    ids[b["name"]].append("block")
for m in json.load(open(R + "gate_mobs.json", encoding="utf-8")):
    ids[m["id"] + "_spawn_egg"].append("egg")
for g in json.load(open(R + "gear.json", encoding="utf-8")):
    for m in g["mats"]:
        ids[m["id"]].append("mat")
    for w in g["weapons"]:
        ids[w["id"]].append("weapon")
    for s in g["sets"]:
        for p in s["pieces"]:
            ids[p["id"]].append("armour")
# blocks and items registered by hand in the Java (the city, the sculpts, the world): a data id must not reuse one
JAVA = r'(?:block|registerBlock|registerItem|registerSimpleItem)\(\s*"([a-z0-9_]+)"'
for f in glob.glob(GAME + "src/main/java/com/snoringwalrus/ashbound/*.java"):
    if os.path.basename(f) in ("GateBlocks.java", "Gear.java", "Armors.java", "GateMobs.java"):
        continue
    for m in set(re.findall(JAVA, open(f, encoding="utf-8").read())):
        ids[m].append("java:" + os.path.basename(f)[:-5])
bad = {k: v for k, v in ids.items() if len(v) > 1}
print("ids", len(ids), "clashes", bad or "none")
