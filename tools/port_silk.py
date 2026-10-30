"""Brings the Silk Archive's blocks over from E:/Ashbound (tools/silkblocks.py) to the Epic Fight add-on, the same
way port_city.py brings the capital's: looks, names, tags, and SilkBlocks.java, which registers them.

    python tools/port_silk.py
"""
import port_city as PC
import port_weapons as P

JAVA = P.GAME + "src/main/java/com/snoringwalrus/ashbound/SilkBlocks.java"

FAMILIES = [
    (["archive_stone", "archive_stone_stairs", "archive_stone_slab", "archive_stone_wall"], "STONE_BRICKS"),
    (["archive_tiles", "archive_tile_stairs", "archive_tile_slab"], "POLISHED_DEEPSLATE"),
    (["walnut_panel", "walnut_panel_stairs", "walnut_panel_slab"], "DARK_OAK_PLANKS"),
    (["archive_shelves", "webbed_shelves", "index_drawers"], "BOOKSHELF"),
    (["silk_wall", "silk_cocoon"], "WHITE_WOOL"),
    (["parchment_stack"], "WHITE_WOOL"),
    (["black_ink"], "BLACK_CONCRETE"),
]
FITTINGS = {
    "archive_lamp": ("Block::new", "BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(2f, 6f)"
                     ".sound(SoundType.LANTERN).lightLevel(s -> 15)"),
}

if __name__ == "__main__":
    PC.FAMILIES, PC.FITTINGS, PC.JAVA = FAMILIES, FITTINGS, JAVA
    names = [b for fam, _ in FAMILIES for b in fam] + list(FITTINGS)
    kinds, nm, nt = PC.assets(names)
    PC.tags(names)
    PC.lang(names)
    PC.java(kinds)
    src = open(JAVA, encoding="utf-8").read()
    src = src.replace("/** The capital's building blocks (written by tools/port_city.py: edit that, not this). */",
                      "/** The Silk Archive's blocks (written by tools/port_silk.py: edit that, not this). */")
    src = src.replace("public final class CityBlocks {", "public final class SilkBlocks {").replace("private CityBlocks() {}", "private SilkBlocks() {}")
    open(JAVA, "w", encoding="utf-8").write(src)
    print("silk blocks: %d (%s), %d models, %d textures" % (
        len(names), ", ".join("%d %s" % (list(kinds.values()).count(k), k) for k in sorted(set(kinds.values()))), nm, nt))
