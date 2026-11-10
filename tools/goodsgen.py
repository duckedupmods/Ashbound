"""The Trades goods (meals, brews, elixirs) from one table: what each is for (its ARCHETYPE: which stats, which catch), its level
and recipe, its look. The numbers come from a power BUDGET by kind and level, so no good is accidentally stronger than another;
a good's rarity (Trades.Rarity, Common x1 to Legendary x2.2) then multiplies what it gives, never its catch.

    python tools/goodsgen.py            check the table, write src/main/resources/data/ashbound/trades/goods.json + tools/goods_icons.json
    python tools/goodsgen.py --sheet    and docs/concepts/goods_sheet.png (icons from the game textures; run the icons first)
    then: python tools/itemicons.py h --game ; python tools/trade_goods.py

Pass 16 (11/7): stats are all % (they keep up with your rank), stamina is a real stat now (Epic Fight's 15 bar starves melee),
every brew has a catch that buys it more, elixirs pay in toxicity. Same recipes in every world.
"""
import json
import math
import os
import sys
from collections import Counter

GAME = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(GAME, "src/main/resources/data/ashbound/trades/goods.json")
ICONS = os.path.join(GAME, "tools/goods_icons.json")
SHEET = os.path.join(GAME, "docs/concepts/goods_sheet.png")

KINDS = ("meat fish veg grain fruit sweet dairy egg mushroom herb flower water ember frost venom glow bone wart gate nut spice").split()

# what one unit of a stat costs from the budget: damage and spell power are the yardstick; staying power is cheaper (it's not
# killing anything), flat stun armour is per point
COST = {"dmg%": 1.0, "spell%": 1.0, "health%": 0.9, "armour%": 0.7, "move%": 1.1, "speed%": 1.2, "heal%": 0.8, "arrow%": 0.8,
        "stamina%": 0.2, "stamina_regen%": 0.15, "mana%": 0.25, "mana_regen%": 0.2, "dodge_cost%": 0.5, "stun_armour": 1.0,
        "ash%": 0.4, "coins%": 0.4, "dig%": 0.2}

# a Common good's budget at its level: one meal (10 min, tires you of it), one brew (5 min, has a catch), up to three elixirs
# (8 min, toxicity). Legendary is x2.2 of this.
def budget(kind, lv):
    return {"meal": 3.75 + 0.125 * lv, "brew": 5 + 0.15 * lv, "elixir": 4.4 + 0.125 * lv}[kind]


ARCH = {   # positives as (stat, share of the budget)
    "wayfarer": [("stamina%", .5), ("stamina_regen%", .5)],          # the stamina meal: roll and still swing
    "bulwark": [("health%", .6), ("stamina%", .4)],
    "courser": [("stamina_regen%", .5), ("move%", .5)],
    "brute": [("dmg%", 1.0)],
    "battlemage": [("spell%", .5), ("dmg%", .5)],
    "sage": [("mana%", .5), ("mana_regen%", .5)],
    "spellwright": [("spell%", .7), ("mana_regen%", .3)],
    "pilgrim": [("stamina%", .5), ("mana%", .5)],
    "juggernaut": [("health%", .5), ("armour%", .5)],
    "warden": [("armour%", .6), ("stun_armour", .4)],
    "steady": [("stun_armour", 1.0)],
    "duelist": [("dodge_cost%", .5), ("speed%", .5)],
    "swift": [("dodge_cost%", .5), ("move%", .5)],
    "skirmisher": [("speed%", .5), ("move%", .5)],
    "hunter": [("arrow%", .6), ("move%", .4)],
    "mender": [("heal%", .6), ("mana_regen%", .4)],
    "vital": [("health%", 1.0)],
    "stonehide": [("armour%", 1.0)],
    "tide": [("stamina_regen%", .6), ("mana_regen%", .4)],
    "vanguard": [("health%", .4), ("armour%", .3), ("dmg%", .3)],
    "feast": [("health%", .35), ("dmg%", .35), ("stamina%", .3)],
    "arcanist": [("spell%", .6), ("mana%", .4)],
    "fortune": [("ash%", .5), ("coins%", .5)],
    "delver": [("dig%", .6), ("health%", .4)],
    "none": [],
}
CATCH_SHARE = 0.35   # a catch costs this share of the budget and buys as much again in what the good gives

M, B, E = "meal", "brew", "elixir"
# id, kind, name, level, archetype, recipe, catch stat or "", icon shape, colours (food, chunk), extra
# extra: fx "fire_resistance,...", now "heal=30", tox override, food (nutrition)
T = [
    # ---- meals: the long buff, one at a time, tiring if you have it again soon
    ("jerky", M, "Trail Jerky", 1, "wayfarer", "meat meat", "", "JERKY", ("a8583a", "8a4028"), {}),
    ("hearthbread", M, "Hearthbread", 1, "vital", "grain grain dairy", "", "LOAF", ("d9a45a", "c08844"), {}),
    ("trail_mix", M, "Trail Mix", 2, "courser", "nut fruit", "", "CAKES", ("b08a5a", "8a2a3a"), {}),
    ("hunters_stew", M, "Hunter's Stew", 3, "bulwark", "meat veg veg", "", "BOWL", ("9a5a2a", "e08a3a"), {}),
    ("fish_cakes", M, "Fish Cakes", 3, "hunter", "fish grain egg", "", "CAKES", ("d8b070", "c09050"), {}),
    ("nutbread", M, "Hazel Nutbread", 4, "wayfarer", "nut grain sweet", "", "LOAF", ("a8703a", "6a4020"), {}),
    ("sunrise_breakfast", M, "Sunrise Breakfast", 5, "skirmisher", "egg meat grain", "", "PLATE", ("f0c040", "c8603a"), {}),
    ("foragers_salad", M, "Forager's Salad", 5, "courser", "veg fruit herb", "", "BOWL", ("6aae3a", "e04a4a"), {}),
    ("mushroom_broth", M, "Mushroom Broth", 5, "mender", "mushroom mushroom water", "", "BOWL", ("9a7a5a", "d8c8b0"), {}),
    ("spiced_porridge", M, "Spiced Porridge", 6, "pilgrim", "grain dairy spice", "", "BOWL", ("e0c08a", "a0502a"), {}),
    ("roasted_roots", M, "Roasted Roots", 7, "vital", "veg veg spice", "", "PLATE", ("c87a3a", "e8b040"), {}),
    ("fishermans_chowder", M, "Fisherman's Chowder", 8, "sage", "fish veg dairy", "", "BOWL", ("e8dcc0", "e09a6a"), {}),
    ("elven_fruit_bowl", M, "Elven Fruit Bowl", 8, "spellwright", "fruit fruit sweet", "", "BOWL", ("e05a7a", "f0c040"), {}),
    ("pilgrims_flatbread", M, "Pilgrim's Flatbread", 9, "pilgrim", "grain veg herb", "", "LOAF", ("e8c890", "6aae3a"), {}),
    ("honey_cakes", M, "Honey Cakes", 10, "fortune", "grain sweet egg", "", "CAKES", ("e8a830", "c87a18"), {}),
    ("smoked_eel", M, "Smoked Eel", 10, "tide", "fish fish spice", "", "JERKY", ("6a5a4a", "c8a060"), {}),
    ("berry_tart", M, "Berry Tart", 11, "duelist", "fruit sweet grain dairy", "", "PIE", ("8a2a5a", "f0e0d0"), {}),
    ("ember_skewers", M, "Ember Skewers", 12, "brute", "meat meat ember", "", "SKEWER", ("d04a1a", "f0c040"), {}),
    ("miners_pie", M, "Miner's Pie", 12, "delver", "meat grain veg mushroom", "", "PIE", ("c88a3a", "7a3a1a"), {}),
    ("glowcap_risotto", M, "Glowcap Risotto", 14, "spellwright", "mushroom grain glow", "", "BOWL", ("e8e0b0", "7ae0f0"), {}),
    ("frostfish_platter", M, "Frostfish Platter", 15, "stonehide", "fish frost herb", "", "PLATE", ("8ad0f0", "f0a080"), {"fx": "fire_resistance"}),
    ("herders_casserole", M, "Herder's Casserole", 16, "juggernaut", "meat dairy veg veg", "speed%", "PIE", ("b0703a", "e8d8b0"), {}),
    ("peppered_steak", M, "Peppered Steak", 18, "brute", "meat spice ember", "armour%", "PLATE", ("8a2a1a", "2a1a10"), {}),
    ("sweetroot_dumplings", M, "Sweetroot Dumplings", 19, "tide", "veg grain sweet egg", "", "BOWL", ("f0d8a8", "e08a3a"), {}),
    ("dwarven_fryup", M, "Dwarven Fry-up", 20, "warden", "meat egg mushroom veg grain", "", "PLATE", ("c06a2a", "f0d050"), {"food": 12}),
    ("deepwater_chowder", M, "Deepwater Chowder", 22, "sage", "fish fish veg gate", "", "BOWL", ("4a7a9a", "e8dcc0"), {}),
    ("nut_roast", M, "Hearth Nut Roast", 24, "wayfarer", "nut veg spice grain", "", "PLATE", ("8a5a2a", "6aae3a"), {"food": 10}),
    ("gatewardens_roast", M, "Gatewarden's Roast", 25, "vanguard", "meat meat veg gate", "", "PLATE", ("a03a1a", "6aae3a"), {"food": 12}),
    ("saltglass_platter", M, "Saltglass Platter", 28, "juggernaut", "fish frost spice gate", "", "PLATE", ("c8e8f0", "f08a6a"), {}),
    ("emberheart_pie", M, "Emberheart Pie", 30, "brute", "meat ember spice gate", "health%", "PIE", ("c0401a", "f8b040"), {}),
    ("moonpetal_salad", M, "Moonpetal Salad", 35, "spellwright", "veg fruit flower glow", "", "BOWL", ("a8c0f0", "f0f0ff"), {}),
    ("founders_feast", M, "Founder's Feast", 40, "feast", "meat fish veg grain gate", "", "PLATE", ("b06a2a", "f0c040"), {"food": 14}),
    ("rangers_banquet", M, "Ranger's Banquet", 45, "wayfarer", "meat meat nut spice gate", "", "PLATE", ("7a4a2a", "e8b040"), {"food": 14}),
    # ---- brews: a short push, and always a catch
    ("highmourn_ale", B, "Highmourn Ale", 1, "steady", "grain grain water", "move%", "TANKARD", ("d09a3a", "fffaf0"), {}),
    ("herbal_tea", B, "Herbal Tea", 3, "sage", "herb herb water", "move%", "CUP", ("7aa04a", "e8f0e8"), {}),
    ("spiced_cider", B, "Spiced Cider", 4, "courser", "fruit spice water", "armour%", "BOTTLE", ("d8902a", "fff0c0"), {}),
    ("honey_mead", B, "Honey Mead", 5, "brute", "sweet sweet water", "health%", "TANKARD", ("e8b040", "fff4d0"), {}),
    ("nutbrown_ale", B, "Nutbrown Ale", 6, "wayfarer", "grain nut water", "dmg%", "TANKARD", ("8a5a2a", "f0e0c0"), {}),
    ("miners_coffee", B, "Miner's Coffee", 7, "skirmisher", "herb dairy sweet water", "armour%", "CUP", ("4a2a1a", "e8d8c0"), {}),
    ("vintners_red", B, "Vintner's Red", 8, "spellwright", "fruit fruit water", "move%", "BOTTLE", ("8a1a3a", "d06080"), {}),
    ("ginger_beer", B, "Ginger Beer", 9, "duelist", "spice spice water", "health%", "BOTTLE", ("e8c060", "fff8d0"), {}),
    ("barrow_rum", B, "Barrow Rum", 11, "battlemage", "sweet spice grain water", "armour%", "BOTTLE", ("8a4a1a", "e8a050"), {}),
    ("dwarven_stout", B, "Dwarven Stout", 12, "vital", "grain grain mushroom water", "move%", "TANKARD", ("4a2a1a", "e8dcc8"), {}),
    ("sailors_grog", B, "Sailor's Grog", 13, "tide", "fruit sweet spice water", "spell%", "TANKARD", ("b0602a", "f0d8a0"), {}),
    ("frostberry_wine", B, "Frostberry Wine", 15, "juggernaut", "fruit frost water", "move%", "BOTTLE", ("9ac8ff", "e8f4ff"), {}),
    ("blackroot_porter", B, "Blackroot Porter", 17, "bulwark", "grain grain nut mushroom water", "move%", "TANKARD", ("2a1a10", "c8b8a0"), {}),
    ("thornwine", B, "Thornwine", 19, "brute", "fruit venom water", "health%", "BOTTLE", ("5a1a4a", "a0e060"), {}),
    ("emberbrand", B, "Emberbrand Whisky", 20, "brute", "grain ember water", "health%", "BOTTLE", ("e0701a", "ffc070"), {"fx": "fire_resistance"}),
    ("moonmead", B, "Moonmead", 22, "spellwright", "sweet flower glow water", "health%", "BOTTLE", ("c0c8ff", "ffffff"), {}),
    ("elfroot_cordial", B, "Elfroot Cordial", 25, "mender", "flower herb sweet water", "move%", "BOTTLE", ("c0f0a0", "f4fff0"), {}),
    ("giants_stout", B, "Giant's Stout", 27, "juggernaut", "grain grain bone water", "speed%", "TANKARD", ("3a2a1a", "f0e8d8"), {}),
    ("cinderspice_wine", B, "Cinderspice Wine", 32, "battlemage", "fruit ember spice water gate", "armour%", "BOTTLE", ("a02a1a", "ffb050"), {}),
    ("second_wind", B, "Second Wind", 36, "wayfarer", "herb spice sweet water gate", "health%", "CUP", ("a8e0c0", "ffffff"), {}),
    # ---- elixirs: tools for a fight, paid in toxicity (100 drains in 12 min)
    ("night_eye", E, "Night-eye Drops", 1, "none", "glow glow", "", "VIAL", ("6a7aff", "c0c8ff"), {"fx": "night_vision", "tox": 0}),
    ("mending_draught", E, "Draught of Mending", 3, "none", "herb glow water", "", "FLASK", ("e04a5a", "ffa0a8"), {"now": "heal=30", "tox": 25}),
    ("wind_tonic", E, "Wind Tonic", 4, "wayfarer", "herb nut water", "", "FLASK", ("a0e0f0", "ffffff"), {}),
    ("antidote", E, "Antidote", 5, "none", "venom herb dairy", "", "VIAL", ("9ae07a", "e0ffd0"), {"now": "cure=1", "tox": 0}),
    ("mana_draught", E, "Mana Draught", 5, "none", "wart herb water", "", "FLASK", ("4a8aff", "a8d0ff"), {"now": "mana=40", "tox": 25}),
    ("hawkeye_tincture", E, "Hawkeye Tincture", 7, "hunter", "nut glow water", "", "VIAL", ("e0c040", "fff8c0"), {}),
    ("flamewalk", E, "Flamewalk Tonic", 8, "none", "ember ember water", "", "FLASK", ("ff7a2a", "ffd090"), {"fx": "fire_resistance", "tox": 10}),
    ("deepbreath", E, "Deepbreath Elixir", 8, "none", "fish glow water", "", "FLASK", ("3ac0c0", "a8f0f0"), {"fx": "water_breathing,night_vision", "tox": 5}),
    ("marrow_draught", E, "Marrow Draught", 10, "juggernaut", "bone bone water", "", "FLASK", ("e8e0c8", "a09080"), {}),
    ("swiftfoot", E, "Swiftfoot Elixir", 12, "swift", "sweet herb glow", "", "CONE", ("f0e05a", "fffac0"), {}),
    ("viper_oil", E, "Viper Oil", 13, "brute", "venom spice water", "", "VIAL", ("4a8a2a", "c0f080"), {}),
    ("ironskin", E, "Ironskin Elixir", 15, "warden", "bone gate water", "", "CONE", ("9a9aa8", "e0e0ec"), {"tox": 45}),
    ("clarity_draught", E, "Draught of Clarity", 16, "sage", "flower wart water", "", "CONE", ("d0b0ff", "ffffff"), {}),
    ("rallying_draught", E, "Rallying Draught", 18, "tide", "herb flower glow water", "", "FLASK", ("f0a040", "fff0c0"), {"now": "heal=15"}),
    ("arcane_philtre", E, "Arcane Philtre", 20, "arcanist", "wart glow gate", "", "CONE", ("b05aff", "e0b8ff"), {"tox": 50}),
    ("greater_mending", E, "Greater Mending", 22, "none", "herb glow gate water", "", "FLASK", ("ff3a5a", "ffc0c8"), {"now": "heal=50", "tox": 35}),
    ("frostblood", E, "Frostblood Elixir", 24, "warden", "frost bone water", "", "CONE", ("6ab0f0", "e8f8ff"), {}),
    ("berserkers_draught", E, "Berserker's Draught", 25, "brute", "venom ember gate", "", "FLASK", ("c01a1a", "ff7a6a"), {"tox": 55}),
    ("stormstep", E, "Stormstep Elixir", 28, "skirmisher", "glow sweet fruit water", "", "CONE", ("8ab0ff", "ffffa0"), {}),
    ("fortune_elixir", E, "Elixir of Fortune", 30, "fortune", "gate gate glow sweet", "", "CONE", ("ffd040", "fff4b0"), {}),
    ("titans_draught", E, "Titan's Draught", 33, "vital", "bone wart gate water", "", "FLASK", ("a07a4a", "f0d8a0"), {}),
    ("starfire_philtre", E, "Starfire Philtre", 38, "battlemage", "glow wart flower gate", "", "CONE", ("f0f0ff", "a0c0ff"), {}),
    ("phoenix_tears", E, "Phoenix Tears", 42, "mender", "ember flower glow gate", "", "VIAL", ("ff8a2a", "fff0a0"), {"now": "heal=40"}),
]
MINUTES = {M: 10, B: 5, E: 8}


def stats_of(kind, lv, arch, catch):
    b = budget(kind, lv)
    out = {}
    more = 1.0
    if catch:
        more = 1 + CATCH_SHARE
    for st, share in ARCH[arch]:
        v = b * more * share / COST[st]
        out[st] = max(1, int(round(v)))
    if catch:
        out[catch] = -max(1, int(round(b * CATCH_SHARE / COST[catch])))
    return out


def shade(hexc, k):
    r, g, b = (int(hexc[i:i + 2], 16) for i in (0, 2, 4))
    f = lambda c: max(0, min(255, int(round(c * k if k < 1 else c + (255 - c) * (k - 1)))))
    return "%02x%02x%02x" % (f(r), f(g), f(b))


def build():
    goods, icons, errors = [], {}, []
    seen = {}
    ids = Counter(t[0] for t in T)
    for i, n in ids.items():
        if n > 1:
            errors.append("id twice: " + i)
    for gid, kind, name, lv, arch, needs, catch, shape, (food, chunk), extra in T:
        for k in needs.split():
            if k not in KINDS:
                errors.append(f"{gid}: '{k}' isn't a kind")
        key = (kind, tuple(sorted(needs.split())))
        if key in seen:
            errors.append(f"{gid} and {seen[key]} have the same {kind} recipe: {needs}")
        seen[key] = gid
        if not 2 <= len(needs.split()) <= 5:
            errors.append(f"{gid}: a recipe is 2 to 5 things")
        if kind == B and not catch:
            errors.append(f"{gid}: a brew needs its catch")
        if lv >= 20 and "gate" not in needs and kind != M:
            pass
        st = stats_of(kind, lv, arch, catch)
        b = budget(kind, lv)
        tox = extra.get("tox", int(round(5 + 6 * b)) if kind == E else 0)
        g = {"id": gid, "kind": kind, "name": name, "level": lv, "needs": needs,
             "stats": ",".join(f"{k}={v}" for k, v in st.items()), "fx": extra.get("fx", ""), "now": extra.get("now", ""),
             "colour": int(food, 16), "food": extra.get("food", {M: 6 + lv // 6, B: 2, E: 0}[kind]), "tox": tox,
             "archetype": arch, "minutes": MINUTES[kind]}
        goods.append(g)
        icons[gid] = {"shape": shape, "food": food, "shade": shade(food, 0.62), "shine": shade(food, 1.55), "chunk": chunk, "drink": kind != M}
    return goods, icons, errors


def table(goods):
    for kind in (M, B, E):
        print(f"\n== {kind}s ({sum(1 for g in goods if g['kind'] == kind)})")
        for g in goods:
            if g["kind"] != kind:
                continue
            extra = " ".join(x for x in (g["fx"], g["now"], f"tox {g['tox']}" if g["tox"] else "") if x)
            print(f"  {g['level']:>2} {g['name']:22} {g['needs']:32} {g['stats']:42} {extra}")


def sheet(goods):
    from PIL import Image, ImageDraw, ImageFont
    tex = os.path.join(GAME, "src/main/resources/assets/ashbound/textures/item")
    cols, cw, ch = 3, 620, 56
    rows = math.ceil(len(goods) / cols)
    img = Image.new("RGB", (cols * cw + 20, rows * ch + 70), (18, 14, 12))
    d = ImageDraw.Draw(img)
    try:
        f1, f2 = ImageFont.truetype("arial.ttf", 17), ImageFont.truetype("arial.ttf", 13)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    d.text((14, 12), "Ashbound goods (pass 16): Common values; Uncommon x1.25, Rare x1.5, Epic x1.8, Legendary x2.2 (catches stay)", fill=(240, 200, 120), font=f1)
    tint = {M: (230, 170, 90), B: (210, 150, 70), E: (150, 170, 255)}
    for i, g in enumerate(goods):
        x, y = 10 + (i // rows) * cw, 50 + (i % rows) * ch
        p = os.path.join(tex, g["id"] + ".png")
        if os.path.exists(p):
            ic = Image.open(p).convert("RGBA").resize((48, 48), Image.NEAREST)
            img.paste(ic, (x, y), ic)
        d.text((x + 56, y + 2), f"{g['name']}  ", fill=tint[g["kind"]], font=f1)
        d.text((x + 56 + d.textlength(g['name'] + '  ', font=f1), y + 5), f"{g['kind']} {g['level']}   {g['needs']}", fill=(150, 140, 130), font=f2)
        line = g["stats"].replace(",", "  ").replace("=", " ") + ("  " + g["now"].replace("=", " ") + "%" if g["now"] else "") + \
            ("  " + g["fx"] if g["fx"] else "") + (f"  tox {g['tox']}" if g["tox"] else "")
        d.text((x + 56, y + 26), line, fill=(220, 220, 210), font=f2)
    os.makedirs(os.path.dirname(SHEET), exist_ok=True)
    img.save(SHEET)
    print("wrote", SHEET)


def main():
    goods, icons, errors = build()
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(goods, open(OUT, "w", encoding="utf-8"), indent=1)
    json.dump(icons, open(ICONS, "w", encoding="utf-8"), indent=1)
    table(goods)
    print(f"\nwrote {OUT}: {len(goods)} goods")
    if "--sheet" in sys.argv:
        sheet(goods)


if __name__ == "__main__":
    main()
