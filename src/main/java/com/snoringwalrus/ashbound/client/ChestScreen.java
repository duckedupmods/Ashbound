package com.snoringwalrus.ashbound.client;

import org.lwjgl.glfw.GLFW;

import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Tidy;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * A chest or shulker box in our own frame, in place of the vanilla screen (InvButtons swaps it in). Middle mouse sorts, T takes all,
 * here and nowhere else; the buttons down the side say so. The server does the work, see Tidy.
 *
 * As on BagScreen, the screen's corner (leftPos, topPos) is where the Menu's slots are measured from; the panel is px, py.
 */
public class ChestScreen extends AbstractContainerScreen<AbstractContainerMenu> {
	private static final int SLOTS_W = 176, SIDE = 72, W = SLOTS_W + SIDE, IN = 4, UP = 8, FOOT = 8, BTN_H = 16, BTN_GAP = 3;
	private int px, py, panelH, packY;

	public ChestScreen(AbstractContainerMenu menu, Inventory inv, Component title) {
		super(menu, inv, title);
	}

	@Override
	protected void init() {
		int low = 0;
		packY = Integer.MAX_VALUE;
		for (var s : menu.slots) {
			low = Math.max(low, s.y);
			if (s.container == minecraft.player.getInventory()) packY = Math.min(packY, s.y);
		}
		panelH = UP + low + 16 + FOOT;
		imageWidth = W;
		imageHeight = panelH;
		super.init();
		px = leftPos;
		py = topPos;
		leftPos = px + IN;
		topPos = py + UP;
		int x = px + IN + SLOTS_W, w = SIDE - IN - 6, y = py + 26;
		addRenderableWidget(new AshUi.AshButton(x, y, w, BTN_H, Component.literal("Take all"), b -> tidy(Tidy.TAKE), true));
		addRenderableWidget(new AshUi.AshButton(x, y + BTN_H + BTN_GAP, w, BTN_H, Component.literal("Sort"), b -> tidy(Tidy.SORT), false));
		addRenderableWidget(new AshUi.AshButton(x, y + 2 * (BTN_H + BTN_GAP), w, BTN_H, Component.literal("Stash"), b -> tidy(Tidy.STASH), false));
	}

	private static void tidy(int what) {
		PacketDistributor.sendToServer(new Net.InvTidy(what));
	}

	@Override
	protected boolean hasClickedOutside(double mx, double my, int left, int top, int button) {
		return mx < px || my < py || mx >= px + W || my >= py + panelH;
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		if (button == GLFW.GLFW_MOUSE_BUTTON_MIDDLE && !minecraft.gameMode.hasInfiniteItems()) {
			tidy(Tidy.SORT);
			return true;
		}
		return super.mouseClicked(mx, my, button);
	}

	@Override
	public boolean keyPressed(int key, int scan, int mods) {
		if (key == GLFW.GLFW_KEY_T) {
			tidy(Tidy.TAKE);
			return true;
		}
		return super.keyPressed(key, scan, mods);
	}

	@Override
	protected void renderBg(GuiGraphics g, float pt, int mx, int my) {
		AshUi.panel(g, px, py, W, panelH);
		AshUi.header(g, px, py, W, 20, title.getString().toUpperCase());
		AshUi.divider(g, px + 10, topPos + packY - 7, SLOTS_W - 12);
		for (var s : menu.slots) AshUi.inset(g, leftPos + s.x - 1, topPos + s.y - 1, 18, 18);
		int x = px + IN + SLOTS_W, y = py + 26 + 3 * (BTN_H + BTN_GAP) + 4;
		g.drawString(font, "T  take all", x, y, AshUi.MUTED, false);
		g.drawString(font, "Wheel  sort", x, y + 11, AshUi.MUTED, false);
	}

	@Override
	protected void renderLabels(GuiGraphics g, int mx, int my) {
		// the header says what this is
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		renderTooltip(g, mx, my);
	}
}
