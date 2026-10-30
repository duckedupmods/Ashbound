package com.snoringwalrus.ashbound.client;

import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;
import org.lwjgl.opengl.GL11;
import org.lwjgl.opengl.GL30;

import com.mojang.blaze3d.pipeline.RenderTarget;
import com.mojang.blaze3d.pipeline.TextureTarget;
import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.mojang.math.Axis;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.GateDungeons;
import com.snoringwalrus.ashbound.GateEntity;

import net.minecraft.client.Camera;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.AbstractTexture;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.util.Mth;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * How a gate looks (GateEntity has its timeline; tools/blender/gate_rift.py is the look it copies): a crack in the
 * world. In its own frame: x across its face, y up, z through it, its middle at the origin. Drawn in this order:
 *  - torn debris: chunks of the dungeon behind it (GateDungeons), ripped through, hanging and turning round it;
 *  - the tear (gate_rift.fsh): its dark inside (writes depth, so what's behind it stays hidden), then its lips
 *    burning white-hot into the rank colour; the shape is one of GateRift's, read from a distance field;
 *  - shards of the world knocked loose round it, each showing what's behind it a little out of place
 *    (gate_shard.fsh, from a copy of the frame so far);
 *  - added light: fracture lines running off the lips, lightning, the flash with its lens streak, the shockwave
 *    ring on the ground (gate_glow.fsh).
 */
public class GateRenderer extends EntityRenderer<GateEntity> {
	private static final ResourceLocation NONE = ResourceLocation.withDefaultNamespace("textures/misc/white.png");
	private static final ResourceLocation WARP = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "gate_warp");
	private static final ResourceLocation RIFT = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/misc/gate_rift.png");
	/** How far the tear's quad reaches past its lips, so the halo has room to fade to nothing. */
	private static final float REACH = 1.8f;

	static final class Types extends RenderType {
		private Types() {
			super(null, null, null, 0, false, false, null, null);
		}

		/** Premultiplied: rgb is added, alpha is how much of what's behind is covered. */
		private static final TransparencyStateShard PREMUL = new TransparencyStateShard(Ashbound.ID + "_premul", () -> {
			RenderSystem.enableBlend();
			RenderSystem.blendFuncSeparate(GlStateManager.SourceFactor.ONE, GlStateManager.DestFactor.ONE_MINUS_SRC_ALPHA,
					GlStateManager.SourceFactor.ONE, GlStateManager.DestFactor.ONE_MINUS_SRC_ALPHA);
		}, () -> {
			RenderSystem.disableBlend();
			RenderSystem.defaultBlendFunc();
		});

		private static RenderType make(String name, ShaderStateShard shader, EmptyTextureStateShard tex, WriteMaskStateShard mask, int size) {
			return create(Ashbound.ID + "_" + name, DefaultVertexFormat.POSITION_COLOR_TEX_LIGHTMAP, VertexFormat.Mode.QUADS, size, false, false,
					CompositeState.builder().setShaderState(shader).setTextureState(tex).setTransparencyState(PREMUL).setCullState(NO_CULL)
							.setWriteMaskState(mask).setDepthTestState(LEQUAL_DEPTH_TEST).createCompositeState(false));
		}

		/** The distance fields, read smooth (blurred = linear filtering), never mipmapped. */
		private static final TextureStateShard FIELD = new TextureStateShard(RIFT, true, false);
		static final RenderType VOID = make("gate_void", new ShaderStateShard(() -> GateShaders.rift), FIELD, COLOR_DEPTH_WRITE, 256);
		static final RenderType LIPS = make("gate_lips", new ShaderStateShard(() -> GateShaders.rift), FIELD, COLOR_WRITE, 256);
		static final RenderType GLOW = make("gate_glow", new ShaderStateShard(() -> GateShaders.glow), NO_TEXTURE, COLOR_WRITE, 1 << 15);
		static final RenderType SHARD = make("gate_shard", new ShaderStateShard(() -> GateShaders.shard), new TextureStateShard(WARP, false, false),
				COLOR_WRITE, 1024);
	}

	public GateRenderer(EntityRendererProvider.Context ctx) {
		super(ctx);
		shadowRadius = 0;
	}

	@Override
	public ResourceLocation getTextureLocation(GateEntity g) {
		return NONE;
	}

	@Override
	public boolean shouldRender(GateEntity g, Frustum frustum, double x, double y, double z) {
		return g.shouldRender(x, y, z) && frustum.isVisible(g.getBoundingBoxForCulling());
	}

	// ---------------------------------------------------------------- the timeline, frame by frame

	/** Where it is in its life this frame. */
	static final class State {
		float t, crack = -1, sx, sy, hot = 1, live, push = 1, lift = 1, flash, wave = -1, waveR, tear;
		boolean open, earth = true;
	}

	private static float clamp01(float x) {
		return Mth.clamp(x, 0, 1);
	}

	private static float easeOutBack(float k) {
		float c = 1.9f;
		return 1 + (c + 1) * (k - 1) * (k - 1) * (k - 1) + c * (k - 1) * (k - 1);
	}

	static State state(GateEntity g, float partial) {
		State s = new State();
		long now = g.level().getGameTime();
		float a = now - g.opened() + partial;
		s.t = (now % 100000) + partial;
		if (a < GateEntity.CRACK) {
			// a hairline of light tears down the air, cracks running off it; the ground starts to lift
			s.crack = Math.max(0, a / GateEntity.CRACK);
			s.sx = 0.035f;
			s.sy = 0.75f * Mth.sqrt(s.crack);
			s.hot = 1.6f;
			s.live = 0.4f + 0.6f * s.crack;
			s.lift = s.crack * 0.6f;
			s.push = 0.55f;
		} else {
			// it bursts: a flash and a streak, a shockwave over the ground, the earth flung out, then it settles
			float b = a - GateEntity.CRACK, k = clamp01(b / GateEntity.OPEN);
			s.sx = Mth.lerp(easeOutBack(k), 0.035f, 1);
			s.sy = Mth.lerp(1 - (1 - k) * (1 - k), 0.75f, 1);
			s.hot = Mth.lerp(k, 1.8f, 1);
			s.live = 1;
			s.flash = Math.max(0, 1 - b / 10);
			if (b < 30) {
				s.wave = b;
				s.waveR = 8;
			}
			s.push = b < 4 ? Mth.lerp(b / 4, 0.55f, 1.5f) : 1 + 0.5f * Math.max(0, 1 - (b - 4) / 40);
		}
		if (g.closing()) {
			// it burns hotter, drags the debris in, its lips pull together and seal, then it bangs
			float c = now - g.closed() + partial;
			s.flash = 0;
			s.wave = -1;
			s.hot = 1 + clamp01(c / 40) * 1.5f;
			s.push = Math.max(0.3f, 1 - c / 40 * 0.7f);
			s.tear = clamp01((c - 14) / 10);
			if (c < 18) s.sx = 1;
			else if (c < GateEntity.SHUT) s.sx = 1 - 0.9f * (float) Math.pow((c - 18) / (GateEntity.SHUT - 18), 2);
			else s.sx = Mth.lerp(clamp01((c - GateEntity.SHUT) / (GateEntity.BANG - GateEntity.SHUT)), 0.1f, 0.02f);
			s.sy = c < GateEntity.SHUT ? 1 - 0.05f * clamp01((c - 18) / 26) : Mth.lerp(clamp01((c - GateEntity.SHUT) / (GateEntity.BANG - GateEntity.SHUT)), 0.95f, 0.04f);
			if (c >= GateEntity.BANG) {
				float w = c - GateEntity.BANG;
				s.sx = s.sy = 0;
				s.earth = false;
				s.tear = 0;
				s.flash = Math.max(0, 1 - w / 12) * 1.4f;
				if (w < 34) {
					s.wave = w;
					s.waveR = 12;
				}
				s.live = Math.max(0, 1 - w / 40);
			}
		}
		s.open = s.sx > 0.004f && s.sy > 0.004f;
		return s;
	}

	// ---------------------------------------------------------------- drawing

	@Override
	public void render(GateEntity g, float yaw, float partial, PoseStack pose, MultiBufferSource buffers, int light) {
		State s = state(g, partial);
		int c = GateEntity.COLOUR[g.rank()];
		float r = (c >> 16 & 255) / 255f, gr = (c >> 8 & 255) / 255f, b = (c & 255) / 255f;
		boolean dark = GateEntity.dark(g.rank());
		long seed = g.getUUID().getLeastSignificantBits();
		int seedCode = (int) Math.floorMod(seed, 60);

		Camera camera = Minecraft.getInstance().gameRenderer.getMainCamera();
		Vec3 me = g.getPosition(partial);
		Vector3f eye = new Vector3f((float) (camera.getPosition().x - me.x), (float) (camera.getPosition().y - me.y - GateEntity.MID),
				(float) (camera.getPosition().z - me.z));
		Quaternionf face = Axis.YP.rotationDegrees(-g.getYRot());

		pose.pushPose();
		pose.translate(0, GateEntity.MID, 0);
		Matrix4f world = new Matrix4f(pose.last().pose());
		pose.mulPose(face);
		Matrix4f local = new Matrix4f(pose.last().pose());

		if (s.earth && (s.open || s.crack >= 0)) earth(pose, buffers, s, seed, light, GateDungeons.of(g).debris());

		int shape = (int) Math.floorMod(seed >>> 9, GateRift.SHAPES.length);
		float[] lip = GateRift.SHAPES[shape];
		if (s.open) {
			int flags = (dark ? 1 : 0) + 2 * Mth.clamp(Math.round(s.hot * 10), 0, 31) + 64 * Mth.clamp(Math.round(s.sx * 255), 1, 255);
			int code = 8 * (shape + 4 * seedCode);
			tear(buffers.getBuffer(Types.VOID), local, s, r, gr, b, code, flags);
			tear(buffers.getBuffer(Types.LIPS), local, s, r, gr, b, code + 1, flags);
			if (s.crack < 0 && s.sx > 0.2f) shards(buffers.getBuffer(Types.SHARD), local, s, lip, seed, r, gr, b);
		}

		VertexConsumer glow = buffers.getBuffer(Types.GLOW);
		Glow gl = new Glow(glow, world, eye, camera.rotation(), face);
		if (s.crack >= 0) cracks(gl, s, seed, r, gr, b);
		else if (s.open) fractures(gl, s, lip, seed, r, gr, b);
		if (s.open && (GateEntity.lightning(g.rank()) || s.tear > 0)) bolts(gl, s, lip, seed, r, gr, b);
		if (s.crack >= 0) gl.spot(0, 0, 0, 0.6f + s.crack * 1.2f, r, gr, b, 0.6f + 0.4f * s.crack, 0);
		if (s.flash > 0) {
			gl.spot(0, 0, 0, 7 * s.flash + 2, r, gr, b, Math.min(1, s.flash), 0);
			gl.streak(0, 0, 0, 16 * Math.min(1.4f, s.flash + 0.3f), 0.7f, r, gr, b, Math.min(1, s.flash * 1.2f));
		}
		if (s.wave >= 0) wave(gl, s, r, gr, b);
		pose.popPose();
		super.render(g, yaw, partial, pose, buffers, light);
	}

	private static float hash(long seed, int i) {
		long h = seed * 6364136223846793005L + i * 1442695040888963407L;
		h ^= h >>> 33;
		h *= 0xff51afd7ed558ccdL;
		h ^= h >>> 33;
		return (h & 0xFFFFFF) / (float) 0x1000000;
	}

	/** The tear's quad in the face's plane: as wide as the squeezed tear plus room for its halo, its UVs in blocks
	 *  (x as drawn, y unsqueezed so the field is read at its full height). */
	private static void tear(VertexConsumer v, Matrix4f m, State s, float r, float g, float b, int code, int flags) {
		float hx = GateRift.EX * s.sx + REACH, ky = GateRift.H + REACH + 0.2f, hy = ky * s.sy;
		v.addVertex(m, -hx, -hy, 0).setColor(r, g, b, s.live).setUv(-hx, -ky).setUv2(code, flags);
		v.addVertex(m, hx, -hy, 0).setColor(r, g, b, s.live).setUv(hx, -ky).setUv2(code, flags);
		v.addVertex(m, hx, hy, 0).setColor(r, g, b, s.live).setUv(hx, ky).setUv2(code, flags);
		v.addVertex(m, -hx, hy, 0).setColor(r, g, b, s.live).setUv(-hx, ky).setUv2(code, flags);
	}

	/** A point on the lip (squeezed with the tear), and in `out` the way out from it there. */
	private static Vector3f lipPoint(float[] lip, int i, State s, Vector3f out) {
		int n = lip.length / 2, a = Math.floorMod(i, n), c = (a + 1) % n;
		float x = lip[a * 2] * s.sx, y = lip[a * 2 + 1] * s.sy, tx = lip[c * 2] * s.sx - x, ty = lip[c * 2 + 1] * s.sy - y;
		float len = Mth.sqrt(tx * tx + ty * ty) + 1e-5f;
		out.set(ty / len, -tx / len, 0); // outward, the outline running counter-clockwise
		return new Vector3f(x, y, 0);
	}

	/** Shards of the world knocked loose off its lips: each a tilted sliver showing what's behind it out of place. */
	private static void shards(VertexConsumer v, Matrix4f m, State s, float[] lip, long seed, float r, float g, float b) {
		GateWarp.grab();
		float grow = Mth.clamp((s.sx - 0.2f) / 0.8f, 0, 1) * s.live;
		Vector3f out = new Vector3f();
		for (int i = 0; i < 9; i++) {
			Vector3f p = lipPoint(lip, (int) (hash(seed, 600 + i) * 1000), s, out);
			float off = 0.35f + hash(seed, 610 + i) * 1.4f, size = (0.22f + hash(seed, 620 + i) * 0.4f) * grow;
			float bob = Mth.sin(s.t * 0.05f + i * 1.7f) * 0.08f, spin = s.t * 0.004f * (hash(seed, 630 + i) - 0.5f);
			float cx = p.x + out.x * off, cy = p.y + out.y * off + bob, cz = (hash(seed, 640 + i) - 0.5f) * 0.8f;
			float tilt = (hash(seed, 650 + i) - 0.5f) * 1.2f;
			int dir = (int) (hash(seed, 660 + i) * 64);
			for (int k = 0; k < 4; k++) {
				float a = (k + hash(seed, 670 + i * 4 + k) * 0.6f) * Mth.HALF_PI + spin, rad = size * (0.6f + hash(seed, 690 + i * 4 + k) * 0.7f);
				float x = Mth.cos(a) * rad, y = Mth.sin(a) * rad * 1.4f;
				v.addVertex(m, cx + x, cy + y, cz + x * tilt).setColor(r, g, b, grow).setUv(k == 1 || k == 2 ? 1 : -1, k >= 2 ? 1 : -1).setUv2(dir, 0);
			}
		}
	}

	/** Added-light shapes, in the frame turned with the world (origin at the gate's middle). */
	static final class Glow {
		final VertexConsumer v;
		final Matrix4f m;
		final Vector3f eye, right, up;
		final Quaternionf face;

		Glow(VertexConsumer v, Matrix4f m, Vector3f eye, Quaternionf cam, Quaternionf face) {
			this.v = v;
			this.m = m;
			this.eye = eye;
			this.right = new Vector3f(1, 0, 0).rotate(cam);
			this.up = new Vector3f(0, 1, 0).rotate(cam);
			this.face = face;
		}

		/** A point in the gate's own frame, turned into this one. */
		Vector3f local(float x, float y, float z) {
			return new Vector3f(x, y, z).rotate(face);
		}

		void quad(Vector3f c, Vector3f ax, Vector3f ay, float r, float g, float b, float a, int mode) {
			vert(c.x - ax.x - ay.x, c.y - ax.y - ay.y, c.z - ax.z - ay.z, r, g, b, a, -1, -1, mode);
			vert(c.x + ax.x - ay.x, c.y + ax.y - ay.y, c.z + ax.z - ay.z, r, g, b, a, 1, -1, mode);
			vert(c.x + ax.x + ay.x, c.y + ax.y + ay.y, c.z + ax.z + ay.z, r, g, b, a, 1, 1, mode);
			vert(c.x - ax.x + ay.x, c.y - ax.y + ay.y, c.z - ax.z + ay.z, r, g, b, a, -1, 1, mode);
		}

		void vert(float x, float y, float z, float r, float g, float b, float a, float u, float w, int mode) {
			v.addVertex(m, x, y, z).setColor(r, g, b, a).setUv(u, w).setUv2(mode, 0);
		}

		/** A round glow facing you. */
		void spot(float x, float y, float z, float size, float r, float g, float b, float a, int mode) {
			quad(new Vector3f(x, y, z), new Vector3f(right).mul(size), new Vector3f(up).mul(size), r, g, b, a, mode);
		}

		/** A lens streak: long and thin across the screen. */
		void streak(float x, float y, float z, float half, float tall, float r, float g, float b, float a) {
			quad(new Vector3f(x, y, z), new Vector3f(right).mul(half), new Vector3f(up).mul(tall), r, g, b, a, 1);
		}

		/** A soft line from p to q, w wide, turned toward you. */
		void line(Vector3f p, Vector3f q, float w, float r, float g, float b, float a) {
			Vector3f d = new Vector3f(q).sub(p);
			Vector3f toEye = new Vector3f(eye).sub(p);
			Vector3f side = d.cross(toEye, new Vector3f());
			if (side.lengthSquared() < 1e-8f) return;
			side.normalize(w / 2);
			vert(p.x - side.x, p.y - side.y, p.z - side.z, r, g, b, a, 0, -1, 2);
			vert(q.x - side.x, q.y - side.y, q.z - side.z, r, g, b, a, 0, -1, 2);
			vert(q.x + side.x, q.y + side.y, q.z + side.z, r, g, b, a, 0, 1, 2);
			vert(p.x + side.x, p.y + side.y, p.z + side.z, r, g, b, a, 0, 1, 2);
		}
	}

	private static float hot(float c) {
		return Math.min(1, c * 0.5f + 0.5f);
	}

	/** A jagged forking line through the face's plane, from (x, y) heading at angle ang. */
	private static void jag(Glow gl, long k, float x, float y, float ang, int steps, float step, float w, float grow, float r, float g, float b, float a, int depth) {
		Vector3f p = gl.local(x, y, -0.05f);
		int n = Math.max(1, (int) (steps * grow));
		for (int j = 0; j < n; j++) {
			ang += (hash(k, 10 + j * 3) - 0.5f) * 1.2f;
			x += Mth.cos(ang) * step;
			y += Mth.sin(ang) * step;
			Vector3f q = gl.local(x, y, -0.05f);
			gl.line(p, q, w, r, g, b, a);
			if (depth < 2 && hash(k, 11 + j * 3) < 0.22f)
				jag(gl, k * 31 + j, x, y, ang + (hash(k, 12 + j * 3) < 0.5f ? -1 : 1) * 0.8f, steps / 2, step * 0.8f, w * 0.65f, grow, r, g, b, a, depth + 1);
			p = q;
			w *= 0.9f;
		}
	}

	/** Before it opens: reality splits like struck glass off the hairline, flickering, spreading. */
	private static void cracks(Glow gl, State s, long seed, float r, float g, float b) {
		float flick = 0.75f + 0.25f * hash(seed, (int) s.t * 13);
		for (int i = 0; i < 9; i++) {
			float y = (hash(seed, 300 + i) - 0.5f) * GateRift.H * 1.3f * s.sy;
			boolean right = hash(seed, 320 + i) < 0.5f;
			float ang = (right ? 0 : Mth.PI) + (hash(seed, 340 + i) - 0.5f) * 1.8f;
			jag(gl, seed ^ (i * 977L), 0, y, ang, 10, 0.35f, 0.12f, s.crack, hot(r), hot(g), hot(b), flick, 0);
		}
	}

	/** Once open: the air round it fractured like struck glass, lines running off its lips, reaching out as it
	 *  widens and drawn back in as it seals. */
	private static void fractures(Glow gl, State s, float[] lip, long seed, float r, float g, float b) {
		float grow = Mth.clamp(s.sx, 0, 1), flick = 0.8f + 0.2f * hash(seed, (int) (s.t / 3) * 7);
		Vector3f out = new Vector3f();
		for (int i = 0; i < 10; i++) {
			Vector3f p = lipPoint(lip, (int) (hash(seed, 400 + i) * 1000), s, out);
			float ang = (float) Math.atan2(out.y, out.x) + (hash(seed, 420 + i) - 0.5f) * 1.0f;
			jag(gl, seed ^ (i * 6007L), p.x, p.y, ang, 9, 0.28f, 0.08f, grow, hot(r), hot(g), hot(b), flick * s.live, 0);
		}
	}

	/** Lightning crawling off the lips: always for SS and SSS, for every rank as it closes. */
	private static void bolts(Glow gl, State s, float[] lip, long seed, float r, float g, float b) {
		int beat = (int) (s.t / 2);
		int count = 2 + (int) (s.tear * 5);
		Vector3f out = new Vector3f();
		for (int i = 0; i < count; i++) {
			long k = seed ^ (beat * 7919L + i * 104729L);
			if (hash(k, 0) > 0.7f) continue;
			Vector3f p = lipPoint(lip, (int) (hash(k, 1) * 1000), s, out);
			jag(gl, k, p.x, p.y, (float) Math.atan2(out.y, out.x), 7, 0.45f, 0.1f, 1, hot(r), hot(g), hot(b), 1, 1);
		}
	}

	/** The shockwave: a ring of light racing over the ground. */
	private static void wave(Glow gl, State s, float r, float g, float b) {
		float f = s.wave / (s.waveR > 10 ? 34 : 30), rad = s.waveR * (1 - (1 - f) * (1 - f)) + 0.5f;
		float a = (1 - f) * (1 - f), y = -GateEntity.MID + 0.2f;
		int n = 96;
		for (int i = 0; i < n; i++) {
			float t0 = i * Mth.TWO_PI / n, t1 = (i + 1) * Mth.TWO_PI / n;
			float w = 0.55f;
			Vector3f a0 = new Vector3f(Mth.cos(t0) * (rad - w), y, Mth.sin(t0) * (rad - w)), a1 = new Vector3f(Mth.cos(t1) * (rad - w), y, Mth.sin(t1) * (rad - w));
			Vector3f b0 = new Vector3f(Mth.cos(t0) * (rad + w), y, Mth.sin(t0) * (rad + w)), b1 = new Vector3f(Mth.cos(t1) * (rad + w), y, Mth.sin(t1) * (rad + w));
			gl.vert(a0.x, a0.y, a0.z, r, g, b, a, 0, -1, 2);
			gl.vert(a1.x, a1.y, a1.z, r, g, b, a, 0, -1, 2);
			gl.vert(b1.x, b1.y, b1.z, r, g, b, a, 0, 1, 2);
			gl.vert(b0.x, b0.y, b0.z, r, g, b, a, 0, 1, 2);
		}
	}

	/** Bits of the dungeon it tore through: rise as it cracks, flung out as it bursts, hanging and turning, dragged in as it closes. */
	private static void earth(PoseStack pose, MultiBufferSource buffers, State s, long seed, int light, BlockState[] debris) {
		var blocks = Minecraft.getInstance().getBlockRenderer();
		int lit = LightTexture.pack(Math.max(LightTexture.block(light), 12), LightTexture.sky(light));
		float spin = 1 + (s.hot - 1) * 3;
		for (int i = 0; i < 18; i++) {
			float a0 = hash(seed, i * 7) * Mth.TWO_PI, rad = 3.4f + hash(seed, i * 7 + 1) * 3.2f, h = (hash(seed, i * 7 + 2) - 0.35f) * 9f;
			float size = 0.35f + hash(seed, i * 7 + 3) * 0.6f, v = 0.4f + hash(seed, i * 7 + 4) * 0.6f;
			float ang = a0 + s.t * 0.006f * v * spin;
			float y = Mth.lerp(s.lift, -GateEntity.MID + 0.5f, h * Math.min(1.2f, s.push)) + Mth.sin(s.t * 0.04f + a0) * 0.2f;
			pose.pushPose();
			pose.translate(Mth.cos(ang) * rad * s.push, y, Mth.sin(ang) * rad * s.push * 0.7f);
			pose.mulPose(Axis.XP.rotation(s.t * 0.015f * v * spin + a0));
			pose.mulPose(Axis.ZP.rotation(s.t * 0.01f * v * spin));
			float sz = size * Math.min(1, s.push + 0.2f);
			pose.scale(sz, sz, sz);
			pose.translate(-0.5, -0.5, -0.5);
			blocks.renderSingleBlock(debris[i % debris.length], pose, buffers, lit, OverlayTexture.NO_OVERLAY);
			pose.popPose();
		}
	}

	// ---------------------------------------------------------------- the frame copy the shards bend

	/** Once a frame (when a gate's shards first need it): the frame so far, copied into a texture. */
	static final class GateWarp {
		private static TextureTarget target;
		private static int frame = -1;
		static int frameNow;

		static final class Tex extends AbstractTexture {
			@Override
			public void load(ResourceManager rm) {}

			@Override
			public int getId() {
				return target == null ? 0 : target.getColorTextureId();
			}

			@Override
			public void releaseId() {}
		}

		static void grab() {
			if (frame == frameNow) return;
			frame = frameNow;
			Minecraft mc = Minecraft.getInstance();
			RenderTarget main = mc.getMainRenderTarget();
			int draw = GL11.glGetInteger(GL30.GL_DRAW_FRAMEBUFFER_BINDING), read = GL11.glGetInteger(GL30.GL_READ_FRAMEBUFFER_BINDING);
			if (target == null) {
				target = new TextureTarget(main.width, main.height, false, Minecraft.ON_OSX);
				target.setFilterMode(GL11.GL_LINEAR);
				mc.getTextureManager().register(WARP, new Tex());
			} else if (target.width != main.width || target.height != main.height) {
				target.resize(main.width, main.height, Minecraft.ON_OSX);
			}
			GlStateManager._glBindFramebuffer(GL30.GL_READ_FRAMEBUFFER, main.frameBufferId);
			GlStateManager._glBindFramebuffer(GL30.GL_DRAW_FRAMEBUFFER, target.frameBufferId);
			GlStateManager._glBlitFrameBuffer(0, 0, main.width, main.height, 0, 0, target.width, target.height, GL11.GL_COLOR_BUFFER_BIT, GL11.GL_NEAREST);
			GlStateManager._glBindFramebuffer(GL30.GL_READ_FRAMEBUFFER, read);
			GlStateManager._glBindFramebuffer(GL30.GL_DRAW_FRAMEBUFFER, draw);
			GlStateManager._viewport(0, 0, main.width, main.height);
		}
	}
}
