package com.snoringwalrus.ashbound;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.entity.RandomizableContainerBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.EventHooks;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/**
 * The world's towers (docs/TOWERS.md) come alive when someone walks up to one: its monsters on every floor (each
 * floor raised as someone comes near it, see wake), a glowing foreman on each, and the boss on the roof; the climb is open, so whoever wants the boss can run for it.
 * When the boss falls its coffer rises on the roof. A day after it was last stocked, with none of its monsters left,
 * it stocks again and its coffers refill. Where everything goes comes from data/ashbound/tower/NAME.json (tools/towers/*.py), in the
 * tower's own frame: (0, 0, 0) stands on the ground block at its foot.
 */
public final class TowerSites {
	private TowerSites() {}

	static final String TAG = "ashbound_tower";
	static final long DAY = 24000;
	static final List<String> KINDS = List.of("clockwork_spire", "serpent_ziggurat", "rimeholt", "glass_minaret", "warlords_fang");
	private static final Map<String, Marks> MARKS = new HashMap<>();

	record Mark(int x, int y, int z, String kind) {}

	/** hoard: the boss chest's block; loot: its table (the floor coffers use it without the _boss) */
	record Marks(List<Mark> mobs, List<Mark> foremen, List<Mark> seals, List<Mark> chests, Mark boss, Mark reward, String hoard, String loot) {
		String coffers() {
			return loot.replace("_boss", "");
		}
	}

	static Marks marks(String kind) {
		return MARKS.computeIfAbsent(kind, k -> {
			try (InputStream in = TowerSites.class.getResourceAsStream("/data/ashbound/tower/" + k + ".json")) {
				JsonObject o = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
				JsonArray b = o.getAsJsonArray("boss"), r = o.has("reward") ? o.getAsJsonArray("reward") : null;
				return new Marks(list(o, "mobs"), list(o, "foremen"), list(o, "seals"), list(o, "chests"),
						new Mark(b.get(0).getAsInt(), b.get(1).getAsInt(), b.get(2).getAsInt(), b.get(3).getAsString()),
						r == null ? null : new Mark(r.get(0).getAsInt(), r.get(1).getAsInt(), r.get(2).getAsInt(), ""),
						o.has("hoard") ? o.get("hoard").getAsString() : "spire_hoard",
						o.has("loot") ? o.get("loot").getAsString() : "chests/tower_" + k.replace("_spire", "") + "_boss");
			} catch (Exception e) {
				Ashbound.LOG.error("tower marks for {} won't load", k, e);
				return new Marks(List.of(), List.of(), List.of(), List.of(), null, null, "spire_hoard", "chests/tower_clockwork_boss");
			}
		});
	}

	private static List<Mark> list(JsonObject o, String key) {
		List<Mark> out = new ArrayList<>();
		for (var e : o.getAsJsonArray(key)) {
			JsonArray a = e.getAsJsonArray();
			out.add(new Mark(a.get(0).getAsInt(), a.get(1).getAsInt(), a.get(2).getAsInt(), a.size() > 3 ? a.get(3).getAsString() : ""));
		}
		return out;
	}

	/** a tower standing in the world: its kind, where its foot is, how it's turned */
	record Site(String kind, BlockPos foot, Rotation rot) {
		BlockPos at(int x, int y, int z) {
			BlockPos r = new BlockPos(x, 0, z).rotate(rot);
			return foot.offset(r.getX(), y + 1, r.getZ());
		}

		String key() {
			return kind + "@" + foot.asLong();
		}
	}

	// ---------------------------------------------------------------- what's been stocked, kept with the world

	static final class State extends SavedData {
		final Map<String, Long> stocked = new HashMap<>();
		/** which of a tower's monsters (mobs, then foremen, then the boss) have been raised since it was stocked */
		final Map<String, java.util.BitSet> woke = new HashMap<>();
		/** towers raised by command (/ashbound tree clockwork_spire): not world structures, so kept here */
		final Map<String, Site> placed = new HashMap<>();

		static State get(ServerLevel level) {
			return level.getDataStorage().computeIfAbsent(new SavedData.Factory<>(State::new, State::load, null), "ashbound_towers");
		}

		static State load(CompoundTag tag, HolderLookup.Provider p) {
			State s = new State();
			CompoundTag st = tag.getCompound("stocked"), pl = tag.getCompound("placed");
			for (String k : st.getAllKeys()) s.stocked.put(k, st.getLong(k));
			CompoundTag wk = tag.getCompound("woke");
			for (String k : wk.getAllKeys()) s.woke.put(k, java.util.BitSet.valueOf(wk.getLongArray(k)));
			for (String k : pl.getAllKeys()) {
				CompoundTag t = pl.getCompound(k);
				Site site = new Site(t.getString("kind"), BlockPos.of(t.getLong("foot")), Rotation.values()[t.getInt("rot")]);
				s.placed.put(site.key(), site);
			}
			return s;
		}

		@Override
		public CompoundTag save(CompoundTag tag, HolderLookup.Provider p) {
			CompoundTag st = new CompoundTag(), pl = new CompoundTag();
			stocked.forEach(st::putLong);
			CompoundTag wk = new CompoundTag();
			woke.forEach((k, b) -> wk.putLongArray(k, b.toLongArray()));
			tag.put("woke", wk);
			placed.forEach((k, site) -> {
				CompoundTag t = new CompoundTag();
				t.putString("kind", site.kind());
				t.putLong("foot", site.foot().asLong());
				t.putInt("rot", site.rot().ordinal());
				pl.put(k, t);
			});
			tag.put("stocked", st);
			tag.put("placed", pl);
			return tag;
		}
	}

	// ---------------------------------------------------------------- finding them

	/** a tower someone raised by command now stands at `foot` */
	static void placed(ServerLevel level, String kind, BlockPos foot, Rotation rot) {
		if (!KINDS.contains(kind)) return;
		State st = State.get(level);
		Site s = new Site(kind, foot, rot);
		st.placed.put(s.key(), s);
		st.stocked.remove(s.key());
		st.setDirty();
	}

	static Site siteAt(ServerLevel level, BlockPos pos) {
		for (Site s : State.get(level).placed.values())
			if (Math.abs(pos.getX() - s.foot().getX()) <= 24 && Math.abs(pos.getZ() - s.foot().getZ()) <= 24
					&& pos.getY() >= s.foot().getY() - 10 && pos.getY() <= s.foot().getY() + 120) return s;
		var reg = level.registryAccess().registryOrThrow(Registries.STRUCTURE);
		for (String kind : KINDS) {
			Structure s = reg.get(ResourceKey.create(Registries.STRUCTURE, ResourceLocation.fromNamespaceAndPath(Ashbound.ID, kind)));
			if (s == null) continue;
			StructureStart start = level.structureManager().getStructureWithPieceAt(pos, s);
			if (!start.isValid()) continue;
			for (StructurePiece piece : start.getPieces())
				if (piece instanceof Trees.Piece p) return new Site(kind, new BlockPos(p.ox, p.y0, p.oz), p.rot);
		}
		return null;
	}

	private static void tick(ServerTickEvent.Post e) {
		if (e.getServer().getTickCount() % 20 == 3) hunt(e);
		if (e.getServer().getTickCount() % 40 != 7) return;
		for (ServerPlayer p : e.getServer().getPlayerList().getPlayers()) {
			if (p.isSpectator()) continue;
			ServerLevel level = p.serverLevel();
			Site site = siteAt(level, p.blockPosition());
			if (site == null) continue;
			State st = State.get(level);
			Long last = st.stocked.get(site.key());
			long now = level.getGameTime();
			if (last == null || (now - last >= DAY && alive(level, site) == 0)) {
				stock(level, site);
				st.stocked.put(site.key(), now);
			}
			wake(level, site, p.getY());
		}
	}

	/** a tower monster with no player to fight takes the nearest one within 40 blocks, whatever it was busy with */
	private static void hunt(ServerTickEvent.Post e) {
		for (ServerPlayer p : e.getServer().getPlayerList().getPlayers()) {
			if (p.isSpectator() || p.isCreative()) continue;
			for (Mob m : p.serverLevel().getEntitiesOfClass(Mob.class, p.getBoundingBox().inflate(40, 10, 40),   // its own floor, not the ones above
					m -> m.isAlive() && m.getTags().stream().anyMatch(t -> t.startsWith(TAG + ":")))) {
				if (m.getTarget() instanceof ServerPlayer t && t.isAlive() && !t.isSpectator() && !t.isCreative()
						&& t.distanceToSqr(m) <= p.distanceToSqr(m) + 16) continue;
				m.setTarget(p);
			}
		}
	}

	static boolean ours(Entity e) {
		if (!e.isAlive() || Spells.isThrall(e)) return false;
		for (String t : e.getTags()) if (t.startsWith(TAG + ":") || t.equals("ashbound_dweller")) return true;
		return false;
	}

	private static String tag(Site s) {
		return TAG + ":" + s.key();
	}

	static int alive(ServerLevel level, Site s) {
		AABB box = new AABB(s.foot()).inflate(40, 130, 40);
		return level.getEntitiesOfClass(Mob.class, box, m -> m.isAlive() && m.getTags().contains(tag(s))).size();
	}

	// ---------------------------------------------------------------- stocking

	static void stock(ServerLevel level, Site s) {
		Marks mk = marks(s.kind());
		AABB box = new AABB(s.foot()).inflate(40, 130, 40);
		for (Mob old : level.getEntitiesOfClass(Mob.class, box, m -> m.getTags().contains(tag(s)))) old.discard();
		State st = State.get(level);
		st.woke.put(s.key(), new java.util.BitSet());
		st.setDirty();
		for (int i = 0; i < mk.seals().size(); i++) seal(level, s, mk.seals().get(i), true);
		int nests = 0;
		for (List<Mark> floor : floors(mk.mobs()))
			for (Mark at : nestsFor(floor)) {
				nest(level, s, at, floor);
				nests++;
			}
		for (Mark c : mk.chests())
			if (SilkProps.stocked(level, s.at(c.x(), c.y(), c.z())) instanceof RandomizableContainerBlockEntity box2 && box2.isEmpty())
				box2.setLootTable(ResourceKey.create(Registries.LOOT_TABLE,
						ResourceLocation.fromNamespaceAndPath(Ashbound.ID, mk.coffers())), level.getRandom().nextLong());
		Ashbound.LOG.info("tower {} stocked: {} spawners for {} monster spots, {} foremen", s.key(), nests, mk.mobs().size(), mk.foremen().size());
	}

	// ---------------------------------------------------------------- spawners

	/** the ordinary monsters' spots, grouped by floor (a jump of more than 4 in height starts the next) */
	static List<List<Mark>> floors(List<Mark> mobs) {
		List<Mark> by = new ArrayList<>(mobs);
		by.sort(java.util.Comparator.comparingInt(Mark::y));
		List<List<Mark>> out = new ArrayList<>();
		for (Mark m : by) {
			if (out.isEmpty() || m.y() - out.get(out.size() - 1).get(0).y() > 4) out.add(new ArrayList<>());
			out.get(out.size() - 1).add(m);
		}
		return out;
	}

	/** where a floor's spawners stand: one, or two far apart on a crowded floor */
	static List<Mark> nestsFor(List<Mark> floor) {
		Mark a = floor.get(0);
		if (floor.size() < 7) return List.of(a);
		Mark b = a;
		for (Mark m : floor)
			if (sq(m.x() - a.x()) + sq(m.z() - a.z()) > sq(b.x() - a.x()) + sq(b.z() - a.z())) b = m;
		return b == a ? List.of(a) : List.of(a, b);
	}

	private static int sq(int v) {
		return v * v;
	}

	/** A floor's monsters come out of a spawner (10/29: placed all at once, 15 of them were on you at the third floor):
	 *  two at a time, at most three of a kind about, only with someone close; break it and that floor goes quiet.
	 *  It turns out the kinds that floor was laid out with, tagged as the tower's so they hunt and count as its own. */
	static void nest(ServerLevel level, Site s, Mark at, List<Mark> floor) {
		BlockPos pos = s.at(at.x(), at.y(), at.z());
		level.setBlock(pos, Blocks.SPAWNER.defaultBlockState(), Block.UPDATE_ALL);
		if (!(level.getBlockEntity(pos) instanceof net.minecraft.world.level.block.entity.SpawnerBlockEntity sp)) return;
		Map<String, Integer> kinds = new java.util.LinkedHashMap<>();
		for (Mark m : floor) kinds.merge(m.kind(), 1, Integer::sum);
		net.minecraft.nbt.ListTag potentials = new net.minecraft.nbt.ListTag();
		CompoundTag first = null;
		for (var k : kinds.entrySet()) {
			ResourceLocation id = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, k.getKey());
			if (!BuiltInRegistries.ENTITY_TYPE.containsKey(id)) continue;
			CompoundTag entity = new CompoundTag();
			entity.putString("id", id.toString());
			net.minecraft.nbt.ListTag tags = new net.minecraft.nbt.ListTag();
			tags.add(net.minecraft.nbt.StringTag.valueOf(tag(s)));
			entity.put("Tags", tags);
			CompoundTag rules = new CompoundTag();   // any light: a tower's halls are lit
			rules.put("block_light_limit", new net.minecraft.nbt.IntArrayTag(new int[] {0, 15}));
			rules.put("sky_light_limit", new net.minecraft.nbt.IntArrayTag(new int[] {0, 15}));
			CompoundTag data = new CompoundTag();
			data.put("entity", entity);
			data.put("custom_spawn_rules", rules);
			CompoundTag w = new CompoundTag();
			w.put("data", data);
			w.putInt("weight", k.getValue());
			potentials.add(w);
			if (first == null) first = data;
		}
		if (first == null) return;
		CompoundTag t = new CompoundTag();
		t.put("SpawnPotentials", potentials);
		t.put("SpawnData", first.copy());
		t.putShort("Delay", (short) 20);
		t.putShort("MinSpawnDelay", (short) 160);
		t.putShort("MaxSpawnDelay", (short) 400);
		t.putShort("SpawnCount", (short) 2);
		t.putShort("MaxNearbyEntities", (short) 3);
		t.putShort("RequiredPlayerRange", (short) 14);
		t.putShort("SpawnRange", (short) 4);
		sp.getSpawner().load(level, pos, t);
		sp.setChanged();
	}

	/** WAKE: how far above or below someone a floor's monsters are raised. A whole tower at once is ~90 monsters, all
	 *  drawn through the floors when you look down, and the frame rate halves; so a floor fills as you come up to it. */
	static final int WAKE = 10;

	static void wake(ServerLevel level, Site s, double y) {
		Marks mk = marks(s.kind());
		State st = State.get(level);
		int n = mk.mobs().size(), f = mk.foremen().size();
		java.util.BitSet woke = st.woke.computeIfAbsent(s.key(), k -> {
			java.util.BitSet all = new java.util.BitSet();   // stocked before floors woke one by one: all of it is up already
			all.set(0, n + f + 1);
			return all;
		});
		for (int i = n; i < n + f + (mk.boss() != null ? 1 : 0); i++) {   // the floors' monsters come out of their spawners
			if (woke.get(i)) continue;
			Mark m = i < n ? mk.mobs().get(i) : i < n + f ? mk.foremen().get(i - n) : mk.boss();
			if (Math.abs(s.at(m.x(), m.y(), m.z()).getY() - y) > WAKE) continue;
			spawn(level, s, m, i < n ? null : i < n + f ? Integer.valueOf(i - n) : Integer.valueOf(-1));
			woke.set(i);
			st.setDirty();
		}
	}

	/** floor: the floor whose key it carries (its foreman), -1 the boss, null an ordinary monster */
	private static void spawn(ServerLevel level, Site s, Mark m, Integer floor) {
		EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.getOptional(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, m.kind())).orElse(null);
		if (type == null) return;
		BlockPos at = s.at(m.x(), m.y(), m.z());
		for (int k = 0; k < 4 && !level.getBlockState(at).getCollisionShape(level, at).isEmpty(); k++) at = at.above();
		Entity e = type.create(level);
		if (!(e instanceof Mob mob)) return;
		float yaw = level.getRandom().nextFloat() * 360f;
		mob.moveTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5, yaw, 0f);
		mob.addTag(tag(s));
		mob.setPersistenceRequired();
		var range = mob.getAttribute(Attributes.FOLLOW_RANGE);
		if (range != null && range.getBaseValue() < 48) range.setBaseValue(48);
		EventHooks.finalizeMobSpawn(mob, level, level.getCurrentDifficultyAt(at), MobSpawnType.STRUCTURE, null);
		if (floor != null && floor >= 0) {
			mob.addTag("ashbound_tower_key:" + floor);
			mob.setCustomName(Component.literal("Foreman of the " + ordinal(floor + 1) + " Floor"));
			mob.setGlowingTag(true);
			var hp = mob.getAttribute(Attributes.MAX_HEALTH);
			if (hp != null) {
				hp.setBaseValue(Balance.foreman(s.kind(), hp.getBaseValue()));
				mob.setHealth(mob.getMaxHealth());
			}
		}
		level.addFreshEntity(mob);
	}

	private static String ordinal(int n) {
		return switch (n) {
			case 1 -> "First";
			case 2 -> "Second";
			case 3 -> "Third";
			case 4 -> "Fourth";
			case 5 -> "Fifth";
			case 6 -> "Sixth";
			default -> "Seventh";
		};
	}

	/** the brass gate at the top of a stair, across its end and the floor either side, so it can't be walked round */
	static void seal(ServerLevel level, Site s, Mark m, boolean shut) {
		Block bars = BuiltInRegistries.BLOCK.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "spire_bars"));
		List<BlockPos> ps = new ArrayList<>();
		for (int dz = -2; dz <= 2; dz++)          // the stair's three lanes and the floor either side of its head
			for (int dy = 0; dy < 4; dy++) ps.add(s.at(m.x(), m.y() + dy, m.z() + dz));
		for (BlockPos p : ps) {
			BlockState here = level.getBlockState(p);
			if (shut && (here.isAir() || here.is(Blocks.CAVE_AIR))) level.setBlock(p, bars.defaultBlockState(), Block.UPDATE_ALL);
			else if (!shut && here.is(bars)) level.setBlock(p, Blocks.AIR.defaultBlockState(), Block.UPDATE_ALL);
		}
		if (shut) for (BlockPos p : ps)
			if (level.getBlockState(p).is(bars)) level.setBlock(p, Block.updateFromNeighbourShapes(level.getBlockState(p), level, p), Block.UPDATE_ALL);
		if (!shut) {
			Vec3 c = Vec3.atCenterOf(s.at(m.x(), m.y() + 1, m.z()));
			level.sendParticles(ParticleTypes.CLOUD, c.x, c.y, c.z, 30, 0.6, 1.0, 0.6, 0.04);
			level.sendParticles(ParticleTypes.ELECTRIC_SPARK, c.x, c.y, c.z, 40, 0.6, 1.0, 0.6, 0.2);
			level.playSound(null, BlockPos.containing(c), SoundEvents.IRON_DOOR_OPEN, SoundSource.BLOCKS, 1.5f, 0.6f);
			level.playSound(null, BlockPos.containing(c), SoundEvents.PISTON_CONTRACT, SoundSource.BLOCKS, 1.2f, 0.7f);
		}
	}

	private static void died(LivingDeathEvent e) {
		if (!(e.getEntity().level() instanceof ServerLevel level)) return;
		Entity dead = e.getEntity();
		String key = null;
		Integer floor = null;
		for (String t : dead.getTags()) {
			if (t.startsWith(TAG + ":")) key = t.substring(TAG.length() + 1);
			if (t.startsWith("ashbound_tower_key:")) floor = Integer.parseInt(t.substring("ashbound_tower_key:".length()));
		}
		if (key == null) return;
		Site s = siteAt(level, dead.blockPosition());
		if (s == null || !s.key().equals(key)) return;
		Marks mk = marks(s.kind());
		Component say = null;
		if (floor != null && floor < mk.seals().size()) {
			seal(level, s, mk.seals().get(floor), false);
			say = Component.literal("The Cog Key turns. The brass gate grinds open.");
		} else if (mk.boss() != null && dead.getType() == BuiltInRegistries.ENTITY_TYPE.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, mk.boss().kind()))) {
			say = dead.getDisplayName().copy().append(" has fallen. Its hoard rises from the roof.");
			if (mk.reward() != null) reward(level, s, mk.reward(), mk);
		}
		if (say != null) {
			Component msg = say;
			for (ServerPlayer p : level.players())
				if (p.distanceToSqr(dead) < 96 * 96) p.displayClientMessage(msg, true);
		}
	}

	/** the boss's coffer, filled from chests/tower_KIND_boss: its heart, mainsprings, a weapon or two, maybe its own */
	private static void reward(ServerLevel level, Site s, Mark m, Marks mk) {
		BlockPos at = s.at(m.x(), m.y(), m.z());
		Block hoard = BuiltInRegistries.BLOCK.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, mk.hoard()));
		level.setBlock(at, hoard.defaultBlockState().setValue(PropBlock.FACING, s.rot().rotate(Direction.SOUTH)), Block.UPDATE_ALL);
		if (level.getBlockEntity(at) instanceof RandomizableContainerBlockEntity box)
			box.setLootTable(ResourceKey.create(Registries.LOOT_TABLE, ResourceLocation.fromNamespaceAndPath(Ashbound.ID, mk.loot())),
					level.getRandom().nextLong());
		Vec3 c = Vec3.atCenterOf(at);
		level.sendParticles(ParticleTypes.FLASH, c.x, c.y, c.z, 1, 0, 0, 0, 0);
		level.sendParticles(ParticleTypes.ELECTRIC_SPARK, c.x, c.y + 0.4, c.z, 60, 0.6, 0.6, 0.6, 0.25);
		level.sendParticles(ParticleTypes.CLOUD, c.x, c.y, c.z, 30, 0.8, 0.4, 0.8, 0.03);
		level.playSound(null, at, SoundEvents.PISTON_EXTEND, SoundSource.BLOCKS, 1.5f, 0.6f);
		level.playSound(null, at, SoundEvents.PLAYER_LEVELUP, SoundSource.BLOCKS, 1f, 0.8f);
	}

	static void register() {
		NeoForge.EVENT_BUS.addListener(TowerSites::tick);
		NeoForge.EVENT_BUS.addListener(TowerSites::died);
		// tower monsters don't hurt each other (a boss's sweep catching its own), so none turns on another
		NeoForge.EVENT_BUS.addListener((LivingIncomingDamageEvent e) -> {
			Entity a = e.getSource().getEntity();
			if (a != null && a != e.getEntity() && ours(a) && ours(e.getEntity())) e.setCanceled(true);
		});
	}
}
