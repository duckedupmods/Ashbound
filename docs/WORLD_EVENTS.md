# World events (outside the gates)

All roll per party of players (`Party.fightKey`), never per player or per world, and scale to how many are together.
Nothing of a scene is kept across a restart: whatever's left when the world loads is cleared.
Adventurer parties (meetings, talk, requests) are in ADVENTURERS.md.

## Wild encounters (`Encounters.java`, built 11/4, 49/49 headless, unseen in game)
First after ~5 min out, then every 10-15 min; 40-70 blocks off, out of sight, never in town or deep underground.
One live per party. Test with `/ashbound encounter <caravan|deserters|hunter|duelist|fallen>` (20 blocks ahead).
- **Caravan under attack** (25%): Hob's wagon model, a peddler (Npc, sells their wares), a hired party one rank under
  yours as guards, gate monsters of your rank on them. "Steel on steel" on the action bar within 80. All attackers dead
  with a player within 48: the trader pays (x1.0, GP, half the time a find) and keeps selling for 2 min.
- **Deserters** (20%): the Brigand's Gorge mobs (lieutenant + 2-5 footpads/knife dancers/hexers, the ogre at C+ or 4+
  players) brought to your party's rank (`Balance.atRank`). They hold within 6 of their spot and won't target you while
  talking terms. Right-click the lieutenant: pay the toll (~0.8x pay), talk them down (30% + 10% per player near, +10%
  per rank you're above), or draw steel. Hit one and it's a fight. All dead: their purse (x1.2).
- **Wounded hunter** (15%, only with a town within 700): an adventurer at 30% health who can't mend. Talk: "I'll get you
  there" and they follow you (Escort goal); every 30-45 s a wave of 2-3 monsters from behind, out of sight (4 at most).
  Into a town: x1.5 and thanks; they die: "The hunter didn't make it."
- **Wandering duelist** (20%): an adventurer one rank above you, melee role. Accept: one bout, only you and them can hurt
  each other (`Encounters.duel` in `Adventurers.hurt`); whoever would drop under 15% health yields instead (no death).
  You win: their weapon + coins. You lose: "Train, and find me again."
- **Fallen party** (20%): see below.
- Lines: `caravan_*`, `deserter_*`, `hunter_*`, `duel_*`, `fallen_*`, `stash_*`, `diary_*` in adventurer_lines.json.

## Fallen adventurers + treasure maps (`Encounters.Fallen`, `Treasure.java`, built 11/5, unseen in game)
- **The camp**: 2-4 of an adventurer party near your rank, dead round our Cold Campfire (`dead_campfire`, smoke particles
  only, nothing burns) with a Bandit Tent. They're real `Adventurer`s, dressed as usual, then `fallDown(pose)`: no AI,
  invulnerable, never a target (`canBeSeenAsEnemy`), a 1.4 x 0.5 box, and lying in one of three poses of ours
  (tools/fallen_pose.py -> animmodels/animations/biped/fallen_back/front/side.json, played by AdventurerPatch under
  SLEEP/ADMIRE/SPECTATE). 3 in 4 times 2-5 of the rank's gate monsters are still about (held within 14).
- **Searching** (right-click a body): refused while one of the killers is within 24. Each body once: ~0.3x pay in coins,
  35% one thing they wore or held (it comes off the body), and the one who had it: the **torn map**.
- **The map**: a vanilla filled map (scale 2) centred on an X 300-800 blocks off (never sea, river, beach or town, by the
  world's biome recipe since the land isn't there yet), red X marker, name "Torn Map of the ...", a scrawl in its lore,
  the stash id in custom data. Carrying it puts "The ...' Stash" in the Journal and follows it on the compass
  (an Errand with giver `@treasure:<id>`, never expires; `Errands.drop` takes it off everyone when it's dug up).
- **The spot** is made only when someone carrying the map comes within 56: dry ground near the X, turned earth (coarse
  dirt) over it, a chest two blocks down, a dead wildwood tree 3 off with our Procession Banner at its foot and a Skull
  Stake by the X. Saved in `ashbound_stashes` (world saved data), so maps work across sessions.
- **The bane**: breaking any block within 7 of the X (or touching the chest) wakes it: the killers' dungeon's elite,
  at your rank, x2.5 health (+0.5 per extra player near) and +25% damage, named "<Elite>, Bane of the <party>", with a
  pack of 2-6 of the dungeon's monsters. The chest won't give while the bane lives within 40.
- **The chest**: right-click (or break) it once the bane's down: it's gone, and whoever opened it, their party, and anyone
  who hit the bane (`Stash.hitters`, saved), all within 250, get x2 pay + GP and their own share (nobody else does), showering
  from 8 over their head, spread about, no pickup for 2.5 s so it's seen falling (`Dropped.rain`, also the storm's;
  marked with their name and colour): 2-3 finds,
  the dungeon's mats (3-5, 70% 1-3 of the second, 30% the third), 40% a world weapon, 15% one of the dungeon's weapons,
  and the party's **Last Pages** (a written book: setting out, the stash, the end, naming the bane).
- Test: `/ashbound encounter fallen`, `/ashbound treasure` (a map to a stash 60-100 off). Headless: `SelfTest.fallenTreasure`.

## Gate storms (`SkyCracks.java`, `SkyCrack`, `StormSpire`, `StormStrike`, client `StormSky`, built 11/4, 50/50 headless, unseen in game)
Replaces the sky cracks + falling shards (rejected in game: "looks like a png"). Concept approved 11/4:
tools/blender/gate_storm.py -> tools/renders/gate/storm_A_wide/crater/far.png. **No fire anywhere** (forest lag).
- First 20-30 min out, then every 40-60 min. 70-115 blocks ahead of a player who can see the sky, outside towns.
  "A gate storm rolls in, to the north!" within 400. `/ashbound storm [rank 0-6]`, `/ashbound storm win` (beats the nearest one now: spires and monsters gone, loot given; old `/ashbound skycrack` still works).
- **Eye** (remade 11/4 after "still looks like a png"; concept tools/blender/gate_storm_eye.py -> storm_eye_A_*.png):
  the gate (`SkyCrack`, SCALE 4.5) 64 up, face-down, dungeon hall through it (GateWindow), at the top of a **funnel** of
  cloud climbing from the deck (`SkyCrack.DECK` 20 under it): solid back wall + lid (entitySolid, red toward the tear),
  three streaked walls (textures/entity/storm_funnel.png from tools/storm_funnel_tex.py) turning faster further in,
  streaks climbing, fraying out at the foot; two red wisp discs turning in the tear's mouth (parallax over the hall);
  lightning crawling down the funnel wall every ~1 s.
- **Clouds** (`StormSky.clouds`): tools/blender/storm_clouds.py bakes the deck looking up (textures/entity/storm_clouds.png,
  RGBA); three rings 175/150/120 across at DECK-6..DECK+2 under the eye, from the funnel's foot out, each turning at its
  own speed; spread out as it rolls in (240 ticks), brightened by lightning flashes.
- **Weather** (client only): under it (120 flat, nothing past 230) the client's rain and thunder go up (put back after),
  fog drawn in to 180 and tinted dark grey-red, flashes tint the fog and the screen.
- **Strikes** (`StormStrike`): every 30 s (faster each time, 17 s at least) 1-3 near players (5-15 blocks off, never on
  them): a ground ring charges 30 ticks, then the bolt (rank colour, white core, forks), 4 + 3 x rank to whatever is
  within 3, a GateScorch patch radius 2.6, and 12 ticks later 2-3 of the eye's dungeon's own monsters climb out (at most
  8 + 2 x players out). Harmless far strikes every 3-7 s under the storm for the look and the thunder.
- **Storm spires** (`StormSpire`, client `StormSpireRenderer`): 3 + (players - 1, up to 3) burst up 16-32 blocks round the
  eye after it opens (rise 40 ticks), 14-23 tall, built from the dungeon's own blocks (GateDungeons debris), torn chunks
  and a white-hot core on top that the storm feeds lightning. Struck at the foot (hitbox 3.2 x 6), 40 x (rank+1) x
  sqrt(players) each, red flash when hit.
- **Closing it**: all spires down -> the eye falters, strikes at the party stop, "Finish the N still out" (monsters that
  died, unloaded or strayed 200+ from the eye don't count). The last one dead -> it collapses: everyone within 250 gets
  3x pay + 3x GP, and a harmless strike lands 3 blocks beside each of them and **their own loot** falls from 4 over their head (lands where it lands, on
  trees too; ItemEntity owned by them, marked like thrown gear: glow, light thread, their name in their colour): a find (half the time two), 2-4 of the dungeon's first mat, 50% 1-2 of
  its second, 12% its third, 6% one of its (non-boss) weapons (`SkyCracks.loot`).
- Left alone 30 min, or **nobody within 500 for 2.5 min** (EMPTY 3000 ticks): it blows itself out, what came out stays.
- Quest compass ignores it (`GateEntity.sky()`).

## Meteor falls (`Meteors.java`, `MeteorShard`, client `MeteorRenderer` + `MeteorFx`, built 11/6, 54/54 headless, unseen in game)
Concept: tools/blender/meteor_fall.py -> tools/renders/meteor/meteor_fall.png, meteor_crater.png. Assets: tools/meteor_assets.py.
- When a gate breaks, pieces of its crystal ring fall. Per party: first 30-45 min out, then every 40-80 min (not while
  its storm is live). Lands 70-130 ahead on dry natural ground outside towns; `fits()` refuses water, slopes > 12, any
  non-natural block or block entity within 2.4 x radius (never on builds).
- Falls 150 ticks from 150-200 out and 170-210 up (the entity already stands where it lands; the client draws the head
  along `from`): fireball glows + streak (GateRenderer.Glow), flame/smoke/signal-smoke/ember particles always visible.
  "A gate-shard falls from the sky, to the X!" within 600.
- Hits: crater radius 8 + rank/2 (bowl, `glassed_ground` middle (light 7, emissive cracks), `scorched_earth` to a raised
  rim, burnt ring out to 2.4R: leaves gone, logs -> `charred_log`, plants gone, thrown rock). Blast throws/singes players.
  Smoke column (signal smoke) while it stands.
- Wakes when a non-creative player comes within 22 (or hits it): its gate's monsters every 20 s (cap 6 + 2/player).
  3 veins, 55 x (rank+1) x sqrt(players) each; each break: a small crystal goes, heat pulse 30 ticks later (radius 7,
  4 + 3 x rank, sets alight). Last vein: bursts, 2x pay + GP, Dropped.rain loot (find, Shardglass 2-4, gate mats,
  6% weapon) to everyone within 64.
- Nobody comes for 20 min -> goes dark; awake but left 2.5 min -> goes dark (monsters stay). Crater stays.
- Shardglass: glassed ground drops it 35% (else scorched earth); 4 -> Temper Ember.
- Test: `/ashbound meteor [rank 0-6]`, `/ashbound meteor win`. Headless: `SelfTest.meteorFall`.

## Later (agreed, not built)
Gate-shard meteor, ashfall night; legend hunts; village festivals; capital arena.
