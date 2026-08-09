import oscP5.*;
import netP5.*;

/* Temporal 3D wavefunction cloud driven by the same OSC grains as audio. */

OscP5 oscP5;
ArrayList<CloudGrain> grains = new ArrayList<CloudGrain>();

int frameId = -1;
float physicsTime = 0;
float norm = 0;
float centerX, centerY, centerZ;
float spreadX, spreadY, spreadZ;
float rotX = -0.55;
float rotY = 0.72;
float zoom = 1.0;
final float VISUAL_LIFE_MS = 450.0;

class CloudGrain {
  PVector position;
  PVector current;
  float amplitude;
  float phase;
  float energy;
  float audioDecayMs;
  int born;

  CloudGrain(float x, float y, float z, float amp, float ph,
             float jx, float jy, float jz, float e, float decay) {
    position = new PVector(x, y, z);
    current = new PVector(jx, jy, jz);
    amplitude = amp;
    phase = ph;
    energy = e;
    audioDecayMs = decay;
    born = millis();
  }

  float ageMs() { return millis() - born; }
  boolean alive() { return ageMs() < VISUAL_LIFE_MS; }
}

void setup() {
  size(1280, 820, P3D);
  colorMode(HSB, 1.0);
  smooth(8);
  frameRate(60);
  textFont(createFont("Menlo", 13));
  oscP5 = new OscP5(this, 7401);
}

void draw() {
  background(0);
  for (int i = grains.size() - 1; i >= 0; i--) {
    if (!grains.get(i).alive()) grains.remove(i);
  }
  drawHeader();
  drawCloud();
}

void drawHeader() {
  hint(DISABLE_DEPTH_TEST);
  camera();
  fill(1);
  text("QMW TEMPORAL WAVEFUNCTION CLOUD", 28, 32);
  fill(0, 0, 0.67);
  text("|psi|² = size/opacity  phase = hue  current = motion  energy = brightness", 28, 54);
  text("Every sonic grain decays in 5 ms; the longer visual trail reveals trajectory.", 28, 76);
  fill(1);
  text("frame " + frameId + "   t " + nf(physicsTime, 1, 3) +
       "   norm " + nf(norm, 1, 9) + "   visible grains " + grains.size(), 28, 104);
  hint(ENABLE_DEPTH_TEST);
}

void drawCloud() {
  pushMatrix();
  translate(width * 0.53, height * 0.55, 0);
  scale(zoom);
  rotateX(rotX);
  rotateY(rotY);
  drawBox();

  for (CloudGrain grain : grains) {
    float age = grain.ageMs() / VISUAL_LIFE_MS;
    float alpha = constrain((1.0 - age) * (0.15 + grain.amplitude), 0, 1);
    PVector p = grain.position.copy().mult(285);
    PVector drift = grain.current.copy().mult(age * 95);
    p.add(drift);
    float hue = (grain.phase + 1.0) * 0.5;
    float brightness = constrain(0.3 + 0.7 * grain.energy, 0, 1);

    stroke(hue, 0.5, brightness, alpha * 0.35);
    strokeWeight(1);
    PVector start = grain.position.copy().mult(285);
    line(start.x, start.y, start.z, p.x, p.y, p.z);

    noStroke();
    fill(hue, 0.82, brightness, alpha);
    pushMatrix();
    translate(p.x, p.y, p.z);
    sphereDetail(5);
    sphere(2.0 + grain.amplitude * 10.0);
    popMatrix();
  }

  drawMomentEllipsoid();
  popMatrix();
}

void drawBox() {
  noFill();
  stroke(0, 0, 0.22);
  strokeWeight(1);
  box(570);
  stroke(0, 0, 0.13);
  line(-285, 0, 0, 285, 0, 0);
  line(0, -285, 0, 0, 285, 0);
  line(0, 0, -285, 0, 0, 285);
}

void drawMomentEllipsoid() {
  pushMatrix();
  // Center/spread arrive in physical coordinates; defaults use extent ±8.
  translate(centerX / 8.0 * 285, centerY / 8.0 * 285, centerZ / 8.0 * 285);
  noFill();
  stroke(0.56, 0.25, 0.8, 0.45);
  strokeWeight(1.5);
  scale(max(0.02, spreadX / 8.0), max(0.02, spreadY / 8.0), max(0.02, spreadZ / 8.0));
  sphere(285);
  popMatrix();
}

void oscEvent(OscMessage message) {
  String address = message.addrPattern();
  if (address.equals("/qmw/wavefunction/cloud/frame")) {
    frameId = message.get(0).intValue();
    physicsTime = message.get(1).floatValue();
    norm = message.get(3).floatValue();
    centerX = message.get(4).floatValue();
    centerY = message.get(5).floatValue();
    centerZ = message.get(6).floatValue();
    spreadX = message.get(7).floatValue();
    spreadY = message.get(8).floatValue();
    spreadZ = message.get(9).floatValue();
  } else if (address.equals("/qmw/wavefunction/cloud/grain")) {
    grains.add(new CloudGrain(
      message.get(2).floatValue(), message.get(3).floatValue(), message.get(4).floatValue(),
      message.get(5).floatValue(), message.get(6).floatValue(),
      message.get(7).floatValue(), message.get(8).floatValue(), message.get(9).floatValue(),
      message.get(10).floatValue(), message.get(11).floatValue()
    ));
  }
}

void mouseDragged() {
  rotY += (mouseX - pmouseX) * 0.01;
  rotX += (mouseY - pmouseY) * 0.01;
}

void keyPressed() {
  if (key == '+') zoom *= 1.08;
  if (key == '-') zoom /= 1.08;
}
