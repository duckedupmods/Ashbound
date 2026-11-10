package com.snoringwalrus.ashbound;

import java.util.Comparator;
import java.util.LinkedHashSet;
import java.util.Set;
import java.util.function.Supplier;

import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ItemLike;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * Our own creative tabs: Gear (every dungeon's weapons, armour sets and drops, F to S, then the forge and anything
 * else of ours), Monsters (the spawn eggs) and Blocks (the dungeons' and the world's blocks and props).
 */
public final class Tabs {
	private Tabs() {}

	static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, Ashbound.ID);
	private static final String RANKS = "FEDCBAS";
	/** Each tab's own emblem (tools/itemicons_d.py), items only so the tab has something to show; in no tab themselves. */
	private static final DeferredItem<Item> GEAR = emblem("tab_gear"), MONSTERS = emblem("tab_monsters"), BLOCKS = emblem("tab_blocks");

	private static DeferredItem<Item> emblem(String id) {
		return Weapons.ITEMS.registerItem(id, Item::new, new Item.Properties().stacksTo(1));
	}

	static void register(IEventBus bus) {
		tab("gear", "Ashbound: Gear", () -> new ItemStack(GEAR.get()), out -> {
			for (Gear.Dungeon d : Gear.DUNGEONS.stream().sorted(Comparator.comparingInt(d -> RANKS.indexOf(d.rank()))).toList()) {
				for (Gear.Weapon w : d.weapons()) out.add(Gear.item(w.id()));
				for (Gear.Set s : d.sets()) for (Gear.Piece p : s.pieces()) out.add(Gear.item(p.id()));
				for (String m : d.mats()) out.add(Gear.item(m));
			}
			out.add(GateForge.ITEM.get());
			Stations.ITEMS.forEach(i -> out.add(i.get()));
			Gear.WEAPONS.forEach(i -> out.add(i.get()));
			Weapons.ALL.forEach(i -> out.add(i.get()));
			Armors.ALL.forEach(i -> out.add(i.get()));
			Curios.ITEMS.forEach(i -> out.add(i.get()));
			out.add(ColdForge.SHARD.get());
			out.add(ColdForge.EMBER.get());
			out.add(ColdForge.BRAND.get());
			for (int i = 0; i < Books.BOOKS.size(); i++) out.add(Books.book(i + 1, Skills.ALL.get(0).id()).getItem());
			Books.TOMES.forEach(i -> out.add(i.get()));
			Trades.ITEMS.values().forEach(i -> out.add(i.get()));
		});
		tab("monsters", "Ashbound: Monsters", () -> new ItemStack(MONSTERS.get()), out -> {
			GateMobs.EGGS.forEach(i -> out.add(i.get()));
			SilkMobs.EGGS.forEach(i -> out.add(i.get()));
			out.add(Monsters.CINDERHUSK_EGG.get());
			Beast.EGGS.forEach(i -> out.add(i.get()));
		});
		tab("blocks", "Ashbound: Blocks", () -> new ItemStack(BLOCKS.get()), out ->
				WorldBlocks.ITEMS.forEach(i -> out.add(i.get())));
		TABS.register(bus);
	}

	/** what a tab holds, each item once */
	private static final class Out {
		final Set<Item> items = new LinkedHashSet<>();

		void add(ItemLike i) {
			if (i != null) items.add(i.asItem());
		}
	}

	private static void tab(String id, String title, Supplier<ItemStack> icon, java.util.function.Consumer<Out> fill) {
		TABS.register(id, () -> CreativeModeTab.builder()
				.title(Component.literal(title))
				.icon(icon)
				.displayItems((params, output) -> {
					Out o = new Out();
					fill.accept(o);
					o.items.forEach(output::accept);
				})
				.build());
	}
}
