package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.common.util.FakePlayer;
import net.neoforged.neoforge.event.entity.living.LivingDamageEvent;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Who's doing what in a fight: damage to monsters and healing that landed, for a party or for someone alone, with a thrall's hits going
 * to whoever called it. Ten quiet seconds end a fight and the next hit starts a new one. Healing comes through heal() here because a
 * heal doesn't say who sent it, and it only counts what the health bar actually gained. Each hit or heal also goes back to whoever did it
 * as a number (client/HitNumbers); the screen side of all this is client/MeterHud.
 */
final class Meters {
	private Meters() {}

	private static final int QUIET = 200, SEND_EVERY = 20, FORGET = 1200, NUMBER_RANGE = 64;
	private static final float SMALLEST_NUMBER = 0.5f;

	private static final class Line {
		final String name;
		double damage, heal, over;

		Line(String name) {
			this.name = name;
		}
	}

	private static final class Fight {
		final Map<UUID, Line> lines = new LinkedHashMap<>();
		long start, last;
		UUID by;
		boolean changed;
	}

	/** by party, or by player if they're alone */
	private static final Map<Object, Fight> FIGHTS = new HashMap<>();

	static void register() {
		NeoForge.EVENT_BUS.addListener(Meters::hit);
		NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post e) -> tick(e.getServer()));
		NeoForge.EVENT_BUS.addListener((ServerStoppedEvent e) -> FIGHTS.clear());
	}

	private static void hit(LivingDamageEvent.Post e) {
		LivingEntity target = e.getEntity();
		float amount = e.getNewDamage();
		if (amount <= 0 || target.level().isClientSide || target instanceof Player || Spells.isThrall(target)) return;
		Entity by = e.getSource().getEntity();
		ServerPlayer p = by instanceof ServerPlayer sp ? sp : null;
		if (p == null && by != null && Spells.isThrall(by) && Spells.ownerOf(by) != null) p = target.getServer().getPlayerList().getPlayer(Spells.ownerOf(by));
		if (p == null) return;
		credit(p, amount, 0);
		number(p, target, amount, by == p ? Net.HitNumber.HIT : Net.HitNumber.THRALL);
	}

	/** Heals `to`, to the credit of whoever sent it. */
	static void heal(Player by, LivingEntity to, float amount) {
		float was = to.getHealth();
		to.heal(amount);
		float gained = to.getHealth() - was;
		if (!(by instanceof ServerPlayer p)) return;
		// what found nobody hurt is kept apart: a healer whose friends are full still shows what they sent (11/7)
		if (amount - gained > 0 && to instanceof Player) credit(p, 0, 0, amount - Math.max(0, gained));
		if (gained <= 0) return;
		credit(p, 0, gained);
		number(p, to, gained, Net.HitNumber.HEAL);
	}

	private static void number(ServerPlayer p, LivingEntity on, float amount, int kind) {
		if (p instanceof FakePlayer || amount < SMALLEST_NUMBER || p.level() != on.level() || p.distanceTo(on) > NUMBER_RANGE) return;
		PacketDistributor.sendToPlayer(p, new Net.HitNumber(on.getX(), on.getY() + on.getBbHeight() * 0.8, on.getZ(), amount, kind));
	}

	private static void credit(ServerPlayer p, double damage, double heal) {
		credit(p, damage, heal, 0);
	}

	private static void credit(ServerPlayer p, double damage, double heal, double over) {
		Object key = Party.fightKey(p);
		long now = p.server.getTickCount();
		Fight f = FIGHTS.get(key);
		if (f == null || now - f.last > QUIET) {
			f = new Fight();
			f.start = now;
			FIGHTS.put(key, f);
		}
		f.last = now;
		f.by = p.getUUID();
		f.changed = true;
		Line l = f.lines.computeIfAbsent(p.getUUID(), u -> new Line(p.getGameProfile().getName()));
		l.damage += damage;
		l.heal += heal;
		l.over += over;
	}

	private static void tick(MinecraftServer server) {
		long now = server.getTickCount();
		if (now % SEND_EVERY != 0) return;
		for (Iterator<Fight> it = FIGHTS.values().iterator(); it.hasNext();) {
			Fight f = it.next();
			if (now - f.last > FORGET) it.remove();
			else if (f.changed) {
				f.changed = false;
				send(server, f);
			}
		}
	}

	private static void send(MinecraftServer server, Fight f) {
		ServerPlayer by = server.getPlayerList().getPlayer(f.by);
		if (by == null) return;
		List<Net.MeterLine> lines = new ArrayList<>();
		for (Line l : f.lines.values()) lines.add(new Net.MeterLine(l.name, (float) l.damage, (float) l.heal, (float) l.over));
		Net.Meter m = new Net.Meter(lines, Math.max(1f, (f.last - f.start) / 20f));
		for (UUID u : Party.circle(by).keySet()) {
			ServerPlayer o = server.getPlayerList().getPlayer(u);
			if (o != null && !(o instanceof FakePlayer)) PacketDistributor.sendToPlayer(o, m);
		}
	}

	/** For SelfTest: what p has on the meter in this fight, {damage, healing}. */
	static double[] of(ServerPlayer p) {
		Fight f = FIGHTS.get(Party.fightKey(p));
		Line l = f == null ? null : f.lines.get(p.getUUID());
		return l == null ? new double[2] : new double[] {l.damage, l.heal};
	}
}
