/*
    qmw_harmonic_delay_list16_v2.js

    Pitch-stable feedback-delay tuning shared with the v4 harmonic resonator.

    inlet 0: fundamental frequency, bang, or range control
    inlet 1: engine Hamiltonian-gap ratio list[16]
    inlet 2: harmonic lock 0..1 (1 = exact harmonics)
    inlet 3: raw quantum spectrum morph 0..1

    Normal Harmonic Lock motion is bounded to +/-50 cents. Raw Hamiltonian
    ratios are available only through the separate spectrum morph control.

    outlet 0: list of 16 delay times for feedback inlet 6
    outlet 1: status
*/

autowatch = 1;
inlets = 4;
outlets = 2;

var N = 16;
var minimumDelayMs = 1.0;
var maximumDelayMs = 2000.0;
var currentFundamental = 55.0;
var harmonicLock = 1.0;
var quantumSpectrumMorph = 0.0;
var maximumDetuneCents = 50.0;
var engineRatios = new Array(N);
var initialIndex;

for (initialIndex = 0; initialIndex < N; initialIndex++) {
    engineRatios[initialIndex] = initialIndex + 1;
}

function numeric(value, fallback) {
    var converted = Number(value);
    return isFinite(converted) ? converted : fallback;
}

function clip(value, low, high) {
    return Math.max(low, Math.min(high, numeric(value, low)));
}

function effectiveRatio(index) {
    var harmonic = index + 1;
    if (index === 0) {
        return 1.0;
    }

    var quantum = Math.max(0.01, engineRatios[index]);
    var deviationCents = 1200.0 * Math.log(quantum / harmonic) / Math.LN2;
    var boundedCents = clip(
        deviationCents,
        -maximumDetuneCents,
        maximumDetuneCents
    );
    var boundedQuantum = harmonic * Math.pow(2.0, boundedCents / 1200.0);
    var locked = boundedQuantum * (1.0 - harmonicLock)
        + harmonic * harmonicLock;
    return locked * (1.0 - quantumSpectrumMorph)
        + quantum * quantumSpectrumMorph;
}

function outputDelays(value) {
    var frequency = Math.max(0.001, numeric(value, currentFundamental));
    var delays = new Array(N);
    var index;

    currentFundamental = frequency;
    for (index = 0; index < N; index++) {
        delays[index] = clip(
            1000.0 / (frequency * Math.max(0.01, effectiveRatio(index))),
            minimumDelayMs,
            maximumDelayMs
        );
    }

    outlet(0, delays);
    outlet(1, [
        "engine_delays",
        frequency,
        "lock",
        harmonicLock,
        "spectrum_morph",
        quantumSpectrumMorph,
        "detune_cents",
        maximumDetuneCents,
        "count",
        N
    ]);
}

function msg_int(value) {
    if (inlet === 0) {
        outputDelays(value);
    } else if (inlet === 2) {
        harmonicLock = clip(value, 0.0, 1.0);
        outputDelays(currentFundamental);
    } else if (inlet === 3) {
        quantumSpectrumMorph = clip(value, 0.0, 1.0);
        outputDelays(currentFundamental);
    }
}

function msg_float(value) {
    msg_int(value);
}

function list() {
    var values = arrayfromargs(arguments);
    var index;

    if (inlet !== 1) {
        outlet(1, ["error", "ratio_list_wrong_inlet", inlet]);
        return;
    }
    if (values.length !== N) {
        outlet(1, [
            "error",
            "engine_ratios",
            "expected",
            N,
            "received",
            values.length
        ]);
        return;
    }
    for (index = 0; index < N; index++) {
        engineRatios[index] = Math.max(
            0.01,
            numeric(values[index], index + 1)
        );
    }
    outputDelays(currentFundamental);
}

function bang() {
    outputDelays(currentFundamental);
}

function range(low, high) {
    minimumDelayMs = Math.max(0.1, numeric(low, minimumDelayMs));
    maximumDelayMs = Math.max(
        minimumDelayMs,
        numeric(high, maximumDelayMs)
    );
    outputDelays(currentFundamental);
}

function detunecents(value) {
    maximumDetuneCents = clip(value, 0.0, 50.0);
    outputDelays(currentFundamental);
}

function status() {
    outlet(1, [
        "status",
        "fundamental",
        currentFundamental,
        "lock",
        harmonicLock,
        "spectrum_morph",
        quantumSpectrumMorph,
        "detune_cents",
        maximumDetuneCents
    ]);
}

function anything() {
    outlet(1, ["error", "unknown_message", messagename]
        .concat(arrayfromargs(arguments)));
}
