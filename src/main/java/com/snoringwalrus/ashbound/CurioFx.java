package com.snoringwalrus.ashbound;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.RandomizableContainerBlockEntity;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.common.Tags;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.living.LivingEntityUseItemEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.living.MobEffectEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.level.BlockDropsEvent;
import net.neoforged.neoforge.event.level.BlockEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import top.theillusivec4.curios.api.CuriosApi;
import yesman.epicfight.api.event.EpicFightEventHooks;
import yesman.epicfight.api.utils.AttackResult;
import yesman.epicfight.skill.Skill;
import yesman.epicfight.skill.SkillCategories;
import yesman.epicfight.world.capabilities.EpicFightCapabilities;
import yesman.epicfight.world.capabilities.entitypatch.player.ServerPlayerPatch;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * What the epic and legendary curios do and the relics' powers (docs/RELICS.md). A relic's power has three tiers
 * (custom data "relic_tier", upgraded at the Gate Forge); the [V] powers are cast with the curio key, sneak+V uses the
 * Rift Key. What a player wears is read every half second into {@link #WORN}.
 */
public final class CurioFx {
	private CurioFx() {}

	static final String TIER = "relic_tier";

	/** per player: what they wear (id -> relic tier, 1 for a curio), refreshed every 10 ticks */
	private static final Map<UUID, Map<String, Integer>> WORN = new HashMap<>();

	private static final class S {
		int casts, hits, souls, brand, chitin;
		boolean empowered, mantis;
		long rime, oath, vigil, spore, hourglass, coal, coalUntil, wick, noose, acorn, horn, rift, pick, spindle, lodestone, gorget;
		float dodgeCost;
		Vec3 mark;
		ResourceKey<Level> markDim;
	}

	private static final Map<UUID, S> STATE = new HashMap<>();
	/** allies hitting harder for a while (the Censer's +20%, the Warhorn's): id -> (until, multiplier) */
	private static final Map<UUID, double[]> EMPOWER = new HashMap<>();
	/** the Hourglass: frozen players waking at (game time, health fraction) */
	private static final Map<UUID, double[]> THAW = new HashMap<>();
	/** the Wick's ward: perSecond is a share of each one's max health */
	private record Ward(ServerLevel level, Vec3 at, long until, float perSecond) {}
	private record Web(ServerLevel level, Vec3 at, long until, int stun, UUID owner) {}
	private record Sense(UUID player, List<BlockPos> ores, long until) {}
	private record Horn(UUID player, long until) {}
	/** the Blight Vial's rot on whoever its wearer hits: our own, so a quick string of hits doesn't keep resetting it
	 *  before it bites (vanilla poison only ticks every 25) and the undead, immune to poison, rot too */
	private record Blight(LivingEntity victim, UUID owner, long until, float perSecond) {}
	private static final Map<UUID, Blight> BLIGHTS = new HashMap<>();
	private static final List<Ward> WARDS = new ArrayList<>();
	private static final List<Web> WEBS = new ArrayList<>();
	private static final List<Sense> SENSES = new ArrayList<>();
	private static final List<Horn> HORNS = new ArrayList<>();
	private static final List<Object[]> SHORTEN = new ArrayList<>();
	private static final ResourceLocation HORN_KB = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "warhorn");

	private static S state(Player p) {
		return STATE.computeIfAbsent(p.getUUID(), k -> new S());
	}

	// ---------------------------------------------------------------- what is worn

	public static int tier(ItemStack s) {
		int t = s.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag().getInt(TIER);
		return Math.max(1, Math.min(3, t));
	}

	private static Map<String, Integer> read(Player p) {
		Map<String, Integer> m = new HashMap<>();
		CuriosApi.getCuriosInventory(p).ifPresent(inv -> inv.findCurios(st -> st.getItem() instanceof Curios.Curio).forEach(r -> {
			Curios.Curio c = (Curios.Curio) r.stack().getItem();
			m.put(c.spec.id(), c.spec.slot().equals("relic") ? tier(r.stack()) : 1);
		}));
		return m;
	}

	/** 0 if not worn, else 1 (a curio) or the relic's tier */
	static int w(Player p, String id) {
		Map<String, Integer> m = WORN.get(p.getUUID());
		if (m == null) WORN.put(p.getUUID(), m = read(p));
		return m.getOrDefault(id, 0);
	}

	private static ServerPlayerPatch patch(ServerPlayer p) {
		return EpicFightCapabilities.getEntityPatch(p, ServerPlayerPatch.class);
	}

	private static void stamina(ServerPlayer p, float add) {
		ServerPlayerPatch pp = patch(p);
		if (pp != null) pp.setStamina(Math.min(pp.getMaxStamina(), pp.getStamina() + add));
	}

	/** the gear ladder at the player's level band (Gear.scale, rank C = 1): flat curio numbers grow with it */
	static float power(ServerPlayer p) {
		int l = Levels.level(p);
		char r = l < 10 ? 'F' : l < 20 ? 'E' : l < 30 ? 'D' : l < 45 ? 'C' : l < 60 ? 'B' : l < 75 ? 'A' : 'S';
		return (float) (Gear.scale(r) / Gear.scale('C'));
	}

	static boolean isBoss(LivingEntity e) {
		if (e.getType().is(Tags.EntityTypes.BOSSES)) return true;
		ResourceLocation id = BuiltInRegistries.ENTITY_TYPE.getKey(e.getType());
		Balance.Mult m = id.getNamespace().equals(Ashbound.ID) ? Balance.solved(id.getPath()) : null;
		return m != null && "boss".equals(m.role());
	}

	private static boolean elite(LivingEntity e) {
		ResourceLocation id = BuiltInRegistries.ENTITY_TYPE.getKey(e.getType());
		Balance.Mult m = id.getNamespace().equals(Ashbound.ID) ? Balance.solved(id.getPath()) : null;
		return m != null && ("elite".equals(m.role()) || "boss".equals(m.role()));
	}

	private static boolean foe(Entity e, Player p) {
		return e instanceof LivingEntity l && l != p && l.isAlive() && e instanceof Enemy && !Spells.isThrall(e);
	}

	private static void stun(LivingEntity e, int ticks) {
		e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, ticks, 6));
		e.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, ticks, 4));
	}

	private static void puff(LivingEntity e, ParticleOptions o, int n) {
		if (e.level() instanceof ServerLevel sl) sl.sendParticles(o, e.getX(), e.getY() + e.getBbHeight() * 0.6, e.getZ(), n, 0.4, 0.5, 0.4, 0.02);
	}

	private static void say(ServerPlayer p, String text, ChatFormatting c) {
		p.displayClientMessage(Component.literal(text).withStyle(c), true);
	}

	// ---------------------------------------------------------------- setup

	static void register() {
		NeoForge.EVENT_BUS.addListener(CurioFx::hurt);
		NeoForge.EVENT_BUS.addListener((net.neoforged.neoforge.event.RegisterCommandsEvent e) -> e.getDispatcher().register(
				net.minecraft.commands.Commands.literal("ashbound").requires(c -> c.hasPermission(2))
						.then(net.minecraft.commands.Commands.literal("vfx").then(net.minecraft.commands.Commands
								.argument("name", com.mojang.brigadier.arguments.StringArgumentType.word())
								.suggests((c, b) -> net.minecraft.commands.SharedSuggestionProvider.suggest(LOOKS, b))
								.executes(c -> preview(c.getSource().getPlayerOrException(),
										com.mojang.brigadier.arguments.StringArgumentType.getString(c, "name")))))));
		NeoForge.EVENT_BUS.addListener(CurioFx::died);
		NeoForge.EVENT_BUS.addListener(CurioFx::tick);
		NeoForge.EVENT_BUS.addListener(CurioFx::serverTick);
		NeoForge.EVENT_BUS.addListener(CurioFx::potion);
		NeoForge.EVENT_BUS.addListener(CurioFx::drops);
		NeoForge.EVENT_BUS.addListener(CurioFx::broke);
		NeoForge.EVENT_BUS.addListener(CurioFx::effectAdded);
		NeoForge.EVENT_BUS.addListener((MobEffectEvent.Applicable e) -> {
			if (e.getEntity() instanceof ServerPlayer p && e.getEffectInstance().is(MobEffects.POISON) && w(p, "blight_vial") > 0)
				e.setResult(MobEffectEvent.Applicable.Result.DO_NOT_APPLY);
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedOutEvent e) -> {
			WORN.remove(e.getEntity().getUUID());
			STATE.remove(e.getEntity().getUUID());
		});
		// a roll: cheaper with the Torc / Void Marble; the Pearl blinks, the Spindle leaves a web
		EpicFightEventHooks.Player.CONSUME_SKILL.registerEvent(e -> {
			if (!(e.getEntityPatch().getOriginal() instanceof ServerPlayer p) || e.getSkill().getCategory() != SkillCategories.DODGE) return;
			if (e.getResourceType() == Skill.Resource.STAMINA) {
				float cut = (w(p, "gryphon_torc") > 0 ? 0.25f : 0) + (float) (Passives.stat(p, "dodge_cost%") / 100);
				if (cut > 0) e.setAmount(e.getAmount() * Math.max(0.2f, 1 - cut));
				state(p).dodgeCost = e.getAmount();
			}
			rolled(p);
		});
		// a dodge that slipped a real attack: the Mantis Molt
		EpicFightEventHooks.Entity.ON_DODGE.registerEvent(e -> {
			if (!(e.getEntityPatch().getOriginal() instanceof ServerPlayer p)) return;
			int t = w(p, "mantis_molt");
			if (t == 0) return;
			S s = state(p);
			stamina(p, Math.max(1, s.dodgeCost) * (0.25f + 0.25f * t));
			s.mantis = true;
			Vfx.around(p, Vfx.mote(0x9CE05A, 0.035f, 10, 0), 14, 0.22);
			Vfx.rise(p, Vfx.wisp(0x6FB040, 0.35f, 18, -0.002f, true), 4);
		});
		// a blocked hit: the Oathring taunts and shields, the Rose throws some of it back
		EpicFightEventHooks.Entity.TAKE_DAMAGE_INCOME.registerEvent(e -> {
			if (!(e.getEntityPatch().getOriginal() instanceof ServerPlayer p)) return;
			if (e.getResult() != AttackResult.ResultType.BLOCKED && !e.isParried()) return;
			long now = p.level().getGameTime();
			S s = state(p);
			Entity by = e.getDamageSource().getEntity();
			if (w(p, "wardens_oathring") > 0 && now >= s.oath) {
				s.oath = now + 160;
				for (Mob m : p.level().getEntitiesOfClass(Mob.class, p.getBoundingBox().inflate(8), m -> foe(m, p))) Threat.taunt(m, p);
				p.addEffect(new MobEffectInstance(MobEffects.ABSORPTION, 200, 0));
				p.level().playSound(null, p.blockPosition(), SoundEvents.RAVAGER_ROAR, SoundSource.PLAYERS, 0.5f, 1.6f);
			}
			int rose = w(p, "thornborn_rose");
			if (rose > 0 && by instanceof LivingEntity att && att != p && p.distanceTo(att) < 6)
				att.hurt(p.damageSources().thorns(p), e.getDamage() * (0.05f + 0.05f * rose));
		}, -900);
	}

	// ---------------------------------------------------------------- hits

	private static void hurt(LivingIncomingDamageEvent e) {
		LivingEntity victim = e.getEntity();
		if (victim.level().isClientSide) return;
		long now = victim.level().getGameTime();
		Entity src = e.getSource().getEntity(), direct = e.getSource().getDirectEntity();
		float amount = e.getAmount();
		if (src instanceof ServerPlayer p) {
			if (w(p, "ring_of_the_drowned_god") > 0 && p.isInWaterOrRain()) amount *= 1.15f;
			if (elite(victim)) amount *= (float) (1 + Passives.stat(p, "elite_dmg%") / 100);
			if (direct instanceof Spells.Bolt && w(p, "augurs_ember") > 0) victim.igniteForSeconds(2);
		}
		// whoever an ally empowered
		if (src != null) {
			double[] em = EMPOWER.get(src.getUUID());
			if (em != null && em[0] > now) amount *= (float) em[1];
		}
		// a player's own melee hit
		if (src instanceof ServerPlayer p && direct == p) {
			S s = state(p);
			s.hits++;
			if (w(p, "chitin_loop") > 0 && ++s.chitin % 5 == 0) stamina(p, 1.5f);
			if (w(p, "blight_vial") > 0) {
				Blight old = BLIGHTS.get(victim.getUUID());
				float per = Math.max(1, amount * 0.25f / 3);
				BLIGHTS.put(victim.getUUID(), new Blight(victim, p.getUUID(), now + 60, old != null && old.until() > now ? Math.max(per, old.perSecond()) : per));
			}
			if (s.coalUntil > now) {
				victim.igniteForSeconds(3);
				amount *= 1.10f + 0.05f * w(p, "kiln_fathers_coal");
			}
			if (s.mantis) {
				s.mantis = false;
				amount *= 1.2f;
				if (!isBoss(victim)) stun(victim, 20);
			}
			int brand = w(p, "legions_brand");
			if (brand > 0 && ++s.brand % 3 == 0) {
				amount *= 1.15f + 0.15f * brand;
				brandLook(victim);
			}
			int rose = w(p, "thornborn_rose");
			if (rose > 0) p.heal(amount * (0.02f + 0.01f * rose));
			int stone = w(p, "stormspire_lodestone");
			if (stone > 0 && now - s.lodestone >= 240 - 40L * stone) {
				s.lodestone = now;
				lightning(p, victim, amount * 0.4f, 1 + stone);
			}
		}
		// arrows
		if (direct instanceof AbstractArrow a && src instanceof ServerPlayer p && a.isCritArrow() && w(p, "marksmans_gyre") > 0) {
			LivingEntity next = null;
			for (LivingEntity m : victim.level().getEntitiesOfClass(LivingEntity.class, victim.getBoundingBox().inflate(4), m -> m != victim && foe(m, p)))
				if (next == null || m.distanceToSqr(victim) < next.distanceToSqr(victim)) next = m;
			if (next != null) {
				next.hurt(p.damageSources().arrow(a, p), amount * 0.7f);
				if (next.level() instanceof ServerLevel sl) {
					Vfx.arc(sl, Vfx.chest(victim), Vfx.chest(next), Vfx.mote(0xFFE6A0, 0.03f, 8, 0), 10, 0.15);
					Vfx.burst(sl, Vfx.chest(next), Vfx.mote(0xFFD070, 0.035f, 8, 0.03f), 8, 0.25);
				}
			}
		}
		// a player taking it
		if (victim instanceof ServerPlayer p) {
			S s = state(p);
			if (src instanceof LivingEntity att && att.isInvertedHealAndHarm() && w(p, "reliquary_finger_bone") > 0) amount *= 0.9f;
			if (src instanceof LivingEntity att && !(att instanceof Player) && direct == att) {
				if (w(p, "rime_band") > 0 && now >= s.rime) {
					s.rime = now + 200;
					att.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 20, 1));
					frost(att, 10);
				}
				int spore = w(p, "spore_heart");
				if (spore > 0 && now >= s.spore) {
					s.spore = now + 120 - 20L * spore;
					AreaEffectCloud c = new AreaEffectCloud(p.level(), p.getX(), p.getY(), p.getZ());
					c.setOwner(p);
					c.setRadius(spore == 3 ? 3.5f : 2.5f);
					c.setRadiusPerTick(0);
					c.setDuration(60);
					c.setParticle(Vfx.wisp(0x8E6BB8, 0.5f, 30, -0.003f, false));
					p.level().addFreshEntity(c);
					float per = Math.max(1, amount * (0.2f + 0.1f * spore) / 3);
					for (LivingEntity m : p.level().getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(c.getRadius()), m -> foe(m, p)))
						BLIGHTS.put(m.getUUID(), new Blight(m, p.getUUID(), now + 60, per));
				}
			}
			if (THAW.containsKey(p.getUUID())) amount = 0;   // frozen in the Hourglass's ice
			int glass = w(p, "rime_hourglass");
			if (amount >= p.getHealth() && glass > 0 && now >= s.hourglass) {
				s.hourglass = now + 14400 - 2400L * glass;
				cd(p, 14400 - 2400 * glass);
				amount = 0;
				p.setHealth(1);
				p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 50, 4));
				stun(p, 40);
				p.setTicksFrozen(200);
				THAW.put(p.getUUID(), new double[] {now + 40, 0.2 + 0.1 * glass});
				frost(p, 30);
				Vfx.groundRing(p.serverLevel(), p.position().add(0, 0.05, 0), 0.5, Vfx.band(0xBFE4F8, 0.12f, 40, 0.008f));
				p.level().playSound(null, p.blockPosition(), SoundEvents.GLASS_BREAK, SoundSource.PLAYERS, 1f, 0.6f);
				say(p, "The Rime Hourglass turns", ChatFormatting.AQUA);
			}
			if (w(p, "last_vigil_reliquary") > 0 && now >= s.vigil && amount > 0 && p.getHealth() - amount < p.getMaxHealth() * 0.3f) {
				s.vigil = now + 2400;
				p.addEffect(new MobEffectInstance(MobEffects.ABSORPTION, 200, 2));
				holy(p, 18);
				p.level().playSound(null, p.blockPosition(), SoundEvents.BEACON_ACTIVATE, SoundSource.PLAYERS, 0.8f, 1.4f);
			}
		}
		if (amount != e.getAmount()) e.setAmount(amount);
	}

	/** magic from a player that isn't a blow of theirs (no direct entity), so it doesn't set off the on-hit curios again */
	static DamageSource unhit(Player p) {
		return new DamageSource(p.level().registryAccess().registryOrThrow(Registries.DAMAGE_TYPE).getHolderOrThrow(DamageTypes.INDIRECT_MAGIC), null, p);
	}

	/** whether the Blight Vial's rot is on this one */
	static boolean blighted(LivingEntity e) {
		Blight b = BLIGHTS.get(e.getUUID());
		return b != null && b.until() > e.level().getGameTime();
	}

	// ---------------------------------------------------------------- looks shared by several effects (Vfx)

	private static ServerLevel sl(Entity e) {
		return (ServerLevel) e.level();
	}

	/** frost: ice glints flying off, cold breath round the body */
	private static void frost(LivingEntity e, int n) {
		if (!(e.level() instanceof ServerLevel l)) return;
		Vfx.burst(l, Vfx.chest(e), Vfx.mote(0xCFF0FF, 0.03f, 12, 0.03f), n, 0.25);
		Vfx.ring(l, e.position().add(0, 0.2, 0), e.getBbWidth() * 0.6, Vfx.wisp(0xBFE4F8, 0.5f, 30, 0, false), 8, 0.03);
		Vfx.groundRing(l, e.position().add(0, 0.04, 0), e.getBbWidth() * 0.7, Vfx.band(0xBFE4F8, 0.1f, 30, 0.01f));
	}

	/** holy light: gold motes rising, a pale glow round the body */
	private static void holy(LivingEntity e, int n) {
		Vfx.rise(e, Vfx.mote(0xFFE7A0, 0.03f, 20, -0.03f), n);
		Vfx.around(e, Vfx.wisp(0xF6E6B0, 0.45f, 24, -0.004f, true), n / 4, 0.02);
		if (e.level() instanceof ServerLevel l) Vfx.groundRing(l, e.position().add(0, 0.04, 0), 0.5, Vfx.band(0xF2B04A, 0.04f, 24, 0.02f));
	}

	/** the void: violet light rushing in (leaving) or bursting out (arriving) */
	private static void void_(ServerPlayer p, boolean leaving) {
		Vec3 c = Vfx.chest(p);
		if (leaving) {
			Vfx.implode(p.serverLevel(), c, 1.6, Vfx.mote(0xB070FF, 0.035f, 10, 0), 30);
			Vfx.implode(p.serverLevel(), c, 1.2, Vfx.wisp(0x5A2A9A, 0.5f, 12, 0, true), 8);
		} else {
			Vfx.burst(p.serverLevel(), c, Vfx.mote(0xC890FF, 0.035f, 12, 0), 26, 0.35);
			Vfx.around(p, Vfx.wisp(0x6A34B0, 0.5f, 22, -0.004f, true), 6, 0.05);
			Vfx.groundRing(p.serverLevel(), p.position().add(0, 0.04, 0), 0.3, Vfx.band(0xB070FF, 0.05f, 16, 0.03f));
		}
	}

	/** Legion's Brand: teal fire out of the wound, the brand's sigil flaring round the foe */
	private static void brandLook(LivingEntity v) {
		if (!(v.level() instanceof ServerLevel sl)) return;
		Vfx.burst(sl, Vfx.chest(v), Vfx.mote(0x38E0C8, 0.045f, 12, 0.02f), 24, 0.36);
		Vfx.burst(sl, Vfx.chest(v), Vfx.wisp(0x1FA898, 0.35f, 14, -0.006f, true), 5, 0.03);
		Vec3 waist = v.position().add(0, v.getBbHeight() * 0.3, 0);
		double r = v.getBbWidth() * 1.2 + 0.2;
		Vfx.groundRing(sl, waist, r, Vfx.band(0x38E0C8, 0.05f, 14, 0.01f));
		Vfx.groundRing(sl, waist.add(0, 0.05, 0), r + 0.15, Vfx.band(0xC8FFF6, 0.025f, 12, 0.015f));
	}

	/** the Kiln-Father's Coal flares: a ring of fire running out from the feet, sparks thrown up */
	private static void coalLook(ServerPlayer p) {
		Vfx.groundRing(p.serverLevel(), p.position().add(0, 0.04, 0), 0.4, Vfx.band(0xFFC070, 0.06f, 22, 0.04f));
		Vfx.ring(p.serverLevel(), p.position().add(0, 0.15, 0), 0.4, Vfx.wisp(0xE8742C, 0.4f, 20, -0.006f, true), 22, 0.16);
		Vfx.burst(p.serverLevel(), Vfx.chest(p), Vfx.mote(0xFFB050, 0.035f, 16, -0.01f), 20, 0.3);
	}

	/** the Pale Abbot's Wick: the ward's gold circle (its flames go round it while it lasts) */
	private static void wardLook(ServerPlayer p) {
		holy(p, 14);
		Vfx.groundRing(p.serverLevel(), p.position().add(0, 0.04, 0), 6, Vfx.band(0xF2B04A, 0.06f, 100, 0));
		Vfx.groundRing(p.serverLevel(), p.position().add(0, 0.05, 0), 5.8, Vfx.band(0xFFE7A0, 0.025f, 100, 0));
	}

	/** the Rotwood Acorn: roots burst up; rings of green-gold light run out, seed-sparks thrown up */
	private static void acornLook(ServerLevel l, Vec3 at) {
		Vfx.groundRing(l, at.add(0, 0.05, 0), 0.4, Vfx.band(0x7FC23A, 0.08f, 26, 0.12f));
		Vfx.groundRing(l, at.add(0, 0.06, 0), 0.2, Vfx.band(0xC8E86A, 0.04f, 22, 0.08f));
		Vfx.ring(l, at.add(0, 0.15, 0), 0.6, Vfx.wisp(0x2A3A18, 0.8f, 34, 0, false), 10, 0.1);
		Vfx.burst(l, at.add(0, 0.3, 0), Vfx.mote(0xC8E86A, 0.04f, 18, 0.04f), 24, 0.35);
	}

	/** the Warhorn: the call rolls out in two rings of warm light and a wall of dust */
	private static void hornLook(ServerPlayer p) {
		Vfx.groundRing(p.serverLevel(), p.position().add(0, 0.1, 0), 0.6, Vfx.band(0xF08A30, 0.1f, 24, 0.25f));
		Vfx.groundRing(p.serverLevel(), p.position().add(0, 0.08, 0), 0.4, Vfx.band(0xFFD090, 0.05f, 30, 0.3f));
		Vfx.ring(p.serverLevel(), p.position().add(0, 0.2, 0), 0.6, Vfx.wisp(0x8A7660, 0.7f, 30, 0, false), 24, 0.3);
	}

	/** an ally the Warhorn kindled */
	private static void kindled(LivingEntity q) {
		Vfx.rise(q, Vfx.wisp(0xF08A30, 0.4f, 22, -0.008f, true), 5);
		Vfx.around(q, Vfx.mote(0xFFB050, 0.03f, 12, -0.02f), 8, 0.1);
	}

	/** the Gryphon Plume's jump: a ring of wind-dust under the feet */
	private static void plumeLook(ServerPlayer p) {
		Vfx.ring(p.serverLevel(), p.position(), 0.4, Vfx.wisp(0xF2EEE6, 0.4f, 16, 0.002f, false), 12, 0.12);
		Vfx.groundRing(p.serverLevel(), p.position(), 0.3, Vfx.band(0xFFF6D8, 0.03f, 12, 0.04f));
		Vfx.burst(p.serverLevel(), p.position(), Vfx.mote(0xFFF6D8, 0.025f, 10, 0.03f), 6, 0.15);
	}

	static final List<String> LOOKS = List.of("blight", "brand", "lightning", "frost", "void", "coal", "warhorn", "acorn", "holy", "plume");

	/** /ashbound vfx NAME: an effect's look played on what the player is looking at (else on them), nothing else of it */
	static int preview(ServerPlayer p, String name) {
		ServerLevel l = p.serverLevel();
		LivingEntity t = null;
		for (LivingEntity m : l.getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(12), m -> m != p && m.isAlive()))
			if (p.hasLineOfSight(m) && p.getLookAngle().dot(m.position().subtract(p.position()).normalize()) > 0.9
					&& (t == null || m.distanceToSqr(p) < t.distanceToSqr(p))) t = m;
		LivingEntity on = t != null ? t : p;
		switch (name) {
			case "blight" -> BLIGHTS.put(on.getUUID(), new Blight(on, p.getUUID(), l.getGameTime() + 60, 0));
			case "brand" -> brandLook(on);
			case "lightning" -> lightning(p, on, 0, 2);
			case "frost" -> frost(on, 24);
			case "void" -> {
				void_(p, true);
				void_(p, false);
			}
			case "coal" -> {
				coalLook(p);
				state(p).coalUntil = l.getGameTime() + 80;
			}
			case "warhorn" -> {
				hornLook(p);
				if (on != p) kindled(on);
			}
			case "acorn" -> acornLook(l, on.position());
			case "holy" -> wardLook(p);
			case "plume" -> plumeLook(p);
			default -> {
				return 0;
			}
		}
		return 1;
	}

	/** the Lodestone: lightning on the target and jumping to n more */
	private static void lightning(ServerPlayer p, LivingEntity at, float dmg, int n) {
		ServerLevel sl = p.serverLevel();
		LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(sl);
		if (bolt != null) {
			bolt.moveTo(at.position());
			bolt.setVisualOnly(true);
			sl.addFreshEntity(bolt);
		}
		Vfx.groundRing(sl, at.position().add(0, 0.05, 0), 0.5, Vfx.band(0x7FC8FF, 0.06f, 14, 0.025f));
		Vfx.burst(sl, Vfx.chest(at), Vfx.mote(0xCFF2FF, 0.03f, 8, 0.02f), 14, 0.35);
		LivingEntity from = at;
		List<LivingEntity> hit = new ArrayList<>(List.of(at));
		for (int k = 0; k < n; k++) {
			LivingEntity best = null;
			for (LivingEntity m : sl.getEntitiesOfClass(LivingEntity.class, from.getBoundingBox().inflate(5), m -> foe(m, p) && !hit.contains(m)))
				if (best == null || m.distanceToSqr(from) < best.distanceToSqr(from)) best = m;
			if (best == null) break;
			Vec3 a = from.position().add(0, from.getBbHeight() / 2, 0), b = best.position().add(0, best.getBbHeight() / 2, 0);
			Vfx.bolt(sl, a, b, 0x7FC8FF, 0.035f, 6);
			Vfx.burst(sl, b, Vfx.mote(0xCFF2FF, 0.03f, 8, 0.02f), 12, 0.3);
			Vfx.groundRing(sl, best.position().add(0, 0.05, 0), 0.4, Vfx.band(0x7FC8FF, 0.05f, 12, 0.02f));
			best.hurt(unhit(p), dmg);
			hit.add(best);
			from = best;
		}
	}

	private static void died(LivingDeathEvent e) {
		LivingEntity dead = e.getEntity();
		if (dead.level().isClientSide) return;
		if (Spells.isThrall(dead)) {
			UUID owner = Spells.ownerOf(dead);
			Player p = owner == null ? null : dead.level().getPlayerByUUID(owner);
			if (p instanceof ServerPlayer sp && w(sp, "heart_of_the_hive") > 0 && !dead.getType().equals(EntityType.SILVERFISH))
				for (int k = 0; k < 3; k++)
					Spells.thrall(sp, EntityType.SILVERFISH, dead.getX() + (k - 1) * 0.6, dead.getY(), dead.getZ(), 160, 6 * power(sp), 2 * power(sp));
			return;
		}
		if (!(e.getSource().getEntity() instanceof ServerPlayer p) || !(dead instanceof Enemy)) return;
		S s = state(p);
		if (w(p, "salt_khans_seal") > 0) p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 60, 0));
		if (w(p, "briar_heart") > 0) p.heal(p.getMaxHealth() * 0.04f);
		int gland = w(p, "chimera_gland");
		if (gland > 0) {
			List<Holder<MobEffect>> pool = new ArrayList<>(List.of(MobEffects.DAMAGE_BOOST, MobEffects.MOVEMENT_SPEED, MobEffects.REGENERATION));
			java.util.Collections.shuffle(pool, new java.util.Random(p.getRandom().nextLong()));
			for (int k = 0; k < (gland == 3 ? 2 : 1); k++) p.addEffect(new MobEffectInstance(pool.get(k), 80 + 40 * gland, 0));
		}
		int signet = w(p, "barrow_kings_signet");
		if (signet > 0 && ++s.souls >= 12 - 2 * signet) {
			s.souls = 0;
			for (int k = 0; k < (signet == 3 ? 2 : 1); k++)
				Spells.thrall(p, EntityType.VEX, p.getX() + (k == 0 ? 1.5 : -1.5), p.getY() + 1, p.getZ(), 200 + 100 * signet, 24 * power(p), 5 * power(p));
			p.level().playSound(null, p.blockPosition(), SoundEvents.WITHER_SKELETON_AMBIENT, SoundSource.PLAYERS, 0.8f, 0.7f);
			say(p, "The Barrow King's warrior rises", ChatFormatting.DARK_AQUA);
		}
	}

	// ---------------------------------------------------------------- spells (Spells calls these)

	/** a cast went off: the Ninth Pyre makes every fourth free and stronger */
	static void onCast(ServerPlayer p, int cost) {
		S s = state(p);
		s.empowered = w(p, "ring_of_the_ninth_pyre") > 0 && ++s.casts % 4 == 0;
		if (s.empowered) {
			float mana = Math.min(Spells.max(p), p.getData(Spells.MANA) + cost);
			p.setData(Spells.MANA, mana);
			PacketDistributor.sendToPlayer(p, new Net.Mana(mana, Spells.max(p)));
			Vfx.rise(p, Vfx.wisp(0xE8742C, 0.4f, 20, -0.008f, true), 6);
			Vfx.around(p, Vfx.mote(0xFFB050, 0.03f, 12, -0.02f), 12, 0.12);
		}
	}

	static double spellMult(Player p) {
		S s = STATE.get(p.getUUID());
		return s != null && s.empowered ? 1.5 : 1;
	}

	/** a heal landed on these: the Censer clears a bad effect and empowers each */
	static void healed(ServerPlayer p, List<LivingEntity> near) {
		if (w(p, "salt_saints_censer") == 0) return;
		long now = p.level().getGameTime();
		for (LivingEntity e : near) {
			for (MobEffectInstance m : new ArrayList<>(e.getActiveEffects()))
				if (m.getEffect().value().getCategory() == MobEffectCategory.HARMFUL) {
					e.removeEffect(m.getEffect());
					break;
				}
			EMPOWER.put(e.getUUID(), new double[] {now + 60, 1.2});
		}
	}

	// ---------------------------------------------------------------- rolls

	private static void rolled(ServerPlayer p) {
		long now = p.level().getGameTime();
		S s = state(p);
		int pearl = w(p, "void_pearl");
		if (pearl > 0) {
			Vec3 from = p.position();
			Vec3 dir = p.getDeltaMovement().multiply(1, 0, 1);
			if (dir.lengthSqr() < 1e-4) dir = p.getLookAngle().multiply(1, 0, 1);
			dir = dir.normalize();
			void_(p, true);
			for (double d = 3; d >= 1; d -= 0.5) {
				AABB box = p.getBoundingBox().move(dir.scale(d));
				if (p.level().noCollision(p, box)) {
					p.teleportTo(p.getX() + dir.x * d, p.getY(), p.getZ() + dir.z * d);
					break;
				}
			}
			void_(p, false);
			Vfx.arc(p.serverLevel(), from.add(0, 1, 0), p.position().add(0, 1, 0), Vfx.mote(0xB070FF, 0.025f, 10, 0), 10, 0.1);
			AreaEffectCloud c = new AreaEffectCloud(p.level(), from.x, from.y, from.z);
			c.setOwner(p);
			c.setRadius(2f);
			c.setRadiusPerTick(0);
			c.setDuration(60);
			c.setParticle(Vfx.wisp(0x7A3FC8, 0.45f, 24, -0.004f, true));
			c.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 20 + 20 * pearl, 1));
			if (pearl == 3) c.addEffect(new MobEffectInstance(MobEffects.WITHER, 40, 0));
			p.level().addFreshEntity(c);
			p.level().playSound(null, p.blockPosition(), SoundEvents.ENDERMAN_TELEPORT, SoundSource.PLAYERS, 0.6f, 1.4f);
		}
		int spindle = w(p, "silk_matrons_spindle");
		if (spindle > 0 && now >= s.spindle) {
			s.spindle = now + 120;
			WEBS.add(new Web(p.serverLevel(), p.position(), now + 80, 10 + 10 * spindle, p.getUUID()));
		}
	}

	// ---------------------------------------------------------------- the key: relic powers and the Rift Key

	static void key(ServerPlayer p, int what) {
		long now = p.level().getGameTime();
		S s = state(p);
		WORN.put(p.getUUID(), read(p));
		if (what == 1) {   // a Gryphon Plume double jump (the client moved; the fall it was in no longer counts)
			if (w(p, "gryphon_plume") > 0) {
				p.resetFallDistance();
				plumeLook(p);
			}
			return;
		}
		if (what == 2) {   // sneak + key: the Rift Key
			if (w(p, "rift_key") == 0) {
				say(p, "No Rift Key worn", ChatFormatting.GRAY);
				return;
			}
			if (s.mark == null || s.markDim != p.level().dimension()) {
				s.mark = p.position();
				s.markDim = p.level().dimension();
				say(p, "Rift marked", ChatFormatting.LIGHT_PURPLE);
				void_(p, false);
			} else if (now < s.rift) {
				say(p, "The rift is closed for " + (s.rift - now) / 20 + " s", ChatFormatting.GRAY);
			} else {
				void_(p, true);
				p.teleportTo(s.mark.x, s.mark.y, s.mark.z);
				void_(p, false);
				p.level().playSound(null, p.blockPosition(), SoundEvents.ENDERMAN_TELEPORT, SoundSource.PLAYERS, 1f, 0.8f);
				s.mark = null;
				s.rift = now + 6000;
			}
			return;
		}
		int t;
		if ((t = w(p, "kiln_fathers_coal")) > 0) {
			if (ready(p, s.coal, now)) {
				s.coal = now + 1800;
				cd(p, 1800);
				s.coalUntil = now + 80 + 40L * t;
				p.addEffect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 80 + 40 * t, 0));
				coalLook(p);
				p.level().playSound(null, p.blockPosition(), SoundEvents.BLAZE_SHOOT, SoundSource.PLAYERS, 1f, 0.6f);
				say(p, "Molten", ChatFormatting.GOLD);
			}
		} else if ((t = w(p, "pale_abbots_wick")) > 0) {
			if (ready(p, s.wick, now)) {
				s.wick = now + 1200;
				cd(p, 1200);
				WARDS.add(new Ward(p.serverLevel(), p.position(), now + 100, 0.02f + 0.015f * t));
				wardLook(p);
				p.level().playSound(null, p.blockPosition(), SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.PLAYERS, 1f, 0.8f);
			}
		} else if ((t = w(p, "hangmans_noose")) > 0) {
			if (ready(p, s.noose, now)) {
				LivingEntity target = aimed(p, 16);
				if (target == null) {
					say(p, "Nothing to catch", ChatFormatting.GRAY);
					return;
				}
				s.noose = now + 400;
				cd(p, 400);
				Vec3 pull = p.position().subtract(target.position()).normalize().scale(isBoss(target) ? 0.4 : 1.6);
				target.setDeltaMovement(pull.x, 0.35, pull.z);
				target.hurtMarked = true;
				if (!isBoss(target)) stun(target, 10 + 10 * t);
				Vfx.arc(p.serverLevel(), Vfx.chest(p), Vfx.chest(target), Vfx.mote(0xB08A5A, 0.03f, 10, 0), 14, 0.08);
				Vfx.burst(p.serverLevel(), Vfx.chest(target), Vfx.mote(0xE0C890, 0.03f, 10, 0.03f), 10, 0.25);
				p.level().playSound(null, target.blockPosition(), SoundEvents.FISHING_BOBBER_RETRIEVE, SoundSource.PLAYERS, 1f, 0.6f);
			}
		} else if ((t = w(p, "mosskings_acorn")) > 0) {
			if (ready(p, s.acorn, now)) {
				s.acorn = now + 800;
				cd(p, 800);
				HitResult hr = p.level().clip(new ClipContext(p.getEyePosition(), p.getEyePosition().add(p.getLookAngle().scale(10)),
						ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, p));
				Vec3 at = hr.getLocation();
				for (LivingEntity m : p.level().getEntitiesOfClass(LivingEntity.class, new AABB(at, at).inflate(4), m -> foe(m, p)))
					stun(m, 30 + 10 * t);
				acornLook(p.serverLevel(), at);
				p.level().playSound(null, BlockPos.containing(at), SoundEvents.ROOTED_DIRT_BREAK, SoundSource.PLAYERS, 1.2f, 0.7f);
			}
		} else if ((t = w(p, "warhorn_of_the_last_keep")) > 0) {
			if (ready(p, s.horn, now)) {
				s.horn = now + 1200;
				cd(p, 1200);
				for (ServerPlayer q : p.serverLevel().getEntitiesOfClass(ServerPlayer.class, p.getBoundingBox().inflate(12))) {
					EMPOWER.put(q.getUUID(), new double[] {now + 200, 1.05 + 0.05 * t});
					AttributeInstance kb = q.getAttribute(Attributes.KNOCKBACK_RESISTANCE);
					if (kb != null && kb.getModifier(HORN_KB) == null)
						kb.addTransientModifier(new AttributeModifier(HORN_KB, 0.25, AttributeModifier.Operation.ADD_VALUE));
					HORNS.add(new Horn(q.getUUID(), now + 200));
					kindled(q);
				}
				hornLook(p);
				p.level().playSound(null, p.blockPosition(), SoundEvents.RAID_HORN.value(), SoundSource.PLAYERS, 1.2f, 1f);
			}
		} else say(p, "No relic with a power on this key", ChatFormatting.GRAY);
	}

	/** tells the relic HUD a cooldown started */
	private static void cd(ServerPlayer p, int ticks) {
		PacketDistributor.sendToPlayer(p, new Net.RelicCd(ticks));
	}

	private static boolean ready(ServerPlayer p, long at, long now) {
		if (now >= at) return true;
		say(p, "Ready in " + (at - now + 19) / 20 + " s", ChatFormatting.GRAY);
		return false;
	}

	/** the monster you look at, within reach */
	private static LivingEntity aimed(ServerPlayer p, double reach) {
		Vec3 eye = p.getEyePosition(), look = p.getLookAngle();
		LivingEntity best = null;
		double bestD = reach;
		for (LivingEntity m : p.level().getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(reach), m -> foe(m, p))) {
			var hit = m.getBoundingBox().inflate(0.4).clip(eye, eye.add(look.scale(reach)));
			if (hit.isPresent() && eye.distanceTo(hit.get()) < bestD) {
				bestD = eye.distanceTo(hit.get());
				best = m;
			}
		}
		return best;
	}

	// ---------------------------------------------------------------- the Gate Forge: relic tiers

	/** used on the Forge with a relic in hand: I -> II costs 1 boss trophy + 5000 Ash, II -> III 3 trophies + 20000 Ash */
	static void upgrade(ServerPlayer p, ItemStack relic) {
		int t = tier(relic);
		if (t >= 3) {
			say(p, "This relic is at its full power (III)", ChatFormatting.GOLD);
			return;
		}
		int trophies = t == 1 ? 1 : 3, ash = t == 1 ? 5000 : 20000;
		List<net.minecraft.world.item.Item> kinds = new ArrayList<>();
		for (Gear.Dungeon d : Gear.DUNGEONS) {
			net.minecraft.world.item.Item it = Gear.item(d.mats()[2]);
			if (it != null) kinds.add(it);
		}
		int have = 0;
		for (net.minecraft.world.item.Item it : kinds) have += GateForge.count(p, it);
		if (!p.isCreative() && (have < trophies || p.getData(Levels.ASH) < ash)) {
			say(p, "Power " + roman(t + 1) + " takes " + trophies + " boss troph" + (trophies == 1 ? "y" : "ies") + " and " + ash + " Ash", ChatFormatting.RED);
			return;
		}
		if (!p.isCreative()) {
			int left = trophies;
			for (ItemStack s : p.getInventory().items)
				if (left > 0 && kinds.contains(s.getItem())) {
					int k = Math.min(left, s.getCount());
					s.shrink(k);
					left -= k;
				}
			p.setData(Levels.ASH, p.getData(Levels.ASH) - ash);
			Levels.sync(p);
		}
		CustomData.update(DataComponents.CUSTOM_DATA, relic, tag -> tag.putInt(TIER, t + 1));
		p.level().playSound(null, p.blockPosition(), SoundEvents.ANVIL_USE, SoundSource.BLOCKS, 0.8f, 0.7f);
		p.level().playSound(null, p.blockPosition(), SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.PLAYERS, 0.6f, 1.2f);
		p.displayClientMessage(relic.getHoverName().copy().append(Component.literal(" awakens: power " + roman(t + 1)).withStyle(ChatFormatting.GOLD)), true);
	}

	public static String roman(int t) {
		return t <= 1 ? "I" : t == 2 ? "II" : "III";
	}

	// ---------------------------------------------------------------- ticking

	private static void tick(PlayerTickEvent.Post e) {
		if (!(e.getEntity() instanceof ServerPlayer p)) return;
		long now = p.level().getGameTime();
		if (p.tickCount % 10 == 0) WORN.put(p.getUUID(), read(p));
		Map<String, Integer> worn = WORN.get(p.getUUID());
		if (worn == null || worn.isEmpty()) return;
		S s = state(p);
		// the Plume: a slow fall (the client holds it there) doesn't build up a fall
		if (worn.containsKey("gryphon_plume") && !p.onGround() && p.getY() - p.yOld > -0.2) p.resetFallDistance();
		if (s.coalUntil > now && p.tickCount % 4 == 0) {   // the Coal: embers off the wearer, a glow now and then
			Vfx.rise(p, Vfx.mote(0xFF9A3A, 0.025f, 14, -0.03f), 3);
			if (p.tickCount % 12 == 0) Vfx.rise(p, Vfx.wisp(0xE8742C, 0.35f, 18, -0.01f, true), 1);
		}
		if (p.tickCount % 20 != 0) return;
		if (worn.containsKey("ring_of_the_drowned_god") && p.isInWater()) {
			p.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 80, 0, true, false));
			p.addEffect(new MobEffectInstance(MobEffects.DOLPHINS_GRACE, 80, 0, true, false));
		}
		if (worn.containsKey("grub_lantern") && p.getY() < 50 && !p.level().canSeeSky(p.blockPosition())
				&& (!p.hasEffect(MobEffects.NIGHT_VISION) || p.getEffect(MobEffects.NIGHT_VISION).getDuration() < 220))
			p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 400, 0, true, false));
		if (worn.containsKey("kraken_eye"))
			for (LivingEntity m : p.level().getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(24), m -> foe(m, p) && m.isInWater()))
				m.addEffect(new MobEffectInstance(MobEffects.GLOWING, 30, 0, true, false));
		if (worn.containsKey("bulwark_gorget"))
			for (Mob m : p.level().getEntitiesOfClass(Mob.class, p.getBoundingBox().inflate(12), m -> foe(m, p)
					&& m.getTarget() instanceof Player other && other != p))
				if (p.getRandom().nextFloat() < 0.2f) m.setTarget(p);
		if (worn.containsKey("corsairs_compass") && p.isShiftKeyDown()) compass(p);
	}

	/** the Compass (sneaking): the nearest structure chest nobody has opened yet */
	private static void compass(ServerPlayer p) {
		BlockPos best = null;
		int cx = p.blockPosition().getX() >> 4, cz = p.blockPosition().getZ() >> 4;
		for (int dx = -4; dx <= 4; dx++)
			for (int dz = -4; dz <= 4; dz++) {
				var chunk = p.level().getChunkSource().getChunkNow(cx + dx, cz + dz);
				if (chunk == null) continue;
				for (BlockEntity be : chunk.getBlockEntities().values())
					if (be instanceof RandomizableContainerBlockEntity c && c.getLootTable() != null
							&& (best == null || be.getBlockPos().distSqr(p.blockPosition()) < best.distSqr(p.blockPosition())))
						best = be.getBlockPos();
			}
		if (best == null) {
			say(p, "The needle drifts: no unopened chest near", ChatFormatting.GRAY);
			return;
		}
		Vec3 d = Vec3.atCenterOf(best).subtract(p.position());
		String[] dirs = {"south", "south-west", "west", "north-west", "north", "north-east", "east", "south-east"};
		int k = Math.floorMod((int) Math.round(Math.toDegrees(Math.atan2(-d.x, d.z)) / 45.0), 8);
		int up = (int) Math.round(d.y);
		say(p, "Chest: " + (int) d.horizontalDistance() + " blocks " + dirs[k] + (up > 2 ? ", " + up + " up" : up < -2 ? ", " + -up + " down" : ""),
				ChatFormatting.YELLOW);
	}

	private static void serverTick(ServerTickEvent.Post e) {
		var server = e.getServer();
		long now = server.overworld().getGameTime();
		EMPOWER.values().removeIf(v -> v[0] <= now);
		for (Blight b : new ArrayList<>(BLIGHTS.values())) {
			LivingEntity v = b.victim();
			if (b.until() <= now || !v.isAlive() || v.isRemoved()) {
				BLIGHTS.remove(v.getUUID(), b);
				continue;
			}
			if (now % 4 == 0) {   // rot: sickly vapour seeping off it, green ichor dripping
				Vfx.rise(v, Vfx.wisp(0x4E6A22, 0.4f, 26, -0.003f, false), 2);
				Vfx.rise(v, Vfx.wisp(0x9CE040, 0.3f, 18, -0.004f, true), 1);
				Vfx.drip(v, Vfx.mote(0xA6E04A, 0.02f, 14, 0.05f), 1);
				if (now % 12 == 0 && v.onGround() && v.level() instanceof ServerLevel bl)
					Vfx.groundRing(bl, v.position().add((bl.random.nextDouble() - 0.5) * v.getBbWidth(), 0.03, (bl.random.nextDouble() - 0.5) * v.getBbWidth()),
							0.04, Vfx.band(0xB6F04A, 0.05f, 30, 0.002f));
			}
			if (now % 20 == 0 && b.perSecond() > 0) {
				// past the hit's own i-frames and without adding any, so it never eats the wearer's next blow
				ServerPlayer p = server.getPlayerList().getPlayer(b.owner());
				int was = v.invulnerableTime;
				v.invulnerableTime = 0;
				v.hurt(p != null ? unhit(p) : v.damageSources().magic(), b.perSecond());
				v.invulnerableTime = was;
			}
		}
		for (Iterator<Map.Entry<UUID, double[]>> it = THAW.entrySet().iterator(); it.hasNext(); ) {
			var en = it.next();
			if (en.getValue()[0] > now) continue;
			ServerPlayer p = server.getPlayerList().getPlayer(en.getKey());
			if (p != null && p.isAlive()) {
				p.setHealth((float) Math.max(p.getHealth(), p.getMaxHealth() * en.getValue()[1]));
				p.setTicksFrozen(0);
				frost(p, 24);
			}
			it.remove();
		}
		for (Iterator<Ward> it = WARDS.iterator(); it.hasNext(); ) {
			Ward w = it.next();
			if (w.until() <= now) {
				it.remove();
				continue;
			}
			if (now % 20 == 0)
				for (LivingEntity l : w.level().getEntitiesOfClass(LivingEntity.class, new AABB(w.at(), w.at()).inflate(6),
						l -> l instanceof Player || Spells.isThrall(l))) {
					l.heal(l.getMaxHealth() * w.perSecond());
					Vfx.rise(l, Vfx.mote(0xFFD98A, 0.025f, 16, -0.02f), 3);
				}
			if (now % 4 == 0)
				for (int k = 0; k < 16; k++) {
					double a = k * Math.PI / 8 + now * 0.05;
					w.level().sendParticles(Vfx.wisp(0xF2B04A, 0.3f, 14, -0.004f, true), w.at().x + Math.cos(a) * 6, w.at().y + 0.2, w.at().z + Math.sin(a) * 6, 1, 0, 0.02, 0, 0);
				}
		}
		for (Iterator<Web> it = WEBS.iterator(); it.hasNext(); ) {
			Web w = it.next();
			if (w.until() <= now) {
				it.remove();
				continue;
			}
			if (now % 5 == 0) w.level().sendParticles(Vfx.wisp(0xE8E4DA, 0.35f, 20, 0, false), w.at().x, w.at().y + 0.15, w.at().z, 4, 0.7, 0.05, 0.7, 0);
			Player owner = w.level().getPlayerByUUID(w.owner());
			if (owner == null) continue;
			for (LivingEntity m : w.level().getEntitiesOfClass(LivingEntity.class, new AABB(w.at(), w.at()).inflate(1.5, 1, 1.5), m -> foe(m, owner))) {
				stun(m, w.stun());
				Vfx.burst(sl(m), Vfx.chest(m), Vfx.mote(0xF4F0E6, 0.025f, 12, 0.02f), 14, 0.25);
				Vfx.around(m, Vfx.wisp(0xE8E4DA, 0.4f, 22, 0, false), 5, 0.02);
				it.remove();
				break;
			}
		}
		for (Iterator<Sense> it = SENSES.iterator(); it.hasNext(); ) {
			Sense s = it.next();
			ServerPlayer p = server.getPlayerList().getPlayer(s.player());
			if (p == null || s.until() <= now) {
				it.remove();
				continue;
			}
			if (now % 10 == 0)
				for (BlockPos b : s.ores())
					p.serverLevel().sendParticles(p, Vfx.wisp(0xFFC860, 0.35f, 16, -0.002f, true), true, b.getX() + 0.5, b.getY() + 0.5, b.getZ() + 0.5, 1, 0.2, 0.2, 0.2, 0);
		}
		for (Iterator<Horn> it = HORNS.iterator(); it.hasNext(); ) {
			Horn h = it.next();
			if (h.until() > now) continue;
			ServerPlayer p = server.getPlayerList().getPlayer(h.player());
			if (p != null && HORNS.stream().noneMatch(o -> o != h && o.player().equals(h.player()) && o.until() > now)) {
				AttributeInstance kb = p.getAttribute(Attributes.KNOCKBACK_RESISTANCE);
				if (kb != null) kb.removeModifier(HORN_KB);
			}
			it.remove();
		}
		for (Iterator<Object[]> it = SHORTEN.iterator(); it.hasNext(); ) {
			Object[] o = it.next();
			it.remove();
			if (!(o[0] instanceof ServerPlayer p) || !p.isAlive()) continue;
			@SuppressWarnings("unchecked") Holder<MobEffect> eff = (Holder<MobEffect>) o[1];
			MobEffectInstance cur = p.getEffect(eff);
			if (cur == null) continue;
			int dur = (int) (cur.getDuration() * (1 - Math.min(0.9, (double) o[2])));
			p.removeEffect(eff);
			SHORTENING.set(true);
			try {
				p.addEffect(new MobEffectInstance(eff, dur, cur.getAmplifier(), cur.isAmbient(), cur.isVisible(), cur.showIcon()), null);
			} finally {
				SHORTENING.set(false);
			}
		}
	}

	/** the Salt Ward: poison and wither run shorter (trimmed the tick after they land) */
	private static final ThreadLocal<Boolean> SHORTENING = ThreadLocal.withInitial(() -> false);

	private static void effectAdded(MobEffectEvent.Added e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || SHORTENING.get()) return;
		Holder<MobEffect> eff = e.getEffectInstance().getEffect();
		if (!eff.equals(MobEffects.POISON) && !eff.equals(MobEffects.WITHER)) return;
		double cut = Passives.stat(p, "poison_short%") / 100;
		if (cut <= 0 || e.getOldEffectInstance() != null) return;
		SHORTEN.add(new Object[] {p, eff, cut});
	}

	/** the Cask Mother's Tap: a potion you drink reaches your friends */
	private static void potion(LivingEntityUseItemEvent.Finish e) {
		if (!(e.getEntity() instanceof ServerPlayer p)) return;
		int t = w(p, "cask_mothers_tap");
		var contents = e.getItem().get(DataComponents.POTION_CONTENTS);
		if (t == 0 || contents == null) return;
		double share = 0.25 + 0.25 * t;
		List<LivingEntity> near = p.level().getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(4 + 2 * t),
				l -> l != p && (l instanceof Player || Spells.isThrall(l)));
		contents.forEachEffect(m -> {
			for (LivingEntity l : near) {
				l.addEffect(new MobEffectInstance(m.getEffect(), (int) (m.getDuration() * share), m.getAmplifier()));
				Vfx.rise(l, Vfx.mote(0xF0E2B0, 0.025f, 16, -0.02f), 6);
				Vfx.rise(l, Vfx.wisp(0xD8C890, 0.35f, 20, -0.005f, true), 2);
			}
		});
	}

	/** Delver's Last Pick: a fifth of mined ore drops twice */
	private static void drops(BlockDropsEvent e) {
		if (!(e.getBreaker() instanceof ServerPlayer p) || !e.getState().is(Tags.Blocks.ORES) || w(p, "delvers_last_pick") == 0) return;
		if (p.getRandom().nextFloat() >= 0.2f) return;
		List<ItemEntity> extra = new ArrayList<>();
		for (ItemEntity it : e.getDrops()) extra.add(new ItemEntity(e.getLevel(), it.getX(), it.getY(), it.getZ(), it.getItem().copy()));
		e.getDrops().addAll(extra);
	}

	/** ...and breaking ore shows the ore round it for 5 s */
	private static void broke(BlockEvent.BreakEvent e) {
		if (!(e.getPlayer() instanceof ServerPlayer p) || !e.getState().is(Tags.Blocks.ORES) || w(p, "delvers_last_pick") == 0) return;
		long now = p.level().getGameTime();
		S s = state(p);
		if (now < s.pick) return;
		s.pick = now + 600;
		List<BlockPos> ores = new ArrayList<>();
		for (BlockPos b : BlockPos.betweenClosed(e.getPos().offset(-6, -6, -6), e.getPos().offset(6, 6, 6)))
			if (!b.equals(e.getPos()) && p.level().getBlockState(b).is(Tags.Blocks.ORES)) ores.add(b.immutable());
		if (!ores.isEmpty()) SENSES.add(new Sense(p.getUUID(), ores, now + 100));
	}
}
