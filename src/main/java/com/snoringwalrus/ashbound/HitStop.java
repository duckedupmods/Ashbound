package com.snoringwalrus.ashbound;

import java.util.Map;
import java.util.WeakHashMap;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * The blow that lands stops the swing and what it hit for a moment, which is most of what makes it feel heavy. The ticks
 * are given back straight after (mixin/AnimationPlayerMixin plays them double), so a held swing costs no damage a second
 * and the client and the server stay together. Only a player's own blows, and a held thing isn't held again until it's
 * caught up.
 */
public final class HitStop {
	private HitStop() {}

	private static final int RANGE = 48;
	private static final float HEAVY = 0.6f, MEDIUM = 0.25f;
	/** until when, by game time, and for how long; one map a side, they run on different threads */
	private static final Map<Entity, long[]> SERVER = new WeakHashMap<>(), CLIENT = new WeakHashMap<>();

	private static Map<Entity, long[]> of(Entity e) {
		return e.level().isClientSide ? CLIENT : SERVER;
	}

	/** How hard a blow's stop is, 0 to 1 of a heavy one. */
	static int ticks(float heavy) {
		return heavy > HEAVY ? 3 : heavy > MEDIUM ? 2 : 1;
	}

	public static void hold(Entity e, int ticks) {
		long now = e.level().getGameTime();
		long[] h = of(e).get(e);
		if (h != null && now < h[0] + h[1]) return;
		of(e).put(e, new long[] {now + ticks, ticks});
	}

	/** Standing still this tick. */
	public static boolean held(Entity e) {
		long[] h = of(e).get(e);
		return h != null && e.level().getGameTime() < h[0];
	}

	/** Giving it back this tick. */
	public static boolean owes(Entity e) {
		long[] h = of(e).get(e);
		if (h == null) return false;
		long now = e.level().getGameTime();
		return now >= h[0] && now < h[0] + h[1];
	}

	static void strike(ServerLevel level, Entity by, Entity on, float heavy) {
		int t = ticks(heavy);
		hold(by, t);
		hold(on, t);
		PacketDistributor.sendToPlayersNear(level, null, on.getX(), on.getY(), on.getZ(), RANGE, new Net.HitHold(by.getId(), on.getId(), t));
	}
}
