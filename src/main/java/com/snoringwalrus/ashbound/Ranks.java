package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;

import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.storage.loot.LootContext;
import net.minecraft.world.level.storage.loot.functions.LootItemFunction;
import net.minecraft.world.level.storage.loot.functions.LootItemFunctionType;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * Your rank and your party's (docs/BALANCE.md pass 12). You climb to a rank by level and by what you wear: most of your kit has to be of that
 * rank, so nobody walks into rank A with rank D gear. A party's rank is its members' average. It's what sets which gates open, what a chest
 * or a monster leaves you and how far past it a kill still pays.
 */
public final class Ranks {
	private Ranks() {}

	public static final String LADDER = "FEDCBAS";
	private static final int CHECK_EVERY = 100, KIT_MIDDLE = 2, TOP = LADDER.length() - 1;
	private static final EquipmentSlot[] KIT = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET, EquipmentSlot.MAINHAND};

	static final DeferredRegister<LootItemFunctionType<?>> FUNCTIONS = DeferredRegister.create(Registries.LOOT_FUNCTION_TYPE, Ashbound.ID);
	private static final Supplier<LootItemFunctionType<ChestFind>> CHEST_FIND = FUNCTIONS.register("chest_find", () -> new LootItemFunctionType<>(ChestFind.CODEC));

	static void register(IEventBus bus) {
		FUNCTIONS.register(bus);
		NeoForge.EVENT_BUS.addListener(Ranks::check);
	}

	// ---------------------------------------------------------------- what's what

	private static Map<Item, Integer> itemRank;

	/** Every item of ours that has a rank: a dungeon's by its dungeon, a boss weapon's a step above it, a found one by its own. */
	private static Map<Item, Integer> itemRanks() {
		if (itemRank != null) return itemRank;
		Map<Item, Integer> out = new HashMap<>();
		for (Gear.Dungeon d : Gear.DUNGEONS) {
			int r = LADDER.indexOf(d.rank());
			for (Gear.Weapon w : d.weapons()) out.put(Gear.item(w.id()), Math.min(TOP, r + (w.boss() ? 1 : 0)));
			for (Gear.Set s : d.sets()) for (Gear.Piece p : s.pieces()) out.put(Gear.item(p.id()), r);
		}
		for (WorldArms.Arm a : WorldArms.ARMS) out.put(Gear.item(a.id()), LADDER.indexOf(a.weapon().rank()));
		for (WorldArms.Found f : WorldArms.GARB_ITEMS.values()) out.put(f.item().get(), LADDER.indexOf(f.garb().rank()));
		itemRank = out;
		return out;
	}

	/** A piece's rank: 0 for anything that isn't ours. A Joined weapon stands a rank above its stage. */
	static int of(ItemStack s) {
		if (Joined.is(s)) return Math.min(TOP, Joined.stage(s) + 1);
		return itemRanks().getOrDefault(s.getItem(), 0);
	}

	/** Your kit's rank: the middle of your armour and weapon, so three good pieces of five count and a pickaxe in hand doesn't. */
	static int kit(Player p) {
		int[] ranks = new int[KIT.length];
		for (int i = 0; i < KIT.length; i++) ranks[i] = of(p.getItemBySlot(KIT[i]));
		Arrays.sort(ranks);
		return ranks[KIT_MIDDLE];
	}

	/** What level and kit have earned, F until you've found the capital. */
	static int earned(ServerPlayer p) {
		if (!Coins.flag(p, "found_capital")) return 0;
		return Math.min(band(p), kit(p));
	}

	private static int band(ServerPlayer p) {
		return LADDER.indexOf(Balance.rankAt(Levels.level(p)));
	}

	/** Your rank. It doesn't fall when you change your clothes. */
	public static int rank(ServerPlayer p) {
		return p.getData(Levels.RANK);
	}

	/** Your party's: the rounded average of those online, or your own. */
	public static int party(ServerPlayer p) {
		List<ServerPlayer> all = new ArrayList<>(Party.others(p));
		all.add(p);
		return Math.round((float) all.stream().mapToInt(Ranks::rank).sum() / all.size());
	}

	/** Levelled past your kit: the next rank's gates open as often as your own, so there's somewhere to go for it. */
	static boolean outgrown(ServerPlayer p) {
		return band(p) > rank(p);
	}

	private static void check(PlayerTickEvent.Post e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || p.tickCount % CHECK_EVERY != 0) return;
		int was = rank(p), now = earned(p);
		if (now <= was) return;
		p.setData(Levels.RANK, now);
		p.sendSystemMessage(Component.literal("Rank " + LADDER.charAt(now)).withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD)
				.append(Component.literal("  your gates and finds climb with you").withStyle(ChatFormatting.GRAY)));
		p.level().playSound(null, p.blockPosition(), SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.PLAYERS, 0.8f, 1f);
	}

	// ---------------------------------------------------------------- finds

	private record Find(Item item, String type) {}

	private static List<List<Find>> weapons, armour, world;
	private static final double WEAPON_SHARE = 0.45, ARMOUR_SHARE = 0.40, FITS = 0.6;
	private static final double UP_ONE = 0.15, UP_TWO = 0.02, DOWN_ONE = 0.25;
	/** What each class wears and swings, so most of what falls for you is yours to use. */
	private static final Map<String, List<String>> USES = Map.of("vanguard", List.of("sword", "shield", "heavy"), "breaker", List.of("hammer", "heavy"),
			"reaver", List.of("twohander", "medium"), "lancer", List.of("spear", "medium"), "shade", List.of("dagger", "light"), "hunter", List.of("bow", "light"),
			"ashcaster", List.of("black", "robe"), "mender", List.of("white", "robe"), "caller", List.of("summon", "robe"));

	private static List<List<Find>> empty() {
		List<List<Find>> out = new ArrayList<>();
		for (int i = 0; i <= TOP; i++) out.add(new ArrayList<>());
		return out;
	}

	private static void finds() {
		if (weapons != null) return;
		List<List<Find>> w = empty(), a = empty(), f = empty();
		for (Gear.Dungeon d : Gear.DUNGEONS) {
			int r = LADDER.indexOf(d.rank());
			for (Gear.Weapon x : d.weapons()) if (!x.boss()) w.get(r).add(new Find(Gear.item(x.id()), x.kind()));
			for (Gear.Set s : d.sets()) for (Gear.Piece p : s.pieces()) a.get(r).add(new Find(Gear.item(p.id()), s.cls()));
		}
		for (WorldArms.Arm x : WorldArms.ARMS) f.get(LADDER.indexOf(x.weapon().rank())).add(new Find(Gear.item(x.id()), x.kind()));
		for (WorldArms.Found x : WorldArms.GARB_ITEMS.values()) f.get(LADDER.indexOf(x.garb().rank())).add(new Find(x.item().get(), x.garb().cls()));
		weapons = w;
		armour = a;
		world = f;
	}

	/** The rank a find comes up at: mostly the party's, sometimes the one below, now and then a lucky one above. */
	static int findRank(int rank, RandomSource r) {
		double x = r.nextDouble();
		int step = x < UP_TWO ? 2 : x < UP_TWO + UP_ONE ? 1 : x < UP_TWO + UP_ONE + DOWN_ONE ? -1 : 0;
		return Math.max(0, Math.min(TOP, rank + step));
	}

	/** A piece of gear for this player, at their party's rank: a forged weapon, a forged piece of armour or a world piece of that rank, most likely one they can use. */
	static Item find(ServerPlayer p, RandomSource r) {
		finds();
		int at = findRank(party(p), r);
		double x = r.nextDouble();
		List<Find> pool = x < WEAPON_SHARE ? weapons.get(at) : x < WEAPON_SHARE + ARMOUR_SHARE ? armour.get(at) : world.get(at);
		if (pool.isEmpty()) pool = weapons.get(at);
		Classes.Cls c = Classes.of(p);
		if (c != null && r.nextDouble() < FITS) {
			List<String> uses = USES.getOrDefault(c.id(), List.of());
			List<Find> fit = pool.stream().filter(f -> uses.contains(f.type())).toList();
			if (fit.isEmpty()) fit = armour.get(at).stream().filter(f -> uses.contains(f.type())).toList();
			if (!fit.isEmpty()) pool = fit;
		}
		return pool.isEmpty() ? null : pool.get(r.nextInt(pool.size())).item();
	}

	/** How much likelier a chest is to hold gear for a party standing round it: it's one chest between them all. */
	static float chestFor(ServerPlayer p) {
		int near = 1 + (int) Party.others(p).stream().filter(o -> o.level() == p.level() && o.distanceTo(p) < CHEST_REACH).count();
		return 1 + CHEST_PER_PLAYER * (near - 1);
	}

	private static final float CHEST_REACH = 32, CHEST_PER_PLAYER = 0.5f;

	/** A structure chest's gear, rolled when it's first opened, so it's for whoever opened it. */
	record ChestFind(float chance) implements LootItemFunction {
		static final MapCodec<ChestFind> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(Codec.FLOAT.fieldOf("chance").forGetter(ChestFind::chance)).apply(i, ChestFind::new));

		@Override
		public LootItemFunctionType<ChestFind> getType() {
			return CHEST_FIND.get();
		}

		@Override
		public ItemStack apply(ItemStack stack, LootContext ctx) {
			Entity who = ctx.getParamOrNull(LootContextParams.THIS_ENTITY);
			if (!(who instanceof ServerPlayer p) || ctx.getRandom().nextFloat() >= chance * chestFor(p)) return ItemStack.EMPTY;
			Item it = find(p, ctx.getRandom());
			return it == null ? ItemStack.EMPTY : new ItemStack(it);
		}
	}
}
