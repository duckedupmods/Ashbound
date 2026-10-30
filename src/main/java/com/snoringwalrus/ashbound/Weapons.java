package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.world.item.Item;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * Our item register. The weapons themselves are every dungeon's, listed in /ashbound/gear.json ({@link Gear}); each
 * swings with one of Epic Fight's movesets, picked by its data file (data/ashbound/capabilities/weapons).
 */
public final class Weapons {
	private Weapons() {}

	static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(Ashbound.ID);
	/** The forge's hand tools: never in anyone's pack, only in their hand at the work (client/ForgeScene). */
	public static final net.neoforged.neoforge.registries.DeferredItem<Item> SMITH_HAMMER = ITEMS.registerSimpleItem("smith_hammer", new Item.Properties().stacksTo(1)),
			TAILOR_NEEDLE = ITEMS.registerSimpleItem("tailor_needle", new Item.Properties().stacksTo(1));
	static final List<DeferredItem<? extends Item>> ALL = new ArrayList<>();
}
