#version 150

// The mage's and the skills' effects (client/SpellParticles, client/FxKit). texCoord2.x is the mode, texCoord2.y carries
// k (how far through its life, 0-255) and a seed (the rest, times 256). vertexColor: the element's colour and how much.
// Output is premultiplied (blend ONE, ONE_MINUS_SRC_ALPHA): rgb adds light, alpha hides what's behind.
// 0 fire: the atlas holds heat in red; heat picks the colour, from a dark edge through the element's colour to white.
// 1 smoke: the atlas holds lit smoke; tinted.  2 circle: the atlas's spell circle.
// The rest are drawn here from texCoord0, -1..1 across the quad unless they say:
// 3 drop: a wet bead.  4 hole: black, with a burning edge.  5 crystal: x is how much a facet faces the light.
// 6 streak: soft across x.  7 glow: a soft round pool of light.  8 plain: the colour as it is.
// 9 slash: x inner to outer edge, y tail to head; burns away from the tail.  10 flow: x across, y along in blocks; energy
// streaming towards y's end.  11 ring: a shockwave running out to the rim.  12 crack: the ground split from the middle.
// 13 flare: a hot star with long streaks.  14 swirl: a vortex, k is the size of the hole in it.  15 arc: lightning along
// a ribbon, x across, y along.  16 rune: a magic circle, the seed picks its star.  17 tube: x round a tube, y along it.
// 18 ink: an atlas flame as solid black with a burning rim, eaten as k grows.  19 star: a filled spiky flash; black colour
// makes its black twin.  20 crescent: a thrown blade, its outer edge white.  21 sheet: a skin of liquid, x round, y 0 at
// its foot to 1 at its lip.
uniform sampler2D Sampler0;
uniform vec4 ColorModulator;
uniform float GameTime;

in vec4 vertexColor;
in vec2 texCoord0;
in vec2 texCoord2;

out vec4 fragColor;

const vec3 WHITE = vec3(1.0);
const float PI = 3.14159265;

float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

float fbm(vec2 p) {
    float a = 0.5, s = 0.0;
    for (int i = 0; i < 4; i++) {
        s += a * noise(p);
        p = p * 2.03 + vec2(17.1, 9.2);
        a *= 0.5;
    }
    return s / 0.9375;
}

// from a dark edge through the colour to white
vec3 ramp(vec3 c, float h) {
    vec3 hot = mix(c, WHITE, 0.65);
    return h < 0.3 ? mix(c * 0.3, c, h / 0.3) : h < 0.7 ? mix(c, hot, (h - 0.3) / 0.4) : mix(hot, WHITE, (h - 0.7) / 0.3);
}

float line(float x, float at, float w) {
    return 1.0 - smoothstep(0.0, w, abs(x - at));
}

// how far a point is from the edge of a cell: the dark lines of cracked ground, running out from the middle
float cracks(vec2 p, float seed) {
    const float ROUND = 7.0;
    float r = length(p);
    vec2 w = vec2(noise(p * 4.0 + seed), noise(p * 4.0 + seed + 9.0)) - 0.5;
    vec2 q = vec2(pow(r, 0.7) * 2.1, (atan(p.y, p.x) / (2.0 * PI) + 0.5) * ROUND) + w * 0.5 + vec2(seed * 3.1, 0.0);
    vec2 ip = floor(q), f = fract(q), mr = vec2(0.0);
    float md = 8.0;
    for (int j = -1; j <= 1; j++)
        for (int i = -1; i <= 1; i++) {
            vec2 g = vec2(float(i), float(j)), c = vec2(ip.x + g.x, mod(ip.y + g.y, ROUND));
            vec2 o = vec2(hash(c + seed), hash(c + seed + 7.7)), d = g + o - f;
            float l = dot(d, d);
            if (l < md) {
                md = l;
                mr = d;
            }
        }
    md = 8.0;
    for (int j = -2; j <= 2; j++)
        for (int i = -2; i <= 2; i++) {
            vec2 g = vec2(float(i), float(j)), c = vec2(ip.x + g.x, mod(ip.y + g.y, ROUND));
            vec2 o = vec2(hash(c + seed), hash(c + seed + 7.7)), d = g + o - f;
            if (dot(mr - d, mr - d) > 0.00001) md = min(md, dot(0.5 * (mr + d), normalize(d - mr)));
        }
    return md;
}

void main() {
    int mode = int(texCoord2.x + 0.5);
    float k = mod(texCoord2.y, 256.0) / 255.0, seed = floor(texCoord2.y / 256.0);
    float t = GameTime * 1200.0;
    vec3 c = vertexColor.rgb;
    float va = vertexColor.a;
    vec2 p = texCoord0;
    float r = length(p);
    if (mode == 0) {
        vec4 tx = texture(Sampler0, p);
        float h = clamp(tx.r * 1.6, 0.0, 1.0);
        vec3 hot = mix(c, WHITE, 0.7);
        vec3 col = h < 0.35 ? mix(c * 0.22, c, h / 0.35) : h < 0.72 ? mix(c, hot, (h - 0.35) / 0.37) : mix(hot, WHITE, (h - 0.72) / 0.28);
        float a = tx.a * va;
        fragColor = vec4(col * a * (0.7 + h * 1.1), a * 0.6);
    } else if (mode == 1) {
        vec4 tx = texture(Sampler0, p);
        float a = tx.a * va;
        fragColor = vec4(c * clamp(tx.r * 2.4, 0.0, 1.0) * a, a);
    } else if (mode == 2) {
        vec4 tx = texture(Sampler0, p);
        float a = tx.a * va;
        fragColor = vec4(mix(c, WHITE, tx.r * 0.75) * a * 1.3, a * 0.15);
    } else if (mode == 3) {
        float w = (1.0 - abs(p.y)) * 0.55;
        float body = 1.0 - smoothstep(w * 0.6, w + 0.001, abs(p.x));
        fragColor = vec4(mix(c, WHITE, 0.3) * body * va, body * va);
    } else if (mode == 4) {
        float rim = exp(-pow((r - 0.62) / 0.045, 2.0));
        float halo = r > 0.62 ? exp(-(r - 0.62) / 0.13) : 0.0;
        float core = 1.0 - smoothstep(0.58, 0.64, r);
        fragColor = vec4((mix(c, WHITE, 0.7) * rim + c * halo * 0.6) * va, (core + rim * 0.4) * va);
    } else if (mode == 5) {
        float h = p.x;
        fragColor = vec4(mix(c * 0.4, mix(c, WHITE, 0.75), h) * va * 0.85, va * 0.75);
    } else if (mode == 6) {
        float tip = 1.0 - abs(p.y);
        float e = 1.0 - min(abs(p.x) / max(tip, 0.001), 1.0);
        float a = pow(e, 1.6) * va;
        float lit = step(0.001, c.r + c.g + c.b);
        fragColor = vec4(mix(c, WHITE, pow(e, 4.0) * lit) * a * 1.3, a * (lit > 0.0 ? 0.12 : 0.9));
    } else if (mode == 7) {
        float a = exp(-r * r * 4.5) * (1.0 - smoothstep(0.75, 1.0, r)) * va;
        fragColor = vec4(c * a, 0.0);
    } else if (mode == 9) {
        float n = fbm(vec2(p.y * 5.0 + seed * 0.37 - k * 2.0, p.x * 1.2 + seed));
        float grain = fbm(vec2(p.y * 2.5 + seed, p.x * 8.0 + seed * 0.7 - k * 4.0));
        float outer = 1.0 - smoothstep(0.84, 1.0, p.x);
        float inner = smoothstep(-1.0, 0.5, p.x);
        float burn = k * k * 1.3;
        float m = smoothstep(burn, burn + 0.16, n * 0.5 + grain * 0.28 + p.y * 0.34);
        float edge = line(p.x, 0.8, 0.13);
        float h = clamp(inner * inner * (0.12 + grain * 0.5) + edge * 0.85, 0.0, 1.0) * (0.5 + 0.5 * m);
        float a = outer * inner * m * va;
        fragColor = vec4(ramp(c, h) * a * 1.2, a * 0.7);
    } else if (mode == 10) {
        float n = fbm(vec2(p.x * 1.3 + seed, p.y * 0.7 - t * 3.2));
        float n2 = fbm(vec2(p.x * 2.5 - seed, p.y * 1.6 - t * 6.0));
        float e = 1.0 - min(abs(p.x), 1.0);
        float m = smoothstep(0.02, 0.42, e * (0.25 + n * 1.1) + e * e * 0.35 - 0.1);
        float h = pow(e, 5.0) * 0.8 + smoothstep(0.46, 0.7, n2) * e * 0.6;
        float a = m * va;
        fragColor = vec4(ramp(c, clamp(h, 0.0, 1.0)) * a * (0.85 + h), a * 0.4);
    } else if (mode == 11) {
        float e = 1.0 - (1.0 - k) * (1.0 - k) * (1.0 - k);
        float front = mix(0.08, 0.93, e), w = mix(0.1, 0.022, e);
        float ang = atan(p.y, p.x);
        float n = fbm(vec2(cos(ang), sin(ang)) * 3.0 + seed + r * 2.0);
        float lead = exp(-pow((r - front) / w, 2.0)) * (0.55 + n * 0.9);
        float wake = r < front ? exp((r - front) / 0.2) * smoothstep(0.25, 0.75, n) * 0.5 : 0.0;
        float gone = 1.0 - smoothstep(0.55, 1.0, k);
        float h = clamp(lead * 1.3 + wake * 0.3, 0.0, 1.0);
        float a = clamp(lead + wake, 0.0, 1.0) * gone * (1.0 - smoothstep(0.93, 1.0, r)) * va;
        fragColor = vec4(ramp(c, h) * a * 1.6, a * 0.5);
    } else if (mode == 12) {
        float reach = 1.0 - pow(1.0 - min(k * 3.5, 1.0), 3.0);
        float d = cracks(p, seed);
        float thin = mix(0.09, 0.025, min(r, 1.0));
        float cut = 1.0 - smoothstep(0.0, thin, d);
        float heat = exp(-max(d, 0.0) * 9.0);
        float cool = 1.0 - smoothstep(0.1, 0.8, k);
        float window = (1.0 - smoothstep(reach * 0.72, reach * 0.98, r)) * (1.0 - smoothstep(0.8, 1.0, k));
        float ember = cut * (0.25 + cool * 0.75);
        float h = clamp(ember * 1.1 * (0.4 + cool) + heat * cool * 0.35, 0.0, 1.0);
        float scorch = clamp(cut * 0.95 + heat * 0.3, 0.0, 1.0);
        fragColor = vec4(ramp(c, h) * (ember + heat * cool * 0.4) * window * va * 1.5, scorch * window * va * 0.9);
    } else if (mode == 13) {
        float across = exp(-abs(p.y) * 34.0) * exp(-abs(p.x) * 2.3);
        float up = exp(-abs(p.x) * 55.0) * exp(-abs(p.y) * 3.4);
        float ang = atan(p.y, p.x);
        float rays = pow(noise(vec2(cos(ang), sin(ang)) * 5.0 + seed), 3.0) * exp(-r * 3.4);
        float h = exp(-r * r * 16.0) * 1.3 + across + up * 0.75 + rays * 1.1;
        float a = h * (1.0 - smoothstep(0.75, 1.0, r)) * va;
        fragColor = vec4(mix(c, WHITE, clamp(h, 0.0, 1.0)) * a, min(a, 1.0) * 0.15);
    } else if (mode == 14) {
        float ang = atan(p.y, p.x) + log(max(r, 0.02)) * 3.2 + t * 2.4;
        float n = fbm(vec2(cos(ang), sin(ang)) * 1.7 + vec2(r * 2.2 - t * 0.6, seed));
        float hole = k * 0.75;
        float open = smoothstep(hole - 0.015, hole + 0.04, r);
        float rim = hole > 0.0 ? exp(-pow((r - hole) / 0.045, 2.0)) : 0.0;
        float disc = (1.0 - smoothstep(0.55, 1.0, r)) * open;
        float arms = smoothstep(0.34, 0.72, n);
        float h = clamp(arms * (1.15 - r) + rim * 1.2, 0.0, 1.0);
        float a = clamp(arms * disc + rim, 0.0, 1.0) * va;
        fragColor = vec4(ramp(c, h) * a * 1.4, max(a * 0.55, (1.0 - open) * (1.0 - smoothstep(0.9, 1.0, r)) * va));
    } else if (mode == 15) {
        float x = p.x + (fbm(vec2(p.y * 1.6 + seed, t * 11.0)) - 0.5) * 1.5 + (noise(vec2(p.y * 7.0 - seed, t * 19.0)) - 0.5) * 0.4;
        float e = exp(-x * x * 90.0), halo = exp(-x * x * 7.0);
        float flick = 0.65 + 0.35 * noise(vec2(t * 24.0, seed));
        float h = e + halo * 0.3;
        float a = h * flick * (1.0 - smoothstep(0.85, 1.0, abs(p.x))) * va;
        fragColor = vec4(mix(c, WHITE, min(e * 1.2, 1.0)) * a * 1.4, min(a, 1.0) * 0.2);
    } else if (mode == 16) {
        float ang = atan(p.y, p.x), spin = t * 0.5 + seed;
        float rings = line(r, 0.965, 0.012) + line(r, 0.905, 0.008) + line(r, 0.6, 0.01) + line(r, 0.55, 0.006) + line(r, 0.17, 0.012);
        float ticks = step(0.5, fract((ang + spin * 0.4) * 60.0 / (2.0 * PI))) * step(0.905, r) * step(r, 0.965) * 0.55;
        // a band of glyphs that turns the other way
        float cell = floor((ang - spin) * 16.0 / PI), row = floor((r - 0.6) / 0.305 * 5.0);
        float glyph = step(0.6, r) * step(r, 0.9) * step(0.5, hash(vec2(mod(cell, 32.0), row) + seed)) * step(0.14, fract((r - 0.6) / 0.305 * 5.0)) * step(0.16, fract((ang - spin) * 16.0 / PI));
        // the star, each point joined to the next but one
        float n = 3.0 + mod(seed, 5.0), b = 2.0 * PI / n;
        float fold = mod(ang + spin * 0.7 + b * 0.5, b) - b * 0.5;
        float star = line(r * cos(fold), 0.55 * cos(b), 0.012) * step(r, 0.55);
        float reveal = smoothstep(0.0, 0.03, k * 7.0 - (ang + PI) / (2.0 * PI));
        float h = clamp(rings + ticks + glyph * 0.4 + star, 0.0, 1.0) * reveal;
        float pool = exp(-r * r * 2.6) * 0.12 * reveal;
        float a = (h + pool) * (1.0 - smoothstep(0.97, 1.0, r)) * va;
        fragColor = vec4(mix(c, WHITE, h * 0.65) * a * 1.5, a * 0.2);
    } else if (mode == 17) {
        float b = p.x * PI;
        float n = fbm(vec2(cos(b) * 1.3 + p.y * 0.35 - t * 1.6, sin(b) * 1.3 + seed + p.y * 0.1));
        float n2 = fbm(vec2(cos(b) * 2.4 + seed, sin(b) * 2.4 + p.y * 0.8 - t * 3.0));
        float burn = 0.16 + k * 0.6;
        float m = smoothstep(burn, burn + 0.3, n);
        float h = clamp(m * 0.45 + smoothstep(0.5, 0.74, n2) * m * 0.75, 0.0, 1.0);
        float a = m * va;
        fragColor = vec4(ramp(c, h) * a * 1.3, a * 0.4);
    } else if (mode == 18) {
        vec4 tx = texture(Sampler0, p);
        float h = tx.a * (0.6 + clamp(tx.r * 1.6, 0.0, 1.0) * 0.6), cut = 0.3 + k * k * 0.5;
        float body = smoothstep(cut, cut + 0.06, h), edge = smoothstep(cut - 0.28, cut - 0.06, h) * (1.0 - body);
        float hot = smoothstep(cut - 0.1, cut - 0.01, h) * (1.0 - body);
        fragColor = vec4((c * edge * 1.5 + mix(c, WHITE, 0.55) * hot * 0.9) * va, max(body, edge * 0.85) * va);
    } else if (mode == 19) {
        float count = 10.0 + mod(seed, 7.0), ang = (atan(p.y, p.x) / (2.0 * PI) + 0.5) * count + seed * 0.13;
        float sp = abs(fract(ang) - 0.5) * 2.0, jag = hash(vec2(mod(floor(ang), count), seed)); jag = 0.22 + 0.78 * jag * jag;
        float reach = mix(0.13, 0.98 * jag, pow(sp, 2.6)) * (1.0 - k * 0.3);
        float body = 1.0 - smoothstep(reach - 0.025, reach + 0.01, r);
        float core = (1.0 - smoothstep(reach * 0.4, reach * 0.62, r)) * step(0.001, c.r + c.g + c.b);
        float a = body * (1.0 - smoothstep(0.65, 1.0, k)) * va;
        fragColor = vec4(mix(c, WHITE, core) * a * 1.5, a * 0.9);
    } else if (mode == 20) {
        float R0 = length(p + vec2(0.0, 0.62)), al = atan(p.x, p.y + 0.62) / 1.02;
        float w = 0.24 * pow(max(1.0 - al * al, 0.0), 1.2), d = (R0 - 1.2) / max(w, 0.001);
        float n = fbm(vec2(al * 3.0 + seed, d * 0.7 + seed * 0.3));
        float m = smoothstep(k * 1.25 - 0.2, k * 1.25 - 0.06, n + 0.08);
        float body = (1.0 - smoothstep(0.86, 1.0, abs(d))) * step(abs(al), 1.0);
        float a = body * m * va, hot = smoothstep(0.15, 0.8, d) * step(0.001, c.r + c.g + c.b);
        fragColor = vec4(mix(c, WHITE, hot) * a * 1.5, a * 0.85);
    } else if (mode == 21) {
        float n = fbm(vec2(p.x * 9.0 + seed, p.y * 1.4 - t * 0.6));
        float n2 = fbm(vec2(p.x * 30.0 - seed, p.y * 2.2));
        float torn = smoothstep(k * 0.95 - 0.1, k * 0.95 + 0.1, n + p.y * 0.25);
        float lip = smoothstep(0.82, 0.97, p.y);
        float fill = smoothstep(0.04, 0.6, p.y) * smoothstep(0.34, 0.6, n2 + 0.08);
        float a = clamp(fill * 0.75 + lip, 0.0, 1.0) * torn * va;
        fragColor = vec4(mix(c, WHITE, lip) * a * 1.4, a * 0.35);
    } else {
        fragColor = vec4(c * va, 0.0);
    }
    fragColor *= ColorModulator;
    if (fragColor.a < 0.002 && dot(fragColor.rgb, fragColor.rgb) < 0.0001) discard;
}
