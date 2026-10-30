"""Who lives in Highmourn, and where they stand: the city's marks (S.marks, set as each place is built) turned into
townsfolk, and strollers down the busy streets. Written to data/ashbound/capital/cast.json as
[kind, shop, mode, x, y, z] in the city's frame; Capital.java stands each one in as its chunk is made.

kind: an NPC id (data/ashbound/npc/) or "@tag/tag" for one of the forge's townsfolk carrying those tags.
shop: the wares they sell (data/ashbound/shop/), "" for none. mode: "stand" (keeps their spot), "stroll" (wanders a
little way round it), "errand" (about their whole quarter), "sit" (on the seat they're put on, x y z being the seat's
block; a 7th field is the way they face). Between times they chat, sit, play (NpcLife.java).

    python tools/capital_cast.py     recast from the city as last built (tools/renders/cast_in.pkl), no full rebuild
"""
import json
import math
import os
import pickle
import random


HORN = (-208, 18, -126, 62)     # capital_city.HORNSEND
OUT = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources", "data", "ashbound", "capital", "cast.json")
KEPT = os.path.join(os.path.dirname(__file__), "renders", "cast_in.pkl")

# the hand-made townsfolk and the leads, by the mark they stand at
LEADS = {
    "guild_master": ("guild_master", ""),
    "guild_barkeep": ("townsfolk_3000", "innkeeper"),
    "quartermaster": ("quartermaster", "quartermaster"),
    "armourer": ("smith", "smith"),
    "archer": ("hunter", ""),
    "innkeeper": ("innkeeper", "innkeeper"),
    "priest": ("priestess", ""),
    "founder": ("forgemaster", "forgemaster"),
    "archmage": ("archmage", ""),
    "hearth_well": ("fence", "fence"),
    "horn_fence": ("@demon/fence", "fence"),
    "trainer": ("adventurer_c_5008", ""),
}
# everyone else by the kind of mark: who, the shop, how they keep their spot
ROLES = {
    "guild_clerk": ("@townsfolk/scholar", "", "stand"),
    "horn_cook": ("@demon/cook", "innkeeper", "stand"),
    "horn_tinker": ("@demon/smith", "trade_smith", "stand"),
    "horn_elder": ("@demon/elder", "", "stroll"),
    "adventurers": ("@adventurer", "", "stroll"),
    "sparring": ("@adventurer/striker", "", "stand"),
    "smith": ("@townsfolk/smith", "trade_smith", "stand"),
    "foundry_hand": ("@townsfolk/smith", "", "stroll"),
    "cooper": ("@townsfolk/merchant", "trade_general", "stand"),
    "fishmonger": ("@townsfolk/merchant", "trade_fishmonger", "stand"),
    "fisher": ("@townsfolk/farmer", "", "stand"),
    "bathkeeper": ("@townsfolk/barmaid", "", "stand"),
    "shrine_keeper": ("@townsfolk/acolyte", "", "stand"),
    "acolyte": ("@townsfolk/acolyte", "", "stroll"),
    "mason": ("@townsfolk/smith", "", "stand"),
    "mason_hand": ("@townsfolk/farmer", "", "stroll"),
    "tanner": ("@townsfolk/hunter", "", "stand"),
    "dyer": ("@townsfolk/merchant", "trade_tailor", "stand"),
    "gate_guard": ("@townsfolk/guard", "", "stand"),
    "keep_guard": ("@townsfolk/guard", "", "stand"),
    "keep_captain": ("@townsfolk/guard", "", "stand"),
    "hall_warden": ("@townsfolk/guard", "", "stand"),
    "hall_keeper": ("@townsfolk/elder", "", "stand"),
    "lord": ("@townsfolk/elder", "", "stand"),
    "steward": ("@townsfolk/scholar", "", "stand"),
    "novice_master": ("@townsfolk/scholar", "", "stand"),
    "arcanum_lecturer": ("@townsfolk/scholar", "", "stand"),
    "arcanum_librarian": ("@townsfolk/scholar", "trade_books", "stand"),
    "arcanum_alchemist": ("@townsfolk/herbalist", "alchemist", "stand"),
    "arcanum_herbalist": ("@townsfolk/herbalist", "", "stroll"),
    "arcanum_porter": ("@townsfolk/guard", "", "stand"),
    "mage_trainer": ("@adventurer/b", "", "stand"),
}
MAGE = {"black": "@adventurer/black_mage/b", "white": "@adventurer/white_mage/b", "summon": "@adventurer/black_mage/b"}
SKIP = ("hero", "hero_colossus", "warden", "guild_belfry", "gate_board", "bounty_board", "champion", "arcanum_start",
        "arcanum_tower_ground")
# who walks the streets, by the kind of street, and how far apart
STREET = {"market": 7, "square": 7, "main": 11, "hearth": 10, "walk": 14, "green": 13, "lane": 17, "alley": 26}
CROWD = (("@townsfolk/adult", 6), ("@townsfolk/elder", 2), ("@townsfolk/child", 2), ("@adventurer", 2), ("@townsfolk/guard", 1))
# how many walk the streets together (stopping to chat), and how many of those out alone are crossing town
GROUPS = ((1, 5), (2, 4), (3, 1))
ERRAND = 0.35
# who's sat on which seats, and how many of them are taken
SEATS = {
    "guild_chair": (0.7, (("@adventurer", 6), ("@townsfolk/adult", 1))),
    "bar_stool": (0.6, (("@adventurer", 3), ("@townsfolk/adult", 3))),
    "bench": (0.4, (("@townsfolk/adult", 4), ("@townsfolk/elder", 3), ("@townsfolk/child", 1), ("@adventurer", 1))),
    "towel_bench": (0.4, (("@townsfolk/adult", 3), ("@townsfolk/elder", 1))),
    "school_chair": (0.75, (("@scholar", 3), ("@white_mage", 2), ("@black_mage", 2), ("@acolyte", 2), ("@townsfolk/teen", 2))),
}
YAW = {"south": 0, "west": 90, "north": 180, "east": 270}
# customers browsing at each market stall
BROWSERS = (("@townsfolk/adult", 5), ("@townsfolk/elder", 2), ("@townsfolk/child", 1), ("@adventurer", 1))


def passable(st):
    return st is None or st == "air" or any(w in st for w in ("carpet", "light[", "short_grass", "fern", "pressure_plate"))


def footing(st):
    return st is not None and st != "air" and not passable(st) and "water" not in st and "lava" not in st \
        and "fence" not in st and "_wall[" not in st and "pane" not in st and "bars" not in st


def spot(B, x, y, z, taken, reach=3):
    """The free floor nearest x, y, z: footing under it, room for a body over it, nobody there yet."""
    for r in range(reach + 1):
        ring = [(x + a, z + b) for a in range(-r, r + 1) for b in range(-r, r + 1) if max(abs(a), abs(b)) == r]
        ring.sort(key=lambda c: (c[0] - x) ** 2 + (c[1] - z) ** 2)
        for cx, cz in ring:
            for dy in (0, 1, -1):
                yy = y + dy
                if (cx, yy, cz) in taken:
                    continue
                if footing(B.get((cx, yy - 1, cz))) and passable(B.get((cx, yy, cz))) and passable(B.get((cx, yy + 1, cz))):
                    return cx, yy, cz
    return None


def pick(rnd, table):
    t = rnd.uniform(0, sum(w for _, w in table))
    for v, w in table:
        t -= w
        if t <= 0:
            return v
    return table[-1][0]


def cast(S, roads, ground):
    B, rnd = S.B, random.Random(1312)
    out, taken, missed = [], set(), []

    def add(kind, shop, mode, x, y, z, reach=3):
        p = spot(B, x, y, z, taken, reach)
        if p is None:
            return False
        taken.add(p)
        out.append([kind, shop, mode, p[0], p[1], p[2]])
        return True
    for key, (x, y, z) in sorted(S.marks.items()):
        role = key.split(":")[0]
        if role in SKIP:
            continue
        if role in LEADS and not any(e[0] == LEADS[role][0] for e in out):
            kind, shop = LEADS[role]
            mode = "stand"
        elif role == "shopkeeper":
            trade = key.split(":")[1]
            kind, shop, mode = "@townsfolk/merchant", "trade_" + trade, "stand"
            if trade == "apothecary":
                shop = "alchemist"
                if not any(e[0] == "alchemist" for e in out):
                    kind = "alchemist"
        elif role == "guild_clerk" and not any(e[0] == "receptionist" for e in out):
            kind, shop, mode = "receptionist", "", "stand"        # Elowen at the first desk
        elif role in ROLES:
            kind, shop, mode = ROLES[role]
            if role == "mage_trainer":
                kind = MAGE.get(key.split(":")[1], kind)
        else:
            missed.append(key)
            continue
        if not add(kind, shop, mode, x, y, z):
            missed.append(key)
            continue
        if role == "hearth_well":                       # children round the well, under Rook's eye
            for k in range(3):
                add("@townsfolk/child", "", "stroll", x + 3 - k * 3, y, z + 3)
    # people sat about: at the guild's tables, the bars, the benches round the squares and greens
    sat = 0
    for (x, y, z), st in sorted(B.items()):
        if not st or not st.startswith("ashbound:"):
            continue
        name = st[9:].split("[")[0]
        if name not in SEATS or ("piece=" in st and "piece=0" not in st):
            continue
        share, who = SEATS[name]
        over = B.get((x, y + 1, z))
        if rnd.random() > share or (x, y, z) in taken or not (passable(over) or over.startswith("ashbound:" + name)):
            continue
        face = st.split("facing=")[1].split(",")[0].split("]")[0] if "facing=" in st else "north"
        taken.add((x, y, z))
        out.append([pick(rnd, who), "", "sit", x, y, z, YAW.get(face, 0)])
        sat += 1
    # customers at the stalls, a step or two out in front of the shopkeeper
    for e in list(out):
        if e[2] == "stand" and e[1].startswith("trade_"):
            for _ in range(rnd.choice((0, 1, 1, 2))):
                add(pick(rnd, BROWSERS), "", "stroll", e[3] + rnd.randint(-2, 2), e[4], e[5] + rnd.randint(-2, 2), reach=3)
    streets = 0
    for r in roads:
        every = STREET.get(r.kind)
        if not every:
            continue
        run, nxt = 0.0, rnd.uniform(0, every)
        for i in range(1, len(r.samples)):
            run += math.dist(r.samples[i - 1][:2], r.samples[i][:2])
            if run < nxt:
                continue
            nxt += every * rnd.uniform(0.7, 1.3)
            qx, qz, hw = r.samples[i][:3]
            ox = rnd.uniform(-hw, hw) * 0.6
            x, z = round(qx + ox), round(qz + rnd.uniform(-hw, hw) * 0.6)
            n = pick(rnd, GROUPS)
            mode = "errand" if n == 1 and rnd.random() < ERRAND else "stroll"
            for k in range(n):                          # a group stands close, so they fall to talking
                if add(pick(rnd, CROWD), "", mode, x + k * 2 - (n - 1), ground(x, z) + 1, z + rnd.randint(-1, 1), reach=2):
                    streets += 1
    # Hornsend's streets are Hornsend's folk; the watch still walks through
    horn = 0
    for c in out:
        if HORN[0] <= c[3] <= HORN[2] and HORN[1] <= c[5] <= HORN[3] and not c[0].startswith("@demon") and "guard" not in c[0]:
            c[0] = "@demon/child" if "child" in c[0] else "@demon/elder" if "elder" in c[0] else rnd.choice(("@demon/sweeper", "@demon/sweeper", "@demon/adult"))
            horn += 1
    print("cast: %d in Hornsend" % horn)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), separators=(",", ":"))
    print("cast: %d townsfolk (%d out on the streets, %d sat down); no spot for %s"
          % (len(out), streets, sat, ", ".join(missed) or "none"))
    return out


class Road:
    def __init__(self, kind, samples):
        self.kind, self.samples = kind, samples


class Kept:
    def __init__(self, B, marks):
        self.B, self.marks = B, marks


def keep(S, roads, H):
    """What the cast is made from, so it can be made again without building the whole city."""
    os.makedirs(os.path.dirname(KEPT), exist_ok=True)
    with open(KEPT, "wb") as f:
        pickle.dump((dict(S.B), dict(S.marks), [(r.kind, r.samples) for r in roads], dict(H)), f)


if __name__ == "__main__":
    with open(KEPT, "rb") as f:
        B, marks, roads, H = pickle.load(f)
    cast(Kept(B, marks), [Road(k, s) for k, s in roads], lambda x, z: H.get((x, z), 0))
