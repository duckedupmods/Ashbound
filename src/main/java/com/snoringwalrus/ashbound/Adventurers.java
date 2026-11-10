package com.snoringwalrus.ashbound;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.brigadier.arguments.StringArgumentType;

import javax.annotation.Nullable;

import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.event.EventHooks;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.OwnableEntity;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.levelgen.Heightmap;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import yesman.epicfight.api.event.EpicFightEventHooks;
import yesman.epicfight.gameasset.Armatures;

/**
 * Adventurers: parties of the guild's other hunters, for life in the world, not story. Each party (/ashbound/adventurers.json,
 * tools/adventurers.py) is a name, a rank, a colour and its members' looks and roles; spawned, they're dressed from the same pools
 * players loot at that rank (the dungeons' Gate Forge sets and weapons, now and then a found set or a world weapon), so their rank
 * reads off their gear. Low ranks wear odd pieces, from C up whole sets; most leave the helmet off so you can see who they are.
 */
public final class Adventurers {
	private Adventurers() {}

	public static final DeferredHolder<EntityType<?>, EntityType<Adventurer>> TYPE = Townsfolk.ENTITIES.register("adventurer",
			() -> EntityType.Builder.of(Adventurer::new, MobCategory.MISC).sized(0.6f, 1.8f).clientTrackingRange(8).build(Ashbound.ID + ":adventurer"));

	/** How far a player can be for them to stay. */
	static final double STAY = 112;

	public record Member(String kind, String name, String role, String race, String sex) {}

	public record Party(String name, char rank, String colour, List<Member> members) {}

	public static final List<Party> PARTIES = load();

	private static List<Party> load() {
		List<Party> out = new ArrayList<>();
		try (InputStream in = Adventurers.class.getResourceAsStream("/ashbound/adventurers.json")) {
			if (in == null) return out;
			for (JsonElement e : JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonArray()) {
				JsonObject o = e.getAsJsonObject();
				List<Member> ms = new ArrayList<>();
				for (JsonElement m : o.getAsJsonArray("members")) {
					JsonObject mo = m.getAsJsonObject();
					ms.add(new Member(mo.get("kind").getAsString(), mo.get("name").getAsString(), mo.get("role").getAsString(), mo.get("race").getAsString(),
							mo.get("sex").getAsString()));
				}
				out.add(new Party(o.get("name").getAsString(), o.get("rank").getAsString().charAt(0), o.get("colour").getAsString(), ms));
			}
		} catch (Exception ex) {
			Ashbound.LOG.error("adventurers not loaded", ex);
		}
		return out;
	}

	// ---------------------------------------------------------------- numbers by rank

	private static final String RANKS = "FEDCBAS";

	private static int r(Adventurer a) {
		return Math.max(0, RANKS.indexOf(a.rank()));
	}

	/** Their health: a bit sturdier than a player at that rank, so they last a fight with a camp. */
	private static final double[] HEALTH = {40, 55, 70, 90, 115, 145, 180};
	private static final float[] ARROW = {3, 4, 5, 6.5f, 8, 10, 12}, BOLT = {4, 5.5f, 7, 9, 11, 13.5f, 16};

	static float arrowDamage(Adventurer a) {
		return ARROW[r(a)];
	}

	static float boltDamage(Adventurer a) {
		return BOLT[r(a)];
	}

	// ---------------------------------------------------------------- what they wear and carry

	/** Armour class and weapon kind by role (the Gate Forge's: heavy, medium, light, robe; sword, twohander, hammer...). */
	private static String cls(String role) {
		return switch (role) {
			case "tank", "breaker" -> "heavy";
			case "striker", "lancer" -> "medium";
			case "ranger", "rogue" -> "light";
			default -> "robe";
		};
	}

	private static String kind(String role, RandomSource rng) {
		return switch (role) {
			case "tank" -> "sword";
			case "breaker" -> "hammer";
			case "striker" -> rng.nextFloat() < 0.6f ? "sword" : "twohander";
			case "lancer" -> "spear";
			case "ranger" -> "bow";
			case "rogue" -> "dagger";
			case "black_mage" -> "black";
			default -> "white";
		};
	}

	/** How a weapon kind is fought (MobMoves' stance names; bows and staffs fight their own way). */
	private static String fights(String kind) {
		return switch (kind) {
			case "twohander" -> "greatsword";
			case "hammer" -> "maul";
			case "spear", "dagger", "bow", "black", "white" -> kind;
			case "summon" -> "black";
			default -> "sword";
		};
	}

	/** The dungeons of a rank, or the nearest rank that has some. */
	static List<Gear.Dungeon> dungeons(char rank) {
		for (int d = 0; d < RANKS.length(); d++)
			for (int s : new int[] {-1, 1}) {
				int i = RANKS.indexOf(rank) + d * s;
				if (i < 0 || i >= RANKS.length()) continue;
				char r = RANKS.charAt(i);
				List<Gear.Dungeon> out = Gear.DUNGEONS.stream().filter(g -> g.rank() == r).toList();
				if (!out.isEmpty()) return out;
			}
		return Gear.DUNGEONS;
	}

	static <T> T any(List<T> l, RandomSource rng) {
		return l.isEmpty() ? null : l.get(rng.nextInt(l.size()));
	}

	private static EquipmentSlot slot(String s) {
		return switch (s) {
			case "helm" -> EquipmentSlot.HEAD;
			case "chest" -> EquipmentSlot.CHEST;
			case "legs" -> EquipmentSlot.LEGS;
			default -> EquipmentSlot.FEET;
		};
	}

	/** A world weapon's chance to be carried in place of a forged one, by rarity (the structure chests' odds, about). */
	private static final Map<WorldArms.Tier, Float> FIND = Map.of(WorldArms.Tier.UNCOMMON, 0.2f, WorldArms.Tier.RARE, 0.08f, WorldArms.Tier.EPIC, 0.03f,
			WorldArms.Tier.LEGENDARY, 0.01f);

	static void dress(Adventurer a, char rank, String role, RandomSource rng) {
		List<Gear.Dungeon> ds = dungeons(rank);
		String cls = cls(role), kind = kind(role, rng);
		// the weapon: their rank's forged one of its kind, a boss weapon now and then, a world weapon by its rarity
		List<Gear.Weapon> pool = ds.stream().flatMap(d -> d.weapons().stream()).filter(x -> x.kind().equals(kind) && !x.boss()).toList();
		if (pool.isEmpty()) pool = Gear.DUNGEONS.stream().flatMap(d -> d.weapons().stream()).filter(x -> x.kind().equals(kind) && !x.boss()).toList();
		Gear.Weapon w = any(pool, rng);
		Gear.Dungeon home = w == null ? any(ds, rng) : Gear.DUNGEONS.stream().filter(d -> d.weapons().contains(w)).findFirst().orElse(any(ds, rng));
		String weapon = w == null ? null : w.id();
		if (rng.nextFloat() < 0.05f) {
			Gear.Weapon b = any(home.bossWeapons().stream().filter(x -> x.kind().equals(kind)).toList(), rng);
			if (b != null) weapon = b.id();
		}
		for (WorldArms.Arm arm : WorldArms.ARMS)
			if (arm.kind().equals(kind) && arm.weapon() != null && arm.weapon().rank() == rank && rng.nextFloat() < FIND.getOrDefault(arm.tier(), 0f) / 4) {
				weapon = arm.id();
				break;
			}
		put(a, EquipmentSlot.MAINHAND, weapon);
		if (role.equals("tank")) {
			Gear.Weapon sh = any(ds.stream().flatMap(d -> d.weapons().stream()).filter(x -> x.kind().equals("shield") && !x.boss()).toList(), rng);
			if (sh != null) put(a, EquipmentSlot.OFFHAND, sh.id());
		}
		a.fights = fights(kind);
		a.gate = home.gate();
		// the armour: whole sets from C up, odd pieces below it; a found set of that rank now and then
		boolean whole = RANKS.indexOf(rank) >= RANKS.indexOf('C');
		List<Gear.Set> sets = new ArrayList<>();
		for (Gear.Dungeon d : ds) for (Gear.Set s : d.sets()) if (s.cls().equals(cls)) sets.add(s);
		Gear.Set set = any(sets, rng);
		WorldArms.Garb found = rng.nextFloat() < 0.15f ? any(WorldArms.GARB.stream().filter(g -> g.rank() == rank && g.cls().equals(cls)).toList(), rng) : null;
		boolean helmet = rng.nextFloat() < 0.3f;
		List<String> slots = List.of("helm", "chest", "legs", "boots");
		for (int i = 0; i < slots.size(); i++) {
			String sl = slots.get(i);
			if (sl.equals("helm") && !helmet) continue;
			if (!whole && !sl.equals("chest") && rng.nextFloat() < 0.25f) continue;      // a low ranker's missing a piece or two
			String id = null;
			// a found set's pieces are listed helm, chest, legs, boots (tools/worldarmour.py)
			if (found != null && found.parts().size() == slots.size()) id = found.id() + "_" + found.parts().get(i);
			if (id == null) {
				Gear.Set from = whole ? set : any(sets, rng);
				if (from != null) id = from.pieces().stream().filter(p -> p.slot().equals(sl)).map(Gear.Piece::id).findFirst().orElse(null);
			}
			put(a, slot(sl), id);
		}
	}

	private static void put(Adventurer a, EquipmentSlot s, String id) {
		if (id == null) return;
		Item it = Gear.item(id);
		if (it == null) return;
		a.setItemSlot(s, new ItemStack(it));
		a.setDropChance(s, 2.0f);       // what they wore, whole, if they fall
	}

	// ---------------------------------------------------------------- spawning

	/** A whole party, round a spot near the ground: dressed before they come into the world, so Epic Fight fits their moves to it. */
	static List<Adventurer> spawn(ServerLevel l, BlockPos near, Party p) {
		return spawn(l, near, p, p.members().size());
	}

	/** Only the first few of them (in town a party's about in twos and threes). In a ring round the spot, so none stands in a camp's fire. */
	static List<Adventurer> spawn(ServerLevel l, BlockPos near, Party p, int most) {
		List<Adventurer> out = new ArrayList<>();
		UUID id = UUID.randomUUID();
		RandomSource rng = l.getRandom();
		// whoever leads walks in front: the shieldbearer if there is one
		List<Member> order = new ArrayList<>(p.members());
		order.sort((x, y) -> Boolean.compare(!x.role().equals("tank"), !y.role().equals("tank")));
		int n = Math.min(most, order.size());
		double turn = rng.nextDouble() * Math.PI * 2;
		String ask = rng.nextFloat() < ASKS ? ASK_KINDS.get(rng.nextInt(ASK_KINDS.size())) : "";
		for (int i = 0; i < n; i++) {
			Member m = order.get(i);
			Adventurer a = TYPE.get().create(l);
			if (a == null) continue;
			a.setUp(m.kind(), m.role(), String.valueOf(p.rank()));
			a.party = id;
			a.slot = i;
			a.leads = i == 0;
			a.partyName = p.name();
			a.ask = ask;
			a.setCustomName(Component.literal(m.name()));
			a.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).setBaseValue(HEALTH[Math.max(0, RANKS.indexOf(p.rank()))]);
			a.setHealth(a.getMaxHealth());
			// a hit staggers anyone; the shieldbearer, who takes them all, shrugs most of it off
			var stun = a.getAttribute(yesman.epicfight.registry.entries.EpicFightAttributes.STUN_ARMOR);
			if (stun != null) stun.setBaseValue(m.role().equals("tank") ? 10 + 2 * RANKS.indexOf(p.rank()) : 2 + RANKS.indexOf(p.rank()) * 0.5);
			dress(a, p.rank(), m.role(), rng);
			double a2 = turn + Math.PI * 2 * i / n;
			BlockPos at = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, near.offset((int) Math.round(Math.cos(a2) * 2.2), 0, (int) Math.round(Math.sin(a2) * 2.2)));
			a.moveTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5, rng.nextFloat() * 360, 0);
			l.addFreshEntity(a);
			out.add(a);
		}
		return out;
	}

	// ---------------------------------------------------------------- meeting them out in the world

	/** Every few minutes out, per party of players (six together meet them as often as one alone does), 60 to 100 blocks off and
	 * out of everyone's sight; never more than a few parties about at once. */
	private static final int FIRST = 1200, EVERY = 3600, MORE = 3600, RETRY = 600, NEAR = 60, FAR = 100, ABOUT = 160, MOST = 3;
	private static final Map<Object, Long> NEXT = new HashMap<>();
	static final List<String> MEETINGS = List.of("roam", "fight", "camp", "gate", "town");

	private static void tick(ServerTickEvent.Post e) {
		MinecraftServer s = e.getServer();
		if (s.getTickCount() % 100 != 0) return;
		ServerLevel l = s.overworld();
		long now = l.getGameTime();
		Map<Object, ServerPlayer> groups = new LinkedHashMap<>();
		for (ServerPlayer p : l.players()) if (!p.isSpectator()) groups.putIfAbsent(com.snoringwalrus.ashbound.Party.fightKey(p), p);
		NEXT.keySet().retainAll(groups.keySet());
		for (var g : groups.entrySet()) {
			Long at = NEXT.get(g.getKey());
			if (at == null) NEXT.put(g.getKey(), now + FIRST + l.random.nextInt(FIRST));
			else if (now >= at) NEXT.put(g.getKey(), now + (meet(l, g.getValue(), null) != null ? EVERY + l.random.nextInt(MORE) : RETRY));
		}
	}

	/** A party of about this player's party's rank, somewhere near them, about something (one of MEETINGS, or what suits the place
	 * and the hour); what happened, or null if there was no room or nowhere to put them. */
	@Nullable
	static String meet(ServerLevel l, ServerPlayer p, @Nullable String what) {
		RandomSource r = l.getRandom();
		java.util.Set<String> here = new java.util.HashSet<>();
		for (Adventurer a : l.getEntitiesOfClass(Adventurer.class, p.getBoundingBox().inflate(ABOUT), a -> a.fallen() == 0)) here.add(a.partyName);
		if (what == null && here.size() >= MOST) return null;
		Capital.Site town = town(p.blockPosition());
		if (what == null) what = town != null ? "town" : pick(l, p, r);
		Party party = choose(Ranks.party(p), here, r);
		if (party == null) return null;
		BlockPos at;
		List<Adventurer> made;
		switch (what) {
			case "town" -> {
				if (town == null) return null;
				int[] c = Waypoints.anchor(town);
				at = out(l, new Vec3(c[0], c[1], c[2]), 4, 36, 20, r);
				if (at == null || town(at) != town) return null;
				made = spawn(l, at, party, 2 + r.nextInt(2));
				for (Adventurer a : made) post(a, at, -1);
			}
			case "gate" -> {
				GateEntity g = l.getEntitiesOfClass(GateEntity.class, p.getBoundingBox().inflate(140)).stream().findAny().orElse(null);
				if (g == null) return null;
				at = out(l, g.position(), 6, 14, 40, r);
				if (at == null) return null;
				made = spawn(l, at, party);
				int stay = 2400 + r.nextInt(2400);
				for (Adventurer a : made) post(a, at, stay);
			}
			case "camp" -> {
				at = wild(l, p, r);
				if (at == null) return null;
				l.setBlock(at, Blocks.CAMPFIRE.defaultBlockState(), 3);
				made = spawn(l, at, party);
				for (Adventurer a : made) {
					a.mode = "camp";
					a.home = at;
				}
			}
			case "fight" -> {
				at = wild(l, p, r);
				if (at == null) return null;
				made = spawn(l, at, party);
				int foes = brawl(l, at, party, made, r);
				if (foes == 0) return null;
			}
			default -> {
				at = wild(l, p, r);
				if (at == null) return null;
				made = spawn(l, at, party);
			}
		}
		if (made.isEmpty()) return null;
		return party.name() + " (" + party.rank() + "), " + made.size() + " of them, " + what + " " + Math.round(Math.sqrt(p.distanceToSqr(Vec3.atCenterOf(at)))) + " blocks off";
	}

	/** What a party out in the wilds is about: round a fire at night, now and then by a gate that's open near you, in a fight, or walking. */
	private static String pick(ServerLevel l, ServerPlayer p, RandomSource r) {
		if (l.isNight() && r.nextFloat() < 0.5f) return "camp";
		if (r.nextFloat() < 0.35f && !l.getEntitiesOfClass(GateEntity.class, p.getBoundingBox().inflate(140)).isEmpty()) return "gate";
		return r.nextFloat() < 0.4f ? "fight" : "roam";
	}

	/** Mostly your own rank, now and then one either side, once in a while two: a party not already about. */
	@Nullable
	static Party choose(int rank, java.util.Set<String> here, RandomSource r) {
		float roll = r.nextFloat();
		int off = roll < 0.6f ? 0 : roll < 0.78f ? -1 : roll < 0.93f ? 1 : r.nextBoolean() ? 2 : -2;
		int want = Math.max(0, Math.min(RANKS.length() - 1, rank + off));
		List<Party> free = PARTIES.stream().filter(x -> !here.contains(x.name())).toList();
		if (free.isEmpty()) return null;
		int best = free.stream().mapToInt(x -> Math.abs(RANKS.indexOf(x.rank()) - want)).min().orElse(0);
		List<Party> pick = free.stream().filter(x -> Math.abs(RANKS.indexOf(x.rank()) - want) == best).toList();
		return pick.get(r.nextInt(pick.size()));
	}

	private static void post(Adventurer a, BlockPos at, int stay) {
		a.mode = "post";
		a.home = at;
		a.stay = stay;
	}

	/** A few of the monsters of a gate of their rank, got out and on them: they're already at it when you come over the hill. */
	private static int brawl(ServerLevel l, BlockPos at, Party party, List<Adventurer> made, RandomSource r) {
		List<Gear.Dungeon> pool = dungeons(party.rank());
		if (pool.isEmpty() || made.isEmpty()) return 0;
		Gear.Dungeon d = any(pool, r);
		int n = Math.max(2, made.size() - 1 + r.nextInt(2)), done = 0;
		for (int k = 0; k < n; k++) {
			var type = BuiltInRegistries.ENTITY_TYPE.getOptional(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, any(d.mobs(), r))).orElse(null);
			if (type == null || !(type.create(l) instanceof Mob m)) continue;
			double a = r.nextDouble() * Math.PI * 2, far = 5 + r.nextDouble() * 4;
			BlockPos top = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, at.offset((int) (Math.cos(a) * far), 0, (int) (Math.sin(a) * far)));
			m.moveTo(top.getX() + 0.5, top.getY(), top.getZ() + 0.5, r.nextFloat() * 360f, 0);
			EventHooks.finalizeMobSpawn(m, l, l.getCurrentDifficultyAt(top), MobSpawnType.EVENT, null);
			if (!l.addFreshEntity(m)) continue;
			Adventurer on = any(made, r);
			m.setTarget(on);
			on.setTarget(m);
			done++;
		}
		return done;
	}

	// ---------------------------------------------------------------- what they ask of you (AdventurerTalk, Errands)

	/** how many parties have a request, and what kinds: a sealed report for the Guild, something from a gate, a camp to clear */
	private static final float ASKS = 0.25f;
	static final List<String> ASK_KINDS = List.of("report", "fetch", "camp");
	/** a camp's monsters carry the party's id under this; they keep to within this of their fire */
	static final String CAMP_TAG = "ashbound_camp";
	private static final int CAMP_NEAR = 35, CAMP_FAR = 60, CAMP_KEEP = 8;

	/** Somewhere for a camp of monsters 35 to 60 blocks off, out of town and out of sight. */
	@Nullable
	static BlockPos campSite(ServerLevel l, Vec3 from, RandomSource r) {
		for (int k = 0; k < 6; k++) {
			BlockPos at = out(l, from, CAMP_NEAR, CAMP_FAR, 24, r);
			if (at != null && town(at) == null) return at;
		}
		return null;
	}

	/** Monsters of a gate of this rank dug in round a fire: they stay put till they're dealt with. How many there are. */
	static int makeCamp(ServerLevel l, BlockPos at, String id, char rank, int n, RandomSource r) {
		Gear.Dungeon d = any(dungeons(rank), r);
		if (d == null) return 0;
		if (l.getBlockState(at).canBeReplaced()) l.setBlock(at, Blocks.CAMPFIRE.defaultBlockState(), 3);
		int done = 0;
		for (int k = 0; k < n; k++) {
			var type = BuiltInRegistries.ENTITY_TYPE.getOptional(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, any(d.mobs(), r))).orElse(null);
			if (type == null || !(type.create(l) instanceof Mob m)) continue;
			double a = Math.PI * 2 * k / n + r.nextDouble() * 0.6, far = 3 + r.nextDouble() * 2.5;
			BlockPos top = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, at.offset((int) Math.round(Math.cos(a) * far), 0, (int) Math.round(Math.sin(a) * far)));
			m.moveTo(top.getX() + 0.5, top.getY(), top.getZ() + 0.5, r.nextFloat() * 360f, 0);
			EventHooks.finalizeMobSpawn(m, l, l.getCurrentDifficultyAt(top), MobSpawnType.EVENT, null);
			m.setPersistenceRequired();
			m.getPersistentData().putString(CAMP_TAG, id);
			if (m instanceof net.minecraft.world.entity.PathfinderMob pm) pm.restrictTo(at, CAMP_KEEP);
			if (l.addFreshEntity(m)) done++;
		}
		return done;
	}

	/** One of a camp has died: if it was the last, its fire goes out and the party who asked stops heading there (and says so). */
	static void campLost(ServerLevel l, String id, Entity dead) {
		boolean more = !l.getEntitiesOfClass(Mob.class, dead.getBoundingBox().inflate(48), m -> m != dead && m.isAlive() && id.equals(m.getPersistentData().getString(CAMP_TAG))).isEmpty();
		if (more) return;
		for (Adventurer a : l.getEntitiesOfClass(Adventurer.class, dead.getBoundingBox().inflate(160), a -> a.party.toString().equals(id))) {
			if (a.task != null && l.getBlockState(a.task).is(Blocks.CAMPFIRE))
				l.setBlock(a.task, l.getBlockState(a.task).setValue(net.minecraft.world.level.block.CampfireBlock.LIT, false), 3);
			a.task = null;
			if (a.leads) a.bark("camp_cleared", null, Map.of(), true);
		}
		BlockPos at = dead.blockPosition();
		for (BlockPos b : BlockPos.betweenClosed(at.offset(-CAMP_KEEP - 2, -3, -CAMP_KEEP - 2), at.offset(CAMP_KEEP + 2, 3, CAMP_KEEP + 2)))
			if (l.getBlockState(b).is(Blocks.CAMPFIRE) && l.getBlockState(b).getValue(net.minecraft.world.level.block.CampfireBlock.LIT)) {
				l.setBlock(b, l.getBlockState(b).setValue(net.minecraft.world.level.block.CampfireBlock.LIT, false), 3);
				break;
			}
	}

	/** Dry open ground 60 to 100 blocks from this player, outside any town, that nobody can see. */
	@Nullable
	private static BlockPos wild(ServerLevel l, ServerPlayer p, RandomSource r) {
		for (int k = 0; k < 4; k++) {
			BlockPos at = out(l, p.position(), NEAR, FAR, 48, r);
			if (at != null && town(at) == null) return at;
		}
		return null;
	}

	/** Somewhere from `near` to `far` round a spot, on dry ground, in a ticking chunk, more than `close` from every player and out of their view. */
	@Nullable
	static BlockPos out(ServerLevel l, Vec3 centre, int near, int far, int close, RandomSource r) {
		for (int k = 0; k < 20; k++) {
			double a = r.nextDouble() * Math.PI * 2, d = near + r.nextDouble() * (far - near);
			BlockPos col = BlockPos.containing(centre.x + Math.cos(a) * d, 0, centre.z + Math.sin(a) * d);
			if (!l.isPositionEntityTicking(col)) continue;
			BlockPos at = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, col);
			if (!l.getFluidState(at).isEmpty() || !l.getFluidState(at.below()).isEmpty() || l.getBlockState(at.below()).getCollisionShape(l, at.below()).isEmpty()) continue;
			if (!l.getBlockState(at).canBeReplaced() || !l.getBlockState(at.above()).isAir()) continue;
			if (!seen(l, at, close)) return at;
		}
		return null;
	}

	/** Someone's too close, or has it in front of them with nothing in the way. */
	private static boolean seen(ServerLevel l, BlockPos at, int close) {
		Vec3 spot = Vec3.atBottomCenterOf(at).add(0, 1.4, 0);
		for (ServerPlayer p : l.players()) {
			Vec3 to = spot.subtract(p.getEyePosition());
			double flat = Math.hypot(to.x, to.z);
			if (flat < close) return true;
			if (flat > 160) continue;
			Vec3 look = p.getLookAngle();
			if ((look.x * to.x + look.z * to.z) / (Math.hypot(look.x, look.z) * flat + 1e-6) < 0.35) continue;   // behind or off to the side
			if (l.clip(new ClipContext(p.getEyePosition(), spot, ClipContext.Block.VISUAL, ClipContext.Fluid.NONE, p)).getType() == HitResult.Type.MISS) return true;
		}
		return false;
	}

	/** The town or village this is in, if any. */
	@Nullable
	static Capital.Site town(BlockPos at) {
		for (Capital.Site s : Capital.sites)
			if (at.getX() >= s.cx0 * 16 && at.getX() < (s.cx0 + s.cw) * 16 && at.getZ() >= s.cz0 * 16 && at.getZ() < (s.cz0 + s.cd) * 16) return s;
		return null;
	}

	// ---------------------------------------------------------------- who hurts whom

	/** The player behind a blow: themselves, their arrow or bolt, their pet, mount or thrall. */
	private static boolean byPlayer(Entity e) {
		if (e instanceof Projectile pr) e = pr.getOwner();
		if (e instanceof OwnableEntity o && o.getOwner() instanceof Player) return true;
		return e instanceof Player || e != null && Spells.isThrall(e);
	}

	/** What each has dealt, for the fight test (SelfTest.adventurerFight). */
	static final Map<UUID, Float> DEALT = new java.util.concurrent.ConcurrentHashMap<>();

	private static void hurt(LivingIncomingDamageEvent e) {
		Entity by = e.getSource().getEntity();
		if (by instanceof Projectile pr) by = pr.getOwner();
		if (by instanceof Adventurer a && e.getEntity() instanceof net.minecraft.world.entity.monster.Enemy) DEALT.merge(a.getUUID(), e.getAmount(), Float::sum);
		// a player pitching in on their fight: they'll remember it
		if (by instanceof Player pl && e.getEntity() instanceof net.minecraft.world.entity.monster.Enemy && e.getEntity().level() instanceof ServerLevel l)
			for (Adventurer a : l.getEntitiesOfClass(Adventurer.class, e.getEntity().getBoundingBox().inflate(20), a -> a.getTarget() == e.getEntity() && a.helper == null)) {
				a.helper = pl.getUUID();
				for (Adventurer m : a.mates()) m.helper = pl.getUUID();
			}
		// a duel's blows land (Encounters)
		if (Encounters.duel(e, by)) return;
		if (e.getEntity() instanceof Adventurer && (byPlayer(e.getSource().getEntity()) || by instanceof Adventurer)) e.setCanceled(true);
		else if (by instanceof Adventurer && (e.getEntity() instanceof Player || byPlayer(e.getEntity()))) e.setCanceled(true);
	}

	/** Monsters go for adventurers too, not only for players. */
	private static void join(EntityJoinLevelEvent e) {
		if (!e.getLevel().isClientSide() && e.getEntity() instanceof Monster m)
			m.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(m, Adventurer.class, true));
	}

	private static void commands(RegisterCommandsEvent e) {
		e.getDispatcher().register(Commands.literal("ashbound").requires(s -> s.hasPermission(2)).then(Commands.literal("adventurers")
				.then(Commands.literal("spawn").executes(c -> spawnNear(c.getSource().getPlayerOrException(), null))
						.then(Commands.argument("rank_or_name", StringArgumentType.greedyString())
								.suggests((c, b) -> net.minecraft.commands.SharedSuggestionProvider.suggest(PARTIES.stream().map(Party::name), b))
								.executes(c -> spawnNear(c.getSource().getPlayerOrException(), StringArgumentType.getString(c, "rank_or_name")))))
				.then(Commands.literal("meet").executes(c -> meetNear(c.getSource().getPlayerOrException(), null))
						.then(Commands.argument("what", StringArgumentType.word())
								.suggests((c, b) -> net.minecraft.commands.SharedSuggestionProvider.suggest(MEETINGS, b))
								.executes(c -> meetNear(c.getSource().getPlayerOrException(), StringArgumentType.getString(c, "what")))))
				.then(Commands.literal("clear").executes(c -> {
					int n = 0;
					for (ServerLevel l : c.getSource().getServer().getAllLevels())
						for (Entity a : l.getEntities(TYPE.get(), x -> true)) {
							a.discard();
							n++;
						}
					int done = n;
					c.getSource().sendSuccess(() -> Component.literal("Sent " + done + " adventurers on their way"), false);
					return n;
				}))));
	}

	private static int spawnNear(ServerPlayer p, String what) {
		List<Party> pick = PARTIES.stream().filter(x -> what == null || x.name().equalsIgnoreCase(what) || what.length() == 1 && x.rank() == Character.toUpperCase(what.charAt(0))).toList();
		if (pick.isEmpty()) {
			p.sendSystemMessage(Component.literal("No party like that").withStyle(ChatFormatting.RED));
			return 0;
		}
		Party party = pick.get(p.getRandom().nextInt(pick.size()));
		var look = p.getLookAngle();
		List<Adventurer> made = spawn(p.serverLevel(), BlockPos.containing(p.position().add(look.x * 8, 0, look.z * 8)), party);
		p.sendSystemMessage(Component.literal(party.name() + " (" + party.rank() + "), " + made.size() + " of them").withStyle(ChatFormatting.GOLD));
		return made.size();
	}

	private static int meetNear(ServerPlayer p, @Nullable String what) {
		String done = meet(p.serverLevel(), p, what);
		p.sendSystemMessage(Component.literal(done != null ? done : "Nobody turned up (no room out of sight, or nothing like that near)")
				.withStyle(done != null ? ChatFormatting.GOLD : ChatFormatting.RED));
		return done != null ? 1 : 0;
	}

	static void register(IEventBus bus) {
		bus.addListener((EntityAttributeCreationEvent e) -> e.put(TYPE.get(), Adventurer.attributes().build()));
		EpicFightEventHooks.Registry.ENTITY_PATCH.registerEvent(e -> e.registerEntityPatch(TYPE.get(), AdventurerPatch::new));
		bus.addListener((FMLCommonSetupEvent e) -> e.enqueueWork(() -> Armatures.registerEntityTypeArmature(TYPE.get(), Armatures.BIPED)));
		NeoForge.EVENT_BUS.addListener(Adventurers::hurt);
		NeoForge.EVENT_BUS.addListener(Adventurers::join);
		NeoForge.EVENT_BUS.addListener(Adventurers::commands);
		NeoForge.EVENT_BUS.addListener(Adventurers::tick);
		Encounters.init();
		Treasure.init();
		Bounties.init();
		WorldBeasts.init();
	}
}
