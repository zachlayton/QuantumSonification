autowatch = 1;
inlets = 1;
outlets = 5;

var MAX_VOICES = 8;
var presetName = "normal";
var fieldT = 1.0;
var spreadHzPerT = 40.0;
var carrierHz = 220.0;
var bankLevel = 0.42;
var dryLevel = 0.28;

var presets = {
    normal: {
        title: "NORMAL TRIPLET",
        dry: 1.0,
        factors: [1.0],
        strengths: [1.0]
    },
    sodium_d1: {
        title: "ANOMALOUS D1 QUARTET",
        dry: 0.0,
        factors: [2.0 / 3.0, 4.0 / 3.0],
        strengths: [1.0 / 3.0, 2.0 / 3.0]
    },
    sodium_d2: {
        title: "ANOMALOUS D2 SEXTET",
        dry: 0.0,
        factors: [1.0 / 3.0, 1.0, 5.0 / 3.0],
        strengths: [2.0 / 3.0, 1.0, 1.0 / 3.0]
    }
};

function clamp(value, low, high) {
    return Math.max(low, Math.min(high, Number(value)));
}

function preset(value) {
    var key = String(value);
    if (presets[key]) {
        presetName = key;
        update();
    }
}

function field(value) {
    fieldT = clamp(value, 0.0, 20.0);
    update();
}

function spread(value) {
    spreadHzPerT = clamp(value, 0.0, 1000.0);
    update();
}

function carrier(value) {
    carrierHz = clamp(value, 20.0, 12000.0);
    update();
}

// Project integrations use a collision-resistant selector. Some Max setups
// reserve or shadow the generic `carrier` selector during JS reinstantiation.
function carrierfreq(value) {
    carrierHz = clamp(value, 20.0, 12000.0);
    update();
}

function bank(value) {
    bankLevel = clamp(value, 0.0, 1.0);
    update();
}

function dry(value) {
    dryLevel = clamp(value, 0.0, 1.0);
    update();
}

function bang() {
    update();
}

function update() {
    var data = presets[presetName];
    var shifts = [];
    var gains = [];
    var sumStrength = 0.0;
    var i;

    for (i = 0; i < data.strengths.length; i++) {
        sumStrength += data.strengths[i];
    }

    for (i = 0; i < MAX_VOICES; i++) {
        if (i < data.factors.length) {
            var shift = data.factors[i] * fieldT * spreadHzPerT;
            var gain = bankLevel * Math.sqrt(data.strengths[i] / sumStrength);
            outlet(0, "target", i + 1);
            outlet(0, "carrier", carrierHz);
            outlet(0, "shift", shift);
            outlet(0, "gain", gain);
            shifts.push(shift);
            gains.push(gain);
        } else {
            outlet(0, "target", i + 1);
            outlet(0, "gain", 0.0);
            shifts.push(0.0);
            gains.push(0.0);
        }
    }

    outlet(1, data.dry * dryLevel);
    outlet(2, shifts);
    outlet(3, gains);
    outlet(
        4,
        "set",
        data.title + " | B=" + fieldT.toFixed(3) + " T | audible scale=" +
            spreadHzPerT.toFixed(2) + " Hz/T | " + data.factors.length + " ring voices"
    );
}
