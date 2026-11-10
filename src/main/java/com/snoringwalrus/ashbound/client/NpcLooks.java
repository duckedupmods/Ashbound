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
	/** When the server first asked for a class (0: not asking); the screen opens the first tick nothing's in its way. */
	private static long classAsked;
	private static String classBlocker = "";
	private static long joined;

	private static void openClass() {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null) return;
		if (mc.screen instanceof ClassScreen || mc.screen instanceof MountScreen) {
			classAsked = 0;
			return;
		}
		if (mc.screen == null) {
			Ashbound.LOG.info("[Ashbound] class screen opened {} ms after the first ask", System.currentTimeMillis() - classAsked);
			classAsked = 0;
			classBlocker = "";
			mc.setScreen(new ClassScreen());
			return;
		}
		String b = mc.screen.getClass().getName();
		if (!b.equals(classBlocker)) {
			classBlocker = b;
			Ashbound.LOG.info("[Ashbound] class screen waiting: {} is open ({} ms after the ask)", b, System.currentTimeMillis() - classAsked);
		}
	}

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

	/** An adventurer (Adventurers): the same cube meshes and sizes as the townsfolk, in the real armour and weapons they wear. */
	public static class AdventurerRenderer extends PHumanoidRenderer<com.snoringwalrus.ashbound.Adventurer, com.snoringwalrus.ashbound.AdventurerPatch,
			HumanoidModel<com.snoringwalrus.ashbound.Adventurer>, HumanoidMobRenderer<com.snoringwalrus.ashbound.Adventurer, HumanoidModel<com.snoringwalrus.ashbound.Adventurer>>, HumanoidMesh> {
		public AdventurerRenderer(EntityRendererProvider.Context ctx, EntityType<?> type) {
			super(Meshes.BIPED, ctx, type);
		}

		@Override
		public AssetAccessor<HumanoidMesh> getMeshProvider(com.snoringwalrus.ashbound.AdventurerPatch patch) {
			return mesh(patch.getOriginal().kindId());
		}
	}

	/** Their vanilla renderer, with an armour layer: Epic Fight builds its own layers from this one's, and without it their armour
	 * wouldn't be drawn at all (while the body under it is left out, as for players). */
	public static HumanoidMobRenderer<com.snoringwalrus.ashbound.Adventurer, HumanoidModel<com.snoringwalrus.ashbound.Adventurer>> vanillaAdventurer(EntityRendererProvider.Context ctx) {
		var r = new HumanoidMobRenderer<com.snoringwalrus.ashbound.Adventurer, HumanoidModel<com.snoringwalrus.ashbound.Adventurer>>(ctx,
				new HumanoidModel<>(ctx.bakeLayer(net.minecraft.client.model.geom.ModelLayers.ZOMBIE)), 0.5f) {
			@Override
			public ResourceLocation getTextureLocation(com.snoringwalrus.ashbound.Adventurer e) {
				return texture(e.kindId());
			}
		};
		r.addLayer(new net.minecraft.client.renderer.entity.layers.HumanoidArmorLayer<>(r,
				new net.minecraft.client.model.HumanoidArmorModel<>(ctx.bakeLayer(net.minecraft.client.model.geom.ModelLayers.PLAYER_INNER_ARMOR)),
				new net.minecraft.client.model.HumanoidArmorModel<>(ctx.bakeLayer(net.minecraft.client.model.geom.ModelLayers.PLAYER_OUTER_ARMOR)), ctx.getModelManager()));
		return r;
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
		Net.onPhotos = () -> Minecraft.getInstance().setScreen(new Photos.Table());
		Net.onClassAsk = () -> {
			if (classAsked == 0) {
				classAsked = System.currentTimeMillis();
				Ashbound.LOG.info("[Ashbound] class asked {} ms after joining", classAsked - joined);
			}
			openClass();
		};
		NeoForge.EVENT_BUS.addListener((net.neoforged.neoforge.client.event.ClientPlayerNetworkEvent.LoggingIn e) -> joined = System.currentTimeMillis());
		NeoForge.EVENT_BUS.addListener((net.neoforged.neoforge.client.event.ClientTickEvent.Post e) -> {
			if (classAsked != 0) openClass();
		});
		com.snoringwalrus.ashbound.Books.onTome = f -> Minecraft.getInstance().setScreen(new TomeScreen(f));
		Net.onPoster = m -> Minecraft.getInstance().setScreen(new WantedScreen(m));
		com.snoringwalrus.ashbound.Books.onOffer = m -> Minecraft.getInstance().setScreen(new ReplaceScreen(m.skill(), m.rank()));
		Net.onMountAsk = () -> {
			if (Minecraft.getInstance().screen == null) Minecraft.getInstance().setScreen(new MountScreen());
		};
		Net.onBoard = m -> {
			Minecraft mc = Minecraft.getInstance();
			if (mc.screen instanceof QuestBoardScreen b && b.entity() == m.entity()) b.set(m);
			else mc.setScreen(new QuestBoardScreen(m));
		};
	}
}
