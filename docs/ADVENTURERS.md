# Adventurers (world life)

Agreed 11/3: the guild's other hunters out in the world, for life, not story. They spawn round players, fight what's near,
camp, talk, and go when you've gone. Nothing about them is tracked except a death near you (the guild tag report, later).

## Built 11/3 (step 1: the entity, compiles, unseen in game)
- **Parties:** `tools/adventurers.py` rolls 16 parties (F to S, 66 adventurers) from the NPC forge's adventurer recipe,
  with an elf, dwarf or demon now and then and four parties mostly of one race (Thornbacks elves, Stonejaws and Ironwake
  dwarves, Ember Wake demons). `--sheet` renders the lineup (tools/renders/adventurers_v1.png), `--export` writes their
  bare cube meshes (no carried gear), npc_scales.json and `/ashbound/adventurers.json`.
- **Gear from the loot pools** (`Adventurers.dress`): armour class by role (tank/breaker heavy, blade/lancer medium,
  ranger/rogue light, mages robe), the rank's Gate Forge sets (odd pieces below C, whole sets from C), a found set 15% of
  the time, helmets on only 30%; the rank's forged weapon of the role's kind, a boss weapon 5%, a world weapon by rarity.
  Tanks carry a shield. All of it drops whole if they fall.
- **Fighting** (`Adventurer`, `AdventurerPatch`): melee swing their weapon's Epic Fight combos (MobMoves stances by
  weapon) from their own place round the target (front for the tank, then the sides, then behind; everyone attacks,
  no turn-taking). Rangers use the bow (keep ~16 off), black mages throw bolts of their staff's element, white mages
  heal whoever is under 70% (party or players), lowest first. Targets: monsters on players or on them first, then any
  monster in sight within 16. Monsters target them back.
- **Rules:** players can't hurt them and they can't hurt players (or each other); they regenerate out of a fight; gone
  after 30 s with no player within 112 blocks.
- **Command:** `/ashbound adventurers spawn [rank or party name]`, `/ashbound adventurers clear`.

## Built 11/3 (step 2: meeting them, 46/46 headless, unseen in game)
- **No roads** (our road generation is too buggy): whoever leads wanders anywhere, a spot 40-80 blocks off a little
  off their last heading, on dry ground, walked in 16-block legs, then a rest. If the leader falls the next one leads.
- **The spawner** (`Adventurers.tick/meet`): every 3-6 min out (first after 1-2 min), per party of players (six
  together meet them as often as one alone), 60-100 blocks off, more than 48 from everyone and out of their view
  (view cone + line of sight). At most 3 parties within 160. Overworld only.
- **What they're about:** in a town or village (Capital sites) 2-3 of a party idle round the plaza for good; out in the
  wilds at night half the time a **camp** (a real campfire, everyone round it facing in, the tank 6 out looking out;
  broken at sunup, the fire put out by the last to leave, a dead camp's fire stays lit); by an open gate within 140
  (35%) they stand about it 2-4 min then move on; otherwise 40% a **fight** (2-5 monsters of a gate of their rank already
  on them) or just walking.
- **Rank:** 60% yours (party rank), 18% one lower, 15% one higher, 7% two off; never a party already about.
- **Fixes:** black mage bolts lead a moving target (7 -> 31 damage in the fight test); tanks get Epic Fight stun armour
  (10 + 2/rank, others 2 + 0.5/rank) so the guard doesn't leave them stunlocked (0 -> 189).
- **Command:** `/ashbound adventurers meet [roam|fight|camp|gate|town]` forces one near you.

## Built 11/3 (step 3a: lines and talk, 47/47 headless, unseen in game)
- **Lines over their heads** (`Adventurer.bark/talk`, client `AdventurerBarks`): text on a dark band, 4 s, fading, heard
  within 20 blocks. One of a party at a time; each waits 20-40 s for small talk. When: going into a fight (tank taunts
  60%, others 25%), under 35% health, healing someone, a mate falling, a fight won (or thanks to the player who helped),
  nodding to a player the first time they come within 10 (by rank gap: higher / same / lower), small talk by rank tier
  (walk, camp, town). All lines in `src/main/resources/ashbound/adventurer_lines.json` (placeholders listed there).
- **Talking** (`AdventurerTalk`, the townsfolk's TalkScreen): right-click any of them; the whole party stops and looks at
  you for 10 s. Greeting by tier (or "you pulled us out of it" if you helped them); Who are you? (party, rank, count, how
  long together, who leads); Heard anything? (a real lead: nearest open gate with dir/distance/rank, a breakout or raid
  on the board, the nearest town; sometimes talk of an epic/legendary world weapon in a ruin, a rumour only); Good hunting.
  Not while fighting ("Not now!").

## Built 11/4 (step 3b: requests, unseen in game)
- About 1 party in 4 has a request (`Adventurer.ask`, rolled in `Adventurers.spawn`). Talk to any of them: "Need a hand
  with anything?" appears. They say what and the pay; "I'll do it" puts it in the Journal / guild card as a favour
  (`Errands`, giver `adv:<party>`, template `adv_<kind>`), "Not today" and they don't ask you again.
  - **Report**: carry their sealed report to Elowen's desk (compass points there). Pay x0.6.
  - **Fetch**: 3-5 of a gate's first material, or 1-2 of its second (a gate of their rank), left at the desk. x0.9 / x1.2.
  - **Camp**: monsters of their rank's gates dug in round a campfire 35-60 blocks off, out of sight and out of town
    (3-5, persistent, kept within 8 of the fire). The party sets off for it at a jog (`Adventurer.task`) and fights it
    with you. Kills by anyone count; the last one pays you on the spot, puts the fire out, and they say so. x1.3.
    In town a camp request becomes a fetch.
  - Pay: the favour table by THEIR rank, GP if you're registered, and half the time a find of your party's rank.
  - The desk turn-in: Elowen gets "I've a sealed report from the ..." / "The ... asked me to leave these with you."
  - Lines: `req_*` and `camp_cleared` in adventurer_lines.json.

## Next
- In-game look at lines, talk, meetings and requests.

## Later updates (agreed 11/4, kept for later)
1. **They come to help you**: a party within ~40 blocks when you're under a third of your health, or a mate's down with
   monsters on you, runs in; the tank pulls monsters off you, the white mage heals you; a line after, and they owe you.
   A party far below the threat's rank may run instead.
2. **Deaths and the Guild**: adventurers can die for good; Elowen mentions it next time; some leave a guild tag on the
   body. Hand it in at the desk for a small reward. The lie check: the Guild knows who was near, so "never saw them"
   when you did, or "tried to save them" when you didn't, gets remembered (Guild Points lost, a mark on your record).
3. **Party colours**: a cape or sash in the party's colour over the armour, to tell parties apart at a distance. A
   concept and a lineup sheet first.
