package com.snoringwalrus.ashbound;

import java.util.List;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemStack;

/**
 * Strangers at the modpack's ruins. The first time someone walks into a place, there may be someone there before them: an
 * adventurer who wants the place cleared and will pay for it out of their pack ({@link Errands}), or a peddler working the road
 * with something to sell. The world remembers who's met where, so a place gets its one chance.
 */
final class Wayfarers {
	private Wayfarers() {}

	static final String TAG = "ashbound_wayfarer";
	private static final float CHANCE = 0.6f, PEDDLER = 0.3f;
	private static final List<String> WARES = List.of("trade_general", "alchemist", "trade_smith", "trade_books");
	/** what a wayfarer's pack gives: the odds of embers, and of one of the world's weapons, of a rank near yours */
	private static final float EMBERS = 0.5f, ARM = 0.25f;
	private static final String RANKS = "FEDCBAS";

	static void visit(ServerLevel level, ServerPlayer p, Haunts.Haunt h) {
		Haunts.State st = Haunts.State.get(level);
		if (st.met.contains(h.key())) return;
		RandomSource r = level.getRandom();
		BlockPos at = null;
		if (RandomSource.create(level.getSeed() ^ h.key().hashCode()).nextFloat() < CHANCE) {
			at = Haunts.spot(level, p, h, 2, 0);
			if (at == null) return;   // nowhere for them to stand right now: look again
		}
		st.met.add(h.key());
		st.setDirty();
		if (at == null) return;
		boolean selling = r.nextFloat() < PEDDLER;
		Npc n = Talk.spawn(level, selling ? "@townsfolk" : "@adventurer", selling ? WARES.get(r.nextInt(WARES.size())) : "", "stand", at.getX() + 0.5, at.getY(), at.getZ() + 0.5, r.nextFloat() * 360f);
		if (n != null) n.addTag(TAG);
	}

	static boolean is(Npc n) {
		return n.getTags().contains(TAG);
	}

	/** Out of their pack. */
	static ItemStack find(ServerPlayer p) {
		RandomSource r = p.getRandom();
		float roll = r.nextFloat();
		if (roll < EMBERS) return new ItemStack(Smithing.TEMPER.get(), 1 + r.nextInt(2));
		if (roll < EMBERS + ARM) {
			int most = Math.min(RANKS.length() - 1, Gates.home(p) + 1);
			List<WorldArms.Arm> can = WorldArms.ARMS.stream().filter(a -> a.weapon() != null && RANKS.indexOf(a.weapon().rank()) <= most).toList();
			if (!can.isEmpty()) return new ItemStack(Gear.item(can.get(r.nextInt(can.size())).id()));
		}
		return new ItemStack(net.minecraft.world.item.Items.GOLDEN_APPLE, 1 + r.nextInt(2));
	}
}
