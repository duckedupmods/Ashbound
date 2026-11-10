package com.snoringwalrus.ashbound.client;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Properties;

import net.neoforged.fml.loading.FMLPaths;

/**
 * What each player has set for themselves, kept in config: the hit numbers on the Party screen, the meter on MeterSetup, and how
 * the skills look on FxSetup (how see-through, how much they glow, the camera's shake, the screen's flash and speed lines).
 */
public final class HudPrefs {
	private HudPrefs() {}

	static final int OFF = 0, IN_FIGHTS = 1, ALWAYS = 2;
	static final int BOTH = 0, ONLY_DAMAGE = 1, ONLY_HEALING = 2;
	static final int NORMAL = 1;
	static final float START_X = 0, START_Y = 0.5f;
	private static final float[] SIZES = {0.8f, 1f, 1.25f};
	static final float[] FX_ALPHA = {0.25f, 0.5f, 0.75f, 1f}, FX_GLOW = {0f, 0.5f, 1f}, FX_SHAKE = {0f, 0.4f, 1f}, FX_ALLY = {0f, 0.25f, 0.5f, 1f};
	private static final String FILE = "ashbound-hud.properties", NUMBERS = "hit_numbers", OLD_METERS = "party_meters",
			SHOW = "meter_show", VIEW = "meter_view", SIZE = "meter_size", X = "meter_x", Y = "meter_y",
			FX_SEE = "fx_opacity", FX_SHINE = "fx_glow", FX_KICK = "fx_shake", FX_FLASH = "fx_flash", FX_LINES = "fx_lines", FX_ALLIES = "fx_allies", ALLY_GLOW = "ally_glow";

	static boolean numbers = true;
	static int meterShow = IN_FIGHTS, meterView = BOTH, meterSize = NORMAL;
	static float meterX = START_X, meterY = START_Y;
	static int fxSee = FX_ALPHA.length - 1, fxShine = FX_GLOW.length - 1, fxKick = FX_SHAKE.length - 1;
	static boolean fxFlash = true, fxLines = true;
	/** other players' skill and spell effects, as a share of how they'd be drawn (0: not at all); party members outlined */
	static int fxAllies = FX_ALLY.length - 1;
	static boolean allyGlow;

	static float fxAlly() {
		return FX_ALLY[fxAllies];
	}

	/** Whether this one is outlined for you: a party member, with Glowing allies on (mixin/TossedGlowMixin, AllyGlowMixin). */
	public static boolean glowsForMe(net.minecraft.world.entity.Entity e) {
		var mc = net.minecraft.client.Minecraft.getInstance();
		if (!allyGlow || !(e instanceof net.minecraft.world.entity.player.Player p) || p == mc.player || p.isSpectator()) return false;
		String name = p.getGameProfile().getName();
		return com.snoringwalrus.ashbound.Net.clientParty.stream().anyMatch(m -> m.name().equals(name));
	}

	static float scale() {
		return SIZES[meterSize];
	}

	/** how much of a skill's effect is drawn: 1 is all of it */
	static float fxAlpha() {
		return FX_ALPHA[fxSee];
	}

	static float fxGlow() {
		return FX_GLOW[fxShine];
	}

	static float fxShake() {
		return FX_SHAKE[fxKick];
	}

	private static Path file() {
		return FMLPaths.CONFIGDIR.get().resolve(FILE);
	}

	static void load() {
		Path f = file();
		if (!Files.exists(f)) return;
		Properties p = new Properties();
		try (var in = Files.newInputStream(f)) {
			p.load(in);
		} catch (IOException e) {
			return;
		}
		numbers = !"false".equals(p.getProperty(NUMBERS));
		meterShow = whole(p, SHOW, "false".equals(p.getProperty(OLD_METERS)) ? OFF : IN_FIGHTS, ALWAYS);
		meterView = whole(p, VIEW, BOTH, ONLY_HEALING);
		meterSize = whole(p, SIZE, NORMAL, SIZES.length - 1);
		meterX = share(p, X, START_X);
		meterY = share(p, Y, START_Y);
		fxSee = whole(p, FX_SEE, FX_ALPHA.length - 1, FX_ALPHA.length - 1);
		fxShine = whole(p, FX_SHINE, FX_GLOW.length - 1, FX_GLOW.length - 1);
		fxKick = whole(p, FX_KICK, FX_SHAKE.length - 1, FX_SHAKE.length - 1);
		fxFlash = !"false".equals(p.getProperty(FX_FLASH));
		fxLines = !"false".equals(p.getProperty(FX_LINES));
		fxAllies = whole(p, FX_ALLIES, FX_ALLY.length - 1, FX_ALLY.length - 1);
		allyGlow = "true".equals(p.getProperty(ALLY_GLOW));
	}

	private static int whole(Properties p, String key, int otherwise, int most) {
		try {
			return Math.clamp(Integer.parseInt(p.getProperty(key, "")), 0, most);
		} catch (NumberFormatException e) {
			return otherwise;
		}
	}

	private static float share(Properties p, String key, float otherwise) {
		try {
			return Math.clamp(Float.parseFloat(p.getProperty(key, "")), 0f, 1f);
		} catch (NumberFormatException e) {
			return otherwise;
		}
	}

	static void save() {
		Properties p = new Properties();
		p.setProperty(NUMBERS, String.valueOf(numbers));
		p.setProperty(SHOW, String.valueOf(meterShow));
		p.setProperty(VIEW, String.valueOf(meterView));
		p.setProperty(SIZE, String.valueOf(meterSize));
		p.setProperty(X, String.valueOf(meterX));
		p.setProperty(Y, String.valueOf(meterY));
		p.setProperty(FX_SEE, String.valueOf(fxSee));
		p.setProperty(FX_SHINE, String.valueOf(fxShine));
		p.setProperty(FX_KICK, String.valueOf(fxKick));
		p.setProperty(FX_FLASH, String.valueOf(fxFlash));
		p.setProperty(FX_LINES, String.valueOf(fxLines));
		p.setProperty(FX_ALLIES, String.valueOf(fxAllies));
		p.setProperty(ALLY_GLOW, String.valueOf(allyGlow));
		try (var out = Files.newOutputStream(file())) {
			p.store(out, null);
		} catch (IOException ignored) {
			// it only costs them the setting next launch
		}
	}
}
