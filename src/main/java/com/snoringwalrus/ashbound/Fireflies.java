package com.snoringwalrus.ashbound;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;

/**
 * Fireflies over the elves' floors, glade and pool: an invisible, airy block (tools/villages.py scatters them) that
 * now and then lets a firefly go - a soft glowing mote that drifts and blinks (client/GateParticles.Firefly). More of
 * them after dusk.
 */
public final class Fireflies extends Block {
	public static final DeferredHolder<net.minecraft.core.particles.ParticleType<?>, SimpleParticleType> MOTE =
			Gates.PARTICLES.register("firefly", () -> new SimpleParticleType(false));
	static final DeferredBlock<Block> BLOCK = WorldBlocks.BLOCKS.registerBlock("fireflies", Fireflies::new,
			BlockBehaviour.Properties.of().noCollission().noOcclusion().noLootTable().replaceable().instabreak());

	/** loads the class so its block and particle are in the registers before they're handed to the bus */
	static void init() {
	}

	public Fireflies(Properties props) {
		super(props);
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
	public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
		long t = level.getDayTime() % 24000;
		boolean dark = t > 12500 && t < 23500;
		if (random.nextFloat() > (dark ? 0.9f : 0.3f)) return;
		for (int i = dark ? 2 : 1; i > 0; i--)
			level.addParticle(MOTE.get(), pos.getX() + random.nextDouble() * 3 - 1, pos.getY() + random.nextDouble() * 2,
					pos.getZ() + random.nextDouble() * 3 - 1, 0, 0, 0);
	}
}
