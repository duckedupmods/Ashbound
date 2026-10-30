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

/**
 * The villages' moving parts (tools/blender/village_props.py): an invisible hub block whose renderer turns its model
 * with the world's clock - the windmill's sails on the cap's hub, the mill's wheel in its race, the lake's bell rocking
 * on its yoke. Each faces the way its model's front should look; neighbours fall out of step by where they stand.
 */
public final class VillageSpin extends Block implements EntityBlock {
	enum Kind {
		/** model, degrees a tick (or the swing's amplitude for the bell), how far the model reaches past its block */
		SAILS("windmill_sails", 1.2f, 12), WHEEL("water_wheel", -2.4f, 6), BELL("village_bell", 14f, 2);

		final String model;
		final float speed;
		final int reach;

		Kind(String model, float speed, int reach) {
			this.model = model;
			this.speed = speed;
			this.reach = reach;
		}
	}

	static final DeferredBlock<Block> WINDMILL = hub("windmill_hub", Kind.SAILS);
	static final DeferredBlock<Block> WHEEL = hub("wheel_hub", Kind.WHEEL);
	static final DeferredBlock<Block> BELL = hub("bell_hook", Kind.BELL);
	static final DeferredHolder<BlockEntityType<?>, BlockEntityType<Entity>> ENTITY = ClockHands.TYPES.register("village_spin",
			() -> BlockEntityType.Builder.of(Entity::new, WINDMILL.get(), WHEEL.get(), BELL.get()).build(null));

	/** loads the class so its blocks are in the register before it's handed to the bus */
	static void init() {
	}

	private static DeferredBlock<Block> hub(String name, Kind kind) {
		return WorldBlocks.BLOCKS.registerBlock(name, p -> new VillageSpin(p, kind),
				BlockBehaviour.Properties.of().strength(-1f, 3600000f).noCollission().noOcclusion().noLootTable());
	}

	/** the models by name: their own class, so a dedicated server never loads client classes */
	static final class Models {
		static final ModelResourceLocation SAILS = model("windmill_sails"), WHEEL = model("water_wheel"), BELL = model("village_bell");

		private static ModelResourceLocation model(String name) {
			return ModelResourceLocation.standalone(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "block/" + name));
		}

		static ModelResourceLocation of(Kind k) {
			return switch (k) {
				case SAILS -> SAILS;
				case WHEEL -> WHEEL;
				case BELL -> BELL;
			};
		}
	}

	final Kind kind;

	public VillageSpin(Properties props, Kind kind) {
		super(props);
		this.kind = kind;
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

	/**
	 * The sails and the wheel are built round their axle at the model's origin, the axle along z (out of the front);
	 * the bell sits in its block with the yoke's axle along x at (y 1.13, z 0.5) and rocks about it.
	 */
	public static final class Renderer implements BlockEntityRenderer<Entity> {
		@Override
		public void render(Entity be, float partial, PoseStack pose, MultiBufferSource buffers, int light, int overlay) {
			if (be.getLevel() == null || !(be.getBlockState().getBlock() instanceof VillageSpin spin)) return;
			BlockPos p = be.getBlockPos();
			float t = (be.getLevel().getGameTime() % 72000L) + partial + (p.getX() * 37 + p.getZ() * 91 & 255);
			Direction f = be.getBlockState().getValue(PropBlock.FACING);
			BakedModel m = Minecraft.getInstance().getModelManager().getModel(Models.of(spin.kind));
			pose.pushPose();
			pose.translate(0.5, 0.5, 0.5);
			pose.mulPose(Axis.YP.rotationDegrees(180f - f.toYRot()));
			if (spin.kind == Kind.BELL) {
				float swing = spin.kind.speed * (float) Math.sin(t * 2 * Math.PI / 90.0) * (0.6f + 0.4f * (float) Math.sin(t / 400.0));
				pose.translate(-0.5, -0.5, -0.5);
				pose.translate(0, 1.13, 0.5);
				pose.mulPose(Axis.XP.rotationDegrees(swing));
				pose.translate(0, -1.13, -0.5);
			} else {
				pose.mulPose(Axis.ZP.rotationDegrees(t * spin.kind.speed % 360f));
			}
			Minecraft.getInstance().getBlockRenderer().getModelRenderer().renderModel(pose.last(), buffers.getBuffer(Sheets.cutoutBlockSheet()),
					null, m, 1f, 1f, 1f, light, overlay);
			pose.popPose();
		}

		@Override
		public AABB getRenderBoundingBox(Entity be) {
			return new AABB(be.getBlockPos()).inflate(be.getBlockState().getBlock() instanceof VillageSpin s ? s.kind.reach : 2);
		}

		@Override
		public int getViewDistance() {
			return 192;
		}
	}
}
