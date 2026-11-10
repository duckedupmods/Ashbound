// The sky, from nothing but the direction you look: vanilla's colours are thrown away, its stars kept.

#include "/lib/settings.glsl"
#include "/lib/common.glsl"

in vec3 ray;
in vec4 tint;

/* RENDERTARGETS: 0,1 */
layout(location = 0) out vec4 outColor;
layout(location = 1) out vec4 outMask;

void main() {
    vec3 c = hasSkylight ? skyAt(normalize(ray)) : toLinear(fogColor) * 0.5;
    bool star = tint.r == tint.g && tint.g == tint.b && tint.r > 0.0 && tint.a > 0.0 && tint.a < 1.0;
    if (star) c += vec3(tint.r) * 1.6 * (1.0 - rainStrength);
    outColor = vec4(c, 1.0);
    outMask = vec4(star ? 0.5 : 0.0, 0.0, 0.0, 1.0);
}
