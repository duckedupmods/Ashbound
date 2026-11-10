package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.ItemTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import top.theillusivec4.curios.api.CuriosApi;
import top.theillusivec4.curios.api.type.inventory.ICurioStacksHandler;
import top.theillusivec4.curios.api.type.inventory.IDynamicStackHandler;

/**
 * The pouch on your belt: four slots of their own beside the inventory for what you carry but never fight with (the Guild Card, the
 * Warp Stone, the Bottomless Bag, the Ration Pouch), so they stop taking up the pack. They stay with you when you die. It's a Curios
 * slot (data/ashbound/curios/slots/pouch.json, the tag curios:pouch says what fits), so the menu and the saving are Curios' own;
 * client/CharacterScreen draws it and a right-click on something in it uses it.
 */
public final class BeltPouch {
	private BeltPouch() {}

	public static final String SLOT = "pouch";
	private static final TagKey<Item> FITS = ItemTags.create(ResourceLocation.fromNamespaceAndPath("curios", SLOT));
	/** Once, for everyone: what they were handed goes in by itself. */
	private static final String SETTLED = "pouch_settled";

	private static IDynamicStackHandler slots(Player p) {
		return CuriosApi.getCuriosInventory(p).flatMap(inv -> inv.getStacksHandler(SLOT)).map(ICurioStacksHandler::getStacks).orElse(null);
	}

	/** What's in it, the stacks themselves. */
	static List<ItemStack> held(Player p) {
		List<ItemStack> out = new ArrayList<>();
		IDynamicStackHandler in = slots(p);
		for (int i = 0; in != null && i < in.getSlots(); i++) if (!in.getStackInSlot(i).isEmpty()) out.add(in.getStackInSlot(i));
		return out;
	}

	/** Whatever belongs in it comes out of the pack, while there's room. */
	static void tuck(ServerPlayer p) {
		IDynamicStackHandler in = slots(p);
		if (in == null) return;
		Inventory pack = p.getInventory();
		int free = 0;
		for (int i = 0; i < pack.items.size(); i++) {
			ItemStack s = pack.items.get(i);
			if (!s.is(FITS)) continue;
			while (free < in.getSlots() && !in.getStackInSlot(free).isEmpty()) free++;
			if (free == in.getSlots()) return;
			in.setStackInSlot(free, s.copy());
			pack.items.set(i, ItemStack.EMPTY);
		}
	}

	/** The first tuck, once they've got their kit. Later on they're free to take things out again. Not in creative, whose
	 * inventory doesn't show the pouch: it waits until they're back in survival. */
	static void settle(ServerPlayer p) {
		if (Classes.of(p) == null || Coins.flag(p, SETTLED) || p.isCreative()) return;
		Coins.setFlag(p, SETTLED);
		tuck(p);
	}

	/** The right-click in the inventory that needs the server: the Bag or the Warp Stone. The Guild Card is the client's own. */
	public static boolean opens(ItemStack s) {
		return s.is(Bag.POUCH.get()) || Waypoints.stone(s);
	}

	static void use(ServerPlayer p, int slot) {
		IDynamicStackHandler in = slots(p);
		if (in == null || slot < 0 || slot >= in.getSlots()) return;
		ItemStack s = in.getStackInSlot(slot);
		if (s.is(Bag.POUCH.get())) Bag.open(p);
		else if (Waypoints.stone(s)) Waypoints.warp(p, s);
	}
}
