"""What the skill tree really gives a player of each class at each rank (pass 13b): walk the tree from its start along its
links, every point to the best node in reach (its worth to that class, per point), keystones once their area has
key_need points, then add the stats up as % offence and % defence. balance.py's build() used a flat guess a point.

    python tools/tree_build.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import balance as B  # noqa: E402

T = B.load("ashbound/skill_tree.json")
NODES = {n["id"]: n for n in T["nodes"]}
NEXT = {}
for a, b in T["links"]:
    NEXT.setdefault(a, set()).add(b)
    NEXT.setdefault(b, set()).add(a)
OFF = {"dmg%": 1, "speed%": 1, "strikes": 4, "impact": 2, "reach": 6, "velocity%": 0.4}
SCHOOL = {"arrow%": 1, "spell%": 1, "thrall_dmg%": 1, "heal%": 1}   # counted as offence for the class whose school it is
DEF = {"health%": 1, "armour%": 0.5, "negation%": 0.4, "stun_armour": 1, "stamina": 2, "guard%": 0.5, "move%": 0.6, "knockback": 1,
       "stamina_regen%": 0.3, "mana": 0.25, "mana_regen%": 1, "thrall_hp%": 0.5}
# the areas a class's weapons use (a Vanguard holds sword and shield); points past them buy nothing that counts
CLASS_AREAS = {"vanguard": ("shield", "sword"), "breaker": ("hammer",), "reaver": ("twohander",), "lancer": ("spear",),
               "shade": ("dagger",), "hunter": ("bow",), "ashcaster": ("black",), "mender": ("white",), "caller": ("summon",)}
CLASS_SCHOOL = {"hunter": "arrow%", "ashcaster": "spell%", "mender": "heal%", "caller": "thrall_dmg%"}
MECH = 2.0   # a notable that unlocks a move and isn't in MECHANIC: about this much survival
# the notables that are a mechanic, not a number: their expected worth in a boss fight, % offence / % defence (valued by
# hand from their text: how often it's up x what it gives; for a Mender 'offence' is healing)
MECHANIC = {
    "Emergency Escape": (0, 4), "Twin Leap": (0, 1), "Pillager": (0, 1), "Adaptive Skin": (0, 6), "Second Wind": (0, 6),
    "Riposte": (8, 2), "Disarm": (2, 3), "Flowing Steel": (7, 0), "Cleaving Arc": (3, 0), "Duelist": (10, 0), "Flourish": (0, 1),
    "Technician": (0, 3), "Backstab": (15, 0), "Shadow Lunge": (3, 2), "Venom Edge": (4, 0), "Execute": (12, 0), "Catharsis": (6, 0), "Vanish": (0, 4),
    "Meteor Slam": (3, 0), "Concussion": (4, 4), "Aftershock": (2, 0), "Shatter": (12, 0), "Momentum": (15, 0),
    "Revelation": (6, 0), "Pin": (2, 4), "Vault": (1, 1), "Whirl": (3, 0), "Charge": (6, 0),
    "Berserker": (8, 0), "Endurance": (0, 4), "Rage": (8, 0), "Forbidden Strength": (2, 0), "Sunder": (13, 0), "Last Stand": (0, 6),
    "Parrying": (0, 8), "Impact Guard": (0, 5), "Shield Bash": (6, 2), "Taunt": (0, 0), "Guardian": (0, 5), "Thorns of Iron": (4, 0), "Retaliate": (8, 0),
    "Hunter's Mark": (15, 0), "Volley": (6, 0), "Piercing Shot": (3, 0), "Steady Aim": (12, 0), "Fire Arrow": (4, 0), "Skirmisher": (5, 0), "Point Blank": (6, 0),
    "Overload": (5, 0), "Lingering Curse": (3, 0), "Static": (2, 0), "Mana Shield": (0, 8), "Siphon": (2, 0), "Spellweaver": (6, 0), "Arcane Surge": (6, 0),
    "Mending Aura": (15, 0), "Blessing": (4, 0), "Aegis": (0, 6), "Purify": (0, 2), "Smite": (5, 0), "Sanctuary": (10, 0), "Radiance": (8, 0),
    "Pack Tactics": (12, 0), "Death Pact": (0, 3), "Soul Harvest": (0, 2), "Long Service": (6, 0), "Frenzy": (12, 0), "Bone Armour": (0, 6),
}
# a keystone's worth to its class, net of its drawback, % offence / % defence (their text, valued by hand)
KEYSTONE = {"Blade Dance": (14, 0), "Shadow Step": (22, -14), "Earthshaker": (8, 0), "Impaler": (8, 0), "Titan's Grip": (20, 0),
            "Unbreakable": (0, 10), "Deadeye": (30, 0), "Glass Cannon": (40, -22), "Martyr": (40, 0), "Legion": (5, 0)}


def worth(n, cls):
    sch = CLASS_SCHOOL.get(cls)
    o = sum(OFF.get(k, 0) * v for k, v in n["stats"].items()) + (n["stats"].get(sch, 0) if sch else 0)
    if cls == "mender":
        o += 0  # a Mender's 'offence' is its heal
    d = sum(DEF.get(k, 0) * v for k, v in {**n["stats"], **n.get("always", {})}.items())
    if n["kind"] == "notable" and n["name"] in MECHANIC:
        mo, md = MECHANIC[n["name"]]
        o += mo
        d += md
    elif n["kind"] == "notable" and n.get("ef") and not n["stats"]:
        d += MECH
    if n["kind"] == "keystone" and n["name"] in KEYSTONE:
        o, d = KEYSTONE[n["name"]]
    return o, d


def walk(cls, points):
    own = CLASS_AREAS[cls]
    taken = {T["start"]: 1}
    spent = {}
    off = dfn = 0.0
    for _ in range(points):
        best, bv = None, -1e9
        frontier = set()
        for k in taken:
            frontier |= NEXT.get(k, set())
            if taken[k] < NODES[k].get("max", 1):
                frontier.add(k)
        for k in frontier:
            n = NODES[k]
            if taken.get(k, 0) >= n.get("max", 1):
                continue
            if n["kind"] == "keystone" and spent.get(n["area"], 0) < T["key_need"]:
                continue
            if n["area"] not in own + ("core",):
                continue
            o, d = worth(n, cls)
            v = o + 0.8 * d + (3 if n["area"] in own else 0)
            if v > bv:
                best, bv = k, v
        if best is None:
            break
        taken[best] = taken.get(best, 0) + 1
        spent[NODES[best]["area"]] = spent.get(NODES[best]["area"], 0) + 1
        o, d = worth(NODES[best], cls)
        off += o
        dfn += d
    return off, dfn


if __name__ == "__main__":
    print("the tree's real worth at each rank's middle level, %% offence / %% defence (balance.build guessed %.2f / %.2f a point)" % B.TREE_PER_POINT)
    print(f"  {'class':10}" + "".join(f"{r:>12}" for r in B.RANKS))
    for cls in CLASS_AREAS:
        print(f"  {cls:10}" + "".join(f"{'%3.0f/%-3.0f' % walk(cls, B.MID_LEVEL[r] - 1):>12}" for r in B.RANKS))
    print(f"  {'guess':10}" + "".join(f"{'%3.0f/%-3.0f' % ((B.MID_LEVEL[r] - 1) * B.TREE_PER_POINT[0], (B.MID_LEVEL[r] - 1) * B.TREE_PER_POINT[1]):>12}" for r in B.RANKS))
