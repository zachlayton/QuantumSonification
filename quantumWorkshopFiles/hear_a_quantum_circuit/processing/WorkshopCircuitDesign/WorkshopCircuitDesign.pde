/*
 * Module 3 — Circuit design
 * A six-slot H/X/Y/Z playground. CNOT belongs to Module 4.
 * Install Processing's official Sound library in Contribution Manager first.
 */
import processing.sound.*;

String[] gates = new String[6];
String[] palette = {"H", "X", "Y", "Z"};
float p0 = 1, p1 = 0, bx = 0, by = 0, bz = 1;
TriOsc tone;
Env envelope;
boolean soundReady = false;
String audioStatus = "Initializing Sound…";
float[] cue = {};
int cueIndex = 0;
int nextTone = 0;
String cueState = "|0〉";

void setup() {
  size(900, 600);
  textFont(createFont("Arial", 16));
  try {
    tone = new TriOsc(this);
    envelope = new Env(this);
    soundReady = true;
    audioStatus = "Sound ready.";
  } catch (Throwable error) {
    audioStatus = "Sound missing: install Sound in Contribution Manager.";
  }
}

void draw() {
  background(8, 12, 20);
  playQueuedTone();
  fill(245);
  textSize(26);
  text("MODULE 3 · CIRCUIT DESIGN", 34, 48);
  fill(155, 178, 207);
  textSize(14);
  text("One idea: gate order changes the state. Reach |1〉, then return to |0〉.", 34, 76);

  for (int i = 0; i < palette.length; i++) {
    button(42 + i * 96, 118, 82, 42, palette[i], false);
  }
  button(452, 118, 116, 42, "CLEAR", false);
  button(584, 118, 156, 42, "HEAR", false);
  button(42, 176, 170, 38, "LOAD H-Z-H", false);
  button(224, 176, 170, 38, "LOAD H-X-H", false);
  button(406, 176, 170, 38, "LOAD H-Y-H", false);
  fill(155, 178, 207);
  textSize(12);
  text("Compare the same gate between two H gates.", 598, 200);

  fill(245);
  textSize(15);
  text("CIRCUIT · left to right", 42, 250);
  for (int i = 0; i < gates.length; i++) {
    float x = 42 + i * 112;
    stroke(92, 112, 145);
    line(x - 8, 290, x + 98, 290);
    noStroke();
    fill(gates[i] == null ? color(28, 40, 57) : color(242, 132, 54));
    rect(x, 265, 72, 50, 8);
    fill(gates[i] == null ? color(155, 178, 207) : color(8, 12, 20));
    textAlign(CENTER, CENTER);
    textSize(18);
    text(gates[i] == null ? "·" : gates[i], x + 36, 290);
  }
  textAlign(LEFT, BASELINE);

  probabilityBar(84, 370, 300, p0, "|0〉", color(91, 151, 246));
  probabilityBar(84, 444, 300, p1, "|1〉", color(242, 132, 54));
  fill(245);
  textSize(18);
  text(p1 > 0.999 ? "TARGET REACHED · |1〉"
    : p0 > 0.999 ? "CURRENT STATE · |0〉"
    : "CURRENT STATE · superposition", 474, 386);
  fill(155, 178, 207);
  textSize(13);
  text("Bloch  (" + signed(bx) + ", " + signed(by) + ", " + signed(bz) + ")", 474, 418);
  text("Python presets: compare-x · compare-y", 474, 452);
  fill(242, 194, 28);
  textSize(14);
  text("REFLECT · Why do H-X-H and H-Y-H separate gates that looked identical on |0〉?", 42, 530);
  fill(soundReady ? color(74, 220, 142) : color(242, 132, 54));
  textSize(12);
  text(audioStatus, 42, 562);
}

void mouseClicked() {
  for (int i = 0; i < palette.length; i++) {
    if (hit(42 + i * 96, 118, 82, 42)) {
      addGate(palette[i]);
      hearState();
      return;
    }
  }
  if (hit(452, 118, 116, 42)) clearGates();
  else if (hit(584, 118, 156, 42)) hearState();
  else if (hit(42, 176, 170, 38)) loadSandwich("Z");
  else if (hit(224, 176, 170, 38)) loadSandwich("X");
  else if (hit(406, 176, 170, 38)) loadSandwich("Y");
}

void addGate(String gate) {
  for (int i = 0; i < gates.length; i++) {
    if (gates[i] == null) {
      gates[i] = gate;
      updateState();
      return;
    }
  }
  audioStatus = "Six-slot beginner limit. Clear or hear this circuit.";
}

void clearGates() {
  for (int i = 0; i < gates.length; i++) gates[i] = null;
  updateState();
}

void loadSandwich(String middleGate) {
  clearGates();
  gates[0] = "H";
  gates[1] = middleGate;
  gates[2] = "H";
  updateState();
  hearState();
}

void updateState() {
  float ar = 1, ai = 0, br = 0, bi = 0;
  float root = sqrt(0.5);
  for (String gate : gates) {
    if (gate == null) continue;
    float nar = ar, nai = ai, nbr = br, nbi = bi;
    if (gate.equals("H")) {
      nar = (ar + br) * root; nai = (ai + bi) * root;
      nbr = (ar - br) * root; nbi = (ai - bi) * root;
    } else if (gate.equals("X")) {
      nar = br; nai = bi; nbr = ar; nbi = ai;
    } else if (gate.equals("Y")) {
      nar = bi; nai = -br; nbr = -ai; nbi = ar;
    } else if (gate.equals("Z")) {
      nbr = -br; nbi = -bi;
    }
    ar = nar; ai = nai; br = nbr; bi = nbi;
  }
  p0 = ar * ar + ai * ai;
  p1 = br * br + bi * bi;
  bx = 2 * (ar * br + ai * bi);
  by = 2 * (ar * bi - ai * br);
  bz = p0 - p1;
}

void hearState() {
  if (!soundReady) {
    audioStatus = "Missing library: install official Sound, then reopen.";
    return;
  }
  // Cancel a previous gate's envelope so the new final-state cue is unambiguous.
  try {
    tone.stop();
  } catch (Throwable error) {
    // The next play call can still recover if no oscillator was active.
  }
  if (p0 > 0.001 && p1 > 0.001) {
    cue = new float[]{220, 440};
    cueState = "superposition";
  } else if (p1 > 0.001) {
    cue = new float[]{440};
    cueState = "|1〉";
  } else {
    cue = new float[]{220};
    cueState = "|0〉";
  }
  cueIndex = 0;
  nextTone = millis() + 40;
  audioStatus = "QUEUED FINAL STATE · " + cueState
    + (cue.length == 1 ? " · " + round(cue[0]) + " Hz" : " · 220 then 440 Hz");
}

void playQueuedTone() {
  if (cueIndex >= cue.length || millis() < nextTone) return;
  try {
    float frequency = cue[cueIndex];
    tone.play(frequency, 0.18);
    envelope.play(tone, 0.008, 0.16, 0.16, 0.24);
    cueIndex++;
    nextTone = millis() + 480;
    audioStatus = "PLAYING " + cueState + " · " + round(frequency) + " Hz"
      + (cue.length > 1 ? " · tone " + cueIndex + " of " + cue.length : "");
  } catch (Throwable error) {
    soundReady = false;
    audioStatus = "Audio device failed; run 03_circuit_design.py.";
  }
}

void probabilityBar(float x, float y, float w, float value, String label, int c) {
  fill(245);
  textSize(14);
  text(label, x, y);
  noStroke();
  fill(28, 40, 57);
  rect(x, y + 12, w, 26, 6);
  fill(c);
  rect(x, y + 12, max(1, w * value), 26, 6);
  fill(245);
  text(round(value * 100) + "%", x + w - 42, y + 32);
}

void button(float x, float y, float w, float h, String label, boolean active) {
  boolean hover = hit(x, y, w, h);
  noStroke();
  fill(active ? color(242, 132, 54)
    : hover ? color(242, 194, 28) : color(28, 40, 57));
  rect(x, y, w, h, 8);
  fill(active || hover ? color(8, 12, 20) : color(245));
  textAlign(CENTER, CENTER);
  textSize(13);
  text(label, x + w / 2, y + h / 2);
  textAlign(LEFT, BASELINE);
}

boolean hit(float x, float y, float w, float h) {
  return mouseX >= x && mouseX <= x + w && mouseY >= y && mouseY <= y + h;
}

String signed(float value) {
  if (abs(value) < 0.005) value = 0;
  return (value >= 0 ? "+" : "") + nf(value, 1, 2);
}

void exit() {
  if (tone != null) tone.stop();
  super.exit();
}
