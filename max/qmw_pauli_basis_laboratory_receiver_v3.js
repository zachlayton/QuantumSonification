autowatch = 1;
inlets = 1;
outlets = 10;

// 0 computational heatmap
// 1 experimental heatmap
// 2 computational selected 16-bin row
// 3 experimental selected 16-bin row
// 4 computational 255 Pauli coefficients
// 5 experimental 255 Pauli coefficients
// 6 experimental-minus-computational Pauli coefficients
// 7 computational five correlation shells
// 8 experimental five correlation shells
// 9 human-readable status

var selectedPosition = 0.0;
var states = { computational: null, experimental: null };

var pendingRevision = -1;
var pendingSource = "computational";
var pendingShots = 256;
var pendingPreset = "";
var pendingTransform = "";
var pendingSettings = [];
var pendingPaulis = [];
var pendingShells = [];
var pendingMetrics = null;
var receivedSettings = 0;
var receivedPaulis = 0;

function _args(argsObject) {
    return arrayfromargs(argsObject);
}

function _clamp(value, minimum, maximum) {
    return Math.max(minimum, Math.min(maximum, value));
}

function _sourceKey(value) {
    var name = String(value).toLowerCase();
    return name.indexOf("experimental") >= 0
        ? "experimental"
        : "computational";
}

function _status(text) {
    outlet(9, "set", text);
}

function _availableText() {
    var computationalText = states.computational ? "COMPUTATIONAL✓" : "COMPUTATIONAL—";
    var experimentalText = states.experimental ? "EXPERIMENTAL✓" : "EXPERIMENTAL—";
    return computationalText + "  " + experimentalText;
}

function begin() {
    var a = _args(arguments);
    pendingRevision = parseInt(a[0], 10);
    pendingSource = _sourceKey(a[1]);
    pendingPreset = String(a[2]);
    pendingTransform = String(a[3]);
    pendingShots = Math.max(1, parseInt(a[4], 10));
    pendingSettings = new Array(81);
    pendingPaulis = new Array(255);
    pendingShells = new Array(5);
    pendingMetrics = null;
    receivedSettings = 0;
    receivedPaulis = 0;
    _status(
        "receiving " + pendingSource.toUpperCase() +
        " revision " + pendingRevision + "..."
    );
}

function setting() {
    var a = _args(arguments);
    var revision = parseInt(a[0], 10);
    var index = parseInt(a[1], 10);
    if (revision !== pendingRevision || index < 0 || index >= 81 || a.length < 19)
        return;
    var axes = String(a[2]);
    var probabilities = [];
    for (var bin = 0; bin < 16; bin++) {
        var count = Math.max(0, parseFloat(a[3 + bin]));
        probabilities[bin] = count / pendingShots;
    }
    if (!pendingSettings[index])
        receivedSettings++;
    pendingSettings[index] = {
        axes: axes,
        probabilities: probabilities
    };
}

function pauli() {
    var a = _args(arguments);
    var revision = parseInt(a[0], 10);
    var index = parseInt(a[1], 10);
    if (revision !== pendingRevision || index < 0 || index >= 255)
        return;
    if (typeof pendingPaulis[index] === "undefined")
        receivedPaulis++;
    pendingPaulis[index] = parseFloat(a[4]);
}

function shell() {
    var a = _args(arguments);
    var revision = parseInt(a[0], 10);
    var weight = parseInt(a[1], 10);
    if (revision !== pendingRevision || weight < 0 || weight > 4)
        return;
    pendingShells[weight] = parseFloat(a[3]);
}

function metrics() {
    var a = _args(arguments);
    if (parseInt(a[0], 10) !== pendingRevision)
        return;
    pendingMetrics = {
        purity: parseFloat(a[1]),
        entropy: parseFloat(a[2]),
        minimumEigenvalue: parseFloat(a[3]),
        fidelity: parseFloat(a[4])
    };
}

function end() {
    var a = _args(arguments);
    var revision = parseInt(a[0], 10);
    if (revision !== pendingRevision)
        return;
    if (receivedSettings !== 81 || receivedPaulis !== 255) {
        _status(
            "incomplete " + pendingSource.toUpperCase() + " rev " + revision +
            ": " + receivedSettings + "/81 settings, " +
            receivedPaulis + "/255 Pauli terms"
        );
        return;
    }
    states[pendingSource] = {
        revision: revision,
        source: pendingSource,
        preset: pendingPreset,
        transform: pendingTransform,
        shots: pendingShots,
        settings: pendingSettings,
        paulis: pendingPaulis,
        shells: pendingShells,
        metrics: pendingMetrics
    };
    _writeSurface(pendingSource);
    _renderAll();
    _status(
        "stored " + pendingSource.toUpperCase() + " rev " + revision +
        "  " + pendingPreset + "/" + pendingTransform +
        "  " + _availableText()
    );
}

function select(value) {
    selectedPosition = _clamp(Number(value), 0.0, 80.0);
    _renderSelected();
}

function _renderHeatmap(source, outletIndex) {
    var state = states[source];
    if (!state)
        return;
    var matrix = new JitterMatrix(1, "char", 16, 81);
    matrix.setall(0);
    for (var settingIndex = 0; settingIndex < 81; settingIndex++) {
        var row = state.settings[settingIndex];
        if (!row)
            continue;
        for (var bin = 0; bin < 16; bin++)
            matrix.setcell2d(
                bin,
                settingIndex,
                Math.round(
                    255 * _clamp(row.probabilities[bin], 0.0, 1.0)
                )
            );
    }
    outlet(outletIndex, "jit_matrix", matrix.name);
}

function _difference(left, right) {
    if (!left || !right)
        return null;
    var result = [];
    for (var index = 0; index < left.length; index++)
        result[index] = Number(right[index]) - Number(left[index]);
    return result;
}

function _renderAll() {
    _renderHeatmap("computational", 0);
    _renderHeatmap("experimental", 1);
    if (states.computational) {
        outlet(4, states.computational.paulis);
        outlet(7, states.computational.shells);
    }
    if (states.experimental) {
        outlet(5, states.experimental.paulis);
        outlet(8, states.experimental.shells);
    }
    var pauliDifference = _difference(
        states.computational && states.computational.paulis,
        states.experimental && states.experimental.paulis
    );
    if (pauliDifference)
        outlet(6, pauliDifference);
    _renderSelected();
}

function _interpolatedRow(state) {
    if (!state)
        return null;
    var lowerIndex = Math.floor(selectedPosition);
    var upperIndex = Math.min(80, lowerIndex + 1);
    var amount = selectedPosition - lowerIndex;
    var lower = state.settings[lowerIndex];
    var upper = state.settings[upperIndex];
    if (!lower || !upper)
        return null;
    var probabilities = [];
    for (var bin = 0; bin < 16; bin++) {
        probabilities[bin] =
            (1.0 - amount) * lower.probabilities[bin] +
            amount * upper.probabilities[bin];
    }
    return {
        axes: lower.axes + (upperIndex === lowerIndex ? "" : " → " + upper.axes),
        probabilities: probabilities
    };
}

function _renderSelected() {
    var computational = _interpolatedRow(states.computational);
    var experimental = _interpolatedRow(states.experimental);
    if (computational)
        outlet(2, computational.probabilities);
    if (experimental)
        outlet(3, experimental.probabilities);
    if (computational || experimental) {
        _status(
            _availableText() +
            "  setting " + selectedPosition.toFixed(3) + "/80  " +
            (computational ? computational.axes : experimental.axes)
        );
    }
}

function _makeWavetable(probabilities) {
    var frames = 256;
    var table = [];
    var mean = 0.0;
    var peak = 0.0;
    for (var frame = 0; frame < frames; frame++) {
        var phase = 2.0 * Math.PI * frame / frames;
        var value = 0.0;
        for (var harmonic = 0; harmonic < 16; harmonic++) {
            var amplitude = Math.sqrt(
                Math.max(0.0, probabilities[harmonic])
            );
            value += amplitude * Math.sin((harmonic + 1) * phase);
        }
        table[frame] = value;
        mean += value;
    }
    mean /= frames;
    for (var index = 0; index < frames; index++) {
        table[index] -= mean;
        peak = Math.max(peak, Math.abs(table[index]));
    }
    if (peak > 0.0) {
        for (var sample = 0; sample < frames; sample++)
            table[sample] = 0.9 * table[sample] / peak;
    }
    return table;
}

function _surfaceName(source) {
    return source === "experimental"
        ? "qmw_basis_experimental_v3_2d"
        : "qmw_basis_computational_v3_2d";
}

function _writeSurface(source) {
    var state = states[source];
    if (!state)
        return;
    var surface = new Buffer(_surfaceName(source));
    for (var settingIndex = 0; settingIndex < 81; settingIndex++) {
        var row = state.settings[settingIndex];
        if (row) {
            surface.poke(
                1,
                settingIndex * 256,
                _makeWavetable(row.probabilities)
            );
        }
    }
}

function _clearSurface(source) {
    var zeroes = [];
    for (var index = 0; index < 81 * 256; index++)
        zeroes[index] = 0.0;
    new Buffer(_surfaceName(source)).poke(1, 0, zeroes);
}

function status() {
    _status(_args(arguments).join(" "));
}

function error() {
    _status("ERROR: " + _args(arguments).join(" "));
}

function clear() {
    states = { computational: null, experimental: null };
    _clearSurface("computational");
    _clearSurface("experimental");
    _status("cleared COMPUTATIONAL and EXPERIMENTAL");
}
