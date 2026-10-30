package com.snoringwalrus.ashbound.mixin;

import com.snoringwalrus.ashbound.Capital;
import net.minecraft.world.level.levelgen.NoiseChunk;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Where the ground is once the capital's shaped it: the surface rules lay grass on it, the aquifers keep off it. */
@Mixin(NoiseChunk.class)
public class NoiseChunkMixin {
	@Inject(method = "preliminarySurfaceLevel", at = @At("RETURN"), cancellable = true)
	private void ashbound$capital(int x, int z, CallbackInfoReturnable<Integer> cir) {
		int raw = cir.getReturnValueI(), v = Capital.surface(x, z, raw);
		if (v != raw) cir.setReturnValue(v);
	}
}
