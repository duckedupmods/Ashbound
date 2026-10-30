package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import yesman.epicfight.gameasset.Animations;
import yesman.epicfight.world.capabilities.EpicFightCapabilities;
import yesman.epicfight.world.capabilities.entitypatch.player.ServerPlayerPatch;

/**
 * The R skill every Joined weapon earns, one to a weapon type, whatever gates went into it. The melee ones borrow
 * Epic Fight's big attack animations and land their own blow on top; the rest are the kind's own magic. All of it ends
 * in the same 20 seconds on the item, shown on the hotbar.
 */
public final class JoinedSkills {
	private JoinedSkills() {}

	public static final int COOLDOWN = 20 * 20;

	private record Later(ServerPlayer p, Runnable then) {}

	private static final List<List<Later>> SOON = new ArrayList<>();

	static void init() {
		for (int i = 0; i < 40; i++) SOON.add(new ArrayList<>());
		NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post e) -> {
			List<Later> now = SOON.remove(0);
			SOON.add(new ArrayList<>());
			for (Later l : now) if (l.p.isAlive()) l.then.run();
		});
	}

	private static void later(ServerPlayer p, int ticks, Runnable then) {
		SOON.get(ticks).add(new Later(p, then));
	}

	/** The name shown when it's used, by weapon type. */
	public static String name(String kind) {
		return switch (kind) {
			case "sword" -> "Severing Oath";
			case "dagger" -> "Two Shadows";
			case "hammer" -> "Concord's Fall";
			case "spear" -> "Unbroken Line";
			case "twohander" -> "Two Hearts";
			case "shield" -> "The Closed Hand";
			case "bow" -> "Twin Volley";
			case "black" -> "Black Accord";
			case "white" -> "White Accord";
			default -> "Bound Accord";
		};
	}

	static void use(ServerPlayer p) {
		ItemStack it = Joined.stage(p.getMainHandItem()) > 0 ? p.getMainHandItem() : p.getOffhandItem();
		if (Joined.stage(it) <= 0 || p.getCooldowns().isOnCooldown(it.getItem())) return;
		String kind = Smithing.boss(it).kind();
		p.getCooldowns().addCooldown(it.getItem(), COOLDOWN);
		p.displayClientMessage(Component.literal(name(kind)).withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD), true);
		p.serverLevel().playSound(null, p.blockPosition(), SoundEvents.FIRECHARGE_USE, SoundSource.PLAYERS, 1f, 0.6f);
		switch (kind) {
			case "sword" -> {
				anim(p, Animations.DANCING_EDGE);
				later(p, 7, () -> line(p, 9, 1.6, 2.2));
			}
			case "dagger" -> twoShadows(p);
			case "hammer" -> {
				anim(p, Animations.THE_GUILLOTINE);
				later(p, 14, () -> ring(p, p.position(), 6, 2.5, 0.6));
			}
			case "spear" -> {
				anim(p, Animations.GRASPING_SPIRAL_FIRST);
				later(p, 6, () -> line(p, 12, 1.1, 2.4));
			}
			case "twohander" -> {
				anim(p, Animations.STEEL_WHIRLWIND);
				for (int t : new int[] {8, 15, 22}) later(p, t, () -> ring(p, p.position(), 4, 1.1, 0.1));
			}
			case "shield" -> closedHand(p);
			case "bow" -> volley(p, it);
			case "white" -> Spells.accordHeal(p);
			case "summon" -> Spells.accordSummon(p, Smithing.boss(it));
			default -> Spells.accordBolts(p, Smithing.boss(it));
		}
	}

	private static void anim(ServerPlayer p, yesman.epicfight.api.animation.AnimationManager.AnimationAccessor<? extends yesman.epicfight.api.animation.types.StaticAnimation> a) {
		ServerPlayerPatch pp = EpicFightCapabilities.getEntityPatch(p, ServerPlayerPatch.class);
		if (pp != null) pp.playAnimationSynchronized(a, 0f);
	}

	private static float strength(ServerPlayer p) {
		return (float) p.getAttributeValue(Attributes.ATTACK_DAMAGE);
	}

	private static void strike(ServerPlayer p, LivingEntity e, float amount) {
		e.invulnerableTime = 0;
		e.hurt(p.damageSources().playerAttack(p), amount);
	}

	/** A blow along where you're looking, through everything in it. */
	private static void line(ServerPlayer p, double length, double width, double mult) {
		ServerLevel l = p.serverLevel();
		Vec3 from = p.getEyePosition().add(0, -0.4, 0), dir = p.getLookAngle();
		float amount = strength(p) * (float) mult;
		for (double d = 1; d < length; d += 0.5) {
			Vec3 at = from.add(dir.scale(d));
			l.sendParticles(ParticleTypes.FLAME, at.x, at.y, at.z, 3, 0.15, 0.15, 0.15, 0.01);
			if ((int) (d * 2) % 3 == 0) l.sendParticles(ParticleTypes.SWEEP_ATTACK, at.x, at.y, at.z, 1, 0, 0, 0, 0);
		}
		AABB box = new AABB(from, from.add(dir.scale(length))).inflate(width);
		for (LivingEntity e : l.getEntitiesOfClass(LivingEntity.class, box, x -> x instanceof Enemy && x.isAlive())) {
			Vec3 to = e.getBoundingBox().getCenter().subtract(from);
			double along = to.dot(dir);
			if (along > 0 && along < length + 1 && to.subtract(dir.scale(along)).length() <= width + e.getBbWidth() / 2) strike(p, e, amount);
		}
		l.playSound(null, p.blockPosition(), SoundEvents.PLAYER_ATTACK_SWEEP, SoundSource.PLAYERS, 1.2f, 0.6f);
	}

	/** A ring going out round a spot; lift throws them up. */
	private static void ring(ServerPlayer p, Vec3 at, double radius, double mult, double lift) {
		ServerLevel l = p.serverLevel();
		int n = (int) (radius * 12);
		for (int i = 0; i < n; i++) {
			double a = Mth.TWO_PI * i / n;
			l.sendParticles(ParticleTypes.FLAME, at.x + Math.cos(a) * radius, at.y + 0.2, at.z + Math.sin(a) * radius, 1, 0, 0.1, 0, 0.02);
			l.sendParticles(ParticleTypes.LAVA, at.x + Math.cos(a) * radius * 0.6, at.y + 0.2, at.z + Math.sin(a) * radius * 0.6, 1, 0, 0, 0, 0);
		}
		float amount = strength(p) * (float) mult;
		for (LivingEntity e : l.getEntitiesOfClass(LivingEntity.class, new AABB(at, at).inflate(radius, 3, radius), x -> x instanceof Enemy && x.isAlive())) {
			if (e.distanceToSqr(at) > (radius + 1) * (radius + 1)) continue;
			strike(p, e, amount);
			if (lift > 0) e.push(0, lift, 0);
		}
		l.playSound(null, p.blockPosition(), SoundEvents.ANVIL_LAND, SoundSource.PLAYERS, 0.9f, 0.5f);
	}

	/** Behind what you're looking at, and two blows in the back. */
	private static void twoShadows(ServerPlayer p) {
		ServerLevel l = p.serverLevel();
		Vec3 from = p.getEyePosition(), dir = p.getLookAngle();
		LivingEntity t = null;
		double best = 0.7;
		for (LivingEntity e : l.getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(10), x -> x instanceof Enemy && x.isAlive())) {
			double d = e.getEyePosition().subtract(from).normalize().dot(dir);
			if (d > best) {
				best = d;
				t = e;
			}
		}
		anim(p, Animations.EVISCERATE_FIRST);
		if (t == null) return;
		LivingEntity target = t;
		l.sendParticles(ParticleTypes.LARGE_SMOKE, p.getX(), p.getY() + 1, p.getZ(), 20, 0.3, 0.5, 0.3, 0.02);
		Vec3 back = target.position().subtract(target.getLookAngle().multiply(1, 0, 1).normalize().scale(target.getBbWidth() / 2 + 1));
		p.teleportTo(back.x, target.getY(), back.z);
		p.lookAt(net.minecraft.commands.arguments.EntityAnchorArgument.Anchor.EYES, target.getEyePosition());
		float amount = strength(p) * 1.5f;
		strike(p, target, amount);
		later(p, 7, () -> {
			if (target.isAlive()) strike(p, target, amount);
			l.sendParticles(ParticleTypes.CRIT, target.getX(), target.getY(1), target.getZ(), 24, 0.4, 0.4, 0.4, 0.3);
		});
	}

	/** It takes the room's eyes: all near turn on you and are thrown back, and you stand fast. */
	private static void closedHand(ServerPlayer p) {
		ServerLevel l = p.serverLevel();
		ring(p, p.position(), 5, 0.8, 0.3);
		p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 100, 1));
		for (Mob m : l.getEntitiesOfClass(Mob.class, p.getBoundingBox().inflate(9), x -> x instanceof Enemy && x.isAlive())) {
			m.setTarget(p);
			Vec3 away = m.position().subtract(p.position()).multiply(1, 0, 1).normalize().scale(0.8);
			m.push(away.x, 0.2, away.z);
		}
	}

	/** A fan of seven, each of them a full shot. */
	private static void volley(ServerPlayer p, ItemStack bow) {
		ServerLevel l = p.serverLevel();
		for (int i = -3; i <= 3; i++) {
			Arrow a = new Arrow(l, p, new ItemStack(Items.ARROW), bow);
			a.shootFromRotation(p, p.getXRot(), p.getYRot() + i * 5f, 0, 3.2f, 0.4f);
			a.setCritArrow(true);
			a.pickup = AbstractArrow.Pickup.DISALLOWED;
			l.addFreshEntity(a);
		}
		l.playSound(null, p.blockPosition(), SoundEvents.ARROW_SHOOT, SoundSource.PLAYERS, 1.2f, 0.7f);
	}
}
