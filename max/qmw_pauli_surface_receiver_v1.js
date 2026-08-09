// Receive revision plus 15 Pauli coefficients and build a 4x256 surface.
autowatch = 1;
inlets = 1;
outlets = 2; // status, bang buffer~ to redraw

function list() {
    var values = arrayfromargs(arguments);
    if (values.length !== 16) {
        outlet(0, ["error", "pauli15_expected_revision_plus_15", values.length]);
        return;
    }
    var revision = Math.floor(Number(values.shift()));
    var coefficients = [];
    for (var index = 0; index < 15; index++) {
        var value = Number(values[index]);
        if (!isFinite(value)) {
            outlet(0, ["error", "pauli15_nonfinite", index]);
            return;
        }
        coefficients.push(value);
    }
    var rows = [[], [], [], []], peak = 0.0;
    for (var row = 0; row < 4; row++) {
        for (var sample = 0; sample < 256; sample++) {
            var phase = 2.0 * Math.PI * sample / 256.0;
            var sum = 0.08 * Math.sin(phase);
            for (var term = 0; term < 15; term++) {
                var value = coefficients[term];
                var base = 2 * term + (value >= 0.0 ? 1 : 2);
                var harmonic = row === 0 ? base :
                    (row === 1 ? base + 12 : (row === 2 ? 2 * base : 61 - base));
                sum += Math.abs(value) * Math.sin(harmonic * phase);
            }
            rows[row].push(sum);
            peak = Math.max(peak, Math.abs(sum));
        }
    }
    if (peak > 0.95) {
        for (var r = 0; r < 4; r++)
            for (var s = 0; s < 256; s++) rows[r][s] *= 0.95 / peak;
    }
    try {
        var target = new Buffer("qmw_wavetable");
        for (var writeRow = 0; writeRow < 4; writeRow++)
            target.poke(1, writeRow * 256, rows[writeRow]);
        outlet(1, "bang");
        outlet(0, ["pauli15_surface_loaded", revision, 4, 256]);
    } catch (error) {
        outlet(0, ["error", "surface_buffer_poke_failed", String(error)]);
    }
}
