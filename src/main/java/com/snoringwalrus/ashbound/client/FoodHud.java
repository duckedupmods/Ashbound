package com.snoringwalrus.ashbound.client;

import java.util.List;

import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Trades;

import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;

/**
 * What you've eaten and drunk that's working now (11/7, the user: "no way to see the buffs from food anywhere"): left of the
 * hotbar, one iron socket each (the meal, the brew, the elixirs, the snack) with the minutes left under it; hold TAB and
 * what each one gives is written above them.
 */
public final class FoodHud {
	private FoodHud() {}

	private static final int TILE = 22;

	public static void hooks(IEventBus bus) {
		bus.addListener((RegisterGuiLayersEvent e) -> e.registerAbove(VanillaGuiLayers.HOTBAR,
				ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "food_buffs"), FoodHud::draw));
	}

	/** The thing to show for a buff: our good's item, or the food a snack came from. */
	private static ItemStack icon(Trades.Good g) {
		if (g.id().startsWith(Trades.SNACK)) {
			ResourceLocation id = ResourceLocation.tryParse(g.id().substring(Trades.SNACK.length()));
			return id == null ? ItemStack.EMPTY : new ItemStack(BuiltInRegistries.ITEM.get(id));
		}
		var it = Trades.ITEMS.get(g.id());
		return it == null ? ItemStack.EMPTY : new ItemStack(it.get());
	}

	private static String clock(long ticks) {
		long s = ticks / 20;
		return s >= 60 ? (s / 60) + "m" : s + "s";
	}

	private static void draw(GuiGraphics g, DeltaTracker dt) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || mc.options.hideGui || mc.player.isSpectator()) return;
		List<Object[]> on = Trades.running(mc.player);
		if (on.isEmpty()) return;
		// right to left from beside the off-hand slot
		int right = g.guiWidth() / 2 - 91 - 34, y = g.guiHeight() - 23;
		boolean tab = mc.options.keyPlayerList.isDown();
		g.pose().pushPose();
		g.pose().translate(0, 0, 150);
		int lineY = y - 14;
		for (int i = 0; i < on.size(); i++) {
			Trades.Good gd = (Trades.Good) on.get(i)[0];
			long left = (Long) on.get(i)[1];
			double k = (Double) on.get(i)[2];
			int x = right - (i + 1) * TILE;
			g.fill(x - 1, y - 1, x + 21, y + 21, 0xFF050404);
			g.fill(x, y, x + 20, y + 20, left < 600 ? 0xFF6A2A1A : 0xFF3D3833);
			g.fill(x + 1, y + 1, x + 19, y + 19, 0xFF16120F);
			ItemStack s = icon(gd);
			if (!s.isEmpty()) g.renderItem(s, x + 2, y + 2);
			String t = clock(left);
			g.pose().pushPose();
			g.pose().translate(0, 0, 200);
			g.pose().scale(0.75f, 0.75f, 1);
			g.drawString(mc.font, t, Math.round((x + 20) / 0.75f) - mc.font.width(t), Math.round((y + 14) / 0.75f), left < 600 ? 0xFFFF9A6A : 0xFFECE4D6, true);
			g.pose().popPose();
			if (tab) {
				// what it does, one line, above the sockets (rightmost buff lowest)
				String text = gd.name() + ": " + String.join(", ", Trades.lines(gd, k));
				g.drawString(mc.font, text, right - mc.font.width(text), lineY, 0xFFB8D8FF, true);
				lineY -= 10;
			}
		}
		g.pose().popPose();
	}
}
