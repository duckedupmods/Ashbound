package com.snoringwalrus.ashbound;

import java.util.LinkedHashMap;
import java.util.Map;

import com.mojang.serialization.MapCodec;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * Legend trophies (tools/trophies.py): the piece each Legend leaves when it falls, cut from its own model. A block you set
 * down anywhere (a shelf, a table, a plinth), its face turned to you.
 */
public final class Trophies {
	private Trophies() {}

	/** a trophy: stands on what it's put on, faces whoever set it down */
	public static class TrophyBlock extends HorizontalDirectionalBlock {
		static final MapCodec<TrophyBlock> CODEC = simpleCodec(TrophyBlock::new);
		private static final VoxelShape SHAPE = Block.box(1, 0, 1, 15, 15, 15);

		public TrophyBlock(BlockBehaviour.Properties p) {
			super(p);
			registerDefaultState(stateDefinition.any().setValue(FACING, Direction.SOUTH));
		}

		@Override
		protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
			return CODEC;
		}

		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
			b.add(FACING);
		}

		@Override
		public BlockState getStateForPlacement(BlockPlaceContext ctx) {
			return defaultBlockState().setValue(FACING, ctx.getHorizontalDirection().getOpposite());
		}

		@Override
		protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos pos, CollisionContext ctx) {
			return SHAPE;
		}
	}

	/** Legend -> its trophy's item */
	private static final Map<String, DeferredItem<?>> BY_LEGEND = new LinkedHashMap<>();

	private static void trophy(String id, String legend, MapColor colour, SoundType sound) {
		DeferredBlock<Block> b = WorldBlocks.BLOCKS.registerBlock("trophy_" + id, TrophyBlock::new,
				BlockBehaviour.Properties.of().mapColor(colour).strength(1.5f, 6f).sound(sound).noOcclusion());
		DeferredItem<?> it = Weapons.ITEMS.registerSimpleBlockItem(b, new Item.Properties().rarity(Rarity.EPIC).stacksTo(16));
		WorldBlocks.ITEMS.add(it);
		BY_LEGEND.put(legend, it);
	}

	static {
		trophy("penitents_bell", "rime_penitent", MapColor.COLOR_BROWN, SoundType.METAL);
		trophy("blackbriar_antlers", "old_blackbriar", MapColor.WOOD, SoundType.BONE_BLOCK);
		trophy("red_ploughshare", "red_plough", MapColor.COLOR_RED, SoundType.METAL);
		trophy("sunbreaker_mirror", "sunbreaker", MapColor.GOLD, SoundType.STONE);
		trophy("mires_lantern_staff", "grandmother_mire", MapColor.COLOR_BLACK, SoundType.LANTERN);
		trophy("hollow_smile_mask", "hollow_smile", MapColor.QUARTZ, SoundType.BONE_BLOCK);
		trophy("old_harpoons_anchor", "old_harpoon", MapColor.METAL, SoundType.CHAIN);
		trophy("mountain_fort", "walking_mountain", MapColor.STONE, SoundType.STONE);
	}

	/** Loads the class, so the trophies are registered. */
	static void init() {}

	/** This Legend's trophy (empty if it hasn't one). */
	static ItemStack of(String legend) {
		DeferredItem<?> it = BY_LEGEND.get(legend);
		return it == null ? ItemStack.EMPTY : new ItemStack(it.get());
	}
}
