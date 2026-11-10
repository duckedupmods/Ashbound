package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import javax.annotation.Nullable;

import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.player.Player;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.living.LivingChangeTargetEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.player.AttackEntityEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/**
 * Downed, not dead (the whole mod): a player in a party who'd die with a party member near goes down instead. They crawl,
 * can't fight or use things, monsters leave them be, and they bleed out over BLEED ticks. A party member crouching beside
 * them for REVIVE ticks brings them back at a third of their health. They die for real when they bleed out, when they're
 * hit again, when they log out, or when everyone near them is down too. Alone, you just die. Nothing of it is saved.
 * (The arena will hook in here to put its fallen on the stands.)
 */
final class Downed {
	private Downed() {}

	/** how long you bleed out; how long a crouch beside you takes to bring you back; how near they must be, and a helper must be for you to go down */
	static final int BLEED = 600, REVIVE = 60;
	static final double REACH = 2.5, HELP = 96;
	static final float BACK = 0.3f;

	static final class Down {
		final long since;
		int left = BLEED, progress;
		@Nullable
		UUID by;

		Down(long since) {
			this.since = since;
		}
	}

	static final Map<UUID, Down> DOWN = new HashMap<>();
	/** let these die for real (bleeding out, hit again, the party wiped) */
	private static final Set<UUID> LET_DIE = new HashSet<>();

	static boolean is(Player p) {
		return DOWN.containsKey(p.getUUID());
	}

	/** Party members near p who could come for them: online, same world, alive, not down themselves. */
	static List<ServerPlayer> helpers(ServerPlayer p) {
		List<ServerPlayer> out = new ArrayList<>();
		for (ServerPlayer o : Party.others(p))
			if (o.level() == p.level() && o.isAlive() && !o.isSpectator() && !is(o) && o.distanceTo(p) < HELP) out.add(o);
		return out;
	}

	// ---------------------------------------------------------------- going down

	private static void dying(LivingDeathEvent e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || p.isCreative() || p.isSpectator()) return;
		if (LET_DIE.remove(p.getUUID())) {
			DOWN.remove(p.getUUID());
			return;
		}
		DamageSource src = e.getSource();
		if (is(p)) {
			// hit again while down: that's it
			finish(p, false);
			return;
		}
		if (src.is(DamageTypeTags.BYPASSES_INVULNERABILITY) || helpers(p).isEmpty()) return;
		e.setCanceled(true);
		down(p);
	}

	/** p goes down: crawling at 1 health, bleeding out, the party told. */
	static void down(ServerPlayer p) {
		ServerLevel l = p.serverLevel();
		DOWN.put(p.getUUID(), new Down(l.getGameTime()));
		p.setHealth(1f);
		p.invulnerableTime = 30;
		p.clearFire();
		p.setForcedPose(Pose.SWIMMING);
		p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, BLEED + 40, 3, false, false, false));
		p.addEffect(new MobEffectInstance(MobEffects.GLOWING, BLEED + 40, 0, false, false, false));
		// monsters on them look for someone else
		for (Mob m : l.getEntitiesOfClass(Mob.class, p.getBoundingBox().inflate(32), m -> m.getTarget() == p)) m.setTarget(null);
		l.playSound(null, p.getX(), p.getY(), p.getZ(), SoundEvents.PLAYER_HURT, SoundSource.PLAYERS, 1.2f, 0.6f);
		l.playSound(null, p.getX(), p.getY(), p.getZ(), SoundEvents.ARMOR_EQUIP_CHAIN.value(), SoundSource.PLAYERS, 1f, 0.5f);
		String name = p.getGameProfile().getName();
		for (ServerPlayer o : Party.others(p))
			o.sendSystemMessage(Component.literal(name + " is down! Crouch beside them to bring them back (" + BLEED / 20 + "s).").withStyle(ChatFormatting.RED, ChatFormatting.BOLD));
		p.sendSystemMessage(Component.literal("You're down. Hold on: your party can bring you back.").withStyle(ChatFormatting.RED));
	}

	/** Brought back by `by`: a third of their health, on their feet. */
	static void revive(ServerPlayer p, @Nullable ServerPlayer by) {
		if (DOWN.remove(p.getUUID()) == null) return;
		up(p);
		p.setHealth(Math.max(1f, p.getMaxHealth() * BACK));
		p.invulnerableTime = 40;
		ServerLevel l = p.serverLevel();
		l.sendParticles(ParticleTypes.HAPPY_VILLAGER, p.getX(), p.getY() + 1, p.getZ(), 16, 0.5, 0.6, 0.5, 0.1);
		l.playSound(null, p.getX(), p.getY(), p.getZ(), SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 0.7f, 1.4f);
		String name = p.getGameProfile().getName();
		if (by != null) {
			p.displayClientMessage(Component.literal(by.getGameProfile().getName() + " brought you back").withStyle(ChatFormatting.GREEN), true);
			for (ServerPlayer o : Party.others(p))
				o.displayClientMessage(Component.literal(by.getGameProfile().getName() + " brought " + name + " back").withStyle(ChatFormatting.GREEN), true);
		}
	}

	private static void up(ServerPlayer p) {
		p.setForcedPose(null);
		p.removeEffect(MobEffects.MOVEMENT_SLOWDOWN);
		p.removeEffect(MobEffects.GLOWING);
	}

	/** They die for real. */
	static void finish(ServerPlayer p, boolean kill) {
		DOWN.remove(p.getUUID());
		up(p);
		if (kill && p.isAlive()) {
			LET_DIE.add(p.getUUID());
			p.hurt(p.damageSources().genericKill(), Float.MAX_VALUE);
			LET_DIE.remove(p.getUUID());
		}
	}

	// ---------------------------------------------------------------- while down

	private static void tick(ServerTickEvent.Post e) {
		if (DOWN.isEmpty()) return;
		var server = e.getServer();
		for (UUID u : new ArrayList<>(DOWN.keySet())) {
			ServerPlayer p = server.getPlayerList().getPlayer(u);
			Down d = DOWN.get(u);
			if (p == null || d == null || !p.isAlive()) {
				DOWN.remove(u);
				continue;
			}
			step(p, d);
		}
	}

	/** One tick down: bleeding, the crawl held, a helper's crouch counted. */
	static void step(ServerPlayer p, Down d) {
		ServerLevel l = p.serverLevel();
		p.setForcedPose(Pose.SWIMMING);
		if (p.getHealth() > 1f) p.setHealth(1f);
		// a helper crouching beside them
		ServerPlayer helper = null;
		for (ServerPlayer o : Party.others(p))
			if (o.isCrouching() && !is(o) && o.isAlive() && o.level() == l && o.distanceTo(p) <= REACH) {
				helper = o;
				break;
			}
		if (helper != null) {
			d.progress++;
			d.by = helper.getUUID();
			String bar = bar(d.progress / (float) REVIVE);
			helper.displayClientMessage(Component.literal("Reviving " + p.getGameProfile().getName() + "  " + bar).withStyle(ChatFormatting.GREEN), true);
			p.displayClientMessage(Component.literal("Being brought back  " + bar).withStyle(ChatFormatting.GREEN), true);
			if (d.progress % 10 == 0) l.sendParticles(ParticleTypes.HEART, p.getX(), p.getY() + 0.6, p.getZ(), 1, 0.3, 0.2, 0.3, 0);
			if (d.progress >= REVIVE) {
				revive(p, helper);
				return;
			}
			return;      // no bleeding while someone holds you
		}
		d.progress = Math.max(0, d.progress - 2);
		d.left--;
		if (d.left % 20 == 0)
			p.displayClientMessage(Component.literal("DOWN  bleeding out " + d.left / 20 + "s  (a party member can crouch beside you)").withStyle(ChatFormatting.RED), true);
		if (d.left % 8 == 0) l.sendParticles(new DustParticleOptions(new org.joml.Vector3f(0.6f, 0.02f, 0.02f), 1.2f), p.getX(), p.getY() + 0.3, p.getZ(), 2, 0.3, 0.1, 0.3, 0);
		if (d.left <= 0) {
			p.sendSystemMessage(Component.literal("You bled out.").withStyle(ChatFormatting.DARK_RED));
			finish(p, true);
			return;
		}
		// everyone near them down (or nobody left to come): the party's beaten
		if (helpers(p).isEmpty()) {
			finish(p, true);
		}
	}

	private static String bar(float f) {
		int n = Math.round(Math.max(0, Math.min(1, f)) * 12);
		return "[" + "|".repeat(n) + ".".repeat(12 - n) + "]";
	}

	// ---------------------------------------------------------------- what the downed can't do

	private static void noAttack(AttackEntityEvent e) {
		if (is(e.getEntity())) e.setCanceled(true);
	}

	private static <E extends PlayerInteractEvent & net.neoforged.bus.api.ICancellableEvent> void noUse(E e) {
		if (is(e.getEntity())) e.setCanceled(true);
	}

	private static void noTarget(LivingChangeTargetEvent e) {
		if (e.getNewAboutToBeSetTarget() instanceof Player p && is(p)) e.setCanceled(true);
	}

	private static void left(PlayerEvent.PlayerLoggedOutEvent e) {
		if (e.getEntity() instanceof ServerPlayer p && is(p)) finish(p, true);
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener(EventPriority.LOWEST, Downed::dying);
		NeoForge.EVENT_BUS.addListener(Downed::tick);
		NeoForge.EVENT_BUS.addListener(Downed::noAttack);
		NeoForge.EVENT_BUS.addListener(PlayerInteractEvent.RightClickItem.class, Downed::noUse);
		NeoForge.EVENT_BUS.addListener(PlayerInteractEvent.RightClickBlock.class, Downed::noUse);
		NeoForge.EVENT_BUS.addListener(PlayerInteractEvent.EntityInteract.class, Downed::noUse);
		NeoForge.EVENT_BUS.addListener(Downed::noTarget);
		NeoForge.EVENT_BUS.addListener(Downed::left);
	}
}
