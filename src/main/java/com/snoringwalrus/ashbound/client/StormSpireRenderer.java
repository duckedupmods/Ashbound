package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

import com.mojang.blaze3d.vertex.PoseStack;
import com.snoringwalrus.ashbound.GateDungeons;
import com.snoringwalrus.ashbound.GateEntity;
import com.snoringwalrus.ashbound.SkyCrack;
import com.snoringwalrus.ashbound.StormSpire;

import net.minecraft.client.Camera;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.block.BlockRenderDispatcher;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/**
 * A storm spire (StormSpire, tools/blender/gate_storm.py's look): a jagged leaning pillar of the storm's dungeon's own
 * blocks, wider at the foot, its top torn into chunks hanging round a white-hot core; the storm's lightning feeds the core
 * now and then. It bursts up out of the ground over its first RISE ticks, and flashes red when struck.
 */
public class StormSpireRenderer extends EntityRenderer<StormSpire> {
	private static final ResourceLocation NONE = ResourceLocation.withDefaultNamespace("textures/misc/white.png");
	private static final BlockState[] FALLBACK = {Blocks.DEEPSLATE_BRICKS.defaultBlockState(), Blocks.POLISHED_BLACKSTONE_BRICKS.defaultBlockState(),
			Blocks.CRACKED_DEEPSLATE_BRICKS.defaultBlockState()};
	/** its blocks, worked out once per shape: x, y, z (cell corners, y from the ground), which of the palette, lit or not */
	private static final Map<Long, List<float[]>> SHAPES = new HashMap<>();

	public StormSpireRenderer(EntityRendererProvider.Context ctx) {
		super(ctx);
		shadowRadius = 0;
	}

	@Override
	public ResourceLocation getTextureLocation(StormSpire s) {
		return NONE;
	}

	private static float hash(long seed, int i) {
		return StormStrikeRenderer.hash(seed, i);
	}

	/** The pillar: rings of blocks round a wandering, leaning middle, hollow inside, then chunks round the top. */
	static List<float[]> shape(int seed, float tall) {
		int h = Math.max(6, Math.round(tall));
		long key = (long) seed << 8 | h;
		List<float[]> have = SHAPES.get(key);
		if (have != null) return have;
		if (SHAPES.size() > 64) SHAPES.clear();
		List<float[]> out = new ArrayList<>();
		float lx = (hash(seed, 1) - 0.5f) * 0.24f, lz = (hash(seed, 2) - 0.5f) * 0.24f;
		float cx = 0, cz = 0;
		int n = 0;
		for (int y = 0; y < h; y++) {
			float t = y / (float) h;
			float rad = 2.5f * (float) Math.pow(1 - t, 0.8) + 0.6f;
			cx = lx * y + Mth.sin(y * 0.5f + seed) * 0.6f;
			cz = lz * y + Mth.cos(y * 0.4f + seed) * 0.6f;
			int ix0 = Math.round(cx), iz0 = Math.round(cz);
			for (int dx = -4; dx <= 4; dx++)
				for (int dz = -4; dz <= 4; dz++) {
					float d = Mth.sqrt((dx + ix0 - cx) * (dx + ix0 - cx) + (dz + iz0 - cz) * (dz + iz0 - cz));
					float edge = rad + (hash(seed, 1000 + n++) - 0.6f);
					if (d >= edge || d < edge - 1.6f && y > 0) continue;
					int which = (int) (hash(seed, 3000 + n) * 3);
					boolean lit = t > 0.55f && hash(seed, 5000 + n) < 0.18f;
					out.add(new float[] {ix0 + dx - 0.5f, y, iz0 + dz - 0.5f, which, lit ? 1 : 0, 1});
				}
		}
		// torn chunks hanging round the top
		for (int k = 0; k < 12; k++) {
			float a = hash(seed, 7000 + k) * Mth.TWO_PI, r = 1.8f + hash(seed, 7100 + k) * 2.6f, s = hash(seed, 7200 + k) < 0.4f ? 0.5f : 1f;
			out.add(new float[] {cx + Mth.cos(a) * r - s / 2, h - 2 + hash(seed, 7300 + k) * 6, cz + Mth.sin(a) * r - s / 2, (int) (hash(seed, 7400 + k) * 3),
					hash(seed, 7500 + k) < 0.4f ? 1 : 0, s});
		}
		// where the core burns
		out.add(new float[] {cx, h + 1.5f, cz, -1, 0, 0});
		SHAPES.put(key, out);
		return out;
	}

	private static BlockState[] palette(StormSpire e) {
		SkyCrack s = e.storm();
		if (s == null) return FALLBACK;
		List<BlockState> solid = new ArrayList<>();
		for (BlockState b : GateDungeons.of(s).debris()) if (b.isSolid() && b.getLightEmission() == 0 && solid.size() < 3) solid.add(b);
		if (solid.isEmpty()) return FALLBACK;
		while (solid.size() < 3) solid.add(solid.get(solid.size() % solid.size()));
		return solid.toArray(new BlockState[0]);
	}

	@Override
	public void render(StormSpire e, float yaw, float partial, PoseStack pose, MultiBufferSource buffers, int light) {
		float t = e.tickCount + partial;
		float rise = Mth.clamp(t / StormSpire.RISE, 0, 1);
		rise = 1 - (1 - rise) * (1 - rise) * (1 - rise);
		List<float[]> cells = shape(e.seed(), e.tall());
		float tall = Math.max(6, Math.round(e.tall()));
		BlockState[] pal = palette(e);
		BlockRenderDispatcher br = Minecraft.getInstance().getBlockRenderer();
		boolean hit = System.currentTimeMillis() - e.struck < 220;
		int overlay = hit ? OverlayTexture.pack(0, true) : OverlayTexture.NO_OVERLAY;
		float shake = rise < 1 ? (hash(e.seed(), (int) t) - 0.5f) * 0.3f : 0;
		float sink = -(tall + 2) * (1 - rise);
		float[] core = null;

		pose.pushPose();
		pose.translate(shake, sink, -shake);
		for (float[] c : cells) {
			if (c[3] < 0) {
				core = c;
				continue;
			}
			pose.pushPose();
			pose.translate(c[0], c[1], c[2]);
			if (c[5] != 1) pose.scale(c[5], c[5], c[5]);
			br.renderSingleBlock(pal[(int) c[3] % pal.length], pose, buffers, c[4] > 0 ? LightTexture.FULL_BRIGHT : light, overlay);
			pose.popPose();
		}

		// the core, white-hot in the gate's colour, and the lightning feeding it
		SkyCrack s = e.storm();
		int col = GateEntity.COLOUR[s == null ? 5 : Mth.clamp(s.rank(), 0, GateEntity.COLOUR.length - 1)];
		float r = (col >> 16 & 255) / 255f, g = (col >> 8 & 255) / 255f, b = (col & 255) / 255f;
		Camera cam = Minecraft.getInstance().gameRenderer.getMainCamera();
		Vector3f eye = new Vector3f((float) (cam.getPosition().x - e.getX() - shake), (float) (cam.getPosition().y - e.getY() - sink),
				(float) (cam.getPosition().z - e.getZ() + shake));
		GateRenderer.Glow gl = new GateRenderer.Glow(buffers.getBuffer(GateRenderer.Types.GLOW), new Matrix4f(pose.last().pose()), eye, cam.rotation(),
				new Quaternionf());
		if (core != null) {
			float pulse = 0.8f + 0.2f * Mth.sin(t * 0.2f), bright = (1 - e.broken() * 0.5f) * rise;
			gl.spot(core[0], core[1], core[2], 4.5f * pulse, r, g, b, 0.55f * bright, 0);
			gl.spot(core[0], core[1], core[2], 1.6f * pulse, Math.min(1, r * 0.3f + 0.75f), Math.min(1, g * 0.3f + 0.75f), Math.min(1, b * 0.3f + 0.75f),
					(hit ? 1f : 0.9f) * bright, 0);
			// fed: a bolt out of the cloud every second or so, lasting a few ticks
			int beat = (int) (t / 23), in = (int) t - beat * 23;
			if (rise >= 1 && in < 4 && hash(e.seed(), 9000 + beat) < 0.7f) {
				float top = s == null ? 30 : (float) (s.getY() + GateEntity.MID - SkyCrack.DECK + 2 - e.getY()) - core[1];
				pose.pushPose();
				pose.translate(core[0], core[1], core[2]);
				Vector3f eye2 = new Vector3f(eye).sub(core[0], core[1], core[2]);
				GateRenderer.Glow g2 = new GateRenderer.Glow(buffers.getBuffer(GateRenderer.Types.GLOW), new Matrix4f(pose.last().pose()), eye2, cam.rotation(),
						new Quaternionf());
				StormStrikeRenderer.bolt(g2, e.seed() * 31L + beat, Math.max(8, top), r, g, b, in == 2 ? 0.3f : 0.85f);
				pose.popPose();
			}
		}
		pose.popPose();
	}

	@Override
	public boolean shouldRender(StormSpire e, Frustum f, double x, double y, double z) {
		return true;
	}
}
