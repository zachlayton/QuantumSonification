/*
    qmw_harmonic_delay_list16_v1.js

    Converts the engine's ratio field into sixteen synchronized delay times:
        effective_ratio[i] = mix(engine_ratio[i], i + 1, harmonic_lock)
        delay[i] = 1000 / (fundamental * effective_ratio[i]) milliseconds

    inlet 0: fundamental frequency, bang, or range control
    inlet 1: engine harmonic/gap ratio list[16]
    inlet 2: harmonic lock 0..1

    outlet 0: list of 16 delay times for feedback inlet 6
    outlet 1: status
*/

autowatch = 1;
inlets = 3;
outlets = 2;

var N = 16;
var minimumDelayMs = 1.0;
var maximumDelayMs = 2000.0;
var currentFundamental = 55.0;
var harmonicLock = 0.92;
var engineRatios = new Array(N);
var initialIndex;

for (initialIndex = 0; initialIndex < N; initialIndex++) {
    engineRatios[initialIndex] = initialIndex + 1;
}

function numeric(value, fallback) {
    var converted = Number(value);
    return isFinite(converted) ? converted : fallback;
}

function outputDelays(value) {
    var frequency = Math.max(0.001, numeric(value, currentFundamental));
    var delays = new Array(N);
    var index;

    currentFundamental = frequency;
    for (index = 0; index < N; index++) {
        var exactHarmonic = index + 1;
        var effectiveRatio = engineRatios[index] * (1.0 - harmonicLock)
            + exactHarmonic * harmonicLock;
        delays[index] = Math.max(
            minimumDelayMs,
            Math.min(
                maximumDelayMs,
                1000.0 / (frequency * Math.max(0.01, effectiveRatio))
            )
        );
    }

    outlet(0, delays);
    outlet(1, ["engine_delays", frequency, "lock", harmonicLock,
        "count", N]);
}

function msg_int(value) {
    if (inlet === 0) {
        outputDelays(value);
    } else if (inlet === 2) {
        harmonicLock = Math.max(0.0, Math.min(1.0, numeric(value, harmonicLock)));
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
        outlet(1, ["error", "engine_ratios", "expected", N,
            "received", values.length]);
        return;
    }
    for (index = 0; index < N; index++) {
        engineRatios[index] = Math.max(0.01, numeric(values[index], index + 1));
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

function anything() {
    outlet(1, ["error", "unknown_message", messagename]
        .concat(arrayfromargs(arguments)));
}
