"""The Joined weapons, the Cold Forge's own: one of each kind, made only by laying two boss weapons in its hands, and
grown by feeding it more. Hand-built in tools/joined_shapes.py.

    python tools/joinedgear.py [--no-icons]   -> ashbound/joined.json, meshes, textures, item models, capabilities, lang
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import weaponforge as W  # noqa: E402
from weaponforge import Theme, bx, ring_xy  # noqa: E402
from voxsword import ramp  # noqa: E402
import gui3d  # noqa: E402
import joined_shapes  # noqa: E402

GAME = W.GAME
RES = os.path.join(GAME, "src/main/resources")
GEAR = json.load(open(os.path.join(RES, "ashbound/gear.json"), encoding="utf-8"))

ITEMS = [("oathbinder", "Oathbinder", "sword"), ("twinfang", "Twinfang", "dagger"), ("concord", "Concord", "hammer"),
         ("unison", "Unison", "spear"), ("two_hearted", "Two-Hearted", "twohander"), ("the_closed_hand", "The Closed Hand", "shield"),
         ("twinstring", "Twinstring", "bow"), ("black_accord", "Black Accord", "black"), ("white_accord", "White Accord", "white"),
         ("bound_accord", "Bound Accord", "summon")]
LADDER = 1.4   # a rank (Joined.mult takes it from there)
RANKS = "DCBAS"


class Joined(Theme):
    def __init__(self):
        super().__init__("joined",
                         blade=ramp("#20222a", "#343844", "#4c5260", "#6c7482", "#909aa8", "#b8c0ca", "#dce2e6", "#f6f4ec"),
                         dark=ramp("#0c0c10", "#16161c", "#22222a", "#32323c", "#46464f", "#5c5a62"),
                         wrap=ramp("#1a1208", "#2a1e10", "#402e18", "#584224", "#725a34"),
                         wood=ramp("#16161c", "#22222a", "#32323c", "#46464f", "#5c5a62", "#747078"),
                         glow=ramp("#5a1c04", "#a03a08", "#e06a12", "#ff9a2a", "#ffc65a", "#ffe6a0", "#fff8e0"),
                         acc=ramp("#4a2e08", "#7a4c10", "#a87018", "#d0961f", "#ecbc34", "#ffdc6a"))

    def emblem(self, s, cx, y, size, z, boss):
        # two rings locked through each other, one gold, one burning
        r = size * 0.42
        ring_xy(s, cx - r * 0.55, y, r, size * 0.15, "acc", 12, depth=z + 0.2)
        ring_xy(s, cx + r * 0.55, y, r, size * 0.15, "glow", 12, glow=True, depth=z + 0.2)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # the seam the two were joined along, and a gold band at each end of it
        if where == "blade":
            bx(s, 0, y0 + (y1 - y0) * 0.06, 0, max(0.5, half * 0.22), (y1 - y0) * 0.86, thick + 0.1, "glow", glow=True, tag="seam")
        for k in (0.04, 0.94):
            bx(s, 0, y0 + (y1 - y0) * k, 0, half * 2 + 0.4, 0.7, thick + 0.25, "acc", tag="band")


def base(kind):
    """What the kind's weapon hits for at rank F, from the first boss weapon of it, a rank above its dungeon's, and its speed."""
    for d in GEAR:
        for w in d["weapons"]:
            if w["boss"] and w["kind"] == kind and w.get("damage"):
                return round(w["damage"] / LADDER ** ("FEDCBAS".index(d["rank"]) + 1), 1), w["speed"], w
    for d in GEAR:
        for w in d["weapons"]:
            if w["boss"] and w["kind"] == kind:
                return 0, 0, w
    raise KeyError(kind)


def main():
    joined_shapes.install()
    th = Joined()
    W.THEMES["joined"] = th
    table, icons = [], []
    lang_p = os.path.join(RES, "assets/ashbound/lang/en_us.json")
    lang = json.load(open(lang_p, encoding="utf-8"))
    for iid, name, kind in ITEMS:
        dmg, speed, like = base(kind)
        it = dict(like, id=iid, name=name, kind=kind, rank="S", boss=True, old=False, damage=dmg, speed=speed)
        W.make(th, it, icons)
        cap = os.path.join(RES, "data/ashbound/capabilities/weapons/%s.json" % like["id"])
        if os.path.exists(cap):
            json.dump(json.load(open(cap, encoding="utf-8")), open(os.path.join(RES, "data/ashbound/capabilities/weapons/%s.json" % iid), "w", encoding="utf-8"), indent=1)
        table.append({"id": iid, "name": name, "kind": kind, "damage": dmg, "speed": speed})
        lang["item.ashbound." + iid] = name
    json.dump(table, open(os.path.join(RES, "ashbound/joined.json"), "w", encoding="utf-8"), indent=1)
    json.dump(lang, open(lang_p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    if "--no-icons" not in sys.argv:
        W.render_icons(icons)
    for iid, _, kind in ITEMS:
        path = os.path.join(gui3d.A, "models/item/%s.json" % iid)
        m = json.load(open(path, encoding="utf-8"))
        if m.get("loader") != "neoforge:separate_transforms":
            continue
        r = gui3d.pose(iid, kind)
        sc, t = gui3d.fit(iid, r)
        rot = gui3d.euler_xyz(r)
        disp = m["base"].setdefault("display", {})
        disp["gui"] = {"rotation": rot, "translation": t, "scale": [round(sc, 4)] * 3}
        disp["fixed"] = dict(disp["gui"])
        disp["ground"] = {"rotation": rot, "translation": [round(v * 0.55, 3) for v in t[:2]] + [0], "scale": [round(sc * 0.55, 4)] * 3}
        for k in ("gui", "fixed", "ground"):
            m.get("perspectives", {}).pop(k, None)
        m.setdefault("perspectives", {})
        m["gui_light"] = "side"
        json.dump(m, open(path, "w", encoding="utf-8"), indent=1)
    W.sheet("joined", [i[0] for i in ITEMS])
    print("joined:", [(t["id"], t["damage"]) for t in table])


if __name__ == "__main__":
    main()
