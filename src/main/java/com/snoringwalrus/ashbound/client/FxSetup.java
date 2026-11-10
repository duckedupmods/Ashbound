package com.snoringwalrus.ashbound.client;

import java.util.function.IntConsumer;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/**
 * How the skills look to you, from the Skills screen: how see-through their effects are, how much they glow, how hard the camera
 * shakes on a big blow, and whether the screen flashes and throws speed lines. Each player's own (HudPrefs); nobody else's changes.
 */
class FxSetup extends Screen {
	private static final int W = 290, H = 202, PAD = 10, TOP = 28, ROW = 20, LABEL_W = 86, BTN_H = 16, BTN_GAP = 4;
	private static final String[] SEE = {"25%", "50%", "75%", "Full"}, GLOW = {"Off", "Soft", "Full"}, SHAKE = {"Off", "Low", "Full"}, ONOFF = {"Off", "On"};
	private static final String[] ALLY = {"Off", "25%", "50%", "Full"};
	private static final String[] ROWS = {"Opacity", "Glow", "Camera shake", "Screen flash", "Speed lines", "Allies' effects", "Glowing allies"};

	private final Screen back;

	FxSetup(Screen back) {
		super(Component.literal("Skill effects"));
		this.back = back;
	}

	private int left() {
		return (width - W) / 2;
	}

	private int top() {
		return (height - H) / 2;
	}

	@Override
	protected void init() {
		choice(0, SEE, HudPrefs.fxSee, i -> HudPrefs.fxSee = i);
		choice(1, GLOW, HudPrefs.fxShine, i -> HudPrefs.fxShine = i);
		choice(2, SHAKE, HudPrefs.fxKick, i -> HudPrefs.fxKick = i);
		choice(3, ONOFF, HudPrefs.fxFlash ? 1 : 0, i -> HudPrefs.fxFlash = i == 1);
		choice(4, ONOFF, HudPrefs.fxLines ? 1 : 0, i -> HudPrefs.fxLines = i == 1);
		choice(5, ALLY, HudPrefs.fxAllies, i -> HudPrefs.fxAllies = i);
		choice(6, ONOFF, HudPrefs.allyGlow ? 1 : 0, i -> HudPrefs.allyGlow = i == 1);
		int half = (W - 2 * PAD - BTN_GAP) / 2, y = top() + H - PAD - BTN_H;
		addRenderableWidget(new AshUi.AshButton(left() + PAD, y, half, BTN_H, Component.literal("Defaults"), b -> {
			HudPrefs.fxSee = HudPrefs.FX_ALPHA.length - 1;
			HudPrefs.fxShine = HudPrefs.FX_GLOW.length - 1;
			HudPrefs.fxKick = HudPrefs.FX_SHAKE.length - 1;
			HudPrefs.fxFlash = HudPrefs.fxLines = true;
			HudPrefs.fxAllies = HudPrefs.FX_ALLY.length - 1;
			HudPrefs.allyGlow = false;
			HudPrefs.save();
			rebuildWidgets();
		}, false));
		addRenderableWidget(new AshUi.AshButton(left() + PAD + half + BTN_GAP, y, half, BTN_H, Component.literal("Done"), b -> onClose(), true));
	}

	/** A row of choices: the one in force glows. */
	private void choice(int row, String[] names, int now, IntConsumer pick) {
		int x = left() + PAD + LABEL_W, y = top() + TOP + row * ROW, w = (W - 2 * PAD - LABEL_W - (names.length - 1) * BTN_GAP) / names.length;
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
		g.fill(0, 0, width, height, 0x80000000);
		AshUi.panel(g, left(), top(), W, H);
		AshUi.header(g, left(), top(), W, 20, "SKILL EFFECTS");
		for (int i = 0; i < ROWS.length; i++) g.drawString(font, ROWS[i], left() + PAD, top() + TOP + i * ROW + 4, AshUi.LABEL, false);
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
