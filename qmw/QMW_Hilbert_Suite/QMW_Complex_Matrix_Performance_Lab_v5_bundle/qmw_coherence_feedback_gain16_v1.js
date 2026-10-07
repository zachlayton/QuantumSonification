/*
    qmw_coherence_feedback_gain16_v1.js

    Generates a uniform sixteen-branch feedback-gain list from normalized
    coherence and entropy while preserving a known fixed baseline.

        gain = base + depth * span * coherence * (1 - entropy_damping*entropy)

    inlet 0: coherence 0..1, or bang
    inlet 1: entropy 0..1
    inlet 2: Feedback Depth 0..1

    outlet 0: gain list[16]
    outlet 1: effective scalar gain
    outlet 2: status
*/

autowatch = 1;
inlets = 3;
outlets = 3;

var N = 16;
var coherence = 0.0;
var entropy = 0.0;
var depth = 0.0;
var baseGain = 0.03;
var dynamicSpan = 0.09;
var entropyDamping = 0.60;
var hardCap = 0.15;

function numeric(value, fallback) {
    var converted = Number(value);
    return isFinite(converted) ? converted : fallback;
}

function clip(value, low, high) {
    return Math.max(low, Math.min(high, numeric(value, low)));
}

function emitGain() {
    var organization = 1.0 - entropyDamping * entropy;
    var gain = baseGain
        + depth * dynamicSpan * coherence * organization;
    var values = new Array(N);
    var index;

    gain = clip(gain, 0.0, hardCap);
    for (index = 0; index < N; index++) {
        values[index] = gain;
    }

    outlet(0, values);
    outlet(1, gain);
    outlet(2, ["feedback_gain", gain, "coherence", coherence,
        "entropy", entropy, "depth", depth]);
}

function msg_int(value) {
    msg_float(value);
}

function msg_float(value) {
    if (inlet === 0) {
        coherence = clip(value, 0.0, 1.0);
    } else if (inlet === 1) {
        entropy = clip(value, 0.0, 1.0);
    } else {
        depth = clip(value, 0.0, 1.0);
    }
    emitGain();
}

function bang() {
    emitGain();
}

function baseline(value) {
    baseGain = clip(value, 0.0, hardCap);
    emitGain();
}

function span(value) {
    dynamicSpan = clip(value, 0.0, hardCap);
    emitGain();
}

function damping(value) {
    entropyDamping = clip(value, 0.0, 1.0);
    emitGain();
}

function cap(value) {
    hardCap = clip(value, 0.01, 0.30);
    emitGain();
}

function anything() {
    outlet(2, ["error", "unknown_message", messagename]
        .concat(arrayfromargs(arguments)));
}
