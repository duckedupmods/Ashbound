package com.snoringwalrus.ashbound;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.serialization.Codec;

import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.AxeItem;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.CrossbowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ShieldItem;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.TridentItem;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.living.LivingDropsEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.player.ItemTooltipEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;
import yesman.epicfight.api.event.EpicFightEventHooks;
import yesman.epicfight.api.utils.AttackResult;
import yesman.epicfight.network.EpicFightNetworkManager;
import yesman.epicfight.network.server.SPRemoveSkillAndLearn;
import yesman.epicfight.registry.EpicFightRegistries;
import yesman.epicfight.registry.entries.EpicFightAttributes;
import yesman.epicfight.world.capabilities.EpicFightCapabilities;
import yesman.epicfight.world.capabilities.item.CapabilityItem;
import yesman.epicfight.skill.Skill;
import yesman.epicfight.skill.SkillContainer;
import yesman.epicfight.world.capabilities.EpicFightCapabilities;
import yesman.epicfight.world.capabilities.entitypatch.player.ServerPlayerPatch;
import yesman.epicfight.world.capabilities.skill.PlayerSkills;
import yesman.epicfight.world.item.SkillBookItem;

/**
 * The Ash Tree (docs/SKILLTREE.md, tools/skilltree.py -> skill_tree.json): one point a level, spent on a node joined
 * to one you have. Small nodes and notables add stats (an area's only while you hold its weapon, the Core's always);
 * notables and keystones may carry a mechanic (fx, coded below) or unlock an Epic Fight skill (ef), which the tree
 * learns and equips for you: the tree is the only way to get them (skill books are gone, K opens this tree).
 */
public final class Passives {
	private Passives() {}

	/** role: stat (numbers, up to max ranks), ember (changes a move), gold (a new move or skill), key (a keystone) */
	public record Node(String id, String kind, String role, int max, String name, String area, String about, Map<String, Double> stats,
			Map<String, Double> always, String fx, String ef, float x, float y, int icon) {}

	public static final Map<String, Node> NODES = new LinkedHashMap<>();
	public static final Map<String, Set<String>> LINKS = new HashMap<>();
	public static final Map<String, String> AREA_NAMES = new LinkedHashMap<>(), AREA_COLOURS = new HashMap<>();
	/** each area's emblem (an icon cell) and its page: where each of its nodes sits there */
	public static final Map<String, Integer> AREA_ICONS = new HashMap<>();
	/** each area's emblem: a cell of textures/gui/tree_emblems.png (a rendered weapon, 128px, 4 to a row) */
	public static final Map<String, Integer> AREA_EMBLEMS = new HashMap<>();
	public static final Map<String, Map<String, float[]>> PAGES = new LinkedHashMap<>();
	/** each area's picture behind its page (lines in page units) and the points it takes to fill */
	public static final Map<String, List<float[][]>> FIGURES = new HashMap<>();
	public static final Map<String, Integer> AREA_POINTS = new HashMap<>();
	/** the overview's tree: trunk, bark, a branch to each emblem (tools/skilltree.py overview()) */
	public static JsonObject overview;
	/** points spent in an area before its keystone opens */
	public static int keyNeed = 16;
	public static String start = "core_start";
	/** rows of 16 icons in textures/gui/tree_icons.png */
	public static int iconRows = 1;

	static {
		try (InputStream in = Passives.class.getResourceAsStream("/ashbound/skill_tree.json")) {
			JsonObject o = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
			start = o.get("start").getAsString();
			iconRows = o.has("icon_rows") ? o.get("icon_rows").getAsInt() : 1;
			if (o.has("key_need")) keyNeed = o.get("key_need").getAsInt();
			if (o.has("overview")) overview = o.getAsJsonObject("overview");
			for (JsonElement e : o.getAsJsonArray("areas")) {
				JsonObject a = e.getAsJsonObject();
				AREA_NAMES.put(a.get("id").getAsString(), a.get("name").getAsString());
				AREA_COLOURS.put(a.get("id").getAsString(), a.get("colour").getAsString());
				if (a.has("icon")) AREA_ICONS.put(a.get("id").getAsString(), a.get("icon").getAsInt());
				if (a.has("emblem")) AREA_EMBLEMS.put(a.get("id").getAsString(), a.get("emblem").getAsInt());
				Map<String, float[]> page = new LinkedHashMap<>();
				if (a.has("page")) for (Map.Entry<String, JsonElement> p : a.getAsJsonObject("page").entrySet())
					page.put(p.getKey(), new float[] {p.getValue().getAsJsonArray().get(0).getAsFloat(), p.getValue().getAsJsonArray().get(1).getAsFloat()});
				PAGES.put(a.get("id").getAsString(), page);
				List<float[][]> fig = new ArrayList<>();
				if (a.has("figure")) for (JsonElement ln : a.getAsJsonArray("figure")) fig.add(points(ln));
				FIGURES.put(a.get("id").getAsString(), fig);
				if (a.has("points")) AREA_POINTS.put(a.get("id").getAsString(), a.get("points").getAsInt());
			}
			for (JsonElement e : o.getAsJsonArray("nodes")) {
				JsonObject n = e.getAsJsonObject();
				NODES.put(n.get("id").getAsString(), new Node(n.get("id").getAsString(), n.get("kind").getAsString(),
						n.has("role") ? n.get("role").getAsString() : "stat", n.has("max") ? n.get("max").getAsInt() : 1, n.get("name").getAsString(), n.get("area").getAsString(), n.get("about").getAsString(), stats(n, "stats"),
						stats(n, "always"), str(n, "fx"), str(n, "ef"), n.get("x").getAsFloat(), n.get("y").getAsFloat(),
						n.has("icon") ? n.get("icon").getAsInt() : 0));
			}
			for (JsonElement e : o.getAsJsonArray("links")) {
				String a = e.getAsJsonArray().get(0).getAsString(), b = e.getAsJsonArray().get(1).getAsString();
				LINKS.computeIfAbsent(a, k -> new HashSet<>()).add(b);
				LINKS.computeIfAbsent(b, k -> new HashSet<>()).add(a);
			}
		} catch (Exception e) {
			Ashbound.LOG.error("skill tree not loaded", e);
		}
	}

	/** [[x, y], ...] as an array of points */
	public static float[][] points(JsonElement e) {
		var arr = e.getAsJsonArray();
		float[][] out = new float[arr.size()][2];
		for (int i = 0; i < arr.size(); i++) {
			out[i][0] = arr.get(i).getAsJsonArray().get(0).getAsFloat();
			out[i][1] = arr.get(i).getAsJsonArray().get(1).getAsFloat();
		}
		return out;
	}

	private static Map<String, Double> stats(JsonObject n, String key) {
		Map<String, Double> m = new HashMap<>();
		if (n.has(key)) for (Map.Entry<String, JsonElement> s : n.getAsJsonObject(key).entrySet()) m.put(s.getKey(), s.getValue().getAsDouble());
		return m;
	}

	private static String str(JsonObject n, String key) {
		return n.has(key) && !n.get(key).isJsonNull() ? n.get(key).getAsString() : null;
	}

	// ---------------------------------------------------------------- your nodes

	static final DeferredRegister<AttachmentType<?>> ATTACHMENTS = DeferredRegister.create(NeoForgeRegistries.ATTACHMENT_TYPES, Ashbound.ID);

	/** the nodes you've taken, once per rank (the start isn't listed: everyone has it) */
	public static final Supplier<AttachmentType<List<String>>> TAKEN = ATTACHMENTS.register("tree",
			() -> AttachmentType.<List<String>>builder(() -> new ArrayList<>()).serialize(Codec.STRING.listOf()).copyOnDeath().build());

	/** client: what the server last said */
	public static Set<String> clientTaken = new HashSet<>();
	public static Map<String, Integer> clientRanks = new HashMap<>();
	/** client: the local player, whose tree clientTaken is */
	public static UUID clientSelf;
	/** the two-hander keystone, Titan's Grip */
	static final String TITAN = "twohander_k";

	/** Titan's Grip taken (held or not). The client knows its own tree; another player it takes on trust */
	public static boolean titanGrip(Player p) {
		if (p instanceof ServerPlayer sp) return sp.getData(TAKEN).contains(TITAN);
		return !p.getUUID().equals(clientSelf) || clientTaken.contains(TITAN);
	}

	/** Titan's Grip's price: any weapon but a two-hander is no use to you */
	public static boolean titanLocked(Player p) {
		String k = kindOf(p.getMainHandItem());
		return !k.isEmpty() && !k.equals("twohander") && titanGrip(p);
	}

	private static void titanNag(ServerPlayer p) {
		State s = state(p);
		long now = p.level().getGameTime();
		if (now < s.nag) return;
		s.nag = now + 40;
		p.displayClientMessage(Component.literal("Titan's Grip: only two-handers answer you").withStyle(ChatFormatting.RED), true);
	}
	public static int clientPoints;
	public static Set<String> clientEquipped = new HashSet<>();

	public static int points(ServerPlayer p) {
		return Levels.level(p) - 1 - p.getData(TAKEN).size();
	}

	static boolean owns(ServerPlayer p, String id) {
		return id.equals(start) || p.getData(TAKEN).contains(id);
	}

	static int rank(ServerPlayer p, String id) {
		int n = 0;
		for (String t : p.getData(TAKEN)) if (t.equals(id)) n++;
		return n;
	}

	/** points spent in one area (ranks count) */
	public static int spentIn(java.util.Collection<String> taken, String area) {
		int n = 0;
		for (String t : taken) {
			Node nd = NODES.get(t);
			if (nd != null && nd.area().equals(area)) n++;
		}
		return n;
	}

	/** client: what the server sent, once per rank */
	public static void clientSet(List<String> taken) {
		clientTaken = new HashSet<>(taken);
		Map<String, Integer> r = new HashMap<>();
		for (String t : taken) r.merge(t, 1, Integer::sum);
		clientRanks = r;
	}

	/** what one point does: 0 take, 1 refund, 2 buy a level, 3 reset all, 4 equip/unequip an unlocked Epic Fight skill */
	static void act(ServerPlayer p, int action, String id) {
		switch (action) {
			case 0 -> take(p, id);
			case 1 -> refund(p, id);
			case 2 -> Levels.levelUp(p);
			case 3 -> reset(p);
			case 4 -> toggle(p, id);
			default -> {}
		}
		sync(p);
	}

	private static void take(ServerPlayer p, String id) {
		Node n = NODES.get(id);
		if (n == null || id.equals(start) || rank(p, id) >= n.max() || points(p) <= 0) return;
		boolean first = !owns(p, id);
		if (first && LINKS.getOrDefault(id, Set.of()).stream().noneMatch(l -> owns(p, l))) return;
		if (n.kind().equals("keystone")) {
			if (p.getData(TAKEN).stream().anyMatch(t -> NODES.get(t) != null && NODES.get(t).kind().equals("keystone"))) {
				p.displayClientMessage(Component.literal("One keystone at a time").withStyle(ChatFormatting.RED), true);
				return;
			}
			if (spentIn(p.getData(TAKEN), n.area()) < keyNeed) {
				p.displayClientMessage(Component.literal("Spend " + keyNeed + " points in " + AREA_NAMES.get(n.area()) + " first")
						.withStyle(ChatFormatting.RED), true);
				return;
			}
		}
		List<String> l = new ArrayList<>(p.getData(TAKEN));
		l.add(id);
		p.setData(TAKEN, l);
		if (first && n.ef() != null) learn(p, n.ef(), true);
		p.level().playSound(null, p.blockPosition(), SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, 0.8f,
				n.kind().equals("small") ? 1.2f + 0.08f * rank(p, id) : 0.8f);
		apply(p);
	}

	/** what taking a point back costs */
	public static int refundCost(int level) {
		return 30 + 10 * level;
	}

	private static void refund(ServerPlayer p, String id) {
		if (!p.getData(TAKEN).contains(id)) return;
		List<String> rest = new ArrayList<>(p.getData(TAKEN));
		rest.remove(id);
		boolean gone = !rest.contains(id);
		if (gone && !joined(rest)) {
			p.displayClientMessage(Component.literal("That would cut off other nodes").withStyle(ChatFormatting.RED), true);
			return;
		}
		// a keystone you hold keeps the points it needed in its area
		Node was = NODES.get(id);
		boolean keyHere = rest.stream().anyMatch(t -> NODES.get(t) != null && NODES.get(t).kind().equals("keystone")
				&& was != null && NODES.get(t).area().equals(was.area()));
		if (keyHere && !was.kind().equals("keystone") && spentIn(rest, was.area()) - 1 < keyNeed) {
			p.displayClientMessage(Component.literal("Your keystone needs " + keyNeed + " points here").withStyle(ChatFormatting.RED), true);
			return;
		}
		int cost = refundCost(Levels.level(p));
		if (!p.isCreative() && p.getData(Levels.ASH) < cost) {
			p.displayClientMessage(Component.literal("Taking it back costs " + cost + " Ash").withStyle(ChatFormatting.RED), true);
			return;
		}
		if (!p.isCreative()) p.setData(Levels.ASH, p.getData(Levels.ASH) - cost);
		p.setData(TAKEN, rest);
		if (gone && was != null && was.ef() != null) forget(p, was.ef());
		Levels.sync(p);
		apply(p);
	}

	/** every taken node still joined to the start without the one taken back */
	private static boolean joined(List<String> taken) {
		Set<String> have = new HashSet<>(taken), seen = new HashSet<>(List.of(start));
		List<String> todo = new ArrayList<>(List.of(start));
		while (!todo.isEmpty()) {
			String cur = todo.remove(todo.size() - 1);
			for (String nb : LINKS.getOrDefault(cur, Set.of()))
				if (have.contains(nb) && seen.add(nb)) todo.add(nb);
		}
		return seen.size() == have.size() + 1;
	}

	/** a full reset: every point back, for Ash */
	public static int resetCost(int level) {
		return 50 * level;
	}

	private static void reset(ServerPlayer p) {
		int cost = resetCost(Levels.level(p));
		if (p.getData(TAKEN).isEmpty()) return;
		if (!p.isCreative() && p.getData(Levels.ASH) < cost) {
			p.displayClientMessage(Component.literal("A full reset costs " + cost + " Ash").withStyle(ChatFormatting.RED), true);
			return;
		}
		if (!p.isCreative()) p.setData(Levels.ASH, p.getData(Levels.ASH) - cost);
		for (String id : new HashSet<>(p.getData(TAKEN))) {
			Node n = NODES.get(id);
			if (n != null && n.ef() != null) forget(p, n.ef());
		}
		p.setData(TAKEN, new ArrayList<>());
		p.level().playSound(null, p.blockPosition(), SoundEvents.FIRE_EXTINGUISH, SoundSource.PLAYERS, 0.8f, 0.8f);
		Levels.sync(p);
		apply(p);
	}

	static void sync(ServerPlayer p) {
		List<String> eq = new ArrayList<>();
		ServerPlayerPatch pp = patch(p);
		if (pp != null)
			pp.getPlayerSkills().listSkillContainers().filter(c -> c.getSkill() != null)
					.forEach(c -> eq.add(c.getSkill().getRegistryName().getPath()));
		PacketDistributor.sendToPlayer(p, new Net.Tree(new ArrayList<>(p.getData(TAKEN)), points(p), eq));
	}

	// ---------------------------------------------------------------- Epic Fight's skills

	private static ServerPlayerPatch patch(ServerPlayer p) {
		return EpicFightCapabilities.getEntityPatch(p, ServerPlayerPatch.class);
	}

	private static Skill skill(String id) {
		return EpicFightRegistries.SKILL.get(ResourceLocation.fromNamespaceAndPath("epicfight", id));
	}

	/** learns it, and equips it: in an empty slot of its kind, or over the first one if equip says so */
	private static void learn(ServerPlayer p, String id, boolean replace) {
		ServerPlayerPatch pp = patch(p);
		Skill s = skill(id);
		if (pp == null || s == null) return;
		PlayerSkills ps = pp.getPlayerSkills();
		if (s.getCategory().learnable()) ps.addLearnedSkill(s);
		if (ps.isEquipping(s)) return;
		SkillContainer c = ps.getFirstEmptyContainer(s.getCategory());
		if (c == null && replace) c = ps.getSkillContainersFor(s.getCategory()).stream().findFirst().orElse(null);
		if (c == null) return;
		c.setSkill(s);
		EpicFightNetworkManager.sendToPlayer(c.createSyncPacketToLocalPlayer(), p);
		EpicFightNetworkManager.sendToAllPlayerTrackingThisEntity(c.createSyncPacketToRemotePlayer(), p);
	}

	private static void forget(ServerPlayer p, String id) {
		ServerPlayerPatch pp = patch(p);
		Skill s = skill(id);
		if (pp == null || s == null) return;
		PlayerSkills ps = pp.getPlayerSkills();
		SkillContainer c = ps.getSkillContainer(s);
		if (c != null) {
			c.setSkill(null);
			EpicFightNetworkManager.sendToPlayer(new SPRemoveSkillAndLearn(s, c.getSlot()), p);
			EpicFightNetworkManager.sendToAllPlayerTrackingThisEntity(c.createSyncPacketToRemotePlayer(), p);
		}
		ps.removeLearnedSkill(s);
	}

	/** an unlocked skill on or off (two dodges or more passives than slots: you pick which) */
	private static void toggle(ServerPlayer p, String id) {
		Node n = NODES.get(id);
		if (n == null || n.ef() == null || !owns(p, id)) return;
		ServerPlayerPatch pp = patch(p);
		Skill s = skill(n.ef());
		if (pp == null || s == null) return;
		SkillContainer c = pp.getPlayerSkills().getSkillContainer(s);
		if (c != null) {
			c.setSkill(null);
			EpicFightNetworkManager.sendToPlayer(c.createSyncPacketToLocalPlayer(), p);
			EpicFightNetworkManager.sendToAllPlayerTrackingThisEntity(c.createSyncPacketToRemotePlayer(), p);
		} else learn(p, n.ef(), true);
	}

	/** everyone has Roll and Guard (the start), and everything their nodes unlock */
	private static void grant(ServerPlayer p) {
		// nodes the tree no longer has (a remake) are dropped, their points back
		Map<String, Integer> seen = new HashMap<>();
		List<String> kept = p.getData(TAKEN).stream().filter(NODES::containsKey)
				.filter(t -> seen.merge(t, 1, Integer::sum) <= NODES.get(t).max()).toList();
		if (kept.size() != p.getData(TAKEN).size()) p.setData(TAKEN, new ArrayList<>(kept));
		learn(p, "roll", false);
		learn(p, "guard", false);
		p.getAttribute(EpicFightAttributes.STAMINA_REGEN).setBaseValue(STAMINA_REGEN);
		for (String id : new HashSet<>(p.getData(TAKEN))) {
			Node n = NODES.get(id);
			if (n != null && n.ef() != null) learn(p, n.ef(), false);
		}
	}

	// ---------------------------------------------------------------- stats

	/** Epic Fight's is 1: a little quicker, since swings cost stamina here and there they cost none */
	private static final double STAMINA_REGEN = 1.25;
	/** a bow shot's stamina: about 1.1 a second, ranged keeps its distance */
	private static final float BOW_COST = 1.2f;

	/** A swing's stamina before armour's weight: about 1.25 a second of nonstop swinging, whatever the weapon (tools/balance.py SWING). */
	static float swingCost(Player p, ItemStack held) {
		String kind = kindOf(held);
		if (kind.equals("twohander") && has(p, "titans_grip")) return kindOf(p.getOffhandItem()).equals("twohander") ? 1.4f : 2.1f;
		return switch (kind) {
			case "" -> otherSwing(held);
			case "dagger" -> 0.4f;
			case "spear" -> 0.7f;
			case "hammer", "twohander" -> 1.6f;
			case "black", "white", "summon" -> 1.2f;
			default -> 0.6f;
		};
	}

	/** weapons of the modpack's other mods: by how Epic Fight holds them. Fists and tools stay free. */
	private static float otherSwing(ItemStack held) {
		if (held.isEmpty()) return 0;
		CapabilityItem cap = EpicFightCapabilities.getItemStackCapability(held);
		if (cap.isEmpty()) return 0;
		var category = cap.getWeaponCategory();
		if (category == CapabilityItem.WeaponCategories.NOT_WEAPON || category == CapabilityItem.WeaponCategories.FIST
				|| category == CapabilityItem.WeaponCategories.PICKAXE || category == CapabilityItem.WeaponCategories.SHOVEL
				|| category == CapabilityItem.WeaponCategories.HOE) return 0;
		if (category == CapabilityItem.WeaponCategories.GREATSWORD || category == CapabilityItem.WeaponCategories.LONGSWORD
				|| category == CapabilityItem.WeaponCategories.AXE) return 1.6f;
		if (category == CapabilityItem.WeaponCategories.SPEAR || category == CapabilityItem.WeaponCategories.TRIDENT) return 0.7f;
		return category == CapabilityItem.WeaponCategories.DAGGER ? 0.4f : 0.6f;
	}

	/** a weapon's stamina on its tooltip, as a staff shows its mana; null for what costs none */
	static Component staminaLine(Player p, ItemStack s) {
		String kind = kindOf(s);
		String text = kind.equals("bow") ? BOW_COST + " stamina a shot" : kind.equals("shield") ? "Blocking costs stamina" : null;
		if (text == null) {
			float cost = swingCost(p, s);
			if (cost <= 0) return null;
			text = cost + " stamina a swing";
		}
		return Component.literal(text).withStyle(ChatFormatting.GREEN);
	}

	private static void staminaTooltip(ItemTooltipEvent e) {
		if (e.getItemStack().getItem() instanceof Spells.Staff) return;   // it says so itself, under its mana
		Component line = staminaLine(e.getEntity(), e.getItemStack());
		if (line == null) return;
		List<Component> lines = e.getToolTip();
		int at = Math.min(1, lines.size());
		while (at < lines.size() && !lines.get(at).getString().isEmpty()) at++;
		lines.add(at, line);
	}

	/** what a held item counts as: one of the ten weapon types, or nothing */
	public static String kindOf(ItemStack s) {
		if (s.isEmpty()) return "";
		ResourceLocation id = BuiltInRegistries.ITEM.getKey(s.getItem());
		if (id.getNamespace().equals(Ashbound.ID)) {
			Gear.Weapon w = Gear.WEAPON.get(id.getPath());
			if (w != null) return w.kind();
			WorldArms.Arm a = WorldArms.of(s);
			if (a != null) return a.kind();
		}
		String path = id.getPath();
		if (s.getItem() instanceof ShieldItem) return "shield";
		if (s.getItem() instanceof BowItem || s.getItem() instanceof CrossbowItem) return "bow";
		if (s.getItem() instanceof TridentItem || path.contains("spear")) return "spear";
		if (path.contains("greatsword") || path.contains("longsword")) return "twohander";
		if (path.contains("dagger")) return "dagger";
		if (s.getItem() instanceof AxeItem || path.contains("hammer") || path.contains("mace")) return "hammer";
		if (s.getItem() instanceof SwordItem || path.contains("tachi") || path.contains("sword")) return "sword";
		return "";
	}

	/** the areas live right now: the Core, the main hand's weapon, and a shield in either hand */
	private static Set<String> live(Player p) {
		Set<String> s = new HashSet<>(List.of("core", kindOf(p.getMainHandItem())));
		if (kindOf(p.getOffhandItem()).equals("shield")) s.add("shield");
		return s;
	}

	/** a stat summed over your live nodes, plus every keystone drawback and your curios */
	static double stat(Player p, String key) {
		if (!(p instanceof ServerPlayer sp)) return 0;
		Set<String> live = live(p);
		double v = 0;
		for (String id : sp.getData(TAKEN)) {
			Node n = NODES.get(id);
			if (n == null) continue;
			if (live.contains(n.area())) v += n.stats().getOrDefault(key, 0.0);
			v += n.always().getOrDefault(key, 0.0);
		}
		return v + Classes.stat(p, key) + Curios.stat(p, key);   // worn curios' stats that no attribute holds (bow damage, Ash...)
	}

	/** whether one of your live nodes carries this mechanic */
	static boolean has(Player p, String fx) {
		if (!(p instanceof ServerPlayer sp)) return false;
		Set<String> live = live(p);
		for (String id : sp.getData(TAKEN)) {
			Node n = NODES.get(id);
			if (n != null && fx.equals(n.fx()) && live.contains(n.area())) return true;
		}
		return false;
	}

	private record Stat(Holder<Attribute> attr, AttributeModifier.Operation op, double scale) {}

	private static final Map<String, Stat> STATS = new LinkedHashMap<>();

	private static Map<String, Stat> stats() {
		if (STATS.isEmpty()) {
			var base = AttributeModifier.Operation.ADD_MULTIPLIED_BASE;
			var total = AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL;
			var add = AttributeModifier.Operation.ADD_VALUE;
			STATS.put("health%", new Stat(Attributes.MAX_HEALTH, total, 0.01));
			STATS.put("stamina", new Stat(EpicFightAttributes.MAX_STAMINA, add, 1));
			STATS.put("stamina_regen%", new Stat(EpicFightAttributes.STAMINA_REGEN, base, 0.01));
			STATS.put("move%", new Stat(Attributes.MOVEMENT_SPEED, base, 0.01));
			STATS.put("armour", new Stat(Attributes.ARMOR, add, 1));
			STATS.put("stun_armour", new Stat(EpicFightAttributes.STUN_ARMOR, add, 1));
			STATS.put("weight%", new Stat(EpicFightAttributes.WEIGHT, total, 0.01));
			STATS.put("mana", new Stat(Spells.MAX_MANA, add, 1));
			STATS.put("mana_regen%", new Stat(Spells.MANA_REGEN, base, 0.01));
			STATS.put("dmg%", new Stat(Attributes.ATTACK_DAMAGE, total, 0.01));
			STATS.put("speed%", new Stat(Attributes.ATTACK_SPEED, total, 0.01));
			STATS.put("negation%", new Stat(EpicFightAttributes.ARMOR_NEGATION, add, 1));
			STATS.put("impact", new Stat(EpicFightAttributes.IMPACT, add, 1));
			STATS.put("strikes", new Stat(EpicFightAttributes.MAX_STRIKES, add, 1));
			STATS.put("reach", new Stat(Attributes.ENTITY_INTERACTION_RANGE, add, 1));
			STATS.put("knockback", new Stat(Attributes.ATTACK_KNOCKBACK, add, 1));
			STATS.put("spell%", new Stat(Spells.SPELL_POWER, base, 0.01));
			STATS.put("heal%", new Stat(Spells.SPELL_POWER, base, 0.01));
		}
		return STATS;
	}

	private static final Map<UUID, Map<String, Double>> APPLIED = new HashMap<>();

	/** puts your live nodes' stats on you as attribute modifiers (only what changed) */
	static void apply(ServerPlayer p) {
		Map<String, Double> want = new HashMap<>();
		for (String key : stats().keySet())
			if (!key.equals("spell%") && !key.equals("heal%")) want.put(key, stat(p, key));
		// spell power and healing are the same attribute: one modifier
		want.put("spell%", stat(p, "spell%") + stat(p, "heal%"));
		if (has(p, "bone_armour")) want.merge("armour", (double) Spells.thralls(p), Double::sum);
		if (has(p, "impaler") && p.getOffhandItem().isEmpty()) {
			want.merge("reach", 1.0, Double::sum);
			want.merge("strikes", 3.0, Double::sum);
		}
		Map<String, Double> had = APPLIED.computeIfAbsent(p.getUUID(), k -> new HashMap<>());
		if (want.equals(had)) return;
		float health = p.getHealth();
		for (Map.Entry<String, Double> e : want.entrySet()) {
			if (e.getValue().equals(had.get(e.getKey()))) continue;
			Stat s = stats().get(e.getKey());
			AttributeInstance a = p.getAttribute(s.attr());
			if (a == null) continue;
			ResourceLocation id = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "tree_" + e.getKey().replace("%", "_pct"));
			a.removeModifier(id);
			if (e.getValue() != 0) a.addPermanentModifier(new AttributeModifier(id, e.getValue() * s.scale(), s.op()));
		}
		had.clear();
		had.putAll(want);
		if (p.getHealth() > p.getMaxHealth() || health > p.getMaxHealth()) {
			PacketDistributor.sendToPlayer(p, new Net.QuietHealth());
			p.setHealth(Math.min(health, p.getMaxHealth()));
		}
	}

	// ---------------------------------------------------------------- the mechanics

	/** per player timers and counters (game time) */
	private static final class State {
		long riposte, flow, shadow, secondWind, taunt, unbreakable;
		long lunge, bash, retaliate, rageUntil, frenzy, momentumAt, nag;
		int combo, arrows, bolts, hits, rage, momentum;
		long lastHit;
		UUID lastTarget;
		float staminaBefore = -1, refund;
	}

	private static final Map<UUID, State> STATE = new HashMap<>();
	private static final Map<UUID, Long> MARKED = new HashMap<>(), BLESSED = new HashMap<>();
	private static boolean splashing;

	private static State state(Player p) {
		return STATE.computeIfAbsent(p.getUUID(), k -> new State());
	}

	static void register(IEventBus bus) {
		ATTACHMENTS.register(bus);
		NeoForge.EVENT_BUS.addListener((PlayerTickEvent.Post e) -> {
			if (!(e.getEntity() instanceof ServerPlayer p)) return;
			if (p.tickCount % 10 == 0) apply(p);
			State s = STATE.get(p.getUUID());
			if (s != null && s.staminaBefore >= 0) {
				// a blocked hit last tick: give back part of the stamina it took
				ServerPlayerPatch pp = patch(p);
				if (pp != null) {
					float lost = s.staminaBefore - pp.getStamina();
					if (lost > 0) pp.setStamina(Math.min(pp.getMaxStamina(), pp.getStamina() + lost * s.refund));
				}
				s.staminaBefore = -1;
			}
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedInEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer p) {
				grant(p);
				apply(p);
				sync(p);
			}
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerRespawnEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer p) {
				p.getAttribute(EpicFightAttributes.STAMINA_REGEN).setBaseValue(STAMINA_REGEN);
				APPLIED.remove(p.getUUID());
				apply(p);
				sync(p);
			}
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedOutEvent e) -> {
			APPLIED.remove(e.getEntity().getUUID());
			STATE.remove(e.getEntity().getUUID());
		});
		// skill books would be a way round the tree
		NeoForge.EVENT_BUS.addListener((LivingDropsEvent e) -> e.getDrops().removeIf(i -> i.getItem().getItem() instanceof SkillBookItem));
		NeoForge.EVENT_BUS.addListener(Passives::hurt);
		NeoForge.EVENT_BUS.addListener(Passives::died);
		NeoForge.EVENT_BUS.addListener(Passives::arrow);
		EpicFightEventHooks.Entity.ON_DODGE.registerEvent(e -> {
			if (!(e.getEntityPatch().getOriginal() instanceof ServerPlayer p)) return;
			State s = state(p);
			long now = p.level().getGameTime();
			if (has(p, "flow_after_dodge")) s.flow = now + 60;
			if (has(p, "lunge")) s.lunge = now + 20;
			Entity by = e.getDamageSource().getDirectEntity();
			if (has(p, "shadow_step") && by instanceof LivingEntity && by == e.getDamageSource().getEntity()) s.shadow = now + 80;
		});
		EpicFightEventHooks.Entity.TAKE_DAMAGE_INCOME.registerEvent(e -> {
			if (!(e.getEntityPatch().getOriginal() instanceof ServerPlayer p)) return;
			State s = state(p);
			long now = p.level().getGameTime();
			if (e.isParried() && has(p, "riposte")) s.riposte = now + 80;
			if (e.getResult() != AttackResult.ResultType.BLOCKED && !e.isParried()) return;
			blocked(p, s, now, e.getDamageSource().getEntity(), e.getDamage());
		}, -1000);
		NeoForge.EVENT_BUS.addListener(net.neoforged.bus.api.EventPriority.LOW, Passives::staminaTooltip);
		NeoForge.EVENT_BUS.addListener((net.neoforged.neoforge.event.entity.player.ArrowNockEvent e) -> {
			if (!(e.getEntity() instanceof ServerPlayer p) || p.isCreative() || patch(p) == null || patch(p).getStamina() > 0) return;
			p.displayClientMessage(Component.literal("Out of breath").withStyle(ChatFormatting.GREEN), true);
			e.setAction(net.minecraft.world.InteractionResultHolder.fail(e.getBow()));
		});
		NeoForge.EVENT_BUS.addListener((net.neoforged.neoforge.event.entity.player.ArrowLooseEvent e) -> {
			if (!(e.getEntity() instanceof ServerPlayer p) || p.isCreative() || patch(p) == null) return;
			ServerPlayerPatch pp = patch(p);
			pp.setStamina(Math.max(0, pp.getStamina() - pp.getModifiedStaminaConsume(BOW_COST)));
			pp.resetActionTick();
		});
		EpicFightEventHooks.Player.COMBO_ATTACK.registerEvent(e -> {
			ServerPlayerPatch pp = e.getPlayerPatch();
			if (pp.getOriginal() instanceof ServerPlayer p && !p.isCreative()) {
				float cost = pp.getModifiedStaminaConsume(swingCost(p, p.getMainHandItem()));
				if (cost > 0) {
					// any breath left starts a swing, none stops it (docs/BALANCE.md pass 7)
					if (pp.getStamina() <= 0) {
						p.displayClientMessage(Component.literal("Out of breath").withStyle(ChatFormatting.GREEN), true);
						e.cancel();
						return;
					}
					pp.setStamina(Math.max(0, pp.getStamina() - cost));
				}
			}
			// Shadow Lunge: the first swing right after a dodge throws you forward into it
			if (pp.getOriginal() instanceof ServerPlayer p && has(p, "lunge")) {
				State s = state(p);
				if (s.lunge > p.level().getGameTime()) {
					Vec3 f = p.getLookAngle().multiply(1, 0, 1).normalize().scale(1.1);
					p.setDeltaMovement(f.x, 0.08, f.z);
					p.hurtMarked = true;
					s.lunge = 0;
				}
			}
		});
	}

	private static void blocked(ServerPlayer p, State s, long now, Entity by, float dmg) {
		ServerPlayerPatch pp = patch(p);
		double refund = stat(p, "guard%") / 100;
		if (has(p, "unbreakable") && now >= s.unbreakable) {
			refund = 1;
			s.unbreakable = now + 80;
		}
		if (has(p, "bash")) s.bash = now + 60;
		if (has(p, "retaliate")) s.retaliate = now + 60;
		if (refund > 0 && pp != null) {
			s.staminaBefore = pp.getStamina();
			s.refund = (float) Math.min(1, refund);
		}
		if (has(p, "reflect") && by instanceof LivingEntity att && att != p && p.distanceTo(att) < 5)
			att.hurt(p.damageSources().thorns(p), dmg * 0.3f);
		if (has(p, "taunt") && now >= s.taunt) {
			s.taunt = now + 100;
			for (Mob m : p.level().getEntitiesOfClass(Mob.class, p.getBoundingBox().inflate(8), m -> m instanceof Enemy && !Spells.isThrall(m)))
				m.setTarget(p);
			p.level().playSound(null, p.blockPosition(), SoundEvents.RAVAGER_ROAR, SoundSource.PLAYERS, 0.5f, 1.6f);
		}
	}

	private static void hurt(LivingIncomingDamageEvent e) {
		LivingEntity victim = e.getEntity();
		long now = victim.level().getGameTime();
		Entity src = e.getSource().getEntity(), direct = e.getSource().getDirectEntity();
		float amount = e.getAmount();
		// a player's own melee hit
		if (src instanceof ServerPlayer p && (direct == p || direct instanceof AbstractArrow) && titanLocked(p)) {
			titanNag(p);
			e.setCanceled(true);
			return;
		}
		if (src instanceof ServerPlayer p && direct == p && !splashing) {
			State s = state(p);
			if (s.riposte > now && has(p, "riposte")) {
				amount *= 1.6f;
				s.riposte = 0;
				if (has(p, "disarm")) stun(victim, 40);
			}
			s.hits++;
			s.frenzy = now + 100;
			if (has(p, "execute") && victim.getHealth() < victim.getMaxHealth() * 0.3f) amount *= 1.5f;
			// Titan's Grip: the pair comes fast (the dual swords' moves), each blade hits for less (balance.py PASS 6)
			if (has(p, "titans_grip") && kindOf(p.getOffhandItem()).equals("twohander")) amount *= 0.75f;
			if (has(p, "shatter") && victim.hasEffect(MobEffects.MOVEMENT_SLOWDOWN)) amount *= 1.3f;
			if (has(p, "momentum")) {
				s.momentum = now - s.momentumAt < 30 ? Math.min(5, s.momentum + 1) : 0;
				s.momentumAt = now;
				amount *= 1 + 0.05f * s.momentum;
			}
			if (has(p, "charge") && p.isSprinting()) amount *= 1.4f;
			if (has(p, "sunder") && s.hits % 3 == 0) amount *= 1.4f;
			if (s.rageUntil > now && has(p, "rage")) amount *= 1 + 0.05f * s.rage;
			if (s.retaliate > now && has(p, "retaliate")) amount *= 1.2f;
			if (s.bash > now && has(p, "bash")) {
				amount *= 1.25f;
				stun(victim, 20);
				s.bash = 0;
			}
			if (has(p, "concuss") && s.hits % 4 == 0) stun(victim, 20);
			if (has(p, "pin") && p.distanceTo(victim) >= 3) victim.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 3));
			if (has(p, "cleave") && s.hits % 3 == 0) splash(p, victim, amount * 0.5f, 2.5);
			if (has(p, "whirl") && s.hits % 5 == 0) splash(p, victim, amount * 0.5f, 3);
			if (s.flow > now && has(p, "flow_after_dodge")) amount *= 1.15f;
			if (s.shadow > now && has(p, "shadow_step")) {
				amount *= 2f;
				s.shadow = 0;
			}
			if (has(p, "duelist") && p.level().getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(8),
					m -> m instanceof Enemy && m.isAlive()).size() <= 1) amount *= 1.12f;
			if (has(p, "backstab")) {
				Vec3 facing = victim.getLookAngle().multiply(1, 0, 1).normalize();
				Vec3 toP = p.position().subtract(victim.position()).multiply(1, 0, 1).normalize();
				if (facing.dot(toP) < -0.3) amount *= 1.4f;
			}
			if (has(p, "keep_away") && p.distanceTo(victim) >= 2.5f) amount *= 1.1f;
			if (has(p, "blade_dance")) {
				if (!victim.getUUID().equals(s.lastTarget)) amount *= 0.75f;
				s.combo = now - s.lastHit < 30 ? s.combo + 1 : 1;
				if (s.combo % 4 == 0) amount *= 2f;
				s.lastHit = now;
				s.lastTarget = victim.getUUID();
			}
			if (has(p, "venom")) victim.addEffect(new MobEffectInstance(MobEffects.POISON, 40, 0));
			if (has(p, "earthshaker")) splash(p, victim, amount * 0.25f, 2.5);
		}
		// arrows
		if (direct instanceof AbstractArrow a && src instanceof ServerPlayer p) {
			amount *= (float) (1 + stat(p, "arrow%") / 100);
			if (a.getTags().contains("ab_steady")) amount *= 1.2f;
			if (a.getTags().contains("ab_deadeye")) amount *= 1.5f;
			if (a.getTags().contains("ab_moving")) amount *= 0.7f;
			if (state(p).flow > now && has(p, "flow_after_dodge")) amount *= 1.15f;
			if (a.isCritArrow() && has(p, "mark")) MARKED.put(victim.getUUID(), now + 120);
			if (has(p, "point_blank") && p.distanceTo(victim) <= 6) amount *= 1.25f;
			if (a.isCritArrow() && has(p, "pierce")) splash(p, victim, amount * 0.6f, 2);
			state(p).frenzy = now + 100;
		}
		// thralls
		if (src != null && Spells.isThrall(src)) {
			UUID owner = Spells.ownerOf(src);
			Player p = owner == null ? null : victim.level().getPlayerByUUID(owner);
			if (p != null) {
				if (has(p, "pack")) amount *= 1 + 0.05f * Math.max(0, Spells.thralls(p) - 1);
				if (has(p, "legion")) amount *= 0.7f;
				if (has(p, "frenzy") && state(p).frenzy > now) amount *= 1.2f;
			}
		}
		// whoever hits a marked target, a blessed attacker
		if (src instanceof ServerPlayer p && victim.isInvertedHealAndHarm() && has(p, "smite")) amount *= 1.3f;
		if (src instanceof Player || src != null && Spells.isThrall(src)) {
			if (MARKED.getOrDefault(victim.getUUID(), 0L) > now) amount *= 1.15f;
			if (BLESSED.getOrDefault(src.getUUID(), 0L) > now) amount *= 1.1f;
		}
		// a player taking it
		if (victim instanceof ServerPlayer p) {
			if (has(p, "mana_shield")) {
				float mana = p.getData(Spells.MANA), off = Math.min(amount * 0.2f, mana / 2);
				if (off > 0) {
					p.setData(Spells.MANA, mana - off * 2);
					amount -= off;
				}
			}
			State s = state(p);
			if (has(p, "last_stand") && p.getHealth() < p.getMaxHealth() * 0.3f) amount *= 0.75f;
			for (ServerPlayer q : p.serverLevel().getEntitiesOfClass(ServerPlayer.class, p.getBoundingBox().inflate(6), q -> q != p))
				if (has(q, "guardian")) {
					amount *= 0.9f;
					break;
				}
			if (src instanceof LivingEntity att && !(att instanceof Player)) {
				if (has(p, "rage")) {
					s.rage = s.rageUntil > now ? Math.min(4, s.rage + 1) : 1;
					s.rageUntil = now + 120;
				}
				if (has(p, "static") && direct == att && p.distanceTo(att) < 5) att.hurt(p.damageSources().indirectMagic(p, p), 3);
			}
			if (amount >= p.getHealth() && has(p, "second_wind") && now >= s.secondWind) {
				amount = Math.max(0, p.getHealth() - 1);
				s.secondWind = now + 3600;
				p.invulnerableTime = 40;
				p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 40, 4));
				p.level().playSound(null, p.blockPosition(), SoundEvents.TOTEM_USE, SoundSource.PLAYERS, 0.6f, 1.3f);
				p.displayClientMessage(Component.literal("Second Wind").withStyle(ChatFormatting.GOLD), true);
			}
		}
		if (amount != e.getAmount()) e.setAmount(amount);
	}

	/** a short stun: slowed to a crawl and too weak to hurt */
	private static void stun(LivingEntity e, int ticks) {
		e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, ticks, 6));
		e.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, ticks, 4));
		if (e.level() instanceof ServerLevel sl)
			sl.sendParticles(net.minecraft.core.particles.ParticleTypes.CRIT, e.getX(), e.getY() + e.getBbHeight() + 0.2, e.getZ(), 8, 0.3, 0.1, 0.3, 0.1);
	}

	/** hurts the monsters around a target (shockwaves); never players or thralls */
	private static void splash(ServerPlayer p, LivingEntity at, float dmg, double r) {
		if (dmg <= 0) return;
		splashing = true;
		try {
			for (LivingEntity m : p.level().getEntitiesOfClass(LivingEntity.class, at.getBoundingBox().inflate(r),
					m -> m != at && m != p && m instanceof Enemy && !Spells.isThrall(m) && m.isAlive()))
				m.hurt(p.damageSources().playerAttack(p), dmg);
		} finally {
			splashing = false;
		}
		((ServerLevel) p.level()).sendParticles(net.minecraft.core.particles.ParticleTypes.EXPLOSION, at.getX(), at.getY() + 0.2, at.getZ(), 1, 0, 0, 0, 0);
	}

	private static void died(LivingDeathEvent e) {
		LivingEntity dead = e.getEntity();
		if (dead.level().isClientSide) return;
		if (Spells.isThrall(dead)) {
			UUID owner = Spells.ownerOf(dead);
			Player p = owner == null ? null : dead.level().getPlayerByUUID(owner);
			if (p != null && has(p, "death_pact")) p.heal(3);
			return;
		}
		if (!(e.getSource().getEntity() instanceof ServerPlayer p)) return;
		if (has(p, "kill_heal")) p.heal(1);
		if (has(p, "flourish")) {
			ServerPlayerPatch pp = patch(p);
			if (pp != null) pp.setStamina(Math.min(pp.getMaxStamina(), pp.getStamina() + 3));
		}
		if (has(p, "vanish")) {
			p.addEffect(new MobEffectInstance(MobEffects.INVISIBILITY, 60, 0));
			for (Mob m : p.level().getEntitiesOfClass(Mob.class, p.getBoundingBox().inflate(16), m -> m.getTarget() == p)) m.setTarget(null);
		}
		if (has(p, "siphon")) {
			float mana = Math.min(Spells.max(p), p.getData(Spells.MANA) + 6);
			p.setData(Spells.MANA, mana);
			PacketDistributor.sendToPlayer(p, new Net.Mana(mana, Spells.max(p)));
		}
		if (has(p, "harvest"))
			for (LivingEntity t : p.level().getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(32),
					t -> Spells.isThrall(t) && p.getUUID().equals(Spells.ownerOf(t)))) t.heal(4);
		if (has(p, "aftershock") && e.getSource().getDirectEntity() == p)
			splash(p, dead, (float) (p.getAttributeValue(Attributes.ATTACK_DAMAGE) * 0.4), 3);
	}

	/** arrows as they leave the bow: speed, and what they were shot like */
	private static void arrow(EntityJoinLevelEvent e) {
		if (e.getLevel().isClientSide || e.loadedFromDisk() || !(e.getEntity() instanceof AbstractArrow a) || !(a.getOwner() instanceof ServerPlayer p))
			return;
		if (a.getTags().contains("ab_volley")) return;
		double v = stat(p, "velocity%");
		if (v != 0) a.setDeltaMovement(a.getDeltaMovement().scale(1 + v / 100));
		boolean still = p.getDeltaMovement().horizontalDistanceSqr() < 0.0004;
		if (has(p, "steady") && still) a.addTag("ab_steady");
		if (has(p, "deadeye")) a.addTag(a.isCritArrow() ? "ab_deadeye" : still ? "ab_plain" : "ab_moving");
		if (has(p, "fire_arrow") && (state(p).arrows + 1) % 4 == 0) a.igniteForSeconds(100);
		if (has(p, "volley") && ++state(p).arrows % 5 == 0) {
			for (int side : new int[] {-1, 1}) {
				Entity copy = a.getType().create(e.getLevel());
				if (!(copy instanceof AbstractArrow c)) continue;
				c.setOwner(p);
				c.setPos(a.getX(), a.getY(), a.getZ());
				c.setDeltaMovement(a.getDeltaMovement().yRot((float) Math.toRadians(8 * side)));
				c.setBaseDamage(a.getBaseDamage());
				c.setCritArrow(a.isCritArrow());
				c.pickup = AbstractArrow.Pickup.CREATIVE_ONLY;
				c.addTag("ab_volley");
				e.getLevel().addFreshEntity(c);
			}
		}
	}

	// ---------------------------------------------------------------- what the staffs ask

	/** spell power on top of the attribute: Spellweaver while your mana is high */
	static double spellMult(Player p) {
		double m = 1;
		if (has(p, "spellweaver") && p instanceof ServerPlayer sp && sp.getData(Spells.MANA) > Spells.max(p) * 0.8f) m *= 1.12;
		if (has(p, "surge") && p instanceof ServerPlayer sp && sp.getData(Spells.MANA) >= Spells.max(p) * 0.99f) m *= 1.3;
		return m * CurioFx.spellMult(p);   // the Ninth Pyre's fourth spell
	}

	/** an Overload bolt: every sixth */
	static boolean overload(Player p) {
		return has(p, "overload") && ++state(p).bolts % 6 == 0;
	}

	static void blessed(LivingEntity e, long until) {
		BLESSED.put(e.getUUID(), until);
	}
}
