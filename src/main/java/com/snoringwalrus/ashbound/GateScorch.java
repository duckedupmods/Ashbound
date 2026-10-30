package com.snoringwalrus.ashbound;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * The ground a gate burnt as it opened: black char with cracks glowing in the gate's colour. Once its gate is
 * gone the glow dims (FADING) and the char wears away a patch at a time, over a few days.
 */
public class GateScorch extends Block {
	public static final IntegerProperty RANK = IntegerProperty.create("rank", 0, 8);
	public static final BooleanProperty FADING = BooleanProperty.create("fading");
	private static final VoxelShape SHAPE = Block.box(0, 0, 0, 16, 1, 16);

	public GateScorch(Properties p) {
		super(p);
		registerDefaultState(stateDefinition.any().setValue(RANK, 0).setValue(FADING, false));
	}

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
		b.add(RANK, FADING);
	}

	@Override
	protected VoxelShape getShape(BlockState s, BlockGetter level, BlockPos pos, CollisionContext ctx) {
		return SHAPE;
	}

	@Override
	protected boolean canSurvive(BlockState s, LevelReader level, BlockPos pos) {
		BlockPos below = pos.below();
		return level.getBlockState(below).isFaceSturdy(level, below, Direction.UP);
	}

	@Override
	protected BlockState updateShape(BlockState s, Direction dir, BlockState other, LevelAccessor level, BlockPos pos, BlockPos otherPos) {
		return dir == Direction.DOWN && !canSurvive(s, level, pos) ? Blocks.AIR.defaultBlockState() : s;
	}

	@Override
	protected void randomTick(BlockState s, ServerLevel level, BlockPos pos, RandomSource r) {
		if (!s.getValue(FADING)) {
			if (level.getEntitiesOfClass(GateEntity.class, new AABB(pos).inflate(10), g -> !g.closing()).isEmpty())
				level.setBlock(pos, s.setValue(FADING, true), 2);
		} else if (r.nextInt(24) == 0) {
			level.removeBlock(pos, false);
		}
	}
}
