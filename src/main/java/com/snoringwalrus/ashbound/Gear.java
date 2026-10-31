package com.snoringwalrus.ashbound;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.EquipmentSlotGroup;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.ShieldItem;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tiers;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * Every dungeon's gear, from /ashbound/gear.json (tools/gear.py): its three drops (common, elite, the boss's
 * trophy), its ten forged weapons and six boss weapons, its four armour sets (registered by {@link Armors}), and
 * which of its monsters are common, elite, casters and the boss ({@link GateLoot}). The Gate Forge's recipes are
 * the forged weapons and the armour pieces at their cost in the three drops.
 */
public final class Gear {
	private Gear() {}

	public record Cost(int common, int elite, int trophy) {}

	public record Weapon(String id, String name, String kind, char rank, boolean boss, Cost cost, double damage, double speed) {
		public boolean staff() {
			return kind.equals("black") || kind.equals("white") || kind.equals("summon");
		}
	}

	public record Piece(String id, String name, String slot, Cost cost) {}

	public record Set(String id, String cls, List<Piece> pieces) {}

	/** One thing the forge makes: the item's id, its cost, and its tab ("weapon", or the armour class). */
	public record Recipe(String id, Cost cost, String tab) {}

	public record Dungeon(String gate, char rank, String title, String element, int colour, String boss, String elite,
			List<String> mobs, List<String> casters, String summon, String[] mats, List<Weapon> weapons, List<Set> sets,
			List<Recipe> recipes) {
		public List<Weapon> bossWeapons() {
			return weapons.stream().filter(Weapon::boss).toList();
		}
	}

	// the colour of each dungeon's spells and sparks (set before DUNGEONS loads, which reads it; the later ones carry their own in gear.json)
	private static final Map<String, Integer> COLOURS = Map.of("cellar", 0x9ab040, "gallows", 0xe07a2a, "rotwood", 0x8ad04a,
			"crypt", 0xffd27a, "plague", 0xe8f4c8, "temple", 0x7ad0ff, "ossuary", 0x4ae68a, "foundry", 0xff6a1a,
			"frost", 0xbfe8ff, "silk", 0xc79aff);

	public static final List<Dungeon> DUNGEONS = load();
	static final Map<String, DeferredItem<Item>> ITEMS = new LinkedHashMap<>();
	static final List<DeferredItem<Item>> MATS = new ArrayList<>(), WEAPONS = new ArrayList<>();
	static final Map<String, Weapon> WEAPON = new HashMap<>();

	public static double scale(char rank) {
		return switch (rank) { case 'F' -> 0.8; case 'E' -> 0.864; case 'D' -> 0.933; case 'B' -> 1.088; case 'A' -> 1.175; case 'S' -> 1.269; default -> 1.008; };
	}

	private static Cost cost(JsonObject o) {
		if (o == null) return new Cost(0, 0, 0);
		return new Cost(o.get("common").getAsInt(), o.get("elite").getAsInt(), o.get("trophy").getAsInt());
	}

	private static List<String> strings(JsonElement e) {
		List<String> out = new ArrayList<>();
		e.getAsJsonArray().forEach(s -> out.add(s.getAsString()));
		return out;
	}

	private static List<Dungeon> load() {
		List<Dungeon> out = new ArrayList<>();
		try (InputStream in = Gear.class.getResourceAsStream("/ashbound/gear.json")) {
			if (in == null) return out;
			for (JsonElement el : JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonArray()) {
				JsonObject g = el.getAsJsonObject();
				String[] mats = new String[3];
				int i = 0;
				for (JsonElement m : g.getAsJsonArray("mats")) mats[i++] = m.getAsJsonObject().get("id").getAsString();
				List<Weapon> weapons = new ArrayList<>();
				List<Recipe> recipes = new ArrayList<>();
				for (JsonElement we : g.getAsJsonArray("weapons")) {
					JsonObject w = we.getAsJsonObject();
					Weapon wp = new Weapon(w.get("id").getAsString(), w.get("name").getAsString(), w.get("kind").getAsString(),
							w.get("rank").getAsString().charAt(0), w.get("boss").getAsBoolean(), cost(w.getAsJsonObject("cost")),
							w.has("damage") ? w.get("damage").getAsDouble() : 0, w.has("speed") ? w.get("speed").getAsDouble() : 0);
					weapons.add(wp);
					if (!wp.boss()) recipes.add(new Recipe(wp.id(), wp.cost(), "weapon"));
				}
				List<Set> sets = new ArrayList<>();
				for (JsonElement se : g.getAsJsonArray("sets")) {
					JsonObject s = se.getAsJsonObject();
					List<Piece> pieces = new ArrayList<>();
					for (JsonElement pe : s.getAsJsonArray("pieces")) {
						JsonObject p = pe.getAsJsonObject();
						Piece pc = new Piece(p.get("id").getAsString(), p.get("name").getAsString(), p.get("slot").getAsString(), cost(p.getAsJsonObject("cost")));
						pieces.add(pc);
						recipes.add(new Recipe(pc.id(), pc.cost(), s.get("cls").getAsString()));
					}
					sets.add(new Set(s.get("id").getAsString(), s.get("cls").getAsString(), pieces));
				}
				String gate = g.get("gate").getAsString();
				out.add(new Dungeon(gate, g.get("rank").getAsString().charAt(0), g.get("title").getAsString(), g.get("element").getAsString(),
						g.has("colour") ? g.get("colour").getAsInt() : COLOURS.getOrDefault(gate, 0xffffff), g.get("boss").getAsString(), g.get("elite").getAsString(), strings(g.get("mobs")),
						strings(g.get("casters")), g.get("summon").getAsString(), mats, weapons, sets, recipes));
			}
		} catch (Exception e) {
			Ashbound.LOG.error("gear not loaded", e);
		}
		return out;
	}

	public static Dungeon of(String gate) {
		for (Dungeon d : DUNGEONS) if (d.gate().equals(gate)) return d;
		return null;
	}

	/** Our item by id (the forge, the loot), or null. */
	public static Item item(String id) {
		DeferredItem<Item> d = ITEMS.get(id);
		if (d != null) return d.get();
		var key = net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(Ashbound.ID, id);
		return BuiltInRegistries.ITEM.containsKey(key) ? BuiltInRegistries.ITEM.get(key) : null;
	}

	private static Rarity rarity(boolean boss) {
		return boss ? Rarity.EPIC : Rarity.RARE;
	}

	/** Registers the drops and the weapons (the armour is {@link Armors}'). */
	static void init() {
		for (Dungeon d : DUNGEONS) {
			Rarity[] rar = {Rarity.UNCOMMON, Rarity.RARE, Rarity.EPIC};
			for (int i = 0; i < 3; i++) {
				Rarity r = rar[i];
				String id = d.mats()[i];
				DeferredItem<Item> it = Weapons.ITEMS.registerItem(id, p -> new Item(p.rarity(r).stacksTo(r == Rarity.EPIC ? 16 : 64)));
				ITEMS.put(id, it);
				MATS.add(it);
			}
			for (Weapon w : d.weapons()) {
				WEAPON.put(w.id(), w);
				DeferredItem<Item> it = Weapons.ITEMS.registerItem(w.id(), p -> weapon(w, p));
				ITEMS.put(w.id(), it);
				WEAPONS.add(it);
			}
		}
		// the forgemaster's plain staffs, so a mage has something before their first gate
		for (String school : List.of("black", "white", "summon")) {
			Weapon w = new Weapon("apprentice_" + school + "_staff", "Apprentice's Staff", school, 'F', false, new Cost(0, 0, 0), 0, 0);
			WEAPON.put(w.id(), w);
			DeferredItem<Item> it = Weapons.ITEMS.registerItem(w.id(), p -> new Spells.Staff(w, p.stacksTo(1).durability(400)));
			ITEMS.put(w.id(), it);
			WEAPONS.add(it);
		}
		NeoForge.EVENT_BUS.addListener((EntityJoinLevelEvent e) -> {
			if (!e.getLevel().isClientSide && e.getEntity() instanceof AbstractArrow a && a.getOwner() instanceof Player p) bowDamage(a, p);
		});
	}

	static Item weapon(Weapon w, Item.Properties p) {
		p = p.rarity(rarity(w.boss())).fireResistant();
		int wear = (int) (1500 * scale(w.rank()) * (w.boss() ? 1.4 : 1));
		switch (w.kind()) {
			case "shield" -> {
				return new ShieldItem(p.durability(wear));
			}
			case "bow" -> {
				return new BowItem(p.durability(wear * 2 / 3));
			}
			case "black", "white", "summon" -> {
				return new Spells.Staff(w, p.stacksTo(1));
			}
			default -> {
				ItemAttributeModifiers stats = ItemAttributeModifiers.builder()
						.add(Attributes.ATTACK_DAMAGE, new AttributeModifier(Item.BASE_ATTACK_DAMAGE_ID, w.damage() - 1, AttributeModifier.Operation.ADD_VALUE),
								EquipmentSlotGroup.MAINHAND)
						.add(Attributes.ATTACK_SPEED, new AttributeModifier(Item.BASE_ATTACK_SPEED_ID, w.speed() - 4, AttributeModifier.Operation.ADD_VALUE),
								EquipmentSlotGroup.MAINHAND)
						.build();
				return new SwordItem(Tiers.DIAMOND, p.attributes(stats).durability(wear)) {
					@Override
					public void appendHoverText(ItemStack stack, TooltipContext ctx, List<Component> lines, TooltipFlag flag) {
						tooltip(w, lines);
					}
				};
			}
		}
	}

	/** where a weapon comes from, under its name */
	static void tooltip(Weapon w, List<Component> lines) {
		for (Dungeon d : DUNGEONS)
			if (d.weapons().contains(w)) {
				lines.add(Component.literal((w.boss() ? "Boss weapon, " : "Rank " + w.rank() + ", ") + d.title())
						.withStyle(w.boss() ? net.minecraft.ChatFormatting.GOLD : net.minecraft.ChatFormatting.GRAY));
				return;
			}
	}

	/** an arrow off one of our bows hits as hard as the bow's rank */
	private static void bowDamage(AbstractArrow a, Player p) {
		a.setBaseDamage(a.getBaseDamage() * bowPower(p));
	}

	/** what the bow in hand does to an arrow's damage */
	static double bowPower(Player p) {
		for (ItemStack s : List.of(p.getMainHandItem(), p.getOffhandItem())) {
			Weapon w = WEAPON.get(BuiltInRegistries.ITEM.getKey(s.getItem()).getPath());
			if (w != null && w.kind().equals("bow") && BuiltInRegistries.ITEM.getKey(s.getItem()).getNamespace().equals(Ashbound.ID))
				return 2.3 * scale(w.rank()) * (w.boss() ? 1.1 : 1) * Smithing.mult(s);
		}
		return 1;
	}

	/** the bows and shields, for their drawn and raised looks (client) */
	public static List<Item> ofKind(String kind) {
		List<Item> out = new ArrayList<>();
		for (Dungeon d : DUNGEONS)
			for (Weapon w : d.weapons())
				if (w.kind().equals(kind) && ITEMS.containsKey(w.id())) out.add(ITEMS.get(w.id()).get());
		for (WorldArms.Arm a : WorldArms.ARMS)
			if (a.kind().equals(kind) && ITEMS.containsKey(a.id())) out.add(ITEMS.get(a.id()).get());
		for (Weapon w : Joined.ALL) if (w.kind().equals(kind)) out.add(ITEMS.get(w.id()).get());
		return out;
	}
}
