/**
 * QMW I Ching Network Visualizer V1
 * Processing 4 + oscP5, UDP 7404.
 *
 * A read-only, atomic mirror of /qmw/iching/network revisions.
 * Drag to rotate, mouse wheel to zoom, R to reset, D for demo, H for help.
 */
import oscP5.*;
import processing.event.MouseEvent;

final int OSC_PORT = 7404;
final String ROOT = "/qmw/iching/network";
final int NODES = 64, EDGES = 192, DENSITY = 16;

OscP5 osc;
NetworkFrame active = new NetworkFrame();
NetworkFrame candidate = null;
float rotationX = -0.36, rotationY = 0.62, zoom = 1.0;
float dragX, dragY;
boolean dragging = false, showHelp = true;
long lastCommitMillis = 0;

class EdgeDatum {
  int source, target, line;
  float weight, phase;
  EdgeDatum(int s, int t, int l, float w, float p) {
    source=s; target=t; line=l; weight=w; phase=p;
  }
}

class NetworkFrame {
  int revision=-1, seed=0, primary=0, movingMask=0, transformed=0, changeRegister=0;
  String pauli="----";
  float pauliExpectation=0, mutualInformation=0, changeEntropy=0, purity=1;
  float primaryPhase=0, primaryStrength=0;
  float[] lineProbability = new float[6];
  float[] lineCoherence = new float[6];
  float[] linePhase = new float[6];
  float[] flux = new float[15];
  float[] fluxStrength = new float[15];
  ArrayList<EdgeDatum> edges = new ArrayList<EdgeDatum>();
  float[][] densityReal = new float[DENSITY][DENSITY];
  float[][] densityImag = new float[DENSITY][DENSITY];
  boolean hasReading=false, hasMetrics=false, hasPauli=false, hasPrimaryPhase=false;
  boolean[] realRows = new boolean[DENSITY], imagRows = new boolean[DENSITY];
  boolean[] lineSeen = new boolean[6];
  int lineCount=0, fluxCount=0;

  boolean complete() {
    int realCount=0, imagCount=0;
    for (int i=0; i<DENSITY; i++) { if (realRows[i]) realCount++; if (imagRows[i]) imagCount++; }
    return hasReading && hasMetrics && hasPauli && hasPrimaryPhase && lineCount==6 &&
           edges.size()==EDGES && fluxCount==15 && realCount==16 && imagCount==16;
  }
}

void settings() { size(1440, 900, P3D); smooth(8); }

void setup() {
  colorMode(HSB, 1.0); textFont(createFont("Menlo", 13));
  osc = new OscP5(this, OSC_PORT);
  loadDemo();
  surface.setTitle("QMW I Ching Phase Network — UDP " + OSC_PORT);
}

void draw() {
  background(0.67, 0.22, 0.055);
  drawGraph();
  hint(DISABLE_DEPTH_TEST);
  camera();
  drawDensityPanel();
  drawHUD();
  hint(ENABLE_DEPTH_TEST);
}

PVector nodePosition(int node) {
  float ux = (((node >> 3) & 1) == 1 ? 1 : -1) * 215;
  float uy = (((node >> 4) & 1) == 1 ? 1 : -1) * 215;
  float uz = (((node >> 5) & 1) == 1 ? 1 : -1) * 215;
  float lx = (((node >> 0) & 1) == 1 ? 1 : -1) * 48;
  float ly = (((node >> 1) & 1) == 1 ? 1 : -1) * 48;
  float lz = (((node >> 2) & 1) == 1 ? 1 : -1) * 48;
  return new PVector(ux+lx, uy+ly, uz+lz);
}

float phaseHue(float phase) { return ((phase + PI) / TWO_PI + 1.0) % 1.0; }

boolean pathNode(int node) {
  int current=active.primary;
  if (node==current) return true;
  for (int q=0; q<6; q++) {
    if ((active.movingMask & (1<<q)) != 0) { current ^= 1<<q; if (node==current) return true; }
  }
  return false;
}

void drawGraph() {
  pushMatrix();
  translate(width*0.39, height*0.52, 0);
  scale(zoom); rotateX(rotationX); rotateY(rotationY);
  float maxWeight=1e-9;
  for (EdgeDatum e : active.edges) maxWeight=max(maxWeight, e.weight);

  for (EdgeDatum e : active.edges) {
    PVector a=nodePosition(e.source), b=nodePosition(e.target);
    float normalized=sqrt(constrain(e.weight/maxWeight, 0, 1));
    boolean moving=(active.movingMask & (1<<(e.line-1))) != 0;
    stroke(phaseHue(e.phase), moving ? 0.92 : 0.55, moving ? 0.95 : 0.35,
           moving ? 0.68+0.26*sin(frameCount*0.06+e.phase) : 0.34);
    strokeWeight(moving ? 1.4+3.8*normalized : 0.45+1.7*normalized);
    line(a.x,a.y,a.z,b.x,b.y,b.z);
  }

  noStroke();
  for (int node=0; node<NODES; node++) {
    PVector p=nodePosition(node);
    float population=max(0, active.densityReal[visibleIndex(node)][visibleIndex(node)]);
    float radius=3.5+22*sqrt(population);
    if (node==active.primary) fill(0.12,0.90,1.0);
    else if (node==active.transformed) fill(0.52,0.90,1.0);
    else if (pathNode(node)) fill(phaseHue(active.primaryPhase),0.75,0.92);
    else fill(0.58,0.35,0.54);
    pushMatrix(); translate(p.x,p.y,p.z);
    if (node==active.transformed) radius += 3+2*sin(frameCount*0.09);
    sphereDetail(7); sphere(radius); popMatrix();
  }
  popMatrix();
}

int visibleIndex(int hexagram) {
  int[] q={0,2,3,5}; int result=0;
  for (int i=0; i<4; i++) result |= ((hexagram>>q[i])&1)<<i;
  return result;
}

void drawDensityPanel() {
  float x0=width-390, y0=170, cell=20;
  fill(0,0,0.10,0.88); noStroke(); rect(x0-20,y0-42,360,390,10);
  fill(0,0,0.92); textSize(15); text("4-QUBIT DENSITY — MAGNITUDE / PHASE",x0,y0-17);
  for (int row=0; row<DENSITY; row++) for (int col=0; col<DENSITY; col++) {
    float re=active.densityReal[row][col], im=active.densityImag[row][col];
    float magnitude=sqrt(re*re+im*im), phase=atan2(im,re);
    fill(phaseHue(phase), magnitude>1e-7 ? 0.78 : 0, constrain(0.10+3.2*sqrt(magnitude),0,1));
    rect(x0+col*cell,y0+row*cell,cell-1,cell-1);
  }
  fill(0,0,0.62); textSize(11); text("phase hue  −π",x0,y0+342); text("+π",x0+300,y0+342);
  for (int i=0; i<300; i++) { stroke(i/300.0,0.8,0.8); line(x0+i,y0+350,x0+i,y0+358); }
}

void drawHUD() {
  fill(0,0,0.92); textSize(18); text("QMW I CHING — PHASE NETWORK",28,34);
  textSize(13); fill(0,0,0.74);
  text("revision " + active.revision + "   seed " + unsignedSeed(active.seed) +
       "   OSC " + OSC_PORT + "   " + (millis()-lastCommitMillis<1600 ? "● COMMIT" : "○ listening"),28,58);
  fill(0,0,0.90); textSize(14);
  text("H₀ " + active.primary + "   M " + active.movingMask + "   H₁ " + active.transformed +
       "   change " + active.changeRegister,28,84);
  text("Pauli " + active.pauli + "  <P> " + nf(active.pauliExpectation,1,4) +
       "   I(L:U) " + nf(active.mutualInformation,1,4) + " bits",28,107);
  text("path phase " + nf(active.primaryPhase,1,4) + " rad   purity " + nf(active.purity,1,4),28,130);

  float y=height-92;
  for (int line=0; line<6; line++) {
    boolean moving=(active.movingMask&(1<<line))!=0;
    fill(phaseHue(active.linePhase[line]),0.80,moving?1.0:0.58);
    rect(28+line*116,y,104,7);
    fill(0,0,moving?0.95:0.60); textSize(11);
    text("L"+(line+1)+" p="+nf(active.lineProbability[line],1,2)+" φ="+nf(active.linePhase[line],1,2),28+line*116,y+23);
  }
  if (showHelp) {
    fill(0,0,0.08,0.84); noStroke(); rect(width-390,590,360,180,10);
    fill(0,0,0.88); textSize(12);
    text("DRAG  rotate\nWHEEL  zoom\nR  reset view\nD  deterministic demo\nH  hide help\n\nAtomic scene swaps only after matching /end.",width-370,620);
  }
}

String unsignedSeed(int value) { return String.valueOf(((long)value) & 0xffffffffL); }

void oscEvent(OscMessage m) {
  String address=m.addrPattern();
  if (!address.startsWith(ROOT)) return;
  String route=address.substring(ROOT.length());
  try {
    if (route.equals("/begin")) {
      candidate=new NetworkFrame(); candidate.revision=m.get(0).intValue(); candidate.seed=m.get(1).intValue(); return;
    }
    if (candidate==null || m.get(0).intValue()!=candidate.revision) return;
    if (route.equals("/reading")) {
      candidate.primary=m.get(1).intValue(); candidate.movingMask=m.get(2).intValue();
      candidate.transformed=m.get(3).intValue(); candidate.changeRegister=m.get(4).intValue(); candidate.hasReading=true;
    } else if (route.equals("/metrics")) {
      candidate.mutualInformation=m.get(1).floatValue(); candidate.changeEntropy=m.get(2).floatValue();
      candidate.purity=m.get(3).floatValue(); candidate.hasMetrics=true;
    } else if (route.equals("/primary_phase")) {
      candidate.primaryPhase=m.get(1).floatValue(); candidate.primaryStrength=m.get(2).floatValue(); candidate.hasPrimaryPhase=true;
    } else if (route.equals("/pauli")) {
      candidate.pauli=m.get(1).stringValue(); candidate.pauliExpectation=m.get(2).floatValue(); candidate.hasPauli=true;
    } else if (route.equals("/line_phase")) {
      int line=m.get(1).intValue()-1;
      if (line>=0 && line<6) { if (!candidate.lineSeen[line]) { candidate.lineSeen[line]=true; candidate.lineCount++; }
        candidate.lineProbability[line]=m.get(2).floatValue(); candidate.lineCoherence[line]=m.get(3).floatValue(); candidate.linePhase[line]=m.get(4).floatValue(); }
    } else if (route.equals("/edge")) {
      candidate.edges.add(new EdgeDatum(m.get(1).intValue(),m.get(2).intValue(),m.get(3).intValue(),m.get(4).floatValue(),m.get(5).floatValue()));
    } else if (route.equals("/flux")) {
      if (candidate.fluxCount<15) { candidate.flux[candidate.fluxCount]=m.get(3).floatValue(); candidate.fluxStrength[candidate.fluxCount]=m.get(4).floatValue(); candidate.fluxCount++; }
    } else if (route.equals("/density/real_row") || route.equals("/density/imag_row")) {
      int row=m.get(1).intValue(); if (row<0 || row>=16) return;
      boolean real=route.equals("/density/real_row");
      for (int col=0; col<16; col++) { if (real) candidate.densityReal[row][col]=m.get(col+2).floatValue(); else candidate.densityImag[row][col]=m.get(col+2).floatValue(); }
      if (real) candidate.realRows[row]=true; else candidate.imagRows[row]=true;
    } else if (route.equals("/end")) {
      if (candidate.complete()) { active=candidate; lastCommitMillis=millis(); }
      candidate=null;
    }
  } catch (Exception ignored) { candidate=null; }
}

void loadDemo() {
  NetworkFrame d=new NetworkFrame(); d.revision=0; d.seed=42; d.primary=15; d.movingMask=4; d.transformed=11; d.changeRegister=3;
  d.pauli="ZYZZ"; d.pauliExpectation=-0.4167; d.mutualInformation=0.5369; d.changeEntropy=0.7789; d.purity=0.7196; d.primaryPhase=-1.6145;
  for (int i=0;i<6;i++) { d.lineProbability[i]=0.12+0.11*i; d.lineCoherence[i]=0.15+0.08*i; d.linePhase[i]=-PI+i*TWO_PI/6.0; }
  for (int node=0;node<64;node++) for (int q=0;q<6;q++) { int target=node^(1<<q); if (node<target) d.edges.add(new EdgeDatum(node,target,q+1,0.01+0.01*q,d.linePhase[q])); }
  for (int i=0;i<16;i++) { d.densityReal[i][i]=(i==15?0.32:0.68/15.0); if(i<15){d.densityReal[i][i+1]=0.018;d.densityReal[i+1][i]=0.018;} }
  active=d; lastCommitMillis=millis();
}

void mousePressed(){dragging=true;dragX=mouseX;dragY=mouseY;}
void mouseReleased(){dragging=false;}
void mouseDragged(){if(dragging){rotationY+=(mouseX-dragX)*0.008;rotationX+=(mouseY-dragY)*0.008;dragX=mouseX;dragY=mouseY;}}
void mouseWheel(MouseEvent event){zoom=constrain(zoom-event.getCount()*0.06,0.45,1.8);}
void keyPressed(){if(key=='r'||key=='R'){rotationX=-0.36;rotationY=0.62;zoom=1;}else if(key=='d'||key=='D')loadDemo();else if(key=='h'||key=='H')showHelp=!showHelp;}
