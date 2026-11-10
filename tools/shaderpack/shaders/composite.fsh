#version 330 compatibility

// The air: ink lines on the near things, haze filling the valleys, light shafts, the water you're in.

/*
const int colortex0Format = RGBA16F;
const int colortex1Format = RG8;
const int colortex2Format = R11F_G11F_B10F;
const int colortex3Format = R11F_G11F_B10F;
const int colortex4Format = R11F_G11F_B10F;
const int colortex5Format = R11F_G11F_B10F;
*/

#include "/lib/settings.glsl"
#include "/lib/common.glsl"

const float HAND_DEPTH = 0.56, RAY_REACH = 72.0;

uniform sampler2D colortex0;
uniform sampler2D colortex1;
uniform sampler2D depthtex0;
uniform sampler2D shadowtex0;

in vec2 uv;

/* RENDERTARGETS: 0 */
layout(location = 0) out vec4 outColor;

float depthAt(vec2 p) {
    return texture(depthtex0, p).r;
}

float linear(float d) {
    return 2.0 * near * far / (far + near - (2.0 * d - 1.0) * (far - near));
}

// A flat wall has none of this however steep it is: 1/distance runs in a straight line across any plane, so only real edges bend it.
float ink(float d) {
    vec2 px = 1.0 / vec2(viewWidth, viewHeight);
    float at = 1.0 / linear(d);
    float x = abs(1.0 / linear(depthAt(uv + vec2(px.x, 0.0))) + 1.0 / linear(depthAt(uv - vec2(px.x, 0.0))) - 2.0 * at);
    float y = abs(1.0 / linear(depthAt(uv + vec2(0.0, px.y))) + 1.0 / linear(depthAt(uv - vec2(0.0, px.y))) - 2.0 * at);
    return smoothstep(0.03, 0.14, max(x, y) / at) * (1.0 - smoothstep(10.0, 42.0, linear(d)));
}

float rays(vec3 dir, float reach) {
    const int STEPS = 10;
    float step_ = reach / float(STEPS), t = step_ * dither(gl_FragCoord.xy), lit = 0.0;
    for (int i = 0; i < STEPS; i++) {
        vec4 p = shadowProjection * shadowModelView * vec4(dir * t, 1.0);
        vec3 s = vec3(distort(p.xy), p.z) * 0.5 + 0.5;
        lit += step(s.z - 0.0005, texture(shadowtex0, s.xy).r);
        t += step_;
    }
    return lit / float(STEPS);
}

void main() {
    vec3 c = texture(colortex0, uv).rgb;
    float d = depthAt(uv);
    if (d < HAND_DEPTH) {
        outColor = vec4(c, 1.0);
        return;
    }
    vec4 view = gbufferProjectionInverse * vec4(vec3(uv, d) * 2.0 - 1.0, 1.0);
    view /= view.w;
    vec3 feet = mat3(gbufferModelViewInverse) * view.xyz, dir = normalize(feet);
    float dist = length(feet), open = float(eyeBrightnessSmooth.y) / 240.0;
    bool sky = d >= 1.0;

#ifdef INK_EDGES
    if (!sky) c *= 1.0 - ink(d) * INK_STRENGTH;
#endif

    if (isEyeInWater == 1) {
        vec3 deep = (hasSkylight ? ambientSky() + keyLight() * 0.2 : closedAmbient()) * vec3(0.05, 0.3, 0.36);
        c = mix(deep, c * vec3(0.55, 0.9, 0.95), exp(-dist * 0.075));
    } else if (isEyeInWater == 2) {
        c = mix(vec3(2.4, 0.7, 0.1), c, exp(-dist * 1.3));
    } else if (hasSkylight) {
        if (!sky) {
            // haze pools low and thins out above; caves stay clear
            float y = max(feet.y + cameraPosition.y - 62.0, 0.0);
            float thick = (0.0015 + 0.0085 * rainStrength) * exp(-y * 0.018) * mix(0.15, 1.0, open);
            vec3 air = skyAt(vec3(dir.x, max(dir.y, 0.02) * 0.3, dir.z));
            c = mix(air, c, exp(-dist * thick));
            if (texture(colortex1, uv).g < 0.5) c = mix(c, skyAt(dir), smoothstep(far * 0.74, far * 0.98, dist));
        }
#ifdef GODRAYS
        float reach = min(dist, RAY_REACH);
        float toLight = max(dot(dir, lightDir()), 0.0);
        float phase = 0.12 + 0.3 * pow(toLight, 3.0) + 1.1 * pow(toLight, 16.0);
        c += keyLight() * rays(dir, reach) * phase * RAYS_STRENGTH * 0.14 * (1.0 - exp(-reach * 0.04)) * mix(0.25, 1.0, open);
#endif
    } else if (!sky) {
        vec3 air = closedAmbient() * 0.7;
        c = mix(air, c, exp(-dist * 0.012));
        c = mix(c, air, smoothstep(far * 0.74, far * 0.98, dist));
    }

    c *= exp(-dist * (blindness * 0.5 + darknessFactor * 0.16));
    outColor = vec4(c, 1.0);
}
