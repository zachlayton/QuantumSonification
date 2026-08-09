// Receive: revision followed by exactly 256 wavetable samples.
// Samples are written directly with Max's Buffer API.
// Outlet 1 -> multislider; outlet 2 -> status.
autowatch = 1;
inlets = 1;
outlets = 3;

function list() {
    var values = arrayfromargs(arguments);
    if (values.length !== 257) {
        outlet(2, ["error", "expected_revision_plus_256_points", values.length]);
        return;
    }
    var revision = Math.floor(Number(values.shift()));
    var points = [];
    for (var index = 0; index < 256; index++) {
        var value = Number(values[index]);
        if (!isFinite(value)) {
            outlet(2, ["error", "nonfinite_point", index]);
            return;
        }
        points.push(Math.max(-1.0, Math.min(1.0, value)));
    }
    // Keep the visual path independent so a Buffer API error cannot hide a
    // correctly received OSC table.
    outlet(1, points);
    try {
        var target = new Buffer("qmw_wavetable");
        target.poke(1, 0, points);
        outlet(2, ["loaded", revision, 256]);
    } catch (error) {
        outlet(2, ["error", "buffer_poke_failed", String(error)]);
    }
}
