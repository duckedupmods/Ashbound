package com.snoringwalrus.ashbound.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import net.minecraft.world.item.ItemStack;

/** Nothing wears out, from any mod. The second is for what was already worn: no bar on it. */
@Mixin(ItemStack.class)
public abstract class NoWearMixin {
	@Inject(method = "isDamageableItem", at = @At("HEAD"), cancellable = true)
	private void ashbound$noWear(CallbackInfoReturnable<Boolean> ci) {
		ci.setReturnValue(false);
	}

	@Inject(method = "isDamaged", at = @At("HEAD"), cancellable = true)
	private void ashbound$neverWorn(CallbackInfoReturnable<Boolean> ci) {
		ci.setReturnValue(false);
	}
}
