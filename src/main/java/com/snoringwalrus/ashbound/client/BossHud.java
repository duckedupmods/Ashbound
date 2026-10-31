package com.snoringwalrus.ashbound.client;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.LerpingBossEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.minecraft.world.BossEvent;
import net.neoforged.neoforge.client.event.CustomizeGuiOverlayEvent;
import net.neoforged.neoforge.common.NeoForge;

/**
 * Boss bars in the same iron as the rest: the name between two ember rules, then a long pointed blade under it, a pale
 * chunk draining where a hit landed, a flash on the hit and a slow gleam along it. Its colour is the server's, so a
 * boss's phases still show; elites get a shorter, thinner one. The name sits under the given y, where vanilla's sits
 * above it, so a list of them clears the compass: see QuestHud.ROOM.
 */
final class BossHud {
	private BossHud() {}

	private static final int WIDE = 250, SHORT = 150, TALL = 8, THIN = 5, NAME = 11, AFTER = 10, TIP = 5, RULE = 54, GLEAM = 26, GLEAM_SPEED = 12;
	private static final float FLASH_MS = 180;
	private static final Map<UUID, VitalsHud.Bar> BARS = new HashMap<>();
	private static long last;

	static void hooks() {
		NeoForge.EVENT_BUS.addListener((CustomizeGuiOverlayEvent.BossEventProgress e) -> {
			e.setCanceled(true);
			LerpingBossEvent b = e.getBossEvent();
			boolean boss = b.getOverlay() == BossEvent.BossBarOverlay.NOTCHED_10 || b.getOverlay() == BossEvent.BossBarOverlay.PROGRESS;
			draw(e.getGuiGraphics(), b, e.getY(), boss ? WIDE : SHORT, boss ? TALL : THIN);
			e.setIncrement(NAME + (boss ? TALL : THIN) + AFTER);
		});
	}

	private static int[] colours(BossEvent.BossBarColor c) {
		return switch (c) {
			case PURPLE -> new int[] {0xFFA850E8, 0xFF3E1478, 0xFFE0B8FF};
			case WHITE -> new int[] {0xFFECE4D6, 0xFF8A8076, 0xFFFFFFFF};
			case YELLOW -> new int[] {0xFFE8B83A, 0xFF7A5210, 0xFFFFE8A0};
			case BLUE -> new int[] {0xFF5AA0FF, 0xFF1E3E9A, 0xFFB8DCFF};
			case GREEN -> new int[] {0xFF8EC83A, 0xFF3A6018, 0xFFD4E88A};
			case PINK -> new int[] {0xFFE85AA8, 0xFF7A1450, 0xFFFFB8DC};
			default -> new int[] {0xFFE0442C, 0xFF7A1410, 0xFFFF9A7A};
		};
	}

	private static int notches(BossEvent.BossBarOverlay o) {
		return switch (o) {
			case NOTCHED_6 -> 6;
			case NOTCHED_10 -> 10;
			case NOTCHED_12 -> 12;
			case NOTCHED_20 -> 20;
			default -> 1;
		};
	}

	private static void draw(GuiGraphics g, LerpingBossEvent b, int y, int w, int h) {
		var font = Minecraft.getInstance().font;
		long now = System.currentTimeMillis();
		float step = Math.min(0.1f, (now - last) / 1000f), f = Mth.clamp(b.getProgress(), 0, 1);
		last = now;
		if (BARS.size() > 32) BARS.clear();
		VitalsHud.Bar bar = BARS.computeIfAbsent(b.getId(), id -> new VitalsHud.Bar(f));
		bar.step(f, step, now);

		int cx = g.guiWidth() / 2, x = cx - w / 2, half = font.width(b.getName()) / 2;
		Component name = b.getName();
		g.drawString(font, name, cx - half, y, AshUi.TEXT, true);
		AshUi.rule(g, cx - half - 8 - RULE, cx - half - 8, y + 4, false);
		AshUi.rule(g, cx + half + 8, cx + half + 8 + RULE, y + 4, true);

		int by = y + NAME, fw = Math.round(w * Mth.clamp(bar.shown, 0, 1)), tw = Math.round(w * Mth.clamp(bar.trail, 0, 1));
		int[] c = colours(b.getColor());
		VitalsHud.frame(g, x, by, w, h);
		g.fill(x, by, x + w, by + h, 0xFF160C0A);
		VitalsHud.tip(g, x - 2, by, h, true, TIP);
		VitalsHud.tip(g, x + w + 2, by, h, false, TIP);
		if (tw > fw) g.fill(x + fw, by, x + tw, by + h, 0xFFE8C8A0);
		if (fw > 0) {
			g.fillGradient(x, by, x + fw, by + h, c[0], c[1]);
			g.fill(x, by, x + fw, by + 1, c[2]);
			g.fill(x + fw - 1, by, x + fw, by + h, c[2]);
			int at = (int) (now / GLEAM_SPEED % (w + GLEAM * 2)) - GLEAM, from = Math.max(0, at), to = Math.min(fw, at + GLEAM);
			if (to > from) g.fill(x + from, by + 1, x + to, by + h, 0x28FFFFFF);
			float hit = 1 - Mth.clamp((now - bar.hitAt()) / FLASH_MS, 0, 1);
			if (hit > 0) g.fill(x, by, x + fw, by + h, Math.round(hit * 0x90) << 24 | 0xFFFFFF);
		}
		int n = notches(b.getOverlay());
		for (int i = 1; i < n; i++) g.fill(x + w * i / n, by + h / 2, x + w * i / n + 1, by + h, 0xA0050404);
	}
}
