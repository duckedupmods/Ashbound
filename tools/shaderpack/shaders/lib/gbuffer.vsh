// The vertex half of everything drawn into the world. Programs say what they are with defines (tools/emberlight.py).

#include "/lib/settings.glsl"
#include "/lib/common.glsl"

#ifdef TERRAIN
in vec4 mc_Entity;
in vec2 mc_midTexCoord;
#endif

out vec2 uv;
out vec2 lm;
out vec4 tint;
out vec3 feet;
out vec3 normal;
flat out int blockId;

void main() {
    uv = (gl_TextureMatrix[0] * gl_MultiTexCoord0).xy;
    lm = clamp((gl_TextureMatrix[1] * gl_MultiTexCoord1).xy * 33.05 / 32.0 - 1.05 / 32.0, 0.0, 1.0);
    tint = gl_Color;
    normal = normalize(mat3(gbufferModelViewInverse) * (gl_NormalMatrix * gl_Normal));
    blockId = -1;
    vec4 view = gl_ModelViewMatrix * gl_Vertex;
    feet = (gbufferModelViewInverse * view).xyz;
#ifdef TERRAIN
    blockId = int(mc_Entity.x + 0.5);
    #ifdef FOLIAGE_SWAY
    if (blockId == ID_LEAVES || blockId == ID_PLANT) {
        float amount = blockId == ID_LEAVES ? 1.0 : gl_MultiTexCoord0.t < mc_midTexCoord.t ? 1.6 : 0.0;
        feet += sway(feet + cameraPosition, amount) * smoothstep(0.2, 0.7, lm.y);
        view = gbufferModelView * vec4(feet, 1.0);
    }
    #endif
#endif
    gl_Position = gl_ProjectionMatrix * view;
}
