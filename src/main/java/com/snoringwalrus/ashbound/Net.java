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

	/** Right-clicking something in the belt pouch. */
	public record PouchUse(int slot) implements CustomPacketPayload {
		public static final Type<PouchUse> TYPE = id("pouch_use");
		public static final StreamCodec<ByteBuf, PouchUse> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, PouchUse::slot, PouchUse::new);
		@Override public Type<PouchUse> type() { return TYPE; }
	}

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

	/** A hit or a heal you just did, for the number over it. */
	public record HitNumber(double x, double y, double z, float amount, int kind) implements CustomPacketPayload {
		public static final int HIT = 0, THRALL = 1, HEAL = 2;
		public static final Type<HitNumber> TYPE = id("hit_number");
		public static final StreamCodec<ByteBuf, HitNumber> CODEC = StreamCodec.composite(ByteBufCodecs.DOUBLE, HitNumber::x, ByteBufCodecs.DOUBLE, HitNumber::y, ByteBufCodecs.DOUBLE, HitNumber::z,
				ByteBufCodecs.FLOAT, HitNumber::amount, ByteBufCodecs.VAR_INT, HitNumber::kind, HitNumber::new);
		@Override public Type<HitNumber> type() { return TYPE; }
	}

	public static java.util.function.Consumer<HitNumber> onHitNumber = m -> {};

	/** @param over healing sent that found nobody hurt (the health bar was already full) */
	public record MeterLine(String name, float damage, float heal, float over) {
		static final StreamCodec<ByteBuf, MeterLine> STREAM = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, MeterLine::name, ByteBufCodecs.FLOAT, MeterLine::damage, ByteBufCodecs.FLOAT, MeterLine::heal,
				ByteBufCodecs.FLOAT, MeterLine::over, MeterLine::new);
	}

	/** Everyone's totals in this fight and how long it's gone on. */
	public record Meter(List<MeterLine> lines, float seconds) implements CustomPacketPayload {
		public static final Type<Meter> TYPE = id("meter");
		public static final StreamCodec<ByteBuf, Meter> CODEC = StreamCodec.composite(MeterLine.STREAM.apply(ByteBufCodecs.list()), Meter::lines, ByteBufCodecs.FLOAT, Meter::seconds, Meter::new);
		@Override public Type<Meter> type() { return TYPE; }
	}

	public static volatile Meter clientMeter;
	public static volatile long clientMeterAt;

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
	public record ForgeOpen(BlockPos pos) implements CustomPacketPayload {
		public static final Type<ForgeOpen> TYPE = id("forge_open");
		public static final StreamCodec<ByteBuf, ForgeOpen> CODEC = StreamCodec.composite(BlockPos.STREAM_CODEC, ForgeOpen::pos, ForgeOpen::new);
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
	/** What the Journal shows: the quests done, those being followed (both comma-separated). */
	public record JournalState(String done, String tracked) implements CustomPacketPayload {
		public static final Type<JournalState> TYPE = id("journal_state");
		public static final StreamCodec<ByteBuf, JournalState> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, JournalState::done, ByteBufCodecs.STRING_UTF8, JournalState::tracked, JournalState::new);
		@Override public Type<JournalState> type() { return TYPE; }
	}

	/** A quest to follow too, "unfollow:" or "abandon:" one; empty just asks for the Journal's state. */
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
	/** have: how far you are toward the Form's moment where it can be counted (the Crown's thralls out), else -1 */
	public record FormState(String form, boolean ready, int left, int rest, int have) implements CustomPacketPayload {
		public static final Type<FormState> TYPE = id("form_state");
		public static final StreamCodec<ByteBuf, FormState> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, FormState::form, ByteBufCodecs.BOOL, FormState::ready,
				ByteBufCodecs.VAR_INT, FormState::left, ByteBufCodecs.VAR_INT, FormState::rest, ByteBufCodecs.VAR_INT, FormState::have, FormState::new);
		@Override public Type<FormState> type() { return TYPE; }
	}

	/** Who's in what Form, for everyone who can see them; empty when it ends. */
	public record FormAura(int entity, String form) implements CustomPacketPayload {
		public static final Type<FormAura> TYPE = id("form_aura");
		public static final StreamCodec<ByteBuf, FormAura> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, FormAura::entity, ByteBufCodecs.STRING_UTF8, FormAura::form, FormAura::new);
		@Override public Type<FormAura> type() { return TYPE; }
	}

	/** A skill's look: its name, where, which way, how big, and who it's on. */
	/** @param by the player whose it is (-1: a monster's, the world's), for each client's allies' effects setting */
	public record SkillFx(String look, org.joml.Vector3f at, org.joml.Vector3f dir, float r, int on, int by) implements CustomPacketPayload {
		public static final Type<SkillFx> TYPE = id("skill_fx");
		public static final StreamCodec<ByteBuf, SkillFx> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, SkillFx::look, ByteBufCodecs.VECTOR3F, SkillFx::at, ByteBufCodecs.VECTOR3F, SkillFx::dir,
				ByteBufCodecs.FLOAT, SkillFx::r, ByteBufCodecs.VAR_INT, SkillFx::on, ByteBufCodecs.VAR_INT, SkillFx::by, SkillFx::new);
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

	/** A wanted poster, read (Bounties.read): what it says, and what you can do. state: 0 take it, 1 you're hunting it, 2 claim your bounty,
	 * 3 slain by someone else, 4 your hands are full. nums: rank, coins, points, bounty id; texts: legend, name, land, way, slain by. */
	public record PosterView(int entity, int state, List<Integer> nums, List<String> texts) implements CustomPacketPayload {
		public static final Type<PosterView> TYPE = id("poster_view");
		public static final StreamCodec<ByteBuf, PosterView> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, PosterView::entity, ByteBufCodecs.VAR_INT, PosterView::state,
				ByteBufCodecs.VAR_INT.apply(ByteBufCodecs.list()), PosterView::nums, ByteBufCodecs.STRING_UTF8.apply(ByteBufCodecs.list()), PosterView::texts, PosterView::new);
		@Override public Type<PosterView> type() { return TYPE; }
	}

	/** Ashfall night on or off (Ashfall), and since when (game time). */
	/** The Ring's crowd reacting (Arena.cheer): which Ring, and how (0 a kill, 1 a wave, 2 a win, 3 a ruler / fight on, 4 one falls). */
	public record ArenaCheer(int slot, int kind) implements CustomPacketPayload {
		public static final Type<ArenaCheer> TYPE = id("arena_cheer");
		public static final StreamCodec<ByteBuf, ArenaCheer> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, ArenaCheer::slot, ByteBufCodecs.VAR_INT, ArenaCheer::kind, ArenaCheer::new);
		@Override public Type<ArenaCheer> type() { return TYPE; }
	}

	public static Consumer<ArenaCheer> onCheer = m -> {};

	public record AshfallSync(boolean on, long since) implements CustomPacketPayload {
		public static final Type<AshfallSync> TYPE = id("ashfall_sync");
		public static final StreamCodec<ByteBuf, AshfallSync> CODEC = StreamCodec.composite(ByteBufCodecs.BOOL, AshfallSync::on, ByteBufCodecs.VAR_LONG, AshfallSync::since, AshfallSync::new);
		@Override public Type<AshfallSync> type() { return TYPE; }
	}

	/** "Take it" (or "Claim the bounty") on a poster's screen. */
	public record PosterAct(int entity) implements CustomPacketPayload {
		public static final Type<PosterAct> TYPE = id("poster_act");
		public static final StreamCodec<ByteBuf, PosterAct> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, PosterAct::entity, PosterAct::new);
		@Override public Type<PosterAct> type() { return TYPE; }
	}

	public record TomeRead(String form) implements CustomPacketPayload {
		public static final Type<TomeRead> TYPE = id("tome_read");
		public static final StreamCodec<ByteBuf, TomeRead> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, TomeRead::form, TomeRead::new);
		@Override public Type<TomeRead> type() { return TYPE; }
	}

	/** What your mount has learned, by track. */
	public record MountRanks(List<Integer> ranks) implements CustomPacketPayload {
		public static final Type<MountRanks> TYPE = id("mount_ranks");
		public static final StreamCodec<ByteBuf, MountRanks> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT.apply(ByteBufCodecs.list()), MountRanks::ranks, MountRanks::new);
		@Override public Type<MountRanks> type() { return TYPE; }
	}

	/** Buy the next rank of a track. */
	public record MountUp(int track) implements CustomPacketPayload {
		public static final Type<MountUp> TYPE = id("mount_up");
		public static final StreamCodec<ByteBuf, MountUp> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, MountUp::track, MountUp::new);
		@Override public Type<MountUp> type() { return TYPE; }
	}

	/** One kind in the Bottomless Bag: a single of it, how many, and whose when it's a party's. */
	public record BagLine(ItemStack stack, long count, String who) {
		public static final StreamCodec<RegistryFriendlyByteBuf, BagLine> CODEC = StreamCodec.composite(
				ItemStack.STREAM_CODEC, BagLine::stack, ByteBufCodecs.VAR_LONG, BagLine::count, ByteBufCodecs.STRING_UTF8, BagLine::who, BagLine::new);
	}

	/** All that's in the bag you have open, and how many it's shared by. */
	public record BagLines(List<BagLine> lines, int sharing) implements CustomPacketPayload {
		public static final Type<BagLines> TYPE = id("bag_lines");
		public static final StreamCodec<RegistryFriendlyByteBuf, BagLines> CODEC = StreamCodec.composite(
				BagLine.CODEC.apply(ByteBufCodecs.list()), BagLines::lines, ByteBufCodecs.VAR_INT, BagLines::sharing, BagLines::new);
		@Override public Type<BagLines> type() { return TYPE; }
	}

	/** What's done with the bag (Bag.OPEN and so on), and to what. */
	/** Your trades as the server keeps them (Trades.STATE): levels, perks, known recipes, running buffs. */
	public record TradeState(java.util.Map<String, String> state) implements CustomPacketPayload {
		public static final Type<TradeState> TYPE = id("trade_state");
		public static final StreamCodec<ByteBuf, TradeState> CODEC = StreamCodec.composite(
				ByteBufCodecs.map(java.util.HashMap::new, ByteBufCodecs.STRING_UTF8, ByteBufCodecs.STRING_UTF8), TradeState::state, TradeState::new);
		@Override public Type<TradeState> type() { return TYPE; }
	}

	/** A bench's Craft, a perk taken, perks forgotten, the book's make-again (Trades.CRAFT and the rest). */
	/** A bench's station: what's on its fire and tray (Kitchen), each thing's done tick, and the server's tick now. */
	public record KitchenState(List<net.minecraft.world.item.ItemStack> items, List<Long> start, List<Long> done, long now) implements CustomPacketPayload {
		public static final Type<KitchenState> TYPE = id("kitchen_state");
		public static final StreamCodec<net.minecraft.network.RegistryFriendlyByteBuf, KitchenState> CODEC = StreamCodec.composite(
				net.minecraft.world.item.ItemStack.OPTIONAL_STREAM_CODEC.apply(ByteBufCodecs.list()), KitchenState::items,
				ByteBufCodecs.VAR_LONG.apply(ByteBufCodecs.list()), KitchenState::start,
				ByteBufCodecs.VAR_LONG.apply(ByteBufCodecs.list()), KitchenState::done, ByteBufCodecs.VAR_LONG, KitchenState::now, KitchenState::new);
		@Override public Type<KitchenState> type() { return TYPE; }
	}

	public static KitchenState clientKitchen = new KitchenState(List.of(), List.of(), List.of(), 0);
	public static long clientKitchenAt;

	public record TradeAct(int what, String arg) implements CustomPacketPayload {
		public static final Type<TradeAct> TYPE = id("trade_act");
		public static final StreamCodec<ByteBuf, TradeAct> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, TradeAct::what, ByteBufCodecs.STRING_UTF8, TradeAct::arg, TradeAct::new);
		@Override public Type<TradeAct> type() { return TYPE; }
	}

	public record PetAct(String pet) implements CustomPacketPayload {
		public static final Type<PetAct> TYPE = id("pet_act");
		public static final StreamCodec<ByteBuf, PetAct> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, PetAct::pet, PetAct::new);
		@Override public Type<PetAct> type() { return TYPE; }
	}

	/** The pets you have to hand, and the one that's out. */
	public record PetList(List<String> owned, String worn) implements CustomPacketPayload {
		public static final Type<PetList> TYPE = id("pet_list");
		public static final StreamCodec<ByteBuf, PetList> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8.apply(ByteBufCodecs.list()), PetList::owned, ByteBufCodecs.STRING_UTF8, PetList::worn, PetList::new);
		@Override public Type<PetList> type() { return TYPE; }
	}

	public record BagAct(int what, ItemStack item) implements CustomPacketPayload {
		public static final Type<BagAct> TYPE = id("bag_act");
		public static final StreamCodec<RegistryFriendlyByteBuf, BagAct> CODEC = StreamCodec.composite(
				ByteBufCodecs.VAR_INT, BagAct::what, ItemStack.OPTIONAL_STREAM_CODEC, BagAct::item, BagAct::new);
		@Override public Type<BagAct> type() { return TYPE; }
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

	/** Where a party member is, for the maps. */
	public record PartySpot(java.util.UUID id, double x, double y, double z, String dim) {
		static final StreamCodec<ByteBuf, PartySpot> STREAM = StreamCodec.composite(net.minecraft.core.UUIDUtil.STREAM_CODEC, PartySpot::id, ByteBufCodecs.DOUBLE, PartySpot::x, ByteBufCodecs.DOUBLE, PartySpot::y,
				ByteBufCodecs.DOUBLE, PartySpot::z, ByteBufCodecs.STRING_UTF8, PartySpot::dim, PartySpot::new);
	}

	public record PartySpots(List<PartySpot> spots) implements CustomPacketPayload {
		public static final Type<PartySpots> TYPE = id("party_spots");
		public static final StreamCodec<ByteBuf, PartySpots> CODEC = StreamCodec.composite(PartySpot.STREAM.apply(ByteBufCodecs.list()), PartySpots::spots, PartySpots::new);
		@Override public Type<PartySpots> type() { return TYPE; }
	}

	/** The scroll wheel: look there. */
	public record Ping(double x, double y, double z) implements CustomPacketPayload {
		public static final Type<Ping> TYPE = id("ping");
		public static final StreamCodec<ByteBuf, Ping> CODEC = StreamCodec.composite(ByteBufCodecs.DOUBLE, Ping::x, ByteBufCodecs.DOUBLE, Ping::y, ByteBufCodecs.DOUBLE, Ping::z, Ping::new);
		@Override public Type<Ping> type() { return TYPE; }
	}

	/** What hangs over the heads round you (Marks): entity ids, and the mark for each. */
	public record NpcMarks(List<Integer> ids, List<Integer> marks) implements CustomPacketPayload {
		public static final Type<NpcMarks> TYPE = id("npc_marks");
		public static final StreamCodec<ByteBuf, NpcMarks> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT.apply(ByteBufCodecs.list()), NpcMarks::ids,
				ByteBufCodecs.VAR_INT.apply(ByteBufCodecs.list()), NpcMarks::marks, NpcMarks::new);
		@Override public Type<NpcMarks> type() { return TYPE; }
	}

	public record PingAt(String who, double x, double y, double z) implements CustomPacketPayload {
		public static final Type<PingAt> TYPE = id("ping_at");
		public static final StreamCodec<ByteBuf, PingAt> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, PingAt::who, ByteBufCodecs.DOUBLE, PingAt::x, ByteBufCodecs.DOUBLE, PingAt::y, ByteBufCodecs.DOUBLE, PingAt::z, PingAt::new);
		@Override public Type<PingAt> type() { return TYPE; }
	}

	/** Someone on the Party screen. */
	public record PartyCard(String name, int role, int rank, boolean online) {
		public static final int MEMBER = 0, COMMANDER = 1, LEADER = 2;
		static final StreamCodec<ByteBuf, PartyCard> STREAM = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, PartyCard::name, ByteBufCodecs.VAR_INT, PartyCard::role, ByteBufCodecs.VAR_INT, PartyCard::rank, ByteBufCodecs.BOOL, PartyCard::online, PartyCard::new);
	}

	/** What the Party screen shows: everyone including you, the party's rank (yours alone), the bank and its last lines, and who's invited you. */
	public record PartyBoard(List<PartyCard> cards, int rank, int bank, List<String> ledger, String invitedBy) implements CustomPacketPayload {
		public static final Type<PartyBoard> TYPE = id("party_board");
		public static final StreamCodec<ByteBuf, PartyBoard> CODEC = StreamCodec.composite(PartyCard.STREAM.apply(ByteBufCodecs.list()), PartyBoard::cards, ByteBufCodecs.VAR_INT, PartyBoard::rank, ByteBufCodecs.VAR_INT, PartyBoard::bank,
				ByteBufCodecs.STRING_UTF8.apply(ByteBufCodecs.list()), PartyBoard::ledger, ByteBufCodecs.STRING_UTF8, PartyBoard::invitedBy, PartyBoard::new);
		@Override public Type<PartyBoard> type() { return TYPE; }
	}

	/** A press on the Party screen. The server checks every one against who you are. */
	public record PartyAct(int what, String who, int coins) implements CustomPacketPayload {
		public static final int SHOW = 0, INVITE = 1, ACCEPT = 2, DECLINE = 3, LEAVE = 4, KICK = 5, COMMANDER = 6, LEAD = 7, PUT_IN = 8, TAKE_OUT = 9;
		public static final Type<PartyAct> TYPE = id("party_act");
		public static final StreamCodec<ByteBuf, PartyAct> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, PartyAct::what, ByteBufCodecs.STRING_UTF8, PartyAct::who, ByteBufCodecs.VAR_INT, PartyAct::coins, PartyAct::new);
		@Override public Type<PartyAct> type() { return TYPE; }
	}

	public record PartySync(List<PartyMember> members) implements CustomPacketPayload {
		public static final Type<PartySync> TYPE = id("party_sync");
		public static final StreamCodec<ByteBuf, PartySync> CODEC = StreamCodec.composite(PartyMember.STREAM.apply(ByteBufCodecs.list()), PartySync::members, PartySync::new);
		@Override public Type<PartySync> type() { return TYPE; }
	}

	public record SpellFx(int kind, String gate, org.joml.Vector3f at, float r, int on, int by) implements CustomPacketPayload {
		public static final Type<SpellFx> TYPE = id("spell_fx");
		public static final StreamCodec<ByteBuf, SpellFx> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, SpellFx::kind, ByteBufCodecs.STRING_UTF8, SpellFx::gate, ByteBufCodecs.VECTOR3F, SpellFx::at,
				ByteBufCodecs.FLOAT, SpellFx::r, ByteBufCodecs.VAR_INT, SpellFx::on, ByteBufCodecs.VAR_INT, SpellFx::by, SpellFx::new);
		@Override public Type<SpellFx> type() { return TYPE; }
	}

	public record GuildJob(String id, String title, String text, int x, int z, boolean has) {
		static final StreamCodec<ByteBuf, GuildJob> STREAM = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, GuildJob::id, ByteBufCodecs.STRING_UTF8, GuildJob::title, ByteBufCodecs.STRING_UTF8, GuildJob::text,
				ByteBufCodecs.VAR_INT, GuildJob::x, ByteBufCodecs.VAR_INT, GuildJob::z, ByteBufCodecs.BOOL, GuildJob::has, GuildJob::new);
	}

	/** @param taken the ids on your card: the rest are only on the board */
	public record GuildJobs(List<GuildJob> jobs, List<String> taken) implements CustomPacketPayload {
		public static final Type<GuildJobs> TYPE = id("guild_jobs");
		public static final StreamCodec<ByteBuf, GuildJobs> CODEC = StreamCodec.composite(GuildJob.STREAM.apply(ByteBufCodecs.list()), GuildJobs::jobs,
				ByteBufCodecs.STRING_UTF8.apply(ByteBufCodecs.list()), GuildJobs::taken, GuildJobs::new);
		@Override public Type<GuildJobs> type() { return TYPE; }
	}

	public record QuestTrack(String title, int x, int z, boolean has) {
		static final StreamCodec<ByteBuf, QuestTrack> STREAM = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, QuestTrack::title, ByteBufCodecs.VAR_INT, QuestTrack::x,
				ByteBufCodecs.VAR_INT, QuestTrack::z, ByteBufCodecs.BOOL, QuestTrack::has, QuestTrack::new);
	}

	/** Every quest being followed, for the compass. */
	public record QuestTracks(List<QuestTrack> all) implements CustomPacketPayload {
		public static final Type<QuestTracks> TYPE = id("quest_tracks");
		public static final StreamCodec<ByteBuf, QuestTracks> CODEC = StreamCodec.composite(QuestTrack.STREAM.apply(ByteBufCodecs.list()), QuestTracks::all, QuestTracks::new);
		@Override public Type<QuestTracks> type() { return TYPE; }
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

	public record ForgeCraft(BlockPos pos, Job job, int embers) implements CustomPacketPayload {
		public static final Type<ForgeCraft> TYPE = id("forge_craft");
		public static final StreamCodec<ByteBuf, ForgeCraft> CODEC = StreamCodec.composite(BlockPos.STREAM_CODEC, ForgeCraft::pos, Job.CODEC, ForgeCraft::job, ByteBufCodecs.VAR_INT, ForgeCraft::embers, ForgeCraft::new);
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
	public static Consumer<QuestTracks> onQuestTrack = m -> {};
	public static Consumer<GuildJobs> onGuildJobs = m -> {};
	public static Consumer<SpellFx> onSpellFx = m -> {};
	public static List<PartyMember> clientParty = List.of();
	public static PartyBoard clientBoard = new PartyBoard(List.of(), 0, 0, List.of(), "");
	public static BagLines clientBag = new BagLines(List.of(), 1);
	public static PetList clientPets = new PetList(List.of(), "");
	public static volatile List<PartySpot> clientSpots = List.of();
	public static Consumer<PingAt> onPing = m -> {};
	public static Consumer<NpcMarks> onNpcMarks = m -> {};
	public static Consumer<ForgeEcho> onForgeEcho = m -> {};
	public static Consumer<QuestBoard> onBoard = m -> {};
	public static Consumer<PosterView> onPoster = m -> {};
	public static Runnable onCard = () -> {};
	public static Runnable onPhotos = () -> {};
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
			r.playToClient(HitNumber.TYPE, HitNumber.CODEC, (m, ctx) -> onHitNumber.accept(m));
			r.playToClient(Meter.TYPE, Meter.CODEC, (m, ctx) -> {
				clientMeter = m;
				clientMeterAt = System.currentTimeMillis();
			});
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
			r.playToClient(QuestTracks.TYPE, QuestTracks.CODEC, (m, ctx) -> onQuestTrack.accept(m));
			r.playToClient(GuildJobs.TYPE, GuildJobs.CODEC, (m, ctx) -> onGuildJobs.accept(m));
			r.playToClient(SpellFx.TYPE, SpellFx.CODEC, (m, ctx) -> onSpellFx.accept(m));
			r.playToClient(PartySync.TYPE, PartySync.CODEC, (m, ctx) -> clientParty = m.members());
			r.playToClient(PartyBoard.TYPE, PartyBoard.CODEC, (m, ctx) -> clientBoard = m);
			r.playToClient(PartySpots.TYPE, PartySpots.CODEC, (m, ctx) -> clientSpots = m.spots());
			r.playToClient(PingAt.TYPE, PingAt.CODEC, (m, ctx) -> onPing.accept(m));
			r.playToClient(NpcMarks.TYPE, NpcMarks.CODEC, (m, ctx) -> onNpcMarks.accept(m));
			r.playToServer(Ping.TYPE, Ping.CODEC, (m, ctx) -> Party.ping((ServerPlayer) ctx.player(), m));
			r.playToServer(JournalPick.TYPE, JournalPick.CODEC, (m, ctx) -> Story.pick((ServerPlayer) ctx.player(), m.key()));
			r.playToServer(ForgeRelay.TYPE, ForgeRelay.CODEC, (m, ctx) -> Smithing.onRelay(m, (ServerPlayer) ctx.player()));
			r.playToClient(ForgeEcho.TYPE, ForgeEcho.CODEC, (m, ctx) -> onForgeEcho.accept(m));
			r.playToServer(ForgeDone.TYPE, ForgeDone.CODEC, (m, ctx) -> Smithing.onDone(m, (ServerPlayer) ctx.player()));
			r.playToClient(RelicCd.TYPE, RelicCd.CODEC, (m, ctx) -> {
				relicCdTotal = m.ticks() * 50L;
				relicCdEnd = System.currentTimeMillis() + relicCdTotal;
			});
			r.playToServer(CurioKey.TYPE, CurioKey.CODEC, (m, ctx) -> Spells.as(ctx.player(), () -> {
				if (m.what() == JOINED_SKILL) Skills.use((ServerPlayer) ctx.player(), 0);
				else if (m.what() == MOUNT) Mounts.toggle((ServerPlayer) ctx.player());
				else if (m.what() == FORM) Forms.key((ServerPlayer) ctx.player());
				else CurioFx.key((ServerPlayer) ctx.player(), m.what());
			}));
			r.playToServer(PouchUse.TYPE, PouchUse.CODEC, (m, ctx) -> BeltPouch.use((ServerPlayer) ctx.player(), m.slot()));
			r.playToClient(ClassState.TYPE, ClassState.CODEC, (m, ctx) -> {
				Classes.client = m.key();
				if (m.key().isEmpty()) onClassAsk.run();
			});
			r.playToClient(MountState.TYPE, MountState.CODEC, (m, ctx) -> {
				Mounts.client = m.key();
				if (m.key().isEmpty()) onMountAsk.run();
			});
			r.playToServer(MountPick.TYPE, MountPick.CODEC, (m, ctx) -> Mounts.pick((ServerPlayer) ctx.player(), m.key()));
			r.playToServer(MountUp.TYPE, MountUp.CODEC, (m, ctx) -> Mounts.upgrade((ServerPlayer) ctx.player(), m.track()));
			r.playToClient(MountRanks.TYPE, MountRanks.CODEC, (m, ctx) -> {
				for (int i = 0; i < Mounts.clientRanks.length && i < m.ranks().size(); i++) Mounts.clientRanks[i] = m.ranks().get(i);
			});
			r.playToServer(InvTidy.TYPE, InvTidy.CODEC, (m, ctx) -> Tidy.act((ServerPlayer) ctx.player(), m.what()));
			r.playToServer(PartyAct.TYPE, PartyAct.CODEC, (m, ctx) -> Party.act((ServerPlayer) ctx.player(), m));
			r.playToServer(BagAct.TYPE, BagAct.CODEC, (m, ctx) -> Bag.act((ServerPlayer) ctx.player(), m));
			r.playToClient(BagLines.TYPE, BagLines.CODEC, (m, ctx) -> clientBag = m);
			r.playToServer(PetAct.TYPE, PetAct.CODEC, (m, ctx) -> Pets.act((ServerPlayer) ctx.player(), m.pet()));
			r.playToClient(TradeState.TYPE, TradeState.CODEC, (m, ctx) -> Trades.client = m.state());
			r.playToServer(TradeAct.TYPE, TradeAct.CODEC, (m, ctx) -> Trades.act((ServerPlayer) ctx.player(), m));
			r.playToClient(KitchenState.TYPE, KitchenState.CODEC, (m, ctx) -> {
				clientKitchen = m;
				clientKitchenAt = ctx.player().level().getGameTime();
			});
			r.playToClient(PetList.TYPE, PetList.CODEC, (m, ctx) -> clientPets = m);
			r.playToClient(PosterView.TYPE, PosterView.CODEC, (m, ctx) -> onPoster.accept(m));
			r.playToClient(ArenaCheer.TYPE, ArenaCheer.CODEC, (m, ctx) -> onCheer.accept(m));
			r.playToClient(AshfallSync.TYPE, AshfallSync.CODEC, (m, ctx) -> {
				Ashfall.client = m.on();
				Ashfall.clientSince = m.since();
			});
			r.playToServer(PosterAct.TYPE, PosterAct.CODEC, (m, ctx) -> Bounties.act((ServerPlayer) ctx.player(), m.entity()));
			r.playToServer(TomeRead.TYPE, TomeRead.CODEC, (m, ctx) -> Books.confirm((ServerPlayer) ctx.player(), m.form()));
			r.playToClient(BookOffer.TYPE, BookOffer.CODEC, (m, ctx) -> Books.onOffer.accept(m));
			r.playToServer(BookSwap.TYPE, BookSwap.CODEC, (m, ctx) -> Books.swap((ServerPlayer) ctx.player(), m.give()));
			r.playToClient(FormState.TYPE, FormState.CODEC, (m, ctx) -> {
				Forms.clientForm = m.form();
				Forms.clientReady = m.ready();
				Forms.clientUntil = System.currentTimeMillis() + m.left() * 50L;
				Forms.clientRest = System.currentTimeMillis() + m.rest() * 50L;
				Forms.clientHave = m.have();
			});
			r.playToClient(FormAura.TYPE, FormAura.CODEC, (m, ctx) -> onFormAura.accept(m));
			r.playToClient(SkillFx.TYPE, SkillFx.CODEC, (m, ctx) -> onSkillFx.accept(m));
			r.playToClient(HealBeam.TYPE, HealBeam.CODEC, (m, ctx) -> onHealBeam.accept(m));
			r.playToServer(SkillUse.TYPE, SkillUse.CODEC, (m, ctx) -> Spells.as(ctx.player(), () -> Skills.use((ServerPlayer) ctx.player(), m.slot())));
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
