// Small backstage evaluator for the reused four-qubit QAC JSUI command stream.
// It supports only the gates exposed by that JSUI: H, X, Y, Z, S, T, and CX.
// This is a workshop sound adapter, not a replacement for the QMW/Qiskit engine.

autowatch = 1;
inlets = 1;
outlets = 2; // 16 probabilities, status

var SIZE = 16;
var re = [];
var im = [];
var gateCount = 0;

resetState();

function QuantumCircuit() {
    resetState();
}

function qc() {
    var args = arrayfromargs(arguments);
    if (args.length < 2) return;
    var gate = String(args[0]).toLowerCase();
    if (gate === "cx" && args.length >= 3) {
        applyCx(Number(args[1]), Number(args[2]));
    } else {
        applyOneQubit(gate, Number(args[1]));
    }
    gateCount++;
}

function Simulator() {
    outputProbabilities();
}

function sim() {
    // The QAC programmer asks for QASM after Simulator. The audio state has
    // already been emitted by Simulator, so no duplicate event is needed.
}

function clear_audio() {
    var probabilities = [];
    for (var i = 0; i < SIZE; i++) {
        probabilities.push(0);
    }
    outlet(0, probabilities);
    outlet(1, "set", "Circuit cleared -> audio off");
}

function resetState() {
    re = [];
    im = [];
    for (var i = 0; i < SIZE; i++) {
        re.push(i === 0 ? 1 : 0);
        im.push(0);
    }
    gateCount = 0;
}

function applyOneQubit(gate, qubit) {
    if (qubit < 0 || qubit > 3) return;
    var mask = 1 << qubit;
    var invSqrt2 = 0.7071067811865476;
    for (var base = 0; base < SIZE; base++) {
        if ((base & mask) !== 0) continue;
        var paired = base | mask;
        var ar = re[base], ai = im[base];
        var br = re[paired], bi = im[paired];

        if (gate === "h") {
            re[base] = (ar + br) * invSqrt2;
            im[base] = (ai + bi) * invSqrt2;
            re[paired] = (ar - br) * invSqrt2;
            im[paired] = (ai - bi) * invSqrt2;
        } else if (gate === "x") {
            re[base] = br;
            im[base] = bi;
            re[paired] = ar;
            im[paired] = ai;
        } else if (gate === "y") {
            re[base] = bi;
            im[base] = -br;
            re[paired] = -ai;
            im[paired] = ar;
        } else if (gate === "z") {
            re[paired] = -br;
            im[paired] = -bi;
        } else if (gate === "s") {
            re[paired] = -bi;
            im[paired] = br;
        } else if (gate === "t") {
            var c = Math.SQRT1_2;
            re[paired] = c * (br - bi);
            im[paired] = c * (br + bi);
        }
    }
}

function applyCx(control, target) {
    if (
        control < 0 || control > 3 ||
        target < 0 || target > 3 ||
        control === target
    ) return;
    var controlMask = 1 << control;
    var targetMask = 1 << target;
    for (var index = 0; index < SIZE; index++) {
        if ((index & controlMask) === 0 || (index & targetMask) !== 0) continue;
        var paired = index | targetMask;
        var nextRe = re[index], nextIm = im[index];
        re[index] = re[paired];
        im[index] = im[paired];
        re[paired] = nextRe;
        im[paired] = nextIm;
    }
}

function outputProbabilities() {
    var probabilities = [];
    var total = 0;
    var active = 0;
    for (var i = 0; i < SIZE; i++) {
        var probability = re[i] * re[i] + im[i] * im[i];
        probabilities.push(probability);
        total += probability;
        if (probability > 0.000001) active++;
    }
    if (total > 0) {
        for (i = 0; i < SIZE; i++) probabilities[i] /= total;
    }
    outlet(0, probabilities);
    outlet(
        1,
        "set",
        gateCount + " gates -> " + active + " active overtone"
            + (active === 1 ? "" : "s")
    );
}
