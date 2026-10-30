package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

import com.mojang.serialization.MapCodec;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.Containers;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.ChainBlock;
import net.minecraft.world.level.block.FenceBlock;
import net.minecraft.world.level.block.IronBarsBlock;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.WebBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.entity.RandomizableContainerBlockEntity;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;

/**
 * The Silk Archive's own fittings (models and textures from tools/silkprops.py), so the dungeon shows no vanilla
 * block: web, cable, chain, lantern, grille, plate, rail, beam, lectern, reading chair and the coffer that holds
 * its loot.
 */
public final class SilkProps {
	private SilkProps() {}

	private static BlockBehaviour.Properties pewter() {
		return BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(3f, 6f).sound(SoundType.CHAIN).noOcclusion();
	}

	private static DeferredBlock<Block> block(String name, Function<BlockBehaviour.Properties, ? extends Block> make, BlockBehaviour.Properties props) {
		DeferredBlock<Block> b = WorldBlocks.BLOCKS.registerBlock(name, make::apply, props);
		WorldBlocks.ITEMS.add(Weapons.ITEMS.registerSimpleBlockItem(b));
		return b;
	}

	/** Loads the class, so its blocks are registered. */
	static void init() {}

	static final DeferredBlock<Block> SILK_WEB = block("silk_web", p -> new WebBlock(p) {}, BlockBehaviour.Properties.of()
			.mapColor(MapColor.WOOL).forceSolidOn().noCollission().requiresCorrectToolForDrops().strength(4f).noOcclusion());
	static final DeferredBlock<Block> SILK_CABLE = block("silk_cable", Block::new, BlockBehaviour.Properties.of()
			.mapColor(MapColor.WOOL).strength(0.8f).sound(SoundType.WOOL).ignitedByLava());
	static final DeferredBlock<Block> ARCHIVE_CHAIN = block("archive_chain", ChainBlock::new, pewter());
	static final DeferredBlock<Block> ARCHIVE_LANTERN = block("archive_lantern", LanternBlock::new, BlockBehaviour.Properties.of()
			.mapColor(MapColor.METAL).strength(3.5f).sound(SoundType.LANTERN).lightLevel(s -> 14).noOcclusion());
	static final DeferredBlock<Block> ARCHIVE_GRILLE = block("archive_grille", p -> new IronBarsBlock(p) {}, pewter());
	static final DeferredBlock<Block> ARCHIVE_IRON = block("archive_iron", Block::new, BlockBehaviour.Properties.of()
			.mapColor(MapColor.METAL).strength(5f, 6f).sound(SoundType.METAL).requiresCorrectToolForDrops());
	static final DeferredBlock<Block> WALNUT_FENCE = block("walnut_fence", FenceBlock::new, BlockBehaviour.Properties.of()
			.mapColor(MapColor.COLOR_BROWN).strength(2f, 3f).sound(SoundType.WOOD).ignitedByLava().noOcclusion());
	static final DeferredBlock<Block> WALNUT_BEAM = block("walnut_beam", RotatedPillarBlock::new, BlockBehaviour.Properties.of()
			.mapColor(MapColor.COLOR_BROWN).strength(2f).sound(SoundType.WOOD).ignitedByLava());
	static final DeferredBlock<Block> ARCHIVE_LECTERN = block("archive_lectern",
			p -> new PropBlock.Facing(p, Block.box(2, 0, 2, 14, 13, 14)), BlockBehaviour.Properties.of()
					.mapColor(MapColor.COLOR_BROWN).strength(2f, 3f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> ARCHIVE_CHAIR = block("archive_chair",
			p -> new PropBlock.Facing(p, Block.box(1.5, 0, 1.5, 14.5, 9, 14.5)), BlockBehaviour.Properties.of()
					.mapColor(MapColor.COLOR_BROWN).strength(2f, 3f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> ARCHIVE_COFFER = block("archive_coffer", Coffer::new, BlockBehaviour.Properties.of()
			.mapColor(MapColor.COLOR_BROWN).strength(2.5f).sound(SoundType.WOOD).noOcclusion());

	// the sculpted ones (tools/blender/silk_assets.py, tools/silkmeshes.py)
	static final DeferredBlock<Block> COCOON = block("cocoon", Cocoon::new, BlockBehaviour.Properties.of()
			.mapColor(MapColor.WOOL).strength(1.2f).sound(SoundType.WOOL).ignitedByLava().noOcclusion());
	static final DeferredBlock<Block> ARCHIVE_PAPERS = block("archive_papers", Papers::new, BlockBehaviour.Properties.of()
			.mapColor(MapColor.SAND).strength(0.3f).sound(SoundType.WOOL).ignitedByLava().noOcclusion().noCollission());
	static final DeferredBlock<Block> PAPER_REAM = block("paper_ream", p -> new PropBlock.Facing(p, Block.box(0, 0, 0, 16, 16, 16)),
			BlockBehaviour.Properties.of().mapColor(MapColor.SAND).strength(0.8f).sound(SoundType.WOOL).ignitedByLava().noOcclusion());
	static final DeferredBlock<Block> MOONGLASS_LAMP = block("moonglass_lamp", p -> new Block(p) {
		@Override
		protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
			return LAMP_SHAPE;
		}
	}, BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(2f, 6f).sound(SoundType.LANTERN).lightLevel(s -> 15).noOcclusion());
	private static final VoxelShape LAMP_SHAPE = Block.box(3, 1, 3, 13, 16, 13);

	static final DeferredHolder<BlockEntityType<?>, BlockEntityType<CofferEntity>> COFFER = ClockHands.TYPES.register("archive_coffer",
			() -> {
				// the archive's coffer and every gate's own (GateBlocks), all one kind of chest
				List<Block> all = new ArrayList<>(List.of(ARCHIVE_COFFER.get()));
				GateBlocks.COFFERS.forEach(c -> all.add(c.get()));
				return BlockEntityType.Builder.of(CofferEntity::new, all.toArray(Block[]::new)).build(null);
			});

	public enum Pose implements StringRepresentable {
		STAND, SEAT, HANG, PRESSED, UPPER;

		@Override
		public String getSerializedName() {
			return name().toLowerCase(java.util.Locale.ROOT);
		}
	}

	public static final EnumProperty<Pose> POSE = EnumProperty.create("pose", Pose.class);

	/** Someone wound in silk: standing (two blocks), sat in a chair, hung from the web (three), crushed in a press.
	 *  The blocks a tall one reaches into are "upper": nothing of their own drawn, just there to bump into. */
	public static class Cocoon extends Block {
		private static final VoxelShape BODY = Block.box(3, 0, 3, 13, 16, 13);
		private static final VoxelShape SEAT = Block.box(3, 0, 3, 13, 13, 13);
		private static final VoxelShape HANG = Block.box(4, 0, 4, 12, 16, 12);

		public Cocoon(Properties props) {
			super(props);
			registerDefaultState(stateDefinition.any().setValue(PropBlock.FACING, Direction.NORTH).setValue(POSE, Pose.PRESSED));
		}

		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
			builder.add(PropBlock.FACING, POSE);
		}

		@Override
		public BlockState getStateForPlacement(BlockPlaceContext ctx) {
			return defaultBlockState().setValue(PropBlock.FACING, ctx.getHorizontalDirection().getOpposite());
		}

		@Override
		protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
			return switch (state.getValue(POSE)) {
				case SEAT -> SEAT;
				case HANG -> HANG;
				case PRESSED -> Shapes.block();
				default -> BODY;
			};
		}
	}

	/** Papers left on a desk or dropped on the floor: low when they lie on a slab, half a block down. */
	public static class Papers extends Block {
		public static final BooleanProperty LOW = BooleanProperty.create("low");
		private static final VoxelShape FLAT = Block.box(1, 0, 1, 15, 3, 15);
		private static final VoxelShape FLAT_LOW = Block.box(1, -8, 1, 15, -5, 15);

		public Papers(Properties props) {
			super(props);
			registerDefaultState(stateDefinition.any().setValue(PropBlock.FACING, Direction.NORTH).setValue(LOW, false));
		}

		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
			builder.add(PropBlock.FACING, LOW);
		}

		@Override
		public BlockState getStateForPlacement(BlockPlaceContext ctx) {
			return defaultBlockState().setValue(PropBlock.FACING, ctx.getHorizontalDirection().getOpposite());
		}

		@Override
		protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
			return state.getValue(LOW) ? FLAT_LOW : FLAT;
		}
	}

	/** A three-row chest drawn by its own model; the lair fills it from a loot table like any chest. */
	public static class Coffer extends BaseEntityBlock {
		private static final MapCodec<Coffer> CODEC = simpleCodec(Coffer::new);
		private static final VoxelShape SHAPE = Block.box(1, 0, 1.5, 15, 14, 14.5);
		private static final VoxelShape SHAPE_X = Block.box(1.5, 0, 1, 14.5, 14, 15);

		public Coffer(Properties props) {
			super(props);
			registerDefaultState(stateDefinition.any().setValue(PropBlock.FACING, Direction.NORTH));
		}

		@Override
		protected MapCodec<? extends BaseEntityBlock> codec() {
			return CODEC;
		}

		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
			builder.add(PropBlock.FACING);
		}

		@Override
		public BlockState getStateForPlacement(BlockPlaceContext ctx) {
			return defaultBlockState().setValue(PropBlock.FACING, ctx.getHorizontalDirection().getOpposite());
		}

		@Override
		protected RenderShape getRenderShape(BlockState state) {
			return RenderShape.MODEL;
		}

		@Override
		protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
			return state.getValue(PropBlock.FACING).getAxis() == Direction.Axis.Z ? SHAPE : SHAPE_X;
		}

		@Override
		public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
			return new CofferEntity(pos, state);
		}

		@Override
		protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
			if (!level.isClientSide && level.getBlockEntity(pos) instanceof CofferEntity c) player.openMenu(c);
			return InteractionResult.sidedSuccess(level.isClientSide);
		}

		@Override
		protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean moved) {
			Containers.dropContentsOnDestroy(state, newState, level, pos);
			super.onRemove(state, level, pos, newState, moved);
		}
	}

	/** a boss's hoard: the coffer two blocks wide and higher, across the way it faces */
	public static class Hoard extends Coffer {
		private static final MapCodec<Hoard> CODEC = simpleCodec(Hoard::new);
		private static final VoxelShape SHAPE = Block.box(-7, 0, 1, 23, 19, 15);
		private static final VoxelShape SHAPE_X = Block.box(1, 0, -7, 15, 19, 23);

		public Hoard(Properties props) {
			super(props);
		}

		@Override
		protected MapCodec<? extends BaseEntityBlock> codec() {
			return CODEC;
		}

		@Override
		protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
			return state.getValue(PropBlock.FACING).getAxis() == Direction.Axis.Z ? SHAPE : SHAPE_X;
		}
	}

	public static class CofferEntity extends RandomizableContainerBlockEntity {
		private NonNullList<ItemStack> items = NonNullList.withSize(27, ItemStack.EMPTY);

		public CofferEntity(BlockPos pos, BlockState state) {
			super(COFFER.get(), pos, state);
		}

		@Override
		protected NonNullList<ItemStack> getItems() {
			return items;
		}

		@Override
		protected void setItems(NonNullList<ItemStack> items) {
			this.items = items;
		}

		@Override
		protected Component getDefaultName() {
			return Component.translatable("container.ashbound.archive_coffer");
		}

		@Override
		protected AbstractContainerMenu createMenu(int id, Inventory inv) {
			return ChestMenu.threeRows(id, inv, this);
		}

		@Override
		public int getContainerSize() {
			return 27;
		}

		@Override
		protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
			super.loadAdditional(tag, registries);
			items = NonNullList.withSize(getContainerSize(), ItemStack.EMPTY);
			if (!tryLoadLootTable(tag)) ContainerHelper.loadAllItems(tag, items, registries);
		}

		@Override
		protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
			super.saveAdditional(tag, registries);
			if (!trySaveLootTable(tag)) ContainerHelper.saveAllItems(tag, items, registries);
		}
	}
}
