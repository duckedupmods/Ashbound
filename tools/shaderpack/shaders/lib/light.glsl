// How a lit surface looks. Everything is lit where it's drawn, so glass and water match the ground behind them.

uniform sampler2D shadowtex0;

float sunReach(vec3 feet, vec3 normal) {
    float dist = length(feet);
    vec3 at = feet + normal * (0.05 + dist * 0.0022);
    vec4 p = shadowProjection * shadowModelView * vec4(at, 1.0);
    vec2 d = distort(p.xy);
    vec3 s = vec3(d, p.z) * 0.5 + 0.5;
    if (s.x < 0.0 || s.x > 1.0 || s.y < 0.0 || s.y > 1.0) return 1.0;
    float stretch = 1.0 / max(0.12 + 0.88 * length(p.xy), 0.12), size = SHADOW_SOFT / float(shadowMapResolution) * mix(1.0, 0.7, min(stretch * 0.1, 1.0));
    float turn = dither(gl_FragCoord.xy) * TAU, lit = 0.0;
    const int TAPS = 10;
    for (int i = 0; i < TAPS; i++) {
        float r = sqrt((float(i) + 0.5) / float(TAPS)), a = float(i) * 2.399963 + turn;
        lit += step(s.z - 0.00035, texture(shadowtex0, s.xy + vec2(cos(a), sin(a)) * r * size).r);
    }
    return lit / float(TAPS);
}

// how much torchlight, the held item's included
float blockLight(float lm, vec3 feet) {
    float held = float(max(heldBlockLightValue, heldBlockLightValue2)) / 15.0;
    return max(lm, held * clamp(1.0 - length(feet) / 13.0, 0.0, 1.0));
}

vec3 shade(vec3 albedo, vec3 normal, vec3 feet, vec2 lm, float foliage, bool useShadow) {
    vec3 light = vec3(0.012, 0.014, 0.02) + vec3(0.1, 0.16, 0.1) * nightVision;
    if (hasSkylight) {
        vec3 L = lightDir();
        float NoL = dot(normal, L), lit = 0.0;
        float wrap = foliage > 0.0 ? 0.4 + 0.6 * max(NoL, 0.0) : max(NoL, 0.0);
        if (wrap > 0.001) {
            lit = useShadow ? sunReach(feet, foliage > 0.0 ? L * 0.25 : normal) : 1.0;
            lit *= smoothstep(0.0, 0.3, lm.y);
            float beyond = smoothstep(shadowDistance * 0.8, shadowDistance, length(feet));
            lit = mix(lit, smoothstep(0.55, 0.9, lm.y), beyond);
        }
        light += keyLight() * wrap * lit;
        light += ambientSky() * lm.y * lm.y * (0.68 + 0.32 * normal.y);
        // leaves with the sun behind them glow through
        float behind = pow(max(dot(normalize(feet), L), 0.0), 4.0);
        light += keyLight() * vec3(0.9, 1.0, 0.32) * behind * foliage * lit * 0.9;
    } else {
        light += closedAmbient();
    }
    float b = blockLight(lm.x, feet), e = b * b * (0.45 + 0.55 * b * b);
    light += mix(EMBER, EMBER_HOT, e) * e * 2.1 * EMBER_STRENGTH;
    return albedo * light;
}
