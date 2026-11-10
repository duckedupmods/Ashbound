package com.snoringwalrus.ashbound.client;

import com.mojang.blaze3d.vertex.VertexConsumer;
import com.snoringwalrus.ashbound.SpellLook;
import com.snoringwalrus.ashbound.client.SpellParticles.Beam;
import com.snoringwalrus.ashbound.client.SpellParticles.Fx;
import com.snoringwalrus.ashbound.client.SpellParticles.Spike;

import net.minecraft.client.Camera;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;

import static com.snoringwalrus.ashbound.client.SpellFx.add;
import static com.snoringwalrus.ashbound.client.SpellFx.flip;
import static com.snoringwalrus.ashbound.client.SpellFx.floor;
import static com.snoringwalrus.ashbound.client.SpellFx.mix;
import static com.snoringwalrus.ashbound.client.SpellFx.pool;
import static com.snoringwalrus.ashbound.client.SpellFx.rand;
import static com.snoringwalrus.ashbound.client.SpellParticles.GLOW;
import static com.snoringwalrus.ashbound.client.SpellParticles.INK;
import static com.snoringwalrus.ashbound.client.SpellParticles.ROLL;
import static com.snoringwalrus.ashbound.client.SpellParticles.SMOKE;
import static com.snoringwalrus.ashbound.client.SpellParticles.STREAK;

/**
 * Every staff style's own shape (StaffSpells.Style), from the concepts in tools/blender/vfx_styles.py. Black is thin, hard and goes one way;
 * white is round, soft and rises, with nothing pointed; a summon is a rip in the world. The colour is the staff's own. Keep the mass dark or
 * mid-value with the light on its edges: nothing here fills the screen, and white only ever goes in a thin line.
 */
final class StyleFx {
	private StyleFx() {}

	private static final int WHITE = 0xFFFFFF, BLACK = 0, GREY = 0x3A3430, EMBER = 0xFF7A2C;
	private static final Vec3 UP = new Vec3(0, 1, 0);

	static void play(ClientLevel l, String what, String gate, Vec3 at, Vec3 dir, float r) {
		int c = SpellLook.colour(gate), pale = mix(c, WHITE, 0.35f);
		Vec3 f = floor(l, at);
		switch (what) {
			case "ring" -> {
				int own = gate.isEmpty() ? EMBER : c;
				Motifs.shatter(l, at, own, r, 4);
				Motifs.burst(l, gate.isEmpty() ? SpellLook.Family.FLAME : SpellLook.of(gate), own, at, r * 0.6f);
				SkillFx.kick(at, 0.5f);
			}
			case "line" -> {
				int own = gate.isEmpty() ? EMBER : c;
				Vec3 waist = at.add(0, 0.4, 0);
				Motifs.needle(l, waist, dir, own, r, 0.45f, 11);
				Motifs.burst(l, gate.isEmpty() ? SpellLook.Family.FLAME : SpellLook.of(gate), own, waist.add(dir.normalize().scale(r)), 1.4f);
				SkillFx.kick(at, 0.3f);
			}
			case "orb" -> FxKit.later(l, 3, () -> {
				if (l.getEntity((int) r) instanceof Entity e) add(new Ringed(l, e, c, true));
			});
			case "flask" -> FxKit.later(l, 3, () -> {
				if (l.getEntity((int) r) instanceof Entity e) add(new Ringed(l, e, pale, false));
			});
			case "orb_burst" -> {
				FxKit.impact(l, at, c, 1.5f);
				FxKit.ink(l, at, c, 6, r * 0.4f, 1.6f, 20);
				FxKit.ring(l, at, pale, r, 14);
				FxKit.rocks(l, at, 8, 0.3);
			}
			case "rune" -> {
				add(new FxKit.Decal(l, f.add(0, 0.02, 0), c, FxKit.RUNE, r, 70, 0.7f).spun(0.004f));
				thorns(l, f, c, r, 8, 0.7f, 60);
				for (int i = 0; i < 3; i++) flip(l, ROLL, SMOKE, mix(c, GREY, 0.8f), f.add(rand(l.getRandom(), 0).multiply(r * 0.6, 0, r * 0.6)).add(0, 0.2, 0), Vec3.ZERO, 0.9f, 1.8f, 50);
			}
			case "rune_burst" -> {
				thorns(l, f, c, r * 0.8f, 12, 2.2f, 16);
				FxKit.impact(l, at, c, 1.1f);
				FxKit.ring(l, at, pale, r, 12);
			}
			case "lance" -> lance(l, at, dir, c, pale, r);
			case "fan" -> {
				Vec3 d = dir.normalize(), side = d.cross(UP).normalize();
				for (int i = -1; i <= 1; i++) {
					Vec3 u = d.yRot(i * 0.42f), v = side.yRot(i * 0.42f);
					FxKit.later(l, Math.abs(i), () -> FxKit.slash(l, at, u, v, c, r, 0.34f, -1.1f, 1.1f, 7));
				}
			}
			case "mark" -> {
				FxKit.ring(l, at, c, r, 34);
				pool(l, at, c, r, 34, 0.3f);
			}
			case "fall" -> add(new FxKit.Meteor(l, f, c, (int) r));
			case "fall_burst" -> {
				FxKit.slam(l, at, c, r, 0.8f);
				FxKit.ink(l, f.add(0, 1, 0), c, 5, 1, 1.8f, 24);
			}
			case "rain" -> rain(l, f, c, pale, r);
			case "mend" -> mend(l, at, c, pale);
			case "spring" -> spring(l, f, c, pale, r);
			case "flask_burst" -> {
				add(new FxKit.Crown(l, f, pale, 0.3f, r * 0.8f, 1.6f, 22, 0.6f));
				add(new FxKit.Decal(l, f.add(0, 0.03, 0), pale, FxKit.RING, r, 18, 0.5f));
				mist(l, f, c, r, 4);
				FxKit.rising(l, at, pale, r, 16, 18);
			}
			case "blades" -> rip(l, f, c, pale, 3.4f, 0.34f);
			case "band" -> {
				rip(l, f, c, pale, 2.8f, 0.24f);
				FxKit.cracks(l, at, c, 1.6f, 40);
			}
			case "mages" -> {
				add(new FxKit.Decal(l, f.add(0, 0.8, 0), c, FxKit.RUNE, 1.1f, 34, 0.8f).spun(0.05f));
				FxKit.ink(l, f.add(0, 0.5, 0), c, 3, 0.4f, 0.6f, 18);
			}
			case "brute" -> {
				FxKit.slam(l, at, c, 3.4f, 1);
				FxKit.ink(l, f.add(0, 0.8, 0), c, 8, 1.3f, 1.5f, 26);
			}
			case "swarm" -> {
				add(new FxKit.Decal(l, f.add(0, 0.03, 0), pale, FxKit.RING, 0.6f, 12, 0.7f));
				FxKit.ink(l, f.add(0, 0.2, 0), c, 3, 0.4f, 0.5f, 16);
			}
			default -> {}
		}
	}

	private static void thorns(ClientLevel l, Vec3 f, int c, float wide, int n, float tall, int life) {
		RandomSource r = l.getRandom();
		for (int i = 0; i < n; i++) {
			float a = i * Mth.TWO_PI / n + r.nextFloat() * 0.3f;
			Vec3 foot = f.add(Mth.cos(a) * wide, 0, Mth.sin(a) * wide), lean = new Vec3(Mth.cos(a) * 0.25, 1, Mth.sin(a) * 0.25);
			add(new Spike(l, foot, lean.scale(tall * (0.7 + r.nextDouble() * 0.5)), mix(c, BLACK, 0.3f), 0.09f, life));
		}
	}

	/** A hard ruled line, and shards of it breaking outwards along its length. */
	private static void lance(ClientLevel l, Vec3 from, Vec3 dir, int c, int pale, float far) {
		Vec3 d = dir.normalize();
		FxKit.lance(l, from, d, c, far, 0.3f, 11);
		RandomSource r = l.getRandom();
		for (int i = 1, n = (int) (far / 2.4f); i <= n; i++) {
			Vec3 at = from.add(d.scale(i * 2.4f)), off = rand(r, 0);
			FxKit.later(l, i, () -> add(new Spike(l, at, d.add(off.scale(0.5)).normalize().scale(1.1 + r.nextDouble()), pale, 0.07f, 14)));
		}
	}

	/** A soft cloud over the spot and slow drops under it, landing in rings. */
	private static void rain(ClientLevel l, Vec3 f, int c, int pale, float wide) {
		RandomSource r = l.getRandom();
		Vec3 top = f.add(0, 4.4, 0);
		for (int i = 0; i < 4; i++) {
			double a = r.nextDouble() * Mth.TWO_PI, far = wide * 0.6 * r.nextDouble();
			flip(l, ROLL, SMOKE, mix(c, GREY, 0.45f), top.add(Math.cos(a) * far, r.nextDouble() * 0.4, Math.sin(a) * far), Vec3.ZERO, 1.6f, 2.6f, 26);
		}
		for (int i = 0; i < 18; i++) {
			double a = r.nextDouble() * Mth.TWO_PI, far = wide * Math.sqrt(r.nextDouble());
			Vec3 drop = top.add(Math.cos(a) * far, -r.nextDouble(), Math.sin(a) * far);
			FxKit.later(l, r.nextInt(10), () -> flip(l, 0, STREAK, pale, drop, new Vec3(0, -0.34, 0), 0.06f, 0.03f, 10).stretched(7).drag(1));
		}
		for (int i = 0; i < 3; i++) {
			double a = r.nextDouble() * Mth.TWO_PI, far = wide * Math.sqrt(r.nextDouble());
			Vec3 at = f.add(Math.cos(a) * far, 0.03, Math.sin(a) * far);
			FxKit.later(l, 9 + r.nextInt(6), () -> add(new FxKit.Decal(l, at, pale, FxKit.RING, 0.6f, 12, 0.5f)));
		}
	}

	/** Light winding up someone in a slow ribbon. */
	private static void mend(ClientLevel l, Vec3 feet, int c, int pale) {
		for (int i = 0; i < 26; i++) {
			float t = i / 26f, a = t * 2.6f * Mth.TWO_PI;
			Vec3 p = feet.add(Mth.cos(a) * 0.65f, t * 2.3f, Mth.sin(a) * 0.65f);
			FxKit.later(l, i, () -> flip(l, 0, GLOW, mix(pale, c, 0.4f), p, new Vec3(0, 0.01, 0), 0.24f, 0.08f, 14));
		}
		FxKit.halo(l, feet, pale, 0.8f, 2.2f, 3);
	}

	/** A low pool that wells up and folds over, the drops falling back round it. */
	private static void spring(ClientLevel l, Vec3 f, int c, int pale, float wide) {
		RandomSource r = l.getRandom();
		pool(l, f, c, wide, 30, 0.22f);
		add(new FxKit.Crown(l, f, pale, 0.15f, wide * 0.45f, 2, 26, 0.5f));
		add(new FxKit.Decal(l, f.add(0, 0.03, 0), pale, FxKit.RING, wide, 24, 0.45f));
		for (int i = 0; i < 12; i++) {
			double a = i * Mth.TWO_PI / 12, s = 0.05 + r.nextDouble() * 0.05;
			flip(l, 0, GLOW, pale, f.add(0, 1.2, 0), new Vec3(Math.cos(a) * s, 0.2, Math.sin(a) * s), 0.14f, 0.05f, 22).falls(0.5f);
		}
		mist(l, f, c, wide * 0.7f, 3);
	}

	private static void mist(ClientLevel l, Vec3 f, int c, float wide, int n) {
		RandomSource r = l.getRandom();
		for (int i = 0; i < n; i++) {
			double a = r.nextDouble() * Mth.TWO_PI, far = wide * r.nextDouble();
			flip(l, ROLL, SMOKE, mix(c, GREY, 0.55f), f.add(Math.cos(a) * far, 0.25, Math.sin(a) * far), new Vec3(Math.cos(a) * 0.02, 0.005, Math.sin(a) * 0.02), 0.8f, 1.7f, 34);
		}
	}

	/** A tall thin tear in the air: nothing in the middle, a lit edge, and it bleeds a little smoke at the foot. */
	private static void rip(ClientLevel l, Vec3 f, int c, int pale, float tall, float wide) {
		Vec3 high = UP.scale(tall);
		add(new Beam(l, f, high, c, wide * 1.7f, 26, 0.75f, null, 0.5f));
		add(new Beam(l, f, high, pale, wide * 1.15f, 22, 0.5f, null, 0.5f));
		add(new Beam(l, f, high, BLACK, wide, 28, 1, null, 0.5f));
		FxKit.ink(l, f.add(0, 0.5, 0), c, 4, 0.3f, 0.7f, 18);
		FxKit.streaks(l, f.add(0, tall * 0.5f, 0), pale, 6, 0.3, 0.04f, 5, 8, 0);
	}

	/** What rides on a lobbed thing for as long as it flies: two rings turning about it, with dark smoke for an orb and soft motes for a flask. */
	private static final class Ringed extends Fx {
		private static final int LONGEST = 200, BEADS = 12;
		final Entity on;
		final int rgb;
		final boolean dark;

		Ringed(ClientLevel l, Entity on, int rgb, boolean dark) {
			super(l, on.position(), rgb);
			this.on = on;
			this.rgb = rgb;
			this.dark = dark;
			lifetime = LONGEST;
		}

		@Override
		public void tick() {
			if (on.isRemoved() || age++ >= lifetime) {
				remove();
				return;
			}
			ClientLevel l = (ClientLevel) level;
			Vec3 mid = on.position().add(0, on.getBbHeight() / 2, 0);
			float turn = age * 0.2f, reach = dark ? 0.85f : 0.4f;
			for (int ring = 0; ring < (dark ? 2 : 1); ring++)
				for (int i = 0; i < BEADS; i++) {
					float a = turn + i * Mth.TWO_PI / BEADS, tilt = ring == 0 ? 0.5f : -0.8f;
					Vec3 p = new Vec3(Mth.cos(a) * reach, Mth.sin(a) * reach * Mth.sin(tilt), Mth.sin(a) * reach * Mth.cos(tilt));
					flip(l, 0, GLOW, rgb, mid.add(p), Vec3.ZERO, 0.09f, 0.03f, 2);
				}
			if (dark) flip(l, ROLL, INK, rgb, mid, Vec3.ZERO, 0.5f, 0.9f, 12);
		}

		@Override
		public void render(VertexConsumer b, Camera cam, float partial) {}
	}
}
