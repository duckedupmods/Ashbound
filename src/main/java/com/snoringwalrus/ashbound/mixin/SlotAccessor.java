package com.snoringwalrus.ashbound.mixin;

import net.minecraft.world.inventory.Slot;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Mutable;
import org.spongepowered.asm.mixin.gen.Accessor;

/** Lets a screen lay out a menu's slots its own way; only ever used on the client's copy of the menu. */
@Mixin(Slot.class)
public interface SlotAccessor {
	@Mutable
	@Accessor("x")
	void setAshX(int x);

	@Mutable
	@Accessor("y")
	void setAshY(int y);
}
