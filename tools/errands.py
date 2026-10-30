"""The favours townsfolk ask (Errands.java): data/ashbound/errand/errands.json.

Each is a little story round something slain, brought or carried. who: any of these NPC tags can ask it (a lead never
does). from/to: the asker's Guild rank it's for, 0 = F (unregistered counts as F). kill "@foes" takes a foe from FOES
at your rank. n: how many, from-to. mul: on PAY at your rank (coins, Guild Points). {n}, {target} in the ask.

    python tools/errands.py
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "resources", "data", "ashbound", "errand", "errands.json")

CHANCE = 0.3
# per rank F..SSS: coins and Guild Points for a plain favour; a little under what a board request of that rank pays
PAY = [[30, 15], [60, 30], [110, 60], [220, 120], [380, 200], [800, 400], [1500, 800], [3000, 1500], [6000, 3000]]
FOES = [
    ["minecraft:zombie", "minecraft:skeleton", "minecraft:spider"],
    ["minecraft:zombie", "minecraft:creeper", "minecraft:skeleton", "minecraft:husk"],
    ["minecraft:drowned", "minecraft:witch", "minecraft:creeper", "minecraft:stray"],
    ["minecraft:pillager", "minecraft:phantom", "ashbound:cinderhusk"],
    ["minecraft:enderman", "minecraft:pillager", "minecraft:blaze"],
    ["minecraft:wither_skeleton", "minecraft:evoker", "minecraft:enderman"],
    ["minecraft:wither_skeleton", "minecraft:ravager", "minecraft:evoker"],
    ["minecraft:ravager", "minecraft:wither_skeleton"],
    ["minecraft:ravager", "minecraft:wither_skeleton"],
]
ANY = 8
TOWN = ["townsfolk"]
L = []


def kill(id, who, title, hook, ask, thanks, n=(4, 8), mul=1.0, frm=0, to=ANY, target="@foes", gift=None):
    L.append(dict(id=id, who=who, title=title, hook=hook, ask=ask, thanks=thanks, n=list(n), mul=mul, to=to, gift=gift or [], kill=target, **{"from": frm}))


def bring(id, who, title, hook, ask, thanks, target, n=(4, 12), mul=0.8, frm=0, to=ANY, gift=None):
    L.append(dict(id=id, who=who, title=title, hook=hook, ask=ask, thanks=thanks, n=list(n), mul=mul, to=to, gift=gift or [], collect=target, **{"from": frm}))


def letter(id, who, title, hook, ask, thanks, tag, to_name, mul=1.2, frm=0, to=ANY, gift=None):
    L.append(dict(id=id, who=who, title=title, hook=hook, ask=ask, thanks=thanks, n=[1, 1], mul=mul, to=to, gift=gift or [], deliver=tag, to_name=to_name, **{"from": frm}))


# ---------------------------------------------------------------- the city and the villages
kill("pest_fields", ["farmer", "baker"], "Trouble in the Fields", "Oh, thank goodness. You've got a sword, haven't you?",
     "They've been coming down to the fields after dark. I've not slept in a week. Get rid of {n} {target} for me?",
     "I'll sleep tonight. Bless you.", gift=[["minecraft:bread", 6]])
kill("guard_short", ["guard"], "Short a Patrol", "You. You look like you can use that.",
     "We're two patrols short and I've {n} {target} too close to the road. Clear them and I'll see you're paid.",
     "Good work. I never saw you, and neither did the paperwork.")
kill("grudge", TOWN + ["merchant"], "A Small Grudge", "Could I trouble you? It's a little embarrassing.",
     "One of them chased me clean up a tree last week, in front of everybody. Kill {n} {target}. Any of them. It's the principle.",
     "That's better. I feel taller.", n=(3, 6))
kill("lost_dog", ["child"], "For Biscuit", "Are you a real adventurer?",
     "The monsters scared my dog and she ran off. She came back, but I'm still cross. Can you beat up {n} {target}? I've saved up.",
     "You're the best! I'm telling everyone!", n=(2, 4), mul=0.7, gift=[["minecraft:cookie", 3]])
kill("scholar_sample", ["scholar", "acolyte"], "A Matter of Study", "Ah, an adventurer. Perfect timing.",
     "I'm writing on how they behave when they're cornered. For that I need a few fewer of them. Say, {n} {target}.",
     "Fascinating. I shan't ask what it was like. Actually, I shall, but later.", gift=[["minecraft:experience_bottle", 3]])
bring("baker_wheat", ["baker", "farmer"], "Short on Flour", "You wouldn't happen to be heading past any farms?",
      "The mill's run dry and I've orders to fill. If you could find me {n} {target}, I'd pay above the market.",
      "You've saved my morning. Here, and take a loaf.", "minecraft:wheat", n=(12, 24), gift=[["minecraft:bread", 4]])
bring("merchant_leather", ["merchant"], "A Rushed Order", "Have you a moment? And a strong back?",
      "A buyer wants a shipment by the week's end and I'm short {n} {target}. Find them and we'll both do well.",
      "Just in time. A pleasure, as always.", "minecraft:leather", n=(6, 12))
bring("smith_iron", ["smith"], "Iron for the Forge", "You've the look of someone who goes where the ore is.",
      "Orders stacked to the rafters, and my iron's gone. {n} {target} would see me through the month.",
      "That's good iron. You've an eye.", "minecraft:iron_ingot", n=(6, 12), mul=1.1, frm=1)
bring("barmaid_sugar", ["barmaid"], "A Sweet Tooth", "Oh! Perfect. You look like you get about.",
      "We're out of the good stuff and the regulars are getting ideas. Bring me {n} {target} and the next one's on me.",
      "You're a lifesaver. Don't tell the cook.", "minecraft:sugar", n=(8, 16), gift=[["minecraft:honey_bottle", 2]])
bring("herbal_kit", ["acolyte"], "Bandages for the Shrine", "Forgive me, might I ask you something?",
      "We go through linen faster than the faithful bring it. {n} {target} would mean a great deal to the sick.",
      "May the road be kind to you.", "minecraft:string", n=(8, 16))
bring("child_flowers", ["child"], "Flowers for Gran", "Hey! Hey, you! Are you busy?",
      "It's my gran's birthday and I'm not allowed past the wall. Can you get me {n} {target}? They're her favourite!",
      "She's going to cry! The good kind!", "minecraft:dandelion", n=(3, 6), mul=0.6, gift=[["minecraft:cookie", 2]])
letter("town_letter", TOWN + ["merchant"], "A Letter to Anvilgate", "I don't suppose you're travelling north?",
       "My brother-in-law works the Hold. He doesn't write, so I must. Would you take this to any dwarf at Anvilgate? They'll pass it on, and pay you for the trouble. They always do.",
       "From who? Hah! Here, for your boots.", "dwarf", "any dwarf at Anvilgate", mul=2.0)
letter("guard_report", ["guard"], "Sealed Orders", "You there. Reliable, are you?",
       "This goes to any smith, sealed. Don't open it, don't ask. They'll pay on delivery.",
       "About time. Here's your coin. Off you go.", "smith", "any smith", mul=1.0)
letter("scholar_elves", ["scholar"], "A Query for the Elves", "Do you ever go near Lumenhollow?",
       "I've been asking the same elf the same question for eleven years. Please take this letter to anyone at the Tree.",
       "Ah. Tell them we'll reply in a decade or so. For your trouble.", "elf", "any elf at Lumenhollow", mul=2.0)

# ---------------------------------------------------------------- Anvilgate
kill("hold_shafts", ["miner"], "Things in the Shafts", "You. Tall one. Can you swing that thing?",
     "Lost a whole level to them last week. {n} {target}, gone, and the crew'll go back down. I'll stand you a drink as well.",
     "Hah! Not bad for someone with their head in the weather.", gift=[["minecraft:coal", 8]])
kill("hold_road", ["dwarf"], "Clearing the Pass", "Hold on. You've got the arms for it.",
     "The pass is thick with them and the mules won't go near. See off {n} {target}. We pay in good iron.",
     "Well struck. Here, this is honest metal.", gift=[["minecraft:iron_ingot", 3]])
bring("hold_coal", ["smith", "miner"], "Coal for the Deep Forge", "You. You got pockets?",
      "Deep forge eats coal like a dragon with a cough. {n} {target}. Don't dawdle.",
      "That'll keep her burning. Good.", "minecraft:coal", n=(16, 32))
bring("hold_copper", ["merchant"], "Copper, Quick", "A word, tall one, while there's a profit in it.",
      "Stepcliff wants rails and I'm short. {n} {target} and we'll split it the way I say.",
      "Fair weight. Rare, for a surface walker.", "minecraft:copper_ingot", n=(12, 24), frm=1)
bring("hold_ale", ["dwarf"], "A Dry Shift", "This is serious, so listen.",
      "The cellar's dry. The CELLAR. Bring {n} {target} so we can brew before the third shift finds out.",
      "You've saved more lives than you'll ever know.", "minecraft:wheat", n=(16, 24), gift=[["minecraft:iron_ingot", 2]])
letter("hold_hinges", ["dwarf"], "Invoice for the Elves", "You're heading somewhere with trees?",
       "They owe for forty hinges, and they've owed for sixty years. Hand this to any elf at Lumenhollow. Smile while you do it.",
       "Ah, the hinges. Do tell them we adore their urgency. For your trouble.", "elf", "any elf at Lumenhollow", mul=2.0)

# ---------------------------------------------------------------- Lumenhollow
kill("tree_wardens", ["warden"], "Thinning the Dusk", "Stay a moment. You move like one who's fought.",
     "They gather where the roots run thin. Remove {n} {target}. Quietly, if your kind can manage it.",
     "Adequately done. The Tree noticed.", gift=[["minecraft:arrow", 16]])
kill("tree_rot", ["herbalist", "elder"], "Before the Rot Spreads", "Wait. You've come from the east road, haven't you?",
     "They carry the rot on them. Each one that falls buys the forest another season. {n} {target}, if you would.",
     "That is one more season. Thank you, little-lived one.", gift=[["minecraft:golden_apple", 1]], mul=1.2, frm=1)
bring("tree_oil", ["lamplighter"], "Oil for the Lanterns", "Forgive me. Might you have a moment? Or a year?",
      "The lanterns run low and the moths are shy this season. {n} {target} would keep them through to spring.",
      "One more night for each of them. They'd thank you.", "minecraft:honeycomb", n=(4, 8), mul=1.0)
bring("tree_herbs", ["herbalist"], "Fresh Cuttings", "Your boots have been somewhere interesting.",
      "I've need of {n} {target}. Cut clean, not pulled. I'll know.",
      "Hm. Mostly cut clean. It will do.", "minecraft:fern", n=(6, 12), gift=[["minecraft:glistering_melon_slice", 2]])
bring("tree_wool", ["weaver"], "Thread for the Loom", "You're wearing that on purpose? Never mind. I've a request.",
      "Our silk won't dress everyone. Bring me {n} {target} and I shall see what I can do for your dignity.",
      "A start. Do come back in forty years.", "minecraft:white_wool", n=(8, 16))
letter("tree_song", ["singer"], "A Verse for the Hold", "Would you carry something for me? It's only a verse.",
       "A dwarf once asked me how a song ended, a long time ago. It's finished now. Please take it to any dwarf at Anvilgate.",
       "It took them how long? Hah! Fair enough. For your walk.", "dwarf", "any dwarf at Anvilgate", mul=2.0)

# ---------------------------------------------------------------- Hornsend
kill("horn_stones", ["demon"], "The Night Watch", "You stopped. Could I ask you something, then?",
     "They come up the drains at night, and when they do it's our doors that get stoned for it. Kill {n} {target} and I'll make sure Hornsend remembers.",
     "That's the first time anybody's done that for us. Thank you.", gift=[["minecraft:blaze_powder", 2]], mul=1.1)
bring("horn_soup", ["cook"], "Pepper for the Pot", "You've got a kind face. Unusual, up here.",
      "Nobody on the market will sell to me. If you'd buy {n} {target} and bring them here, the whole Row eats tonight.",
      "Sit, sit. It's safe. Mostly.", "minecraft:red_mushroom", n=(6, 12), gift=[["minecraft:rabbit_stew", 2]])
bring("horn_coal", ["sweeper", "smith"], "A Cold Quarter", "I wouldn't normally ask.",
      "The city's coal stops at the top of the steps. {n} {target} would see the old ones through the week.",
      "They'll never know who sent it. I will.", "minecraft:coal", n=(12, 24))
letter("horn_letter", ["demon"], "A Name for the Guild", "Would you carry a letter? It won't bite.",
       "It's only a name, for the register. It needs to reach any guard in the city, and they'll throw it away. But it'll have been delivered.",
       "From who? Hornsend? ...Fine. Here. Don't tell anyone.", "guard", "any guard", mul=1.5)

if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"chance": CHANCE, "pay": PAY, "foes": FOES, "list": L}, f, indent=1, ensure_ascii=False)
    print(len(L), "favours")
