package com.snoringwalrus.ashbound.client;

import com.snoringwalrus.ashbound.Classes;
import com.snoringwalrus.ashbound.Coins;
import com.snoringwalrus.ashbound.Errands;
import com.snoringwalrus.ashbound.Guild;
import com.snoringwalrus.ashbound.Levels;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.PlayerFaceRenderer;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.world.item.ItemStack;

/**
 * Your guild card, held up (use the card): the front with your face, name, rank seal, the points to the
 * next evaluation and what you carry (coins, Ash); the back with the ladder F to SSS, your rank lit, the
 * oath on parchment and the receptionist's hand; slipped behind it, the favours you've taken on for townsfolk.
 * Side by side when there's room (click to swap the back for the favours), else click to turn through them.
 */
public class GuildCardScreen extends Screen {
	private static final int W = 300, H = 188;
	private static final String OATH = "I go where the gates open. I bring back what I swore to, or I do not come back. What the dark takes, the Guild will not ransom.";
	/** Which side's showing: the front (only when there's no room for two), the back, the favours. */
	private int side = 1;

	public GuildCardScreen() {
		super(Component.literal("Guild Card"));
	}

	private boolean both() {
		return width >= W * 2 + 30 && height >= H + 20;
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		side = both() ? 3 - side : (side + 1) % 3;
		return true;
	}

	/** All of it: the screen's own buttons, if ever, go over it. */
	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		g.fill(0, 0, width, height, 0x90000000);
		int y = (height - H) / 2;
		if (both()) {
			int x = (width - W * 2 - 16) / 2;
			front(g, x, y);
			if (side == 2) favours(g, x + W + 16, y);
			else back(g, x + W + 16, y);
			String s = "click for your " + (side == 2 ? "card's back" : "favours");
			g.drawString(font, s, x + W + 16 + (W - font.width(s)) / 2, y + H + 6, AshUi.DIM, false);
		} else {
			int x = (width - W) / 2;
			if (side == 1) back(g, x, y);
			else if (side == 2) favours(g, x, y);
			else front(g, x, y);
			String s = "click to turn it over";
			g.drawString(font, s, (width - font.width(s)) / 2, y + H + 6, AshUi.DIM, false);
		}
	}

	private void front(GuiGraphics g, int x, int y) {
		var p = minecraft.player;
		Guild.Card c = Guild.of(p);
		AshUi.panel(g, x, y, W, H);
		AshUi.header(g, x, y, W, 24, null);
		g.renderItem(new ItemStack(Guild.CARD_ITEM.get()), x + 9, y + 6);
		g.drawString(font, Component.literal("ADVENTURERS' GUILD").withStyle(ChatFormatting.BOLD), x + 29, y + 7, AshUi.TEXT, true);
		g.drawString(font, "HIGHMOURN CHAPTER", x + 29, y + 16, 0xFF7D756A, false);
		String no = "No. " + String.format("%04d", Math.abs(p.getUUID().hashCode()) % 10000);
		g.drawString(font, no, x + W - 12 - font.width(no), y + 11, 0xFF8A8076, false);

		// the face, the name, the seal
		int py = y + 34;
		AshUi.tile(g, x + 12, py, 44, 0);
		PlayerFaceRenderer.draw(g, p.getSkin(), x + 16, py + 4, 36);
		g.drawString(font, "BEARER", x + 64, py + 2, AshUi.LABEL, false);
		g.pose().pushPose();
		g.pose().translate(x + 64, py + 13, 0);
		g.pose().scale(1.5f, 1.5f, 1f);
		g.drawString(font, Component.literal(p.getName().getString()).withStyle(ChatFormatting.BOLD), 0, 0, AshUi.TEXT, true);
		g.pose().popPose();
		Classes.Cls cls = Classes.byId(Classes.client);
		String sub = c.registered() ? c.rankName() + "-rank " + (cls == null ? "adventurer" : cls.name()) + "  ·  level " + Levels.clientLevel : "Not registered. See the receptionist.";
		g.drawString(font, sub, x + 64, py + 30, c.registered() ? AshUi.MUTED : AshUi.BAD, false);
		AshUi.seal(g, x + W - 58, py - 2, 46, c.rank());

		// to the next evaluation
		int by = y + 98;
		int next = c.next(), prev = Guild.NEED[c.rank()];
		float k = next < 0 ? 1 : Math.min(1f, (c.points() - prev) / (float) Math.max(1, next - prev));
		String to = c.canRankUp() ? "EVALUATION READY" : next < 0 ? "THE LAST RANK" : "TO " + Guild.RANKS[Math.min(Guild.RANKS.length - 1, c.rank() + 1)] + "-RANK";
		String gp = next < 0 ? c.points() + " GP" : c.points() + " / " + next + " GP";
		g.drawString(font, to, x + 12, by, c.canRankUp() ? 0xFF8AD070 : AshUi.LABEL, false);
		g.drawString(font, gp, x + W - 12 - font.width(gp), by, AshUi.EMBER_LT, false);
		AshUi.bar(g, x + 12, by + 12, W - 24, 5, k);
		AshUi.divider(g, x + 12, by + 26, W - 24);

		// what's on the card
		int sy = by + 36, cw = (W - 24) / 4;
		stat(g, x + 12, sy, String.valueOf(c.done().size()), "REQUESTS", 0, AshUi.TEXT);
		stat(g, x + 12 + cw, sy, c.active().size() + "/" + Guild.MAX_ACTIVE, "TAKEN", 0, AshUi.TEXT);
		stat(g, x + 12 + cw * 2, sy, String.format("%,d", Coins.of(p)), "COINS", 1, AshUi.TEXT);
		stat(g, x + 12 + cw * 3, sy, String.format("%,d", Levels.clientAsh), "ASH", 2, 0xFFF39150);
	}

	/** A number over its label; icon 1 = a coin, 2 = Ash's flame. */
	private void stat(GuiGraphics g, int x, int y, String value, String label, int icon, int colour) {
		int vx = x;
		if (icon == 1) {
			AshUi.coin(g, x, y);
			vx += 12;
		} else if (icon == 2) {
			AshUi.flame(g, x, y - 1);
			vx += 10;
		}
		g.drawString(font, Component.literal(value).withStyle(ChatFormatting.BOLD), vx, y + 1, colour, true);
		g.drawString(font, label, x, y + 13, AshUi.LABEL, false);
	}

	private void favours(GuiGraphics g, int x, int y) {
		AshUi.panel(g, x, y, W, H);
		AshUi.header(g, x, y, W, 24, "FAVOURS");
		String n = Errands.client.size() + "/" + Errands.MAX;
		g.drawString(font, n, x + W - 12 - font.width(n), y + 8, AshUi.LABEL, false);
		if (Errands.client.isEmpty()) {
			var lines = font.split(Component.literal("Nobody's asked you for anything. Stop and talk to people: some of them have troubles of their own.").withStyle(ChatFormatting.ITALIC), W - 40);
			int ly = y + 74;
			for (FormattedCharSequence line : lines) {
				g.drawString(font, line, x + (W - font.width(line)) / 2, ly, AshUi.MUTED, false);
				ly += 11;
			}
			return;
		}
		int fy = y + 36;
		for (Errands.View v : Errands.client) {
			g.drawString(font, Component.literal(v.title()).withStyle(ChatFormatting.BOLD), x + 14, fy, v.ready() ? 0xFF8AD070 : AshUi.TEXT, true);
			g.drawString(font, v.objective(), x + 14, fy + 12, AshUi.EMBER_LT, false);
			g.drawString(font, v.where(), x + 14, fy + 23, AshUi.LABEL, false);
			fy += 48;
		}
	}

	private void back(GuiGraphics g, int x, int y) {
		Guild.Card c = Guild.of(minecraft.player);
		AshUi.panel(g, x, y, W, H);
		AshUi.header(g, x, y, W, 24, "THE LADDER");
		// the ranks, F to SSS, yours lit
		int n = Guild.RANKS.length, bw = 26, gap = (W - 24 - n * bw) / (n - 1);
		for (int i = 0; i < n; i++) {
			int bx = x + 12 + i * (bw + gap), by = y + 34;
			boolean mine = i == c.rank() && c.registered(), past = i < c.rank();
			if (mine) {
				g.blitSprite(AshUi.EMBER, bx, by, bw, bw);
				g.renderOutline(bx, by, bw, bw, AshUi.BLACK);
				g.renderOutline(bx + 1, by + 1, bw - 2, bw - 2, AshUi.EMBER_LT);
			} else {
				g.fill(bx, by, bx + bw, by + bw, 0xFF0C0B0A);
				g.renderOutline(bx, by, bw, bw, AshUi.BLACK);
				g.renderOutline(bx + 1, by + 1, bw - 2, bw - 2, past ? 0xFF8A8076 : AshUi.LINE);
			}
			Component r = Component.literal(Guild.RANKS[i]).withStyle(ChatFormatting.BOLD);
			g.drawString(font, r, bx + (bw - font.width(r)) / 2, by + 9, mine ? 0xFFFFF3E2 : past ? 0xFFCFC6B8 : 0xFF5C544C, true);
		}
		// the oath, on parchment
		int oy = y + 70, ow = W - 24;
		var lines = font.split(Component.literal(OATH).withStyle(ChatFormatting.ITALIC), ow - 16);
		int oh = lines.size() * 10 + 10;
		g.blitSprite(AshUi.PARCHMENT, x + 12, oy, ow, oh);
		g.renderOutline(x + 12, oy, ow, oh, 0xC03A2A16);
		int ly = oy + 6;
		for (FormattedCharSequence line : lines) {
			g.drawString(font, line, x + 12 + (ow - font.width(line)) / 2, ly, 0xFF3A2814, false);
			ly += 10;
		}
		// the receptionist's hand, the small print, the Guild's seal in red wax
		int sy = y + H - 34;
		g.pose().pushPose();
		g.pose().translate(x + 14, sy, 0);
		g.pose().scale(1.5f, 1.5f, 1f);
		g.drawString(font, Component.literal("Elowen").withStyle(ChatFormatting.ITALIC), 0, 0, AshUi.TEXT, true);
		g.pose().popPose();
		g.fill(x + 14, sy + 14, x + 100, sy + 15, 0xFF8A5430);
		g.drawString(font, "RECEPTIONIST", x + 14, sy + 18, AshUi.LABEL, false);
		g.pose().pushPose();
		g.pose().translate(x + W / 2f + 18, sy + 6, 0);
		g.pose().scale(0.75f, 0.75f, 1f);
		String[] small = {"If found, return to any Guild hall.", "Replacement: 500 coins."};
		for (int i = 0; i < small.length; i++) g.drawString(font, small[i], -font.width(small[i]) / 2, i * 11, 0xFF7D756A, false);
		g.pose().popPose();
		AshUi.tinted(g, AshUi.SEAL, x + W - 46, sy - 6, 34, 34, 0xFF8A1A14);
	}
}
