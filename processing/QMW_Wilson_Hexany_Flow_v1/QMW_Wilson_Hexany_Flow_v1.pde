/**
 * QMW Wilson Hexany probability-flow visualizer.
 * Processing 4 + oscP5. Receives UDP 7411 from
 * examples/qmw_complete_cps_flow_v5.py and qmw_wilson_hexany_phase3.py.
 * Complete-CPS state frames and legacy v4 OSC addresses remain accepted.
 *
 

Six central vertices show the sounding Hexany.
Eight stellate tips expose probability outside the weight-two shell.
Vertex size represents probability.
Vertex color represents phase.
Directed pulses show the probability current being sonified.
The two interpenetrating tetrahedra distinguish harmonic and reciprocal/subharmonic structure.
Dragging rotates the complete stella octangula.
*/

import oscP5.*;
import netP5.*;

OscP5 osc;
final int OSC_PORT = 7411;
final float LEDGER_WIDTH = 470;
final int[] MASKS = {3, 5, 6, 9, 10, 12};
final int[] CPS_INDEX_MASKS = {3, 5, 9, 6, 10, 12};
final String[] RATIOS = {"1/1", "5/3", "5/4", "7/6", "7/4", "35/24"};
final String[] FACTORS = {"1·3", "1·5", "3·5", "1·7", "3·7", "5·7"};
String[] pendingTuningRatios = new String[6];
String[] pendingTuningFactors = new String[6];
boolean[] pendingTuningSeen = new boolean[6];

PVector[] lattice = {
  new PVector(1, 0, 0), new PVector(0, 1, 0), new PVector(0, 0, -1),
  new PVector(0, 0, 1), new PVector(0, -1, 0), new PVector(-1, 0, 0)
};
float[] probability = new float[6];
float[] phase = new float[6];
float[] activation = new float[6];
float[] phaseCoherence = new float[6];
float[] pendingProbability = new float[6];
float[] pendingPhase = new float[6];
float[] pendingActivation = new float[6];
float[] pendingCoherence = new float[6];
float[][] edgeCoupling = new float[6][6];
PVector[] screenPoint = new PVector[6];
PVector[] basisLattice = new PVector[16];
PVector[] basisScreen = new PVector[16];
float[] basisProbability = new float[16];
float[] basisPhase = new float[16];
float[] gradeProbability = new float[5];
final int[] GENERATORS = {1, 3, 5, 7};
final int DIAMOND_VERTEX_COUNT = 12;
final int VIEW_HEXANY = 0;
final int VIEW_DIAMOND = 1;
final int VIEW_SCALA = 2;
int[] diamondNumerator = new int[DIAMOND_VERTEX_COUNT];
int[] diamondDenominator = new int[DIAMOND_VERTEX_COUNT];
PVector[] diamondLattice = new PVector[DIAMOND_VERTEX_COUNT];
PVector[] diamondScreen = new PVector[DIAMOND_VERTEX_COUNT];
float[] diamondSupport = new float[DIAMOND_VERTEX_COUNT];
float[] diamondCoherence = new float[DIAMOND_VERTEX_COUNT];
float[] diamondPhase = new float[DIAMOND_VERTEX_COUNT];
final int MAX_MOS_VOICES = 64;
float[] mosPosition = new float[MAX_MOS_VOICES];
float[] mosRatio = new float[MAX_MOS_VOICES];
float[] mosActivation = new float[MAX_MOS_VOICES];
int[] mosPower = new int[MAX_MOS_VOICES];
boolean[] mosPresent = new boolean[MAX_MOS_VOICES];
final int MAX_SCALA_DEGREES = 256;
float[] scalaRatio = new float[MAX_SCALA_DEGREES];
float[] scalaCents = new float[MAX_SCALA_DEGREES];
float[] scalaProbability = new float[MAX_SCALA_DEGREES];
String[] scalaToken = new String[MAX_SCALA_DEGREES];
PVector[] scalaScreen = new PVector[MAX_SCALA_DEGREES];
int[] scalaAssignment = new int[16];
float[] pendingScalaRatio = new float[MAX_SCALA_DEGREES];
float[] pendingScalaCents = new float[MAX_SCALA_DEGREES];
String[] pendingScalaToken = new String[MAX_SCALA_DEGREES];
int[] pendingScalaAssignment = new int[16];
boolean[] pendingScalaDegreeSeen = new boolean[MAX_SCALA_DEGREES];
boolean[] pendingScalaAssignmentSeen = new boolean[16];
int scalaDegreeCount = 0;
int pendingScalaDegreeCount = 0;
int pendingScalaRevision = -1;
int activeScalaRevision = -1;
float scalaPeriod = 2;
String scalaDescription = "no Scala scale loaded";
String scalaPath = "";
boolean scalaConstantStructure = false;
int scalaIntervalClassCount = 0;
int scalaConflictingClassCount = 0;
boolean pendingScalaConstantStructure = false;
int pendingScalaIntervalClassCount = 0;
int pendingScalaConflictingClassCount = 0;
boolean pendingScalaStructureSeen = false;

int generation = 0;
int maxDepth = 32;
int seed = 23;
float shellProbability = 1;
float shellLeakage = 0;
float shellPurity = 1;
float entropy = 0;
float temperature = 0.65;
int flowSource = -1;
int flowDestination = -1;
float flowCurrent = 0;
float flowTheta = 0;
float flowBeta = 0;
float flowPhase = 0;
int flowStarted = -10000;
int phasePulseBasis = -1;
float phasePulseStrength = 0;
float phasePulseAngle = 0;
int phasePulseStarted = -10000;
int activeRevision = -1;
int pendingRevision = -1;
float pendingShellProbability = 1;
float pendingShellLeakage = 0;
float pendingShellPurity = 1;
int measuredVertex = -1;
int measurementStarted = -10000;
int selectedBasis = -1;
int selectedGrade = -1;
String selectedMotion = "—";
int mosSourceNumerator = 3;
int mosSourceDenominator = 7;
int mosTargetNumerator = 3;
int mosTargetDenominator = 7;
float mosProgress = 1;
float mosActiveVoiceCount = 7;
int instrumentGrade = -1;
int constantStructureState = -1;
String tuningFamily = "fixed";
boolean circuitTuningEnabled = true;
int pendingTuningRevision = -1;
int activeTuningRevision = -1;
int pendingTuningVertexCount = 0;
boolean dynamicTuningLabelsActive = false;
float angleX = -0.32;
float angleY = 0.55;
float dragX;
float dragY;
boolean dragging = false;
int geometryView = VIEW_HEXANY;
int hoverDiamond = -1;

void settings() {
  size(1440, 820, P2D);
  smooth(8);
}

void setup() {
  colorMode(HSB, TWO_PI, 1, 1, 1);
  textFont(createFont("Helvetica Neue", 15));
  textAlign(CENTER, CENTER);
  osc = new OscP5(this, OSC_PORT);
  probability[1] = 1;
  basisProbability[5] = 1;
  gradeProbability[2] = 1;
  initializeStellateGeometry();
  initializeDiamondGeometry();
}

void draw() {
  background(0.62, 0.26, 0.075);
  if (!dragging) angleY += 0.0014;
  if (geometryView == VIEW_HEXANY) projectLattice();
  else if (geometryView == VIEW_DIAMOND) projectDiamond();
  else projectScala();
  drawTitle();
  drawMOSNavigation();
  drawBasisLedger();
  if (geometryView == VIEW_HEXANY) {
    drawStellateEdges();
    drawEdges();
    drawFlow();
    drawPhasePulse();
    drawPoles();
    drawOuterVertices();
    drawVertices();
  } else if (geometryView == VIEW_DIAMOND) {
    updateDiamondQuantumField();
    drawDiamondEdges();
    drawDiamondVertices();
    drawDiamondLegend();
  } else {
    updateScalaQuantumField();
    drawScalaGeometry();
  }
  drawFooter();
}

void drawMOSNavigation() {
  float left = LEDGER_WIDTH + 28;
  float right = width - 30;
  float top = 91;
  float baseline = 139;
  noStroke();
  fill(0, 0, 0.10, 0.82);
  rect(left, top, right - left, 68, 9);

  textAlign(LEFT, TOP);
  fill(0, 0, 0.78);
  textSize(12);
  String gradeText = instrumentGrade < 0 ? "all grades" : instrumentGrade + ")4";
  String csText = constantStructureState < 0 ? "CS n/a" :
                  (constantStructureState == 1 ? "Constant Structure" : "CS violation");
  text("TUNING " + tuningFamily + "  " + GENERATORS[0] + "·" + GENERATORS[1] +
       "·" + GENERATORS[2] + "·" + GENERATORS[3] + "   MOS " +
       mosSourceNumerator + "/" + mosSourceDenominator + "  →  " +
       mosTargetNumerator + "/" + mosTargetDenominator + "   morph " +
       nf(mosProgress, 1, 2) + "   " + gradeText + "   " + csText,
       left + 12, top + 8);

  stroke(0, 0, 0.34, 0.9);
  strokeWeight(1);
  line(left + 14, baseline, right - 14, baseline);
  for (int voice = 0; voice < MAX_MOS_VOICES; voice++) {
    if (!mosPresent[voice]) continue;
    float x = map(mosPosition[voice], 0, 1, left + 18, right - 18);
    float gain = constrain(mosActivation[voice], 0, 1);
    float hue = (voice * 0.63) % TWO_PI;
    noStroke();
    fill(hue, 0.62, 1, 0.18 + 0.82 * gain);
    circle(x, baseline, 7 + 13 * gain);
    fill(0, 0, 0.92, 0.28 + 0.72 * gain);
    textAlign(CENTER, TOP);
    textSize(9);
    text(str(mosPower[voice]), x, baseline + 10);
  }
}

void initializeStellateGeometry() {
  basisLattice[1] = new PVector(1, 1, 1);
  basisLattice[2] = new PVector(1, -1, -1);
  basisLattice[4] = new PVector(-1, 1, -1);
  basisLattice[8] = new PVector(-1, -1, 1);
  for (int singleton : new int[]{1, 2, 4, 8}) {
    basisLattice[15 ^ singleton] = PVector.mult(basisLattice[singleton], -1);
  }
  for (int i = 0; i < 6; i++) basisLattice[MASKS[i]] = lattice[i].copy();
  basisLattice[0] = new PVector(0, 0, -1.85);
  basisLattice[15] = new PVector(0, 0, 1.85);
}

void initializeDiamondGeometry() {
  PVector[] tetrahedron = {
    new PVector(1, 1, 1), new PVector(1, -1, -1),
    new PVector(-1, 1, -1), new PVector(-1, -1, 1)
  };
  int index = 0;
  for (int numerator = 0; numerator < 4; numerator++) {
    for (int denominator = 0; denominator < 4; denominator++) {
      if (numerator == denominator) continue;
      diamondNumerator[index] = numerator;
      diamondDenominator[index] = denominator;
      diamondLattice[index] = PVector.sub(
        tetrahedron[numerator], tetrahedron[denominator]
      ).mult(0.5);
      index++;
    }
  }
}

void projectLattice() {
  float geometryWidth = width - LEDGER_WIDTH;
  float centerX = LEDGER_WIDTH + geometryWidth * 0.5;
  float radius = min(geometryWidth, height) * 0.31;
  for (int i = 0; i < 6; i++) {
    PVector p = lattice[i].copy();
    float x1 = cos(angleY) * p.x + sin(angleY) * p.z;
    float z1 = -sin(angleY) * p.x + cos(angleY) * p.z;
    float y2 = cos(angleX) * p.y - sin(angleX) * z1;
    float z2 = sin(angleX) * p.y + cos(angleX) * z1;
    float perspective = 1.0 + 0.12 * z2;
    screenPoint[i] = new PVector(
      centerX + radius * x1 * perspective,
      height * 0.52 + radius * y2 * perspective,
      z2
    );
  }
  for (int mask = 0; mask < 16; mask++) {
    PVector p = basisLattice[mask];
    float x1 = cos(angleY) * p.x + sin(angleY) * p.z;
    float z1 = -sin(angleY) * p.x + cos(angleY) * p.z;
    float y2 = cos(angleX) * p.y - sin(angleX) * z1;
    float z2 = sin(angleX) * p.y + cos(angleX) * z1;
    float perspective = 1.0 + 0.08 * z2;
    basisScreen[mask] = new PVector(
      centerX + radius * x1 * perspective,
      height * 0.52 + radius * y2 * perspective,
      z2
    );
  }
}

void projectDiamond() {
  float geometryWidth = width - LEDGER_WIDTH;
  float centerX = LEDGER_WIDTH + geometryWidth * 0.5;
  float radius = min(geometryWidth, height) * 0.235;
  for (int i = 0; i < DIAMOND_VERTEX_COUNT; i++) {
    PVector p = diamondLattice[i].copy();
    float x1 = cos(angleY) * p.x + sin(angleY) * p.z;
    float z1 = -sin(angleY) * p.x + cos(angleY) * p.z;
    float y2 = cos(angleX) * p.y - sin(angleX) * z1;
    float z2 = sin(angleX) * p.y + cos(angleX) * z1;
    float perspective = 1.0 + 0.10 * z2;
    diamondScreen[i] = new PVector(
      centerX + radius * x1 * perspective,
      height * 0.53 + radius * y2 * perspective,
      z2
    );
  }
}

void projectScala() {
  float geometryWidth = width - LEDGER_WIDTH;
  float centerX = LEDGER_WIDTH + geometryWidth * 0.5;
  float centerY = height * 0.54;
  float radius = min(geometryWidth, height) * 0.31;
  float periodCents = 1200.0 * log(max(scalaPeriod, 1.000001)) / log(2.0);
  for (int degree = 0; degree < scalaDegreeCount; degree++) {
    float turn = scalaCents[degree] / periodCents;
    float angle = -HALF_PI + TWO_PI * turn;
    scalaScreen[degree] = new PVector(
      centerX + radius * cos(angle),
      centerY + radius * sin(angle),
      0
    );
  }
}

void drawTitle() {
  fill(0, 0, 0.94);
  textAlign(LEFT, TOP);
  textSize(23);
  text("QMW COMPLETE CPS · LIVE STATE", 32, 25);
  fill(0, 0, 0.62);
  textSize(13);
  text("all 16 basis states · Pascal grades 1–4–6–4–1", 34, 58);
  textAlign(LEFT, TOP);
  fill(0, 0, 0.94);
  textSize(18);
  String geometryTitle = "ERV WILSON HEXANY · 2)4";
  if (geometryView == VIEW_DIAMOND)
    geometryTitle = "ERV WILSON TETRADIC DIAMOND · 12 DIRECTED RATIOS";
  if (geometryView == VIEW_SCALA)
    geometryTitle = "SCALA GEOMETRY · " + scalaDescription;
  text(geometryTitle, LEDGER_WIDTH + 28, 28);
  fill(0, 0, 0.58);
  textSize(12);
  String geometrySubtitle =
    "inner octahedron · exact ratios relative to |0011⟩ · click title to cycle geometry";
  if (geometryView == VIEW_DIAMOND)
    geometrySubtitle = "a/b and b/a are opposite · otonal + utonal triangles · click title to cycle";
  if (geometryView == VIEW_SCALA)
    geometrySubtitle = scalaDegreeCount + " degrees · " +
      (scalaConstantStructure ? "CONSTANT STRUCTURE" :
       "not constant structure (" + scalaConflictingClassCount + " collisions)") +
      " · live basis-state projection";
  text(geometrySubtitle, LEDGER_WIDTH + 30, 56);
  textAlign(RIGHT, TOP);
  fill(0, 0, 0.9);
  text("generation " + generation + " / " + maxDepth, width - 34, 27);
  fill(0, 0, 0.58);
  text("0)4 " + nf(basisProbability[0], 1, 3) + "   2)4 " +
       nf(shellProbability, 1, 3) + "   4)4 " + nf(basisProbability[15], 1, 3),
       width - 34, 53);
  textAlign(RIGHT, TOP);
  fill(0, 0, 0.48);
  text("leak " + nf(shellLeakage, 1, 4) + "   purity " + nf(shellPurity, 1, 4),
       width - 34, 72);
}

void drawBasisLedger() {
  float x0 = 28;
  float panelWidth = LEDGER_WIDTH - 48;
  float top = 105;
  float rowGap = 114;
  float tileW = 61;
  float tileH = 86;
  float gap = 7;

  textAlign(LEFT, TOP);
  fill(0, 0, 0.56);
  textSize(12);
  text("probability · phase · Wilson product", x0, 82);

  for (int grade = 0; grade <= 4; grade++) {
    int count = 0;
    for (int mask = 0; mask < 16; mask++) if (Integer.bitCount(mask) == grade) count++;
    float totalWidth = count * tileW + (count - 1) * gap;
    float startX = x0 + panelWidth - totalWidth;
    float y = top + grade * rowGap;

    textAlign(LEFT, CENTER);
    fill(0, 0, 0.64);
    textSize(12);
    text(grade + ")4", x0, y + tileH * 0.5 - 7);
    fill(0, 0, 0.90);
    text(nf(gradeProbability[grade], 1, 3), x0, y + tileH * 0.5 + 11);

    int column = 0;
    for (int mask = 0; mask < 16; mask++) {
      if (Integer.bitCount(mask) != grade) continue;
      drawBasisTile(mask, startX + column * (tileW + gap), y, tileW, tileH);
      column++;
    }
  }
}

void drawBasisTile(int mask, float x, float y, float w, float h) {
  float p = constrain(basisProbability[mask], 0, 1);
  float hue = wrapPhase(basisPhase[mask]);
  boolean hexany = Integer.bitCount(mask) == 2;
  boolean selected = mask == selectedBasis;
  boolean source = mask == flowSource && millis() - flowStarted < 900;
  boolean destination = mask == flowDestination && millis() - flowStarted < 900;

  noStroke();
  fill(0, 0, 0.13, 0.94);
  rect(x, y, w, h, 7);
  fill(hue, 0.46, 0.76, 0.10 + 0.72 * sqrt(p));
  rect(x + 2, y + h - 4 - (h - 8) * sqrt(p), w - 4, (h - 8) * sqrt(p), 5);

  noFill();
  if (selected) stroke(1.0, 0.82, 1, 1);
  else if (destination) stroke(2.1, 0.72, 1, 1);
  else if (source) stroke(5.45, 0.65, 1, 0.95);
  else if (hexany) stroke(0.72, 0.54, 0.90, 0.82);
  else stroke(0, 0, 0.34, 0.72);
  strokeWeight(selected ? 3 : (hexany ? 1.6 : 1));
  rect(x, y, w, h, 7);

  noStroke();
  fill(0, 0, 0.95);
  textAlign(CENTER, TOP);
  textSize(12);
  text(binary(mask, 4), x + w * 0.5, y + 8);
  fill(0, 0, 0.72);
  textSize(10);
  text("×" + productForMask(mask), x + w * 0.5, y + 29);
  fill(0, 0, 0.96);
  textSize(11);
  text(nf(p, 1, 3), x + w * 0.5, y + 49);
  fill(hue, 0.65, 1, 0.94);
  rect(x + 9, y + h - 10, w - 18, 3, 2);
}

int productForMask(int mask) {
  int product = 1;
  for (int qubit = 0; qubit < 4; qubit++) {
    if (((mask >> qubit) & 1) == 1) product *= GENERATORS[qubit];
  }
  return product;
}

float stellateTipProbability() {
  int[] outerMasks = {1, 2, 4, 8, 7, 11, 13, 14};
  float total = 0;
  for (int mask : outerMasks) total += basisProbability[mask];
  return total;
}

void drawStellateEdges() {
  int[] singleton = {1, 2, 4, 8};
  strokeWeight(1.1);
  for (int a = 0; a < 4; a++) {
    for (int b = a + 1; b < 4; b++) {
      int middle = singleton[a] | singleton[b];
      stroke(0.55, 0.46, 0.72, 0.36);
      line(basisScreen[singleton[a]].x, basisScreen[singleton[a]].y,
           basisScreen[middle].x, basisScreen[middle].y);
      line(basisScreen[middle].x, basisScreen[middle].y,
           basisScreen[singleton[b]].x, basisScreen[singleton[b]].y);

      int reciprocalA = 15 ^ singleton[a];
      int reciprocalB = 15 ^ singleton[b];
      int reciprocalMiddle = 15 ^ middle;
      stroke(5.35, 0.40, 0.76, 0.34);
      line(basisScreen[reciprocalA].x, basisScreen[reciprocalA].y,
           basisScreen[reciprocalMiddle].x, basisScreen[reciprocalMiddle].y);
      line(basisScreen[reciprocalMiddle].x, basisScreen[reciprocalMiddle].y,
           basisScreen[reciprocalB].x, basisScreen[reciprocalB].y);
    }
    stroke(1.05, 0.52, 0.94, 0.48);
    line(basisScreen[0].x, basisScreen[0].y,
         basisScreen[singleton[a]].x, basisScreen[singleton[a]].y);
    stroke(4.75, 0.48, 0.94, 0.48);
    int reciprocal = 15 ^ singleton[a];
    line(basisScreen[reciprocal].x, basisScreen[reciprocal].y,
         basisScreen[15].x, basisScreen[15].y);
  }
}

void drawEdges() {
  strokeWeight(1.2);
  for (int i = 0; i < 6; i++) {
    for (int j = i + 1; j < 6; j++) {
      if ((MASKS[i] ^ MASKS[j]) == 15) continue;
      float coupling = edgeCoupling[i][j];
      stroke(coupling > 0 ? 3.45 : 0, coupling > 0 ? 0.42 : 0,
             coupling > 0 ? 0.72 : 0.38, 0.42 + 0.32 * coupling);
      strokeWeight(1.2 + 2.5 * coupling);
      line(screenPoint[i].x, screenPoint[i].y, screenPoint[j].x, screenPoint[j].y);
    }
  }
}

void drawFlow() {
  if (flowSource < 0 || flowSource > 15 || flowDestination < 0 || flowDestination > 15) return;
  float age = (millis() - flowStarted) / 900.0;
  if (age > 1) return;
  PVector a = basisScreen[flowSource];
  PVector b = basisScreen[flowDestination];
  float envelope = sin(PI * constrain(age, 0, 1));
  float hue = wrapPhase(flowPhase);
  stroke(hue, 0.76, 1, 0.35 + 0.65 * envelope);
  strokeWeight(2 + 16 * sqrt(max(0, flowCurrent)) * envelope);
  line(a.x, a.y, b.x, b.y);
  float travel = constrain(age * 1.45, 0, 1);
  float px = lerp(a.x, b.x, travel);
  float py = lerp(a.y, b.y, travel);
  noStroke();
  fill(hue, 0.45, 1, 0.95);
  circle(px, py, 11 + 24 * sqrt(max(0, flowCurrent)));
  drawArrow(a, b, hue, envelope);
}

void drawPhasePulse() {
  if (phasePulseBasis < 0 || phasePulseBasis > 15) return;
  float age = (millis() - phasePulseStarted) / 700.0;
  if (age > 1) return;
  PVector p = basisScreen[phasePulseBasis];
  float envelope = sin(PI * constrain(age, 0, 1));
  float radius = 34 + 90 * sqrt(max(0, phasePulseStrength)) * envelope;
  noFill();
  stroke(wrapPhase(phasePulseAngle), 0.72, 1, 0.85 * envelope);
  strokeWeight(2 + 5 * envelope);
  circle(p.x, p.y, radius);
}

void drawOuterVertices() {
  int[] outerMasks = {1, 2, 4, 8, 7, 11, 13, 14};
  for (int mask : outerMasks) {
    PVector p = basisScreen[mask];
    float value = basisProbability[mask];
    float radius = 17 + 58 * sqrt(max(0, value));
    float hue = wrapPhase(basisPhase[mask]);
    boolean harmonic = Integer.bitCount(mask) == 1;
    noStroke();
    fill(hue, 0.50, 0.90, 0.10 + 0.55 * sqrt(max(0, value)));
    circle(p.x, p.y, radius + 24);
    stroke(harmonic ? 0.55 : 5.35, 0.45, 0.88, 0.78);
    strokeWeight(1.4);
    fill(hue, 0.40, 0.78, 0.35 + 0.55 * sqrt(max(0, value)));
    circle(p.x, p.y, radius);
    noStroke();
    fill(0, 0, 0.94, 0.94);
    textAlign(CENTER, CENTER);
    textSize(13);
    text(stellateLabel(mask), p.x, p.y - 2);
    textSize(10);
    text("|" + binary(mask, 4) + "⟩", p.x, p.y + 13);
    if (value > 0.0001) {
      textSize(10);
      text(nf(value, 1, 3), p.x, p.y + radius * 0.57 + 11);
    }
  }
}

void drawPoles() {
  int[] poles = {0, 15};
  String[] labels = {"0)4 · 1", "4)4 · 105"};
  for (int i = 0; i < 2; i++) {
    int mask = poles[i];
    PVector p = basisScreen[mask];
    float value = basisProbability[mask];
    float radius = 24 + 70 * sqrt(max(0, value));
    float hue = wrapPhase(basisPhase[mask]);
    noStroke();
    fill(hue, 0.38, 1, 0.13 + 0.58 * sqrt(max(0, value)));
    circle(p.x, p.y, radius + 30);
    stroke(i == 0 ? 1.05 : 4.75, 0.55, 1, 0.9);
    strokeWeight(2.2);
    fill(hue, 0.42, 0.88, 0.62 + 0.30 * sqrt(max(0, value)));
    circle(p.x, p.y, radius);
    noStroke();
    fill(0, 0, 0.06, 0.95);
    textAlign(CENTER, CENTER);
    textSize(13);
    text(labels[i], p.x, p.y - 3);
    textSize(10);
    text("|" + binary(mask, 4) + "⟩  " + nf(value, 1, 3), p.x, p.y + 14);
  }
}

String stellateLabel(int mask) {
  if (Integer.bitCount(mask) == 1) {
    return str(GENERATORS[bitIndex(mask)]);
  }
  int missing = 15 ^ mask;
  return "/" + GENERATORS[bitIndex(missing)];
}

int bitIndex(int singleton) {
  for (int i = 0; i < 4; i++) if (singleton == (1 << i)) return i;
  return 0;
}

void drawArrow(PVector a, PVector b, float hue, float envelope) {
  PVector direction = PVector.sub(b, a);
  direction.normalize();
  PVector normal = new PVector(-direction.y, direction.x);
  PVector tip = PVector.lerp(a, b, 0.70);
  PVector back = PVector.sub(tip, PVector.mult(direction, 18));
  noStroke();
  fill(hue, 0.65, 1, 0.3 + 0.7 * envelope);
  triangle(tip.x, tip.y, back.x + normal.x * 8, back.y + normal.y * 8,
           back.x - normal.x * 8, back.y - normal.y * 8);
}

void drawVertices() {
  Integer[] order = {0, 1, 2, 3, 4, 5};
  for (int pass = 0; pass < 6; pass++) {
    int deepest = pass;
    for (int j = pass + 1; j < 6; j++)
      if (screenPoint[order[j]].z < screenPoint[order[deepest]].z) deepest = j;
    int temp = order[pass]; order[pass] = order[deepest]; order[deepest] = temp;
  }
  for (int k = 0; k < 6; k++) {
    int i = order[k];
    PVector p = screenPoint[i];
    float vertexProbability = probability[i];
    float vertexPhase = basisPhase[MASKS[i]];
    float radius = 30 + 78 * sqrt(max(0, vertexProbability));
    float hue = wrapPhase(vertexPhase);
    noStroke();
    fill(hue, 0.45, 0.88, 0.08 + 0.30 * activation[i]);
    circle(p.x, p.y, radius + 28 + 34 * activation[i]);
    if (i == measuredVertex && millis() - measurementStarted < 1200) {
      noFill();
      stroke(1.05, 0.75, 1, 0.9);
      strokeWeight(3.5);
      circle(p.x, p.y, radius + 38);
      noStroke();
    }
    fill(hue, 0.62, 0.92, 0.90);
    circle(p.x, p.y, radius);
    noFill();
    stroke(hue, 0.25, 1, 0.25 + 0.7 * phaseCoherence[i]);
    strokeWeight(1 + 4 * phaseCoherence[i]);
    circle(p.x, p.y, radius + 8);
    noStroke();
    fill(0, 0, 0.08, 0.92);
    textAlign(CENTER, CENTER);
    textSize(16);
    text(RATIOS[i], p.x, p.y - 4);
    textSize(11);
    text(FACTORS[i] + "  |" + binary(MASKS[i], 4) + "⟩", p.x, p.y + 15);
    fill(0, 0, 0.90);
    textSize(12);
    text(nf(vertexProbability, 1, 3), p.x, p.y + radius * 0.58 + 14);
  }
}

void updateDiamondQuantumField() {
  for (int vertex = 0; vertex < DIAMOND_VERTEX_COUNT; vertex++) {
    int numerator = diamondNumerator[vertex];
    int denominator = diamondDenominator[vertex];
    int numeratorBit = 1 << numerator;
    int denominatorBit = 1 << denominator;
    float real = 0;
    float imaginary = 0;
    float support = 0;
    for (int source = 0; source < 16; source++) {
      if ((source & denominatorBit) == 0 || (source & numeratorBit) != 0) continue;
      int destination = source ^ denominatorBit ^ numeratorBit;
      float magnitude = sqrt(max(0, basisProbability[source] * basisProbability[destination]));
      float phaseDifference = basisPhase[destination] - basisPhase[source];
      real += magnitude * cos(phaseDifference);
      imaginary += magnitude * sin(phaseDifference);
      support += basisProbability[source] + basisProbability[destination];
    }
    diamondSupport[vertex] = constrain(support, 0, 1);
    diamondCoherence[vertex] = constrain(2.0 * sqrt(real * real + imaginary * imaginary), 0, 1);
    diamondPhase[vertex] = atan2(imaginary, real);
  }
}

void drawDiamondEdges() {
  for (int left = 0; left < DIAMOND_VERTEX_COUNT; left++) {
    for (int right = left + 1; right < DIAMOND_VERTEX_COUNT; right++) {
      boolean sharedNumerator = diamondNumerator[left] == diamondNumerator[right];
      boolean sharedDenominator = diamondDenominator[left] == diamondDenominator[right];
      if (!sharedNumerator && !sharedDenominator) continue;
      float activity = sqrt(max(0, diamondSupport[left] * diamondSupport[right]));
      if (sharedDenominator) stroke(3.55, 0.48, 0.88, 0.22 + 0.40 * activity);
      else stroke(5.35, 0.45, 0.90, 0.22 + 0.40 * activity);
      strokeWeight(1.0 + 2.4 * activity);
      line(
        diamondScreen[left].x, diamondScreen[left].y,
        diamondScreen[right].x, diamondScreen[right].y
      );
    }
  }
}

void drawDiamondVertices() {
  hoverDiamond = -1;
  float nearest = 100000;
  for (int i = 0; i < DIAMOND_VERTEX_COUNT; i++) {
    float distance = dist(mouseX, mouseY, diamondScreen[i].x, diamondScreen[i].y);
    if (distance < nearest && distance < 34) {
      nearest = distance;
      hoverDiamond = i;
    }
  }

  Integer[] order = new Integer[DIAMOND_VERTEX_COUNT];
  for (int i = 0; i < DIAMOND_VERTEX_COUNT; i++) order[i] = i;
  for (int pass = 0; pass < DIAMOND_VERTEX_COUNT; pass++) {
    int deepest = pass;
    for (int j = pass + 1; j < DIAMOND_VERTEX_COUNT; j++)
      if (diamondScreen[order[j]].z < diamondScreen[order[deepest]].z) deepest = j;
    int temporary = order[pass]; order[pass] = order[deepest]; order[deepest] = temporary;
  }

  int active = activeDiamondTransition();
  for (int position = 0; position < DIAMOND_VERTEX_COUNT; position++) {
    int i = order[position];
    PVector point = diamondScreen[i];
    float support = diamondSupport[i];
    float coherence = diamondCoherence[i];
    float hue = wrapPhase(diamondPhase[i]);
    float radius = 25 + 25 * sqrt(support) + 16 * coherence;

    noStroke();
    fill(hue, 0.48, 0.92, 0.08 + 0.28 * support + 0.34 * coherence);
    circle(point.x, point.y, radius + 24 * coherence);
    fill(hue, 0.38 + 0.30 * coherence, 0.82, 0.72 + 0.24 * support);
    circle(point.x, point.y, radius);
    noFill();
    if (i == active) stroke(1.0, 0.88, 1, 1);
    else if (i == hoverDiamond) stroke(0, 0, 1, 0.92);
    else stroke(0, 0, 0.56, 0.62);
    strokeWeight(i == active ? 3.5 : (i == hoverDiamond ? 2.2 : 1.0));
    circle(point.x, point.y, radius + 5);

    noStroke();
    fill(0, 0, 0.06, 0.96);
    textAlign(CENTER, CENTER);
    textSize(13);
    text(rawDiamondRatio(i), point.x, point.y - 4);
    fill(0, 0, 0.16, 0.86);
    textSize(9);
    text("→" + foldedDiamondRatio(i), point.x, point.y + 12);
  }
}

void drawDiamondLegend() {
  float left = LEDGER_WIDTH + 30;
  textAlign(LEFT, TOP);
  textSize(11);
  fill(0, 0, 0.65);
  text("shared denominator: harmonic / otonal triangles", left, 174);
  text("shared numerator: subharmonic / utonal triangles", left, 192);
  if (hoverDiamond >= 0) {
    int numerator = diamondNumerator[hoverDiamond];
    int denominator = diamondDenominator[hoverDiamond];
    fill(0, 0, 0.92);
    text(
      "selected " + rawDiamondRatio(hoverDiamond) + "  octave-folded " +
      foldedDiamondRatio(hoverDiamond) + "  support " +
      nf(diamondSupport[hoverDiamond], 1, 3) + "  transition coherence " +
      nf(diamondCoherence[hoverDiamond], 1, 3) + "  q" + denominator + "→q" + numerator,
      left, height - 82
    );
  }
}

void updateScalaQuantumField() {
  for (int degree = 0; degree < scalaDegreeCount; degree++) scalaProbability[degree] = 0;
  for (int basis = 0; basis < 16; basis++) {
    int degree = scalaAssignment[basis];
    if (degree >= 0 && degree < scalaDegreeCount)
      scalaProbability[degree] += basisProbability[basis];
  }
}

void drawScalaGeometry() {
  if (scalaDegreeCount <= 0) {
    fill(0, 0, 0.75);
    textAlign(CENTER, CENTER);
    textSize(18);
    text("Load a .scl file from Max to reveal its geometry", (LEDGER_WIDTH + width) * 0.5, height * 0.52);
    return;
  }

  // The scale itself is a circular graph in its declared period.
  for (int degree = 0; degree < scalaDegreeCount; degree++) {
    int next = (degree + 1) % scalaDegreeCount;
    stroke(0.62, 0.32, 0.76, 0.58);
    strokeWeight(1.4);
    line(scalaScreen[degree].x, scalaScreen[degree].y,
         scalaScreen[next].x, scalaScreen[next].y);
  }

  // Project edges of the four-dimensional Boolean cube onto Scala degrees.
  for (int basis = 0; basis < 16; basis++) {
    for (int qubit = 0; qubit < 4; qubit++) {
      int neighbor = basis ^ (1 << qubit);
      if (neighbor <= basis) continue;
      int left = scalaAssignment[basis];
      int right = scalaAssignment[neighbor];
      if (left < 0 || right < 0 || left >= scalaDegreeCount || right >= scalaDegreeCount || left == right) continue;
      float activity = sqrt(max(0, basisProbability[basis] * basisProbability[neighbor]));
      stroke((qubit * 1.37) % TWO_PI, 0.54, 0.92, 0.08 + 0.52 * activity);
      strokeWeight(0.7 + 4.2 * activity);
      line(scalaScreen[left].x, scalaScreen[left].y,
           scalaScreen[right].x, scalaScreen[right].y);
    }
  }

  if (flowSource >= 0 && flowDestination >= 0 && millis() - flowStarted < 900) {
    int sourceDegree = scalaAssignment[flowSource];
    int destinationDegree = scalaAssignment[flowDestination];
    if (sourceDegree >= 0 && destinationDegree >= 0 &&
        sourceDegree < scalaDegreeCount && destinationDegree < scalaDegreeCount) {
      stroke(1.0, 0.88, 1, 0.95);
      strokeWeight(3.0 + 8.0 * constrain(flowCurrent, 0, 1));
      line(scalaScreen[sourceDegree].x, scalaScreen[sourceDegree].y,
           scalaScreen[destinationDegree].x, scalaScreen[destinationDegree].y);
    }
  }

  for (int degree = 0; degree < scalaDegreeCount; degree++) {
    float energy = constrain(scalaProbability[degree], 0, 1);
    float hue = (scalaCents[degree] / max(1, 1200.0 * log(scalaPeriod) / log(2.0))) * TWO_PI;
    float diameter = 15 + 46 * sqrt(energy);
    noStroke();
    fill(hue, 0.58, 0.95, 0.18 + 0.76 * sqrt(energy));
    circle(scalaScreen[degree].x, scalaScreen[degree].y, diameter);
    noFill();
    stroke(hue, 0.42, 1, 0.72);
    strokeWeight(1.2 + 2.0 * sqrt(energy));
    circle(scalaScreen[degree].x, scalaScreen[degree].y, diameter + 5);
    noStroke();
    fill(0, 0, 0.96);
    textAlign(CENTER, CENTER);
    textSize(scalaDegreeCount > 24 ? 8 : 10);
    String label = scalaToken[degree] == null ? str(degree) : scalaToken[degree];
    if (label.length() > 10) label = label.substring(0, 9) + "…";
    text(label, scalaScreen[degree].x, scalaScreen[degree].y);
  }

  fill(0, 0, 0.68);
  textAlign(LEFT, TOP);
  textSize(11);
  text("ring: Scala period order · chords: one-qubit adjacency · vertex size: assigned probability",
       LEDGER_WIDTH + 30, 174);
  text("interval classes: " + scalaIntervalClassCount +
       " · Wilson CS test: " + (scalaConstantStructure ? "passes" : "fails"),
       LEDGER_WIDTH + 30, 192);
  if (scalaPath.length() > 0)
    text(scalaPath, LEDGER_WIDTH + 30, 210);
}

int activeDiamondTransition() {
  if (flowSource < 0 || flowDestination < 0 || millis() - flowStarted >= 900) return -1;
  int changed = flowSource ^ flowDestination;
  if (Integer.bitCount(changed) != 2 || Integer.bitCount(flowSource) != Integer.bitCount(flowDestination)) return -1;
  int numerator = -1;
  int denominator = -1;
  for (int qubit = 0; qubit < 4; qubit++) {
    int sourceBit = (flowSource >> qubit) & 1;
    int destinationBit = (flowDestination >> qubit) & 1;
    if (sourceBit == 0 && destinationBit == 1) numerator = qubit;
    if (sourceBit == 1 && destinationBit == 0) denominator = qubit;
  }
  for (int i = 0; i < DIAMOND_VERTEX_COUNT; i++) {
    if (diamondNumerator[i] == numerator && diamondDenominator[i] == denominator) return i;
  }
  return -1;
}

String rawDiamondRatio(int index) {
  return GENERATORS[diamondNumerator[index]] + "/" + GENERATORS[diamondDenominator[index]];
}

String foldedDiamondRatio(int index) {
  int numerator = GENERATORS[diamondNumerator[index]];
  int denominator = GENERATORS[diamondDenominator[index]];
  int divisor = gcdInt(numerator, denominator);
  numerator /= divisor;
  denominator /= divisor;
  while (numerator < denominator) numerator *= 2;
  while (numerator >= 2 * denominator) denominator *= 2;
  divisor = gcdInt(numerator, denominator);
  return (numerator / divisor) + "/" + (denominator / divisor);
}

int gcdInt(int left, int right) {
  left = abs(left);
  right = abs(right);
  while (right != 0) {
    int remainder = left % right;
    left = right;
    right = remainder;
  }
  return max(1, left);
}

void drawFooter() {
  textAlign(LEFT, BOTTOM);
  fill(0, 0, 0.62);
  textSize(13);
  text("temperature " + nf(temperature, 1, 2) + "   seed " + seed +
       "   revision " + activeRevision, 34, height - 25);
  if (selectedBasis >= 0) {
    fill(0, 0, 0.88);
    text("selected |" + binary(selectedBasis, 4) + "⟩   grade " + selectedGrade +
         ")4   " + selectedMotion, 34, height - 48);
  }
  textAlign(RIGHT, BOTTOM);
  if (flowSource >= 0) {
    fill(0, 0, 0.9);
    text("|" + binary(flowSource, 4) + "⟩  →  |" + binary(flowDestination, 4) +
         "⟩   current " + nf(flowCurrent, 1, 4) +
         "   θ " + nf(flowTheta, 1, 3), width - 34, height - 25);
  }
}

float wrapPhase(float value) {
  float wrapped = value % TWO_PI;
  if (wrapped < 0) wrapped += TWO_PI;
  return wrapped;
}

int maskIndex(int mask) {
  for (int i = 0; i < MASKS.length; i++) if (MASKS[i] == mask) return i;
  return -1;
}

void oscEvent(OscMessage message) {
  try {
  if (message.checkAddrPattern("/qmw/wilson/tuning/begin")) {
    pendingTuningRevision = message.get(0).intValue();
    pendingTuningVertexCount = message.get(4).intValue();
    for (int i = 0; i < 6; i++) {
      pendingTuningSeen[i] = false;
      pendingTuningRatios[i] = "";
      pendingTuningFactors[i] = "";
    }
  } else if (message.checkAddrPattern("/qmw/wilson/tuning/vertex")) {
    if (message.get(0).intValue() != pendingTuningRevision) return;
    int index = maskIndex(message.get(2).intValue());
    if (index >= 0) {
      pendingTuningFactors[index] = message.get(3).intValue() + "·" + message.get(4).intValue();
      pendingTuningRatios[index] = message.get(6).intValue() + "/" + message.get(7).intValue();
      pendingTuningSeen[index] = true;
    }
  } else if (message.checkAddrPattern("/qmw/wilson/tuning/end")) {
    int revision = message.get(0).intValue();
    int count = message.get(2).intValue();
    if (revision != pendingTuningRevision || count != 6 || pendingTuningVertexCount != 6) return;
    for (int i = 0; i < 6; i++) if (!pendingTuningSeen[i]) return;
    for (int i = 0; i < 6; i++) {
      FACTORS[i] = pendingTuningFactors[i];
      RATIOS[i] = pendingTuningRatios[i];
    }
    activeTuningRevision = revision;
    dynamicTuningLabelsActive = true;
  } else if (message.checkAddrPattern("/qmw/wilson/tuning/frame")) {
    generation = message.get(0).intValue();
    tuningFamily = message.get(1).stringValue();
    circuitTuningEnabled = message.get(2).intValue() != 0;
    int separator = 10;
    while (separator < message.arguments().length && message.get(separator).intValue() != -1) {
      separator++;
    }
    if (separator + 4 < message.arguments().length) {
      for (int qubit = 0; qubit < 4; qubit++) {
        GENERATORS[qubit] = message.get(separator + 1 + qubit).intValue();
      }
    }
    if (!circuitTuningEnabled) tuningFamily += " (bypass)";
  } else if (message.checkAddrPattern("/qmw/wilson/tuning/scala/begin")) {
    pendingScalaRevision = message.get(0).intValue();
    pendingScalaDegreeCount = min(MAX_SCALA_DEGREES, message.get(3).intValue());
    scalaDescription = message.get(2).stringValue();
    scalaPeriod = oscNumber(message, 4);
    scalaPath = message.get(5).stringValue();
    for (int degree = 0; degree < MAX_SCALA_DEGREES; degree++)
      pendingScalaDegreeSeen[degree] = false;
    for (int basis = 0; basis < 16; basis++)
      pendingScalaAssignmentSeen[basis] = false;
    pendingScalaStructureSeen = false;
  } else if (message.checkAddrPattern("/qmw/wilson/tuning/scala/degree")) {
    if (message.get(0).intValue() != pendingScalaRevision) return;
    int degree = message.get(1).intValue();
    if (degree >= 0 && degree < pendingScalaDegreeCount) {
      pendingScalaRatio[degree] = oscNumber(message, 2);
      pendingScalaCents[degree] = oscNumber(message, 3);
      pendingScalaToken[degree] = message.get(4).stringValue();
      pendingScalaDegreeSeen[degree] = true;
    }
  } else if (message.checkAddrPattern("/qmw/wilson/tuning/scala/assignment")) {
    if (message.get(0).intValue() != pendingScalaRevision) return;
    int basis = message.get(1).intValue();
    if (basis >= 0 && basis < 16) {
      pendingScalaAssignment[basis] = message.get(2).intValue();
      pendingScalaAssignmentSeen[basis] = true;
    }
  } else if (message.checkAddrPattern("/qmw/wilson/tuning/scala/constant-structure")) {
    if (message.get(0).intValue() != pendingScalaRevision) return;
    pendingScalaConstantStructure = message.get(1).intValue() != 0;
    pendingScalaIntervalClassCount = message.get(2).intValue();
    pendingScalaConflictingClassCount = message.get(3).intValue();
    pendingScalaStructureSeen = true;
  } else if (message.checkAddrPattern("/qmw/wilson/tuning/scala/end")) {
    int revision = message.get(0).intValue();
    int degreeCount = message.get(1).intValue();
    if (revision != pendingScalaRevision || degreeCount != pendingScalaDegreeCount) return;
    for (int degree = 0; degree < degreeCount; degree++)
      if (!pendingScalaDegreeSeen[degree]) return;
    for (int basis = 0; basis < 16; basis++)
      if (!pendingScalaAssignmentSeen[basis]) return;
    if (!pendingScalaStructureSeen) return;
    scalaDegreeCount = degreeCount;
    for (int degree = 0; degree < degreeCount; degree++) {
      scalaRatio[degree] = pendingScalaRatio[degree];
      scalaCents[degree] = pendingScalaCents[degree];
      scalaToken[degree] = pendingScalaToken[degree];
    }
    for (int basis = 0; basis < 16; basis++)
      scalaAssignment[basis] = pendingScalaAssignment[basis];
    scalaConstantStructure = pendingScalaConstantStructure;
    scalaIntervalClassCount = pendingScalaIntervalClassCount;
    scalaConflictingClassCount = pendingScalaConflictingClassCount;
    activeScalaRevision = revision;
    geometryView = VIEW_SCALA;
  } else if (message.checkAddrPattern("/qmw/wilson/navigation/frame")) {
    generation = message.get(0).intValue();
    mosSourceNumerator = message.get(1).intValue();
    mosSourceDenominator = message.get(2).intValue();
    mosTargetNumerator = message.get(3).intValue();
    mosTargetDenominator = message.get(4).intValue();
    mosProgress = oscNumber(message, 5);
    mosActiveVoiceCount = oscNumber(message, 6);
    instrumentGrade = message.get(7).intValue();
    constantStructureState = message.get(8).intValue();
    for (int voice = 0; voice < MAX_MOS_VOICES; voice++) mosPresent[voice] = false;
  } else if (message.checkAddrPattern("/qmw/wilson/navigation/voice")) {
    int voice = message.get(1).intValue();
    if (voice >= 0 && voice < MAX_MOS_VOICES) {
      mosPresent[voice] = true;
      mosPower[voice] = message.get(2).intValue();
      mosPosition[voice] = oscNumber(message, 3);
      mosRatio[voice] = oscNumber(message, 4);
      mosActivation[voice] = oscNumber(message, 5);
    }
  } else if (message.checkAddrPattern("/qmw/wilson/navigation/end")) {
    // Atomic packet terminator: state is already staged by frame + voice packets.
  } else if (message.checkAddrPattern("/qmw/wilson/cps/definition")) {
    maxDepth = max(maxDepth, 256);
  } else if (message.checkAddrPattern("/qmw/wilson/state16")) {
    generation = message.get(0).intValue();
    for (int mask = 0; mask < 16; mask++) {
      basisProbability[mask] = oscNumber(message, 1 + mask);
      basisPhase[mask] = oscNumber(message, 17 + mask);
    }
    for (int grade = 0; grade < 5; grade++) {
      gradeProbability[grade] = oscNumber(message, 33 + grade);
    }
    for (int i = 0; i < 6; i++) probability[i] = basisProbability[MASKS[i]];
  } else if (message.checkAddrPattern("/qmw/wilson/pascal_step")) {
    generation = message.get(0).intValue();
    selectedBasis = message.get(1).intValue();
    selectedGrade = message.get(2).intValue();
    selectedMotion = message.get(3).stringValue();
    for (int grade = 0; grade < 5; grade++) {
      gradeProbability[grade] = oscNumber(message, 4 + grade);
    }
  } else if (message.checkAddrPattern("/qmw/wilson/cps/edge")) {
    int source = message.get(1).intValue();
    int destination = message.get(2).intValue();
    if (source >= 0 && source < 6 && destination >= 0 && destination < 6) {
      int i = maskIndex(CPS_INDEX_MASKS[source]);
      int j = maskIndex(CPS_INDEX_MASKS[destination]);
      if (i >= 0 && j >= 0) {
        edgeCoupling[i][j] = oscNumber(message, 7);
        edgeCoupling[j][i] = edgeCoupling[i][j];
      }
    }
  } else if (message.checkAddrPattern("/qmw/wilson/cps/frame")) {
    pendingRevision = message.get(0).intValue();
    generation = message.get(1).intValue();
    pendingShellProbability = oscNumber(message, 3);
    pendingShellLeakage = oscNumber(message, 4);
    pendingShellPurity = oscNumber(message, 5);
    for (int i = 0; i < 6; i++) {
      pendingProbability[i] = 0;
      pendingPhase[i] = 0;
      pendingActivation[i] = 0;
      pendingCoherence[i] = 0;
    }
  } else if (message.checkAddrPattern("/qmw/wilson/cps/vertex")) {
    if (message.get(0).intValue() != pendingRevision) return;
    int basisMask = message.get(2).intValue();
    int index = maskIndex(basisMask);
    if (index >= 0) {
      if (!dynamicTuningLabelsActive) {
        FACTORS[index] = message.get(3).stringValue().replace(",", "·");
        RATIOS[index] = message.get(4).intValue() + "/" + message.get(5).intValue();
      }
      pendingProbability[index] = oscNumber(message, 8);
      pendingActivation[index] = oscNumber(message, 9);
      pendingPhase[index] = oscNumber(message, 10);
      pendingCoherence[index] = oscNumber(message, 11);
    }
  } else if (message.checkAddrPattern("/qmw/wilson/cps/end")) {
    int revision = message.get(0).intValue();
    if (revision != pendingRevision) return;
    activeRevision = revision;
    shellProbability = pendingShellProbability;
    shellLeakage = pendingShellLeakage;
    shellPurity = pendingShellPurity;
    for (int i = 0; i < 6; i++) {
      probability[i] = pendingProbability[i];
      activation[i] = pendingActivation[i];
      phase[i] = pendingPhase[i];
      phaseCoherence[i] = pendingCoherence[i];
      basisProbability[MASKS[i]] = probability[i] * shellProbability;
      basisPhase[MASKS[i]] = phase[i];
    }
  } else if (message.checkAddrPattern("/qmw/wilson/cps/flow")) {
    generation = message.get(1).intValue();
    flowSource = message.get(4).intValue();
    flowDestination = message.get(5).intValue();
    flowCurrent = oscNumber(message, 7);
    flowTheta = oscNumber(message, 8);
    flowBeta = oscNumber(message, 9);
    flowPhase = oscNumber(message, 10);
    flowStarted = millis();
  } else if (message.checkAddrPattern("/qmw/wilson/cps/measurement")) {
    int cpsIndex = message.get(2).intValue();
    measuredVertex = (cpsIndex >= 0 && cpsIndex < 6) ? maskIndex(CPS_INDEX_MASKS[cpsIndex]) : -1;
    measurementStarted = millis();
  } else if (message.checkAddrPattern("/qmw/wilson/cps/status")) {
    entropy = oscNumber(message, 5);
    temperature = oscNumber(message, 6);
  } else if (message.checkAddrPattern("/qmw/wilson/frame")) {
    generation = message.get(0).intValue();
    shellProbability = oscNumber(message, 1);
    entropy = oscNumber(message, 2);
    temperature = oscNumber(message, 3);
    maxDepth = message.get(4).intValue();
    seed = message.get(5).intValue();
  } else if (message.checkAddrPattern("/qmw/wilson/vertex")) {
    int basisMask = message.get(1).intValue();
    int index = maskIndex(basisMask);
    if (index >= 0) {
      probability[index] = oscNumber(message, 4);
      phase[index] = oscNumber(message, 5);
      basisProbability[basisMask] = probability[index];
      basisPhase[basisMask] = phase[index];
    }
  } else if (message.checkAddrPattern("/qmw/wilson/basis")) {
    int basisMask = message.get(1).intValue();
    if (basisMask >= 0 && basisMask < 16) {
      basisProbability[basisMask] = oscNumber(message, 3);
      basisPhase[basisMask] = oscNumber(message, 4);
    }
  } else if (message.checkAddrPattern("/qmw/wilson/flow")) {
    generation = message.get(0).intValue();
    flowSource = message.get(1).intValue();
    flowDestination = message.get(2).intValue();
    flowCurrent = oscNumber(message, 3);
    flowTheta = oscNumber(message, 4);
    flowBeta = oscNumber(message, 5);
    flowPhase = oscNumber(message, 6);
    flowStarted = millis();
  } else if (message.checkAddrPattern("/qmw/wilson/phase")) {
    generation = message.get(0).intValue();
    phasePulseBasis = message.get(1).intValue();
    phasePulseStrength = oscNumber(message, 2);
    phasePulseAngle = oscNumber(message, 3);
    phasePulseStarted = millis();
  }
  } catch (Exception error) {
    println("OSC parse error " + message.addrPattern() + " " + message.typetag());
    error.printStackTrace();
  }
}

float oscNumber(OscMessage message, int index) {
  char type = message.typetag().charAt(index);
  if (type == 'i') return message.get(index).intValue();
  return message.get(index).floatValue();
}

void mousePressed() {
  if (mouseX > LEDGER_WIDTH && mouseY < 82) {
    geometryView = (geometryView + 1) % 3;
    dragging = false;
    return;
  }
  dragging = true;
  dragX = mouseX;
  dragY = mouseY;
}

void mouseDragged() {
  angleY += (mouseX - dragX) * 0.009;
  angleX += (mouseY - dragY) * 0.009;
  dragX = mouseX;
  dragY = mouseY;
}

void mouseReleased() {
  dragging = false;
}

void keyPressed() {
  if (key == 'd' || key == 'D') geometryView = VIEW_DIAMOND;
  if (key == 'h' || key == 'H') geometryView = VIEW_HEXANY;
  if (key == 's' || key == 'S') geometryView = VIEW_SCALA;
}
