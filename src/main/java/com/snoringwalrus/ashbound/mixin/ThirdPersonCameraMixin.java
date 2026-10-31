package com.snoringwalrus.ashbound.mixin;

import net.minecraft.client.Camera;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * The third-person camera in a forest or a cave: vanilla snaps it in and out every frame as blocks pass behind you.
 * Here leaves don't stop it at all, and while it still comes in at once for rock, so you never see through the
 * ground, it only drifts back out, so a gap flashing past doesn't throw it around.
 */
@Mixin(Camera.class)
public abstract class ThirdPersonCameraMixin {
	/** Blocks a second it drifts back out; after this long unused (first person, a menu) it starts fresh. */
	@Unique private static final float ashbound$OUT = 2.5f;
	@Unique private static final long ashbound$STALE = 500_000_000L;
	@Unique private float ashbound$zoom = -1;
	@Unique private long ashbound$last;

	@Shadow private Entity entity;

	@Redirect(method = "getMaxZoom", require = 0, at = @At(value = "INVOKE",
			target = "Lnet/minecraft/world/level/BlockGetter;clip(Lnet/minecraft/world/level/ClipContext;)Lnet/minecraft/world/phys/BlockHitResult;"))
	private BlockHitResult ashbound$throughLeaves(BlockGetter level, ClipContext ctx) {
		Vec3 from = ctx.getFrom(), to = ctx.getTo(), way = to.subtract(from).normalize();
		BlockHitResult hit = level.clip(ctx);
		for (int i = 0; i < 24 && hit.getType() != HitResult.Type.MISS && level.getBlockState(hit.getBlockPos()).is(BlockTags.LEAVES); i++) {
			from = hit.getLocation().add(way.scale(0.05));
			if (from.distanceToSqr(ctx.getFrom()) >= to.distanceToSqr(ctx.getFrom())) return BlockHitResult.miss(to, hit.getDirection(), hit.getBlockPos());
			// on through this leaf block to the next thing
			hit = level.clip(new ClipContext(ashbound$pastBlock(from, way, hit), to, ClipContext.Block.VISUAL, ClipContext.Fluid.NONE, entity));
		}
		return hit;
	}

	/** The first point along the way that's out of the block just hit. */
	@Unique
	private static Vec3 ashbound$pastBlock(Vec3 from, Vec3 way, BlockHitResult hit) {
		Vec3 at = from;
		for (int i = 0; i < 40 && net.minecraft.core.BlockPos.containing(at).equals(hit.getBlockPos()); i++) at = at.add(way.scale(0.05));
		return at;
	}

	@Inject(method = "getMaxZoom", require = 0, at = @At("RETURN"), cancellable = true)
	private void ashbound$ease(float wanted, CallbackInfoReturnable<Float> cir) {
		float want = cir.getReturnValueF();
		long now = System.nanoTime();
		float dt = (now - ashbound$last) / 1e9f;
		if (ashbound$zoom < 0 || now - ashbound$last > ashbound$STALE) ashbound$zoom = want;
		ashbound$last = now;
		ashbound$zoom = want < ashbound$zoom ? want : Math.min(want, ashbound$zoom + ashbound$OUT * dt);
		cir.setReturnValue(ashbound$zoom);
	}
}
