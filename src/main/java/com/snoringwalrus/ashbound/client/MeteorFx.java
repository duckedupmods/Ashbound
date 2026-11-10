package com.snoringwalrus.ashbound.client;

import com.snoringwalrus.ashbound.Ashfall;
import com.snoringwalrus.ashbound.MeteorShard;

import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * A gate-shard's particles (MeteorShard; the look is tools/blender/meteor_fall.py): falling, a trail of fire going to
 * thick smoke behind the head, sparks and embers shed off it, seen from far off; landed, a smoke column climbing off it
 * for the whole region to see, embers and the odd spit of lava while it's awake.
 */
public final class MeteorFx {
	private MeteorFx() {}

	private static void at(Level l, ParticleOptions o, Vec3 p, double spread, RandomSource r, double vx, double vy, double vz) {
		l.addAlwaysVisibleParticle(o, true, p.x + (r.nextDouble() - 0.5) * spread, p.y + (r.nextDouble() - 0.5) * spread, p.z + (r.nextDouble() - 0.5) * spread, vx, vy, vz);
	}

	public static void tick(MeteorShard s) {
		Level l = s.level();
		RandomSource r = l.getRandom();
		Vec3 base = s.position();
		switch (s.phase()) {
			case MeteorShard.FALLING -> {
				if (s.fallen(0) >= 1) return;
				Vec3 back = s.heading().scale(-1);
				// three steps along this tick's stretch of the path, so the trail has no gaps
				for (int k = 0; k < 3; k++) {
					Vec3 h = base.add(s.head(k / 3f));
					at(l, ParticleTypes.FLAME, h.add(back.scale(2)), 3, r, back.x * 0.25, back.y * 0.25, back.z * 0.25);
					at(l, ParticleTypes.FLAME, h.add(back.scale(5)), 4, r, back.x * 0.15, back.y * 0.15, back.z * 0.15);
					at(l, ParticleTypes.LARGE_SMOKE, h.add(back.scale(8 + r.nextDouble() * 6)), 4, r, 0, 0.02, 0);
					at(l, ParticleTypes.CAMPFIRE_SIGNAL_SMOKE, h.add(back.scale(12 + r.nextDouble() * 20)), 5, r, 0, 0.01, 0);
					at(l, Ashfall.EMBER.get(), h.add(back.scale(4)), 5, r, back.x * 0.3 + (r.nextDouble() - 0.5) * 0.3, back.y * 0.3, back.z * 0.3 + (r.nextDouble() - 0.5) * 0.3);
					if (r.nextFloat() < 0.4f) at(l, ParticleTypes.LAVA, h, 2, r, 0, 0, 0);
				}
				if (r.nextFloat() < 0.5f) at(l, ParticleTypes.CAMPFIRE_COSY_SMOKE, base.add(s.head(0)).add(back.scale(30 + r.nextDouble() * 40)), 8, r, 0, 0.005, 0);
			}
			case MeteorShard.LANDED, MeteorShard.AWAKE -> {
				Vec3 top = base.add(0, 4.5, 0);
				at(l, ParticleTypes.CAMPFIRE_SIGNAL_SMOKE, top, 2.5, r, 0, 0.07 + r.nextDouble() * 0.03, 0);
				if (s.tickCount % 3 == 0) at(l, ParticleTypes.LARGE_SMOKE, base.add(0, 1, 0), 5, r, 0, 0.06, 0);
				if (s.tickCount % 2 == 0) at(l, Ashfall.EMBER.get(), base.add(0, 1.5, 0), 4, r, (r.nextDouble() - 0.5) * 0.05, 0.05 + r.nextDouble() * 0.06, (r.nextDouble() - 0.5) * 0.05);
				if (s.phase() == MeteorShard.AWAKE) {
					at(l, Ashfall.EMBER.get(), base.add(0, 2, 0), 6, r, 0, 0.08, 0);
					if (r.nextFloat() < 0.1f) at(l, ParticleTypes.LAVA, base.add(0, 0.5, 0), 4, r, 0, 0, 0);
					if (r.nextFloat() < 0.3f) at(l, ParticleTypes.ELECTRIC_SPARK, base.add(0, 3, 0), 3, r, 0, 0.05, 0);
				}
			}
			case MeteorShard.SHATTER -> {
				at(l, ParticleTypes.END_ROD, base.add(0, 3, 0), 3, r, (r.nextDouble() - 0.5) * 0.3, r.nextDouble() * 0.2, (r.nextDouble() - 0.5) * 0.3);
				at(l, ParticleTypes.ELECTRIC_SPARK, base.add(0, 3, 0), 3, r, 0, 0.1, 0);
			}
			default -> {
				if (s.tickCount % 4 == 0) at(l, ParticleTypes.CAMPFIRE_COSY_SMOKE, base.add(0, 3, 0), 2, r, 0, 0.03, 0);
			}
		}
	}
}
