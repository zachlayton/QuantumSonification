// Pauli occupation and energy-shell fields -> 24 Grainflow voice slots.
autowatch = 1;
inlets = 1;
outlets = 8;

var STREAMS = 6;
var GRAINS = 4;
var VOICES = STREAMS * GRAINS;
var factors = [-1.0, 0.0, 1.0, 99.0, 99.0, 99.0];
var strengths = [1.0, 1.0, 1.0, 0.0, 0.0, 0.0];
var presets = {
    normal: {f: [-1, 0, 1, 99, 99, 99], s: [1, 1, 1, 0, 0, 0]},
    sodium_d1: {f: [-4/3, -2/3, 2/3, 4/3, 99, 99], s: [2/3, 1/3, 1/3, 2/3, 0, 0]},
    sodium_d2: {f: [-5/3, -1, -1/3, 1/3, 1, 5/3], s: [1/3, 1, 2/3, 2/3, 1, 1/3]}
};
var presetName = "normal";
var statisticsName = "fermion";
var particlesValue = 2;
var fieldValue = 1.0;
var shellCenter = 0.0;
var shellWidth = 4.0;
var entropyValue = 0.25;
var coherenceValue = 0.8;
var densityValue = 0.85;
var deviationSemitones = 1.5;
var sourceDurationMs = 5587.528;
var lookupMode = 1;
var seedValue = 0x2468ace1;
var previous = [0, 0, 0, 0, 0, 0];

function preset(value) {
    var key = String(value).toLowerCase();
    if (!presets[key]) return;
    presetName = key; factors = presets[key].f.slice(); strengths = presets[key].s.slice(); tick();
}
function statistics(value) { var key = String(value).toLowerCase(); if (key === "fermion" || key === "boson" || key === "classical") { statisticsName = key; tick(); } }
function particles(value) { particlesValue = Math.max(0, Math.floor(num(value, 2))); tick(); }
function field(value) { fieldValue = clamp(num(value, 1.0), 0.0, 20.0); tick(); }
function center(value) { shellCenter = num(value, 0.0); tick(); }
function width(value) { shellWidth = Math.max(0.0, num(value, 4.0)); tick(); }
function entropy(value) { entropyValue = clamp(num(value, 0.25), 0.0, 1.0); tick(); }
function coherence(value) { coherenceValue = clamp(num(value, 0.8), 0.0, 1.0); tick(); }
function density(value) { densityValue = clamp(num(value, 0.85), 0.0, 1.0); tick(); }
function deviation(value) { deviationSemitones = clamp(num(value, 1.5), 0.0, 24.0); tick(); }
function duration(value) { sourceDurationMs = Math.max(10.0, num(value, 5587.528)); tick(); }
function mode(value) { lookupMode = Math.max(0, Math.min(2, Math.floor(num(value, 1)))); tick(); }
function bang() { tick(); }
function test() { tick(); }

function randomUnit() {
    seedValue = ((1664525 * seedValue + 1013904223) % 4294967296) >>> 0;
    return seedValue / 4294967296.0;
}

function accessible() {
    var result = [], half = shellWidth * 0.5, nearest = 0, nearestDistance = Infinity;
    for (var i = 0; i < STREAMS; i++) {
        var distance = Math.abs(fieldValue * factors[i] - shellCenter);
        if (strengths[i] > 0.0 && distance <= half) result.push(i);
        if (strengths[i] > 0.0 && distance < nearestDistance) { nearest = i; nearestDistance = distance; }
    }
    if (!result.length) result.push(nearest);
    return result;
}

function configuration() {
    var modes = accessible();
    var result = [0, 0, 0, 0, 0, 0];
    if (statisticsName === "fermion") {
        // An overfilled fermionic shell is excluded, not silently truncated.
        if (particlesValue > modes.length) return result;
        var pool = modes.slice();
        for (var p = 0; p < particlesValue; p++) {
            var pick = entropyValue > 0.0001 ? Math.floor(randomUnit() * pool.length) : 0;
            result[pool.splice(pick, 1)[0]] = 1;
        }
    } else if (statisticsName === "boson") {
        for (var b = 0; b < particlesValue; b++) {
            var bias = coherenceValue > 0.5 && b > 0 ? 0 : Math.floor(randomUnit() * modes.length);
            result[modes[bias]] += 1;
        }
    } else {
        for (var c = 0; c < particlesValue; c++) result[modes[Math.floor(randomUnit() * modes.length)]] += 1;
    }
    return result;
}

function tick() {
    var occupation = configuration();
    previous = occupation.slice();
    var rates = [], delays = [], windows = [], amplitudes = [];
    var totalWeight = 0.0;
    var stream, grain;

    for (stream = 0; stream < STREAMS; stream++) {
        for (grain = 0; grain < GRAINS; grain++) {
            var micro = (grain - 1.5) / 1.5;
            var semitones = fieldValue * factors[stream] * 2.0;
            semitones += micro * deviationSemitones * entropyValue;
            var rate = strengths[stream] > 0.0 ? Math.pow(2.0, semitones / 12.0) : 1.0;
            var phase01 = wrap01(stream / STREAMS + grain / VOICES + (1.0 - coherenceValue) * 0.125);
            var delay = -sourceDurationMs * phase01;
            var windowOffset = wrap01((stream * GRAINS + grain) / VOICES + entropyValue * 0.04 * micro);
            var weight = occupation[stream] * strengths[stream];
            var amplitude = weight > 0.0 ? Math.sqrt(weight / GRAINS) : 0.0;
            amplitude *= 0.6 + 0.4 * coherenceValue;
            rates.push(rate); delays.push(delay); windows.push(windowOffset); amplitudes.push(amplitude);
            totalWeight += amplitude * amplitude;
        }
    }

    var scale = totalWeight > 0.0 ? 0.95 / Math.sqrt(totalWeight) : 0.0;
    for (var i = 0; i < VOICES; i++) amplitudes[i] *= scale;
    pokeTable("qmw_pauli_rates", rates);
    pokeTable("qmw_pauli_delays", delays);
    pokeTable("qmw_pauli_windows", windows);

    outlet(0, rates); outlet(1, delays); outlet(2, windows); outlet(3, amplitudes);
    for (i = 0; i < VOICES; i++) outlet(4, "setvalue", i + 1, amplitudes[i]);
    outlet(5, "rateBuffer", "qmw_pauli_rates");
    outlet(5, "delayBuffer", "qmw_pauli_delays");
    outlet(5, "windowBuffer", "qmw_pauli_windows");
    outlet(5, "rateMode", lookupMode);
    outlet(5, "delayMode", lookupMode);
    outlet(5, "windowMode", lookupMode);
    outlet(5, "density", densityValue);
    outlet(5, "rateRandom", entropyValue * 0.35);
    outlet(5, "delayRandom", entropyValue * sourceDurationMs * 0.05);
    outlet(5, "windowOffsetRandom", entropyValue * 0.12);
    outlet(6, occupation);
    outlet(7, "set", "PAULI 24-SLOT FIELD", presetName.toUpperCase(), statisticsName.toUpperCase(),
        "N=" + particlesValue, "occupation=" + occupation.join("/"), "mode=" + lookupMode);
}

function pokeTable(name, values) {
    var table = values.slice(); table.push(values.length ? values[values.length - 1] : 0.0);
    try { new Buffer(name).poke(1, 0, table); }
    catch (error) { post("qmw_pauli_parameter_field_v2: could not write " + name + "\n"); }
}
function wrap01(value) { return value - Math.floor(value); }
function clamp(value, low, high) { return Math.max(low, Math.min(high, value)); }
function num(value, fallback) { var result = Number(value); return isFinite(result) ? result : fallback; }
