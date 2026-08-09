// Receive either the legacy revision + 256 samples packet or chunked packets:
// revision, chunk index, chunk total, followed by up to 64 samples.
// Samples are written directly with Max's Buffer API.
// Outlet 1 -> multislider; outlet 2 -> status.
autowatch = 1;
inlets = 1;
outlets = 3;

var pendingRevision = -1;
var pendingTotal = 0;
var pendingChunks = {};

function list() {
    var values = arrayfromargs(arguments);
    if (values.length === 257) {
        var legacyRevision = Math.floor(Number(values.shift()));
        loadPoints(legacyRevision, values);
        return;
    }

    if (values.length < 4) {
        outlet(2, ["error", "invalid_point_chunk", values.length]);
        return;
    }
    var revision = Math.floor(Number(values.shift()));
    var index = Math.floor(Number(values.shift()));
    var total = Math.floor(Number(values.shift()));
    if (total < 1 || index < 0 || index >= total) {
        outlet(2, ["error", "invalid_point_chunk_metadata", revision, index, total]);
        return;
    }
    if (revision !== pendingRevision || total !== pendingTotal) {
        pendingRevision = revision;
        pendingTotal = total;
        pendingChunks = {};
    }
    pendingChunks[index] = values;
    for (var chunk = 0; chunk < pendingTotal; chunk++) {
        if (!pendingChunks.hasOwnProperty(chunk)) return;
    }
    var assembled = [];
    for (var part = 0; part < pendingTotal; part++) {
        assembled = assembled.concat(pendingChunks[part]);
    }
    pendingRevision = -1;
    pendingTotal = 0;
    pendingChunks = {};
    loadPoints(revision, assembled);
}

function loadPoints(revision, values) {
    if (values.length !== 256) {
        outlet(2, ["error", "expected_256_assembled_points", values.length]);
        return;
    }
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
