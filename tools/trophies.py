"""Legend trophies: the piece each Legend leaves when it falls, cut out of its own model (its bone's boxes at rest), set to
stand in one block. Mounted on a block (TrophyBlock), dropped by its Legend (Bounties / WorldBeasts).

    python tools/trophies.py preview      renders tools/renders/trophies/trophies_sheet.png (nothing in the game changes)
    python tools/trophies.py export       writes each trophy's mesh, texture, models and blockstate into the mod
"""
import json
import math
import os
import subprocess
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import beastkit as B  # noqa: E402
import connect_check as CC  # noqa: E402

V = B.V
GAME = Path(HERE).parent
ASSETS = GAME / "src/main/resources/assets/ashbound"
OUT = GAME / "tools/renders/trophies"
VOX = Path("E:/Ashbound/tools/renders/vox")

# id, legend, bones kept, tags left out, turn about y (deg) so its face looks out, how big (blocks, its longest side), name
TROPHIES = [
    ("penitents_bell", "rime_penitent", ["bell"], [], 0, 0.85, "The Penitent's Bell"),
    ("blackbriar_antlers", "old_blackbriar", ["head"], [], 0, 0.95, "Blackbriar's Antlered Skull"),
    ("red_ploughshare", "red_plough", ["ar_hand"], ["gauntlet", "knuckle"], 0, 0.95, "The Red Ploughshare"),
    ("sunbreaker_mirror", "sunbreaker", ["head"], [], 0, 0.9, "Sunbreaker's Mirror"),
    ("mires_lantern_staff", "grandmother_mire", ["ar_hand"], ["palm", "fist"], 0, 0.98, "Grandmother Mire's Lantern Staff"),
    ("hollow_smile_mask", "hollow_smile", ["head"], [], 0, 0.7, "The Hollow Smile's Mask"),
    ("old_harpoons_anchor", "old_harpoon", ["ar_hand"], ["fist"], 0, 0.95, "Old Harpoon's Anchor"),
    ("mountain_fort", "walking_mountain", ["fort"], [], 0, 0.95, "The Walking Mountain's Fort"),
]


def cut(tid, legend, bones, skip, turn, size):
    """the trophy's scene: the Legend at rest with only these bones' boxes, and how to put it in a block"""
    m = B.mod(legend)
    s, parts = m.make(legend, False)
    keep = {id(parts[b]) for b in bones}
    s.boxes = [b for b in s.boxes if id(b.part) in keep and b.tag not in skip]
    s.name = tid
    pts = [p for b in s.boxes for p in CC.aabb(b)]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    c = [(lo[i] + hi[i]) / 2 for i in range(3)]
    k = size / max(hi[i] - lo[i] for i in range(3))
    a = math.radians(turn)
    ca, sa = math.cos(a), math.sin(a)

    def to_block(p):
        x, y, z = (p[0] - c[0]) * k, (p[1] - lo[1]) * k, (p[2] - c[2]) * k
        return (x * ca + z * sa + 0.5, y, -x * sa + z * ca + 0.5)
    return s, to_block, [(hi[i] - lo[i]) * k for i in range(3)]


def write(s, to_block, obj, png):
    img, tris = s.build()
    img.save(png)
    old = V.to_item
    V.to_item = to_block
    try:
        V.write_obj(Path(obj), tris)
    finally:
        V.to_item = old
    return sum(len(t) for t in tris.values())


def preview():
    from PIL import Image, ImageDraw, ImageFont
    OUT.mkdir(parents=True, exist_ok=True)
    names = []
    for tid, legend, bones, skip, turn, size, _ in TROPHIES:
        s, to_block, dims = cut(tid, legend, bones, skip, turn, size)
        # the preview renderer reads model pixels: one block = 16
        n = write(s, lambda p: tuple(v * 16 for v in to_block(p)), VOX / ("%s_f0.obj" % tid), VOX / ("%s_f0.png" % tid))
        print("%-22s %5d tris  %.2f x %.2f x %.2f blocks" % (tid, n, *dims))
        names.append(tid)
    subprocess.run([B.BLENDER, "-b", "-P", str(Path(HERE) / "blender" / "trophy_preview.py"), "--", str(OUT)] + names,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    font = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 18)
    T = 360
    sheet = Image.new("RGB", (4 * T, 2 * (T + 34)), (30, 26, 24))
    d = ImageDraw.Draw(sheet)
    for i, (tid, *_, title) in enumerate(TROPHIES):
        x, y = (i % 4) * T, (i // 4) * (T + 34)
        p = OUT / ("%s.png" % tid)
        if p.exists():
            im = Image.open(p).convert("RGBA").resize((T, T), Image.LANCZOS)
            sheet.paste(im, (x, y), im)
        d.text((x + T / 2 - d.textlength(title, font=font) / 2, y + T + 6), title, font=font, fill=(226, 206, 164))
    sheet.save(OUT / "trophies_sheet.png")
    print(OUT / "trophies_sheet.png")


def export():
    lang_p = ASSETS / "lang/en_us.json"
    lang = json.load(open(lang_p, encoding="utf-8"))
    for tid, legend, bones, skip, turn, size, title in TROPHIES:
        s, to_block, dims = cut(tid, legend, bones, skip, turn, size)
        obj = ASSETS / ("models/mesh/trophy_%s.obj" % tid)
        n = write(s, to_block, obj, ASSETS / ("textures/block/trophy_%s.png" % tid))
        # the material file the obj names: its atlas, lit and glowing alike
        mtl = obj.with_suffix(".mtl")
        mtl.write_text("newmtl prop\nKa 0 0 0\nmap_Kd ashbound:block/trophy_%s\n\nnewmtl glow\nKa 1 1 1\nmap_Kd ashbound:block/trophy_%s\n" % (tid, tid))
        # every group says which: the obj loader draws a group with no usemtl untextured
        lines = ["mtllib %s" % mtl.name]
        for l in obj.read_text(encoding="utf-8").splitlines():
            if l.startswith(("mtllib", "usemtl")):
                continue
            lines.append(l)
            if l.startswith("g "):
                lines.append("usemtl " + ("glow" if l.split()[1] in ("fire", "glow") else "prop"))
        obj.write_text("\n".join(lines) + "\n", encoding="utf-8")
        model = {"loader": "neoforge:obj", "model": "ashbound:models/mesh/trophy_%s.obj" % tid, "flip_v": True,
                 "automatic_culling": False, "shade_quads": True, "render_type": "minecraft:cutout",
                 "textures": {"particle": "ashbound:block/trophy_%s" % tid},
                 "display": {"gui": {"rotation": [20, 200, 0], "translation": [0, -1.5, 0], "scale": [0.85, 0.85, 0.85]},
                             "ground": {"rotation": [0, 0, 0], "translation": [0, 2, 0], "scale": [0.4, 0.4, 0.4]},
                             "fixed": {"rotation": [0, 180, 0], "translation": [0, -2, 0], "scale": [0.8, 0.8, 0.8]},
                             "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.4, 0.4, 0.4]},
                             "thirdperson_lefthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.4, 0.4, 0.4]},
                             "firstperson_righthand": {"rotation": [0, 225, 0], "translation": [0, 0, 0], "scale": [0.4, 0.4, 0.4]},
                             "firstperson_lefthand": {"rotation": [0, 225, 0], "translation": [0, 0, 0], "scale": [0.4, 0.4, 0.4]}}}
        (ASSETS / ("models/block/trophy_%s.json" % tid)).write_text(json.dumps(model, indent=1), encoding="utf-8")
        (ASSETS / ("models/item/trophy_%s.json" % tid)).write_text(json.dumps({"parent": "ashbound:block/trophy_%s" % tid}, indent=1), encoding="utf-8")
        # its face looks the way the placer looked from (TrophyBlock.FACING): the mesh's front is +z, south
        (ASSETS / ("blockstates/trophy_%s.json" % tid)).write_text(json.dumps({"variants": {
            "facing=%s" % f: {"model": "ashbound:block/trophy_%s" % tid, "y": y}
            for f, y in (("south", 0), ("west", 90), ("north", 180), ("east", 270))}}, indent=1), encoding="utf-8")
        # broken, it comes back to you
        (GAME / ("src/main/resources/data/ashbound/loot_table/blocks/trophy_%s.json" % tid)).write_text(json.dumps({"type": "minecraft:block", "pools": [
            {"rolls": 1, "entries": [{"type": "minecraft:item", "name": "ashbound:trophy_%s" % tid}],
             "conditions": [{"condition": "minecraft:survives_explosion"}]}]}, indent=1), encoding="utf-8")
        lang["block.ashbound.trophy_" + tid] = title
        print("game %-22s %5d tris" % (tid, n))
    json.dump(lang, open(lang_p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    {"preview": preview, "export": export}[sys.argv[1]]()
