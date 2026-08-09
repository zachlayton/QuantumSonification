// Render compact Pauli-15 descriptors into separate local/IBM 4x256 buffers.
autowatch = 1;
inlets = 1;
outlets = 7; // status, buffer bangs, preview, Pauli list, local XYZ, IBM XYZ

var states = { local: null, ibm: null };
var renderMode = "hybrid";
var spectralSpatial = 0.5;
var smoothDetailed = 0.5;
var stableNonlinear = 0.0;

function clamp(x, lo, hi) { return Math.max(lo, Math.min(hi, x)); }
function safeTanh(x) {
    var e = Math.exp(2 * clamp(x, -20, 20));
    return (e - 1) / (e + 1);
}
function mode(value) { renderMode = String(value).toLowerCase(); rerender(); }
function spectral(value) { spectralSpatial = clamp(Number(value), 0, 1); rerender(); }
function detail(value) { smoothDetailed = clamp(Number(value), 0, 1); rerender(); }
function nonlinear(value) { stableNonlinear = clamp(Number(value), 0, 1); rerender(); }

function list() {
    var a = arrayfromargs(arguments);
    if (a.length !== 21) {
        outlet(0, ["error", "state_expected_21_atoms", a.length]);
        return;
    }
    var revision = Math.floor(Number(a.shift()));
    var source = String(a.shift()).toLowerCase();
    if (source !== "local" && source !== "ibm") {
        outlet(0, ["error", "state_source", source]); return;
    }
    var coefficients = [];
    for (var i = 0; i < 15; i++) coefficients.push(Number(a.shift()));
    states[source] = { revision: revision, c: coefficients, features: a };
    outlet(0, ["state_received", source, revision]);
    outlet(4, coefficients);
    outlet(source === "local" ? 5 : 6,
        [coefficients[6], coefficients[10], coefficients[14]]);
    try {
        render(source, true);
    } catch (error) {
        outlet(0, ["error", "render_failed", source, revision, String(error)]);
    }
}

function rerender() {
    if (states.local) render("local", false);
    if (states.ibm) render("ibm", false);
}

function cyclicSpline(knots, size) {
    var out = [], n = knots.length;
    for (var s = 0; s < size; s++) {
        var position = s * n / size;
        var i1 = Math.floor(position), t = position - i1;
        var p0 = knots[(i1 - 1 + n) % n], p1 = knots[i1 % n];
        var p2 = knots[(i1 + 1) % n], p3 = knots[(i1 + 2) % n];
        var t2 = t*t, t3 = t2*t;
        out.push(0.5 * ((2*p1) + (-p0+p2)*t +
            (2*p0-5*p1+4*p2-p3)*t2 + (-p0+3*p1-3*p2+p3)*t3));
    }
    return out;
}

function ifftLike(c, size, row) {
    var out = [];
    for (var s = 0; s < size; s++) {
        var phase = 2*Math.PI*s/size, sum = 0.04*Math.sin(phase);
        for (var i = 0; i < 15; i++) {
            var base = 2*i + (c[i] >= 0 ? 1 : 2);
            var h = row === 0 ? base : row === 1 ? base+12 : row === 2 ? 2*base : 61-base;
            sum += Math.abs(c[i]) * Math.sin(h*phase);
        }
        out.push(sum);
    }
    return out;
}

var pauli = {
    I: [[[1,0],[0,0]],[[0,0],[1,0]]],
    X: [[[0,0],[1,0]],[[1,0],[0,0]]],
    Y: [[[0,0],[0,-1]],[[0,1],[0,0]]],
    Z: [[[1,0],[0,0]],[[0,0],[-1,0]]]
};
var terms = ["XI","YI","ZI","IX","IY","IZ","XX","XY","XZ","YX","YY","YZ","ZX","ZY","ZZ"];

function densityKnots(c) {
    var values = { II: 1.0 };
    for (var i = 0; i < 15; i++) values[terms[i]] = c[i];
    var matrix = [];
    for (var r = 0; r < 4; r++) {
        matrix[r] = [];
        for (var col = 0; col < 4; col++) matrix[r][col] = [0,0];
    }
    for (var name in values) {
        var a = pauli[name.charAt(0)], b = pauli[name.charAt(1)], scale = values[name]/4;
        for (var r0=0;r0<2;r0++) for (var r1=0;r1<2;r1++)
            for (var c0=0;c0<2;c0++) for (var c1=0;c1<2;c1++) {
                var x=a[r0][c0], y=b[r1][c1];
                var re=x[0]*y[0]-x[1]*y[1], im=x[0]*y[1]+x[1]*y[0];
                matrix[2*r0+r1][2*c0+c1][0] += scale*re;
                matrix[2*r0+r1][2*c0+c1][1] += scale*im;
            }
    }
    var knots=[];
    for (var r=0;r<4;r++) for (var col=0;col<4;col++) {
        knots.push(matrix[r][col][0]); knots.push(matrix[r][col][1]);
    }
    return knots;
}

function smoothCircular(x, passes) {
    var current=x.slice(0), n=x.length;
    for (var p=0;p<passes;p++) {
        var next=[];
        for (var i=0;i<n;i++) next[i]=(current[(i-1+n)%n]+2*current[i]+current[(i+1)%n])/4;
        current=next;
    }
    return current;
}

function renderIR(source, state, waveform) {
    var length=262144, ir=[], c=state.c, f=state.features;
    var correlation=clamp(Number(f[2]),0,1), entropy=clamp(Number(f[3]),0,1);
    var rt60Samples=Math.round(length*(0.35+0.60*entropy)), peak=0, energy=0;
    // Calculate the Pauli coloration once as a 256-sample texture. Reusing it
    // avoids 7.8 million sin() calls for an 11-second IR.
    var diffusionPattern=[];
    for (var p=0;p<256;p++) {
        var sum=0;
        for (var term=0;term<15;term++)
            sum += c[term]*Math.sin(2*Math.PI*(term+1)*(p+1)/257)/(1+term*0.18);
        diffusionPattern.push(sum);
    }
    var reflectionA=Math.round(length*0.017);
    var reflectionB=Math.round(length*0.043);
    var reflectionC=Math.round(length*0.091);
    for (var i=0;i<length;i++) {
        // Reach -60 dB at the entropy-selected RT60 point.
        var envelope=Math.exp(Math.log(0.001)*i/rt60Samples);
        var color=waveform[i%256];
        var diffusion=diffusionPattern[i%256];
        var value=envelope*(0.55*color+0.08*diffusion);
        // Correlation controls deterministic early-reflection strength.
        if (i===reflectionA || i===reflectionB || i===reflectionC)
            value+=correlation*envelope*0.22;
        ir.push(value); peak=Math.max(peak,Math.abs(value)); energy+=value*value;
    }
    // Bound both instantaneous peak and total convolution energy.
    var energyScale=energy>0 ? 0.9/Math.sqrt(energy) : 1;
    var peakScale=peak>0 ? 0.7/peak : 1;
    var scale=Math.min(energyScale,peakScale);
    for (var j=0;j<length;j++) ir[j]*=scale;
    var target=new Buffer(source === "local" ? "qmw_v3_ir_local" : "qmw_v3_ir_ibm");
    target.send("sizeinsamps",length,1);
    target.poke(1,0,ir);
}

function render(source, updateIR) {
    var state=states[source], c=state.c, density=cyclicSpline(densityKnots(c),256);
    var spline=cyclicSpline([1].concat(c),256), rows=[], peak=0;
    for (var row=0;row<4;row++) {
        var spectral=ifftLike(c,256,row), t=clamp(spectralSpatial+(row-1.5)*0.12,0,1), wave=[];
        for (var i=0;i<256;i++) {
            var value;
            if (renderMode === "ifft") value=spectral[i];
            else if (renderMode === "spline") value=spline[i];
            else if (renderMode === "density") value=density[i];
            else value=(1-t)*spectral[i]+t*(0.65*density[i]+0.35*spline[i]);
            wave.push(value);
        }
        wave=smoothCircular(wave,Math.round((1-smoothDetailed)*10));
        for (var j=0;j<256;j++) {
            var shaped=safeTanh(2.5*wave[j])/safeTanh(2.5);
            wave[j]=(1-stableNonlinear)*wave[j]+stableNonlinear*shaped;
            peak=Math.max(peak,Math.abs(wave[j]));
        }
        rows.push(wave);
    }
    var scale=peak>0.95 ? 0.95/peak : 1.0;
    var target=new Buffer(source === "local" ? "qmw_v3_local" : "qmw_v3_ibm");
    for (var r=0;r<4;r++) {
        var scaled=[]; for (var s=0;s<256;s++) scaled.push(rows[r][s]*scale);
        target.poke(1,r*256,scaled);
        if (r === 3) outlet(3, scaled);
    }
    if (updateIR) {
        renderIR(source,state,rows[3]);
        // These bangs also tell multiconvolve~ to reload the changed IR.
        outlet(source === "local" ? 1 : 2,"bang");
    }
    outlet(0,["rendered",source,state.revision,renderMode,spectralSpatial,smoothDetailed,stableNonlinear]);
}
