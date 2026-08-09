// Translate a 16 x 16 Heisenberg field into CNMAT spectral models and SDIF.
autowatch = 1;
inlets = 1;
outlets = 9;

var DIMENSION = 16;
var CELL_COUNT = 256;
var magnitude = fill(CELL_COUNT, 0.0);
var frequency = fill(CELL_COUNT, 55.0);
var phase = fill(CELL_COUNT, 0.0);
var pan = fill(CELL_COUNT, 0.0);
var haveMagnitude = false;
var haveFrequency = false;
var havePhase = false;
var havePan = false;
var collecting = false;
var frameRevision = 0;
var mode = "coherent";
var outcome = -1;
var disturbance = 0.0;
var cellGain = 0.32;
var threshold = 0.000001;
var previousMode = "";
var previousOutcome = -999;
var localTest = false;

function fill(count, value) {
    var result = [];
    for (var i = 0; i < count; i++) result.push(value);
    return result;
}

function anything() {
    var args = arrayfromargs(arguments);
    var name = String(messagename);
    // A held local diagnostic must not be replaced by the publisher's next
    // periodic frame. `resume` returns control to OSC on the following frame.
    if (localTest) return;
    if (name === "begin") {
        collecting = true;
        if (args.length) frameRevision = Math.max(0, Math.floor(num(args[0], 0)));
    } else if (name === "end") {
        collecting = false;
        renderIfReady();
    } else if (name === "magnitude_normalized" || name === "magnitude") {
        magnitude = vector(args, 0.0);
        haveMagnitude = true;
        if (!collecting) renderIfReady();
    } else if (name === "frequency_hz") {
        frequency = vector(args, 55.0);
        haveFrequency = true;
        if (!collecting) renderIfReady();
    } else if (name === "phase") {
        phase = vector(args, 0.0);
        havePhase = true;
        if (!collecting) renderIfReady();
    } else if (name === "pan") {
        pan = vector(args, 0.0);
        havePan = true;
        if (!collecting) renderIfReady();
    } else if (name === "mode" && args.length) {
        mode = String(args[0]);
    } else if (name === "outcome" && args.length) {
        outcome = Math.floor(num(args[0], -1));
    } else if (name === "disturbance" && args.length) {
        disturbance = Math.max(0.0, num(args[0], 0.0));
    } else if (name === "cell_gain" && args.length) {
        cellGain = Math.max(0.0, num(args[0], 0.32));
        renderIfReady();
    } else if (name === "threshold" && args.length) {
        threshold = Math.max(0.0, num(args[0], 0.000001));
        renderIfReady();
    }
}

function vector(values, fallback) {
    var result = fill(CELL_COUNT, fallback);
    var count = Math.min(CELL_COUNT, values.length);
    for (var i = 0; i < count; i++) result[i] = num(values[i], fallback);
    return result;
}

function renderIfReady() {
    if (haveMagnitude && haveFrequency && havePhase && havePan) render();
}

function render() {
    var energy = 0.0;
    var active = 0;
    var i;
    for (i = 0; i < CELL_COUNT; i++) {
        var m = Math.max(0.0, magnitude[i]);
        if (m >= threshold) {
            energy += m * m;
            active++;
        }
    }
    var norm = energy > 0.0 ? cellGain / Math.sqrt(energy) : 0.0;
    var noisiness = mode === "unread" ? Math.min(0.9, 0.18 + 1.25 * disturbance) : 0.0;
    var sinLeft = [];
    var sinRight = [];
    var resLeft = [];
    var resRight = [];
    var trc = [];
    var resSdif = [];

    for (i = 0; i < CELL_COUNT; i++) {
        var row = Math.floor(i / DIMENSION);
        var column = i % DIMENSION;
        var mag = Math.max(0.0, magnitude[i]);
        var amp = mag >= threshold ? mag * norm : 0.0;
        var p = Math.max(-1.0, Math.min(1.0, pan[i]));
        var left = Math.sqrt((1.0 - p) * 0.5);
        var right = Math.sqrt((1.0 + p) * 0.5);
        var hz = Math.max(1.0, frequency[i]);
        var decay = 0.8 + 7.2 * (1.0 - Math.min(1.0, mag));
        var ph = phase[i];

        sinLeft.push(hz, amp * left, noisiness);
        sinRight.push(hz, amp * right, noisiness);
        resLeft.push(hz, amp * left, decay);
        resRight.push(hz, amp * right, decay);
        trc.push(i, hz, amp, ph);
        resSdif.push(hz, amp, decay, ph);
        outlet(5, "set", column, row, mag);
    }

    outlet(0, sinLeft);
    outlet(1, sinRight);
    outlet(2, resLeft);
    outlet(3, resRight);

    if (mode === "coherent") {
        outlet(4, "noise_gain", 0.0);
        outlet(4, "sin_gain", 0.78);
        outlet(4, "res_gain", 0.08);
    } else if (mode === "unread") {
        outlet(4, "noise_gain", 8.0);
        outlet(4, "sin_gain", 0.20);
        outlet(4, "res_gain", 0.52);
    } else {
        outlet(4, "noise_gain", 0.0);
        outlet(4, "sin_gain", 0.34);
        outlet(4, "res_gain", 0.62);
        if (previousMode !== "recorded" || previousOutcome !== outcome)
            outlet(4, "impulse", 0.72);
    }

    // Two simultaneous SDIF views of the same relational frame.
    var frameTime = frameRevision * 0.001;
    sendNewMatrix(7, frameTime, "1TRC", trc);
    sendNewMatrix(8, frameTime, "1RES", resSdif);

    var shownOutcome = outcome < 0 ? "none" : String(outcome);
    outlet(6, "set", "CNMAT", "mode=" + mode, "outcome=" + shownOutcome,
        "disturbance=" + disturbance.toFixed(5), "active_cells=" + active,
        "SDIF_frame=" + frameRevision);
    previousMode = mode;
    previousOutcome = outcome;
}

// SDIF-listpoke needs `newmatrix` as the message selector, not as the first
// member of an ordinary Max list.
function sendNewMatrix(outletNumber, frameTime, matrixType, data) {
    var message = [outletNumber, "newmatrix", frameTime, matrixType,
        CELL_COUNT, 4].concat(data);
    outlet.apply(this, message);
}

function test() {
    localTest = true;
    var savedMode = mode;
    mode = "coherent";
    for (var i = 0; i < CELL_COUNT; i++) {
        var row = Math.floor(i / DIMENSION);
        var column = i % DIMENSION;
        magnitude[i] = row === column ? 0.4 : ((row + column) % 9 === 0 ? 0.13 : 0.0);
        frequency[i] = 55.0 * Math.pow(2.0, ((row * 5 + column * 3) % 60) / 12.0);
        phase[i] = (column - row) * 0.19;
        pan[i] = (column - row) / 15.0;
    }
    haveMagnitude = haveFrequency = havePhase = havePan = true;
    frameRevision++;
    render();
    mode = savedMode;
    outlet(6, "set", "LOCAL TEST HELD", "continuous CNMAT field",
        "press RESUME LIVE to return to OSC");
}

function resume() {
    localTest = false;
    // Require one complete atomic matrix before rendering live again.
    haveMagnitude = haveFrequency = havePhase = havePan = false;
    collecting = false;
    outlet(6, "set", "LIVE RESUMED", "waiting for next complete OSC frame");
}

function num(value, fallback) {
    var result = Number(value);
    return isFinite(result) ? result : fallback;
}
