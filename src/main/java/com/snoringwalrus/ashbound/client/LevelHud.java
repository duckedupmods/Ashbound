package com.snoringwalrus.ashbound.client;

import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Levels;

import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;

/**
 * Level and Ash, right of the hotbar past the relic: an ember bar for the way to the next level, shown for a few seconds after Ash
 * comes in, while the player list key (TAB) is held, or while a level is ready to buy in the tree (K). A level up
 * gets a big moment in the middle.
 */
public final class LevelHud {
	private LevelHud() {}

	private static final int RIGHT_OF_RELIC = 34;
	private static float shown;

	public static void hooks(IEventBus bus) {
		bus.addListener((RegisterGuiLayersEvent e) -> e.registerAbove(VanillaGuiLayers.HOTBAR,
				ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "level"), LevelHud::draw));
	}

	private static void draw(GuiGraphics g, DeltaTracker dt) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || mc.options.hideGui) return;
		long now = System.currentTimeMillis();
		boolean ready = Levels.clientNext > 0 && Levels.clientAsh >= Levels.clientNext;
		boolean show = ready || mc.options.keyPlayerList.isDown() || now - Levels.clientGained < 4000 || now - Levels.clientLevelled < 4000;
		float f = Levels.clientNext > 0 ? Math.min(1, Levels.clientAsh / (float) Levels.clientNext) : 1;
		shown += (f - shown) * 0.2f;
		if (show) {
			int w = 70, h = 4;
			int x = g.guiWidth() / 2 + 91 + RIGHT_OF_RELIC, y = g.guiHeight() - 10;
			g.fill(x - 1, y - 1, x + w + 1, y + h + 1, 0xC0050404);
			g.fill(x, y, x + w, y + h, 0xFF2A1A12);
			int fw = Math.round(w * shown);
			g.fillGradient(x, y, x + fw, y + h, 0xFFFFB050, 0xFFB0401A);
			g.fill(x, y, x + fw, y + 1, 0xFFFFE0B0);
			String lv = ready ? "Lv " + Levels.clientLevel + "  level up: K" : "Lv " + Levels.clientLevel;
			g.drawString(mc.font, lv, ready ? x + w - mc.font.width(lv) : x, y - 10, 0xFFFFC870, true);
			if (!ready) {
				String ash = Levels.clientNext > 0 ? Levels.clientAsh + " / " + Levels.clientNext : "max";
				g.drawString(mc.font, ash, x + w - mc.font.width(ash), y - 10, 0xFFB8A090, true);
			}
		}
		long since = now - Levels.clientLevelled;
		if (since < 3000) {
			// fades in fast, holds, fades out
			float a = since < 250 ? since / 250f : since > 2200 ? (3000 - since) / 800f : 1f;
			int alpha = Math.max(4, Math.round(a * 255)) << 24;
			String t = "LEVEL " + Levels.clientLevel;
			var pose = g.pose();
			pose.pushPose();
			pose.translate(g.guiWidth() / 2f, g.guiHeight() / 3f, 0);
			pose.scale(3f, 3f, 1f);
			g.drawString(mc.font, t, -mc.font.width(t) / 2, -4, alpha | 0xFFC060, true);
			pose.popPose();
			String sub = "+1 skill point";
			g.drawString(mc.font, sub, (g.guiWidth() - mc.font.width(sub)) / 2, g.guiHeight() / 3 + 12, alpha | 0xD8C8B8, true);
		}
	}
}
