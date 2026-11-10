package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import net.minecraft.world.level.storage.loot.predicates.LootItemRandomChanceCondition;
import net.minecraft.world.level.storage.loot.providers.number.ConstantValue;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.LootTableLoadEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * Where recipes come from (11/7, the user: "talking to NPCs, recipes in chests, guess them, find them at monster drops sometimes"). The
 * first level's recipes everyone knows; the rest are learnt:
 * <ul>
 * <li>pages: a cook's torn page, a brewer's note, an alchemist's formula, found in structure chests (more in houses and taverns) and now and
 * then on monsters (often on bosses). Read one (use it) and you learn a recipe of its trade you didn't know, most likely one near your
 * level. Unread, it can be handed to a friend.</li>
 * <li>townsfolk: anyone you talk to may know a few ("Know any good recipes?"); cooks, brewers and herbalists know more of their own. They
 * teach one for coins.</li>
 * <li>guessing: the right things in the slots still make it, and you've found it (Trades.craft).</li>
 * </ul>
 */
public final class Recipes {
	private Recipes() {}

	public static final Map<Trades.Kind, DeferredItem<Item>> PAGES = new EnumMap<>(Trades.Kind.class);

	static void items() {
		PAGES.put(Trades.Kind.MEAL, Weapons.ITEMS.registerItem("recipe_meal", p -> new Page(p, Trades.Kind.MEAL), new Item.Properties().stacksTo(16)));
		PAGES.put(Trades.Kind.BREW, Weapons.ITEMS.registerItem("recipe_brew", p -> new Page(p, Trades.Kind.BREW), new Item.Properties().stacksTo(16)));
		PAGES.put(Trades.Kind.ELIXIR, Weapons.ITEMS.registerItem("recipe_elixir", p -> new Page(p, Trades.Kind.ELIXIR), new Item.Properties().stacksTo(16)));
	}

	static void register() {
		NeoForge.EVENT_BUS.addListener(Recipes::chests);
		NeoForge.EVENT_BUS.addListener(Recipes::died);
	}

	private static String what(Trades.Kind k) {
		return k == Trades.Kind.MEAL ? "cooking" : k == Trades.Kind.BREW ? "brewing" : "alchemy";
	}

	/** An unread recipe page: use it to learn one you don't know. */
	public static class Page extends Item {
		final Trades.Kind kind;

		Page(Properties p, Trades.Kind kind) {
			super(p);
			this.kind = kind;
		}

		@Override
		public InteractionResultHolder<ItemStack> use(Level level, Player p, InteractionHand hand) {
			ItemStack s = p.getItemInHand(hand);
			if (p instanceof ServerPlayer sp) {
				Trades.Good g = read(sp, kind);
				if (g == null) {
					// you know all this trade's recipes: what's left in it is a little practice
					Trades.gain(sp, kind.trade, 40);
					sp.displayClientMessage(Component.literal("Nothing in it you don't know already. You pick up a trick or two.").withStyle(ChatFormatting.GRAY), false);
				}
				s.consume(1, p);
			}
			return InteractionResultHolder.sidedSuccess(s, level.isClientSide());
		}

		@Override
		public void appendHoverText(ItemStack s, TooltipContext ctx, List<Component> out, TooltipFlag flag) {
			out.add(Component.literal("Read it to learn a " + what(kind) + " recipe").withStyle(ChatFormatting.GOLD));
			out.add(Component.literal("you don't know yet (use it)").withStyle(ChatFormatting.GOLD));
			out.add(Component.literal("Unread, it can go to a friend").withStyle(ChatFormatting.DARK_GRAY));
		}
	}

	/** Learns a recipe of this kind you don't know, most likely one near your level; null if you know them all. */
	static Trades.Good read(ServerPlayer p, Trades.Kind kind) {
		int lv = Trades.level(p, kind.trade);
		List<Trades.Good> pool = new ArrayList<>();
		List<Integer> w = new ArrayList<>();
		int total = 0;
		for (Trades.Good g : Trades.GOODS.values()) {
			if (g.kind() != kind || Trades.knows(p, g.id())) continue;
			int wt = g.level() <= lv ? 4 : g.level() <= lv + 6 ? 3 : 1;
			pool.add(g);
			w.add(wt);
			total += wt;
		}
		if (pool.isEmpty()) return null;
		int r = p.getRandom().nextInt(total);
		Trades.Good got = pool.get(pool.size() - 1);
		for (int i = 0; i < pool.size(); i++) {
			r -= w.get(i);
			if (r < 0) {
				got = pool.get(i);
				break;
			}
		}
		Trades.learn(p, got.id());
		told(p, got);
		return got;
	}

	/** "Recipe learnt", what it needs, and whether you can make it yet. */
	static void told(ServerPlayer p, Trades.Good g) {
		List<String> needs = new ArrayList<>();
		for (String n : g.needs()) needs.add(Trades.KIND_NAMES.getOrDefault(n, n));
		Trades.Trade t = Trades.trade(g.kind().trade);
		boolean can = Trades.level(p, t.id()) >= g.level();
		p.displayClientMessage(Component.literal("Recipe learnt: ").withStyle(ChatFormatting.GOLD).append(Component.literal(g.name()).withStyle(ChatFormatting.YELLOW))
				.append(Component.literal(" (" + String.join(", ", needs) + ")").withStyle(ChatFormatting.GRAY)), false);
		if (!can) p.displayClientMessage(Component.literal("You'll make it at " + t.name() + " " + g.level()).withStyle(ChatFormatting.GRAY), false);
		p.playNotifySound(SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 0.8f, 1f);
		p.playNotifySound(SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 0.4f, 1.6f);
	}

	// ---------------------------------------------------------------- where pages turn up

	/** Structure chests: a page now and then, more often in houses, taverns and kitchens. */
	private static void chests(LootTableLoadEvent e) {
		ResourceLocation id = e.getName();
		String ns = id.getNamespace(), path = id.getPath();
		boolean stash = path.contains("chest") || ns.equals("kaisyn") && (path.startsWith("village/") || path.startsWith("outpost/"));
		if (ns.equals(Ashbound.ID) || !stash || path.contains("entities/") || path.contains("archeology") || path.contains("archaeology")) return;
		boolean home = path.contains("village") || path.contains("house") || path.contains("tavern") || path.contains("kitchen") || path.contains("inn")
				|| path.contains("butcher") || path.contains("farm");
		boolean lab = path.contains("witch") || path.contains("alchem") || path.contains("library") || path.contains("stronghold") || path.contains("mage")
				|| path.contains("tower");
		float chance = home ? 0.2f : lab ? 0.15f : 0.08f;
		LootPool.Builder pool = LootPool.lootPool().setRolls(ConstantValue.exactly(1)).when(LootItemRandomChanceCondition.randomChance(chance));
		pool.add(LootItem.lootTableItem(PAGES.get(Trades.Kind.MEAL).get()).setWeight(home ? 5 : 3));
		pool.add(LootItem.lootTableItem(PAGES.get(Trades.Kind.BREW).get()).setWeight(home ? 4 : 2));
		pool.add(LootItem.lootTableItem(PAGES.get(Trades.Kind.ELIXIR).get()).setWeight(lab ? 6 : 2));
		e.getTable().addPool(pool.name("ashbound_recipes").build());
	}

	/** Monsters carry one now and then; bosses and elites more often. */
	private static void died(LivingDeathEvent e) {
		LivingEntity d = e.getEntity();
		if (!(d.level() instanceof ServerLevel) || !(e.getSource().getEntity() instanceof Player) || Spells.isThrall(d) || !(d instanceof Enemy)) return;
		RandomSource r = d.getRandom();
		boolean boss = d instanceof MobSkills.User u && u.kind().boss();
		float chance = boss ? 0.35f : GateLoot.elite(d) ? 0.08f : 0.012f;
		if (r.nextFloat() >= chance) return;
		int k = r.nextInt(7);
		Trades.Kind kind = k < 3 ? Trades.Kind.MEAL : k < 5 ? Trades.Kind.BREW : Trades.Kind.ELIXIR;
		d.spawnAtLocation(new ItemStack(PAGES.get(kind).get()));
	}

	// ---------------------------------------------------------------- townsfolk

	/** The recipes someone knows: the same each time you ask (from who they are), more of their own trade for a cook, brewer or herbalist. */
	static List<Trades.Good> known(Npc npc) {
		Talk.Kind k = npc.kind();
		String who = (npc.kindId() + " " + (k == null ? "" : k.title() + " " + String.join(" ", k.tags())) + " " + npc.shopId()).toLowerCase();
		Trades.Kind lean = null;
		if (has(who, "cook", "chef", "baker", "butcher", "fish", "farmer", "kitchen", "grocer", "food")) lean = Trades.Kind.MEAL;
		else if (has(who, "brew", "tavern", "inn", "barkeep", "bartender", "ale", "vint", "wine", "cellar")) lean = Trades.Kind.BREW;
		else if (has(who, "herb", "alchem", "apothec", "healer", "witch", "mage", "priest", "scholar", "potion", "druid")) lean = Trades.Kind.ELIXIR;
		Random r = new Random(npc.kindId().hashCode() * 31L + npc.getName().getString().hashCode());
		List<Trades.Good> out = new ArrayList<>();
		for (Trades.Kind kind : Trades.Kind.values()) {
			List<Trades.Good> of = new ArrayList<>();
			for (Trades.Good g : Trades.GOODS.values()) if (g.kind() == kind && g.level() > 1) of.add(g);
			// a cook, brewer or herbalist knows three of their own; anyone else, one in five knows a single one
			int n = kind == lean ? 3 : lean == null && kind == Trades.Kind.values()[Math.floorMod(npc.kindId().hashCode(), 3)] && r.nextInt(5) == 0 ? 1 : 0;
			for (int i = 0; i < n && !of.isEmpty(); i++) {
				// most know the plain things; a trade's own people the finer ones too
				int top = kind == lean ? of.size() : Math.max(1, of.size() / 2);
				out.add(of.remove(r.nextInt(Math.min(top, of.size()))));
			}
		}
		out.sort((a, b) -> Integer.compare(a.level(), b.level()));
		return out;
	}

	private static boolean has(String s, String... words) {
		for (String w : words) if (s.contains(w)) return true;
		return false;
	}

	/** What they'd teach you next (their simplest you don't know), or null. */
	private static Trades.Good next(ServerPlayer p, Npc npc) {
		for (Trades.Good g : known(npc)) if (!Trades.knows(p, g.id())) return g;
		return null;
	}

	public static int price(Trades.Good g) {
		return 12 + 3 * g.level();
	}

	/** "Know any good recipes?": only from those who know one you don't (most townsfolk know none). */
	static Talk.Option option(ServerPlayer p, Npc npc) {
		return next(p, npc) == null ? null : new Talk.Option("Know any good recipes?", "", "", "recipe:ask");
	}

	/** The day (24000 ticks) this one last taught you: one recipe a day each. */
	private static String taughtKey(Npc npc) {
		return "taught." + npc.kindId() + "." + npc.getName().getString();
	}

	private static boolean taughtToday(ServerPlayer p, Npc npc) {
		String v = Trades.note(p, taughtKey(npc));
		return v != null && v.equals(String.valueOf(p.level().getDayTime() / 24000));
	}

	private static List<Talk.Option> after() {
		return List.of(new Talk.Option("Something else.", "", "start", ""), new Talk.Option("Goodbye.", "", "", "close"));
	}

	private static final String[][] OFFER = {
			{"My mother's {good}. {needs}, and patience. I'll teach it you for {price} coins.", "Ah, {good}. Not hard once you've seen it done. {price} coins and it's yours.",
					"{good}: {needs}. Everyone in my family can make it. {price} coins, and don't tell my sister I sold it."},
			{"{good}. {needs}, and leave it longer than you think. {price} coins.", "I'll not give away the house brew. But {good}... for {price} coins, maybe.",
					"{good}: {needs}. Learnt it from an old cellarman. {price} coins."},
			{"{good}. {needs}, measured to the grain. {price} coins, and you never heard it from me.", "Careful with {good}: {needs}, no more. {price} coins for the method.",
					"{good}. I wrote it down once and the page caught fire. {price} coins and I'll say it slowly."}};

	/** A choice from the recipe talk; null ends the conversation. */
	static Errands.Reply pick(ServerPlayer p, Npc npc, String act) {
		if (act.equals("recipe:ask")) {
			Trades.Good g = next(p, npc);
			if (g != null && taughtToday(p, npc))
				return new Errands.Reply("One a day, friend. Make that one a few times first, then come back tomorrow.", after());
			if (g == null) {
				String t = known(npc).isEmpty() ? "Me? I eat what's put in front of me. Ask the cooks, or look in old chests: people leave pages in the strangest places."
						: "That's all I know, and you have it now. Old chests and the beasts out there carry torn pages, if you're brave.";
				return new Errands.Reply(t, after());
			}
			List<String> needs = new ArrayList<>();
			for (String n : g.needs()) needs.add(Trades.KIND_NAMES.getOrDefault(n, n).toLowerCase());
			String[] lines = OFFER[g.kind().ordinal()];
			String line = lines[Math.floorMod(npc.getName().getString().hashCode() + g.id().hashCode(), lines.length)];
			String needWords = String.join(", ", needs);
			line = line.replace("{good}", g.name()).replace("{needs}", Character.toUpperCase(needWords.charAt(0)) + needWords.substring(1))
					.replace("{price}", String.valueOf(price(g)));
			Trades.Trade t = Trades.trade(g.kind().trade);
			String level = Trades.level(p, t.id()) >= g.level() ? "" : "\n(You'll make it at " + t.name() + " " + g.level() + ")";
			return new Errands.Reply(line + level, List.of(new Talk.Option("Teach me. (" + price(g) + " coins)", "", "", "recipe:buy:" + g.id()),
					new Talk.Option("Not now.", "", "start", "")));
		}
		if (act.startsWith("recipe:buy:")) {
			String id = act.substring("recipe:buy:".length());
			Trades.Good g = Trades.GOODS.get(id);
			if (g == null || !known(npc).contains(g)) return null;
			if (Trades.knows(p, id)) return new Errands.Reply("You know that one already.", after());
			if (taughtToday(p, npc)) return new Errands.Reply("One a day, friend. Come back tomorrow.", after());
			if (!Coins.pay(p, price(g))) return new Errands.Reply("Come back with " + price(g) + " coins. A recipe's worth more than a meal.", after());
			Trades.learn(p, id);
			Trades.note(p, taughtKey(npc), String.valueOf(p.level().getDayTime() / 24000));
			told(p, g);
			return new Errands.Reply(next(p, npc) != null ? "There. Don't burn it the first time. I know another, but that's for another day."
					: "There. Don't burn it the first time. Everyone does.", after());
		}
		return null;
	}
}
