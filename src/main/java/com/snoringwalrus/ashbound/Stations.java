package com.snoringwalrus.ashbound;

import java.util.List;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.BlockHitResult;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * The Trades' own stations (pass 16), Minecraft-style block models from tools/stationprops.py: the Cook's Fire, the Brewer's Cask and
 * the Alchemist's Bench. Any mod's stove, keg or stand still works by sneaking with an empty hand (up to Rare); these open with a plain
 * use, make up to Epic and keep the make-again list ({@link Trades.Bench#tier} 1). Crafted (data/ashbound/recipe) or bought (the
 * innkeeper, the quartermaster, the alchemist). The house's stations are tier 2.
 */
public final class Stations {
	private Stations() {}

	public static final DeferredBlock<Block> COOKS_FIRE = station("cooks_fire", Trades.Kind.MEAL, MapColor.STONE, SoundType.STONE, 12);
	public static final DeferredBlock<Block> BREWERS_CASK = station("brewers_cask", Trades.Kind.BREW, MapColor.WOOD, SoundType.WOOD, 0);
	public static final DeferredBlock<Block> ALCHEMISTS_BENCH = station("alchemists_bench", Trades.Kind.ELIXIR, MapColor.WOOD, SoundType.WOOD, 7);
	public static final List<DeferredItem<net.minecraft.world.item.BlockItem>> ITEMS = List.of(
			Weapons.ITEMS.registerSimpleBlockItem(COOKS_FIRE), Weapons.ITEMS.registerSimpleBlockItem(BREWERS_CASK),
			Weapons.ITEMS.registerSimpleBlockItem(ALCHEMISTS_BENCH));

	/** The manor's own (tier 2: no cap, the better of two rolls). Fixed in the house: unbreakable, no item, nothing dropped. */
	public static final DeferredBlock<Block> HOME_COOKS_FIRE = home("cooks_fire", Trades.Kind.MEAL, MapColor.STONE, SoundType.STONE, 12);
	public static final DeferredBlock<Block> HOME_BREWERS_CASK = home("brewers_cask", Trades.Kind.BREW, MapColor.WOOD, SoundType.WOOD, 0);
	public static final DeferredBlock<Block> HOME_ALCHEMISTS_BENCH = home("alchemists_bench", Trades.Kind.ELIXIR, MapColor.WOOD, SoundType.WOOD, 7);

	/** The manor's footprint in the city file's own coordinates (tools/capital_home.py: the hall, its wing, the cellar). */
	static final int[] MANOR = {-238, 5, -120, -215, 30, -104};
	/** The whole homestead (house, terraces, fields): no townsfolk live or sit there. */
	static final int[] HOMESTEAD = {-305, -30, -135, -200, 60, -75};
	/** Given at the end of Act II. */
	static final String MANOR_FLAG = "ch:act2_drowned_fire";

	static void init() {
		net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(Stations::door);
	}

	static boolean ownsManor(ServerPlayer p) {
		return Coins.flag(p, MANOR_FLAG) || p.isCreative();
	}

	static boolean inManor(Level level, BlockPos pos) {
		Capital.Site s = Capital.site;
		if (s == null || level.dimension() != Level.OVERWORLD) return false;
		int x = pos.getX() - s.x, y = pos.getY() - s.floor, z = pos.getZ() - s.z;
		return x >= MANOR[0] && x <= MANOR[3] && y >= MANOR[1] && y <= MANOR[4] && z >= MANOR[2] && z <= MANOR[5];
	}

	static boolean inHomestead(Level level, BlockPos pos) {
		Capital.Site s = Capital.site;
		if (s == null || level.dimension() != Level.OVERWORLD) return false;
		int x = pos.getX() - s.x, y = pos.getY() - s.floor, z = pos.getZ() - s.z;
		return x >= HOMESTEAD[0] && x <= HOMESTEAD[3] && y >= HOMESTEAD[1] && y <= HOMESTEAD[4] && z >= HOMESTEAD[2] && z <= HOMESTEAD[5];
	}

	static void locked(ServerPlayer p) {
		p.displayClientMessage(net.minecraft.network.chat.Component.literal(
				"The manor is locked. The city gives it to the one who finishes The Five Fires II.").withStyle(net.minecraft.ChatFormatting.GOLD), true);
	}

	/** The manor's doors stay shut until it is the player's. */
	private static void door(net.neoforged.neoforge.event.entity.player.PlayerInteractEvent.RightClickBlock e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || !(e.getLevel().getBlockState(e.getPos()).getBlock() instanceof net.minecraft.world.level.block.DoorBlock)
				|| !inManor(e.getLevel(), e.getPos()) || ownsManor(p)) return;
		e.setCanceled(true);
		locked(p);
	}

	private static DeferredBlock<Block> home(String id, Trades.Kind kind, MapColor colour, SoundType sound, int light) {
		return WorldBlocks.BLOCKS.registerBlock("home_" + id, p -> new Station(p, kind, 2),
				BlockBehaviour.Properties.of().mapColor(colour).strength(-1.0f, 3600000.0f).sound(sound).noOcclusion().noLootTable()
						.lightLevel(s -> light));
	}

	private static DeferredBlock<Block> station(String id, Trades.Kind kind, MapColor colour, SoundType sound, int light) {
		return WorldBlocks.BLOCKS.registerBlock(id, p -> new Station(p, kind, 1),
				BlockBehaviour.Properties.of().mapColor(colour).strength(2.5f).sound(sound).noOcclusion().lightLevel(s -> light));
	}

	public static class Station extends PropBlock.Facing {
		public final Trades.Kind kind;
		public final int tier;

		Station(Properties p, Trades.Kind kind, int tier) {
			super(p, Block.box(0, 0, 0, 16, 16, 16));
			this.kind = kind;
			this.tier = tier;
		}

		@Override
		protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
			if (player instanceof ServerPlayer p) {
				if (tier >= 2 && !ownsManor(p)) locked(p);
				else Trades.open(p, kind, tier, pos);
			}
			return InteractionResult.sidedSuccess(level.isClientSide);
		}
	}
}
