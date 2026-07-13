// qmw_density_field_to_wavetable.js
//
// Max js helper for four q-labelled wavetable Gen~ voices.
//
// Inlets for bare OSC-route list outputs:
//   inlet 0: real list      -> b0..b15
//   inlet 1: imag list      -> im0..im15
//   inlet 2: magnitude list -> m0..m15
//   inlet 3: phase list     -> ph0..ph15
//   inlet 4: speed list     -> s0..s15
//
// Outlets:
//   outlet 0 -> q0 gen~
//   outlet 1 -> q1 gen~
//   outlet 2 -> q2 gen~
//   outlet 3 -> q3 gen~

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
    speed: "s"
};

var scalarParams = {
    purity: true,
    entropy: true,
    coherence: true,
    amp: true,
    default_freq: true,
    value_smooth_ms: true,
    magnitude_smooth_ms: true,
    phase_smooth_ms: true,
    fast_smooth_ms: true,
    slow_smooth_ms: true,
    phase_depth: true,
    imag_mix: true,
    drive: true,
    max_drive: true,
    auto_level: true,
    mix_voices: true,
    output_ceiling: true
};

var inletNames = ["real", "imag", "magnitude", "phase", "speed"];

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
    post("qmw_density_field_to_wavetable: outlet " + voice + " test\n");
    outlet(voice, "amp", 0.2);
    outlet(voice, "default_freq", 55 * (voice + 1));
    for (var i = 0; i < NUM_BASIS; i++) {
        outlet(voice, "m" + i, 1);
        outlet(voice, "b" + i, Math.sin(i / NUM_BASIS * 6.283185307179586));
        outlet(voice, "im" + i, 0);
        outlet(voice, "ph" + i, 0);
        outlet(voice, "s" + i, 0);
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
