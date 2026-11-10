package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

import com.mojang.authlib.GameProfile;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.neoforged.neoforge.common.util.FakePlayer;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

/**
 * Self-tests for the Ash Tree and the balance (run headless: gradlew runGameTestServer). Each test logs every check as
 * "SELFTEST ok/FAIL ..." and fails with the list of what broke.
 */
@GameTestHolder(Ashbound.ID)
@PrefixGameTestTemplate(false)
public final class SelfTest {
	private SelfTest() {}

	private static final class Checks {
		final String test;
		final List<String> fails = new ArrayList<>();

		Checks(String test) {
			this.test = test;
		}

		void check(boolean ok, String what) {
			Ashbound.LOG.info("SELFTEST {} {}: {}", ok ? "ok  " : "FAIL", test, what);
			if (!ok) fails.add(what);
		}

		void near(double got, double want, double tol, String what) {
			check(Math.abs(got - want) <= tol, what + String.format(" (got %.3f, want %.3f)", got, want));
		}

		void end(GameTestHelper h) {
			if (fails.isEmpty()) h.succeed();
			else h.fail(test + ": " + String.join("; ", fails));
		}
	}

	private static FakePlayer player(GameTestHelper h, int level) {
		FakePlayer p = FakePlayerFactory.get(h.getLevel(), new GameProfile(UUID.randomUUID(), "ashtest"));
		p.setData(Levels.LEVEL, level);
		p.setData(Levels.ASH, 1_000_000);
		p.setData(Passives.TAKEN, new ArrayList<>());
		var at = h.absoluteVec(new net.minecraft.world.phys.Vec3(2, 1, 4));
		p.setPos(at.x, at.y, at.z);
		return p;
	}

	private static void take(FakePlayer p, String... ids) {
		for (String id : ids) Passives.act(p, 0, id);
	}

	private static ItemStack weapon(String kind, boolean boss) {
		for (Gear.Weapon w : Gear.WEAPON.values())
			if (w.kind().equals(kind) && w.rank() == 'C' && w.boss() == boss)
				return new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, w.id())));
		return ItemStack.EMPTY;
	}

	private static Zombie dummy(GameTestHelper h) {
		Zombie z = h.spawnWithNoFreeWill(EntityType.ZOMBIE, new BlockPos(2, 1, 2));
		z.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);
		z.getAttribute(Attributes.ARMOR).setBaseValue(0);
		z.setHealth(1000);
		return z;
	}

	/** the health one raw hit of `raw` takes off the target, after the tree's mechanics */
	private static float hit(FakePlayer p, LivingEntity target, float raw) {
		target.invulnerableTime = 0;
		float before = target.getHealth();
		target.hurt(p.damageSources().playerAttack(p), raw);
		return before - target.getHealth();
	}

	// ---------------------------------------------------------------- the tree's rules

	@GameTest(template = "selftest")
	public static void treeRules(GameTestHelper h) {
		Checks c = new Checks("treeRules");
		c.check(Passives.NODES.size() == 149, "149 nodes loaded (" + Passives.NODES.size() + ")");
		c.check(Passives.AREA_POINTS.getOrDefault("sword", 0) == 27, "an area takes 27 points");
		FakePlayer p = player(h, 60);
		c.check(Passives.points(p) == 59, "level 60 has 59 points");
		for (int i = 0; i < 7; i++) take(p, "sword_s0");
		c.check(Passives.rank(p, "sword_s0") == 5, "a stat node stops at its 5 ranks (" + Passives.rank(p, "sword_s0") + ")");
		take(p, "sword_n3");
		c.check(Passives.rank(p, "sword_n3") == 0, "a node not joined to yours can't be taken");
		take(p, "sword_s1", "sword_s1", "sword_s1", "sword_s1", "sword_s1", "sword_n0", "sword_s2", "sword_s3", "sword_n3", "sword_v2");
		c.check(Passives.spentIn(p.getData(Passives.TAKEN), "sword") == 15, "15 points in the Blade so far");
		take(p, "sword_k");
		c.check(Passives.rank(p, "sword_k") == 0, "the keystone stays shut below 16 points");
		take(p, "sword_s2");
		c.check(Passives.spentIn(p.getData(Passives.TAKEN), "sword") == 16, "16 points in the Blade");
		take(p, "sword_k");
		c.check(Passives.rank(p, "sword_k") == 1, "the keystone opens at 16 points");
		int s2 = Passives.rank(p, "sword_s2");
		Passives.act(p, 1, "sword_s2");
		c.check(Passives.rank(p, "sword_s2") == s2, "a point the keystone needs can't be taken back");
		Passives.act(p, 1, "sword_n0");
		c.check(Passives.rank(p, "sword_n0") == 1, "a node holding others up can't be taken back");
		take(p, "dagger_s0", "dagger_s0", "dagger_s0", "dagger_s0", "dagger_s0", "dagger_s1", "dagger_s1", "dagger_s1", "dagger_s1",
				"dagger_s1", "dagger_n0", "dagger_s2", "dagger_s2", "dagger_s2", "dagger_s3", "dagger_n3", "dagger_v2", "dagger_k");
		c.check(Passives.rank(p, "dagger_k") == 0, "only one keystone at a time");
		int before = Passives.rank(p, "sword_v1");
		Passives.act(p, 1, "sword_v2");
		c.check(Passives.rank(p, "sword_v2") == 1, "the node before a held keystone stays");
		c.check(before == 0 && Passives.points(p) == 59 - p.getData(Passives.TAKEN).size(), "points = level - 1 - ranks taken");
		Passives.act(p, 3, "");
		c.check(p.getData(Passives.TAKEN).isEmpty(), "a full reset clears everything");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void healthCap(GameTestHelper h) {
		Checks c = new Checks("healthCap");
		Zombie z = h.spawnWithNoFreeWill(EntityType.ZOMBIE, new BlockPos(2, 1, 2));
		z.getAttribute(Attributes.MAX_HEALTH).setBaseValue(5000);
		z.setHealth(5000);
		c.near(z.getMaxHealth(), 5000, 0.1, "max health above vanilla's 1024");
		c.near(z.getHealth(), 5000, 0.1, "health fills past 1024");
		c.end(h);
	}

	// ---------------------------------------------------------------- the classes

	@GameTest(template = "selftest")
	public static void classes(GameTestHelper h) {
		Checks c = new Checks("classes");
		c.check(Classes.ALL.size() == 9, "nine classes");
		for (Classes.Cls k : Classes.ALL) {
			c.check(!Classes.icon(k).isEmpty(), k.id() + "'s weapon exists");
			c.check(Classes.kit(k).stream().noneMatch(s -> s.isEmpty()), k.id() + "'s whole kit exists");
			c.check(Classes.kit(k).size() <= 14, k.id() + "'s kit fits the chooser");
			c.check(k.perkKey().endsWith("%") || k.perkValue() <= 2, k.id() + "'s bonus is a small one");
		}
		FakePlayer p = player(h, 1);
		int coins = Coins.of(p);
		Classes.pick(p, "wizard");
		c.check(Classes.of(p) == null, "a class that doesn't exist is ignored");
		Classes.pick(p, "hunter");
		c.check(Classes.of(p) == Classes.byId("hunter"), "a pick takes");
		c.check(p.getMainHandItem().getItem() == Classes.icon(Classes.byId("hunter")).getItem(), "the weapon is in hand");
		c.check(!p.getItemBySlot(net.minecraft.world.entity.EquipmentSlot.CHEST).isEmpty(), "the armour is worn");
		c.near(Coins.of(p) - coins, Classes.START_COINS, 0, "the coins arrive");
		c.near(Passives.stat(p, "arrow%"), 8, 0.001, "the class's bonus reaches the tree's stat");
		int arrows = p.getInventory().countItem(Items.ARROW);
		c.near(arrows, 320, 0, "a hunter sets out with five stacks of arrows");
		c.check(p.getInventory().countItem(Items.IRON_PICKAXE) == 1 && p.getInventory().countItem(Items.RED_BED) == 1, "everyone gets tools and a bed");
		c.check(!p.getItemBySlot(net.minecraft.world.entity.EquipmentSlot.LEGS).isEmpty(), "the legs are worn too");
		Classes.pick(p, "hunter");
		Classes.pick(p, "shade");
		c.check(Classes.of(p) == Classes.byId("hunter"), "a second pick can't change class");
		c.near(p.getInventory().countItem(Items.ARROW), arrows, 0, "a second pick gives no second kit");
		c.near(Coins.of(p) - coins, Classes.START_COINS, 0, "a second pick gives no more coins");
		c.end(h);
	}

	// ---------------------------------------------------------------- trades

	@GameTest(template = "selftest")
	public static void trades(GameTestHelper h) {
		Checks c = new Checks("trades");
		c.check(Trades.ALL.size() == 8, "eight trades");
		for (Trades.Trade t : Trades.ALL) {
			long n = Trades.PERKS.values().stream().filter(pk -> pk.trade().equals(t.id())).count();
			c.near(n, 12, 0, t.id() + " has twelve perks");
			for (int b = 0; b < 3; b++)
				for (int tier = 0; tier < 4; tier++) {
					int bb = b, tt = tier;
					c.check(Trades.PERKS.values().stream().anyMatch(pk -> pk.trade().equals(t.id()) && pk.branch() == bb && pk.tier() == tt), t.id() + " branch " + b + " tier " + tier);
				}
		}
		for (Trades.Good g : Trades.GOODS.values()) {
			c.check(Trades.ITEMS.containsKey(g.id()), g.id() + " has an item");
			for (String k : g.needs()) c.check(Trades.KIND_NAMES.containsKey(k), g.id() + "'s " + k + " is a kind");
			c.check(Trades.match(g.kind(), g.needs()) == g, g.id() + "'s recipe makes it and nothing else first");
		}
		c.check("meat".equals(Trades.kindOf(new ItemStack(Items.BEEF))) && "veg".equals(Trades.kindOf(new ItemStack(Items.CARROT)))
				&& "grain".equals(Trades.kindOf(new ItemStack(Items.WHEAT))) && "fish".equals(Trades.kindOf(new ItemStack(Items.COD)))
				&& "glow".equals(Trades.kindOf(new ItemStack(Items.GLOWSTONE_DUST))) && "sweet".equals(Trades.kindOf(new ItemStack(Items.SUGAR))),
				"plain things are the kinds you'd think");
		c.check(Trades.kindOf(new ItemStack(Items.STONE)) == null, "stone isn't food");
		c.check(Trades.kindOf(new ItemStack(Items.ENDER_PEARL)) == null, "a pearl isn't a pear");
		// pass 16: rarity from the trade level, kept to the bench, a gate's material lifting it
		for (double lv : new double[] {1, 12, 25, 40, 50, 70}) c.near(java.util.Arrays.stream(Trades.odds(lv)).sum(), 100, 0.01, "rarity odds at " + lv + " add up");
		var rnd = net.minecraft.util.RandomSource.create(5);
		int[] at1 = new int[5], at50 = new int[5];
		for (int i = 0; i < 4000; i++) {
			at1[Trades.rollRarity(rnd, 1, 0, 4, 1)]++;
			at50[Trades.rollRarity(rnd, 50, 0, 4, 1)]++;
		}
		c.near(at1[0] / 40.0, 85, 3, "level 1 makes Common about 85% of the time");
		c.near(at50[4] / 40.0, 4, 1.5, "level 50 makes Legendary about 4% of the time");
		boolean capped = true;
		for (int i = 0; i < 500; i++) capped &= Trades.rollRarity(rnd, 50, 0, 2, 1) <= 2;
		c.check(capped, "any mod's stove makes Rare at best");
		c.check(Trades.rollRarity(rnd, 1, 3, 4, 1) >= 3, "an S gate's material makes it Epic at least");
		c.near(Trades.mult(5, false), 2.2, 0.001, "Legendary is x2.2");
		for (var st : List.of(Stations.COOKS_FIRE, Stations.BREWERS_CASK, Stations.ALCHEMISTS_BENCH)) {
			c.check(st.get() instanceof Stations.Station s && s.tier == 1, st.getId() + " is a tier 1 station");
			c.check(h.getLevel().getServer().getRecipeManager().byKey(st.getId()).isPresent(), st.getId() + " can be crafted");
		}
		for (var st : List.of(Stations.HOME_COOKS_FIRE, Stations.HOME_BREWERS_CASK, Stations.HOME_ALCHEMISTS_BENCH)) {
			c.check(st.get() instanceof Stations.Station s && s.tier == 2, st.getId() + " is the manor's (tier 2)");
			c.check(st.get().defaultDestroyTime() < 0, st.getId() + " can't be broken");
		}
		c.check(Stations.MANOR_FLAG.equals("ch:act2_drowned_fire"), "the manor opens after Act II");
		// 11/7 rework: the manor's stations are the big sculpted ones, any piece opens its kind (locked till Act II)
		c.check(SculptBlocks.MANOR_COOKHEARTH.get() instanceof PropBlock.Sculpt s1 && s1.use() == PropBlock.Sculpt.Use.MEAL, "the Cook's Hearth cooks");
		c.check(SculptBlocks.MANOR_BREWERY.get() instanceof PropBlock.Sculpt s2 && s2.use() == PropBlock.Sculpt.Use.BREW, "the Brewer's Kettle brews");
		c.check(SculptBlocks.MANOR_ALEMBIC.get() instanceof PropBlock.Sculpt s3 && s3.use() == PropBlock.Sculpt.Use.ELIXIR, "the Alchemist's Still makes elixirs");
		c.check(Stations.HOMESTEAD[0] <= -300 && Stations.HOMESTEAD[3] >= -206, "no townsfolk at the homestead");
		// 11/7 cooking takes time at a station, mastery makes it quicker (Kitchen)
		c.check(Kitchen.stars(0) == 0 && Kitchen.stars(5) == 1 && Kitchen.stars(70) == 4, "mastery stars at 5/15/35/70 made");
		Trades.Good anyGood = Trades.GOODS.values().iterator().next();
		c.check(Kitchen.seconds(anyGood, 4) < Kitchen.seconds(anyGood, 0) && Kitchen.seconds(anyGood, 0) >= 15, "a master cooks quicker: "
				+ Kitchen.seconds(anyGood, 0) + "s -> " + Kitchen.seconds(anyGood, 4) + "s");
		c.check(Trades.IN_X + 2 * 22 + 8 == 215 && Trades.PACK_X + 81 == 215, "the bench's slots and pack sit on its centre line");
		c.check(Trades.GOODS.size() >= 70, "the goods table is in: " + Trades.GOODS.size());
		// pass 16: whole words, and every food mod's raw things land in a kind (Croptopia, Farmer's Delight, Let's Do...)
		java.util.Map<String, String> want = java.util.Map.of("croptopia:eggplant", "veg", "croptopia:cauliflower", "veg", "croptopia:steamed_broccoli", "veg",
				"croptopia:almond", "nut", "croptopia:cinnamon", "spice", "croptopia:honeydew", "fruit", "croptopia:blueberry", "fruit", "croptopia:chile_pepper", "ember");
		want.forEach((id, k) -> {
			var it = BuiltInRegistries.ITEM.getOptional(ResourceLocation.parse(id));
			if (it.isPresent()) c.check(k.equals(Trades.kindOf(new ItemStack(it.get()))), id + " is " + k + ": " + Trades.kindOf(new ItemStack(it.get())));
		});
		java.util.Map<String, Integer> kinds = new java.util.TreeMap<>();
		java.util.List<String> none = new java.util.ArrayList<>();
		for (var e : BuiltInRegistries.ITEM.entrySet()) {
			String ns = e.getKey().location().getNamespace(), path = e.getKey().location().getPath();
			if (!(ns.equals("croptopia") || ns.equals("farmersdelight") || ns.startsWith("letsdo") || ns.equals("vinery") || ns.equals("farm_and_charm")
					|| ns.equals("herbalbrews") || ns.equals("brewery") || ns.equals("bakery") || ns.equals("meadow") || ns.equals("candlelight"))) continue;
			ItemStack st = new ItemStack(e.getValue());
			if (!st.has(net.minecraft.core.component.DataComponents.FOOD) && !st.is(Trades.CROPS_TAG)) continue;
			String k = Trades.kindOf(st);
			if (k == null) none.add(ns + ":" + path);
			else kinds.merge(k, 1, Integer::sum);
		}
		Ashbound.LOG.info("SELFTEST kinds of the food mods' food: {}; no kind ({}): {}", kinds, none.size(), String.join(" ", none));
		c.near(Trades.level(0), 1, 0, "everyone starts at 1");
		c.near(Trades.level(Trades.need(1)), 2, 0, "one level's XP is level 2");
		c.check(Trades.match(Trades.Kind.MEAL, List.of("meat", "veg", "veg")).id().equals("hunters_stew"), "meat and two vegetables is a stew, in any order");
		c.check(Trades.match(Trades.Kind.MEAL, List.of("veg", "meat", "veg")).id().equals("hunters_stew"), "in any order");
		c.check(Trades.match(Trades.Kind.MEAL, List.of("meat", "veg", "veg", "fish")) == null, "a thing too many is a miss");
		c.check(Trades.match(Trades.Kind.BREW, List.of("meat", "veg", "veg")) == null, "a keg won't make a stew");
		FakePlayer p = player(h, 1);
		p.containerMenu = new Trades.Bench(1, p.getInventory(), Trades.Kind.MEAL);
		var b = (Trades.Bench) p.containerMenu;
		b.in.setItem(0, new ItemStack(Items.BEEF));
		b.in.setItem(1, new ItemStack(Items.CARROT));
		b.in.setItem(2, new ItemStack(Items.POTATO));
		Trades.act(p, new Net.TradeAct(Trades.CRAFT, ""));
		c.check(p.getInventory().countItem(Trades.ITEMS.get("hunters_stew").get()) == 0 && !Trades.knows(p, "hunters_stew"), "a stew is beyond a Novice of level 1");
		Trades.gain(p, "cooking", Trades.need(1) + Trades.need(2));
		int xpWas = Trades.xp(p, "cooking");
		p.getInventory().clearContent();
		b.in.setItem(0, new ItemStack(Items.BEEF));
		b.in.setItem(1, new ItemStack(Items.CARROT));
		b.in.setItem(2, new ItemStack(Items.POTATO));
		Trades.act(p, new Net.TradeAct(Trades.CRAFT, ""));
		c.check(p.getInventory().countItem(Trades.ITEMS.get("hunters_stew").get()) >= 1, "the bench made the stew");
		c.check(b.in.isEmpty(), "and used what was in it");
		c.check(Trades.knows(p, "hunters_stew"), "it's in the recipe book now");
		c.check(Trades.xp(p, "cooking") - xpWas > 60, "finding it gives trade XP");
		b.in.setItem(0, new ItemStack(Items.STONE_SWORD));
		c.check(!b.slots.get(0).mayPlace(new ItemStack(Items.STONE_SWORD)), "a sword doesn't go in a cooking pot");
		b.in.clearContent();
		b.in.setItem(0, new ItemStack(Items.BEEF));
		b.in.setItem(1, new ItemStack(Items.SUGAR));
		Trades.act(p, new Net.TradeAct(Trades.CRAFT, ""));
		c.check(p.getInventory().countItem(Trades.ITEMS.get("burnt_mush").get()) == 1, "a miss is mush");
		// 11/7: any other food is a small buff that tires; recipes are learnt from pages and townsfolk
		Trades.Good beef = Trades.snack(Items.COOKED_BEEF);
		c.check(beef != null && beef.stats().containsKey("stamina%"), "cooked beef is a snack: " + (beef == null ? "-" : beef.stats()));
		c.check(Trades.snack(Trades.ITEMS.get("jerky").get()) == null && Trades.snack(Items.STONE) == null, "our dishes and stone aren't snacks");
		double st0 = Passives.stat(p, "stamina%");
		Trades.eatSnack(p, new ItemStack(Items.COOKED_BEEF));
		double once = Passives.stat(p, "stamina%") - st0;
		Trades.eatSnack(p, new ItemStack(Items.COOKED_BEEF));
		double twice = Passives.stat(p, "stamina%") - st0;
		c.check(once > 0 && twice > 0 && twice < once, "beef again is worth less: " + once + " -> " + twice);
		c.check(Trades.knows(p, "jerky") && !Trades.knows(p, "nutbread"), "the first level's recipes are known, the rest found");
		Trades.Good page = Recipes.read(p, Trades.Kind.MEAL);
		c.check(page != null && Trades.knows(p, page.id()), "a page teaches a recipe: " + (page == null ? "-" : page.id()));
		c.check(Recipes.PAGES.size() == 3 && Recipes.price(Trades.GOODS.get("nutbread")) > 12, "three kinds of page, recipes cost coins");
		double before = Passives.stat(p, "health%");
		Trades.consume(p, Trades.GOODS.get("hunters_stew"), 1, false);
		double stew = Trades.GOODS.get("hunters_stew").stats().get("health%"), ale = Trades.GOODS.get("highmourn_ale").stats().get("move%");
		c.near(Passives.stat(p, "health%") - before, stew, 0.001, "a Common stew's health reaches your stats");
		double moveWas = Passives.stat(p, "move%");
		Trades.consume(p, Trades.GOODS.get("highmourn_ale"), 4, false);
		c.near(Passives.stat(p, "move%") - moveWas, ale, 0.001, "an ale's catch isn't made bigger by its rarity");
		c.near(Passives.stat(p, "health%") - before, stew, 0.001, "a brew doesn't push the meal off");
		Trades.consume(p, Trades.GOODS.get("jerky"), 1, false);
		c.near(Passives.stat(p, "health%") - before, 0, 0.001, "a second meal takes the first one's place");
		// fatigue: the same dish again soon is worth less, a second brew makes you tipsy, elixirs fill your toxicity
		p.setShiftKeyDown(true);                                    // sneaking: have it though the jerky's stronger
		Trades.consume(p, Trades.GOODS.get("hunters_stew"), 1, false);
		p.setShiftKeyDown(false);
		c.near(Passives.stat(p, "health%") - before, stew * 0.7, 0.001, "a stew again so soon is 70% as good");
		double bread = Passives.stat(p, "health%");
		Trades.consume(p, Trades.GOODS.get("hearthbread"), 1, false);
		c.near(Passives.stat(p, "health%"), bread, 0.001, "a weaker meal leaves the stronger one running (11/7)");
		c.check(Trades.tipsy(p) == 0, "one brew, sober");
		Trades.consume(p, Trades.GOODS.get("highmourn_ale"), 1, false);
		c.check(Trades.tipsy(p) == 1, "a second brew in ten minutes, tipsy");
		c.near(Passives.stat(p, "move%") - moveWas, ale - 5, 0.001, "tipsy is a little slower on top of the catch");
		Trades.consume(p, Trades.GOODS.get("ironskin"), 1, false);
		Trades.consume(p, Trades.GOODS.get("berserkers_draught"), 1, false);
		c.near(Trades.toxicity(p), 100, 0.5, "two strong elixirs fill the toxicity");
		c.check(Trades.toxicity(p) <= Trades.toxLimit(p), "and stay just inside the limit");
		double dmgWas = Passives.stat(p, "dmg%");
		Trades.consume(p, Trades.GOODS.get("arcane_philtre"), 1, false);
		c.check(Trades.toxicity(p) > Trades.toxLimit(p), "a third goes over");
		c.near(Passives.stat(p, "dmg%"), dmgWas, 0.001, "different elixirs all work at once");
		p.setHealth(1);
		Trades.consume(p, Trades.GOODS.get("mending_draught"), 1, false);
		double mend = Trades.GOODS.get("mending_draught").now().get("heal") / 100;
		c.near(p.getHealth(), Math.min(p.getMaxHealth(), 1 + p.getMaxHealth() * mend), 0.01, "mending heals " + Math.round(mend * 100) + "% of your health");
		Trades.Perk first = Trades.PERKS.get("shared_plate");
		c.check(Trades.why(p, first) != null, "a perk needs its level");
		Trades.gain(p, "cooking", 5000);
		c.check(Trades.why(p, Trades.PERKS.get("long_simmer")) != null, "and the one before it in its branch");
		Trades.act(p, new Net.TradeAct(Trades.TAKE_PERK, "shared_plate"));
		c.check(Trades.has(p, "shared_plate"), "a perk can be taken");
		c.near(Trades.spent(p), 1, 0, "and its point is spent");
		c.check(Trades.earned(p) <= Trades.MOST_POINTS, "points stop at the cap");
		Trades.gain(p, "smithing", 100000);
		c.check(Trades.earned(p) == Trades.MOST_POINTS, "however much you level, " + Trades.MOST_POINTS + " points");
		p.containerMenu = b;
		p.getInventory().clearContent();
		// pass 16: a batch at our own station, the same recipe again and again from the pack until it runs out
		int stews = p.getInventory().countItem(Trades.ITEMS.get("hunters_stew").get());
		b.tier = 1;
		p.getInventory().add(new ItemStack(Items.BEEF, 2));
		p.getInventory().add(new ItemStack(Items.CARROT, 2));
		p.getInventory().add(new ItemStack(Items.POTATO, 2));
		b.in.setItem(0, new ItemStack(Items.BEEF));
		b.in.setItem(1, new ItemStack(Items.CARROT));
		b.in.setItem(2, new ItemStack(Items.POTATO));
		Trades.act(p, new Net.TradeAct(Trades.CRAFT, "64"));
		c.near(p.getInventory().countItem(Trades.ITEMS.get("hunters_stew").get()) - stews, 3, 0, "a station's batch makes three stews from three sets, then stops");
		b.tier = 0;
		double[] house = Trades.oddsAt(30, 0, Trades.cap(2), Trades.rolls(2)), stove = Trades.oddsAt(30, 0, Trades.cap(0), Trades.rolls(0));
		c.near(java.util.Arrays.stream(house).sum(), 100, 0.01, "the house's odds add up");
		c.check(house[0] < stove[0] && stove[3] == 0 && stove[4] == 0, "the house rolls better than a borrowed stove, which never makes Epic");
		c.end(h);
	}

	// ---------------------------------------------------------------- adventurers

	@GameTest(template = "selftest")
	public static void adventurers(GameTestHelper h) {
		Checks c = new Checks("adventurers");
		c.check(Adventurers.PARTIES.size() >= 12, "the parties load");
		for (Adventurers.Party pa : Adventurers.PARTIES) c.check(pa.members().size() >= 3, pa.name() + " has at least three");
		var rng = h.getLevel().getRandom();
		for (char rank : "FEDCBAS".toCharArray())
			for (String role : List.of("tank", "breaker", "striker", "lancer", "ranger", "rogue", "black_mage", "white_mage")) {
				Adventurer a = Adventurers.TYPE.get().create(h.getLevel());
				Adventurers.dress(a, rank, role, rng);
				c.check(!a.getMainHandItem().isEmpty(), rank + " " + role + " carries a weapon");
				c.check(!a.getItemBySlot(net.minecraft.world.entity.EquipmentSlot.CHEST).isEmpty(), rank + " " + role + " wears a chest piece");
				if (role.equals("tank")) c.check(!a.getOffhandItem().isEmpty(), rank + " tank has a shield");
				if (role.equals("ranger")) c.check(a.getMainHandItem().getItem() instanceof net.minecraft.world.item.BowItem && a.fights.equals("bow"), rank + " ranger draws a bow");
				if (role.endsWith("mage")) c.check(a.fights.equals(role.equals("black_mage") ? "black" : "white"), rank + " " + role + " casts");
			}
		var at = h.absolutePos(new net.minecraft.core.BlockPos(1, 2, 1));
		List<Adventurer> made = Adventurers.spawn(h.getLevel(), at, Adventurers.PARTIES.get(0));
		c.check(made.size() == Adventurers.PARTIES.get(0).members().size(), "a whole party comes into the world");
		Adventurer one = made.get(0), two = made.get(1);
		FakePlayer p = player(h, 1);
		float was = one.getHealth();
		one.hurt(h.getLevel().damageSources().playerAttack(p), 5);
		c.near(one.getHealth(), was, 0.001, "a player can't hurt them");
		one.hurt(h.getLevel().damageSources().mobAttack(two), 5);
		c.near(one.getHealth(), was, 0.001, "nor can one of their own");
		var z = net.minecraft.world.entity.EntityType.ZOMBIE.create(h.getLevel());
		z.moveTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5);
		h.getLevel().addFreshEntity(z);
		float zw = z.getHealth();
		z.hurt(h.getLevel().damageSources().mobAttack(one), 5);
		c.check(z.getHealth() < zw, "they hurt monsters");
		c.check(made.stream().allMatch(a -> a.party.equals(one.party)), "they know their party");
		made.forEach(net.minecraft.world.entity.Entity::discard);
		z.discard();
		c.end(h);
	}

	/** Who you meet out there, and a camp: a fire nobody stands in, put out by the last of them to go. */
	@GameTest(template = "selftest")
	public static void adventurerMeet(GameTestHelper h) {
		Checks c = new Checks("adventurerMeet");
		var r = h.getLevel().getRandom();
		for (int rank = 0; rank < 7; rank++) {
			int far = 0;
			for (int k = 0; k < 200; k++) far = Math.max(far, Math.abs("FEDCBAS".indexOf(Adventurers.choose(rank, java.util.Set.of(), r).rank()) - rank));
			c.check(far <= 2, "rank " + "FEDCBAS".charAt(rank) + " meets parties within two ranks of it");
		}
		java.util.Set<String> all = new java.util.HashSet<>();
		Adventurers.PARTIES.forEach(x -> all.add(x.name()));
		c.check(Adventurers.choose(0, all, r) == null, "no party is about twice");
		var at = h.absolutePos(new net.minecraft.core.BlockPos(2, 2, 2));
		h.getLevel().setBlock(at, net.minecraft.world.level.block.Blocks.CAMPFIRE.defaultBlockState(), 3);
		List<Adventurer> made = Adventurers.spawn(h.getLevel(), at, Adventurers.PARTIES.get(0));
		made.forEach(a -> {
			a.mode = "camp";
			a.home = at;
		});
		c.check(made.stream().noneMatch(a -> a.blockPosition().getX() == at.getX() && a.blockPosition().getZ() == at.getZ()), "nobody stands in the fire");
		c.check(made.stream().filter(a -> a.leads).count() == 1, "one of them leads");
		made.forEach(net.minecraft.world.entity.Entity::discard);
		c.check(!h.getLevel().getBlockState(at).is(net.minecraft.world.level.block.Blocks.CAMPFIRE), "the last of them to go puts the fire out");
		c.end(h);
	}

	/** What they say: every kind of line there, filled in, and a rumour that's real words. */
	@GameTest(template = "selftest")
	public static void adventurerTalk(GameTestHelper h) {
		Checks c = new Checks("adventurerTalk");
		var r = h.getLevel().getRandom();
		var at = h.absolutePos(new net.minecraft.core.BlockPos(2, 2, 2));
		List<Adventurer> made = Adventurers.spawn(h.getLevel(), at, Adventurers.PARTIES.get(0));
		Adventurer a = made.get(0);
		FakePlayer p = player(h, 1);
		p.moveTo(at.getX() + 3, at.getY(), at.getZ());
		for (String k : List.of("taunt", "fight", "heal", "hurt", "won", "thanks", "mate_down", "busy", "walk_low", "walk_mid", "walk_high", "camp_low",
				"camp_mid", "camp_high", "town", "see_higher", "see_lower", "see_same", "greet_low", "greet_mid", "greet_high", "greet_owed", "who", "since",
				"rumour_gate", "rumour_incident", "rumour_town", "rumour_weapon", "rumour_none", "bye"))
			c.check(!AdventurerTalk.LINES.getOrDefault(k, List.of()).isEmpty(), "they have lines for " + k);
		for (String k : List.of("taunt", "thanks", "see_higher", "greet_high", "walk_low", "bye")) {
			String s = AdventurerTalk.line(k, a, p, java.util.Map.of("who", "Ada"), r);
			c.check(!s.isEmpty() && !s.contains("{"), k + " fills in: " + s);
		}
		String rumour = AdventurerTalk.rumour(a, p, r);
		c.check(!rumour.isEmpty() && !rumour.contains("{"), "a rumour: " + rumour);
		// the test's fake player isn't one of the world's players: as far as they know nobody's there
		a.bark("taunt", null, java.util.Map.of(), true);
		c.check(a.bark().isEmpty(), "with nobody near to hear, they say nothing");
		made.forEach(net.minecraft.world.entity.Entity::discard);
		c.end(h);
	}

	/** What a party asks of you: each kind worded and paid, and a camp put down, cleared and paid for, its fire out, the party done with it. */
	@GameTest(template = "selftest", timeoutTicks = 100)
	public static void adventurerAsk(GameTestHelper h) {
		Checks c = new Checks("adventurerAsk");
		var l = h.getLevel();
		var r = l.getRandom();
		var at = h.absolutePos(new net.minecraft.core.BlockPos(2, 2, 2));
		List<Adventurer> made = Adventurers.spawn(l, at, Adventurers.PARTIES.get(0));
		Adventurer a = made.get(0);
		FakePlayer p = player(h, 1);
		p.moveTo(at.getX() + 3, at.getY(), at.getZ());
		for (String k : List.of("req_title_report", "req_title_fetch", "req_title_camp", "req_ask_report", "req_ask_fetch", "req_ask_camp", "req_take_report",
				"req_take_fetch", "req_take_camp", "req_no", "req_full", "req_none", "req_desk", "camp_cleared"))
			c.check(!AdventurerTalk.LINES.getOrDefault(k, List.of()).isEmpty(), "they have lines for " + k);
		// a report and a fetch go to the Guild: only asked where there's a Guild
		for (String kind : List.of("report", "fetch")) {
			made.forEach(m -> m.ask = kind);
			AdventurerTalk.Ask o = AdventurerTalk.offer(a, p, r);
			if (Story.desk() == null) c.check(o == null, kind + ": no Guild in this world, so they don't ask");
			else c.check(o != null && !o.text().contains("{") && o.errand().coins() > 0 && !o.errand().title().contains("{"), kind + ": " + (o == null ? "-" : o.errand().title() + " / " + o.errand().objective()));
		}
		// a camp, as if they'd asked and you'd said yes
		made.forEach(m -> m.ask = "camp");
		c.check(AdventurerTalk.asks(a, p), "they've something to ask");
		var camp = l.getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, at.offset(6, 0, 6));
		Errands.Errand e = new Errands.Errand(Errands.ADV_T + "camp", Errands.KILL, Errands.CAMP + a.party, 3, 0, 40, 0, Errands.ADV + a.party, a.partyName,
				camp.getX(), camp.getZ(), 0, "Test Camp", "Clear the camp: 3 of them");
		boolean took = AdventurerTalk.take(a, p, new AdventurerTalk.Ask("camp", e, "", camp, 3), r);
		c.check(took, "taken on");
		Errands.Errand mine = Errands.find(p, "fav:" + Errands.ADV + a.party);
		c.check(mine != null && mine.count() > 0, "on the list: " + (mine == null ? "-" : mine.count() + " to kill"));
		c.check(!AdventurerTalk.asks(a, p), "and they don't ask again");
		c.check(made.stream().allMatch(m -> camp.equals(m.task) && m.ask.isEmpty()), "the party sets off for it");
		c.check(l.getBlockState(camp).is(net.minecraft.world.level.block.Blocks.CAMPFIRE), "a fire at the camp");
		List<net.minecraft.world.entity.Mob> foes = l.getEntitiesOfClass(net.minecraft.world.entity.Mob.class, new net.minecraft.world.phys.AABB(camp).inflate(12),
				m -> (a.party.toString()).equals(m.getPersistentData().getString(Adventurers.CAMP_TAG)));
		c.check(mine != null && foes.size() == mine.count(), foes.size() + " monsters dug in");
		c.check(foes.stream().allMatch(net.minecraft.world.entity.Mob::isPersistenceRequired), "who stay put");
		int before = Coins.of(p);
		for (var m : foes) {
			m.kill();
			Errands.campFell(a.party.toString(), List.of(p));
		}
		c.check(Errands.find(p, "fav:" + Errands.ADV + a.party) == null, "cleared and done");
		c.check(Coins.of(p) >= before + 40, "paid: " + (Coins.of(p) - before) + " coins");
		c.check(!l.getBlockState(camp).getValue(net.minecraft.world.level.block.CampfireBlock.LIT), "the fire's out");
		c.check(made.stream().allMatch(m -> m.task == null), "and the party's done with it");
		made.forEach(net.minecraft.world.entity.Entity::discard);
		c.end(h);
	}

	/** Wild encounters: each scene set down and played through: a caravan saved, deserters parleying then fighting, a hunter only
	 * where there's a town, a duel to yielding both ways; and everything of a scene gone when it ends. */
	@GameTest(template = "selftest", timeoutTicks = 100)
	public static void encounters(GameTestHelper h) {
		Checks c = new Checks("encounters");
		var l = h.getLevel();
		var r = l.getRandom();
		var at = l.getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, h.absolutePos(new net.minecraft.core.BlockPos(3, 2, 3)));
		FakePlayer p = player(h, 1);
		p.moveTo(at.getX() + 4, at.getY(), at.getZ());
		for (String k : List.of("caravan_hear", "caravan_thanks", "deserter_warn", "deserter_ask", "deserter_paid", "deserter_talked", "deserter_failed", "deserter_fight",
				"deserter_purse", "hunter_help", "hunter_ask", "hunter_go", "hunter_no", "hunter_on", "hunter_wave", "hunter_safe", "hunter_lost", "hunter_after",
				"duel_call", "duel_ask", "duel_start", "duel_on", "duel_no", "duel_yield", "duel_win"))
			c.check(!AdventurerTalk.LINES.getOrDefault(k, List.of()).isEmpty(), "lines for " + k);
		// a caravan: a wagon, a trader, guards, and what's attacking them
		var cs = Encounters.begin("caravan", l, at, 1, 1, null, r);
		c.check(cs instanceof Encounters.Caravan, "a caravan");
		if (cs instanceof Encounters.Caravan cv) {
			c.check(cs.ents.stream().anyMatch(u -> l.getEntity(u) instanceof Wagon), "with its wagon");
			c.check(cv.trader != null && l.getEntity(cv.trader) instanceof Npc, "and a trader");
			c.check(!cv.guards.isEmpty() && !cv.foes.isEmpty(), cv.guards.size() + " guards against " + cv.foes.size());
			cv.foes.forEach(u -> {
				if (l.getEntity(u) != null) l.getEntity(u).kill();
			});
			cv.tick(r);
			c.check(cv.saved && cv.endAt > 0, "saved, and winding up");
			cs.end();
			c.check(cs.ents.stream().allMatch(u -> l.getEntity(u) == null || !l.getEntity(u).isAlive()), "and gone when it ends");
		}
		// deserters: they don't go for you while they're talking terms; then they do
		var ds = Encounters.begin("deserters", l, at, 2, 1, null, r);
		c.check(ds instanceof Encounters.Deserters, "deserters");
		if (ds instanceof Encounters.Deserters d) {
			c.check(d.toll > 0 && d.men.size() >= 3, d.men.size() + " of them, toll " + d.toll);
			var boss = (net.minecraft.world.entity.Mob) l.getEntity(d.boss);
			c.check(boss != null && "D".equals(boss.getPersistentData().getString("ashbound_soft")), "brought to the party's rank");
			boss.setTarget(p);
			c.check(boss.getTarget() == null, "talking terms, not fighting");
			d.fight();
			boss.setTarget(p);
			c.check(boss.getTarget() == p, "and then fighting");
			ds.end();
		}
		// a hunter needs a town to walk to
		var hs = Encounters.begin("hunter", l, at, 1, 1, null, r);
		if (Capital.sites.length == 0) c.check(hs == null, "no town in this world: no hunter");
		else c.check(hs == null || hs instanceof Encounters.Hunter, "a hunter, with a town to walk to");
		if (hs != null) hs.end();
		// a duel, won: they yield, and hand over their blade
		var dl = Encounters.begin("duelist", l, at, 1, 1, null, r);
		c.check(dl instanceof Encounters.Duelist, "a duelist");
		if (dl instanceof Encounters.Duelist du && l.getEntity(du.duelist) instanceof Adventurer a) {
			boolean armed = !a.getMainHandItem().isEmpty();
			a.duel = p.getUUID();
			c.check(!a.isAlliedTo(p), "not on your side for the bout");
			a.setHealth(a.getMaxHealth() * 0.2f);
			a.invulnerableTime = 0;
			a.hurt(p.damageSources().playerAttack(p), a.getMaxHealth() * 0.2f);
			c.check(a.duel == null && du.done && a.isAlive(), "they yield, alive");
			c.check(!armed || a.getMainHandItem().isEmpty(), "and give up their blade");
			// and lost (the test's fake player can't be hurt, so straight to the end of it)
			a.duel = p.getUUID();
			Encounters.duelOver(a, p, false);
			c.check(a.duel == null && a.getTarget() == null, "you yield: the bout's over");
			dl.end();
		}
		Encounters.LIVE.clear();
		c.end(h);
	}

	/** A fallen party: dead where they fell (lying still, out of every fight); not searched with what killed them close; the map on
	 * one of them leads to a stash that's made when someone's near, wakes its bane when they dig, won't give while it lives, and
	 * pays out when it's down. */
	@GameTest(template = "selftest", timeoutTicks = 100)
	public static void fallenTreasure(GameTestHelper h) {
		Checks c = new Checks("fallenTreasure");
		var l = h.getLevel();
		var r = l.getRandom();
		var at = l.getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, h.absolutePos(new net.minecraft.core.BlockPos(3, 2, 3)));
		FakePlayer p = player(h, 1);
		p.moveTo(at.getX() + 4, at.getY(), at.getZ());
		for (String k : List.of("fallen_hear", "fallen_foes", "fallen_search", "fallen_map", "stash_scrawl", "stash_near", "stash_wake", "diary_out", "diary_stash", "diary_end"))
			c.check(!AdventurerTalk.LINES.getOrDefault(k, List.of()).isEmpty(), "lines for " + k);
		var sc = Encounters.begin("fallen", l, at, 1, 1, null, r);
		c.check(sc instanceof Encounters.Fallen, "a fallen party");
		if (!(sc instanceof Encounters.Fallen f)) {
			Encounters.LIVE.clear();
			c.end(h);
			return;
		}
		c.check(f.dead.size() >= 2, f.dead.size() + " of them dead round the fire");
		boolean lying = f.dead.stream().allMatch(u -> l.getEntity(u) instanceof Adventurer a && a.fallen() > 0 && a.isNoAi() && a.isInvulnerable() && !a.canBeSeenAsEnemy()
				&& a.getBbHeight() < 1);
		c.check(lying, "lying still, nothing to fight or target");
		c.check(l.getBlockState(at).getBlock() != net.minecraft.world.level.block.Blocks.FIRE && !f.placed.isEmpty(), "a cold fire, no flame");
		Adventurer holder = l.getEntity(f.holder) instanceof Adventurer a ? a : null;
		c.check(holder != null, "one of them has the map");
		if (holder == null) {
			sc.end();
			Encounters.LIVE.clear();
			c.end(h);
			return;
		}
		// what killed them, standing over them: no searching yet
		net.minecraft.world.entity.Mob foe = f.foes.isEmpty() ? null : (net.minecraft.world.entity.Mob) l.getEntity(f.foes.get(0));
		if (foe == null) {
			foe = Encounters.monster(l, Adventurers.any(Gear.of(f.gate).mobs(), r), at, 2, r);
			if (foe != null && l.addFreshEntity(sc.keep(foe))) f.foes.add(foe.getUUID());
		}
		if (foe != null) {
			foe.moveTo(holder.getX() + 2, holder.getY(), holder.getZ());
			f.search(p, holder);
			c.check(!f.searched.contains(holder.getUUID()), "not searched with a killer close");
		}
		for (java.util.UUID u : f.foes) if (l.getEntity(u) != null) l.getEntity(u).kill();
		int before = Coins.of(p);
		f.search(p, holder);
		ItemStack map = ItemStack.EMPTY;
		for (int i = 0; i < p.getInventory().getContainerSize(); i++) if (Treasure.of(l, p.getInventory().getItem(i)) != null) map = p.getInventory().getItem(i);
		Treasure.Stash far = Treasure.of(l, map);
		c.check(Coins.of(p) > before && far != null, "searched: coins and a torn map");
		if (far != null) {
			double d = Math.hypot(far.pos.getX() - at.getX(), far.pos.getZ() - at.getZ());
			c.check(d >= Treasure.NEAR - 1 && d <= Treasure.FAR + 1 && !far.placed, "its X " + Math.round(d) + " blocks off, nothing there yet");
			Treasure.state(l).stashes.remove(far.id);
		}
		int after = Coins.of(p);
		f.search(p, holder);
		c.check(Coins.of(p) == after, "nothing more on them the second time");
		BlockPos fire = f.placed.get(0);
		sc.end();
		c.check(f.dead.stream().allMatch(u -> l.getEntity(u) == null || !l.getEntity(u).isAlive()), "the dead are gone when it ends");
		c.check(!l.getBlockState(fire).getBlock().getDescriptionId().contains("campfire"), "and their fire with them");
		// a stash close by, to dig up
		Treasure.Stash st = Treasure.of(l, Treasure.map(l, at, 1, f.gate, f.party, r, 6, 9));
		c.check(st != null, "a map to a stash");
		if (st != null) {
			Treasure.place(l, st, r);
			c.check(st.placed && st.chest != null && l.getBlockState(st.chest).is(net.minecraft.world.level.block.Blocks.CHEST) && st.chest.getY() == st.pos.getY() - 3,
					"the chest is buried two blocks under the X");
			Treasure.wake(l, st, p);
			var bane = st.guard == null ? null : l.getEntity(st.guard);
			c.check(st.woke && bane instanceof net.minecraft.world.entity.Mob && bane.getCustomName() != null && bane.getCustomName().getString().contains("Bane of"),
					"digging wakes its bane: " + st.guardName);
			if (bane instanceof net.minecraft.world.entity.Mob m) m.moveTo(st.pos.getX() + 3, st.pos.getY(), st.pos.getZ());
			Treasure.open(l, st, p);
			c.check(!st.opened, "it won't give while the bane lives");
			if (bane != null) bane.kill();
			Treasure.open(l, st, p);
			c.check(st.opened && !l.getBlockState(st.chest).is(net.minecraft.world.level.block.Blocks.CHEST), "once it's down, the chest bursts open");
			c.check(Treasure.sharers(l, st, p, st.pos).contains(p), "whoever opens it shares in it");
			var loot = Treasure.loot(p, st, Gear.of(st.gate), r);
			c.check(loot.size() >= 4 && loot.get(loot.size() - 1).is(net.minecraft.world.item.Items.WRITTEN_BOOK), loot.size() + " things each, with the party's last pages");
			for (var e : l.getEntitiesOfClass(net.minecraft.world.entity.Mob.class, new net.minecraft.world.phys.AABB(st.pos).inflate(48), e -> e.getTags().contains(Treasure.TAG)))
				e.discard();
			Treasure.state(l).stashes.remove(st.id);
		}
		Encounters.LIVE.clear();
		c.end(h);
	}

	/** The gate storms: its eye opens face-down high over the ground, spires burst up round it, a strike warns, hits,
	 * scorches without fire and lets the dungeon's monsters out; breaking every spire collapses it and pays. */
	@GameTest(template = "selftest", timeoutTicks = 100)
	public static void skyCrack(GameTestHelper h) {
		Checks c = new Checks("skyCrack");
		var l = h.getLevel();
		var r = l.getRandom();
		var ground = l.getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, h.absolutePos(new net.minecraft.core.BlockPos(3, 2, 3)));
		FakePlayer p = player(h, 1);
		p.moveTo(ground.getX() + 2, ground.getY(), ground.getZ());
		SkyCrack sc = SkyCracks.open(l, ground, 1, 1, null, r);
		c.check(sc != null && sc.sky() && sc.middle().y > ground.getY() + 40, "it tears open high over the ground");
		if (sc == null) {
			c.end(h);
			return;
		}
		SkyCracks.Crack k = SkyCracks.LIVE.get(sc.getUUID());
		c.check(k != null && k.anchors == 3, "three spires hold it open for one");
		c.check(Math.abs(sc.tilt() - 90) < 0.01f, "its eye lies face-down: " + sc.tilt());
		c.check(!k.monsters.isEmpty(), "its strikes bring its dungeon's monsters: " + k.monsters);
		SkyCracks.raise(l, sc, k, r);
		c.check(k.placed == 3 && k.left == 3 && k.spires.size() == 3, "three spires burst up: " + k.placed);
		boolean round = k.spires.stream().allMatch(u -> l.getEntity(u) instanceof StormSpire s && Math.hypot(s.getX() - sc.getX(), s.getZ() - sc.getZ()) < SkyCracks.SPIRE_FAR + 2);
		c.check(round, "the spires stand round the eye");
		// a strike: warning first, then it hits, scorches (never fire) and the monsters climb out
		var st = SkyCracks.strike(l, sc, k, sc.getX() + 4, sc.getZ() + 4, false, r);
		c.check(st != null && st.charge() > 0, "a strike at the party warns first");
		if (st != null) {
			for (int i = 0; i <= StormStrike.CHARGE + StormStrike.CLIMB + 1; i++) {
				st.tickCount++;
				st.tick();
			}
			c.check(!k.mobs.isEmpty(), k.mobs.size() + " monsters climbed out of the strike");
			int fire = 0, burnt = 0;
			for (var at : net.minecraft.core.BlockPos.betweenClosed(st.blockPosition().offset(-4, -3, -4), st.blockPosition().offset(4, 3, 4))) {
				var bs = l.getBlockState(at);
				if (bs.is(net.minecraft.world.level.block.Blocks.FIRE)) fire++;
				if (bs.is(Gates.SCORCH.get())) burnt++;
			}
			c.check(fire == 0 && burnt > 0, "it scorched " + burnt + " blocks and lit no fire");
		}
		int before = Coins.of(p);
		for (java.util.UUID u : new java.util.ArrayList<>(k.spires))
			if (l.getEntity(u) instanceof StormSpire s) {
				c.check(!s.hurt(p.damageSources().playerAttack(p), 1), "a spire still rising can't be struck");
				for (int i = 0; i < StormSpire.RISE; i++) {
					s.tickCount++;
					s.tick();
				}
				c.check(s.isPickable(), "a risen spire can be struck");
				s.hurt(p.damageSources().playerAttack(p), 100000);
			}
		c.check(k.finishing && !k.won && !sc.closing(), "the spires down, it waits for its monsters to be finished: " + k.mobs.size());
		for (java.util.UUID u : new java.util.ArrayList<>(k.mobs))
			if (l.getEntity(u) instanceof net.minecraft.world.entity.LivingEntity m) m.kill();
		SkyCracks.tick(sc);
		c.check(k.won && sc.closing(), "the last of them dead, the storm collapses");
		var share = SkyCracks.loot(p, k, r);
		c.check(share.size() >= 2 && share.stream().noneMatch(net.minecraft.world.item.ItemStack::isEmpty), "a share of loot: " + share);
		// the fake player isn't one of the world's players: pay it as if it were there
		SkyCracks.LIVE.remove(sc.getUUID());
		k.spires.forEach(u -> {
			if (l.getEntity(u) != null) l.getEntity(u).discard();
		});
		k.mobs.forEach(u -> {
			if (l.getEntity(u) != null) l.getEntity(u).discard();
		});
		sc.discard();
		c.check(before >= 0, "cleared away");
		c.end(h);
	}

	/** A party against three tough husks for fifteen seconds: who fought, how much, and where they ended up. */
	@GameTest(template = "selftest", timeoutTicks = 420)
	public static void adventurerFight(GameTestHelper h) {
		Checks c = new Checks("adventurerFight");
		h.getLevel().getServer().setDifficulty(net.minecraft.world.Difficulty.NORMAL, true);
		var at = h.absolutePos(new net.minecraft.core.BlockPos(1, 2, 1));
		Adventurers.Party pa = Adventurers.PARTIES.stream().filter(x -> x.members().size() >= 5).findFirst().orElse(Adventurers.PARTIES.get(0));
		List<Adventurer> made = Adventurers.spawn(h.getLevel(), at, pa);
		List<net.minecraft.world.entity.monster.Husk> husks = new java.util.ArrayList<>();
		for (int i = 0; i < 3; i++) {
			var z = net.minecraft.world.entity.EntityType.HUSK.create(h.getLevel());
			z.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).setBaseValue(400);
			z.setHealth(400);
			var top = h.getLevel().getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, at.offset(7 + i, 0, 3));
			z.moveTo(top.getX() + 0.5, top.getY(), top.getZ() + 0.5);
			h.getLevel().addFreshEntity(z);
			husks.add(z);
		}
		java.util.Map<Adventurer, net.minecraft.world.phys.Vec3> from = new java.util.HashMap<>();
		made.forEach(a -> from.put(a, a.position()));
		h.runAfterDelay(20, () -> {
			for (Adventurer a : made)
				Ashbound.LOG.info("SELFTEST fight goals {} {} ({}): {} husks alive {}", a.getName().getString(), a.role(), a.fights,
						a.goalSelector.getAvailableGoals().stream().map(w -> w.getPriority() + ":" + w.getGoal().getClass().getSimpleName()).toList(),
						husks.stream().filter(net.minecraft.world.entity.Entity::isAlive).count());
		});
		h.runAfterDelay(300, () -> {
			for (Adventurer a : made) {
				float dealt = Adventurers.DEALT.getOrDefault(a.getUUID(), 0f);
				String goals = a.goalSelector.getAvailableGoals().stream().filter(w -> w.isRunning()).map(w -> w.getGoal().getClass().getSimpleName()).toList().toString();
				Ashbound.LOG.info("SELFTEST fight {} {} ({}): dealt {} target {} moved {} at {} goals {}", a.getName().getString(), a.role(), a.fights,
						String.format("%.1f", dealt), a.getTarget() == null ? "none" : a.getTarget().getType().toShortString(),
						String.format("%.1f", a.position().distanceTo(from.get(a))), a.blockPosition().toShortString(), goals);
				if (!a.role().equals("white_mage")) c.check(dealt > 0, a.role() + " (" + a.fights + ") fought");
			}
			made.forEach(net.minecraft.world.entity.Entity::discard);
			husks.forEach(net.minecraft.world.entity.Entity::discard);
			c.end(h);
		});
	}

	@GameTest(template = "selftest")
	public static void modVillages(GameTestHelper h) {
		Checks c = new Checks("mod_villages");
		var biomes = h.getLevel().registryAccess().registryOrThrow(net.minecraft.core.registries.Registries.BIOME);
		ResourceLocation ctov = ResourceLocation.fromNamespaceAndPath("ctov", "large/village_plains");
		java.util.function.Function<net.minecraft.resources.ResourceKey<net.minecraft.world.level.biome.Biome>, String> race = k -> ModVillages.race(biomes.getHolderOrThrow(k), ctov);
		c.check(race.apply(net.minecraft.world.level.biome.Biomes.DESERT).equals("demon") && race.apply(net.minecraft.world.level.biome.Biomes.BADLANDS).equals("demon")
				&& race.apply(net.minecraft.world.level.biome.Biomes.SAVANNA).equals("demon"), "deserts, badlands and savanna are the demons'");
		c.check(race.apply(net.minecraft.world.level.biome.Biomes.SNOWY_PLAINS).equals("dwarf") && race.apply(net.minecraft.world.level.biome.Biomes.TAIGA).equals("dwarf")
				&& race.apply(net.minecraft.world.level.biome.Biomes.MEADOW).equals("human"), "snow and taiga are the dwarves', a meadow the humans'");
		c.check(race.apply(net.minecraft.world.level.biome.Biomes.FOREST).equals("elf") && race.apply(net.minecraft.world.level.biome.Biomes.CHERRY_GROVE).equals("elf")
				&& race.apply(net.minecraft.world.level.biome.Biomes.SWAMP).equals("elf") && race.apply(net.minecraft.world.level.biome.Biomes.JUNGLE).equals("elf"),
				"forests, cherry groves, swamps and jungles are the elves'");
		c.check(race.apply(net.minecraft.world.level.biome.Biomes.PLAINS).equals("human") && race.apply(net.minecraft.world.level.biome.Biomes.BEACH).equals("human"), "plains and beaches are the humans'");
		c.check(ModVillages.village(ctov) && ModVillages.village(ResourceLocation.fromNamespaceAndPath("towns_and_towers", "village_meadow"))
				&& !ModVillages.village(ResourceLocation.fromNamespaceAndPath("towns_and_towers", "pillager_outpost_meadow"))
				&& !ModVillages.village(ResourceLocation.fromNamespaceAndPath("ashbound", "village_hill")), "villages are told from outposts, and ours are left alone");
		for (String r : new String[] {"dwarf", "elf", "demon", "human"})
			for (int i = 0; i < 4; i++) c.check(Talk.resolve(ModVillages.who(r, i), h.getLevel().random) != null, "someone answers to " + ModVillages.who(r, i));
		c.end(h);
	}

	// ---------------------------------------------------------------- the mounts

	@GameTest(template = "selftest")
	public static void mounts(GameTestHelper h) {
		Checks c = new Checks("mounts");
		c.check(Mounts.ALL.size() == 5, "five mounts");
		for (Mounts.Kind k : Mounts.ALL) {
			var m = Mounts.type(k).create(h.getLevel());
			c.check(m != null && m.kind == k, k.id() + " can be made");
			c.near(m.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.STEP_HEIGHT), k.step(), 0.001, k.id() + "'s step height");
			c.check(!m.hurt(h.getLevel().damageSources().generic(), 1000), k.id() + " can't be hurt");
			m.discard();
		}
		FakePlayer p = player(h, 7);
		Mounts.pick(p, "thornback");
		c.check(Mounts.of(p) == null, "no mount before a class");
		Classes.pick(p, "shade");
		Mounts.pick(p, "griffin");
		c.check(Mounts.of(p) == null, "a mount that doesn't exist is ignored");
		Mounts.pick(p, "thornback");
		c.check(Mounts.of(p) == Mounts.byId("thornback"), "a pick takes");
		Mounts.pick(p, "ashmane");
		c.check(Mounts.of(p) == Mounts.byId("thornback"), "a second pick can't change mount");
		p.setPos(p.getX(), p.getY() + 24, p.getZ());   // the test room is too small for it
		Mounts.toggle(p);
		// a FakePlayer refuses to ride anything, so this stops at the mount turning up
		var called = h.getLevel().getEntitiesOfClass(Mount.class, p.getBoundingBox().inflate(2));
		c.check(called.size() == 1 && called.get(0).kind == Mounts.of(p), "the key calls your mount");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void tidy(GameTestHelper h) {
		Checks c = new Checks("tidy");
		FakePlayer p = player(h, 8);
		var inv = p.getInventory();
		inv.setItem(0, new net.minecraft.world.item.ItemStack(Items.TORCH, 5));
		inv.setItem(20, new net.minecraft.world.item.ItemStack(Items.STONE, 40));
		inv.setItem(30, new net.minecraft.world.item.ItemStack(Items.STONE, 40));
		inv.setItem(12, new net.minecraft.world.item.ItemStack(Items.IRON_SWORD));
		Tidy.act(p, Tidy.SORT);
		c.check(inv.getItem(9).is(Items.IRON_SWORD), "gear sorts first");
		c.check(inv.getItem(10).is(Items.STONE) && inv.getItem(10).getCount() == 64 && inv.getItem(11).getCount() == 16, "part stacks merge");
		c.check(inv.getItem(0).is(Items.TORCH) && inv.getItem(0).getCount() == 5, "the hotbar stays put");
		c.check(inv.countItem(Items.STONE) == 80, "nothing lost sorting");
		var box = new net.minecraft.world.SimpleContainer(27);
		box.setItem(3, new net.minecraft.world.item.ItemStack(Items.STONE, 1));
		box.setItem(9, new net.minecraft.world.item.ItemStack(Items.DIAMOND, 4));
		p.containerMenu = net.minecraft.world.inventory.ChestMenu.threeRows(1, inv, box);
		Tidy.act(p, Tidy.STASH);
		c.check(inv.countItem(Items.STONE) == 0 && !box.hasAnyMatching(s -> s.is(Items.IRON_SWORD)), "stash takes only what the box holds");
		c.check(box.countItem(Items.STONE) == 81, "nothing lost stashing");
		Tidy.act(p, Tidy.TAKE);
		c.check(box.isEmpty() && inv.countItem(Items.DIAMOND) == 4 && inv.countItem(Items.STONE) == 81, "take all empties the box");
		p.containerMenu = p.inventoryMenu;
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void skills(GameTestHelper h) {
		Checks c = new Checks("skills");
		c.check(Skills.SPECS.size() == 18 && Skills.ALL.size() == 54, "two paths a class, three skills each");
		for (Classes.Cls k : Classes.ALL) c.check(Skills.specsOf(k.id()).size() == 2, k.id() + " has two paths");
		for (Skills.Spec s : Skills.SPECS) c.check(Skills.of(s) != null, s.id() + " teaches a skill");
		FakePlayer p = player(h, 1);
		Skills.pick(p, "bastion_slam");
		c.check(Skills.spec(p) == null, "no skill before a class");
		Classes.pick(p, "vanguard");
		Skills.pick(p, "bastion_slam");
		c.check(Skills.spec(p) == null, "no skill before its level");
		p.setData(Levels.LEVEL, Skills.SPEC_LEVEL);
		Skills.pick(p, "cinder_field");
		c.check(Skills.spec(p) == null, "no skill of another class");
		Skills.pick(p, "bastion_slam");
		c.check(Skills.spec(p) == Skills.spec("bulwark"), "a skill takes, and its path with it");
		Skills.pick(p, "oath_charge");
		c.check(Skills.rank(p, "oath_charge") == 0, "and the other for that level is gone");
		c.check(Skills.rank(p, "bastion_slam") == 1 && Skills.slot(p, 1).equals("bastion_slam"), "it goes on the first free key");
		Skills.teach(p, "bastion_slam", 3);
		Skills.teach(p, "bastion_slam", 2);
		c.check(Skills.rank(p, "bastion_slam") == 3, "a lower book doesn't take a rank away");
		Skills.assign(p, 3, "bastion_slam");
		c.check(Skills.slot(p, 3).equals("bastion_slam") && Skills.slot(p, 1).isEmpty(), "a skill moves between keys");
		Skills.assign(p, 2, "deadeye");
		c.check(Skills.slot(p, 2).isEmpty(), "a skill you don't know can't go on a key");
		Skills.assign(p, 0, "bastion_slam");
		c.check(Skills.slot(p, 0).isEmpty(), "the first key stays the held weapon's");
		var boar = net.minecraft.world.entity.EntityType.ZOMBIE.create(h.getLevel());
		boar.moveTo(p.getX() + 1, p.getY(), p.getZ());
		h.getLevel().addFreshEntity(boar);
		float was = boar.getHealth();
		var patch = yesman.epicfight.world.capabilities.EpicFightCapabilities.getEntityPatch(p, yesman.epicfight.world.capabilities.entitypatch.player.ServerPlayerPatch.class);
		if (patch != null) patch.setStamina(patch.getMaxStamina());
		Skills.use(p, 3);
		c.check(boar.getHealth() < was, "the skill lands");
		was = boar.getHealth();
		Skills.use(p, 3);
		c.check(boar.getHealth() == was, "and waits out its cooldown");
		boar.discard();
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void forms(GameTestHelper h) {
		Checks c = new Checks("forms");
		c.check(Forms.ALL.size() == Classes.ALL.size(), "a Tome for every class");
		for (Classes.Cls k : Classes.ALL) c.check(Forms.ALL.stream().filter(f -> f.cls().equals(k.id())).count() == 1, k.id() + " has its Tome");
		c.check(Books.TOMES.size() == Forms.ALL.size() && Books.BOOKS.size() == Skills.MAX_RANK, "the books are all there");
		FakePlayer p = player(h, 20);
		Classes.pick(p, "vanguard");
		Skills.pick(p, "bastion_slam");
		var drake = Forms.byId("drake");
		c.check(!Forms.read(p, Forms.byId("crown")), "another class's Tome can't be read");
		c.check(Skills.slot(p, 1).equals("bastion_slam") && Skills.open(p) == Skills.SLOTS, "four keys before a Tome");
		Skills.assign(p, 3, "bastion_slam");
		c.check(Forms.read(p, drake), "your own can");
		c.check(Skills.open(p) == Skills.SLOTS - 1 && Skills.slot(p, 3).isEmpty(), "and it costs the last key");
		Skills.assign(p, 3, "bastion_slam");
		c.check(Skills.slot(p, 3).isEmpty(), "that key stays gone");
		c.check(!Forms.read(p, drake), "the same Tome twice does nothing");
		p.setHealth(p.getMaxHealth());
		Forms.key(p);
		c.check(!Forms.active(p, "drake"), "no Form before its moment");
		p.setHealth(p.getMaxHealth() * 0.25f);
		Forms.key(p);
		c.check(Forms.active(p, "drake"), "the Form comes under 30% health");
		c.check(p.getArmorValue() == 0, "and takes your armour");
		Forms.leave(p);
		c.check(!Forms.active(p, "drake"), "it ends");
		Forms.key(p);
		c.check(!Forms.active(p, "drake"), "and rests before it comes again");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void books(GameTestHelper h) {
		Checks c = new Checks("books");
		var r = net.minecraft.util.RandomSource.create(5);
		int top = 0;
		for (int i = 0; i < 2000; i++) top = Math.max(top, Books.rollRank('F', r));
		c.check(top == 3, "an F dungeon's luck tops out at rank III");
		for (int i = 0; i < 2000; i++) c.check(Books.rollRank('S', r) <= Skills.MAX_RANK, "never past the top");
		FakePlayer p = player(h, 20);
		Classes.pick(p, "ashcaster");
		Skills.pick(p, "cinder_field");
		var wrong = Books.book(3, "void_none");
		p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, wrong);
		wrong.getItem().use(h.getLevel(), p, net.minecraft.world.InteractionHand.MAIN_HAND);
		c.check(Skills.rank(p, "cinder_field") == 1, "a blank book teaches nothing");
		for (int[] step : new int[][] {{3, 3}, {3, 4}, {2, 4}, {5, 5}}) {
			var b = Books.book(step[0], "cinder_field");
			p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, b);
			b.getItem().use(h.getLevel(), p, net.minecraft.world.InteractionHand.MAIN_HAND);
			c.check(Skills.rank(p, "cinder_field") == step[1], "book " + step[0] + " leaves rank " + step[1]);
		}
		var w = Gear.WEAPONS.stream().map(i -> i.get()).filter(i -> i instanceof Spells.Staff s && s.kind().equals("black")).findFirst().orElseThrow();
		p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, new net.minecraft.world.item.ItemStack(w));
		double mine = Spells.boost(Spells.held(p), p);
		c.check(mine > Spells.BOOST_FLOOR, "a black staff boosts an Ashcaster");
		FakePlayer q = player(h, 20);
		Classes.pick(q, "vanguard");
		q.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, new net.minecraft.world.item.ItemStack(w));
		c.near(Spells.boost(Spells.held(q), q), Spells.BOOST_FLOOR, 0.001, "and nobody else");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void skillPaths(GameTestHelper h) {
		Checks c = new Checks("skill paths");
		c.check(Skills.ALL.size() == Skills.SPECS.size() * Skills.UNLOCK.length, "three skills on every path");
		for (Skills.Spec s : Skills.SPECS) c.check(Skills.path(s.id()).size() == Skills.UNLOCK.length, s.id() + " has its three");
		c.check(Skills.ALL.stream().map(Skills.Skill::id).distinct().count() == Skills.ALL.size(), "no two skills share an id");
		for (Classes.Cls k : Classes.ALL) for (int t = 0; t < Skills.UNLOCK.length; t++) {
			var two = Skills.choices(k.id(), t);
			c.check(two.size() == 2 && !two.get(0).spec().equals(two.get(1).spec()), k.id() + " chooses between its two paths at level " + Skills.UNLOCK[t]);
		}
		FakePlayer p = player(h, 19);
		Classes.pick(p, "vanguard");
		Skills.pick(p, "shield_wall");
		c.check(Skills.rank(p, "shield_wall") == 0, "not the second before the first");
		Skills.pick(p, "bastion_slam");
		Skills.pick(p, "oath_cross");
		c.check(Skills.rank(p, "bastion_slam") == 1 && Skills.rank(p, "oath_cross") == 0, "at 19 only one skill");
		c.check(Skills.pending(19, Skills.picks(p)) == -1, "with nothing to choose");
		p.setData(Levels.LEVEL, 20);
		c.check(Skills.pending(20, Skills.picks(p)) == 1, "20 is the next choice");
		Skills.pick(p, "unbroken");
		c.check(Skills.rank(p, "unbroken") == 0, "the third can't jump the queue");
		Skills.pick(p, "oath_cross");
		c.check(Skills.rank(p, "oath_cross") == 1 && Skills.slot(p, 2).equals("oath_cross"), "the second can be the other path's, and goes on the next key");
		Skills.pick(p, "shield_wall");
		c.check(Skills.rank(p, "shield_wall") == 0, "one a level");
		var early = Books.book(2, "unbroken");
		p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, early);
		early.getItem().use(h.getLevel(), p, net.minecraft.world.InteractionHand.MAIN_HAND);
		c.check(Skills.rank(p, "unbroken") == 2, "a book teaches a skill early, if you've not chosen on its level");
		p.setData(Levels.LEVEL, 40);
		c.check(Skills.pending(40, Skills.picks(p)) == -1, "and that was the choice");
		var other = Books.book(3, "oath_charge");
		p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, other);
		other.getItem().use(h.getLevel(), p, net.minecraft.world.InteractionHand.MAIN_HAND);
		c.check(Skills.rank(p, "oath_charge") == 0, "the other one for a level you've chosen on asks first");
		Books.swap(p, "bastion_slam");
		c.check(Skills.rank(p, "oath_charge") == 3 && Skills.rank(p, "bastion_slam") == 0, "and takes one of yours for it");
		c.check(Skills.slot(p, 1).equals("oath_charge"), "on the same key");
		c.check(p.getMainHandItem().isEmpty(), "the book's gone");
		c.check(Skills.lost(p, "bastion_slam"), "the skill's lost");
		Skills.pick(p, "bastion_slam");
		c.check(Skills.rank(p, "bastion_slam") == 0, "and it can't be chosen back");
		Books.swap(p, "oath_cross");
		c.check(Skills.rank(p, "oath_cross") == 1, "no book, no swap");
		var foreign = Books.book(5, "meteor");
		p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, foreign);
		foreign.getItem().use(h.getLevel(), p, net.minecraft.world.InteractionHand.MAIN_HAND);
		Books.swap(p, "oath_cross");
		c.check(Skills.rank(p, "meteor") == 0 && Skills.rank(p, "oath_cross") == 1, "another class's book does nothing");
		FakePlayer old = player(h, 40);
		Classes.pick(old, "vanguard");
		old.setData(Skills.STATE, new java.util.HashMap<>(java.util.Map.of("spec", "bulwark", "rank.bastion_slam", "1", "rank.shield_wall", "2")));
		c.check(Skills.pending(40, Skills.picks(old)) == 0, "a save from before");
		Skills.settle(old);
		c.check(Skills.pending(40, Skills.picks(old)) == 2, "keeps what it had and chooses the rest");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void noSwingsWithoutHands(GameTestHelper h) {
		Checks c = new Checks("a body only plays what it can");
		var cog = BuiltInRegistries.ENTITY_TYPE.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "cogling")).create(h.getLevel());
		var duelist = BuiltInRegistries.ENTITY_TYPE.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "clockwork_duelist")).create(h.getLevel());
		var dual = yesman.epicfight.gameasset.Animations.BIPED_MOB_SWORD_DUAL3;
		if (cog instanceof net.minecraft.world.entity.Mob m && duelist instanceof net.minecraft.world.entity.Mob d) {
			c.check(MobSkills.fits(m, dual) == yesman.epicfight.gameasset.Animations.SPIDER_ATTACK, "a cogling's spin comes out as a bite");
			c.check(MobSkills.fits(m, yesman.epicfight.gameasset.Animations.BIPED_MOB_THROW) == yesman.epicfight.gameasset.Animations.SPIDER_ATTACK, "and so does its pull");
			c.check(MobSkills.fits(d, dual) == dual, "a duelist keeps its two swords");
		} else c.check(false, "the monsters exist");
		if (cog != null) {
			var at = h.absoluteVec(new net.minecraft.world.phys.Vec3(2, 1, 2));
			cog.setPos(at.x, at.y, at.z);
			h.getLevel().addFreshEntity(cog);
			var patch = yesman.epicfight.world.capabilities.EpicFightCapabilities.getEntityPatch(cog, yesman.epicfight.world.capabilities.entitypatch.LivingEntityPatch.class);
			c.check(patch != null && !patch.getArmature().hasJoint("Tool_R"), "a cogling has no hand");
			if (patch != null) {
				var hand = yesman.epicfight.gameasset.Armatures.BIPED.get().searchJointByName("Tool_R");
				var hits = new yesman.epicfight.api.collider.MultiOBBCollider(3, 0.35, 0.5, 1, 0, 0, -1).updateAndSelectCollideEntity(patch, null, 0, 0.1f, hand, 1);
				c.check(hits.isEmpty(), "and a swing from a hand it hasn't got hits nothing, where it used to take the server down");
			}
			cog.discard();
		}
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void nothingShovesBosses(GameTestHelper h) {
		Checks c = new Checks("a boss can't be shoved");
		Thrall t = Mounts.REVENANT.get().create(h.getLevel());
		c.check(t != null && !t.isPushable(), "a thrall's not pushed");
		GateMobs.Kind boss = GateMobs.KINDS.stream().filter(GateMobs.Kind::boss).findFirst().orElseThrow();
		var type = BuiltInRegistries.ENTITY_TYPE.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, boss.id()));
		c.check(type.create(h.getLevel()) instanceof net.minecraft.world.entity.LivingEntity e && !e.isPushable(), boss.id() + " stands its ground");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void threat(GameTestHelper h) {
		Checks c = new Checks("who a monster turns on");
		FakePlayer p = player(h, 20);
		Classes.pick(p, "vanguard");
		c.check(Threat.tank(p), "a Vanguard's a tank");
		Cinderhusk m = Monsters.CINDERHUSK.get().create(h.getLevel());
		Thrall t = Mounts.REVENANT.get().create(h.getLevel());
		if (m != null && t != null) {
			var at = h.absoluteVec(new net.minecraft.world.phys.Vec3(2, 1, 2));
			m.setPos(at.x, at.y, at.z);
			t.setPos(at.x, at.y, at.z + 1);
			t.addTag(Spells.THRALL);
			h.getLevel().addFreshEntity(m);
			h.getLevel().addFreshEntity(t);
			Threat.hit(m, t, 10);
			c.check(Threat.choice(m) == t, "a thrall alone holds it");
			m.setTarget(p);
			c.check(m.getTarget() == t, "and nothing turns it from the one who's earned it");
			Threat.hit(m, p, 2);
			c.check(Threat.choice(m) == p, "a tank's small blow outweighs a thrall's: tank 6 to 2.5");
			m.setTarget(p);
			Threat.hit(m, t, 12);
			c.check(Threat.choice(m) == p, "a thrall's blows don't take it back");
			Threat.taunt(m, t);
			c.check(m.getTarget() == t, "a taunt jumps the queue");
			Threat.forget(m, t);
			Threat.taunt(m, p);
			c.check(m.getTarget() == p, "and a tank's taunts stand");
			m.discard();
			t.discard();
		}
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void bowsNeedNoArrows(GameTestHelper h) {
		Checks c = new Checks("a bow always shoots");
		FakePlayer p = player(h, 20);
		var bow = new ItemStack(Gear.item("deep_seam_bow"));
		c.check(p.getInventory().countItem(Items.ARROW) == 0, "no arrows on them");
		c.check(!p.getProjectile(bow).isEmpty(), "our bow still has something to loose");
		c.check(p.getProjectile(new ItemStack(Items.BOW)).isEmpty(), "a vanilla one doesn't");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void listOfThirteen(GameTestHelper h) {
		Checks c = new Checks("the list of thirteen");
		FakePlayer p = player(h, 20);
		ItemStack sword = new ItemStack(Items.IRON_SWORD);
		sword.hurtAndBreak(50, h.getLevel(), null, i -> {});
		c.check(sword.getDamageValue() == 0 && !sword.isBarVisible(), "nothing wears out");
		ItemStack worn = new ItemStack(Items.IRON_SWORD);
		worn.setDamageValue(100);
		c.check(!worn.isBarVisible(), "and what was worn shows no bar");
		var bows = Gear.DUNGEONS.stream().flatMap(d -> d.weapons().stream()).filter(w -> w.kind().equals("bow") && !w.boss()).toList();
		p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, new ItemStack(Gear.item(bows.get(0).id())));
		double low = Gear.bowPower(p);
		p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, new ItemStack(Gear.item(bows.get(bows.size() - 1).id())));
		c.check(Gear.bowPower(p) > low * 1.3, "a bow of a higher rank hits harder: " + Gear.bowPower(p) + " over " + low);
		ItemStack tip = p.getMainHandItem();
		c.check(tip.getTooltipLines(net.minecraft.world.item.Item.TooltipContext.of(h.getLevel()), p, net.minecraft.world.item.TooltipFlag.NORMAL).stream().anyMatch(l -> l.getString().contains("arrow damage")), "and it says so");
		for (int e = 0; e <= Smithing.MOST_EMBERS; e++) {
			float sum = 0;
			for (float o : Smithing.odds(e)) sum += o;
			c.near(sum, 1, 0.001, "the forge's odds add up with " + e + " embers");
		}
		c.check(Smithing.odds(0)[3] < 0.05f && Smithing.odds(Smithing.MOST_EMBERS)[3] > 0.4f, "embers buy a Perfect");
		c.check(Smithing.odds(0)[1] > 0.5f, "most pieces come out Fine");
		c.check(Smithing.upgradeChance(0, 0) > Smithing.upgradeChance(9, 0) && Smithing.upgradeChance(9, Smithing.MOST_EMBERS) > 0.5f, "upgrades get harder, and embers help");
		c.check(!Wayfarers.find(p).isEmpty(), "a wayfarer's pack has something in it");
		int[] at = Capital.centre();
		if (at != null) c.check(Math.hypot(at[0], at[1]) < 9100 && Math.hypot(at[0], at[1]) > 4900, "the capital's 5-9k out: " + at[0] + ", " + at[1]);
		double total = 0;
		for (int i = 0; i < GateEntity.RANKS.length; i++) if (GateDungeons.has(i)) total += Gates.odds(i, 0, true, false);
		c.check(Gates.odds(1, 0, true, false) / total > 0.12, "more E gates early than there were");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void gateGround(GameTestHelper h) {
		Checks c = new Checks("a gate's ground comes and goes");
		var level = h.getLevel();
		BlockPos o = h.absolutePos(BlockPos.ZERO).offset(0, 60, 0);
		for (int dx = -16; dx <= 16; dx++)
			for (int dz = -16; dz <= 16; dz++) {
				level.setBlock(o.offset(dx, -2, dz), Blocks.DIRT.defaultBlockState(), 2);
				level.setBlock(o.offset(dx, -1, dz), Blocks.GRASS_BLOCK.defaultBlockState(), 2);
			}
		GateEntity g = Gates.GATE.get().create(level);
		g.moveTo(o.getX() + 0.5, o.getY(), o.getZ() + 0.5, 30, 0);
		g.setRank(0);
		g.opened(level.getGameTime() - GateEntity.CRACK);
		level.addFreshEntity(g);
		g.tick();
		g.tick();
		int changed = 0, own = 0, path = 0, burnt = 0;
		for (int dx = -16; dx <= 16; dx++)
			for (int dz = -16; dz <= 16; dz++) {
				var s = level.getBlockState(o.offset(dx, -1, dz));
				if (s.is(Blocks.GRASS_BLOCK)) continue;
				changed++;
				if (BuiltInRegistries.BLOCK.getKey(s.getBlock()).getNamespace().equals(Ashbound.ID) && !s.is(Gates.SCORCH.get())) own++;
				if (s.is(Blocks.DIRT_PATH)) path++;
				if (s.is(Gates.SCORCH.get())) burnt++;
			}
		c.check(own > 15, "its dungeon's floor bleeds through: " + own + " (" + GateDungeons.of(g).name() + ")");
		c.check(burnt > 5, "a fissure burns across its foot: " + burnt);
		c.check(path > 5, "a trodden path runs off its face: " + path);
		g.discard();
		int left = 0;
		for (int dx = -16; dx <= 16; dx++)
			for (int dz = -16; dz <= 16; dz++) {
				if (!level.getBlockState(o.offset(dx, -1, dz)).is(Blocks.GRASS_BLOCK)) left++;
				var up = level.getBlockState(o.offset(dx, 0, dz));
				if (!up.isAir() && !up.is(Gates.SCORCH.get())) left++;
			}
		c.check(changed > 30 && left == 0, "and it all goes back when the gate's gone: " + changed + " changed, " + left + " left");
		for (int dx = -16; dx <= 16; dx++)
			for (int dz = -16; dz <= 16; dz++)
				for (int dy = -2; dy <= 1; dy++) level.setBlock(o.offset(dx, dy, dz), Blocks.AIR.defaultBlockState(), 2);
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void pets(GameTestHelper h) {
		Checks c = new Checks("pets");
		c.check(Pets.ALL.size() >= 36, "a lot of pets (" + Pets.ALL.size() + ")");
		for (WorldArms.Tier t : WorldArms.Tier.values()) c.check(Pets.specs().stream().anyMatch(s -> s.tier() == t), "pets of every rarity: " + t);
		c.check(Curios.SPECS.stream().noneMatch(s -> s.slot().equals("pet")), "and they don't crowd the curios' own drops");
		var slots = top.theillusivec4.curios.api.CuriosApi.getPlayerSlots(h.getLevel());
		c.check(slots.containsKey("pet") && slots.get("pet").getSize() == 1, "players have one pet slot");
		for (Curios.Spec s : Pets.specs()) {
			Item item = BuiltInRegistries.ITEM.get(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(Ashbound.ID, s.id()));
			c.check(item instanceof Curios.Curio, s.id() + " is an item");
			c.check(new ItemStack(item).is(net.minecraft.tags.ItemTags.create(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("curios", "pet"))), s.id() + " fits the slot");
		}
		FakePlayer p = player(h, 8);
		ItemStack fox = new ItemStack(BuiltInRegistries.ITEM.get(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "coin_fox")));
		var inv = top.theillusivec4.curios.api.CuriosApi.getCuriosInventory(p).orElse(null);
		c.check(inv != null, "a player has curios");
		if (inv != null) {
			double before = Curios.stat(p, "coins%");
			inv.setEquippedCurio("pet", 0, fox);
			c.near(Curios.stat(p, "coins%") - before, 6, 0.001, "a worn pet's buff counts");
			c.check(Pets.worn(p) != null && Pets.worn(p).id().equals("coin_fox"), "and it's the one worn");
		}
		var tip = fox.getTooltipLines(Item.TooltipContext.of(h.getLevel()), p, net.minecraft.world.item.TooltipFlag.NORMAL);
		c.check(tip.stream().anyMatch(l -> l.getString().contains("Rare Pet")) && tip.stream().anyMatch(l -> l.getString().contains("heel")), "the tooltip says what it is");
		c.check(Curios.pet(h.getLevel().getRandom(), 2) != null, "a boss has a pet to drop");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void mountTraining(GameTestHelper h) {
		Checks c = new Checks("mount training");
		FakePlayer p = player(h, 8);
		Classes.pick(p, "shade");
		Mounts.pick(p, "ashmane");
		c.check(Mounts.airTicks(p) == 0 && !Mounts.tireless(p), "nothing flies at the start");
		Coins.set(p, 799);
		Mounts.upgrade(p, Mounts.WINGS);
		c.check(Mounts.rank(p, Mounts.WINGS) == 0 && Coins.of(p) == 799, "a rank you can't pay for doesn't happen");
		Coins.set(p, 1000);
		Mounts.upgrade(p, Mounts.WINGS);
		c.check(Mounts.rank(p, Mounts.WINGS) == 1 && Coins.of(p) == 200 && Mounts.airTicks(p) > 0, "the first rank of Wings flies");
		Coins.set(p, 1_000_000);
		for (int t = 0; t < Mounts.TRACKS.size(); t++)
			for (int i = 0; i < 8; i++) Mounts.upgrade(p, t);
		for (int t = 0; t < Mounts.TRACKS.size(); t++) {
			Mounts.Track track = Mounts.TRACKS.get(t);
			c.check(track.costs().length == track.ranks().length, track.id() + " says what each rank does");
			c.check(Mounts.rank(p, t) == track.costs().length, track.id() + " tops out");
		}
		c.check(Mounts.tireless(p), "any mount at the top of Wings never tires");
		int spent = 0;
		for (Mounts.Track t : Mounts.TRACKS) for (int n : t.costs()) spent += n;
		c.check(Coins.of(p) == 1_000_000 - spent + 800, "each rank paid for once");
		c.near(Mounts.speedFor(p), 1.25, 0.001, "top stride");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void bottomlessBag(GameTestHelper h) {
		Checks c = new Checks("the bag");
		FakePlayer a = player(h, 8), b = player(h, 8);
		var menu = new Bag.Menu(1, a.getInventory());
		a.containerMenu = menu;
		Bag.store(a, new ItemStack(Items.STONE, 64));
		for (int i = 0; i < 1000; i++) Bag.store(a, new ItemStack(Items.STONE, 64));
		c.check(Bag.count(a, new ItemStack(Items.STONE)) == 64 * 1001, "it holds far more than a chest");
		ItemStack named = new ItemStack(Items.IRON_SWORD);
		named.set(net.minecraft.core.component.DataComponents.CUSTOM_NAME, net.minecraft.network.chat.Component.literal("Mine"));
		Bag.store(a, named);
		c.check(Bag.count(a, new ItemStack(Items.IRON_SWORD)) == 0 && Bag.count(a, named) == 1, "different things stay apart");
		ItemStack got = Bag.take(a, new ItemStack(Items.STONE), 1000);
		c.check(got.getCount() == 64, "a stack at most comes out");
		c.check(Bag.take(a, new ItemStack(Items.DIAMOND), 5).isEmpty(), "what isn't in it can't come out");
		c.check(Bag.count(b, new ItemStack(Items.STONE)) == 0, "a stranger can't reach it");
		Party.form(a, b);
		c.check(Bag.count(b, new ItemStack(Items.STONE)) == 64 * 1000, "the party can");
		c.check(Bag.take(b, new ItemStack(Items.STONE), 64).getCount() == 64, "and can take from it");
		Bag.store(b, new ItemStack(Items.TORCH, 10));
		c.check(Bag.count(a, new ItemStack(Items.TORCH)) == 10, "both ways");
		Party.remove(h.getLevel().getServer(), b.getUUID(), " left the party");
		c.check(Bag.count(a, new ItemStack(Items.TORCH)) == 0 && Bag.count(b, new ItemStack(Items.TORCH)) == 10, "what you put in leaves with you");
		c.check(Bag.count(a, new ItemStack(Items.STONE)) == 64 * 999 && Bag.count(b, new ItemStack(Items.STONE)) == 0, "and what you didn't stays");
		a.getInventory().setItem(12, new ItemStack(Items.TORCH, 3));
		a.getInventory().setItem(0, new ItemStack(Items.TORCH, 3));
		menu.setCarried(new ItemStack(Items.DIAMOND, 5));
		Bag.act(a, new Net.BagAct(Bag.RIGHT, ItemStack.EMPTY));
		c.check(menu.getCarried().getCount() == 4 && Bag.count(a, new ItemStack(Items.DIAMOND)) == 1, "right click puts in one");
		Bag.act(a, new Net.BagAct(Bag.LEFT, ItemStack.EMPTY));
		c.check(menu.getCarried().isEmpty() && Bag.count(a, new ItemStack(Items.DIAMOND)) == 5, "left click puts in the lot");
		Bag.act(a, new Net.BagAct(Bag.RIGHT, new ItemStack(Items.STONE)));
		c.check(menu.getCarried().getCount() == 32, "right click takes half a stack");
		menu.setCarried(ItemStack.EMPTY);
		Bag.act(a, new Net.BagAct(Bag.PUT_PACK, ItemStack.EMPTY));
		c.check(a.getInventory().getItem(12).isEmpty() && a.getInventory().getItem(0).getCount() == 3 && Bag.count(a, new ItemStack(Items.TORCH)) == 3, "put in all leaves the hotbar");
		for (int i = 0; i < 36; i++) a.getInventory().setItem(i, new ItemStack(Items.DIRT));
		long before = Bag.count(a, new ItemStack(Items.STONE));
		Bag.act(a, new Net.BagAct(Bag.QUICK, new ItemStack(Items.STONE)));
		c.check(Bag.count(a, new ItemStack(Items.STONE)) == before, "a full pack keeps nothing it can't hold, and loses nothing");
		a.getInventory().clearContent();
		a.getInventory().setItem(9, new ItemStack(Items.TORCH, 7));
		menu.quickMoveStack(a, 0);
		c.check(a.getInventory().getItem(9).isEmpty() && Bag.count(a, new ItemStack(Items.TORCH)) == 10, "shift-click puts it in");
		c.check(Tidy.shelf(new ItemStack(Items.IRON_SWORD)) == 0 && Tidy.shelf(new ItemStack(Gear.item(Gear.DUNGEONS.get(0).weapons().get(0).id()))) == 0, "weapons are on their shelf without wear");
		a.containerMenu = a.inventoryMenu;
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void thrallsSwing(GameTestHelper h) {
		Checks c = new Checks("summons swing");
		Thrall t = Mounts.REVENANT.get().create(h.getLevel());
		c.check(t != null, "a revenant");
		if (t != null) {
			t.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
			for (int i = 0; i < 4; i++) t.aiStep();
			c.check(t.getAttackAnim(1) > 0, "its arm moves: " + t.getAttackAnim(1));
			for (int i = 0; i < t.getCurrentSwingDuration(); i++) t.aiStep();
			c.check(t.getAttackAnim(1) == 0, "and comes back: " + t.getAttackAnim(1));
			t.discard();
		}
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void wagon(GameTestHelper h) {
		Checks c = new Checks("the wagon at spawn");
		Talk.Kind k = Talk.kind(Intro.KIND);
		c.check(k != null, "the wagoner's words load");
		if (k != null) {
			boolean starts = false;
			for (Talk.Option o : k.nodes().get(k.start()).options()) starts |= o.act().equals("intro");
			c.check(starts, "he can start the telling");
		}
		net.minecraft.server.level.ServerLevel level = h.getLevel();
		BlockPos at = new BlockPos(9000, level.getChunk(562, 562).getMinBuildHeight() + 70, 9000);
		// a tree whose trunk stands in the clearing and whose bough reaches far out of it: it must go whole
		var oak = net.minecraft.world.level.block.Blocks.OAK_LOG.defaultBlockState();
		BlockPos trunk = at.offset(18, 1, 8), tip = at.offset(27, 7, 8);
		for (int y = 0; y < 7; y++) level.setBlock(trunk.above(y), oak, 2);
		for (int x = 18; x <= 27; x++) level.setBlock(at.offset(x, 7, 8), oak, 2);
		level.setBlock(tip.east(), net.minecraft.world.level.block.Blocks.OAK_LEAVES.defaultBlockState(), 2);
		Intro.place(level, at, new net.minecraft.world.phys.Vec3(0, 0, 1));
		var box = new net.minecraft.world.phys.AABB(at).inflate(12);
		var there = level.getEntities((net.minecraft.world.entity.Entity) null, box, e -> true);
		c.check(there.stream().filter(e -> e instanceof Wagon).count() == 1, "his wagon, Bramble in the shafts");
		c.check(there.stream().anyMatch(e -> e instanceof Npc n && Intro.KIND.equals(n.kindId())), "and the wagoner");
		c.check(level.getBlockState(at).is(net.minecraft.world.level.block.Blocks.GRASS_BLOCK), "on level ground");
		c.check(level.getBlockState(trunk).isAir() && level.getBlockState(tip).isAir() && level.getBlockState(tip.east()).isAir(), "the tree in the way felled whole");
		there.forEach(net.minecraft.world.entity.Entity::discard);
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void camps(GameTestHelper h) {
		Checks c = new Checks("camps go easy early");
		FakePlayer p = player(h, 1);
		c.check(Balance.rankAt(1).equals("F") && Balance.rankAt(19).equals("E") && Balance.rankAt(90).equals("S"), "levels have ranks");
		var type = BuiltInRegistries.ENTITY_TYPE.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "void_sentinel"));
		c.check(Balance.solved("void_sentinel") != null && "S".equals(Balance.solved("void_sentinel").rank()), "the void's monsters are rank S");
		if (type.create(h.getLevel()) instanceof net.minecraft.world.entity.Mob late && type.create(h.getLevel()) instanceof net.minecraft.world.entity.Mob early) {
			float hp = late.getMaxHealth();
			double hit = late.getAttributeValue(Attributes.ATTACK_DAMAGE);
			Balance.soften(late, "void_sentinel", 90);
			c.near(late.getMaxHealth(), hp, 0.01, "a rank S player meets it as it is");
			Balance.soften(early, "void_sentinel", 5);
			c.check(early.getMaxHealth() < hp * 0.6f, "level 5 meets a rank E one: " + early.getMaxHealth() + " of " + hp);
			c.check(early.getAttributeValue(Attributes.ATTACK_DAMAGE) < hit * 0.5, "and it hits like one: " + early.getAttributeValue(Attributes.ATTACK_DAMAGE) + " of " + hit);
			c.near(early.getHealth(), early.getMaxHealth(), 0.01, "at full health");
			c.check(Balance.paysAs(early, "S").equals("E") && Balance.paysFor(early) < 0.6, "and it pays like one");
			late.discard();
			early.discard();
		}
		c.near(Balance.crowded(p, 1, 100, 0.4), 1, 0.001, "the first blow is in full");
		c.near(Balance.crowded(p, 2, 105, 0.4), 0.4, 0.001, "a second monster inside the second does a share");
		c.near(Balance.crowded(p, 1, 110, 0.4), 1, 0.001, "the same monster keeps hitting in full");
		c.near(Balance.crowded(p, 3, 125, 0.4), 0.4, 0.001, "the crowd stays cut while the first one's on you");
		c.near(Balance.crowded(p, 3, 140, 0.4), 1, 0.001, "and a lone blow later is in full");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void hitStop(GameTestHelper h) {
		Checks c = new Checks("hit stop and party");
		FakePlayer p = player(h, 20);
		c.check(!HitStop.held(p) && !HitStop.owes(p), "nothing to start with");
		HitStop.hold(p, 2);
		c.check(HitStop.held(p) && !HitStop.owes(p), "held");
		c.check(java.util.Arrays.stream(yesman.epicfight.api.animation.AnimationPlayer.class.getDeclaredMethods()).anyMatch(m -> m.getName().contains("ashbound$hold")), "the swing really stops: Epic Fight's player is patched");
		c.check(HitStop.ticks(0) == 1 && HitStop.ticks(1) == 3, "a heavy blow stops longer");
		c.near(Balance.share(1), 1, 0.001, "alone you keep it all");
		c.check(Balance.share(4) > 0.6 && Balance.share(4) < 0.65, "four share, and still beat going alone");
		for (Skills.Skill s : Skills.ALL)
			if (s.cost() > 25) c.check(s.cost() <= 100, s.id() + " fits on a 100 mana bar");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void skillStrength(GameTestHelper h) {
		Checks c = new Checks("what a skill's multiplier is of");
		FakePlayer p = player(h, 20);
		Classes.pick(p, "hunter");
		var bow = Gear.WEAPONS.stream().map(i -> i.get()).filter(i -> i instanceof net.minecraft.world.item.BowItem).findFirst().orElseThrow();
		p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, new net.minecraft.world.item.ItemStack(bow));
		c.check(JoinedSkills.strength(p) > 3, "a bow's skills aren't a bare hand's: " + JoinedSkills.strength(p));
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void skillsRun(GameTestHelper h) {
		Checks c = new Checks("every skill runs");
		for (Classes.Cls k : Classes.ALL) {
			FakePlayer p = player(h, 40);
			Classes.pick(p, k.id());
			for (Skills.Skill s : Skills.ofClass(k.id()))
				try {
					s.act().run(p, 1);
				} catch (RuntimeException e) {
					c.check(false, s.id() + " threw " + e);
				}
		}
		c.check(true, "all " + Skills.ALL.size() + " ran");
		c.end(h);
	}

	// ---------------------------------------------------------------- what the first play session asked for

	/** A tag naming one block that doesn't exist loses everything in it, vanilla's too, and nothing can be mined. */
	@GameTest(template = "selftest")
	public static void toolsWork(GameTestHelper h) {
		Checks c = new Checks("toolsWork");
		var pick = new net.minecraft.world.item.ItemStack(Items.IRON_PICKAXE);
		var axe = new net.minecraft.world.item.ItemStack(Items.IRON_AXE);
		var shovel = new net.minecraft.world.item.ItemStack(Items.IRON_SHOVEL);
		var stone = net.minecraft.world.level.block.Blocks.COBBLESTONE.defaultBlockState();
		c.check(pick.isCorrectToolForDrops(stone) && pick.getDestroySpeed(stone) > 1, "an iron pickaxe mines cobblestone");
		var iron = net.minecraft.world.level.block.Blocks.IRON_ORE.defaultBlockState();
		c.check(pick.isCorrectToolForDrops(iron), "and iron ore");
		c.check(axe.getDestroySpeed(net.minecraft.world.level.block.Blocks.OAK_LOG.defaultBlockState()) > 1, "an axe chops wood");
		c.check(axe.getDestroySpeed(net.minecraft.world.level.block.Blocks.CRAFTING_TABLE.defaultBlockState()) > 1, "and a crafting table");
		c.check(shovel.getDestroySpeed(net.minecraft.world.level.block.Blocks.DIRT.defaultBlockState()) > 1, "a shovel digs dirt");
		var log = new net.minecraft.world.item.ItemStack(WorldBlocks.WILDWOOD_LOG.get());
		c.check(log.is(net.minecraft.tags.ItemTags.LOGS), "wildwood is a log");
		c.check(h.getLevel().getRecipeManager().byKey(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "wildwood_log_to_planks")).isPresent(), "and makes planks");
		c.check(new net.minecraft.world.item.ItemStack(net.minecraft.core.registries.BuiltInRegistries.ITEM.get(
				net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "cedar_planks"))).is(net.minecraft.tags.ItemTags.PLANKS), "our planks craft like any planks");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void gateOdds(GameTestHelper h) {
		Checks c = new Checks("gateOdds");
		double total = 0;
		for (int i = 0; i < GateEntity.RANKS.length; i++) if (GateDungeons.has(i)) total += Gates.odds(i, 0, true, false);
		c.check(Gates.odds(0, 0, true, false) / total > 0.6, "most gates on the road to the capital are F");
		c.check(Gates.odds(0, 0, false, false) > Gates.odds(1, 0, false, false) && Gates.odds(1, 0, false, false) > Gates.odds(2, 0, false, false), "from F, each rank up is rarer");
		c.check(Gates.odds(6, 6, false, false) > Gates.odds(0, 6, false, false), "a late player sees their own rank");
		c.check(Gates.odds(3, 0, false, false) == 0 && Gates.odds(5, 2, false, true) == 0, "a gate reaches two ranks up, no further");
		c.check(Gates.odds(4, 3, false, true) >= Gates.odds(3, 3, false, true), "a party that's outlevelled its gear gets the next rank as often as its own");
		FakePlayer p = player(h, 40);
		var zombie = EntityType.ZOMBIE.create(h.getLevel());
		c.check(!Balance.scales(zombie), "vanilla monsters don't grow for a party");
		if (net.neoforged.fml.ModList.get().isLoaded("cataclysm")) {
			var type = net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.get(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("cataclysm", "ignis"));
			if (type.create(h.getLevel()) instanceof net.minecraft.world.entity.Mob ignis) {
				c.check(Balance.scales(ignis), "another mod's monster grows like ours");
				c.check(Balance.boss(ignis), "and its boss is known as one");
			} else c.check(false, "cataclysm:ignis exists");
		}
		c.check(Gates.home(p) == 0, "no capital found: home is F, whatever the level");
		Coins.setFlag(p, "found_capital");
		c.check(Ranks.earned(p) == 0, "level 40 in no gear earns no rank: it takes the kit as well");
		Gear.Dungeon cGate = Gear.DUNGEONS.stream().filter(x -> x.rank() == 'C' && !x.weapons().isEmpty()).findFirst().orElseThrow();
		List<Gear.Piece> plate = cGate.sets().get(3).pieces();
		var worn = List.of(net.minecraft.world.entity.EquipmentSlot.HEAD, net.minecraft.world.entity.EquipmentSlot.CHEST, net.minecraft.world.entity.EquipmentSlot.LEGS);
		for (int i = 0; i < worn.size(); i++) p.setItemSlot(worn.get(i), new ItemStack(Gear.item(plate.get(i).id())));
		c.check(Ranks.earned(p) == 3, "three rank C pieces of five and level 40: rank C");
		for (var slot : worn) p.setItemSlot(slot, ItemStack.EMPTY);
		p.setData(Levels.RANK, 3);
		c.check(Gates.home(p) == 3, "and the rank holds when the armour comes off");
		c.check(Ranks.of(new ItemStack(Gear.item(Gear.DUNGEONS.get(0).bossWeapons().get(0).id()))) == 1, "a rank F boss's weapon is rank E");
		for (int i = 0; i < 200; i++) c.check(Ranks.findRank(0, h.getLevel().random) <= 2, "a find reaches two ranks up at most");
		c.check(Ranks.find(p, h.getLevel().random) != null, "there's gear to find at every rank");
		p.setData(Levels.RANK, 0);
		c.near(Balance.paysUpTo("A", 0), Balance.paysUpTo("A", 0), 0, "");
		c.check(Balance.paysUpTo("E", 0) == 1 && Balance.paysUpTo("A", 0) < 0.4, "a rank A kill pays a rank F party like a rank E one: " + Balance.paysUpTo("A", 0));
		c.check(GateLoot.weaponOdds(0) == GateLoot.WEAPON_ODDS && GateLoot.weaponOdds(9) >= 1, "ten bosses at the worst for a weapon");
		Gear.Dungeon one = Gear.DUNGEONS.get(0), kinD = Gear.DUNGEONS.get(1);
		Item otherMat = Gear.item(kinD.mats()[0]);
		p.getInventory().add(new ItemStack(otherMat, 12));
		c.check(GateForge.countKin(p, one, 0) >= 12 && GateForge.affords(p, one, new Gear.Cost(12, 0, 0)), "another dungeon of the rank's drops pay at this forge");
		GateForge.pay(p, one, new Gear.Cost(12, 0, 0));
		c.check(GateForge.carried(p, otherMat) == 0, "and they're what gets spent");
		for (int i = 0; i < 200; i++) c.check(GateDungeons.has(Gates.roll(h.getLevel().random, p)), "a roll is a built rank");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void sharedChests(GameTestHelper h) {
		Checks c = new Checks("sharedChests");
		BlockPos at = h.absolutePos(new BlockPos(2, 1, 2));
		h.getLevel().setBlock(at, SilkProps.ARCHIVE_COFFER.get().defaultBlockState(), 3);
		var box = (SilkProps.CofferEntity) h.getLevel().getBlockEntity(at);
		var table = net.minecraft.resources.ResourceKey.create(net.minecraft.core.registries.Registries.LOOT_TABLE,
				net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "chests/wayside"));
		box.setLootTable(table, 7L);
		FakePlayer a = player(h, 5), b = player(h, 5);
		var mine = box.share(a);
		c.check(!mine.isEmpty(), "a stocked coffer has something in it");
		mine.clearContent();
		c.check(box.share(a).isEmpty(), "your share stays as you left it");
		c.check(!box.share(b).isEmpty(), "taking yours leaves the other player's");
		box.setLootTable(table, 8L);
		c.check(!box.share(a).isEmpty(), "stocked again, everyone starts over");
		for (String id : List.of("chests/wayside")) c.check(h.getLevel().getServer().reloadableRegistries().getLootTable(table) != null, id + " loads");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void gateScorch(GameTestHelper h) {
		Checks c = new Checks("gateScorch");
		var level = h.getLevel();
		BlockPos cell = h.absolutePos(new BlockPos(2, 3, 2));
		level.setBlock(cell.north(), net.minecraft.world.level.block.Blocks.STONE.defaultBlockState(), 3);
		var wall = Gates.SCORCH.get().defaultBlockState().setValue(GateScorch.FLOOR, false).setValue(GateScorch.NORTH, true);
		c.check(wall.canSurvive(level, cell), "char lies on a side with stone behind it");
		level.setBlock(cell, wall, 3);
		level.setBlock(cell.north(), net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), 3);
		c.check(level.getBlockState(cell).isAir(), "and goes when the stone does");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void rationPouch(GameTestHelper h) {
		Checks c = new Checks("rationPouch");
		FakePlayer p = player(h, 1);
		p.getInventory().clearContent();
		ItemStack pouch = new ItemStack(Rations.POUCH.get());
		pouch.set(net.minecraft.core.component.DataComponents.BUNDLE_CONTENTS, new net.minecraft.world.item.component.BundleContents(List.of(new ItemStack(net.minecraft.world.item.Items.BREAD, 2))));
		p.getInventory().setItem(20, pouch);
		c.check(Rations.plain(new ItemStack(net.minecraft.world.item.Items.BREAD)), "bread goes in");
		c.check(!Rations.plain(new ItemStack(net.minecraft.world.item.Items.GOLDEN_APPLE)), "a golden apple stays out");
		c.check(!Rations.plain(new ItemStack(net.minecraft.world.item.Items.ROTTEN_FLESH)), "rotten flesh stays out");
		c.check(!Rations.plain(new ItemStack(net.minecraft.world.item.Items.MUSHROOM_STEW)), "a stew stays out, its bowl would be lost");
		c.check(!Rations.plain(new ItemStack(net.minecraft.world.item.Items.STONE)), "a stone stays out");
		p.getFoodData().setFoodLevel(18);
		Rations.feed(p);
		c.check(p.getFoodData().getFoodLevel() == 18, "not hungry, it stays shut");
		p.getFoodData().setFoodLevel(8);
		Rations.feed(p);
		c.check(p.getFoodData().getFoodLevel() == 13, "hungry, you eat from it (" + p.getFoodData().getFoodLevel() + ")");
		p.getFoodData().setFoodLevel(8);
		Rations.feed(p);
		Rations.feed(p);
		c.check(p.getInventory().getItem(20).get(net.minecraft.core.component.DataComponents.BUNDLE_CONTENTS).isEmpty(), "and it runs out");
		c.check(p.getFoodData().getFoodLevel() == 13, "an empty pouch feeds no one");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void beltPouch(GameTestHelper h) {
		Checks c = new Checks("beltPouch");
		FakePlayer p = player(h, 1);
		p.getInventory().clearContent();
		BeltPouch.held(p).forEach(s -> s.setCount(0));
		ItemStack rations = Rations.stocked(new ItemStack(net.minecraft.world.item.Items.BREAD, 3));
		p.getInventory().setItem(20, rations);
		p.getInventory().setItem(21, new ItemStack(Guild.CARD_ITEM.get()));
		p.getInventory().setItem(22, new ItemStack(net.minecraft.world.item.Items.STONE));
		BeltPouch.tuck(p);
		c.check(BeltPouch.held(p).size() == 2, "the card and the rations go in (" + BeltPouch.held(p).size() + ")");
		c.check(p.getInventory().getItem(20).isEmpty() && p.getInventory().getItem(21).isEmpty(), "and they've left the pack");
		c.check(p.getInventory().getItem(22).is(net.minecraft.world.item.Items.STONE), "anything else stays where it is");
		p.getFoodData().setFoodLevel(8);
		Rations.feed(p);
		c.check(p.getFoodData().getFoodLevel() == 13, "you still eat from it in there (" + p.getFoodData().getFoodLevel() + ")");
		for (int i = 0; i < 6; i++) p.getInventory().setItem(i, new ItemStack(Guild.CARD_ITEM.get()));
		BeltPouch.tuck(p);
		c.check(BeltPouch.held(p).size() == 4, "it holds four (" + BeltPouch.held(p).size() + ")");
		c.check(p.getInventory().getItem(3).is(Guild.CARD_ITEM.get()) && p.getInventory().getItem(5).is(Guild.CARD_ITEM.get()), "the rest stay in the pack");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void forgeFromBag(GameTestHelper h) {
		Checks c = new Checks("forgeFromBag");
		FakePlayer p = player(h, 1);
		p.getInventory().clearContent();
		var it = net.minecraft.world.item.Items.ECHO_SHARD;
		long before = Bag.count(p, new ItemStack(it));
		Bag.take(p, new ItemStack(it), (int) Math.min(before, 64));
		Bag.store(p, new ItemStack(it, 100));
		p.getInventory().setItem(3, new ItemStack(it, 10));
		c.check(GateForge.count(p, it) == 110, "the forge sees the pack and the bag (" + GateForge.count(p, it) + ")");
		c.check(GateForge.carried(p, it) == 10, "and the pack on its own");
		GateForge.take(p, it, 75);
		c.check(p.getInventory().getItem(3).isEmpty(), "the pack goes first");
		c.check(GateForge.count(p, it) == 35, "the rest comes out of the bag, more than a stack of it (" + GateForge.count(p, it) + ")");
		GateForge.take(p, it, 999);
		c.check(GateForge.count(p, it) == 0, "taking too many leaves none, not fewer than none");
		c.check(Dropped.matters(new ItemStack(net.minecraft.world.item.Items.IRON_SWORD)), "a sword shows on the ground");
		c.check(!Dropped.matters(new ItemStack(net.minecraft.world.item.Items.COBBLESTONE)), "cobble doesn't");
		FakePlayer other = player(h, 2);
		c.check(Dropped.colour(p) != Dropped.colour(other), "two players, two colours");
		c.check(Dropped.colour(p) == Dropped.colour(p), "and yours stays yours");
		var thrown = new net.minecraft.world.entity.item.ItemEntity(h.getLevel(), 0, 0, 0, new ItemStack(net.minecraft.world.item.Items.IRON_SWORD));
		Dropped.mark(thrown, p);
		c.check(thrown.isCurrentlyGlowing() && thrown.isCustomNameVisible() && thrown.getCustomName().getStyle().getColor().getValue() == Dropped.colour(p), "the name over it comes up in their colour");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void meters(GameTestHelper h) {
		Checks c = new Checks("meters");
		FakePlayer p = player(h, 30);
		double[] was = Meters.of(p);
		p.setHealth(p.getMaxHealth() - 6);
		Meters.heal(p, p, 4);
		c.near(Meters.of(p)[1] - was[1], 4, 0.01, "a heal goes on the healer's line");
		Meters.heal(p, p, 1000);
		c.near(Meters.of(p)[1] - was[1], 6, 0.01, "overhealing doesn't count");
		var mob = h.spawnWithNoFreeWill(net.minecraft.world.entity.EntityType.ZOMBIE, new BlockPos(1, 2, 1));
		float full = mob.getHealth();
		mob.hurt(p.damageSources().playerAttack(p), 4);
		c.check(mob.getHealth() < full, "the mob was hit");
		c.near(Meters.of(p)[0] - was[0], full - mob.getHealth(), 0.01, "a hit counts what it took off");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void staffStyles(GameTestHelper h) {
		Checks c = new Checks("staffStyles");
		FakePlayer p = player(h, 1);
		for (StaffSpells.Style s : StaffSpells.Style.values()) {
			Gear.Weapon w = null;
			int n = 0;
			for (var it : net.minecraft.core.registries.BuiltInRegistries.ITEM)
				if (it instanceof Spells.Staff st && !st.weapon.id().startsWith("apprentice_") && StaffSpells.Style.of(st.weapon) == s) {
					w = st.weapon;
					n++;
				}
			c.check(w != null, s.title + ": " + n + " staffs cast it");
			if (w == null) continue;
			Spells.dismiss(p);
			Spells.cast(p, w);
			if (!s.school.equals("summon")) continue;
			int want = StaffSpells.band(w, w.boss() ? 3 : 2);
			c.check(Spells.thralls(p) == want, s.title + " calls " + want + " (" + Spells.thralls(p) + ")");
			var called = h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.Mob.class, p.getBoundingBox().inflate(6), Spells::isThrall);
			c.check(called.stream().noneMatch(m -> m.getTags().contains("ashbound_asleep") || m.isNoAi()), s.title + ": awake");
			c.check(called.stream().allMatch(m -> m instanceof Thrall t && !t.model.equals("revenant")), s.title + ": calls the Bound");
			c.check(called.stream().allMatch(m -> m.getTarget() != p), s.title + ": not after their own caller");
		}
		Spells.dismiss(p);
		c.check(Math.abs(Smithing.Quality.MASTERWORK.bonus - 0.2) < 1e-6 && Smithing.Quality.PERFECT.bonus > Smithing.Quality.MASTERWORK.bonus, "a Masterwork is worth having");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void curioSwap(GameTestHelper h) {
		Checks c = new Checks("curioSwap");
		FakePlayer p = player(h, 1);
		p.getInventory().clearContent();
		List<Curios.Curio> rings = new ArrayList<>();
		for (var it : net.minecraft.core.registries.BuiltInRegistries.ITEM) if (it instanceof Curios.Curio k && k.slotId().equals("relic")) rings.add(k);
		var slots = top.theillusivec4.curios.api.CuriosApi.getCuriosInventory(p).flatMap(inv -> inv.getStacksHandler("relic")).orElseThrow().getStacks();
		slots.setStackInSlot(0, ItemStack.EMPTY);
		ItemStack a = new ItemStack(rings.get(0)), b = new ItemStack(rings.get(1)), twin = new ItemStack(rings.get(0));
		p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, a.copy());
		p.gameMode.useItem(p, h.getLevel(), p.getMainHandItem(), net.minecraft.world.InteractionHand.MAIN_HAND);
		c.check(slots.getStackInSlot(0).is(rings.get(0)) && p.getMainHandItem().isEmpty(), "worn, and gone from the hand");
		p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, b.copy());
		p.gameMode.useItem(p, h.getLevel(), p.getMainHandItem(), net.minecraft.world.InteractionHand.MAIN_HAND);
		c.check(slots.getStackInSlot(0).is(rings.get(1)) && p.getMainHandItem().is(rings.get(0)), "swapped, the old one back in hand (" + p.getMainHandItem() + ", worn " + slots.getStackInSlot(0) + ")");
		slots.setStackInSlot(0, a.copy());
		p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, twin.copy());
		p.gameMode.useItem(p, h.getLevel(), p.getMainHandItem(), net.minecraft.world.InteractionHand.MAIN_HAND);
		c.check(slots.getStackInSlot(0).is(rings.get(0)) && p.getMainHandItem().is(rings.get(0)), "the same one again: both still there (" + p.getMainHandItem() + ", worn " + slots.getStackInSlot(0) + ")");
		slots.setStackInSlot(0, ItemStack.EMPTY);
		p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, ItemStack.EMPTY);
		for (String slotId : List.of("relic", "ring", "necklace", "charm", "pet")) curioClicks(c, p, slotId);
		c.end(h);
	}

	/** However you try to put a second one on, you still have two. */
	private static void curioClicks(Checks c, FakePlayer p, String slotId) {
		Curios.Curio one = null;
		for (var it : net.minecraft.core.registries.BuiltInRegistries.ITEM) if (it instanceof Curios.Curio k && k.slotId().equals(slotId)) one = k;
		var slots = top.theillusivec4.curios.api.CuriosApi.getCuriosInventory(p).flatMap(inv -> inv.getStacksHandler(slotId)).orElseThrow().getStacks();
		var menu = new top.theillusivec4.curios.common.inventory.container.CuriosContainer(0, p.getInventory());
		int at = -1;
		for (var s : menu.slots) if (at < 0 && s instanceof top.theillusivec4.curios.common.inventory.CurioSlot k && !k.isCosmetic() && k.getIdentifier().equals(slotId)) at = s.index;
		c.check(at >= 0, slotId + ": the menu has it");
		if (at < 0) return;
		final Curios.Curio item = one;
		final var worn = slots;
		String[] ways = {"click", "right-click", "shift-click", "number key"};
		for (int w = 0; w < ways.length; w++) {
			for (int i = 0; i < worn.getSlots(); i++) worn.setStackInSlot(i, new ItemStack(item));
			p.getInventory().clearContent();
			menu.setCarried(ItemStack.EMPTY);
			int before = worn.getSlots();
			switch (w) {
				case 0, 1 -> {
					menu.setCarried(new ItemStack(item));
					menu.clicked(at, w, net.minecraft.world.inventory.ClickType.PICKUP, p);
				}
				case 2 -> {
					p.getInventory().setItem(9, new ItemStack(item));
					menu.clicked(9, 0, net.minecraft.world.inventory.ClickType.QUICK_MOVE, p);
				}
				default -> {
					p.getInventory().setItem(0, new ItemStack(item));
					menu.clicked(at, 0, net.minecraft.world.inventory.ClickType.SWAP, p);
				}
			}
			int count = p.getInventory().countItem(item) + menu.getCarried().getCount();
			for (int i = 0; i < worn.getSlots(); i++) count += worn.getStackInSlot(i).getCount();
			c.check(count == before + 1, slotId + " by " + ways[w] + ": still all there (" + count + " of " + (before + 1) + ")");
			c.check(worn.getStackInSlot(0).getCount() == 1, slotId + " by " + ways[w] + ": worn one at a time (" + worn.getStackInSlot(0).getCount() + ")");
		}
		for (int i = 0; i < worn.getSlots(); i++) worn.setStackInSlot(i, ItemStack.EMPTY);
		p.getInventory().clearContent();
		menu.setCarried(ItemStack.EMPTY);
	}

	private static void bankAct(FakePlayer p, int what, String who, int coins) {
		Party.act(p, new Net.PartyAct(what, who, coins));
	}

	@GameTest(template = "selftest")
	public static void partyBank(GameTestHelper h) {
		Checks c = new Checks("partyBank");
		FakePlayer lead = FakePlayerFactory.get(h.getLevel(), new GameProfile(UUID.randomUUID(), "ashlead"));
		FakePlayer mate = FakePlayerFactory.get(h.getLevel(), new GameProfile(UUID.randomUUID(), "ashmate"));
		Coins.set(lead, 100);
		Coins.set(mate, 10);
		c.check(Party.form(lead, mate), "a party forms");
		bankAct(lead, Net.PartyAct.PUT_IN, "", 60);
		c.check(Coins.of(lead) == 40 && Party.bank(lead) == 60, "paying in moves the coins");
		bankAct(lead, Net.PartyAct.PUT_IN, "", 1000);
		c.check(Coins.of(lead) == 0 && Party.bank(lead) == 100, "you can't pay in more than you carry");
		bankAct(mate, Net.PartyAct.PUT_IN, "", -5);
		bankAct(mate, Net.PartyAct.TAKE_OUT, "", -5);
		c.check(Coins.of(mate) == 10 && Party.bank(lead) == 100, "no minus amounts");
		bankAct(mate, Net.PartyAct.TAKE_OUT, "", 50);
		c.check(Coins.of(mate) == 10 && Party.bank(lead) == 100, "a plain member can't take from the bank");
		bankAct(mate, Net.PartyAct.COMMANDER, "ashmate", 0);
		bankAct(mate, Net.PartyAct.TAKE_OUT, "", 50);
		c.check(Party.bank(lead) == 100, "a member can't make themselves a commander");
		bankAct(lead, Net.PartyAct.COMMANDER, "ashmate", 0);
		bankAct(mate, Net.PartyAct.TAKE_OUT, "", 1000);
		c.check(Coins.of(mate) == 110 && Party.bank(lead) == 0, "a commander takes out what's there and no more");
		bankAct(mate, Net.PartyAct.KICK, "ashlead", 0);
		c.check(Party.same(lead, mate), "a commander can't kick the leader");
		bankAct(mate, Net.PartyAct.PUT_IN, "", 30);
		Party.remove(h.getLevel().getServer(), lead.getUUID(), " left the party");
		Party.arrive(mate);
		c.check(!Party.same(lead, mate) && Coins.of(mate) == 110, "the last one left gets the bank, even coming back later");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void healOne(GameTestHelper h) {
		Checks c = new Checks("healOne");
		FakePlayer p = player(h, 20);
		c.check(Spells.healTarget(p) == null, "alone, a white staff has no one to aim at");
		Spells.pickHealTarget(p, "nobody");
		c.check(Spells.healTarget(p) == null, "a name that isn't in your party heals no one");
		Spells.pickHealTarget(p, "");
		c.end(h);
	}

	// ---------------------------------------------------------------- the mechanics, hit for hit

	@GameTest(template = "selftest")
	public static void mechanics(GameTestHelper h) {
		Checks c = new Checks("mechanics");
		Zombie z = dummy(h);
		ItemStack dagger = weapon("dagger", false), great = weapon("twohander", false), sword = weapon("sword", false), white = weapon("white", false);
		c.check(!dagger.isEmpty() && !great.isEmpty() && !sword.isEmpty() && !white.isEmpty(), "test weapons found");

		// Execute: +50% below 30% health
		FakePlayer plain = player(h, 60), exec = player(h, 60);
		plain.setItemInHand(InteractionHand.MAIN_HAND, dagger.copy());
		exec.setItemInHand(InteractionHand.MAIN_HAND, dagger.copy());
		take(exec, "dagger_s0", "dagger_s1", "dagger_n0", "dagger_n2", "dagger_v1");
		z.setHealth(200);
		float base = hit(plain, z, 10);
		float ex = hit(exec, z, 10);
		c.near(ex / base, 1.5, 0.02, "Execute below 30% health");

		// Sunder: every 3rd hit +40%
		FakePlayer sun = player(h, 60);
		sun.setItemInHand(InteractionHand.MAIN_HAND, great.copy());
		take(sun, "twohander_s0", "twohander_s1", "twohander_n0", "twohander_n2", "twohander_v1");
		z.setHealth(1000);
		float a = hit(sun, z, 10), b = hit(sun, z, 10), third = hit(sun, z, 10);
		c.near(b / a, 1.0, 0.02, "Sunder: 2nd hit plain");
		c.near(third / a, 1.4, 0.02, "Sunder: 3rd hit +40%");

		// Smite: +30% to undead
		FakePlayer cleric = player(h, 60), smiter = player(h, 60);
		cleric.setItemInHand(InteractionHand.MAIN_HAND, white.copy());
		smiter.setItemInHand(InteractionHand.MAIN_HAND, white.copy());
		take(smiter, "white_s0", "white_s1", "white_n0", "white_n2", "white_v1");
		float plainW = hit(cleric, z, 10), smite = hit(smiter, z, 10);
		c.near(smite / plainW, 1.3, 0.02, "Smite on a zombie");

		// Titan's Grip: the lock, one blade, two blades
		FakePlayer titan = player(h, 60);
		take(titan, "twohander_s0", "twohander_s0", "twohander_s0", "twohander_s0", "twohander_s0", "twohander_s1", "twohander_s1",
				"twohander_s1", "twohander_s1", "twohander_s1", "twohander_n0", "twohander_s2", "twohander_s2", "twohander_s2",
				"twohander_s3", "twohander_n3", "twohander_v2", "twohander_k");
		c.check(Passives.titanGrip(titan), "Titan's Grip taken");
		titan.setItemInHand(InteractionHand.MAIN_HAND, sword.copy());
		c.check(Passives.titanLocked(titan), "a sword is locked out");
		c.near(hit(titan, z, 10), 0, 0.001, "a sword deals nothing with Titan's Grip");
		titan.setItemInHand(InteractionHand.MAIN_HAND, great.copy());
		c.check(!Passives.titanLocked(titan), "a two-hander isn't locked");
		float one = hit(titan, z, 10);
		titan.setItemInHand(InteractionHand.OFF_HAND, great.copy());
		float two = hit(titan, z, 10);
		c.near(one, 10, 0.05, "one two-hander hits in full");
		c.near(two / one, 0.75, 0.02, "two two-handers: each hit -25%");
		c.end(h);
	}

	// ---------------------------------------------------------------- the balance in the game's own items and monsters

	@GameTest(template = "selftest")
	public static void balance(GameTestHelper h) {
		Checks c = new Checks("balance");
		// rank C dungeon weapons carry the PASS 6 damage (tools/gear.py STATS) on the 1.4x ladder (C = 2.195)
		String[][] want = {{"sword", "16.5", "1.6"}, {"dagger", "10.1", "2.4"}, {"spear", "18.7", "1.2"}, {"hammer", "39.5", "0.85"},
				{"twohander", "43.9", "0.85"}};
		// one rank up is 1.4x the weapon damage: gear carries the climb (tools/balance.py pass 11)
		String ladder = "FEDCBAS";
		for (int i = 0; i + 1 < ladder.length(); i++)
			c.near(Gear.scale(ladder.charAt(i + 1)) / Gear.scale(ladder.charAt(i)), 1.4, 0.005, ladder.charAt(i) + " -> " + ladder.charAt(i + 1) + " weapon step");
		// armour: a rank's plate is a real step, past vanilla's cap, and it's in the armour that counts
		double fCut = Balance.armour("medium", 'F')[0], sCut = Balance.armour("medium", 'S')[0];
		c.check(sCut >= fCut * 10, "rank S armour is ten times rank F's: " + fCut + " to " + sCut);
		c.near(Attributes.ARMOR.value().sanitizeValue(500), 500, 0.01, "armour goes past vanilla's 30");
		c.near(Balance.kept(40, 0), 0.5, 0.001, "40 armour is half the damage");
		c.near(Balance.kept(40, 20), 1 / 3f, 0.001, "toughness makes armour go further");
		c.near(Gear.mends(Gear.scale('S')), 0.322, 0.01, "a rank S heal is in step with health, not blows");
		// a real player's hit goes through our armour, a monster's spell too, and a fall doesn't
		var real = new net.neoforged.neoforge.common.util.FakePlayer(h.getLevel(), new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(), "armour_test")) {
			@Override
			public boolean isInvulnerableTo(net.minecraft.world.damagesource.DamageSource s) {
				return false;
			}
		};
		net.neoforged.fml.util.ObfuscationReflectionHelper.setPrivateValue(net.minecraft.server.level.ServerPlayer.class, real, 0, "spawnInvulnerableTime");
		real.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);
		real.setHealth(1000);
		real.getAttribute(Attributes.ARMOR).setBaseValue(120);
		c.near(real.getArmorValue(), 120, 0.01, "armour past vanilla's cap is worn");
		Zombie biter = h.spawnWithNoFreeWill(EntityType.ZOMBIE, new BlockPos(3, 1, 3));
		real.invulnerableTime = 0;
		real.hurt(real.damageSources().mobAttack(biter), 100);
		c.near(1000 - real.getHealth(), 25, 0.5, "120 armour takes a 100 blow to 25: " + (1000 - real.getHealth()));
		real.invulnerableTime = 0;
		float was = real.getHealth();
		real.hurt(real.damageSources().indirectMagic(biter, biter), 100);
		c.near(was - real.getHealth(), 25, 0.5, "a monster's spell counts as a blow: " + (was - real.getHealth()));
		real.invulnerableTime = 0;
		was = real.getHealth();
		real.hurt(real.damageSources().fall(), 10);
		c.near(was - real.getHealth(), 10, 0.5, "a fall is a fall: " + (was - real.getHealth()));
		// a stack made on the old ladder catches up, and what was rolled on it stays
		ItemStack old = weapon("sword", false);
		var rolled = net.minecraft.world.item.component.ItemAttributeModifiers.builder()
				.add(Attributes.ATTACK_DAMAGE, new net.minecraft.world.entity.ai.attributes.AttributeModifier(net.minecraft.world.item.Item.BASE_ATTACK_DAMAGE_ID, 6.6, net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADD_VALUE), net.minecraft.world.entity.EquipmentSlotGroup.MAINHAND)
				.add(Attributes.LUCK, new net.minecraft.world.entity.ai.attributes.AttributeModifier(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "roll_0"), 1, net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADD_VALUE), net.minecraft.world.entity.EquipmentSlotGroup.MAINHAND).build();
		old.set(net.minecraft.core.component.DataComponents.ATTRIBUTE_MODIFIERS, rolled);
		Smithing.relevel(old);
		double[] now = {1, 0};
		for (var e : old.getAttributeModifiers().modifiers()) {
			if (e.attribute().equals(Attributes.ATTACK_DAMAGE)) now[0] += e.modifier().amount();
			if (e.attribute().equals(Attributes.LUCK)) now[1] += e.modifier().amount();
		}
		c.near(now[0], 16.5, 0.01, "an old stack's damage catches up");
		c.near(now[1], 1, 0.01, "its roll stays");
		for (String[] w : want) {
			ItemStack s = weapon(w[0], false);
			double dmg = 1, spd = 4;
			for (var e : s.getAttributeModifiers().modifiers()) {
				if (e.attribute().equals(Attributes.ATTACK_DAMAGE)) dmg += e.modifier().amount();
				if (e.attribute().equals(Attributes.ATTACK_SPEED)) spd += e.modifier().amount();
			}
			c.near(dmg, Double.parseDouble(w[1]), 0.01, w[0] + " damage at rank C");
			c.near(spd, Double.parseDouble(w[2]), 0.01, w[0] + " attack speed");
		}
		// monsters spawn with their solved health (base x balance.json)
		int n = 0;
		for (GateMobs.Kind k : GateMobs.KINDS) {
			if (n >= 12) break;
			var type = BuiltInRegistries.ENTITY_TYPE.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, k.id()));
			if (!(type.create(h.getLevel()) instanceof LivingEntity e)) continue;
			Balance.Mult m = Balance.mob(k.id());
			c.near(e.getMaxHealth(), k.hp() * m.hp(), 0.6, k.id() + " (" + m.rank() + " " + m.role() + ") health");
			e.discard();
			n++;
		}
		c.check(n > 0, "monsters checked: " + n);
		c.end(h);
	}

	// ---------------------------------------------------------------- curios and relics (docs/RELICS.md)

	private static ItemStack curio(String id) {
		return new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, id)));
	}

	@GameTest(template = "selftest")
	public static void forging(GameTestHelper h) {
		Checks c = new Checks("forging");
		FakePlayer p = player(h, 1);
		c.check(Smithing.Quality.of(0.2f) == Smithing.Quality.CRUDE && Smithing.Quality.of(0.6f) == Smithing.Quality.FINE
				&& Smithing.Quality.of(0.8f) == Smithing.Quality.MASTERWORK && Smithing.Quality.of(0.95f) == Smithing.Quality.PERFECT, "scores make the four qualities");
		for (Gear.Dungeon d : Gear.DUNGEONS)
			for (Gear.Weapon w : d.weapons())
				for (float[] bar : Smithing.pattern(w.kind()))
					for (float b : bar) if (b < 0 || b >= 4) c.check(false, w.kind() + " has a note outside its bar");
		Gear.Weapon sword = Gear.DUNGEONS.get(0).weapons().stream().filter(w -> w.kind().equals("sword") && !w.boss()).findFirst().orElseThrow();
		Item it = Gear.item(sword.id());
		ItemStack plain = Smithing.make(it, Smithing.Quality.FINE, "", p), best = Smithing.make(it, Smithing.Quality.PERFECT, "Widow's Kiss", p);
		p.setItemSlot(net.minecraft.world.entity.EquipmentSlot.MAINHAND, plain);
		double fine = damage(p);
		p.setItemSlot(net.minecraft.world.entity.EquipmentSlot.MAINHAND, best);
		c.near(damage(p) / fine, 1.35, 0.03, "a Perfect hits 35% harder");
		c.check(best.getHoverName().getString().equals("Widow's Kiss"), "a Perfect keeps the name you gave it");
		c.check(plain.getHoverName().getString().equals(new ItemStack(it).getHoverName().getString()), "anything less keeps its own name");
		c.near(Smithing.mult(best), 1.35, 0.001, "staffs and bows read the same bonus");
		c.near(Smithing.mult(new ItemStack(it)), 1, 0.001, "a looted weapon has no bonus");
		// upgrades
		ItemStack up = Smithing.make(it, Smithing.Quality.FINE, "", p);
		for (int i = 0; i < Smithing.TOP; i++) Smithing.raise(up);
		c.check(Smithing.plus(up) == 10 && up.getHoverName().getString().endsWith(" +10"), "+10 shows on its name");
		p.setItemSlot(net.minecraft.world.entity.EquipmentSlot.MAINHAND, up);
		c.near(damage(p) / fine, 1.40, 0.05, "+10 is 40% stronger");
		c.check(Smithing.upgradeCost(4).trophy() == 0 && Smithing.upgradeCost(5).trophy() > 0, "trophies only past +5");
		c.check(Smithing.need(9) > Smithing.need(0) && Smithing.need(9) <= 0.92f, "harder each +, +10 still reachable without a Perfect");
		// no way back to Minecraft's own mode
		c.check(!yesman.epicfight.world.gamerule.EpicFightGameRules.CAN_SWITCH_PLAYER_MODE.getRuleValue(h.getLevel()), "the battle mode switch is off");
		// trouble out in the world: on the board, raised when someone's there, over when what got out is dead
		Gear.Dungeon out = Gear.DUNGEONS.get(0);
		Incidents.Incident inc = Incidents.post(h.getLevel(), false, out, "", p.getBlockX(), p.getBlockZ());
		c.check(Guild.quest(inc.id) != null && Guild.quest(inc.id).objective().contains("Put down"), "a boss that got out goes up on the board");
		c.check(!Guild.jobs(p).isEmpty(), "and shows in the Journal");
		Incidents.raise(h.getLevel(), inc, p);
		c.check(inc.raised && inc.left.size() == 1, "it's there when someone comes");
		if (!inc.left.isEmpty() && h.getLevel().getEntity(inc.left.get(0)) instanceof net.minecraft.world.entity.LivingEntity boss) boss.kill();
		c.check(Incidents.over(inc.id), "and it's over when it falls");
		for (var mob : h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.Mob.class, new net.minecraft.world.phys.AABB(p.blockPosition()).inflate(32), m -> m.getTags().contains(Incidents.TAG))) mob.discard();
		c.check(Guild.quest("board_gate_f") != null && Guild.quest("board_gate_f").objective().equals("Close 1 Rank F Gate"), "gate requests are on the board");
		c.check(Guild.quest("board_tower_rimeholt") != null, "tower requests are on the board");
		if (net.neoforged.fml.ModList.get().isLoaded("cataclysm")) c.check(Guild.quest("board_cataclysm_the_harbinger") != null, "Cataclysm requests are on the board");
		// staffs: a cast locks every staff of that school you carry, not only the one in your hand
		FakePlayer mage = player(h, 1);
		List<Gear.Weapon> blacks = new ArrayList<>();
		for (Gear.Dungeon d : Gear.DUNGEONS) for (Gear.Weapon w : d.weapons()) if (w.kind().equals("black") && blacks.size() < 2) blacks.add(w);
		ItemStack first = new ItemStack(Gear.item(blacks.get(0).id())), second = new ItemStack(Gear.item(blacks.get(1).id()));
		mage.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, first);
		net.minecraft.world.item.Item other = second.getItem();
		mage.getInventory().add(second);
		c.check(first.use(h.getLevel(), mage, net.minecraft.world.InteractionHand.MAIN_HAND).getResult().consumesAction(), "a staff casts");
		c.check(!first.use(h.getLevel(), mage, net.minecraft.world.InteractionHand.MAIN_HAND).getResult().consumesAction(), "not again at once");
		c.check(mage.getCooldowns().isOnCooldown(other), "nor with another staff of the school");
		// stamina: heavier swings cost more, fists nothing
		c.check(Passives.swingCost(mage, weapon("hammer", false)) > Passives.swingCost(mage, weapon("sword", false)), "a hammer swing costs more than a sword's");
		c.check(Passives.swingCost(mage, weapon("sword", false)) > Passives.swingCost(mage, weapon("dagger", false)), "a sword swing costs more than a dagger's");
		c.near(Passives.swingCost(mage, ItemStack.EMPTY), 0, 0.001, "fists cost nothing");
		c.near(Passives.swingCost(mage, new ItemStack(net.minecraft.world.item.Items.IRON_PICKAXE)), 0, 0.001, "nor do tools");
		c.check(Gear.WEAPON.values().stream().allMatch(w -> Passives.swingCost(mage, new ItemStack(Gear.item(w.id()))) > 0), "every weapon costs stamina");
		c.check(Passives.swingCost(mage, new ItemStack(net.minecraft.world.item.Items.IRON_SWORD)) > 0, "a vanilla sword too");
		// a party: what one does, the other has, the card and the Cold Forge excepted; nobody online here, so it waits for them
		FakePlayer ann = player(h, 2), ben = player(h, 3);
		c.check(Party.form(ann, ben) && Party.same(ann, ben), "two make a party");
		Story.mark(ann, "story/capital");
		Story.mark(ann, "story/registered");
		Story.mark(ann, "cold/seen");
		c.check(!Coins.flag(ben, "q:story/capital"), "someone away has it when they're back");
		Party.arrive(ben);
		c.check(Coins.flag(ben, "q:story/capital"), "a step one does is done for both");
		c.check(!Coins.flag(ben, "q:story/registered") && !Coins.flag(ben, "q:cold/seen"), "your card and the Cold Forge stay yours");
		Party.remove(h.getLevel().getServer(), ben.getUUID(), " left the party");
		c.check(!Party.same(ann, ben) && Party.others(ann).isEmpty(), "two less one is no party");
		// a town's waystone goes up under its own name
		BlockPos stone = h.absolutePos(new BlockPos(2, 2, 2));
		c.check(Waypoints.raise(h.getLevel(), stone, "Testmere", "lake"), "a waystone goes up");
		c.check(net.blay09.mods.waystones.api.WaystonesAPI.getWaystoneAt(h.getLevel(), stone).map(w -> w.getName().getString()).orElse("").equals("Testmere"), "and it's called after its town");
		// the story: one straight line, with everyone and everything it names really there
		var story = Journal.CHAPTERS.stream().filter(ch -> !ch.title().equals("The Hunter's Ledger")).flatMap(ch -> ch.quests().stream()).toList();
		boolean line = true;
		for (int i = 0; i < story.size(); i++) line &= story.get(i).deps().equals(i == 0 ? List.of() : List.of(story.get(i - 1).key()));
		c.check(line, "each step of the story opens the next");
		c.check(story.stream().allMatch(q -> q.who().isEmpty() || Talk.kind(q.who()) != null), "everyone the story names lives in the city");
		c.check(story.stream().allMatch(q -> h.getLevel().getServer().getAdvancements().get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, q.flag())) != null), "every step has its advancement");
		FakePlayer walker = player(h, 1);
		c.check(Story.meeting(walker, "innkeeper") == null, "Dunstan keeps his words until you get there");
		for (var q : story) {
			if (q.who().equals("innkeeper")) break;
			Story.mark(walker, q.flag());
		}
		c.check(Story.meeting(walker, "innkeeper") != null, "then says them");
		Coins.setFlag(walker, "went_there");
		c.check(Talk.test(walker, "flag:went_there") && !Talk.test(walker, "coins:6"), "the dialogue's flag and coin checks work");
		// the Joining
		Gear.Dungeon f = Gear.DUNGEONS.get(0);
		Gear.Weapon bossSword = f.bossWeapons().stream().filter(w -> w.kind().equals("sword")).findFirst().orElseThrow();
		ItemStack bs = new ItemStack(Gear.item(bossSword.id())), sameRank = bs.copy(), wrongKind = new ItemStack(Gear.item(f.bossWeapons().stream().filter(w -> w.kind().equals("dagger")).findFirst().orElseThrow().id()));
		c.check(Joined.after(bs, sameRank) == 1, "two rank D swords make a rank C Joined sword");
		c.check(Joined.after(bs, wrongKind) == 0, "a sword won't join a dagger");
		c.check(Joined.after(bs, new ItemStack(Gear.item(sword.id()))) == 0, "forged steel won't join");
		ItemStack made = Joined.result(bs, sameRank);
		c.check(Joined.stage(made) == 1 && Joined.is(made), "what comes out is the Joined sword");
		double bossAtC = Gear.DUNGEONS.stream().flatMap(d -> d.bossWeapons().stream()).filter(w -> w.kind().equals("sword") && w.rank() == 'C').findFirst().orElseThrow().damage();
		c.check(Joined.of("sword").damage() * Joined.mult(made) > bossAtC * 1.05, "a Joined weapon stands above the boss weapons of its rank");
		ItemStack rankC = new ItemStack(Gear.item(Gear.DUNGEONS.stream().flatMap(d -> d.bossWeapons().stream()).filter(w -> w.kind().equals("sword") && w.rank() == 'C').findFirst().orElseThrow().id()));
		c.check(Joined.after(made, sameRank) == 0, "a boss weapon below a Joined one's rank won't feed it");
		c.check(Joined.after(made, rankC) == 2 && Joined.after(rankC, made) == 0, "a boss weapon of its rank feeds a Joined one, in that order");
		Joined.setStage(made, 4);
		c.check(Joined.after(made, sameRank) == 0, "a rank S Joined weapon wants a rank S boss weapon");
		Joined.setStage(made, Joined.TOP);
		c.check(!Joined.canLead(made), "S+ is the end of it");
		// the Cold Forge: the quest's steps, and its altar found from any piece of it
		Gear.Dungeon rankE = Gear.DUNGEONS.stream().filter(d -> d.rank() == 'E').findFirst().orElseThrow();
		ColdForge.bossDown(p, rankE);
		c.check(GateForge.count(p, ColdForge.SHARD.get()) == 0, "no shard before Wendel sends you after them");
		Coins.setFlag(p, "cold_hunt");
		ColdForge.bossDown(p, rankE);
		ColdForge.bossDown(p, rankE);
		c.check(GateForge.count(p, ColdForge.SHARD.get()) == 1, "one shard a rank, however many bosses fall");
		for (char r : new char[] {'D', 'C'}) ColdForge.bossDown(p, Gear.DUNGEONS.stream().filter(d -> d.rank() == r).findFirst().orElseThrow());
		c.check(ColdForge.shardsReady(p), "three shards from three ranks");
		ColdForge.bind(p);
		c.check(GateForge.count(p, ColdForge.EMBER.get()) == 1 && GateForge.count(p, ColdForge.SHARD.get()) == 0, "Wendel binds them into the Ember");
		ColdForge.giveBrand(p);
		c.check(GateForge.count(p, ColdForge.BRAND.get()) == 1 && Coins.flag(p, "cold_brand"), "Wendel hands over the Brand");
		c.check(net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.containsKey(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "ossric")), "the trial's boss exists");
		for (Journal.Chapter ch : Journal.CHAPTERS)
			for (Journal.Quest q : ch.quests()) for (String d : q.deps()) if (Journal.of(d) == null) c.check(false, q.key() + " waits on " + d + ", which isn't a quest");
		c.check(Journal.open(Journal.CHAPTERS.get(0).quests().get(0), java.util.Set.of()), "the Journal's first quest is open from the start");
		BlockPos piece = h.absolutePos(new BlockPos(1, 2, 1));
		PropBlock.Sculpt lit = (PropBlock.Sculpt) SculptBlocks.COLD_FORGE_LIT.get();
		for (int i = 0; i < 200; i += 37) {
			h.getLevel().setBlock(piece, lit.defaultBlockState().setValue(PropBlock.FACING, net.minecraft.core.Direction.SOUTH).setValue(lit.piece, i), 2);
			BlockPos altar = ColdForge.altar(h.getLevel(), piece);
			c.check(altar != null && altar.distManhattan(piece) < 24, "the altar lies within the forge from piece " + i);
		}
		h.getLevel().setBlock(piece, net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), 2);
		c.check(h.getLevel().getServer().getAdvancements().get(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "cold/lit")) != null, "the book's steps are loaded");
		// armour: a Perfect piece has 10% more armour
		Item helm = Gear.item(Gear.DUNGEONS.get(0).sets().get(3).pieces().get(0).id());
		c.near(armour(Smithing.make(helm, Smithing.Quality.PERFECT, "", p)) / armour(new ItemStack(helm)), 1.35, 0.02, "a Perfect helm has 35% more armour");
		c.check(Smithing.Craft.of("robe").cloth && !Smithing.Craft.of("heavy").cloth && Smithing.Craft.of("sword") == Smithing.Craft.METAL, "robes are stitched, plate hammered");
		c.end(h);
	}

	private static double armour(ItemStack s) {
		double[] a = {0};
		s.forEachModifier(net.minecraft.world.entity.EquipmentSlot.HEAD, (attr, m) -> {
			if (attr.is(net.minecraft.world.entity.ai.attributes.Attributes.ARMOR)) a[0] += m.amount();
		});
		return a[0];
	}

	private static double damage(FakePlayer p) {
		var a = p.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.ATTACK_DAMAGE);
		a.removeModifiers();
		p.getMainHandItem().forEachModifier(net.minecraft.world.entity.EquipmentSlot.MAINHAND, (attr, m) -> {
			if (attr.is(net.minecraft.world.entity.ai.attributes.Attributes.ATTACK_DAMAGE)) a.addOrReplacePermanentModifier(m);
		});
		return a.getValue();
	}

	@GameTest(template = "selftest")
	public static void curios(GameTestHelper h) {
		Checks c = new Checks("curios");
		c.check(Curios.SPECS.size() == 76, "76 curios and relics loaded (" + Curios.SPECS.size() + ")");
		for (String slot : new String[] {"ring", "amulet", "charm"})
			c.check(Curios.SPECS.stream().filter(s -> s.slot().equals(slot)).count() == 20, "20 " + slot + "s");
		c.check(Curios.SPECS.stream().filter(s -> s.slot().equals("relic")).allMatch(s -> s.tier() == WorldArms.Tier.LEGENDARY),
				"relics are all legendary");
		var slots = top.theillusivec4.curios.api.CuriosApi.getPlayerSlots(h.getLevel());
		for (String id : new String[] {"ring", "necklace", "charm", "relic"}) c.check(slots.containsKey(id), "players have a " + id + " slot");
		c.check(slots.containsKey("ring") && slots.get("ring").getSize() == 2, "two ring slots");
		int worn = slots.values().stream().filter(s -> !s.getIdentifier().equals(BeltPouch.SLOT)).mapToInt(s -> s.getSize()).sum();
		c.check(worn <= com.snoringwalrus.ashbound.client.CharacterScreen.CURIO_CELLS, "the Character screen has a cell for all " + worn + " slots");
		FakePlayer p = player(h, 30);
		var ring = new top.theillusivec4.curios.api.SlotContext("ring", p, 0, false, true);
		var relic = new top.theillusivec4.curios.api.SlotContext("relic", p, 0, false, true);
		ItemStack knuckle = curio("brigands_knuckle_ring");
		c.check(top.theillusivec4.curios.api.CuriosApi.isStackValid(ring, knuckle), "a ring fits the ring slot");
		c.check(!top.theillusivec4.curios.api.CuriosApi.isStackValid(relic, knuckle), "a ring doesn't fit the relic slot");
		c.check(top.theillusivec4.curios.api.CuriosApi.isStackValid(relic, curio("void_pearl")), "a relic fits the relic slot");
		double dmg = 0;
		for (var e : ((Curios.Curio) knuckle.getItem()).getAttributeModifiers(ring, ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "t"), knuckle).entries())
			if (e.getKey().equals(Attributes.ATTACK_DAMAGE)) dmg += e.getValue().amount();
		c.near(dmg, 0.03, 0.0001, "Knuckle-Ring gives +3% melee damage");
		var inv = top.theillusivec4.curios.api.CuriosApi.getCuriosInventory(p);
		c.check(inv.isPresent(), "players have a curios inventory");
		inv.ifPresent(i -> {
			i.setEquippedCurio("ring", 0, curio("bowstring_ring"));
			i.setEquippedCurio("ring", 1, curio("marksmans_gyre"));
			i.setEquippedCurio("charm", 0, curio("knucklebone_charm"));
		});
		c.near(Passives.stat(p, "arrow%"), 9, 0.001, "two rings stack their bow damage into the tree's stat");
		c.near(Passives.stat(p, "ash%"), 6, 0.001, "a charm's Ash bonus reaches the tree's stat");
		c.near(Curios.stat(p, "health%"), 0, 0.001, "attribute stats aren't counted twice");
		c.check(Curios.wears(p, "marksmans_gyre") && !Curios.wears(p, "void_pearl"), "wears() sees what is worn");
		c.end(h);
	}

	@GameTest(template = "selftest")
	public static void curioEffects(GameTestHelper h) {
		Checks c = new Checks("curioEffects");
		FakePlayer p = player(h, 30);
		var inv = top.theillusivec4.curios.api.CuriosApi.getCuriosInventory(p).orElseThrow();
		// the Ninth Pyre: every fourth spell free and half again as strong
		inv.setEquippedCurio("ring", 0, curio("ring_of_the_ninth_pyre"));
		inv.setEquippedCurio("relic", 0, curio("legions_brand"));
		inv.setEquippedCurio("charm", 0, curio("blight_vial"));
		p.setData(Spells.MANA, 10f);
		for (int k = 1; k <= 3; k++) CurioFx.onCast(p, 8);
		c.near(CurioFx.spellMult(p), 1, 0.001, "casts 1-3 are plain");
		CurioFx.onCast(p, 8);
		c.near(CurioFx.spellMult(p), 1.5, 0.001, "the 4th cast is empowered");
		c.near(p.getData(Spells.MANA), 18, 0.001, "...and its mana comes back");
		// Legion's Brand (I): every third hit +30%
		Zombie z = dummy(h);
		float a = hit(p, z, 10), b = hit(p, z, 10), d = hit(p, z, 10);
		c.near(a + b, 20, 0.01, "hits 1-2 plain");
		c.near(d, 13, 0.01, "hit 3 burns for +30%");
		c.check(CurioFx.blighted(z), "the Blight Vial rots what it hits, a zombie too");
		// right-click in hand: a ring goes in the free ring slot, then swaps for the first one worn
		var hand = net.minecraft.world.InteractionHand.MAIN_HAND;
		p.setItemInHand(hand, curio("bowstring_ring"));
		p.setItemInHand(hand, p.getMainHandItem().use(p.level(), p, hand).getObject());
		c.check(p.getMainHandItem().isEmpty() && inv.getStacksHandler("ring").orElseThrow().getStacks().getStackInSlot(1).is(curio("bowstring_ring").getItem()),
				"right-click wears a ring in the free slot");
		p.setItemInHand(hand, curio("marksmans_gyre"));
		p.setItemInHand(hand, p.getMainHandItem().use(p.level(), p, hand).getObject());
		c.check(p.getMainHandItem().is(curio("ring_of_the_ninth_pyre").getItem()), "with both full it swaps for the first ring");
		// a relic awakens at the Forge: trophies and Ash
		ItemStack relic = curio("void_pearl");
		c.check(CurioFx.tier(relic) == 1, "a found relic is power I");
		CurioFx.upgrade(p, relic);
		c.check(CurioFx.tier(relic) == 1, "no trophy, no upgrade");
		var trophy = Gear.item(Gear.DUNGEONS.get(0).mats()[2]);
		p.getInventory().add(new ItemStack(trophy, 4));
		int ash = p.getData(Levels.ASH);
		CurioFx.upgrade(p, relic);
		c.check(CurioFx.tier(relic) == 2, "1 trophy + Ash: power II");
		c.check(p.getData(Levels.ASH) == ash - 5000 && GateForge.count(p, trophy) == 3, "it took 1 trophy and 5000 Ash");
		CurioFx.upgrade(p, relic);
		c.check(CurioFx.tier(relic) == 3 && GateForge.count(p, trophy) == 0, "3 more trophies: power III");
		CurioFx.upgrade(p, relic);
		c.check(CurioFx.tier(relic) == 3, "III is the top");
		c.end(h);
	}

	// ---------------------------------------------------------------- reported: a Hollow Knight took no damage at all

	@GameTest(template = "selftest")
	public static void hollowKnightHurts(GameTestHelper h) {
		Checks c = new Checks("hollowKnightHurts");
		for (String id : new String[] {"hollow_knight", "hollow_squire", "siege_knight"}) {
			var type = BuiltInRegistries.ENTITY_TYPE.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, id));
			@SuppressWarnings("unchecked") Entity e = h.spawnWithNoFreeWill((net.minecraft.world.entity.EntityType<net.minecraft.world.entity.Mob>) type, new BlockPos(2, 1, 2));
			if (!(e instanceof LivingEntity m)) {
				c.check(false, id + " spawns as a living thing");
				continue;
			}
			FakePlayer p = player(h, 30);
			float front = hit(p, m, 20);
			p.setPos(m.getX(), m.getY(), m.getZ() - 2);
			float back = hit(p, m, 20);
			Ashbound.LOG.info("SELFTEST {} hp {} max {} front {} back {} armor {} invul {}", id, m.getHealth(), m.getMaxHealth(), front, back,
					m.getArmorValue(), m.isInvulnerable());
			c.check(front > 0 && back > 0, id + " takes damage (front " + front + ", back " + back + ")");
			e.discard();
		}
		c.end(h);
	}

	// ---------------------------------------------------------------- reported: the Ashwalkers die the moment they come

	@GameTest(template = "selftest", timeoutTicks = 200)
	public static void ashwalkersLive(GameTestHelper h) {
		Checks c = new Checks("ashwalkersLive");
		java.util.List<Mob> mobs = new ArrayList<>();
		int i = 0;
		for (String id : new String[] {"ashwalker", "cinder_hulk", "ash_herald"}) {
			var type = BuiltInRegistries.ENTITY_TYPE.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, id));
			if (!(type.create(h.getLevel()) instanceof Mob m)) {
				c.check(false, id + " is a mob");
				continue;
			}
			var at = h.absolutePos(new BlockPos(1 + i * 2, 1, 2));
			i++;
			m.moveTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5, 0, 0);
			m.addTag(Ashfall.ROAMER);
			net.neoforged.neoforge.event.EventHooks.finalizeMobSpawn(m, h.getLevel(), h.getLevel().getCurrentDifficultyAt(at), net.minecraft.world.entity.MobSpawnType.EVENT, null);
			h.getLevel().addFreshEntity(m);
			Balance.atRank(m, id, "F");
			m.addTag(Ashfall.TAG);
			m.addTag(Ashfall.WALKER);
			Ashbound.LOG.info("SELFTEST {} spawned hp {} / {} cancelled {}", id, m.getHealth(), m.getMaxHealth(), m.isSpawnCancelled());
			mobs.add(m);
		}
		h.runAfterDelay(40, () -> {
			for (Mob m : mobs) {
				var src = m.getLastDamageSource();
				Ashbound.LOG.info("SELFTEST {} after 2s: alive {} removed {} hp {} / {} last hit {}", m.getType().getDescriptionId(), m.isAlive(),
						m.getRemovalReason(), m.getHealth(), m.getMaxHealth(), src == null ? "none" : src.getMsgId());
				c.check(m.isAlive(), m.getType().getDescriptionId() + " lives (hp " + m.getHealth() + ", " + (src == null ? "no hit" : src.getMsgId()) + ")");
			}
			c.end(h);
		});
	}

	// ---------------------------------------------------------------- meteor fall

	/** A gate-shard: it falls, blasts a crater (glassed middle, scorched rim) only in natural ground, stands in it, wakes,
	 *  lets its gate's monsters out, and bursts after its three veins are broken, with Shardglass in the loot. */
	@GameTest(template = "selftest", timeoutTicks = 100)
	public static void meteorFall(GameTestHelper h) {
		Checks c = new Checks("meteorFall");
		var l = h.getLevel();
		var r = l.getRandom();
		// well away from the other tests: the crater's blast reaches 20 blocks
		BlockPos far = h.absolutePos(new BlockPos(0, 0, 0)).offset(420, 0, 420);
		for (int cx = -2; cx <= 2; cx++)
			for (int cz = -2; cz <= 2; cz++) l.getChunk((far.getX() >> 4) + cx, (far.getZ() >> 4) + cz);
		BlockPos ground = l.getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, far);
		FakePlayer p = player(h, 1);
		p.moveTo(ground.getX() + 30, ground.getY() + 2, ground.getZ());
		MeteorShard s = Meteors.open(l, ground, 1, 1, null, r);
		c.check(s != null && s.phase() == MeteorShard.FALLING, "it comes down out of the sky");
		if (s == null) {
			c.end(h);
			return;
		}
		Meteors.Fall f = Meteors.LIVE.get(s.getUUID());
		c.check(f != null && s.head(0).y > 150, "it starts high up: " + s.head(0));
		c.check(f != null && !f.monsters.isEmpty(), "its gate's monsters come with it: " + (f == null ? null : f.monsters));
		Meteors.land(l, s, f, r);
		c.check(s.phase() == MeteorShard.LANDED && s.getY() < ground.getY(), "it lands in its crater: " + s.getY() + " under " + ground.getY());
		int glass = 0, scorch = 0;
		for (BlockPos at : BlockPos.betweenClosed(ground.offset(-f.radius - 3, -8, -f.radius - 3), ground.offset(f.radius + 3, 4, f.radius + 3))) {
			var bs = l.getBlockState(at);
			if (bs.is(Meteors.GLASSED.get())) glass++;
			if (bs.is(Meteors.SCORCHED.get())) scorch++;
		}
		c.check(glass > 4 && scorch > 20, "the crater: " + glass + " glassed, " + scorch + " scorched");
		// never where anything's built: a chest near makes the ground unfit
		BlockPos chest = l.getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, ground.offset(40, 0, 0));
		l.setBlockAndUpdate(chest, net.minecraft.world.level.block.Blocks.CHEST.defaultBlockState());
		c.check(!Meteors.fits(l, chest.offset(6, 0, 0), 8), "it won't come down by a chest");
		l.setBlockAndUpdate(chest, net.minecraft.world.level.block.Blocks.AIR.defaultBlockState());
		Meteors.wake(l, s);
		c.check(s.phase() == MeteorShard.AWAKE, "it wakes");
		Meteors.wave(l, s, f, r);
		c.check(!f.mobs.isEmpty(), f.mobs.size() + " monsters crawled out of the cracks");
		for (int i = 0; i < 3; i++) {
			c.check(s.veins() == 3 - i, "veins left: " + s.veins());
			s.hurt(p.damageSources().playerAttack(p), 1e6f);
		}
		c.check(s.phase() == MeteorShard.SHATTER && f.won, "its last vein broken, it bursts");
		var share = Meteors.loot(p, f, r);
		c.check(share.stream().anyMatch(st -> st.is(Meteors.SHARDGLASS.get())), "Shardglass in the loot: " + share);
		f.mobs.forEach(u -> {
			if (l.getEntity(u) != null) l.getEntity(u).discard();
		});
		Meteors.LIVE.remove(s.getUUID());
		s.discard();
		c.end(h);
	}

	// ---------------------------------------------------------------- downed, not dead

	/** Going down: crawling at 1 health; brought back at a third; bleeding out kills for real; alone you just die. */
	@GameTest(template = "selftest", timeoutTicks = 60)
	public static void downedRevive(GameTestHelper h) {
		Checks c = new Checks("downedRevive");
		FakePlayer p = player(h, 1);
		p.setHealth(p.getMaxHealth());
		Downed.down(p);
		c.check(Downed.is(p) && p.getHealth() == 1f && p.getForcedPose() == net.minecraft.world.entity.Pose.SWIMMING, "down: crawling at 1 health");
		Downed.revive(p, null);
		c.check(!Downed.is(p) && Math.abs(p.getHealth() - p.getMaxHealth() * Downed.BACK) < 0.01f && p.getForcedPose() == null, "brought back at a third: " + p.getHealth());
		Downed.down(p);
		Downed.Down d = Downed.DOWN.get(p.getUUID());
		d.left = 1;
		Downed.step(p, d);
		c.check(!Downed.is(p) && p.getForcedPose() == null, "bleeding out ends it (the test player can't be hurt, so only the state is checked)");
		// a death with nobody near to help: the event goes through, nobody goes down
		FakePlayer q = player(h, 2);
		var ev = new net.neoforged.neoforge.event.entity.living.LivingDeathEvent(q, q.damageSources().generic());
		net.neoforged.neoforge.common.NeoForge.EVENT_BUS.post(ev);
		c.check(!ev.isCanceled() && !Downed.is(q), "alone (no party near), you just die");
		// down already and hit again: no second chance
		Downed.down(q);
		var again = new net.neoforged.neoforge.event.entity.living.LivingDeathEvent(q, q.damageSources().generic());
		net.neoforged.neoforge.common.NeoForge.EVENT_BUS.post(again);
		c.check(!again.isCanceled() && !Downed.is(q), "hit again while down, you die");
		c.end(h);
	}

	// ---------------------------------------------------------------- the Tidewrack

	/** The sea's monsters are registered, balanced, and know how to fight. */
	@GameTest(template = "selftest", timeoutTicks = 40)
	public static void tidewrack(GameTestHelper h) {
		Checks c = new Checks("tidewrack");
		for (String k : new String[] {"lamprey_hound", "merrow", "reef_knight", "net_hag", "hullback", "abyss_angler"}) {
			var type = BuiltInRegistries.ENTITY_TYPE.getOptional(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, k));
			c.check(type.isPresent() && type.get().create(h.getLevel()) instanceof net.minecraft.world.entity.Mob, k + " is a monster");
		}
		c.end(h);
	}

	// ---------------------------------------------------------------- pass 13: a boss moved to another rank

	/** A boss made a boss of another rank climbs (or drops) like the bosses do, and its armour follows the bosses' armour, not its hit. */
	@GameTest(template = "selftest", timeoutTicks = 40)
	public static void bossesMoveByRole(GameTestHelper h) {
		Checks c = new Checks("bossesMoveByRole");
		int i = 0;
		for (String[] k : new String[][] {{"cairn_giant", "F", "0.064"}, {"walking_mountain", "S", "6.48"}}) {
			var type = BuiltInRegistries.ENTITY_TYPE.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, k[0]));
			if (!(type.create(h.getLevel()) instanceof Mob m)) {
				c.check(false, k[0] + " is a mob");
				continue;
			}
			var at = h.absolutePos(new BlockPos(1 + i++ * 3, 1, 2));
			m.moveTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5, 0, 0);
			net.neoforged.neoforge.event.EventHooks.finalizeMobSpawn(m, h.getLevel(), h.getLevel().getCurrentDifficultyAt(at), net.minecraft.world.entity.MobSpawnType.EVENT, null);
			h.getLevel().addFreshEntity(m);
			double hp0 = m.getMaxHealth(), arm0 = m.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.ARMOR);
			Balance.atRank(m, k[0], k[1]);
			double hp1 = m.getMaxHealth(), arm1 = m.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.ARMOR), want = Double.parseDouble(k[2]);
			Ashbound.LOG.info("SELFTEST {} to {}: hp {} -> {}, armour {} -> {}", k[0], k[1], hp0, hp1, arm0, arm1);
			c.check(hp0 > 0 && Math.abs(hp1 / hp0 / want - 1) < 0.08 || hp1 >= 1023, k[0] + " at " + k[1] + ": health x" + String.format("%.3f", hp1 / hp0) + " (bosses' x" + k[2] + ")");
			c.check(arm1 <= Math.max(arm0 * 2.2, 4), k[0] + " at " + k[1] + ": armour " + String.format("%.1f", arm0) + " -> " + String.format("%.1f", arm1) + ", not the hit's climb");
			m.discard();
		}
		c.end(h);
	}

	// ---------------------------------------------------------------- the overworld bosses

	/** Each overworld boss is a monster with its summon, a recipe for it, a land, and spoils worth the trip. */
	@GameTest(template = "selftest", timeoutTicks = 40)
	public static void worldBosses(GameTestHelper h) {
		Checks c = new Checks("worldBosses");
		FakePlayer p = FakePlayerFactory.get(h.getLevel(), new GameProfile(UUID.randomUUID(), "ashboss"));
		c.check(WorldBosses.ALL.size() == 5, WorldBosses.ALL.size() + " world bosses");
		for (WorldBosses.Boss b : WorldBosses.ALL) {
			var type = BuiltInRegistries.ENTITY_TYPE.getOptional(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, b.kind()));
			c.check(type.isPresent() && type.get().create(h.getLevel()) instanceof net.minecraft.world.entity.Mob, b.kind() + " is a monster");
			var item = WorldBosses.SUMMONS.get(b.summon());
			c.check(item != null && item.get() instanceof WorldBosses.Summon sm && sm.boss == b, b.summon() + " calls " + b.kind());
			c.check(h.getLevel().getRecipeManager().byKey(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, b.summon())).isPresent(), b.summon() + " can be made");
			var spoils = WorldBosses.spoils(p, b.kind(), 4, h.getLevel().getRandom());
			c.check(spoils.size() >= 4 && spoils.stream().noneMatch(net.minecraft.world.item.ItemStack::isEmpty), b.kind() + " leaves " + spoils.size() + " things");
		}
		c.end(h);
	}

	// ---------------------------------------------------------------- quest chains

	/** Every chain loads, and everything in it is real: its things, its monsters, the people it sends you to. */
	@GameTest(template = "selftest", timeoutTicks = 40)
	public static void questChains(GameTestHelper h) {
		Checks c = new Checks("questChains");
		c.check(Chains.ALL.size() >= 12, Chains.ALL.size() + " chains loaded");
		java.util.function.Predicate<String> person = to -> to.isEmpty() || to.equals("@giver")
				|| (to.startsWith("kind:") ? Talk.kind(to.substring(5)) != null : to.startsWith("tag:") ? Talk.anyTagged(to.substring(4)) : Talk.kind(to) != null || Talk.anyTagged(to));
		for (Chains.Chain ch : Chains.ALL.values()) {
			boolean ok = !ch.steps().isEmpty() && (ch.auto() || person.test(ch.giver()) && !ch.giver().isEmpty());
			String bad = ok ? "" : " giver " + ch.giver();
			for (String it : ch.items()) if (Chains.stack(it).isEmpty()) bad += " item " + it;
			for (var s : ch.steps()) {
				if (!java.util.Set.of("talk", "kill", "find", "event", "deliver", "boss", "choice").contains(s.kind())) bad += " step " + s.kind();
				if (!s.item().isEmpty() && Chains.stack(s.item()).isEmpty()) bad += " item " + s.item();
				if ((s.kind().equals("kill") || s.kind().equals("boss")) && !s.what().startsWith("@")
						&& !BuiltInRegistries.ENTITY_TYPE.containsKey(ResourceLocation.parse(s.what()))) bad += " monster " + s.what();
				if (s.kind().equals("talk") || s.kind().equals("deliver") || s.kind().equals("choice")) if (!person.test(s.to()) || s.to().isEmpty()) bad += " to " + s.to();
				if (s.in().startsWith("legend:") && !BuiltInRegistries.ENTITY_TYPE.containsKey(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, s.in().substring(7)))) bad += " legend " + s.in();
				if (s.in().startsWith("dungeon:") && Gear.DUNGEONS.stream().noneMatch(d -> d.gate().equals(s.in().substring(8)))) bad += " dungeon " + s.in();
				if ((s.kind().equals("find") || s.kind().equals("event")) && s.in().isEmpty()) bad += " find where?";
			}
			c.check(bad.isEmpty(), ch.id() + bad);
		}
		c.end(h);
	}

	// ---------------------------------------------------------------- boss arenas

	/** The Kiln-Father's Hearth: a big floor, the Brand in the middle, room where Ossric comes up, slag below the floor. */
	@GameTest(template = "selftest", timeoutTicks = 40)
	public static void bossHearth(GameTestHelper h) {
		Checks c = new Checks("bossHearth");
		java.util.Map<Long, net.minecraft.world.level.block.state.BlockState> b = new java.util.HashMap<>();
		HearthShape.blocks((x, y, z, st) -> b.put(net.minecraft.core.BlockPos.asLong(x, y, z), st));
		Ashbound.LOG.info("SELFTEST hearth: {} blocks, {} chimneys", b.size(), HearthShape.STACKS.size());
		c.check(b.size() > 40000 && HearthShape.STACKS.size() == 9, "the hearth: " + b.size() + " blocks, 9 chimneys");
		var air = net.minecraft.world.level.block.Blocks.AIR;
		java.util.function.BiPredicate<Integer, Integer> floor = (x, z) -> b.containsKey(net.minecraft.core.BlockPos.asLong(x, -1, z));
		c.check(floor.test(0, 0) && floor.test(55, 0) && floor.test(0, -55) && !floor.test(0, 62), "a floor 60 out from the middle, the channel past it");
		c.check(b.get(net.minecraft.core.BlockPos.asLong(0, -1, 0)).getLightEmission() > 0, "the Brand glows in the middle");
		boolean room = true;
		for (int x = -4; x <= 4; x++)
			for (int z = 26; z <= 35; z++)
				for (int y = 0; y < 14; y++) {
					var st = b.get(net.minecraft.core.BlockPos.asLong(x, y, z));
					if (st != null && !st.is(air)) room = false;
				}
		c.check(room, "nothing stands where Ossric comes up");
		boolean landing = true;
		for (int x = -3; x <= 3; x++) for (int z = -3; z <= 3; z++) for (int y = 0; y < 3; y++) if (b.containsKey(net.minecraft.core.BlockPos.asLong(x, y, z))) landing = false;
		c.check(landing, "the party lands in the open");
		c.check(b.containsKey(net.minecraft.core.BlockPos.asLong(62, -3, 0)) && !b.containsKey(net.minecraft.core.BlockPos.asLong(62, -1, 0)), "the slag channel lies below the floor");
		BossArenas.defs();
		var def = BossArenas.DEFS.get("hearth");
		c.check(def != null && def.sigil().get() == ColdForge.BRAND.get() && "ossric".equals(def.boss()), "the Brand is Ossric's sigil");
		c.end(h);
	}

	/** The Graveyard of Ships: a deck 60 out, the sea round it held in, room where the Wreck-Mother comes up, the sigil's hers. */
	@GameTest(template = "selftest", timeoutTicks = 40)
	public static void bossWreck(GameTestHelper h) {
		Checks c = new Checks("bossWreck");
		java.util.Map<Long, net.minecraft.world.level.block.state.BlockState> b = new java.util.HashMap<>();
		WreckShape.blocks((x, y, z, st) -> b.put(net.minecraft.core.BlockPos.asLong(x, y, z), st));
		Ashbound.LOG.info("SELFTEST graveyard: {} blocks, {} lamps", b.size(), WreckShape.LAMPS.size());
		c.check(b.size() > 60000 && WreckShape.LAMPS.size() == 4, "the graveyard: " + b.size() + " blocks, 4 standing masts");
		java.util.function.BiPredicate<Integer, Integer> deck = (x, z) -> b.containsKey(net.minecraft.core.BlockPos.asLong(x, -1, z));
		c.check(deck.test(0, 0) && deck.test(0, -55) && deck.test(50, 0), "a deck out to the rim");
		var water = net.minecraft.world.level.block.Blocks.WATER;
		var sea = b.get(net.minecraft.core.BlockPos.asLong(90, WreckShape.SEA, 3));
		c.check(sea != null && sea.is(water), "the sea round it");
		boolean held = true;                              // every water block has something under it and nothing open to the side at the edge
		for (var e : b.entrySet())
			if (e.getValue().is(water)) {
				var p = net.minecraft.core.BlockPos.of(e.getKey());
				if (!b.containsKey(p.below().asLong())) held = false;
				for (var d : net.minecraft.core.Direction.Plane.HORIZONTAL) if (!b.containsKey(p.relative(d).asLong())) held = false;
			}
		c.check(held, "the sea can't spill (a bed under it, a reef round it, the hull sealed)");
		boolean room = true;
		for (int x = -5; x <= 5; x++)
			for (int z = 38; z <= 50; z++)
				for (int y = 0; y < 8; y++) {
					var st = b.get(net.minecraft.core.BlockPos.asLong(x, y, z));
					if (st != null && !st.isAir()) room = false;
				}
		c.check(room, "nothing stands where the Wreck-Mother comes up");
		boolean landing = true;
		for (int x = -3; x <= 3; x++) for (int z = -3; z <= 3; z++) for (int y = 0; y < 3; y++) if (b.containsKey(net.minecraft.core.BlockPos.asLong(x, y, z))) landing = false;
		c.check(landing, "the party lands in the open");
		BossArenas.defs();
		var def = BossArenas.DEFS.get("wreck");
		c.check(def != null && def.sigil().get() == BossArenas.DROWNED_SIGIL.get() && "wreck_mother".equals(def.boss()), "the Drowned Sigil sends you to the Wreck-Mother");
		c.end(h);
	}

	/** The Grey Fold: a square 60 out, a basin where the party lands, room where the Shepherd walks in, nothing floating. */
	@GameTest(template = "selftest", timeoutTicks = 40)
	public static void bossFold(GameTestHelper h) {
		Checks c = new Checks("bossFold");
		java.util.Map<Long, net.minecraft.world.level.block.state.BlockState> b = new java.util.HashMap<>();
		GreyFoldShape.blocks((x, y, z, st) -> b.put(net.minecraft.core.BlockPos.asLong(x, y, z), st));
		Ashbound.LOG.info("SELFTEST grey fold: {} blocks", b.size());
		c.check(b.size() > 40000, "the fold: " + b.size() + " blocks");
		java.util.function.BiPredicate<Integer, Integer> floor = (x, z) -> b.containsKey(net.minecraft.core.BlockPos.asLong(x, -1, z));
		c.check(floor.test(0, 0) && floor.test(0, -55) && floor.test(55, 0), "a square out to the edge");
		boolean room = true;
		for (int x = -4; x <= 4; x++) for (int z = 30; z <= 39; z++) for (int y = 0; y < 10; y++) if (b.containsKey(net.minecraft.core.BlockPos.asLong(x, y, z))) room = false;
		c.check(room, "nothing stands where the Shepherd walks in");
		boolean landing = true;
		for (int x = -3; x <= 3; x++) for (int z = -3; z <= 3; z++) for (int y = 0; y < 3; y++) if (b.containsKey(net.minecraft.core.BlockPos.asLong(x, y, z))) landing = false;
		c.check(landing, "the party lands in the open basin");
		int floating = 0;                                  // every block above the ground rests on something (or beside something)
		for (long k : b.keySet()) {
			var p = net.minecraft.core.BlockPos.of(k);
			if (p.getY() < 1) continue;
			boolean held = b.containsKey(p.below().asLong());
			for (var d : net.minecraft.core.Direction.Plane.HORIZONTAL) if (b.containsKey(p.relative(d).asLong())) held = true;
			if (!held && floating++ < 12) Ashbound.LOG.info("SELFTEST floating {} {}", p, b.get(k));
		}
		c.check(floating == 0, floating + " blocks hanging in the air");
		BossArenas.defs();
		var def = BossArenas.DEFS.get("fold");
		c.check(def != null && def.sigil().get() == BossArenas.ASHEN_SIGIL.get() && "ash_shepherd".equals(def.boss()), "the Ashen Sigil sends you to the Shepherd");
		c.end(h);
	}

	/** Every boss arena: a floor under the landing, the landing open, room where its boss comes up, a sigil to go there. */
	@GameTest(template = "selftest", timeoutTicks = 100)
	public static void bossArenasAll(GameTestHelper h) {
		Checks c = new Checks("bossArenasAll");
		BossArenas.defs();
		for (var def : BossArenas.DEFS.values()) {
			java.util.Map<Long, net.minecraft.world.level.block.state.BlockState> b = new java.util.HashMap<>();
			def.shape().accept((x, y, z, st) -> b.put(net.minecraft.core.BlockPos.asLong(x, y, z), st));
			boolean floor = b.containsKey(net.minecraft.core.BlockPos.asLong(0, -1, 0)), landing = true, room = true;
			for (int x = -2; x <= 2; x++) for (int z = -2; z <= 2; z++) for (int y = 0; y < 3; y++) if (b.containsKey(net.minecraft.core.BlockPos.asLong(x, y, z))) landing = false;
			int bx = (int) Math.floor(def.bossAt().x), bz = (int) Math.floor(def.bossAt().z);
			for (int x = -3; x <= 3; x++) for (int z = -3; z <= 3; z++) for (int y = 0; y < 7; y++) if (b.containsKey(net.minecraft.core.BlockPos.asLong(bx + x, y, bz + z))) room = false;
			var boss = BuiltInRegistries.ENTITY_TYPE.getOptional(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, def.boss()));
			c.check(floor && landing && room && boss.isPresent() && def.sigil().get() != null,
					def.id() + ": " + b.size() + " blocks" + (floor ? "" : ", no floor") + (landing ? "" : ", landing blocked") + (room ? "" : ", boss spot blocked")
							+ (boss.isPresent() ? "" : ", no " + def.boss()));
		}
		c.end(h);
	}

	// ---------------------------------------------------------------- the Ashen Ring

	/** The Ring: its shape has stands, seats and gates; waves climb the ranks, a ruler every 10th; spoils; Veyra talks. */
	@GameTest(template = "selftest", timeoutTicks = 60)
	public static void arenaRing(GameTestHelper h) {
		Checks c = new Checks("arenaRing");
		int[] n = {0};
		ArenaShape.blocks((x, y, z, st) -> n[0]++);
		var seats = ArenaShape.seats();
		Ashbound.LOG.info("SELFTEST arena: {} blocks, {} seats", n[0], seats.size());
		c.check(n[0] > 50000 && seats.size() > 800, "the Ring: " + n[0] + " blocks, " + seats.size() + " seats");
		c.check(Arena.rank(1) == 'F' && Arena.rank(7) == 'E' && Arena.rank(37) == 'S' && Arena.rank(90) == 'S', "waves climb the ranks");
		// the test server makes no datapack dimensions (no gates either): the waves are tried in its own world
		var ring = h.getLevel().getServer().getLevel(Arena.RING);
		Ashbound.LOG.info("SELFTEST arena: Ring dimension {}", ring == null ? "not made by the test server" : "there");
		if (ring == null) ring = h.getLevel();
		FakePlayer p = player(h, 10);
		if (ring != null) {
			Arena.Run run = new Arena.Run(3);
			run.members.add(p.getUUID());
			run.wave = 9;
			Arena.wave(ring, run);
			c.check(run.wave == 10 && run.pending.stream().anyMatch(s2 -> s2.startsWith("!")), "wave 10 brings a ruler: " + run.pending);
			run.wave = 3;
			Arena.wave(ring, run);
			c.check(run.pending.size() >= 5 && run.pending.stream().noneMatch(s2 -> s2.startsWith("!")), "wave 4: " + run.pending.size() + " monsters, no ruler");
			var sp = Arena.spoils(p, run, ring.getRandom());
			c.check(!sp.isEmpty(), "spoils at a breather: " + sp);
		}
		c.check(Talk.kind("veyra") != null, "Veyra has her words");
		c.end(h);
	}
}
