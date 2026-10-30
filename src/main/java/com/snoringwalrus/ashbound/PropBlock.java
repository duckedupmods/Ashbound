package com.snoringwalrus.ashbound;

import java.util.BitSet;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.inventory.AnvilMenu;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.inventory.CraftingMenu;
import net.minecraft.world.inventory.EnchantmentMenu;
import net.minecraft.world.inventory.GrindstoneMenu;
import net.minecraft.world.inventory.SmithingMenu;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Highmourn's carved and wrought props, drawn by their own block models (tools/props.py,
 * tools/lampmodel.py, tools/elfstatue.py):
 *  - Facing: one block turned to face whoever placed it (gargoyle, bench, wall lantern)
 *  - Statue: four blocks tall, facing (the hunter and warden statues)
 *  - Lamp: three blocks tall, its arms along an axis (the twin-arm street lamp)
 * The tall ones place their upper parts above themselves and go as one when any part is broken.
 */
public final class PropBlock {
	public static final EnumProperty<Direction> FACING = BlockStateProperties.HORIZONTAL_FACING;
	public static final EnumProperty<Direction.Axis> AXIS = BlockStateProperties.HORIZONTAL_AXIS;

	private PropBlock() {}

	public static class Facing extends Block {
		private final VoxelShape shape;

		public Facing(Properties props, VoxelShape shape) {
			super(props);
			this.shape = shape;
			registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH));
		}

		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
			builder.add(FACING);
		}

		@Override
		public BlockState getStateForPlacement(BlockPlaceContext ctx) {
			// wall-mounted things face away from the wall clicked; the rest face the player
			Direction f = ctx.getClickedFace().getAxis().isHorizontal() ? ctx.getClickedFace() : ctx.getHorizontalDirection().getOpposite();
			return defaultBlockState().setValue(FACING, f);
		}

		@Override
		protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
			return PropShapes.of(this, 0, state.getValue(FACING), shape);
		}
	}

	/** Shared by the tall props: the parts stacked above the base, placed and broken together. */
	public abstract static class Tall extends Block {
		private final VoxelShape shape;

		protected Tall(Properties props, VoxelShape shape) {
			super(props);
			this.shape = shape;
		}

		protected abstract IntegerProperty part();

		protected abstract int parts();

		protected abstract BlockState turned(BlockPlaceContext ctx);

		@Override
		public BlockState getStateForPlacement(BlockPlaceContext ctx) {
			BlockPos pos = ctx.getClickedPos();
			Level level = ctx.getLevel();
			if (pos.getY() + parts() - 1 > (level.getMaxBuildHeight() - 1)) return null;
			for (int i = 1; i < parts(); i++) {
				if (!level.getBlockState(pos.above(i)).canBeReplaced(ctx)) return null;
			}
			return turned(ctx).setValue(part(), 0);
		}

		@Override
		public void setPlacedBy(Level level, BlockPos pos, BlockState state, LivingEntity by, ItemStack stack) {
			for (int i = 1; i < parts(); i++) level.setBlock(pos.above(i), state.setValue(part(), i), Block.UPDATE_ALL);
		}

		@Override
		public BlockState playerWillDestroy(Level level, BlockPos pos, BlockState state, Player player) {
			int p = state.getValue(part());
			for (int i = 0; i < parts(); i++) {
				if (i == p) continue;
				BlockPos o = pos.above(i - p);
				if (level.getBlockState(o).is(this)) level.setBlock(o, net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), Block.UPDATE_ALL | Block.UPDATE_SUPPRESS_DROPS);
			}
			return super.playerWillDestroy(level, pos, state, player);
		}

		@Override
		protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
			return shape;
		}
	}

	public static class Statue extends Tall {
		public static final IntegerProperty PART = IntegerProperty.create("part", 0, 3);

		public Statue(Properties props) {
			super(props, Block.box(1, 0, 1, 15, 16, 15));
			registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH).setValue(PART, 0));
		}

		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
			builder.add(FACING, PART);
		}

		@Override
		protected IntegerProperty part() {
			return PART;
		}

		@Override
		protected int parts() {
			return 4;
		}

		@Override
		protected BlockState turned(BlockPlaceContext ctx) {
			return defaultBlockState().setValue(FACING, ctx.getHorizontalDirection().getOpposite());
		}
	}

	public static class Lamp extends Tall {
		public static final IntegerProperty PART = IntegerProperty.create("part", 0, 2);

		public Lamp(Properties props) {
			super(props, Block.box(5, 0, 5, 11, 16, 11));
			registerDefaultState(stateDefinition.any().setValue(AXIS, Direction.Axis.X).setValue(PART, 0));
		}

		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
			builder.add(AXIS, PART);
		}

		@Override
		protected IntegerProperty part() {
			return PART;
		}

		@Override
		protected int parts() {
			return 3;
		}

		@Override
		protected BlockState turned(BlockPlaceContext ctx) {
			return defaultBlockState().setValue(AXIS, ctx.getHorizontalDirection().getClockWise().getAxis());
		}

		/** The two cells beside the lanterns (under the arm ends), lit by invisible light blocks so the lamp throws its light wide. */
		public static BlockPos[] glow(BlockPos base, Direction.Axis axis) {
			BlockPos mid = base.above(1);
			Direction d = Direction.get(Direction.AxisDirection.POSITIVE, axis);
			return new BlockPos[] {mid.relative(d), mid.relative(d.getOpposite())};
		}

		@Override
		public void setPlacedBy(Level level, BlockPos pos, BlockState state, LivingEntity by, ItemStack stack) {
			super.setPlacedBy(level, pos, state, by, stack);
			for (BlockPos g : glow(pos, state.getValue(AXIS))) {
				if (level.getBlockState(g).isAir()) level.setBlock(g, LIGHT, Block.UPDATE_ALL);
			}
		}

		@Override
		public BlockState playerWillDestroy(Level level, BlockPos pos, BlockState state, Player player) {
			for (BlockPos g : glow(pos.below(state.getValue(PART)), state.getValue(AXIS))) {
				if (level.getBlockState(g).is(net.minecraft.world.level.block.Blocks.LIGHT)) level.setBlock(g, net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), Block.UPDATE_ALL);
			}
			return super.playerWillDestroy(level, pos, state, player);
		}

		private static final BlockState LIGHT = net.minecraft.world.level.block.Blocks.LIGHT.defaultBlockState()
				.setValue(net.minecraft.world.level.block.LightBlock.LEVEL, 15);
	}

	/**
	 * A market stall (tools/marketprops.py): three blocks wide and three high, its counter facing whoever
	 * placed it, its shelves two blocks behind, the row between left empty for the merchant to stand in
	 * (under the canopy). PART p = (dx + 1) + 3 * dy + 9 * row, dx across the front from the model's
	 * left, row 0 the counter's and 1 the shelves'; the base is the middle of the counter (part 1).
	 * Placed, broken and turned as one.
	 */
	public static class Stall extends Block {
		public static final IntegerProperty PART = IntegerProperty.create("part", 0, 17);

		public Stall(Properties props) {
			super(props);
			registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH).setValue(PART, 1));
		}

		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
			builder.add(FACING, PART);
		}

		static Direction right(Direction f) {
			return switch (f) {
				case EAST -> Direction.SOUTH;
				case SOUTH -> Direction.WEST;
				case WEST -> Direction.NORTH;
				default -> Direction.EAST;
			};
		}

		/** Where part p stands from the base, for a stall facing f. */
		public static BlockPos offset(Direction f, int p) {
			int dx = p % 3 - 1, dy = p / 3 % 3, back = p / 9 * 2;
			Direction r = right(f), b = f.getOpposite();
			return new BlockPos(r.getStepX() * dx + b.getStepX() * back, dy, r.getStepZ() * dx + b.getStepZ() * back);
		}

		/** The merchant's place behind the counter (feet), from the base. */
		public static BlockPos merchant(Direction f) {
			return BlockPos.ZERO.relative(f.getOpposite());
		}

		@Override
		public BlockState getStateForPlacement(BlockPlaceContext ctx) {
			Direction f = ctx.getHorizontalDirection().getOpposite();
			BlockPos pos = ctx.getClickedPos();
			Level level = ctx.getLevel();
			if (pos.getY() + 2 > (level.getMaxBuildHeight() - 1)) return null;
			for (int p = 0; p < 18; p++) {
				if (p != 1 && !level.getBlockState(pos.offset(offset(f, p))).canBeReplaced(ctx)) return null;
			}
			for (int dx = -1; dx <= 1; dx++) {
				for (int dy = 0; dy < 2; dy++) {
					BlockPos m = pos.offset(offset(f, dx + 1)).relative(f.getOpposite()).above(dy);
					if (!level.getBlockState(m).canBeReplaced(ctx)) return null;
				}
			}
			return defaultBlockState().setValue(FACING, f).setValue(PART, 1);
		}

		@Override
		public void setPlacedBy(Level level, BlockPos pos, BlockState state, LivingEntity by, ItemStack stack) {
			Direction f = state.getValue(FACING);
			for (int p = 0; p < 18; p++) {
				if (p != 1) level.setBlock(pos.offset(offset(f, p)), state.setValue(PART, p), Block.UPDATE_ALL);
			}
		}

		@Override
		public BlockState playerWillDestroy(Level level, BlockPos pos, BlockState state, Player player) {
			Direction f = state.getValue(FACING);
			BlockPos base = pos.subtract(offset(f, state.getValue(PART)));
			for (int p = 0; p < 18; p++) {
				BlockPos o = base.offset(offset(f, p));
				if (!o.equals(pos) && level.getBlockState(o).is(this))
					level.setBlock(o, net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), Block.UPDATE_ALL | Block.UPDATE_SUPPRESS_DROPS);
			}
			return super.playerWillDestroy(level, pos, state, player);
		}

		/** A box given for a stall facing north, turned to face f. */
		static VoxelShape turned(Direction f, double x1, double y1, double z1, double x2, double y2, double z2) {
			return switch (f) {
				case EAST -> Block.box(16 - z2, y1, x1, 16 - z1, y2, x2);
				case SOUTH -> Block.box(16 - x2, y1, 16 - z2, 16 - x1, y2, 16 - z1);
				case WEST -> Block.box(z1, y1, 16 - x2, z2, y2, 16 - x1);
				default -> Block.box(x1, y1, z1, x2, y2, z2);
			};
		}

		@Override
		protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
			int p = state.getValue(PART), dy = p / 3 % 3;
			Direction f = state.getValue(FACING);
			VoxelShape packed = PropShapes.of(this, p, f, null);
			if (packed != null) return packed;
			if (p < 9) {
				// the counter, then the posts and rail, then the canopy's slope
				return dy == 0 ? turned(f, 0, 0, 0, 16, 16, 9) : dy == 1 ? turned(f, 0, 0, 0, 16, 16, 3) : turned(f, 0, 0, 0, 16, 10, 16);
			}
			return dy < 2 ? turned(f, 0, 0, 9, 16, 16, 16) : turned(f, 0, 0, 0, 16, 10, 16);
		}

		/** The two lanterns over the merchant light the stall; the candle and lantern sellers' counters glow too. */
		public static int light(BlockState state, boolean bright) {
			int p = state.getValue(PART);
			return p == 12 || p == 14 ? 13 : bright && p < 3 ? 11 : 0;
		}
	}

	/**
	 * The guild's props (tools/guildprops.py): w blocks wide, h high and d deep, facing whoever placed
	 * them. PART p = dx + w * (dy + h * dz), dx to the prop's right as modelled (east when it faces
	 * north), dz going back; the base is the front row's middle (dx = (w - 1) / 2). Placed, broken and
	 * turned as one. The shape is one box per block, given as for a prop facing north.
	 */
	public static class Multi extends Block {
		public static final IntegerProperty PART = IntegerProperty.create("part", 0, 26);
		public final int w, h, d;
		private final double[] box;

		public Multi(Properties props, int w, int h, int d, double... box) {
			super(props);
			this.w = w;
			this.h = h;
			this.d = d;
			this.box = box;
			registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH).setValue(PART, base()));
		}

		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
			builder.add(FACING, PART);
		}

		private int base() {
			return (w - 1) / 2;
		}

		private int parts() {
			return w * h * d;
		}

		/** Where part p stands from the base, for a prop facing f. */
		public BlockPos offset(Direction f, int p) {
			int dx = p % w - base(), dy = p / w % h, dz = p / (w * h);
			Direction r = Stall.right(f), b = f.getOpposite();
			return new BlockPos(r.getStepX() * dx + b.getStepX() * dz, dy, r.getStepZ() * dx + b.getStepZ() * dz);
		}

		@Override
		public BlockState getStateForPlacement(BlockPlaceContext ctx) {
			Direction f = ctx.getHorizontalDirection().getOpposite();
			BlockPos pos = ctx.getClickedPos();
			Level level = ctx.getLevel();
			if (pos.getY() + h - 1 > (level.getMaxBuildHeight() - 1)) return null;
			for (int p = 0; p < parts(); p++) {
				if (p != base() && !level.getBlockState(pos.offset(offset(f, p))).canBeReplaced(ctx)) return null;
			}
			return defaultBlockState().setValue(FACING, f).setValue(PART, base());
		}

		@Override
		public void setPlacedBy(Level level, BlockPos pos, BlockState state, LivingEntity by, ItemStack stack) {
			Direction f = state.getValue(FACING);
			for (int p = 0; p < parts(); p++) {
				if (p != base()) level.setBlock(pos.offset(offset(f, p)), state.setValue(PART, p), Block.UPDATE_ALL);
			}
		}

		@Override
		public BlockState playerWillDestroy(Level level, BlockPos pos, BlockState state, Player player) {
			Direction f = state.getValue(FACING);
			BlockPos origin = pos.subtract(offset(f, state.getValue(PART)));
			for (int p = 0; p < parts(); p++) {
				BlockPos o = origin.offset(offset(f, p));
				if (!o.equals(pos) && level.getBlockState(o).is(this))
					level.setBlock(o, net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), Block.UPDATE_ALL | Block.UPDATE_SUPPRESS_DROPS);
			}
			return super.playerWillDestroy(level, pos, state, player);
		}

		@Override
		protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
			Direction f = state.getValue(FACING);
			return PropShapes.of(this, state.getValue(PART), f, Stall.turned(f, box[0], box[1], box[2], box[3], box[4], box[5]));
		}

		/** A light level for the listed parts, none for the rest. */
		public static java.util.function.ToIntFunction<BlockState> lit(int level, int... parts) {
			return s -> {
				int p = s.getValue(PART);
				for (int q : parts) if (q == p) return level;
				return 0;
			};
		}
	}

	/** One block of the Moonwell Priestess (tools/elfstatue.py in E:/Ashbound); the pieces holding moonwater glow. */
	public static class ElfPiece extends Block {
		public static final IntegerProperty PIECE = IntegerProperty.create("piece", 0, ElfStatue.PIECES - 1);

		public ElfPiece(Properties props) {
			super(props);
			registerDefaultState(stateDefinition.any().setValue(PIECE, 0));
		}

		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
			builder.add(PIECE);
		}

		public static int light(BlockState state) {
			return ElfStatue.glows(state.getValue(PIECE)) ? 10 : 0;
		}
	}

	/**
	 * A sculpted prop (tools/sculpt.py): modelled in Blender, one block model per piece it passes through, facing
	 * north as modelled and turned by FACING. Placed whole by the generators; unbreakable, so nothing is left
	 * hanging. Its glowing pieces give light, some give off embers, steam or sparkles, and a few work as the
	 * station they look like (the great hearth smiths, the anvil repairs, the grindstone grinds, the lectern
	 * enchants, the alchemy bench crafts).
	 */
	public static class Sculpt extends Block {
		public enum Use { NONE, SMITHING, ANVIL, GRINDSTONE, ENCHANTING, CRAFTING }

		public enum Fx { NONE, EMBERS, STEAM, MAGIC, DRIP, MOLTEN }

		private static IntegerProperty making;                 // the piece property of the block being made
		public final IntegerProperty piece;
		private final int light;
		private final Use use;
		private final Fx fx;
		private final BitSet glow = new BitSet(), smoke = new BitSet();

		public static Sculpt make(Properties props, int pieces, int light, Use use, Fx fx, int[] glow, int[] smoke) {
			IntegerProperty piece = IntegerProperty.create("piece", 0, Math.max(1, pieces - 1));
			making = piece;
			BitSet lit = new BitSet();                           // read while the states are built, before the fields exist
			for (int i : glow) lit.set(i);
			return new Sculpt(props.lightLevel(s -> lit.get(s.getValue(piece)) ? light : 0), light, use, fx, glow, smoke);
		}

		private Sculpt(Properties props, int light, Use use, Fx fx, int[] glow, int[] smoke) {
			super(props);
			this.piece = making;
			this.light = light;
			this.use = use;
			this.fx = fx;
			for (int i : glow) this.glow.set(i);
			for (int i : smoke) this.smoke.set(i);
			registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH).setValue(piece, 0));
		}

		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
			builder.add(FACING, making);
		}

		int lightOf(BlockState s) {
			return glow.get(s.getValue(piece)) ? light : 0;
		}

		@Override
		protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
			return PropShapes.of(this, state.getValue(piece), state.getValue(FACING), Shapes.block());
		}

		@Override
		protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
			if (use == Use.NONE) return InteractionResult.PASS;
			if (level.isClientSide) return InteractionResult.SUCCESS;
			ContainerLevelAccess at = ContainerLevelAccess.create(level, pos);
			player.openMenu(switch (use) {
				case SMITHING -> new SimpleMenuProvider((id, inv, p) -> new SmithingMenu(id, inv, at) {
					@Override
					protected boolean isValidBlock(BlockState s) {
						return true;
					}
				}, Component.translatable("container.upgrade"));
				case ANVIL -> new SimpleMenuProvider((id, inv, p) -> new AnvilMenu(id, inv, at) {
					@Override
					protected boolean isValidBlock(BlockState s) {
						return true;
					}
				}, Component.translatable("container.repair"));
				case GRINDSTONE -> new SimpleMenuProvider((id, inv, p) -> new GrindstoneMenu(id, inv, at) {
					@Override
					public boolean stillValid(Player p2) {
						return near(p2, pos);
					}
				}, Component.translatable("container.grindstone_title"));
				case ENCHANTING -> new SimpleMenuProvider((id, inv, p) -> new EnchantmentMenu(id, inv, at) {
					@Override
					public boolean stillValid(Player p2) {
						return near(p2, pos);
					}
				}, Component.translatable("container.enchant"));
				default -> new SimpleMenuProvider((id, inv, p) -> new CraftingMenu(id, inv, at) {
					@Override
					public boolean stillValid(Player p2) {
						return near(p2, pos);
					}
				}, Component.translatable("container.crafting"));
			});
			return InteractionResult.CONSUME;
		}

		static boolean near(Player p, BlockPos pos) {
			return p.distanceToSqr(pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5) <= 64;
		}

		@Override
		public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource r) {
			if (fx == Fx.NONE || !smoke.get(state.getValue(piece))) return;
			double x = pos.getX() + 0.2 + r.nextDouble() * 0.6, y = pos.getY() + 0.3 + r.nextDouble() * 0.6, z = pos.getZ() + 0.2 + r.nextDouble() * 0.6;
			switch (fx) {
				case EMBERS -> {
					if (r.nextInt(3) == 0) level.addParticle(ParticleTypes.SMALL_FLAME, x, y, z, 0, 0.02, 0);
					if (r.nextInt(5) == 0) level.addParticle(ParticleTypes.LAVA, x, y, z, 0, 0, 0);
					if (r.nextInt(2) == 0) level.addParticle(ParticleTypes.SMOKE, x, y + 0.3, z, 0, 0.03, 0);
				}
				case MOLTEN -> {
					if (r.nextInt(3) == 0) level.addParticle(ParticleTypes.LAVA, x, y, z, 0, 0, 0);
					level.addParticle(ParticleTypes.SMOKE, x, y + 0.2, z, 0, 0.02, 0);
				}
				case STEAM -> {
					if (r.nextInt(2) == 0) level.addParticle(ParticleTypes.WHITE_SMOKE, x, y + 0.2, z, 0, 0.025, 0);
				}
				case MAGIC -> {
					level.addParticle(ParticleTypes.ENCHANT, x, y, z, (r.nextDouble() - 0.5) * 0.6, r.nextDouble() * 0.4, (r.nextDouble() - 0.5) * 0.6);
					if (r.nextInt(6) == 0) level.addParticle(ParticleTypes.END_ROD, x, y, z, 0, 0.01, 0);
				}
				case DRIP -> {
					level.addParticle(ParticleTypes.SPLASH, x, pos.getY() + 0.1, z, 0, 0.05, 0);
					if (r.nextInt(3) == 0) level.addParticle(ParticleTypes.BUBBLE_POP, x, pos.getY() + 0.1, z, 0, 0.02, 0);
				}
				default -> { }
			}
		}
	}
}
