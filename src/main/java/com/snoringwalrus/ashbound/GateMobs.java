package com.snoringwalrus.ashbound;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

import javax.annotation.Nullable;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import net.minecraft.world.InteractionHand;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.WrappedGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.monster.Spider;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.common.DeferredSpawnEggItem;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import yesman.epicfight.api.collider.Collider;
import yesman.epicfight.api.event.EpicFightEventHooks;
import yesman.epicfight.api.utils.math.OpenMatrix4f;
import yesman.epicfight.gameasset.Armatures;
import yesman.epicfight.world.capabilities.entitypatch.mob.SpiderPatch;
import yesman.epicfight.api.animation.Animator;
import yesman.epicfight.api.animation.LivingMotions;
import yesman.epicfight.gameasset.Animations;
import yesman.epicfight.world.capabilities.entitypatch.Factions;
import yesman.epicfight.world.capabilities.entitypatch.HumanoidMobPatch;
import yesman.epicfight.world.entity.ai.goal.AnimatedAttackGoal;
import yesman.epicfight.world.entity.ai.goal.TargetChasingGoal;

/**
 * The older gates' dwellers (the Drowned Cellar's, Gallows Hill's...), listed in /ashbound/gate_mobs.json by
 * tools/port_gate.py: each one's voxel model from E:\Ashbound put on Epic Fight's biped or spider by tools/efmob.py,
 * drawn back up at its own size, fought like the Silk Archive's (SilkMobs). A boss gets a bar; the one that holds a
 * gate's key opens its seal when it falls.
 */
public final class GateMobs {
	private GateMobs() {}

	/** A kind: its id, the mesh efmob wrote, "biped" or "spider", how much bigger than the mesh it's drawn, its hitbox. */
	public record Kind(String id, String mesh, boolean spider, float scale, float w, float h, double hp, double speed, double dmg,
			double armor, double kb, boolean boss, boolean key, boolean fire, int egg, int spots, float reach) {}

	/** Built on four legs (efmob.mounted): how much of a clip's hip motion each keeps. A rider's horse none, a beast enough to lunge. */
	public static final Map<String, Float> ON_ALL_FOURS = Map.of("winter_marshal", 0f, "bone_hound", 0.35f, "grave_rat", 0.35f);

	public static final List<Kind> KINDS = load();
	static final Map<Kind, DeferredHolder<EntityType<?>, EntityType<Walker>>> WALKER = new LinkedHashMap<>();
	static final Map<Kind, DeferredHolder<EntityType<?>, EntityType<Crawler>>> CRAWLER = new LinkedHashMap<>();
	static final List<DeferredItem<Item>> EGGS = new ArrayList<>();

	private static List<Kind> load() {
		List<Kind> out = new ArrayList<>();
		try (InputStream in = GateMobs.class.getResourceAsStream("/ashbound/gate_mobs.json")) {
			if (in == null) return out;
			for (JsonElement el : JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonArray()) {
				JsonObject o = el.getAsJsonObject();
				out.add(new Kind(o.get("id").getAsString(), o.get("mesh").getAsString(), "spider".equals(o.get("rig").getAsString()),
						o.get("scale").getAsFloat(), o.get("w").getAsFloat(), o.get("h").getAsFloat(), o.get("hp").getAsDouble(),
						o.get("speed").getAsDouble(), o.get("dmg").getAsDouble(), o.get("armor").getAsDouble(), o.get("kb").getAsDouble(),
						o.has("boss") && o.get("boss").getAsBoolean(), o.has("key") && o.get("key").getAsBoolean(),
						o.has("fire") && o.get("fire").getAsBoolean(), o.get("egg").getAsInt(), o.get("spots").getAsInt(),
						o.has("reach") ? o.get("reach").getAsFloat() : 0));
			}
		} catch (Exception e) {
			Ashbound.LOG.error("gate monsters not loaded", e);
		}
		return out;
	}

	private static AttributeSupplier.Builder stats(Kind k) {
		Balance.Mult b = Balance.mob(k.id());
		return Monster.createMonsterAttributes().add(Attributes.FOLLOW_RANGE, k.boss() ? 48 : 32).add(Attributes.MAX_HEALTH, k.hp() * b.hp())
				.add(Attributes.STEP_HEIGHT, k.boss() ? 1.6 : 0.6)
				.add(Attributes.MOVEMENT_SPEED, k.speed()).add(Attributes.ATTACK_DAMAGE, k.dmg() * b.dmg()).add(Attributes.ARMOR, k.armor())
				.add(Attributes.KNOCKBACK_RESISTANCE, k.kb());
	}

	private static <T extends Monster> DeferredHolder<EntityType<?>, EntityType<T>> type(Kind k, EntityType.EntityFactory<T> make) {
		DeferredHolder<EntityType<?>, EntityType<T>> t = Monsters.ENTITIES.register(k.id(), () -> {
			EntityType.Builder<T> b = EntityType.Builder.of(make, MobCategory.MONSTER).sized(k.w(), k.h()).clientTrackingRange(10);
			if (k.fire()) b.fireImmune();
			return b.build(Ashbound.ID + ":" + k.id());
		});
		Supplier<EntityType<? extends net.minecraft.world.entity.Mob>> s = t::get;
		EGGS.add(Weapons.ITEMS.registerItem(k.id() + "_spawn_egg", p -> new DeferredSpawnEggItem(s, k.egg(), k.spots(), p)));
		return t;
	}

	static {
		for (Kind k : KINDS) {
			if (k.spider()) CRAWLER.put(k, type(k, (t, l) -> new Crawler(t, l, k)));
			else WALKER.put(k, type(k, (t, l) -> new Walker(t, l, k)));
		}
	}

	static void register(IEventBus bus) {
		bus.addListener((EntityAttributeCreationEvent e) -> {
			WALKER.forEach((k, t) -> e.put(t.get(), stats(k).build()));
			CRAWLER.forEach((k, t) -> e.put(t.get(), stats(k).build()));
		});
		EpicFightEventHooks.Registry.ENTITY_PATCH.registerEvent(e -> {
			WALKER.forEach((k, t) -> e.registerEntityPatch(t.get(), m -> new WalkerPatch((Walker) m)));
			CRAWLER.forEach((k, t) -> e.registerEntityPatch(t.get(), m -> new CrawlerPatch((Crawler) m)));
		});
		bus.addListener((FMLCommonSetupEvent e) -> e.enqueueWork(() -> {
			WALKER.values().forEach(t -> Armatures.registerEntityTypeArmature(t.get(), Armatures.BIPED));
			CRAWLER.values().forEach(t -> Armatures.registerEntityTypeArmature(t.get(), Armatures.SPIDER));
		}));
	}

	/** The key-holder falls: the gate's seal (its "seal:N" points) gives way. */
	private static void fell(Kind k, Entity e) {
		if (k.key() && e.level() instanceof ServerLevel level) {
			Lairs.openSeal(level, e.blockPosition());
			MobSkills.unward(level, e.blockPosition());
		}
	}

	/** A shield-bearer takes a blow from in front on its shield. */
	private static float guard(Mob m, Kind k, DamageSource source, float amount) {
		if (!MobMoves.of(k).shield() || MobSkills.busy(m) || !(source.getEntity() instanceof LivingEntity by)) return amount;
		Vec3 to = by.position().subtract(m.position()).normalize();
		if (to.dot(Vec3.directionFromRotation(0, m.yBodyRot)) < 0.45) return amount;
		m.level().playSound(null, m.getX(), m.getY(), m.getZ(), SoundEvents.SHIELD_BLOCK, SoundSource.HOSTILE, 1f, 0.8f);
		if (m.level() instanceof ServerLevel level)
			level.sendParticles(ParticleTypes.ENCHANTED_HIT, m.getX() + to.x * m.getBbWidth() * 0.6, m.getY() + m.getBbHeight() * 0.5,
					m.getZ() + to.z * m.getBbWidth() * 0.6, 10, 0.2, 0.3, 0.2, 0.1);
		return amount * 0.35f;
	}

	/** The ones that walk on two legs. */
	public static class Walker extends Monster implements MobSkills.User {
		public final Kind kind;
		private final MobSkills.State skills = new MobSkills.State();

		public Walker(EntityType<? extends Walker> type, Level level, Kind kind) {
			super(type, level);
			this.kind = kind;
			if (kind.boss()) xpReward = 150;
		}

		@Override
		public Kind kind() {
			return kind;
		}

		@Override
		public MobSkills.State state() {
			return skills;
		}

		@Override
		public boolean hurt(DamageSource source, float amount) {
			if (!level().isClientSide && MobSkills.refuses(this, source.getEntity())) return false;
			return super.hurt(source, guard(this, kind, source, amount));
		}

		@Override
		public void addAdditionalSaveData(CompoundTag tag) {
			super.addAdditionalSaveData(tag);
			skills.save(tag);
		}

		@Override
		public void readAdditionalSaveData(CompoundTag tag) {
			super.readAdditionalSaveData(tag);
			skills.load(tag);
		}

		@Override
		public void remove(RemovalReason reason) {
			MobSkills.gone(this);
			super.remove(reason);
		}

		@Override
		protected void registerGoals() {
			SilkMobs.hunt(this);
			goalSelector.addGoal(0, new MobSkills.SkillGoal(this));
		}

		@Override
		public void die(DamageSource cause) {
			super.die(cause);
			fell(kind, this);
			MobSkills.gone(this);
		}

		@Override
		protected void customServerAiStep() {
			super.customServerAiStep();
			MobSkills.tick(this);
		}
	}

	/** The many-legged ones, on the spider: they climb. */
	public static class Crawler extends Spider implements MobSkills.User {
		public final Kind kind;
		private final MobSkills.State skills = new MobSkills.State();

		public Crawler(EntityType<? extends Crawler> type, Level level, Kind kind) {
			super(type, level);
			this.kind = kind;
			if (kind.boss()) xpReward = 150;
		}

		@Override
		public Kind kind() {
			return kind;
		}

		@Override
		public MobSkills.State state() {
			return skills;
		}

		@Override
		public boolean hurt(DamageSource source, float amount) {
			if (!level().isClientSide && MobSkills.refuses(this, source.getEntity())) return false;
			return super.hurt(source, guard(this, kind, source, amount));
		}

		@Override
		public void addAdditionalSaveData(CompoundTag tag) {
			super.addAdditionalSaveData(tag);
			skills.save(tag);
		}

		@Override
		public void readAdditionalSaveData(CompoundTag tag) {
			super.readAdditionalSaveData(tag);
			skills.load(tag);
		}

		@Override
		public void remove(RemovalReason reason) {
			MobSkills.gone(this);
			super.remove(reason);
		}

		@Override
		protected void registerGoals() {
			SilkMobs.hunt(this);
			goalSelector.addGoal(0, new MobSkills.SkillGoal(this));
		}

		@Override
		public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType reason, @Nullable SpawnGroupData data) {
			data = super.finalizeSpawn(level, difficulty, reason, data);
			for (Entity rider : getPassengers()) rider.discard();
			removeAllEffects();
			return data;
		}

		@Override
		public void die(DamageSource cause) {
			super.die(cause);
			fell(kind, this);
			MobSkills.gone(this);
		}

		@Override
		protected void customServerAiStep() {
			super.customServerAiStep();
			MobSkills.tick(this);
			MobMoves.press(this, kind);
		}
	}

	/** Fought by Epic Fight on its biped: its own stance and skills (MobMoves), not a zombie's grab. */
	public static class WalkerPatch extends HumanoidMobPatch<Walker> {
		public WalkerPatch(Walker original) {
			super(original, Factions.UNDEAD);
		}

		@Override
		public void initAnimator(Animator animator) {
			super.initAnimator(animator);
			commonAggresiveMobAnimatorInit(animator);
			animator.addLivingAnimation(LivingMotions.CHASE, Animations.BIPED_RUN);
		}

		@Override
		public void updateMotion(boolean considerInaction) {
			super.commonAggressiveMobUpdateMotion(considerInaction);
		}

		@Override
		public void setAIAsInfantry(boolean holdingRangedWeapon) {
			Kind k = original.kind;
			original.goalSelector.addGoal(0, new AnimatedAttackGoal<>(this, MobMoves.<HumanoidMobPatch<?>>behaviours(original, k).build(this)));
			original.goalSelector.addGoal(1, new TargetChasingGoal(this, original, MobMoves.chase(k), true, MobMoves.stopAt(k)));
		}

		@Override
		public Collider getColliderMatching(InteractionHand hand) {
			Collider own = MobMoves.collider(original.kind);
			return own != null ? own : super.getColliderMatching(hand);
		}

		@Override
		public OpenMatrix4f getModelMatrix(float partialTicks) {
			float s = original.kind.scale();
			return super.getModelMatrix(partialTicks).scale(s, s, s);
		}
	}

	/** Fought by Epic Fight on its spider: its bites and leaps, reach grown with its size, and its own skills. */
	public static class CrawlerPatch extends SpiderPatch<Crawler> {
		public CrawlerPatch(Crawler original) {
			super(original);
		}

		@Override
		protected void initAI() {
			super.initAI();
			for (WrappedGoal w : java.util.List.copyOf(original.goalSelector.getAvailableGoals()))
				if (w.getGoal() instanceof AnimatedAttackGoal || w.getGoal() instanceof TargetChasingGoal) original.goalSelector.removeGoal(w.getGoal());
			Kind k = original.kind;
			original.goalSelector.addGoal(0, new AnimatedAttackGoal<>(this, MobMoves.<SpiderPatch<?>>behaviours(original, k).build(this)));
			original.goalSelector.addGoal(1, new TargetChasingGoal(this, original, 1.0D, false, MobMoves.stopAt(k)));
		}

		@Override
		public OpenMatrix4f getModelMatrix(float partialTicks) {
			float s = original.kind.scale();
			return super.getModelMatrix(partialTicks).scale(s, s, s);
		}
	}
}
