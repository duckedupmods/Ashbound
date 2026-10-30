package com.snoringwalrus.ashbound;

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

	static final DeferredBlock<Block> GREYSTONE = block("greystone", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> GREYSTONE_STAIRS = block("greystone_stairs", p -> new StairBlock(GREYSTONE.get().defaultBlockState(), p), BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> GREYSTONE_SLAB = block("greystone_slab", SlabBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> GREYSTONE_WALL = block("greystone_wall", WallBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS).forceSolidOn());
	static final DeferredBlock<Block> MOSSY_GREYSTONE = block("mossy_greystone", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> MOSSY_GREYSTONE_STAIRS = block("mossy_greystone_stairs", p -> new StairBlock(MOSSY_GREYSTONE.get().defaultBlockState(), p), BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> MOSSY_GREYSTONE_SLAB = block("mossy_greystone_slab", SlabBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> MOSSY_GREYSTONE_WALL = block("mossy_greystone_wall", WallBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS).forceSolidOn());
	static final DeferredBlock<Block> CLAY_ROOF_TILES = block("clay_roof_tiles", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.TERRACOTTA));
	static final DeferredBlock<Block> CLAY_ROOF_TILE_STAIRS = block("clay_roof_tile_stairs", p -> new StairBlock(CLAY_ROOF_TILES.get().defaultBlockState(), p), BlockBehaviour.Properties.ofFullCopy(Blocks.TERRACOTTA));
	static final DeferredBlock<Block> CLAY_ROOF_TILE_SLAB = block("clay_roof_tile_slab", SlabBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.TERRACOTTA));
	static final DeferredBlock<Block> STATUE_STONE = block("statue_stone", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.SMOOTH_STONE));
	static final DeferredBlock<Block> STATUE_STONE_STAIRS = block("statue_stone_stairs", p -> new StairBlock(STATUE_STONE.get().defaultBlockState(), p), BlockBehaviour.Properties.ofFullCopy(Blocks.SMOOTH_STONE));
	static final DeferredBlock<Block> STATUE_STONE_SLAB = block("statue_stone_slab", SlabBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.SMOOTH_STONE));
	static final DeferredBlock<Block> GILDED_TILES = block("gilded_tiles", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.GOLD_BLOCK));
	static final DeferredBlock<Block> GILDED_TILE_STAIRS = block("gilded_tile_stairs", p -> new StairBlock(GILDED_TILES.get().defaultBlockState(), p), BlockBehaviour.Properties.ofFullCopy(Blocks.GOLD_BLOCK));
	static final DeferredBlock<Block> GILDED_TILE_SLAB = block("gilded_tile_slab", SlabBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.GOLD_BLOCK));
	static final DeferredBlock<Block> CARVED_LIMESTONE = block("carved_limestone", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> LIMESTONE_BRICKS = block("limestone_bricks", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> LIMESTONE_BRICK_STAIRS = block("limestone_brick_stairs", p -> new StairBlock(LIMESTONE_BRICKS.get().defaultBlockState(), p), BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> LIMESTONE_BRICK_SLAB = block("limestone_brick_slab", SlabBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> LIMESTONE_BRICK_WALL = block("limestone_brick_wall", WallBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS).forceSolidOn());
	static final DeferredBlock<Block> CRACKED_LIMESTONE_BRICKS = block("cracked_limestone_bricks", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> MOSSY_LIMESTONE_BRICKS = block("mossy_limestone_bricks", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> LIMESTONE_FLAGSTONES = block("limestone_flagstones", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> LIMESTONE_PILLAR = block("limestone_pillar", RotatedPillarBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> PALE_LIMESTONE = block("pale_limestone", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> PALE_LIMESTONE_STAIRS = block("pale_limestone_stairs", p -> new StairBlock(PALE_LIMESTONE.get().defaultBlockState(), p), BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> PALE_LIMESTONE_SLAB = block("pale_limestone_slab", SlabBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> PALE_LIMESTONE_WALL = block("pale_limestone_wall", WallBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS).forceSolidOn());
	static final DeferredBlock<Block> SLATE_SHINGLES = block("slate_shingles", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.DEEPSLATE_TILES));
	static final DeferredBlock<Block> SLATE_SHINGLE_STAIRS = block("slate_shingle_stairs", p -> new StairBlock(SLATE_SHINGLES.get().defaultBlockState(), p), BlockBehaviour.Properties.ofFullCopy(Blocks.DEEPSLATE_TILES));
	static final DeferredBlock<Block> SLATE_SHINGLE_SLAB = block("slate_shingle_slab", SlabBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.DEEPSLATE_TILES));
	static final DeferredBlock<Block> MOSSY_SLATE_SHINGLES = block("mossy_slate_shingles", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.DEEPSLATE_TILES));
	static final DeferredBlock<Block> MOSSY_SLATE_SHINGLE_STAIRS = block("mossy_slate_shingle_stairs", p -> new StairBlock(MOSSY_SLATE_SHINGLES.get().defaultBlockState(), p), BlockBehaviour.Properties.ofFullCopy(Blocks.DEEPSLATE_TILES));
	static final DeferredBlock<Block> MOSSY_SLATE_SHINGLE_SLAB = block("mossy_slate_shingle_slab", SlabBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.DEEPSLATE_TILES));
	static final DeferredBlock<Block> WOOD_SHINGLES = block("wood_shingles", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.SPRUCE_PLANKS));
	static final DeferredBlock<Block> WOOD_SHINGLE_STAIRS = block("wood_shingle_stairs", p -> new StairBlock(WOOD_SHINGLES.get().defaultBlockState(), p), BlockBehaviour.Properties.ofFullCopy(Blocks.SPRUCE_PLANKS));
	static final DeferredBlock<Block> WOOD_SHINGLE_SLAB = block("wood_shingle_slab", SlabBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.SPRUCE_PLANKS));
	static final DeferredBlock<Block> BLUE_ROOF_TILES = block("blue_roof_tiles", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.TERRACOTTA));
	static final DeferredBlock<Block> BLUE_ROOF_TILE_STAIRS = block("blue_roof_tile_stairs", p -> new StairBlock(BLUE_ROOF_TILES.get().defaultBlockState(), p), BlockBehaviour.Properties.ofFullCopy(Blocks.TERRACOTTA));
	static final DeferredBlock<Block> BLUE_ROOF_TILE_SLAB = block("blue_roof_tile_slab", SlabBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.TERRACOTTA));
	static final DeferredBlock<Block> GREEN_ROOF_TILES = block("green_roof_tiles", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.TERRACOTTA));
	static final DeferredBlock<Block> GREEN_ROOF_TILE_STAIRS = block("green_roof_tile_stairs", p -> new StairBlock(GREEN_ROOF_TILES.get().defaultBlockState(), p), BlockBehaviour.Properties.ofFullCopy(Blocks.TERRACOTTA));
	static final DeferredBlock<Block> GREEN_ROOF_TILE_SLAB = block("green_roof_tile_slab", SlabBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.TERRACOTTA));
	static final DeferredBlock<Block> PLASTER = block("plaster", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.MUD_BRICKS));
	static final DeferredBlock<Block> PLASTER_TIMBER = block("plaster_timber", TimberBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.MUD_BRICKS));
	static final DeferredBlock<Block> OCHRE_PLASTER = block("ochre_plaster", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.MUD_BRICKS));
	static final DeferredBlock<Block> OCHRE_PLASTER_TIMBER = block("ochre_plaster_timber", TimberBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.MUD_BRICKS));
	static final DeferredBlock<Block> ROSE_PLASTER = block("rose_plaster", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.MUD_BRICKS));
	static final DeferredBlock<Block> ROSE_PLASTER_TIMBER = block("rose_plaster_timber", TimberBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.MUD_BRICKS));
	static final DeferredBlock<Block> SLATE_PLASTER = block("slate_plaster", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.MUD_BRICKS));
	static final DeferredBlock<Block> SLATE_PLASTER_TIMBER = block("slate_plaster_timber", TimberBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.MUD_BRICKS));
	static final DeferredBlock<Block> LEADED_GLASS_PANE = block("leaded_glass_pane", p -> new IronBarsBlock(p) {}, BlockBehaviour.Properties.of().strength(0.3f).sound(SoundType.GLASS).noOcclusion());
	static final DeferredBlock<Block> LIT_LEADED_GLASS_PANE = block("lit_leaded_glass_pane", p -> new IronBarsBlock(p) {}, BlockBehaviour.Properties.of().strength(0.3f).sound(SoundType.GLASS).noOcclusion().lightLevel(s -> 11));
	static final DeferredBlock<Block> LEADED_ARCH_WINDOW_PANE = block("leaded_arch_window_pane", p -> new IronBarsBlock(p) {}, BlockBehaviour.Properties.of().strength(0.3f).sound(SoundType.GLASS).noOcclusion());
	static final DeferredBlock<Block> FLOWER_BOX = block("flower_box", Block::new, BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(1f, 2f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> WALL_LANTERN = block("wall_lantern", p -> new PropBlock.Facing(p, Block.box(5, 3, 4, 11, 15, 16)), BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(2f, 6f).sound(SoundType.LANTERN).noOcclusion().noCollission().lightLevel(s -> 14));
	static final DeferredBlock<Block> STREET_LAMP = block("street_lamp", PropBlock.Lamp::new, BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(2f, 6f).sound(SoundType.LANTERN).noOcclusion().lightLevel(s -> s.getValue(PropBlock.Lamp.PART) > 0 ? 15 : 0));
	static final DeferredBlock<Block> BENCH = block("bench", p -> new PropBlock.Facing(p, Block.box(0, 0, 2, 16, 9, 13)), BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(1f, 2f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> ELF_STATUE = block("elf_statue", PropBlock.ElfPiece::new, BlockBehaviour.Properties.of().mapColor(MapColor.QUARTZ).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion().lightLevel(PropBlock.ElfPiece::light));
	static final DeferredBlock<Block> GREEN_SHUTTER = block("green_shutter", p -> new TrapDoorBlock(BlockSetType.SPRUCE, p) {}, BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(3f).sound(SoundType.WOOD).noOcclusion().ignitedByLava());
	static final DeferredBlock<Block> BLUE_SHUTTER = block("blue_shutter", p -> new TrapDoorBlock(BlockSetType.SPRUCE, p) {}, BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(3f).sound(SoundType.WOOD).noOcclusion().ignitedByLava());
	static final DeferredBlock<Block> RED_SHUTTER = block("red_shutter", p -> new TrapDoorBlock(BlockSetType.SPRUCE, p) {}, BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(3f).sound(SoundType.WOOD).noOcclusion().ignitedByLava());
	static final DeferredBlock<Block> PRODUCE_CRATE = block("produce_crate", p -> new PropBlock.Facing(p, Block.box(1, 0, 1, 15, 8, 15)), BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(1f, 2f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> FISH_CRATE = block("fish_crate", p -> new PropBlock.Facing(p, Block.box(1, 0, 1, 15, 8, 15)), BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(1f, 2f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> CANDLE_RACK = block("candle_rack", p -> new PropBlock.Facing(p, Block.box(1, 0, 1, 15, 8, 15)), BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(1f, 2f).sound(SoundType.WOOD).noOcclusion().lightLevel(s -> 12));
	static final DeferredBlock<Block> POTION_SHELF = block("potion_shelf", p -> new PropBlock.Facing(p, Block.box(1, 0, 1, 15, 15, 15)), BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(1f, 2f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> BOOK_PILE = block("book_pile", p -> new PropBlock.Facing(p, Block.box(1, 0, 1, 15, 8, 15)), BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(1f, 2f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> GRAIN_SACKS = block("grain_sacks", p -> new PropBlock.Facing(p, Block.box(1, 0, 1, 15, 8, 15)), BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(1f, 2f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> MERCHANT_SCALES = block("merchant_scales", p -> new PropBlock.Facing(p, Block.box(1, 0, 1, 15, 8, 15)), BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(1f, 2f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> STALL_CANDLES = block("stall_candles", PropBlock.Stall::new, BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2f, 3f).sound(SoundType.WOOD).noOcclusion().ignitedByLava().lightLevel(s -> PropBlock.Stall.light(s, true)));
	static final DeferredBlock<Block> STALL_APOTHECARY = block("stall_apothecary", PropBlock.Stall::new, BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2f, 3f).sound(SoundType.WOOD).noOcclusion().ignitedByLava().lightLevel(s -> PropBlock.Stall.light(s, false)));
	static final DeferredBlock<Block> STALL_BONES = block("stall_bones", PropBlock.Stall::new, BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2f, 3f).sound(SoundType.WOOD).noOcclusion().ignitedByLava().lightLevel(s -> PropBlock.Stall.light(s, false)));
	static final DeferredBlock<Block> STALL_FISH = block("stall_fish", PropBlock.Stall::new, BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2f, 3f).sound(SoundType.WOOD).noOcclusion().ignitedByLava().lightLevel(s -> PropBlock.Stall.light(s, false)));
	static final DeferredBlock<Block> STALL_PRODUCE = block("stall_produce", PropBlock.Stall::new, BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2f, 3f).sound(SoundType.WOOD).noOcclusion().ignitedByLava().lightLevel(s -> PropBlock.Stall.light(s, false)));
	static final DeferredBlock<Block> STALL_SMITH = block("stall_smith", PropBlock.Stall::new, BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2f, 3f).sound(SoundType.WOOD).noOcclusion().ignitedByLava().lightLevel(s -> PropBlock.Stall.light(s, false)));
	static final DeferredBlock<Block> STALL_BOOKS = block("stall_books", PropBlock.Stall::new, BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2f, 3f).sound(SoundType.WOOD).noOcclusion().ignitedByLava().lightLevel(s -> PropBlock.Stall.light(s, false)));
	static final DeferredBlock<Block> STALL_BUTCHER = block("stall_butcher", PropBlock.Stall::new, BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2f, 3f).sound(SoundType.WOOD).noOcclusion().ignitedByLava().lightLevel(s -> PropBlock.Stall.light(s, false)));
	static final DeferredBlock<Block> STALL_CURIOS = block("stall_curios", PropBlock.Stall::new, BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2f, 3f).sound(SoundType.WOOD).noOcclusion().ignitedByLava().lightLevel(s -> PropBlock.Stall.light(s, false)));
	static final DeferredBlock<Block> STALL_LANTERNS = block("stall_lanterns", PropBlock.Stall::new, BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2f, 3f).sound(SoundType.WOOD).noOcclusion().ignitedByLava().lightLevel(s -> PropBlock.Stall.light(s, true)));
}
