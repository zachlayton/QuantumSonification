// qmw_density_field_to_resonator.js
//
// Max js helper for four q-labelled quantum resonator Gen~ voices.
//
// Inlets for bare OSC-route list outputs:
//   inlet 0: magnitude list -> m0..m15
//   inlet 1: phase list     -> ph0..ph15
//   inlet 2: speed list     -> s0..s15
//   inlet 3: harmonic/gap list -> h0..h15
//
// This parser deliberately does not emit b0..b15 or im0..im15.

autowatch = 1;
inlets = 4;
outlets = 4;

var NUM_VOICES = 4;
var NUM_BASIS = 16;

var listPrefixes = {
    magnitude: "m",
    phase: "ph",
    speed: "s",
    harmonic: "h",
    harmonics: "h",
    gap: "h"
};

var scalarParams = {
    purity: true,
    entropy: true,
    coherence: true,
    amp: true,
    default_freq: true,
    attack_ms: true,
    slow_decay_ms: true,
    fast_decay_ms: true,
    magnitude_smooth_ms: true,
    phase_smooth_ms: true,
    brightness: true,
    mix_voices: true,
    output_ceiling: true
};

var inletNames = ["magnitude", "phase", "speed", "harmonics"];

function anything() {
    dispatch([messagename].concat(arrayfromargs(arguments)));
}

function list() {
    var args = arrayfromargs(arguments);
    if (args.length > 0 && isNumeric(args[0])) {
        dispatch([inletNames[inlet]].concat(args));
        return;
    }
    dispatch(args);
}

function dispatch(tokens) {
    if (!tokens || tokens.length < 1) {
        return;
    }

    var first = String(tokens[0]);
    var voice = voiceIndex(first);
    if (voice >= 0) {
        dispatchToVoice(voice, tokens.slice(1));
        return;
    }

    for (var i = 0; i < NUM_VOICES; i++) {
        dispatchToVoice(i, tokens);
    }
}

function dispatchToVoice(voice, tokens) {
    if (!tokens || tokens.length < 1) {
        return;
    }

    var name = String(tokens[0]);
    var values = tokens.slice(1);

    if (listPrefixes.hasOwnProperty(name)) {
        emitListParams(voice, listPrefixes[name], values);
        return;
    }

    if (scalarParams.hasOwnProperty(name) && values.length >= 1) {
        outlet(voice, name, sanitizeNumber(values[0], 0));
    }
}

function emitListParams(voice, prefix, values) {
    var count = Math.min(NUM_BASIS, values.length);
    for (var i = 0; i < count; i++) {
        outlet(voice, prefix + i, sanitizeNumber(values[i], 0));
    }
}

function test() {
    for (var voice = 0; voice < NUM_VOICES; voice++) {
        emitTestVoice(voice);
    }
}

function test0() {
    emitTestVoice(0);
}

function test1() {
    emitTestVoice(1);
}

function test2() {
    emitTestVoice(2);
}

function test3() {
    emitTestVoice(3);
}

function emitTestVoice(voice) {
    post("qmw_density_field_to_resonator: outlet " + voice + " test\n");
    outlet(voice, "amp", 0.2);
    outlet(voice, "default_freq", 55 * (voice + 1));
    for (var i = 0; i < NUM_BASIS; i++) {
        outlet(voice, "m" + i, 1);
        outlet(voice, "ph" + i, 0);
        outlet(voice, "s" + i, 0);
        outlet(voice, "h" + i, i + 1);
    }
}

function voiceIndex(name) {
    if (name === "q0") {
        return 0;
    }
    if (name === "q1") {
        return 1;
    }
    if (name === "q2") {
        return 2;
    }
    if (name === "q3") {
        return 3;
    }
    return -1;
}

function sanitizeNumber(value, fallback) {
    var number = Number(value);
    if (!isFinite(number)) {
        return fallback;
    }
    return number;
}

function isNumeric(value) {
    return isFinite(Number(value));
}
// qmw_density_field_to_resonator.js
//
// Max js helper for four q-labelled quantum resonator Gen~ voices.
//
// Inlets for bare OSC-route list outputs:
//   inlet 0: magnitude list -> m0..m15
//   inlet 1: phase list     -> ph0..ph15
//   inlet 2: speed list     -> s0..s15
//   inlet 3: harmonic/gap list -> h0..h15
//
// This parser deliberately does not emit b0..b15 or im0..im15.

autowatch = 1;
inlets = 4;
outlets = 4;

var NUM_VOICES = 4;
var NUM_BASIS = 16;

var listPrefixes = {
    magnitude: "m",
    phase: "ph",
    speed: "s",
    harmonic: "h",
    harmonics: "h",
    gap: "h"
};

var scalarParams = {
    purity: true,
    entropy: true,
    coherence: true,
    amp: true,
    default_freq: true,
    attack_ms: true,
    slow_decay_ms: true,
    fast_decay_ms: true,
    magnitude_smooth_ms: true,
    phase_smooth_ms: true,
    brightness: true,
    mix_voices: true,
    output_ceiling: true
};

var inletNames = ["magnitude", "phase", "speed", "harmonics"];

function anything() {
    dispatch([messagename].concat(arrayfromargs(arguments)));
}

function list() {
    var args = arrayfromargs(arguments);
    if (args.length > 0 && isNumeric(args[0])) {
        dispatch([inletNames[inlet]].concat(args));
        return;
    }
    dispatch(args);
}

function dispatch(tokens) {
    if (!tokens || tokens.length < 1) {
        return;
    }

    var first = String(tokens[0]);
    var voice = voiceIndex(first);
    if (voice >= 0) {
        dispatchToVoice(voice, tokens.slice(1));
        return;
    }

    for (var i = 0; i < NUM_VOICES; i++) {
        dispatchToVoice(i, tokens);
    }
}

function dispatchToVoice(voice, tokens) {
    if (!tokens || tokens.length < 1) {
        return;
    }

    var name = String(tokens[0]);
    var values = tokens.slice(1);

    if (listPrefixes.hasOwnProperty(name)) {
        emitListParams(voice, listPrefixes[name], values);
        return;
    }

    if (scalarParams.hasOwnProperty(name) && values.length >= 1) {
        outlet(voice, name, sanitizeNumber(values[0], 0));
    }
}

function emitListParams(voice, prefix, values) {
    var count = Math.min(NUM_BASIS, values.length);
    for (var i = 0; i < count; i++) {
        outlet(voice, prefix + i, sanitizeNumber(values[i], 0));
    }
}

function test() {
    for (var voice = 0; voice < NUM_VOICES; voice++) {
        emitTestVoice(voice);
    }
}

function test0() {
    emitTestVoice(0);
}

function test1() {
    emitTestVoice(1);
}

function test2() {
    emitTestVoice(2);
}

function test3() {
    emitTestVoice(3);
}

function emitTestVoice(voice) {
    post("qmw_density_field_to_resonator: outlet " + voice + " test\n");
    outlet(voice, "amp", 0.2);
    outlet(voice, "default_freq", 55 * (voice + 1));
    for (var i = 0; i < NUM_BASIS; i++) {
        outlet(voice, "m" + i, 1);
        outlet(voice, "ph" + i, 0);
        outlet(voice, "s" + i, 0);
        outlet(voice, "h" + i, i + 1);
    }
}

function voiceIndex(name) {
    if (name === "q0") {
        return 0;
    }
    if (name === "q1") {
        return 1;
    }
    if (name === "q2") {
        return 2;
    }
    if (name === "q3") {
        return 3;
    }
    return -1;
}

function sanitizeNumber(value, fallback) {
    var number = Number(value);
    if (!isFinite(number)) {
        return fallback;
    }
    return number;
}

function isNumeric(value) {
    return isFinite(Number(value));
}
