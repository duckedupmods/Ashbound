# Dungeon gear (EFTest, 2026-10-28, DRAFT)

Every dungeon makes the FULL weapon set (all 10 types) + its boss weapon, and FOUR armour sets, one per weight
class, so a mage, a rogue, a fighter and a tank all gear up in every gate. Everything is crafted at the Gate Forge
from that dungeon's 3 drops; nothing drops whole. `*` = already modelled in old Ashbound (ported, not remade).

## Boss weapons

Every boss has 6 boss weapons, one per role: sword, shield, heavy (a two-hander, hammer or spear), dagger, bow and
one staff. The staff matches the boss, and each staff school has 3 bosses:
- black: Cask Mother, Sovereign, Ossric;
- white: Mossking, Surgeon, Winter Marshal;
- summoner: Hangman, Pale Abbot, Assembler.

Boss weapons drop, not crafted: 20% a kill, rolled separately for each player, any of the 6 at random. Each has its
own model and R skill and sits two rows above its dungeon on the stat ladder. Duplicates are kept for **forge
fusion** (later): a boss weapon + materials (+ another boss weapon) makes a stronger one of the same type, so a
summoner fuses the Hangman's staff up into the next summoner staff, and so on.

## Drops

| Drop | From | Used for |
|---|---|---|
| Common | every monster in the gate | everything |
| Elite | the elite (key) monster; casters drop it 10% of the time | every piece, more for staffs and big weapons |
| Boss trophy | the boss, every kill | helms (1), upgrades past +5 and fusion (later) |
| Boss weapon | the boss, 20% a kill, rolled for each player | one of its 6, picked at random |

## Armour classes (numbers for a full set at rank C; other ranks scale by the stat ladder's x)

In code: Armors.Kind (vanilla side) and tools/efarmor.py EF (Epic Fight stun armour and weight, netherite-like at heavy).

| Class | Armour | Toughness | EF stun armour | EF weight | Pros | Cons |
|---|---|---|---|---|---|---|
| Robe (mage) | 6 | 0 | 3 | 1.5 | +15% spell power, +10% mana regen, +8% move, dodges cost 25% less stamina | knocked over by anything, dies to a combo |
| Light | 10 | 0 | 10 | 4 | +8% move, +8% attack speed, dodges cost 15% less stamina | staggers easily |
| Medium | 15 | 1 | 30 | 8 | no penalties, shrugs off light hits | nothing standout |
| Heavy | 20 | 3 | 60 | 14 | rarely staggered, 30% knockback resist | -8% move, -5% attack speed, heavy weight drains stamina fast |

Set bonus (2pc / 4pc) stays per set: one dungeon element each (Undertow, Strangle, Bloom, Wax, Crystallize...).

## Costs (rank F; E x1.25, D x1.4, C x1.5, B x1.75, rounded)

| Piece | Common | Elite | Trophy |
|---|---|---|---|
| Helm | 10 | 1 | 1 |
| Chest | 16 | 2 | |
| Legs | 12 | 1 | |
| Boots | 8 | 1 | |
| Dagger | 8 | 1 | |
| Sword / Spear / Bow | 12 | 1 | |
| Hammer | 14 | 1 | |
| Shield | 12 | 2 | |
| Two-hander | 18 | 2 | |
| Any staff | 10 | 2 | |
| Upgrade +1 / +2 / +3 / +4 / +5 | 4 / 4 / 8 / 8 / 12 | - / - / - / 1 / 2 | |

A full armour set is 46 common, 5 elite and 1 trophy: roughly 3 clears at F.

## The Drowned Cellar (F): Sodden Cork / Mimic's Tongue / Mother of Vinegar

| Slot | Item | Note |
|---|---|---|
| Sword | Bilge Falchion* | |
| Dagger | Spigot Knife | a cellarman's tap-knife |
| Hammer | Cooper's Mallet* | |
| Spear | Bilge Boathook | hooked pole |
| Two-hander | Stave Cleaver | cask staves banded into a blade |
| Shield | Cask-Lid Shield | an iron-hooped barrel head |
| Bow | Hoop Bow | |
| Black staff | Sourwell Staff | spits acid that eats armour |
| White staff | Mother's Ladle | heals over time from the living culture |
| Summoner staff | Revel Tap | pours out sodden revellers |
| Boss sword | Lees Sabre | drops from the Cask Mother |
| Boss shield | Mother's Lid | drops from the Cask Mother |
| Boss heavy | Tidebreaker* (two-hander) | drops from the Cask Mother |
| Boss dagger | Corkscrew | drops from the Cask Mother |
| Boss bow | Undertow Bow | drops from the Cask Mother |
| Boss staff | Sourmother (black) | drops from the Cask Mother |
| Robe | Vintner's Robe | |
| Light | Corkrunner | |
| Medium | Cooper's Harness | stave plates and hoops |
| Heavy | Bilgewader* | |

## Gallows Hill (F): Hangman's Hemp / Gibbet Shackle / the Hangman's Hood

| Slot | Item | Note |
|---|---|---|
| Sword | Headsman's Sword | |
| Dagger | Gibbet Knives* | |
| Hammer | Trapdoor Maul | |
| Spear | Gibbet Hook | |
| Two-hander | Gibbet Greatblade* | |
| Shield | Gibbet Door | |
| Bow | Noose Bow | hemp-strung |
| Black staff | Tar Staff | burning tar |
| White staff | Last Rites | |
| Summoner staff | Hanging Tree | raises the Dropped |
| Boss sword | Hangman's Verdict | drops from the Hangman |
| Boss shield | Gallows Gate | drops from the Hangman |
| Boss heavy | The Last Drop (two-hander, axe) | drops from the Hangman |
| Boss dagger | Noose-Cutter | drops from the Hangman |
| Boss bow | The Long Drop | drops from the Hangman |
| Boss staff | Thirteen Knots (summoner) | drops from the Hangman |
| Robe | Tarwitch Shroud | |
| Light | Gibbet* | |
| Medium | Headsman's Leathers | |
| Heavy | Gallowsguard | gibbet-cage plate |

## The Rotwood (F): Grey Mycelium / Stag Velvet / the Mossking's Crown

| Slot | Item | Note |
|---|---|---|
| Sword | Rotbranch Blade | |
| Dagger | Thorn Shiv | |
| Hammer | Burl Maul | |
| Spear | Stagtine Spear* | |
| Two-hander | Antler Greatblade | |
| Shield | Shelf-Fungus Shield | |
| Bow | Yewrot Bow | |
| Black staff | Sporeblight | spore cloud |
| White staff | Mossheart | |
| Summoner staff | Rootcaller | raises the Rooted |
| Boss sword | Mossking's Briar | drops from the Mossking |
| Boss shield | Crownbark | drops from the Mossking |
| Boss heavy | Thornmother* (two-hander) | drops from the Mossking |
| Boss dagger | Velvet Tine | drops from the Mossking |
| Boss bow | Antlerbow | drops from the Mossking |
| Boss staff | Mosscrown (white) | drops from the Mossking |
| Robe | Rotwarden* | |
| Light | Stagrunner | velvet hide |
| Medium | Barkwight | bark plates |
| Heavy | Heartwood | heavy bark and antler |

## The Crypt (E): Corpse Wax / Coffin Bracket / the Abbot's Death-Mask

| Slot | Item | Note |
|---|---|---|
| Sword | Vigil Sword | |
| Dagger | Gravedigger's Knife | |
| Hammer | Bellmaul | |
| Spear | Gravespike | |
| Two-hander | Candlewake* | |
| Shield | Coffin-Lid Shield | |
| Bow | Mourner's Bow | |
| Black staff | Wickfire | candle flame bolts |
| White staff | Censer of Rest | |
| Summoner staff | Ghoulbell | calls ghouls |
| Boss sword | Pale Vigil | drops from the Pale Abbot |
| Boss shield | Abbot's Reliquary | drops from the Pale Abbot |
| Boss heavy | Gravewarden's Oath* (two-hander) | drops from the Pale Abbot |
| Boss dagger | Last Candle | drops from the Pale Abbot |
| Boss bow | Requiem | drops from the Pale Abbot |
| Boss staff | Abbot's Crozier (summoner) | drops from the Pale Abbot |
| Robe | Abbot's Vestments | |
| Light | Mourner's Weeds | |
| Medium | Gravewarden* | |
| Heavy | Coffinplate | |

## The Plague Ward (D): Lime Gauze / Beak Resin / the Surgeon's Lamp

| Slot | Item | Note |
|---|---|---|
| Sword | Plague Bonesaw* | |
| Dagger | Plague Lancets* | |
| Hammer | Plague Pestle* | |
| Spear | Beak Cane* | |
| Two-hander | Plague Amputator* | |
| Shield | Quarantine Door | |
| Bow | Tourniquet Bow | |
| Black staff | Miasma Censer | |
| White staff | Lime Lamp | |
| Summoner staff | Leper's Bell | calls bell lepers |
| Boss sword | Mercy* | drops from the Surgeon |
| Boss shield | Surgeon's Tray | drops from the Surgeon |
| Boss heavy | Surgeon's Probe (spear) | drops from the Surgeon |
| Boss dagger | Scalpel Saint | drops from the Surgeon |
| Boss bow | Suture Bow | drops from the Surgeon |
| Boss staff | Lampbearer (white) | drops from the Surgeon |
| Robe | Beakmask* | |
| Light | Orderly's Wraps | |
| Medium | Friar's Harness | |
| Heavy | Quarantine Plate | |

## The Faceless Temple (C): Mana Shard / Stolen Visage / the Sovereign's Mask

| Slot | Item | Note |
|---|---|---|
| Sword | Faceless Blade* | |
| Dagger | Faceless Fang* | |
| Hammer | Faceless Maul* | |
| Spear | Faceless Lance* | |
| Two-hander | Faceless Greatsword* | |
| Shield | Mirror of No Face | |
| Bow | Shardstring Bow | |
| Black staff | Shardcaller | crystal lances |
| White staff | Veilhealer | |
| Summoner staff | Maskbearer | calls hollows |
| Boss sword | Sovereign's Edge | drops from the Sovereign |
| Boss shield | Thousand-Face Aegis | drops from the Sovereign |
| Boss heavy | Starfell Edge* (two-hander) | drops from the Sovereign |
| Boss dagger | Visage Thief | drops from the Sovereign |
| Boss bow | Starfall Bow | drops from the Sovereign |
| Boss staff | Manacrown (black) | drops from the Sovereign |
| Robe | Acolyte's Veil | |
| Light | Faceless* | |
| Medium | Sentinel's Mail | |
| Heavy | Sovereign Plate | |

## The Ossuary Engine (C): Grave Brass / Soul Wick / the Engine Heart

| Slot | Item | Note |
|---|---|---|
| Sword | Bonewright Blade* | |
| Dagger | Bonewright Shiv* | |
| Hammer | Bonewright Maul* | |
| Spear | Bonewright Pike* | |
| Two-hander | Bonewright Greatblade* | |
| Shield | Ribcage Shield | |
| Bow | Brass Recurve | |
| Black staff | Wickflame | |
| White staff | Hymn Staff | |
| Summoner staff | Assembler's Crank | builds bone hounds |
| Boss sword | Engine Blade | drops from the Assembler |
| Boss shield | Boilerplate | drops from the Assembler |
| Boss heavy | Brasshog Cleaver* (two-hander) | drops from the Assembler |
| Boss dagger | Piston Shiv | drops from the Assembler |
| Boss bow | Steam Arbalest | drops from the Assembler |
| Boss staff | Assembler's Heart (summoner) | drops from the Assembler |
| Robe | Cantor's Robe | |
| Light | Stitched Leathers | |
| Medium | Bonewright* | |
| Heavy | Pallbearer Plate | |

## The Slag Foundry (C): Slag Iron / Crucible Ember / the Kiln-Father's Brand

| Slot | Item | Note |
|---|---|---|
| Sword | Kiln Blade* | |
| Dagger | Kiln Fang* | |
| Hammer | Kiln Maul* | |
| Spear | Kiln Pike* | |
| Two-hander | Kiln Greatsword* | |
| Shield | Kiln Bulwark* | in EFTest already |
| Bow | Kiln Longbow* | in EFTest already |
| Black staff | Crucible Staff | molten bolts |
| White staff | Hearth Staff | |
| Summoner staff | Slagmother | pours slaglings |
| Boss sword | Brandsteel | drops from Ossric |
| Boss shield | Furnace Door | drops from Ossric |
| Boss heavy | Kilnheart* (two-hander) | drops from Ossric |
| Boss dagger | Ember Fang | drops from Ossric |
| Boss bow | Bellows Bow | drops from Ossric |
| Boss staff | Ossric's Brand (black) | drops from Ossric |
| Robe | Bellows Robe | |
| Light | Slagrunner | |
| Medium | Riveter's Harness | |
| Heavy | Kilnplate* | |

## The Frozen Procession (B): Rime Shard / Frozen Fletch / the Marshal's Heart (drops NEW)

| Slot | Item | Note |
|---|---|---|
| Sword | Rime Sword | |
| Dagger | Icicle Dirk | |
| Hammer | Glacier Maul | |
| Spear | Frostbound Pike | |
| Two-hander | Procession Greatsword | |
| Shield | Glacier Tower | |
| Bow | Frostbound Longbow | |
| Black staff | Blizzard Staff | |
| White staff | Thaw Staff | |
| Summoner staff | Banner of the March | calls frostbound |
| Boss sword | Marshal's Sabre | drops from the Winter Marshal |
| Boss shield | Winter Standard | drops from the Winter Marshal |
| Boss heavy | Wintermarch (spear, halberd) | drops from the Winter Marshal |
| Boss dagger | Frostbite | drops from the Winter Marshal |
| Boss bow | Hoarfrost Bow | drops from the Winter Marshal |
| Boss staff | Last Ember (white) | drops from the Winter Marshal |
| Robe | Snowshroud | |
| Light | Hoarstep | |
| Medium | Marcher's Mail | |
| Heavy | Rimeguard | NEW |

## What has to be built

- Weapons: 90 dungeon weapons, 28 exist (ported), 62 new (27 of them staffs, 9 shields, 9 bows).
- Boss weapons: 54, 7 exist (the old boss weapons), 47 new, each with an R skill.
- Armour: 36 sets (144 pieces), 8 exist (ported to EF meshes), 28 new (112 pieces).
- Code: the Gate Forge block and screen, drops on every mob, the 4 class stat profiles, spell power and mana, 3 spell schools.
- The Frozen Procession has only 3 monster kinds (frostbound, archer, Marshal); the rule is 5.
- Before the first gate, the smith sells plain starter gear of every type, including a starter robe, so nobody waits
  on iron.

## Forging (built 10/30, Smithing.java)

Gear is made by hand at the anvil: first step, three rounds of rhythm with the master, last step. Weapons and plate are
hammered, light armour and robes stitched. Crude -5%, Fine, Masterwork +5%, Perfect +10% and you name it.
Upgrades +1 to +10: 4% each, common + elite, trophies from +6, harder each +, a poor run wastes the drops, never the piece.
The Joining (the Cold Forge, not the Gate Forge): two boss weapons of a kind and rank + 10 common, 5 elite, 3 trophies of
the second's gate = that kind's Joined weapon, a rank up (D+D = rank C ... S+S = S+), 12% over a boss weapon of that rank,
every fifth blow bursting for 60% round the target. A Joined weapon + a boss weapon of at least its rank raises it, to S+.
Keeps the higher +. Joined weapons can't be upgraded at the Gate Forge. Each has its type's R skill (JoinedSkills.java, 20 s cooldown); boss weapons have none of their own. Unlock: Wendel, the vault under the armoury, an
Ember Shard from a rank E, D and C boss, Wendel binds them, press the First Ember to the stone (ColdForge.java). Once
lit it's lit for everyone in that world.
A Masterwork or better lets a smith make that piece for you at Fine. A friend can take the master's side of the anvil.
