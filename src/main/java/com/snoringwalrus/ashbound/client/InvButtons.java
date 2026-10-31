package com.snoringwalrus.ashbound.client;

import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Tidy;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractButton;
import net.minecraft.client.gui.narration.NarrationElementOutput;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.gui.screens.inventory.ContainerScreen;
import net.minecraft.client.gui.screens.inventory.ShulkerBoxScreen;
import net.minecraft.network.chat.Component;
import net.neoforged.neoforge.client.event.ScreenEvent;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.network.PacketDistributor;

/** Small iron buttons along the top right of a chest: the server does the work, see Tidy. */
final class InvButtons {
	private InvButtons() {}

	private static final int W = 42, H = 13, GAP = 2, ABOVE = 15;

	static void hooks() {
		NeoForge.EVENT_BUS.addListener((ScreenEvent.Init.Post e) -> {
			if (e.getScreen() instanceof ContainerScreen || e.getScreen() instanceof ShulkerBoxScreen) {
				AbstractContainerScreen<?> s = (AbstractContainerScreen<?>) e.getScreen();
				e.addListener(new Press(s, 0, "Sort", Tidy.SORT));
				e.addListener(new Press(s, 1, "Stash", Tidy.STASH));
				e.addListener(new Press(s, 2, "Take all", Tidy.TAKE));
			}
		});
	}

	private static final class Press extends AbstractButton {
		private final AbstractContainerScreen<?> screen;
		private final int place, what;

		Press(AbstractContainerScreen<?> screen, int place, String name, int what) {
			super(0, 0, W, H, Component.literal(name));
			this.screen = screen;
			this.place = place;
			this.what = what;
		}

		@Override
		public void onPress() {
			PacketDistributor.sendToServer(new Net.InvTidy(what));
		}

		/** Asked each frame: the recipe book moves the inventory over. */
		@Override
		protected void renderWidget(GuiGraphics g, int mx, int my, float pt) {
			setX(screen.getGuiLeft() + screen.getXSize() - (place + 1) * (W + GAP) + GAP);
			setY(screen.getGuiTop() - ABOVE);
			var font = Minecraft.getInstance().font;
			AshUi.row(g, getX(), getY(), W, H, false, isHovered());
			g.drawString(font, getMessage(), getX() + (W - font.width(getMessage())) / 2, getY() + 3, isHovered() ? AshUi.TEXT : AshUi.BODY, true);
		}

		@Override
		protected void updateWidgetNarration(NarrationElementOutput out) {
			defaultButtonNarrationText(out);
		}
	}
}
