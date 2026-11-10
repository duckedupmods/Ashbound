"""A sheet of the whole cube cast (after tools/mcexport.py has written the preview meshes): leads, adventurers,
townsfolk, elves, dwarves and demons in named rows, every one labelled.

    python tools/mc_cast_sheet.py OUT.png"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

import mcstyle as M
import mcexport as X

BLENDER = "E:/Steam/steamapps/common/Blender/blender.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
LEADS = {'guild_master': 'adventurer_s_36848002', 'archmage': 'adventurer_ss_36619001', 'forgemaster': 'townsfolk_56403004'}
PER, W, H, GAP = 17, 1800, 300, 1.2


def name(id_):
    s = M.spec(LEADS.get(id_, id_))
    return s.get("name", id_).split(" ")[0]


def rows():
    ids = list(json.load(open(X.PREVIEW / "scales.json")))
    groups = [("Leads", ["wagoner"] + sorted(i for i in ids if i in LEADS or (M.HAND / (i + ".json")).exists())),
              ("Adventurers", [i for i in ids if i.startswith("adventurer") and i not in LEADS.values()]),
              ("Townsfolk", [i for i in ids if i.startswith("townsfolk") and i not in LEADS.values()]),
              ("Elves", [i for i in ids if i.startswith("elf")]),
              ("Dwarves", [i for i in ids if i.startswith("dwarf")]),
              ("Demons", [i for i in ids if i.startswith("demon")])]
    out = []
    for title, g in groups:
        g = sorted(g, key=lambda i: (M.spec(LEADS.get(i, i)).get("age", "adult") != "kid", i)) if title != "Leads" else g
        per = PER if len(g) > PER else len(g)
        for k in range(0, len(g), PER):
            out.append({"title": title + (" (cont.)" if k else ""), "ids": g[k:k + per]})
    return out


if __name__ == "__main__":
    OUT = sys.argv[1]
    tmp = str(X.PREVIEW / "rows")
    os.makedirs(tmp, exist_ok=True)
    R = rows()
    json.dump(R, open(os.path.join(tmp, "rows.json"), "w"))
    subprocess.run([BLENDER, "-b", "-P", os.path.join(HERE, "blender", "mc_ef_grid.py"), "--", os.path.join(tmp, "rows.json"), tmp],
                   check=True, stdout=subprocess.DEVNULL)
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 13)
    big = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 18)
    sheet = Image.new("RGB", (W, (H + 22) * len(R)), (24, 26, 30))
    d = ImageDraw.Draw(sheet)
    for n, r in enumerate(R):
        y = n * (H + 22)
        sheet.paste(Image.open(os.path.join(tmp, "row_%02d.png" % n)).convert("RGB"), (0, y))
        d.text((10, y + 6), r["title"], font=big, fill=(240, 230, 210))
        for i, id_ in enumerate(r["ids"]):
            x = (i - (len(r["ids"]) - 1) / 2) * GAP
            sx = W / 2 - x * W / (PER * GAP + 1)
            t = name(id_)
            d.text((sx - d.textlength(t, font=font) / 2, y + H + 3), t, font=font, fill=(220, 220, 220))
    sheet.save(OUT)
    print("sheet", OUT, sheet.size)
