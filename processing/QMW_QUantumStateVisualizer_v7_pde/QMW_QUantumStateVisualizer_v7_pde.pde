import oscP5.*;
import netP5.*;
import processing.event.*;

OscP5 oscP5;

int N = 256;
int HISTORY = 140;
int SCOPE_HISTORY = 900;
int SIGNAL_COUNT = 16;
int displayMode = 12;
int densityDisplayMode = 0;
// 0 = full matrix
// 1 = coherence-only
// 2 = diagonal/populations
// 3 = phase-only
// 4 = tensor field

int tensorRenderMode = 0;

// 0 = streamlines
// 1 = particles
// 2 = both

float[][] probabilityHistory = new float[HISTORY][N];
float[][] phaseHistory = new float[HISTORY][N];
float[][] realHistory = new float[HISTORY][N];
float[][] imagHistory = new float[HISTORY][N];
float[][] spectrumHistory = new float[HISTORY][N];
float[][] spectrumPhaseHistory = new float[HISTORY][N];
float[] realPsi = new float[N];
float[] imagPsi = new float[N];

float[][] rhoReal = new float[16][16];
float[][] rhoImag = new float[16][16];

float[] densityEigenvalues = new float[16];
float[][] eigenReal = new float[16][16];
float[][] eigenImag = new float[16][16];

int densityEigenMode = 0;

int writeIndex = 0;
boolean hasWavepacket = false;
boolean hasWavefunction = false;
boolean hasSpectrum = false;
boolean hasDensity = false;
boolean sourceWavepacketAvailable = false;

float rotX = -0.95;
float rotY = 0.55;
float zoom = 0.86;
float heightScale = 520.0;
int waveWindow = 112;
boolean followPacket = true;

float blochX = 0;
float blochY = 0;
float blochZ = 0;
float perturbedBlochX = 0;
float perturbedBlochY = 0;
float perturbedBlochZ = 0;

float fieldStrength = 0;
float fieldAcceleration = 0;
float densityDeltaMax = 0;
float densityDeltaMean = 0;

float[][] qubitBloch = new float[4][3];
float[][] spinBloch = new float[4][3];
float[] spinLength = new float[4];
float[] spinPhase = new float[4];
float[] spinPurity = new float[4];
float[] spinEntropy = new float[4];
float[] spinSpeed = new float[4];
float[][][] spinTrail = new float[4][SCOPE_HISTORY][3];
int[] spinTrailCount = new int[4];
int[] spinTrailWriteIndex = new int[4];
float[][] pairSpinXXYYZZ = new float[6][3];
boolean hasSpin = false;

float bohmX = 0;
float bohmVelocity = 0;
float bohmSpeed = 0;
float bohmPhase = 0;
float bohmDensity = 0;
float bohmNodeProximity = 0;
float bohmCurvature = 0;
float bohmFieldVelocity = 0;

float[] scopeXHistory = new float[SCOPE_HISTORY];
float[] scopeYHistory = new float[SCOPE_HISTORY];
float[] scopeZHistory = new float[SCOPE_HISTORY];
int scopeWriteIndex = 0;
float scopeX = 0;
float scopeY = 0;
float scopeZ = 0;
boolean hasScopeInput = false;
int lastScopeInputMs = -100000;

float[][] signalHistory = new float[SIGNAL_COUNT][SCOPE_HISTORY];
String[] signalNames = {
  "Q0 Bloch X", "Q0 Bloch Y", "Q0 Bloch Z",
  "Q1 Bloch X", "Q1 Bloch Y", "Q1 Bloch Z",
  "Q2 Bloch X", "Q2 Bloch Y", "Q2 Bloch Z",
  "Q3 Bloch X", "Q3 Bloch Y", "Q3 Bloch Z",
  "Purity", "Coherence", "Entropy", "Entangle"
};
int signalWriteIndex = 0;
float purity = 0;
float coherence = 0;
float entropy = 0;
float entanglement = 0;
float hamiltonianX = 0;
float hamiltonianY = 0;
float hamiltonianZ = 0;

void setup() {
  size(1280, 820, P3D);
  colorMode(HSB, 1.0);
  frameRate(60);
  oscP5 = new OscP5(this, 7401);
  textFont(createFont("Menlo", 12));
}

void draw() {
  background(0);
  lights();
  drawHeader();
  sampleScopeInput();
  sampleSignalInputs();
  boolean waveModeUnavailable = displayMode >= 2 && displayMode <= 6 && !sourceWavepacketAvailable;

  if (displayMode == 1) {
    drawDensityMatrix();
  } else if (waveModeUnavailable) {
    drawUnavailableWaveScope();
  } else if (displayMode == 2) {
    drawWavefunctionWaterfall();
  } else if (displayMode == 3) {
    drawComplexWavefunctionCurve();
  } else if (displayMode == 4) {
    drawProbabilityCurve();
  } else if (displayMode == 5) {
    drawPhaseCurve();
  } else if (displayMode == 6) {
    drawSpectrumTerrain();
  } else if (displayMode == 7) {
    drawSignalStripChart();
  } else if (displayMode == 8) {
    drawStateTrajectoryScope();
  } else if (displayMode == 9) {
    drawLissajousScope();
  } else if (displayMode == 10) {
    drawWaveformFrequencyView();
  }
  else if (displayMode == 11) {
  drawFourBlochSpheres();
  }
  else if (displayMode == 12) {
    drawSpinMode();
  }
  else if (displayMode == 13) {
    drawGyroscopeMode();
  }

  if (displayMode >= 7 || waveModeUnavailable) {
    drawHeader();
  }
  if (displayMode < 7 && !waveModeUnavailable) {
    drawTelemetryPanel();
  }
  drawFooter();
}

void drawHeader() {
  hint(DISABLE_DEPTH_TEST);
  camera();
  fill(0, 0, 1);
  text("QMW Quantum Oscilloscope", 24, 26);
  text("UDP 7401  |  a density (m % full, coherence, phase, diag )  |  wavepacket: b |ψ|²  c complex ψ  d probability  e phase  s spectrum", 24, 46);
  text("signal scopes: g strip chart  h XYZ trace  i XY scope  j waveform/frequency  k qubit vectors  l spin mode  y gyroscope", 24, 66);
  text("drag/arrows = rotate   +/-/wheel = zoom   [ ] = height   { } = window   f = follow   0 = reset", 24, 86);
  text("Tensor field:  T = Streamlines / Particles / Both",24,118);
  hint(ENABLE_DEPTH_TEST);
}

void drawFooter() {
  hint(DISABLE_DEPTH_TEST);
  camera();
  fill(hasDensity ? color(0.34, 0.8, 1.0) : color(0.05, 0.9, 1.0));
  text(hasDensity ? "density stream active" : "waiting for /qmw/density/real/*", 24, height - 38);
  fill(hasWavepacket ? color(0.58, 0.8, 1.0) : color(0.05, 0.9, 1.0));
  text(sourceWavepacketAvailable ? "wavepacket stream active" : "wavepacket stream unavailable", 24, height - 20);
  hint(ENABLE_DEPTH_TEST);
}

void drawDensityTensorParticles() {

  float spacing = 34.0;
  float origin = -7.5 * spacing;
  float stepSize = 10.0;
  int steps = 32;

  noStroke();

  for (int seedR = 1; seedR < 15; seedR += 2) {
    for (int seedC = 1; seedC < 15; seedC += 2) {

      if (densityMagAt(seedR, seedC) < 0.008) continue;

      float x = origin + seedC * spacing;
      float z = origin + seedR * spacing;

      float prevAngle = tensorAngleAt(seedR, seedC);

      for (int k = 0; k < steps; k++) {

        float gc = (x - origin) / spacing;
        float gr = (z - origin) / spacing;

        if (gc < 0.5 || gc > 14.5 || gr < 0.5 || gr > 14.5)
          break;

        int r = constrain(round(gr),0,15);
        int c = constrain(round(gc),0,15);

        float mag = densityMagAt(r,c);
        float phase = densityPhaseAt(r,c);
        float angle = tensorAngleAt(r,c);

        if (abs(angle-prevAngle) > HALF_PI)
          angle += PI;

        prevAngle = angle;

        float y = -mag*210;

        float hue = map(phase,-PI,PI,0,1);
        float bright = constrain(0.25+mag*10.0,0,1);

        pushMatrix();
        translate(x,y,z);
        fill(hue,0.8,bright,0.65);
        stroke(hue,0.8,bright,0.9);
        strokeWeight(2.5 + mag*5.0);
        point(x,y,z);
        popMatrix();

        x += cos(angle)*stepSize;
        z += sin(angle)*stepSize;
      }
    }
  }
}

void drawUnavailableWaveScope() {
  drawLissajousScope();
  hint(DISABLE_DEPTH_TEST);
  camera();
  fill(0.06, 0.85, 1.0);
  text(
    "selected mode needs real wavepacket data; showing live signal scope instead",
    24,
    108
  );
  hint(ENABLE_DEPTH_TEST);
}

void drawDensityMatrix() {
  if (densityDisplayMode == 4) {
    drawDensityTensorField();
  } else {
    drawDensityMatrix3D(densityDisplayMode);
  }
}

void drawDensityTensorField() {
  pushMatrix();
  translate(width * 0.38, height * 0.55, 0);
  scale(zoom);
  rotateX(rotX);
  rotateY(rotY);
  rotateZ(-0.18);

  float spacing = 34.0;
  float origin = -7.5 * spacing;
  float glyphScale = 42.0;

  strokeWeight(1.2);

  for (int r = 0; r < 16; r++) {
    for (int c = 0; c < 16; c++) {
      float re = rhoReal[r][c];
      float im = rhoImag[r][c];
      float mag = sqrt(re * re + im * im);
      float phase = atan2(im, re);

      float a = re;
      float b = im;
      float d = mag;

      float trace = a + d;
      float det = a * d - b * b;
      float disc = sqrt(max(0.0, (a - d) * (a - d) + 4.0 * b * b));

      float lambda1 = 0.5 * (trace + disc);
      float lambda2 = 0.5 * (trace - disc);

      float angle = 0.5 * atan2(2.0 * b, a - d);

      float x = origin + c * spacing;
      float z = origin + r * spacing;
      float y = -mag * 240.0;

      float hue;
      if (det < 0.0) {
        hue = 0.02;       // saddle
      } else if (abs(phase) > PI * 0.55) {
        hue = 0.78;       // focus-like phase rotation
      } else {
        hue = 0.55;       // center / coherent field
      }

      float brightness = constrain(0.18 + mag * 12.0, 0.0, 1.0);
      float len1 = constrain(abs(lambda1) * glyphScale * 8.0, 2.0, spacing * 0.80);
      float len2 = constrain(abs(lambda2) * glyphScale * 8.0, 1.0, spacing * 0.45);


      /*
      pushMatrix();
      translate(x, y, z);
      rotateY(angle);

      stroke(hue, 0.85, brightness, 0.85);
      line(-len1, 0, 0, len1, 0, 0);

      stroke(hue, 0.45, brightness, 0.45);
      line(0, 0, -len2, 0, 0, len2);
      

      popMatrix();

      if (mag > 0.035) {
        stroke(hue, 0.75, brightness, 0.22);
        line(x, 0, z, x, y, z);
      }
      */
    }
  }
  
  if (tensorRenderMode == 0) {
    drawDensityTensorStreamlines();
}
else if (tensorRenderMode == 1) {
    drawDensityTensorParticles();
}
else {
    drawDensityTensorStreamlines();
    drawDensityTensorParticles();
}

  popMatrix();

  hint(DISABLE_DEPTH_TEST);
  camera();
  fill(0, 0, 1);
  text("Density tensor field topology  |  red=saddle  blue=center/coherence  violet=focus-like phase", 24, 112);
  hint(ENABLE_DEPTH_TEST);
}

void drawDensityTensorStreamlines() {
  float spacing = 34.0;
  float origin = -7.5 * spacing;
  float stepSize = 13.0;
  int steps = 22;

  strokeWeight(1.4);
  noFill();

  for (int seedR = 1; seedR < 15; seedR += 2) {
    for (int seedC = 1; seedC < 15; seedC += 2) {
      float seedMag = densityMagAt(seedR, seedC);
      if (seedMag < 0.008) continue;

      float x = origin + seedC * spacing;
      float z = origin + seedR * spacing;

      float phase = densityPhaseAt(seedR, seedC);
      float hue = map(phase, -PI, PI, 0.0, 1.0);
      float bright = constrain(0.22 + seedMag * 10.0, 0.0, 1.0);

      stroke(hue, 0.78, bright, 0.58);

      beginShape();
      curveVertex(x, -seedMag * 210.0, z);
      curveVertex(x, -seedMag * 210.0, z);

      float prevAngle = tensorAngleAt(seedR, seedC);

      for (int k = 0; k < steps; k++) {
        float gc = (x - origin) / spacing;
        float gr = (z - origin) / spacing;

        if (gr < 0.5 || gr > 14.5 || gc < 0.5 || gc > 14.5) {
          break;
        }

        int r = constrain(round(gr), 0, 15);
        int c = constrain(round(gc), 0, 15);

        float angle = tensorAngleAt(r, c);

        // Resolve 180-degree eigenvector ambiguity for smooth flow.
        if (abs(angle - prevAngle) > HALF_PI) {
          angle += PI;
        }
        prevAngle = angle;

        float mag = densityMagAt(r, c);
        float y = -mag * 210.0;

        x += cos(angle) * stepSize;
        z += sin(angle) * stepSize;

        curveVertex(x, y, z);
      }

      curveVertex(x, 0, z);
      endShape();
    }
  }
}

float densityMagAt(int r, int c) {
  float re = rhoReal[r][c];
  float im = rhoImag[r][c];
  return sqrt(re * re + im * im);
}

float densityPhaseAt(int r, int c) {
  return atan2(rhoImag[r][c], rhoReal[r][c]);
}

float tensorAngleAt(int r, int c) {
  float re = rhoReal[r][c];
  float im = rhoImag[r][c];
  float mag = sqrt(re * re + im * im);

  float a = re;
  float b = im;
  float d = mag;

  return 0.5 * atan2(2.0 * b, a - d);
}


void drawDensityMatrix3D(int mode) {
  pushMatrix();
  translate(width * 0.32, height * 0.52, 0);
  scale(zoom);
  rotateX(rotX);
  rotateY(rotY);
  rotateZ(-0.18);

  float cell = 30.0;
  float origin = -8 * cell;

  noStroke();

  for (int r = 0; r < 16; r++) {
    for (int c = 0; c < 16; c++) {
      float re = rhoReal[r][c];
      float im = rhoImag[r][c];
      float mag = sqrt(re * re + im * im);
      float phase = atan2(im, re);

      if (mode == 1 && r == c) {
        mag = 0.0;        // coherence-only
      }

      if (mode == 2 && r != c) {
        mag = 0.0;        // diagonal-only
      }

      if (mode == 3) {
        mag = 0.08;       // phase-only flat field
      }

      float h = map(phase, -PI, PI, 0, 1);
      float b = constrain(mag * 16.0, 0.08, 1.0);
      float z = mag * 420.0;

      pushMatrix();
      translate(origin + c * cell, origin + r * cell, z * 0.5);
      fill(h, 0.82, b);
      box(cell * 0.86, cell * 0.86, max(2.0, z));
      popMatrix();
    }
  }

  stroke(0, 0, 0.45);
  noFill();
  rect(origin - cell * 0.5, origin - cell * 0.5, cell * 16, cell * 16);

  popMatrix();
}

void drawDensityEigenMode() {
  pushMatrix();
  translate(width * 0.36, height * 0.55, 0);
  scale(zoom);
  rotateX(rotX);
  rotateY(rotY);
  rotateZ(-0.18);

  float spacing = 70.0;
  float origin = -1.5 * spacing;
  float ampScale = 520.0;

  int mode = densityEigenMode;
  float lambda = densityEigenvalues[mode];

  noStroke();

  for (int i = 0; i < 16; i++) {
    int row = i / 4;
    int col = i % 4;

    float re = eigenReal[mode][i];
    float im = eigenImag[mode][i];

    float amp = sqrt(re * re + im * im);
    float phase = atan2(im, re);

    float x = origin + col * spacing;
    float z = origin + row * spacing;
    float y = -amp * ampScale;

    float hue = map(phase, -PI, PI, 0.0, 1.0);
    float bright = constrain(0.15 + amp * 4.0 + lambda * 0.5, 0.0, 1.0);

    pushMatrix();
    translate(x, y, z);
    fill(hue, 0.85, bright);
    sphere(10 + amp * 34.0);
    popMatrix();

    stroke(hue, 0.70, bright, 0.65);
    strokeWeight(1.0 + amp * 3.0);
    line(x, 0, z, x, y, z);
    noStroke();
  }

  drawEigenModeGrid(spacing, origin);

  popMatrix();

  hint(DISABLE_DEPTH_TEST);
  camera();
  fill(0, 0, 1);
  text(
    "Density eigenmode " + densityEigenMode
      + "   λ = " + nf(lambda, 1, 5)
      + "   press n to cycle modes",
    24,
    112
  );
  hint(ENABLE_DEPTH_TEST);
}

void drawEigenModeGrid(float spacing, float origin) {
  stroke(0, 0, 0.32, 0.75);
  strokeWeight(1);
  noFill();

  for (int r = 0; r < 4; r++) {
    line(origin, 0, origin + r * spacing,
         origin + 3 * spacing, 0, origin + r * spacing);
  }

  for (int c = 0; c < 4; c++) {
    line(origin + c * spacing, 0, origin,
         origin + c * spacing, 0, origin + 3 * spacing);
  }
}




void drawWavefunctionWaterfall() {
  pushMatrix();
  translate(width * 0.44, height * 0.56, 0);
  scale(zoom);
  rotateX(rotX);
  rotateY(rotY);

  int xStep = 2;
  float xScale = 6.4;
  float tScale = 5.0;

  noStroke();
  for (int h = 0; h < HISTORY - 1; h++) {
    int rowA = historyIndex(h);
    int rowB = historyIndex(h + 1);
    int peakA = followPacket ? wavepacketPeakIndex(rowA) : N / 2;
    int peakB = followPacket ? wavepacketPeakIndex(rowB) : N / 2;
    beginShape(TRIANGLE_STRIP);
    for (int j = 0; j < waveWindow; j += xStep) {
      waterfallVertex(rowA, h, focusedSampleIndex(peakA, j), j, xScale, tScale);
      waterfallVertex(rowB, h + 1, focusedSampleIndex(peakB, j), j, xScale, tScale);
    }
    endShape();
  }

  drawWaterfallGrid(xScale, tScale);
  popMatrix();
}

void waterfallVertex(int row, int h, int i, int j, float xScale, float tScale) {
  float p = probabilityHistory[row][i];
  float ph = phaseHistory[row][i];
  float x = (j - waveWindow / 2.0) * xScale;
  float y = -p * heightScale;
  float z = (h - HISTORY / 2.0) * tScale;
  float hue = map(ph, -PI, PI, 0.0, 1.0);
  float bright = constrain(0.16 + p * 12.0, 0.0, 1.0);
  fill(hue, 0.78, bright);
  vertex(x, y, z);
}

void wavepacketSurfaceVertex(int row, int h, int i, int j, float xScale, float tScale, int surfaceMode) {
  float p = probabilityHistory[row][i];
  float re = realHistory[row][i];
  float im = imagHistory[row][i];
  float amp = sqrt(max(0.0, re * re + im * im));
  float ph = phaseHistory[row][i];
  float x = (j - waveWindow / 2.0) * xScale;
  float z = (h - HISTORY / 2.0) * tScale;
  float y = 0.0;
  float hue = map(ph, -PI, PI, 0.0, 1.0);
  float sat = 0.78;
  float bright = constrain(0.18 + p * 12.0 + amp * 0.8, 0.0, 1.0);

  if (surfaceMode == 3) {
    y = -amp * 380.0;
    bright = constrain(0.20 + amp * 3.5, 0.0, 1.0);
    sat = 0.92;
  } else if (surfaceMode == 4) {
    y = -p * heightScale;
    hue = 0.55 + constrain(p * 1.7, 0.0, 0.22);
    sat = 0.70;
    bright = constrain(0.12 + p * 13.0, 0.0, 1.0);
  } else if (surfaceMode == 5) {
    float phaseWave = sin(ph);
    y = -p * heightScale * 0.40 - phaseWave * 150.0;
    sat = 0.95;
    bright = constrain(0.35 + abs(phaseWave) * 0.5 + p * 2.0, 0.0, 1.0);
  } else {
    y = -p * heightScale;
  }

  fill(hue, sat, bright);
  vertex(x, y, z);
}

void drawWavepacketSurface(int surfaceMode) {
  pushMatrix();
  translate(width * 0.44, height * 0.57, 0);
  scale(zoom);
  rotateX(rotX);
  rotateY(rotY);

  int xStep = 2;
  float xScale = 6.4;
  float tScale = 5.0;

  noStroke();
  for (int h = 0; h < HISTORY - 1; h++) {
    int rowA = historyIndex(h);
    int rowB = historyIndex(h + 1);
    int peakA = followPacket ? wavepacketPeakIndex(rowA) : N / 2;
    int peakB = followPacket ? wavepacketPeakIndex(rowB) : N / 2;
    beginShape(TRIANGLE_STRIP);
    for (int j = 0; j < waveWindow; j += xStep) {
      wavepacketSurfaceVertex(rowA, h, focusedSampleIndex(peakA, j), j, xScale, tScale, surfaceMode);
      wavepacketSurfaceVertex(rowB, h + 1, focusedSampleIndex(peakB, j), j, xScale, tScale, surfaceMode);
    }
    endShape();
  }

  drawWaterfallGrid(xScale, tScale);
  popMatrix();
}

int wavepacketPeakIndex(int row) {
  int peak = 0;
  float peakValue = probabilityHistory[row][0];
  for (int i = 1; i < N; i++) {
    if (probabilityHistory[row][i] > peakValue) {
      peakValue = probabilityHistory[row][i];
      peak = i;
    }
  }
  return peak;
}

int focusedSampleIndex(int peak, int j) {
  int offset = j - waveWindow / 2;
  int idx = peak + offset;
  while (idx < 0) idx += N;
  return idx % N;
}

void drawWaterfallGrid(float xScale, float tScale) {
  stroke(0, 0, 0.28, 0.65);
  strokeWeight(1);
  noFill();
  float xMin = -waveWindow / 2.0 * xScale;
  float xMax = waveWindow / 2.0 * xScale;
  float zMin = -HISTORY / 2.0 * tScale;
  float zMax = HISTORY / 2.0 * tScale;
  for (int g = -4; g <= 4; g++) {
    float x = map(g, -4, 4, xMin, xMax);
    line(x, 0, zMin, x, 0, zMax);
  }
  for (int g = -6; g <= 6; g++) {
    float z = map(g, -6, 6, zMin, zMax);
    line(xMin, 0, z, xMax, 0, z);
  }
}

void drawComplexWavefunctionCurve() {
  drawWavepacketSurface(3);
}

void drawProbabilityCurve() {
  drawWavepacketSurface(4);
}

void drawPhaseCurve() {
  drawWavepacketSurface(5);
}

void drawSpectrumTerrain() {
  pushMatrix();
  translate(width * 0.44, height * 0.57, 0);
  scale(zoom);
  rotateX(rotX);
  rotateY(rotY);

  int xStep = 2;
  float xScale = 5.0;
  float tScale = 5.0;
  int spectrumWindow = 150;

  noStroke();
  for (int h = 0; h < HISTORY - 1; h++) {
    int rowA = historyIndex(h);
    int rowB = historyIndex(h + 1);
    beginShape(TRIANGLE_STRIP);
    for (int j = 0; j < spectrumWindow; j += xStep) {
      int i = centeredSpectrumIndex(j, spectrumWindow);
      spectrumVertex(rowA, h, i, j, spectrumWindow, xScale, tScale);
      spectrumVertex(rowB, h + 1, i, j, spectrumWindow, xScale, tScale);
    }
    endShape();
  }

  drawSpectrumGrid(spectrumWindow, xScale, tScale);
  popMatrix();
}

void spectrumVertex(int row, int h, int i, int j, int spectrumWindow, float xScale, float tScale) {
  float power = constrain(spectrumHistory[row][i], 0.0, 1.0);
  float phase = spectrumPhaseHistory[row][i];
  float x = (j - spectrumWindow / 2.0) * xScale;
  float liftedPower = pow(power, 0.34);
  float phaseRipple = sin(phase + h * 0.08) * liftedPower * 110.0;
  float y = -liftedPower * heightScale * 0.82 + phaseRipple;
  float z = (h - HISTORY / 2.0) * tScale + cos(phase) * liftedPower * 42.0;
  float centerPull = 1.0 - abs(j - spectrumWindow / 2.0) / (spectrumWindow / 2.0);
  float hue = map(phase, -PI, PI, 0.0, 1.0) + 0.10 * centerPull;
  hue = hue - floor(hue);
  float bright = constrain(0.16 + liftedPower * 1.05, 0.0, 1.0);
  fill(hue, 0.90, bright);
  vertex(x, y, z);
}

int centeredSpectrumIndex(int j, int spectrumWindow) {
  int start = N / 2 - spectrumWindow / 2;
  int idx = start + j;
  return constrain(idx, 0, N - 1);
}

void drawSpectrumGrid(int spectrumWindow, float xScale, float tScale) {
  stroke(0, 0, 0.28, 0.65);
  strokeWeight(1);
  noFill();
  float xMin = -spectrumWindow / 2.0 * xScale;
  float xMax = spectrumWindow / 2.0 * xScale;
  float zMin = -HISTORY / 2.0 * tScale;
  float zMax = HISTORY / 2.0 * tScale;
  for (int g = -5; g <= 5; g++) {
    float x = map(g, -5, 5, xMin, xMax);
    line(x, 0, zMin, x, 0, zMax);
  }
  for (int g = -6; g <= 6; g++) {
    float z = map(g, -6, 6, zMin, zMax);
    line(xMin, 0, z, xMax, 0, z);
  }
}

void sampleSignalInputs() {
  int s = 0;

  for (int q = 0; q < 4; q++) {
    signalHistory[s++][signalWriteIndex] = qubitBloch[q][0];
    signalHistory[s++][signalWriteIndex] = qubitBloch[q][1];
    signalHistory[s++][signalWriteIndex] = qubitBloch[q][2];
  }

  signalHistory[s++][signalWriteIndex] = purity;
  signalHistory[s++][signalWriteIndex] = coherence;
  signalHistory[s++][signalWriteIndex] = entropy;
  signalHistory[s++][signalWriteIndex] = entanglement;

  signalWriteIndex = (signalWriteIndex + 1) % SCOPE_HISTORY;
}

void drawSignalStripChart() {
  hint(DISABLE_DEPTH_TEST);
  camera();
  noLights();

  float left = 150;
  float right = width - 90;
  float top = 124;
  float rowH = (height - 198) / float(SIGNAL_COUNT);
  float graphW = right - left;

  fill(0, 0, 1);
  text("Real-data scalar strip chart", 24, 104);

  for (int s = 0; s < SIGNAL_COUNT; s++) {
    float cy = top + s * rowH + rowH * 0.5;
    float lo = signalMin(s);
    float hi = signalMax(s);
    float span = hi - lo;
    if (span < 0.0001) {
      lo -= 0.5;
      hi += 0.5;
      span = hi - lo;
    }

    stroke(0, 0, 0.22, 0.80);
    strokeWeight(1);
    line(left, cy, right, cy);
    line(left, cy - rowH * 0.34, right, cy - rowH * 0.34);
    line(left, cy + rowH * 0.34, right, cy + rowH * 0.34);

    noFill();
    float hue = (0.56 + s * 0.075) % 1.0;
    stroke(hue, 0.78, 0.95, 0.92);
    strokeWeight(1.8);
    beginShape();
    for (int i = 0; i < SCOPE_HISTORY; i++) {
      int idx = (signalWriteIndex + i) % SCOPE_HISTORY;
      float x = left + i * graphW / float(SCOPE_HISTORY - 1);
      float norm = (signalHistory[s][idx] - lo) / span;
      float y = cy + rowH * 0.34 - norm * rowH * 0.68;
      vertex(x, y);
    }
    endShape();

    int latest = (signalWriteIndex + SCOPE_HISTORY - 1) % SCOPE_HISTORY;
    fill(0, 0, 1);
    text(signalNames[s], 24, cy - 4);
    text(
      "now " + nf(signalHistory[s][latest], 1, 5)
        + "   min " + nf(lo, 1, 5)
        + "   max " + nf(hi, 1, 5),
      right - 280,
      cy - 4
    );
  }

  hint(ENABLE_DEPTH_TEST);
  lights();
}

float signalMin(int signalIndex) {
  float m = signalHistory[signalIndex][0];
  for (int i = 1; i < SCOPE_HISTORY; i++) {
    m = min(m, signalHistory[signalIndex][i]);
  }
  return m;
}

float signalMax(int signalIndex) {
  float m = signalHistory[signalIndex][0];
  for (int i = 1; i < SCOPE_HISTORY; i++) {
    m = max(m, signalHistory[signalIndex][i]);
  }
  return m;
}

void drawWaveformFrequencyView() {
  hint(DISABLE_DEPTH_TEST);
  camera();
  noLights();

  int[] channels = {
  0, 1, 2,
  3, 4, 5,
  6, 7, 8,
  9, 10, 11,
  12, 13, 14, 15
};
  int rowCount = channels.length;
  int dftSamples = 256;
  int bins = 48;
  float left = 74;
  float split = width * 0.50;
  float right = width - 58;
  float top = 126;
  float rowH = (height - 198) / float(rowCount);

  fill(0, 0, 1);
  text("Time-domain waveform and 2D frequency view", 24, 106);
  text("frequency plot uses the live signal history, Hann window, mean removed", split + 22, 106);

  for (int r = 0; r < rowCount; r++) {
    int channel = channels[r];
    float rowTop = top + r * rowH;
    float rowBottom = rowTop + rowH - 16;
    float cy = (rowTop + rowBottom) * 0.5;
    drawWaveformPanel(channel, left, rowTop, split - 28, rowBottom);
    drawFrequencyPanel(channel, split + 22, rowTop, right, rowBottom, dftSamples, bins);

    fill(0, 0, 1);
    text(signalNames[channel], 24, cy + 4);
  }

  hint(ENABLE_DEPTH_TEST);
  lights();
}

void drawWaveformPanel(int channel, float left, float top, float right, float bottom) {
  float lo = signalMin(channel);
  float hi = signalMax(channel);
  float span = hi - lo;
  if (span < 0.0001) {
    lo -= 0.5;
    hi += 0.5;
    span = hi - lo;
  }

  drawPanelGrid(left, top, right, bottom);
  float centerY = (top + bottom) * 0.5;
  stroke(0, 0, 0.36, 0.88);
  line(left, centerY, right, centerY);

  noFill();
  stroke((0.56 + channel * 0.075) % 1.0, 0.80, 0.96, 0.95);
  strokeWeight(1.6);
  beginShape();
  for (int i = 0; i < SCOPE_HISTORY; i++) {
    int idx = (signalWriteIndex + i) % SCOPE_HISTORY;
    float x = map(i, 0, SCOPE_HISTORY - 1, left, right);
    float norm = (signalHistory[channel][idx] - lo) / span;
    float y = bottom - norm * (bottom - top);
    vertex(x, y);
  }
  endShape();

  int latest = (signalWriteIndex + SCOPE_HISTORY - 1) % SCOPE_HISTORY;
  fill(0, 0, 0.92);
  text(
    "time  now " + nf(signalHistory[channel][latest], 1, 5)
      + "  min " + nf(lo, 1, 5)
      + "  max " + nf(hi, 1, 5),
    left,
    bottom + 13
  );
}

void drawFourBlochSpheres() {
  hint(DISABLE_DEPTH_TEST);
  camera();
  noLights();

  fill(0, 0, 1);
  text("Four-qubit Bloch spheres", 24, 108);
  text("q0 q1 q2 q3 reduced one-qubit states", 24, 128);

  float r = 92;
  float startX = 210;
  float y = height * 0.52;
  float gap = 250;

  for (int q = 0; q < 4; q++) {
    drawSingleBlochSphere(
      startX + q * gap,
      y,
      r,
      qubitBloch[q][0],
      qubitBloch[q][1],
      qubitBloch[q][2],
      "q" + q
    );
  }

  lights();
  hint(ENABLE_DEPTH_TEST);
}

void drawSingleBlochSphere(
  float cx,
  float cy,
  float r,
  float x,
  float y,
  float z,
  String label
) {
  stroke(0, 0, 0.35);
  strokeWeight(1);
  noFill();

  ellipse(cx, cy, r * 2, r * 2);
  line(cx - r, cy, cx + r, cy);
  line(cx, cy - r, cx, cy + r);

  float vx = constrain(x, -1, 1) * r;
  float vy = -constrain(y, -1, 1) * r;

  stroke(0.58, 0.85, 1.0);
  strokeWeight(3);
  line(cx, cy, cx + vx, cy + vy);

  noStroke();
  fill(0.58, 0.85, 1.0);
  ellipse(cx + vx, cy + vy, 10, 10);

  fill(0, 0, 1);
  text(label, cx - 12, cy - r - 22);
  text("x " + nf(x, 1, 3), cx - 42, cy + r + 24);
  text("y " + nf(y, 1, 3), cx - 42, cy + r + 42);
  text("z " + nf(z, 1, 3), cx - 42, cy + r + 60);
}

void drawSpinMode() {
  hint(DISABLE_DEPTH_TEST);
  camera();
  noLights();

  fill(0, 0, 1);
  text("Live spin mode", 92, 134);
  text(hasSpin ? "density-derived /qmw/spin stream active" : "waiting for /qmw/spin/q*/bloch", 92, 154);
  text("XZ projection, hue/size shows Y depth, trail shows live motion", 92, 174);

  float panelW = width * 0.405;
  float panelH = 225;
  float left = 92;
  float top = 205;
  float gapX = 52;
  float gapY = 258;
  float rightLeft = left + panelW + gapX;
  drawSpinPanel(0, left, top, panelW, panelH);
  drawSpinPanel(1, rightLeft, top, panelW, panelH);
  drawSpinPanel(2, left, top + gapY, panelW, panelH);
  drawSpinPanel(3, rightLeft, top + gapY, panelW, panelH);

  lights();
  hint(ENABLE_DEPTH_TEST);
}

void drawSpinPanel(int q, float left, float top, float w, float h) {
  fill(0, 0, 0.08, 0.72);
  noStroke();
  rect(left, top, w, h, 8);

  float cx = left + 108;
  float cy = top + h * 0.52;
  float r = min(68, h * 0.31);
  float x = spinBloch[q][0];
  float y = spinBloch[q][1];
  float z = spinBloch[q][2];

  stroke(0, 0, 0.32);
  strokeWeight(1);
  noFill();
  ellipse(cx, cy, r * 2, r * 2);
  line(cx - r, cy, cx + r, cy);
  line(cx, cy - r, cx, cy + r);
  fill(0, 0, 0.68);
  text("-X", cx - r - 22, cy + 4);
  text("+X", cx + r + 8, cy + 4);
  text("+Z", cx - 9, cy - r - 10);
  text("-Z", cx - 9, cy + r + 20);

  int count = min(spinTrailCount[q], SCOPE_HISTORY);
  int start = (spinTrailWriteIndex[q] - count + SCOPE_HISTORY) % SCOPE_HISTORY;
  for (int i = 1; i < count; i++) {
    int a = (start + i - 1) % SCOPE_HISTORY;
    int b = (start + i) % SCOPE_HISTORY;
    float ax = cx + spinTrail[q][a][0] * r;
    float ay = cy - spinTrail[q][a][2] * r;
    float bx = cx + spinTrail[q][b][0] * r;
    float by = cy - spinTrail[q][b][2] * r;
    float alpha = map(i, 1, max(1, count - 1), 0.14, 0.80);
    stroke(0.58, 0.18, 0.95, alpha);
    strokeWeight(1.5);
    line(ax, ay, bx, by);
  }

  float vx = cx + constrain(x, -1, 1) * r;
  float vz = cy - constrain(z, -1, 1) * r;
  float hue = y >= 0 ? 0.33 : 0.88;
  float dot = 8 + 10 * constrain(abs(y), 0, 1);
  stroke(0.02, 0.88, 1.0);
  strokeWeight(3);
  line(cx, cy, vx, vz);
  noStroke();
  fill(hue, 0.82, 1.0);
  ellipse(vx, vz, dot, dot);

  float readX = left + 210;
  fill(0, 0, 1);
  text("q" + q + " spin", readX, top + 30);
  text("x " + nf(x, 1, 3) + "   y " + nf(y, 1, 3) + "   z " + nf(z, 1, 3), readX, top + 54);
  text("length " + nf(spinLength[q], 1, 3) + "   phase " + nf(spinPhase[q], 1, 3), readX, top + 78);
  text("purity " + nf(spinPurity[q], 1, 3) + "   entropy " + nf(spinEntropy[q], 1, 3), readX, top + 102);
  text("speed " + nf(spinSpeed[q], 1, 3), readX, top + 126);
  float barW = max(120, w - 245);
  drawMiniBar("X", readX, top + 152, barW, 8, x, true);
  drawMiniBar("Y", readX, top + 176, barW, 8, y, true);
  drawMiniBar("Z", readX, top + 200, barW, 8, z, true);
}

void drawMiniBar(String label, float x, float y, float w, float h, float value, boolean bipolar) {
  fill(0, 0, 0.20);
  noStroke();
  rect(x, y, w, h);
  float norm = bipolar ? map(constrain(value, -1, 1), -1, 1, 0, 1) : constrain(value, 0, 1);
  fill(value >= 0 ? color(0.33, 0.75, 0.95) : color(0.88, 0.75, 0.95));
  rect(x, y, w * norm, h);
  fill(0, 0, 0.78);
  text(label + " " + nf(value, 1, 3), x, y - 4);
}

void drawSpinCorrelationPanel(float left, float top, float right, float bottom) {
  fill(0, 0, 0.10, 0.78);
  noStroke();
  rect(left, top, right - left, bottom - top, 8);
  fill(0, 0, 1);
  text("Pair spin correlations [XX YY ZZ]", left + 12, top + 22);
  String[] pairs = {"01", "02", "03", "12", "13", "23"};
  for (int i = 0; i < 6; i++) {
    float y = top + 44 + i * 18;
    text("q" + pairs[i].charAt(0) + "-q" + pairs[i].charAt(1), left + 12, y);
    for (int k = 0; k < 3; k++) {
      float v = pairSpinXXYYZZ[i][k];
      float x = left + 78 + k * 72;
      fill(v >= 0 ? color(0.33, 0.72, 0.95) : color(0.88, 0.72, 0.95));
      rect(x, y - 10, 30 * abs(v), 8);
      fill(0, 0, 0.82);
      text(nf(v, 1, 2), x + 34, y);
    }
  }
}

void drawGyroscopeMode() {
  hint(DISABLE_DEPTH_TEST);
  camera();
  noLights();

  fill(0, 0, 1);
  text("Spin gyroscope mode", 24, 108);
  text(hasSpin ? "live density spin: axis, precession, speed, coupling" : "waiting for /qmw/spin stream", 24, 128);
  text("disc tilt = Bloch X/Z, color = Y handedness, ring intensity = angular speed", 24, 148);

  float left = 72;
  float top = 190;
  float gapX = 300;
  float gapY = 265;
  float[][] centers = {
    {left, top},
    {left + gapX, top},
    {left, top + gapY},
    {left + gapX, top + gapY}
  };

  for (int q = 0; q < 4; q++) {
    drawGyroDisc(q, centers[q][0], centers[q][1], 96);
  }

  drawGyroCouplingMap(width * 0.62, 190, width - 70, height - 90);

  lights();
  hint(ENABLE_DEPTH_TEST);
}

void drawGyroDisc(int q, float cx, float cy, float r) {
  float x = spinBloch[q][0];
  float y = spinBloch[q][1];
  float z = spinBloch[q][2];
  float length = spinLength[q];
  float phase = spinPhase[q];
  float speed = spinSpeed[q];
  float handedHue = y >= 0 ? 0.33 : 0.88;
  float glow = constrain(speed * 0.12, 0.12, 1.0);

  fill(0, 0, 0.08, 0.74);
  noStroke();
  rect(cx - r - 34, cy - r - 46, 2 * r + 68, 2 * r + 108, 10);

  stroke(0.58, 0.16, 0.28 + 0.65 * glow, 0.82);
  strokeWeight(2 + 5 * glow);
  noFill();
  ellipse(cx, cy, r * 2.05, r * (0.62 + 0.32 * abs(z)));

  pushMatrix();
  translate(cx, cy);
  rotate(phase);
  stroke(handedHue, 0.64, 0.88, 0.56);
  strokeWeight(2);
  noFill();
  ellipse(0, 0, r * 1.75, r * 0.45);
  line(-r * 0.88, 0, r * 0.88, 0);
  popMatrix();

  int count = min(spinTrailCount[q], SCOPE_HISTORY);
  int start = (spinTrailWriteIndex[q] - count + SCOPE_HISTORY) % SCOPE_HISTORY;
  for (int i = 1; i < count; i++) {
    int a = (start + i - 1) % SCOPE_HISTORY;
    int b = (start + i) % SCOPE_HISTORY;
    float ax = cx + spinTrail[q][a][0] * r * 0.78;
    float ay = cy - spinTrail[q][a][2] * r * 0.78;
    float bx = cx + spinTrail[q][b][0] * r * 0.78;
    float by = cy - spinTrail[q][b][2] * r * 0.78;
    float alpha = map(i, 1, max(1, count - 1), 0.10, 0.72);
    stroke(0.10, 0.78, 0.95, alpha);
    strokeWeight(1.4);
    line(ax, ay, bx, by);
  }

  float axisX = x * r * 0.86;
  float axisY = -z * r * 0.86;
  stroke(0.02, 0.88, 1.0);
  strokeWeight(4);
  line(cx, cy, cx + axisX, cy + axisY);
  noStroke();
  fill(handedHue, 0.86, 1.0);
  ellipse(cx + axisX, cy + axisY, 12 + 12 * abs(y), 12 + 12 * abs(y));

  fill(0, 0, 1);
  text("q" + q + " gyro", cx - r, cy - r - 22);
  text("len " + nf(length, 1, 3) + "  phase " + nf(phase, 1, 2), cx - r, cy + r + 28);
  text("speed " + nf(speed, 1, 3) + "  purity " + nf(spinPurity[q], 1, 3), cx - r, cy + r + 48);
}

void drawGyroCouplingMap(float left, float top, float right, float bottom) {
  fill(0, 0, 0.08, 0.76);
  noStroke();
  rect(left, top, right - left, bottom - top, 10);
  fill(0, 0, 1);
  text("Gyro coupling map", left + 18, top + 28);
  text("pair tension from |XX|+|YY|+|ZZ|", left + 18, top + 48);

  float cx = (left + right) * 0.5;
  float cy = (top + bottom) * 0.52;
  float rr = min(right - left, bottom - top) * 0.32;
  float[][] pos = {
    {cx, cy - rr},
    {cx + rr, cy},
    {cx, cy + rr},
    {cx - rr, cy}
  };
  int[][] pairs = {
    {0, 1}, {0, 2}, {0, 3}, {1, 2}, {1, 3}, {2, 3}
  };

  for (int i = 0; i < pairs.length; i++) {
    int a = pairs[i][0];
    int b = pairs[i][1];
    float tension = (
      abs(pairSpinXXYYZZ[i][0])
      + abs(pairSpinXXYYZZ[i][1])
      + abs(pairSpinXXYYZZ[i][2])
    ) / 3.0;
    stroke(0.58, 0.76, 0.35 + 0.65 * tension, 0.20 + 0.70 * tension);
    strokeWeight(1 + 7 * tension);
    line(pos[a][0], pos[a][1], pos[b][0], pos[b][1]);
  }

  for (int q = 0; q < 4; q++) {
    float len = spinLength[q];
    noStroke();
    fill(0.10 + 0.12 * q, 0.70, 0.45 + 0.55 * len);
    ellipse(pos[q][0], pos[q][1], 34 + 18 * len, 34 + 18 * len);
    fill(0, 0, 1);
    text("q" + q, pos[q][0] - 8, pos[q][1] + 4);
  }
}



void drawFrequencyPanel(int channel, float left, float top, float right, float bottom, int samples, int bins) {
  drawPanelGrid(left, top, right, bottom);

  float[] magnitudes = new float[bins + 1];
  float maxMag = 0.000001;
  for (int bin = 1; bin <= bins; bin++) {
    magnitudes[bin] = dftMagnitude(channel, bin, samples);
    maxMag = max(maxMag, magnitudes[bin]);
  }

  strokeWeight(1);
  for (int bin = 1; bin <= bins; bin++) {
    float mag = magnitudes[bin];
    float x = map(bin, 1, bins, left, right);
    float y = bottom - (mag / maxMag) * (bottom - top);
    float hue = map(bin, 1, bins, 0.54, 0.86);
    stroke(hue, 0.78, 0.88, 0.88);
    line(x, bottom, x, y);
    stroke(hue, 0.45, 1.0, 0.94);
    strokeWeight(3);
    point(x, y);
    strokeWeight(1);
  }

  fill(0, 0, 0.92);
  text("frequency bins 1-" + bins + "  peak " + nf(maxMag, 1, 6), left, bottom + 13);
}

void drawPanelGrid(float left, float top, float right, float bottom) {
  stroke(0, 0, 0.24, 0.80);
  strokeWeight(1);
  noFill();
  rect(left, top, right - left, bottom - top);
  for (int i = 1; i < 4; i++) {
    float x = lerp(left, right, i / 4.0);
    line(x, top, x, bottom);
  }
  for (int i = 1; i < 3; i++) {
    float y = lerp(top, bottom, i / 3.0);
    line(left, y, right, y);
  }
}

float signalWindowMean(int channel, int samples) {
  float sum = 0.0;
  for (int n = 0; n < samples; n++) {
    int idx = (signalWriteIndex - samples + n + SCOPE_HISTORY) % SCOPE_HISTORY;
    sum += signalHistory[channel][idx];
  }
  return sum / float(samples);
}

float dftMagnitude(int channel, int bin, int samples) {
  float mean = signalWindowMean(channel, samples);
  float re = 0.0;
  float im = 0.0;

  for (int n = 0; n < samples; n++) {
    int idx = (signalWriteIndex - samples + n + SCOPE_HISTORY) % SCOPE_HISTORY;
    float window = 0.5 - 0.5 * cos(TWO_PI * n / float(samples - 1));
    float v = (signalHistory[channel][idx] - mean) * window;
    float phase = TWO_PI * bin * n / float(samples);
    re += v * cos(phase);
    im -= v * sin(phase);
  }

  return sqrt(re * re + im * im) / float(samples);
}

void drawStateTrajectoryScope() {
  pushMatrix();
  translate(width * 0.46, height * 0.56, 0);
  scale(zoom);
  rotateX(rotX);
  rotateY(rotY);

  float radius = min(width * 0.24, height * 0.34);
  drawTrajectoryAxes(radius);

  noFill();
  for (int i = 1; i < SCOPE_HISTORY; i++) {
    int a = (scopeWriteIndex + i - 1) % SCOPE_HISTORY;
    int b = (scopeWriteIndex + i) % SCOPE_HISTORY;
    float age = i / float(SCOPE_HISTORY - 1);
    float z = 0.5 * (scopeZHistory[a] + scopeZHistory[b]);
    float hue = 0.54 + 0.26 * z + 0.12 * age;
    hue = hue - floor(hue);
    stroke(hue, 0.80, 0.25 + age * 0.70, 0.16 + age * 0.70);
    strokeWeight(1.1 + 1.4 * age);
    line(
      scopeXHistory[a] * radius,
      -scopeYHistory[a] * radius,
      scopeZHistory[a] * radius,
      scopeXHistory[b] * radius,
      -scopeYHistory[b] * radius,
      scopeZHistory[b] * radius
    );
  }
  popMatrix();

  drawStateTrajectoryReadout();
}

void drawTrajectoryAxes(float radius) {
  strokeWeight(1);
  stroke(0, 0, 0.28, 0.75);
  noFill();
  box(radius * 2.0);

  stroke(0.00, 0.72, 0.90);
  line(-radius, 0, 0, radius, 0, 0);
  stroke(0.34, 0.72, 0.90);
  line(0, -radius, 0, 0, radius, 0);
  stroke(0.58, 0.72, 0.90);
  line(0, 0, -radius, 0, 0, radius);
}

void drawStateTrajectoryReadout() {
  hint(DISABLE_DEPTH_TEST);
  camera();
  boolean externalActive = hasScopeInput && millis() - lastScopeInputMs < 1500;
  int latest = (scopeWriteIndex + SCOPE_HISTORY - 1) % SCOPE_HISTORY;
  fill(0, 0, 1);
  text(externalActive ? "XYZ trace: external OSC data" : "XYZ trace: Bloch / perturbed Bloch data", 24, 108);
  text(
    "x " + nf(scopeXHistory[latest], 1, 4)
      + "   y " + nf(scopeYHistory[latest], 1, 4)
      + "   z " + nf(scopeZHistory[latest], 1, 4)
      + "   H " + nf(hamiltonianX, 1, 4) + " "
      + nf(hamiltonianY, 1, 4) + " "
      + nf(hamiltonianZ, 1, 4),
    24,
    128
  );
  hint(ENABLE_DEPTH_TEST);
}

void sampleScopeInput() {
  boolean externalActive = hasScopeInput && millis() - lastScopeInputMs < 1500;
  float x = externalActive ? scopeX : perturbedBlochX;
  float y = externalActive ? scopeY : perturbedBlochY;
  float z = externalActive ? scopeZ : perturbedBlochZ;

  if (!externalActive && abs(x) + abs(y) + abs(z) < 0.0001) {
    x = blochX;
    y = blochY;
    z = blochZ;
  }

  scopeXHistory[scopeWriteIndex] = constrain(x, -1.0, 1.0);
  scopeYHistory[scopeWriteIndex] = constrain(y, -1.0, 1.0);
  scopeZHistory[scopeWriteIndex] = constrain(z, -1.0, 1.0);
  scopeWriteIndex = (scopeWriteIndex + 1) % SCOPE_HISTORY;
}

void drawLissajousScope() {
  hint(DISABLE_DEPTH_TEST);
  camera();
  noLights();

  float cx = width * 0.45;
  float cy = height * 0.54;
  float radius = min(width * 0.34, height * 0.40) * zoom;
  boolean externalActive = hasScopeInput && millis() - lastScopeInputMs < 1500;

  drawScopeGrid(cx, cy, radius);

  drawDirectScopeTrace(cx, cy, radius);

  drawScopeReadout(cx, cy, radius);
  hint(ENABLE_DEPTH_TEST);
  lights();
}

void drawDirectScopeTrace(float cx, float cy, float radius) {
  noFill();
  for (int i = 1; i < SCOPE_HISTORY; i++) {
    int a = (scopeWriteIndex + i - 1) % SCOPE_HISTORY;
    int b = (scopeWriteIndex + i) % SCOPE_HISTORY;
    float age = i / float(SCOPE_HISTORY - 1);
    float za = scopeZHistory[a];
    float zb = scopeZHistory[b];
    float z = 0.5 * (za + zb);
    float hue = 0.54 + 0.28 * z + 0.12 * age;
    hue = hue - floor(hue);
    float alpha = constrain(0.05 + age * 0.82, 0.0, 0.9);
    float bright = constrain(0.18 + age * 0.68 + abs(z) * 0.26, 0.0, 1.0);
    stroke(hue, 0.82, bright, alpha);
    strokeWeight(1.0 + max(0.0, z) * 2.4);
    line(
      cx + scopeXHistory[a] * radius,
      cy - scopeYHistory[a] * radius,
      cx + scopeXHistory[b] * radius,
      cy - scopeYHistory[b] * radius
    );
  }
}

void drawScopeGrid(float cx, float cy, float radius) {
  stroke(0, 0, 0.20, 0.70);
  strokeWeight(1);
  noFill();
  for (int ring = 1; ring <= 4; ring++) {
    ellipse(cx, cy, radius * 0.5 * ring, radius * 0.5 * ring);
  }
  line(cx - radius, cy, cx + radius, cy);
  line(cx, cy - radius, cx, cy + radius);

  for (int tick = -4; tick <= 4; tick++) {
    float x = cx + tick * radius / 4.0;
    float y = cy + tick * radius / 4.0;
    line(x, cy - 7, x, cy + 7);
    line(cx - 7, y, cx + 7, y);
  }
}

void drawScopeReadout(float cx, float cy, float radius) {
  boolean externalActive = hasScopeInput && millis() - lastScopeInputMs < 1500;
  int latest = (scopeWriteIndex + SCOPE_HISTORY - 1) % SCOPE_HISTORY;
  int previous = (scopeWriteIndex + SCOPE_HISTORY - 2) % SCOPE_HISTORY;
  float x = scopeXHistory[latest];
  float y = scopeYHistory[latest];
  float z = scopeZHistory[latest];
  float r = sqrt(x * x + y * y);
  float angle = atan2(y, x);
  float speed = dist(x, y, scopeXHistory[previous], scopeYHistory[previous]);

  fill(0, 0, 1);
  text(
    externalActive ? "XY scope: external OSC data" : "XY scope: Bloch XY data",
    cx - radius,
    cy + radius + 28
  );
  text(
    "x " + nf(x, 1, 3)
      + "   y " + nf(y, 1, 3)
      + "   z " + nf(z, 1, 3)
      + "   r " + nf(r, 1, 3)
      + "   angle " + nf(angle, 1, 3)
      + "   speed " + nf(speed, 1, 4),
    cx - radius,
    cy + radius + 48
  );
}

void drawTelemetryPanel() {
  hint(DISABLE_DEPTH_TEST);
  camera();
  float x = width - 330;
  float y = 88;
  fill(0, 0, 0.08, 0.82);
  noStroke();
  rect(x - 18, y - 24, 306, 430);

  fill(0, 0, 1);
  text("Oscilloscope Telemetry", x, y);
  y += 26;
  text("Bloch      " + nf(blochX, 1, 3) + "  " + nf(blochY, 1, 3) + "  " + nf(blochZ, 1, 3), x, y);
  y += 20;
  text("Perturbed  " + nf(perturbedBlochX, 1, 3) + "  " + nf(perturbedBlochY, 1, 3) + "  " + nf(perturbedBlochZ, 1, 3), x, y);
  y += 30;
  text("Field strength      " + nf(fieldStrength, 1, 4), x, y);
  y += 20;
  text("Field acceleration  " + nf(fieldAcceleration, 1, 4), x, y);
  y += 30;
  text("Density Δ max       " + nf(densityDeltaMax, 1, 6), x, y);
  y += 20;
  text("Density Δ mean      " + nf(densityDeltaMean, 1, 6), x, y);
  y += 30;
  text("Bohm x              " + nf(bohmX, 1, 4), x, y);
  y += 20;
  text("Bohm velocity       " + nf(bohmVelocity, 1, 4), x, y);
  y += 20;
  text("Bohm speed          " + nf(bohmSpeed, 1, 4), x, y);
  y += 20;
  text("Bohm phase          " + nf(bohmPhase, 1, 4), x, y);
  y += 20;
  text("Bohm density        " + nf(bohmDensity, 1, 4), x, y);
  y += 20;
  text("Node proximity      " + nf(bohmNodeProximity, 1, 4), x, y);
  y += 20;
  text("Curvature           " + nf(bohmCurvature, 1, 4), x, y);
  y += 20;
  text("Field velocity      " + nf(bohmFieldVelocity, 1, 4), x, y);
  hint(ENABLE_DEPTH_TEST);
}

void oscEvent(OscMessage msg) {
  String addr = msg.addrPattern();

  if (addr.equals("/qmw/source/wavepacket/available")) {
    sourceWavepacketAvailable = msg.get(0).floatValue() > 0.5;
    if (!sourceWavepacketAvailable) {
      hasWavepacket = false;
      hasWavefunction = false;
      hasSpectrum = false;
    }
  } else if (addr.equals("/qmw/source/wavepacket/probability")) {
    for (int i = 0; i < min(N, msg.arguments().length); i++) {
      probabilityHistory[writeIndex][i] = msg.get(i).floatValue();
    }
    hasWavepacket = true;
    sourceWavepacketAvailable = true;
  } else if (addr.equals("/qmw/source/wavepacket/phase")) {
    for (int i = 0; i < min(N, msg.arguments().length); i++) {
      phaseHistory[writeIndex][i] = msg.get(i).floatValue();
    }
    writeIndex = (writeIndex + 1) % HISTORY;
    hasWavepacket = true;
  } else if (addr.equals("/qmw/source/wavepacket/real")) {
    for (int i = 0; i < min(N, msg.arguments().length); i++) {
      realPsi[i] = msg.get(i).floatValue();
      realHistory[writeIndex][i] = realPsi[i];
    }
    hasWavefunction = true;
  } else if (addr.equals("/qmw/source/wavepacket/imag")) {
    for (int i = 0; i < min(N, msg.arguments().length); i++) {
      imagPsi[i] = msg.get(i).floatValue();
      imagHistory[writeIndex][i] = imagPsi[i];
    }
    hasWavefunction = true;
  } else if (addr.equals("/qmw/source/wavepacket/spectrum")) {
    for (int i = 0; i < min(N, msg.arguments().length); i++) {
      spectrumHistory[writeIndex][i] = msg.get(i).floatValue();
    }
    hasSpectrum = true;
  } else if (addr.equals("/qmw/source/wavepacket/spectrum_phase")) {
    for (int i = 0; i < min(N, msg.arguments().length); i++) {
      spectrumPhaseHistory[writeIndex][i] = msg.get(i).floatValue();
    }
    hasSpectrum = true;
  } else if (addr.equals("/qmw/scope/x") || addr.equals("/scope/x")) {
    scopeX = msg.get(0).floatValue();
    hasScopeInput = true;
    lastScopeInputMs = millis();
  } else if (addr.equals("/qmw/scope/y") || addr.equals("/scope/y")) {
    scopeY = msg.get(0).floatValue();
    hasScopeInput = true;
    lastScopeInputMs = millis();
  } else if (addr.equals("/qmw/scope/z") || addr.equals("/scope/z")) {
    scopeZ = msg.get(0).floatValue();
    hasScopeInput = true;
    lastScopeInputMs = millis();
  } else if (addr.equals("/qmw/scope/xy") || addr.equals("/scope/xy") || addr.equals("/xy")) {
    if (msg.arguments().length >= 2) {
      scopeX = msg.get(0).floatValue();
      scopeY = msg.get(1).floatValue();
      hasScopeInput = true;
      lastScopeInputMs = millis();
    }
  } else if (addr.equals("/qmw/scope/xyz") || addr.equals("/scope/xyz") || addr.equals("/xyz")) {
    if (msg.arguments().length >= 3) {
      scopeX = msg.get(0).floatValue();
      scopeY = msg.get(1).floatValue();
      scopeZ = msg.get(2).floatValue();
      hasScopeInput = true;
      lastScopeInputMs = millis();
    }
  } else if (addr.startsWith("/qmw/density/real/")) {
    int row = int(addr.substring(addr.lastIndexOf("/") + 1));
    if (row >= 0 && row < 16) {
      for (int i = 0; i < min(16, msg.arguments().length); i++) {
        rhoReal[row][i] = msg.get(i).floatValue();
      }
      hasDensity = true;
    }
  } 
  
  else if (addr.startsWith("/qmw/density/imag/")) {
  int row = int(addr.substring(addr.lastIndexOf("/") + 1));
  if (row >= 0 && row < 16) {
    for (int i = 0; i < min(16, msg.arguments().length); i++) {
      rhoImag[row][i] = msg.get(i).floatValue();
    }
    hasDensity = true;
  }
}

else if (addr.equals("/qmw/density/eigenvalues")) {
  for (int i = 0; i < min(16, msg.arguments().length); i++) {
    densityEigenvalues[i] = msg.get(i).floatValue();
  }
}

else if (addr.startsWith("/qmw/density/eigenvector/")) {
  String[] parts = split(addr, "/");
  int mode = int(parts[4]);
  String component = parts[5];

  if (mode >= 0 && mode < 16) {
    for (int i = 0; i < min(16, msg.arguments().length); i++) {
      if (component.equals("real")) {
        eigenReal[mode][i] = msg.get(i).floatValue();
      } else if (component.equals("imag")) {
        eigenImag[mode][i] = msg.get(i).floatValue();
      }
    }
  }
}

else if (addr.startsWith("/qmw/spin/q")) {
  String[] parts = split(addr, "/");
  if (parts.length >= 5) {
    int q = int(parts[3].substring(1));
    String field = parts[4];
    if (q >= 0 && q < 4) {
      if (field.equals("bloch") && msg.arguments().length >= 3) {
        spinBloch[q][0] = msg.get(0).floatValue();
        spinBloch[q][1] = msg.get(1).floatValue();
        spinBloch[q][2] = msg.get(2).floatValue();
        appendSpinTrail(q, spinBloch[q][0], spinBloch[q][1], spinBloch[q][2]);
        hasSpin = true;
      } else if (field.equals("length")) {
        spinLength[q] = msg.get(0).floatValue();
      } else if (field.equals("phase")) {
        spinPhase[q] = msg.get(0).floatValue();
      } else if (field.equals("purity")) {
        spinPurity[q] = msg.get(0).floatValue();
      } else if (field.equals("entropy")) {
        spinEntropy[q] = msg.get(0).floatValue();
      } else if (field.equals("speed")) {
        spinSpeed[q] = msg.get(0).floatValue();
      } else if (field.equals("trail")) {
        loadSpinTrail(q, msg);
        hasSpin = true;
      }
    }
  }
}

else if (addr.startsWith("/qmw/spin/pair/") && addr.endsWith("/xx_yy_zz")) {
  String[] parts = split(addr, "/");
  if (parts.length >= 6) {
    int pair = pairIndex(parts[4]);
    if (pair >= 0 && msg.arguments().length >= 3) {
      pairSpinXXYYZZ[pair][0] = msg.get(0).floatValue();
      pairSpinXXYYZZ[pair][1] = msg.get(1).floatValue();
      pairSpinXXYYZZ[pair][2] = msg.get(2).floatValue();
      hasSpin = true;
    }
  }
}
    
    
    else if (addr.startsWith("/qmw/qubit/") && addr.endsWith("/bloch")) {
  String[] parts = split(addr, "/");
  int q = int(parts[3]);

  if (q >= 0 && q < 4 && msg.arguments().length >= 3) {
    qubitBloch[q][0] = msg.get(0).floatValue();
    qubitBloch[q][1] = msg.get(1).floatValue();
    qubitBloch[q][2] = msg.get(2).floatValue();
      }
    
  } else if (addr.equals("/qmw/bloch/x") || addr.equals("/qmw/bloch/vector_x")) {
    blochX = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/bloch/y") || addr.equals("/qmw/bloch/vector_y")) {
    blochY = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/bloch/z") || addr.equals("/qmw/bloch/vector_z")) {
    blochZ = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/bloch/perturbed_x")) {
    perturbedBlochX = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/bloch/perturbed_y")) {
    perturbedBlochY = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/bloch/perturbed_z")) {
    perturbedBlochZ = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/visual/field_strength")) {
    fieldStrength = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/visual/field_acceleration")) {
    fieldAcceleration = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/density/delta_rho/max")) {
    densityDeltaMax = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/density/delta_rho/mean")) {
    densityDeltaMean = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/purity") || addr.equals("/qmw/density/purity")) {
    purity = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/coherence") || addr.equals("/qmw/density/coherence_l1")) {
    coherence = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/entropy") || addr.equals("/qmw/density/von_neumann_entropy")) {
    entropy = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/entanglement")) {
    entanglement = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/hamiltonian/x") || addr.equals("/qmw/hamiltonian/pauli_x")) {
    hamiltonianX = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/hamiltonian/y") || addr.equals("/qmw/hamiltonian/pauli_y")) {
    hamiltonianY = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/hamiltonian/z") || addr.equals("/qmw/hamiltonian/pauli_z")) {
    hamiltonianZ = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/bohm/x") || addr.equals("/qmw/bohm/position")) {
    bohmX = msg.get(0).floatValue();
  } 
   else if (addr.startsWith("/qmw/qubit/") && addr.endsWith("/bloch")) {
    String[] parts = split(addr, "/");
    int q = int(parts[3]);

    if (q >= 0 && q < 4 && msg.arguments().length >= 3) {
    qubitBloch[q][0] = msg.get(0).floatValue();
    qubitBloch[q][1] = msg.get(1).floatValue();
    qubitBloch[q][2] = msg.get(2).floatValue();
  }
}
    else if (addr.equals("/qmw/bohm/velocity")) {
    bohmVelocity = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/bohm/speed")) {
    bohmSpeed = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/bohm/phase")) {
    bohmPhase = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/bohm/density") || addr.equals("/qmw/bohm/local_density")) {
    bohmDensity = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/bohm/node_proximity")) {
    bohmNodeProximity = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/bohm/curvature") || addr.equals("/qmw/bohm/field_curvature")) {
    bohmCurvature = msg.get(0).floatValue();
  } else if (addr.equals("/qmw/bohm/field_velocity")) {
    bohmFieldVelocity = msg.get(0).floatValue();
  }
}

int historyIndex(int offset) {
  return (writeIndex + offset) % HISTORY;
}

void appendSpinTrail(int q, float x, float y, float z) {
  if (q < 0 || q >= 4) return;
  int index = spinTrailWriteIndex[q];
  spinTrail[q][index][0] = x;
  spinTrail[q][index][1] = y;
  spinTrail[q][index][2] = z;
  spinTrailWriteIndex[q] = (index + 1) % SCOPE_HISTORY;
  spinTrailCount[q] = min(SCOPE_HISTORY, spinTrailCount[q] + 1);
}

void loadSpinTrail(int q, OscMessage msg) {
  if (q < 0 || q >= 4) return;
  int triples = min(SCOPE_HISTORY, msg.arguments().length / 3);
  spinTrailCount[q] = triples;
  spinTrailWriteIndex[q] = triples % SCOPE_HISTORY;
  for (int i = 0; i < triples; i++) {
    spinTrail[q][i][0] = msg.get(i * 3).floatValue();
    spinTrail[q][i][1] = msg.get(i * 3 + 1).floatValue();
    spinTrail[q][i][2] = msg.get(i * 3 + 2).floatValue();
  }
}

int pairIndex(String name) {
  if (name.equals("0_1")) return 0;
  if (name.equals("0_2")) return 1;
  if (name.equals("0_3")) return 2;
  if (name.equals("1_2")) return 3;
  if (name.equals("1_3")) return 4;
  if (name.equals("2_3")) return 5;
  return -1;
}

void mouseDragged() {
  rotY += (mouseX - pmouseX) * 0.01;
  rotX += (mouseY - pmouseY) * 0.01;
}

void mouseWheel(MouseEvent event) {
  zoom *= pow(1.08, -event.getCount());
  zoom = constrain(zoom, 0.22, 4.0);
}

void keyPressed() 
{
  println("KEY:", key, " displayMode:", displayMode);
  if (key == '1' || key == 'a' || key == 'A') displayMode = 1;
  if (key == '2' || key == 'b' || key == 'B') displayMode = 2;
  if (key == '3' || key == 'c' || key == 'C') displayMode = 3;
  if (key == '4' || key == 'd' || key == 'D') displayMode = 4;
  if (key == '5' || key == 'e' || key == 'E') displayMode = 5;
  if (key == '6' || key == 's' || key == 'S') displayMode = 6;
  if (key == '7' || key == 'g' || key == 'G') displayMode = 7;
  if (key == '8' || key == 'h' || key == 'H') displayMode = 8;  if (key == '9' || key == 'i' || key == 'I') displayMode = 9;
  if (key == 'j' || key == 'J') displayMode = 10;
  if (key == 'k' || key == 'K') displayMode = 11;
  if (key == 'l' || key == 'L') displayMode = 12;
  if (key == 'y' || key == 'Y') displayMode = 13;
  if (displayMode == 1 && (key == 'm' || key == 'M')) {
  densityDisplayMode = (densityDisplayMode + 1) % 5;
}

if (displayMode == 1 && (key == 'n' || key == 'N')) {
  densityEigenMode = (densityEigenMode + 1) % 16;
  println("densityEigenMode:", densityEigenMode);

}

if (displayMode == 1 && (key == 't' || key == 'T')) {
    tensorRenderMode = (tensorRenderMode + 1) % 3;
}

  if (key == '+' || key == '=') zoom *= 1.08;
  if (key == '-' || key == '_') zoom /= 1.08;
  if (key == ']') heightScale *= 1.10;
  if (key == '[') heightScale /= 1.10;
  if (key == '}') waveWindow += 8;
  if (key == '{') waveWindow -= 8;
  if (key == 'f' || key == 'F') followPacket = !followPacket;
  if (key == CODED) {
    if (keyCode == LEFT) rotY -= 0.08;
    if (keyCode == RIGHT) rotY += 0.08;
    if (keyCode == UP) rotX -= 0.08;
    if (keyCode == DOWN) rotX += 0.08;
  }
  if (key == '0') {
    rotX = -0.95;
    rotY = 0.55;
    zoom = 0.86;
    heightScale = 520.0;
    waveWindow = 112;
    followPacket = true;
  }
  zoom = constrain(zoom, 0.22, 4.0);
  heightScale = constrain(heightScale, 80.0, 2400.0);
  waveWindow = constrain(waveWindow, 32, N);
}
