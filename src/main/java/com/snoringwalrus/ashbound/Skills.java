package com.snoringwalrus.ashbound;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.function.Supplier;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.serialization.Codec;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import yesman.epicfight.gameasset.Animations;
import yesman.epicfight.world.capabilities.EpicFightCapabilities;
import yesman.epicfight.world.capabilities.entitypatch.player.ServerPlayerPatch;

/**
 * Each class's two paths and the skills on them. At each of the levels in {@link #UNLOCK} you choose one of the class's
 * two skills for that level, from either path, so the three you end up with are your build ({@link #pick}). A skill comes
 * at rank I; books raise it, teach one early if you've not chosen for its level, and otherwise make you give one up for it
 * for good ({@link #replace}). The bar has four keys: the first is always whatever you're
 * holding (a staff's own skill, a Joined weapon's), the other three are yours to fill on the skills screen
 * (client/SkillScreen). The server holds all of it, down to the cooldowns. SkillArts has the later skills.
 */
public final class Skills {
	private Skills() {}

	public static final int SPEC_LEVEL = 5, MAX_RANK = 5, SLOTS = 4, FIRST_OWN_SLOT = 1;
	/** the level each of a path's skills comes at, in {@link #ALL}'s order */
	public static final int[] UNLOCK = {SPEC_LEVEL, 20, 35};
	/** each rank past the first */
	private static final double PER_RANK = 0.2;
	private static final int SECOND = 20;

	public record Spec(String id, String cls, String name, String blurb) {}

	public interface Act {
		void run(ServerPlayer p, double mult);
	}

	/** Cooldown in seconds. A mage's cost is mana and it needs a staff of its school; anyone else's is stamina. */
	public record Skill(String id, String spec, String name, String blurb, int cooldown, int cost, Act act) {}

	public static final List<Spec> SPECS = List.of(
			new Spec("bulwark", "vanguard", "Bulwark", "Hold the line. Everything that moves hits you and breaks on the shield."),
			new Spec("oathblade", "vanguard", "Oathblade", "Go in first, and the blade pays you back for it."),
			new Spec("quake", "breaker", "Quake", "Hit the ground so hard the whole room falls over."),
			new Spec("executioner", "breaker", "Executioner", "One slow blow, and nothing left to hit twice."),
			new Spec("bloodreaver", "reaver", "Bloodreaver", "Pay in your own blood for damage nobody else can reach."),
			new Spec("tempest", "reaver", "Tempest", "Keep turning. Nothing near you stays standing."),
			new Spec("dragoon", "lancer", "Dragoon", "Up off the ground, then down on top of them."),
			new Spec("phalanx", "lancer", "Phalanx", "One thrust, straight through the whole line."),
			new Spec("assassin", "shade", "Assassin", "Gone from where they're looking, in their back the next moment."),
			new Spec("venom", "shade", "Venom", "A scratch is enough. Then you only have to wait."),
			new Spec("marksman", "hunter", "Marksman", "Take your time. One arrow is all it needs."),
			new Spec("trapper", "hunter", "Trapper", "Pick the ground first and let them walk onto it."),
			new Spec("pyre", "ashcaster", "Pyre", "Set the floor alight and stand well back."),
			new Spec("void", "ashcaster", "Void", "Tear a hole in the air and feed the room to it."),
			new Spec("radiant", "mender", "Radiant", "Nobody dies while you're looking at them."),
			new Spec("warpriest", "mender", "Warpriest", "Your god hits as hard as it heals."),
			new Spec("bonelord", "caller", "Bonelord", "Too many of them to count, and more where those came from."),
			new Spec("soulbinder", "caller", "Soulbinder", "One champion, bound to you, worth a whole host."));

	public static final List<Skill> ALL = List.of(
			new Skill("bastion_slam", "bulwark", "Bastion Slam", "Slam the ground: all near turn on you, and you stand fast.", 14, 4, Skills::bastion),
			new Skill("oath_charge", "oathblade", "Oath Charge", "Charge through the line, healed for what you hit.", 12, 4, Skills::charge),
			new Skill("rift_slam", "quake", "Rift Slam", "A shockwave that throws everything near into the air.", 16, 5, Skills::rift),
			new Skill("headsmans_drop", "executioner", "Headsman's Drop", "A long wind-up, then one huge blow ahead of you.", 20, 5, Skills::headsman),
			new Skill("blood_price", "bloodreaver", "Blood Price", "Spend a seventh of your health on a burst all round you.", 12, 2, Skills::blood),
			new Skill("steel_tempest", "tempest", "Steel Tempest", "Three spinning sweeps.", 15, 5, Skills::tempest),
			new Skill("skyfall", "dragoon", "Skyfall", "Leap high, and crash down in a ring.", 14, 4, Skills::skyfall),
			new Skill("spear_wall", "phalanx", "Spear Wall", "A long thrust through everything in line.", 12, 4, Skills::spearWall),
			new Skill("vanish", "assassin", "Vanish", "Vanish, and strike twice from behind what you're looking at.", 16, 3, Skills::vanish),
			new Skill("viper_bite", "venom", "Viper Bite", "A quick cut ahead that poisons everything it touches.", 10, 3, Skills::viper),
			new Skill("deadeye", "marksman", "Deadeye", "One perfect arrow, worth a volley.", 16, 3, Skills::deadeye),
			new Skill("snare_field", "trapper", "Snare Field", "Pins everything where you aim for a few seconds.", 14, 3, Skills::snare),
			new Skill("cinder_field", "pyre", "Cinder Field", "The ground where you aim burns for a while.", 14, 30, Skills::cinder),
			new Skill("black_hole", "void", "Black Hole", "Pulls all near where you aim together, then bursts.", 18, 34, Skills::hole),
			new Skill("mass_renewal", "radiant", "Mass Renewal", "A great heal for everyone near.", 30, 60, Skills::renewal),
			new Skill("judgement", "warpriest", "Judgement", "Smites what you're looking at and mends your party.", 16, 45, Skills::judgement),
			new Skill("bone_horde", "bonelord", "Bone Horde", "Your whole host at once.", 60, 90, Skills::horde),
			new Skill("bound_champion", "soulbinder", "Bound Champion", "Calls one thrall of far greater strength.", 60, 90, Skills::champion),
			new Skill("shield_wall", "bulwark", "Shield Wall", "A dome of light: all near take far less for a while.", 24, 5, SkillArts::shieldWall),
			new Skill("unbroken", "bulwark", "Unbroken", "Nothing gets past you for seven seconds. Then you give it all back.", 60, 6, SkillArts::unbroken),
			new Skill("oath_cross", "oathblade", "Crossing Oath", "Two great crossing cuts ahead, each one mending you.", 10, 3, SkillArts::oathCross),
			new Skill("last_oath", "oathblade", "Last Oath", "A blade of light as long as a house. The closer to death, the harder it falls.", 30, 6, SkillArts::lastOath),
			new Skill("fault_line", "quake", "Fault Line", "The ground splits ahead of you and throws up what's on it.", 14, 4, SkillArts::faultLine),
			new Skill("worldbreaker", "quake", "Worldbreaker", "Three blows, each wider than the last.", 36, 7, SkillArts::worldbreaker),
			new Skill("reapers_mark", "executioner", "Reaper's Mark", "Mark what you're looking at: everyone hits it a third harder.", 18, 3, SkillArts::reapersMark),
			new Skill("beheading", "executioner", "Beheading", "One blow. Past a quarter health it's more than double.", 30, 6, SkillArts::beheading),
			new Skill("red_thirst", "bloodreaver", "Red Thirst", "For a while every blow gives you back part of what it did.", 22, 3, SkillArts::redThirst),
			new Skill("crimson_rite", "bloodreaver", "Crimson Rite", "Half your health, spent all at once on everything near.", 40, 3, SkillArts::crimsonRite),
			new Skill("razor_gale", "tempest", "Razor Gale", "Send a wall of blades walking away from you.", 13, 4, SkillArts::razorGale),
			new Skill("eye_of_storm", "tempest", "Eye of the Storm", "Drag everything in and don't stop turning.", 36, 7, SkillArts::eyeOfStorm),
			new Skill("dragon_lunge", "dragoon", "Dragon Lunge", "Go through them, spear first.", 10, 3, SkillArts::dragonLunge),
			new Skill("dragons_descent", "dragoon", "Dragon's Descent", "Up out of sight, and down on the spot you pick.", 32, 6, SkillArts::dragonsDescent),
			new Skill("spear_hedge", "phalanx", "Spear Hedge", "Spears burst up in a line ahead and hold what they catch.", 14, 4, SkillArts::spearHedge),
			new Skill("thousand_thrusts", "phalanx", "Thousand Thrusts", "Too fast to see, and it doesn't stop at the first one.", 28, 6, SkillArts::thousandThrusts),
			new Skill("smoke_step", "assassin", "Smoke Step", "Gone where you're looking, leaving the ones behind you choking.", 10, 3, SkillArts::smokeStep),
			new Skill("death_blossom", "assassin", "Death Blossom", "Behind five of them, one after another, before the first has fallen.", 30, 5, SkillArts::deathBlossom),
			new Skill("toxic_cloud", "venom", "Toxic Cloud", "A cloud that hangs where you aim and poisons what breathes it.", 16, 3, SkillArts::toxicCloud),
			new Skill("plague_bloom", "venom", "Plague Bloom", "Everything poisoned near you bursts, and spreads it.", 30, 4, SkillArts::plagueBloom),
			new Skill("arrow_rain", "marksman", "Arrow Rain", "Three waves out of the sky on the spot you aim at.", 18, 4, SkillArts::arrowRain),
			new Skill("piercing_star", "marksman", "Piercing Star", "Draw for a breath, then a line of light through everything.", 32, 5, SkillArts::piercingStar),
			new Skill("spike_pit", "trapper", "Spike Pit", "Stakes burst up three times where you aim.", 14, 3, SkillArts::spikePit),
			new Skill("killing_ground", "trapper", "Killing Ground", "All who stand in it are slowed and everyone hits them harder.", 34, 5, SkillArts::killingGround),
			new Skill("flame_lance", "pyre", "Flame Lance", "A line of fire through everything ahead.", 10, 16, SkillArts::flameLance),
			new Skill("meteor", "pyre", "Meteor", "It comes down where you aim. Don't be there.", 30, 60, SkillArts::meteor),
			new Skill("void_lances", "void", "Void Lances", "Black spears out of the floor where you aim.", 12, 16, SkillArts::voidLances),
			new Skill("event_horizon", "void", "Event Horizon", "A hole in the world that eats the room for three seconds, then bursts.", 32, 70, SkillArts::eventHorizon),
			new Skill("sanctify", "radiant", "Sanctify", "The ground you stand on heals everyone on it.", 24, 40, SkillArts::sanctify),
			new Skill("second_dawn", "radiant", "Second Dawn", "Everyone near, whole again, clean again, and untouchable for a moment.", 90, 90, SkillArts::secondDawn),
			new Skill("holy_lance", "warpriest", "Holy Lance", "A spear of light straight ahead that mends you a little.", 10, 30, SkillArts::holyLance),
			new Skill("heavens_wrath", "warpriest", "Heaven's Wrath", "Light rains down on the spot you aim at, then your party's mended.", 36, 70, SkillArts::heavensWrath),
			new Skill("marrow_burst", "bonelord", "Marrow Burst", "Each of your thralls blasts everything round it.", 16, 30, SkillArts::marrowBurst),
			new Skill("legion", "bonelord", "Legion", "Six at once, all you can hold together.", 90, 95, SkillArts::legion),
			new Skill("soul_mend", "soulbinder", "Soul Mend", "Your thralls are healed and hit harder for a while.", 20, 40, SkillArts::soulMend),
			new Skill("ascended", "soulbinder", "Ascended", "Your champion grows, hits twice as hard, and is whole again.", 60, 80, SkillArts::ascended));

	/** spec (the path of your first skill), picks (a bit for each level you've chosen on), rank.SKILL, slot.N, lost.SKILL for what you gave up */
	public static final Supplier<AttachmentType<Map<String, String>>> STATE = Coins.ATTACHMENTS.register("skills",
			() -> AttachmentType.<Map<String, String>>builder(() -> new HashMap<>()).serialize(Codec.unboundedMap(Codec.STRING, Codec.STRING)).copyOnDeath().build());

	/** Who's been marked, and until when: anyone's blows land harder on them. */
	private static final Map<LivingEntity, Long> MARKED = new java.util.WeakHashMap<>();
	private static final float MARK_HURTS = 1.33f, THIRST = 0.15f;

	/** When each skill of each player is next ready, by game time. */
	private static final Map<UUID, Map<String, Long>> READY = new HashMap<>();
	private static final String HELD = "held", BUFF = "buff.";

	// your own, on your own screen
	public static String clientSpec = "";
	public static int clientPicks;
	public static Map<String, Integer> clientRanks = Map.of();
	public static String[] clientBar = new String[SLOTS];
	/** millis it's ready at, and how long it took */
	public static final Map<String, long[]> clientCooling = new HashMap<>();

	public static void register() {
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedInEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer p) {
				settle(p);
				remind(p);
				sync(p);
			}
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedOutEvent e) -> READY.remove(e.getEntity().getUUID()));
		NeoForge.EVENT_BUS.addListener((net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent e) -> {
			Long until = MARKED.get(e.getEntity());
			if (until != null && e.getEntity().level().getGameTime() < until && e.getSource().getEntity() instanceof Player) e.setAmount(e.getAmount() * MARK_HURTS);
		});
		NeoForge.EVENT_BUS.addListener(Skills::commands);
		NeoForge.EVENT_BUS.addListener((net.neoforged.neoforge.event.entity.living.LivingDamageEvent.Post e) -> {
			if (e.getSource().getDirectEntity() instanceof ServerPlayer p && e.getNewDamage() > 0) {
				float heavy = Math.min(1, e.getNewDamage() / Math.max(1, JoinedSkills.strength(p) * 2));
					Spells.skillFx(p.serverLevel(), "hit", e.getEntity().getBoundingBox().getCenter(), Vec3.ZERO, heavy, null);
					HitStop.strike(p.serverLevel(), p, e.getEntity(), heavy);
				if (left(p, BUFF + "thirst") > 0) p.heal(e.getNewDamage() * THIRST);
			}
		});
	}

	private static final com.mojang.brigadier.suggestion.SuggestionProvider<net.minecraft.commands.CommandSourceStack> SKILL_IDS = (c, b) ->
			net.minecraft.commands.SharedSuggestionProvider.suggest(ALL.stream().map(Skill::id), b);

	private static void commands(RegisterCommandsEvent e) {
		e.getDispatcher().register(Commands.literal("ashbound").requires(s -> s.hasPermission(2)).then(Commands.literal("skill")
				.then(Commands.literal("reset").then(Commands.argument("player", EntityArgument.player()).executes(c -> {
					ServerPlayer p = EntityArgument.getPlayer(c, "player");
					p.setData(STATE, new HashMap<>());
					sync(p);
					return 1;
				})))
				.then(Commands.literal("spec").then(Commands.argument("player", EntityArgument.player()).then(Commands.argument("id", StringArgumentType.word()).executes(c -> {
					ServerPlayer p = EntityArgument.getPlayer(c, "player");
					Spec s = spec(StringArgumentType.getString(c, "id"));
					if (s == null) return 0;
					put(p, "spec", s.id());
					teach(p, of(s).id(), 1);
					return 1;
				}))))
				.then(Commands.literal("book").then(Commands.argument("player", EntityArgument.player()).then(Commands.argument("rank", IntegerArgumentType.integer(1, MAX_RANK)).executes(c -> {
					ServerPlayer p = EntityArgument.getPlayer(c, "player");
					Spec s = spec(p);
					if (s == null) return 0;
					p.getInventory().add(Books.book(IntegerArgumentType.getInteger(c, "rank"), of(s).id()));
					return 1;
				}).then(Commands.argument("id", StringArgumentType.word()).suggests(SKILL_IDS).executes(c -> {
					ServerPlayer p = EntityArgument.getPlayer(c, "player");
					Skill k = byId(StringArgumentType.getString(c, "id"));
					if (k == null) return 0;
					p.getInventory().add(Books.book(IntegerArgumentType.getInteger(c, "rank"), k.id()));
					return 1;
				})))))
				.then(Commands.literal("learn").then(Commands.argument("player", EntityArgument.player()).then(Commands.argument("id", StringArgumentType.word()).suggests(SKILL_IDS).executes(c -> {
					ServerPlayer p = EntityArgument.getPlayer(c, "player");
					Skill k = byId(StringArgumentType.getString(c, "id"));
					if (k == null) return 0;
					teach(p, k.id(), 1);
					return 1;
				}))))
				.then(Commands.literal("try").then(Commands.argument("id", StringArgumentType.word()).suggests(SKILL_IDS).executes(c -> {
					Skill k = byId(StringArgumentType.getString(c, "id"));
					if (k == null) return 0;
					k.act().run(c.getSource().getPlayerOrException(), 1);
					return 1;
				})))
				.then(Commands.literal("rank").then(Commands.argument("player", EntityArgument.player()).then(Commands.argument("rank", IntegerArgumentType.integer(1, MAX_RANK)).executes(c -> {
					ServerPlayer p = EntityArgument.getPlayer(c, "player");
					Spec s = spec(p);
					if (s == null) return 0;
					teach(p, of(s).id(), IntegerArgumentType.getInteger(c, "rank"));
					return 1;
				}))))));
	}

	public static Spec spec(String id) {
		for (Spec s : SPECS) if (s.id().equals(id)) return s;
		return null;
	}

	public static Spec spec(Player p) {
		return spec(p.getData(STATE).getOrDefault("spec", ""));
	}

	public static Skill byId(String id) {
		for (Skill s : ALL) if (s.id().equals(id)) return s;
		return null;
	}

	/** A path's skills, first to last. */
	public static List<Skill> path(String spec) {
		return ALL.stream().filter(k -> k.spec().equals(spec)).toList();
	}

	/** A specialization's first skill. */
	public static Skill of(Spec s) {
		return path(s.id()).get(0);
	}

	/** Which of the levels a skill belongs to: 0, 1 or 2. */
	public static int tier(Skill k) {
		return path(k.spec()).indexOf(k);
	}

	/** The level a skill comes at. */
	public static int unlock(Skill k) {
		return UNLOCK[tier(k)];
	}

	/** What a class chooses between on a level: one from each path. */
	public static List<Skill> choices(String cls, int tier) {
		return specsOf(cls).stream().map(s -> path(s.id()).get(tier)).toList();
	}

	public static int picks(Player p) {
		return Integer.parseInt(p.getData(STATE).getOrDefault("picks", "0"));
	}

	/** The first of the levels you've reached and not chosen on, or -1. */
	public static int pending(int level, int picks) {
		for (int i = 0; i < UNLOCK.length; i++) if (level >= UNLOCK[i] && (picks >> i & 1) == 0) return i;
		return -1;
	}

	/** Every skill of a class, both paths. */
	public static List<Skill> ofClass(String cls) {
		return ALL.stream().filter(k -> spec(k.spec()).cls().equals(cls)).toList();
	}

	public static List<Spec> specsOf(String cls) {
		return SPECS.stream().filter(s -> s.cls().equals(cls)).toList();
	}

	public static int rank(Player p, String skill) {
		String r = p.getData(STATE).get("rank." + skill);
		return r == null ? 0 : Integer.parseInt(r);
	}

	public static String slot(Player p, int slot) {
		return p.getData(STATE).getOrDefault("slot." + slot, "");
	}

	private static void put(ServerPlayer p, String key, String value) {
		Map<String, String> m = new HashMap<>(p.getData(STATE));
		if (value == null) m.remove(key);
		else m.put(key, value);
		p.setData(STATE, m);
	}

	/** At this rank, never down. A skill that's new goes in the first free key. */
	public static void teach(ServerPlayer p, String skill, int rank) {
		boolean known = rank(p, skill) > 0;
		Skill k = byId(skill);
		put(p, "rank." + skill, String.valueOf(Math.min(MAX_RANK, Math.max(rank, rank(p, skill)))));
		put(p, "picks", String.valueOf(picks(p) | 1 << tier(k)));
		if (spec(p) == null) put(p, "spec", k.spec());
		for (int i = FIRST_OWN_SLOT; !known && i < open(p); i++)
			if (slot(p, i).isEmpty()) {
				put(p, "slot." + i, skill);
				break;
			}
		sync(p);
	}

	public static boolean lost(Player p, String skill) {
		return p.getData(STATE).containsKey("lost." + skill);
	}

	/** A save from before the choosing: what you already know is what you chose. */
	static void settle(ServerPlayer p) {
		int picks = picks(p);
		for (Skill k : ALL) if (rank(p, k.id()) > 0 || lost(p, k.id())) picks |= 1 << tier(k);
		if (picks != picks(p)) put(p, "picks", String.valueOf(picks));
	}

	/** A new class: what the old one taught is gone, and its choices with it. */
	static void keepOwn(ServerPlayer p) {
		Classes.Cls c = Classes.of(p);
		if (c == null) return;
		Map<String, String> m = new HashMap<>(p.getData(STATE));
		boolean gone = m.entrySet().removeIf(e -> {
			Skill k = byId(e.getKey().startsWith("slot.") ? e.getValue() : e.getKey().substring(e.getKey().indexOf('.') + 1));
			return k != null && !spec(k.spec()).cls().equals(c.id());
		});
		Spec s = spec(m.getOrDefault("spec", ""));
		if (s != null && !s.cls().equals(c.id())) gone = true;
		if (!gone) return;
		m.remove("spec");
		m.remove("picks");
		p.setData(STATE, m);
		settle(p);
		for (Skill k : ALL) if (rank(p, k.id()) > 0 && spec(p) == null) put(p, "spec", k.spec());
		sync(p);
	}

	/** Says so when your level has earned a choice you've not made. */
	static void remind(ServerPlayer p) {
		if (Classes.of(p) == null || pending(Levels.level(p), picks(p)) < 0) return;
		p.sendSystemMessage(Component.literal("A new skill to choose: press ").withStyle(ChatFormatting.GOLD)
				.append(Component.keybind("key.ashbound.skills").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD)));
	}

	/** A book of a skill you don't have: one you know goes for good, and this comes in its place, on its key. */
	public static void replace(ServerPlayer p, String give, String take, int rank) {
		int key = -1;
		for (int i = FIRST_OWN_SLOT; i < SLOTS; i++) if (slot(p, i).equals(give)) key = i;
		put(p, "rank." + give, null);
		put(p, "lost." + give, "1");
		put(p, "lost." + take, null);
		if (key >= 0) put(p, "slot." + key, take);
		put(p, "rank." + take, String.valueOf(Math.min(MAX_RANK, rank)));
		sync(p);
	}

	/** How many keys you have: a Tome takes the last. */
	public static int open(Player p) {
		return p.getData(STATE).containsKey("form") ? SLOTS - 1 : SLOTS;
	}

	/** The Tome you've read, and the key it costs. */
	static void setForm(ServerPlayer p, String form) {
		put(p, "form", form);
		put(p, "slot." + (SLOTS - 1), null);
		sync(p);
	}

	/** One of your class's two for the first level you've reached and not chosen on; either path's, and for good. */
	public static void pick(ServerPlayer p, String id) {
		Skill k = byId(id);
		Classes.Cls c = Classes.of(p);
		if (k == null || c == null || !spec(k.spec()).cls().equals(c.id()) || tier(k) != pending(Levels.level(p), picks(p))) return;
		teach(p, k.id(), 1);
		p.serverLevel().playSound(null, p.blockPosition(), SoundEvents.ENCHANTMENT_TABLE_USE, SoundSource.PLAYERS, 1f, 0.8f);
	}

	/** Puts a skill you know on one of your keys, off any other it was on; empty clears the key. */
	public static void assign(ServerPlayer p, int slot, String id) {
		if (slot < FIRST_OWN_SLOT || slot >= open(p) || !id.isEmpty() && rank(p, id) <= 0) return;
		for (int i = FIRST_OWN_SLOT; i < SLOTS; i++) if (slot(p, i).equals(id)) put(p, "slot." + i, null);
		put(p, "slot." + slot, id.isEmpty() ? null : id);
		sync(p);
	}

	public static void sync(ServerPlayer p) {
		Map<String, String> m = p.getData(STATE);
		List<String> known = ALL.stream().filter(s -> rank(p, s.id()) > 0 || lost(p, s.id())).map(s -> s.id() + "=" + rank(p, s.id())).toList();
		List<String> bar = java.util.stream.IntStream.range(0, SLOTS).mapToObj(i -> slot(p, i)).toList();
		PacketDistributor.sendToPlayer(p, new Net.SkillState(m.getOrDefault("spec", ""), known, bar, picks(p)));
		Forms.sync(p);
	}

	private static long left(ServerPlayer p, String key) {
		return READY.getOrDefault(p.getUUID(), Map.of()).getOrDefault(key, 0L) - p.level().getGameTime();
	}

	private static void cool(ServerPlayer p, String key, int ticks) {
		READY.computeIfAbsent(p.getUUID(), u -> new HashMap<>()).put(key, p.level().getGameTime() + ticks);
		PacketDistributor.sendToPlayer(p, new Net.SkillCool(key, ticks));
	}

	/** A skill's lasting effect, looked at by {@link #left}. */
	static void buff(ServerPlayer p, String id, int ticks) {
		READY.computeIfAbsent(p.getUUID(), u -> new HashMap<>()).put(BUFF + id, p.level().getGameTime() + ticks);
	}

	static void mark(LivingEntity e, int ticks) {
		MARKED.put(e, e.level().getGameTime() + ticks);
	}

	static void say(ServerPlayer p, String what) {
		p.displayClientMessage(Component.literal(what).withStyle(ChatFormatting.GRAY), true);
	}

	/** The school a mage's skills need a staff of, or null for those who need none. */
	private static String school(Skill s) {
		return switch (spec(s.spec()).cls()) {
			case "ashcaster" -> "black";
			case "mender" -> "white";
			case "caller" -> "summon";
			default -> null;
		};
	}

	/** Pays for it, or says why not. */
	private static boolean pay(ServerPlayer p, Skill s) {
		String school = school(s);
		if (school == null) {
			ServerPlayerPatch pp = EpicFightCapabilities.getEntityPatch(p, ServerPlayerPatch.class);
			if (pp == null || p.isCreative()) return true;
			if (pp.getStamina() < s.cost()) {
				say(p, "Out of breath");
				return false;
			}
			pp.setStamina(pp.getStamina() - s.cost());
			return true;
		}
		Gear.Weapon w = Spells.held(p);
		if (w == null || !w.kind().equals(school)) {
			say(p, "Needs a " + (school.equals("summon") ? "summoner" : school) + " staff in hand");
			return false;
		}
		if (!Spells.spend(p, s.cost())) {
			say(p, "Not enough mana");
			return false;
		}
		return true;
	}

	public static void use(ServerPlayer p, int slot) {
		if (slot == 0) {
			held(p);
			return;
		}
		Skill s = byId(slot(p, slot));
		if (s == null) {
			say(p, pending(Levels.level(p), picks(p)) >= 0 ? "You've a skill to choose first" : "Nothing on this key");
			return;
		}
		if (left(p, s.id()) > 0 || Passives.titanLocked(p) || !pay(p, s)) return;
		cool(p, s.id(), s.cooldown() * SECOND);
		p.displayClientMessage(Component.literal(s.name()).withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD), true);
		s.act().run(p, 1 + PER_RANK * (rank(p, s.id()) - 1));
	}

	/** The first key: what the thing in your hand does. */
	private static void held(ServerPlayer p) {
		if (Joined.stage(p.getMainHandItem()) > 0 || Joined.stage(p.getOffhandItem()) > 0) {
			JoinedSkills.use(p);
			return;
		}
		Gear.Weapon w = Spells.held(p);
		if (w == null) {
			say(p, "Nothing in your hand has a skill of its own");
			return;
		}
		if (left(p, HELD) > 0 || Passives.titanLocked(p)) return;
		if (!Spells.spend(p, Spells.cost(w.kind()) * HELD_COST)) {
			say(p, "Not enough mana");
			return;
		}
		cool(p, HELD, Spells.heldCooldown(w.kind()) * SECOND);
		p.displayClientMessage(Component.literal(heldName(w.kind())).withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD), true);
		Spells.heldSkill(p, w);
	}

	private static final int HELD_COST = 2;

	public static String heldName(String kind) {
		return switch (kind) {
			case "white" -> "Great Heal";
			case "summon" -> "Greater Host";
			default -> "Braided Bolts";
		};
	}

	// ---------------------------------------------------------------- the skills themselves

	static void look(ServerPlayer p, String id, Vec3 at) {
		Spells.skillFx(p.serverLevel(), id, at, p.getLookAngle(), 0, p);
	}

	static void thud(ServerPlayer p) {
		p.serverLevel().playSound(null, p.blockPosition(), SoundEvents.ANVIL_LAND, SoundSource.PLAYERS, 0.9f, 0.5f);
	}

	static float strength(ServerPlayer p) {
		return JoinedSkills.strength(p);
	}

	static Vec3 aim(ServerPlayer p, double range) {
		return p.pick(range, 0, false).getLocation();
	}

	static List<LivingEntity> near(ServerPlayer p, Vec3 at, double r) {
		return p.serverLevel().getEntitiesOfClass(LivingEntity.class, new AABB(at, at).inflate(r, 3, r),
				e -> e instanceof Enemy && e.isAlive() && e.distanceToSqr(at) <= (r + 1) * (r + 1));
	}

	static void each(ServerPlayer p, Vec3 at, double r, Consumer<LivingEntity> then) {
		near(p, at, r).forEach(then);
	}

	/** What magic hits for: the staff in your hand, as a bolt is. */
	static float magic(ServerPlayer p, double bolts) {
		Gear.Weapon w = Spells.held(p);
		return w == null ? 0 : (float) (20 * bolts * Spells.power(w, p));
	}

	private static void bastion(ServerPlayer p, double m) {
		look(p, "bastion_slam", p.position());
		JoinedSkills.ringHit(p, p.position(), 5, 1.4 * m, 0.3);
		thud(p);
		p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 5 * SECOND, 1));
		for (Mob e : p.serverLevel().getEntitiesOfClass(Mob.class, p.getBoundingBox().inflate(10), x -> x instanceof Enemy && x.isAlive())) Threat.taunt(e, p);
	}

	private static void charge(ServerPlayer p, double m) {
		Vec3 go = p.getLookAngle().multiply(1, 0, 1).normalize();
		JoinedSkills.anim(p, Animations.DANCING_EDGE);
		p.setDeltaMovement(go.scale(1.8).add(0, 0.2, 0));
		p.hurtMarked = true;
		JoinedSkills.later(p, 6, () -> {
			look(p, "oath_charge", p.position().subtract(p.getLookAngle().scale(3)));
			JoinedSkills.lineHit(p, 6, 1.5, 1.8 * m);
			p.heal(p.getMaxHealth() * 0.08f);
		});
	}

	private static void rift(ServerPlayer p, double m) {
		JoinedSkills.anim(p, Animations.THE_GUILLOTINE);
		JoinedSkills.later(p, 14, () -> {
			look(p, "rift_slam", p.position());
			JoinedSkills.ringHit(p, p.position(), 7, 2.6 * m, 0.7);
			thud(p);
		});
	}

	private static void headsman(ServerPlayer p, double m) {
		JoinedSkills.anim(p, Animations.THE_GUILLOTINE);
		look(p, "headsman_rise", p.position());
		JoinedSkills.later(p, 18, () -> {
			look(p, "headsmans_drop", p.position());
			JoinedSkills.lineHit(p, 4, 1.5, 5 * m);
			thud(p);
		});
	}

	private static void blood(ServerPlayer p, double m) {
		p.setHealth(Math.max(1, p.getHealth() - p.getMaxHealth() / 7));
		JoinedSkills.anim(p, Animations.STEEL_WHIRLWIND);
		JoinedSkills.later(p, 8, () -> {
			look(p, "blood_price", p.position());
			JoinedSkills.ringHit(p, p.position(), 5, 3 * m, 0.1);
		});
	}

	private static void tempest(ServerPlayer p, double m) {
		JoinedSkills.anim(p, Animations.STEEL_WHIRLWIND);
		for (int t : new int[] {8, 15, 22})
			JoinedSkills.later(p, t, () -> {
				Spells.skillFx(p.serverLevel(), "steel_tempest", p.position(), p.getLookAngle(), t / 8f, p);
				JoinedSkills.ringHit(p, p.position(), 4.5, 1.3 * m, 0.1);
			});
	}

	private static void skyfall(ServerPlayer p, double m) {
		Vec3 go = p.getLookAngle().multiply(1, 0, 1).normalize();
		look(p, "skyfall_up", p.position());
		p.setDeltaMovement(go.scale(0.7).add(0, 1.15, 0));
		p.hurtMarked = true;
		JoinedSkills.later(p, 12, () -> {
			p.setDeltaMovement(go.scale(0.3).add(0, -1.6, 0));
			p.hurtMarked = true;
		});
		JoinedSkills.later(p, 20, () -> {
			p.resetFallDistance();
			look(p, "skyfall", p.position());
			JoinedSkills.ringHit(p, p.position(), 5, 2.5 * m, 0.4);
			thud(p);
		});
	}

	private static void spearWall(ServerPlayer p, double m) {
		JoinedSkills.anim(p, Animations.GRASPING_SPIRAL_FIRST);
		JoinedSkills.later(p, 6, () -> {
			look(p, "spear_wall", p.position());
			JoinedSkills.lineHit(p, 14, 1.4, 2.6 * m);
		});
	}

	private static void vanish(ServerPlayer p, double m) {
		look(p, "vanish", p.position());
		p.addEffect(new MobEffectInstance(MobEffects.INVISIBILITY, 3 * SECOND, 0, false, false));
		JoinedSkills.twoShadows(p, 1.6 * m);
		look(p, "vanish_cut", p.position());
	}

	private static void viper(ServerPlayer p, double m) {
		JoinedSkills.anim(p, Animations.EVISCERATE_FIRST);
		look(p, "viper_bite", p.position());
		JoinedSkills.lineHit(p, 5, 1.6, 1.2 * m);
		Vec3 ahead = p.position().add(p.getLookAngle().scale(3));
		float sting = strength(p) * 0.2f * (float) m;
		each(p, ahead, 3.5, e -> {
			e.addEffect(new MobEffectInstance(MobEffects.POISON, 6 * SECOND, (int) Math.round((m - 1) / PER_RANK / 2) + 1));
			SkillArts.venom(p, e, sting, 6);
		});
	}

	private static void deadeye(ServerPlayer p, double m) {
		ItemStack bow = p.getMainHandItem().getItem() instanceof BowItem ? p.getMainHandItem() : p.getOffhandItem();
		if (!(bow.getItem() instanceof BowItem)) {
			say(p, "Needs a bow in hand");
			return;
		}
		ServerLevel l = p.serverLevel();
		Arrow a = new Arrow(l, p, new ItemStack(Items.ARROW), bow);
		a.shootFromRotation(p, p.getXRot(), p.getYRot(), 0, 4.5f, 0);
		a.setCritArrow(true);
		a.setBaseDamage(a.getBaseDamage() * 2 * m);
		a.pickup = AbstractArrow.Pickup.DISALLOWED;
		l.addFreshEntity(a);
		look(p, "deadeye", p.position());
		l.playSound(null, p.blockPosition(), SoundEvents.CROSSBOW_SHOOT, SoundSource.PLAYERS, 1.2f, 0.6f);
	}

	private static void snare(ServerPlayer p, double m) {
		Vec3 at = aim(p, 24);
		ServerLevel l = p.serverLevel();
		look(p, "snare_field", at);
		each(p, at, 4, e -> {
			e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, (int) (4 * SECOND * m), 5));
			JoinedSkills.strike(p, e, strength(p) * 1.2f);
		});
		l.playSound(null, at.x, at.y, at.z, SoundEvents.TRIPWIRE_CLICK_ON, SoundSource.PLAYERS, 1.2f, 0.7f);
	}

	private static void cinder(ServerPlayer p, double m) {
		Vec3 at = aim(p, 24);
		ServerLevel l = p.serverLevel();
		float each = magic(p, 0.45 * m);
		for (int t = 0; t < 7; t++)
			JoinedSkills.later(p, t * 15, () -> {
				look(p, "cinder_field", at);
				each(p, at, 4, e -> {
					JoinedSkills.strike(p, e, each);
					e.igniteForSeconds(2);
				});
			});
		l.playSound(null, at.x, at.y, at.z, SoundEvents.FIRECHARGE_USE, SoundSource.PLAYERS, 1.2f, 0.7f);
	}

	private static void hole(ServerPlayer p, double m) {
		Vec3 at = aim(p, 24).add(0, 1, 0);
		ServerLevel l = p.serverLevel();
		float burst = magic(p, 3 * m);
		look(p, "black_hole", at);
		for (int t = 0; t < 8; t++)
			JoinedSkills.later(p, t * 5, () -> {
				each(p, at, 8, e -> {
					Vec3 in = at.subtract(e.position()).normalize().scale(0.38);
					e.setDeltaMovement(in);
					e.hurtMarked = true;
				});
			});
		JoinedSkills.later(p, 42, () -> {
			look(p, "black_hole_burst", at);
			each(p, at, 5, e -> JoinedSkills.strike(p, e, burst));
		});
		l.playSound(null, at.x, at.y, at.z, SoundEvents.ENDERMAN_TELEPORT, SoundSource.PLAYERS, 1.2f, 0.5f);
	}

	private static void renewal(ServerPlayer p, double m) {
		Spells.accordHeal(p, (float) (0.3 * m));
	}

	private static void judgement(ServerPlayer p, double m) {
		Vec3 at = aim(p, 24);
		ServerLevel l = p.serverLevel();
		float hit = magic(p, 2.5 * m);
		look(p, "judgement", at);
		each(p, at, 3, e -> JoinedSkills.strike(p, e, hit));
		for (Player o : l.getEntitiesOfClass(Player.class, p.getBoundingBox().inflate(10))) o.heal(o.getMaxHealth() * (float) (0.1 * m));
		l.playSound(null, at.x, at.y, at.z, SoundEvents.TRIDENT_THUNDER.value(), SoundSource.PLAYERS, 0.7f, 1.4f);
	}

	private static void horde(ServerPlayer p, double m) {
		Spells.host(p, 4, 1.2 * m);
	}

	private static void champion(ServerPlayer p, double m) {
		Spells.host(p, 1, 2.2 * m);
	}
}
