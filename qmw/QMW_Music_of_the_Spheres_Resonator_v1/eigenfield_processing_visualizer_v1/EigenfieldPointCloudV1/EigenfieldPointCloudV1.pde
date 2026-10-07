/**
 * Eigenfield Point Cloud Visualizer v1
 *
 * Processing 4 sketch for eigenfield_timing_layer_v1.py.
 *
 * Dependencies:
 *   oscP5
 *
 * OSC input:
 *   UDP 7440
 *
 * Cloud mapping:
 *   x = normalized log eigenvalue
 *   y = quantum mode probability
 *   z = complex mode phase
 *
 * Visual mapping:
 *   point position   <- eigenvalue / probability / phase
 *   point diameter   <- mode amplitude + envelope activity
 *   point brightness <- trigger/envelope activity
 *   halo radius      <- current envelope amplitude
 *   trail length     <- release time
 */

import oscP5.*;
import netP5.*;

OscP5 oscP5;

final int OSC_PORT = 7440;
final int MAX_MODES = 256;

int modeCount = 0;

float[] cloudX = new float[MAX_MODES];
float[] cloudY = new float[MAX_MODES];
float[] cloudZ = new float[MAX_MODES];

float[] eigenvalues = new float[MAX_MODES];
float[] probabilities = new float[MAX_MODES];
float[] amplitudes = new float[MAX_MODES];
float[] phases = new float[MAX_MODES];

float[] envelopeLevel = new float[MAX_MODES];
float[] envelopePeak = new float[MAX_MODES];
float[] envelopeStartMs = new float[MAX_MODES];
float[] attackMs = new float[MAX_MODES];
float[] durationMs = new float[MAX_MODES];
float[] releaseMs = new float[MAX_MODES];
float[] sustain = new float[MAX_MODES];

float rotationX = -0.28;
float rotationY = 0.55;
float targetRotationX = rotationX;
float targetRotationY = rotationY;
float zoom = 1.0;

boolean autoRotate = true;
boolean drawConnections = true;
boolean drawLabels = false;
boolean drawAxes = true;

PFont uiFont;

void settings() {
  size(1280, 820, P3D);
  smooth(8);
}

void setup() {
  surface.setTitle("Quantum Eigenfield — Point Density Cloud");
  frameRate(60);

  oscP5 = new OscP5(this, OSC_PORT);

  uiFont = createFont("Arial", 14);
  textFont(uiFont);

  for (int i = 0; i < MAX_MODES; i++) {
    cloudX[i] = 0;
    cloudY[i] = 0;
    cloudZ[i] = 0;
    probabilities[i] = 0;
    amplitudes[i] = 0;
    phases[i] = 0;
    envelopeLevel[i] = 0;
  }

  println("Eigenfield visualizer listening on UDP " + OSC_PORT);
}

void draw() {
  background(5);

  updateEnvelopeLevels();

  if (autoRotate) {
    targetRotationY += 0.0018;
  }

  rotationX = lerp(rotationX, targetRotationX, 0.12);
  rotationY = lerp(rotationY, targetRotationY, 0.12);

  drawHeader();

  pushMatrix();
  translate(width * 0.52, height * 0.54, 0);
  scale(zoom);
  rotateX(rotationX);
  rotateY(rotationY);

  float cloudScaleX = min(width, height) * 0.34;
  float cloudScaleY = min(width, height) * 0.30;
  float cloudScaleZ = min(width, height) * 0.28;

  if (drawAxes) {
    drawCoordinateAxes(cloudScaleX, cloudScaleY, cloudScaleZ);
  }

  if (drawConnections) {
    drawSpectralConnections(cloudScaleX, cloudScaleY, cloudScaleZ);
  }

  drawPoints(cloudScaleX, cloudScaleY, cloudScaleZ);
  popMatrix();

  drawLegend();
}

void drawHeader() {
  hint(DISABLE_DEPTH_TEST);
  fill(240);
  textAlign(LEFT, TOP);
  textSize(20);
  text("Quantum Eigenfield", 24, 20);

  fill(150);
  textSize(12);
  text(
    "x: log eigenvalue    y: quantum probability    z: complex phase",
    24, 50
  );

  text(
    "modes: " + modeCount
    + "    OSC: " + OSC_PORT
    + "    FPS: " + nf(frameRate, 1, 1),
    24, 70
  );
  hint(ENABLE_DEPTH_TEST);
}

void drawCoordinateAxes(float sx, float sy, float sz) {
  strokeWeight(1.0);

  stroke(110);
  line(-sx, 0, 0, sx, 0, 0);

  stroke(90);
  line(0, -sy, 0, 0, sy, 0);

  stroke(70);
  line(0, 0, -sz, 0, 0, sz);

  noStroke();
}

void drawSpectralConnections(float sx, float sy, float sz) {
  if (modeCount < 2) return;

  strokeWeight(1.0);

  for (int i = 0; i < modeCount - 1; i++) {
    float p0 = probabilities[i];
    float p1 = probabilities[i + 1];
    float activity = max(envelopeLevel[i], envelopeLevel[i + 1]);

    float alpha = 15 + 90 * max(max(p0, p1), activity);
    stroke(180, alpha);

    float x0 = cloudX[i] * sx;
    float y0 = -cloudY[i] * sy;
    float z0 = cloudZ[i] * sz;

    float x1 = cloudX[i + 1] * sx;
    float y1 = -cloudY[i + 1] * sy;
    float z1 = cloudZ[i + 1] * sz;

    line(x0, y0, z0, x1, y1, z1);
  }

  noStroke();
}

void drawPoints(float sx, float sy, float sz) {
  sphereDetail(10);

  for (int i = 0; i < modeCount; i++) {
    float x = cloudX[i] * sx;
    float y = -cloudY[i] * sy;
    float z = cloudZ[i] * sz;

    float p = constrain(probabilities[i], 0, 1);
    float a = constrain(amplitudes[i], 0, 1);
    float env = constrain(envelopeLevel[i], 0, 1);

    float baseSize = 4.0 + 24.0 * pow(max(p, 0.0001), 0.35);
    float size = baseSize + 34.0 * env + 8.0 * a;

    pushMatrix();
    translate(x, y, z);

    float brightness = 70 + 150 * max(p, env);
    float phaseNormalized = (phases[i] + PI) / TWO_PI;

    // Hue-like phase encoding using RGB interpolation without fixed palette.
    float r = 90 + 120 * phaseNormalized;
    float g = 110 + 100 * (1.0 - abs(phaseNormalized - 0.5) * 2.0);
    float b = 220 - 120 * phaseNormalized;

    ambientLight(35, 35, 35);
    pointLight(220, 220, 220, 0, 0, 400);

    noStroke();
    fill(
      constrain(r + brightness * env * 0.35, 0, 255),
      constrain(g + brightness * env * 0.35, 0, 255),
      constrain(b + brightness * env * 0.35, 0, 255),
      220
    );
    sphere(size * 0.5);

    if (env > 0.01) {
      noFill();
      stroke(255, 80 + 150 * env);
      strokeWeight(1.0 + 2.0 * env);
      sphere(size * (0.7 + 0.7 * env));
      noStroke();
    }

    if (drawLabels && (p > 0.05 || env > 0.2)) {
      hint(DISABLE_DEPTH_TEST);
      fill(240);
      textAlign(LEFT, CENTER);
      textSize(10);
      text("#" + i + "  λ=" + nf(eigenvalues[i], 1, 3), size, 0);
      hint(ENABLE_DEPTH_TEST);
    }

    popMatrix();
  }
}

void updateEnvelopeLevels() {
  float now = millis();

  for (int i = 0; i < modeCount; i++) {
    float elapsed = now - envelopeStartMs[i];

    if (envelopePeak[i] <= 0 || elapsed < 0) {
      envelopeLevel[i] = 0;
      continue;
    }

    float a = max(attackMs[i], 1);
    float d = max(durationMs[i], a + 1);
    float r = max(releaseMs[i], 1);
    float s = constrain(sustain[i], 0, 1);

    float level;

    if (elapsed <= a) {
      level = elapsed / a;
    } else if (elapsed <= d) {
      float bodyPosition = (elapsed - a) / max(d - a, 1);
      level = lerp(1.0, s, bodyPosition);
    } else if (elapsed <= d + r) {
      float releasePosition = (elapsed - d) / r;
      level = s * (1.0 - releasePosition);
    } else {
      level = 0;
      envelopePeak[i] = 0;
    }

    envelopeLevel[i] = constrain(level * envelopePeak[i], 0, 1);
  }
}

void triggerMode(
  int index,
  float amp,
  float attack,
  float duration,
  float release,
  float sustainValue
) {
  if (index < 0 || index >= MAX_MODES) return;

  envelopePeak[index] = constrain(amp, 0, 1);
  envelopeStartMs[index] = millis();
  attackMs[index] = max(1, attack);
  durationMs[index] = max(attackMs[index] + 1, duration);
  releaseMs[index] = max(1, release);
  sustain[index] = constrain(sustainValue, 0, 1);
}

void oscEvent(OscMessage message) {
  String address = message.addrPattern();

  if (address.equals("/eigenfield/cloud/count")) {
    modeCount = constrain(message.get(0).intValue(), 0, MAX_MODES);
    return;
  }

  if (address.equals("/eigenfield/cloud/x")) {
    copyFloatList(message, cloudX);
    return;
  }

  if (address.equals("/eigenfield/cloud/y")) {
    copyFloatList(message, cloudY);
    return;
  }

  if (address.equals("/eigenfield/cloud/z")) {
    copyFloatList(message, cloudZ);
    return;
  }

  if (address.equals("/eigenfield/cloud/eigenvalues")) {
    copyFloatList(message, eigenvalues);
    return;
  }

  if (address.equals("/eigenfield/cloud/probabilities")) {
    copyFloatList(message, probabilities);
    return;
  }

  if (address.equals("/eigenfield/cloud/amplitudes")) {
    copyFloatList(message, amplitudes);
    return;
  }

  if (address.equals("/eigenfield/cloud/phases")) {
    copyFloatList(message, phases);
    return;
  }

  if (address.equals("/eigenfield/time/event")) {
    if (message.arguments().length >= 10) {
      int index = message.get(0).intValue();
      float amp = message.get(4).floatValue();
      float attack = message.get(5).floatValue();
      float duration = message.get(6).floatValue();
      float release = message.get(7).floatValue();
      float sustainValue = message.get(8).floatValue();

      triggerMode(
        index,
        amp,
        attack,
        duration,
        release,
        sustainValue
      );
    }
    return;
  }
}

void copyFloatList(OscMessage message, float[] destination) {
  int count = min(message.arguments().length, destination.length);

  for (int i = 0; i < count; i++) {
    try {
      destination[i] = message.get(i).floatValue();
    } catch (Exception error) {
      destination[i] = 0;
    }
  }

  modeCount = max(modeCount, count);
}

void drawLegend() {
  hint(DISABLE_DEPTH_TEST);

  float x = width - 260;
  float y = 22;

  fill(15, 220);
  noStroke();
  rect(x - 14, y - 10, 245, 130, 8);

  fill(210);
  textAlign(LEFT, TOP);
  textSize(12);
  text("Controls", x, y);

  fill(145);
  text(
    "drag: rotate\n"
    + "wheel: zoom\n"
    + "space: auto-rotate\n"
    + "c: connections\n"
    + "l: labels\n"
    + "a: axes\n"
    + "r: reset view",
    x, y + 24
  );

  hint(ENABLE_DEPTH_TEST);
}

void mouseDragged() {
  autoRotate = false;
  targetRotationY += (mouseX - pmouseX) * 0.008;
  targetRotationX += (mouseY - pmouseY) * 0.008;
  targetRotationX = constrain(targetRotationX, -HALF_PI, HALF_PI);
}

void mouseWheel(processing.event.MouseEvent event) {
  float amount = event.getCount();
  zoom *= pow(0.92, amount);
  zoom = constrain(zoom, 0.35, 3.5);
}

void keyPressed() {
  if (key == ' ') autoRotate = !autoRotate;
  if (key == 'c' || key == 'C') drawConnections = !drawConnections;
  if (key == 'l' || key == 'L') drawLabels = !drawLabels;
  if (key == 'a' || key == 'A') drawAxes = !drawAxes;

  if (key == 'r' || key == 'R') {
    targetRotationX = -0.28;
    targetRotationY = 0.55;
    zoom = 1.0;
  }
}
