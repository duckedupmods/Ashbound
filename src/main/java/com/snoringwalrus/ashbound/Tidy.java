package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.inventory.ClickType;
import net.minecraft.world.inventory.ShulkerBoxMenu;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;

/** The Sort, Take all and Stash buttons, done here so they work the same on a server: see client/InvButtons. */
public final class Tidy {
	private Tidy() {}

	public static final int SORT = 0, TAKE = 1, STASH = 2;
	/** the backpack part of the inventory; the hotbar is left where you put it */
	private static final int PACK_FROM = 9, PACK_TO = 35;

	public static void act(ServerPlayer p, int what) {
		AbstractContainerMenu m = p.containerMenu;
		boolean box = m instanceof ChestMenu || m instanceof ShulkerBoxMenu;
		if (!m.stillValid(p) || !box && m != p.inventoryMenu && !(m instanceof top.theillusivec4.curios.common.inventory.container.CuriosContainer) || !box && what != SORT) return;
		switch (what) {
			case SORT -> sort(box ? theirs(p, m) : pack(p, m));
			case TAKE -> theirs(p, m).forEach(s -> m.clicked(s.index, 0, ClickType.QUICK_MOVE, p));
			case STASH -> stash(p, m);
			default -> {}
		}
		m.broadcastChanges();
	}

	private static List<Slot> theirs(ServerPlayer p, AbstractContainerMenu m) {
		return m.slots.stream().filter(s -> s.container != p.getInventory()).toList();
	}

	private static List<Slot> pack(ServerPlayer p, AbstractContainerMenu m) {
		return m.slots.stream().filter(s -> s.container == p.getInventory() && s.getContainerSlot() >= PACK_FROM && s.getContainerSlot() <= PACK_TO).toList();
	}

	/** Puts away what the box already holds some of. */
	private static void stash(ServerPlayer p, AbstractContainerMenu m) {
		List<Slot> box = theirs(p, m);
		for (Slot s : pack(p, m))
			if (s.hasItem() && box.stream().anyMatch(b -> ItemStack.isSameItem(b.getItem(), s.getItem()))) m.clicked(s.index, 0, ClickType.QUICK_MOVE, p);
	}

	/** Gear first, then food, blocks and the rest, same things together and part stacks merged. */
	private static void sort(List<Slot> slots) {
		List<ItemStack> all = new ArrayList<>();
		for (Slot s : slots) {
			if (!s.hasItem()) continue;
			ItemStack next = s.getItem().copy();
			for (ItemStack have : all) {
				if (next.isEmpty()) break;
				if (!ItemStack.isSameItemSameComponents(have, next)) continue;
				int room = Math.min(next.getCount(), have.getMaxStackSize() - have.getCount());
				have.grow(room);
				next.shrink(room);
			}
			if (!next.isEmpty()) all.add(next);
		}
		all.sort(Comparator.comparingInt(Tidy::shelf).thenComparing((ItemStack s) -> BuiltInRegistries.ITEM.getKey(s.getItem()).toString())
				.thenComparing(Comparator.comparingInt(ItemStack::getCount).reversed()));
		for (int i = 0; i < slots.size(); i++) slots.get(i).set(i < all.size() ? all.get(i) : ItemStack.EMPTY);
	}

	/** 0 weapons and tools, 1 armour, 2 food, 3 goods, 4 blocks. Nothing wears out, but what would have still has a limit. */
	public static int shelf(ItemStack s) {
		if (s.getItem() instanceof ArmorItem) return 1;
		if (s.has(DataComponents.MAX_DAMAGE)) return 0;
		if (s.has(DataComponents.FOOD)) return 2;
		return s.getItem() instanceof BlockItem ? 4 : 3;
	}
}
