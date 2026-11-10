package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;

import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.EquipmentSlotGroup;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.minecraft.world.item.crafting.Ingredient;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * The gate armour sets. Every dungeon makes four, one per {@link Kind}: a robe for mages, light, medium and
 * heavy. A set's numbers come from its kind and its dungeon's rank; Epic Fight's side (stun armour, weight,
 * which drains stamina and slows swings) is in data/ashbound/capabilities/armors, and the meshes it draws in
 * animmodels/armor (tools/efarmor.py). The sets themselves are listed in /ashbound/gear.json (tools/gear.py).
 */
public final class Armors {
	private Armors() {}

	static final DeferredRegister<ArmorMaterial> MATERIALS = DeferredRegister.create(Registries.ARMOR_MATERIAL, Ashbound.ID);
	static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(Ashbound.ID);
	static final List<DeferredItem<? extends Item>> ALL = new ArrayList<>();

	/**
	 * A full set's armour, toughness and knockback resistance at rank C, and what wearing it does to how you move
	 * (the whole set's share; each piece carries a quarter). Spell power and mana come with the spells.
	 */
	enum Kind {
		ROBE(6, 0, 0, 0.08, 0, 18, SoundEvents.ARMOR_EQUIP_LEATHER, -3),
		LIGHT(10, 0, 0, 0.08, 0.08, 14, SoundEvents.ARMOR_EQUIP_LEATHER, 0),
		MEDIUM(15, 1, 0, 0, 0, 10, SoundEvents.ARMOR_EQUIP_CHAIN, 0),
		HEAVY(20, 3, 0.3, -0.08, -0.05, 9, SoundEvents.ARMOR_EQUIP_NETHERITE, 4);

		final double armour, toughness, knockback, move, attack;
		final int enchant, durability;
		final Holder<SoundEvent> sound;

		Kind(double armour, double toughness, double knockback, double move, double attack, int enchant, Holder<SoundEvent> sound, int durability) {
			this.armour = armour;
			this.toughness = toughness;
			this.knockback = knockback;
			this.move = move;
			this.attack = attack;
			this.enchant = enchant;
			this.sound = sound;
			this.durability = durability;
		}
	}

	/** the stat ladder (docs/DUNGEONS.md): how strong a rank's gear is next to rank C, and how long it lasts */
	private static double scale(char rank) {
		return switch (rank) { case 'F' -> 0.80; case 'E' -> 0.87; case 'D' -> 0.93; case 'B' -> 1.08; case 'A' -> 1.16; case 'S' -> 1.25; default -> 1.0; };
	}

	private static int wear(char rank) {
		return switch (rank) { case 'F' -> 18; case 'E' -> 21; case 'D' -> 24; case 'B' -> 32; case 'A' -> 36; case 'S' -> 40; default -> 28; };
	}

	private static final ArmorItem.Type[] PIECES = {ArmorItem.Type.HELMET, ArmorItem.Type.CHESTPLATE, ArmorItem.Type.LEGGINGS, ArmorItem.Type.BOOTS};
	private static final double[] SHARE = {0.15, 0.40, 0.30, 0.15};

	/** a set of four, named NAME_HELM, NAME_CHEST... after its pieces */
	private static void set(String name, String dungeon, char rank, Kind kind, String helm, String chest, String legs, String boots) {
		set(name, dungeon, rank, kind, helm, chest, legs, boots, null);
	}

	/** colour: a found set's rarity on its pieces' names (null for a dungeon's) */
	private static void set(String name, String dungeon, char rank, Kind kind, String helm, String chest, String legs, String boots,
			WorldArms.Garb found) {
		double x = scale(rank);
		// the class's armour at this rank from tools/balance.py, split over the pieces in whole points
		double[] solved = Balance.armour(kind.name().toLowerCase(java.util.Locale.ROOT), rank);
		double total = solved != null ? solved[0] : kind.armour * x, tough = solved != null ? solved[1] : kind.toughness * x;
		EnumMap<ArmorItem.Type, Integer> defence = new EnumMap<>(ArmorItem.Type.class);
		int sum = 0;
		for (int i = 0; i < 4; i++) {
			int v = Math.max(1, (int) Math.round(total * SHARE[i]));
			defence.put(PIECES[i], v);
			sum += v;
		}
		defence.put(ArmorItem.Type.CHESTPLATE, defence.get(ArmorItem.Type.CHESTPLATE) + Math.max(1, (int) Math.round(total)) - sum);
		DeferredHolder<ArmorMaterial, ArmorMaterial> mat = MATERIALS.register(name, () -> new ArmorMaterial(defence, kind.enchant, kind.sound,
				() -> Ingredient.EMPTY, List.of(new ArmorMaterial.Layer(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, name))), (float) (tough / 4), (float) (kind.knockback / 4)));
		String[] parts = {helm, chest, legs, boots};
		for (int i = 0; i < 4; i++) {
			ArmorItem.Type type = PIECES[i];
			String id = name + "_" + parts[i];
			DeferredItem<Item> it = ITEMS.registerItem(id, p -> {
				p = p.durability(type.getDurability(wear(rank) + kind.durability)).rarity(Rarity.RARE);
				if (found != null)
					p = p.component(DataComponents.ITEM_NAME, Component.translatable("item.ashbound." + id).withStyle(found.tier().colour));
				return new Piece(name, mat, type, kind, p);
			});
			ALL.add(it);
			if (found != null) WorldArms.GARB_ITEMS.put(id, new WorldArms.Found(it, found));
		}
	}

	/** an armour piece that also changes how fast its wearer moves and swings, by its kind */
	static final class Piece extends ArmorItem {
		private final String set;
		private final Kind kind;
		private ItemAttributeModifiers modifiers;

		Piece(String set, Holder<ArmorMaterial> mat, Type type, Kind kind, Properties p) {
			super(mat, type, p);
			this.set = set;
			this.kind = kind;
		}

		@Override
		public ResourceLocation getArmorTexture(ItemStack stack, Entity entity, EquipmentSlot slot, ArmorMaterial.Layer layer, boolean inner) {
			return ArmorFx.sheet(set);
		}

		boolean designed() {
			return ArmorFx.sheet(set) != null;
		}

		@Override
		public ItemAttributeModifiers getDefaultAttributeModifiers() {
			if (modifiers == null) {
				ItemAttributeModifiers m = super.getDefaultAttributeModifiers();
				EquipmentSlotGroup slot = EquipmentSlotGroup.bySlot(getEquipmentSlot());
				ResourceLocation id = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "armour_kind." + getType().getName());
				if (kind.move != 0)
					m = m.withModifierAdded(Attributes.MOVEMENT_SPEED, new AttributeModifier(id, kind.move / 4, AttributeModifier.Operation.ADD_MULTIPLIED_BASE), slot);
				if (kind.attack != 0)
					m = m.withModifierAdded(Attributes.ATTACK_SPEED, new AttributeModifier(id, kind.attack / 4, AttributeModifier.Operation.ADD_MULTIPLIED_BASE), slot);
				if (kind == Kind.ROBE) {
					// a robe's whole set: +15% spell power, +10% mana back
					m = m.withModifierAdded(Spells.SPELL_POWER, new AttributeModifier(id, 0.15 / 4, AttributeModifier.Operation.ADD_VALUE), slot);
					m = m.withModifierAdded(Spells.MANA_REGEN, new AttributeModifier(id, 0.10 / 4, AttributeModifier.Operation.ADD_VALUE), slot);
				}
				modifiers = m;
			}
			return modifiers;
		}
	}

	/** every dungeon's four sets, from /ashbound/gear.json */
	static void all() {
		for (Gear.Dungeon d : Gear.DUNGEONS)
			for (Gear.Set st : d.sets()) {
				List<Gear.Piece> p = st.pieces();
				set(st.id(), d.gate(), d.rank(), Kind.valueOf(st.cls().toUpperCase(java.util.Locale.ROOT)), part(st.id(), p.get(0)),
						part(st.id(), p.get(1)), part(st.id(), p.get(2)), part(st.id(), p.get(3)));
			}
		// the world's found sets (/ashbound/world_armour.json, tools/worldarmour.py): never forged, their rarity on the names
		for (WorldArms.Garb g : WorldArms.GARB)
			set(g.id(), "world", g.rank(), Kind.valueOf(g.cls().toUpperCase(java.util.Locale.ROOT)), g.parts().get(0), g.parts().get(1),
					g.parts().get(2), g.parts().get(3), g);
	}

	private static String part(String set, Gear.Piece p) {
		return p.id().substring(set.length() + 1);
	}
}
