#version 150

// The mage's effects (client/SpellParticles). texCoord2.x is the mode. vertexColor: the element's colour and how much.
// Output is premultiplied (blend ONE, ONE_MINUS_SRC_ALPHA): rgb adds light, alpha hides what's behind.
// 0 fire: the atlas holds heat in red; heat picks the colour, from a dark edge through the element's colour to white.
// 1 smoke: the atlas holds lit smoke; tinted.  2 circle: the atlas's spell circle.
// The rest are drawn here from texCoord0, -1..1 across the quad:
// 3 drop: a wet bead.  4 hole: black, with a burning edge.  5 crystal: x is how much a facet faces the light.
// 6 streak: soft across x.  7 glow: a soft round pool of light.  8 plain: the colour as it is.
uniform sampler2D Sampler0;
uniform vec4 ColorModulator;

in vec4 vertexColor;
in vec2 texCoord0;
in vec2 texCoord2;

out vec4 fragColor;

const vec3 WHITE = vec3(1.0);

void main() {
    int mode = int(texCoord2.x + 0.5);
    vec3 c = vertexColor.rgb;
    float va = vertexColor.a;
    vec2 p = texCoord0;
    float r = length(p);
    if (mode == 0) {
        vec4 t = texture(Sampler0, p);
        float h = clamp(t.r * 1.6, 0.0, 1.0);
        vec3 hot = mix(c, WHITE, 0.7);
        vec3 col = h < 0.35 ? mix(c * 0.22, c, h / 0.35) : h < 0.72 ? mix(c, hot, (h - 0.35) / 0.37) : mix(hot, WHITE, (h - 0.72) / 0.28);
        float a = t.a * va;
        fragColor = vec4(col * a * (0.7 + h * 1.1), a * 0.6);
    } else if (mode == 1) {
        vec4 t = texture(Sampler0, p);
        float a = t.a * va;
        fragColor = vec4(c * clamp(t.r * 2.4, 0.0, 1.0) * a, a);
    } else if (mode == 2) {
        vec4 t = texture(Sampler0, p);
        float a = t.a * va;
        fragColor = vec4(mix(c, WHITE, t.r * 0.75) * a * 1.3, a * 0.15);
    } else if (mode == 3) {
        if (r > 1.0) discard;
        vec3 n = vec3(p, sqrt(1.0 - r * r));
        float diff = max(dot(n, normalize(vec3(-0.4, 0.7, 0.6))), 0.0);
        float spec = pow(max(dot(n, normalize(vec3(-0.25, 0.45, 0.85))), 0.0), 60.0);
        float edge = pow(1.0 - n.z, 3.0);
        fragColor = vec4((c * (0.12 + 0.5 * diff) + WHITE * spec * 0.9 + c * edge * 0.8) * va, va);
    } else if (mode == 4) {
        float rim = exp(-pow((r - 0.62) / 0.045, 2.0));
        float halo = r > 0.62 ? exp(-(r - 0.62) / 0.13) : 0.0;
        float core = 1.0 - smoothstep(0.58, 0.64, r);
        fragColor = vec4((mix(c, WHITE, 0.7) * rim + c * halo * 0.6) * va, (core + rim * 0.4) * va);
    } else if (mode == 5) {
        float k = p.x;
        fragColor = vec4(mix(c * 0.4, mix(c, WHITE, 0.75), k) * va * 0.85, va * 0.75);
    } else if (mode == 6) {
        float k = 1.0 - min(abs(p.x), 1.0);
        float a = pow(k, 1.6) * va;
        fragColor = vec4(mix(c, WHITE, pow(k, 4.0)) * a * 1.3, a * 0.12);
    } else if (mode == 7) {
        float a = exp(-r * r * 4.5) * (1.0 - smoothstep(0.75, 1.0, r)) * va;
        fragColor = vec4(c * a, 0.0);
    } else {
        fragColor = vec4(c * va, 0.0);
    }
    fragColor *= ColorModulator;
    if (fragColor.a < 0.002 && dot(fragColor.rgb, fragColor.rgb) < 0.0001) discard;
}
