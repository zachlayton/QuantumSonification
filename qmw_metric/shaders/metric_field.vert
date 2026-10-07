#version 300 es
precision highp float;

in vec3 aPosition;
in vec2 aUV;
uniform sampler2D uPotential;
uniform sampler2D uSigma;
uniform sampler2D uLapse;
uniform mat4 uModelViewProjection;
uniform float uHeightScale;
out vec2 vUV;
out float vPotential;
out float vSigma;
out float vLapse;

void main() {
    float phi = texture(uPotential, aUV).r;
    float sigma = texture(uSigma, aUV).r;
    float lapse = texture(uLapse, aUV).r;
    vec3 displaced = aPosition;
    displaced.z += uHeightScale * (-phi);
    // The x/y mesh coordinates remain the same coordinates sampled by Python.
    gl_Position = uModelViewProjection * vec4(displaced, 1.0);
    vUV = aUV;
    vPotential = phi;
    vSigma = sigma;
    vLapse = lapse;
}
