/*
    qmw_feedback_branch_controls16_v1.js

    Control-rate preparation for the sixteen complex resonator-feedback lanes.

    inlet 0: sixteen phase angles in radians, or control messages
    inlet 1: sixteen non-negative feedback gains
    inlet 2: sixteen feedback delay times in milliseconds

    outlet 0: phase-radians list
    outlet 1: safety-clamped feedback-gain list
    outlet 2: safety-clamped delay-time list
    outlet 3: status and validation messages

    No motion is generated here. Every change must arrive as quantum data or
    an explicit operator-control message.
*/

autowatch = 1;
inlets = 3;
outlets = 4;

setinletassist(0, "16 quantum phase values in radians, or control messages");
setinletassist(1, "16 feedback-gain values");
setinletassist(2, "16 feedback-delay values in milliseconds");
setoutletassist(0, "phase in radians, 16 values");
setoutletassist(1, "clamped feedback gains, 16 values");
setoutletassist(2, "clamped delay times in milliseconds, 16 values");
setoutletassist(3, "status and validation messages");

var N = 16;
var phases = new Array(N);
var gains = new Array(N);
var delays = new Array(N);
var gainCeiling = 0.92;
var minimumDelayMs = 2.0;
var maximumDelayMs = 2000.0;

resetArrays();

function numeric(value) {
    var converted = Number(value);
    return isFinite(converted) ? converted : 0.0;
}

function clamp(value, minimum, maximum) {
    return Math.max(minimum, Math.min(maximum, numeric(value)));
}

function resetArrays() {
    var index;
    for (index = 0; index < N; index++) {
        phases[index] = 0.0;
        gains[index] = 0.0;
        delays[index] = 10.0;
    }
}

function requireSixteen(values, label) {
    if (values.length !== N) {
        outlet(3, ["error", label, "expected", N, "received", values.length]);
        post("qmw feedback16: " + label + " requires exactly " + N
            + " values; received " + values.length + "\n");
        return 0;
    }
    return 1;
}

function emitPhases() {
    var outputPhases = new Array(N);
    var index;

    for (index = 0; index < N; index++) {
        outputPhases[index] = phases[index];
    }

    outlet(0, outputPhases);
}

function emitGains() {
    var safeGains = new Array(N);
    var index;

    for (index = 0; index < N; index++) {
        gains[index] = clamp(gains[index], 0.0, gainCeiling);
        safeGains[index] = gains[index];
    }

    outlet(1, safeGains);
}

function emitDelays() {
    var safeDelays = new Array(N);
    var index;

    for (index = 0; index < N; index++) {
        delays[index] = clamp(delays[index], minimumDelayMs, maximumDelayMs);
        safeDelays[index] = delays[index];
    }

    outlet(2, safeDelays);
}

function emitAll(reason) {
    emitPhases();
    emitGains();
    emitDelays();
    emitStatus(reason);
}

function setPhases(values) {
    var index;
    if (!requireSixteen(values, "phase")) {
        return;
    }
    for (index = 0; index < N; index++) {
        phases[index] = nearestEquivalentPhase(phases[index], numeric(values[index]));
    }
    emitPhases();
    emitStatus("phase");
}

function setGains(values) {
    var index;
    if (!requireSixteen(values, "gain")) {
        return;
    }
    for (index = 0; index < N; index++) {
        gains[index] = clamp(values[index], 0.0, gainCeiling);
    }
    emitGains();
    emitStatus("gain");
}

function setDelays(values) {
    var index;
    if (!requireSixteen(values, "delay")) {
        return;
    }
    for (index = 0; index < N; index++) {
        delays[index] = clamp(values[index], minimumDelayMs, maximumDelayMs);
    }
    emitDelays();
    emitStatus("delay");
}

function list() {
    var values = arrayfromargs(arguments);
    if (inlet === 0) {
        setPhases(values);
    } else if (inlet === 1) {
        setGains(values);
    } else {
        setDelays(values);
    }
}

function phase() {
    setPhases(arrayfromargs(arguments));
}

function gain() {
    setGains(arrayfromargs(arguments));
}

function delay() {
    setDelays(arrayfromargs(arguments));
}

function initialize() {
    resetArrays();
    emitAll("initialize");
}

function safe() {
    var index;
    for (index = 0; index < N; index++) {
        gains[index] = 0.0;
    }
    emitGains();
    emitStatus("safe");
}

function ceiling(value) {
    gainCeiling = clamp(value, 0.0, 0.98);
    emitGains();
    emitStatus("ceiling");
}

function delayrange(minimum, maximum) {
    var newMinimum = clamp(minimum, 0.1, 2000.0);
    var newMaximum = clamp(maximum, newMinimum, 10000.0);

    minimumDelayMs = newMinimum;
    maximumDelayMs = newMaximum;
    emitDelays();
    emitStatus("delayrange");
}

function tune() {
    var values = arrayfromargs(arguments);
    var fundamental;
    var ratio;
    var index;

    if (values.length !== N + 1) {
        outlet(3, ["error", "tune", "expected", N + 1, "received", values.length]);
        return;
    }

    fundamental = Math.max(0.001, numeric(values[0]));
    for (index = 0; index < N; index++) {
        ratio = Math.max(0.001, numeric(values[index + 1]));
        delays[index] = clamp(1000.0 / (fundamental * ratio),
            minimumDelayMs, maximumDelayMs);
    }

    emitDelays();
    emitStatus("tune");
}

function setphase(indexValue, value) {
    var index = Math.floor(numeric(indexValue));
    if (!validIndex(index)) {
        return;
    }
    phases[index] = nearestEquivalentPhase(phases[index], numeric(value));
    emitPhases();
    emitStatus("setphase");
}

function nearestEquivalentPhase(current, target) {
    var delta = Math.atan2(Math.sin(target - current), Math.cos(target - current));
    return current + delta;
}

function setgain(indexValue, value) {
    var index = Math.floor(numeric(indexValue));
    if (!validIndex(index)) {
        return;
    }
    gains[index] = clamp(value, 0.0, gainCeiling);
    emitGains();
    emitStatus("setgain");
}

function setdelay(indexValue, value) {
    var index = Math.floor(numeric(indexValue));
    if (!validIndex(index)) {
        return;
    }
    delays[index] = clamp(value, minimumDelayMs, maximumDelayMs);
    emitDelays();
    emitStatus("setdelay");
}

function validIndex(index) {
    if (index < 0 || index >= N) {
        outlet(3, ["error", "index_out_of_range", index]);
        return 0;
    }
    return 1;
}

function emitStatus(reason) {
    var gainMaximum = 0.0;
    var delayMinimum = maximumDelayMs;
    var delayMaximum = minimumDelayMs;
    var phaseMinimum = phases[0];
    var phaseMaximum = phases[0];
    var index;

    for (index = 0; index < N; index++) {
        gainMaximum = Math.max(gainMaximum, gains[index]);
        delayMinimum = Math.min(delayMinimum, delays[index]);
        delayMaximum = Math.max(delayMaximum, delays[index]);
        phaseMinimum = Math.min(phaseMinimum, phases[index]);
        phaseMaximum = Math.max(phaseMaximum, phases[index]);
    }

    outlet(3, [
        "feedback_status", reason,
        "gain_max", gainMaximum,
        "ceiling", gainCeiling,
        "delay_min_ms", delayMinimum,
        "delay_max_ms", delayMaximum,
        "phase_span", phaseMaximum - phaseMinimum
    ]);
}

function status() {
    emitStatus("query");
}

function anything() {
    outlet(3, ["error", "unknown_message", messagename].concat(arrayfromargs(arguments)));
}
