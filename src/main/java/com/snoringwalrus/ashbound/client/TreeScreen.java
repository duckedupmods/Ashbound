package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;

import org.lwjgl.glfw.GLFW;

import com.google.gson.JsonObject;
import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.math.Axis;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Levels;
import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Passives;

import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.ConfirmScreen;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.TextColor;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * The Ash Tree (K, in place of Epic Fight's skill screen; docs/SKILLTREE.md). The overview is a burning ash tree: the
 * trunk is the Core, a branch runs up to each weapon's emblem, and the points you spend climb each branch as fire.
 * Click an emblem and its page opens: about fourteen nodes drawn on the weapon's own picture. Stat nodes take several
 * points (the pips under them); ember nodes change a move, gold ones add one, the red keystone at the tip needs
 * points in the area first. Click to take a point, right-click to take one back for Ash, Esc back to the tree.
 */
public class TreeScreen extends Screen {
	private static final ResourceLocation ICONS = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/gui/tree_icons.png");
	private static final ResourceLocation FRAMES = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/gui/tree_frames.png");
	/** the overview's painting (tools/blender/tree_ui.py), 2400x900: the 1600x900 the paths are in, 400 spare each side */
	private static final ResourceLocation EMBLEMS = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/gui/tree_emblems.png");
	private static final ResourceLocation TREE = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/gui/tree_bg.png");
	private static final int TOP = 32, TAB = 34;
	private static final List<String> ROLES = List.of("stat", "ember", "gold", "key", "emblem");
	private static final float[][] ASH = new float[260][4];

	static {
		Random r = new Random(11);
		for (float[] s : ASH) {
			s[0] = r.nextFloat();
			s[1] = r.nextFloat();
			s[2] = 0.3f + r.nextFloat() * 0.7f;
			s[3] = r.nextFloat();
		}
	}

	/** null: the overview; otherwise the area whose page is open */
	private String page;
	private float zoom = 1, panX, panY, midX, midY;
	private double downX, downY;
	private boolean dragged;
	private Button levelUp, reset;
	private Passives.Node hover;
	private String hotEmblem;

	public TreeScreen() {
		super(Component.literal("The Ash Tree"));
	}

	@Override
	protected void init() {
		levelUp = addRenderableWidget(Button.builder(Component.literal("Level up"), b -> act(2, "")).bounds(width - 196, 6, 100, 20).build());
		reset = addRenderableWidget(Button.builder(Component.literal("Reset tree"), b -> minecraft.setScreen(new ConfirmScreen(yes -> {
			if (yes) act(3, "");
			minecraft.setScreen(this);
		}, Component.literal("Take back every point?"), Component.literal("It costs " + Passives.resetCost(Levels.clientLevel) + " Ash."))))
				.bounds(width - 92, 6, 86, 20).build());
		if (page != null) open(page);
	}

	private static void act(int action, String node) {
		PacketDistributor.sendToServer(new Net.TreeAct(action, node));
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float delta) {}

	// ---------------------------------------------------------------- helpers

	private static boolean owned(String id) {
		return id.equals(Passives.start) || Passives.clientTaken.contains(id);
	}

	private static int rank(String id) {
		return Passives.clientRanks.getOrDefault(id, 0);
	}

	/** another point can go in: joined to yours, not full, and a keystone's area has its points */
	private static boolean takeable(String id) {
		Passives.Node n = Passives.NODES.get(id);
		if (n == null || id.equals(Passives.start) || rank(id) >= n.max()) return false;
		if (!owned(id) && Passives.LINKS.getOrDefault(id, Set.of()).stream().noneMatch(TreeScreen::owned)) return false;
		return !n.kind().equals("keystone") || spent(n.area()) >= Passives.keyNeed;
	}

	private static int colour(String area, float f) {
		String h = Passives.AREA_COLOURS.getOrDefault(area, "#c0c0c0");
		int r = (int) (Integer.parseInt(h.substring(1, 3), 16) * f), g = (int) (Integer.parseInt(h.substring(3, 5), 16) * f),
				b = (int) (Integer.parseInt(h.substring(5, 7), 16) * f);
		return 0xFF000000 | Math.min(255, r) << 16 | Math.min(255, g) << 8 | Math.min(255, b);
	}

	private static int spent(String area) {
		int n = 0;
		for (Map.Entry<String, Integer> e : Passives.clientRanks.entrySet()) {
			Passives.Node nd = Passives.NODES.get(e.getKey());
			if (nd != null && nd.area().equals(area)) n += e.getValue();
		}
		return n;
	}

	private static float filled(String area) {
		return Math.min(1f, spent(area) / (float) Math.max(1, Passives.AREA_POINTS.getOrDefault(area, 27)));
	}

	/** one straight line, a single quad turned to its angle */
	private static void line(GuiGraphics g, float x0, float y0, float x1, float y1, float w, int c) {
		float len = (float) Math.hypot(x1 - x0, y1 - y0);
		var p = g.pose();
		p.pushPose();
		p.translate(x0, y0, 0);
		p.mulPose(Axis.ZP.rotation((float) Math.atan2(y1 - y0, x1 - x0)));
		p.scale(1, Math.max(1, w), 1);
		g.fill(0, 0, Math.round(len + Math.max(1, w) * 0.3f), 1, c);
		p.popPose();
	}

	private static void line(GuiGraphics g, float x0, float y0, float x1, float y1, float w, int c, boolean centred) {
		float a = (float) Math.atan2(y1 - y0, x1 - x0), h = Math.max(1, w) / 2;
		line(g, x0 + (float) Math.sin(a) * h, y0 - (float) Math.cos(a) * h, x1 + (float) Math.sin(a) * h, y1 - (float) Math.cos(a) * h, w, c);
	}

	private static void icon(GuiGraphics g, int cell, float x, float y, float size, float dim) {
		g.setColor(dim, dim, dim, 1f);
		var p = g.pose();
		p.pushPose();
		p.translate(x, y, 0);
		p.scale(size / 16f, size / 16f, 1);
		g.blit(ICONS, 0, 0, 16, 16, (cell % 16) * 16, (cell / 16) * 16, 16, 16, 256, Passives.iconRows * 16);
		p.popPose();
		g.setColor(1f, 1f, 1f, 1f);
	}

	/** a cell of the frames sheet (128px: rows stat ember gold key emblem; columns locked open taken, glow, disc) */
	private static void sprite(GuiGraphics g, int col, int row, float cx, float cy, float size, int argb) {
		g.setColor((argb >> 16 & 255) / 255f, (argb >> 8 & 255) / 255f, (argb & 255) / 255f, (argb >>> 24) / 255f);
		RenderSystem.enableBlend();
		var p = g.pose();
		p.pushPose();
		p.translate(cx - size / 2, cy - size / 2, 0);
		p.scale(size / 128f, size / 128f, 1);
		g.blit(FRAMES, 0, 0, 128, 128, col * 128, row * 128, 128, 128, 512, 640);
		p.popPose();
		g.setColor(1f, 1f, 1f, 1f);
	}

	/** light that adds up: glows, embers, fire on the branches */
	private static void additive(boolean on) {
		if (on) {
			RenderSystem.enableBlend();
			RenderSystem.blendFunc(GlStateManager.SourceFactor.SRC_ALPHA, GlStateManager.DestFactor.ONE);
		} else RenderSystem.defaultBlendFunc();
	}

	private static void glow(GuiGraphics g, float x, float y, float size, int argb) {
		sprite(g, 3, 0, x, y, size, argb);
	}

	/** a cut-corner frame like the rest of the mod's screens */
	private static void frame(GuiGraphics g, int x0, int y0, int x1, int y1, int edge, int fill) {
		g.fill(x0 + 2, y0, x1 - 2, y1, edge);
		g.fill(x0, y0 + 2, x1, y1 - 2, edge);
		g.fill(x0 + 2, y0 + 1, x1 - 2, y1 - 1, fill);
		g.fill(x0 + 1, y0 + 2, x1 - 1, y1 - 2, fill);
	}

	private void wrap(GuiGraphics g, String text, int x, int w, int colour, int[] at) {
		for (FormattedCharSequence ln : font.split(Component.literal(text), w)) {
			g.drawString(font, ln, x, at[0], colour, false);
			at[0] += 10;
		}
	}

	private void text(GuiGraphics g, String s, float x, float y, float scale, int colour) {
		var p = g.pose();
		p.pushPose();
		p.translate(x - font.width(s) * scale / 2, y, 0);
		p.scale(scale, scale, 1);
		g.drawString(font, s, 0, 0, colour, true);
		p.popPose();
	}

	/** the dark ground, a warm glow from below */
	private void ground(GuiGraphics g) {
		g.fill(0, 0, width, height, 0xFF0E0A09);
		additive(true);
		glow(g, width / 2f, height * 1.02f, Math.max(width, height) * 1.3f, 0x70A0400F);
		additive(false);
	}

	/** ash drifting down */
	private void ash(GuiGraphics g) {
		float t = (System.currentTimeMillis() % 600000L) / 1000f;
		for (float[] s : ASH) {
			float y = (s[1] + t * 0.012f * s[2]) % 1f, x = s[0] + (float) Math.sin(t * 0.4f + s[3] * 6) * 0.004f;
			int c = Math.round(40 + 50 * s[2]);
			int px = Math.round(x * width), py = Math.round(y * height);
			g.fill(px, py, px + 1, py + 1, 0xFF000000 | c << 16 | (c - 8) << 8 | (c - 14));
		}
	}

	// ---------------------------------------------------------------- render

	@Override
	public void render(GuiGraphics g, int mx, int my, float delta) {
		ground(g);
		if (page == null) overview(g, mx, my);
		else {
			ash(g);
			page(g, mx, my);
		}
		// the bar along the top
		g.fill(0, 0, width, TOP, 0xF0120D0B);
		g.fill(0, TOP, width, TOP + 1, 0xFF8A4A1C);
		g.drawString(font, "THE ASH TREE", 8, 6, 0xFFFFB050, true);
		String info = "Level " + Levels.clientLevel + "   Points " + Passives.clientPoints + "   Ash " + Levels.clientAsh
				+ (Levels.clientNext > 0 ? " / " + Levels.clientNext : "");
		g.drawString(font, info, 8, 19, 0xFFD8C8B0, true);
		levelUp.active = Levels.clientNext > 0 && Levels.clientAsh >= Levels.clientNext;
		levelUp.setMessage(Component.literal(levelUp.active ? "Level up!" : "Level up"));
		reset.active = !Passives.clientTaken.isEmpty();
		super.render(g, mx, my, delta);
		if (page == null && hotEmblem != null) g.renderComponentTooltip(font, emblemTip(hotEmblem), mx, my);
	}

	// the overview: the burning tree

	private float os() {
		return Math.min(width / 1600f, (height - TOP) / 900f);
	}

	private float ox(float x) {
		return (width - 1600 * os()) / 2 + x * os();
	}

	private float oy(float y) {
		return TOP + (height - TOP - 900 * os()) / 2 + y * os();
	}

	private static float[][] pts(JsonObject limb) {
		return Passives.points(limb.get("pts"));
	}

	private void overview(GuiGraphics g, int mx, int my) {
		JsonObject ov = Passives.overview;
		if (ov == null) return;
		float s = os(), t = (System.currentTimeMillis() % 600000L) / 1000f;
		// the painted tree, filling the same 1600x900 space the paths are in
		var ps = g.pose();
		ps.pushPose();
		ps.translate(ox(-400), oy(0), 0);
		ps.scale(s, s, 1);
		g.blit(TREE, 0, 0, 0, 0, 2400, 900, 2400, 900);
		ps.popPose();
		ash(g);
		JsonObject br = ov.getAsJsonObject("branches"), em = ov.getAsJsonObject("emblems");
		List<String> ar = areas();
		// fire: the Core's cracks up the trunk, then each branch lit as far as its points go
		additive(true);
		float[][] tr = pts(ov.getAsJsonObject("trunk"));
		float core = 0.35f + 0.65f * filled("core");
		// warmth rising up the trunk in slow pulses
		for (int i = 0; i < tr.length; i++) {
			float pulse = 0.5f + 0.5f * (float) Math.sin(i * 0.7f - t * 2.2f);
			glow(g, ox(tr[i][0]), oy(tr[i][1]), 90 * s, alpha(core * (0.12f + 0.22f * pulse), 0xFF5A14));
		}
		for (String a : ar) {
			float f = filled(a);
			if (f <= 0) continue;
			float[][] p = pts(br.getAsJsonObject(a));
			int n = Math.round(f * (p.length - 1));
			for (int i = 0; i < n; i++) {
				float x = ox(p[i][0]), y = oy(p[i][1]);
				glow(g, x, y, 46 * s, 0x50FF6A1A);
				line(g, x, y, ox(p[i + 1][0]), oy(p[i + 1][1]), Math.max(1.5f, 5 * s), 0xFFFF8A2A, true);
				if (i % 4 == 0) glow(g, x, y, 16 * s, 0xFFFFC870);
			}
			// sparks drifting up off the lit part
			for (int k = 0; k < 6 + n; k++) {
				float ph = (k * 0.618f + t * (0.25f + (k % 3) * 0.08f)) % 1f;
				float[] q = p[(k * 7) % Math.max(1, n)];
				float x = ox(q[0]) + (float) Math.sin(t * 2 + k) * 6 * s, y = oy(q[1]) - ph * 90 * s;
				glow(g, x, y, Math.max(2, 7 * s), alpha(1 - ph, 0xFFB050));
			}
		}
		additive(false);
		// the emblems, the Core at the foot
		hotEmblem = null;
		var c = ov.getAsJsonArray("core");
		emblem(g, "core", ox(c.get(0).getAsFloat()), oy(c.get(1).getAsFloat()), Math.max(30, 112 * s), mx, my);
		for (String a : ar) {
			var e = em.getAsJsonArray(a);
			emblem(g, a, ox(e.get(0).getAsFloat()), oy(e.get(1).getAsFloat()), Math.max(24, 88 * s), mx, my);
		}
		String hint = "Click a branch to open it";
		g.drawString(font, hint, (width - font.width(hint)) / 2, height - 12, 0xFF8A7A6A, true);
	}

	private static int alpha(float a, int rgb) {
		return Math.round(Mth.clamp(a, 0, 1) * 255) << 24 | rgb;
	}

	private void emblem(GuiGraphics g, String area, float x, float y, float size, int mx, int my) {
		boolean hot = Math.hypot(mx - x, my - y) <= size / 2;
		if (hot) hotEmblem = area;
		float f = filled(area);
		if (f > 0 || hot) {
			additive(true);
			glow(g, x, y, size * 1.9f, hot ? 0x70FFB060 : 0x48FF7A20);
			additive(false);
		}
		sprite(g, f > 0 ? 2 : hot ? 1 : 0, 4, x, y, size, 0xFFFFFFFF);
		emblemArt(g, area, x, y, size * 0.66f, f > 0 || hot ? 1f : 0.6f);
		// progress round the rim, gold
		int dots = 28, lit = Math.round(f * dots);
		for (int i = 0; i < dots; i++) {
			double a = -Math.PI / 2 + i * Math.PI * 2 / dots;
			float r = size / 2 + Math.max(2, size * 0.06f);
			sprite(g, 3, 1, x + (float) Math.cos(a) * r, y + (float) Math.sin(a) * r, Math.max(2, size * 0.055f), i < lit ? 0xFFFFD27A : 0xFF3A302A);
		}
		float ts = Mth.clamp(size / 70f, 0.6f, 1f);
		text(g, Passives.AREA_NAMES.get(area).toUpperCase(), x, y + size / 2 + size * 0.12f + 2, ts, f > 0 ? 0xFFFFD27A : 0xFFE8D8C0);
		String n = spent(area) + " / " + Passives.AREA_POINTS.getOrDefault(area, 0);
		text(g, n, x, y + size / 2 + size * 0.12f + 2 + 10 * ts, ts * 0.9f, 0xFF9A8A7A);
	}

	/** an area's rendered weapon (its emblem), centred */
	private static void emblemArt(GuiGraphics g, String area, float x, float y, float size, float dim) {
		int cell = Passives.AREA_EMBLEMS.getOrDefault(area, 0);
		g.setColor(dim, dim, dim, 1f);
		RenderSystem.enableBlend();
		var p = g.pose();
		p.pushPose();
		p.translate(x - size / 2, y - size / 2, 0);
		p.scale(size / 128f, size / 128f, 1);
		g.blit(EMBLEMS, 0, 0, 128, 128, (cell % 4) * 128, (cell / 4) * 128, 128, 128, 512, 384);
		p.popPose();
		g.setColor(1f, 1f, 1f, 1f);
	}

	private static List<String> areas() {
		List<String> l = new ArrayList<>(Passives.AREA_NAMES.keySet());
		l.remove("core");
		return l;
	}

	private static List<Component> emblemTip(String area) {
		List<Component> l = new ArrayList<>();
		l.add(Component.literal(Passives.AREA_NAMES.get(area)).withStyle(s -> s.withColor(TextColor.fromRgb(colour(area, 1f) & 0xFFFFFF)).withBold(true)));
		l.add(Component.literal(spent(area) + " of " + Passives.AREA_POINTS.getOrDefault(area, 0) + " points").withStyle(ChatFormatting.GOLD));
		for (String id : Passives.PAGES.getOrDefault(area, Map.of()).keySet()) {
			Passives.Node nd = Passives.NODES.get(id);
			if (nd != null && !nd.kind().equals("small") && owned(id))
				l.add(Component.literal("  " + nd.name()).withStyle(nd.kind().equals("keystone") ? ChatFormatting.RED : ChatFormatting.YELLOW));
		}
		l.add(Component.literal(area.equals("core") ? "always counts" : "counts while you hold its weapon").withStyle(ChatFormatting.DARK_GRAY));
		l.add(Component.literal("Click to open").withStyle(ChatFormatting.GREEN));
		return l;
	}

	// a page: tabs, the weapon's picture with its nodes, the side panel

	private int info() {
		return Mth.clamp(width / 4, 130, 210);
	}

	private int px0() {
		return TAB + 6;
	}

	private int px1() {
		return width - info() - 6;
	}

	private int py0() {
		return TOP + 6;
	}

	private int py1() {
		return height - 6;
	}

	private int tab() {
		return Mth.clamp((height - TOP - 10) / Passives.AREA_NAMES.size() - 2, 14, 28);
	}

	/** opens an area's page, fitted to the room there is */
	private void open(String area) {
		page = area;
		List<float[]> all = new ArrayList<>(Passives.PAGES.getOrDefault(area, Map.of()).values());
		for (float[][] ln : Passives.FIGURES.getOrDefault(area, List.of())) all.addAll(List.of(ln));
		float x0 = Float.MAX_VALUE, x1 = -Float.MAX_VALUE, y0 = Float.MAX_VALUE, y1 = -Float.MAX_VALUE;
		for (float[] p : all) {
			x0 = Math.min(x0, p[0]);
			x1 = Math.max(x1, p[0]);
			y0 = Math.min(y0, p[1]);
			y1 = Math.max(y1, p[1]);
		}
		midX = (x0 + x1) / 2;
		midY = (y0 + y1) / 2;
		panX = panY = 0;
		float w = px1() - px0() - 40, h = py1() - py0() - 60;
		zoom = Math.min(w / Math.max(1, x1 - x0), h / Math.max(1, y1 - y0));
	}

	private float sx(float x) {
		return (px0() + px1()) / 2f + (x - midX + panX) * zoom;
	}

	private float sy(float y) {
		return (py0() + 20 + py1()) / 2f + (y - midY + panY) * zoom;
	}

	private float size(Passives.Node n) {
		float base = switch (n.role()) {
			case "stat" -> 44;
			case "key" -> 76;
			case "gold" -> 62;
			default -> 56;
		};
		return Math.max(n.role().equals("stat") ? 12 : 16, base * zoom);
	}

	private void page(GuiGraphics g, int mx, int my) {
		// tabs
		List<String> all = new ArrayList<>(Passives.AREA_NAMES.keySet());
		int t = tab();
		for (int i = 0; i < all.size(); i++) {
			String a = all.get(i);
			int y = TOP + 6 + i * (t + 2);
			boolean on = a.equals(page);
			frame(g, 4, y, 4 + t, y + t, on ? 0xFFFFB050 : spent(a) > 0 ? 0xFF8A5A30 : 0xFF3A302A, on ? 0xFF3A2416 : 0xFF1A1512);
			emblemArt(g, a, 4 + t / 2f, y + t / 2f, t + 2, on ? 1f : 0.6f);
			int n = spent(a);
			if (n > 0) g.drawString(font, String.valueOf(n), 4 + t + 2, y + t - 8, 0xFFFFB050, true);
		}
		frame(g, px0(), py0(), px1(), py1(), 0xFF4A3C32, 0xC0120E0C);
		g.enableScissor(px0() + 1, py0() + 1, px1() - 1, py1() - 1);
		// the weapon's picture, brighter the more of it is yours
		float f = filled(page);
		int fig = colour(page, 0.22f + 0.5f * f);
		for (float[][] ln : Passives.FIGURES.getOrDefault(page, List.of()))
			for (int i = 0; i < ln.length - 1; i++) line(g, sx(ln[i][0]), sy(ln[i][1]), sx(ln[i + 1][0]), sy(ln[i + 1][1]), Math.max(1, 3 * zoom), fig, true);
		// links: dark, or fire between two of yours
		Map<String, float[]> pg = Passives.PAGES.getOrDefault(page, Map.of());
		for (Map.Entry<String, float[]> e : pg.entrySet())
			for (String b : Passives.LINKS.getOrDefault(e.getKey(), Set.of())) {
				float[] pb = pg.get(b);
				if (pb == null || e.getKey().compareTo(b) > 0) continue;
				float x0 = sx(e.getValue()[0]), y0 = sy(e.getValue()[1]), x1 = sx(pb[0]), y1 = sy(pb[1]);
				if (owned(e.getKey()) && owned(b)) {
					additive(true);
					line(g, x0, y0, x1, y1, Math.max(4, 12 * zoom), 0x40FF6A1A, true);
					additive(false);
					line(g, x0, y0, x1, y1, Math.max(2, 4 * zoom), 0xFFFF9A40, true);
				} else line(g, x0, y0, x1, y1, Math.max(1.5f, 4 * zoom), 0xFF4A3E35, true);
			}
		hover = null;
		long now = System.currentTimeMillis();
		float labels = Mth.clamp(zoom * 1.4f, 0.6f, 1f);
		for (Map.Entry<String, float[]> e : pg.entrySet()) {
			Passives.Node n = Passives.NODES.get(e.getKey());
			if (n == null) continue;
			float x = sx(e.getValue()[0]), y = sy(e.getValue()[1]), s = size(n);
			boolean have = owned(n.id()), can = takeable(n.id());
			boolean hot = mx > px0() && mx < px1() && my > py0() && my < py1() && Math.hypot(mx - x, my - y) <= s / 2;
			if (hot) hover = n;
			if (have || hot || can) {
				additive(true);
				float pulse = can && !have ? 0.5f + 0.5f * (float) Math.sin(now / 300.0) : 1;
				glow(g, x, y, s * 2.1f, hot ? 0x80FFC070 : have ? 0x58FF7A20 : alpha(0.3f * pulse, 0xFFA040));
				additive(false);
			}
			int row = Math.max(0, ROLES.indexOf(n.role()));
			sprite(g, have ? 2 : can ? 1 : 0, row, x, y, s, 0xFFFFFFFF);
			float is = s * (n.role().equals("stat") ? 0.5f : 0.56f);
			icon(g, n.icon(), x - is / 2, y - is / 2, is, have ? 1f : can ? 0.75f : 0.4f);
			if (n.ef() != null) {
				float m = Math.max(3, s / 6);
				g.fill(Math.round(x + s * 0.3f), Math.round(y - s * 0.42f), Math.round(x + s * 0.3f + m), Math.round(y - s * 0.42f + m),
						Passives.clientEquipped.contains(n.ef()) ? 0xFF8CD0FF : 0xFF3C6CA0);
			}
			float below = y + s / 2 + 2;
			if (n.max() > 1) {  // rank pips
				int r = rank(n.id());
				float pw = Math.max(2, s * 0.13f), gap = pw * 0.5f, x0 = x - (n.max() * (pw + gap) - gap) / 2;
				for (int k = 0; k < n.max(); k++)
					g.fill(Math.round(x0 + k * (pw + gap)), Math.round(below), Math.round(x0 + k * (pw + gap) + pw), Math.round(below + Math.max(2, pw * 0.6f)),
							k < r ? 0xFFFFD27A : 0xFF3E342C);
				below += Math.max(2, pw * 0.6f) + 2;
			}
			text(g, n.name(), x, below + 1, labels * (n.role().equals("stat") ? 0.85f : 1f), have ? 0xFFFFE0B0 : can ? 0xFFC8B8A0 : 0xFF8A7A6A);
		}
		g.disableScissor();
		g.drawString(font, Passives.AREA_NAMES.get(page).toUpperCase(), px0() + 10, py0() + 8, colour(page, 1f), true);
		String sub = spent(page) + " / " + Passives.AREA_POINTS.getOrDefault(page, 0) + " points" + (page.equals("core") ? "   always counts" : "   counts while you hold its weapon");
		g.drawString(font, sub, px0() + 10, py0() + 20, 0xFF8A7A6A, false);
		side(g);
	}

	private static final Map<String, String> STAT_NAMES = new LinkedHashMap<>();

	static {
		String[][] s = {{"health%", "% health"}, {"stamina", " max stamina"}, {"stamina_regen%", "% stamina regen"}, {"move%", "% move speed"},
				{"armour", " armour"}, {"stun_armour", " stun armour"}, {"weight%", "% armour weight"}, {"mana", " max mana"},
				{"mana_regen%", "% mana regen"}, {"dmg%", "% damage"}, {"speed%", "% attack speed"}, {"negation%", "% armour negation"},
				{"impact", " impact"}, {"reach", " reach"}, {"strikes", " enemies per swing"}, {"knockback", " knockback"},
				{"guard%", "% stamina back on a block"}, {"arrow%", "% arrow damage"}, {"velocity%", "% arrow speed"},
				{"spell%", "% spell power"}, {"heal%", "% healing"}, {"thrall_hp%", "% thrall health"}, {"thrall_dmg%", "% thrall damage"},
				{"ash%", "% Ash"}};
		for (String[] p : s) STAT_NAMES.put(p[0], p[1]);
	}

	private static String role(Passives.Node n) {
		return switch (n.role()) {
			case "key" -> "Keystone: big, with a cost";
			case "gold" -> n.ef() != null ? "A new skill" : "A new move";
			case "ember" -> "Changes how you fight";
			default -> n.kind().equals("start") ? "Where every path starts" : "Stat: up to " + n.max() + " points";
		};
	}

	private void side(GuiGraphics g) {
		int x0 = width - info(), top = py0();
		frame(g, x0, top, width - 6, py1(), 0xFF4A3C32, 0xE0120E0C);
		int w = width - 6 - x0 - 16;
		x0 += 8;
		int[] y = {top + 8};
		if (hover != null) {
			Passives.Node n = hover;
			boolean have = owned(n.id());
			sprite(g, have ? 2 : 1, Math.max(0, ROLES.indexOf(n.role())), x0 + 18, y[0] + 18, 36, 0xFFFFFFFF);
			icon(g, n.icon(), x0 + 8, y[0] + 8, 20, 1f);
			int ny = y[0] + 4;
			for (FormattedCharSequence ln : font.split(Component.literal(n.name()).withStyle(ChatFormatting.BOLD), w - 42)) {
				g.drawString(font, ln, x0 + 42, ny, colour(n.area(), 1f), true);
				ny += 10;
			}
			int rc = switch (n.role()) {
				case "key" -> 0xFFF05050;
				case "gold" -> 0xFFFFD27A;
				case "ember" -> 0xFFFF9A40;
				default -> 0xFFB8A898;
			};
			g.drawString(font, role(n), x0 + 42, ny + 2, rc, false);
			y[0] = Math.max(ny + 16, top + 52);
			wrap(g, n.about(), x0, w, 0xFFD8C8B0, y);
			if (n.max() > 1) {
				y[0] += 4;
				wrap(g, "Points: " + rank(n.id()) + " / " + n.max(), x0, w, 0xFFFFD27A, y);
			}
			if (n.kind().equals("keystone")) {
				y[0] += 4;
				wrap(g, "Needs " + Passives.keyNeed + " points in " + Passives.AREA_NAMES.get(n.area()) + " (you have " + spent(n.area()) + "). One keystone at a time.",
						x0, w, 0xFF9A8A7A, y);
			}
			y[0] += 8;
			if (n.ef() != null) {
				boolean eq = Passives.clientEquipped.contains(n.ef());
				wrap(g, have ? eq ? "Epic Fight skill: equipped (click to unequip)" : "Epic Fight skill: off (click to equip)"
						: "Unlocks an Epic Fight skill", x0, w, 0xFF8CD0FF, y);
				y[0] += 6;
			}
			String act = takeable(n.id()) ? Passives.clientPoints > 0 ? "Click: put a point in" : "No points left: level up with Ash"
					: have && rank(n.id()) >= n.max() ? "" : have ? "" : n.kind().equals("keystone") && spent(n.area()) < Passives.keyNeed
					? "Spend more points here first" : "Take a node next to it first";
			if (!act.isEmpty()) wrap(g, act, x0, w, act.startsWith("Click") ? 0xFF7CE07C : 0xFF9A8A7A, y);
			if (have && !n.id().equals(Passives.start))
				wrap(g, "Right-click: take a point back for " + Passives.refundCost(Levels.clientLevel) + " Ash", x0, w, 0xFF9A8A7A, y);
			return;
		}
		// nothing under the cursor: what this page gives you
		g.drawString(font, "THIS PAGE GIVES YOU", x0, y[0], 0xFFE8963C, true);
		y[0] += 14;
		Map<String, Double> sum = new LinkedHashMap<>();
		List<String> extra = new ArrayList<>();
		for (Map.Entry<String, Integer> e : Passives.clientRanks.entrySet()) {
			Passives.Node n = Passives.NODES.get(e.getKey());
			if (n == null || !n.area().equals(page)) continue;
			n.stats().forEach((k, v) -> sum.merge(k, v * e.getValue(), Double::sum));
			if (!n.kind().equals("small")) extra.add(n.name());
		}
		if (sum.isEmpty() && extra.isEmpty()) {
			wrap(g, "Nothing yet. Glowing nodes are ones you can take.", x0, w, 0xFF9A8A7A, y);
		} else {
			for (Map.Entry<String, Double> e : sum.entrySet()) {
				double v = e.getValue();
				String s = (v > 0 ? "+" : "") + (v == Math.floor(v) ? String.valueOf((int) v) : String.format(java.util.Locale.ROOT, "%.1f", v))
						+ STAT_NAMES.getOrDefault(e.getKey(), " " + e.getKey());
				wrap(g, s, x0, w, 0xFFD8C8B0, y);
			}
			for (String s : extra) wrap(g, s, x0, w, 0xFFFFD8A0, y);
		}
		// what the shapes mean
		y[0] = Math.max(y[0] + 10, py1() - 62);
		String[][] key = {{"stat", "stat: several points"}, {"ember", "changes a move"}, {"gold", "a new move or skill"}, {"key", "keystone"}};
		for (String[] k : key) {
			sprite(g, 2, ROLES.indexOf(k[0]), x0 + 6, y[0] + 4, 11, 0xFFFFFFFF);
			g.drawString(font, k[1], x0 + 16, y[0], 0xFF9A8A7A, false);
			y[0] += 13;
		}
	}

	// ---------------------------------------------------------------- input

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		if (super.mouseClicked(mx, my, button)) return true;
		downX = mx;
		downY = my;
		dragged = false;
		return true;
	}

	@Override
	public boolean mouseDragged(double mx, double my, int button, double dx, double dy) {
		if (page == null) return true;
		if (Math.abs(mx - downX) + Math.abs(my - downY) > 3) dragged = true;
		if (dragged) {
			panX += (float) (dx / zoom);
			panY += (float) (dy / zoom);
		}
		return true;
	}

	@Override
	public boolean mouseReleased(double mx, double my, int button) {
		super.mouseReleased(mx, my, button);
		if (dragged || my < TOP) return true;
		if (page == null) {
			if (hotEmblem != null) open(hotEmblem);
			return true;
		}
		// a tab
		if (mx < TAB + 4) {
			List<String> all = new ArrayList<>(Passives.AREA_NAMES.keySet());
			int i = (int) ((my - TOP - 6) / (tab() + 2));
			if (i >= 0 && i < all.size()) open(all.get(i));
			return true;
		}
		Passives.Node n = hover;
		if (n == null) return true;
		if (button == 1 && owned(n.id())) act(1, n.id());
		else if (button == 0 && takeable(n.id())) act(0, n.id());
		else if (button == 0 && owned(n.id()) && n.ef() != null) act(4, n.id());
		return true;
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double sx, double sy) {
		if (page == null) return true;
		float old = zoom;
		zoom = Mth.clamp(zoom * (sy > 0 ? 1.15f : 1 / 1.15f), 0.2f, 2.5f);
		float cx = (px0() + px1()) / 2f, cy = (py0() + 20 + py1()) / 2f;
		float wx = (float) ((mx - cx) / old - panX), wy = (float) ((my - cy) / old - panY);
		panX = (float) ((mx - cx) / zoom - wx);
		panY = (float) ((my - cy) / zoom - wy);
		return true;
	}

	@Override
	public boolean keyPressed(int key, int scan, int mods) {
		if (key == GLFW.GLFW_KEY_ESCAPE && page != null) {
			page = null;
			return true;
		}
		if (Minecraft.getInstance().options.keyInventory.matches(key, scan)) {
			onClose();
			return true;
		}
		return super.keyPressed(key, scan, mods);
	}
}
