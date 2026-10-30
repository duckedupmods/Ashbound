package com.snoringwalrus.ashbound;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import yesman.epicfight.api.event.EpicFightEventHooks;
import yesman.epicfight.gameasset.Armatures;

/** The people of Highmourn: one entity for all of them (Npc), what they say (Talk), sell (Shop), and your purse. */
public final class Townsfolk {
	private Townsfolk() {}

	static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(Registries.ENTITY_TYPE, Ashbound.ID);

	public static final DeferredHolder<EntityType<?>, EntityType<Npc>> NPC = ENTITIES.register("npc",
			() -> EntityType.Builder.of(Npc::new, MobCategory.MISC).sized(0.6f, 1.8f).clientTrackingRange(6).build(Ashbound.ID + ":npc"));

	static void register(IEventBus bus) {
		ENTITIES.register(bus);
		Coins.ATTACHMENTS.register(bus);
		Net.register(bus);
		Talk.init();
		Shop.init();
		bus.addListener((yesman.epicfight.api.animation.AnimationManager.AnimationRegistryEvent e) -> e.newBuilder(Ashbound.ID, NpcPatch::build));
		bus.addListener((EntityAttributeCreationEvent e) -> e.put(NPC.get(), Npc.attributes().build()));
		EpicFightEventHooks.Registry.ENTITY_PATCH.registerEvent(e -> e.registerEntityPatch(NPC.get(), NpcPatch::new));
		bus.addListener((FMLCommonSetupEvent e) -> e.enqueueWork(() -> Armatures.registerEntityTypeArmature(NPC.get(), Armatures.BIPED)));
	}
}
