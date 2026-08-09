// Eight-voice quantum parameter-field writer for Grainflow 2.1.
autowatch = 1;
inlets = 1;
outlets = 7;

var VOICES = 8;
var TABLE_SIZE = VOICES + 1;
var TWO_PI = Math.PI * 2.0;
var magnitudeValue = 0.55;
var phaseValue = 0.0;
var purityValue = 0.8;
var entropyValue = 0.2;
var coherenceValue = 0.8;
var lookupMode = 1;
var sourceDurationMs = 5587.528;

function magnitude(value) { magnitudeValue = clamp(num(value, 0.55), 0.0, 1.0); update(); }
function phase(value) { phaseValue = num(value, 0.0); update(); }
function purity(value) { purityValue = clamp(num(value, 0.8), 0.0, 1.0); update(); }
function entropy(value) { entropyValue = clamp(num(value, 0.2), 0.0, 1.0); update(); }
function coherence(value) { coherenceValue = clamp(num(value, 0.8), 0.0, 1.0); update(); }
function duration(value) { sourceDurationMs = Math.max(10.0, num(value, 5587.528)); update(); }
function mode(value) { lookupMode = Math.max(0, Math.min(2, Math.floor(num(value, 1)))); update(); }
function test() { autoduration(); }

function autoduration() {
    try {
        var source = new Buffer("qmw_fdg_source");
        var sampleRate = source.samplerate();
        var frames = source.framecount();
        if (sampleRate > 0.0 && frames > 0) sourceDurationMs = 1000.0 * frames / sampleRate;
    } catch (error) {
        post("qmw_fdg_parameter_field_v1: using declared source duration\n");
    }
    update();
}

function list() {
    var values = arrayfromargs(arguments);
    if (values.length >= 5) {
        magnitudeValue = clamp(num(values[0], magnitudeValue), 0.0, 1.0);
        phaseValue = num(values[1], phaseValue);
        purityValue = clamp(num(values[2], purityValue), 0.0, 1.0);
        entropyValue = clamp(num(values[3], entropyValue), 0.0, 1.0);
        coherenceValue = clamp(num(values[4], coherenceValue), 0.0, 1.0);
        update();
    }
}

function update() {
    var rates = [];
    var delays = [];
    var windows = [];
    var amplitudes = [];
    var phase01 = wrap01(phaseValue / TWO_PI);
    var energy = 0.0;
    var i;

    for (i = 0; i < VOICES; i++) {
        var x = (i - (VOICES - 1) * 0.5) / ((VOICES - 1) * 0.5);
        var signedGap = x * magnitudeValue;
        var direction = signedGap < 0.0 ? -1.0 : 1.0;
        // A compressed signed-gap map spanning at most four octaves of rate.
        var rate = direction * Math.pow(2.0, Math.abs(signedGap) * 2.0);
        var relationalPhase = wrap01(phase01 + coherenceValue * i / VOICES);
        // Grainflow traversal buffers are millisecond offsets into the source.
        var delay = -sourceDurationMs * relationalPhase;
        // Window offsets are phasor positions. Purity contracts the field
        // around ordered voice locations; entropy perturbs it in mode 2.
        var windowOffset = wrap01(i / VOICES + (1.0 - purityValue) * 0.125);
        var shell = Math.exp(-2.2 * x * x);
        var amplitude = Math.sqrt(Math.max(0.0, magnitudeValue)) * shell;
        amplitude *= 0.28 + 0.72 * (purityValue * coherenceValue + (1.0 - coherenceValue) * 0.45);

        rates.push(rate);
        delays.push(delay);
        windows.push(windowOffset);
        amplitudes.push(amplitude);
        energy += amplitude * amplitude;
    }

    // Energy-normalize the eight-channel amplitude field.
    var scale = energy > 0.0 ? 0.9 / Math.sqrt(energy) : 0.0;
    for (i = 0; i < amplitudes.length; i++) amplitudes[i] *= scale;

    pokeTable("qmw_fdg_rates", rates);
    pokeTable("qmw_fdg_delays", delays);
    pokeTable("qmw_fdg_windows", windows);

    outlet(0, rates);
    outlet(1, delays);
    outlet(2, windows);
    outlet(3, amplitudes);
    for (i = 0; i < VOICES; i++) outlet(4, "setvalue", i + 1, amplitudes[i]);

    outlet(5, "rateBuffer", "qmw_fdg_rates");
    outlet(5, "delayBuffer", "qmw_fdg_delays");
    outlet(5, "windowBuffer", "qmw_fdg_windows");
    outlet(5, "rateMode", lookupMode);
    outlet(5, "delayMode", lookupMode);
    outlet(5, "windowMode", lookupMode);
    outlet(5, "rateRandom", entropyValue * 0.55);
    outlet(5, "delayRandom", entropyValue * sourceDurationMs * 0.08);
    outlet(5, "windowOffsetRandom", entropyValue * 0.16);

    outlet(6, "set", "8-VOICE FIELD", "mode=" + lookupMode,
        "magnitude=" + magnitudeValue.toFixed(3),
        "phase=" + phaseValue.toFixed(3),
        "purity=" + purityValue.toFixed(3),
        "entropy=" + entropyValue.toFixed(3),
        "coherence=" + coherenceValue.toFixed(3));
}

function pokeTable(name, values) {
    var table = values.slice(0);
    table.push(values.length ? values[values.length - 1] : 0.0);
    try {
        new Buffer(name).poke(1, 0, table);
    } catch (error) {
        post("qmw_fdg_parameter_field_v1: could not write " + name + "\n");
    }
}

function wrap01(value) { return value - Math.floor(value); }
function clamp(value, minimum, maximum) { return Math.max(minimum, Math.min(maximum, value)); }
function num(value, fallback) {
    var result = Number(value);
    return isFinite(result) ? result : fallback;
}
