"""The statues of the Hall of Heroes: the ten past heroes on their plinths down the nave, the first of them in the niche
over the dais, and the two colossi in the great niches either side of the hall's front.

Each is a sculpted statue (tools/blender/hero_statues.py -> tools/sculpt.py): one block, ashbound:NAME[facing,piece],
with a block model for every cell it fills, made the way the Moonwell Priestess was. Here they're stood centred on
the plinth or niche round the marks hall_of_heroes() left, facing across the nave (or down it, or out of the front).

    blender -b -P tools/blender/hero_statues.py     then     python tools/sculpt.py
"""

S = None                      # set by capital.py (its Build)
SCULPT = None                 # capital_city.sculpt, set with S


def sculpt_info():
    import capital_city as CY
    return CY.SCULPT

# mark -> (figure, height); the figure's cells face +z (south) as voxelized
HEROES = {
    "hero:0": ("hero_shield", 12), "hero:1": ("hero_hammer", 12), "hero:2": ("hero_bow", 12),
    "hero:3": ("hero_blackmage", 12), "hero:4": ("hero_priestess", 12), "hero:5": ("hero_rogue", 12),
    "hero:6": ("hero_spear", 12), "hero:7": ("hero_summoner", 12), "hero:8": ("hero_paladin", 12),
    "hero:9": ("hero_axe", 12), "hero:first": ("hero_first", 14),
    "hero_colossus:w": ("colossus_knight", 22), "hero_colossus:e": ("colossus_mage", 22),
}
TURN = {"south": 0, "west": 1, "north": 2, "east": 3}          # quarter turns clockwise seen from above, from south
ROT = {"north": "east", "east": "south", "south": "west", "west": "north"}


def turned(st, q):
    """A block state turned q quarter turns clockwise (stairs, logs and the like)."""
    if q % 4 == 0 or "[" not in st:
        return st
    name, props = st[:-1].split("[", 1)
    out = []
    for kv in props.split(","):
        k, v = kv.split("=")
        if k == "facing" and v in ROT:
            for _ in range(q % 4):
                v = ROT[v]
        elif k == "axis" and v in ("x", "z") and q % 2:
            v = "z" if v == "x" else "x"
        out.append("%s=%s" % (k, v))
    return "%s[%s]" % (name, ",".join(out))


def facing(mark, x):
    if mark.startswith("hero:") and mark != "hero:first":
        return "east" if x < 0 else "west"             # down the nave's sides, each looking across it
    return "south"                                      # the first hero down the hall, the colossi out of the front


def stand(mark, at):
    """One statue on its mark, centred on what it stands on: the nave's plinths are two cells wide out from the mark
    (away from the nave), the first hero's niche and the colossi's are centred on theirs."""
    name, _ = HEROES[mark]
    if name not in sculpt_info():
        print("  no statue %s yet (%s): left empty" % (name, mark))
        return 0
    w, h, d = sculpt_info()[name]["size"]
    face = facing(mark, at[0])
    W, D = (d, w) if face in ("east", "west") else (w, d)
    x, y, z = at
    if mark.startswith("hero:") and mark != "hero:first":
        cxc = min(x, x - 1 if face == "east" else x + 1) + 1.0      # the plinth's middle, its two cells x and x - s
        czc = z + 0.5
    elif mark == "hero:first":
        cxc, czc = x + 0.5, z                                       # into its niche behind the mark
    else:
        cxc, czc = x + 0.5, z + 0.0                                 # the colossi's niches run z - 2 .. z + 1
    SCULPT(name, round(cxc - W / 2), round(czc - D / 2), face, y)
    return sum(1 for _ in sculpt_info()[name]["pieces"])


def build():
    placed = 0
    for mark in HEROES:
        at = S.marks.get(mark)
        if at:
            placed += stand(mark, at)
    print("  heroes' statues: %d pieces" % placed)
