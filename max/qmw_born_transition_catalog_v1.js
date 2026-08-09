autowatch = 1;
inlets = 1;
outlets = 5;

var rows = {};
var expected = 0;
var revision = 0;
var activeIndex = -1;
var headers = [
    "active", "species", "transition", "audio Hz", "probability",
    "duration ms", "linewidth Hz", "photon THz", "wavelength nm"
];

function cell(column, row, value) {
    outlet(0, "set", column, row, value);
}

function begin(nextRevision, count, species, mapping) {
    revision = Number(nextRevision);
    expected = Number(count);
    rows = {};
    activeIndex = -1;
    outlet(0, "clear", "all");
    for (var column = 0; column < headers.length; column++) {
        cell(column, 0, headers[column]);
    }
    outlet(4, "set", species + " — " + mapping + " — " + count + " lines");
}

function row() {
    var values = arrayfromargs(arguments);
    var index = Number(values[0]);
    rows[index] = {
        index: index,
        species: String(values[1]),
        transition: String(values[2]) + " -> " + String(values[3]),
        audio: Number(values[4]),
        probability: Number(values[5]),
        duration: Number(values[6]),
        linewidth: Number(values[7]),
        photon: Number(values[8]),
        wavelength: Number(values[9])
    };
}

function end(endRevision, count) {
    if (Number(endRevision) !== revision) {
        return;
    }
    redraw();
}

function active(eventId, index) {
    var previous = activeIndex;
    activeIndex = Number(index);
    if (previous >= 0) {
        cell(0, previous + 1, "");
    }
    cell(0, activeIndex + 1, ">");
    if (rows[activeIndex]) {
        outlet(4, "set", "event " + eventId + " — " + rows[activeIndex].species +
            " — " + rows[activeIndex].transition);
    }
}

function redraw() {
    var frequency = [];
    var probability = [];
    var duration = [];
    var frequencyMin = Infinity;
    var frequencyMax = -Infinity;
    var probabilityMax = 0;
    var durationMax = 0;

    for (var index = 0; index < expected; index++) {
        var item = rows[index];
        if (!item) {
            continue;
        }
        var displayRow = index + 1;
        cell(0, displayRow, index === activeIndex ? ">" : "");
        cell(1, displayRow, item.species);
        cell(2, displayRow, item.transition);
        cell(3, displayRow, item.audio.toFixed(3));
        cell(4, displayRow, item.probability.toFixed(6));
        cell(5, displayRow, item.duration.toFixed(3));
        cell(6, displayRow, item.linewidth.toFixed(6));
        cell(7, displayRow, item.photon.toFixed(3));
        cell(8, displayRow, item.wavelength.toFixed(3));
        var logFrequency = Math.log(Math.max(item.audio, 0.000001));
        frequency[index] = logFrequency;
        probability[index] = item.probability;
        duration[index] = item.duration;
        frequencyMin = Math.min(frequencyMin, logFrequency);
        frequencyMax = Math.max(frequencyMax, logFrequency);
        probabilityMax = Math.max(probabilityMax, item.probability);
        durationMax = Math.max(durationMax, item.duration);
    }

    var frequencyRange = Math.max(frequencyMax - frequencyMin, 0.000001);
    for (var normalizedIndex = 0; normalizedIndex < expected; normalizedIndex++) {
        frequency[normalizedIndex] =
            (frequency[normalizedIndex] - frequencyMin) / frequencyRange;
        probability[normalizedIndex] /= Math.max(probabilityMax, 0.000001);
        duration[normalizedIndex] /= Math.max(durationMax, 0.000001);
    }
    outlet(1, frequency);
    outlet(2, probability);
    outlet(3, duration);
}
