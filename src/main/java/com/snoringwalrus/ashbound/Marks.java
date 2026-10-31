package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * What hangs over a townsperson's head, for you alone: a star over the people you come to see, a ! over anyone with a step of
 * your story or a favour to ask, a ? over anyone waiting on what you owe them. Only who's near is looked at, and the client's
 * told only when that changes.
 */
public final class Marks {
	private Marks() {}

	public static final int STAR = 0, NEWS = 1, OWED = 2;
	private static final int EVERY = 40;
	private static final double REACH = 40;
	private static final Map<UUID, Net.NpcMarks> LAST = new HashMap<>();

	/** -1 for nothing. */
	private static int of(ServerPlayer p, Npc n) {
		if (Errands.owed(p, n)) return OWED;
		if (Story.meeting(p, n.kindId()) != null || Errands.asks(p, n)) return NEWS;
		return n.keepsCounter() ? STAR : -1;
	}

	private static void look(ServerPlayer p) {
		List<Integer> ids = new ArrayList<>(), marks = new ArrayList<>();
		for (Npc n : p.level().getEntitiesOfClass(Npc.class, p.getBoundingBox().inflate(REACH))) {
			int m = of(p, n);
			if (m < 0) continue;
			ids.add(n.getId());
			marks.add(m);
		}
		Net.NpcMarks now = new Net.NpcMarks(ids, marks);
		if (now.equals(LAST.put(p.getUUID(), now))) return;
		PacketDistributor.sendToPlayer(p, now);
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post e) -> {
			if (e.getServer().getTickCount() % EVERY == 3) e.getServer().getPlayerList().getPlayers().forEach(Marks::look);
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedOutEvent e) -> LAST.remove(e.getEntity().getUUID()));
	}
}
