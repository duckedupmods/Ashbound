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

	/** What a four-legged one sounds like: its own kind's, never the vanilla spider's it's built on (that's only for climbing). */
	record Voice(@Nullable net.minecraft.sounds.SoundEvent ambient, net.minecraft.sounds.SoundEvent hurt, net.minecraft.sounds.SoundEvent death,
			net.minecraft.sounds.SoundEvent step, float pitch) {}

	private static final Voice HOUND = new Voice(SoundEvents.WOLF_GROWL, SoundEvents.WOLF_HURT, SoundEvents.WOLF_DEATH, SoundEvents.WOLF_STEP, 0.75f),
			BUG = new Voice(SoundEvents.SILVERFISH_AMBIENT, SoundEvents.SILVERFISH_HURT, SoundEvents.SILVERFISH_DEATH, SoundEvents.SILVERFISH_STEP, 0.6f),
			HULL = new Voice(SoundEvents.ELDER_GUARDIAN_AMBIENT, SoundEvents.ELDER_GUARDIAN_HURT, SoundEvents.ELDER_GUARDIAN_DEATH, SoundEvents.RAVAGER_STEP, 0.55f),
			MITE = new Voice(SoundEvents.ENDERMITE_AMBIENT, SoundEvents.ENDERMITE_HURT, SoundEvents.ENDERMITE_DEATH, SoundEvents.ENDERMITE_STEP, 0.8f),
			BEAST = new Voice(SoundEvents.HOGLIN_AMBIENT, SoundEvents.HOGLIN_HURT, SoundEvents.HOGLIN_DEATH, SoundEvents.HOGLIN_STEP, 0.85f),
			STEED = new Voice(SoundEvents.SKELETON_HORSE_AMBIENT, SoundEvents.SKELETON_HORSE_HURT, SoundEvents.SKELETON_HORSE_DEATH, SoundEvents.HORSE_STEP, 0.8f),
			DRAKE = new Voice(SoundEvents.RAVAGER_AMBIENT, SoundEvents.RAVAGER_HURT, SoundEvents.RAVAGER_DEATH, SoundEvents.RAVAGER_STEP, 1.25f),
			WING = new Voice(SoundEvents.PHANTOM_AMBIENT, SoundEvents.PHANTOM_HURT, SoundEvents.PHANTOM_DEATH, SoundEvents.HORSE_STEP, 0.7f),
			WET = new Voice(SoundEvents.GUARDIAN_AMBIENT_LAND, SoundEvents.GUARDIAN_HURT_LAND, SoundEvents.GUARDIAN_DEATH_LAND, SoundEvents.GUARDIAN_FLOP, 0.7f),
			SLIME = new Voice(SoundEvents.SLIME_SQUISH, SoundEvents.SLIME_HURT, SoundEvents.SLIME_DEATH, SoundEvents.SLIME_SQUISH_SMALL, 0.7f),
			IRON = new Voice(null, SoundEvents.IRON_GOLEM_HURT, SoundEvents.IRON_GOLEM_DEATH, SoundEvents.IRON_GOLEM_STEP, 1.4f),
			WOOD = new Voice(null, SoundEvents.ZOMBIE_ATTACK_WOODEN_DOOR, SoundEvents.ZOMBIE_BREAK_WOODEN_DOOR, SoundEvents.WOOD_STEP, 0.8f),
			HEART = new Voice(SoundEvents.WARDEN_HEARTBEAT, SoundEvents.WARDEN_HURT, SoundEvents.WARDEN_DEATH, SoundEvents.SLIME_SQUISH, 1f),
			CORPSE = new Voice(SoundEvents.ZOMBIE_AMBIENT, SoundEvents.ZOMBIE_HURT, SoundEvents.ZOMBIE_DEATH, SoundEvents.ZOMBIE_STEP, 0.8f),
			// the world's beasts (WorldBeasts)
			BOAR = new Voice(SoundEvents.HOGLIN_AMBIENT, SoundEvents.HOGLIN_HURT, SoundEvents.HOGLIN_DEATH, SoundEvents.HOGLIN_STEP, 0.65f),
			BULL = new Voice(SoundEvents.RAVAGER_AMBIENT, SoundEvents.RAVAGER_HURT, SoundEvents.RAVAGER_DEATH, SoundEvents.RAVAGER_STEP, 0.7f),
			SABRE = new Voice(SoundEvents.POLAR_BEAR_WARNING, SoundEvents.POLAR_BEAR_HURT, SoundEvents.POLAR_BEAR_DEATH, SoundEvents.POLAR_BEAR_STEP, 0.7f),
			// the Rime Penitent: a hollow groan in the ice, iron and glass when it's hit, a stride like a golem's
			PENITENT = new Voice(SoundEvents.WARDEN_AMBIENT, SoundEvents.IRON_GOLEM_HURT, SoundEvents.WARDEN_DEATH, SoundEvents.IRON_GOLEM_STEP, 0.55f),
			// the other Legends: each its own throat, its own tread
			BRIAR = new Voice(SoundEvents.RAVAGER_ROAR, SoundEvents.WOOD_BREAK, SoundEvents.RAVAGER_DEATH, SoundEvents.WOOD_STEP, 0.6f),
			PLOUGH = new Voice(SoundEvents.RAVAGER_AMBIENT, SoundEvents.IRON_GOLEM_DAMAGE, SoundEvents.IRON_GOLEM_DEATH, SoundEvents.IRON_GOLEM_STEP, 0.5f),
			COLOSSUS = new Voice(SoundEvents.ELDER_GUARDIAN_AMBIENT_LAND, SoundEvents.STONE_BREAK, SoundEvents.IRON_GOLEM_DEATH, SoundEvents.STONE_STEP, 0.45f),
			HAG = new Voice(SoundEvents.WITCH_CELEBRATE, SoundEvents.WITCH_HURT, SoundEvents.WITCH_DEATH, SoundEvents.SLIME_SQUISH, 0.6f),
			SMILE = new Voice(SoundEvents.ENDERMAN_AMBIENT, SoundEvents.ENDERMAN_HURT, SoundEvents.ENDERMAN_DEATH, SoundEvents.BAMBOO_WOOD_STEP, 0.6f),
			DROWNED_GIANT = new Voice(SoundEvents.DROWNED_AMBIENT, SoundEvents.DROWNED_HURT, SoundEvents.DROWNED_DEATH, SoundEvents.DROWNED_STEP, 0.5f),
			MOUNTAIN = new Voice(SoundEvents.RAVAGER_ROAR, SoundEvents.STONE_BREAK, SoundEvents.IRON_GOLEM_DEATH, SoundEvents.STONE_STEP, 0.4f),
			LIZARD = new Voice(SoundEvents.CAT_HISS, SoundEvents.SNIFFER_HURT, SoundEvents.SNIFFER_DEATH, SoundEvents.SNIFFER_STEP, 0.55f),
			TOAD = new Voice(SoundEvents.FROG_AMBIENT, SoundEvents.FROG_HURT, SoundEvents.FROG_DEATH, SoundEvents.FROG_STEP, 0.4f),
			PANTHER = new Voice(SoundEvents.CAT_HISS, SoundEvents.CAT_HURT, SoundEvents.CAT_DEATH, SoundEvents.WOLF_STEP, 0.45f),
			WALRUS = new Voice(SoundEvents.POLAR_BEAR_AMBIENT, SoundEvents.GUARDIAN_HURT_LAND, SoundEvents.GUARDIAN_DEATH_LAND, SoundEvents.GUARDIAN_FLOP, 0.5f),
			APE = new Voice(SoundEvents.RAVAGER_AMBIENT, SoundEvents.IRON_GOLEM_HURT, SoundEvents.IRON_GOLEM_DEATH, SoundEvents.IRON_GOLEM_STEP, 0.55f);

	static Voice voice(String id) {
		if (LegendSounds.has(id)) return LegendSounds.voice(id);   // the Legends speak with their own voices
		switch (id) {
			case "wreck_mother": return HULL;                     // a ship-crab, not a spider (11/7: "it has spider sounds")
			case "thornmaw": return BOAR;
			case "gorehorn": return BULL;
			case "frostjaw", "pale_widow": return SABRE;
			case "rime_penitent": return PENITENT;
			case "old_blackbriar": return BRIAR;
			case "red_plough": return PLOUGH;
			case "sunbreaker": return COLOSSUS;
			case "grandmother_mire": return HAG;
			case "hollow_smile": return SMILE;
			case "old_harpoon": return DROWNED_GIANT;
			case "walking_mountain": return MOUNTAIN;
			case "sun_basilisk": return LIZARD;
			case "bogmaw": return TOAD;
			case "vexclaw": return PANTHER;
			case "tidetusk": return WALRUS;
			case "cragmaul": return APE;
			default: break;
		}
		if (id.contains("hound") || id.contains("wolf") || id.contains("hyena") || id.contains("warg")) return HOUND;
		if (id.contains("mite") || id.contains("tick")) return MITE;
		if (id.contains("stag")) return BEAST;
		if (id.contains("destrier")) return STEED;
		if (id.contains("gryphon")) return WING;
		if (id.contains("drake") || id.contains("ignavar") || id.contains("salamander")) return DRAKE;
		if (id.contains("eel") || id.contains("crab") || id.contains("kraken") || id.contains("deep_thing")) return WET;
		if (id.contains("slug") || id.contains("leech")) return SLIME;
		if (id.contains("cogling") || id.contains("drill")) return IRON;
		if (id.contains("mimic")) return WOOD;
		if (id.contains("heart")) return HEART;
		if (id.contains("convict")) return CORPSE;
		return BUG;   // crawlers, beetles, scarabs, scorpions, the ossipede, the coilspawn, the brood queen
	}

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
		@Override
		public boolean isPushable() {
			return !kind.boss() && super.isPushable();
		}

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

		// the ones with voices of their own (LegendSounds: the ashfall night's); the rest keep a monster's
		private Voice own() {
			return LegendSounds.has(kind.id()) ? LegendSounds.voice(kind.id()) : null;
		}

		@Override
		protected net.minecraft.sounds.SoundEvent getAmbientSound() {
			Voice v = own();
			return v != null ? v.ambient() : super.getAmbientSound();
		}

		@Override
		protected net.minecraft.sounds.SoundEvent getHurtSound(DamageSource src) {
			Voice v = own();
			return v != null ? v.hurt() : super.getHurtSound(src);
		}

		@Override
		protected net.minecraft.sounds.SoundEvent getDeathSound() {
			Voice v = own();
			return v != null ? v.death() : super.getDeathSound();
		}

		@Override
		protected void playStepSound(net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState state) {
			Voice v = own();
			if (v != null && v.step() != null) playSound(v.step(), 0.3f, 1f);
			else super.playStepSound(pos, state);
		}

		@Override
		public float getVoicePitch() {
			Voice v = own();
			return v != null ? v.pitch() * (0.92f + random.nextFloat() * 0.16f) : super.getVoicePitch();
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
		private Voice voice() {
			return GateMobs.voice(kind.id());
		}

		@Override
		protected net.minecraft.sounds.SoundEvent getAmbientSound() {
			return voice().ambient();
		}

		@Override
		protected net.minecraft.sounds.SoundEvent getHurtSound(DamageSource source) {
			return voice().hurt();
		}

		@Override
		protected net.minecraft.sounds.SoundEvent getDeathSound() {
			return voice().death();
		}

		@Override
		protected void playStepSound(net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState state) {
			playSound(voice().step(), 0.15f, 1f);
		}

		@Override
		public float getVoicePitch() {
			return voice().pitch() * (kind.boss() ? 0.8f : 1f) * (0.9f + random.nextFloat() * 0.2f);
		}


		@Override
		public boolean isPushable() {
			return !kind.boss() && super.isPushable();
		}

		/** the world's beasts walk; only the many-legged climb */
		@Override
		public boolean onClimbable() {
			return !WorldBeasts.IDS.contains(kind.id()) && super.onClimbable();
		}

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
