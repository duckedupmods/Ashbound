package com.snoringwalrus.ashbound.client;

import java.util.function.Consumer;

import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.SpellLook;
import com.snoringwalrus.ashbound.Spells;
import com.snoringwalrus.ashbound.Vfx;
import com.snoringwalrus.ashbound.client.SpellParticles.Beam;
import com.snoringwalrus.ashbound.client.SpellParticles.Bound;
import com.snoringwalrus.ashbound.client.SpellParticles.Dome;
import com.snoringwalrus.ashbound.client.SpellParticles.Flat;
import com.snoringwalrus.ashbound.client.SpellParticles.Flip;
import com.snoringwalrus.ashbound.client.SpellParticles.Head;
import com.snoringwalrus.ashbound.client.SpellParticles.Orbit;
import com.snoringwalrus.ashbound.client.SpellParticles.Silk;
import com.snoringwalrus.ashbound.client.SpellParticles.Spike;

import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.Particle;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;

import static com.snoringwalrus.ashbound.client.SpellParticles.BLAST;
import static com.snoringwalrus.ashbound.client.SpellParticles.CIRCLE;
import static com.snoringwalrus.ashbound.client.SpellParticles.FIRE;
import static com.snoringwalrus.ashbound.client.SpellParticles.FLAME;
import static com.snoringwalrus.ashbound.client.SpellParticles.GLOW;
import static com.snoringwalrus.ashbound.client.SpellParticles.HOLE;
import static com.snoringwalrus.ashbound.client.SpellParticles.INK;
import static com.snoringwalrus.ashbound.client.SpellParticles.ROLL;
import static com.snoringwalrus.ashbound.client.SpellParticles.SMOKE;

/**
 * The mage's magic as it looks (concepts: tools/blender/vfx_mage.py): the flash at the staff, each family of bolt in flight
 * and landing, the white school's circle and shafts of light, the summoners' circle and what climbs out of it, the Joined
 * staffs' skills. Drawn here on each client from a word from the server (Net.SpellFx), and from each bolt as it flies.
 */
public final class SpellFx {
	private SpellFx() {}

	private static final int SMOKE_DARK = 0x3A3430, HOLY = 0xFFF0C0;

	public static void hooks() {
		Net.onSpellFx = SpellFx::play;
		Spells.onBolt = SpellFx::trail;
		// SpellParticles draws both faces, and a particle type has nowhere of its own to put that back
		net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener((net.neoforged.neoforge.client.event.RenderLevelStageEvent e) -> {
			if (e.getStage() != net.neoforged.neoforge.client.event.RenderLevelStageEvent.Stage.AFTER_PARTICLES) return;
			Bloom.draw(e.getModelViewMatrix());
			com.mojang.blaze3d.systems.RenderSystem.enableCull();
		});
	}

	private static Minecraft mc() {
		return Minecraft.getInstance();
	}

	static void add(Particle p) {
		mc().particleEngine.add(p);
	}

	static Vec3 rand(RandomSource r, double up) {
		Vec3 v = new Vec3(r.nextGaussian(), r.nextGaussian() + up, r.nextGaussian());
		return v.lengthSqr() < 1e-6 ? new Vec3(0, 1, 0) : v.normalize();
	}

	static Flip flip(ClientLevel l, int sheet, int mode, int rgb, Vec3 at, Vec3 v, float s0, float s1, int life) {
		Flip f = new Flip(l, at, v, rgb, sheet, mode, s0, s1, life, 1);
		add(f);
		return f;
	}

	static void sparks(ClientLevel l, Vec3 at, int rgb, int n, double speed, float gravity) {
		RandomSource r = l.getRandom();
		Vfx.Opt big = Vfx.mote(rgb, 0.05f, 16, gravity), small = Vfx.mote(rgb, 0.025f, 12, gravity);
		for (int i = 0; i < n; i++) {
			Vec3 v = rand(r, 0.4).scale(speed * (0.3 + r.nextDouble()));
			l.addParticle(i % 5 == 0 ? big : small, true, at.x, at.y, at.z, v.x, v.y, v.z);
		}
	}

	/** The ground under a point, for circles and pools. */
	static Vec3 floor(ClientLevel l, Vec3 at) {
		BlockPos.MutableBlockPos p = BlockPos.containing(at).mutable();
		for (int i = 0; i < 8 && l.getBlockState(p).isAir(); i++) p.move(0, -1, 0);
		return new Vec3(at.x, p.getY() + 1.04, at.z);
	}

	static void pool(ClientLevel l, Vec3 at, int rgb, float radius, int life, float peak) {
		add(new Flat(l, floor(l, at), rgb, GLOW, radius, life, 0, peak));
	}

	static void shock(ClientLevel l, Vec3 at, int rgb, float start, float grow, int life) {
		add(new FxKit.Decal(l, floor(l, at), rgb, FxKit.RING, Math.max(0.8f, start + Math.abs(grow) * life), life + 6, 1));
	}

	static void blast(ClientLevel l, Vec3 at, int rgb, float s) {
		FxKit.impact(l, at, rgb, s);
		flip(l, BLAST, FIRE, rgb, at, Vec3.ZERO, 1.1f * s, 2.3f * s, 15);
		RandomSource r = l.getRandom();
		for (int i = 0; i < 7; i++) {
			Vec3 d = rand(r, 0.5);
			flip(l, FLAME, FIRE, rgb, at.add(d.scale(0.5 * s)), d.scale(0.11 * s), 0.55f * s, 0.8f * s, 12).stretched(1.6f);
		}
		for (int i = 0; i < 4; i++) {
			Vec3 d = rand(r, 1.5);
			flip(l, ROLL, SMOKE, SMOKE_DARK, at.add(d.scale(0.7 * s)), d.scale(0.03).add(0, 0.03, 0), 0.8f * s, 1.5f * s, 34);
		}
		pool(l, at, rgb, 3.4f * s, 16, 0.7f);
	}

	// ---------------------------------------------------------------- bolts in flight

	/** Every tick of a bolt, on each client. */
	private static void trail(Spells.Bolt b) {
		ClientLevel l = (ClientLevel) b.level();
		SpellLook.Family fam = SpellLook.of(b.gate());
		int c = SpellLook.colour(b.gate());
		RandomSource r = l.getRandom();
		Vec3 at = b.position().add(0, 0.2, 0), v = b.getDeltaMovement();
		if (!b.dressed) {
			b.dressed = true;
			add(new Head(l, b, c));
			if (fam != SpellLook.Family.HEX && fam != SpellLook.Family.THREAD) add(new FxKit.Comet(l, b, c, fam == SpellLook.Family.LIGHTNING ? FxKit.ARC : FxKit.FLOW, fam == SpellLook.Family.LIQUID));
			if (fam == SpellLook.Family.THREAD && b.getOwner() != null)
				for (int i = 0; i < 4; i++) add(new Silk(l, b.getOwner(), b, c, 0.9f - i * 0.1f, i * Mth.HALF_PI, 0.3f + i * 0.04f));
		}
		if (b.tickCount % 3 == 0) add(new FxKit.Decal(l, at.subtract(v.scale(0.4)), mix(c, 0xFFFFFF, 0.5f), FxKit.RING, 1.1f, 8, 0.55f).across(v));
		switch (fam) {
			case FLAME, ROT -> {
				for (int i = 0; i < 2; i++) {
					Vec3 p = at.subtract(v.scale(i * 0.5 + 0.2)).add(rand(r, 0).scale(0.1));
					flip(l, FLAME, FIRE, c, p, v.scale(0.12).add(rand(r, 0).scale(0.012)), 0.5f, 0.2f, 10).stretched(1.9f);
				}
				if (b.tickCount % 2 == 0) flip(l, ROLL, SMOKE, fam == SpellLook.Family.ROT ? mix(c, SMOKE_DARK, 0.6f) : SMOKE_DARK, at.subtract(v.scale(0.8)), new Vec3(0, 0.02, 0), 0.4f, 1f, 22);
				sparks(l, at, c, fam == SpellLook.Family.ROT ? 3 : 2, 0.05, fam == SpellLook.Family.ROT ? -0.02f : 0.04f);
			}
			case SHARD -> {
				flip(l, ROLL, SMOKE, mix(c, 0xFFFFFF, 0.5f), at.subtract(v.scale(0.5)), Vec3.ZERO, 0.25f, 0.7f, 12);
				sparks(l, at.subtract(v.scale(0.3)), mix(c, 0xFFFFFF, 0.5f), 2, 0.05, 0.03f);
			}
			case LIGHTNING -> {
				Vfx.Opt arc = new Vfx.Opt(c, 0.03f, 3, 0, Vfx.GLOW | Vfx.BOLT);
				for (int i = 0; i < 2; i++) {
					Vec3 d = rand(r, 0).scale(0.8 + r.nextDouble() * 0.9);
					l.addParticle(arc, true, at.x, at.y, at.z, d.x, d.y, d.z);
				}
				if (b.getOwner() != null && b.tickCount % 2 == 0) {
					Vec3 from = tip(b.getOwner()), d = at.subtract(from);
					if (d.lengthSqr() < 400) l.addParticle(new Vfx.Opt(c, 0.04f, 3, 0, Vfx.GLOW | Vfx.BOLT), true, from.x, from.y, from.z, d.x, d.y, d.z);
				}
				sparks(l, at, c, 2, 0.08, 0);
			}
			case LIQUID -> {
				flip(l, ROLL, SMOKE, mix(c, 0xFFFFFF, 0.3f), at.subtract(v.scale(0.6)), Vec3.ZERO, 0.3f, 0.9f, 14);
				FxKit.streaks(l, at.subtract(v.scale(0.4)), mix(c, 0xFFFFFF, 0.5f), 2, 0.12, 0.05f, 5, 6, 0);
			}
			case HEX -> {
				for (int i = 0; i < 3; i++) {
					Vec3 p = at.subtract(v.scale(i * 0.45 + 0.1)).add(rand(r, 0).scale(0.12 + i * 0.05));
					flip(l, FLAME, INK, c, p, v.scale(0.1), 0.62f - i * 0.08f, 0.3f, 15).stretched(1.9f);
				}
				if (b.tickCount % 2 == 0) flip(l, ROLL, INK, c, at.subtract(v.scale(0.9)), new Vec3(0, 0.015, 0), 0.4f, 0.8f, 18);
				sparks(l, at, c, 2, 0.06, -0.01f);
			}
			case VOID -> {
				if (b.tickCount % 3 == 0) add(new Orbit(l, at, 0.75f, r.nextFloat() * Mth.TWO_PI, 0.5f, c, 0.3f, 9));
				flip(l, FLAME, FIRE, c, at.subtract(v.scale(0.6)), v.scale(0.1), 0.24f, 0.1f, 9).stretched(1.8f);
				Vfx.Opt in = Vfx.mote(c, 0.03f, 9, 0);
				for (int i = 0; i < 3; i++) {
					Vec3 d = rand(r, 0), p = at.add(d.scale(1.4));
					l.addParticle(in, true, p.x, p.y, p.z, v.x - d.x * 0.15, v.y - d.y * 0.15, v.z - d.z * 0.15);
				}
			}
			case THREAD -> sparks(l, at, c, 2, 0.04, 0.01f);
		}
	}

	static int mix(int a, int b, float k) {
		int r = (int) Mth.lerp(k, a >> 16 & 255, b >> 16 & 255), g = (int) Mth.lerp(k, a >> 8 & 255, b >> 8 & 255), bl = (int) Mth.lerp(k, a & 255, b & 255);
		return r << 16 | g << 8 | bl;
	}

	/** About where someone's staff ends. */
	private static Vec3 tip(Entity e) {
		return tip(e, 1);
	}

	static Vec3 tip(Entity e, float partial) {
		Vec3 look = e.getViewVector(partial), right = look.cross(new Vec3(0, 1, 0));
		right = right.lengthSqr() < 1e-4 ? new Vec3(1, 0, 0) : right.normalize();
		return e.getEyePosition(partial).add(look.scale(0.7)).add(right.scale(0.35)).add(0, -0.2, 0);
	}

	// ---------------------------------------------------------------- what lands

	static void hit(ClientLevel l, SpellLook.Family fam, int c, Vec3 at, Entity on) {
		RandomSource r = l.getRandom();
		switch (fam) {
			case FLAME -> {
				blast(l, at, c, 1.2f);
				shock(l, at, c, 0.6f, 0.2f, 12);
				FxKit.cracks(l, at, c, 2.8f, 50);
				FxKit.later(l, 2, () -> tongues(l, at, c, FIRE, 9, 0.16));
			}
			case SHARD -> {
				FxKit.impact(l, at, mix(c, 0xFFFFFF, 0.3f), 0.9f);
				Vec3 f = floor(l, at).add(0, -0.1, 0);
				for (int i = 0; i < 20; i++) {
					double a = r.nextDouble() * Mth.TWO_PI, d = 0.2 + r.nextDouble() * 2.2;
					Vec3 foot = f.add(Math.cos(a) * d, 0, Math.sin(a) * d);
					Vec3 axis = new Vec3(Math.cos(a) * 0.5, 1, Math.sin(a) * 0.5).normalize().scale((2.8 - d) * (0.8 + r.nextDouble() * 0.7) + 0.4);
					add(new Spike(l, foot, axis, c, 0.12f + 0.16f * (float) (2.4 - d) / 2.4f, 24 + r.nextInt(14)));
				}
				for (int i = 0; i < 6; i++) flip(l, ROLL, SMOKE, mix(c, 0xFFFFFF, 0.6f), f.add(rand(r, 0).multiply(1.2, 0, 1.2)).add(0, 0.3, 0), Vec3.ZERO, 0.6f, 1.2f, 22);
				shock(l, at, c, 1.2f, 0.12f, 12);
				pool(l, at, c, 2.8f, 22, 0.55f);
				FxKit.later(l, 22, () -> {   // and it all breaks
					add(new FxKit.Pop(l, f.add(0, 1, 0), mix(c, 0xFFFFFF, 0.5f), SpellParticles.STAR, 1.8f, 1.2f, 3, r.nextFloat() * Mth.TWO_PI, 0));
					FxKit.streaks(l, f.add(0, 1, 0), mix(c, 0xFFFFFF, 0.6f), 22, 0.8, 0.06f, 4, 8, 0.6);
				});
			}
			case LIGHTNING -> {
				FxKit.impact(l, at, c, 1);
				Vec3 f = floor(l, at);
				for (int i = 0; i < 3; i++)   // it strikes three times
					FxKit.later(l, i * 2, () -> {
						Vec3 sky = at.add(r.nextDouble() - 0.5, 12, r.nextDouble() - 0.5);
						add(new Beam(l, sky, at.subtract(sky), mix(c, 0xFFFFFF, 0.5f), 0.55f, 5, 1, null, 1).lightning());
						FxKit.flare(l, at, c, 2.8f, 3);
					});
				for (int i = 0; i < 7; i++) {
					double a = r.nextDouble() * Mth.TWO_PI;
					add(new Beam(l, at, new Vec3(Math.cos(a) * 2.2, f.y - at.y, Math.sin(a) * 2.2), c, 0.3f, 7 + i, 1, null, 0.8f).lightning());
				}
				FxKit.cracks(l, at, c, 2.4f, 40);
				shock(l, at, c, 0.5f, 0.2f, 10);
				pool(l, at, c, 3.4f, 12, 0.8f);
			}
			case LIQUID -> {
				FxKit.impact(l, at, c, 0.8f);
				Vec3 f = floor(l, at);
				int pale = mix(c, 0xFFFFFF, 0.25f);
				add(new FxKit.Crown(l, f, pale, 0.4f, 2.3f, 3, 20, 1));
				add(new FxKit.Crown(l, f, pale, 0.25f, 1.4f, 3.8f, 16, 0.8f));
				FxKit.streaks(l, f.add(0, 0.6, 0), pale, 26, 0.9, 0.05f, 5, 12, 1.4);
				for (int i = 0; i < 8; i++) {   // and it hangs as mist, not drops
					double a = i * Mth.TWO_PI / 8;
					flip(l, ROLL, SMOKE, mix(c, 0xFFFFFF, 0.3f), f.add(Math.cos(a) * 1.5, 0.5 + r.nextDouble(), Math.sin(a) * 1.5), new Vec3(Math.cos(a) * 0.05, 0.01, Math.sin(a) * 0.05), 0.7f, 1.6f, 26);
				}
				shock(l, at, c, 0.8f, 0.2f, 12);
				pool(l, at, c, 3, 16, 0.5f);
			}
			case ROT -> {
				FxKit.impact(l, at, c, 0.9f);
				for (int i = 0; i < 12; i++) {   // the stalk going up, black with a sick rim
					Vec3 p = at.add(rand(r, 0).multiply(0.35, 0, 0.35)).add(0, i * 0.08, 0);
					flip(l, ROLL, INK, c, p, new Vec3(0, 0.1 + i * 0.012, 0), 0.6f, 1.2f, 22 + i);
				}
				for (int i = 0; i < 12; i++) {   // the head rolling out at the top
					double a = i * Mth.TWO_PI / 12;
					flip(l, ROLL, INK, c, at.add(0, 2.2, 0), new Vec3(Math.cos(a) * 0.075, 0.035, Math.sin(a) * 0.075), 0.7f, 1.6f, 34);
				}
				Vfx.Opt spore = Vfx.mote(mix(c, 0xFFFFFF, 0.5f), 0.02f, 40, -0.01f);
				for (int i = 0; i < 40; i++) {
					Vec3 v = rand(r, 0.8).scale(0.04 + r.nextDouble() * 0.08);
					l.addParticle(spore, true, at.x, at.y + 0.6, at.z, v.x, v.y, v.z);
				}
				FxKit.cracks(l, at, c, 2.4f, 60);
			}
			case VOID -> {
				Vec3 mid = at.add(0, 0.3, 0);
				add(new Flip(l, mid, Vec3.ZERO, c, 0, HOLE, 2.6f, 1.2f, 12, 1));
				add(new Flip(l, mid, Vec3.ZERO, c, 0, GLOW, 4f, 4.6f, 14, 0.5f));
				add(new FxKit.Decal(l, mid, c, FxKit.SWIRL, 3.4f, 12, 0.9f).facing(0.3f));
				for (int i = 0; i < 18; i++) add(new Orbit(l, mid, 1.3f + r.nextFloat() * 0.8f, r.nextFloat() * Mth.TWO_PI, 0.55f, c, 0.55f, 12));
				Vfx.Opt in = Vfx.mote(c, 0.04f, 10, 0);
				for (int i = 0; i < 50; i++) {
					Vec3 d = rand(r, 0), p = mid.add(d.scale(2 + r.nextDouble() * 1.8)), v = d.scale(-0.34);
					l.addParticle(in, true, p.x, p.y, p.z, v.x, v.y, v.z);
				}
				shock(l, at, c, 3.4f, -0.14f, 10);
				FxKit.later(l, 10, () -> {   // it takes it all in, then gives it back bigger
					blast(l, mid, c, 1.5f);
					pool(l, at, c, 4.4f, 20, 0.7f);
				});
			}
			case THREAD -> {
				FxKit.impact(l, at, c, 0.7f);
				if (on != null) add(new Bound(l, on, c, 50));
				Vec3 f = floor(l, at);
				for (int i = 0; i < 8; i++) {
					double a = r.nextDouble() * Mth.TWO_PI;
					add(new Beam(l, at, new Vec3(Math.cos(a) * 2.2, f.y - at.y, Math.sin(a) * 2.2), c, 0.035f, 34, 0.9f, null, 1));
				}
				pool(l, at, c, 2.4f, 18, 0.45f);
			}
			case HEX -> {
				FxKit.impact(l, at, c, 1.1f);
				Vec3 f = floor(l, at);
				FxKit.rune(l, at, mix(c, 0, 0.35f), 2.6f, 30);
				FxKit.cracks(l, at, c, 2.8f, 60);
				FxKit.later(l, 1, () -> {
					flip(l, BLAST, INK, c, f.add(0, 1.1, 0), new Vec3(0, 0.04, 0), 1.2f, 2.4f, 20);
					tongues(l, f.add(0, 0.5, 0), c, INK, 12, 0.22);
				});
			}
		}
	}

	/** Flames standing up out of a blow and leaning outward, which is what keeps it from being a splat on the floor. */
	static void tongues(ClientLevel l, Vec3 at, int c, int mode, int n, double speed) {
		RandomSource r = l.getRandom();
		for (int i = 0; i < n; i++) {
			double a = i * Mth.TWO_PI / n + r.nextDouble() * 0.4, lean = 0.2 + r.nextDouble() * 0.5;
			Vec3 d = new Vec3(Math.cos(a) * lean, 1, Math.sin(a) * lean).normalize();
			flip(l, FLAME, mode, c, at.add(d.scale(0.4)), d.scale(speed * (0.6 + r.nextDouble() * 0.7)), 0.9f, 1.2f, 18 + r.nextInt(8)).stretched(2.3f).drag(0.9f);
		}
	}

	private static void overload(ClientLevel l, int c, Vec3 at) {
		RandomSource r = l.getRandom();
		FxKit.impact(l, at, c, 3);
		flip(l, BLAST, FIRE, c, at, Vec3.ZERO, 2.4f, 5.4f, 20);
		flip(l, BLAST, FIRE, mix(c, 0xFFFFFF, 0.3f), at, Vec3.ZERO, 1.2f, 3.2f, 13);
		for (int i = 0; i < 16; i++) {
			Vec3 d = rand(r, 0.6);
			flip(l, FLAME, FIRE, c, at.add(d), d.scale(0.22), 1.1f, 1.7f, 15).stretched(1.8f);
		}
		for (int i = 0; i < 12; i++) flip(l, ROLL, SMOKE, SMOKE_DARK, at.add(rand(r, 1.5).scale(1.6)), new Vec3(0, 0.06, 0), 1.3f, 2.8f, 50);
		Vec3 f = floor(l, at);
		for (int i = 0; i < 24; i++) {   // the dust thrown out along the ground
			double a = i * Mth.TWO_PI / 24;
			flip(l, ROLL, SMOKE, 0x8A7A68, f.add(Math.cos(a), 0.3, Math.sin(a)), new Vec3(Math.cos(a) * 0.3, 0.012, Math.sin(a) * 0.3), 0.7f, 1.6f, 22);
		}
		sparks(l, at, c, 70, 0.75, 0.05f);
		shock(l, at, c, 0.8f, 0.42f, 16);
		pool(l, at, c, 8, 22, 0.9f);
	}

	// ---------------------------------------------------------------- the white school

	private static void healCircle(ClientLevel l, Vec3 at, int c, float reach, int life) {
		Vec3 f = floor(l, at);
		int pale = mix(c, 0xFFFFFF, 0.6f);
		add(new Flat(l, f, c, CIRCLE, reach, life, 0.012f, 1));
		add(new Flat(l, f, c, GLOW, reach * 1.2f, life, 0, 0.32f));
		add(new FxKit.Tube(l, f, new Vec3(0, 1, 0), c, 2.2f, reach, reach, 0.6f, Math.min(life, 40), 0.22f));
		for (int i = 0; i * 12 < life; i++)   // it breathes out in rings for as long as it stands
			FxKit.later(l, i * 12, () -> add(new FxKit.Decal(l, f.add(0, 0.03, 0), pale, FxKit.RING, reach, 18, 0.8f)));
		FxKit.flare(l, f.add(0, 0.6, 0), c, reach * 0.7f, 8);
		FxKit.rising(l, at, pale, reach, 18 + (int) reach * 4, 18);
		sparks(l, f.add(0, 0.3, 0), pale, 16, 0.12, -0.02f);
	}

	private static void shaftOn(ClientLevel l, Entity on, int c) {
		Vec3 at = on.position();
		FxKit.column(l, at, mix(c, HOLY, 0.3f), 6, 0.8f, 24, on);
		Vec3 f = floor(l, at);
		add(new Flat(l, f, c, GLOW, 1.5f, 22, 0, 0.8f));
		add(new FxKit.Pop(l, at.add(0, on.getBbHeight() * 0.55, 0), mix(c, 0xFFFFFF, 0.3f), SpellParticles.STAR, 1.6f, 0.8f, 3, l.getRandom().nextFloat() * Mth.TWO_PI, 0));
		FxKit.halo(l, at, mix(c, 0xFFFFFF, 0.6f), on.getBbWidth() + 0.8f, on.getBbHeight() * 1.2f, 4);
		FxKit.rising(l, at, mix(c, 0xFFFFFF, 0.6f), 0.8f, 14, 16);
	}

	private static void lance(ClientLevel l, Entity on, int c) {
		Vec3 at = on.position();
		Vec3 mid = at.add(0, on.getBbHeight() * 0.5, 0);
		FxKit.column(l, at, c, 11, 0.7f, 14, on);
		FxKit.impact(l, mid, mix(c, HOLY, 0.4f), 0.8f);
		FxKit.cracks(l, at, c, 2, 40);
		shock(l, at, c, 0.4f, 0.13f, 10);
		pool(l, at, c, 2.2f, 12, 0.8f);
	}

	// ---------------------------------------------------------------- the summoners

	/** Something climbing out of the ground: a black tear, black fire up out of it, and the earth thrown off. */
	static void rise(ClientLevel l, Vec3 at, int c) {
		Vec3 f = floor(l, at);
		add(new Flat(l, f.add(0, 0.03, 0), c, HOLE, 1.8f, 34, 0.02f, 1));
		FxKit.gather(l, f.add(0, 0.8, 0), c, 1.6f, 6);
		FxKit.later(l, 6, () -> {
			FxKit.impact(l, f.add(0, 0.8, 0), c, 0.7f);
			tongues(l, f.add(0, 0.3, 0), c, INK, 10, 0.2);
			FxKit.ink(l, f.add(0, 0.6, 0), c, 5, 0.6f, 1.2f, 22);
			FxKit.rocks(l, at, 10, 0.3);
			FxKit.streaks(l, f.add(0, 0.3, 0), mix(c, 0xFFFFFF, 0.4f), 12, 0.7, 0.06f, 7, 9, 3);
			shock(l, at, c, 0.85f, 0.1f, 14);
		});
		pool(l, at, c, 2.2f, 28, 0.8f);
	}

	private static void summonCircle(ClientLevel l, Vec3 at, int c, float reach) {
		Vec3 f = floor(l, at);
		add(new Flat(l, f, c, CIRCLE, reach, 46, -0.018f, 1));
		add(new Flat(l, f, c, GLOW, reach * 1.2f, 46, 0, 0.4f));
		add(new Flat(l, f.add(0, 0.02, 0), c, HOLE, reach * 0.75f, 46, 0.03f, 0.85f));
		add(new FxKit.Decal(l, f, c, FxKit.SWIRL, reach * 0.9f, 46, 0.7f).spun(0.02f));
		add(new FxKit.Tube(l, f, new Vec3(0, 1, 0), c, 2.6f, reach, reach * 0.8f, 1.4f, 40, 0.3f));
		FxKit.ink(l, f.add(0, 0.5, 0), c, 8, reach * 0.5f, 1.3f, 26);
		for (int i = 0; i < 3; i++) FxKit.later(l, i * 8, () -> FxKit.ring(l, at, mix(c, 0xFFFFFF, 0.5f), reach * 1.1f, 14));
	}

	// ---------------------------------------------------------------- from the server

	private static void play(Net.SpellFx m) {
		ClientLevel l = mc().level;
		if (l == null) return;
		Vec3 at = new Vec3(m.at());
		int c = SpellLook.colour(m.gate());
		Entity e = m.on() >= 0 ? l.getEntity(m.on()) : null;
		switch (m.kind()) {
			case Spells.FX_CAST -> {
				Vec3 tip = e != null ? tip(e) : at;
				flip(l, BLAST, FIRE, c, tip, Vec3.ZERO, 0.28f * m.r(), 0.6f * m.r(), 7);
				add(new Flip(l, tip, Vec3.ZERO, c, 0, GLOW, 1.1f * m.r(), 1.2f * m.r(), 7, 0.6f));
				FxKit.flare(l, tip, c, 1.3f * m.r(), 5);
				add(new FxKit.Pop(l, tip, c, SpellParticles.STAR, 0.8f * m.r(), 0.4f * m.r(), 3, l.getRandom().nextFloat() * Mth.TWO_PI, 0));
				if (e != null) add(new FxKit.Decal(l, tip, mix(c, 0xFFFFFF, 0.5f), FxKit.RING, 1.2f * m.r(), 7, 0.8f).across(e.getLookAngle()));
				sparks(l, tip, c, (int) (8 * m.r()), 0.14, 0.03f);
			}
			case Spells.FX_HIT -> hit(l, SpellLook.of(m.gate()), c, at, e);
			case Spells.FX_OVERLOAD -> overload(l, c, at);
			case Spells.FX_HEAL -> healCircle(l, at, c, m.r(), 30);
			case Spells.FX_BLESS -> {
				if (e != null) shaftOn(l, e, c);
			}
			case Spells.FX_LANCE -> {
				if (e != null) lance(l, e, c);
			}
			case Spells.FX_WARD -> healCircle(l, at, c, m.r(), 80);
			case Spells.FX_GUARD -> {
				if (e != null) {
					add(new Dome(l, e.position(), c, 1.6f, 16));
					FxKit.halo(l, e.position(), mix(c, 0xFFFFFF, 0.5f), e.getBbWidth() + 1, e.getBbHeight(), 3);
					FxKit.flare(l, e.position().add(0, 1, 0), c, 1.6f, 6);
				}
			}
			case Spells.FX_SUMMON -> summonCircle(l, at, c, m.r());
			case Spells.FX_RISE -> rise(l, at, c);
			case Spells.FX_GONE -> {
				FxKit.ink(l, at.add(0, 0.8, 0), c, 7, 0.5f, 1.1f, 20);
				FxKit.streaks(l, at.add(0, 0.8, 0), mix(c, 0xFFFFFF, 0.4f), 10, 0.5, 0.05f, 5, 8, 0.8);
				sparks(l, at.add(0, 0.8, 0), c, 14, 0.2, -0.02f);
			}
			case Spells.FX_GREAT_HEAL -> {
				healCircle(l, at, c, m.r(), 70);
				add(new Dome(l, floor(l, at), c, m.r(), 70));
				FxKit.column(l, at, mix(c, HOLY, 0.4f), 16, 2, 26, null);
			}
			default -> {}
		}
	}
}
