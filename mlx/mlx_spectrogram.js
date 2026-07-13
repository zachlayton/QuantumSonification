autowatch = 1;

inlets = 1;
outlets = 1;
post("mlx_spectrogram loaded\n");

var WIDTH = 128;
var HEIGHT = 16;

// 1-plane float matrix is simpler and reliable in jit.pwindow.
var matrix = new JitterMatrix(
    1,
    "float32",
    WIDTH,
    HEIGHT
);


function clamp(value, low, high) {
    return Math.max(low, Math.min(high, value));
}


function clear() {
    matrix.setall(0.0);
    outlet(0, "jit_matrix", matrix.name);
}


function list() {
    var values = arrayfromargs(arguments);

    if (values.length < HEIGHT) {
        post("mlx_spectrogram: expected 16 values, got "
            + values.length + "\n");
        return;
    }

    // Shift image left one column.
    for (var x = 0; x < WIDTH - 1; x++) {
        for (var y = 0; y < HEIGHT; y++) {
            var value = matrix.getcell(x + 1, y);
            matrix.setcell(x, y, value);
        }
    }

    // Write newest FFT frame at right edge.
    for (var bin = 0; bin < HEIGHT; bin++) {
        var magnitude = clamp(
            parseFloat(values[bin]),
            0.0,
            1.0
        );

        // Lowest FFT bin at bottom.
        var y = HEIGHT - 1 - bin;

        matrix.setcell(WIDTH - 1, y, magnitude);
    }

    outlet(0, "jit_matrix", matrix.name);
}