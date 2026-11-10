package com.snoringwalrus.ashbound;

import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.neoforged.neoforge.registries.DeferredHolder;

/** A slab of ice a beast tore out of the ground and flung (Beast's "throw"): it hits hard and freezes you solid. */
public class IceSlab extends ThrowableItemProjectile {
	static final DeferredHolder<EntityType<?>, EntityType<IceSlab>> TYPE = Monsters.ENTITIES.register("ice_slab",
			() -> EntityType.Builder.<IceSlab>of(IceSlab::new, MobCategory.MISC).sized(1.0f, 1.0f).clientTrackingRange(8).updateInterval(1)
					.build(Ashbound.ID + ":ice_slab"));

	float damage = 8;
	/** 0 ice, 1 a soul lantern, 2 a harpoon, 3 a boulder */
	int kind;

	public IceSlab(EntityType<? extends IceSlab> type, Level level) {
		super(type, level);
	}

	IceSlab(Level level, LivingEntity owner, float damage) {
		this(level, owner, damage, 0);
	}

	IceSlab(Level level, LivingEntity owner, float damage, int kind) {
		super(TYPE.get(), owner, level);
		this.damage = damage;
		this.kind = kind;
		setItem(new net.minecraft.world.item.ItemStack(switch (kind) {
			case 1 -> Items.SOUL_LANTERN;
			case 2 -> Items.TRIDENT;
			case 3 -> Items.TERRACOTTA;
			default -> Items.PACKED_ICE;
		}));
	}

	@Override
	protected Item getDefaultItem() {
		return Items.PACKED_ICE;
	}

	@Override
	protected double getDefaultGravity() {
		return 0.04;
	}

	@Override
	protected boolean canHitEntity(Entity e) {
		return e != getOwner() && !(e instanceof Beast) && e instanceof LivingEntity && e.isAlive() && !(e instanceof Player p && (p.isSpectator() || p.isCreative()));
	}

	@Override
	public void tick() {
		super.tick();
		if (level() instanceof ServerLevel l && tickCount % 2 == 0)
			l.sendParticles(switch (kind) {
				case 1 -> ParticleTypes.SOUL_FIRE_FLAME;
				case 2 -> ParticleTypes.SPLASH;
				case 3 -> ParticleTypes.CAMPFIRE_COSY_SMOKE;
				default -> ParticleTypes.SNOWFLAKE;
			}, getX(), getY() + 0.5, getZ(), 3, 0.3, 0.3, 0.3, 0.01);
	}

	@Override
	protected void onHitEntity(EntityHitResult hit) {
		super.onHitEntity(hit);
		if (hit.getEntity() instanceof LivingEntity e && e.hurt(damageSources().thrown(this, getOwner()), damage)) {
			switch (kind) {
				case 1 -> {          // the soul in it gets out, and it burns cold
					e.igniteForSeconds(4);
					e.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 100), getOwner());
				}
				case 2 -> {          // the harpoon's rope: hauled back in to him
					if (getOwner() != null) {
						net.minecraft.world.phys.Vec3 in = getOwner().position().subtract(e.position()).multiply(1, 0, 1).normalize();
						e.setDeltaMovement(in.scale(1.6).add(0, 0.4, 0));
						e.hurtMarked = true;
					}
				}
				case 3 -> e.knockback(1.4, -getDeltaMovement().x, -getDeltaMovement().z);
				default -> {
					e.setTicksFrozen(e.getTicksRequiredToFreeze() + 60);
					e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 50, 5), getOwner());
					e.knockback(0.8, -getDeltaMovement().x, -getDeltaMovement().z);
				}
			}
		}
	}

	@Override
	protected void onHit(HitResult hit) {
		super.onHit(hit);
		if (level() instanceof ServerLevel l) {
			l.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, switch (kind) {
				case 1 -> Blocks.SOUL_SOIL.defaultBlockState();
				case 2 -> Blocks.OAK_PLANKS.defaultBlockState();
				case 3 -> Blocks.TERRACOTTA.defaultBlockState();
				default -> Blocks.PACKED_ICE.defaultBlockState();
			}), getX(), getY() + 0.4, getZ(), 40, 0.5, 0.4, 0.5, 0.2);
			if (kind == 0) l.sendParticles(ParticleTypes.SNOWFLAKE, getX(), getY() + 0.4, getZ(), 30, 0.8, 0.5, 0.8, 0.08);
			if (kind == 1) l.sendParticles(ParticleTypes.SOUL, getX(), getY() + 0.6, getZ(), 20, 0.6, 0.5, 0.6, 0.05);
			playSound(switch (kind) {
				case 1 -> SoundEvents.SOUL_ESCAPE.value();
				case 2 -> SoundEvents.TRIDENT_HIT;
				case 3 -> SoundEvents.STONE_BREAK;
				default -> SoundEvents.GLASS_BREAK;
			}, 2.0f, 0.6f);
			Spells.skillFx(l, "quake", position(), net.minecraft.world.phys.Vec3.ZERO, 0.35f, null);
			discard();
		}
	}
}
