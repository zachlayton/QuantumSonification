// qmw_density_field_to_gen_qvoices.js
//
// Max js helper for four q-labelled Gen~ voices.
//
// Use five inlets for bare OSC-route list outputs:
//   inlet 0: real list
//   inlet 1: imag list
//   inlet 2: magnitude list
//   inlet 3: phase list
//   inlet 4: speed list
//
// Use four outlets, one per Gen~ voice:
//   outlet 0 -> q0 gen~
//   outlet 1 -> q1 gen~
//   outlet 2 -> q2 gen~
//   outlet 3 -> q3 gen~
//
// Incoming forms:
//   real <16 floats>        -> sends b0..b15 to all q voices
//   imag <16 floats>        -> sends im0..im15 to all q voices
//   magnitude <16 floats>   -> sends m0..m15 to all q voices
//   phase <16 floats>       -> sends ph0..ph15 to all q voices
//   speed <16 floats>       -> sends s0..s15 to all q voices
//   harmonic <16 floats>    -> sends h0..h15 to all q voices
//   gap <16 floats>         -> sends h0..h15 to all q voices
//
//   q0 real <16 floats>     -> sends b0..b15 only to q0
//   q1 magnitude <16 floats> -> sends m0..m15 only to q1
//
//   purity <float>          -> sends purity to all q voices
//   entropy <float>         -> sends entropy to all q voices
//   coherence <float>       -> sends coherence to all q voices
//
// Debug:
//   test                    -> emits simple params from all four outlets
//   test0                   -> emits simple params from outlet 0 only
//   test1                   -> emits simple params from outlet 1 only
//   test2                   -> emits simple params from outlet 2 only
//   test3                   -> emits simple params from outlet 3 only

autowatch = 1;
inlets = 5;
outlets = 4;

var NUM_VOICES = 4;
var NUM_BASIS = 16;

var listPrefixes = {
    real: "b",
    imag: "im",
    magnitude: "m",
    phase: "ph",
    speed: "s",
    harmonic: "h",
    gap: "h"
};

var scalarParams = {
    purity: true,
    entropy: true,
    coherence: true,
    amp: true,
    default_freq: true,
    value_smooth_ms: true,
    magnitude_smooth_ms: true,
    attack_ms: true,
    slow_decay_ms: true,
    fast_decay_ms: true,
    brightness: true,
    mix_voices: true,
    output_ceiling: true,
    fast_smooth_ms: true,
    slow_smooth_ms: true,
    phase_smooth_ms: true,
    phase_depth: true,
    imag_mix: true,
    max_drive: true,
    auto_level: true,
    drive: true
};

var inletNames = [
    "real",
    "imag",
    "magnitude",
    "phase",
    "speed"
];

function anything() {
    var args = arrayfromargs(arguments);
    dispatch([messagename].concat(args));
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

    dispatchToAll(tokens);
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
    post("qmw_density_field_to_gen_qvoices: outlet " + voice + " test\n");
    outlet(voice, "amp", 0.2);
    outlet(voice, "default_freq", 55 * (voice + 1));
    outlet(voice, "m0", 1);
    outlet(voice, "m1", 1);
    outlet(voice, "m2", 1);
    outlet(voice, "m3", 1);
    outlet(voice, "m4", 1);
    outlet(voice, "m5", 1);
    outlet(voice, "m6", 1);
    outlet(voice, "m7", 1);
    outlet(voice, "m8", 1);
    outlet(voice, "m9", 1);
    outlet(voice, "m10", 1);
    outlet(voice, "m11", 1);
    outlet(voice, "m12", 1);
    outlet(voice, "m13", 1);
    outlet(voice, "m14", 1);
    outlet(voice, "m15", 1);
    outlet(voice, "b0", 1);
    outlet(voice, "b1", 0.5);
    outlet(voice, "b2", 0);
    outlet(voice, "b3", -0.5);
    outlet(voice, "b4", -1);
    outlet(voice, "b5", -0.5);
    outlet(voice, "b6", 0);
    outlet(voice, "b7", 0.5);
    outlet(voice, "b8", 1);
    outlet(voice, "b9", 0.5);
    outlet(voice, "b10", 0);
    outlet(voice, "b11", -0.5);
    outlet(voice, "b12", -1);
    outlet(voice, "b13", -0.5);
    outlet(voice, "b14", 0);
    outlet(voice, "b15", 0.5);
}

function dispatchToAll(tokens) {
    for (var voice = 0; voice < NUM_VOICES; voice++) {
        dispatchToVoice(voice, tokens);
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
