#version 330 compatibility

// What goes into the bloom, a quarter of the size: things that are glowing, and very little else.

#include "/lib/settings.glsl"
#include "/lib/common.glsl"

uniform sampler2D colortex0;
uniform sampler2D colortex1;

in vec2 uv;

/* RENDERTARGETS: 2 */
layout(location = 0) out vec4 outColor;

vec3 tap(vec2 p) {
    vec3 c = min(texture(colortex0, p).rgb, vec3(12.0));
    float over = max(dot(c, LUMA) - 1.4, 0.0) / max(dot(c, LUMA), 0.001);
    return c * max(over, texture(colortex1, p).r);
}

void main() {
    vec2 px = 1.5 / vec2(viewWidth, viewHeight);
    outColor = vec4((tap(uv + px) + tap(uv - px) + tap(uv + vec2(px.x, -px.y)) + tap(uv + vec2(-px.x, px.y))) * 0.25, 1.0);
}
