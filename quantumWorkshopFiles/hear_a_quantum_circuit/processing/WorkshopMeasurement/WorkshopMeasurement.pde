/*
 * Module 5 — Measurement and entropy
 *
 * One idea: repeated measurements sample one prepared state.
 * A single copy gives one outcome; many fresh copies reveal a distribution.
 *
 * Install Processing's official Sound library in Contribution Manager first.
 */
import processing.sound.*;

String preparation = "|+〉";
float theta = HALF_PI;
float phi = 0.0;
String basis = "Z";

int shots = 32;
int lastBatchShots = 32;
int countA = 16;
int countB = 16;
float sampleEntropy = 1.0;
String lastOutcome = "none yet";
boolean copyCollapsed = false;
int collapsedOutcome = 0;

Pulse toneA;
Pulse toneB;
Env envA;
Env envB;
boolean soundReady = false;
String audioStatus = "Initializing Sound…";

void setup() {
  size(1100, 720);
  smooth(8);
  textFont(createFont("Arial", 16));
  runBatch(false);
  try {
    toneA = new Pulse(this);
    toneB = new Pulse(this);
    envA = new Env(this);
    envB = new Env(this);
    toneA.width(0.5);
    toneB.width(0.5);
    soundReady = true;
    audioStatus = "Sound ready · one measurement plays one outcome.";
  } catch (Throwable error) {
    audioStatus = "Sound missing: install Sound in Contribution Manager.";
  }
}

void draw() {
  background(8, 12, 20);
  drawHeader();
  drawPreparation();
  drawPrediction();
  drawSingleCopy();
  drawBatch();
  drawFooter();
}

void drawHeader() {
  fill(245);
  textSize(26);
  text("MODULE 5 · MEASUREMENT + ENTROPY", 32, 42);
  fill(155, 178, 207);
  textSize(14);
  text(
    "Prepare one state. Measure fresh copies. Compare one outcome with a distribution.",
    34, 68
  );
}

void drawPreparation() {
  fill(245);
  textSize(18);
  text("1 · PREPARE THE SAME STATE", 38, 112);

  button(38, 132, 70, 38, "|0〉", preparation.equals("|0〉"));
  button(118, 132, 70, 38, "H → |+〉", preparation.equals("|+〉"));
  button(198, 132, 84, 38, "75 / 25", preparation.equals("75/25"));
  button(292, 132, 70, 38, "|1〉", preparation.equals("|1〉"));

  fill(155, 178, 207);
  textSize(12);
  text("Prepared state", 38, 208);
  fill(245);
  textSize(20);
  text(preparationLabel(), 38, 238);

  fill(155, 178, 207);
  textSize(12);
  text("Choose a measurement basis", 38, 282);
  button(38, 296, 112, 38, "Z BASIS", basis.equals("Z"));
  button(162, 296, 112, 38, "X BASIS", basis.equals("X"));

  fill(155, 178, 207);
  textSize(12);
  text(
    basis.equals("Z")
      ? "Z asks: |0〉 or |1〉?"
      : "X asks: |+〉 or |−〉?",
    38, 364
  );
}

void drawPrediction() {
  float[] probabilities = probabilitiesForBasis();
  String first = firstLabel();
  String second = secondLabel();

  fill(245);
  textSize(18);
  text("2 · PREDICT", 390, 112);
  fill(155, 178, 207);
  textSize(12);
  text("Quantum probabilities for every fresh copy", 390, 136);

  probabilityBar(390, 174, 290, probabilities[0], first, color(91, 151, 246));
  probabilityBar(390, 244, 290, probabilities[1], second, color(242, 132, 54));

  fill(245);
  textSize(16);
  text("Expected entropy", 390, 338);
  fill(242, 194, 28);
  textSize(32);
  text(nf(binaryEntropy(probabilities[0]), 1, 3) + " bits", 390, 378);
  fill(155, 178, 207);
  textSize(11);
  text("0 bits = certain · 1 bit = evenly split", 390, 402);
}

void drawSingleCopy() {
  fill(245);
  textSize(18);
  text("3 · MEASURE ONE FRESH COPY", 744, 112);
  button(744, 138, 256, 44, "MEASURE ONCE", false);

  fill(155, 178, 207);
  textSize(12);
  text("One copy cannot reveal the distribution.", 744, 210);

  noStroke();
  fill(28, 40, 57);
  rect(744, 238, 256, 126, 12);
  if (copyCollapsed) {
    fill(collapsedOutcome == 0 ? color(91, 151, 246) : color(242, 132, 54));
    ellipse(786, 301, 54, 54);
    fill(245);
    textSize(15);
    text("Outcome  " + lastOutcome, 830, 294);
    fill(155, 178, 207);
    textSize(11);
    text("this copy collapsed", 830, 319);
  } else {
    fill(155, 178, 207);
    textSize(14);
    text("No copy measured yet", 776, 306);
  }

  fill(155, 178, 207);
  textSize(11);
  text("The preparation above is unchanged;", 744, 390);
  text("the next click prepares a new copy.", 744, 408);
}

void drawBatch() {
  fill(245);
  textSize(18);
  text("4 · REPEAT WITH FRESH COPIES", 38, 458);

  int[] choices = {8, 32, 256};
  for (int i = 0; i < choices.length; i++) {
    button(38 + i * 76, 478, 66, 36, str(choices[i]), shots == choices[i]);
  }
  button(276, 478, 108, 36, "RUN BATCH", false);

  float sampleA = float(countA) / lastBatchShots;
  float sampleB = float(countB) / lastBatchShots;
  sampleBar(
    420, 486, 360, sampleA,
    firstLabel() + " · " + countA, color(91, 151, 246)
  );
  sampleBar(
    420, 542, 360, sampleB,
    secondLabel() + " · " + countB, color(242, 132, 54)
  );

  fill(245);
  textSize(15);
  text("Observed entropy", 874, 486);
  fill(242, 194, 28);
  textSize(30);
  text(nf(sampleEntropy, 1, 3), 874, 526);
  fill(155, 178, 207);
  textSize(12);
  text("bits", 874, 548);

  fill(155, 178, 207);
  textSize(12);
  text(
    "Last batch: " + lastBatchShots + " independent preparations in the "
      + basis + " basis.",
    38, 610
  );
  text(
    "Try 8 several times, then 256. The prediction stays fixed while the sample varies.",
    38, 634
  );
}

void drawFooter() {
  fill(soundReady ? color(74, 220, 142) : color(242, 132, 54));
  textSize(12);
  text(audioStatus, 40, 680);
  fill(155, 178, 207);
  text(
    "Measurement count is not time: every shot begins with a newly prepared copy.",
    40, 702
  );
}

void mouseClicked() {
  if (hit(38, 132, 70, 38)) {
    prepareState("|0〉", 0, 0);
    return;
  }
  if (hit(118, 132, 70, 38)) {
    prepareState("|+〉", HALF_PI, 0);
    return;
  }
  if (hit(198, 132, 84, 38)) {
    prepareState("75/25", 2.0 * acos(sqrt(0.75)), 0);
    return;
  }
  if (hit(292, 132, 70, 38)) {
    prepareState("|1〉", PI, 0);
    return;
  }
  if (hit(38, 296, 112, 38)) {
    basis = "Z";
    resetResults();
    return;
  }
  if (hit(162, 296, 112, 38)) {
    basis = "X";
    resetResults();
    return;
  }
  if (hit(744, 138, 256, 44)) {
    measureOne();
    return;
  }

  int[] choices = {8, 32, 256};
  for (int i = 0; i < choices.length; i++) {
    if (hit(38 + i * 76, 478, 66, 36)) {
      shots = choices[i];
      return;
    }
  }
  if (hit(276, 478, 108, 36)) runBatch(true);
}

void prepareState(String name, float newTheta, float newPhi) {
  preparation = name;
  theta = newTheta;
  phi = newPhi;
  resetResults();
}

void resetResults() {
  copyCollapsed = false;
  lastOutcome = "none yet";
  runBatch(false);
  if (soundReady) audioStatus = "State ready · predict, then measure.";
}

void measureOne() {
  float[] probabilities = probabilitiesForBasis();
  collapsedOutcome = random(1) < probabilities[0] ? 0 : 1;
  copyCollapsed = true;
  lastOutcome = collapsedOutcome == 0 ? firstLabel() : secondLabel();
  playOutcome(collapsedOutcome);
}

void runBatch(boolean playSound) {
  float[] probabilities = probabilitiesForBasis();
  countA = 0;
  for (int shot = 0; shot < shots; shot++) {
    if (random(1) < probabilities[0]) countA++;
  }
  countB = shots - countA;
  lastBatchShots = shots;
  float pA = float(countA) / lastBatchShots;
  float pB = float(countB) / lastBatchShots;
  sampleEntropy = entropyTerm(pA) + entropyTerm(pB);
  if (playSound) playBatchSummary(pA, pB);
}

float[] probabilitiesForBasis() {
  float z0 = sq(cos(theta / 2.0));
  if (basis.equals("Z")) return new float[]{z0, 1.0 - z0};
  float plus = 0.5 * (1.0 + sin(theta) * cos(phi));
  plus = constrain(plus, 0, 1);
  return new float[]{plus, 1.0 - plus};
}

void playOutcome(int outcome) {
  if (!soundReady) {
    audioStatus = "Visual result ready · install Sound to hear outcomes.";
    return;
  }
  try {
    float frequency = outcome == 0 ? firstFrequency() : secondFrequency();
    Pulse selectedTone = outcome == 0 ? toneA : toneB;
    Env selectedEnv = outcome == 0 ? envA : envB;
    selectedTone.play(frequency, 0.18);
    selectedEnv.play(selectedTone, 0.008, 0.16, 0.12, 0.28);
    audioStatus = "One copy → " + lastOutcome + " · " + round(frequency) + " Hz.";
  } catch (Throwable error) {
    soundReady = false;
    audioStatus = "Audio device failed; the visual measurement still works.";
  }
}

void playBatchSummary(float pA, float pB) {
  if (!soundReady) {
    audioStatus = "Batch complete · install Sound to hear its summary chord.";
    return;
  }
  try {
    toneA.play(firstFrequency(), 0.14 * sqrt(pA));
    toneB.play(secondFrequency(), 0.14 * sqrt(pB));
    envA.play(toneA, 0.008, 0.22, 0.10, 0.32);
    envB.play(toneB, 0.008, 0.22, 0.10, 0.32);
    audioStatus = "Batch summary chord · loudness follows observed counts.";
  } catch (Throwable error) {
    soundReady = false;
    audioStatus = "Audio device failed; the histogram still shows the batch.";
  }
}

float firstFrequency() {
  return basis.equals("Z") ? 220.0 : 330.0;
}

float secondFrequency() {
  return basis.equals("Z") ? 440.0 : 495.0;
}

String firstLabel() {
  return basis.equals("Z") ? "|0〉" : "|+〉";
}

String secondLabel() {
  return basis.equals("Z") ? "|1〉" : "|−〉";
}

String preparationLabel() {
  if (preparation.equals("|0〉")) return "|ψ〉 = |0〉";
  if (preparation.equals("|1〉")) return "|ψ〉 = |1〉";
  if (preparation.equals("|+〉")) return "|ψ〉 = (|0〉 + |1〉) / √2";
  return "|ψ〉 = √0.75 |0〉 + √0.25 |1〉";
}

float binaryEntropy(float probabilityA) {
  return entropyTerm(probabilityA) + entropyTerm(1.0 - probabilityA);
}

float entropyTerm(float probability) {
  if (probability <= 0) return 0;
  return -probability * (log(probability) / log(2));
}

void probabilityBar(float x, float y, float w, float value, String label, int c) {
  fill(245);
  textSize(14);
  text(label + "  " + round(value * 100) + "%", x, y);
  noStroke();
  fill(28, 40, 57);
  rect(x, y + 12, w, 22, 6);
  fill(c);
  rect(x, y + 12, max(1, w * value), 22, 6);
}

void sampleBar(float x, float y, float w, float value, String label, int c) {
  fill(245);
  textSize(13);
  text(label, x, y);
  noStroke();
  fill(28, 40, 57);
  rect(x, y + 10, w, 20, 5);
  fill(c);
  rect(x, y + 10, max(1, w * value), 20, 5);
  fill(155, 178, 207);
  text(round(value * 100) + "%", x + w + 12, y + 26);
}

void button(float x, float y, float w, float h, String label, boolean active) {
  boolean hover = hit(x, y, w, h);
  noStroke();
  fill(active ? color(242, 132, 54)
    : hover ? color(242, 194, 28) : color(28, 40, 57));
  rect(x, y, w, h, 8);
  fill(active || hover ? color(8, 12, 20) : color(245));
  textAlign(CENTER, CENTER);
  textSize(12);
  text(label, x + w / 2, y + h / 2);
  textAlign(LEFT, BASELINE);
}

boolean hit(float x, float y, float w, float h) {
  return mouseX >= x && mouseX <= x + w && mouseY >= y && mouseY <= y + h;
}

void exit() {
  if (toneA != null) toneA.stop();
  if (toneB != null) toneB.stop();
  super.exit();
}
