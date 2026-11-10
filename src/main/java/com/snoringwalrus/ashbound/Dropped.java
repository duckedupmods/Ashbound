package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

import net.minecraft.ChatFormatting;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.TickTask;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.level.saveddata.SavedData;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.item.ItemTossEvent;

/**
 * Gear thrown on the ground shows up from a way off, with whose it is, and lasts half an hour instead of five minutes, because it's
 * nearly always a slip of the key. Everyone in a world has a colour of their own, the first free one when they first throw something
 * down: the name over the item comes up in it, and since a custom name reaches every client by itself, client/TossedFx and
 * mixin/TossedGlowMixin read the colour off that for the light and the outline. A stack of ordinary stuff is left alone.
 */
public final class Dropped {
	private Dropped() {}

	/** How long it stays on the ground, in ticks. */
	private static final int LASTS = 36000;
	/** Far enough apart to tell at a glance, with no white among them. */
	private static final int[] COLOURS = {0xFF5A4A, 0x5AA8FF, 0x6AE06A, 0xFFD040, 0xD070FF, 0x40E0D0, 0xFF9030, 0xFF70B0, 0xB0E040, 0x8090FF, 0xC89060, 0x30C080};
	private static final String[] COLOUR_NAMES = {"red", "blue", "green", "yellow", "violet", "turquoise", "orange", "pink", "lime", "periwinkle", "tan", "jade"};

	/** Who's got which: their place in this list. */
	private static final class State extends SavedData {
		final List<UUID> seen = new ArrayList<>();

		@Override
		public CompoundTag save(CompoundTag tag, HolderLookup.Provider reg) {
			ListTag list = new ListTag();
			for (UUID u : seen) list.add(NbtUtils.createUUID(u));
			tag.put("seen", list);
			return tag;
		}

		static State load(CompoundTag tag, HolderLookup.Provider reg) {
			State s = new State();
			for (Tag t : tag.getList("seen", Tag.TAG_INT_ARRAY)) s.seen.add(NbtUtils.loadUUID(t));
			return s;
		}
	}

	private static State state(MinecraftServer server) {
		return server.overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(State::new, State::load, null), "ashbound_drop_colours");
	}

	private static final int FRESH = 100;

	static boolean matters(ItemStack s) {
		return s.getMaxStackSize() == 1 || s.getRarity() != Rarity.COMMON;
	}

	/** p's place among the colours, telling them the first time. */
	static int colour(ServerPlayer p) {
		State st = state(p.server);
		if (!st.seen.contains(p.getUUID())) {
			st.seen.add(p.getUUID());
			st.setDirty();
			int i = (st.seen.size() - 1) % COLOURS.length;
			p.sendSystemMessage(Component.literal("What you throw down shows up in " + COLOUR_NAMES[i] + ".").withColor(COLOURS[i]));
		}
		return COLOURS[st.seen.indexOf(p.getUUID()) % COLOURS.length];
	}

	static void mark(ItemEntity thrown, Player by) {
		if (!matters(thrown.getItem())) return;
		thrown.setGlowingTag(true);
		thrown.lifespan = LASTS;
		if (!(by instanceof ServerPlayer p)) return;
		thrown.setCustomName(Component.literal(p.getGameProfile().getName() + ": ").append(thrown.getItem().getHoverName()).withColor(colour(p)));
		thrown.setCustomNameVisible(true);
	}

	/** Loot that's theirs (a gate storm's share): marked the way thrown gear is, their name and colour over it, whatever it is. */
	static void markFor(ItemEntity it, ServerPlayer p) {
		it.setGlowingTag(true);
		it.lifespan = LASTS;
		it.setCustomName(Component.literal(p.getGameProfile().getName() + ": ").append(it.getItem().getHoverName()).withColor(colour(p)));
		it.setCustomNameVisible(true);
	}

	/** Someone's share of loot (a gate storm's, a dug-up stash's), showering down from well over their head, spread about them: it
	 *  lands wherever it lands (a tree, a ledge: it's marked, they'll see it and climb for it), and can't be picked up till it's
	 *  down, so it's seen falling. Theirs alone to pick up. What it was, for the chat. */
	static String rain(net.minecraft.server.level.ServerLevel l, ServerPlayer p, List<ItemStack> items, net.minecraft.util.RandomSource r) {
		return rain(l, p, items, r, null);
	}

	/** The same, keeping the item entities in out (to find what's still lying about later). */
	static String rain(net.minecraft.server.level.ServerLevel l, ServerPlayer p, List<ItemStack> items, net.minecraft.util.RandomSource r,
			@javax.annotation.Nullable List<ItemEntity> out) {
		StringBuilder b = new StringBuilder();
		double y = p.getY() + 8;
		for (ItemStack i : items) {
			if (i.isEmpty()) continue;
			b.append(", ").append(i.getCount() > 1 ? i.getCount() + " " : "").append(i.getHoverName().getString());
			ItemEntity ie = new ItemEntity(l, p.getX(), y, p.getZ(), i);
			ie.setDeltaMovement((r.nextDouble() - 0.5) * 0.5, 0.15, (r.nextDouble() - 0.5) * 0.5);
			ie.setPickUpDelay(50);
			ie.setTarget(p.getUUID());
			markFor(ie, p);
			l.addFreshEntity(ie);
			if (out != null) out.add(ie);
		}
		return b.toString();
	}

	static void register() {
		NeoForge.EVENT_BUS.addListener((ItemTossEvent e) -> {
			ItemEntity it = e.getEntity();
			Player by = e.getPlayer();
			MinecraftServer server = by.getServer();
			if (server == null) return;
			// /give's flash of the item passes through here too and only becomes a fake afterwards: its age is at the end of its life by the next tick
			server.tell(new TickTask(server.getTickCount() + 1, () -> {
				if (!it.isRemoved() && it.getAge() < FRESH) mark(it, by);
			}));
		});
	}
}
