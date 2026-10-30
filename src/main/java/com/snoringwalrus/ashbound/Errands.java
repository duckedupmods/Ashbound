package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.function.Supplier;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;

import io.netty.buffer.ByteBuf;
import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimpleJsonResourceReloadListener;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.AddReloadListenerEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

/**
 * Favours: townsfolk who, now and then, ask you for something when you stop to talk (tools/errands.py writes the list
 * to data/ashbound/errand/errands.json). Who asks and what's fixed for a couple of days per person and player, so
 * talking to them again doesn't roll again. Something slain, something brought, a letter carried; you go back to
 * whoever asked (a letter is paid for where it lands). No guild card needed: the pay's coin, plus Guild Points if
 * you're registered, plus whatever they can spare. Three at a time; a favour left a week is forgotten.
 */
public final class Errands {
	private Errands() {}

	public static final int MAX = 3, KILL = 0, COLLECT = 1, DELIVER = 2;
	private static final int CYCLE = 2, EXPIRE = 7;

	public record Errand(String template, int type, String target, int count, int progress, int coins, int points, String giver, String giverName,
						 int x, int z, long day, String title, String objective) {
		static final Codec<Errand> CODEC = RecordCodecBuilder.create(i -> i.group(
				Codec.STRING.fieldOf("template").forGetter(Errand::template),
				Codec.INT.fieldOf("type").forGetter(Errand::type),
				Codec.STRING.fieldOf("target").forGetter(Errand::target),
				Codec.INT.fieldOf("count").forGetter(Errand::count),
				Codec.INT.fieldOf("progress").forGetter(Errand::progress),
				Codec.INT.fieldOf("coins").forGetter(Errand::coins),
				Codec.INT.fieldOf("points").forGetter(Errand::points),
				Codec.STRING.fieldOf("giver").forGetter(Errand::giver),
				Codec.STRING.fieldOf("giver_name").forGetter(Errand::giverName),
				Codec.INT.fieldOf("x").forGetter(Errand::x),
				Codec.INT.fieldOf("z").forGetter(Errand::z),
				Codec.LONG.fieldOf("day").forGetter(Errand::day),
				Codec.STRING.fieldOf("title").forGetter(Errand::title),
				Codec.STRING.fieldOf("objective").forGetter(Errand::objective)
		).apply(i, Errand::new));

		Errand advanced() {
			return new Errand(template, type, target, count, progress + 1, coins, points, giver, giverName, x, z, day, title, objective);
		}
	}

	/** What you've taken on, and who you've already answered this cycle ("uuid:cycle"). */
	public record State(List<Errand> errands, List<String> asked) {
		static final State NEW = new State(List.of(), List.of());
		static final Codec<State> CODEC = RecordCodecBuilder.create(i -> i.group(
				Errand.CODEC.listOf().optionalFieldOf("errands", List.of()).forGetter(State::errands),
				Codec.STRING.listOf().optionalFieldOf("asked", List.of()).forGetter(State::asked)
		).apply(i, State::new));
	}

	/** One favour as your guild card lists it. */
	public record View(String title, String objective, String where, boolean ready) {
		public static final StreamCodec<ByteBuf, View> STREAM = StreamCodec.composite(
				ByteBufCodecs.STRING_UTF8, View::title, ByteBufCodecs.STRING_UTF8, View::objective,
				ByteBufCodecs.STRING_UTF8, View::where, ByteBufCodecs.BOOL, View::ready, View::new);
	}

	static final DeferredRegister<AttachmentType<?>> ATTACHMENTS = DeferredRegister.create(NeoForgeRegistries.ATTACHMENT_TYPES, Ashbound.ID);
	public static final Supplier<AttachmentType<State>> STATE = ATTACHMENTS.register("errands",
			() -> AttachmentType.builder(() -> State.NEW).serialize(State.CODEC).copyOnDeath().build());

	/** Your favours as the server last told it (client side). */
	public static List<View> client = List.of();

	// ---------------------------------------------------------------- the list

	private record Template(String id, List<String> who, int from, int to, int type, String target, int nMin, int nMax, double mul, String title,
							String hook, String ask, String thanks, String toName, List<ItemStack> gift) {}

	private static List<Template> LIST = List.of();
	private static float CHANCE = 0.3f;
	private static int[][] PAY = {{30, 15}};
	private static List<List<String>> FOES = List.of(List.of("minecraft:zombie"));

	private static void load(Map<ResourceLocation, JsonElement> files) {
		JsonElement e = files.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "errands"));
		if (e == null) return;
		try {
			JsonObject j = e.getAsJsonObject();
			CHANCE = j.get("chance").getAsFloat();
			JsonArray pay = j.getAsJsonArray("pay");
			int[][] p = new int[pay.size()][2];
			for (int i = 0; i < p.length; i++) p[i] = new int[] {pay.get(i).getAsJsonArray().get(0).getAsInt(), pay.get(i).getAsJsonArray().get(1).getAsInt()};
			PAY = p;
			List<List<String>> foes = new ArrayList<>();
			for (JsonElement r : j.getAsJsonArray("foes")) {
				List<String> ids = new ArrayList<>();
				for (JsonElement id : r.getAsJsonArray()) if (BuiltInRegistries.ENTITY_TYPE.containsKey(ResourceLocation.parse(id.getAsString()))) ids.add(id.getAsString());
				foes.add(ids.isEmpty() ? List.of("minecraft:zombie") : ids);
			}
			FOES = foes;
			List<Template> out = new ArrayList<>();
			for (JsonElement el : j.getAsJsonArray("list")) {
				JsonObject o = el.getAsJsonObject();
				int type = o.has("kill") ? KILL : o.has("collect") ? COLLECT : DELIVER;
				String target = o.get(type == KILL ? "kill" : type == COLLECT ? "collect" : "deliver").getAsString();
				if (type == COLLECT && !BuiltInRegistries.ITEM.containsKey(ResourceLocation.parse(target))) {
					Ashbound.LOG.warn("The favour {} wants {}, which isn't in the game", o.get("id").getAsString(), target);
					continue;
				}
				List<String> who = new ArrayList<>();
				o.getAsJsonArray("who").forEach(t -> who.add(t.getAsString()));
				List<ItemStack> gift = new ArrayList<>();
				if (o.has("gift")) {
					for (JsonElement g : o.getAsJsonArray("gift")) {
						ResourceLocation id = ResourceLocation.parse(g.getAsJsonArray().get(0).getAsString());
						if (BuiltInRegistries.ITEM.containsKey(id)) gift.add(new ItemStack(BuiltInRegistries.ITEM.get(id), g.getAsJsonArray().get(1).getAsInt()));
					}
				}
				JsonArray n = o.getAsJsonArray("n");
				out.add(new Template(o.get("id").getAsString(), who, o.get("from").getAsInt(), o.get("to").getAsInt(), type, target, n.get(0).getAsInt(), n.get(1).getAsInt(),
						o.has("mul") ? o.get("mul").getAsDouble() : 1, o.get("title").getAsString(), o.get("hook").getAsString(), o.get("ask").getAsString(),
						o.get("thanks").getAsString(), o.has("to_name") ? o.get("to_name").getAsString() : "", List.copyOf(gift)));
			}
			LIST = out;
			Ashbound.LOG.info("{} kinds of favour the townsfolk can ask", out.size());
		} catch (Exception ex) {
			Ashbound.LOG.error("Couldn't read the favours", ex);
		}
	}

	private static Template template(String id) {
		for (Template t : LIST) if (t.id().equals(id)) return t;
		return null;
	}

	// ---------------------------------------------------------------- what's on offer

	private record Offer(Template t, String target, int count, int coins, int points) {
		String objective() {
			return switch (t.type()) {
				case KILL -> "Slay " + count + " " + name(target, count, true);
				case COLLECT -> "Bring " + count + " " + name(target, count, false);
				default -> "Take the letter to " + t.toName();
			};
		}

		String reward() {
			return Errands.reward(coins, points, t.gift());
		}
	}

	private static String name(String id, int n, boolean mob) {
		ResourceLocation r = ResourceLocation.parse(id);
		String s = (mob ? BuiltInRegistries.ENTITY_TYPE.get(r).getDescription() : new ItemStack(BuiltInRegistries.ITEM.get(r)).getHoverName()).getString();
		return n > 1 && !s.endsWith("s") ? s + "s" : s;
	}

	private static String reward(int coins, int points, List<ItemStack> gift) {
		StringBuilder b = new StringBuilder(coins + " coins");
		if (points > 0) b.append(", +").append(points).append(" GP");
		for (ItemStack s : gift) b.append(", ").append(s.getCount()).append(" ").append(s.getHoverName().getString());
		return b.toString();
	}

	private static long day(ServerPlayer p) {
		return p.level().getDayTime() / 24000L;
	}

	private static String key(ServerPlayer p, Npc npc) {
		return npc.getStringUUID() + ":" + day(p) / CYCLE;
	}

	/** What this person would ask you this cycle, if anything. */
	private static Offer offer(ServerPlayer p, Npc npc) {
		State s = p.getData(STATE);
		if (npc.is("lead") || s.errands().size() >= MAX || s.asked().contains(key(p, npc))) return null;
		for (Errand e : s.errands()) if (e.giver().equals(npc.getStringUUID())) return null;
		Random r = new Random(key(p, npc).hashCode() ^ p.getUUID().hashCode());
		if (r.nextFloat() >= CHANCE) return null;
		int rank = Math.min(Guild.of(p).rank(), PAY.length - 1);
		List<Template> can = new ArrayList<>();
		for (Template t : LIST) if (rank >= t.from() && rank <= t.to() && t.who().stream().anyMatch(npc::is)) can.add(t);
		if (can.isEmpty()) return null;
		Template t = can.get(r.nextInt(can.size()));
		String target = t.target();
		if (target.equals("@foes")) {
			List<String> pool = FOES.get(Math.min(rank, FOES.size() - 1));
			target = pool.get(r.nextInt(pool.size()));
		}
		int count = t.nMin() + r.nextInt(t.nMax() - t.nMin() + 1);
		boolean guild = Guild.of(p).registered();
		return new Offer(t, target, count, (int) Math.round(PAY[rank][0] * t.mul()), guild ? (int) Math.round(PAY[rank][1] * t.mul()) : 0);
	}

	private static void set(ServerPlayer p, List<Errand> errands, List<String> asked) {
		p.setData(STATE, new State(List.copyOf(errands), List.copyOf(asked)));
		sync(p);
	}

	/** Favours left over a week drop off your list; the reminders of who asked this cycle go with the cycle. */
	private static void sweep(ServerPlayer p) {
		State s = p.getData(STATE);
		long today = day(p);
		String cycle = ":" + today / CYCLE;
		List<Errand> keep = new ArrayList<>();
		for (Errand e : s.errands()) {
			if (today - e.day() <= EXPIRE) keep.add(e);
			else p.sendSystemMessage(Component.literal(e.giverName() + " has given up on you: ").withStyle(ChatFormatting.GRAY).append(Component.literal(e.title()).withStyle(ChatFormatting.GOLD)));
		}
		List<String> asked = s.asked().stream().filter(a -> a.endsWith(cycle)).toList();
		if (keep.size() != s.errands().size() || asked.size() != s.asked().size()) set(p, keep, asked);
	}

	private static int carried(ServerPlayer p, String id) {
		int n = 0;
		for (int i = 0; i < p.getInventory().getContainerSize(); i++) {
			ItemStack s = p.getInventory().getItem(i);
			if (!s.isEmpty() && BuiltInRegistries.ITEM.getKey(s.getItem()).toString().equals(id)) n += s.getCount();
		}
		return n;
	}

	private static boolean ready(ServerPlayer p, Errand e) {
		return switch (e.type()) {
			case KILL -> e.progress() >= e.count();
			case COLLECT -> carried(p, e.target()) >= e.count();
			default -> false;
		};
	}

	static void sync(ServerPlayer p) {
		List<View> views = new ArrayList<>();
		for (Errand e : p.getData(STATE).errands()) {
			String left = e.type() == KILL ? "  " + Math.min(e.progress(), e.count()) + "/" + e.count() : "";
			String where = e.type() == DELIVER ? "From " + e.giverName() : "Back to " + e.giverName() + ", near " + e.x() + ", " + e.z();
			views.add(new View(e.title(), e.objective() + left, where, ready(p, e)));
		}
		PacketDistributor.sendToPlayer(p, new Net.ErrandSync(views));
	}

	// ---------------------------------------------------------------- in the conversation (Talk)

	/** A line and its choices, said by whoever you're talking to. */
	record Reply(String text, List<Talk.Option> options) {}

	private static final List<Talk.Option> BYE = List.of(new Talk.Option("Something else.", "", "start", ""), new Talk.Option("Goodbye.", "", "", "close"));

	/** A line they'd open with if they've something to ask; "" if not. */
	static String hook(ServerPlayer p, Npc npc) {
		sweep(p);
		Offer o = offer(p, npc);
		return o == null ? "" : o.t().hook();
	}

	/** The choices to put at the top of the first thing they say. */
	static List<Talk.Option> options(ServerPlayer p, Npc npc) {
		List<Talk.Option> out = new ArrayList<>();
		for (Errand e : p.getData(STATE).errands()) {
			if (e.type() == DELIVER) {
				if (!e.giver().equals(npc.getStringUUID()) && npc.is(e.target())) out.add(new Talk.Option("I've a letter for you.", "", "", "errand:letter"));
			} else if (e.giver().equals(npc.getStringUUID())) {
				out.add(ready(p, e) ? new Talk.Option("It's done. (" + e.title() + ")", "", "", "errand:turn_in")
						: new Talk.Option("About that favour...", "", "", "errand:ask_drop"));
			}
		}
		if (offer(p, npc) != null) out.add(new Talk.Option("Do you need something?", "", "", "errand:hear"));
		return out;
	}

	/** A choice from options(). Null: they've nothing to say to that (it's gone stale), the conversation ends. */
	static Reply pick(ServerPlayer p, Npc npc, String act) {
		State s = p.getData(STATE);
		switch (act) {
			case "errand:hear" -> {
				Offer o = offer(p, npc);
				if (o == null) return null;
				String ask = o.t().ask().replace("{n}", String.valueOf(o.count())).replace("{target}", o.t().type() == DELIVER ? "" : name(o.target(), o.count(), o.t().type() == KILL));
				return new Reply(ask + "\n\n" + o.objective() + "\nReward: " + o.reward(), List.of(new Talk.Option("I'll do it.", "", "", "errand:take"), new Talk.Option("Not today.", "", "", "errand:no")));
			}
			case "errand:take" -> {
				Offer o = offer(p, npc);
				if (o == null) return null;
				List<Errand> list = new ArrayList<>(s.errands());
				String target = o.target();
				list.add(new Errand(o.t().id(), o.t().type(), target, o.count(), 0, o.coins(), o.points(), npc.getStringUUID(), npc.kind().name(),
						npc.getBlockX(), npc.getBlockZ(), day(p), o.t().title(), o.objective()));
				List<String> asked = new ArrayList<>(s.asked());
				asked.add(key(p, npc));
				set(p, list, asked);
				p.level().playSound(null, p.blockPosition(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 1f, 1.2f);
				p.sendSystemMessage(Component.literal("Favour: ").withStyle(ChatFormatting.GRAY).append(Component.literal(o.t().title()).withStyle(ChatFormatting.GOLD))
						.append(Component.literal(" - " + o.objective()).withStyle(ChatFormatting.GRAY)));
				return new Reply("Thank you. Truly.", BYE);
			}
			case "errand:no" -> {
				List<String> asked = new ArrayList<>(s.asked());
				asked.add(key(p, npc));
				set(p, s.errands(), asked);
				return new Reply("No, of course. Forget I asked.", BYE);
			}
			case "errand:ask_drop" -> {
				return new Reply("Yes? How's it coming along?", List.of(new Talk.Option("Still working on it.", "", "start", ""), new Talk.Option("I can't do it. I'm sorry.", "", "", "errand:drop")));
			}
			case "errand:drop" -> {
				List<Errand> list = new ArrayList<>(s.errands());
				list.removeIf(e -> e.type() != DELIVER && e.giver().equals(npc.getStringUUID()));
				List<String> asked = new ArrayList<>(s.asked());
				asked.add(key(p, npc));
				set(p, list, asked);
				return new Reply("Ah. Well. Thank you for trying.", BYE);
			}
			case "errand:turn_in" -> {
				for (Errand e : s.errands()) {
					if (e.type() == DELIVER || !e.giver().equals(npc.getStringUUID()) || !ready(p, e)) continue;
					if (e.type() == COLLECT) take(p, e.target(), e.count());
					return pay(p, e);
				}
				return null;
			}
			case "errand:letter" -> {
				for (Errand e : s.errands()) if (e.type() == DELIVER && !e.giver().equals(npc.getStringUUID()) && npc.is(e.target())) return pay(p, e);
				return null;
			}
			default -> {
				return null;
			}
		}
	}

	private static void take(ServerPlayer p, String id, int count) {
		int left = count;
		for (int i = 0; i < p.getInventory().getContainerSize() && left > 0; i++) {
			ItemStack s = p.getInventory().getItem(i);
			if (!s.isEmpty() && BuiltInRegistries.ITEM.getKey(s.getItem()).toString().equals(id)) {
				int n = Math.min(left, s.getCount());
				s.shrink(n);
				left -= n;
			}
		}
	}

	private static Reply pay(ServerPlayer p, Errand e) {
		State s = p.getData(STATE);
		List<Errand> list = new ArrayList<>(s.errands());
		list.remove(e);
		set(p, list, s.asked());
		Template t = template(e.template());
		List<ItemStack> gift = t == null ? List.of() : t.gift();
		Coins.give(p, e.coins());
		if (e.points() > 0) Guild.points(p, e.points());
		for (ItemStack i : gift) p.getInventory().placeItemBackInInventory(i.copy());
		p.level().playSound(null, p.blockPosition(), SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 0.7f, 1.3f);
		p.sendSystemMessage(Component.literal("Favour done: ").withStyle(ChatFormatting.GRAY).append(Component.literal(e.title()).withStyle(ChatFormatting.GOLD))
				.append(Component.literal("  " + reward(e.coins(), e.points(), gift)).withStyle(ChatFormatting.YELLOW)));
		return new Reply(t == null ? "Thank you." : t.thanks(), BYE);
	}

	// ---------------------------------------------------------------- out in the world

	private static void killed(LivingDeathEvent ev) {
		if (!(ev.getSource().getEntity() instanceof ServerPlayer p) || ev.getEntity() instanceof Player) return;
		State s = p.getData(STATE);
		if (s.errands().isEmpty()) return;
		String id = BuiltInRegistries.ENTITY_TYPE.getKey(ev.getEntity().getType()).toString();
		List<Errand> list = new ArrayList<>();
		boolean changed = false;
		for (Errand e : s.errands()) {
			if (e.type() == KILL && e.target().equals(id) && e.progress() < e.count()) {
				e = e.advanced();
				changed = true;
				if (e.progress() >= e.count())
					p.sendSystemMessage(Component.literal(e.title()).withStyle(ChatFormatting.GOLD).append(Component.literal(" - done! Go back to " + e.giverName() + ".").withStyle(ChatFormatting.GREEN)));
				else p.displayClientMessage(Component.literal(e.title() + "  " + e.progress() + " / " + e.count()).withStyle(ChatFormatting.GOLD), true);
			}
			list.add(e);
		}
		if (changed) set(p, list, s.asked());
	}

	static void init(IEventBus bus) {
		ATTACHMENTS.register(bus);
		NeoForge.EVENT_BUS.addListener(Errands::killed);
		NeoForge.EVENT_BUS.addListener((AddReloadListenerEvent e) -> e.addListener(new SimpleJsonResourceReloadListener(new Gson(), "errand") {
			@Override
			protected void apply(Map<ResourceLocation, JsonElement> files, ResourceManager rm, ProfilerFiller pf) {
				load(files);
			}
		}));
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedInEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer sp) {
				sweep(sp);
				sync(sp);
			}
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.Clone e) -> {
			if (e.getEntity() instanceof ServerPlayer sp) sync(sp);
		});
	}
}
