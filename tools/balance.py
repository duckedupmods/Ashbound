"""Balance check (docs/BALANCE.md): reads the real data and prints, per gate rank, how the numbers land against
the targets. Pass 1: weapons vs monster health. Pass 2: monster damage vs armour.

    python tools/balance.py            # both passes
    python tools/balance.py --mobs     # every monster's numbers, by rank and role
    python tools/balance.py --html out.html

The formulas copy the game's (vanilla armour, Armors.java, Gear.java, Spells.java), so a change there needs one here.
"""
import json
import math
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "src/main/resources"
RANKS = "FEDCBAS"

# --- the game's numbers (keep in step with the Java) ----------------------------------------------------------
WEAPON_STEP, ARMOUR_STEP = 1.4, 1.5   # gear carries the climb (pass 11): a rank's weapon +40%, its armour +50%
SCALE = {r: round(0.8 * WEAPON_STEP ** i, 3) for i, r in enumerate(RANKS)}  # Gear.scale: weapon damage
ARMOUR_SCALE = {"F": 0.80, "E": 0.87, "D": 0.93, "C": 1.0, "B": 1.08, "A": 1.16, "S": 1.25}  # weight and toughness keep the gentle ladder
ARMOUR_K = 40.0   # Balance.kept: damage x K / (K + armour x (1 + toughness / 20)): every K armour is one more health bar
TOUGH_PER = 20.0
CLASS_ARMOUR = {"robe": 0.6, "light": 0.8, "medium": 1.0, "heavy": 1.4}   # a class's armour next to medium's
SHARE = (0.15, 0.40, 0.30, 0.15)
PLAYER_HP = 20.0  # at level 1
HP_PER_LEVEL = 0.4  # health grows with level (decided 10/29; the level system isn't built yet)
MID_LEVEL = {"F": 5, "E": 15, "D": 25, "C": 37, "B": 52, "A": 67, "S": 82}
# 10/31: 0.6 was too much for friends, 0.15 left a four-player dungeon far too easy. Gates 0.3; outside them it stays 0.15.
PARTY = {"hp_per_player": 0.3, "road_hp_per_player": 0.15, "boss_dmg_per_player": 0.08, "gate_dmg_per_player": 0.04, "solo_boss_dmg": -0.3, "radius": 32, "reward_share": 0.2}
# outside monsters get their rank from where they live (decided 10/29)
HAUNT_RANK = {"black_banner": "E", "deep_delvers": "E", "barrow_host": "D", "drowned_corsairs": "D", "sporefolk": "D",
              "salt_cursed": "C", "thornborn": "C", "rimebound": "C", "blightkin": "C", "broodmothers": "C",
              "sky_legion": "B", "hollow_order": "B", "ash_legion": "A", "voidborn": "S", "tidewrack": "D"}
# the world's beasts (tools/mobs/world_beasts.py) are solved at C and moved to the rank they spawn at (Balance.atRank):
# a beast fights like an elite of its rank, a legend like a boss
BEAST_RANK = "C"
LEGEND_HP, LEGEND_DMG = 0.4, 0.75
# pass 13: the bosses that aren't a gate's, on their rank's boss target times their own weight (health x, damage x).
# The story's arena bosses are each act's climax, a little above a gate boss; the Founder-King is the hardest thing in the
# game. The five overworld summons are solved at B and moved to the summoner's party rank (WorldBosses, Balance.atRank):
# a big fight you choose, about twice a gate boss. Their party scaling is a gate's (Balance.party), not the road's.
BOSS_BAND, TOWER_BOSS_BAND, BOSS_DMG_BAND = (0.85, 1.2), (1.15, 1.35), (0.85, 1.15)
ELITE_BAND, ELITE_DMG_BAND = (0.75, 1.3), (0.8, 1.25)
STORY_BOSSES = {"wreck_mother": ("B", 1.3, 1.1), "ash_shepherd": ("B", 1.3, 1.1), "nebula_moth": ("S", 1.3, 1.1),
                "constellation_knight": ("S", 1.3, 1.15), "orrery_magus": ("S", 1.3, 1.1), "founder_king": ("S", 1.6, 1.2)}
WORLD_BOSSES = {k: ("B", 1.8, 1.15) for k in ("cairn_giant", "hart_lord", "saltglass_hydra", "ironback_scorpion", "rime_lich")}
# the ashfall night's own (Ashfall.java): given their role's multipliers at the beasts' rank, moved to the party's rank
# when they come (Balance.atRank); kept out of the medians so they don't shift anyone else
ASHFALL = {"ashwalker": "normal", "ash_herald": "normal", "cinder_hulk": "elite"}   # a Legend vs a gate boss of its rank: ~75 s solo instead of ~190, a big hit takes ~5 to kill, not 3.5
BEASTS = {"thornmaw": "elite", "gorehorn": "elite", "sun_basilisk": "elite", "bogmaw": "elite",
          "vexclaw": "elite", "tidetusk": "elite", "cragmaul": "elite",
          "old_blackbriar": "boss", "red_plough": "boss", "rime_penitent": "boss", "sunbreaker": "boss",
          "grandmother_mire": "boss", "hollow_smile": "boss", "old_harpoon": "boss", "walking_mountain": "boss"}
SPELL = {"black": (20.0, 16, 20), "white": (9.0, 38, 60), "summon": (0, 60, 300)}  # damage/heal, mana, cooldown ticks
MANA, MANA_REGEN, MANA_IDLE = 100.0, 0.06, 0.14  # max, share of max a second while casting, and 1.5 s after the last cast
BOLT_LANDS = 0.8  # a bolt is a slow projectile: how many of them hit something that moves
BOW_ARROW = 6.0 * 2.6  # full-draw vanilla arrow (2 x speed 3) x Gear.power (pass 13: 2.6, was 2.3); one shot ~1.1 s
THRALL_DMG = 4.8  # (pass 13b, was 4.3) a summoned thrall's hit at rank C (Spells.summon), four at most
# Epic Fight's real swing timing (tools/ef_timing.py -> ef_timing.json): a kind's combo, hits a second at its speed
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ef_timing  # noqa: E402
TIMING = json.loads((Path(__file__).resolve().parent / "ef_timing.json").read_text(encoding="utf-8"))
COMBO = {"sword": "sword", "dagger": "dagger", "hammer": "greatsword", "spear": "spear", "twohander": "greatsword"}
TITAN_DMG = 0.75      # Titan's Grip: each hit of the pair -25%
TITAN_STAMINA = 0.5   # extra stamina every swing with it
# stamina (Epic Fight: 15 at most, a roll 4, a step 3, x (weight / 40) of armour; Passives.swingCost, regen 1.25)
SWING = {"sword": 0.6, "dagger": 0.4, "spear": 0.7, "hammer": 1.6, "twohander": 1.6}
BOW_COST = 1.2
STAMINA, ROLL, STAMINA_REGEN = 15.0, 4.0, 1.25
WEIGHT = {"robe": 1.5, "light": 4, "medium": 8, "heavy": 14}  # a full set at rank C (efarmor.py EF), x ARMOUR_SCALE
# what a rank's typical player has from the tree and curios: stamina, regen on top
BUILD_BREATH = {"F": (0, 0), "E": (0.5, 0.03), "D": (1, 0.06), "C": (2, 0.1), "B": (3, 0.14), "A": (4, 0.17), "S": (5, 0.2)}
# how a kind's damage a second should sit against the sword's (slower, riskier or wider weapons a little more)
KIND_DPS = {"sword": (0.95, 1.05), "dagger": (0.85, 1.05), "spear": (0.85, 1.0), "hammer": (0.82, 1.0), "twohander": (0.92, 1.08)}
# (hammers and two-handers hit up to 3 enemies a swing, hammers stagger hardest: a little less on one target)


def hits_per_s(combo, speed):
    """hits a second spamming a combo (Epic Fight plays each swing at its basis speed / your attack speed)"""
    return ef_timing.combo_rate(TIMING[combo], speed)[0]


BIG_HIT = 1.8  # the hardest MobSkills multiplier (atk * 1.8f)

# monsters whose numbers live in Java, not gate_mobs.json: hp, damage, armour
JAVA_MOBS = {"cinderhusk": (40, 6, 4), "bound_scholar": (55, 8, 4), "lector": (70, 9, 6), "inkbound": (95, 11, 10),
             "weaver": (80, 10, 4), "silk_mite": (10, 3, 0), "silk_queen": (600, 18, 12)}  # Cinderhusk.java, SilkMobs.java

# Targets (research pass 10/29, docs/BALANCE.md "By the book"): seconds are REAL fight time, with the share of it you
# actually hit (UPTIME: dodging, moving, waiting out a boss's openings); hits survived lean to the hard end.
# 10/31: not one flat target any more. The first ranks are a little easy, the late ones are the epic fights.
# pass 14 (11/7, user): easy start, the hardest stretch mid game (B), then the power comes back - at A and S the road's
# monsters fall fast and you can take a few more blows, while the bosses (gate, story, world, legend) stay long, epic fights.
# pass 15: hits_big from B up set by tools/balance_mc.py so two ok damage players beat a gate boss ~80% (was 25% at S)
CURVE = {"F": {"normal_hits": 3, "elite_s": 9, "boss_solo_s": 110, "hits_normal": 14, "hits_elite": 9, "hits_big": 5.5},
         "E": {"normal_hits": 3, "elite_s": 10, "boss_solo_s": 130, "hits_normal": 12.5, "hits_elite": 8, "hits_big": 4.5},
         "D": {"normal_hits": 3.5, "elite_s": 12, "boss_solo_s": 160, "hits_normal": 10.5, "hits_elite": 7, "hits_big": 4},
         "C": {"normal_hits": 4, "elite_s": 14, "boss_solo_s": 190, "hits_normal": 9, "hits_elite": 6, "hits_big": 3.5},
         "B": {"normal_hits": 4.5, "elite_s": 16, "boss_solo_s": 230, "hits_normal": 7.5, "hits_elite": 5, "hits_big": 4},
         "A": {"normal_hits": 4, "elite_s": 15, "boss_solo_s": 250, "hits_normal": 8, "hits_elite": 5, "hits_big": 4.1},
         "S": {"normal_hits": 3, "elite_s": 12, "boss_solo_s": 270, "hits_normal": 9, "hits_elite": 5.5, "hits_big": 4.4}}
SOLVE = CURVE["C"]
# A blow from a second monster within a second of the last one does this much (Balance.crowded): a crowd can't melt you
# early on. From S a crowd is a crowd.
CROWD = {"F": 0.4, "E": 0.45, "D": 0.55, "C": 0.65, "B": 0.75, "A": 0.85, "S": 1.0}


def goal(rank, key):
    """the band around a rank's target"""
    v = CURVE[rank][key]
    return v * 0.8, v * 1.2


def class_hits(rank, cls):
    """normal hits a class survives at a rank: its armour's share of medium's health bars, medium's being CURVE's"""
    a, t = MEDIUM[rank]
    x = kept(1, a * CLASS_ARMOUR[cls], TOUGH[cls] * ARMOUR_SCALE[rank] if cls != "medium" else t)
    v = CURVE[rank]["hits_normal"] * kept(1, a, t) / x
    return v * 0.85, v * 1.15


UPTIME = {"normal": 1.0, "elite": 0.7, "boss": 0.6}

# The expected build of a player at a rank's middle level: monsters are solved against a typical player of the rank, not
# a naked one. Tree: level - 1 points; small nodes are ~0.45% offence and defence a point, notables and keystones add
# mechanics (Execute, Sunder...) on top. Curios: a kit of the rank's usual rarity, partly filled early. Weapon affixes:
# a world weapon's rolls (pass 5) as they come to hand.
TREE_PER_POINT = (0.65, 0.45)   # % offence, % defence a tree point
KIT = {"F": ("uncommon", 0.25), "E": ("uncommon", 0.6), "D": ("rare", 0.6), "C": ("rare", 0.85), "B": ("epic", 0.85),
       "A": ("epic", 1.0), "S": ("legendary", 1.0)}   # rarity, share of the four curio slots worn
RELIC = {"F": 0, "E": 0, "D": 0.5, "C": 1, "B": 1, "A": 1, "S": 1}   # a relic worn (its stats; its power isn't counted)
AFFIX = {"F": 0, "E": 2, "D": 4, "C": 6, "B": 8, "A": 10, "S": 12}   # % damage from a rolled weapon
CURIO_OFF = {"dmg%", "speed%", "arrow%", "spell%", "thrall_dmg%", "mana_regen%", "elite_dmg%"}
CURIO_DEF = {"health%", "armour%", "tough%", "heal%", "kb%", "thrall_hp%", "stamina_regen%", "dodge_cost%"}
_BUILD = {}


def build(rank):
    """(offence, defence) multipliers of the rank's typical player"""
    if rank in _BUILD:
        return _BUILD[rank]
    cs = load("ashbound/curios.json")
    def split(sel):
        o = st.mean(sum(curio_worth({k: v}) for k, v in c["stats"].items() if k in CURIO_OFF) for c in sel)
        d = st.mean(sum(curio_worth({k: v}) for k, v in c["stats"].items() if k in CURIO_DEF) for c in sel)
        return o, d
    rar, share = KIT[rank]
    ko, kd = split([c for c in cs if c["rarity"] == rar and c["slot"] != "relic"])
    ro, rd = split([c for c in cs if c["slot"] == "relic"])
    pts = MID_LEVEL[rank] - 1
    # pass 13b: the tree as players really spend it (tools/tree_build.py walks it per class), the median class; was pts x TREE_PER_POINT
    import tree_build
    walks = [tree_build.walk(c, pts) for c in tree_build.CLASS_AREAS]
    to, td = st.median(w[0] for w in walks), st.median(w[1] for w in walks)
    off = 1 + (to + 4 * share * ko + RELIC[rank] * ro + AFFIX[rank]) / 100
    dfn = 1 + (td + 4 * share * kd + RELIC[rank] * rd) / 100
    _BUILD[rank] = (off, dfn)
    return off, dfn


def load(p):
    return json.loads((RES / p).read_text(encoding="utf-8"))


def armour_cut(dmg, armour, tough=0.0):
    """vanilla CombatRules.getDamageAfterAbsorb"""
    f = min(20.0, max(armour / 5.0, armour - dmg / (2.0 + tough / 4.0))) / 25.0
    return dmg * (1 - f)


def kept(dmg, armour, tough=0.0):
    """what's left of a blow on a player (Balance.kept)"""
    return dmg * ARMOUR_K / (ARMOUR_K + armour * (1 + tough / TOUGH_PER))


MEDIUM = {r: (round(20 * ARMOUR_STEP ** i), round(0.8 + 0.1 * i, 1)) for i, r in enumerate(RANKS)}  # the anchor class: armour, toughness per rank
TOUGH = {"robe": 0.0, "light": 0.0, "heavy": 3.0}  # toughness at C, scaled like the old ladder
ARMOUR_TABLE = {}  # filled from balance.json (or solve): class -> rank -> (armour, toughness)


def pieces(total):
    """a set's armour split over helm/chest/legs/boots as whole points, summing to the rounded total"""
    p = [max(1, math.floor(total * s + 0.5)) for s in SHARE]
    p[1] += max(1, math.floor(total + 0.5)) - sum(p)
    return p


def set_armour(cls, rank):
    if cls == "medium":
        a, t = MEDIUM[rank]
    else:
        a, t = ARMOUR_TABLE[cls][rank]
    return sum(pieces(a)), t


# --- monsters ---------------------------------------------------------------------------------------------------
BAL = RES / "ashbound/balance.json"


def monsters(raw=False):
    """every placed monster as (rank, role, where, numbers, hp multiplier); with balance.json applied unless raw"""
    mobs = {m["id"]: m for m in load("ashbound/gate_mobs.json")}
    for k, (hp, dmg, arm) in JAVA_MOBS.items():
        mobs[k] = {"id": k, "hp": hp, "dmg": dmg, "armor": arm}
    foreman = {}
    if not raw and BAL.exists():
        b = json.loads(BAL.read_text(encoding="utf-8"))
        for k, (h, d, *_) in b["mobs"].items():
            if k in mobs:
                mobs[k] = dict(mobs[k], hp=mobs[k]["hp"] * h, dmg=mobs[k]["dmg"] * d)
        foreman = b["foreman_hp"]
        ARMOUR_TABLE.update({c: {r: tuple(v) for r, v in t.items()} for c, t in b.get("armour", {}).items()})
    out = []  # (rank, role, where, mob, hp multiplier)
    for d in load("ashbound/gear.json"):
        tower = (RES / f"data/ashbound/tower/{d['gate']}.json").exists()
        where = ("tower " if tower else "") + d["gate"]
        if tower:
            t = load(f"data/ashbound/tower/{d['gate']}.json")
            for k in sorted({m[3] for m in t["mobs"]}):
                out.append((d["rank"], "normal", where, mobs[k], 1))
            for k in sorted({m[3] for m in t["foremen"]}):
                out.append((d["rank"], "elite", where + " (foreman)", mobs[k], foreman[d["gate"]] / mobs[k]["hp"] if d["gate"] in foreman else 2))
            out.append((d["rank"], "boss", where, mobs[t["boss"][3]], 1))
            continue
        for k in d["mobs"]:
            out.append((d["rank"], "normal", where, mobs[k], 1))
        out.append((d["rank"], "elite", where, mobs[d["elite"]], 1))
        out.append((d["rank"], "boss", where, mobs[d["boss"]], 1))
    h = load("ashbound/haunts.json")
    for f, v in h["factions"].items():
        for k in v["mobs"]:
            out.append((HAUNT_RANK.get(f, "?"), "normal", "haunt " + f, mobs[k], 1))
        out.append((HAUNT_RANK.get(f, "?"), "elite", "haunt " + f, mobs[v["elite"]], 1))
    # factions with a spawner of their own (Tidewrack.java), ranked like the haunts
    for f, (ks, el) in OWN_SPAWNERS.items():
        for k in ks:
            if k in mobs:
                out.append((HAUNT_RANK.get(f, "?"), "normal", "haunt " + f, mobs[k], 1))
        if el in mobs:
            out.append((HAUNT_RANK.get(f, "?"), "elite", "haunt " + f, mobs[el], 1))
    return out


OWN_SPAWNERS = {"tidewrack": (("lamprey_hound", "merrow", "reef_knight", "net_hag", "hullback"), "abyss_angler")}


# --- player damage ----------------------------------------------------------------------------------------------
def weapons():
    """per rank and kind: the median dungeon weapon (not boss drops)"""
    by = {}
    for d in load("ashbound/gear.json"):
        for w in d["weapons"]:
            if not w["boss"]:
                by.setdefault((d["rank"], w["kind"]), []).append(w)
    return by


KIND_EDGE = {"spear": 1.15, "hammer": 1.08}   # Passives.KIND_EDGE (pass 13b)


def dps(kind, ws, rank, summon_mob=None):
    """sustained damage per second (before the monster's armour) and one hit's damage"""
    x = SCALE[rank]
    if kind in ("sword", "dagger", "hammer", "spear", "twohander"):
        dmg = st.median(w["damage"] for w in ws)
        spd = st.median(w["speed"] for w in ws)
        dmg *= KIND_EDGE.get(kind, 1.0)
        return dmg * hits_per_s(COMBO[kind], spd), dmg
    if kind == "shield":
        return None, None
    if kind == "bow":
        hit = BOW_ARROW * x
        return hit / 1.1, hit
    if kind == "black":
        hit, cost, cd = SPELL["black"]
        hit *= x
        rate = cast_rate(cost, cd, 6, 4) / 0.6 * BOLT_LANDS  # casts landed a second while casting: the cooldown or the mana
        return rate * hit, hit
    if kind == "summon" and summon_mob:
        # up to four thralls (two a cast), each hitting about once a second
        hit = THRALL_DMG * x
        return 4 * hit, hit
    return None, None


def cast_rate(cost, cd, on, off, ticks=40000):
    """casts a second: casting for on seconds, then dodging for off, with the mana Spells.regen gives back"""
    m, casts, ready, last = MANA, 0, 0, -999
    for t in range(ticks):
        if t % ((on + off) * 20) < on * 20 and t >= ready and m >= cost:
            m -= cost
            casts += 1
            ready, last = t + cd, t
        m = min(MANA, m + MANA * (MANA_IDLE if t - last > 30 else MANA_REGEN) / 20)
    return casts / (ticks / 20)


def stamina_regen(s, cap, regen):
    """PlayerPatch.tick: a tick's stamina back, faster the fuller you are"""
    return cap * 0.01 * (1 + (s / (cap - 0.5 * s)) ** 2) * regen


def swing_duty(cost, rate, load, cap=STAMINA, regen=STAMINA_REGEN, resume=0.7, ticks=6000):
    """share of a fight spent swinging if stamina is all that stops you: swing until only a roll is left, roll, back off
    until the bar is resume full, go again. Regen waits 30 ticks after an action, less with regen above 1, and a
    swing's animation holds that wait."""
    roll, gate = ROLL * load, 30 - int(900 / int(30 * regen))
    s, wait, busy, on, hitting, next_swing = cap, 0, 0, 0, True, 0.0
    for t in range(ticks):
        if busy > 0:
            busy -= 1
        elif wait > 0:
            wait -= 1
        if hitting:
            if s > roll:
                if t >= next_swing:
                    s, wait, busy, next_swing = max(0, s - cost * load), 30, int(20 / rate), t + 20 / rate
                on += 1
            else:
                s, wait, busy, hitting = max(0, s - roll), 30, 14, False
        elif s >= cap * resume:
            hitting = True
        if s < cap and wait <= gate:
            s = min(cap, s + stamina_regen(s, cap, regen))
    return on / ticks


def print_breath():
    """PASS 7: stamina and mana. How long a bar lasts, and whether stamina or the UPTIME the monsters are solved for stops you."""
    print("PASS 7 - stamina and mana")
    print("  stamina: swings in a full bar, seconds of nonstop swinging, rolls in a bar")
    load = {c: 1 + WEIGHT[c] / 40 for c in WEIGHT}
    ws = weapons()
    for k, cost in SWING.items():
        rate = hits_per_s(COMBO[k], st.median(w["speed"] for w in ws[("C", k)]))
        print(f"    {k:10} {cost:.1f} a swing: {STAMINA / cost:3.0f} swings, {STAMINA / cost / rate:4.1f} s ({cost * rate:.2f} a second)")
    print("    rolls: " + "  ".join(f"{c} {STAMINA / (ROLL * x):.1f}" for c, x in load.items()) + f"   bow: {STAMINA / BOW_COST:.0f} shots")
    print(f"  share of a fight stamina lets you swing (monsters are solved for bosses {UPTIME['boss']:.0%}, elites {UPTIME['elite']:.0%}), and a sword's solo boss")
    print(f"  {'':4} {'light':>6} {'medium':>6} {'heavy':>6}   boss s (medium)")
    for r in RANKS:
        extra, more = BUILD_BREATH[r]
        rate = hits_per_s("sword", 1.6)
        row = [swing_duty(SWING["sword"], rate, 1 + WEIGHT[c] * ARMOUR_SCALE[r] / 40, STAMINA + extra, STAMINA_REGEN + more) for c in ("light", "medium", "heavy")]
        boss = CURVE[r]["boss_solo_s"] * UPTIME["boss"] / min(UPTIME["boss"], row[1])
        print(f"  {r:4} " + " ".join(f"{d:6.0%}" for d in row) + f"   {fmt(boss, *goal(r, 'boss_solo_s'))}")
    print("  mana: nonstop, and casting 6 s in 10")
    for kind, (hit, cost, cd) in SPELL.items():
        burst = MANA / max(0.01, cost * 20 / cd - MANA * MANA_REGEN)
        lasts = f"full bar {burst:.0f} s at full speed" if burst < 999 else "never short"
        print(f"    {kind:7} {cost} mana, {cd / 20:.0f} s cooldown: {lasts}, then {cast_rate(cost, cd, 10, 0):.2f} casts a second; "
              f"{cast_rate(cost, cd, 6, 4):.2f} with pauses")


def fmt(v, lo, hi, fmt_="{:.0f}"):
    s = fmt_.format(v)
    if v < lo:
        return s + "↓"
    if v > hi:
        return s + "↑"
    return s


def report():
    mobs = monsters()
    ws = weapons()
    gear = load("ashbound/gear.json")
    rows1, rows2 = [], []
    for r in RANKS:
        here = [m for m in mobs if m[0] == r]
        if not here:
            continue
        def hp_of(role):
            v = [m[3]["hp"] * m[4] for m in here if m[1] == role]
            return st.median(v) if v else 0
        def arm_of(role):
            v = [m[3]["armor"] for m in here if m[1] == role]
            return st.median(v) if v else 0
        def dmg_of(role):
            v = [m[3]["dmg"] for m in here if m[1] == role]
            return st.median(v) if v else 0
        nhp, ehp, bhp = hp_of("normal"), hp_of("elite"), hp_of("boss")
        narm, earm, barm = arm_of("normal"), arm_of("elite"), arm_of("boss")
        summon = next((m[3] for m in here if m[3]["id"] in {d["summon"] for d in gear if d["rank"] == r}), None)
        line = {"rank": r, "normal_hp": nhp, "elite_hp": ehp, "boss_hp": bhp, "kinds": {}}
        for kind in ("sword", "dagger", "spear", "hammer", "twohander", "bow", "black", "summon"):
            got = ws.get((r, kind), [])
            if not got and kind not in ("bow", "black", "summon"):
                continue
            d, hit = dps(kind, got, r, summon)
            if d is None:
                continue
            # the monster's armour on each hit (scaled to sustained dps by the same ratio)
            off = build(r)[0]
            d, hit = d * off, hit * off
            nh = armour_cut(hit, narm)
            hits = nhp / nh
            el = ehp / (d * armour_cut(hit, earm) / hit) / UPTIME["elite"] / (1 + skill_share(r))
            bo = bhp / (d * armour_cut(hit, barm) / hit) / UPTIME["boss"] / (1 + skill_share(r))
            line["kinds"][kind] = (d, hits, el, bo)
        rows1.append(line)

        ndmg, bdmg = dmg_of("normal"), dmg_of("boss") * BIG_HIT
        l2 = {"rank": r, "normal_dmg": ndmg, "boss_big": bdmg, "cls": {}}
        for cls in ("robe", "light", "medium", "heavy"):
            a, t = set_armour(cls, r)
            hp = player_hp(r) * build(r)[1]
            l2["cls"][cls] = (a, t, hp / kept(ndmg, a, t), hp / kept(bdmg, a, t))
        rows2.append(l2)
    return rows1, rows2, mobs


def player_hp(rank):
    return PLAYER_HP + HP_PER_LEVEL * (MID_LEVEL[rank] - 1)


def raw_for(hp, a, t, hits):
    """the raw hit that leaves `hits` hits to kill a player with hp through armour a / toughness t"""
    return hp / hits / kept(1, a, t)


# --- pass 3: levels, Ash, coins, materials ------------------------------------------------------------------------
BAND = {"F": (1, 10), "E": (10, 20), "D": (20, 30), "C": (30, 45), "B": (45, 60), "A": (60, 75), "S": (75, 90)}
CLEARS = {"F": 4, "E": 6, "D": 8, "C": 10, "B": 12, "A": 14, "S": 16}  # dungeon clears (or the same outside) per band
LEVEL_A, LEVEL_P, MAX_LEVEL = 80, 1.55, 100  # Ash from level L to L+1: A * L^P (the old tree's curve)
CLEAR_COINS = {"F": 250, "E": 300, "D": 350, "C": 450, "B": 550, "A": 650, "S": 800}  # a solo clear's coins
# GateLoot (mirror of the Java): each monster's common mats (chance, count), caster's elite-mat chance, elite, boss
MATS = {"common": (0.5, 1), "caster_elite": 0.05, "elite": (3, 1), "boss": (4, 7, 1, 2, 1)}  # boss: common lo-hi, elite lo-hi, trophy


def cost(level):
    return round(LEVEL_A * level ** LEVEL_P)


def lair_mobs(name):
    """the monsters a dungeon is stocked with (its .bin points), statues left out"""
    import gzip
    import struct
    f = RES / f"data/ashbound/lair/gate_{name}.bin"
    if not f.exists():
        return []
    b, i = gzip.open(f).read(), 4
    def u16():
        nonlocal i
        i += 2
        return struct.unpack(">H", b[i - 2:i])[0]
    def text():
        nonlocal i
        n = u16()
        i += n
        return b[i - n:i].decode()
    for _ in range(u16()):
        text()
    out = []
    for _ in range(u16()):
        k = text()
        i += 24
        if k.startswith("mob:") and not k.endswith("!"):
            out.append(k[4:k.rindex(":")].split(":")[-1].split("@")[0])
    return out


def clears(mult):
    """per rank: the median dungeon clear's monster health (after balance), mats, and how many monsters"""
    base = {m["id"]: m for m in load("ashbound/gate_mobs.json")}
    for k, (hp, dmg, arm) in JAVA_MOBS.items():
        base[k] = {"id": k, "hp": hp}
    hp = lambda k: base[k]["hp"] * mult.get(k, (1,))[0] if k in base else 0
    by = {}
    for d in load("ashbound/gear.json"):
        ms = lair_mobs(d["gate"])
        if not ms:
            continue
        total = sum(hp(k) for k in ms) + hp(d["boss"])
        casters = sum(1 for k in ms if k in d["casters"])
        elites = sum(1 for k in ms if k == d["elite"])
        c, e = MATS["common"], MATS["elite"]
        b = MATS["boss"]
        common = (len(ms) - elites) * c[0] * c[1] + elites * e[0] + (b[0] + b[1]) / 2
        elite_m = casters * MATS["caster_elite"] + elites * e[1] + (b[2] + b[3]) / 2
        by.setdefault(d["rank"], []).append((total, len(ms), common, elite_m, b[4]))
    return {r: tuple(st.median(x[i] for x in v) for i in range(5)) for r, v in by.items()}


def progress(mult):
    """Ash and coins per point of a monster's health, per rank, so each band takes CLEARS clears"""
    cl = clears(mult)
    ash, coins = {}, {}
    for r, (lo, hi) in BAND.items():
        need = sum(cost(L) for L in range(lo, hi))
        ash[r] = round(need / (CLEARS[r] * cl[r][0]), 3)
        coins[r] = round(CLEAR_COINS[r] / cl[r][0], 4)
    return {"levels": {"a": LEVEL_A, "p": LEVEL_P, "max": MAX_LEVEL}, "ash_per_hp": ash, "coins_per_hp": coins}


def print_progress():
    b = json.loads(BAL.read_text(encoding="utf-8"))
    mult = b["mobs"]
    cl = clears(mult)
    gear = load("ashbound/gear.json")
    print("PASS 3 - levels, Ash, coins and materials (one player's share of a clear of the rank's median dungeon: everyone rolls their own)")
    print(f"  level curve: {LEVEL_A} x L^{LEVEL_P}  (level 10 costs {cost(10)}, 50 {cost(50)}, 90 {cost(90)}); "
          f"health {PLAYER_HP:.0f} + {HP_PER_LEVEL}/level")
    print(f"  {'rank':4} {'levels':>7} {'clears':>6} {'monsters':>8} {'Ash/clear':>10} {'coins':>6} {'commons':>8} {'elite m':>8} {'clears/set':>10}")
    for r, (lo, hi) in BAND.items():
        tot, n, common, elite_m, trophy = cl[r]
        g = next(d for d in gear if d["rank"] == r and d["weapons"])   # what a set costs at this rank, not at F
        set_cost = [sum(p["cost"][k] for p in g["sets"][0]["pieces"]) for k in ("common", "elite", "trophy")]
        per_set = max(set_cost[0] / common, set_cost[1] / elite_m, set_cost[2] / trophy)
        print(f"  {r:4} {lo:>3}-{hi:<3} {CLEARS[r]:>6} {n:>8.0f} {tot * b['ash_per_hp'][r]:>10.0f} "
              f"{tot * b['coins_per_hp'][r]:>6.0f} {common:>8.1f} {elite_m:>8.1f} {per_set:>10.1f}")


# --- pass 5: affixes (WorldArms.AFFIXES / Tier, mirrored) -------------------------------------------------------------
AFFIXES = {  # name: (lo, hi, what one point of it is worth in "% more damage or survivability" at rank C)
    "Keen": (0.025, 0.045, lambda v, r: v * 100),                                  # +% damage
    "Swift": (0.02, 0.04, lambda v, r: v * 100),                                 # +% attack speed
    "Brutal": (0.35, 0.65, lambda v, r: v * SCALE[r] / SCALE["C"] / weapon_hit(r) * 100),  # flat damage x the rank's ladder
    "Hale": (0.025, 0.045, lambda v, r: v * 100),                                # +% of all your health
    "Warded": (0.03, 0.05, lambda v, r: armour_gain(v, r)),                      # +% armour
    "Arcane": (0.025, 0.045, lambda v, r: v * 100),                                # +% spell power
    "Flowing": (0.03, 0.05, lambda v, r: v * 100),                               # +% mana regen = +% sustained casting
    "Deep": (2, 4, lambda v, r: v),                                              # +mana on 100 (regen is a share of it)
    "Fleet": (0.04, 0.06, lambda v, r: v * 50), "Steadfast": (0.09, 0.15, lambda v, r: v * 20),
    "Tempered": (1.1, 1.9, lambda v, r: v * 2), "Lucky": (1.1, 1.7, lambda v, r: v * 2),  # utility, valued low
}
TIERS = {"uncommon": (1, 1.0), "rare": (2, 1.2), "epic": (3, 1.4), "legendary": (4, 1.6)}  # affixes, roll power
AFFIX_BUDGET = (2, 4)  # one uncommon affix's worth (docs/BALANCE.md power scale)


def weapon_hit(r):
    return st.median(w["damage"] for w in weapons()[(r, "sword")])


def armour_gain(v, r):
    a, t = MEDIUM[r]
    return (kept(1, a, t) / kept(1, a * (1 + v), t) - 1) * 100


def print_affixes():
    print("PASS 5 - affixes (mid roll, worth in % at each rank; budget for one uncommon affix "
          f"{AFFIX_BUDGET[0]}-{AFFIX_BUDGET[1]})")
    print("  " + f"{'affix':10}" + "".join(f"{r:>6}" for r in "FCS"))
    for k, (lo, hi, f) in AFFIXES.items():
        v = (lo + hi) / 2
        print(f"  {k:10}" + "".join(f"{fmt(f(v, r), *AFFIX_BUDGET, '{:.1f}'):>6}" for r in "FCS"))
    combat = [f((lo + hi) / 2, "C") for k, (lo, hi, f) in AFFIXES.items() if k in ("Keen", "Swift", "Brutal", "Hale", "Warded")]
    avg = st.mean(combat)
    for t, (n, pw) in TIERS.items():
        print(f"  {t:10} {n} affixes x{pw}: about +{n * avg * pw:.0f}% on top of the weapon")
    arms = load("ashbound/world_arms.json")
    ws = weapons()
    print("  world weapons' own damage next to the same rank's dungeon weapon:")
    for t in TIERS:
        rs = []
        for a in arms:
            got = ws.get((a["rank"], a["kind"]))
            if a["rarity"] == t and got and a.get("damage") and got[0]["damage"]:
                rs.append(a["damage"] / st.median(w["damage"] for w in got))
        if rs:
            print(f"    {t:10} x{st.median(rs):.2f} (of {len(rs)})")


# --- curios and relics (tools/curios.py -> curios.json) ---------------------------------------------------------------
# their own stats' worth, besides the tree's (TREE_WORTH): utility ones low, Ash/coins nothing in a fight
CURIO_WORTH = {"armour%": 0.5, "tough%": 0.3, "kb%": 0.3, "elite_dmg%": 0.5, "poison_short%": 0.08, "dodge_cost%": 0.3,
               # utility: no fight in it, but it speeds the game up (levels, loot, coins) or gets you places
               "luck": 2.0, "ash%": 0.5, "coins%": 0.3, "safe_fall": 0.5, "mining%": 0.15, "oxygen": 0.5, "swim%": 0.1}
# a curio's stats by rarity, in % (docs/RELICS.md: U ~3, R ~4.5, E ~6 + a perk, L ~6 + an effect; relics' stats ride along)
CURIO_BUDGET = {"uncommon": (2.4, 3.6), "rare": (3.8, 5.2), "epic": (5.0, 7.0), "legendary": (5.0, 7.5),
                "relic": (2.4, 3.6)}   # a relic's stats ride along its power


def curio_worth(stats):
    return sum(CURIO_WORTH.get(k, TREE_WORTH.get(k, 1)) * v for k, v in stats.items())


def print_curios():
    cs = load("ashbound/curios.json")
    print("CURIOS - stats' worth in % against their rarity's budget (effects not counted)")
    by = {}
    off = []
    for c in cs:
        w = curio_worth(c["stats"])
        by.setdefault((c["slot"], c["rarity"]), []).append(w)
        lo, hi = CURIO_BUDGET["relic" if c["slot"] == "relic" else c["rarity"]]
        if not lo <= w <= hi:
            off.append(f"{c['id']} ({c['rarity']} {c['slot']}) {w:.1f} " + ("↓" if w < lo else "↑") + f"  {c['stats']}")
    for (slot, rar), ws in sorted(by.items()):
        print(f"  {slot:7} {rar:10} {len(ws):2}  worth {st.mean(ws):4.1f}  ({min(ws):.1f}-{max(ws):.1f})")
    full = {r: st.mean(w for (s_, rr), ws in by.items() if rr == r and s_ != "relic" for w in ws) for r in CURIO_BUDGET if r != "relic"}
    print(f"  a full kit (2 rings, amulet, charm) of one rarity: " + ", ".join(f"{r} +{4 * v:.0f}%" for r, v in full.items()))
    print(f"  off budget: {len(off)}")
    for o in off:
        print("    " + o)


# --- one rank up ----------------------------------------------------------------------------------------------------
RANK_UP = (2.2, 3.4)   # how much harder the next rank is in your old gear (Diablo 3's Torment step is about 2.3); the gear it drops takes that back to ~1.65 (pass 11)


def print_rank_up():
    """a player with rank r gear and level against rank r+1's monsters: kills take longer x they die sooner"""
    rows1, rows2, _ = report()
    k1 = {l["rank"]: l for l in rows1}
    k2 = {l["rank"]: l for l in rows2}
    mobs = monsters()
    ws = weapons()
    print("ONE RANK UP - your rank's gear, level and build against the next rank's monsters (sword, medium armour)")
    for a, b in zip(RANKS, RANKS[1:]):
        if a not in k1 or b not in k1:
            continue
        hit = st.median(w["damage"] for w in ws[(a, "sword")]) * build(a)[0]
        def med(r, role, key):
            return st.median(m[3][key] * (m[4] if key == "hp" else 1) for m in mobs if m[0] == r and m[1] == role)
        kill = (med(b, "normal", "hp") / armour_cut(hit, med(b, "normal", "armor"))) / (med(a, "normal", "hp") / armour_cut(hit, med(a, "normal", "armor")))
        arm, t = set_armour("medium", a)
        hurt = kept(med(b, "normal", "dmg"), arm, t) / kept(med(a, "normal", "dmg"), arm, t)
        x = kill * hurt
        step = WEAPON_STEP * kept(1, arm, t) / kept(1, *set_armour("medium", b))
        print(f"  {a} -> {b}: kills take x{kill:.2f}, hits hurt x{hurt:.2f}  =  {fmt(x, *RANK_UP, '{:.2f}x')}, in that rank's gear x{x / step:.2f}")


# --- pass 4: the skill tree (tools/skilltree.py -> skill_tree.json) ---------------------------------------------------
# what one unit of each node stat is worth in "% more damage or survivability" (docs/BALANCE.md power scale)
TREE_WORTH = {"dmg%": 1, "speed%": 1, "arrow%": 1, "spell%": 1, "heal%": 1, "thrall_dmg%": 1, "health%": 1, "move%": 0.6,
              "negation%": 0.4, "impact": 4, "stun_armour": 1, "armour%": 0.5, "stamina": 2, "stamina_regen%": 0.3,
              "mana": 0.25, "mana_regen%": 1, "thrall_hp%": 0.5, "velocity%": 0.4, "reach": 10, "guard%": 0.5,
              "strikes": 4, "knockback": 2, "weight%": -0.05, "ash%": 0}
SMALL_BUDGET = (0.8, 1.6)


def print_tree():
    t = load("ashbound/skill_tree.json")
    print("PASS 4 - the skill tree (a small node should be worth ~1)")
    by = {}
    for n in t["nodes"]:
        if n["kind"] == "small":
            w = sum(TREE_WORTH.get(k, 1) * v for k, v in n["stats"].items())
            by.setdefault(n["area"], []).append(w)
    for area, ws in by.items():
        print(f"  {area:10} {len(ws):3} small nodes, worth {fmt(st.mean(ws), *SMALL_BUDGET, '{:.2f}'):>6} each, "
              f"area total {sum(ws):5.1f}")
    unknown = {k for n in t["nodes"] for k in list(n["stats"]) + list(n.get("always", {})) if k not in TREE_WORTH}
    if unknown:
        print("  stats with no worth set:", ", ".join(sorted(unknown)))


def print_speed():
    """PASS 6: attack speed. Every melee weapon's real damage a second with Epic Fight's swing timing, the kinds
    against the sword, single items against their kind, and Titan's Grip against everything"""
    print("PASS 6 - attack speed (Epic Fight swing timing; DPS before armour)")
    print("  hits a second at each kind's speed: " + ", ".join(
        f"{k} {hits_per_s(c, s):.2f} (vanilla {s})" for k, c, s in (("sword", "sword", 1.6), ("dagger", "dagger", 2.4),
        ("spear", "spear", 1.2), ("hammer", "greatsword", 0.85), ("twohander", "greatsword", 0.85))))
    print(f"  Titan's Grip (dual sword moves at a two-hander's 0.85): {hits_per_s('titan', 0.85):.2f} hits/s; "
          f"two swords: {hits_per_s('sword_dual', 1.6):.2f}")
    ws = weapons()
    print(f"  {'rank':4} " + " ".join(f"{k:>16}" for k in KIND_DPS) + f" {'two swords':>11} {'TITAN':>14}")
    base = {}
    for r in RANKS:
        if (r, "sword") not in ws:
            continue
        sword = dps("sword", ws[(r, "sword")], r)[0]
        cells = []
        for k in KIND_DPS:
            if (r, k) not in ws:
                cells.append(f"{'-':>16}")
                continue
            v = dps(k, ws[(r, k)], r)[0]
            base[(r, k)] = v
            cells.append(f"{v:5.1f} {fmt(v / sword, *KIND_DPS[k], '{:.2f}x'):>9}")
        sd = st.median(w["damage"] for w in ws[(r, "sword")])
        duo = sd * hits_per_s("sword_dual", 1.6)
        th = st.median(w["damage"] for w in ws[(r, "twohander")]) if (r, "twohander") in ws else 0
        titan = th * TITAN_DMG * hits_per_s("titan", 0.85)
        print(f"  {r:4} " + " ".join(cells) + f" {duo:5.1f} {duo / sword:4.2f}x {titan:5.1f} {titan / sword:4.2f}x")
    gs = hits_per_s("greatsword", 0.85)
    tt = hits_per_s("titan", 0.85)
    print(f"  Titan's Grip vs one two-hander: {tt * TITAN_DMG / gs:.2f}x damage a second, "
          f"+{TITAN_STAMINA * tt:.1f} stamina a second spent")
    # single items: each weapon's DPS against its kind's dungeon median at that rank (boss drops expected a bit more)
    odd = []
    items = [(d["rank"], w, "dungeon" if not w["boss"] else "boss") for d in load("ashbound/gear.json") for w in d["weapons"]]
    items += [(w["rank"], w, "world " + w.get("rarity", "")) for w in load("ashbound/world_arms.json")]
    for r, w, src in items:
        k = w["kind"]
        if k not in COMBO or (r, k) not in base or not w.get("damage"):
            continue
        v = w["damage"] * hits_per_s(COMBO[k], w["speed"])
        want = base[(r, k)] * (WEAPON_STEP if src == "boss" else 1.0)
        if abs(v / want - 1) > 0.12:
            odd.append(f"{w['id']} ({r} {k}, {src}) {v:.1f} vs {want:.1f} = {v / want:.2f}x")
    print(f"  items more than 12% off their kind at their rank: {len(odd)}")
    for o in odd[:40]:
        print("    " + o)


# --- pass 8: the 54 skills (Skills.java, SkillArts.java), rank I. On one target and on three, in the class's own unit
# (w a weapon blow, b a bolt, a an arrow), as a share of the damage the class does anyway.
# name: (level tier, unit, one target, three targets, cooldown s, mana)
SKILLS = {
    "vanguard": {"Bastion Slam": (1, "w", 1.4, 4.2, 14, 0), "Oath Charge": (1, "w", 1.8, 5.4, 12, 0), "Shield Wall": (2, "u", 0, 0, 24, 0), "Crossing Oath": (2, "w", 2.2, 4.4, 10, 0),
                 "Unbroken": (3, "w", 5, 15, 60, 0), "Last Oath": (3, "w", 6, 12, 30, 0)},
    "breaker": {"Rift Slam": (1, "w", 2.6, 7.8, 16, 0), "Headsman's Drop": (1, "w", 5, 5, 20, 0), "Fault Line": (2, "w", 2.2, 6.6, 14, 0), "Reaper's Mark": (2, "w", 5.3, 5.3, 18, 0),
                "Worldbreaker": (3, "w", 7.8, 23.4, 36, 0), "Beheading": (3, "w", 7.5, 7.5, 30, 0)},
    "reaver": {"Blood Price": (1, "w", 3, 9, 12, 0), "Steel Tempest": (1, "w", 3.9, 11.7, 15, 0), "Red Thirst": (2, "u", 0, 0, 22, 0), "Razor Gale": (2, "w", 2, 6, 13, 0),
               "Crimson Rite": (3, "w", 9, 27, 40, 0), "Eye of the Storm": (3, "w", 9, 27, 36, 0)},
    "lancer": {"Skyfall": (1, "w", 2.5, 7.5, 14, 0), "Spear Wall": (1, "w", 2.6, 5.2, 12, 0), "Dragon Lunge": (2, "w", 2, 4, 10, 0), "Spear Hedge": (2, "w", 2.2, 6, 14, 0),
               "Dragon's Descent": (3, "w", 7, 21, 32, 0), "Thousand Thrusts": (3, "w", 6, 12, 28, 0)},
    "shade": {"Vanish": (1, "w", 3.2, 3.2, 16, 0), "Viper Bite": (1, "w", 2.4, 7.2, 10, 0), "Smoke Step": (2, "u", 0, 0, 10, 0), "Toxic Cloud": (2, "w", 2.1, 6.3, 16, 0),
              "Death Blossom": (3, "w", 6.5, 6.5, 30, 0), "Plague Bloom": (3, "w", 6, 18, 30, 0)},
    "hunter": {"Deadeye": (1, "a", 3, 3, 16, 0), "Snare Field": (1, "w", 1.2, 3.6, 14, 0), "Arrow Rain": (2, "a", 1.7, 5, 18, 0), "Spike Pit": (2, "w", 3, 9, 14, 0),
               "Piercing Star": (3, "a", 6.75, 13.5, 32, 0), "Killing Ground": (3, "u", 0, 0, 34, 0)},
    "ashcaster": {"Cinder Field": (1, "b", 3.15, 9.45, 14, 30), "Black Hole": (1, "b", 3, 9, 18, 34), "Flame Lance": (2, "b", 1.6, 3.2, 10, 16), "Void Lances": (2, "b", 1.6, 4.8, 12, 16),
                  "Meteor": (3, "b", 6, 18, 30, 60), "Event Horizon": (3, "b", 7.4, 22, 32, 70)},
    "mender": {"Mass Renewal": (1, "u", 0, 0, 30, 60), "Judgement": (1, "b", 2.5, 2.5, 16, 0), "Sanctify": (2, "u", 0, 0, 24, 40), "Holy Lance": (2, "b", 1.8, 3.6, 10, 0),
               "Second Dawn": (3, "u", 0, 0, 90, 90), "Heaven's Wrath": (3, "b", 5.6, 12, 36, 0)},
    "caller": {"Bone Horde": (1, "u", 0, 0, 60, 90), "Bound Champion": (1, "u", 0, 0, 60, 90), "Marrow Burst": (2, "u", 0, 0, 16, 30), "Soul Mend": (2, "u", 0, 0, 20, 40),
               "Legion": (3, "u", 0, 0, 90, 95), "Ascended": (3, "u", 0, 0, 60, 80)},
}
BASE_RATE = {"w": 1.29, "b": 0.44, "a": 0.54}   # of each unit a second a class does anyway (solved uptime)
BOLT_MANA = SPELL["black"][1]
SKILL_BUDGET = {1: (0.10, 0.36), 2: (0.10, 0.36), 3: (0.14, 0.40)}   # share of a class's own damage, one target
SKILL_USE = 0.7     # how much of the time a skill really goes off on cooldown
BOOK_RANK = {"F": 1, "E": 1, "D": 2, "C": 2, "B": 3, "A": 3, "S": 4}   # the rank a player's skills have reached
PER_RANK = 0.2


def skill_value(s):
    tier, unit, one, three, cd, mana = s
    net = mana / BOLT_MANA if unit == "b" and mana else 0   # the bolts that mana would have been
    return (one - net) / cd / BASE_RATE[unit], (three - net) / cd / BASE_RATE[unit]


def skill_share(rank):
    """what a rank's typical player adds to a long fight with their skills: one chosen for each level reached"""
    tiers = [t for t, lv in zip((1, 2, 3), (5, 20, 35)) if MID_LEVEL[rank] >= lv]
    x = 0
    for t in tiers:
        vals = [skill_value(s)[0] for c in SKILLS.values() for s in c.values() if s[0] == t and s[1] != "u"]
        x += st.median(vals)
    return x * SKILL_USE * (1 + PER_RANK * (BOOK_RANK[rank] - 1))


def print_skills():
    print("PASS 8 - skills, rank I: share of the class's own damage, one target / three (mana skills net of the bolts it would have bought)")
    for cls, ss in SKILLS.items():
        print(f"  {cls}")
        for name, s in ss.items():
            if s[1] == "u":
                print(f"    L{(5, 20, 35)[s[0] - 1]:<3} {name:18} utility, {s[4]} s" + (f", {s[5]} mana" + (" OVER THE BAR" if s[5] > MANA else "") if s[5] else ""))
                continue
            one, three = skill_value(s)
            print(f"    L{(5, 20, 35)[s[0] - 1]:<3} {name:18} {fmt(one * 100, SKILL_BUDGET[s[0]][0] * 100, SKILL_BUDGET[s[0]][1] * 100, '{:.0f}%'):>6} / {three * 100:3.0f}%   {s[4]} s")
    print("  a rank's typical player, all skills going: " + "  ".join(f"{r} +{skill_share(r) * 100:.0f}%" for r in RANKS))


# --- pass 12: every class alone, and parties of 1 to 6 ------------------------------------------------------------------
# A class's damage a second next to the sword's on one target, once its skills are counted (PASS 1, PASS 8), and what it gives up: a Vanguard
# spends time blocking, a Mender healing; alone a Mender's casts burn what's near (Spells.sear). PARTY_DPS is what they do with a party to look after.
# pass 13b: lancer x1.15 (Passives.KIND_EDGE spear), breaker x1.08 (hammer), caller x1.12 (THRALL_DMG 4.3 -> 4.8)
CLASS_DPS = {"vanguard": (0.85, 0.7), "breaker": (0.99, 0.99), "reaver": (0.98, 0.98), "lancer": (1.06, 1.06), "shade": (0.96, 0.96), "hunter": (0.82, 0.82),
             "ashcaster": (0.93, 0.93), "mender": (0.62, 0.3), "caller": (1.06, 1.06)}
CLASS_WEARS = {"vanguard": "heavy", "breaker": "heavy", "reaver": "medium", "lancer": "medium", "shade": "light", "hunter": "light", "ashcaster": "robe", "mender": "robe", "caller": "robe"}
CLASS_SAFE = {"vanguard": 2.0, "hunter": 1.5, "ashcaster": 1.5, "mender": 1.8, "caller": 1.6}   # ranged, self-heals and thralls in the way: hits landed on you come less often
COMPS = {1: ("reaver",), 2: ("vanguard", "reaver"), 3: ("vanguard", "mender", "reaver"), 4: ("vanguard", "mender", "reaver", "ashcaster"),
         5: ("vanguard", "mender", "reaver", "ashcaster", "caller"), 6: ("vanguard", "mender", "reaver", "ashcaster", "caller", "hunter")}


def print_classes():
    print("PASS 12 - every class alone at a rank's boss, against the sword's target (time) and medium's hits (survival, in robe/light/medium/heavy as it wears)")
    print("  " + f"{'class':10}" + "".join(f"{r + ' boss s':>10}" for r in "FCS") + "".join(f"{r + ' hits':>9}" for r in "FCS"))
    for c, (solo, _) in CLASS_DPS.items():
        row = "".join(f"{CURVE[r]['boss_solo_s'] / solo:>10.0f}" for r in "FCS")
        hits = ""
        for r in "FCS":
            a, t = set_armour(CLASS_WEARS[c], r)
            hits += f"{CURVE[r]['hits_normal'] * kept(1, *set_armour('medium', r)) / kept(1, a, t) * CLASS_SAFE.get(c, 1):>9.1f}"
        print(f"  {c:10}" + row + hits)
    slow = max(CURVE["S"]["boss_solo_s"] / v[0] for v in CLASS_DPS.values()) / CURVE["S"]["boss_solo_s"]
    print(f"  slowest alone is {slow:.2f}x the target, a long fight but a winnable one")
    print("PARTY - a rank C gate: the usual party at each size, and five of one kind")
    print(f"  {'players':8}{'monster hp':>11}{'boss s':>8}{'x solo':>7}{'all dps':>9}{'ash each':>9}{'levels/h':>9}{'mats/h':>8}  party")
    solo_t = CURVE["C"]["boss_solo_s"] / CLASS_DPS["reaver"][0]
    for n, comp in COMPS.items():
        hp = 1 + PARTY["hp_per_player"] * (n - 1)
        dps = sum(CLASS_DPS[c][1 if n > 1 else 0] for c in comp)
        t = CURVE["C"]["boss_solo_s"] * hp / dps
        share = 1 / (1 + PARTY["reward_share"] * (n - 1))
        print(f"  {n:<8}{hp:>10.2f}x{t:>8.0f}{t / solo_t:>7.2f}{CURVE['C']['boss_solo_s'] * hp / n:>9.0f}{share:>9.0%}{share * solo_t / t:>8.2f}x{solo_t / t:>7.2f}x  " + ", ".join(comp))


def print_party():
    print("PARTY - health +%d%% a player, boss damage +%d%%; Ash and coins a head 1 / (1 + %.2f (n - 1))" % (PARTY["hp_per_player"] * 100, PARTY["boss_dmg_per_player"] * 100, PARTY["reward_share"]))
    print(f"  {'players':8} {'boss hp':>8} {'boss s':>7} {'elite s':>8} {'boss hits':>10} {'reward':>7} {'levels x solo':>14}")
    for n in (1, 2, 3, 4, 6, 8):
        hp = 1 + PARTY["hp_per_player"] * (n - 1)
        pace = hp / n
        share = 1 / (1 + PARTY["reward_share"] * (n - 1))
        print(f"  {n:<8} {hp:>7.2f}x {SOLVE['boss_solo_s'] * pace:>7.0f} {SOLVE['elite_s'] * pace:>8.1f} {1 + PARTY['boss_dmg_per_player'] * (n - 1):>9.2f}x {share:>6.0%} {share / pace:>13.2f}x")


def solve():
    """per-monster health and damage multipliers that put every rank's median on the targets; keeps each monster's
    hand-set strength next to its neighbours"""
    mobs = monsters(raw=True)
    ws = weapons()
    mult, foreman, ranks, armour, plain, role_at = {}, {}, {}, {}, {}, {}
    for r in RANKS:
        S = CURVE[r]
        here = [m for m in mobs if m[0] == r]
        if not here:
            continue
        sw = ws[(r, "sword")]
        hit = st.median(w["damage"] for w in sw)
        spd = hits_per_s("sword", st.median(w["speed"] for w in sw))  # real hits a second, not vanilla's swings
        a, t = set_armour("medium", r)
        off, dfn = build(r)
        hit *= off
        hp = player_hp(r) * dfn   # the build's defence as more health to chew through
        want, target, arms = {}, {}, {}
        for role in ("normal", "elite", "boss"):
            g = [m for m in here if m[1] == role and m[4] == 1]
            arm = st.median(m[3]["armor"] for m in g)
            arms[role] = arm
            cut = armour_cut(hit, arm)
            more = 1 + skill_share(r)   # skills shorten long fights; a normal monster is dead before they matter
            hp_t = {"normal": S["normal_hits"] * cut, "elite": S["elite_s"] * UPTIME["elite"] * spd * cut * more,
                    "boss": S["boss_solo_s"] * UPTIME["boss"] * spd * cut * more}[role]
            dmg_t = {"normal": raw_for(hp, a, t, S["hits_normal"]), "elite": raw_for(hp, a, t, S["hits_elite"]),
                     "boss": raw_for(hp, a, t, S["hits_big"]) / BIG_HIT}[role]
            hm = hp_t / st.median(m[3]["hp"] for m in g)
            dm = dmg_t / st.median(m[3]["dmg"] for m in g)
            want[role] = (hm, dm)
            target[role] = (hp_t, dmg_t)
            for m in g:
                mult.setdefault(m[3]["id"], (round(hm, 3), round(dm, 3), role, r))
        # a tower's foremen are its own floor monsters raised to elite health
        for tw in {m[2] for m in here if m[2].startswith("tower ") and m[1] == "normal"}:
            g = [m for m in here if m[2] == tw and m[1] == "normal"]
            arm = st.median(m[3]["armor"] for m in g)
            foreman[tw.split()[1]] = round(S["elite_s"] * UPTIME["elite"] * spd * armour_cut(hit, arm) * (1 + skill_share(r)))  # a foreman's health
        for m in here:
            if m[1] == "elite" and m[4] != 1:
                mult.setdefault(m[3]["id"], (1.0, round(want["elite"][1], 3), "elite", r))
        ranks[r] = {k: [round(x, 3) for x in v] for k, v in want.items()}
        role_at[r] = {k: [round(v[0], 1), round(v[1], 2), round(arms[k], 1)] for k, v in target.items()}
        if r == BEAST_RANK:
            for k, role in ASHFALL.items():
                mult[k] = (round(want[role][0], 3), round(want[role][1], 3), role, r)
        if r == BEAST_RANK:     # each beast right on its role's target, not dragging the rank's medians about
            gm = {m["id"]: m for m in load("ashbound/gate_mobs.json")}
            if (RES / "ashbound/beasts.json").exists():   # the ones on their own skeletons (beastkit.py)
                gm.update({k: dict(v, id=k) for k, v in load("ashbound/beasts.json").items()})
            for role in ("elite", "boss"):  # one multiplier a role: the median beast on target, each keeps its own build
                g = [gm[b] for b, ro in BEASTS.items() if ro == role and b in gm]
                if g:
                    # a Legend roams the open world, met solo or by a few: lighter than a gate's boss (LEGEND_HP of its health, LEGEND_DMG of its hits)
                    soft_hp, soft_dmg = (LEGEND_HP, LEGEND_DMG) if role == "boss" else (1.0, 1.0)
                    hm, dm = soft_hp * target[role][0] / st.median(m["hp"] for m in g), soft_dmg * target[role][1] / st.median(m["dmg"] for m in g)
                    for m in g:
                        mult[m["id"]] = (round(hm, 3), round(dm, 3), role, r)
        # pass 13: a rank's bosses kept in a band round its target (variety, not 0.6x to 1.7x of each other); a tower's boss is its climb's top
        for m in here:
            k = m[3]["id"]
            if m[1] not in ("boss", "elite") or m[4] != 1 or k not in mult or mult[k][2] != m[1]:
                continue
            h, d, role, rr = mult[k]
            lo, hi = (TOWER_BOSS_BAND if m[2].startswith("tower ") else BOSS_BAND) if role == "boss" else ELITE_BAND
            dlo, dhi = BOSS_DMG_BAND if role == "boss" else ELITE_DMG_BAND
            ratio, dr = m[3]["hp"] * h / target[role][0], m[3]["dmg"] * d / target[role][1]
            mult[k] = (round(h * min(hi, max(lo, ratio)) / ratio, 3), round(d * min(dhi, max(dlo, dr)) / dr, 3), role, rr)
        gm_all = {m["id"]: m for m in load("ashbound/gate_mobs.json")}
        for k, (rk, hx, dx) in {**STORY_BOSSES, **WORLD_BOSSES}.items():
            if rk == r and k in gm_all:
                mult[k] = (round(hx * target["boss"][0] / gm_all[k]["hp"], 3), round(dx * target["boss"][1] / gm_all[k]["dmg"], 3), "boss", r)
        # each other class's armour so it survives its target number of this rank's normal hits
        ndmg = st.median(m[3]["dmg"] * mult[m[3]["id"]][1] for m in here if m[1] == "normal")
        plain[r] = [round(st.median(m[3]["hp"] * mult[m[3]["id"]][0] for m in here if m[1] == "normal"), 1), round(ndmg, 2)]
        for cls in CLASS_ARMOUR:
            if cls != "medium":
                armour.setdefault(cls, {})[r] = [round(MEDIUM[r][0] * CLASS_ARMOUR[cls]), round(TOUGH[cls] * ARMOUR_SCALE[r], 2)]
    out = {"_about": "written by tools/balance.py --solve; mobs: [health x, damage x, role, rank] on top of each monster's own numbers; foreman_hp: a tower foreman's health",
           "player": {"hp": PLAYER_HP, "hp_per_level": HP_PER_LEVEL, "armour_k": ARMOUR_K, "tough_per": TOUGH_PER}, "party": PARTY, "haunt_rank": HAUNT_RANK,
           "rank_normal": plain, "rank_role": role_at, "band_top": {r: hi for r, (lo, hi) in BAND.items()}, "crowd": CROWD,
           "foreman_hp": foreman, "ranks": ranks, **progress(mult),
           "armour": dict(armour, medium={r: [a, round(t, 2)] for r, (a, t) in MEDIUM.items()}), "mobs": dict(sorted(mult.items()))}
    BAL.write_text(json.dumps(out, indent=1), encoding="utf-8")
    ARMOUR_TABLE.update({c: {r: tuple(v) for r, v in t.items()} for c, t in out["armour"].items()})
    for c in ("robe", "light", "medium", "heavy"):
        print(f"  {c:7} armour " + "  ".join(f"{r} {sum(pieces(out['armour'][c][r][0]))}" for r in out["armour"][c]))
    print(f"wrote {BAL.relative_to(ROOT)}: {len(mult)} monsters")
    for r, v in ranks.items():
        print(f"  {r}: " + "  ".join(f"{k} hp x{h:.2f} dmg x{d:.2f}" for k, (h, d) in v.items()) )
    print("  tower foremen: " + ", ".join(f"{k} {v} hp" for k, v in foreman.items()))


def print_report():
    rows1, rows2, mobs = report()
    print("PASS 1 - weapons vs monster health (median weapon of the rank, median monster; ↑/↓ = outside target)")
    print("  targets by rank (CURVE): " + "  ".join(f"{r} {CURVE[r]['normal_hits']} hits/{CURVE[r]['elite_s']}s/{CURVE[r]['boss_solo_s']}s" for r in RANKS))
    for l in rows1:
        print(f"\n  {l['rank']}: normal {l['normal_hp']:.0f} hp, elite {l['elite_hp']:.0f}, boss {l['boss_hp']:.0f}")
        print(f"    {'weapon':10} {'dps':>5} {'hits/normal':>12} {'elite s':>9} {'boss s':>9}")
        o, dd = build(l["rank"])
        print(f"    (the rank's typical build: +{(o - 1) * 100:.0f}% damage, +{(dd - 1) * 100:.0f}% survival)")
        for k, (d, h, e, b) in l["kinds"].items():
            r = l["rank"]
            print(f"    {k:10} {d:5.1f} {fmt(h, *goal(r, 'normal_hits'), '{:.1f}'):>12} {fmt(e, *goal(r, 'elite_s')):>9} {fmt(b, *goal(r, 'boss_solo_s')):>9}")
    print("\nPASS 2 - monster damage vs armour (full set of the rank; player health at the rank's middle level)")
    print("  medium is on CURVE; the other classes follow their armour (CLASS_ARMOUR); big attack about a third")
    for l in rows2:
        print(f"\n  {l['rank']}: player {player_hp(l['rank']):.0f} hp, normal hit {l['normal_dmg']:.1f}, boss big attack {l['boss_big']:.1f}")
        for c, (a, t, hn, hb) in l["cls"].items():
            lo, hi = class_hits(l["rank"], c)
            print(f"    {c:7} armour {a:3} tough {t:3.1f}  takes {kept(100, a, t):2.0f}%   normal {fmt(hn, lo, hi, '{:.1f}'):>6}   big {fmt(hb, lo * 0.3, hi * 0.42, '{:.1f}'):>6}")
    unranked = {m[2] for m in mobs if m[0] == "?"}
    if unranked:
        print("UNRANKED: " + ", ".join(sorted(unranked)))


def print_mobs():
    for r in RANKS + "?":
        for role in ("normal", "elite", "boss"):
            ms = [m for m in monsters() if m[0] == r and m[1] == role]
            if ms:
                print(f"{r} {role}: " + ", ".join(f"{m[3]['id']} {m[3]['hp'] * m[4]:.0f}/{m[3]['dmg']:.0f}/{m[3]['armor']:.0f}" for m in ms))


if __name__ == "__main__":
    if "--solve" in sys.argv:
        solve()
    elif "--mobs" in sys.argv:
        print_mobs()
    else:
        print_report()
        print()
        print_speed()
        print()
        print_breath()
        print()
        print_progress()
        print()
        print_affixes()
        print()
        print_tree()
        print()
        print_curios()
        print()
        print_rank_up()
        print()
        print_skills()
        print()
        print_party()
        print()
        print_classes()
