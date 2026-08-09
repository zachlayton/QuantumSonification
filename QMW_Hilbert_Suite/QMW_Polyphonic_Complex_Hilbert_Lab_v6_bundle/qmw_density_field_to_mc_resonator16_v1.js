/*
    qmw_density_field_to_mc_resonator16_v1.js

    Converts the conductor's density-field lists into named Gen parameter
    messages for one sixteen-channel mc.gen~ resonator.

    inlet 0: magnitude[16]
    inlet 1: phase[16]
    inlet 2: speed[16]
    inlet 3: harmonics[16]
    inlet 4: purity scalar
    inlet 5: entropy scalar
    inlet 6: coherence scalar

    outlet 0: named Gen parameter messages
    outlet 1: validation/status
*/

autowatch = 1;
inlets = 7;
outlets = 2;

var N = 16;
var names = ["magnitude", "phase", "speed", "harmonics",
    "purity", "entropy", "coherence"];
var prefixes = ["m", "ph", "s", "h"];

function numeric(value, fallback) {
    var converted = Number(value);
    return isFinite(converted) ? converted : fallback;
}

function clip(value, low, high) {
    return Math.max(low, Math.min(high, numeric(value, low)));
}

function acceptVector(values, vectorIndex) {
    var index;
    var value;
    if (values.length !== N) {
        outlet(1, ["error", names[vectorIndex], "expected", N,
            "received", values.length]);
        return;
    }

    for (index = 0; index < N; index++) {
        value = numeric(values[index], 0.0);
        if (vectorIndex === 0) {
            value = clip(value, 0.0, 1.0);
        } else if (vectorIndex === 2) {
            value = clip(value, -1.0, 1.0);
        } else if (vectorIndex === 3) {
            value = Math.max(0.01, value);
        }
        outlet(0, prefixes[vectorIndex] + index, value);
    }
    outlet(1, ["received", names[vectorIndex], N]);
}

function acceptScalar(value, scalarIndex) {
    var name = names[scalarIndex];
    outlet(0, name, clip(value, 0.0, 1.0));
    outlet(1, ["received", name]);
}

function list() {
    var values = arrayfromargs(arguments);
    if (inlet < 4) {
        acceptVector(values, inlet);
    } else if (values.length > 0) {
        acceptScalar(values[0], inlet);
    }
}

function msg_int(value) {
    if (inlet >= 4) {
        acceptScalar(value, inlet);
    }
}

function msg_float(value) {
    if (inlet >= 4) {
        acceptScalar(value, inlet);
    }
}

function safe() {
    var index;
    for (index = 0; index < N; index++) {
        outlet(0, "m" + index, 0.0);
        outlet(0, "ph" + index, 0.0);
        outlet(0, "s" + index, 0.0);
        outlet(0, "h" + index, index + 1);
    }
    outlet(0, "purity", 1.0);
    outlet(0, "entropy", 0.0);
    outlet(0, "coherence", 0.0);
    outlet(1, ["safe", 1]);
}

function test() {
    safe();
    outlet(0, "m0", 1.0);
    outlet(1, ["test", "basis", 0]);
}

function anything() {
    outlet(1, ["error", "unknown_message", messagename]
        .concat(arrayfromargs(arguments)));
}
