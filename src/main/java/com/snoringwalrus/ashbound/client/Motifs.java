package com.snoringwalrus.ashbound.client;

import com.snoringwalrus.ashbound.SpellLook;
import com.snoringwalrus.ashbound.client.SpellParticles.Beam;
import com.snoringwalrus.ashbound.client.SpellParticles.Spike;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.phys.Vec3;

import static com.snoringwalrus.ashbound.client.SpellFx.add;
import static com.snoringwalrus.ashbound.client.SpellFx.flip;
import static com.snoringwalrus.ashbound.client.SpellFx.floor;
import static com.snoringwalrus.ashbound.client.SpellFx.mix;
import static com.snoringwalrus.ashbound.client.SpellFx.pool;
import static com.snoringwalrus.ashbound.client.SpellFx.rand;
import static com.snoringwalrus.ashbound.client.SpellFx.sparks;
import static com.snoringwalrus.ashbound.client.SpellFx.tongues;
import static com.snoringwalrus.ashbound.client.SpellParticles.CRESCENT;
import static com.snoringwalrus.ashbound.client.SpellParticles.FIRE;
import static com.snoringwalrus.ashbound.client.SpellParticles.FLAME;
import static com.snoringwalrus.ashbound.client.SpellParticles.GLOW;
import static com.snoringwalrus.ashbound.client.SpellParticles.HOLE;
import static com.snoringwalrus.ashbound.client.SpellParticles.INK;
import static com.snoringwalrus.ashbound.client.SpellParticles.ROLL;
import static com.snoringwalrus.ashbound.client.SpellParticles.SMOKE;
import static com.snoringwalrus.ashbound.client.SpellParticles.STREAK;

/**
 * One signature per family of skills, so they can be told apart by shape with the colour gone (the rule in tools/blender/vfx_styles.py).
 * A Vanguard's blow is a wall, a Breaker's a fault in the ground, a Headsman's a single thin cut, a Reaver's a black crown of blood, a Lancer's
 * a ruled line, Shade's petals of smoke, venom a cloud that hangs, fire real flame and soot, the void pulls in, and grace rises soft.
 * Each keeps its mass dark or mid-value with the light on the edges, and white stays out of it.
 */
final class Motifs {
	private Motifs() {}

	private static final Vec3 UP = new Vec3(0, 1, 0);
	private static final int WHITE = 0xFFFFFF, BLACK = 0, SOOT = 0x2A2420, ROCK = 0x4A4038;

	private static Vec3 flat(Vec3 dir) {
		Vec3 f = dir.multiply(1, 0, 1);
		return f.lengthSqr() < 1e-4 ? new Vec3(0, 0, 1) : f.normalize();
	}

	/** Vanguard: straight plates going up in a ring, a hard top edge, a thin line round the foot. */
	static void wall(ClientLevel l, Vec3 at, int c, float radius, float high, int life) {
		Vec3 f = floor(l, at);
		int pale = mix(c, WHITE, 0.3f);
		add(new FxKit.Crown(l, f, mix(c, BLACK, 0.2f), radius * 0.98f, radius, high, life, 0.55f));
		add(new FxKit.Decal(l, f.add(0, 0.02, 0), pale, FxKit.RING, radius, life / 2, 0.6f));
		add(new FxKit.Decal(l, f.add(0, 0.02, 0), c, FxKit.RUNE, radius * 0.9f, life, 0.5f));
		FxKit.rising(l, at, pale, radius, 10, 14);
	}

	/** Breaker: the ground splits away from you along a line and throws up slabs of itself, with fire down in the cracks. */
	static void fissure(ClientLevel l, Vec3 at, Vec3 dir, int c, float length, float wide) {
		Vec3 d = flat(dir), side = new Vec3(-d.z, 0, d.x);
		RandomSource r = l.getRandom();
		int n = Math.max(2, (int) (length / 1.5f));
		for (int i = 0; i < n; i++) {
			Vec3 p = at.add(d.scale(i * 1.5f)).add(side.scale((r.nextDouble() - 0.5) * wide));
			FxKit.later(l, i, () -> {
				Vec3 f = floor(l, p);
				FxKit.cracks(l, p, c, 1.7f, 46);
				add(new Spike(l, f.add(0, -0.2, 0), new Vec3((r.nextDouble() - 0.5) * 0.5, 1, (r.nextDouble() - 0.5) * 0.5).scale(0.9 + r.nextDouble() * 1.1), ROCK, 0.3f, 22));
				tongues(l, f, c, FIRE, 2, 0.16);
				FxKit.rocks(l, p, 3, 0.32);
			});
		}
		FxKit.dust(l, at, wide + 1, 6);
	}

	/** The same, out all round. */
	static void shatter(ClientLevel l, Vec3 at, int c, float radius, int arms) {
		float start = l.getRandom().nextFloat() * Mth.TWO_PI;
		for (int i = 0; i < arms; i++) {
			float a = start + i * Mth.TWO_PI / arms;
			fissure(l, at, new Vec3(Mth.cos(a), 0, Mth.sin(a)), c, radius, 0.8f);
		}
		add(new FxKit.Decal(l, floor(l, at).add(0, 0.02, 0), mix(c, WHITE, 0.25f), FxKit.RING, radius, 14, 0.55f));
	}

	/** Headsman: one thin straight line, dark with a lit edge, top to bottom, and nothing else till it's landed. */
	static void cut(ClientLevel l, Vec3 at, int c, float tall, float wide) {
		Vec3 top = at.add(0, tall, 0), down = at.subtract(top);
		add(new Beam(l, top, down, BLACK, wide * 2.2f, 9, 0.9f, null, 1));
		add(new Beam(l, top, down, c, wide, 8, 0.9f, null, 1));
		add(new Beam(l, top, down, mix(c, WHITE, 0.35f), wide * 0.3f, 6, 0.9f, null, 1));
	}

	/** Reaver: a black crown thrown up off the ground with red on its lip, and blood that falls. */
	static void gore(ClientLevel l, Vec3 at, int c, float radius) {
		Vec3 f = floor(l, at);
		add(new FxKit.Crown(l, f, mix(c, BLACK, 0.45f), radius * 0.2f, radius, radius * 0.5f + 0.8f, 20, 0.8f));
		FxKit.ink(l, f.add(0, 0.7, 0), c, (int) (3 + radius), radius * 0.5f, 1.2f, 20);
		FxKit.spray(l, f.add(0, 1, 0), c, (int) (14 + radius * 6), 0.3 + radius * 0.06);
		pool(l, at, mix(c, BLACK, 0.5f), radius, 30, 0.5f);
	}

	/** Steel: thin cuts of wind stacked up through a height, each turned from the last. No smoke, no fire, nothing soft. */
	static void gale(ClientLevel l, Vec3 at, int c, float radius, float high, int cuts) {
		int pale = mix(c, WHITE, 0.3f);
		float start = l.getRandom().nextFloat() * Mth.TWO_PI;
		for (int i = 0; i < cuts; i++) {
			float k = (i + 0.5f) / cuts, a = start + i * 1.9f, tilt = 0.18f * (i % 2 == 0 ? 1 : -1);
			Vec3 u = new Vec3(Mth.cos(a), tilt, Mth.sin(a)).normalize(), v = new Vec3(-Mth.sin(a), -tilt, Mth.cos(a)).normalize();
			Vec3 mid = at.add(0, high * k, 0);
			FxKit.later(l, i, () -> FxKit.slash(l, mid, u, v, mix(c, pale, k), radius * (0.7f + 0.3f * k), 0.3f, 0, Mth.TWO_PI * 0.8f, 8));
		}
		FxKit.streaks(l, at.add(0, high * 0.5f, 0), pale, 6, 0.8, 0.04f, 7, 7, 0);
	}

	/** Lancer: a ruled line with standing rings of air down it. Long, thin, gone. */
	static void needle(ClientLevel l, Vec3 from, Vec3 dir, int c, float length, float wide, int life) {
		Vec3 d = dir.normalize();
		add(new Beam(l, from, d.scale(length), BLACK, wide * 1.6f, life, 0.7f, null, 0.5f));
		add(new Beam(l, from, d.scale(length), c, wide, life, 0.9f, null, 0.5f));
		add(new Beam(l, from, d.scale(length), mix(c, WHITE, 0.35f), wide * 0.25f, life - 2, 0.9f, null, 0.7f));
		FxKit.wake(l, from, d, mix(c, WHITE, 0.3f), length, wide * 2.4f, Math.max(3, (int) (length / 3)));
		Vec3 end = from.add(d.scale(length));
		FxKit.later(l, 3, () -> FxKit.streaks(l, end, mix(c, WHITE, 0.3f), 8, 0.6, 0.04f, 7, 7, 0));
	}

	/** Shade: a slow black bloom with crescents opening off it, and nothing lit but their edges. */
	static void petals(ClientLevel l, Vec3 at, int c, float radius, int n) {
		for (int i = 0; i < n; i++) {
			float a = i * Mth.TWO_PI / n;
			Vec3 out = new Vec3(Mth.cos(a), 0, Mth.sin(a));
			FxKit.later(l, i, () -> {
				add(new FxKit.Pop(l, at.add(out.scale(radius * 0.6f)), BLACK, CRESCENT, radius * 0.5f, radius * 1.1f, 12, a, 0.6f));
				add(new FxKit.Pop(l, at.add(out.scale(radius * 0.6f)), c, CRESCENT, radius * 0.42f, radius * 0.95f, 11, a, 0.6f));
			});
		}
		FxKit.ink(l, at, c, 5, radius * 0.4f, 1.2f, 20);
	}

	/** Venom: a low cloud that sits there, and things dripping and bubbling in it. */
	static void fumes(ClientLevel l, Vec3 at, int c, float radius, int life) {
		RandomSource r = l.getRandom();
		Vec3 f = floor(l, at);
		for (int i = 0; i < (int) (4 + radius * 2); i++) {
			double a = r.nextDouble() * Mth.TWO_PI, far = radius * Math.sqrt(r.nextDouble());
			flip(l, ROLL, SMOKE, mix(c, SOOT, 0.55f), f.add(Math.cos(a) * far, 0.4 + r.nextDouble() * 0.9, Math.sin(a) * far), new Vec3(Math.cos(a) * 0.01, 0.006, Math.sin(a) * 0.01), 1.2f, 2.4f, life);
		}
		pool(l, at, mix(c, BLACK, 0.3f), radius, life, 0.4f);
		for (int i = 0; i < 10; i++) {
			double a = r.nextDouble() * Mth.TWO_PI, far = radius * Math.sqrt(r.nextDouble());
			Vec3 p = f.add(Math.cos(a) * far, 0.1, Math.sin(a) * far);
			FxKit.later(l, r.nextInt(Math.max(1, life / 2)), () -> flip(l, 0, GLOW, c, p, new Vec3(0, 0.05, 0), 0.05f, 0.16f, 14));
		}
	}

	/** Fire that's fire: tongues out of the ground, flames going up, soot over it and embers falling back. */
	static void blaze(ClientLevel l, Vec3 at, int c, float radius) {
		RandomSource r = l.getRandom();
		Vec3 f = floor(l, at);
		tongues(l, f, c, FIRE, (int) (6 + radius * 2), 0.14 + radius * 0.02);
		for (int i = 0; i < (int) (6 + radius * 2); i++) {
			double a = r.nextDouble() * Mth.TWO_PI, far = radius * 0.7 * Math.sqrt(r.nextDouble());
			flip(l, FLAME, FIRE, i % 3 == 0 ? mix(c, 0xFFD060, 0.5f) : c, f.add(Math.cos(a) * far, 0.1, Math.sin(a) * far), new Vec3(0, 0.1 + r.nextDouble() * 0.08, 0), 0.9f, 1.5f, 15).stretched(2);
		}
		for (int i = 0; i < (int) (3 + radius); i++) flip(l, ROLL, SMOKE, SOOT, f.add(rand(r, 1.2).scale(radius * 0.5)).add(0, 1 + radius * 0.3, 0), new Vec3(0, 0.05, 0), 1.2f, 1.2f + radius * 0.5f, 40);
		sparks(l, f.add(0, 0.6, 0), c, (int) (10 + radius * 3), 0.2, -0.01f);
	}

	/** The void: everything goes in. Rings closing, smoke and light dragged to the middle, a hole. */
	static void drawIn(ClientLevel l, Vec3 at, int c, float reach, int ticks) {
		RandomSource r = l.getRandom();
		flip(l, 0, HOLE, c, at, Vec3.ZERO, reach * 0.3f, reach * 0.55f, ticks);
		add(new FxKit.Decal(l, at, mix(c, WHITE, 0.2f), FxKit.RING, reach * 1.5f, ticks, 0.7f).facing(-1).inward());
		for (int i = 0; i < 10; i++) {
			Vec3 d = rand(r, 0), from = at.add(d.scale(reach * (0.7 + r.nextDouble() * 0.5)));
			flip(l, ROLL, INK, c, from, at.subtract(from).scale(1.0 / ticks), 0.7f, 0.2f, ticks);
		}
	}

	/** Grace: a lotus of soft light opening, motes turning up out of it. Round, slow, nothing pointed and nothing thrown. */
	static void grace(ClientLevel l, Vec3 at, int c, float radius) {
		Vec3 f = floor(l, at);
		int pale = mix(c, WHITE, 0.3f);
		add(new FxKit.Crown(l, f, pale, radius * 0.3f, radius, 1 + radius * 0.2f, 26, 0.45f));
		add(new FxKit.Tube(l, f, UP, c, 3 + radius * 0.3f, radius * 0.5f, radius * 0.5f, 0.6f, 34, 0.1f));
		add(new FxKit.Decal(l, f.add(0, 0.03, 0), pale, FxKit.RING, radius * 1.1f, 22, 0.45f));
		for (int i = 0; i < 18; i++) {
			float t = i / 18f, a = t * 6 * Mth.PI;
			Vec3 p = f.add(Mth.cos(a) * radius * 0.6f, 0.3 + t * 3, Mth.sin(a) * radius * 0.6f);
			FxKit.later(l, i, () -> flip(l, 0, GLOW, pale, p, new Vec3(0, 0.02, 0), 0.16f, 0.05f, 16));
		}
	}

	/** Light coming down on one spot from straight above: a thin soft shaft, not a pillar. */
	static void shaft(ClientLevel l, Vec3 at, int c, float tall, float wide, int life) {
		Vec3 f = floor(l, at);
		add(new FxKit.Tube(l, f, UP, c, tall, wide, wide * 0.8f, 0.4f, life, 0.3f));
		add(new Beam(l, f.add(0, tall, 0), new Vec3(0, -tall, 0), mix(c, WHITE, 0.3f), wide * 0.2f, life, 0.7f, null, 0.5f));
	}

	/** Caller: the ground rips, black with a lit lip, and smoke pours out of it. */
	static void tearOpen(ClientLevel l, Vec3 at, int c, float radius) {
		Vec3 f = floor(l, at);
		add(new SpellParticles.Flat(l, f.add(0, 0.02, 0), c, HOLE, radius * 0.8f, 40, 0.02f, 0.8f));
		FxKit.cracks(l, at, c, radius, 60);
		FxKit.ink(l, f.add(0, 0.5, 0), c, (int) (4 + radius), radius * 0.5f, 1.4f, 26);
		FxKit.rocks(l, at, (int) (4 + radius * 2), 0.3);
	}

	/** Cold thin needles in a burst, for anything Hunter. */
	static void frost(ClientLevel l, Vec3 at, int c, int n) {
		FxKit.streaks(l, at, mix(c, WHITE, 0.3f), n, 0.8, 0.035f, 8, 7, 0);
	}

	/** A monster's blow in its dungeon's own stuff: the same family as that dungeon's bolts, at any size. */
	static void burst(ClientLevel l, SpellLook.Family fam, int c, Vec3 at, float r) {
		Vec3 f = floor(l, at);
		switch (fam) {
			case FLAME -> blaze(l, at, c, r);
			case SHARD -> {
				RandomSource rnd = l.getRandom();
				for (int i = 0; i < (int) (6 + r * 2); i++) {
					double a = i * 2.4, far = r * 0.8 * rnd.nextDouble();
					add(new Spike(l, f.add(Math.cos(a) * far, -0.1, Math.sin(a) * far), new Vec3(Math.cos(a) * 0.4, 1, Math.sin(a) * 0.4).scale(1 + rnd.nextDouble() * 1.4), mix(c, WHITE, 0.2f), 0.14f, 24));
				}
				frost(l, f.add(0, 0.8, 0), c, 8);
			}
			case LIGHTNING -> {
				RandomSource rnd = l.getRandom();
				for (int i = 0; i < 5; i++) {
					double a = rnd.nextDouble() * Mth.TWO_PI;
					add(new Beam(l, f.add(0, 0.2, 0), new Vec3(Math.cos(a) * r, 0, Math.sin(a) * r), c, 0.2f, 8, 0.9f, null, 0.7f).lightning());
				}
				add(new Beam(l, f.add(0, 7, 0), new Vec3(0, -7, 0), c, 0.25f, 6, 0.9f, null, 1).lightning());
			}
			case LIQUID -> {
				add(new FxKit.Crown(l, f, c, 0.3f, r, 0.8f + r * 0.4f, 18, 0.7f));
				FxKit.spray(l, f.add(0, 0.8, 0), c, (int) (12 + r * 6), 0.4);
			}
			case ROT -> fumes(l, at, c, r, 34);
			case VOID -> {
				drawIn(l, f.add(0, 0.8, 0), c, r, 10);
				FxKit.later(l, 10, () -> FxKit.ink(l, f.add(0, 0.8, 0), c, 6, r * 0.5f, 1.2f, 20));
			}
			case THREAD -> {
				RandomSource rnd = l.getRandom();
				for (int i = 0; i < 8; i++) {
					double a = rnd.nextDouble() * Mth.TWO_PI;
					add(new Beam(l, f.add(Math.cos(a) * r, 0, Math.sin(a) * r), new Vec3(-Math.cos(a) * r, 2 + rnd.nextDouble() * 2, -Math.sin(a) * r), c, 0.05f, 16, 0.8f, null, 0.2f));
				}
			}
			case HEX -> {
				FxKit.ink(l, f.add(0, 1, 0), c, 7, r * 0.5f, 1.3f, 22);
				SpellFx.tongues(l, f, c, INK, 8, 0.18);
			}
		}
	}

	/** What a monster breathes, in its dungeon's own stuff. Fire is SkillFx.breath's. */
	static void stream(ClientLevel l, SpellLook.Family fam, Vec3 from, Vec3 dir, int c) {
		RandomSource r = l.getRandom();
		Vec3 d = dir.normalize();
		int pale = mix(c, WHITE, 0.3f);
		switch (fam) {
			case SHARD -> {
				for (int i = 0; i < 12; i++) {
					Vec3 p = from.add(d.scale(r.nextDouble() * 5)).add(rand(r, 0).scale(0.5));
					add(new Spike(l, p, d.add(rand(r, 0).scale(0.2)).normalize().scale(1.1), pale, 0.07f, 10));
				}
				for (int i = 0; i < 5; i++) flip(l, ROLL, SMOKE, pale, from.add(d.scale(i * 1.2)), d.scale(0.1), 0.5f, 1.3f, 16);
			}
			case LIGHTNING -> {
				for (int i = 0; i < 4; i++) add(new Beam(l, from, d.add(rand(r, 0).scale(0.25)).normalize().scale(6 + r.nextDouble() * 3), c, 0.18f, 6, 0.85f, null, 0.7f).lightning());
			}
			case LIQUID -> {
				for (int i = 0; i < 18; i++) flip(l, 0, STREAK, i % 4 == 0 ? BLACK : pale, from, d.scale(0.5 + r.nextDouble() * 0.5).add(rand(r, 0).scale(0.1)), 0.1f, 0.03f, 12 + r.nextInt(6)).stretched(5).falls(0.5f);
			}
			case THREAD -> {
				for (int i = 0; i < 6; i++) add(new Beam(l, from, d.add(rand(r, 0).scale(0.18)).normalize().scale(7), c, 0.04f, 14, 0.8f, null, 0.3f));
			}
			default -> {   // rot, void, hex: a rolling dark front with its colour on the edge
				for (int i = 0; i < 9; i++) flip(l, ROLL, INK, c, from.add(d.scale(i * 0.6)), d.scale(0.14).add(rand(r, 0).scale(0.03)), 0.6f, 1.5f + i * 0.08f, 16 + r.nextInt(6));
				if (fam == SpellLook.Family.ROT) for (int i = 0; i < 4; i++) flip(l, ROLL, SMOKE, mix(c, SOOT, 0.55f), from.add(d.scale(2 + i)), d.scale(0.08), 0.8f, 1.8f, 26);
			}
		}
	}

	static void flame(ClientLevel l, Vec3 at, Vec3 dir, int c, float length) {
		RandomSource r = l.getRandom();
		for (int i = 0; i < 22; i++) flip(l, FLAME, FIRE, i % 3 == 0 ? mix(c, 0xFFD060, 0.5f) : c, at.add(dir.scale(r.nextDouble() * length)).add(rand(r, 0).scale(0.4)), dir.scale(0.2).add(rand(r, 0).scale(0.03)), 0.8f, 0.3f, 12).stretched(1.8f);
	}
}
