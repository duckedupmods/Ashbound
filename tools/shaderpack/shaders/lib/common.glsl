// What every program shares: the time of day as colours of light, and the sky.

const float TAU = 6.2831853;
const vec3 LUMA = vec3(0.2126, 0.7152, 0.0722);

// the sun: pale gold at noon, deep orange low down. All of the mood is in these few lines.
const vec3 SUN_DAY = vec3(1.0, 0.91, 0.76) * 3.1;
const vec3 SUN_GOLD = vec3(1.0, 0.52, 0.2) * 3.2;
const vec3 MOON = vec3(0.42, 0.58, 1.0) * 0.5;
// the light from the sky, cool so shadows read blue against the warm sun
const vec3 AMB_DAY = vec3(0.46, 0.6, 0.86) * 0.72;
const vec3 AMB_GOLD = vec3(0.6, 0.46, 0.56) * 0.5;
const vec3 AMB_NIGHT = vec3(0.09, 0.13, 0.27) * 0.42;
// torches, lava, braziers: everything lit by a block burns like an ember
const vec3 EMBER = vec3(1.0, 0.56, 0.24);
const vec3 EMBER_HOT = vec3(1.0, 0.8, 0.58);

uniform float sunAngle;
uniform float rainStrength;
uniform float frameTimeCounter;
uniform float viewWidth;
uniform float viewHeight;
uniform float near;
uniform float far;
uniform float nightVision;
uniform float blindness;
uniform float darknessFactor;
uniform float ambientLight;
uniform int isEyeInWater;
uniform int heldBlockLightValue;
uniform int heldBlockLightValue2;
uniform bool hasSkylight;
uniform ivec2 eyeBrightnessSmooth;
uniform vec3 cameraPosition;
uniform vec3 sunPosition;
uniform vec3 shadowLightPosition;
uniform vec3 fogColor;
uniform mat4 gbufferModelView;
uniform mat4 gbufferModelViewInverse;
uniform mat4 gbufferProjectionInverse;
uniform mat4 shadowModelView;
uniform mat4 shadowProjection;

vec3 toLinear(vec3 c) {
    return pow(max(c, vec3(0.0)), vec3(2.2));
}

float dither(vec2 p) {
    return fract(52.9829189 * fract(dot(p, vec2(0.06711056, 0.00583715))));
}

float sunHeight() {
    return sin(sunAngle * TAU);
}

float golden() {
    return 1.0 - smoothstep(0.0, 0.42, abs(sunHeight()));
}

// the sun or the moon, whichever is up, and gone for a moment as they change over
vec3 keyLight() {
    float h = sunHeight();
    vec3 c = h > 0.0 ? mix(SUN_DAY, SUN_GOLD, golden()) : MOON;
    return c * smoothstep(0.0, 0.07, abs(h)) * mix(1.0, 0.16, rainStrength);
}

vec3 ambientSky() {
    vec3 a = mix(AMB_NIGHT, mix(AMB_DAY, AMB_GOLD, golden()), smoothstep(-0.12, 0.12, sunHeight()));
    return mix(a, vec3(dot(a, LUMA)) * 0.75, rainStrength * 0.8);
}

vec3 lightDir() {
    return normalize(mat3(gbufferModelViewInverse) * shadowLightPosition);
}

vec3 sunDir() {
    return normalize(mat3(gbufferModelViewInverse) * sunPosition);
}

vec3 skyAt(vec3 dir) {
    float h = sunHeight(), gold = golden(), day = smoothstep(-0.14, 0.1, h);
    vec3 top = mix(vec3(0.012, 0.02, 0.055), mix(vec3(0.13, 0.3, 0.74), vec3(0.2, 0.2, 0.46), gold), day);
    vec3 low = mix(vec3(0.035, 0.055, 0.12), mix(vec3(0.66, 0.78, 0.92), vec3(1.0, 0.5, 0.24), gold), day);
    float up = max(dir.y, 0.0);
    vec3 c = mix(low, top, 1.0 - pow(1.0 - up, 3.5));
    c *= mix(0.55, 1.0, smoothstep(-0.25, 0.0, dir.y));
    float toSun = max(dot(dir, sunDir()), 0.0);
    c += mix(vec3(1.0, 0.8, 0.55) * 0.18, vec3(1.0, 0.42, 0.14) * 0.85, gold) * pow(toSun, 7.0) * day;
    c += vec3(1.0, 0.86, 0.65) * pow(toSun, 90.0) * 0.5 * day;
    return mix(c, vec3(dot(c, LUMA)) * 0.62, rainStrength * 0.85);
}

// the world's light in a place with no sky: the nether's heat, a gate's dark
vec3 closedAmbient() {
    return toLinear(fogColor) * 0.5 + vec3(0.05, 0.052, 0.07) + ambientLight * 0.25;
}

vec2 distort(vec2 p) {
    return p / (length(p) * 0.88 + 0.12);
}

vec3 sway(vec3 world, float amount) {
    float t = frameTimeCounter;
    float gust = 0.5 + 0.5 * sin(t * 0.8 + world.x * 0.09 + world.z * 0.13);
    vec3 s = vec3(sin(t * 1.7 + world.x * 0.7 + world.y * 0.5), 0.4 * sin(t * 1.3 + world.z * 0.9), cos(t * 1.5 + world.z * 0.7 + world.y * 0.3));
    return s * amount * (0.025 + 0.055 * gust) * (1.0 + 1.5 * rainStrength);
}
