autowatch = 1;
inlets = 1;
outlets = 5;

// outlet 0: crossfaded 16 x 81 Jitter heatmap
// outlet 1: crossfaded selected sixteen-bin histogram
// outlet 2: crossfaded 255 non-identity Pauli coefficients
// outlet 3: crossfaded five correlation-shell RMS values
// outlet 4: human-readable status

var selectedPosition = 0.0;
var sourceMix = 0.0; // 0 = local, 1 = IBM
var states = { local: null, ibm: null };

var pendingRevision = -1;
var pendingSource = "local";
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
    return name.indexOf("ibm") >= 0 ? "ibm" : "local";
}

function _status(text) {
    outlet(4, "set", text);
}

function _availableText() {
    var localText = states.local ? "LOCAL✓" : "LOCAL—";
    var ibmText = states.ibm ? "IBM✓" : "IBM—";
    return localText + "  " + ibmText;
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
    pendingSettings[index] = { axes: axes, probabilities: probabilities };
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
    _renderAll();
    _status(
        "stored " + pendingSource.toUpperCase() + " rev " + revision +
        "  " + pendingPreset + "/" + pendingTransform +
        "  " + _availableText() +
        "  mix " + sourceMix.toFixed(3)
    );
}

function select(value) {
    selectedPosition = _clamp(Number(value), 0.0, 80.0);
    _renderSelected();
}

function msg_float(value) {
    xfade(value);
}

function xfade(value) {
    sourceMix = _clamp(Number(value), 0.0, 1.0);
    _renderAll();
    _status(
        _availableText() + "  crossfade " + sourceMix.toFixed(3) +
        "  (0=LOCAL, 1=IBM)"
    );
}

function _blend(localValue, ibmValue) {
    if (typeof localValue === "undefined" || localValue === null)
        return Number(ibmValue);
    if (typeof ibmValue === "undefined" || ibmValue === null)
        return Number(localValue);
    return (1.0 - sourceMix) * Number(localValue) + sourceMix * Number(ibmValue);
}

function _mixedSetting(index) {
    var localRow = states.local && states.local.settings[index];
    var ibmRow = states.ibm && states.ibm.settings[index];
    if (!localRow && !ibmRow)
        return null;
    var probabilities = [];
    for (var bin = 0; bin < 16; bin++) {
        probabilities[bin] = _blend(
            localRow ? localRow.probabilities[bin] : null,
            ibmRow ? ibmRow.probabilities[bin] : null
        );
    }
    return {
        axes: localRow ? localRow.axes : ibmRow.axes,
        probabilities: probabilities
    };
}

function _mixedArray(field, length) {
    var localValues = states.local ? states.local[field] : null;
    var ibmValues = states.ibm ? states.ibm[field] : null;
    if (!localValues && !ibmValues)
        return null;
    var values = [];
    for (var index = 0; index < length; index++) {
        values[index] = _blend(
            localValues ? localValues[index] : null,
            ibmValues ? ibmValues[index] : null
        );
    }
    return values;
}

function _renderAll() {
    if (!states.local && !states.ibm)
        return;
    var matrix = new JitterMatrix(1, "char", 16, 81);
    matrix.setall(0);
    for (var settingIndex = 0; settingIndex < 81; settingIndex++) {
        var row = _mixedSetting(settingIndex);
        if (!row)
            continue;
        for (var bin = 0; bin < 16; bin++)
            matrix.setcell2d(
                bin,
                settingIndex,
                Math.round(255 * _clamp(row.probabilities[bin], 0.0, 1.0))
            );
    }
    outlet(0, "jit_matrix", matrix.name);

    var paulis = _mixedArray("paulis", 255);
    if (paulis)
        outlet(2, paulis);
    var shells = _mixedArray("shells", 5);
    if (shells)
        outlet(3, shells);
    _renderSelected();
}

function _renderSelected() {
    var lowerIndex = Math.floor(selectedPosition);
    var upperIndex = Math.min(80, lowerIndex + 1);
    var settingMix = selectedPosition - lowerIndex;
    var lowerRow = _mixedSetting(lowerIndex);
    var upperRow = _mixedSetting(upperIndex);
    if (!lowerRow && !upperRow)
        return;
    if (!lowerRow)
        lowerRow = upperRow;
    if (!upperRow)
        upperRow = lowerRow;
    var probabilities = [];
    for (var bin = 0; bin < 16; bin++) {
        probabilities[bin] =
            (1.0 - settingMix) * lowerRow.probabilities[bin] +
            settingMix * upperRow.probabilities[bin];
    }
    outlet(1, probabilities);
    _writeWavetable(probabilities);
    var axesText = lowerRow.axes;
    if (upperIndex !== lowerIndex)
        axesText += " → " + upperRow.axes;
    _status(
        _availableText() +
        "  mix " + sourceMix.toFixed(3) +
        "  setting " + selectedPosition.toFixed(3) + "/80  " + axesText +
        "  row morph " + settingMix.toFixed(3)
    );
}

function _writeWavetable(probabilities) {
    var frames = 256;
    var table = [];
    var mean = 0.0;
    var peak = 0.0;
    for (var frame = 0; frame < frames; frame++) {
        var phase = 2.0 * Math.PI * frame / frames;
        var value = 0.0;
        for (var harmonic = 0; harmonic < 16; harmonic++) {
            var amplitude = Math.sqrt(Math.max(0.0, probabilities[harmonic]));
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
    new Buffer("qmw_full4q_setting").poke(1, 0, table);
}

function status() {
    _status(_args(arguments).join(" "));
}

function error() {
    _status("ERROR: " + _args(arguments).join(" "));
}

function clear() {
    states = { local: null, ibm: null };
    _status("cleared LOCAL and IBM");
}

function clear_local() {
    states.local = null;
    _renderAll();
    _status("cleared LOCAL  " + _availableText());
}

function clear_ibm() {
    states.ibm = null;
    _renderAll();
    _status("cleared IBM  " + _availableText());
}
