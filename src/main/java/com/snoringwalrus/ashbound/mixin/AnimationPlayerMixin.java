package com.snoringwalrus.ashbound.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import com.snoringwalrus.ashbound.HitStop;

import yesman.epicfight.api.animation.AnimationPlayer;
import yesman.epicfight.world.capabilities.entitypatch.LivingEntityPatch;

/** HitStop: an Epic Fight animation stands still while it's held, then runs two ticks to one until it's caught up. */
@Mixin(value = AnimationPlayer.class, remap = false)
public abstract class AnimationPlayerMixin {
	@Shadow
	protected float elapsedTime;
	@Shadow
	protected float prevElapsedTime;
	@Shadow
	protected boolean isEnd;
	@Unique
	private boolean ashbound$again;

	@Shadow
	public abstract void tick(LivingEntityPatch<?> patch);

	@Inject(method = "tick", at = @At("HEAD"), cancellable = true, require = 0)
	private void ashbound$hold(LivingEntityPatch<?> patch, CallbackInfo ci) {
		if (!ashbound$again && HitStop.held(patch.getOriginal())) {
			prevElapsedTime = elapsedTime;
			ci.cancel();
		}
	}

	@Inject(method = "tick", at = @At("TAIL"), require = 0)
	private void ashbound$catchUp(LivingEntityPatch<?> patch, CallbackInfo ci) {
		if (ashbound$again || isEnd || !HitStop.owes(patch.getOriginal())) return;
		float from = prevElapsedTime;
		ashbound$again = true;
		tick(patch);
		ashbound$again = false;
		prevElapsedTime = from;   // the swing's hit box sweeps both ticks
	}
}
