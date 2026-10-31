package com.snoringwalrus.ashbound.client;

import com.snoringwalrus.ashbound.Forms;
import com.snoringwalrus.ashbound.Net;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.neoforged.neoforge.network.PacketDistributor;

/** The warning before an Awakening Tome: what it gives, what it takes, and that it can't be put back. */
public class TomeScreen extends Screen {
	private static final int W = 300, H = 186, PAD = 14, BTN_W = 120, BTN_H = 20, RED = 0xFFE05A40;
	private final Forms.Form form;

	public TomeScreen(Forms.Form form) {
		super(Component.literal(form.tome()));
		this.form = form;
	}

	private int left() {
		return (width - W) / 2;
	}

	private int top() {
		return (height - H) / 2;
	}

	private int buttonY() {
		return top() + H - PAD - BTN_H;
	}

	private static boolean in(double mx, double my, int x, int y, int w, int h) {
		return mx >= x && mx < x + w && my >= y && my < y + h;
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		if (in(mx, my, left() + PAD, buttonY(), BTN_W, BTN_H)) {
			PacketDistributor.sendToServer(new Net.TomeRead(form.id()));
			onClose();
			return true;
		}
		if (in(mx, my, left() + W - PAD - BTN_W, buttonY(), BTN_W, BTN_H)) {
			onClose();
			return true;
		}
		return super.mouseClicked(mx, my, button);
	}

	private int block(GuiGraphics g, String label, String text, int y, int colour) {
		int x = left() + PAD, w = W - PAD * 2;
		g.drawString(font, label, x, y, AshUi.LABEL, false);
		y += 11;
		for (FormattedCharSequence l : font.split(Component.literal(text), w)) {
			g.drawString(font, l, x, y, colour, false);
			y += 10;
		}
		return y + 5;
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		g.fill(0, 0, width, height, 0xB0000000);
		AshUi.panel(g, left(), top(), W, H);
		AshUi.header(g, left(), top(), W, 24, form.tome().toUpperCase());
		int y = top() + 32;
		y = block(g, "When", form.trigger(), y, AshUi.BODY);
		y = block(g, "It gives you", form.gift(), y, AshUi.EMBER_LT);
		y = block(g, "It takes from you", form.price(), y, RED);
		block(g, "And for good", "Your last skill key is gone once you've read this", y, RED);
		int by = buttonY(), read = left() + PAD, leave = left() + W - PAD - BTN_W;
		AshUi.row(g, read, by, BTN_W, BTN_H, false, in(mx, my, read, by, BTN_W, BTN_H));
		AshUi.row(g, leave, by, BTN_W, BTN_H, false, in(mx, my, leave, by, BTN_W, BTN_H));
		String a = "Read it", b = "Close the book";
		g.drawString(font, a, read + (BTN_W - font.width(a)) / 2, by + 6, RED, true);
		g.drawString(font, b, leave + (BTN_W - font.width(b)) / 2, by + 6, AshUi.TEXT, true);
	}
}
