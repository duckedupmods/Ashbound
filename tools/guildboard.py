"""The Guild's board beyond the hand-written requests: gates of every rank, the towers and the old horrors of the Cataclysm.
Each one's a file in data/ashbound/quest (only ours, prefixed board_, are rewritten). Raids on villages and bosses that
get out aren't here: those come up by themselves as the game runs (Incidents.java).

    python tools/guildboard.py
"""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "src/main/resources/data/ashbound/quest")
RANKS = "FEDCBAS"
GATE_POINTS = dict(zip(RANKS, (40, 80, 150, 300, 550, 900, 1500)))
GATE_COINS = dict(zip(RANKS, (60, 110, 200, 380, 650, 1100, 2000)))
GATE_ASH = dict(zip(RANKS, (30, 60, 110, 200, 340, 520, 800)))

GATE_TEXT = {
    "F": ("A Crack by the Road", "A crack's opened where the carts go. Nothing in it should trouble you for long. Close it before something walks out."),
    "E": ("Close It Before Dark", "The farms have seen a gate in the fields, and the lights in it aren't lanterns. Go in and put down what rules it."),
    "D": ("Not for Beginners", "Rank D, and three parties turned back. Close it."),
    "C": ("A Gate That Bites", "The Guild has lost people to this one. Take a party, take vials, and come back."),
    "B": ("The Deep Ones Open", "A gate of this rank doesn't close itself, and it doesn't stay quiet. Go through."),
    "A": ("By Order of the Guild Master", "Halvard wants this one shut, and he doesn't ask twice."),
    "S": ("What Nobody Came Back From", "Nobody on the board has finished one of these and written down what's inside. Be the first."),
}

TOWERS = [
    ("warlords_fang", "gorrak", "The Warlord's Fang", "C", "minecraft:iron_axe",
     "Gorrak's orcs raid from the Fang and go home to count the heads. Climb it, floor by floor, and take his off him."),
    ("clockwork_spire", "grand_horologe", "The Clockwork Spire", "C", "minecraft:clock",
     "It keeps winding itself, and what it winds comes out and walks. Stop the Grand Horologe at the top."),
    ("serpent_ziggurat", "coiled_king", "The Serpent Ziggurat", "C", "minecraft:emerald",
     "Hunters who go near come back with bites that don't close. The Coiled King holds the top of the steps. Kill it."),
    ("rimeholt", "jarl_hrimgar", "Rimeholt", "B", "minecraft:packed_ice",
     "The cold coming off Rimeholt reached the road this year. Jarl Hrimgar won't come down, so go up."),
    ("glass_minaret", "djinn_sultan", "The Glass Minaret", "B", "minecraft:glass",
     "Traders have started seeing it from three deserts at once. Climb it and end the Djinn Sultan's reign."),
]

# overworld and elsewhere: the boss, its name, where it lives, the rank the Guild puts on it
OVER, NETHER, END = "minecraft:overworld", "minecraft:the_nether", "minecraft:the_end"
CATACLYSM = [
    ("the_harbinger", "The Harbinger", "ancient_factory", OVER, "A", "minecraft:redstone_block",
     "An old works has started up by itself. What's running it has been waiting a long time for something to shoot."),
    ("ancient_remnant", "The Ancient Remnant", "cursed_pyramid", OVER, "A", "minecraft:sandstone",
     "Grave-robbers opened a pyramid and only the sand came back. Something very large and very dead is in there."),
    ("maledictus", "Maledictus", "frosted_prison", OVER, "A", "minecraft:blue_ice",
     "A prison in the ice, and its one prisoner isn't asleep. Don't let it find the door."),
    ("the_leviathan", "The Leviathan", "sunken_city", OVER, "S", "minecraft:heart_of_the_sea",
     "Sailors have stopped going near the drowned city. Whatever's under it has started to come up. You'll want to breathe water."),
    ("scylla", "Scylla", "acropolis", OVER, "S", "minecraft:lightning_rod",
     "Storm without end over an old acropolis on the water. The ships that went to look never came home."),
    ("netherite_monstrosity", "The Netherite Monstrosity", "soul_black_smith", NETHER, "S", "minecraft:netherite_ingot",
     "Someone forged this in the Nether and lost control of it. Wendel says he'd like to see the workmanship. He means after."),
    ("ignis", "Ignis", "burning_arena", NETHER, "S", "minecraft:blaze_powder",
     "A burning arena in the Nether, and a knight in it who's still waiting for a fair fight. Give it one."),
    ("ender_guardian", "The Ender Guardian", "ruined_citadel", END, "S", "minecraft:purpur_block",
     "Beyond the End, a ruined citadel, and what still stands watch over it. Nobody's paying you to come back quickly."),
]


def write(name, **q):
    json.dump(q, open(os.path.join(OUT, "board_" + name + ".json"), "w", encoding="utf8", newline="\n"), indent=1, ensure_ascii=False)


def main():
    for f in os.listdir(OUT):
        if f.startswith("board_"):
            os.remove(os.path.join(OUT, f))
    n = 0
    for rank, (title, text) in GATE_TEXT.items():
        write("gate_" + rank.lower(), title=title, rank=rank, text=text, gate=rank, what="Rank %s Gate" % rank, count=1,
              points=GATE_POINTS[rank], coins=GATE_COINS[rank], ash=GATE_ASH[rank], icon="minecraft:ender_eye")
        write("gates_" + rank.lower(), title="Three Rank %s Gates" % rank, rank=rank, text="The board's overflowing. Close three of them and the Guild pays over the odds.",
              gate=rank, what="Rank %s Gates" % rank, count=3, points=GATE_POINTS[rank] * 4, coins=GATE_COINS[rank] * 4, ash=GATE_ASH[rank] * 4, icon="minecraft:ender_eye")
        n += 2
    for kind, boss, title, rank, icon, text in TOWERS:
        write("tower_" + kind, title="Clear " + title, rank=rank, text=text, kill="ashbound:" + boss, count=1, locate="ashbound:" + kind,
              points=GATE_POINTS[rank] * 2, coins=GATE_COINS[rank] * 2, ash=GATE_ASH[rank] * 2, icon=icon)
        n += 1
    for boss, name, where, dim, rank, icon, text in CATACLYSM:
        write("cataclysm_" + boss, title=name, rank=rank, text=text, kill="cataclysm:" + boss, what=name, count=1, locate="cataclysm:" + where, dim=dim,
              points=GATE_POINTS[rank] * 2, coins=GATE_COINS[rank] * 3, ash=GATE_ASH[rank] * 2, icon=icon)
        n += 1
    print(n, "requests")


if __name__ == "__main__":
    main()
