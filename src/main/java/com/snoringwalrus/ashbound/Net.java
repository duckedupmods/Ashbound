package com.snoringwalrus.ashbound;

import java.util.List;
import java.util.function.Consumer;
import java.util.function.IntConsumer;

import io.netty.buffer.ByteBuf;
import net.minecraft.core.BlockPos;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import net.neoforged.neoforge.network.registration.PayloadRegistrar;

/** What the townsfolk's talk and shops send between server and client. The client's side sets the hooks. */
public final class Net {
	private Net() {}

	private static <T extends CustomPacketPayload> CustomPacketPayload.Type<T> id(String path) {
		return new CustomPacketPayload.Type<>(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, path));
	}

	/** A node of a conversation to show (entity -1: it's over). */
	public record NpcTalk(int entity, String name, String title, String text, List<String> options) implements CustomPacketPayload {
		public static final Type<NpcTalk> TYPE = id("npc_talk");
		public static final StreamCodec<ByteBuf, NpcTalk> CODEC = StreamCodec.composite(
				ByteBufCodecs.VAR_INT, NpcTalk::entity, ByteBufCodecs.STRING_UTF8, NpcTalk::name, ByteBufCodecs.STRING_UTF8, NpcTalk::title,
				ByteBufCodecs.STRING_UTF8, NpcTalk::text, ByteBufCodecs.STRING_UTF8.apply(ByteBufCodecs.list()), NpcTalk::options, NpcTalk::new);
		@Override public Type<NpcTalk> type() { return TYPE; }
	}

	/** The answer picked (-1: they walked away from it). */
	public record NpcPick(int entity, int option) implements CustomPacketPayload {
		public static final Type<NpcPick> TYPE = id("npc_pick");
		public static final StreamCodec<ByteBuf, NpcPick> CODEC = StreamCodec.composite(
				ByteBufCodecs.VAR_INT, NpcPick::entity, ByteBufCodecs.VAR_INT, NpcPick::option, NpcPick::new);
		@Override public Type<NpcPick> type() { return TYPE; }
	}

	public record ShopLine(ItemStack stack, int price) {
		public static final StreamCodec<RegistryFriendlyByteBuf, ShopLine> CODEC = StreamCodec.composite(
				ItemStack.STREAM_CODEC, ShopLine::stack, ByteBufCodecs.VAR_INT, ShopLine::price, ShopLine::new);
	}

	/** A shopkeeper's wares, opened from their talk. */
	public record ShopOpen(int entity, String name, String title, List<ShopLine> buy, List<ShopLine> sell) implements CustomPacketPayload {
		public static final Type<ShopOpen> TYPE = id("shop_open");
		public static final StreamCodec<RegistryFriendlyByteBuf, ShopOpen> CODEC = StreamCodec.composite(
				ByteBufCodecs.VAR_INT, ShopOpen::entity, ByteBufCodecs.STRING_UTF8, ShopOpen::name, ByteBufCodecs.STRING_UTF8, ShopOpen::title,
				ShopLine.CODEC.apply(ByteBufCodecs.list()), ShopOpen::buy, ShopLine.CODEC.apply(ByteBufCodecs.list()), ShopOpen::sell, ShopOpen::new);
		@Override public Type<ShopOpen> type() { return TYPE; }
	}

	/** Buy (or sell) line `line` of the shop, `times` over. */
	public record ShopTrade(int entity, boolean sell, int line, int times) implements CustomPacketPayload {
		public static final Type<ShopTrade> TYPE = id("shop_trade");
		public static final StreamCodec<ByteBuf, ShopTrade> CODEC = StreamCodec.composite(
				ByteBufCodecs.VAR_INT, ShopTrade::entity, ByteBufCodecs.BOOL, ShopTrade::sell, ByteBufCodecs.VAR_INT, ShopTrade::line,
				ByteBufCodecs.VAR_INT, ShopTrade::times, ShopTrade::new);
		@Override public Type<ShopTrade> type() { return TYPE; }
	}

	/** Your purse. */
	public record Purse(int coins) implements CustomPacketPayload {
		public static final Type<Purse> TYPE = id("purse");
		public static final StreamCodec<ByteBuf, Purse> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, Purse::coins, Purse::new);
		@Override public Type<Purse> type() { return TYPE; }
	}

	/** Your mana now and at most. */
	/** your tree: the nodes you have, points left, the Epic Fight skills you have equipped */
	public record Tree(List<String> taken, int points, List<String> equipped) implements CustomPacketPayload {
		public static final Type<Tree> TYPE = id("tree");
		public static final StreamCodec<ByteBuf, Tree> CODEC = StreamCodec.composite(
				ByteBufCodecs.STRING_UTF8.apply(ByteBufCodecs.list()), Tree::taken, ByteBufCodecs.VAR_INT, Tree::points,
				ByteBufCodecs.STRING_UTF8.apply(ByteBufCodecs.list()), Tree::equipped, Tree::new);
		@Override public Type<Tree> type() { return TYPE; }
	}

	/** the tree screen asks: 0 take, 1 refund, 2 buy a level, 3 reset, 4 equip/unequip a skill (Passives.act) */
	public record TreeAct(int action, String node) implements CustomPacketPayload {
		public static final Type<TreeAct> TYPE = id("tree_act");
		public static final StreamCodec<ByteBuf, TreeAct> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, TreeAct::action,
				ByteBufCodecs.STRING_UTF8, TreeAct::node, TreeAct::new);
		@Override public Type<TreeAct> type() { return TYPE; }
	}

	/** your level, the Ash you hold and the next level's cost; gained: Ash just came in, up: you just levelled */
	public record Level(int level, int ash, int next, boolean gained, boolean up) implements CustomPacketPayload {
		public static final Type<Level> TYPE = id("level");
		public static final StreamCodec<ByteBuf, Level> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, Level::level,
				ByteBufCodecs.VAR_INT, Level::ash, ByteBufCodecs.VAR_INT, Level::next, ByteBufCodecs.BOOL, Level::gained,
				ByteBufCodecs.BOOL, Level::up, Level::new);
		@Override public Type<Level> type() { return TYPE; }
	}

	/** the curio key: 0 the worn relic's power, 1 a Gryphon Plume double jump, 2 (sneaking) the Rift Key */
	/** CurioKey's value for the R key's Joined skill. */
	public static final int JOINED_SKILL = 9;

	public record CurioKey(int what) implements CustomPacketPayload {
		public static final Type<CurioKey> TYPE = id("curio_key");
		public static final StreamCodec<ByteBuf, CurioKey> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, CurioKey::what, CurioKey::new);
		@Override public Type<CurioKey> type() { return TYPE; }
	}

	/** your relic's power just went on cooldown for this many ticks (client/RelicHud draws the sweep) */
	public record RelicCd(int ticks) implements CustomPacketPayload {
		public static final Type<RelicCd> TYPE = id("relic_cd");
		public static final StreamCodec<ByteBuf, RelicCd> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, RelicCd::ticks, RelicCd::new);
		@Override public Type<RelicCd> type() { return TYPE; }
	}

	/** when (System ms) the relic's cooldown ends and how long it was */
	public static volatile long relicCdEnd, relicCdTotal;

	public record Mana(float mana, float max) implements CustomPacketPayload {
		public static final Type<Mana> TYPE = id("mana");
		public static final StreamCodec<ByteBuf, Mana> CODEC = StreamCodec.composite(ByteBufCodecs.FLOAT, Mana::mana, ByteBufCodecs.FLOAT, Mana::max, Mana::new);
		@Override public Type<Mana> type() { return TYPE; }
	}

	/** Your max health is about to drop (a Hale piece taken off): the health update after it isn't a hit, so no flinch. */
	public record QuietHealth() implements CustomPacketPayload {
		public static final Type<QuietHealth> TYPE = id("quiet_health");
		public static final StreamCodec<ByteBuf, QuietHealth> CODEC = StreamCodec.unit(new QuietHealth());
		@Override public Type<QuietHealth> type() { return TYPE; }
	}

	/** until when (System ms) a health drop on the client is a lowered max, not a hit (mixin.LocalPlayerHurtMixin) */
	public static volatile long quietUntil;

	/** The Gate Forge at pos was used: open it. */
	/** Open the forge at pos; `known` is what the smith will make for you (ids, comma separated). */
	public record ForgeOpen(BlockPos pos, String known) implements CustomPacketPayload {
		public static final Type<ForgeOpen> TYPE = id("forge_open");
		public static final StreamCodec<ByteBuf, ForgeOpen> CODEC = StreamCodec.composite(BlockPos.STREAM_CODEC, ForgeOpen::pos, ByteBufCodecs.STRING_UTF8, ForgeOpen::known, ForgeOpen::new);
		@Override public Type<ForgeOpen> type() { return TYPE; }
	}

	/** Forge recipe `recipe` of dungeon `gate` (Gear.DUNGEONS order) at the forge at pos. */
	/** A piece of work at the forge (Smithing: MAKE, UPGRADE, FUSE, QUICK). Made: the gate and its recipe. Upgraded: the
	 * inventory slot. Fused: the slot, and the gate and weapon it becomes. */
	public record Job(int type, int gate, int recipe, int slot) {
		public static final StreamCodec<ByteBuf, Job> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, Job::type, ByteBufCodecs.VAR_INT, Job::gate,
				ByteBufCodecs.VAR_INT, Job::recipe, ByteBufCodecs.VAR_INT, Job::slot, Job::new);
	}

	/** The anvil's ready: where, the work, who the smith is (-1, nobody), which way you face, and, for a friend at the
	 * master's side, whose work it is (-1, your own). */
	/** The Cold Forge waking: its centre, the way it faces, how long the scene runs, when the blocks turn (ColdForge). */
	/** What the Journal shows: the quests done, the one being followed. */
	public record JournalState(String done, String tracked) implements CustomPacketPayload {
		public static final Type<JournalState> TYPE = id("journal_state");
		public static final StreamCodec<ByteBuf, JournalState> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, JournalState::done, ByteBufCodecs.STRING_UTF8, JournalState::tracked, JournalState::new);
		@Override public Type<JournalState> type() { return TYPE; }
	}

	/** A quest to follow; empty just asks for the Journal's state. */
	public record JournalPick(String key) implements CustomPacketPayload {
		public static final Type<JournalPick> TYPE = id("journal_pick");
		public static final StreamCodec<ByteBuf, JournalPick> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, JournalPick::key, JournalPick::new);
		@Override public Type<JournalPick> type() { return TYPE; }
	}

	/** What the compass points at. */
	/** A guild request as the Journal shows it. */
	public record PartyMember(String name, float health, float max, boolean leader, boolean online, boolean near) {
		static final StreamCodec<ByteBuf, PartyMember> STREAM = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, PartyMember::name, ByteBufCodecs.FLOAT, PartyMember::health, ByteBufCodecs.FLOAT, PartyMember::max,
				ByteBufCodecs.BOOL, PartyMember::leader, ByteBufCodecs.BOOL, PartyMember::online, ByteBufCodecs.BOOL, PartyMember::near, PartyMember::new);
	}

	public record PartySync(List<PartyMember> members) implements CustomPacketPayload {
		public static final Type<PartySync> TYPE = id("party_sync");
		public static final StreamCodec<ByteBuf, PartySync> CODEC = StreamCodec.composite(PartyMember.STREAM.apply(ByteBufCodecs.list()), PartySync::members, PartySync::new);
		@Override public Type<PartySync> type() { return TYPE; }
	}

	public record SpellFx(int kind, String gate, org.joml.Vector3f at, float r, int on) implements CustomPacketPayload {
		public static final Type<SpellFx> TYPE = id("spell_fx");
		public static final StreamCodec<ByteBuf, SpellFx> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, SpellFx::kind, ByteBufCodecs.STRING_UTF8, SpellFx::gate, ByteBufCodecs.VECTOR3F, SpellFx::at,
				ByteBufCodecs.FLOAT, SpellFx::r, ByteBufCodecs.VAR_INT, SpellFx::on, SpellFx::new);
		@Override public Type<SpellFx> type() { return TYPE; }
	}

	public record GuildJob(String id, String title, String text, int x, int z, boolean has) {
		static final StreamCodec<ByteBuf, GuildJob> STREAM = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, GuildJob::id, ByteBufCodecs.STRING_UTF8, GuildJob::title, ByteBufCodecs.STRING_UTF8, GuildJob::text,
				ByteBufCodecs.VAR_INT, GuildJob::x, ByteBufCodecs.VAR_INT, GuildJob::z, ByteBufCodecs.BOOL, GuildJob::has, GuildJob::new);
	}

	public record GuildJobs(List<GuildJob> jobs) implements CustomPacketPayload {
		public static final Type<GuildJobs> TYPE = id("guild_jobs");
		public static final StreamCodec<ByteBuf, GuildJobs> CODEC = StreamCodec.composite(GuildJob.STREAM.apply(ByteBufCodecs.list()), GuildJobs::jobs, GuildJobs::new);
		@Override public Type<GuildJobs> type() { return TYPE; }
	}

	public record QuestTrack(String title, int x, int z, boolean has) implements CustomPacketPayload {
		public static final Type<QuestTrack> TYPE = id("quest_track");
		public static final StreamCodec<ByteBuf, QuestTrack> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, QuestTrack::title, ByteBufCodecs.VAR_INT, QuestTrack::x,
				ByteBufCodecs.VAR_INT, QuestTrack::z, ByteBufCodecs.BOOL, QuestTrack::has, QuestTrack::new);
		@Override public Type<QuestTrack> type() { return TYPE; }
	}

	public record ColdWake(BlockPos centre, float face, int ends, int swap) implements CustomPacketPayload {
		public static final Type<ColdWake> TYPE = id("cold_wake");
		public static final StreamCodec<ByteBuf, ColdWake> CODEC = StreamCodec.composite(BlockPos.STREAM_CODEC, ColdWake::centre, ByteBufCodecs.FLOAT, ColdWake::face,
				ByteBufCodecs.VAR_INT, ColdWake::ends, ByteBufCodecs.VAR_INT, ColdWake::swap, ColdWake::new);
		@Override public Type<ColdWake> type() { return TYPE; }
	}

	public record ForgeStart(BlockPos anvil, boolean ghost, Job job, int smith, float face, int worker) implements CustomPacketPayload {
		public static final Type<ForgeStart> TYPE = id("forge_start");
		public static final StreamCodec<ByteBuf, ForgeStart> CODEC = StreamCodec.composite(BlockPos.STREAM_CODEC, ForgeStart::anvil, ByteBufCodecs.BOOL, ForgeStart::ghost,
				Job.CODEC, ForgeStart::job, ByteBufCodecs.VAR_INT, ForgeStart::smith, ByteBufCodecs.FLOAT, ForgeStart::face, ByteBufCodecs.VAR_INT, ForgeStart::worker, ForgeStart::new);
		@Override public Type<ForgeStart> type() { return TYPE; }
	}

	/** Something done at the anvil (Smithing.SWING and on), to pass on. */
	public record ForgeRelay(int action, float value) implements CustomPacketPayload {
		public static final Type<ForgeRelay> TYPE = id("forge_relay");
		public static final StreamCodec<ByteBuf, ForgeRelay> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, ForgeRelay::action, ByteBufCodecs.FLOAT, ForgeRelay::value, ForgeRelay::new);
		@Override public Type<ForgeRelay> type() { return TYPE; }
	}

	/** What someone at an anvil did. */
	public record ForgeEcho(int player, int action, float value) implements CustomPacketPayload {
		public static final Type<ForgeEcho> TYPE = id("forge_echo");
		public static final StreamCodec<ByteBuf, ForgeEcho> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, ForgeEcho::player, ByteBufCodecs.VAR_INT, ForgeEcho::action,
				ByteBufCodecs.FLOAT, ForgeEcho::value, ForgeEcho::new);
		@Override public Type<ForgeEcho> type() { return TYPE; }
	}

	/** The work's done (its score, a name if it earned one), or you walked off (score under 0). */
	public record ForgeDone(float score, String name) implements CustomPacketPayload {
		public static final Type<ForgeDone> TYPE = id("forge_done");
		public static final StreamCodec<ByteBuf, ForgeDone> CODEC = StreamCodec.composite(ByteBufCodecs.FLOAT, ForgeDone::score, ByteBufCodecs.STRING_UTF8, ForgeDone::name, ForgeDone::new);
		@Override public Type<ForgeDone> type() { return TYPE; }
	}

	public record ForgeCraft(BlockPos pos, Job job) implements CustomPacketPayload {
		public static final Type<ForgeCraft> TYPE = id("forge_craft");
		public static final StreamCodec<ByteBuf, ForgeCraft> CODEC = StreamCodec.composite(BlockPos.STREAM_CODEC, ForgeCraft::pos, Job.CODEC, ForgeCraft::job, ForgeCraft::new);
		@Override public Type<ForgeCraft> type() { return TYPE; }
	}

	/** Your guild card. */
	public record GuildSync(Guild.Card card) implements CustomPacketPayload {
		public static final Type<GuildSync> TYPE = id("guild_sync");
		public static final StreamCodec<ByteBuf, GuildSync> CODEC = StreamCodec.composite(Guild.Card.STREAM, GuildSync::card, GuildSync::new);
		@Override public Type<GuildSync> type() { return TYPE; }
	}

	/** The favours you've taken on (Errands). */
	public record ErrandSync(List<Errands.View> views) implements CustomPacketPayload {
		public static final Type<ErrandSync> TYPE = id("errand_sync");
		public static final StreamCodec<ByteBuf, ErrandSync> CODEC = StreamCodec.composite(Errands.View.STREAM.apply(ByteBufCodecs.list()), ErrandSync::views, ErrandSync::new);
		@Override public Type<ErrandSync> type() { return TYPE; }
	}

	/** One request as the board shows it. state: Guild.AVAILABLE / ACTIVE / READY / LOCKED. icon: an item id to draw it
	 *  with; gifts: the reward items as "id*count". */
	public record QuestView(String id, String title, int rank, String text, String objective, int progress, int count, String reward, int state,
							int coins, int points, String icon, List<String> gifts) {
		public static final StreamCodec<ByteBuf, QuestView> CODEC = StreamCodec.of((buf, v) -> {
			ByteBufCodecs.STRING_UTF8.encode(buf, v.id());
			ByteBufCodecs.STRING_UTF8.encode(buf, v.title());
			ByteBufCodecs.VAR_INT.encode(buf, v.rank());
			ByteBufCodecs.STRING_UTF8.encode(buf, v.text());
			ByteBufCodecs.STRING_UTF8.encode(buf, v.objective());
			ByteBufCodecs.VAR_INT.encode(buf, v.progress());
			ByteBufCodecs.VAR_INT.encode(buf, v.count());
			ByteBufCodecs.STRING_UTF8.encode(buf, v.reward());
			ByteBufCodecs.VAR_INT.encode(buf, v.state());
			ByteBufCodecs.VAR_INT.encode(buf, v.coins());
			ByteBufCodecs.VAR_INT.encode(buf, v.points());
			ByteBufCodecs.STRING_UTF8.encode(buf, v.icon());
			ByteBufCodecs.STRING_UTF8.apply(ByteBufCodecs.list()).encode(buf, v.gifts());
		}, buf -> new QuestView(ByteBufCodecs.STRING_UTF8.decode(buf), ByteBufCodecs.STRING_UTF8.decode(buf), ByteBufCodecs.VAR_INT.decode(buf),
				ByteBufCodecs.STRING_UTF8.decode(buf), ByteBufCodecs.STRING_UTF8.decode(buf), ByteBufCodecs.VAR_INT.decode(buf),
				ByteBufCodecs.VAR_INT.decode(buf), ByteBufCodecs.STRING_UTF8.decode(buf), ByteBufCodecs.VAR_INT.decode(buf),
				ByteBufCodecs.VAR_INT.decode(buf), ByteBufCodecs.VAR_INT.decode(buf), ByteBufCodecs.STRING_UTF8.decode(buf),
				ByteBufCodecs.STRING_UTF8.apply(ByteBufCodecs.list()).decode(buf)));
	}

	/** The guild's board, opened (or refreshed) at a receptionist. */
	public record QuestBoard(int entity, List<QuestView> quests) implements CustomPacketPayload {
		public static final Type<QuestBoard> TYPE = id("quest_board");
		public static final StreamCodec<ByteBuf, QuestBoard> CODEC = StreamCodec.composite(
				ByteBufCodecs.VAR_INT, QuestBoard::entity, QuestView.CODEC.apply(ByteBufCodecs.list()), QuestBoard::quests, QuestBoard::new);
		@Override public Type<QuestBoard> type() { return TYPE; }
	}

	/** Take, abandon or report a request (Guild.ACCEPT / ABANDON / REPORT). */
	public record QuestAct(int entity, int action, String quest) implements CustomPacketPayload {
		public static final Type<QuestAct> TYPE = id("quest_act");
		public static final StreamCodec<ByteBuf, QuestAct> CODEC = StreamCodec.composite(
				ByteBufCodecs.VAR_INT, QuestAct::entity, ByteBufCodecs.VAR_INT, QuestAct::action, ByteBufCodecs.STRING_UTF8, QuestAct::quest, QuestAct::new);
		@Override public Type<QuestAct> type() { return TYPE; }
	}

	// the client's handlers (AshboundClient sets them)
	public static Consumer<NpcTalk> onTalk = m -> {};
	public static Consumer<ShopOpen> onShop = m -> {};
	public static IntConsumer onPurse = n -> Coins.client = n;
	public static Consumer<ForgeOpen> onForge = m -> {};
	public static Consumer<ForgeStart> onForgeStart = m -> {};
	public static Consumer<ColdWake> onColdWake = m -> {};
	public static Consumer<JournalState> onJournal = m -> {};
	public static Consumer<QuestTrack> onQuestTrack = m -> {};
	public static Consumer<GuildJobs> onGuildJobs = m -> {};
	public static Consumer<SpellFx> onSpellFx = m -> {};
	public static List<PartyMember> clientParty = List.of();
	public static Consumer<ForgeEcho> onForgeEcho = m -> {};
	public static Consumer<QuestBoard> onBoard = m -> {};
	public static Runnable onCard = () -> {};

	static void register(IEventBus bus) {
		bus.addListener((RegisterPayloadHandlersEvent e) -> {
			PayloadRegistrar r = e.registrar("1");
			r.playToClient(NpcTalk.TYPE, NpcTalk.CODEC, (m, ctx) -> onTalk.accept(m));
			r.playToClient(ShopOpen.TYPE, ShopOpen.CODEC, (m, ctx) -> onShop.accept(m));
			r.playToClient(Purse.TYPE, Purse.CODEC, (m, ctx) -> onPurse.accept(m.coins()));
			r.playToClient(GuildSync.TYPE, GuildSync.CODEC, (m, ctx) -> Guild.client = m.card());
			r.playToClient(ErrandSync.TYPE, ErrandSync.CODEC, (m, ctx) -> Errands.client = m.views());
			r.playToClient(QuestBoard.TYPE, QuestBoard.CODEC, (m, ctx) -> onBoard.accept(m));
			r.playToServer(QuestAct.TYPE, QuestAct.CODEC, (m, ctx) -> Guild.onAct(m, (ServerPlayer) ctx.player()));
			r.playToClient(Mana.TYPE, Mana.CODEC, (m, ctx) -> {
				Spells.clientMana = m.mana();
				Spells.clientMax = m.max();
			});
			r.playToClient(Tree.TYPE, Tree.CODEC, (m, ctx) -> {
				Passives.clientSet(m.taken());
				if (ctx.player() != null) Passives.clientSelf = ctx.player().getUUID();
				Passives.clientPoints = m.points();
				Passives.clientEquipped = new java.util.HashSet<>(m.equipped());
			});
			r.playToServer(TreeAct.TYPE, TreeAct.CODEC, (m, ctx) -> Passives.act((ServerPlayer) ctx.player(), m.action(), m.node()));
			r.playToClient(Level.TYPE, Level.CODEC, (m, ctx) -> {
				Levels.clientLevel = m.level();
				Levels.clientAsh = m.ash();
				Levels.clientNext = m.next();
				long now = System.currentTimeMillis();
				if (m.gained()) Levels.clientGained = now;
				if (m.up()) Levels.clientLevelled = now;
			});
			r.playToClient(ForgeOpen.TYPE, ForgeOpen.CODEC, (m, ctx) -> onForge.accept(m));
			r.playToClient(QuietHealth.TYPE, QuietHealth.CODEC, (m, ctx) -> quietUntil = System.currentTimeMillis() + 500);
			r.playToServer(ForgeCraft.TYPE, ForgeCraft.CODEC, (m, ctx) -> GateForge.onCraft(m, (ServerPlayer) ctx.player()));
			r.playToClient(ForgeStart.TYPE, ForgeStart.CODEC, (m, ctx) -> onForgeStart.accept(m));
			r.playToClient(ColdWake.TYPE, ColdWake.CODEC, (m, ctx) -> onColdWake.accept(m));
			r.playToClient(JournalState.TYPE, JournalState.CODEC, (m, ctx) -> onJournal.accept(m));
			r.playToClient(QuestTrack.TYPE, QuestTrack.CODEC, (m, ctx) -> onQuestTrack.accept(m));
			r.playToClient(GuildJobs.TYPE, GuildJobs.CODEC, (m, ctx) -> onGuildJobs.accept(m));
			r.playToClient(SpellFx.TYPE, SpellFx.CODEC, (m, ctx) -> onSpellFx.accept(m));
			r.playToClient(PartySync.TYPE, PartySync.CODEC, (m, ctx) -> clientParty = m.members());
			r.playToServer(JournalPick.TYPE, JournalPick.CODEC, (m, ctx) -> Story.pick((ServerPlayer) ctx.player(), m.key()));
			r.playToServer(ForgeRelay.TYPE, ForgeRelay.CODEC, (m, ctx) -> Smithing.onRelay(m, (ServerPlayer) ctx.player()));
			r.playToClient(ForgeEcho.TYPE, ForgeEcho.CODEC, (m, ctx) -> onForgeEcho.accept(m));
			r.playToServer(ForgeDone.TYPE, ForgeDone.CODEC, (m, ctx) -> Smithing.onDone(m, (ServerPlayer) ctx.player()));
			r.playToClient(RelicCd.TYPE, RelicCd.CODEC, (m, ctx) -> {
				relicCdTotal = m.ticks() * 50L;
				relicCdEnd = System.currentTimeMillis() + relicCdTotal;
			});
			r.playToServer(CurioKey.TYPE, CurioKey.CODEC, (m, ctx) -> {
				if (m.what() == JOINED_SKILL) JoinedSkills.use((ServerPlayer) ctx.player());
				else CurioFx.key((ServerPlayer) ctx.player(), m.what());
			});
			r.playToServer(NpcPick.TYPE, NpcPick.CODEC, (m, ctx) -> Talk.onPick(m, (ServerPlayer) ctx.player()));
			r.playToServer(ShopTrade.TYPE, ShopTrade.CODEC, (m, ctx) -> Shop.onTrade(m, (ServerPlayer) ctx.player()));
		});
	}
}
