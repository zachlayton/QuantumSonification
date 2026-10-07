/*
 * Module 4 — Entanglement
 * Install Processing's official Sound library in Contribution Manager first.
 */
import processing.sound.*;

boolean useCnot = true;
boolean q0Controls = true;
boolean useH = true;
TriOsc firstVoice;
TriOsc secondVoice;
Env firstEnvelope;
Env secondEnvelope;
boolean soundReady = false;
String audioStatus = "Initializing Sound…";

void setup() {
  size(820, 580);
  textFont(createFont("Arial", 16));
  try {
    firstVoice = new TriOsc(this);
    secondVoice = new TriOsc(this);
    firstEnvelope = new Env(this);
    secondEnvelope = new Env(this);
    soundReady = true;
    audioStatus = "Sound ready · the two possible joint outcomes play together.";
  } catch (Throwable error) {
    audioStatus = "Sound missing: install Sound in Contribution Manager.";
  }
}

void draw() {
  background(8, 12, 20);
  fill(245);
  textSize(26);
  text("MODULE 4 · ENTANGLEMENT", 34, 48);
  fill(155, 178, 207);
  textSize(14);
  text("Build the link, then hear the two possible joint outcomes together.", 34, 76);

  button(34, 98, 150, 50, useH ? "H: ON" : "H: OFF", useH);
  button(198, 98, 160, 50, useCnot ? "CNOT: ON" : "CNOT: OFF", useCnot);
  button(
    372, 98, 208, 50,
    q0Controls ? "q0 → q1" : "q1 → q0",
    false
  );
  button(594, 98, 192, 50, "HEAR STATE", false);
  drawCircuitPanel();
  drawOutcomePanel();

  fill(soundReady ? color(74, 220, 142) : color(242, 132, 54));
  textSize(12);
  text(audioStatus, 34, 558);
}

void mouseClicked() {
  if (hit(34, 98, 150, 50)) {
    useH = !useH;
    hearPair();
  } else if (hit(198, 98, 160, 50)) {
    useCnot = !useCnot;
    hearPair();
  } else if (hit(372, 98, 208, 50)) {
    q0Controls = !q0Controls;
    hearPair();
  } else if (hit(594, 98, 192, 50)) hearPair();
}

void hearPair() {
  if (!soundReady) {
    audioStatus = "Missing library: install official Sound, then reopen.";
    return;
  }
  try {
    boolean linked = useH && useCnot && q0Controls;
    boolean twoOutcomes = useH;
    firstVoice.stop();
    secondVoice.stop();
    firstVoice.play(220, 0.13);
    firstEnvelope.play(firstVoice, 0.008, 0.34, 0.18, 0.55);
    if (twoOutcomes) {
      float secondFrequency = linked ? 440 : 277;
      secondVoice.play(secondFrequency, 0.13);
      secondEnvelope.play(secondVoice, 0.008, 0.34, 0.18, 0.55);
    }
    if (!useH) {
      audioStatus = "H off: CNOT receives |00〉 and leaves |00〉 at 100% · 220 Hz.";
    } else if (linked) {
      audioStatus = "Playing |00〉 + |11〉 together · 220 + 440 Hz.";
    } else if (useCnot) {
      audioStatus = "q1 controls, but starts at |0〉: |00〉 + |01〉 · 220 + 277 Hz.";
    } else {
      audioStatus = "CNOT off: |00〉 + |01〉 together · 220 + 277 Hz.";
    }
  } catch (Throwable error) {
    soundReady = false;
    audioStatus = "Audio device failed; run 04_entanglement.py.";
  }
}

void drawCircuitPanel() {
  float panelX = 34;
  float panelY = 168;
  float panelW = 492;
  float panelH = 350;
  float wireStart = 82;
  float wireEnd = 484;
  float controlY = 302;
  float targetY = 422;

  noStroke();
  fill(17, 25, 37);
  rect(panelX, panelY, panelW, panelH, 12);

  fill(245);
  textSize(14);
  text("THE CIRCUIT", 56, 198);
  fill(155, 178, 207);
  text("Toggle H and CNOT; swap direction to test each gate's job.", 56, 220);

  fill(245);
  textSize(16);
  text(q0Controls ? "q0 · control qubit" : "q0 · target qubit", wireStart, 260);
  text(q0Controls ? "q1 · target qubit" : "q1 · control qubit", wireStart, 380);

  stroke(155, 178, 207);
  strokeWeight(3);
  line(wireStart, controlY, wireEnd, controlY);
  line(wireStart, targetY, wireEnd, targetY);

  // Both qubits enter in |0〉.
  fill(155, 178, 207);
  noStroke();
  textSize(14);
  text("|0〉", 50, controlY + 5);
  text("|0〉", 50, targetY + 5);

  // H is optional and acts only on q0.
  textAlign(CENTER, CENTER);
  if (useH) {
    stroke(91, 151, 246);
    strokeWeight(3);
    fill(17, 25, 37);
    rect(166, controlY - 23, 46, 46, 4);
    fill(245);
    noStroke();
    textSize(20);
    text("H", 189, controlY);
  } else {
    stroke(75, 91, 112);
    strokeWeight(2);
    noFill();
    rect(166, controlY - 23, 46, 46, 4);
    fill(155, 178, 207);
    noStroke();
    textSize(11);
    text("H off", 189, controlY);
  }

  if (useCnot) {
    drawCnot(
      365,
      q0Controls ? controlY : targetY,
      q0Controls ? targetY : controlY
    );
  } else {
    fill(242, 132, 54);
    textSize(13);
    text("CNOT removed", 365, (controlY + targetY) / 2);
  }
  textAlign(LEFT, BASELINE);
}

void drawCnot(float gateX, float controlY, float targetY) {
  stroke(242, 194, 28);
  strokeWeight(4);
  line(gateX, controlY, gateX, targetY);

  // Filled control dot.
  fill(242, 194, 28);
  noStroke();
  circle(gateX, controlY, 20);

  // Circled plus target.
  fill(17, 25, 37);
  stroke(242, 194, 28);
  strokeWeight(4);
  circle(gateX, targetY, 54);
  line(gateX - 18, targetY, gateX + 18, targetY);
  line(gateX, targetY - 18, gateX, targetY + 18);

  fill(242, 194, 28);
  noStroke();
  textAlign(CENTER, BASELINE);
  textSize(13);
  text("CNOT", gateX, controlY - 24);
}

void drawOutcomePanel() {
  float panelX = 550;
  float panelY = 168;
  float panelW = 236;
  float panelH = 350;

  noStroke();
  fill(17, 25, 37);
  rect(panelX, panelY, panelW, panelH, 12);

  fill(245);
  textSize(14);
  text("POSSIBLE JOINT OUTCOMES", panelX + 18, panelY + 30);
  fill(155, 178, 207);
  textSize(12);
  text("The two highlighted states", panelX + 18, panelY + 54);
  text("sound at the same time.", panelX + 18, panelY + 72);

  boolean linked = useH && useCnot && q0Controls;
  if (linked) {
    outcomeRow(panelX + 18, panelY + 108, "00", 220, 0.5);
    outcomeRow(panelX + 18, panelY + 188, "11", 440, 0.5);
  } else if (useH) {
    outcomeRow(panelX + 18, panelY + 108, "00", 220, 0.5);
    outcomeRow(panelX + 18, panelY + 188, "01", 277, 0.5);
  } else {
    outcomeRow(panelX + 18, panelY + 108, "00", 220, 1.0);
    fill(155, 178, 207);
    textSize(13);
    text("No second outcome.", panelX + 18, panelY + 220);
  }

  fill(linked ? color(74, 220, 142) : color(242, 132, 54));
  textSize(14);
  text(
    linked ? "ENTANGLED: 00 or 11"
      : useH ? "NOT LINKED: 00 or 01" : "CERTAIN: 00",
    panelX + 18,
    panelY + 302
  );
  fill(155, 178, 207);
  textSize(12);
  text(
    useH ? "Each possibility: 50%" : "One possibility: 100%",
    panelX + 18,
    panelY + 326
  );
}

void outcomeRow(
  float x, float y, String bits, int frequency, float probability
) {
  noStroke();
  fill(28, 40, 57);
  rect(x, y, 200, 58, 8);
  fill(91, 151, 246);
  rect(x, y, 200 * probability, 58, 8, 0, 0, 8);
  fill(245);
  textSize(20);
  text("|" + bits + "〉", x + 14, y + 27);
  textSize(12);
  text(round(probability * 100) + "%  ·  " + frequency + " Hz", x + 14, y + 47);
}

void button(float x, float y, float w, float h, String label, boolean active) {
  boolean hover = hit(x, y, w, h);
  noStroke();
  fill(active ? color(242, 132, 54)
    : hover ? color(242, 194, 28) : color(28, 40, 57));
  rect(x, y, w, h, 8);
  fill(active || hover ? color(8, 12, 20) : color(245));
  textAlign(CENTER, CENTER);
  textSize(14);
  text(label, x + w / 2, y + h / 2);
  textAlign(LEFT, BASELINE);
}

boolean hit(float x, float y, float w, float h) {
  return mouseX >= x && mouseX <= x + w && mouseY >= y && mouseY <= y + h;
}

void exit() {
  if (firstVoice != null) firstVoice.stop();
  if (secondVoice != null) secondVoice.stop();
  super.exit();
}
