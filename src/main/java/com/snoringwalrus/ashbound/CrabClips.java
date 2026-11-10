package com.snoringwalrus.ashbound;

import yesman.epicfight.api.animation.AnimationManager;
import yesman.epicfight.api.animation.AnimationManager.AnimationAccessor;
import yesman.epicfight.api.animation.types.AttackAnimation;
import yesman.epicfight.gameasset.Armatures;
import yesman.epicfight.gameasset.ColliderPreset;
import yesman.epicfight.model.armature.SpiderArmature;

/**
 * The crab's own blow on the spider skeleton (tools/crab_clips.py): it stays low and slams both claws forward, where a
 * spider rears up on its back legs to bite (11/7: the Wreck-Mother "attacked like a spider"). Monsters of the "crab"
 * stance (tools/mob_moves.py) swing this for every bite and leap (MobSkills.fits).
 */
public final class CrabClips {
	private CrabClips() {}

	public static AnimationAccessor<AttackAnimation> CLAW;

	static void build(AnimationManager.AnimationBuilder b) {
		CLAW = b.nextAccessor("spider/crab_claw", a -> new AttackAnimation(0.15F, 0.28F, 0.36F, 0.5F, 0.9F, ColliderPreset.SPIDER,
				((SpiderArmature) Armatures.SPIDER.get()).head, a, Armatures.SPIDER));
	}
}
