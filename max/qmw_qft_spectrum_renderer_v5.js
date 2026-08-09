// V5: full QFT/IQFT bin renderer, harmonic wavetable, and scrolling history.
autowatch = 1;
inlets = 3;   // probabilities, amplitudes, phases
outlets = 3;  // status, jit_matrix spectrogram, 16-bin display

var bins = [];
var amplitudes = [];
var phases = [];
var latestRevision = -1;
var latestSource = "local";
var latestTransform = "qft";
// Explicit 8-bit luminance avoids host-dependent float-matrix preview ranges.
var history = new JitterMatrix(1, "char", 16, 96);
var historyPixels = [];

function clearHistoryPixels() {
    historyPixels = [];
    for (var y = 0; y < 96; y++) {
        var row = [];
        for (var x = 0; x < 16; x++) row.push(0);
        historyPixels.push(row);
    }
}

function loadbang() {
    // Faint calibration grid: if this is visible, JS -> Jitter -> pwindow is
    // healthy even before the first quantum result arrives.
    clearHistoryPixels();
    for (var y = 0; y < 96; y++)
        for (var x = 0; x < 16; x++) {
            historyPixels[y][x] = ((x + y) % 8 === 0) ? 28 : 3;
            history.setcell2d(x, y, historyPixels[y][x]);
        }
    outlet(1, "jit_matrix", history.name);
    outlet(0, ["qft_renderer_ready", 16, 96]);
}

function parseFrame(args, kind) {
    var a = arrayfromargs(args);
    if (a.length !== 19) {
        outlet(0, ["error", kind + "_expected_19_atoms", a.length]);
        return null;
    }
    var revision = Math.floor(Number(a.shift()));
    var source = String(a.shift()).toLowerCase();
    var transform = String(a.shift()).toLowerCase();
    var values = [];
    for (var i = 0; i < 16; i++) values.push(Number(a.shift()));
    latestRevision = revision;
    latestSource = source;
    latestTransform = transform;
    return values;
}

function list() {
    if (inlet === 0) {
        var frame = arrayfromargs(arguments);
        if (frame.length === 52 && String(frame[1]) === "qft_frame") {
            latestRevision = Math.floor(Number(frame[0]));
            latestSource = String(frame[2]).toLowerCase();
            latestTransform = String(frame[3]).toLowerCase();
            bins = frame.slice(4, 20);
            amplitudes = frame.slice(20, 36);
            phases = frame.slice(36, 52);
            pushHistory(bins);
            emitSpectrumData();
            renderWavetable();
            outlet(0, ["qft_bins", latestTransform, latestSource, latestRevision]);
            return;
        }
        var values = parseFrame(arguments, "bins");
        if (!values) return;
        bins = values;
        pushHistory(values);
        outlet(2, ["probabilities"].concat(values));
        emitDescriptors();
        outlet(0, ["qft_bins", latestTransform, latestSource, latestRevision]);
    } else if (inlet === 1) {
        var magnitudes = parseFrame(arguments, "amplitudes");
        if (!magnitudes) return;
        amplitudes = magnitudes;
        outlet(2, ["magnitudes"].concat(amplitudes));
        emitDescriptors();
        renderWavetable();
    } else {
        var angles = parseFrame(arguments, "phases");
        if (!angles) return;
        phases = angles;
        outlet(2, ["phases"].concat(phases));
        emitDescriptors();
        renderWavetable();
    }
}

function emitSpectrumData() {
    outlet(2, ["probabilities"].concat(bins));
    outlet(2, ["magnitudes"].concat(amplitudes));
    outlet(2, ["phases"].concat(phases));
    emitDescriptors();
}

function emitDescriptors() {
    if (bins.length !== 16 || phases.length !== 16) return;
    var total = 0, centroid = 0, entropy = 0, real = 0, imag = 0;
    for (var i = 0; i < 16; i++) total += Math.max(0, Number(bins[i]));
    if (total <= 0) return;
    for (i = 0; i < 16; i++) {
        var weight = Math.max(0, Number(bins[i])) / total;
        centroid += weight * i / 15;
        if (weight > 0) entropy -= weight * Math.log(weight) / Math.log(16);
        real += weight * Math.cos(Number(phases[i]));
        imag += weight * Math.sin(Number(phases[i]));
    }
    var phaseDispersion = 1 - Math.sqrt(real * real + imag * imag);
    outlet(2, ["descriptors", centroid, entropy, phaseDispersion]);
}

function pushHistory(values) {
    // Circuit results arrive as discrete events rather than at video rate.
    // Give each result an eight-row time slice so a single submission is
    // clearly visible, and use sqrt scaling to reveal quieter probability bins.
    var x, y, rows = 8;
    if (historyPixels.length !== 96) clearHistoryPixels();
    historyPixels.splice(0, rows);
    for (y = 0; y < rows; y++) {
        var newRow = [];
        for (x = 0; x < 16; x++)
            newRow.push(Math.round(
                255 * Math.sqrt(Math.max(0, Math.min(1, Number(values[x]))))
            ));
        historyPixels.push(newRow);
    }
    for (y = 0; y < 96; y++)
        for (x = 0; x < 16; x++)
            history.setcell2d(x, y, historyPixels[y][x]);
    outlet(1, "jit_matrix", history.name);
}

function renderWavetable() {
    if (amplitudes.length !== 16) return;
    var table = [], peak = 0;
    for (var sample = 0; sample < 256; sample++) {
        var time = 2 * Math.PI * sample / 256;
        var value = 0;
        for (var bin = 0; bin < 16; bin++) {
            var angle = phases.length === 16 ? phases[bin] : 0;
            value += amplitudes[bin] * Math.sin((bin + 1) * time + angle);
        }
        table.push(value);
        peak = Math.max(peak, Math.abs(value));
    }
    var scale = peak > 0.95 ? 0.95 / peak : 1;
    for (var i = 0; i < 256; i++) table[i] *= scale;
    try {
        var target = new Buffer("qmw_v5_qft_wave");
        target.poke(1, 0, table);
        outlet(0, ["qft_wavetable", latestTransform, latestSource, latestRevision]);
    } catch (error) {
        outlet(0, ["error", "qft_buffer", String(error)]);
    }
}
