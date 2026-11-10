package com.snoringwalrus.ashbound.client;

import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodType;

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

/**
 * Our effects under an Iris shader pack. While a pack draws the world Iris throws away whatever is drawn onto the main
 * target with a shader it doesn't know, and all of ours are. So with a pack on they go into a layer of their own that shares
 * the world's depth, walls still hiding them, and the layer goes over the frame once the pack has finished it. Nothing here
 * does anything without a pack, and Iris stays optional: it's reached by name.
 */
public final class ShaderPacks {
	private ShaderPacks() {}

	private static final int CAPACITY = 1 << 18;
	private static final Object API;
	private static final MethodHandle IN_USE, SHADOW_PASS;
	private static TextureTarget layer;
	private static ByteBufferBuilder bytes;
	private static int depth = -1;
	private static boolean inside, drawn;

	static {
		Object api = null;
		MethodHandle use = null, shadow = null;
		try {
			Class<?> c = Class.forName("net.irisshaders.iris.api.v0.IrisApi");
			MethodHandles.Lookup l = MethodHandles.publicLookup();
			api = l.findStatic(c, "getInstance", MethodType.methodType(c)).invoke();
			use = l.findVirtual(c, "isShaderPackInUse", MethodType.methodType(boolean.class));
			shadow = l.findVirtual(c, "isRenderingShadowPass", MethodType.methodType(boolean.class));
		} catch (Throwable noIris) {
			api = null;
		}
		API = api;
		IN_USE = use;
		SHADOW_PASS = shadow;
	}

	private static boolean ask(MethodHandle h) {
		if (API == null) return false;
		try {
			return (boolean) h.invoke(API);
		} catch (Throwable e) {
			return false;
		}
	}

	static boolean on() {
		return ask(IN_USE);
	}

	/** The layer, the size of the frame and on the frame's depth. */
	static RenderTarget layer() {
		RenderTarget main = Minecraft.getInstance().getMainRenderTarget();
		if (layer == null || layer.width != main.width || layer.height != main.height || depth != main.getDepthTextureId()) {
			if (layer != null) layer.destroyBuffers();
			layer = new TextureTarget(main.width, main.height, false, Minecraft.ON_OSX);
			layer.setClearColor(0, 0, 0, 0);
			depth = main.getDepthTextureId();
			layer.bindWrite(false);
			GlStateManager._glFramebufferTexture2D(GL30.GL_FRAMEBUFFER, GL30.GL_DEPTH_ATTACHMENT, GL11.GL_TEXTURE_2D, depth, 0);
			layer.clear(Minecraft.ON_OSX);
			main.bindWrite(true);
		}
		return layer;
	}

	/** What's drawn from here goes into the layer. The sun's view of the world doesn't belong in it. */
	static void bind() {
		if (!on() || ask(SHADOW_PASS)) return;
		layer().bindWrite(true);
		inside = drawn = true;
	}

	static void unbind() {
		if (!inside) return;
		inside = false;
		Minecraft.getInstance().getMainRenderTarget().bindWrite(true);
	}

	/** Something was put in the layer without {@link #bind()}. */
	static void drew() {
		drawn = true;
	}

	/** A particle sheet's buffer: with a pack on it draws itself into the layer, and the engine gets nothing to throw away. */
	static BufferBuilder sheet(Tesselator tesselator) {
		if (!on()) return tesselator.begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR_TEX_LIGHTMAP);
		if (bytes == null) bytes = new ByteBufferBuilder(CAPACITY);
		bytes.clear();
		return new Sheet(bytes);
	}

	private static final class Sheet extends BufferBuilder {
		Sheet(ByteBufferBuilder bytes) {
			super(bytes, VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR_TEX_LIGHTMAP);
		}

		@Override
		public MeshData build() {
			MeshData mesh = super.build();
			if (mesh != null) {
				bind();
				BufferUploader.drawWithShader(mesh);
				unbind();
			}
			return null;
		}
	}

	/** The pack has finished the frame: it's now on the main target, and ours goes over it. */
	public static void present() {
		if (!on()) return;
		GateRenderer.GateWarp.late();
		if (!drawn || GateShaders.post == null) return;
		drawn = false;
		RenderTarget main = Minecraft.getInstance().getMainRenderTarget();
		main.bindWrite(true);
		RenderSystem.disableDepthTest();
		RenderSystem.depthMask(false);
		RenderSystem.enableBlend();
		RenderSystem.blendFuncSeparate(GlStateManager.SourceFactor.ONE, GlStateManager.DestFactor.ONE_MINUS_SRC_ALPHA, GlStateManager.SourceFactor.ZERO, GlStateManager.DestFactor.ONE);
		Bloom.pass(GateShaders.post, layer(), null, 0, 0, 1);
		RenderSystem.defaultBlendFunc();
		RenderSystem.disableBlend();
		RenderSystem.enableDepthTest();
		RenderSystem.depthMask(true);
		layer().clear(Minecraft.ON_OSX);
		main.bindWrite(true);
	}
}
