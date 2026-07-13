import oscP5.*;
import netP5.*;

OscP5 oscP5;

float[][] rhoReal = new float[16][16];
float[][] rhoImag = new float[16][16];

float blochX = 0;
float blochY = 0;
float blochZ = 0;

float fieldStrength = 0;
float fieldAcceleration = 0;

void setup() {
  size(1000, 700, P3D);
  colorMode(HSB, 1.0);
  frameRate(60);
  oscP5 = new OscP5(this, 7401);
  textFont(createFont("Menlo", 12));
}

void draw() {
  background(0);

  drawDensityMatrix(40, 60, 420);
  drawBlochSphere(700, 300, 170);
  drawTextPanel();
}

void drawDensityMatrix(float x0, float y0, float size) {
  float cell = size / 16.0;

  pushMatrix();
  translate(x0, y0);

  for (int r = 0; r < 16; r++) {
    for (int c = 0; c < 16; c++) {
      float re = rhoReal[r][c];
      float im = rhoImag[r][c];

      float mag = sqrt(re * re + im * im);
      float phase = atan2(im, re);

      float hue = map(phase, -PI, PI, 0, 1);
      float brightness = constrain(mag * 12.0, 0, 1);

      fill(hue, 0.85, brightness);
      noStroke();
      rect(c * cell, r * cell, cell - 1, cell - 1);
    }
  }

  stroke(1);
  noFill();
  rect(0, 0, size, size);

  fill(1);
  text("16 × 16 density matrix: hue = phase, brightness = magnitude", 0, -15);

  popMatrix();
}

void drawBlochSphere(float cx, float cy, float radius) {
  pushMatrix();
  translate(cx, cy, 0);

  stroke(0.55);
  noFill();
  ellipse(0, 0, radius * 2, radius * 2);

  stroke(0.2, 0.4, 1.0);
  line(-radius, 0, radius, 0);
  line(0, -radius, 0, radius);

  float vx = blochX * radius;
  float vy = -blochY * radius;
  float vz = blochZ;

  stroke(0.0, 0.0, 1.0);
  strokeWeight(4);
  line(0, 0, vx, vy);

  fill(0.0, 0.0, 1.0);
  noStroke();
  ellipse(vx, vy, 12, 12);

  strokeWeight(1);
  fill(1);
  text("Bloch projection", -60, -radius - 20);
  text("x: " + nf(blochX, 1, 3), -60, radius + 25);
  text("y: " + nf(blochY, 1, 3), -60, radius + 45);
  text("z: " + nf(blochZ, 1, 3), -60, radius + 65);

  popMatrix();
}

void drawTextPanel() {
  fill(1);
  text("QMW Visualizer", 40, 10);
  text("Receiving from Python on UDP 7401", 40, 22);

  text("field strength: " + nf(fieldStrength, 1, 4), 560, 560);
  text("field acceleration: " + nf(fieldAcceleration, 1, 4), 560, 580);

  text("Max sends source changes to Python on UDP 7402", 40, 640);
  text("/qmw/excitation internal | hydrogen_spectrum | hydrogen_orbital | schrodinger_packet", 40, 660);
}

void oscEvent(OscMessage msg) {
  String addr = msg.addrPattern();

  if (addr.startsWith("/qmw/density/real/")) {
    int row = int(addr.substring(addr.lastIndexOf("/") + 1));
    for (int i = 0; i < min(16, msg.arguments().length); i++) {
      rhoReal[row][i] = msg.get(i).floatValue();
    }
  }

  else if (addr.startsWith("/qmw/density/imag/")) {
    int row = int(addr.substring(addr.lastIndexOf("/") + 1));
    for (int i = 0; i < min(16, msg.arguments().length); i++) {
      rhoImag[row][i] = msg.get(i).floatValue();
    }
  }

  else if (addr.equals("/qmw/bloch/x")) {
    blochX = msg.get(0).floatValue();
  }

  else if (addr.equals("/qmw/bloch/y")) {
    blochY = msg.get(0).floatValue();
  }

  else if (addr.equals("/qmw/bloch/z")) {
    blochZ = msg.get(0).floatValue();
  }

  else if (addr.equals("/qmw/visual/field_strength")) {
    fieldStrength = msg.get(0).floatValue();
  }

  else if (addr.equals("/qmw/visual/field_acceleration")) {
    fieldAcceleration = msg.get(0).floatValue();
  }
}
