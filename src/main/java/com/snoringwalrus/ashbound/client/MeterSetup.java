package com.snoringwalrus.ashbound.client;

import java.util.List;
import java.util.function.IntConsumer;

import com.snoringwalrus.ashbound.Net;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;

/**
 * Setting up the party meter: the meter itself is on the screen over the game and you drag it where you want it, with what it shows
 * picked on a small card. Before your first fight it shows made-up numbers so there's something to place.
 */
class MeterSetup extends Screen {
	private static final int W = 240, H = 126, PAD = 10, TOP = 26, ROW = 20, LABEL_W = 44, BTN_H = 16, BTN_GAP = 4, HINT_Y = 61, HOVER_ALPHA = 128;
	private static final float SNAP = 0.02f, CENTRE = 0.5f, FAINT = 0.5f;
	private static final String[] SHOW = {"Off", "In fights", "Always"}, VIEW = {"Both", "Damage", "Healing"}, SIZE = {"Small", "Normal", "Large"};

	private final Screen back;
	private boolean dragging;
	private int grabX, grabY;

	MeterSetup(Screen back) {
		super(Component.literal("Party meter"));
		this.back = back;
	}

	private int left() {
		return (width - W) / 2;
	}

	private int top() {
		return (height - H) / 2;
	}

	/** The real fight if there's been one, otherwise a stand-in with your name on it. */
	private Net.Meter meter() {
		if (Net.clientMeter != null) return Net.clientMeter;
		String me = minecraft.player.getGameProfile().getName();
		return new Net.Meter(List.of(new Net.MeterLine(me, 1260, 90, 0), new Net.MeterLine("Second", 840, 0, 0), new Net.MeterLine("Third", 310, 620, 180)), 10);
	}

	@Override
	protected void init() {
		choice(0, SHOW, HudPrefs.meterShow, i -> HudPrefs.meterShow = i);
		choice(1, VIEW, HudPrefs.meterView, i -> HudPrefs.meterView = i);
		choice(2, SIZE, HudPrefs.meterSize, i -> HudPrefs.meterSize = i);
		int half = (W - 2 * PAD - BTN_GAP) / 2, y = top() + H - PAD - BTN_H;
		addRenderableWidget(new AshUi.AshButton(left() + PAD, y, half, BTN_H, Component.literal("Reset place"), b -> {
			HudPrefs.meterX = HudPrefs.START_X;
			HudPrefs.meterY = HudPrefs.START_Y;
			HudPrefs.save();
		}, false));
		addRenderableWidget(new AshUi.AshButton(left() + PAD + half + BTN_GAP, y, half, BTN_H, Component.literal("Done"), b -> onClose(), true));
	}

	/** A row of three: the one in force glows. */
	private void choice(int row, String[] names, int now, IntConsumer pick) {
		int x = left() + PAD + LABEL_W, y = top() + TOP + row * ROW, w = (W - 2 * PAD - LABEL_W - 2 * BTN_GAP) / 3;
		for (int i = 0; i < names.length; i++) {
			int which = i;
			addRenderableWidget(new AshUi.AshButton(x + i * (w + BTN_GAP), y, w, BTN_H, Component.literal(names[i]), b -> {
				pick.accept(which);
				HudPrefs.save();
				rebuildWidgets();
			}, i == now));
		}
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		AshUi.panel(g, left(), top(), W, H);
		AshUi.header(g, left(), top(), W, 20, "PARTY METER");
		String[] rows = {"Show", "View", "Size"};
		for (int i = 0; i < rows.length; i++) g.drawString(font, rows[i], left() + PAD, top() + TOP + i * ROW + 4, AshUi.LABEL, false);
		g.drawCenteredString(font, "Drag the meter to move it", left() + W / 2, top() + TOP + HINT_Y, AshUi.MUTED);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		Net.Meter m = meter();
		int[] b = MeterHud.box(m, width, height);
		boolean on = HudPrefs.meterShow != HudPrefs.OFF;
		g.pose().pushPose();
		g.pose().translate(0, 0, 200);
		MeterHud.paint(g, minecraft, m, Net.clientMeter == null ? "Example" : "Your last fight", false, on ? 1 : FAINT);
		if (dragging || inside(b, mx, my)) g.renderOutline(b[0] - 1, b[1] - 1, b[2] + 2, b[3] + 2, dragging ? AshUi.EMBER_LT : HOVER_ALPHA << 24 | AshUi.EMBER_C & 0xFFFFFF);
		g.pose().popPose();
	}

	private static boolean inside(int[] b, double mx, double my) {
		return mx >= b[0] && mx < b[0] + b[2] && my >= b[1] && my < b[1] + b[3];
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		int[] b = MeterHud.box(meter(), width, height);
		if (button == 0 && inside(b, mx, my)) {
			dragging = true;
			grabX = (int) mx - b[0];
			grabY = (int) my - b[1];
			return true;
		}
		return super.mouseClicked(mx, my, button);
	}

	@Override
	public boolean mouseDragged(double mx, double my, int button, double dx, double dy) {
		if (!dragging) return super.mouseDragged(mx, my, button, dx, dy);
		int[] b = MeterHud.box(meter(), width, height);
		HudPrefs.meterX = snap(MeterHud.share((int) mx - grabX, width, b[2]));
		HudPrefs.meterY = snap(MeterHud.share((int) my - grabY, height, b[3]));
		return true;
	}

	/** Keeps it off the screen's edge, and pulls it onto the edges and the middle when it's close. */
	private static float snap(float at) {
		float k = Mth.clamp(at, 0, 1);
		return k < SNAP ? 0 : k > 1 - SNAP ? 1 : Math.abs(k - CENTRE) < SNAP ? CENTRE : k;
	}

	@Override
	public boolean mouseReleased(double mx, double my, int button) {
		if (dragging) {
			dragging = false;
			HudPrefs.save();
			return true;
		}
		return super.mouseReleased(mx, my, button);
	}

	@Override
	public void onClose() {
		minecraft.setScreen(back);
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}
}
