package com.snoringwalrus.ashbound.mixin;

import com.snoringwalrus.ashbound.Capital;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.biome.BiomeManager;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.levelgen.GenerationStep;
import net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator;
import net.minecraft.world.level.levelgen.RandomState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** No caves or ravines cut through the capital's ground. */
@Mixin(NoiseBasedChunkGenerator.class)
public class NoiseBasedChunkGeneratorMixin {
	@Inject(method = "applyCarvers", at = @At("HEAD"), cancellable = true)
	private void ashbound$noCaves(WorldGenRegion level, long seed, RandomState random, BiomeManager biomes, StructureManager structures,
			ChunkAccess chunk, GenerationStep.Carving step, CallbackInfo ci) {
		if (Capital.owns(chunk.getPos())) ci.cancel();
	}
}
