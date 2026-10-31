package com.snoringwalrus.ashbound.mixin;

import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** A mount jumps when its rider presses jump; see Mount.tickRidden. */
@Mixin(LivingEntity.class)
public interface JumpingAccessor {
	@Accessor("jumping")
	boolean ashbound$jumping();
}
