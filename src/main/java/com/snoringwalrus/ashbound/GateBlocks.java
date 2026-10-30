package com.snoringwalrus.ashbound;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.ChainBlock;
import net.minecraft.world.level.block.FenceBlock;
import net.minecraft.world.level.block.IronBarsBlock;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.TrapDoorBlock;
import net.minecraft.world.level.block.WallBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockSetType;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.neoforge.registries.DeferredBlock;

/**
 * The older gates' blocks, listed in /ashbound/gate_blocks.json by tools/port_gate.py, so a dungeon comes over
 * without new code: its masonry ("full", "stairs", "slab", "wall", "pillar", each feeling like a vanilla block), and
 * its fittings, sculpted in Blender (tools/blender/gate_props.py) and drawn by NeoForge's OBJ loader: "facing" and
 * "plain" props with a hitbox, "chain", "bars", "fence", "lantern", "trapdoor" on vanilla's own behaviours, and
 * "coffer" (holds the loot, SilkProps.Coffer).
 */
public final class GateBlocks {
	private GateBlocks() {}

	static final Map<String, DeferredBlock<Block>> ALL = new HashMap<>();
	static final List<DeferredBlock<Block>> COFFERS = new ArrayList<>();

	private static DeferredBlock<Block> block(String name, Function<BlockBehaviour.Properties, ? extends Block> make, BlockBehaviour.Properties props) {
		if (ALL.containsKey(name)) {   // two gates with a block of one name: the first keeps it (a second registration would stop the rest loading)
			Ashbound.LOG.warn("gate block {} listed twice, the second is skipped", name);
			return ALL.get(name);
		}
		DeferredBlock<Block> b = WorldBlocks.BLOCKS.registerBlock(name, make::apply, props);
		WorldBlocks.ITEMS.add(Weapons.ITEMS.registerSimpleBlockItem(b));
		ALL.put(name, b);
		return b;
	}

	/** Loads the class, so its blocks are registered. */
	static void init() {}

	static {
		try (InputStream in = GateBlocks.class.getResourceAsStream("/ashbound/gate_blocks.json")) {
			if (in != null) {
				JsonObject j = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
				for (JsonElement e : j.getAsJsonArray("blocks")) masonry(e.getAsJsonObject());
				for (JsonElement e : j.getAsJsonArray("props")) prop(e.getAsJsonObject());
			}
		} catch (Exception e) {
			Ashbound.LOG.error("gate blocks not loaded", e);
		}
	}

	private static void masonry(JsonObject o) {
		String name = o.get("name").getAsString(), kind = o.get("kind").getAsString();
		BlockBehaviour.Properties p = BlockBehaviour.Properties.ofFullCopy(BuiltInRegistries.BLOCK.get(ResourceLocation.parse(o.get("feel").getAsString())));
		if (o.has("light")) {
			int light = o.get("light").getAsInt();
			p.lightLevel(s -> light);
		}
		switch (kind) {
			case "pillar" -> block(name, RotatedPillarBlock::new, p);
			case "slab" -> block(name, SlabBlock::new, p);
			case "wall" -> block(name, WallBlock::new, p.forceSolidOn());
			case "stairs" -> {
				DeferredBlock<Block> base = ALL.get(o.get("base").getAsString());
				block(name, q -> new StairBlock(base.get().defaultBlockState(), q), p);
			}
			default -> block(name, Block::new, p);
		}
	}

	private static SoundType sound(String name) {
		try {
			return (SoundType) SoundType.class.getField(name.toUpperCase(java.util.Locale.ROOT)).get(null);
		} catch (ReflectiveOperationException e) {
			return SoundType.STONE;
		}
	}

	private static MapColor color(String name) {
		try {
			return (MapColor) MapColor.class.getField(name.toUpperCase(java.util.Locale.ROOT)).get(null);
		} catch (ReflectiveOperationException e) {
			return MapColor.STONE;
		}
	}

	private static VoxelShape box(JsonObject o) {
		if (!o.has("box")) return Block.box(0, 0, 0, 16, 16, 16);
		JsonArray b = o.getAsJsonArray("box");
		return Block.box(b.get(0).getAsDouble(), b.get(1).getAsDouble(), b.get(2).getAsDouble(), b.get(3).getAsDouble(),
				b.get(4).getAsDouble(), b.get(5).getAsDouble());
	}

	private static void prop(JsonObject o) {
		String name = o.get("name").getAsString(), kind = o.get("kind").getAsString();
		BlockBehaviour.Properties p = BlockBehaviour.Properties.of().noOcclusion()
				.mapColor(color(o.has("color") ? o.get("color").getAsString() : "stone"))
				.sound(sound(o.has("sound") ? o.get("sound").getAsString() : "stone"))
				.strength(o.has("strength") ? o.get("strength").getAsFloat() : 1.5f);
		if (o.has("light")) {
			int light = o.get("light").getAsInt();
			p.lightLevel(s -> light);
		}
		if (o.has("solid") && !o.get("solid").getAsBoolean()) p.noCollission();
		VoxelShape shape = box(o);
		switch (kind) {
			case "chain" -> block(name, ChainBlock::new, p);
			case "bars" -> block(name, q -> new IronBarsBlock(q) {}, p);
			case "fence" -> block(name, FenceBlock::new, p);
			case "lantern" -> block(name, LanternBlock::new, p);
			case "trapdoor" -> block(name, q -> new TrapDoorBlock(BlockSetType.IRON, q), p);
			case "pillar" -> block(name, RotatedPillarBlock::new, p);
			case "coffer" -> COFFERS.add(block(name, SilkProps.Coffer::new, p));
			case "hoard" -> COFFERS.add(block(name, SilkProps.Hoard::new, p));
			case "facing" -> block(name, q -> new PropBlock.Facing(q, shape), p);
			default -> block(name, q -> new Block(q) {
				@Override
				protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
					return shape;
				}
			}, p);
		}
	}
}
