autowatch = 1;
inlets = 1;
outlets = 5;

// outlet 0: MIDI [pitch velocity channel]
// outlet 1: probabilities [p0 p1]
// outlet 2: messages for bach.roll
// outlet 3: human-readable state
// outlet 4: Bloch vector [x y z] for neural timbre control

var bloch = [0.0, 0.0, 1.0];
var hamiltonian = [0.18, 0.11, 0.07];
var intervalMs = 160;
var stepIndex = 0;
var maxHistory = 64;
var t1Ms = 0.0;
var t2Ms = 0.0;
var measurementAxis = "Z";
var midiPitch0 = 60;
var midiPitch1 = 67;
var sourceMode = 0;

function loadbang() {
    outlet(1, [1.0, 0.0]);
    emitBloch();
    outlet(3, "ready");
    clear();
}

function hx(v) {
    hamiltonian[0] = Number(v);
}

function hy(v) {
    hamiltonian[1] = Number(v);
}

function hz(v) {
    hamiltonian[2] = Number(v);
}

function t1(v) {
    t1Ms = Math.max(0.0, Number(v));
}

function t2(v) {
    t2Ms = Math.max(0.0, Number(v));
}

function axis(v) {
    var candidate = String(v).toUpperCase();
    if (candidate === "X" || candidate === "Y" || candidate === "Z") {
        measurementAxis = candidate;
        outlet(3, "measurement axis " + measurementAxis);
    }
}

function state(x, y, z) {
    bloch = clampBloch([Number(x), Number(y), Number(z)]);
    emitState();
    outlet(3, "external state");
}

function conductorstate(x, y, z) {
    if (sourceMode !== 1) return;
    bloch = clampBloch([Number(x), Number(y), Number(z)]);
    emitState();
}

function pitches(p0, p1) {
    midiPitch0 = Math.max(0, Math.min(127, Math.round(Number(p0))));
    midiPitch1 = Math.max(0, Math.min(127, Math.round(Number(p1))));
}

function source(v) {
    sourceMode = Number(v) > 0 ? 1 : 0;
    outlet(3, sourceMode ? "source: CONDUCTOR qubit 0" : "source: LOCAL Hamiltonian");
}

function interval(v) {
    intervalMs = Math.max(20, Math.round(Number(v)));
}

function history(v) {
    maxHistory = Math.max(8, Math.round(Number(v)));
}

function tick() {
    if (stepIndex >= maxHistory) {
        clear();
    }

    // Explicit note-offs keep the output compatible with ordinary MIDI synths.
    midi(midiPitch0, 0, 1);
    midi(midiPitch1, 0, 2);

    if (sourceMode === 0) {
        evolveBloch();
        applyDecoherence();
    }

    var p0 = clamp01(0.5 * (1.0 + bloch[2]));
    var p1 = 1.0 - p0;

    // sqrt(probability) maps the quantum amplitude magnitude to MIDI velocity.
    var v0 = Math.round(127 * Math.sqrt(p0));
    var v1 = Math.round(127 * Math.sqrt(p1));

    if (v0 > 0) midi(midiPitch0, v0, 1);
    if (v1 > 0) midi(midiPitch1, v1, 2);

    outlet(1, [p0, p1]);
    emitBloch();
    appendToRoll(p0, p1, v0, v1);
    outlet(3, sourceMode ? "following CONDUCTOR qubit 0" :
        "evolving H=(" + rounded(hamiltonian[0]) + ", " + rounded(hamiltonian[1]) + ", " + rounded(hamiltonian[2]) + ")");
    stepIndex += 1;
}

function measure() {
    if (sourceMode === 1) {
        outlet(3, "CONDUCTOR has no remote measurement endpoint; switch to LOCAL");
        return;
    }
    var axisVector = axisToVector(measurementAxis);
    var expectation = dot(bloch, axisVector);
    var probabilityPlus = clamp01(0.5 * (1.0 + expectation));
    var result = Math.random() < probabilityPlus ? 1.0 : -1.0;

    bloch = [result * axisVector[0], result * axisVector[1], result * axisVector[2]];
    midi(midiPitch0, 0, 1);
    midi(midiPitch1, 0, 2);
    emitState();
    outlet(3, "MEASURED " + measurementAxis + (result > 0 ? "+" : "−") + "  p+=" + rounded(probabilityPlus));
}

function reset() {
    midi(midiPitch0, 0, 1);
    midi(midiPitch1, 0, 2);
    if (sourceMode === 1) {
        stepIndex = 0;
        clear();
        outlet(3, "roll cleared; CONDUCTOR state unchanged");
        return;
    }
    bloch = [0.0, 0.0, 1.0];
    stepIndex = 0;
    emitState();
    outlet(3, "reset |0>");
    clear();
}

function clear() {
    stepIndex = 0;
    outlet(2, "clear");
    outlet(2, ["domain", maxHistory * intervalMs]);
}

function stop() {
    midi(midiPitch0, 0, 1);
    midi(midiPitch1, 0, 2);
    outlet(3, "stopped");
}

function midi(pitch, velocity, channel) {
    outlet(0, [pitch, velocity, channel]);
}

function emitBloch() {
    // RAVE latents typically occupy roughly a standard-normal range.
    outlet(4, [2.5 * bloch[0], 2.5 * bloch[1], 2.5 * bloch[2]]);
}

function emitState() {
    var p0 = clamp01(0.5 * (1.0 + bloch[2]));
    outlet(1, [p0, 1.0 - p0]);
    emitBloch();
}

function evolveBloch() {
    // For H = 1/2(hx*sigma_x + hy*sigma_y + hz*sigma_z), the Bloch
    // vector rotates around h. Rodrigues' formula gives the exact step.
    var angle = norm(hamiltonian);
    if (angle < 1e-12) return;

    var axisVector = scaleVector(hamiltonian, 1.0 / angle);
    var cosine = Math.cos(angle);
    var sine = Math.sin(angle);
    var crossTerm = cross(axisVector, bloch);
    var projection = dot(axisVector, bloch);

    bloch = [
        bloch[0] * cosine + crossTerm[0] * sine + axisVector[0] * projection * (1.0 - cosine),
        bloch[1] * cosine + crossTerm[1] * sine + axisVector[1] * projection * (1.0 - cosine),
        bloch[2] * cosine + crossTerm[2] * sine + axisVector[2] * projection * (1.0 - cosine)
    ];
    bloch = clampBloch(bloch);
}

function applyDecoherence() {
    if (t2Ms > 0.0) {
        var transverseDecay = Math.exp(-intervalMs / t2Ms);
        bloch[0] *= transverseDecay;
        bloch[1] *= transverseDecay;
    }
    if (t1Ms > 0.0) {
        var longitudinalDecay = Math.exp(-intervalMs / t1Ms);
        bloch[2] = 1.0 - (1.0 - bloch[2]) * longitudinalDecay;
    }
    bloch = clampBloch(bloch);
}

function axisToVector(axisName) {
    if (axisName === "X") return [1.0, 0.0, 0.0];
    if (axisName === "Y") return [0.0, 1.0, 0.0];
    return [0.0, 0.0, 1.0];
}

function dot(a, b) {
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

function cross(a, b) {
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    ];
}

function norm(a) {
    return Math.sqrt(dot(a, a));
}

function scaleVector(a, scalar) {
    return [a[0] * scalar, a[1] * scalar, a[2] * scalar];
}

function clampBloch(candidate) {
    var length = norm(candidate);
    if (length <= 1.0 || length < 1e-12) return candidate;
    return scaleVector(candidate, 1.0 / length);
}

function clamp01(value) {
    return Math.max(0.0, Math.min(1.0, value));
}

function rounded(value) {
    return Math.round(value * 1000.0) / 1000.0;
}

function appendToRoll(p0, p1, v0, v1) {
    var onset = stepIndex * intervalMs;
    var duration = Math.max(20, Math.round(intervalMs * 0.85));

    if (v0 > 0) {
        outlet(2, ["addchord", 1, "[", onset, "[", 6000, duration, v0,
            "[", "slots", "[", 1, p0, "]", "[", 2, Math.atan2(bloch[1], bloch[0]), "]", "]", "]", "]"]);
    }
    if (v1 > 0) {
        outlet(2, ["addchord", 2, "[", onset, "[", 6700, duration, v1,
            "[", "slots", "[", 1, p1, "]", "[", 2, Math.atan2(bloch[1], bloch[0]), "]", "]", "]", "]"]);
    }
}
