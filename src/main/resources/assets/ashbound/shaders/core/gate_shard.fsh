#version 150

// A shard of the world knocked loose off the tear: what's behind it (Sampler0, the frame so far) seen a little out
// of place, as if through broken glass, its edges catching the tear's light. texCoord0: -1..1 over the shard (its
// edges at |x| or |y| = 1); texCoord2.x: which way it bends the view (0..63 round the circle).
// vertexColor: the rank colour; alpha = how far it has grown in.
uniform sampler2D Sampler0;
uniform vec2 ScreenSize;
uniform vec4 ColorModulator;

in vec4 vertexColor;
in vec2 texCoord0;
in vec2 texCoord2;

out vec4 fragColor;

void main() {
    float a = vertexColor.a;
    if (a < 0.01) discard;
    float ang = texCoord2.x / 64.0 * 6.2831853;
    vec2 uv = gl_FragCoord.xy / ScreenSize + vec2(cos(ang), sin(ang)) * 0.018 * a;
    vec3 seen = texture(Sampler0, clamp(uv, vec2(0.001), vec2(0.999))).rgb;
    float edge = max(abs(texCoord0.x), abs(texCoord0.y));
    float rim = exp(-(1.0 - edge) * 14.0);
    // glass: a touch darker and tinted by the light it sits in, a bright lip where it broke
    vec3 e = seen * mix(vec3(0.82), vertexColor.rgb, 0.18) + mix(vertexColor.rgb, vec3(1.0), 0.5) * rim * 0.9;
    fragColor = vec4(min(e, vec3(1.0)) * a, a) * ColorModulator;
}
