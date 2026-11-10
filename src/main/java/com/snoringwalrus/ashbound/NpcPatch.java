package com.snoringwalrus.ashbound;

import yesman.epicfight.api.animation.AnimationManager;
import yesman.epicfight.api.animation.Animator;
import yesman.epicfight.api.animation.types.StaticAnimation;
import yesman.epicfight.gameasset.Armatures;
import yesman.epicfight.api.animation.LivingMotions;
import yesman.epicfight.gameasset.Animations;
import yesman.epicfight.api.utils.math.OpenMatrix4f;
import yesman.epicfight.world.capabilities.entitypatch.Factions;
import yesman.epicfight.world.capabilities.entitypatch.HumanoidMobPatch;

/**
 * How Epic Fight animates a townsperson: on its biped, breathing, walking, falling like anyone else, never
 * fighting (none of its attack goals are given them). Each kind's mesh is fitted to the player-sized skeleton
 * (tools/efmob.py --npc), so it's drawn back at its own size here: a child small, a smith broad.
 */
public class NpcPatch extends HumanoidMobPatch<Npc> {
	/** Sat on a chair or a bench: Epic Fight's sit is for boats (legs out, feet up), this one's thighs are on the
	 * seat and the shins go down to the floor (assets/ashbound/animmodels/animations/biped/npc_sit.json, made by
	 * tools/npc_sit.py from Epic Fight's idle and sit), the head free to turn to a neighbour. */
	public static AnimationManager.AnimationAccessor<StaticAnimation> SIT;

	static void build(AnimationManager.AnimationBuilder b) {
		SIT = b.nextAccessor("biped/npc_sit", a -> new StaticAnimation(true, a, Armatures.BIPED));
		Smithing.build(b);
		CrabClips.build(b);
		AdventurerPatch.build(b);
	}

	public NpcPatch(Npc original) {
		super(original, Factions.NEUTRAL);
	}

	@Override
	protected void initAI() {}

	@Override
	public void initAnimator(Animator animator) {
		super.initAnimator(animator);
		commonMobAnimatorInit(animator);
		animator.addLivingAnimation(LivingMotions.SIT, SIT);
		animator.addLivingAnimation(LivingMotions.KNEEL, Animations.BIPED_KNEEL);
		animator.addLivingAnimation(LivingMotions.RUN, Animations.BIPED_RUN);
	}

	/** Walking and standing as any mob, and what Npc.act says beyond: sat on a bench, knelt, running about. */
	@Override
	public void updateMotion(boolean considerInaction) {
		commonMobUpdateMotion(considerInaction);
		if (currentLivingMotion == LivingMotions.DEATH || currentLivingMotion == LivingMotions.INACTION) return;
		switch (original.act()) {
			case Npc.POSE_SIT -> currentLivingMotion = LivingMotions.SIT;
			case Npc.POSE_KNEEL -> currentLivingMotion = LivingMotions.KNEEL;
			case Npc.POSE_RUN -> {
				if (currentLivingMotion == LivingMotions.WALK) currentLivingMotion = LivingMotions.RUN;
			}
			default -> {}
		}
		currentCompositeMotion = currentLivingMotion;
	}

	@Override
	public OpenMatrix4f getModelMatrix(float partialTicks) {
		float s = (float) Npc.SCALE.applyAsDouble(original.kindId());
		OpenMatrix4f m = super.getModelMatrix(partialTicks);
		// sat down the server sets them as if grown-up sized: a smaller body has its hips raised to the seat again
		if (original.act() == Npc.POSE_SIT && s != 1f) m.translate(0, (float) (NpcLife.SIT_DROP * (1 - s)), 0);
		return m.scale(s, s, s);
	}
}
