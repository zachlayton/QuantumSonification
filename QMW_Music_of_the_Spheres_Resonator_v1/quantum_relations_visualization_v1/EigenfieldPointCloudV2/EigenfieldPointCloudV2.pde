/**
 * Eigenfield Point Cloud V2
 *
 * Receives:
 *   eigenfield cloud/events on UDP 7440
 *   quantum relations/measurement on UDP 7450
 *
 * Required library: oscP5
 */

import oscP5.*;

OscP5 cloudOsc;
OscP5 relationOsc;

final int CLOUD_PORT = 7440;
final int RELATION_PORT = 7450;
final int MAX_MODES = 256;
final int MAX_QUBITS = 8;

int modeCount = 0;
int qubitCount = 4;

float[] cloudX = new float[MAX_MODES];
float[] cloudY = new float[MAX_MODES];
float[] cloudZ = new float[MAX_MODES];
float[] eigenvalues = new float[MAX_MODES];
float[] probabilities = new float[MAX_MODES];
float[] amplitudes = new float[MAX_MODES];
float[] phases = new float[MAX_MODES];

float[] env = new float[MAX_MODES];
float[] envPeak = new float[MAX_MODES];
float[] envStart = new float[MAX_MODES];
float[] attackMs = new float[MAX_MODES];
float[] durationMs = new float[MAX_MODES];
float[] releaseMs = new float[MAX_MODES];
float[] sustain = new float[MAX_MODES];

float superpositionX = 0;
float superpositionY = 0;
float superpositionZ = 0;
float purity = 1;
float globalEntropy = 0;

float[][] mutualInfo = new float[MAX_QUBITS][MAX_QUBITS];
float[][] concurrence = new float[MAX_QUBITS][MAX_QUBITS];

String measurementBasis = "Z";
String measurementMode = "probe";
String measurementBitstring = "";
int measurementOutcome = -1;
float measurementProbability = 0;
float measurementFlash = 0;

float rotX = -0.28;
float rotY = 0.55;
float targetRotX = rotX;
float targetRotY = rotY;
float zoom = 1.0;
boolean autoRotate = true;
boolean showSpectralLinks = true;
boolean showEntanglement = true;
boolean showLabels = false;

void settings() {
  size(1280, 840, P3D);
  smooth(8);
}

void setup() {
  surface.setTitle("Quantum Eigenfield — Superposition, Entanglement, Measurement");
  frameRate(60);
  cloudOsc = new OscP5(this, CLOUD_PORT);
  relationOsc = new OscP5(this, RELATION_PORT);
  textFont(createFont("Arial", 13));
}

void draw() {
  background(4);
  updateEnvelopes();
  measurementFlash *= 0.92;

  if (autoRotate) targetRotY += 0.0015;
  rotX = lerp(rotX, targetRotX, 0.12);
  rotY = lerp(rotY, targetRotY, 0.12);

  drawHUD();

  pushMatrix();
  translate(width * 0.52, height * 0.56, 0);
  scale(zoom);
  rotateX(rotX);
  rotateY(rotY);

  float superposition = basisSuperposition();
  float expansion = 0.78 + 0.72 * superposition;
  float sx = min(width, height) * 0.34 * expansion;
  float sy = min(width, height) * 0.28 * expansion;
  float sz = min(width, height) * 0.28 * expansion;

  drawAxes(sx, sy, sz);
  if (showSpectralLinks) drawSpectralLinks(sx, sy, sz);
  if (showEntanglement) drawEntanglementConstellations(sx, sy, sz);
  drawPoints(sx, sy, sz);
  drawMeasurementPlane(sx, sy, sz);

  popMatrix();
  drawLegend();
}

float basisSuperposition() {
  if (measurementBasis.equals("X")) return superpositionX;
  if (measurementBasis.equals("Y")) return superpositionY;
  return superpositionZ;
}

void drawHUD() {
  hint(DISABLE_DEPTH_TEST);
  fill(240);
  textAlign(LEFT, TOP);
  textSize(20);
  text("Quantum Eigenfield", 24, 18);

  fill(155);
  textSize(12);
  text(
    "basis " + measurementBasis
    + "   superposition " + nf(basisSuperposition(), 1, 3)
    + "   purity " + nf(purity, 1, 3)
    + "   entropy " + nf(globalEntropy, 1, 3),
    24, 49
  );

  if (measurementOutcome >= 0) {
    fill(220 + 35 * measurementFlash);
    text(
      "measurement " + measurementMode
      + "   outcome " + measurementBitstring
      + "   p=" + nf(measurementProbability, 1, 4),
      24, 69
    );
  }
  hint(ENABLE_DEPTH_TEST);
}

void drawAxes(float sx, float sy, float sz) {
  strokeWeight(1);
  stroke(85); line(-sx, 0, 0, sx, 0, 0);
  stroke(70); line(0, -sy, 0, 0, sy, 0);
  stroke(60); line(0, 0, -sz, 0, 0, sz);
  noStroke();
}

void drawSpectralLinks(float sx, float sy, float sz) {
  if (modeCount < 2) return;
  for (int i = 0; i < modeCount - 1; i++) {
    float activity = max(env[i], env[i + 1]);
    float alpha = 12 + 90 * max(activity, max(probabilities[i], probabilities[i + 1]));
    stroke(175, alpha);
    line(
      cloudX[i] * sx, -cloudY[i] * sy, cloudZ[i] * sz,
      cloudX[i + 1] * sx, -cloudY[i + 1] * sy, cloudZ[i + 1] * sz
    );
  }
  noStroke();
}

void drawEntanglementConstellations(float sx, float sy, float sz) {
  if (qubitCount < 2 || modeCount < 2) return;

  for (int i = 0; i < qubitCount; i++) {
    for (int j = i + 1; j < qubitCount; j++) {
      float mi = mutualInfo[i][j];
      float c = concurrence[i][j];
      float strength = constrain(0.45 * mi + 0.75 * c, 0, 1.5);
      if (strength < 0.01) continue;

      int modeA = round(map(i, 0, max(1, qubitCount - 1), 0, modeCount - 1));
      int modeB = round(map(j, 0, max(1, qubitCount - 1), 0, modeCount - 1));

      float x0 = cloudX[modeA] * sx;
      float y0 = -cloudY[modeA] * sy;
      float z0 = cloudZ[modeA] * sz;
      float x1 = cloudX[modeB] * sx;
      float y1 = -cloudY[modeB] * sy;
      float z1 = cloudZ[modeB] * sz;

      strokeWeight(1.0 + 5.0 * strength);
      stroke(230, 35 + 150 * strength);
      line(x0, y0, z0, x1, y1, z1);

      // Shared envelope pulse along the relational edge.
      float shared = max(env[modeA], env[modeB]) * strength;
      if (shared > 0.02) {
        noStroke();
        fill(255, 80 + 150 * shared);
        float t = 0.5 + 0.4 * sin(frameCount * 0.05);
        pushMatrix();
        translate(lerp(x0, x1, t), lerp(y0, y1, t), lerp(z0, z1, t));
        sphere(3 + 8 * shared);
        popMatrix();
      }
    }
  }
  strokeWeight(1);
  noStroke();
}

void drawPoints(float sx, float sy, float sz) {
  sphereDetail(10);
  float superposition = basisSuperposition();

  for (int i = 0; i < modeCount; i++) {
    float x = cloudX[i] * sx;
    float y = -cloudY[i] * sy;
    float z = cloudZ[i] * sz;

    float p = constrain(probabilities[i], 0, 1);
    float a = constrain(amplitudes[i], 0, 1);
    float e = constrain(env[i], 0, 1);

    float visibility = lerp(0.30, 1.0, superposition);
    float size = visibility * (
      4 + 24 * pow(max(p, 0.0001), 0.35) + 34 * e + 8 * a
    );

    float phaseNorm = (phases[i] + PI) / TWO_PI;

    pushMatrix();
    translate(x, y, z);
    noStroke();

    float flashBoost = measurementFlash * measurementSelectionWeight(i);
    fill(
      85 + 135 * phaseNorm + 35 * e + 70 * flashBoost,
      110 + 90 * (1 - abs(phaseNorm - 0.5) * 2) + 35 * e,
      220 - 115 * phaseNorm + 35 * e,
      75 + 175 * max(p, max(e, flashBoost))
    );
    sphere(size * 0.5);

    if (e > 0.01 || flashBoost > 0.01) {
      noFill();
      stroke(255, 60 + 180 * max(e, flashBoost));
      strokeWeight(1 + 2.5 * max(e, flashBoost));
      sphere(size * (0.72 + 0.8 * max(e, flashBoost)));
      noStroke();
    }

    if (showLabels && (p > 0.05 || e > 0.2)) {
      hint(DISABLE_DEPTH_TEST);
      fill(240);
      textAlign(LEFT, CENTER);
      textSize(10);
      text("#" + i + " λ=" + nf(eigenvalues[i], 1, 3), size, 0);
      hint(ENABLE_DEPTH_TEST);
    }
    popMatrix();
  }
}

float measurementSelectionWeight(int modeIndex) {
  if (measurementOutcome < 0 || modeCount < 1) return 0;
  int selected = measurementOutcome % modeCount;
  float distance = abs(modeIndex - selected);
  return exp(-0.5 * sq(distance / max(1.0, modeCount * 0.06)));
}

void drawMeasurementPlane(float sx, float sy, float sz) {
  if (measurementFlash < 0.01) return;

  pushMatrix();
  noFill();
  stroke(255, 40 + 150 * measurementFlash);
  strokeWeight(1.5 + 2 * measurementFlash);

  if (measurementBasis.equals("X")) {
    rotateY(HALF_PI);
    box(2, sy * 2, sz * 2);
  } else if (measurementBasis.equals("Y")) {
    rotateX(HALF_PI);
    box(sx * 2, 2, sz * 2);
  } else {
    box(sx * 2, sy * 2, 2);
  }
  popMatrix();
  noStroke();
}

void updateEnvelopes() {
  float now = millis();
  for (int i = 0; i < modeCount; i++) {
    float elapsed = now - envStart[i];
    if (envPeak[i] <= 0 || elapsed < 0) {
      env[i] = 0;
      continue;
    }

    float a = max(attackMs[i], 1);
    float d = max(durationMs[i], a + 1);
    float r = max(releaseMs[i], 1);
    float s = constrain(sustain[i], 0, 1);

    float level = 0;
    if (elapsed <= a) level = elapsed / a;
    else if (elapsed <= d) level = lerp(1, s, (elapsed - a) / max(d - a, 1));
    else if (elapsed <= d + r) level = s * (1 - (elapsed - d) / r);
    else envPeak[i] = 0;

    env[i] = constrain(level * envPeak[i], 0, 1);
  }
}

void triggerMode(int index, float amp, float attack, float duration, float release, float sustainValue) {
  if (index < 0 || index >= MAX_MODES) return;
  envPeak[index] = constrain(amp, 0, 1);
  envStart[index] = millis();
  attackMs[index] = max(1, attack);
  durationMs[index] = max(attackMs[index] + 1, duration);
  releaseMs[index] = max(1, release);
  sustain[index] = constrain(sustainValue, 0, 1);
}

void oscEvent(OscMessage m) {
  String a = m.addrPattern();

  if (a.equals("/eigenfield/cloud/count")) { modeCount = constrain(m.get(0).intValue(), 0, MAX_MODES); return; }
  if (a.equals("/eigenfield/cloud/x")) { copyList(m, cloudX); return; }
  if (a.equals("/eigenfield/cloud/y")) { copyList(m, cloudY); return; }
  if (a.equals("/eigenfield/cloud/z")) { copyList(m, cloudZ); return; }
  if (a.equals("/eigenfield/cloud/eigenvalues")) { copyList(m, eigenvalues); return; }
  if (a.equals("/eigenfield/cloud/probabilities")) { copyList(m, probabilities); return; }
  if (a.equals("/eigenfield/cloud/amplitudes")) { copyList(m, amplitudes); return; }
  if (a.equals("/eigenfield/cloud/phases")) { copyList(m, phases); return; }

  if (a.equals("/eigenfield/time/event") && m.arguments().length >= 10) {
    triggerMode(
      m.get(0).intValue(),
      m.get(4).floatValue(),
      m.get(5).floatValue(),
      m.get(6).floatValue(),
      m.get(7).floatValue(),
      m.get(8).floatValue()
    );
    return;
  }

  if (a.equals("/quantum/superposition/x")) { superpositionX = m.get(0).floatValue(); return; }
  if (a.equals("/quantum/superposition/y")) { superpositionY = m.get(0).floatValue(); return; }
  if (a.equals("/quantum/superposition/z")) { superpositionZ = m.get(0).floatValue(); return; }
  if (a.equals("/quantum/global/purity")) { purity = m.get(0).floatValue(); return; }
  if (a.equals("/quantum/global/entropy_bits")) { globalEntropy = m.get(0).floatValue(); return; }
  if (a.equals("/quantum/relations/qubits")) { qubitCount = constrain(m.get(0).intValue(), 1, MAX_QUBITS); return; }

  if (a.equals("/quantum/mutual_information/matrix")) {
    copyMatrix(m, mutualInfo, qubitCount);
    return;
  }

  if (a.equals("/quantum/concurrence/matrix")) {
    copyMatrix(m, concurrence, qubitCount);
    return;
  }

  if (a.equals("/quantum/measurement/basis")) { measurementBasis = m.get(0).stringValue(); return; }
  if (a.equals("/quantum/measurement/mode")) { measurementMode = m.get(0).stringValue(); return; }
  if (a.equals("/quantum/measurement/outcome")) { measurementOutcome = m.get(0).intValue(); return; }
  if (a.equals("/quantum/measurement/probability")) { measurementProbability = m.get(0).floatValue(); return; }
  if (a.equals("/quantum/measurement/bitstring")) { measurementBitstring = m.get(0).stringValue(); return; }
  if (a.equals("/quantum/measurement/flash")) { measurementFlash = 1.0; return; }
}

void copyList(OscMessage m, float[] destination) {
  int count = min(m.arguments().length, destination.length);
  for (int i = 0; i < count; i++) {
    try { destination[i] = m.get(i).floatValue(); }
    catch (Exception e) { destination[i] = 0; }
  }
  modeCount = max(modeCount, count);
}

void copyMatrix(OscMessage m, float[][] destination, int n) {
  int count = min(m.arguments().length, n * n);
  for (int k = 0; k < count; k++) {
    int i = k / n;
    int j = k % n;
    destination[i][j] = m.get(k).floatValue();
  }
}

void drawLegend() {
  hint(DISABLE_DEPTH_TEST);
  float x = width - 285;
  float y = 22;
  fill(14, 225);
  noStroke();
  rect(x - 14, y - 10, 270, 154, 8);
  fill(215);
  textAlign(LEFT, TOP);
  textSize(12);
  text("Controls", x, y);
  fill(145);
  text(
    "drag: rotate\nwheel: zoom\nspace: auto-rotate\n"
    + "c: spectral links\ne: entanglement links\n"
    + "l: labels\nx/y/z: display basis\nr: reset view",
    x, y + 24
  );
  hint(ENABLE_DEPTH_TEST);
}

void mouseDragged() {
  autoRotate = false;
  targetRotY += (mouseX - pmouseX) * 0.008;
  targetRotX += (mouseY - pmouseY) * 0.008;
  targetRotX = constrain(targetRotX, -HALF_PI, HALF_PI);
}

void mouseWheel(processing.event.MouseEvent event) {
  zoom *= pow(0.92, event.getCount());
  zoom = constrain(zoom, 0.35, 3.5);
}

void keyPressed() {
  if (key == ' ') autoRotate = !autoRotate;
  if (key == 'c' || key == 'C') showSpectralLinks = !showSpectralLinks;
  if (key == 'e' || key == 'E') showEntanglement = !showEntanglement;
  if (key == 'l' || key == 'L') showLabels = !showLabels;
  if (key == 'x' || key == 'X') measurementBasis = "X";
  if (key == 'y' || key == 'Y') measurementBasis = "Y";
  if (key == 'z' || key == 'Z') measurementBasis = "Z";
  if (key == 'r' || key == 'R') {
    targetRotX = -0.28;
    targetRotY = 0.55;
    zoom = 1.0;
  }
}
