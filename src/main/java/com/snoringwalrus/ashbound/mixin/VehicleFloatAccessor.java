package com.snoringwalrus.ashbound.mixin;

import net.minecraft.server.network.ServerGamePacketListenerImpl;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** A server without allow-flight kicks a rider who stays up on a vehicle; see Mount.tick. */
@Mixin(ServerGamePacketListenerImpl.class)
public interface VehicleFloatAccessor {
	@Accessor("aboveGroundVehicleTickCount")
	void ashbound$floating(int ticks);
}
