package com.snoringwalrus.ashbound;

import javax.annotation.Nullable;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
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
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;

/**
 * Ossric's failed apprentices, ash over embers, hauling a Kiln Maul. Epic Fight fights it (CinderhuskPatch):
 * the maul's moves, stuns and knockdowns; it only wanders, looks about and picks whom to hunt itself.
 */
public class Cinderhusk extends Monster {
	public Cinderhusk(EntityType<? extends Cinderhusk> type, Level level) {
		super(type, level);
	}

	public static AttributeSupplier.Builder attributes() {
		return Monster.createMonsterAttributes()
				.add(Attributes.MAX_HEALTH, 40 * Balance.mob("cinderhusk").hp())
				.add(Attributes.MOVEMENT_SPEED, 0.24)
				.add(Attributes.ATTACK_DAMAGE, 6 * Balance.mob("cinderhusk").dmg())
				.add(Attributes.FOLLOW_RANGE, 32)
				.add(Attributes.ARMOR, 4)
				.add(Attributes.KNOCKBACK_RESISTANCE, 0.4);
	}

	@Override
	protected void registerGoals() {
		// Epic Fight adds its own attack and chase goals ahead of these
		goalSelector.addGoal(1, new FloatGoal(this));
		goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.8));
		goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 10));
		goalSelector.addGoal(7, new RandomLookAroundGoal(this));
		targetSelector.addGoal(1, new HurtByTargetGoal(this));
		targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
	}

	@Override
	public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType reason, @Nullable SpawnGroupData data) {
		data = super.finalizeSpawn(level, difficulty, reason, data);
		setItemSlot(EquipmentSlot.MAINHAND, new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "kiln_maul"))));
		setDropChance(EquipmentSlot.MAINHAND, 0);
		return data;
	}
}
