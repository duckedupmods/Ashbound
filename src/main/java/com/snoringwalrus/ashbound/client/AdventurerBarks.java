package com.snoringwalrus.ashbound.client;

import java.util.List;

import com.mojang.blaze3d.vertex.PoseStack;
import com.snoringwalrus.ashbound.Adventurer;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.network.chat.FormattedText;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.client.event.RenderLevelStageEvent;
import net.neoforged.neoforge.common.NeoForge;

/** An adventurer's line over their head (Adventurer.bark): plain text on a dark band, facing you, up four seconds and fading out. */
public final class AdventurerBarks {
	private AdventurerBarks() {}

	private static final long UP = 3300, FADE = 700;
	private static final int WIDE = 150;
	private static final double SEEN = 20;

	public static void hooks() {
		NeoForge.EVENT_BUS.addListener(AdventurerBarks::draw);
	}

	private static void draw(RenderLevelStageEvent e) {
		if (e.getStage() != RenderLevelStageEvent.Stage.AFTER_ENTITIES) return;
		Minecraft mc = Minecraft.getInstance();
		if (mc.level == null || mc.player == null || mc.options.hideGui) return;
		long now = System.currentTimeMillis();
		List<Adventurer> near = mc.level.getEntitiesOfClass(Adventurer.class, mc.player.getBoundingBox().inflate(SEEN), a -> !a.bark().isEmpty() && now - a.barkSince < UP + FADE);
		if (near.isEmpty()) return;
		Font font = mc.font;
		MultiBufferSource.BufferSource buf = mc.renderBuffers().bufferSource();
		PoseStack ps = e.getPoseStack();
		Vec3 cam = e.getCamera().getPosition();
		float pt = e.getPartialTick().getGameTimeDeltaPartialTick(false);
		for (Adventurer a : near) {
			long age = now - a.barkSince;
			float alpha = age < UP ? 1 : 1 - (age - UP) / (float) FADE;
			// in quickly, out slowly
			float in = Mth.clamp(age / 120f, 0, 1);
			List<FormattedCharSequence> lines = font.split(FormattedText.of(a.bark()), WIDE);
			Vec3 at = a.getPosition(pt).add(0, a.getBbHeight() + 0.55 + 0.1 * in, 0);
			ps.pushPose();
			ps.translate(at.x - cam.x, at.y - cam.y, at.z - cam.z);
			ps.mulPose(e.getCamera().rotation());
			ps.scale(0.025f, -0.025f, 0.025f);
			var m = ps.last().pose();
			int text = (int) (alpha * 255) << 24 | 0xF2EEE4, band = (int) (alpha * 150) << 24 | 0x15120F;
			int y = -lines.size() * 10;
			for (FormattedCharSequence l : lines) {
				float x = -font.width(l) / 2f;
				font.drawInBatch(l, x, y, text, false, m, buf, Font.DisplayMode.NORMAL, band, 0xF000F0);
				y += 10;
			}
			ps.popPose();
		}
		buf.endBatch();
	}
}
