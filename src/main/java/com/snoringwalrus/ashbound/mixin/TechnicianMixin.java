package com.snoringwalrus.ashbound.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import yesman.epicfight.api.event.types.entity.DodgeEvent;
import yesman.epicfight.skill.SkillContainer;
import yesman.epicfight.skill.SkillSlots;
import yesman.epicfight.skill.passive.TechnicianSkill;

/**
 * Technician gives back what the dodge in your dodge slot cost. The skill tree can leave that slot empty, and a hit slipped then
 * threw, inside a monster's tick, and took the whole server down mid boss fight. With nothing there, there's nothing to give back.
 */
@Mixin(value = TechnicianSkill.class, remap = false)
public abstract class TechnicianMixin {
	@Inject(method = "lambda$onInitiate$0", at = @At("HEAD"), cancellable = true)
	private static void ashbound$noDodge(SkillContainer container, DodgeEvent e, CallbackInfo ci) {
		if (container.getExecutor().getSkill(SkillSlots.DODGE).getSkill() == null) ci.cancel();
	}
}
