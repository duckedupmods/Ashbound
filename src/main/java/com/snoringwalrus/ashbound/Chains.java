package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

import javax.annotation.Nullable;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderSet;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.TickTask;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimpleJsonResourceReloadListener;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.world.Container;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.component.ItemLore;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.RandomizableContainerBlockEntity;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.AddReloadListenerEvent;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

/**
 * Quest chains (data/ashbound/chain/*.json): a story told in steps, each one something to do somewhere. The side quests
 * ("bring it to my mum"), the courier runs, and the main quest are all chains. A step is one of:
 * <ul>
 * <li>{@code talk}: speak to someone ({@code to}), who says {@code say} when you say {@code reply};
 * <li>{@code kill}: {@code n} of {@code what}, maybe only {@code when} it's night/ashfall/rain, maybe only near {@code where};
 * <li>{@code find}: {@code item}, which is only there while you're on the step: in a structure's chest ({@code in:
 *     "structure:id"}), a dungeon boss's hoard ({@code "dungeon:gate"}), a legend's carcass ({@code "legend:kind"});
 * <li>{@code event}: {@code item} from a world event ({@code in}: "ashfall" a chance per kill on an ashfall night, "meteor",
 *     "storm", "treasure", "arena", "boss:arena-id"), {@code chance} per drop;
 * <li>{@code deliver}: carry {@code item} to {@code to}; {@code give} hands it to you as the step starts, {@code minutes} puts
 *     a clock on it (a tip if you're quick);
 * <li>{@code boss}: beat {@code what} once;
 * <li>{@code choice}: {@code to} asks, you pick one of {@code choices}; the chain remembers (flag ch:id:flag).
 * </ul>
 * {@code to} is "kind:id", "tag:t", "@giver" (whoever gave you the chain) or a bare kind id or tag. {@code where} is what the
 * compass points at: "capital", "at:x,z" in the city, "gate:R", "village" or "village:kind" (the nearest), "structure:id",
 * "@giver". A party shares its kills and its finds; a talk done is done for the party members standing by.
 */
public final class Chains {
	private Chains() {}

	public static final String TAG = "ashbound_chain";
	static final String SIDE = "fav:ch:", MAIN = "ch:";

	// ---------------------------------------------------------------- the data

	record Choice(String text, String flag, String say) {}

	record Step(String kind, String text, String what, int n, String where, String to, String in, String item, String name, String lore,
				float chance, String when, String say, String reply, boolean give, int minutes, List<Choice> choices) {}

	/** type: "side", "courier", "main". auto: given without asking once `after` holds (the main quest's acts). */
	record Chain(String id, String title, String type, String giver, String after, int rank, boolean repeat, boolean auto, String hook, String ask,
				 String thanks, int coins, int points, List<String> items, List<Step> steps) {
		boolean main() {
			return type.equals("main");
		}

		String key() {
			return (main() ? MAIN : SIDE) + id;
		}
	}

	static final Map<String, Chain> ALL = new java.util.LinkedHashMap<>();

	private static String str(JsonObject o, String k, String or) {
		return o.has(k) ? o.get(k).getAsString() : or;
	}

	private static void load(Map<ResourceLocation, JsonElement> files) {
		ALL.clear();
		for (var f : files.entrySet()) {
			List<JsonElement> list = new ArrayList<>();
			if (f.getValue().isJsonArray()) f.getValue().getAsJsonArray().forEach(list::add);
			else list.add(f.getValue());
			for (JsonElement e : list) {
				try {
					Chain c = chain(e.getAsJsonObject());
					ALL.put(c.id(), c);
				} catch (RuntimeException ex) {
					Ashbound.LOG.error("[Ashbound] bad chain in {}: {}", f.getKey(), ex.toString());
				}
			}
		}
		Ashbound.LOG.info("[Ashbound] {} quest chains", ALL.size());
	}

	static Chain chain(JsonObject o) {
		List<Step> steps = new ArrayList<>();
		for (JsonElement se : o.getAsJsonArray("steps")) {
			JsonObject s = se.getAsJsonObject();
			List<Choice> ch = new ArrayList<>();
			if (s.has("choices"))
				for (JsonElement ce : s.getAsJsonArray("choices")) {
					JsonObject c = ce.getAsJsonObject();
					ch.add(new Choice(str(c, "text", "..."), str(c, "flag", ""), str(c, "say", "")));
				}
			steps.add(new Step(str(s, "do", "talk"), str(s, "text", ""), str(s, "what", ""), s.has("n") ? s.get("n").getAsInt() : 1, str(s, "where", ""),
					str(s, "to", ""), str(s, "in", ""), str(s, "item", ""), str(s, "name", ""), str(s, "lore", ""),
					s.has("chance") ? s.get("chance").getAsFloat() : 1f, str(s, "when", ""), str(s, "say", ""), str(s, "reply", ""),
					s.has("give") && s.get("give").getAsBoolean(), s.has("minutes") ? s.get("minutes").getAsInt() : 0, ch));
		}
		List<String> items = new ArrayList<>();
		if (o.has("items")) o.getAsJsonArray("items").forEach(i -> items.add(i.getAsString()));
		String rank = str(o, "rank", "F");
		return new Chain(o.get("id").getAsString(), str(o, "title", "A favour"), str(o, "type", "side"), str(o, "giver", ""), str(o, "after", ""),
				Math.max(0, "FEDCBAS".indexOf(rank)), o.has("repeat") && o.get("repeat").getAsBoolean(), o.has("auto") && o.get("auto").getAsBoolean(),
				str(o, "hook", ""), str(o, "ask", ""), str(o, "thanks", "Thank you."), o.has("coins") ? o.get("coins").getAsInt() : 0,
				o.has("points") ? o.get("points").getAsInt() : 0, items, steps);
	}

	// ---------------------------------------------------------------- what you're on

	/** One chain under way: which step, how far along, the clock, where the compass points, who gave it you. */
	public record Prog(String id, int step, int n, long deadline, int x, int z, boolean has, String giver, String giverName, int gx, int gz) {
		static final Codec<Prog> CODEC = RecordCodecBuilder.create(i -> i.group(
				Codec.STRING.fieldOf("id").forGetter(Prog::id),
				Codec.INT.fieldOf("step").forGetter(Prog::step),
				Codec.INT.fieldOf("n").forGetter(Prog::n),
				Codec.LONG.fieldOf("deadline").forGetter(Prog::deadline),
				Codec.INT.fieldOf("x").forGetter(Prog::x),
				Codec.INT.fieldOf("z").forGetter(Prog::z),
				Codec.BOOL.fieldOf("has").forGetter(Prog::has),
				Codec.STRING.fieldOf("giver").forGetter(Prog::giver),
				Codec.STRING.fieldOf("giver_name").forGetter(Prog::giverName),
				Codec.INT.fieldOf("gx").forGetter(Prog::gx),
				Codec.INT.fieldOf("gz").forGetter(Prog::gz)
		).apply(i, Prog::new));

		Prog n(int v) {
			return new Prog(id, step, v, deadline, x, z, has, giver, giverName, gx, gz);
		}

		@Nullable Chain chain() {
			return ALL.get(id);
		}

		@Nullable Step now() {
			Chain c = chain();
			return c == null || step >= c.steps().size() ? null : c.steps().get(step);
		}
	}

	static final DeferredRegister<AttachmentType<?>> ATTACHMENTS = DeferredRegister.create(NeoForgeRegistries.ATTACHMENT_TYPES, Ashbound.ID);
	public static final Supplier<AttachmentType<List<Prog>>> STATE = ATTACHMENTS.register("chains",
			() -> AttachmentType.<List<Prog>>builder(() -> List.of()).serialize(Prog.CODEC.listOf()).copyOnDeath().build());

	static List<Prog> on(ServerPlayer p) {
		return p.getData(STATE);
	}

	@Nullable
	static Prog prog(ServerPlayer p, String id) {
		for (Prog g : on(p)) if (g.id().equals(id)) return g;
		return null;
	}

	private static void put(ServerPlayer p, Prog g) {
		List<Prog> list = new ArrayList<>(on(p));
		list.removeIf(o -> o.id().equals(g.id()));
		list.add(g);
		p.setData(STATE, list);
	}

	private static void drop(ServerPlayer p, String id) {
		List<Prog> list = new ArrayList<>(on(p));
		if (list.removeIf(o -> o.id().equals(id))) p.setData(STATE, list);
	}

	static boolean done(ServerPlayer p, Chain c) {
		return Coins.flag(p, "ch:" + c.id());
	}

	/** By the Journal's key ("fav:ch:id" or "ch:id"). */
	@Nullable
	static Prog find(ServerPlayer p, String key) {
		String id = key.startsWith(SIDE) ? key.substring(SIDE.length()) : key.startsWith(MAIN) ? key.substring(MAIN.length()) : null;
		return id == null ? null : prog(p, id);
	}

	static boolean isKey(String key) {
		return key.startsWith(SIDE) || key.startsWith(MAIN);
	}

	// ---------------------------------------------------------------- starting one, moving on

	static boolean can(ServerPlayer p, Chain c) {
		if (prog(p, c.id()) != null || (done(p, c) && !c.repeat())) return false;
		if (c.repeat() && Coins.flag(p, "chday:" + c.id() + ":" + Errands.day(p))) return false;   // once a day
		if (Guild.of(p).rank() < c.rank()) return false;
		return c.after().isEmpty() || Talk.test(p, c.after());
	}

	static void start(ServerPlayer p, Chain c, @Nullable Npc giver) {
		Prog g = new Prog(c.id(), 0, 0, 0, 0, 0, false, giver == null ? "" : giver.getStringUUID(), giver == null ? "" : giver.kind().name(),
				giver == null ? p.getBlockX() : giver.getBlockX(), giver == null ? p.getBlockZ() : giver.getBlockZ());
		put(p, g);
		p.level().playSound(null, p.blockPosition(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 1f, 1.1f);
		p.sendSystemMessage(Component.literal(c.main() ? "Story: " : "Quest: ").withStyle(ChatFormatting.GRAY).append(Component.literal(c.title()).withStyle(ChatFormatting.GOLD)));
		enter(p, g);
		Story.pick(p, c.key());
	}

	/** A step begins: hand over what it gives, start its clock, find where it is. */
	private static void enter(ServerPlayer p, Prog g) {
		Step s = g.now();
		Chain c = g.chain();
		if (s == null || c == null) return;
		long deadline = s.minutes() > 0 ? p.level().getGameTime() + s.minutes() * 1200L : 0;
		int[] at = where(p, g, s.where());
		g = new Prog(g.id(), g.step(), 0, deadline, at == null ? 0 : at[0], at == null ? 0 : at[1], at != null, g.giver(), g.giverName(), g.gx(), g.gz());
		put(p, g);
		if (s.give() && !s.item().isEmpty()) give(p, token(s, c.id(), s.n()));
		if (!s.text().isEmpty()) p.sendSystemMessage(Component.literal("  " + s.text() + (s.minutes() > 0 ? " (" + s.minutes() + " min)" : "")).withStyle(ChatFormatting.GRAY));
		sync(p);
		// a find or event step you've already got the things for is done as soon as it starts
		if ((s.kind().equals("find") || s.kind().equals("event")) && carried(p, s, c.id()) >= s.n()) next(p, g);
	}

	/** On to the next step, or the end and its reward. */
	static void next(ServerPlayer p, Prog g) {
		Chain c = g.chain();
		if (c == null) {
			drop(p, g.id());
			return;
		}
		Prog n = new Prog(g.id(), g.step() + 1, 0, 0, 0, 0, false, g.giver(), g.giverName(), g.gx(), g.gz());
		if (n.step() >= c.steps().size()) {
			finish(p, c, g);
			return;
		}
		put(p, n);
		p.level().playSound(null, p.blockPosition(), SoundEvents.EXPERIENCE_ORB_PICKUP, SoundSource.PLAYERS, 0.6f, 1.3f);
		enter(p, n);
	}

	private static void finish(ServerPlayer p, Chain c, Prog g) {
		drop(p, c.id());
		Coins.setFlag(p, "ch:" + c.id());
		if (c.repeat()) {
			List<String> fl = new ArrayList<>(p.getData(Coins.FLAGS));
			fl.removeIf(f -> f.startsWith("chday:" + c.id() + ":"));
			fl.add("chday:" + c.id() + ":" + Errands.day(p));
			p.setData(Coins.FLAGS, fl);
		}
		int coins = c.coins();
		if (g.deadline() > 0 && p.level().getGameTime() < g.deadline() - (long) (minutesOf(g) * 600)) coins += Math.max(5, coins / 2);   // under half the time: a tip
		if (coins > 0) Coins.give(p, coins);
		if (c.points() > 0 && Guild.of(p).registered()) Guild.points(p, c.points());
		StringBuilder got = new StringBuilder();
		for (String it : c.items()) {
			ItemStack s = stack(it);
			if (s.isEmpty()) continue;
			got.append(", ").append(s.getCount() > 1 ? s.getCount() + " " : "").append(s.getHoverName().getString());
			give(p, s);
		}
		p.sendSystemMessage(Component.literal(c.title()).withStyle(ChatFormatting.GOLD).append(Component.literal(" - done!").withStyle(ChatFormatting.GREEN)));
		if (coins > 0 || got.length() > 0 || c.points() > 0)
			p.sendSystemMessage(Component.literal("  " + (coins > 0 ? "+" + coins + " coins" : "") + (c.points() > 0 && Guild.of(p).registered() ? ", +" + c.points() + " GP" : "") + got)
					.withStyle(ChatFormatting.YELLOW));
		p.playNotifySound(SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.PLAYERS, 0.8f, 1.1f);
		sync(p);
		Story.state(p);
		autos(p);
	}

	private static int minutesOf(Prog g) {
		Step s = g.now();
		return s == null ? 0 : s.minutes();
	}

	/** Given up (side quests only): its things go with it. */
	static void abandon(ServerPlayer p, String key) {
		Prog g = find(p, key);
		if (g == null || g.chain() == null || g.chain().main()) return;
		take(p, g.id(), Integer.MAX_VALUE, null);
		drop(p, g.id());
		p.sendSystemMessage(Component.literal("You gave up on " + g.chain().title() + ".").withStyle(ChatFormatting.GRAY));
		sync(p);
	}

	/** The story's acts, handed to you once what comes before is done. */
	static void autos(ServerPlayer p) {
		for (Chain c : ALL.values()) if (c.auto() && can(p, c)) start(p, c, null);
	}

	// ---------------------------------------------------------------- things

	static ItemStack stack(String spec) {
		String[] sp = spec.trim().split(" ");
		Item it = BuiltInRegistries.ITEM.get(ResourceLocation.parse(sp[0]));
		return it == net.minecraft.world.item.Items.AIR ? ItemStack.EMPTY : new ItemStack(it, sp.length > 1 ? Integer.parseInt(sp[1]) : 1);
	}

	/** The step's thing: a named one is marked as this chain's (and only counts for it); a plain one is any of that item. */
	static ItemStack token(Step s, String chain, int n) {
		ItemStack st = stack(s.item());
		if (st.isEmpty()) return st;
		st.setCount(Math.max(1, n));
		if (!s.name().isEmpty()) {
			st.set(DataComponents.CUSTOM_NAME, Component.literal(s.name()).withStyle(st2 -> st2.withItalic(false).withColor(ChatFormatting.GOLD)));
			if (!s.lore().isEmpty()) st.set(DataComponents.LORE, new ItemLore(List.of(Component.literal(s.lore()).withStyle(st2 -> st2.withItalic(true).withColor(ChatFormatting.GRAY)))));
			CustomData.update(DataComponents.CUSTOM_DATA, st, t -> t.putString(TAG, chain));
		}
		return st;
	}

	private static boolean matches(ItemStack have, Step s, String chain) {
		if (have.isEmpty() || s.item().isEmpty()) return false;
		ItemStack want = stack(s.item());
		if (want.isEmpty() || !have.is(want.getItem())) return false;
		if (s.name().isEmpty()) return true;
		CustomData d = have.get(DataComponents.CUSTOM_DATA);
		return d != null && chain.equals(d.copyTag().getString(TAG));
	}

	static int carried(ServerPlayer p, Step s, String chain) {
		int n = 0;
		for (ItemStack i : p.getInventory().items) if (matches(i, s, chain)) n += i.getCount();
		for (ItemStack i : p.getInventory().offhand) if (matches(i, s, chain)) n += i.getCount();
		return n;
	}

	/** Takes up to n of a step's thing (null step: every thing marked for this chain). */
	private static void take(ServerPlayer p, String chain, int n, @Nullable Step s) {
		var inv = p.getInventory();
		for (int i = 0; i < inv.getContainerSize() && n > 0; i++) {
			ItemStack it = inv.getItem(i);
			boolean ours = s != null ? matches(it, s, chain) : it.has(DataComponents.CUSTOM_DATA) && chain.equals(it.get(DataComponents.CUSTOM_DATA).copyTag().getString(TAG));
			if (!ours) continue;
			int k = Math.min(n, it.getCount());
			it.shrink(k);
			n -= k;
		}
	}

	private static void give(ServerPlayer p, ItemStack s) {
		if (s.isEmpty()) return;
		if (!p.getInventory().add(s)) p.drop(s, false);
	}

	/** Theirs alone, where it fell. */
	private static void spill(ServerLevel l, ServerPlayer p, double x, double y, double z, ItemStack s) {
		ItemEntity ie = new ItemEntity(l, x, y, z, s);
		ie.setDefaultPickUpDelay();
		ie.setTarget(p.getUUID());
		Dropped.markFor(ie, p);
		l.addFreshEntity(ie);
	}

	// ---------------------------------------------------------------- where

	@Nullable
	static int[] where(ServerPlayer p, Prog g, String code) {
		if (code.isEmpty()) return null;
		if (code.equals("@giver")) return g.giver().isEmpty() ? null : new int[] {g.gx(), g.gz()};
		if (code.startsWith("village")) {
			Capital.Site best = village(p, code);
			return best == null ? null : new int[] {best.x, best.z};
		}
		if (code.startsWith("structure:")) {
			if (!(p.level() instanceof ServerLevel l)) return null;
			var reg = l.registryAccess().registryOrThrow(Registries.STRUCTURE);
			var h = reg.getHolder(ResourceKey.create(Registries.STRUCTURE, ResourceLocation.parse(code.substring(10))));
			if (h.isEmpty()) return null;
			var found = l.getChunkSource().getGenerator().findNearestMapStructure(l, HolderSet.direct(h.get()), p.blockPosition(), 100, false);
			return found == null ? null : new int[] {found.getFirst().getX(), found.getFirst().getZ()};
		}
		return Story.where(p, code);
	}

	@Nullable
	static Capital.Site village(ServerPlayer p, String code) {
		String kind = code.startsWith("village:") ? code.substring(8) : "";
		Capital.Site best = null;
		for (Capital.Site s : Capital.sites) {
			if (s.name.equals("highmourn") || (!kind.isEmpty() && !s.name.equals(kind))) continue;
			if (best == null || dist(p, s.x, s.z) < dist(p, best.x, best.z)) best = s;
		}
		return best;
	}

	private static double dist(Player p, int x, int z) {
		double dx = p.getX() - x, dz = p.getZ() - z;
		return dx * dx + dz * dz;
	}

	/** Is this the one the step means, and are they where it says? */
	static boolean who(ServerPlayer p, Prog g, Step s, Npc npc) {
		String to = s.to();
		boolean is;
		if (to.equals("@giver")) is = npc.getStringUUID().equals(g.giver());
		else if (to.startsWith("kind:")) is = npc.kindId().equals(to.substring(5));
		else if (to.startsWith("tag:")) is = npc.is(to.substring(4));
		else is = npc.kindId().equals(to) || npc.is(to);
		if (!is) return false;
		// "an elf at Lumenhollow": anyone with the tag will do, but only there
		if (!to.equals("@giver") && !to.startsWith("kind:") && g.has() && !s.where().isEmpty() && !s.where().startsWith("gate:")) {
			double dx = npc.getX() - g.x(), dz = npc.getZ() - g.z();
			int r = s.where().equals("capital") ? 320 : 200;
			return dx * dx + dz * dz < r * r;
		}
		return true;
	}

	// ---------------------------------------------------------------- in the conversation (Talk)

	/** A line they'd open with when they've a chain to give you; "" if not. */
	static String hook(ServerPlayer p, Npc npc) {
		Chain c = offer(p, npc);
		return c == null ? "" : c.hook();
	}

	@Nullable
	private static Chain offer(ServerPlayer p, Npc npc) {
		for (Chain c : ALL.values()) {
			if (c.auto() || c.giver().isEmpty() || !can(p, c)) continue;
			String gv = c.giver();
			boolean is = gv.startsWith("kind:") ? npc.kindId().equals(gv.substring(5)) : gv.startsWith("tag:") ? npc.is(gv.substring(4)) : npc.kindId().equals(gv) || npc.is(gv);
			// asked by "any smith": only one in four of them has it to ask, so not every smith in the city opens with it
			if (is && !gv.startsWith("kind:") && ((npc.getUUID().hashCode() ^ c.id().hashCode()) & 3) != 0) continue;
			if (is) return c;
		}
		return null;
	}

	static List<Talk.Option> options(ServerPlayer p, Npc npc) {
		List<Talk.Option> out = new ArrayList<>();
		for (Prog g : on(p)) {
			Step s = g.now();
			if (s == null || !(s.kind().equals("talk") || s.kind().equals("deliver") || s.kind().equals("choice")) || !who(p, g, s, npc)) continue;
			if (s.kind().equals("deliver") && carried(p, s, g.id()) < s.n()) continue;
			out.add(new Talk.Option(s.reply().isEmpty() ? s.kind().equals("deliver") ? "I've something for you." : "About " + g.chain().title() + "..." : s.reply(), "", "",
					"chain:" + g.id() + ":" + s.kind()));
		}
		Chain c = offer(p, npc);
		if (c != null) out.add(new Talk.Option(c.main() ? "What is it?" : "Do you need something?", "", "", "chain:" + c.id() + ":hear"));
		return out;
	}

	private static final List<Talk.Option> BYE = List.of(new Talk.Option("Something else.", "", "start", ""), new Talk.Option("Goodbye.", "", "", "close"));

	@Nullable
	static Errands.Reply pick(ServerPlayer p, Npc npc, String act) {
		String[] a = act.split(":");
		if (a.length < 3) return null;
		Chain c = ALL.get(a[1]);
		if (c == null) return null;
		Prog g = prog(p, c.id());
		switch (a[2]) {
			case "hear" -> {
				if (!can(p, c)) return null;
				String reward = (c.coins() > 0 ? c.coins() + " coins" : "") + (c.points() > 0 && Guild.of(p).registered() ? (c.coins() > 0 ? ", " : "") + c.points() + " GP" : "");
				for (String it : c.items()) {
					ItemStack s = stack(it);
					if (!s.isEmpty()) reward += (reward.isEmpty() ? "" : ", ") + s.getHoverName().getString();
				}
				String first = c.steps().isEmpty() ? "" : c.steps().get(0).text();
				return new Errands.Reply(c.ask() + (first.isEmpty() ? "" : "\n\n" + first) + (reward.isEmpty() ? "" : "\nReward: " + reward),
						List.of(new Talk.Option("I'll do it.", "", "", "chain:" + c.id() + ":take"), new Talk.Option("Not now.", "", "", "chain:" + c.id() + ":no")));
			}
			case "take" -> {
				if (!can(p, c)) return null;
				start(p, c, npc);
				return new Errands.Reply("Thank you. Truly.", BYE);
			}
			case "no" -> {
				return new Errands.Reply("If you change your mind, I'll be here.", BYE);
			}
			case "pick" -> {
				Step s = g == null ? null : g.now();
				if (s == null || !s.kind().equals("choice") || a.length < 4) return null;
				Choice ch = s.choices().get(Math.min(Integer.parseInt(a[3]), s.choices().size() - 1));
				if (!ch.flag().isEmpty()) Coins.setFlag(p, "ch:" + c.id() + ":" + ch.flag());
				advanceHere(p, c, s, npc);
				return new Errands.Reply(ch.say().isEmpty() ? "So be it." : ch.say(), BYE);
			}
			default -> {}
		}
		Step s = g == null ? null : g.now();
		if (s == null || !s.kind().equals(a[2]) || !who(p, g, s, npc)) return null;
		if (s.kind().equals("choice")) {
			List<Talk.Option> opts = new ArrayList<>();
			for (int i = 0; i < s.choices().size(); i++) opts.add(new Talk.Option(s.choices().get(i).text(), "", "", "chain:" + c.id() + ":pick:" + i));
			return new Errands.Reply(s.say(), opts);
		}
		if (s.kind().equals("deliver")) {
			if (carried(p, s, c.id()) < s.n()) return null;
			take(p, c.id(), s.n(), s);
		}
		String say = s.say().isEmpty() ? c.thanks() : s.say();
		advanceHere(p, c, s, npc);
		return new Errands.Reply(say, BYE);
	}

	/** A talk done for you and for your party standing by on the same step. */
	private static void advanceHere(ServerPlayer p, Chain c, Step s, Npc npc) {
		List<ServerPlayer> who = new ArrayList<>();
		who.add(p);
		for (ServerPlayer o : Party.others(p)) if (o.level() == p.level() && o.distanceTo(npc) < 16) who.add(o);
		for (ServerPlayer o : who) {
			Prog g = prog(o, c.id());
			if (g != null && g.now() == s) next(o, g);
		}
	}

	// ---------------------------------------------------------------- out in the world

	private static boolean when(Level l, Step s) {
		return switch (s.when()) {
			case "night" -> l.isNight();
			case "ashfall" -> Ashfall.on(l);
			case "rain" -> l.isRaining();
			default -> true;
		};
	}

	private static boolean near(ServerPlayer p, Prog g, Step s) {
		if (s.where().isEmpty() || !g.has() || s.where().startsWith("gate:")) return true;
		double dx = p.getX() - g.x(), dz = p.getZ() - g.z();
		return dx * dx + dz * dz < 160 * 160;
	}

	private static void killed(LivingDeathEvent e) {
		LivingEntity dead = e.getEntity();
		if (!(dead.level() instanceof ServerLevel l) || dead instanceof Player || Spells.isThrall(dead)) return;
		if (!(e.getSource().getEntity() instanceof ServerPlayer killer)) return;
		String id = BuiltInRegistries.ENTITY_TYPE.getKey(dead.getType()).toString();
		String path = BuiltInRegistries.ENTITY_TYPE.getKey(dead.getType()).getPath();
		String gate = null;
		for (Gear.Dungeon d : Gear.DUNGEONS) if (d.boss().equals(path)) gate = d.gate();
		List<ServerPlayer> there = new ArrayList<>(l.getEntitiesOfClass(ServerPlayer.class, dead.getBoundingBox().inflate(48), q -> !q.isSpectator()));
		if (!there.contains(killer)) there.add(killer);
		for (ServerPlayer q : Party.alongside(there, Party.SHARE)) if (!there.contains(q)) there.add(q);
		for (ServerPlayer p : there) {
			for (Prog g : new ArrayList<>(on(p))) {
				Step s = g.now();
				Chain c = g.chain();
				if (s == null || c == null) continue;
				switch (s.kind()) {
					case "kill", "boss" -> {
						boolean hit = s.what().equals(id) || s.what().equals("@any") || s.what().equals("@haunt") && Haunts.garrison(dead);
						if (!hit || !when(l, s) || !near(p, g, s)) continue;
						int n = g.n() + 1;
						if (n >= s.n()) {
							p.sendSystemMessage(Component.literal(c.title()).withStyle(ChatFormatting.GOLD).append(Component.literal(" - " + (s.kind().equals("boss") ? "it's dead." : "that's all of them.")).withStyle(ChatFormatting.GREEN)));
							next(p, g);
						} else {
							put(p, g.n(n));
							p.displayClientMessage(Component.literal(c.title() + "  " + n + " / " + s.n()).withStyle(ChatFormatting.GOLD), true);
							sync(p);
						}
					}
					case "find", "event" -> {
						boolean from = s.in().equals("dungeon:" + gate) || s.in().equals("legend:" + path) || s.in().equals("kill:" + id)
								|| s.in().equals("ashfall") && Ashfall.on(l);
						if (!from || p.getRandom().nextFloat() >= s.chance() || carried(p, s, c.id()) >= s.n()) continue;
						spill(l, p, dead.getX(), dead.getY() + 0.5, dead.getZ(), token(s, c.id(), 1));
						p.displayClientMessage(Component.literal("Something of " + c.title() + " drops!").withStyle(ChatFormatting.GOLD), true);
					}
					default -> {}
				}
			}
		}
	}

	/** A world event's loot shower (meteor, storm, treasure, arena, boss:id): the quest things it brings p, to rain down with it. */
	static List<ItemStack> extra(ServerPlayer p, String source) {
		List<ItemStack> out = new ArrayList<>();
		for (Prog g : on(p)) {
			Step s = g.now();
			Chain c = g.chain();
			if (s == null || c == null || !(s.kind().equals("event") || s.kind().equals("find")) || !s.in().equals(source)) continue;
			int want = s.n() - carried(p, s, c.id());
			if (want <= 0 || p.getRandom().nextFloat() >= s.chance()) continue;
			out.add(token(s, c.id(), source.equals("meteor") || source.startsWith("boss:") ? want : 1));
		}
		return out;
	}

	/** A structure's chest opened for the first time: the thing you're looking for is in it. */
	private static void opened(PlayerInteractEvent.RightClickBlock e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || !(p.level() instanceof ServerLevel l) || on(p).isEmpty()) return;
		BlockEntity be = l.getBlockEntity(e.getPos());
		if (!(be instanceof RandomizableContainerBlockEntity rc) || rc.getLootTable() == null) return;
		BlockPos pos = e.getPos();
		for (Prog g : on(p)) {
			Step s = g.now();
			Chain c = g.chain();
			if (s == null || c == null || !s.kind().equals("find") || !s.in().startsWith("structure:") || carried(p, s, c.id()) >= s.n()) continue;
			ResourceKey<Structure> key = ResourceKey.create(Registries.STRUCTURE, ResourceLocation.parse(s.in().substring(10)));
			if (!l.structureManager().getStructureWithPieceAt(pos, (net.minecraft.core.Holder<Structure> h) -> h.is(key)).isValid()) continue;
			ItemStack t = token(s, c.id(), s.n() - carried(p, s, c.id()));
			// once the chest's own loot is in it (it fills as it opens)
			l.getServer().tell(new TickTask(l.getServer().getTickCount() + 1, () -> {
				if (be instanceof Container ct) {
					for (int i = 0; i < ct.getContainerSize(); i++)
						if (ct.getItem(i).isEmpty()) {
							ct.setItem(i, t);
							ct.setChanged();
							p.displayClientMessage(Component.literal("There it is: " + t.getHoverName().getString() + "!").withStyle(ChatFormatting.GOLD), true);
							return;
						}
				}
				give(p, t);
			}));
		}
	}

	/** Now and then: things picked up finish a find, a clock runs out. */
	private static void tick(PlayerTickEvent.Post e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || p.tickCount % 20 != 7) return;
		List<Prog> list = on(p);
		if (list.isEmpty()) {
			if (p.tickCount % 400 == 7) autos(p);
			return;
		}
		long now = p.level().getGameTime();
		for (Prog g : new ArrayList<>(list)) {
			Step s = g.now();
			Chain c = g.chain();
			if (c == null) {
				drop(p, g.id());
				continue;
			}
			if (s == null) continue;
			if ((s.kind().equals("find") || s.kind().equals("event")) && carried(p, s, c.id()) >= s.n()) {
				p.sendSystemMessage(Component.literal(c.title()).withStyle(ChatFormatting.GOLD).append(Component.literal(" - you have it.").withStyle(ChatFormatting.GREEN)));
				next(p, g);
			} else if (g.deadline() > 0 && now > g.deadline() && !c.main()) {
				take(p, c.id(), Integer.MAX_VALUE, null);
				drop(p, c.id());
				p.sendSystemMessage(Component.literal(c.title() + ": too late. Whoever was waiting has given up.").withStyle(ChatFormatting.RED));
				sync(p);
			} else if (g.deadline() > 0 && p.tickCount % 200 == 7) {
				long left = (g.deadline() - now) / 20;
				p.displayClientMessage(Component.literal(c.title() + ": " + left / 60 + ":" + String.format("%02d", left % 60) + " left").withStyle(ChatFormatting.GOLD), true);
			}
		}
		if (p.tickCount % 400 == 7) autos(p);
	}

	// ---------------------------------------------------------------- the Journal and the compass

	/** Your chains as the Journal's favours page lists them. */
	static List<Errands.View> views(ServerPlayer p) {
		List<Errands.View> out = new ArrayList<>();
		for (Prog g : on(p)) {
			Chain c = g.chain();
			Step s = g.now();
			if (c == null || s == null) continue;
			String left = s.kind().equals("kill") && s.n() > 1 ? "  " + g.n() + "/" + s.n()
					: (s.kind().equals("find") || s.kind().equals("event")) && s.n() > 1 ? "  " + Math.min(carried(p, s, c.id()), s.n()) + "/" + s.n() : "";
			String step = "Step " + (g.step() + 1) + " of " + c.steps().size();
			String where = g.has() ? step + " - near " + g.x() + ", " + g.z() : step;
			out.add(new Errands.View((c.main() ? "✦ " : "") + c.title(), (s.text().isEmpty() ? s.kind() : s.text()) + left, where, false, c.key()));
		}
		return out;
	}

	@Nullable
	static Net.QuestTrack track(ServerPlayer p, String key) {
		Prog g = find(p, key);
		Chain c = g == null ? null : g.chain();
		if (c == null) return null;
		boolean here = p.level().dimension() == Level.OVERWORLD;
		return new Net.QuestTrack(c.title(), g.x(), g.z(), g.has() && here);
	}

	static void sync(ServerPlayer p) {
		Errands.sync(p);
	}

	// ---------------------------------------------------------------- testing

	private static void commands(RegisterCommandsEvent e) {
		e.getDispatcher().register(Commands.literal("ashbound").requires(c -> c.hasPermission(2)).then(Commands.literal("chain")
				.then(Commands.literal("start").then(Commands.argument("id", StringArgumentType.word()).suggests((c, b) -> {
					ALL.keySet().forEach(b::suggest);
					return b.buildFuture();
				}).executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					Chain ch = ALL.get(StringArgumentType.getString(c, "id"));
					if (ch == null) return 0;
					drop(p, ch.id());
					start(p, ch, null);
					return 1;
				})))
				.then(Commands.literal("next").executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					List<Prog> list = on(p);
					if (list.isEmpty()) return 0;
					Prog g = list.get(list.size() - 1);
					Step s = g.now();
					if (s != null && (s.kind().equals("find") || s.kind().equals("event") || s.kind().equals("deliver")) && carried(p, s, g.id()) < s.n())
						give(p, token(s, g.id(), s.n() - carried(p, s, g.id())));
					else next(p, g);
					return 1;
				}))
				.then(Commands.literal("list").executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					for (Prog g : on(p))
						c.getSource().sendSuccess(() -> Component.literal(g.id() + " step " + (g.step() + 1) + " n " + g.n()), false);
					c.getSource().sendSuccess(() -> Component.literal(ALL.size() + " chains loaded"), false);
					return 1;
				}))));
	}

	static void init(IEventBus bus) {
		ATTACHMENTS.register(bus);
		NeoForge.EVENT_BUS.addListener(Chains::killed);
		NeoForge.EVENT_BUS.addListener(Chains::opened);
		NeoForge.EVENT_BUS.addListener(Chains::tick);
		NeoForge.EVENT_BUS.addListener(Chains::commands);
		NeoForge.EVENT_BUS.addListener((AddReloadListenerEvent e) -> e.addListener(new SimpleJsonResourceReloadListener(new Gson(), "chain") {
			@Override
			protected void apply(Map<ResourceLocation, JsonElement> files, ResourceManager rm, ProfilerFiller pf) {
				load(files);
			}
		}));
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedInEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer sp) autos(sp);
		});
	}
}
