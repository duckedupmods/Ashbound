package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

import net.minecraft.core.Holder;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.Vec3;
import yesman.epicfight.gameasset.Animations;

import static com.snoringwalrus.ashbound.JoinedSkills.anim;
import static com.snoringwalrus.ashbound.JoinedSkills.later;
import static com.snoringwalrus.ashbound.JoinedSkills.lineHit;
import static com.snoringwalrus.ashbound.JoinedSkills.ringHit;
import static com.snoringwalrus.ashbound.JoinedSkills.strike;
import static com.snoringwalrus.ashbound.Skills.aim;
import static com.snoringwalrus.ashbound.Skills.each;
import static com.snoringwalrus.ashbound.Skills.look;
import static com.snoringwalrus.ashbound.Skills.magic;
import static com.snoringwalrus.ashbound.Skills.say;
import static com.snoringwalrus.ashbound.Skills.strength;
import static com.snoringwalrus.ashbound.Skills.thud;

/**
 * The skills a path teaches at its later levels ({@link Skills#UNLOCK}), two to a path: the first a tool for the job, the
 * second the thing the whole path was walking towards. Multipliers and cooldowns are in docs/BALANCE.md.
 */
final class SkillArts {
	private SkillArts() {}

	private static final int SECOND = 20;
	/** an arrow's base damage */
	private static final double ARROW = 2;

	private static Vec3 ahead(ServerPlayer p) {
		Vec3 f = p.getLookAngle().multiply(1, 0, 1);
		return f.lengthSqr() < 1e-4 ? new Vec3(0, 0, 1) : f.normalize();
	}

	private static void debuff(LivingEntity e, Holder<MobEffect> what, int ticks, int level) {
		e.addEffect(new MobEffectInstance(what, ticks, level));
	}

	private static List<Player> allies(ServerPlayer p, double r) {
		return p.serverLevel().getEntitiesOfClass(Player.class, p.getBoundingBox().inflate(r));
	}

	/** The nearest enemy you're looking at. */
	private static LivingEntity front(ServerPlayer p, double reach) {
		Vec3 from = p.getEyePosition(), dir = p.getLookAngle();
		LivingEntity best = null;
		double aim = 0.8;
		for (LivingEntity e : p.serverLevel().getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(reach), x -> x instanceof Enemy && x.isAlive())) {
			double d = e.getBoundingBox().getCenter().subtract(from).normalize().dot(dir);
			if (d > aim && p.hasLineOfSight(e)) {
				aim = d;
				best = e;
			}
		}
		return best;
	}

	private static void pull(ServerPlayer p, Vec3 to, double r, double speed) {
		each(p, to, r, e -> {
			e.setDeltaMovement(to.subtract(e.position()).normalize().scale(speed));
			e.hurtMarked = true;
		});
	}

	private static ItemStack bow(ServerPlayer p) {
		ItemStack b = p.getMainHandItem().getItem() instanceof BowItem ? p.getMainHandItem() : p.getOffhandItem();
		if (b.getItem() instanceof BowItem) return b;
		say(p, "Needs a bow in hand");
		return null;
	}

	private static List<Mob> thralls(ServerPlayer p) {
		return p.serverLevel().getEntitiesOfClass(Mob.class, p.getBoundingBox().inflate(40), e -> p.getUUID().equals(Spells.ownerOf(e)));
	}

	/** Vanilla poison is a flat point or two, nothing to anything past rank E; this is the Venom path's real bite, a second at a time. */
	static void venom(ServerPlayer p, LivingEntity e, float each, int seconds) {
		for (int t = 1; t <= seconds; t++)
			later(p, t * SECOND, () -> {
				if (!e.isAlive()) return;
				e.invulnerableTime = 0;
				e.hurt(p.damageSources().magic(), each);
			});
	}

	// ---------------------------------------------------------------- Vanguard

	static void shieldWall(ServerPlayer p, double m) {
		look(p, "shield_wall", p.position());
		thud(p);
		for (Player o : allies(p, 7)) debuff(o, MobEffects.DAMAGE_RESISTANCE, (int) (6 * SECOND * m), 1);
	}

	static void unbroken(ServerPlayer p, double m) {
		look(p, "unbroken", p.position());
		thud(p);
		debuff(p, MobEffects.DAMAGE_RESISTANCE, 7 * SECOND, 2);
		for (Mob e : p.serverLevel().getEntitiesOfClass(Mob.class, p.getBoundingBox().inflate(14), x -> x instanceof Enemy && x.isAlive())) Threat.taunt(e, p);
		later(p, 7 * SECOND, () -> {
			look(p, "unbroken_end", p.position());
			ringHit(p, p.position(), 7, 5 * m, 0.5);
			thud(p);
		});
	}

	static void oathCross(ServerPlayer p, double m) {
		anim(p, Animations.DANCING_EDGE);
		for (int t : new int[] {4, 9})
			later(p, t, () -> {
				Spells.skillFx(p.serverLevel(), "oath_cross", p.position(), p.getLookAngle(), t, p);
				lineHit(p, 6, 1.6, 1.1 * m);
				p.heal(p.getMaxHealth() * 0.03f);
			});
	}

	static void lastOath(ServerPlayer p, double m) {
		anim(p, Animations.THE_GUILLOTINE);
		look(p, "last_oath_rise", p.position());
		later(p, 20, () -> {
			look(p, "last_oath", p.position());
			lineHit(p, 12, 2, (4 + 4 * (1 - p.getHealth() / p.getMaxHealth())) * m);
			thud(p);
		});
	}

	// ---------------------------------------------------------------- Breaker

	static void faultLine(ServerPlayer p, double m) {
		anim(p, Animations.THE_GUILLOTINE);
		Vec3 go = ahead(p), from = p.position();
		for (int i = 0; i < 6; i++) {
			Vec3 at = from.add(go.scale(2 + i * 2.4));
			later(p, 12 + i * 3, () -> {
				Spells.skillFx(p.serverLevel(), "fault_line", at, go, 2.6f, p);
				ringHit(p, at, 2.6, 1.1 * m, 0.5);
			});
		}
		later(p, 12, () -> thud(p));
	}

	static void worldbreaker(ServerPlayer p, double m) {
		anim(p, Animations.THE_GUILLOTINE);
		look(p, "worldbreaker_rise", p.position());
		int[] when = {14, 26, 38};
		double[] reach = {5, 7, 9.5};
		for (int i = 0; i < when.length; i++) {
			double r = reach[i];
			later(p, when[i], () -> {
				Spells.skillFx(p.serverLevel(), "worldbreaker", p.position(), p.getLookAngle(), (float) r, p);
				ringHit(p, p.position(), r, 2.6 * m, 0.6);
				thud(p);
			});
		}
	}

	static void reapersMark(ServerPlayer p, double m) {
		LivingEntity t = front(p, 16);
		if (t == null) {
			say(p, "Nothing to mark");
			return;
		}
		Spells.skillFx(p.serverLevel(), "reapers_mark", t.position(), Vec3.ZERO, t.getBbHeight(), t);
		Skills.mark(t, (int) (10 * SECOND * m));
		strike(p, t, strength(p) * (float) m);
	}

	static void beheading(ServerPlayer p, double m) {
		LivingEntity t = front(p, 6);
		anim(p, Animations.THE_GUILLOTINE);
		look(p, "beheading_rise", p.position());
		if (t == null) return;
		later(p, 16, () -> {
			if (!t.isAlive()) return;
			boolean low = t.getHealth() < t.getMaxHealth() * 0.25f;
			Spells.skillFx(p.serverLevel(), "beheading", t.position(), p.getLookAngle(), low ? 1 : 0, t);
			strike(p, t, strength(p) * (float) ((low ? 14 : 6) * m));
			thud(p);
		});
	}

	// ---------------------------------------------------------------- Reaver

	static void redThirst(ServerPlayer p, double m) {
		look(p, "red_thirst", p.position());
		Skills.buff(p, "thirst", (int) (8 * SECOND * m));
	}

	static void crimsonRite(ServerPlayer p, double m) {
		p.setHealth(Math.max(1, p.getHealth() / 2));
		anim(p, Animations.STEEL_WHIRLWIND);
		look(p, "crimson_rite_rise", p.position());
		later(p, 14, () -> {
			look(p, "crimson_rite", p.position());
			ringHit(p, p.position(), 8, 9 * m, 0.4);
			each(p, p.position(), 8, e -> debuff(e, MobEffects.WITHER, 5 * SECOND, 1));
			thud(p);
		});
	}

	static void razorGale(ServerPlayer p, double m) {
		anim(p, Animations.STEEL_WHIRLWIND);
		Vec3 go = ahead(p), from = p.position();
		for (int i = 0; i < 7; i++) {
			Vec3 at = from.add(go.scale(2 + i * 2));
			later(p, 4 + i * 4, () -> {
				Spells.skillFx(p.serverLevel(), "razor_gale", at, go, 0, null);
				ringHit(p, at, 2.4, 1.0 * m, 0.25);
			});
		}
	}

	static void eyeOfStorm(ServerPlayer p, double m) {
		anim(p, Animations.STEEL_WHIRLWIND);
		for (int i = 0; i < 10; i++) {
			int n = i;
			later(p, 2 + i * 5, () -> {
				Spells.skillFx(p.serverLevel(), "eye_of_storm", p.position(), p.getLookAngle(), n, p);
				pull(p, p.position(), 8, 0.3);
				ringHit(p, p.position(), 4.5, 0.9 * m, 0);
			});
		}
	}

	// ---------------------------------------------------------------- Lancer

	static void dragonLunge(ServerPlayer p, double m) {
		anim(p, Animations.GRASPING_SPIRAL_FIRST);
		look(p, "dragon_lunge", p.position());
		lineHit(p, 8, 1.4, 2 * m);
		p.setDeltaMovement(ahead(p).scale(2).add(0, 0.25, 0));
		p.hurtMarked = true;
	}

	static void dragonsDescent(ServerPlayer p, double m) {
		Vec3 to = aim(p, 20);
		look(p, "skyfall_up", p.position());
		p.setDeltaMovement(ahead(p).scale(0.3).add(0, 1.7, 0));
		p.hurtMarked = true;
		Spells.skillFx(p.serverLevel(), "descent_mark", to, Vec3.ZERO, 7, null);
		later(p, 16, () -> {
			p.setDeltaMovement(to.subtract(p.position()).scale(1 / 6.0));
			p.hurtMarked = true;
			look(p, "descent_dive", p.position());
		});
		later(p, 22, () -> {
			p.resetFallDistance();
			look(p, "dragons_descent", p.position());
			ringHit(p, p.position(), 7, 7 * m, 0.6);
			thud(p);
		});
		later(p, 30, p::resetFallDistance);
	}

	static void spearHedge(ServerPlayer p, double m) {
		Vec3 go = ahead(p), from = p.position();
		anim(p, Animations.GRASPING_SPIRAL_FIRST);
		for (int i = 1; i <= 5; i++) {
			Vec3 at = from.add(go.scale(i * 2));
			later(p, i * 2, () -> {
				Spells.skillFx(p.serverLevel(), "spear_hedge", at, go, 0, null);
				each(p, at, 2.2, e -> {
					strike(p, e, strength(p) * (float) (1.1 * m));
					debuff(e, MobEffects.MOVEMENT_SLOWDOWN, 2 * SECOND, 3);
				});
			});
		}
	}

	static void thousandThrusts(ServerPlayer p, double m) {
		anim(p, Animations.GRASPING_SPIRAL_FIRST);
		for (int i = 0; i < 8; i++)
			later(p, 3 + i * 3, () -> {
				look(p, "thrust", p.position());
				lineHit(p, 9, 1, 0.75 * m);
			});
	}

	// ---------------------------------------------------------------- Shade

	static void smokeStep(ServerPlayer p, double m) {
		look(p, "vanish", p.position());
		each(p, p.position(), 5, e -> {
			debuff(e, MobEffects.MOVEMENT_SLOWDOWN, (int) (3 * SECOND * m), 2);
			debuff(e, MobEffects.WEAKNESS, (int) (3 * SECOND * m), 0);
		});
		Vec3 to = aim(p, 10).subtract(p.getLookAngle().scale(0.7));
		p.teleportTo(to.x, Math.max(to.y, p.getY()), to.z);
		p.resetFallDistance();
		look(p, "smoke_step", p.position());
	}

	static void deathBlossom(ServerPlayer p, double m) {
		ServerLevel l = p.serverLevel();
		List<LivingEntity> foes = new ArrayList<>(Skills.near(p, p.position(), 14));
		foes.sort(Comparator.comparingDouble(e -> e.distanceToSqr(p)));
		look(p, "vanish", p.position());
		debuff(p, MobEffects.INVISIBILITY, 2 * SECOND, 0);
		float hit = strength(p) * (float) (1.3 * m);
		for (int i = 0; i < 5 && !foes.isEmpty(); i++) {   // five cuts, round whoever's there
			LivingEntity t = foes.get(i % Math.min(5, foes.size()));
			later(p, i * 4, () -> {
				if (!t.isAlive()) return;
				Vec3 back = t.position().subtract(t.getLookAngle().multiply(1, 0, 1).normalize().scale(t.getBbWidth() / 2 + 1));
				p.teleportTo(back.x, t.getY(), back.z);
				Spells.skillFx(l, "blossom_cut", t.getBoundingBox().getCenter(), p.getLookAngle(), 0, null);
				strike(p, t, hit);
			});
		}
		later(p, 22, () -> {
			if (foes.isEmpty()) return;
			look(p, "death_blossom", p.position());
			p.resetFallDistance();
		});
		if (foes.isEmpty()) say(p, "Nothing near");
	}

	static void toxicCloud(ServerPlayer p, double m) {
		Vec3 at = aim(p, 18);
		int level = (int) Math.round((m - 1) / 0.4);
		for (int t = 0; t < 6; t++)
			later(p, t * SECOND, () -> {
				look(p, "toxic_cloud", at);
				each(p, at, 4, e -> {
					debuff(e, MobEffects.POISON, 3 * SECOND, level);
					strike(p, e, strength(p) * 0.35f);
				});
			});
	}

	static void plagueBloom(ServerPlayer p, double m) {
		look(p, "plague_bloom", p.position());
		float hit = strength(p) * (float) (6 * m);
		for (LivingEntity e : Skills.near(p, p.position(), 12)) {
			if (!e.hasEffect(MobEffects.POISON)) continue;
			Spells.skillFx(p.serverLevel(), "plague_burst", e.position(), Vec3.ZERO, e.getBbHeight(), null);
			strike(p, e, hit);
			each(p, e.position(), 3, o -> debuff(o, MobEffects.POISON, 6 * SECOND, 1));
		}
	}

	// ---------------------------------------------------------------- Hunter

	static void arrowRain(ServerPlayer p, double m) {
		ItemStack bow = bow(p);
		if (bow == null) return;
		ServerLevel l = p.serverLevel();
		Vec3 at = aim(p, 30);
		look(p, "arrow_rain_mark", at);
		for (int wave = 0; wave < 3; wave++)
			later(p, 6 + wave * 8, () -> {
				look(p, "arrow_rain", at);
				for (int i = 0; i < 8; i++) {
					Arrow a = new Arrow(l, p, new ItemStack(Items.ARROW), bow);
					a.setPos(at.x + (l.random.nextDouble() - 0.5) * 8, at.y + 14 + l.random.nextDouble() * 3, at.z + (l.random.nextDouble() - 0.5) * 8);
					a.setDeltaMovement(0, -2.6, 0);
					a.setBaseDamage(a.getBaseDamage() * 0.8 * m);
					a.setCritArrow(true);
					a.pickup = AbstractArrow.Pickup.DISALLOWED;
					l.addFreshEntity(a);
				}
				l.playSound(null, at.x, at.y, at.z, SoundEvents.ARROW_SHOOT, SoundSource.PLAYERS, 1.2f, 0.7f);
			});
	}

	static void piercingStar(ServerPlayer p, double m) {
		ItemStack bow = bow(p);
		if (bow == null) return;
		look(p, "star_charge", p.position());
		float hit = (float) (ARROW * 4.5 * Gear.bowPower(p) * 4.5 * m);
		later(p, 18, () -> {
			look(p, "piercing_star", p.position());
			JoinedSkills.lineAmount(p, 40, 1.2, hit);
			p.serverLevel().playSound(null, p.blockPosition(), SoundEvents.TRIDENT_THUNDER.value(), SoundSource.PLAYERS, 0.8f, 1.6f);
		});
	}

	static void spikePit(ServerPlayer p, double m) {
		Vec3 at = aim(p, 20);
		look(p, "spike_pit_set", at);
		for (int t : new int[] {12, 22, 32})
			later(p, t, () -> {
				look(p, "spike_pit", at);
				each(p, at, 3.5, e -> {
					strike(p, e, strength(p) * (float) m);
					debuff(e, MobEffects.MOVEMENT_SLOWDOWN, 3 * SECOND, 3);
				});
			});
	}

	static void killingGround(ServerPlayer p, double m) {
		Vec3 at = aim(p, 20);
		for (int t = 0; t < 10 * m; t++) {
			int n = t;
			later(p, t * SECOND, () -> {
				if (n % 2 == 0) look(p, "killing_ground", at);
				each(p, at, 8, e -> {
					Skills.mark(e, 30);
					debuff(e, MobEffects.MOVEMENT_SLOWDOWN, 30, 1);
				});
			});
		}
		p.serverLevel().playSound(null, at.x, at.y, at.z, SoundEvents.TRIPWIRE_CLICK_ON, SoundSource.PLAYERS, 1.2f, 0.5f);
	}

	// ---------------------------------------------------------------- Ashcaster

	static void flameLance(ServerPlayer p, double m) {
		look(p, "flame_lance", p.position());
		JoinedSkills.lineAmount(p, 14, 1.2, magic(p, 1.6 * m));
		p.serverLevel().playSound(null, p.blockPosition(), SoundEvents.BLAZE_SHOOT, SoundSource.PLAYERS, 1.2f, 0.6f);
	}

	static void meteor(ServerPlayer p, double m) {
		Vec3 at = aim(p, 28);
		float hit = magic(p, 6 * m);
		ServerLevel l = p.serverLevel();
		look(p, "meteor_fall", at);
		later(p, 24, () -> {
			look(p, "meteor", at);
			each(p, at, 7, e -> {
				strike(p, e, hit);
				e.igniteForSeconds(4);
			});
			l.playSound(null, at.x, at.y, at.z, SoundEvents.GENERIC_EXPLODE.value(), SoundSource.PLAYERS, 1.6f, 0.6f);
		});
	}

	static void voidLances(ServerPlayer p, double m) {
		Vec3 at = aim(p, 22);
		look(p, "void_lances", at);
		float hit = magic(p, 1.6 * m);
		each(p, at, 3.5, e -> {
			strike(p, e, hit);
			debuff(e, MobEffects.MOVEMENT_SLOWDOWN, 2 * SECOND, 3);
		});
		p.serverLevel().playSound(null, at.x, at.y, at.z, SoundEvents.ENDERMAN_TELEPORT, SoundSource.PLAYERS, 1, 0.7f);
	}

	static void eventHorizon(ServerPlayer p, double m) {
		Vec3 at = aim(p, 24).add(0, 1.5, 0);
		float tick = magic(p, 0.9 * m), burst = magic(p, 2 * m);
		look(p, "event_horizon", at);
		for (int t = 0; t < 6; t++)
			later(p, t * 10, () -> {
				pull(p, at, 10, 0.34);
				each(p, at, 7, e -> strike(p, e, tick));
			});
		later(p, 60, () -> {
			look(p, "event_burst", at);
			each(p, at, 8, e -> strike(p, e, burst));
		});
		p.serverLevel().playSound(null, at.x, at.y, at.z, SoundEvents.WARDEN_SONIC_CHARGE, SoundSource.PLAYERS, 1.2f, 0.6f);
	}

	// ---------------------------------------------------------------- Mender

	static void sanctify(ServerPlayer p, double m) {
		Vec3 at = p.position();
		ServerLevel l = p.serverLevel();
		for (int t = 0; t < 8; t++) {
			int n = t;
			later(p, t * SECOND, () -> {
				if (n % 3 == 0) look(p, "sanctify", at);
				for (Player o : l.getEntitiesOfClass(Player.class, new net.minecraft.world.phys.AABB(at, at).inflate(6, 3, 6))) o.heal(o.getMaxHealth() * (float) (0.03 * m));
			});
		}
	}

	static void secondDawn(ServerPlayer p, double m) {
		look(p, "second_dawn", p.position());
		for (Player o : allies(p, 16)) {
			o.setHealth(o.getMaxHealth());
			o.getActiveEffects().stream().filter(e -> !e.getEffect().value().isBeneficial()).map(MobEffectInstance::getEffect).toList().forEach(o::removeEffect);
			debuff(o, MobEffects.DAMAGE_RESISTANCE, (int) (3 * SECOND * m), 3);
			Spells.skillFx(p.serverLevel(), "dawn_on", o.position(), Vec3.ZERO, 0, o);
		}
		p.serverLevel().playSound(null, p.blockPosition(), SoundEvents.BEACON_ACTIVATE, SoundSource.PLAYERS, 1.2f, 1.3f);
	}

	static void holyLance(ServerPlayer p, double m) {
		look(p, "holy_lance", p.position());
		JoinedSkills.lineAmount(p, 16, 1.2, magic(p, 1.8 * m));
		p.heal(p.getMaxHealth() * 0.03f);
		p.serverLevel().playSound(null, p.blockPosition(), SoundEvents.BEACON_POWER_SELECT, SoundSource.PLAYERS, 1, 1.8f);
	}

	static void heavensWrath(ServerPlayer p, double m) {
		Vec3 at = aim(p, 24);
		ServerLevel l = p.serverLevel();
		float hit = magic(p, 0.7 * m);
		look(p, "heavens_wrath_mark", at);
		for (int t = 0; t < 8; t++)
			later(p, 10 + t * 5, () -> {
				Vec3 pt = at.add((l.random.nextDouble() - 0.5) * 12, 0, (l.random.nextDouble() - 0.5) * 12);
				look(p, "heavens_wrath", pt);
				each(p, pt, 2.8, e -> strike(p, e, hit));
				l.playSound(null, pt.x, pt.y, pt.z, SoundEvents.TRIDENT_THUNDER.value(), SoundSource.PLAYERS, 0.4f, 1.6f);
			});
		later(p, 50, () -> {
			for (Player o : allies(p, 10)) o.heal(o.getMaxHealth() * (float) (0.15 * m));
		});
	}

	// ---------------------------------------------------------------- Caller

	static void marrowBurst(ServerPlayer p, double m) {
		List<Mob> mine = thralls(p);
		if (mine.isEmpty()) say(p, "No thralls out");
		float hit = magic(p, m);
		for (Mob t : mine) {
			Spells.skillFx(p.serverLevel(), "marrow_burst", t.position(), Vec3.ZERO, 0, null);
			each(p, t.position(), 3, e -> strike(p, e, hit));
		}
	}

	static void legion(ServerPlayer p, double m) {
		look(p, "legion", p.position());
		Spells.host(p, 6, 1.1 * m);
	}

	static void soulMend(ServerPlayer p, double m) {
		List<Mob> mine = thralls(p);
		if (mine.isEmpty()) say(p, "No thralls out");
		for (Mob t : mine) {
			t.heal(t.getMaxHealth() * 0.5f);
			debuff(t, MobEffects.DAMAGE_BOOST, (int) (8 * SECOND * m), 1);
			Spells.skillFx(p.serverLevel(), "soul_mend", t.position(), Vec3.ZERO, 0, t);
		}
	}

	static void ascended(ServerPlayer p, double m) {
		if (thralls(p).stream().noneMatch(t -> t instanceof Thrall c && c.champion)) Spells.host(p, 1, 2.2 * m);
		later(p, 1, () -> {
			for (Mob t : thralls(p)) {
				if (!(t instanceof Thrall c) || !c.champion) continue;
				var dmg = c.getAttribute(Attributes.ATTACK_DAMAGE);
				var size = c.getAttribute(Attributes.SCALE);
				if (dmg == null || size == null) continue;
				double was = dmg.getBaseValue();
				dmg.setBaseValue(was * 2);
				size.setBaseValue(1.5);
				c.setHealth(c.getMaxHealth());
				Spells.skillFx(p.serverLevel(), "ascended", c.position(), Vec3.ZERO, 0, c);
				later(p, 15 * SECOND, () -> {
					dmg.setBaseValue(was);
					size.setBaseValue(1);
				});
			}
		});
	}
}
