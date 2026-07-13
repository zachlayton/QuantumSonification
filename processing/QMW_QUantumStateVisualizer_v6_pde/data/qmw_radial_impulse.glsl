#ifdef GL_ES
precision mediump float;
precision mediump int;
#endif

#define PROCESSING_COLOR_SHADER

uniform vec2 resolution;
uniform float time;
uniform float fieldStrength;
uniform float centerEnergy;

uniform float band0;
uniform float band1;
uniform float band2;
uniform float band3;
uniform float band4;
uniform float band5;
uniform float band6;
uniform float band7;

uniform float phase0;
uniform float phase1;
uniform float phase2;
uniform float phase3;
uniform float phase4;
uniform float phase5;
uniform float phase6;
uniform float phase7;

float ring(float r, float center, float width) {
  float d = (r - center) / width;
  return exp(-d * d);
}

vec3 palette(float t) {
  vec3 a = vec3(0.46, 0.40, 0.42);
  vec3 b = vec3(0.48, 0.40, 0.36);
  vec3 c = vec3(1.00, 1.00, 1.00);
  vec3 d = vec3(0.02, 0.28, 0.62);
  return a + b * cos(6.28318 * (c * t + d));
}

vec3 addBand(vec2 p, float r, float angle, float band, float phase, float radius, float hue) {
  float outward = fract(time * 0.16 + radius * 0.72);
  float impulse = ring(r, outward, 0.030 + band * 0.020);
  float shell = ring(r, radius, 0.018 + band * 0.028);
  float angular = 0.64 + 0.36 * cos(angle * (3.0 + radius * 12.0) + phase + time * 0.65);
  float energy = band * (shell + 0.55 * impulse) * angular;
  return palette(hue + phase * 0.08 + time * 0.025) * energy;
}

void main() {
  vec2 uv = gl_FragCoord.xy / resolution.xy;
  vec2 p = uv * 2.0 - 1.0;
  p.x *= resolution.x / resolution.y;

  float r = length(p);
  float angle = atan(p.y, p.x);
  float vignette = smoothstep(1.35, 0.16, r);
  float grid = 0.030 / max(0.015, abs(fract(r * 18.0 - time * 0.10) - 0.5));
  grid = clamp(grid, 0.0, 0.18);

  float center = centerEnergy * exp(-r * r * 48.0);
  vec3 color = vec3(0.004, 0.006, 0.010);
  color += vec3(0.95, 0.98, 1.0) * center;
  color += vec3(0.08, 0.16, 0.22) * grid * vignette;

  color += addBand(p, r, angle, band0, phase0, 0.12, 0.02);
  color += addBand(p, r, angle, band1, phase1, 0.20, 0.10);
  color += addBand(p, r, angle, band2, phase2, 0.29, 0.18);
  color += addBand(p, r, angle, band3, phase3, 0.38, 0.30);
  color += addBand(p, r, angle, band4, phase4, 0.49, 0.44);
  color += addBand(p, r, angle, band5, phase5, 0.61, 0.58);
  color += addBand(p, r, angle, band6, phase6, 0.74, 0.72);
  color += addBand(p, r, angle, band7, phase7, 0.88, 0.86);

  float glow = exp(-r * 1.8) * (0.08 + fieldStrength * 0.30);
  color += vec3(0.10, 0.22, 0.32) * glow;
  color *= vignette;

  gl_FragColor = vec4(pow(color, vec3(0.82)), 1.0);
}
