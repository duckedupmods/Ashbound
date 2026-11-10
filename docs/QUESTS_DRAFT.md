# Quests remake: draft v2 (for approval)

Nothing is built yet. This version follows your notes:
- quests built from what we already have
- few vanilla ones
- courier runs in the cities
- "bring it to my son" quests
- a main quest of go-there-get-that steps with summonable bosses, the Mage, Astral Beings, and the King
- something for the water
- no Nether or End for now (the Blaze, Wither and Ender Dragon requests come off the board until then)

## The engine (small, needed by everything below)

Each quest chain is a JSON file with steps:

| step | does |
|---|---|
| `talk` | speak to a named NPC |
| `kill` | N of a monster; can require night, rain, ashfall, or "near X" |
| `find` | an item that's **only there while you're on the step**: in a named dungeon's boss chest, a tower's hoard, a structure's chest |
| `event` | an item from a world event: a meteor's finish, an ashfall-night drop (a chance per kill), a gate storm's loot fall, a legend's carcass |
| `deliver` | carry an item to a person, optionally **against the clock** |
| `boss` | beat a boss: once in the story, then again whenever you like with its summon item |
| `choice` | two answers; the chain remembers which |

The Journal (J) shows the step, and the compass points the way. A party shares its steps.

## Boss arenas (sigils)

Every main-story boss, beaten once, gives its **sigil**. Hand a sigil to **Veyra** in the guild hall, and she sends the
whole party (everyone near you, like the Ashen Ring) into **that boss's own arena**, somewhere in the void. When the
boss dies, or the party falls, everyone comes home with what they earned.

- **Each boss gets its own stage**, built for spectacle. The Blender Cycles concept comes first, then the build, the way
  the Ashen Ring was made. For example:
  - **Ossric:** a colossal dead forge floating in ash, with anvils the size of houses, a river of slag round the floor,
    and his chimney-stacks on the horizon.
  - **The Wreck-Mother:** a ring of broken galleons on a black sea under a storm. The floor is the deck of the biggest
    wreck, and waves wash over its edges.
  - **The Ashen Herald:** a burnt town square on a floating island, with ash falling forever and a red sky.
  - **The Astral Beings:** star-glass platforms in open space, with planets close enough to touch.
  - **The final boss:** designed with you.
- **The tech already exists**, from the Ashen Ring: its own dimension, chunk-by-chunk building with no freeze, the party
  teleport, returning home, spectating on death, and the wipe rule. Each arena is a shape plus its own lighting and sky.
- **Ossric first:** the Founder's Brand becomes his sigil. Veyra sends you to his forge-arena, and beating him there
  makes the Cold Forge accept you, so **fusion opens**. Rematches whenever you want, for his drops.
- Story first-kills also happen in the arenas: Veyra sends you once you've gathered the act's pieces.

## Five overworld bosses (new)

Five more bosses, fought **out in the world** whenever you like. Each has a summon item, crafted or found, that you
use on open ground away from towns. The item checks there's room first and says why if there isn't. They're
party-scaled, and each has its own drops. One per region and mood, for example the mountains, the deep forest, the
coast, the badlands, and the snow. Each one gets a concept for your yes first, the badass rule, and connect_check.

## Main quest: *The Five Fires*

The idea, kept short: the gates are cracks in a seal the first smiths lit long ago. Ashfall, meteors and storms are the
seal breaking. Each act sends you round the world to gather what's needed to light the next part again, and ends with a
boss who then becomes summonable.

| act | rank | steps (go there, do that) | ends with |
|---|---|---|---|
| **I. The Brand** | F→C | Close a gate (exists). Wendel's three shards from E, D and C gate bosses (exist). The First Ember (exists). Summon Ossric with the Brand, out of town. | **Ossric** → fusion forge opens |
| **II. The Drowned Fire** | C→B | The Archmage at the Arcanum: the second Fire lies under the sea. Get: the **Bell's Clapper** from the Tide Chapel (E dungeon); a **lens shard** from a meteor's heart (meteor finish); a **sea-chart** from a Tidal Towns harbourmaster after three of his jobs; **Old Harpoon's** harpoon (legend hunt on the coast). Dive to the **Sunken Fire** (new water structure, see below). | **The Wreck-Mother** (new sea boss) → sigil |
| **III. Ash in the Wind** | B | **5 ash-sigils** dropped by monsters on ashfall nights. **Storm-glass** from a gate storm's eye. The Horologe's escapement from the **Clockwork Spire** hoard. The **Jarl's horn** from **Rimeholt**. Light the third Fire on the Frozen Procession's road. | **The Ashen Herald** (new; the thing that walks in front of ashfall nights) → sigil |
| **IV. The Mage's Road** | A→S | **Veyra** joins the story: the last two Fires were taken *up*, out of the world. She opens **Astral Rings**: arenas like the Ashen Ring, but built of star-glass in the void. Each holds an **Astral Being** that keeps a star-ember. Three fights, one per ring, each needing a key from the world: the Countess's ring (Bloodmoon Court), the Minotaur's horn (Obsidian Labyrinth), the Keeper's lamp (Abyssal Lighthouse). | **3 Astral Beings** → sigils |
| **V. The King** | S→SS | With the star-embers you're called to **the King in the citadel** (the Lord's Keep). The audience, his story, and the truth of who first lit the Fires. He asks for one last thing: the **Crown Gate** under the keep, the oldest crack of all. | **The final boss** of the game (new, its own arena) |

The final boss and the King's twist are to be designed together with you. Every new boss and its arena (the Wreck-Mother, the Ashen Herald, the 3 Astral Beings, the final boss, and Ossric's
forge) gets a Cycles concept for your yes first. Bosses follow the badass rule and get connect_check.

## The water (new)

- **Tidewrack monsters**, our own, in oceans, beaches and rivers, built the way we built Haunts, with 5 of them, for example:
  - a crab-thing wearing a ship's hull
  - lantern eels in the dark water
  - a drowned bosun with a boarding hook
  - a net-witch who drags players under
  - a reef-knight grown into coral
- **Sunken structures** of ours: wrecks with their own loot, a drowned watchtower, and the **Sunken Fire** for Act II.
  Our weapon pool also goes into the vanilla ocean ruins and shipwreck chests.
- **The Wreck-Mother**: a colossal sea boss with a sunken galleon for a shell. It's the Act II boss, fought in its
  wreck-ring arena.
- **Tidal Towns** villages get their own errands: fishers, harbourmasters, divers.
- A sea **meteor**: one that falls into the sea opens a flooded crater you dive into.

## Side quests

**From our own content (most of them):**
- **Gates:** "close the crack by the mill before it spills" (the gate nearest a village), and "bring me the Mossking's
  heartwood".
- **Legends:** a hunter's widow wants Old Blackbriar's thorn, a ploughman wants the Red Plough stopped before
  harvest. These use the bounty and trophy system that already exists.
- **Meteors:** "a shard fell on my field, get the glass out before the Guild claims it" (shardglass delivery).
- **Ashfall nights:** "my son is still out at the farm, bring him home before dawn" (an escort-lite: he follows you), and
  "keep the shrine brazier lit until morning".
- **Gate storms:** "bring me storm-glass, the Arcanum pays double".
- **Our monsters:** the custom-monster requests stay (Cask Mother, Gibbet Knight, Mourners, the Sexton, Thorns and the
  rest).

**Courier runs ("uber"):** someone in Highmourn (or a village) hands you a parcel for someone else. The compass points the way,
there's a timer, and you get a tip for speed. There are lots of small, funny ones: love letters, a cake, a smith's
sealed order, a lost cat in a basket. Some go between towns along the roads. They'd be the busy little filler of city life.

**"Bring it to my…":** kill or find something, then take it to a relative somewhere else, who has their own line and
reward. For example: "My boy's at the Hold, give him his father's knife", or "Mum's at Lumen, she'll want to know it's
dead: bring her its fang."

**A few vanilla ones stay:** the silk-and-spiders quest at Tanners' Lane and the East Yard zombies, each with a
named finale.

## Build order

1. The chain engine, the arena system (sigils → Veyra → the boss's arena), and **Ossric's forge-arena** (concept first)
   so fusion works. **First.**
2. Courier runs, "bring it to my…", and the event and legend side quests, so the world fills up fast.
3. The water: Tidewrack monsters and wrecks, then the Wreck-Mother concept. That gives Act II.
4. Act III (the Ashen Herald concept).
5. Act IV (Astral Ring look plus 3 Astral Beings concepts).
6. Act V (the King, the Crown Gate, the final boss; designed with you).
