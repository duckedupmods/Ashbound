package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.function.Supplier;

import javax.annotation.Nullable;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
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
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.neoforged.neoforge.registries.DeferredItem;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.EventHooks;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.level.BlockEvent;
import net.neoforged.neoforge.event.level.ExplosionEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/**
 * Boss arenas: a main-story boss's sigil, handed to Veyra in the guild hall, sends the whole party (everyone near) into
 * that boss's own arena out in the void, each its own dimension and its own spectacle. The boss comes up after a breath;
 * fall and you watch (a spectator) until it's over; the whole party down and it's lost; the boss dead and everyone who
 * was there has beaten it (its first time is the story's beat), its spoils rain down, and Veyra pulls you home. The sigil
 * isn't used up: a rematch whenever you like. Built like the Ashen Ring (Arena): each arena raised chunk by chunk, once,
 * in slots along x so parties don't meet; nothing in an arena can be broken.
 *
 * The first: the Founder's Brand -> the Kiln-Father's Hearth (HearthShape) -> Ossric; beating him there opens the Cold
 * Forge's Joining.
 */
public final class BossArenas {
	private BossArenas() {}

	static final String TAG = "ashbound_boss_arena";
	static final int SLOTS = 4, SPACING = 1024, FLOOR = 160, VERSION = 1, COME = 100, LINGER = 6000, LAST_CALL = 1200;
	/** Veyra's door home, opened when the boss dies: south of the Brand, out of the way of the spoils */
	static final Vec3 DOOR = new Vec3(0.5, 0, -12.5);

	/**
	 * One arena: its sigil, its dimension, its shape (relative to the origin, floor top at y 0), its boss and where it comes
	 * up, the gate whose spoils it drops, what a win means, and what hurts in there (each tick, per player).
	 */
	record Def(String id, String title, String sub, Supplier<Item> sigil, ResourceKey<Level> dim, Consumer<ArenaShape.Sink> shape, int reach,
			String boss, Vec3 bossAt, float bossYaw, String gate, Consumer<ServerPlayer> won, Hazard hazard, List<Vec3> smoke) {}

	interface Hazard {
		void at(ServerPlayer p, Vec3 rel);
	}

	static final Map<String, Def> DEFS = new LinkedHashMap<>();

	/** The Archmage's sigil for the Graveyard of Ships (Act II); kept, for rematches. */
	public static final DeferredItem<Item> DROWNED_SIGIL = Weapons.ITEMS.registerItem("drowned_sigil",
			p -> new Item(p.rarity(Rarity.EPIC).stacksTo(1).fireResistant()));
	/** Veyra's sigils for the Astral Rings (Act IV); kept, for rematches. */
	public static final DeferredItem<Item> SIGIL_MOTH = Weapons.ITEMS.registerItem("sigil_moth", p -> new Item(p.rarity(Rarity.EPIC).stacksTo(1).fireResistant()));
	public static final DeferredItem<Item> SIGIL_KNIGHT = Weapons.ITEMS.registerItem("sigil_knight", p -> new Item(p.rarity(Rarity.EPIC).stacksTo(1).fireResistant()));
	public static final DeferredItem<Item> SIGIL_MAGUS = Weapons.ITEMS.registerItem("sigil_magus", p -> new Item(p.rarity(Rarity.EPIC).stacksTo(1).fireResistant()));
	/** The King's key to the Crown Gate (Act V); kept, for rematches. */
	public static final DeferredItem<Item> CROWN_KEY = Weapons.ITEMS.registerItem("crown_key", p -> new Item(p.rarity(Rarity.EPIC).stacksTo(1).fireResistant()));
	/** The Archmage's sigil for the Grey Fold (Act III); kept, for rematches. */
	public static final DeferredItem<Item> ASHEN_SIGIL = Weapons.ITEMS.registerItem("ashen_sigil",
			p -> new Item(p.rarity(Rarity.EPIC).stacksTo(1).fireResistant()));

	static ResourceKey<Level> dim(String id) {
		return ResourceKey.create(Registries.DIMENSION, ResourceLocation.fromNamespaceAndPath(Ashbound.ID, id));
	}

	static void defs() {
		if (!DEFS.isEmpty()) return;
		DEFS.put("hearth", new Def("hearth", "THE KILN-FATHER'S HEARTH", "Something a long way off picks up its hammer.", ColdForge.BRAND,
				dim("kiln_hearth"), HearthShape::blocks, HearthShape.R_RIM + 40,
				"ossric", HearthShape.BOSS, 180f, "foundry",
				p -> {
					if (!Coins.flag(p, "cold_proved")) {
						Coins.setFlag(p, "cold_proved");
						Story.mark(p, "cold/proved");
						p.sendSystemMessage(Component.literal("The Kiln-Father kneels. Back in the city, the Cold Forge's great hands open: the Joining is yours.")
								.withStyle(ChatFormatting.GOLD));
					}
				},
				(p, rel) -> {
					// the slag channel burns and drags
					double r = Math.hypot(rel.x, rel.z);
					if (r > HearthShape.R_FLOOR - 0.3 && r < HearthShape.R_SLAG + 0.3 && rel.y < -0.5) {
						if (p.tickCount % 10 == 0) p.hurt(p.damageSources().lava(), 3f);
						p.igniteForSeconds(4);
						p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 30, 2, false, false));
					}
				}, HearthShape.STACKS));
		DEFS.put("wreck", new Def("wreck", "THE GRAVEYARD OF SHIPS", "Out past the rim, something huge moves under the water.", DROWNED_SIGIL,
				dim("ship_graveyard"), WreckShape::blocks, WreckShape.R_SEA + 4,
				"wreck_mother", WreckShape.BOSS, 180f, "tide_chapel",
				p -> {
					if (!Coins.flag(p, "wreck_proved")) {
						Coins.setFlag(p, "wreck_proved");
						p.sendSystemMessage(Component.literal("The Wreck-Mother sinks into the black water, and something under the deck goes cold and still.")
								.withStyle(ChatFormatting.GOLD));
					}
				},
				(p, rel) -> {
					// every twenty seconds a wave comes over the rim's gaps: it knocks you inward and off your feet
					double r = Math.hypot(rel.x, rel.z);
					if (r < WreckShape.R_DECK - 8 || rel.y < -2 || rel.y > 4) return;
					long t = p.level().getGameTime() % 400;
					if (t > 30 || !WreckShape.gap(Math.atan2(rel.z, rel.x))) return;
					if (t == 0) p.serverLevel().playSound(null, p.blockPosition(), SoundEvents.GENERIC_SPLASH, SoundSource.AMBIENT, 2f, 0.5f);
					p.push(-rel.x / r * 0.25, 0.05, -rel.z / r * 0.25);
					p.hurtMarked = true;
					p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 1, false, false));
					if (t % 4 == 0) p.serverLevel().sendParticles(ParticleTypes.SPLASH, p.getX(), p.getY() + 0.5, p.getZ(), 12, 0.6, 0.4, 0.6, 0.2);
				}, List.of()));
		DEFS.put("fold", new Def("fold", "THE GREY FOLD", "Somewhere in the ash, a bell is ringing.", ASHEN_SIGIL,
				dim("grey_fold"), GreyFoldShape::blocks, GreyFoldShape.R_EDGE + 30,
				"ash_shepherd", GreyFoldShape.BOSS, 180f, "rimeholt",
				p -> {
					if (!Coins.flag(p, "fold_proved")) {
						Coins.setFlag(p, "fold_proved");
						p.sendSystemMessage(Component.literal("The Ash Shepherd comes apart for good, and for a moment the ash stops falling.")
								.withStyle(ChatFormatting.GOLD));
					}
				},
				(p, rel) -> {
					// every half a minute a gust of ash blows across the square: it shoves, and you can't see far in it
					long t = p.level().getGameTime() % 600;
					if (t > 60) return;
					double a = (p.level().getGameTime() / 600) * 2.1;          // a new way each time
					if (t == 0) p.serverLevel().playSound(null, p.blockPosition(), SoundEvents.ELYTRA_FLYING, SoundSource.AMBIENT, 0.6f, 0.5f);
					p.push(Math.cos(a) * 0.04, 0, Math.sin(a) * 0.04);
					p.hurtMarked = true;
					if (t % 20 == 0) p.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 40, 0, false, false));
					if (t % 3 == 0) p.serverLevel().sendParticles(ParticleTypes.ASH, p.getX(), p.getY() + 1, p.getZ(), 30, 3, 1.5, 3, 0.02);
				}, List.of()));
		astral("moth", "THE MOTH'S RING", "Far off, something vast unfolds its wings across the stars.", SIGIL_MOTH, AstralShape::moth, "nebula_moth", "bloodmoon_court");
		astral("knight", "THE KNIGHT'S RING", "Somewhere above you, a constellation stands up.", SIGIL_KNIGHT, AstralShape::knight, "constellation_knight", "obsidian_labyrinth");
		DEFS.put("crown", new Def("crown", "THE CROWN GATE", "Under the keep, under everything, a hammer starts to ring.", CROWN_KEY,
				dim("crown_gate"), CrownShape::blocks, 135, "founder_king", CrownShape.BOSS, 180f, "eclipse_cathedral",
				p -> {
					if (!Coins.flag(p, "founder_dead")) {
						Coins.setFlag(p, "founder_dead");
						p.sendSystemMessage(Component.literal("The Founder-King falls, and the five Fires burn on without him. The oldest crack in the world is only a crack now.")
								.withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD));
					}
				},
				(p, rel) -> {
					// the Fires mend whoever stands by one; and the Founder's hammer brings sparks down where you stand
					if (p.tickCount % 20 == 0)
						for (Vec3 b : CrownShape.BRAZIERS)
							if (Math.hypot(rel.x - b.x, rel.z - b.z) < 4.5) {
								p.heal(2f);
								p.serverLevel().sendParticles(ParticleTypes.HAPPY_VILLAGER, p.getX(), p.getY() + 1, p.getZ(), 4, 0.4, 0.6, 0.4, 0);
							}
					starfall(p, rel);
				}, List.of()));
		astral("magus", "THE MAGUS'S RING", "The planets turn, and something at their middle turns to look at you.", SIGIL_MAGUS, AstralShape::magus, "orrery_magus", "abyssal_lighthouse");
	}

	/** An Astral Ring (Act IV): its flag on a win, and stars falling where you stand. */
	private static void astral(String id, String title, String sub, Supplier<Item> sigil, Consumer<ArenaShape.Sink> shape, String boss, String gate) {
		DEFS.put(id, new Def(id, title, sub, sigil, dim("astral_" + id), shape, 140, boss, AstralShape.BOSS, 180f, gate,
				p -> {
					if (!Coins.flag(p, "astral_" + id)) {
						Coins.setFlag(p, "astral_" + id);
						p.sendSystemMessage(Component.literal("The star-ember it kept drops into your hands, and burns cold.").withStyle(ChatFormatting.GOLD));
					}
				}, BossArenas::starfall, List.of()));
	}

	/** Every ten seconds a star falls on the spot each player stood a breath ago: the mark shows first, then it strikes. */
	private static void starfall(ServerPlayer p, Vec3 rel) {
		long t = p.level().getGameTime() % 200;
		var tag = p.getPersistentData();
		ServerLevel l = p.serverLevel();
		if (t == 0) {
			tag.putDouble("ash_star_x", p.getX() + (p.getRandom().nextDouble() - 0.5) * 3);
			tag.putDouble("ash_star_z", p.getZ() + (p.getRandom().nextDouble() - 0.5) * 3);
			tag.putDouble("ash_star_y", p.getY());
		}
		if (!tag.contains("ash_star_x")) return;
		double x = tag.getDouble("ash_star_x"), y = tag.getDouble("ash_star_y"), z = tag.getDouble("ash_star_z");
		if (t < 30 && t % 3 == 0) {
			for (int i = 0; i < 12; i++) {
				double a = i / 12.0 * Math.PI * 2;
				l.sendParticles(p, ParticleTypes.END_ROD, true, x + Math.cos(a) * 2.5, y + 0.1, z + Math.sin(a) * 2.5, 1, 0, 0, 0, 0);
			}
			l.sendParticles(p, ParticleTypes.END_ROD, true, x, y + 30 - t, z, 2, 0.2, 0.5, 0.2, 0);
		}
		if (t == 30) {
			l.sendParticles(ParticleTypes.FLASH, x, y + 0.5, z, 1, 0, 0, 0, 0);
			l.sendParticles(ParticleTypes.END_ROD, x, y + 0.5, z, 40, 1.2, 0.4, 1.2, 0.2);
			l.playSound(null, x, y, z, SoundEvents.AMETHYST_BLOCK_BREAK, SoundSource.HOSTILE, 2f, 0.5f);
			if (Math.hypot(p.getX() - x, p.getZ() - z) < 2.5 && Math.abs(p.getY() - y) < 3) {
				p.hurt(p.damageSources().magic(), 10f);
				p.push((p.getX() - x) * 0.3, 0.5, (p.getZ() - z) * 0.3);
				p.hurtMarked = true;
			}
			tag.remove("ash_star_x");
		}
	}

	static boolean isArena(ResourceKey<Level> d) {
		defs();
		if (d == Arena.RING) return true;
		for (Def def : DEFS.values()) if (def.dim() == d) return true;
		return false;
	}

	@Nullable
	static Def defOf(ResourceKey<Level> d) {
		defs();
		for (Def def : DEFS.values()) if (def.dim() == d) return def;
		return null;
	}

	static final int COMING = 0, FIGHT = 1, WON = 2, BUILDING = 3;

	static final class Run {
		final Def def;
		final int slot;
		final Set<UUID> members = new LinkedHashSet<>(), fallen = new HashSet<>();
		int phase = BUILDING;
		long until;
		@Nullable UUID boss;
		/** each player's spoils still on the ground (item entities), swept into their packs when they go */
		final Map<UUID, List<UUID>> spoils = new HashMap<>();
		boolean warned;
		/** Veyra's door: a gate's tear, the way out (11/7: the ring of sparks it was couldn't be seen from ten blocks) */
		@Nullable UUID gate;

		Run(Def def, int slot) {
			this.def = def;
			this.slot = slot;
		}

		BlockPos origin() {
			return new BlockPos(slot * SPACING, FLOOR, 0);
		}

		Vec3 at(Vec3 rel) {
			BlockPos o = origin();
			return new Vec3(o.getX() + rel.x, o.getY() + rel.y, o.getZ() + rel.z);
		}
	}

	static final List<Run> RUNS = new ArrayList<>();

	// ---------------------------------------------------------------- what's kept: which slots are raised

	static final class Data extends SavedData {
		final Map<String, Integer> built = new HashMap<>();

		@Override
		public CompoundTag save(CompoundTag tag, HolderLookup.Provider reg) {
			CompoundTag b = new CompoundTag();
			built.forEach(b::putInt);
			tag.put("built", b);
			return tag;
		}

		static Data load(CompoundTag tag, HolderLookup.Provider reg) {
			Data d = new Data();
			CompoundTag b = tag.getCompound("built");
			for (String k : b.getAllKeys()) d.built.put(k, b.getInt(k));
			return d;
		}
	}

	static Data data(MinecraftServer server) {
		return server.overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(Data::new, Data::load, null), "ashbound_boss_arenas");
	}

	// ---------------------------------------------------------------- raising an arena, chunk by chunk, never waiting on a load

	private static final Map<String, int[][]> SHAPES = new HashMap<>();
	private static final Map<String, BlockState[]> STATES = new HashMap<>();

	/** The arena's blocks as [x, y, z] in chunk order, bottom up in each (the last word on a spot wins). */
	static int[][] shape(Def def) {
		int[][] got = SHAPES.get(def.id());
		if (got != null) return got;
		Map<Long, int[]> at = new LinkedHashMap<>();
		List<BlockState> st = new ArrayList<>();
		def.shape().accept((x, y, z, s) -> {
			long k = BlockPos.asLong(x, y, z);
			at.put(k, new int[] {x, y, z, st.size()});
			st.add(s);
		});
		List<int[]> l = new ArrayList<>(at.values());
		l.sort((a, b) -> {
			int c = Integer.compare(a[0] >> 4, b[0] >> 4);
			if (c == 0) c = Integer.compare(a[2] >> 4, b[2] >> 4);
			return c != 0 ? c : Integer.compare(a[1], b[1]);
		});
		int[][] out = new int[l.size()][];
		BlockState[] ss = new BlockState[l.size()];
		for (int i = 0; i < out.length; i++) {
			int[] a = l.get(i);
			out[i] = new int[] {a[0], a[1], a[2]};
			ss[i] = st.get(a[3]);
		}
		SHAPES.put(def.id(), out);
		STATES.put(def.id(), ss);
		return out;
	}

	private static final class Job {
		final Run run;
		int next;

		Job(Run run) {
			this.run = run;
		}
	}

	@Nullable
	private static Job job;

	static void keep(ServerLevel l, Run run, boolean on) {
		BlockPos o = run.origin();
		int r = run.def.reach();
		for (int cx = (o.getX() - r) >> 4; cx <= (o.getX() + r) >> 4; cx++)
			for (int cz = (o.getZ() - r) >> 4; cz <= (o.getZ() + r) >> 4; cz++) l.setChunkForced(cx, cz, on);
	}

	private static void build(MinecraftServer server) {
		Job j = job;
		if (j == null) return;
		Run run = j.run;
		ServerLevel l = server.getLevel(run.def.dim());
		if (l == null) {
			job = null;
			return;
		}
		int[][] xyz = shape(run.def);
		BlockState[] st = STATES.get(run.def.id());
		BlockPos o = run.origin();
		BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
		long stop = System.nanoTime() + 20_000_000L;
		while (j.next < xyz.length && System.nanoTime() < stop) {
			int cx = (o.getX() + xyz[j.next][0]) >> 4, cz = (o.getZ() + xyz[j.next][2]) >> 4;
			if (!l.hasChunk(cx, cz)) {
				l.setChunkForced(cx, cz, true);
				break;
			}
			while (j.next < xyz.length && ((o.getX() + xyz[j.next][0]) >> 4) == cx && ((o.getZ() + xyz[j.next][2]) >> 4) == cz) {
				p.set(o.getX() + xyz[j.next][0], o.getY() + xyz[j.next][1], o.getZ() + xyz[j.next][2]);
				l.setBlock(p, st[j.next], Block.UPDATE_CLIENTS);
				j.next++;
			}
		}
		if (server.getTickCount() % 10 == 0)
			for (ServerPlayer m : online(server, run))
				m.displayClientMessage(Component.literal("Veyra's circle flares... the way opens " + j.next * 100 / xyz.length + "%")
						.withStyle(ChatFormatting.AQUA, ChatFormatting.ITALIC), true);
		if (j.next < xyz.length) return;
		job = null;
		data(server).built.put(run.def.id() + ":" + run.slot, VERSION);
		data(server).setDirty();
		arrive(l, run);
	}

	// ---------------------------------------------------------------- going in

	/** Veyra's word ("bossarena:enter" in her talk): the sigil in your hand, or else the first one you carry. */
	static void act(ServerPlayer p, String what) {
		if (!what.startsWith("enter")) return;
		defs();
		Def def = null;
		if (what.startsWith("enter:")) {                       // a named arena, its sigil carried
			Def d = DEFS.get(what.substring(6));
			if (d != null && GateForge.carried(p, d.sigil().get()) > 0) def = d;
		}
		if (def == null) for (Def d : DEFS.values()) if (p.getMainHandItem().is(d.sigil().get())) def = d;
		if (def == null)
			for (Def d : DEFS.values()) if (GateForge.carried(p, d.sigil().get()) > 0) {
				def = d;
				break;
			}
		if (def == null) {
			p.sendSystemMessage(Component.literal("Veyra: \"A sigil, ringwalker. Without one I've nowhere to send you.\"").withStyle(ChatFormatting.GRAY));
			return;
		}
		begin(p, def);
	}

	@Nullable
	static Run runOf(Entity p) {
		for (Run r : RUNS) if (r.members.contains(p.getUUID())) return r;
		return null;
	}

	static boolean begin(ServerPlayer p, Def def) {
		if (isArena(p.level().dimension()) || runOf(p) != null || Arena.runOf(p) != null) return false;
		ServerLevel l = p.server.getLevel(def.dim());
		if (l == null) {
			p.sendSystemMessage(Component.literal("Veyra frowns at the sigil. \"That way's shut in this world.\"").withStyle(ChatFormatting.GRAY));
			return false;
		}
		int slot = -1;
		for (int i = 0; i < SLOTS && slot < 0; i++) {
			final int s = i;
			if (RUNS.stream().noneMatch(r -> r.def == def && r.slot == s)) slot = i;
		}
		if (slot < 0) {
			p.sendSystemMessage(Component.literal("Veyra: \"Every way there is taken. Give it a little while.\"").withStyle(ChatFormatting.GRAY));
			return false;
		}
		List<ServerPlayer> party = new ArrayList<>();
		party.add(p);
		for (ServerPlayer o : Party.others(p))
			if (o.level() == p.level() && o.distanceTo(p) < 48 && o.isAlive() && !Downed.is(o) && runOf(o) == null && Arena.runOf(o) == null) party.add(o);
		Run run = new Run(def, slot);
		for (ServerPlayer m : party) {
			run.members.add(m.getUUID());
			Arena.remember(m);
			m.sendSystemMessage(Component.literal("Veyra takes the sigil's weight in her palm, and the guild hall burns away...").withStyle(ChatFormatting.AQUA, ChatFormatting.ITALIC));
			m.serverLevel().sendParticles(ParticleTypes.FLAME, m.getX(), m.getY() + 1, m.getZ(), 60, 0.5, 1, 0.5, 0.05);
		}
		RUNS.add(run);
		keep(l, run, true);
		Integer built = data(p.server).built.get(def.id() + ":" + slot);
		if (built != null && built == VERSION) arrive(l, run);
		else if (job == null) job = new Job(run);
		return true;
	}

	private static void arrive(ServerLevel l, Run run) {
		shape(run.def);                                  // (fills the arena's smoke spots)
		int i = 0;
		List<ServerPlayer> in = online(l.getServer(), run);
		for (ServerPlayer m : in) {
			double a = i++ * Math.PI * 2 / Math.max(1, in.size());
			Vec3 at = run.at(new Vec3(Math.cos(a) * 2.5 + 0.5, 0, Math.sin(a) * 2.5 + 0.5));
			Vec3 boss = run.at(run.def.bossAt());
			float yaw = (float) Math.toDegrees(Math.atan2(-(boss.x - at.x), boss.z - at.z));
			m.teleportTo(l, at.x, at.y, at.z, yaw, 0f);
			title(m, run.def.title(), run.def.sub());
			m.playNotifySound(SoundEvents.BEACON_ACTIVATE, SoundSource.PLAYERS, 1f, 0.5f);
		}
		run.phase = COMING;
		run.until = l.getGameTime() + COME;
	}

	static List<ServerPlayer> online(MinecraftServer server, Run run) {
		List<ServerPlayer> out = new ArrayList<>();
		for (UUID u : run.members) {
			ServerPlayer p = server.getPlayerList().getPlayer(u);
			if (p != null) out.add(p);
		}
		return out;
	}

	// ---------------------------------------------------------------- the fight

	private static void tick(ServerTickEvent.Post e) {
		MinecraftServer server = e.getServer();
		build(server);
		for (Run run : new ArrayList<>(RUNS)) {
			if (run.phase == BUILDING) continue;
			ServerLevel l = server.getLevel(run.def.dim());
			if (l == null) continue;
			run.members.removeIf(u -> {
				ServerPlayer p = server.getPlayerList().getPlayer(u);
				return p == null || p.level() != l;
			});
			if (run.members.isEmpty()) {
				end(l, run, null);
				continue;
			}
			long now = l.getGameTime();
			for (ServerPlayer p : online(server, run)) {
				Vec3 rel = p.position().subtract(Vec3.atLowerCornerOf(run.origin()));
				if (rel.y < -30) {                           // over the edge: back onto the hearth
					Vec3 c = run.at(new Vec3(0.5, 0, 0.5));
					p.teleportTo(l, c.x, c.y, c.z, p.getYRot(), 0f);
					p.fallDistance = 0;
				} else if (!run.fallen.contains(p.getUUID())) run.def.hazard().at(p, rel);
			}
			if (now % 8 == 0) smoke(l, run);
			if (run.def.id().equals("wreck") && now % 90 == 0) storm(l, run);
			switch (run.phase) {
				case COMING -> {
					if (now >= run.until) summon(l, run);
				}
				case FIGHT -> fight(l, run);
				case WON -> door(l, run, now);
				default -> {}
			}
		}
	}

	/** The storm over the Graveyard: lightning out over the sea, for show (it hurts nobody, burns nothing). */
	private static void storm(ServerLevel l, Run run) {
		RandomSource r = l.getRandom();
		if (r.nextFloat() > 0.45f) return;
		double a = r.nextDouble() * Math.PI * 2, d = 80 + r.nextDouble() * 30;
		Vec3 at = run.at(new Vec3(Math.cos(a) * d, WreckShape.SEA + 1, Math.sin(a) * d));
		var bolt = net.minecraft.world.entity.EntityType.LIGHTNING_BOLT.create(l);
		if (bolt == null) return;
		bolt.moveTo(at.x, at.y, at.z);
		bolt.setVisualOnly(true);
		l.addFreshEntity(bolt);
	}

	/** The chimneys' smoke, seen from across the void. */
	private static void smoke(ServerLevel l, Run run) {
		RandomSource r = l.getRandom();
		for (Vec3 s : run.def.smoke()) {
			Vec3 at = run.at(s);
			for (ServerPlayer p : l.players())
				if (run.members.contains(p.getUUID())) {
					l.sendParticles(p, ParticleTypes.CAMPFIRE_SIGNAL_SMOKE, true, at.x + r.nextGaussian(), at.y + 1, at.z + r.nextGaussian(), 2, 1.2, 0.5, 1.2, 0.02);
					if (r.nextFloat() < 0.3f) l.sendParticles(p, ParticleTypes.LAVA, true, at.x, at.y + 0.5, at.z, 1, 1, 0.2, 1, 0);
				}
		}
	}

	private static void summon(ServerLevel l, Run run) {
		var type = BuiltInRegistries.ENTITY_TYPE.getOptional(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, run.def.boss())).orElse(null);
		if (type == null || !(type.create(l) instanceof Mob m)) {
			end(l, run, "The way closes before anything comes. (No boss here.)");
			return;
		}
		Vec3 at = run.at(run.def.bossAt());
		m.moveTo(at.x, at.y, at.z, run.def.bossYaw(), 0);
		EventHooks.finalizeMobSpawn(m, l, l.getCurrentDifficultyAt(BlockPos.containing(at)), MobSpawnType.EVENT, null);
		m.setPersistenceRequired();
		m.addTag(TAG);
		// more of you, more of it: Balance.party scales it like a gate's boss (pass 13; the extra half a player it had on top was a double count)
		l.addFreshEntity(m);
		run.boss = m.getUUID();
		ServerPlayer near = null;
		for (ServerPlayer p : online(l.getServer(), run)) if (near == null || p.distanceToSqr(m) < near.distanceToSqr(m)) near = p;
		Slumber.wake(l, m, near);
		l.sendParticles(ParticleTypes.EXPLOSION_EMITTER, at.x, at.y + 1, at.z, 1, 0, 0, 0, 0);
		l.sendParticles(ParticleTypes.LAVA, at.x, at.y + 1, at.z, 60, 3, 1, 3, 0);
		run.phase = FIGHT;
	}

	private static void fight(ServerLevel l, Run run) {
		Entity b = run.boss == null ? null : l.getEntity(run.boss);
		if (b instanceof Mob m && m.isAlive()) {
			if (m.getY() < run.origin().getY() - 25) {              // off the edge: back up where it came from
				Vec3 at = run.at(run.def.bossAt());
				m.teleportTo(at.x, at.y, at.z);
			}
		}
		boolean anyUp = false;
		for (ServerPlayer p : online(l.getServer(), run)) if (!run.fallen.contains(p.getUUID()) && !Downed.is(p)) anyUp = true;
		if (!anyUp) end(l, run, "It's too much for you, this time. Veyra pulls what's left of you home.");
	}

	/** The boss dead (LivingDeathEvent): everyone who's there has beaten it. */
	private static void won(ServerLevel l, Run run) {
		run.phase = WON;
		run.until = l.getGameTime() + LINGER;
		RandomSource r = l.getRandom();
		Gear.Dungeon d = null;
		for (char c : "FEDCBAS".toCharArray())
			for (Gear.Dungeon g : Adventurers.dungeons(c)) if (g.gate().equals(run.def.gate())) d = g;
		for (ServerPlayer p : online(l.getServer(), run)) {
			if (run.fallen.contains(p.getUUID())) unfall(l, run, p);
			if (Downed.is(p)) Downed.revive(p, null);
			p.setHealth(p.getMaxHealth());
			run.def.won().accept(p);
			title(p, "VICTORY", "Gather your spoils, then walk through Veyra's door.");
			if (d == null) continue;
			List<ItemStack> spoils = new ArrayList<>();
			for (int i = 0; i < 2; i++) spoils.add(new ItemStack(Ranks.find(p, r)));
			for (String mat : d.mats()) {
				Item it = Gear.item(mat);
				if (it != null) spoils.add(new ItemStack(it, 2 + r.nextInt(4)));
			}
			List<Gear.Weapon> arms = d.bossWeapons();
			if (!arms.isEmpty() && r.nextFloat() < 0.25f) {
				Item it = Gear.item(arms.get(r.nextInt(arms.size())).id());
				if (it != null) spoils.add(new ItemStack(it));
			}
			spoils.addAll(Chains.extra(p, "boss:" + run.def.id()));
			List<ItemEntity> fell = new ArrayList<>();
			String got = Dropped.rain(l, p, spoils, r, fell);
			List<UUID> mine = run.spoils.computeIfAbsent(p.getUUID(), k -> new ArrayList<>());
			for (ItemEntity ie : fell) mine.add(ie.getUUID());
			int[] pay = Errands.pay("FEDCBAS".indexOf(d.rank()));
			int coins = pay[0] * 3;
			Coins.give(p, coins);
			p.sendSystemMessage(Component.literal("  +" + coins + " coins" + got).withStyle(ChatFormatting.YELLOW));
			p.playNotifySound(SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.PLAYERS, 1f, 1f);
		}
		Vec3 at = run.at(DOOR);
		l.playSound(null, at.x, at.y, at.z, SoundEvents.END_PORTAL_SPAWN, SoundSource.PLAYERS, 1.2f, 1.3f);
		l.sendParticles(ParticleTypes.END_ROD, at.x, at.y + 2, at.z, 80, 0.6, 1.4, 0.6, 0.15);
		GateEntity g = Gates.GATE.get().create(l);                // a gate's tear, facing the arena's heart, the way home
		if (g != null) {
			g.moveTo(at.x, at.y, at.z, 0, 0);
			g.setRank(2);
			g.makeWayOut();
			g.opened(l.getGameTime());
			l.addFreshEntity(g);
			run.gate = g.getUUID();
		}
	}

	// ---------------------------------------------------------------- Veyra's door home

	private static final DustParticleOptions RIM = new DustParticleOptions(new Vector3f(0.35f, 0.95f, 1f), 1.4f);

	/** The door stands open till everyone's walked through it (or a long while has gone by); whoever steps in goes home with
	 *  whatever of their spoils still lies about the arena. */
	private static void door(ServerLevel l, Run run, long now) {
		Vec3 at = run.at(DOOR);
		RandomSource r = l.getRandom();
		// the door itself is a gate's tear (GateEntity, a way out): walking into it is through()
		if (now % 2 == 0 && r.nextFloat() < 0.3f) l.sendParticles(ParticleTypes.END_ROD, at.x, at.y + 0.2, at.z, 1, 1.6, 0, 0.3, 0.01);
		for (ServerPlayer p : online(l.getServer(), run)) {
			Vec3 d = p.position().subtract(at);
			if (run.gate == null && Math.abs(d.x) < 1.3 && Math.abs(d.z) < 0.9 && d.y > -1 && d.y < 3.5) {
				leave(l, run, p, "You step through Veyra's door, and you're home.");
				continue;
			}
			if (now % 40 == 0) {
				int left = lying(l, run, p);
				p.displayClientMessage(Component.literal(left > 0 ? left + " of your spoils still lie here. Veyra's door stands open when you're done."
						: "Veyra's door stands open. Walk through to go home.").withStyle(ChatFormatting.AQUA), true);
			}
		}
		if (run.members.isEmpty()) return;
		if (!run.warned && now >= run.until - LAST_CALL) {
			run.warned = true;
			for (ServerPlayer p : online(l.getServer(), run))
				p.sendSystemMessage(Component.literal("Veyra: \"I can't hold the door much longer, ringwalkers. A minute.\"").withStyle(ChatFormatting.AQUA));
		}
		if (now >= run.until) end(l, run, "Veyra's door closes round you, and you're home.");
	}

	/** How many of p's spoils are still on the ground. */
	static int lying(ServerLevel l, Run run, ServerPlayer p) {
		int n = 0;
		for (UUID u : run.spoils.getOrDefault(p.getUUID(), List.of()))
			if (l.getEntity(u) instanceof ItemEntity ie && ie.isAlive()) n++;
		return n;
	}

	/** p's spoils still lying about, picked up off the arena floor (to go into their pack once they're home). */
	private static List<ItemStack> sweep(ServerLevel l, Run run, ServerPlayer p) {
		List<ItemStack> out = new ArrayList<>();
		List<UUID> mine = run.spoils.remove(p.getUUID());
		if (mine == null) return out;
		for (UUID u : mine)
			if (l.getEntity(u) instanceof ItemEntity ie && ie.isAlive()) {
				out.add(ie.getItem().copy());
				ie.discard();
			}
		return out;
	}

	/** Home, with their spoils: in the pack, or at their feet (marked) if it's full. */
	private static void home(ServerLevel l, Run run, ServerPlayer p) {
		List<ItemStack> left = sweep(l, run, p);
		p.setHealth(Math.max(p.getHealth(), p.getMaxHealth() * 0.5f));
		p.clearFire();
		Arena.home(p);
		if (left.isEmpty()) return;
		int dropped = 0;
		for (ItemStack s : left)
			if (!p.getInventory().add(s) && !s.isEmpty()) {
				ItemEntity ie = new ItemEntity(p.serverLevel(), p.getX(), p.getY() + 0.5, p.getZ(), s);
				ie.setTarget(p.getUUID());
				Dropped.markFor(ie, p);
				p.serverLevel().addFreshEntity(ie);
				dropped++;
			}
		p.sendSystemMessage(Component.literal("Veyra brought along the " + left.size() + " spoils you left lying" + (dropped > 0 ? " (" + dropped
				+ " at your feet: your pack's full)." : ".")).withStyle(ChatFormatting.AQUA));
	}

	/** One of them goes home; the run ends once nobody's left in it. */
	private static void leave(ServerLevel l, Run run, ServerPlayer p, String why) {
		run.members.remove(p.getUUID());
		run.fallen.remove(p.getUUID());
		p.sendSystemMessage(Component.literal(why).withStyle(ChatFormatting.AQUA));
		p.playNotifySound(SoundEvents.PORTAL_TRAVEL, SoundSource.PLAYERS, 0.25f, 1.6f);
		home(l, run, p);
	}

	/** Someone walked into a way-out gate: if it's an arena's door, they go home through it. */
	static boolean through(GateEntity g, ServerPlayer p) {
		if (!(p.level() instanceof ServerLevel l)) return false;
		for (Run run : RUNS)
			if (g.getUUID().equals(run.gate)) {
				if (run.members.contains(p.getUUID())) leave(l, run, p, "You step through Veyra's door, and you're home.");
				return true;
			}
		return false;
	}

	static void end(ServerLevel l, Run run, @Nullable String why) {
		RUNS.remove(run);
		if (run.gate != null) {
			Entity g = l.getEntity(run.gate);
			if (g != null) g.discard();
		}
		if (job != null && job.run == run) job = null;
		keep(l, run, false);
		if (run.boss != null) {
			Entity b = l.getEntity(run.boss);
			if (b != null) b.discard();
		}
		for (UUID u : new HashSet<>(run.members)) {
			ServerPlayer p = l.getServer().getPlayerList().getPlayer(u);
			if (p == null) continue;
			if (why != null) p.sendSystemMessage(Component.literal(why).withStyle(ChatFormatting.AQUA));
			if (p.level() == l) home(l, run, p);
		}
	}

	// ---------------------------------------------------------------- falling in there

	private static void died(LivingDeathEvent e) {
		LivingEntity d = e.getEntity();
		if (!(d.level() instanceof ServerLevel l) || defOf(l.dimension()) == null) return;
		if (d instanceof ServerPlayer p) {
			Run run = runOf(p);
			if (run == null) return;
			e.setCanceled(true);
			fall(l, run, p);
			return;
		}
		for (Run run : RUNS)
			if (run.phase == FIGHT && d.getUUID().equals(run.boss)) won(l, run);
	}

	/** The last blow each player in an arena took: who, how much, what they had (for "you died": a one-hit kill shouldn't look like a bug). */
	private static final Map<UUID, String[]> LAST_HIT = new HashMap<>();

	private static void hit(net.neoforged.neoforge.event.entity.living.LivingDamageEvent.Pre e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || defOf(p.level().dimension()) == null) return;
		Entity by = e.getSource().getEntity();
		String who = by != null ? by.getDisplayName().getString() : e.getSource().getMsgId();
		LAST_HIT.put(p.getUUID(), new String[] {who, String.valueOf(Math.round(e.getNewDamage())), String.valueOf(Math.round(p.getHealth() + p.getAbsorptionAmount()))});
	}

	private static void fall(ServerLevel l, Run run, ServerPlayer p) {
		Downed.DOWN.remove(p.getUUID());
		p.setForcedPose(null);
		p.setHealth(p.getMaxHealth());
		p.removeAllEffects();
		p.clearFire();
		p.setGameMode(GameType.SPECTATOR);
		run.fallen.add(p.getUUID());
		Vec3 s = run.at(new Vec3(0.5, 24, -40.5));
		p.teleportTo(l, s.x, s.y, s.z, 0f, 25f);
		String[] hit = LAST_HIT.remove(p.getUUID());
		title(p, "YOU DIED", hit == null ? "Watch. If they win, you've won it with them." : hit[0] + " hit you for " + hit[1]);
		p.sendSystemMessage(Component.literal("You died" + (hit == null ? "" : ": " + hit[0] + " hit you for " + hit[1] + ", you had " + hit[2])
				+ ". You watch from above; if your party wins, you've won it with them.").withStyle(ChatFormatting.RED));
	}

	private static void unfall(ServerLevel l, Run run, ServerPlayer p) {
		CompoundTag t = p.getPersistentData().getCompound(Arena.BACK);
		GameType mode = GameType.byId(t.contains("mode") ? t.getInt("mode") : GameType.SURVIVAL.getId());
		if (mode == GameType.SPECTATOR) mode = GameType.SURVIVAL;
		p.setGameMode(mode);
		Vec3 c = run.at(new Vec3(0.5, 0, 0.5));
		p.teleportTo(l, c.x, c.y, c.z, p.getYRot(), 0f);
		run.fallen.remove(p.getUUID());
	}

	private static void login(PlayerEvent.PlayerLoggedInEvent e) {
		if (e.getEntity() instanceof ServerPlayer p && defOf(p.level().dimension()) != null && runOf(p) == null) Arena.home(p);
	}

	private static void logout(PlayerEvent.PlayerLoggedOutEvent e) {
		if (!(e.getEntity() instanceof ServerPlayer p)) return;
		Run run = runOf(p);
		if (run == null) return;
		run.members.remove(p.getUUID());
		run.fallen.remove(p.getUUID());
		if (p.level() instanceof ServerLevel l) home(l, run, p);
		else Arena.home(p);
	}

	// ---------------------------------------------------------------- nothing in an arena breaks (the Ashen Ring too)

	private static void noBreak(BlockEvent.BreakEvent e) {
		if (e.getLevel() instanceof Level l && isArena(l.dimension()) && !e.getPlayer().isCreative()) e.setCanceled(true);
	}

	private static void noPlace(BlockEvent.EntityPlaceEvent e) {
		if (e.getLevel() instanceof Level l && isArena(l.dimension()) && !(e.getEntity() instanceof net.minecraft.world.entity.player.Player pl && pl.isCreative()))
			e.setCanceled(true);
	}

	private static void noBlast(ExplosionEvent.Detonate e) {
		if (isArena(e.getLevel().dimension())) e.getAffectedBlocks().clear();
	}

	private static void title(ServerPlayer p, String big, String small) {
		p.connection.send(new ClientboundSetTitlesAnimationPacket(10, 60, 20));
		p.connection.send(new ClientboundSetTitleTextPacket(Component.literal(big).withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD)));
		p.connection.send(new ClientboundSetSubtitleTextPacket(Component.literal(small).withStyle(ChatFormatting.GRAY)));
	}

	private static void commands(RegisterCommandsEvent e) {
		e.getDispatcher().register(Commands.literal("ashbound").then(Commands.literal("bossarena").requires(s -> s.hasPermission(2))
				.then(Commands.literal("enter").executes(c -> {
					act(c.getSource().getPlayerOrException(), "enter");
					return 1;
				}))
				.then(Commands.literal("win").executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					Run run = runOf(p);
					if (run == null || run.phase != FIGHT || run.boss == null) return 0;
					Entity b = p.serverLevel().getEntity(run.boss);
					if (b instanceof LivingEntity le) le.kill();
					return 1;
				}))));
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener(BossArenas::tick);
		NeoForge.EVENT_BUS.addListener(EventPriority.LOWEST, BossArenas::died);
		NeoForge.EVENT_BUS.addListener(BossArenas::login);
		NeoForge.EVENT_BUS.addListener(BossArenas::logout);
		NeoForge.EVENT_BUS.addListener(BossArenas::noBreak);
		NeoForge.EVENT_BUS.addListener(BossArenas::noPlace);
		NeoForge.EVENT_BUS.addListener(BossArenas::noBlast);
		NeoForge.EVENT_BUS.addListener(BossArenas::commands);
		NeoForge.EVENT_BUS.addListener(EventPriority.LOWEST, BossArenas::hit);
	}
}
