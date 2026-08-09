// Four-qubit event engine: local reduced-state motion creates local events;
// pair correlations create coupling. No shared periodic LFO is used.
autowatch = 1;
inlets = 6;   // q0 q1 q2 q3, clock, correlation list
outlets = 4;

var TICK_SECONDS = 0.025;
var states = [];
var correlations = [0, 0, 0];
var tickCount = 0;

for (var i = 0; i < 4; i++) {
    states.push({
        x: 0, y: 0, z: 1, previousX: 0, previousY: 0, previousZ: 1,
        phase: i * 0.25, purity: 1, entropy: 0, speed: 0,
        activity: 0, accumulator: i * 0.19, seed: 1009 + i * 7919,
        pulse: 0
    });
}

function anything() {
    if (inlet < 4) updateQubit(inlet, messagename, arrayfromargs(arguments));
}

function list() {
    var values = arrayfromargs(arguments);
    if (inlet < 4) updateQubit(inlet, "list", values);
    else if (inlet === 5) updateCorrelations(values);
}

function bang() {
    if (inlet === 4) advance();
}

function updateQubit(index, selector, values) {
    selector = String(selector || "");
    if (selector.charAt(0) === "/") selector = selector.substring(1);
    if (selector === "list" && values.length && typeof values[0] === "string") {
        selector = String(values.shift());
        if (selector.charAt(0) === "/") selector = selector.substring(1);
    }
    var state = states[index];
    if (selector === "bloch" && values.length >= 3) {
        var nx = finite(values[0], state.x);
        var ny = finite(values[1], state.y);
        var nz = finite(values[2], state.z);
        var dx = nx - state.x, dy = ny - state.y, dz = nz - state.z;
        state.activity = clamp(Math.sqrt(dx * dx + dy * dy + dz * dz) * 3.5, 0, 1);
        state.previousX = state.x; state.previousY = state.y; state.previousZ = state.z;
        state.x = nx; state.y = ny; state.z = nz;
    } else if (selector === "phase" && values.length) {
        state.phase = wrap01(finite(values[0], 0) / 6.283185307179586);
    } else if (selector === "purity" && values.length) {
        state.purity = clamp(finite(values[0], 1), 0, 1);
    } else if (selector === "entropy" && values.length) {
        state.entropy = clamp(finite(values[0], 0) / 1.0, 0, 1);
    } else if ((selector === "speed" || selector === "velocity") && values.length) {
        state.speed = clamp(Math.abs(finite(values[0], 0)), 0, 1);
    }
}

function updateCorrelations(values) {
    if (values.length >= 9) {
        correlations[0] = meanAbs(values, 0);
        correlations[1] = meanAbs(values, 3);
        correlations[2] = meanAbs(values, 6);
    }
}

function meanAbs(values, offset) {
    return clamp((Math.abs(finite(values[offset], 0))
        + Math.abs(finite(values[offset + 1], 0))
        + Math.abs(finite(values[offset + 2], 0))) / 3, 0, 1);
}

function advance() {
    tickCount++;
    var fired = [0, 0, 0, 0];
    for (var i = 0; i < 4; i++) {
        var state = states[i];
        var transverse = clamp(Math.sqrt(state.x * state.x + state.y * state.y), 0, 1);
        var rate = 0.12 + 3.6 * state.activity + 1.4 * state.speed + 0.75 * transverse;
        state.accumulator += rate * TICK_SECONDS;
        state.pulse = 0;
        if (state.accumulator >= 1) {
            state.accumulator -= 1;
            var probability = clamp(0.2 + 0.5 * transverse + 0.3 * (1 - state.purity), 0, 1);
            if (random01(state) <= probability) fired[i] = 1;
        }
        state.activity *= 0.94;
    }

    // Correlation is the only source of cross-voice triggering.
    couple(fired, 0, 1, correlations[0]);
    couple(fired, 1, 2, correlations[1]);
    couple(fired, 2, 3, correlations[2]);

    for (var voice = 0; voice < 4; voice++) emitVoice(voice, fired[voice]);
}

function couple(fired, first, second, strength) {
    if (strength < 0.35) return;
    if (fired[first] && random01(states[second]) < strength) fired[second] = 1;
    else if (fired[second] && random01(states[first]) < strength) fired[first] = 1;
}

function emitVoice(index, fired) {
    var state = states[index];
    var transverse = clamp(Math.sqrt(state.x * state.x + state.y * state.y), 0, 1);
    var brightness = clamp(0.12 + 0.78 * transverse + 0.10 * state.purity, 0, 1);
    var noiseVariation = clamp(0.08 + 0.62 * transverse + 0.30 * state.activity, 0, 1);
    var duration = 300 + 2700 * (0.25 + 0.75 * state.purity) * (0.45 + 0.55 * transverse);
    outlet(index, "quantum_brightness", brightness);
    outlet(index, "quantum_noise_variation", noiseVariation);
    outlet(index, "quantum_event_decay_ms", duration);
    outlet(index, "quantum_pulse", fired ? 1 : 0);
}

function random01(state) {
    state.seed = (state.seed * 1664525 + 1013904223) % 4294967296;
    return state.seed / 4294967296;
}

function finite(value, fallback) {
    value = Number(value);
    return isFinite(value) ? value : fallback;
}

function clamp(value, low, high) { return Math.max(low, Math.min(high, value)); }
function wrap01(value) { value = value - Math.floor(value); return value < 0 ? value + 1 : value; }

function reset() {
    for (var i = 0; i < 4; i++) {
        states[i].accumulator = i * 0.19;
        states[i].activity = 0;
        states[i].seed = 1009 + i * 7919;
    }
}
