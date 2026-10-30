package com.snoringwalrus.ashbound.mixin;

import com.snoringwalrus.ashbound.Capital;
import net.minecraft.core.RegistryAccess;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.chunk.ChunkGeneratorStructureState;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplateManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** The capital's chunks: no other structures start round it, and its own blocks go in instead of trees and flowers. */
@Mixin(ChunkGenerator.class)
public class ChunkGeneratorMixin {
	@Inject(method = "createStructures", at = @At("HEAD"), cancellable = true)
	private void ashbound$noStructures(RegistryAccess registries, ChunkGeneratorStructureState state, StructureManager structures,
			ChunkAccess chunk, StructureTemplateManager templates, CallbackInfo ci) {
		if (Capital.blocksStructures(chunk.getPos())) ci.cancel();
	}

	@Inject(method = "applyBiomeDecoration", at = @At("HEAD"), cancellable = true)
	private void ashbound$cityChunk(WorldGenLevel level, ChunkAccess chunk, StructureManager structures, CallbackInfo ci) {
		if (Capital.owns(chunk.getPos())) {
			Capital.place(level, chunk);
			ci.cancel();
		}
	}

	@Inject(method = "applyBiomeDecoration", at = @At("RETURN"))
	private void ashbound$cityBlocks(WorldGenLevel level, ChunkAccess chunk, StructureManager structures, CallbackInfo ci) {
		if (!Capital.owns(chunk.getPos()) && Capital.hasBlocks(chunk.getPos())) Capital.place(level, chunk);
	}
}
