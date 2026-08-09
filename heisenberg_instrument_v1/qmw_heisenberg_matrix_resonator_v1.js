// Route one complete 16 x 16 transition field into 256 poly~ resonator cells.
autowatch = 1;
inlets = 1;
outlets = 3;

var DIMENSION = 16;
var CELL_COUNT = DIMENSION * DIMENSION;
var magnitude = zeros(CELL_COUNT);
var frequency = fill(CELL_COUNT, 55.0);
var phase = zeros(CELL_COUNT);
var pan = zeros(CELL_COUNT);
var haveMagnitude = false;
var haveFrequency = false;
var havePhase = false;
var havePan = false;
var currentMode = "coherent";
var currentOutcome = -1;
var currentDisturbance = 0.0;
var cellGain = 0.42;
var activityThreshold = 0.000001;
var collectingFrame = false;

function zeros(count) { return fill(count, 0.0); }

function fill(count, value) {
    var result = [];
    for (var index = 0; index < count; index++) result.push(value);
    return result;
}

function anything() {
    var args = arrayfromargs(arguments);
    var name = String(messagename);
    if (name === "begin") {
        collectingFrame = true;
    } else if (name === "end") {
        collectingFrame = false;
        renderIfReady();
    } else if (name === "magnitude" || name === "magnitude_normalized") {
        magnitude = vector(args, 0.0);
        haveMagnitude = true;
        if (!collectingFrame) renderIfReady();
    } else if (name === "frequency_hz") {
        frequency = vector(args, 55.0);
        haveFrequency = true;
        if (!collectingFrame) renderIfReady();
    } else if (name === "phase") {
        phase = vector(args, 0.0);
        havePhase = true;
        if (!collectingFrame) renderIfReady();
    } else if (name === "pan") {
        pan = vector(args, 0.0);
        havePan = true;
        if (!collectingFrame) renderIfReady();
    } else if (name === "mode" && args.length) {
        currentMode = String(args[0]);
        emitStatus();
    } else if (name === "outcome" && args.length) {
        currentOutcome = Math.floor(number(args[0], -1));
        emitStatus();
    } else if (name === "disturbance" && args.length) {
        currentDisturbance = number(args[0], 0.0);
        emitStatus();
    } else if (name === "cell_gain" && args.length) {
        cellGain = Math.max(0.0, number(args[0], 0.42));
        renderIfReady();
    } else if (name === "threshold" && args.length) {
        activityThreshold = Math.max(0.0, number(args[0], 0.000001));
        renderIfReady();
    }
}

function vector(values, fallback) {
    var result = fill(CELL_COUNT, fallback);
    var count = Math.min(CELL_COUNT, values.length);
    for (var index = 0; index < count; index++)
        result[index] = number(values[index], fallback);
    return result;
}

function renderIfReady() {
    if (!(haveMagnitude && haveFrequency && havePhase && havePan)) return;
    render();
}

function render() {
    var energy = 0.0;
    var active = 0;
    var index;
    for (index = 0; index < CELL_COUNT; index++) {
        var value = Math.max(0.0, magnitude[index]);
        if (value >= activityThreshold) {
            energy += value * value;
            active++;
        }
    }
    var normalization = energy > 0.0 ? cellGain / Math.sqrt(energy) : 0.0;

    for (index = 0; index < CELL_COUNT; index++) {
        var row = Math.floor(index / DIMENSION);
        var column = index % DIMENSION;
        var mag = Math.max(0.0, magnitude[index]);
        var amplitude = mag >= activityThreshold ? mag * normalization : 0.0;
        var decay = 35.0 + 365.0 * Math.sqrt(Math.min(1.0, mag));

        outlet(0, "target", index + 1);
        outlet(0, "frequency", Math.max(1.0, frequency[index]));
        outlet(0, "phase", phase[index]);
        outlet(0, "pan", Math.max(-1.0, Math.min(1.0, pan[index])));
        outlet(0, "decay", decay);
        outlet(0, "amplitude", amplitude);
        outlet(1, "set", column, row, mag);
    }
    outlet(0, "target", 0);
    emitStatus(active);
}

function emitStatus(active) {
    var count = typeof active === "number" ? active : -1;
    var outcome = currentOutcome < 0 ? "none" : String(currentOutcome);
    outlet(
        2,
        "set",
        "mode=" + currentMode,
        "outcome=" + outcome,
        "disturbance=" + currentDisturbance.toFixed(5),
        "active_cells=" + count
    );
}

function test() {
    for (var index = 0; index < CELL_COUNT; index++) {
        var row = Math.floor(index / DIMENSION);
        var column = index % DIMENSION;
        magnitude[index] = row === column ? 0.35 : ((row + column) % 11 === 0 ? 0.12 : 0.0);
        frequency[index] = 55.0 * Math.pow(2.0, ((row + column) % 48) / 12.0);
        phase[index] = (column - row) * 0.17;
        pan[index] = (column - row) / 15.0;
    }
    haveMagnitude = haveFrequency = havePhase = havePan = true;
    render();
}

function number(value, fallback) {
    var result = Number(value);
    return isFinite(result) ? result : fallback;
}
