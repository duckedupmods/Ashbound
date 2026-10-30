package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.List;

import org.lwjgl.glfw.GLFW;

import com.snoringwalrus.ashbound.Gear;
import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Npc;
import com.snoringwalrus.ashbound.Smithing;

import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Strike with the Master, played over the world (ForgeScene is the stage). The first step: hold, and let go when the
 * work's the right colour. The duet: the master taps a bar, you answer it, three rounds, and each good blow beats the
 * work closer to its shape. The last step: click as it cools through the mark. All timed from the clock on each frame,
 * never the 20 a second ticks: a blow has to be right to the hundredth.
 *
 * A friend on the master's side plays the same bars from the other end: their taps are what you hear, they work the
 * bellows with you, and how well they kept time adds to the work. Theirs follows yours, stage by stage.
 */
public class ForgeStrikeScreen extends Screen {
	private enum Stage { FADE, FIRE, DUET, QUENCH, COOL, DONE }

	private static final float HEAT_AIM = 0.8f, HEAT_ZONE = 0.09f, COOL_AIM = 0.42f, COOL_ZONE = 0.07f;
	private static final float PERFECT = 0.08f, GOOD = 0.16f, LATE = 0.24f;
	/** Beats in a round: the master's bar, a two-beat breath with a count, your bar, a beat's rest. */
	private static final int READY_AT = 4, YOURS_AT = 6, REST_AT = 10, ROUND = 11;
	private static final int ROUNDS = 3, BAR_W = 260;

	private record Note(float at, boolean answer, int round, float beat) {}

	private final Net.ForgeStart m;
	private final Net.Job job;
	private final boolean helper;
	private final Smithing.Metal metal, metal2;
	/** The Joining: a fire for each piece, each on its own mouse button, and both have to land. */
	private final boolean fuse;
	private float heat2, fireScore2;
	private boolean held2, pressed2, done1, done2;
	private final Smithing.Craft craft;
	private final ItemStack made, result;
	private final String smithName;
	private final float beat;
	private final float bonus; // a dwarf's touch
	private final List<Note> notes = new ArrayList<>();
	private final float[] judged; // how each note went: -1 not yet, 0 missed, up to 1 dead on
	private final List<Float> counts = new ArrayList<>();
	private int nextTap, count;

	private Stage stage = Stage.FADE;
	private long stageStart = System.nanoTime();
	private boolean held, finished, pressed, partner, partnerPump;
	private float heat, fireScore, quenchScore, score, partnerSum;
	private int strays, partnerNotes;
	private float flash;
	private Smithing.Quality quality;
	private boolean took;
	private String line = "";
	private EditBox nameBox;

	static void open(Net.ForgeStart m) {
		Minecraft mc = Minecraft.getInstance();
		Net.Job j = m.job();
		var inv = mc.player.getInventory().items;
		ItemStack made, result, other = ItemStack.EMPTY;
		String kind;
		if (j.type() == Smithing.MAKE) {
			Item it = Gear.item(Gear.DUNGEONS.get(j.gate()).recipes().get(j.recipe()).id());
			if (it == null) return;
			made = result = new ItemStack(it);
			kind = Smithing.kind(it);
		} else {
			// a friend's client has its own pack: the job carries the piece's id and + for them (Smithing.shared)
			ItemStack from = m.worker() < 0 ? inv.get(j.slot()).copy()
					: Smithing.shown(net.minecraft.core.registries.BuiltInRegistries.ITEM.byId(j.slot()), j.type() == Smithing.UPGRADE ? j.gate() : 0);
			made = from;
			kind = j.type() == Smithing.FUSE && com.snoringwalrus.ashbound.Joined.is(from) ? Smithing.boss(from).kind() : Smithing.kind(made.getItem());
			if (j.type() == Smithing.FUSE) {
				var reg = net.minecraft.core.registries.BuiltInRegistries.ITEM;
				other = m.worker() < 0 ? inv.get(j.gate()).copy() : new ItemStack(reg.byId(j.gate()));
				result = m.worker() < 0 ? com.snoringwalrus.ashbound.Joined.result(from, other) : new ItemStack(Gear.item(com.snoringwalrus.ashbound.Joined.of(kind).id()));
			} else result = from;
		}
		ForgeScene.start(m, made, Smithing.Craft.of(kind), j.type() != Smithing.MAKE, m.worker() >= 0);
		ForgeScene.second(other);
		mc.setScreen(new ForgeStrikeScreen(m, made, other, result, kind));
	}

	private ForgeStrikeScreen(Net.ForgeStart m, ItemStack made, ItemStack other, ItemStack result, String kind) {
		super(Component.literal("Forging"));
		this.m = m;
		this.job = m.job();
		this.helper = m.worker() >= 0;
		this.made = made;
		this.result = result;
		Gear.Dungeon gate = Smithing.home(made.getItem());
		if (gate == null) gate = job.gate() >= 0 && job.gate() < Gear.DUNGEONS.size() ? Gear.DUNGEONS.get(job.gate()) : Gear.DUNGEONS.get(0);
		ForgeScene.tint(gate.colour());
		metal = Smithing.metal(gate);
		Gear.Dungeon gate2 = other.isEmpty() ? null : Smithing.home(other.getItem());
		fuse = job.type() == Smithing.FUSE && !helper;
		metal2 = gate2 == null ? metal : Smithing.metal(gate2);
		craft = Smithing.Craft.of(kind);
		Npc smith = Minecraft.getInstance().level.getEntity(m.smith()) instanceof Npc n ? n : null;
		boolean dwarf = smith != null && smith.is("dwarf");
		smithName = smith != null ? smith.getName().getString() : job.type() == Smithing.FUSE ? "The Forge" : "";
		bonus = dwarf ? 0.03f : 0;
		beat = 0.36f / metal.tempo() / Smithing.tempo(job, made) / (dwarf ? 1.12f : 1f);
		float[][] p = Smithing.pattern(kind);
		boolean fights = Smithing.fights(job, made, metal);
		counts.add(0f);
		counts.add(beat);
		float t = beat * 2; // two counts in
		for (int r = 0; r < ROUNDS; r++) {
			float[] call = r == ROUNDS - 1 ? p[1] : p[0];
			float[] back = r == ROUNDS - 1 && fights ? p[0] : call;
			for (float b : call) notes.add(new Note(t + b * beat, false, r, b));
			counts.add(t + READY_AT * beat);
			counts.add(t + (READY_AT + 1) * beat);
			for (float b : back) notes.add(new Note(t + YOURS_AT * beat + b * beat, true, r, b));
			t += ROUND * beat;
		}
		judged = new float[notes.size()];
		java.util.Arrays.fill(judged, -1);
	}

	private float now() {
		return (System.nanoTime() - stageStart) * 1e-9f;
	}

	private void go(Stage s) {
		stage = s;
		stageStart = System.nanoTime();
		if (!helper) relay(Smithing.STAGE, s.ordinal());
	}

	private static void relay(int action, float value) {
		if (Minecraft.getInstance().getConnection() != null) PacketDistributor.sendToServer(new Net.ForgeRelay(action, value));
	}

	/** Whether a note is this player's to play. */
	private boolean mine(Note n) {
		return n.answer() != helper;
	}

	/** What the other one at the anvil did. */
	void heard(int action, float value) {
		switch (action) {
			case Smithing.JOINED -> partner = true;
			case Smithing.LEAVE -> {
				partner = false;
				partnerPump = false;
			}
			case Smithing.BELLOWS -> partnerPump = value > 0;
			case Smithing.MASTER -> {
				partnerSum += value;
				partnerNotes++;
			}
			case Smithing.SWING -> {
				if (helper && value > 0) ForgeScene.shape = Math.min(1, ForgeScene.shape + 1f / Math.max(1, notes.size() / 2));
			}
			case Smithing.RESULT -> {
				score = value;
				settle();
			}
			case Smithing.STAGE -> {
				Stage s = Stage.values()[(int) value];
				if (s == Stage.QUENCH) heat = 1;
				if (s == Stage.DONE) reveal();
				else go(s);
			}
			case Smithing.END -> {
				if (helper && stage != Stage.DONE) onClose();
			}
			default -> {}
		}
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {}

	@Override
	public void tick() {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null) return;
		if (mc.player.hurtTime > 0 || mc.player.distanceToSqr(m.anvil().getCenter()) > 25) onClose();
		if (stage == Stage.FIRE && held) ForgeScene.bellows(heat);
		if (helper && stage == Stage.DONE && now() > 4f) onClose();
	}

	// ---------------------------------------------------------------- your hands

	private void press2() {
		if (stage == Stage.FIRE && fuse && !pressed2) pressed2 = held2 = true;
	}

	private void release2() {
		if (stage != Stage.FIRE || !held2) return;
		held2 = false;
		done2 = true;
		fireScore2 = zone(heat2, HEAT_AIM, HEAT_ZONE);
		if (done1) fired();
	}

	private void press() {
		if (stage == Stage.FIRE && !pressed) {
			pressed = held = true;
			if (helper) relay(Smithing.BELLOWS, 1);
		} else if (stage == Stage.DUET) {
			blow();
		} else if (stage == Stage.QUENCH && !helper) {
			plunge();
		} else if (stage == Stage.DONE && nameBox == null && now() > 0.8f) {
			finish();
		}
	}

	private void release() {
		if (stage == Stage.FIRE && held) {
			held = false;
			if (helper) {
				relay(Smithing.BELLOWS, 0);
				pressed = false; // pump again if you like
			} else if (fuse && !done2) {
				done1 = true;
				fireScore = zone(heat, HEAT_AIM, HEAT_ZONE);
			} else fired();
		}
	}

	private void fired() {
		fireScore = fuse ? (zone(heat, HEAT_AIM, HEAT_ZONE) + fireScore2) / 2 : zone(heat, HEAT_AIM, HEAT_ZONE);
		go(Stage.DUET);
	}

	private static float zone(float v, float aim, float width) {
		float off = Math.abs(v - aim);
		return off <= width * 0.4f ? 1 : Math.max(0, 1 - (off - width * 0.4f) / (width * 1.6f));
	}

	private void blow() {
		float t = now();
		int best = -1;
		float off = LATE;
		for (int i = 0; i < notes.size(); i++) {
			if (!mine(notes.get(i)) || judged[i] >= 0) continue;
			float d = Math.abs(t - notes.get(i).at());
			if (d < off) {
				off = d;
				best = i;
			}
		}
		float how = 0;
		if (best < 0) strays++;
		else {
			how = judged[best] = off <= PERFECT ? 1f : off <= GOOD ? 0.65f : 0.3f;
			flash = 1;
		}
		if (helper) {
			ForgeScene.tap();
			relay(Smithing.MASTER, how);
		} else {
			ForgeScene.strike(how);
			relay(Smithing.SWING, how);
		}
	}

	private void plunge() {
		quenchScore = zone(heat, COOL_AIM, COOL_ZONE);
		ForgeScene.quench(quenchScore);
		total();
		relay(Smithing.RESULT, score);
		go(Stage.COOL);
	}

	/** A fifth the first step, three fifths the blows, a fifth the last; what a friend or a dwarf adds on top. */
	private void total() {
		float sum = 0;
		int n = 0;
		for (int i = 0; i < notes.size(); i++)
			if (notes.get(i).answer()) {
				sum += Math.max(0, judged[i]);
				n++;
			}
		float friend = partnerNotes == 0 ? 0 : 0.05f * partnerSum / partnerNotes;
		score = Math.max(0, 0.2f * fireScore + 0.6f * sum / Math.max(1, n) + 0.2f * quenchScore - Math.min(0.2f, strays * 0.02f)) + friend + bonus;
		settle();
	}

	private void settle() {
		quality = Smithing.Quality.of(score);
		took = job.type() == Smithing.UPGRADE && score >= Smithing.need(Smithing.plus(made));
		line = Smithing.line(quality, (int) (System.nanoTime() >> 20));
	}

	private void reveal() {
		ForgeScene.shape = 1;
		ForgeScene.heat = 0;
		ForgeScene.join = 1;
		ForgeScene.show(result);
		if (job.type() == Smithing.FUSE) ForgeScene.pillar();
		ForgeScene.reveal(quality == null ? Smithing.Quality.FINE : quality);
		if (quality == Smithing.Quality.PERFECT && job.type() != Smithing.UPGRADE && !helper) {
			nameBox = new EditBox(font, width / 2 - 90, height - 62, 180, 16, Component.literal("Name"));
			nameBox.setMaxLength(32);
			nameBox.setHint(Component.literal("Name it, or Enter to leave it").withStyle(ChatFormatting.DARK_GRAY));
			addRenderableWidget(nameBox);
			setInitialFocus(nameBox);
		}
		go(Stage.DONE);
	}

	private void finish() {
		if (finished) return;
		finished = true;
		ForgeScene.stop();
		if (!helper) PacketDistributor.sendToServer(new Net.ForgeDone(score, nameBox == null ? "" : nameBox.getValue()));
		else relay(Smithing.LEAVE, 0);
		onClose();
	}

	@Override
	public void removed() {
		if (finished) return;
		finished = true;
		ForgeScene.stop();
		if (Minecraft.getInstance().getConnection() == null) return;
		if (helper) relay(Smithing.LEAVE, 0);
		else PacketDistributor.sendToServer(new Net.ForgeDone(-1, ""));
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		if (nameBox != null) return super.mouseClicked(mx, my, button);
		if (button == 1) press2();
		else press();
		return true;
	}

	@Override
	public boolean mouseReleased(double mx, double my, int button) {
		if (button == 1) release2();
		else release();
		return true;
	}

	@Override
	public boolean keyPressed(int key, int scan, int mods) {
		if (nameBox != null && (key == GLFW.GLFW_KEY_ENTER || key == GLFW.GLFW_KEY_KP_ENTER)) {
			finish();
			return true;
		}
		if (key == GLFW.GLFW_KEY_SPACE && nameBox == null) {
			press();
			return true;
		}
		return super.keyPressed(key, scan, mods);
	}

	@Override
	public boolean keyReleased(int key, int scan, int mods) {
		if (key == GLFW.GLFW_KEY_SPACE) release();
		return super.keyReleased(key, scan, mods);
	}

	// ---------------------------------------------------------------- the clock

	private void step(float dt) {
		float t = now();
		switch (stage) {
			case FADE -> {
				if (t > 0.5f && !helper) go(Stage.FIRE);
			}
			case FIRE -> {
				if (held || partnerPump) heat += metal.rise() * dt * (held && partnerPump ? 1.6f : 1f);
				else heat = Math.max(0, heat - metal.fall() * 0.25f * dt);
				ForgeScene.heat = fuse ? Math.max(heat, heat2) : heat;
				if (helper) break;
				if (fuse) {
					if (held2) heat2 += metal2.rise() * dt;
					else if (!done2) heat2 = Math.max(0, heat2 - metal2.fall() * 0.25f * dt);
					if (heat >= 1.15f && held) release();
					if (heat2 >= 1.15f && held2) release2();
					if (t > 9f) {
						fireScore2 = done2 ? fireScore2 : zone(heat2, HEAT_AIM, HEAT_ZONE);
						fired();
					}
				} else if (heat >= 1.15f) {
					held = false;
					fired();
				} else if (t > 7f) fired();
			}
			case DUET -> {
				while (count < counts.size() && t >= counts.get(count)) {
					ForgeScene.count();
					count++;
				}
				while (nextTap < notes.size() && t >= notes.get(nextTap).at()) {
					if (!notes.get(nextTap).answer() && !helper && !partner) ForgeScene.tap();
					nextTap++;
				}
				int done = 0, all = 0;
				for (int i = 0; i < notes.size(); i++) {
					Note n = notes.get(i);
					if (!mine(n)) continue;
					all++;
					if (judged[i] < 0 && t > n.at() + LATE) judged[i] = 0;
					done += judged[i] > 0 ? 1 : 0;
				}
				if (job.type() == Smithing.FUSE) ForgeScene.join += (done / (float) all - ForgeScene.join) * Math.min(1, dt * 10);
				else if (!helper && job.type() != Smithing.UPGRADE) ForgeScene.shape += (done / (float) all - ForgeScene.shape) * Math.min(1, dt * 10);
				ForgeScene.dolly = Math.min(0.6f, t * 0.06f);
				ForgeScene.heat = Math.max(0.55f, Math.min(0.95f, heat) - t * 0.03f) + flash * 0.15f;
				flash *= Math.max(0, 1 - dt * 8);
				if (!helper && t > notes.get(notes.size() - 1).at() + 2 * beat + 0.2f) {
					heat = 1;
					ForgeScene.lift = 0.12f;
					go(Stage.QUENCH);
				}
			}
			case QUENCH -> {
				heat -= metal.fall() * dt;
				ForgeScene.heat = heat;
				if (heat <= 0.1f && !helper) plunge();
			}
			case COOL -> {
				ForgeScene.lift = Math.max(-0.5f, ForgeScene.lift - dt * 4);
				ForgeScene.heat = Math.max(0, ForgeScene.heat - dt * 2);
				if (t > 1.1f && !helper) reveal();
			}
			case DONE -> {
				ForgeScene.lift = Math.min(0.75f, 0.1f + t * 1.2f);
				ForgeScene.spin += dt * 50;
				ForgeScene.dolly = Math.min(1f, 0.6f + t * 0.5f);
			}
		}
	}

	// ---------------------------------------------------------------- drawing

	private long last = System.nanoTime();

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		long n = System.nanoTime();
		step(Math.min(0.05f, (n - last) * 1e-9f));
		last = n;
		switch (stage) {
			case FADE -> {
				g.fill(0, 0, width, height, (int) (Math.max(0, 1 - now() * 2) * 255) << 24);
				if (helper) title(g, "WAITING AT THE ANVIL", AshUi.BODY, "You've taken the master's side");
			}
			case FIRE -> fire(g);
			case DUET -> duet(g);
			case QUENCH -> quench(g);
			case COOL -> {}
			case DONE -> done(g);
		}
		super.render(g, mx, my, pt);
	}

	private int barX() {
		return (width - BAR_W) / 2;
	}

	private int barY() {
		return height - 44;
	}

	private void title(GuiGraphics g, String s, int colour, String sub) {
		Component t = Component.literal(s).withStyle(ChatFormatting.BOLD);
		g.drawString(font, t, (width - font.width(t)) / 2, barY() - 24, colour, true);
		if (sub != null) g.drawString(font, sub, (width - font.width(sub)) / 2, barY() + 20, AshUi.MUTED, true);
	}

	/** A gauge with its mark: dull red up to white (for cloth, the gate's colour deepening), and where to stop. */
	private void gauge(GuiGraphics g, float v, float aim, float zone, int y) {
		int x = barX(), h = 12;
		AshUi.inset(g, x - 2, y - 2, BAR_W + 4, h + 4);
		for (int i = 0; i < BAR_W; i++) {
			float k = i / (float) BAR_W;
			g.fill(x + i, y, x + i + 1, y + h, 0xFF000000 | ForgeScene.gaugeColour(k));
		}
		int z0 = x + (int) ((aim - zone) * BAR_W), z1 = x + (int) ((aim + zone) * BAR_W);
		g.fill(z0, y - 3, z1, y, AshUi.EMBER_LT);
		g.fill(z0, y + h, z1, y + h + 3, AshUi.EMBER_LT);
		g.fill(z0, y, z0 + 1, y + h, 0xCCFFFFFF);
		g.fill(z1 - 1, y, z1, y + h, 0xCCFFFFFF);
		int nx = x + (int) (Math.max(0, Math.min(1, v)) * BAR_W);
		g.fill(nx - 1, y - 4, nx + 1, y + h + 4, 0xFFFFFFFF);
	}

	private void fire(GuiGraphics g) {
		if (helper) title(g, "THE BELLOWS", AshUi.EMBER_LT, "Hold to pump with them");
		else if (fuse) title(g, "TWO FIRES", AshUi.EMBER_LT, "Left and right mouse: hold each, let go in the mark");
		else title(g, craft.fire, AshUi.EMBER_LT, pressed ? "Let go in the mark" : craft.fireHint);
		gauge(g, heat, HEAT_AIM, HEAT_ZONE, barY());
		if (fuse) gauge(g, heat2, HEAT_AIM, HEAT_ZONE, barY() + 24);
		String w = craft.cloth ? "" : metal.word();
		g.drawString(font, w, (width - font.width(w)) / 2, barY() - 12, AshUi.BODY, true);
	}

	private void quench(GuiGraphics g) {
		title(g, craft.last, 0xFF9AD0F0, helper ? null : craft.lastHint);
		gauge(g, heat, COOL_AIM, COOL_ZONE, barY());
	}

	private void duet(GuiGraphics g) {
		float t = now(), first = notes.get(0).at();
		float since = (t - first) / beat;
		int round = since < 0 ? 0 : Math.min(ROUNDS - 1, (int) (since / ROUND));
		float in = since - round * ROUND;
		boolean answering = in >= READY_AT, yours = answering != helper, ready = in >= READY_AT && in < YOURS_AT;
		float into = since < 0 ? 0 : answering ? Math.max(0, Math.min(1, (in - YOURS_AT) / 4)) : in / 4;
		String who = since < 0 ? "LISTEN" : ready ? (in < READY_AT + 1 ? "READY" : "READY...") : yours ? "YOUR TURN" : helper ? "THEIR TURN" : smithName.isEmpty() ? "LISTEN" : smithName.toUpperCase();
		if (job.type() == Smithing.FUSE && round == ROUNDS - 1 && !ready) who = yours ? "HOLD IT TOGETHER" : "IT'S FIGHTING YOU";
		title(g, who, yours ? AshUi.EMBER_LT : AshUi.TEXT, "Click or Space on the marks");
		int x = barX(), y = barY(), h = 14;
		AshUi.inset(g, x - 2, y - 2, BAR_W + 4, h + 4);
		for (int b = 0; b < 4; b++) g.fill(x + b * BAR_W / 4, y, x + b * BAR_W / 4 + 1, y + h, 0xFF3D3833);
		for (int i = 0; i < notes.size(); i++) {
			Note n = notes.get(i);
			if (n.round() != round || n.answer() != answering) continue;
			int nx = x + (int) (n.beat() / 4f * BAR_W);
			boolean past = t >= n.at();
			int c = yours ? judged[i] < 0 ? 0xFFECE4D6 : judged[i] >= 1 ? 0xFFFFD24A : judged[i] > 0 ? 0xFFE8742C : 0xFF55504A
					: past ? 0xFFFFD24A : 0xFF8A8278;
			int r = yours && judged[i] >= 1 ? 6 : 4;
			g.fill(nx - r + 1, y + h / 2 - r, nx + r - 1, y + h / 2 + r, c);
		}
		int head = x + (int) (into * BAR_W);
		g.fill(head, y - 3, head + 1, y + h + 3, yours ? AshUi.EMBER_LT : 0xFFD9D2C5);
		for (int r = 0; r < ROUNDS; r++) {
			int px = width / 2 - 18 + r * 14;
			g.fill(px, y + h + 6, px + 8, y + h + 8, r <= round ? AshUi.EMBER_C : 0xFF3D3833);
		}
	}

	private void done(GuiGraphics g) {
		float t = now();
		int a = (int) (Math.min(1, t * 3) * 255) << 24;
		boolean upgrade = job.type() == Smithing.UPGRADE;
		String big = quality == null ? "" : upgrade ? took ? "+" + (Smithing.plus(made) + 1) : "IT DIDN'T TAKE"
				: job.type() == Smithing.FUSE ? "JOINED" : quality.title.toUpperCase();
		int colour = upgrade ? took ? 0xFFD24A : 0xE07A62 : quality == null ? 0xFFFFFF : quality.colour.getColor();
		g.pose().pushPose();
		g.pose().translate(width / 2f, 34, 0);
		g.pose().scale(3f, 3f, 1f);
		Component q = Component.literal(big).withStyle(ChatFormatting.BOLD);
		g.drawString(font, q, -font.width(q) / 2, 0, a | colour, true);
		g.pose().popPose();
		String item = upgrade && !took ? "Your materials are spent. The piece is unharmed." : result.getHoverName().getString();
		g.drawString(font, item, (width - font.width(item)) / 2, 66, a | 0xECE4D6, true);
		if (!smithName.isEmpty() && t > 0.5f) {
			String l = smithName + ": \"" + line + "\"";
			g.drawString(font, l, (width - font.width(l)) / 2, height - 84, 0xFFD9D2C5, true);
		}
		if (nameBox == null && t > 0.8f && !helper) {
			String hint = "Click to take it";
			g.drawString(font, hint, (width - font.width(hint)) / 2, height - 30, AshUi.MUTED, true);
		}
	}
}
