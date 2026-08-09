// Local four-voice router for QMW_Sonification_Rack_Module_v1.maxpat.
// Kept beside the patch so Max never instantiates a one-outlet placeholder.

autowatch = 1;
inlets = 4;
outlets = 4;

var NUM_VOICES = 4;
var NUM_BASIS = 16;
var inletNames = ["magnitude", "phase", "speed", "harmonics"];

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
    if (!tokens || tokens.length < 1) return;
    var voice = voiceIndex(String(tokens[0]));
    if (voice >= 0) {
        dispatchToVoice(voice, tokens.slice(1));
        return;
    }
    for (var index = 0; index < NUM_VOICES; index++)
        dispatchToVoice(index, tokens);
}

function dispatchToVoice(voice, tokens) {
    if (!tokens || tokens.length < 1) return;
    var name = String(tokens[0]);
    var values = tokens.slice(1);
    if (listPrefixes.hasOwnProperty(name)) {
        emitListParams(voice, listPrefixes[name], values);
        return;
    }
    if (scalarParams.hasOwnProperty(name) && values.length >= 1)
        outlet(voice, name, sanitizeNumber(values[0], 0));
}

function emitListParams(voice, prefix, values) {
    var count = Math.min(NUM_BASIS, values.length);
    for (var index = 0; index < count; index++)
        outlet(voice, prefix + index, sanitizeNumber(values[index], 0));
}

function test() {
    for (var voice = 0; voice < NUM_VOICES; voice++) emitTestVoice(voice);
}

function test0() { emitTestVoice(0); }
function test1() { emitTestVoice(1); }
function test2() { emitTestVoice(2); }
function test3() { emitTestVoice(3); }

function emitTestVoice(voice) {
    outlet(voice, "amp", 0.2);
    outlet(voice, "default_freq", 55 * (voice + 1));
    for (var index = 0; index < NUM_BASIS; index++) {
        outlet(voice, "m" + index, 1);
        outlet(voice, "ph" + index, 0);
        outlet(voice, "s" + index, 0);
        outlet(voice, "h" + index, index + 1);
    }
}

function voiceIndex(name) {
    if (name === "q0") return 0;
    if (name === "q1") return 1;
    if (name === "q2") return 2;
    if (name === "q3") return 3;
    return -1;
}

function sanitizeNumber(value, fallback) {
    var number = Number(value);
    return isFinite(number) ? number : fallback;
}

function isNumeric(value) {
    return isFinite(Number(value));
}
