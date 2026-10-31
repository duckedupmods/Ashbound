# Balance plan (10/29, plan only - nothing built yet)

Foundation first, fine-tuning at the end. Every system is balanced against the same targets, with one tool.

## 1. Targets per gate rank (set first, everything is tuned to them)

The player is at the rank's expected gear (that rank's Gate Forge set + a weapon of that rank) and level.

| | F | E | D | C | B | A | S | SSS |
|---|---|---|---|---|---|---|---|---|
| Expected level | 1-10 | 10-20 | 20-30 | 30-45 | 45-60 | 60-75 | 75-90 | 90-100 |
| Normal monster dies in | 3-5 hits | | | | | | | |
| Elite dies in | 10-15 s | | | | | | | |
| Boss solo / party of 4 | 2-4 min / ~1 min | | | | | | | |
| Hits you survive from a normal monster | 8-10 | | | | | | | |
| Hits you survive from a boss's big attack | 3-4 | | | | | | | |

(The numbers in the first column hold for every rank: monsters and gear scale together. Fill in or tweak per rank tomorrow.)

- One rank above your gear: about twice as hard. One rank below: easy, but no one-shots.
- Tank (shield + heavy armour) survives about 2x a mage's hits; a mage deals about 1.5x a tank's damage.

## 1b. Outside monsters (not only the gates)

Everything outside the gates gets a rank too, so it fits the same targets:
- the 14 factions' 84 monsters in the modpack's structures (Haunts), the 5 towers' 24 monsters, named elites/bounties,
  and the vanilla mobs once they're remade (zombie, skeleton, spider...).
- Their rank comes from WHERE they are: each structure kind/faction and each tower gets a rank band (e.g. Brigands E-D,
  a tower B-A), and/or the world gets harder with distance from spawn (decide tomorrow). Night spawns stay low rank.

## 1c. Solo and every kind of party

The targets must hold solo AND in a party (1-8 players), whatever the party is made of.
- **Party scaling:** a monster's health (and a boss's damage a little) grows with the players near it when it spawns
  or is first hit, e.g. +60-80% health per extra player, so a party isn't a steamroll and solo isn't impossible.
  Loot rolls per player (each gets their own drop), so parties aren't punished.
- **Every party kind** is checked by the simulator: each of the 10 weapon types solo; duos (tank + dps, healer + dps,
  dps + dps); the classic 4 (tank, healer, 2 dps); all-dps; all-summoners; 8 players. A party with no healer or no tank
  must still be able to win, just harder (no role is mandatory, the roles make it easier).
- Solo must be viable for every weapon type, including white staff and summoner (they get enough self-damage/self-heal).
- Bosses get mechanics that reward roles (a tank can hold aggro, a healer saves a wipe) without walls that need them.

## 2. One power scale

Everything gets a power cost in one currency, roughly "% more damage or survivability":
small tree node ~1, notable ~4-5, keystone ~15 minus its drawback, weapon affix ~2-4, relic by rarity, armour piece by rank.
Each tree area gets the same budget; a validator flags any area, node or item out of line.

## 3. Rules against runaway stacking

- "Increased" bonuses add within a kind (5 x +10% = +50%); only keystones multiply.
- Hard caps: damage reduction 75%, attack speed +60%, cooldowns at least half, dodge i-frames at most 2x, move speed +50%.
- One keystone at a time.

## 4. The tool: tools/balance.py (to build)

Reads the real data (gear.json weapons, armour sets, world_arms.json, gate_mobs.json + the faction/tower monsters,
relics, the tree) and works out, per rank:
- time to kill a normal monster / elite / boss with each weapon type,
- hits survived from each monster's attacks with each armour class,
- (later) the best 100-point build per tree area, compared against each other: outliers get nerfed or helped.
Prints a table per rank with anything outside the targets in red; writes a sheet for the user.

In game: a training dummy that shows DPS, `/ashbound build <preset>` for test builds, `/ashbound level`, and an optional
death / clear-time log per dungeon for friends' playtests.

## 5. Passes, in order

1. **Weapons vs monster health** (no tree): weapon damage/speed per type and rank; monster health per rank (dungeon mobs,
   elites, bosses, the 84 faction monsters, the 24 tower monsters, world weapons), solo and with party scaling.
2. **Monster damage vs armour**: every monster's attack damage per rank; armour classes (robe/light/medium/heavy) and their
   armour/toughness per rank; how many hits each class survives.
3. **Drops and economy**: world-arms and armour drop rates (cut once already 10/29), mats, coins, Ash per kill and the
   level curve (100 levels).
4. **Skill tree**: small nodes, then notables and keystones, against the budget and the simulator.
5. **Affixes and relics** on top.
6. **Final tuning** when content is complete: simulator over everything together + playtests for feel.

All numbers live in data files (gear.json, mob specs, the tree's file), so a change is a number and a reload.

## Tomorrow

1. Read every current number: weapon damage per rank, monster health/damage per rank, armour values. Dump them into one table.
2. Fill in the targets above with the user, the outside monsters' ranks (by place or distance), and the party scaling.
3. Build tools/balance.py and run pass 1 and 2; show the user the table (what's too strong / too weak).
4. Then the skill tree concept image (design agreed 10/29: 10 weapon areas + the player Core, ~100 points,
   tree unlocks Epic Fight skills - see memory ashbound-skill-tree).

## Pass 1-2 results (first run of tools/balance.py)

- **Boss big attacks one-shot every armour class at every rank** (0.5-1.4 hits; target 3-4). Biggest problem.
- **Player health is 20 for the whole game** while a normal monster's hit grows 4 -> 10 (F -> S) and armour only
  grows a little (gear scale 0.80 -> 1.25). By B, a robe or light wearer dies in 2-3 normal hits.
- **Heavy armour is fine against normal monsters** (8-11 hits); robe/light/medium are all too low.
- **Bosses die too fast solo:** 45-110 s against a 2-4 min target, and a party would melt them (no party scaling yet).
- **Elites are too tanky from C up:** 20-50 s against 10-15 s (their health grows faster than weapons do).
- **Black staff is broken:** 2-3 dps sustained. 100 mana = 8 bolts, then a 16 s refill.
- **Summoner is too strong from B up:** 4 thralls, 30-40 dps, double any melee weapon.
- **Bow is a bit low:** about 60% of a sword's dps.
- **Hits per normal monster are mostly fine.** Daggers are slightly high, and two-handers/hammers slightly low; their
  speed makes up for it.
- The 84 haunt monsters have no rank yet (normal hp 20-240).
- The model leaves out Epic Fight combos/skills, dodging, mob attack rate and affixes, so these are baseline numbers.

## Passes 1-2 done (10/29, in the code, untested in game)

Decided with the user: **health grows with level** (20 + 0.4 per level, ~60 at 100), **outside monsters ranked by
place** (faction -> rank in tools/balance.py HAUNT_RANK), **mana comes back while casting**.

- `python tools/balance.py --solve` writes `src/main/resources/ashbound/balance.json`; `python tools/balance.py` prints
  the check (every line on target now except weapon character: daggers ~5.5 hits, hammers/two-handers ~2-2.7).
- balance.json is read by `Balance.java`: health/damage multiplier per monster (GateMobs, SilkMobs, Cinderhusk), tower
  foreman health (TowerSites), armour per class and rank (Armors), and party scaling (+40% health per extra player near,
  bosses +5% damage, grows when a new player joins the fight).
- Solver targets (SOLVE in the tool): normal 4 sword hits, elite 12.5 s, boss 3 min solo; a medium-armour player takes
  9 normal hits, 6 elite hits, 3.5 boss big attacks. Robe 6, light 7.5, heavy ~12.5 normal hits.
- Code changes: black bolt 9 dmg, 8 mana, mana regen 10%/s while casting (16% idle); bow arrows x1.7 (was 1.35);
  thralls hit 3.3 x spell power each (not their mob's damage).
- Haunt ranks: Black Banner, Deep Delvers E; Barrow Host, Drowned Corsairs, Sporefolk D; Salt-Cursed, Thornborn,
  Rimebound, Blightkin, Broodmothers C; Sky Legion, Hollow Order B; Ash Legion A; Voidborn S.
- **Not done yet: the level system itself.** Until it exists every player has 20 hp, so from rank C up monsters hit
  harder than the solve assumes (C ~1.7x, S ~2.6x). Level + Ash curve is pass 3.
- Not modelled: one rank up ~= 2x harder (currently ~1.2-1.3x: gear ladder is gentle; tree + levels add the rest).

## Passes 3 and 5 done (10/29, compile, untested in game)

**Pass 3: levels, Ash, coins, materials** (`Levels.java`, `client/LevelHud.java`, tool `print_progress`)
- Level 1-100, cost 80 x L^1.55 Ash. Each level gives +0.4 health (a modifier, kept through death) and a tree point.
  **Until the tree screen exists, levels are bought automatically** as soon as the Ash is there.
- Every solved monster pays Ash and coins by its own health x its rank's rate (balance.json ash_per_hp / coins_per_hp).
  Everyone within 32 blocks gets the full amount. Rates are solved so each level band takes CLEARS dungeon clears:
  F 4, E 6, D 8, C 10, B 12, A 14, S 16 (~70 clears to level 90). A solo clear gives coins F 250 -> S 800.
- Materials (GateLoot): half of monsters drop 1 common, casters a 5% elite mat, the elite 3 commons + 1 elite mat,
  the boss per player 4-7 commons, 1-2 elite mats, the trophy. A full set takes ~2-2.5 clears (it was ~1).
- World-arms drops roll per player near the kill, and only that player can pick their drop up.
- HUD: "Lv N" + ember Ash bar left of the hotbar for 4 s after Ash comes in (or while TAB is held); a big
  "LEVEL N" moment on level up. Cheats: `/ashbound ash N`, `/ashbound level N`.

**Pass 5: affixes** (WorldArms.AFFIXES, tool `print_affixes`): each uncommon affix is worth 2-4%. Brutal 0.15-0.35,
Hale is now +2.5-4.5% of all health (not flat), Warded 0.3-0.6, Deep 2-4, Flowing 3-5%. Tier power 1.0/1.2/1.4/1.6,
so a legendary is about +22% on its weapon (was ~+50%). Utility affixes (Fleet, Steadfast, Tempered, Lucky) are low.

**One rank up is ~1.35x harder** (kills take longer x you die sooner), not the 2x in section 1. Steepening means a
steeper gear ladder (Gear.scale) and the solve follows. Ask the user.

**Pass 4 (tree), relics, pass 6:** wait for their content. The tree uses the power scale (small node ~1, notable
4-5, keystone ~15 minus its drawback) and gets a validator in balance.py when it's built. Relics follow the affix budget by rarity.
Pass 6 is the final run with everything plus playtests.
- Note: at high level vanilla draws 2-3 rows of hearts (52 hp at level 82). A custom health bar would fix it.

## Pass 6a: attack speed (10/29)

`tools/ef_timing.py` reads Epic Fight's jar (each combo animation's phases, BASIS_ATTACK_SPEED, ATTACK_SPEED_FACTOR,
length) into `tools/ef_timing.json`; Epic Fight plays a swing at `attack_speed / basis`, so a combo's real hits a second
are the sum of its recoveries over that. balance.py PASS 6 prints every kind's real DPS against the sword, flags single
items more than 12% off their kind (none: every weapon of a kind shares one speed), and Titan's Grip.

Findings: real hits/s sword 2.14 (vanilla model said 1.6), dagger 3.33 (2.4), spear 1.74 (1.2), greatsword moves 0.79
(0.85). Hammers were 0.54x a sword's DPS, two-handers 0.71x, daggers 1.14x; Titan's Grip 1.85x a single two-hander.

Changes:
- gear.py STATS at rank C: two-hander 14.5 -> 20, hammer 11 -> 18, dagger 5.5 -> 4.6 (world_arms.json damage recomputed
  in place). Now dagger 0.96x, spear 0.92x, hammer 0.89x (3 targets + most stagger), two-hander 0.98x (3 targets).
- Titan's Grip: dual-sword moves at a two-hander's speed (1.33 hits/s), each hit -25% (Passives.hurt, only with a
  two-hander in the off hand): 1.24x a sword, 1.26x one two-hander, +2 stamina/s. Two swords (no keystone) are 1.17x.
- solve() uses the real sword hits/s: elite and boss health x1.34 (normals unchanged, they're counted in hits).
- Ranged caught up: bow factor 1.7 -> 2.3, black bolt 9 -> 12, thrall hit 3.3 -> 4.3 (bow 0.78x, black 0.93x, summon
  ~0.9x melee; elites in 12-16 s).
- PASS 1's "hits per normal" for heavy weapons reads 1.5-2 (flagged low) but their time to kill matches the sword's.

## Self-tests (10/29)

`gradlew runGameTestServer` (headless, exits) runs `SelfTest.java`: 51 checks in 4 GameTests (template
`data/ashbound/structure/selftest.nbt`, an empty 8x4x8), each logged as `SELFTEST ok/FAIL`.
- treeRules: rank caps, joined-node rule, keystone needs 16 points, one keystone, refunds that would cut nodes off or
  drop a keystone below 16, points = level - 1 - ranks, full reset.
- mechanics (a FakePlayer hitting a 1000-health zombie): Execute 1.5x, Sunder 3rd hit 1.4x, Smite 1.3x, Titan lock 0,
  Titan dual 0.75x.
- balance: rank C damage/speed on the real items, 12 monsters' spawned health = base x balance.json.
- healthCap: max health past 1024.

Found and fixed by them: the mod crashed on a dedicated server (ClockHands loaded a client class; models moved to
ClockHands.Models), and max health was capped at 1024 by vanilla, so every boss over it (F bosses ~2000) had half its
health: Balance.raiseHealthCap() lifts the cap to 1,000,000 on both sides.

## Pass 6b: the 1.55 rank ladder, curios, boss weapons (10/29)

Balanced with everything built so far (fusion weapons not built yet: they get their own step when they exist).

- **Rank ladder**: weapon damage 1.24x a rank (gear.py / balance.py SCALE, Gear.scale): F 0.80, E 0.99, D 1.23, C 1.53,
  B 1.89, A 2.35, S 2.91. F is unchanged (a sword still 6). Stagger (gear.py IMPACT_SCALE) and armour toughness
  (balance.py ARMOUR_SCALE) keep the old gentle ladder: vanilla caps armour at 30 / 80%, so survival steps come from
  the solved monster damage. Monsters re-solved to the same targets. `ONE RANK UP` in the report: 1.52-1.58x at every
  step (kills x1.24, hits hurt x1.25). gear.json / world_arms.json damage recomputed in place.
- **Boss weapons** one rank above their dungeon (was two: +45-70% on the new ladder): +24% rank +8% boss = ~1.34x.
  Item check compares them at their own rank x1.08: 0 items off.
- **Brutal** (flat damage) grows with the weapon's rank (WorldArms.roll): worth 2.2% at every rank.
- **Curios** (balance.py CURIOS, CURIO_WORTH / CURIO_BUDGET): every curio's stats retuned to its rarity's band in
  real worth, not raw % (3% armour is worth ~1.5%): uncommon 3, rare 4.5, epic/legendary 6, relics 3 (their power is
  the effect). Utility counts part (luck 2, Ash 0.5, coins 0.3...). A full kit: uncommon +12%, rare +18%, epic/legendary
  +24% (about half a rank). 0 off budget.
- **Curio effects that used flat numbers**: Hive broodlings and Barrow Vex grow with the wearer's level band
  (CurioFx.power); Briar Heart heals 4% of max health a kill, the Wick's ward 3.5-6.5% a second; the Spore Heart's
  cloud rots (the blight, a share of the hit that set it off) instead of vanilla poison.
- SelfTest: rank C damage on the new ladder, each rank step 1.24x.

## By the book (research pass, 10/29) - supersedes pass 6b's 1.24 ladder

What published games and design writing say, and what changed here:

| Topic | Reference | Ours now |
|---|---|---|
| Normal enemy hits | 2-hit kills make combat mindless (Galdur devlog); soulslikes ~3-5 | 4 hits |
| Elite health | ~6x a normal (Galdur) | 5-6x |
| Boss solo length | planned 3-5 min, real fights run longer than HP math (movement); players tire past ~5 min (GW2 forum) | 3.5 min REAL (UPTIME: elites 70%, bosses 60% of the time spent hitting) |
| Hits to die | soulslikes: a few solid hits kill even in good armour (Dark Souls critiques) | medium 8 normal hits, boss big attack 3 (was 9 / 3.5) |
| Co-op scaling | Elden Ring: +60% boss health for one helper, +100-130% for two | +60% health per extra player (was 40%) |
| Per-tier step | Diablo 3 Torment: health ~1.6x, damage ~1.45x a level; WoW: ~1% stats per item level, +13 per difficulty | 1.55x harder a rank with the player's build |
| Gear power | WoW budget curve; items too strong cause power creep (Neverwinter) | curios to budget, a full kit ~half a rank |
| Curve shape | sawtooth: spike, then power payoff (flow) | new rank = spike, levels/tree/curios inside it = payoff |

**The big fix: monsters are solved against the rank's typical BUILD**, not a naked player (`build()` in balance.py): tree
points (level - 1) at ~0.65% offence / 0.45% defence each, a curio kit of the rank's rarity (partly filled early), a relic
from D, weapon affixes. Typical build: F +4%/+3% ... C +35%/+25% ... S +71%/+49% (damage/survival). Before this the late
game would have been far too easy (an S player ~1.7x stronger than the targets assumed).

Counting the build, levels and the tree already make each rank ~1.33x more dangerous to be hit by, so the weapon ladder
goes back to **1.08x a rank** (F 0.80 ... S 1.27; the 1.24 step double-counted). ONE RANK UP: 1.47-1.59x (avg ~1.55).
Boss weapons back to two ranks up (+26%). Brutal stays rank-scaled.

Flagged, kept on purpose: elites take daggers, bows and summoners 18-20 s from rank C (sword 15 s; armour cuts small
hits more). Robe a hair over on boss big attacks at S (2.7 hits).

Sources: Galdur devlog (itch.io), ARPG Balance (UCA paper), GW2 forum "how long is too long", Elden Ring co-op scaling
(Expert Beacon), Diablo 3 Torment table (BlizzardWatch), WoW item levels (wowutils), bugnet/abratabia on difficulty curves,
Game Developer "design lessons from Dark Souls".

## Pass 7: stamina and mana (10/31)

Before: swings cost no stamina at all (Epic Fight's basic attack has no resource), so only rolls and guards used the bar; a black
staff lost 3 mana a second, so a full bar lasted 33 s and mana never came up. `python tools/balance.py` prints PASS 7, with Epic
Fight's real regen run a tick at a time (`swing_duty`, `cast_rate`).

- **Stamina**: 15 at most, roll 4, step 3, all x (1 + armour weight / 40): rolls in a bar robe 3.6, light 3.4, medium 3.1, heavy 2.8.
- **Swings cost stamina** (Passives.swingCost, COMBO_ATTACK, x armour weight): dagger 0.4, sword 0.6, spear 0.7, hammer and two-hander
  1.6, staff bash 1.2; about 1.25 a second whatever the weapon, a bar is ~12 s of nonstop swinging. Fists and tools are free. A bow shot
  costs 1.2. COMBAT_REFERENCE's rule: any stamina above 0 starts a swing, at 0 it doesn't ("Out of breath").
- Weapons from other mods (Weapons of Miracles) pay by how Epic Fight holds them. Every weapon's tooltip shows its cost.
- **Regen** base 1.25 (Epic Fight 1): waits 1.2 s after an action instead of 1.5 s, refills 25% faster. Without it melee could swing only
  ~45% of a fight, well under the 60% bosses are solved for.
- **Titan's Grip** +0.5 a swing (was +1.5 when swings were free), two two-handers cost 1.4 in all, as they swing faster.
- **Guard is unchanged**: Epic Fight stacks it, (0.6 x blocks in a row) x the hit's impact, so a chain of blocks breaks the guard.
- **Mana**: regen 6% a second casting, 14% idle (was 10 / 16). Black 16 (was 13), white 38, summon 60 (was 45). A black bar is 10 s of
  nonstop bolts, then 0.5 casts a second; with pauses 0.55. White lasts 15 s of nonstop heals, then a heal every 3.6 s. Summoners are
  never short: their cooldown is the limit. Casts cost no stamina.
- BOLT_LANDS 0.8: a bolt is a slow projectile, and black's damage in PASS 1 now counts misses (~0.9x a sword).

Result, sword in medium armour: stamina allows 52% of a fight at F, 59% at C, 64% at S. Solved uptime for bosses is 60%, so low ranks run a
little long: solo boss 240 s at F, 210 s from B, inside the 150-270 target. Monster numbers unchanged, no re-solve.
Not measured: the real impact of our monsters' hits, so how many blocks a guard takes is untested.


## Skills, Forms and staffs (10/31)

Basic melee is about 1.3 x weapon damage a second. A skill adds (multiplier / cooldown) of weapon damage a second per target hit:

| Skill | Hit x | Cooldown | Per second, rank I | Rank V | Shape |
|---|---|---|---|---|---|
| Bastion Slam | 1.2 | 14 | .09 | .15 | ring, aggro, resistance |
| Oath Charge | 1.8 | 12 | .15 | .27 | line, heals 8% |
| Rift Slam | 2.2 | 16 | .14 | .25 | wide ring, throws |
| Headsman's Drop | 5 | 20 | .25 | .45 | single, slow |
| Blood Price | 3 | 12 | .25 | .45 | ring, costs 1/7 health |
| Steel Tempest | 3.9 | 15 | .26 | .47 | small ring |
| Skyfall | 2.5 | 14 | .18 | .32 | ring on landing |
| Spear Wall | 2.6 | 12 | .22 | .39 | long line |
| Vanish | 3.2 | 16 | .20 | .36 | single, teleports |
| Viper Bite | 1.2 | 10 | .12 | .22 | cone + poison |
| Snare Field | .8 | 14 | .06 | .11 | pins the group |

So a skill is 5-20% more damage at rank I and 8-36% at rank V, on top of its effect; rank V is the book chase, not the baseline. The single-target
ones top the list because they can't hit a crowd. Hunter's Deadeye is 6 x an arrow. Mage skills are in bolts, 20 x power each: Cinder Field 7 pulses of .6 over 14s, Black Hole 3 over 18s, Judgement 2.5 over 16s.

Staffs: anyone not of the staff's class gets .85 of it; its class gets .85 x (1.10 + .03 per rank, +.10 boss). That's 1.0 at a rank C normal staff, what the solved balance assumed, .9 at rank F and 1.15 at a rank S boss staff.
The first key on a staff: Braided Bolts 3 x 1.4 bolts over 15s (twice the mana), Great Heal 20% over 30s, Greater Host 4 thralls over 45s.

Summons: horde is 4 at 1.2 x per rank step, Bound Champion 1 at 2.2 x, more health, and it cleaves round what it hits.

Forms (damage dealt / taken, seconds, rest): drake 2.2/2, 20, 120; hammerfall 1.4/1.2, 15, 90; communion 1.3-2.5/1.3, 18, 100; tyrant 1.6/1 (2.5 on the ground), 18, 90; noone 3/any hit leaves 1 health, 12, 80; stag 2/1.5, 15, 80;
offering 2/1.3, 15, 90; crown 1/.7, 20, 120. Over a whole fight that's +15-25% damage for one key lost for good, so the price is real and the risk is what you're buying. **None of this has been played.** Expect to move these once it has.


## The later skills (10/31)

Each path has three skills, at levels 5, 20 and 35. Key numbers, rank I (each rank +20%):

| Skill | Hit x | Cooldown | Shape |
|---|---|---|---|
| Crossing Oath | 1.1 x 2 | 10 | line, heals 3% each |
| Last Oath | 4-8 | 30 | long line, more the lower your health |
| Fault Line | .8 x up to 2 per target | 14 | six rings walking forward |
| Worldbreaker | 2 x 3 | 40 | rings 5, 7, 9.5 |
| Beheading | 6, 14 under 25% | 30 | single |
| Crimson Rite | 6 | 40 | costs half your health, ring 8 |
| Razor Gale | .7 | 13 | seven rings walking forward |
| Eye of the Storm | .7 x 10 | 40 | pulls in |
| Dragon's Descent | 4.5 | 36 | ring 7 where you aim |
| Thousand Thrusts | .55 x 8 | 28 | line |
| Death Blossom | 2.2, up to 5 targets | 30 | teleports |
| Plague Bloom | 2.4 | 30 | only on the poisoned |
| Piercing Star | 2 x 4.5 x bow x 2 | 32 | line 40 |

Reaper's Mark and Killing Ground: everyone hits a third harder. Red Thirst: 15% back. Mage skills, in bolts: Flame Lance 1.6/10s, Meteor 6/30s, Void Lances 1.6/12s, Event Horizon .9 x 6 + 2/32s, Holy Lance 1.8/10s, Heaven's Wrath .7 x 8/36s, Marrow Burst 1 per thrall/16s. Sanctify 3% a second for 8s, Second Dawn full heal + 80% less damage for 3s, once in 90s. **None of this has been played.**


## Pass 8: skills and the 15% party (10/31 evening)

Supersedes the numbers in "The later skills" and "Skills, Forms and staffs" where they differ, and the skill levels: now 5, 20, 35, one of two at each.
`python tools/balance.py` prints PASS 8 (all 54, as a share of the class's own damage, mana skills net of the bolts that mana would have bought) and PARTY.

**Party** (balance.json `party`, `tools/balance.py` PARTY): +15% health a player (was +60%), boss damage still +5%. Ash and coins a head are 1 / (1 + 0.25 (n - 1)), because at 15% a party of four clears 2.75x as fast and would otherwise level 2.75x as fast. Result: boss 210 s alone, 121 s for 2, 76 s for 4, 54 s for 8; levels 1.4-1.6x solo.

**Bugs found:**
- Skill multipliers were of the raw weapon hit, so a hammer's were ~4x a dagger's. Now JoinedSkills.strength = hit x attack speed / 1.6.
- With a bow in hand strength was the bare hand (~1), so Snare Field and Spike Pit did nothing. Now 3.3 x bowPower, about a sword blow.
- Vanilla poison is flat, so the Venom path did nothing past rank E. Viper Bite adds SkillArts.venom, .2 x strength a second for 6 s.
- Death Blossom hit a lone boss once. Now five cuts round whoever's there, 1.3 each.
- Deadeye was really ~9 arrows; the speed multiplies base damage. Now x2 at speed 4.5, 3 arrows, 16 s. Piercing Star was only 3 arrows, now 6.75.
- Legion cost 120 and Second Dawn 100 on a 100 bar. Now 95 and 90. Killing Ground's duration ignored rank.
- Flame Lance and Void Lances cost more than the bolts they replaced on one target: 16 mana now.

**Number changes, rank I:** Bastion 1.4, Rift 2.6, Fault Line 1.1 a ring, Razor Gale 1.0, Spear Hedge 1.1, Unbroken 5, Worldbreaker 2.6 x 3 / 36 s, Crimson Rite 9, Eye of the Storm .9 x 10 / 36 s, Dragon's Descent 7 / 32 s, Thousand Thrusts .75 x 8, Toxic Cloud .35 x 6, Plague Bloom 6, Snare 1.2, Cinder Field .45 x 7, Killing Ground 10 s / 34 s.

**Monsters re-solved with skills counted.** A rank's typical player adds this much to a long fight: F, E +12%, D +26%, C +41%, B, A +47%, S +54% (one skill for each level reached, used 70% of the time, books on the way up). Elite and boss health rise by exactly that; normal monsters and all monster damage are unchanged.

Flagged, kept on purpose: Bastion Slam, Unbroken and Snare Field are low in damage because their worth is taunt, damage reduction and pinning. Holy Lance and Judgement read high because they're a Mender's only damage. PASS 1's "hits per normal" flags are weapon character, as before. None of this has been played.

Hit-stop costs no damage: a held swing's ticks are played double straight after (HitStop, AnimationPlayerMixin).

## Pass 9: the difficulty curve and camps (10/31, 23/23 headless, unplayed)

The user: a camp "disintegrated" a party; wants a little easy at first, epic late. Party health was not the cause: it
never touched normal monsters' damage. The causes were in the camps, and every rank was solved to the same flat targets.

- **CURVE in tools/balance.py replaces the flat SOLVE.** Medium armour survives 13 normal hits at F down to 6 at S; a
  normal takes 3 sword hits at F, 5 at S; an elite 9 s to 20 s; a solo boss 110 s to 330 s; boss big attacks 5 to 2.4.
  The class hit targets move with it. Armour never drops from one rank to the next.
- **Camps (Haunts.java):** at most 8 alive at once (was 14), the total stays, they arrive in waves. A place fills at one
  speed however many players walk in, one monster per 3 s (was one per 2 s per player).
- **A place outside a gate is at most one rank above the best player within 64 blocks** (Balance.soften). Before, a
  rank S void monster hit a level 5 player for 22.7 raw, more than their whole health bar; now 4.6. It pays Ash and
  coins at the lowered rank. It still drops its own loot.
- **Crowds (Balance.crowded):** the first blow in a second is in full, blows from other monsters inside that second do
  40% at F, 45, 55, 65, 75, 85, 100% at S. Bosses always hit in full. A boss's hit doesn't start the window.
- balance.json gains rank_normal, band_top and crowd. Dungeons are the same length in Ash: progress() re-solves Ash per
  health.
