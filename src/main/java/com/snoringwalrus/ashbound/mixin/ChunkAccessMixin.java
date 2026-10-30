package com.snoringwalrus.ashbound.mixin;

import com.snoringwalrus.ashbound.Capital;
import net.minecraft.world.level.biome.BiomeResolver;
import net.minecraft.world.level.chunk.ChunkAccess;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** The capital's own ground gets its own biome (not the snowy peaks the land was before it was cut down). */
@Mixin(ChunkAccess.class)
public class ChunkAccessMixin {
	@ModifyVariable(method = "fillBiomesFromNoise", at = @At("HEAD"), argsOnly = true)
	private BiomeResolver ashbound$capital(BiomeResolver resolver) {
		return Capital.biomes(resolver);
	}
}
