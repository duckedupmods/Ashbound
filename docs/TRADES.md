# Trades (secondary skills)

Status: BUILT 11/3 (see below); first agreed in talk 11/2. No minigames: discovery benches for Cooking/Brewing/Alchemy; Smithing and Tailoring stay on the Gate Forge (duet, known recipes) with XP and perks.

## Built 11/3 (compiles, headless test passes, unseen in game)

- Trades.java holds everything: the 8 trades, 96 perks (the perk lists in Trades.java are the truth; they replaced the
  first lists below where those weren't buildable yet, such as Vein Sense, trainers and the Stockpot), 34 goods + 3 misses,
  the bench menu, XP sources, buffs, the forge hooks. ModVillages.java puts our races in other mods' villages.
- Levels 1-50, XP to next level 40 + 12*L. Trade points: 1 per level gained in any trade, at most 60. Perk tiers cost
  1/2/2/3 and need trade level 5/15/30/45, each after the one above it in its branch. Forget all perks: 150 coins.
- Benches: sneak + empty hand on any block whose name says stove / cooking_pot / campfire / smoker / oven... (Cooking),
  keg / barrel / brew / cask / ferment... (Brewing), brewing_stand / cauldron / alembic / alchemy... (Alchemy).
  5 slots, every item used; the kinds of what's in are shown (Meat, Herb...), quality odds, a recipe book that refills the
  slots from your pack. A recipe above your level fails with a hint of the level. Start known: Trail Jerky, Hearthbread,
  Highmourn Ale, Night-eye Drops.
- Buffs: one meal, one brew, one elixir at a time (two elixirs with Twin Elixir). Stats go through Passives.stat (new keys
  dig% and fall% are attributes now). Quality x0.7 / 1 / 1.2 / 1.4, happy accident x1.25 and 1.5x as long. Brews' catches
  aren't scaled by quality, Clear Head and the rest shrink them.
- XP: craft 18 + 4/item + level/2 (+60 first time), miss 4; ore 10, stone 1 in 8, ripe crop 4, flowers, breeding 8, fish 25,
  forge piece 45 + 8/rank, upgrade 30 + 8/rank, the mods' own cooking 2-3.
- Forge: Smithing (weapons, heavy/medium) or Tailoring (robes, light) by the piece: level x0.003 + perks on the roll,
  material cuts, ember savings, spare pieces.
- Tab: Trades between Skills and Journal. Commands: /ashbound trade reset|xp|learnall PLAYER, /ashbound village here.

## Strength and fatigue (11/3, second pass)
Scored with balance.py's worth scale (1 = about 1% damage or survival): a meal goes from about 3 (level 1) to 10 (level 25),
a brew 2 to 7.6 net (its catch is on move speed or health, which every build uses), a combat elixir about 7-8.
Quality Crude 0.8 / Fine 1 / Masterwork 1.1 / Perfect 1.2; a happy accident x1.1 strength, x1.5 time. Power perks 5%.
Mending heals 15% of max health, the Mana Draught gives 35% of max mana. Strong buffs, but not all the time:
- **Meals, tired of it:** the same dish again soon is 100/70/45/25%; one time wears off every 20 min (10 with Highmourn Table).
- **Brews, tipsy:** the second brew in 10 min = tipsy (-5% move, mild camera sway); the third = drunk (-10% move,
  -20% stamina regen, no sprinting, more sway). Hard Head moves both one brew later.
- **Elixirs, toxicity:** each adds toxicity (combat 40-55, mending/mana 25, utility 0-10), limit 100, drains in 12 min.
  Up to three different elixirs run at once. Over the limit: Weakness and 2% max health lost every 2 s (never below 1)
  until it drains. Hardened Blood +25 limit, Tempered Blood drains 50% faster. A bar left of the armour shows it.

## How it works

- 8 trades, each with its own level 1-50 from XP earned by doing it.
- Every trade level gained gives 1 **trade point**, shared across all trades, at most **60** in total.
  A trade's tree costs 25 points to max, so a player can master about 2 trades or spread over 4.
  A perk also needs its trade's level (rows open at levels 5 / 15 / 30 / 45).
- Reset all trade points at the guild for coins (levels stay).
- Ranks by level: Novice 1, Apprentice 10, Journeyman 20, Expert 30, Master 40, Grandmaster 50.
  The rank shows on the Trades tab of the Character screen and as a title.
- Quality: Crude / Fine / Masterwork / Perfect, rolled from the trade level and perks.
  Quality scales an item's buff (Crude -30%, Fine normal, Masterwork +20%, Perfect +40%). Perfect items carry the maker's name.

## Two kinds of crafting

**Discovery benches (Cooking, Brewing, Alchemy):** our own block with a window: up to 5 ingredient slots and Craft.
You don't know what comes out. A hit writes the recipe into your Recipe Book (then it can be made on purpose,
quantity box); a miss gives Burnt Mush / Sour Wash / Fizzled Draught and the ingredients are gone. Rare
**happy accidents** turn a craft into a better version with an extra effect. Trainers and found notes give hints
("something sweet with the frost-fish..."). Ingredients come from Farmer's Delight and the Let's Do mods; their own
pots, ovens and barrels keep working as they are.

**Gate Forge (Smithing, Tailoring):** unchanged: known recipes from the gate tabs, the Strike with the Master duet.
Forging and upgrading give trade XP; perks make it better.

## The 8 trades and their perks (3 branches of 4 each)

### Cooking - Cook's Table
- **Feast:** Shared Plate (meals also feed party members within 8 blocks) / Long Simmer (+50% buff time) /
  Banquet (craft a feast block: 6 servings, party buff 20 min) / Highmourn Table (feasts give one extra buff).
- **Flavour:** Seasoned (+10% buff strength) / Second Taste (20% a meal rolls a second buff) /
  Keen Palate (hints show which ingredient a recipe is missing) / Signature Dish (Perfect meals +25% more).
- **Thrift:** Leftovers (15% an ingredient isn't used) / Double Batch (10% double output) /
  Field Cook (cook at any campfire, up to Fine) / Stockpot (meals stack to 64).
- Meals: health regen, max health, stamina, poise, mana, resistances per gate element, mining speed.

### Brewing - Brewer's Vat
- Brews are short, strong fight buffs with a catch (ale: +poise, aim sways; mead: +damage, -defence; herbal tea: mana regen, slower).
- **Strength:** Stout Heart (+15% brew effect) / Barrel Aged (leaving a brew in the vat longer raises quality odds) /
  Liquid Courage (brews also give fear immunity) / Legendary Cask (Perfect brews last twice as long).
- **Steadiness:** Clear Head (catches halved) / Iron Gut (no nausea ever) / Steady Hands (no aim sway) /
  Toast (a brew drunk near the party gives them half its effect).
- **Tavern:** Tavern Price (+30% sell price) / Cask Master (3 per batch) / House Brew (name your own recipe) /
  Regulars (innkeepers buy anything you make, guild requests pay more).

### Alchemy - Alchemy Table
- **Elixirs:** gate resistances (frost, plague, ember, void...), each 10 min; Potent (+20%) / Lasting (+50% time) /
  Twin Elixir (drink two at once) / Philosopher's Draught (rare: all resistances at half strength).
- **Oils & bombs:** weapon oils (fire, frost, holy vs undead, venom) / Fuse (bombs) / Coat Twice (oils last 2x hits) /
  Grenadier (bombs throw farther, bigger blast).
- **Remedies:** Better Potions (healing potions +25%) / Antidote (cures gate afflictions) / Field Medic (potions on
  allies by throwing) / Last Breath Tonic (rare: survive one killing blow).

### Smithing - Gate Forge (weapons, heavy and medium armour)
- **Craft:** Steady Rhythm (duet windows +15%) / Master's Eye (+Masterwork and Perfect odds) /
  Signature Blade (Perfect weapons +5% damage) / Own Pattern (make any Masterworked item at Fine without the duet).
- **Upgrades:** Tempered (+1 upgrade score) / Cheap Steel (upgrades cost 20% less) / Trophy Smith (trophy
  upgrades from +5 instead of +6) / Fusion Master (fusion keeps quality).
- **Road:** Whetstone (repair gear anywhere) / Salvage (break gear for half its mats) / Thrifty Smelt (10% mats back) /
  Dwarven Secrets (needs a dwarf trainer: +3% duet score).

### Tailoring - Gate Forge (robes, light armour) + Tailor's Frame
- **Craft:** Fine Stitch (+quality odds) / Ward Runes (robes +5% spell power) / Second Skin (light armour +3% speed) /
  Signature Weave (Perfect robes and light armour get a minor ward).
- **Gear:** Cloaks (craft cloaks: small resistances) / Dyes (recolour armour) / Deep Pockets (bag +1 tab) /
  Banners (party banner block: +5% damage near it).
- **Road:** Patchwork (repair cloth/leather anywhere) / Unpick (break cloth gear for mats) / Thrift (10% cloth back) /
  Elven Pattern (needs an elf trainer: robes regen mana faster).

### Farming - crops, herbs, animals
- **Fields:** Green Thumb (crops grow faster near you) / Rich Harvest (+1 drop 25%) / Rare Seeds (rare crops for
  top recipes) / Harvest Moon (whole field ripens once a day).
- **Herbs:** Herb Sense (rare herbs glow when near) / Careful Pick (herbs drop 2) / Gate Herbs (herbs inside gates) /
  Greenhouse (herbs grow in any biome in your garden).
- **Beasts:** Herdsman (animals breed faster) / Good Milk (better animal goods, more quality) / Mount Feed (craft
  feed: mounts train faster) / Beast Friend (pets gain XP faster).

### Fishing - rod (Lili's Lucky Lures if it fits)
- **Catch:** Patient (bites 20% faster) / Big Catch (bigger fish, more food) / Treasure (junk chests and coins) /
  Legend Fish (rare named fish per biome).
- **Gates:** Gate Waters (fish inside gates: frost-fish, ember eel...) / Trophy Fish (mount a big one on your wall) /
  Lucky (+gate-fish odds) / Abyss Line (fish up a gate key fragment, very rare).
- **Rest:** Calm Waters (fishing restores health and mana) / Bait Maker / Net (fish from a boat, 2 at once) /
  Fisher's Tale (fishing requests pay double).

### Mining - ores, stone, gate ore
- **Veins:** Vein Sense (nearby ore glows for 5 s, cooldown) / Rich Vein (+1 ore 20%) / Gate Ore (rare gate-metal
  veins in the world, not only in gates) / Mother Lode (a vein sometimes runs on: the whole vein drops).
- **Stone:** Quarry (stone-type blocks mine 25% faster) / Clean Cut (stone drops as itself) / Gem Eye (gems from
  stone, for relics) / Dwarven Pick (needs a dwarf trainer: mining speed +15%).
- **Delve:** Deep Breath (no slow underwater/in caves) / Lantern (light around you underground) /
  Cave Sense (see nearby caves on the minimap) / Tunnel Rat (fall damage -50%).

## Trainers by race (village and capital NPCs)
- Dwarves: Smithing, Mining. Elves: Alchemy, Tailoring, Farming herbs. Demons: Brewing, fire cooking.
  Humans: Cooking, Fishing, Farming.
- A trainer gives the rank-up trial at levels 10 / 20 / 30 / 40 (a delivery of crafted goods at a quality),
  sells hints and a few recipe notes, and unlocks the race perks.

## Trade requests
- New board section at the guild: "the inn needs 12 stews (Fine+)", "the guard needs 20 antidotes before the Plague
  Ward". Coins + trade XP; higher quality pays more. Shops buy Masterwork goods at much more.

## Open
- Can a player max every trade over time, or only about 2 (the shared 60-point cap above)? Not decided.

## Later (Christmas update): the lost village
Manor Row is dropped. Instead a quest chain ends with reclaiming a ruined village abandoned after the 10-gate incident:
clear it, the waystone is restored, a mansion, villagers move in and ask for buildings, town management. Not now.
