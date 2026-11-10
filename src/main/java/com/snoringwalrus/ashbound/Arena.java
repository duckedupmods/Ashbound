package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import javax.annotation.Nullable;

import com.mojang.brigadier.arguments.IntegerArgumentType;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.HoverEvent;
import net.minecraft.network.chat.Style;
import net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitlesAnimationPacket;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.EventHooks;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.registries.DeferredBlock;

/**
 * The Ashen Ring (tools/blender/arena_ring.py is the look; ArenaShape its blocks): Veyra the Ringkeeper, at the second desk
 * in the guild hall, sends a whole party to a colosseum in its own dimension once they've proved themselves (killed what
 * rules an E-rank gate or harder). Waves of monsters come in through the four gates, from every dungeon of the rank the
 * wave has climbed to (F for 1-6, E for 7-12 ... S from 37, harder still past 42), more of them for more players, a
 * dungeon's boss every 10th. Every 5th wave cleared there's a breather: everyone healed and back, their spoils fall round
 * them, and they choose: on, or out with what they've won. Waves 10, 20, 30 ... are kept: a party can start from the highest
 * one all of them have reached. Fall in there and you watch from the stands until the next wave; if the whole party is
 * down, it's over, and you go home with everything won so far. A crowd of townsfolk fills the stands (client/ArenaCrowd)
 * and cheers each kill. The best waves are kept on Veyra's records beside the adventurer parties'.
 */
public final class Arena {
	private Arena() {}

	public static final ResourceKey<Level> RING = ResourceKey.create(Registries.DIMENSION, ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "ashen_ring"));
	static final String TAG = "ashbound_arena", BACK = "ashbound_ring_back", RANKS = "FEDCBAS";
	/** a pause between waves; how long the breather waits for a choice before taking you out; most monsters out at once */
	static final int PAUSE = 100, BREATHER = 2400, MOST_OUT = 18, VERSION = 1;
	/** Veyra's desk in the guild hall, in the city's frame */
	static final int[] VEYRA = {-18, 21, -117};

	static final DeferredBlock<Block> SAND = block("arena_sand", BlockBehaviour.Properties.ofFullCopy(Blocks.SANDSTONE).mapColor(MapColor.COLOR_LIGHT_GRAY)
			.sound(SoundType.SAND).strength(-1f, 3600000f));
	static final DeferredBlock<Block> RUNE = block("arena_rune", BlockBehaviour.Properties.ofFullCopy(Blocks.SANDSTONE).mapColor(MapColor.COLOR_LIGHT_BLUE)
			.sound(SoundType.AMETHYST).strength(-1f, 3600000f).lightLevel(s -> 10).emissiveRendering((s, g, p) -> true));

	private static DeferredBlock<Block> block(String name, BlockBehaviour.Properties props) {
		DeferredBlock<Block> b = WorldBlocks.BLOCKS.registerBlock(name, Block::new, props);
		WorldBlocks.ITEMS.add(Weapons.ITEMS.registerSimpleBlockItem(b));
		return b;
	}

	static final int READY = 0, FIGHT = 1, REST = 2, BUILDING = 3;

	/** One party's run. */
	static final class Run {
		final int slot;
		final Set<UUID> members = new LinkedHashSet<>(), benched = new HashSet<>();
		final List<UUID> mobs = new ArrayList<>();
		final List<String> pending = new ArrayList<>();
		int wave, phase = BUILDING, best;
		long until, lastSpawn;
		String names = "";

		Run(int slot) {
			this.slot = slot;
		}

		Vec3 at(Vec3 rel) {
			BlockPos o = ArenaShape.origin(slot);
			return new Vec3(o.getX() + rel.x, o.getY() + rel.y, o.getZ() + rel.z);
		}
	}

	static final Map<Integer, Run> RUNS = new HashMap<>();

	// ---------------------------------------------------------------- what's kept: the Rings built, the records

	static final class Data extends SavedData {
		final Map<Integer, Integer> built = new HashMap<>();
		/** a party's names -> its best wave */
		final Map<String, Integer> records = new HashMap<>();

		@Override
		public CompoundTag save(CompoundTag tag, HolderLookup.Provider reg) {
			CompoundTag b = new CompoundTag();
			built.forEach((k, v) -> b.putInt(String.valueOf(k), v));
			tag.put("built", b);
			CompoundTag rec = new CompoundTag();
			records.forEach(rec::putInt);
			tag.put("records", rec);
			return tag;
		}

		static Data load(CompoundTag tag, HolderLookup.Provider reg) {
			Data d = new Data();
			CompoundTag b = tag.getCompound("built");
			for (String k : b.getAllKeys()) d.built.put(Integer.parseInt(k), b.getInt(k));
			CompoundTag rec = tag.getCompound("records");
			for (String k : rec.getAllKeys()) d.records.put(k, rec.getInt(k));
			return d;
		}
	}

	static Data data(MinecraftServer server) {
		return server.overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(Data::new, Data::load, null), "ashbound_ring");
	}

	// ---------------------------------------------------------------- raising a Ring (spread over ticks)

	private static int[] XS, YS, ZS;
	private static BlockState[] ST;

	/** The Ring's blocks, in chunk order (and bottom up in each), so it's raised one chunk at a time. */
	private static void shape() {
		if (XS != null) return;
		List<int[]> at = new ArrayList<>();
		List<BlockState> st = new ArrayList<>();
		ArenaShape.blocks((x, y, z, s) -> {
			at.add(new int[] {x, y, z, st.size()});
			st.add(s);
		});
		at.sort((a, b) -> {
			int c = Integer.compare(a[0] >> 4, b[0] >> 4);
			if (c == 0) c = Integer.compare(a[2] >> 4, b[2] >> 4);
			return c != 0 ? c : Integer.compare(a[1], b[1]);
		});
		int n = at.size();
		XS = new int[n];
		YS = new int[n];
		ZS = new int[n];
		ST = new BlockState[n];
		for (int i = 0; i < n; i++) {
			int[] a = at.get(i);
			XS[i] = a[0];
			YS[i] = a[1];
			ZS[i] = a[2];
			ST[i] = st.get(a[3]);
		}
	}

	private static final class Job {
		final int slot;
		int next;

		Job(int slot) {
			this.slot = slot;
		}
	}

	@Nullable
	private static Job job;

	/** The chunks a Ring stands in, kept loaded while it's raised and while a run is in it. */
	static void keep(ServerLevel l, int slot, boolean on) {
		BlockPos o = ArenaShape.origin(slot);
		int r = ArenaShape.R_OUT + 3;
		for (int cx = (o.getX() - r) >> 4; cx <= (o.getX() + r) >> 4; cx++)
			for (int cz = (o.getZ() - r) >> 4; cz <= (o.getZ() + r) >> 4; cz++) l.setChunkForced(cx, cz, on);
	}

	/** A little of the Ring raised each tick: chunk by chunk, each one only once it's loaded (never waited for). */
	private static void build(ServerLevel l) {
		Job j = job;
		if (j == null) return;
		shape();
		BlockPos o = ArenaShape.origin(j.slot);
		if (j.next == 0 && l.getServer().getTickCount() % 20 == 0) keep(l, j.slot, true);
		BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
		long stop = System.nanoTime() + 20_000_000L;
		while (j.next < XS.length && System.nanoTime() < stop) {
			int cx = (o.getX() + XS[j.next]) >> 4, cz = (o.getZ() + ZS[j.next]) >> 4;
			if (!l.hasChunk(cx, cz)) {
				l.setChunkForced(cx, cz, true);
				break;                                   // loading: on with it next tick
			}
			while (j.next < XS.length && ((o.getX() + XS[j.next]) >> 4) == cx && ((o.getZ() + ZS[j.next]) >> 4) == cz) {
				p.set(o.getX() + XS[j.next], o.getY() + YS[j.next], o.getZ() + ZS[j.next]);
				l.setBlock(p, ST[j.next], Block.UPDATE_CLIENTS);
				j.next++;
			}
		}
		int pct = j.next * 100 / XS.length;
		Run run = RUNS.get(j.slot);
		if (run != null && l.getServer().getTickCount() % 10 == 0)
			for (ServerPlayer m : online(l.getServer(), run))
				m.displayClientMessage(Component.literal("Veyra's circle flares... the Ring rises " + pct + "%").withStyle(ChatFormatting.AQUA, ChatFormatting.ITALIC), true);
		if (j.next < XS.length) return;
		job = null;
		data(l.getServer()).built.put(j.slot, VERSION);
		data(l.getServer()).setDirty();
		if (run != null) arrive(l, run);
	}

	// ---------------------------------------------------------------- going in

	/** Veyra's word ("arena:start", "arena:best", "arena:records" in her talk). */
	static void act(ServerPlayer p, String what) {
		switch (what) {
			case "start" -> begin(p, 0);
			case "best" -> begin(p, -1);
			case "records" -> records(p);
			default -> {}
		}
	}

	/** The highest milestone (10, 20, ...) this player has reached. */
	static int milestone(ServerPlayer p) {
		int m = 0;
		for (int w = 10; w <= 200; w += 10) if (Coins.flag(p, "ring_m" + w)) m = w;
		return m;
	}

	@Nullable
	static Run runOf(Entity p) {
		for (Run r : RUNS.values()) if (r.members.contains(p.getUUID())) return r;
		return null;
	}

	/** In with p's party (those near p): from the start, or (from < 0) the highest milestone all of them have reached. */
	static boolean begin(ServerPlayer p, int from) {
		if (p.level().dimension() == RING || runOf(p) != null) return false;
		List<ServerPlayer> party = new ArrayList<>();
		party.add(p);
		for (ServerPlayer o : Party.others(p))
			if (o.level() == p.level() && o.distanceTo(p) < 48 && o.isAlive() && !Downed.is(o) && runOf(o) == null) party.add(o);
		int start = from;
		if (from < 0) {
			start = Integer.MAX_VALUE;
			for (ServerPlayer m : party) start = Math.min(start, milestone(m));
		}
		int slot = -1;
		for (int i = 0; i < ArenaShape.SLOTS; i++)
			if (!RUNS.containsKey(i) && (job == null || job.slot != i)) {
				slot = i;
				break;
			}
		if (slot < 0) {
			p.sendSystemMessage(Component.literal("Veyra: \"Every Ring is taken tonight. Come back in a little while.\"").withStyle(ChatFormatting.GRAY));
			return false;
		}
		ServerLevel ring = p.server.getLevel(RING);
		if (ring == null) return false;
		Run run = new Run(slot);
		run.wave = start;
		run.best = start;
		List<String> names = new ArrayList<>();
		for (ServerPlayer m : party) {
			run.members.add(m.getUUID());
			names.add(m.getGameProfile().getName());
			remember(m);
		}
		names.sort(String::compareToIgnoreCase);
		run.names = String.join(", ", names);
		RUNS.put(slot, run);
		keep(ring, slot, true);
		Integer built = data(p.server).built.get(slot);
		if (built != null && built == VERSION) arrive(ring, run);
		else if (job == null) job = new Job(slot);
		for (ServerPlayer m : party) {
			m.sendSystemMessage(Component.literal("Veyra raises her hands, and the guild hall falls away...").withStyle(ChatFormatting.AQUA, ChatFormatting.ITALIC));
			m.serverLevel().sendParticles(ParticleTypes.REVERSE_PORTAL, m.getX(), m.getY() + 1, m.getZ(), 60, 0.5, 1, 0.5, 0.1);
		}
		return true;
	}

	static void remember(ServerPlayer p) {
		CompoundTag t = new CompoundTag();
		t.putString("dim", p.level().dimension().location().toString());
		t.putDouble("x", p.getX());
		t.putDouble("y", p.getY());
		t.putDouble("z", p.getZ());
		t.putFloat("yaw", p.getYRot());
		t.putInt("mode", p.gameMode.getGameModeForPlayer().getId());
		p.getPersistentData().put(BACK, t);
	}

	/** Back where you were before, as you were (your game mode back if you'd fallen). */
	static void home(ServerPlayer p) {
		CompoundTag t = p.getPersistentData().getCompound(BACK);
		p.getPersistentData().remove(BACK);
		Downed.DOWN.remove(p.getUUID());
		p.setForcedPose(null);
		GameType mode = GameType.byId(t.contains("mode") ? t.getInt("mode") : GameType.SURVIVAL.getId());
		if (p.gameMode.getGameModeForPlayer() != mode) p.setGameMode(mode);
		ServerLevel to = t.contains("dim") ? p.server.getLevel(ResourceKey.create(Registries.DIMENSION, ResourceLocation.parse(t.getString("dim")))) : null;
		if (to == null || BossArenas.isArena(to.dimension())) {
			to = p.server.overworld();
			BlockPos s = to.getSharedSpawnPos();
			p.teleportTo(to, s.getX() + 0.5, s.getY(), s.getZ() + 0.5, p.getYRot(), 0f);
		} else p.teleportTo(to, t.getDouble("x"), t.getDouble("y"), t.getDouble("z"), t.getFloat("yaw"), 0f);
	}

	private static void arrive(ServerLevel ring, Run run) {
		int i = 0;
		List<ServerPlayer> in = online(ring.getServer(), run);
		for (ServerPlayer m : in) {
			double a = i++ * Math.PI * 2 / Math.max(1, in.size());
			Vec3 at = run.at(new Vec3(Math.cos(a) * 2.5 + 0.5, 0, Math.sin(a) * 2.5 + 0.5));
			m.teleportTo(ring, at.x, at.y, at.z, (float) Math.toDegrees(Math.atan2(-Math.cos(a), Math.sin(a))) + 180, 0f);
			title(m, "THE ASHEN RING", run.wave == 0 ? "The crowd rises. The first wave is coming." : "From wave " + run.wave + ". The crowd remembers you.");
			m.playNotifySound(SoundEvents.BEACON_ACTIVATE, SoundSource.PLAYERS, 1f, 0.6f);
		}
		run.phase = READY;
		run.until = ring.getGameTime() + PAUSE + 60;
		cheer(ring, run, 2);
	}

	// ---------------------------------------------------------------- the run

	static List<ServerPlayer> online(MinecraftServer server, Run run) {
		List<ServerPlayer> out = new ArrayList<>();
		for (UUID u : run.members) {
			ServerPlayer p = server.getPlayerList().getPlayer(u);
			if (p != null) out.add(p);
		}
		return out;
	}

	private static void tick(ServerTickEvent.Post e) {
		MinecraftServer server = e.getServer();
		ServerLevel ring = server.getLevel(RING);
		if (ring == null) return;
		build(ring);
		if (server.getTickCount() % 200 == 50) veyra(server);
		long now = ring.getGameTime();
		for (Run run : new ArrayList<>(RUNS.values())) {
			if (run.phase == BUILDING) continue;
			// who's still in: online, in the Ring
			run.members.removeIf(u -> {
				ServerPlayer p = server.getPlayerList().getPlayer(u);
				return p == null || p.level() != ring;
			});
			if (run.members.isEmpty()) {
				end(ring, run, null);
				continue;
			}
			for (ServerPlayer p : online(server, run))
				if (p.getY() < ArenaShape.FLOOR - 40) {
					// over the edge: back onto the sand
					Vec3 c = run.at(new Vec3(0.5, 0, 0.5));
					p.teleportTo(ring, c.x, c.y, c.z, p.getYRot(), 0f);
					p.fallDistance = 0;
				}
			switch (run.phase) {
				case READY -> {
					long left = run.until - now;
					if (left == 60 || left == 40 || left == 20)
						for (ServerPlayer p : online(server, run)) p.displayClientMessage(Component.literal("Wave " + (run.wave + 1) + " in " + left / 20).withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD), true);
					if (left <= 0) wave(ring, run);
				}
				case FIGHT -> fight(ring, run, now);
				case REST -> {
					if (now >= run.until) end(ring, run, "The crowd waited. You leave with your spoils.");
					else if ((run.until - now) % 400 == 0) for (ServerPlayer p : online(server, run)) choices(p, run);
				}
				default -> {}
			}
		}
	}

	/** The rank the monsters of wave w come from: F for 1-6, E for 7-12, ... S from 37. */
	static char rank(int w) {
		return RANKS.charAt(Math.min(6, Math.max(0, (w - 1) / 6)));
	}

	static void wave(ServerLevel ring, Run run) {
		run.wave++;
		run.phase = FIGHT;
		run.lastSpawn = 0;
		RandomSource r = ring.getRandom();
		int players = Math.max(1, run.members.size());
		char rank = rank(run.wave);
		List<Gear.Dungeon> ds = Adventurers.dungeons(rank);
		List<String> pool = new ArrayList<>();
		for (Gear.Dungeon d : ds) pool.addAll(d.mobs());
		run.pending.clear();
		int count = (int) Math.round((3 + run.wave / 2.0) * (1 + 0.5 * (players - 1)));
		boolean boss = run.wave % 10 == 0 && !ds.isEmpty();
		if (boss) {
			Gear.Dungeon d = ds.get(r.nextInt(ds.size()));
			run.pending.add("!" + d.boss());
			count /= 2;
		}
		for (int i = 0; i < count && !pool.isEmpty(); i++) run.pending.add(pool.get(r.nextInt(pool.size())));
		// those who fell come back in for it
		for (UUID u : new ArrayList<>(run.benched)) {
			ServerPlayer p = ring.getServer().getPlayerList().getPlayer(u);
			if (p != null) unbench(ring, run, p);
		}
		run.benched.clear();
		for (ServerPlayer p : online(ring.getServer(), run)) {
			title(p, "WAVE " + run.wave, boss ? "Something that rules a gate comes through." : rank + "-rank, " + run.pending.size() + " of them");
			p.playNotifySound(boss ? SoundEvents.WITHER_SPAWN : SoundEvents.RAID_HORN.value(), SoundSource.HOSTILE, boss ? 0.6f : 1f, 0.8f);
		}
		cheer(ring, run, boss ? 3 : 1);
	}

	private static void fight(ServerLevel ring, Run run, long now) {
		run.mobs.removeIf(u -> !(ring.getEntity(u) instanceof LivingEntity m) || !m.isAlive());
		if (now % 20 == 0 && run.pending.isEmpty()) Spells.glowLast(ring, run.mobs, false);
		RandomSource r = ring.getRandom();
		// out through the gates, a few at a time
		if (!run.pending.isEmpty() && now - run.lastSpawn >= 30 && run.mobs.size() < MOST_OUT) {
			run.lastSpawn = now;
			for (int k = 0; k < 3 && !run.pending.isEmpty() && run.mobs.size() < MOST_OUT; k++) {
				int g = r.nextInt(4);
				Mob m = spawn(ring, run, run.pending.remove(0), g, r);
				if (m != null) run.mobs.add(m.getUUID());
			}
		}
		if (now % 4 == 0) rifts(ring, run, r);
		for (UUID u : run.mobs)
			if (ring.getEntity(u) instanceof Mob m && m.getY() < ArenaShape.FLOOR - 30) m.kill();
		// the whole party down: it's over
		boolean anyUp = false;
		for (ServerPlayer p : online(ring.getServer(), run)) if (!run.benched.contains(p.getUUID()) && !Downed.is(p)) anyUp = true;
		if (!anyUp) {
			end(ring, run, "The Ring has had its fill of you. You wake in the guild hall with what you won.");
			return;
		}
		if (run.pending.isEmpty() && run.mobs.isEmpty()) cleared(ring, run);
	}

	@Nullable
	private static Mob spawn(ServerLevel ring, Run run, String id, int gate, RandomSource r) {
		boolean boss = id.startsWith("!");
		String key = boss ? id.substring(1) : id;
		var type = BuiltInRegistries.ENTITY_TYPE.getOptional(key.contains(":") ? ResourceLocation.parse(key) : ResourceLocation.fromNamespaceAndPath(Ashbound.ID, key)).orElse(null);
		if (type == null || !(type.create(ring) instanceof Mob m)) return null;
		Vec3 at = run.at(ArenaShape.lair(gate)).add(r.nextDouble() - 0.5, 0, r.nextDouble() - 0.5);
		Vec3 mouth = run.at(ArenaShape.gate(gate));
		float yaw = (float) Math.toDegrees(Math.atan2(-(mouth.x - at.x), mouth.z - at.z));
		m.moveTo(at.x, at.y, at.z, yaw, 0);
		EventHooks.finalizeMobSpawn(m, ring, ring.getCurrentDifficultyAt(BlockPos.containing(at)), MobSpawnType.EVENT, null);
		m.setPersistenceRequired();
		m.addTag(TAG);
		// past S, everything comes harder each wave
		if (run.wave > 42) {
			double k = 0.06 * (run.wave - 42);
			ResourceLocation surge = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "ring_surge");
			for (var attr : List.of(Attributes.MAX_HEALTH, Attributes.ATTACK_DAMAGE)) {
				var inst = m.getAttribute(attr);
				if (inst != null && inst.getModifier(surge) == null) inst.addPermanentModifier(new AttributeModifier(surge, k, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
			}
			m.setHealth(m.getMaxHealth());
		}
		if (!ring.addFreshEntity(m)) return null;
		ServerPlayer near = null;
		for (ServerPlayer p : online(ring.getServer(), run))
			if (!run.benched.contains(p.getUUID()) && !Downed.is(p) && (near == null || p.distanceToSqr(m) < near.distanceToSqr(m))) near = p;
		if (near != null) m.setTarget(near);
		ring.sendParticles(ParticleTypes.REVERSE_PORTAL, mouth.x, mouth.y + 2, mouth.z, 40, 1.2, 1.5, 1.2, 0.2);
		ring.playSound(null, mouth.x, mouth.y, mouth.z, boss ? SoundEvents.WARDEN_EMERGE : SoundEvents.PORTAL_TRAVEL, SoundSource.HOSTILE, boss ? 3f : 0.3f, boss ? 0.7f : 1.6f);
		return m;
	}

	/** The gates while monsters come: a ring of the rank's colour turning in each mouth. */
	private static void rifts(ServerLevel ring, Run run, RandomSource r) {
		int col = GateEntity.COLOUR[Mth.clamp(RANKS.indexOf(rank(Math.max(1, run.wave))), 0, 8)];
		var dust = new DustParticleOptions(new org.joml.Vector3f((col >> 16 & 255) / 255f, (col >> 8 & 255) / 255f, (col & 255) / 255f), 1.6f);
		long t = ring.getGameTime();
		for (int g = 0; g < 4; g++) {
			Vec3 c = run.at(ArenaShape.gate(g)).add(0, 2.6, 0);
			double ga = ArenaShape.GATES[g];
			for (int k = 0; k < 3; k++) {
				double a = t * 0.15 + k * 2.1 + r.nextDouble() * 0.2;
				double w = Math.cos(a) * 2.3, h = Math.sin(a) * 2.6;
				ring.sendParticles(dust, c.x - Math.sin(ga) * w, c.y + h, c.z + Math.cos(ga) * w, 1, 0, 0, 0, 0);
			}
			if (r.nextFloat() < 0.4f) ring.sendParticles(ParticleTypes.REVERSE_PORTAL, c.x, c.y, c.z, 2, 1, 1.4, 1, 0.02);
		}
	}

	private static void cleared(ServerLevel ring, Run run) {
		run.best = Math.max(run.best, run.wave);
		record(ring.getServer(), run);
		cheer(ring, run, 2);
		boolean mile = run.wave % 10 == 0;
		for (ServerPlayer p : online(ring.getServer(), run)) {
			if (mile && !Coins.flag(p, "ring_m" + run.wave)) {
				Coins.setFlag(p, "ring_m" + run.wave);
				p.sendSystemMessage(Component.literal("Milestone: wave " + run.wave + ". Veyra can send you in from here next time.").withStyle(ChatFormatting.AQUA, ChatFormatting.BOLD));
			}
		}
		if (run.wave % 5 != 0) {
			run.phase = READY;
			run.until = ring.getGameTime() + PAUSE;
			for (ServerPlayer p : online(ring.getServer(), run))
				p.displayClientMessage(Component.literal("Wave " + run.wave + " cleared").withStyle(ChatFormatting.GREEN, ChatFormatting.BOLD), true);
			return;
		}
		// a breather: everyone up and healed, spoils for each, and a choice
		run.phase = REST;
		run.until = ring.getGameTime() + BREATHER;
		RandomSource r = ring.getRandom();
		for (UUID u : new ArrayList<>(run.benched)) {
			ServerPlayer p = ring.getServer().getPlayerList().getPlayer(u);
			if (p != null) unbench(ring, run, p);
		}
		run.benched.clear();
		for (ServerPlayer p : online(ring.getServer(), run)) {
			if (Downed.is(p)) Downed.revive(p, null);
			p.setHealth(p.getMaxHealth());
			p.getFoodData().eat(20, 1f);
			List<ItemStack> share = new java.util.ArrayList<>(spoils(p, run, r));
			share.addAll(Chains.extra(p, "arena"));
			String got = Dropped.rain(ring, p, share, r);
			int[] pay = Errands.pay(RANKS.indexOf(rank(run.wave)));
			int coins = pay[0] * (1 + run.wave / 10), gp = Guild.of(p).registered() ? pay[1] : 0;
			Coins.give(p, coins);
			if (gp > 0) Guild.points(p, gp);
			title(p, "WAVE " + run.wave + " CLEARED", "The crowd throws their winnings down to you");
			p.sendSystemMessage(Component.literal("  +" + coins + " coins" + (gp > 0 ? ", +" + gp + " GP" : "") + got).withStyle(ChatFormatting.YELLOW));
			choices(p, run);
		}
	}

	private static void choices(ServerPlayer p, Run run) {
		Component on = Component.literal("[ Fight on ]").withStyle(Style.EMPTY.withColor(ChatFormatting.RED).withBold(true)
				.withClickEvent(new ClickEvent(ClickEvent.Action.RUN_COMMAND, "/ashbound ring continue"))
				.withHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, Component.literal("Waves " + (run.wave + 1) + "-" + (run.wave + 5) + ", harder"))));
		Component out = Component.literal("[ Leave with your spoils ]").withStyle(Style.EMPTY.withColor(ChatFormatting.GREEN).withBold(true)
				.withClickEvent(new ClickEvent(ClickEvent.Action.RUN_COMMAND, "/ashbound ring leave")));
		p.sendSystemMessage(Component.literal("Veyra's voice: \"Well? They want more of you.\"  ").withStyle(ChatFormatting.AQUA).append(on).append("  ").append(out));
	}

	/** One player's spoils at a breather: finds, the wave's rank's mats, a weapon now and then (more the further you go). */
	static List<ItemStack> spoils(ServerPlayer p, Run run, RandomSource r) {
		List<ItemStack> out = new ArrayList<>();
		for (int i = 0; i < 1 + run.wave / 10; i++) out.add(new ItemStack(Ranks.find(p, r)));
		List<Gear.Dungeon> ds = Adventurers.dungeons(rank(run.wave));
		if (ds.isEmpty()) return out;
		Gear.Dungeon d = ds.get(r.nextInt(ds.size()));
		if (d.mats().length > 0) {
			var it = Gear.item(d.mats()[0]);
			if (it != null) out.add(new ItemStack(it, 2 + r.nextInt(3)));
		}
		if (d.mats().length > 1 && r.nextFloat() < 0.5f) {
			var it = Gear.item(d.mats()[1]);
			if (it != null) out.add(new ItemStack(it, 1 + r.nextInt(2)));
		}
		if (r.nextFloat() < 0.05f + run.wave * 0.004f) {
			List<Gear.Weapon> arms = d.weapons().stream().filter(w -> !w.boss() || run.wave % 10 == 0).toList();
			var it = arms.isEmpty() ? null : Gear.item(arms.get(r.nextInt(arms.size())).id());
			if (it != null) out.add(new ItemStack(it));
		}
		return out;
	}

	/** A choice at the breather (`/ashbound ring continue|leave`). */
	static int choose(ServerPlayer p, boolean on) {
		Run run = runOf(p);
		if (run == null || run.phase != REST) return 0;
		ServerLevel ring = p.serverLevel();
		if (on) {
			run.phase = READY;
			run.until = ring.getGameTime() + 80;
			for (ServerPlayer m : online(p.server, run))
				m.sendSystemMessage(Component.literal(p.getGameProfile().getName() + " chose to fight on.").withStyle(ChatFormatting.RED));
			cheer(ring, run, 3);
		} else end(ring, run, p.getGameProfile().getName() + " called it. You leave the Ring with your spoils.");
		return 1;
	}

	static void end(ServerLevel ring, Run run, @Nullable String why) {
		RUNS.remove(run.slot);
		if (job == null || job.slot != run.slot) keep(ring, run.slot, false);
		record(ring.getServer(), run);
		for (UUID u : run.mobs) {
			Entity e = ring.getEntity(u);
			if (e != null) e.discard();
		}
		for (UUID u : new HashSet<>(run.members)) {
			ServerPlayer p = ring.getServer().getPlayerList().getPlayer(u);
			if (p == null) continue;
			if (why != null) p.sendSystemMessage(Component.literal(why).withStyle(ChatFormatting.AQUA));
			p.sendSystemMessage(Component.literal("Best wave this run: " + run.best).withStyle(ChatFormatting.GRAY));
			if (p.level() == ring) {
				p.setHealth(Math.max(p.getHealth(), p.getMaxHealth() * 0.5f));
				home(p);
			}
		}
	}

	// ---------------------------------------------------------------- falling in there

	/** Dead in the Ring (and nobody brought you back): you watch from the stands until the next wave. */
	private static void died(LivingDeathEvent e) {
		LivingEntity d = e.getEntity();
		if (d.level().dimension() != RING || !(d.level() instanceof ServerLevel ring)) return;
		if (d instanceof ServerPlayer p) {
			Run run = runOf(p);
			if (run == null) return;
			e.setCanceled(true);
			bench(ring, run, p);
			return;
		}
		if (d.getTags().contains(TAG))
			for (Run run : RUNS.values())
				if (run.mobs.contains(d.getUUID())) cheer(ring, run, 0);
	}

	static void bench(ServerLevel ring, Run run, ServerPlayer p) {
		Downed.DOWN.remove(p.getUUID());
		p.setForcedPose(null);
		p.setHealth(p.getMaxHealth());
		p.removeAllEffects();
		p.clearFire();
		p.setGameMode(GameType.SPECTATOR);
		run.benched.add(p.getUUID());
		Vec3 s = run.at(ArenaShape.stands());
		p.teleportTo(ring, s.x, s.y, s.z, 180f, 20f);
		title(p, "YOU FELL", "Watch from the stands. You're back in for the next wave.");
		cheer(ring, run, 4);
	}

	private static void unbench(ServerLevel ring, Run run, ServerPlayer p) {
		CompoundTag t = p.getPersistentData().getCompound(BACK);
		GameType mode = GameType.byId(t.contains("mode") ? t.getInt("mode") : GameType.SURVIVAL.getId());
		if (mode == GameType.SPECTATOR) mode = GameType.SURVIVAL;
		p.setGameMode(mode);
		Vec3 c = run.at(new Vec3(0.5 + ring.getRandom().nextInt(3) - 1, 0, 0.5 + ring.getRandom().nextInt(3) - 1));
		p.teleportTo(ring, c.x, c.y, c.z, p.getYRot(), 0f);
		p.setHealth(p.getMaxHealth());
	}

	/** Back in the world with nothing running for you there (a restart, a drop): sent home. */
	private static void login(PlayerEvent.PlayerLoggedInEvent e) {
		if (e.getEntity() instanceof ServerPlayer p && p.level().dimension() == RING && runOf(p) == null) home(p);
	}

	private static void logout(PlayerEvent.PlayerLoggedOutEvent e) {
		if (!(e.getEntity() instanceof ServerPlayer p)) return;
		Run run = runOf(p);
		if (run == null) return;
		run.members.remove(p.getUUID());
		run.benched.remove(p.getUUID());
		// back where they came from, so they wake up there
		home(p);
	}

	// ---------------------------------------------------------------- the crowd

	/** 0 a kill, 1 a wave starts, 2 a wave's won, 3 a ruler comes / they fight on, 4 one of you falls. */
	static void cheer(ServerLevel ring, Run run, int kind) {
		Net.ArenaCheer msg = new Net.ArenaCheer(run.slot, kind);
		for (ServerPlayer p : ring.players()) PacketDistributor.sendToPlayer(p, msg);
		BlockPos o = ArenaShape.origin(run.slot);
		if (kind == 2 || kind == 3)
			ring.playSound(null, o.getX(), o.getY() + 12, o.getZ(), SoundEvents.PLAYER_LEVELUP, SoundSource.AMBIENT, 1.5f, 0.6f);
	}

	private static void title(ServerPlayer p, String big, String small) {
		p.connection.send(new ClientboundSetTitlesAnimationPacket(8, 50, 15));
		p.connection.send(new ClientboundSetTitleTextPacket(Component.literal(big).withStyle(ChatFormatting.AQUA, ChatFormatting.BOLD)));
		p.connection.send(new ClientboundSetSubtitleTextPacket(Component.literal(small).withStyle(ChatFormatting.GRAY)));
	}

	// ---------------------------------------------------------------- the records

	private static void record(MinecraftServer server, Run run) {
		if (run.best <= 0 || run.names.isEmpty()) return;
		Data d = data(server);
		if (d.records.getOrDefault(run.names, 0) < run.best) {
			d.records.put(run.names, run.best);
			d.setDirty();
		}
	}

	/** Veyra's records: the best ten, yours and the adventurer parties'. */
	static void records(ServerPlayer p) {
		Map<String, Integer> all = new HashMap<>(data(p.server).records);
		for (Adventurers.Party a : Adventurers.PARTIES) {
			int rk = Math.max(0, RANKS.indexOf(Character.toUpperCase(a.rank())));
			all.merge(a.name(), 4 + rk * 6 + Math.floorMod(a.name().hashCode(), 6), Math::max);
		}
		p.sendSystemMessage(Component.literal("Veyra's records: the deepest anyone has gone in the Ring").withStyle(ChatFormatting.AQUA, ChatFormatting.BOLD));
		var top = all.entrySet().stream().sorted((a, b) -> b.getValue() - a.getValue()).limit(10).toList();
		int i = 1;
		Map<String, Integer> mine = data(p.server).records;
		for (var e : top)
			p.sendSystemMessage(Component.literal("  " + i++ + ". wave " + e.getValue() + "  " + e.getKey())
					.withStyle(mine.containsKey(e.getKey()) ? ChatFormatting.GOLD : ChatFormatting.GRAY));
		int m = milestone(p);
		p.sendSystemMessage(Component.literal("  Your milestone: " + (m == 0 ? "none yet" : "wave " + m)).withStyle(ChatFormatting.YELLOW));
	}

	// ---------------------------------------------------------------- Veyra, and her proof

	/** She stands at the second desk in the guild hall: put there if she isn't (in worlds made before her). */
	private static void veyra(MinecraftServer server) {
		int[] c = Capital.centre();
		if (c == null) return;
		ServerLevel l = server.overworld();
		double x = c[0] + VEYRA[0] + 0.5, y = Capital.FLOOR + VEYRA[1], z = c[1] + VEYRA[2] + 0.5;
		BlockPos at = BlockPos.containing(x, y, z);
		if (!l.hasChunkAt(at) || l.getNearestPlayer(x, y, z, 48, false) == null) return;
		if (!l.getEntitiesOfClass(Npc.class, new net.minecraft.world.phys.AABB(at).inflate(8), n -> "veyra".equals(n.kindId())).isEmpty()) return;
		int up = 0;
		while (up <= 3 && (!l.getBlockState(at).getCollisionShape(l, at).isEmpty() || !l.getBlockState(at.above()).getCollisionShape(l, at.above()).isEmpty())) {
			at = at.above();
			up++;
		}
		if (up > 3) return;
		// the desk is hers: whoever the city put there (a scholar, in worlds made before her) goes
		for (Npc o : l.getEntitiesOfClass(Npc.class, new net.minecraft.world.phys.AABB(at).inflate(1.5), n -> !"veyra".equals(n.kindId()))) o.discard();
		Talk.spawn(l, "veyra", "", "stand", x, at.getY(), z, 90f);
	}

	private static final Map<String, Character> BOSSES = new HashMap<>();

	/** A ruler of an E-rank gate or harder dead: whoever Veyra asked for proof and was there has it. */
	private static void proof(LivingDeathEvent e) {
		LivingEntity d = e.getEntity();
		if (!(d.level() instanceof ServerLevel l) || l.dimension() != Lairs.GATES) return;
		if (BOSSES.isEmpty())
			for (char c : RANKS.toCharArray()) for (Gear.Dungeon g : Adventurers.dungeons(c)) BOSSES.put(g.boss(), g.rank());
		Character rk = BOSSES.get(BuiltInRegistries.ENTITY_TYPE.getKey(d.getType()).getPath());
		if (rk == null || rk == 'F') return;
		for (ServerPlayer p : l.getEntitiesOfClass(ServerPlayer.class, d.getBoundingBox().inflate(64)))
			if (Coins.flag(p, "ring_asked") && !Coins.flag(p, "ring_mark")) {
				Coins.setFlag(p, "ring_mark");
				p.sendSystemMessage(Component.literal("Its blood is on you. Veyra will want to see it.").withStyle(ChatFormatting.AQUA, ChatFormatting.ITALIC));
			}
	}

	// ---------------------------------------------------------------- commands

	private static void commands(RegisterCommandsEvent e) {
		e.getDispatcher().register(Commands.literal("ashbound").then(Commands.literal("ring")
				.then(Commands.literal("continue").executes(c -> choose(c.getSource().getPlayerOrException(), true)))
				.then(Commands.literal("leave").executes(c -> choose(c.getSource().getPlayerOrException(), false)))
				.then(Commands.literal("records").executes(c -> {
					records(c.getSource().getPlayerOrException());
					return 1;
				}))
				.then(Commands.literal("start").requires(s -> s.hasPermission(2))
						.executes(c -> begin(c.getSource().getPlayerOrException(), 0) ? 1 : 0)
						.then(Commands.argument("wave", IntegerArgumentType.integer(0, 200))
								.executes(c -> begin(c.getSource().getPlayerOrException(), IntegerArgumentType.getInteger(c, "wave")) ? 1 : 0)))
				.then(Commands.literal("win").requires(s -> s.hasPermission(2)).executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					Run run = runOf(p);
					if (run == null || run.phase != FIGHT) return 0;
					for (UUID u : run.mobs) {
						Entity m = p.serverLevel().getEntity(u);
						if (m != null) m.discard();
					}
					run.mobs.clear();
					run.pending.clear();
					return 1;
				}))
				.then(Commands.literal("unlock").requires(s -> s.hasPermission(2)).executes(c -> {
					Coins.setFlag(c.getSource().getPlayerOrException(), "ring_asked");
					Coins.setFlag(c.getSource().getPlayerOrException(), "ring_mark");
					Coins.setFlag(c.getSource().getPlayerOrException(), "ring_proved");
					return 1;
				}))));
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener(Arena::tick);
		NeoForge.EVENT_BUS.addListener(EventPriority.LOWEST, Arena::died);
		NeoForge.EVENT_BUS.addListener(Arena::proof);
		NeoForge.EVENT_BUS.addListener(Arena::login);
		NeoForge.EVENT_BUS.addListener(Arena::logout);
		NeoForge.EVENT_BUS.addListener(Arena::commands);
	}
}
