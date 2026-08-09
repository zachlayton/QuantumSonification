// Quantum Matrix Bus adapter for the legacy Heisenberg OSC matrix frame.
//
// Input messages:
//   begin <revision> <dimension>
//   real <N*N values>
//   imag <N*N values>
//   magnitude <N*N values>
//   phase <N*N values>
//   frequency_hz <N*N values>
//   pan <N*N values>
//   end <revision>
//
// Matrix outlets 0-4 are published first. Outlet 5 emits the commit last; QMB
// consumers must use that commit as the transaction boundary. Outlet 6 reports
// status and rejected frames.

autowatch = 1;
inlets = 1;
outlets = 7;

var REQUIRED_FIELDS = ["real", "imag", "magnitude", "phase", "frequency_hz", "pan"];
var MATRIX_FIELDS = ["contributions", "magnitude", "phase", "frequency_hz", "pan"];
var banks = [makeBank("a"), makeBank("b")];
var activeBank = 0;
var collecting = false;
var candidateRevision = -1;
var candidateDimension = 0;
var candidateFields = {};

function makeNamedMatrix(planes, suffix) {
    var matrix = new JitterMatrix(planes, "float64", 1, 1);
    matrix.name = "qmb_heisenberg_" + suffix;
    return matrix;
}

function makeBank(label) {
    return {
        contributions: makeNamedMatrix(2, "contributions_" + label),
        magnitude: makeNamedMatrix(1, "magnitude_" + label),
        phase: makeNamedMatrix(1, "phase_" + label),
        frequency_hz: makeNamedMatrix(1, "frequency_hz_" + label),
        pan: makeNamedMatrix(1, "pan_" + label)
    };
}

function begin(revision, dimension) {
    var parsedRevision = integer(revision);
    var parsedDimension = integer(dimension);
    if (parsedRevision < 0 || parsedDimension < 1) {
        reject("invalid_begin", revision, dimension);
        return;
    }
    collecting = true;
    candidateRevision = parsedRevision;
    candidateDimension = parsedDimension;
    candidateFields = {};
    status("collecting", candidateRevision, candidateDimension);
}

function real() { acceptField("real", arguments); }
function imag() { acceptField("imag", arguments); }
function magnitude() { acceptField("magnitude", arguments); }
function phase() { acceptField("phase", arguments); }
function frequency_hz() { acceptField("frequency_hz", arguments); }
function pan() { acceptField("pan", arguments); }

function acceptField(name, argsObject) {
    if (!collecting) {
        reject("field_outside_frame", name);
        return;
    }
    var values = numericVector(argsObject);
    var expected = candidateDimension * candidateDimension;
    if (values === null || values.length !== expected) {
        reject("invalid_field", name, values === null ? -1 : values.length, expected);
        return;
    }
    candidateFields[name] = values;
}

function end(revision) {
    var parsedRevision = integer(revision);
    if (!collecting) {
        reject("end_without_begin", parsedRevision);
        return;
    }
    if (parsedRevision !== candidateRevision) {
        reject("revision_mismatch", parsedRevision, candidateRevision);
        resetCandidate();
        return;
    }
    var missing = [];
    for (var i = 0; i < REQUIRED_FIELDS.length; i++) {
        if (!candidateFields.hasOwnProperty(REQUIRED_FIELDS[i])) missing.push(REQUIRED_FIELDS[i]);
    }
    if (missing.length) {
        reject("missing_fields", missing.join(","));
        resetCandidate();
        return;
    }
    commitCandidate();
}

function commitCandidate() {
    var nextBank = 1 - activeBank;
    var bank = banks[nextBank];
    var dimension = candidateDimension;
    var count = dimension * dimension;
    var complex = new Array(count * 2);
    var realValues = candidateFields.real;
    var imagValues = candidateFields.imag;
    var i;

    for (i = 0; i < count; i++) {
        complex[2 * i] = realValues[i];
        complex[2 * i + 1] = imagValues[i];
    }

    resizeBank(bank, dimension);
    writeComplexMatrix(bank.contributions, complex, dimension);
    writeScalarMatrix(bank.magnitude, candidateFields.magnitude, dimension);
    writeScalarMatrix(bank.phase, candidateFields.phase, dimension);
    writeScalarMatrix(bank.frequency_hz, candidateFields.frequency_hz, dimension);
    writeScalarMatrix(bank.pan, candidateFields.pan, dimension);

    // Publish all candidate references before the single transaction commit.
    outlet(0, "jit_matrix", bank.contributions.name);
    outlet(1, "jit_matrix", bank.magnitude.name);
    outlet(2, "jit_matrix", bank.phase.name);
    outlet(3, "jit_matrix", bank.frequency_hz.name);
    outlet(4, "jit_matrix", bank.pan.name);
    activeBank = nextBank;
    outlet(5, "commit", candidateRevision, dimension, nextBank);
    status("committed", candidateRevision, dimension, nextBank);
    resetCandidate();
}

function resizeBank(bank, dimension) {
    for (var i = 0; i < MATRIX_FIELDS.length; i++) {
        bank[MATRIX_FIELDS[i]].dim = [dimension, dimension];
    }
}

// Max's legacy `js` object exposes setcell methods but not the V8-only
// copyarraytomatrix fast path. These explicit writes keep the adapter portable
// across both JavaScript runtimes. The matrices are inactive while being filled.
function writeComplexMatrix(matrix, values, dimension) {
    var index = 0;
    for (var row = 0; row < dimension; row++) {
        for (var column = 0; column < dimension; column++) {
            matrix.setcell2d(column, row, values[index], values[index + 1]);
            index += 2;
        }
    }
}

function writeScalarMatrix(matrix, values, dimension) {
    var index = 0;
    for (var row = 0; row < dimension; row++) {
        for (var column = 0; column < dimension; column++) {
            matrix.setcell2d(column, row, values[index]);
            index++;
        }
    }
}

function numericVector(argsObject) {
    var args = Array.prototype.slice.call(argsObject);
    var values = [];
    for (var i = 0; i < args.length; i++) {
        var value = Number(args[i]);
        if (!isFinite(value)) return null;
        values.push(value);
    }
    return values;
}

function integer(value) {
    var number = Number(value);
    if (!isFinite(number) || Math.floor(number) !== number) return -1;
    return number;
}

function resetCandidate() {
    collecting = false;
    candidateRevision = -1;
    candidateDimension = 0;
    candidateFields = {};
}

function reject() {
    var args = Array.prototype.slice.call(arguments);
    outlet.apply(this, [6, "rejected"].concat(args));
}

function status() {
    var args = Array.prototype.slice.call(arguments);
    outlet.apply(this, [6, "status"].concat(args));
}

function selftest() {
    begin(1, 2);
    real(1.0, 0.0, 0.0, -1.0);
    imag(0.0, 0.5, -0.5, 0.0);
    magnitude(1.0, 0.5, 0.5, 1.0);
    phase(0.0, 1.5707963267948966, -1.5707963267948966, 3.141592653589793);
    frequency_hz(110.0, 440.0, 440.0, 165.0);
    pan(-0.8, -0.45, 0.45, 0.8);
    end(1);
}
