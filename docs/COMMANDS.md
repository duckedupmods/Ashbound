# Test commands (operators only)

## Survive
- `/ashbound tank` - netherite armour (Prot IV), Resistance III, Fire Res, Regen II, Saturation
- `/ashbound tank off` - effects off (armour stays)
- `/ashbound oneshot` - Bossbane (test): a netherite sword that kills anything, bosses too, in one hit

## See the magic
- `/ashbound spell <gate>` - throw that dungeon's bolt (tab completes all 30), no staff or mana needed, no damage
- `/ashbound spell heal|radiance|summon|host|overload|great_heal|braid` - the rest of the mage's effects

## Go into a dungeon
- `/ashbound lair gate_<gate>` - walk straight into a dungeon (tab completes all 25)
- `/ashbound lair gate_<gate> rebuild` - same, rebuilt fresh (respawns mobs, closes seals)
- `/ashbound gate F|E|D|C|B|A|S` - tear open a gate of that rank in front of you (picks one of the rank's dungeons)
- `/ashbound gate close` - close the nearest gate

New dungeons: gate_weeping_mine, gate_tide_chapel, gate_brigands_gorge (E); gate_rookery, gate_hollow_circus,
gate_mirefen_coven (D); gate_sandsunk_tomb (C); gate_fallen_titan, gate_jade_monastery (B); gate_storm_bastion,
gate_bloodmoon_court, gate_obsidian_labyrinth (A); gate_abyssal_lighthouse, gate_eclipse_cathedral, gate_wyrms_hoard (S).
Old ones: gate_cellar, gate_gallows, gate_rotwood, gate_crypt, gate_plague, gate_temple, gate_ossuary, gate_foundry,
gate_frost, gate_silk.

## Gear
- `/ashbound set <set>` - wear a whole armour set (your old armour goes to your bag)
- `/ashbound gear <gate>` - that dungeon's 16 weapons (10 forged + 6 boss) and a stack of each of its 3 drops

| Dungeon | Sets |
|---|---|
| cellar | vintner corkrunner cooper bilgewader |
| gallows | tarwitch gibbet headsman gallowsguard |
| rotwood | rotwarden stagrunner barkwight heartwood |
| crypt | abbot mourner gravewarden coffinplate |
| plague | beakmask orderly friar quarantine |
| temple | acolyte faceless sentinel sovereign |
| ossuary | cantor stitchhide bonewright pallbearer |
| foundry | bellows slagrunner riveter kilnplate |
| frost | snowshroud hoarstep marcher rimeguard |
| silk | archivist silkrunner lector bindplate |
| weeping_mine | lampwright tunnelrat shaftman deepdelver |
| tide_chapel | tidepriest netrunner wrackmail brineclad |
| brigands_gorge | hexer outlaw highwayman gorgeguard |
| rookery | augur featherblade ravenmantle rookplate |
| hollow_circus | fireeater motley ringhand ringiron |
| mirefen_coven | hexweave bogrunner fenwarden trollhide |
| sandsunk_tomb | linenwrap jackalrunner sunscale tombguard |
| fallen_titan | bilepriest sinewrunner marrowplate titanbone |
| jade_monastery | incenserobe jadeguard lionward templeguard |
| storm_bastion | stormcaller galerunner bastionmail stormhelm |
| bloodmoon_court | sanguine fencer courtier nightguard |
| obsidian_labyrinth | oracle hornrunner hornbreaker basaltplate |
| abyssal_lighthouse | abysswatch deepsight lampkeeper anglerplate |
| eclipse_cathedral | ashchoir fallenblade haloguard eclipse |
| wyrms_hoard | ashcultist scalehide wyrmscale hoardplate |

## Monsters
- `/summon ashbound:<id>` - any monster, e.g. `/summon ashbound:ignavar`, `/summon ashbound:fallen_seraph`,
  `/summon ashbound:keeper_in_light` (spawn eggs are in the "Ashbound: Monsters" creative tab)
- Add `{NoAI:1b}` to look at one standing still: `/summon ashbound:ignavar ~ ~ ~5 {NoAI:1b}`

## Other
- `/ashbound coins <n>` - set coins
- `/ashbound capital` - teleport to Highmourn
- `/ashbound tree <name>` - grow a wildwood tree
- `/ashbound tree clockwork_spire` - raise the Clockwork Spire where you stand (a lag spike: 125k blocks)
- `/locate structure ashbound:clockwork_spire` - find one in new chunks (plains, savanna, meadow, windswept hills)
- `/ashbound npc <kind>`, `/ashbound npc crowd <n> <tags>` - townsfolk
