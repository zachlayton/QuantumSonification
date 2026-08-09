autowatch = 1;
inlets = 1;
outlets = 4;

var graphDim = 4;
var graphReal = [];
var graphAbs = [];
var modalCount = 0;
var modalEigenvalues = [];
var modalStableIds = [];
var modalClusterIds = [];
var modalOverlap = [];
var modalAngles = [];
var modalResiduals = [];

function values(args) {
    return arrayfromargs(args);
}

function clamp01(value) {
    return Math.max(0.0, Math.min(1.0, value));
}

function graph_dimension(value) {
    graphDim = Math.max(1, Math.floor(Number(value)));
}

function graph_rho_real() {
    graphReal = values(arguments);
    drawGraph(graphReal, 0, true);
}

function graph_rho_abs() {
    graphAbs = values(arguments);
    drawGraph(graphAbs, 1, false);
}

function drawGraph(data, outletIndex, signed) {
    if (data.length !== graphDim * graphDim) {
        outlet(3, "graph matrix length " + data.length + " != " + (graphDim * graphDim));
        return;
    }
    var matrix = new JitterMatrix(4, "char", graphDim, graphDim);
    var maximum = 0.0;
    var i;
    for (i = 0; i < data.length; i++) {
        maximum = Math.max(maximum, Math.abs(Number(data[i])));
    }
    maximum = Math.max(maximum, 1.0e-15);
    for (var y = 0; y < graphDim; y++) {
        for (var x = 0; x < graphDim; x++) {
            var raw = Number(data[y * graphDim + x]);
            var normalized = signed ? raw / maximum : clamp01(raw / maximum);
            var red;
            var green;
            var blue;
            if (signed) {
                red = Math.round(32 + 223 * Math.max(normalized, 0.0));
                blue = Math.round(32 + 223 * Math.max(-normalized, 0.0));
                green = Math.round(24 + 72 * (1.0 - Math.abs(normalized)));
            } else {
                red = Math.round(255 * Math.pow(normalized, 1.5));
                green = Math.round(255 * Math.sqrt(normalized));
                blue = Math.round(80 + 175 * (1.0 - normalized));
            }
            matrix.setcell2d(x, y, [255, red, green, blue]);
        }
    }
    outlet(outletIndex, "jit_matrix", matrix.name);
}

function modal_count(value) {
    modalCount = Math.max(0, Math.floor(Number(value)));
    drawModal();
}

function modal_eigenvalues() {
    modalEigenvalues = values(arguments);
    drawModal();
}

function modal_stable_ids() {
    modalStableIds = values(arguments);
    drawModal();
}

function modal_cluster_ids() {
    modalClusterIds = values(arguments);
    drawModal();
}

function modal_overlap() {
    modalOverlap = values(arguments);
    drawModal();
}

function modal_angles() {
    modalAngles = values(arguments);
    drawModal();
}

function modal_residuals() {
    modalResiduals = values(arguments);
    drawModal();
}

function normalizedAt(data, index, minimum, maximum) {
    if (index >= data.length) {
        return 0.0;
    }
    var value = Number(data[index]);
    if (!isFinite(value)) {
        return 0.0;
    }
    return clamp01((value - minimum) / Math.max(maximum - minimum, 1.0e-15));
}

function drawModal() {
    var count = modalCount || modalEigenvalues.length;
    if (count < 1) {
        return;
    }
    var rows = 6;
    var matrix = new JitterMatrix(4, "char", count, rows);
    var eigenMin = Math.min.apply(null, modalEigenvalues);
    var eigenMax = Math.max.apply(null, modalEigenvalues);
    var stableMax = Math.max.apply(null, modalStableIds.concat([1]));
    var clusterMax = Math.max.apply(null, modalClusterIds.concat([1]));
    for (var x = 0; x < count; x++) {
        var bands = [
            normalizedAt(modalEigenvalues, x, eigenMin, eigenMax),
            normalizedAt(modalStableIds, x, 0.0, stableMax),
            normalizedAt(modalClusterIds, x, 0.0, clusterMax),
            normalizedAt(modalOverlap, x, 0.0, 1.0),
            1.0 - normalizedAt(modalAngles, x, 0.0, Math.PI / 2.0),
            1.0 - normalizedAt(modalResiduals, x, 0.0, 1.0e-4)
        ];
        for (var y = 0; y < rows; y++) {
            var value = clamp01(bands[y]);
            var red = Math.round(255 * value);
            var green = Math.round(255 * Math.sqrt(value));
            var blue = Math.round(255 * (1.0 - value));
            matrix.setcell2d(x, y, [255, red, green, blue]);
        }
    }
    outlet(2, "jit_matrix", matrix.name);
}

function status() {
    outlet(3, values(arguments).join(" "));
}

function bang() {
    if (graphReal.length) drawGraph(graphReal, 0, true);
    if (graphAbs.length) drawGraph(graphAbs, 1, false);
    drawModal();
}
