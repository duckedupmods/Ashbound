package com.snoringwalrus.ashbound.mixin;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import net.neoforged.fml.loading.FMLLoader;
import net.neoforged.fml.loading.FMLPaths;
import org.objectweb.asm.tree.ClassNode;
import org.spongepowered.asm.mixin.extensibility.IMixinConfigPlugin;
import org.spongepowered.asm.mixin.extensibility.IMixinInfo;

/**
 * The screen layout other mods read from their own files: minimap top right, Jade's look-at box under it,
 * FancyMenu's editor bar off. A mixin plugin because this is the one thing that runs before those mods load; a marker
 * file makes it happen once, so whatever a player changes afterwards stays theirs.
 */
public class EarlyConfig implements IMixinConfigPlugin {
	private static final String MARK = "ashbound-layout-2.done", FREE_WARPS = "ashbound-warps-free.done";
	private static final String MAP = "module;id=xaerominimap:minimap;x=0;y=0;centered=false;fromRight=true;fromBottom=false;flippedVer=false;flippedHor=false;";
	/** the box's top right corner: across the screen, and up from the bottom of it */
	private static final String LOOK_X = "0.995", LOOK_Y = "0.56";

	@Override
	public void onLoad(String pkg) {
		waystones(FMLPaths.CONFIGDIR.get().resolve("waystones-common.toml"));
		if (!FMLLoader.getDist().isClient()) return;
		Path dir = FMLPaths.CONFIGDIR.get();
		try {
			if (Files.exists(dir.resolve(MARK))) return;
			map(dir.resolve("xaerohud.txt"));
			look(dir.resolve("jade/jade.json"));
			menu(dir.resolve("fancymenu/options.txt"));
			Files.writeString(dir.resolve(MARK), "");
		} catch (IOException | RuntimeException e) {
			// a layout isn't worth a crash at launch; it's tried again next time
		}
	}

	/** Warping's free: levels here are ours, and vanilla experience is what it'd charge. On servers too, once. */
	private static void waystones(Path f) {
		try {
			Path done = f.resolveSibling(FREE_WARPS);
			if (Files.exists(done)) return;
			if (Files.exists(f)) Files.writeString(f, Files.readString(f).replace("enableCosts = true", "enableCosts = false"));
			else write(f, "[teleports]\n\tenableCosts = false\n");
			Files.writeString(done, "");
		} catch (IOException | RuntimeException e) {
			// tried again next time
		}
	}

	private static void write(Path f, String text) throws IOException {
		Files.createDirectories(f.getParent());
		Files.writeString(f, text);
	}

	private static void map(Path f) throws IOException {
		if (!Files.exists(f)) {
			write(f, MAP + "\n");
			return;
		}
		String all = Files.readString(f);
		write(f, all.lines().map(l -> l.startsWith("module;id=xaerominimap:minimap;") ? MAP : l).collect(Collectors.joining("\n", "", "\n")));
	}

	private static void look(Path f) throws IOException {
		if (!Files.exists(f)) {
			write(f, "{\"overlay\":{\"overlayAnchorX\":1.0,\"overlayAnchorY\":0.0,\"overlayPosX\":" + LOOK_X + ",\"overlayPosY\":" + LOOK_Y + "}}");
			return;
		}
		write(f, Files.readString(f).replaceAll("\"overlayAnchorX\":\\s*[0-9.]+", "\"overlayAnchorX\": 1.0").replaceAll("\"overlayAnchorY\":\\s*[0-9.]+", "\"overlayAnchorY\": 0.0")
				.replaceAll("\"overlayPosX\":\\s*[0-9.]+", "\"overlayPosX\": " + LOOK_X).replaceAll("\"overlayPosY\":\\s*[0-9.]+", "\"overlayPosY\": " + LOOK_Y));
	}

	private static void menu(Path f) throws IOException {
		String off = "B:show_customization_overlay = 'false';";
		if (!Files.exists(f)) {
			write(f, "##[customization]\n\n" + off + "\n");
			return;
		}
		write(f, Files.readString(f).replaceAll("B:show_customization_overlay = '[a-z]+';", off));
	}

	@Override public String getRefMapperConfig() { return null; }
	@Override public boolean shouldApplyMixin(String target, String mixin) { return true; }
	@Override public void acceptTargets(Set<String> mine, Set<String> others) {}
	@Override public List<String> getMixins() { return null; }
	@Override public void preApply(String target, ClassNode node, String mixin, IMixinInfo info) {}
	@Override public void postApply(String target, ClassNode node, String mixin, IMixinInfo info) {}
}
