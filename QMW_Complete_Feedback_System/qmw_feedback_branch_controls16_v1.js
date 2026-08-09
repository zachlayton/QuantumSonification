/*
    qmw_feedback_branch_controls16_v1.js

    Validates and conditions the sixteen per-branch controls used by
    qmw_density_matrix_resonator_feedback16_mc_v1.maxpat.

    inlet 0: 16 projection phases in radians, or control messages
    inlet 1: 16 feedback gains
    inlet 2: 16 delay times in milliseconds

    outlet 0: 16 unwrapped phase values
    outlet 1: 16 bounded gain values
    outlet 2: 16 bounded delay values
    outlet 3: status and validation messages
*/

autowatch = 1;
inlets = 3;
outlets = 4;

setinletassist(0, "16 projection phases (radians), or controls");
setinletassist(1, "16 feedback gains (bounded to 0..ceiling)");
setinletassist(2, "16 feedback delays (milliseconds)");
setoutletassist(0, "16 shortest-arc unwrapped phases");
setoutletassist(1, "16 bounded gains");
setoutletassist(2, "16 bounded delays in milliseconds");
setoutletassist(3, "status and validation messages");

var N = 16;
var TWO_PI = Math.PI * 2.0;
var gainCeiling = 0.92;
var minimumDelay = 1.0;
var maximumDelay = 2000.0;
var phase = new Array(N);
var gain = new Array(N);
var delayMs = new Array(N);

initialize();

function initialize() {
    var index;
    for (index = 0; index < N; index++) {
        phase[index] = 0.0;
        gain[index] = 0.0;
        delayMs[index] = 10.0;
    }
}

function numeric(value) {
    var converted = Number(value);
    return isFinite(converted) ? converted : 0.0;
}

function clip(value, low, high) {
    return Math.max(low, Math.min(high, numeric(value)));
}

function requireSixteen(values, label) {
    if (values.length === N) {
        return 1;
    }
    outlet(3, ["error", label, "expected", N, "received", values.length]);
    post("qmw feedback16: " + label + " requires exactly " + N
        + " values; received " + values.length + "\n");
    return 0;
}

function nearestPhase(previous, wrapped) {
    var delta = wrapped - previous;
    delta = Math.atan2(Math.sin(delta), Math.cos(delta));
    return previous + delta;
}

function acceptPhase(values) {
    var index;
    if (!requireSixteen(values, "phase")) {
        return;
    }
    for (index = 0; index < N; index++) {
        phase[index] = nearestPhase(phase[index], numeric(values[index]));
    }
    outlet(0, phase);
}

function acceptGain(values) {
    var index;
    if (!requireSixteen(values, "gain")) {
        return;
    }
    for (index = 0; index < N; index++) {
        gain[index] = clip(values[index], 0.0, gainCeiling);
    }
    outlet(1, gain);
}

function acceptDelay(values) {
    var index;
    if (!requireSixteen(values, "delay")) {
        return;
    }
    for (index = 0; index < N; index++) {
        delayMs[index] = clip(values[index], minimumDelay, maximumDelay);
    }
    outlet(2, delayMs);
}

function list() {
    var values = arrayfromargs(arguments);
    if (inlet === 0) {
        acceptPhase(values);
    } else if (inlet === 1) {
        acceptGain(values);
    } else {
        acceptDelay(values);
    }
}

function phases() {
    acceptPhase(arrayfromargs(arguments));
}

function gains() {
    acceptGain(arrayfromargs(arguments));
}

function delays() {
    acceptDelay(arrayfromargs(arguments));
}

function ceiling(value) {
    var index;
    gainCeiling = clip(value, 0.0, 0.99);
    for (index = 0; index < N; index++) {
        gain[index] = Math.min(gain[index], gainCeiling);
    }
    outlet(1, gain);
    outlet(3, ["ceiling", gainCeiling]);
}

function delayrange(low, high) {
    var candidateLow = Math.max(0.1, numeric(low));
    var candidateHigh = Math.max(candidateLow, numeric(high));
    minimumDelay = candidateLow;
    maximumDelay = candidateHigh;
    acceptDelay(delayMs);
    outlet(3, ["delayrange", minimumDelay, maximumDelay]);
}

function zero() {
    var index;
    for (index = 0; index < N; index++) {
        gain[index] = 0.0;
    }
    outlet(1, gain);
    outlet(3, ["gains", "zero"]);
}

function safe() {
    var index;
    for (index = 0; index < N; index++) {
        phase[index] = 0.0;
        gain[index] = 0.0;
        delayMs[index] = 10.0;
    }
    outlet(2, delayMs);
    outlet(1, gain);
    outlet(0, phase);
    outlet(3, ["safe", 1]);
}

function tune() {
    var values = arrayfromargs(arguments);
    var fundamental;
    var index;
    var ratio;

    if (values.length !== N + 1) {
        outlet(3, ["error", "tune", "expected", N + 1,
            "received", values.length]);
        return;
    }

    fundamental = Math.max(0.001, numeric(values[0]));
    for (index = 0; index < N; index++) {
        ratio = Math.max(0.001, numeric(values[index + 1]));
        delayMs[index] = clip(1000.0 / (fundamental * ratio),
            minimumDelay, maximumDelay);
    }
    outlet(2, delayMs);
    outlet(3, ["tuned", fundamental]);
}

function status() {
    outlet(3, [
        "status",
        "gain_ceiling", gainCeiling,
        "delay_min_ms", minimumDelay,
        "delay_max_ms", maximumDelay,
        "gain_max", Math.max.apply(null, gain),
        "delay_min_active", Math.min.apply(null, delayMs),
        "delay_max_active", Math.max.apply(null, delayMs)
    ]);
}

function bang() {
    outlet(2, delayMs);
    outlet(1, gain);
    outlet(0, phase);
    status();
}

function anything() {
    outlet(3, ["error", "unknown_message", messagename]
        .concat(arrayfromargs(arguments)));
}
