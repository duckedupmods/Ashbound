package com.snoringwalrus.ashbound.client;

import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Classes;
import com.snoringwalrus.ashbound.Forms;
import com.snoringwalrus.ashbound.Levels;
import com.snoringwalrus.ashbound.Skills;

import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;

/** The four skill keys, left of the hotbar, in iron sockets like the relic's: the first is what's in your hand. */
final class SkillHud {
	private SkillHud() {}

	private static final int SIZE = 22, GAP = 2, OFF_HOTBAR = 8;

	static void hooks(IEventBus bus) {
		bus.addListener((RegisterGuiLayersEvent e) -> e.registerAbove(VanillaGuiLayers.HOTBAR,
				ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "skills"), SkillHud::draw));
	}

	private static final ResourceLocation ICONS = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/gui/skill_icons.png");
	private static final int ICON = 16, COLUMNS = 6, ROWS = 9;

	/** A skill's picture at this spot (tools/skill_items.py). */
	static void icon(GuiGraphics g, Skills.Skill s, int x, int y) {
		int i = Skills.ALL.indexOf(s);
		g.blit(ICONS, x, y, (i % COLUMNS) * ICON, (i / COLUMNS) * ICON, ICON, ICON, COLUMNS * ICON, ROWS * ICON);
	}

	/** What the first key does, and the cooldown it runs on, or null. */
	static String held(Minecraft mc) {
		return SkillScreen.heldName(mc.player.getMainHandItem());
	}

	private static void draw(GuiGraphics g, DeltaTracker dt) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || mc.options.hideGui || mc.player.isSpectator()) return;
		var font = mc.font;
		long now = System.currentTimeMillis();
		int y = g.guiHeight() - SIZE - 1, x0 = g.guiWidth() / 2 - 91 - OFF_HOTBAR - Skills.SLOTS * (SIZE + GAP) + GAP;
		for (int i = 0; i < Skills.SLOTS; i++) {
			int x = x0 + i * (SIZE + GAP);
			g.fill(x - 1, y - 1, x + SIZE + 1, y + SIZE + 1, 0xFF050404);
			g.fill(x, y, x + SIZE, y + SIZE, 0xFF3D3833);
			g.fill(x + 1, y + 1, x + SIZE - 1, y + SIZE - 1, 0xFF16120F);
			if (i == Skills.SLOTS - 1 && !Forms.clientForm.isEmpty()) {   // what the Tome took
				g.fill(x + 4, y + 10, x + SIZE - 4, y + 12, 0xFF6A2018);
				continue;
			}
			String cool = null;
			if (i == 0) {
				String name = held(mc);
				if (name != null) {
					g.renderItem(mc.player.getMainHandItem(), x + 3, y + 3);
					cool = "held";
				}
			} else {
				var s = Skills.byId(Skills.clientBar[i] == null ? "" : Skills.clientBar[i]);
				if (s != null) {
					icon(g, s, x + 3, y + 3);
					cool = s.id();
				}
			}
			g.pose().pushPose();
			g.pose().translate(0, 0, 200);
			long[] c = cool == null ? null : Skills.clientCooling.get(cool);
			if (c != null && c[0] > now) {
				int h = Math.round((SIZE - 2) * (c[0] - now) / (float) c[1]);
				g.fill(x + 1, y + SIZE - 1 - h, x + SIZE - 1, y + SIZE - 1, 0xB0050404);
				String secs = String.valueOf((int) Math.ceil((c[0] - now) / 1000.0));
				g.drawString(font, secs, x + SIZE / 2 - font.width(secs) / 2, y + 7, AshUi.TEXT, true);
			}
			String key = CurioKeys.slotKey(i).getTranslatedKeyMessage().getString();
			g.pose().scale(0.75f, 0.75f, 1);
			g.drawString(font, key, Math.round((x + SIZE - 1) / 0.75f) - font.width(key), Math.round((y + SIZE - 7) / 0.75f), AshUi.MUTED, true);
			g.pose().popPose();
		}
		if (!Classes.client.isEmpty() && Skills.pending(Levels.clientLevel, Skills.clientPicks) >= 0) {
			String t = "New skill: " + CurioKeys.SKILLS.getTranslatedKeyMessage().getString();
			g.drawString(font, t, x0 + (Skills.SLOTS * (SIZE + GAP) - font.width(t)) / 2, y - 11, AshUi.EMBER_LT, true);
		}
	}
}
