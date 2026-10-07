/*
 * Module 1 — Superposition
 * Install Processing's official Sound library in Contribution Manager first.
 */
import processing.sound.*;

TriOsc tone;
Env envelope;
boolean useH = false;
boolean soundReady = false;
String audioStatus = "Initializing Sound…";
float[] cue = {};
int cueIndex = 0;
int nextTone = 0;

void setup() {
  size(760, 520);
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
  text("MODULE 1 · SUPERPOSITION", 34, 48);
  fill(155, 178, 207);
  textSize(14);
  text("One idea: H changes one certain outcome into two possibilities.", 34, 76);

  button(48, 128, 220, 58, useH ? "H GATE: ON" : "H GATE: OFF", useH);
  button(492, 128, 220, 58, "HEAR THE STATE", false);

  float p0 = useH ? 0.5 : 1.0;
  float p1 = useH ? 0.5 : 0.0;
  probabilityBar(116, 246, 520, p0, "|0〉 · 220 Hz", color(91, 151, 246));
  probabilityBar(116, 324, 520, p1, "|1〉 · 440 Hz", color(242, 132, 54));

  fill(245);
  textSize(16);
  text(useH ? "Listen for two notes." : "Listen for one note.", 48, 420);
  fill(242, 194, 28);
  text("REFLECT · What changed when H was present?", 48, 456);
  fill(soundReady ? color(74, 220, 142) : color(242, 132, 54));
  textSize(12);
  text(audioStatus, 48, 492);
}

void mouseClicked() {
  if (hit(48, 128, 220, 58)) {
    useH = !useH;
    hearState();
  } else if (hit(492, 128, 220, 58)) {
    hearState();
  }
}

void hearState() {
  if (!soundReady) {
    audioStatus = "Missing library: install official Sound, then reopen.";
    return;
  }
  cue = useH ? new float[]{220, 440} : new float[]{220};
  cueIndex = 0;
  nextTone = millis();
}

void playQueuedTone() {
  if (cueIndex >= cue.length || millis() < nextTone) return;
  try {
    tone.play(cue[cueIndex], 0.18);
    envelope.play(tone, 0.008, 0.16, 0.16, 0.24);
    cueIndex++;
    nextTone = millis() + 480;
    audioStatus = "Played " + (useH ? "two possible outcomes." : "the certain |0〉 outcome.");
  } catch (Throwable error) {
    soundReady = false;
    audioStatus = "Audio device failed; run 01_superposition.py.";
  }
}

void probabilityBar(float x, float y, float w, float value, String label, int c) {
  fill(245);
  textSize(14);
  text(label, x, y);
  noStroke();
  fill(28, 40, 57);
  rect(x, y + 14, w, 28, 6);
  fill(c);
  rect(x, y + 14, max(1, w * value), 28, 6);
  fill(245);
  text(round(value * 100) + "%", x + w - 42, y + 35);
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
  if (tone != null) tone.stop();
  super.exit();
}
