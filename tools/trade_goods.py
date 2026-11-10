"""Item models and English names for the Trades goods (goods.json from tools/goodsgen.py + the three misses). Their icons come from
tools/itemicons_h.py (python tools/itemicons.py h --game). Reads the ids and names from goods.json.

    python tools/trade_goods.py
"""
import json
import os
import re

GAME = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
A = os.path.join(GAME, "src/main/resources/assets/ashbound")
SRC = os.path.join(GAME, "src/main/java/com/snoringwalrus/ashbound/Trades.java")
MISSES = {"burnt_mush": "Burnt Mush", "sour_wash": "Sour Wash", "fizzled_draught": "Fizzled Draught"}


def main():
    goods = {g["id"]: g["name"] for g in json.load(open(os.path.join(GAME, "src/main/resources/data/ashbound/trades/goods.json"), encoding="utf-8"))}
    goods.update(MISSES)
    for gid in goods:
        if not os.path.exists(os.path.join(A, "textures/item", gid + ".png")):
            raise SystemExit("no icon for " + gid + ": run python tools/itemicons.py h --game")
        json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": "ashbound:item/" + gid}},
                  open(os.path.join(A, "models/item", gid + ".json"), "w", encoding="utf-8"), indent=1)
    lang = os.path.join(A, "lang/en_us.json")
    text = open(lang, encoding="utf-8").read()
    have = json.loads(text)
    add = {"item.ashbound." + g: n for g, n in goods.items() if have.get("item.ashbound." + g) != n}
    if add:
        body = text.rstrip().rstrip("}").rstrip()
        fresh = [k for k in add if k not in have]
        if fresh:
            body += ",\n" + ",\n".join('  %s: %s' % (json.dumps(k), json.dumps(add[k])) for k in fresh)
        text = body + "\n}\n"
        for k in add:
            if k in have:
                text = text.replace('%s: %s' % (json.dumps(k), json.dumps(have[k])), '%s: %s' % (json.dumps(k), json.dumps(add[k])))
        json.loads(text)
        open(lang, "w", encoding="utf-8").write(text)
    print(len(goods), "goods:", len(add), "names written")


if __name__ == "__main__":
    main()
