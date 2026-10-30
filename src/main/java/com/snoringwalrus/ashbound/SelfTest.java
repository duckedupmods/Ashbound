package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

import com.mojang.authlib.GameProfile;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
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
		// rank C dungeon weapons carry the PASS 6 damage (tools/gear.py STATS) on the 1.08x ladder (C = 1.008)
		String[][] want = {{"sword", "7.6", "1.6"}, {"dagger", "4.6", "2.4"}, {"spear", "8.6", "1.2"}, {"hammer", "18.1", "0.85"},
				{"twohander", "20.2", "0.85"}};
		// one rank up is 1.08x the weapon damage (with levels, the tree and the monsters solved to it, ~1.55x harder: tools/balance.py)
		String ladder = "FEDCBAS";
		for (int i = 0; i + 1 < ladder.length(); i++)
			c.near(Gear.scale(ladder.charAt(i + 1)) / Gear.scale(ladder.charAt(i)), 1.08, 0.005, ladder.charAt(i) + " -> " + ladder.charAt(i + 1) + " weapon step");
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
		c.near(damage(p) / fine, 1.10, 0.03, "a Perfect hits 10% harder");
		c.check(best.getHoverName().getString().equals("Widow's Kiss"), "a Perfect keeps the name you gave it");
		c.check(plain.getHoverName().getString().equals(new ItemStack(it).getHoverName().getString()), "anything less keeps its own name");
		c.near(Smithing.mult(best), 1.10, 0.001, "staffs and bows read the same bonus");
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
		if (net.neoforged.fml.ModList.get().isLoaded("cataclysm")) c.check(Guild.quest("board_cataclysm_ignis") != null, "Cataclysm requests are on the board");
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
		c.near(armour(Smithing.make(helm, Smithing.Quality.PERFECT, "", p)) / armour(new ItemStack(helm)), 1.10, 0.02, "a Perfect helm has 10% more armour");
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
}
