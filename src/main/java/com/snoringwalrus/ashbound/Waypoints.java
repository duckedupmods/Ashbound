package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import net.blay09.mods.waystones.api.MutableWaystone;
import net.blay09.mods.waystones.api.Waystone;
import net.blay09.mods.waystones.api.WaystoneStyle;
import net.blay09.mods.waystones.api.WaystoneStyles;
import net.blay09.mods.waystones.api.WaystonesAPI;
import net.blay09.mods.waystones.core.WaystoneManagerImpl;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.saveddata.SavedData;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/**
 * A waystone in every town, named for it: Highmourn's by the market fountain, each village's by its centre. It goes up
 * from the world as it really stands, the first time someone comes near, on the nearest open floor to the spot; the
 * world remembers which are up.
 */
final class Waypoints {
	private Waypoints() {}

	/** From the capital's centre: the market fountain (tools/capital_city.py FOUNTAIN). */
	private static final int PLAZA_X = -30, PLAZA_Z = 92;
	private static final int COME_NEAR = 80, SEARCH_FROM = 5, SEARCH_TO = 22, FLOOR_SLACK = 4, EVERY = 40;
	private static final String GIVEN = "warp_given", BAG_GIVEN = "bag_given";
	private static final int SHARE_EVERY = 100;
	private static final ResourceLocation STONE = ResourceLocation.fromNamespaceAndPath("waystones", "warp_stone");

	private static final class State extends SavedData {
		final Set<String> up = new HashSet<>();

		@Override
		public CompoundTag save(CompoundTag tag, HolderLookup.Provider reg) {
			ListTag list = new ListTag();
			for (String s : up) list.add(StringTag.valueOf(s));
			tag.put("up", list);
			return tag;
		}

		static State load(CompoundTag tag, HolderLookup.Provider reg) {
			State s = new State();
			for (Tag t : tag.getList("up", Tag.TAG_STRING)) s.up.add(t.getAsString());
			return s;
		}
	}

	private static State state(ServerLevel level) {
		return level.getDataStorage().computeIfAbsent(new SavedData.Factory<>(State::new, State::load, null), "ashbound_waypoints");
	}

	/** Where in a place the stone's looked for: x, the height of a floor there, z. */
	private static int[] anchor(Capital.Site s) {
		if (s == Capital.site) return new int[] {s.x + PLAZA_X, Capital.FLOOR + 1, s.z + PLAZA_Z};
		double[] g = s.d.points.getOrDefault("centre", new double[] {0, 1, 0});
		return new int[] {s.x + (int) g[0], s.floor + (int) g[1], s.z + (int) g[2]};
	}

	/** Solid under it and room for the stone; `clear`, with nothing right beside it either, so it stands in the open. */
	private static boolean fits(ServerLevel level, BlockPos p, boolean clear) {
		if (!level.getBlockState(p).isAir() || !level.getBlockState(p.above()).isAir() || !level.getBlockState(p.above(2)).isAir()) return false;
		if (!level.getBlockState(p.below()).isFaceSturdy(level, p.below(), Direction.UP)) return false;
		if (!clear) return true;
		for (int dx = -1; dx <= 1; dx++)
			for (int dz = -1; dz <= 1; dz++)
				if (!level.getBlockState(p.offset(dx, 0, dz)).isAir() || !level.getBlockState(p.offset(dx, 1, dz)).isAir()) return false;
		return true;
	}

	/** The nearest open floor to the spot, ring by ring. */
	private static BlockPos spot(ServerLevel level, int ax, int ay, int az) {
		for (int pass = 0; pass < 2; pass++)
			for (int r = SEARCH_FROM; r <= SEARCH_TO; r++)
				for (int d = -r; d <= r; d++)
					for (int side = 0; side < 4; side++) {
						int x = ax + (side == 0 ? d : side == 1 ? -d : side == 2 ? r : -r), z = az + (side == 0 ? r : side == 1 ? -r : side == 2 ? d : -d);
						for (int k = 0; k <= FLOOR_SLACK * 2; k++) {
							BlockPos p = new BlockPos(x, ay + (k % 2 == 0 ? k / 2 : -(k + 1) / 2), z);
							if (fits(level, p, pass == 0)) return p;
						}
					}
		return null;
	}

	private static WaystoneStyle style(String kind) {
		return switch (kind) {
			case "hold" -> WaystoneStyles.DEEPSLATE;
			case "tree" -> WaystoneStyles.MOSSY;
			default -> WaystoneStyles.DEFAULT;
		};
	}

	/** A waystone of this name at p. */
	static boolean raise(ServerLevel level, BlockPos p, String title, String kind) {
		var placed = WaystonesAPI.placeWaystone(level, p, style(kind));
		if (placed.isEmpty() || !(placed.get() instanceof MutableWaystone named)) return false;
		named.setName(Component.literal(title));
		WaystoneManagerImpl.get(level.getServer()).updateWaystone(placed.get());
		return true;
	}

	private static void comeNear(ServerLevel level, ServerPlayer p) {
		State st = state(level);
		for (Capital.Site s : Capital.near(p.getBlockX(), p.getBlockZ())) {
			String key = s.x + "," + s.z;
			if (st.up.contains(key)) continue;
			int[] a = anchor(s);
			if (p.distanceToSqr(a[0], p.getY(), a[2]) > COME_NEAR * COME_NEAR
					|| !level.hasChunksAt(a[0] - SEARCH_TO, a[2] - SEARCH_TO, a[0] + SEARCH_TO, a[2] + SEARCH_TO)) continue;
			BlockPos at = spot(level, a[0], a[1], a[2]);
			if (at == null) Ashbound.LOG.warn("No room for a waystone in {}", s.title);
			else raise(level, at, s.title, s.name);
			st.up.add(key);
			st.setDirty();
		}
	}

	/** Everyone carries a Warp Stone, whenever they started, once they've their class: it takes you to any waystone you've found. */
	private static void handOut(ServerPlayer p) {
		if (Classes.of(p) == null) return;
		if (!Coins.flag(p, BAG_GIVEN)) {
			Coins.setFlag(p, BAG_GIVEN);
			ItemStack bag = new ItemStack(Bag.POUCH.get());
			if (!p.getInventory().add(bag)) p.drop(bag, false);
			p.sendSystemMessage(Component.literal("You carry a Bottomless Bag. Right-click it to open it, sneak and right-click to put your whole pack in.").withStyle(ChatFormatting.GOLD));
		}
		if (Coins.flag(p, GIVEN)) return;
		Coins.setFlag(p, GIVEN);
		ItemStack s = new ItemStack(BuiltInRegistries.ITEM.get(STONE));
		if (!p.getInventory().add(s)) p.drop(s, false);
		p.sendSystemMessage(Component.literal("You carry a Warp Stone. Right-click a waystone to mark it, hold right-click on the stone to go to any that you or your party have marked.").withStyle(ChatFormatting.GOLD));
		p.sendSystemMessage(Component.literal("Press J for your Journal: it's where your quests are, and it'll show you how they work.").withStyle(ChatFormatting.GOLD));
		p.sendSystemMessage(Component.literal("Press I for your Bottomless Bag: it holds anything, as much as you like, and your party shares it.").withStyle(ChatFormatting.GOLD));
	}

	/** What one of a party has found, they all have: that takes in whoever joined late, and whoever was away when it was found. */
	private static void share(MinecraftServer server) {
		Set<ServerPlayer> seen = new HashSet<>();
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			if (!seen.add(p)) continue;
			List<ServerPlayer> party = new ArrayList<>(Party.others(p));
			if (party.isEmpty()) continue;
			party.add(p);
			seen.addAll(party);
			Map<UUID, Waystone> found = new LinkedHashMap<>();
			for (ServerPlayer m : party) for (Waystone w : WaystonesAPI.getActivatedWaystones(m)) found.put(w.getWaystoneUid(), w);
			for (ServerPlayer m : party) {
				List<Waystone> news = found.values().stream().filter(w -> !WaystonesAPI.isWaystoneActivated(m, w)).toList();
				news.forEach(w -> WaystonesAPI.activateWaystone(m, w));
				if (news.isEmpty()) continue;
				Component what = news.size() == 1 ? news.get(0).getName() : Component.literal(news.size() + " waystones");
				m.displayClientMessage(Component.literal("Your party marked ").append(what).withStyle(ChatFormatting.GOLD), true);
			}
		}
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post e) -> {
			if (e.getServer().getTickCount() % SHARE_EVERY == 0) share(e.getServer());
			if (e.getServer().getTickCount() % EVERY != 0) return;
			ServerLevel level = e.getServer().overworld();
			for (ServerPlayer p : level.players()) comeNear(level, p);
			for (ServerPlayer p : e.getServer().getPlayerList().getPlayers()) handOut(p);
		});
		NeoForge.EVENT_BUS.addListener((PlayerInteractEvent.RightClickItem e) -> {
			if (e.getLevel().dimension() != Lairs.GATES || !BuiltInRegistries.ITEM.getKey(e.getItemStack().getItem()).equals(STONE)) return;
			e.setCanceled(true);
			e.getEntity().displayClientMessage(Component.literal("Nothing answers in here. A gate has only the one way out.").withStyle(ChatFormatting.RED), true);
		});
	}
}
