package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/** The blocks our world is built from: the wildwood (tools/port_world.py brings their looks over), and the forest floor's bits. */
public final class WorldBlocks {
	private WorldBlocks() {}

	static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(Ashbound.ID);
	static final List<DeferredItem<? extends Item>> ITEMS = new ArrayList<>();

	private static DeferredBlock<Block> block(String name, java.util.function.Function<BlockBehaviour.Properties, ? extends Block> make,
			BlockBehaviour.Properties props) {
		DeferredBlock<Block> b = BLOCKS.registerBlock(name, make::apply, props);
		ITEMS.add(Weapons.ITEMS.registerSimpleBlockItem(b));
		return b;
	}

	private static DeferredBlock<Block> leaves(String name) {
		return block(name, LeavesBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.OAK_LEAVES));
	}

	static final DeferredBlock<Block> WILDWOOD_LOG = block("wildwood_log", RotatedPillarBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.DARK_OAK_LOG));
	static final DeferredBlock<Block> WILDWOOD_WOOD = block("wildwood_wood", RotatedPillarBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.DARK_OAK_WOOD));
	static final DeferredBlock<Block> MOSSY_WILDWOOD_WOOD = block("mossy_wildwood_wood", RotatedPillarBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.DARK_OAK_WOOD));
	static {
		for (String n : new String[] {"wildwood_leaves", "wildwood_leaves_sunlit", "wildwood_leaves_shade", "wildwood_blossom", "wildwood_leaves_amber",
				"wildwood_leaves_crimson", "wildwood_leaves_rose", "wildwood_needles", "wildwood_leaves_lilac"})
			leaves(n);
	}
	static final DeferredBlock<Block> MOSSY_FIELDSTONE = block("mossy_fieldstone", Block::new, BlockBehaviour.Properties.of()
			.mapColor(MapColor.STONE).strength(1.8f, 6f).sound(SoundType.STONE).requiresCorrectToolForDrops());
	static final DeferredBlock<Block> MOSSY_FIELDSTONE_SLAB = block("mossy_fieldstone_slab", SlabBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE));
	static final DeferredBlock<Block> VIGIL_CANDLES = block("vigil_candles", Block::new, BlockBehaviour.Properties.of()
			.mapColor(MapColor.WOOL).strength(0.8f).sound(SoundType.CANDLE).lightLevel(s -> 12).noOcclusion());
}
