package com.snoringwalrus.ashbound;

import net.minecraft.world.entity.ai.goal.RangedBowAttackGoal;
import yesman.epicfight.api.animation.AnimationManager;
import yesman.epicfight.api.animation.Animator;
import yesman.epicfight.api.animation.types.StaticAnimation;
import yesman.epicfight.gameasset.Armatures;
import yesman.epicfight.api.animation.LivingMotions;
import yesman.epicfight.api.utils.math.OpenMatrix4f;
import yesman.epicfight.gameasset.Animations;
import yesman.epicfight.world.capabilities.entitypatch.Factions;
import yesman.epicfight.world.capabilities.entitypatch.HumanoidMobPatch;
import yesman.epicfight.world.entity.ai.goal.AnimatedAttackGoal;

/**
 * How Epic Fight moves an adventurer: on its biped like a player, swinging their real weapon's moves (MobMoves' stance for it)
 * from their own place round the target, or drawing a bow, or casting; drawn at their own size, like the townsfolk.
 */
public class AdventurerPatch extends HumanoidMobPatch<Adventurer> {
	/** The dead of a fallen party, lying still: on the back, face down, curled on a side (tools/fallen_pose.py). Played under
	 * living motions no mob of ours uses otherwise. */
	public static AnimationManager.AnimationAccessor<StaticAnimation> BACK, FRONT, SIDE;
	private static final LivingMotions[] LYING = {LivingMotions.SLEEP, LivingMotions.ADMIRE, LivingMotions.SPECTATE};

	static void build(AnimationManager.AnimationBuilder b) {
		BACK = b.nextAccessor("biped/fallen_back", a -> new StaticAnimation(true, a, Armatures.BIPED));
		FRONT = b.nextAccessor("biped/fallen_front", a -> new StaticAnimation(true, a, Armatures.BIPED));
		SIDE = b.nextAccessor("biped/fallen_side", a -> new StaticAnimation(true, a, Armatures.BIPED));
	}

	public AdventurerPatch(Adventurer original) {
		super(original, Factions.NEUTRAL);
	}

	@Override
	public void initAnimator(Animator animator) {
		super.initAnimator(animator);
		commonAggresiveMobAnimatorInit(animator);
		animator.addLivingAnimation(LivingMotions.CHASE, Animations.BIPED_RUN);
		animator.addLivingAnimation(LYING[0], BACK);
		animator.addLivingAnimation(LYING[1], FRONT);
		animator.addLivingAnimation(LYING[2], SIDE);
	}

	@Override
	public void updateMotion(boolean considerInaction) {
		int f = original.fallen();
		if (f > 0) {
			currentLivingMotion = LYING[Math.min(f, 3) - 1];
			currentCompositeMotion = currentLivingMotion;
			return;
		}
		if (original.fights.equals("bow")) commonAggressiveRangedMobUpdateMotion(considerInaction);
		else commonAggressiveMobUpdateMotion(considerInaction);
	}

	@Override
	public void setAIAsInfantry(boolean holdingRangedWeapon) {
		original.goalSelector.getAvailableGoals().removeIf(w -> w.getGoal() instanceof Adventurer.Surround || w.getGoal() instanceof Adventurer.Cast
				|| w.getGoal() instanceof RangedBowAttackGoal || w.getGoal() instanceof AnimatedAttackGoal);
		switch (original.fights) {
			case "bow" -> {
				original.goalSelector.addGoal(1, new RangedBowAttackGoal<>(original, 1.0, 22, 16f));
			}
			case "black", "white" -> original.goalSelector.addGoal(1, original.new Cast());
			default -> {
				original.goalSelector.addGoal(0, new AnimatedAttackGoal<>(this, MobMoves.<HumanoidMobPatch<?>>behaviours(original, original.fights).build(this)));
				original.goalSelector.addGoal(1, original.new Surround());
			}
		}
	}

	@Override
	public OpenMatrix4f getModelMatrix(float partialTicks) {
		float s = (float) Npc.SCALE.applyAsDouble(original.kindId());
		return super.getModelMatrix(partialTicks).scale(s, s, s);
	}
}
