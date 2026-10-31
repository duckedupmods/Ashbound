package com.snoringwalrus.ashbound.mixin;

import java.util.ArrayList;
import java.util.List;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import net.minecraft.world.entity.Entity;
import yesman.epicfight.api.animation.Joint;
import yesman.epicfight.api.animation.types.AttackAnimation;
import yesman.epicfight.api.collider.Collider;
import yesman.epicfight.api.collider.MultiCollider;
import yesman.epicfight.world.capabilities.entitypatch.LivingEntityPatch;

/** A swing for a joint the body doesn't have hits nothing. Left alone, Epic Fight throws, and takes the whole server with it. */
@Mixin(value = {Collider.class, MultiCollider.class}, remap = false)
public abstract class ColliderMixin {
	@Inject(method = "updateAndSelectCollideEntity", at = @At("HEAD"), cancellable = true, require = 0)
	private void ashbound$noJoint(LivingEntityPatch<?> patch, AttackAnimation animation, float from, float to, Joint joint, float speed, CallbackInfoReturnable<List<Entity>> ci) {
		if (joint != null && !patch.getArmature().hasJoint(joint.getName())) ci.setReturnValue(new ArrayList<>());
	}
}
