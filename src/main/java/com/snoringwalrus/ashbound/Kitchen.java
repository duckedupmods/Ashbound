package com.snoringwalrus.ashbound;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Display;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Cooking takes time (11/7, the user: "have time to do the recipes, show it cooking there with a timer, faster the more you make it").
 * What a bench makes goes on the fire at that station: the dish sits on it with a countdown over it, one after another for a batch, and
 * waits in the station's Ready tray once done (a chime, a line to whoever's cooking). Anyone at the station can take what's ready.
 * How long: {@link #seconds} from the recipe's size and level, cut by your mastery of that recipe (made.GOOD in the trade state).
 */
public final class Kitchen {
	private Kitchen() {}

	/** One thing on the fire: what comes out and the game tick it's done. */
	public record Out(ItemStack item, long start, long done) {}

	static final class Job {
		ResourceKey<Level> dim;
		BlockPos key;                 // the station's corner (a big sculpted one: the corner of all its pieces)
		Vec3 dishAt, labelAt;
		Trades.Kind kind;
		UUID owner;
		final List<Out> outs = new ArrayList<>();
		UUID dish, label;
		int announced;                // how many of outs have been announced ready
	}

	/** Mastery: stars at 5, 15, 35 and 70 made; each cuts the time. */
	public static final int[] STARS_AT = {5, 15, 35, 70};
	public static final double[] SPEED = {1.0, 0.85, 0.7, 0.55, 0.4};
	/** The most things on one station's fire and tray at once. */
	public static final int MOST = 32;

	private static final Map<String, Job> JOBS = new LinkedHashMap<>();

	public static int stars(int made) {
		int s = 0;
		while (s < STARS_AT.length && made >= STARS_AT[s]) s++;
		return s;
	}

	/** How long a good takes at a mastery: 10 s, 5 more for each thing in it, half its level more; down to 40% at four stars. */
	public static int seconds(Trades.Good g, int stars) {
		return (int) Math.round((10 + 5 * g.needs().size() + g.level() / 2.0) * SPEED[Math.max(0, Math.min(4, stars))]);
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener(Kitchen::tick);
		NeoForge.EVENT_BUS.addListener(Kitchen::joined);
		NeoForge.EVENT_BUS.addListener((net.neoforged.neoforge.event.server.ServerStoppedEvent e) -> reset());
	}

	// ---------------------------------------------------------------- where a station is

	/** A station's key (the corner of all its pieces) and its box: a big sculpted one is many blocks of one kind. */
	static BlockPos[] box(Level level, BlockPos at) {
		Block b = level.getBlockState(at).getBlock();
		BlockPos lo = at, hi = at;
		Set<BlockPos> seen = new HashSet<>();
		ArrayDeque<BlockPos> todo = new ArrayDeque<>();
		todo.add(at);
		seen.add(at);
		while (!todo.isEmpty() && seen.size() < 40) {
			BlockPos p = todo.poll();
			lo = new BlockPos(Math.min(lo.getX(), p.getX()), Math.min(lo.getY(), p.getY()), Math.min(lo.getZ(), p.getZ()));
			hi = new BlockPos(Math.max(hi.getX(), p.getX()), Math.max(hi.getY(), p.getY()), Math.max(hi.getZ(), p.getZ()));
			for (Direction d : Direction.values()) {
				BlockPos n = p.relative(d);
				if (!seen.contains(n) && n.distManhattan(at) <= 6 && level.getBlockState(n).getBlock() == b) {
					seen.add(n);
					todo.add(n);
				}
			}
		}
		return new BlockPos[] {lo, hi};
	}

	private static String id(ResourceKey<Level> dim, BlockPos key) {
		return dim.location() + "|" + key.asLong();
	}

	static Job job(Level level, BlockPos pos) {
		BlockPos[] b = box(level, pos);
		return JOBS.get(id(level.dimension(), b[0]));
	}

	// ---------------------------------------------------------------- cooking

	/** Puts a made thing on the station's fire behind what's there; false when the station's full. */
	static boolean add(ServerPlayer p, BlockPos pos, Trades.Kind kind, ItemStack made, int seconds) {
		ServerLevel level = p.serverLevel();
		BlockPos[] b = box(level, pos);
		String k = id(level.dimension(), b[0]);
		Job j = JOBS.get(k);
		if (j == null) {
			j = new Job();
			j.dim = level.dimension();
			j.key = b[0];
			j.kind = kind;
			double cx = (b[0].getX() + b[1].getX() + 1) / 2.0, cz = (b[0].getZ() + b[1].getZ() + 1) / 2.0;
			int h = b[1].getY() - b[0].getY() + 1;
			j.dishAt = new Vec3(cx, b[0].getY() + (h >= 3 ? 1.45 : h + 0.1), cz);
			j.labelAt = new Vec3(cx, b[1].getY() + 1.45, cz);
			JOBS.put(k, j);
		}
		if (j.outs.size() >= MOST) return false;
		j.owner = p.getUUID();
		long now = level.getGameTime();
		long start = now;
		for (Out o : j.outs) start = Math.max(start, o.done());
		j.outs.add(new Out(made, start, start + seconds * 20L));
		dirty(p.server);
		return true;
	}

	/** Gives whoever asks what's ready at their open bench's station. */
	static void collect(ServerPlayer p) {
		if (!(p.containerMenu instanceof Trades.Bench b) || b.pos == null) return;
		Job j = job(p.level(), b.pos);
		if (j == null) return;
		long now = p.level().getGameTime();
		int n = 0;
		for (var it = j.outs.iterator(); it.hasNext();) {
			Out o = it.next();
			if (o.done() > now) continue;
			ItemStack s = o.item().copy();
			if (!p.getInventory().add(s)) p.drop(s, false);
			it.remove();
			j.announced = Math.max(0, j.announced - 1);
			n++;
		}
		if (n > 0) {
			p.playNotifySound(SoundEvents.ITEM_PICKUP, SoundSource.PLAYERS, 0.6f, 1.0f);
			dirty(p.server);
		}
		send(p);
	}

	/** The open bench's station's fire and tray, to its player. */
	static void send(ServerPlayer p) {
		if (!(p.containerMenu instanceof Trades.Bench b) || b.pos == null) return;
		Job j = job(p.level(), b.pos);
		List<ItemStack> items = new ArrayList<>();
		List<Long> start = new ArrayList<>(), done = new ArrayList<>();
		if (j != null)
			for (Out o : j.outs) {
				items.add(o.item());
				start.add(o.start());
				done.add(o.done());
			}
		PacketDistributor.sendToPlayer(p, new Net.KitchenState(items, start, done, p.level().getGameTime()));
	}

	// ---------------------------------------------------------------- every half second

	private static void tick(ServerTickEvent.Post e) {
		MinecraftServer server = e.getServer();
		if (server.getTickCount() % 10 != 0) return;
		if (!loaded) load(server);
		for (var it = JOBS.values().iterator(); it.hasNext();) {
			Job j = it.next();
			ServerLevel level = server.getLevel(j.dim);
			if (level == null) continue;
			if (j.outs.isEmpty()) {
				remove(level, j);
				it.remove();
				dirty(server);
				continue;
			}
			if (!level.isLoaded(j.key)) continue;
			long now = level.getGameTime();
			int ready = 0;
			Out cooking = null;
			for (Out o : j.outs) {
				if (o.done() <= now) ready++;
				else if (cooking == null) cooking = o;
			}
			if (ready > j.announced) {                                  // something just came off the fire
				level.playSound(null, j.key, j.kind == Trades.Kind.MEAL ? SoundEvents.NOTE_BLOCK_BELL.value() : SoundEvents.NOTE_BLOCK_CHIME.value(),
						SoundSource.BLOCKS, 0.8f, 1.2f);
				ServerPlayer o = server.getPlayerList().getPlayer(j.owner);
				if (o != null && cooking == null)
					o.displayClientMessage(Component.literal(j.outs.get(0).item().getHoverName().getString() + (ready > 1 ? " and the rest" : "") + " ready at the "
							+ Trades.trade(j.kind.trade).bench()).withStyle(ChatFormatting.GOLD), true);
				j.announced = ready;
			}
			Out show = cooking != null ? cooking : j.outs.get(0);
			Display.ItemDisplay dish = dish(level, j);
			if (dish != null) {
				dish.getSlot(0).set(show.item().copyWithCount(1));
				dish.setGlowingTag(cooking == null);
			}
			Display.TextDisplay label = label(level, j);
			if (label != null) setText(label, cooking == null
					? Component.literal("Ready: " + ready + "  (open to take)").withStyle(ChatFormatting.GREEN)
					: Component.literal(show.item().getHoverName().getString() + "  " + clock((cooking.done() - now) / 20)).withStyle(ChatFormatting.GOLD)
							.append(Component.literal(j.outs.size() - ready > 1 ? "  +" + (j.outs.size() - ready - 1) : "").withStyle(ChatFormatting.GRAY))
							.append(Component.literal(ready > 0 ? "  Ready " + ready : "").withStyle(ChatFormatting.GREEN)));
			if (cooking != null) {
				Vec3 a = j.dishAt;
				switch (j.kind) {
					case MEAL -> {
						level.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, a.x, a.y + 0.3, a.z, 1, 0.1, 0.05, 0.1, 0.01);
						level.sendParticles(ParticleTypes.BUBBLE_POP, a.x, a.y + 0.1, a.z, 3, 0.15, 0.02, 0.15, 0.0);
					}
					case BREW -> level.sendParticles(ParticleTypes.CLOUD, a.x, a.y + 0.4, a.z, 1, 0.1, 0.05, 0.1, 0.0);
					case ELIXIR -> level.sendParticles(ParticleTypes.WITCH, a.x, a.y + 0.2, a.z, 2, 0.15, 0.1, 0.15, 0.0);
				}
			}
		}
		for (ServerPlayer p : server.getPlayerList().getPlayers()) if (p.containerMenu instanceof Trades.Bench b && b.pos != null) send(p);
	}

	public static String clock(long s) {
		s = Math.max(0, s);
		return s / 60 + ":" + (s % 60 < 10 ? "0" : "") + s % 60;
	}

	private static void setText(Display.TextDisplay d, Component c) {
		CompoundTag t = new CompoundTag();
		d.saveWithoutId(t);
		t.putString("text", Component.Serializer.toJson(c, d.registryAccess()));
		d.load(t);
	}

	private static Display.ItemDisplay dish(ServerLevel level, Job j) {
		Entity e = j.dish == null ? null : level.getEntity(j.dish);
		if (e instanceof Display.ItemDisplay d) return d;
		Display.ItemDisplay d = EntityType.ITEM_DISPLAY.create(level);
		if (d == null) return null;
		CompoundTag t = new CompoundTag();
		t.putString("billboard", "vertical");
		CompoundTag tr = new CompoundTag();
		tr.put("left_rotation", Capital.floats(0, 0, 0, 1));
		tr.put("right_rotation", Capital.floats(0, 0, 0, 1));
		tr.put("translation", Capital.floats(0, 0, 0));
		tr.put("scale", Capital.floats(0.55f, 0.55f, 0.55f));
		t.put("transformation", tr);
		d.load(t);
		d.addTag("ash_kitchen");
		d.moveTo(j.dishAt.x, j.dishAt.y, j.dishAt.z, 0, 0);
		level.addFreshEntity(d);
		j.dish = d.getUUID();
		dirty(level.getServer());
		return d;
	}

	private static Display.TextDisplay label(ServerLevel level, Job j) {
		Entity e = j.label == null ? null : level.getEntity(j.label);
		if (e instanceof Display.TextDisplay d) return d;
		Display.TextDisplay d = EntityType.TEXT_DISPLAY.create(level);
		if (d == null) return null;
		CompoundTag t = new CompoundTag();
		t.putString("billboard", "center");
		t.putInt("background", 0x90100A06);
		t.putFloat("view_range", 0.6f);
		d.load(t);
		d.addTag("ash_kitchen");
		d.moveTo(j.labelAt.x, j.labelAt.y, j.labelAt.z, 0, 0);
		level.addFreshEntity(d);
		j.label = d.getUUID();
		dirty(level.getServer());
		return d;
	}

	private static void remove(ServerLevel level, Job j) {
		for (UUID u : new UUID[] {j.dish, j.label}) {
			Entity e = u == null ? null : level.getEntity(u);
			if (e != null) e.discard();
		}
	}

	/** A dish or label left from a job that's gone (taken while its chunk was away): cleared as it loads. */
	private static void joined(EntityJoinLevelEvent e) {
		if (e.getLevel().isClientSide() || !e.getEntity().getTags().contains("ash_kitchen")) return;
		UUID u = e.getEntity().getUUID();
		for (Job j : JOBS.values()) if (u.equals(j.dish) || u.equals(j.label)) return;
		if (loaded) e.setCanceled(true);
	}

	// ---------------------------------------------------------------- kept with the world

	private static boolean loaded;
	private static Data data;

	private static void dirty(MinecraftServer s) {
		if (data != null) data.setDirty();
	}

	private static void load(MinecraftServer server) {
		loaded = true;
		JOBS.clear();
		data = server.overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(Data::new, Data::read, null), "ashbound_kitchen");
	}

	/** Forgets the last world's jobs (a new world in the same game). */
	static void reset() {
		loaded = false;
		data = null;
		JOBS.clear();
	}

	static final class Data extends SavedData {
		static Data read(CompoundTag t, HolderLookup.Provider reg) {
			for (Tag x : t.getList("jobs", Tag.TAG_COMPOUND)) {
				CompoundTag c = (CompoundTag) x;
				Job j = new Job();
				j.dim = ResourceKey.create(Registries.DIMENSION, ResourceLocation.parse(c.getString("dim")));
				j.key = BlockPos.of(c.getLong("key"));
				j.kind = Trades.Kind.values()[c.getInt("kind")];
				j.dishAt = new Vec3(c.getDouble("dx"), c.getDouble("dy"), c.getDouble("dz"));
				j.labelAt = new Vec3(c.getDouble("lx"), c.getDouble("ly"), c.getDouble("lz"));
				if (c.hasUUID("owner")) j.owner = c.getUUID("owner");
				if (c.hasUUID("dish")) j.dish = c.getUUID("dish");
				if (c.hasUUID("label")) j.label = c.getUUID("label");
				j.announced = c.getInt("announced");
				for (Tag y : c.getList("outs", Tag.TAG_COMPOUND)) {
					CompoundTag o = (CompoundTag) y;
					ItemStack s = ItemStack.parseOptional(reg, o.getCompound("item"));
					if (!s.isEmpty()) j.outs.add(new Out(s, o.contains("start") ? o.getLong("start") : o.getLong("done") - 400, o.getLong("done")));
				}
				JOBS.put(id(j.dim, j.key), j);
			}
			return new Data();
		}

		@Override
		public CompoundTag save(CompoundTag t, HolderLookup.Provider reg) {
			ListTag l = new ListTag();
			for (Job j : JOBS.values()) {
				CompoundTag c = new CompoundTag();
				c.putString("dim", j.dim.location().toString());
				c.putLong("key", j.key.asLong());
				c.putInt("kind", j.kind.ordinal());
				c.putDouble("dx", j.dishAt.x);
				c.putDouble("dy", j.dishAt.y);
				c.putDouble("dz", j.dishAt.z);
				c.putDouble("lx", j.labelAt.x);
				c.putDouble("ly", j.labelAt.y);
				c.putDouble("lz", j.labelAt.z);
				if (j.owner != null) c.putUUID("owner", j.owner);
				if (j.dish != null) c.putUUID("dish", j.dish);
				if (j.label != null) c.putUUID("label", j.label);
				c.putInt("announced", j.announced);
				ListTag os = new ListTag();
				for (Out o : j.outs) {
					CompoundTag ot = new CompoundTag();
					ot.put("item", o.item().save(reg));
					ot.putLong("start", o.start());
					ot.putLong("done", o.done());
					os.add(ot);
				}
				c.put("outs", os);
				l.add(c);
			}
			t.put("jobs", l);
			return t;
		}
	}
}
