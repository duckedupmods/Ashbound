"""The quest book (FTB Quests) from a plain list: each quest watches one of the silent advancements Story.java grants,
or holds an item, so the book only shows the game's own progress. Ids come from the quest's key, so progress survives a
rewrite of the text.

    python tools/questbook.py   -> run/config/ftbquests/quests/
"""
import hashlib
import json
import os
import shutil

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "run", "config", "ftbquests", "quests")


def uid(key):
    h = hashlib.sha1(("ashbound:" + key).encode()).hexdigest()[:16].upper()
    return ("7" + h[1:]) if h[0] in "89ABCDEF" else h     # a positive long


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def snbt(v, ind=0):
    pad, inner = "\t" * ind, "\t" * (ind + 1)
    if isinstance(v, dict):
        if not v:
            return "{ }"
        return "{\n" + "".join("%s%s: %s\n" % (inner, k, snbt(x, ind + 1)) for k, x in v.items()) + pad + "}"
    if isinstance(v, (list, tuple)):
        if not v:
            return "[ ]"
        return "[\n" + "".join("%s%s\n" % (inner, snbt(x, ind + 1)) for x in v) + pad + "]"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return "%sd" % v
    if isinstance(v, int):
        return str(v)
    return q(v)


def adv(path):
    return {"type": "advancement", "advancement": "ashbound:" + path, "criterion": ""}


def item(iid, n=1):
    return {"type": "item", "item": {"count": 1, "id": iid}, "count": n, "consume_items": False}


CAST = {e[0]: e for e in json.load(open(os.path.join(ROOT, "src/main/resources/data/ashbound/capital/cast.json"), encoding="utf8")) if e[0][0] != "@"}
VAULT = (-125, -50)


def at(place):
    """The compass code for an NPC's post in the city, or a spot there."""
    x, z = (CAST[place][3], CAST[place][5]) if isinstance(place, str) else place
    return "at:%d,%d" % (x, z)


def done(path):
    return adv("story/" + path)


def step(key, title, icon, task, text, where, who="", say=(), reply="Go on.", reach=0, rewards=()):
    """One step of the story: each opens when the one before it is done. With `who`, it's done by speaking to them (they
    say `say`); with `reach`, by coming that close to `where`."""
    return dict(key=key, title=title, icon=icon, task=task, text=text, where=where, who=who, say=list(say), reply=reply, reach=reach, rewards=rewards)


def meet(key, title, icon, who, text, say, reply):
    return step(key, title, icon, done("meet_" + key), text, at(who), who, say, reply)


def visit(key, title, icon, place, reach, text):
    return step(key, title, icon, done("reach_" + key), text, at(place), reach=reach)


STORY = [
    ("the_road", "The Road to Highmourn", "minecraft:compass", "You came out of a crack in the world with nothing. Find the city.", [
        step("capital", "Find Highmourn", "minecraft:compass", done("capital"),
             "You woke in the ash with the clothes on your back and a crack in the world closing behind you. Every road in these lands runs to one city, and it's a long way off. Follow the compass and the roads. You'll know the walls when you see them.", "capital"),
        visit("gate_of_oaths", "The Gate of Oaths", "minecraft:iron_door", (0, 175), 18,
              "Highmourn's south gate stands open to anyone who'll keep the peace inside it. Walk in."),
        meet("dunstan", "A Bed and a Word", "minecraft:red_bed", "innkeeper",
             "A stranger's first stop is the Pilgrim's Rest, on the green west of the High Street. Ask Dunstan Pell what's being said.",
             ["You've the look of someone the road spat out. Sit. The first one's on the house, and so is this.",
              "Highmourn feeds people who work. See the market so you know what things cost, then get up to the guild hall and ask for Elowen."],
             "Thanks, Dunstan."),
        visit("market", "The Market", "minecraft:emerald", (-30, 92), 16,
              "Follow the High Street to the fountain. Everything in this city that can be sold is sold here, and the waystone by it will bring you back from anywhere. Touch it. Every village has one too."),
        visit("guild_square", "The Guild Square", "minecraft:white_banner", (0, -91), 14,
              "Stair Street and the grand stair take you up the bank to the Guild Square. The hall is the one with the clock."),
        step("guild", "Sign the Guild's Register", "minecraft:writable_book", done("registered"),
             "Elowen keeps the register at the first desk in the Hall of Quests, the guild hall's west wing. Nobody fights the gates without a card.", at("receptionist")),
        meet("halvard", "Behind the Desk", "minecraft:shield", "guild_master",
             "Elowen says the Guild Master wants a look at anyone new. Halvard Saltblood is across the hall.",
             ["So you're the one the road spat out. Elowen has you down as F. That's fair.",
              "Hear me. The gates are opening faster than I can close them, and I've buried better than you. Read the board. Then walk this city and meet the people holding it up. You'll need every one of them."],
             "Where do I start?"),
        step("board", "The Gate Board", "minecraft:paper", done("board"),
             "Ask Elowen to show you the requests. They're how the Guild pays, and how your rank climbs.", at("receptionist")),
    ]),
    ("know_the_city", "Know the City", "minecraft:filled_map", "Halvard's orders: learn who keeps Highmourn standing.", [
        meet("brann", "The Quartermaster", "minecraft:chest", "quartermaster",
             "Brann Holt sells the Guild's kit, just east of the square.",
             ["Halvard sent you? Then you're short of everything.",
              "Coin buys from me, and the Guild pays coin for requests. Ash is another matter: Ash is for the Tree, not my shelves. Press K when you've got some. Now go and see Garrick in the yard, before you hurt yourself."],
             "Understood."),
        meet("garrick", "The Training Yard", "minecraft:bow", "hunter",
             "Garrick runs the butts in the training yard, west of the square.",
             ["Easy. Halvard's stray, is it?",
              "I hunt what comes out of the gates so the farms don't have to. Your guard and your feet keep you alive in there. Learn them here, on something that can't kill you. Then see Hesta. A good arm's wasted on bad steel."],
             "I'll go."),
        meet("hesta", "The Gatesmith", "minecraft:iron_chestplate", "smith",
             "Hesta Kell keeps the smithy on the terrace, west of the yard.",
             ["What falls out of the gates, I make into what goes back into them. Plain work, done right.",
              "The great work's down in the Ashforge with Wendel. He'll want to see you."],
             "On my way."),
        meet("wendel", "The Ashforge", "ashbound:smith_hammer", "forgemaster",
             "Wendel Blackwood is Forgemaster of the Ashforge, in the west of the lower city.",
             ["Stand back from the sparks. Hesta sends me everyone who's never held a hammer. Fine.",
              "Bring me what a gate drops and you'll strike with me, and the piece will be as good as your timing. Not before. Now, if you've the stomach for it, there's someone at the Rat's Nest who knows what the Guild doesn't."],
             "I'll find them."),
        meet("rook", "The Rat's Nest", "minecraft:rabbit_foot", "fence",
             "Rook keeps a door in the Hearth ward that most people walk past.",
             ["Never met you. Neither of us was here.",
              "I buy what the Guild doesn't ask about and I hear what it doesn't want heard. West of here there's a quarter this city pretends it hasn't got. Walk it once. Keep your hands where they can see them."],
             "Noted."),
        visit("hornsend", "Hornsend", "minecraft:goat_horn", (-161, 39), 16,
              "The demons Highmourn won't house live in Hornsend, at the city's west end. Walk through it. They've done you no harm."),
        meet("wenna", "The Phial-Keeper", "minecraft:glass_bottle", "alchemist",
             "Wenna Morrow keeps the apothecary by the market.",
             ["You should have a healer's worry on you by now, and if you don't, you will.",
              "Buy your vials before the gate, not after. It's never after. And when you're done here, go east, past the river. Elske likes to look at the new ones."],
             "I will."),
        meet("elske", "The Arcanum", "minecraft:enchanted_book", "archmage",
             "Elske Barrow is Archmage of the Arcanum, in its tower in the east of the city.",
             ["Halvard's list, is it? Every stray is on it.",
              "Everyone has mana, even you. Whether you learn what it's for is your business, and my doors are open if you do. Go up to the citadel next. Mother Ysolde asks to see everyone before the gates do."],
             "Thank you, Archmage."),
        meet("ysolde", "The Sanctuary of Embers", "minecraft:soul_lantern", "priestess",
             "Take the Stair of Champions up to the citadel. Mother Ysolde tends the Pale Flame in the Sanctuary, east of the court.",
             ["You came up past the eight on the stair. Every one of them stood where you're standing.",
              "Come back to me when you're hurt. There's no shame in it. Look in on the Keep as you cross the court, and then go and see the Hall of Heroes. Someone should read those names."],
             "I will, Mother."),
        visit("keep", "The Lord's Keep", "minecraft:golden_helmet", (-73, -166), 12,
              "The Lord of Highmourn holds the great hall in the Keep, west across the court. See who you're fighting for."),
        visit("heroes", "The Hall of Heroes", "minecraft:totem_of_undying", (3, -248), 12,
              "Behind the citadel the Guild keeps its dead. Go and read the names."),
        meet("report", "Report to Halvard", "minecraft:shield", "guild_master",
             "You've seen the city. Go back down to the guild hall and tell Halvard.",
             ["You found your way back. Good. Now you know who's holding this city up, and whose names are on that wall.",
              "No more walking. There are cracks on the roads and the board's full of them. Go through one. Put down what rules it. Come back."],
             "I'll close one."),
    ]),
    ("first_blood", "First Blood", "minecraft:iron_sword", "Your first gate, and the first blade you make from it.", [
        step("first_gate", "Close a Gate", "minecraft:ender_eye", done("first_gate"),
             "The cracks in the world open wherever they please. Go through one, and put down what rules it.", "gate:F"),
        step("first_forge", "Work the Anvil", "ashbound:smith_hammer", done("first_forge"),
             "Take what the gate dropped to Wendel Blackwood in the Ashforge, and strike with him.", at("forgemaster")),
        step("masterwork", "A Masterwork", "ashbound:smith_hammer", done("masterwork"),
             "Keep time with the master. Do it well enough and he'll make that piece for you from then on.", at("forgemaster")),
        step("plus_five", "Raised to +5", "ashbound:smith_hammer", done("plus_five"),
             "Upgrades at the Gate Forge. A poor run wastes the drops, never the piece.", at("forgemaster")),
        step("boss_weapon", "A Boss's Own Weapon", "minecraft:nether_star", done("boss_weapon"),
             "One boss in five leaves its weapon behind. Keep them, even the doubles: an old forge may want them.", "gate:F"),
        step("rank_e", "Rank E", "minecraft:gold_ingot", done("rank_e"),
             "Finish requests from the board for Guild Points, then ask Elowen for an evaluation.", at("receptionist"), rewards=[("xp_levels", 5)]),
    ]),
    ("the_cold_forge", "The Cold Forge", "ashbound:first_ember", "Something under the Ashforge is older than the city.", [
        step("told", "An Old Rumour", "minecraft:book", adv("cold/told"), "Ask Wendel Blackwood about the dead forge below the armoury.", at("forgemaster")),
        step("seen", "Cold Stone", "minecraft:stone_bricks", adv("cold/seen"), "Go down the stair in the armoury and put your hand on it.", at(VAULT)),
        step("hunt", "What the Stone Wants", "minecraft:book", adv("cold/hunt"), "Tell Wendel what you saw.", at("forgemaster")),
        step("shard_e", "Shard of the First Fire", "ashbound:ember_shard", adv("cold/shard_e"), "Rank E: kill a gate's boss with the hunt in mind, and take what falls out of it.", "gate:E"),
        step("rank_d", "Rank D", "minecraft:gold_ingot", done("rank_d"), "The next shard is deeper than your card allows. Earn your evaluation from Elowen.", at("receptionist")),
        step("shard_d", "Shard of the Second Fire", "ashbound:ember_shard", adv("cold/shard_d"), "Rank D: the same, deeper in.", "gate:D"),
        step("rank_c", "Rank C", "minecraft:gold_ingot", done("rank_c"), "One more rank, and one more shard.", at("receptionist")),
        step("shard_c", "Shard of the Third Fire", "ashbound:ember_shard", adv("cold/shard_c"), "Rank C: the last of them.", "gate:C"),
        step("ember", "The First Ember", "ashbound:first_ember", adv("cold/ember"), "Bring all three shards to Wendel. Stand back when he says so.", at("forgemaster")),
        step("lit", "The Cold Forge Wakes", "ashbound:first_ember", adv("cold/lit"), "Press the Ember to the stone.", at(VAULT)),
        step("brand", "The Founder's Brand", "ashbound:founders_brand", adv("cold/brand"), "It burns, but it won't work for you. Ask Wendel why.", at("forgemaster")),
        step("proved", "The Forge's Trial", "ashbound:founders_brand", adv("cold/proved"), "Press the Brand to the altar, and put down what comes. Bring friends.", at(VAULT), rewards=[("xp_levels", 15)]),
        step("joined", "Two Made One", "minecraft:nether_star", adv("cold/joined"), "Lay two boss weapons of a kind in its hands, and hold them together when they fight you.", at(VAULT)),
    ]),
    ("the_deep_gates", "The Deep Gates", "minecraft:crying_obsidian", "Nobody's come back from the high ones to say what's in them.", [
        step("rank_b", "Rank B", "minecraft:gold_ingot", done("rank_b"), "Elowen will see you for an evaluation when the points are there.", at("receptionist")),
        step("gate_b", "A Rank B Gate", "minecraft:ender_eye", done("gate_b"), "Close one.", "gate:B", rewards=[("xp_levels", 13)]),
        step("rank_a", "Rank A", "minecraft:gold_ingot", done("rank_a"), "Few get this far. Elowen will write it in herself.", at("receptionist")),
        step("gate_a", "A Rank A Gate", "minecraft:ender_eye", done("gate_a"), "Close one.", "gate:A", rewards=[("xp_levels", 16)]),
        step("rank_s", "Rank S", "minecraft:gold_ingot", done("rank_s"), "The last card the Guild prints without a council.", at("receptionist")),
        step("gate_s", "A Rank S Gate", "minecraft:ender_eye", done("gate_s"), "Close one. Take friends.", "gate:S", rewards=[("xp_levels", 20)]),
        meet("name", "A Name in the Hall", "minecraft:totem_of_undying", "guild_master",
             "Halvard wants you at the guild hall.",
             ["S. I've written that word on a card twice in thirty years, and the other one's in the Hall of Heroes.",
              "You came through my door with mud on your boots and nothing to your name. It's on the wall now. Large, and at the front. The gates aren't done with us. But they've learned what comes through them."],
             "They have."),
    ]),
]


def chapters():
    """The story, one straight line: each step needs the one before, the last of a chapter opens the next."""
    out, prev = [], None
    for name, title, icon, sub, steps in STORY:
        quests = []
        for i, s in enumerate(steps):
            deps = [prev] if prev else []
            quests.append((s["key"], s["title"], s["icon"], s["task"], i % 8 * 2, i // 8 * 2, deps, [s["text"]], s["rewards"]))
            prev = name + "/" + s["key"]
        out.append((name, title, icon, sub, quests))
    return out


def quest(chap, key, title, icon, task, x, y, deps, desc, rewards=()):
    r = {"id": uid(chap + "/" + key), "title": title, "icon": {"id": icon, "count": 1}, "x": float(x), "y": float(y),
         "description": desc, "dependencies": [uid(d if "/" in d else chap + "/" + d) for d in deps],
         "tasks": [{"id": uid(chap + "/" + key + "/task"), **task}]}
    if rewards:
        r["rewards"] = [{"id": uid(chap + "/" + key + "/reward%d" % i), "type": k, k: v} for i, (k, v) in enumerate(rewards)]
    return r


def bounties():
    """The Hunter's Ledger: every boss of the gates and the towers, a column to a rank, each rank open once the last
    has been begun."""
    gear = json.load(open(os.path.join(ROOT, "src/main/resources/ashbound/gear.json"), encoding="utf8"))
    lang = json.load(open(os.path.join(ROOT, "src/main/resources/assets/ashbound/lang/en_us.json"), encoding="utf8"))
    out, seen = [], {}
    xp = {"F": 3, "E": 5, "D": 7, "C": 10, "B": 13, "A": 16, "S": 20}
    for x, rank in enumerate("FEDCBAS"):
        row = [d for d in gear if d["rank"] == rank]
        for y, d in enumerate(row):
            name = lang.get("entity.ashbound." + d["boss"], d["boss"].replace("_", " ").title())
            icon = "ashbound:" + d["mats"][2]["id"]
            deps = [seen["FEDCBAS"[x - 1]]] if x else []
            key = d["gate"]
            seen.setdefault(rank, key)
            out.append((key, name, icon, {"type": "kill", "entity": "ashbound:" + d["boss"], "value": 1}, x * 3, y * 1.6 - (len(row) - 1) * 0.8, deps,
                        ["Rank %s: %s. Put down what rules it." % (rank, d["title"])], [("xp_levels", xp[rank])]))
    return out


def journal(chaps):
    """The same quests for the game's own Journal and compass; the story's steps also say who ends them and how."""
    meta = {name + "/" + st["key"]: st for name, _t, _i, _s, steps in STORY for st in steps}
    out = []
    for name, title, icon, sub, quests in chaps:
        qs = []
        for key, t, _i, task, _x, _y, deps, desc, *_r in quests:
            flag = task["advancement"].split(":", 1)[1] if task["type"] == "advancement" else "kill/" + task["entity"].split(":", 1)[1]
            full = name + "/" + key
            st = meta.get(full, {})
            qs.append({"key": full, "title": t, "text": " ".join(desc), "flag": flag, "deps": [d if "/" in d else name + "/" + d for d in deps],
                       "where": st.get("where") or "gate:" + desc[0][5], "who": st.get("who", ""), "say": st.get("say", []), "reply": st.get("reply", ""), "reach": st.get("reach", 0)})
        out.append({"title": title, "sub": sub, "quests": qs})
    json.dump(out, open(os.path.join(ROOT, "src/main/resources/ashbound/journal.json"), "w", encoding="utf8"), indent=1, ensure_ascii=False)


def advancements(chaps):
    """The story's silent steps, for the ones nothing has made yet."""
    for *_h, quests in chaps:
        for q in quests:
            task = q[3]
            if task["type"] != "advancement" or not task["advancement"].startswith("ashbound:story/"):
                continue
            path = os.path.join(ROOT, "src/main/resources/data/ashbound/advancement", task["advancement"].split(":")[1] + ".json")
            if not os.path.exists(path):
                json.dump({"criteria": {"done": {"trigger": "minecraft:impossible"}}, "requirements": [["done"]]}, open(path, "w", encoding="utf8"), indent=1)


def main():
    CHAPTERS = chapters()
    CHAPTERS.append(("hunters_ledger", "The Hunter's Ledger", "minecraft:writable_book", "Every boss of the gates and towers, rank by rank.", bounties()))
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(os.path.join(OUT, "chapters"))
    data = {"default_consume_items": False, "default_quest_shape": "gear", "default_reward_team": False, "detection_delay": 20,
            "disable_gui": False, "grid_scale": 0.5, "pause_game": False, "progression_mode": "linear",
            "title": "Ashbound", "version": 13}
    open(os.path.join(OUT, "data.snbt"), "w", encoding="utf8", newline="\n").write(snbt(data) + "\n")
    open(os.path.join(OUT, "chapter_groups.snbt"), "w", encoding="utf8", newline="\n").write(snbt({"chapter_groups": []}) + "\n")
    for i, (name, title, icon, sub, quests) in enumerate(CHAPTERS):
        c = {"default_hide_dependency_lines": False, "default_quest_shape": "", "filename": name, "group": "", "icon": {"id": icon, "count": 1},
             "id": uid("chapter/" + name), "order_index": i, "quest_links": [], "subtitle": [sub], "title": title,
             "quests": [quest(name, *s) for s in quests]}
        open(os.path.join(OUT, "chapters", name + ".snbt"), "w", encoding="utf8", newline="\n").write(snbt(c) + "\n")
    journal(CHAPTERS)
    advancements(CHAPTERS)
    print("%d chapters, %d quests" % (len(CHAPTERS), sum(len(c[4]) for c in CHAPTERS)))


if __name__ == "__main__":
    main()
