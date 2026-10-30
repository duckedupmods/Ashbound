"""The city's shops (data/ashbound/shop/ID.json, opened from a shopkeeper's talk): the old mod's five (Brann, Hesta,
Wenna, Dunstan, Rook) with what doesn't exist on 1.21.1 swapped for Epic Fight's own, and one for each trade round
the market. Prices in coins.

    python tools/npc_shops.py
"""
import json
import os

OLD = 'E:/Ashbound/src/main/resources/data/ashbound/shop/'
OUT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources', 'data', 'ashbound', 'shop')
SWAP = {'ashbound:iron_greatsword': 'epicfight:iron_greatsword', 'minecraft:iron_spear': 'epicfight:iron_spear'}


def b(item, price, count=1, potion=None):
    it = {'id': item}
    if count > 1:
        it['count'] = count
    if potion:
        it['components'] = {'minecraft:potion_contents': {'potion': 'minecraft:' + potion}}
    return {'item': it, 'price': price}


def s(item, price):
    return {'item': item, 'price': price}


# the forgemaster takes the gates' drops off you too: commons cheap, elites dear, trophies dearer
GEAR = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources', 'ashbound', 'gear.json'), encoding='utf-8'))
GATE_DROPS = [s('ashbound:' + m['id'], {'common': 2, 'elite': 18, 'trophy': 90}[m['role']]) for g in GEAR for m in g['mats']]

TRADES = {
    'trade_general': {
        'buy': [b('minecraft:torch', 20, 16), b('minecraft:lantern', 35), b('minecraft:bread', 18, 3), b('minecraft:lead', 30),
                b('minecraft:bucket', 40), b('minecraft:shears', 30), b('minecraft:flint_and_steel', 25), b('minecraft:bundle', 60),
                b('minecraft:map', 40), b('minecraft:compass', 90), b('minecraft:red_bed', 70), b('minecraft:campfire', 45)],
        'sell': [s('minecraft:string', 2), s('minecraft:leather', 5), s('minecraft:feather', 1), s('minecraft:bone', 2), s('minecraft:flint', 1),
                 s('minecraft:stick', 1)]},
    'trade_baker': {
        'buy': [b('minecraft:bread', 15, 3), b('minecraft:cookie', 12, 6), b('minecraft:cake', 60), b('minecraft:pumpkin_pie', 25, 2),
                b('minecraft:honey_bottle', 30)],
        'sell': [s('minecraft:wheat', 1), s('minecraft:egg', 1), s('minecraft:sugar_cane', 1), s('minecraft:pumpkin', 3), s('minecraft:milk_bucket', 8)]},
    'trade_tailor': {
        'buy': [b('minecraft:leather_helmet', 30), b('minecraft:leather_chestplate', 50), b('minecraft:leather_leggings', 45),
                b('minecraft:leather_boots', 30), b('minecraft:white_wool', 6, 4), b('minecraft:red_wool', 8, 4), b('minecraft:black_wool', 8, 4),
                b('minecraft:white_banner', 40), b('minecraft:red_carpet', 10, 4)],
        'sell': [s('minecraft:white_wool', 1), s('minecraft:string', 2), s('minecraft:leather', 5), s('minecraft:rabbit_hide', 2)]},
    'trade_grocer': {
        'buy': [b('minecraft:apple', 10, 4), b('minecraft:carrot', 8, 6), b('minecraft:baked_potato', 12, 4), b('minecraft:melon_slice', 8, 6),
                b('minecraft:sweet_berries', 8, 8), b('minecraft:beetroot_soup', 18), b('minecraft:golden_carrot', 45, 2)],
        'sell': [s('minecraft:wheat', 1), s('minecraft:potato', 1), s('minecraft:carrot', 1), s('minecraft:beetroot', 1), s('minecraft:apple', 2),
                 s('minecraft:melon_slice', 1), s('minecraft:sweet_berries', 1)]},
    'trade_books': {
        'buy': [b('minecraft:book', 30), b('minecraft:writable_book', 45), b('minecraft:paper', 10, 8), b('minecraft:map', 40),
                b('minecraft:bookshelf', 80), b('minecraft:lectern', 90)],
        'sell': [s('minecraft:paper', 1), s('minecraft:book', 8), s('minecraft:ink_sac', 2), s('minecraft:feather', 1)]},
    'trade_chandler': {
        'buy': [b('minecraft:candle', 12, 4), b('minecraft:white_candle', 14, 4), b('minecraft:red_candle', 14, 4), b('minecraft:torch', 20, 16),
                b('minecraft:lantern', 35), b('minecraft:soul_lantern', 45), b('minecraft:honeycomb', 20, 2)],
        'sell': [s('minecraft:honeycomb', 3), s('minecraft:string', 2), s('minecraft:coal', 2), s('minecraft:charcoal', 2)]},
    'trade_fishmonger': {
        'buy': [b('minecraft:cooked_cod', 12, 3), b('minecraft:cooked_salmon', 15, 3), b('minecraft:fishing_rod', 40), b('minecraft:bucket', 40),
                b('minecraft:dried_kelp', 6, 8)],
        'sell': [s('minecraft:cod', 2), s('minecraft:salmon', 3), s('minecraft:tropical_fish', 5), s('minecraft:pufferfish', 6),
                 s('minecraft:ink_sac', 2), s('minecraft:nautilus_shell', 25)]},
    'trade_smith': {
        'buy': [b('minecraft:iron_sword', 90), b('minecraft:iron_axe', 85), b('minecraft:iron_pickaxe', 85), b('minecraft:iron_shovel', 50),
                b('minecraft:shield', 120), b('minecraft:iron_ingot', 20), b('minecraft:chain', 25, 4)],
        'sell': [s('minecraft:iron_ingot', 6), s('minecraft:coal', 2), s('minecraft:copper_ingot', 2), s('minecraft:raw_iron', 4)]},
    'forgemaster': {
        'buy': [b('epicfight:iron_greatsword', 220), b('epicfight:iron_longsword', 180), b('epicfight:iron_tachi', 180),
                b('epicfight:iron_spear', 150), b('epicfight:iron_dagger', 90), b('minecraft:iron_helmet', 120), b('minecraft:iron_chestplate', 200),
                b('minecraft:iron_leggings', 170), b('minecraft:iron_boots', 110), b('minecraft:diamond_sword', 420), b('minecraft:diamond', 160),
                b('minecraft:anvil', 260), b('minecraft:grindstone', 60), b('ashbound:gate_forge', 300),
                b('ashbound:apprentice_black_staff', 140), b('ashbound:apprentice_white_staff', 140),
                b('ashbound:apprentice_summon_staff', 160)],
        'sell': [s('minecraft:iron_ingot', 6), s('minecraft:gold_ingot', 10), s('minecraft:diamond', 60), s('minecraft:netherite_scrap', 150),
                 s('minecraft:coal', 2), s('minecraft:raw_iron', 4), s('minecraft:raw_gold', 7)] + GATE_DROPS},
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in sorted(os.listdir(OLD)):
        d = json.load(open(OLD + f, encoding='utf-8'))
        for l in d.get('buy', []):
            l['item']['id'] = SWAP.get(l['item']['id'], l['item']['id'])
        d['buy'] = [l for l in d.get('buy', []) if not l['item']['id'].startswith('ashbound:')]
        d['sell'] = [l for l in d.get('sell', []) if not l['item'].startswith('ashbound:')]
        json.dump(d, open(os.path.join(OUT, f), 'w', encoding='utf-8'), indent=1)
    for k, d in TRADES.items():
        json.dump(d, open(os.path.join(OUT, k + '.json'), 'w', encoding='utf-8'), indent=1)
    print(len(os.listdir(OUT)), 'shops')


if __name__ == '__main__':
    main()
