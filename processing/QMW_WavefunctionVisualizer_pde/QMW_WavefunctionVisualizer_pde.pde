import oscP5.*;
import netP5.*;

OscP5 oscP5;

int N = 256;
float[] probability = new float[N];
float[] phase = new float[N];

void setup() {
  size(1200, 700, P3D);
  colorMode(HSB, 1.0);
  frameRate(60);
  oscP5 = new OscP5(this, 7401);
  textFont(createFont("Menlo", 12));
}

void draw() {
  background(0);

  drawWavefunction();
  drawInfo();
}

void drawWavefunction() {
  pushMatrix();
  translate(80, height * 0.55);

  float w = width - 160;
  float dx = w / float(N - 1);

  noFill();
  strokeWeight(2);

  beginShape();
  for (int i = 0; i < N; i++) {
    float x = i * dx;
    float y = -probability[i] * 360.0;
    float hue = map(phase[i], -PI, PI, 0, 1);

    stroke(hue, 0.9, 1.0);
    vertex(x, y);
  }
  endShape();

  for (int i = 0; i < N; i += 4) {
    float x = i * dx;
    float y = -probability[i] * 360.0;
    float hue = map(phase[i], -PI, PI, 0, 1);

    stroke(hue, 0.8, 0.8, 0.4);
    line(x, 0, x, y);

    noStroke();
    fill(hue, 0.9, 1.0);
    ellipse(x, y, 4, 4);
  }

  stroke(0, 0, 0.4);
  line(0, 0, w, 0);

  popMatrix();
}

void drawInfo() {
  fill(1);
  text("QMW Schrödinger Wavefunction Visualizer", 40, 35);
  text("|ψ(x)|² = height, phase arg(ψ) = hue", 40, 55);
  text("Listening on UDP 7401", 40, 75);
}

void oscEvent(OscMessage msg) {
  String addr = msg.addrPattern();

  if (addr.equals("/qmw/source/wavepacket/probability")) {
    for (int i = 0; i < min(N, msg.arguments().length); i++) {
      probability[i] = msg.get(i).floatValue();
    }
  }

  else if (addr.equals("/qmw/source/wavepacket/phase")) {
    for (int i = 0; i < min(N, msg.arguments().length); i++) {
      phase[i] = msg.get(i).floatValue();
    }
  }
}
