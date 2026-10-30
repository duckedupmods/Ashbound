package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

import javax.annotation.Nullable;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.BossEvent;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.monster.Spider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.common.DeferredSpawnEggItem;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import yesman.epicfight.api.event.EpicFightEventHooks;
import yesman.epicfight.api.utils.math.OpenMatrix4f;
import yesman.epicfight.gameasset.Armatures;
import yesman.epicfight.world.capabilities.entitypatch.mob.SpiderPatch;
import yesman.epicfight.world.capabilities.entitypatch.mob.ZombiePatch;

/**
 * The Silk Archive's dwellers (voxel models from E:\Ashbound's tools/vox*.py, put on Epic Fight's skeletons by
 * tools/efmob.py). The three that walk fight on its biped like zombies; the three spiders on its spider. Each mesh
 * is fitted at Epic Fight's size and drawn back up at its own (SCALE, efmob's "scale back").
 */
public final class SilkMobs {
	private SilkMobs() {}

	/** A kind: its id, the mesh efmob wrote, how much bigger than the mesh it's drawn, its hitbox. */
	public record Kind(String id, String mesh, float scale, float w, float h, int egg, int spots) {}

	public static final Kind SCHOLAR = new Kind("bound_scholar", "scholar", 1.6f, 0.9f, 2.4f, 0xd8d0bd, 0x2a2420);
	public static final Kind LECTOR = new Kind("lector", "lector", 1.75f, 0.9f, 2.6f, 0x3a2c2a, 0xc9b98f);
	public static final Kind INKBOUND = new Kind("inkbound", "inkbound", 1.7f, 1.0f, 2.5f, 0x15161a, 0x3e4f6a);
	public static final Kind WEAVER = new Kind("weaver", "weaver", 1.8f, 2.2f, 3.1f, 0xe8e2d6, 0x6a1f2a);
	public static final Kind MITE = new Kind("silk_mite", "mite", 0.34f, 0.5f, 0.35f, 0xece6da, 0x8a2a2a);
	public static final Kind QUEEN = new Kind("silk_queen", "silkqueen", 5.6f, 4.0f, 4.6f, 0xf2ece0, 0x8f1020);

	public static final List<Kind> WALKERS = List.of(SCHOLAR, LECTOR, INKBOUND);
	public static final List<Kind> SPIDERS = List.of(WEAVER, MITE, QUEEN);
	static final Map<Kind, DeferredHolder<EntityType<?>, EntityType<Walker>>> WALKER = new java.util.LinkedHashMap<>();
	static final Map<Kind, DeferredHolder<EntityType<?>, EntityType<Crawler>>> CRAWLER = new java.util.LinkedHashMap<>();
	static final List<DeferredItem<Item>> EGGS = new ArrayList<>();

	private static AttributeSupplier.Builder stats(Kind k) {
		Balance.Mult m = Balance.mob(k.id());
		AttributeSupplier.Builder b = Monster.createMonsterAttributes().add(Attributes.FOLLOW_RANGE, 32);
		if (k == SCHOLAR) return b.add(Attributes.MAX_HEALTH, 55 * m.hp()).add(Attributes.MOVEMENT_SPEED, 0.25).add(Attributes.ATTACK_DAMAGE, 8 * m.dmg()).add(Attributes.ARMOR, 4);
		if (k == LECTOR) return b.add(Attributes.MAX_HEALTH, 70 * m.hp()).add(Attributes.MOVEMENT_SPEED, 0.22).add(Attributes.ATTACK_DAMAGE, 9 * m.dmg()).add(Attributes.ARMOR, 6);
		if (k == INKBOUND) return b.add(Attributes.MAX_HEALTH, 95 * m.hp()).add(Attributes.MOVEMENT_SPEED, 0.23).add(Attributes.ATTACK_DAMAGE, 11 * m.dmg())
				.add(Attributes.ARMOR, 10).add(Attributes.KNOCKBACK_RESISTANCE, 0.6);
		if (k == WEAVER) return b.add(Attributes.MAX_HEALTH, 80 * m.hp()).add(Attributes.MOVEMENT_SPEED, 0.32).add(Attributes.ATTACK_DAMAGE, 10 * m.dmg()).add(Attributes.ARMOR, 4);
		if (k == MITE) return b.add(Attributes.MAX_HEALTH, 10 * m.hp()).add(Attributes.MOVEMENT_SPEED, 0.36).add(Attributes.ATTACK_DAMAGE, 3 * m.dmg());
		return b.add(Attributes.MAX_HEALTH, 600 * m.hp()).add(Attributes.MOVEMENT_SPEED, 0.28).add(Attributes.ATTACK_DAMAGE, 18 * m.dmg())
				.add(Attributes.ARMOR, 12).add(Attributes.KNOCKBACK_RESISTANCE, 1.0).add(Attributes.FOLLOW_RANGE, 48);
	}

	private static <T extends Monster> DeferredHolder<EntityType<?>, EntityType<T>> type(Kind k, EntityType.EntityFactory<T> make) {
		DeferredHolder<EntityType<?>, EntityType<T>> t = Monsters.ENTITIES.register(k.id(),
				() -> EntityType.Builder.of(make, MobCategory.MONSTER).sized(k.w(), k.h()).clientTrackingRange(10).build(Ashbound.ID + ":" + k.id()));
		Supplier<EntityType<? extends net.minecraft.world.entity.Mob>> s = t::get;
		EGGS.add(Weapons.ITEMS.registerItem(k.id() + "_spawn_egg", p -> new DeferredSpawnEggItem(s, k.egg(), k.spots(), p)));
		return t;
	}

	static {
		for (Kind k : WALKERS) WALKER.put(k, type(k, (t, l) -> new Walker(t, l, k)));
		for (Kind k : SPIDERS) CRAWLER.put(k, type(k, (t, l) -> new Crawler(t, l, k)));
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

	static void hunt(Monster m) {
		// Epic Fight adds its own attack and chase goals ahead of these
		m.goalSelector.addGoal(1, new FloatGoal(m));
		m.goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(m, 0.8));
		m.goalSelector.addGoal(6, new LookAtPlayerGoal(m, Player.class, 10));
		m.goalSelector.addGoal(7, new RandomLookAroundGoal(m));
		m.targetSelector.addGoal(1, new HurtByTargetGoal(m));
		m.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(m, Player.class, true));
	}

	/** The scholar, the lector and the inkbound. */
	public static class Walker extends Monster {
		public final Kind kind;

		public Walker(EntityType<? extends Walker> type, Level level, Kind kind) {
			super(type, level);
			this.kind = kind;
		}

		@Override
		protected void registerGoals() {
			hunt(this);
		}
	}

	/** The weaver, the mites and the Silk Queen: spiders, so they climb the stacks. */
	public static class Crawler extends Spider {
		public final Kind kind;
		@Nullable
		private final ServerBossEvent bar;

		public Crawler(EntityType<? extends Crawler> type, Level level, Kind kind) {
			super(type, level);
			this.kind = kind;
			bar = kind == QUEEN && !level.isClientSide ? new ServerBossEvent(Component.translatable("entity.ashbound.silk_queen"),
					BossEvent.BossBarColor.RED, BossEvent.BossBarOverlay.NOTCHED_10) : null;
			if (kind == QUEEN) xpReward = 200;
		}

		@Override
		protected void registerGoals() {
			hunt(this);   // not the vanilla spider's: these hunt by day as well
		}

		@Override
		public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType reason, @Nullable SpawnGroupData data) {
			data = super.finalizeSpawn(level, difficulty, reason, data);
			for (Entity rider : getPassengers()) rider.discard();   // no skeleton riding it, no vanilla spider's potions
			removeAllEffects();
			return data;
		}

		@Override
		protected void customServerAiStep() {
			super.customServerAiStep();
			if (bar != null) bar.setProgress(getHealth() / getMaxHealth());
		}

		@Override
		public void startSeenByPlayer(ServerPlayer p) {
			super.startSeenByPlayer(p);
			if (bar != null) bar.addPlayer(p);
		}

		@Override
		public void stopSeenByPlayer(ServerPlayer p) {
			super.stopSeenByPlayer(p);
			if (bar != null) bar.removePlayer(p);
		}
	}

	public static class WalkerPatch extends ZombiePatch<Walker> {
		public WalkerPatch(Walker original) {
			super(original);
		}

		@Override
		public OpenMatrix4f getModelMatrix(float partialTicks) {
			float s = original.kind.scale();
			return super.getModelMatrix(partialTicks).scale(s, s, s);
		}
	}

	public static class CrawlerPatch extends SpiderPatch<Crawler> {
		public CrawlerPatch(Crawler original) {
			super(original);
		}

		@Override
		public OpenMatrix4f getModelMatrix(float partialTicks) {
			float s = original.kind.scale();
			return super.getModelMatrix(partialTicks).scale(s, s, s);
		}
	}
}
