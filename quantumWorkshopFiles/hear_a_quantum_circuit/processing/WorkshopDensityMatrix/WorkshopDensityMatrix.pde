/*
 * Research bridge — Density matrix unfolding in time
 *
 * One idea: rho(t) is a state engine. Its populations, coherence, phase,
 * Bloch vector, and sound all change together as preparation time t advances.
 *
 * Install Processing's official Sound library in Contribution Manager first.
 */
import processing.sound.*;

float[][] rhoReal = new float[2][2];
float[][] rhoImag = new float[2][2];

boolean evolving = false;
boolean evolutionFamily = true;
float evolutionTime = 0.0;
float dephaseRate = 0.16;
float phasePeriod = 8.0;
int previousMillis = 0;

Pulse tone;
LowPass filter;
boolean soundReady = false;
boolean filterConnected = false;
boolean engineSoundActive = false;
String audioStatus = "Initializing Sound…";

float[] coherenceHistory = new float[260];
float[] phaseHistory = new float[260];
int historyCount = 0;
int lastHistoryMillis = 0;

void setup() {
  size(1100, 720);
  smooth(8);
  textFont(createFont("Arial", 16));
  resetPurePlus();
  previousMillis = millis();
  try {
    tone = new Pulse(this);
    filter = new LowPass(this);
    soundReady = true;
    audioStatus = "Sound ready · PLAY ρ(t) starts one evolving tone.";
  } catch (Throwable error) {
    audioStatus = "Sound missing: install Sound in Contribution Manager.";
  }
}

void draw() {
  updateDensityEngine();
  background(8, 12, 20);
  drawHeader();
  drawEngineControls();
  drawDensityMatrix();
  drawBlochFromDensity();
  drawTimeStory();
  drawFooter();
}

void drawHeader() {
  fill(245);
  textSize(26);
  text("RESEARCH BRIDGE · DENSITY MATRIX ρ(t)", 32, 42);
  fill(155, 178, 207);
  textSize(14);
  text(
    "Watch one valid state engine unfold: populations stay fixed while coherence rotates and decays.",
    34, 68
  );
}

void drawEngineControls() {
  button(34, 92, 142, 42, "RESET PURE |+〉", false);
  button(190, 92, 90, 42, "− 0.5 s", false);
  button(292, 92, 90, 42, "+ 0.5 s", false);
  button(394, 92, 142, 42, evolving ? "PAUSE ρ(t)" : "PLAY ρ(t)", evolving);
  button(550, 92, 142, 42, "MIXED I/2", false);

  fill(245);
  textSize(13);
  text("PREPARATION TIME  t = " + nf(evolutionTime, 1, 2) + " s", 748, 108);
  fill(155, 178, 207);
  textSize(11);
  text("t advances the state continuously; it is not a shot count.", 748, 130);
}

void drawDensityMatrix() {
  fill(245);
  textSize(18);
  text("THE ENGINE · 2 × 2 DENSITY MATRIX", 38, 178);
  fill(155, 178, 207);
  textSize(12);
  text("brightness = magnitude · hue = complex phase", 38, 198);

  String[] labels = {"|0〉", "|1〉"};
  for (int column = 0; column < 2; column++) {
    fill(155, 178, 207);
    textAlign(CENTER, CENTER);
    text(labels[column] + " bra", 116 + column * 148, 222);
  }
  for (int row = 0; row < 2; row++) {
    fill(155, 178, 207);
    textAlign(RIGHT, CENTER);
    text(labels[row], 40, 282 + row * 112);
    for (int column = 0; column < 2; column++) {
      drawDensityCell(
        50 + column * 148, 242 + row * 112, 136, 92,
        rhoReal[row][column], rhoImag[row][column],
        "ρ" + row + column
      );
    }
  }
  textAlign(LEFT, BASELINE);

  fill(245);
  textSize(15);
  text("Trace        " + nf(densityTrace(), 1, 3), 50, 494);
  text("Purity       " + nf(densityPurity(), 1, 3), 50, 520);
  text("Coherence    " + nf(coherenceMagnitude(), 1, 3), 50, 546);
  fill(155, 178, 207);
  textSize(12);
  text("Diagonal cells: populations", 50, 578);
  text("Off-diagonal cells: coherence + phase", 50, 598);
}

void drawDensityCell(
  float x, float y, float w, float h,
  float realValue, float imaginaryValue, String label
) {
  float magnitude = sqrt(realValue * realValue + imaginaryValue * imaginaryValue);
  float phase = atan2(imaginaryValue, realValue);
  colorMode(HSB, 360, 100, 100, 100);
  float hue = map(phase, -PI, PI, 0, 360);
  float brightness = 18 + 82 * constrain(magnitude / 0.5, 0, 1);
  noStroke();
  fill(hue, magnitude < 0.001 ? 0 : 72, brightness, 100);
  rect(x, y, w, h, 10);
  colorMode(RGB, 255, 255, 255, 255);

  fill(brightness > 58 ? color(8, 12, 20) : color(245));
  textAlign(CENTER, CENTER);
  textSize(13);
  text(label, x + w / 2, y + 20);
  textSize(16);
  text(complexText(realValue, imaginaryValue), x + w / 2, y + 51);
  textSize(11);
  text("|ρ| " + nf(magnitude, 1, 3), x + w / 2, y + 75);
  textAlign(LEFT, BASELINE);
}

void drawBlochFromDensity() {
  float centerX = 552;
  float centerY = 346;
  float radius = 132;
  float x = blochX();
  float y = blochY();

  fill(245);
  textSize(18);
  text("BLOCH VECTOR DERIVED FROM ρ", 400, 178);
  fill(155, 178, 207);
  textSize(12);
  text("projection rotates; length shrinks as coherence is lost", 400, 198);

  noFill();
  stroke(92, 112, 145);
  strokeWeight(2);
  ellipse(centerX, centerY, radius * 2, radius * 2);
  stroke(58, 76, 102);
  line(centerX - radius, centerY, centerX + radius, centerY);
  line(centerX, centerY - radius, centerX, centerY + radius);

  stroke(242, 194, 28);
  strokeWeight(5);
  line(centerX, centerY, centerX + radius * x, centerY - radius * y);
  noStroke();
  fill(242, 194, 28);
  ellipse(centerX + radius * x, centerY - radius * y, 15, 15);
  fill(155, 178, 207);
  textSize(11);
  text("+X", centerX + radius + 8, centerY + 4);
  text("+Y", centerX - 9, centerY - radius - 8);

  fill(245);
  textSize(14);
  text("x  " + signed(blochX()), 430, 522);
  text("y  " + signed(blochY()), 520, 522);
  text("z  " + signed(blochZ()), 610, 522);
  text("|r|  " + nf(blochLength(), 1, 3), 430, 550);
}

void drawTimeStory() {
  float graphX = 748;
  float graphY = 210;
  float graphW = 310;
  float graphH = 250;

  fill(245);
  textSize(18);
  text("UNFOLDING IN TIME", 748, 178);
  fill(155, 178, 207);
  textSize(12);
  text("yellow = coherence · blue = wrapped phase", 748, 198);

  noStroke();
  fill(18, 27, 40);
  rect(graphX, graphY, graphW, graphH, 10);
  stroke(58, 76, 102);
  line(graphX, graphY + graphH / 2, graphX + graphW, graphY + graphH / 2);

  int points = min(historyCount, coherenceHistory.length);
  if (points > 1) {
    noFill();
    stroke(242, 194, 28);
    strokeWeight(3);
    beginShape();
    for (int i = 0; i < points; i++) {
      float px = map(i, 0, coherenceHistory.length - 1, graphX, graphX + graphW);
      float py = graphY + graphH - coherenceHistory[i] * graphH;
      vertex(px, py);
    }
    endShape();

    stroke(91, 151, 246);
    strokeWeight(2);
    beginShape();
    for (int i = 0; i < points; i++) {
      float px = map(i, 0, coherenceHistory.length - 1, graphX, graphX + graphW);
      float py = map(phaseHistory[i], 0, TWO_PI, graphY + graphH, graphY);
      vertex(px, py);
    }
    endShape();
  }

  fill(245);
  textSize(14);
  text("ρ01(t) = ½ e^(−γt) e^(−iωt)", 748, 500);
  fill(155, 178, 207);
  textSize(12);
  text("coherence magnitude  " + nf(coherenceMagnitude(), 1, 3), 748, 532);
  text("coherence phase      " + nf(wrappedCoherencePhase(), 1, 3) + " rad", 748, 554);
  text("tone cutoff          " + round(engineCutoff()) + " Hz", 748, 576);
  text("pulse duty           " + round(engineDuty() * 100) + "%", 748, 598);
}

void drawFooter() {
  fill(soundReady ? color(74, 220, 142) : color(242, 132, 54));
  textSize(12);
  text(audioStatus, 40, 680);
  fill(155, 178, 207);
  text(
    "Chosen sonification: coherence → brightness; complex phase → pulse width.",
    40, 702
  );
}

void updateDensityEngine() {
  int now = millis();
  float deltaSeconds = constrain((now - previousMillis) / 1000.0, 0, 0.05);
  previousMillis = now;
  if (!evolving) return;

  evolutionTime += deltaSeconds;
  setEvolutionDensity(evolutionTime);
  updateEngineSound();

  if (now - lastHistoryMillis > 80) {
    pushHistory();
    lastHistoryMillis = now;
  }
}

void resetPurePlus() {
  stopEngineSound();
  evolutionTime = 0;
  evolving = false;
  evolutionFamily = true;
  setEvolutionDensity(0);
  clearHistory();
  pushHistory();
  if (soundReady) audioStatus = "PURE |+〉 ready · press PLAY ρ(t).";
}

void setEvolutionDensity(float time) {
  float coherence = exp(-dephaseRate * time);
  float phase = TWO_PI * time / phasePeriod;
  rhoReal[0][0] = 0.5;
  rhoImag[0][0] = 0;
  rhoReal[1][1] = 0.5;
  rhoImag[1][1] = 0;
  rhoReal[0][1] = 0.5 * coherence * cos(phase);
  rhoImag[0][1] = -0.5 * coherence * sin(phase);
  rhoReal[1][0] = rhoReal[0][1];
  rhoImag[1][0] = -rhoImag[0][1];
}

void setMixedDensity() {
  stopEngineSound();
  evolving = false;
  evolutionFamily = false;
  rhoReal[0][0] = 0.5;
  rhoImag[0][0] = 0;
  rhoReal[1][1] = 0.5;
  rhoImag[1][1] = 0;
  rhoReal[0][1] = 0;
  rhoImag[0][1] = 0;
  rhoReal[1][0] = 0;
  rhoImag[1][0] = 0;
  clearHistory();
  pushHistory();
  if (soundReady) audioStatus = "MIXED I/2 · zero coherence, no phase direction.";
}

void mouseClicked() {
  if (hit(34, 92, 142, 42)) {
    resetPurePlus();
    return;
  }
  if (hit(190, 92, 90, 42)) {
    setEvolutionTime(evolutionTime - 0.5);
    return;
  }
  if (hit(292, 92, 90, 42)) {
    setEvolutionTime(evolutionTime + 0.5);
    return;
  }
  if (hit(394, 92, 142, 42)) {
    if (!evolutionFamily) resetPurePlus();
    evolving = !evolving;
    if (evolving) startEngineSound();
    else {
      stopEngineSound();
      if (soundReady) {
        audioStatus = "ρ(t) PAUSED at " + nf(evolutionTime, 1, 2) + " s.";
      }
    }
    return;
  }
  if (hit(550, 92, 142, 42)) setMixedDensity();
}

void setEvolutionTime(float requestedTime) {
  stopEngineSound();
  evolving = false;
  evolutionFamily = true;
  evolutionTime = constrain(requestedTime, 0, 20);
  setEvolutionDensity(evolutionTime);
  pushHistory();
  if (soundReady) {
    audioStatus = "ρ prepared at t=" + nf(evolutionTime, 1, 2) + " s.";
  }
}

void startEngineSound() {
  if (!soundReady || tone == null) {
    audioStatus = "ρ(t) is moving visually. Install Sound to hear it.";
    return;
  }
  try {
    tone.width(engineDuty());
    tone.play(330.0, 0.10);
    if (!filterConnected) {
      filter.process(tone, engineCutoff());
      filterConnected = true;
    } else {
      filter.freq(engineCutoff());
    }
    engineSoundActive = true;
    updateEngineSound();
  } catch (Throwable error) {
    soundReady = false;
    engineSoundActive = false;
    audioStatus = "Audio device failed; ρ(t) still evolves visually.";
  }
}

void updateEngineSound() {
  if (!soundReady || !engineSoundActive || tone == null) return;
  try {
    tone.freq(330.0);
    tone.width(engineDuty());
    filter.freq(engineCutoff());
    audioStatus = "ρ(t) SOUND · phase duty " + round(engineDuty() * 100)
      + "% · coherence cutoff " + round(engineCutoff()) + " Hz";
  } catch (Throwable error) {
    soundReady = false;
    engineSoundActive = false;
    audioStatus = "Audio device failed; ρ(t) still evolves visually.";
  }
}

float engineDuty() {
  if (coherenceMagnitude() < 0.001) return 0.5;
  return map(wrappedCoherencePhase(), 0, TWO_PI, 0.03, 0.97);
}

float engineCutoff() {
  return lerp(700, 5000, coherenceMagnitude());
}

void stopEngineSound() {
  if (engineSoundActive && tone != null) {
    try {
      tone.stop();
    } catch (Throwable error) {
      // The visual engine remains usable if the audio device disappears.
    }
  }
  engineSoundActive = false;
}

void clearHistory() {
  historyCount = 0;
  for (int i = 0; i < coherenceHistory.length; i++) {
    coherenceHistory[i] = 0;
    phaseHistory[i] = 0;
  }
}

void pushHistory() {
  if (historyCount < coherenceHistory.length) {
    coherenceHistory[historyCount] = coherenceMagnitude();
    phaseHistory[historyCount] = wrappedCoherencePhase();
    historyCount++;
    return;
  }
  for (int i = 1; i < coherenceHistory.length; i++) {
    coherenceHistory[i - 1] = coherenceHistory[i];
    phaseHistory[i - 1] = phaseHistory[i];
  }
  coherenceHistory[coherenceHistory.length - 1] = coherenceMagnitude();
  phaseHistory[phaseHistory.length - 1] = wrappedCoherencePhase();
}

float densityTrace() {
  return rhoReal[0][0] + rhoReal[1][1];
}

float densityPurity() {
  float sum = 0;
  for (int row = 0; row < 2; row++) {
    for (int column = 0; column < 2; column++) {
      sum += rhoReal[row][column] * rhoReal[row][column]
        + rhoImag[row][column] * rhoImag[row][column];
    }
  }
  return constrain(sum, 0, 1);
}

float coherenceMagnitude() {
  return constrain(
    2.0 * sqrt(
      rhoReal[0][1] * rhoReal[0][1]
      + rhoImag[0][1] * rhoImag[0][1]
    ),
    0, 1
  );
}

float coherencePhase() {
  if (coherenceMagnitude() < 0.001) return 0;
  return atan2(-rhoImag[0][1], rhoReal[0][1]);
}

float wrappedCoherencePhase() {
  return (coherencePhase() + TWO_PI) % TWO_PI;
}

float blochX() {
  return rhoReal[0][1] + rhoReal[1][0];
}

float blochY() {
  return rhoImag[1][0] - rhoImag[0][1];
}

float blochZ() {
  return rhoReal[0][0] - rhoReal[1][1];
}

float blochLength() {
  float x = blochX();
  float y = blochY();
  float z = blochZ();
  return sqrt(x * x + y * y + z * z);
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

String complexText(float realValue, float imaginaryValue) {
  String sign = imaginaryValue >= 0 ? " + " : " − ";
  return nf(realValue, 1, 3) + sign + nf(abs(imaginaryValue), 1, 3) + "i";
}

String signed(float value) {
  if (abs(value) < 0.005) value = 0;
  return (value >= 0 ? "+" : "") + nf(value, 1, 2);
}

void exit() {
  stopEngineSound();
  if (tone != null) tone.stop();
  super.exit();
}
