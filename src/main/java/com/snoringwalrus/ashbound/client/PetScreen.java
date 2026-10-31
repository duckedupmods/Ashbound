package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.List;

import com.mojang.blaze3d.platform.Lighting;
import com.mojang.math.Axis;
import com.snoringwalrus.ashbound.Curios;
import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Pets;

import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.network.PacketDistributor;

/** Every pet there is, rarest last: yours lit, the rest in the dark to go after. Pick one to see it, then call it to your side. */
public class PetScreen extends Screen implements MenuTabs.Panel {
	private static final int W = 330, H = 200, COLS = 6, TILE = 24, GRID_X = 12, GRID_Y = 44, SIDE_X = 168, SIDE_W = 150, TOP = 30, SHOW_H = 84, BTN_H = 18, FULL_LIGHT = 0xF000F0;
	private static final float TILT = 12, SPIN = 0.03f, FILL = 0.8f, WALK = 0.12f;
	private final long opened = System.nanoTime();
	private final List<Pets.Pet> all = new ArrayList<>(Pets.ALL.values());
	private Pets.Pet picked;
	private AshUi.AshButton call;

	public PetScreen() {
		super(Component.literal("Pets"));
		all.sort((a, b) -> a.spec().tier().compareTo(b.spec().tier()));
		PacketDistributor.sendToServer(new Net.PetAct(""));
	}

	private int left() {
		return (width - W) / 2;
	}

	private int top() {
		return (height - H) / 2;
	}

	@Override
	public int panelTop() {
		return top();
	}

	@Override
	protected void init() {
		call = addRenderableWidget(new AshUi.AshButton(left() + SIDE_X, top() + H - BTN_H - 10, SIDE_W, BTN_H, Component.empty(),
				b -> PacketDistributor.sendToServer(new Net.PetAct(picked.id())), true));
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	private static boolean owned(Pets.Pet p) {
		return Net.clientPets.owned().contains(p.id());
	}

	private Pets.Pet at(double mx, double my) {
		int cx = (int) Math.floor((mx - left() - GRID_X) / TILE), cy = (int) Math.floor((my - top() - GRID_Y) / TILE);
		if (cx < 0 || cx >= COLS || cy < 0) return null;
		int i = cy * COLS + cx;
		return i < all.size() ? all.get(i) : null;
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		Pets.Pet p = at(mx, my);
		if (p != null) {
			picked = p;
			return true;
		}
		return super.mouseClicked(mx, my, button);
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		g.fill(0, 0, width, height, 0x90000000);
		int x = left(), y = top();
		AshUi.panel(g, x, y, W, H);
		AshUi.header(g, x, y, W, 24, "PETS");
		if (picked == null) picked = all.stream().filter(p -> p.id().equals(Net.clientPets.worn())).findFirst()
				.orElse(all.stream().filter(PetScreen::owned).findFirst().orElse(all.get(0)));
		long found = all.stream().filter(PetScreen::owned).count();
		g.drawString(font, found + " of " + all.size() + " found", x + GRID_X, y + TOP + 1, AshUi.MUTED, false);
		Pets.Pet over = at(mx, my);
		for (int i = 0; i < all.size(); i++) tile(g, all.get(i), x + GRID_X + i % COLS * TILE, y + GRID_Y + i / COLS * TILE, over);
		side(g, x + SIDE_X, y + TOP);
	}

	private void tile(GuiGraphics g, Pets.Pet p, int x, int y, Pets.Pet over) {
		boolean mine = owned(p);
		AshUi.tile(g, x, y, TILE, mine ? p.spec().tier().ordinal() : 0);
		g.renderItem(new ItemStack(Curios.item(p.spec())), x + 4, y + 4);
		g.pose().pushPose();
		g.pose().translate(0, 0, 250);
		if (!mine) g.fill(x + 2, y + 2, x + TILE - 2, y + TILE - 2, 0xC4100D0B);
		if (p == picked) g.renderOutline(x, y, TILE, TILE, AshUi.EMBER_LT);
		else if (p == over) g.renderOutline(x, y, TILE, TILE, AshUi.BODY);
		if (p.id().equals(Net.clientPets.worn())) g.fill(x + TILE - 7, y + 3, x + TILE - 3, y + 7, AshUi.EMBER_LT);
		g.pose().popPose();
	}

	private void side(GuiGraphics g, int x, int y) {
		boolean mine = owned(picked), out = picked.id().equals(Net.clientPets.worn());
		AshUi.inset(g, x, y, SIDE_W, SHOW_H);
		show(g, picked, x, y, SIDE_W, SHOW_H, mine);
		int ty = y + SHOW_H + 5;
		g.drawString(font, Component.literal(picked.spec().name()).withStyle(ChatFormatting.BOLD), x, ty, AshUi.TEXT, true);
		g.drawString(font, picked.spec().tier().title + "  " + picked.spec().faction(), x, ty + 11, AshUi.RARITY_TEXT[picked.spec().tier().ordinal()], false);
		ty += 24;
		for (String line : Curios.buffs(picked.spec())) {
			g.drawString(font, line, x, ty, mine ? AshUi.BODY : AshUi.MUTED, false);
			ty += 10;
		}
		if (!mine) g.drawString(font, "Found on bosses and in chests", x, ty + 1, AshUi.MUTED, false);
		call.active = mine;
		call.setMessage(Component.literal(!mine ? "Not found yet" : out ? "Send it away" : "Call to your side"));
	}

	/** The real thing, turning: on its feet or on the wing. One you haven't found is a dark shape. */
	private void show(GuiGraphics g, Pets.Pet p, int x, int y, int w, int h, boolean mine) {
		float ticks = (System.nanoTime() - opened) / 5.0E7f, size = FILL * Math.min(w, h) / p.box()[3];
		boolean walks = p.where() == Pets.Where.HEEL;
		var ps = g.pose();
		g.enableScissor(x + 2, y + 2, x + w - 2, y + h - 2);
		ps.pushPose();
		ps.translate(x + w / 2f, y + h / 2f, 150);
		ps.scale(size, size, -size);
		ps.mulPose(Axis.ZP.rotationDegrees(180));
		ps.mulPose(Axis.XP.rotationDegrees(-TILT));
		ps.mulPose(Axis.YP.rotation(ticks * SPIN));
		ps.translate(-p.box()[0], -p.box()[1], -p.box()[2]);
		Lighting.setupForEntityInInventory();
		MountRender.pet(p.id(), ticks, walks ? ticks * WALK : 0, walks ? 0.4f : 0, !walks, 0, ps, g.bufferSource(), mine ? FULL_LIGHT : 0);
		g.flush();
		Lighting.setupFor3DItems();
		ps.popPose();
		g.disableScissor();
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		Pets.Pet p = at(mx, my);
		if (p != null) g.renderTooltip(font, Component.literal(p.spec().name()), mx, my);
	}
}
