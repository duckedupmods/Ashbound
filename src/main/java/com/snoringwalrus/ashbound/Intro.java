package com.snoringwalrus.ashbound;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.UUID;

import com.mojang.brigadier.Command;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.animal.horse.Horse;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Hob Tarrant's wagon, by the world's spawn: a hay cart and its two horses, turned to face the capital, and the wagoner
 * who pulled you off the road. He asks whether everyone's here, then IntroScene plays for you and whoever's stood with
 * you and hasn't seen it: what the gates' colours mean, and where Highmourn is. Nobody can be hurt while they watch.
 */
public final class Intro {
	private Intro() {}

	static final String KIND = "wagoner";
	/** IntroScene's length in ticks. */
	public static final int LENGTH = 1010;
	private static final String SEEN = "saw_intro", HINT = "intro_hint", TAG = "ashbound_wagon";
	private static final ResourceLocation CART = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "hay_cart");
	private static final int NEAR = 48, CLEARING = 20, TREE_TOP = 40, SEARCH = 24, FORCE_CHUNKS = 4, LATE = 100;
	private static final Map<UUID, Long> WATCHING = new HashMap<>();

	// ---------------------------------------------------------------- where it stands, kept with the world

	static final class State extends SavedData {
		boolean placed;
		int x, y, z;
		float yaw;

		static State get(ServerLevel level) {
			return level.getDataStorage().computeIfAbsent(new SavedData.Factory<>(State::new, State::load, null), "ashbound_intro");
		}

		static State load(CompoundTag tag, HolderLookup.Provider p) {
			State s = new State();
			s.placed = tag.getBoolean("placed");
			s.x = tag.getInt("x");
			s.y = tag.getInt("y");
			s.z = tag.getInt("z");
			s.yaw = tag.getFloat("yaw");
			return s;
		}

		@Override
		public CompoundTag save(CompoundTag tag, HolderLookup.Provider p) {
			tag.putBoolean("placed", placed);
			tag.putInt("x", x);
			tag.putInt("y", y);
			tag.putInt("z", z);
			tag.putFloat("yaw", yaw);
			return tag;
		}
	}

	// ---------------------------------------------------------------- putting it in the world

	private static void set(ServerLevel level) {
		State st = State.get(level);
		BlockPos spawn = level.getSharedSpawnPos();
		for (int x = -FORCE_CHUNKS; x <= FORCE_CHUNKS; x++)
			for (int z = -FORCE_CHUNKS; z <= FORCE_CHUNKS; z++) level.getChunk((spawn.getX() >> 4) + x, (spawn.getZ() >> 4) + z);
		BlockPos at = spot(level, spawn);
		int[] c = Capital.centre();
		Vec3 way = c == null ? new Vec3(0, 0, 1) : new Vec3(c[0] - at.getX(), 0, c[1] - at.getZ()).normalize();
		place(level, at, way);
		st.placed = true;
		st.x = at.getX();
		st.y = at.getY();
		st.z = at.getZ();
		st.yaw = yaw(way);
		st.setDirty();
	}

	private static float yaw(Vec3 way) {
		return (float) (Mth.atan2(-way.x, way.z) * Mth.RAD_TO_DEG);
	}

	/** The ground near spawn that's flattest and dry, a little off the spot itself; `at` is the block the cart stands on. */
	private static BlockPos spot(ServerLevel level, BlockPos spawn) {
		BlockPos best = spawn;
		double low = Double.MAX_VALUE;
		for (int r = 8; r <= SEARCH; r += 4)
			for (int k = 0; k < 16; k++) {
				int x = spawn.getX() + (int) (Math.cos(k * Math.PI / 8) * r), z = spawn.getZ() + (int) (Math.sin(k * Math.PI / 8) * r);
				int[] hs = new int[25];
				int n = 0;
				double wet = 0;
				for (int dx = -6; dx <= 6; dx += 3)
					for (int dz = -6; dz <= 6; dz += 3) {
						int h = ground(level, x + dx, z + dz);
						hs[n++] = h;
						if (!level.getFluidState(new BlockPos(x + dx, h, z + dz)).isEmpty()) wet += 100;
					}
				Arrays.sort(hs);
				double score = hs[24] - hs[0] + wet + r * 0.05;
				if (score < low) {
					low = score;
					best = new BlockPos(x, hs[12], z);
				}
			}
		return best;
	}

	private static int ground(ServerLevel level, int x, int z) {
		return level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z) - 1;
	}

	static void place(ServerLevel level, BlockPos at, Vec3 way) {
		Vec3 side = new Vec3(-way.z, 0, way.x);
		Vec3 foot = Vec3.atBottomCenterOf(at.above());
		flatten(level, at, 5);
		flatten(level, BlockPos.containing(foot.add(way.scale(4))).atY(at.getY()), 4);
		clear(level, BlockPos.containing(foot.add(way.scale(8))).atY(at.getY()));
		cart(level, foot, way);
		for (int s = -1; s <= 1; s += 2) horse(level, foot.add(way.scale(3.5)).add(side.scale(s * 1.05)), way, s < 0 ? 0x101 : 0x204);
		Vec3 him = foot.add(side.scale(2.8)).add(way.scale(0.6));
		Talk.spawn(level, KIND, "", "stand", him.x, him.y, him.z, yaw(side.reverse()));
	}

	/** Ground round the wagon levelled at its own height, so nothing stands on a slope or in a bush. */
	private static void flatten(ServerLevel level, BlockPos c, int r) {
		int h = c.getY();
		for (int dx = -r; dx <= r; dx++)
			for (int dz = -r; dz <= r; dz++) {
				if (dx * dx + dz * dz > r * r) continue;
				int x = c.getX() + dx, z = c.getZ() + dz, top = ground(level, x, z);
				for (int y = h + 1; y <= Math.max(top, h + 3); y++) level.setBlock(new BlockPos(x, y, z), Blocks.AIR.defaultBlockState(), 2);
				for (int y = top; y < h; y++) level.setBlock(new BlockPos(x, y, z), Blocks.DIRT.defaultBlockState(), 2);
				level.setBlock(new BlockPos(x, h, z), Blocks.GRASS_BLOCK.defaultBlockState(), 2);
			}
	}

	/** Trees out of the way of the road ahead: the gates of the vision stand there. */
	private static void clear(ServerLevel level, BlockPos c) {
		for (int dx = -CLEARING; dx <= CLEARING; dx++)
			for (int dz = -CLEARING; dz <= CLEARING; dz++) {
				if (dx * dx + dz * dz > CLEARING * CLEARING) continue;
				for (int y = c.getY() - 4; y <= c.getY() + TREE_TOP; y++) {
					BlockPos p = new BlockPos(c.getX() + dx, y, c.getZ() + dz);
					BlockState s = level.getBlockState(p);
					if (s.is(BlockTags.LOGS) || s.is(BlockTags.LEAVES) || s.getBlock() instanceof LeavesBlock) level.setBlock(p, Blocks.AIR.defaultBlockState(), 2);
				}
			}
	}

	/** The cart's model has its shafts down -Z. */
	private static void cart(ServerLevel level, Vec3 foot, Vec3 way) {
		var d = EntityType.BLOCK_DISPLAY.create(level);
		if (d == null) return;
		float half = (float) Math.atan2(-way.x, -way.z) / 2;
		CompoundTag t = new CompoundTag(), tr = new CompoundTag();
		t.put("block_state", net.minecraft.nbt.NbtUtils.writeBlockState(BuiltInRegistries.BLOCK.get(CART).defaultBlockState()));
		tr.put("left_rotation", Capital.floats(0, Mth.sin(half), 0, Mth.cos(half)));
		tr.put("right_rotation", Capital.floats(0, 0, 0, 1));
		tr.put("translation", Capital.floats(0, 0, 0));
		tr.put("scale", Capital.floats(1, 1, 1));
		t.put("transformation", tr);
		t.putFloat("view_range", 4f);
		d.load(t);
		d.moveTo(foot.x, foot.y, foot.z, 0, 0);
		d.addTag(TAG);
		level.addFreshEntity(d);
	}

	private static void horse(ServerLevel level, Vec3 at, Vec3 way, int coat) {
		Horse h = EntityType.HORSE.create(level);
		if (h == null) return;
		h.moveTo(at.x, at.y, at.z, yaw(way), 0);
		h.setYHeadRot(yaw(way));
		h.setYBodyRot(yaw(way));
		h.setNoAi(true);
		h.setSilent(true);
		h.setInvulnerable(true);
		h.setPersistenceRequired();
		h.addTag(TAG);
		CompoundTag t = new CompoundTag();
		h.addAdditionalSaveData(t);
		t.putInt("Variant", coat);
		h.readAdditionalSaveData(t);
		level.addFreshEntity(h);
	}

	// ---------------------------------------------------------------- watching

	/** `npc` null: only you (/ashbound intro). */
	public static void start(ServerPlayer p, Npc npc) {
		ServerLevel level = p.serverLevel();
		State st = State.get(p.server.overworld());
		int[] c = Capital.centre();
		BlockPos at = st.placed ? new BlockPos(st.x, st.y, st.z) : p.blockPosition();
		Net.IntroPlay m = new Net.IntroPlay(at, st.placed ? st.yaw : p.getYRot(), c != null, c == null ? 0 : c[0], c == null ? 0 : c[1]);
		long ends = p.server.getTickCount() + LENGTH + LATE;
		for (ServerPlayer q : level.players()) {
			boolean with = q == p || npc != null && q.distanceToSqr(npc) < NEAR * NEAR && !Coins.flag(q, SEEN) && Classes.of(q) != null && Mounts.of(q) != null;
			if (!with) continue;
			WATCHING.put(q.getUUID(), ends);
			PacketDistributor.sendToPlayer(q, m);
		}
	}

	/** The scene's over on their screen, or it was skipped. */
	public static void done(ServerPlayer p) {
		if (WATCHING.remove(p.getUUID()) == null) return;
		Coins.setFlag(p, SEEN);
		int[] c = Capital.centre();
		if (c != null) p.sendSystemMessage(Component.literal("Highmourn lies at X " + c[0] + ", Z " + c[1] + ". The compass points the way.").withStyle(ChatFormatting.GOLD));
	}

	private static void tick(ServerTickEvent.Post e) {
		if (e.getServer().getTickCount() % 20 != 7 || e.getServer().getPlayerList().getPlayers().isEmpty()) return;
		ServerLevel level = e.getServer().overworld();
		if (!State.get(level).placed) set(level);
		long now = e.getServer().getTickCount();
		for (Iterator<Map.Entry<UUID, Long>> it = WATCHING.entrySet().iterator(); it.hasNext();)
			if (it.next().getValue() < now) it.remove();
		for (ServerPlayer p : e.getServer().getPlayerList().getPlayers()) {
			if (Coins.flag(p, HINT) || Coins.flag(p, SEEN) || Coins.flag(p, "found_capital") || Classes.of(p) == null || Mounts.of(p) == null) continue;
			Coins.setFlag(p, HINT);
			p.sendSystemMessage(Component.literal("A wagoner has stopped on the road near you. He's waving you over.").withStyle(ChatFormatting.GOLD));
		}
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener(Intro::tick);
		NeoForge.EVENT_BUS.addListener((LivingIncomingDamageEvent e) -> {
			if (WATCHING.containsKey(e.getEntity().getUUID())) e.setCanceled(true);
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedOutEvent e) -> WATCHING.remove(e.getEntity().getUUID()));
		// the horses stay in harness
		NeoForge.EVENT_BUS.addListener((PlayerInteractEvent.EntityInteract e) -> {
			if (e.getTarget().getTags().contains(TAG)) {
				e.setCancellationResult(InteractionResult.SUCCESS);
				e.setCanceled(true);
			}
		});
		NeoForge.EVENT_BUS.addListener((RegisterCommandsEvent e) -> e.getDispatcher().register(Commands.literal("ashbound")
				.requires(s -> s.hasPermission(2))
				.then(Commands.literal("intro").executes(c -> {
					start(c.getSource().getPlayerOrException(), null);
					return Command.SINGLE_SUCCESS;
				}))));
	}
}
