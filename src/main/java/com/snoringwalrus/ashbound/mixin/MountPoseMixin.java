package com.snoringwalrus.ashbound.mixin;

import com.snoringwalrus.ashbound.client.MountPose;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import yesman.epicfight.api.animation.Animator;
import yesman.epicfight.api.animation.Pose;
import yesman.epicfight.api.client.animation.ClientAnimator;

/** The one place every pose passes, blends between clips included. See client.MountPose. */
@Mixin(ClientAnimator.class)
public abstract class MountPoseMixin {
	@Inject(method = "getPose(FZ)Lyesman/epicfight/api/animation/Pose;", at = @At("RETURN"))
	private void ashbound$mount(float partial, boolean composed, CallbackInfoReturnable<Pose> cir) {
		MountPose.apply(((Animator) (Object) this).getEntityPatch(), cir.getReturnValue(), partial);
	}
}
