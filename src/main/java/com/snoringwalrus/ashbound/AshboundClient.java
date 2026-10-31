package com.snoringwalrus.ashbound;

import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.entity.HumanoidMobRenderer;
import net.minecraft.client.renderer.entity.SpiderRenderer;
import net.minecraft.client.renderer.item.ItemProperties;
import net.minecraft.client.renderer.item.ItemPropertyFunction;
import net.minecraft.resources.ResourceLocation;
import com.snoringwalrus.ashbound.client.NpcLooks;

import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;
import net.neoforged.neoforge.client.event.ModelEvent;
import yesman.epicfight.api.client.event.EpicFightClientEventHooks;
import yesman.epicfight.api.client.model.Meshes;
import yesman.epicfight.api.asset.AssetAccessor;
import yesman.epicfight.client.mesh.HumanoidMesh;
import yesman.epicfight.client.mesh.SpiderMesh;
import yesman.epicfight.client.renderer.patched.entity.PHumanoidRenderer;
import yesman.epicfight.client.renderer.patched.entity.PSpiderRenderer;

/**
 * The client side: our shield and bow change model as they're raised and drawn, like vanilla's own, and our
 * monsters are drawn by Epic Fight with their own meshes (tools/efmob.py) on its biped skeleton.
 */
@EventBusSubscriber(modid = Ashbound.ID, value = Dist.CLIENT)
public final class AshboundClient {
	private AshboundClient() {}

	static final Meshes.MeshAccessor<HumanoidMesh> CINDERHUSK = Meshes.MeshAccessor.create(Ashbound.ID, "entity/cinderhusk",
			loader -> loader.loadSkinnedMesh(HumanoidMesh::new));

	/** Epic Fight's own hooks, set up as the mod loads: its renderer for each of our monsters. */
	@SuppressWarnings({"rawtypes", "unchecked"})
	static void hooks(net.neoforged.bus.api.IEventBus bus) {
		com.snoringwalrus.ashbound.client.VitalsHud.hooks(bus);
		com.snoringwalrus.ashbound.client.LevelHud.hooks(bus);
		com.snoringwalrus.ashbound.client.CurioKeys.hooks();
		com.snoringwalrus.ashbound.client.RelicHud.hooks(bus);
		com.snoringwalrus.ashbound.client.CurioKeys.skillHud(bus);
		com.snoringwalrus.ashbound.client.WornCurios.hooks(bus);
		// the Ash Tree is the only skill screen: K opens it in place of Epic Fight's, and skill books don't open
		net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener((net.neoforged.neoforge.client.event.ScreenEvent.Opening e) -> {
			if (e.getNewScreen() instanceof yesman.epicfight.client.gui.screen.SkillEditScreen)
				e.setNewScreen(new com.snoringwalrus.ashbound.client.TreeScreen());
			else if (e.getNewScreen() instanceof yesman.epicfight.client.gui.screen.SkillBookScreen) e.setCanceled(true);
		});
		EpicFightClientEventHooks.Registry.ADD_PATCHED_ENTITY.registerEvent(e -> e.addPatchedEntityRenderer(Monsters.CINDERHUSK.get(),
				type -> new PHumanoidRenderer(CINDERHUSK, e.getContext(), type).initLayerLast(e.getContext(), type)));
		EpicFightClientEventHooks.Registry.ADD_PATCHED_ENTITY.registerEvent(e -> e.addPatchedEntityRenderer(Townsfolk.NPC.get(),
				type -> new NpcLooks.Renderer(e.getContext(), type).initLayerLast(e.getContext(), type)));
		NpcLooks.hooks();
		// players keep Epic Fight's body in mining mode too: the vanilla model would wear our armour sheets as flat boxes
		EpicFightClientEventHooks.Render.VALIDATE_PLAYER_MODEL_TO_RENDER.registerEvent(e -> e.setShouldRender(true));
		SilkMobs.WALKER.forEach((k, t) -> {
			Meshes.MeshAccessor<HumanoidMesh> mesh = Meshes.MeshAccessor.create(Ashbound.ID, "entity/" + k.mesh(), loader -> loader.loadSkinnedMesh(HumanoidMesh::new));
			EpicFightClientEventHooks.Registry.ADD_PATCHED_ENTITY.registerEvent(e -> e.addPatchedEntityRenderer(t.get(),
					type -> new PHumanoidRenderer(mesh, e.getContext(), type).initLayerLast(e.getContext(), type)));
		});
		SilkMobs.CRAWLER.forEach((k, t) -> {
			Meshes.MeshAccessor<SpiderMesh> mesh = Meshes.MeshAccessor.create(Ashbound.ID, "entity/" + k.mesh(), loader -> loader.loadSkinnedMesh(SpiderMesh::new));
			EpicFightClientEventHooks.Registry.ADD_PATCHED_ENTITY.registerEvent(e -> e.addPatchedEntityRenderer(t.get(), type -> new PSpiderRenderer(e.getContext(), type) {
				@Override
				public AssetAccessor<SpiderMesh> getDefaultMesh() {
					return mesh;
				}
			}));
		});
		GateMobs.WALKER.forEach((k, t) -> {
			Meshes.MeshAccessor<HumanoidMesh> mesh = Meshes.MeshAccessor.create(Ashbound.ID, "entity/" + k.mesh(), loader -> loader.loadSkinnedMesh(HumanoidMesh::new));
			EpicFightClientEventHooks.Registry.ADD_PATCHED_ENTITY.registerEvent(e -> e.addPatchedEntityRenderer(t.get(),
					type -> new PHumanoidRenderer(mesh, e.getContext(), type).initLayerLast(e.getContext(), type)));
		});
		GateMobs.CRAWLER.forEach((k, t) -> {
			Meshes.MeshAccessor<SpiderMesh> mesh = Meshes.MeshAccessor.create(Ashbound.ID, "entity/" + k.mesh(), loader -> loader.loadSkinnedMesh(SpiderMesh::new));
			EpicFightClientEventHooks.Registry.ADD_PATCHED_ENTITY.registerEvent(e -> e.addPatchedEntityRenderer(t.get(), type -> new PSpiderRenderer(e.getContext(), type) {
				@Override
				public AssetAccessor<SpiderMesh> getDefaultMesh() {
					return mesh;
				}
			}));
		});
	}

	/** Without Epic Fight's renderer it would fall back to this; the texture is the one its mesh is mapped to. */
	@SubscribeEvent
	static void renderers(EntityRenderersEvent.RegisterRenderers event) {
		event.registerEntityRenderer(Monsters.CINDERHUSK.get(), ctx -> new HumanoidMobRenderer<Cinderhusk, HumanoidModel<Cinderhusk>>(ctx,
				new HumanoidModel<>(ctx.bakeLayer(ModelLayers.ZOMBIE)), 0.7f) {
			@Override
			public ResourceLocation getTextureLocation(Cinderhusk entity) {
				return TEXTURE;
			}
		});
		event.registerEntityRenderer(Townsfolk.NPC.get(), NpcLooks::vanilla);
		SilkMobs.WALKER.forEach((k, t) -> event.registerEntityRenderer(t.get(), ctx -> new HumanoidMobRenderer<SilkMobs.Walker, HumanoidModel<SilkMobs.Walker>>(ctx,
				new HumanoidModel<>(ctx.bakeLayer(ModelLayers.ZOMBIE)), 0.7f) {
			@Override
			public ResourceLocation getTextureLocation(SilkMobs.Walker entity) {
				return ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/" + k.mesh() + ".png");
			}
		}));
		SilkMobs.CRAWLER.forEach((k, t) -> event.registerEntityRenderer(t.get(), ctx -> new SpiderRenderer<SilkMobs.Crawler>(ctx) {
			@Override
			public ResourceLocation getTextureLocation(SilkMobs.Crawler entity) {
				return ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/" + k.mesh() + ".png");
			}
		}));
		GateMobs.WALKER.forEach((k, t) -> event.registerEntityRenderer(t.get(), ctx -> new HumanoidMobRenderer<GateMobs.Walker, HumanoidModel<GateMobs.Walker>>(ctx,
				new HumanoidModel<>(ctx.bakeLayer(ModelLayers.ZOMBIE)), 0.7f) {
			@Override
			public ResourceLocation getTextureLocation(GateMobs.Walker entity) {
				return ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/" + k.mesh() + ".png");
			}
		}));
		GateMobs.CRAWLER.forEach((k, t) -> event.registerEntityRenderer(t.get(), ctx -> new SpiderRenderer<GateMobs.Crawler>(ctx) {
			@Override
			public ResourceLocation getTextureLocation(GateMobs.Crawler entity) {
				return ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/" + k.mesh() + ".png");
			}
		}));
		event.registerBlockEntityRenderer(ClockHands.ENTITY.get(), ctx -> new ClockHands.Renderer());
		event.registerBlockEntityRenderer(VillageSpin.ENTITY.get(), ctx -> new VillageSpin.Renderer());
		event.registerEntityRenderer(Spells.BOLT.get(), net.minecraft.client.renderer.entity.NoopRenderer::new);
		event.registerEntityRenderer(MobBolt.TYPE.get(), net.minecraft.client.renderer.entity.NoopRenderer::new);
		for (Mounts.Kind k : Mounts.ALL) event.registerEntityRenderer(Mounts.type(k), com.snoringwalrus.ashbound.client.MountRender::new);
		event.registerEntityRenderer(Mounts.REVENANT.get(), com.snoringwalrus.ashbound.client.ThrallRender::new);
		event.registerEntityRenderer(Mounts.CHAMPION.get(), com.snoringwalrus.ashbound.client.ThrallRender::new);
	}

	/** the curio key (V) */
	@SubscribeEvent
	static void keys(net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent event) {
		com.snoringwalrus.ashbound.client.CurioKeys.register(event);
	}

	/** The clock's hands are models with no block of their own, so they're loaded by name. */
	@SubscribeEvent
	static void models(ModelEvent.RegisterAdditional event) {
		event.register(ClockHands.Models.MINUTE);
		event.register(ClockHands.Models.HOUR);
		event.register(VillageSpin.Models.SAILS);
		event.register(VillageSpin.Models.WHEEL);
		event.register(VillageSpin.Models.BELL);
	}

	static final ResourceLocation TEXTURE = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/cinderhusk.png");

	@SubscribeEvent
	static void setup(FMLClientSetupEvent event) {
		event.enqueueWork(() -> {
			ItemPropertyFunction using = (stack, level, e, seed) -> e != null && e.isUsingItem() && e.getUseItem() == stack ? 1 : 0;
			for (net.minecraft.world.item.Item shield : Gear.ofKind("shield"))
				ItemProperties.register(shield, ResourceLocation.withDefaultNamespace("blocking"), using);
			for (net.minecraft.world.item.Item bow : Gear.ofKind("bow")) {
				ItemProperties.register(bow, ResourceLocation.withDefaultNamespace("pulling"), using);
				ItemProperties.register(bow, ResourceLocation.withDefaultNamespace("pull"), (stack, level, e, seed) ->
						e == null || e.getUseItem() != stack ? 0 : (stack.getUseDuration(e) - e.getUseItemRemainingTicks()) / 20f);
			}
		});
	}
}
