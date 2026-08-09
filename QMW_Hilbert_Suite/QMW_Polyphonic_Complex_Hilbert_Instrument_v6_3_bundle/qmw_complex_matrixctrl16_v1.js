/*
    qmw_complex_matrixctrl16_v1.js

    Canonical complex 16 x 16 matrix editor for matrixctrl.

    inlet 0: matrixctrl [column row magnitude] or control messages
    inlet 1: upstream Re(rho), 256 row-major values
    inlet 2: upstream Im(rho), 256 row-major values

    outlet 0: canonical Re matrix, 256 row-major values
    outlet 1: canonical Im matrix, 256 row-major values
    outlet 2: silent UI updates for matrixctrl (set/clear)
    outlet 3: commit after both matrix lists
    outlet 4: source, safety, and selected-cell status
    outlet 5: selected [column row magnitude phase real imag]
    outlet 6: UI state [source_index hermitian safety safety_scale commit_count]
*/

autowatch = 1;
inlets = 3;
outlets = 7;

var N = 16;
var CELLS = N * N;
var upstreamRe = new Array(CELLS);
var upstreamIm = new Array(CELLS);
var manualRe = new Array(CELLS);
var manualIm = new Array(CELLS);
var currentRe = new Array(CELLS);
var currentIm = new Array(CELLS);
var upstreamReDirty = 0;
var upstreamImDirty = 0;
var sourceMode = "follow";
var morphAmount = 0.0;
var hermitianLock = 1;
var safetyEnabled = 1;
var selectedColumn = 0;
var selectedRow = 0;
var lastSafetyScale = 1.0;
var commitCount = 0;

initializeIdentity(upstreamRe, upstreamIm);
initializeIdentity(manualRe, manualIm);
initializeIdentity(currentRe, currentIm);

function numeric(value, fallback) {
    var converted = Number(value);
    return isFinite(converted) ? converted : fallback;
}

function clamp(value, low, high) {
    return Math.max(low, Math.min(high, value));
}

function initializeIdentity(realMatrix, imagMatrix) {
    var row;
    var column;
    var index;
    for (row = 0; row < N; row++) {
        for (column = 0; column < N; column++) {
            index = row * N + column;
            realMatrix[index] = row === column ? 1.0 : 0.0;
            imagMatrix[index] = 0.0;
        }
    }
}

function copyMatrix(sourceReal, sourceImag, targetReal, targetImag) {
    var index;
    for (index = 0; index < CELLS; index++) {
        targetReal[index] = numeric(sourceReal[index], 0.0);
        targetImag[index] = numeric(sourceImag[index], 0.0);
    }
}

function matrixMagnitude(realValue, imagValue) {
    return Math.sqrt(realValue * realValue + imagValue * imagValue);
}

function sourceIndex() {
    if (sourceMode === "freeze") return 1;
    if (sourceMode === "manual") return 2;
    if (sourceMode === "morph") return 3;
    return 0;
}

function safetyScaleFor(realMatrix, imagMatrix) {
    var row;
    var column;
    var index;
    var rowSum;
    var columnSum;
    var maximum = 1.0;
    if (!safetyEnabled) return 1.0;
    for (row = 0; row < N; row++) {
        rowSum = 0.0;
        columnSum = 0.0;
        for (column = 0; column < N; column++) {
            index = row * N + column;
            rowSum += matrixMagnitude(realMatrix[index], imagMatrix[index]);
            index = column * N + row;
            columnSum += matrixMagnitude(realMatrix[index], imagMatrix[index]);
        }
        maximum = Math.max(maximum, rowSum, columnSum);
    }
    return 1.0 / maximum;
}

function refreshGrid(realMatrix, imagMatrix) {
    var row;
    var column;
    var index;
    var magnitude;
    for (row = 0; row < N; row++) {
        for (column = 0; column < N; column++) {
            index = row * N + column;
            magnitude = matrixMagnitude(realMatrix[index], imagMatrix[index]);
            outlet(2, "set", column, row, magnitude);
        }
    }
}

function selectedStatus(reason) {
    var index = selectedRow * N + selectedColumn;
    var realValue = numeric(currentRe[index], 0.0);
    var imagValue = numeric(currentIm[index], 0.0);
    outlet(4, [
        "selected", reason,
        "source", sourceMode,
        "column", selectedColumn,
        "row", selectedRow,
        "magnitude", matrixMagnitude(realValue, imagValue),
        "phase", Math.atan2(imagValue, realValue),
        "real", realValue,
        "imag", imagValue,
        "hermitian", hermitianLock,
        "safety", safetyEnabled,
        "safety_scale", lastSafetyScale,
        "morph", morphAmount,
        "commit_count", commitCount
    ]);
    outlet(5, [selectedColumn, selectedRow,
        matrixMagnitude(realValue, imagValue),
        Math.atan2(imagValue, realValue), realValue, imagValue]);
    outlet(6, [sourceIndex(), hermitianLock, safetyEnabled,
        lastSafetyScale, commitCount]);
}

function emitCanonical(sourceReal, sourceImag, reason) {
    var outputReal = new Array(CELLS);
    var outputImag = new Array(CELLS);
    var index;
    lastSafetyScale = safetyScaleFor(sourceReal, sourceImag);
    for (index = 0; index < CELLS; index++) {
        outputReal[index] = numeric(sourceReal[index], 0.0) * lastSafetyScale;
        outputImag[index] = numeric(sourceImag[index], 0.0) * lastSafetyScale;
    }
    copyMatrix(outputReal, outputImag, currentRe, currentIm);
    outlet(0, outputReal);
    outlet(1, outputImag);
    commitCount += 1;
    outlet(3, "commit");
    refreshGrid(outputReal, outputImag);
    selectedStatus(reason);
}

function emitCurrentSource(reason) {
    var blendedRe;
    var blendedIm;
    var index;
    if (sourceMode === "follow") {
        emitCanonical(upstreamRe, upstreamIm, reason);
        return;
    }
    if (sourceMode === "morph") {
        blendedRe = new Array(CELLS);
        blendedIm = new Array(CELLS);
        for (index = 0; index < CELLS; index++) {
            blendedRe[index] = upstreamRe[index] * (1.0 - morphAmount)
                + manualRe[index] * morphAmount;
            blendedIm[index] = upstreamIm[index] * (1.0 - morphAmount)
                + manualIm[index] * morphAmount;
        }
        emitCanonical(blendedRe, blendedIm, reason);
        return;
    }
    emitCanonical(manualRe, manualIm, reason);
}

function acceptUpstream(values, imaginary) {
    var target;
    var index;
    if (values.length !== CELLS) {
        outlet(4, ["error", imaginary ? "upstream_im" : "upstream_re",
            "expected", CELLS, "received", values.length]);
        return;
    }
    target = imaginary ? upstreamIm : upstreamRe;
    for (index = 0; index < CELLS; index++) target[index] = numeric(values[index], 0.0);
    if (imaginary) upstreamImDirty = 1;
    else upstreamReDirty = 1;
    if (upstreamReDirty && upstreamImDirty) {
        upstreamReDirty = 0;
        upstreamImDirty = 0;
        if (sourceMode === "follow" || sourceMode === "morph") {
            emitCurrentSource("upstream_pair");
        } else {
            outlet(4, ["stored", "upstream_pair", "source", sourceMode]);
        }
    }
}

function ensureManualSource() {
    if (sourceMode !== "manual") {
        copyMatrix(currentRe, currentIm, manualRe, manualIm);
        sourceMode = "manual";
    }
}

function enforceHermitian() {
    var row;
    var column;
    var index;
    var transpose;
    var symmetricReal;
    var antisymmetricImag;
    for (row = 0; row < N; row++) {
        manualIm[row * N + row] = 0.0;
        for (column = row + 1; column < N; column++) {
            index = row * N + column;
            transpose = column * N + row;
            symmetricReal = 0.5 * (manualRe[index] + manualRe[transpose]);
            antisymmetricImag = 0.5 * (manualIm[index] - manualIm[transpose]);
            manualRe[index] = symmetricReal;
            manualRe[transpose] = symmetricReal;
            manualIm[index] = antisymmetricImag;
            manualIm[transpose] = -antisymmetricImag;
        }
    }
}

function editSelected(magnitude, phaseValue, reason) {
    var index;
    var transpose;
    var realValue;
    var imagValue;
    ensureManualSource();
    magnitude = clamp(numeric(magnitude, 0.0), 0.0, 1.0);
    phaseValue = numeric(phaseValue, 0.0);
    if (selectedRow === selectedColumn) phaseValue = 0.0;
    realValue = magnitude * Math.cos(phaseValue);
    imagValue = magnitude * Math.sin(phaseValue);
    index = selectedRow * N + selectedColumn;
    manualRe[index] = realValue;
    manualIm[index] = imagValue;
    if (hermitianLock && selectedRow !== selectedColumn) {
        transpose = selectedColumn * N + selectedRow;
        manualRe[transpose] = realValue;
        manualIm[transpose] = -imagValue;
    }
    emitCurrentSource(reason);
}

function gridcell(columnValue, rowValue, magnitudeValue) {
    var index;
    var phaseValue;
    selectedColumn = clamp(Math.floor(numeric(columnValue, 0)), 0, N - 1);
    selectedRow = clamp(Math.floor(numeric(rowValue, 0)), 0, N - 1);
    ensureManualSource();
    index = selectedRow * N + selectedColumn;
    phaseValue = Math.atan2(manualIm[index], manualRe[index]);
    editSelected(magnitudeValue, phaseValue, "grid_edit");
}

function magnitude(value) {
    var index;
    var phaseValue;
    ensureManualSource();
    index = selectedRow * N + selectedColumn;
    phaseValue = Math.atan2(manualIm[index], manualRe[index]);
    editSelected(value, phaseValue, "magnitude_edit");
}

function phase(value) {
    var index;
    var magnitudeValue;
    ensureManualSource();
    index = selectedRow * N + selectedColumn;
    magnitudeValue = matrixMagnitude(manualRe[index], manualIm[index]);
    editSelected(magnitudeValue, numeric(value, 0.0), "phase_edit");
}

function phasedeg(value) {
    phase(numeric(value, 0.0) * Math.PI / 180.0);
}

function select(columnValue, rowValue) {
    selectedColumn = clamp(Math.floor(numeric(columnValue, 0)), 0, N - 1);
    selectedRow = clamp(Math.floor(numeric(rowValue, 0)), 0, N - 1);
    selectedStatus("select");
}

function follow() {
    sourceMode = "follow";
    emitCurrentSource("follow");
}

function freeze() {
    copyMatrix(currentRe, currentIm, manualRe, manualIm);
    sourceMode = "freeze";
    emitCurrentSource("freeze");
}

function manual() {
    sourceMode = "manual";
    emitCurrentSource("manual");
}

function morph(value) {
    sourceMode = "morph";
    morphAmount = clamp(numeric(value, morphAmount), 0.0, 1.0);
    emitCurrentSource("morph");
}

function hermitian(value) {
    hermitianLock = numeric(value, hermitianLock) !== 0.0 ? 1 : 0;
    if (hermitianLock) {
        ensureManualSource();
        enforceHermitian();
        emitCurrentSource("hermitian_lock");
    } else {
        selectedStatus("hermitian_free");
    }
}

function safety(value) {
    safetyEnabled = numeric(value, safetyEnabled) !== 0.0 ? 1 : 0;
    emitCurrentSource("safety");
}

function identity() {
    initializeIdentity(manualRe, manualIm);
    sourceMode = "manual";
    emitCurrentSource("manual_identity");
}

function clearoffdiag() {
    var row;
    var column;
    ensureManualSource();
    for (row = 0; row < N; row++) {
        for (column = 0; column < N; column++) {
            if (row !== column) {
                manualRe[row * N + column] = 0.0;
                manualIm[row * N + column] = 0.0;
            }
        }
    }
    emitCurrentSource("clear_offdiagonal");
}

function status() {
    selectedStatus("query");
}

function list() {
    var values = arrayfromargs(arguments);
    if (inlet === 1) {
        acceptUpstream(values, 0);
        return;
    }
    if (inlet === 2) {
        acceptUpstream(values, 1);
        return;
    }
    if (values.length === 3) {
        gridcell(values[0], values[1], values[2]);
        return;
    }
    outlet(4, ["error", "grid_list", "expected", 3, "received", values.length]);
}

function anything() {
    outlet(4, ["error", "unknown", messagename].concat(arrayfromargs(arguments)));
}
