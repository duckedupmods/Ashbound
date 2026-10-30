// Value noise and fbm for the gate shaders (0..1, mean ~0.5), plus a rotate and a soft tone curve.
float gate_hash(vec3 p) {
    p = fract(p * vec3(443.897, 441.423, 437.195));
    p += dot(p, p.yzx + 19.19);
    return fract((p.x + p.y) * p.z);
}

float gate_noise(vec3 p) {
    vec3 i = floor(p), f = fract(p);
    vec3 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
    float n000 = gate_hash(i), n100 = gate_hash(i + vec3(1, 0, 0));
    float n010 = gate_hash(i + vec3(0, 1, 0)), n110 = gate_hash(i + vec3(1, 1, 0));
    float n001 = gate_hash(i + vec3(0, 0, 1)), n101 = gate_hash(i + vec3(1, 0, 1));
    float n011 = gate_hash(i + vec3(0, 1, 1)), n111 = gate_hash(i + vec3(1, 1, 1));
    return mix(mix(mix(n000, n100, u.x), mix(n010, n110, u.x), u.y),
               mix(mix(n001, n101, u.x), mix(n011, n111, u.x), u.y), u.z);
}

float gate_fbm(vec3 p) {
    float s = 0.0, a = 0.5, w = 0.0;
    for (int i = 0; i < 5; i++) {
        s += gate_noise(p) * a;
        w += a;
        p = p * 2.03 + vec3(17.1, 9.3, 4.7);
        a *= 0.55;
    }
    return s / w;
}

vec2 gate_rot(vec2 p, float a) {
    float c = cos(a), s = sin(a);
    return vec2(c * p.x - s * p.y, s * p.x + c * p.y);
}

// keeps the hue: the brightest channel is rolled off and the others follow it, so a hot rank colour stays that
// colour instead of every channel clipping to white (white only where white light is actually added)
vec3 gate_tone(vec3 e) {
    float m = max(max(e.r, e.g), e.b);
    return m < 1e-5 ? vec3(0.0) : e * ((1.0 - exp(-m)) / m);
}

// smoothstep that also runs downhill (edge0 > edge1), which plain smoothstep leaves undefined
float gate_ss(float a, float b, float x) {
    return a < b ? smoothstep(a, b, x) : 1.0 - smoothstep(b, a, x);
}
