// V6 local/IBM Pauli comparison and phase-sensitive coherence synthesis.
autowatch = 1;
inlets = 1;
outlets = 5; // status, local-15, IBM-15, difference-15, coherence descriptors

var localValues = null;
var ibmValues = null;
var labels = ["XI","YI","ZI","IX","IY","IZ","XX","XY","XZ","YX","YY","YZ","ZX","ZY","ZZ"];

function c(re, im) { return {re:re, im:im}; }
function add(a,b) { return c(a.re+b.re,a.im+b.im); }
function mul(a,b) { return c(a.re*b.re-a.im*b.im,a.re*b.im+a.im*b.re); }
function scale(a,s) { return c(a.re*s,a.im*s); }

var P = {
    I:[[c(1,0),c(0,0)],[c(0,0),c(1,0)]],
    X:[[c(0,0),c(1,0)],[c(1,0),c(0,0)]],
    Y:[[c(0,0),c(0,-1)],[c(0,1),c(0,0)]],
    Z:[[c(1,0),c(0,0)],[c(0,0),c(-1,0)]]
};

function kron(a,b) {
    var out=[];
    for (var r=0;r<4;r++) { out[r]=[]; for (var col=0;col<4;col++)
        out[r][col]=mul(a[Math.floor(r/2)][Math.floor(col/2)],b[r%2][col%2]); }
    return out;
}

function density(values) {
    var rho=[], r, col;
    for (r=0;r<4;r++) { rho[r]=[]; for (col=0;col<4;col++) rho[r][col]=c(0,0); }
    var identity=kron(P.I,P.I);
    for (r=0;r<4;r++) for (col=0;col<4;col++) rho[r][col]=identity[r][col];
    for (var i=0;i<15;i++) {
        var term=kron(P[labels[i].charAt(0)],P[labels[i].charAt(1)]);
        for (r=0;r<4;r++) for (col=0;col<4;col++)
            rho[r][col]=add(rho[r][col],scale(term[r][col],Number(values[i])));
    }
    for (r=0;r<4;r++) for (col=0;col<4;col++) rho[r][col]=scale(rho[r][col],0.25);
    return rho;
}

function coherences(values) {
    var rho=density(values), pairs=[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]], out=[];
    for (var i=0;i<pairs.length;i++) {
        var z=rho[pairs[i][0]][pairs[i][1]];
        out.push({magnitude:Math.sqrt(z.re*z.re+z.im*z.im),phase:Math.atan2(z.im,z.re)});
    }
    return out;
}

function writeVoice(name, values) {
    var q=coherences(values), wave=[], peak=0;
    for (var n=0;n<256;n++) {
        var t=2*Math.PI*n/256, value=0;
        for (var k=0;k<q.length;k++) value+=q[k].magnitude*Math.sin((k+1)*t+q[k].phase);
        wave.push(value); peak=Math.max(peak,Math.abs(value));
    }
    var gain=peak>0.95 ? 0.95/peak : 1;
    for (n=0;n<256;n++) wave[n]*=gain;
    new Buffer(name).poke(1,0,wave);
    var descriptors=[];
    for (k=0;k<q.length;k++) descriptors.push(q[k].magnitude,q[k].phase);
    return descriptors;
}

function list() {
    var a=arrayfromargs(arguments);
    if (a.length!==21) { outlet(0,["error","state_expected_21_atoms",a.length]); return; }
    var revision=Math.floor(Number(a.shift())), source=String(a.shift()).toLowerCase(), values=[];
    for (var i=0;i<15;i++) values.push(Number(a.shift()));
    if (source==="local") { localValues=values; outlet(1,values); }
    else if (source==="ibm") { ibmValues=values; outlet(2,values); }
    else return;
    var d=writeVoice(source==="local" ? "qmw_v6_coherence_local" : "qmw_v6_coherence_ibm",values);
    outlet(4,[source,revision].concat(d));
    if (localValues && ibmValues) {
        var delta=[]; for (i=0;i<15;i++) delta.push(ibmValues[i]-localValues[i]);
        outlet(3,delta); writeVoice("qmw_v6_coherence_difference",delta);
    }
    outlet(0,["coherence_ready",source,revision]);
}
