#include "/lib/settings.glsl"
#include "/lib/common.glsl"

out vec3 ray;
out vec4 tint;

void main() {
    vec4 view = gl_ModelViewMatrix * gl_Vertex;
    ray = mat3(gbufferModelViewInverse) * view.xyz;
    tint = gl_Color;
    gl_Position = gl_ProjectionMatrix * view;
}
