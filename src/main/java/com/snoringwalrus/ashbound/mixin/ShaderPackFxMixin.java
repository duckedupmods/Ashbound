package com.snoringwalrus.ashbound.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import com.snoringwalrus.ashbound.client.ShaderPacks;

import net.minecraft.client.DeltaTracker;
import net.minecraft.client.renderer.GameRenderer;

/** The first moment a shader pack's frame is whole: our effects go over it here (client/ShaderPacks). */
@Mixin(GameRenderer.class)
abstract class ShaderPackFxMixin {
	@Inject(method = "renderLevel", at = @At("TAIL"))
	private void ashbound$effects(DeltaTracker delta, CallbackInfo ci) {
		ShaderPacks.present();
	}
}
