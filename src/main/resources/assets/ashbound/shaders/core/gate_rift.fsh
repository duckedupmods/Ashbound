#version 150
#moj_import <ashbound:gate_noise.glsl>

// The tear: a crack in the world (the look of tools/blender/gate_rift.py). Its shape comes from a signed distance
// field (Sampler0 = textures/misc/gate_rift.png, 4 shapes side by side, tools/gate_rift.py), so every glow fades out
// with the distance from the lip and never shows the quad it is drawn on.
// texCoord0: blocks across (x) and up (y) from the tear's middle, in the world (already squeezed by its size).
// texCoord2.x: layer (0 = the dark inside, writes depth; 1 = the burning lips, added light) + 8 * (shape + 4 * seed).
// texCoord2.y: dark (1 = black inside, S up) + 2 * heat (tenths, 0..31) + 64 * width (0..255 = 0..1)
//              + 16384 if there's a far side to show (Sampler1: client/GateWindow drew it from this camera, half size).
// The tear is drawn WIDE times as wide as its field.
// vertexColor: the rank colour; alpha = how alive it is.
uniform sampler2D Sampler0;
uniform sampler2D Sampler1;
uniform vec2 ScreenSize;
uniform float GameTime;
uniform vec4 ColorModulator;

in vec4 vertexColor;
in vec2 texCoord0;
in vec2 texCoord2;

out vec4 fragColor;

const float H = 4.9, EX = 3.2, EZ = 7.1, DMAX = 2.0, WIDE = 2.0;

void main() {
    float T = GameTime * 1200.0;
    int code = int(texCoord2.x + 0.5);
    int layer = code - (code / 8) * 8;
    int rest = code / 8;
    int shape = rest - (rest / 4) * 4;
    float seed = float(rest / 4) * 3.17;
    int flags = int(texCoord2.y + 0.5);
    bool window = flags >= 16384;
    if (window) flags -= 16384;
    bool dark = flags - (flags / 2) * 2 == 1;
    float hot = float((flags / 2) - (flags / 64) * 32) / 10.0;
    float sx = max(float(flags / 64) / 255.0, 0.004) * WIDE;
    vec3 col = vertexColor.rgb;
    float live = vertexColor.a;
    vec2 p = texCoord0;

    // the distance from the lip in blocks: the field read at the unsqueezed point, squeezed back, plus however far
    // past the field's edge (sideways) or past the tips (up and down) this point is
    vec2 lp = vec2(p.x / sx, p.y);
    vec2 cl = clamp(lp, vec2(-EX + 0.02, -EZ + 0.02), vec2(EX - 0.02, EZ - 0.02));
    vec2 uv = vec2((float(shape) + 0.5 + cl.x / (2.0 * EX)) / 4.0, 0.5 - cl.y / (2.0 * EZ));
    float d = (texture(Sampler0, uv).r - 0.5) * 2.0 * DMAX;
    d = max(d * min(sx, 1.0), abs(p.y) - (H + 0.2)) + max(abs(p.x) - EX * sx, 0.0);

    if (layer == 0) {
        if (d > -0.015 || live < 0.02) discard;
        if (window) {
            // the far side, where it is on screen: dimmer and tinted toward the lips, darker behind the black ones
            vec3 seen = texture(Sampler1, gl_FragCoord.xy / ScreenSize).rgb;
            float deep = clamp(-d / 0.9, 0.0, 1.0);
            vec3 w = seen * (0.3 + 0.7 * deep) * (dark ? 0.55 : 1.0) + col * (1.0 - deep) * 0.2;
            fragColor = vec4(w * live, live) * ColorModulator;
            return;
        }
        // the far side: black, a faint light moving deep in it (brighter for the low ranks)
        float n = gate_fbm(vec3(p * 0.8, seed + T * 0.12));
        float far = gate_ss(0.5, 0.78, n) * gate_ss(-0.05, -0.9, d);
        vec3 e = gate_tone(col * far * (dark ? 0.12 : 0.9));
        fragColor = vec4(e * live, live) * ColorModulator;
        return;
    }

    float n1 = gate_fbm(vec3(p * 1.1, seed + T * 0.35 * hot));
    float n2 = gate_fbm(vec3(p * 4.5, seed + 7.0 + T * 0.9 * hot));
    float jit = ((n1 - 0.5) * 0.5 + (n2 - 0.5) * 0.18) * clamp(sx * 1.5, 0.12, 1.0);
    float dj = d + jit;
    float outside = gate_ss(-0.04, 0.06, dj);
    float od = max(dj, 0.0), id = max(-dj, 0.0);
    float core = pow(1.0 - gate_ss(0.0, 0.05, abs(dj)), 2.0);
    float band = exp(-8.0 * od - 30.0 * id);
    float halo = exp(-2.6 * od) * outside;
    float burn = exp(-22.0 * id) * (1.0 - outside);
    float tongue = gate_ss(0.55, 0.75, n1) * exp(-3.0 * od) * outside;
    float fade = gate_ss(1.75, 0.9, d);
    vec3 white = mix(col, vec3(1.0, 0.96, 0.9), 0.8);
    vec3 e = col * (band * 1.4 + halo * 0.1 + burn * 0.35 + tongue * 0.75) * fade + white * core * 2.6;
    e *= hot * live;
    fragColor = vec4(gate_tone(e), 0.0) * ColorModulator;
}
