package com.snoringwalrus.ashbound.client;

import java.util.List;

import com.snoringwalrus.ashbound.Classes;
import com.snoringwalrus.ashbound.Net;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * The first thing a new player sees: nine classes on the left, the one you're looking at on the right with its kit
 * and bonus, and a button to take it. Esc lets you reach the pause menu; the server asks again if you close it.
 */
public class ClassScreen extends Screen {
	private static final int W = 420, H = 240, CARD_W = 68, CARD_H = 62, GAP = 4, PAD = 12, TOP = 30, BTN_H = 20, TILE = 20, PER_ROW = 7;
	private int picked;

	public ClassScreen() {
		super(Component.literal("Choose your class"));
	}

	private int left() {
		return (width - W) / 2;
	}

	private int top() {
		return (height - H) / 2;
	}

	private int cardX(int i) {
		return left() + PAD + (i % 3) * (CARD_W + GAP);
	}

	private int cardY(int i) {
		return top() + TOP + (i / 3) * (CARD_H + GAP);
	}

	/** The detail column's left edge and width. */
	private int infoX() {
		return left() + PAD + 3 * (CARD_W + GAP) + 6;
	}

	private int infoW() {
		return left() + W - PAD - infoX();
	}

	private int buttonY() {
		return top() + H - PAD - BTN_H;
	}

	private int tileX(int i) {
		return infoX() + (i % PER_ROW) * (TILE + 2);
	}

	private int tileY(int i) {
		return top() + 130 + (i / PER_ROW) * (TILE + 2);
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
		for (int i = 0; i < Classes.ALL.size(); i++)
			if (in(mx, my, cardX(i), cardY(i), CARD_W, CARD_H)) {
				picked = i;
				return true;
			}
		if (in(mx, my, infoX(), buttonY(), infoW(), BTN_H)) {
			PacketDistributor.sendToServer(new Net.ClassPick(Classes.ALL.get(picked).id()));
			onClose();
			return true;
		}
		return super.mouseClicked(mx, my, button);
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		g.fill(0, 0, width, height, 0xA0000000);
		int x = left(), y = top();
		AshUi.panel(g, x, y, W, H);
		AshUi.header(g, x, y, W, 24, "CHOOSE YOUR CLASS");
		for (int i = 0; i < Classes.ALL.size(); i++) card(g, i, mx, my);
		info(g, mx, my);
	}

	private void card(GuiGraphics g, int i, int mx, int my) {
		Classes.Cls c = Classes.ALL.get(i);
		int x = cardX(i), y = cardY(i);
		AshUi.row(g, x, y, CARD_W, CARD_H, i == picked, in(mx, my, x, y, CARD_W, CARD_H));
		g.pose().pushPose();
		g.pose().translate(x + (CARD_W - 32) / 2f, y + 6, 0);
		g.pose().scale(2f, 2f, 1f);
		g.renderItem(Classes.icon(c), 0, 0);
		g.pose().popPose();
		g.drawString(font, c.name(), x + (CARD_W - font.width(c.name())) / 2, y + 41, i == picked ? AshUi.TEXT : AshUi.BODY, true);
		g.drawString(font, c.role(), x + (CARD_W - font.width(c.role())) / 2, y + 51, AshUi.MUTED, false);
	}

	private void info(GuiGraphics g, int mx, int my) {
		Classes.Cls c = Classes.ALL.get(picked);
		int x = infoX(), w = infoW(), y = top() + TOP;
		g.pose().pushPose();
		g.pose().translate(x, y, 0);
		g.pose().scale(1.5f, 1.5f, 1f);
		g.drawString(font, Component.literal(c.name()).withStyle(ChatFormatting.BOLD), 0, 0, AshUi.TEXT, true);
		g.pose().popPose();
		g.drawString(font, c.role(), x, y + 15, AshUi.MUTED, false);
		int ty = y + 29;
		for (FormattedCharSequence l : font.split(Component.literal(c.blurb()), w)) {
			g.drawString(font, l, x, ty, AshUi.BODY, false);
			ty += 10;
		}
		g.drawString(font, "LASTING BONUS", x, top() + 96, AshUi.LABEL, false);
		g.drawString(font, c.perk(), x, top() + 106, AshUi.EMBER_LT, false);
		g.drawString(font, "STARTS WITH", x, top() + 119, AshUi.LABEL, false);
		List<ItemStack> kit = Classes.kit(c);
		for (int i = 0; i < kit.size(); i++) {
			AshUi.tile(g, tileX(i), tileY(i), TILE, 0);
			g.renderItem(kit.get(i), tileX(i) + 2, tileY(i) + 2);
			g.renderItemDecorations(font, kit.get(i), tileX(i) + 2, tileY(i) + 2);
		}
		int coinY = tileY(kit.size() - 1) + TILE + 5;
		AshUi.coin(g, x, coinY);
		g.drawString(font, Classes.START_COINS + " coins", x + 12, coinY + 1, AshUi.BODY, false);
		int by = buttonY();
		boolean hover = in(mx, my, x, by, w, BTN_H);
		AshUi.row(g, x, by, w, BTN_H, hover, false);
		String take = "Choose " + c.name();
		g.drawString(font, take, x + (w - font.width(take)) / 2, by + 6, AshUi.TEXT, true);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		List<ItemStack> kit = Classes.kit(Classes.ALL.get(picked));
		for (int i = 0; i < kit.size(); i++)
			if (in(mx, my, tileX(i), tileY(i), TILE, TILE)) g.renderTooltip(font, kit.get(i), mx, my);
	}
}
