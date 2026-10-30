"""A Roster v2 lair's meta (data/ashbound/lair/gate_<gate>.json): what the old dungeons carried by hand, made from
gear.py's table (title, rank, boss) and dforge.py (the seal's words)."""
import gear as G
import dforge

ORDER = ["weeping_mine", "tide_chapel", "brigands_gorge", "rookery", "hollow_circus", "mirefen_coven", "sandsunk_tomb",
         "fallen_titan", "jade_monastery", "storm_bastion", "bloodmoon_court", "obsidian_labyrinth", "abyssal_lighthouse",
         "eclipse_cathedral", "wyrms_hoard"]


def meta(gate):
    d = next(x for x in G.D if x["gate"] == gate)
    D = dforge.DUNGEONS[gate]
    title = d["title"]
    return {"dimension": "ashbound:gates", "title": title[0].lower() + title[1:] if title.startswith("The ") else title,
            "test_origin": [100000 + 3000 * ORDER.index(gate), 20, 0], "boss": "ashbound:" + d["boss"],
            "seal": D.get("seal_words", "The way is barred"), "broken": D.get("broken_words", "The way opens"),
            "arrive": [title.upper(), "%s-Rank Gate" % d["rank"]], "rank": d["rank"],
            "loot": "ashbound:chests/gate_" + gate}
