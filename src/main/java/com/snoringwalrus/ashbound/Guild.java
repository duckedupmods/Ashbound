package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;

import io.netty.buffer.ByteBuf;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.core.HolderSet;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitlesAnimationPacket;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimpleJsonResourceReloadListener;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.level.Level;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.AddReloadListenerEvent;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

/**
 * The Adventurers' Guild: your guild card (registered or not, your rank F to SSS, your Guild Points, the requests
 * you've taken and how far along they are) attached to you, saved and sent to your client; the requests on the board
 * (data/ashbound/quest/*.json); taking, abandoning and reporting them at the receptionist; ranking up there once you
 * have the points (an evaluation, not automatic).
 *
 * A request: {"title", "rank": "F", "text", "kill": "minecraft:zombie" | "#minecraft:skeletons" or "collect":
 * "minecraft:bone" | "#minecraft:wool", "count", "points", "coins", "ash", "items": [["id", n]], "repeat": true}.
 * You may take requests of your rank or one above it, three at a time.
 */
public final class Guild {
	private Guild() {}

	public static final String[] RANKS = {"F", "E", "D", "C", "B", "A", "S", "SS", "SSS"};
	/** Guild Points needed for each rank's evaluation. */
	public static final int[] NEED = {0, 100, 300, 700, 1500, 3000, 6000, 12000, 25000};
	public static final int MAX_ACTIVE = 3;
	public static final int ACCEPT = 0, ABANDON = 1, REPORT = 2;
	public static final int AVAILABLE = 0, ACTIVE = 1, READY = 2, LOCKED = 3;
	/** How far off a kill still counts for you; how many chunks out a request's structure is looked for. */
	private static final int SHARED = 32, LOCATE = 100;

	// ---------------------------------------------------------------- the guild card

	/** @param at whether x, z say where it is (a tower or the like, looked up when you took it) */
	public record Active(String id, int progress, int x, int z, boolean at) {
		static final Codec<Active> CODEC = RecordCodecBuilder.create(i -> i.group(
				Codec.STRING.fieldOf("id").forGetter(Active::id),
				Codec.INT.optionalFieldOf("progress", 0).forGetter(Active::progress),
				Codec.INT.optionalFieldOf("x", 0).forGetter(Active::x),
				Codec.INT.optionalFieldOf("z", 0).forGetter(Active::z),
				Codec.BOOL.optionalFieldOf("at", false).forGetter(Active::at)
		).apply(i, Active::new));
		static final StreamCodec<ByteBuf, Active> STREAM = StreamCodec.composite(
				ByteBufCodecs.STRING_UTF8, Active::id, ByteBufCodecs.VAR_INT, Active::progress, ByteBufCodecs.VAR_INT, Active::x, ByteBufCodecs.VAR_INT, Active::z,
				ByteBufCodecs.BOOL, Active::at, Active::new);

		Active progressed() {
			return new Active(id, progress + 1, x, z, at);
		}
	}

	public record Card(boolean registered, int rank, int points, List<Active> active, List<String> done) {
		public static final Card NEW = new Card(false, 0, 0, List.of(), List.of());
		static final Codec<Card> CODEC = RecordCodecBuilder.create(i -> i.group(
				Codec.BOOL.optionalFieldOf("registered", false).forGetter(Card::registered),
				Codec.INT.optionalFieldOf("rank", 0).forGetter(Card::rank),
				Codec.INT.optionalFieldOf("points", 0).forGetter(Card::points),
				Active.CODEC.listOf().optionalFieldOf("active", List.of()).forGetter(Card::active),
				Codec.STRING.listOf().optionalFieldOf("done", List.of()).forGetter(Card::done)
		).apply(i, Card::new));
		public static final StreamCodec<ByteBuf, Card> STREAM = StreamCodec.composite(
				ByteBufCodecs.BOOL, Card::registered, ByteBufCodecs.VAR_INT, Card::rank, ByteBufCodecs.VAR_INT, Card::points,
				Active.STREAM.apply(ByteBufCodecs.list()), Card::active, ByteBufCodecs.STRING_UTF8.apply(ByteBufCodecs.list()), Card::done,
				Card::new);

		/** Points for the next evaluation, or -1 at SSS. */
		public int next() {
			return rank + 1 < RANKS.length ? NEED[rank + 1] : -1;
		}

		public boolean canRankUp() {
			return registered && next() >= 0 && points >= next();
		}

		public String rankName() {
			return RANKS[Math.max(0, Math.min(RANKS.length - 1, rank))];
		}

		public Active active(String id) {
			for (Active a : active) if (a.id().equals(id)) return a;
			return null;
		}
	}

	static final DeferredRegister<AttachmentType<?>> ATTACHMENTS = DeferredRegister.create(NeoForgeRegistries.ATTACHMENT_TYPES, Ashbound.ID);
	public static final Supplier<AttachmentType<Card>> CARD = ATTACHMENTS.register("guild_card",
			() -> AttachmentType.builder(() -> Card.NEW).serialize(Card.CODEC).copyOnDeath().build());

	/** The card as the server last told it (client side). */
	public static Card client = Card.NEW;

	/** The card you carry: use it to hold it up (client/GuildCardScreen). */
	public static final DeferredItem<Item> CARD_ITEM = Weapons.ITEMS.registerItem("guild_card", p -> new Item(p.stacksTo(1).rarity(Rarity.UNCOMMON)) {
		@Override
		public InteractionResultHolder<ItemStack> use(Level level, Player who, InteractionHand hand) {
			if (level.isClientSide) Net.onCard.run();
			return InteractionResultHolder.sidedSuccess(who.getItemInHand(hand), level.isClientSide);
		}
	});

	public static Card of(Player p) {
		return p.level().isClientSide() ? client : p.getData(CARD);
	}

	private static void set(ServerPlayer p, Card c) {
		p.setData(CARD, c);
		sync(p);
	}

	static void sync(ServerPlayer p) {
		PacketDistributor.sendToPlayer(p, new Net.GuildSync(p.getData(CARD)));
	}

	// ---------------------------------------------------------------- the requests

	/**
	 * @param target an entity or item (or # tag), "gate:R" for closing gates of that rank, "incident:id" for one of Incidents
	 * @param locate the structure a request sends you to, found when you take it  @param dim which world that's in; null, this one
	 */
	public record Quest(String id, String title, int rank, String text, boolean kill, String target, int count,
						int points, int coins, int ash, List<ItemStack> items, boolean repeat, String what, String icon, String locate, String dim) {
		/** "Slay 8 Zombies" / "Bring 12 Bones" / "Close 3 Rank E Gates". */
		public String objective() {
			if (incident()) return what;
			return (gate() ? "Close " : kill ? "Slay " : "Bring ") + count + " " + targetName();
		}

		boolean gate() {
			return target.startsWith("gate:");
		}

		boolean incident() {
			return target.startsWith("incident:");
		}

		public String targetName() {
			if (what != null) return what;
			if (target.startsWith("#")) {
				String n = ResourceLocation.parse(target.substring(1)).getPath().replace('_', ' ');
				return Character.toUpperCase(n.charAt(0)) + n.substring(1);
			}
			ResourceLocation id = ResourceLocation.parse(target);
			Component c = kill ? BuiltInRegistries.ENTITY_TYPE.get(id).getDescription() : new ItemStack(BuiltInRegistries.ITEM.get(id)).getHoverName();
			String s = c.getString();
			return count > 1 && !s.endsWith("s") ? s + "s" : s;
		}

		public String reward() {
			StringBuilder b = new StringBuilder();
			if (coins > 0) b.append(coins).append(" coins, ");
			b.append("+").append(points).append(" GP");
			if (ash > 0) b.append(", ").append(ash).append(" Ash");
			for (ItemStack s : items) b.append(", ").append(s.getCount()).append(" ").append(s.getHoverName().getString());
			return b.toString();
		}

		boolean matches(Entity e) {
			if (!kill) return false;
			if (target.startsWith("#")) return e.getType().is(TagKey.create(Registries.ENTITY_TYPE, ResourceLocation.parse(target.substring(1))));
			return !gate() && !incident() && BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).toString().equals(target);
		}

		boolean matches(ItemStack s) {
			if (kill || s.isEmpty()) return false;
			if (target.startsWith("#")) return s.is(TagKey.create(Registries.ITEM, ResourceLocation.parse(target.substring(1))));
			return BuiltInRegistries.ITEM.getKey(s.getItem()).toString().equals(target);
		}
	}

	private static Map<String, Quest> QUESTS = Map.of();

	private static void load(Map<ResourceLocation, JsonElement> files) {
		List<Quest> all = new ArrayList<>();
		for (var e : files.entrySet()) {
			if (!e.getKey().getNamespace().equals(Ashbound.ID)) continue;
			try {
				JsonObject j = e.getValue().getAsJsonObject();
				boolean gate = j.has("gate"), kill = gate || j.has("kill");
				String target = gate ? "gate:" + j.get("gate").getAsString() : j.get(kill ? "kill" : "collect").getAsString();
				if (!gate && !target.startsWith("#") && !(kill ? BuiltInRegistries.ENTITY_TYPE : BuiltInRegistries.ITEM).containsKey(ResourceLocation.parse(target))) {
					Ashbound.LOG.warn("The request {} wants {}, which isn't in the game", e.getKey(), target);
					continue;
				}
				List<ItemStack> items = new ArrayList<>();
				if (j.has("items")) {
					for (JsonElement el : j.getAsJsonArray("items")) {
						JsonArray a = el.getAsJsonArray();
						ResourceLocation id = ResourceLocation.parse(a.get(0).getAsString());
						if (BuiltInRegistries.ITEM.containsKey(id)) items.add(new ItemStack(BuiltInRegistries.ITEM.get(id), a.size() > 1 ? a.get(1).getAsInt() : 1));
					}
				}
				all.add(new Quest(e.getKey().getPath(), j.get("title").getAsString(), rankOf(j.get("rank").getAsString()), j.get("text").getAsString(), kill, target,
						j.has("count") ? j.get("count").getAsInt() : 1, j.has("points") ? j.get("points").getAsInt() : 10,
						j.has("coins") ? j.get("coins").getAsInt() : 0, j.has("ash") ? j.get("ash").getAsInt() : 0, List.copyOf(items),
						!j.has("repeat") || j.get("repeat").getAsBoolean(), j.has("what") ? j.get("what").getAsString() : null, j.has("icon") ? j.get("icon").getAsString() : null,
						j.has("locate") ? j.get("locate").getAsString() : null, j.has("dim") ? j.get("dim").getAsString() : null));
			} catch (Exception ex) {
				Ashbound.LOG.error("Couldn't read the request {}", e.getKey(), ex);
			}
		}
		all.sort(Comparator.comparingInt(Quest::rank).thenComparing(Quest::title));
		Map<String, Quest> out = new LinkedHashMap<>();
		for (Quest q : all) out.put(q.id(), q);
		QUESTS = out;
		Ashbound.LOG.info("The guild's board holds {} requests", out.size());
	}

	/** A request by id, from the board or what's going on out there. */
	static Quest quest(String id) {
		Quest q = QUESTS.get(id);
		return q != null ? q : Incidents.quest(id);
	}

	public static int rankOf(String name) {
		for (int i = 0; i < RANKS.length; i++) if (RANKS[i].equalsIgnoreCase(name)) return i;
		return 0;
	}

	// ---------------------------------------------------------------- at the counter

	/** Writes you into the guild: an F-rank card, and the card itself to carry. */
	public static void register(ServerPlayer p) {
		Card c = of(p);
		if (c.registered()) return;
		set(p, new Card(true, 0, c.points(), c.active(), c.done()));
		p.getInventory().placeItemBackInInventory(new ItemStack(CARD_ITEM.get()));
		BeltPouch.tuck(p);
		p.level().playSound(null, p.blockPosition(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 1f, 1f);
		title(p, Component.literal("F").withStyle(ChatFormatting.GRAY, ChatFormatting.BOLD), Component.literal("Registered with the Adventurers' Guild"));
	}

	/** The evaluation: up one rank if you have the points. */
	public static boolean rankUp(ServerPlayer p) {
		Card c = of(p);
		if (!c.canRankUp()) return false;
		Card n = new Card(true, c.rank() + 1, c.points(), c.active(), c.done());
		set(p, n);
		p.level().playSound(null, p.blockPosition(), SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.PLAYERS, 1f, 1f);
		title(p, Component.literal(n.rankName() + " Rank").withStyle(rankStyle(n.rank()), ChatFormatting.BOLD), Component.literal("Your guild card has been updated"));
		Story.mark(p, "story/rank_" + n.rankName().toLowerCase(java.util.Locale.ROOT));
		return true;
	}

	/** Guild Points for something done outside the board (a favour, Errands); nothing if you're not on the register. */
	static void points(ServerPlayer p, int n) {
		Card c = of(p);
		if (c.registered()) set(p, new Card(true, c.rank(), c.points() + n, c.active(), c.done()));
	}

	/** Anything of yours ready to be reported. */
	static boolean anyReady(ServerPlayer p) {
		Card c = of(p);
		for (Active a : c.active()) {
			Quest q = quest(a.id());
			if (q != null && progress(p, q, a) >= q.count()) return true;
		}
		return false;
	}

	private static void title(ServerPlayer p, Component big, Component small) {
		p.connection.send(new ClientboundSetTitlesAnimationPacket(10, 50, 20));
		p.connection.send(new ClientboundSetSubtitleTextPacket(small));
		p.connection.send(new ClientboundSetTitleTextPacket(big));
	}

	private static ChatFormatting rankStyle(int rank) {
		return switch (rank) {
			case 0 -> ChatFormatting.GRAY;
			case 1 -> ChatFormatting.GREEN;
			case 2 -> ChatFormatting.DARK_AQUA;
			case 3 -> ChatFormatting.BLUE;
			case 4 -> ChatFormatting.LIGHT_PURPLE;
			case 5 -> ChatFormatting.GOLD;
			case 6 -> ChatFormatting.RED;
			case 7 -> ChatFormatting.DARK_RED;
			default -> ChatFormatting.YELLOW;
		};
	}

	/** How many of what a collect request wants you're carrying. */
	private static int carried(ServerPlayer p, Quest q) {
		int n = 0;
		for (int i = 0; i < p.getInventory().getContainerSize(); i++) {
			ItemStack s = p.getInventory().getItem(i);
			if (q.matches(s)) n += s.getCount();
		}
		return n;
	}

	private static int progress(ServerPlayer p, Quest q, Active a) {
		if (q.incident()) return Incidents.over(q.id()) ? 1 : 0;
		return q.kill() ? a.progress() : Math.min(q.count(), carried(p, q));
	}

	// ---------------------------------------------------------------- the board

	/** The item a request is drawn with on the board: what it wants brought, or the egg of what it wants slain. */
	private static String icon(Quest q) {
		if (q.icon() != null) return q.icon();
		if (!q.kill()) {
			if (!q.target().startsWith("#")) return q.target();
			for (var h : BuiltInRegistries.ITEM.getTagOrEmpty(TagKey.create(Registries.ITEM, ResourceLocation.parse(q.target().substring(1)))))
				return BuiltInRegistries.ITEM.getKey(h.value()).toString();
			return "minecraft:paper";
		}
		if (!q.target().startsWith("#")) {
			ResourceLocation egg = ResourceLocation.parse(q.target() + "_spawn_egg");
			if (BuiltInRegistries.ITEM.containsKey(egg)) return egg.toString();
		}
		return "minecraft:iron_sword";
	}

	/** Shows you the board (opens it, or refreshes it if it's open). */
	public static void board(ServerPlayer p, Npc npc) {
		Story.mark(p, "story/board");
		Card c = of(p);
		List<Net.QuestView> views = new ArrayList<>();
		List<Quest> posted = new ArrayList<>();
		for (Incidents.Incident i : Incidents.live()) posted.add(Incidents.quest(i));
		posted.addAll(QUESTS.values());
		for (Quest q : posted) {
			Active a = c.active(q.id());
			if (a == null && q.incident() && Incidents.over(q.id())) continue;
			int state;
			int prog = 0;
			if (a != null) {
				prog = progress(p, q, a);
				state = prog >= q.count() ? READY : ACTIVE;
			} else if (q.rank() > c.rank() + 1) {
				state = LOCKED;
			} else if (!q.repeat() && c.done().contains(q.id())) {
				continue;
			} else {
				state = AVAILABLE;
			}
			List<String> gifts = new ArrayList<>();
			for (ItemStack s : q.items()) gifts.add(BuiltInRegistries.ITEM.getKey(s.getItem()) + "*" + s.getCount());
			views.add(new Net.QuestView(q.id(), q.title(), q.rank(), q.text(), q.objective(), prog, q.count(), q.reward(), state,
					q.coins(), q.points(), icon(q), gifts));
		}
		PacketDistributor.sendToPlayer(p, new Net.QuestBoard(npc.getId(), views));
	}

	static void onAct(Net.QuestAct msg, ServerPlayer p) {
		if (!(p.level().getEntity(msg.entity()) instanceof Npc npc) || npc.distanceTo(p) > 8) return;
		Card c = of(p);
		Quest q = quest(msg.quest());
		if (q == null || !c.registered()) return;
		List<Active> active = new ArrayList<>(c.active());
		Active a = c.active(q.id());
		switch (msg.action()) {
			case ACCEPT -> {
				if (a != null || q.rank() > c.rank() + 1 || active.size() >= MAX_ACTIVE || (!q.repeat() && c.done().contains(q.id()))) return;
				int[] at = locate(p, q);
				active.add(new Active(q.id(), 0, at == null ? 0 : at[0], at == null ? 0 : at[1], at != null));
				set(p, new Card(true, c.rank(), c.points(), List.copyOf(active), c.done()));
				Story.pick(p, "req:" + q.id());
				for (ServerPlayer o : Party.others(p)) {
					if (take(o, q, at)) o.sendSystemMessage(Component.literal(p.getScoreboardName() + " took a request for the party: ").withStyle(ChatFormatting.GRAY)
							.append(Component.literal(q.title()).withStyle(ChatFormatting.GOLD)).append(Component.literal(" - " + q.objective()).withStyle(ChatFormatting.GRAY)));
					else p.sendSystemMessage(Component.literal(o.getScoreboardName() + " can't take this one: their card's rank, or three requests already").withStyle(ChatFormatting.GRAY));
				}
				p.level().playSound(null, p.blockPosition(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 1f, 1.2f);
				p.sendSystemMessage(Component.literal("Request taken: ").withStyle(ChatFormatting.GRAY)
						.append(Component.literal(q.title()).withStyle(ChatFormatting.GOLD)).append(Component.literal(" - " + q.objective()).withStyle(ChatFormatting.GRAY)));
			}
			case ABANDON -> {
				if (a == null) return;
				active.remove(a);
				set(p, new Card(true, c.rank(), c.points(), List.copyOf(active), c.done()));
			}
			case REPORT -> {
				if (a == null || progress(p, q, a) < q.count()) return;
				if (!q.kill()) {
					int left = q.count();
					for (int i = 0; i < p.getInventory().getContainerSize() && left > 0; i++) {
						ItemStack s = p.getInventory().getItem(i);
						if (q.matches(s)) {
							int take = Math.min(left, s.getCount());
							s.shrink(take);
							left -= take;
						}
					}
				}
				Card n = pay(p, q, a);
				Party.share(p, Party.REQUEST + q.id());
				if (n.canRankUp() && !c.canRankUp() && npc.kind() != null)
					p.sendSystemMessage(Component.literal(npc.kind().name() + ": ").withStyle(ChatFormatting.GOLD)
							.append(Component.literal("Oh! You have enough points for a rank evaluation. Talk to me when you're ready!").withStyle(ChatFormatting.WHITE)));
			}
			default -> {
				return;
			}
		}
		board(p, npc);
		Story.state(p);
	}

	/** A request off your active list and its pay in your hands. */
	private static Card pay(ServerPlayer p, Quest q, Active a) {
		Card c = of(p);
		List<Active> active = new ArrayList<>(c.active());
		active.remove(a);
		List<String> done = new ArrayList<>(c.done());
		if (!done.contains(q.id())) done.add(q.id());
		Card n = new Card(true, c.rank(), c.points() + q.points(), List.copyOf(active), List.copyOf(done));
		set(p, n);
		if (q.coins() > 0) Coins.give(p, q.coins());
		if (q.ash() > 0) Levels.give(p, q.ash());
		for (ItemStack s : q.items()) p.getInventory().placeItemBackInInventory(s.copy());
		p.level().playSound(null, p.blockPosition(), SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 0.7f, 1.3f);
		p.sendSystemMessage(Component.literal("Request complete: ").withStyle(ChatFormatting.GRAY)
				.append(Component.literal(q.title()).withStyle(ChatFormatting.GOLD))
				.append(Component.literal("  " + q.reward()).withStyle(ChatFormatting.YELLOW)));
		return n;
	}

	/** Your party took this request: on your card too, if it can be. */
	private static boolean take(ServerPlayer p, Quest q, int[] at) {
		Card c = of(p);
		if (c.active(q.id()) != null) return true;
		if (!c.registered() || q.rank() > c.rank() + 1 || c.active().size() >= MAX_ACTIVE || (!q.repeat() && c.done().contains(q.id()))) return false;
		List<Active> active = new ArrayList<>(c.active());
		active.add(new Active(q.id(), 0, at == null ? 0 : at[0], at == null ? 0 : at[1], at != null));
		set(p, new Card(true, c.rank(), c.points(), List.copyOf(active), c.done()));
		Story.pick(p, "req:" + q.id());
		return true;
	}

	/** Someone in your party reported this request: yours is done with it, and paid. */
	static void settle(ServerPlayer p, String id) {
		Quest q = quest(id);
		Card c = of(p);
		Active a = c.active(id);
		if (q == null || a == null) return;
		Card n = pay(p, q, a);
		if (n.canRankUp() && !c.canRankUp()) p.sendSystemMessage(Component.literal("You have enough points for a rank evaluation. Talk to Elowen.").withStyle(ChatFormatting.GOLD));
		Story.state(p);
	}

	/** Where a request's structure stands, the nearest to you in its world; null if it hasn't one, or none's to be found. */
	private static int[] locate(ServerPlayer p, Quest q) {
		if (q.locate() == null) return null;
		ServerLevel level = q.dim() == null ? p.serverLevel() : p.server.getLevel(ResourceKey.create(Registries.DIMENSION, ResourceLocation.parse(q.dim())));
		var holder = level == null ? null : level.registryAccess().registryOrThrow(Registries.STRUCTURE).getHolder(ResourceKey.create(Registries.STRUCTURE, ResourceLocation.parse(q.locate()))).orElse(null);
		if (holder == null) return null;
		var found = level.getChunkSource().getGenerator().findNearestMapStructure(level, HolderSet.direct(holder), p.blockPosition(), LOCATE, false);
		return found == null ? null : new int[] {found.getFirst().getX(), found.getFirst().getZ()};
	}

	/** The ids of the requests on your card: those the Journal can give up. */
	static List<String> taken(ServerPlayer p) {
		return of(p).active().stream().map(Active::id).toList();
	}

	/** Given up from the Journal: off your card, as at the desk. */
	static void abandon(ServerPlayer p, String id) {
		Card c = of(p);
		Active a = c.active(id);
		if (a == null) return;
		List<Active> active = new ArrayList<>(c.active());
		active.remove(a);
		set(p, new Card(true, c.rank(), c.points(), List.copyOf(active), c.done()));
		Quest q = quest(id);
		p.sendSystemMessage(Component.literal("Request given up: ").withStyle(ChatFormatting.GRAY).append(Component.literal(q == null ? id : q.title()).withStyle(ChatFormatting.GOLD)));
	}

	/** Your requests, then what's out there you haven't taken: for the Journal and the compass. */
	static List<Net.GuildJob> jobs(ServerPlayer p) {
		Card c = of(p);
		List<Net.GuildJob> out = new ArrayList<>();
		for (Active a : c.active()) {
			Quest q = quest(a.id());
			if (q != null) out.add(job(p, q, a));
		}
		for (Incidents.Incident i : Incidents.live()) if (!i.over && c.active(i.id) == null) out.add(job(p, Incidents.quest(i), null));
		return out;
	}

	private static Net.GuildJob job(ServerPlayer p, Quest q, Active a) {
		int prog = a == null ? 0 : progress(p, q, a);
		boolean ready = a != null && prog >= q.count();
		int[] at = ready ? Story.desk() : q.incident() ? Incidents.where(q.id()) : q.gate() ? Story.where(p, "gate:" + q.target().charAt(5)) : a != null && a.at() ? new int[] {a.x(), a.z()} : null;
		boolean here = ready || q.dim() == null || p.level().dimension().location().toString().equals(q.dim());
		if (!ready && q.dim() == null && (q.incident() || q.locate() != null) && p.level().dimension() != Level.OVERWORLD) here = false;
		String title = q.title() + (here ? "" : q.dim() == null ? "" : q.dim().endsWith("nether") ? " (in the Nether)" : " (in the End)");
		if (ready) title += " (report it)";
		else if (q.gate() && at == null) title += " (no gate near)";
		StringBuilder text = new StringBuilder(ready ? "Done. Report to Elowen at the Guild." : q.text() + "\n\n" + q.objective());
		if (!ready && q.count() > 1) text.append("  ").append(prog).append(" / ").append(q.count());
		if (!ready && a == null) text.append("\n\nNot taken yet: Elowen has it on the board.");
		if (at != null && !q.incident()) text.append("\n\nAt ").append(at[0]).append(", ").append(at[1]).append(".");
		text.append("\n\nPays ").append(q.reward()).append(".");
		return new Net.GuildJob(q.id(), title, text.toString(), at == null ? 0 : at[0], at == null ? 0 : at[1], at != null && here);
	}

	/** A gate of this rank closed counts toward any request to close them, for those in it and their parties. */
	static void gateClosed(List<ServerPlayer> there, char rank) {
		for (ServerPlayer p : Party.with(there)) credit(p, q -> q.gate() && q.target().charAt(5) == rank);
	}

	/** A kill counts toward any request to slay its kind, for everyone there when it fell and their parties. */
	private static void killed(LivingDeathEvent e) {
		if (!(e.getSource().getEntity() instanceof ServerPlayer killer) || e.getEntity() instanceof Player) return;
		List<ServerPlayer> there = new ArrayList<>(killer.serverLevel().getEntitiesOfClass(ServerPlayer.class, e.getEntity().getBoundingBox().inflate(SHARED), o -> !o.isSpectator() && o != killer));
		there.add(killer);
		for (ServerPlayer p : Party.with(there)) credit(p, q -> q.matches(e.getEntity()));
	}

	private static void credit(ServerPlayer p, java.util.function.Predicate<Quest> counts) {
		Card c = of(p);
		if (c.active().isEmpty()) return;
		List<Active> active = new ArrayList<>();
		boolean changed = false;
		for (Active a : c.active()) {
			Quest q = quest(a.id());
			if (q != null && counts.test(q) && a.progress() < q.count()) {
				a = a.progressed();
				changed = true;
				if (a.progress() >= q.count())
					p.sendSystemMessage(Component.literal(q.title()).withStyle(ChatFormatting.GOLD).append(Component.literal(" - done! Report back to the Guild.").withStyle(ChatFormatting.GREEN)));
				else p.displayClientMessage(Component.literal(q.title() + "  " + a.progress() + " / " + q.count()).withStyle(ChatFormatting.GOLD), true);
			}
			active.add(a);
		}
		if (changed) set(p, new Card(c.registered(), c.rank(), c.points(), List.copyOf(active), c.done()));
	}

	static void init(IEventBus bus) {
		ATTACHMENTS.register(bus);
		NeoForge.EVENT_BUS.addListener(Guild::killed);
		NeoForge.EVENT_BUS.addListener((AddReloadListenerEvent e) -> e.addListener(new SimpleJsonResourceReloadListener(new Gson(), "quest") {
			@Override
			protected void apply(Map<ResourceLocation, JsonElement> files, ResourceManager rm, ProfilerFiller pf) {
				load(files);
			}
		}));
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedInEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer sp) sync(sp);
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.Clone e) -> {
			if (e.getEntity() instanceof ServerPlayer sp) sync(sp);
		});
		// /ashbound gp 500: Guild Points to test an evaluation with
		NeoForge.EVENT_BUS.addListener((RegisterCommandsEvent e) -> e.getDispatcher().register(Commands.literal("ashbound").requires(s -> s.hasPermission(2))
				.then(Commands.literal("gp").then(Commands.argument("n", IntegerArgumentType.integer()).executes(s -> {
					ServerPlayer p = s.getSource().getPlayerOrException();
					Card c = of(p);
					set(p, new Card(c.registered(), c.rank(), Math.max(0, c.points() + IntegerArgumentType.getInteger(s, "n")), c.active(), c.done()));
					return 1;
				})))));
	}
}
