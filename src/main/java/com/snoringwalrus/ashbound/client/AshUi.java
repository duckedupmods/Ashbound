package com.snoringwalrus.ashbound.client;

import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;

/**
 * The Ashbound look for screens (sprites from the old mod's tools/ui_sprites.py): a near-black char ground with
 * falling ash and a faint ember glow from below, a blackened iron frame with cut corners, bone-white text, ember
 * orange only for what matters (what's picked, the main button, coins).
 */
final class AshUi {
	private AshUi() {}

	static final ResourceLocation GROUND = id("ground"), CHAR = id("char"), EMBER = id("ember"), FRAME = id("frame"), COIN = id("coin"),
			PARCHMENT = id("parchment"), WOOD = id("wood"), FLAME = id("flame"), SEAL = id("seal"), PIN = id("pin");
	static final int INK = 0xFF2A1A0C, INK_RED = 0xFF8A2A10;

	static final int TEXT = 0xFFECE4D6, BODY = 0xFFD9D2C5, MUTED = 0xFF9A9086, DIM = 0xFF6F685D, LABEL = 0xFFA0968A,
			EMBER_C = 0xFFE8742C, EMBER_LT = 0xFFF0A050, LINE = 0xFF3D3833, BLACK = 0xFF050404, BAD = 0xFFE07A62;
	/** The frame's cut corners are this deep; what's drawn under the panel stays inside them. */
	static final int CUT = 5;

	private static ResourceLocation id(String name) {
		return ResourceLocation.fromNamespaceAndPath("ashbound", "ash/" + name);
	}

	static Font font() {
		return Minecraft.getInstance().font;
	}

	/** A panel: the ash ground, the ember glow rising from the bottom, the iron frame round it. */
	static void panel(GuiGraphics g, int x, int y, int w, int h) {
		g.blitSprite(GROUND, x + CUT, y, w - 2 * CUT, h);
		g.blitSprite(GROUND, x, y + CUT, CUT, h - 2 * CUT);
		g.blitSprite(GROUND, x + w - CUT, y + CUT, CUT, h - 2 * CUT);
		g.fillGradient(x + CUT, y + h / 2, x + w - CUT, y + h - 2, 0x00000000, 0x2C96340E);
		g.fillGradient(x + CUT, y + 2, x + w - CUT, y + 14, 0x50000000, 0x00000000);
		g.blitSprite(FRAME, x, y, w, h);
	}

	/** A dark strip across the top of a panel with a title in it, between two rules. */
	static void header(GuiGraphics g, int x, int y, int w, int h, String title) {
		g.blitSprite(CHAR, x + 4, y + 4, w - 8, h - 4);
		g.fill(x + 4, y + h - 1, x + w - 4, y + h, BLACK);
		g.fill(x + 4, y + h, x + w - 4, y + h + 1, 0xFF5C544C);
		g.fill(x + w / 4, y + h - 2, x + w * 3 / 4, y + h - 1, 0x60E8742C);
		if (title == null) return;
		Font f = font();
		Component t = Component.literal(title).withStyle(ChatFormatting.BOLD);
		int tw = f.width(t);
		int cy = y + (h - 8) / 2 + 2;
		g.drawString(f, t, x + (w - tw) / 2, cy, TEXT, true);
		rule(g, x + 14, x + (w - tw) / 2 - 14, cy + 3, false);
		rule(g, x + (w + tw) / 2 + 14, x + w - 14, cy + 3, true);
		diamond(g, x + (w - tw) / 2 - 9, cy + 1);
		diamond(g, x + (w + tw) / 2 + 5, cy + 1);
	}

	/** A thin line fading out toward one end. */
	static void rule(GuiGraphics g, int x0, int x1, int y, boolean fadeRight) {
		int n = Math.max(1, x1 - x0);
		for (int i = 0; i < n; i += 2) {
			float k = fadeRight ? 1 - i / (float) n : i / (float) n;
			g.fill(x0 + i, y, Math.min(x1, x0 + i + 2), y + 1, ((int) (0xC0 * k) << 24) | 0x857B70);
		}
	}

	/** A small 5x5 diamond, bone grey with an ember heart. */
	static void diamond(GuiGraphics g, int x, int y) {
		int c = 0xFF8A8076;
		g.fill(x + 2, y, x + 3, y + 5, BLACK);
		g.fill(x, y + 2, x + 5, y + 3, BLACK);
		g.fill(x + 1, y + 1, x + 4, y + 4, c);
		g.fill(x + 2, y + 2, x + 3, y + 3, EMBER_C);
	}

	/** A divider: a dark line with a light one under it. */
	static void divider(GuiGraphics g, int x, int y, int w) {
		g.fill(x, y, x + w, y + 1, BLACK);
		g.fill(x, y + 1, x + w, y + 2, LINE);
	}

	/** A sunk box (steppers). */
	static void inset(GuiGraphics g, int x, int y, int w, int h) {
		g.fill(x, y, x + w, y + h, 0x9A050404);
		g.renderOutline(x, y, w, h, BLACK);
		g.renderOutline(x + 1, y + 1, w - 2, h - 2, LINE);
	}

	/** A row in a list: faintly lit, or glowing ember when it's the one picked. */
	static void row(GuiGraphics g, int x, int y, int w, int h, boolean picked, boolean hover) {
		if (picked) {
			g.blitSprite(EMBER, x, y, w, h);
			g.renderOutline(x, y, w, h, BLACK);
			g.renderOutline(x + 1, y + 1, w - 2, h - 2, EMBER_LT);
			g.fill(x + 1, y + 1, x + 3, y + h - 1, EMBER_LT);
		} else {
			g.fill(x, y, x + w, y + h, hover ? 0x22FFF0DC : 0x10FFF0DC);
			g.renderOutline(x, y, w, h, BLACK);
			g.renderOutline(x + 1, y + 1, w - 2, h - 2, hover ? 0xFF8A8076 : 0xFF3D3833);
		}
	}

	static final int[] RARITY_RIM = {0xFF6A625A, 0xFF5A7898, 0xFFB89A52, 0xFFE07A36};
	static final int[] RARITY_FILL = {0xFF2C2925, 0xFF1C2838, 0xFF3A3018, 0xFF4A220C};
	static final int[] RARITY_TEXT = {0xFFE2DBCF, 0xFF9CBDE0, 0xFFECCA70, 0xFFF39150};

	/** 0 common, 1 fine, 2 rare, 3 prized: the item's own rarity, nudged up by what it costs. */
	static int rarity(ItemStack s, int price) {
		int r = s.getRarity() == Rarity.EPIC ? 3 : s.getRarity() == Rarity.RARE ? 2 : s.getRarity() == Rarity.UNCOMMON ? 1 : 0;
		int byPrice = price >= 190 ? 3 : price >= 110 ? 2 : price >= 50 ? 1 : 0;
		return Math.max(r, byPrice);
	}

	/** An item's tile: dark, tinted and rimmed by its rarity. */
	static void tile(GuiGraphics g, int x, int y, int size, int rarity) {
		g.fill(x, y, x + size, y + size, BLACK);
		g.fill(x + 1, y + 1, x + size - 1, y + size - 1, RARITY_RIM[rarity]);
		g.fill(x + 2, y + 2, x + size - 2, y + size - 2, 0xFF0E0C0B);
		g.fillGradient(x + 2, y + 2, x + size - 2, y + size - 2, RARITY_FILL[rarity], 0xFF0E0C0B);
	}

	/** A sprite tinted by an 0xAARRGGBB colour. */
	static void tinted(GuiGraphics g, ResourceLocation sprite, int x, int y, int w, int h, int colour) {
		g.setColor((colour >> 16 & 255) / 255f, (colour >> 8 & 255) / 255f, (colour & 255) / 255f, (colour >>> 24) / 255f);
		g.blitSprite(sprite, x, y, w, h);
		g.setColor(1f, 1f, 1f, 1f);
	}

	static void flame(GuiGraphics g, int x, int y) {
		g.blitSprite(FLAME, x, y, 7, 9);
	}

	/** A bar in a black trough, filled ember. */
	static void bar(GuiGraphics g, int x, int y, int w, int h, float k) {
		g.fill(x - 1, y - 1, x + w + 1, y + h + 1, 0xFF5C544C);
		g.fill(x, y, x + w, y + h, 0xFF0C0B0A);
		int f = (int) (w * Math.max(0, Math.min(1, k)));
		if (f > 0) {
			g.fillGradient(x, y, x + f, y + h, 0xFFFFB060, 0xFFC0501C);
			g.fill(x, y, x + f, y + 1, 0x80FFD8A8);
		}
	}

	static final int[] RANK_WAX = {0xFF8A8480, 0xFF4E8A44, 0xFF3E8A98, 0xFF4A64B0, 0xFF7A48A0, 0xFFB08A34, 0xFFA8382C, 0xFF8A1C2C, 0xFFD8B850};

	/** A wax seal in the rank's colour with its letter. */
	static void seal(GuiGraphics g, int x, int y, int size, int rank) {
		rank = Math.max(0, Math.min(RANK_WAX.length - 1, rank));
		tinted(g, SEAL, x, y, size, size, RANK_WAX[rank]);
		String r = com.snoringwalrus.ashbound.Guild.RANKS[rank];
		float s = size >= 20 ? (r.length() > 1 ? 1f : 1.4f) : (r.length() > 2 ? 0.55f : r.length() > 1 ? 0.7f : 1f);
		g.pose().pushPose();
		g.pose().translate(x + size / 2f, y + size / 2f - 3.5f * s, 0);
		g.pose().scale(s, s, 1f);
		Component t = Component.literal(r).withStyle(ChatFormatting.BOLD);
		g.drawString(font(), t, -font().width(t) / 2, 0, 0xFFF4EEE4, true);
		g.pose().popPose();
	}

	static void coin(GuiGraphics g, int x, int y) {
		g.blitSprite(COIN, x, y, 9, 9);
	}

	/** "120 (coin)", right-aligned to rx. Returns its left edge. */
	static int price(GuiGraphics g, int rx, int y, int amount, int colour) {
		String s = String.format("%,d", amount);
		int w = font().width(s);
		coin(g, rx - 9, y - 1);
		g.drawString(font(), s, rx - 12 - w, y, colour, true);
		return rx - 12 - w;
	}

	/** A button in the look: iron and char, or glowing ember for the one that matters. */
	static class AshButton extends Button {
		final boolean ember;

		AshButton(int x, int y, int w, int h, Component msg, OnPress press, boolean ember) {
			super(x, y, w, h, msg, press, DEFAULT_NARRATION);
			this.ember = ember;
		}

		@Override
		protected void renderWidget(GuiGraphics g, int mx, int my, float pt) {
			int x = getX(), y = getY(), w = getWidth(), h = getHeight();
			boolean hot = isHoveredOrFocused() && active;
			if (ember && active) {
				g.blitSprite(EMBER, x, y, w, h);
				g.fillGradient(x + 2, y + 2, x + w - 2, y + h / 2, hot ? 0x40FFAA5A : 0x24FFAA5A, 0x00FFAA5A);
				g.renderOutline(x, y, w, h, BLACK);
				g.renderOutline(x + 1, y + 1, w - 2, h - 2, hot ? 0xFFFFC888 : EMBER_LT);
			} else {
				g.blitSprite(CHAR, x, y, w, h);
				g.renderOutline(x, y, w, h, BLACK);
				g.renderOutline(x + 1, y + 1, w - 2, h - 2, !active ? 0xFF2C2724 : hot ? 0xFFA0968A : 0xFF6A625A);
			}
			int c = !active ? 0xFF5A544C : ember ? 0xFFFFF3E2 : hot ? 0xFFFFFFFF : 0xFFDDD5C8;
			Component m = getMessage();
			g.drawString(font(), m, x + (w - font().width(m)) / 2, y + (h - 8) / 2, c, true);
		}
	}
}
