#version 300 es
precision highp float;

in vec2 vUV;
in float vPotential;
in float vSigma;
in float vLapse;
uniform sampler2D uCurvature;
uniform sampler2D uVorticity;
uniform float uContourCount;
uniform float uTime;
out vec4 fragColor;

void main() {
    float bands = abs(fract(vPotential * uContourCount) - 0.5);
    float contour = 1.0 - smoothstep(0.43, 0.50, bands);
    float curvature = texture(uCurvature, vUV).r;
    float vorticity = texture(uVorticity, vUV).r;
    // Effective redshift/time-dilation cues are explicitly visual metaphors.
    float localClock = uTime * max(vLapse, 0.001);
    float pulse = 0.5 + 0.5 * sin(localClock * 2.0);
    vec3 wellColor = mix(vec3(0.03, 0.06, 0.15), vec3(0.82, 0.20, 0.12), pulse);
    vec3 flowColor = vec3(0.15, 0.55, 0.72) * clamp(abs(vorticity), 0.0, 1.0);
    vec3 color = wellColor * (0.35 + 0.65 * contour) + flowColor + 0.08 * abs(curvature);
    fragColor = vec4(color, 1.0);
}
