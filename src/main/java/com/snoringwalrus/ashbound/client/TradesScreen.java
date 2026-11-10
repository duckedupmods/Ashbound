package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.List;

import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Trades;

import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Your eight trades down the left with their levels; the picked one on the right: what it is, where it's done, your points, its
 * perks in three branches (top to bottom, each after the one above); along the bottom what you've eaten or drunk that's still working.
 */
public class TradesScreen extends Screen implements MenuTabs.Panel {
	private static final int W = 424, H = 254, PAD = 10, TOP = 30, ROW_H = 24, LIST_W = 128, SIDE_X = PAD + LIST_W + 10, SIDE_W = W - SIDE_X - PAD,
			COL_GAP = 6, COL_W = (SIDE_W - 2 * COL_GAP) / 3, PERK_H = 26, PERK_GAP = 5, PERKS_Y = 92, FOOT = 22, BTN_W = 116, BTN_H = 16;
	private static String picked = "cooking";
	private AshUi.AshButton reset;

	public TradesScreen() {
		super(Component.literal("Trades"));
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

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	protected void init() {
		reset = addRenderableWidget(new AshUi.AshButton(left() + W - PAD - BTN_W, top() + H - FOOT + 1, BTN_W, BTN_H,
				Component.literal("Forget perks (" + Trades.RESET_COINS + ")"), b -> PacketDistributor.sendToServer(new Net.TradeAct(Trades.RESET, "")), false));
	}

	static ItemStack icon(String trade) {
		return switch (trade) {
			case "cooking" -> new ItemStack(Trades.ITEMS.get("hunters_stew").get());
			case "brewing" -> new ItemStack(Trades.ITEMS.get("highmourn_ale").get());
			case "alchemy" -> new ItemStack(Trades.ITEMS.get("mending_draught").get());
			case "smithing" -> new ItemStack(Items.ANVIL);
			case "tailoring" -> new ItemStack(Items.STRING);
			case "farming" -> new ItemStack(Items.WHEAT);
			case "fishing" -> new ItemStack(Items.FISHING_ROD);
			default -> new ItemStack(Items.IRON_PICKAXE);
		};
	}

	private Trades.Trade rowAt(double mx, double my) {
		int i = (int) Math.floor((my - top() - TOP) / ROW_H);
		if (mx < left() + PAD || mx >= left() + PAD + LIST_W || my < top() + TOP || i < 0 || i >= Trades.ALL.size()) return null;
		return Trades.ALL.get(i);
	}

	private int perkX(Trades.Perk pk) {
		return left() + SIDE_X + pk.branch() * (COL_W + COL_GAP);
	}

	private int perkY(Trades.Perk pk) {
		return top() + PERKS_Y + 12 + pk.tier() * (PERK_H + PERK_GAP);
	}

	private Trades.Perk perkAt(double mx, double my) {
		for (Trades.Perk pk : Trades.PERKS.values()) {
			if (!pk.trade().equals(picked)) continue;
			int x = perkX(pk), y = perkY(pk);
			if (mx >= x && mx < x + COL_W && my >= y && my < y + PERK_H) return pk;
		}
		return null;
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		Trades.Trade t = rowAt(mx, my);
		if (t != null) {
			picked = t.id();
			return true;
		}
		Trades.Perk pk = perkAt(mx, my);
		if (pk != null && minecraft.player != null && Trades.why(minecraft.player, pk) == null) {
			PacketDistributor.sendToServer(new Net.TradeAct(Trades.TAKE_PERK, pk.id()));
			return true;
		}
		return super.mouseClicked(mx, my, button);
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		g.fill(0, 0, width, height, 0x90000000);
		int x = left(), y = top();
		AshUi.panel(g, x, y, W, H);
		AshUi.header(g, x, y, W, 24, "TRADES");
		Player p = minecraft.player;
		list(g, p, x + PAD, y + TOP, mx, my);
		side(g, p, x + SIDE_X, y + TOP, mx, my);
		AshUi.divider(g, x + PAD, y + H - FOOT - 4, W - 2 * PAD);
		buffs(g, p, x + PAD, y + H - FOOT + 5);
	}

	private void list(GuiGraphics g, Player p, int x, int y, int mx, int my) {
		Trades.Trade over = rowAt(mx, my);
		for (int i = 0; i < Trades.ALL.size(); i++) {
			Trades.Trade t = Trades.ALL.get(i);
			int ry = y + i * ROW_H, lv = Trades.level(p, t.id());
			AshUi.row(g, x, ry, LIST_W, ROW_H - 2, t.id().equals(picked), t == over);
			g.renderItem(icon(t.id()), x + 3, ry + 3);
			g.drawString(font, t.name(), x + 23, ry + 3, AshUi.TEXT, true);
			String lvl = Integer.toString(lv);
			g.drawString(font, lvl, x + LIST_W - 5 - font.width(lvl), ry + 3, lv > 1 ? AshUi.EMBER_LT : AshUi.MUTED, false);
			AshUi.bar(g, x + 24, ry + 15, LIST_W - 30, 2, Trades.into(Trades.xp(p, t.id())));
		}
	}

	private void side(GuiGraphics g, Player p, int x, int y, int mx, int my) {
		Trades.Trade t = Trades.trade(picked);
		int lv = Trades.level(p, picked), xp = Trades.xp(p, picked);
		g.drawString(font, Component.literal(t.name()).withStyle(ChatFormatting.BOLD), x, y, AshUi.TEXT, true);
		String lvl = Trades.rank(lv) + ", level " + lv + (lv < Trades.TOP_LEVEL ? " (" + Math.round(Trades.into(xp) * 100) + "%)" : "");
		g.drawString(font, lvl, x + SIDE_W - font.width(lvl), y, AshUi.EMBER_LT, false);
		int ty = y + 12;
		for (FormattedCharSequence line : font.split(Component.literal(t.blurb()), SIDE_W)) {
			g.drawString(font, line, x, ty, AshUi.MUTED, false);
			ty += 10;
		}
		g.drawString(font, font.plainSubstrByWidth(where(t), SIDE_W), x, ty, AshUi.DIM, false);
		int free = Trades.earned(p) - Trades.spent(p);
		String pts = free + " point" + (free == 1 ? "" : "s") + " to spend   (" + Trades.earned(p) + " of " + Trades.MOST_POINTS + " earned in all trades)";
		g.drawString(font, font.plainSubstrByWidth(pts, SIDE_W), x, ty + 12, free > 0 ? AshUi.EMBER_LT : AshUi.MUTED, false);
		int py = top() + PERKS_Y;
		for (int b = 0; b < 3; b++) {
			int cx = x + b * (COL_W + COL_GAP);
			String bn = t.branches()[b].toUpperCase();
			g.drawString(font, bn, cx + (COL_W - font.width(bn)) / 2, py, AshUi.LABEL, false);
		}
		Trades.Perk hover = perkAt(mx, my);
		for (Trades.Perk pk : Trades.PERKS.values()) {
			if (!pk.trade().equals(picked)) continue;
			int px = perkX(pk), y0 = perkY(pk);
			boolean mine = Trades.has(p, pk.id()), can = Trades.why(p, pk) == null;
			if (pk.tier() > 0) g.fill(px + COL_W / 2, y0 - PERK_GAP, px + COL_W / 2 + 1, y0, mine ? AshUi.EMBER_LT : AshUi.LINE);
			AshUi.row(g, px, y0, COL_W, PERK_H, mine, pk == hover);
			g.drawString(font, font.plainSubstrByWidth(pk.name(), COL_W - 8), px + 5, y0 + 4, mine ? AshUi.TEXT : can ? AshUi.BODY : AshUi.DIM, mine);
			String sub = mine ? "Yours" : "Level " + pk.level() + ", " + pk.cost() + " pt" + (pk.cost() > 1 ? "s" : "");
			g.drawString(font, font.plainSubstrByWidth(sub, COL_W - 8), px + 5, y0 + 15, mine ? AshUi.EMBER_LT : can ? AshUi.EMBER_C : AshUi.DIM, false);
		}
	}

	private static String where(Trades.Trade t) {
		return switch (t.id()) {
			case "cooking" -> "Sneak and use an empty hand on a stove, campfire or smoker";
			case "brewing" -> "Sneak and use an empty hand on a keg or a barrel";
			case "alchemy" -> "Sneak and use an empty hand on a brewing stand or cauldron";
			case "smithing", "tailoring" -> "Levels at the Gate Forge";
			default -> "Levels as you gather";
		};
	}

	private void buffs(GuiGraphics g, Player p, int x, int y) {
		List<Object[]> on = Trades.running(p);
		int room = W - 2 * PAD - BTN_W - 8;
		// what it's costing you, in front: tipsy, toxicity
		StringBuilder cost = new StringBuilder();
		int tipsy = Trades.tipsy(p);
		if (tipsy > 0) cost.append(tipsy == 1 ? "Tipsy" : "Drunk");
		double tox = Trades.toxicity(p);
		if (tox > 0.5) cost.append(cost.length() > 0 ? "   " : "").append("Toxicity ").append(Math.round(tox)).append("/").append(Math.round(Trades.toxLimit(p)));
		if (cost.length() > 0) {
			String c = cost + "   ";
			g.drawString(font, c, x, y, tox > Trades.toxLimit(p) ? AshUi.BAD : AshUi.EMBER_LT, false);
			x += font.width(c);
			room -= font.width(c);
		}
		if (on.isEmpty()) {
			g.drawString(font, font.plainSubstrByWidth("Nothing you've eaten or drunk is working now", room), x, y, AshUi.DIM, false);
			return;
		}
		StringBuilder sb = new StringBuilder();
		for (Object[] b : on) {
			long secs = (Long) b[1] / 20;
			if (sb.length() > 0) sb.append("   ");
			sb.append(((Trades.Good) b[0]).name()).append(" ").append(secs / 60).append(":").append(String.format("%02d", secs % 60));
		}
		g.drawString(font, font.plainSubstrByWidth(sb.toString(), room), x, y, AshUi.BODY, false);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		reset.active = minecraft.player != null && Trades.spent(minecraft.player) > 0;
		super.render(g, mx, my, pt);
		Trades.Perk pk = perkAt(mx, my);
		if (pk != null) {
			List<Component> lines = new ArrayList<>();
			lines.add(Component.literal(pk.name()).withStyle(ChatFormatting.GOLD));
			lines.add(Component.literal(pk.text()));
			String no = Trades.why(minecraft.player, pk);
			if (no != null) lines.add(Component.literal(no).withStyle(Trades.has(minecraft.player, pk.id()) ? ChatFormatting.GREEN : ChatFormatting.RED));
			else lines.add(Component.literal("Click to take it (" + pk.cost() + " point" + (pk.cost() > 1 ? "s" : "") + ")").withStyle(ChatFormatting.GRAY));
			g.renderComponentTooltip(font, lines, mx, my);
		}
		Trades.Trade t = rowAt(mx, my);
		if (t != null) {
			int xp = Trades.xp(minecraft.player, t.id()), lv = Trades.level(xp);
			g.renderComponentTooltip(font, List.of(Component.literal(t.name() + ", " + Trades.rank(lv) + " " + lv), Component.literal(lv >= Trades.TOP_LEVEL ? "Mastered"
					: Math.round(Trades.into(xp) * Trades.need(lv)) + " / " + Trades.need(lv) + " XP to " + (lv + 1)).withStyle(ChatFormatting.GRAY)), mx, my);
		}
	}
}
