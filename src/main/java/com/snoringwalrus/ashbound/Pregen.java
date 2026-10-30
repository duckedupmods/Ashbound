package com.snoringwalrus.ashbound;

import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.TicketType;
import net.minecraft.world.level.ChunkPos;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/**
 * A timing test for world generation, run headless: start the server with -Dashbound.pregen=R and it generates the
 * (2R+1)² chunks round x 512 (fresh ground, off the spawn), all at once as a moving player's would be, logs how long
 * that took and stops. Off unless the property is set.
 */
final class Pregen {
	private Pregen() {}

	private static int radius, cx, cz;
	private static long start;
	private static boolean on;

	static void hook() {
		radius = Integer.getInteger("ashbound.pregen", 0);
		if (radius <= 0) return;
		NeoForge.EVENT_BUS.addListener((ServerStartedEvent e) -> {
			ServerLevel level = e.getServer().overworld();
			cx = 32;
			cz = 0;
			int[] cap = "capital".equals(System.getProperty("ashbound.pregen.at")) ? Capital.centre() : null;
			if (cap != null) {
				cx = Math.floorDiv(cap[0], 16);
				cz = Math.floorDiv(cap[1] + 40, 16);
			}
			String at = System.getProperty("ashbound.pregen.at", "");
			if (at.startsWith("village:"))
				for (Capital.Site s : Capital.sites)
					if (s.name.equals(at.substring(8))) {
						cx = Math.floorDiv(s.x, 16);
						cz = Math.floorDiv(s.z, 16);
						Ashbound.LOG.info("pregen: round the {} village at {}, {} (floor {})", s.name, s.x, s.z, s.floor);
						break;
					}
			for (int x = -radius; x <= radius; x++)
				for (int z = -radius; z <= radius; z++)
					// a ticket, as a player's view puts down: the chunk's made on the worker threads, not waited for here
					level.getChunkSource().addRegionTicket(TicketType.FORCED, new ChunkPos(cx + x, cz + z), 0, new ChunkPos(cx + x, cz + z));
			start = System.nanoTime();
			on = true;
			Ashbound.LOG.info("pregen: {} chunks", (2 * radius + 1) * (2 * radius + 1));
		});
		NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post e) -> {
			if (!on) return;
			MinecraftServer server = e.getServer();
			ServerLevel level = server.overworld();
			int done = 0, all = 0;
			for (int x = -radius; x <= radius; x++)
				for (int z = -radius; z <= radius; z++) {
					all++;
					if (level.getChunkSource().getChunkNow(cx + x, cz + z) != null) done++;
				}
			if (server.getTickCount() % 40 == 0) Ashbound.LOG.info("pregen: {}/{}", done, all);
			if (done < all) return;
			on = false;
			Ashbound.LOG.info("pregen: done {} chunks in {} ms", all, (System.nanoTime() - start) / 1_000_000);
			server.halt(false);
		});
	}
}
