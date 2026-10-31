package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.List;

import com.snoringwalrus.ashbound.Coins;
import com.snoringwalrus.ashbound.Mount;
import com.snoringwalrus.ashbound.Mounts;
import com.snoringwalrus.ashbound.Net;

import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.neoforged.neoforge.network.PacketDistributor;

/** Training your mount (Mounts.TRACKS): it turns on the left, what it can learn on the right, each with what it's got and what's next. */
public class MountUpScreen extends Screen implements MenuTabs.Panel {
	private static final int W = 430, H = 228, PAD = 12, TOP = 30, SIDE_W = 142, ROW_H = 41, GAP = 3, BTN_W = 66, BTN_H = 18;
	private final long opened = System.nanoTime();
	private final List<AshUi.AshButton> buy = new ArrayList<>();
	private Mount shown;

	public MountUpScreen() {
		super(Component.literal("Your mount"));
		MountRender.preload();
	}

	private int left() {
		return (width - W) / 2;
	}

	private int top() {
		return (height - H) / 2;
	}

	@Override
	public int panelTop() {
		return top();
	}

	private int rowX() {
		return left() + PAD + SIDE_W + 8;
	}

	private int rowW() {
		return left() + W - PAD - rowX();
	}

	private int rowY(int i) {
		return top() + TOP + i * (ROW_H + GAP);
	}

	@Override
	protected void init() {
		buy.clear();
		for (int i = 0; i < Mounts.TRACKS.size(); i++) {
			int t = i;
			buy.add(addRenderableWidget(new AshUi.AshButton(rowX() + rowW() - BTN_W - 5, rowY(i) + (ROW_H - BTN_H) / 2, BTN_W, BTN_H, Component.empty(),
					b -> PacketDistributor.sendToServer(new Net.MountUp(t)), true)));
		}
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		g.fill(0, 0, width, height, 0x90000000);
		int x = left(), y = top();
		Mounts.Kind k = Mounts.byId(Mounts.client);
		AshUi.panel(g, x, y, W, H);
		AshUi.header(g, x, y, W, 24, "TRAIN YOUR MOUNT");
		if (k == null) return;
		if (shown == null || shown.kind != k) shown = Mounts.type(k).create(minecraft.level);
		if (shown != null && MountRender.ready(k.id())) MountScreen.preview(g, shown, opened, x + PAD, y + TOP, SIDE_W, 128);
		int ty = y + TOP + 132;
		g.drawString(font, Component.literal(k.name()).withStyle(ChatFormatting.BOLD), x + PAD + 4, ty, AshUi.TEXT, true);
		g.drawString(font, k.title(), x + PAD + 4, ty + 11, AshUi.MUTED, false);
		AshUi.divider(g, x + PAD + 4, ty + 24, SIDE_W - 8);
		AshUi.coin(g, x + PAD + 4, ty + 31);
		g.drawString(font, String.format("%,d", Coins.client), x + PAD + 17, ty + 32, AshUi.TEXT, true);
		for (int i = 0; i < Mounts.TRACKS.size(); i++) track(g, i, mx, my);
	}

	private void track(GuiGraphics g, int i, int mx, int my) {
		Mounts.Track t = Mounts.TRACKS.get(i);
		int x = rowX(), y = rowY(i), w = rowW(), rank = Mounts.clientRanks[i], max = t.costs().length;
		boolean top = rank >= max;
		AshUi.row(g, x, y, w, ROW_H, false, false);
		g.drawString(font, Component.literal(t.name()).withStyle(ChatFormatting.BOLD), x + 7, y + 6, rank > 0 ? AshUi.EMBER_LT : AshUi.TEXT, true);
		int px = x + 7 + font.width(Component.literal(t.name()).withStyle(ChatFormatting.BOLD)) + 7;
		for (int n = 0; n < max; n++) {
			g.fill(px + n * 7, y + 7, px + n * 7 + 5, y + 12, AshUi.BLACK);
			g.fill(px + n * 7 + 1, y + 8, px + n * 7 + 4, y + 11, n < rank ? AshUi.EMBER_C : 0xFF3D3833);
		}
		int tw = w - BTN_W - 18;
		String now = rank > 0 ? "Now: " + t.ranks()[rank - 1] : t.about();
		g.drawString(font, font.plainSubstrByWidth(now, tw), x + 7, y + 18, rank > 0 ? AshUi.BODY : AshUi.MUTED, false);
		if (!top) g.drawString(font, font.plainSubstrByWidth("Next: " + t.ranks()[rank], tw), x + 7, y + 29, AshUi.MUTED, false);
		AshUi.AshButton b = buy.get(i);
		b.setMessage(Component.literal(top ? "MASTERED" : String.format("%,d", t.costs()[rank])));
		b.active = !top && Coins.client >= t.costs()[rank];
	}
}
