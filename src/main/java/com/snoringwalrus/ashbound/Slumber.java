package com.snoringwalrus.ashbound;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.tick.EntityTickEvent;

/**
 * Bosses sleep where they stand till someone comes close (WAKE blocks) or strikes them: no AI, slow breath rising off
 * them. Waking, they roar, flare and go straight for whoever woke them. A boss that has woken once stays awake.
 */
public final class Slumber {
	private Slumber() {}

	static final String ASLEEP = "ashbound_asleep", AWAKE = "ashbound_awake";
	static final double WAKE = 14;

	static boolean boss(Object e) {
		return e instanceof MobSkills.User u && u.kind().boss();
	}

	static void register() {
		NeoForge.EVENT_BUS.addListener((EntityJoinLevelEvent e) -> {
			if (e.getLevel().isClientSide() || !(e.getEntity() instanceof Mob m) || !boss(m)) return;
			if (m.getTags().contains(AWAKE) || m.getTags().contains(ASLEEP)) return;
			m.addTag(ASLEEP);
			m.setNoAi(true);
		});
		NeoForge.EVENT_BUS.addListener((EntityTickEvent.Post e) -> {
			if (!(e.getEntity() instanceof Mob m) || !(m.level() instanceof ServerLevel level) || m.tickCount % 10 != 0
					|| !m.getTags().contains(ASLEEP)) return;
			Player p = level.getNearestPlayer(m.getX(), m.getY(), m.getZ(), WAKE + m.getBbWidth() / 2,
					t -> t instanceof Player q && !q.isSpectator() && !q.isCreative());
			if (p != null) wake(level, m, p);
			else if (m.tickCount % 40 == 0)
				level.sendParticles(ParticleTypes.POOF, m.getX(), m.getEyeY(), m.getZ(), 2, m.getBbWidth() * 0.2, 0.1, m.getBbWidth() * 0.2, 0.005);
		});
		NeoForge.EVENT_BUS.addListener((LivingIncomingDamageEvent e) -> {
			if (e.getEntity() instanceof Mob m && m.level() instanceof ServerLevel level && m.getTags().contains(ASLEEP))
				wake(level, m, e.getSource().getEntity() instanceof Player p ? p : null);
		});
	}

	static void wake(ServerLevel level, Mob m, Player by) {
		m.removeTag(ASLEEP);
		m.addTag(AWAKE);
		m.setNoAi(false);
		if (by != null) m.setTarget(by);
		float big = Math.max(1f, m.getBbHeight() / 2f);
		level.playSound(null, m.blockPosition(), SoundEvents.RAVAGER_ROAR, SoundSource.HOSTILE, 2.5f, 0.55f);
		level.playSound(null, m.blockPosition(), SoundEvents.WARDEN_EMERGE, SoundSource.HOSTILE, 1.2f, 0.8f);
		level.sendParticles(ParticleTypes.SONIC_BOOM, m.getX(), m.getY() + m.getBbHeight() * 0.6, m.getZ(), 1, 0, 0, 0, 0);
		level.sendParticles(ParticleTypes.LARGE_SMOKE, m.getX(), m.getY() + 0.5, m.getZ(), 40, big, 0.4, big, 0.05);
		level.sendParticles(Spells.spark(MobMoves.gate(((MobSkills.User) m).kind())), m.getX(), m.getY() + m.getBbHeight() * 0.5, m.getZ(),
				60, big, big, big, 0.15);
		Component msg = Component.literal((m.hasCustomName() ? m.getCustomName().getString() : m.getName().getString()) + " awakens!");
		for (ServerPlayer p : level.players())
			if (p.distanceToSqr(m) < 64 * 64) p.displayClientMessage(msg, true);
	}
}
