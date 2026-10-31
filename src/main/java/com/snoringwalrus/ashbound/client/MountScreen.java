package com.snoringwalrus.ashbound.client;

import java.util.HashMap;
import java.util.Map;

import com.snoringwalrus.ashbound.Mount;
import com.snoringwalrus.ashbound.Mounts;
import com.snoringwalrus.ashbound.Net;
import com.mojang.blaze3d.platform.Lighting;
import com.mojang.math.Axis;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.neoforged.neoforge.network.PacketDistributor;

/** Comes right after the class: five mounts on the left, the one you're looking at turning on the right. Esc works as on ClassScreen. */
public class MountScreen extends Screen {
	private static final int W = 420, H = 240, PAD = 12, TOP = 30, CARD_W = 118, CARD_H = 36, GAP = 3, BTN_H = 20;
	private static final double FASTEST = 0.30, HIGHEST = 1.08;
	private final Map<String, Mount> shown = new HashMap<>();
	/** how much of the frame it may fill, its turn and tilt; its walk runs at this share of a walking pace */
	private static final float FILL = 0.9f, SPIN = 0.018f, TILT = 12, SHOW_GAIT = 0.12f, SHOW_STRIDE = 0.035f;
	private final long opened = System.nanoTime();
	private int picked;

	public MountScreen() {
		super(Component.literal("Choose your mount"));
		MountRender.preload();
	}

	private int left() {
		return (width - W) / 2;
	}

	private int top() {
		return (height - H) / 2;
	}

	private int cardY(int i) {
		return top() + TOP + i * (CARD_H + GAP);
	}

	private int infoX() {
		return left() + PAD + CARD_W + 8;
	}

	private int infoW() {
		return left() + W - PAD - infoX();
	}

	private int buttonY() {
		return top() + H - PAD - BTN_H;
	}

	private static boolean in(double mx, double my, int x, int y, int w, int h) {
		return mx >= x && mx < x + w && my >= y && my < y + h;
	}

	private Mount mount(Mounts.Kind k) {
		return shown.computeIfAbsent(k.id(), id -> Mounts.type(k).create(Minecraft.getInstance().level));
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		for (int i = 0; i < Mounts.ALL.size(); i++)
			if (in(mx, my, left() + PAD, cardY(i), CARD_W, CARD_H)) {
				picked = i;
				return true;
			}
		if (in(mx, my, infoX(), buttonY(), infoW(), BTN_H)) {
			PacketDistributor.sendToServer(new Net.MountPick(Mounts.ALL.get(picked).id()));
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
		AshUi.header(g, x, y, W, 24, "CHOOSE YOUR MOUNT");
		for (int i = 0; i < Mounts.ALL.size(); i++) {
			Mounts.Kind k = Mounts.ALL.get(i);
			int cy = cardY(i);
			AshUi.row(g, x + PAD, cy, CARD_W, CARD_H, i == picked, in(mx, my, x + PAD, cy, CARD_W, CARD_H));
			g.drawString(font, k.name(), x + PAD + 7, cy + 7, i == picked ? AshUi.TEXT : AshUi.BODY, true);
			g.drawString(font, k.title(), x + PAD + 7, cy + 20, AshUi.MUTED, false);
		}
		info(g, mx, my, pt);
	}

	private void stat(GuiGraphics g, int x, int y, int w, String name, float k) {
		g.drawString(font, name, x, y, AshUi.LABEL, false);
		AshUi.bar(g, x + 40, y + 1, w - 40, 6, k);
	}

	/** Drawn on a real clock, not the game's ticks: at 20 steps a second it would stutter however fast the screen runs. */
	private void preview(GuiGraphics g, Mount m, int x, int y, int w, int h) {
		float ticks = (System.nanoTime() - opened) / 5.0E7f;
		m.tickCount = (int) ticks;
		m.gait = m.gaitO = SHOW_GAIT;
		m.stride = m.strideO = ticks * SHOW_STRIDE;
		float[] box = MountRender.box(m);
		float size = FILL * Math.min(w / (box[3] * 2), h / (box[4] * 2));
		var ps = g.pose();
		g.enableScissor(x, y, x + w, y + h);
		ps.pushPose();
		ps.translate(x + w / 2f, y + h / 2f, 150);
		ps.scale(size, size, -size);
		ps.mulPose(Axis.ZP.rotationDegrees(180));
		ps.mulPose(Axis.XP.rotationDegrees(-TILT));
		ps.mulPose(Axis.YP.rotation(ticks * SPIN));
		Lighting.setupForEntityInInventory();
		MountRender.show(m, 0, ps, g.bufferSource());
		g.flush();
		Lighting.setupFor3DItems();
		ps.popPose();
		g.disableScissor();
	}

	private void info(GuiGraphics g, int mx, int my, float pt) {
		Mounts.Kind k = Mounts.ALL.get(picked);
		int x = infoX(), w = infoW(), y = top() + TOP;
		int ph = 104;
		if (MountRender.ready(k.id())) preview(g, mount(k), x, y, w, ph);
		int ty = y + ph + 2;
		g.pose().pushPose();
		g.pose().translate(x, ty, 0);
		g.pose().scale(1.3f, 1.3f, 1f);
		g.drawString(font, Component.literal(k.name()).withStyle(ChatFormatting.BOLD), 0, 0, AshUi.TEXT, true);
		g.pose().popPose();
		ty += 13;
		for (FormattedCharSequence l : font.split(Component.literal(k.blurb()), w)) {
			g.drawString(font, l, x, ty, AshUi.BODY, false);
			ty += 10;
		}
		g.drawString(font, k.special(), x, ty + 1, AshUi.EMBER_LT, false);
		ty += 13;
		int half = (w - 8) / 2;
		stat(g, x, ty, half, "Speed", (float) (k.speed() / FASTEST));
		stat(g, x + half + 8, ty, half, "Jump", (float) (k.jump() / HIGHEST));
		int by = buttonY();
		AshUi.row(g, x, by, w, BTN_H, in(mx, my, x, by, w, BTN_H), false);
		String take = "Ride " + k.name();
		g.drawString(font, take, x + (w - font.width(take)) / 2, by + 6, AshUi.TEXT, true);
	}
}
