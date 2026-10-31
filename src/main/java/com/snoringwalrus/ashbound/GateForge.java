package com.snoringwalrus.ashbound;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.BlockHitResult;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * The Gate Forge: an anvil on a quenched furnace where the gates' drops become their gear. Use it to open the forge
 * (ForgeScreen): every dungeon's weapons and armour, each at its cost in that dungeon's common drop, elite drop and
 * the boss's trophy, then upgrades; what comes of it is {@link Smithing}'s.
 */
public final class GateForge {
	private GateForge() {}

	public static final DeferredBlock<Block> BLOCK = WorldBlocks.BLOCKS.registerBlock("gate_forge", Forge::new,
			BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(5f, 1200f).sound(SoundType.ANVIL).noOcclusion()
					.lightLevel(s -> 9));
	public static final DeferredItem<net.minecraft.world.item.BlockItem> ITEM = Weapons.ITEMS.registerSimpleBlockItem(BLOCK);

	static void init() {}

	static class Forge extends PropBlock.Facing {
		Forge(Properties p) {
			super(p, Block.box(0, 0, 0, 16, 15, 16));
		}

		/** a relic in hand: raise its power a tier (CurioFx.upgrade) */
		@Override
		protected net.minecraft.world.ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player,
				net.minecraft.world.InteractionHand hand, BlockHitResult hit) {
			if (!(stack.getItem() instanceof Curios.Curio c) || !c.spec.slot().equals("relic"))
				return net.minecraft.world.ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
			if (player instanceof ServerPlayer p) CurioFx.upgrade(p, stack);
			return net.minecraft.world.ItemInteractionResult.sidedSuccess(level.isClientSide);
		}

		@Override
		protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
			if (player instanceof ServerPlayer p && !Smithing.join(p, pos)) PacketDistributor.sendToPlayer(p, new Net.ForgeOpen(pos));
			return InteractionResult.sidedSuccess(level.isClientSide);
		}
	}

	/** how many of an item the player carries */
	public static int count(Player p, Item it) {
		if (it == null) return 0;
		int n = 0;
		for (ItemStack s : p.getInventory().items) if (s.is(it)) n += s.getCount();
		return n;
	}

	static void take(Player p, Item it, int n) {
		for (ItemStack s : p.getInventory().items) {
			if (n <= 0) return;
			if (s.is(it)) {
				int k = Math.min(n, s.getCount());
				s.shrink(k);
				n -= k;
			}
		}
	}

	static void pay(Player p, Gear.Dungeon d, Gear.Cost c) {
		if (p.isCreative()) return;
		take(p, Gear.item(d.mats()[0]), c.common());
		take(p, Gear.item(d.mats()[1]), c.elite());
		take(p, Gear.item(d.mats()[2]), c.trophy());
	}

	public static boolean affords(Player p, Gear.Dungeon d, Gear.Cost c) {
		if (p.isCreative()) return true;
		return count(p, Gear.item(d.mats()[0])) >= c.common() && count(p, Gear.item(d.mats()[1])) >= c.elite()
				&& count(p, Gear.item(d.mats()[2])) >= c.trophy();
	}

	/** A forge at pos, or a smith there who'll work one for you. */
	private static boolean at(ServerPlayer p, BlockPos pos) {
		return p.level().getBlockState(pos).is(BLOCK.get()) || ColdForge.isLit(p.level().getBlockState(pos))
				|| !p.level().getEntitiesOfClass(Npc.class, new net.minecraft.world.phys.AABB(pos).inflate(4), GateForge::smith).isEmpty();
	}

	public static boolean smith(Npc n) {
		return n.kindId().equals("forgemaster") || (n.is("smith") && n.is("dwarf"));
	}

	/** Opens the forge for you at a smith's side (Talk). */
	static void open(ServerPlayer p, Npc smith) {
		PacketDistributor.sendToPlayer(p, new Net.ForgeOpen(smith.blockPosition()));
	}

	static void onCraft(Net.ForgeCraft m, ServerPlayer p) {
		if (at(p, m.pos()) && p.distanceToSqr(m.pos().getCenter()) <= 64) Smithing.request(p, m.pos(), m.job(), m.embers());
	}
}
