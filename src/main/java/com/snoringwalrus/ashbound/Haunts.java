package com.snoringwalrus.ashbound;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.AABB;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.EventHooks;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/**
 * The modpack's structures, held by our monsters (/ashbound/haunts.json, tools/haunts.py). When a player is inside one
 * of them its faction's garrison turns up round them, a few at a time out of their sight, up to a cap that grows
 * with the place's size; the big places get the faction's elite too. Kill the whole garrison and the place stays
 * clear for three days, then a new band moves in. The structure's own monsters (its mod's, vanilla's) stay as well.
 */
public final class Haunts {
	private Haunts() {}

	static final String TAG = "ashbound_haunt";
	static final long REFILL = 3 * 24000;

	record Faction(Map<String, Integer> mobs, String elite) {}

	private static Map<String, Faction> factions;
	private static Map<String, String> exact;
	private static List<Map.Entry<String, String>> prefixes;

	private static void load() {
		if (factions != null) return;
		factions = new HashMap<>();
		exact = new HashMap<>();
		prefixes = new ArrayList<>();
		try (InputStream in = Haunts.class.getResourceAsStream("/ashbound/haunts.json")) {
			JsonObject o = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
			for (var f : o.getAsJsonObject("factions").entrySet()) {
				JsonObject d = f.getValue().getAsJsonObject();
				Map<String, Integer> mobs = new LinkedHashMap<>();
				for (var m : d.getAsJsonObject("mobs").entrySet()) mobs.put(m.getKey(), m.getValue().getAsInt());
				factions.put(f.getKey(), new Faction(mobs, d.has("elite") ? d.get("elite").getAsString() : null));
			}
			for (var s : o.getAsJsonObject("structures").entrySet()) {
				String k = s.getKey(), f = s.getValue().getAsString();
				if (k.endsWith("*")) prefixes.add(Map.entry(k.substring(0, k.length() - 1), f));
				else exact.put(k, f);
			}
			Ashbound.LOG.info("haunts: {} factions in {} structures (+{} kinds by prefix)", factions.size(), exact.size(), prefixes.size());
		} catch (Exception e) {
			Ashbound.LOG.error("haunts.json won't load", e);
		}
	}

	static String factionOf(ResourceLocation id) {
		load();
		String k = id.toString(), f = exact.get(k);
		if (f != null) return f;
		for (var p : prefixes) if (k.startsWith(p.getKey())) return p.getValue();
		return null;
	}

	/** one structure in the world: what holds it and where it is */
	record Haunt(String faction, String key, BoundingBox box, StructureStart start) {
		int cap() {
			int area = box.getXSpan() * box.getZSpan();
			return Math.min(8, 3 + area / 800);
		}

		/** how many come in all before the place is clear: a big place keeps its numbers, they just come in waves */
		int garrison() {
			return Math.min(14, 3 + box.getXSpan() * box.getZSpan() / 500) * 2;
		}

		boolean big() {
			return box.getXSpan() * box.getZSpan() >= 1600;
		}

		String tag() {
			return TAG + ":" + key;
		}
	}

	static Haunt hauntAt(ServerLevel level, BlockPos pos) {
		load();
		var reg = level.registryAccess().registryOrThrow(Registries.STRUCTURE);
		for (Map.Entry<Structure, it.unimi.dsi.fastutil.longs.LongSet> e : level.structureManager().getAllStructuresAt(pos).entrySet()) {
			ResourceLocation id = reg.getKey(e.getKey());
			if (id == null || id.getNamespace().equals(Ashbound.ID)) continue;
			String f = factionOf(id);
			if (f == null || !factions.containsKey(f)) continue;
			StructureStart start = level.structureManager().getStructureAt(pos, e.getKey());
			if (!start.isValid()) continue;
			BoundingBox bb = start.getBoundingBox();
			return new Haunt(f, id + "@" + start.getChunkPos().toLong(), bb, start);
		}
		return null;
	}

	// ---------------------------------------------------------------- what's been sent where, kept with the world

	static final class State extends SavedData {
		/** monsters sent into each place since its last refill */
		final Map<String, Integer> sent = new HashMap<>();
		/** when each place was cleared */
		final Map<String, Long> cleared = new HashMap<>();

		static State get(ServerLevel level) {
			return level.getDataStorage().computeIfAbsent(new SavedData.Factory<>(State::new, State::load, null), "ashbound_haunts");
		}

		static State load(CompoundTag tag, HolderLookup.Provider p) {
			State s = new State();
			CompoundTag a = tag.getCompound("sent"), b = tag.getCompound("cleared");
			for (String k : a.getAllKeys()) s.sent.put(k, a.getInt(k));
			for (String k : b.getAllKeys()) s.cleared.put(k, b.getLong(k));
			return s;
		}

		@Override
		public CompoundTag save(CompoundTag tag, HolderLookup.Provider p) {
			CompoundTag a = new CompoundTag(), b = new CompoundTag();
			sent.forEach(a::putInt);
			cleared.forEach(b::putLong);
			tag.put("sent", a);
			tag.put("cleared", b);
			return tag;
		}
	}

	// ---------------------------------------------------------------- the garrison turning up

	private static void tick(ServerTickEvent.Post e) {
		if (e.getServer().getTickCount() % 60 != 19) return;
		Set<String> served = new HashSet<>();   // a place fills at one speed, however many walk in
		for (ServerPlayer p : e.getServer().getPlayerList().getPlayers()) {
			if (p.isSpectator() || p.isCreative()) continue;
			ServerLevel level = p.serverLevel();
			if (level.getDifficulty() == Difficulty.PEACEFUL) continue;
			Haunt h = hauntAt(level, p.blockPosition());
			if (h == null || !served.add(h.key())) continue;
			State st = State.get(level);
			long now = level.getGameTime();
			Long when = st.cleared.get(h.key());
			if (when != null) {
				if (now - when < REFILL) continue;
				st.cleared.remove(h.key());
				st.sent.remove(h.key());
				st.setDirty();
			}
			int sent = st.sent.getOrDefault(h.key(), 0), alive = alive(level, h);
			if (sent >= h.garrison()) {
				if (alive == 0) {
					st.cleared.put(h.key(), now);
					st.setDirty();
				}
				continue;
			}
			if (alive >= h.cap()) continue;
			Faction f = factions.get(h.faction());
			String kind = h.big() && f.elite() != null && sent == h.garrison() / 2 ? f.elite() : pick(f, level.getRandom());
			if (spawn(level, p, h, kind)) {
				st.sent.put(h.key(), sent + 1);
				st.setDirty();
			}
		}
	}

	private static String pick(Faction f, RandomSource r) {
		int total = 0;
		for (int w : f.mobs().values()) total += w;
		int n = r.nextInt(Math.max(1, total));
		for (var m : f.mobs().entrySet()) if ((n -= m.getValue()) < 0) return m.getKey();
		return f.mobs().keySet().iterator().next();
	}

	static int alive(ServerLevel level, Haunt h) {
		AABB box = AABB.of(h.box()).inflate(16);
		return level.getEntitiesOfClass(Mob.class, box, m -> m.isAlive() && m.getTags().contains(h.tag())).size();
	}

	/** somewhere 10-28 blocks off, inside one of the structure's pieces, on a floor with room to stand, out of sight */
	private static boolean spawn(ServerLevel level, ServerPlayer p, Haunt h, String kind) {
		EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.getOptional(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, kind)).orElse(null);
		if (type == null) return false;
		RandomSource r = level.getRandom();
		int room = (int) Math.ceil(type.getHeight()), wide = type.getWidth() > 1.2f ? 1 : 0;
		for (int t = 0; t < 16; t++) {
			double a = r.nextDouble() * Math.PI * 2, d = 10 + r.nextDouble() * 18;
			int x = p.getBlockX() + (int) Math.round(Math.cos(a) * d), z = p.getBlockZ() + (int) Math.round(Math.sin(a) * d);
			for (int y = p.getBlockY() + 8; y >= p.getBlockY() - 12; y--) {
				BlockPos at = new BlockPos(x, y, z);
				if (!inPiece(h, at) || !stand(level, at, room, wide)) continue;
				if (level.getNearestPlayer(x + 0.5, y + 1, z + 0.5, 8, false) != null) break;
				if (d < 20 && sees(level, p, at, room)) break;      // out in the open, far is far enough
				Entity e = type.create(level);
				if (!(e instanceof Mob mob)) return false;
				mob.moveTo(x + 0.5, y, z + 0.5, r.nextFloat() * 360f, 0f);
				mob.addTag(h.tag());
				mob.setPersistenceRequired();
				var range = mob.getAttribute(Attributes.FOLLOW_RANGE);
				if (range != null && range.getBaseValue() < 32) range.setBaseValue(32);
				EventHooks.finalizeMobSpawn(mob, level, level.getCurrentDifficultyAt(at), MobSpawnType.STRUCTURE, null);
				int best = 1;
				for (ServerPlayer q : level.players()) if (q.distanceToSqr(p) < 64 * 64) best = Math.max(best, Levels.level(q));
				Balance.soften(mob, kind, best);
				level.addFreshEntity(mob);
				return true;
			}
		}
		return false;
	}

	private static boolean inPiece(Haunt h, BlockPos at) {
		if (!h.box().isInside(at)) return false;
		for (StructurePiece piece : h.start().getPieces()) if (piece.getBoundingBox().isInside(at)) return true;
		return false;
	}

	/** a sturdy floor under `at`, `room` blocks of open air from it up (and round it for the wide ones), no water */
	private static boolean stand(ServerLevel level, BlockPos at, int room, int wide) {
		BlockPos floor = at.below();
		if (!level.getBlockState(floor).isFaceSturdy(level, floor, Direction.UP)) return false;
		for (int dx = -wide; dx <= wide; dx++)
			for (int dz = -wide; dz <= wide; dz++)
				for (int dy = 0; dy < room; dy++) {
					BlockPos q = at.offset(dx, dy, dz);
					var s = level.getBlockState(q);
					if (!s.getCollisionShape(level, q).isEmpty() || !s.getFluidState().isEmpty()) return false;
				}
		return true;
	}

	/** the player could see it pop in: a clear line from their eyes to its middle */
	private static boolean sees(ServerLevel level, ServerPlayer p, BlockPos at, int room) {
		var to = net.minecraft.world.phys.Vec3.atBottomCenterOf(at).add(0, room * 0.5, 0);
		var hit = level.clip(new net.minecraft.world.level.ClipContext(p.getEyePosition(), to,
				net.minecraft.world.level.ClipContext.Block.COLLIDER, net.minecraft.world.level.ClipContext.Fluid.NONE, p));
		return hit.getType() == net.minecraft.world.phys.HitResult.Type.MISS;
	}

	static boolean ours(Entity e) {
		if (!e.isAlive()) return false;
		for (String t : e.getTags()) if (t.startsWith(TAG + ":")) return true;
		return false;
	}

	static void register() {
		NeoForge.EVENT_BUS.addListener(Haunts::tick);
		// a garrison doesn't hurt its own (the breaker's swing catching a deserter)
		NeoForge.EVENT_BUS.addListener((LivingIncomingDamageEvent e) -> {
			Entity a = e.getSource().getEntity();
			if (a != null && a != e.getEntity() && ours(a) && ours(e.getEntity())) e.setCanceled(true);
		});
	}
}
