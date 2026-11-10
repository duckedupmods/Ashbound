#version 330 compatibility

#include "/lib/settings.glsl"

uniform sampler2D gtexture;
uniform float alphaTestRef;

in vec2 uv;
in float alpha;
flat in int blockId;

/* RENDERTARGETS: 0 */
layout(location = 0) out vec4 outColor;

void main() {
    if (blockId == ID_WATER) discard;
    vec4 c = texture(gtexture, uv);
    if (c.a * alpha < max(alphaTestRef, 0.1)) discard;
    outColor = c;
}
