package com.snoringwalrus.ashbound;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.brigadier.arguments.StringArgumentType;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.saveddata.SavedData;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.EventHooks;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/**
 * Trouble that goes up on the Guild's board by itself, with where it is: a raid on a village (a gate's monsters at its
 * walls), or a breakout (a gate's boss got out with its pack and is roaming the wilds). It's kept with the world and the
 * same for everyone. The monsters aren't there until somebody comes near, and then the place on the board follows them.
 * Ending one is what counts, whoever does it: everyone who took the request can report it.
 */
public final class Incidents {
	private Incidents() {}

	static final String TAG = "ash_incident";
	private static final int ROLL = 6000, LIFE = 48000, MAX = 4, WAKE = 56, NEAR = 320, FAR = 900, CITY = 320, RAID_RANGE = 3000;
	/** A raid is over when this few are left: the rest scatter. */
	private static final int STRAGGLERS = 2;
	/** Paid by rank, F to S. */
	private static final int[] POINTS = {40, 80, 150, 300, 550, 900, 1500}, COINS = {60, 110, 200, 380, 650, 1100, 2000}, ASH = {30, 60, 110, 200, 340, 520, 800};

	static final class Incident {
		String id, gate, place;
		boolean raid, raised, over;
		int rank, x, z;
		long until;
		final List<UUID> left = new ArrayList<>();

		Gear.Dungeon dungeon() {
			for (Gear.Dungeon d : Gear.DUNGEONS) if (d.gate().equals(gate)) return d;
			return Gear.DUNGEONS.get(0);
		}

		String title() {
			return raid ? "Raid on " + place : name(dungeon().boss()) + " Got Out";
		}
	}

	static final class State extends SavedData {
		final List<Incident> all = new ArrayList<>();
		int next;

		@Override
		public CompoundTag save(CompoundTag tag, HolderLookup.Provider reg) {
			tag.putInt("next", next);
			ListTag list = new ListTag();
			for (Incident i : all) {
				CompoundTag t = new CompoundTag();
				t.putString("id", i.id);
				t.putString("gate", i.gate);
				t.putString("place", i.place);
				t.putBoolean("raid", i.raid);
				t.putBoolean("raised", i.raised);
				t.putBoolean("over", i.over);
				t.putInt("rank", i.rank);
				t.putInt("x", i.x);
				t.putInt("z", i.z);
				t.putLong("until", i.until);
				ListTag left = new ListTag();
				for (UUID u : i.left) left.add(NbtUtils.createUUID(u));
				t.put("left", left);
				list.add(t);
			}
			tag.put("all", list);
			return tag;
		}

		static State load(CompoundTag tag, HolderLookup.Provider reg) {
			State s = new State();
			s.next = tag.getInt("next");
			for (Tag e : tag.getList("all", Tag.TAG_COMPOUND)) {
				CompoundTag t = (CompoundTag) e;
				Incident i = new Incident();
				i.id = t.getString("id");
				i.gate = t.getString("gate");
				i.place = t.getString("place");
				i.raid = t.getBoolean("raid");
				i.raised = t.getBoolean("raised");
				i.over = t.getBoolean("over");
				i.rank = t.getInt("rank");
				i.x = t.getInt("x");
				i.z = t.getInt("z");
				i.until = t.getLong("until");
				for (Tag u : t.getList("left", Tag.TAG_INT_ARRAY)) i.left.add(NbtUtils.loadUUID(u));
				s.all.add(i);
			}
			return s;
		}
	}

	private static MinecraftServer server;

	private static State state(ServerLevel any) {
		return any.getServer().overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(State::new, State::load, null), "ashbound_incidents");
	}

	/** Names from our own language file: a dedicated server has no other way to know them. */
	private static JsonObject lang;

	static String name(String boss) {
		if (lang == null) {
			try (var in = new InputStreamReader(Incidents.class.getResourceAsStream("/assets/ashbound/lang/en_us.json"), StandardCharsets.UTF_8)) {
				lang = JsonParser.parseReader(in).getAsJsonObject();
			} catch (java.io.IOException e) {
				lang = new JsonObject();
			}
		}
		var n = lang.get("entity.ashbound." + boss);
		return n != null ? n.getAsString() : boss;
	}

	// ---------------------------------------------------------------- what the board and the Journal see

	static List<Incident> live() {
		return server == null ? List.of() : state(server.overworld()).all;
	}

	private static Incident of(String id) {
		for (Incident i : live()) if (i.id.equals(id)) return i;
		return null;
	}

	static boolean over(String id) {
		Incident i = of(id);
		return i == null || i.over;
	}

	static int[] where(String id) {
		Incident i = of(id);
		return i == null ? null : new int[] {i.x, i.z};
	}

	static Guild.Quest quest(String id) {
		Incident i = of(id);
		return i == null ? null : quest(i);
	}

	static Guild.Quest quest(Incident i) {
		Gear.Dungeon d = i.dungeon();
		String text = i.raid
				? "Monsters out of " + d.title() + " are at the walls of " + i.place + ", and they've no one to stop them. Get there and drive them off."
				: name(d.boss()) + " has broken out of " + d.title() + " with its pack, and it's roaming the wilds. Find it and put it down.";
		text += " Last seen at " + i.x + ", " + i.z + ".";
		int r = Math.min(i.rank, POINTS.length - 1);
		return new Guild.Quest(i.id, i.title(), i.rank, text, true, "incident:" + i.id, 1, POINTS[r], COINS[r], ASH[r], List.of(), false,
				i.raid ? "Drive off the raid" : "Put down " + name(d.boss()), "ashbound:" + d.mats()[2], null, null);
	}

	// ---------------------------------------------------------------- what comes up

	/** Fits whoever's about: from a rank under the best of them to one over it. */
	private static List<Gear.Dungeon> suitable(MinecraftServer s) {
		int best = 0;
		for (ServerPlayer p : s.getPlayerList().getPlayers()) best = Math.max(best, Guild.of(p).rank());
		List<Gear.Dungeon> out = new ArrayList<>();
		for (Gear.Dungeon d : Gear.DUNGEONS) {
			int r = Guild.rankOf(String.valueOf(d.rank()));
			if (r >= best - 1 && r <= best + 1) out.add(d);
		}
		return out.isEmpty() ? Gear.DUNGEONS : out;
	}

	/** Dry ground out in the wilds, a fair walk from this player and clear of the city; null if none turned up. */
	private static int[] wilds(ServerLevel level, ServerPlayer p, RandomSource r) {
		int[] city = Capital.centre();
		for (int tries = 0; tries < 16; tries++) {
			double a = r.nextDouble() * Math.PI * 2, d = NEAR + r.nextDouble() * (FAR - NEAR);
			int x = p.getBlockX() + (int) (Math.cos(a) * d), z = p.getBlockZ() + (int) (Math.sin(a) * d);
			if (city != null && Math.hypot(x - city[0], z - city[1]) < CITY) continue;
			var gen = level.getChunkSource().getGenerator();
			if (gen.getBaseHeight(x, z, Heightmap.Types.OCEAN_FLOOR_WG, level, level.getChunkSource().randomState()) > level.getSeaLevel() + 1) return new int[] {x, z};
		}
		return null;
	}

	/** Goes up on the board. */
	static Incident post(ServerLevel level, boolean raid, Gear.Dungeon d, String place, int x, int z) {
		State s = state(level);
		Incident i = new Incident();
		i.id = "incident_" + s.next++;
		i.raid = raid;
		i.gate = d.gate();
		i.rank = Guild.rankOf(String.valueOf(d.rank()));
		i.place = place;
		i.x = x;
		i.z = z;
		i.until = level.getGameTime() + LIFE;
		s.all.add(i);
		s.setDirty();
		for (ServerPlayer p : level.getServer().getPlayerList().getPlayers())
			if (Guild.of(p).registered()) {
				p.sendSystemMessage(Component.literal("New at the Guild: ").withStyle(ChatFormatting.GRAY)
						.append(Component.literal(i.title()).withStyle(ChatFormatting.GOLD)).append(Component.literal("  Rank " + Guild.RANKS[i.rank]).withStyle(ChatFormatting.GRAY)));
				Story.state(p);
			}
		return i;
	}

	/** Something new, if there's room: a village if one's free, else whatever got out. */
	private static Incident roll(ServerLevel level, ServerPlayer p, Boolean raidOnly) {
		RandomSource r = level.getRandom();
		List<Gear.Dungeon> pool = suitable(level.getServer());
		Gear.Dungeon d = pool.get(r.nextInt(pool.size()));
		boolean raid = raidOnly != null ? raidOnly : r.nextBoolean();
		Capital.Site[] sites = Capital.sites;
		if (raid) {
			List<Capital.Site> close = new ArrayList<>();
			for (int k = 1; k < sites.length; k++) if (Math.hypot(sites[k].x - p.getX(), sites[k].z - p.getZ()) < RAID_RANGE) close.add(sites[k]);
			if (!close.isEmpty()) {
				Capital.Site v = close.get(r.nextInt(close.size()));
				for (Incident i : live()) if (i.raid && !i.over && i.place.equals(v.title)) return null;
				int[] centre = Waypoints.anchor(v);
				return post(level, true, d, v.title, centre[0], centre[2]);
			}
		}
		int[] at = wilds(level, p, r);
		return at == null ? null : post(level, false, d, "", at[0], at[1]);
	}

	private static Mob spawn(ServerLevel level, Incident i, String id, double x, double z) {
		var type = BuiltInRegistries.ENTITY_TYPE.getOptional(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, id)).orElse(null);
		if (type == null || !(type.create(level) instanceof Mob m)) return null;
		BlockPos top = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, BlockPos.containing(x, 0, z));
		m.moveTo(top.getX() + 0.5, top.getY(), top.getZ() + 0.5, level.getRandom().nextFloat() * 360f, 0);
		m.addTag(TAG);
		m.addTag(TAG + ":" + i.id);
		m.setPersistenceRequired();
		EventHooks.finalizeMobSpawn(m, level, level.getCurrentDifficultyAt(top), MobSpawnType.EVENT, null);
		return level.addFreshEntity(m) ? m : null;
	}

	/** Not one of them is anywhere about. */
	private static boolean nobody(ServerLevel level, Incident i) {
		for (UUID u : i.left) if (level.getEntity(u) != null) return false;
		return true;
	}

	/** Somebody's close: they're there now. */
	static void raise(ServerLevel level, Incident i, ServerPlayer by) {
		RandomSource r = level.getRandom();
		Gear.Dungeon d = i.dungeon();
		i.raised = true;
		int ring = i.raid ? 18 : 8, mobs = i.raid ? 8 + Math.min(i.rank, 4) * 2 : 3 + r.nextInt(3);
		for (int k = 0; k < mobs + 1; k++) {
			double a = r.nextDouble() * Math.PI * 2, far = ring * (0.4 + 0.6 * r.nextDouble());
			String id = k == mobs ? d.elite() : d.mobs().get(r.nextInt(d.mobs().size()));
			Mob m = spawn(level, i, id, i.x + Math.cos(a) * far, i.z + Math.sin(a) * far);
			if (m != null && i.raid) i.left.add(m.getUUID());
		}
		if (!i.raid) {
			Mob boss = spawn(level, i, d.boss(), i.x, i.z);
			if (boss != null) {
				i.left.add(boss.getUUID());
				Slumber.wake(level, boss, by);
			}
		}
		state(level).setDirty();
		level.playSound(null, i.x, by.getY(), i.z, SoundEvents.ENDER_DRAGON_GROWL, SoundSource.HOSTILE, 6f, 0.7f);
		for (ServerPlayer p : level.players())
			if (p.distanceToSqr(i.x, p.getY(), i.z) < WAKE * WAKE * 4)
				p.displayClientMessage(Component.literal(i.raid ? i.title() + "! Drive them off!" : i.title() + "!").withStyle(ChatFormatting.RED, ChatFormatting.BOLD), true);
	}

	private static void end(ServerLevel level, Incident i) {
		i.over = true;
		i.left.clear();
		i.until = level.getGameTime() + LIFE;
		state(level).setDirty();
		for (ServerPlayer p : level.getServer().getPlayerList().getPlayers()) {
			if (Guild.of(p).active(i.id) == null) continue;
			p.sendSystemMessage(Component.literal(i.title()).withStyle(ChatFormatting.GOLD).append(Component.literal(" - done! Report back to the Guild.").withStyle(ChatFormatting.GREEN)));
			Story.state(p);
		}
	}

	private static void onDeath(LivingDeathEvent e) {
		if (!e.getEntity().getTags().contains(TAG) || !(e.getEntity().level() instanceof ServerLevel level)) return;
		for (Incident i : live()) {
			if (i.over || !i.left.remove(e.getEntity().getUUID())) continue;
			state(level).setDirty();
			if (i.left.size() <= (i.raid ? STRAGGLERS : 0)) end(level, i);
			else if (e.getSource().getEntity() instanceof ServerPlayer p)
				p.displayClientMessage(Component.literal(i.title() + "  " + i.left.size() + " left").withStyle(ChatFormatting.GOLD), true);
			return;
		}
	}

	private static void tick(MinecraftServer s) {
		ServerLevel level = s.overworld();
		if (s.getPlayerList().getPlayers().isEmpty()) return;
		long now = level.getGameTime();
		State st = state(level);
		boolean changed = st.all.removeIf(i -> (i.over || !i.raised) && now > i.until);
		for (Incident i : st.all) {
			if (i.over) continue;
			if (!i.raised) {
				for (ServerPlayer p : level.players())
					if (!p.isSpectator() && p.distanceToSqr(i.x, p.getY(), i.z) < WAKE * WAKE) {
						raise(level, i, p);
						changed = true;
						break;
					}
			} else if (nobody(level, i)) {
				// someone's standing there and there's nothing to fight, so it never really came: it comes now
				for (ServerPlayer p : level.players())
					if (!p.isSpectator() && p.distanceToSqr(i.x, p.getY(), i.z) < WAKE * WAKE) {
						i.left.clear();
						raise(level, i, p);
						changed = true;
						break;
					}
			} else if (!i.left.isEmpty() && level.getEntity(i.left.get(0)) instanceof Mob m && (m.getBlockX() != i.x || m.getBlockZ() != i.z)) {
				i.x = m.getBlockX();     // the board follows them about
				i.z = m.getBlockZ();
				changed = true;
			}
		}
		if (changed) st.setDirty();
		if (now % ROLL < 20 && st.all.stream().filter(i -> !i.over).count() < MAX) {
			var ps = s.getPlayerList().getPlayers();
			ServerPlayer p = ps.get(level.getRandom().nextInt(ps.size()));
			if (p.level() == level) roll(level, p, null);
		}
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener(Incidents::onDeath);
		NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post e) -> {
			server = e.getServer();
			if (server.getTickCount() % 20 == 0) tick(server);
		});
		// /ashbound incident raid|breakout: one now, to test with
		NeoForge.EVENT_BUS.addListener((RegisterCommandsEvent e) -> e.getDispatcher().register(Commands.literal("ashbound").requires(s -> s.hasPermission(2))
				.then(Commands.literal("incident").then(Commands.argument("what", StringArgumentType.word()).executes(s -> {
					ServerPlayer p = s.getSource().getPlayerOrException();
					Incident i = roll(s.getSource().getServer().overworld(), p, StringArgumentType.getString(s, "what").equals("raid"));
					s.getSource().sendSystemMessage(Component.literal(i == null ? "Nothing came up." : i.title() + " at " + i.x + ", " + i.z));
					return 1;
				})))));
	}
}
