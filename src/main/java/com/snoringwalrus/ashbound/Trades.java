package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.serialization.Codec;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.core.Holder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.loot.BuiltInLootTables;
import net.minecraft.world.level.storage.loot.LootParams;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.common.Tags;
import net.neoforged.neoforge.common.extensions.IMenuTypeExtension;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.living.BabyEntitySpawnEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.living.LivingDropsEvent;
import net.neoforged.neoforge.event.entity.player.ItemFishedEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.level.BlockDropsEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * Trades: the work you do between fights. Eight of them, each levelled by doing it (1 to 50); every level you gain in any of them gives a
 * trade point, up to {@link #MOST_POINTS}, spent on that trade's perks, so you master a couple and dabble in the rest.
 * <p>
 * Cooking, Brewing and Alchemy are found by trying: sneak and use an empty hand on a stove, a keg, a brewing stand (any mod's: it goes by the
 * block's name), put up to five things in and see what comes out. What works goes in your recipe book; what doesn't is mush. Smithing and
 * Tailoring are the Gate Forge as it was, now with levels and perks; Farming, Fishing and Mining level as you gather. Plan: docs/TRADES.md.
 */
public final class Trades {
	private Trades() {}

	public record Trade(String id, String name, String bench, String blurb, String[] branches) {}

	public static final List<Trade> ALL = List.of(
			new Trade("cooking", "Cooking", "Cook's Fire", "Meals that keep you going: one meal's buff at a time.", new String[] {"Feast", "Flavour", "Thrift"}),
			new Trade("brewing", "Brewing", "Brewer's Cask", "Strong drink for a fight, and every one has a catch.", new String[] {"Strength", "Steadiness", "Tavern"}),
			new Trade("alchemy", "Alchemy", "Alchemist's Bench", "Elixirs, tonics and draughts for the gates.", new String[] {"Elixirs", "Reagents", "Remedies"}),
			new Trade("smithing", "Smithing", "Gate Forge", "Weapons, heavy and medium armour, and upgrades.", new String[] {"Craft", "Upgrades", "Road"}),
			new Trade("tailoring", "Tailoring", "Gate Forge", "Robes and light armour, and their upgrades.", new String[] {"Craft", "Upgrades", "Road"}),
			new Trade("farming", "Farming", "", "Crops, herbs and beasts.", new String[] {"Fields", "Herbs", "Beasts"}),
			new Trade("fishing", "Fishing", "", "Fish, and what else is down there.", new String[] {"Catch", "Treasure", "Fresh"}),
			new Trade("mining", "Mining", "", "Ore, stone and the dark.", new String[] {"Veins", "Stone", "Delve"}));

	public static final int TOP_LEVEL = 50, MOST_POINTS = 60, RESET_COINS = 150;
	/** A perk's tier: what it costs, and the trade level it needs. */
	public static final int[] TIER_COST = {1, 2, 2, 3}, TIER_LEVEL = {5, 15, 30, 45};
	public static final String[] RANKS = {"Novice", "Apprentice", "Journeyman", "Expert", "Master", "Grandmaster"};

	public static Trade trade(String id) {
		for (Trade t : ALL) if (t.id().equals(id)) return t;
		return null;
	}

	/** XP from one level to the next. */
	public static int need(int level) {
		return 40 + 12 * level;
	}

	public static int level(int xp) {
		int l = 1;
		while (l < TOP_LEVEL && xp >= need(l)) {
			xp -= need(l);
			l++;
		}
		return l;
	}

	/** How far into this level, 0 to 1. */
	public static float into(int xp) {
		int l = 1;
		while (l < TOP_LEVEL && xp >= need(l)) {
			xp -= need(l);
			l++;
		}
		return l >= TOP_LEVEL ? 1 : xp / (float) need(l);
	}

	public static String rank(int level) {
		return RANKS[Math.min(RANKS.length - 1, level / 10)];
	}

	// ---------------------------------------------------------------- perks

	public record Perk(String id, String trade, int branch, int tier, String name, String text, Map<String, Double> fx) {
		public int cost() {
			return TIER_COST[tier];
		}

		public int level() {
			return TIER_LEVEL[tier];
		}
	}

	public static final Map<String, Perk> PERKS = new LinkedHashMap<>();

	private static void perk(String trade, int branch, int tier, String id, String name, String text, String fx) {
		Map<String, Double> m = new HashMap<>();
		for (String kv : fx.split(",")) {
			String[] a = kv.split("=");
			m.put(a[0].trim(), Double.parseDouble(a[1]));
		}
		PERKS.put(id, new Perk(id, trade, branch, tier, name, text, m));
	}

	static {
		// cooking
		perk("cooking", 0, 0, "shared_plate", "Shared Plate", "Your meals feed the party near you too, at half strength", "share=0.5");
		perk("cooking", 0, 1, "long_simmer", "Long Simmer", "Meals last 50% longer", "time%=50");
		perk("cooking", 0, 2, "banquet", "Banquet", "The party near you gets your meals at full strength", "share=0.5");
		perk("cooking", 0, 3, "highmourn_table", "Highmourn Table", "Dishes stop tiring you twice as fast", "tire=1");
		perk("cooking", 1, 0, "seasoned", "Seasoned", "Meals 5% stronger", "power%=5");
		perk("cooking", 1, 1, "keen_palate", "Keen Palate", "You can tell when a mix is one thing away from a dish", "hint=1");
		perk("cooking", 1, 2, "chefs_hands", "Chef's Hands", "Better quality", "quality=0.08");
		perk("cooking", 1, 3, "signature_dish", "Signature Dish", "Happy accidents far more often, and better quality", "accident%=4,quality=0.05");
		perk("cooking", 2, 0, "leftovers", "Leftovers", "15% chance each ingredient isn't used up", "save%=15");
		perk("cooking", 2, 1, "quick_study_c", "Quick Study", "25% more Cooking XP", "xp%=25");
		perk("cooking", 2, 2, "double_batch", "Double Batch", "15% chance of making two", "double%=15");
		perk("cooking", 2, 3, "full_larder", "Full Larder", "15% more of each: ingredients kept and doubles", "save%=15,double%=15");
		// brewing
		perk("brewing", 0, 0, "stout_heart", "Stout Heart", "Brews 5% stronger", "power%=5");
		perk("brewing", 0, 1, "barrel_aged", "Barrel Aged", "Better quality", "quality=0.08");
		perk("brewing", 0, 2, "strong_stuff", "Strong Stuff", "Brews last 50% longer", "time%=50");
		perk("brewing", 0, 3, "legendary_cask", "Legendary Cask", "Happy accidents far more often, brews 5% stronger", "accident%=4,power%=5");
		perk("brewing", 1, 0, "clear_head", "Clear Head", "A brew's catch is halved", "catch%=-50");
		perk("brewing", 1, 1, "iron_gut", "Iron Gut", "A brew's catch is a quarter smaller again", "catch%=-25");
		perk("brewing", 1, 2, "toast", "Toast", "The party near you gets half of a brew you drink", "share=0.5");
		perk("brewing", 1, 3, "hard_head", "Hard Head", "You only get tipsy from the third brew in ten minutes", "tipsy=1");
		perk("brewing", 2, 0, "cellar_keeper", "Cellar Keeper", "15% chance each ingredient isn't used up", "save%=15");
		perk("brewing", 2, 1, "regular", "Regular", "25% more Brewing XP", "xp%=25");
		perk("brewing", 2, 2, "cask_master", "Cask Master", "20% chance of making two", "double%=20");
		perk("brewing", 2, 3, "house_brew", "House Brew", "15% more doubles, and better quality", "double%=15,quality=0.05");
		// alchemy
		perk("alchemy", 0, 0, "potent", "Potent", "Elixirs 5% stronger", "power%=5");
		perk("alchemy", 0, 1, "lasting", "Lasting", "Elixirs last 50% longer", "time%=50");
		perk("alchemy", 0, 2, "hardened_blood", "Hardened Blood", "You can hold 25 more toxicity", "tox=25");
		perk("alchemy", 0, 3, "philosophers_eye", "Philosopher's Eye", "Happy accidents far more often, and better quality", "accident%=4,quality=0.08");
		perk("alchemy", 1, 0, "careful_measure", "Careful Measure", "15% chance each ingredient isn't used up", "save%=15");
		perk("alchemy", 1, 1, "apprentice_notes", "Apprentice's Notes", "25% more Alchemy XP", "xp%=25");
		perk("alchemy", 1, 2, "double_distill", "Double Distill", "15% chance of making two", "double%=15");
		perk("alchemy", 1, 3, "tempered_blood", "Tempered Blood", "Toxicity drains 50% faster, and 10% more doubles", "drain%=50,double%=10");
		perk("alchemy", 2, 0, "remedy", "Remedy", "Healing, mana and cures from your draughts work 50% better", "instant%=50");
		perk("alchemy", 2, 1, "field_medic", "Field Medic", "The party near you gets half of an elixir you drink", "share=0.5");
		perk("alchemy", 2, 2, "steady_measure", "Steady Measure", "Better quality", "quality=0.08");
		perk("alchemy", 2, 3, "last_breath", "Last Breath", "With an elixir working on you, a killing blow leaves you at 1 health (once in 10 minutes)", "last_breath=1");
		// smithing and tailoring: the Gate Forge's rolls
		for (String t : new String[] {"smithing", "tailoring"}) {
			String s = t.equals("smithing") ? "" : "_t";
			String piece = t.equals("smithing") ? "weapons and metal armour" : "robes and light armour";
			perk(t, 0, 0, "steady_rhythm" + s, "Steady Rhythm", "Better quality on " + piece, "forge_roll=0.02");
			perk(t, 0, 1, "masters_eye" + s, "Master's Eye", "Better quality again", "forge_roll=0.03");
			perk(t, 0, 2, "hot_forge" + s, t.equals("smithing") ? "Hot Forge" : "Quick Needle", "25% more " + trade(t).name() + " XP", "xp%=25");
			perk(t, 0, 3, "signature" + s, t.equals("smithing") ? "Signature Blade" : "Signature Weave", "Perfect pieces come more often", "forge_roll=0.04");
			perk(t, 1, 0, "tempered" + s, "Tempered", "Upgrades take more often", "upgrade_roll=0.02");
			perk(t, 1, 1, "cheap_steel" + s, t.equals("smithing") ? "Cheap Steel" : "Cheap Cloth", "Upgrades and pieces take 10% fewer common materials", "cost%=-10");
			perk(t, 1, 2, "ember_thrift" + s, "Ember Thrift", "Half the time, the Temper Embers you burn aren't used up", "ember_save%=50");
			perk(t, 1, 3, "master_temper" + s, "Master Temper", "Upgrades take more often again", "upgrade_roll=0.03");
			perk(t, 2, 0, "thrifty" + s, "Thrift", "5% fewer common materials", "cost%=-5");
			perk(t, 2, 1, "spare_piece" + s, "Spare Piece", "10% chance a new piece comes out twice", "double%=10");
			perk(t, 2, 2, "old_secrets" + s, t.equals("smithing") ? "Dwarven Secrets" : "Elven Pattern", "Better quality and upgrades", "forge_roll=0.02,upgrade_roll=0.02");
			perk(t, 2, 3, "grand" + s, t.equals("smithing") ? "Grand Smith" : "Grand Tailor", "10% fewer common materials", "cost%=-10");
		}
		// farming
		perk("farming", 0, 0, "green_thumb", "Green Thumb", "Crops near you grow faster", "growth=1");
		perk("farming", 0, 1, "rich_harvest", "Rich Harvest", "20% chance a ripe crop drops twice", "crop_double%=20");
		perk("farming", 0, 2, "harvest_hand", "Harvest Hand", "25% more Farming XP", "xp%=25");
		perk("farming", 0, 3, "harvest_moon", "Harvest Moon", "Crops grow faster again, 15% more doubles", "growth=1,crop_double%=15");
		perk("farming", 1, 0, "careful_pick", "Careful Pick", "25% chance flowers, mushrooms and berries drop twice", "herb_double%=25");
		perk("farming", 1, 1, "replant", "Replant", "Ripe crops you harvest plant themselves again", "replant=1");
		perk("farming", 1, 2, "golden_crop", "Golden Crop", "3% chance a ripe crop drops a golden carrot", "golden%=3");
		perk("farming", 1, 3, "bloom", "Bloom", "25% more herb doubles", "herb_double%=25");
		perk("farming", 2, 0, "herdsman", "Herdsman", "25% chance animals you breed have twins", "twin%=25");
		perk("farming", 2, 1, "butchers_hand", "Butcher's Hand", "30% chance animals you kill drop double meat", "meat_double%=30");
		perk("farming", 2, 2, "stockman", "Stockman", "25% more Farming XP from beasts and crops", "xp%=25");
		perk("farming", 2, 3, "big_herd", "Big Herd", "25% more twins, 20% more double meat", "twin%=25,meat_double%=20");
		// fishing
		perk("fishing", 0, 0, "patient", "Patient", "15% chance a catch comes up twice", "fish_double%=15");
		perk("fishing", 0, 1, "big_catch", "Big Catch", "15% more doubles", "fish_double%=15");
		perk("fishing", 0, 2, "net_caster", "Net Caster", "25% more Fishing XP", "xp%=25");
		perk("fishing", 0, 3, "full_net", "Full Net", "20% more doubles", "fish_double%=20");
		perk("fishing", 1, 0, "treasure", "Treasure", "10% chance of a treasure with your catch", "treasure%=10");
		perk("fishing", 1, 1, "coin_purse", "Coin Purse", "20% chance of a few coins with your catch", "coins%=20");
		perk("fishing", 1, 2, "lucky", "Lucky", "10% more treasure", "treasure%=10");
		perk("fishing", 1, 3, "abyss_line", "Abyss Line", "15% more treasure", "treasure%=15");
		perk("fishing", 2, 0, "fresh_catch", "Fresh Catch", "What you reel in is Fresh: a meal made with it comes out better", "fresh=0.06");
		perk("fishing", 2, 1, "quick_bite", "Quick Bite", "Fish bite sooner", "lure=50");
		perk("fishing", 2, 2, "sea_legs", "Sea Legs", "From a boat, 20% more doubles", "boat_double%=20");
		perk("fishing", 2, 3, "master_angler", "Master Angler", "Fish bite sooner again, and Fresh fish make meals better again", "lure=40,fresh=0.06");
		// mining
		perk("mining", 0, 0, "rich_vein", "Rich Vein", "15% chance ore drops twice", "ore_double%=15");
		perk("mining", 0, 1, "prospector", "Prospector", "25% more Mining XP", "xp%=25");
		perk("mining", 0, 2, "deep_vein", "Deep Vein", "15% more ore doubles", "ore_double%=15");
		perk("mining", 0, 3, "mother_lode", "Mother Lode", "20% more ore doubles", "ore_double%=20");
		perk("mining", 1, 0, "quarry", "Quarry", "Mine 10% faster", "dig%=10");
		perk("mining", 1, 1, "gem_eye", "Gem Eye", "Now and then a gem in plain stone", "gem%=1");
		perk("mining", 1, 2, "hard_hands", "Hard Hands", "Mine 10% faster again", "dig%=10");
		perk("mining", 1, 3, "dwarven_pick", "Dwarven Pick", "Mine 15% faster again", "dig%=15");
		perk("mining", 2, 0, "tunnel_rat", "Tunnel Rat", "25% less fall damage", "fall%=-25");
		perk("mining", 2, 1, "dark_eye", "Dark Eye", "You see in the dark deep underground", "dark_eye=1");
		perk("mining", 2, 2, "deep_lungs", "Deep Lungs", "Mining Fatigue doesn't touch you", "no_fatigue=1");
		perk("mining", 2, 3, "cave_cat", "Cave Cat", "25% less fall damage again", "fall%=-25");
	}

	// ---------------------------------------------------------------- goods: what the benches make

	public enum Kind {
		MEAL("cooking", 10), BREW("brewing", 5), ELIXIR("alchemy", 8);

		public final String trade;
		public final int minutes;

		Kind(String trade, int minutes) {
			this.trade = trade;
			this.minutes = minutes;
		}

		public static Kind of(String trade) {
			for (Kind k : values()) if (k.trade.equals(trade)) return k;
			return null;
		}
	}

	/**
	 * One thing a bench makes: what goes in (ingredient kinds, one per item, all used), the level it needs, and what it does. stats are
	 * Passives stat keys for the buff's length (a negative one in a brew is its catch); fx are vanilla effects for the same time; now is
	 * what happens at once (heal, mana, cure).
	 */
	public record Good(String id, Kind kind, String name, int level, List<String> needs, Map<String, Double> stats, List<String> fx,
			Map<String, Double> now, int colour, int food) {}

	public static final Map<String, Good> GOODS = new LinkedHashMap<>();

	private static void good(Kind k, String id, String name, int level, String needs, String stats, String fx, String now, int colour, int food) {
		Map<String, Double> s = new LinkedHashMap<>(), n = new LinkedHashMap<>();
		if (!stats.isEmpty()) for (String kv : stats.split(",")) s.put(kv.split("=")[0], Double.parseDouble(kv.split("=")[1]));
		if (!now.isEmpty()) for (String kv : now.split(",")) n.put(kv.split("=")[0], Double.parseDouble(kv.split("=")[1]));
		GOODS.put(id, new Good(id, k, name, level, List.of(needs.split(" ")), s, fx.isEmpty() ? List.of() : List.of(fx.split(",")), n, colour, food));
	}

	/** How much toxicity an elixir leaves in you, of a limit of 100 that drains in twelve minutes: utility ones next to nothing (goods.json). */
	public static final Map<String, Integer> TOX = new HashMap<>();

	/**
	 * The goods come from data/ashbound/trades/goods.json, written by tools/goodsgen.py (one table: archetype, level, recipe; the stats from a
	 * power budget so none is stronger than its level). Read here at class load because each good is an item.
	 */
	static {
		try (var in = Trades.class.getResourceAsStream("/data/ashbound/trades/goods.json")) {
			if (in == null) throw new IllegalStateException("no goods.json: run tools/goodsgen.py");
			var arr = com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(in, java.nio.charset.StandardCharsets.UTF_8)).getAsJsonArray();
			for (var el : arr) {
				var o = el.getAsJsonObject();
				Kind k = switch (o.get("kind").getAsString()) { case "meal" -> Kind.MEAL; case "brew" -> Kind.BREW; default -> Kind.ELIXIR; };
				String id = o.get("id").getAsString();
				good(k, id, o.get("name").getAsString(), o.get("level").getAsInt(), o.get("needs").getAsString(), o.get("stats").getAsString(),
						o.get("fx").getAsString(), o.get("now").getAsString(), o.get("colour").getAsInt(), o.get("food").getAsInt());
				if (k == Kind.ELIXIR) TOX.put(id, o.get("tox").getAsInt());
			}
		} catch (java.io.IOException e) {
			throw new IllegalStateException(e);
		}
	}

	/** What a miss makes, by bench. */
	public static final Map<Kind, String> MISS = Map.of(Kind.MEAL, "burnt_mush", Kind.BREW, "sour_wash", Kind.ELIXIR, "fizzled_draught");
	/** What you know at the start, so the book shows how a recipe reads. */
	private static final List<String> FIRST = List.of("jerky", "hearthbread", "highmourn_ale", "night_eye");

	public static final Map<String, String> KIND_NAMES = new LinkedHashMap<>();

	static {
		for (String[] kv : new String[][] {{"meat", "Meat"}, {"fish", "Fish"}, {"veg", "Vegetable"}, {"grain", "Grain"}, {"fruit", "Fruit"},
				{"sweet", "Sweet"}, {"dairy", "Dairy"}, {"egg", "Egg"}, {"mushroom", "Mushroom"}, {"herb", "Herb"}, {"flower", "Flower"},
				{"water", "Water"}, {"ember", "Ember"}, {"frost", "Frost"}, {"venom", "Venom"}, {"glow", "Glow"}, {"bone", "Bone"},
				{"wart", "Nether Wart"}, {"gate", "Gate material"}, {"nut", "Nut"}, {"spice", "Spice"}})
			KIND_NAMES.put(kv[0], kv[1]);
	}

	// ---------------------------------------------------------------- items

	public static final Map<String, DeferredItem<Item>> ITEMS = new LinkedHashMap<>();

	static {
		for (Good g : GOODS.values()) {
			Item.Properties pr = new Item.Properties().stacksTo(16).food(new FoodProperties.Builder().nutrition(g.food()).saturationModifier(g.kind() == Kind.MEAL ? 0.8f : 0.1f).alwaysEdible().build());
			ITEMS.put(g.id(), Weapons.ITEMS.registerItem(g.id(), p -> new GoodItem(p, g.id()), pr));
		}
		Recipes.items();
		for (String miss : MISS.values())
			ITEMS.put(miss, Weapons.ITEMS.registerItem(miss, p -> new GoodItem(p, miss), new Item.Properties().stacksTo(16)
					.food(new FoodProperties.Builder().nutrition(1).saturationModifier(0).alwaysEdible().build())));
	}

	/** A meal, a brew or an elixir: eaten or drunk, its buff on you for its time, as well made as it was. */
	public static final class GoodItem extends Item {
		final String id;

		GoodItem(Properties p, String id) {
			super(p);
			this.id = id;
		}

		Good good() {
			return GOODS.get(id);
		}

		private Kind kind() {
			Good g = good();
			if (g != null) return g.kind();
			for (var e : MISS.entrySet()) if (e.getValue().equals(id)) return e.getKey();
			return Kind.MEAL;
		}

		/** A weaker meal or brew than the one running isn't had (it would be wasted): sneak to have it anyway. */
		@Override
		public net.minecraft.world.InteractionResultHolder<ItemStack> use(Level level, Player p, InteractionHand hand) {
			ItemStack s = p.getItemInHand(hand);
			Good g = good();
			if (g != null && g.kind() != Kind.ELIXIR && !p.isShiftKeyDown()) {
				double k = mult(quality(s), accident(s)) * (g.kind() == Kind.MEAL ? tired(p, g.id()) : 1);
				Good better = stronger(p, "buff." + g.kind().name(), g, k);
				if (better != null) {
					if (level.isClientSide) p.displayClientMessage(Component.literal("Your " + better.name() + " is stronger and still going. Sneak to have this anyway")
							.withStyle(ChatFormatting.GOLD), true);
					return net.minecraft.world.InteractionResultHolder.fail(s);
				}
			}
			return super.use(level, p, hand);
		}

		@Override
		public UseAnim getUseAnimation(ItemStack s) {
			return kind() == Kind.MEAL ? UseAnim.EAT : UseAnim.DRINK;
		}

		@Override
		public int getUseDuration(ItemStack s, LivingEntity e) {
			return kind() == Kind.MEAL ? 32 : 24;
		}

		@Override
		public ItemStack finishUsingItem(ItemStack s, Level level, LivingEntity e) {
			if (e instanceof ServerPlayer p) {
				Good g = good();
				if (g == null) {
					p.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 120));
					p.displayClientMessage(Component.literal("That was a mistake").withStyle(ChatFormatting.GRAY), true);
				} else consume(p, g, quality(s), accident(s));
			}
			boolean bottle = kind() != Kind.MEAL;
			ItemStack left = super.finishUsingItem(s, level, e);
			if (bottle && e instanceof Player p && !p.getAbilities().instabuild && !p.getInventory().add(new ItemStack(Items.GLASS_BOTTLE)))
				p.drop(new ItemStack(Items.GLASS_BOTTLE), false);
			return left;
		}

		@Override
		public Component getName(ItemStack s) {
			Rarity q = goodRarity(s);
			Component base = super.getName(s);
			return q == null || q == Rarity.COMMON ? base : Component.literal(q.title + " ").append(base).withStyle(q.colour);
		}

		@Override
		public void appendHoverText(ItemStack s, TooltipContext ctx, List<Component> out, TooltipFlag flag) {
			Good g = good();
			if (g == null) {
				out.add(Component.literal("Something went wrong in the making").withStyle(ChatFormatting.DARK_GRAY));
				return;
			}
			double k = mult(quality(s), accident(s));
			if (accident(s)) out.add(Component.literal("A happy accident").withStyle(ChatFormatting.LIGHT_PURPLE));
			for (String line : lines(g, k)) out.add(Component.literal(line).withStyle(line.startsWith("-") ? ChatFormatting.RED : ChatFormatting.BLUE));
			if (!g.stats().isEmpty() || !g.fx().isEmpty()) out.add(Component.literal(minutes(g, accident(s)) + " min, " + kindWord(g.kind()) + " buff").withStyle(ChatFormatting.GRAY));
			int tox = TOX.getOrDefault(g.id(), 0);
			if (tox > 0) out.add(Component.literal("Toxicity " + tox).withStyle(ChatFormatting.DARK_GREEN));
			String by = tag(s).getString("ash_by");
			if (!by.isEmpty()) out.add(Component.literal("Made by " + by).withStyle(ChatFormatting.DARK_GRAY));
		}
	}

	private static String kindWord(Kind k) {
		return k == Kind.MEAL ? "meal" : k == Kind.BREW ? "brew" : "elixir";
	}

	public static List<String> lines(Good g, double k) {
		List<String> out = new ArrayList<>();
		for (var e : g.stats().entrySet()) out.add(statLine(e.getKey(), e.getValue() * (e.getValue() < 0 ? 1 : k)));
		for (String f : g.fx()) out.add("+ " + fxName(f));
		for (var e : g.now().entrySet())
			out.add(switch (e.getKey()) {
				case "heal" -> "Heals " + Math.round(e.getValue() * k) + "% of your health";
				case "mana" -> "Gives back " + Math.round(e.getValue() * k) + "% of your mana";
				default -> "Cures poison, wither, hunger and nausea";
			});
		return out;
	}

	private static String fxName(String f) {
		return switch (f) {
			case "fire_resistance" -> "Fire resistance";
			case "night_vision" -> "Night vision";
			case "water_breathing" -> "Water breathing";
			case "resistance" -> "Resistance";
			default -> f;
		};
	}

	public static String statLine(String key, double v) {
		String name = switch (key) {
			case "health%" -> "% max health";
			case "stamina" -> " stamina";
			case "stamina_regen%" -> "% stamina regen";
			case "move%" -> "% move speed";
			case "armour%" -> "% armour";
			case "stun_armour" -> " stun armour";
			case "mana" -> " max mana";
			case "mana_regen%" -> "% mana regen";
			case "dmg%" -> "% damage";
			case "speed%" -> "% attack speed";
			case "spell%" -> "% spell power";
			case "heal%" -> "% healing";
			case "arrow%" -> "% bow damage";
			case "ash%" -> "% Ash";
			case "coins%" -> "% coins";
			case "dodge_cost%" -> "% cheaper rolls";
			case "stamina%" -> "% max stamina";
			case "mana%" -> "% max mana";
			case "dig%" -> "% mining speed";
			default -> " " + key;
		};
		long r = Math.round(v);
		return (r >= 0 ? "+" : "") + r + name;
	}

	// ---------------------------------------------------------------- the player's trades

	/** xp.TRADE, perk.ID, known.GOOD, buff.KIND (good|end tick|mult), buff2/3.ELIXIR, breath (tick of the last Last Breath),
	 * ate.GOOD (times|tick), drinks (ticks of the brews in the last ten minutes), tox (amount|tick). */
	public static final Supplier<AttachmentType<Map<String, String>>> STATE = Coins.ATTACHMENTS.register("trades",
			() -> AttachmentType.<Map<String, String>>builder(() -> new HashMap<>()).serialize(Codec.unboundedMap(Codec.STRING, Codec.STRING)).copyOnDeath().build());

	/** What the client was last sent; what it knows of its own trades. */
	public static Map<String, String> client = Map.of();

	private static Map<String, String> state(Player p) {
		return p.level().isClientSide ? client : p.getData(STATE);
	}

	private static void put(ServerPlayer p, String k, String v) {
		Map<String, String> m = new HashMap<>(p.getData(STATE));
		if (v == null) m.remove(k);
		else m.put(k, v);
		p.setData(STATE, m);
		DIRTY.add(p.getUUID());
	}

	public static int xp(Player p, String trade) {
		try {
			return Integer.parseInt(state(p).getOrDefault("xp." + trade, "0"));
		} catch (NumberFormatException e) {
			return 0;
		}
	}

	public static int level(Player p, String trade) {
		return level(xp(p, trade));
	}

	public static boolean has(Player p, String perk) {
		return state(p).containsKey("perk." + perk);
	}

	public static boolean knows(Player p, String good) {
		if (state(p).containsKey("known." + good) || FIRST.contains(good)) return true;
		Good g = GOODS.get(good);                         // the first level's recipes everyone knows; the rest are found (Recipes)
		return g != null && g.level() <= 1;
	}

	/** A note kept with your trades (Recipes: who taught you what day). */
	static String note(Player p, String k) {
		return state(p).get(k);
	}

	static void note(ServerPlayer p, String k, String v) {
		put(p, k, v);
	}

	/** Whether you could make it now: you know it and your trade is up to it. */
	public static boolean canMake(Player p, Good g) {
		return knows(p, g.id()) && level(p, g.kind().trade) >= g.level();
	}

	/** Learns a recipe (a page read, a townsman's secret); false if you knew it. */
	public static boolean learn(ServerPlayer p, String good) {
		if (!GOODS.containsKey(good) || knows(p, good)) return false;
		put(p, "known." + good, "1");
		sync(p);
		return true;
	}

	public static int earned(Player p) {
		int n = 0;
		for (Trade t : ALL) n += level(p, t.id()) - 1;
		return Math.min(MOST_POINTS, n);
	}

	public static int spent(Player p) {
		int n = 0;
		for (String k : state(p).keySet())
			if (k.startsWith("perk.")) {
				Perk pk = PERKS.get(k.substring(5));
				if (pk != null) n += pk.cost();
			}
		return n;
	}

	/** A perk value summed over the trade's perks you have. */
	public static double perk(Player p, String trade, String key) {
		double v = 0;
		for (String k : state(p).keySet())
			if (k.startsWith("perk.")) {
				Perk pk = PERKS.get(k.substring(5));
				if (pk != null && pk.trade().equals(trade)) v += pk.fx().getOrDefault(key, 0.0);
			}
		return v;
	}

	/** What's stopping you taking a perk, or null. */
	public static String why(Player p, Perk pk) {
		if (has(p, pk.id())) return "Already yours";
		if (level(p, pk.trade()) < pk.level()) return "Needs " + trade(pk.trade()).name() + " " + pk.level();
		if (pk.tier() > 0) {
			for (Perk o : PERKS.values())
				if (o.trade().equals(pk.trade()) && o.branch() == pk.branch() && o.tier() == pk.tier() - 1 && !has(p, o.id())) return "Take " + o.name() + " first";
		}
		if (earned(p) - spent(p) < pk.cost()) return "Needs " + pk.cost() + " trade point" + (pk.cost() > 1 ? "s" : "");
		return null;
	}

	/** Trade XP, with the trade's own XP perks; tells you when a level comes. */
	public static void gain(ServerPlayer p, String trade, double amount) {
		if (amount <= 0 || p.isSpectator()) return;
		int before = xp(p, trade), add = (int) Math.max(1, Math.round(amount * (1 + perk(p, trade, "xp%") / 100)));
		int was = level(before), now = level(before + add);
		put(p, "xp." + trade, Integer.toString(before + add));
		if (now > was) {
			Trade t = trade(trade);
			p.displayClientMessage(Component.literal(t.name() + " " + now + (rank(now).equals(rank(was)) ? "" : ", " + rank(now)))
					.withStyle(ChatFormatting.GOLD), false);
			if (earned(p) > spent(p)) p.displayClientMessage(Component.literal("You have a trade point to spend: the Trades tab").withStyle(ChatFormatting.GRAY), false);
			List<String> learnt = new ArrayList<>();                 // the recipes you know that this level lets you make, and the ones still to find
			int unfound = 0;
			for (Good g : GOODS.values())
				if (g.kind().trade.equals(trade) && g.level() > was && g.level() <= now) {
					if (knows(p, g.id())) learnt.add(g.name());
					else unfound++;
				}
			if (!learnt.isEmpty())
				p.displayClientMessage(Component.literal("You can make now: " + String.join(", ", learnt)).withStyle(ChatFormatting.YELLOW), false);
			if (unfound > 0)
				p.displayClientMessage(Component.literal(unfound + " more recipe" + (unfound > 1 ? "s" : "") + " of this level to find: ask townsfolk, read pages from chests and monsters, or guess")
						.withStyle(ChatFormatting.GRAY), false);
			p.playNotifySound(SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 0.6f, 1.3f);
		}
	}

	private static final Set<UUID> DIRTY = new HashSet<>();

	public static void sync(ServerPlayer p) {
		DIRTY.remove(p.getUUID());
		PacketDistributor.sendToPlayer(p, new Net.TradeState(new HashMap<>(p.getData(STATE))));
	}

	// ---------------------------------------------------------------- buffs

	/**
	 * A good's rarity (pass 16, was Crude to Perfect): it multiplies what the good gives, never its catch. Which one you get is rolled from
	 * your trade level ({@link #ODDS}), lifted by the quality perks and Fresh Catch, kept to what the bench can make ({@link Bench#tier}) and
	 * raised by a gate's material in the pot.
	 */
	public enum Rarity {
		COMMON("Common", 1.0, ChatFormatting.WHITE), UNCOMMON("Uncommon", 1.25, ChatFormatting.GREEN), RARE("Rare", 1.5, ChatFormatting.AQUA),
		EPIC("Epic", 1.8, ChatFormatting.LIGHT_PURPLE), LEGENDARY("Legendary", 2.2, ChatFormatting.GOLD);

		public final String title;
		public final double mult;
		public final ChatFormatting colour;

		Rarity(String title, double mult, ChatFormatting colour) {
			this.title = title;
			this.mult = mult;
			this.colour = colour;
		}
	}

	/** Chance in % of each rarity, Common to Legendary, at trade level 1, 25 and 50; a straight line between. */
	static final double[][] ODDS = {{85, 14, 1, 0, 0}, {45, 33, 16, 5, 1}, {20, 35, 28, 13, 4}};

	/** The odds at a level (past 50 by the quality perks: each 0.01 of them is a level). */
	public static double[] odds(double lv) {
		lv = Math.max(1, lv);
		double[] a = lv <= 25 ? ODDS[0] : ODDS[1], b = lv <= 25 ? ODDS[1] : ODDS[2];
		double t = lv <= 25 ? (lv - 1) / 24 : Math.min(1.4, (lv - 25) / 25);
		double[] out = new double[5];
		double sum = 0;
		for (int i = 0; i < 5; i++) sum += out[i] = Math.max(0, a[i] + (b[i] - a[i]) * t);
		for (int i = 0; i < 5; i++) out[i] = out[i] / sum * 100;
		return out;
	}

	/** One rarity from the odds, 0 Common to 4 Legendary, best of `rolls`, at least `floor`, at most `cap`. */
	public static int rollRarity(net.minecraft.util.RandomSource r, double lv, int floor, int cap, int rolls) {
		double[] o = odds(lv);
		int best = 0;
		for (int n = 0; n < rolls; n++) {
			double x = r.nextDouble() * 100;
			int q = 0;
			while (q < 4 && x >= o[q]) x -= o[q++];
			best = Math.max(best, q);
		}
		return Math.max(Math.min(floor, cap), Math.min(best, cap));
	}

	/** The best rarity a bench of this tier makes (0 any mod's: Rare, 1 ours: Epic, 2 the house's: Legendary) and how many rolls it takes. */
	public static int cap(int tier) {
		return tier <= 0 ? 2 : tier == 1 ? 3 : 4;
	}

	public static int rolls(int tier) {
		return tier >= 2 ? 2 : 1;
	}

	/** Your rarity level at this bench: your trade level, lifted by the quality perks and Fresh Catch (0.01 of them is a level). */
	public static double rarityLevel(Player p, Bench b) {
		return level(p, b.kind.trade) + 100 * (perk(p, b.kind.trade, "quality") + fresh(b));
	}

	/** Each rarity's chance in %, exactly as {@link #rollRarity} rolls it: best of `rolls`, then kept between floor and cap. */
	public static double[] oddsAt(double lv, int floor, int cap, int rolls) {
		double[] o = odds(lv), out = new double[5];
		double below = 0;
		for (int q = 0; q < 5; q++) {
			double upTo = below + o[q] / 100;
			double pq = Math.pow(Math.min(1, upTo), rolls) - Math.pow(below, rolls);
			below = upTo;
			out[Math.max(Math.min(floor, cap), Math.min(q, cap))] += pq * 100;
		}
		return out;
	}

	/** The lowest rarity a gate's material makes: an F-D gate's Uncommon, C-A's Rare, S's Epic. */
	public static int gateFloor(Bench b) {
		int floor = 0;
		for (int i = 0; i < SLOTS_IN; i++) {
			ItemStack s = b.in.getItem(i);
			if (!"gate".equals(kindOf(s))) continue;
			String path = BuiltInRegistries.ITEM.getKey(s.getItem()).getPath();
			for (var d : Gear.DUNGEONS)
				for (String m : d.mats())
					if (path.equals(m)) floor = Math.max(floor, "FED".indexOf(d.rank()) >= 0 ? 1 : d.rank() == 'S' ? 3 : 2);
		}
		return floor;
	}

	public static double mult(int quality, boolean accident) {
		double k = Rarity.values()[Math.max(1, Math.min(5, quality)) - 1].mult;
		return accident ? k * 1.1 : k;
	}

	private static int minutes(Good g, boolean accident) {
		return (int) Math.round(g.kind().minutes * (accident ? 1.5 : 1));
	}

	private record Buff(Good good, long end, double k) {}

	private static Buff buff(Player p, String slot) {
		String v = state(p).get(slot);
		if (v == null) return null;
		String[] a = v.split("\\|");
		Good g = GOODS.get(a[0]);
		if (g == null && a[0].startsWith(SNACK)) {
			ResourceLocation id = ResourceLocation.tryParse(a[0].substring(SNACK.length()));
			if (id != null) g = snack(BuiltInRegistries.ITEM.get(id));
		}
		if (g == null || a.length < 3) return null;
		try {
			return new Buff(g, Long.parseLong(a[1]), Double.parseDouble(a[2]));
		} catch (NumberFormatException e) {
			return null;
		}
	}

	private static final String[] SLOTS = {"buff.MEAL", "buff.BREW", "buff.ELIXIR", "buff2.ELIXIR", "buff3.ELIXIR", "buff.SNACK"}, ELIXIR_SLOTS = {"buff.ELIXIR", "buff2.ELIXIR", "buff3.ELIXIR"};

	// ---------------------------------------------------------------- fatigue: strong buffs, but not all the time

	/** A dish had again soon is worth less: its strength by how many times you've had it lately. */
	private static final double[] TIRED = {1, 0.7, 0.45, 0.25};
	/** One "time" of a dish wears off in 20 minutes (10 with Highmourn Table). */
	private static final long TIRE_TICKS = 24000;
	/** Brews counted for tipsiness, and toxicity's limit and how fast it drains: all of it in twelve minutes, so one strong elixir can be kept up
	 * (they last eight) but two only by an alchemist with Tempered Blood. */
	public static final long DRINK_TICKS = 12000;
	public static final double TOX_LIMIT = 100, TOX_DRAIN = 100 / 14400.0;

	/** How many times you've had a dish lately, worn off by the time since. */
	private static int ate(Player p, String good) {
		String v = state(p).get("ate." + good);
		if (v == null) return 0;
		String[] a = v.split("\\|");
		try {
			long tire = perk(p, "cooking", "tire") > 0 ? TIRE_TICKS / 2 : TIRE_TICKS;
			return (int) Math.max(0, Integer.parseInt(a[0]) - (p.level().getGameTime() - Long.parseLong(a[1])) / tire);
		} catch (RuntimeException e) {
			return 0;
		}
	}

	/** A dish's strength for you now, as tired of it as you are. */
	public static double tired(Player p, String good) {
		return TIRED[Math.min(TIRED.length - 1, ate(p, good))];
	}

	// ---------------------------------------------------------------- any other food: a small buff of its own (11/7)

	/** Ids of the snack buffs: "snack:" and the food's item id. */
	public static final String SNACK = "snack:";
	/** What a kind of food does eaten as it is: its stat and that stat at full strength (a first-level meal's own numbers). */
	private static final Map<String, Object[]> SNACK_STAT = new HashMap<>();
	private static final Map<Item, java.util.Optional<Good>> SNACKS = new java.util.concurrent.ConcurrentHashMap<>();

	static {
		for (Object[] e : new Object[][] {{"meat", "stamina%", 10.0}, {"egg", "stamina%", 10.0}, {"fish", "mana%", 9.0}, {"veg", "stamina_regen%", 13.0},
				{"nut", "stamina_regen%", 13.0}, {"sweet", "stamina_regen%", 13.0}, {"grain", "health%", 4.0}, {"dairy", "health%", 4.0},
				{"fruit", "mana_regen%", 9.0}, {"mushroom", "mana_regen%", 9.0}, {"herb", "heal%", 3.0}, {"spice", "dmg%", 3.0}, {"ember", "dmg%", 3.0},
				{"flower", "spell%", 3.0}, {"glow", "spell%", 3.0}, {"frost", "armour%", 5.0}})
			SNACK_STAT.put((String) e[0], new Object[] {e[1], e[2]});
	}

	/**
	 * The buff of a food that isn't one of ours (vanilla's, Croptopia's, Farmer's Delight's...), or null: its kind's stat, as strong as it is
	 * filling (a big dish about half a cooked meal), a real dish a little health besides. Eaten again soon it tires you like a meal does.
	 */
	public static Good snack(Item it) {
		return SNACKS.computeIfAbsent(it, i -> java.util.Optional.ofNullable(makeSnack(i))).orElse(null);
	}

	private static Good makeSnack(Item it) {
		if (it instanceof GoodItem || it == Items.AIR) return null;
		ItemStack s = new ItemStack(it);
		FoodProperties f = s.get(DataComponents.FOOD);
		if (f == null || f.nutrition() <= 0) return null;
		String kind = kindOf(s);
		Object[] st = kind == null ? new Object[] {"stamina_regen%", 13.0} : SNACK_STAT.get(kind);
		if (st == null) return null;                                   // bones, venom, warts: not a meal
		int n = f.nutrition();
		double k = Math.max(0.12, Math.min(0.6, n / 16.0));
		Map<String, Double> stats = new LinkedHashMap<>();
		stats.put((String) st[0], (double) Math.max(1, Math.round((Double) st[1] * k)));
		if (n >= 7) stats.merge(st[0].equals("health%") ? "stamina%" : "health%", st[0].equals("health%") ? (double) Math.round(10 * k) : n >= 10 ? 2.0 : 1.0, Double::sum);
		int minutes = Math.max(3, Math.min(8, 2 + n / 2));
		return new Good(SNACK + BuiltInRegistries.ITEM.getKey(it), Kind.MEAL, it.getDescription().getString(), 0, List.of(), stats, List.of(), Map.of(), 0xFFFFFF,
				minutes);
	}

	/** A snack's minutes (kept in its food field). */
	public static int snackMinutes(Good g) {
		return g.food();
	}

	/** Eating any other food: its buff in the snack slot, worth less the more often you've had it. */
	private static void snacked(net.neoforged.neoforge.event.entity.living.LivingEntityUseItemEvent.Finish e) {
		if (e.getEntity() instanceof ServerPlayer p) eatSnack(p, e.getItem());
	}

	static void eatSnack(ServerPlayer p, ItemStack food) {
		Good g = snack(food.getItem());
		if (g == null) return;
		long now = p.level().getGameTime();
		int times = ate(p, g.id());
		double k = TIRED[Math.min(TIRED.length - 1, times)];
		put(p, "ate." + g.id(), (times + 1) + "|" + now);
		Good better = stronger(p, "buff.SNACK", g, k);
		if (better != null) {
			p.displayClientMessage(Component.literal("Filling, but your " + better.name() + " buff is stronger: kept it").withStyle(ChatFormatting.GRAY), true);
			DIRTY.add(p.getUUID());
			return;
		}
		put(p, "buff.SNACK", g.id() + "|" + (now + snackMinutes(g) * 1200L) + "|" + k);
		p.displayClientMessage(Component.literal(g.name() + ": " + String.join(", ", lines(g, k)) + ", " + snackMinutes(g) + " min"
				+ (times > 0 ? " (" + Math.round(k * 100) + "%: you've had it lately)" : "")).withStyle(times > 0 ? ChatFormatting.GOLD : ChatFormatting.GREEN), true);
		DIRTY.add(p.getUUID());
	}

	/** The food's buff under its name, for any food that isn't ours: what it gives you now, tired of it as you are. */
	private static void snackTooltip(net.neoforged.neoforge.event.entity.player.ItemTooltipEvent e) {
		Good g = snack(e.getItemStack().getItem());
		if (g == null) return;
		double k = e.getEntity() == null ? 1 : tired(e.getEntity(), g.id());
		List<Component> out = e.getToolTip();
		int at = Math.min(1, out.size());
		for (String l : lines(g, k)) out.add(at++, Component.literal(l).withStyle(ChatFormatting.BLUE));
		out.add(at++, Component.literal(snackMinutes(g) + " min, snack buff" + (k < 1 ? " (" + Math.round(k * 100) + "%: had lately)" : "")).withStyle(k < 1 ? ChatFormatting.GOLD : ChatFormatting.GRAY));
	}

	/** What one point of each stat is worth, against a first-level meal (so a buff's strength reads across stats). */
	private static final Map<String, Double> WORTH = new HashMap<>();

	static {
		for (Object[] e : new Object[][] {{"stamina%", 10.0}, {"stamina", 10.0}, {"stamina_regen%", 13.0}, {"health%", 4.0}, {"mana%", 9.0}, {"mana", 10.0},
				{"mana_regen%", 9.0}, {"move%", 2.0}, {"heal%", 3.0}, {"spell%", 3.0}, {"dmg%", 5.0}, {"armour%", 8.0}, {"speed%", 2.0}, {"arrow%", 3.0},
				{"dodge_cost%", 5.0}, {"ash%", 6.0}, {"coins%", 6.0}, {"dig%", 16.0}, {"stun_armour", 2.0}})
			WORTH.put((String) e[0], (Double) e[1]);
	}

	/** A buff's strength: its stats, each against a first-level meal's, times its make. */
	static double strength(Good g, double k) {
		double v = 0;
		for (var e : g.stats().entrySet()) if (e.getValue() > 0) v += e.getValue() / WORTH.getOrDefault(e.getKey(), 5.0);
		return v * k;
	}

	/** The running meal or brew (or snack) that a new one would wipe out though it's stronger, or null: a weaker one doesn't
	 *  replace it (11/7: "I eat a rare food, then a bad one, and it just replaces the buffs"); sneak to eat it anyway. */
	public static Good stronger(Player p, String slot, Good g, double k) {
		Buff b = buff(p, slot);
		long now = p.level().getGameTime();
		if (b == null || b.end() - now < 600 || b.good() == g || g.stats().isEmpty()) return null;
		return strength(b.good(), b.k()) > strength(g, k) * 1.05 ? b.good() : null;
	}

	/** Brews drunk in the last ten minutes. */
	private static List<Long> drinks(Player p) {
		List<Long> out = new ArrayList<>();
		long now = p.level().getGameTime();
		for (String t : state(p).getOrDefault("drinks", "").split(","))
			try {
				if (!t.isEmpty() && now - Long.parseLong(t) < DRINK_TICKS) out.add(Long.parseLong(t));
			} catch (NumberFormatException e) {
				// skip it
			}
		return out;
	}

	/** 0 sober, 1 tipsy (the second brew in ten minutes, the third with Hard Head), 2 drunk (one more). */
	public static int tipsy(Player p) {
		return Math.max(0, Math.min(2, drinks(p).size() - 1 - (int) perk(p, "brewing", "tipsy")));
	}

	public static double toxLimit(Player p) {
		return TOX_LIMIT + perk(p, "alchemy", "tox");
	}

	/** Toxicity in you now, drained by the time since the last elixir. */
	public static double toxicity(Player p) {
		String v = state(p).get("tox");
		if (v == null) return 0;
		String[] a = v.split("\\|");
		try {
			double rate = TOX_DRAIN * (1 + perk(p, "alchemy", "drain%") / 100);
			return Math.max(0, Double.parseDouble(a[0]) - (p.level().getGameTime() - Long.parseLong(a[1])) * rate);
		} catch (RuntimeException e) {
			return 0;
		}
	}

	/** Your buffs still running: good, ticks left, strength. For the Trades tab. */
	public static List<Object[]> running(Player p) {
		List<Object[]> out = new ArrayList<>();
		long now = p.level().getGameTime();
		for (String s : SLOTS) {
			Buff b = buff(p, s);
			if (b != null && b.end() > now) out.add(new Object[] {b.good(), b.end() - now, b.k()});
		}
		return out;
	}

	/** What a meal, a brew or an elixir does now and for its time, for you and maybe the party near you. */
	static void consume(ServerPlayer p, Good g, int quality, boolean accident) {
		String trade = g.kind().trade;
		double k = mult(quality, accident);
		give(p, g, k, minutes(g, accident), false);
		double share = perk(p, trade, "share");
		if (share > 0) {
			Map<UUID, String> circle = Party.circle(p);
			for (ServerPlayer o : p.serverLevel().players())
				if (o != p && circle.containsKey(o.getUUID()) && o.distanceToSqr(p) < 64) {
					give(o, g, k * Math.min(1, share), minutes(g, accident), true);
					o.displayClientMessage(Component.literal(p.getGameProfile().getName() + " shared " + g.name()).withStyle(ChatFormatting.GRAY), true);
				}
		}
	}

	/** Where a new elixir goes: its own slot if it's running, else an empty one, else the one closest to running out. */
	private static String elixirSlot(Player p, Good g) {
		long now = p.level().getGameTime();
		String free = null, soonest = null;
		long end = Long.MAX_VALUE;
		for (String s : ELIXIR_SLOTS) {
			Buff b = buff(p, s);
			if (b == null || b.end() <= now) {
				if (free == null) free = s;
			} else if (b.good() == g) return s;
			else if (b.end() < end) {
				end = b.end();
				soonest = s;
			}
		}
		return free != null ? free : soonest;
	}

	/** What having this good does to your fatigue: a dish tires you of it, a brew counts toward tipsy, an elixir adds toxicity. */
	private static void fatigue(ServerPlayer p, Good g, boolean shared) {
		long now = p.level().getGameTime();
		switch (g.kind()) {
			case MEAL -> {
				int times = ate(p, g.id());
				put(p, "ate." + g.id(), (times + 1) + "|" + now);
				if (times > 0 && !shared)
					p.displayClientMessage(Component.literal("You're tiring of " + g.name() + ": " + Math.round(TIRED[Math.min(TIRED.length - 1, times)] * 100)
							+ "% as good. Something else would be better").withStyle(ChatFormatting.GOLD), false);
			}
			case BREW -> {
				if (shared) return;
				int was = tipsy(p);
				List<Long> d = drinks(p);
				d.add(now);
				StringBuilder sb = new StringBuilder();
				for (long t : d) sb.append(sb.length() > 0 ? "," : "").append(t);
				put(p, "drinks", sb.toString());
				int is = tipsy(p);
				if (is > was) p.displayClientMessage(Component.literal(is == 1 ? "You're tipsy: a little slower for a while" : "You're drunk: slower, no running, and the world sways")
						.withStyle(ChatFormatting.GOLD), false);
			}
			case ELIXIR -> {
				int tox = TOX.getOrDefault(g.id(), 0);
				if (tox <= 0 || shared) return;
				double was = toxicity(p), is = was + tox;
				put(p, "tox", is + "|" + now);
				if (is > toxLimit(p) && was <= toxLimit(p))
					p.displayClientMessage(Component.literal("Too much in your blood: weak and sick until it drains").withStyle(ChatFormatting.RED), false);
			}
		}
	}

	/** Puts one good's buff on someone (a shared one at the sharer's strength, but its catch at the drinker's own). */
	private static void give(ServerPlayer p, Good g, double k, int minutes, boolean shared) {
		String trade = g.kind().trade;
		if (g.kind() == Kind.MEAL) k *= tired(p, g.id());
		fatigue(p, g, shared);
		double power = 1 + perk(p, trade, "power%") / 100, time = 1 + perk(p, trade, "time%") / 100;
		int ticks = (int) Math.round(minutes * 60 * 20 * time);
		boolean kept = false;
		if (!g.stats().isEmpty()) {
			String slot = g.kind() == Kind.ELIXIR ? elixirSlot(p, g) : "buff." + g.kind().name();
			Good better = g.kind() == Kind.ELIXIR || p.isShiftKeyDown() ? null : stronger(p, slot, g, k * power);
			if (better != null) {
				kept = true;
				p.displayClientMessage(Component.literal("Your " + better.name() + " is stronger: kept it (sneak while eating to swap)").withStyle(ChatFormatting.GOLD), false);
			} else put(p, slot, g.id() + "|" + (p.level().getGameTime() + ticks) + "|" + (k * power));
		}
		for (String f : g.fx()) {
			Holder<MobEffect> e = switch (f) {
				case "fire_resistance" -> MobEffects.FIRE_RESISTANCE;
				case "night_vision" -> MobEffects.NIGHT_VISION;
				case "water_breathing" -> MobEffects.WATER_BREATHING;
				case "resistance" -> MobEffects.DAMAGE_RESISTANCE;
				default -> null;
			};
			if (e != null) p.addEffect(new MobEffectInstance(e, ticks, 0, false, true));
		}
		double instant = (1 + perk(p, "alchemy", "instant%") / 100) * k;
		for (var e : g.now().entrySet()) {
			switch (e.getKey()) {
				case "heal" -> p.heal((float) (p.getMaxHealth() * e.getValue() / 100 * instant));
				case "mana" -> p.setData(Spells.MANA, Math.min(Spells.max(p), p.getData(Spells.MANA) + (float) (Spells.max(p) * e.getValue() / 100 * instant)));
				default -> {
					p.removeEffect(MobEffects.POISON);
					p.removeEffect(MobEffects.WITHER);
					p.removeEffect(MobEffects.HUNGER);
					p.removeEffect(MobEffects.CONFUSION);
				}
			}
		}
		if (!shared && !kept) p.displayClientMessage(Component.literal(g.name() + ": " + String.join(", ", lines(g, k * power))).withStyle(ChatFormatting.GREEN), true);
		DIRTY.add(p.getUUID());
	}

	/** Your trade buffs' stat, for Passives.stat: meals, brews (catches shrunk by your Brewing perks), elixirs, and perk stats like dig%. */
	static double stat(Player p, String key) {
		if (!(p instanceof ServerPlayer)) return 0;
		double v = 0;
		long now = p.level().getGameTime();
		for (String s : SLOTS) {
			Buff b = buff(p, s);
			if (b == null || b.end() <= now) continue;
			Double base = b.good().stats().get(key);
			if (base == null) continue;
			if (base < 0) {
				// a brew's catch: what it costs you, made smaller by Clear Head and the rest
				double cut = b.good().kind() == Kind.BREW ? Math.max(0, 1 + perk(p, "brewing", "catch%") / 100) : 1;
				v += base * cut;
			} else v += base * b.k();
		}
		if (key.equals("dig%") || key.equals("fall%")) v += perk(p, "mining", key);
		int tipsy = tipsy(p);
		if (tipsy > 0 && key.equals("move%")) v -= tipsy == 1 ? 5 : 10;
		if (tipsy > 1 && key.equals("stamina_regen%")) v -= 20;
		return v;
	}

	// ---------------------------------------------------------------- what an item is, to a cook

	private static TagKey<Item> c(String path) {
		return TagKey.create(Registries.ITEM, ResourceLocation.fromNamespaceAndPath("c", path));
	}

	private static final TagKey<Item> RAW_MEAT = c("foods/raw_meat"), COOKED_MEAT = c("foods/cooked_meat"), RAW_FISH = c("foods/raw_fish"),
			COOKED_FISH = c("foods/cooked_fish"), VEG = c("foods/vegetable"), FRUIT = c("foods/fruit"), BERRY = c("foods/berry"),
			BREAD = c("foods/bread"), CROPS = c("crops"), MUSHROOMS = c("mushrooms"), MILK = c("foods/milk"), EGGS = c("eggs"),
			FLOWERS = TagKey.create(Registries.ITEM, ResourceLocation.withDefaultNamespace("flowers")), SEEDS = c("seeds");

	/** c:crops, for the self-test's sweep of the food mods */
	static final TagKey<Item> CROPS_TAG = CROPS;

	private static Set<String> gateMats;

	private static boolean gate(String path, String ns) {
		if (gateMats == null) {
			gateMats = new HashSet<>();
			for (var d : Gear.DUNGEONS) for (String m : d.mats()) if (m != null) gateMats.add(m);
		}
		return ns.equals(Ashbound.ID) && gateMats.contains(path);
	}

	/**
	 * Whether a word of the id is one of these (pass 16: whole words, so "steamed" isn't tea, "veggie" isn't egg, "eggplant" isn't egg): a word
	 * matches as itself, with an s or es, or as the end or start of a longer word when it's 4+ letters ("blueberry" is berry, "leafy" is leaf).
	 */
	private static boolean any(String path, String... words) {
		String[] tokens = path.split("_");
		for (String w : words)
			for (String t : tokens)
				if (t.equals(w) || t.equals(w + "s") || t.equals(w + "es") || (w.length() >= 4 && (t.endsWith(w) || t.startsWith(w) && ENDINGS.contains(t.substring(w.length())))))
					return true;
		return false;
	}

	/** How a word may go on and still be itself: "leafy", "malted", "glowing" - not "pearl" for pear or "rosemary" for rose. */
	private static final Set<String> ENDINGS = Set.of("y", "ed", "ing", "ie", "ies", "er", "ers");

	/** Raw ingredients by their exact id (any mod's, Croptopia's crops and orchards most of all), looked at before the word rules. */
	private static final Map<String, String> RAW = new HashMap<>();

	private static void raw(String kind, String ids) {
		for (String id : ids.split(" ")) RAW.put(id, kind);
	}

	static {
		raw("veg", "artichoke asparagus bellpepper blackbean broccoli cabbage cauliflower celery cucumber eggplant garlic greenbean greenonion kale leek lettuce "
				+ "onion radish rhubarb rutabaga soybean spinach squash sweetpotato tomatillo tomato turnip yam zucchini saguaro");
		raw("fruit", "apricot avocado banana blackberry blueberry cantaloupe cherry coconut cranberry currant date dragonfruit elderberry fig grape grapefruit "
				+ "honeydew kiwi kumquat lemon lime mango nectarine olive orange peach pear persimmon pineapple plum raspberry starfruit strawberry");
		raw("nut", "almond cashew peanut pecan walnut hazelnut chestnut acorn");
		raw("spice", "cinnamon ginger mustard nutmeg pepper peppercorn turmeric vanilla salt paprika clove cardamom");
		raw("ember", "chile_pepper");
		raw("grain", "barley corn hops oat rice flour dough noodle tortilla");
		raw("herb", "basil tea coffee rosemary oregano parsley dill chive");
		raw("dairy", "butter milk_bottle");
	}

	/** The ingredient kind of an item (one: what it's most like), or null if no bench wants it. */
	public static String kindOf(ItemStack s) {
		if (s.isEmpty()) return null;
		ResourceLocation id = BuiltInRegistries.ITEM.getKey(s.getItem());
		String path = id.getPath(), ns = id.getNamespace();
		if (gate(path, ns)) return "gate";
		if (s.getItem() instanceof GoodItem) return null;
		String raw = RAW.get(path);
		if (raw != null && !path.endsWith("_seed") && !path.endsWith("_sapling")) return raw;
		if (s.is(Items.NETHER_WART) || path.contains("nether_wart")) return "wart";
		if (s.is(Items.POTION) || s.is(Items.WATER_BUCKET) || any(path, "water_bottle")) return "water";
		if (s.is(Items.BLAZE_POWDER) || s.is(Items.MAGMA_CREAM) || s.is(Items.FIRE_CHARGE) || any(path, "ember", "blaze", "chili", "pepper", "cinder")) return "ember";
		if (s.is(Items.SNOWBALL) || s.is(Items.ICE) || s.is(Items.PACKED_ICE) || any(path, "frost", "snow", "glacier")) return "frost";
		if (s.is(Items.SPIDER_EYE) || s.is(Items.POISONOUS_POTATO) || s.is(Items.FERMENTED_SPIDER_EYE) || s.is(Items.PUFFERFISH) || any(path, "venom", "poison", "toxic")) return "venom";
		if (s.is(Items.GLOWSTONE_DUST) || s.is(Items.GLOW_BERRIES) || s.is(Items.GLOW_INK_SAC) || s.is(Items.AMETHYST_SHARD) || any(path, "glow", "luminous")) return "glow";
		if (s.is(Items.BONE) || s.is(Items.BONE_MEAL)) return "bone";
		if (s.is(RAW_FISH) || s.is(COOKED_FISH) || any(path, "fish", "salmon", "cod", "trout", "carp", "tuna", "eel", "squid", "crab", "shrimp", "clam", "anchovy", "calamari", "oyster", "roe", "sushi", "lobster", "mussel")) return "fish";
		if (s.is(RAW_MEAT) || s.is(COOKED_MEAT) || any(path, "beef", "pork", "mutton", "chicken", "rabbit", "venison", "bacon", "ham", "sausage", "steak", "meat", "chop", "drumstick", "pepperoni", "salami", "jerky", "carnitas", "burger", "frog", "meatball", "meatballs"))
			return "meat";
		if (s.is(EGGS) || any(path, "egg")) return "egg";
		if (s.is(MILK) || s.is(Items.MILK_BUCKET) || any(path, "milk", "cheese", "butter", "cream", "yogurt", "yoghurt", "crema", "mozzarella")) return "dairy";
		if (s.is(Items.SUGAR) || s.is(Items.HONEY_BOTTLE) || s.is(Items.HONEYCOMB) || s.is(Items.COCOA_BEANS) || any(path, "sugar", "honey", "syrup", "chocolate", "jam", "caramel", "candy", "candied", "toffee", "fudge"))
			return "sweet";
		if (s.is(MUSHROOMS) || any(path, "mushroom", "fungus", "truffle", "morel")) return "mushroom";
		if (s.is(FLOWERS) || any(path, "flower", "rose", "tulip", "lily", "orchid", "lavender", "daisy", "hibiscus", "bloom")) return "flower";
		if (s.is(FRUIT) || s.is(BERRY) || any(path, "apple", "berry", "berries", "melon", "grape", "cherry", "peach", "orange", "lemon", "banana", "coconut", "plum", "pear", "fig", "fruit"))
			return "fruit";
		if (s.is(BREAD) || any(path, "wheat", "bread", "flour", "dough", "rice", "barley", "oat", "rye", "corn", "hops", "malt", "pasta", "crust", "bun", "baguette", "croissant", "toast", "oatmeal", "pretzel", "waffle", "scones")) return "grain";
		if (any(path, "herb", "leaf", "leaves", "mint", "sage", "thyme", "basil", "tea", "coffee", "yerba", "rooibos", "fern", "kelp", "moss") && !path.endsWith("_log")
				&& !s.is(Tags.Items.STONES))
			return "herb";
		if (s.is(VEG) || s.is(CROPS) || any(path, "carrot", "potato", "beetroot", "tomato", "cabbage", "onion", "lettuce", "pumpkin", "garlic", "bean", "pea", "squash",
				"eggplant", "cucumber", "radish", "turnip", "leek", "celery", "spinach", "tofu", "salad"))
			return "veg";
		if (s.is(SEEDS)) return null;
		if (any(path, "nut", "nuts", "nutty") || path.equals("raisins")) return path.equals("raisins") ? "fruit" : "nut";
		if (any(path, "bone", "broth")) return "bone";
		// a dish named for a raw thing ("pecan_pie", "kiwi_sorbet", "steamed_broccoli")
		for (String t : path.split("_")) {
			String k = RAW.get(t);
			if (k != null) return k;
		}
		return null;
	}

	/**
	 * What these items make, if anything: a good whose needs they fill exactly (one item each, none left over), or null. Only goods of
	 * the bench's kind. close says how near the nearest miss came (one swap or one more), for Keen Palate.
	 */
	public static Good match(Kind kind, List<String> kinds) {
		for (Good g : GOODS.values()) {
			if (g.kind() != kind || g.needs().size() != kinds.size()) continue;
			List<String> left = new ArrayList<>(g.needs());
			boolean ok = true;
			for (String k : kinds) if (!left.remove(k)) ok = false;
			if (ok) return g;
		}
		return null;
	}

	/** How many things off from the nearest good: 0 a match, 1 one thing away (one wrong, one missing or one too many). */
	public static int off(Kind kind, List<String> kinds) {
		int best = 99;
		for (Good g : GOODS.values()) {
			if (g.kind() != kind) continue;
			List<String> left = new ArrayList<>(g.needs());
			int extra = 0;
			for (String k : kinds) if (!left.remove(k)) extra++;
			best = Math.min(best, Math.max(extra, left.size()));
		}
		return best;
	}

	// ---------------------------------------------------------------- benches

	public static final int SLOTS_IN = 5;

	/** Which bench a block is, by its name (any mod's stove, keg or alembic counts), or null. */
	public static Kind benchOf(BlockState st) {
		String path = BuiltInRegistries.BLOCK.getKey(st.getBlock()).getPath();
		if (any(path, "brewing_stand", "cauldron", "alembic", "alchemy", "mortar", "apothecary")) return Kind.ELIXIR;
		if (any(path, "stove", "cooking_pot", "skillet", "campfire", "smoker", "oven", "grill", "kitchen", "cooking", "roaster", "cook_")) return Kind.MEAL;
		if (any(path, "brew", "keg", "barrel", "ferment", "cask", "vat", "kettle", "distill", "wine_", "tea_")) return Kind.BREW;
		return null;
	}

	private static final DeferredRegister<MenuType<?>> MENUS = DeferredRegister.create(Registries.MENU, Ashbound.ID);
	public static final Supplier<MenuType<Bench>> BENCH = MENUS.register("trade_bench",
			() -> IMenuTypeExtension.create((id, inv, buf) -> {
				Bench b = new Bench(id, inv, Kind.values()[buf.readVarInt()]);
				b.tier = buf.readVarInt();
				if (buf.readBoolean()) b.pos = buf.readBlockPos();
				return b;
			}));

	/** Where the bench's five slots sit (centred under the pot, client/BenchScreen), and the pack under the three columns. */
	public static final int IN_X = 163, IN_Y = 121, PACK_X = 134, PACK_Y = 206;

	public static final class Bench extends AbstractContainerMenu {
		public final Kind kind;
		public final SimpleContainer in = new SimpleContainer(SLOTS_IN);
		/** what made it: 0 any mod's stove, keg or stand (up to Rare), 1 our own station (up to Epic), 2 the house's (no cap, best of two rolls) */
		public int tier;
		/** the station it's open at: what it makes goes on that fire (Kitchen); null, it comes at once */
		public BlockPos pos;

		public Bench(int id, Inventory inv, Kind kind) {
			super(BENCH.get(), id);
			this.kind = kind;
			for (int i = 0; i < SLOTS_IN; i++) addSlot(new Slot(in, i, IN_X + i * 22, IN_Y) {
				@Override
				public boolean mayPlace(ItemStack s) {
					return kindOf(s) != null;
				}
			});
			for (int r = 0; r < 3; r++)
				for (int col = 0; col < 9; col++) addSlot(new Slot(inv, 9 + r * 9 + col, PACK_X + col * 18, PACK_Y + r * 18));
			for (int col = 0; col < 9; col++) addSlot(new Slot(inv, col, PACK_X + col * 18, PACK_Y + 58));
		}

		@Override
		public boolean stillValid(Player p) {
			return p.isAlive();
		}

		@Override
		public ItemStack quickMoveStack(Player p, int i) {
			Slot s = slots.get(i);
			if (!s.hasItem()) return ItemStack.EMPTY;
			ItemStack it = s.getItem(), was = it.copy();
			if (i < SLOTS_IN) {
				if (!moveItemStackTo(it, SLOTS_IN, slots.size(), true)) return ItemStack.EMPTY;
			} else {
				if (kindOf(it) == null) return ItemStack.EMPTY;
				// one item into the first empty slot: a recipe is counted in items, not stacks
				boolean moved = false;
				for (int j = 0; j < SLOTS_IN && !moved; j++)
					if (!slots.get(j).hasItem()) {
						slots.get(j).set(it.split(1));
						moved = true;
					}
				if (!moved) return ItemStack.EMPTY;
			}
			s.setChanged();
			return it.isEmpty() || it.getCount() != was.getCount() ? ItemStack.EMPTY : was;
		}

		@Override
		public void removed(Player p) {
			super.removed(p);
			if (p instanceof ServerPlayer) clearContainer(p, in);
		}

		List<String> kinds() {
			List<String> out = new ArrayList<>();
			for (int i = 0; i < SLOTS_IN; i++) {
				ItemStack s = in.getItem(i);
				if (!s.isEmpty()) out.add(kindOf(s));
			}
			return out;
		}
	}

	static void open(ServerPlayer p, Kind k) {
		open(p, k, 0);
	}

	/** tier: 0 any mod's stove, keg or stand (up to Rare), 1 our own station (up to Epic), 2 the house's (no cap, best of two) */
	static void open(ServerPlayer p, Kind k, int tier) {
		open(p, k, tier, null);
	}

	/** pos: the station's block; what's made there cooks on it for a while (Kitchen). */
	static void open(ServerPlayer p, Kind k, int tier, BlockPos pos) {
		Trade t = trade(k.trade);
		BlockPos at = pos == null ? null : pos.immutable();
		p.openMenu(new SimpleMenuProvider((id, inv, pl) -> {
			Bench b = new Bench(id, inv, k);
			b.tier = tier;
			b.pos = at;
			return b;
		}, Component.literal(t.bench())), buf -> {
			buf.writeVarInt(k.ordinal());
			buf.writeVarInt(tier);
			buf.writeBoolean(at != null);
			if (at != null) buf.writeBlockPos(at);
		});
		sync(p);
		Kitchen.send(p);
	}

	public static final int CRAFT = 0, TAKE_PERK = 1, RESET = 2, FILL = 3, TAKE_READY = 4;

	static void act(ServerPlayer p, Net.TradeAct m) {
		switch (m.what()) {
			case CRAFT -> {
				// at our own stations (tier 1+), a batch: craft, put the same recipe in again from the pack, until it runs out
				int n = 1;
				try {
					if (!m.arg().isEmpty()) n = Math.max(1, Math.min(64, Integer.parseInt(m.arg())));
				} catch (NumberFormatException ignored) {}
				if (!(p.containerMenu instanceof Bench b)) return;
				if (b.tier < 1) n = 1;
				Good g = match(b.kind, b.kinds());
				int made = 0;
				for (int i = 0; i < n; i++) {
					if (i > 0 && (g == null || !knows(p, g.id()) || !fill(p, g.id(), true))) break;
					if (!craft(p)) break;
					made++;
				}
				if (n > 1 && g != null && made > 0)
					p.displayClientMessage(Component.literal((b.pos != null ? "On the fire: " : "Made ") + g.name() + " x" + made).withStyle(ChatFormatting.GOLD), false);
				Kitchen.send(p);
			}
			case TAKE_PERK -> {
				Perk pk = PERKS.get(m.arg());
				if (pk == null) return;
				String no = why(p, pk);
				if (no != null) {
					p.displayClientMessage(Component.literal(no).withStyle(ChatFormatting.RED), true);
					return;
				}
				put(p, "perk." + pk.id(), "1");
				p.playNotifySound(SoundEvents.ENCHANTMENT_TABLE_USE, SoundSource.PLAYERS, 0.6f, 1.2f);
				sync(p);
			}
			case RESET -> {
				if (spent(p) == 0) return;
				if (!Coins.pay(p, RESET_COINS)) {
					p.displayClientMessage(Component.literal("Forgetting your perks costs " + RESET_COINS + " coins").withStyle(ChatFormatting.RED), true);
					return;
				}
				Map<String, String> s = new HashMap<>(p.getData(STATE));
				s.keySet().removeIf(k -> k.startsWith("perk."));
				p.setData(STATE, s);
				p.displayClientMessage(Component.literal("Your trade points are yours to spend again").withStyle(ChatFormatting.GOLD), true);
				sync(p);
			}
			case FILL -> fill(p, m.arg());
			case TAKE_READY -> Kitchen.collect(p);
			default -> {}
		}
	}

	/** The book's "make again": back to your pack with what's in the slots, then one of each thing the recipe needs from it. */
	private static void fill(ServerPlayer p, String goodId) {
		fill(p, goodId, false);
	}

	/** Puts a known recipe's things in the slots from your pack; whether they're all there (quiet: no "Missing" line). */
	private static boolean fill(ServerPlayer p, String goodId, boolean quiet) {
		if (!(p.containerMenu instanceof Bench b)) return false;
		Good g = GOODS.get(goodId);
		if (g == null || g.kind() != b.kind || !knows(p, goodId)) return false;
		for (int i = 0; i < SLOTS_IN; i++) {
			ItemStack s = b.in.removeItemNoUpdate(i);
			if (!s.isEmpty() && !p.getInventory().add(s)) p.drop(s, false);
		}
		var items = p.getInventory().items;
		int slot = 0;
		List<String> missing = new ArrayList<>();
		for (String need : g.needs()) {
			boolean found = false;
			for (ItemStack s : items)
				if (need.equals(kindOf(s))) {
					b.in.setItem(slot++, s.split(1));
					found = true;
					break;
				}
			if (!found) missing.add(KIND_NAMES.get(need));
		}
		b.broadcastChanges();
		if (!missing.isEmpty() && !quiet) p.displayClientMessage(Component.literal("Missing: " + String.join(", ", missing)).withStyle(ChatFormatting.RED), true);
		return missing.isEmpty();
	}

	/** Which good an item is (null: not one of ours). */
	public static String goodId(ItemStack s) {
		for (Good g : GOODS.values()) if (ITEMS.containsKey(g.id()) && ITEMS.get(g.id()).get() == s.getItem()) return g.id();
		return null;
	}

	/** Times you've made a good (its mastery: Kitchen.stars). */
	public static int madeCount(Player p, String good) {
		try {
			return Integer.parseInt(state(p).getOrDefault("made." + good, "0"));
		} catch (NumberFormatException e) {
			return 0;
		}
	}

	/** One make from the slots; false when nothing was made (a miss, a full station: a batch stops). */
	private static boolean craft(ServerPlayer p) {
		if (!(p.containerMenu instanceof Bench b)) return false;
		float fresh = fresh(b);
		List<String> kinds = b.kinds();
		if (kinds.isEmpty()) return false;
		if (b.pos != null) {                               // a full station takes nothing more
			Kitchen.Job j = Kitchen.job(p.level(), b.pos);
			if (j != null && j.outs.size() >= Kitchen.MOST) {
				p.displayClientMessage(Component.literal("The fire's full: take what's ready first").withStyle(ChatFormatting.RED), true);
				return false;
			}
		}
		String trade = b.kind.trade;
		int lv = level(p, trade);
		Good g = match(b.kind, kinds);
		boolean ready = g != null && lv >= g.level();
		// the slots are spent, but Leftovers and the like keep some
		double save = perk(p, trade, "save%") / 100;
		for (int i = 0; i < SLOTS_IN; i++) {
			ItemStack s = b.in.getItem(i);
			if (s.isEmpty()) continue;
			if (ready && p.getRandom().nextDouble() < save) continue;
			ItemStack spent = s.getItem() == Items.WATER_BUCKET || s.getItem() == Items.MILK_BUCKET ? new ItemStack(Items.BUCKET) : ItemStack.EMPTY;
			if (s.getItem() == Items.POTION || s.getItem() == Items.HONEY_BOTTLE) spent = new ItemStack(Items.GLASS_BOTTLE);
			s.shrink(1);
			if (!spent.isEmpty() && !p.getInventory().add(spent)) p.drop(spent, false);
		}
		b.broadcastChanges();
		if (g != null && !ready) {
			p.displayClientMessage(Component.literal("It almost came together, but it's beyond your hands yet (" + trade(trade).name() + " " + g.level() + ")")
					.withStyle(ChatFormatting.GRAY), false);
			give(p, new ItemStack(ITEMS.get(MISS.get(b.kind)).get()));
			gain(p, trade, 4);
			return false;
		}
		if (g == null) {
			String hint = perk(p, trade, "hint") > 0 && off(b.kind, kinds) == 1 ? " You can tell it was one thing away from something." : "";
			p.displayClientMessage(Component.literal("That didn't work." + hint).withStyle(ChatFormatting.GRAY), true);
			p.playNotifySound(SoundEvents.FIRE_EXTINGUISH, SoundSource.PLAYERS, 0.5f, 1.2f);
			give(p, new ItemStack(ITEMS.get(MISS.get(b.kind)).get()));
			gain(p, trade, 4);
			return false;
		}
		int times = madeCount(p, g.id());
		int stars = Kitchen.stars(times);
		// four stars: a master's hand, a little more often the better make (two levels of rarity)
		int q = rollRarity(p.getRandom(), rarityLevel(p, b) + (stars >= 4 ? 2 : 0), gateFloor(b), cap(b.tier), rolls(b.tier));
		boolean accident = p.getRandom().nextDouble() < (3 + perk(p, trade, "accident%")) / 100;
		int n = p.getRandom().nextDouble() < perk(p, trade, "double%") / 100 ? 2 : 1;
		ItemStack made = good(g, q + 1, accident, p);
		made.setCount(n);
		boolean found = !knows(p, g.id());
		if (found) put(p, "known." + g.id(), "1");
		Rarity ql = Rarity.values()[q];
		put(p, "made." + g.id(), String.valueOf(times + 1));
		int secs = Kitchen.seconds(g, stars);
		boolean cooks = b.pos != null && Kitchen.add(p, b.pos, b.kind, made, secs);
		p.displayClientMessage(Component.literal(found ? "New recipe! " : "").withStyle(ChatFormatting.GOLD)
				.append(Component.literal(ql.title + " " + g.name() + (n > 1 ? " x2" : "") + (accident ? ", a happy accident" : "")).withStyle(ql.colour))
				.append(Component.literal(cooks ? ", on the fire " + Kitchen.clock(secs) : "").withStyle(ChatFormatting.GRAY)), true);
		if (Kitchen.stars(times + 1) > stars)
			p.displayClientMessage(Component.literal(g.name() + ": mastery " + "\u2605".repeat(stars + 1) + ", it goes quicker now").withStyle(ChatFormatting.GOLD), false);
		p.playNotifySound(found ? SoundEvents.PLAYER_LEVELUP : cooks ? SoundEvents.FIRECHARGE_USE : b.kind == Kind.MEAL ? SoundEvents.GENERIC_EAT : SoundEvents.BREWING_STAND_BREW,
				SoundSource.PLAYERS, cooks ? 0.3f : 0.6f, 1.1f);
		if (!cooks) give(p, made);
		gain(p, trade, 18 + 4 * g.needs().size() + g.level() / 2 + (found ? 60 : 0));
		sync(p);
		return true;
	}

	/** The best Fresh Catch among a cooking bench's fish: what it adds to the meal's roll. */
	public static float fresh(Bench b) {
		float best = 0;
		for (int i = 0; i < SLOTS_IN; i++) best = Math.max(best, tag(b.in.getItem(i)).getFloat("ash_fresh"));
		return b.kind == Kind.MEAL ? best : 0;
	}

	private static void give(ServerPlayer p, ItemStack s) {
		if (!p.getInventory().add(s)) p.drop(s, false);
	}

	/** A good as made: its rarity (1 Common to 5 Legendary), whether it's a happy accident, and who made it. */
	public static ItemStack good(Good g, int quality, boolean accident, ServerPlayer by) {
		ItemStack s = new ItemStack(ITEMS.get(g.id()).get());
		CompoundTag t = new CompoundTag();
		t.putInt("ash_quality", quality);
		if (accident) t.putBoolean("ash_accident", true);
		if (by != null && quality >= 3) t.putString("ash_by", by.getGameProfile().getName());
		s.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
		return s;
	}

	private static CompoundTag tag(ItemStack s) {
		CustomData c = s.get(DataComponents.CUSTOM_DATA);
		return c == null ? new CompoundTag() : c.copyTag();
	}

	public static int quality(ItemStack s) {
		int q = tag(s).getInt("ash_quality");
		return q <= 0 ? 2 : q;
	}

	static Rarity goodRarity(ItemStack s) {
		int q = tag(s).getInt("ash_quality");
		return q >= 1 && q <= 5 ? Rarity.values()[q - 1] : null;
	}

	public static boolean accident(ItemStack s) {
		return tag(s).getBoolean("ash_accident");
	}

	// ---------------------------------------------------------------- the forge's hooks (Smithing calls these)

	/** Which forge trade a piece is: robes and light armour are Tailoring. */
	public static String forgeTrade(Item out) {
		return Smithing.Craft.of(Smithing.kind(out)).cloth ? "tailoring" : "smithing";
	}

	/** What a trade's level and perks add to a forge roll (a new piece, or an upgrade). */
	public static float forgeRoll(ServerPlayer p, Item out, boolean upgrade) {
		String t = forgeTrade(out);
		return level(p, t) * 0.002f + (float) perk(p, t, upgrade ? "upgrade_roll" : "forge_roll");
	}

	/** A forge job's cost with this trade's material perks. */
	public static Gear.Cost forgeCost(ServerPlayer p, Item out, Gear.Cost c) {
		double cut = Math.max(-60, perk(p, forgeTrade(out), "cost%")) / 100;
		return cut == 0 ? c : new Gear.Cost((int) Math.max(1, Math.round(c.common() * (1 + cut))), c.elite(), c.trophy());
	}

	public static boolean embersKept(ServerPlayer p, Item out) {
		return p.getRandom().nextDouble() < perk(p, forgeTrade(out), "ember_save%") / 100;
	}

	public static boolean forgeTwice(ServerPlayer p, Item out) {
		return p.getRandom().nextDouble() < perk(p, forgeTrade(out), "double%") / 100;
	}

	public static void forged(ServerPlayer p, Item out, boolean upgrade, char rank) {
		int r = Math.max(0, "FEDCBAS".indexOf(rank));
		gain(p, forgeTrade(out), (upgrade ? 30 : 45) + r * 8);
	}

	// ---------------------------------------------------------------- gathering

	private static void drops(BlockDropsEvent e) {
		if (!(e.getBreaker() instanceof ServerPlayer p) || p.isCreative()) return;
		BlockState st = e.getState();
		ServerLevel level = e.getLevel();
		var rnd = p.getRandom();
		if (st.is(Tags.Blocks.ORES)) {
			gain(p, "mining", 10);
			if (rnd.nextDouble() < perk(p, "mining", "ore_double%") / 100) twice(e);
		} else if (st.is(Tags.Blocks.STONES) || st.is(net.minecraft.tags.BlockTags.BASE_STONE_OVERWORLD)) {
			if (rnd.nextInt(8) == 0) gain(p, "mining", 1);
			double gem = perk(p, "mining", "gem%");
			if (gem > 0 && rnd.nextDouble() * 100 < gem) {
				Item[] gems = {Items.LAPIS_LAZULI, Items.AMETHYST_SHARD, Items.EMERALD, Items.LAPIS_LAZULI, Items.DIAMOND};
				e.getDrops().add(new ItemEntity(level, e.getPos().getX() + 0.5, e.getPos().getY() + 0.5, e.getPos().getZ() + 0.5, new ItemStack(gems[rnd.nextInt(gems.length)])));
			}
		} else if (st.getBlock() instanceof CropBlock crop && crop.isMaxAge(st)) {
			gain(p, "farming", 4);
			if (rnd.nextDouble() < perk(p, "farming", "crop_double%") / 100) twice(e);
			if (rnd.nextDouble() * 100 < perk(p, "farming", "golden%"))
				e.getDrops().add(new ItemEntity(level, e.getPos().getX() + 0.5, e.getPos().getY() + 0.5, e.getPos().getZ() + 0.5, new ItemStack(Items.GOLDEN_CARROT)));
			if (perk(p, "farming", "replant") > 0) replant(level, e.getPos(), crop, e);
		} else if (st.is(net.minecraft.tags.BlockTags.FLOWERS) || st.is(net.minecraft.tags.BlockTags.SWORD_EFFICIENT) && kindOf(firstDrop(e)) != null) {
			if (rnd.nextInt(3) == 0) gain(p, "farming", 1);
			if (rnd.nextDouble() < perk(p, "farming", "herb_double%") / 100) twice(e);
		}
	}

	private static ItemStack firstDrop(BlockDropsEvent e) {
		return e.getDrops().isEmpty() ? ItemStack.EMPTY : e.getDrops().get(0).getItem();
	}

	private static void twice(BlockDropsEvent e) {
		List<ItemEntity> more = new ArrayList<>();
		for (ItemEntity d : e.getDrops()) {
			if (d.getItem().getItem() instanceof net.minecraft.world.item.BlockItem bi && bi.getBlock() == e.getState().getBlock()) continue;
			more.add(new ItemEntity(e.getLevel(), d.getX(), d.getY(), d.getZ(), d.getItem().copy()));
		}
		e.getDrops().addAll(more);
	}

	/** Replant: one seed out of the drops back into the ground, once the block's gone. */
	private static void replant(ServerLevel level, BlockPos pos, CropBlock crop, BlockDropsEvent e) {
		ItemStack seed = new ItemStack(crop.getCloneItemStack(level, pos, e.getState()).getItem());
		for (ItemEntity d : e.getDrops())
			if (d.getItem().is(seed.getItem())) {
				d.getItem().shrink(1);
				level.getServer().execute(() -> {
					if (level.getBlockState(pos).isAir() && crop.defaultBlockState().canSurvive(level, pos)) level.setBlockAndUpdate(pos, crop.getStateForAge(0));
				});
				return;
			}
	}

	private static void fished(ItemFishedEvent e) {
		if (!(e.getEntity() instanceof ServerPlayer p)) return;
		var rnd = p.getRandom();
		gain(p, "fishing", 25);
		double twice = perk(p, "fishing", "fish_double%") + (p.getVehicle() instanceof net.minecraft.world.entity.vehicle.Boat ? perk(p, "fishing", "boat_double%") : 0);
		if (rnd.nextDouble() < twice / 100)
			for (ItemStack s : List.copyOf(e.getDrops())) give(p, s.copy());
		if (rnd.nextDouble() < perk(p, "fishing", "treasure%") / 100) {
			LootTable t = p.server.reloadableRegistries().getLootTable(BuiltInLootTables.FISHING_TREASURE);
			LootParams lp = new LootParams.Builder(p.serverLevel()).withParameter(LootContextParams.ORIGIN, p.position()).withParameter(LootContextParams.TOOL, p.getMainHandItem())
					.withParameter(LootContextParams.THIS_ENTITY, e.getHookEntity()).withLuck(p.getLuck()).create(LootContextParamSets.FISHING);
			for (ItemStack s : t.getRandomItems(lp)) give(p, s);
			p.displayClientMessage(Component.literal("Something else came up with it").withStyle(ChatFormatting.AQUA), true);
		}
		if (rnd.nextDouble() < perk(p, "fishing", "coins%") / 100) Coins.give(p, 3 + rnd.nextInt(10));
		// Fresh Catch: the fish carries how much better it makes a meal, whoever cooks it
		double fresh = perk(p, "fishing", "fresh");
		if (fresh > 0)
			for (ItemStack s : e.getDrops())
				if ("fish".equals(kindOf(s))) {
					CompoundTag t = tag(s);
					t.putFloat("ash_fresh", (float) fresh);
					s.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
				}
	}

	/** Quick Bite: a hook cast by an angler with it is lured sooner (the hook's lure is in ticks; a level of the Lure enchantment is 100). */
	private static void cast(net.neoforged.neoforge.event.entity.EntityJoinLevelEvent e) {
		if (e.getLevel().isClientSide() || !(e.getEntity() instanceof net.minecraft.world.entity.projectile.FishingHook hook) || !(hook.getPlayerOwner() instanceof ServerPlayer p)) return;
		int more = (int) perk(p, "fishing", "lure");
		if (more <= 0) return;
		try {
			if (lure == null) {
				lure = net.minecraft.world.entity.projectile.FishingHook.class.getDeclaredField("lureSpeed");
				lure.setAccessible(true);
			}
			lure.setInt(hook, lure.getInt(hook) + more);
		} catch (ReflectiveOperationException ex) {
			Ashbound.LOG.warn("Quick Bite can't reach the hook's lure: {}", ex.toString());
		}
	}

	private static java.lang.reflect.Field lure;

	private static void born(BabyEntitySpawnEvent e) {
		if (!(e.getCausedByPlayer() instanceof ServerPlayer p) || !(e.getChild() instanceof AgeableMob child)) return;
		gain(p, "farming", 8);
		if (p.getRandom().nextDouble() < perk(p, "farming", "twin%") / 100 && e.getParentA() instanceof Animal a && a.level() instanceof ServerLevel sl) {
			AgeableMob twin = a.getBreedOffspring(sl, e.getParentB() instanceof AgeableMob b ? b : a);
			if (twin != null) {
				twin.setBaby(true);
				twin.moveTo(a.getX(), a.getY(), a.getZ(), 0, 0);
				sl.addFreshEntity(twin);
			}
		}
	}

	private static void killed(LivingDropsEvent e) {
		if (!(e.getSource().getEntity() instanceof ServerPlayer p) || !(e.getEntity() instanceof Animal)) return;
		if (p.getRandom().nextDouble() >= perk(p, "farming", "meat_double%") / 100) return;
		List<ItemEntity> more = new ArrayList<>();
		for (ItemEntity d : e.getDrops())
			if ("meat".equals(kindOf(d.getItem()))) more.add(new ItemEntity(d.level(), d.getX(), d.getY(), d.getZ(), d.getItem().copy()));
		e.getDrops().addAll(more);
	}

	/** Last Breath: with an elixir on you, death waits once in ten minutes. */
	private static void dying(LivingDeathEvent e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || perk(p, "alchemy", "last_breath") <= 0) return;
		long now = p.level().getGameTime();
		boolean on = false;
		for (String s : ELIXIR_SLOTS) {
			Buff b = buff(p, s);
			on |= b != null && b.end() > now;
		}
		long last = Long.parseLong(p.getData(STATE).getOrDefault("breath", "-99999"));
		if (!on || now - last < 12000) return;
		e.setCanceled(true);
		p.setHealth(1);
		put(p, "breath", Long.toString(now));
		p.displayClientMessage(Component.literal("Last Breath").withStyle(ChatFormatting.LIGHT_PURPLE), true);
		p.level().playSound(null, p.blockPosition(), SoundEvents.TOTEM_USE, SoundSource.PLAYERS, 0.6f, 1.4f);
	}

	private static void tick(ServerPlayer p) {
		if (p.tickCount % 100 == 0 && perk(p, "farming", "growth") > 0) {
			// Green Thumb: a ripening crop near you gets a growth tick, two with Harvest Moon
			ServerLevel l = p.serverLevel();
			int tries = (int) perk(p, "farming", "growth") * 6;
			for (int i = 0; i < tries; i++) {
				BlockPos at = p.blockPosition().offset(p.getRandom().nextInt(13) - 6, p.getRandom().nextInt(5) - 2, p.getRandom().nextInt(13) - 6);
				BlockState st = l.getBlockState(at);
				if (st.getBlock() instanceof CropBlock crop && !crop.isMaxAge(st)) st.randomTick(l, at, l.random);
			}
		}
		if (p.tickCount % 20 == 0) {
			if (perk(p, "mining", "no_fatigue") > 0) p.removeEffect(MobEffects.DIG_SLOWDOWN);
			if (perk(p, "mining", "dark_eye") > 0 && p.getY() < 40 && !p.level().canSeeSky(p.blockPosition())) {
				MobEffectInstance nv = p.getEffect(MobEffects.NIGHT_VISION);
				if (nv == null || nv.getDuration() < 260) p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 400, 0, true, false, false));
			}
			if (DIRTY.contains(p.getUUID())) sync(p);
		}
		if (p.tickCount % 40 == 0 && toxicity(p) > toxLimit(p)) {
			p.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 60, 0, false, false, true));
			if (p.getHealth() > 1) p.setHealth(Math.max(1, p.getHealth() - p.getMaxHealth() * 0.02f));
		}
		if (p.isSprinting() && tipsy(p) > 1) p.setSprinting(false);
	}

	/** Sneak and use an empty hand on a stove, a keg or a brewing stand: that trade's bench. */
	private static void use(PlayerInteractEvent.RightClickBlock e) {
		if (!e.getEntity().isShiftKeyDown() || e.getHand() != InteractionHand.MAIN_HAND || !e.getEntity().getMainHandItem().isEmpty()) return;
		BlockState st = e.getLevel().getBlockState(e.getPos());
		if (st.getBlock() instanceof Stations.Station) return;   // our own: it opens itself, at its own tier
		Kind k = benchOf(st);
		if (k == null) return;
		e.setCanceled(true);
		e.setCancellationResult(InteractionResult.SUCCESS);
		if (e.getEntity() instanceof ServerPlayer p) open(p, k, 0, e.getPos());
	}

	/** Cooking with the mods' own pots and ovens, or the crafting grid, still counts a little. */
	private static void made(PlayerEvent.ItemCraftedEvent e) {
		if (e.getEntity() instanceof ServerPlayer p && e.getCrafting().has(DataComponents.FOOD) && !(e.getCrafting().getItem() instanceof GoodItem))
			gain(p, "cooking", 3);
	}

	private static void smelted(PlayerEvent.ItemSmeltedEvent e) {
		if (e.getEntity() instanceof ServerPlayer p && e.getSmelting().has(DataComponents.FOOD)) gain(p, "cooking", 2 * e.getSmelting().getCount());
	}

	private static void commands(RegisterCommandsEvent e) {
		e.getDispatcher().register(Commands.literal("ashbound").requires(s -> s.hasPermission(2)).then(Commands.literal("trade")
				.then(Commands.literal("reset").then(Commands.argument("player", EntityArgument.player()).executes(c -> {
					ServerPlayer p = EntityArgument.getPlayer(c, "player");
					p.setData(STATE, new HashMap<>());
					sync(p);
					return 1;
				})))
				.then(Commands.literal("xp").then(Commands.argument("player", EntityArgument.player()).then(Commands.argument("trade", StringArgumentType.word())
						.suggests((c, b) -> net.minecraft.commands.SharedSuggestionProvider.suggest(ALL.stream().map(Trade::id), b))
						.then(Commands.argument("amount", IntegerArgumentType.integer(1)).executes(c -> {
							ServerPlayer p = EntityArgument.getPlayer(c, "player");
							String t = StringArgumentType.getString(c, "trade");
							if (trade(t) == null) return 0;
							gain(p, t, IntegerArgumentType.getInteger(c, "amount"));
							sync(p);
							return 1;
						})))))
				.then(Commands.literal("learnall").then(Commands.argument("player", EntityArgument.player()).executes(c -> {
					ServerPlayer p = EntityArgument.getPlayer(c, "player");
					for (String g : GOODS.keySet()) put(p, "known." + g, "1");
					sync(p);
					return 1;
				})))));
	}

	public static void register(IEventBus bus) {
		MENUS.register(bus);
		NeoForge.EVENT_BUS.addListener(Trades::drops);
		NeoForge.EVENT_BUS.addListener(Trades::fished);
		NeoForge.EVENT_BUS.addListener(Trades::cast);
		NeoForge.EVENT_BUS.addListener(Trades::born);
		NeoForge.EVENT_BUS.addListener(Trades::killed);
		NeoForge.EVENT_BUS.addListener(Trades::dying);
		NeoForge.EVENT_BUS.addListener(Trades::use);
		NeoForge.EVENT_BUS.addListener(Trades::made);
		NeoForge.EVENT_BUS.addListener(Trades::smelted);
		NeoForge.EVENT_BUS.addListener(Trades::commands);
		NeoForge.EVENT_BUS.addListener(Trades::snacked);
		NeoForge.EVENT_BUS.addListener(Trades::snackTooltip);
		Recipes.register();
		NeoForge.EVENT_BUS.addListener((PlayerTickEvent.Post e) -> {
			if (e.getEntity() instanceof ServerPlayer p) tick(p);
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedInEvent e) -> {
			if (!(e.getEntity() instanceof ServerPlayer p)) return;
			sync(p);
			if (!Coins.flag(p, "trades_told")) {
				Coins.setFlag(p, "trades_told");
				p.sendSystemMessage(Component.literal("Trades: sneak and use an empty hand on a stove, campfire or smoker to cook, on a keg or barrel to brew, "
						+ "on a brewing stand or cauldron for alchemy. Put things in and see what comes out. Your levels and perks are on the Trades tab.")
						.withStyle(ChatFormatting.GOLD));
			}
		});
	}
}
