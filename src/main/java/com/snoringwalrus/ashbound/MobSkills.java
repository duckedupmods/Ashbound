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
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitlesAnimationPacket;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.BossEvent;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.event.EventHooks;
import yesman.epicfight.api.animation.AnimationManager.AnimationAccessor;
import yesman.epicfight.api.animation.types.StaticAnimation;
import yesman.epicfight.gameasset.Animations;
import yesman.epicfight.world.capabilities.EpicFightCapabilities;
import yesman.epicfight.world.capabilities.entitypatch.LivingEntityPatch;

/**
 * The gate monsters' own skills (mob_moves.json lists who has which), their bosses' phases, the elites' and bosses'
 * bars, and the ward on a boss whose dungeon has no seal. A skill is a little timeline the monster runs on the
 * server: a wind-up you can read (an Epic Fight move, a sound, sparks where it will land), then what it does. While
 * one runs the monster does nothing else (SkillGoal holds its legs). Everything that hurts, burns or chills is in its
 * dungeon's own element (Spells.spark/dust/element), so a Foundry caster's bolt is fire and a Frost one's is ice.
 */
public final class MobSkills {
	private MobSkills() {}

	/** What a monster that fights with skills shows the rest of the code. */
	public interface User {
		GateMobs.Kind kind();

		State state();
	}

	/** A lingering patch of the dungeon's element (a cloud, a burning pool): hurts whoever stands in it. */
	record Hazard(Vec3 at, double radius, long until, float damage) {}

	/** One monster's skill state. */
	public static final class State {
		String active;
		MobMoves.Skill skill;
		int t;
		@Nullable
		LivingEntity target;
		Vec3 at = Vec3.ZERO, dir = Vec3.ZERO;
		final List<Vec3> marks = new ArrayList<>();
		final Set<UUID> struck = new HashSet<>();
		final Map<String, Long> next = new HashMap<>();
		final List<UUID> minions = new ArrayList<>();
		final List<Hazard> hazards = new ArrayList<>();
		int phase = 1, invulnerable;
		boolean warded, gripped;
		@Nullable
		ServerBossEvent bar;

		void save(CompoundTag tag) {
			tag.putInt("ashbound_phase", phase);
			tag.putBoolean("ashbound_warded", warded);
		}

		void load(CompoundTag tag) {
			phase = Math.max(1, tag.getInt("ashbound_phase"));
			warded = tag.getBoolean("ashbound_warded");
		}
	}

	// ---------------------------------------------------------------- what the AI asks

	public static boolean busy(Mob m) {
		return m instanceof User u && u.state().active != null;
	}

	public static int phase(Mob m) {
		return m instanceof User u ? u.state().phase : 1;
	}

	/** A skill can start: off cooldown, its phase reached, and whatever else it needs. */
	static boolean ready(Mob m, MobMoves.Skill sk) {
		if (!(m instanceof User u) || u.state().active != null || u.state().invulnerable > 0) return false;
		State s = u.state();
		if (s.phase < sk.phase()) return false;
		Long at = s.next.get(sk.name());
		if (at != null && m.level().getGameTime() < at) return false;
		LivingEntity t = m.getTarget();
		return switch (sk.name()) {
			case "heal" -> m.getHealth() < m.getMaxHealth() * 0.7f;
			case "summon" -> alive(m, s) < (u.kind().boss() ? 6 : 3);
			case "pull", "bolt", "volley", "beam", "breath" -> t != null && m.hasLineOfSight(t);
			default -> true;
		};
	}

	private static int alive(Mob m, State s) {
		if (!(m.level() instanceof ServerLevel level)) return 0;
		s.minions.removeIf(id -> {
			Entity e = level.getEntity(id);
			return e == null || !e.isAlive();
		});
		return s.minions.size();
	}

	/** Starts a skill (an Epic Fight behaviour's action). */
	static void cast(Mob m, MobMoves.Skill sk) {
		if (!(m instanceof User u) || !(m.level() instanceof ServerLevel)) return;
		State s = u.state();
		s.active = sk.name();
		s.skill = sk;
		s.t = 0;
		s.target = m.getTarget();
		s.marks.clear();
		s.struck.clear();
		int cd = MobMoves.cooldown(sk.name());
		if (u.kind().boss()) cd = (int) (cd * (1.0 - 0.18 * (s.phase - 1)));
		s.next.put(sk.name(), m.level().getGameTime() + cd);
		m.getNavigation().stop();
	}

	// ---------------------------------------------------------------- every tick, on the server

	static void tick(Mob m) {
		if (!(m instanceof User u) || !(m.level() instanceof ServerLevel level)) return;
		State s = u.state();
		GateMobs.Kind k = u.kind();
		if (s.invulnerable > 0) s.invulnerable--;
		if (!s.gripped || m.tickCount % 40 == 0) MobMoves.grip(m, k);
		if (k.key() && !m.hasGlowingTag()) m.setGlowingTag(true);
		bar(m, level, s, k);
		hazards(m, level, s);
		if (k.boss()) phases(m, level, s, k);
		if (s.active == null) return;
		if (!m.isAlive()) {
			s.active = null;
			return;
		}
		LivingEntity t = s.target;
		if (t != null && (!t.isAlive() || t.level() != m.level())) t = s.target = null;
		if (t != null && s.t < 6) m.getLookControl().setLookAt(t, 60, 60);
		boolean done;
		try {
			done = run(m, level, s, k, t);
		} catch (RuntimeException e) {
			Ashbound.LOG.error("monster skill {} failed", s.active, e);
			done = true;
		}
		s.t++;
		if (done || s.t > 140) {
			if (m.isInvisible() && "burrow".equals(s.active)) m.setInvisible(false);
			s.active = null;
		}
	}

	/** One step of the running skill; true when it's over. */
	private static boolean run(Mob m, ServerLevel level, State s, GateMobs.Kind k, @Nullable LivingEntity t) {
		double size = size(k);
		float atk = (float) m.getAttributeValue(Attributes.ATTACK_DAMAGE);
		String gate = MobMoves.gate(k);
		return switch (s.active) {
			case "phase" -> s.t >= 50;
			case "leap" -> {
				if (s.t == 0) {
					anim(m, Animations.BIPED_LANDING);
					sound(m, SoundEvents.RAVAGER_ROAR, 0.8f, 1.3f);
				}
				if (s.t == 0) fx(level, "gather", gate, m.position().add(0, 1, 0), new Vec3(10, 0, 0), (float) (1.6 * size), null);
				if (s.t < 10) yield false;
				if (s.t == 10) {
					Vec3 to = t != null ? t.position() : m.position().add(m.getLookAngle().scale(6));
					Vec3 d = to.subtract(m.position());
					double flight = 16;
					m.setDeltaMovement(d.x / flight, 0.75 + Math.min(0.6, d.length() * 0.03), d.z / flight);
					m.hasImpulse = true;
					s.at = to;
					fx(level, "launch", gate, m.position(), Vec3.ZERO, 2, null);
					fx(level, "tell", gate, to, new Vec3(flight, 0, 0), (float) (2.6 * size), null);
					yield false;
				}
				m.getNavigation().stop();
				trail(level, m, gate);
				if (s.t > 14 && m.onGround() || s.t > 60) {
					slam(m, level, s, m.position(), 2.6 * size, atk * 1.5f, 1.2, gate);
					anim(m, k.spider() ? Animations.SPIDER_ATTACK : Animations.BIPED_MOB_GREATSWORD);
					yield true;
				}
				yield false;
			}
			case "slam" -> {
				Vec3 at = m.position().add(flat(m.getLookAngle()).scale(MobMoves.reach(k) * 0.55));
				if (s.t == 0) {
					anim(m, k.spider() ? Animations.SPIDER_JUMP_ATTACK : Animations.BIPED_MOB_GREATSWORD);
					fx(level, "tell", gate, at, new Vec3(14, 0, 0), (float) (2.4 * size), null);
				}
				if (s.t < 14) yield false;
				if (s.t == 14) slam(m, level, s, at, 2.4 * size, atk * 1.6f, 1.0, gate);
				yield s.t > 26;
			}
			case "charge" -> {
				if (s.t == 0) {
					sound(m, SoundEvents.RAVAGER_ROAR, 1f, 0.9f);
					fx(level, "gather", gate, m.position().add(0, 1, 0), new Vec3(14, 0, 0), (float) (1.6 * size), null);
				}
				if (s.t < 14) {
					if (t != null) m.getLookControl().setLookAt(t, 90, 90);
					yield false;
				}
				if (s.t == 14) s.dir = flat(t != null ? t.position().subtract(m.position()) : m.getLookAngle()).normalize();
				double speed = 0.55 + 0.12 * size;
				m.setDeltaMovement(s.dir.x * speed, m.getDeltaMovement().y, s.dir.z * speed);
				m.setYRot((float) (Mth.atan2(s.dir.z, s.dir.x) * Mth.RAD_TO_DEG) - 90f);
				m.yBodyRot = m.getYRot();
				if (s.t % 3 == 0) fx(level, "dash", gate, m.position(), s.dir, 0, null);
				for (LivingEntity v : victims(m, m.getBoundingBox().inflate(0.6), s))
					hit(m, v, atk * 1.4f, 1.6, gate, s);
				if (m.horizontalCollision && s.t > 16) {
					sound(m, SoundEvents.ANVIL_LAND, 0.8f, 0.6f);
					fx(level, "crash", gate, m.position().add(0, 1, 0), Vec3.ZERO, 0, null);
					yield true;
				}
				yield s.t > 14 + 22;
			}
			case "spin" -> {
				if (s.t == 0) anim(m, Animations.BIPED_MOB_SWORD_DUAL3);
				m.yBodyRot += 40;
				if (s.t % 6 == 3) {
					double r = MobMoves.reach(k) * 1.15;
					sound(m, SoundEvents.PLAYER_ATTACK_SWEEP, 1f, 0.7f);
					fx(level, "spin", gate, m.position(), new Vec3(Math.cos(s.t), 0, Math.sin(s.t)), (float) r, null);
					s.struck.clear();
					for (LivingEntity v : victims(m, m.getBoundingBox().inflate(r, 0.5, r), s))
						if (v.distanceToSqr(m) < r * r) hit(m, v, atk * 0.75f, 0.6, gate, s);
				}
				yield s.t > 24;
			}
			case "quake" -> {
				if (s.t == 0) anim(m, k.spider() ? Animations.SPIDER_ATTACK : Animations.BIPED_MOB_GREATSWORD);
				if (s.t == 10) s.dir = flat(t != null ? t.position().subtract(m.position()) : m.getLookAngle()).normalize();
				if (s.t >= 10 && (s.t - 10) % 3 == 0) {
					int n = (s.t - 10) / 3;
					Vec3 p = m.position().add(s.dir.scale(1.5 + n * 1.7));
					fx(level, "quake", gate, p, Vec3.ZERO, 0, null);
					sound(level, p, SoundEvents.GENERIC_EXPLODE.value(), 0.5f, 0.7f);
					s.struck.clear();
					for (LivingEntity v : victims(m, new AABB(p, p).inflate(1.6, 1.5, 1.6), s)) {
						hit(m, v, atk * 1.1f, 0.3, gate, s);
						v.push(0, 0.6, 0);
					}
				}
				yield s.t > 10 + 3 * 8;
			}
			case "roar" -> {
				if (s.t == 0) sound(m, k.boss() ? SoundEvents.WARDEN_ROAR : SoundEvents.RAVAGER_ROAR, 1.2f, 0.8f);
				if (s.t == 10) {
					fx(level, "roar", gate, m.getEyePosition(), Vec3.ZERO, 0, null);
					for (Player p : level.getEntitiesOfClass(Player.class, m.getBoundingBox().inflate(9), p -> p.isAlive() && !p.isSpectator())) {
						p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 1));
						p.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 80, 0));
						knock(m, p, 0.8);
					}
				}
				yield s.t > 26;
			}
			case "pull" -> {
				if (s.t == 0) anim(m, Animations.BIPED_MOB_THROW);
				if (s.t == 8 && t != null) {
					Vec3 from = m.position().add(0, m.getBbHeight() * 0.6, 0), to = t.position().add(0, t.getBbHeight() * 0.5, 0);
					fx(level, "pull", gate, from, to.subtract(from).normalize(), (float) from.distanceTo(to), null);
					Vec3 d = from.subtract(to);
					t.setDeltaMovement(d.x * 0.22, 0.35 + d.y * 0.1, d.z * 0.22);
					t.hurtMarked = true;
					hit(m, t, atk * 0.5f, 0, gate, s);
					sound(m, SoundEvents.CHAIN_PLACE, 1f, 0.6f);
				}
				yield s.t > 14;
			}
			case "blink" -> {
				if (s.t == 0) {
					fx(level, "blink", gate, m.position().add(0, 1, 0), Vec3.ZERO, 0, null);
					sound(m, SoundEvents.ENDERMAN_TELEPORT, 1f, 0.8f);
				}
				if (s.t == 6 && t != null) {
					Vec3 back = flat(t.getLookAngle()).normalize().scale(-(1.5 + k.w()));
					Vec3 to = t.position().add(back);
					if (level.noCollision(m, m.getBoundingBox().move(to.subtract(m.position())))) m.teleportTo(to.x, to.y, to.z);
					m.lookAt(t, 180, 180);
					fx(level, "blink", gate, m.position().add(0, 1, 0), Vec3.ZERO, 0, null);
				}
				if (s.t == 8) anim(m, MobMoves.opener(k));
				yield s.t > 9;
			}
			case "dash" -> {
				anim(m, MobMoves.dash(k));
				yield true;
			}
			case "pounce" -> {
				if (s.t == 0) {
					if (k.spider()) anim(m, Animations.SPIDER_JUMP_ATTACK);
					sound(m, SoundEvents.HOGLIN_ATTACK, 1f, 1.3f);
				}
				if (s.t == 4) {
					Vec3 to = t != null ? t.position() : m.position().add(m.getLookAngle().scale(4));
					Vec3 d = to.subtract(m.position());
					m.setDeltaMovement(d.x / 9, 0.42 + Math.min(0.3, d.y * 0.1), d.z / 9);
					m.hasImpulse = true;
					fx(level, "launch", gate, m.position(), Vec3.ZERO, 1.4f, null);
				}
				if (s.t > 4) {
					for (LivingEntity v : victims(m, m.getBoundingBox().inflate(0.5), s)) hit(m, v, atk * 1.2f, 0.7, gate, s);
					if (s.t > 8 && m.onGround()) yield true;
				}
				yield s.t > 30;
			}
			case "burrow" -> {
				if (s.t < 16) {
					if (s.t % 4 == 0) fx(level, "quake", gate, m.position(), Vec3.ZERO, 0, null);
					if (s.t == 0) sound(m, SoundEvents.ROOTED_DIRT_BREAK, 1.2f, 0.6f);
					if (s.t == 12) {
						m.setInvisible(true);
						s.invulnerable = Math.max(s.invulnerable, 30);
					}
					yield false;
				}
				if (s.t < 34) {
					if (t != null) {
						s.at = t.position();
						if (s.t % 6 == 4) fx(level, "tell", gate, s.at, new Vec3(6, 0, 0), (float) (2.0 * size), null);
					}
					yield false;
				}
				m.teleportTo(s.at.x, s.at.y, s.at.z);
				m.setInvisible(false);
				slam(m, level, s, s.at, 2.0 * size, atk * 1.4f, 0.4, gate);
				for (LivingEntity v : level.getEntitiesOfClass(Player.class, new AABB(s.at, s.at).inflate(2.2), p -> p.isAlive())) v.push(0, 0.8, 0);
				yield true;
			}
			case "bolt", "volley" -> {
				if (s.t == 0) anim(m, k.spider() ? Animations.SPIDER_ATTACK : Animations.BIPED_MOB_THROW);
				int shots = s.active.equals("bolt") ? 1 : k.boss() ? 5 : 3;
				for (int n = 0; n < shots; n++)
					if (s.t == 8 + n * 3 && t != null) {
						double spread = shots == 1 ? 0 : (n - (shots - 1) / 2.0) * 0.18;
						bolt(m, level, t, spread, atk * (shots == 1 ? 1.0f : 0.7f), gate);
					}
				yield s.t > 8 + shots * 3 + 2;
			}
			case "rain" -> {
				if (s.t == 0) {
					anim(m, k.spider() ? Animations.SPIDER_ATTACK : Animations.BIPED_MOB_THROW);
					sound(m, SoundEvents.EVOKER_PREPARE_ATTACK, 1f, 0.8f);
				}
				if (s.t == 6) {
					Vec3 c = t != null ? t.position() : m.position();
					int n = k.boss() ? 9 : 5;
					for (int i = 0; i < n; i++) {
						double a = m.getRandom().nextDouble() * Math.PI * 2, r = i == 0 ? 0 : 1.5 + m.getRandom().nextDouble() * (k.boss() ? 5 : 3);
						s.marks.add(c.add(Math.cos(a) * r, 0, Math.sin(a) * r));
						fx(level, "mark", gate, s.marks.get(i), new Vec3(24 + i * 2, 0, 0), 1.6f, null);
					}
				}
				if (s.t >= 30 && s.t < 30 + s.marks.size() * 2 && (s.t - 30) % 2 == 0) {
					Vec3 p = s.marks.get((s.t - 30) / 2);
					fx(level, "strike", gate, p, Vec3.ZERO, 0, null);
					sound(level, p, SoundEvents.GENERIC_EXPLODE.value(), 0.5f, 1.2f);
					s.struck.clear();
					for (LivingEntity v : victims(m, new AABB(p, p).inflate(1.6, 2, 1.6), s)) hit(m, v, atk * 0.9f, 0.3, gate, s);
				}
				yield s.t > 32 + s.marks.size() * 2;
			}
			case "lightning" -> {
				if (s.t == 0) anim(m, k.spider() ? Animations.SPIDER_ATTACK : Animations.BIPED_MOB_THROW);
				if (s.t == 4) {
					s.at = t != null ? t.position() : m.position();
					fx(level, "tell", gate, s.at, new Vec3(20, 0, 0), 2.5f, null);
				}
				if (s.t == 24) {
					LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(level);
					if (bolt != null) {
						bolt.moveTo(s.at);
						bolt.setVisualOnly(true);
						level.addFreshEntity(bolt);
					}
					fx(level, "thunder", gate, s.at, Vec3.ZERO, 0, null);
					for (LivingEntity v : victims(m, new AABB(s.at, s.at).inflate(2.5, 3, 2.5), s)) {
						hit(m, v, atk * 1.8f, 0.4, gate, s);
						v.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 2));
					}
				}
				yield s.t > 28;
			}
			case "cloud" -> {
				if (s.t == 0) anim(m, k.spider() ? Animations.SPIDER_ATTACK : Animations.BIPED_MOB_THROW);
				if (s.t == 8) {
					Vec3 c = t != null ? t.position() : m.position();
					s.hazards.add(new Hazard(c, k.boss() ? 4.5 : 3.0, level.getGameTime() + (k.boss() ? 160 : 120), atk * 0.3f));
					fx(level, "cloud", gate, c, new Vec3(k.boss() ? 160 : 120, 0, 0), k.boss() ? 4.5f : 3f, null);
					sound(level, c, SoundEvents.BREWING_STAND_BREW, 1f, 0.6f);
				}
				yield s.t > 12;
			}
			case "breath" -> {
				if (s.t == 0) sound(m, SoundEvents.BLAZE_SHOOT, 1.2f, 0.6f);
				if (t != null && s.t < 8) s.dir = t.getEyePosition().subtract(m.getEyePosition()).normalize();
				if (t != null) {
					Vec3 want = t.getEyePosition().subtract(m.getEyePosition()).normalize();
					s.dir = s.dir.lerp(want, 0.06).normalize();
					m.getLookControl().setLookAt(t, 20, 20);
				}
				if (s.t >= 6) {
					Vec3 eye = m.getEyePosition().add(flat(s.dir).normalize().scale(k.w() * 0.5));
					double len = 6 + 2 * size;
					if (s.t % 3 == 0) fx(level, "breath", gate, eye, s.dir, (float) len, null);
					if (s.t % 6 == 0) {
						s.struck.clear();
						for (Player p : level.getEntitiesOfClass(Player.class, m.getBoundingBox().inflate(len), p -> p.isAlive() && !p.isSpectator())) {
							Vec3 d = p.position().add(0, p.getBbHeight() * 0.5, 0).subtract(eye);
							if (d.length() < len && d.normalize().dot(s.dir) > 0.86) hit(m, p, atk * 0.45f, 0.1, gate, s);
						}
					}
				}
				yield s.t > 40;
			}
			case "beam" -> {
				if (s.t == 0) {
					anim(m, k.spider() ? Animations.SPIDER_ATTACK : Animations.BIPED_MOB_THROW);
					sound(m, SoundEvents.BEACON_ACTIVATE, 1.5f, 0.6f);
					s.at = t != null ? t.position().add(0, 1, 0) : m.position().add(m.getLookAngle().scale(8));
					fx(level, "gather", gate, m.getEyePosition(), new Vec3(20, 0, 0), 3, null);
				}
				Vec3 eye = m.getEyePosition();
				if (s.t < 20) yield false;
				if (t != null) s.at = s.at.lerp(t.position().add(0, 1, 0), 0.07);
				Vec3 d = s.at.subtract(eye).normalize();
				double len = 26;
				if (s.t % 3 == 2) fx(level, "beam", gate, eye, d, (float) len, null);
				if (s.t % 5 == 0) {
					s.struck.clear();
					for (Player p : level.getEntitiesOfClass(Player.class, m.getBoundingBox().inflate(len), p -> p.isAlive() && !p.isSpectator())) {
						Vec3 q = p.position().add(0, p.getBbHeight() * 0.5, 0).subtract(eye);
						double along = q.dot(d);
						if (along > 0 && along < len && q.subtract(d.scale(along)).length() < 1.1) hit(m, p, atk * 0.6f, 0.1, gate, s);
					}
				}
				yield s.t > 52;
			}
			case "summon" -> {
				if (s.t == 0) {
					anim(m, k.spider() ? Animations.SPIDER_ATTACK : Animations.BIPED_MOB_THROW);
					sound(m, SoundEvents.EVOKER_PREPARE_SUMMON, 1.2f, 0.7f);
				}
				if (s.t == 12) summon(m, level, s, k);
				yield s.t > 16;
			}
			case "heal" -> {
				if (s.t == 0) {
					anim(m, k.spider() ? Animations.SPIDER_ATTACK : Animations.BIPED_MOB_THROW);
					sound(m, SoundEvents.EVOKER_PREPARE_WOLOLO, 1f, 0.8f);
				}
				if (s.t == 0) fx(level, "gather", gate, m.position().add(0, 1, 0), new Vec3(12, 0, 0), 2, null);
				if (s.t < 12) yield false;
				if (s.t == 12) {
					m.heal(m.getMaxHealth() * (k.boss() ? 0.07f : 0.15f));
					fx(level, "heal", gate, m.position(), Vec3.ZERO, 0, m);
					for (Mob ally : level.getEntitiesOfClass(Mob.class, m.getBoundingBox().inflate(10), a -> a != m && a instanceof User && a.isAlive())) {
						ally.heal(ally.getMaxHealth() * 0.2f);
						fx(level, "healed", gate, ally.position(), Vec3.ZERO, 0, ally);
					}
				}
				yield s.t > 16;
			}
			default -> true;
		};
	}

	// ---------------------------------------------------------------- bosses: phases, ward, bars

	/** At two-thirds and one-third of its health a boss rises again: untouchable for a moment, a blast, harder after. */
	private static void phases(Mob m, ServerLevel level, State s, GateMobs.Kind k) {
		float hp = m.getHealth() / m.getMaxHealth();
		int want = hp <= 0.33f ? 3 : hp <= 0.66f ? 2 : 1;
		if (want <= s.phase || !m.isAlive()) return;
		s.phase = want;
		s.active = "phase";
		s.t = 0;
		s.invulnerable = 50;
		m.getNavigation().stop();
		anim(m, k.spider() ? Animations.SPIDER_ATTACK : Animations.BIPED_MOB_THROW);
		sound(m, SoundEvents.WITHER_SPAWN, 1.0f, want == 3 ? 0.6f : 0.8f);
		String gate = MobMoves.gate(k);
		fx(level, "phase", gate, m.position(), Vec3.ZERO, 0, m);
		for (Player p : level.getEntitiesOfClass(Player.class, m.getBoundingBox().inflate(10), Player::isAlive)) knock(m, p, 1.6);
		var speed = m.getAttribute(Attributes.MOVEMENT_SPEED);
		var dmg = m.getAttribute(Attributes.ATTACK_DAMAGE);
		ResourceLocation id = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "boss_phase");
		if (speed != null) {
			speed.removeModifier(id);
			speed.addTransientModifier(new AttributeModifier(id, 0.12 * (want - 1), AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
		}
		if (dmg != null) {
			dmg.removeModifier(id);
			dmg.addTransientModifier(new AttributeModifier(id, 0.18 * (want - 1), AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
		}
		if (s.bar != null) s.bar.setColor(want == 2 ? BossEvent.BossBarColor.PURPLE : BossEvent.BossBarColor.WHITE);
		Component name = m.getDisplayName();
		Component sub = Component.literal(want == 2 ? "rises again" : "unleashes everything").withStyle(want == 2 ? ChatFormatting.LIGHT_PURPLE : ChatFormatting.GOLD);
		for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, m.getBoundingBox().inflate(48), Player::isAlive)) {
			p.connection.send(new ClientboundSetTitlesAnimationPacket(5, 40, 15));
			p.connection.send(new ClientboundSetTitleTextPacket(name.copy().withStyle(ChatFormatting.DARK_RED)));
			p.connection.send(new ClientboundSetSubtitleTextPacket(sub));
		}
		// the minions it can call come at once
		for (MobMoves.Skill sk : MobMoves.of(k).skills())
			if (sk.name().equals("summon")) {
				s.skill = sk;
				summon(m, level, s, k);
				break;
			}
	}

	/** Damage the boss would take, after its ward and its phase change. */
	static boolean refuses(Mob m, @Nullable Entity by) {
		if (!(m instanceof User u)) return false;
		State s = u.state();
		if (s.invulnerable > 0) return true;
		if (s.warded) {
			if (by instanceof ServerPlayer p && m.level() instanceof ServerLevel level) {
				p.displayClientMessage(Component.literal(m.getDisplayName().getString() + " is warded - slay the dungeon's elite first").withStyle(ChatFormatting.GOLD), true);
				fx(level, "ward", MobMoves.gate(u.kind()), m.position(), Vec3.ZERO, Math.max(1.6f, m.getBbHeight() * 0.8f), null);
				sound(m, SoundEvents.SHIELD_BLOCK, 1f, 0.5f);
			}
			return true;
		}
		return false;
	}

	/** The elite fell: every warded boss in reach of it (its own dungeon's) can be hurt now. */
	static void unward(ServerLevel level, BlockPos near) {
		for (Mob m : level.getEntitiesOfClass(Mob.class, new AABB(near).inflate(400, 160, 400), e -> e instanceof User u && u.state().warded)) {
			((User) m).state().warded = false;
			for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new AABB(near).inflate(64), Player::isAlive))
				p.displayClientMessage(Component.literal("The ward on " + m.getDisplayName().getString() + " breaks").withStyle(ChatFormatting.GOLD), true);
		}
	}

	/** A boss's bar (red) or an elite's (yellow), shown to whoever is near it. */
	private static void bar(Mob m, ServerLevel level, State s, GateMobs.Kind k) {
		if (!k.boss() && !k.key()) return;
		if (s.bar == null) {
			Component title = k.boss() ? m.getDisplayName()
					: Component.literal("").append(m.getDisplayName()).append(Component.literal("  -  Elite, holds the key").withStyle(ChatFormatting.GOLD));
			s.bar = new ServerBossEvent(title, k.boss() ? (s.phase == 1 ? BossEvent.BossBarColor.RED : s.phase == 2 ? BossEvent.BossBarColor.PURPLE : BossEvent.BossBarColor.WHITE)
					: BossEvent.BossBarColor.YELLOW, k.boss() ? BossEvent.BossBarOverlay.NOTCHED_10 : BossEvent.BossBarOverlay.NOTCHED_6);
		}
		s.bar.setProgress(Mth.clamp(m.getHealth() / m.getMaxHealth(), 0, 1));
		if (m.tickCount % 10 != 0) return;
		double near = k.boss() ? 56 : 36;
		for (ServerPlayer p : level.players()) {
			boolean in = m.isAlive() && p.distanceToSqr(m) < near * near;
			if (in && !s.bar.getPlayers().contains(p)) s.bar.addPlayer(p);
			else if (!in && s.bar.getPlayers().contains(p)) s.bar.removePlayer(p);
		}
	}

	static void gone(Mob m) {
		if (m instanceof User u && u.state().bar != null) u.state().bar.removeAllPlayers();
	}

	// ---------------------------------------------------------------- the pieces skills are made of

	private static void hazards(Mob m, ServerLevel level, State s) {
		if (s.hazards.isEmpty()) return;
		long now = level.getGameTime();
		s.hazards.removeIf(h -> now > h.until());
		String gate = MobMoves.gate(((User) m).kind());
		for (Hazard h : s.hazards) {
			if (now % 15 == 0)
				for (Player p : level.getEntitiesOfClass(Player.class, new AABB(h.at(), h.at()).inflate(h.radius(), 2, h.radius()), Player::isAlive)) {
					p.hurt(m.damageSources().indirectMagic(m, m), h.damage());
					Spells.element(gate, p, 2);
				}
		}
	}

	private static void summon(Mob m, ServerLevel level, State s, GateMobs.Kind k) {
		if (s.skill == null || s.skill.arg().isEmpty()) return;
		EntityType<?> type = net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, s.skill.arg()));
		int n = Math.min((k.boss() ? 2 + s.phase : 2), (k.boss() ? 6 : 3) - alive(m, s));
		String gate = MobMoves.gate(k);
		for (int i = 0; i < n; i++) {
			double a = m.getRandom().nextDouble() * Math.PI * 2, r = 2 + k.w() * 0.5 + m.getRandom().nextDouble() * 2;
			Vec3 p = m.position().add(Math.cos(a) * r, 0, Math.sin(a) * r);
			if (!(type.create(level) instanceof Mob e)) continue;
			e.moveTo(p.x, p.y, p.z, m.getRandom().nextFloat() * 360f, 0);
			if (!level.noCollision(e)) e.moveTo(m.getX(), m.getY(), m.getZ(), e.getYRot(), 0);
			EventHooks.finalizeMobSpawn(e, level, level.getCurrentDifficultyAt(e.blockPosition()), MobSpawnType.MOB_SUMMONED, null);
			e.addTag("ashbound_dweller");
			e.setTarget(m.getTarget());
			level.addFreshEntity(e);
			s.minions.add(e.getUUID());
			fx(level, "summon", gate, p, Vec3.ZERO, 0, null);
		}
	}

	private static void bolt(Mob m, ServerLevel level, LivingEntity t, double spread, float damage, String gate) {
		MobBolt b = new MobBolt(MobBolt.TYPE.get(), level);
		b.setOwner(m);
		Vec3 from = m.getEyePosition().add(flat(m.getLookAngle()).normalize().scale(m.getBbWidth() * 0.6));
		Vec3 d = t.getEyePosition().subtract(0, 0.4, 0).subtract(from).normalize();
		d = d.yRot((float) spread);
		b.setPos(from.x, from.y, from.z);
		b.setDeltaMovement(d.scale(0.9));
		b.damage = damage;
		b.setGate(gate);
		level.addFreshEntity(b);
		sound(m, SoundEvents.BLAZE_SHOOT, 0.7f, 1.2f);
	}

	/** A blow on the ground at `at`: everyone near it hurt and thrown, dust and sparks. */
	private static void slam(Mob m, ServerLevel level, State s, Vec3 at, double r, float damage, double knock, String gate) {
		fx(level, "slam", gate, at, Vec3.ZERO, (float) r, null);
		sound(level, at, SoundEvents.GENERIC_EXPLODE.value(), 0.8f, 0.6f);
		sound(level, at, SoundEvents.ANVIL_LAND, 0.6f, 0.5f);
		s.struck.clear();
		for (LivingEntity v : victims(m, new AABB(at, at).inflate(r, 2.5, r), s))
			if (v.distanceToSqr(at) < (r + 0.6) * (r + 0.6)) hit(m, v, damage, knock, gate, s);
	}

	private static List<LivingEntity> victims(Mob m, AABB box, State s) {
		return m.level().getEntitiesOfClass(LivingEntity.class, box,
				v -> v != m && v.isAlive() && !(v instanceof User) && !s.struck.contains(v.getUUID()) && (v instanceof Player p ? !p.isSpectator() && !p.isCreative() : v == m.getTarget()));
	}

	private static void hit(Mob m, LivingEntity v, float damage, double knock, String gate, State s) {
		s.struck.add(v.getUUID());
		if (v.hurt(m.damageSources().mobAttack(m), damage)) {
			Spells.element(gate, v, 2);
			if (knock > 0) knock(m, v, knock);
		}
	}

	private static void knock(Entity from, LivingEntity v, double strength) {
		Vec3 d = flat(v.position().subtract(from.position()));
		if (d.lengthSqr() < 1e-4) d = new Vec3(0, 0, 1);
		d = d.normalize();
		v.push(d.x * strength, 0.25 + strength * 0.2, d.z * strength);
		v.hurtMarked = true;
	}

	static void anim(Mob m, AnimationAccessor<? extends StaticAnimation> a) {
		LivingEntityPatch<?> p = EpicFightCapabilities.getEntityPatch(m, LivingEntityPatch.class);
		if (p != null && a != null) p.playAnimationSynchronized(a, 0.0F);
	}

	private static void trail(ServerLevel level, Mob m, String gate) {
		if (m.tickCount % 2 == 0) fx(level, "trail", gate, m.position().add(0, m.getBbHeight() * 0.4, 0), Vec3.ZERO, 0, null);
	}

	/** What it looks like is on the client: SkillFx.monster, in the dungeon's colour. dir carries a tell's length in its x. */
	private static void fx(ServerLevel level, String what, String gate, Vec3 at, Vec3 dir, float r, @Nullable Entity on) {
		Spells.skillFx(level, "mob_" + what + ":" + gate, at, dir, r, on);
	}

	private static Vec3 flat(Vec3 v) {
		return new Vec3(v.x, 0, v.z);
	}

	private static void sound(Mob m, SoundEvent e, float vol, float pitch) {
		m.level().playSound(null, m.getX(), m.getY(), m.getZ(), e, SoundSource.HOSTILE, vol, pitch);
	}

	private static void sound(ServerLevel level, Vec3 at, SoundEvent e, float vol, float pitch) {
		level.playSound(null, at.x, at.y, at.z, e, SoundSource.HOSTILE, vol, pitch);
	}

	/** how much bigger than a player it's drawn */
	static double size(GateMobs.Kind k) {
		return Math.max(1.0, k.h() / 2.2);
	}

	/** Holds its legs still (over the chase) while a skill runs. */
	static final class SkillGoal extends Goal {
		private final Mob mob;

		SkillGoal(Mob mob) {
			this.mob = mob;
			setFlags(java.util.EnumSet.of(Goal.Flag.MOVE, Goal.Flag.JUMP));
		}

		@Override
		public boolean canUse() {
			return busy(mob);
		}

		@Override
		public boolean requiresUpdateEveryTick() {
			return true;
		}
	}
}
