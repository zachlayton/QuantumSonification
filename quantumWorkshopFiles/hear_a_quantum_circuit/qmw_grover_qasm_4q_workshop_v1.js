// Four-qubit Grover rehearsal and OpenQASM 2 generator for Max.
//
// This is the workshop-scale version of ExactGroverStatevectorEngine:
// every preview applies the marked-state sign flip and 2*mean-state
// diffusion to the actual 16 amplitudes. It does not use a fitted curve.
//
// Inlet:
//   target 0..15        choose the marked basis state
//   preview 0..3        update the local 16-overtone display only
//   send 3              update locally and send QASM through the existing bridge
//
// Outlets:
//   0 QASM, 1 probabilities, 2 status, 3 marked-state probability

autowatch = 1;
inlets = 1;
outlets = 4;

var NUM_QUBITS = 4;
var DIMENSION = 16;
var markedTarget = 9; // |1001>, partial 10

var MCX_DEFINITION = [
    "gate mcx q0,q1,q2,q3 {",
    "h q3;",
    "u1(pi/8) q0; u1(pi/8) q1; u1(pi/8) q2; u1(pi/8) q3;",
    "cx q0,q1; u1(-pi/8) q1; cx q0,q1;",
    "cx q1,q2; u1(-pi/8) q2; cx q0,q2; u1(pi/8) q2;",
    "cx q1,q2; u1(-pi/8) q2; cx q0,q2;",
    "cx q2,q3; u1(-pi/8) q3; cx q1,q3; u1(pi/8) q3;",
    "cx q2,q3; u1(-pi/8) q3; cx q0,q3; u1(pi/8) q3;",
    "cx q2,q3; u1(-pi/8) q3; cx q1,q3; u1(pi/8) q3;",
    "cx q2,q3; u1(-pi/8) q3; cx q0,q3;",
    "h q3;",
    "}"
].join(" ");

function clampInteger(value, low, high) {
    var number = Math.floor(Number(value));
    if (!isFinite(number)) number = low;
    return Math.max(low, Math.min(high, number));
}

function binary4(value) {
    var text = Number(value).toString(2);
    while (text.length < 4) text = "0" + text;
    return text;
}

function target(value) {
    markedTarget = clampInteger(value, 0, DIMENSION - 1);
    preview(0);
}

function exactProbabilities(iterations) {
    var amplitudes = [];
    var amplitude = 1.0 / Math.sqrt(DIMENSION);
    var i, step, mean;
    for (i = 0; i < DIMENSION; i++) amplitudes.push(amplitude);

    for (step = 0; step < iterations; step++) {
        // Phase oracle: the marked amplitude alone changes sign.
        amplitudes[markedTarget] *= -1.0;
        mean = 0.0;
        for (i = 0; i < DIMENSION; i++) mean += amplitudes[i];
        mean /= DIMENSION;
        // Diffusion: reflect every amplitude about the current mean.
        for (i = 0; i < DIMENSION; i++) {
            amplitudes[i] = 2.0 * mean - amplitudes[i];
        }
    }

    var probabilities = [];
    for (i = 0; i < DIMENSION; i++) {
        probabilities.push(amplitudes[i] * amplitudes[i]);
    }
    return probabilities;
}

function publishLocal(iterations, action) {
    var probabilities = exactProbabilities(iterations);
    var markedProbability = probabilities[markedTarget];
    outlet(1, probabilities);
    outlet(3, markedProbability);
    outlet(
        2,
        "set",
        action + " · target |" + binary4(markedTarget) + "〉 · iteration "
            + iterations + " · marked " + (100.0 * markedProbability).toFixed(2) + "%"
    );
}

function preview(value) {
    var iterations = clampInteger(value, 0, 3);
    publishLocal(iterations, "LOCAL");
}

function run(value) {
    preview(value);
}

function send(value) {
    var iterations = clampInteger(value, 0, 3);
    publishLocal(iterations, "SENDING QASM");
    outlet(0, "qasm", buildQasm(iterations));
}

function buildQasm(iterations) {
    var statements = [
        "OPENQASM 2.0;",
        "include \"qelib1.inc\";",
        MCX_DEFINITION,
        "qreg q[4];",
        "h q[0]; h q[1]; h q[2]; h q[3];"
    ];
    var flipZeros = [];
    var qubit, step;
    for (qubit = 0; qubit < NUM_QUBITS; qubit++) {
        if (((markedTarget >> qubit) & 1) === 0) {
            flipZeros.push("x q[" + qubit + "];");
        }
    }
    var flips = flipZeros.join(" ");

    for (step = 0; step < iterations; step++) {
        if (flips.length) statements.push(flips);
        statements.push("h q[3]; mcx q[0],q[1],q[2],q[3]; h q[3];");
        if (flips.length) statements.push(flips);
        statements.push([
            "h q[0]; h q[1]; h q[2]; h q[3];",
            "x q[0]; x q[1]; x q[2]; x q[3];",
            "h q[3]; mcx q[0],q[1],q[2],q[3]; h q[3];",
            "x q[0]; x q[1]; x q[2]; x q[3];",
            "h q[0]; h q[1]; h q[2]; h q[3];"
        ].join(" "));
    }
    return statements.join(" ");
}

function loadbang() {
    preview(0);
}
