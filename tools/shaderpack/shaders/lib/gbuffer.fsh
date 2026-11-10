// The fragment half. colortex0 is the lit picture in linear light, past 1.0 where it's bright; colortex1.r is what glows,
// for the bloom, and .g keeps clouds out of the edge-of-the-world fade.

#include "/lib/settings.glsl"
#include "/lib/common.glsl"
#include "/lib/light.glsl"

uniform sampler2D gtexture;
uniform float alphaTestRef;
uniform vec4 entityColor;

in vec2 uv;
in vec2 lm;
in vec4 tint;
in vec3 feet;
in vec3 normal;
flat in int blockId;

/* RENDERTARGETS: 0,1 */
layout(location = 0) out vec4 outColor;
layout(location = 1) out vec4 outMask;

#ifdef WATER
float waves(vec2 p) {
    float t = frameTimeCounter;
    return sin(p.x * 1.1 + t * 1.2) * 0.3 + sin(p.y * 1.7 - t * 0.9) * 0.22 + sin((p.x + p.y) * 2.9 + t * 1.8) * 0.1 + sin((p.x * 0.6 - p.y) * 4.3 - t * 2.1) * 0.05;
}

vec4 water(vec3 base) {
    vec2 p = (feet + cameraPosition).xz;
    vec3 n = vec3(0.0, 1.0, 0.0);
    #ifdef WATER_WAVES
    const float E = 0.08;
    float h = waves(p);
    if (normal.y > 0.5) n = normalize(vec3((h - waves(p + vec2(E, 0.0))) * 0.45, E, (h - waves(p + vec2(0.0, E))) * 0.45));
    else n = normal;
    #else
    n = normal;
    #endif
    vec3 V = normalize(feet);
    float fresnel = 0.03 + 0.97 * pow(1.0 - max(dot(-V, n), 0.0), 5.0);
    vec3 body = shade(toLinear(base) * vec3(0.5, 0.75, 0.8), n, feet, lm, 0.0, true);
    vec3 mirror = hasSkylight ? skyAt(reflect(V, n)) * lm.y * lm.y : vec3(0.0);
    vec3 c = mix(body, mirror, fresnel);
    if (hasSkylight) c += keyLight() * pow(max(dot(reflect(V, n), lightDir()), 0.0), 320.0) * 2.5 * smoothstep(0.5, 0.95, lm.y);
    return vec4(c, mix(0.62, 0.92, fresnel));
}
#endif

void main() {
    vec4 c = texture(gtexture, uv) * tint;
    if (c.a < alphaTestRef) discard;
#ifdef ENTITY
    c.rgb = mix(c.rgb, entityColor.rgb, entityColor.a);
#endif
    vec3 albedo = toLinear(c.rgb);
    float bright = max(c.r, max(c.g, c.b)), glow = 0.0, foliage = 0.0, cloud = 0.0;
    vec3 rgb;

#if defined(WATER)
    if (blockId == ID_WATER) {
        vec4 w = water(c.rgb);
        outColor = w;
        outMask = vec4(0.0);
        return;
    }
#endif

#if defined(UNLIT)
    rgb = albedo * 1.6;
    glow = 1.0;
#elif defined(CLOUDS)
    rgb = albedo * (keyLight() * 0.5 + ambientSky() * 1.1 + 0.02);
    cloud = 1.0;
#elif defined(FLAT)
    rgb = shade(albedo, vec3(0.0, 1.0, 0.0), feet, lm, 0.25, false);
#else
    if (blockId == ID_LEAVES || blockId == ID_PLANT) {
        foliage = 1.0;
        albedo = mix(vec3(dot(albedo, LUMA)), albedo, 1.14);
    }
    vec3 n = blockId == ID_PLANT ? vec3(0.0, 1.0, 0.0) : normal;
    #ifdef HAND
    bool useShadow = false;
    #else
    bool useShadow = true;
    #endif
    rgb = shade(albedo, n, feet, lm, foliage, useShadow);
    #ifdef HAND
    if (!hasSkylight) rgb = max(rgb, albedo * 0.1);
    #endif
    // a block that gives light and whose pixel is bright is the light: true of every lantern in the mod without a list of them
    glow = blockId == ID_GLOW ? smoothstep(0.35, 0.8, bright) : lm.x > 0.91 ? smoothstep(0.72, 0.95, bright) : 0.0;
    #ifdef TERRAIN
    rgb += albedo * glow * 3.4 * EMBER_STRENGTH;
    #else
    glow = 0.0;
    #endif
#endif
    outColor = vec4(rgb, c.a);
    outMask = vec4(glow, cloud, 0.0, 1.0);
}
