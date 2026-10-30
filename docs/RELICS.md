# Curios and relics (v2 list, 10/29 — not built yet)

Our own system instead of Apotheosis. **60 curios** (20 rings, 20 amulets, 20 charms) with rarities, plus
**16 relics** whose power is upgraded (I -> II -> III). The 30 items agreed earlier are all kept (marked *).

## Rules

- **Slots (Curios API, already in the pack):** Ring x2, Amulet x1, Charm x1, Relic x1 (custom slot).
- **Rarity (same tiers and weights as the world arms):** per slot 7 Uncommon, 6 Rare, 4 Epic, 3 Legendary.
  - U: one stat, worth ~3% (one uncommon affix, docs/BALANCE.md pass 5)
  - R: two stats, ~4.5% together
  - E: ~6% of stats + a small **perk**
  - L: ~6% of stats + a real **effect**
- Stats are % (damage, health, armour, spell power...) so a curio stays useful at every rank; luck and mana flat.
- Every party role gets something in every slot: melee, tank, bow, black / white / summon mages, explorers.
- **Where:** like the world weapons: mod structure chests, faction elites, tower hoards. Epics and legendaries mostly
  from elites, tower hoards and big dungeon chests. Each item belongs to a faction (its look follows the faction).
- Wearing two copies of the same ring: only one counts.
- Models: a sculpted Blender model each, shown in the slot (gui3d, like the weapons); amulets and relics also show on
  the body. Concept sheet before modelling.

Short names: dmg = melee damage, as = attack speed, ms = move speed, hp = max health, arm = armour,
tough = toughness, kb = knockback resistance, sp = spell power, regen = mana regen, ranged = bow damage,
summon = thrall damage, heal = healing done, stam = stamina regen.

## Rings (20) — mostly offence

| | Name | Faction | Stats | Perk / effect |
|---|---|---|---|---|
| U | Brigand's Knuckle-Ring * | Brigands | +3% dmg | |
| U | Tunnel Rat's Band * | Delvers | +3% ms | |
| U | Gravedigger's Loop | Grave-born | +3% arm | |
| U | Spore-Stained Ring | Sporefolk | +3% regen | |
| U | Bowstring Ring | Sky Legion | +3% ranged | |
| U | Iron Thumb-Ring | Fallen Order | +5% kb | |
| U | Knotted Bone Ring | Blightkin | +3% summon | |
| R | Corsair's Doubloon * | Corsairs | +0.5 luck, +2% ms | |
| R | Tarnished Signet * | Fallen Order | +3% arm, +3% kb | |
| R | Ember Coil | Ash Legion | +3% sp, +2% regen | |
| R | Briar Band | Thornborn | +3% heal, +2% hp | |
| R | Frostbitten Ring | Rimebound | +2% hp, +2% tough | |
| R | Hollow-Eye Ring | Voidborn | +5% as, -1% hp | |
| E | Salt Khan's Seal * | Salt-Cursed | +4% dmg, +2% as | Kills give +10% ms for 3 s |
| E | Chitin Loop * | Brood | +3% tough, +3% as | Every 5th hit gives back a little stamina |
| E | Rime Band * | Rimebound | +3% hp, +3% arm | Whoever hits you is slowed 1 s (10 s cooldown) |
| E | Marksman's Gyre | Sky Legion | +6% ranged | Fully drawn arrows go through one enemy |
| L | Ring of the Drowned God * | Corsairs | +3% arm, +3% hp | Breathe underwater, swim fast; +15% damage while wet |
| L | Ring of the Ninth Pyre | Ash Legion | +4% sp, +2% regen | Every 4th spell costs no mana and hits 50% harder |
| L | Warden's Oathring | Fallen Order | +4% arm, +5% kb | A blocked hit taunts enemies within 8 blocks and gives 2 hearts of absorption (8 s cooldown) |

## Amulets (20) — mostly defence and magic

| | Name | Faction | Stats | Perk / effect |
|---|---|---|---|---|
| U | Wolf-Tooth Necklace * | Brigands | +3% hp | |
| U | Miner's Medallion | Delvers | +3% tough | |
| U | Shell Pendant | Corsairs | +4 mana | |
| U | Grave Candle Pendant | Grave-born | +3% heal | |
| U | Spore Bead String | Sporefolk | +3% regen | |
| U | Thorn Choker | Thornborn | +3% arm | |
| U | Ash Prayer Beads | Ash Legion | +3% sp | |
| R | Moonpetal Locket * | Sky Legion | +4 mana, +3% regen | |
| R | Legion Sun-Disc * | Salt-Cursed | +3% sp, +2% hp | |
| R | Frozen Tear | Rimebound | +3% hp, +2% kb | |
| R | Brood Mother's Fang | Brood | +3% summon, +3% thrall health | |
| R | Gilded Pyx | Fallen Order | +3% heal, +3 mana | |
| R | Void-Glass Shard | Voidborn | +6% sp, -1.5% hp | |
| E | Augur's Ember * | Ash Legion | +6% sp | Spells set the target on fire for 2 s |
| E | Briar Heart * | Thornborn | +3% hp, +3% regen | Each kill heals half a heart |
| E | Gryphon Torc * | Sky Legion | +3% as, +3% ms | Dodges cost 25% less stamina |
| E | Bulwark Gorget | Fallen Order | +3% arm, +3% tough | +20% threat (monsters pick you first) |
| L | Last Vigil Reliquary * | Fallen Order | +3% sp, +3% hp | Below 30% health: a soul shield absorbs 6 hearts (2 min cooldown) |
| L | Heart of the Hive | Brood | +4% summon, +2% hp | A thrall that dies bursts into 3 broodlings for 8 s |
| L | Salt Saint's Censer | Salt-Cursed | +4% heal, +4 mana | Your heals also clear one bad effect and give the ally +20% damage for 3 s |

## Charms (20) — utility, loot and exploring

| | Name | Faction | Stats | Perk / effect |
|---|---|---|---|---|
| U | Poacher's Rabbit Foot * | Brigands | +0.5 luck | |
| U | Delver's Lamp * | Delvers | +3% tough | |
| U | Loaded Dice | Corsairs | +6% coins from kills | |
| U | Knucklebone Charm | Grave-born | +3% Ash from kills | |
| U | Bundle of Briar Twigs | Thornborn | +5% stam | |
| U | Snow Hare's Tail | Rimebound | +2 safe-fall blocks | |
| U | Ash-Stamped Token | Ash Legion | +3% dmg vs elites | |
| R | Spore Pouch * | Sporefolk | +2% hp, +3% regen | |
| R | Harpy Feather * | Sky Legion | +3 safe-fall blocks, +2% ms | |
| R | Smuggler's Purse | Brigands | +8% coins, +0.5 luck | |
| R | Void Marble | Voidborn | +6% stam, dodges cost 10% less | |
| R | Salt Ward | Salt-Cursed | Poison and wither 25% shorter, +2% hp | |
| R | Grub Lantern | Brood | Night vision underground, +2% tough | |
| E | Kraken Eye * | Corsairs | +oxygen, faster swimming | Sees monsters through water (glow) |
| E | Corsair's Compass * | Corsairs | +1 luck, +3% ms | Points to the nearest unlooted structure chest |
| E | Blight Vial | Blightkin | +3% hp | Immune to poison; your hits rot the foe for 3 s (a quarter of the hit, undead too) |
| E | Reliquary Finger-Bone | Grave-born | +6% Ash | Undead deal 10% less damage to you |
| L | Gryphon Plume * | Sky Legion | +3% ms | Double jump; slow fall while holding jump |
| L | Delver's Last Pick | Delvers | +3% tough, +10% mining speed | Mined ore: 20% chance of a double drop; breaking ore shows ore within 6 blocks for 5 s (30 s cooldown) |
| L | Rift Key | Voidborn | +3% ms | Mark a spot; use again to rift back to it (5 min cooldown) |

## Relics (16) — legendary only, with powers you upgrade

A relic always has a **power**: some trigger by themselves, some are used on a key (default **V**). You find it at I.
**Upgrade it at the Gate Forge**: I -> II costs 1 boss trophy + Ash, II -> III costs 3 boss trophies + more Ash (trophies
of any boss at or above the relic's rank). Small stats, big powers. Relic slot only from big dungeon chests, tower hoards
and bosses.

| Name | From | Stats | Power (I -> II -> III) |
|---|---|---|---|
| Barrow King's Signet * | Grave-born | +3% hp | A kill is a soul; at 10 / 8 / 6 souls a ghost warrior fights with you for 15 / 20 / 25 s (III: two ghosts) |
| Rime Hourglass * | Rimebound | +3% arm | A killing blow freezes you in ice for 2 s, then you stand up at 30 / 40 / 50% health (10 / 8 / 6 min cooldown) |
| Void Pearl * | Voidborn | +3% ms | Dodges blink 3 blocks further and leave a rift that slows for 2 / 3 / 4 s (III: the rift also hurts) |
| Mantis Molt * | Brood | +3% as | A dodge that slips an attack gives back 50 / 75 / 100% of its stamina; your next hit staggers |
| Spore Heart * | Sporefolk | +3% hp | Getting hit puffs poison spores round you (5 / 4 / 3 s cooldown, III: bigger cloud) |
| Legion's Brand * | Ash Legion | +3% dmg | Every 3rd combo hit bursts into teal fire for 30 / 45 / 60% extra damage |
| Thornborn Rose * | Thornborn | +3% arm | Hits heal 3 / 4 / 5% of the damage dealt; blocking reflects 10 / 15 / 20% |
| Chimera Gland * | Blightkin | +2% hp | Each kill: a random buff for 6 / 8 / 10 s (strength, speed or regeneration; III: two at once) |
| Kiln-Father's Coal | Foundry (Ossric) | +3% dmg | **[V]** Become molten for 6 / 8 / 10 s: hits burn, +15 / 20 / 25% damage, immune to fire (90 s cooldown) |
| Pale Abbot's Wick | Crypt (Pale Abbot) | +3% heal | **[V]** Set a candle ward (6 blocks): allies inside heal 0.5 / 0.75 / 1 heart a second for 5 s (60 s cooldown) |
| Hangman's Noose | Gallows Hill (Hangman) | +4% kb | **[V]** Yank one enemy to you and stun it 1 / 1.5 / 2 s (bosses: no stun) (20 s cooldown) |
| Cask Mother's Tap | Drowned Cellar (Cask Mother) | +3% hp | A potion you drink also works on allies within 6 / 8 / 10 blocks at 50 / 75 / 100% |
| Mossking's Acorn | Rotwood (Mossking) | +3% tough | **[V]** Throw an acorn: roots burst up and hold enemies within 4 blocks for 2 / 2.5 / 3 s (40 s cooldown) |
| Silk Matron's Spindle | Silk Archive | +3% ms | Dodging leaves a web: the first enemy in it is bound for 1 / 1.5 / 2 s (6 s cooldown) |
| Stormspire Lodestone | tower hoards | +3% as | Every 10 / 8 / 6 s your next hit calls lightning that jumps to 2 / 3 / 4 enemies |
| Warhorn of the Last Keep | tower hoards | +3% hp | **[V]** Blow the horn: party within 12 blocks gets +10 / 15 / 20% damage and +25% kb for 10 s (60 s cooldown) |

## Balance notes

- Curio totals: 4 curios = ~18-24% of stats + up to 4 perks/effects. A full legendary set is a big jump, so the
  balance pass counts them (with fusion weapons) before the 1.55x rank ladder (docs/BALANCE.md) is applied.
- Relic powers at III are about a keystone's worth; one relic at a time keeps them from stacking.

## Next

1. User approves or edits this list.
2. Concept sheet of the 60 + 16: DONE 10/29 as quick box models, `python tools/curios.py [ids|slots] --sheet`
   (meshes in tools/renders/curios/mesh, shots via tools/blender/curio_shots.py, sheet tools/renders/curios.png).
   Not in the game yet; awaiting approval.
3. **Slice 1 DONE 10/29 (compiles, SelfTest `curios` passes, untested in game):** `tools/curios.py --export` writes the
   76 meshes + 3D-in-slot item models, names, `ashbound/curios.json`, the Curios tags (ring/necklace/charm/relic) and
   slot data (ring x2, relic slot + icon, all four given to players). `Curios.java` registers them (rarity names, own
   tooltip), stats = attribute modifiers while worn; stats with no attribute (bow damage, thrall, Ash, coins, elite
   damage, poison, dodge frames) are summed by `Curios.stat` inside `Passives.stat`. Curios is now a compile + required
   dependency. Active today: all attribute stats, bow/thrall damage, Ash. Not yet: coins%, elite_dmg%, poison_short%,
   dodge_frames, every perk/effect, relic powers, the V key, Forge upgrades I-III.
4. **Slice 2 DONE 10/29 (compiles, SelfTest `curioEffects` passes, untested in game):** `CurioFx.java` does every
   epic/legendary perk and every relic power by tier (custom data `relic_tier`). V = the worn relic's [V] power,
   sneak+V = Rift Key (client/CurioKeys.java, Net.CurioKey); the Gryphon Plume double jump/slow fall is client-side
   with the server resetting the fall. A relic used on a Gate Forge goes I->II (1 boss trophy + 5000 Ash) and
   II->III (3 trophies + 20000 Ash). coins% (Levels), elite_dmg%, poison_short%, dodge_cost% now work. Loot: structure
   chests 5% (houses 2.5%, big dungeons/treasure 10%) a curio, big dungeon/treasure chests 3% a relic; bosses 12% curio
   + 6% relic, tower foremen 5% + 2%, elites 4%, any monster 0.2%; each player near rolls their own.
   Changed from the list: Void Marble = dodges cost 10% less (was +1 i-frame); Mantis Molt's next hit staggers (was
   unblockable); Kraken Eye makes monsters in water glow for everyone; the Compass works while sneaking.
   Still open: worn amulet/relic models on the body; tower hoards don't roll curios yet; balance pass.
5. **UI 10/29 (compiles, untested in game):** the Curios slot panel recoloured to charred iron + ember
   (`tools/curios_ui.py` -> assets/curios/textures/gui/curios, our mod loads AFTER Curios so ours win); the relic HUD
   right of the hotbar (client/RelicHud.java): the relic's model in an iron socket, its tier above, the V key, an
   ember rim when ready and a draining dark sweep + seconds while cooling down (Net.RelicCd).
4. Loot tables (structures, elites, towers, bosses), SelfTest checks, then the balance pass.
