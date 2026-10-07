// Workshop measurement layer for the four-qubit / sixteen-partial patch.
//
// Inlet:
//   list of 16 exact computational-basis probabilities
//   measure <shots>  (one immediate shot; larger values start a stream)
//   run <shots>
//   pause
//   reset
//   exact
//
// Outlets:
//   0 sampled probabilities for the additive-synth audition
//   1 sampled probabilities for the observed-frequency histogram
//   2 participant-facing status
//   3 silence control after each short outcome tone

autowatch = 1;
inlets = 1;
outlets = 4;

var NUM_BASIS = 16;
var expected = [];
var runningCounts = [];
var runningObserved = [];
var shotTarget = 0;
var shotIndex = 0;
var shotInterval = 350;
var shotTask = null;
var silenceTask = null;

initialize();

function initialize() {
    expected = [];
    runningCounts = [];
    runningObserved = [];
    for (var i = 0; i < NUM_BASIS; i++) {
        expected.push(0);
        runningCounts.push(0);
        runningObserved.push(0);
    }
}

function list() {
    storeExpected(arrayfromargs(arguments));
}

function probabilities() {
    storeExpected(arrayfromargs(arguments));
}

function storeExpected(values) {
    cancelTasks(false);
    var total = 0;
    var next = [];
    var i;

    for (i = 0; i < NUM_BASIS; i++) {
        var value = Math.max(0, Number(values[i]) || 0);
        next.push(value);
        total += value;
    }

    if (total <= 0) {
        initialize();
        outlet(2, "set", "Circuit cleared · build a state before measuring");
        return;
    }

    for (i = 0; i < NUM_BASIS; i++) {
        next[i] /= total;
    }
    expected = next;
    outlet(2, "set", "Exact state ready · choose a shot count");
}

function measure(value) {
    var shots = Math.max(1, Math.floor(Number(value) || 1));
    run(shots);
}

function run(value) {
    var shots = Math.max(1, Math.floor(Number(value) || 1));
    if (sum(expected) <= 0) {
        outlet(2, "set", "Build a circuit before measuring");
        return;
    }

    cancelTasks();
    runningCounts = [];
    runningObserved = [];
    var i;
    for (i = 0; i < NUM_BASIS; i++) {
        runningCounts.push(0);
        runningObserved.push(0);
    }
    shotTarget = shots;
    shotIndex = 0;
    shotInterval = intervalFor(shots);
    outlet(1, runningObserved);
    outlet(2, "set", "Preparing " + shots + " fresh circuit"
        + (shots === 1 ? "" : "s") + "...");

    if (typeof Task === "undefined") {
        for (i = 0; i < shots; i++) {
            advanceShot();
        }
        return;
    }

    shotTask = new Task(advanceShot, this);
    shotTask.interval = shotInterval;
    shotTask.repeat(shots, 0);
}

function advanceShot() {
    if (shotIndex >= shotTarget) return;

    var outcome = chooseOutcome(expected);
    var oneShot = [];
    runningCounts[outcome]++;
    shotIndex++;

    for (var i = 0; i < NUM_BASIS; i++) {
        runningObserved[i] = runningCounts[i] / shotIndex;
        oneShot.push(i === outcome ? 1 : 0);
    }

    outlet(1, runningObserved);
    outlet(0, oneShot);
    scheduleSilence();

    if (shotIndex >= shotTarget) {
        outlet(
            2,
            "set",
            "COMPLETE " + shotTarget + " SHOT"
                + (shotTarget === 1 ? "" : "S")
                + " · final |" + binary4(outcome) + "〉"
                + " · H = " + formatNumber(shannonEntropy(runningObserved))
                + " bits"
        );
        if (shotTask) {
            shotTask.freepeer();
            shotTask = null;
        }
    } else {
        outlet(
            2,
            "set",
            "SHOT " + shotIndex + " / " + shotTarget
                + " → |" + binary4(outcome) + "〉 · partial " + (outcome + 1)
                + " · H = " + formatNumber(shannonEntropy(runningObserved))
        );
    }
}

function exact() {
    if (sum(expected) <= 0) {
        outlet(2, "set", "Build a circuit before returning to exact sound");
        return;
    }
    cancelTasks();
    outlet(0, expected);
    outlet(2, "set", "Auditioning exact probabilities again");
}

function pause() {
    if (shotIndex <= 0 || shotIndex >= shotTarget) {
        cancelTasks();
        outlet(2, "set", "No shot stream is currently running");
        return;
    }
    cancelTasks();
    outlet(
        2,
        "set",
        "PAUSED AFTER SHOT " + shotIndex + " / " + shotTarget
    );
}

function reset() {
    cancelTasks();
    runningCounts = [];
    runningObserved = [];
    for (var i = 0; i < NUM_BASIS; i++) {
        runningCounts.push(0);
        runningObserved.push(0);
    }
    shotTarget = 0;
    shotIndex = 0;
    outlet(1, runningObserved);
    outlet(3, "silence");
    outlet(2, "set", "Measurement stream reset · exact state is unchanged");
}

function interval(value) {
    shotInterval = Math.max(40, Number(value) || 350);
    if (shotTask && shotTask.running) {
        shotTask.interval = shotInterval;
    }
}

function intervalFor(shots) {
    if (shots <= 32) return 350;
    if (shots <= 128) return 140;
    return 70;
}

function scheduleSilence() {
    var duration = Math.max(35, Math.min(180, shotInterval * 0.65));
    if (typeof Task === "undefined") {
        outlet(3, "silence");
        return;
    }
    if (!silenceTask) {
        silenceTask = new Task(stopTone, this);
    } else {
        silenceTask.cancel();
    }
    silenceTask.schedule(duration);
}

function stopTone() {
    outlet(3, "silence");
}

function cancelTasks(stopAudio) {
    if (shotTask) {
        shotTask.cancel();
        shotTask.freepeer();
        shotTask = null;
    }
    if (silenceTask) {
        silenceTask.cancel();
    }
    if (stopAudio !== false) {
        outlet(3, "silence");
    }
}

function chooseOutcome(probabilities) {
    var draw = Math.random();
    var cumulative = 0;
    for (var i = 0; i < NUM_BASIS; i++) {
        cumulative += probabilities[i];
        if (draw < cumulative || i === NUM_BASIS - 1) {
            return i;
        }
    }
    return NUM_BASIS - 1;
}

function shannonEntropy(probabilities) {
    var entropy = 0;
    for (var i = 0; i < probabilities.length; i++) {
        var probability = probabilities[i];
        if (probability > 0) {
            entropy -= probability * (Math.log(probability) / Math.LN2);
        }
    }
    return entropy;
}

function sum(values) {
    var total = 0;
    for (var i = 0; i < values.length; i++) {
        total += values[i];
    }
    return total;
}

function firstActive(counts) {
    for (var i = 0; i < counts.length; i++) {
        if (counts[i] > 0) return i;
    }
    return 0;
}

function activeCount(counts) {
    var active = 0;
    for (var i = 0; i < counts.length; i++) {
        if (counts[i] > 0) active++;
    }
    return active;
}

function binary4(value) {
    var text = Number(value).toString(2);
    while (text.length < 4) {
        text = "0" + text;
    }
    return text;
}

function formatNumber(value) {
    return Math.round(value * 1000) / 1000;
}
