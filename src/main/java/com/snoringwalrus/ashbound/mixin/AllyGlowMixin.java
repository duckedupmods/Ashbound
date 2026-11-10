package com.snoringwalrus.ashbound.mixin;

import com.snoringwalrus.ashbound.client.HudPrefs;

import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Glowing allies (the Skill effects screen): your party members outlined for you, through walls (11/7). Nobody else sees it. */
@Mixin(Minecraft.class)
public abstract class AllyGlowMixin {
	@Inject(method = "shouldEntityAppearGlowing", at = @At("HEAD"), cancellable = true)
	private void ashbound$allies(Entity e, CallbackInfoReturnable<Boolean> cir) {
		if (HudPrefs.glowsForMe(e)) cir.setReturnValue(true);
	}
}
