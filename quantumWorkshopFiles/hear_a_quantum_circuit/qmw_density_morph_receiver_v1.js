// Receive static and evolving 256-sample tables with click-safe buffering.
autowatch = 1;
inlets = 1;
outlets = 4; // blended display, density A/B xfade, status, metrics

var TABLE_SIZE = 256;
var staticSamples = [];
var densitySamples = [];
var activeDensityBuffer = 0;
var sourceBlend = 0.0;

function anything() {
    var args = arrayfromargs(arguments);
    var name = String(messagename);
    if (name === "static") staticFrame(args);
    else if (name === "frame") densityFrame(args);
    else if (name === "metrics") densityMetrics(args);
    else if (name === "blend") blend(args.length ? args[0] : 0);
    else if (name === "clear") clear();
}

function staticFrame(args) {
    if (args.length !== TABLE_SIZE + 1) {
        status("static frame rejected: expected revision + 256 samples");
        return;
    }
    var revision = integer(args.shift(), -1);
    var points = boundedTable(args);
    if (!points) return;
    if (!writeBuffer("qmw_dm_static", points)) return;
    staticSamples = points;
    publishDisplay();
    status("static probability wavetable loaded · revision " + revision);
}

function densityFrame(args) {
    if (args.length !== TABLE_SIZE + 2) {
        status("density frame rejected: expected revision, frame + 256 samples");
        return;
    }
    var revision = integer(args.shift(), -1);
    var frame = integer(args.shift(), -1);
    var points = boundedTable(args);
    if (!points) return;
    var nextBuffer = activeDensityBuffer ? 0 : 1;
    var name = nextBuffer ? "qmw_dm_density_B" : "qmw_dm_density_A";
    if (!writeBuffer(name, points)) return;
    densitySamples = points;
    activeDensityBuffer = nextBuffer;
    outlet(1, nextBuffer);
    publishDisplay();
    status("density frame " + frame + " · revision " + revision);
}

function densityMetrics(args) {
    if (args.length !== 5) return;
    outlet(3, [
        numberValue(args[2]),
        numberValue(args[3]),
        numberValue(args[4])
    ]);
}

function blend(value) {
    sourceBlend = Math.max(0.0, Math.min(1.0, numberValue(value)));
    publishDisplay();
}

function clear() {
    var zeros = [];
    for (var i = 0; i < TABLE_SIZE; i++) zeros.push(0.0);
    writeBuffer("qmw_dm_static", zeros);
    writeBuffer("qmw_dm_density_A", zeros);
    writeBuffer("qmw_dm_density_B", zeros);
    staticSamples = [];
    densitySamples = [];
    activeDensityBuffer = 0;
    outlet(1, 0);
    outlet(0, zeros);
    status("density wavetable cleared");
}

function publishDisplay() {
    var output = [];
    var i;
    if (staticSamples.length !== TABLE_SIZE && densitySamples.length !== TABLE_SIZE) return;
    for (i = 0; i < TABLE_SIZE; i++) {
        var staticValue = staticSamples.length === TABLE_SIZE
            ? staticSamples[i] : densitySamples[i];
        var densityValue = densitySamples.length === TABLE_SIZE
            ? densitySamples[i] : staticValue;
        output.push(
            (1.0 - sourceBlend) * staticValue
            + sourceBlend * densityValue
        );
    }
    outlet(0, output);
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
