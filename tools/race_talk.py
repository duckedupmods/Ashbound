"""What the villages' races say: dwarfs of Anvilgate are blunt and proud, elves of Lumenhollow have long memories and
dry manners, demons of Hornsend (Highmourn's outcast quarter) are careful, tired and funnier than you'd expect.

Each person's conversation is rolled from their spec (tools/npc_specs): a greeting, who they are, their trade, their
people, and a rumour. {first} is their first name, {title} their trade. Written to tools/npc_talk (efmob --npc reads
it) and straight into the mod's data/ashbound/npc.

    python tools/race_talk.py          every dwarf, elf and demon in npc_specs
"""
import json
import os
import random
from pathlib import Path

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
SPECS = HERE / "npc_specs"
TALK = HERE / "npc_talk"
DATA = HERE.parent / "src" / "main" / "resources" / "data" / "ashbound" / "npc"

BACK = [{"text": "Something else.", "go": "start"}, {"text": "Goodbye.", "do": "close"}]

RACES = {
    "dwarf": {
        "greet": ["Mind your head. Actually, you'll be fine, it's the beams that should worry.",
                  "Boots off the good stone, tall one.",
                  "Hah. A surface walker. Lost, or buying?",
                  "You've the look of someone who's never held a proper hammer.",
                  "Hold's open to anyone with coin or manners. Which've you got?"],
        "people_q": "What's Anvilgate like?",
        "people": ["Nine hundred steps down to the deep forge and we count every one. Up here's just the porch.",
                   "Our grandmothers cut this gate with hand tools. Took sixty years. Nobody's said thank you yet.",
                   "Stone doesn't lie, doesn't rot and doesn't ask how your day went. Fine neighbours, stones.",
                   "Highmourn buys our iron and calls it theirs. Look at their gate hinges. Those are ours."],
        "other_q": "What do you make of the elves?",
        "other": ["Lovely folk. Live in a tree. On purpose.",
                  "An elf once told me my great-grandfather was 'a promising young man'. She meant it, too.",
                  "They sing to their timber. Timber burns. I'll say no more.",
                  "We trade them hinges, they send us lamp oil. Neither side says what it's really for."],
        "rumors": ["We broke through into something on the ninth level. Sealed it the same shift. Nobody's talking.",
                   "The Foundry gate's heat comes up through our deep shafts. Good for the bread. Bad for the sleep.",
                   "There's a seam of black iron that rings when you strike it, and something under it rings back.",
                   "An old crew went to the Gallows Hill for the rope iron. Came back with less crew.",
                   "The elves pay double for anything that came out of a gate. Ask yourself why."],
        "roles": {
            "miner": {"who": ["{first}. I dig. Fourth generation of diggers, and the fifth's already underfoot.",
                              "{first}, third shift. Ask me about the rock, not about the sky. Haven't seen it since spring."],
                      "q": "How's the digging?",
                      "a": ["Good iron, bad air. That's the wrong way round, but the pay's the same.",
                            "Timber's short, so we're propping with stone. Elves won't sell us the good beams at any price.",
                            "If your lamp goes blue, leave. Don't think about it, don't finish your sentence. Leave.",
                            "You can hear the mountain settle at night. New lads think it's snoring. Might be."]},
            "smith": {"who": ["{first}. If it's got an edge and it's worth owning, likely it came past this anvil.",
                              "{first}. Smith. Everyone's a smith in the Hold, but I'm the one they ask when it goes wrong."],
                      "q": "What makes a good blade?",
                      "a": ["Patience. A hot fire, then a cold head. Most folk get one of the two.",
                            "Listen to it. A bad blade sounds wrong before it looks wrong.",
                            "Gate-iron holds a heat for days. Won't fold, won't quench right. I'd love a bar of it.",
                            "Human smiths rush the temper. It's why their swords have such exciting lives."]},
            "guard": {"who": ["{first}. Hold Guard. I stand at the gate and judge your shoes.",
                              "{first}. Yes, it's a big door. Yes, I've got the key. No, you can't hold it."],
                      "q": "Anything to report?",
                      "a": ["Quiet above. Too quiet below. I prefer it the other way round.",
                            "Two caravans short this month. Road's bad past the ford.",
                            "We don't let what comes out of the gates into the Hold. That's the whole job. It's a good job.",
                            "Saw a horned fellow pay full toll last week, polite as you like. Strange days."]},
            "merchant": {"who": ["{first}. I sell what comes up and buy what goes down. Everyone needs a {first}.",
                                 "{first}, ore trader. Fair weights, fair prices, and no credit, ever."],
                         "q": "How's trade?",
                         "a": ["Coal's up, copper's down, and Highmourn still pays late.",
                               "A road would help. A real one. Mules don't care for mountains and neither do I.",
                               "Everything from a gate sells high till someone important dies holding it.",
                               "Reedmere wants nails, Stepcliff wants rope, everyone wants it yesterday."]},
            "child": {"who": ["I'm {first}! I'm nearly as tall as Grandfather's axe!",
                              "I'm {first}. I'm allowed to the third level. Only if someone's looking."],
                      "q": "What are you up to?",
                      "a": ["Grandmother says I'll get my first hammer when I can lift it. I can nearly lift it!",
                            "I found a crystal! It's a secret. It's in my boot. Don't tell!",
                            "Do you really sleep where there's no ceiling? Aren't you scared the sky'll fall off?",
                            "Elves are so tall! I asked one what the weather was like up there. She laughed for a week."]},
        },
    },
    "elf": {
        "greet": ["Welcome, little-lived one. Mind the moss, it was here first.",
                  "You walk loudly. It's all right. The Tree has forgiven worse.",
                  "Ah. Another visitor. The last one was only eighty years ago.",
                  "Peace on your road, traveller. Do wipe your boots.",
                  "The lanterns said someone was coming. They're usually right."],
        "people_q": "Tell me about Lumenhollow.",
        "people": ["The Tree was old when Highmourn was a ford and a bad idea. We only live on it. It tolerates us.",
                   "Nobody built these decks. We asked the boughs, and waited. It's a very different thing.",
                   "We keep the lanterns lit for those who went into the gates. It's been a while. We're patient.",
                   "Every ring of the Tree holds a song. We've sung as far back as the third hundred. It takes years."],
        "other_q": "What do you make of the dwarfs?",
        "other": ["Delightful. So busy. They go in and out of the mountain like bees with a grievance.",
                  "I knew the Hold's first founder. Short temper, short beard. She'd be appalled by the new gate.",
                  "They buy our lamp oil and never once ask what it's made from. It's the politest thing about them.",
                  "A dwarf told me stone doesn't lie. Stone doesn't do anything, dear. That's rather the point of it."],
        "rumors": ["The Silk Archive isn't a ruin. It's a record. Whatever wrote it would like it back.",
                   "The Rotwood used to sing. I remember it. What sings there now isn't the same voice.",
                   "When the gates first cracked, the Tree dropped every leaf in a night. It has done so only once before.",
                   "There's a road to the Fallen Moon in the old songs. We stopped singing that one. On purpose.",
                   "Something has been walking the outer boughs at dusk. It leaves no prints, and the moss doesn't mind it."],
        "roles": {
            "elder": {"who": ["I am {first}, Elder of the Tree. I've buried three of your kingdoms. They were nice, some of them.",
                              "{first}. I speak for the Tree, in that I'm old and nobody dares interrupt."],
                      "q": "What should I know, Elder?",
                      "a": ["That haste is only fear, wearing good boots.",
                            "That the gates opened before, and were shut before. Ask yourself who paid.",
                            "Highmourn's walls are very fine. Walls generally are, right up to the end.",
                            "Nothing, yet. Come back when you've lost something. You'll listen better."]},
            "herbalist": {"who": ["{first}. I mend what the forest will let me mend.",
                                  "{first}, of the herb rings. Don't touch the blue ones. Or the ones next to the blue ones."],
                          "q": "What grows up here?",
                          "a": ["Lamp-moss for wounds, silverleaf for fever, and patience for everything else.",
                                "Rot's creeping in from the east. It takes the bark first, then the birds go quiet.",
                                "Bring me anything from the Rotwood and I'll burn it. Politely. But I will.",
                                "The glow on the mushrooms is only pretty until you eat one."]},
            "lamplighter": {"who": ["{first}. I keep the lanterns. All nine hundred and twelve of them.",
                                    "{first}, Lantern Keeper. I'm told it's a calming job. I'm told that by people who aren't me."],
                            "q": "Why so many lanterns?",
                            "a": ["One for each who walked into a gate and hasn't walked out. We add to them. We don't take any away.",
                                  "Because the dark up here listens. It's better if it has something to look at.",
                                  "They burn lower near the new moon. We don't know why. Yes, it worries us.",
                                  "Please don't blow on it. People do. I don't know why people do."]},
            "singer": {"who": ["{first}. I keep the songs, the long ones, the ones with nine hundred verses.",
                               "{first}, Songkeeper. I'm on the fortieth year of the Lay of the Second Bough. It's going well."],
                       "q": "Will you sing something?",
                       "a": ["Certainly. It will take until spring. Do sit.",
                             "There's one about a human who came here and left quickly. It's short. It's a comedy.",
                             "Not today. The last time I sang that one, the river moved.",
                             "Every song is a map, if you've the patience. Most people want the short way round."]},
            "warden": {"who": ["{first}. Grove Warden. I watch the roots, and I'm watching yours.",
                               "{first}. If the arrows stop, it's because you were polite. Keep it up."],
                       "q": "Is the forest safe?",
                       "a": ["The forest is fine. It's you I'd worry for.",
                             "Things come down from the gates and they don't belong. We correct that.",
                             "Keep to the bridges after dark. The boughs below aren't all boughs.",
                             "I've seen rot-beasts walk past a sleeping child and stop to kill a sapling. Think about that."]},
            "weaver": {"who": ["{first}. I weave what the silkmoths give, and the moths give what they please.",
                               "{first}, Silk Weaver. This cloak took eleven years. No, you can't afford it."],
                       "q": "What makes elven silk so fine?",
                       "a": ["Time, mostly. You'd be surprised what time does for a thing.",
                             "The moths feed on the Tree. The silk remembers it. Wear it and you may have strange dreams.",
                             "Something's been buying up raw silk through Highmourn. A lot of it. I'd like to know who.",
                             "There's a pattern we don't weave any more. It kept getting finished by itself overnight."]},
            "child": {"who": ["I'm {first}! I'm only sixty-one, so I'm allowed to run on the bridges.",
                              "I'm {first}. I can whistle to the moths. Listen. Oh. They're asleep."],
                      "q": "What are you up to?",
                      "a": ["I'm learning the Lay of the Second Bough! I know verse one! It's very long!",
                            "A dwarf came and she was so short and SO loud and I liked her.",
                            "Are you old? You look old. You look like you might be nearly thirty.",
                            "I'm not allowed to the outer boughs. There's a thing there. It's nice, but I'm not allowed."]},
        },
    },
    "demon": {
        "greet": ["Yes, the horns are real. No, you can't touch them. Now, how can I help?",
                  "Welcome to Hornsend. Mind your purse, not because of us. The city's watch comes through here.",
                  "You stopped. Most walk faster. I'm grateful, in a suspicious way.",
                  "A human, on purpose? Are you lost, or are you the brave sort?",
                  "Keep your hand off that hilt and we'll get along fine. Everyone does, eventually."],
        "people_q": "What is Hornsend?",
        "people": ["Three streets under the wall that the city forgot it owned. So we moved in. It's ours now, more or less.",
                   "When the gates cracked, some of us ran out of them. Not to fight. Just to stop being down there.",
                   "We pay the tax, the double tax and the horn tax. The horn tax isn't a joke. I wish it was.",
                   "Nobody comes here by accident. Which is why everybody here is so glad of a customer."],
        "other_q": "How does the city treat you?",
        "other": ["We're allowed to sweep its streets and mend its drains. At night. Where nobody has to look.",
                  "The Guild will take our coin, but not our names. Elowen tried. I'll give her that much.",
                  "The children here don't know they're supposed to be afraid of us. It's the best part of the day.",
                  "Every time something crawls from a gate, somebody throws a stone at our door. We've built a very nice wall from them."],
        "rumors": ["What's behind the gates isn't an army. It's a landlord. It wants its tenants back.",
                   "We know what the seals at the gate mouths say. Nobody's asked us. Nobody ever asks.",
                   "An old demon on Ash Row says the first crack was opened from this side. He says it very quietly.",
                   "Someone in a good coat comes down here at night and pays well for old names. Ours, not his.",
                   "When a gate boss dies, every horn in Hornsend aches at once. We've learned to stop what we're doing."],
        "roles": {
            "fence": {"who": ["{first}. I find things. Don't ask where. It's more fun for you if you don't.",
                              "{first}. I buy what the shops won't touch and I've never once asked a question."],
                      "q": "What's for sale?",
                      "a": ["Whatever the gate-runners couldn't explain to the Guild.",
                            "Nothing's stolen. It's just had a very sudden change of owner.",
                            "I've a key that opens nothing yet. I'm told that's the expensive kind.",
                            "Quality goods. Ask anyone. Well, not anyone. Ask quietly."]},
            "cook": {"who": ["{first}. I cook. If you're squeamish, it's chicken.",
                             "{first}. Best stew in Highmourn, and I'll fight the Hearth Ward's inn over it."],
                     "q": "What's in the pot?",
                     "a": ["Pepper, mostly. We came from a hot place. Everything up here tastes of rain.",
                           "My grandmother's recipe. It's got no names in it you could say with your mouth.",
                           "It's safe for humans. Mostly. Have you been feeling brave?",
                           "Two guardsmen eat here every week. They come in by the back. Their secret's safe."]},
            "smith": {"who": ["{first}. I mend pots. I used to make other things. I make pots now.",
                              "{first}. They'd never buy a blade from me, so I sell it to someone who sells it to them."],
                      "q": "Where did you learn the trade?",
                      "a": ["Down there. We forged for something that never once said thank you. Pots don't ask much.",
                            "A dwarf came by, looked at my welds for an hour, said 'hm', and left. I've had that framed.",
                            "The trick is to work the metal cold. I've had enough of the other way.",
                            "Iron doesn't care what your face looks like. It's why I like it."]},
            "sweeper": {"who": ["{first}. I sweep the Hearth Ward. I've seen everything you've dropped.",
                                "{first}. City's lamplighters quit in winter. Guess who's been lighting them."],
                        "q": "How's the work?",
                        "a": ["Honest. Cold. They pay a third, and only look at me when something's missing.",
                              "You'd be amazed what a nobleman drops at midnight. I keep that to myself. For now.",
                              "Night shift's quiet. Good for thinking. Bad for thinking, too.",
                              "A little girl waved at me yesterday. Her mother pulled her away, but still."]},
            "elder": {"who": ["I'm {first}. I was somebody, once, in a place with a much better view of the fire.",
                              "{first}. I'm the oldest thing in Hornsend, and yes, that includes the drains."],
                      "q": "What do you remember?",
                      "a": ["Too much. It's the only thing we brought with us.",
                            "That we weren't always this. Nobody's born with horns who didn't sign for them.",
                            "We walked out in the dark, thirty of us, holding hands. Nobody up here would believe that part.",
                            "Sit a while. It's been a long time since anybody asked."]},
            "child": {"who": ["I'm {first}! I'm getting my second horn! Look! No, look closer!",
                              "I'm {first}. Are you a knight? Knights are scared of us. You don't look scared."],
                      "q": "What are you up to?",
                      "a": ["Racing the rats on Ash Row. The rats are winning. They've got more legs.",
                            "I was born up here! I've never even been down there! I like rain!",
                            "Why do people cross the road when they see my mum? She makes really good soup.",
                            "If you tie a ribbon on your horn, the city children will play with you. Sometimes."]},
        },
    },
}


def conv(sp):
    race = RACES[sp["race"]]
    role = race["roles"].get(sp["role"]) or race["roles"][next(iter(race["roles"]))]
    rng = random.Random(sp["seed"] + 7)
    first = sp["name"].split()[0]
    fill = lambda t: t.replace("{first}", first).replace("{title}", sp["title"])
    nodes = {
        "who": {"text": [fill(rng.choice(role["who"]))], "options": BACK},
        "trade": {"text": [fill(rng.choice(role["a"]))], "options": BACK},
    }
    opts = [{"text": "Who are you?", "go": "who"}, {"text": role["q"], "go": "trade"}]
    if sp["age"] != "kid":
        nodes["people"] = {"text": [rng.choice(race["people"])], "options": BACK}
        nodes["other"] = {"text": [rng.choice(race["other"])], "options": BACK}
        nodes["rumor"] = {"text": [rng.choice(race["rumors"])], "options": BACK}
        opts += [{"text": race["people_q"], "go": "people"}, {"text": race["other_q"], "go": "other"},
                 {"text": "Heard any rumours?", "go": "rumor"}]
    if sp["race"] == "dwarf" and sp["role"] == "smith":
        opts.insert(0, {"text": "Forge me something from the gates.", "do": "forge"})
    nodes["start"] = {"text": [fill(rng.choice(race["greet"]))], "options": opts + [{"text": "Goodbye.", "do": "close"}]}
    tags = [sp["recipe"], sp["role"], sp["age"], sp["sex"], sp["race"]]
    return {"name": sp["name"], "title": sp["title"], "tags": tags, "start": "start", "nodes": nodes}


if __name__ == "__main__":
    n = 0
    for f in sorted(SPECS.glob("*.json")):
        sp = json.loads(f.read_text(encoding="utf-8"))
        if sp.get("race") not in RACES:
            continue
        c = json.dumps(conv(sp), indent=1, ensure_ascii=False)
        (TALK / f.name).write_text(c, encoding="utf-8")
        (DATA / f.name).write_text(c, encoding="utf-8")
        n += 1
    print(n, "conversations")
