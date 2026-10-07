// Workshop bridge: four qubits -> 16 basis probabilities -> 16 overtones.
//
// Input:
//   a list of 16 non-negative computational-basis probabilities
//   fundamental <Hz>
//
// Basis order follows the existing QMW/Qiskit convention:
//   index 0..15 = |q3 q2 q1 q0>
//
// Output 0 drives poly~. Output 1 updates the participant-facing status.
// Output 2 exposes the 16 pre-mix oscillator gains for individual meters.

autowatch = 1;
inlets = 1;
outlets = 3; // poly~ commands, status, 16 oscillator gains

var NUM_BASIS = 16;
var fundamentalHz = 55;

function list() {
    setProbabilities(arrayfromargs(arguments));
}

function probabilities() {
    setProbabilities(arrayfromargs(arguments));
}

function fundamental(value) {
    var hz = Math.max(20, Number(value) || 55);
    fundamentalHz = hz;
    for (var i = 0; i < NUM_BASIS; i++) {
        outlet(0, "target", i + 1);
        outlet(0, "frequency", fundamentalHz * (i + 1));
    }
    outlet(0, "target", 0);
    outlet(1, "set", "Fundamental " + formatNumber(hz) + " Hz · partial 16 = "
        + formatNumber(hz * 16) + " Hz");
}

function clear() {
    var values = [];
    for (var i = 0; i < NUM_BASIS; i++) {
        values.push(i === 0 ? 1 : 0);
    }
    setProbabilities(values);
}

function silence() {
    var amplitudes = [];
    for (var i = 0; i < NUM_BASIS; i++) {
        amplitudes.push(0);
    }
    outlet(0, "target", 0);
    outlet(0, "amp", 0);
    outlet(2, amplitudes);
    outlet(1, "set", "Audio off · build a circuit to hear it");
}

function setProbabilities(values) {
    var normalized = [];
    var total = 0;
    var i;

    for (i = 0; i < NUM_BASIS; i++) {
        var value = Math.max(0, Number(values[i]) || 0);
        normalized.push(value);
        total += value;
    }

    if (total <= 0) {
        silence();
        return;
    }

    var active = [];
    var amplitudes = [];
    for (i = 0; i < NUM_BASIS; i++) {
        var probability = normalized[i] / total;
        var amplitude = Math.sqrt(probability);
        amplitudes.push(amplitude);
        outlet(0, "target", i + 1);
        outlet(0, "frequency", fundamentalHz * (i + 1));
        outlet(0, "amp", amplitude);
        if (probability > 0.000001) {
            active.push("|" + binary4(i) + ">");
        }
    }

    outlet(0, "target", 0);
    outlet(2, amplitudes);
    outlet(
        1,
        "set",
        active.length <= 4
            ? "Active basis states: " + active.join("  ")
            : active.length + " active basis states"
    );
}

function binary4(value) {
    var text = Number(value).toString(2);
    while (text.length < 4) {
        text = "0" + text;
    }
    return text;
}

function formatNumber(value) {
    return Math.round(value * 100) / 100;
}
