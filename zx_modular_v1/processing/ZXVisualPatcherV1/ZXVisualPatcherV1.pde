/**
 * QMW ZX Visual Patcher v1
 *
 * A diagram-first Processing frontend for the PennyLane / PyZX / Max / Rack
 * system. The canvas contains ZX and ZXH objects: Z spiders, X spiders,
 * Hadamard boxes/edges, multi-leg H-boxes, boundaries, and wires.
 *
 * OSC input:
 *   UDP 7497
 *   /qmw/zx/fader <int control-id> <float 0..1>
 *
 * Interaction:
 *   drag                  move a node
 *   shift-click           select multiple nodes
 *   Left/Right arrows     change selected spider phase
 *   Z / X / H / B         add spider, Hadamard, or boundary
 *   N                     add a CNOT expanded as Z-control / X-target
 *   J, then I/X/Y/Z       type a four-qubit Pauli gadget; Return creates it
 *   M                     cycle ZX / CNOT ladder / balanced tree views
 *   E                     Euler-decompose a selected one-wire ZX chain
 *   C, then two clicks    connect nodes
 *   Command-C / Command-V copy and paste the selected subgraph
 *   F                     fuse two selected like-colored spiders
 *   I / P / K             identity / pi-copy / state-copy
 *   A / O / G             bialgebra / Hopf / color change
 *   w / Shift-W           local complementation / pivot
 *   Y / U / T             H-box / absorb / compact Toffoli
 *   V                     add a discard terminal
 *   D                     open/refresh density inspector
 *   Q                     load a four-qubit mixed-state discard-ZX example
 *   1..8                  create GHZ state with that many outputs
 *   L                     enter a GHZ output count from 1 to 64
 *   0                     open circuit preset library
 *   Return                commit the inspected density to the QMW engine
 *   delete                remove selected nodes
 *   S                     save zx_graph.json
 *   R                     restore the demonstration graph
 */

import oscP5.*;
import netP5.*;
import processing.event.MouseEvent;

final int OSC_PORT = 7497;
final int MAX_PORT = 7496;
final int RACK_PORT = 7000;
final int SUPERCOLLIDER_PORT = 57120;
final int PYTHON_VERIFIER_PORT = 7499;

OscP5 oscP5;
NetAddress maxTarget;
NetAddress rackTarget;
NetAddress superColliderTarget;
NetAddress pythonVerifierTarget;
ArrayList<ZXNode> nodes = new ArrayList<ZXNode>();
ArrayList<ZXEdge> edges = new ArrayList<ZXEdge>();
ArrayList<ZXClipboardNode> clipboardNodes = new ArrayList<ZXClipboardNode>();
ArrayList<ZXClipboardEdge> clipboardEdges = new ArrayList<ZXClipboardEdge>();
ArrayList<ZXNode> pendingRewriteNodes = new ArrayList<ZXNode>();
ArrayList<ZXEdge> pendingRewriteEdges = new ArrayList<ZXEdge>();

float[] quantumControl = {0.0, 0.5, 0.0, 0.0, 0.5, 1.0};
int lastOscMillis = -100000;
int nextNodeId = 1;

ZXNode dragNode = null;
ZXNode connectFrom = null;
float dragOffsetX = 0;
float dragOffsetY = 0;
boolean connectMode = false;
boolean shiftDown = false;
String statusText = "drag the diagram · press C to patch";
String rewriteFeedback = "";
boolean rewriteFeedbackSuccess = false;
int rewriteFeedbackUntil = 0;
int graphRevision = 0;
int rackRewriteResetAt = 0;
int pasteGeneration = 0;
String pendingRewriteRule = "";
float pendingScalarReal = 1.0;
float pendingScalarImag = 0.0;
float diagramScalarReal = 1.0;
float diagramScalarImag = 0.0;

boolean densityPanelVisible = false;
boolean densityDirty = false;
int densityDirtyAt = 0;
boolean densityFrameReceiving = false;
int densityRevision = -1;
String densityMode = "";
String densityStatus = "D opens the density inspector";
float densityTrace = 0;
float densityPurity = 0;
float densityCoherence = 0;
float densityEntropy = 0;
float densityMinEigenvalue = 0;
float densitySuccessProbability = 0;
int densityDimension = 16;
int densityQubitCount = 4;
float[][] densityReal = new float[densityDimension][densityDimension];
float[][] densityImag = new float[densityDimension][densityDimension];
float[] densityProbabilities = new float[densityDimension];
float[][] densityBloch = new float[densityQubitCount][3];
float[] densityLocalPurity = new float[densityQubitCount];
float[] densityLocalEntropy = new float[densityQubitCount];

boolean pauliInputMode = false;
String pauliInputText = "";
boolean ghzInputMode = false;
String ghzInputText = "";
boolean circuitPresetMode = false;
String activePauliLabel = "";
int activePauliCentralNodeId = -1;
float activePauliTheta = PI / 4.0;
float activePauliExpectation = 0;
boolean activePauliVerified = false;
float activePauliError = 0;
ArrayList<PauliGadgetMacro> pauliScore = new ArrayList<PauliGadgetMacro>();
boolean pauliScoreMode = false;
int nextPauliGadgetId = 1;
int activePauliGadgetId = -1;
int draggingPauliGadgetId = -1;
float pauliDragStartX = 0;
String pauliViewMode = "ZX";

boolean eulerPanelVisible = false;
String eulerSource = "";
String eulerBasis = "ZXZ";
int eulerQubit = -1;
float eulerTheta = 0;
float eulerPhi = 0;
float eulerLambda = 0;
float eulerGamma = 0;
float eulerZXScalarPhase = 0;
float eulerError = 0;
boolean eulerVerified = false;
int nextEulerRequestId = 1;
int pendingEulerRequestId = -1;
final int EULER_LIVE_DEBOUNCE_MS = 90;
ArrayList<Integer> liveEulerNodeIds = new ArrayList<Integer>();
boolean eulerLiveEnabled = false;
boolean eulerDirty = false;
int eulerDirtyAt = 0;
String circuitEulerBasis = "ZXZ";

PFont diagramFont;


void settings() {
  size(1280, 800, P2D);
  smooth(8);
}


void setup() {
  surface.setTitle("QMW ZX Visual Patcher");
  frameRate(60);
  diagramFont = createFont("Serif", 18);
  textFont(diagramFont);
  maxTarget = new NetAddress("127.0.0.1", MAX_PORT);
  rackTarget = new NetAddress("127.0.0.1", RACK_PORT);
  superColliderTarget = new NetAddress("127.0.0.1", SUPERCOLLIDER_PORT);
  pythonVerifierTarget = new NetAddress(
    "127.0.0.1",
    PYTHON_VERIFIER_PORT
  );
  oscP5 = new OscP5(this, OSC_PORT);

  resetGraph();
}


void draw() {
  serviceTimedOsc();
  background(249, 249, 246);
  if (pauliScoreMode && !pauliViewMode.equals("ZX")) {
    drawPauliCircuitView();
  } else {
    if (pauliScoreMode) drawPauliMacroBands();
    drawWireLayer();
    drawNodeLayer();
  }
  drawFusionCue();
  if (pauliScoreMode) drawPauliRelationCue();
  drawRuleBar();
  if (eulerPanelVisible) drawEulerPanel();
  if (densityPanelVisible) drawDensityPanel();
  drawStatus();
  if (pauliInputMode) drawPauliInput();
  if (ghzInputMode) drawGHZInput();
  if (circuitPresetMode) drawCircuitPresetLibrary();
}


void resetGraph() {
  clearLiveEulerSelection();
  eulerPanelVisible = false;
  eulerVerified = false;
  nodes.clear();
  edges.clear();
  nextNodeId = 1;
  diagramScalarReal = 1.0;
  diagramScalarImag = 0.0;
  clearActivePauli();
  clearPauliScore();

  ZXNode in0 = addBoundary("input", 0, 80, 275);
  ZXNode in1 = addBoundary("input", 1, 80, 525);
  ZXNode zAlpha = addNode("Z", 300, 310, "α");
  ZXNode zBeta = addNode("Z", 550, 420, "β");
  ZXNode x = addNode("X", 810, 485, "γ");
  ZXNode h = addNode("H", 790, 245, "");
  ZXNode out0 = addBoundary("output", 0, 1160, 245);
  ZXNode out1 = addBoundary("output", 1, 1160, 455);
  ZXNode out2 = addBoundary("output", 2, 1160, 620);

  zAlpha.phase = PI / 4.0;
  zBeta.phase = PI / 3.0;
  x.phase = -PI / 4.0;

  addEdge(in0, zAlpha);
  addEdge(in1, zAlpha);
  addEdge(zAlpha, zBeta);
  addEdge(zAlpha, h);
  addEdge(h, out0);
  addEdge(zBeta, x);
  addEdge(x, out1);
  addEdge(x, out2);
  statusText = "Shift-click the two connected green spiders, then press F";
  sendGraphSnapshot();
}


ZXNode addNode(String kind, float x, float y, String label) {
  ZXNode node = new ZXNode(nextNodeId++, kind, x, y, label);
  nodes.add(node);
  return node;
}


ZXNode addBoundary(String role, int index, float x, float y) {
  ZXNode node = addNode("B", x, y, "");
  node.boundaryRole = role;
  node.boundaryIndex = index;
  node.label = boundaryLabel(node);
  return node;
}


String boundaryLabel(ZXNode node) {
  if (node.boundaryRole.equals("input")) return "in q" + node.boundaryIndex;
  if (node.boundaryRole.equals("output")) return "out q" + node.boundaryIndex;
  return "";
}


int nextBoundaryIndex(String role) {
  int index = 0;
  boolean occupied = true;
  while (occupied) {
    occupied = false;
    for (ZXNode node : nodes) {
      if (
        node.kind.equals("B")
        && node.boundaryRole.equals(role)
        && node.boundaryIndex == index
      ) {
        occupied = true;
        index += 1;
        break;
      }
    }
  }
  return index;
}


void addEdge(ZXNode a, ZXNode b) {
  addEdge(a, b, "plain");
}


void addEdge(ZXNode a, ZXNode b, String kind) {
  if (a == null || b == null || a == b) return;
  int parallelCount = edgeCountBetween(a, b);
  float bend = 0;
  if (parallelCount > 0) {
    int magnitude = ((parallelCount + 1) / 2) * 42;
    bend = parallelCount % 2 == 1 ? magnitude : -magnitude;
    if (parallelCount == 1 && edges.size() > 0) {
      for (ZXEdge edge : edges) {
        if (
          (edge.a == a && edge.b == b)
          || (edge.a == b && edge.b == a)
        ) {
          edge.bend = -42;
        }
      }
      bend = 42;
    }
  } else {
    bend = ((edges.size() % 3) - 1) * 18.0;
  }
  edges.add(new ZXEdge(a, b, bend, kind));
}


boolean edgeExists(ZXNode a, ZXNode b) {
  return edgeCountBetween(a, b) > 0;
}


int edgeCountBetween(ZXNode a, ZXNode b) {
  int count = 0;
  for (ZXEdge edge : edges) {
    if ((edge.a == a && edge.b == b) || (edge.a == b && edge.b == a)) {
      count += 1;
    }
  }
  return count;
}


void drawWireLayer() {
  float coherence = quantumControl[3];
  if (coherence > 0.02) {
    noFill();
    stroke(232, 160, 172, 22 + 55 * coherence);
    strokeWeight(7 + 9 * coherence);
    for (ZXEdge edge : edges) drawBezier(edge);
  }

  noFill();
  strokeWeight(2.2 + 1.8 * abs(quantumControl[1] - 0.5));
  for (ZXEdge edge : edges) {
    if (edge.kind.equals("hadamard")) {
      drawHadamardEdge(edge);
    } else {
      stroke(25, 25, 25);
      drawBezier(edge);
    }
  }

  float direction = quantumControl[4] >= 0.5 ? 1.0 : -1.0;
  float speed = 0.035 + 0.22 * abs(quantumControl[4] - 0.5) * 2.0;
  for (int i = 0; i < edges.size(); i++) {
    ZXEdge edge = edges.get(i);
    float t = (millis() * speed * 0.001 + i * 0.137) % 1.0;
    if (direction < 0) t = 1.0 - t;
    PVector p = edgePoint(edge, t);
    noStroke();
    fill(nodeColor(edge.a.kind), 190);
    ellipse(p.x, p.y, 5.5, 5.5);
  }

  if (connectMode && connectFrom != null) {
    stroke(45, 45, 45, 130);
    strokeWeight(1.5);
    line(connectFrom.x, connectFrom.y, mouseX, mouseY);
  }
}


void drawHadamardEdge(ZXEdge edge) {
  stroke(59, 112, 170);
  strokeWeight(3.0);
  for (int segment = 0; segment < 20; segment += 2) {
    float t0 = segment / 20.0;
    float t1 = (segment + 1) / 20.0;
    PVector a = edgePoint(edge, t0);
    PVector b = edgePoint(edge, t1);
    line(a.x, a.y, b.x, b.y);
  }
}


void drawBezier(ZXEdge edge) {
  PVector[] points = edgeControlPoints(edge);
  bezier(
    points[0].x, points[0].y,
    points[1].x, points[1].y,
    points[2].x, points[2].y,
    points[3].x, points[3].y
  );
}


PVector edgePoint(ZXEdge edge, float t) {
  PVector[] points = edgeControlPoints(edge);
  return new PVector(
    bezierPoint(points[0].x, points[1].x, points[2].x, points[3].x, t),
    bezierPoint(points[0].y, points[1].y, points[2].y, points[3].y, t)
  );
}


PVector[] edgeControlPoints(ZXEdge edge) {
  PVector a = new PVector(edge.a.x, edge.a.y);
  PVector b = new PVector(edge.b.x, edge.b.y);
  PVector delta = PVector.sub(b, a);
  float length = max(delta.mag(), 1.0);
  PVector normal = new PVector(-delta.y / length, delta.x / length);
  float bendScale = 0.45 + 2.1 * quantumControl[2];
  PVector offset = PVector.mult(normal, edge.bend * bendScale);
  PVector c1 = PVector.add(PVector.add(a, PVector.mult(delta, 0.34)), offset);
  PVector c2 = PVector.add(PVector.add(a, PVector.mult(delta, 0.66)), offset);
  return new PVector[] {a, c1, c2, b};
}


void drawNodeLayer() {
  for (ZXNode node : nodes) {
    drawNode(node);
  }
}


void drawNode(ZXNode node) {
  float pulse = 1.0;
  if (node.kind.equals("Z") || node.kind.equals("X")) {
    pulse += 0.055 * quantumControl[5] * sin(millis() * 0.004 + node.id);
  }

  if (eulerLiveEnabled && liveEulerContains(node.id)) {
    noFill();
    stroke(59, 151, 96, 210);
    strokeWeight(2.2);
    ellipse(node.x, node.y, 60, 60);
  }

  if (node.selected) {
    noFill();
    stroke(65, 108, 196, 220);
    strokeWeight(3.0);
    ellipse(node.x, node.y, 70, 70);
    noStroke();
    fill(65, 108, 196);
    ellipse(node.x + 24, node.y - 24, 10, 10);
  }

  stroke(20);
  strokeWeight(2.4);

  if (node.kind.equals("H")) {
    rectMode(CENTER);
    fill(245, 244, 205);
    rect(node.x, node.y, 43, 43);
    return;
  }

  if (node.kind.equals("HB")) {
    rectMode(CENTER);
    fill(250, 221, 116);
    rect(node.x, node.y, 58, 42, 8);
    fill(40);
    textAlign(CENTER, CENTER);
    textSize(16);
    text(node.label, node.x, node.y - 1);
    return;
  }

  if (node.kind.equals("B")) {
    fill(25);
    ellipse(node.x, node.y, 8, 8);
    noStroke();
    fill(85);
    textSize(11);
    textAlign(
      node.boundaryRole.equals("input") ? LEFT : RIGHT,
      CENTER
    );
    float labelX = node.x + (
      node.boundaryRole.equals("input") ? 12 : -12
    );
    text(node.label, labelX, node.y - 12);
    return;
  }

  if (node.kind.equals("D")) {
    noFill();
    stroke(25);
    strokeWeight(2.6);
    arc(node.x, node.y + 2, 34, 26, 0, PI);
    line(node.x - 17, node.y + 2, node.x + 17, node.y + 2);
    line(node.x, node.y - 17, node.x, node.y + 2);
    noStroke();
    fill(75);
    textAlign(CENTER, TOP);
    textSize(node.label.length() > 9 ? 9 : 10);
    text(
      node.label.equals("") ? "discard" : node.label,
      node.x,
      node.y + 18
    );
    return;
  }

  fill(nodeColor(node.kind));
  ellipse(node.x, node.y, 48 * pulse, 48 * pulse);
  fill(18);
  textAlign(CENTER, CENTER);
  textSize(18);
  text(node.label, node.x, node.y - 2);
}


int nodeColor(String kind) {
  if (kind.equals("Z")) return color(188, 230, 176);
  if (kind.equals("X")) return color(234, 156, 164);
  if (kind.equals("H")) return color(245, 244, 205);
  if (kind.equals("HB")) return color(250, 221, 116);
  if (kind.equals("D")) return color(85);
  return color(35);
}


ArrayList<ZXNode> selectedNodes() {
  ArrayList<ZXNode> selected = new ArrayList<ZXNode>();
  for (ZXNode node : nodes) {
    if (node.selected) selected.add(node);
  }
  return selected;
}


boolean fusionSelectionReady() {
  ArrayList<ZXNode> selected = selectedNodes();
  return (
    selected.size() == 2
    && (selected.get(0).kind.equals("Z") || selected.get(0).kind.equals("X"))
    && selected.get(0).kind.equals(selected.get(1).kind)
    && edgeCountBetween(selected.get(0), selected.get(1)) == 1
  );
}


void drawFusionCue() {
  if (fusionSelectionReady()) {
    rectMode(CENTER);
    stroke(65, 108, 196);
    strokeWeight(1.5);
    fill(232, 239, 252);
    rect(width * 0.5, 93, 280, 36, 18);
    noStroke();
    fill(35, 62, 110);
    textAlign(CENTER, CENTER);
    textSize(13);
    text("FUSION READY  ·  press F", width * 0.5, 91);
  }

  if (millis() < rewriteFeedbackUntil && !rewriteFeedback.equals("")) {
    rectMode(CENTER);
    noStroke();
    fill(
      rewriteFeedbackSuccess
      ? color(224, 244, 228, 245)
      : color(253, 235, 210, 245)
    );
    rect(width * 0.5, 145, 610, 54, 16);
    fill(rewriteFeedbackSuccess ? color(37, 105, 58) : color(135, 76, 22));
    textAlign(CENTER, CENTER);
    textSize(15);
    text(rewriteFeedback, width * 0.5, 143);
  }
}


void drawRuleBar() {
  noStroke();
  fill(238, 239, 235, 242);
  rectMode(CENTER);
  rect(width * 0.5, 54, width - 38, 30, 12);
  fill(72);
  textAlign(CENTER, CENTER);
  textSize(11);
  text(
    "I identity   P π-copy   K state-copy   A bialgebra   "
    + "O Hopf   G color   w lcomp   W pivot   J Pauli   0 circuits   D density",
    width * 0.5,
    53
  );
}


void drawDensityPanel() {
  float panelX = 646;
  float panelY = 82;
  float panelW = 612;
  float panelH = 680;
  float gridX = 686;
  float gridY = 224;
  float gridSize = 424;
  int displayDimension = min(densityDimension, 64);
  int displayStride = max(1, densityDimension / displayDimension);
  float cell = gridSize / displayDimension;

  rectMode(CORNER);
  noStroke();
  fill(255, 255, 253, 248);
  rect(panelX, panelY, panelW, panelH, 18);
  stroke(205, 207, 201);
  strokeWeight(1.2);
  noFill();
  rect(panelX, panelY, panelW, panelH, 18);

  noStroke();
  fill(34);
  textAlign(LEFT, TOP);
  textSize(20);
  text(
    "Density matrix  ρ   ·   " + densityQubitCount + "q   ·   "
    + densityDimension + "×" + densityDimension,
    panelX + 25,
    panelY + 20
  );
  textSize(11);
  fill(92);
  text(
    densityRevision < 0
      ? "waiting for discard-ZX evaluation"
      : densityMode + "  ·  revision " + densityRevision,
    panelX + 25,
    panelY + 50
  );

  fill(54);
  textSize(12);
  text(
    "Tr " + nf(densityTrace, 0, 4)
    + "    purity " + nf(densityPurity, 0, 4)
    + "    S " + nf(densityEntropy, 0, 4),
    panelX + 25,
    panelY + 75
  );
  text(
    "coherence ℓ₁ " + nf(densityCoherence, 0, 4)
    + "    min λ " + nf(densityMinEigenvalue, 0, 5)
    + "    weight " + nf(densitySuccessProbability, 0, 4),
    panelX + 25,
    panelY + 96
  );

  float maxMagnitude = 0.000001;
  for (int row = 0; row < densityDimension; row++) {
    for (int column = 0; column < densityDimension; column++) {
      maxMagnitude = max(
        maxMagnitude,
        sqrt(
          densityReal[row][column] * densityReal[row][column]
          + densityImag[row][column] * densityImag[row][column]
        )
      );
    }
  }

  if (densityDimension <= 16) {
    textAlign(CENTER, CENTER);
    textSize(8);
    fill(105);
    for (int index = 0; index < densityDimension; index++) {
      text(hex(index, 1), gridX + index * cell + cell * 0.5, gridY - 9);
      text(hex(index, 1), gridX - 10, gridY + index * cell + cell * 0.5);
    }
  } else {
    textAlign(LEFT, CENTER);
    textSize(8);
    fill(105);
    text("0", gridX, gridY - 9);
    text(
      str(densityDimension - 1),
      gridX + gridSize - 18,
      gridY - 9
    );
  }

  colorMode(HSB, TWO_PI, 1, 1, 1);
  for (int displayRow = 0; displayRow < displayDimension; displayRow++) {
    for (
      int displayColumn = 0;
      displayColumn < displayDimension;
      displayColumn++
    ) {
      float magnitude = 0;
      float phase = 0;
      int rowStart = displayRow * displayStride;
      int columnStart = displayColumn * displayStride;
      int rowEnd = min(densityDimension, rowStart + displayStride);
      int columnEnd = min(
        densityDimension,
        columnStart + displayStride
      );
      for (int row = rowStart; row < rowEnd; row++) {
        for (int column = columnStart; column < columnEnd; column++) {
          float real = densityReal[row][column];
          float imag = densityImag[row][column];
          float candidate = sqrt(real * real + imag * imag);
          if (candidate >= magnitude) {
            magnitude = candidate;
            phase = positiveModulo(atan2(imag, real), TWO_PI);
          }
        }
      }
      float normalized = constrain(magnitude / maxMagnitude, 0, 1);
      noStroke();
      fill(phase, 0.76 * sqrt(normalized), 0.18 + 0.82 * sqrt(normalized), 1);
      rect(
        gridX + displayColumn * cell,
        gridY + displayRow * cell,
        max(0.7, cell - 0.7),
        max(0.7, cell - 0.7),
        min(3, cell * 0.2)
      );
    }
  }
  colorMode(RGB, 255);

  float summaryX = gridX + gridSize + 24;
  fill(55);
  textAlign(LEFT, TOP);
  textSize(11);
  text("local Bloch vectors", summaryX, gridY);
  float blochSpacing = min(70, 375.0 / max(1, densityQubitCount));
  for (int qubit = 0; qubit < densityQubitCount; qubit++) {
    float y = gridY + 26 + qubit * blochSpacing;
    fill(75);
    text(
      "q" + qubit
      + "  (" + nf(densityBloch[qubit][0], 0, 2)
      + ", " + nf(densityBloch[qubit][1], 0, 2)
      + ", " + nf(densityBloch[qubit][2], 0, 2) + ")",
      summaryX,
      y
    );
    text(
      "P " + nf(densityLocalPurity[qubit], 0, 3)
      + "   S " + nf(densityLocalEntropy[qubit], 0, 3),
      summaryX,
      y + 18
    );
    stroke(214);
    line(
      summaryX,
      y + min(42, blochSpacing - 4),
      panelX + panelW - 22,
      y + min(42, blochSpacing - 4)
    );
    noStroke();
  }

  fill(72);
  textAlign(LEFT, TOP);
  textSize(11);
  text(densityStatus, panelX + 25, panelY + panelH - 59);
  fill(112);
  text(
    "D close/refresh   ·   0 circuit library   ·   2 Bell   ·   Return commit",
    panelX + 25,
    panelY + panelH - 34
  );
  if (!activePauliLabel.equals("")) {
    fill(activePauliVerified ? color(37, 105, 58) : color(135, 76, 22));
    textAlign(RIGHT, TOP);
    text(
      activePauliLabel
      + "   〈P〉 " + nf(activePauliExpectation, 0, 5)
      + "   θ " + phaseLabel(activePauliTheta),
      panelX + panelW - 24,
      panelY + 22
    );
  }
}


void drawStatus() {
  boolean oscLive = millis() - lastOscMillis < 1200;
  noStroke();
  fill(oscLive ? color(98, 176, 112) : color(165));
  ellipse(26, 25, 8, 8);

  fill(70);
  textAlign(LEFT, CENTER);
  textSize(12);
  text(
    oscLive ? "PennyLane live" : "OSC 7497 waiting",
    39,
    24
  );

  fill(100);
  textAlign(RIGHT, CENTER);
  text(
    pauliScoreMode
      ? (
        pauliScore.size() + " Pauli gadgets · " + pauliViewMode
        + " view · drag phase nodes to reorder · Shift-select + F"
      )
      : "Z X H B generators   ·   N CNOT   ·   C cable   ·   ⌘C ⌘V   ·   F fuse",
    width - 24,
    24
  );

  fill(105);
  textAlign(LEFT, CENTER);
  text(statusText, 24, height - 24);
  textAlign(RIGHT, CENTER);
  text(
    "scalar " + scalarLabel()
    + "   → Max " + MAX_PORT
    + "   Rack " + RACK_PORT
    + "   SuperCollider " + SUPERCOLLIDER_PORT,
    width - 24,
    height - 24
  );
}


String scalarLabel() {
  if (abs(diagramScalarImag) < 0.0001) return nf(diagramScalarReal, 0, 3);
  String sign = diagramScalarImag >= 0 ? " + " : " − ";
  return (
    nf(diagramScalarReal, 0, 3)
    + sign + nf(abs(diagramScalarImag), 0, 3) + "i"
  );
}


void multiplyDiagramScalar(float factor) {
  diagramScalarReal *= factor;
  diagramScalarImag *= factor;
  sendGraphScalar();
}


void sendGraphScalar() {
  OscMessage message = new OscMessage("/qmw/zx/graph/scalar");
  message.add(diagramScalarReal);
  message.add(diagramScalarImag);
  oscP5.send(message, pythonVerifierTarget);
  oscP5.send(message, maxTarget);
  oscP5.send(message, superColliderTarget);
}


void mousePressed() {
  if (pauliScoreMode && !pauliViewMode.equals("ZX")) {
    PauliGadgetMacro gadget = pauliGadgetNearestX(mouseX);
    if (gadget != null && mouseY > 90 && mouseY < 710) {
      clearSelection();
      setActivePauliGadget(gadget.id, true);
      sendPauliActive();
      statusText = gadget.label + " selected in " + pauliViewMode + " view";
    }
    return;
  }

  ZXNode hit = nodeAt(mouseX, mouseY);

  if (mouseButton == RIGHT) {
    if (hit != null) {
      hit.selected = true;
      deleteSelected();
    }
    return;
  }

  if (connectMode) {
    if (hit == null) return;
    if (connectFrom == null) {
      connectFrom = hit;
      statusText = "choose the second endpoint";
    } else {
      if (
        liveEulerContains(connectFrom.id)
        || liveEulerContains(hit.id)
      ) {
        invalidateLiveEulerSelection();
      }
      if (connectFrom == hit) {
        statusText = "a ZX wire needs two different endpoints";
        return;
      }
      addEdge(connectFrom, hit);
      sendEdgeAdded(connectFrom, hit);
      connectFrom = null;
      connectMode = false;
      statusText = "wire connected";
      markDensityDirty();
    }
    return;
  }

  if (hit == null) {
    if (!shiftDown) clearSelection();
    return;
  }

  if (pauliScoreMode && hit.pauliGadgetId >= 0) {
    PauliGadgetMacro gadget = pauliGadgetWithId(hit.pauliGadgetId);
    if (gadget != null) {
      ZXNode phaseNode = nodeWithId(gadget.phaseNodeId);
      if (phaseNode != null) hit = phaseNode;
      setActivePauliGadget(gadget.id, false);
      sendPauliActive();
    }
  }

  if (shiftDown) {
    hit.selected = !hit.selected;
  } else {
    clearSelection();
    hit.selected = true;
  }

  if (hit.selected) {
    dragNode = hit;
    dragOffsetX = hit.x - mouseX;
    dragOffsetY = hit.y - mouseY;
    if (pauliScoreMode && hit.pauliRole.equals("phase")) {
      draggingPauliGadgetId = hit.pauliGadgetId;
      pauliDragStartX = mouseX;
    }
  }
}


void mouseDragged() {
  if (dragNode == null) return;
  dragNode.x = constrain(mouseX + dragOffsetX, 28, width - 28);
  dragNode.y = constrain(mouseY + dragOffsetY, 55, height - 55);
}


void mouseReleased() {
  if (pauliScoreMode && draggingPauliGadgetId >= 0) {
    if (abs(mouseX - pauliDragStartX) > 18) {
      int destination = pauliScoreIndexNearestX(mouseX);
      reorderPauliGadget(draggingPauliGadgetId, destination);
    }
    draggingPauliGadgetId = -1;
  } else if (dragNode != null) {
    sendNodePosition(dragNode);
  }
  dragNode = null;
}


void mouseWheel(MouseEvent event) {
  adjustSelectedPhases(-event.getCount() * PI / 8.0);
}


void adjustSelectedPhases(float amount) {
  if (pauliScoreMode) {
    boolean scoreChanged = false;
    int lastChangedId = -1;
    for (ZXNode node : nodes) {
      if (node.selected && node.pauliRole.equals("phase")) {
        PauliGadgetMacro gadget = pauliGadgetWithId(node.pauliGadgetId);
        if (gadget != null) {
          gadget.theta += amount;
          scoreChanged = true;
          lastChangedId = gadget.id;
        }
      }
    }
    if (scoreChanged) {
      setActivePauliGadget(lastChangedId, false);
      float turns = positiveModulo(activePauliTheta / TWO_PI, 1.0);
      quantumControl[0] = turns;
      sendFader(1, turns);
      rebuildPauliScoreGraph(lastChangedId, true);
      statusText = (
        activePauliLabel + " phase changed · complete score reverified"
      );
      return;
    }
  }

  boolean changed = false;
  boolean changedPauli = false;
  boolean changedLiveEuler = false;
  for (ZXNode node : nodes) {
    if (node.selected && (node.kind.equals("Z") || node.kind.equals("X"))) {
      node.phase += amount;
      node.label = phaseLabel(node.phase);
      float turns = positiveModulo(node.phase / TWO_PI, 1.0);
      quantumControl[0] = turns;
      sendFader(1, turns);
      sendNodePhase(node);
      changed = true;
      if (node.id == activePauliCentralNodeId) {
        activePauliTheta = node.phase;
        changedPauli = true;
      }
      if (eulerLiveEnabled && liveEulerContains(node.id)) {
        changedLiveEuler = true;
      }
    }
  }
  if (changed) {
    if (changedPauli) {
      updateActivePauliScalar();
      sendPauliGadget();
    }
    if (changedLiveEuler) {
      markLiveEulerDirty();
      statusText = "spider phase changed · live Euler update queued";
    } else {
      statusText = "spider phase changed";
    }
    markDensityDirty();
  }
  else statusText = "select a Z or X spider before changing phase";
}


void keyPressed() {
  if (keyCode == SHIFT) {
    shiftDown = true;
    return;
  }

  if (pauliInputMode) {
    handlePauliInputKey();
    return;
  }
  if (ghzInputMode) {
    handleGHZInputKey();
    return;
  }
  if (circuitPresetMode) {
    handleCircuitPresetKey();
    return;
  }

  boolean commandDown = keyEvent != null && keyEvent.isMetaDown();
  if (commandDown && (key == 'c' || key == 'C')) {
    copySelection();
    return;
  }
  if (commandDown && (key == 'v' || key == 'V')) {
    pasteClipboard();
    return;
  }

  if (key == 'z' || key == 'Z') addNodeAtMouse("Z");
  else if (key == 'x' || key == 'X') addNodeAtMouse("X");
  else if (key == 'h' || key == 'H') addNodeAtMouse("H");
  else if (key == 'b' || key == 'B') addNodeAtMouse("B");
  else if (key == 'v' || key == 'V') addNodeAtMouse("D");
  else if (key == 'd' || key == 'D') toggleDensityPanel();
  else if (key == 'q' || key == 'Q') resetDensityDemo();
  else if (key == '0') beginCircuitPresetLibrary();
  else if (key >= '1' && key <= '8') {
    resetGHZDemo(int(key - '0'));
  }
  else if (key == 'l' || key == 'L') beginGHZInput();
  else if (key == 'n' || key == 'N') addCNOTAtMouse();
  else if (key == 'j' || key == 'J') beginPauliInput();
  else if (key == 'm' || key == 'M') cyclePauliView();
  else if (key == 'e' || key == 'E') requestEulerDecomposition();
  else if (key == 'y' || key == 'Y') addNodeAtMouse("HB");
  else if (key == 't' || key == 'T') addToffoliAtMouse();
  else if (key == 'c' || key == 'C') {
    connectMode = true;
    connectFrom = null;
    statusText = "choose the first cable endpoint";
  }
  else if (key == 'f' || key == 'F') fuseSelectedSpiders();
  else if (key == 'i' || key == 'I') {
    applyNamedRewrite("identity_removal");
  }
  else if (key == 'p' || key == 'P') applyNamedRewrite("pi_copy");
  else if (key == 'k' || key == 'K') applyNamedRewrite("state_copy");
  else if (key == 'a' || key == 'A') applyNamedRewrite("bialgebra");
  else if (key == 'o' || key == 'O') applyNamedRewrite("hopf");
  else if (key == 'g' || key == 'G') applyNamedRewrite("color_change");
  else if (key == 'w') applyNamedRewrite("local_complementation");
  else if (key == 'W') applyNamedRewrite("pivot");
  else if (key == 'u' || key == 'U') applyNamedRewrite("absorb");
  else if (key == 's' || key == 'S') saveGraph();
  else if (key == 'r' || key == 'R') resetGraph();
  else if (key == '[' || key == '-' || keyCode == LEFT) {
    adjustSelectedPhases(-PI / 8.0);
  }
  else if (key == ']' || key == '=' || keyCode == RIGHT) {
    adjustSelectedPhases(PI / 8.0);
  }
  else if (keyCode == DELETE || keyCode == BACKSPACE) deleteSelected();
  else if (keyCode == ENTER || keyCode == RETURN) commitDensityPreview();
  else if (keyCode == ESC) {
    key = 0;
    connectMode = false;
    connectFrom = null;
    statusText = "connection cancelled";
  }
}


void keyReleased() {
  if (keyCode == SHIFT) shiftDown = false;
}


void addNodeAtMouse(String kind) {
  String label = "";
  if (kind.equals("Z") || kind.equals("X")) label = "0";
  if (kind.equals("HB")) label = "−1";
  ZXNode node = addNode(
    kind,
    constrain(mouseX, 28, width - 28),
    constrain(mouseY, 55, height - 55),
    label
  );
  if (kind.equals("HB")) node.phase = PI;
  if (kind.equals("B")) {
    node.boundaryRole = mouseX < width * 0.5 ? "input" : "output";
    node.boundaryIndex = nextBoundaryIndex(node.boundaryRole);
    node.label = boundaryLabel(node);
  }
  if (kind.equals("D")) {
    node.boundaryRole = "discard";
    node.boundaryIndex = discardCount() - 1;
    node.label = "discard";
  }
  clearSelection();
  node.selected = true;
  sendNodeAdded(node);
  statusText = kind + " node added";
  markDensityDirty();
}


int discardCount() {
  int count = 0;
  for (ZXNode node : nodes) if (node.kind.equals("D")) count += 1;
  return count;
}


void toggleDensityPanel() {
  densityPanelVisible = !densityPanelVisible;
  if (densityPanelVisible) {
    requestDensityPreview();
  } else {
    statusText = "density inspector closed";
  }
}


void requestDensityPreview() {
  OscMessage message = new OscMessage("/qmw/zx/density/request");
  message.add(graphRevision);
  oscP5.send(message, pythonVerifierTarget);
  densityStatus = "evaluating doubled ket/bra semantics…";
  statusText = "density preview requested from discard-ZX bridge";
  densityDirty = false;
}


void commitDensityPreview() {
  if (!densityPanelVisible || densityRevision < 0) {
    statusText = "open a valid density preview with D before committing";
    return;
  }
  if (densityQubitCount > 4) {
    statusText = (
      densityQubitCount
      + "-qubit preview remains live in Processing/Max; "
      + "the resonator commit is four-qubit"
    );
    return;
  }
  OscMessage message = new OscMessage("/qmw/zx/density/commit");
  message.add(densityRevision);
  oscP5.send(message, pythonVerifierTarget);
  densityStatus = "sending revision " + densityRevision + " atomically to engine…";
  statusText = "density commit requested";
}


void markDensityDirty() {
  densityDirty = true;
  densityDirtyAt = millis();
}


void resetDensityDemo() {
  clearLiveEulerSelection();
  eulerPanelVisible = false;
  eulerVerified = false;
  nodes.clear();
  edges.clear();
  nextNodeId = 1;
  diagramScalarReal = 1.0;
  diagramScalarImag = 0.0;
  clearActivePauli();
  clearPauliScore();

  float boundaryX = 555;
  float spiderX = 330;
  float[] wireY = {230, 350, 470, 590};
  ZXNode[] outputs = new ZXNode[4];
  for (int qubit = 0; qubit < 4; qubit++) {
    outputs[qubit] = addBoundary(
      "output",
      qubit,
      boundaryX,
      wireY[qubit]
    );
  }

  ZXNode entangledSystem = addNode("Z", spiderX, wireY[0], "0");
  ZXNode discard = addNode("D", spiderX, 126, "discard");
  discard.boundaryRole = "discard";
  discard.boundaryIndex = 0;
  addEdge(entangledSystem, outputs[0]);
  addEdge(entangledSystem, discard);

  for (int qubit = 1; qubit < 4; qubit++) {
    ZXNode zeroState = addNode("X", spiderX, wireY[qubit], "0");
    addEdge(zeroState, outputs[qubit]);
  }

  clearSelection();
  entangledSystem.selected = true;
  discard.selected = true;
  densityPanelVisible = true;
  densityRevision = -1;
  densityStatus = "synchronizing the mixed-state example…";
  statusText = "discard-ZX demo: q0 is maximally mixed; q1–q3 are |0〉";
  sendGraphSnapshot();
  markDensityDirty();
}


void resetGHZDemo(int outputCount) {
  if (outputCount < 1 || outputCount > 64) {
    statusText = "GHZ output count must be between 1 and 64";
    return;
  }
  clearLiveEulerSelection();
  eulerPanelVisible = false;
  eulerVerified = false;
  nodes.clear();
  edges.clear();
  nextNodeId = 1;
  diagramScalarReal = 1.0;
  diagramScalarImag = 0.0;
  clearActivePauli();
  clearPauliScore();
  clearDensityFrame();

  float spiderX = 285;
  float boundaryX = outputCount <= 8 ? 565 : 1160;
  float centerY = 400;
  float topY = 115;
  float bottomY = 685;
  ZXNode ghz = addNode("Z", spiderX, centerY, "0");
  ghz.phase = 0;
  for (int qubit = 0; qubit < outputCount; qubit++) {
    float outputY = outputCount == 1
      ? centerY
      : map(qubit, 0, outputCount - 1, topY, bottomY);
    ZXNode output = addBoundary(
      "output",
      qubit,
      boundaryX,
      outputY
    );
    addEdge(ghz, output);
  }

  clearSelection();
  ghz.selected = true;
  densityPanelVisible = outputCount <= 8;
  densityRevision = -1;
  densityStatus = outputCount <= 8
    ? (
      "verifying GHZ" + outputCount + " as a "
      + (1 << outputCount) + "×" + (1 << outputCount) + " density matrix"
    )
    : (
      "GHZ" + outputCount
      + " retained as a compact graph; dense mode is capped at eight outputs"
    );
  statusText = (
    "GHZ" + outputCount + " state · one green Z(0) spider · "
    + outputCount + " tagged outputs"
  );
  sendGraphSnapshot();
  if (outputCount <= 8) markDensityDirty();
}


void beginGHZInput() {
  ghzInputMode = true;
  ghzInputText = "";
  statusText = "type a GHZ output count, then press Return";
}


void handleGHZInputKey() {
  if (keyCode == ESC) {
    key = 0;
    ghzInputMode = false;
    ghzInputText = "";
    statusText = "GHZ generator entry cancelled";
    return;
  }
  if (keyCode == BACKSPACE || keyCode == DELETE) {
    if (ghzInputText.length() > 0) {
      ghzInputText = ghzInputText.substring(0, ghzInputText.length() - 1);
    }
    return;
  }
  if (keyCode == ENTER || keyCode == RETURN) {
    if (ghzInputText.length() == 0) {
      statusText = "enter a GHZ output count from 1 to 64";
      return;
    }
    int outputCount = int(ghzInputText);
    ghzInputMode = false;
    ghzInputText = "";
    resetGHZDemo(outputCount);
    return;
  }
  if (
    key >= '0'
    && key <= '9'
    && ghzInputText.length() < 2
  ) {
    ghzInputText += key;
  }
}


void beginCircuitPresetLibrary() {
  circuitPresetMode = true;
  statusText = "choose a circuit-to-ZX comparison preset";
}


void handleCircuitPresetKey() {
  if (keyCode == ESC || key == '0') {
    key = 0;
    circuitPresetMode = false;
    statusText = "circuit preset library closed";
    return;
  }
  int selection = -1;
  if (key >= '1' && key <= '9') {
    selection = int(key - '0');
  } else {
    char choice = Character.toUpperCase(key);
    if (choice >= 'A' && choice <= 'G') {
      selection = 10 + int(choice - 'A');
    }
  }
  if (selection >= 1) {
    circuitPresetMode = false;
    buildCircuitPreset(selection);
  }
}


void clearForCircuitPreset() {
  clearLiveEulerSelection();
  eulerPanelVisible = false;
  eulerVerified = false;
  nodes.clear();
  edges.clear();
  nextNodeId = 1;
  diagramScalarReal = 1.0;
  diagramScalarImag = 0.0;
  clearActivePauli();
  clearPauliScore();
  clearDensityFrame();
  densityPanelVisible = false;
  densityRevision = -1;
}


ZXNode[] beginZeroStateWires(int qubitCount, float[] wireY) {
  ZXNode[] previous = new ZXNode[qubitCount];
  for (int qubit = 0; qubit < qubitCount; qubit++) {
    ZXNode zeroState = addNode("X", 62, wireY[qubit], "0");
    zeroState.phase = 0;
    previous[qubit] = zeroState;
  }
  return previous;
}


void appendHadamardGate(
  ZXNode[] previous,
  int qubit,
  float x,
  float[] wireY
) {
  ZXNode gate = addNode("H", x, wireY[qubit], "");
  addEdge(previous[qubit], gate);
  previous[qubit] = gate;
  diagramScalarReal /= sqrt(2.0);
  diagramScalarImag /= sqrt(2.0);
}


void appendZPhaseGate(
  ZXNode[] previous,
  int qubit,
  float x,
  float phase,
  float[] wireY
) {
  ZXNode gate = addNode("Z", x, wireY[qubit], phaseLabel(phase));
  gate.phase = phase;
  addEdge(previous[qubit], gate);
  previous[qubit] = gate;
}


void appendCNOTGate(
  ZXNode[] previous,
  int control,
  int target,
  float x,
  float[] wireY
) {
  ZXNode controlSpider = addNode("Z", x, wireY[control], "0");
  ZXNode targetSpider = addNode("X", x, wireY[target], "0");
  addEdge(previous[control], controlSpider);
  addEdge(previous[target], targetSpider);
  addEdge(controlSpider, targetSpider);
  previous[control] = controlSpider;
  previous[target] = targetSpider;
  diagramScalarReal *= sqrt(2.0);
  diagramScalarImag *= sqrt(2.0);
}


void finishStateWires(
  ZXNode[] previous,
  float outputX,
  float[] wireY
) {
  for (int qubit = 0; qubit < previous.length; qubit++) {
    ZXNode output = addBoundary(
      "output",
      qubit,
      outputX,
      wireY[qubit]
    );
    addEdge(previous[qubit], output);
  }
}


void finishCircuitPreset(String label) {
  clearSelection();
  densityStatus = "evaluating " + label + " through the generic ZX compiler…";
  statusText = label + " · expanded ZX comparison · D refreshes density";
  sendGraphSnapshot();
  markDensityDirty();
}


void buildGraphStatePreset(String topology) {
  float[] outputY = {170, 320, 470, 620};
  float[] nodeX = {345, 520, 520, 345};
  float[] nodeY = {245, 245, 545, 545};
  ZXNode[] graphNodes = new ZXNode[4];
  for (int qubit = 0; qubit < 4; qubit++) {
    graphNodes[qubit] = addNode(
      "Z",
      nodeX[qubit],
      nodeY[qubit],
      "0"
    );
    ZXNode output = addBoundary("output", qubit, 925, outputY[qubit]);
    addEdge(graphNodes[qubit], output);
  }

  if (topology.equals("RING")) {
    addEdge(graphNodes[0], graphNodes[1], "hadamard");
    addEdge(graphNodes[1], graphNodes[2], "hadamard");
    addEdge(graphNodes[2], graphNodes[3], "hadamard");
    addEdge(graphNodes[3], graphNodes[0], "hadamard");
  } else if (topology.equals("STAR")) {
    addEdge(graphNodes[0], graphNodes[1], "hadamard");
    addEdge(graphNodes[0], graphNodes[2], "hadamard");
    addEdge(graphNodes[0], graphNodes[3], "hadamard");
  } else if (topology.equals("COMPLETE")) {
    for (int left = 0; left < 4; left++) {
      for (int right = left + 1; right < 4; right++) {
        addEdge(graphNodes[left], graphNodes[right], "hadamard");
      }
    }
  }
  finishCircuitPreset(
    topology + " GRAPH STATE · zero-phase Z spiders + Hadamard edges"
  );
}


void buildPhaseGadgetFusionPreset() {
  densityPanelVisible = false;
  pauliScore.clear();
  pauliScoreMode = true;
  nextPauliGadgetId = 1;
  PauliGadgetMacro first = new PauliGadgetMacro(
    nextPauliGadgetId++,
    "ZZII",
    PI / 4.0
  );
  PauliGadgetMacro second = new PauliGadgetMacro(
    nextPauliGadgetId++,
    "ZZII",
    PI / 8.0
  );
  pauliScore.add(first);
  pauliScore.add(second);
  rebuildPauliScoreGraph(second.id, true);
  clearSelection();
  ZXNode firstPhase = nodeWithId(first.phaseNodeId);
  ZXNode secondPhase = nodeWithId(second.phaseNodeId);
  if (firstPhase != null) firstPhase.selected = true;
  if (secondPhase != null) secondPhase.selected = true;
  statusText = (
    "PHASE GADGET FUSION · ZZII π/4 + π/8 selected · press F"
  );
  rewriteFeedback = "FUSIBLE PHASE GADGETS  ·  press F to obtain 3π/8";
  rewriteFeedbackSuccess = true;
  rewriteFeedbackUntil = millis() + 7000;
}


void buildLocalComplementationPreset() {
  ZXNode center = addNode("Z", 390, 400, "π/2");
  center.phase = PI / 2.0;
  float[] neighborY = {225, 400, 575};
  for (int index = 0; index < 3; index++) {
    ZXNode neighbor = addNode("Z", 690, neighborY[index], "0");
    ZXNode output = addBoundary(
      "output",
      index,
      1080,
      neighborY[index]
    );
    addEdge(center, neighbor, "hadamard");
    addEdge(neighbor, output);
  }
  finishCircuitPreset(
    "LOCAL COMPLEMENTATION DEMO · selected π/2 interior spider"
  );
  clearSelection();
  center.selected = true;
  statusText = "LOCAL COMPLEMENTATION READY · press lowercase w";
  rewriteFeedback = (
    "LC READY  ·  complements the three-neighbor graph and preserves its tensor"
  );
  rewriteFeedbackSuccess = true;
  rewriteFeedbackUntil = millis() + 7000;
}


void buildPivotPreset() {
  ZXNode left = addNode("Z", 350, 315, "0");
  ZXNode right = addNode("Z", 350, 500, "0");
  addEdge(left, right, "hadamard");
  float[] outputY = {150, 285, 530, 665};
  for (int qubit = 0; qubit < 4; qubit++) {
    ZXNode neighbor = addNode("Z", 690, outputY[qubit], "0");
    ZXNode output = addBoundary(
      "output",
      qubit,
      1080,
      outputY[qubit]
    );
    addEdge(qubit < 2 ? left : right, neighbor, "hadamard");
    addEdge(neighbor, output);
  }
  finishCircuitPreset("PIVOT DEMO · selected interior Pauli pair");
  clearSelection();
  left.selected = true;
  right.selected = true;
  statusText = "PIVOT READY · press Shift-W";
  rewriteFeedback = (
    "PIVOT READY  ·  toggles connectivity across the two neighbor sets"
  );
  rewriteFeedbackSuccess = true;
  rewriteFeedbackUntil = millis() + 7000;
}


void buildTeleportationCPTPPreset() {
  float[] wireY = {205, 400, 595};
  ZXNode[] previous = new ZXNode[3];
  previous[0] = addBoundary("input", 0, 55, wireY[0]);
  previous[1] = addNode("X", 55, wireY[1], "0");
  previous[2] = addNode("X", 55, wireY[2], "0");

  appendHadamardGate(previous, 1, 150, wireY);
  appendCNOTGate(previous, 1, 2, 265, wireY);
  appendCNOTGate(previous, 0, 1, 405, wireY);
  appendHadamardGate(previous, 0, 515, wireY);

  // Deferred measurement: q0 and q1 retain the two classical outcomes.
  // Coherent corrections are equivalent to feed-forward X and Z.
  appendCNOTGate(previous, 1, 2, 660, wireY);
  appendHadamardGate(previous, 2, 765, wireY);
  appendCNOTGate(previous, 0, 2, 875, wireY);
  appendHadamardGate(previous, 2, 985, wireY);

  ZXNode measureX = addNode("D", 1140, wireY[0], "mX→Z→discard");
  measureX.boundaryRole = "discard";
  measureX.boundaryIndex = 0;
  ZXNode measureZ = addNode("D", 1140, wireY[1], "mZ→X→discard");
  measureZ.boundaryRole = "discard";
  measureZ.boundaryIndex = 1;
  ZXNode output = addBoundary("output", 0, 1140, wireY[2]);
  addEdge(previous[0], measureX);
  addEdge(previous[1], measureZ);
  addEdge(previous[2], output);

  // The two raw red zero-state spiders each carry sqrt(2). Correcting the
  // amplitude by 1/2 makes the dilation trace-preserving before normalization.
  diagramScalarReal *= 0.5;
  diagramScalarImag *= 0.5;
  finishCircuitPreset(
    "TELEPORTATION CPTP · coherent outcomes + X/Z corrections + discard"
  );
  statusText = (
    "TELEPORTATION CPTP · input q0 emerges on output q0 · D inspects |0〉"
  );
}


void buildCircuitPreset(int selection) {
  clearForCircuitPreset();
  float[] fourWireY = {175, 315, 455, 595};

  if (selection == 1) {
    ZXNode[] previous = beginZeroStateWires(4, fourWireY);
    appendHadamardGate(previous, 0, 205, fourWireY);
    appendCNOTGate(previous, 0, 1, 405, fourWireY);
    finishStateWires(previous, 1160, fourWireY);
    finishCircuitPreset(
      "QAC BELL · H(q0), CX(q0,q1), q2/q3 = |0〉"
    );
    return;
  }

  if (selection == 2) {
    ZXNode[] previous = beginZeroStateWires(4, fourWireY);
    appendHadamardGate(previous, 0, 165, fourWireY);
    appendCNOTGate(previous, 0, 1, 360, fourWireY);
    appendCNOTGate(previous, 1, 2, 585, fourWireY);
    appendCNOTGate(previous, 2, 3, 810, fourWireY);
    finishStateWires(previous, 1160, fourWireY);
    finishCircuitPreset(
      "QAC GHZ · H(q0), CX(0,1), CX(1,2), CX(2,3)"
    );
    return;
  }

  if (selection == 3) {
    ZXNode[] previous = beginZeroStateWires(4, fourWireY);
    float columnLeft = 125;
    float columnStep = 65;
    for (int qubit = 0; qubit < 4; qubit++) {
      appendHadamardGate(
        previous,
        qubit,
        columnLeft + qubit * columnStep,
        fourWireY
      );
    }
    appendCNOTGate(
      previous,
      0,
      1,
      columnLeft + 5 * columnStep,
      fourWireY
    );
    appendCNOTGate(
      previous,
      2,
      3,
      columnLeft + 7 * columnStep,
      fourWireY
    );
    appendCNOTGate(
      previous,
      1,
      2,
      columnLeft + 10 * columnStep,
      fourWireY
    );
    appendZPhaseGate(
      previous,
      0,
      columnLeft + 13 * columnStep,
      PI / 4.0,
      fourWireY
    );
    appendZPhaseGate(
      previous,
      3,
      columnLeft + 14 * columnStep,
      PI / 2.0,
      fourWireY
    );
    finishStateWires(previous, 1160, fourWireY);
    finishCircuitPreset(
      "QAC WEAVE · H×4, CX(0,1), CX(2,3), CX(1,2), T(q0), S(q3)"
    );
    return;
  }

  if (selection == 4) {
    ZXNode[] graphNodes = new ZXNode[4];
    for (int qubit = 0; qubit < 4; qubit++) {
      graphNodes[qubit] = addNode("Z", 410, fourWireY[qubit], "0");
      ZXNode output = addBoundary(
        "output",
        qubit,
        850,
        fourWireY[qubit]
      );
      addEdge(graphNodes[qubit], output);
      if (qubit > 0) {
        addEdge(graphNodes[qubit - 1], graphNodes[qubit], "hadamard");
      }
    }
    finishCircuitPreset(
      "CLUSTER4 · graph-state Z spiders joined by Hadamard edges"
    );
    return;
  }

  if (selection == 5) {
    float[] twoWireY = {300, 500};
    ZXNode[] previous = new ZXNode[2];
    for (int qubit = 0; qubit < 2; qubit++) {
      previous[qubit] = addBoundary(
        "input",
        qubit,
        145,
        twoWireY[qubit]
      );
    }
    appendCNOTGate(previous, 0, 1, 600, twoWireY);
    finishStateWires(previous, 1050, twoWireY);
    finishCircuitPreset("CNOT MAP · green control / red target");
    return;
  }

  if (selection == 6) {
    ZXNode magic = addNode("Z", 430, 400, "π/4");
    magic.phase = PI / 4.0;
    ZXNode output = addBoundary("output", 0, 850, 400);
    addEdge(magic, output);
    finishCircuitPreset("T MAGIC STATE · |0〉 + exp(iπ/4)|1〉");
    return;
  }

  if (selection == 7) {
    ZXNode[] previous = beginZeroStateWires(4, fourWireY);
    finishStateWires(previous, 850, fourWireY);
    finishCircuitPreset("PRODUCT STATE · |0000〉");
    return;
  }

  if (selection == 8) {
    float[] twoWireY = {300, 500};
    ZXNode[] previous = new ZXNode[2];
    for (int qubit = 0; qubit < 2; qubit++) {
      previous[qubit] = addBoundary(
        "input",
        qubit,
        90,
        twoWireY[qubit]
      );
    }
    appendCNOTGate(previous, 0, 1, 330, twoWireY);
    appendCNOTGate(previous, 1, 0, 600, twoWireY);
    appendCNOTGate(previous, 0, 1, 870, twoWireY);
    finishStateWires(previous, 1160, twoWireY);
    finishCircuitPreset("SWAP MAP · CX(0,1), CX(1,0), CX(0,1)");
    return;
  }

  if (selection == 9) {
    ZXNode[] previous = new ZXNode[4];
    for (int qubit = 0; qubit < 4; qubit++) {
      previous[qubit] = addBoundary(
        "input",
        qubit,
        70,
        fourWireY[qubit]
      );
    }
    appendHadamardGate(previous, 0, 230, fourWireY);
    appendHadamardGate(previous, 0, 440, fourWireY);
    appendZPhaseGate(previous, 1, 230, -PI / 4.0, fourWireY);
    appendZPhaseGate(previous, 1, 440, PI / 4.0, fourWireY);
    appendZPhaseGate(previous, 2, 170, PI / 4.0, fourWireY);
    appendZPhaseGate(previous, 2, 300, PI / 4.0, fourWireY);
    appendZPhaseGate(previous, 2, 440, -PI / 2.0, fourWireY);
    appendCNOTGate(previous, 2, 3, 660, fourWireY);
    appendCNOTGate(previous, 2, 3, 890, fourWireY);
    finishStateWires(previous, 1160, fourWireY);
    finishCircuitPreset(
      "IDENTITY LAB · H² · T†T · TT S† · CX²"
    );
    return;
  }

  if (selection == 10) {
    buildGraphStatePreset("RING");
    return;
  }

  if (selection == 11) {
    buildGraphStatePreset("STAR");
    return;
  }

  if (selection == 12) {
    buildGraphStatePreset("COMPLETE");
    return;
  }

  if (selection == 13) {
    buildPhaseGadgetFusionPreset();
    return;
  }

  if (selection == 14) {
    buildLocalComplementationPreset();
    return;
  }

  if (selection == 15) {
    buildPivotPreset();
    return;
  }

  if (selection == 16) {
    buildTeleportationCPTPPreset();
    return;
  }

  densityPanelVisible = false;
  statusText = "unknown circuit preset";
}


void beginPauliInput() {
  pauliInputMode = true;
  pauliInputText = "";
  statusText = "type four symbols from I X Y Z, then press Return";
}


void handlePauliInputKey() {
  if (keyCode == ESC) {
    key = 0;
    pauliInputMode = false;
    pauliInputText = "";
    statusText = "Pauli gadget entry cancelled";
    return;
  }
  if (keyCode == BACKSPACE || keyCode == DELETE) {
    if (pauliInputText.length() > 0) {
      pauliInputText = pauliInputText.substring(0, pauliInputText.length() - 1);
    }
    return;
  }
  if (keyCode == ENTER || keyCode == RETURN) {
    if (pauliInputText.length() != 4) {
      statusText = "Pauli label needs four symbols, for example XYZI";
      return;
    }
    if (pauliInputText.equals("IIII")) {
      statusText = "IIII is the identity; choose at least one X, Y, or Z";
      return;
    }
    String label = pauliInputText;
    pauliInputMode = false;
    pauliInputText = "";
    buildPauliGadget(label, PI / 4.0);
    return;
  }

  char symbol = Character.toUpperCase(key);
  if (
    pauliInputText.length() < 4
    && (symbol == 'I' || symbol == 'X' || symbol == 'Y' || symbol == 'Z')
  ) {
    pauliInputText += symbol;
  }
}


void clearActivePauli() {
  activePauliLabel = "";
  activePauliCentralNodeId = -1;
  activePauliTheta = PI / 4.0;
  activePauliExpectation = 0;
  activePauliVerified = false;
  activePauliError = 0;
  activePauliGadgetId = -1;
}


void clearPauliScore() {
  pauliScore.clear();
  pauliScoreMode = false;
  nextPauliGadgetId = 1;
  draggingPauliGadgetId = -1;
  pauliViewMode = "ZX";
}


int pauliWeight(String label) {
  int weight = 0;
  for (int qubit = 0; qubit < label.length(); qubit++) {
    if (label.charAt(qubit) != 'I') weight += 1;
  }
  return weight;
}


int pauliHadamardCount(String label) {
  int count = 0;
  for (int qubit = 0; qubit < label.length(); qubit++) {
    char axis = label.charAt(qubit);
    if (axis == 'X' || axis == 'Y') count += 2;
  }
  return count;
}


void buildPauliGadget(String label, float theta) {
  if (pauliScoreMode && pauliScore.size() >= 8) {
    statusText = "the visual score currently supports at most eight gadgets";
    return;
  }
  if (!pauliScoreMode) {
    invalidateLiveEulerSelection();
    nodes.clear();
    edges.clear();
    pauliScore.clear();
    nextPauliGadgetId = 1;
    pauliScoreMode = true;
    densityPanelVisible = false;
  }
  PauliGadgetMacro gadget = new PauliGadgetMacro(
    nextPauliGadgetId++,
    label,
    theta
  );
  pauliScore.add(gadget);
  rebuildPauliScoreGraph(gadget.id, true);
  statusText = (
    label + " appended as gadget " + pauliScore.size()
    + " · ordered score verification pending"
  );
}


void rebuildPauliScoreGraph(int selectedGadgetId, boolean transmit) {
  invalidateLiveEulerSelection();
  nodes.clear();
  edges.clear();
  nextNodeId = 1;
  pauliScoreMode = true;
  float[] wireY = {165, 275, 385, 495};
  ZXNode[] previous = new ZXNode[4];
  for (int qubit = 0; qubit < 4; qubit++) {
    previous[qubit] = addBoundary("input", qubit, 55, wireY[qubit]);
  }

  float scoreLeft = 150;
  float scoreRight = 1090;
  float slotWidth = (scoreRight - scoreLeft) / max(1, pauliScore.size());
  for (int scoreIndex = 0; scoreIndex < pauliScore.size(); scoreIndex++) {
    PauliGadgetMacro gadget = pauliScore.get(scoreIndex);
    float centerX = scoreLeft + (scoreIndex + 0.5) * slotWidth;
    float basisOffset = min(42, slotWidth * 0.16);
    gadget.centerX = centerX;
    ZXNode[] anchors = new ZXNode[4];

    for (int qubit = 0; qubit < 4; qubit++) {
      char axis = gadget.label.charAt(qubit);
      if (axis == 'Y') {
        ZXNode leftS = addNode(
          "Z",
          centerX - 2.0 * basisOffset,
          wireY[qubit],
          "−π/2"
        );
        leftS.phase = -PI / 2.0;
        tagPauliNode(leftS, gadget.id, "basis");
        addEdge(previous[qubit], leftS);
        previous[qubit] = leftS;
      }
      if (axis == 'X' || axis == 'Y') {
        ZXNode leftH = addNode(
          "H",
          centerX - basisOffset,
          wireY[qubit],
          ""
        );
        tagPauliNode(leftH, gadget.id, "basis");
        addEdge(previous[qubit], leftH);
        previous[qubit] = leftH;
      }
      if (axis != 'I') {
        ZXNode anchor = addNode("Z", centerX, wireY[qubit], "0");
        tagPauliNode(anchor, gadget.id, "anchor");
        addEdge(previous[qubit], anchor);
        previous[qubit] = anchor;
        anchors[qubit] = anchor;
      }
      if (axis == 'X' || axis == 'Y') {
        ZXNode rightH = addNode(
          "H",
          centerX + basisOffset,
          wireY[qubit],
          ""
        );
        tagPauliNode(rightH, gadget.id, "basis");
        addEdge(previous[qubit], rightH);
        previous[qubit] = rightH;
      }
      if (axis == 'Y') {
        ZXNode rightS = addNode(
          "Z",
          centerX + 2.0 * basisOffset,
          wireY[qubit],
          "π/2"
        );
        rightS.phase = PI / 2.0;
        tagPauliNode(rightS, gadget.id, "basis");
        addEdge(previous[qubit], rightS);
        previous[qubit] = rightS;
      }
    }

    ZXNode hub = addNode("Z", centerX, 585, "0");
    tagPauliNode(hub, gadget.id, "hub");
    ZXNode phaseSpider = addNode(
      "Z",
      centerX,
      680,
      phaseLabel(gadget.theta)
    );
    phaseSpider.phase = gadget.theta;
    tagPauliNode(phaseSpider, gadget.id, "phase");
    gadget.phaseNodeId = phaseSpider.id;
    for (int qubit = 0; qubit < 4; qubit++) {
      if (anchors[qubit] != null) {
        addEdge(anchors[qubit], hub, "hadamard");
      }
    }
    addEdge(hub, phaseSpider, "hadamard");
  }

  for (int qubit = 0; qubit < 4; qubit++) {
    ZXNode output = addBoundary("output", qubit, 1225, wireY[qubit]);
    addEdge(previous[qubit], output);
  }

  setPauliScoreScalar(false);
  clearSelection();
  setActivePauliGadget(selectedGadgetId, true);
  activePauliVerified = false;
  if (transmit) {
    sendGraphSnapshot();
    sendPauliScore();
    sendPauliActive();
  }
  markDensityDirty();
}


void tagPauliNode(ZXNode node, int gadgetId, String role) {
  node.pauliGadgetId = gadgetId;
  node.pauliRole = role;
}


PauliGadgetMacro pauliGadgetWithId(int gadgetId) {
  for (PauliGadgetMacro gadget : pauliScore) {
    if (gadget.id == gadgetId) return gadget;
  }
  return null;
}


int pauliGadgetIndex(int gadgetId) {
  for (int index = 0; index < pauliScore.size(); index++) {
    if (pauliScore.get(index).id == gadgetId) return index;
  }
  return -1;
}


PauliGadgetMacro pauliGadgetNearestX(float x) {
  if (pauliScore.size() == 0) return null;
  PauliGadgetMacro closest = pauliScore.get(0);
  float distance = abs(x - closest.centerX);
  for (PauliGadgetMacro gadget : pauliScore) {
    float candidate = abs(x - gadget.centerX);
    if (candidate < distance) {
      closest = gadget;
      distance = candidate;
    }
  }
  return closest;
}


int pauliScoreIndexNearestX(float x) {
  PauliGadgetMacro gadget = pauliGadgetNearestX(x);
  return gadget == null ? 0 : pauliGadgetIndex(gadget.id);
}


void reorderPauliGadget(int gadgetId, int destination) {
  int source = pauliGadgetIndex(gadgetId);
  if (source < 0) return;
  destination = constrain(destination, 0, pauliScore.size() - 1);
  PauliGadgetMacro moving = pauliScore.get(source);
  boolean semanticsPreserved = true;
  int low = min(source, destination);
  int high = max(source, destination);
  for (int index = low; index <= high; index++) {
    PauliGadgetMacro crossed = pauliScore.get(index);
    if (
      crossed.id != moving.id
      && !pauliStringsCommute(moving.label, crossed.label)
    ) {
      semanticsPreserved = false;
    }
  }
  if (source != destination) {
    pauliScore.remove(source);
    pauliScore.add(destination, moving);
  }
  rebuildPauliScoreGraph(gadgetId, true);
  statusText = (
    moving.label + " moved to position " + (destination + 1)
    + (
      semanticsPreserved
      ? " · commuting reorder preserves the unitary"
      : " · noncommuting reorder intentionally changes the score"
    )
  );
}


void setActivePauliGadget(int gadgetId, boolean selectPhaseNode) {
  PauliGadgetMacro gadget = pauliGadgetWithId(gadgetId);
  if (gadget == null) {
    clearActivePauli();
    return;
  }
  activePauliGadgetId = gadget.id;
  activePauliLabel = gadget.label;
  activePauliTheta = gadget.theta;
  activePauliCentralNodeId = gadget.phaseNodeId;
  if (selectPhaseNode) {
    ZXNode phaseNode = nodeWithId(gadget.phaseNodeId);
    if (phaseNode != null) phaseNode.selected = true;
  }
}


void setPauliScoreScalar(boolean transmit) {
  float scalarReal = 1.0;
  float scalarImag = 0.0;
  for (PauliGadgetMacro gadget : pauliScore) {
    int weight = pauliWeight(gadget.label);
    int hadamards = pauliHadamardCount(gadget.label);
    float normalization = pow(2.0, 0.5 * (weight - 1 - hadamards));
    float gadgetReal = normalization * cos(gadget.theta / 2.0);
    float gadgetImag = -normalization * sin(gadget.theta / 2.0);
    float nextReal = scalarReal * gadgetReal - scalarImag * gadgetImag;
    float nextImag = scalarReal * gadgetImag + scalarImag * gadgetReal;
    scalarReal = nextReal;
    scalarImag = nextImag;
  }
  diagramScalarReal = scalarReal;
  diagramScalarImag = scalarImag;
  if (transmit) sendGraphScalar();
}


void updateActivePauliScalar() {
  setPauliScoreScalar(true);
}


void sendPauliGadget() {
  sendPauliScore();
  sendPauliActive();
}


void sendPauliScore() {
  if (!pauliScoreMode || pauliScore.size() == 0) return;
  OscMessage message = new OscMessage("/qmw/zx/pauli/score");
  message.add(pauliScore.size());
  for (PauliGadgetMacro gadget : pauliScore) {
    message.add(gadget.id);
    message.add(gadget.label);
    message.add(gadget.theta);
  }
  oscP5.send(message, pythonVerifierTarget);
}


void sendPauliActive() {
  PauliGadgetMacro gadget = pauliGadgetWithId(activePauliGadgetId);
  if (gadget == null) return;
  OscMessage message = new OscMessage("/qmw/zx/pauli/active");
  message.add(gadget.id);
  message.add(gadget.label);
  message.add(gadget.theta);
  message.add(gadget.phaseNodeId);
  oscP5.send(message, pythonVerifierTarget);
}


boolean liveEulerContains(int nodeId) {
  return liveEulerNodeIds.contains(Integer.valueOf(nodeId));
}


void clearLiveEulerSelection() {
  liveEulerNodeIds.clear();
  eulerLiveEnabled = false;
  eulerDirty = false;
  pendingEulerRequestId = -1;
}


void invalidateLiveEulerSelection() {
  boolean wasLive = eulerLiveEnabled || liveEulerNodeIds.size() > 0;
  clearLiveEulerSelection();
  if (wasLive) {
    eulerVerified = false;
    eulerSource = "selection changed";
  }
}


void markLiveEulerDirty() {
  if (!eulerLiveEnabled || liveEulerNodeIds.size() == 0) return;
  eulerDirty = true;
  eulerDirtyAt = millis();
}


boolean sendEulerRequest(
  ArrayList<Integer> nodeIds,
  boolean liveUpdate
) {
  if (nodeIds.size() == 0) {
    invalidateLiveEulerSelection();
    statusText = "live Euler selection is empty";
    return false;
  }

  for (Integer nodeId : nodeIds) {
    ZXNode node = nodeWithId(nodeId.intValue());
    if (node == null) {
      invalidateLiveEulerSelection();
      statusText = "live Euler selection no longer exists";
      return false;
    }
    if (
      !node.kind.equals("Z")
      && !node.kind.equals("X")
      && !node.kind.equals("H")
    ) {
      invalidateLiveEulerSelection();
      statusText = "Euler lens accepts selected Z, X, or H nodes only";
      return false;
    }
  }

  pendingEulerRequestId = nextEulerRequestId++;
  OscMessage message = new OscMessage("/qmw/zx/euler/request");
  message.add(pendingEulerRequestId);
  message.add(nodeIds.size());
  for (Integer nodeId : nodeIds) message.add(nodeId.intValue());
  oscP5.send(message, pythonVerifierTarget);
  eulerDirty = false;
  statusText = liveUpdate
    ? "live Euler lens evaluating phase change…"
    : (
      "Euler lens latched " + nodeIds.size()
      + " node(s) · verifying 2×2 tensor"
    );
  return true;
}


void requestLiveEulerDecomposition() {
  if (!eulerLiveEnabled) {
    eulerDirty = false;
    return;
  }
  ArrayList<Integer> nodeIds = new ArrayList<Integer>();
  nodeIds.addAll(liveEulerNodeIds);
  sendEulerRequest(nodeIds, true);
}


void requestEulerDecomposition() {
  ArrayList<ZXNode> selected = selectedNodes();
  if (selected.size() == 0) {
    eulerPanelVisible = !eulerPanelVisible;
    if (!eulerPanelVisible) clearLiveEulerSelection();
    statusText = eulerPanelVisible
      ? "Euler lens opened · select a one-wire chain and press E"
      : "Euler lens hidden · live selection released";
    return;
  }

  ArrayList<Integer> nodeIds = new ArrayList<Integer>();
  for (ZXNode node : selected) {
    if (
      !node.kind.equals("Z")
      && !node.kind.equals("X")
      && !node.kind.equals("H")
    ) {
      statusText = "Euler lens accepts selected Z, X, or H nodes only";
      return;
    }
    nodeIds.add(Integer.valueOf(node.id));
  }

  liveEulerNodeIds.clear();
  liveEulerNodeIds.addAll(nodeIds);
  eulerLiveEnabled = true;
  eulerPanelVisible = true;
  sendEulerRequest(nodeIds, false);
}


String eulerAngleLabel(float angle) {
  return nf(angle / PI, 0, 4) + "π";
}


void drawEulerAxisNode(char axis, float x, float y, String parameter) {
  stroke(28);
  strokeWeight(1.5);
  if (axis == 'Z') fill(188, 230, 176);
  else if (axis == 'X') fill(234, 156, 164);
  else fill(244, 205, 132);
  ellipse(x, y, 48, 48);
  noStroke();
  fill(30);
  textAlign(CENTER, CENTER);
  textSize(12);
  text(str(axis) + "(" + parameter + ")", x, y - 1);
}


void drawEulerPanel() {
  float centerX = width - 275;
  float centerY = 183;
  rectMode(CENTER);
  noStroke();
  fill(255, 254, 250, 246);
  rect(centerX, centerY, 510, 182, 18);
  stroke(eulerVerified ? color(64, 139, 84) : color(156, 93, 64));
  strokeWeight(2);
  noFill();
  rect(centerX, centerY, 510, 182, 18);

  noStroke();
  fill(44);
  textAlign(LEFT, CENTER);
  textSize(14);
  text(
    "EULER LENS"
    + (eulerLiveEnabled ? (eulerDirty ? " · LIVE…" : " · LIVE") : "")
    + " · " + eulerBasis + " · " + eulerSource,
    centerX - 234,
    centerY - 70
  );
  textSize(11);
  fill(90);
  text(
    eulerVerified
      ? "verified 2×2 reconstruction · error " + str(eulerError)
      : "waiting / unverified",
    centerX - 234,
    centerY - 49
  );

  float wireY = centerY + 2;
  stroke(48);
  strokeWeight(2);
  line(centerX - 205, wireY, centerX + 205, wireY);
  char leftAxis = eulerBasis.charAt(2);
  char middleAxis = eulerBasis.charAt(1);
  char rightAxis = eulerBasis.charAt(0);
  drawEulerAxisNode(leftAxis, centerX - 112, wireY, "λ");
  drawEulerAxisNode(middleAxis, centerX, wireY, "θ");
  drawEulerAxisNode(rightAxis, centerX + 112, wireY, "φ");

  fill(58);
  textAlign(CENTER, CENTER);
  textSize(11);
  text(eulerAngleLabel(eulerLambda), centerX - 112, centerY + 39);
  text(eulerAngleLabel(eulerTheta), centerX, centerY + 39);
  text(eulerAngleLabel(eulerPhi), centerX + 112, centerY + 39);
  textAlign(LEFT, CENTER);
  text(
    "γ " + eulerAngleLabel(eulerGamma)
    + "    ZX scalar " + eulerAngleLabel(eulerZXScalarPhase)
    + (eulerQubit >= 0 ? "    q" + eulerQubit : ""),
    centerX - 205,
    centerY + 66
  );
}


void drawPauliInput() {
  rectMode(CENTER);
  noStroke();
  fill(28, 32, 39, 238);
  rect(width * 0.5, height * 0.5, 570, 190, 22);
  fill(255);
  textAlign(CENTER, CENTER);
  textSize(20);
  text("Create a four-qubit Pauli gadget", width * 0.5, height * 0.5 - 55);
  textSize(34);
  String cursor = pauliInputText.length() < 4 ? "▌" : "";
  text(pauliInputText + cursor, width * 0.5, height * 0.5);
  textSize(13);
  fill(205);
  text(
    "I = no connection   Z = direct   X = H basis   Y = S†H basis   ·   Return",
    width * 0.5,
    height * 0.5 + 58
  );
}


void drawGHZInput() {
  rectMode(CENTER);
  noStroke();
  fill(24, 42, 31, 242);
  rect(width * 0.5, height * 0.5, 570, 205, 22);
  fill(255);
  textAlign(CENTER, CENTER);
  textSize(20);
  text(
    "Create one green GHZ spider with N outputs",
    width * 0.5,
    height * 0.5 - 62
  );
  textSize(38);
  String cursor = ghzInputText.length() < 2 ? "▌" : "";
  text(
    (ghzInputText.length() == 0 ? "N = " : "N = " + ghzInputText) + cursor,
    width * 0.5,
    height * 0.5 - 4
  );
  textSize(13);
  fill(205);
  text(
    "1–8 = exact dense preview   ·   9–64 = compact graph mode   ·   Return",
    width * 0.5,
    height * 0.5 + 64
  );
}


void drawCircuitPresetLibrary() {
  rectMode(CENTER);
  noStroke();
  fill(23, 28, 40, 246);
  rect(width * 0.5, height * 0.5, 1120, 650, 24);

  fill(255);
  textAlign(CENTER, CENTER);
  textSize(23);
  text(
    "Circuit programmer → expanded ZX library",
    width * 0.5,
    height * 0.5 - 290
  );
  textSize(12);
  fill(190, 201, 222);
  text(
    "Choose 1–9 or A–G · every preset is a real editable graph evaluated by PyZX",
    width * 0.5,
    height * 0.5 - 257
  );

  String[] labels = {
    "1   QAC BELL",
    "2   QAC GHZ₄",
    "3   QAC WEAVE",
    "4   CLUSTER₄",
    "5   CNOT MAP",
    "6   T MAGIC STATE",
    "7   PRODUCT |0000〉",
    "8   SWAP = 3 CNOTs",
    "9   IDENTITY LAB",
    "A   RING GRAPH₄",
    "B   STAR GRAPH₄",
    "C   COMPLETE GRAPH₄",
    "D   PHASE FUSION",
    "E   LOCAL COMPLEMENT",
    "F   PIVOT",
    "G   TELEPORT CPTP"
  };
  String[] details = {
    "H(q0) · CX(0,1) · q2/q3 remain |0〉",
    "H(q0) · CX(0,1) · CX(1,2) · CX(2,3)",
    "exact Max preset: H×4 · three CX · T(q0) · S(q3)",
    "canonical graph state with Hadamard entangling edges",
    "two-input/two-output unitary ZX macro",
    "one-output green π/4 state spider",
    "four independent red zero-state spiders",
    "CX(0,1) · CX(1,0) · CX(0,1)",
    "H² · T†T · TT S† · CX² all reduce to identity",
    "four-cycle graph state",
    "GHZ-equivalent graph topology",
    "all six graph edges on four qubits",
    "ZZII π/4 + π/8 · selected and ready for F",
    "π/2 interior spider · press lowercase w",
    "interior Pauli pair · press Shift-W",
    "coherent outcomes · X/Z corrections · discard"
  };

  float startY = height * 0.5 - 205;
  for (int index = 0; index < labels.length; index++) {
    int column = index / 8;
    int row = index % 8;
    float x = width * 0.5 - 272 + column * 544;
    float y = startY + row * 51;
    fill(index < 3 ? color(50, 67, 103) : color(43, 50, 65));
    rect(x, y, 516, 42, 11);
    fill(index < 3 ? color(224, 233, 255) : color(238));
    textAlign(LEFT, CENTER);
    textSize(12);
    text(labels[index], x - 240, y - 8);
    fill(177, 185, 202);
    textSize(9);
    text(details[index], x - 240, y + 10);
  }

  textAlign(CENTER, CENTER);
  textSize(11);
  fill(160, 169, 188);
  text(
    "Outside this library: 2 = compact Bell spider · 4 = compact GHZ₄ spider · Esc closes",
    width * 0.5,
    height * 0.5 + 300
  );
}


void cyclePauliView() {
  if (!pauliScoreMode) {
    statusText = "create a Pauli score with J before changing synthesis view";
    return;
  }
  if (pauliViewMode.equals("ZX")) pauliViewMode = "LADDER";
  else if (pauliViewMode.equals("LADDER")) pauliViewMode = "TREE";
  else pauliViewMode = "ZX";
  statusText = "Pauli score view · " + pauliViewMode;
}


ArrayList<PauliGadgetMacro> selectedPauliGadgets() {
  ArrayList<PauliGadgetMacro> selected = new ArrayList<PauliGadgetMacro>();
  for (ZXNode node : nodes) {
    if (!node.selected || node.pauliGadgetId < 0) continue;
    PauliGadgetMacro gadget = pauliGadgetWithId(node.pauliGadgetId);
    if (gadget != null && !selected.contains(gadget)) selected.add(gadget);
  }
  return selected;
}


boolean pauliStringsCommute(String left, String right) {
  int anticommutingSites = 0;
  for (int qubit = 0; qubit < 4; qubit++) {
    char a = left.charAt(qubit);
    char b = right.charAt(qubit);
    if (a != 'I' && b != 'I' && a != b) anticommutingSites += 1;
  }
  return anticommutingSites % 2 == 0;
}


boolean pauliGadgetsCanFuse(PauliGadgetMacro first, PauliGadgetMacro second) {
  if (first == null || second == null || !first.label.equals(second.label)) {
    return false;
  }
  int low = min(pauliGadgetIndex(first.id), pauliGadgetIndex(second.id));
  int high = max(pauliGadgetIndex(first.id), pauliGadgetIndex(second.id));
  if (low < 0 || high <= low) return false;
  for (int index = low + 1; index < high; index++) {
    if (!pauliStringsCommute(first.label, pauliScore.get(index).label)) {
      return false;
    }
  }
  return true;
}


void drawPauliMacroBands() {
  rectMode(CENTER);
  for (PauliGadgetMacro gadget : pauliScore) {
    ZXNode phase = nodeWithId(gadget.phaseNodeId);
    boolean selected = phase != null && phase.selected;
    noStroke();
    fill(
      selected
      ? color(65, 108, 196, 22)
      : color(80, 84, 92, 8)
    );
    float bandWidth = max(72, 860.0 / max(1, pauliScore.size()) - 10);
    rect(gadget.centerX, 405, bandWidth, 610, 14);
    fill(selected ? color(45, 78, 145) : color(94));
    textAlign(CENTER, CENTER);
    textSize(12);
    text(
      (pauliGadgetIndex(gadget.id) + 1) + " · " + gadget.label,
      gadget.centerX,
      94
    );
  }
}


void drawPauliRelationCue() {
  ArrayList<PauliGadgetMacro> selected = selectedPauliGadgets();
  if (selected.size() != 2) return;
  PauliGadgetMacro first = selected.get(0);
  PauliGadgetMacro second = selected.get(1);
  boolean commute = pauliStringsCommute(first.label, second.label);
  boolean fusible = pauliGadgetsCanFuse(first, second);
  rectMode(CENTER);
  noStroke();
  fill(
    fusible
    ? color(220, 244, 226, 248)
    : (commute ? color(226, 238, 250, 248) : color(252, 229, 219, 248))
  );
  rect(width * 0.5, 112, 520, 38, 16);
  fill(
    fusible
    ? color(36, 105, 58)
    : (commute ? color(44, 83, 132) : color(142, 67, 50))
  );
  textAlign(CENTER, CENTER);
  textSize(13);
  String relation = fusible
    ? "FUSIBLE · press F"
    : (commute ? "COMMUTE · safe to reorder" : "ANTICOMMUTE · order matters");
  text(first.label + "  ↔  " + second.label + "    " + relation, width * 0.5, 111);
}


void drawPauliCircuitView() {
  float[] wireY = {190, 300, 410, 520};
  stroke(36);
  strokeWeight(2);
  for (int qubit = 0; qubit < 4; qubit++) {
    line(55, wireY[qubit], 1225, wireY[qubit]);
    noStroke();
    fill(70);
    textAlign(LEFT, CENTER);
    textSize(12);
    text("q" + qubit, 20, wireY[qubit]);
    stroke(36);
  }
  noStroke();
  fill(48);
  textAlign(CENTER, CENTER);
  textSize(18);
  text(
    pauliViewMode.equals("LADDER")
      ? "CNOT ladder synthesis · depth 2(weight−1)"
      : "balanced-tree synthesis · depth 2⌈log₂(weight)⌉",
    width * 0.5,
    82
  );

  for (PauliGadgetMacro gadget : pauliScore) {
    boolean selected = gadget.id == activePauliGadgetId;
    rectMode(CENTER);
    noStroke();
    fill(selected ? color(65, 108, 196, 26) : color(80, 84, 92, 8));
    float bandWidth = max(78, 860.0 / max(1, pauliScore.size()) - 12);
    rect(gadget.centerX, 365, bandWidth, 560, 14);
    fill(selected ? color(45, 78, 145) : color(75));
    textAlign(CENTER, CENTER);
    textSize(13);
    text(gadget.label, gadget.centerX, 118);

    if (pauliViewMode.equals("LADDER")) {
      drawPauliLadder(gadget, wireY);
    } else {
      drawPauliTree(gadget, wireY);
    }
  }
}


void drawAxisBadge(char axis, float x, float y) {
  if (axis == 'I') return;
  rectMode(CENTER);
  stroke(28);
  strokeWeight(1.5);
  if (axis == 'Z') fill(188, 230, 176);
  else if (axis == 'X') fill(234, 156, 164);
  else fill(244, 205, 132);
  rect(x, y, 25, 25, 5);
  noStroke();
  fill(32);
  textAlign(CENTER, CENTER);
  textSize(12);
  text(str(axis), x, y - 1);
}


void drawCnotMark(float x, float controlY, float targetY) {
  stroke(32);
  strokeWeight(1.8);
  line(x, controlY, x, targetY);
  noStroke();
  fill(32);
  ellipse(x, controlY, 9, 9);
  noFill();
  stroke(32);
  ellipse(x, targetY, 18, 18);
  line(x - 7, targetY, x + 7, targetY);
  line(x, targetY - 7, x, targetY + 7);
}


void drawPauliLadder(PauliGadgetMacro gadget, float[] wireY) {
  IntList active = new IntList();
  for (int qubit = 0; qubit < 4; qubit++) {
    char axis = gadget.label.charAt(qubit);
    if (axis != 'I') {
      active.append(qubit);
      drawAxisBadge(axis, gadget.centerX - 42, wireY[qubit]);
      drawAxisBadge(axis, gadget.centerX + 42, wireY[qubit]);
    }
  }
  for (int index = 0; index < active.size() - 1; index++) {
    float offset = -24 + index * 10;
    drawCnotMark(
      gadget.centerX + offset,
      wireY[active.get(index)],
      wireY[active.get(index + 1)]
    );
    drawCnotMark(
      gadget.centerX - offset,
      wireY[active.get(index)],
      wireY[active.get(index + 1)]
    );
  }
  int pivot = active.get(active.size() - 1);
  rectMode(CENTER);
  stroke(28);
  fill(188, 230, 176);
  rect(gadget.centerX, wireY[pivot], 54, 30, 6);
  noStroke();
  fill(28);
  textAlign(CENTER, CENTER);
  textSize(11);
  text("Rz " + phaseLabel(gadget.theta), gadget.centerX, wireY[pivot] - 1);
}


void drawPauliTree(PauliGadgetMacro gadget, float[] wireY) {
  IntList active = new IntList();
  for (int qubit = 0; qubit < 4; qubit++) {
    char axis = gadget.label.charAt(qubit);
    if (axis == 'I') continue;
    active.append(qubit);
    drawAxisBadge(axis, gadget.centerX - 48, wireY[qubit]);
    drawAxisBadge(axis, gadget.centerX + 48, wireY[qubit]);
  }

  IntList representatives = new IntList();
  for (int index = 0; index < active.size(); index += 2) {
    if (index + 1 < active.size()) {
      int control = active.get(index);
      int target = active.get(index + 1);
      drawCnotMark(gadget.centerX - 25, wireY[control], wireY[target]);
      drawCnotMark(gadget.centerX + 25, wireY[control], wireY[target]);
      representatives.append(target);
    } else {
      representatives.append(active.get(index));
    }
  }
  if (representatives.size() > 1) {
    int control = representatives.get(0);
    int target = representatives.get(1);
    drawCnotMark(gadget.centerX - 7, wireY[control], wireY[target]);
    drawCnotMark(gadget.centerX + 7, wireY[control], wireY[target]);
  }
  int pivot = representatives.get(representatives.size() - 1);
  rectMode(CENTER);
  stroke(28);
  fill(188, 230, 176);
  rect(gadget.centerX, wireY[pivot], 54, 30, 6);
  noStroke();
  fill(28);
  textAlign(CENTER, CENTER);
  textSize(11);
  text("Rz " + phaseLabel(gadget.theta), gadget.centerX, wireY[pivot] - 1);
}


void applyNamedRewrite(String ruleId) {
  ArrayList<ZXNode> selected = selectedNodes();
  if (selected.size() == 0) {
    statusText = "select the " + ruleId.replace("_", " ") + " pattern first";
    rewriteFeedback = "NO PATTERN SELECTED  ·  " + ruleId.replace("_", " ");
    rewriteFeedbackSuccess = false;
    rewriteFeedbackUntil = millis() + 2600;
    return;
  }

  invalidateLiveEulerSelection();
  OscMessage message = new OscMessage("/qmw/zx/rewrite/apply");
  message.add(ruleId);
  message.add(selected.size());
  for (ZXNode node : selected) message.add(node.id);
  oscP5.send(message, pythonVerifierTarget);
  statusText = (
    ruleId.replace("_", " ")
    + " sent to Python/PyZX · waiting for tensor verification"
  );
  rewriteFeedback = "VERIFYING " + ruleId.replace("_", " ").toUpperCase() + "…";
  rewriteFeedbackSuccess = false;
  rewriteFeedbackUntil = millis() + 5000;
}


void addCNOTAtMouse() {
  float centerX = constrain(mouseX, 165, width - 165);
  float centerY = constrain(mouseY, 125, height - 125);
  float leftX = centerX - 125;
  float rightX = centerX + 125;
  float controlY = centerY - 68;
  float targetY = centerY + 68;

  ZXNode controlInput = addNode("B", leftX, controlY, "");
  ZXNode controlSpider = addNode("Z", centerX, controlY, "0");
  ZXNode controlOutput = addNode("B", rightX, controlY, "");
  ZXNode targetInput = addNode("B", leftX, targetY, "");
  ZXNode targetSpider = addNode("X", centerX, targetY, "0");
  ZXNode targetOutput = addNode("B", rightX, targetY, "");
  controlInput.boundaryRole = "input";
  controlInput.boundaryIndex = 0;
  controlInput.label = boundaryLabel(controlInput);
  controlOutput.boundaryRole = "output";
  controlOutput.boundaryIndex = 0;
  controlOutput.label = boundaryLabel(controlOutput);
  targetInput.boundaryRole = "input";
  targetInput.boundaryIndex = 1;
  targetInput.label = boundaryLabel(targetInput);
  targetOutput.boundaryRole = "output";
  targetOutput.boundaryIndex = 1;
  targetOutput.label = boundaryLabel(targetOutput);

  ZXNode[] inserted = {
    controlInput,
    controlSpider,
    controlOutput,
    targetInput,
    targetSpider,
    targetOutput
  };
  for (ZXNode node : inserted) sendNodeAdded(node);

  addEdge(controlInput, controlSpider);
  addEdge(controlSpider, controlOutput);
  addEdge(targetInput, targetSpider);
  addEdge(targetSpider, targetOutput);
  addEdge(controlSpider, targetSpider);

  sendEdgeAdded(controlInput, controlSpider);
  sendEdgeAdded(controlSpider, controlOutput);
  sendEdgeAdded(targetInput, targetSpider);
  sendEdgeAdded(targetSpider, targetOutput);
  sendEdgeAdded(controlSpider, targetSpider);

  clearSelection();
  controlSpider.selected = true;
  targetSpider.selected = true;
  multiplyDiagramScalar(sqrt(2.0));
  statusText = "CNOT expanded to its connected Z-control / X-target spiders";
  rewriteFeedback = "CNOT IS A ZX MACRO  ·  Z control + X target";
  rewriteFeedbackSuccess = true;
  rewriteFeedbackUntil = millis() + 3200;
  markDensityDirty();
}


void addToffoliAtMouse() {
  float centerX = constrain(mouseX, 230, width - 230);
  float centerY = constrain(mouseY, 205, height - 205);
  float leftX = centerX - 190;
  float rightX = centerX + 190;
  float zX = centerX;
  float[] wireY = {centerY - 105, centerY, centerY + 105};

  ZXNode[] leftBoundary = new ZXNode[3];
  ZXNode[] rightBoundary = new ZXNode[3];
  ZXNode[] zSpider = new ZXNode[3];
  for (int wire = 0; wire < 3; wire++) {
    leftBoundary[wire] = addNode("B", leftX, wireY[wire], "");
    rightBoundary[wire] = addNode("B", rightX, wireY[wire], "");
    zSpider[wire] = addNode("Z", zX, wireY[wire], "0");
    leftBoundary[wire].boundaryRole = "input";
    leftBoundary[wire].boundaryIndex = wire;
    leftBoundary[wire].label = boundaryLabel(leftBoundary[wire]);
    rightBoundary[wire].boundaryRole = "output";
    rightBoundary[wire].boundaryIndex = wire;
    rightBoundary[wire].label = boundaryLabel(rightBoundary[wire]);
  }

  ZXNode targetHIn = addNode("H", centerX - 92, wireY[2], "");
  ZXNode targetHOut = addNode("H", centerX + 92, wireY[2], "");
  ZXNode centralHBox = addNode("HB", centerX + 58, centerY, "−1");
  centralHBox.phase = PI;

  ArrayList<ZXNode> inserted = new ArrayList<ZXNode>();
  for (int wire = 0; wire < 3; wire++) {
    inserted.add(leftBoundary[wire]);
    inserted.add(zSpider[wire]);
    inserted.add(rightBoundary[wire]);
  }
  inserted.add(targetHIn);
  inserted.add(targetHOut);
  inserted.add(centralHBox);
  for (ZXNode node : inserted) sendNodeAdded(node);

  for (int wire = 0; wire < 2; wire++) {
    addEdge(leftBoundary[wire], zSpider[wire]);
    addEdge(zSpider[wire], rightBoundary[wire]);
    sendEdgeAdded(leftBoundary[wire], zSpider[wire]);
    sendEdgeAdded(zSpider[wire], rightBoundary[wire]);
  }
  addEdge(leftBoundary[2], targetHIn);
  addEdge(targetHIn, zSpider[2]);
  addEdge(zSpider[2], targetHOut);
  addEdge(targetHOut, rightBoundary[2]);
  sendEdgeAdded(leftBoundary[2], targetHIn);
  sendEdgeAdded(targetHIn, zSpider[2]);
  sendEdgeAdded(zSpider[2], targetHOut);
  sendEdgeAdded(targetHOut, rightBoundary[2]);

  for (int wire = 0; wire < 3; wire++) {
    addEdge(zSpider[wire], centralHBox);
    sendEdgeAdded(zSpider[wire], centralHBox);
  }

  clearSelection();
  for (ZXNode node : zSpider) node.selected = true;
  centralHBox.selected = true;
  multiplyDiagramScalar(0.5);
  statusText = "compact ZXH Toffoli inserted · three Z spiders + three H-boxes";
  rewriteFeedback = "TOFFOLI  ·  H(target) · CCZ H-box · H(target)";
  rewriteFeedbackSuccess = true;
  rewriteFeedbackUntil = millis() + 4200;
  markDensityDirty();
}


void copySelection() {
  ArrayList<ZXNode> selected = selectedNodes();
  if (selected.size() == 0) {
    statusText = "select diagram elements before pressing ⌘C";
    return;
  }

  clipboardNodes.clear();
  clipboardEdges.clear();
  pasteGeneration = 0;

  float centerX = 0;
  float centerY = 0;
  for (ZXNode node : selected) {
    centerX += node.x;
    centerY += node.y;
  }
  centerX /= selected.size();
  centerY /= selected.size();

  for (ZXNode node : selected) {
    clipboardNodes.add(
      new ZXClipboardNode(
        node.id,
        node.kind,
        node.x - centerX,
        node.y - centerY,
        node.phase,
        node.label,
        node.boundaryRole,
        node.boundaryIndex
      )
    );
  }

  for (ZXEdge edge : edges) {
    if (edge.a.selected && edge.b.selected) {
      clipboardEdges.add(
        new ZXClipboardEdge(
          edge.a.id,
          edge.b.id,
          edge.bend,
          edge.kind
        )
      );
    }
  }

  statusText = (
    "copied " + clipboardNodes.size()
    + " nodes and " + clipboardEdges.size() + " internal wires"
  );
}


void pasteClipboard() {
  if (clipboardNodes.size() == 0) {
    statusText = "the ZX clipboard is empty";
    return;
  }

  pasteGeneration += 1;
  float offset = 22.0 * pasteGeneration;
  float centerX = constrain(mouseX + offset, 165, width - 165);
  float centerY = constrain(mouseY + offset, 125, height - 125);
  HashMap<Integer, ZXNode> pasted = new HashMap<Integer, ZXNode>();

  clearSelection();
  for (ZXClipboardNode item : clipboardNodes) {
    ZXNode node = addNode(
      item.kind,
      constrain(centerX + item.relativeX, 28, width - 28),
      constrain(centerY + item.relativeY, 55, height - 55),
      item.label
    );
    node.phase = item.phase;
    node.boundaryRole = item.boundaryRole;
    node.boundaryIndex = item.boundaryIndex;
    node.selected = true;
    pasted.put(item.originalId, node);
    sendNodeAdded(node);
  }

  for (ZXClipboardEdge item : clipboardEdges) {
    ZXNode a = pasted.get(item.sourceId);
    ZXNode b = pasted.get(item.targetId);
    if (a != null && b != null) {
      addEdge(a, b, item.kind);
      sendEdgeAdded(a, b, item.kind);
    }
  }

  statusText = (
    "pasted " + pasted.size()
    + " nodes · the duplicate is selected"
  );
  markDensityDirty();
}


ZXNode nodeAt(float x, float y) {
  for (int i = nodes.size() - 1; i >= 0; i--) {
    ZXNode node = nodes.get(i);
    float radius = node.kind.equals("B") ? 16 : 31;
    if (node.kind.equals("D")) radius = 27;
    if (node.kind.equals("HB")) radius = 36;
    if (dist(x, y, node.x, node.y) <= radius) return node;
  }
  return null;
}


void clearSelection() {
  for (ZXNode node : nodes) node.selected = false;
}


void deleteSelected() {
  if (pauliScoreMode) {
    ArrayList<PauliGadgetMacro> selectedGadgets = selectedPauliGadgets();
    if (selectedGadgets.size() > 0) {
      for (PauliGadgetMacro gadget : selectedGadgets) {
        pauliScore.remove(gadget);
      }
      if (pauliScore.size() == 0) {
        resetGraph();
        statusText = "last Pauli gadget removed · starter graph restored";
      } else {
        int selectedId = pauliScore.get(0).id;
        rebuildPauliScoreGraph(selectedId, true);
        statusText = selectedGadgets.size() + " Pauli gadget(s) removed";
      }
      return;
    }
  }

  boolean deletingLiveEuler = false;
  for (ZXNode node : nodes) {
    if (node.selected && liveEulerContains(node.id)) {
      deletingLiveEuler = true;
    }
  }
  for (ZXNode node : nodes) {
    if (node.selected) sendNodeDeleted(node);
  }
  for (int i = edges.size() - 1; i >= 0; i--) {
    ZXEdge edge = edges.get(i);
    if (edge.a.selected || edge.b.selected) edges.remove(i);
  }
  for (int i = nodes.size() - 1; i >= 0; i--) {
    if (nodes.get(i).selected) nodes.remove(i);
  }
  if (deletingLiveEuler) invalidateLiveEulerSelection();
  statusText = "selection removed";
  markDensityDirty();
}


void fuseSelectedSpiders() {
  if (fuseSelectedPauliGadgets()) return;

  ArrayList<ZXNode> selected = selectedNodes();

  if (!fusionSelectionReady()) {
    statusText = "fusion needs two connected Z spiders or two connected X spiders";
    rewriteFeedback = "NOT FUSABLE  ·  select two connected spiders of one color";
    rewriteFeedbackSuccess = false;
    rewriteFeedbackUntil = millis() + 2600;
    return;
  }

  ZXNode keep = selected.get(0);
  ZXNode remove = selected.get(1);
  if (
    liveEulerContains(keep.id)
    || liveEulerContains(remove.id)
  ) {
    invalidateLiveEulerSelection();
  }
  keep.x = (keep.x + remove.x) * 0.5;
  keep.y = (keep.y + remove.y) * 0.5;
  keep.phase += remove.phase;
  keep.label = phaseLabel(keep.phase);

  for (int i = edges.size() - 1; i >= 0; i--) {
    ZXEdge edge = edges.get(i);
    if (
      (edge.a == keep && edge.b == remove)
      || (edge.a == remove && edge.b == keep)
    ) {
      edges.remove(i);
      continue;
    }
    if (edge.a == remove) edge.a = keep;
    if (edge.b == remove) edge.b = keep;
    if (edge.a == edge.b) edges.remove(i);
  }

  removeDuplicateEdges();
  nodes.remove(remove);
  clearSelection();
  keep.selected = true;
  sendRewriteFusion(keep, remove);
  statusText = "fusion sent to Python · waiting for semantic verification";
  rewriteFeedback = "VERIFYING " + keep.kind + " FUSION…";
  rewriteFeedbackSuccess = false;
  rewriteFeedbackUntil = millis() + 4000;
  markDensityDirty();
}


boolean fuseSelectedPauliGadgets() {
  if (!pauliScoreMode) return false;
  ArrayList<PauliGadgetMacro> selected = selectedPauliGadgets();
  if (selected.size() != 2) return false;
  PauliGadgetMacro first = selected.get(0);
  PauliGadgetMacro second = selected.get(1);
  if (!pauliGadgetsCanFuse(first, second)) {
    statusText = (
      "whole-gadget fusion requires equal labels and only commuting gadgets between them"
    );
    rewriteFeedback = (
      "NOT FUSABLE  ·  " + first.label + " and " + second.label
    );
    rewriteFeedbackSuccess = false;
    rewriteFeedbackUntil = millis() + 3600;
    return true;
  }

  int firstIndex = pauliGadgetIndex(first.id);
  int secondIndex = pauliGadgetIndex(second.id);
  PauliGadgetMacro keep = firstIndex < secondIndex ? first : second;
  PauliGadgetMacro remove = firstIndex < secondIndex ? second : first;
  keep.theta += remove.theta;
  pauliScore.remove(remove);
  rebuildPauliScoreGraph(keep.id, true);
  rewriteFeedback = (
    "VERIFYING WHOLE-GADGET FUSION  ·  " + keep.label
    + " θ=" + phaseLabel(keep.theta)
  );
  rewriteFeedbackSuccess = false;
  rewriteFeedbackUntil = millis() + 5000;
  statusText = (
    keep.label + " gadgets fused across commuting context · PyZX checking score"
  );
  return true;
}


void removeDuplicateEdges() {
  for (int i = edges.size() - 1; i >= 0; i--) {
    ZXEdge a = edges.get(i);
    for (int j = 0; j < i; j++) {
      ZXEdge b = edges.get(j);
      if (
        (a.a == b.a && a.b == b.b)
        || (a.a == b.b && a.b == b.a)
      ) {
        edges.remove(i);
        break;
      }
    }
  }
}


String phaseLabel(float phase) {
  float units = phase / PI;
  if (abs(units) < 0.015) return "0";
  if (abs(units - 1.0) < 0.015) return "π";
  if (abs(units + 1.0) < 0.015) return "−π";
  if (abs(units - 0.5) < 0.015) return "π/2";
  if (abs(units + 0.5) < 0.015) return "−π/2";
  return nf(units, 0, 2) + "π";
}


void saveGraph() {
  JSONObject graph = new JSONObject();
  graph.setString("schema", "qmw.zx-visual-graph.v1");

  JSONArray nodeData = new JSONArray();
  for (int i = 0; i < nodes.size(); i++) {
    ZXNode node = nodes.get(i);
    JSONObject item = new JSONObject();
    item.setInt("id", node.id);
    item.setString("kind", node.kind);
    item.setFloat("x", node.x);
    item.setFloat("y", node.y);
    item.setFloat("phase_radians", node.phase);
    item.setString("boundary_role", node.boundaryRole);
    item.setInt("boundary_index", node.boundaryIndex);
    nodeData.setJSONObject(i, item);
  }

  JSONArray edgeData = new JSONArray();
  for (int i = 0; i < edges.size(); i++) {
    ZXEdge edge = edges.get(i);
    JSONObject item = new JSONObject();
    item.setInt("source", edge.a.id);
    item.setInt("target", edge.b.id);
    item.setString("kind", edge.kind);
    edgeData.setJSONObject(i, item);
  }

  graph.setJSONArray("nodes", nodeData);
  graph.setJSONArray("edges", edgeData);
  saveJSONObject(graph, sketchPath("zx_graph.json"));
  statusText = "saved zx_graph.json";
}


void oscEvent(OscMessage message) {
  if (message.checkAddrPattern("/qmw/circuit/euler/begin")) {
    circuitEulerBasis = message.get(2).stringValue();
    statusText = (
      "circuit Euler transaction · revision " + message.get(0).intValue()
      + " · " + message.get(1).intValue() + " one-qubit gates"
    );
    return;
  }

  if (message.checkAddrPattern("/qmw/circuit/euler/gate")) {
    eulerSource = (
      "circuit r" + message.get(0).intValue()
      + " · #" + message.get(1).intValue()
      + " " + message.get(2).stringValue()
    );
    eulerQubit = message.get(3).intValue();
    eulerBasis = circuitEulerBasis;
    eulerTheta = message.get(4).floatValue();
    eulerPhi = message.get(5).floatValue();
    eulerLambda = message.get(6).floatValue();
    eulerGamma = message.get(7).floatValue();
    eulerZXScalarPhase = message.get(8).floatValue();
    eulerVerified = message.get(9).intValue() == 1;
    eulerError = message.get(10).floatValue();
    eulerPanelVisible = true;
    return;
  }

  if (message.checkAddrPattern("/qmw/circuit/euler/end")) {
    statusText = (
      "circuit Euler data ready · " + message.get(1).intValue()
      + " gates · " + message.get(4).intValue() + " skipped"
    );
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/euler/result")) {
    if (message.get(0).intValue() != pendingEulerRequestId) return;
    eulerSource = message.get(1).stringValue();
    eulerQubit = message.get(2).intValue();
    eulerBasis = message.get(3).stringValue();
    eulerTheta = message.get(4).floatValue();
    eulerPhi = message.get(5).floatValue();
    eulerLambda = message.get(6).floatValue();
    eulerGamma = message.get(7).floatValue();
    eulerZXScalarPhase = message.get(8).floatValue();
    eulerVerified = message.get(9).intValue() == 1;
    eulerError = message.get(10).floatValue();
    eulerPanelVisible = true;
    if (eulerVerified) {
      statusText = eulerLiveEnabled
        ? "live Euler verified · phase edits now update Processing and Max"
        : "Euler lens verified · λ → θ → φ is the time-ordered ZX chain";
    } else {
      invalidateLiveEulerSelection();
      statusText = "Euler lens reconstruction rejected · live selection released";
    }
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/euler/error")) {
    if (message.get(0).intValue() != pendingEulerRequestId) return;
    eulerVerified = false;
    eulerPanelVisible = true;
    invalidateLiveEulerSelection();
    statusText = "Euler lens error · " + message.get(1).stringValue();
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/pauli/select")) {
    String label = message.get(0).stringValue().toUpperCase();
    PauliGadgetMacro match = null;
    for (PauliGadgetMacro gadget : pauliScore) {
      if (gadget.label.equals(label)) {
        match = gadget;
        break;
      }
    }
    if (match != null) {
      clearSelection();
      setActivePauliGadget(match.id, true);
      sendPauliActive();
      statusText = label + " selected from tomography · gadget highlighted";
    } else {
      statusText = (
        "tomography selected " + label + " · no matching score gadget"
      );
    }
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/pauli/score_verified")) {
    boolean verified = message.get(1).intValue() == 1;
    float absoluteError = message.get(2).floatValue();
    String detail = message.get(3).stringValue();
    activePauliVerified = verified;
    activePauliError = absoluteError;
    rewriteFeedbackSuccess = verified;
    rewriteFeedback = verified
      ? (
        "✓ ORDERED PAULI SCORE VERIFIED  ·  "
        + message.get(0).intValue() + " gadgets · error " + str(absoluteError)
      )
      : "✕ PAULI SCORE REJECTED  ·  " + detail;
    rewriteFeedbackUntil = millis() + 5600;
    statusText = detail;
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/pauli/verified")) {
    String label = message.get(0).stringValue();
    if (!label.equals(activePauliLabel)) return;
    activePauliTheta = message.get(2).floatValue();
    activePauliVerified = message.get(3).intValue() == 1;
    activePauliError = message.get(4).floatValue();
    String detail = message.get(5).stringValue();
    rewriteFeedbackSuccess = activePauliVerified;
    rewriteFeedback = activePauliVerified
      ? "✓ " + label + " PAULI ROTATION VERIFIED  ·  error " + str(activePauliError)
      : "✕ " + label + " GADGET REJECTED  ·  " + detail;
    rewriteFeedbackUntil = millis() + 5600;
    statusText = detail;
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/pauli/live")) {
    String label = message.get(1).stringValue();
    if (!label.equals(activePauliLabel)) return;
    activePauliExpectation = message.get(3).floatValue();
    activePauliTheta = message.get(4).floatValue();
    activePauliVerified = message.get(5).intValue() == 1;
    statusText = (
      label + " live · weight " + message.get(2).intValue()
      + " · 〈P〉 " + nf(activePauliExpectation, 0, 6)
    );
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/pauli/error")) {
    statusText = "Pauli OSC error · " + message.get(0).stringValue();
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/density/begin")) {
    densityRevision = message.get(0).intValue();
    densityMode = message.get(1).stringValue();
    int incomingDimension = message.get(2).intValue();
    if (
      incomingDimension < 2
      || incomingDimension > 256
      || (incomingDimension & (incomingDimension - 1)) != 0
    ) {
      densityFrameReceiving = false;
      densityRevision = -1;
      densityStatus = "unsupported density dimension " + incomingDimension;
      statusText = densityStatus;
      return;
    }
    allocateDensityFrame(incomingDimension);
    densitySuccessProbability = message.get(3).floatValue();
    clearDensityFrame();
    densityFrameReceiving = true;
    if (activePauliLabel.equals("")) densityPanelVisible = true;
    densityStatus = "receiving revision " + densityRevision + "…";
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/density/meta")) {
    if (message.get(0).intValue() != densityRevision) return;
    densityTrace = message.get(1).floatValue();
    densityPurity = message.get(2).floatValue();
    densityCoherence = message.get(3).floatValue();
    densityEntropy = message.get(4).floatValue();
    densityMinEigenvalue = message.get(5).floatValue();
    densitySuccessProbability = message.get(6).floatValue();
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/density/probabilities")) {
    if (message.get(0).intValue() != densityRevision) return;
    for (int index = 0; index < densityDimension; index++) {
      densityProbabilities[index] = message.get(index + 1).floatValue();
    }
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/density/row")) {
    if (message.get(0).intValue() != densityRevision) return;
    int row = message.get(1).intValue();
    if (row < 0 || row >= densityDimension) return;
    for (int column = 0; column < densityDimension; column++) {
      densityReal[row][column] = message.get(column + 2).floatValue();
      densityImag[row][column] = message.get(
        column + 2 + densityDimension
      ).floatValue();
    }
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/density/bloch")) {
    if (message.get(0).intValue() != densityRevision) return;
    int qubit = message.get(1).intValue();
    if (qubit < 0 || qubit >= densityQubitCount) return;
    densityBloch[qubit][0] = message.get(2).floatValue();
    densityBloch[qubit][1] = message.get(3).floatValue();
    densityBloch[qubit][2] = message.get(4).floatValue();
    densityLocalPurity[qubit] = message.get(5).floatValue();
    densityLocalEntropy[qubit] = message.get(6).floatValue();
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/density/end")) {
    if (message.get(0).intValue() != densityRevision) return;
    densityFrameReceiving = false;
    densityStatus = message.get(1).stringValue();
    statusText = densityQubitCount <= 4
      ? "physical density preview ready · Return commits it"
      : (
        "physical " + densityQubitCount
        + "-qubit preview ready in Processing and Max"
      );
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/density/error")) {
    densityFrameReceiving = false;
    densityPanelVisible = true;
    densityRevision = -1;
    densityStatus = "diagram not density-ready: " + message.get(0).stringValue();
    statusText = densityStatus;
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/density/commit_sent")) {
    int revision = message.get(0).intValue();
    String host = message.get(1).stringValue();
    int port = message.get(2).intValue();
    densityStatus = (
      "revision " + revision + " sent to engine " + host + ":" + port
    );
    statusText = "density candidate sent atomically · engine validation is authoritative";
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/graph/request")) {
    sendGraphSnapshot();
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/graph/synchronized")) {
    int revision = message.get(0).intValue();
    int nodeCount = message.get(1).intValue();
    int edgeCount = message.get(2).intValue();
    statusText = (
      "Python mirror synchronized · revision " + revision
      + " · " + nodeCount + " nodes · " + edgeCount + " wires"
    );
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/graph/error")) {
    String detail = message.get(0).stringValue();
    statusText = "graph packet rejected · " + detail;
    rewriteFeedback = "GRAPH PACKET REJECTED  ·  " + detail;
    rewriteFeedbackSuccess = false;
    rewriteFeedbackUntil = millis() + 4200;
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/rewrite/result")) {
    int keepId = message.get(0).intValue();
    int removedId = message.get(1).intValue();
    boolean verified = message.get(2).intValue() == 1;
    float absoluteError = message.get(3).floatValue();
    float fusedPhase = message.get(4).floatValue();
    String detail = message.get(5).stringValue();
    rewriteFeedbackSuccess = verified;
    rewriteFeedback = verified
      ? "✓ SEMANTICS PRESERVED  ·  error " + str(absoluteError)
      : "✕ REWRITE REJECTED  ·  " + detail;
    rewriteFeedbackUntil = millis() + 5000;
    statusText = detail;
    if (verified) {
      ZXNode keep = nodeWithId(keepId);
      if (keep != null) {
        sendCommittedFusion(
          keepId,
          removedId,
          keep.kind,
          fusedPhase
        );
      }
    }
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/rewrite/graph/begin")) {
    pendingRewriteRule = message.get(0).stringValue();
    pendingScalarReal = message.get(1).floatValue();
    pendingScalarImag = message.get(2).floatValue();
    pendingRewriteNodes.clear();
    pendingRewriteEdges.clear();
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/rewrite/graph/node")) {
    int nodeId = message.get(0).intValue();
    String kind = message.get(1).stringValue();
    float phase = message.get(4).floatValue();
    String label = "";
    if (kind.equals("Z") || kind.equals("X")) label = phaseLabel(phase);
    if (kind.equals("HB")) label = "−1";
    ZXNode node = new ZXNode(
      nodeId,
      kind,
      message.get(2).floatValue() * width,
      message.get(3).floatValue() * height,
      label
    );
    node.phase = phase;
    if (message.arguments().length >= 7) {
      node.boundaryRole = message.get(5).stringValue();
      node.boundaryIndex = message.get(6).intValue();
      if (node.kind.equals("B")) node.label = boundaryLabel(node);
      if (node.kind.equals("D")) node.label = "discard";
    }
    pendingRewriteNodes.add(node);
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/rewrite/graph/edge")) {
    ZXNode a = pendingNodeWithId(message.get(0).intValue());
    ZXNode b = pendingNodeWithId(message.get(1).intValue());
    if (a != null && b != null) {
      addPendingEdge(a, b, message.get(2).stringValue());
    }
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/rewrite/graph/end")) {
    invalidateLiveEulerSelection();
    nodes.clear();
    edges.clear();
    nodes.addAll(pendingRewriteNodes);
    edges.addAll(pendingRewriteEdges);
    diagramScalarReal = pendingScalarReal;
    diagramScalarImag = pendingScalarImag;
    nextNodeId = 1;
    for (ZXNode node : nodes) nextNodeId = max(nextNodeId, node.id + 1);
    clearSelection();
    statusText = message.get(1).stringValue();
    pendingRewriteNodes.clear();
    pendingRewriteEdges.clear();
    markDensityDirty();
    return;
  }

  if (message.checkAddrPattern("/qmw/zx/rewrite/result_v2")) {
    String ruleId = message.get(0).stringValue();
    boolean verified = message.get(1).intValue() == 1;
    float absoluteError = message.get(2).floatValue();
    String detail = message.get(3).stringValue();
    rewriteFeedbackSuccess = verified;
    rewriteFeedback = verified
      ? (
        "✓ " + ruleId.replace("_", " ").toUpperCase()
        + "  ·  exact error " + str(absoluteError)
      )
      : "✕ " + ruleId.replace("_", " ").toUpperCase() + "  ·  " + detail;
    rewriteFeedbackUntil = millis() + 5600;
    statusText = detail;
    if (verified) {
      diagramScalarReal = message.get(6).floatValue();
      diagramScalarImag = message.get(7).floatValue();
      sendCommittedNamedRewrite(ruleId, absoluteError);
    }
    return;
  }

  if (!message.checkAddrPattern("/qmw/zx/fader")) return;
  if (message.arguments().length < 2) return;

  int controlId = message.get(0).intValue();
  float value = constrain(message.get(1).floatValue(), 0.0, 1.0);
  if (controlId < 1 || controlId > quantumControl.length) return;
  quantumControl[controlId - 1] = value;
  lastOscMillis = millis();
  sendFader(controlId, value);

  if (controlId == 1) {
    PauliGadgetMacro activeGadget = pauliGadgetWithId(activePauliGadgetId);
    if (pauliScoreMode && activeGadget != null) {
      activeGadget.theta = value * TWO_PI;
      rebuildPauliScoreGraph(activeGadget.id, true);
      statusText = activeGadget.label + " phase updated from OSC";
      return;
    }

    ZXNode target = nodeWithId(activePauliCentralNodeId);
    if (target == null) {
      for (ZXNode node : nodes) {
        if (node.kind.equals("Z")) {
          target = node;
          break;
        }
      }
    }
    if (target != null) {
      target.phase = value * TWO_PI;
      target.label = phaseLabel(target.phase);
      sendNodePhase(target);
      if (target.id == activePauliCentralNodeId) {
        activePauliTheta = target.phase;
        updateActivePauliScalar();
        sendPauliGadget();
      }
      markDensityDirty();
    }
  }
}


ZXNode pendingNodeWithId(int nodeId) {
  for (ZXNode node : pendingRewriteNodes) {
    if (node.id == nodeId) return node;
  }
  return null;
}


void addPendingEdge(ZXNode a, ZXNode b, String kind) {
  if (a == null || b == null || a == b) return;
  int parallelCount = 0;
  for (ZXEdge edge : pendingRewriteEdges) {
    if (
      (edge.a == a && edge.b == b)
      || (edge.a == b && edge.b == a)
    ) {
      parallelCount += 1;
    }
  }
  float bend = parallelCount == 0 ? 0 : (parallelCount % 2 == 0 ? -42 : 42);
  if (parallelCount == 1) {
    for (ZXEdge edge : pendingRewriteEdges) {
      if (
        (edge.a == a && edge.b == b)
        || (edge.a == b && edge.b == a)
      ) {
        edge.bend = -42;
      }
    }
  }
  pendingRewriteEdges.add(new ZXEdge(a, b, bend, kind));
}


float positiveModulo(float value, float modulus) {
  return ((value % modulus) + modulus) % modulus;
}


void sendFader(int controlId, float value) {
  OscMessage qmwMessage = new OscMessage("/qmw/zx/fader");
  qmwMessage.add(controlId);
  qmwMessage.add(value);
  oscP5.send(qmwMessage, maxTarget);
  oscP5.send(qmwMessage, superColliderTarget);

  OscMessage rackMessage = new OscMessage("/fader");
  rackMessage.add(controlId);
  rackMessage.add(value);
  oscP5.send(rackMessage, rackTarget);
}


void sendNodePosition(ZXNode node) {
  OscMessage message = new OscMessage("/qmw/zx/node/position");
  message.add(node.id);
  message.add(node.x / width);
  message.add(node.y / height);
  oscP5.send(message, maxTarget);
  oscP5.send(message, superColliderTarget);
  oscP5.send(message, pythonVerifierTarget);
}


void sendNodePhase(ZXNode node) {
  OscMessage message = new OscMessage("/qmw/zx/node/phase");
  message.add(node.id);
  message.add(node.kind);
  message.add(node.phase);
  oscP5.send(message, maxTarget);
  oscP5.send(message, superColliderTarget);
  oscP5.send(message, pythonVerifierTarget);
}


void sendNodeAdded(ZXNode node) {
  OscMessage message = new OscMessage("/qmw/zx/node/add");
  message.add(node.id);
  message.add(node.kind);
  message.add(node.x / width);
  message.add(node.y / height);
  message.add(node.phase);
  message.add(node.boundaryRole);
  message.add(node.boundaryIndex);
  oscP5.send(message, maxTarget);
  oscP5.send(message, superColliderTarget);
  oscP5.send(message, pythonVerifierTarget);
}


void sendNodeDeleted(ZXNode node) {
  OscMessage message = new OscMessage("/qmw/zx/node/delete");
  message.add(node.id);
  oscP5.send(message, maxTarget);
  oscP5.send(message, superColliderTarget);
  oscP5.send(message, pythonVerifierTarget);
}


void sendEdgeAdded(ZXNode a, ZXNode b) {
  sendEdgeAdded(a, b, "plain");
}


void sendEdgeAdded(ZXNode a, ZXNode b, String kind) {
  if (a == null || b == null || a == b) {
    statusText = "self-loop rejected before OSC transmission";
    return;
  }
  OscMessage message = new OscMessage("/qmw/zx/edge/add");
  message.add(a.id);
  message.add(b.id);
  message.add(kind);
  oscP5.send(message, maxTarget);
  oscP5.send(message, superColliderTarget);
  oscP5.send(message, pythonVerifierTarget);
}


void sendRewriteFusion(ZXNode keep, ZXNode removed) {
  OscMessage message = new OscMessage("/qmw/zx/rewrite/fuse");
  message.add(keep.id);
  message.add(removed.id);
  message.add(keep.kind);
  message.add(keep.phase);
  oscP5.send(message, pythonVerifierTarget);
}


void sendCommittedFusion(
  int keepId,
  int removedId,
  String kind,
  float fusedPhase
) {
  float fusedTurns = positiveModulo(fusedPhase / TWO_PI, 1.0);
  quantumControl[0] = fusedTurns;
  sendFader(1, fusedTurns);

  OscMessage message = new OscMessage("/qmw/zx/rewrite/fuse");
  message.add(keepId);
  message.add(removedId);
  message.add(kind);
  message.add(fusedPhase);
  oscP5.send(message, maxTarget);
  oscP5.send(message, superColliderTarget);

  OscMessage rackPulse = new OscMessage("/fader");
  rackPulse.add(7);
  rackPulse.add(1.0);
  oscP5.send(rackPulse, rackTarget);
  rackRewriteResetAt = millis() + 90;
}


void sendCommittedNamedRewrite(String ruleId, float absoluteError) {
  OscMessage message = new OscMessage("/qmw/zx/rewrite/apply");
  message.add(ruleId);
  message.add(absoluteError);
  message.add(diagramScalarReal);
  message.add(diagramScalarImag);
  oscP5.send(message, maxTarget);
  oscP5.send(message, superColliderTarget);

  OscMessage rackPulse = new OscMessage("/fader");
  rackPulse.add(7);
  rackPulse.add(1.0);
  oscP5.send(rackPulse, rackTarget);
  rackRewriteResetAt = millis() + 90;
}


ZXNode nodeWithId(int nodeId) {
  for (ZXNode node : nodes) {
    if (node.id == nodeId) return node;
  }
  return null;
}


void serviceTimedOsc() {
  if (rackRewriteResetAt > 0 && millis() >= rackRewriteResetAt) {
    OscMessage rackReset = new OscMessage("/fader");
    rackReset.add(7);
    rackReset.add(0.0);
    oscP5.send(rackReset, rackTarget);
    rackRewriteResetAt = 0;
  }
  if (
    (densityPanelVisible || !activePauliLabel.equals(""))
    && densityDirty
    && millis() - densityDirtyAt >= 275
  ) {
    requestDensityPreview();
  }
  if (
    eulerLiveEnabled
    && eulerDirty
    && millis() - eulerDirtyAt >= EULER_LIVE_DEBOUNCE_MS
  ) {
    requestLiveEulerDecomposition();
  }
}


void allocateDensityFrame(int dimension) {
  densityDimension = dimension;
  densityQubitCount = round(log(dimension) / log(2));
  densityReal = new float[dimension][dimension];
  densityImag = new float[dimension][dimension];
  densityProbabilities = new float[dimension];
  densityBloch = new float[densityQubitCount][3];
  densityLocalPurity = new float[densityQubitCount];
  densityLocalEntropy = new float[densityQubitCount];
}


void clearDensityFrame() {
  densityTrace = 0;
  densityPurity = 0;
  densityCoherence = 0;
  densityEntropy = 0;
  densityMinEigenvalue = 0;
  for (int row = 0; row < densityDimension; row++) {
    densityProbabilities[row] = 0;
    for (int column = 0; column < densityDimension; column++) {
      densityReal[row][column] = 0;
      densityImag[row][column] = 0;
    }
  }
  for (int qubit = 0; qubit < densityQubitCount; qubit++) {
    densityBloch[qubit][0] = 0;
    densityBloch[qubit][1] = 0;
    densityBloch[qubit][2] = 0;
    densityLocalPurity[qubit] = 0;
    densityLocalEntropy[qubit] = 0;
  }
}


void sendGraphSnapshot() {
  graphRevision += 1;

  OscMessage begin = new OscMessage("/qmw/zx/graph/begin");
  begin.add(graphRevision);
  begin.add(diagramScalarReal);
  begin.add(diagramScalarImag);
  oscP5.send(begin, pythonVerifierTarget);

  for (ZXNode node : nodes) {
    OscMessage nodeMessage = new OscMessage("/qmw/zx/node/add");
    nodeMessage.add(node.id);
    nodeMessage.add(node.kind);
    nodeMessage.add(node.x / width);
    nodeMessage.add(node.y / height);
    nodeMessage.add(node.phase);
    nodeMessage.add(node.boundaryRole);
    nodeMessage.add(node.boundaryIndex);
    oscP5.send(nodeMessage, pythonVerifierTarget);
  }

  for (ZXEdge edge : edges) {
    if (edge.a == null || edge.b == null || edge.a == edge.b) continue;
    OscMessage edgeMessage = new OscMessage("/qmw/zx/edge/add");
    edgeMessage.add(edge.a.id);
    edgeMessage.add(edge.b.id);
    edgeMessage.add(edge.kind);
    oscP5.send(edgeMessage, pythonVerifierTarget);
  }

  OscMessage end = new OscMessage("/qmw/zx/graph/end");
  end.add(graphRevision);
  oscP5.send(end, pythonVerifierTarget);
}


class ZXNode {
  int id;
  String kind;
  float x;
  float y;
  float phase = 0;
  String label;
  String boundaryRole = "";
  int boundaryIndex = -1;
  boolean selected = false;
  int pauliGadgetId = -1;
  String pauliRole = "";

  ZXNode(int id, String kind, float x, float y, String label) {
    this.id = id;
    this.kind = kind;
    this.x = x;
    this.y = y;
    this.label = label;
  }
}


class PauliGadgetMacro {
  int id;
  String label;
  float theta;
  int phaseNodeId = -1;
  float centerX = 0;

  PauliGadgetMacro(int id, String label, float theta) {
    this.id = id;
    this.label = label;
    this.theta = theta;
  }
}


class ZXEdge {
  ZXNode a;
  ZXNode b;
  float bend;
  String kind;

  ZXEdge(ZXNode a, ZXNode b, float bend, String kind) {
    this.a = a;
    this.b = b;
    this.bend = bend;
    this.kind = kind;
  }
}


class ZXClipboardNode {
  int originalId;
  String kind;
  float relativeX;
  float relativeY;
  float phase;
  String label;
  String boundaryRole;
  int boundaryIndex;

  ZXClipboardNode(
    int originalId,
    String kind,
    float relativeX,
    float relativeY,
    float phase,
    String label,
    String boundaryRole,
    int boundaryIndex
  ) {
    this.originalId = originalId;
    this.kind = kind;
    this.relativeX = relativeX;
    this.relativeY = relativeY;
    this.phase = phase;
    this.label = label;
    this.boundaryRole = boundaryRole;
    this.boundaryIndex = boundaryIndex;
  }
}


class ZXClipboardEdge {
  int sourceId;
  int targetId;
  float bend;
  String kind;

  ZXClipboardEdge(
    int sourceId,
    int targetId,
    float bend,
    String kind
  ) {
    this.sourceId = sourceId;
    this.targetId = targetId;
    this.bend = bend;
    this.kind = kind;
  }
}
