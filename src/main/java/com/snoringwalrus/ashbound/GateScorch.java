package com.snoringwalrus.ashbound;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
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
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * The ground a gate burnt as it opened: black char with cracks glowing in the gate's colour. Once its gate is
 * gone the glow dims (FADING) and the char wears away a patch at a time, over a few days. It lies on the ground
 * and up the sides of whatever's next to it, so a step or a bank is burnt all the way round.
 */
public class GateScorch extends Block {
	public static final IntegerProperty RANK = IntegerProperty.create("rank", 0, 8);
	public static final BooleanProperty FADING = BooleanProperty.create("fading");
	public static final BooleanProperty FLOOR = BooleanProperty.create("floor"), NORTH = BooleanProperty.create("north"),
			EAST = BooleanProperty.create("east"), SOUTH = BooleanProperty.create("south"), WEST = BooleanProperty.create("west");
	private static final VoxelShape FLOOR_SHAPE = Block.box(0, 0, 0, 16, 1, 16), NORTH_SHAPE = Block.box(0, 0, 0, 16, 16, 1),
			EAST_SHAPE = Block.box(15, 0, 0, 16, 16, 16), SOUTH_SHAPE = Block.box(0, 0, 15, 16, 16, 16), WEST_SHAPE = Block.box(0, 0, 0, 1, 16, 16);
	/** How far up or down a side the char climbs from the ground it lies on. */
	static final int CLIMB = 4;

	public GateScorch(Properties p) {
		super(p);
		registerDefaultState(stateDefinition.any().setValue(RANK, 0).setValue(FADING, false).setValue(FLOOR, true)
				.setValue(NORTH, false).setValue(EAST, false).setValue(SOUTH, false).setValue(WEST, false));
	}

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
		b.add(RANK, FADING, FLOOR, NORTH, EAST, SOUTH, WEST);
	}

	public static BooleanProperty side(Direction d) {
		return switch (d) {
			case NORTH -> NORTH;
			case EAST -> EAST;
			case SOUTH -> SOUTH;
			case WEST -> WEST;
			default -> FLOOR;
		};
	}

	@Override
	protected VoxelShape getShape(BlockState s, BlockGetter level, BlockPos pos, CollisionContext ctx) {
		VoxelShape v = s.getValue(FLOOR) ? FLOOR_SHAPE : Shapes.empty();
		if (s.getValue(NORTH)) v = Shapes.or(v, NORTH_SHAPE);
		if (s.getValue(EAST)) v = Shapes.or(v, EAST_SHAPE);
		if (s.getValue(SOUTH)) v = Shapes.or(v, SOUTH_SHAPE);
		if (s.getValue(WEST)) v = Shapes.or(v, WEST_SHAPE);
		return v;
	}

	/** Whether char can lie against the block that way from `pos`: bare ground, not a tree. */
	public static boolean holds(BlockGetter level, BlockPos pos, Direction way) {
		BlockPos at = pos.relative(way);
		BlockState s = level.getBlockState(at);
		return !s.is(BlockTags.LOGS) && !s.is(BlockTags.LEAVES) && s.isFaceSturdy(level, at, way.getOpposite());
	}

	/** This state with only the faces that still have something behind them; AIR if none do. */
	private static BlockState settled(BlockState s, BlockGetter level, BlockPos pos) {
		boolean any = false;
		for (Direction d : new Direction[] {Direction.DOWN, Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST}) {
			boolean on = s.getValue(side(d)) && holds(level, pos, d);
			s = s.setValue(side(d), on);
			any |= on;
		}
		return any ? s : Blocks.AIR.defaultBlockState();
	}

	@Override
	protected boolean canSurvive(BlockState s, LevelReader level, BlockPos pos) {
		return !settled(s, level, pos).isAir();
	}

	@Override
	protected BlockState updateShape(BlockState s, Direction dir, BlockState other, LevelAccessor level, BlockPos pos, BlockPos otherPos) {
		return settled(s, level, pos);
	}

	@Override
	protected void randomTick(BlockState s, ServerLevel level, BlockPos pos, RandomSource r) {
		if (!s.getValue(FADING)) {
			if (level.getEntitiesOfClass(GateEntity.class, new AABB(pos).inflate(14), g -> !g.closing()).isEmpty())
				level.setBlock(pos, s.setValue(FADING, true), 2);
		} else if (r.nextInt(24) == 0) {
			level.removeBlock(pos, false);
		}
	}
}
