/**
 * QMW Photoionization Microscopy v1
 *
 * Processing 4 visualizer for the Deng et al. Figure 5 reference source.
 * Dependency: oscP5. OSC input: UDP 17620.
 *
 * Scientific display:
 *   circular image <- normalized radial detector flux
 *   curve          <- the same detector observable in rho
 *   lanes          <- eight equal radial integrations for QMW renderers
 *   peak rings     <- detected radial maxima
 */

import oscP5.*;
import netP5.*;

OscP5 oscP5;

final int OSC_PORT = 17620;
final int SAMPLE_COUNT = 101;
final int LANE_COUNT = 8;
final float RHO_MAX_UM = 0.15;

float[] rhoUm = new float[SAMPLE_COUNT];
float[] targetFlux = new float[SAMPLE_COUNT];
float[] displayFlux = new float[SAMPLE_COUNT];
float[] lanes = new float[LANE_COUNT];
float[] peakRho = new float[8];
float[] peakWeight = new float[8];
int peakCount = 0;
PImage[] spatialFields = new PImage[5];
float[] spatialFieldAnchors = {0, 2, 4, 6, 8};
PImage[][] stateAtlas = new PImage[4][2];
String[] stateLabels = {"(0,29,0)", "(3,26,0)", "(23,0,0)", "(20,3,0)"};
String[] stateFamilies = {"RED STARK", "RED STARK", "BLUE STARK", "BLUE STARK"};
String[] stateNodes = {"0 transverse nodes", "3 transverse nodes", "0 transverse nodes", "3 transverse nodes"};
String[] stateFiles = {"red_0_29_0", "red_3_26_0", "blue_23_0_0", "blue_20_3_0"};
boolean stateAtlasMode = false;
int selectedState = 0;

float electricField = 808.0;
float magneticField = 0.0;
float resonanceEnergy = -169.617;
float radialMean = 0.0;
float radialRms = 0.0;
float radialExtent = 0.0;
float targetMagneticField = 0.0;
float targetEnergy = -169.617;
float targetMean = 0.0;
float targetRms = 0.0;
float targetExtent = 0.0;

long lastOscMs = -100000;
boolean paused = false;
boolean showGuides = true;
PFont uiFont;

void settings() {
  size(1440, 900, P2D);
  smooth(8);
}

void setup() {
  surface.setTitle("QMW Photoionization Microscopy v1");
  frameRate(60);
  oscP5 = new OscP5(this, OSC_PORT);
  uiFont = createFont("Helvetica Neue", 14);
  textFont(uiFont);
  for (int i = 0; i < SAMPLE_COUNT; i++) {
    rhoUm[i] = RHO_MAX_UM * i / float(SAMPLE_COUNT - 1);
  }
  for (int i = 0; i < spatialFields.length; i++) {
    spatialFields[i] = loadImage("figure5_spatial_b" + int(spatialFieldAnchors[i]) + ".png");
  }
  for (int i = 0; i < stateAtlas.length; i++) {
    stateAtlas[i][0] = loadImage("figure4_" + stateFiles[i] + "_b0.png");
    stateAtlas[i][1] = loadImage("figure4_" + stateFiles[i] + "_b6.png");
  }
  println("Photoionization visualizer listening on UDP " + OSC_PORT);
}

void draw() {
  background(3, 7, 17);
  if (!paused) updateSmoothedState();
  drawHeader();
  if (stateAtlasMode) {
    drawStateAtlas();
    drawFooter();
    return;
  }
  drawSpatialField(42, 168, 755, 300);
  drawDetector(1080, 300, 190);
  drawProfile(42, 565, 755, 205);
  drawLanes(850, 610, 535, 155);
  drawFooter();
}

void updateSmoothedState() {
  magneticField = lerp(magneticField, targetMagneticField, 0.10);
  resonanceEnergy = lerp(resonanceEnergy, targetEnergy, 0.10);
  radialMean = lerp(radialMean, targetMean, 0.10);
  radialRms = lerp(radialRms, targetRms, 0.10);
  radialExtent = lerp(radialExtent, targetExtent, 0.10);
  for (int i = 0; i < SAMPLE_COUNT; i++) {
    displayFlux[i] = lerp(displayFlux[i], targetFlux[i], 0.14);
  }
}

void drawHeader() {
  fill(236, 244, 255);
  textAlign(LEFT, TOP);
  textSize(25);
  text("PHOTOIONIZATION MICROSCOPY", 38, 30);

  fill(112, 196, 232);
  textSize(12);
  text(
    stateAtlasMode
      ? "FIGURE 4 STATE ATLAS  ·  PARABOLIC QUANTUM NUMBERS  ·  F = 808 V/cm"
      : "HYDROGEN  ·  RED STARK RESONANCE (1,28,0)  ·  F = 808 V/cm",
    40, 67
  );

  boolean live = millis() - lastOscMs < 2000;
  noStroke();
  fill(live ? color(58, 221, 174) : color(228, 142, 70));
  circle(1254, 48, 9);
  fill(170, 188, 207);
  textAlign(RIGHT, CENTER);
  text(live ? "OSC LIVE  :17620" : "WAITING FOR OSC  :17620", 1385, 48);
}

void drawStateAtlas() {
  float selectorY = 108;
  float selectorX = 42;
  float selectorW = 315;
  float selectorGap = 12;
  for (int i = 0; i < stateLabels.length; i++) {
    float x = selectorX + i * (selectorW + selectorGap);
    noStroke();
    fill(i == selectedState ? color(22, 111, 145) : color(15, 27, 43));
    rect(x, selectorY, selectorW, 54, 5);
    fill(232, 242, 252);
    textAlign(LEFT, CENTER);
    textSize(14);
    text((i + 1) + "  " + stateFamilies[i] + "  " + stateLabels[i], x + 14, selectorY + 20);
    fill(139, 160, 181);
    textSize(11);
    text(stateNodes[i], x + 14, selectorY + 39);
  }

  float panelY = 215;
  drawAtlasPanel(stateAtlas[selectedState][0], 58, panelY, 630, 480, "B = 0 T");
  drawAtlasPanel(stateAtlas[selectedState][1], 752, panelY, 630, 480, "B = 6 T");

  fill(226, 236, 247);
  textAlign(LEFT, TOP);
  textSize(17);
  text(
    stateFamilies[selectedState] + "  " + stateLabels[selectedState]
    + "  ·  " + stateNodes[selectedState],
    58, 742
  );
  fill(126, 149, 172);
  textSize(12);
  String behavior = selectedState < 2
    ? "Red state: the 6 T diamagnetic field compresses the distribution toward the symmetry axis."
    : "Blue state: the 6 T field pushes the distribution farther from the symmetry axis in this energy regime.";
  text(behavior, 58, 772);
  text(
    "These are probability-density images. Dark nodal surfaces distinguish states; wavefunction sign/phase is not present in the printed figure.",
    58, 794
  );
}

void drawAtlasPanel(PImage imageValue, float x, float y, float w, float h, String label) {
  fill(8, 14, 36);
  noStroke();
  rect(x, y, w, h);
  if (imageValue != null) {
    float scaleValue = min(w / imageValue.width, h / imageValue.height);
    float drawW = imageValue.width * scaleValue;
    float drawH = imageValue.height * scaleValue;
    imageMode(CORNER);
    image(imageValue, x + (w - drawW) * 0.5, y + (h - drawH) * 0.5, drawW, drawH);
  }
  noFill();
  stroke(80, 106, 134);
  rect(x, y, w, h);
  fill(238, 246, 255);
  textAlign(LEFT, TOP);
  textSize(16);
  text(label, x + 15, y + 13);
}

void drawDetector(float cx, float cy, float radius) {
  fill(10, 17, 31);
  noStroke();
  circle(cx, cy, radius * 2.0 + 34);

  if (showGuides) {
    noFill();
    stroke(90, 118, 145, 55);
    strokeWeight(1);
    for (int i = 1; i <= 4; i++) circle(cx, cy, radius * 2.0 * i / 4.0);
    line(cx - radius, cy, cx + radius, cy);
    line(cx, cy - radius, cx, cy + radius);
  }

  for (int i = SAMPLE_COUNT - 1; i >= 1; i--) {
    float value = constrain(displayFlux[i], 0, 1);
    float rr = radius * rhoUm[i] / RHO_MAX_UM;
    color c = microscopyColor(value);
    noFill();
    stroke(red(c), green(c), blue(c), 30 + 220 * pow(value, 0.7));
    strokeWeight(max(2.0, radius / SAMPLE_COUNT * 2.35));
    circle(cx, cy, rr * 2.0);
  }

  noStroke();
  fill(234, 250, 255, 210);
  circle(cx, cy, 3.5);

  for (int i = 0; i < peakCount; i++) {
    float rr = radius * peakRho[i] / RHO_MAX_UM;
    noFill();
    stroke(255, 225, 105, 220 * peakWeight[i]);
    strokeWeight(1.5);
    circle(cx, cy, rr * 2.0);
  }

  fill(166, 185, 205);
  textAlign(CENTER, TOP);
  textSize(12);
  text("DETECTOR PLANE  ·  RADIAL PROBABILITY FLUX", cx, cy + radius + 35);
  fill(104, 126, 151);
  text("0.15 µm radius", cx, cy + radius + 56);
}

color microscopyColor(float value) {
  value = constrain(value, 0, 1);
  if (value < 0.45) {
    return lerpColor(color(7, 20, 76), color(0, 188, 232), value / 0.45);
  }
  return lerpColor(color(0, 188, 232), color(255, 226, 86), (value - 0.45) / 0.55);
}

void drawSpatialField(float x, float y, float w, float h) {
  fill(225, 236, 248);
  textAlign(LEFT, BOTTOM);
  textSize(15);
  text("RESONANT ELECTRON SPATIAL DISTRIBUTION  ·  ρ,z", x, y - 25);

  int upper = 0;
  while (upper < spatialFieldAnchors.length && spatialFieldAnchors[upper] < magneticField) upper++;
  if (upper <= 0) upper = 0;
  if (upper >= spatialFieldAnchors.length) upper = spatialFieldAnchors.length - 1;
  int lower = max(0, upper - 1);
  float blend = upper == lower ? 0 : map(
    magneticField, spatialFieldAnchors[lower], spatialFieldAnchors[upper], 0, 1
  );

  noStroke();
  fill(8, 14, 36);
  rect(x, y, w, h);
  imageMode(CORNER);
  if (spatialFields[lower] != null) {
    tint(255, 255 * (1.0 - blend));
    image(spatialFields[lower], x, y, w, h);
  }
  if (upper != lower && spatialFields[upper] != null) {
    tint(255, 255 * blend);
    image(spatialFields[upper], x, y, w, h);
  }
  noTint();

  noFill();
  stroke(86, 112, 139, 150);
  strokeWeight(1);
  rect(x, y, w, h);
  line(x, y + h * 0.5, x + w, y + h * 0.5);

  fill(218, 229, 240);
  textSize(11);
  textAlign(LEFT, TOP);
  text("z = -0.6 µm", x, y + h + 9);
  textAlign(CENTER, TOP);
  text("detector direction  ←     z     →  Coulomb centre", x + w * 0.5, y + h + 9);
  textAlign(RIGHT, TOP);
  text("z ≈ 0", x + w, y + h + 9);
  textAlign(LEFT, BOTTOM);
  text("+ρ", x + 8, y + 18);
  textAlign(LEFT, TOP);
  text("-ρ", x + 8, y + h - 19);

  fill(126, 149, 172);
  textAlign(LEFT, TOP);
  text(
    "Paper-calculated density after 500 ps. Colored curves at 0 T and 8 T are the authors' representative classical paths.",
    x, y + h + 34
  );
}

void drawProfile(float x, float y, float w, float h) {
  fill(225, 236, 248);
  textAlign(LEFT, BOTTOM);
  textSize(15);
  text("NORMALIZED RADIAL DISTRIBUTION", x, y - 22);

  stroke(61, 80, 102);
  strokeWeight(1);
  noFill();
  rect(x, y, w, h);
  for (int i = 1; i < 4; i++) {
    float gy = y + h * i / 4.0;
    stroke(49, 66, 87, 110);
    line(x, gy, x + w, gy);
  }

  noStroke();
  fill(0, 194, 232, 34);
  beginShape();
  vertex(x, y + h);
  for (int i = 0; i < SAMPLE_COUNT; i++) {
    vertex(x + w * i / float(SAMPLE_COUNT - 1), y + h * (1.0 - displayFlux[i]));
  }
  vertex(x + w, y + h);
  endShape(CLOSE);

  noFill();
  stroke(64, 222, 245);
  strokeWeight(2.2);
  beginShape();
  for (int i = 0; i < SAMPLE_COUNT; i++) {
    vertex(x + w * i / float(SAMPLE_COUNT - 1), y + h * (1.0 - displayFlux[i]));
  }
  endShape();

  for (int i = 0; i < peakCount; i++) {
    float px = x + w * peakRho[i] / RHO_MAX_UM;
    float py = y + h * (1.0 - peakWeight[i]);
    noStroke();
    fill(255, 225, 105);
    circle(px, py, 8);
    fill(212, 222, 234);
    textAlign(CENTER, BOTTOM);
    textSize(10);
    text(nf(peakRho[i], 0, 4), px, py - 8);
  }

  fill(114, 137, 161);
  textAlign(LEFT, TOP);
  text("0", x, y + h + 10);
  textAlign(CENTER, TOP);
  text("ρ  (µm)", x + w * 0.5, y + h + 10);
  textAlign(RIGHT, TOP);
  text("0.15", x + w, y + h + 10);
}

void drawLanes(float x, float y, float w, float h) {
  fill(225, 236, 248);
  textAlign(LEFT, BOTTOM);
  textSize(15);
  text("EIGHT RADIAL LANES", x, y - 22);

  float gap = 9;
  float laneW = (w - gap * (LANE_COUNT - 1)) / LANE_COUNT;
  for (int i = 0; i < LANE_COUNT; i++) {
    float xx = x + i * (laneW + gap);
    float value = constrain(lanes[i], 0, 1);
    noStroke();
    fill(16, 27, 44);
    rect(xx, y, laneW, h);
    color c = microscopyColor(value);
    fill(red(c), green(c), blue(c), 220);
    rect(xx, y + h * (1.0 - value), laneW, h * value);
    fill(133, 153, 174);
    textAlign(CENTER, TOP);
    textSize(11);
    text(str(i + 1), xx + laneW * 0.5, y + h + 9);
    fill(210, 222, 234);
    textAlign(CENTER, BOTTOM);
    text(nf(value, 0, 3), xx + laneW * 0.5, y + h * (1.0 - value) - 6);
  }
}

void drawFooter() {
  float y = 846;
  fill(235, 242, 251);
  textAlign(LEFT, CENTER);
  textSize(18);
  text("B  " + nf(magneticField, 1, 2) + " T", 40, y);
  text("E  " + nf(resonanceEnergy, 1, 3) + " cm⁻¹", 245, y);
  text("RMS  " + nf(radialRms, 0, 4) + " µm", 525, y);
  text("EXTENT  " + nf(radialExtent, 0, 4) + " µm", 770, y);
  fill(103, 127, 152);
  textSize(11);
  textAlign(RIGHT, CENTER);
  text(
    stateAtlasMode
      ? "1–4 select state  ·  M live microscopy  ·  digitized Figure 4 reference data"
      : "P pause  ·  G guides  ·  A state atlas  ·  digitized Figure 5 reference data",
    1385, y
  );
}

void oscEvent(OscMessage message) {
  String address = message.addrPattern();
  lastOscMs = millis();
  if (address.equals("/qmw/photoionization/config") && message.arguments().length >= 2) {
    electricField = message.get(0).floatValue();
    targetMagneticField = message.get(1).floatValue();
  } else if (address.equals("/qmw/photoionization/resonance") && message.arguments().length >= 2) {
    targetEnergy = message.get(1).floatValue();
  } else if (address.equals("/qmw/photoionization/detector/rho_um")) {
    copyFloats(message, rhoUm, SAMPLE_COUNT);
  } else if (address.equals("/qmw/photoionization/detector/radial_flux")) {
    copyFloats(message, targetFlux, SAMPLE_COUNT);
  } else if (address.equals("/qmw/photoionization/detector/lanes")) {
    copyFloats(message, lanes, LANE_COUNT);
  } else if (address.equals("/qmw/photoionization/detector/peaks")) {
    peakCount = min(peakRho.length, message.arguments().length / 2);
    for (int i = 0; i < peakCount; i++) {
      peakRho[i] = message.get(i * 2).floatValue();
      peakWeight[i] = message.get(i * 2 + 1).floatValue();
    }
  } else if (address.equals("/qmw/photoionization/observables") && message.arguments().length >= 3) {
    targetMean = message.get(0).floatValue();
    targetRms = message.get(1).floatValue();
    targetExtent = message.get(2).floatValue();
  }
}

void copyFloats(OscMessage message, float[] destination, int limit) {
  int count = min(limit, message.arguments().length);
  for (int i = 0; i < count; i++) destination[i] = message.get(i).floatValue();
}

void keyPressed() {
  if (key == 'p' || key == 'P' || key == ' ') paused = !paused;
  if (key == 'g' || key == 'G') showGuides = !showGuides;
  if (key == 'a' || key == 'A') stateAtlasMode = true;
  if (key == 'm' || key == 'M') stateAtlasMode = false;
  if (key >= '1' && key <= '4') {
    selectedState = int(key - '1');
    stateAtlasMode = true;
  }
}

void mousePressed() {
  if (!stateAtlasMode) return;
  float selectorY = 108;
  float selectorX = 42;
  float selectorW = 315;
  float selectorGap = 12;
  if (mouseY < selectorY || mouseY > selectorY + 54) return;
  for (int i = 0; i < stateLabels.length; i++) {
    float x = selectorX + i * (selectorW + selectorGap);
    if (mouseX >= x && mouseX <= x + selectorW) selectedState = i;
  }
}
