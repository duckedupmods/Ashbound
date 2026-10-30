"""The world's armour: eight sets found, never forged, like the world's weapons (tools/worldarms.py), from the same
factions of the great ruins. Two of each class (robe, light, medium, heavy), Uncommon to Legendary. Each is armorforge's
class template in its own theme, plus its own hand-built pieces (EXTRAS below): a corsair's bandana and earring, a
deserter's torn tabard with an arrow still in it, an alchemist's goggles and vials, a hollow knight's plume, a mantis's
forearm scythes and compound eyes, a barrow lord's crown and fur, an ice crown under the aurora, a gryphon rider's wings.

    python tools/worldarmour.py [sets]        meshes into tools/armor_src, world_armour.json, names
    python tools/efarmor.py <sets>            then onto Epic Fight's body (it reads world_armour.json too)
"""
import json
import os
import sys

sys.path.insert(0, 'E:/Ashbound/tools')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import armorforge as AF  # noqa: E402
import voxsword as V  # noqa: E402
import weaponforge as W  # noqa: E402
import worldarms as WA  # noqa: E402
import gear as G  # noqa: E402
from voxboss import C  # noqa: E402

OUT = os.path.join(G.GAME, "src/main/resources/ashbound/world_armour.json")

# id, prefix, class, rarity, (blade, dark, wrap, wood, glow, acc), cloth, emblem, trim, what it is
SETS = [
    ("corsair", "Corsair's", "light", "uncommon", ("tarnished", "iron", "red_cloth", "dark_wood", "g_sea", "brass"),
     "sea_cloth", "anchor", "wrap", "sea-stained leathers off a drowned crew"),
    ("deserter", "Deserter's", "medium", "uncommon", ("worn_iron", "rust", "red_cloth", "oak", "g_plain", "iron"),
     "red_cloth", "stud", "plain", "a soldier's kit worn by the man who ran"),
    ("alchemist", "Alchemist's", "robe", "rare", ("brass", "dark_iron", "brown_leather", "dark_wood", "g_venom", "brass"),
     "green_cloth", "gem", "drip", "a Blightkin alchemist's robes, goggles and all"),
    ("hollow_knight", "Hollow Knight's", "heavy", "rare", ("tarnished", "dark_iron", "blue_cloth", "dark_wood", "g_soul", "silver"),
     "blue_cloth", "crown", "filigree", "the Fallen Order's plate, the knight inside long gone"),
    ("mantis", "Mantis", "light", "epic", ("venom", "dark_iron", "black_leather", "chitin", "g_venom", "chitin"),
     "green_cloth", "claw", "teeth", "a brood reaper's chitin, its scythes still on the arms"),
    ("barrow_lord", "Barrow Lord's", "heavy", "epic", ("black_steel", "dark_iron", "fur", "dark_wood", "g_soul", "gold"),
     "purple_cloth", "skull", "runes", "a barrow lord's grave-plate, crowned, furred and still cold"),
    ("aurora", "Aurora", "robe", "legendary", ("ice", "silver", "white_cloth", "ice", "g_aurora", "silver"),
     "white_cloth", "crystal", "frost", "vestments of the cold chaplains, an ice crown and the northern lights"),
    ("gryphon_rider", "Gryphon Rider's", "medium", "legendary", ("bronze", "bronze", "white_cloth", "pale_wood", "g_storm", "gold"),
     "white_cloth", "wings", "filigree", "the Sky Legion's riding armour, winged helm and feathered shoulders"),
]
RANK = WA.RANK


# ---------------------------------------------------------------- each set's own pieces
# player units: feet at 0, facing +z, right hand -x; the helm round y 23-34, the body y 12-24, arms at x 6, legs x 2

def fire(add, part, box, mat="glow"):
    add(part, box, mat, group="fire")


def x_corsair(s, p, add, mount, th):
    h, c = p["helm_head"], p["chest_body"]
    for k, x in enumerate((0.6, -0.6)):   # the bandana's knot and tails
        V.chain(mount(h), (x, 29.0), [(2.6, 168 - 20 * k, 1.4, 0.5), (2.2, 178 - 10 * k, 1.1, 0.5)], "wrap", z=-4.9)
    add(h, C(0, 28.4, -4.9, 2.2, 1.6, 0.8), "wrap", tag="knot")
    add(h, C(-4.8, 24.6, 1.2, 0.5, 1.2, 0.5), "gold", tag="earring")
    V.chain(mount(c), (2.8, 12.4), [(3.0, 172, 1.6, 0.5), (2.2, 186, 1.2, 0.5)], "wrap", z=2.9)   # sash tails
    add(c, C(-2.6, 15.0, 2.9, 1.2, 1.2, 0.6), "acc", tag="button")
    add(c, C(-2.6, 18.0, 2.9, 1.2, 1.2, 0.6), "acc", tag="button")


def x_deserter(s, p, add, mount, th):
    c, a = p["chest_body"], p["chest_arm_l"]
    add(c, C(0, 7.4, 2.95, 4.6, 12.6, 0.5), "wrap", tag="tabard")
    add(c, C(1.4, 6.4, 2.95, 1.6, 1.0, 0.5), "wrap", tag="tatter")
    add(c, C(-1.2, 6.8, 2.95, 1.4, 0.6, 0.5), "wrap", tag="tatter")
    add(c, C(0, 16.0, 3.25, 1.4, 1.4, 0.4), "dark", tag="badge_torn")
    V.chain(mount(a), (7.4, 21.0), [(4.0, -55, 0.5, 0.5)], "wood", z=1.0)   # an arrow still in the pauldron
    V.chain(mount(a), (10.6, 23.2), [(0.9, -55, 1.0, 0.3), (0.6, -30, 0.7, 0.3)], "wrap", z=1.0)   # its fletching


def x_alchemist(s, p, add, mount, th):
    h, c = p["helm_head"], p["chest_body"]
    add(h, C(0, 30.6, -0.6, 9.8, 0.8, 9.6), "leather", tag="goggle_strap")
    for side in (1, -1):
        add(h, C(side * 1.7, 30.0, 5.0, 2.6, 2.4, 1.0), "acc", tag="goggle")
        fire(add, h, C(side * 1.7, 30.4, 5.5, 1.6, 1.6, 0.4))
    for k, x in enumerate((-2.8, -1.4, 0.0)):   # vials on the sash
        add(c, C(x, 13.6, 3.0, 1.0, 0.4, 1.0), "acc", tag="cork")
        fire(add, c, C(x, 11.8, 3.0, 0.9, 1.8, 0.9))
    add(c, C(0, 13.0, -3.6, 4.0, 7.6, 1.8), "acc", tag="tank")   # a brass tank on the back, a window in it
    fire(add, c, C(0, 14.4, -4.55, 1.6, 4.4, 0.3))
    V.chain(mount(c), (1.8, 20.4), [(2.4, -40, 0.7, 0.7), (2.2, -120, 0.6, 0.6)], "acc", z=-3.4)   # its tube


def x_hollow_knight(s, p, add, mount, th):
    h, c = p["helm_head"], p["chest_body"]
    add(h, C(0, 34.2, -0.6, 1.4, 2.6, 9.0), "wrap", tag="plume")
    add(h, C(0, 27.4, -5.4, 1.6, 8.6, 0.9), "wrap", tag="plume_tail")
    add(h, C(0, 33.2, 4.6, 1.8, 1.6, 1.0), "acc", tag="plume_clasp")
    fire(add, h, C(0, 27.65, 4.9, 7.4, 0.6, 0.45))   # the soul in the slit
    for z in (3.15, -3.15):   # a tattered tabard, front and back
        add(c, C(0, 7.0, z, 5.0, 13.6, 0.5), "wrap", tag="tabard")
        add(c, C(-1.4, 6.0, z, 1.6, 1.0, 0.5), "wrap", tag="tatter")
    add(c, C(0, 13.0, 3.45, 3.2, 3.2, 0.3), "acc", tag="crest_plate")


def x_mantis(s, p, add, mount, th):
    h, c = p["helm_head"], p["chest_body"]
    for side in (1, -1):
        fire(add, h, C(side * 2.0, 27.4, 4.75, 2.6, 2.2, 0.6))   # compound eyes
        add(h, C(side * 2.0, 27.0, 4.6, 3.2, 3.0, 0.4), "acc", tag="eye_rim")
        V.chain(mount(h), (side * 2.6, 23.8), [(1.8, 180 - side * 15, 1.0, 0.9), (1.6, 180 - side * 70, 0.7, 0.8)], "acc", z=4.9)
        V.chain(mount(h), (side * 1.2, 33.6), [(3.0, -side * 25, 0.45, 0.45), (2.6, -side * 60, 0.35, 0.35)], "dark", z=1.6)
        a = p["chest_arm_l" if side > 0 else "chest_arm_r"]   # the scythes off the forearms
        x = side * 6.0
        add(a, C(x + side * 2.3, 13.0, 0, 0.8, 4.0, 3.6), "acc", tag="scythe_root")
        V.chain(mount(a), (x + side * 2.6, 16.6), [(3.2, 180 + side * 8, 1.4, 0.9), (3.0, 180 + side * 30, 1.1, 0.8),
                                                   (2.2, 180 + side * 62, 0.8, 0.7), (1.2, 180 + side * 95, 0.5, 0.6)], "blade", z=0.0)
    for k in range(3):   # plates down the back
        add(c, C(0, 13.0 + k * 3.4, -3.0, 7.6 - k * 0.8, 3.0, 0.8), "blade" if k % 2 == 0 else "acc", tag="back_plate")
    add(c, C(0, 12.8, -3.5, 1.0, 10.0, 0.5), "dark", tag="spine")


def x_barrow_lord(s, p, add, mount, th):
    h, c = p["helm_head"], p["chest_body"]
    add(h, C(0, 33.0, -0.2, 10.6, 1.6, 10.6), "gold", tag="crown_band")
    for k in range(5):   # the crown's points, front and sides
        hh = 3.4 if k % 2 == 0 else 2.2
        add(h, C(-3.6 + k * 1.8, 34.4, 4.9, 1.0, hh, 0.8), "gold", tag="crown")
    for side in (1, -1):
        for z in (-2.4, 1.2):
            add(h, C(side * 4.9, 34.4, z, 0.8, 2.6, 1.0), "gold", tag="crown")
    fire(add, h, C(0, 27.65, 4.9, 7.4, 0.6, 0.45))
    add(c, C(0, 21.2, 0, 12.6, 3.6, 7.6), "wrap", tag="fur")   # the fur mantle
    add(c, C(0, 18.4, -3.6, 10.0, 3.0, 1.4), "wrap", tag="fur")
    add(c, C(0, 22.0, 0.8, 11.0, 0.9, 7.0), "gold", tag="torc")
    for side, b in ((1, "chest_arm_l"), (-1, "chest_arm_r")):
        add(p[b], C(side * 6.6, 22.6, 0, 7.2, 2.4, 7.2), "wrap", tag="fur")


def x_aurora(s, p, add, mount, th):
    h, c = p["helm_head"], p["chest_body"]
    for k in range(7):   # the ice crown along the hood's brow
        hh = (4.6, 2.6, 3.6, 5.4, 3.6, 2.6, 4.6)[k]
        x = -3.6 + k * 1.2
        add(h, C(x, 33.6, 2.0, 1.0, hh, 1.0), "blade", tag="icicle")
        add(h, C(x, 33.6 + hh, 2.0, 0.5, 0.8, 0.5), "blade", tag="icicle")
    fire(add, h, C(0, 34.2, 2.6, 1.0, 3.2, 0.6))
    for k in range(6):   # the aurora, hanging off the shoulders down the back
        x = -4.0 + k * 1.6
        ln = (9.0, 11.0, 12.0, 11.4, 10.2, 8.6)[k]
        fire(add, c, C(x, 23.0 - ln, -3.3, 1.5, ln, 0.4), "white" if k % 2 else "glow")
    add(c, C(0, 22.6, -3.4, 10.4, 1.2, 0.8), "acc", tag="clasp_bar")
    add(c, C(0, 17.4, 3.0, 2.8, 3.4, 0.6), "acc", tag="crystal_frame")
    fire(add, c, C(0, 17.8, 3.3, 1.6, 2.6, 0.6))


def x_gryphon_rider(s, p, add, mount, th):
    h = p["helm_head"]
    for side in (1, -1):   # the winged helm
        add(h, C(side * 5.1, 26.6, -0.6, 1.0, 5.0, 3.0), "acc", tag="wing_root")
        for k in range(5):
            V.chain(mount(h), (side * 5.3, 26.8 + k * 1.0), [(5.4 - 0.6 * k, -side * (18 + 13 * k), 1.6, 0.9),
                                                            (3.4 - 0.4 * k, -side * (34 + 15 * k), 1.1, 0.8)],
                    "acc" if k == 0 else "wrap", z=-0.6)
        a = p["chest_arm_l" if side > 0 else "chest_arm_r"]   # feathers under the pauldrons
        x = side * 6.0
        for j, (dx, dz) in enumerate(((-1.4, 1.6), (0.0, 0.0), (1.4, -1.6))):
            add(a, C(x + side * 0.6 + dx * 0.6, 15.6, dz, 1.3, 3.6 - 0.3 * j, 1.0), "wrap", tag="feather")
            add(a, C(x + side * 0.6 + dx * 0.6, 15.0, dz, 0.8, 0.8, 1.0), "acc", tag="feather_tip")
    c = p["chest_body"]
    add(c, C(0, 6.6, 3.0, 4.8, 8.2, 0.5), "wrap", tag="tabard")   # a white riding tabard, gold-edged
    add(c, C(0, 6.6, 3.05, 5.2, 0.6, 0.5), "acc", tag="tabard_hem")
    add(c, C(0, 7.0, -3.0, 6.0, 7.6, 0.5), "wrap", tag="tabard")
    add(h, C(0, 24.6, 5.3, 1.8, 3.4, 1.0), "gold", tag="beak")
    add(h, C(0, 24.0, 5.7, 1.0, 1.2, 0.8), "gold", tag="beak")
    add(h, C(0, 33.4, -0.4, 1.6, 2.0, 8.6), "wrap", tag="crest")
    for side in (1, -1):
        fire(add, h, C(side * 2.2, 27.0, 5.0, 1.4, 0.6, 0.4))


EXTRAS = {k[2:]: f for k, f in globals().items() if k.startswith("x_")}


def register():
    """their themes, cloth and pieces into armorforge, as if each were a gate"""
    for sid, prefix, cls, rar, pal, cloth, emb, trim, about in SETS:
        W.THEMES[sid] = WA.One(sid, *pal, emb, trim, scars=0.06 if rar == "uncommon" else 0.03)
        AF.CLOTH[sid] = WA.PAL[cloth]
        AF.EXTRAS[sid] = EXTRAS[sid]


def rows():
    out = []
    for sid, prefix, cls, rar, pal, cloth, emb, trim, about in SETS:
        pieces = [dict(id="%s_%s" % (sid, part), name="%s %s" % (prefix, G.PIECE_NAMES[part]), slot=slot)
                  for slot, part in zip(("helm", "chest", "legs", "boots"), G.PIECES[cls])]
        out.append(dict(id=sid, prefix=prefix, cls=cls, rarity=rar, rank=RANK[rar], about=about, pieces=pieces))
    return out


def main(only):
    register()
    out = rows()
    lang_path = os.path.join(W.ASSETS, "lang/en_us.json")
    lang = json.load(open(lang_path, encoding="utf-8"))
    for row in out:
        for pc in row["pieces"]:
            lang["item.ashbound." + pc["id"]] = pc["name"]
        if not only or row["id"] in only:
            AF.export(row["id"], row["cls"], row["id"])
            print("armour", row["rarity"], row["id"], row["cls"])
    G.dump(OUT, out)
    G.dump(lang_path, lang)


if __name__ == "__main__":
    main([a for a in sys.argv[1:] if not a.startswith("--")])
