// QMW local hybrid wavetable renderer.
// Five inlets: real, imag, magnitude, phase, speed (16 floats each).
// Writes alternately to qmw_hybrid_table_A/B and reports table_mix to Gen~.

autowatch = 1;
inlets = 5;
outlets = 2;

var N = 256;
var K = 16;
var values = [];
var names = ["real", "imag", "magnitude", "phase", "speed"];
var active = 0;
var spectralWeight = 0.58;
var contourWeight = 0.27;
var detailWeight = 0.15;
var spectralSpatial = 0.22;
var smoothing = 0.35;
var renderDelayMs = 8;
var previous = [];
var renderTask = new Task(renderNow, this);

for (var stream = 0; stream < 5; stream++) {
    values[stream] = [];
    for (var i = 0; i < K; i++) values[stream][i] = stream === 2 ? 1 : 0;
}
for (var n = 0; n < N; n++) previous[n] = 0;

function list() {
    var input = arrayfromargs(arguments);
    setStream(inlet, input);
}

function anything() {
    var args = arrayfromargs(arguments);
    var name = String(messagename);
    if (name === "real") setStream(0, args);
    else if (name === "imag") setStream(1, args);
    else if (name === "magnitude") setStream(2, args);
    else if (name === "phase") setStream(3, args);
    else if (name === "speed") setStream(4, args);
    else if (name === "weights" && args.length >= 3) weights(args[0], args[1], args[2]);
    else if (name === "spectral_spatial" && args.length) setSpectralSpatial(args[0]);
    else if (name === "detail" && args.length) setDetail(args[0]);
    else if (name === "smoothing" && args.length) smoothing = clamp(Number(args[0]), 0, 0.98);
    else if (name === "render") scheduleRender();
}

function setSpectralSpatial(value) {
    spectralSpatial = clamp(Number(value), 0, 1);
    // Equal-power endpoints make the middle useful without a level hollow.
    spectralWeight = Math.cos(spectralSpatial * Math.PI * 0.5);
    contourWeight = Math.sin(spectralSpatial * Math.PI * 0.5);
    scheduleRender();
}

function setDetail(value) {
    detailWeight = clamp(Number(value), 0, 1);
    scheduleRender();
}

function weights(spectral, contour, detail) {
    spectralWeight = Math.max(0, Number(spectral));
    contourWeight = Math.max(0, Number(contour));
    detailWeight = Math.max(0, Number(detail));
    scheduleRender();
}

function setStream(which, input) {
    if (which < 0 || which >= 5) return;
    for (var i = 0; i < Math.min(K, input.length); i++) {
        var x = Number(input[i]);
        values[which][i] = isFinite(x) ? x : 0;
    }
    scheduleRender();
}

function scheduleRender() {
    renderTask.cancel();
    renderTask.schedule(renderDelayMs);
}

function renderNow() {
    var table = [];
    var sum = 0;
    var weightSum = Math.max(spectralWeight + contourWeight + detailWeight, 1e-12);

    for (var n = 0; n < N; n++) {
        var cycle = n / N;
        var knotPosition = cycle * K;
        var k0 = Math.floor(knotPosition) % K;
        var k1 = (k0 + 1) % K;
        var t = knotPosition - Math.floor(knotPosition);
        var smoothT = t * t * (3 - 2 * t);
        var contour0 = complexKnot(k0);
        var contour1 = complexKnot(k1);
        var contour = contour0 + (contour1 - contour0) * smoothT;

        // The 16 complex descriptors become harmonics 1..16. Magnitude and
        // phase remain local quantum controls rather than transmitted samples.
        var spectral = 0;
        var detail = 0;
        for (var k = 0; k < K; k++) {
            var re = values[0][k];
            var im = values[1][k];
            var mag = clamp(values[2][k], 0, 1);
            var ph = values[3][k];
            var amp = (0.2 + 0.8 * mag) * Math.sqrt(re * re + im * im);
            var complexPhase = Math.atan2(im, re) + ph;
            var harmonic = k + 1;
            spectral += amp * Math.cos(2 * Math.PI * harmonic * cycle + complexPhase) / Math.sqrt(harmonic);

            // A restrained sideband layer exposes motion without increasing OSC.
            var motion = clamp(Math.abs(values[4][k]), 0, 1);
            detail += motion * amp * Math.sin(2 * Math.PI * (harmonic * 2 + 1) * cycle - complexPhase) / harmonic;
        }

        var sample = (spectralWeight * spectral + contourWeight * contour + detailWeight * detail) / weightSum;
        table[n] = sample;
        sum += sample;
    }

    var mean = sum / N;
    var peak = 1e-12;
    for (var j = 0; j < N; j++) {
        table[j] -= mean;
        peak = Math.max(peak, Math.abs(table[j]));
    }
    var scale = 0.92 / peak;
    for (var q = 0; q < N; q++) {
        var normalized = tanhCompat(table[q] * scale * 1.25) / tanhCompat(1.25);
        table[q] = smoothing * previous[q] + (1 - smoothing) * normalized;
        previous[q] = table[q];
    }

    var next = 1 - active;
    var bufferName = next ? "qmw_hybrid_table_B" : "qmw_hybrid_table_A";
    var target = new Buffer(bufferName);
    target.poke(1, 0, table);
    active = next;

    outlet(0, "table_mix", active);
    outlet(1, "rendered", bufferName, N, peak);
}

function complexKnot(k) {
    var re = values[0][k];
    var im = values[1][k];
    var mag = clamp(values[2][k], 0, 1);
    var ph = values[3][k];
    return (0.2 + 0.8 * mag) * (re * Math.cos(ph) - 0.35 * im * Math.sin(ph));
}

function clamp(x, lo, hi) {
    return Math.max(lo, Math.min(hi, x));
}

// Max 8's legacy js object does not provide the ES6 Math.tanh function.
function tanhCompat(x) {
    if (x > 20) return 1;
    if (x < -20) return -1;
    var doubled = Math.exp(2 * x);
    return (doubled - 1) / (doubled + 1);
}

function bang() { scheduleRender(); }
