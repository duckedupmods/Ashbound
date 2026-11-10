package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.EnumSet;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.navigation.GroundPathNavigation;
import net.minecraft.world.level.pathfinder.PathFinder;
import net.minecraft.world.level.pathfinder.PathType;
import net.minecraft.world.level.pathfinder.PathfindingContext;
import net.minecraft.world.level.pathfinder.WalkNodeEvaluator;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.util.DefaultRandomPos;
import net.minecraft.world.entity.ai.util.LandRandomPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;
import net.minecraft.world.phys.Vec3;
import yesman.epicfight.api.animation.types.StaticAnimation;
import yesman.epicfight.api.asset.AssetAccessor;
import yesman.epicfight.gameasset.Animations;
import yesman.epicfight.world.capabilities.EpicFightCapabilities;
import yesman.epicfight.world.capabilities.entitypatch.LivingEntityPatch;

/**
 * How the townsfolk spend their day: taking a seat on the benches and chairs round them, stopping to chat with
 * whoever they meet (waving hello, laughing, throwing up their hands, Epic Fight's own emotes), the children playing
 * tag, everyone else wandering their streets. Each is a goal on Npc; two chatting or playing are tied by a field
 * on each, so either breaking off ends it for both.
 */
final class NpcLife {
	/** Every `every` ticks (even), on a tick this NPC's goals really run: a mob's selector and most goal ticks take
	 * turns by tickCount + id, so plain tickCount % 10 never lands for an NPC with an odd id. */
	static boolean beat(Npc n, int every) {
		return (n.tickCount + n.getId()) % every == 0;
	}

	private NpcLife() {}

	static final float WALK = 0.55f, RUN = 0.95f;

	/** Play one of Epic Fight's clips on them, seen by everyone round. */
	static void gesture(Npc n, AssetAccessor<? extends StaticAnimation> clip) {
		LivingEntityPatch<?> p = EpicFightCapabilities.getEntityPatch(n, LivingEntityPatch.class);
		if (p != null) p.playAnimationSynchronized(clip, 0f);
	}

	// ---------------------------------------------------------------- taking a seat

	/** What can be sat on, and how high its seat is (models/block/*: the bench's plank, the chair's cushion). */
	static final Map<String, Double> SEATS = Map.of("bench", 0.44, "guild_chair", 0.56, "towel_bench", 0.5, "bar_stool", 0.75, "school_chair", 0.53);
	/** Seats somebody's on or making for (block positions; every level shares it, the city's all in one). */
	static final Set<Long> TAKEN = new HashSet<>();
	/** How far under a seat's top they're stood: the sit (NpcPatch.SIT) holds the hips 0.72 over the feet, the
	 * seat ~0.08 under the hips; the feet come out 0.44 under the seat, on the floor from a bench. */
	static final double SIT_DROP = 0.64;

	static double seatTop(BlockState st) {
		var key = BuiltInRegistries.BLOCK.getKey(st.getBlock());
		if (!key.getNamespace().equals(Ashbound.ID)) return -1;
		Double h = SEATS.get(key.getPath());
		if (h == null) return -1;
		Property<?> piece = st.getBlock().getStateDefinition().getProperty("piece");
		if (piece != null && !st.getValue(piece).equals(0)) return -1;      // a chair's back, the towels' rack
		return h;
	}

	static Direction facing(BlockState st) {
		Property<?> f = st.getBlock().getStateDefinition().getProperty("facing");
		return f != null && st.getValue(f) instanceof Direction d ? d : Direction.NORTH;
	}

	/** The nearest free seat within r of `at` with room over it, or null. */
	static BlockPos findSeat(Level level, BlockPos at, int r) {
		BlockPos best = null;
		double bestD = Double.MAX_VALUE;
		for (BlockPos p : BlockPos.betweenClosed(at.offset(-r, -2, -r), at.offset(r, 2, r))) {
			if (TAKEN.contains(p.asLong()) || Stations.inHomestead(level, p)) continue;
			BlockState st = level.getBlockState(p);
			BlockState over = level.getBlockState(p.above());
			if (seatTop(st) < 0 || !(over.is(st.getBlock()) || over.getCollisionShape(level, p.above()).isEmpty())) continue;
			double d = p.distSqr(at);
			if (d < bestD) {
				bestD = d;
				best = p.immutable();
			}
		}
		return best;
	}

	static final class Sit extends Goal {
		final Npc n;
		BlockPos target;
		int left, tries, next;

		Sit(Npc n) {
			this.n = n;
			setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK, Flag.JUMP));
		}

		@Override
		public boolean canUse() {
			if (!n.free() || n.tickCount < next) return false;
			int r;
			switch (n.mode) {
				case "sit" -> {
					if (!beat(n, 10)) return false;
					r = 3;
				}
				case "stroll", "errand" -> {
					if (n.getRandom().nextInt(600) != 0) return false;
					r = 10;
				}
				default -> {
					return false;
				}
			}
			target = findSeat(n.level(), n.mode.equals("sit") && n.home != null ? n.home : n.blockPosition(), r);
			if (target == null) {
				next = n.tickCount + 200;
				return false;
			}
			return true;
		}

		@Override
		public void start() {
			TAKEN.add(target.asLong());
			n.going = target;
			tries = 0;
			left = n.mode.equals("sit") ? 12000 + n.getRandom().nextInt(12000) : 500 + n.getRandom().nextInt(1000);
			walk();
		}

		private void walk() {
			BlockPos front = floorBeside(n.level(), target);
			if (front == null) front = target;
			n.getNavigation().moveTo(front.getX() + 0.5, front.getY(), front.getZ() + 0.5, WALK);
		}

		@Override
		public boolean canContinueToUse() {
			return target != null && left > 0 && seatTop(n.level().getBlockState(target)) >= 0;
		}

		@Override
		public void tick() {
			if (n.seat != null) {
				if (n.talkingTo == null) left--;
				return;
			}
			double dx = n.getX() - (target.getX() + 0.5), dz = n.getZ() - (target.getZ() + 0.5);
			double d = dx * dx + dz * dz;
			if (d < 2.6 || (n.getNavigation().isDone() && d < 6)) {
				sitDown(n, target);
			} else if (n.getNavigation().isDone() && ++tries > 3) {
				left = 0;
			} else if (n.getNavigation().isDone()) {
				walk();
			}
		}

		@Override
		public void stop() {
			standUp(n);
			if (target != null) TAKEN.remove(target.asLong());
			target = null;
			n.going = null;
			next = n.tickCount + (n.mode.equals("sit") ? 40 + n.getRandom().nextInt(120) : 1200);
		}

		static void sitDown(Npc n, BlockPos at) {
			BlockState st = n.level().getBlockState(at);
			n.getNavigation().stop();
			n.seat = at;
			n.seatTop = at.getY() + seatTop(st);
			n.seatYaw = facing(st).toYRot();
			n.setYHeadRot(n.seatYaw);
			n.setAct(Npc.POSE_SIT);
			hold(n);
		}

		/** Kept on their seat: still, facing out from its back. */
		static void hold(Npc n) {
			n.noPhysics = true;
			n.setNoGravity(true);
			n.setDeltaMovement(Vec3.ZERO);
			n.setPos(n.seat.getX() + 0.5, n.seatTop - SIT_DROP, n.seat.getZ() + 0.5);
			n.setYRot(n.seatYaw);
			n.yBodyRot = n.seatYaw;
			n.getNavigation().stop();
		}

		static void standUp(Npc n) {
			if (n.seat == null) return;
			BlockPos at = n.seat;
			n.seat = null;
			n.noPhysics = false;
			n.setNoGravity(false);
			n.setAct(Npc.POSE_NONE);
			Level level = n.level();
			BlockPos p = floorBeside(level, at);
			if (p != null) n.setPos(p.getX() + 0.5, p.getY(), p.getZ() + 0.5);
		}

		static void leave(Npc n) {
			if (n.seat != null) TAKEN.remove(n.seat.asLong());
			if (n.going != null) TAKEN.remove(n.going.asLong());
		}

		/** Open floor to stand on nearest a seat: its front's often the table, so round the sides and the back too. */
		static BlockPos floorBeside(Level level, BlockPos at) {
			Direction f = facing(level.getBlockState(at));
			for (Direction d : new Direction[] {f, f.getClockWise(), f.getCounterClockWise(), f.getOpposite()}) {
				BlockPos p = at.relative(d);
				if (standable(level, p)) return p;
			}
			for (int r = 2; r <= 3; r++)
				for (BlockPos p : BlockPos.betweenClosed(at.offset(-r, 0, -r), at.offset(r, 0, r)))
					if (standable(level, p)) return p.immutable();
			return null;
		}

		private static boolean standable(Level level, BlockPos p) {
			return level.getBlockState(p).getCollisionShape(level, p).isEmpty() && level.getBlockState(p.above()).getCollisionShape(level, p.above()).isEmpty()
					&& !level.getBlockState(p.below()).getCollisionShape(level, p.below()).isEmpty();
		}
	}

	// ---------------------------------------------------------------- finding their way

	/** Walks like anyone else but never counts the top of a table, a chair or a counter as floor. */
	static final class FloorNav extends GroundPathNavigation {
		FloorNav(Mob mob, Level level) {
			super(mob, level);
		}

		@Override
		protected PathFinder createPathFinder(int maxVisitedNodes) {
			nodeEvaluator = new WalkNodeEvaluator() {
				@Override
				public PathType getPathType(PathfindingContext c, int x, int y, int z) {
					return c.getBlockState(new BlockPos(x, y - 1, z)).getBlock() instanceof PropBlock.Sculpt ? PathType.BLOCKED : super.getPathType(c, x, y, z);
				}
			};
			nodeEvaluator.setCanPassDoors(true);
			return new PathFinder(nodeEvaluator, maxVisitedNodes);
		}
	}

	// ---------------------------------------------------------------- chatting

	static final class Chat extends Goal {
		final Npc n;
		boolean leads;
		int left, nextGesture;

		Chat(Npc n) {
			this.n = n;
			setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
		}

		/** How often they strike up a conversation (per tick), and how far they'll go to. */
		private int chance() {
			return switch (n.mode) {
				case "stroll" -> 260;
				case "errand" -> 340;
				case "sit" -> 220;
				default -> n.keepsCounter() ? 1400 : 500;
			};
		}

		private double reach() {
			return n.mode.equals("stand") ? 4 : 8;
		}

		@Override
		public boolean canUse() {
			if (n.partner != null) return n.seat == null && n.talkingTo == null; // someone came over to them
			if (!n.free() || n.kind() == null || n.getRandom().nextInt(chance()) != 0) return false;
			Npc best = null;
			double bestD = reach() * reach();
			for (Npc o : n.level().getEntitiesOfClass(Npc.class, n.getBoundingBox().inflate(reach(), 2, reach()))) {
				if (o == n || !o.free() || o.kind() == null || o.going != null) continue;
				if (o.is("child") != n.is("child") && n.getRandom().nextInt(3) != 0) continue;
				double d = o.distanceToSqr(n);
				if (d < bestD) {
					bestD = d;
					best = o;
				}
			}
			if (best == null) return false;
			n.partner = best;
			best.partner = n;
			leads = true;
			return true;
		}

		@Override
		public void start() {
			left = leads ? 240 + n.getRandom().nextInt(500) : Integer.MAX_VALUE;
			nextGesture = 30 + n.getRandom().nextInt(60);
			if (leads && n.getRandom().nextInt(3) == 0) gesture(n, Animations.BIPED_WAVE_HAND);
		}

		@Override
		public boolean canContinueToUse() {
			Npc p = n.partner;
			return p != null && p.isAlive() && p.partner == n && left > 0 && n.talkingTo == null && p.distanceToSqr(n) < 144;
		}

		@Override
		public void tick() {
			Npc p = n.partner;
			left--;
			n.getLookControl().setLookAt(p, 30f, 30f);
			double d = p.distanceToSqr(n);
			if (leads && d > 5.3 && !n.mode.equals("stand")) {
				if (beat(n, 10)) n.getNavigation().moveTo(p, WALK);
			} else {
				n.getNavigation().stop();
				if (--nextGesture <= 0 && d < 9) {
					nextGesture = 70 + n.getRandom().nextInt(120);
					int r = n.getRandom().nextInt(10);
					if (r < 3) gesture(n, Animations.BIPED_LAUGH);
					else if (r == 3) gesture(n, Animations.BIPED_FRUSTRATED);
					else if (r == 4 && (n.is("guard") || n.is("adventurer")) && (p.is("guard") || p.is("adventurer"))) gesture(n, Animations.BIPED_SALUTE);
				}
			}
		}

		@Override
		public void stop() {
			if (leads && n.partner != null && n.getRandom().nextInt(3) == 0) gesture(n, Animations.BIPED_WAVE_HAND);
			part(n);
			leads = false;
		}

		static void part(Npc n) {
			Npc p = n.partner;
			n.partner = null;
			if (p != null && p.partner == n) p.partner = null;
		}
	}

	// ---------------------------------------------------------------- the children's tag

	static final class Play extends Goal {
		final Npc n;
		int left, pause;

		Play(Npc n) {
			this.n = n;
			setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK, Flag.JUMP));
		}

		@Override
		public boolean canUse() {
			if (n.playmate != null) return n.talkingTo == null;
			if (!n.free() || !n.is("child") || n.getRandom().nextInt(300) != 0) return false;
			List<Npc> kids = new ArrayList<>();
			for (Npc o : n.level().getEntitiesOfClass(Npc.class, n.getBoundingBox().inflate(12, 3, 12)))
				if (o != n && o.free() && o.is("child") && o.going == null) kids.add(o);
			if (kids.isEmpty()) return false;
			Npc o = kids.get(n.getRandom().nextInt(kids.size()));
			n.playmate = o;
			o.playmate = n;
			n.it = true;
			o.it = false;
			return true;
		}

		@Override
		public void start() {
			left = 300 + n.getRandom().nextInt(400);
			pause = 20;
			n.setAct(Npc.POSE_RUN);
		}

		@Override
		public boolean canContinueToUse() {
			Npc o = n.playmate;
			return o != null && o.isAlive() && o.playmate == n && left > 0 && n.talkingTo == null && o.talkingTo == null
					&& o.distanceToSqr(n) < 400;
		}

		@Override
		public void tick() {
			Npc o = n.playmate;
			left--;
			if (pause > 0) {
				pause--;
				n.getNavigation().stop();
				n.getLookControl().setLookAt(o, 30f, 30f);
				return;
			}
			if (n.it) {
				if (beat(n, 6)) n.getNavigation().moveTo(o, RUN);
				n.getLookControl().setLookAt(o, 30f, 30f);
				if (n.distanceToSqr(o) < 1.6) { // tag, you're it
					n.it = false;
					o.it = true;
					pause = 15;
				}
			} else if (n.getNavigation().isDone() || beat(n, 30)) {
				Vec3 away = DefaultRandomPos.getPosAway(n, 8, 4, o.position());
				if (away != null) n.getNavigation().moveTo(away.x, away.y, away.z, RUN);
			}
		}

		@Override
		public void stop() {
			n.setAct(Npc.POSE_NONE);
			Npc o = n.playmate;
			n.playmate = null;
			if (o != null && o.playmate == n) o.playmate = null;
			n.getNavigation().stop();
		}
	}

	// ---------------------------------------------------------------- wandering

	/** Round their spot (strollers), or off on errands across their quarter; those who tend things kneel to it. */
	static final class Wander extends WaterAvoidingRandomStrollGoal {
		final Npc n;

		Wander(Npc n) {
			super(n, WALK, 0.001f);
			this.n = n;
		}

		@Override
		public boolean canUse() {
			if (!n.free() || !(n.mode.equals("stroll") || n.mode.equals("errand"))) return false;
			setInterval(n.mode.equals("errand") ? 80 : 160);
			return super.canUse();
		}

		@Override
		public boolean canContinueToUse() {
			return n.free() && super.canContinueToUse();
		}

		@Override
		protected Vec3 getPosition() {
			int r = n.mode.equals("errand") ? 24 : 9;
			return LandRandomPos.getPos(n, r, 6);
		}

		@Override
		public void stop() {
			super.stop();
			if ((n.is("farmer") || n.is("herbalist")) && n.getRandom().nextInt(3) == 0) n.kneel(100 + n.getRandom().nextInt(140));
		}
	}
}
