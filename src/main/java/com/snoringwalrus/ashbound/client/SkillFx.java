package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.SpellLook;
import com.snoringwalrus.ashbound.client.SpellParticles.Arc;
import com.snoringwalrus.ashbound.client.SpellParticles.Beam;
import com.snoringwalrus.ashbound.client.SpellParticles.Bead;
import com.snoringwalrus.ashbound.client.SpellParticles.Dome;
import com.snoringwalrus.ashbound.client.SpellParticles.Flat;
import com.snoringwalrus.ashbound.client.SpellParticles.Flip;
import com.snoringwalrus.ashbound.client.SpellParticles.Orbit;
import com.snoringwalrus.ashbound.client.SpellParticles.Spike;

import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.model.BookModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.EnchantTableRenderer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.event.RenderLevelStageEvent;
import net.neoforged.neoforge.client.event.ViewportEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;
import net.neoforged.neoforge.common.NeoForge;

import static com.snoringwalrus.ashbound.client.SpellFx.add;
import static com.snoringwalrus.ashbound.client.SpellFx.blast;
import static com.snoringwalrus.ashbound.client.SpellFx.flip;
import static com.snoringwalrus.ashbound.client.SpellFx.floor;
import static com.snoringwalrus.ashbound.client.SpellFx.mix;
import static com.snoringwalrus.ashbound.client.SpellFx.pool;
import static com.snoringwalrus.ashbound.client.SpellFx.rand;
import static com.snoringwalrus.ashbound.client.SpellFx.shock;
import static com.snoringwalrus.ashbound.client.SpellFx.sparks;
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
 * The skills as they look, each its own shape and colour, built the way good action effects are: a wind-up, one white-hot
 * instant, then a slow fall away, with big soft shapes under small fast ones and a kick of the camera on anything heavy.
 * The pieces are {@link FxKit}'s. Also what a Form looks like round whoever is in it, the flash and speed lines on the
 * screen, the healer's mark on their target, and a book reading itself into you.
 */
final class SkillFx {
	private SkillFx() {}

	private static final int GOLD = 0xFFC850, EMBER = 0xFF7A2C, CRIMSON = 0xE0202C, BLOOD = 0xB01018, STEEL = 0x8CD8F0, SKY = 0x70B8FF, VIOLET = 0x8A4CE0,
			VENOM = 0x60D040, WHITE = 0xFFFFFF, OLIVE = 0xA8B850, PURPLE = 0x7A30D0, TEAL = 0x40E0C8, DARK = 0x2A2430;
	private static final float SHAKE_FADE = 0.82f, HEAR_SHAKE = 28, FLASH_FADE = 0.86f;
	/** Full-screen moments stay a tint: it's the brightest thing that can happen to someone's eyes, and in a party it happens often. */
	private static final float MOST_FLASH = 0.14f, DARK_BEAT = 0.25f;
	private static final int[] BOOK_COLOUR = {0xC8C0B0, 0x60D080, 0x50A0FF, 0xB060FF, 0xFFB030};

	private static final float PUNCH = 3, LINES_FADE = 0.8f;
	private static final int LINES = 46, MARK_EVERY = 10;

	private static final float FIRST_PERSON = 0.35f;
	private static float shake, flash, punch, lines;
	private static int flashRgb, linesRgb;
	/** where what's being drawn is: the screen only flashes for what's near */
	private static Vec3 stage = Vec3.ZERO;
	/** who's in which Form */
	private static final Map<Integer, String> AURA = new HashMap<>();
	private static final List<Reading> READING = new ArrayList<>();
	private static BookModel book;

	/** A book floating up and reading itself. */
	private static final class Reading {
		final Entity on;
		final int rgb;
		final boolean tome;
		int age;

		Reading(Entity on, int rgb, boolean tome) {
			this.on = on;
			this.rgb = rgb;
			this.tome = tome;
		}
	}

	private static final int BOOK_TICKS = 56, BOOK_OPEN = 12, BOOK_BURST = 46;

	/** The Form an entity is in, as far as this client's been told, or null. */
	static String aura(int entity) {
		return AURA.get(entity);
	}

	static void hooks(IEventBus bus) {
		Net.onSkillFx = SkillFx::play;
		Net.onFormAura = m -> {
			if (m.form().isEmpty()) AURA.remove(m.entity());
			else AURA.put(m.entity(), m.form());
		};
		NeoForge.EVENT_BUS.addListener((ClientTickEvent.Post e) -> tick());
		Net.onHealBeam = m -> {
			ClientLevel l = Minecraft.getInstance().level;
			if (l == null) return;
			Entity from = l.getEntity(m.from()), to = l.getEntity(m.to());
			if (m.ticks() <= 0) FxKit.HealBeam.cut(m.from(), m.to());
			else if (from != null && to != null) add(new FxKit.HealBeam(l, from, to, mix(com.snoringwalrus.ashbound.SpellLook.colour(m.gate()), 0x90FFB0, 0.6f), m.ticks()));
		};
		NeoForge.EVENT_BUS.addListener((ViewportEvent.ComputeCameraAngles e) -> angles(e));
		NeoForge.EVENT_BUS.addListener((ViewportEvent.ComputeFov e) -> {
			if (punch > 0.02f) e.setFOV(e.getFOV() + punch * HudPrefs.fxShake());
		});
		NeoForge.EVENT_BUS.addListener(SkillFx::books);
		bus.addListener((RegisterGuiLayersEvent e) -> e.registerAboveAll(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "skill_flash"), SkillFx::flash));
	}

	static void kick(Vec3 at, float amount) {
		var p = Minecraft.getInstance().player;
		if (p == null) return;
		float near = amount * SpellParticles.from * Math.max(0, 1 - (float) p.position().distanceTo(at) / HEAR_SHAKE);
		shake = Math.max(shake, near);
		punch = Math.max(punch, near * PUNCH);
	}

	/** Lines racing in from the edge of the screen, the way a big moment does in an anime. */
	private static void lines(int rgb, float strength) {
		lines = Math.max(lines, strength * near());
		linesRgb = rgb;
	}

	/** Anyone who picked a heal target and has a white staff out sees a mark under them. */
	private static void marked(ClientLevel l) {
		var mc = Minecraft.getInstance();
		if (CurioKeys.healTarget.isEmpty() || mc.player.tickCount % MARK_EVERY != 0 || !(mc.player.getMainHandItem().getItem() instanceof com.snoringwalrus.ashbound.Spells.Staff s) || !s.kind().equals("white")) return;
		for (var o : l.players())
			if (o.getName().getString().equals(CurioKeys.healTarget)) add(new FxKit.Decal(l, floor(l, o.position()), 0x90FFB0, FxKit.RUNE, 1.3f, MARK_EVERY + 4, 0.8f).follows(o));
	}

	private static void linesLayer(GuiGraphics g) {
		if (lines < 0.02f || !HudPrefs.fxLines) return;
		int w = g.guiWidth(), h = g.guiHeight();
		float cx = w / 2f, cy = h / 2f, far = Mth.sqrt(cx * cx + cy * cy);
		RandomSource r = RandomSource.create(Minecraft.getInstance().level == null ? 0 : Minecraft.getInstance().level.getGameTime());
		var pose = g.pose().last().pose();
		com.mojang.blaze3d.systems.RenderSystem.disableDepthTest();
		com.mojang.blaze3d.systems.RenderSystem.enableBlend();
		com.mojang.blaze3d.systems.RenderSystem.defaultBlendFunc();
		com.mojang.blaze3d.systems.RenderSystem.setShader(net.minecraft.client.renderer.GameRenderer::getPositionColorShader);
		var v = com.mojang.blaze3d.vertex.Tesselator.getInstance().begin(com.mojang.blaze3d.vertex.VertexFormat.Mode.TRIANGLES, com.mojang.blaze3d.vertex.DefaultVertexFormat.POSITION_COLOR);
		int colour = mix(linesRgb, WHITE, 0.3f);
		for (int i = 0; i < LINES; i++) {
			float a = r.nextFloat() * Mth.TWO_PI, wide = 0.006f + r.nextFloat() * 0.018f * lines, in = far * (0.62f + 0.3f * r.nextFloat() + 0.12f * (1 - lines));
			float alpha = (0.15f + 0.35f * r.nextFloat()) * Math.min(1, lines * 1.5f);
			v.addVertex(pose, cx + Mth.cos(a) * in, cy + Mth.sin(a) * in, 0).setColor((colour >> 16 & 255) / 255f, (colour >> 8 & 255) / 255f, (colour & 255) / 255f, alpha);
			v.addVertex(pose, cx + Mth.cos(a - wide) * far * 1.1f, cy + Mth.sin(a - wide) * far * 1.1f, 0).setColor((colour >> 16 & 255) / 255f, (colour >> 8 & 255) / 255f, (colour & 255) / 255f, alpha);
			v.addVertex(pose, cx + Mth.cos(a + wide) * far * 1.1f, cy + Mth.sin(a + wide) * far * 1.1f, 0).setColor((colour >> 16 & 255) / 255f, (colour >> 8 & 255) / 255f, (colour & 255) / 255f, alpha);
		}
		com.mojang.blaze3d.vertex.BufferUploader.drawWithShader(v.buildOrThrow());
		com.mojang.blaze3d.systems.RenderSystem.disableBlend();
		com.mojang.blaze3d.systems.RenderSystem.enableDepthTest();
	}

	private static float near() {
		var p = Minecraft.getInstance().player;
		return p == null ? 0 : Math.max(0, 1 - (float) p.position().distanceTo(stage) / (HEAR_SHAKE * 1.5f));
	}

	private static void flashOf(int rgb, float a) {
		flash = Math.max(flash, Math.min(a, MOST_FLASH) * near());
		flashRgb = rgb;
	}

	/** The anime trick for the biggest blows: one tick of near black, then the colour. */
	private static void frame(ClientLevel l, Vec3 at, int rgb, float a) {
		stage = at;
		float near = near();
		flash = Math.max(flash, DARK_BEAT * near);
		flashRgb = 0;
		FxKit.later(l, 1, () -> {
			flash = Math.min(a, MOST_FLASH) * near;
			flashRgb = rgb;
		});
	}

	private static void angles(ViewportEvent.ComputeCameraAngles e) {
		if (shake < 0.02f) return;
		double t = e.getPartialTick() + (Minecraft.getInstance().level == null ? 0 : Minecraft.getInstance().level.getGameTime());
		float k = shake * inEyes() * HudPrefs.fxShake();
		e.setYaw(e.getYaw() + (float) Math.sin(t * 3.1) * k * 1.3f);
		e.setPitch(e.getPitch() + (float) Math.sin(t * 3.9 + 1) * k);
		e.setRoll(e.getRoll() + (float) Math.sin(t * 2.3 + 2) * k * 1.4f);
	}

	private static void flash(GuiGraphics g, DeltaTracker dt) {
		linesLayer(g);
		if (flash < 0.01f || !HudPrefs.fxFlash) return;
		g.fill(0, 0, g.guiWidth(), g.guiHeight(), Math.round(flash * inEyes() * 255) << 24 | flashRgb);
	}

	/** In first person it all lands on your eyes, with no body in the way: shakes and flashes come at a share of what they'd be. */
	private static float inEyes() {
		return Minecraft.getInstance().options.getCameraType().isFirstPerson() ? FIRST_PERSON : 1;
	}

	private static void tick() {
		shake *= SHAKE_FADE;
		flash *= FLASH_FADE;
		punch *= SHAKE_FADE;
		lines *= LINES_FADE;
		ClientLevel l = Minecraft.getInstance().level;
		if (l == null) {
			AURA.clear();
			READING.clear();
			return;
		}
		if (Minecraft.getInstance().player != null) marked(l);
		for (var it = AURA.entrySet().iterator(); it.hasNext(); ) {
			var e = it.next();
			Entity on = l.getEntity(e.getKey());
			if (on == null) it.remove();
			else aura(l, on, e.getValue());
		}
		for (Iterator<Reading> it = READING.iterator(); it.hasNext(); ) {
			Reading r = it.next();
			r.age++;
			if (r.age >= BOOK_TICKS || r.on.isRemoved()) it.remove();
			else reading(l, r);
		}
	}

	/** An upright frame across the way someone's looking: x to their right, y up, z ahead. */
	private static Vec3 right(Vec3 dir) {
		Vec3 r = dir.cross(new Vec3(0, 1, 0));
		return r.lengthSqr() < 1e-4 ? new Vec3(1, 0, 0) : r.normalize();
	}

	private static Vec3 flat(Vec3 dir) {
		Vec3 f = dir.multiply(1, 0, 1);
		return f.lengthSqr() < 1e-4 ? new Vec3(0, 0, 1) : f.normalize();
	}

	/** Round the ground: a flat sweep at waist height, full turn or a slice of one, with a hot edge on it. */
	private static void sweep(ClientLevel l, Vec3 at, Vec3 dir, int rgb, float radius, float width, float span, int life) {
		float a = (float) Mth.atan2(dir.z, dir.x);
		FxKit.slash(l, at, new Vec3(1, 0, 0), new Vec3(0, 0, 1), rgb, radius, width, a - span / 2, a + span / 2, life);
	}

	/** Top to bottom, in front of you: the shape of an overhead blow. */
	private static void cleave(ClientLevel l, Vec3 at, Vec3 dir, int rgb, float radius, float width, int life) {
		FxKit.slash(l, at, flat(dir), new Vec3(0, 1, 0), rgb, radius, width, 2.4f, -0.5f, life);
	}

	/** Blades punched up out of the ground in a ring, from the middle out, each with a dark one in it, and they break when they go. */
	private static void spikes(ClientLevel l, Vec3 at, int rgb, int n, float reach, float tall, float wide) {
		RandomSource r = l.getRandom();
		Vec3 f = floor(l, at).add(0, -0.1, 0);
		int dark = mix(rgb, 0, 0.65f), pale = mix(rgb, WHITE, 0.6f);
		for (int i = 0; i < n; i++) {
			double a = i * Mth.TWO_PI / n + r.nextDouble() * 0.3, d = reach * (0.5 + r.nextDouble() * 0.5);
			Vec3 foot = f.add(Math.cos(a) * d, 0, Math.sin(a) * d);
			Vec3 axis = new Vec3(Math.cos(a) * 0.55, 1, Math.sin(a) * 0.55).normalize().scale(tall * (0.6 + r.nextDouble() * 0.6));
			int life = 20 + r.nextInt(14), wait = (int) (d * 1.2);
			FxKit.later(l, wait, () -> {
				add(new Spike(l, foot, axis.scale(0.8), dark, wide * 1.6f, life));
				add(new Spike(l, foot, axis, rgb, wide, life));
				flip(l, 0, SpellParticles.STREAK, pale, foot, axis.normalize().scale(0.9), 0.08f, 0.03f, 8).stretched(6).drag(0.8f);
			});
			FxKit.later(l, wait + life - 2, () -> FxKit.streaks(l, foot.add(axis.scale(0.6)), pale, 3, 0.35, 0.04f, 4, 6, 0.6));
		}
	}

	private static void smoke(ClientLevel l, Vec3 at, int rgb, int n, float spread, float size) {
		RandomSource r = l.getRandom();
		for (int i = 0; i < n; i++) {
			Vec3 d = rand(r, 0.6);
			flip(l, ROLL, SMOKE, rgb, at.add(d.scale(spread)), d.scale(0.04).add(0, 0.02, 0), size * 0.6f, size * 1.4f, 26 + r.nextInt(12));
		}
	}

	private static void play(Net.SkillFx m) {
		SpellParticles.as(SpellParticles.share(m.by()), () -> draw(m));
	}

	private static void draw(Net.SkillFx m) {
		ClientLevel l = Minecraft.getInstance().level;
		if (l == null) return;
		Entity on = m.on() < 0 ? null : l.getEntity(m.on());
		Vec3 at = new Vec3(m.at()), dir = new Vec3(m.dir()), waist = at.add(0, 1, 0);
		float r = m.r();
		stage = at;
		switch (m.look()) {
			case "hit" -> hit(l, at, r);
			case "quake" -> kick(at, r);          // a beast's slam, landing, roar: only the camera, no look of its own
			case "ring" -> {
				FxKit.slam(l, at, EMBER, r, 0.6f);
				kick(at, 0.5f);
			}
			case "line" -> {
				FxKit.lance(l, waist, dir, EMBER, r, 0.7f, 12);
				kick(at, 0.3f);
			}
			// ---- Vanguard: gold, and everything it does is a wall going up
			case "bastion_slam" -> {
				Motifs.wall(l, at, GOLD, 5, 3.2f, 34);
				FxKit.later(l, 4, () -> Motifs.wall(l, at, mix(GOLD, 0, 0.2f), 3, 2, 26));
				FxKit.rocks(l, at, 10, 0.3);
				kick(at, 0.7f);
			}
			case "oath_charge" -> {
				Motifs.needle(l, waist, dir, GOLD, 9, 0.5f, 11);
				sweep(l, waist.add(dir.scale(3)), dir, GOLD, 3.4f, 0.7f, 3.2f, 11);
				FxKit.dust(l, at, 2, 6);
				kick(at, 0.3f);
			}
			case "shield_wall" -> {
				Motifs.wall(l, at, STEEL, 7, 3, 44);
				add(new Dome(l, at, STEEL, 7, 34));
				FxKit.later(l, 6, () -> FxKit.ring(l, at, STEEL, 7, 14));
				kick(at, 0.5f);
			}
			case "unbroken" -> {
				FxKit.gather(l, waist, EMBER, 3, 8);
				Motifs.wall(l, at, EMBER, 2.4f, 4, 30);
				Motifs.blaze(l, at, EMBER, 3);
				add(new FxKit.Tube(l, at, new Vec3(0, 1, 0), GOLD, 3, 1.4f, 1.1f, 2, 140, 0.35f).follows(on));
				FxKit.rune(l, at, EMBER, 6, 140);
				lines(EMBER, 0.6f);
				kick(at, 1.2f);
			}
			case "unbroken_end" -> {
				Motifs.shatter(l, at, EMBER, 7, 6);
				Motifs.blaze(l, at, EMBER, 5);
				frame(l, at, EMBER, 0.12f);
				lines(EMBER, 0.8f);
				kick(at, 1.6f);
			}
			case "oath_cross" -> {
				Vec3 side = right(dir), mid = waist.add(flat(dir).scale(2.2)).add(0, 0.4, 0);
				float tilt = r < 6 ? 1 : -1;
				Vec3 slant = side.scale(tilt).add(0, 1, 0).normalize();
				FxKit.slash(l, mid, slant, flat(dir).scale(-1), GOLD, 3, 0.7f, -1.5f, 1.5f, 13);
				sparks(l, mid, GOLD, 14, 0.3, 0.03f);
				kick(at, 0.35f);
			}
			case "last_oath_rise" -> {
				add(new Beam(l, at.add(0, 1.8, 0), new Vec3(0, 11, 0), GOLD, 0.7f, 22, 0.8f, on, 0.5f));
				FxKit.gather(l, at.add(0, 4, 0), GOLD, 4, 18);
				FxKit.rune(l, at, GOLD, 3.4f, 24);
				lines(GOLD, 0.4f);
			}
			case "last_oath" -> {
				Vec3 f = flat(dir), far = at.add(f.scale(9));
				FxKit.slash(l, waist.add(f.scale(1)), f, new Vec3(0, 1, 0), GOLD, 11, 1.8f, 1.9f, -0.15f, 15);
				Motifs.wall(l, far, GOLD, 6, 5, 34);
				Motifs.shatter(l, far, GOLD, 6, 5);
				frame(l, at, GOLD, 0.14f);
				lines(GOLD, 0.9f);
				kick(at, 2.2f);
			}
			// ---- Breaker: the ground itself, split and thrown, with the fire underneath showing
			case "rift_slam" -> {
				Motifs.shatter(l, at, EMBER, 7, 5);
				Motifs.blaze(l, at, EMBER, 3);
				lines(EMBER, 0.4f);
				kick(at, 1.4f);
			}
			case "fault_line" -> {
				Motifs.fissure(l, at, dir, EMBER, 5, 1.2f);
				FxKit.ring(l, at, EMBER, 3, 12);
				kick(at, 0.4f);
			}
			case "worldbreaker_rise" -> {
				FxKit.rune(l, at, EMBER, 9.6f, 44);
				FxKit.gather(l, waist, EMBER, 5, 30);
				FxKit.rocks(l, at, 10, 0.2);
			}
			case "worldbreaker" -> {
				Motifs.shatter(l, at, r > 8 ? CRIMSON : EMBER, r, 6);
				Motifs.blaze(l, at, EMBER, r * 0.6f);
				if (r > 8) frame(l, at, EMBER, 0.12f);
				lines(EMBER, r / 10);
				kick(at, r / 4);
			}
			// ---- Headsman: one thin line, then what it did
			case "headsman_rise" -> {
				add(new Beam(l, at.add(0, 1.6, 0), new Vec3(0, 3, 0), CRIMSON, 0.1f, 18, 0.9f, on, 0));
				FxKit.gather(l, at.add(0, 4, 0), CRIMSON, 2.4f, 16);
			}
			case "headsmans_drop" -> {
				Vec3 f = flat(dir), hit = at.add(f.scale(3));
				Motifs.cut(l, floor(l, hit), CRIMSON, 9, 0.5f);
				cleave(l, waist.add(f.scale(1.5)).add(0, 0.8, 0), f, CRIMSON, 3.8f, 0.8f, 13);
				FxKit.later(l, 2, () -> Motifs.fissure(l, hit, f, CRIMSON, 4, 0.5f));
				frame(l, at, CRIMSON, 0.1f);
				lines(CRIMSON, 0.6f);
				kick(at, 1.6f);
			}
			case "reapers_mark" -> {
				Vec3 top = at.add(0, r + 0.9, 0);
				add(new FxKit.Decal(l, top, CRIMSON, FxKit.RUNE, 1.3f, 200, 0.8f).facing(0.5f).follows(on));
				Motifs.cut(l, at, CRIMSON, r + 0.9f, 0.16f);
				FxKit.ink(l, at.add(0, r / 2, 0), CRIMSON, 3, 0.5f, 0.9f, 18);
			}
			case "beheading_rise" -> FxKit.gather(l, at.add(0, 3, 0), CRIMSON, 2.6f, 14);
			case "beheading" -> {
				Vec3 mid = at.add(0, 1.2, 0), side = right(dir);
				FxKit.slash(l, mid, side, new Vec3(0, 1, 0), CRIMSON, 2.6f, 0.8f, 2.6f, -0.5f, 12);
				Motifs.cut(l, floor(l, at), CRIMSON, 6, 0.3f);
				Motifs.gore(l, at, CRIMSON, r > 0 ? 4 : 2.4f);
				if (r > 0) frame(l, at, CRIMSON, 0.14f);
				lines(CRIMSON, r > 0 ? 0.9f : 0.5f);
				kick(at, r > 0 ? 2.2f : 1.2f);
			}
			// ---- Reaver: black with a red edge, the same rule as the black staff's fire
			case "blood_price" -> {
				sweep(l, waist, dir, BLOOD, 4.2f, 0.9f, Mth.TWO_PI, 13);
				Motifs.gore(l, at, BLOOD, 4.6f);
				FxKit.cracks(l, at, CRIMSON, 5, 60);
				kick(at, 0.8f);
			}
			case "red_thirst" -> {
				add(new FxKit.Tube(l, at, new Vec3(0, 1, 0), BLOOD, 3.2f, 0.9f, 0.5f, 3, 160, 0.4f).follows(on));
				FxKit.rune(l, at, CRIMSON, 2.6f, 26);
				FxKit.spray(l, waist, BLOOD, 24, 0.3f);
				FxKit.ink(l, waist, CRIMSON, 4, 0.6f, 0.9f, 18);
			}
			case "crimson_rite_rise" -> {
				FxKit.rune(l, at, CRIMSON, 8, 18);
				Motifs.drawIn(l, waist, CRIMSON, 5, 14);
				lines(CRIMSON, 0.5f);
			}
			case "crimson_rite" -> {
				Motifs.gore(l, at, CRIMSON, 8);
				sweep(l, waist, dir, BLOOD, 7.5f, 1.5f, Mth.TWO_PI, 15);
				SpellFx.tongues(l, floor(l, at), CRIMSON, INK, 16, 0.3);
				FxKit.cracks(l, at, CRIMSON, 8, 70);
				frame(l, at, CRIMSON, 0.14f);
				lines(CRIMSON, 0.9f);
				kick(at, 1.8f);
			}
			// ---- Steel: thin cuts stacked up, nothing soft
			case "steel_tempest", "eye_of_storm" -> {
				boolean eye = m.look().startsWith("eye");
				Motifs.gale(l, at, STEEL, eye ? 4.8f : 4, 2.4f, eye ? 5 : 4);
				FxKit.ring(l, at, STEEL, (eye ? 4.8f : 4) + 1, 11);
				FxKit.dust(l, at, eye ? 4.8f : 4, 5);
				kick(at, 0.3f);
			}
			case "razor_gale" -> {
				Motifs.gale(l, at, STEEL, 2.3f, 3.2f, 3);
				FxKit.dust(l, at, 2, 3);
			}
			// ---- Lancer: long thin lines and the air they leave behind
			case "skyfall_up" -> {
				FxKit.ring(l, at, SKY, 3.6f, 12);
				Motifs.needle(l, at, new Vec3(0, 1, 0), SKY, 10, 0.3f, 10);
				FxKit.dust(l, at, 3, 8);
				kick(at, 0.3f);
			}
			case "skyfall" -> {
				Motifs.needle(l, at.add(0, 16, 0), new Vec3(0, -1, 0), SKY, 16, 0.5f, 12);
				Motifs.shatter(l, at, SKY, 5.5f, 4);
				lines(SKY, 0.5f);
				kick(at, 1.2f);
			}
			case "dragon_lunge" -> {
				Motifs.needle(l, waist, flat(dir), SKY, 9, 0.4f, 10);
				FxKit.dust(l, at, 1.6f, 5);
				kick(at, 0.4f);
			}
			case "descent_mark" -> {
				FxKit.rune(l, at, SKY, r, 34);
				add(new Beam(l, floor(l, at), new Vec3(0, 18, 0), SKY, 0.07f, 34, 0.7f, null, 0));
			}
			case "descent_dive" -> {
				Motifs.needle(l, at.add(0, 1, 0), dir.reverse(), SKY, 12, 0.4f, 8);
				lines(SKY, 0.4f);
			}
			case "dragons_descent" -> {
				Motifs.needle(l, at.add(0, 26, 0), new Vec3(0, -1, 0), SKY, 26, 0.9f, 16);
				Motifs.shatter(l, at, SKY, 7.5f, 6);
				frame(l, at, SKY, 0.12f);
				lines(SKY, 0.9f);
				kick(at, 2);
			}
			case "spear_wall" -> {
				for (int i = 2; i < 14; i += 3) {
					Vec3 p = waist.add(0, 0.4, 0).add(dir.scale(i));
					FxKit.later(l, i / 3, () -> {
						add(new Spike(l, p, dir.scale(2.4), GOLD, 0.14f, 12));
						add(new FxKit.Decal(l, p, mix(GOLD, WHITE, 0.3f), FxKit.RING, 1.1f, 9, 0.7f).across(dir));
					});
				}
				kick(at, 0.5f);
			}
			case "spear_hedge" -> {
				spikes(l, at, GOLD, 12, 2, 2.4f, 0.14f);
				FxKit.rocks(l, at, 6, 0.3);
				FxKit.ring(l, at, GOLD, 2.4f, 9);
			}
			case "thrust" -> {
				Vec3 side = right(dir), off = side.scale((l.getRandom().nextDouble() - 0.5) * 1.2).add(0, (l.getRandom().nextDouble() - 0.5) * 0.9, 0);
				Motifs.needle(l, waist.add(0, 0.4, 0).add(off), dir, GOLD, 9, 0.16f, 6);
				kick(at, 0.15f);
			}
			// ---- Shade: black smoke, violet edges, gone before the cut's finished
			case "vanish" -> {
				FxKit.ink(l, waist, VIOLET, 12, 0.8f, 1.5f, 20);
				add(new FxKit.Decal(l, waist, VIOLET, FxKit.SWIRL, 1.8f, 14, 0.8f).facing(0.25f));
				for (int i = 0; i < 6; i++) add(new Orbit(l, waist, 0.9f, i * 1.05f, 0.4f, VIOLET, 0.25f, 12));
			}
			case "smoke_step" -> {
				add(new FxKit.Decal(l, waist, VIOLET, FxKit.SWIRL, 1.6f, 11, 0.8f).facing(0.3f));
				FxKit.ink(l, waist, VIOLET, 5, 0.5f, 1.1f, 16);
			}
			case "vanish_cut", "blossom_cut" -> {
				Vec3 mid = m.look().startsWith("blossom") ? at : waist, side = right(dir);
				FxKit.slash(l, mid, side, new Vec3(0, 1, 0), VIOLET, 1.9f, 0.6f, 2.3f, -0.8f, 9);
				FxKit.later(l, 2, () -> FxKit.slash(l, mid, side.reverse(), new Vec3(0, 1, 0), VIOLET, 1.9f, 0.4f, 2.3f, -0.8f, 8));
				FxKit.ink(l, mid, VIOLET, 3, 0.4f, 0.8f, 14);
				kick(at, 0.5f);
			}
			case "death_blossom" -> {
				Motifs.petals(l, waist, VIOLET, 4, 8);
				add(new FxKit.Decal(l, waist, VIOLET, FxKit.SWIRL, 3.4f, 22, 0.8f).facing(0));
				FxKit.ring(l, at, VIOLET, 8, 18);
				frame(l, at, VIOLET, 0.1f);
				lines(VIOLET, 0.7f);
				kick(at, 0.9f);
			}
			// ---- Venom: a cloud that hangs there
			case "viper_bite" -> {
				sweep(l, waist.add(dir.scale(1.2)), dir, VENOM, 3, 0.7f, 2.4f, 10);
				FxKit.spray(l, waist.add(dir.scale(2.5)), VENOM, 20, 0.35f);
				Motifs.fumes(l, at.add(dir.scale(3)), VENOM, 2.2f, 26);
			}
			case "toxic_cloud" -> Motifs.fumes(l, at, VENOM, 4.4f, 40);
			case "plague_bloom" -> {
				FxKit.ring(l, at, VENOM, 13, 20);
				FxKit.rune(l, at, VENOM, 4, 16);
				Motifs.drawIn(l, waist, VENOM, 3, 10);
				kick(at, 0.4f);
			}
			case "plague_burst" -> {
				Vec3 mid = at.add(0, r * 0.5, 0);
				Motifs.fumes(l, at, VENOM, 3, 30);
				FxKit.spray(l, mid, VENOM, 26, 0.5f);
				SpellFx.tongues(l, mid, VENOM, INK, 8, 0.2);
			}
			// ---- Hunter: cold thin needles, and the ground waiting for you
			case "deadeye" -> {
				Vec3 eye = at.add(0, 1.4, 0);
				Motifs.needle(l, eye, dir, STEEL, 40, 0.14f, 9);
				kick(at, 0.4f);
			}
			case "arrow_rain_mark" -> {
				FxKit.rune(l, at, STEEL, 4.6f, 30);
				FxKit.gather(l, at.add(0, 5, 0), STEEL, 3, 20);
			}
			case "arrow_rain" -> {
				RandomSource rnd = l.getRandom();
				Vec3 f = floor(l, at);
				for (int i = 0; i < 12; i++) {
					Vec3 land = f.add((rnd.nextDouble() - 0.5) * 8, 0, (rnd.nextDouble() - 0.5) * 8);
					int life = 5 + rnd.nextInt(4);
					flip(l, 0, SpellParticles.STREAK, mix(STEEL, WHITE, 0.3f), land.add(0, life * 2.6, 0), new Vec3(0, -2.6, 0), 0.12f, 0.08f, life).stretched(10).drag(1);
					FxKit.later(l, life, () -> {
						add(new Spike(l, land, new Vec3((rnd.nextDouble() - 0.5) * 0.3, 1, (rnd.nextDouble() - 0.5) * 0.3), mix(STEEL, 0, 0.4f), 0.05f, 30));
						add(new FxKit.Decal(l, land, mix(STEEL, WHITE, 0.3f), FxKit.RING, 1.1f, 9, 0.7f));
						FxKit.rocks(l, land, 2, 0.2);
					});
				}
			}
			case "star_charge" -> {
				Vec3 tip = at.add(0, 1.4, 0).add(dir.scale(1));
				FxKit.gather(l, tip, STEEL, 3, 16);
				for (int i = 0; i < 8; i++) add(new Orbit(l, tip, 1.5f, i * 0.8f, 0.5f, STEEL, 0.2f, 16));
				lines(STEEL, 0.3f);
			}
			case "piercing_star" -> {
				Vec3 eye = at.add(0, 1.4, 0);
				Motifs.needle(l, eye, dir, STEEL, 40, 0.5f, 15);
				add(new Beam(l, eye, dir.scale(40), STEEL, 0.4f, 22, 0.7f, null, 0.5f).lightning());
				FxKit.ring(l, at, STEEL, 5, 12);
				frame(l, at, STEEL, 0.1f);
				lines(STEEL, 0.9f);
				kick(at, 1.2f);
			}
			case "snare_field" -> {
				FxKit.rune(l, at, OLIVE, 4.2f, 74);
				spikes(l, at, OLIVE, 16, 4, 1.4f, 0.12f);
				RandomSource rnd = l.getRandom();
				for (int i = 0; i < 6; i++) {
					double a = i * Mth.TWO_PI / 6 + rnd.nextDouble();
					add(new Beam(l, floor(l, at).add(0, 0.15, 0), new Vec3(Math.cos(a) * 4, 0, Math.sin(a) * 4), OLIVE, 0.2f, 26, 0.8f, null, 0.6f).lightning());
				}
			}
			case "spike_pit_set" -> FxKit.rune(l, at, OLIVE, 3.6f, 40);
			case "spike_pit" -> {
				spikes(l, at, 0xB8A070, 16, 3.5f, 2.2f, 0.17f);
				FxKit.rocks(l, at, 12, 0.35);
				FxKit.dust(l, at, 3, 6);
				kick(at, 0.3f);
			}
			case "killing_ground" -> {
				FxKit.rune(l, at, CRIMSON, 8.4f, 46);
				add(new FxKit.Decal(l, floor(l, at), CRIMSON, FxKit.SWIRL, 8, 46, 0.3f).spun(0.01f));
				FxKit.ink(l, floor(l, at).add(0, 0.4, 0), CRIMSON, 8, 4, 1.4f, 30);
			}
			// ---- Ashcaster: real flame and soot; the void pulls in
			case "cinder_field" -> {
				Motifs.blaze(l, at, EMBER, 4);
				FxKit.cracks(l, at, EMBER, 5, 24);
				pool(l, at, EMBER, 4.6f, 18, 0.45f);
			}
			case "flame_lance" -> {
				Vec3 eye = at.add(0, 1.4, 0);
				Motifs.needle(l, eye, dir, EMBER, 14, 0.5f, 12);
				Motifs.flame(l, eye, dir, EMBER, 14);
				kick(at, 0.4f);
			}
			case "meteor_fall" -> {
				FxKit.rune(l, at, EMBER, 7.4f, 26);
				add(new FxKit.Decal(l, floor(l, at), EMBER, FxKit.RING, 8, 24, 0.7f).inward());
				add(new FxKit.Meteor(l, floor(l, at), 0xFF9040, 24));
			}
			case "meteor" -> {
				Motifs.shatter(l, at, EMBER, 8, 6);
				Motifs.blaze(l, at, EMBER, 7);
				smoke(l, at.add(0, 2, 0), 0x2A2420, 14, 4, 3);
				frame(l, at, EMBER, 0.14f);
				lines(EMBER, 0.9f);
				kick(at, 2.4f);
			}
			case "black_hole", "event_horizon" -> {
				boolean big = m.look().startsWith("event");
				float s = big ? 5 : 3.4f;
				int life = big ? 66 : 44;
				flip(l, 0, HOLE, PURPLE, at, Vec3.ZERO, s * 0.7f, s * 0.9f, life);
				add(new FxKit.Decal(l, at, PURPLE, FxKit.SWIRL, s, life, 0.8f).facing(0.42f));
				add(new FxKit.Decal(l, floor(l, at), PURPLE, FxKit.SWIRL, s * 2.2f, life, 0.6f));
				for (int i = 0; i < 14; i++) add(new Orbit(l, at, s - i * 0.2f, i * 0.63f, 0.5f, PURPLE, 0.3f, life - 4));
				for (int i = 0; i * 10 < life - 8; i++) FxKit.later(l, i * 10, () -> Motifs.drawIn(l, at, PURPLE, s * 1.3f, 10));
			}
			case "black_hole_burst", "event_burst" -> {
				float s = m.look().startsWith("event") ? 1.4f : 1;
				FxKit.ink(l, at, PURPLE, 10, 3 * s, 2, 24);
				FxKit.impact(l, at, PURPLE, 2 * s);
				SpellFx.tongues(l, at, PURPLE, INK, 14, 0.3);
				FxKit.ring(l, at, PURPLE, 8 * s, 18);
				frame(l, at, PURPLE, 0.12f);
				lines(PURPLE, 0.8f);
				kick(at, 1.5f * s);
			}
			case "void_lances" -> {
				add(new Flat(l, floor(l, at).add(0, 0.02, 0), PURPLE, HOLE, 3.4f, 24, 0.02f, 0.9f));
				spikes(l, at, PURPLE, 14, 3.4f, 3.4f, 0.2f);
				FxKit.ink(l, at.add(0, 0.8, 0), PURPLE, 6, 2, 1.3f, 20);
				kick(at, 0.4f);
			}
			// ---- Mender: light from above, round and soft; never a white fill
			case "judgement" -> {
				add(new FxKit.Decal(l, floor(l, at), GOLD, FxKit.RING, 3.6f, 8, 0.7f).inward());
				Motifs.shaft(l, at, 0xFFE9A8, 18, 1.2f, 16);
				Motifs.wall(l, at, GOLD, 3.4f, 1.8f, 22);
				kick(at, 0.8f);
			}
			case "sanctify" -> {
				FxKit.rune(l, at, GOLD, 6.2f, 62);
				Motifs.grace(l, at, GOLD, 5.6f);
				for (int i = 1; i < 5; i++) FxKit.later(l, i * 12, () -> FxKit.rising(l, at, mix(GOLD, WHITE, 0.3f), 5.6f, 10, 20));
			}
			case "second_dawn" -> {
				FxKit.gather(l, at.add(0, 2, 0), GOLD, 6, 10);
				Motifs.shaft(l, at, 0xFFE9A8, 34, 3.4f, 34);
				Motifs.grace(l, at, GOLD, 9);
				FxKit.rune(l, at, GOLD, 16, 50);
				FxKit.ring(l, at, GOLD, 14, 34);
				FxKit.rising(l, at, mix(GOLD, WHITE, 0.3f), 14, 50, 24);
				frame(l, at, GOLD, 0.12f);
				lines(GOLD, 0.8f);
				kick(at, 1.2f);
			}
			case "dawn_on" -> {
				Motifs.shaft(l, at, GOLD, 8, 0.7f, 20);
				FxKit.halo(l, at, mix(GOLD, WHITE, 0.3f), 1.4f, 2.2f, 4);
			}
			case "holy_lance" -> {
				Motifs.needle(l, at.add(0, 1.4, 0), dir, 0xFFE9A8, 16, 0.45f, 13);
				kick(at, 0.35f);
			}
			case "heavens_wrath_mark" -> {
				FxKit.rune(l, at, GOLD, 7.6f, 60);
				add(new FxKit.Tube(l, floor(l, at), new Vec3(0, 1, 0), GOLD, 2.4f, 7.4f, 7.4f, 0.8f, 56, 0.15f));
			}
			case "heavens_wrath" -> {
				Motifs.cut(l, floor(l, at), 0xFFE9A8, 20, 0.35f);
				FxKit.impact(l, at.add(0, 0.6, 0), GOLD, 0.7f);
				FxKit.cracks(l, at, GOLD, 2.6f, 50);
				FxKit.rocks(l, at, 6, 0.3);
				kick(at, 0.5f);
			}
			// ---- Caller: out of the ground, black and cold
			case "champion_rise" -> {
				SpellFx.rise(l, at, PURPLE);
				Motifs.tearOpen(l, at, PURPLE, 5);
				add(new FxKit.Decal(l, floor(l, at), PURPLE, FxKit.SWIRL, 4.4f, 30, 0.8f).spun(0.03f));
				frame(l, at, PURPLE, 0.1f);
				lines(PURPLE, 0.5f);
				kick(at, 1.4f);
			}
			case "legion" -> {
				FxKit.rune(l, at, PURPLE, 8, 46);
				Motifs.tearOpen(l, at, PURPLE, 7);
				lines(PURPLE, 0.5f);
				kick(at, 0.8f);
			}
			case "marrow_burst" -> {
				spikes(l, at, 0xD8D8B8, 10, 2.6f, 1.8f, 0.13f);
				FxKit.ink(l, at.add(0, 0.8, 0), TEAL, 4, 0.8f, 1.1f, 18);
				FxKit.ring(l, at, TEAL, 3.4f, 11);
				FxKit.rocks(l, at, 6, 0.3);
			}
			case "soul_mend" -> {
				add(new FxKit.Tube(l, at, new Vec3(0, 1, 0), TEAL, 3.4f, 0.9f, 0.4f, 3, 20, 0.5f).follows(on));
				FxKit.rune(l, at, TEAL, 1.8f, 22);
				FxKit.halo(l, at, mix(TEAL, WHITE, 0.3f), 1.6f, 2.2f, 4);
			}
			case "ascended" -> {
				Motifs.shaft(l, at, GOLD, 22, 1.8f, 26);
				Motifs.grace(l, at, GOLD, 5);
				add(new FxKit.Tube(l, at, new Vec3(0, 1, 0), GOLD, 4, 1.4f, 0.9f, 2, 300, 0.25f).follows(on));
				frame(l, at, GOLD, 0.1f);
				lines(GOLD, 0.6f);
				kick(at, 1.2f);
			}
			// ---- Forms
			case "tome" -> READING.add(new Reading(on == null ? Minecraft.getInstance().player : on, CRIMSON, true));
			case "martyr_saved" -> {
				Motifs.shaft(l, at, GOLD, 14, 1.2f, 22);
				Motifs.grace(l, at, GOLD, 3.4f);
				FxKit.halo(l, at, mix(GOLD, WHITE, 0.3f), 1.6f, 2.4f, 4);
			}
			case "hammer_wave" -> {
				Motifs.shatter(l, at, EMBER, r, 4);
				kick(at, 0.3f);
			}
			case "strike_drake" -> breath(l, at.add(0, 1.5, 0), dir, EMBER, 0xFFD060);
			case "strike_hammerfall" -> {
				Motifs.shatter(l, at, EMBER, 6, 5);
				Motifs.blaze(l, at, EMBER, 2.5f);
				kick(at, 1.1f);
			}
			case "strike_crown" -> {
				Motifs.tearOpen(l, at, PURPLE, 6);
				FxKit.impact(l, waist, PURPLE, 1.2f);
				kick(at, 1.1f);
			}
			case "strike_communion" -> {
				sweep(l, waist, dir, BLOOD, 4.4f, 0.9f, Mth.TWO_PI, 12);
				Motifs.gore(l, at, CRIMSON, 3.6f);
				kick(at, 0.7f);
			}
			case "strike_tyrant" -> {
				Motifs.needle(l, at, dir.scale(4).add(0, 5, 0).normalize(), SKY, 7, 0.4f, 11);
				FxKit.ring(l, at, SKY, 3.4f, 11);
			}
			default -> {
				if (m.look().startsWith("form_")) enter(l, at, m.look().substring(5), on);
				else if (m.look().startsWith("book_")) READING.add(new Reading(on == null ? Minecraft.getInstance().player : on, BOOK_COLOUR[Mth.clamp(m.look().charAt(5) - '1', 0, 4)], false));
				else if (m.look().startsWith("mob_")) {
					int cut = m.look().indexOf(':');
					monster(l, m.look().substring(4, cut), m.look().substring(cut + 1), at, dir, r, on);
				} else if (m.look().startsWith("style_")) {
					int cut = m.look().indexOf(':');
					StyleFx.play(l, m.look().substring(6, cut), m.look().substring(cut + 1), at, dir, r);
				}
			}
		}
	}

	/** The gate monsters' skills (MobSkills), in their dungeon's colour; anything that's going to land shows where first. */
	private static void monster(ClientLevel l, String what, String gate, Vec3 at, Vec3 dir, float r, Entity on) {
		int c = SpellLook.colour(gate), pale = mix(c, WHITE, 0.3f);
		SpellLook.Family fam = SpellLook.of(gate);
		Vec3 f = floor(l, at);
		switch (what) {
			case "tell" -> {   // dir.x: how many ticks till it lands
				int t = Math.max(4, (int) dir.x);
				add(new Flat(l, f, c, SpellParticles.GLOW, r * 1.2f, t + 2, 0, 0.3f));
				add(new FxKit.Decal(l, f.add(0, 0.02, 0), c, FxKit.RUNE, r, t + 3, 0.8f));
				add(new FxKit.Decal(l, f.add(0, 0.03, 0), pale, FxKit.RING, r * 1.15f, t, 1).inward());
				FxKit.gather(l, f.add(0, 0.7, 0), c, Math.max(1.2f, r * 0.6f), t);
			}
			case "slam" -> {
				FxKit.slam(l, at, c, r, r * 0.45f);
				Motifs.burst(l, fam, c, at, r * 0.7f);
				kick(at, Math.min(1.6f, r * 0.3f));
			}
			case "launch" -> {
				Motifs.burst(l, fam, c, at, Math.min(r, 2));
				FxKit.ring(l, at, c, r, 12);
				FxKit.dust(l, at, r, 6);
			}
			case "trail" -> {
				if (fam == SpellLook.Family.FLAME) flip(l, FLAME, FIRE, c, at, new Vec3(0, 0.04, 0), 0.6f, 0.2f, 10).stretched(1.6f);
				else FxKit.ink(l, at, c, 1, 0.3f, 0.8f, 12);
			}
			case "gather" -> Motifs.drawIn(l, at, c, r, Math.max(4, (int) dir.x));
			case "dash" -> {
				Motifs.needle(l, at.add(0, 0.6, 0), dir.reverse(), c, 2.4f, 0.2f, 7);
				FxKit.dust(l, at, 1.2f, 3);
			}
			case "crash" -> {
				FxKit.impact(l, at, c, 0.9f);
				Motifs.burst(l, fam, c, at, 2);
				FxKit.rocks(l, at, 10, 0.4);
				kick(at, 0.8f);
			}
			case "spin" -> {
				Motifs.gale(l, at, c, r, 1.8f, 3);
				FxKit.dust(l, at, r, 4);
				kick(at, 0.25f);
			}
			case "quake" -> {
				FxKit.cracks(l, at, c, 2.4f, 50);
				Motifs.fissure(l, at, dir, c, 3, 0.8f);
				Motifs.burst(l, fam, c, at, 1.6f);
				kick(at, 0.35f);
			}
			case "roar" -> {
				Vec3 mouth = at;
				for (int i = 0; i < 4; i++) {
					float size = 3 + i * 3;
					FxKit.later(l, i * 2, () -> add(new FxKit.Decal(l, mouth, pale, FxKit.RING, size, 12, 1).facing(-1)));
				}
				FxKit.ring(l, at, c, 9, 16);
				FxKit.dust(l, at, 6, 12);
				FxKit.streaks(l, mouth, pale, 22, 1.2, 0.07f, 7, 8, 0);
				FxKit.streaks(l, mouth, 0, 8, 1, 0.1f, 6, 8, 0);
				lines(c, 0.6f);
				kick(at, 1.4f);
			}
			case "pull" -> {   // from at, along dir, r long
				Motifs.needle(l, at, dir, c, r, 0.2f, 9);
				add(new Beam(l, at, dir.scale(r), pale, 0.07f, 7, 0.8f, null, 0.9f).lightning());
			}
			case "blink" -> {
				Motifs.petals(l, at, c, 1.6f, 4);
				add(new FxKit.Decal(l, at, c, FxKit.SWIRL, 1.7f, 12, 0.8f).facing(0.25f));
			}
			case "mark" -> {   // dir.x: ticks
				int t = (int) dir.x;
				add(new FxKit.Decal(l, f.add(0, 0.02, 0), c, FxKit.RUNE, r, t + 2, 0.9f));
				add(new Flat(l, f, c, SpellParticles.GLOW, r * 1.1f, t, 0, 0.25f));
				add(new FxKit.Decal(l, f.add(0, 0.03, 0), pale, FxKit.RING, r * 1.2f, t, 0.7f).inward());
			}
			case "strike" -> {
				Vec3 sky = f.add(0, 11, 0);
				add(new Beam(l, sky, f.subtract(sky), 0, 0.8f, 7, 0.8f, null, 1));
				add(new Beam(l, sky, f.subtract(sky), c, 0.55f, 7, 1, null, 1));
				add(new Beam(l, sky, f.subtract(sky), pale, 0.2f, 5, 1, null, 1));
				FxKit.impact(l, f.add(0, 0.4, 0), c, 0.5f);
				Motifs.burst(l, fam, c, at, 1.6f);
				FxKit.cracks(l, at, c, 1.8f, 34);
				kick(at, 0.3f);
			}
			case "thunder" -> {
				SpellFx.hit(l, SpellLook.Family.LIGHTNING, c, at.add(0, 0.6, 0), null);
				kick(at, 0.8f);
			}
			case "cloud" -> {   // dir.x: how long it stands
				int t = (int) dir.x;
				add(new FxKit.Decal(l, f.add(0, 0.02, 0), c, FxKit.SWIRL, r, t, 0.45f).spun(0.015f));
				add(new FxKit.Decal(l, f.add(0, 0.03, 0), mix(c, 0, 0.3f), FxKit.RUNE, r, t, 0.6f));
				for (int i = 0; i * 14 < t - 10; i++) FxKit.later(l, i * 14, () -> Motifs.fumes(l, at, c, r, 28));
			}
			case "breath" -> {
				if (fam == SpellLook.Family.FLAME) breath(l, at, dir, c, pale);
				else {
					Motifs.stream(l, fam, at, dir, c);
					kick(at, 0.2f);
				}
			}
			case "beam" -> {   // from at, along dir, r long; each burst lasts until the next
				Vec3 end = at.add(dir.scale(r));
				add(new Beam(l, at, dir.scale(r), 0, 1.25f, 5, 0.7f, null, 1));
				add(new Beam(l, at, dir.scale(r), c, 0.95f, 5, 1, null, 1));
				add(new Beam(l, at, dir.scale(r), pale, 0.32f, 4, 1, null, 1));
				FxKit.flare(l, at, c, 2, 4);
				add(new FxKit.Pop(l, end, c, SpellParticles.STAR, 1.6f, 1, 3, l.getRandom().nextFloat() * Mth.TWO_PI, 0));
				FxKit.streaks(l, at.add(dir.scale(l.getRandom().nextFloat() * r)), pale, 3, 0.4, 0.05f, 5, 6, 0);
				kick(at, 0.08f);
			}
			case "summon" -> {
				SpellFx.rise(l, at, c);
				Motifs.tearOpen(l, at, c, 2.4f);
			}
			case "heal" -> {
				Motifs.grace(l, at, c, 2.4f);
				FxKit.halo(l, at, pale, 1.5f, 2.4f, 3);
			}
			case "healed" -> {
				Motifs.grace(l, at, c, 1.2f);
			}
			case "phase" -> {   // a boss rising again: the biggest thing in the dungeon
				FxKit.gather(l, at.add(0, 1.5, 0), c, 5, 8);
				FxKit.later(l, 8, () -> {
					stage = at;
					Motifs.burst(l, fam, c, at, 7);
					Motifs.shatter(l, at, c, 9, 6);
					Motifs.shaft(l, at, c, 28, 2.4f, 30);
					FxKit.rune(l, at, c, 9, 50);
					FxKit.ink(l, at.add(0, 1, 0), c, 12, 3, 2.2f, 34);
					frame(l, at, c, 0.14f);
					lines(c, 0.9f);
					kick(at, 2.2f);
				});
			}
			case "ward" -> {
				add(new Dome(l, at, c, r, 12));
				Motifs.wall(l, at, c, r, 2, 14);
			}
			default -> {}
		}
	}

	/** Every blow that lands: a white star on the spot, sparks that follow the weapon, a smear of a cut. */
	private static void hit(ClientLevel l, Vec3 at, float heavy) {
		int c = mix(GOLD, WHITE, 0.2f);
		RandomSource r = l.getRandom();
		if (heavy > 0.5f) FxKit.flare(l, at, c, heavy * 1.3f, 5);
		float roll = r.nextFloat() * Mth.TWO_PI;
		add(new FxKit.Pop(l, at, 0, SpellParticles.STAR, 0.9f + heavy, 0.6f + heavy * 0.6f, 4, roll, 0));
		add(new FxKit.Pop(l, at, c, SpellParticles.STAR, 0.7f + heavy, 0.4f + heavy * 0.6f, 3, roll, 0));
		flip(l, BLAST, FIRE, c, at, Vec3.ZERO, 0.2f + heavy * 0.25f, 0.6f + heavy * 0.45f, 6);
		FxKit.streaks(l, at, c, 4 + (int) (heavy * 5), 0.5 + heavy * 0.3, 0.05f, 4, 5, 0);
		sparks(l, at, c, 8 + (int) (heavy * 12), 0.25 + heavy * 0.2, 0.05f);
		float a = r.nextFloat() * Mth.TWO_PI;
		add(new Arc(l, at, new Vec3(Math.cos(a), 0.4, Math.sin(a)).normalize(), new Vec3(-Math.sin(a), 0.7, Math.cos(a)).normalize(), c, 0.9f + heavy * 0.5f, 0.14f + heavy * 0.08f, 2.6f, 0.3f, 6));
		if (heavy > 0.5f) kick(at, heavy * 0.25f);
	}

	private static void breath(ClientLevel l, Vec3 from, Vec3 dir, int c, int hot) {
		RandomSource r = l.getRandom();
		for (int i = 0; i < 26; i++) {
			Vec3 d = dir.add(rand(r, 0).scale(0.2)).normalize().scale(0.45 + r.nextDouble() * 0.5);
			flip(l, i % 4 == 0 ? BLAST : FLAME, FIRE, i % 3 == 0 ? hot : c, from.add(dir.scale(0.7)), d, 0.4f, 1.5f, 14 + r.nextInt(8)).stretched(1.4f);
		}
		smoke(l, from.add(dir.scale(5)), mix(c, 0x201C1A, 0.8f), 3, 2, 1.5f);
		FxKit.streaks(l, from.add(dir.scale(2)), hot, 6, 0.8, 0.05f, 6, 8, 0);
		sparks(l, from.add(dir.scale(2)), c, 10, 0.6, 0);
		kick(from, 0.3f);
	}

	private static int colourOf(String form) {
		return switch (form) {
			case "drake" -> EMBER;
			case "hammerfall" -> 0xFFA040;
			case "communion" -> CRIMSON;
			case "tyrant" -> SKY;
			case "noone" -> VIOLET;
			case "stag" -> 0xD8F0FF;
			case "offering" -> 0xFF5020;
			case "martyr" -> GOLD;
			default -> PURPLE;
		};
	}

	/** The moment of taking a Form: the biggest thing anyone in the party does. */
	private static void enter(ClientLevel l, Vec3 at, String form, Entity on) {
		int c = colourOf(form);
		Vec3 waist = at.add(0, 1, 0);
		switch (form) {
			case "drake", "offering" -> Motifs.blaze(l, at, c, 7);
			case "hammerfall" -> Motifs.shatter(l, at, c, 8, 6);
			case "communion" -> Motifs.gore(l, at, c, 7);
			case "tyrant" -> Motifs.gale(l, at, c, 5, 5, 6);
			case "noone" -> Motifs.petals(l, waist, c, 4, 8);
			case "stag", "martyr" -> Motifs.grace(l, at, c, 7);
			default -> Motifs.tearOpen(l, at, c, 7);
		}
		Motifs.shaft(l, at, c, 26, 2, 26);
		FxKit.rune(l, at, c, 8, 40);
		frame(l, at, c, 0.14f);
		lines(c, 0.9f);
		kick(at, 2.2f);
	}

	/** Which way their body faces, from their yaw, without the head turning it. */
	private static Vec3 facing(Entity on) {
		float yaw = (on instanceof net.minecraft.world.entity.LivingEntity e ? e.yBodyRot : on.getYRot()) * Mth.DEG_TO_RAD;
		return new Vec3(-Math.sin(yaw), 0, Math.cos(yaw));
	}

	private static void aura(ClientLevel l, Entity on, String form) {
		RandomSource r = l.getRandom();
		int c = colourOf(form), t = on.tickCount;
		Vec3 front = facing(on), side = right(front), back = on.position().subtract(front.scale(0.3)), waist = on.position().add(0, 1, 0);
		switch (form) {
			case "drake" -> {
				// two wings of fire on the back, each a line of flames that beats
				float beat = Mth.sin(t * 0.28f) * 0.45f;
				for (int s = -1; s <= 1; s += 2)
					for (int i = 1; i <= 7; i++) {
						double k = i / 7.0, out = k * 2.5, up = 1.5 + Math.sin(k * 2.4) * 1.2 + beat * k * 2.2 - k * k * 0.7;
						Vec3 p = back.add(side.scale(s * out)).add(0, up, 0).subtract(front.scale(k * 0.6));
						flip(l, FLAME, FIRE, i > 4 ? 0xFFD060 : EMBER, p, new Vec3(0, -0.02, 0), 0.55f - (float) k * 0.1f, 0.2f, 6);
						if (i % 2 == 0)
							flip(l, FLAME, FIRE, EMBER, p.add(0, -0.4 - (1 - k) * 0.9, 0), new Vec3(0, -0.04, 0), 0.4f, 0.1f, 6);
					}
				if (t % 4 == 0) sparks(l, waist, EMBER, 3, 0.12, -0.03f);
				if (t % 10 == 0) pool(l, on.position(), EMBER, 2.4f, 14, 0.5f);
			}
			case "hammerfall" -> {
				// the ground gives under every step, and slag hangs round you
				if (t % 7 == 0 && on.onGround()) {
					FxKit.cracks(l, on.position(), c, 1.5f, 16);
					FxKit.rocks(l, on.position(), 1, 0.15);
				}
				if (t % 4 == 0) add(new Orbit(l, waist, 1.2f, r.nextFloat() * Mth.TWO_PI, 0.3f, mix(c, 0x201C1A, 0.5f), 0.26f, 14));
				if (t % 3 == 0) sparks(l, on.position().add(0, 0.1, 0), c, 2, 0.08, 0.04f);
			}
			case "communion" -> {
				// it runs off you: black at the core, red on the edge, and it pools where you stand
				if (t % 2 == 0) add(new Bead(l, waist.add(rand(r, 0).scale(0.5)), new Vec3(0, -0.02, 0), BLOOD, 0.08f, 16));
				if (t % 3 == 0) flip(l, ROLL, INK, CRIMSON, waist.add(rand(r, 0).scale(0.45)), new Vec3(0, 0.02, 0), 0.4f, 0.9f, 18);
				if (t % 14 == 0) pool(l, on.position(), mix(BLOOD, 0, 0.5f), 1.8f, 20, 0.45f);
			}
			case "tyrant" -> {
				// a thin turning cut of wind round you, never quite closed
				if (t % 12 == 0) {
					float a = t * 0.9f;
					Vec3 u = new Vec3(Mth.cos(a), 0.15, Mth.sin(a)).normalize(), v = new Vec3(-Mth.sin(a), -0.15, Mth.cos(a)).normalize();
					FxKit.slash(l, waist, u, v, c, 1.5f, 0.12f, 0, Mth.TWO_PI * 0.7f, 9);
				}
				add(new Orbit(l, waist, 1.1f, t * 0.5f, 0.2f, c, 0.16f, 6));
			}
			case "noone" -> {
				// you come apart at the edges: smoke left hanging where you were
				if (t % 2 == 0) flip(l, ROLL, INK, VIOLET, on.position().add(rand(r, 0).multiply(0.4, 0, 0.4)).add(0, r.nextDouble() * 1.8, 0), Vec3.ZERO, 0.3f, 0.7f, 16);
			}
			case "stag" -> {
				// antlers of light over the head, and the mark under the feet
				Vec3 head = on.position().add(0, on.getBbHeight() + 0.05, 0);
				if (t % 4 == 0) {
					for (int s = -1; s <= 1; s += 2) {
						Vec3 tip = side.scale(s * 0.7).add(0, 0.9, 0);
						add(new Beam(l, head, tip, c, 0.05f, 6, 0.9f, null, 0));
						add(new Beam(l, head.add(tip.scale(0.5)), side.scale(s * 0.45).add(0, 0.25, 0), c, 0.035f, 6, 0.9f, null, 0));
						add(new Beam(l, head.add(tip.scale(0.75)), side.scale(s * -0.1).add(0, 0.5, 0), c, 0.03f, 6, 0.9f, null, 0));
					}
				}
				if (t % 20 == 0) add(new Flat(l, floor(l, on.position()), c, CIRCLE, 1.8f, 24, 0.02f, 0.8f));
			}
			case "offering" -> {
				flip(l, FLAME, FIRE, r.nextBoolean() ? c : 0x401008, on.position().add(rand(r, 0).multiply(0.5, 0, 0.5)).add(0, r.nextDouble() * 1.8, 0), new Vec3(0, 0.08, 0), 0.5f, 0.2f, 10).stretched(1.8f);
				if (t % 4 == 0) flip(l, ROLL, SMOKE, 0x201814, on.position().add(0, 2, 0), new Vec3(0, 0.05, 0), 0.5f, 1, 18);
			}
			case "martyr" -> {
				// a thin ring over the head, and a little light coming down on them
				if (t % 6 == 0) add(new FxKit.Decal(l, on.position().add(0, on.getBbHeight() + 0.4, 0), mix(c, WHITE, 0.3f), FxKit.RING, 0.7f, 9, 0.7f).across(new Vec3(0, 1, 0)));
				if (t % 5 == 0) flip(l, 0, GLOW, c, on.position().add(rand(r, 0).multiply(0.6, 0, 0.6)).add(0, 2.4, 0), new Vec3(0, -0.04, 0), 0.08f, 0.03f, 18);
			}
			default -> {
				// the Crown: its Colossus fights for you (Spells.colossus), and a mantle of smoke at your feet
				if (t % 2 == 0) flip(l, ROLL, SMOKE, 0x281838, on.position().add(rand(r, 0).multiply(0.9, 0.1, 0.9)).add(0, 0.2, 0), new Vec3(0, 0.03, 0), 0.7f, 1.3f, 22);
			}
		}
	}

	private static Vec3 bookAt(Reading r, float partial) {
		float t = (r.age + partial) / BOOK_OPEN, up = Math.min(1, t);
		return r.on.getPosition(partial).add(facing(r.on).scale(0.85)).add(0, 0.9 + up * (1 - (1 - up) * (1 - up)) * 0.9 + Mth.sin((r.age + partial) * 0.2f) * 0.04, 0);
	}

	/** Runes pour off the pages into the reader, and at the end it burns away in the reader's light. */
	private static void reading(ClientLevel l, Reading r) {
		Vec3 at = bookAt(r, 0), chest = r.on.position().add(0, 1.1, 0);
		RandomSource rnd = l.getRandom();
		if (r.age > BOOK_OPEN && r.age < BOOK_BURST) {
			for (int i = 0; i < 3; i++) {
				Vec3 p = at.add(rand(rnd, 0.2).scale(0.45));
				flip(l, 0, GLOW, r.rgb, p, chest.subtract(p).scale(0.07), 0.13f, 0.04f, 14);
			}
			if (r.age % 3 == 0) add(new Orbit(l, chest, 1.2f, rnd.nextFloat() * Mth.TWO_PI, 0.3f, r.rgb, 0.2f, 10));
			if (r.age % 12 == 0) add(new Flat(l, floor(l, r.on.position()), r.rgb, CIRCLE, 2.4f, 18, 0.03f, 0.9f));
			if (r.tome) flip(l, FLAME, FIRE, EMBER, at.add(rand(rnd, 0).scale(0.4)), new Vec3(0, 0.05, 0), 0.4f, 0.1f, 12);
		}
		if (r.age == BOOK_BURST) {
			stage = r.on.position();
			if (r.tome) {   // a Tome takes something from you for what it gives
				Motifs.blaze(l, r.on.position(), r.rgb, 4);
				Motifs.shaft(l, r.on.position(), r.rgb, 20, 1.4f, 22);
				flashOf(r.rgb, 0.1f);
			} else Motifs.grace(l, r.on.position(), r.rgb, 2.6f);
			Motifs.frost(l, at, r.rgb, r.tome ? 12 : 8);
			kick(r.on.position(), r.tome ? 1.2f : 0.3f);
		}
	}

	private static void books(RenderLevelStageEvent e) {
		if (e.getStage() != RenderLevelStageEvent.Stage.AFTER_ENTITIES || READING.isEmpty()) return;
		Minecraft mc = Minecraft.getInstance();
		if (book == null) book = new BookModel(mc.getEntityModels().bakeLayer(ModelLayers.BOOK));
		float partial = e.getPartialTick().getGameTimeDeltaPartialTick(false);
		Vec3 cam = e.getCamera().getPosition();
		PoseStack ps = e.getPoseStack();
		MultiBufferSource.BufferSource buffers = mc.renderBuffers().bufferSource();
		for (Reading r : READING) {
			if (r.age >= BOOK_BURST) continue;
			float t = r.age + partial, open = Mth.clamp((t - 4) / 10, 0, 1) * (1 - Mth.clamp((t - BOOK_BURST + 4) / 4, 0, 1));
			float page = t * 0.35f;
			Vec3 at = bookAt(r, partial);
			ps.pushPose();
			ps.translate(at.x - cam.x, at.y - cam.y, at.z - cam.z);
			ps.mulPose(Axis.YP.rotationDegrees(-r.on.getYRot() - 90));
			ps.mulPose(Axis.ZP.rotationDegrees(65));
			book.setupAnim(t, Mth.frac(page), Mth.frac(page + 0.25f), open);
			int colour = 0xFF000000 | mix(r.rgb, WHITE, 0.45f);
			// a sprite on the block atlas, not a texture of its own: the Material gives the buffer that maps onto it
			book.renderToBuffer(ps, EnchantTableRenderer.BOOK_LOCATION.buffer(buffers, RenderType::entitySolid), LightTexture.FULL_BRIGHT, OverlayTexture.NO_OVERLAY, colour);
			ps.popPose();
		}
		buffers.endBatch();
	}
}
