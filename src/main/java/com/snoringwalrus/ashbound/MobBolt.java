package com.snoringwalrus.ashbound;

import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.neoforged.neoforge.registries.DeferredHolder;

/** A gate monster's bolt (MobSkills): the black staffs' bolt (Spells.Bolt), its dungeon's element, thrown at players. */
public class MobBolt extends Spells.Bolt {
	static final DeferredHolder<EntityType<?>, EntityType<MobBolt>> TYPE = Monsters.ENTITIES.register("mob_bolt",
			() -> EntityType.Builder.<MobBolt>of(MobBolt::new, MobCategory.MISC).sized(0.4f, 0.4f).clientTrackingRange(6).updateInterval(1)
					.build(Ashbound.ID + ":mob_bolt"));

	public MobBolt(EntityType<? extends MobBolt> type, Level level) {
		super(type, level);
	}

	@Override
	protected boolean canHitEntity(Entity e) {
		// an adventurer mage's bolt is for monsters only
		if (getOwner() instanceof Adventurer) return e != getOwner() && e.isAlive() && e instanceof Enemy;
		return e != getOwner() && e.isAlive() && e instanceof LivingEntity && !(e instanceof Enemy) && !(e instanceof Player p && (p.isSpectator() || p.isCreative()));
	}
}
