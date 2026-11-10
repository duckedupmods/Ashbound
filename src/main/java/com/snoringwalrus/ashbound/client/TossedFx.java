package com.snoringwalrus.ashbound.client;

import net.minecraft.client.Minecraft;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.world.entity.item.ItemEntity;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.common.NeoForge;
import org.joml.Vector3f;

/**
 * A thread of light standing over gear that's been thrown down (Dropped), in the colour of whoever threw it. The outline alone isn't
 * enough: a shader pack can leave outlines out, and this shows either way.
 */
public final class TossedFx {
	private TossedFx() {}

	private static final int EVERY = 3, RANGE = 48, MOTES = 3;
	private static final double HIGH = 2.6, WIDE = 0.08;
	private static final float SIZE = 0.9f;

	/** The thrower's colour, which comes on the name over it; its rarity's if nobody threw it. */
	public static int colour(ItemEntity it) {
		var name = it.getCustomName();
		var thrower = name == null ? null : name.getStyle().getColor();
		return thrower != null ? 0xFF000000 | thrower.getValue() : AshUi.edge(it.getItem());
	}

	public static void hooks() {
		NeoForge.EVENT_BUS.addListener((ClientTickEvent.Post e) -> tick());
	}

	private static void tick() {
		Minecraft mc = Minecraft.getInstance();
		if (mc.level == null || mc.player == null || mc.isPaused() || mc.level.getGameTime() % EVERY != 0) return;
		for (ItemEntity it : mc.level.getEntitiesOfClass(ItemEntity.class, mc.player.getBoundingBox().inflate(RANGE), ItemEntity::isCurrentlyGlowing)) {
			int c = colour(it);
			var dust = new DustParticleOptions(new Vector3f((c >> 16 & 255) / 255f, (c >> 8 & 255) / 255f, (c & 255) / 255f), SIZE);
			for (int i = 0; i < MOTES; i++) {
				var r = mc.level.random;
				mc.level.addParticle(dust, it.getX() + (r.nextDouble() - 0.5) * WIDE, it.getY() + 0.2 + r.nextDouble() * HIGH, it.getZ() + (r.nextDouble() - 0.5) * WIDE, 0, 0.01, 0);
			}
		}
	}
}
