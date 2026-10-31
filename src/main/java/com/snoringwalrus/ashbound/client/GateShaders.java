package com.snoringwalrus.ashbound.client;

import java.io.IOException;

import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.snoringwalrus.ashbound.Ashbound;

import net.minecraft.client.renderer.ShaderInstance;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.RegisterShadersEvent;

/**
 * The gate's own shaders (assets/ashbound/shaders/core): the tear (its dark inside and burning lips),
 * shaped glows, the shards of the world round it, the soft sparks and smoke. All take POSITION_COLOR_TEX_LIGHTMAP;
 * what UV0/UV2 mean is written at the top of each .fsh.
 */
@EventBusSubscriber(modid = Ashbound.ID, value = Dist.CLIENT)
public final class GateShaders {
	private GateShaders() {}

	static ShaderInstance rift, glow, shard, particle, spell, post;

	@SubscribeEvent
	static void register(RegisterShadersEvent e) throws IOException {
		e.registerShader(load(e, "gate_rift"), s -> rift = s);
		e.registerShader(load(e, "gate_glow"), s -> glow = s);
		e.registerShader(load(e, "gate_shard"), s -> shard = s);
		e.registerShader(load(e, "gate_particle"), s -> particle = s);
		e.registerShader(load(e, "spell_fx"), s -> spell = s);
		e.registerShader(new ShaderInstance(e.getResourceProvider(), ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "spell_post"), DefaultVertexFormat.POSITION_TEX), s -> post = s);
	}

	private static ShaderInstance load(RegisterShadersEvent e, String name) throws IOException {
		return new ShaderInstance(e.getResourceProvider(), ResourceLocation.fromNamespaceAndPath(Ashbound.ID, name),
				DefaultVertexFormat.POSITION_COLOR_TEX_LIGHTMAP);
	}
}
