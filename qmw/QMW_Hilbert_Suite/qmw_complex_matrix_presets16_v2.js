/* Complex 16x16 operator presets and audible imaginary-coupling depth v2. */
autowatch = 1;
inlets = 4;
outlets = 4;

var N = 16, CELLS = 256;
var re = new Array(CELLS), im = new Array(CELLS), populations = new Array(N);
var externalRe = new Array(CELLS), externalIm = new Array(CELLS);
var imagDepth = 1.0, source = "identity";
var externalReDirty = 0, externalImDirty = 0;
var i;

for (i = 0; i < N; i++) populations[i] = i === 0 ? 1 : 0;
identity();

function num(v, fallback) { var x = Number(v); return isFinite(x) ? x : fallback; }
function zeroMatrices() { for (var k=0;k<CELLS;k++){ re[k]=0; im[k]=0; } }
function emit() {
    var scaled = new Array(CELLS);
    for (var k=0;k<CELLS;k++) scaled[k] = im[k] * imagDepth;
    outlet(0, re); outlet(1, scaled);
    outlet(3, "commit");
    outlet(2, ["matrix", source, "imag_depth", imagDepth]);
}
function identity() {
    zeroMatrices(); for (var k=0;k<N;k++) re[k*N+k]=1;
    source="identity"; emit();
}
function diagonal() {
    zeroMatrices(); var peak=0;
    for(var k=0;k<N;k++) peak=Math.max(peak,Math.abs(populations[k]));
    peak=Math.max(peak,0.000001);
    for(var j=0;j<N;j++) re[j*N+j]=Math.sqrt(Math.max(0,populations[j])/peak);
    source="diagonal_populations"; emit();
}
function pair(a,b,name) {
    zeroMatrices();
    for(var k=0;k<N;k++) re[k*N+k]=0.72;
    im[a*N+b]=0.36; im[b*N+a]=-0.36;
    source=name; emit();
}
function fundamental_octave(){ pair(0,1,"fundamental_octave"); }
function fundamental_fifth(){ pair(0,4,"fundamental_fifth_harmonic"); }
function third_seventh(){ pair(2,6,"third_seventh_harmonic"); }
function ring() {
    zeroMatrices();
    for(var k=0;k<N;k++) {
        var next=(k+1)%N; re[k*N+k]=0.56;
        im[k*N+next]=0.22; im[next*N+k]=-0.22;
    }
    source="hermitian_coherence_ring"; emit();
}
function external(){
    for(var k=0;k<CELLS;k++){ re[k]=externalRe[k]||0; im[k]=externalIm[k]||0; }
    externalReDirty=0; externalImDirty=0;
    source="external"; emit();
}
function imagdepth(v){
    imagDepth=Math.max(0,Math.min(1,num(v,imagDepth)));
    // Identity and diagonal matrices contain no imaginary cells. In performance
    // use, raising Imaginary Coupling should create coupling rather than multiply
    // zero by a new depth value, so introduce the bounded Hermitian ring.
    if(imagDepth>0 && (source==="identity" || source==="diagonal_populations")){
        ring();
        return;
    }
    emit();
}
function cellpair(a,b){
    a=Math.floor(num(a,0)); b=Math.floor(num(b,1));
    if(a<0||a>=N||b<0||b>=N||a===b){ outlet(2,["error","pair",a,b]); return; }
    pair(a,b,"custom_pair_"+a+"_"+b);
}
function list(){
    var v=arrayfromargs(arguments), target;
    if(inlet===2){
        if(v.length!==N){outlet(2,["error","populations","expected",N,"received",v.length]);return;}
        for(var k=0;k<N;k++) populations[k]=Math.max(0,num(v[k],0));
        if(source==="diagonal_populations") diagonal();
        return;
    }
    if(v.length!==CELLS){outlet(2,["error",inlet===0?"external_re":"external_im","expected",CELLS,"received",v.length]);return;}
    target=inlet===0?externalRe:externalIm;
    for(var j=0;j<CELLS;j++) target[j]=num(v[j],0);
    if(inlet===0) externalReDirty=1; else externalImDirty=1;
    if(source==="external" && externalReDirty && externalImDirty) external();
}
function anything(){ outlet(2,["error","unknown",messagename].concat(arrayfromargs(arguments))); }
