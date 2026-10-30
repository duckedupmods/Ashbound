"""The Silk Archive's sculpted props as blocks: the meshes tools/blender/silk_assets.py made (models/mesh/*.obj and
their baked textures) drawn by NeoForge's OBJ loader, turned by their blockstates.

  cocoon            pose=stand (two tall), seat (in a reading chair), hang (three tall, from the web), pressed
                    (in a book press); pose=upper fills the blocks a tall one reaches into (drawn by the one below)
  archive_papers    a reader's desk, low=true when it lies on a slab (the mesh sinks half a block onto it)
  paper_ream        a block of paper bound with cord
  moonglass_lamp    the hanging orb lamp

    blender -b -P tools/blender/silk_assets.py      (the meshes and textures, first)
    python tools/silkmeshes.py
"""
import json
import os

import port_weapons as P

A = P.ASSETS
FACING_Y = {"north": 0, "east": 90, "south": 180, "west": 270}
MESH = {"cocoon_stand": "silk_cocoon_stand", "cocoon_seat": "silk_cocoon_seat", "cocoon_hang": "silk_cocoon_hang",
        "cocoon_pressed": "silk_cocoon_pressed", "archive_papers_low": "parchment_desk", "archive_papers": "parchment_floor",
        "paper_ream": "parchment_full", "moonglass_lamp": "archive_lamp"}
NAMES = {"cocoon": "Silk Cocoon", "archive_papers": "Archive Papers", "paper_ream": "Ream of Parchment",
         "moonglass_lamp": "Moonglass Lamp"}
TOOLS = {"hoe": ["cocoon"], "axe": ["archive_papers", "paper_ream"], "pickaxe": ["moonglass_lamp"]}


def floor_copy():
    """the desk's papers lifted half a block, to lie on a floor instead of a slab"""
    src = A + "models/mesh/parchment_desk.obj"
    out = []
    for l in open(src, encoding="utf-8").read().splitlines():
        if l.startswith("v "):
            x, y, z = map(float, l.split()[1:])
            l = "v %.5f %.5f %.5f" % (x, y + 0.5, z)
        elif l.startswith("mtllib"):
            l = "mtllib parchment_floor.mtl"
        out.append(l)
    open(A + "models/mesh/parchment_floor.obj", "w", encoding="utf-8").write("\n".join(out) + "\n")
    tex = "ashbound:block/parchment_desk"
    open(A + "models/mesh/parchment_floor.mtl", "w", encoding="utf-8").write(
        "newmtl prop\nKa 0 0 0\nmap_Kd %s\n\nnewmtl glow\nKa 1 1 1\nmap_Kd %s\n" % (tex, tex))


def obj_model(name, mesh):
    tex = "ashbound:block/" + ("parchment_desk" if mesh == "parchment_floor" else mesh)
    P.dump(A + "models/block/%s.json" % name, {"loader": "neoforge:obj", "model": "ashbound:models/mesh/%s.obj" % mesh,
                                                "flip_v": True, "automatic_culling": False, "shade_quads": True,
                                                "render_type": "minecraft:cutout", "textures": {"particle": tex}})


def main():
    floor_copy()
    for n, mesh in MESH.items():
        obj_model(n, mesh)
    P.dump(A + "models/block/cocoon_upper.json", {"textures": {"particle": "ashbound:block/silk_cocoon_stand"}})
    BS = A + "blockstates/%s.json"
    v = {}
    for pose in ("stand", "seat", "hang", "pressed", "upper"):
        for f, y in FACING_Y.items():
            e = {"model": "ashbound:block/cocoon_" + pose}
            if y:
                e["y"] = y
            v["facing=%s,pose=%s" % (f, pose)] = e
    P.dump(BS % "cocoon", {"variants": v})
    v = {}
    for low in ("false", "true"):
        for f, y in FACING_Y.items():
            e = {"model": "ashbound:block/archive_papers" + ("_low" if low == "true" else "")}
            if y:
                e["y"] = y
            v["facing=%s,low=%s" % (f, low)] = e
    P.dump(BS % "archive_papers", {"variants": v})
    P.dump(BS % "paper_ream", {"variants": {"facing=%s" % f: dict({"model": "ashbound:block/paper_ream"}, **({"y": y} if y else {}))
                                            for f, y in FACING_Y.items()}})
    P.dump(BS % "moonglass_lamp", {"variants": {"": {"model": "ashbound:block/moonglass_lamp"}}})
    items = {"cocoon": "cocoon_pressed", "archive_papers": "archive_papers", "paper_ream": "paper_ream", "moonglass_lamp": "moonglass_lamp"}
    for n, m in items.items():
        P.dump(A + "models/item/%s.json" % n, {"parent": "ashbound:block/" + m})
        P.dump(P.DATA + "loot_table/blocks/%s.json" % n, {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [
            {"type": "minecraft:item", "name": "ashbound:" + n}], "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
    lang = json.load(open(A + "lang/en_us.json", encoding="utf-8"))
    lang.update({"block.ashbound." + n: t for n, t in NAMES.items()})
    P.dump(A + "lang/en_us.json", lang)
    tag = P.GAME + "src/main/resources/data/minecraft/tags/block/mineable/%s.json"
    for tool, names in TOOLS.items():
        path = tag % tool
        have = json.load(open(path, encoding="utf-8"))["values"] if os.path.exists(path) else []
        P.dump(path, {"replace": False, "values": have + ["ashbound:" + n for n in names if "ashbound:" + n not in have]})
    print("silk meshes: %d blocks" % len(NAMES))


if __name__ == "__main__":
    main()
