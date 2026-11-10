#version 150

// The glow on the effects (client/Bloom): nine taps along Step, one texel apart with bilinear pairs, or a plain copy
// when Step is zero. Gain is how much of it goes over the frame.
uniform sampler2D Sampler0;
uniform vec2 Step;
uniform float Gain;

in vec2 texCoord0;

out vec4 fragColor;

void main() {
    vec4 c = texture(Sampler0, texCoord0) * 0.227027;
    c += (texture(Sampler0, texCoord0 + Step * 1.384615) + texture(Sampler0, texCoord0 - Step * 1.384615)) * 0.316216;
    c += (texture(Sampler0, texCoord0 + Step * 3.230769) + texture(Sampler0, texCoord0 - Step * 3.230769)) * 0.070270;
    fragColor = c * Gain;
}
