// Lines and flat colours: the block outline, leads.

#include "/lib/settings.glsl"
#include "/lib/common.glsl"

in vec2 uv;
in vec2 lm;
in vec4 tint;
in vec3 feet;
in vec3 normal;
flat in int blockId;

/* RENDERTARGETS: 0,1 */
layout(location = 0) out vec4 outColor;
layout(location = 1) out vec4 outMask;

void main() {
    outColor = vec4(toLinear(tint.rgb), tint.a);
    outMask = vec4(0.0, 0.0, 0.0, 1.0);
}
