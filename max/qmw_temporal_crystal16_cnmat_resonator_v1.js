// Atomic OSC assembler, trigger router, and 16x16 gain monitor for CNMAT resonators~.
autowatch = 1;
inlets = 3;
outlets = 5;

var expectedRevision = -1;
var expectedDimension = 16;
var expectedResonances = 256;
var pending = [];
var receivedRows = [];
var stagedModel = [];
var stagedGains = [];
var stagedRevision = -1;
var committedRawModel = [];
var committedGains = [];
var frequencyMultiplier = 1.0;
var frequencyDirty = false;
var committedRevision = -1;

function anything() {
    var args = arrayfromargs(arguments);
    var name = String(messagename);
    if (inlet === 2) {
        setFrequencyMultiplier(args.length ? args[0] : name);
        return;
    }
    if (inlet === 1) {
        handleQTMPulse([name].concat(args));
        return;
    }
    dispatch(name, args);
}

function list() {
    var args = arrayfromargs(arguments);
    if (inlet === 2 && args.length) {
        setFrequencyMultiplier(args[0]);
        return;
    }
    if (inlet === 1) handleQTMPulse(args);
}

function msg_float(value) {
    if (inlet === 2) setFrequencyMultiplier(value);
}

function msg_int(value) {
    if (inlet === 2) setFrequencyMultiplier(value);
}

function dispatch(name, args) {
    if (name === "begin") begin.apply(this, args);
    else if (name === "row") row.apply(this, args);
    else if (name === "end") end.apply(this, args);
    else if (name === "trigger") trigger(args.length ? args[0] : 0.7);
}

function begin(revision, dimension, resonanceCount) {
    var rev = integer(revision, -1);
    var dim = integer(dimension, 0);
    var count = integer(resonanceCount, 0);
    if (rev < 0 || dim < 1 || count !== dim * dim) {
        status("rejected malformed begin frame");
        resetPending();
        return;
    }
    expectedRevision = rev;
    expectedDimension = dim;
    expectedResonances = count;
    pending = fill(count * 3, 0.0);
    receivedRows = fill(dim, false);
}

function row() {
    var args = arrayfromargs(arguments);
    if (args.length < 2 || expectedRevision < 0) return;
    var revision = integer(args[0], -1);
    var rowIndex = integer(args[1], -1);
    var values = args.slice(2);
    var expectedValues = expectedDimension * 3;
    if (revision !== expectedRevision || rowIndex < 0 || rowIndex >= expectedDimension)
        return;
    if (values.length !== expectedValues) {
        status("rejected row " + rowIndex + ": expected " + expectedValues + " values");
        return;
    }
    var offset = rowIndex * expectedValues;
    for (var index = 0; index < expectedValues; index++)
        pending[offset + index] = number(values[index], 0.0);
    receivedRows[rowIndex] = true;
}

function end(revision) {
    var rev = integer(revision, -1);
    if (rev !== expectedRevision || pending.length !== expectedResonances * 3)
        return;
    for (var index = 0; index < receivedRows.length; index++) {
        if (!receivedRows[index]) {
            status("incomplete frame " + rev + ": missing row " + index);
            return;
        }
    }
    stagedModel = pending.slice(0);
    stagedGains = gainVector(pending);
    stagedRevision = rev;
    status("model " + rev + " staged: waiting for next click");
    resetPending();
}

function trigger(amplitude) {
    var value = Math.max(0.0, Math.min(1.0, number(amplitude, 0.7)));
    commitStagedModel();
    outlet(1, value);
    status("trigger " + value.toFixed(3) + " / model " + committedRevision);
}

function handleQTMPulse(args) {
    // QTM v1 density-clock pulse: record, intrinsic time, Bures increment,
    // phase, coherence, population flux, coherence flux, purity, numerical
    // diagnostics, coherence gain, and hazard increment.
    if (!args || args.length < 8) return;
    var delta = Math.tanh(8.0 * Math.abs(number(args[2], 0.0)));
    var populationFlux = Math.tanh(8.0 * Math.abs(number(args[5], 0.0)));
    var coherenceFlux = Math.tanh(8.0 * Math.abs(number(args[6], 0.0)));
    var purity = Math.max(0.0, Math.min(1.0, number(args[7], 0.0)));
    trigger(0.12 + 0.35 * delta + 0.20 * populationFlux
        + 0.15 * coherenceFlux + 0.18 * purity);
}

function test() {
    var model = [];
    var gains = [];
    for (var rowIndex = 0; rowIndex < 16; rowIndex++) {
        for (var columnIndex = 0; columnIndex < 16; columnIndex++) {
            var relationIndex = rowIndex * 16 + columnIndex;
            var distance = Math.abs(rowIndex - columnIndex);
            var gain = 0.11 * Math.exp(-0.23 * distance)
                * (0.72 + 0.28 * Math.cos(relationIndex * 0.37));
            model.push(
                90.0 + 18.0 * distance + 1.7 * relationIndex,
                gain,
                0.24 + 0.055 * distance
            );
            gains.push(gain);
        }
    }
    stagedModel = model;
    stagedGains = gains;
    stagedRevision = 0;
    trigger(0.72);
}

function commitStagedModel() {
    var hasStagedModel = stagedModel.length > 0;
    var rawModel = hasStagedModel ? stagedModel : committedRawModel;
    if (!rawModel.length || (!hasStagedModel && !frequencyDirty)) return;

    var gains = hasStagedModel ? stagedGains : committedGains;
    var revision = hasStagedModel ? stagedRevision : committedRevision;
    var scaledModel = scaleModelFrequencies(rawModel, frequencyMultiplier);
    outlet(4, sinusoidModel(scaledModel));
    outlet(3, gains);
    outlet(0, scaledModel);

    if (hasStagedModel) {
        committedRawModel = stagedModel.slice(0);
        committedGains = stagedGains.slice(0);
        committedRevision = revision;
        stagedModel = [];
        stagedGains = [];
        stagedRevision = -1;
    }
    frequencyDirty = false;
}

function setFrequencyMultiplier(value) {
    var next = Math.max(0.03125, Math.min(8.0, number(value, 1.0)));
    if (Math.abs(next - frequencyMultiplier) < 1.0e-12) return;
    frequencyMultiplier = next;
    frequencyDirty = true;
    status("frequency x" + next.toFixed(4) + " staged: waiting for next click");
}

function scaleModelFrequencies(rawModel, multiplier) {
    var scaled = rawModel.slice(0);
    for (var index = 0; index < scaled.length; index += 3)
        scaled[index] = Math.max(0.01, number(scaled[index], 0.01) * multiplier);
    return scaled;
}

function sinusoidModel(resonatorModel) {
    var partials = [];
    for (var index = 0; index < resonatorModel.length; index += 3) {
        partials.push(
            number(resonatorModel[index], 0.01),
            0.35 * number(resonatorModel[index + 1], 0.0),
            0.0
        );
    }
    return partials;
}

function gainVector(flatTriples) {
    var gains = [];
    for (var index = 0; index < flatTriples.length; index += 3)
        gains.push(number(flatTriples[index + 1], 0.0));
    return gains;
}

function resetPending() {
    expectedRevision = -1;
    pending = [];
    receivedRows = [];
}

function fill(count, value) {
    var result = [];
    for (var index = 0; index < count; index++) result.push(value);
    return result;
}

function number(value, fallback) {
    var result = Number(value);
    return isFinite(result) ? result : fallback;
}

function integer(value, fallback) {
    return Math.floor(number(value, fallback));
}

function status(message) {
    outlet(2, "set", message);
}
