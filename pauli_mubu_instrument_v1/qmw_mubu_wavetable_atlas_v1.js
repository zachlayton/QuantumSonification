autowatch = 1;
inlets = 1;
outlets = 3;

var SOURCE_SIZE = 256;
var STREAMS = 6;
var SLOT_SIZE = 16384;
var active = 0;
var revision = 0;

function bang() { render(); }

function seed() {
    var points = [];
    for (var i = 0; i < SOURCE_SIZE; i++) {
        var phase = 2.0 * Math.PI * i / SOURCE_SIZE;
        points[i] = 0.62 * Math.sin(phase) + 0.23 * Math.sin(2.0 * phase + 0.37) +
            0.11 * Math.sin(5.0 * phase - 0.61);
    }
    normalize(points);
    new Buffer("qmw_wavetable").poke(1, 0, points);
    outlet(1, "set", "seeded local 256-sample quantum wavetable");
}

function render(value) {
    if (arguments.length) revision = Math.floor(Number(value));
    else revision += 1;
    var source;
    try {
        source = new Buffer("qmw_wavetable").peek(1, 0, SOURCE_SIZE);
    } catch (error) {
        outlet(1, "set", "atlas error: missing qmw_wavetable");
        return;
    }
    if (!(source instanceof Array)) source = [source];
    while (source.length < SOURCE_SIZE) source.push(0.0);
    var peak = 0.0;
    for (var i = 0; i < SOURCE_SIZE; i++) peak = Math.max(peak, Math.abs(Number(source[i])));
    var fallback = peak < 1.0e-7;
    if (fallback) {
        source = [];
        for (var q = 0; q < SOURCE_SIZE; q++) {
            var phase = 2.0 * Math.PI * q / SOURCE_SIZE;
            source[q] = Math.sin(phase) + 0.31 * Math.sin(3.0 * phase + 0.2);
        }
    }
    normalize(source);
    var atlas = [];
    for (var stream = 0; stream < STREAMS; stream++) {
        var phaseOffset = (stream * 37) % SOURCE_SIZE;
        var polarity = stream % 2 ? -1.0 : 1.0;
        for (var sample = 0; sample < SLOT_SIZE; sample++) {
            atlas[stream * SLOT_SIZE + sample] = polarity * source[(sample + phaseOffset) % SOURCE_SIZE];
        }
    }
    var next = 1 - active;
    var name = next ? "qmw_pauli_mubu_atlas_B" : "qmw_pauli_mubu_atlas_A";
    try {
        new Buffer(name).poke(1, 0, atlas);
    } catch (error) {
        outlet(1, "set", "atlas write error: " + String(error));
        return;
    }
    active = next;
    outlet(0, active);
    outlet(1, "set", "committed " + name + " revision=" + revision +
        " samples=" + atlas.length + (fallback ? " fallback-source" : " quantum-source"));
    outlet(2, "commit", revision, active, name, atlas.length);
}

function normalize(values) {
    var mean = 0.0;
    for (var i = 0; i < values.length; i++) mean += Number(values[i]);
    mean /= Math.max(1, values.length);
    var peak = 1.0e-12;
    for (var j = 0; j < values.length; j++) {
        values[j] = Number(values[j]) - mean;
        peak = Math.max(peak, Math.abs(values[j]));
    }
    var scale = 0.92 / peak;
    for (var k = 0; k < values.length; k++) values[k] *= scale;
}

