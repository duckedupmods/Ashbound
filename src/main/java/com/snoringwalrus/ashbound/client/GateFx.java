package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.GateEntity;
import com.snoringwalrus.ashbound.GateScorch;
import com.snoringwalrus.ashbound.Gates;

import net.minecraft.client.Minecraft;
import net.minecraft.core.particles.ColorParticleOption;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.phys.Vec3;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;
import net.neoforged.neoforge.client.event.RegisterColorHandlersEvent;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.event.RenderFrameEvent;
import net.neoforged.neoforge.client.event.ViewportEvent;

/**
 * What a gate does round it, past its own drawing: sparks whipping round its rim and into it, smoke rolling off
 * it lit by it, embers off the scorched ground; bursts of sparks, smoke and a ring of dust as it bursts open and
 * as it bangs shut, a white flash and the view shaking with them (the nearer, the harder); the sky round the
 * deadliest (SSS) bleeding red. Its scorched ground glows in its colour.
 */
@EventBusSubscriber(modid = Ashbound.ID, value = Dist.CLIENT)
public final class GateFx {
	private GateFx() {}

	private static final List<GateEntity> LIVE = new ArrayList<>();
	private static final Map<Integer, Integer> SEEN = new HashMap<>();
	private static float flash, shake;

	static {
		GateEntity.clientTick = GateFx::tick;
	}

	@SubscribeEvent
	static void renderers(EntityRenderersEvent.RegisterRenderers e) {
		e.registerEntityRenderer(Gates.GATE.get(), GateRenderer::new);
	}

	/** The scorch's cracks in its gate's colour, dim once the gate's gone. */
	@SubscribeEvent
	static void colours(RegisterColorHandlersEvent.Block e) {
		e.register((s, level, pos, tint) -> {
			int c = GateEntity.COLOUR[s.getValue(GateScorch.RANK)];
			if (!s.getValue(GateScorch.FADING)) return c;
			return ((c >> 16 & 255) * 2 / 5) << 16 | ((c >> 8 & 255) * 2 / 5) << 8 | (c & 255) * 2 / 5;
		}, Gates.SCORCH.get());
	}

	@SubscribeEvent
	static void layers(RegisterGuiLayersEvent e) {
		e.registerAboveAll(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "gate_flash"), (gfx, delta) -> {
			if (flash < 0.01f) return;
			int a = (int) (Math.min(1, flash) * 220);
			gfx.fill(0, 0, gfx.guiWidth(), gfx.guiHeight(), a << 24 | 0xFFFFFF);
		});
	}

	@SubscribeEvent
	static void frame(RenderFrameEvent.Pre e) {
		GateRenderer.GateWarp.frameNow++;
	}

	@SubscribeEvent
	static void clientTick(ClientTickEvent.Pre e) {
		LIVE.clear();
		flash *= 0.72f;
		shake *= 0.86f;
		if (SEEN.size() > 64) SEEN.clear();
	}

	private static void tick(GateEntity g) {
		LIVE.add(g);
		Minecraft mc = Minecraft.getInstance();
		long now = g.level().getGameTime(), age = now - g.opened();
		int stage = g.closing() ? (now - g.closed() >= GateEntity.BANG ? 3 : 2) : age >= GateEntity.CRACK ? 1 : 0;
		Integer before = SEEN.put(g.getId(), stage);
		boolean burst = before != null && before != stage && stage == 1, bang = before != null && before != stage && stage == 3;
		if ((burst || bang) && mc.player != null) {
			double d = mc.player.position().distanceTo(g.middle());
			float k = (float) Math.max(0, 1 - d / 64);
			flash = Math.max(flash, k * (bang ? 0.7f : 0.5f));
			shake = Math.max(shake, k * (bang ? 1.6f : 1.1f));
		}

		RandomSource r = g.level().random;
		int c = GateEntity.COLOUR[g.rank()];
		boolean dark = GateEntity.dark(g.rank());
		ColorParticleOption spark = ColorParticleOption.create(Gates.SPARK.get(), 0xFF000000 | c);
		ColorParticleOption soot = ColorParticleOption.create(Gates.SMOKE.get(), dark ? 0xFF221E1E : 0xFF464242);
		ColorParticleOption glowSmoke = ColorParticleOption.create(Gates.SMOKE.get(), 0xFE000000 | dim(c, 0.45f));
		Vec3 m = g.middle(), f = g.facing(), side = new Vec3(f.z, 0, -f.x);
		GateRenderer.State s = GateRenderer.state(g, 0);
		float rx = GateEntity.RX * s.sx, ry = GateEntity.RY * s.sy;

		if (burst) {
			for (int i = 0; i < 80; i++) {
				Vec3 v = new Vec3(r.nextGaussian(), r.nextGaussian() * 1.2, r.nextGaussian()).normalize().scale(0.5 + r.nextFloat() * 0.9);
				g.level().addParticle(spark, m.x, m.y, m.z, v.x, v.y, v.z);
			}
			for (int i = 0; i < 34; i++) {
				float a = r.nextFloat() * Mth.TWO_PI;
				Vec3 dir = side.scale(Mth.cos(a)).add(0, Mth.sin(a) * 1.2, 0).add(f.scale(r.nextGaussian() * 0.6));
				Vec3 p = m.add(dir.scale(1.5));
				Vec3 v = dir.scale(0.12 + r.nextFloat() * 0.18);
				g.level().addParticle(i % 3 == 0 ? glowSmoke : soot, p.x, p.y, p.z, v.x, v.y, v.z);
			}
			dust(g, r, soot, 3.0, 0.35);
		}
		if (bang) {
			for (int i = 0; i < 110; i++) {
				Vec3 v = new Vec3(r.nextGaussian(), r.nextGaussian() * 0.8, r.nextGaussian()).normalize().scale(0.6 + r.nextFloat() * 1.1);
				g.level().addParticle(spark, m.x, m.y, m.z, v.x, v.y, v.z);
			}
			for (int i = 0; i < 16; i++) {
				Vec3 v = new Vec3(r.nextGaussian(), r.nextGaussian(), r.nextGaussian()).normalize().scale(0.15);
				g.level().addParticle(glowSmoke, m.x, m.y, m.z, v.x, v.y, v.z);
			}
			dust(g, r, soot, 1.5, 0.5);
		}

		if (s.crack >= 0) {
			// sparks spitting sideways off the hairline
			for (int i = 0; i < 2; i++) {
				Vec3 p = m.add(0, (r.nextFloat() - 0.5f) * 2 * ry, 0);
				Vec3 v = side.scale((r.nextBoolean() ? 1 : -1) * (0.15 + r.nextFloat() * 0.25)).add(f.scale(r.nextGaussian() * 0.1)).add(0, r.nextFloat() * 0.1, 0);
				g.level().addParticle(spark, p.x, p.y, p.z, v.x, v.y, v.z);
			}
			return;
		}
		if (!s.open || stage == 3) return;

		boolean closing = stage == 2;
		int sparks = closing ? 4 : 2;
		for (int i = 0; i < sparks; i++) {
			// whipping round the rim and into it; while closing they come from further out, faster
			float a = r.nextFloat() * Mth.TWO_PI, k = closing ? 2.0f + r.nextFloat() * 1.2f : 1.05f + r.nextFloat() * 0.6f;
			Vec3 radial = side.scale(Mth.cos(a) * rx).add(0, Mth.sin(a) * ry, 0);
			Vec3 tang = side.scale(-Mth.sin(a) * rx).add(0, Mth.cos(a) * ry, 0).normalize();
			Vec3 p = m.add(radial.scale(k)).add(f.scale(r.nextGaussian() * 0.4));
			Vec3 v = tang.scale(0.25 * s.hot).add(radial.normalize().scale(closing ? -0.4 : -0.12));
			g.level().addParticle(spark, p.x, p.y, p.z, v.x, v.y, v.z);
		}
		if (r.nextInt(3) == 0) {
			// smoke rolling off the rim behind it, lit by it
			float a = r.nextFloat() * Mth.TWO_PI;
			Vec3 p = m.add(side.scale(Mth.cos(a) * rx * 1.1)).add(0, Mth.sin(a) * ry * 1.1, 0).add(f.scale(-(0.3 + r.nextFloat())));
			Vec3 v = closing ? m.subtract(p).scale(0.03) : new Vec3(0, 0.02, 0).add(f.scale(-0.01));
			g.level().addParticle(r.nextInt(3) == 0 ? soot : glowSmoke, p.x, p.y, p.z, v.x, v.y, v.z);
		}
		if (!closing && r.nextInt(4) == 0) {
			// a plume of soot off its crown
			Vec3 p = m.add(side.scale((r.nextFloat() - 0.5f) * rx)).add(0, ry * 0.95, 0).add(f.scale(-0.6));
			g.level().addParticle(soot, p.x, p.y, p.z, 0, 0.04, 0);
		}
		if (r.nextInt(2) == 0) {
			// embers drifting up off the scorched ground
			double x = g.getX() + (r.nextDouble() - 0.5) * 10, z = g.getZ() + (r.nextDouble() - 0.5) * 10;
			g.level().addParticle(spark, x, g.getY() + 0.3, z, (r.nextFloat() - 0.5f) * 0.02, 0.05 + r.nextFloat() * 0.06, (r.nextFloat() - 0.5f) * 0.02);
		}
	}

	/** A ring of dust thrown out along the ground from its foot. */
	private static void dust(GateEntity g, RandomSource r, ColorParticleOption soot, double from, double speed) {
		for (int i = 0; i < 40; i++) {
			float a = i / 40f * Mth.TWO_PI + r.nextFloat() * 0.1f;
			double x = g.getX() + Mth.cos(a) * from, z = g.getZ() + Mth.sin(a) * from;
			g.level().addParticle(soot, x, g.getY() + 0.4, z, Mth.cos(a) * speed, 0.02, Mth.sin(a) * speed);
		}
	}

	private static int dim(int c, float k) {
		return (int) ((c >> 16 & 255) * k) << 16 | (int) ((c >> 8 & 255) * k) << 8 | (int) ((c & 255) * k);
	}

	@SubscribeEvent
	static void angles(ViewportEvent.ComputeCameraAngles e) {
		if (shake < 0.02f) return;
		double t = e.getPartialTick() + (Minecraft.getInstance().level == null ? 0 : Minecraft.getInstance().level.getGameTime());
		e.setYaw(e.getYaw() + (float) Math.sin(t * 2.9) * shake * 1.2f);
		e.setPitch(e.getPitch() + (float) Math.sin(t * 3.7 + 1) * shake * 0.9f);
		e.setRoll(e.getRoll() + (float) Math.sin(t * 2.3 + 2) * shake * 1.5f);
	}

	/** Near an SSS gate the air goes the colour of old blood. */
	@SubscribeEvent
	static void fog(ViewportEvent.ComputeFogColor e) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null) return;
		float k = 0;
		for (GateEntity g : LIVE) {
			if (!GateEntity.bleeds(g.rank()) || g.closing()) continue;
			double d = mc.player.position().distanceTo(g.middle());
			k = Math.max(k, (float) Math.max(0, 1 - d / 110));
		}
		if (k <= 0) return;
		k = Math.min(0.75f, k * 0.9f);
		e.setRed(Mth.lerp(k, e.getRed(), 0.34f));
		e.setGreen(Mth.lerp(k, e.getGreen(), 0.02f));
		e.setBlue(Mth.lerp(k, e.getBlue(), 0.03f));
	}
}
