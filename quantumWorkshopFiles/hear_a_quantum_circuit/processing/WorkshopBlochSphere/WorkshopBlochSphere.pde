/*
 * Hear a Quantum Circuit — Module 2: Bloch sphere
 *
 * One idea: theta moves north-to-south; phi moves around the equator.
 * Direct sound uses Processing Sound's Pulse, Env, and LowPass.
 * Theta controls pitch; phi controls pulse width.
 *
 * Install: Sketch > Import Library > Manage Libraries > search "Sound"
 * Optional input-only OSC: /qmw/circuit/q0/bloch x y z on UDP 7497.
 */

import processing.sound.*;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.SocketTimeoutException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

float theta = 0.0;
float phi = 0.0;
float blochX = 0.0;
float blochY = 0.0;
float blochZ = 1.0;
float smoothX = 0.0;
float smoothY = 0.0;
float smoothZ = 1.0;
float sphereRadius = 205;
float northScreenX = 0;
float northScreenY = 0;
float southScreenX = 0;
float southScreenY = 0;
float plusScreenX = 0;
float plusScreenY = 0;
float minusScreenX = 0;
float minusScreenY = 0;
float plusIScreenX = 0;
float plusIScreenY = 0;
float minusIScreenX = 0;
float minusIScreenY = 0;

Pulse stateOscillator;
LowPass stateFilter;
Env stateEnvelope;
boolean soundReady = false;
boolean filterConnected = false;
boolean liveSound = false;
String audioStatus = "Initializing Processing Sound…";
int lastSoundMillis = -100000;

int oscPort = 7497;
int lastOscMillis = -100000;
boolean keepListening = true;
DatagramSocket oscSocket;

float playButtonX = 742;
float playButtonY = 560;
float playButtonWidth = 210;
float playButtonHeight = 46;

String[] buttonLabels = {
  "H", "X", "Y", "Z", "RX −", "RX +", "RY −", "RY +", "RZ −", "RZ +"
};
float buttonLeft = 34;
float buttonTop = 84;
float buttonWidth = 78;
float buttonHeight = 36;
float buttonGap = 8;

void setup() {
  size(980, 720, P3D);
  smooth(8);
  sphereDetail(36);
  textFont(createFont("Arial", 16));
  updateVectorFromAngles();
  initializeSound();
  thread("listenForOsc");
}

void draw() {
  background(8, 12, 20);
  lights();

  smoothX = lerp(smoothX, blochX, 0.18);
  smoothY = lerp(smoothY, blochY, 0.18);
  smoothZ = lerp(smoothZ, blochZ, 0.18);

  drawHeader();
  drawButtons();

  pushMatrix();
  translate(width * 0.48, height * 0.57, 0);
  rotateX(-0.20);
  rotateY(0.48);
  drawSphere();
  drawAxes();
  drawBasisPoints();
  drawBlochVector();
  // Mathematical Bloch +Z is rendered as world -Y: visibly up on screen.
  northScreenX = screenX(0, -sphereRadius, 0);
  northScreenY = screenY(0, -sphereRadius, 0);
  southScreenX = screenX(0, sphereRadius, 0);
  southScreenY = screenY(0, sphereRadius, 0);
  plusScreenX = screenX(sphereRadius, 0, 0);
  plusScreenY = screenY(sphereRadius, 0, 0);
  minusScreenX = screenX(-sphereRadius, 0, 0);
  minusScreenY = screenY(-sphereRadius, 0, 0);
  plusIScreenX = screenX(0, 0, sphereRadius);
  plusIScreenY = screenY(0, 0, sphereRadius);
  minusIScreenX = screenX(0, 0, -sphereRadius);
  minusIScreenY = screenY(0, 0, -sphereRadius);
  popMatrix();

  drawCanonicalStateLabels();
  drawReadout();
  drawConnectionStatus();
  drawAudioControl();
}

void drawHeader() {
  beginFlat();
  fill(245);
  textSize(25);
  text("MODULE 2 · MOVE ONE QUBIT ON THE BLOCH SPHERE", 32, 38);
  fill(155, 178, 207);
  textSize(14);
  text("Move the state, then choose PLAY SELECTED STATE (or press P).", 34, 64);
  endFlat();
}

void drawButtons() {
  beginFlat();
  for (int i = 0; i < buttonLabels.length; i++) {
    float x = buttonLeft + i * (buttonWidth + buttonGap);
    drawButton(x, buttonTop, buttonWidth, buttonHeight, buttonLabels[i]);
  }
  drawButton(34, 132, 152, 40, "RESET · NORTH |0〉");
  endFlat();
}

void drawSphere() {
  noFill();
  stroke(92, 112, 145, 130);
  strokeWeight(1.2);
  sphere(sphereRadius);

  stroke(92, 112, 145, 95);
  ellipse(0, 0, sphereRadius * 2, sphereRadius * 2);
  pushMatrix();
  rotateX(HALF_PI);
  ellipse(0, 0, sphereRadius * 2, sphereRadius * 2);
  popMatrix();
  pushMatrix();
  rotateY(HALF_PI);
  ellipse(0, 0, sphereRadius * 2, sphereRadius * 2);
  popMatrix();
}

void drawAxes() {
  float axis = sphereRadius * 1.18;
  // Rendered frame: Bloch X = world X, Bloch Y = world Z,
  // Bloch Z = world -Y so north/south stays visibly vertical.
  strokeWeight(2);
  stroke(238, 100, 92, 210);
  line(-axis, 0, 0, axis, 0, 0);
  stroke(91, 151, 246, 210);
  line(0, 0, -axis, 0, 0, axis);
  stroke(90, 218, 142, 220);
  line(0, axis, 0, 0, -axis, 0);
}

void drawBasisPoints() {
  noStroke();
  drawPoint(sphereRadius, 0, 0, color(238, 100, 92));
  drawPoint(-sphereRadius, 0, 0, color(238, 100, 92));
  drawPoint(0, -sphereRadius, 0, color(90, 218, 142));
  drawPoint(0, sphereRadius, 0, color(242, 132, 54));
  drawPoint(0, 0, sphereRadius, color(91, 151, 246));
  drawPoint(0, 0, -sphereRadius, color(91, 151, 246));
}

void drawPoint(float x, float y, float z, int pointColor) {
  pushMatrix();
  translate(x, y, z);
  fill(pointColor);
  sphere(6);
  popMatrix();
}

void drawBlochVector() {
  // Render transform:
  //   mathematical X -> world X
  //   mathematical Y -> world Z
  //   mathematical Z -> world -Y (north is visibly up)
  float vx = smoothX * sphereRadius;
  float vy = -smoothZ * sphereRadius;
  float vz = smoothY * sphereRadius;
  stroke(250, 199, 38);
  strokeWeight(5);
  line(0, 0, 0, vx, vy, vz);
  pushMatrix();
  translate(vx, vy, vz);
  noStroke();
  fill(250, 199, 38);
  sphere(12);
  popMatrix();
}

void drawCanonicalStateLabels() {
  beginFlat();
  drawPoleLabel(northScreenX, northScreenY, "NORTH  +Z  |0〉", color(91, 151, 246));
  drawPoleLabel(southScreenX, southScreenY, "SOUTH  −Z  |1〉", color(242, 132, 54));
  drawEquatorLabel(plusScreenX, plusScreenY, "|+〉  +X", color(238, 100, 92), 10, -18);
  drawEquatorLabel(minusScreenX, minusScreenY, "|−〉  −X", color(238, 100, 92), -98, -18);
  drawEquatorLabel(plusIScreenX, plusIScreenY, "|+i〉  +Y", color(91, 151, 246), 10, 8);
  drawEquatorLabel(minusIScreenX, minusIScreenY, "|−i〉  −Y", color(91, 151, 246), -102, -35);
  endFlat();
}

void drawPoleLabel(float x, float y, String label, int labelColor) {
  float boxWidth = 134;
  float boxX = constrain(x - boxWidth / 2, 16, width - boxWidth - 16);
  float boxY = constrain(y - 34, 184, height - 78);
  noStroke();
  fill(8, 12, 20, 225);
  rect(boxX, boxY, boxWidth, 27, 6);
  stroke(labelColor);
  strokeWeight(2);
  line(x, y, constrain(x, boxX + 8, boxX + boxWidth - 8), boxY + 27);
  noStroke();
  fill(labelColor);
  textAlign(CENTER, CENTER);
  textSize(11);
  text(label, boxX + boxWidth / 2, boxY + 13);
  textAlign(LEFT, BASELINE);
}

void drawEquatorLabel(
  float pointX, float pointY, String label, int labelColor, float dx, float dy
) {
  float boxWidth = 88;
  float boxX = constrain(pointX + dx, 16, width - boxWidth - 16);
  float boxY = constrain(pointY + dy, 182, height - 72);
  noStroke();
  fill(8, 12, 20, 220);
  rect(boxX, boxY, boxWidth, 25, 6);
  stroke(labelColor);
  strokeWeight(1.5);
  float edgeX = dx >= 0 ? boxX : boxX + boxWidth;
  line(pointX, pointY, edgeX, boxY + 12);
  noStroke();
  fill(labelColor);
  textAlign(CENTER, CENTER);
  textSize(11);
  text(label, boxX + boxWidth / 2, boxY + 12);
  textAlign(LEFT, BASELINE);
}

void drawReadout() {
  beginFlat();
  float panelX = 742;
  float panelY = 158;
  float p0 = (1.0 + blochZ) * 0.5;
  float p1 = (1.0 - blochZ) * 0.5;

  noStroke();
  fill(18, 26, 38, 235);
  rect(panelX, panelY, 210, 338, 12);
  fill(245);
  textSize(17);
  text("STATE + SOUND", panelX + 18, panelY + 31);
  fill(155, 178, 207);
  textSize(13);
  text("θ  " + nf(theta, 1, 3) + " rad", panelX + 18, panelY + 68);
  text("φ  " + nf(phi, 1, 3) + " rad", panelX + 18, panelY + 92);
  text("x  " + signed(blochX), panelX + 18, panelY + 132);
  text("y  " + signed(blochY), panelX + 18, panelY + 156);
  text("z  " + signed(blochZ), panelX + 18, panelY + 180);
  drawBar(panelX + 18, panelY + 211, 174, p0, "|0〉", color(91, 151, 246));
  drawBar(panelX + 18, panelY + 256, 174, p1, "|1〉", color(242, 132, 54));
  fill(155, 178, 207);
  textSize(11);
  fill(242, 194, 28);
  text("ONE PULSE  " + nf(thetaFrequency(), 1, 1) + " Hz", panelX + 18, panelY + 294);
  fill(155, 178, 207);
  text(
    "DUTY  " + nf(phiDutyCycle() * 100.0, 1, 1) + "%  from φ",
    panelX + 18, panelY + 313
  );
  text("θ pitch · φ width  3–97%", panelX + 18, panelY + 332);
  endFlat();
}

void drawConnectionStatus() {
  beginFlat();
  boolean recentOsc = millis() - lastOscMillis < 3000;
  fill(recentOsc ? color(74, 220, 142) : color(242, 194, 28));
  textSize(13);
  text(
    recentOsc ? "LIVE: Python moved the arrow on UDP 7497"
      : "LOCAL MODE: OSC input is optional",
    742, 518
  );
  fill(155, 178, 207);
  textSize(11);
  text("Direct sound never needs Python or Max.", 742, 538);
  text("red X · blue Y · green vertical Z", 742, 553);
  endFlat();
}

void drawAudioControl() {
  beginFlat();
  boolean hovered = hit(
    mouseX, mouseY,
    playButtonX, playButtonY, playButtonWidth, playButtonHeight
  );
  noStroke();
  fill(!soundReady ? color(92, 104, 120)
    : hovered ? color(242, 194, 28)
    : color(242, 132, 54));
  rect(playButtonX, playButtonY, playButtonWidth, playButtonHeight, 8);
  fill(8, 12, 20);
  textAlign(CENTER, CENTER);
  textSize(13);
  text(
    liveSound ? "LIVE SOUND: ON" : "PLAY SELECTED STATE",
    playButtonX + playButtonWidth / 2,
    playButtonY + playButtonHeight / 2
  );
  textAlign(LEFT, BASELINE);

  fill(soundReady ? color(74, 220, 142) : color(242, 132, 54));
  textSize(11);
  text(audioStatus, 620, 625);
  fill(245);
  text("Terminal fallback:", 620, 646);
  fill(155, 178, 207);
  text("python 02_bloch_sphere.py --axis ry", 620, 666);
  text("--theta " + nf(theta, 1, 6) + " --phi " + nf(phi, 1, 6), 620, 686);
  endFlat();
}

void drawBar(
  float x, float y, float w, float value, String label, int barColor
) {
  fill(245);
  textSize(11);
  text(label, x, y);
  fill(8, 12, 20);
  noStroke();
  rect(x, y + 5, w, 16, 4);
  fill(barColor);
  rect(x, y + 5, max(1, w * constrain(value, 0, 1)), 16, 4);
  fill(245);
  textAlign(RIGHT, BASELINE);
  text(round(value * 100) + "%", x + w - 4, y + 18);
  textAlign(LEFT, BASELINE);
}

void drawButton(float x, float y, float w, float h, String label) {
  boolean hovered = hit(mouseX, mouseY, x, y, w, h);
  noStroke();
  fill(hovered ? color(242, 194, 28) : color(28, 40, 57));
  rect(x, y, w, h, 7);
  fill(hovered ? color(8, 12, 20) : color(222));
  textAlign(CENTER, CENTER);
  textSize(13);
  text(label, x + w / 2, y + h / 2);
  textAlign(LEFT, BASELINE);
}

boolean hit(float mx, float my, float x, float y, float w, float h) {
  return mx >= x && mx <= x + w && my >= y && my <= y + h;
}

void beginFlat() {
  hint(DISABLE_DEPTH_TEST);
  camera();
}

void endFlat() {
  hint(ENABLE_DEPTH_TEST);
}

void mouseClicked() {
  if (hit(
    mouseX, mouseY,
    playButtonX, playButtonY, playButtonWidth, playButtonHeight
  )) {
    playSelectedState();
    return;
  }
  if (hit(mouseX, mouseY, 34, 132, 152, 40)) {
    setState(0, 0);
    if (liveSound) triggerStateSound();
    return;
  }
  for (int i = 0; i < buttonLabels.length; i++) {
    float x = buttonLeft + i * (buttonWidth + buttonGap);
    if (!hit(mouseX, mouseY, x, buttonTop, buttonWidth, buttonHeight)) continue;
    activateButton(i);
    if (liveSound) triggerStateSound();
    return;
  }
}

void mouseDragged() {
  if (mouseY < 140 || mouseX > 720) return;
  theta = constrain(theta + (mouseY - pmouseY) * 0.012, 0, PI);
  phi = wrapAngle(phi + (mouseX - pmouseX) * 0.012);
  updateVectorFromAngles();
  if (liveSound && millis() - lastSoundMillis > 90) triggerStateSound();
}

void keyPressed() {
  if (key == '0') setState(0, 0);
  else if (key == '1') setState(PI, 0);
  else if (key == 'h' || key == 'H') applyH();
  else if (key == 'x' || key == 'X') applyX();
  else if (key == 'y' || key == 'Y') applyY();
  else if (key == 'z' || key == 'Z') applyZ();
  else if (key == 'p' || key == 'P') {
    playSelectedState();
    return;
  } else if (keyCode == UP) rotateYGate(-PI / 18.0);
  else if (keyCode == DOWN) rotateYGate(PI / 18.0);
  else if (keyCode == LEFT) phi = wrapAngle(phi - PI / 18.0);
  else if (keyCode == RIGHT) phi = wrapAngle(phi + PI / 18.0);
  updateVectorFromAngles();
  if (liveSound) triggerStateSound();
}

void activateButton(int index) {
  if (index == 0) applyH();
  else if (index == 1) applyX();
  else if (index == 2) applyY();
  else if (index == 3) applyZ();
  else if (index == 4) rotateXGate(-PI / 12.0);
  else if (index == 5) rotateXGate(PI / 12.0);
  else if (index == 6) rotateYGate(-PI / 12.0);
  else if (index == 7) rotateYGate(PI / 12.0);
  else if (index == 8) rotateZGate(-PI / 12.0);
  else if (index == 9) rotateZGate(PI / 12.0);
}

void initializeSound() {
  try {
    stateOscillator = new Pulse(this);
    stateFilter = new LowPass(this);
    stateEnvelope = new Env(this);
    soundReady = true;
    audioStatus = "Sound ready. θ = pitch · φ = pulse width.";
  } catch (Throwable error) {
    soundReady = false;
    audioStatus = "Audio unavailable: install Sound/check output.";
  }
}

void playSelectedState() {
  if (!soundReady) {
    audioStatus = "No direct audio. Use the Python command below.";
    return;
  }
  liveSound = !liveSound;
  if (liveSound) {
    triggerStateSound();
  } else {
    audioStatus = "Live sound off. Click PLAY to resume.";
  }
}

void triggerStateSound() {
  if (!soundReady) return;
  try {
    float frequency = thetaFrequency();
    float dutyCycle = phiDutyCycle();
    float cutoff = 5000.0;
    stateOscillator.width(dutyCycle);
    stateOscillator.play(frequency, 1.0);
    if (!filterConnected) {
      stateFilter.process(stateOscillator, cutoff);
      filterConnected = true;
    } else {
      stateFilter.freq(cutoff);
    }
    stateEnvelope.play(stateOscillator, 0.008, 0.24, 0.16, 0.30);
    lastSoundMillis = millis();
    audioStatus = "ONE PULSE: " + nf(frequency, 1, 1)
      + " Hz · duty " + nf(dutyCycle * 100.0, 1, 1) + "%.";
  } catch (Throwable error) {
    soundReady = false;
    liveSound = false;
    audioStatus = "Audio device failed. Use the Python command below.";
  }
}

float thetaFrequency() {
  // Direct frequency interpolation: north/equator/south = 220/330/440 Hz.
  return 220.0 + 220.0 * (theta / PI);
}

float phiDutyCycle() {
  // Azimuth is undefined at a pole, so use a neutral square wave there.
  if (abs(sin(theta)) < 0.001) return 0.5;
  // phi is wrapped to (-PI, PI]: -PI/0/PI maps to 3/50/97 percent.
  return map(phi, -PI, PI, 0.03, 0.97);
}

void setState(float nextTheta, float nextPhi) {
  theta = constrain(nextTheta, 0, PI);
  phi = wrapAngle(nextPhi);
  updateVectorFromAngles();
}

void rotateYGate(float angle) {
  setVector(
    blochX * cos(angle) + blochZ * sin(angle),
    blochY,
    -blochX * sin(angle) + blochZ * cos(angle)
  );
}

void rotateXGate(float angle) {
  setVector(
    blochX,
    blochY * cos(angle) - blochZ * sin(angle),
    blochY * sin(angle) + blochZ * cos(angle)
  );
}

void rotateZGate(float angle) {
  setVector(
    blochX * cos(angle) - blochY * sin(angle),
    blochX * sin(angle) + blochY * cos(angle),
    blochZ
  );
}

void applyH() {
  setVector(blochZ, -blochY, blochX);
}

void applyX() {
  setVector(blochX, -blochY, -blochZ);
}

void applyY() {
  setVector(-blochX, blochY, -blochZ);
}

void applyZ() {
  setVector(-blochX, -blochY, blochZ);
}

void updateVectorFromAngles() {
  blochX = sin(theta) * cos(phi);
  blochY = sin(theta) * sin(phi);
  blochZ = cos(theta);
}

void setVector(float x, float y, float z) {
  float length = sqrt(x * x + y * y + z * z);
  if (length < 0.00001) return;
  blochX = x / length;
  blochY = y / length;
  blochZ = z / length;
  theta = acos(constrain(blochZ, -1, 1));
  phi = wrapAngle(atan2(blochY, blochX));
}

float wrapAngle(float angle) {
  while (angle > PI) angle -= TWO_PI;
  while (angle <= -PI) angle += TWO_PI;
  return angle;
}

String signed(float value) {
  if (abs(value) < 0.005) value = 0;
  return (value >= 0 ? "+" : "") + nf(value, 1, 2);
}

void listenForOsc() {
  byte[] buffer = new byte[2048];
  try {
    oscSocket = new DatagramSocket(oscPort);
    oscSocket.setSoTimeout(250);
    while (keepListening) {
      try {
        DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
        oscSocket.receive(packet);
        parseBlochOsc(packet.getData(), packet.getLength());
      } catch (SocketTimeoutException timeout) {
        // Local controls and direct sound are the intentional default.
      }
    }
  } catch (Exception error) {
    // OSC is optional; the sketch remains fully usable in local mode.
  } finally {
    if (oscSocket != null) oscSocket.close();
  }
}

void parseBlochOsc(byte[] data, int length) {
  try {
    ByteBuffer bytes = ByteBuffer.wrap(data, 0, length).order(ByteOrder.BIG_ENDIAN);
    String address = readOscString(bytes);
    String tags = readOscString(bytes);
    if (!address.equals("/qmw/circuit/q0/bloch") || !tags.equals(",fff")) return;
    setVector(bytes.getFloat(), bytes.getFloat(), bytes.getFloat());
    lastOscMillis = millis();
  } catch (Exception ignored) {
    // Malformed or unrelated packets never disable the local activity.
  }
}

String readOscString(ByteBuffer bytes) {
  StringBuilder value = new StringBuilder();
  while (bytes.hasRemaining()) {
    byte next = bytes.get();
    if (next == 0) break;
    value.append((char)(next & 0xff));
  }
  while (bytes.position() % 4 != 0 && bytes.hasRemaining()) bytes.get();
  return value.toString();
}

void exit() {
  keepListening = false;
  if (oscSocket != null) oscSocket.close();
  if (stateOscillator != null) stateOscillator.stop();
  super.exit();
}
