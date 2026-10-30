package com.snoringwalrus.ashbound;

import yesman.epicfight.api.utils.math.OpenMatrix4f;
import yesman.epicfight.world.capabilities.entitypatch.mob.ZombiePatch;

/**
 * How Epic Fight fights the Cinderhusk: like its zombies (the undead faction, fighting with whatever it holds),
 * drawn at its own size. Its mesh (tools/efmob.py) is fitted to the player-sized biped skeleton, so it is
 * scaled back up here.
 */
public class CinderhuskPatch extends ZombiePatch<Cinderhusk> {
	/** tools/efmob.py's "scale back", a little under so it isn't taller than its hitbox. */
	static final float SCALE = 1.6f;

	public CinderhuskPatch(Cinderhusk original) {
		super(original);
	}

	@Override
	public OpenMatrix4f getModelMatrix(float partialTicks) {
		return super.getModelMatrix(partialTicks).scale(SCALE, SCALE, SCALE);
	}
}
