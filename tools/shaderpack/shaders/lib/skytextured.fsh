// The sun and moon.

#include "/lib/settings.glsl"
#include "/lib/common.glsl"

uniform sampler2D gtexture;
uniform int renderStage;

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
    vec4 c = texture(gtexture, uv) * tint;
    float boost = renderStage == MC_RENDER_STAGE_SUN ? 7.0 : renderStage == MC_RENDER_STAGE_MOON ? 2.2 : 1.0;
    outColor = vec4(toLinear(c.rgb) * boost, c.a);
    outMask = vec4(boost > 1.0 ? 1.0 : 0.0, 0.0, 0.0, 1.0);
}
