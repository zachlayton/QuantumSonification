/*
    QMW 16 x 16 unitary matrix presets v1.

    Every built-in preset is generated as a product of complex phase and
    Givens rotations.  morphamount changes rotation angles, rather than
    linearly interpolating matrix entries, so U^H U = I for the full sweep.

    Existing v6 command names are retained as aliases.  External matrices are
    deliberately rejected here; use the separately labelled expressive route
    for arbitrary, Hermitian, dissipative, or feedback matrices.
*/
autowatch = 1;
inlets = 4;
outlets = 4;

var N = 16, CELLS = 256;
var re = new Array(CELLS), im = new Array(CELLS), populations = new Array(N);
var morphAmount = 0.5, source = "identity";
var i;

for (i = 0; i < N; i++) populations[i] = i === 0 ? 1 : 0;

function num(v, fallback) {
    var x = Number(v);
    return isFinite(x) ? x : fallback;
}

function clamp01(v) { return Math.max(0, Math.min(1, num(v, 0))); }
function index(row, column) { return row * N + column; }

function setIdentity() {
    for (var k = 0; k < CELLS; k++) { re[k] = 0; im[k] = 0; }
    for (var lane = 0; lane < N; lane++) re[index(lane, lane)] = 1;
}

// Left-multiply the current matrix by a unitary complex Givens rotation.
function rotateRows(a, b, angle, phase) {
    var c = Math.cos(angle), s = Math.sin(angle);
    var pr = Math.cos(phase), pi = Math.sin(phase);
    for (var column = 0; column < N; column++) {
        var ia = index(a, column), ib = index(b, column);
        var ar = re[ia], ai = im[ia], br = re[ib], bi = im[ib];

        // rowA' = c rowA - exp(-i phase) s rowB
        re[ia] = c * ar - s * (pr * br + pi * bi);
        im[ia] = c * ai - s * (pr * bi - pi * br);

        // rowB' = exp(+i phase) s rowA + c rowB
        re[ib] = s * (pr * ar - pi * ai) + c * br;
        im[ib] = s * (pr * ai + pi * ar) + c * bi;
    }
}

function phaseRow(row, phase) {
    var pr = Math.cos(phase), pi = Math.sin(phase);
    for (var column = 0; column < N; column++) {
        var k = index(row, column), ar = re[k], ai = im[k];
        re[k] = pr * ar - pi * ai;
        im[k] = pr * ai + pi * ar;
    }
}

function diagnostics() {
    var maximumError = 0;
    for (var a = 0; a < N; a++) {
        for (var b = 0; b < N; b++) {
            var dotRe = 0, dotIm = 0;
            for (var column = 0; column < N; column++) {
                var ia = index(a, column), ib = index(b, column);
                dotRe += re[ia] * re[ib] + im[ia] * im[ib];
                dotIm += im[ia] * re[ib] - re[ia] * im[ib];
            }
            var target = a === b ? 1 : 0;
            maximumError = Math.max(maximumError,
                Math.sqrt((dotRe - target) * (dotRe - target) + dotIm * dotIm));
        }
    }
    return maximumError;
}

function emit() {
    outlet(0, re.slice(0));
    outlet(1, im.slice(0));
    outlet(3, "commit");
    outlet(2, ["matrix", source, "morph", morphAmount,
        "unitarity_error", diagnostics(), "contract", "unitary"]);
}

function rebuild() {
    setIdentity();
    var m = morphAmount;
    var peak, lane, theta;

    if (source === "diagonal_phase") {
        peak = 0;
        for (lane = 0; lane < N; lane++) peak = Math.max(peak, populations[lane]);
        peak = Math.max(peak, 0.000001);
        for (lane = 0; lane < N; lane++) {
            theta = m * Math.PI * populations[lane] / peak;
            phaseRow(lane, theta);
        }
    } else if (source === "fundamental_octave") {
        rotateRows(0, 1, m * Math.PI / 4, Math.PI / 2);
    } else if (source === "fundamental_fifth_harmonic") {
        rotateRows(0, 4, m * Math.PI / 4, Math.PI / 2);
    } else if (source === "third_seventh_harmonic") {
        rotateRows(2, 6, m * Math.PI / 4, Math.PI / 2);
    } else if (source === "unitary_coherence_ring") {
        // A chain of adjacent rotations is unitary at every intermediate m.
        for (lane = 0; lane < N - 1; lane++)
            rotateRows(lane, lane + 1, m * 0.32, (lane % 4) * Math.PI / 2);
        rotateRows(N - 1, 0, m * 0.32, 3 * Math.PI / 2);
    }
    emit();
}

function identity() { source = "identity"; rebuild(); }
function diagonal() { source = "diagonal_phase"; rebuild(); }
function fundamental_octave() { source = "fundamental_octave"; rebuild(); }
function fundamental_fifth() { source = "fundamental_fifth_harmonic"; rebuild(); }
function third_seventh() { source = "third_seventh_harmonic"; rebuild(); }
function ring() { source = "unitary_coherence_ring"; rebuild(); }
function morphamount(v) { morphAmount = clamp01(v); rebuild(); }
function imagdepth(v) {
    outlet(2, ["notice", "imagdepth_ignored", num(v, 1), "contract", "unitary"]);
}
function external() {
    outlet(2, ["error", "external_requires_expressive_route", "contract", "unitary"]);
}
function status() { emit(); }

function list() {
    var v = arrayfromargs(arguments);
    if (inlet === 2) {
        if (v.length !== N) {
            outlet(2, ["error", "populations", "expected", N, "received", v.length]);
            return;
        }
        for (var k = 0; k < N; k++) populations[k] = Math.max(0, num(v[k], 0));
        if (source === "diagonal_phase") rebuild();
        return;
    }
    outlet(2, ["error", "matrix_lists_require_expressive_route", "inlet", inlet]);
}

function anything() {
    outlet(2, ["error", "unknown", messagename].concat(arrayfromargs(arguments)));
}

identity();
