package com.snoringwalrus.ashbound;

import net.neoforged.bus.api.IEventBus;
import yesman.epicfight.api.animation.LivingMotions;
import yesman.epicfight.api.ex_cap.data.Moveset;
import yesman.epicfight.gameasset.Animations;
import yesman.epicfight.gameasset.ColliderPreset;
import net.minecraft.world.entity.player.Player;
import yesman.epicfight.api.ex_cap.provider.ProviderConditional;
import yesman.epicfight.registry.deferred.ItemPresetRegister;
import yesman.epicfight.registry.deferred.ProviderConditionalRegister;
import yesman.epicfight.registry.deferred.holders.DeferredConditional;
import yesman.epicfight.registry.deferred.MovesetRegister;
import yesman.epicfight.registry.deferred.holders.DeferredMoveset;
import yesman.epicfight.registry.deferred.holders.DeferredWeapon;
import yesman.epicfight.registry.entries.EpicFightProviderConditionals;
import yesman.epicfight.registry.entries.EpicFightSkills;
import yesman.epicfight.registry.entries.EpicFightSounds;
import yesman.epicfight.world.capabilities.item.CapabilityItem;
import yesman.epicfight.world.capabilities.item.WeaponCapability;

/**
 * Our own weapon types for Epic Fight (a capability file's "type": "ashbound:..."). The greatsword fights like Epic
 * Fight's, but between swings it's held up in front in both hands (the longsword's stance): ours are thick 3D blades,
 * and resting one on the shoulder the way Epic Fight's flat one rests sinks half of it into the arm. With Titan's
 * Grip (the tree's two-hander keystone) and a second one in the off hand it's held and swung as a pair.
 */
public final class Movesets {
	private Movesets() {}

	static final MovesetRegister MOVESETS = MovesetRegister.create(Ashbound.ID);
	static final ItemPresetRegister PRESETS = ItemPresetRegister.create(Ashbound.ID);
	static final ProviderConditionalRegister CONDITIONALS = ProviderConditionalRegister.create(Ashbound.ID);

	/** Titan's Grip: a two-hander in each hand, swung together (the dual swords' moves, our heavy blades) */
	static final DeferredMoveset GREATSWORD_DUAL = MOVESETS.registerMoveset("greatsword_dual", () -> Moveset.builder()
			.addLivingMotionsRecursive(Animations.BIPED_HOLD_DUAL_WEAPON,
					LivingMotions.IDLE, LivingMotions.JUMP, LivingMotions.KNEEL, LivingMotions.SNEAK,
					LivingMotions.SWIM, LivingMotions.FLY, LivingMotions.CREATIVE_FLY, LivingMotions.CREATIVE_IDLE, LivingMotions.WALK, LivingMotions.CHASE)
			.addLivingMotionModifier(LivingMotions.RUN, Animations.BIPED_RUN_DUAL)
			.addLivingMotionModifier(LivingMotions.BLOCK, Animations.SWORD_DUAL_GUARD)
			.addComboAttacks(Animations.SWORD_DUAL_AUTO1, Animations.SWORD_DUAL_AUTO2, Animations.SWORD_DUAL_AUTO3, Animations.SWORD_DUAL_DASH,
					Animations.SWORD_DUAL_AIR_SLASH)
			.addInnateSkill((stack, player) -> EpicFightSkills.DANCING_EDGE.get()));

	static final DeferredConditional TITAN_GRIP = CONDITIONALS.registerConditional("titan_grip", () -> ProviderConditional.createCustom(
			CapabilityItem.Styles.ONE_HAND, patch -> patch.getOriginal() instanceof Player p && Passives.titanGrip(p)
					&& Passives.kindOf(p.getOffhandItem()).equals("twohander"), true));

	static final DeferredMoveset GREATSWORD_2H = MOVESETS.registerMoveset("greatsword_2h", () -> Moveset.builder()
			.addLivingMotionsRecursive(Animations.BIPED_HOLD_LONGSWORD,
					LivingMotions.IDLE, LivingMotions.JUMP, LivingMotions.KNEEL, LivingMotions.SNEAK,
					LivingMotions.SWIM, LivingMotions.FLY, LivingMotions.CREATIVE_FLY, LivingMotions.CREATIVE_IDLE)
			.addLivingMotionsRecursive(Animations.BIPED_WALK_LONGSWORD, LivingMotions.WALK, LivingMotions.CHASE)
			.addLivingMotionModifier(LivingMotions.RUN, Animations.BIPED_RUN_LONGSWORD)
			.addLivingMotionModifier(LivingMotions.BLOCK, Animations.GREATSWORD_GUARD)
			.addComboAttacks(Animations.GREATSWORD_AUTO1, Animations.GREATSWORD_AUTO2, Animations.GREATSWORD_DASH, Animations.GREATSWORD_AIR_SLASH)
			.addInnateSkill((stack, player) -> EpicFightSkills.STEEL_WHIRLWIND.get()));

	static final DeferredWeapon GREATSWORD = PRESETS.registerWeapon("greatsword", () -> WeaponCapability.builder()
			.category(CapabilityItem.WeaponCategories.GREATSWORD)
			.collider(ColliderPreset.GREATSWORD)
			.swingSound(EpicFightSounds.WHOOSH_BIG)
			.hitSound(EpicFightSounds.BLADE_HIT)
			.canBePlacedOffhand(true)
			.reach(1.0F)
			.setTierValues(0, 0d, 0.0, 0.0)
			.addMoveset(CapabilityItem.Styles.TWO_HAND, GREATSWORD_2H)
			.addMoveset(CapabilityItem.Styles.ONE_HAND, GREATSWORD_DUAL)
			.addConditionals(TITAN_GRIP, EpicFightProviderConditionals.DEFAULT_2H_WIELD_STYLE));

	/** A staff in the hands: a spear's stance and swings, no weapon skill. Not the spear's category, whose guard would take the right click that casts. */
	static final DeferredMoveset STAFF_MOVES = MOVESETS.registerMoveset("staff", () -> Moveset.builder()
			.addLivingMotionsRecursive(Animations.BIPED_HOLD_SPEAR,
					LivingMotions.IDLE, LivingMotions.JUMP, LivingMotions.KNEEL, LivingMotions.SNEAK,
					LivingMotions.SWIM, LivingMotions.FLY, LivingMotions.CREATIVE_FLY, LivingMotions.CREATIVE_IDLE)
			.addLivingMotionsRecursive(Animations.BIPED_WALK_SPEAR, LivingMotions.WALK, LivingMotions.CHASE)
			.addLivingMotionModifier(LivingMotions.RUN, Animations.BIPED_RUN_SPEAR)
			.addComboAttacks(Animations.SPEAR_TWOHAND_AUTO1, Animations.SPEAR_TWOHAND_AUTO2, Animations.SPEAR_DASH, Animations.SPEAR_TWOHAND_AIR_SLASH));

	static final DeferredWeapon STAFF = PRESETS.registerWeapon("staff", () -> WeaponCapability.builder()
			.category(CapabilityItem.WeaponCategories.TRIDENT)
			.collider(ColliderPreset.SPEAR)
			.swingSound(EpicFightSounds.WHOOSH)
			.hitSound(EpicFightSounds.BLUNT_HIT)
			.canBePlacedOffhand(false)
			.setTierValues(0, 0d, 0.0, 0.0)
			.addMoveset(CapabilityItem.Styles.TWO_HAND, STAFF_MOVES)
			.addMoveset(CapabilityItem.Styles.ONE_HAND, STAFF_MOVES)
			.addConditionals(EpicFightProviderConditionals.DEFAULT_2H_WIELD_STYLE));

	static void register(IEventBus bus) {
		CONDITIONALS.register(bus);
		MOVESETS.register(bus);
		PRESETS.register(bus);
	}
}
