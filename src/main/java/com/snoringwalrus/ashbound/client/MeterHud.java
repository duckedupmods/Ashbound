package com.snoringwalrus.ashbound.client;

import java.util.Comparator;
import java.util.List;
import java.util.function.ToDoubleFunction;

import com.mojang.blaze3d.systems.RenderSystem;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Net;

import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.ChatScreen;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.ClientPlayerNetworkEvent;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;
import net.neoforged.neoforge.common.NeoForge;

/**
 * Damage and healing per second for the party (or you alone) over this fight, from Meters. Where it sits, how big it is and whether it's
 * up only in fights or all the time are each player's own (HudPrefs), set on MeterSetup. Left up, it keeps showing the last fight.
 */
public final class MeterHud {
	private MeterHud() {}

	private static final int W = 184, STRIP = 13, HEAD = 12, ROW = 11, GAP = 3, PAD = 4, FACE = 8, FACE_GAP = 2, SHARE_W = 26, HOLD = 15000, FADE = 3000, LIVE = 11000, MARGIN = 6;
	private static final int DAMAGE_TOP = 0xC2502A, DAMAGE_LOW = 0x7A2A14, HEALING_TOP = 0x4FA868, HEALING_LOW = 0x2A6A40, PANEL = 0x050404, RIM = 0x4A443E;
	private static final int DAMAGE_TEXT = 0xE8966A, HEALING_TEXT = 0x8CCB9C, BONE = 0xF0E8D8;

	public static void hooks(IEventBus bus) {
		bus.addListener((RegisterGuiLayersEvent e) -> e.registerAbove(VanillaGuiLayers.HOTBAR,
				ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "meters"), MeterHud::draw));
		NeoForge.EVENT_BUS.addListener((ClientPlayerNetworkEvent.LoggingOut e) -> Net.clientMeter = null);
	}

	private static float alpha(long age) {
		return age < HOLD - FADE ? 1 : Math.max(0, (HOLD - age) / (float) FADE);
	}

	private static int tint(int rgb, int top, float a) {
		return Math.max(8, Math.round(top * a)) << 24 | rgb;
	}

	private static void draw(GuiGraphics g, DeltaTracker dt) {
		Minecraft mc = Minecraft.getInstance();
		if (HudPrefs.meterShow == HudPrefs.OFF || mc.player == null || mc.options.hideGui || !(mc.screen == null || mc.screen instanceof ChatScreen)) return;
		Net.Meter m = Net.clientMeter;
		long age = System.currentTimeMillis() - Net.clientMeterAt;
		float a = HudPrefs.meterShow == HudPrefs.ALWAYS ? 1 : m == null ? 0 : alpha(age);
		if (a <= 0) return;
		String state = m == null ? "No fight yet" : (age < LIVE ? "Fight " : "Last fight ") + clock(m.seconds());
		paint(g, mc, m, state, m != null && age < LIVE, a);
	}

	private static String clock(float seconds) {
		int s = Math.round(seconds);
		return String.format("%d:%02d", s / 60, s % 60);
	}

	private static List<Net.MeterLine> lines(Net.Meter m, ToDoubleFunction<Net.MeterLine> of) {
		return m == null ? List.of() : m.lines().stream().filter(l -> of.applyAsDouble(l) > 0).sorted(Comparator.comparingDouble(of).reversed()).toList();
	}

	private static List<Net.MeterLine> hit(Net.Meter m) {
		return HudPrefs.meterView == HudPrefs.ONLY_HEALING ? List.of() : lines(m, Net.MeterLine::damage);
	}

	private static List<Net.MeterLine> healed(Net.Meter m) {
		return HudPrefs.meterView == HudPrefs.ONLY_DAMAGE ? List.of() : lines(m, Net.MeterLine::heal);
	}

	/** per second: a tenth shown under 10, so a slow healer doesn't read as 1 */
	static String rate(double n) {
		return n < 10 ? String.format("%.1f", n) : HitNumbers.shortly((float) n);
	}

	private static int blockHigh(List<Net.MeterLine> lines) {
		return lines.isEmpty() ? 0 : GAP + HEAD + lines.size() * ROW;
	}

	/** Where it goes on a screen this size, {x, y, w, h}. The saved place is a share of the free room, so a meter on an edge stays on it as it grows or the GUI scale changes. */
	static int[] box(Net.Meter m, int screenW, int screenH) {
		float s = HudPrefs.scale();
		int w = Math.round(W * s), h = Math.round((STRIP + blockHigh(hit(m)) + blockHigh(healed(m)) + PAD) * s);
		return new int[] {MARGIN + Math.round(room(screenW, w) * HudPrefs.meterX), MARGIN + Math.round(room(screenH, h) * HudPrefs.meterY), w, h};
	}

	/** How far the meter can travel along a side this long. */
	static int room(int side, int size) {
		return Math.max(1, side - 2 * MARGIN - size);
	}

	static float share(int at, int side, int size) {
		return (at - MARGIN) / (float) room(side, size);
	}

	static void paint(GuiGraphics g, Minecraft mc, Net.Meter m, String state, boolean live, float a) {
		int[] b = box(m, g.guiWidth(), g.guiHeight());
		float s = HudPrefs.scale();
		g.pose().pushPose();
		g.pose().translate(b[0], b[1], 0);
		g.pose().scale(s, s, 1);
		List<Net.MeterLine> hit = hit(m), healed = healed(m);
		frame(g, W, Math.round(b[3] / s), a);
		if (live) g.fill(PAD + 1, 5, PAD + 4, 8, tint(AshUi.EMBER_C & 0xFFFFFF, 255, a));
		g.drawString(mc.font, state, PAD + (live ? 7 : 1), 3, tint((live ? AshUi.TEXT : AshUi.MUTED) & 0xFFFFFF, 255, a), false);
		g.fill(PAD, STRIP - 1, W - PAD, STRIP, tint(AshUi.EMBER_C & 0xFFFFFF, 90, a));
		float seconds = m == null ? 1 : m.seconds();
		int y = block(g, mc, "Damage", hit, Net.MeterLine::damage, DAMAGE_TOP, DAMAGE_LOW, DAMAGE_TEXT, seconds, STRIP, a);
		block(g, mc, "Healing", healed, Net.MeterLine::heal, HEALING_TOP, HEALING_LOW, HEALING_TEXT, seconds, y, a);
		g.pose().popPose();
	}

	/** Dark glass with a thin iron rim and the corners cut, the small cousin of AshUi.panel: this one can sit on the screen all day. */
	private static void frame(GuiGraphics g, int w, int h, float a) {
		int fill = tint(PANEL, 0xB4, a), rim = tint(RIM, 255, a);
		g.fill(2, 1, w - 2, h - 1, fill);
		g.fill(1, 2, 2, h - 2, fill);
		g.fill(w - 2, 2, w - 1, h - 2, fill);
		g.fill(2, 0, w - 2, 1, rim);
		g.fill(2, h - 1, w - 2, h, rim);
		g.fill(0, 2, 1, h - 2, rim);
		g.fill(w - 1, 2, w, h - 2, rim);
		g.fill(1, 1, 2, 2, rim);
		g.fill(w - 2, 1, w - 1, 2, rim);
		g.fill(1, h - 2, 2, h - 1, rim);
		g.fill(w - 2, h - 2, w - 1, h - 1, rim);
	}

	private static int block(GuiGraphics g, Minecraft mc, String title, List<Net.MeterLine> lines, ToDoubleFunction<Net.MeterLine> of, int top, int low, int text, float seconds, int y, float a) {
		if (lines.isEmpty()) return y;
		var font = mc.font;
		y += GAP;
		int left = PAD, right = W - PAD, share = lines.size() > 1 ? SHARE_W : 0;
		double all = lines.stream().mapToDouble(of).sum(), most = of.applyAsDouble(lines.get(0));
		String total = rate(all / seconds) + "/s";
		// healing: how much of what was sent found nobody hurt (11/7: a healer on a full party only showed 1-3/s and looked broken)
		double over = title.equals("Healing") ? lines.stream().mapToDouble(Net.MeterLine::over).sum() : 0;
		if (over > 0.5) title += "  " + Math.round(100 * over / (over + all)) + "% over";
		g.drawString(font, title, left + 1, y + 1, tint(text, 255, a), false);
		g.drawString(font, total, right - font.width(total), y + 1, tint(AshUi.TEXT & 0xFFFFFF, 255, a), false);
		y += HEAD;
		String me = mc.player.getGameProfile().getName();
		int barX = left + FACE + FACE_GAP, barEnd = right - share;
		for (Net.MeterLine l : lines) {
			double v = of.applyAsDouble(l);
			boolean mine = l.name().equals(me);
			RenderSystem.enableBlend();
			g.setColor(1, 1, 1, a);
			PartyScreen.face(g, mc, l.name(), left, y + 1, FACE);
			g.setColor(1, 1, 1, 1);
			int reach = barX + Math.max(1, (int) Math.round((barEnd - barX) * v / most)), bar = mine ? 235 : 150;
			g.fill(barX, y, barEnd, y + ROW - 1, tint(0, 90, a));
			g.fillGradient(barX, y, reach, y + ROW - 1, tint(top, bar, a), tint(low, bar, a));
			if (mine) g.fill(barX, y, barX + 1, y + ROW - 1, tint(BONE, 200, a));
			// all of it this fight, then each second's share
			String value = HitNumbers.shortly((float) v) + " " + rate(v / seconds) + "/s";
			String name = font.plainSubstrByWidth(l.name(), barEnd - barX - font.width(value) - 8);
			g.drawString(font, name, barX + 3, y + 1, tint(BONE, 255, a), true);
			g.drawString(font, value, barEnd - font.width(value) - 2, y + 1, tint(BONE, 255, a), true);
			if (share > 0) {
				String part = Math.round(100 * v / all) + "%";
				g.drawString(font, part, right - font.width(part), y + 1, tint(AshUi.MUTED & 0xFFFFFF, 255, a), false);
			}
			y += ROW;
		}
		return y;
	}
}
