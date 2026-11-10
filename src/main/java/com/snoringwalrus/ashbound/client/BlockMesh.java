package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

import org.joml.Matrix4f;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.ByteBufferBuilder;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.MeshData;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexBuffer;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.snoringwalrus.ashbound.Ashbound;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.ItemBlockRenderTypes;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.ShaderInstance;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockAndTintGetter;
import net.minecraft.world.level.ColorResolver;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.lighting.LevelLightEngine;
import net.minecraft.world.level.material.FluidState;
import net.neoforged.neoforge.client.model.data.ModelData;

/**
 * A pile of blocks that isn't in the world, meshed once and drawn with our own matrices: a dungeon's first hall seen
 * through its gate, the world kept behind a way out, the whole dungeon for the intro's run (GateWindow, DungeonRun).
 * Built off the render thread (the blocks' own models, ambient occlusion, biome tints of plains), its light baked into
 * the vertex colours from its own light values (so it looks the same in any dimension, at any hour), uploaded when ready.
 */
public final class BlockMesh {
	/** Blocks and their light (block light in the low 4 bits, sky light in the next 4), in the pile's own coordinates. */
	public static final class Blocks {
		final Map<Long, BlockState> states = new HashMap<>();
		final Map<Long, Integer> light = new HashMap<>();

		public void put(int x, int y, int z, BlockState s) {
			if (!s.isAir()) states.put(BlockPos.asLong(x, y, z), s);
		}

		public void light(int x, int y, int z, int block, int sky) {
			light.put(BlockPos.asLong(x, y, z), block | sky << 4);
		}

		public BlockState get(BlockPos p) {
			return states.getOrDefault(p.asLong(), net.minecraft.world.level.block.Blocks.AIR.defaultBlockState());
		}

		public boolean isEmpty() {
			return states.isEmpty();
		}

		/** Light flooding out from whatever glows in it (lamps, lanterns), stopped by solid blocks; no sky. */
		public void flood() {
			java.util.ArrayDeque<long[]> q = new java.util.ArrayDeque<>();
			Map<Long, Integer> lv = new HashMap<>();
			for (var e : states.entrySet()) {
				int l = e.getValue().getLightEmission();
				if (l > 0) {
					lv.put(e.getKey(), l);
					q.add(new long[] {e.getKey(), l});
				}
			}
			BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
			while (!q.isEmpty()) {
				long[] c = q.poll();
				if (lv.getOrDefault(c[0], 0) != c[1] || c[1] <= 1) continue;
				int x = BlockPos.getX(c[0]), y = BlockPos.getY(c[0]), z = BlockPos.getZ(c[0]);
				for (Direction d : Direction.values()) {
					long n = BlockPos.asLong(x + d.getStepX(), y + d.getStepY(), z + d.getStepZ());
					BlockState s = states.get(n);
					if (s != null && s.canOcclude()) continue;
					int l = (int) c[1] - 1;
					if (lv.getOrDefault(n, 0) >= l) continue;
					lv.put(n, l);
					q.add(new long[] {n, l});
				}
			}
			for (var e : lv.entrySet()) light.merge(e.getKey(), e.getValue(), (a, b) -> Math.max(a & 15, b) | (a & 0xF0));
		}
	}

	private record Layer(RenderType type, VertexBuffer buffer) {}

	private final List<Layer> layers = new ArrayList<>();
	private CompletableFuture<Map<RenderType, MeshData>> building;
	private boolean ready;

	private BlockMesh() {}

	/** Starts meshing `blocks` in the background; draw() shows it once it's done. skyK: how bright sky light counts. */
	public static BlockMesh of(Blocks blocks, float skyK) {
		BlockMesh m = new BlockMesh();
		m.building = CompletableFuture.supplyAsync(() -> mesh(blocks, skyK), net.minecraft.Util.backgroundExecutor());
		return m;
	}

	public boolean ready() {
		if (!ready && building != null && building.isDone()) {
			try {
				for (var e : building.join().entrySet()) {
					VertexBuffer vb = new VertexBuffer(VertexBuffer.Usage.STATIC);
					vb.bind();
					vb.upload(e.getValue());
					VertexBuffer.unbind();
					layers.add(new Layer(e.getKey(), vb));
				}
			} catch (Exception ex) {
				Ashbound.LOG.error("A block mesh failed to build", ex);
			}
			building = null;
			ready = true;
		}
		return ready;
	}

	public void close() {
		for (Layer l : layers) l.buffer().close();
		layers.clear();
		if (building != null) building.cancel(false);
	}

	/** Draws it (solid layers, then see-through ones if `translucent`) with these matrices; fog off while it does. */
	public void draw(Matrix4f modelView, Matrix4f proj, boolean solid, boolean translucent) {
		if (!ready()) return;
		float fs = RenderSystem.getShaderFogStart(), fe = RenderSystem.getShaderFogEnd();
		RenderSystem.setShaderFogStart(4096);
		RenderSystem.setShaderFogEnd(8192);
		for (Layer l : layers) {
			boolean t = l.type() == RenderType.translucent();
			if (t ? !translucent : !solid) continue;
			l.type().setupRenderState();
			ShaderInstance sh = RenderSystem.getShader();
			if (sh != null) {
				if (sh.CHUNK_OFFSET != null) sh.CHUNK_OFFSET.set(0f, 0f, 0f);
				l.buffer().bind();
				l.buffer().drawWithShader(modelView, proj, sh);
				VertexBuffer.unbind();
			}
			l.type().clearRenderState();
		}
		RenderSystem.setShaderFogStart(fs);
		RenderSystem.setShaderFogEnd(fe);
	}

	// ---------------------------------------------------------------- meshing

	private static final RenderType[] ORDER = {RenderType.solid(), RenderType.cutoutMipped(), RenderType.cutout(), RenderType.translucent()};

	private static Map<RenderType, MeshData> mesh(Blocks b, float skyK) {
		Minecraft mc = Minecraft.getInstance();
		var dispatcher = mc.getBlockRenderer();
		View view = new View(b);
		RandomSource rnd = RandomSource.create();
		Map<RenderType, ByteBufferBuilder> bytes = new HashMap<>();
		Map<RenderType, Lit> out = new HashMap<>();
		for (RenderType t : ORDER) {
			ByteBufferBuilder bb = new ByteBufferBuilder(t.bufferSize());
			bytes.put(t, bb);
			out.put(t, new Lit(new BufferBuilder(bb, VertexFormat.Mode.QUADS, DefaultVertexFormat.BLOCK), skyK));
		}
		PoseStack pose = new PoseStack();
		BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
		for (var e : b.states.entrySet()) {
			BlockState s = e.getValue();
			p.set(e.getKey());
			FluidState f = s.getFluidState();
			if (!f.isEmpty()) {
				Lit lit = out.get(fluidLayer(ItemBlockRenderTypes.getRenderLayer(f)));
				lit.ox = p.getX() & ~15;
				lit.oy = p.getY() & ~15;
				lit.oz = p.getZ() & ~15;
				try {
					dispatcher.renderLiquid(p, view, lit, s, f);
				} catch (Exception ignored) {}
				lit.ox = lit.oy = lit.oz = 0;
			}
			if (s.getRenderShape() != RenderShape.MODEL) continue;
			var model = dispatcher.getBlockModel(s);
			long seed = s.getSeed(p);
			rnd.setSeed(seed);
			for (RenderType t : model.getRenderTypes(s, rnd, ModelData.EMPTY)) {
				Lit lit = out.get(fluidLayer(t));
				pose.pushPose();
				pose.translate(p.getX(), p.getY(), p.getZ());
				rnd.setSeed(seed);
				try {
					dispatcher.renderBatched(s, p, view, pose, lit, true, rnd, ModelData.EMPTY, t);
				} catch (Exception ignored) {}
				pose.popPose();
			}
		}
		Map<RenderType, MeshData> done = new HashMap<>();
		for (RenderType t : ORDER) {
			MeshData d = out.get(t).to.build();
			if (d != null) done.put(t, d);
		}
		return done;
	}

	private static RenderType fluidLayer(RenderType t) {
		for (RenderType o : ORDER) if (o == t) return t;
		return RenderType.cutout();
	}

	/** Bakes the light into the colour (and draws at full light): the pile looks lit by its own lamps anywhere. Also
	 *  shifts the liquid renderer's section-relative points back to where they belong. */
	private static final class Lit implements VertexConsumer {
		final BufferBuilder to;
		final float skyK;
		int ox, oy, oz;
		private int r, g, b, a;

		Lit(BufferBuilder to, float skyK) {
			this.to = to;
			this.skyK = skyK;
		}

		@Override
		public VertexConsumer addVertex(float x, float y, float z) {
			to.addVertex(x + ox, y + oy, z + oz);
			return this;
		}

		@Override
		public VertexConsumer setColor(int r, int g, int b, int a) {
			this.r = r;
			this.g = g;
			this.b = b;
			this.a = a;
			return this;
		}

		@Override
		public VertexConsumer setUv(float u, float v) {
			to.setUv(u, v);
			return this;
		}

		@Override
		public VertexConsumer setUv1(int u, int v) {
			return this;
		}

		@Override
		public VertexConsumer setUv2(int u, int v) {
			float l = Math.max(u, v * skyK) / 240f;
			l = Mth.clamp(l, 0, 1);
			float k = l / (4 - 3 * l);
			k = Math.max(0.035f, Mth.lerp(0.45f, k, 1 - (1 - k) * (1 - k) * (1 - k) * (1 - k)));
			to.setColor(Math.round(r * k), Math.round(g * k), Math.round(b * k), a);
			to.setUv2(240, 240);
			return this;
		}

		@Override
		public VertexConsumer setNormal(float x, float y, float z) {
			to.setNormal(x, y, z);
			return this;
		}
	}

	/** The pile as a block getter for the models: its blocks, its light, plains' colours. */
	private static final class View implements BlockAndTintGetter {
		private final Blocks b;
		private final Biome plains;

		View(Blocks b) {
			this.b = b;
			Minecraft mc = Minecraft.getInstance();
			this.plains = mc.level.registryAccess().registryOrThrow(Registries.BIOME).getOrThrow(Biomes.PLAINS);
		}

		@Override
		public float getShade(Direction d, boolean shade) {
			if (!shade) return 1;
			return switch (d) {
				case DOWN -> 0.5f;
				case UP -> 1f;
				case NORTH, SOUTH -> 0.8f;
				default -> 0.6f;
			};
		}

		@Override
		public LevelLightEngine getLightEngine() {
			return Minecraft.getInstance().level.getLightEngine();
		}

		@Override
		public int getBrightness(LightLayer layer, BlockPos p) {
			int l = b.light.getOrDefault(p.asLong(), 0);
			return layer == LightLayer.SKY ? l >> 4 & 15 : l & 15;
		}

		@Override
		public int getRawBrightness(BlockPos p, int darken) {
			int l = b.light.getOrDefault(p.asLong(), 0);
			return Math.max(l & 15, (l >> 4 & 15) - darken);
		}

		@Override
		public boolean canSeeSky(BlockPos p) {
			return false;
		}

		@Override
		public int getBlockTint(BlockPos p, ColorResolver r) {
			return r.getColor(plains, p.getX(), p.getZ());
		}

		@Override
		public BlockEntity getBlockEntity(BlockPos p) {
			return null;
		}

		@Override
		public BlockState getBlockState(BlockPos p) {
			return b.get(p);
		}

		@Override
		public FluidState getFluidState(BlockPos p) {
			return b.get(p).getFluidState();
		}

		@Override
		public int getHeight() {
			return 4096;
		}

		@Override
		public int getMinBuildHeight() {
			return -2048;
		}
	}
}
