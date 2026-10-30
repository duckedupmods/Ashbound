package com.snoringwalrus.ashbound.client;

import java.util.List;

import com.snoringwalrus.ashbound.Coins;
import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Npc;
import com.snoringwalrus.ashbound.Shop;

import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * A shopkeeper's wares (Shop), in the ash look: on the left their name over the Buy / Sell list in two columns (each
 * ware on a tile tinted by how fine it is, its price in coins), your purse along the bottom; on the right the one you
 * picked, big, with how many you want and the ember Buy (or Sell) button.
 */
public class ShopScreen extends Screen {
	private static final int ROW = 24, GAP = 3, DETAIL = 160;
	private static final String[] RARITY = {"Common", "Fine", "Rare", "Prized"};

	private final Net.ShopOpen shop;
	private boolean sellTab;
	private int selected, scroll, qty = 1;
	private AshUi.AshButton less, more, deal, all;
	private ItemStack hoverStack;

	public ShopScreen(Net.ShopOpen msg) {
		super(Component.literal(msg.name()));
		shop = msg;
	}

	private List<Net.ShopLine> list() {
		return sellTab ? shop.sell() : shop.buy();
	}

	private Net.ShopLine sel() {
		List<Net.ShopLine> l = list();
		return selected >= 0 && selected < l.size() ? l.get(selected) : null;
	}

	// ---------------------------------------------------------------- layout

	private int pw() {
		return Math.min(width - 16, 560);
	}

	private int ph() {
		return Math.min(height - 16, 270);
	}

	private int px() {
		return (width - pw()) / 2;
	}

	private int py() {
		return (height - ph()) / 2;
	}

	private int mainW() {
		return pw() - DETAIL - 6;
	}

	private int gridX() {
		return px() + 10;
	}

	private int gridY() {
		return py() + 46;
	}

	private int gridW() {
		return mainW() - 20;
	}

	private int colW() {
		return (gridW() - 4) / 2;
	}

	private int rowsShown() {
		return Math.max(1, (ph() - 46 - 30) / (ROW + GAP));
	}

	private int dx() {
		return px() + mainW() + 6;
	}

	@Override
	protected void init() {
		int x = dx(), w = DETAIL, by = py() + ph() - 34;
		less = addRenderableWidget(new AshUi.AshButton(x + w - 74, py() + 122, 18, 16, Component.literal("-"), b -> setQty(qty - 1), false));
		more = addRenderableWidget(new AshUi.AshButton(x + w - 28, py() + 122, 18, 16, Component.literal("+"), b -> setQty(qty + 1), false));
		all = addRenderableWidget(new AshUi.AshButton(x + 10, by - 22, w - 20, 16, Component.literal("ALL OF IT"), b -> setQty(64), false));
		deal = addRenderableWidget(new AshUi.AshButton(x + 10, by, w - 20, 22, Component.empty(), b -> trade(), true));
	}

	private void setQty(int n) {
		Net.ShopLine s = sel();
		int cap = 64;
		if (s != null && sellTab) cap = Math.max(1, Math.min(64, Shop.carried(minecraft.player, s.stack())));
		qty = Math.max(1, Math.min(cap, n));
	}

	private void trade() {
		if (sel() != null) PacketDistributor.sendToServer(new Net.ShopTrade(shop.entity(), sellTab, selected, qty));
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public void tick() {
		if (minecraft.player == null || !(minecraft.level.getEntity(shop.entity()) instanceof Npc n) || n.distanceTo(minecraft.player) > 8) onClose();
		if (sellTab) setQty(qty);
	}

	/** Which ware is under the mouse, or -1. */
	private int wareAt(double mx, double my) {
		if (mx < gridX() || mx >= gridX() + gridW() || my < gridY()) return -1;
		int r = (int) ((my - gridY()) / (ROW + GAP));
		if (r >= rowsShown() || (my - gridY()) - r * (ROW + GAP) >= ROW) return -1;
		int c = mx < gridX() + colW() ? 0 : mx >= gridX() + colW() + 4 ? 1 : -1;
		if (c < 0) return -1;
		int i = (r + scroll) * 2 + c;
		return i < list().size() ? i : -1;
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		if (super.mouseClicked(mx, my, button)) return true;
		int ty = py() + 27;
		if (my >= ty - 2 && my < ty + 12) {
			if (mx >= gridX() && mx < gridX() + 28) return tab(false);
			if (mx >= gridX() + 36 && mx < gridX() + 68) return tab(true);
		}
		int i = wareAt(mx, my);
		if (i >= 0) {
			if (i != selected) qty = 1;
			selected = i;
			setQty(qty);
			return true;
		}
		return false;
	}

	private boolean tab(boolean sell) {
		sellTab = sell;
		selected = 0;
		scroll = 0;
		setQty(1);
		return true;
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double sx, double sy) {
		int max = Math.max(0, (list().size() + 1) / 2 - rowsShown());
		scroll = Math.max(0, Math.min(max, scroll - (int) Math.signum(sy)));
		return true;
	}

	// ---------------------------------------------------------------- drawing

	/** Everything but the buttons, which the screen draws over it. */
	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		g.fill(0, 0, width, height, 0x70000000);
		int x = px(), y = py(), w = mainW(), h = ph();
		int coins = Coins.client;
		boolean free = minecraft.player.isCreative();
		AshUi.panel(g, x, y, w, h);
		AshUi.header(g, x, y, w, 20, shop.name().toUpperCase());
		int ty = y + 27;
		tabLabel(g, "BUY", gridX(), ty, !sellTab);
		tabLabel(g, "SELL", gridX() + 36, ty, sellTab);
		g.drawString(font, shop.title(), x + w - 10 - font.width(shop.title()), ty, AshUi.EMBER_LT, true);
		AshUi.divider(g, gridX(), ty + 11, gridW());
		List<Net.ShopLine> l = list();
		hoverStack = null;
		int hovered = wareAt(mx, my);
		for (int r = 0; r < rowsShown(); r++) {
			for (int c = 0; c < 2; c++) {
				int i = (r + scroll) * 2 + c;
				if (i >= l.size()) break;
				Net.ShopLine s = l.get(i);
				int rx = gridX() + c * (colW() + 4), ry = gridY() + r * (ROW + GAP);
				AshUi.row(g, rx, ry, colW(), ROW, i == selected, i == hovered);
				int rar = AshUi.rarity(s.stack(), s.price());
				AshUi.tile(g, rx + 2, ry + 2, 20, rar);
				g.renderItem(s.stack(), rx + 4, ry + 4);
				if (i == hovered && mx < rx + 22) hoverStack = s.stack();
				boolean can = sellTab ? Shop.carried(minecraft.player, s.stack()) > 0 : free || coins >= s.price();
				int priceX = AshUi.price(g, rx + colW() - 5, ry + 8, s.price(), can ? AshUi.TEXT : AshUi.BAD);
				int tw = priceX - (rx + 26) - 4;
				g.drawString(font, font.plainSubstrByWidth(s.stack().getHoverName().getString(), tw), rx + 26, ry + 4, can ? AshUi.RARITY_TEXT[rar] : AshUi.DIM, true);
				String sub = sellTab ? "You have " + Shop.carried(minecraft.player, s.stack()) : s.stack().getCount() > 1 ? "Bundle of " + s.stack().getCount() : "Single";
				g.drawString(font, font.plainSubstrByWidth(sub, tw), rx + 26, ry + 14, i == selected ? 0xFFFFD2A8 : AshUi.DIM, false);
			}
		}
		if (l.isEmpty()) g.drawString(font, sellTab ? "Not buying anything." : "Nothing for sale.", gridX() + 4, gridY() + 6, AshUi.MUTED, false);
		if ((l.size() + 1) / 2 > rowsShown()) {
			String more = "scroll for more";
			g.drawString(font, more, x + w - 10 - font.width(more), y + h - 32, AshUi.DIM, false);
		}
		// the purse
		AshUi.divider(g, x + 10, y + h - 24, w - 20);
		AshUi.coin(g, x + 12, y + h - 16);
		String cs = String.format("%,d", coins);
		g.drawString(font, Component.literal(cs).withStyle(ChatFormatting.BOLD), x + 25, y + h - 15, AshUi.TEXT, true);
		g.drawString(font, "COINS", x + 30 + font.width(cs) + 6, y + h - 15, AshUi.LABEL, false);
		String hint = "Esc  leave";
		g.drawString(font, hint, x + w - 12 - font.width(hint), y + h - 15, AshUi.DIM, false);
		detail(g, coins, free);
		if (hoverStack == null && sel() != null && mx >= dx() + DETAIL - 46 && mx < dx() + DETAIL - 10 && my >= y + 12 && my < y + 48) hoverStack = sel().stack();
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		if (hoverStack != null) g.renderTooltip(font, hoverStack, mx, my);
	}

	private void tabLabel(GuiGraphics g, String s, int x, int y, boolean on) {
		Component t = Component.literal(s).withStyle(ChatFormatting.BOLD);
		g.drawString(font, t, x, y, on ? 0xFFF2EADC : 0xFF8A8076, true);
		if (on) g.fill(x, y + 10, x + font.width(t), y + 11, AshUi.EMBER_C);
	}

	/** The picked ware: big, its numbers, how many, the deal. */
	private void detail(GuiGraphics g, int coins, boolean free) {
		int x = dx(), y = py(), w = DETAIL, h = ph();
		AshUi.panel(g, x, y, w, h);
		Net.ShopLine s = sel();
		less.visible = more.visible = deal.visible = all.visible = s != null;
		if (s == null) return;
		int rar = AshUi.rarity(s.stack(), s.price());
		int tint = AshUi.RARITY_RIM[rar] & 0x00FFFFFF;
		g.fillGradient(x + 4, y + 4, x + w - 4, y + 54, 0x50000000 | tint, tint);
		AshUi.divider(g, x + 4, y + 54, w - 8);
		AshUi.tile(g, x + w - 46, y + 12, 36, rar);
		g.pose().pushPose();
		g.pose().translate(x + w - 44, y + 14, 0);
		g.pose().scale(2f, 2f, 1f);
		g.renderItem(s.stack(), 0, 0);
		g.pose().popPose();
		int ty = y + 12;
		for (FormattedCharSequence line : font.split(s.stack().getHoverName().copy().withStyle(ChatFormatting.BOLD), w - 64)) {
			g.drawString(font, line, x + 10, ty, AshUi.RARITY_TEXT[rar], true);
			ty += 10;
		}
		g.drawString(font, RARITY[rar] + (s.stack().getCount() > 1 ? "  x" + s.stack().getCount() : ""), x + 10, ty + 2, 0xFFC8B98F, false);
		int have = Shop.carried(minecraft.player, s.stack());
		int ly = y + 64;
		line(g, x, ly, sellTab ? "PAYS EACH" : "PRICE", s.price(), true);
		line(g, x, ly + 14, "IN YOUR PACK", have, false);
		g.drawString(font, "HOW MANY", x + 10, y + 126, AshUi.LABEL, false);
		AshUi.inset(g, x + w - 54, y + 122, 24, 16);
		String q = String.valueOf(qty);
		g.drawString(font, q, x + w - 42 - font.width(q) / 2, y + 126, 0xFFFFFFFF, true);
		int total = qty * s.price();
		AshUi.divider(g, x + 10, y + 144, w - 20);
		if (sellTab) {
			all.visible = true;
			all.active = have > 1;
			deal.setMessage(Component.literal("SELL " + qty + "  +" + String.format("%,d", total)));
			deal.active = have > 0;
			String after = "Purse after: " + String.format("%,d", coins + (have > 0 ? Math.min(qty, have) * s.price() : 0));
			g.drawString(font, after, x + (w - font.width(after)) / 2, y + 150, AshUi.MUTED, false);
		} else {
			all.visible = false;
			deal.setMessage(Component.literal("BUY " + qty + "  " + String.format("%,d", total)));
			deal.active = free || coins >= total;
			String after = free ? "Creative: free" : coins >= total ? "Purse after: " + String.format("%,d", coins - total) : "Not enough coins";
			g.drawString(font, after, x + (w - font.width(after)) / 2, y + 150, coins >= total || free ? AshUi.MUTED : AshUi.BAD, false);
		}
		less.active = qty > 1;
		more.active = qty < (sellTab ? Math.max(1, Math.min(64, have)) : 64);
	}

	private void line(GuiGraphics g, int x, int y, String label, int value, boolean money) {
		g.drawString(font, label, x + 10, y, AshUi.LABEL, false);
		if (money) AshUi.price(g, x + DETAIL - 10, y, value, AshUi.TEXT);
		else g.drawString(font, String.valueOf(value), x + DETAIL - 10 - font.width(String.valueOf(value)), y, AshUi.TEXT, true);
	}
}
