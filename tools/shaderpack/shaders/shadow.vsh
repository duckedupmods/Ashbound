#version 330 compatibility

#include "/lib/settings.glsl"
#include "/lib/common.glsl"

in vec4 mc_Entity;
in vec2 mc_midTexCoord;

uniform mat4 shadowModelViewInverse;

out vec2 uv;
out float alpha;
flat out int blockId;

void main() {
    uv = (gl_TextureMatrix[0] * gl_MultiTexCoord0).xy;
    alpha = gl_Color.a;
    blockId = int(mc_Entity.x + 0.5);
    vec4 view = gl_ModelViewMatrix * gl_Vertex;
#ifdef FOLIAGE_SWAY
    if (blockId == ID_LEAVES || blockId == ID_PLANT) {
        vec3 at = (shadowModelViewInverse * view).xyz;
        float amount = blockId == ID_LEAVES ? 1.0 : gl_MultiTexCoord0.t < mc_midTexCoord.t ? 1.6 : 0.0;
        view = shadowModelView * vec4(at + sway(at + cameraPosition, amount), 1.0);
    }
#endif
    gl_Position = gl_ProjectionMatrix * view;
    gl_Position.xy = distort(gl_Position.xy);
}
