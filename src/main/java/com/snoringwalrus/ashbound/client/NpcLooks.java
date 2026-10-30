package com.snoringwalrus.ashbound.client;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

import com.google.gson.JsonParser;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Npc;
import com.snoringwalrus.ashbound.NpcPatch;

import com.mojang.blaze3d.vertex.PoseStack;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.neoforged.neoforge.client.event.RegisterClientCommandsEvent;
import net.neoforged.neoforge.client.event.RenderFrameEvent;
import net.neoforged.neoforge.common.NeoForge;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.HumanoidMobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import yesman.epicfight.api.asset.AssetAccessor;
import yesman.epicfight.api.client.model.Meshes;
import yesman.epicfight.client.mesh.HumanoidMesh;
import yesman.epicfight.client.renderer.patched.entity.PHumanoidRenderer;

/**
 * How each townsperson looks: their own mesh (animmodels/entity/npc/KIND, tools/efmob.py --npc), texture and size,
 * looked up by the kind the server syncs; and their talk and shop screens opened as the server sends them.
 */
public final class NpcLooks {
	private NpcLooks() {}

	/** Someone not known yet (still "@townsfolk...", or a kind with no mesh) is drawn as this one meanwhile. */
	static final String STAND_IN = "townsfolk_3006";

	private static Map<String, Double> scales;
	private static final Map<String, AssetAccessor<HumanoidMesh>> MESHES = new HashMap<>();

	static Map<String, Double> scales() {
		if (scales == null) {
			scales = new HashMap<>();
			ResourceLocation at = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "npc_scales.json");
			Minecraft.getInstance().getResourceManager().getResource(at).ifPresent(r -> {
				try (var in = new InputStreamReader(r.open(), StandardCharsets.UTF_8)) {
					JsonParser.parseReader(in).getAsJsonObject().entrySet().forEach(e -> scales.put(e.getKey(), e.getValue().getAsDouble()));
				} catch (Exception ex) {
					Ashbound.LOG.error("Couldn't read the townsfolk's sizes", ex);
				}
			});
		}
		return scales;
	}

	static String known(String kind) {
		return scales().containsKey(kind) ? kind : STAND_IN;
	}

	public static double scale(String kind) {
		return scales().getOrDefault(known(kind), 1.0);
	}

	static AssetAccessor<HumanoidMesh> mesh(String kind) {
		return MESHES.computeIfAbsent(known(kind), k -> Meshes.getOrCreate(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "entity/npc/" + k),
				loader -> loader.loadSkinnedMesh(HumanoidMesh::new)));
	}

	static ResourceLocation texture(String kind) {
		return ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/npc/" + known(kind) + ".png");
	}

	/** Epic Fight's renderer for them, with each one's own mesh. */
	public static class Renderer extends PHumanoidRenderer<Npc, NpcPatch, HumanoidModel<Npc>, HumanoidMobRenderer<Npc, HumanoidModel<Npc>>, HumanoidMesh> {
		public Renderer(EntityRendererProvider.Context ctx, EntityType<?> type) {
			super(Meshes.BIPED, ctx, type);
		}

		@Override
		public AssetAccessor<HumanoidMesh> getMeshProvider(NpcPatch patch) {
			return mesh(patch.getOriginal().kindId());
		}

		@Override
		public void render(Npc entity, NpcPatch patch, HumanoidMobRenderer<Npc, HumanoidModel<Npc>> renderer, MultiBufferSource buffer, PoseStack pose, int light, float partialTicks) {
			long t0 = System.nanoTime();
			super.render(entity, patch, renderer, buffer, pose, light, partialTicks);
			drawNanos += System.nanoTime() - t0;
			drawn++;
		}
	}

	// ---------------------------------------------------------------- what they cost (/ashlag)

	static long drawNanos, drawn, frames, since = System.nanoTime(), serverTicks0, serverNanos0, clientNanos0;

	/** What the townsfolk have cost since last asked: drawing them, their client ticks, and on your own world the server's. */
	static int lag(CommandSourceStack src) {
		Minecraft mc = Minecraft.getInstance();
		double secs = Math.max(1e-3, (System.nanoTime() - since) / 1e9), f = Math.max(1, frames);
		int near = mc.level == null ? 0 : (int) java.util.stream.StreamSupport.stream(mc.level.entitiesForRendering().spliterator(), false).filter(e -> e instanceof Npc).count();
		String out = String.format("Townsfolk over %.0f s: %d fps; %d known here, %.1f drawn a frame at %.2f ms a frame; their client ticks %.2f ms a second",
				secs, mc.getFps(), near, drawn / f, drawNanos / f / 1e6, (Npc.clientNanos - clientNanos0) / secs / 1e6);
		var server = mc.getSingleplayerServer();
		if (server != null) {
			int ticks = Math.max(1, server.getTickCount() - (int) serverTicks0);
			out += String.format("; server %.1f ms a tick, %.2f of it theirs", server.getAverageTickTimeNanos() / 1e6, (Npc.serverNanos - serverNanos0) / (double) ticks / 1e6);
			serverTicks0 = server.getTickCount();
		}
		src.sendSystemMessage(Component.literal(out));
		drawNanos = drawn = frames = 0;
		since = System.nanoTime();
		serverNanos0 = Npc.serverNanos;
		clientNanos0 = Npc.clientNanos;
		return 1;
	}

	/** Without Epic Fight's it would fall back to vanilla's humanoid, wearing their texture. */
	public static HumanoidMobRenderer<Npc, HumanoidModel<Npc>> vanilla(EntityRendererProvider.Context ctx) {
		return new HumanoidMobRenderer<>(ctx, new HumanoidModel<>(ctx.bakeLayer(net.minecraft.client.model.geom.ModelLayers.ZOMBIE)), 0.5f) {
			@Override
			public ResourceLocation getTextureLocation(Npc e) {
				return texture(e.kindId());
			}
		};
	}

	/** The server's talk and shop, onto the screen. */
	public static void hooks() {
		Npc.SCALE = NpcLooks::scale;
		NeoForge.EVENT_BUS.addListener((RenderFrameEvent.Post e) -> frames++);
		NeoForge.EVENT_BUS.addListener((RegisterClientCommandsEvent e) -> e.getDispatcher().register(Commands.literal("ashlag").executes(c -> lag(c.getSource()))));
		Net.onTalk = m -> {
			Minecraft mc = Minecraft.getInstance();
			if (m.entity() < 0) {
				if (mc.screen instanceof TalkScreen t) t.closeQuietly();
			} else if (mc.screen instanceof TalkScreen t && t.entity() == m.entity()) {
				t.set(m);
			} else {
				mc.setScreen(new TalkScreen(m));
			}
		};
		Net.onShop = m -> Minecraft.getInstance().setScreen(new ShopScreen(m));
		Net.onCard = () -> Minecraft.getInstance().setScreen(new GuildCardScreen());
		Net.onBoard = m -> {
			Minecraft mc = Minecraft.getInstance();
			if (mc.screen instanceof QuestBoardScreen b && b.entity() == m.entity()) b.set(m);
			else mc.setScreen(new QuestBoardScreen(m));
		};
	}
}
