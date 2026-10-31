package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ShieldItem;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.minecraft.world.item.component.ItemLore;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.registries.DeferredItem;
import yesman.epicfight.api.animation.AnimationManager;
import yesman.epicfight.api.animation.types.StaticAnimation;
import yesman.epicfight.gameasset.Armatures;

/**
 * The forge gives you the piece there and then. It's always yours; how fine it comes out is luck ({@link Quality}), and every
 * Temper Ember you burn on it pushes the luck your way. The same goes for upgrades, +1 to +10: harder each +, and one that
 * doesn't take spends the materials, never the piece.
 *
 * Only the Joining, at the Cold Forge, is still done by hand: you feed the fire, answer the master's rhythm and finish it
 * (client/ForgeStrikeScreen plays it, client/ForgeScene stages it), and a friend can take the master's side of the anvil.
 * Each gate's metal behaves in its own way ({@link Metal}), each kind of gear has its own rhythm ({@link #pattern}). The server
 * only holds the session: nothing is taken until the work is done, and walking off costs nothing.
 */
public final class Smithing {
	private Smithing() {}

	public static AnimationManager.AnimationAccessor<StaticAnimation> READY, STRIKE, TAP, LOW;

	/** Clips by tools/forge_clips.py: the blow starts on its first frame, so it's never blended in late. */
	static void build(AnimationManager.AnimationBuilder b) {
		READY = b.nextAccessor("biped/forge_ready", a -> new StaticAnimation(true, a, Armatures.BIPED));
		STRIKE = b.nextAccessor("biped/forge_strike", a -> new StaticAnimation(0f, false, a, Armatures.BIPED));
		TAP = b.nextAccessor("biped/forge_tap", a -> new StaticAnimation(0f, false, a, Armatures.BIPED));
		LOW = b.nextAccessor("biped/forge_low", a -> new StaticAnimation(true, a, Armatures.BIPED));
	}

	public enum Quality {
		CRUDE("Crude", -0.05, ChatFormatting.GRAY), FINE("Fine", 0, ChatFormatting.WHITE),
		MASTERWORK("Masterwork", 0.05, ChatFormatting.AQUA), PERFECT("Perfect", 0.10, ChatFormatting.GOLD);

		public final String title;
		public final double bonus;
		public final ChatFormatting colour;

		Quality(String title, double bonus, ChatFormatting colour) {
			this.title = title;
			this.bonus = bonus;
			this.colour = colour;
		}

		public static Quality of(float score) {
			return score >= 0.92f ? PERFECT : score >= 0.75f ? MASTERWORK : score >= 0.4f ? FINE : CRUDE;
		}
	}

	/** What the three steps are for a kind of work, and what's in your hand. */
	public enum Craft {
		METAL("smith_hammer", false, "FEED THE FIRE", "Hold to pump the bellows", "QUENCH", "Click as it cools through the mark"),
		RIVET("smith_hammer", false, "HEAT THE RIVETS", "Hold to pump the bellows", "SET THE LAST RIVET", "Click as it cools through the mark"),
		STITCH("tailor_needle", true, "WAX THE THREAD", "Hold to draw the thread through the wax", "TIE IT OFF", "Click as the wax sets through the mark"),
		WEAVE("tailor_needle", true, "DYE THE CLOTH", "Hold it in the dye", "WARD RUNE", "Click as the rune burns through the mark");

		public final String tool, fire, fireHint, last, lastHint;
		public final boolean cloth;

		Craft(String tool, boolean cloth, String fire, String fireHint, String last, String lastHint) {
			this.tool = tool;
			this.cloth = cloth;
			this.fire = fire;
			this.fireHint = fireHint;
			this.last = last;
			this.lastHint = lastHint;
		}

		public static Craft of(String kind) {
			return switch (kind) {
				case "heavy", "medium" -> RIVET;
				case "light" -> STITCH;
				case "robe" -> WEAVE;
				default -> METAL;
			};
		}
	}

	/** How a gate's metal works: how fast the bellows heat it, how fast it cools, the tempo, and whether it fights back
	 * (on the last round your answer isn't what the master played: read the marks, not your ears). */
	public record Metal(String word, float rise, float fall, float tempo, boolean twist) {}

	private static final Metal PLAIN = new Metal("Honest metal. Keep time.", 0.55f, 0.42f, 1f, false),
			COLD = new Metal("Cold metal. It loses its heat fast, so be quick.", 0.5f, 0.75f, 1.15f, false),
			HOT = new Metal("Hot metal. It runs away from you at the bellows.", 0.95f, 0.42f, 1f, false),
			WILD = new Metal("Wild metal. It'll fight you at the end.", 0.55f, 0.42f, 1f, true),
			HEAVY = new Metal("Heavy metal. Slow blows, and every one counts.", 0.45f, 0.35f, 0.85f, false);

	public static Metal metal(Gear.Dungeon d) {
		return switch (d.element()) {
			case "Rime", "Brine", "Undertow", "Abyss" -> COLD;
			case "Brand", "Ember", "Wyrmfire", "Sunfire", "Sunburn", "Fury", "Steam", "Thunder" -> HOT;
			case "Fever", "Hex", "Jest", "Bloom", "Venom", "Carrion", "Blood", "Eclipse" -> WILD;
			case "Toll", "Marrow", "Jade", "Crystallize", "Vein" -> HEAVY;
			default -> PLAIN;
		};
	}

	/** The rhythm of a kind of weapon, in beats of a four-beat bar: a dagger is many quick taps, a greatsword two huge blows. */
	public static float[][] pattern(String kind) {
		return switch (kind) {
			case "heavy" -> new float[][] {{0, 2, 3}, {0, 1.5f, 3}};
			case "medium" -> new float[][] {{0, 1, 2, 3}, {0, 1, 1.5f, 3}};
			case "light" -> new float[][] {{0, 0.5f, 1, 2, 3}, {0, 1, 2, 2.5f, 3}};
			case "robe" -> new float[][] {{0, 0.5f, 1.5f, 2, 3}, {0, 1, 1.5f, 2.5f, 3}};
			case "dagger" -> new float[][] {{0, 0.5f, 1, 2, 2.5f, 3}, {0, 1, 1.5f, 2, 3, 3.5f}};
			case "sword" -> new float[][] {{0, 1, 2, 2.5f}, {0, 0.5f, 2, 3}};
			case "spear" -> new float[][] {{0, 1.5f, 2, 3}, {0, 1, 1.5f, 3}};
			case "hammer" -> new float[][] {{0, 2, 3}, {0, 1, 3}};
			case "twohander" -> new float[][] {{0, 2}, {0, 3}};
			case "shield" -> new float[][] {{0, 1, 2, 3}, {0, 1, 2.5f}};
			case "bow" -> new float[][] {{0, 0.5f, 1.5f, 3}, {0, 1, 2, 2.5f}};
			default -> new float[][] {{0, 1.5f, 3}, {0, 1, 2.5f}}; // the staffs
		};
	}

	/** What the master says when the weapon's done, by quality. */
	private static final String[][] LINES = {
			{"It'll cut. Eventually.", "I've seen worse. Not often.", "Melt it down in your head and try again."},
			{"That'll do.", "Honest work.", "It'll hold an edge."},
			{"Now that's a blade.", "Your arm's learning.", "Not bad at all."},
			{"...I couldn't have done it better.", "Thirty years at this anvil, and that's as good as any of them.", "Put your name on it. You've earned it."}};

	public static String line(Quality q, int seed) {
		String[] l = LINES[q.ordinal()];
		return l[Math.floorMod(seed, l.length)];
	}

	// ---------------------------------------------------------------- what's what

	public static final int MAKE = 0, UPGRADE = 1, FUSE = 2;
	/** What the two at the anvil tell each other and anyone watching (Net.ForgeRelay, Net.ForgeEcho). */
	public static final int SWING = 0, MASTER = 1, BELLOWS = 2, STAGE = 3, BEGIN = 5, END = 6, LEAVE = 7, JOINED = 8, RESULT = 9;
	public static final int TOP = 10;
	private static final Gear.Cost FUSE_COST = new Gear.Cost(10, 5, 3);
	private static final String RANKS = "FEDCBAS";

	/** The drop that betters the forge's luck: dropped by elites and bosses, burned at the forge. */
	public static final DeferredItem<Item> TEMPER = Weapons.ITEMS.registerItem("temper_ember", p -> new Item(p.rarity(net.minecraft.world.item.Rarity.RARE)));
	public static final int MOST_EMBERS = 8;
	/** What each ember adds to the roll, and where the roll (0 to 1, plus the embers) stops being each quality. */
	private static final float EMBER = 0.06f;
	private static final float[] ROLL_TOPS = {0.25f, 0.8f, 0.97f, Float.MAX_VALUE};

	private static Quality rolled(float roll) {
		int i = 0;
		while (roll >= ROLL_TOPS[i]) i++;
		return Quality.values()[i];
	}

	/** The chance of each quality with this many embers on it. */
	public static float[] odds(int embers) {
		float from = embers * EMBER, was = 0;
		float[] out = new float[ROLL_TOPS.length];
		for (int i = 0; i < out.length; i++) {
			float upTo = Math.max(0, Math.min(1, ROLL_TOPS[i] - from));
			out[i] = upTo - was;
			was = upTo;
		}
		return out;
	}

	/** The chance an upgrade takes from this +, with this many embers on it. */
	public static float upgradeChance(int plus, int embers) {
		return Math.max(0, Math.min(1, 1 - need(plus) + embers * EMBER));
	}

	private static final Map<String, Gear.Dungeon> HOME = new HashMap<>();
	private static final Map<String, String> KIND = new HashMap<>();

	private static void index() {
		if (!HOME.isEmpty()) return;
		for (Gear.Dungeon d : Gear.DUNGEONS) {
			for (Gear.Weapon w : d.weapons()) {
				HOME.put(w.id(), d);
				KIND.put(w.id(), w.kind());
			}
			for (Gear.Set st : d.sets())
				for (Gear.Piece pc : st.pieces()) {
					HOME.put(pc.id(), d);
					KIND.put(pc.id(), st.cls());
				}
		}
	}

	private static String id(Item it) {
		return net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(it).getPath();
	}

	/** The gate a piece of gear belongs to, or null for what isn't gate gear. */
	public static Gear.Dungeon home(Item it) {
		index();
		return HOME.get(id(it));
	}

	/** The kind of work a piece of gear is: a weapon's kind, or an armour class. */
	public static String kind(Item it) {
		index();
		return KIND.getOrDefault(id(it), "sword");
	}

	private static CompoundTag tag(ItemStack s) {
		CustomData c = s.get(DataComponents.CUSTOM_DATA);
		return c == null ? new CompoundTag() : c.copyTag();
	}

	public static int plus(ItemStack s) {
		return tag(s).getInt("ash_plus");
	}

	public static Gear.Cost upgradeCost(int plus) {
		return plus < 5 ? new Gear.Cost(6 + 3 * plus, 1 + plus / 2, 0) : new Gear.Cost(10 + 3 * plus, 2 + plus / 2, 1 + (plus - 5) / 2);
	}

	/** What the roll must reach to raise a piece from this +. */
	public static float need(int plus) {
		return 0.45f + plus * 0.045f;
	}

	public static float tempo(Net.Job j, ItemStack work) {
		return j.type() == UPGRADE ? 1 + plus(work) * 0.02f : j.type() == FUSE ? 1.1f : 1f;
	}

	public static boolean fights(Net.Job j, ItemStack work, Metal m) {
		return m.twist() || j.type() == FUSE || (j.type() == UPGRADE && plus(work) >= 7);
	}

	public static Gear.Weapon boss(ItemStack s) {
		Gear.Weapon w = Gear.WEAPON.get(id(s.getItem()));
		return w != null && w.boss() ? w : null;
	}

	public static Gear.Cost fuseCost() {
		return FUSE_COST;
	}

	/** What a job asks for and gives, or null if it can't be done as things stand. */
	private record Order(Gear.Dungeon d, Gear.Cost cost, Item out) {}

	private static Order order(ServerPlayer p, Net.Job j) {
		var items = p.getInventory().items;
		switch (j.type()) {
			case MAKE -> {
				if (j.gate() < 0 || j.gate() >= Gear.DUNGEONS.size()) return null;
				Gear.Dungeon d = Gear.DUNGEONS.get(j.gate());
				if (j.recipe() < 0 || j.recipe() >= d.recipes().size()) return null;
				Gear.Recipe r = d.recipes().get(j.recipe());
				Item out = Gear.item(r.id());
				return out == null ? null : new Order(d, r.cost(), out);
			}
			case UPGRADE -> {
				if (j.slot() < 0 || j.slot() >= items.size()) return null;
				ItemStack s = items.get(j.slot());
				Gear.Dungeon d = s.isEmpty() ? null : home(s.getItem());
				return d == null || plus(s) >= TOP ? null : new Order(d, upgradeCost(plus(s)), s.getItem());
			}
			case FUSE -> {
				// the Joining: slot and gate are the two pieces, what it takes is the second's gate's
				if (j.slot() < 0 || j.slot() >= items.size() || j.gate() < 0 || j.gate() >= items.size() || j.slot() == j.gate()) return null;
				ItemStack a = items.get(j.slot()), b = items.get(j.gate());
				if (Joined.after(a, b) <= 0) return null;
				return new Order(home(b.getItem()), FUSE_COST, Gear.item(Joined.of(boss(a).kind()).id()));
			}
			default -> {
				return null;
			}
		}
	}

	/** The forge's button: the piece, there and then, or for the Joining, to the anvil. */
	static void request(ServerPlayer p, BlockPos at, Net.Job j, int wanted) {
		Order o = order(p, j);
		if (o == null || (j.type() == FUSE) != (ColdForge.altar(p.level(), at) != null) || (j.type() == FUSE && !Coins.flag(p, "cold_proved"))) return;   // the Joining is the Cold Forge's alone
		if (!GateForge.affords(p, o.d, o.cost)) {
			p.displayClientMessage(Component.literal("You're short of what that takes").withStyle(ChatFormatting.RED), true);
			return;
		}
		if (j.type() == FUSE) {
			begin(p, at, j);
			return;
		}
		int embers = Math.max(0, Math.min(Math.min(wanted, MOST_EMBERS), GateForge.count(p, TEMPER.get())));
		float roll = p.getRandom().nextFloat() + embers * EMBER;
		GateForge.pay(p, o.d, o.cost);
		GateForge.take(p, TEMPER.get(), embers);
		p.level().playSound(null, at, SoundEvents.ANVIL_USE, SoundSource.BLOCKS, 0.8f, 0.9f);
		if (p.level() instanceof ServerLevel sl) sl.sendParticles(ParticleTypes.LAVA, at.getX() + 0.5, at.getY() + 1.1, at.getZ() + 0.5, 6 + embers * 2, 0.25, 0.1, 0.25, 0);
		if (j.type() == MAKE) {
			Quality q = rolled(roll);
			Component made = give(p, o.out, q, "", 0, 0);
			p.displayClientMessage(Component.literal(q.title + ": ").withStyle(q.colour).append(made), true);
			return;
		}
		ItemStack it = p.getInventory().items.get(j.slot());
		if (roll < need(plus(it))) {
			p.displayClientMessage(Component.literal("It didn't take. Your materials are spent, the piece is unharmed").withStyle(ChatFormatting.GRAY), true);
			return;
		}
		raise(it);
		if (plus(it) >= 5) Story.mark(p, "story/plus_five");
		p.displayClientMessage(Component.literal("It took: ").withStyle(ChatFormatting.GREEN).append(it.getHoverName()), true);
	}

	private static Npc nearestSmith(Level l, BlockPos at) {
		return l.getEntitiesOfClass(Npc.class, new AABB(at).inflate(9), GateForge::smith).stream()
				.min(java.util.Comparator.comparingDouble(n -> n.distanceToSqr(at.getCenter()))).orElse(null);
	}

	// ---------------------------------------------------------------- at the anvil

	private static final class Session {
		final BlockPos anvil;
		final Net.Job job;
		final Npc smith;
		final boolean ghost;
		final long began;
		final ServerPlayer worker;
		ServerPlayer helper;

		Session(ServerPlayer worker, BlockPos anvil, boolean ghost, Net.Job job, Npc smith, long began) {
			this.worker = worker;
			this.anvil = anvil;
			this.ghost = ghost;
			this.job = job;
			this.smith = smith;
			this.began = began;
		}
	}

	private static final Map<UUID, Session> SESSIONS = new HashMap<>();
	private static final int LONGEST = 45 * 20;

	private static boolean free(Level l, BlockPos p) {
		return l.getBlockState(p).getCollisionShape(l, p).isEmpty() && l.getBlockState(p.above()).getCollisionShape(l, p.above()).isEmpty()
				&& !l.getBlockState(p.below()).getCollisionShape(l, p.below()).isEmpty();
	}

	/** The anvil to work on: the forge, or a plain anvil near the smith. */
	private static BlockPos anvilNear(Level l, BlockPos at) {
		BlockPos best = null;
		double d = Double.MAX_VALUE;
		for (BlockPos p : BlockPos.betweenClosed(at.offset(-6, -2, -6), at.offset(6, 2, 6))) {
			var s = l.getBlockState(p);
			if (!s.is(GateForge.BLOCK.get()) && !s.is(Blocks.ANVIL) && !s.is(Blocks.CHIPPED_ANVIL) && !s.is(Blocks.DAMAGED_ANVIL)) continue;
			double k = p.distSqr(at) - (s.is(GateForge.BLOCK.get()) ? 1000 : 0);
			if (k < d) {
				d = k;
				best = p.immutable();
			}
		}
		return best;
	}

	/** The sides of the anvil someone can stand at, nearest to where they are first. */
	private static List<Direction> sides(ServerPlayer p, BlockPos anvil) {
		List<Direction> out = new ArrayList<>();
		for (Direction d : Direction.Plane.HORIZONTAL) if (free(p.level(), anvil.relative(d))) out.add(d);
		out.sort(java.util.Comparator.comparingDouble(d -> anvil.relative(d).getCenter().distanceToSqr(p.position())));
		return out;
	}

	private static void begin(ServerPlayer p, BlockPos at, Net.Job job) {
		Level l = p.level();
		BlockPos altar = ColdForge.altar(l, at);
		Npc smith = altar != null ? null : nearestSmith(l, at);   // the Cold Forge keeps its own time
		BlockPos anvil = altar != null ? altar : anvilNear(l, at);
		boolean ghost = anvil == null; // a smith with no anvil about: they set a little one down (ForgeScene draws it)
		if (ghost) anvil = smith != null ? smith.blockPosition().relative(smith.getDirection(), 2) : at;
		List<Direction> sides = sides(p, anvil);
		Direction side = sides.isEmpty() ? Direction.getNearest(p.getX() - anvil.getX(), 0, p.getZ() - anvil.getZ()) : sides.get(0);
		float yaw = side.getOpposite().toYRot();
		if (!sides.isEmpty()) {
			Vec3 stand = anvil.relative(side).getBottomCenter();
			p.connection.teleport(stand.x, stand.y, stand.z, yaw, 10);
		}
		if (smith != null) {
			BlockPos across = sides.contains(side.getOpposite()) ? anvil.relative(side.getOpposite())
					: sides.size() > 1 ? anvil.relative(sides.get(1)) : smith.blockPosition();
			smith.forge(across.getBottomCenter(), anvil, LONGEST);
		}
		SESSIONS.put(p.getUUID(), new Session(p, anvil, ghost, job, smith, l.getGameTime()));
		PacketDistributor.sendToPlayer(p, new Net.ForgeStart(anvil, ghost, job, smith == null ? -1 : smith.getId(), yaw, -1));
		Order o = order(p, job);
		echo(p, BEGIN, o != null && Craft.of(kind(o.out)).cloth ? 1 : 0);
	}

	/** A friend steps up to an anvil someone's working: they take the master's side. True if someone's at it. */
	static boolean join(ServerPlayer p, BlockPos anvil) {
		for (Session s : SESSIONS.values()) {
			if (!s.anvil.equals(anvil) || s.worker == p) continue;
			if (s.helper != null || p.distanceToSqr(anvil.getCenter()) > 64) return true;
			s.helper = p;
			List<Direction> sides = sides(p, anvil);
			Direction wside = Direction.getNearest(s.worker.getX() - anvil.getX(), 0, s.worker.getZ() - anvil.getZ());
			Direction side = wside.getOpposite();
			Vec3 stand = anvil.relative(side).getBottomCenter();
			if (s.smith != null) {
				Direction aside = sides.stream().filter(d -> d != wside && d != side).findFirst().orElse(null);
				if (aside != null) s.smith.forge(anvil.relative(aside).getBottomCenter(), anvil, LONGEST);
			}
			float yaw = side.getOpposite().toYRot();
			p.connection.teleport(stand.x, stand.y, stand.z, yaw, 10);
			PacketDistributor.sendToPlayer(p, new Net.ForgeStart(anvil, s.ghost, shared(s), s.smith == null ? -1 : s.smith.getId(), yaw, s.worker.getId()));
			echo(p, JOINED, 0);
			return true;
		}
		return false;
	}

	/** The job as a friend's client can read it: the piece's in someone else's pack, so its item id for the slot, and its + for the gate. */
	private static Net.Job shared(Session s) {
		if (s.job.type() == MAKE) return s.job;
		var items = s.worker.getInventory().items;
		ItemStack it = items.get(s.job.slot());
		var reg = net.minecraft.core.registries.BuiltInRegistries.ITEM;
		return new Net.Job(s.job.type(), s.job.type() == UPGRADE ? plus(it) : reg.getId(items.get(s.job.gate()).getItem()), s.job.recipe(), reg.getId(it.getItem()));
	}

	/** A piece at some + (what a friend's client shows of it). */
	public static ItemStack shown(Item it, int plus) {
		ItemStack s = new ItemStack(it);
		CompoundTag t = new CompoundTag();
		t.putInt("ash_plus", plus);
		s.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
		return s;
	}

	private static void echo(ServerPlayer from, int action, float value) {
		Net.ForgeEcho m = new Net.ForgeEcho(from.getId(), action, value);
		for (ServerPlayer o : from.serverLevel().players())
			if (o != from && o.distanceToSqr(from) < 2500) PacketDistributor.sendToPlayer(o, m);
	}

	/** What the two at the anvil do, passed to each other and to anyone watching. */
	static void onRelay(Net.ForgeRelay m, ServerPlayer p) {
		Session s = SESSIONS.get(p.getUUID());
		if (s == null)
			for (Session o : SESSIONS.values()) if (o.helper == p) s = o;
		if (s == null) return;
		if (m.action() == LEAVE && s.helper == p) s.helper = null;
		echo(p, m.action(), m.value());
	}

	private static void release(Session s) {
		if (s.smith != null) s.smith.doneForging();
	}

	/** Finished at the anvil, or walked off (score under 0). */
	static void onDone(Net.ForgeDone m, ServerPlayer p) {
		Session s = SESSIONS.remove(p.getUUID());
		if (s == null) return;
		release(s);
		echo(p, END, 0);
		if (m.score() < 0) return;
		Order o = order(p, s.job);
		if (o == null) return;
		if (!GateForge.affords(p, o.d, o.cost)) {
			p.displayClientMessage(Component.literal("You're short of what that takes").withStyle(ChatFormatting.RED), true);
			return;
		}
		// nobody plays the whole thing in five seconds
		float score = p.level().getGameTime() - s.began < 100 ? 0 : Math.max(0, Math.min(1, m.score()));
		Quality q = Quality.of(score);
		var items = p.getInventory().items;
		ItemStack a = items.get(s.job.slot()), b = items.get(s.job.gate());
		int carried = Math.max(plus(a), plus(b)), stage = Joined.after(a, b);
		String name = m.name() == null || m.name().isBlank() ? tag(a).getString("ash_name") : m.name();
		GateForge.pay(p, o.d, o.cost);
		a.shrink(1);
		b.shrink(1);
		give(p, o.out, q, name, carried, stage);
		Story.mark(p, "cold/joined");
	}

	static void raise(ItemStack it) {
		CompoundTag t = tag(it);
		t.putInt("ash_plus", plus(it) + 1);
		it.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
		dress(it);
	}

	private static Component give(ServerPlayer p, Item out, Quality q, String name, int plus, int joined) {
		ItemStack made = make(out, q, name, p);
		if (joined > 0) {
			Joined.setStage(made, joined);
			dress(made);
		}
		for (int i = 0; i < plus; i++) raise(made);
		Component shown = made.getHoverName();
		Story.mark(p, "story/first_forge");
		if (q.ordinal() >= Quality.MASTERWORK.ordinal()) Story.mark(p, "story/masterwork");
		if (!p.getInventory().add(made)) p.drop(made, false);
		if (q == Quality.PERFECT) {
			Component news = p.getDisplayName().copy().append(" forged ").append(shown.copy().withStyle(ChatFormatting.GOLD));
			for (ServerPlayer o : p.server.getPlayerList().getPlayers()) o.sendSystemMessage(news);
		}
		return shown;
	}

	/** The piece, marked with how well it was made and by whom. */
	static ItemStack make(Item out, Quality q, String name, ServerPlayer p) {
		ItemStack s = new ItemStack(out);
		CompoundTag t = new CompoundTag();
		t.putInt("ash_quality", q.ordinal() + 1);
		if (q.ordinal() >= Quality.MASTERWORK.ordinal()) t.putString("ash_smith", p.getGameProfile().getName());
		String clean = net.minecraft.util.StringUtil.filterText(name == null ? "" : name).trim();
		if (q == Quality.PERFECT && !clean.isEmpty()) t.putString("ash_name", clean.substring(0, Math.min(32, clean.length())));
		s.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
		dress(s);
		return s;
	}

	public static Quality quality(ItemStack s) {
		int q = tag(s).getInt("ash_quality");
		return q >= 1 && q <= Quality.values().length ? Quality.values()[q - 1] : null;
	}

	/** Sets a piece's stats, name and lines from its quality and +. */
	private static void dress(ItemStack s) {
		CompoundTag t = tag(s);
		double k = mult(s);
		ItemStack plain = new ItemStack(s.getItem());
		ItemAttributeModifiers base = s.getItem().getDefaultAttributeModifiers(plain);
		if (base.modifiers().isEmpty()) base = plain.getOrDefault(DataComponents.ATTRIBUTE_MODIFIERS, ItemAttributeModifiers.EMPTY);
		if (!base.modifiers().isEmpty()) {
			ItemAttributeModifiers.Builder b = ItemAttributeModifiers.builder();
			for (ItemAttributeModifiers.Entry e : base.modifiers()) {
				AttributeModifier m = e.modifier();
				double a = m.amount();
				if (e.attribute().is(Attributes.ATTACK_DAMAGE)) a = (a + 1) * k - 1;
				else if (e.attribute().is(Attributes.ARMOR) || e.attribute().is(Attributes.ARMOR_TOUGHNESS)) a *= k;
				b.add(e.attribute(), new AttributeModifier(m.id(), a, m.operation()), e.slot());
			}
			s.set(DataComponents.ATTRIBUTE_MODIFIERS, b.build());
		}
		if (s.getItem() instanceof ShieldItem) s.set(DataComponents.MAX_DAMAGE, (int) (plain.getMaxDamage() * k));
		Quality q = quality(s);
		int plus = t.getInt("ash_plus");
		List<Component> lore = new ArrayList<>();
		if (Joined.stage(s) > 0) lore.add(Component.literal("Joined, Rank " + Joined.rank(Joined.stage(s))).withStyle(st -> st.withColor(ChatFormatting.GOLD).withItalic(false)));
		if (q != null) lore.add(Component.literal(q.title).withStyle(st -> st.withColor(q.colour).withItalic(false)));
		if (t.contains("ash_smith")) lore.add(Component.literal("Forged by " + t.getString("ash_smith")).withStyle(st -> st.withColor(ChatFormatting.DARK_GRAY).withItalic(true)));
		if (!lore.isEmpty()) s.set(DataComponents.LORE, new ItemLore(lore));
		String named = t.getString("ash_name");
		if (!named.isEmpty() || plus > 0) {
			Component nm = named.isEmpty() ? plain.getHoverName().copy() : Component.literal(named).withStyle(ChatFormatting.GOLD);
			if (plus > 0) nm = nm.copy().append(" +" + plus);
			s.set(DataComponents.CUSTOM_NAME, nm.copy().withStyle(st -> st.withItalic(false)));
		}
	}

	/** How much a piece's quality and + add to what it does (the stats for armour and blades; read directly for bows and staffs). */
	public static double mult(ItemStack s) {
		Quality q = quality(s);
		return (1 + (q == null ? 0 : q.bonus)) * (1 + tag(s).getInt("ash_plus") * 0.04) * Joined.mult(s);
	}

	/** A session that outlived its player's connection lets the smith go. */
	static void init() {
		net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener((net.neoforged.neoforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent e) -> {
			Session s = SESSIONS.remove(e.getEntity().getUUID());
			if (s != null) {
				release(s);
				if (e.getEntity() instanceof ServerPlayer p) echo(p, END, 0);
			}
			for (Session o : SESSIONS.values()) if (o.helper == e.getEntity()) o.helper = null;
		});
	}
}
