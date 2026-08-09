import oscP5.*;
import netP5.*;

/*
  QMW GRW event/state visualizer v1

  The Python density engine remains authoritative. This sketch renders the
  adapter's committed post-event rho as a persistent complex point field and
  delta-rho as a transient displacement/flash. It listens on the standard
  Processing port, UDP 7401.

  |rho+|          point height and size (continuing resonant condition)
  arg(rho+)       hue
  |delta rho|     transient radial displacement and brightness
  affected qubit highlighted tetrahedral branch
  Pauli delta     signed XYZ coupling arrow
*/

OscP5 oscP5;

final int MATRIX_N = 16;
final int CELL_COUNT = MATRIX_N * MATRIX_N;

float[] rhoMagnitude = new float[CELL_COUNT];
float[] rhoPhase = new float[CELL_COUNT];
float[] deltaMagnitude = new float[CELL_COUNT];
float[] deltaPhase = new float[CELL_COUNT];
float[] population = new float[MATRIX_N];
float[] branchLevels = new float[4];

int eventId = 0;
int affectedQubit = -1;
int pauliAxis = 0;
float excitation = 0.0;
float coherenceLoss = 0.0;
float bandwidth = 0.0;
float grainStructure = 0.0;
float orientationSign = 1.0;
float dominantDelta = 0.0;
float eventPulse = 0.0;
String pauliTerm = "----";
String pauliName = "I";
boolean hasState = false;

float rotX = -0.62;
float rotY = 0.72;
float zoom = 1.0;

PVector[] branchAnchors = {
  new PVector(-310, -170, -210),
  new PVector( 310, -170, -210),
  new PVector(-310,  170,  210),
  new PVector( 310,  170,  210)
};

void setup() {
  size(1280, 820, P3D);
  colorMode(HSB, 1.0);
  frameRate(60);
  smooth(8);
  textFont(createFont("Menlo", 13));
  oscP5 = new OscP5(this, 7401);
}

void draw() {
  background(0);
  eventPulse *= 0.94;

  drawHeader();
  drawStateField();
  drawEventMeters();
}

void drawHeader() {
  hint(DISABLE_DEPTH_TEST);
  camera();
  fill(1);
  text("QMW GRW SONIFICATION FIELD", 28, 32);
  fill(0, 0, 0.68);
  text("rho+ persists  |  delta rho flashes  |  qubit selects branch  |  Pauli delta orients coupling", 28, 54);
  text("OSC UDP 7401  |  drag: rotate  +/-: zoom", 28, 76);

  if (!hasState) {
    fill(0.08, 0.9, 1.0);
    text("Waiting for /qmw/grw/sonification/...", 28, 105);
  } else {
    fill(1);
    text("event " + eventId + "   qubit " + affectedQubit + "   Pauli " + pauliTerm + " (" + pauliName + ")", 28, 105);
  }
  hint(ENABLE_DEPTH_TEST);
}

void drawStateField() {
  pushMatrix();
  translate(width * 0.54, height * 0.53, 0);
  scale(zoom);
  rotateX(rotX);
  rotateY(rotY);

  ambientLight(0.18, 0.18, 0.18);
  pointLight(0, 0, 1, 0, -380, 380);

  drawReferenceCube();
  drawBranches();
  drawDensityPoints();
  drawOrientationArrow();
  popMatrix();
}

void drawReferenceCube() {
  noFill();
  stroke(0, 0, 0.24);
  strokeWeight(1);
  box(520, 330, 520);

  stroke(0, 0, 0.12);
  for (int i = -8; i <= 8; i += 2) {
    float p = i * 30.0;
    line(-240, 165, p, 240, 165, p);
    line(p, 165, -240, p, 165, 240);
  }
}

void drawDensityPoints() {
  float pulse = constrain(eventPulse, 0, 1);
  for (int row = 0; row < MATRIX_N; row++) {
    for (int col = 0; col < MATRIX_N; col++) {
      int index = row * MATRIX_N + col;
      float magnitude = constrain(rhoMagnitude[index], 0, 1);
      float delta = constrain(deltaMagnitude[index], 0, 1);
      if (magnitude < 0.002 && delta * pulse < 0.01) continue;

      float phase = rhoPhase[index];
      float hue = (phase + 1.0) * 0.5;
      float x = map(col, 0, 15, -235, 235);
      float z = map(row, 0, 15, -235, 235);
      float y = 155 - magnitude * 285;

      // delta-rho briefly opens the committed field away from its equilibrium.
      float angle = TWO_PI * deltaPhase[index] * 0.5;
      x += cos(angle) * delta * pulse * 52;
      z += sin(angle) * delta * pulse * 52;
      y -= delta * pulse * 80;

      float brightness = constrain(0.3 + magnitude * 0.65 + delta * pulse, 0, 1);
      float alpha = constrain(0.18 + magnitude * 0.72 + delta * pulse * 0.5, 0, 1);
      noStroke();
      fill(hue, 0.82, brightness, alpha);
      pushMatrix();
      translate(x, y, z);
      sphereDetail(5);
      sphere(2.5 + magnitude * 10 + delta * pulse * 7);
      popMatrix();

      if (delta * pulse > 0.08) {
        stroke(hue, 0.28, 1.0, delta * pulse);
        strokeWeight(1.5);
        line(map(col, 0, 15, -235, 235), 155 - magnitude * 285,
             map(row, 0, 15, -235, 235), x, y, z);
      }
    }
  }
}

void drawBranches() {
  for (int q = 0; q < 4; q++) {
    PVector anchor = branchAnchors[q];
    float level = constrain(branchLevels[q], 0, 1);
    boolean active = q == affectedQubit;
    float pulse = active ? eventPulse : 0;

    stroke(q / 4.0, active ? 0.9 : 0.2, active ? 1.0 : 0.48, 0.85);
    strokeWeight(active ? 3.5 : 1.2);
    noFill();
    pushMatrix();
    translate(anchor.x, anchor.y, anchor.z);
    rotateX(HALF_PI);
    ellipse(0, 0, 36 + level * 58 + pulse * 65, 36 + level * 58 + pulse * 65);
    popMatrix();

    stroke(0, 0, active ? 0.9 : 0.25, active ? 0.8 : 0.35);
    line(anchor.x, anchor.y, anchor.z, 0, 0, 0);
  }
}

void drawOrientationArrow() {
  if (pauliAxis == 0 || eventPulse < 0.015) return;
  float length = 135 + abs(dominantDelta) * 170;
  PVector direction = new PVector(0, 0, 0);
  if (pauliAxis == 1) direction.x = orientationSign;
  if (pauliAxis == 2) direction.y = orientationSign;
  if (pauliAxis == 3) direction.z = orientationSign;
  direction.mult(length);

  stroke((pauliAxis - 1) / 3.0, 0.9, 1.0, eventPulse);
  strokeWeight(5);
  line(0, 0, 0, direction.x, direction.y, direction.z);
  pushMatrix();
  translate(direction.x, direction.y, direction.z);
  noStroke();
  fill((pauliAxis - 1) / 3.0, 0.9, 1.0, eventPulse);
  sphere(10);
  popMatrix();
}

void drawEventMeters() {
  hint(DISABLE_DEPTH_TEST);
  camera();
  float left = 28;
  float top = height - 122;
  drawMeter("trace distance / excitation", excitation, left, top);
  drawMeter("coherence loss", coherenceLoss, left, top + 28);
  drawMeter("bandwidth", bandwidth, left + 405, top);
  drawMeter("grain structure", grainStructure, left + 405, top + 28);

  fill(0, 0, 0.6);
  text("rho+ population", left + 810, top - 4);
  for (int i = 0; i < 16; i++) {
    float h = constrain(population[i], 0, 1) * 62;
    fill(i / 16.0, 0.75, 0.9);
    rect(left + 810 + i * 23, top + 70 - h, 15, h);
  }
  hint(ENABLE_DEPTH_TEST);
}

void drawMeter(String label, float value, float x, float y) {
  fill(0, 0, 0.62);
  text(label, x, y);
  noStroke();
  fill(0, 0, 0.16);
  rect(x + 190, y - 11, 180, 10);
  fill(0.56, 0.72, 0.95);
  rect(x + 190, y - 11, 180 * constrain(value, 0, 1), 10);
}

void copyFloats(OscMessage message, float[] target) {
  int count = min(target.length, message.arguments().length);
  for (int i = 0; i < count; i++) target[i] = message.get(i).floatValue();
}

void oscEvent(OscMessage message) {
  String address = message.addrPattern();
  if (address.equals("/qmw/grw/sonification/post/rho_magnitude")) {
    copyFloats(message, rhoMagnitude);
    hasState = true;
  } else if (address.equals("/qmw/grw/sonification/post/rho_phase")) {
    copyFloats(message, rhoPhase);
  } else if (address.equals("/qmw/grw/sonification/delta/magnitude")) {
    copyFloats(message, deltaMagnitude);
  } else if (address.equals("/qmw/grw/sonification/delta/phase")) {
    copyFloats(message, deltaPhase);
  } else if (address.equals("/qmw/grw/sonification/post/population")) {
    copyFloats(message, population);
  } else if (address.equals("/qmw/grw/sonification/post/branch_levels")) {
    copyFloats(message, branchLevels);
  } else if (address.equals("/qmw/grw/sonification/pauli")) {
    pauliTerm = message.get(0).stringValue();
    pauliName = message.get(1).stringValue();
    dominantDelta = message.get(2).floatValue();
  } else if (address.equals("/qmw/grw/sonification/event")) {
    eventId = message.get(0).intValue();
    affectedQubit = message.get(1).intValue();
    excitation = message.get(2).floatValue();
    coherenceLoss = message.get(3).floatValue();
    bandwidth = message.get(4).floatValue();
    grainStructure = message.get(5).floatValue();
    pauliAxis = message.get(6).intValue();
    orientationSign = message.get(7).floatValue();
    dominantDelta = message.get(8).floatValue();
    eventPulse = constrain(0.2 + excitation, 0, 1);
    hasState = true;
  }
}

void mouseDragged() {
  rotY += (mouseX - pmouseX) * 0.01;
  rotX += (mouseY - pmouseY) * 0.01;
}

void keyPressed() {
  if (key == '+') zoom *= 1.08;
  if (key == '-') zoom /= 1.08;
}
