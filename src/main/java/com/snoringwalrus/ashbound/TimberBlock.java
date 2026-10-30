package com.snoringwalrus.ashbound;

import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.ItemTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;

/**
 * Timber-framed plaster: one block per plaster colour whose FRAME picks which beams cross it (posts at
 * its left or right edge, rails along its top or bottom, the halves of a brace running corner to
 * corner, a carved panel), so a wall can be laid out like a real frame. Right-click with an axe to
 * cycle the frame. The shapes are listed in tools/citytex.py (FRAMES).
 */
public class TimberBlock extends Block {
	public static final int FRAMES = 23;
	public static final IntegerProperty FRAME = IntegerProperty.create("frame", 0, FRAMES - 1);

	public TimberBlock(Properties props) {
		super(props);
		registerDefaultState(stateDefinition.any().setValue(FRAME, 15));
	}

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
		builder.add(FRAME);
	}

	@Override
	protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player,
			InteractionHand hand, BlockHitResult hit) {
		if (!stack.is(ItemTags.AXES)) {
			return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
		}
		if (!level.isClientSide()) {
			level.setBlock(pos, player.isShiftKeyDown()
					? state.setValue(FRAME, (state.getValue(FRAME) + FRAMES - 1) % FRAMES)
					: state.cycle(FRAME), Block.UPDATE_ALL);
			level.playSound(null, pos, SoundEvents.AXE_STRIP, SoundSource.BLOCKS, 0.6f, 1.3f);
		}
		return ItemInteractionResult.sidedSuccess(level.isClientSide());
	}
}
