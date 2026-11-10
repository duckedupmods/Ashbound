package com.snoringwalrus.ashbound.client;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.client.event.RenderGuiLayerEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;
import net.neoforged.neoforge.common.NeoForge;

/**
 * The hotbar in the same tiles as the Character screen, rimmed by rarity, the held one lit ember. Items sit exactly where vanilla's
 * do, so whatever's measured off the hotbar still lines up. A spectator keeps vanilla's, which is a different thing.
 */
public final class HotbarHud {
	private HotbarHud() {}

	private static final int SLOTS = 9, CELL = 20, W = 182, UP = 21;

	public static void hooks() {
		NeoForge.EVENT_BUS.addListener((RenderGuiLayerEvent.Pre e) -> {
			Minecraft mc = Minecraft.getInstance();
			if (!e.getName().equals(VanillaGuiLayers.HOTBAR) || !(mc.getCameraEntity() instanceof Player p) || p.isSpectator()) return;
			e.setCanceled(true);
			if (!mc.options.hideGui) draw(e.getGuiGraphics(), mc, p, e.getPartialTick().getGameTimeDeltaPartialTick(true));
		});
	}

	private static void draw(GuiGraphics g, Minecraft mc, Player p, float pt) {
		int x0 = (g.guiWidth() - W) / 2 + 1, y = g.guiHeight() - UP;
		g.fill(x0 - 1, y - 1, x0 - 1 + W, y + CELL + 1, 0xFF050404);
		for (int i = 0; i < SLOTS; i++) {
			ItemStack s = p.getInventory().getItem(i);
			int x = x0 + i * CELL;
			AshUi.tile(g, x, y, CELL, AshUi.rarity(s, 0));
			if (i != p.getInventory().selected) continue;
			g.fillGradient(x + 2, y + 2, x + CELL - 2, y + CELL - 2, 0x10E8742C, 0x70E8742C);
			g.renderOutline(x, y, CELL, CELL, AshUi.EMBER_LT);
		}
		for (int i = 0; i < SLOTS; i++) {
			ItemStack s = p.getInventory().getItem(i);
			if (!s.isEmpty()) item(g, mc, p, s, x0 + i * CELL + 2, y + 2, i + 1, pt);
		}
	}

	/** With vanilla's little hop when it's just been picked up. */
	private static void item(GuiGraphics g, Minecraft mc, Player p, ItemStack s, int x, int y, int seed, float pt) {
		float pop = s.getPopTime() - pt;
		if (pop > 0) {
			float k = 1 + pop / 12.5f;
			g.pose().pushPose();
			g.pose().translate(x + 8, y + 12, 0);
			g.pose().scale(1 / k, (k + 1) / 2, 1);
			g.pose().translate(-(x + 8), -(y + 12), 0);
		}
		g.renderItem(p, s, x, y, seed);
		if (pop > 0) g.pose().popPose();
		g.renderItemDecorations(mc.font, s, x, y);
	}
}
