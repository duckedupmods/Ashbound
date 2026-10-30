"""Brings the capital's building blocks over from E:/Ashbound (Minecraft 26.3) to the Epic Fight add-on (1.21.1):
their looks (blockstates, models, textures), names and vanilla tags, and writes CityBlocks.java, which registers
them: what kind of block each is (full, stairs, slab, wall, pillar) is read from its blockstate.

    python tools/port_city.py
"""
import glob
import json
import os
import shutil

import port_weapons as P

SRC = "E:/Ashbound/src/main/resources/"
A = SRC + "assets/ashbound/"
JAVA = P.GAME + "src/main/java/com/snoringwalrus/ashbound/CityBlocks.java"

# family -> (the blocks, the vanilla block whose feel they copy)
FAMILIES = [
    (["greystone", "greystone_stairs", "greystone_slab", "greystone_wall",
      "mossy_greystone", "mossy_greystone_stairs", "mossy_greystone_slab", "mossy_greystone_wall"], "STONE_BRICKS"),
    (["clay_roof_tiles", "clay_roof_tile_stairs", "clay_roof_tile_slab"], "TERRACOTTA"),
    (["statue_stone", "statue_stone_stairs", "statue_stone_slab"], "SMOOTH_STONE"),
    (["gilded_tiles", "gilded_tile_stairs", "gilded_tile_slab"], "GOLD_BLOCK"),
    (["carved_limestone", "limestone_bricks", "limestone_brick_stairs", "limestone_brick_slab", "limestone_brick_wall",
      "cracked_limestone_bricks", "mossy_limestone_bricks", "limestone_flagstones", "limestone_pillar",
      "pale_limestone", "pale_limestone_stairs", "pale_limestone_slab", "pale_limestone_wall"], "STONE_BRICKS"),
    (["slate_shingles", "slate_shingle_stairs", "slate_shingle_slab", "mossy_slate_shingles", "mossy_slate_shingle_stairs",
      "mossy_slate_shingle_slab"], "DEEPSLATE_TILES"),
    (["wood_shingles", "wood_shingle_stairs", "wood_shingle_slab"], "SPRUCE_PLANKS"),
    (["blue_roof_tiles", "blue_roof_tile_stairs", "blue_roof_tile_slab", "green_roof_tiles", "green_roof_tile_stairs",
      "green_roof_tile_slab"], "TERRACOTTA"),
] + [([c, c + "_timber"], "MUD_BRICKS") for c in ("plaster", "ochre_plaster", "rose_plaster", "slate_plaster")]

# the house kit's fittings (tools/houses.py): name -> (Java maker, properties), written as they are
WOOD = "BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(1f, 2f).sound(SoundType.WOOD).noOcclusion()"
WROUGHT = "BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(2f, 6f).sound(SoundType.LANTERN).noOcclusion()"
GLASS = "BlockBehaviour.Properties.of().strength(0.3f).sound(SoundType.GLASS).noOcclusion()"
SHUTTER = "BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(3f).sound(SoundType.WOOD).noOcclusion().ignitedByLava()"
STALL = "BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2f, 3f).sound(SoundType.WOOD).noOcclusion().ignitedByLava()"
FITTINGS = {
    "leaded_glass_pane": ("p -> new IronBarsBlock(p) {}", GLASS),
    "lit_leaded_glass_pane": ("p -> new IronBarsBlock(p) {}", GLASS + ".lightLevel(s -> 11)"),
    "leaded_arch_window_pane": ("p -> new IronBarsBlock(p) {}", GLASS),
    "flower_box": ("Block::new", WOOD),
    "wall_lantern": ("p -> new PropBlock.Facing(p, Block.box(5, 3, 4, 11, 15, 16))", WROUGHT + ".noCollission().lightLevel(s -> 14)"),
    "street_lamp": ("PropBlock.Lamp::new", WROUGHT + ".lightLevel(s -> s.getValue(PropBlock.Lamp.PART) > 0 ? 15 : 0)"),
    "bench": ("p -> new PropBlock.Facing(p, Block.box(0, 0, 2, 16, 9, 13))", WOOD),
    # the Moonwell Priestess on the market fountain, one model per block (E:/Ashbound tools/elfstatue.py)
    "elf_statue": ("PropBlock.ElfPiece::new", "BlockBehaviour.Properties.of().mapColor(MapColor.QUARTZ).strength(-1f, 3600000f)"
                   ".sound(SoundType.STONE).noOcclusion().lightLevel(PropBlock.ElfPiece::light)"),
}
for c in ("green", "blue", "red"):
    FITTINGS[c + "_shutter"] = ("p -> new TrapDoorBlock(BlockSetType.SPRUCE, p) {}", SHUTTER)
for n in ("produce_crate", "fish_crate", "candle_rack", "potion_shelf", "book_pile", "grain_sacks", "merchant_scales"):
    FITTINGS[n] = ("p -> new PropBlock.Facing(p, Block.box(1, 0, 1, 15, %d, 15))" % (15 if n == "potion_shelf" else 8),
                   WOOD + (".lightLevel(s -> 12)" if n == "candle_rack" else ""))
for t in ("candles", "apothecary", "bones", "fish", "produce", "smith", "books", "butcher", "curios", "lanterns"):
    FITTINGS["stall_" + t] = ("PropBlock.Stall::new", STALL + ".lightLevel(s -> PropBlock.Stall.light(s, %s))"
                              % ("true" if t in ("candles", "lanterns") else "false"))


def kind(state):
    if "multipart" in state:
        return "wall"
    keys = " ".join(state["variants"])
    if "shape=" in keys:
        return "stairs"
    if "type=bottom" in keys:
        return "slab"
    if "axis=" in keys:
        return "pillar"
    return "full"


def base_of(name, names):
    """A stairs block's full block: greystone_stairs -> greystone, clay_roof_tile_stairs -> clay_roof_tiles."""
    stem = name[:-len("_stairs")]
    for cand in (stem, stem + "s"):
        if cand in names:
            return cand
    raise SystemExit("no base block for " + name)


def load_model(ref):
    """A 26.3 block model as 1.21.1 reads it: a texture given as {"sprite": ...} becomes the plain name."""
    m = json.load(open(A + "models/" + ref[9:] + ".json", encoding="utf-8"))
    if "textures" in m:
        m["textures"] = {k: v["sprite"] if isinstance(v, dict) else v for k, v in m["textures"].items()}
        # 26.3 picks the render layer from the texture; 1.21.1 needs it named (glass, shutters, lanterns, props)
        used = {f["texture"].lstrip("#") for e in m.get("elements", []) for f in e["faces"].values()}
        a = [alpha(t[9:]) for k, t in m["textures"].items()
             if t.startswith("ashbound:") and (not m.get("elements") or k in used or k == "particle" and not used)]
        if "translucent" in a:
            m["render_type"] = "minecraft:translucent"
        elif "cutout" in a:
            m["render_type"] = "minecraft:cutout"
    return m


def alpha(tex):
    """'translucent' if the texture has half-clear pixels, 'cutout' if it has clear ones, else ''."""
    from PIL import Image
    path = A + "textures/" + tex + ".png"
    if not os.path.exists(path):
        return ""
    px = Image.open(path).convert("RGBA").getchannel("A").getdata()
    part = sum(1 for v in px if 8 < v < 248)
    return "translucent" if part > len(px) * 0.02 else "cutout" if min(px) < 128 else ""


def assets(names):
    models, textures = set(), set()

    def model(ref):
        if not ref.startswith("ashbound:") or ref in models:
            return
        models.add(ref)
        m = load_model(ref)
        if m.get("parent"):
            model(m["parent"])
        for t in m.get("textures", {}).values():
            if t.startswith("ashbound:"):
                textures.add(t[9:])
    kinds = {}
    for b in names:
        st = json.load(open(A + "blockstates/%s.json" % b, encoding="utf-8"))
        kinds[b] = kind(st)
        P.dump(P.ASSETS + "blockstates/%s.json" % b, st)
        parts = st.get("multipart") or [{"apply": v} for v in st["variants"].values()]
        for part in parts:
            v = part["apply"]
            for one in v if isinstance(v, list) else [v]:
                model(one["model"])
        # 1.21.1's items take a model of their own: a wall's inventory look, else the block's
        item = "ashbound:block/%s_inventory" % b if kinds[b] == "wall" else "ashbound:block/" + b
        if kinds[b] == "wall" and not os.path.exists(A + "models/block/%s_inventory.json" % b):
            item = "ashbound:block/%s_post" % b
        it = A + "items/%s.json" % b                    # 26.3's own item look, when it names one model
        if os.path.exists(it):
            d = json.load(open(it, encoding="utf-8"))["model"]
            if d.get("type") == "minecraft:model":
                item = d["model"]
        model(item)
        if item != "ashbound:item/" + b:
            P.dump(P.ASSETS + "models/item/%s.json" % b, {"parent": item})
    for ref in models:
        P.dump(P.ASSETS + "models/" + ref[9:] + ".json", load_model(ref))
    for t in textures:
        for ext in (".png", ".png.mcmeta"):
            if os.path.exists(A + "textures/" + t + ext):
                os.makedirs(os.path.dirname(P.ASSETS + "textures/" + t + ext), exist_ok=True)
                shutil.copy(A + "textures/" + t + ext, P.ASSETS + "textures/" + t + ext)
    return kinds, len(models), len(textures)


def tags(names):
    """Vanilla's tags they're in (walls connect, pickaxes mine...), merged into ours (other ports' entries kept)."""
    ids = {"ashbound:" + b for b in names}
    for path in glob.glob(SRC + "data/minecraft/tags/**/*.json", recursive=True):
        vals = [v for v in json.load(open(path, encoding="utf-8")).get("values", []) if v in ids]
        if not vals:
            continue
        rel = os.path.relpath(path, SRC + "data/minecraft").replace("\\", "/")
        out = P.GAME + "src/main/resources/data/minecraft/" + rel
        have = json.load(open(out, encoding="utf-8"))["values"] if os.path.exists(out) else []
        P.dump(out, {"replace": False, "values": have + [v for v in vals if v not in have]})


def lang(names):
    src = json.load(open(A + "lang/en_us.json", encoding="utf-8"))
    ours = json.load(open(P.ASSETS + "lang/en_us.json", encoding="utf-8"))
    for b in names:
        k = "block.ashbound." + b
        ours[k] = src.get(k) or b.replace("_", " ").title()
    P.dump(P.ASSETS + "lang/en_us.json", ours)


def java(kinds):
    names = list(kinds)
    lines = []
    for fam, feel in FAMILIES:
        for b in fam:
            k, F = kinds[b], b.upper()
            props = "BlockBehaviour.Properties.ofFullCopy(Blocks.%s)" % feel
            if b.endswith("_timber"):
                lines.append('	static final DeferredBlock<Block> %s = block("%s", TimberBlock::new, %s);' % (F, b, props))
            elif k == "full":
                lines.append('\tstatic final DeferredBlock<Block> %s = block("%s", Block::new, %s);' % (F, b, props))
            elif k == "pillar":
                lines.append('\tstatic final DeferredBlock<Block> %s = block("%s", RotatedPillarBlock::new, %s);' % (F, b, props))
            elif k == "slab":
                lines.append('\tstatic final DeferredBlock<Block> %s = block("%s", SlabBlock::new, %s);' % (F, b, props))
            elif k == "wall":
                lines.append('\tstatic final DeferredBlock<Block> %s = block("%s", WallBlock::new, %s.forceSolidOn());' % (F, b, props))
            elif k == "stairs":
                base = base_of(b, names).upper()
                lines.append('\tstatic final DeferredBlock<Block> %s = block("%s", p -> new StairBlock(%s.get().defaultBlockState(), p), %s);'
                             % (F, b, base, props))
    for b, (make, props) in FITTINGS.items():
        lines.append('	static final DeferredBlock<Block> %s = block("%s", %s, %s);' % (b.upper(), b, make, props))
    src = '''package com.snoringwalrus.ashbound;

import java.util.function.Function;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.IronBarsBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.TrapDoorBlock;
import net.minecraft.world.level.block.WallBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.BlockSetType;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.registries.DeferredBlock;

/** The capital's building blocks (written by tools/port_city.py: edit that, not this). */
public final class CityBlocks {
	private CityBlocks() {}

	private static DeferredBlock<Block> block(String name, Function<BlockBehaviour.Properties, ? extends Block> make, BlockBehaviour.Properties props) {
		DeferredBlock<Block> b = WorldBlocks.BLOCKS.registerBlock(name, make::apply, props);
		WorldBlocks.ITEMS.add(Weapons.ITEMS.registerSimpleBlockItem(b));
		return b;
	}

	/** Loads the class, so its blocks are registered. */
	static void init() {}

%s
}
''' % "\n".join(lines)
    with open(JAVA, "w", encoding="utf-8") as f:
        f.write(src)


if __name__ == "__main__":
    names = [b for fam, _ in FAMILIES for b in fam] + list(FITTINGS)
    kinds, nm, nt = assets(names)
    tags(names)
    lang(names)
    java(kinds)
    print("city blocks: %d (%s), %d models, %d textures" % (
        len(names), ", ".join("%d %s" % (list(kinds.values()).count(k), k) for k in sorted(set(kinds.values()))), nm, nt))
