package com.snoringwalrus.ashbound.client;

import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Vfx;

import net.minecraft.ChatFormatting;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.ViewportEvent;

/**
 * The Cold Forge waking: the camera backs off to its front and rises as the Ember sinks into the bowl, the stone shakes,
 * and at the swap (the server turns the blocks) the runes catch and the fire stands up between the hands. Ends on the
 * big banner: this is one of the moments the anime UI is kept for.
 */
@EventBusSubscriber(modid = Ashbound.ID, value = Dist.CLIENT)
public final class ColdScene {
	private ColdScene() {}

	private static boolean on, wasHidden;
	private static CameraType wasCamera;
	private static Vec3 centre, front, eye = Vec3.ZERO;
	private static float yaw, pitch, shake;
	private static int t, ends, swap;

	public static boolean on() {
		return on;
	}

	public static Vec3 eye() {
		return eye;
	}

	public static float yaw() {
		return yaw;
	}

	public static float pitch() {
		return pitch;
	}

	public static void play(Net.ColdWake m) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || on) return;
		on = true;
		centre = m.centre().getCenter();
		float a = m.face() * Mth.DEG_TO_RAD;
		front = new Vec3(-Mth.sin(a), 0, Mth.cos(a));   // the way the forge looks
		t = 0;
		shake = 0;
		ends = m.ends();
		swap = m.swap();
		wasCamera = mc.options.getCameraType();
		wasHidden = mc.options.hideGui;
		mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
		mc.options.hideGui = true;
		frame(0);
		mc.setScreen(new Banner());
	}

	private static void stop() {
		if (!on) return;
		on = false;
		Minecraft mc = Minecraft.getInstance();
		mc.options.setCameraType(wasCamera);
		mc.options.hideGui = wasHidden;
	}

	private static void frame(float pt) {
		float k = Mth.clamp((t + pt) / ends, 0, 1);
		k = k * k * (3 - 2 * k);
		double far = Mth.lerp(k, 6.0, 9.0), up = Mth.lerp(k, 0.0, 2.2);
		eye = centre.add(front.scale(far)).add(0, up, 0);
		Vec3 d = centre.add(0, 0.8, 0).subtract(eye).normalize();
		yaw = (float) (Mth.atan2(-d.x, d.z) * Mth.RAD_TO_DEG);
		pitch = (float) (-Math.asin(d.y) * Mth.RAD_TO_DEG);
	}

	private static void play(SoundEvent s, float pitch, float volume) {
		Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(s, pitch, volume));
	}

	private static void burst(int n, float speed, int rgb) {
		Minecraft mc = Minecraft.getInstance();
		var r = mc.level.random;
		for (int i = 0; i < n; i++) {
			double a = r.nextDouble() * Mth.TWO_PI, s = speed * (0.3 + r.nextDouble());
			mc.level.addParticle(new Vfx.Opt(rgb, 0.08f, 24 + r.nextInt(24), 0.4f, Vfx.GLOW | Vfx.STREAK), centre.x, centre.y, centre.z,
					Math.cos(a) * s, 0.1 + r.nextDouble() * speed * 1.4, Math.sin(a) * s);
		}
	}

	@SubscribeEvent
	static void tick(ClientTickEvent.Post e) {
		Minecraft mc = Minecraft.getInstance();
		if (!on || mc.level == null) return;
		t++;
		frame(0);
		shake *= 0.88f;
		var r = mc.level.random;
		if (t < swap) {
			// the Ember going down into the ash, the old fire drawn to it
			if (t % 20 == 1) play(SoundEvents.WARDEN_HEARTBEAT, 0.7f + t * 0.004f, 1f);
			if (t == 2) play(SoundEvents.BEACON_ACTIVATE, 0.6f, 1f);
			double a = r.nextDouble() * Mth.TWO_PI, s = 3.4;
			Vec3 from = centre.add(Math.cos(a) * s, r.nextDouble() * 3, Math.sin(a) * s);
			Vec3 v = centre.subtract(from).scale(0.08);
			mc.level.addParticle(new Vfx.Opt(0xFF9A30, 0.05f, 14, 0f, Vfx.GLOW | Vfx.STREAK), from.x, from.y, from.z, v.x, v.y, v.z);
			shake = Math.max(shake, t / (float) swap * 0.8f);
		}
		if (t == swap) {
			play(SoundEvents.GENERIC_EXPLODE.value(), 0.5f, 1f);
			play(SoundEvents.FIRECHARGE_USE, 0.5f, 1f);
			play(SoundEvents.BELL_BLOCK, 0.5f, 1f);
			shake = 3f;
			burst(220, 0.5f, 0xFFB24A);
			burst(70, 0.3f, 0xFFF0C0);
		}
		if (t > swap && t < swap + 80) {
			mc.level.addParticle(ParticleTypes.LAVA, centre.x, centre.y, centre.z, 0, 0, 0);
			if (t % 3 == 0) burst(8, 0.22f, 0xFF7A20);
		}
		if (t == swap + 26) play(SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, 0.7f, 1f);
		if (t >= ends && mc.screen instanceof Banner) mc.setScreen(null);
	}

	@SubscribeEvent
	static void angles(ViewportEvent.ComputeCameraAngles e) {
		if (!on || shake < 0.02f) return;
		double n = System.nanoTime() * 1e-8;
		e.setPitch(e.getPitch() + (float) Math.sin(n * 3.1) * shake * 0.5f);
		e.setRoll(e.getRoll() + (float) Math.sin(n * 2.3 + 2) * shake * 0.8f);
	}

	/** Holds you still through the scene, flashes at the swap, and carries the banner. */
	private static final class Banner extends Screen {
		Banner() {
			super(Component.literal("The Cold Forge"));
		}

		@Override
		public boolean isPauseScreen() {
			return false;
		}

		@Override
		public boolean shouldCloseOnEsc() {
			return false;
		}

		@Override
		public void renderBackground(GuiGraphics g, int mx, int my, float pt) {}

		@Override
		public void removed() {
			stop();
		}

		@Override
		public void render(GuiGraphics g, int mx, int my, float pt) {
			float since = t + pt - swap;
			if (since >= 0 && since < 14) g.fill(0, 0, width, height, (int) ((1 - since / 14) * 235) << 24 | 0xFFE6C0);
			float in = (since - 26) / 16;
			if (in <= 0) return;
			int a = Math.max(4, (int) (Mth.clamp(in, 0, 1) * Mth.clamp((ends - t - pt) / 12f, 0, 1) * 255)) << 24;
			g.pose().pushPose();
			g.pose().translate(width / 2f, height * 0.24f, 0);
			g.pose().scale(3.4f, 3.4f, 1f);
			Component big = Component.literal("THE COLD FORGE WAKES").withStyle(ChatFormatting.BOLD);
			g.drawString(font, big, -font.width(big) / 2, 0, a | 0xFFD24A, true);
			g.pose().popPose();
			String sub = "Two can be made one here. Bring it what you've taken from the gates.";
			g.drawString(font, sub, (width - font.width(sub)) / 2, (int) (height * 0.24f) + 38, a | 0xECE4D6, true);
		}
	}
}
