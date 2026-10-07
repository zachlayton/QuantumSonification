// Four-qubit circuit probabilities -> one sparse workshop impulse response.
//
// Inlet:
//   list of 16 computational-basis probabilities
//   refresh
//
// Outlets:
//   0  sixteen tap magnitudes for the participant display
//   1  HIRT multiconvolve~ set message
//   2  participant-facing status
//
// Mapping choice:
//   |0000> ... |1111> select RT60 values from 100 ... 1600 ms.
//   Each probability weights an independent deterministic-noise decay.
//   A fixed direct impulse makes the exported WAV a complete mono IR.

autowatch = 1;
inlets = 1;
outlets = 3;

var BUFFER_NAME = "qmw_workshop_circuit_ir";
var NUM_TAPS = 16;
var lastProbabilities = [];

initialize();

function initialize() {
    lastProbabilities = [];
    for (var i = 0; i < NUM_TAPS; i++) {
        lastProbabilities.push(i === 0 ? 1.0 : 0.0);
    }
}

function list() {
    probabilities.apply(this, arguments);
}

function probabilities() {
    var values = arrayfromargs(arguments);
    var normalized = normalizeProbabilities(values);
    if (!normalized) return;
    lastProbabilities = normalized;
    render();
}

function refresh() {
    render();
}

function render() {
    var target;
    try {
        target = new Buffer(BUFFER_NAME);
    } catch (error) {
        status("IR buffer unavailable · reopen the patch");
        return;
    }

    var frames = Math.max(1, Math.floor(target.framecount()));
    var durationMs = Math.max(1.0, Number(target.length()) || 1600.0);
    var samples = [];
    var componentMagnitudes = [];
    var active = [];
    var i;

    for (i = 0; i < frames; i++) samples.push(0.0);

    // Each basis state contributes an independent dense reflection cloud.
    // RT60 is the time at which that component reaches -60 dB amplitude.
    for (i = 0; i < NUM_TAPS; i++) {
        var probability = lastProbabilities[i];
        var magnitude = Math.sqrt(probability);
        var rt60Ms = 100.0 * (i + 1);
        var seed = (0x13579bdf + (i + 1) * 0x10203) >>> 0;
        componentMagnitudes.push(magnitude);

        if (probability > 0.000001) {
            for (var frame = 1; frame < frames; frame++) {
                seed = lcg(seed);
                var noise = (seed / 4294967296.0) * 2.0 - 1.0;
                var timeMs = (frame / frames) * durationMs;
                // 10^(-3) is -60 dB in amplitude.
                var decay = Math.pow(10.0, -3.0 * timeMs / rt60Ms);
                samples[frame] += magnitude * noise * decay;
            }
        }

        if (probability > 0.000001) {
            active.push({
                index: i,
                rt60: rt60Ms,
                probability: probability
            });
        }
    }

    // Normalize the reverberant tail while retaining a stable direct impulse.
    var peak = 0.0;
    for (i = 1; i < frames; i++) peak = Math.max(peak, Math.abs(samples[i]));
    var tailScale = peak > 0.0 ? 0.55 / peak : 0.0;
    for (i = 1; i < frames; i++) samples[i] *= tailScale;
    samples[0] = 0.8;

    try {
        target.poke(1, 0, samples);
    } catch (error) {
        status("IR write failed · " + String(error));
        return;
    }

    outlet(0, componentMagnitudes);
    outlet(1, "set", 1, 1, BUFFER_NAME, 1);
    status(describe(active, durationMs));
}

function normalizeProbabilities(values) {
    var output = [];
    var total = 0.0;
    var i;

    for (i = 0; i < NUM_TAPS; i++) {
        var value = Number(values[i]);
        if (!isFinite(value)) value = 0.0;
        value = Math.max(0.0, value);
        output.push(value);
        total += value;
    }

    if (total <= 0.0) {
        status("No state yet · build a circuit first");
        return null;
    }

    for (i = 0; i < NUM_TAPS; i++) output[i] /= total;
    return output;
}

function describe(active, durationMs) {
    if (!active.length) return "IR is silent";

    var weightedRt60 = 0.0;
    for (var i = 0; i < active.length; i++) {
        weightedRt60 += active[i].probability * active[i].rt60;
    }

    var text = "IR READY · circuit-weighted RT60 ≈ "
        + Math.round(weightedRt60) + " ms";

    if (active.length <= 3) {
        text += " · ";
        var parts = [];
        for (i = 0; i < active.length; i++) {
            parts.push(
                "|" + binary4(active[i].index) + "> "
                + Math.round(active[i].rt60) + " ms"
            );
        }
        text += parts.join("  ·  ");
    } else {
        text += " · " + active.length + " decay components";
    }
    return text;
}

function lcg(value) {
    value ^= value << 13;
    value ^= value >>> 17;
    value ^= value << 5;
    return value >>> 0;
}

function binary4(value) {
    var text = Math.max(0, Math.min(15, value)).toString(2);
    while (text.length < 4) text = "0" + text;
    return text;
}

function status(text) {
    outlet(2, "set", text);
}
