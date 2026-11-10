"""Pass 13: every fight, every party. A second-by-second fight simulator on top of tools/balance.py's numbers (weapons,
armour, the rank's typical build, the solved monsters): every rank x every kind of fight x every kind of party (solo
each class, tank or none, healer or none, skills or none, 1 to 8 players) -> how long the kill takes, how close the
party comes to dying, who dies. Then checks each against the targets (TARGETS below) and lists what's out.

    python tools/balance_sim.py             the summary: every rank's fights, the usual parties, flags
    python tools/balance_sim.py --all       every party, every fight
    python tools/balance_sim.py --bosses    every boss in the game one by one (gate, arena, overworld, legend) vs its rank

Assumptions (the model's knobs; the in-game Meter is the real check, change these to what play shows):
- a monster in reach swings every MOB_SWING s; LAND of those land on a melee player (dodging, blocking, stepping out),
  less on ranged classes (balance.CLASS_SAFE); a boss or elite adds a big attack (BIG_HIT x) every BIG_EVERY s
- with a tank (Vanguard), THREAT of the blows go to the tank; without one they spread over the party
- everyone gets SUSTAIN: lifesteal, food and potions as a share of health a second, plus a drink (POTION of health,
  every POTION_CD s when under half)
- a Mender heals HEAL(rank) to everyone in the circle (CIRCLE_REACH of the party) every MEND_EVERY s; with skills, the
  Accord (a third of everyone's health) every ACCORD_CD s
- skills add balance.skill_share(rank) to everyone's damage in long fights; without skills they don't
"""
import json
import math
import statistics as st
import sys
from itertools import combinations_with_replacement

import balance as B
B.CLASS_SAFE.setdefault("vanguard", 2.0)   # a Vanguard blocks: about half the blows that would land end on the shield

MOB_SWING, LAND, BIG_EVERY = 1.6, 0.5, 8.0
THREAT = 0.75
SUSTAIN, POTION, POTION_CD = 0.004, 0.3, 30.0
MEND_EVERY, CIRCLE_REACH, ACCORD_CD, ACCORD = 3.6, 0.75, 60.0, 0.33
DT = 0.25
JAVA_SCALE = {"F": 0.8, "E": 1.12, "D": 1.568, "C": 2.195, "B": 3.073, "A": 4.302, "S": 6.023}   # Gear.scale
MEND_CLIMB = 0.66   # Gear.HEAL_CLIMB (pass 15; the staff heal's own climb, was Gear.MEND_CLIMB 0.44)
HEAL_BASE = 4.0      # Spells.HEAL_BASE (pass 13; was 9)

ROLE = {"vanguard": "tank", "breaker": "melee", "reaver": "melee", "lancer": "melee", "shade": "melee", "hunter": "ranged",
        "ashcaster": "ranged", "mender": "healer", "caller": "ranged"}
DPS_CLASSES = ("reaver", "breaker", "lancer", "shade", "hunter", "ashcaster", "caller")

# what a fight should come to (time in s for the whole party; margin = how long the party could have lasted / the kill)
# solo: from balance.CURVE. Parties: the kill takes PARTY_PACE of solo's time per extra player share, never trivial.
TARGETS = {
    "pack": {"margin": 2.5},          # four normals: never a threat to a ready party, a little to someone alone
    "elite": {"margin": 1.6},
    "boss": {"margin": 1.15},         # a gate boss: a fight that punishes mistakes
    "arena": {"margin": 1.1},
    "world": {"margin": 1.05},        # the overworld summons come a rank above you: the hardest thing you can choose
    "legend": {"margin": 1.4},
}


def heal_amount(r):
    """Spells.healing: 9 x power x Gear.mends, with power the staff's ladder"""
    x = JAVA_SCALE[r]
    return HEAL_BASE * x * (x / 0.8) ** (MEND_CLIMB - 1)


def base_hit(r):
    ws = B.weapons()[(r, "sword")]
    off, _ = B.build(r)
    hit = st.median(w["damage"] for w in ws) * off
    return hit, B.hits_per_s("sword", st.median(w["speed"] for w in ws))


import tree_build  # noqa: E402
_TREE = {}


def tree_edge(cls, r):
    """this class's own tree next to the median class's: (offence x, defence x) on top of balance.build"""
    k = (cls, r)
    if k not in _TREE:
        pts = B.MID_LEVEL[r] - 1
        walks = [tree_build.walk(c, pts) for c in tree_build.CLASS_AREAS]
        mo, md = st.median(w[0] for w in walks), st.median(w[1] for w in walks)
        o, d = tree_build.walk(cls, pts)
        off, dfn = B.build(r)
        _TREE[k] = ((off + (o - mo) / 100) / off, (dfn + (d - md) / 100) / dfn)
    return _TREE[k]


class Fighter:
    def __init__(self, cls, r, skills):
        self.cls, self.role = cls, ROLE[cls]
        _, dfn = B.build(r)
        dfn *= tree_edge(cls, r)[1]
        self.max = B.player_hp(r) * dfn
        self.hp = self.max
        self.armour = B.set_armour(B.CLASS_WEARS[cls], r)
        self.safe = B.CLASS_SAFE.get(cls, 1.0)
        self.potion_at = -1e9
        self.dead = False
        self.skills = skills

    def dps_share(self, party_size):
        solo, party = B.CLASS_DPS[self.cls]
        return solo if party_size == 1 else party


def encounter(kind, r, n):
    """the monsters of a fight: list of (hp, dmg, armour, big) after the party scaling Balance.party does"""
    mobs = B.monsters()
    def med(role):
        g = [m for m in mobs if m[0] == r and m[1] == role]
        return (st.median(m[3]["hp"] * m[4] for m in g), st.median(m[3]["dmg"] for m in g), st.median(m[3]["armor"] for m in g))
    gate = kind in ("pack", "elite", "boss", "arena", "world")   # Balance.party: gates, arenas and summoned bosses scale like a gate
    hp_p = B.PARTY["hp_per_player" if gate else "road_hp_per_player"] * (n - 1)
    dm_p = (B.PARTY["boss_dmg_per_player"] if kind in ("boss", "arena", "world", "legend") else B.PARTY["gate_dmg_per_player"] if gate else 0) * (n - 1)
    if n == 1 and kind in ("boss", "arena", "world"):
        dm_p = B.PARTY.get("solo_boss_dmg", 0)   # Balance.party: alone, a gate/arena/summoned boss hits softer
    out = []
    if kind == "pack":
        hp, dmg, arm = med("normal")
        out = [(hp, dmg, arm, False)] * 4
    elif kind == "elite":
        hp, dmg, arm = med("elite")
        nh, nd, na = med("normal")
        out = [(hp, dmg, arm, True), (nh, nd, na, False), (nh, nd, na, False)]
    else:
        hp, dmg, arm = BOSS_OF[kind](r)
        out = [(hp, dmg, arm, True)]
    extra = ARENA_PARTY * (n - 1) if kind == "arena" else 0
    return [(h * (1 + hp_p) * (1 + extra), d * (1 + dm_p), a, big) for h, d, a, big in out]


# the bosses that aren't a gate's: their own numbers through balance.json
GATE = {m["id"]: m for m in B.load("ashbound/gate_mobs.json")}
B.ARMOUR_TABLE.clear()
if (B.RES / "ashbound/beasts.json").exists():
    GATE.update({k: dict(v, id=k) for k, v in B.load("ashbound/beasts.json").items()})
_MOBS = B.monsters()
B.monsters = lambda raw=False: _MOBS
BAL = B.load("ashbound/balance.json")["mobs"]
ARENA = {"ossric": "C", "wreck_mother": "B", "ash_shepherd": "B", "nebula_moth": "S", "constellation_knight": "S", "orrery_magus": "S", "founder_king": "S"}
WORLD = ("cairn_giant", "hart_lord", "saltglass_hydra", "ironback_scorpion", "rime_lich")
LEGENDS = ("old_blackbriar", "red_plough", "rime_penitent", "sunbreaker", "grandmother_mire", "hollow_smile", "old_harpoon", "walking_mountain")
ARENA_PARTY = 0.0   # BossArenas.summon had +50% a player on top of Balance.party; gone in pass 13
RANK_STEP = {}      # a role's hp / dmg ratio rank to rank, from the solved gate bosses (for moving a boss to another rank, Balance.atRank)


def own(k):
    m = GATE.get(k) or B.JAVA_MOBS.get(k)
    if isinstance(m, tuple):
        m = {"hp": m[0], "dmg": m[1], "armor": m[2]}
    h, d, *_ = BAL.get(k, (1, 1))
    return m["hp"] * h, m["dmg"] * d, m["armor"]


def gate_boss(r):
    g = [m for m in B.monsters() if m[0] == r and m[1] == "boss"]
    return st.median(m[3]["hp"] for m in g), st.median(m[3]["dmg"] for m in g), st.median(m[3]["armor"] for m in g)


def moved(k, to):
    """a boss solved at its own rank, made a boss of another (Balance.atRank: as that rank's plain monster to its own)"""
    hp, dmg, arm = own(k)
    fr, role = BAL[k][3], BAL[k][2]
    rr = B.load("ashbound/balance.json").get("rank_role")
    a, b = (rr[fr][role], rr[to][role]) if rr else (B.load("ashbound/balance.json")["rank_normal"][fr], B.load("ashbound/balance.json")["rank_normal"][to])
    return hp * b[0] / a[0], dmg * b[1] / a[1], arm * (b[2] / a[2] if len(a) > 2 and a[2] else b[1] / a[1])   # Balance.atRank: armour as the role's there


def arena_boss(r):
    ks = [k for k, rr in ARENA.items() if rr == r and (k in GATE or k in B.JAVA_MOBS)]
    if not ks:
        return gate_boss(r)
    v = [own(k) for k in ks]
    return tuple(st.median(x[i] for x in v) for i in range(3))


def world_boss(r):
    """summoned at the party's rank (WorldBosses.call)"""
    v = [moved(k, r) for k in WORLD if k in BAL]
    return tuple(st.median(x[i] for x in v) for i in range(3))


def legend(r):
    v = [moved(k, r) for k in LEGENDS if k in BAL]
    return tuple(st.median(x[i] for x in v) for i in range(3))


BOSS_OF = {"boss": gate_boss, "arena": arena_boss, "world": world_boss, "legend": legend}


def kill_time(kind, r, comp, skills=True):
    """seconds for this party to kill this fight (monsters one at a time), from the party's damage alone"""
    n = len(comp)
    foes = encounter(kind, r, n)
    hit, rate = base_hit(r)
    more = 1 + (B.skill_share(r) if skills and kind != "pack" else 0)
    up = B.UPTIME["normal" if kind == "pack" else "elite" if kind == "elite" else "boss"]
    share = sum((B.CLASS_DPS["mender"][1] if c == "mender" and n > 1 else B.CLASS_DPS[c][0 if n == 1 else 1]) * tree_edge(c, r)[0] for c in comp)
    t = 0.0
    for hp, dmg, arm, big in foes:
        t += hp / (rate * share * up * B.armour_cut(hit * more, arm))
    return t, foes


def forgiveness(kind, r, comp, skills=True):
    """(kill seconds, landed blows a minute the party can take for the whole fight with nobody dying, who gives out first).
    A blow is the fight's average landed blow (BIG_SHARE of them a big attack on fights with one); the blows go where
    target_weights sends them; each member's budget is their health, SUSTAIN, potions and what a Mender gives back."""
    t, foes = kill_time(kind, r, comp, skills)
    n = len(comp)
    party = [Fighter(c, r, skills) for c in comp]
    # the average raw blow: monsters weighted by how long each is up (one at a time, the rest crowding in)
    raw, big = 0.0, any(f[3] for f in foes)
    for i, (hp, dmg, arm, b) in enumerate(foes):
        raw += dmg * (1 + (BIG_SHARE * (B.BIG_HIT - 1) if b else 0))
    raw /= len(foes)
    crowd = B.CROWD[r] if len(foes) > 1 else 1.0
    raw *= (1 + crowd * (len(foes) - 1)) / len(foes) if len(foes) > 1 else 1
    healers = sum(1 for c in comp if ROLE[c] == "healer")
    heal = heal_amount(r)
    worst, who = 1e9, None
    for p, w in target_weights(party):
        budget = p.max * (1 + SUSTAIN * t + POTION * (1 + t // POTION_CD))
        if healers and n > 1:
            budget += heal * (t / (MEND_EVERY / healers)) * CIRCLE_REACH
            if skills:
                budget += p.max * ACCORD * (t // ACCORD_CD)
        elif healers:          # a Mender alone heals themself
            budget += heal * (t / MEND_EVERY)
        blow = B.kept(raw, *p.armour) / p.safe
        allowed = budget / blow / w        # landed blows on the whole party before this one falls
        if allowed < worst:
            worst, who = allowed, p.cls
    return t, worst / (t / 60), who


BIG_SHARE = 0.25


def target_weights(alive):
    """who takes the blows: the tank most of them, the rest spread (ranged less often)"""
    tanks = [p for p in alive if p.role == "tank"]
    others = [p for p in alive if p.role != "tank"]
    out = []
    if tanks and others:
        for p in tanks:
            out.append((p, THREAT / len(tanks)))
        for p in others:
            out.append((p, (1 - THREAT) / len(others)))
    else:
        for p in alive:
            out.append((p, 1 / len(alive)))
    return out


PARTIES = {
    "solo reaver": ("reaver",), "solo vanguard": ("vanguard",), "solo mender": ("mender",), "solo hunter": ("hunter",),
    "solo ashcaster": ("ashcaster",), "solo caller": ("caller",), "solo breaker": ("breaker",), "solo shade": ("shade",), "solo lancer": ("lancer",),
    "2 dps": ("reaver", "ashcaster"), "tank+dps": ("vanguard", "reaver"), "heal+dps": ("mender", "reaver"),
    "3 dps": ("reaver", "hunter", "ashcaster"), "tank+heal+dps": ("vanguard", "mender", "reaver"), "tank+2dps": ("vanguard", "reaver", "hunter"),
    "heal+2dps": ("mender", "reaver", "ashcaster"),
    "4 classic": ("vanguard", "mender", "reaver", "ashcaster"), "4 dps": ("reaver", "shade", "hunter", "ashcaster"),
    "tank+3dps": ("vanguard", "reaver", "hunter", "ashcaster"), "heal+3dps": ("mender", "reaver", "hunter", "ashcaster"),
    "2 tank 2 heal": ("vanguard", "vanguard", "mender", "mender"),
    "5 classic": ("vanguard", "mender", "reaver", "ashcaster", "caller"), "5 dps": ("reaver", "shade", "lancer", "hunter", "ashcaster"),
    "6 classic": ("vanguard", "mender", "reaver", "ashcaster", "caller", "hunter"), "6 dps": DPS_CLASSES[:6],
    "8 classic": ("vanguard", "vanguard", "mender", "mender", "reaver", "shade", "ashcaster", "hunter"), "8 dps": DPS_CLASSES + ("reaver",),
}
SUMMARY = ("solo reaver", "solo mender", "tank+dps", "heal+dps", "tank+heal+dps", "4 classic", "4 dps", "heal+3dps", "6 classic", "8 classic", "8 dps")
KINDS = ("pack", "elite", "boss", "arena", "world", "legend")


# landed blows a minute a party must be able to take (forgiveness) and still win: a fight that punishes mistakes
# without asking for perfect play. Lower = harder.
FORGIVE = {"pack": 12, "elite": 7, "boss": 3.0, "arena": 3.0, "world": 2.5, "legend": 4.0}
FORGIVE_HEALED = 1.6     # with a Mender in the party it should be this much more forgiving
PACE = (0.3, 0.8)        # a party's kill time next to the same fight solo, by share of the party: never trivial, never slower


def run(parties, skills_both=True):
    flags = []
    for r in B.RANKS:
        print(f"\n== {r}   player {B.player_hp(r) * B.build(r)[1]:.0f} hp, heal {heal_amount(r):.1f}, skills +{B.skill_share(r) * 100:.0f}%   "
              "cells: kill seconds / landed blows a minute the party can take")
        print(f"  {'party':16}" + "".join(f"{k:>13}" for k in KINDS))
        solo = {k: kill_time(k, r, ("reaver",))[0] for k in KINDS}
        for name in parties:
            comp = PARTIES[name]
            for sk in ((True, False) if skills_both else (True,)):
                row = f"  {name + ('' if sk else ' -sk'):16}"
                for kind in KINDS:
                    t, f, who = forgiveness(kind, r, comp, sk)
                    row += f"{t:6.0f}/{f:5.1f}{'!' if f < FORGIVE[kind] else ' '}"
                    if f < FORGIVE[kind]:
                        flags.append((r, name + ("" if sk else " -sk"), kind, t, f, who))
                print(row)
        print("  solo times vs CURVE: boss %.0f s (target %d)" % (solo["boss"], B.CURVE[r]["boss_solo_s"]))
    print("\nFLAGS - less forgiving than FORGIVE (hits a minute the party can take):")
    for f in flags:
        print(f"  {f[0]} {f[1]:18} {f[2]:7} {f[3]:5.0f}s  {f[4]:4.1f}/min (needs {FORGIVE[f[2]]})  first down: {f[5]}")
    return flags


def bosses():
    print("every boss vs its rank's gate-boss median (hp, damage), solo time at its own rank")
    rows = []
    for k, (h, d, role, r) in sorted(BAL.items(), key=lambda kv: (B.RANKS.index(kv[1][3]), kv[0])):
        if role != "boss" or (k not in GATE and k not in B.JAVA_MOBS):
            continue
        hp, dmg, arm = own(k)
        gh, gd, ga = gate_boss(r)
        where = "arena" if k in ARENA else "world" if k in WORLD else "legend" if k in LEGENDS else "gate"
        rows.append((r, k, where, hp / gh, dmg / gd))
        print(f"  {r} {k:22} {where:7} hp {hp:7.0f} ({hp / gh:4.2f}x)  dmg {dmg:6.1f} ({dmg / gd:4.2f}x)  armour {arm:.0f}")
    return rows


if __name__ == "__main__":
    if "--bosses" in sys.argv:
        bosses()
    elif "--all" in sys.argv:
        run(list(PARTIES))
    else:
        run(SUMMARY, skills_both=False)
