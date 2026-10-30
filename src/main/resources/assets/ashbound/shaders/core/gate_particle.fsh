#version 150
#moj_import <ashbound:gate_noise.glsl>

// The gate's particles, drawn soft from noise instead of a pixel sprite cut out at an alpha test (that gave them
// hard square-pixel edges). texCoord0.x >= 0: smoke, x in [2s, 2s+1] (s = the puff's seed), y 0..1 across it.
// texCoord0.x < 0: a spark streak, x in -3..-1 across it, y 0 at its head to 1 at its tail.
// texCoord2: the lightmap coords (Sampler2). vertexColor: colour and alpha (straight, not premultiplied).
uniform sampler2D Sampler2;
uniform float GameTime;
uniform vec4 ColorModulator;

in vec4 vertexColor;
in vec2 texCoord0;
in vec2 texCoord2;

out vec4 fragColor;

void main() {
    vec4 light = texture(Sampler2, clamp(texCoord2 / 256.0, vec2(0.5 / 16.0), vec2(15.5 / 16.0)));
    if (texCoord0.x < 0.0) {
        float u = texCoord0.x + 2.0, v = texCoord0.y;
        float a = pow(gate_ss(1.0, 0.0, abs(u)), 1.6) * gate_ss(0.0, 0.15, v) * gate_ss(1.0, 0.3, v);
        fragColor = vec4(vertexColor.rgb * (1.0 + (1.0 - abs(u)) * 0.4), vertexColor.a * a) * ColorModulator;
        if (fragColor.a < 0.003) discard;
        return;
    }
    float s = floor(texCoord0.x * 0.5);
    vec2 p = vec2(texCoord0.x - 2.0 * s, texCoord0.y) * 2.0 - 1.0;
    float T = GameTime * 1200.0;
    vec3 q = vec3(p * 1.7, s * 7.31 + T * 0.08);
    float n = gate_fbm(q), m = gate_fbm(q * 2.3 + vec3(3.1, 7.7, 1.3));
    float r = length(p) + (n - 0.5) * 0.6;
    float dens = gate_ss(0.95, 0.15, r) * (0.55 + 0.6 * m);
    vec3 col = vertexColor.rgb * light.rgb * (0.78 + 0.4 * n);
    fragColor = vec4(col, clamp(dens, 0.0, 1.0) * vertexColor.a) * ColorModulator;
    if (fragColor.a < 0.003) discard;
}
