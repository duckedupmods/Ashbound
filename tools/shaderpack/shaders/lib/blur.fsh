// One direction of the bloom's blur: FROM is what's blurred, OUT where it lands, SIZE how much smaller than the screen, STEP the way it runs.

uniform sampler2D FROM;
uniform float viewWidth;
uniform float viewHeight;

in vec2 uv;

layout(location = 0) out vec4 outColor;

void main() {
    vec2 px = STEP * SIZE / vec2(viewWidth, viewHeight);
    vec3 c = texture(FROM, uv).rgb * 0.1964826;
    c += (texture(FROM, uv + px * 1.411765).rgb + texture(FROM, uv - px * 1.411765).rgb) * 0.2969069;
    c += (texture(FROM, uv + px * 3.294118).rgb + texture(FROM, uv - px * 3.294118).rgb) * 0.0944704;
    c += (texture(FROM, uv + px * 5.176471).rgb + texture(FROM, uv - px * 5.176471).rgb) * 0.0103814;
    outColor = vec4(c, 1.0);
}
