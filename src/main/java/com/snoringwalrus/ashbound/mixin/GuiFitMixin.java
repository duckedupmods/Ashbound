package com.snoringwalrus.ashbound.mixin;

import com.mojang.blaze3d.platform.Window;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/**
 * Our screens and HUD are laid out for at least this much room. In a small window the GUI scale would leave less, and things run
 * into each other; here it comes down just far enough, a fraction if need be, so all of it always fits. A window with room is left
 * at whatever the player chose.
 */
@Mixin(Window.class)
public abstract class GuiFitMixin {
	@Unique private static final double ashbound$MIN_W = 440, ashbound$MIN_H = 270;

	@Shadow
	public abstract int getWidth();

	@Shadow
	public abstract int getHeight();

	@ModifyVariable(method = "setGuiScale", at = @At("HEAD"), argsOnly = true)
	private double ashbound$fit(double scale) {
		return Math.max(1, Math.min(scale, Math.min(getWidth() / ashbound$MIN_W, getHeight() / ashbound$MIN_H)));
	}
}
