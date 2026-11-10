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

import javax.annotation.Nullable;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.common.DeferredSpawnEggItem;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * One of the world's beasts on its own skeleton (tools/beastkit.py): not a spider and not Epic Fight's. It walks, stalks,
 * runs and fights from its clips (BeastClips): every attack winds up where you can read it, lands on its "hit" ticks in
 * front of it (reach, arc), and leaves it open after. A "leap" event throws it at its target, a "roar" slows everyone near.
 * Synced: which clip it's doing and the tick it started, and whether it's stalking; the client poses it from those.
 */
public class Beast extends Monster {
	/** a kind of beast: its id, the rig it's drawn with, its numbers (before Balance) */
	public record Kind(String id, String rig, float w, float h, double hp, double speed, double dmg, double armor, double kb, boolean legend, int egg, int spots) {}

	static final Map<String, Kind> KINDS = load();
	static final Map<String, DeferredHolder<EntityType<?>, EntityType<Beast>>> TYPES = new LinkedHashMap<>();
	static final List<DeferredItem<Item>> EGGS = new ArrayList<>();

	private static Map<String, Kind> load() {
		Map<String, Kind> out = new LinkedHashMap<>();
		try (InputStream in = Beast.class.getResourceAsStream("/ashbound/beasts.json")) {
			if (in == null) return out;
			for (Map.Entry<String, JsonElement> e : JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject().entrySet()) {
				JsonObject o = e.getValue().getAsJsonObject();
				out.put(e.getKey(), new Kind(e.getKey(), o.get("rig").getAsString(), o.get("w").getAsFloat(), o.get("h").getAsFloat(), o.get("hp").getAsDouble(),
						o.get("speed").getAsDouble(), o.get("dmg").getAsDouble(), o.get("armor").getAsDouble(), o.get("kb").getAsDouble(),
						o.get("legend").getAsBoolean(), o.get("egg").getAsInt(), o.get("spots").getAsInt()));
			}
		} catch (Exception ex) {
			Ashbound.LOG.error("beasts not loaded", ex);
		}
		return out;
	}

	static {
		for (Kind k : KINDS.values()) {
			DeferredHolder<EntityType<?>, EntityType<Beast>> t = Monsters.ENTITIES.register(k.id(),
					() -> EntityType.Builder.<Beast>of((type, l) -> new Beast(type, l, k), MobCategory.MONSTER).sized(k.w(), k.h()).clientTrackingRange(12)
							.build(Ashbound.ID + ":" + k.id()));
			TYPES.put(k.id(), t);
			Supplier<EntityType<? extends net.minecraft.world.entity.Mob>> s = t::get;
			EGGS.add(Weapons.ITEMS.registerItem(k.id() + "_spawn_egg", p -> new DeferredSpawnEggItem(s, k.egg(), k.spots(), p)));
		}
	}

	static void register(IEventBus bus) {
		WantedPoster.TYPE.getId();     // the Guild's posters of them (Bounties)
		IceSlab.TYPE.getId();          // its thrown ice registers with the beasts
		LegendSounds.register(bus);    // and their own voices
		bus.addListener((EntityAttributeCreationEvent e) -> TYPES.forEach((id, t) -> e.put(t.get(), stats(KINDS.get(id)).build())));
	}

	private static AttributeSupplier.Builder stats(Kind k) {
		Balance.Mult b = Balance.mob(k.id());
		return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, k.hp() * b.hp()).add(Attributes.MOVEMENT_SPEED, k.speed())
				.add(Attributes.ATTACK_DAMAGE, k.dmg() * b.dmg()).add(Attributes.ARMOR, k.armor()).add(Attributes.KNOCKBACK_RESISTANCE, k.kb())
				.add(Attributes.FOLLOW_RANGE, k.legend() ? 48 : 36).add(Attributes.STEP_HEIGHT, 1.6);
	}

	// ---------------------------------------------------------------- the beast

	private static final EntityDataAccessor<Integer> ACT = SynchedEntityData.defineId(Beast.class, EntityDataSerializers.INT);
	private static final EntityDataAccessor<Integer> ACT_AT = SynchedEntityData.defineId(Beast.class, EntityDataSerializers.INT);
	private static final EntityDataAccessor<Boolean> STALK = SynchedEntityData.defineId(Beast.class, EntityDataSerializers.BOOLEAN);
	/** ticks between attacks, and before it roars again */
	private static final int REST = 14, ROAR_REST = 400, DEATH = 50;

	public final Kind kind;
	public final BeastClips.Set clips;
	private int rest, roarRest = 60;
	/** damage it's taken lately (hug it and hit it and it springs aside), and how long until that's forgotten */
	private float pressure;
	private int pressureT;
	/** it sprang aside: breathe on them next. phase2: under 60% it has its slam */
	private boolean breathNext, phase2;
	@Nullable
	private net.minecraft.server.level.ServerBossEvent bar;
	/** a line of ice spikes on its way to you: each {x, z, y hint, game tick it bursts}; the spikes standing, till when */
	private final List<double[]> spikeQ = new ArrayList<>();
	private final Map<Entity, Long> spikes = new HashMap<>();
	private final Set<UUID> spiked = new HashSet<>();
	private float spikeDmg;
	private int spikeKind;
	/** a charge under way: ticks left and the way it's going */
	private int chargeT;
	private Vec3 chargeDir = Vec3.ZERO;
	/** whoever it has hold of (a grab), till the fling */
	@Nullable
	private LivingEntity held;
	/** rocks to come down out of the sky: {x, z, y, game tick} */
	private final List<double[]> rainQ = new ArrayList<>();
	private final Map<String, Integer> cool = new HashMap<>();
	private final Set<UUID> struck = new HashSet<>();
	private boolean provoked;
	/** client: how far it's walked (blocks), for the gait's phase */
	public float travelled, travelledO;

	public Beast(EntityType<? extends Beast> type, Level level, Kind kind) {
		super(type, level);
		this.kind = kind;
		this.clips = BeastClips.of(kind.rig());
		xpReward = kind.legend() ? 200 : 40;
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) {
		super.defineSynchedData(b);
		b.define(ACT, -1);
		b.define(ACT_AT, 0);
		b.define(STALK, false);
	}

	/** what it's doing (a clip's index, -1 none) and since when (the level's game time, truncated) */
	public int act() {
		return entityData.get(ACT);
	}

	public float actTime(float pt) {
		return (int) level().getGameTime() - entityData.get(ACT_AT) + pt;
	}

	public boolean stalking() {
		return entityData.get(STALK);
	}

	@Nullable
	public BeastClips.Clip acting() {
		BeastClips.Clip c = clips.at(act());
		return c != null && actTime(0) < c.len ? c : null;
	}

	@Override
	protected void registerGoals() {
		goalSelector.addGoal(1, new FloatGoal(this));
		goalSelector.addGoal(2, new Hunt());
		goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.55));
		goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 14));
		goalSelector.addGoal(7, new RandomLookAroundGoal(this));
		targetSelector.addGoal(1, new HurtByTargetGoal(this));
		targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
	}

	@Override
	public void tick() {
		super.tick();
		if (level().isClientSide) {
			travelledO = travelled;
			travelled += (float) Math.hypot(getX() - xo, getZ() - zo);
		}
	}

	@Override
	protected void customServerAiStep() {
		super.customServerAiStep();
		if (rest > 0) rest--;
		if (roarRest > 0) roarRest--;
		cool.replaceAll((k, v) -> Math.max(0, v - 1));
		if (pressureT > 0 && --pressureT == 0) pressure = 0;
		tickSpikes();
		tickRain();
		if (acting() == null) {
			chargeT = 0;
			held = null;
		}
		if (bar != null) {
			bar.setProgress(getHealth() / getMaxHealth());
			if (tickCount % 20 == 0) bar.setName(getDisplayName());
		}
		BeastClips.Clip c = acting();
		if (c == null) {
			if (act() >= 0) entityData.set(ACT, -1);
			return;
		}
		int t = (int) actTime(0);
		LivingEntity target = getTarget();
		int firstHit = commit(c);
		if (target != null && t < firstHit - 2) {          // it tracks you through the wind-up, then it's committed
			getLookControl().setLookAt(target, 30, 30);
			float want = (float) (Mth.atan2(target.getZ() - getZ(), target.getX() - getX()) * Mth.RAD_TO_DEG) - 90f;
			setYRot(Mth.approachDegrees(getYRot(), want, 12f));
			yBodyRot = getYRot();
		} else {
			setYRot(yBodyRot);
		}
		getNavigation().stop();
		if (c.at("leap", t) && target != null) leap(c, target);
		if (c.at("roar", t)) roar(c);
		if (c.at("grab", t)) grab(c);
		if (c.at("blink", t) && target != null) blink(target);
		if (c.at("charge", t) && target != null) charge(c, target);
		if (c.at("rain", t)) rain(c);
		if (c.at("hit", t)) strike(c, c.at("guard", t), false);
		if (chargeT > 0) {
			chargeT--;
			setDeltaMovement(chargeDir.x * c.num("speed", 0.9f), getDeltaMovement().y, chargeDir.z * c.num("speed", 0.9f));
			strike(c, false, true);
			if (level() instanceof ServerLevel l)
				l.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, getBlockStateOn()), getX(), getY() + 0.2, getZ(), 8, getBbWidth() * 0.4, 0.1, getBbWidth() * 0.4, 0.15);
		}
		if (held != null) hold();
		if (c.at("dig", t)) dig();
		if (c.at("throw", t) && target != null) hurl(c, target);
		if (c.at("dodge", t)) dodge(c, target);
		if (c.at("slam", t)) slam(c);
		if (c.at("spikes", t) && target != null) spikeLine(c, target);
		if (c.at("breath", t) && kind.id().equals("sunbreaker")) sig(3.5f);   // the sunbeam's own sear
		if (c.at("breath", t)) playSound(switch ((int) c.num("elem", 0)) {
			case 1 -> SoundEvents.BLAZE_SHOOT;
			case 2 -> SoundEvents.WITCH_DRINK;
			default -> SoundEvents.PLAYER_HURT_FREEZE;
		}, 3f, 0.5f);
		float[] sp = c.nums("spray");
		if (sp != null && t >= sp[0] && t <= sp[1]) breathe(c, t);
	}

	/** the tick it stops turning to follow you: just before its first blow (or breath, or throw) */
	private static int commit(BeastClips.Clip c) {
		int at = c.len;
		for (String e : new String[] {"hit", "throw", "slam", "dig", "spikes", "grab", "charge", "blink"})
			if (c.events.containsKey(e)) at = Math.min(at, c.events.get(e)[0]);
		float[] sp = c.nums("spray");
		if (sp != null) at = Math.min(at, (int) sp[0]);
		return at;
	}

	private Vec3 fwd() {
		return Vec3.directionFromRotation(0, yBodyRot);
	}

	/** to its left (the model's +x) */
	private Vec3 left() {
		Vec3 f = fwd();
		return new Vec3(f.z, 0, -f.x);
	}

	private void quake(Vec3 at, float k) {
		if (level() instanceof ServerLevel l) Spells.skillFx(l, "quake", at, Vec3.ZERO, k, this);
	}

	/** a breath tick: a cone (the clip's reach and arc) along where its head is turned; it fills your frost (vanilla's freezing)
	 * and hurts a little, and a full frost freezes you solid; water under it skins over */
	private void breathe(BeastClips.Clip c, int t) {
		if (!(level() instanceof ServerLevel l)) return;
		float[] v = new float[3];
		float turn = 0;
		for (String b : new String[] {"neck", "head"})
			if (c.boneNames().contains(b)) {
				c.bone(b, t, v);
				turn += v[1];
			}
		float yaw = yBodyRot - turn;
		Vec3 dir = Vec3.directionFromRotation(12, yaw);
		Vec3 mouth = position().add(fwd().scale(getBbWidth() * 0.5 + 0.6)).add(0, getBbHeight() * 0.5, 0);
		double reach = c.num("reach", 8), arc = c.num("arc", 50) * 0.5 * Mth.DEG_TO_RAD;
		int elem = (int) c.num("elem", 0);
		for (int i = 0; i < 8; i++) {
			double sx = (random.nextDouble() - 0.5) * 0.35, sy = (random.nextDouble() - 0.5) * 0.2, sp = 0.5 + random.nextDouble() * 0.5;
			net.minecraft.core.particles.ParticleOptions pt = switch (elem) {
				case 1 -> i % 3 == 0 ? ParticleTypes.END_ROD : ParticleTypes.FLAME;
				case 2 -> i % 3 == 0 ? ParticleTypes.SQUID_INK : ParticleTypes.ITEM_SLIME;
				default -> i % 3 == 0 ? ParticleTypes.CLOUD : ParticleTypes.SNOWFLAKE;
			};
			l.sendParticles(pt, mouth.x, mouth.y, mouth.z, 0, dir.x + sx, dir.y + sy, dir.z + sx, sp);
		}
		if (t % 2 != 0) return;
		float dmg = (float) getAttributeValue(Attributes.ATTACK_DAMAGE) * c.num("dmg", 0.1f);
		for (LivingEntity e : l.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(reach), e -> e != this && e.isAlive() && !(e instanceof Beast))) {
			if (e instanceof Player p && (p.isCreative() || p.isSpectator())) continue;
			Vec3 to = e.position().add(0, e.getBbHeight() * 0.5, 0).subtract(mouth);
			double d = to.length();
			if (d > reach + e.getBbWidth() * 0.5) continue;
			if (Math.acos(Mth.clamp(to.normalize().dot(dir), -1, 1)) > arc && d > 1.5) continue;
			if (elem == 1) {          // the sun off its mirror: it burns, and dazzles
				e.hurt(damageSources().inFire(), dmg);
				e.igniteForSeconds(3);
				if (random.nextFloat() < 0.15f) e.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 30), this);
				continue;
			}
			if (elem == 2) {          // the bog: it chokes
				e.hurt(damageSources().mobAttack(this), dmg);
				e.addEffect(new MobEffectInstance(MobEffects.POISON, 80, 1), this);
				if (random.nextFloat() < 0.1f) e.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 80), this);
				continue;
			}
			e.hurt(damageSources().freeze(), dmg);
			e.setTicksFrozen(Math.min(e.getTicksFrozen() + 16, e.getTicksRequiredToFreeze() + 40));
			if (e.getTicksFrozen() >= e.getTicksRequiredToFreeze() && !e.hasEffect(MobEffects.MOVEMENT_SLOWDOWN)) {
				e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 50, 5), this);     // frozen solid
				e.addEffect(new MobEffectInstance(MobEffects.DIG_SLOWDOWN, 50, 3), this);
				l.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, net.minecraft.world.level.block.Blocks.ICE.defaultBlockState()),
						e.getX(), e.getY() + 1, e.getZ(), 30, 0.4, 0.6, 0.4, 0.1);
				e.playSound(SoundEvents.GLASS_PLACE, 1.5f, 0.6f);
			}
		}
		for (double s = 2; elem == 0 && s < reach; s += 1.5) {          // water along its line skins over (melts back, like frost walking)
			BlockPos p = BlockPos.containing(mouth.add(dir.scale(s)));
			for (int dy = 0; dy > -4; dy--) {
				BlockPos q = p.offset(0, dy, 0);
				BlockState st = l.getBlockState(q);
				if (st.is(net.minecraft.world.level.block.Blocks.WATER) && st.getFluidState().isSource() && l.getBlockState(q.above()).isAir()) {
					l.setBlockAndUpdate(q, net.minecraft.world.level.block.Blocks.FROSTED_ICE.defaultBlockState());
					l.scheduleTick(q, net.minecraft.world.level.block.Blocks.FROSTED_ICE, Mth.nextInt(random, 60, 120));
					break;
				}
				if (!st.isAir()) break;
			}
		}
	}

	/** the paw goes into the ground: ice bursts up where it hit (the throw that follows tears it out) */
	private void dig() {
		if (!(level() instanceof ServerLevel l)) return;
		Vec3 at = position().add(fwd().scale(getBbWidth() * 0.5 + 0.6)).add(left().scale(-getBbWidth() * 0.25));
		l.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, net.minecraft.world.level.block.Blocks.PACKED_ICE.defaultBlockState()), at.x, at.y + 0.3, at.z, 50, 0.6, 0.3, 0.6, 0.25);
		l.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, getBlockStateOn()), at.x, at.y + 0.2, at.z, 30, 0.6, 0.2, 0.6, 0.2);
		playSound(SoundEvents.RAVAGER_STEP, 2f, 0.5f);
		playSound(SoundEvents.GLASS_BREAK, 1.5f, 0.5f);
		quake(at, 0.4f);
	}

	/** the slab goes at where you'll be, not where you are */
	private void hurl(BeastClips.Clip c, LivingEntity target) {
		if (kind.id().equals("old_harpoon")) sig(3.0f);   // the harpoon's chain whipping after it
		IceSlab slab = new IceSlab(level(), this, (float) getAttributeValue(Attributes.ATTACK_DAMAGE) * c.num("dmg", 0.9f), (int) c.num("item", 0));
		Vec3 from = position().add(fwd().scale(getBbWidth() * 0.5 + 0.8)).add(0, getBbHeight() * 0.7, 0);
		slab.setPos(from.x, from.y, from.z);
		double speed = c.num("throw", 1.6f);
		Vec3 aim = target.position().add(0, target.getBbHeight() * 0.5, 0);
		double flight = aim.distanceTo(from) / speed;
		aim = aim.add(target.getDeltaMovement().multiply(1, 0, 1).scale(flight));
		Vec3 to = aim.subtract(from);
		// lift for the fall over its flight (gravity 0.04 a tick)
		slab.shoot(to.x, to.y + 0.5 * 0.04 * flight * flight, to.z, (float) speed, 1.5f);
		level().addFreshEntity(slab);
		playSound(SoundEvents.PLAYER_ATTACK_SWEEP, 2f, 0.4f);
	}

	/** the blade goes into the ground and the ice answers: spikes burst up one after another along the ground toward you */
	private void spikeLine(BeastClips.Clip c, LivingEntity target) {
		Vec3 to = target.position().subtract(position()).multiply(1, 0, 1);
		double d = to.length();
		if (d < 0.1) return;
		Vec3 dir = to.scale(1 / d), side = new Vec3(dir.z, 0, -dir.x);
		double start = getBbWidth() * 0.5 + 1.2;
		int n = Mth.clamp((int) ((d - start + 4) / 1.3), 4, 16);
		long now = level().getGameTime();
		spiked.clear();
		spikeDmg = (float) getAttributeValue(Attributes.ATTACK_DAMAGE) * c.num("dmg", 1f);
		spikeKind = (int) c.num("kind", 0);
		for (int i = 0; i < n; i++) {
			Vec3 p = position().add(dir.scale(start + i * 1.3)).add(side.scale((random.nextDouble() - 0.5) * 0.8));
			spikeQ.add(new double[] {p.x, p.z, getY(), now + 1 + i});
		}
		quake(position().add(dir.scale(start)), 0.5f);
		playSound(SoundEvents.GLASS_BREAK, 2f, 0.4f);
	}

	private void tickSpikes() {
		if (!(level() instanceof ServerLevel l)) return;
		long now = l.getGameTime();
		spikes.entrySet().removeIf(e -> {
			if (now < e.getValue()) return false;
			e.getKey().discard();
			return true;
		});
		for (java.util.Iterator<double[]> it = spikeQ.iterator(); it.hasNext(); ) {
			double[] q = it.next();
			if (now < q[3]) continue;
			it.remove();
			burst(l, q[0], q[1], q[2], now);
		}
	}

	private void burst(ServerLevel l, double x, double z, double yHint, long now) {
		BlockPos col = BlockPos.containing(x, yHint + 3, z);
		double gy = Double.NaN;
		for (int dy = 0; dy < 9; dy++) {
			BlockPos q = col.below(dy);
			if (!l.getBlockState(q).getCollisionShape(l, q).isEmpty() && l.getBlockState(q.above()).getCollisionShape(l, q.above()).isEmpty()) {
				gy = q.getY() + 1;
				break;
			}
		}
		if (Double.isNaN(gy)) return;
		for (int i = 0; i < 3; i++) {          // one tall spike and two short ones, leaning out
			float h = i == 0 ? 2.6f + random.nextFloat() * 0.8f : 1.2f + random.nextFloat() * 0.6f, w = i == 0 ? 0.7f : 0.42f;
			double ox = i == 0 ? 0 : (random.nextDouble() - 0.5) * 1.2, oz = i == 0 ? 0 : (random.nextDouble() - 0.5) * 1.2;
			float ax = (random.nextFloat() - 0.5f) * 0.5f, az = (random.nextFloat() - 0.5f) * 0.5f;
			org.joml.Quaternionf q = new org.joml.Quaternionf().rotationXYZ(ax, random.nextFloat() * 6.28f, az);
			final double ground = gy;
			CompoundTag tag = new CompoundTag();
			tag.putString("id", "minecraft:block_display");
			CompoundTag bs = new CompoundTag();
			bs.putString("Name", switch (spikeKind) {
				case 1 -> i == 0 ? "minecraft:dark_oak_log" : "minecraft:mangrove_roots";          // roots
				case 2 -> i == 0 ? "minecraft:cut_sandstone" : "minecraft:sandstone";              // pillars of sandstone
				default -> i == 0 ? "minecraft:blue_ice" : "minecraft:packed_ice";
			});
			tag.put("block_state", bs);
			CompoundTag tf = new CompoundTag();
			tf.put("left_rotation", floats(q.x, q.y, q.z, q.w));
			tf.put("right_rotation", floats(0, 0, 0, 1));
			tf.put("translation", floats(-w / 2, -0.4f, -w / 2));
			tf.put("scale", floats(w, h, w));
			tag.put("transformation", tf);
			Entity e = EntityType.loadEntityRecursive(tag, l, en -> {
				en.moveTo(x + ox, ground, z + oz, 0, 0);
				return en;
			});
			if (e != null && l.addFreshEntity(e)) spikes.put(e, now + 36 + random.nextInt(10));
		}
		BlockState chips = switch (spikeKind) {
			case 1 -> net.minecraft.world.level.block.Blocks.ROOTED_DIRT.defaultBlockState();
			case 2 -> net.minecraft.world.level.block.Blocks.SAND.defaultBlockState();
			default -> net.minecraft.world.level.block.Blocks.PACKED_ICE.defaultBlockState();
		};
		l.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, chips), x, gy + 0.3, z, 18, 0.4, 0.3, 0.4, 0.2);
		if (spikeKind == 0) l.sendParticles(ParticleTypes.SNOWFLAKE, x, gy + 1, z, 8, 0.4, 0.8, 0.4, 0.05);
		l.playSound(null, x, gy, z, switch (spikeKind) {
			case 1 -> SoundEvents.ROOTED_DIRT_BREAK;
			case 2 -> SoundEvents.STONE_BREAK;
			default -> SoundEvents.GLASS_BREAK;
		}, net.minecraft.sounds.SoundSource.HOSTILE, 1.2f, 0.5f + random.nextFloat() * 0.3f);
		for (LivingEntity e : l.getEntitiesOfClass(LivingEntity.class, new net.minecraft.world.phys.AABB(x - 1.4, gy - 1, z - 1.4, x + 1.4, gy + 3, z + 1.4),
				e -> e != this && e.isAlive() && !(e instanceof Beast))) {
			if (e instanceof Player p && (p.isCreative() || p.isSpectator())) continue;
			if (!spiked.add(e.getUUID())) continue;
			if (e.hurt(damageSources().mobAttack(this), spikeDmg)) {
				e.setDeltaMovement(e.getDeltaMovement().add(0, 0.65, 0));
				e.hurtMarked = true;
				if (spikeKind == 0) e.setTicksFrozen(Math.max(e.getTicksFrozen(), e.getTicksRequiredToFreeze() / 2));
				if (spikeKind == 1) e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 50, 3), this);     // the roots hold on
			}
		}
	}

	private static net.minecraft.nbt.ListTag floats(float... v) {
		net.minecraft.nbt.ListTag t = new net.minecraft.nbt.ListTag();
		for (float f : v) t.add(net.minecraft.nbt.FloatTag.valueOf(f));
		return t;
	}

	@Override
	public void remove(RemovalReason why) {
		spikes.keySet().forEach(Entity::discard);
		spikes.clear();
		spikeQ.clear();
		rainQ.clear();
		held = null;
		super.remove(why);
	}

	/** springs aside, away from your blade, and means to breathe on you next */
	private void dodge(BeastClips.Clip c, @Nullable LivingEntity target) {
		Vec3 side = left().scale(random.nextBoolean() ? 1 : -1);
		Vec3 away = target == null ? Vec3.ZERO : position().subtract(target.position()).multiply(1, 0, 1).normalize();
		double k = c.num("side", 1f);
		setDeltaMovement(side.scale(1.1 * k).add(away.scale(0.35 * k)).add(0, 0.42, 0));
		hasImpulse = true;
		breathNext = clips.get("breath") != null;
		playSound(SoundEvents.RAVAGER_STEP, 1.6f, 0.7f);
		playSound(SoundEvents.PLAYER_ATTACK_SWEEP, 1.2f, 0.5f);
	}

	/** its whole weight comes down in front of it: deadly there, nothing at its sides or behind it */
	private void slam(BeastClips.Clip c) {
		if (!(level() instanceof ServerLevel l)) return;
		Vec3 at = position().add(fwd().scale(c.num("front", 3) + getBbWidth() * 0.5));
		double r = c.num("radius", 3f);
		int elem = (int) c.num("elem", 0);
		float dmg = (float) getAttributeValue(Attributes.ATTACK_DAMAGE) * c.num("dmg", 2.4f);
		for (LivingEntity e : l.getEntitiesOfClass(LivingEntity.class, new net.minecraft.world.phys.AABB(at, at).inflate(r + 1, 3, r + 1), e -> e != this && e.isAlive() && !(e instanceof Beast))) {
			if (e instanceof Player p && (p.isCreative() || p.isSpectator())) continue;
			Vec3 to = e.position().subtract(at);
			if (to.horizontalDistance() > r + e.getBbWidth() * 0.5 || Math.abs(to.y) > 2.5) continue;
			if (e.hurt(damageSources().mobAttack(this), dmg)) {
				if (elem == 2) e.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 1), this);
				if (elem == 9) e.addEffect(new MobEffectInstance(MobEffects.WITHER, 60, 0), this);      // thorns, festering
				Vec3 push = to.horizontalDistance() < 0.1 ? fwd() : to.multiply(1, 0, 1).normalize();
				e.setDeltaMovement(e.getDeltaMovement().add(push.scale(0.9)).add(0, 0.7, 0));
				e.hurtMarked = true;
			}
		}
		BlockState ground = l.getBlockState(BlockPos.containing(at).below());
		if (ground.isAir()) ground = getBlockStateOn();
		for (int i = 0; i < 28; i++) {
			double a = i * Math.PI * 2 / 28;
			l.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, ground), at.x + Math.cos(a) * r, at.y + 0.2, at.z + Math.sin(a) * r, 4, 0.2, 0.1, 0.2, 0.15);
		}
		l.sendParticles(ParticleTypes.EXPLOSION, at.x, at.y + 0.5, at.z, 2, 0.6, 0.2, 0.6, 0);
		l.sendParticles(switch (elem) {
			case 2 -> ParticleTypes.ITEM_SLIME;
			case 5 -> ParticleTypes.CAMPFIRE_COSY_SMOKE;
			case 9 -> new BlockParticleOption(ParticleTypes.BLOCK, net.minecraft.world.level.block.Blocks.MANGROVE_ROOTS.defaultBlockState());
			default -> ParticleTypes.SNOWFLAKE;
		}, at.x, at.y + 0.5, at.z, 60, r * 0.5, 0.4, r * 0.5, 0.12);
		playSound(SoundEvents.GENERIC_EXPLODE.value(), 2.5f, 0.55f);
		playSound(SoundEvents.ANVIL_LAND, 1.5f, 0.4f);
		quake(at, 1.0f);
	}

	/** throws itself at its target: as far as it is, up to the clip's leap (forward, up) */
	private void leap(BeastClips.Clip c, LivingEntity target) {
		float[] lp = c.nums("leap");
		double fwd = lp == null ? 1.0 : lp[0], up = lp == null ? 0.5 : lp[1];
		Vec3 to = target.position().subtract(position());
		double d = Math.max(1, to.horizontalDistance());
		double reach = Math.min(1.0, d / 12.0);
		setDeltaMovement(to.x / d * fwd * (0.6 + reach), up, to.z / d * fwd * (0.6 + reach));
		hasImpulse = true;
		playSound(SoundEvents.RAVAGER_STEP, 1.2f, 0.6f);
	}

	/** the roars that are a Legend's own sound instead of its throat: the bell, the crows, the cackle, the giggle, the quake */
	private static final java.util.Set<String> SIG_ROARS = java.util.Set.of("toll", "crows", "cackle", "giggle", "quake");

	/** this Legend's one sound of its own, if it has one */
	private void sig(float volume) {
		SoundEvent s = LegendSounds.get(kind.id(), "sig");
		if (s != null) playSound(s, volume, 1f);
	}

	private void roar(BeastClips.Clip c) {
		roarRest = ROAR_REST;
		SoundEvent own = LegendSounds.get(kind.id(), "roar");
		if (own != null) {                     // its own throat; and the one sound only it makes, where the move is that sound
			if (!SIG_ROARS.contains(c.name)) playSound(own, 4.0f, 1f);
			else sig(4.0f);
		} else {
			SoundEvent s = GateMobs.voice(kind.id()).ambient();
			playSound(s != null ? s : SoundEvents.RAVAGER_ROAR, 3.0f, getVoicePitch() * 0.7f);
			if (c.name.equals("toll")) {          // the Penitent's bell, not a throat
				playSound(SoundEvents.BELL_BLOCK, 4.0f, 0.45f);
				playSound(SoundEvents.BELL_RESONATE, 3.0f, 0.5f);
			} else playSound(SoundEvents.RAVAGER_ROAR, 2.0f, 0.6f);
		}
		double r = c.num("reach", 7);
		if (level() instanceof ServerLevel l) {
			int elem = (int) c.num("elem", 0);
			double cy = getY() + getBbHeight() * 0.7;
			switch (elem) {
				case 1 -> l.sendParticles(ParticleTypes.FLAME, getX(), cy, getZ(), 60, r * 0.4, 0.6, r * 0.4, 0.06);
				case 2 -> l.sendParticles(ParticleTypes.ITEM_SLIME, getX(), cy, getZ(), 60, r * 0.4, 0.6, r * 0.4, 0.06);
				case 3 -> {          // the crows burst off it
					l.sendParticles(ParticleTypes.SQUID_INK, getX(), cy + 1, getZ(), 50, r * 0.3, 1.0, r * 0.3, 0.12);
					l.sendParticles(ParticleTypes.LARGE_SMOKE, getX(), cy + 1, getZ(), 30, r * 0.3, 1.0, r * 0.3, 0.05);
					l.playSound(null, getX(), cy, getZ(), SoundEvents.PARROT_IMITATE_PHANTOM, net.minecraft.sounds.SoundSource.HOSTILE, 2f, 0.6f);
				}
				case 4 -> {          // the tide comes up off him
					l.sendParticles(ParticleTypes.SPLASH, getX(), getY() + 0.5, getZ(), 200, r * 0.5, 0.4, r * 0.5, 0.3);
					l.sendParticles(ParticleTypes.BUBBLE_POP, getX(), cy, getZ(), 40, r * 0.3, 0.6, r * 0.3, 0.1);
					l.playSound(null, getX(), cy, getZ(), SoundEvents.GENERIC_SPLASH, net.minecraft.sounds.SoundSource.HOSTILE, 3f, 0.5f);
				}
				case 5 -> l.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, getBlockStateOn()), getX(), getY() + 0.3, getZ(), 120, r * 0.5, 0.3, r * 0.5, 0.25);
				case 6 -> {
					l.sendParticles(ParticleTypes.SOUL, getX(), cy, getZ(), 40, r * 0.4, 0.8, r * 0.4, 0.04);
					l.sendParticles(ParticleTypes.SCULK_SOUL, getX(), cy, getZ(), 20, r * 0.3, 0.6, r * 0.3, 0.04);
				}
				case 7 -> {
				}
				case 8 -> l.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, net.minecraft.world.level.block.Blocks.SAND.defaultBlockState()),
						getX(), cy, getZ(), 140, r * 0.5, 0.8, r * 0.5, 0.3);
				default -> l.sendParticles(ParticleTypes.SNOWFLAKE, getX(), cy, getZ(), 60, r * 0.4, 0.6, r * 0.4, 0.06);
			}
			for (LivingEntity e : l.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(r), e -> e != this && !(e instanceof Beast)))
			{
				e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 1), this);
				if (elem == 8 || elem == 1) e.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 50), this);
				if (elem == 6) e.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 100), this);
				if (elem == 2) e.addEffect(new MobEffectInstance(MobEffects.POISON, 60), this);
				double d = e.distanceTo(this);
				Vec3 away = e.position().subtract(position()).multiply(1, 0, 1).normalize();
				double k = Math.max(0, 1 - d / r) * (elem == 4 ? 2.2 : 1.4);          // the closer you stand, the harder it throws you
				e.setDeltaMovement(e.getDeltaMovement().add(away.scale(k)).add(0, k * 0.3, 0));
				e.hurtMarked = true;
			}
			quake(position(), kind.legend() ? 0.8f : 0.5f);
		}
	}

	/** whoever's in front of it, within reach, inside the arc: hit, knocked back */
	private void strike(BeastClips.Clip c, boolean guard, boolean once) {
		if (!(level() instanceof ServerLevel l)) return;
		if (!once) struck.clear();          // every swing is a swing of its own (a flurry hits as often as it lands)
		double reach = c.num("reach", 3) + getBbWidth() * 0.5, arc = c.num("arc", 90) * 0.5 * Mth.DEG_TO_RAD;
		Vec3 fwd = Vec3.directionFromRotation(0, yBodyRot);
		float dmg = (float) getAttributeValue(Attributes.ATTACK_DAMAGE) * c.num("dmg", 1f);
		for (LivingEntity e : l.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(reach, 1.5, reach), e -> e != this && e.isAlive() && !(e instanceof Beast))) {
			if (struck.contains(e.getUUID())) continue;
			Vec3 to = e.position().subtract(position());
			double d = to.horizontalDistance();
			if (d > reach + e.getBbWidth() * 0.5) continue;
			if (d > getBbWidth() * 0.6 && Math.acos(Mth.clamp((to.x * fwd.x + to.z * fwd.z) / Math.max(1e-4, d), -1, 1)) > arc) continue;
			if (e instanceof Player p && (p.isCreative() || p.isSpectator())) continue;
			if (guard && e instanceof Player p && p.isBlocking()) {          // the second rake goes through a raised shield
				p.disableShield();
				p.playSound(SoundEvents.SHIELD_BREAK, 1f, 0.8f);
			}
			if (e.hurt(damageSources().mobAttack(this), dmg)) {
				struck.add(e.getUUID());
				float pull = c.num("pull", 0f), fling = c.num("fling", 0f);
				if (pull > 0) {          // the hook: dragged in, not thrown off
					Vec3 in = position().subtract(e.position()).multiply(1, 0, 1).normalize();
					e.setDeltaMovement(in.scale(pull).add(0, 0.3, 0));
					e.hurtMarked = true;
				} else if (held == e && fling > 0) {
					e.setDeltaMovement(fwd.scale(fling).add(0, 0.9, 0));
					e.hurtMarked = true;
					held = null;
				} else e.knockback(c.num("knock", 0.9f), -fwd.x, -fwd.z);
			}
		}
		if (held != null && c.num("fling", 0f) > 0 && held.isAlive()) {          // flung even if the swing missed
			Vec3 f = Vec3.directionFromRotation(0, yBodyRot);
			held.hurt(damageSources().mobAttack(this), dmg);
			held.setDeltaMovement(f.scale(c.num("fling", 1f)).add(0, 0.9, 0));
			held.hurtMarked = true;
			held = null;
		}
		if (!once) playSound(SoundEvents.PLAYER_ATTACK_SWEEP, 1f, 0.6f);
	}

	/** seizes whoever's closest in front, within reach */
	private void grab(BeastClips.Clip c) {
		if (!(level() instanceof ServerLevel l)) return;
		double reach = c.num("reach", 3) + getBbWidth() * 0.5;
		Vec3 f = fwd();
		LivingEntity best = null;
		double bd = reach;
		for (LivingEntity e : l.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(reach, 2, reach), e -> e != this && e.isAlive() && !(e instanceof Beast))) {
			if (e instanceof Player p && (p.isCreative() || p.isSpectator())) continue;
			Vec3 to = e.position().subtract(position());
			double d = to.horizontalDistance();
			if (d < bd && (to.x * f.x + to.z * f.z) > 0) {
				bd = d;
				best = e;
			}
		}
		held = best;
		if (held != null) playSound(SoundEvents.PLAYER_ATTACK_STRONG, 1.4f, 0.5f);
	}

	/** what it holds hangs in its hands, high in front of it */
	private void hold() {
		if (!held.isAlive() || held.isRemoved()) {
			held = null;
			return;
		}
		Vec3 at = position().add(fwd().scale(getBbWidth() * 0.5 + 1.0)).add(0, getBbHeight() * 0.65, 0);
		held.teleportTo(at.x, at.y, at.z);
		held.setDeltaMovement(Vec3.ZERO);
		held.fallDistance = 0;
	}

	/** gone, and behind you: where you're not looking */
	private void blink(LivingEntity target) {
		if (!(level() instanceof ServerLevel l)) return;
		Vec3 look = Vec3.directionFromRotation(0, target.getYRot());
		l.sendParticles(ParticleTypes.LARGE_SMOKE, getX(), getY() + getBbHeight() * 0.5, getZ(), 40, getBbWidth() * 0.4, getBbHeight() * 0.4, getBbWidth() * 0.4, 0.02);
		for (double back : new double[] {3.2, 2.4, 4.2}) {
			Vec3 to = target.position().subtract(look.scale(back + getBbWidth() * 0.5));
			if (l.noCollision(this, getBoundingBox().move(to.subtract(position())))) {
				teleportTo(to.x, to.y, to.z);
				float face = (float) (Mth.atan2(target.getZ() - to.z, target.getX() - to.x) * Mth.RAD_TO_DEG) - 90f;
				setYRot(face);
				yBodyRot = face;
				yHeadRot = face;
				break;
			}
		}
		l.sendParticles(ParticleTypes.REVERSE_PORTAL, getX(), getY() + getBbHeight() * 0.5, getZ(), 50, getBbWidth() * 0.4, getBbHeight() * 0.4, getBbWidth() * 0.4, 0.05);
		playSound(SoundEvents.ENDERMAN_TELEPORT, 2f, 0.5f);
	}

	/** head down, straight at you, carving the ground: anyone in its way is run down */
	private void charge(BeastClips.Clip c, LivingEntity target) {
		if (kind.id().equals("red_plough")) sig(3.5f);   // the plough dragged through the ground
		Vec3 to = target.position().subtract(position()).multiply(1, 0, 1);
		chargeDir = to.lengthSqr() < 1e-4 ? fwd() : to.normalize();
		chargeT = (int) c.num("dash", 14);
		float face = (float) (Mth.atan2(chargeDir.z, chargeDir.x) * Mth.RAD_TO_DEG) - 90f;
		setYRot(face);
		yBodyRot = face;
		struck.clear();
		playSound(SoundEvents.RAVAGER_ROAR, 2f, 0.5f);
	}

	/** stones out of the sky over everyone near: they land a moment apart */
	private void rain(BeastClips.Clip c) {
		if (!(level() instanceof ServerLevel l)) return;
		List<Player> near = l.getEntitiesOfClass(Player.class, getBoundingBox().inflate(18), p -> !p.isSpectator() && !p.isCreative());
		if (near.isEmpty()) return;
		long now = l.getGameTime();
		int n = (int) c.num("n", 10);
		for (int i = 0; i < n; i++) {
			Player p = near.get(i % near.size());
			rainQ.add(new double[] {p.getX() + (random.nextDouble() - 0.5) * 9, p.getZ() + (random.nextDouble() - 0.5) * 9, p.getY() + 14, now + 6 + i * 3});
		}
		quake(position(), 0.7f);
	}

	private void tickRain() {
		if (!(level() instanceof ServerLevel l) || rainQ.isEmpty()) return;
		long now = l.getGameTime();
		for (java.util.Iterator<double[]> it = rainQ.iterator(); it.hasNext(); ) {
			double[] q = it.next();
			if (now < q[3]) continue;
			it.remove();
			IceSlab rock = new IceSlab(l, this, (float) getAttributeValue(Attributes.ATTACK_DAMAGE) * 0.8f, 3);
			rock.setPos(q[0], q[2], q[1]);
			rock.setDeltaMovement(0, -0.6, 0);
			l.addFreshEntity(rock);
		}
	}

	/** starts a clip (server) */
	void begin(String clip) {
		int i = clips.index(clip);
		if (i < 0) return;
		struck.clear();
		entityData.set(ACT, i);
		entityData.set(ACT_AT, (int) level().getGameTime());
		BeastClips.Clip c = clips.at(i);
		rest = REST + c.len;
		cool.put(clip, (int) c.num("cool", c.len * 3));
	}

	@Override
	public boolean hurt(DamageSource source, float amount) {
		if (source.getEntity() instanceof LivingEntity) provoked = true;
		boolean hit = super.hurt(source, amount);
		if (hit) {
			pressure += amount;
			pressureT = 60;
			if (!phase2 && getHealth() < getMaxHealth() * 0.6f && hasPhase2()) {
				phase2 = true;
				roarRest = 0;          // it roars as it turns, and fights harder after
			}
		}
		return hit;
	}

	/** its roar: the clip called that, or any with a "roar" in it (the Penitent's toll) */
	@Nullable
	private String roarClip() {
		if (clips.get("roar") != null) return "roar";
		for (BeastClips.Clip c : clips.clips.values()) if (c.has("roar")) return c.name;
		return null;
	}

	private boolean hasPhase2() {
		for (BeastClips.Clip c : clips.clips.values()) if (c.num("phase", 1) >= 2) return true;
		return false;
	}

	/** what it can open a fight with: a blow, a throw, a slam or a breath */
	private static boolean attack(BeastClips.Clip c) {
		return c.has("hit") || c.has("throw") || c.has("slam") || c.has("spikes") || c.nums("spray") != null;
	}

	// ---------------------------------------------------------------- a legend's bar

	@Override
	public void startSeenByPlayer(net.minecraft.server.level.ServerPlayer p) {
		super.startSeenByPlayer(p);
		if (kind.legend()) {
			if (bar == null) bar = new net.minecraft.server.level.ServerBossEvent(getDisplayName(), net.minecraft.world.BossEvent.BossBarColor.WHITE,
					net.minecraft.world.BossEvent.BossBarOverlay.NOTCHED_10);
			bar.addPlayer(p);
		}
	}

	@Override
	public void stopSeenByPlayer(net.minecraft.server.level.ServerPlayer p) {
		super.stopSeenByPlayer(p);
		if (bar != null) bar.removePlayer(p);
	}

	/** Its fight: stalk in low when it's found you (if it's a stalker and you haven't hit it), roar once, then pick a move
	 * that fits how far you are; chase between them, running if you're far. */
	class Hunt extends Goal {
		Hunt() {
			setFlags(java.util.EnumSet.of(Flag.MOVE, Flag.LOOK));
		}

		@Override
		public boolean canUse() {
			LivingEntity t = getTarget();
			return t != null && t.isAlive();
		}

		@Override
		public void stop() {
			entityData.set(STALK, false);
		}

		@Override
		public boolean requiresUpdateEveryTick() {
			return true;
		}

		@Override
		public void tick() {
			LivingEntity t = getTarget();
			if (t == null || acting() != null) return;
			double d = distanceTo(t) - getBbWidth() * 0.5;
			boolean stalker = clips.get("stalk") != null && !provoked;
			entityData.set(STALK, stalker && d > 6);
			getLookControl().setLookAt(t, 30, 30);
			if (d < 4 && pressure >= getMaxHealth() * 0.12f && clips.get("dodge") != null && cool.getOrDefault("dodge", 0) <= 0) {
				pressure = 0;
				begin("dodge");
				return;
			}
			if (rest <= 0 || breathNext) {
				String pick = choose(d);
				if (pick != null) {
					begin(pick);
					return;
				}
			}
			double speed = stalking() ? 0.55 : d > 10 ? 1.7 : 1.15;
			getNavigation().moveTo(t, speed);
		}

		@Nullable
		private String choose(double d) {
			if (breathNext) {
				breathNext = false;
				if (clips.get("breath") != null && d < 12) return "breath";
			}
			String rc = roarClip();
			if (roarRest <= 0 && rc != null && d < 14 && !stalking()) return rc;
			List<String> fit = new ArrayList<>();
			for (BeastClips.Clip c : clips.clips.values()) {
				if (!attack(c) || cool.getOrDefault(c.name, 0) > 0) continue;
				if (c.num("phase", 1) >= 2 && !phase2) continue;
				if (getRandom().nextFloat() > c.num("odds", 1)) continue;
				float[] range = c.nums("range");
				double lo = range != null ? range[0] : 0, hi = range != null ? range[1] : c.num("reach", 3) + 0.5;
				if (d >= lo && d <= hi) fit.add(c.name);
			}
			return fit.isEmpty() ? null : fit.get(getRandom().nextInt(fit.size()));
		}
	}

	// ---------------------------------------------------------------- sounds, death

	@Override
	protected SoundEvent getAmbientSound() {
		return stalking() ? null : GateMobs.voice(kind.id()).ambient();
	}

	@Override
	protected SoundEvent getHurtSound(DamageSource source) {
		return GateMobs.voice(kind.id()).hurt();
	}

	@Override
	protected SoundEvent getDeathSound() {
		return GateMobs.voice(kind.id()).death();
	}

	@Override
	protected void playStepSound(BlockPos pos, BlockState state) {
		playSound(GateMobs.voice(kind.id()).step(), stalking() ? 0.1f : 0.4f, 0.8f);
	}

	@Override
	public float getVoicePitch() {
		return GateMobs.voice(kind.id()).pitch() * (kind.legend() ? 0.8f : 1f) * (0.92f + random.nextFloat() * 0.16f);
	}

	@Override
	protected void tickDeath() {
		++deathTime;
		if (deathTime >= DEATH && !level().isClientSide && !isRemoved()) {
			level().broadcastEntityEvent(this, (byte) 60);
			remove(RemovalReason.KILLED);
		}
	}

	@Override
	public boolean isPushable() {
		return !kind.legend() && super.isPushable();
	}

	@Override
	protected void checkFallDamage(double y, boolean onGround, BlockState state, BlockPos pos) {
		if (onGround && fallDistance > 2 && level() instanceof ServerLevel l)
			l.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, state), getX(), getY(), getZ(), 24, getBbWidth() * 0.4, 0.1, getBbWidth() * 0.4, 0.15);
		super.checkFallDamage(y, onGround, state, pos);
	}

	@Override
	public boolean causeFallDamage(float dist, float mult, DamageSource src) {
		return false;
	}

	@Override
	public void addAdditionalSaveData(CompoundTag tag) {
		super.addAdditionalSaveData(tag);
		tag.putBoolean("provoked", provoked);
		tag.putBoolean("phase2", phase2);
	}

	@Override
	public void readAdditionalSaveData(CompoundTag tag) {
		super.readAdditionalSaveData(tag);
		provoked = tag.getBoolean("provoked");
		phase2 = tag.getBoolean("phase2");
	}
}
