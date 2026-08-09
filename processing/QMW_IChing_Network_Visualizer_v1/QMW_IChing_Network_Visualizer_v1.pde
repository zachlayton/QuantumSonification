/**
 * QMW I Ching Network Visualizer V1
 * Processing 4 + oscP5, UDP 7404.
 *
 * A read-only, atomic mirror of /qmw/iching/network revisions.
 * Drag to pan, mouse wheel to zoom, space to pause phase, E for edges.
 */
import oscP5.*;
import netP5.*;
import processing.event.MouseEvent;

final int OSC_PORT = 7404;
final int CONTROL_PORT = 7405;
final int IBM_CONTROL_PORT = 7406;
final String ROOT = "/qmw/iching/network";
final String V4_ROOT = "/qmw/iching/v4";
final String CONSULT_ROOT = "/qmw/iching/consult";
final String IBM_ROOT = "/qmw/iching/ibm";
final int NODES = 64, EDGES = 192, DENSITY = 16;
final int[] KING_WEN_BINARY = {
  63,0,17,34,23,58,2,16,55,59,7,56,61,47,4,8,
  25,38,3,48,41,37,32,1,57,39,33,30,18,45,28,14,
  60,15,40,5,53,43,20,10,35,49,31,62,24,6,26,22,
  29,46,9,36,52,11,13,44,54,27,50,19,51,12,21,42
};
final String[] KING_WEN_NAMES = {
  "", "Qian · Creative", "Kun · Receptive", "Zhun · Beginning", "Meng · Youthful Folly",
  "Xu · Waiting", "Song · Conflict", "Shi · Army", "Bi · Holding Together",
  "Xiao Chu · Small Taming", "Lu · Treading", "Tai · Peace", "Pi · Standstill",
  "Tong Ren · Fellowship", "Da You · Great Possession", "Qian · Modesty", "Yu · Enthusiasm",
  "Sui · Following", "Gu · Work on Decay", "Lin · Approach", "Guan · Contemplation",
  "Shi He · Biting Through", "Bi · Grace", "Bo · Splitting Apart", "Fu · Return",
  "Wu Wang · Innocence", "Da Chu · Great Taming", "Yi · Nourishment", "Da Guo · Great Exceeding",
  "Kan · Abysmal Water", "Li · Clinging Fire", "Xian · Influence", "Heng · Duration",
  "Dun · Retreat", "Da Zhuang · Great Power", "Jin · Progress", "Ming Yi · Darkening Light",
  "Jia Ren · Family", "Kui · Opposition", "Jian · Obstruction", "Xie · Deliverance",
  "Sun · Decrease", "Yi · Increase", "Guai · Breakthrough", "Gou · Coming to Meet",
  "Cui · Gathering", "Sheng · Pushing Upward", "Kun · Oppression", "Jing · Well",
  "Ge · Revolution", "Ding · Cauldron", "Zhen · Arousing Thunder", "Gen · Keeping Still",
  "Jian · Development", "Gui Mei · Marrying Maiden", "Feng · Abundance", "Lu · Wanderer",
  "Xun · Gentle Wind", "Dui · Joyous Lake", "Huan · Dispersion", "Jie · Limitation",
  "Zhong Fu · Inner Truth", "Xiao Guo · Small Exceeding", "Ji Ji · After Completion",
  "Wei Ji · Before Completion"
};

OscP5 osc;
NetAddress oracleControl;
NetAddress ibmControl;
int[] kingWenByBinary = new int[64];
NetworkFrame active = new NetworkFrame();
NetworkFrame candidate = null;
GaugeV4Frame gaugeActive = null;
GaugeV4Frame gaugeCandidate = null;
IBMFrame ibmActive = null;
IBMFrame ibmCandidate = null;
float fieldPanX = 0, fieldPanY = 0, zoom = 1.0;
float dragX, dragY;
boolean dragging = false, showHelp = true;
boolean phasePaused = false, showEdges = true;
float frozenPhaseTime = 0;
long lastCommitMillis = 0;
long lastConsultCommitMillis = 0;
long consultRequestedMillis = -10000;
int consultRequestId = 0;
boolean consultAccepted = false, consultPublished = false, consultError = false;
String rejectedFrame = "";
String ibmState = "NOT REQUESTED", ibmBackend = "", ibmJob = "";
long ibmRequestedMillis = -10000;
int ibmRequestRevision = -1;
int ibmRequestSeed = 42, ibmRequestCounter = 0;

class EdgeDatum {
  int source, target, line;
  float weight, phase;
  EdgeDatum(int s, int t, int l, float w, float p) {
    source=s; target=t; line=l; weight=w; phase=p;
  }
}

class PlaquetteDatum {
  int base, lineA, lineB;
  int[] vertices = new int[4];
  float flux, strength;
  PlaquetteDatum(int b, int a, int c, float p, float s) {
    base=b; lineA=a; lineB=c; flux=p; strength=s;
    vertices[0]=base;
    vertices[1]=base^(1<<(lineA-1));
    vertices[2]=vertices[1]^(1<<(lineB-1));
    vertices[3]=base^(1<<(lineB-1));
  }
  boolean contains(int node) {
    for (int vertex:vertices) if (vertex==node) return true;
    return false;
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

class GaugeV4Frame {
  int revision=-1, plaquetteCount=0, pairCount=0, edgeLineTarget=0, spectrumCount=0;
  float time=0;
  float[] population = new float[64];
  float[] moving = new float[6];
  float[] spectrum = new float[8];
  ArrayList<EdgeDatum> edges = new ArrayList<EdgeDatum>();
  ArrayList<PlaquetteDatum> plaquettes = new ArrayList<PlaquetteDatum>();
  int activePlaquettes=0, strongestIndex=0, strongestBase=0, strongestLineA=1, strongestLineB=2;
  int[] strongestVertices = new int[4];
  float meanAbsFlux=0, circularMean=0, circularVariance=0, chirality=0;
  float strongestFlux=0, strongestStrength=0, laplacianTrace=0, minimumEigenvalue=0, hermiticityError=0;
  int[] pairA = new int[15], pairB = new int[15];
  float[] pairMeanAbs = new float[15], pairPhase = new float[15], pairVariance = new float[15];
  float[] pairChirality = new float[15], pairStrength = new float[15];
  boolean hasPopulation=false, hasMoving=false, hasSummary=false, hasSpectrum=false;
  boolean[] edgeLineSeen = new boolean[6], pairSeen = new boolean[15], plaquetteSeen = new boolean[15];
  int edgeLines=0, pairSummaries=0, plaquettePairs=0;

  boolean complete() {
    return hasPopulation && hasMoving && hasSummary && hasSpectrum &&
      edgeLines==edgeLineTarget && edges.size()==EDGES &&
      pairSummaries==pairCount && plaquettePairs==pairCount &&
      plaquettes.size()==plaquetteCount;
  }
}

class IBMFrame {
  int revision=-1, seed=0, shots=0;
  int localPrimary=0, localMask=0, localTransformed=0;
  int externalPrimary=0, externalMask=0, externalTransformed=0;
  String source="", backend="", job="";
  float tvd=0, fidelity=0, movingMae=0;
  float[] localMoving = new float[6], externalMoving = new float[6];
  boolean hasReading=false, hasMetrics=false, hasMoving=false;

  boolean complete() { return hasReading && hasMetrics && hasMoving; }
}

void settings() { size(1440, 900, P3D); smooth(8); }

void setup() {
  colorMode(HSB, 1.0); textFont(createFont("Menlo", 13));
  osc = new OscP5(this, OSC_PORT);
  oracleControl = new NetAddress("127.0.0.1", CONTROL_PORT);
  ibmControl = new NetAddress("127.0.0.1", IBM_CONTROL_PORT);
  for (int number=1;number<=64;number++) kingWenByBinary[KING_WEN_BINARY[number-1]]=number;
  loadDemo();
  surface.setTitle("QMW I Ching Phase Network — UDP " + OSC_PORT);
}

void draw() {
  background(0.67, 0.22, 0.055);
  drawGraph();
  hint(DISABLE_DEPTH_TEST);
  camera();
  drawOraclePanel();
  drawIBMPanel();
  if (gaugeActive!=null) drawGaugePanel(); else drawDensityPanel();
  drawHUD();
  hint(ENABLE_DEPTH_TEST);
}

PVector nodePosition(int node) {
  int lower=node&7, upper=(node>>3)&7;
  return new PVector((lower-3.5)*76, (upper-3.5)*76, 0);
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
  translate(width*0.36+fieldPanX, height*0.51+fieldPanY, 0);
  scale(zoom);
  float maxWeight=1e-9;
  ArrayList<EdgeDatum> fieldEdges = gaugeActive!=null ? gaugeActive.edges : active.edges;
  for (EdgeDatum e : fieldEdges) maxWeight=max(maxWeight, e.weight);
  boolean fieldResolved=gaugeActive==null || maxWeight>0.0005;

  if (showEdges && fieldResolved) for (EdgeDatum e : fieldEdges) {
    PVector a=nodePosition(e.source), b=nodePosition(e.target);
    float normalized=sqrt(constrain(e.weight/maxWeight, 0, 1));
    boolean moving=(active.movingMask & (1<<(e.line-1))) != 0;
    float wave=0.5+0.5*sin(phaseTime()*1.7+e.phase+e.line*0.73);
    float fieldAlpha=gaugeActive!=null ? 0.055+0.19*normalized+0.07*wave : 0.045+0.08*normalized;
    stroke(phaseHue(e.phase), moving ? 0.88 : 0.48, moving ? 0.92 : 0.48,
           moving ? 0.22+0.30*wave : fieldAlpha);
    strokeWeight(moving ? 0.8+1.5*normalized : 0.35+0.45*normalized);
    line(a.x,a.y,b.x,b.y);
    if (moving || (gaugeActive!=null && normalized>0.72)) {
      float t=(phaseTime()*0.13+phaseHue(e.phase))%1.0;
      noStroke(); fill(phaseHue(e.phase),0.55,1.0,0.72);
      ellipse(lerp(a.x,b.x,t),lerp(a.y,b.y,t),3.2,3.2);
    }
  }

  if (strongestLoopVisible()) drawStrongestPlaquette();

  for (int node=0; node<NODES; node++) {
    PVector p=nodePosition(node);
    float population=gaugeActive!=null ? max(0,gaugeActive.population[node]) :
      max(0,active.densityReal[visibleIndex(node)][visibleIndex(node)]);
    drawHexagramGlyph(p.x,p.y,node,nodePhase(node),population);
  }
  popMatrix();
}

boolean strongestLoopVisible() {
  PlaquetteDatum loop=oraclePlaquette();
  float maximum=maxPlaquetteStrength();
  return loop!=null && gaugeActive.activePlaquettes>0 &&
    gaugeActive.laplacianTrace>0.000000001 && maximum>0 &&
    loop.strength>=maximum*0.02 && abs(loop.flux)>0.0000001;
}

float maxPlaquetteStrength() {
  if (gaugeActive==null) return 0;
  float maximum=0;
  for (PlaquetteDatum item:gaugeActive.plaquettes) maximum=max(maximum,item.strength);
  return maximum;
}

String unresolvedLoopReason() {
  PlaquetteDatum loop=oraclePlaquette();
  if (gaugeActive==null || gaugeActive.plaquettes.size()==0) return "awaiting plaquette field";
  if (gaugeActive.laplacianTrace<=0.000000001) return "collapsed field has no coherent edges";
  if (loop==null) return "no plaquette incident on H₀";
  if (abs(loop.flux)<=0.0000001) return "H₀-local loop phase is flat";
  return "H₀-local loop weak relative to this frame";
}

PlaquetteDatum oraclePlaquette() {
  if (gaugeActive==null || gaugeActive.plaquettes.size()==0) return null;
  PlaquetteDatum best=null; float bestScore=-1;
  for (PlaquetteDatum item:gaugeActive.plaquettes) if (item.contains(active.primary)) {
    int movingLines=0;
    if ((active.movingMask&(1<<(item.lineA-1)))!=0) movingLines++;
    if ((active.movingMask&(1<<(item.lineB-1)))!=0) movingLines++;
    float score=item.strength*abs(item.flux)*(1.0+0.28*movingLines);
    if (score>bestScore) { best=item; bestScore=score; }
  }
  return best;
}

float phaseTime() { return phasePaused ? frozenPhaseTime : millis()/1000.0; }

float nodePhase(int node) {
  float sx=0, sy=0, sw=0;
  ArrayList<EdgeDatum> fieldEdges = gaugeActive!=null ? gaugeActive.edges : active.edges;
  for (EdgeDatum e : fieldEdges) if (e.source==node || e.target==node) {
    float w=max(e.weight,1e-6); sx+=cos(e.phase)*w; sy+=sin(e.phase)*w; sw+=w;
  }
  float base=sw>0 ? atan2(sy,sx) : active.primaryPhase;
  float coherence=0;
  for (int q=0;q<6;q++) coherence+=active.lineCoherence[q];
  return base+phaseTime()*(0.20+0.075*coherence)*(1+((node&1)==0?0.12:-0.12));
}

void drawStrongestPlaquette() {
  PlaquetteDatum loop=oraclePlaquette(); if (loop==null) return;
  int[] v=loop.vertices;
  float hue=phaseHue(loop.flux);
  float pulse=0.55+0.45*sin(phaseTime()*3.1);
  stroke(hue,0.92,1.0,0.58+0.35*pulse); strokeWeight(2.2+1.2*pulse); noFill();
  for (int i=0;i<4;i++) {
    PVector a=nodePosition(v[i]), b=nodePosition(v[(i+1)%4]);
    drawLoopEdge(a,b,i);
  }
  float direction=gaugeActive.chirality<0 ? -1.0 : 1.0;
  float travel=(phaseTime()*0.34*direction)%1.0; if (travel<0) travel+=1.0;
  float scaled=travel*4.0; int edge=floor(scaled); float t=scaled-edge;
  PVector a=nodePosition(v[edge]), b=nodePosition(v[(edge+1)%4]);
  PVector particle=loopEdgePoint(a,b,edge,t);
  noStroke(); fill(hue,0.72,1.0,0.96);
  ellipse(particle.x,particle.y,7.0,7.0);
}

PVector[] loopEdgeControls(PVector a,PVector b,int edge) {
  float dx=b.x-a.x, dy=b.y-a.y, length=max(1,sqrt(dx*dx+dy*dy));
  float sign=(edge%2==0)?1.0:-1.0, bend=13.0*sign;
  float nx=-dy/length, ny=dx/length;
  PVector c1=new PVector(lerp(a.x,b.x,0.33)+nx*bend,lerp(a.y,b.y,0.33)+ny*bend);
  PVector c2=new PVector(lerp(a.x,b.x,0.67)+nx*bend,lerp(a.y,b.y,0.67)+ny*bend);
  return new PVector[] {c1,c2};
}

void drawLoopEdge(PVector a,PVector b,int edge) {
  PVector[] c=loopEdgeControls(a,b,edge);
  bezier(a.x,a.y,c[0].x,c[0].y,c[1].x,c[1].y,b.x,b.y);
}

PVector loopEdgePoint(PVector a,PVector b,int edge,float t) {
  PVector[] c=loopEdgeControls(a,b,edge);
  return new PVector(
    bezierPoint(a.x,c[0].x,c[1].x,b.x,t),
    bezierPoint(a.y,c[0].y,c[1].y,b.y,t)
  );
}

void drawHexagramGlyph(float x,float y,int node,float phase,float population) {
  boolean primary=node==active.primary, transformed=node==active.transformed, onPath=pathNode(node);
  float pulse=0.5+0.5*sin(phaseTime()*2.0+phase);
  float halo=17+8*sqrt(constrain(population*16,0,1))+3*pulse;
  pushMatrix(); translate(x,y+2*sin(phaseTime()*0.7+phase));

  noStroke();
  fill(phaseHue(phase),0.72,primary||transformed?0.96:0.68,
       primary||transformed?0.22+0.18*pulse:onPath?0.16:0.055+0.08*population*16);
  ellipse(0,0,halo*2.5,halo*2.5);
  noFill(); stroke(phaseHue(phase),0.62,primary||transformed?1.0:0.68,onPath?0.72:0.26);
  strokeWeight(primary||transformed?2.0:0.8);
  arc(0,0,halo*2,halo*2,phase%TWO_PI,phase%TWO_PI+PI*0.82);
  if (primary) { stroke(0.12,0.84,1.0,0.94); strokeWeight(2.1); ellipse(0,0,52,52); }
  if (transformed) { stroke(0.52,0.84,1.0,0.94); strokeWeight(2.1); ellipse(0,0,primary?59:52,primary?59:52); }

  for (int q=0;q<6;q++) {
    float yy=17-q*6.8;
    boolean yang=(node&(1<<q))!=0;
    boolean moving=(active.movingMask&(1<<q))!=0;
    float linePulse=moving ? 0.72+0.28*sin(phaseTime()*3.0+active.linePhase[q]) : 1.0;
    if (primary) stroke(0.12,0.82,1.0);
    else if (transformed) stroke(0.52,0.82,1.0);
    else stroke(phaseHue(phase+active.linePhase[q]*0.22),moving?0.82:0.34,moving?0.98:0.78);
    strokeWeight(moving?2.5:1.65);
    float half=19*linePulse;
    if (yang) line(-half,yy,half,yy);
    else { line(-half,yy,-4.2,yy); line(4.2,yy,half,yy); }
  }
  if (primary||transformed) {
    fill(primary?0.12:0.52,0.72,1.0); noStroke(); textAlign(CENTER); textSize(9);
    text(primary&&transformed?"H₀ = H₁":primary?"H₀":"H₁",0,34); textAlign(LEFT);
  }
  popMatrix();
}

int visibleIndex(int hexagram) {
  int[] q={0,2,3,5}; int result=0;
  for (int i=0; i<4; i++) result |= ((hexagram>>q[i])&1)<<i;
  return result;
}

String trigramName(int value) {
  String[] names={"Kun · Earth","Zhen · Thunder","Kan · Water","Dui · Lake",
                  "Gen · Mountain","Li · Fire","Xun · Wind","Qian · Heaven"};
  return names[value&7];
}

String movingLineText() {
  if (active.movingMask==0) return "no moving lines";
  String result="moving ";
  for (int q=0;q<6;q++) if ((active.movingMask&(1<<q))!=0)
    result+=(result.equals("moving ")?"":" · ")+"L"+(q+1);
  return result+"  (bottom → top)";
}

String traditionalLineValues() {
  String result="";
  for (int q=0;q<6;q++) {
    boolean yang=(active.primary&(1<<q))!=0, moving=(active.movingMask&(1<<q))!=0;
    int value=moving?(yang?9:6):(yang?7:8);
    result+=(q==0?"":"  ")+value;
  }
  return result;
}

void drawOracleGlyph(float x,float y,int node,float hue) {
  stroke(hue,0.72,1.0); strokeWeight(2.5);
  for (int q=0;q<6;q++) {
    float yy=y+18-q*7.2; boolean yang=(node&(1<<q))!=0;
    if (yang) line(x-22,yy,x+22,yy);
    else { line(x-22,yy,x-5,yy); line(x+5,yy,x+22,yy); }
  }
}

void drawOraclePanel() {
  float x0=width-680, y0=18, w=650, h=145;
  fill(0,0,0.09,0.91); noStroke(); rect(x0,y0,w,h,10);
  int kw0=kingWenByBinary[active.primary], kw1=kingWenByBinary[active.transformed];
  drawOracleGlyph(x0+42,y0+48,active.primary,0.12);
  drawOracleGlyph(x0+348,y0+48,active.transformed,0.52);
  fill(0.12,0.74,1.0); textSize(10); text("PRESENT · H₀",x0+82,y0+20);
  fill(0,0,0.96); textSize(12); text("#"+kw0+"  "+KING_WEN_NAMES[kw0],x0+82,y0+42);
  fill(0,0,0.62); textSize(10); text(trigramName((active.primary>>3)&7)+" over "+trigramName(active.primary&7),x0+82,y0+63);
  text("binary index "+active.primary,x0+82,y0+82);
  fill(0.52,0.74,1.0); textSize(10); text("EMERGING · H₁",x0+388,y0+20);
  fill(0,0,0.96); textSize(12); text("#"+kw1+"  "+KING_WEN_NAMES[kw1],x0+388,y0+42);
  fill(0,0,0.62); textSize(10); text(trigramName((active.transformed>>3)&7)+" over "+trigramName(active.transformed&7),x0+388,y0+63);
  text("binary index "+active.transformed,x0+388,y0+82);
  fill(0,0,0.84); textSize(10); text(movingLineText(),x0+82,y0+116);
  text("values  "+traditionalLineValues(),x0+335,y0+116);

  String state=consultationState();
  boolean waiting=state.equals("CONTACTING")||state.equals("CASTING");
  boolean failed=state.equals("SERVICE OFFLINE")||state.equals("FRAME INCOMPLETE")||state.equals("ORACLE ERROR");
  fill(failed?0.01:waiting?0.08:0.12,failed?0.82:waiting?0.78:0.55,failed?0.88:waiting?0.92:0.74); noStroke();
  rect(width-171,y0+102,124,25,6);
  fill(0,0,0.04); textAlign(CENTER); textSize(10);
  text(state.equals("READY")?"C  CONSULT":state,width-109,y0+119); textAlign(LEFT);
  if (failed) {
    fill(0.01,0.58,0.96); textSize(9);
    String detail=state.equals("SERVICE OFFLINE")?"start publisher:  python …visualizer_publisher_v1.py --serve":
                  state.equals("FRAME INCOMPLETE")?rejectedFrame:"see oracle service console";
    text(detail,x0+82,y0+137);
  }
}

String consultationState() {
  if (consultRequestId==0 || lastConsultCommitMillis>=consultRequestedMillis) return "READY";
  if (consultError) return "ORACLE ERROR";
  long elapsed=millis()-consultRequestedMillis;
  if (!consultAccepted && elapsed>1800) return "SERVICE OFFLINE";
  if (consultPublished && elapsed>4500) return "FRAME INCOMPLETE";
  return consultAccepted?"CASTING":"CONTACTING";
}

String incompleteSummary(NetworkFrame frame) {
  int realCount=0, imagCount=0;
  for (int i=0;i<DENSITY;i++) { if(frame.realRows[i])realCount++; if(frame.imagRows[i])imagCount++; }
  return "incomplete frame: edges "+frame.edges.size()+"/192 · flux "+frame.fluxCount+"/15 · rows "+realCount+"/16 + "+imagCount+"/16";
}

void drawDensityPanel() {
  float x0=width-390, y0=335, cell=20;
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

void drawGaugePanel() {
  float x0=width-410, y0=325, w=380, h=365;
  PlaquetteDatum shownLoop=oraclePlaquette(); boolean loopVisible=strongestLoopVisible();
  fill(0,0,0.10,0.90); noStroke(); rect(x0,y0,w,h,10);
  fill(0,0,0.94); textSize(14); text("V4 DYNAMIC GAUGE — 240 PLAQUETTES",x0+18,y0+25);
  fill(0,0,0.64); textSize(10);
  text("t "+nf(gaugeActive.time,1,3)+"   revision "+gaugeActive.revision+
       "   active "+gaugeActive.activePlaquettes,x0+18,y0+45);
  fill(0,0,0.86); textSize(11);
  text("mean |flux|  "+nf(gaugeActive.meanAbsFlux,1,5)+" rad",x0+18,y0+68);
  text("phase spread  "+nf(gaugeActive.circularVariance,1,5),x0+18,y0+87);
  text("chirality  "+nf(gaugeActive.chirality,1,5)+
       (gaugeActive.chirality<0?"  ↺":"  ↻"),x0+205,y0+68);
  text("L trace  "+nf(gaugeActive.laplacianTrace,1,4),x0+205,y0+87);

  fill(loopVisible?phaseHue(shownLoop.flux):0, loopVisible?0.78:0, loopVisible?1.0:0.56); textSize(10);
  text(loopVisible?"H₀-LOCAL LOOP":"LOOP UNRESOLVED",x0+18,y0+111);
  fill(0,0,0.78);
  text(loopVisible?"base "+shownLoop.base+" · L"+shownLoop.lineA+
       "/L"+shownLoop.lineB+" · φ "+nf(shownLoop.flux,1,4):
       unresolvedLoopReason(),x0+117,y0+111);

  float tileW=65, tileH=38, gap=5, startX=x0+18, startY=y0+128;
  for (int i=0;i<15;i++) {
    int col=i%5, row=i/5; float tx=startX+col*(tileW+gap), ty=startY+row*(tileH+gap);
    float brightness=constrain(0.14+sqrt(max(0,gaugeActive.pairStrength[i]))*4.2,0.14,0.95);
    fill(phaseHue(gaugeActive.pairPhase[i]),0.78,brightness,0.88); noStroke(); rect(tx,ty,tileW,tileH,5);
    fill(0,0,brightness>0.55?0.04:0.96); textSize(9);
    text("L"+gaugeActive.pairA[i]+"·L"+gaugeActive.pairB[i],tx+6,ty+14);
    text("|φ| "+nf(gaugeActive.pairMeanAbs[i],1,3),tx+6,ty+29);
  }

  float sy=y0+275, maxEigen=1e-9;
  for (int i=0;i<gaugeActive.spectrum.length;i++) maxEigen=max(maxEigen,gaugeActive.spectrum[i]);
  fill(0,0,0.66); textSize(9); text("LOW MAGNETIC-LAPLACIAN SPECTRUM",x0+18,sy-7);
  for (int i=0;i<gaugeActive.spectrum.length;i++) {
    float bh=38*sqrt(constrain(gaugeActive.spectrum[i]/maxEigen,0,1));
    fill(0.58+i*0.025,0.64,0.84); noStroke(); rect(x0+20+i*42,sy+40-bh,28,bh);
  }
  fill(0,0,0.55); textSize(9);
  text("λmin "+nf(gaugeActive.minimumEigenvalue,1,7)+
       "   Hermitian error "+nf(gaugeActive.hermiticityError,1,7),x0+18,y0+h-14);
}

String comparisonState() {
  if (ibmState.equals("CONTACTING") && millis()-ibmRequestedMillis>1800) return "SERVICE OFFLINE";
  return ibmState;
}

String compactJob(String job) {
  if (job==null || job.length()==0) return "";
  return job.length()>18 ? job.substring(0,18)+"…" : job;
}

void drawIBMPanel() {
  float x0=width-680, y0=172, w=650, h=112;
  fill(0,0,0.09,0.91); noStroke(); rect(x0,y0,w,h,10);
  fill(0.60,0.62,1.0); textSize(10); text("LOCAL ↔ QUANTUM ROUTE COMPARISON",x0+18,y0+20);
  String state=comparisonState();
  boolean failed=state.equals("SERVICE OFFLINE")||state.equals("ERROR")||state.equals("FRAME INCOMPLETE");
  boolean waiting=state.equals("CONTACTING")||state.equals("ACCEPTED")||state.equals("TRANSPILED")||state.equals("SUBMITTED");

  if (ibmActive==null) {
    fill(0,0,0.72); textSize(11);
    text("No comparison yet.  I runs and sounds Aer unless the service was hardware-enabled.",x0+18,y0+48);
    fill(0,0,0.48); textSize(9);
    text("C always remains local and never submits IBM work.",x0+18,y0+70);
  } else {
    fill(0.12,0.62,0.96); textSize(10); text("LOCAL",x0+18,y0+44);
    fill(0,0,0.90); textSize(11);
    text("H₀ "+ibmActive.localPrimary+"   M "+ibmActive.localMask+"   H₁ "+ibmActive.localTransformed,x0+67,y0+44);
    fill(0.55,0.62,0.96); textSize(10); text(ibmActive.source.toUpperCase(),x0+18,y0+64);
    fill(0,0,0.90); textSize(11);
    text("H₀ "+ibmActive.externalPrimary+"   M "+ibmActive.externalMask+"   H₁ "+ibmActive.externalTransformed,x0+67,y0+64);
    fill(0,0,0.66); textSize(9);
    text("TVD "+nf(ibmActive.tvd,1,3)+"   fidelity "+nf(ibmActive.fidelity,1,3)+"   moving MAE "+nf(ibmActive.movingMae,1,3),x0+18,y0+87);
    String provenance="seed "+unsignedSeed(ibmActive.seed)+" · "+ibmActive.backend+
      (ibmActive.job.length()>0?" · "+compactJob(ibmActive.job):"")+" · "+ibmActive.shots+" shots/circuit";
    text(provenance,x0+268,y0+87);
  }

  fill(failed?0.01:waiting?0.08:0.60,failed?0.82:waiting?0.78:0.52,failed?0.88:waiting?0.92:0.78); noStroke();
  rect(width-171,y0+14,124,25,6);
  fill(0,0,0.04); textAlign(CENTER); textSize(10);
  text(state.equals("NOT REQUESTED")||state.equals("COMPLETE")?"I  COMPARE":state,width-109,y0+31); textAlign(LEFT);
  if (failed) {
    fill(0.01,0.58,0.96); textSize(9);
    text(state.equals("SERVICE OFFLINE")?"start comparison service on UDP 7406":ibmJob,x0+335,y0+106);
  }
}

void drawHUD() {
  fill(0,0,0.92); textSize(18); text("QMW I CHING — EVOLVING HEXAGRAM PHASE FIELD",28,34);
  textSize(13); fill(0,0,0.74);
  int shownRevision=gaugeActive!=null?gaugeActive.revision:active.revision;
  text("revision " + shownRevision + "   seed " + unsignedSeed(active.seed) +
       "   OSC " + OSC_PORT + "   " + (millis()-lastCommitMillis<1600 ? "● COMMIT" : "○ listening"),28,58);
  fill(0,0,0.90); textSize(14);
  text("binary H₀ " + active.primary + "   M " + active.movingMask + "   H₁ " + active.transformed +
       "   change " + active.changeRegister,28,84);
  if (gaugeActive!=null) {
    PlaquetteDatum shownLoop=oraclePlaquette(); boolean loopVisible=strongestLoopVisible();
    text("gauge flux " + nf(gaugeActive.meanAbsFlux,1,5) + " rad   phase spread " +
         nf(gaugeActive.circularVariance,1,5)+"   chirality "+nf(gaugeActive.chirality,1,5),28,107);
    text(loopVisible?"H₀-local square " + shownLoop.base + " · L"+shownLoop.lineA+
         "/L"+shownLoop.lineB+"   φ "+nf(shownLoop.flux,1,4):
         "gauge loop unresolved after collapse",28,130);
  } else {
    text("Pauli " + active.pauli + "  <P> " + nf(active.pauliExpectation,1,4) +
         "   I(L:U) " + nf(active.mutualInformation,1,4) + " bits",28,107);
    text("path phase " + nf(active.primaryPhase,1,4) + " rad   purity " + nf(active.purity,1,4),28,130);
  }

  float y=height-92;
  for (int line=0; line<6; line++) {
    boolean moving=(active.movingMask&(1<<line))!=0;
    fill(phaseHue(active.linePhase[line]),0.80,moving?1.0:0.58);
    rect(28+line*116,y,104,7);
    fill(0,0,moving?0.95:0.60); textSize(11);
    text("L"+(line+1)+" p="+nf(active.lineProbability[line],1,2)+" φ="+nf(active.linePhase[line],1,2),28+line*116,y+23);
  }
  if (showHelp) {
    fill(0,0,0.08,0.84); noStroke(); rect(width-390,700,360,158,10);
    fill(0,0,0.88); textSize(12);
    text("C  capture V4 field → cast → chime\nI  fresh-seeded V2 local ↔ Aer / IBM\nDRAG  pan field     WHEEL  zoom\nSPACE  pause phase\nE  toggle edges     R  reset view\nD  deterministic demo     H  hide help\n\nRead: PRESENT → moving lines → EMERGING\nThe field evolves; the cast remains fixed.",width-370,714);
  }
}

String unsignedSeed(int value) { return String.valueOf(((long)value) & 0xffffffffL); }

void requestConsultation() {
  OscMessage request=new OscMessage("/qmw/iching/consult/request");
  consultRequestId=millis(); request.add(consultRequestId); osc.send(request,oracleControl);
  consultRequestedMillis=millis(); consultAccepted=false; consultPublished=false; consultError=false; rejectedFrame="";
}

void requestIBMComparison() {
  OscMessage request=new OscMessage(IBM_ROOT+"/request");
  ibmRequestCounter++;
  long mixed=System.nanoTime();
  mixed^=((long)(gaugeActive!=null?gaugeActive.revision:active.revision))<<32;
  mixed^=((long)active.primary<<24)^((long)active.movingMask<<12)^active.transformed;
  mixed^=0x9E3779B97F4A7C15L*(long)ibmRequestCounter;
  ibmRequestSeed=(int)(mixed^(mixed>>>32));
  ibmRequestRevision=millis()^(ibmRequestCounter*0x45d9f3b);
  request.add(ibmRequestRevision); request.add(ibmRequestSeed); request.add(3);
  osc.send(request,ibmControl);
  ibmRequestedMillis=millis(); ibmState="CONTACTING"; ibmBackend=""; ibmJob="";
}

int gaugePairIndex(int lineA,int lineB) {
  int index=0;
  for (int a=1;a<=6;a++) for (int b=a+1;b<=6;b++) {
    if (a==lineA && b==lineB) return index;
    index++;
  }
  return -1;
}

void oscEvent(OscMessage m) {
  String address=m.addrPattern();
  if (address.startsWith(V4_ROOT)) {
    String route=address.substring(V4_ROOT.length());
    try {
      int revision=m.get(0).intValue();
      if (route.equals("/consult")) {
        active.primary=m.get(1).intValue(); active.transformed=m.get(2).intValue();
        active.movingMask=0;
        for (int line=0;line<6;line++) {
          int traditional=m.get(3+line).intValue();
          if (traditional==6 || traditional==9) active.movingMask|=1<<line;
          active.lineProbability[line]=m.get(9+line).floatValue();
        }
        active.changeRegister=Integer.bitCount(active.movingMask);
        lastConsultCommitMillis=millis();
        return;
      }
      if (route.equals("/begin")) {
        gaugeCandidate=new GaugeV4Frame(); gaugeCandidate.revision=revision;
        gaugeCandidate.time=m.get(1).floatValue(); gaugeCandidate.plaquetteCount=m.get(2).intValue();
        gaugeCandidate.pairCount=m.get(3).intValue(); gaugeCandidate.edgeLineTarget=m.get(4).intValue();
        gaugeCandidate.spectrumCount=m.get(5).intValue();
        gaugeCandidate.spectrum=new float[gaugeCandidate.spectrumCount]; return;
      }
      if (gaugeCandidate==null || revision!=gaugeCandidate.revision) return;
      if (route.equals("/hexagram64")) {
        for (int i=0;i<64;i++) gaugeCandidate.population[i]=m.get(1+i).floatValue();
        gaugeCandidate.hasPopulation=true;
      } else if (route.equals("/moving6")) {
        for (int i=0;i<6;i++) gaugeCandidate.moving[i]=m.get(1+i).floatValue();
        gaugeCandidate.hasMoving=true;
      } else if (route.equals("/gauge/summary")) {
        gaugeCandidate.activePlaquettes=m.get(1).intValue();
        gaugeCandidate.meanAbsFlux=m.get(2).floatValue(); gaugeCandidate.circularMean=m.get(3).floatValue();
        gaugeCandidate.circularVariance=m.get(4).floatValue(); gaugeCandidate.chirality=m.get(5).floatValue();
        gaugeCandidate.strongestIndex=m.get(6).intValue(); gaugeCandidate.strongestBase=m.get(7).intValue();
        gaugeCandidate.strongestLineA=m.get(8).intValue(); gaugeCandidate.strongestLineB=m.get(9).intValue();
        for (int i=0;i<4;i++) gaugeCandidate.strongestVertices[i]=m.get(10+i).intValue();
        gaugeCandidate.strongestFlux=m.get(14).floatValue(); gaugeCandidate.strongestStrength=m.get(15).floatValue();
        gaugeCandidate.laplacianTrace=m.get(16).floatValue(); gaugeCandidate.minimumEigenvalue=m.get(17).floatValue();
        gaugeCandidate.hermiticityError=m.get(18).floatValue(); gaugeCandidate.hasSummary=true;
      } else if (route.equals("/gauge/spectrum")) {
        for (int i=0;i<gaugeCandidate.spectrumCount;i++) gaugeCandidate.spectrum[i]=m.get(1+i).floatValue();
        gaugeCandidate.hasSpectrum=true;
      } else if (route.equals("/gauge/edge_line")) {
        int line=m.get(1).intValue(); int lineIndex=line-1;
        if (lineIndex>=0 && lineIndex<6 && !gaugeCandidate.edgeLineSeen[lineIndex]) {
          for (int i=0;i<32;i++) {
            int source=m.get(2+i).intValue();
            gaugeCandidate.edges.add(new EdgeDatum(source,source^(1<<lineIndex),line,
              m.get(34+i).floatValue(),m.get(66+i).floatValue()));
          }
          gaugeCandidate.edgeLineSeen[lineIndex]=true; gaugeCandidate.edgeLines++;
        }
      } else if (route.equals("/gauge/pair_summary")) {
        int lineA=m.get(1).intValue(), lineB=m.get(2).intValue(); int index=gaugePairIndex(lineA,lineB);
        if (index>=0 && !gaugeCandidate.pairSeen[index]) {
          gaugeCandidate.pairA[index]=lineA; gaugeCandidate.pairB[index]=lineB;
          gaugeCandidate.pairMeanAbs[index]=m.get(4).floatValue(); gaugeCandidate.pairPhase[index]=m.get(5).floatValue();
          gaugeCandidate.pairVariance[index]=m.get(6).floatValue(); gaugeCandidate.pairChirality[index]=m.get(7).floatValue();
          gaugeCandidate.pairStrength[index]=m.get(8).floatValue();
          gaugeCandidate.pairSeen[index]=true; gaugeCandidate.pairSummaries++;
        }
      } else if (route.equals("/gauge/plaquette_pair")) {
        int lineA=m.get(1).intValue(), lineB=m.get(2).intValue();
        int index=gaugePairIndex(lineA,lineB);
        if (index>=0 && !gaugeCandidate.plaquetteSeen[index]) {
          for (int i=0;i<16;i++) gaugeCandidate.plaquettes.add(
            new PlaquetteDatum(
              m.get(3+i).intValue(),lineA,lineB,
              m.get(19+i).floatValue(),m.get(35+i).floatValue()
            )
          );
          gaugeCandidate.plaquetteSeen[index]=true; gaugeCandidate.plaquettePairs++;
        }
      } else if (route.equals("/end")) {
        if (gaugeCandidate.complete()) {
          gaugeActive=gaugeCandidate; lastCommitMillis=millis();
          for (int line=0;line<6;line++) {
            active.lineProbability[line]=gaugeActive.moving[line];
            float sx=0,sy=0,total=0;
            for (EdgeDatum e:gaugeActive.edges) if (e.line==line+1) {
              sx+=cos(e.phase)*e.weight; sy+=sin(e.phase)*e.weight; total+=e.weight;
            }
            active.linePhase[line]=atan2(sy,sx);
            active.lineCoherence[line]=constrain(total*4.0,0,1);
          }
        } else rejectedFrame="incomplete V4 frame: edges "+gaugeCandidate.edges.size()+"/192 · pairs "+
          gaugeCandidate.pairSummaries+"/"+gaugeCandidate.pairCount+" · plaquettes "+
          gaugeCandidate.plaquettes.size()+"/"+gaugeCandidate.plaquetteCount;
        gaugeCandidate=null;
      }
    } catch (Exception ignored) { gaugeCandidate=null; }
    return;
  }
  if (address.startsWith(IBM_ROOT)) {
    String route=address.substring(IBM_ROOT.length());
    try {
      int revision=m.get(0).intValue();
      if (route.equals("/status")) {
        if (revision==ibmRequestRevision) {
          ibmState=m.get(1).stringValue().toUpperCase();
          ibmBackend=m.get(2).stringValue(); ibmJob=m.get(3).stringValue();
        }
        return;
      }
      if (route.equals("/begin")) {
        if (revision!=ibmRequestRevision) return;
        ibmCandidate=new IBMFrame(); ibmCandidate.revision=revision; ibmCandidate.seed=m.get(1).intValue();
        ibmCandidate.source=m.get(2).stringValue(); ibmCandidate.backend=m.get(3).stringValue();
        ibmCandidate.job=m.get(4).stringValue(); ibmCandidate.shots=m.get(5).intValue(); return;
      }
      if (ibmCandidate==null || revision!=ibmCandidate.revision) return;
      if (route.equals("/reading")) {
        ibmCandidate.localPrimary=m.get(1).intValue(); ibmCandidate.localMask=m.get(2).intValue(); ibmCandidate.localTransformed=m.get(3).intValue();
        ibmCandidate.externalPrimary=m.get(4).intValue(); ibmCandidate.externalMask=m.get(5).intValue(); ibmCandidate.externalTransformed=m.get(6).intValue(); ibmCandidate.hasReading=true;
      } else if (route.equals("/metrics")) {
        ibmCandidate.tvd=m.get(1).floatValue(); ibmCandidate.fidelity=m.get(2).floatValue(); ibmCandidate.movingMae=m.get(3).floatValue(); ibmCandidate.hasMetrics=true;
      } else if (route.equals("/moving")) {
        for (int line=0;line<6;line++) {
          ibmCandidate.localMoving[line]=m.get(1+line).floatValue();
          ibmCandidate.externalMoving[line]=m.get(7+line).floatValue();
        }
        ibmCandidate.hasMoving=true;
      } else if (route.equals("/end")) {
        if (ibmCandidate.complete()) {
          ibmActive=ibmCandidate; ibmState="COMPLETE"; ibmBackend=ibmActive.backend; ibmJob=ibmActive.job;
        } else ibmState="FRAME INCOMPLETE";
        ibmCandidate=null;
      }
    } catch (Exception ignored) { ibmCandidate=null; ibmState="ERROR"; }
    return;
  }
  if (address.startsWith(CONSULT_ROOT)) {
    try {
      int requestId=m.get(0).intValue();
      if (requestId==consultRequestId) {
        if (address.equals(CONSULT_ROOT+"/accepted")) consultAccepted=true;
        else if (address.equals(CONSULT_ROOT+"/published")) consultPublished=true;
        else if (address.equals(CONSULT_ROOT+"/error")) consultError=true;
      }
    } catch (Exception ignored) {}
    return;
  }
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
      if (candidate.complete()) {
        active=candidate; lastCommitMillis=millis();
        ibmActive=null; ibmCandidate=null; ibmState="NOT REQUESTED"; ibmRequestRevision=-1;
      }
      else rejectedFrame=incompleteSummary(candidate);
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
  gaugeActive=null; gaugeCandidate=null; lastConsultCommitMillis=lastCommitMillis;
  ibmActive=null; ibmCandidate=null; ibmState="NOT REQUESTED"; ibmRequestRevision=-1;
}

void mousePressed(){
  if(mouseX>=width-171 && mouseX<=width-47 && mouseY>=120 && mouseY<=147){requestConsultation();return;}
  if(mouseX>=width-171 && mouseX<=width-47 && mouseY>=186 && mouseY<=225){requestIBMComparison();return;}
  dragging=true;dragX=mouseX;dragY=mouseY;
}
void mouseReleased(){dragging=false;}
void mouseDragged(){if(dragging){fieldPanX+=mouseX-dragX;fieldPanY+=mouseY-dragY;dragX=mouseX;dragY=mouseY;}}
void mouseWheel(MouseEvent event){zoom=constrain(zoom-event.getCount()*0.06,0.45,1.8);}
void keyPressed(){
  if(key=='r'||key=='R'){fieldPanX=0;fieldPanY=0;zoom=1;}
  else if(key=='d'||key=='D')loadDemo();
  else if(key=='h'||key=='H')showHelp=!showHelp;
  else if(key=='e'||key=='E')showEdges=!showEdges;
  else if(key=='c'||key=='C')requestConsultation();
  else if(key=='i'||key=='I')requestIBMComparison();
  else if(key==' '){if(!phasePaused)frozenPhaseTime=millis()/1000.0;phasePaused=!phasePaused;}
}
