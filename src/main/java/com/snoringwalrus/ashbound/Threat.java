package com.snoringwalrus.ashbound;

import java.util.Iterator;
import java.util.Map;
import java.util.WeakHashMap;

import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ShieldItem;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.living.LivingChangeTargetEvent;
import net.neoforged.neoforge.event.entity.living.LivingDamageEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/**
 * Who a monster's angriest with. Every blow on it builds threat, a tank's three times over and a thrall's a quarter, and
 * being hit builds it for a tank too, so it turns on whoever's earned it rather than on whoever touched it last. It
 * only changes its mind for someone well ahead of the one it's on. A taunt jumps the queue. Alone, a Caller's thralls
 * still hold it for as long as the Caller stays out of the fight.
 */
public final class Threat {
	private Threat() {}

	private static final float TANK = 3, THRALL = 0.25f, HIT_TANK = 2, TAUNT_OVER = 1.3f, TAUNT_LEAST = 20, SWITCH_OVER = 1.2f, FADE = 0.98f;
	private static final double FORGET = 40;
	private static final int EVERY = 20;
	private static final Map<Mob, Map<LivingEntity, Float>> TABLE = new WeakHashMap<>();

	static boolean tank(Player p) {
		Classes.Cls c = Classes.of(p);
		return c != null && c.role().equals("Tank") || p.getOffhandItem().getItem() instanceof ShieldItem || p.getMainHandItem().getItem() instanceof ShieldItem;
	}

	private static float weight(LivingEntity who) {
		if (Spells.isThrall(who)) return THRALL;
		return who instanceof Player p && tank(p) ? TANK : 1;
	}

	private static boolean angers(Mob m) {
		return m instanceof Enemy && !Spells.isThrall(m);
	}

	/** Someone hurt this monster for `amount`. */
	static void hit(Mob m, LivingEntity who, float amount) {
		if (angers(m) && amount > 0) TABLE.computeIfAbsent(m, k -> new WeakHashMap<>()).merge(who, amount * weight(who), Float::sum);
	}

	/** They've made it look at them, ahead of everyone. */
	static void taunt(Mob m, LivingEntity who) {
		if (angers(m)) {
			Map<LivingEntity, Float> t = TABLE.computeIfAbsent(m, k -> new WeakHashMap<>());
			float most = 0;
			for (float v : t.values()) most = Math.max(most, v);
			t.put(who, Math.max(most * TAUNT_OVER, TAUNT_LEAST));
		}
		m.setTarget(who);
	}

	/** They've slipped away: it has to find someone else. */
	static void forget(Mob m, LivingEntity who) {
		Map<LivingEntity, Float> t = TABLE.get(m);
		if (t != null) t.remove(who);
		m.setTarget(null);
	}

	private static boolean there(Mob m, LivingEntity who) {
		return who.isAlive() && !who.isRemoved() && who.level() == m.level() && who.distanceTo(m) < FORGET && !(who instanceof Player p && (p.isSpectator() || p.isCreative()));
	}

	/** Who it should be fighting; null if it has no quarrel with anyone here. */
	static LivingEntity choice(Mob m) {
		Map<LivingEntity, Float> t = TABLE.get(m);
		if (t == null) return null;
		LivingEntity top = null;
		float most = 0;
		for (Iterator<Map.Entry<LivingEntity, Float>> it = t.entrySet().iterator(); it.hasNext();) {
			Map.Entry<LivingEntity, Float> e = it.next();
			if (!there(m, e.getKey())) it.remove();
			else if (e.getValue() > most) {
				most = e.getValue();
				top = e.getKey();
			}
		}
		LivingEntity now = m.getTarget();
		Float held = now == null ? null : t.get(now);
		return held != null && most < held * SWITCH_OVER ? now : top;
	}

	private static void tick(ServerTickEvent.Post e) {
		if (e.getServer().getTickCount() % EVERY != 0) return;
		for (Iterator<Map.Entry<Mob, Map<LivingEntity, Float>>> it = TABLE.entrySet().iterator(); it.hasNext();) {
			Map.Entry<Mob, Map<LivingEntity, Float>> row = it.next();
			Mob m = row.getKey();
			if (m.isRemoved() || !m.isAlive()) {
				it.remove();
				continue;
			}
			row.getValue().replaceAll((who, v) -> v * FADE);
			LivingEntity top = choice(m);
			if (top != null && top != m.getTarget()) m.setTarget(top);
		}
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener(Threat::tick);
		NeoForge.EVENT_BUS.addListener((LivingDamageEvent.Post e) -> {
			Entity by = e.getSource().getEntity();
			if (e.getEntity() instanceof Mob m && by instanceof LivingEntity who && (who instanceof Player || Spells.isThrall(who))) hit(m, who, e.getNewDamage());
		});
		// a blow caught on a shield counts as much as one taken
		NeoForge.EVENT_BUS.addListener(EventPriority.LOWEST, (LivingIncomingDamageEvent e) -> {
			if (e.getEntity() instanceof Player p && e.getSource().getEntity() instanceof Mob m && tank(p)) hit(m, p, e.getAmount() * HIT_TANK / TANK);
		});
		// whatever turned it round (being hit, a goal looking for the nearest player), it goes for who's earned it
		NeoForge.EVENT_BUS.addListener((LivingChangeTargetEvent e) -> {
			if (!(e.getEntity() instanceof Mob m) || e.getNewAboutToBeSetTarget() == null) return;
			LivingEntity top = choice(m);
			if (top != null) e.setNewAboutToBeSetTarget(top);
		});
	}
}
