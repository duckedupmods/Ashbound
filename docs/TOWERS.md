# Towers

Our own take on the Battle Towers idea: a tall tower you clear floor by floor, with a boss on the roof. Each tower
kind has its own monsters, its own boss and its own gear, and appears only in its own biomes. The first one is the
Clockwork Spire.

## The Clockwork Spire

A gearwright's order built a tower to wind the world's clock. The order is gone, but the tower still runs. Its
automatons keep building more of themselves, and the thing at the top has wound itself into a god.

**Where:** plains, savanna, meadows and windswept hills. It's rare, about one per 1500 x 1500 blocks, and never near
the capital or a settlement.

**Look:** about 100 blocks tall and octagonal.
- A stepped stone base, 31 blocks across.
- The shaft is built from blackened iron panels with brass bands and rivets.
- A great clock face on each of its four sides, with hands that really turn.
- Huge half-buried gears turn in the walls.
- Copper steam pipes climb the outside and vent steam.
- A brass crown of spikes, and a lightning mast that sparks in storms.
- No vanilla blocks show: everything is our own.

**Inside:** eight floors joined by a stair that winds around a great drive shaft, which runs from the boiler to the
roof and turns the whole time.

| Floor | Room | What's in it |
|---|---|---|
| 1 | Boiler Hall | furnaces, a huge boiler, the entrance; Coglings and Brass Sentries |
| 2 | Foundry | casting pits with molten brass, moulds; Steam Hulks |
| 3 | Assembly Line | half-built automatons on racks (some wake up); a mixed fight |
| 4 | Blueprint Archive | shelves, drafting tables, a balcony; Tinker Adepts |
| 5 | Gear Hall | giant turning gears to fight on; Coglings swarm |
| 6 | Clock Chamber | behind the four clock faces, light through the glass; the elite (the Clockwork Duelist) |
| 7 | Pendulum Hall | a giant swinging pendulum to dodge; Sentries and Hulks |
| 8 | The Crown (roof) | an open gear arena under the sky; the boss |

**The climb:**
- Every floor's stair is sealed by a brass gate.
- Killing the floor's foreman (a stronger, glowing monster with a bar, like a dungeon elite) drops a Cog Key that opens
  the next gate.
- Chests sit on every floor; the best ones are behind the boss.
- Monsters respawn after a while (a world-day), so the tower can be cleared again.
- The boss and the roof chest refill once a week (configurable).

## The Gearbound (monsters)

| Monster | Role | Look | Moves |
|---|---|---|---|
| Cogling | swarm, small | a spider-legged automaton the size of a dog, one red lens, saw-tooth mandibles | crawler: pounce, spin |
| Brass Sentry | guard | a tall brass knight automaton, a halberd and a tower shield, a slit visor glowing orange | spear + shield: charge, pull |
| Steam Hulk | brute | huge, a boiler for a chest, piston arms with hammer fists, steam leaking from its joints | fist: slam, charge, a steam cloud |
| Tinker Adept | caster | a human cult engineer in a leather apron and goggles, with a mechanical arm and a spark staff | caster: bolt, lightning, heals constructs, summons Coglings |
| Clockwork Duelist | elite | slender and fast, four arms, two sabres and two daggers, a turning clock-face mask | dual: dash, blink, spin |
| **The Grand Horologe** (boss) | boss | a colossal clockwork titan with a clock face for a head and an open chest showing a glowing mainspring; one arm is a hammer, the other a pendulum blade | see below |

**The Grand Horologe's phases:**
1. **Wound** (100-66%): hammer slams, the pendulum blade sweeps the arena, charges.
2. **Unwound** (66-33%): its chest opens, it breathes steam, Coglings pour out of its back, and gears rain from above.
3. **Overclocked** (33-0%): it glows white hot, lightning strikes from the mast, it spins, and it leaps between the
   gear platforms.

## Gear

The tower gets the same kit as a dungeon:
- **Materials:** Brass Cog (common), Mainspring (from the elites), Horologe Heart (from the boss).
- **Weapons:** all 10 weapon types, plus the boss's own drops.
  - Cogblade (sword)
  - Escapement Dagger (dagger)
  - Piston Maul (hammer)
  - Governor Pike (spear)
  - Gearbreaker (two-hander)
  - Riveted Bulwark (shield)
  - Spring Repeater (bow)
  - Arc Rod (black staff)
  - Tuning Fork (white staff)
  - Tinker's Crank (summon staff)
- **Armour sets:**
  - Gearwright plate (heavy)
  - Tinker's leathers (light)
  - Horologist's coat (robe)
  - Brasswork mail (medium)

## Status (10/28, built, untested in game)

- Blocks, the tower in blocks, inside floors and stairs (walk check passes from door to roof): tools/towers/clockwork_spire.py.
- In the world: Trees.GiantTree places data/ashbound/structure/tower/clockwork_spire.nbt; TowerSites.java stocks it when a
  player walks in (monsters, glowing foremen with doubled health, brass gates at each stair top, the boss on the roof),
  opens a gate when its foreman dies, restocks a day later once nothing is left, refills empty coffers.
- Monsters: tools/mobs/clockwork_spire.py (hand-built), moves in tools/mob_moves.py; the boss has the usual 3 phases.
- Gear: gear.py entry (rank C), weapons via weapon_themes_v2.py ClockworkSpire, armour via armorforge, mats; 3D slot icons.
- Not yet: turning clock hands and gears, steam, the boss's own animations (it uses the maul stance and skills).

## Build order

1. Blocks: iron panels, brass bands, rivets, gears, pipes, clock glass.
2. The tower in blocks, with renders for approval.
3. Placing it in the world, sealed floors, chests, respawn.
4. The monsters, built by hand like the dungeon ones, compared side by side.
5. The boss and its phases.
6. Gear: weapons, armour, materials.
7. More tower kinds later (frozen, desert, sky): see LATER.md.

## The Serpent Ziggurat (jungle, swamp)

A stepped temple-pyramid swallowed by the jungle, where a cult of serpent-folk still feeds its god. Seven terraces of
mossy green-grey limestone with jade inlay and gold friezes, roots and vines pouring over the steps, waterfalls from
the upper terraces into pools at the foot, jade-green braziers. A grand stair climbs the front to the first terrace's
door; above that it lies broken under the jungle, so the climb is inside, terrace by terrace. The summit is a broad
altar court, the boss's arena, with a serpent-head shrine rising behind it.

**Where:** jungle, sparse jungle, bamboo jungle, swamp, mangrove swamp.

| Floor | Room | What's in it |
|---|---|---|
| 1 | Hall of Offerings | the entrance, pools and braziers, Scaleguards |
| 2 | The Serpent Pit | a sunken pit seething with Coilspawn |
| 3 | Barracks of the Coil | weapon racks, Scaleguards and a Jaguar Stalker |
| 4 | The Jaguar Garden | trees grown through the floor, light shafts; Jaguar Stalkers |
| 5 | Venom Sanctum | green pools, Venom Priests |
| 6 | Hall of the Champion | the elite, the Feathered Champion |
| 7 | The Summit Altar | the boss |

**The Coil (monsters):**
| Monster | Role | Look | Moves |
|---|---|---|---|
| Coilspawn | swarm | a jade-plated jungle centipede the length of a horse, venom mandibles | crawler: pounce, cloud |
| Scaleguard | guard | a lizard warrior in jade and gold, an obsidian-edged war club, a feathered shield | sword + shield: charge, slam |
| Jaguar Stalker | skirmisher | a warrior in a jaguar skin and mask, twin claw-blades | twin daggers: pounce, blink, dash |
| Venom Priest | caster | a serpent-crowned priest with a fang staff, robes of green and gold | caster: bolt, cloud, heal, summons Coilspawn |
| Feathered Champion | elite | a towering serpent-knight with a great crest of feathers and a two-handed obsidian blade | greatsword: leap, spin, charge |
| **The Coiled King** (boss) | boss | a colossal naga: a serpent body coiled under a scaled, gold-armoured torso, a cobra hood crowned in jade, a glaive and a sun-disc shield | phases: venom, summoning, then a sun-fire beam |


## Four more towers (10/28)

Each covers biomes the Spire skips and has a silhouette of its own: the Spire is an octagonal iron shaft, the
Ziggurat a stepped pyramid, the Keep a squat giant-scale drum, the Minaret a slender needle under a dome, the Fang a
crooked war-tower of rock and timber. Same runtime: floors stocked on approach, a glowing foreman per floor, an open
climb, the boss asleep on the roof, its hoard rising when it dies (world weapons, enough drops for armour).

### Rimeholt, the Giant's Keep (snowy plains, snowy taiga, groves, snowy slopes, frozen and jagged peaks, ice spikes)

A frost giant's watch-keep: a round drum of blue-black granite 40 across with doors and stairs built for giants,
leaning buttresses like ribs, a crown of pale ice battlements, icicles hanging off every course, rune-carved bands
glowing cold blue, a great horn on the roof. Inside, giant halls: a mead hall with a long table, a forge with an ice
anvil, a kennel, a throne under the roof.

| Monster | Role | Look |
|---|---|---|
| Rime Thrall | swarm | a dead raider frozen solid, frost-cracked skin, a rusted axe, ice in its beard |
| Frost Troll | brute | hunched, white fur and blue hide, icicle tusks, a boulder of ice for a club |
| Huskarl | guard | a giant's man-at-arms in scale and fur, a round shield and a bearded axe, a horned helm |
| Rune Seer | caster | a blind crone in furs, runes glowing in her skin, a staff of whalebone |
| Winter Wolf | skirmisher (elite) | a wolf the size of a horse, ice spines down its back, breath that freezes |
| **Jarl Hrimgar** (boss) | boss | a frost giant king: an ice crown, a beard of icicles, a cloak of white bear, a greataxe of blue ice |

### The Glass Minaret (desert)

A djinn's tower: a slender minaret 100 tall of sun-bleached sandstone banded in turquoise tile, brass balconies on
every stage, pierced screens throwing star-shaped light, an onion dome of brass and glass at the top with burning
sun-mirrors round it. Inside: a bazaar of brass lamps, a mirror hall, a library of scrolls, a sand-clock room, a
garden of glass flowers, the sultan's court under the dome.

| Monster | Role | Look |
|---|---|---|
| Dune Scorpion | swarm | a sand-coloured scorpion the size of a dog, a glowing amber sting |
| Glass Golem | brute | a hulking body of fused desert glass with a sun burning in its chest |
| Sandwraith | caster | a robed thing of whirling sand, a brass mask, a censer that pours sand |
| Mirror Guard | guard | a turbaned guard in brass scale with a scimitar and a mirror-shield |
| Blade Dancer | elite | veiled, silks and bells, four curved blades |
| **The Djinn Sultan** (boss) | boss | a giant of blue smoke from the waist up, four arms, a turban with a burning jewel, two scimitars and a lamp |

### The Warlord's Fang (badlands, wooded badlands, eroded badlands, dark forest)

An orc war-tower raised on a crag of red rock: crooked stone courses, timber hoardings and fighting platforms jutting
off every stage, iron spikes, skull racks, war banners, a war drum on the roof and a great fanged gate. Inside: a
mess hall, pens, a smithy, a shaman's den, the trophy hall, the warlord's roof.

| Monster | Role | Look |
|---|---|---|
| Goblin Cutthroat | swarm | small, sharp, a hooked knife and a stolen helmet too big for it |
| Orc Brute | brute | a slab of green muscle in scrap plate, a spiked club |
| Orc Raider | guard | an orc in hide and iron with a cleaver and a bone shield |
| Goblin Shaman | caster | a hunched goblin in feathers and bones, a skull rattle, green fire |
| Warg Rider | elite | a goblin on a huge black warg, a spear |
| **Gorrak the Warlord** (boss) | boss | a giant orc in a horned iron helm and trophy-hung plate, a war banner on his back, a two-handed cleaver |
