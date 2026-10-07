/*
    qmw_density_matrix16_to_mcs_matrix_v1.js

    Converts a complex 16 x 16 matrix into the control-list protocol used by
    Max's mcs.matrix~ object.

    Matrix list convention (row-major):
        rho[0,0], rho[0,1], ... rho[0,15], rho[1,0], ... rho[15,15]

    mcs.matrix~ list convention:
        input_index output_index gain

    Therefore rho[row, column] is emitted as:
        column row gain

    inlet 0: 256 real values, or control messages
    inlet 1: 256 imaginary values

    outlet 0: Re(rho) control lists
    outlet 1: Im(rho) control lists
    outlet 2: validation/status messages
*/

autowatch = 1;
inlets = 2;
outlets = 3;

setinletassist(0, "Re(rho): 256 row-major floats, or control messages");
setinletassist(1, "Im(rho): 256 row-major floats");
setoutletassist(0, "Re(rho): input output gain lists for mcs.matrix~");
setoutletassist(1, "Im(rho): input output gain lists for mcs.matrix~");
setoutletassist(2, "status and matrix diagnostics");

var N = 16;
var CELLS = N * N;
var re = new Array(CELLS);
var im = new Array(CELLS);
var thresholdValue = 0.0;
var autoCommit = 1;
var haveReal = 0;
var haveImag = 0;

initializeIdentity(0);

function initializeIdentity(emitNow) {
    var row;
    var column;
    var index;

    for (row = 0; row < N; row++) {
        for (column = 0; column < N; column++) {
            index = row * N + column;
            re[index] = row === column ? 1.0 : 0.0;
            im[index] = 0.0;
        }
    }

    haveReal = 1;
    haveImag = 1;

    if (emitNow) {
        emitBoth();
    }
}

function numeric(value) {
    var converted = Number(value);
    return isFinite(converted) ? converted : 0.0;
}

function outputValue(value) {
    var converted = numeric(value);
    return Math.abs(converted) < thresholdValue ? 0.0 : converted;
}

function emitMatrix(outletIndex, matrix) {
    var row;
    var column;
    var index;

    for (row = 0; row < N; row++) {
        for (column = 0; column < N; column++) {
            index = row * N + column;
            outlet(outletIndex, [column, row, outputValue(matrix[index])]);
        }
    }
}

function emitBoth() {
    emitMatrix(0, re);
    emitMatrix(1, im);
    emitStatus("commit");
}

function emitStatus(reason) {
    var row;
    var column;
    var index;
    var transposeIndex;
    var traceRe = 0.0;
    var traceIm = 0.0;
    var hermitianError = 0.0;
    var frobeniusSquared = 0.0;
    var magnitude;
    var error;

    for (row = 0; row < N; row++) {
        index = row * N + row;
        traceRe += numeric(re[index]);
        traceIm += numeric(im[index]);

        for (column = 0; column < N; column++) {
            index = row * N + column;
            transposeIndex = column * N + row;

            error = Math.abs(numeric(re[index]) - numeric(re[transposeIndex]));
            if (error > hermitianError) {
                hermitianError = error;
            }

            error = Math.abs(numeric(im[index]) + numeric(im[transposeIndex]));
            if (error > hermitianError) {
                hermitianError = error;
            }

            magnitude = numeric(re[index]) * numeric(re[index])
                + numeric(im[index]) * numeric(im[index]);
            frobeniusSquared += magnitude;
        }
    }

    outlet(2, [
        "status",
        reason,
        "trace_re", traceRe,
        "trace_im", traceIm,
        "hermitian_error", hermitianError,
        "frobenius_sq", frobeniusSquared,
        "threshold", thresholdValue,
        "autocommit", autoCommit
    ]);
}

function acceptMatrix(values, isImaginary) {
    var target;
    var label;
    var index;

    if (values.length !== CELLS) {
        label = isImaginary ? "imag" : "real";
        outlet(2, ["error", label, "expected", CELLS, "received", values.length]);
        post("qmw rho16: " + label + " matrix requires exactly " + CELLS
            + " values; received " + values.length + "\n");
        return;
    }

    target = isImaginary ? im : re;
    for (index = 0; index < CELLS; index++) {
        target[index] = numeric(values[index]);
    }

    if (isImaginary) {
        haveImag = 1;
    } else {
        haveReal = 1;
    }

    if (autoCommit) {
        emitMatrix(isImaginary ? 1 : 0, target);
        emitStatus(isImaginary ? "imag" : "real");
    } else {
        outlet(2, ["stored", isImaginary ? "imag" : "real", CELLS]);
    }
}

function list() {
    var values = arrayfromargs(arguments);
    acceptMatrix(values, inlet === 1);
}

function real() {
    acceptMatrix(arrayfromargs(arguments), 0);
}

function imag() {
    acceptMatrix(arrayfromargs(arguments), 1);
}

function identity() {
    initializeIdentity(1);
}

function clear() {
    var index;

    for (index = 0; index < CELLS; index++) {
        re[index] = 0.0;
        im[index] = 0.0;
    }

    haveReal = 1;
    haveImag = 1;
    emitBoth();
}

function commit() {
    if (!haveReal || !haveImag) {
        outlet(2, ["warning", "commit_before_both_parts_received",
            "have_real", haveReal, "have_imag", haveImag]);
    }
    emitBoth();
}

function autocommit(value) {
    autoCommit = numeric(value) !== 0.0 ? 1 : 0;
    outlet(2, ["autocommit", autoCommit]);
}

function threshold(value) {
    thresholdValue = Math.max(0.0, numeric(value));
    outlet(2, ["threshold", thresholdValue]);
}

function realcell(row, column, value) {
    setCell(0, row, column, value);
}

function imagcell(row, column, value) {
    setCell(1, row, column, value);
}

function cell(row, column, realValue, imaginaryValue) {
    var rowIndex = Math.floor(numeric(row));
    var columnIndex = Math.floor(numeric(column));
    var index;

    if (rowIndex < 0 || rowIndex >= N || columnIndex < 0 || columnIndex >= N) {
        outlet(2, ["error", "cell_out_of_range", rowIndex, columnIndex]);
        return;
    }

    index = rowIndex * N + columnIndex;
    re[index] = numeric(realValue);
    im[index] = numeric(imaginaryValue);
    haveReal = 1;
    haveImag = 1;

    if (autoCommit) {
        emitBoth();
    } else {
        outlet(2, ["stored", "cell", rowIndex, columnIndex]);
    }
}

function setCell(isImaginary, rowValue, columnValue, value) {
    var row = Math.floor(numeric(rowValue));
    var column = Math.floor(numeric(columnValue));
    var target;

    if (row < 0 || row >= N || column < 0 || column >= N) {
        outlet(2, ["error", "cell_out_of_range", row, column]);
        return 0;
    }

    target = isImaginary ? im : re;
    target[row * N + column] = numeric(value);

    if (isImaginary) {
        haveImag = 1;
    } else {
        haveReal = 1;
    }

    if (autoCommit) {
        outlet(isImaginary ? 1 : 0,
            [column, row, outputValue(target[row * N + column])]);
        emitStatus(isImaginary ? "imagcell" : "realcell");
    }

    return 1;
}

function status() {
    emitStatus("query");
}

function anything() {
    outlet(2, ["error", "unknown_message", messagename].concat(arrayfromargs(arguments)));
}
