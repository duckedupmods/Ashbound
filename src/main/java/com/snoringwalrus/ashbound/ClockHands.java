package com.snoringwalrus.ashbound;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.Sheets;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.client.resources.model.ModelResourceLocation;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * The guild belfry's clock hands: an invisible block in front of the dial's middle (the dial is the clock_face prop),
 * whose renderer turns the two hand models (tools/blender/civic_sculpt.py) to the world's time, the minute hand
 * once round every in-game hour. Faces the way the dial does.
 */
public final class ClockHands extends Block implements EntityBlock {
	static final DeferredRegister<BlockEntityType<?>> TYPES = DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE, Ashbound.ID);
	static final DeferredBlock<Block> BLOCK = WorldBlocks.BLOCKS.registerBlock("clock_hands", ClockHands::new,
			BlockBehaviour.Properties.of().strength(-1f, 3600000f).noCollission().noOcclusion().noLootTable());
	static final DeferredHolder<BlockEntityType<?>, BlockEntityType<Entity>> ENTITY = TYPES.register("clock_hands",
			() -> BlockEntityType.Builder.of(Entity::new, BLOCK.get()).build(null));

	/** the hands' models: their own class, so a dedicated server (no client classes) never loads it */
	static final class Models {
		static final ModelResourceLocation MINUTE = model("clock_hand_minute_0"), HOUR = model("clock_hand_hour_0");

		private static ModelResourceLocation model(String name) {
			return ModelResourceLocation.standalone(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "block/" + name));
		}
	}

	public ClockHands(Properties props) {
		super(props);
		registerDefaultState(stateDefinition.any().setValue(PropBlock.FACING, Direction.NORTH));
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
		return RenderShape.INVISIBLE;
	}

	@Override
	protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
		return Shapes.empty();
	}

	@Override
	public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
		return new Entity(pos, state);
	}

	public static final class Entity extends BlockEntity {
		public Entity(BlockPos pos, BlockState state) {
			super(ENTITY.get(), pos, state);
		}
	}

	/** Draws the hands, set back into the dial's bezel; time 0 is six in the morning. */
	public static final class Renderer implements BlockEntityRenderer<Entity> {
		static final float SCALE = 4.5f, PX = 0.5f, PY = 0.2f;

		@Override
		public void render(Entity be, float partial, PoseStack pose, MultiBufferSource buffers, int light, int overlay) {
			if (be.getLevel() == null) return;
			double t = be.getLevel().getDayTime() % 24000L + (be.getLevel().getGameRules().getBoolean(net.minecraft.world.level.GameRules.RULE_DAYLIGHT) ? partial : 0);
			float minute = (float) (t % 1000.0 / 1000.0 * 360.0);
			float hour = (float) (((t / 1000.0 + 6.0) % 12.0) / 12.0 * 360.0);
			Direction f = be.getBlockState().getValue(PropBlock.FACING);
			pose.pushPose();
			pose.translate(0.5, 0.5, 0.5);
			pose.mulPose(Axis.YP.rotationDegrees(180f - f.toYRot()));
			pose.translate(-0.5, -0.5, -0.5);
			hand(Models.HOUR, hour, 1.22f, pose, buffers, light, overlay);
			hand(Models.MINUTE, minute, 1.12f, pose, buffers, light, overlay);
			pose.popPose();
		}

		private static void hand(ModelResourceLocation where, float angle, float depth, PoseStack pose, MultiBufferSource buffers, int light, int overlay) {
			BakedModel m = Minecraft.getInstance().getModelManager().getModel(where);
			pose.pushPose();
			pose.translate(0.5, 0.5, depth);
			pose.mulPose(Axis.ZP.rotationDegrees(angle));
			pose.scale(SCALE, SCALE, 1f);
			pose.translate(-PX, -PY, 0);
			Minecraft.getInstance().getBlockRenderer().getModelRenderer().renderModel(pose.last(), buffers.getBuffer(Sheets.cutoutBlockSheet()),
					null, m, 1f, 1f, 1f, light, overlay);
			pose.popPose();
		}

		@Override
		public AABB getRenderBoundingBox(Entity be) {
			return new AABB(be.getBlockPos()).inflate(5);
		}

		@Override
		public int getViewDistance() {
			return 256;
		}
	}
}
