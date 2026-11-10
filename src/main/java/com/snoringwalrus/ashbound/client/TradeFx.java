package com.snoringwalrus.ashbound.client;

import com.snoringwalrus.ashbound.Trades;

import net.minecraft.client.Minecraft;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.ViewportEvent;
import net.neoforged.neoforge.common.NeoForge;

/** What too many brews do to your view: a slow, mild sway when tipsy, a bit more when drunk, and no running while drunk. */
public final class TradeFx {
	private TradeFx() {}

	/** Eased in and out so it never snaps; degrees of roll at full. */
	private static float sway;

	static void hooks() {
		NeoForge.EVENT_BUS.addListener((ClientTickEvent.Post e) -> {
			var p = Minecraft.getInstance().player;
			int tipsy = p == null ? 0 : Trades.tipsy(p);
			float want = tipsy == 0 ? 0 : tipsy == 1 ? 1.2f : 3f;
			sway += (want - sway) * 0.02f;
			if (tipsy > 1 && p.isSprinting()) p.setSprinting(false);
		});
		NeoForge.EVENT_BUS.addListener((ViewportEvent.ComputeCameraAngles e) -> {
			if (sway < 0.02f) return;
			double t = System.nanoTime() * 1e-9;
			e.setRoll(e.getRoll() + (float) Math.sin(t * 0.9) * sway);
			e.setYaw(e.getYaw() + (float) Math.sin(t * 0.55 + 1) * sway * 0.35f);
		});
	}
}
