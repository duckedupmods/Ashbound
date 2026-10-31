package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.List;

import org.lwjgl.glfw.GLFW;

import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.GateEntity;
import com.snoringwalrus.ashbound.Intro;
import com.snoringwalrus.ashbound.Net;

import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientPlayerNetworkEvent;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * The wagoner's telling (Intro): the camera leaves you at the cart and goes round it, then gates tear open on the road
 * ahead, a pair of colours at a time, real ones (GateEntity.vision) that only this client sees. Ends on Highmourn's name
 * and where it lies. Everything's placed along the cart: f down the road, u up, s across it. Esc skips.
 */
@EventBusSubscriber(modid = Ashbound.ID, value = Dist.CLIENT)
public final class IntroScene {
	private IntroScene() {}

	private record Shot(int from, int to, Vec3 eyeA, Vec3 eyeB, Vec3 lookA, Vec3 lookB) {}

	private record Line(int from, int to, String text) {}

	private record Tear(int at, int shut, float s, int rank) {}

	private static Shot shot(int from, int to, double f, double u, double s, double f2, double u2, double s2, double lf, double lu, double ls, double lf2, double lu2, double ls2) {
		return new Shot(from, to, new Vec3(f, u, s), new Vec3(f2, u2, s2), new Vec3(lf, lu, ls), new Vec3(lf2, lu2, ls2));
	}

	private static final String WHO = "Hob Tarrant";
	private static final double GATE_F = 16;
	private static final float PAIR = 4.2f;
	private static final int TITLE = 900, BLACK_FADE = 8, FIRST_FADE = 30, WORDS_FADE = 6, EMBER = 0xFF9A30;
	private static final int[] CUTS = {300, 430, 540, 650};

	private static final List<Shot> SHOTS = List.of(
			shot(0, 170, -11, 5, 7, -7, 3, 10, 1, 1, 0, 1, 1.2, 0),
			shot(170, 300, 2.6, 1.8, 6, 2.2, 1.7, 5.4, 0.6, 1.5, 2.8, 0.6, 1.6, 2.8),
			shot(300, 430, 5.5, 1.8, 0, 7, 1.7, 0, GATE_F, 4.5, 0, GATE_F, 4.5, 0),
			shot(430, 540, 7, 1.6, 2, 8, 1.6, 0, GATE_F, 4.5, 0, GATE_F, 4.5, 0),
			shot(540, 650, 8, 1.6, -2, 8.5, 1.6, 0, GATE_F, 4.5, 0, GATE_F, 4.5, 0),
			shot(650, 770, 6, 1.5, 0, 11, 2.2, 0, GATE_F, 5, 0, GATE_F, 5.2, 0),
			shot(770, 900, -4, 2, -5, -6, 3.5, -3, 3, 1.5, 0, 12, 3, 0),
			shot(900, Intro.LENGTH, -6, 3.5, -3, -9, 22, 0, 12, 3, 0, 60, 16, 0));

	private static final List<Line> LINES = List.of(
			new Line(12, 88, "You fell out of a crack at dawn. I've pulled worse off this road."),
			new Line(94, 166, "Sit a moment. Nobody told me any of this, and it cost me two brothers."),
			new Line(176, 296, "They're opening all over these lands. The guild calls them gates. There's a dungeon behind every one, and something ruling it."),
			new Line(306, 426, "The colour's the only warning you'll ever get. Pale or green? That's work for the likes of you."),
			new Line(436, 536, "Blue or purple, take friends. Good ones."),
			new Line(546, 646, "Orange or red have killed people with names."),
			new Line(662, 766, "And if the hole's black and only the rim burns, walk away. Don't look back."),
			new Line(776, 896, "Every road here runs to Highmourn. The guild there pays for this work, and they'll find you a bed. Go on."));

	private static final List<Tear> TEARS = List.of(
			new Tear(306, 430, -PAIR, 0), new Tear(322, 430, PAIR, 1),
			new Tear(436, 540, -PAIR, 2), new Tear(450, 540, PAIR, 3),
			new Tear(546, 650, -PAIR, 4), new Tear(560, 650, PAIR, 5),
			new Tear(656, 770, 0, 6));

	private static boolean on, wasHidden, known;
	private static CameraType wasCamera;
	private static Vec3 anchor = Vec3.ZERO, forward = Vec3.ZERO, across = Vec3.ZERO, eye = Vec3.ZERO;
	private static float yaw, pitch;
	private static int t, capX, capZ, nextId;
	private static final List<GateEntity> GATES = new ArrayList<>();

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

	public static void play(Net.IntroPlay m) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || on) return;
		on = true;
		anchor = Vec3.atBottomCenterOf(m.at().above());
		float a = m.yaw() * Mth.DEG_TO_RAD;
		forward = new Vec3(-Mth.sin(a), 0, Mth.cos(a));
		across = new Vec3(-forward.z, 0, forward.x);
		known = m.known();
		capX = m.x();
		capZ = m.z();
		t = 0;
		nextId = -800000;
		wasCamera = mc.options.getCameraType();
		wasHidden = mc.options.hideGui;
		mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
		mc.options.hideGui = true;
		frame(0);
		mc.setScreen(new Bars());
	}

	/** Done, or skipped: tell the server, and let go of the screen. */
	private static void finish() {
		Minecraft mc = Minecraft.getInstance();
		PacketDistributor.sendToServer(new Net.IntroDone());
		if (mc.screen instanceof Bars) mc.setScreen(null);
		else stop();
	}

	private static void stop() {
		if (!on) return;
		on = false;
		Minecraft mc = Minecraft.getInstance();
		mc.options.setCameraType(wasCamera);
		mc.options.hideGui = wasHidden;
		if (mc.level != null) for (GateEntity g : GATES) mc.level.removeEntity(g.getId(), Entity.RemovalReason.DISCARDED);
		GATES.clear();
	}

	private static Vec3 place(Vec3 local) {
		return anchor.add(forward.scale(local.x)).add(0, local.y, 0).add(across.scale(local.z));
	}

	/** Every frame, from the camera (ForgeCameraMixin), so it glides. */
	public static void frame(float pt) {
		Shot s = SHOTS.get(SHOTS.size() - 1);
		for (Shot c : SHOTS) if (t < c.to()) {
			s = c;
			break;
		}
		float k = Mth.clamp((t + pt - s.from()) / (s.to() - s.from()), 0, 1);
		k = k * k * (3 - 2 * k);
		eye = place(s.eyeA().lerp(s.eyeB(), k));
		Vec3 d = place(s.lookA().lerp(s.lookB(), k)).subtract(eye).normalize();
		yaw = (float) (Mth.atan2(-d.x, d.z) * Mth.RAD_TO_DEG);
		pitch = (float) (-Math.asin(d.y) * Mth.RAD_TO_DEG);
	}

	private static void play(SoundEvent s, float pitch, float volume) {
		Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(s, pitch, volume));
	}

	private static void tear(Tear g) {
		Minecraft mc = Minecraft.getInstance();
		Vec3 at = place(new Vec3(GATE_F, 0, g.s()));
		int ground = mc.level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Mth.floor(at.x), Mth.floor(at.z));
		GateEntity gate = GateEntity.vision(mc.level, new Vec3(at.x, ground, at.z), yawOf(forward), g.rank());
		if (gate == null) return;
		gate.setId(nextId--);
		mc.level.addEntity(gate);
		GATES.add(gate);
		play(SoundEvents.GLASS_BREAK, 0.5f, 0.7f);
		play(SoundEvents.BEACON_ACTIVATE, 0.5f, 0.6f);
	}

	private static float yawOf(Vec3 d) {
		return (float) (Mth.atan2(-d.x, d.z) * Mth.RAD_TO_DEG);
	}

	private static void shut() {
		Minecraft mc = Minecraft.getInstance();
		for (GateEntity g : GATES) mc.level.removeEntity(g.getId(), Entity.RemovalReason.DISCARDED);
		GATES.clear();
	}

	@SubscribeEvent
	static void tick(ClientTickEvent.Post e) {
		Minecraft mc = Minecraft.getInstance();
		if (!on) return;
		if (mc.level == null || mc.player == null) {
			stop();
			return;
		}
		t++;
		for (Tear g : TEARS) {
			if (t == g.at()) tear(g);
			if (t == g.shut()) shut();
		}
		if (t > 650 && t < 770 && t % 28 == 0) play(SoundEvents.WARDEN_HEARTBEAT, 0.7f, 1f);
		if (t == 656) play(SoundEvents.ELDER_GUARDIAN_CURSE, 0.5f, 0.4f);
		if (t == TITLE + 6) {
			play(SoundEvents.BELL_BLOCK, 0.6f, 1f);
			play(SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, 0.7f, 0.7f);
		}
		if (t >= Intro.LENGTH) finish();
	}

	@SubscribeEvent
	static void leaving(ClientPlayerNetworkEvent.LoggingOut e) {
		stop();
	}

	/** Holds you still, and draws the bars, the wagoner's words and the title. */
	private static final class Bars extends Screen {
		Bars() {
			super(Component.literal("The Road"));
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
		public boolean keyPressed(int key, int scan, int mods) {
			if (key == GLFW.GLFW_KEY_ESCAPE) finish();
			return true;
		}

		@Override
		public void renderBackground(GuiGraphics g, int mx, int my, float pt) {}

		@Override
		public void removed() {
			stop();
		}

		private static int alpha(float a) {
			return Math.max(4, Mth.floor(Mth.clamp(a, 0, 1) * 255)) << 24;
		}

		@Override
		public void render(GuiGraphics g, int mx, int my, float pt) {
			float now = t + pt;
			int bar = height / 8;
			float dark = 0;
			for (Shot s : SHOTS) {
				if (now < s.from() || now >= s.to()) continue;
				float in = s.from() == 0 ? FIRST_FADE : BLACK_FADE;
				dark = 1 - Mth.clamp(Math.min((now - s.from()) / in, (s.to() - now) / BLACK_FADE), 0, 1);
			}
			if (dark > 0.01f) g.fill(0, 0, width, height, alpha(dark));
			g.fill(0, 0, width, bar, 0xFF000000);
			g.fill(0, height - bar, width, height, 0xFF000000);
			for (Line l : LINES) {
				if (now < l.from() || now >= l.to()) continue;
				float a = Mth.clamp(Math.min(now - l.from(), l.to() - now) / WORDS_FADE, 0, 1);
				List<FormattedCharSequence> rows = font.split(Component.literal(l.text()), Math.min(width - 48, 380));
				int y = height - bar + 5;
				g.drawCenteredString(font, WHO, width / 2, y - 12 - rows.size() * 3, alpha(a) | EMBER);
				for (FormattedCharSequence row : rows) {
					g.drawCenteredString(font, row, width / 2, y, alpha(a) | 0xF0E8D8);
					y += 11;
				}
			}
			if (now >= TITLE) title(g, Mth.clamp((now - TITLE - 10) / 24, 0, 1));
			g.drawString(font, "Esc to skip", width - font.width("Esc to skip") - 8, 6, 0x90A09888);
		}

		private void title(GuiGraphics g, float a) {
			int mid = height / 2 - 18;
			var pose = g.pose();
			pose.pushPose();
			pose.translate(width / 2f, mid, 0);
			pose.scale(4, 4, 1);
			g.drawCenteredString(font, "HIGHMOURN", 0, 0, alpha(a) | 0xF0E8D8);
			pose.popPose();
			g.fill(width / 2 - 70, mid + 38, width / 2 + 70, mid + 39, alpha(a) | EMBER);
			if (known) {
				pose.pushPose();
				pose.translate(width / 2f, mid + 46, 0);
				pose.scale(1.5f, 1.5f, 1);
				g.drawCenteredString(font, "X " + capX + "    Z " + capZ, 0, 0, alpha(a) | EMBER);
				pose.popPose();
			}
			g.drawCenteredString(font, "The compass knows the way.", width / 2, mid + 66, alpha(a) | 0xB8B0A0);
		}
	}
}
