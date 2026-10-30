package com.snoringwalrus.ashbound.client;

import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.CurioFx;
import com.snoringwalrus.ashbound.Curios;
import com.snoringwalrus.ashbound.Net;

import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;
import top.theillusivec4.curios.api.CuriosApi;

/**
 * The worn relic, right of the hotbar: its model in an iron socket, its power tier above it (I, II, III), the key it
 * answers to, and a dark sweep draining away while its power comes back.
 */
public final class RelicHud {
	private RelicHud() {}

	public static void hooks(IEventBus bus) {
		bus.addListener((RegisterGuiLayersEvent e) -> e.registerAbove(VanillaGuiLayers.HOTBAR,
				ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "relic"), RelicHud::draw));
	}

	private static ItemStack relic(Minecraft mc) {
		return CuriosApi.getCuriosInventory(mc.player).flatMap(inv -> inv.getStacksHandler("relic"))
				.map(h -> h.getStacks().getSlots() > 0 ? h.getStacks().getStackInSlot(0) : ItemStack.EMPTY).orElse(ItemStack.EMPTY);
	}

	private static void draw(GuiGraphics g, DeltaTracker dt) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || mc.options.hideGui || mc.player.isSpectator()) return;
		ItemStack s = relic(mc);
		if (s.isEmpty() || !(s.getItem() instanceof Curios.Curio c)) return;
		int x = g.guiWidth() / 2 + 91 + 8, y = g.guiHeight() - 23;
		// the socket: blackened iron, an ember rim while the power is ready
		long now = System.currentTimeMillis();
		float left = Net.relicCdTotal > 0 ? Math.max(0, (Net.relicCdEnd - now) / (float) Net.relicCdTotal) : 0;
		boolean keyed = c.spec().effect().startsWith("[V]");
		g.fill(x - 1, y - 1, x + 23, y + 23, 0xFF050404);
		g.fill(x, y, x + 22, y + 22, 0xFF3D3833);
		g.fill(x + 1, y + 1, x + 21, y + 21, 0xFF16120F);
		if (keyed && left == 0) {
			int pulse = (int) (0x50 + 0x30 * Math.sin(now / 300.0));
			g.fill(x, y, x + 22, y + 1, pulse << 24 | 0xE8742C);
			g.fill(x, y + 21, x + 22, y + 22, pulse << 24 | 0xE8742C);
		}
		g.renderItem(s, x + 3, y + 3);
		// cooling down: the dark drains from the top as it comes back, the seconds in the middle
		if (left > 0) {
			int h = Math.round(20 * left);
			g.pose().pushPose();
			g.pose().translate(0, 0, 200);
			g.fill(x + 1, y + 21 - h, x + 21, y + 21, 0xB0050404);
			String secs = String.valueOf((int) Math.ceil((Net.relicCdEnd - now) / 1000.0));
			g.drawString(mc.font, secs, x + 11 - mc.font.width(secs) / 2, y + 7, 0xFFECE4D6, true);
			g.pose().popPose();
		}
		// its tier above, the key below
		g.pose().pushPose();
		g.pose().translate(0, 0, 200);
		String tier = CurioFx.roman(CurioFx.tier(s));
		g.drawString(mc.font, tier, x + 11 - mc.font.width(tier) / 2, y - 10, 0xFFF0A050, true);
		if (keyed) {
			String key = CurioKeys.POWER.getTranslatedKeyMessage().getString();
			g.pose().scale(0.75f, 0.75f, 1);
			g.drawString(mc.font, key, Math.round((x + 21) / 0.75f) - mc.font.width(key), Math.round((y + 15) / 0.75f), 0xFF9A9086, true);
		}
		g.pose().popPose();
	}
}
