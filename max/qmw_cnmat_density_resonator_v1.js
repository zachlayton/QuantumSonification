// Atomic OSC assembler and independent trigger router for CNMAT resonators~.
autowatch = 1;
inlets = 2;
outlets = 3;

var expectedRevision = -1;
var expectedDimension = 16;
var expectedResonances = 256;
var pending = [];
var receivedRows = [];
var committedRevision = -1;

function anything() {
    var args = arrayfromargs(arguments);
    var name = String(messagename);
    if (inlet === 1) {
        handleQTMPulse([name].concat(args));
        return;
    }
    dispatch(name, args);
}

function list() {
    var args = arrayfromargs(arguments);
    if (inlet === 1) handleQTMPulse(args);
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
    outlet(0, pending);
    committedRevision = rev;
    status("model " + rev + " committed: " + expectedResonances + " resonances");
    resetPending();
}

function trigger(amplitude) {
    var value = Math.max(0.0, Math.min(1.0, number(amplitude, 0.7)));
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
    var frequencies = [110, 164.81, 220, 277.18, 329.63, 440, 554.37, 659.25];
    for (var index = 0; index < frequencies.length; index++)
        model.push(frequencies[index], 0.12 / Math.sqrt(index + 1), 0.35 + index * 0.18);
    outlet(0, model);
    committedRevision = 0;
    trigger(0.72);
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
