import processing.net.*;

import oscP5.*;
import netP5.*;

OscP5 oscP5;
NetAddress remoteLocation;

float[][] rhoReal = new float[16][16];
float[][] rhoImag = new float[16][16];

float[][] rhoMag = new float[16][16];
float[][] smoothRhoMag = new float[16][16];
float[][] rhoPhase = new float[16][16];

float blochX = 0.0;
float blochY = 0.0;
float blochZ = 0.0;

float smoothX = 0.0;
float smoothY = 0.0;
float smoothZ = 0.0;

ArrayList<PVector> directionTrail = new ArrayList<PVector>();
int maxTrailPoints = 140;

float fieldStrength = 0.0;
float fieldAcceleration = 0.0;

float smoothFieldStrength = 0.0;
float smoothFieldAcceleration = 0.0;


float sphereRadius = 210;

void setup() {
  size(1200, 800, P3D);
  smooth(8);

  // Must match the UDP port used by your Python OSC sender.
  oscP5 = new OscP5(this, 7401);

  textFont(createFont("Arial", 16));
}

void updateDensityDerivedValues() {
  for (int row = 0; row < 16; row++) {
    for (int col = 0; col < 16; col++) {
      float re = rhoReal[row][col];
      float im = rhoImag[row][col];

      rhoMag[row][col] = sqrt(re * re + im * im);
      rhoPhase[row][col] = atan2(im, re);

      smoothRhoMag[row][col] = lerp(
        smoothRhoMag[row][col],
        rhoMag[row][col],
        0.25
      );
    }
  }
}

void drawBasisRays() {
  float r = sphereRadius;

  strokeWeight(1.5);

  // X basis: |+> and |->
  stroke(235, 85, 85, 170);
  line(0, 0, 0,  r, 0, 0);   // +X  |+>
  line(0, 0, 0, -r, 0, 0);   // -X  |->

  // Y basis: |+i> and |-i>
  stroke(90, 220, 125, 170);
  line(0, 0, 0, 0, -r, 0);   // +Y  |+i>
  line(0, 0, 0, 0,  r, 0);   // -Y  |-i>

  // Z basis: |0> and |1>
  stroke(80, 150, 245, 190);
  line(0, 0, 0, 0, 0,  r);   // +Z  |0>
  line(0, 0, 0, 0, 0, -r);   // -Z  |1>

  // Endpoint dots: the six canonical basis states.
  noStroke();

  fill(235, 85, 85);
  pushMatrix();
  translate(r, 0, 0);
  sphere(6);
  popMatrix();

  pushMatrix();
  translate(-r, 0, 0);
  sphere(6);
  popMatrix();

  fill(90, 220, 125);
  pushMatrix();
  translate(0, -r, 0);
  sphere(6);
  popMatrix();

  pushMatrix();
  translate(0, r, 0);
  sphere(6);
  popMatrix();

  fill(80, 150, 245);
  pushMatrix();
  translate(0, 0, r);
  sphere(6);
  popMatrix();

  pushMatrix();
  translate(0, 0, -r);
  sphere(6);
  popMatrix();
}

void drawAxisLabel(String label, float x, float y, float z) {
  pushMatrix();
  translate(x, y, z);

  // Keep text facing the viewer enough to remain legible.
  rotateY(-0.50);
  rotateX(0.28);

  fill(220);
  noStroke();
  textAlign(CENTER, CENTER);
  textSize(15);
  text(label, 0, 0);

  popMatrix();
}

void drawHamiltonianComponents() {
  float scale = sphereRadius * 1.15;

  strokeWeight(10);

  // Pauli-X component
  stroke(230, 95, 95, 180);
  line(0, 0, 0, smoothX * scale, 0, 0);

  // Pauli-Y component
  stroke(95, 225, 145, 180);
  line(0, 0, 0, 0, -smoothY * scale, 0);

  // Pauli-Z component
  stroke(95, 150, 245, 180);
  line(0, 0, 0, 0, 0, smoothZ * scale);
}

void drawDensityPointCloud() {
  float spacing = 34;
  float gridSize = 15 * spacing;

  float originX = width * 0.5 - gridSize * 0.5;
  float originY = height * 0.5 - gridSize * 0.5;

  // Flat screen-space matrix: no camera transforms, no rotation.
  hint(DISABLE_DEPTH_TEST);

  // Faint matrix grid.
  stroke(55, 65, 82, 120);
  strokeWeight(1);

  for (int i = 0; i < 16; i++) {
    float p = i * spacing;

    line(originX + p, originY, originX + p, originY + gridSize);
    line(originX, originY + p, originX + gridSize, originY + p);
  }

  noStroke();

  for (int row = 0; row < 16; row++) {
    for (int col = 0; col < 16; col++) {
      float magnitude = smoothRhoMag[row][col];
      float phase = rhoPhase[row][col];

      float x = originX + col * spacing;
      float y = originY + row * spacing;

      float pointSize = constrain(
        3 + magnitude * 150.0,
        3,
        34
      );

      if (row == col) {
        // Diagonal = populations.
        fill(255, 215, 70, 240);
      } else {
        // Off-diagonals = coherences, phase-colored.
        colorMode(HSB, 255);
        float hue = map(phase, -PI, PI, 0, 255);
        fill(hue, 210, 255, 205);
        colorMode(RGB, 255);
      }

      ellipse(x, y, pointSize, pointSize);
    }
  }

  // Matrix title and axes.
  fill(220);
  textAlign(CENTER, CENTER);
  textSize(16);
  text("4-Qubit Density Matrix ρ", width * 0.5, originY - 38);

  textSize(11);
  fill(150);
  text("ket index j  →", width * 0.5, originY + gridSize + 32);

  pushMatrix();
  translate(originX - 42, height * 0.5);
  rotate(-HALF_PI);
  text("bra index i  →", 0, 0);
  popMatrix();

  hint(ENABLE_DEPTH_TEST);
}

String binaryKet(int value) {
  String bits = binary(value, 4);
  return "|" + bits + ">";
}

void draw() {
  background(8, 10, 15);

  updateDensityDerivedValues();
  drawDensityPointCloud();
}

void drawAxes() {
  float axisLength = sphereRadius * 1.3;

  strokeWeight(2);

  // Pauli-X
  stroke(220, 95, 95);
  line(-axisLength, 0, 0, axisLength, 0, 0);

  // Pauli-Y
  stroke(95, 215, 135);
  line(0, -axisLength, 0, 0, axisLength, 0);

  // Pauli-Z
  stroke(95, 145, 240);
  line(0, 0, -axisLength, 0, 0, axisLength);
}

void drawSphere() {
  pushMatrix();

  noFill();
  stroke(95, 108, 135, 120);
  strokeWeight(1);
  sphereDetail(42);
  sphere(sphereRadius);

  // Equator
  rotateX(HALF_PI);
  ellipse(0, 0, sphereRadius * 2, sphereRadius * 2);

  popMatrix();
}

void drawBlochVector() {
  float x = smoothX;
  float y = smoothY;
  float z = smoothZ;

  float magnitude = sqrt(x*x + y*y + z*z);
  float safeMagnitude = max(magnitude, 0.00001);

  float nx = x / safeMagnitude;
  float ny = y / safeMagnitude;
  float nz = z / safeMagnitude;

  float visualLength = constrain(
    magnitude * sphereRadius * 40.0,
    18,
    sphereRadius
  );

  float vx = nx * visualLength;
  float vy = -ny * visualLength;
  float vz = nz * visualLength;

  stroke(235, 235, 255);
  strokeWeight(4);
  line(0, 0, 0, vx, vy, vz);

  pushMatrix();
  translate(vx, vy, vz);
  noStroke();
  fill(245, 245, 255);
  sphere(9);
  popMatrix();

  // Direction-only projection onto sphere surface.
  pushMatrix();
  translate(
    nx * sphereRadius,
    -ny * sphereRadius,
    nz * sphereRadius
  );
  noStroke();
  fill(255, 165, 45);
  sphere(6);
  popMatrix();
  
  // Record normalized direction, independent of the short physical vector.
// Direction-only point: always placed just outside the sphere surface.
if (magnitude > 0.0001) {
  float markerRadius = sphereRadius * 1.035;

  hint(DISABLE_DEPTH_TEST);

  pushMatrix();
  translate(
    nx * markerRadius,
    -ny * markerRadius,
    nz * markerRadius
  );

  noStroke();
  fill(255, 145, 25);
  sphere(13);
  popMatrix();

  hint(ENABLE_DEPTH_TEST);
}
}

void drawDirectionTrail() {
  if (directionTrail.size() < 2) {
    return;
  }

  noFill();
  strokeWeight(2);

  beginShape();

  for (int i = 0; i < directionTrail.size(); i++) {
    PVector p = directionTrail.get(i);

    float alpha = map(
      i,
      0,
      directionTrail.size() - 1,
      8,
      180
    );

    stroke(255, 165, 45, alpha);
    vertex(p.x, p.y, p.z);
  }

  endShape();
}
void drawHUD() {
  hint(DISABLE_DEPTH_TEST);

  camera();

  fill(235);
  textSize(21);
  text("BLOCH VECTOR", 28, 42);
  text("Current local-state orientation", 28, 67);
  fill(165, 180, 205);
  textSize(14);
  text("H = Xσx + Yσy + Zσz", 28, 67);
  
  fill(255, 120, 120);
text(
  "RAW X / Y / Z: " +
  nf(smoothX, 1, 4) + "   " +
  nf(smoothY, 1, 4) + "   " +
  nf(smoothZ, 1, 4),
  28,
  230
);

  text(
    "Pauli-X drive: " + nf(smoothX, 1, 3),
    28,
    112
  );

  text(
    "Pauli-Y drive: " + nf(smoothY, 1, 3),
    28,
    136
  );

  text(
    "Pauli-Z drive: " + nf(smoothZ, 1, 3),
    28,
    160
  );

  float strength = sqrt(
    smoothX * smoothX +
    smoothY * smoothY +
    smoothZ * smoothZ
  );

  fill(255, 222, 125);
  text(
    "Field strength: " + nf(strength, 1, 3),
    28,
    196
  );

  fill(145, 160, 185);
  textSize(12);
  text(
    "OSC: /qmw/hamiltonian/pauli_x  /pauli_y  /pauli_z",
    28,
    height - 30
  );

  hint(ENABLE_DEPTH_TEST);
}

void oscEvent(OscMessage message) {
  String address = message.addrPattern();

  if (address.startsWith("/qmw/density/real/")) {
    int row = int(
      address.substring("/qmw/density/real/".length())
    );

    if (row >= 0 && row < 16 && message.arguments().length >= 16) {
      for (int col = 0; col < 16; col++) {
        rhoReal[row][col] = message.get(col).floatValue();
      }
    }
    return;
  }

  if (address.startsWith("/qmw/density/imag/")) {
    int row = int(
      address.substring("/qmw/density/imag/".length())
    );

    if (row >= 0 && row < 16 && message.arguments().length >= 16) {
      for (int col = 0; col < 16; col++) {
        rhoImag[row][col] = message.get(col).floatValue();
      }
    }
    return;
  }

  if (message.arguments().length < 1) {
    return;
  }

  float value = message.get(0).floatValue();

  if (address.equals("/qmw/bloch/x")) {
    blochX = value;
  } else if (address.equals("/qmw/bloch/y")) {
    blochY = value;
  } else if (address.equals("/qmw/bloch/z")) {
    blochZ = value;
  }
}
