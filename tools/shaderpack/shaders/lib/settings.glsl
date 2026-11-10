// Emberlight's options, shown on Iris's pack screen. Bracketed lists are the choices offered.

const int shadowMapResolution = 2048; // [1024 2048 3072 4096]
const float shadowDistance = 128.0; // [64.0 96.0 128.0 192.0 256.0]
const float sunPathRotation = -28.0; // [-40.0 -28.0 -15.0 0.0]
const float eyeBrightnessHalflife = 3.0;
const float ambientOcclusionLevel = 1.0;
const bool shadowtex0Nearest = true;

#define SHADOW_SOFT 1.6 // [0.8 1.2 1.6 2.4 3.2]
#define EMBER_STRENGTH 1.0 // [0.6 0.8 1.0 1.25 1.5]
#define BLOOM_STRENGTH 0.5 // [0.0 0.25 0.5 0.75 1.0]
#define GODRAYS
#define RAYS_STRENGTH 0.5 // [0.25 0.5 0.75 1.0]
#define INK_EDGES
#define INK_STRENGTH 0.45 // [0.2 0.3 0.45 0.6 0.8]
#define FOLIAGE_SWAY
#define WATER_WAVES
#define VIGNETTE 0.3 // [0.0 0.15 0.3 0.45]
#define EXPOSURE 1.0 // [0.7 0.85 1.0 1.15 1.3]
#define SATURATION 1.12 // [0.9 1.0 1.12 1.25]

// block.properties
#define ID_PLANT 10001
#define ID_LEAVES 10002
#define ID_WATER 10010
#define ID_GLOW 10020
