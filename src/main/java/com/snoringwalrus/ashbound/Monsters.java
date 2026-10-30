package com.snoringwalrus.ashbound;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.item.Item;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.common.DeferredSpawnEggItem;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;
import yesman.epicfight.api.event.EpicFightEventHooks;
import yesman.epicfight.gameasset.Armatures;

/** Our monsters, each fought by Epic Fight through its patch. */
public final class Monsters {
	private Monsters() {}

	static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(Registries.ENTITY_TYPE, Ashbound.ID);

	public static final DeferredHolder<EntityType<?>, EntityType<Cinderhusk>> CINDERHUSK = ENTITIES.register("cinderhusk",
			() -> EntityType.Builder.of(Cinderhusk::new, MobCategory.MONSTER).sized(0.9f, 2.9f).fireImmune().clientTrackingRange(10)
					.build(Ashbound.ID + ":cinderhusk"));

	static final DeferredItem<Item> CINDERHUSK_EGG = Weapons.ITEMS.registerItem("cinderhusk_spawn_egg",
			p -> new DeferredSpawnEggItem(CINDERHUSK, 0x1b1917, 0xe04a0a, p));

	static void register(IEventBus bus) {
		ENTITIES.register(bus);
		MobBolt.TYPE.getId();   // its type onto the list before the list is read
		bus.addListener((EntityAttributeCreationEvent e) -> e.put(CINDERHUSK.get(), Cinderhusk.attributes().build()));
		EpicFightEventHooks.Registry.ENTITY_PATCH.registerEvent(e -> e.registerEntityPatch(CINDERHUSK.get(), CinderhuskPatch::new));
		// the skeleton Epic Fight animates it on: its biped, which tools/efmob.py fits the mesh to
		bus.addListener((FMLCommonSetupEvent e) -> e.enqueueWork(() -> Armatures.registerEntityTypeArmature(CINDERHUSK.get(), Armatures.BIPED)));
	}
}
