// V1 density morph controls plus an independent IDEAL/IBM source comparison.
autowatch = 1;
inlets = 1;
outlets = 8;
// display, effective source, status, ideal metrics, IBM metrics, TVD,
// ideal density A/B xfade, IBM density A/B xfade

var TABLE_SIZE = 256;
var idealHarmonicSamples = [];
var idealDensitySamples = [];
var ibmHarmonicSamples = [];
var ibmDensitySamples = [];
var requestedSourceBlend = 0.0;
var mappingBlend = 0.0;
var idealRevision = -1;
var ibmRevision = -1;
var activeIdealDensityBuffer = 0;
var activeIbmDensityBuffer = 0;

function anything() {
    var args = arrayfromargs(arguments);
    var name = String(messagename);
    if (name === "ideal") densityFrame("ideal", args, false);
    else if (name === "ibm") densityFrame("ibm", args, false);
    else if (name === "ideal_frame") densityFrame("ideal", args, true);
    else if (name === "ibm_frame") densityFrame("ibm", args, true);
    else if (name === "ideal_harmonic") harmonicFrame("ideal", args);
    else if (name === "ibm_harmonic") harmonicFrame("ibm", args);
    else if (name === "metrics") metrics(args);
    else if (name === "comparison") comparison(args);
    else if (name === "source") sourceBlend(args.length ? args[0] : 0);
    else if (name === "blend") mapping(args.length ? args[0] : 0);
    else if (name === "mapping") mapping(args.length ? args[0] : 0);
    else if (name === "clear") clear();
}

function densityFrame(source, args, evolving) {
    var expected = evolving ? TABLE_SIZE + 5 : TABLE_SIZE + 1;
    if (args.length !== expected) {
        status(
            source + " density rejected: expected revision"
            + (evolving ? ", frame, metrics" : "") + " + 256 samples"
        );
        return;
    }
    var revision = integer(args.shift(), -1);
    var frame = evolving ? integer(args.shift(), -1) : 0;
    var frameMetrics = evolving
        ? [
            numberValue(args.shift()),
            numberValue(args.shift()),
            numberValue(args.shift())
        ]
        : null;
    if (source === "ideal") {
        if (evolving && idealRevision >= 0 && revision !== idealRevision) {
            status("stale ideal density frame rejected · revision " + revision);
            return;
        }
        beginIdealRevision(revision);
    } else if (idealRevision >= 0 && revision !== idealRevision) {
        status("stale IBM density frame rejected · revision " + revision);
        return;
    }

    var points = boundedTable(args);
    if (!points) return;
    if (source === "ideal") {
        activeIdealDensityBuffer = writeDensityBuffer(
            "qmw_compare_ideal_density_",
            activeIdealDensityBuffer,
            points,
            6
        );
        if (activeIdealDensityBuffer < 0) return;
        idealDensitySamples = points;
        if (frameMetrics) outlet(3, frameMetrics);
        status(
            "IDEAL density frame " + frame + " · revision " + revision
        );
    } else {
        activeIbmDensityBuffer = writeDensityBuffer(
            "qmw_compare_ibm_density_",
            activeIbmDensityBuffer,
            points,
            7
        );
        if (activeIbmDensityBuffer < 0) return;
        ibmRevision = revision;
        ibmDensitySamples = points;
        if (frameMetrics) outlet(4, frameMetrics);
        status(
            "IBM-seeded density frame " + frame + " · revision " + revision
        );
    }
    publishBlend();
}

function writeDensityBuffer(prefix, activeBuffer, points, xfadeOutlet) {
    var nextBuffer = activeBuffer ? 0 : 1;
    var name = prefix + (nextBuffer ? "B" : "A");
    if (!writeBuffer(name, points)) return -1;
    outlet(xfadeOutlet, nextBuffer);
    return nextBuffer;
}

function harmonicFrame(source, args) {
    if (args.length !== TABLE_SIZE + 1) {
        status(source + " harmonic rejected: expected revision + 256 samples");
        return;
    }
    var revision = integer(args.shift(), -1);
    if (source === "ibm" && idealRevision >= 0 && revision !== idealRevision) {
        status("stale IBM harmonic rejected · revision " + revision);
        return;
    }
    var points = boundedTable(args);
    if (!points) return;
    if (source === "ideal") {
        beginIdealRevision(revision);
        if (!writeBuffer("qmw_compare_ideal_harmonic", points)) return;
        idealHarmonicSamples = points;
        status("IDEAL static waveform ready · revision " + revision);
    } else {
        if (!writeBuffer("qmw_compare_ibm_harmonic", points)) return;
        ibmRevision = revision;
        ibmHarmonicSamples = points;
        status("IBM static waveform ready · revision " + revision);
    }
    publishBlend();
}

function beginIdealRevision(revision) {
    if (revision === idealRevision) return;
    var zeros = zeroTable();
    writeBuffer("qmw_compare_ibm_harmonic", zeros);
    writeBuffer("qmw_compare_ibm_density_A", zeros);
    writeBuffer("qmw_compare_ibm_density_B", zeros);
    ibmHarmonicSamples = [];
    ibmDensitySamples = [];
    ibmRevision = -1;
    activeIbmDensityBuffer = 0;
    idealRevision = revision;
    outlet(4, [0.0, 0.0, 0.0]);
    outlet(5, 0.0);
    outlet(7, 0);
}

function metrics(args) {
    if (args.length !== 5) return;
    var source = String(args[1]);
    var values = [
        numberValue(args[2]),
        numberValue(args[3]),
        numberValue(args[4])
    ];
    if (source === "ideal") outlet(3, values);
    else if (source === "ibm_diag") outlet(4, values);
}

function comparison(args) {
    if (args.length !== 2) return;
    outlet(5, numberValue(args[1]));
}

function sourceBlend(value) {
    requestedSourceBlend = clamp01(value);
    publishBlend();
    if (requestedSourceBlend > 0.0 && !ibmReady()) {
        status("IBM selected · waiting for hardware result");
    }
}

function mapping(value) {
    mappingBlend = clamp01(value);
    publishBlend();
    status(mappingBlend <= 0.0
        ? "STATIC mapping selected"
        : "DENSITY morph depth " + mappingBlend.toFixed(3));
}

function publishBlend() {
    if (!idealReady()) return;
    var effectiveSourceBlend = ibmReady() ? requestedSourceBlend : 0.0;
    var output = [];
    for (var i = 0; i < TABLE_SIZE; i++) {
        var idealValue = mappedValue(
            idealHarmonicSamples,
            idealDensitySamples,
            i
        );
        var ibmValue = ibmReady()
            ? mappedValue(ibmHarmonicSamples, ibmDensitySamples, i)
            : idealValue;
        output.push(
            (1.0 - effectiveSourceBlend) * idealValue
            + effectiveSourceBlend * ibmValue
        );
    }
    outlet(1, effectiveSourceBlend);
    outlet(0, output);
}

function mappedValue(harmonic, density, index) {
    var harmonicValue = harmonic.length === TABLE_SIZE
        ? harmonic[index] : density[index];
    var densityValue = density.length === TABLE_SIZE
        ? density[index] : harmonicValue;
    return (
        (1.0 - mappingBlend) * harmonicValue
        + mappingBlend * densityValue
    );
}

function idealReady() {
    return (
        idealHarmonicSamples.length === TABLE_SIZE
        || idealDensitySamples.length === TABLE_SIZE
    );
}

function ibmReady() {
    return (
        ibmHarmonicSamples.length === TABLE_SIZE
        && ibmDensitySamples.length === TABLE_SIZE
    );
}

function clear() {
    var zeros = zeroTable();
    writeBuffer("qmw_compare_ideal_harmonic", zeros);
    writeBuffer("qmw_compare_ideal_density_A", zeros);
    writeBuffer("qmw_compare_ideal_density_B", zeros);
    writeBuffer("qmw_compare_ibm_harmonic", zeros);
    writeBuffer("qmw_compare_ibm_density_A", zeros);
    writeBuffer("qmw_compare_ibm_density_B", zeros);
    idealHarmonicSamples = [];
    idealDensitySamples = [];
    ibmHarmonicSamples = [];
    ibmDensitySamples = [];
    requestedSourceBlend = 0.0;
    mappingBlend = 0.0;
    idealRevision = -1;
    ibmRevision = -1;
    activeIdealDensityBuffer = 0;
    activeIbmDensityBuffer = 0;
    outlet(1, 0.0);
    outlet(6, 0);
    outlet(7, 0);
    outlet(0, zeros);
    status("density comparison cleared");
}

function zeroTable() {
    var zeros = [];
    for (var i = 0; i < TABLE_SIZE; i++) zeros.push(0.0);
    return zeros;
}

function boundedTable(values) {
    var points = [];
    for (var i = 0; i < TABLE_SIZE; i++) {
        var value = Number(values[i]);
        if (!isFinite(value)) {
            status("non-finite wavetable sample " + i);
            return null;
        }
        points.push(Math.max(-1.0, Math.min(1.0, value)));
    }
    return points;
}

function writeBuffer(name, points) {
    try {
        var target = new Buffer(name);
        target.poke(1, 0, points);
        return true;
    } catch (error) {
        status("buffer write failed: " + String(error));
        return false;
    }
}

function clamp01(value) {
    return Math.max(0.0, Math.min(1.0, numberValue(value)));
}

function numberValue(value) {
    var result = Number(value);
    return isFinite(result) ? result : 0.0;
}

function integer(value, fallback) {
    var result = Number(value);
    return isFinite(result) ? Math.floor(result) : fallback;
}

function status(text) {
    outlet(2, "set", text);
}
