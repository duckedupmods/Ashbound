package com.snoringwalrus.ashbound.client;

import java.util.List;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.math.Axis;
import com.snoringwalrus.ashbound.Ashbound;

import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

/**
 * Hob's photographs: old black-and-white prints of a gate of each of the first three ranks, the tear the only thing in
 * colour (tools/blender/intro_photos.py). He shows them in the intro (IntroScene) and gives them to you; using them
 * (Intro.PHOTOS) lays them out again. The caption is written on each print's bottom strip, here, not in the picture.
 */
public final class Photos {
	private Photos() {}

	/** A print: its rank, the tear's colour, what Hob wrote under it. */
	record Print(String rank, int colour, String line, ResourceLocation tex) {}

	static final List<Print> ALL = List.of(
			new Print("F", 0xCDD2DC, "Pale. The weakest. Start with these.", tex("f")),
			new Print("E", 0x46E678, "Green. Still forgiving, mostly.", tex("e")),
			new Print("D", 0x3C8CFF, "Blue. Go with friends.", tex("d")));
	/** the higher ranks, said rather than shown */
	static final String ABOVE = "Above D: C purple, B orange, A and S red. Leave those to the guild's best.";
	/** the print's size in its texture, and where the strip under the picture starts */
	static final int W = 684, H = 454, STRIP = 382;
	private static final int INK = 0x2A2420, SHADOW = 0x000000;
	private static final float TITLE = 3.2f, LINE = 2.1f;

	private static ResourceLocation tex(String rank) {
		return ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/gui/photos/" + rank + ".png");
	}

	/** One print, centred on cx, cy, so wide on screen, turned by a few degrees, faded by alpha. */
	static void draw(GuiGraphics g, Font font, Print p, float cx, float cy, float width, float degrees, float alpha) {
		if (alpha <= 0.01f) return;
		float s = width / W;
		var ps = g.pose();
		ps.pushPose();
		ps.translate(cx, cy, 0);
		ps.mulPose(Axis.ZP.rotationDegrees(degrees));
		ps.scale(s, s, 1);
		int a = Mth.clamp(Math.round(alpha * 255), 4, 255) << 24;
		g.fill(-W / 2 + 10, -H / 2 + 14, W / 2 + 10, H / 2 + 14, Math.round(alpha * 110) << 24 | SHADOW);   // its shadow on the table
		RenderSystem.enableBlend();
		RenderSystem.setShaderColor(1, 1, 1, alpha);
		g.blit(p.tex(), -W / 2, -H / 2, 0, 0, W, H, W, H);
		RenderSystem.setShaderColor(1, 1, 1, 1);
		// the caption, in ink on the strip: its rank big, a stroke of its colour, and Hob's word on it
		int y = -H / 2 + STRIP + 8;
		Component rank = Component.literal(p.rank() + " RANK").withStyle(ChatFormatting.BOLD);
		ps.pushPose();
		ps.translate(-W / 2f + 26, y, 0);
		ps.scale(TITLE, TITLE, 1);
		g.drawString(font, rank, 0, 0, a | INK, false);
		int stroke = font.width(rank) + 6;
		g.fill(stroke, 2, stroke + 14, 6, a | p.colour());
		ps.popPose();
		ps.pushPose();
		ps.translate(-W / 2f + 26, y + 9 * TITLE + 2, 0);
		ps.scale(LINE, LINE, 1);
		g.drawString(font, p.line(), 0, 0, a | INK, false);
		ps.popPose();
		ps.popPose();
	}

	/** Using the photographs: all three on the table, and what Hob said of the rest. */
	public static final class Table extends Screen {
		private static final float[] TURN = {-5, 2, 6};

		public Table() {
			super(Component.literal("Hob's photographs"));
		}

		@Override
		public boolean isPauseScreen() {
			return false;
		}

		@Override
		public void render(GuiGraphics g, int mx, int my, float pt) {
			super.render(g, mx, my, pt);
			float w = Math.min(width * 0.36f, (height - 90) * (float) W / H), step = Math.min(w * 0.92f, (width - w - 24) / 2f);
			for (int i = 0; i < ALL.size(); i++) draw(g, font, ALL.get(i), width / 2f + (i - 1) * step, height / 2f - 6 + (i == 1 ? -8 : 4), w, TURN[i], 1);
			AshUi.header(g, width / 2 - 120, 8, 240, 20, "HOB'S PHOTOGRAPHS");
			g.drawCenteredString(font, "A gate's colour is its rank.", width / 2, height - 34, AshUi.TEXT);
			g.drawCenteredString(font, ABOVE, width / 2, height - 22, AshUi.MUTED);
		}
	}
}
