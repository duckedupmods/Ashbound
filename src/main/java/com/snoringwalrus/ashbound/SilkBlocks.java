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

/** The Silk Archive's blocks (written by tools/port_silk.py: edit that, not this). */
public final class SilkBlocks {
	private SilkBlocks() {}

	private static DeferredBlock<Block> block(String name, Function<BlockBehaviour.Properties, ? extends Block> make, BlockBehaviour.Properties props) {
		DeferredBlock<Block> b = WorldBlocks.BLOCKS.registerBlock(name, make::apply, props);
		WorldBlocks.ITEMS.add(Weapons.ITEMS.registerSimpleBlockItem(b));
		return b;
	}

	/** Loads the class, so its blocks are registered. */
	static void init() {}

	static final DeferredBlock<Block> ARCHIVE_STONE = block("archive_stone", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> ARCHIVE_STONE_STAIRS = block("archive_stone_stairs", p -> new StairBlock(ARCHIVE_STONE.get().defaultBlockState(), p), BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> ARCHIVE_STONE_SLAB = block("archive_stone_slab", SlabBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS));
	static final DeferredBlock<Block> ARCHIVE_STONE_WALL = block("archive_stone_wall", WallBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE_BRICKS).forceSolidOn());
	static final DeferredBlock<Block> ARCHIVE_TILES = block("archive_tiles", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.POLISHED_DEEPSLATE));
	static final DeferredBlock<Block> ARCHIVE_TILE_STAIRS = block("archive_tile_stairs", p -> new StairBlock(ARCHIVE_TILES.get().defaultBlockState(), p), BlockBehaviour.Properties.ofFullCopy(Blocks.POLISHED_DEEPSLATE));
	static final DeferredBlock<Block> ARCHIVE_TILE_SLAB = block("archive_tile_slab", SlabBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.POLISHED_DEEPSLATE));
	static final DeferredBlock<Block> WALNUT_PANEL = block("walnut_panel", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.DARK_OAK_PLANKS));
	static final DeferredBlock<Block> WALNUT_PANEL_STAIRS = block("walnut_panel_stairs", p -> new StairBlock(WALNUT_PANEL.get().defaultBlockState(), p), BlockBehaviour.Properties.ofFullCopy(Blocks.DARK_OAK_PLANKS));
	static final DeferredBlock<Block> WALNUT_PANEL_SLAB = block("walnut_panel_slab", SlabBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.DARK_OAK_PLANKS));
	static final DeferredBlock<Block> ARCHIVE_SHELVES = block("archive_shelves", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.BOOKSHELF));
	static final DeferredBlock<Block> WEBBED_SHELVES = block("webbed_shelves", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.BOOKSHELF));
	static final DeferredBlock<Block> INDEX_DRAWERS = block("index_drawers", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.BOOKSHELF));
	static final DeferredBlock<Block> SILK_WALL = block("silk_wall", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.WHITE_WOOL));
	static final DeferredBlock<Block> SILK_COCOON = block("silk_cocoon", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.WHITE_WOOL));
	static final DeferredBlock<Block> PARCHMENT_STACK = block("parchment_stack", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.WHITE_WOOL));
	static final DeferredBlock<Block> BLACK_INK = block("black_ink", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.BLACK_CONCRETE));
	static final DeferredBlock<Block> ARCHIVE_LAMP = block("archive_lamp", Block::new, BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(2f, 6f).sound(SoundType.LANTERN).lightLevel(s -> 15));
}
