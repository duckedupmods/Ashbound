package com.snoringwalrus.ashbound.mixin;

import net.minecraft.client.Camera;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * The third-person camera in a forest or a cave: vanilla snaps it in and out every frame as blocks pass behind you.
 * Here leaves and thin trunks don't stop it at all. Anything else eases it in, and it waits a moment before it drifts back
 * out, so a post or a branch flashing past doesn't saw it back and forth. It only snaps when it would otherwise end up
 * inside something, so you never see through the ground.
 */
@Mixin(Camera.class)
public abstract class ThirdPersonCameraMixin {
	/** Blocks a second in and out, how long it waits before going back out, and after how long unused (first person, a menu) it starts fresh. */
	@Unique private static final float ashbound$IN = 14, ashbound$OUT = 2.5f, ashbound$OUT_SLOWEST = 0.3f;
	@Unique private static final long ashbound$HOLD = 350_000_000L, ashbound$STALE = 500_000_000L;
	/** Blocks of trunk it'll look through, and half the size of the camera, near enough. */
	@Unique private static final int ashbound$TRUNK = 2;
	@Unique private static final double ashbound$SIZE = 0.15;
	@Unique private float ashbound$zoom = -1;
	@Unique private long ashbound$last, ashbound$until;

	@Shadow private Entity entity;
	@Shadow private Vec3 position;
	@Shadow private BlockGetter level;
	@Shadow @Final private Vector3f forwards;

	@Redirect(method = "getMaxZoom", at = @At(value = "INVOKE",
			target = "Lnet/minecraft/world/level/BlockGetter;clip(Lnet/minecraft/world/level/ClipContext;)Lnet/minecraft/world/phys/BlockHitResult;"))
	private BlockHitResult ashbound$throughTrees(BlockGetter level, ClipContext ctx) {
		Vec3 from = ctx.getFrom(), to = ctx.getTo(), way = to.subtract(from).normalize();
		BlockPos end = BlockPos.containing(to);
		BlockHitResult hit = level.clip(ctx), firstLog = null;
		int logs = 0;
		for (int i = 0; i < 24 && hit.getType() != HitResult.Type.MISS; i++) {
			BlockState block = level.getBlockState(hit.getBlockPos());
			if (block.is(BlockTags.LOGS)) {
				if (firstLog == null) firstLog = hit;
				// a tree you can see round, but the camera mustn't stop inside one
				if (++logs > ashbound$TRUNK) return firstLog;
				if (hit.getBlockPos().equals(end)) return hit;
			} else if (!block.is(BlockTags.LEAVES)) return hit;
			from = hit.getLocation().add(way.scale(0.05));
			if (from.distanceToSqr(ctx.getFrom()) >= to.distanceToSqr(ctx.getFrom())) return BlockHitResult.miss(to, hit.getDirection(), hit.getBlockPos());
			// on through this block to the next thing
			hit = level.clip(new ClipContext(ashbound$pastBlock(from, way, hit), to, ClipContext.Block.VISUAL, ClipContext.Fluid.NONE, entity));
		}
		return hit;
	}

	/** The first point along the way that's out of the block just hit. */
	@Unique
	private static Vec3 ashbound$pastBlock(Vec3 from, Vec3 way, BlockHitResult hit) {
		Vec3 at = from;
		for (int i = 0; i < 40 && BlockPos.containing(at).equals(hit.getBlockPos()); i++) at = at.add(way.scale(0.05));
		return at;
	}

	/** Would the camera be inside something, this far back? */
	@Unique
	private boolean ashbound$buried(float back) {
		Vec3 at = position.add(new Vec3(forwards).scale(-back));
		for (int i = 0; i < 8; i++) {
			BlockPos p = BlockPos.containing(at.x + ((i & 1) * 2 - 1) * ashbound$SIZE, at.y + ((i >> 1 & 1) * 2 - 1) * ashbound$SIZE, at.z + ((i >> 2 & 1) * 2 - 1) * ashbound$SIZE);
			if (level.getBlockState(p).isSolidRender(level, p)) return true;
		}
		return false;
	}

	@Inject(method = "getMaxZoom", require = 0, at = @At("RETURN"), cancellable = true)
	private void ashbound$ease(float wanted, CallbackInfoReturnable<Float> cir) {
		float want = cir.getReturnValueF();
		long now = System.nanoTime();
		float dt = (now - ashbound$last) / 1e9f;
		if (ashbound$zoom < 0 || now - ashbound$last > ashbound$STALE) ashbound$zoom = want;
		ashbound$last = now;
		if (want < ashbound$zoom) {
			ashbound$until = now + ashbound$HOLD;
			ashbound$zoom = Math.max(want, ashbound$zoom - ashbound$IN * dt);
			if (ashbound$buried(ashbound$zoom)) ashbound$zoom = want;
		} else if (now >= ashbound$until) {
			float gap = want - ashbound$zoom;
			ashbound$zoom = Math.min(want, ashbound$zoom + Math.max(ashbound$OUT_SLOWEST, Math.min(ashbound$OUT, gap * 3)) * dt);
		}
		cir.setReturnValue(ashbound$zoom);
	}
}
