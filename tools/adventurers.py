"""Adventurer parties for the wilds and the towns (docs/ADVENTURERS.md): each a few of the NPC forge's adventurers of one
rank, a party name and a colour they all wear, some with an elf, a dwarf or a demon among them, a few all of one race.

    python tools/adventurers.py            roll the parties: tools/npc_specs/adv_*.json + tools/adv_parties.json
    python tools/adventurers.py --sheet    then: their cube meshes (mcexport preview) and a lineup sheet, a row a party

They're background life: they spawn round players, fight, camp and talk, and go when you've gone (Adventurers.java)."""
import json
import os
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, "E:/Ashbound/tools")
sys.path.insert(0, str(HERE))
import npcgen  # noqa: E402  the forge's own roller (only read, never changed)

SPECS = HERE / "npc_specs"
PARTIES = HERE / "adv_parties.json"
RECIPE = json.load(open("E:/Ashbound/tools/npc/recipes/adventurer.json"))
RACES = {r: json.load(open(HERE / "npc_recipes" / (r + ".json"))) for r in ("elf", "dwarf", "demon")}
# an adult role of each race to borrow a body from (ears, beard, horns, skin, names), never their job
BODY_ROLE = {"elf": "warden", "dwarf": "guard", "demon": "fence"}

# who's in a party, by how it fights: always a front, mostly a healer
MAKEUPS = [["tank", "white_mage", "striker", "ranger"], ["tank", "striker", "rogue", "black_mage"],
           ["breaker", "lancer", "ranger", "white_mage"], ["tank", "striker", "striker", "white_mage", "black_mage"],
           ["ranger", "rogue", "black_mage"], ["tank", "breaker", "white_mage"], ["lancer", "striker", "ranger", "white_mage"],
           ["tank", "ranger", "black_mage", "white_mage"]]

# name, rank, the colour they wear, race mix (None = mostly human, one other now and then)
PARTY_LIST = [
    ("The Mudlarks", "F", "mustard", None), ("Lantern Hounds", "F", "rust", None), ("The Greenhorns", "F", "moss", None),
    ("Copper Bell Company", "E", "ochre", None), ("The Thornbacks", "E", "forest", "elf"), ("Low Road Five", "E", "brown", None),
    ("Ninth Lantern", "D", "navy", None), ("The Stonejaws", "D", "rust", "dwarf"), ("Gallows Crows", "D", "charcoal", None),
    ("The Red Hounds", "C", "red", None), ("Ember Wake", "C", "oxblood", "demon"),
    ("Silver Thistle", "B", "teal", None), ("The Ashen Vow", "B", "plum", None),
    ("Ironwake", "A", "black", "dwarf"), ("The Last Lanterns", "A", "wine", None),
    ("Crownless", "S", "white", None)]


def body(race, seed):
    """A body of that race from its own recipe, as folkforge.roll_race makes them: its hair, its names, the dwarf beard."""
    import folkforge
    r = dict(RACES[race])
    r.setdefault("hair_style", folkforge.HAIR[race])
    for k in range(20):
        s = npcgen.roll(r, 0, seed * 31 + k, role_name=BODY_ROLE[race])
        if s["age"] == "adult":
            break
    rng = random.Random(s["seed"])
    s["name"] = rng.choice(r["names"][s["sex"]]) + " " + rng.choice(r["names"]["surname"])
    if race == "dwarf":
        s["beard"] = None                       # built whole by the race's own cubes
    return s


def member(party, rank, role, colour, race, seed):
    s = npcgen.roll(RECIPE, 0, seed, rank=rank, role_name=role)
    if race:
        b = body(race, seed)
        for k in ("sex", "build", "skin", "hair", "beard", "name"):
            s[k] = b[k]
        s["race"] = race
        s["face"] = dict(s["face"], iris=b["face"]["iris"], brows=b["face"]["brows"], nose_box=race == "dwarf" or s["face"]["nose_box"])
        s["recipe_race"] = race
    s["outfit"]["colors"]["accent"] = colour
    s["party"] = party
    return s


def roll(seed=4113):
    rng = random.Random(seed)
    out, n, used = [], 0, set()
    for name, rank, colour, mix in PARTY_LIST:
        makeup = rng.choice(MAKEUPS)
        ids = []
        # a mostly human party has one of another race now and then; a race's own party is mostly that race
        odd = rng.randrange(len(makeup)) if not mix and rng.random() < 0.55 else -1
        other = rng.choice(("elf", "dwarf", "demon"))
        for i, role in enumerate(makeup):
            race = mix if mix and (i < 3 or rng.random() < 0.5) else other if i == odd else None
            n += 1
            for k in range(40):                 # nobody shares a first name with another adventurer
                s = member(name, rank, role, colour, race, seed * 1000 + n + 7919 * k)
                if s["name"].split(" ")[0] not in used:
                    break
            used.add(s["name"].split(" ")[0])
            s["id"] = "adv_%s_%02d" % (rank.lower(), n)
            json.dump(s, open(SPECS / (s["id"] + ".json"), "w"), indent=1)
            ids.append(s["id"])
        out.append({"name": name, "rank": rank, "colour": colour, "members": ids})
    json.dump(out, open(PARTIES, "w"), indent=1)
    print(len(out), "parties,", n, "adventurers")
    return out


def sheet(parties, png):
    import mcexport as X
    import mcstyle as M
    ids = [i for p in parties for i in p["members"]]
    # their preview meshes, their scales kept apart from the cast's (mc_cast_sheet reads that one)
    scales = {i: X.export(i, M.folk(i)) for i in ids}
    json.dump(scales, open(X.PREVIEW / "adv_scales.json", "w"), indent=1)
    from PIL import Image, ImageDraw, ImageFont
    tmp = X.PREVIEW / "adv_rows"
    os.makedirs(tmp, exist_ok=True)
    rows = [{"title": "%s  (%s)" % (p["name"], p["rank"]), "ids": p["members"]} for p in parties]
    json.dump(rows, open(tmp / "rows.json", "w"))
    subprocess.run(["E:/Steam/steamapps/common/Blender/blender.exe", "-b", "-P", str(HERE / "blender" / "mc_ef_grid.py"), "--",
                    str(tmp / "rows.json"), str(tmp)], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, MC_GRID_PER="8", MC_GRID_H="420"))
    W, H, PER, GAP = 1800, 420, 8, 1.2
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 13)
    big = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 18)
    img = Image.new("RGB", (W, (H + 36) * len(rows)), (24, 26, 30))
    d = ImageDraw.Draw(img)
    for n, r in enumerate(rows):
        y = n * (H + 36)
        img.paste(Image.open(tmp / ("row_%02d.png" % n)).convert("RGB"), (0, y))
        d.text((10, y + 6), r["title"], font=big, fill=(240, 230, 210))
        for i, id_ in enumerate(r["ids"]):
            s = M.spec(id_)
            x = (i - (len(r["ids"]) - 1) / 2) * GAP
            sx = W / 2 - x * W / (PER * GAP + 1)
            for k, t in enumerate((s["name"].split(" ")[0], s["title"].split(" ", 1)[1] + (" (" + s["recipe_race"] + ")" if s.get("recipe_race") else ""))):
                d.text((sx - d.textlength(t, font=font) / 2, y + H + 2 + 15 * k), t, font=font, fill=(220, 220, 220) if k == 0 else (150, 150, 150))
    img.save(png)
    print("sheet", png, img.size)


def export(parties):
    """Into the mod: each member's cube mesh and texture (bare: they wear real armour and hold real weapons in game), their
    sizes into npc_scales.json, and the parties (name, rank, colour, who and what they do) into /ashbound/adventurers.json."""
    import mcexport as X
    import mcstyle as M
    game = HERE.parent
    scales_at = game / "src/main/resources/assets/ashbound/npc_scales.json"
    scales = json.load(open(scales_at))
    out = []
    for p in parties:
        members = []
        for i in p["members"]:
            s = M.spec(i)
            scales[i] = X.export(i, M.Folk(bare(s)), install=True)
            members.append({"kind": i, "name": s["name"], "role": s["role"], "race": s.get("race") or "human", "sex": s["sex"]})
        out.append({"name": p["name"], "rank": p["rank"], "colour": p["colour"], "members": members})
    json.dump(scales, open(scales_at, "w"), indent=1)
    json.dump(out, open(game / "src/main/resources/ashbound/adventurers.json", "w"), indent=1)
    print("exported", len(out), "parties,", sum(len(p["members"]) for p in out), "meshes")


def bare(s):
    """Their spec without what they'd carry: the game puts real weapons in their hands."""
    s = dict(s, weapon=None, offhand=None, back=None, hip=None, prop=None, pose={"r": "hang", "l": "hang"})
    return s


if __name__ == "__main__":
    if "--export" in sys.argv:
        export(json.load(open(PARTIES)))
        sys.exit()
    parties = roll()
    if "--sheet" in sys.argv:
        sheet(parties, str(HERE / "renders" / "adventurers_v1.png"))
