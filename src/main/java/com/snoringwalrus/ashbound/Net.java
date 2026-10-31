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
	/** CurioKey's value for the mount key. */
	public static final int MOUNT = 10;
	/** CurioKey's value for the Form key. */
	public static final int FORM = 11;

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

	/** Your class; empty means the server wants you to choose one. */
	public record ClassState(String key) implements CustomPacketPayload {
		public static final Type<ClassState> TYPE = id("class_state");
		public static final StreamCodec<ByteBuf, ClassState> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, ClassState::key, ClassState::new);
		@Override public Type<ClassState> type() { return TYPE; }
	}

	/** The party member your white staff answers to; empty for none. */
	public record HealPick(String name) implements CustomPacketPayload {
		public static final Type<HealPick> TYPE = id("heal_pick");
		public static final StreamCodec<ByteBuf, HealPick> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, HealPick::name, HealPick::new);
		@Override public Type<HealPick> type() { return TYPE; }
	}

	/** Your mount, or empty to ask you for one. */
	public record MountState(String key) implements CustomPacketPayload {
		public static final Type<MountState> TYPE = id("mount_state");
		public static final StreamCodec<ByteBuf, MountState> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, MountState::key, MountState::new);
		@Override public Type<MountState> type() { return TYPE; }
	}

	/** Your first path, what you know as skill=rank, your keys, and the levels you've chosen on. */
	public record SkillState(String spec, java.util.List<String> known, java.util.List<String> bar, int picks) implements CustomPacketPayload {
		public static final Type<SkillState> TYPE = id("skill_state");
		public static final StreamCodec<ByteBuf, SkillState> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, SkillState::spec,
				ByteBufCodecs.STRING_UTF8.apply(ByteBufCodecs.list()), SkillState::known, ByteBufCodecs.STRING_UTF8.apply(ByteBufCodecs.list()), SkillState::bar, ByteBufCodecs.VAR_INT, SkillState::picks, SkillState::new);
		@Override public Type<SkillState> type() { return TYPE; }
	}

	/** A blow that landed: both of them stop for a moment (HitStop). */
	public record HitHold(int by, int on, int ticks) implements CustomPacketPayload {
		public static final Type<HitHold> TYPE = id("hit_hold");
		public static final StreamCodec<ByteBuf, HitHold> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, HitHold::by, ByteBufCodecs.VAR_INT, HitHold::on, ByteBufCodecs.VAR_INT, HitHold::ticks, HitHold::new);
		@Override public Type<HitHold> type() { return TYPE; }
	}

	public record SkillCool(String key, int ticks) implements CustomPacketPayload {
		public static final Type<SkillCool> TYPE = id("skill_cool");
		public static final StreamCodec<ByteBuf, SkillCool> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, SkillCool::key, ByteBufCodecs.VAR_INT, SkillCool::ticks, SkillCool::new);
		@Override public Type<SkillCool> type() { return TYPE; }
	}

	public record SkillUse(int slot) implements CustomPacketPayload {
		public static final Type<SkillUse> TYPE = id("skill_use");
		public static final StreamCodec<ByteBuf, SkillUse> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, SkillUse::slot, SkillUse::new);
		@Override public Type<SkillUse> type() { return TYPE; }
	}

	public record SkillPick(String key) implements CustomPacketPayload {
		public static final Type<SkillPick> TYPE = id("skill_pick");
		public static final StreamCodec<ByteBuf, SkillPick> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, SkillPick::key, SkillPick::new);
		@Override public Type<SkillPick> type() { return TYPE; }
	}

	public record SkillSet(int slot, String key) implements CustomPacketPayload {
		public static final Type<SkillSet> TYPE = id("skill_set");
		public static final StreamCodec<ByteBuf, SkillSet> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, SkillSet::slot, ByteBufCodecs.STRING_UTF8, SkillSet::key, SkillSet::new);
		@Override public Type<SkillSet> type() { return TYPE; }
	}

	/** Your Form: which, whether its moment has come, ticks left in it, ticks until it can come again. */
	public record FormState(String form, boolean ready, int left, int rest) implements CustomPacketPayload {
		public static final Type<FormState> TYPE = id("form_state");
		public static final StreamCodec<ByteBuf, FormState> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, FormState::form, ByteBufCodecs.BOOL, FormState::ready,
				ByteBufCodecs.VAR_INT, FormState::left, ByteBufCodecs.VAR_INT, FormState::rest, FormState::new);
		@Override public Type<FormState> type() { return TYPE; }
	}

	/** Who's in what Form, for everyone who can see them; empty when it ends. */
	public record FormAura(int entity, String form) implements CustomPacketPayload {
		public static final Type<FormAura> TYPE = id("form_aura");
		public static final StreamCodec<ByteBuf, FormAura> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, FormAura::entity, ByteBufCodecs.STRING_UTF8, FormAura::form, FormAura::new);
		@Override public Type<FormAura> type() { return TYPE; }
	}

	/** A skill's look: its name, where, which way, how big, and who it's on. */
	public record SkillFx(String look, org.joml.Vector3f at, org.joml.Vector3f dir, float r, int on) implements CustomPacketPayload {
		public static final Type<SkillFx> TYPE = id("skill_fx");
		public static final StreamCodec<ByteBuf, SkillFx> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, SkillFx::look, ByteBufCodecs.VECTOR3F, SkillFx::at, ByteBufCodecs.VECTOR3F, SkillFx::dir,
				ByteBufCodecs.FLOAT, SkillFx::r, ByteBufCodecs.VAR_INT, SkillFx::on, SkillFx::new);
		@Override public Type<SkillFx> type() { return TYPE; }
	}

	/** Ticks of no more than 0 cuts it. */
	public record HealBeam(int from, int to, int ticks, String gate) implements CustomPacketPayload {
		public static final Type<HealBeam> TYPE = id("heal_beam");
		public static final StreamCodec<ByteBuf, HealBeam> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, HealBeam::from, ByteBufCodecs.VAR_INT, HealBeam::to, ByteBufCodecs.VAR_INT, HealBeam::ticks,
				ByteBufCodecs.STRING_UTF8, HealBeam::gate, HealBeam::new);
		@Override public Type<HealBeam> type() { return TYPE; }
	}

	/** The book in your hand wants one of your skills. */
	public record BookOffer(String skill, int rank) implements CustomPacketPayload {
		public static final Type<BookOffer> TYPE = id("book_offer");
		public static final StreamCodec<ByteBuf, BookOffer> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, BookOffer::skill, ByteBufCodecs.VAR_INT, BookOffer::rank, BookOffer::new);
		@Override public Type<BookOffer> type() { return TYPE; }
	}

	public record BookSwap(String give) implements CustomPacketPayload {
		public static final Type<BookSwap> TYPE = id("book_swap");
		public static final StreamCodec<ByteBuf, BookSwap> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, BookSwap::give, BookSwap::new);
		@Override public Type<BookSwap> type() { return TYPE; }
	}

	public record TomeRead(String form) implements CustomPacketPayload {
		public static final Type<TomeRead> TYPE = id("tome_read");
		public static final StreamCodec<ByteBuf, TomeRead> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, TomeRead::form, TomeRead::new);
		@Override public Type<TomeRead> type() { return TYPE; }
	}

	/** A Tidy button. */
	public record InvTidy(int what) implements CustomPacketPayload {
		public static final Type<InvTidy> TYPE = id("inv_tidy");
		public static final StreamCodec<ByteBuf, InvTidy> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, InvTidy::what, InvTidy::new);
		@Override public Type<InvTidy> type() { return TYPE; }
	}

	public record MountPick(String key) implements CustomPacketPayload {
		public static final Type<MountPick> TYPE = id("mount_pick");
		public static final StreamCodec<ByteBuf, MountPick> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, MountPick::key, MountPick::new);
		@Override public Type<MountPick> type() { return TYPE; }
	}

	public record ClassPick(String key) implements CustomPacketPayload {
		public static final Type<ClassPick> TYPE = id("class_pick");
		public static final StreamCodec<ByteBuf, ClassPick> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, ClassPick::key, ClassPick::new);
		@Override public Type<ClassPick> type() { return TYPE; }
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

	/** Hob's telling starts: where the wagon stands and which way it faces, and where Highmourn is if there's one. */
	public record IntroPlay(BlockPos at, float yaw, boolean known, int x, int z) implements CustomPacketPayload {
		public static final Type<IntroPlay> TYPE = id("intro_play");
		public static final StreamCodec<ByteBuf, IntroPlay> CODEC = StreamCodec.composite(BlockPos.STREAM_CODEC, IntroPlay::at, ByteBufCodecs.FLOAT, IntroPlay::yaw,
				ByteBufCodecs.BOOL, IntroPlay::known, ByteBufCodecs.VAR_INT, IntroPlay::x, ByteBufCodecs.VAR_INT, IntroPlay::z, IntroPlay::new);
		@Override public Type<IntroPlay> type() { return TYPE; }
	}

	/** The telling's over on this client, or was skipped. */
	public record IntroDone() implements CustomPacketPayload {
		public static final Type<IntroDone> TYPE = id("intro_done");
		public static final StreamCodec<ByteBuf, IntroDone> CODEC = StreamCodec.unit(new IntroDone());
		@Override public Type<IntroDone> type() { return TYPE; }
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
	public static Consumer<IntroPlay> onIntro = m -> {};
	public static Consumer<JournalState> onJournal = m -> {};
	public static Consumer<QuestTrack> onQuestTrack = m -> {};
	public static Consumer<GuildJobs> onGuildJobs = m -> {};
	public static Consumer<SpellFx> onSpellFx = m -> {};
	public static List<PartyMember> clientParty = List.of();
	public static Consumer<ForgeEcho> onForgeEcho = m -> {};
	public static Consumer<QuestBoard> onBoard = m -> {};
	public static Runnable onCard = () -> {};
	public static Runnable onClassAsk = () -> {};
	public static Runnable onMountAsk = () -> {};
	public static java.util.function.Consumer<FormAura> onFormAura = m -> {};
	public static java.util.function.Consumer<SkillFx> onSkillFx = m -> {};
	public static java.util.function.Consumer<HealBeam> onHealBeam = m -> {};

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
			r.playToClient(IntroPlay.TYPE, IntroPlay.CODEC, (m, ctx) -> onIntro.accept(m));
			r.playToServer(IntroDone.TYPE, IntroDone.CODEC, (m, ctx) -> Intro.done((ServerPlayer) ctx.player()));
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
				if (m.what() == JOINED_SKILL) Skills.use((ServerPlayer) ctx.player(), 0);
				else if (m.what() == MOUNT) Mounts.toggle((ServerPlayer) ctx.player());
				else if (m.what() == FORM) Forms.key((ServerPlayer) ctx.player());
				else CurioFx.key((ServerPlayer) ctx.player(), m.what());
			});
			r.playToClient(ClassState.TYPE, ClassState.CODEC, (m, ctx) -> {
				Classes.client = m.key();
				if (m.key().isEmpty()) onClassAsk.run();
			});
			r.playToClient(MountState.TYPE, MountState.CODEC, (m, ctx) -> {
				Mounts.client = m.key();
				if (m.key().isEmpty()) onMountAsk.run();
			});
			r.playToServer(MountPick.TYPE, MountPick.CODEC, (m, ctx) -> Mounts.pick((ServerPlayer) ctx.player(), m.key()));
			r.playToServer(InvTidy.TYPE, InvTidy.CODEC, (m, ctx) -> Tidy.act((ServerPlayer) ctx.player(), m.what()));
			r.playToServer(TomeRead.TYPE, TomeRead.CODEC, (m, ctx) -> Books.confirm((ServerPlayer) ctx.player(), m.form()));
			r.playToClient(BookOffer.TYPE, BookOffer.CODEC, (m, ctx) -> Books.onOffer.accept(m));
			r.playToServer(BookSwap.TYPE, BookSwap.CODEC, (m, ctx) -> Books.swap((ServerPlayer) ctx.player(), m.give()));
			r.playToClient(FormState.TYPE, FormState.CODEC, (m, ctx) -> {
				Forms.clientForm = m.form();
				Forms.clientReady = m.ready();
				Forms.clientUntil = System.currentTimeMillis() + m.left() * 50L;
				Forms.clientRest = System.currentTimeMillis() + m.rest() * 50L;
			});
			r.playToClient(FormAura.TYPE, FormAura.CODEC, (m, ctx) -> onFormAura.accept(m));
			r.playToClient(SkillFx.TYPE, SkillFx.CODEC, (m, ctx) -> onSkillFx.accept(m));
			r.playToClient(HealBeam.TYPE, HealBeam.CODEC, (m, ctx) -> onHealBeam.accept(m));
			r.playToServer(SkillUse.TYPE, SkillUse.CODEC, (m, ctx) -> Skills.use((ServerPlayer) ctx.player(), m.slot()));
			r.playToServer(SkillPick.TYPE, SkillPick.CODEC, (m, ctx) -> Skills.pick((ServerPlayer) ctx.player(), m.key()));
			r.playToServer(SkillSet.TYPE, SkillSet.CODEC, (m, ctx) -> Skills.assign((ServerPlayer) ctx.player(), m.slot(), m.key()));
			r.playToClient(SkillState.TYPE, SkillState.CODEC, (m, ctx) -> {
				Skills.clientSpec = m.spec();
				Skills.clientPicks = m.picks();
				java.util.Map<String, Integer> ranks = new java.util.HashMap<>();
				for (String k : m.known()) ranks.put(k.substring(0, k.indexOf('=')), Integer.parseInt(k.substring(k.indexOf('=') + 1)));
				Skills.clientRanks = ranks;
				Skills.clientBar = m.bar().toArray(new String[0]);
			});
			r.playToClient(HitHold.TYPE, HitHold.CODEC, (m, ctx) -> {
				for (int id : new int[] {m.by(), m.on()}) {
					var held = ctx.player().level().getEntity(id);
					if (held != null) HitStop.hold(held, m.ticks());
				}
			});
			r.playToClient(SkillCool.TYPE, SkillCool.CODEC, (m, ctx) ->
					Skills.clientCooling.put(m.key(), new long[] {System.currentTimeMillis() + m.ticks() * 50L, m.ticks() * 50L}));
			r.playToServer(HealPick.TYPE, HealPick.CODEC, (m, ctx) -> Spells.pickHealTarget((ServerPlayer) ctx.player(), m.name()));
			r.playToServer(ClassPick.TYPE, ClassPick.CODEC, (m, ctx) -> Classes.pick((ServerPlayer) ctx.player(), m.key()));
			r.playToServer(NpcPick.TYPE, NpcPick.CODEC, (m, ctx) -> Talk.onPick(m, (ServerPlayer) ctx.player()));
			r.playToServer(ShopTrade.TYPE, ShopTrade.CODEC, (m, ctx) -> Shop.onTrade(m, (ServerPlayer) ctx.player()));
		});
	}
}
