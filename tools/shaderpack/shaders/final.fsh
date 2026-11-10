#version 330 compatibility

// The grade: warm lights over cool shadows, colour kept strong, the way an anime background is painted.

#include "/lib/settings.glsl"
#include "/lib/common.glsl"

uniform sampler2D colortex0;
uniform sampler2D colortex2;
uniform sampler2D colortex5;

in vec2 uv;

layout(location = 0) out vec4 outColor;

vec3 filmic(vec3 x) {
    return clamp(x * (2.51 * x + 0.03) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0);
}

void main() {
    vec3 c = texture(colortex0, uv).rgb;
    c += (texture(colortex2, uv).rgb * 0.55 + texture(colortex5, uv).rgb * 0.75) * BLOOM_STRENGTH;

    // your eyes open up underground, so caves are dark but never unreadable
    float open = hasSkylight ? float(eyeBrightnessSmooth.y) / 240.0 : 0.0;
    c = filmic(c * 0.62 * EXPOSURE * mix(1.5, 1.0, open));

    float l = dot(c, LUMA);
    c = mix(vec3(l), c, SATURATION);
    c *= mix(vec3(0.94, 0.98, 1.08), vec3(1.05, 1.0, 0.93), smoothstep(0.1, 0.75, l));
    vec2 p = uv - 0.5;
    c *= 1.0 - VIGNETTE * smoothstep(0.2, 0.75, dot(p, p) * 2.0);

    c = pow(clamp(c, 0.0, 1.0), vec3(1.0 / 2.2));
    outColor = vec4(c + (dither(gl_FragCoord.xy) - 0.5) / 255.0, 1.0);
}
