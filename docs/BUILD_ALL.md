# Build all dungeons (except SSS), 2026-10-28

The user: "make all the dungeons except the SSS, items for each, monsters, bosses etc, you don't have to stop to ask,
I will test at the end". No asking between steps; the user tests at the end. Tick a step off here when it's done, so
the work survives compaction.

Dungeons (10): cellar F, gallows F, rotwood F, crypt E, plague D, foundry C, ossuary C, temple C, frost B, silk B.
The Silk Archive was not in GEAR.md; it gets the same full set (mats Silk Thread / Ink Gland / the Queen's Spinneret,
boss staff = summoner).

## Phase 1: gear systems (code, all dungeons at once)
- [x] gear data: tools/gear.py = THE table (from GEAR.md + silk): per dungeon its mats, mobs (common/elite/boss),
      its 10 weapons, 4 armour sets, 6 boss weapons; writes resources/ashbound/gear.json, lang, mat items
- [x] Mats.java: 30 material items (icons from tools/blender/mat_icons.py or voxel)
- [x] Loot: GateLoot.java, LivingDeathEvent: every gate mob drops 1-2 common, the elite/key 1 elite (+casters 10%),
      the boss 1 trophy each player near + 20%/player one of its 6 boss weapons
- [x] Gate Forge block + menu + screen: pick a dungeon tab, list its recipes, cost shown, craft button (server checks)
- [x] Mana + spell power: player attachment, regen, HUD bar; SPELL_POWER attribute; robes +15% power +10% regen
- [x] Staffs: Staff item (school BLACK bolt / WHITE heal / SUMMON minions), right-click casts, mana cost, cooldown
- [x] Starter gear at Brann Holt (plain robe, staffs, bow, shield...)

## Phase 2: weapons (tools/weaponforge.py, voxsword style like the approved Kiln line)
- [x] port the old `*` weapons from E:/Ashbound (port_weapons.py WEAPONS list)
- [x] parametric builders per type: sword dagger hammer spear twohander shield bow staff; per-dungeon theme
      (palettes + motif: cork/hoop, noose/rope, antler/fungus, candle/wax, beak/lime, mask/crystal, gear/skull,
      ember/slag, ice/banner, silk/ink)
- [x] all 10 dungeons x 10 weapons + 6 boss weapons; render sheets to tools/renders/weapons_<gate>.png

## Phase 3: armour (28 new sets)
- [x] parametric armour builder writing the same OBJ input efarmor.py reads (check voxarmor.py in E:/Ashbound)
- [x] 4 classes per dungeon; robes get skirts automatically; previews + icons

## Phase 4: maps at EF scale (cellar done)
- [x] gallows  - [x] rotwood  - [x] crypt  - [x] plague  - [x] foundry  - [x] ossuary  - [x] frost  - [x] temple
  each: tools/lairs/<gate>_ef.py, reach_check, lightcheck mood, port_gate.py <gate> lair
- [x] frost: 3 more monsters (rule 5 + boss); foundry has 4 + Cinderhusk

## Status log
- 10/28 phase 1 DONE (compiles, untested): tools/gear.py -> resources/ashbound/gear.json (+ weapon EF caps, lang, mat item
  models; old mat icons outlined). Java: Gear (mats, weapons by kind, bow damage, apprentice staffs), Armors from gear.json
  (robes +spell power/regen), Spells (mana attachment+attrs+HUD packet, Staff, Bolt entity, heal, thralls), GateLoot,
  GateForge (block + tools/blender/forge_props.py mesh, ForgeOpen/ForgeCraft), client ForgeScreen + ManaHud.
  Forgemaster sells gate_forge + 3 apprentice staffs and buys drops (tools/npc_shops.py).
  STILL MISSING: icons for 6 mats (frost, silk), weapon models (phase 2), apprentice staff models.
- 10/28 phase 2 DONE: tools/weaponforge.py (themes per gate + type templates + HINTS by name; old `*` copied from
  E:/Ashbound with outlined icons; kiln_bulwark/longbow KEEP = voxkiln_gear.py). Icons batched in one Blender run
  (tools/blender/weapon_icons.py). `python tools/weaponforge.py [gate|id] --icons`. 160 weapons + 3 apprentice staffs.
- 10/28 phase 3 DONE: tools/armorforge.py (class templates x weaponforge themes, per-bone OBJs -> tools/armor_src/,
  atlas grown to 256 for the lining swatch) -> `cd tools; python efarmor.py <sets>` (SETS now from gear.json; src()
  picks old Ashbound only when its rig has helm_head - mob names collide; no despeckle on new sheets) -> icons:
  blender armor_icons.py -- <sets>; python efarmor.py icons <sets>. 32 new sets (silk too), 128 icons.
- 10/28 gallows_ef DONE + ported: road 9w, cage walk 11w, long drop 7w, arena R20 / deck 23; lamps via efkit.light_grid
  + road edge posts; lightcheck now counts only floor reachable from tp (and roofs up to 90 up, for open sky):
  gallows dark 2% lit 66%. Workflow per gate (from tools/lairs): OPEN_SEAL=1 PYTHONPATH=. python
  E:/Ashbound/tools/reach_check.py <g>_ef <Class> | grep NO; python <g>_ef.py --game; cd ..; python port_gate.py <g> lair;
  python lairs/lightcheck.py <g> --bands.
- 10/28 rotwood_ef DONE + ported: glade R16 (cz -219), court R22 h30 (cz -265), glowcap grids; dark 5% lit 55%.
- 10/28 crypt_ef DONE + ported: niche halls 5w x7h, passes min 6 tall, pole lamps sexton/yard; dark 2% lit 68%.
- 10/28 plague_ef DONE + ported: morgue 15w x9h, theatre R18 h20 (cz -206), efkit.hang_grid (+floors() fallback) lime lamps h4 every 5; dark 2% lit 73%.
- 10/28 foundry_ef DONE + ported: hall() 7w x7h, chain-hall gantry 7w, quench stair 7w, kiln heart roof +6 (chains carried up), braziers in slag cave; dark 9% lit 76%.
- 10/28 ossuary_ef DONE + ported: hall() 7x7, catwalk 5w, crypt 17w x9h; dark mood ok (24/30). tools/lairs/reach7.py = reach_check at SEED 7 (what --game exports); all gates pass at 7.
- 10/28 temple_ef DONE + ported (SEED 3): bridge 5w, sealed door 19x18 h11, front stair last step + dais stairs face north (was a hop); dark mood ok 35/27.
- 10/28 frost monsters DONE: tools/frostmobs.py (Frostbound body, halberd stripped) -> tools/mob_src: standard_bearer
  (banner + tower shield + ice crown, KEY), frost_chaplain (hood, vestments, ice-crystal staff, censer), rime_knight
  (horned helm, double pauldrons, ice greatsword). port_gate mobs: spec `stats=` for mobs with no old class, E.SRC
  switches to tools/mob_src when the mesh is there. rime_hound renamed rime_knight in gear.py.
- 10/28 frost_ef DONE + ported: gate out 7x7, bridge 7w (rails/piers out to x4), gate wall + barred 7x7 seal at
  z -188 (Standard Bearer in the camp holds the key), tents raised (chests reachable), archers off the far ledge,
  road lamp posts every 8 + hang_grid lanterns every 5; dark 0% lit 63%, all reachable at SEED 7.
- 10/28 ALL PHASES DONE, compiles + processResources OK. Untested in game. Not built: forge fusion/upgrades (+1..+5),
  a ranged cast for frost_chaplain (melee walker for now).

## Phase 5: the 15 missing Roster v2 dungeons (no SSS) - user 10/28 "do the others as well"
Generators first, then one pilot (Weeping Mine) end to end, then the rest in rank order.
- [x] gear.py: the 15 dungeon() entries (mats, mobs, weapons, boss weapons, sets, colour); gear.json carries lair+debris once built
- [x] blockforge.py: painted masonry families per dungeon -> gate_blocks.json (no new Java)
- [x] props: tools/blender/kit_props.py -- <gate> (common lantern/chain/bars/coffer re-skinned + UNIQUE per gate)
- [x] monsterforge.py + forge_specs.py (THEMES ramps + spec per mob; rig crawler/beast on EF spider) -> tools/mob_src
- [x] tools/lairs/forge_lair.py: spec-driven room chain (hall/cave/round/chasm/descent, passes, seal, coffer niches, hang_grid lamps)
- [x] GateDungeons appends gear.json dungeons with a lair (rank from gear.json); Gear colour + Spells sparks/effects per gate
- E: [x] weeping_mine [x] tide_chapel [x] brigands_gorge
- D: [ ] rookery [ ] hollow_circus [ ] mirefen_coven
- C: [ ] sandsunk_tomb
- B: [ ] fallen_titan [ ] jade_monastery
- A: [ ] storm_bastion [ ] bloodmoon_court [ ] obsidian_labyrinth
- S: [ ] abyssal_lighthouse [ ] eclipse_cathedral [ ] wyrms_hoard

### Per-dungeon recipe (phase 5), all from tools/ (cwd E:/EFTest/game)
1. monsters are HAND-BUILT (template forge_specs bodies rejected by the user 10/28): tools/mobs/<gate>.py, one function
   per monster with vox2.Kit (own story, silhouette, shaders, extra bones), MOBS = {id: dict(make=fn, ent, stats,
   key/boss, rig="crawler" + return joints)}; forge_specs._hand_built() overrides the specs; preview:
   `python tools/monsterforge.py <gate> --preview; python tools/mobsheet.py <gate>` -> tools/renders/mobs/<gate>.png
2. dforge.py: blocks (blockforge painters) + props (common_props + uniques) + layout (palette, rooms, seal index);
   `python tools/blockforge.py <gate> --sheet`; kit_props.py: PALETTES[gate] + UNIQUE[gate] fns;
   `blender -b -P tools/blender/kit_props.py -- <gate> preview`
3. map: `cd tools/lairs; PYTHONPATH=.:..:E:/Ashbound/tools python forge_lair.py <gate> r0 r2 ...` (preview, props stood in
   by vanilla), `OPEN_SEAL=1 ... python reach7.py forge_lair <gate> | grep -v ^ok` (and without OPEN_SEAL: only past-seal NO)
4. `python tools/newgate.py <gate>` (blocks, props, mobs, lair, loot)
5. gear art: weapon_themes_v2.py Theme + HINTS + MATS fns; armorforge CLOTH has all 15;
   `python tools/weaponforge.py <gate> --icons`; `python tools/weaponforge.py mats --icons`;
   `python tools/armorforge.py <gate>`; `cd tools; python efarmor.py <4 set ids>`;
   `blender -b -P tools/blender/armor_icons.py -- <sets>`; `python efarmor.py icons <sets>`
6. `python tools/gear.py; python tools/idcheck.py; ./gradlew compileJava processResources`
Gotchas: mat ids = slug(name) - never name a block the same (weeping_crystal -> weeping_crystal_block);
lime_lamp block/weapon clash fixed (weapon now Limelight Staff); caves get a full-length 7x7 walkway.
- 10/28 weeping_mine DONE (untested): 13 blocks (+8 family), 9 props, 6 mobs (shard_crawler crawler, cart_golem, lamp_miner,
  blind_burrower, foreman KEY, the_vein boss x3.78), 8 rooms (pithead, shaft, crystal gallery, drop, ore hall, pump house
  [Foreman, seal], weeping deep, heart arena), 16 weapons, 4 sets, 3 mats. Compiles.
- 10/28 tide_chapel + brigands_gorge DONE (untested), same recipe. Per-dungeon data now: forge_specs.py (mobs), dforge_<short>.py
  (blocks/props/layout; dforge.py imports them at the end), kit_props.py PALETTES+UNIQUE, weapon_themes_v2.py (Theme, HINTS, MATS).
  Fixed: chasm cleanup deleted other rooms' air below its bridge (now only its own); scatter gives facing only to facing/coffer props.
  Shell heredocs with long python break: write patch files with the Write tool and run them.
- 10/28 MONSTERS REMADE by hand (tools/mobs/*.py, vox2.Kit) for weeping_mine, tide_chapel, brigands_gorge, rookery,
  hollow_circus, mirefen_coven, all ported (newgate <gate> mobs). Sheets: tools/renders/mobs/<gate>.png.
- 10/28 mirefen_coven DONE (untested): blocks, props, lair, loot, weapons, mats, armour, gear.json; compiles.
  Next: sandsunk_tomb, fallen_titan, jade_monastery, storm_bastion, bloodmoon_court, obsidian_labyrinth,
  abyssal_lighthouse, eclipse_cathedral, wyrms_hoard (full recipe, hand-built monsters).
- 10/28 sandsunk_tomb DONE (untested): 12 blocks, 8 props, 6 hand-built mobs, 8 rooms (reach ok), weapons/mats/armour; compiles. monsterforge.Made now gives empty bones a speck (hidden legs).
- 10/28 fallen_titan DONE (untested): 11 blocks (titan_sinew block renamed titan_sinew_wall - mat clash), 8 props, 6 mobs (still_heart boss on the spider rig), 7 rooms; forge_lair chasm no longer holes the next passage floor (y<=fl).
- 10/28 jade_monastery DONE (untested): 12 blocks, 8 props, 6 mobs (thousand_hands boss with a halo of armed hands), 8 rooms (stair of heaven goes UP), gear art; compiles.
- 10/28 storm_bastion DONE (untested): 11 blocks (storm_glass block -> storm_glass_block, mat clash), 8 props, 6 mobs (thunder_abbess boss: storm skirt, halo of rods, bell), 8 rooms (two up-stairs), gear art; compiles.
- 10/28 bloodmoon_court DONE (untested): 11 blocks, 8 props, 6 mobs (counts_hound elite on the spider rig, countess_vael with bat wings + blood gown), 8 rooms, gear art; compiles. Left: obsidian_labyrinth, abyssal_lighthouse, eclipse_cathedral, wyrms_hoard.
- 10/28 obsidian_labyrinth DONE (untested): 10 blocks, 8 props, 6 mobs (minotaur boss: burning horns, labrys), 8 rooms, gear art; compiles.
- 10/28 abyssal_lighthouse DONE (untested): 11 blocks, 8 props, 6 mobs (keeper_in_light boss: lighthouse-lens head + beam, lantern staff; angler_knight elite w/ lure + harpoon), 8 rooms, gear art; compiles. Left: eclipse_cathedral, wyrms_hoard.
- 10/28 eclipse_cathedral DONE (untested): 12 blocks, 8 props, 6 mobs (fallen_seraph boss: black sun + corona, six torn wings, Eclipse greatsword; seraph_warden elite: six wings, eyes in the face wings, fire halo key), 8 rooms (tower stair up), gear art; compiles. Left: wyrms_hoard.
- 10/28 wyrms_hoard DONE (untested): 10 blocks, 8 props, 6 mobs (ignavar boss: four-legged ash dragon on the hound rig, torn wings, gold in his belly; wyrm_priest elite w/ the priest's scale key; drake crawler), 9 rooms, gear art; compiles. ALL 15 Roster v2 dungeons built (no SSS).
