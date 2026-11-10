package com.snoringwalrus.ashbound.client;

import org.joml.Matrix4f;
import org.joml.Matrix4fStack;
import org.joml.Vector3f;
import org.lwjgl.opengl.GL11;
import org.lwjgl.opengl.GL30;

import com.mojang.blaze3d.pipeline.RenderTarget;
import com.mojang.blaze3d.pipeline.TextureTarget;
import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.BufferUploader;
import com.mojang.blaze3d.vertex.ByteBufferBuilder;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.MeshData;
import com.mojang.blaze3d.vertex.Tesselator;
import com.mojang.blaze3d.vertex.VertexFormat;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.ShaderInstance;

/**
 * The glow on the effects, and only on them: nothing in the world blooms. Every vertex the particles draw is written a
 * second time here, drawn into a small texture of its own with the world's depth so walls still hide it, blurred at
 * two sizes and added over the frame. It takes no new mod and touches nothing of vanilla's. spell_post.fsh is the blur.
 */
final class Bloom {
	private Bloom() {}

	private static final int CAPACITY = 1 << 18;
	private static final float TIGHT = 0.3f, MID = 0.5f, WIDE = 0.6f;
	private static ByteBufferBuilder bytes;
	private static BufferBuilder glow;
	private static RenderTarget half, quarterA, quarterB, eighthA, eighthB;
	/** How much of what's drawn right now goes into the glow: a heal beam is on screen for seconds at a time, and has to be easy on the eyes. */
	static float gain = 1;

	/** A frame's particles are starting. */
	static void begin() {
		if (glow != null) return;
		if (bytes == null) bytes = new ByteBufferBuilder(CAPACITY);
		bytes.clear();
		glow = new BufferBuilder(bytes, VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR_TEX_LIGHTMAP);
	}

	/** Smoke doesn't shine; everything else that's black adds nothing and hides the glow behind it, as it should. */
	static void vertex(Vector3f p, float u, float v, float r, float g, float b, float a, int light) {
		float k = gain * HudPrefs.fxGlow();   // how much they glow is each player's (FxSetup)
		if (glow == null || k <= 0 || (light & 0xFFFF) == SpellParticles.SMOKE) return;
		glow.addVertex(p.x, p.y, p.z).setUv(u, v).setColor(r * k, g * k, b * k, a * k).setLight(light);
	}

	private static RenderTarget target(RenderTarget old, int w, int h, boolean depth) {
		if (old != null && old.width == w && old.height == h) return old;
		if (old != null) old.destroyBuffers();
		TextureTarget t = new TextureTarget(w, h, depth, Minecraft.ON_OSX);
		t.setFilterMode(GL11.GL_LINEAR);
		t.setClearColor(0, 0, 0, 0);
		return t;
	}

	static void pass(ShaderInstance s, RenderTarget from, RenderTarget to, float dx, float dy, float gain) {
		if (to != null) to.bindWrite(true);
		RenderSystem.setShader(() -> s);
		RenderSystem.setShaderTexture(0, from.getColorTextureId());
		s.safeGetUniform("Step").set(dx, dy);
		s.safeGetUniform("Gain").set(gain);
		BufferBuilder q = Tesselator.getInstance().begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_TEX);
		q.addVertex(-1, -1, 0).setUv(0, 0);
		q.addVertex(1, -1, 0).setUv(1, 0);
		q.addVertex(1, 1, 0).setUv(1, 1);
		q.addVertex(-1, 1, 0).setUv(0, 1);
		BufferUploader.drawWithShader(q.buildOrThrow());
	}

	private static void blur(ShaderInstance s, RenderTarget from, RenderTarget a, RenderTarget b) {
		pass(s, from, a, 1f / from.width, 0, 1);
		pass(s, a, b, 0, 1f / a.height, 1);
	}

	/** The frame's particles are done: light them up. */
	static void draw(Matrix4f view) {
		if (glow == null) return;
		MeshData mesh = glow.build();
		glow = null;
		ShaderInstance post = GateShaders.post;
		if (mesh == null) return;
		if (post == null || GateShaders.spell == null) {
			mesh.close();
			return;
		}
		RenderTarget main = Minecraft.getInstance().getMainRenderTarget();
		int was = GlStateManager._getInteger(GL30.GL_DRAW_FRAMEBUFFER_BINDING), w = Math.max(16, main.width), h = Math.max(16, main.height);
		half = target(half, w / 2, h / 2, true);
		if (main.isStencilEnabled() && !half.isStencilEnabled()) half.enableStencil();   // or the depth can't be copied, and it shines through walls
		quarterA = target(quarterA, w / 4, h / 4, false);
		quarterB = target(quarterB, w / 4, h / 4, false);
		eighthA = target(eighthA, w / 8, h / 8, false);
		eighthB = target(eighthB, w / 8, h / 8, false);

		half.clear(Minecraft.ON_OSX);
		half.copyDepthFrom(main);
		half.bindWrite(true);
		Matrix4fStack stack = RenderSystem.getModelViewStack();
		stack.pushMatrix();
		stack.set(view);
		RenderSystem.applyModelViewMatrix();
		RenderSystem.enableBlend();
		RenderSystem.blendFunc(GlStateManager.SourceFactor.ONE, GlStateManager.DestFactor.ONE_MINUS_SRC_ALPHA);
		RenderSystem.enableDepthTest();
		RenderSystem.depthFunc(GL11.GL_LEQUAL);
		RenderSystem.depthMask(false);
		RenderSystem.disableCull();
		RenderSystem.setShader(() -> GateShaders.spell);
		RenderSystem.setShaderTexture(0, SpellParticles.ATLAS);
		BufferUploader.drawWithShader(mesh);
		stack.popMatrix();
		RenderSystem.applyModelViewMatrix();

		RenderSystem.disableDepthTest();
		RenderSystem.disableBlend();
		blur(post, half, quarterA, quarterB);
		blur(post, quarterB, eighthA, eighthB);
		RenderTarget out = ShaderPacks.on() ? ShaderPacks.layer() : main;
		out.bindWrite(true);
		RenderSystem.enableBlend();
		RenderSystem.blendFuncSeparate(GlStateManager.SourceFactor.ONE, GlStateManager.DestFactor.ONE, GlStateManager.SourceFactor.ZERO, GlStateManager.DestFactor.ONE);
		pass(post, half, null, 0, 0, TIGHT);
		pass(post, quarterB, null, 0, 0, MID);
		pass(post, eighthB, null, 0, 0, WIDE);
		if (out != main) {
			ShaderPacks.drew();
			main.bindWrite(true);
		}

		RenderSystem.defaultBlendFunc();
		RenderSystem.disableBlend();
		RenderSystem.enableDepthTest();
		RenderSystem.depthMask(true);
		GlStateManager._glBindFramebuffer(GL30.GL_FRAMEBUFFER, was);
	}
}
