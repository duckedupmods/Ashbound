package com.snoringwalrus.ashbound.mixin;

import com.snoringwalrus.ashbound.client.CharacterScreen;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** BetterLockOn fades you out when the camera's right up against you, and that fade reaches the doll on the Character screen too. */
@Pseudo
@Mixin(targets = "net.shelmarow.betterlockon.client.control.LockOnControl", remap = false)
public abstract class DollFadeMixin {
	@Inject(method = "getModelAlpha", at = @At("HEAD"), cancellable = true, require = 0)
	private static void ashbound$solidDoll(double distance, CallbackInfoReturnable<Float> ci) {
		if (CharacterScreen.drawingDoll) ci.setReturnValue(1f);
	}
}
