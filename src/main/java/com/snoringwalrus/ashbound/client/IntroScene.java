package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.List;

import org.lwjgl.glfw.GLFW;

import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.GateEntity;
import com.snoringwalrus.ashbound.Intro;
import com.snoringwalrus.ashbound.Net;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;

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
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.HitResult;
import net.neoforged.neoforge.client.event.RenderLivingEvent;
import net.minecraft.world.phys.Vec3;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientPlayerNetworkEvent;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * The wagoner's telling (Intro): the camera leaves you at the wagon and goes round it to Hob; as he tells of the gates
 * it runs through a whole dungeon, its halls, its monsters and its boss (DungeonRun); then he deals out his photographs
 * of an F, an E and a D gate (Photos), each with its rank written under it, says what's above those, and gives them to
 * you (Intro.done). Then he wishes you luck. Gates torn open on the road (GateEntity.vision, monsters stepping out of
 * them) are still here for a scene that wants them: TEARS and OUTS are empty while the photographs tell it. Everything's placed along the
 * wagon: f down the road, u up, s across it; the gates' shots from where they stand (the first stretch near the road
 * that's level, open, and seen from every spot the camera takes there), far enough back that a whole tear is in frame. The camera never goes through what's solid (it comes in front of it) and nothing alive
 * right at the lens is drawn. Esc skips.
 */
@EventBusSubscriber(modid = Ashbound.ID, value = Dist.CLIENT)
public final class IntroScene {
	private IntroScene() {}

	/** at the gates: placed from the gates' spot and ground, not the wagon's */
	private record Shot(int from, int to, Vec3 eyeA, Vec3 eyeB, Vec3 lookA, Vec3 lookB, boolean atGates) {}

	private record Line(int from, int to, String text) {}

	private record Tear(int at, int shut, float s, int rank) {}

	/** a monster stepping out of a gate: from `at` it walks `steps` blocks towards the camera over `walk` ticks, then waits */
	private record Out(int at, int walk, float s, String id, float steps) {}

	private record Walking(Out o, LivingEntity e) {}

	private static Shot shot(int from, int to, double f, double u, double s, double f2, double u2, double s2, double lf, double lu, double ls, double lf2, double lu2, double ls2) {
		return new Shot(from, to, new Vec3(f, u, s), new Vec3(f2, u2, s2), new Vec3(lf, lu, ls), new Vec3(lf2, lu2, ls2), false);
	}

	private static Shot gates(int from, int to, double f, double u, double s, double f2, double u2, double s2, double lf, double lu, double ls, double lf2, double lu2, double ls2) {
		return new Shot(from, to, new Vec3(f, u, s), new Vec3(f2, u2, s2), new Vec3(lf, lu, ls), new Vec3(lf2, lu2, ls2), true);
	}

	private static final String WHO = "Hob Tarrant";
	/** where down the road the gates may stand (how far, how far off to the side), how much room across and up they need,
	 *  and how far apart they are: a tear is drawn about 13 wide and 10 tall (GateRift x GateEntity.WIDE) */
	private static final int GATE_NEAR = 18, GATE_FAR = 44, GATE_ROOM = 15, GATE_TALL = 12, GATE_SLOPE = 3;
	private static final int[] GATE_ASIDE = {0, 6, -6, 12, -12};
	private static final float PAIR = 7.5f;
	/** nowhere clear found: the gate shots look down from this much higher, over whatever's in the way */
	private static final double LIFT = 7, OVER_GROUND = 1.3;
	/** the camera stops this short of whatever's in its way, and nothing alive this near it is drawn */
	private static final double LENS = 0.35, TOO_NEAR = 2.2;
	private static final int BLACK_FADE = 8, FIRST_FADE = 30, LAST_FADE = 40, WORDS_FADE = 6, EMBER = 0xFF9A30;

	/** The run through the dungeon (DungeonRun), between these ticks; if it isn't meshed in time, Hob's shot holds. */
	private static final int RUN_FROM = 250, RUN_MID = 360, RUN_TO = 470;

	private static final List<Shot> SHOTS = List.of(
			shot(0, 150, -11, 5, 7, -7, 3, 10, 1, 1, 0, 1, 1.2, 0),
			shot(150, RUN_FROM, 2.6, 1.8, 6, 2.2, 1.7, 5.4, 0.6, 1.5, 2.8, 0.6, 1.6, 2.8),
			shot(RUN_FROM, RUN_MID, 2.2, 1.7, 5.4, 2.1, 1.7, 5.25, 0.6, 1.6, 2.8, 0.6, 1.6, 2.8),
			shot(RUN_MID, RUN_TO, 2.1, 1.7, 5.25, 2.0, 1.7, 5.1, 0.6, 1.6, 2.8, 0.6, 1.6, 2.8),
			// back at the wagon while Hob deals out his photographs: over your shoulder, then a little closer
			shot(470, 600, 2.4, 1.8, 6.2, 2.1, 1.75, 5.5, 0.6, 1.5, 2.8, 0.6, 1.55, 2.8),
			shot(600, 720, -1.2, 1.8, 6.0, -0.9, 1.75, 5.4, 0.6, 1.5, 2.8, 0.6, 1.55, 2.8),
			shot(720, Intro.LENGTH, 0.6, 1.9, 8.2, 0.8, 1.8, 7.4, 0.6, 1.6, 2.8, 0.6, 1.6, 3.4));

	private static final List<Line> LINES = List.of(
			new Line(12, 76, "You fell out of a crack at dawn. I've pulled worse off this road."),
			new Line(80, 146, "Sit a moment. Nobody told me any of this, and it cost me two brothers."),
			new Line(156, 246, "They're opening all over these lands. The guild calls them gates."),
			new Line(258, 356, "Step through one and you're somewhere else. Halls full of things that don't sleep."),
			new Line(362, 466, "And at the bottom, something ruling it all. Kill that, and the gate lets you go home."),
			new Line(478, 554, "Here. I took these myself. A gate's colour is its rank. Pale is F, the weakest."),
			new Line(562, 624, "Green is E. Still forgiving, if you keep your head."),
			new Line(632, 716, "Blue is D: take friends. Past that they burn purple, orange, red. Leave those to the guild's best."),
			new Line(728, 840, "Keep the pictures. That's all I know. Good luck out there, and come back in one piece."));

	private static final List<Tear> TEARS = List.of();

	/** what steps out, and from which gate: a Drowned Cellar reveller, a Gallows walker, then the Hangman himself */
	private static final List<Out> OUTS = List.of();
	/** when each photograph is dealt (Photos.ALL's order), how long one takes to land, and when they're swept away */
	private static final int[] PHOTO_AT = {490, 566, 636};
	private static final int DEAL = 14, PHOTOS_GO = 712, SWEEP = 10;
	private static final float[] PHOTO_TURN = {-6, 1, 5};
	/** how wide a print is on screen, and how far the next lies from it */
	private static final float PHOTO_W = 0.34f, PHOTO_STEP = 0.62f, PHOTO_DIM = 0.35f;
	private static final List<Walking> WALKING = new ArrayList<>();

	private static boolean on, wasHidden, known;
	private static CameraType wasCamera;
	private static Vec3 anchor = Vec3.ZERO, forward = Vec3.ZERO, across = Vec3.ZERO, eye = Vec3.ZERO;
	/** where the gates stand: how far down the road, and their ground */
	private static double gateF = GATE_NEAR, gateS, gateY, lift;
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
		DungeonRun.prepare(anchor);
		findGates();
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
		shut();
		DungeonRun.close();
	}

	private static Vec3 place(Vec3 local) {
		return anchor.add(forward.scale(local.x)).add(0, local.y, 0).add(across.scale(local.z));
	}

	/** From the gates' spot: f back up the road from them, u over their ground. */
	private static Vec3 atGates(Vec3 local) {
		Vec3 p = place(new Vec3(gateF + local.x, 0, gateS + local.z));
		return new Vec3(p.x, gateY + local.y, p.z);
	}

	private static int ground(net.minecraft.client.multiplayer.ClientLevel l, Vec3 p, Heightmap.Types kind) {
		return l.getHeight(kind, Mth.floor(p.x), Mth.floor(p.z));
	}

	private static boolean sees(Vec3 from, Vec3 to) {
		Minecraft mc = Minecraft.getInstance();
		return mc.level.clip(new ClipContext(from, to, ClipContext.Block.VISUAL, ClipContext.Fluid.NONE, mc.player)).getType() == HitResult.Type.MISS;
	}

	/**
	 * The first spot near the road where the gates will be seen whole: room across for the pair, ground level enough, nothing
	 * standing in the tears' height (trees, a bank), and from every spot the camera takes there (each gate shot's start and
	 * end) it's in the open, over the ground, with a clear look at both tears.
	 */
	private static void findGates() {
		Minecraft mc = Minecraft.getInstance();
		lift = 0;
		for (int f = GATE_NEAR; f <= GATE_FAR; f += 2)
			for (int aside : GATE_ASIDE) {
				gateF = f;
				gateS = aside;
				Vec3 mid = atGates(Vec3.ZERO);
				int y = ground(mc.level, mid, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES), lo = y, hi = y;
				boolean open = true;
				for (int s = -GATE_ROOM; s <= GATE_ROOM && open; s += 2) {
					Vec3 p = place(new Vec3(f, 0, aside + s));
					int g = ground(mc.level, p, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES);
					lo = Math.min(lo, g);
					hi = Math.max(hi, g);
					for (int u = 1; u <= GATE_TALL && open; u += 2)
						open = mc.level.getBlockState(net.minecraft.core.BlockPos.containing(p.x, y + u, p.z)).isAir();
				}
				if (!open || hi - lo > GATE_SLOPE) continue;
				gateY = y;
				if (watched()) return;
			}
		gateF = GATE_NEAR + 4;   // nowhere clear: down the road on its ground, looked at from above what's in the way
		gateS = 0;
		gateY = ground(mc.level, atGates(Vec3.ZERO), Heightmap.Types.MOTION_BLOCKING_NO_LEAVES);
		lift = LIFT;
	}

	/** Every gate shot's camera, start and end, in the open over the ground and seeing both tears' middles and feet. */
	private static boolean watched() {
		Minecraft mc = Minecraft.getInstance();
		for (Shot s : SHOTS) {
			if (!s.atGates()) continue;
			for (Vec3 local : List.of(s.eyeA(), s.eyeB())) {
				Vec3 eye = atGates(local);
				if (ground(mc.level, eye, Heightmap.Types.MOTION_BLOCKING) > eye.y - OVER_GROUND) return false;
				for (Tear t : TEARS)
					if (!sees(eye, atGates(new Vec3(0, GateEntity.MID, t.s()))) || !sees(eye, atGates(new Vec3(0, 1.5, t.s())))) return false;
			}
		}
		return true;
	}

	/** Never under the ground or in a tree's crown where the camera is. */
	private static Vec3 overGround(Vec3 at) {
		Minecraft mc = Minecraft.getInstance();
		int g = ground(mc.level, at, Heightmap.Types.MOTION_BLOCKING);
		return at.y < g + OVER_GROUND && at.y > g - 12 ? new Vec3(at.x, g + OVER_GROUND, at.z) : at;
	}

	/** In front of whatever's solid between the camera and what it's looking at, never inside it. */
	private static Vec3 unblocked(Vec3 want, Vec3 at) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.level == null || mc.player == null) return want;
		var hit = mc.level.clip(new ClipContext(at, want, ClipContext.Block.VISUAL, ClipContext.Fluid.NONE, mc.player));
		return hit.getType() == HitResult.Type.MISS ? want : hit.getLocation().add(at.subtract(want).normalize().scale(LENS));
	}

	/** Nothing alive right at the lens (mobs, the horse, you): drawn there, it fills the screen from inside. */
	@SubscribeEvent
	static void tooNear(RenderLivingEvent.Pre<?, ?> e) {
		if (on && e.getEntity().distanceToSqr(eye) < TOO_NEAR * TOO_NEAR) e.setCanceled(true);
	}

	/** Every frame, from the camera (ForgeCameraMixin), so it glides. */
	public static void frame(float pt) {
		if (t >= RUN_FROM && t < RUN_TO && DungeonRun.ready()) {   // two cuts: its first halls, then up to its boss
			boolean last = t >= RUN_MID;
			float k = last ? (t + pt - RUN_MID) / (RUN_TO - RUN_MID) : (t + pt - RUN_FROM) / (RUN_MID - RUN_FROM);
			k = Mth.clamp(k, 0, 1);
			k = Mth.lerp(0.35f, k, k * k * (3 - 2 * k));
			eye = DungeonRun.cut(last, k);
			Vec3 d = DungeonRun.cutLook(last, k).subtract(eye).normalize();
			yaw = (float) (Mth.atan2(-d.x, d.z) * Mth.RAD_TO_DEG);
			pitch = (float) (-Math.asin(d.y) * Mth.RAD_TO_DEG);
			return;
		}
		Shot s = SHOTS.get(SHOTS.size() - 1);
		for (Shot c : SHOTS) if (t < c.to()) {
			s = c;
			break;
		}
		float k = Mth.clamp((t + pt - s.from()) / (s.to() - s.from()), 0, 1);
		k = k * k * (3 - 2 * k);
		Vec3 at = s.atGates() ? atGates(s.lookA().lerp(s.lookB(), k)) : place(s.lookA().lerp(s.lookB(), k));
		Vec3 want = s.atGates() ? atGates(s.eyeA().lerp(s.eyeB(), k)).add(0, lift, 0) : place(s.eyeA().lerp(s.eyeB(), k));
		eye = unblocked(overGround(want), at);
		Vec3 d = at.subtract(eye).normalize();
		yaw = (float) (Mth.atan2(-d.x, d.z) * Mth.RAD_TO_DEG);
		pitch = (float) (-Math.asin(d.y) * Mth.RAD_TO_DEG);
	}

	private static void play(SoundEvent s, float pitch, float volume) {
		Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(s, pitch, volume));
	}

	private static void tear(Tear g) {
		Minecraft mc = Minecraft.getInstance();
		Vec3 at = atGates(new Vec3(0, 0, g.s()));
		int ground = ground(mc.level, at, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES);
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
		if (mc.level != null) {
			for (GateEntity g : GATES) mc.level.removeEntity(g.getId(), Entity.RemovalReason.DISCARDED);
			for (Walking w : WALKING) mc.level.removeEntity(w.e().getId(), Entity.RemovalReason.DISCARDED);
		}
		GATES.clear();
		WALKING.clear();
	}

	private static Vec3 ground(Vec3 at) {
		Minecraft mc = Minecraft.getInstance();
		return new Vec3(at.x, mc.level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Mth.floor(at.x), Mth.floor(at.z)), at.z);
	}

	/** One of the gate's own monsters, only on this screen, held still but for the steps it's walked. */
	private static void out(Out o) {
		Minecraft mc = Minecraft.getInstance();
		var type = BuiltInRegistries.ENTITY_TYPE.getOptional(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, o.id()));
		if (type.isEmpty() || !(type.get().create(mc.level) instanceof LivingEntity e)) return;
		Vec3 at = ground(atGates(new Vec3(-0.6, 0, o.s())));
		float face = yawOf(forward.reverse());
		e.setId(nextId--);
		e.moveTo(at.x, at.y, at.z, face, 0);
		e.setYHeadRot(face);
		e.setYBodyRot(face);
		if (e instanceof Mob m) m.setNoAi(true);
		mc.level.addEntity(e);
		WALKING.add(new Walking(o, e));
		play(o.id().equals("hangman") ? SoundEvents.RAVAGER_ROAR : SoundEvents.ZOMBIE_AMBIENT, o.id().equals("hangman") ? 0.5f : 0.6f, 0.8f);
	}

	private static void walk() {
		for (Walking w : WALKING) {
			Out o = w.o();
			float k = Mth.clamp((t - o.at()) / (float) o.walk(), 0, 1);
			Vec3 at = ground(atGates(new Vec3(-0.6 - o.steps() * k, 0, o.s())));
			float face = yawOf(forward.reverse());
			w.e().lerpTo(at.x, at.y, at.z, face, 0, 3);
			w.e().setYHeadRot(face);
		}
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
		for (Out o : OUTS) if (t == o.at()) out(o);
		walk();
		if (t == RUN_FROM) {
			DungeonRun.begin();
			play(SoundEvents.AMBIENT_CAVE.value(), 1f, 0.6f);
		}
		if (t > RUN_FROM && t < RUN_TO && t % 40 == 0) play(SoundEvents.WATER_AMBIENT, 0.8f, 0.5f);
		if (t == RUN_TO - 40) play(SoundEvents.RAVAGER_ROAR, 0.55f, 0.7f);
		if (t == RUN_TO) DungeonRun.end();
		for (int at : PHOTO_AT) if (t == at) play(SoundEvents.BOOK_PAGE_TURN, 0.8f, 1f);
		if (t == PHOTOS_GO) play(SoundEvents.BOOK_PAGE_TURN, 1.1f, 0.8f);
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

		/** Hob's photographs, each dealt onto the last from below, a little turned, then all swept away together. */
		private void photos(GuiGraphics g, float now) {
			if (now < PHOTO_AT[0] || now > PHOTOS_GO + SWEEP) return;
			float gone = Mth.clamp((now - PHOTOS_GO) / SWEEP, 0, 1), w = Math.min(width * PHOTO_W, height * 0.58f * Photos.W / Photos.H);
			g.fill(0, 0, width, height, alpha(PHOTO_DIM * Mth.clamp((now - PHOTO_AT[0]) / DEAL, 0, 1) * (1 - gone)));
			for (int i = 0; i < Photos.ALL.size(); i++) {
				float k = Mth.clamp((now - PHOTO_AT[i]) / DEAL, 0, 1);
				if (k <= 0) continue;
				float e = 1 - (1 - k) * (1 - k) * (1 - k), away = gone * gone;
				float x = width / 2f + (i - 1) * w * PHOTO_STEP, y = height * 0.44f + (i == 1 ? -6 : 6) + (1 - e) * height * 0.7f + away * height;
				Photos.draw(g, font, Photos.ALL.get(i), x, y, w, PHOTO_TURN[i] + (1 - e) * (i - 1) * 14, Math.min(1, k * 2));
			}
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
				float in = s.from() == 0 ? FIRST_FADE : BLACK_FADE, out = s.to() == Intro.LENGTH ? LAST_FADE : BLACK_FADE;
				dark = 1 - Mth.clamp(Math.min((now - s.from()) / in, (s.to() - now) / out), 0, 1);
			}
			if (dark > 0.01f) g.fill(0, 0, width, height, alpha(dark));
			photos(g, now);
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
			g.drawString(font, "Esc to skip", width - font.width("Esc to skip") - 8, 6, 0x90A09888);
		}
	}
}
