package com.snoringwalrus.ashbound.client;

import java.util.UUID;

import com.snoringwalrus.ashbound.Net;

import net.minecraft.client.Minecraft;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.Level;
import net.neoforged.fml.ModList;

/**
 * Your party on Xaero's minimap and world map, wherever they are in the world. Xaero's are in the pack but aren't
 * required, so nothing of theirs is touched unless they're loaded, and each map's part lives in a class of its own.
 */
public final class PartyMap {
	private PartyMap() {}

	private static boolean mini, world;

	/** Each client tick until both are in: their managers appear some time after startup. */
	public static void tick() {
		if (!mini && ModList.get().isLoaded("xaerominimap")) mini = Mini.join();
		if (!world && ModList.get().isLoaded("xaeroworldmap")) world = World.join();
	}

	private static java.util.Iterator<Net.PartySpot> others() {
		Minecraft mc = Minecraft.getInstance();
		UUID me = mc.player == null ? null : mc.player.getUUID();
		return Net.clientSpots.stream().filter(s -> !s.id().equals(me)).iterator();
	}

	private static ResourceKey<Level> dimension(Net.PartySpot s) {
		return ResourceKey.create(Registries.DIMENSION, ResourceLocation.parse(s.dim()));
	}

	private static final class Mini implements xaero.hud.minimap.player.tracker.system.IRenderedPlayerTracker<Net.PartySpot>,
			xaero.hud.minimap.player.tracker.system.ITrackedPlayerReader<Net.PartySpot> {
		static boolean join() {
			var mod = xaero.common.HudMod.INSTANCE;
			if (mod == null || mod.getPlayerTracker() == null) return false;
			mod.getPlayerTracker().register("ashbound_party", new Mini());
			return true;
		}

		@Override public xaero.hud.minimap.player.tracker.system.ITrackedPlayerReader<Net.PartySpot> getReader() { return this; }
		@Override public java.util.Iterator<Net.PartySpot> getTrackedPlayerIterator() { return others(); }
		@Override public UUID getId(Net.PartySpot s) { return s.id(); }
		@Override public double getX(Net.PartySpot s) { return s.x(); }
		@Override public double getY(Net.PartySpot s) { return s.y(); }
		@Override public double getZ(Net.PartySpot s) { return s.z(); }
		@Override public ResourceKey<Level> getDimension(Net.PartySpot s) { return dimension(s); }
	}

	private static final class World implements xaero.map.radar.tracker.system.IPlayerTrackerSystem<Net.PartySpot>,
			xaero.map.radar.tracker.system.ITrackedPlayerReader<Net.PartySpot> {
		static boolean join() {
			var systems = xaero.map.WorldMap.playerTrackerSystemManager;
			if (systems == null) return false;
			systems.register("ashbound_party", new World());
			return true;
		}

		@Override public xaero.map.radar.tracker.system.ITrackedPlayerReader<Net.PartySpot> getReader() { return this; }
		@Override public java.util.Iterator<Net.PartySpot> getTrackedPlayerIterator() { return others(); }
		@Override public UUID getId(Net.PartySpot s) { return s.id(); }
		@Override public double getX(Net.PartySpot s) { return s.x(); }
		@Override public double getY(Net.PartySpot s) { return s.y(); }
		@Override public double getZ(Net.PartySpot s) { return s.z(); }
		@Override public ResourceKey<Level> getDimension(Net.PartySpot s) { return dimension(s); }
	}
}
