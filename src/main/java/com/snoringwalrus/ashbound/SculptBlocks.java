package com.snoringwalrus.ashbound;

import com.snoringwalrus.ashbound.PropBlock.Sculpt.Fx;
import com.snoringwalrus.ashbound.PropBlock.Sculpt.Use;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.registries.DeferredBlock;

/** The sculpted props (written by tools/sculpt.py: edit that, not this). Placed by the generators, not by hand. */
public final class SculptBlocks {
	private SculptBlocks() {}

	private static DeferredBlock<Block> block(String name, int pieces, int light, Use use, Fx fx, int[] glow, int[] smoke, BlockBehaviour.Properties props) {
		return WorldBlocks.BLOCKS.registerBlock(name, p -> PropBlock.Sculpt.make(p, pieces, light, use, fx, glow, smoke), props);
	}

	/** Loads the class, so its blocks are registered. */
	static void init() {}

	static final DeferredBlock<Block> GREAT_HEARTH = block("great_hearth", 24, 13, Use.SMITHING, Fx.EMBERS, new int[] {0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14}, new int[] {0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> SMITH_ANVIL = block("smith_anvil", 1, 8, Use.ANVIL, Fx.NONE, new int[] {0}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> QUENCH_TROUGH = block("quench_trough", 2, 0, Use.NONE, Fx.STEAM, new int[] {}, new int[] {0, 1},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> GRINDSTONE_WHEEL = block("grindstone_wheel", 4, 0, Use.GRINDSTONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> CRUCIBLE_GANTRY = block("crucible_gantry", 6, 15, Use.NONE, Fx.MOLTEN, new int[] {1, 2, 3}, new int[] {1, 2, 3},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> TRIP_HAMMER = block("trip_hammer", 16, 8, Use.NONE, Fx.EMBERS, new int[] {4}, new int[] {4},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> WEAPON_RACK = block("weapon_rack", 4, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> ARMOUR_STAND = block("armour_stand", 2, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> TOOL_WALL = block("tool_wall", 4, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> COAL_BIN = block("coal_bin", 1, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> ORE_BIN = block("ore_bin", 1, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> INGOT_STACK = block("ingot_stack", 1, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> FORGE_CREST = block("forge_crest", 25, 15, Use.NONE, Fx.NONE, new int[] {7, 11, 12, 13, 16, 17, 18}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> MASTER_ANVIL = block("master_anvil", 12, 15, Use.SMITHING, Fx.EMBERS, new int[] {0, 1, 2, 3, 4, 5, 7, 8, 11}, new int[] {0, 1, 2, 3, 4, 5, 7, 8, 11},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> GREAT_BELLOWS = block("great_bellows", 12, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> MOLTEN_SPOUT = block("molten_spout", 17, 15, Use.NONE, Fx.MOLTEN, new int[] {0, 1, 2, 3, 4, 5, 6, 7, 12, 15}, new int[] {0, 1, 2, 3, 4, 5, 6, 7, 12, 15},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> ORE_CART = block("ore_cart", 2, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> LION_SPOUT = block("lion_spout", 2, 0, Use.NONE, Fx.DRIP, new int[] {}, new int[] {0},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> BATH_BOILER = block("bath_boiler", 12, 8, Use.NONE, Fx.EMBERS, new int[] {0, 1}, new int[] {0, 1},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> BATH_TUB = block("bath_tub", 2, 0, Use.NONE, Fx.STEAM, new int[] {}, new int[] {0, 1},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> TOWEL_BENCH = block("towel_bench", 2, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> STEAM_BRAZIER = block("steam_brazier", 2, 8, Use.NONE, Fx.STEAM, new int[] {0}, new int[] {1},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> BATH_PLANT = block("bath_plant", 2, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> ARCANE_ORRERY = block("arcane_orrery", 17, 15, Use.NONE, Fx.MAGIC, new int[] {9, 13}, new int[] {9, 13},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> CRYSTAL_PYLON = block("crystal_pylon", 3, 13, Use.NONE, Fx.MAGIC, new int[] {0, 1, 2}, new int[] {0, 1, 2},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> CRYSTAL_CROWN = block("crystal_crown", 74, 13, Use.NONE, Fx.MAGIC, new int[] {1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 34, 37, 38, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73}, new int[] {1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 34, 37, 38, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73},
			BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(-1f, 3600000f).sound(SoundType.AMETHYST).noOcclusion());
	static final DeferredBlock<Block> ALCHEMY_TABLE = block("alchemy_table", 4, 8, Use.CRAFTING, Fx.MAGIC, new int[] {0, 1, 3}, new int[] {0, 1},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> ARCANE_LECTERN = block("arcane_lectern", 2, 8, Use.ENCHANTING, Fx.MAGIC, new int[] {1}, new int[] {1},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> BRASS_TELESCOPE = block("brass_telescope", 10, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> CELESTIAL_GLOBE = block("celestial_globe", 2, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> RUNE_CIRCLE = block("rune_circle", 25, 12, Use.NONE, Fx.MAGIC, new int[] {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24}, new int[] {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> RUNE_TARGET = block("rune_target", 2, 8, Use.NONE, Fx.MAGIC, new int[] {1}, new int[] {1},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> SCROLL_SHELF = block("scroll_shelf", 6, 8, Use.NONE, Fx.NONE, new int[] {4}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> ARCANE_BRAZIER = block("arcane_brazier", 2, 8, Use.NONE, Fx.MAGIC, new int[] {0, 1}, new int[] {0, 1},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> HERO_SHIELD = block("hero_shield", 148, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> HERO_HAMMER = block("hero_hammer", 101, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> HERO_BOW = block("hero_bow", 116, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> HERO_BLACKMAGE = block("hero_blackmage", 133, 14, Use.NONE, Fx.EMBERS, new int[] {83, 95, 118, 119, 127, 128}, new int[] {83, 95},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> HERO_PRIESTESS = block("hero_priestess", 118, 15, Use.NONE, Fx.MAGIC, new int[] {93, 97, 113}, new int[] {93, 97, 113},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> HERO_ROGUE = block("hero_rogue", 107, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> HERO_SPEAR = block("hero_spear", 114, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> HERO_SUMMONER = block("hero_summoner", 114, 12, Use.NONE, Fx.MAGIC, new int[] {106, 107, 112, 113}, new int[] {106, 107, 112, 113},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> HERO_PALADIN = block("hero_paladin", 129, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> HERO_AXE = block("hero_axe", 103, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> HERO_FIRST = block("hero_first", 189, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> COLOSSUS_KNIGHT = block("colossus_knight", 353, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> COLOSSUS_MAGE = block("colossus_mage", 387, 13, Use.NONE, Fx.MAGIC, new int[] {359, 363, 364, 371, 375, 376, 386}, new int[] {359, 363, 364, 371, 375, 376, 386},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> CLOCK_FACE = block("clock_face", 81, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> WARDEN_BLADE = block("warden_blade", 190, 15, Use.NONE, Fx.EMBERS, new int[] {13, 14, 15, 30, 38, 47, 54, 62, 70, 76, 81, 86, 91, 96, 101, 106, 111, 117, 132, 147, 152, 166, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187}, new int[] {13, 14, 15, 30, 38, 47, 54, 62, 70, 76, 81, 86, 91, 96, 101, 106, 111, 117, 132, 147, 152, 166, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> GUILD_CREST = block("guild_crest", 16, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> SIGN_GENERAL = block("sign_general", 4, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> SIGN_BAKER = block("sign_baker", 4, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> SIGN_TAILOR = block("sign_tailor", 4, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> SIGN_APOTHECARY = block("sign_apothecary", 4, 9, Use.NONE, Fx.NONE, new int[] {0, 1}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> SIGN_GROCER = block("sign_grocer", 4, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> SIGN_BOOKS = block("sign_books", 4, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> SIGN_CHANDLER = block("sign_chandler", 4, 8, Use.NONE, Fx.NONE, new int[] {2, 3}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> SIGN_FISHMONGER = block("sign_fishmonger", 4, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> GUILD_BOARD = block("guild_board", 60, 8, Use.NONE, Fx.NONE, new int[] {40, 49}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> GUILD_COUNTER = block("guild_counter", 6, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> TRESTLE_TABLE = block("trestle_table", 6, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> GUILD_CHAIR = block("guild_chair", 2, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> ROUND_TABLE = block("round_table", 4, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> TAVERN_BAR = block("tavern_bar", 4, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> KEG_RACK = block("keg_rack", 8, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> BAR_STOOL = block("bar_stool", 1, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> GUILD_CHANDELIER = block("guild_chandelier", 18, 8, Use.NONE, Fx.NONE, new int[] {0, 1, 2, 3, 5, 6, 7, 8}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL).noOcclusion());
	static final DeferredBlock<Block> TROPHY_SKULL = block("trophy_skull", 4, 8, Use.NONE, Fx.EMBERS, new int[] {2, 3}, new int[] {2, 3},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> SCHOOL_DESK = block("school_desk", 1, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> SCHOOL_CHAIR = block("school_chair", 1, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> MASTER_DESK = block("master_desk", 2, 8, Use.NONE, Fx.NONE, new int[] {1}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> RUNE_BOARD = block("rune_board", 6, 8, Use.NONE, Fx.NONE, new int[] {1, 4}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> TOPIARY_POT = block("topiary_pot", 2, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> FLOWER_TUB = block("flower_tub", 1, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD).noOcclusion());
	static final DeferredBlock<Block> ROSE_BUSH = block("rose_bush", 1, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.PLANT).strength(-1f, 3600000f).sound(SoundType.AZALEA).noOcclusion());
	static final DeferredBlock<Block> HYDRANGEA = block("hydrangea", 1, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.PLANT).strength(-1f, 3600000f).sound(SoundType.AZALEA).noOcclusion());
	static final DeferredBlock<Block> COLD_FORGE = block("cold_forge", 205, 0, Use.NONE, Fx.NONE, new int[] {}, new int[] {},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
	static final DeferredBlock<Block> COLD_FORGE_LIT = block("cold_forge_lit", 209, 15, Use.NONE, Fx.EMBERS, new int[] {1, 2, 3, 4, 5, 6, 7, 9, 10, 16, 17, 18, 19, 25, 26, 36, 44, 45, 46, 52, 53, 55, 56, 60, 61, 64, 65, 66, 67, 68, 76, 81, 83, 84, 85, 87, 92, 93, 94, 101, 102, 103, 121, 122, 129, 130, 131, 138, 139, 153, 154, 163, 166, 169, 170, 177, 178, 181, 182, 183, 184, 187, 188, 190, 193, 195, 198, 200, 203}, new int[] {1, 2, 3, 4, 5, 6, 7, 9, 10, 16, 17, 18, 19, 25, 26, 36, 44, 45, 46, 52, 53, 55, 56, 60, 61, 64, 65, 66, 67, 68, 76, 81, 83, 84, 85, 87, 92, 93, 94, 101, 102, 103, 121, 122, 129, 130, 131, 138, 139, 153, 154, 163, 166, 169, 170, 177, 178, 181, 182, 183, 184, 187, 188, 190, 193, 195, 198, 200, 203},
			BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(-1f, 3600000f).sound(SoundType.STONE).noOcclusion());
}
