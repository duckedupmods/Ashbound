package com.snoringwalrus.ashbound;

import java.io.DataInputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.zip.GZIPInputStream;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.brigadier.arguments.StringArgumentType;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitlesAnimationPacket;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.RandomizableContainerBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.storage.loot.BuiltInLootTables;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.EventHooks;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/**
 * The gate dungeons: each a block file made in E:\Ashbound (tools/silk.py --game and the like: data/ashbound/lair/
 * NAME.bin and NAME.json), built in the gates dimension (data/ashbound/dimension/gates.json: a void) a few chunks
 * a tick, then stocked: its monsters at their "mob:TYPE:N" points, its boss at "boss", its chests filled. A gate
 * whose dungeon is built takes you in (GateEntity), the build holding you in the tear while it goes up; standing on
 * its "exit" point takes you back out where you came in.
 *
 * Ported from the old mod's Lair (Fabric 26.3), cut down to what the gates need.
 */
public final class Lairs {
	private Lairs() {}

	/** The void the gate dungeons hang in. */
	public static final ResourceKey<Level> GATES = ResourceKey.create(Registries.DIMENSION, ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "gates"));
	public static final List<String> KNOWN = known();

	/** The hand-ported lairs, then every Roster v2 one gear.json says is built (tools/newgate.py). */
	private static List<String> known() {
		List<String> out = new ArrayList<>(List.of("gate_silk", "gate_cellar", "gate_gallows", "gate_rotwood", "gate_crypt", "gate_plague",
				"gate_foundry", "gate_ossuary", "gate_frost", "gate_temple"));
		try (java.io.InputStream in = Lairs.class.getResourceAsStream("/ashbound/gear.json")) {
			if (in != null)
				for (com.google.gson.JsonElement el : com.google.gson.JsonParser.parseReader(
						new java.io.InputStreamReader(in, java.nio.charset.StandardCharsets.UTF_8)).getAsJsonArray()) {
					com.google.gson.JsonObject g = el.getAsJsonObject();
					if (g.has("lair") && !out.contains(g.get("lair").getAsString())) out.add(g.get("lair").getAsString());
				}
		} catch (Exception e) {
			Ashbound.LOG.error("roster v2 lairs not listed", e);
		}
		return List.copyOf(out);
	}
	private static final int FLAGS = Block.UPDATE_CLIENTS | Block.UPDATE_KNOWN_SHAPE;
	private static final String DWELLER = "ashbound_dweller", BACK = "ashbound_gate_back";
	private static final Map<String, Lair> LAIRS = new ConcurrentHashMap<>();
	/** Dungeons whose boss is down, by name, till the last one's out and the gates into them have closed. */
	private static final Map<String, Clearing> CLEARED = new HashMap<>();
	/** How many seconds an emptied dungeon waits for a gate to load, the one you came in by being wherever you've just landed. */
	private static final int GATE_WAIT = 30;

	private static final class Clearing {
		final Set<UUID> gates = new HashSet<>();
		int waited;
	}
	private static Job job;

	static final class Lair {
		final String name;
		String title = "the dungeon", arrive, arriveSub;
		BlockPos origin = BlockPos.ZERO;
		int clearTop = 40, rank;
		ResourceLocation boss, loot;
		BlockPos checkAt;
		Block checkBlock;
		Data data;

		Lair(String name) {
			this.name = name;
		}

		Vec3 world(Vec3 rel) {
			return new Vec3(origin.getX() + rel.x, origin.getY() + rel.y, origin.getZ() + rel.z);
		}

		boolean built(ServerLevel level) {
			return checkAt != null && level.getBlockState(origin.offset(checkAt)).is(checkBlock);
		}
	}

	/** Its blocks, sorted by chunk, and its named points. */
	static final class Data {
		BlockState[] palette;
		final Map<String, Vec3> points = new HashMap<>();
		int[] xs, ys, zs, st;
		final Map<Long, int[]> chunks = new LinkedHashMap<>();
		final Map<Long, Integer> colMin = new HashMap<>();
		int minX = Integer.MAX_VALUE, maxX = Integer.MIN_VALUE, minY = Integer.MAX_VALUE, maxY = Integer.MIN_VALUE,
				minZ = Integer.MAX_VALUE, maxZ = Integer.MIN_VALUE;

		boolean contains(BlockPos origin, BlockPos p) {
			int x = p.getX() - origin.getX(), y = p.getY() - origin.getY(), z = p.getZ() - origin.getZ();
			return x >= minX && x <= maxX && y >= minY - 2 && y <= maxY + 2 && z >= minZ && z <= maxZ;
		}
	}

	/** Each dungeon's build, numbered (the game time it was stocked) and kept with the world. Everything a build puts in
	 *  carries its number: a dweller of an older build, saved in a chunk nobody had loaded when the dungeon was rebuilt
	 *  (so stock() never saw it), is turned away when it loads, or there'd be two of every monster, boss and coffer. */
	static final class Builds extends SavedData {
		final Map<String, Long> now = new HashMap<>();

		static Builds get(ServerLevel level) {
			return level.getDataStorage().computeIfAbsent(new SavedData.Factory<>(Builds::new, Builds::load, null), "ashbound_lair_builds");
		}

		static Builds load(CompoundTag tag, HolderLookup.Provider p) {
			Builds b = new Builds();
			for (String k : tag.getAllKeys()) b.now.put(k, tag.getLong(k));
			return b;
		}

		@Override
		public CompoundTag save(CompoundTag tag, HolderLookup.Provider p) {
			now.forEach(tag::putLong);
			return tag;
		}
	}

	private static final String BUILD = "ashbound_build:";

	private static String buildTag(ServerLevel level, Lair l) {
		return BUILD + l.name + ":" + Builds.get(level).now.getOrDefault(l.name, 0L);
	}

	/** A dungeon's monster or way-out gate loading from disk: an older build's is dropped (Builds). */
	private static void joined(EntityJoinLevelEvent e) {
		if (!e.loadedFromDisk() || !(e.getLevel() instanceof ServerLevel level) || level.dimension() != GATES) return;
		Entity en = e.getEntity();
		if (!en.getTags().contains(DWELLER) && !(en instanceof GateEntity)) return;
		String name = null;
		long was = -1;   // put in before builds were numbered
		for (String t : en.getTags())
			if (t.startsWith(BUILD)) {
				int c = t.lastIndexOf(':');
				name = t.substring(BUILD.length(), c);
				was = Long.parseLong(t.substring(c + 1));
			}
		if (name == null)
			for (String n : KNOWN) {
				Lair l = get(n);
				if (l != null && l.data != null && l.data.contains(l.origin, en.blockPosition())) name = n;
			}
		Long now = name == null ? null : Builds.get(level).now.get(name);
		if (now != null && now != was) {
			e.setCanceled(true);
			Ashbound.LOG.info("{} from an older build of {} left out", en.getType().toShortString(), name);
		}
	}

	private static final class Job {
		final Lair lair;
		final ServerLevel level;
		final Set<UUID> waiting = new LinkedHashSet<>();
		final List<Map.Entry<Long, int[]>> todo;
		int done, ticks;
		final long started = System.currentTimeMillis();

		Job(Lair lair, ServerLevel level) {
			this.lair = lair;
			this.level = level;
			this.todo = new ArrayList<>(lair.data.chunks.entrySet());
		}
	}

	public static void register() {
		NeoForge.EVENT_BUS.addListener((RegisterCommandsEvent e) -> e.getDispatcher().register(Commands.literal("ashbound")
				.requires(s -> s.hasPermission(2))
				.then(Commands.literal("lair").then(Commands.argument("name", StringArgumentType.word())
						.suggests((c, b) -> SharedSuggestionProvider.suggest(KNOWN, b))
						.executes(c -> command(c.getSource(), StringArgumentType.getString(c, "name"), false))
						.then(Commands.literal("rebuild").executes(c -> command(c.getSource(), StringArgumentType.getString(c, "name"), true)))))));
		NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post e) -> tick(e.getServer()));
		NeoForge.EVENT_BUS.addListener((LivingDeathEvent e) -> bossDown(e.getEntity()));
		NeoForge.EVENT_BUS.addListener(Lairs::joined);
		// dead inside: back out in front of the gate you came in by. What's kept on you doesn't outlive the body by itself
		NeoForge.EVENT_BUS.addListener((PlayerEvent.Clone e) -> {
			CompoundTag back = e.getOriginal().getPersistentData().getCompound(BACK);
			if (e.isWasDeath() && e.getOriginal().level().dimension() == GATES && !back.isEmpty()) e.getEntity().getPersistentData().put(BACK, back);
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerRespawnEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer p && !e.isEndConquered() && p.getPersistentData().contains(BACK)) leave(p);
		});
	}

	// ---------------------------------------------------------------- going in and out

	private static int command(CommandSourceStack src, String name, boolean rebuild) {
		ServerPlayer p = src.getPlayer();
		Lair l = get(name);
		if (l == null || l.data == null) {
			src.sendFailure(Component.literal("There's no dungeon called " + name));
			return 0;
		}
		if (p == null) return 0;
		enter(p, name, rebuild);
		return 1;
	}

	/** Through a gate (or by command): in at once if it's built and stocked, otherwise it's raised while you wait. */
	public static void enter(ServerPlayer p, String name) {
		enter(p, name, false);
	}

	/** By this gate, which closes behind the last one out once the boss is down. */
	static void enter(ServerPlayer p, String name, GateEntity gate) {
		enter(p, name, false);
		if (p.getPersistentData().contains(BACK)) p.getPersistentData().getCompound(BACK).putUUID("gate", gate.getUUID());
	}

	private static void enter(ServerPlayer p, String name, boolean rebuild) {
		Lair l = get(name);
		ServerLevel level = p.server.getLevel(GATES);
		if (l == null || l.data == null || level == null) return;
		remember(p);
		if (job != null) {
			if (job.lair == l) job.waiting.add(p.getUUID());
			else p.displayClientMessage(Component.literal("The gate is unstable... try again in a moment"), true);
			return;
		}
		if (!rebuild && l.built(level)) {
			arrive(p, l, level);
			return;
		}
		job = new Job(l, level);
		job.waiting.add(p.getUUID());
	}

	/** A gate onto it has just torn open: raised fresh now, so it stands ready by the time anyone walks in. */
	public static void prepare(MinecraftServer server, String name) {
		Lair l = get(name);
		ServerLevel level = server.getLevel(GATES);
		if (l == null || l.data == null || level == null || job != null) return;
		for (ServerPlayer o : level.players()) if (l.data.contains(l.origin, o.blockPosition())) return;   // someone's in there
		job = new Job(l, level);
	}

	/** Where you were before you went in, kept on you, so the exit takes you back there. */
	private static void remember(ServerPlayer p) {
		if (p.level().dimension() == GATES) return;
		CompoundTag t = new CompoundTag();
		t.putString("dim", p.level().dimension().location().toString());
		t.putDouble("x", p.getX());
		t.putDouble("y", p.getY());
		t.putDouble("z", p.getZ());
		t.putFloat("yaw", p.getYRot());
		p.getPersistentData().put(BACK, t);
	}

	static void leave(ServerPlayer p) {
		CompoundTag t = p.getPersistentData().getCompound(BACK);
		ServerLevel to = t.contains("dim") ? p.server.getLevel(ResourceKey.create(Registries.DIMENSION, ResourceLocation.parse(t.getString("dim")))) : null;
		if (to == null) {
			to = p.server.overworld();
			BlockPos s = to.getSharedSpawnPos();
			p.teleportTo(to, s.getX() + 0.5, s.getY(), s.getZ() + 0.5, p.getYRot(), 0f);
		} else {
			float yaw = t.getFloat("yaw") + 180f;                       // out of the tear, facing away, clear of its face
			Vec3 step = Vec3.directionFromRotation(0, yaw).scale(2.5);
			p.teleportTo(to, t.getDouble("x") + step.x, t.getDouble("y"), t.getDouble("z") + step.z, yaw, 0f);
		}
		p.getPersistentData().remove(BACK);
	}

	private static void arrive(ServerPlayer p, Lair l, ServerLevel level) {
		Vec3 at = l.world(l.data.points.getOrDefault("tp", Vec3.ZERO));
		p.teleportTo(level, at.x, at.y, at.z, 180f, 10f);
		if (l.arrive != null) {
			p.connection.send(new ClientboundSetTitlesAnimationPacket(10, 60, 20));
			p.connection.send(new ClientboundSetTitleTextPacket(Component.literal(l.arrive).withStyle(ChatFormatting.AQUA, ChatFormatting.BOLD)));
			p.connection.send(new ClientboundSetSubtitleTextPacket(Component.literal(l.arriveSub).withStyle(ChatFormatting.GRAY)));
		}
	}

	// ---------------------------------------------------------------- building

	/** Nobody left in a cleared dungeon: what opened onto it goes, as it would if it had run out its time. */
	private static void closeCleared(MinecraftServer server) {
		ServerLevel level = server.getLevel(GATES);
		if (level == null) return;
		for (Iterator<Map.Entry<String, Clearing>> it = CLEARED.entrySet().iterator(); it.hasNext();) {
			var e = it.next();
			Lair l = get(e.getKey());
			Clearing c = e.getValue();
			boolean inside = false;
			for (ServerPlayer p : level.players()) {
				if (!l.data.contains(l.origin, p.blockPosition())) continue;
				inside = true;
				CompoundTag back = p.getPersistentData().getCompound(BACK);
				if (back.hasUUID("gate")) c.gates.add(back.getUUID("gate"));
			}
			if (inside) continue;
			c.gates.removeIf(id -> {
				for (ServerLevel w : server.getAllLevels())
					if (w.getEntity(id) instanceof GateEntity g) {
						g.close();
						return true;
					}
				return false;
			});
			if (c.gates.isEmpty() || ++c.waited > GATE_WAIT) it.remove();
		}
	}

	private static void tick(MinecraftServer server) {
		if (server.getTickCount() % 100 == 0) keepElites(server);
		if (server.getTickCount() % 20 == 0) closeCleared(server);
		Job j = job;
		if (j == null) return;
		long until = System.nanoTime() + 30_000_000L;
		while (!j.todo.isEmpty() && System.nanoTime() < until) {
			Map.Entry<Long, int[]> e = j.todo.remove(j.todo.size() - 1);
			place(j.level, j.lair, e.getKey(), e.getValue());
			j.done++;
		}
		if (j.ticks++ % 10 == 0) {
			int pct = j.done * 100 / Math.max(1, j.lair.data.chunks.size());
			for (UUID u : j.waiting) {
				ServerPlayer p = server.getPlayerList().getPlayer(u);
				if (p == null) continue;
				p.displayClientMessage(Component.literal("The gate is opening... " + pct + "%").withStyle(ChatFormatting.DARK_AQUA, ChatFormatting.ITALIC), true);
				p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 20, 4, false, false));
			}
		}
		if (!j.todo.isEmpty()) return;
		job = null;
		stock(j);
		Ashbound.LOG.info("{} built in {} s", j.lair.title, (System.currentTimeMillis() - j.started) / 1000);
		for (UUID u : j.waiting) {
			ServerPlayer p = server.getPlayerList().getPlayer(u);
			if (p != null) arrive(p, j.lair, j.level);
		}
	}

	/** One chunk: its columns cleared up to clear_top above the origin, then its blocks set. */
	private static void place(ServerLevel level, Lair l, long key, int[] range) {
		Data d = l.data;
		int rcx = (int) (key >> 32), rcz = (int) key, ox = l.origin.getX(), oy = l.origin.getY(), oz = l.origin.getZ();
		level.getChunk((ox >> 4) + rcx, (oz >> 4) + rcz);
		BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
		BlockState air = Blocks.AIR.defaultBlockState();
		int top = Math.min(level.getMaxBuildHeight() - 1, oy + l.clearTop);
		for (int i = 0; i < 16; i++)
			for (int k = 0; k < 16; k++) {
				int rx = rcx * 16 + i, rz = rcz * 16 + k;
				Integer m = d.colMin.get(col(rx, rz));
				if (m == null) continue;
				for (int y = oy + m; y <= top; y++) {
					pos.set(ox + rx, y, oz + rz);
					if (!level.getBlockState(pos).isAir()) level.setBlock(pos, air, FLAGS);
				}
			}
		for (int n = range[0]; n < range[1]; n++) {
			pos.set(ox + d.xs[n], oy + d.ys[n], oz + d.zs[n]);
			level.setBlock(pos, d.palette[d.st[n]], FLAGS);
		}
	}

	/** Built: the last build's monsters taken away, the new ones and the boss put in, the chests filled. */
	private static void stock(Job j) {
		ServerLevel level = j.level;
		Lair l = j.lair;
		Vec3 o = Vec3.atLowerCornerOf(l.origin);
		AABB all = new AABB(o, o).inflate(400, 120, 400);
		for (Mob old : level.getEntitiesOfClass(Mob.class, all, m -> m.getTags().contains(DWELLER))) old.discard();
		for (GateEntity old : level.getEntitiesOfClass(GateEntity.class, all)) old.discard();
		Builds builds = Builds.get(level);
		builds.now.put(l.name, level.getGameTime());
		builds.setDirty();
		String build = buildTag(level, l);
		boolean boss = l.boss != null && BuiltInRegistries.ENTITY_TYPE.containsKey(l.boss);
		if (!boss && l.data.points.containsKey("exit")) wayOut(level, l, l.world(l.data.points.get("exit")), 0f);
		for (Map.Entry<String, Vec3> pt : l.data.points.entrySet()) {
			String k = pt.getKey();
			Vec3 at = l.world(pt.getValue());
			BlockPos bp = BlockPos.containing(at);
			level.getChunk(bp.getX() >> 4, bp.getZ() >> 4);
			if (k.startsWith("mob:") || k.equals("boss") && l.boss != null) {
				float yaw = level.getRandom().nextFloat() * 360f;
				String id;
				// a trailing "!": only a statue, it never wakes
				boolean decor = k.endsWith("!");
				if (decor) k = k.substring(0, k.length() - 1);
				if (k.equals("boss")) {
					id = l.boss.toString();
					yaw = 0f;
				} else {
					if (k.contains("@")) {
						yaw = Float.parseFloat(k.substring(k.indexOf('@') + 1));
						k = k.substring(0, k.indexOf('@'));
					}
					id = k.substring(4, k.lastIndexOf(':'));
				}
				EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.getOptional(ResourceLocation.parse(id)).orElse(null);
				Entity e = type != null ? type.create(level) : null;
				if (e == null) continue;                            // not in the game yet
				e.moveTo(at.x, at.y, at.z, yaw, 0f);
				e.addTag(DWELLER);
				e.addTag(build);
				if (e instanceof Mob m) {
					m.setYBodyRot(yaw);
					m.setYHeadRot(yaw);
					m.setPersistenceRequired();
					EventHooks.finalizeMobSpawn(m, level, level.getCurrentDifficultyAt(bp), MobSpawnType.STRUCTURE, null);
					if (decor) {
						m.addTag("ashbound_decor");
						m.setNoAi(true);
					}
				}
				level.addFreshEntity(e);
			} else if (k.startsWith("loot:") && SilkProps.stocked(level, bp) instanceof RandomizableContainerBlockEntity c) {
				c.setLootTable(l.loot == null ? BuiltInLootTables.SIMPLE_DUNGEON
						: ResourceKey.create(Registries.LOOT_TABLE, l.loot), level.getRandom().nextLong());
			}
		}
	}

	private static boolean hasSeal(Lair l) {
		return l.data.points.keySet().stream().anyMatch(k -> k.startsWith("seal:"));
	}

	/** the "mob:" points whose monster holds the dungeon's key */
	private static List<Map.Entry<String, Vec3>> elites(Lair l) {
		List<Map.Entry<String, Vec3>> out = new java.util.ArrayList<>();
		for (Map.Entry<String, Vec3> e : l.data.points.entrySet()) {
			String k = e.getKey();
			if (!k.startsWith("mob:") || k.endsWith("!")) continue;
			String id = k.substring(4, k.lastIndexOf(':'));
			if (id.contains("@")) id = id.substring(0, id.indexOf('@'));
			String path = id.substring(id.indexOf(':') + 1);
			for (GateMobs.Kind kind : GateMobs.KINDS)
				if (kind.key() && kind.id().equals(path)) out.add(e);
		}
		return out;
	}

	private static boolean hasElite(Lair l) {
		return !elites(l).isEmpty();
	}

	/**
	 * Every few seconds, for each dungeon someone is in: if its way to the boss is still shut (a seal standing, or the
	 * boss still warded) and its elite is nowhere (it never got put in - a build that broke off - or it fell out of the
	 * world), the elite comes back to its place.
	 */
	private static void keepElites(MinecraftServer server) {
		ServerLevel level = server.getLevel(GATES);
		if (level == null || level.players().isEmpty()) return;
		for (String n : KNOWN) {
			Lair l = get(n);
			if (l == null || l.data == null) continue;
			if (level.players().stream().noneMatch(p -> l.data.contains(l.origin, p.blockPosition()))) continue;
			List<Map.Entry<String, Vec3>> el = elites(l);
			if (el.isEmpty()) continue;
			Vec3 o = Vec3.atLowerCornerOf(l.origin);
			AABB all = new AABB(o.add(l.data.minX, l.data.minY - 4, l.data.minZ), o.add(l.data.maxX + 1, l.data.maxY + 4, l.data.maxZ + 1));
			boolean shut = false;
			for (Map.Entry<String, Vec3> e : l.data.points.entrySet())
				if (e.getKey().startsWith("seal:") && !level.getBlockState(BlockPos.containing(l.world(e.getValue()).add(0.5, 0.5, 0.5))).isAir()) {
					shut = true;
					break;
				}
			if (!shut) shut = !level.getEntitiesOfClass(Mob.class, all, m -> m instanceof MobSkills.User u && u.state().warded && m.isAlive()).isEmpty();
			if (!shut) continue;
			boolean alive = !level.getEntitiesOfClass(Mob.class, all, m -> m.isAlive() && m instanceof MobSkills.User u && u.kind().key()
					&& !m.getTags().contains("ashbound_decor")).isEmpty();
			if (alive) continue;
			for (Map.Entry<String, Vec3> e : el) {
				String k = e.getKey();
				String id = k.substring(4, k.lastIndexOf(':'));
				if (id.contains("@")) id = id.substring(0, id.indexOf('@'));
				Vec3 at = l.world(e.getValue());
				EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.getOptional(ResourceLocation.parse(id)).orElse(null);
				if (type == null || !(type.create(level) instanceof Mob m)) continue;
				m.moveTo(at.x, at.y, at.z, level.getRandom().nextFloat() * 360f, 0f);
				m.addTag(DWELLER);
				m.setPersistenceRequired();
				EventHooks.finalizeMobSpawn(m, level, level.getCurrentDifficultyAt(BlockPos.containing(at)), MobSpawnType.STRUCTURE, null);
				level.addFreshEntity(m);
				Ashbound.LOG.info("{}: its elite {} was missing, put back", l.title, id);
			}
		}
	}

	/** A gate standing open inside the dungeon, back to wherever you came in from. */
	private static void wayOut(ServerLevel level, Lair l, Vec3 at, float yaw) {
		GateEntity g = Gates.spawn(level, at, yaw, Math.max(0, l.rank));
		if (g == null) return;
		g.makeWayOut();
		g.addTag(buildTag(level, l));
	}

	/** A gate's key-holder fell near `near`: whatever stands on that dungeon's "seal:N" points (its bars, its roots) gives way. */
	static void openSeal(ServerLevel level, BlockPos near) {
		if (level.dimension() != GATES) return;
		for (String n : KNOWN) {
			Lair l = get(n);
			if (l == null || l.data == null || !l.data.contains(l.origin, near)) continue;
			Vec3 first = null;
			for (Map.Entry<String, Vec3> e : l.data.points.entrySet()) {
				if (!e.getKey().startsWith("seal:")) continue;
				BlockPos p = BlockPos.containing(l.world(e.getValue()).add(0.5, 0.5, 0.5));
				BlockState was = level.getBlockState(p);
				if (was.isAir()) continue;
				level.destroyBlock(p, false);
				if (first == null) first = Vec3.atCenterOf(p);
			}
			if (first == null) continue;
			level.playSound(null, BlockPos.containing(first), net.minecraft.sounds.SoundEvents.IRON_DOOR_OPEN, net.minecraft.sounds.SoundSource.BLOCKS, 2f, 0.5f);
			for (ServerPlayer p : level.players())
				if (p.distanceToSqr(first) < 64 * 64) p.displayClientMessage(Component.literal("The way ahead opens").withStyle(ChatFormatting.GOLD), true);
		}
	}

	/** The boss falls: a gate tears open on its exit point, the way home. */
	private static void bossDown(LivingEntity dead) {
		if (!(dead.level() instanceof ServerLevel level) || level.dimension() != GATES || !dead.getTags().contains(DWELLER)) return;
		for (String n : KNOWN) {
			Lair l = get(n);
			if (l == null || l.data == null || l.boss == null || !l.boss.equals(BuiltInRegistries.ENTITY_TYPE.getKey(dead.getType()))) continue;
			Vec3 ex = l.data.points.get("exit");
			if (ex != null) wayOut(level, l, l.world(ex), 0f);
			CLEARED.computeIfAbsent(n, k -> new Clearing());
		}
	}

	// ---------------------------------------------------------------- loading

	/** Where a dungeon's blocks go, one by one (relative to its origin): GateWindow, DungeonRun, the gate's ground. */
	public interface BlockSink {
		void put(int x, int y, int z, BlockState s);
	}

	/** Every block of the dungeon `name` (from its file; it needn't be built). False if there's no such dungeon. */
	public static boolean blocks(String name, BlockSink sink) {
		Lair l = get(name);
		if (l == null || l.data == null) return false;
		Data d = l.data;
		for (int i = 0; i < d.xs.length; i++) sink.put(d.xs[i], d.ys[i], d.zs[i], d.palette[d.st[i]]);
		return true;
	}

	/** Its named points ("tp", "boss", "mob:TYPE:N", ...), relative to its origin; empty if there's no such dungeon. */
	public static Map<String, Vec3> points(String name) {
		Lair l = get(name);
		return l == null || l.data == null ? Map.of() : java.util.Collections.unmodifiableMap(l.data.points);
	}

	/** Its boss's entity type, or null. */
	public static ResourceLocation boss(String name) {
		Lair l = get(name);
		return l == null ? null : l.boss;
	}

	static Lair get(String name) {
		Lair have = LAIRS.get(name);
		if (have != null) return have;
		try (InputStream in = Lairs.class.getResourceAsStream("/data/ashbound/lair/" + name + ".json")) {
			if (in == null) return null;
			JsonObject j = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
			Lair l = new Lair(name);
			if (j.has("title")) l.title = j.get("title").getAsString();
			if (j.has("arrive")) {
				l.arrive = j.getAsJsonArray("arrive").get(0).getAsString();
				l.arriveSub = j.getAsJsonArray("arrive").get(1).getAsString();
			}
			JsonArray a = j.getAsJsonArray("test_origin");
			l.origin = new BlockPos(a.get(0).getAsInt(), a.get(1).getAsInt(), a.get(2).getAsInt());
			if (j.has("rank")) l.rank = java.util.Arrays.asList(GateEntity.RANKS).indexOf(j.get("rank").getAsString());
			if (j.has("clear_top")) l.clearTop = j.get("clear_top").getAsInt();
			if (j.has("boss")) l.boss = ResourceLocation.parse(j.get("boss").getAsString());
			if (j.has("loot")) l.loot = ResourceLocation.parse(j.get("loot").getAsString());
			if (j.has("built_check")) {
				JsonArray c = j.getAsJsonArray("built_check").get(0).getAsJsonArray();
				l.checkAt = new BlockPos(c.get(0).getAsInt(), c.get(1).getAsInt(), c.get(2).getAsInt());
				l.checkBlock = BuiltInRegistries.BLOCK.get(ResourceLocation.parse(c.get(3).getAsString()));
			}
			l.data = data(name);
			LAIRS.put(name, l);
			return l;
		} catch (Exception e) {
			Ashbound.LOG.error("Couldn't load dungeon " + name, e);
			return null;
		}
	}

	static long col(int x, int z) {
		return ((long) x << 32) | (z & 0xFFFFFFFFL);
	}

	private static Data data(String name) throws java.io.IOException {
		try (InputStream in = Lairs.class.getResourceAsStream("/data/ashbound/lair/" + name + ".bin")) {
			if (in == null) return null;
			DataInputStream s = new DataInputStream(new GZIPInputStream(in));
			byte[] magic = new byte[4];
			s.readFully(magic);
			if (!new String(magic).equals("KILN")) return null;
			Data d = new Data();
			d.palette = new BlockState[s.readUnsignedShort()];
			for (int i = 0; i < d.palette.length; i++) {
				String st = str(s);
				if (st.endsWith("#flow")) st = st.substring(0, st.length() - 5);
				try {
					d.palette[i] = BlockStateParser.parseForBlock(BuiltInRegistries.BLOCK.asLookup(), st, false).blockState();
				} catch (Exception e) {
					Ashbound.LOG.warn("dungeon {}: unknown block {}, left as air", name, st);
					d.palette[i] = Blocks.AIR.defaultBlockState();
				}
			}
			int np = s.readUnsignedShort();
			for (int i = 0; i < np; i++) d.points.put(str(s), new Vec3(s.readDouble(), s.readDouble(), s.readDouble()));
			int n = s.readInt();
			d.xs = new int[n];
			d.ys = new int[n];
			d.zs = new int[n];
			d.st = new int[n];
			long last = Long.MIN_VALUE;
			int from = 0;
			for (int i = 0; i < n; i++) {
				int x = s.readShort(), y = s.readShort(), z = s.readShort(), p = s.readUnsignedShort();
				d.xs[i] = x;
				d.ys[i] = y;
				d.zs[i] = z;
				d.st[i] = p;
				d.minX = Math.min(d.minX, x);
				d.maxX = Math.max(d.maxX, x);
				d.minY = Math.min(d.minY, y);
				d.maxY = Math.max(d.maxY, y);
				d.minZ = Math.min(d.minZ, z);
				d.maxZ = Math.max(d.maxZ, z);
				d.colMin.merge(col(x, z), y, Math::min);
				long ck = col(x >> 4, z >> 4);
				if (ck != last) {
					if (last != Long.MIN_VALUE) d.chunks.put(last, new int[] {from, i});
					last = ck;
					from = i;
				}
			}
			if (last != Long.MIN_VALUE) d.chunks.put(last, new int[] {from, n});
			Ashbound.LOG.info("dungeon {}: {} blocks in {} chunks", name, n, d.chunks.size());
			return d;
		}
	}

	private static String str(DataInputStream s) throws java.io.IOException {
		byte[] b = new byte[s.readUnsignedShort()];
		s.readFully(b);
		return new String(b, StandardCharsets.UTF_8);
	}
}
