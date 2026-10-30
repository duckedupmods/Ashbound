#version 150
#moj_import <ashbound:gate_noise.glsl>

// Added light in shapes. texCoord0 in -1..1 over the quad; texCoord2.x picks the shape:
// 0 = a round glow with a white heart (flashes, the beam's head), 1 = a long thin lens streak,
// 2 = a line, soft across its width (arcs, cracks, the shockwave ring).
uniform vec4 ColorModulator;

in vec4 vertexColor;
in vec2 texCoord0;
in vec2 texCoord2;

out vec4 fragColor;

void main() {
    int mode = int(texCoord2.x + 0.5);
    vec2 p = texCoord0;
    vec3 col = vertexColor.rgb;
    vec3 e;
    if (mode == 0) {
        float r2 = dot(p, p);
        e = col * exp(-r2 * 5.0) * 1.8 + mix(col, vec3(1.0), 0.6) * exp(-r2 * 28.0) * 1.4;
        e *= gate_ss(1.0, 0.8, sqrt(r2));
    } else if (mode == 1) {
        float k = exp(-abs(p.y) * 9.0) * exp(-abs(p.x) * 2.2) * gate_ss(1.0, 0.6, abs(p.x)) * gate_ss(1.0, 0.7, abs(p.y));
        e = (col * 0.8 + vec3(0.2)) * k * 2.2;
    } else {
        float k = exp(-p.y * p.y * 7.0);
        e = col * k * 1.5 + mix(col, vec3(1.0), 0.5) * exp(-p.y * p.y * 40.0) * 0.8;
    }
    e *= vertexColor.a;
    fragColor = vec4(vec3(1.0) - exp(-e), 0.0) * ColorModulator;
}
