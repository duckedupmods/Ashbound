"""Pass 15: who can beat what. A Monte Carlo fight sim on balance_sim's numbers: every fight played RUNS times with
dice (which blow lands, who it goes to, when the big attack comes, damage spread), at three player skills, so each cell
is a WIN CHANCE, not an average. Shows what a party without a healer can beat that one with a healer can (and the other
way round), e.g. a ranger and a tank.

    python -X utf8 tools/balance_mc.py              ranks F D B S, the main parties
    python -X utf8 tools/balance_mc.py --all        every rank
    python -X utf8 tools/balance_mc.py --runs 400   more dice (slower, steadier)

How (the method from simulation-based balancing: set a measurable target, sim it with rule-driven agents, change one knob,
re-sim):
- the party focuses one monster at a time; every living monster swings every MOB_SWING s on average (Poisson), at a
  target picked by threat (balance_sim.target_weights); a blow lands by the player's SKILL, less on ranged and blocking
  classes (balance.CLASS_SAFE); after the first monster the rest hit for balance.CROWD
- elites and bosses throw a big attack (BIG_HIT x) every BIG_EVERY s on average; a skilled player dodges most of them
- everyone has SUSTAIN and drinks a potion under half; a Mender heals the ones in the circle every MEND_EVERY s and, with
  skills, throws the Accord when someone drops under half (a rule-driven healer, like the healer sims do)
- a dead player stays dead (no revive in the fight); the fight is lost when everyone is down, or after CAP s
"""
import sys

import numpy as np

import balance as B
import balance_sim as S

# The player, as Epic Fight plays them (pass 16): every swing aimed at you that reaches you is ROLLED (4 stamina, the
# i-frames work by your timing), BLOCKED if you carry a shield (stamina = the blow's impact x guard's 0.6 penalizer; no
# stamina left = guard break: the blow lands and you're stunned), or it lands. Attacking spends the same stamina bar, so
# every roll is swings you don't make. A careful player keeps RESERVE stamina back for rolls and stops swinging to let it
# fill (Epic Fight: 15 bar, refills only after 1.5 s of not spending, ~3.75 a second with our 1.25 regen).
SKILL = {   # roll timing on a swing, on a big attack, block timing, stamina kept back, damage focus
    "new": dict(dodge=0.35, dodge_big=0.30, block=0.75, reserve=0.0, focus=0.85),
    "ok": dict(dodge=0.65, dodge_big=0.60, block=0.90, reserve=4.0, focus=1.0),
    "good": dict(dodge=0.85, dodge_big=0.85, block=0.97, reserve=8.0, focus=1.1),
}
STAM_MAX, STAM_REGEN, STAM_IDLE, ROLL = 15.0, 15 * 0.01 * 1.25 * 20, 1.5, 4.0   # Epic Fight roll.json: 4; step.json: 3
ATTACK_COST = {"melee": 1.25, "tank": 1.25, "ranged": 1.1, "healer": 0.0}     # Passives.swingCost ~1.25/s; BOW_COST 1.2 a shot; casters spend mana
CASTERS = {"ashcaster", "mender", "caller"}
BLOCK_COST, BLOCK_COST_BIG = 2.0 * 0.6, 5.0 * 0.6    # guard.json penalizer 0.6 x the blow's impact (assumed 2 a swing, 5 a big attack)
IN_REACH = {"tank": 0.75, "melee": 0.65, "ranged": 0.35, "healer": 0.45}   # how often a swing aimed at you finds you in its reach
DECOY = {"caller": 0.35}     # a Caller's thralls take this much of the boss's attention
SPLASH = 0.4                 # a big attack also catches each other melee player near the target this often
POSITION = 0.75              # share of the fight a player is placed to hit at all (walking in, the boss moving, its skills)
STUN = 1.5
DT, CAP = 0.5, 1500.0
GUARD_BREAK = False    # a boss's big attacks go through a shield (MobSkills)
HEAL_X = 1.0
MANA, MANA_REGEN, MEND_COST = 100.0, 100 * 0.06 * 1.1, 38.0   # Spells: a 100 bar, 6%/s while casting (+10% a robe set), a white cast 38
SPREAD = 0.2           # damage dice: +-20% a tick
KINDS = ("pack", "elite", "boss", "arena", "world", "legend", "king")
PARTIES = {
    "solo hunter": ("hunter",), "solo reaver": ("reaver",), "solo vanguard": ("vanguard",), "solo mender": ("mender",),
    "tank+ranger": ("vanguard", "hunter"), "heal+ranger": ("mender", "hunter"), "tank+heal": ("vanguard", "mender"),
    "2 dps": ("reaver", "hunter"),
    "tank+heal+ranger": ("vanguard", "mender", "hunter"), "tank+2dps": ("vanguard", "reaver", "hunter"),
    "heal+2dps": ("mender", "reaver", "hunter"), "3 dps": ("reaver", "hunter", "ashcaster"),
    "4 classic": ("vanguard", "mender", "reaver", "ashcaster"), "tank+3dps": ("vanguard", "reaver", "hunter", "ashcaster"),
    "heal+3dps": ("mender", "reaver", "hunter", "ashcaster"), "4 dps": ("reaver", "shade", "hunter", "ashcaster"),
}
PAIRS = [("tank+ranger", "heal+ranger", "tank+heal+ranger"), ("2 dps", "tank+ranger", "heal+ranger"),
         ("3 dps", "tank+2dps", "heal+2dps"), ("4 dps", "tank+3dps", "heal+3dps", "4 classic")]


def foes(kind, r, n):
    if kind == "king":
        if r != "S":
            return None
        hp, dmg, arm = S.own("founder_king")
        p = B.PARTY
        return [(hp * (1 + p["hp_per_player"] * (n - 1)), dmg * (1 + (p.get("solo_boss_dmg", 0) if n == 1 else p["boss_dmg_per_player"] * (n - 1))), arm, True)]
    return S.encounter(kind, r, n)


def fight(kind, r, comp, skill, runs, skills=True, rng=None, dmg_x=1.0, hp_x=1.0):
    """(win share, mean seconds of the won fights, mean players lost)"""
    fs = foes(kind, r, len(comp))
    if fs is None:
        return None
    fs = [(h * hp_x, d * dmg_x, a, b) for h, d, a, b in fs]
    rng = rng or np.random.default_rng(7)
    sk = SKILL[skill]
    n, m = len(comp), len(fs)
    party = [S.Fighter(c, r, skills) for c in comp]
    hit, rate = S.base_hit(r)
    more = 1 + (B.skill_share(r) if skills and kind != "pack" else 0)
    roles = [S.ROLE[c] for c in comp]
    dps = np.zeros((n, m))
    for i, c in enumerate(comp):
        share = B.CLASS_DPS["mender"][1] if c == "mender" and n > 1 else B.CLASS_DPS[c][0 if n == 1 else 1]
        share *= S.tree_edge(c, r)[0]
        for j, (_, _, arm, _) in enumerate(fs):
            dps[i, j] = rate * share * POSITION * B.armour_cut(hit * more, arm) * sk["focus"]
    mx = np.array([p.max for p in party])
    blow = np.array([[B.kept(d, *p.armour) for (_, d, _, _) in fs] for p in party])    # (n, m)
    crowd = np.array([1.0] + [B.CROWD[r]] * (m - 1))
    bigs = np.array([b for *_, b in fs])
    healer = np.array([ro == "healer" for ro in roles])
    tank = np.array([ro == "tank" for ro in roles])
    shield = tank.copy()
    melee = np.array([ro in ("tank", "melee") for ro in roles])
    reach = np.array([IN_REACH[ro] for ro in roles])
    cost = np.array([0.0 if c in CASTERS else ATTACK_COST[ro] for c, ro in zip(comp, roles)])
    decoy = max([DECOY.get(c, 0) for c in comp] + [0])
    heal = S.heal_amount(r) * HEAL_X

    hp = np.tile(mx, (runs, 1))
    st = np.full((runs, n), STAM_MAX)
    idle = np.zeros((runs, n))           # seconds since stamina was last spent
    rest = np.zeros((runs, n), bool)     # letting the bar fill
    stun = np.zeros((runs, n))
    alive = np.ones((runs, n), bool)
    fhp = np.tile(np.array([f[0] for f in fs]), (runs, 1))
    pot = np.full((runs, n), -1e9)
    mend_t = np.zeros(runs)
    mana = np.full(runs, MANA)
    accord_t = np.full(runs, -1e9)
    done = np.zeros(runs, bool)
    won = np.zeros(runs, bool)
    t_end = np.full(runs, CAP)
    t = 0.0
    R = np.arange(runs)
    spent = np.zeros((runs, n))
    dmg_in = np.zeros((runs, n))

    def take(mask, who, j, mult, big):
        """a blow aimed at `who` (runs,) from monster j: reach, block, roll or land"""
        idx = R[mask]
        w = who[mask]
        if not len(idx):
            return
        here = rng.random(len(idx)) < (1.0 if big else reach[w])
        idx, w = idx[here], w[here]
        if not len(idx):
            return
        ok = alive[idx, w] & (stun[idx, w] <= 0)
        bc = BLOCK_COST_BIG if big else BLOCK_COST
        blocks = ok & shield[w] & (st[idx, w] >= bc)
        broke = ok & shield[w] & ~blocks                      # no stamina left behind the shield: guard break
        held = blocks & (rng.random(len(idx)) < sk["block"])
        st[idx[blocks], w[blocks]] -= bc
        spent[idx[blocks], w[blocks]] = 1
        rolls = ok & ~shield[w] & (st[idx, w] >= ROLL)
        st[idx[rolls], w[rolls]] -= ROLL
        spent[idx[rolls], w[rolls]] = 1
        dodged = rolls & (rng.random(len(idx)) < (sk["dodge_big"] if big else sk["dodge"]))
        lands = ~held & ~dodged
        d = blow[w, j] * mult * (1 + SPREAD * rng.uniform(-1, 1, len(idx)))
        np.add.at(dmg_in, (idx[lands], w[lands]), d[lands])
        stun[idx[broke], w[broke]] = STUN

    while t < CAP and not done.all():
        live = ~done
        spent[:] = 0
        dmg_in[:] = 0
        # attacking: whoever isn't stunned, resting or dead, while their stamina lasts
        swing = alive & (stun <= 0) & ~rest & (st - cost * DT >= sk["reserve"])
        st -= swing * cost * DT
        spent += swing * (cost > 0)
        cur = np.argmax(fhp > 0, axis=1)
        out = (swing[:, :, None] * dps[None]).sum(1)[R, cur] * DT * (1 + SPREAD * rng.uniform(-1, 1, runs))
        fhp[R, cur] -= np.where(live, out, 0)
        # the monsters: each swing and big attack picks a target by threat (a Caller's thralls soak some)
        w = alive * np.where(tank, S.THREAT, 1 - S.THREAT)
        w = np.where(~(alive & tank).any(1, keepdims=True) | ~(alive & ~tank).any(1, keepdims=True), alive.astype(float), w)
        ws = w.sum(1, keepdims=True)
        ws[ws == 0] = 1
        cw = np.cumsum(w / ws, 1)
        for j in range(m):
            up_j = (fhp[:, j] > 0) & live & (rng.random(runs) >= decoy)
            sw = up_j & (rng.random(runs) < DT / S.MOB_SWING)
            bg = up_j & bigs[j] & (rng.random(runs) < DT / S.BIG_EVERY)
            for hits, mult, big in ((sw, crowd[j], False), (bg, B.BIG_HIT, True)):
                tgt = (rng.random((runs, 1)) > cw).sum(1).clip(0, n - 1)
                take(hits, tgt, j, mult, big)
                if big and n > 1:            # the big ones catch whoever's next to the target
                    for k in range(n):
                        near = hits & (tgt != k) & melee[k] & melee[tgt] & (rng.random(runs) < SPLASH)
                        take(near, np.full(runs, k), j, mult, True)
        hp -= dmg_in
        hp += S.SUSTAIN * mx * DT * alive
        # stamina: fills after STAM_IDLE s unspent; rest until nearly full once it's down to the reserve
        idle = np.where(spent > 0, 0, idle + DT)
        st = np.where(idle >= STAM_IDLE, np.minimum(STAM_MAX, st + STAM_REGEN * DT), st)
        rest = np.where(rest, st < STAM_MAX * 0.9, st - cost * DT < sk["reserve"] + ROLL * 0.5) & (cost > 0)
        stun = np.maximum(0, stun - DT)
        # potions under half
        drink = alive & (hp < mx * 0.5) & (t - pot >= S.POTION_CD)
        hp += drink * S.POTION * mx
        pot = np.where(drink, t, pot)
        # the Mender: the circle every MEND_EVERY s while the mana lasts, the Accord when someone's under half
        hl = (alive & healer).sum(1)
        mana = np.minimum(MANA * np.maximum(hl, 1), mana + MANA_REGEN * DT * hl)
        mending = live & (hl > 0) & (t - mend_t >= S.MEND_EVERY / np.maximum(hl, 1)) & (mana >= MEND_COST)
        mana = np.where(mending, mana - MEND_COST, mana)
        if healer.any():
            inside = alive & ((rng.random((runs, n)) < S.CIRCLE_REACH) | (n == 1))
            hp += (mending[:, None] & inside) * heal
            mend_t = np.where(mending, t, mend_t)
            if skills:
                low = (alive & (hp < mx * 0.5)).any(1)
                acc = live & (hl > 0) & low & (t - accord_t >= S.ACCORD_CD)
                hp += (acc[:, None] & alive) * S.ACCORD * mx
                accord_t = np.where(acc, t, accord_t)
        hp = np.minimum(hp, mx)
        alive &= hp > 0
        t += DT
        win_now = live & (fhp <= 0).all(1)
        lose_now = live & ~alive.any(1)
        won |= win_now
        t_end = np.where(win_now | lose_now, t, t_end)
        done |= win_now | lose_now
    lost = n - alive.sum(1)
    tw = t_end[won].mean() if won.any() else float("nan")
    return won.mean(), tw, lost[won].mean() if won.any() else n


def cell(kind, r, comp, runs, skills=True):
    out = [fight(kind, r, comp, s, runs, skills) for s in SKILL]
    if out[0] is None:
        return None
    return out


def pct(x):
    return f"{x * 100:3.0f}"


def main():
    args = sys.argv[1:]
    runs = int(args[args.index("--runs") + 1]) if "--runs" in args else 300
    ranks = args[args.index("--ranks") + 1] if "--ranks" in args else B.RANKS if "--all" in args else "FDBS"
    print(f"win chance %  new/ok/good player   ({runs} fights a cell; king = the Founder-King, S only)")
    table = {}
    for r in ranks:
        print(f"\n== {r}")
        print(f"  {'party':18}" + "".join(f"{k:>14}" for k in KINDS))
        for name, comp in PARTIES.items():
            row = f"  {name:18}"
            for k in KINDS:
                c = cell(k, r, comp, runs)
                table[(r, name, k)] = c
                row += f"{'-':>14}" if c is None else f"{'/'.join(pct(x[0]) for x in c):>14}"
            print(row)
    # the healer gap: what each party can do at an ok skill, side by side
    print("\nwhat they can beat, ok player (win >= 70%): Y yes, ~ coin flip (30-70%), . no")
    for r in ranks:
        print(f"  {r}")
        for group in PAIRS:
            for name in group:
                marks = ""
                for k in KINDS:
                    c = table[(r, name, k)]
                    marks += " " if c is None else "Y" if c[1][0] >= 0.7 else "~" if c[1][0] >= 0.3 else "."
                print(f"    {name:18}{' '.join(marks)}   ({' '.join(k[:2] for k in KINDS)})")
            print()


if __name__ == "__main__":
    main()
