package com.snoringwalrus.ashbound.client;

import com.snoringwalrus.ashbound.GateMobs;
import net.minecraft.util.Mth;
import org.joml.Quaternionf;
import yesman.epicfight.api.animation.JointTransform;
import yesman.epicfight.api.animation.Pose;
import yesman.epicfight.world.capabilities.entitypatch.LivingEntityPatch;

/**
 * Four legs on a biped: Epic Fight's clips are made for a person, so on a horse every swing would pitch it and plant its
 * feet in a human stance. Every finished pose comes through here (mixin.MountPoseMixin): the body keeps only a share of
 * what the clip does to the hips, none for a mount, so a rider fights from a level saddle, and the legs trot on their own.
 */
public final class MountPose {
	private MountPose() {}

	/** strides per block walked, and how far a leg swings and a knee folds, in radians */
	private static final float CADENCE = 0.8f, SWING = 0.38f, FOLD = 0.6f;

	public static void apply(LivingEntityPatch<?> patch, Pose pose, float partial) {
		if (!(patch instanceof GateMobs.WalkerPatch p)) return;
		GateMobs.Walker e = p.getOriginal();
		Float lean = GateMobs.ON_ALL_FOURS.get(e.kind.id());
		if (lean == null || !e.isAlive()) return;
		pose.putJointData("Root", JointTransform.interpolate(JointTransform.empty(), pose.orElseEmpty("Root"), lean));
		float at = e.walkAnimation.position(partial) * CADENCE, pace = Math.min(1, e.walkAnimation.speed(partial) * 1.5f);
		float swing = Mth.sin(at) * SWING * pace, fold = Mth.cos(at) * FOLD * pace;
		leg(pose, "Thigh_L", "Leg_L", swing, Math.max(0, fold));
		leg(pose, "Thigh_R", "Leg_R", -swing, Math.max(0, -fold));
	}

	/** a leg's joints bind with x to the right: about +x the leg comes forward, about -x the shin folds back */
	private static void leg(Pose pose, String thigh, String shin, float swing, float fold) {
		pose.putJointData(thigh, JointTransform.rotation(new Quaternionf().rotationX(swing)));
		pose.putJointData(shin, JointTransform.rotation(new Quaternionf().rotationX(-fold)));
	}
}
