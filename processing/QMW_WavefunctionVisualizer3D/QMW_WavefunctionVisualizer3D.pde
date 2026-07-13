import oscP5.*;
import netP5.*;

OscP5 oscP5;

int N = 256;
int HISTORY = 120;

float[][] probabilityHistory = new float[HISTORY][N];
float[][] phaseHistory = new float[HISTORY][N];

int writeIndex = 0;
boolean hasData = false;

float rotX = -0.75;
float rotY = 0.65;
float zoom = 1.0;
float heightScale = 260.0;

void setup() {
  size(1200, 800, P3D);
  colorMode(HSB, 1.0);
  frameRate(60);
  oscP5 = new OscP5(this, 7401);
  textFont(createFont("Menlo", 12));
}

void draw() {
  background(0);

  lights();

  drawTitle();
  drawWaveSurface();
  drawLegend();
}

void drawTitle() {
  fill(1);
  text("QMW Schrödinger Wavefunction Visualizer 3D", 30, 30);
  text("|ψ(x,t)|² = height, arg(ψ) = hue", 30, 50);
  text("Listening on UDP 7401", 30, 70);
}

void drawWaveSurface() {
  pushMatrix();

  translate(width * 0.56, height * 0.54, 0);
  scale(zoom);
  rotateX(rotX);
  rotateY(rotY);

  float xScale = 4.0;
  float zScale = 5.0;

  strokeWeight(1);
  noFill();

  for (int h = 0; h < HISTORY - 1; h++) {
    int rowA = historyIndex(h);
    int rowB = historyIndex(h + 1);

    beginShape(TRIANGLE_STRIP);

    for (int i = 0; i < N; i += 2) {
      vertexFor(rowA, h, i, xScale, zScale);
      vertexFor(rowB, h + 1, i, xScale, zScale);
    }

    endShape();
  }

  drawAxes(xScale, zScale);

  popMatrix();
}

void vertexFor(int row, int h, int i, float xScale, float zScale) {
  float p = probabilityHistory[row][i];
  float ph = phaseHistory[row][i];

  float x = (i - N / 2.0) * xScale;
  float y = -p * heightScale;
  float z = (h - HISTORY / 2.0) * zScale;

  float hue = map(ph, -PI, PI, 0.0, 1.0);
  float bright = constrain(0.25 + p * 8.0, 0.0, 1.0);

  stroke(hue, 0.9, bright, 0.85);
  fill(hue, 0.85, bright, 0.35);

  vertex(x, y, z);
}

void drawAxes(float xScale, float zScale) {
  stroke(0, 0, 0.45);
  strokeWeight(1);

  float xMin = -N / 2.0 * xScale;
  float xMax = N / 2.0 * xScale;
  float zMin = -HISTORY / 2.0 * zScale;
  float zMax = HISTORY / 2.0 * zScale;

  line(xMin, 0, zMin, xMax, 0, zMin);
  line(xMin, 0, zMax, xMax, 0, zMax);
  line(xMin, 0, zMin, xMin, 0, zMax);
  line(xMax, 0, zMin, xMax, 0, zMax);

  for (int i = -4; i <= 4; i++) {
    float x = map(i, -4, 4, xMin, xMax);
    line(x, 0, zMin, x, 0, zMax);
  }

  for (int j = -4; j <= 4; j++) {
    float z = map(j, -4, 4, zMin, zMax);
    line(xMin, 0, z, xMax, 0, z);
  }
}

void drawLegend() {
  fill(1);
  text("Source: schrodinger_packet", 30, height - 90);
  text("Grid points: " + N, 30, height - 70);
  text("History frames: " + HISTORY, 30, height - 50);
  text("Mouse drag = rotate, +/- = zoom, [ ] = height scale", 30, height - 30);

  if (!hasData) {
    fill(0.08, 1.0, 1.0);
    text("Waiting for /qmw/source/wavepacket/probability and /phase", 30, 105);
  }
}

int historyIndex(int offset) {
  return (writeIndex + offset) % HISTORY;
}

void oscEvent(OscMessage msg) {
  String addr = msg.addrPattern();

  if (addr.equals("/qmw/source/wavepacket/probability")) {
    for (int i = 0; i < min(N, msg.arguments().length); i++) {
      probabilityHistory[writeIndex][i] = msg.get(i).floatValue();
    }
    hasData = true;
  }

  else if (addr.equals("/qmw/source/wavepacket/phase")) {
    for (int i = 0; i < min(N, msg.arguments().length); i++) {
      phaseHistory[writeIndex][i] = msg.get(i).floatValue();
    }

    writeIndex = (writeIndex + 1) % HISTORY;
    hasData = true;
  }
}

void mouseDragged() {
  rotY += (mouseX - pmouseX) * 0.01;
  rotX += (mouseY - pmouseY) * 0.01;
}

void keyPressed() {
  if (key == '+') zoom *= 1.08;
  if (key == '-') zoom /= 1.08;
  if (key == ']') heightScale *= 1.10;
  if (key == '[') heightScale /= 1.10;
}
