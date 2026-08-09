// Fixed four-cell CNMAT renderer for the clear one-qubit measurement lab.
autowatch = 1;
inlets = 1;
outlets = 4;

var COUNT = 4;
var magnitude = [0, 0, 0, 0];
var real = [0, 0, 0, 0];
var frequency = [110, 440, 440, 165];
var pan = [-0.8, -0.45, 0.45, 0.8];
var modeName = "coherent";
var outcomeValue = -1;
var expectationValue = 0.0;
var purityValue = 1.0;
var coherenceValue = 0.0;
var probabilities = [1.0, 0.0];
var collecting = false;
var haveMagnitude = false;
var haveReal = false;
var haveFrequency = false;
var havePan = false;

function anything() {
    var args = arrayfromargs(arguments);
    var name = String(messagename);
    if (name === "begin") collecting = true;
    else if (name === "end") { collecting = false; renderIfReady(); }
    else if (name === "magnitude") { magnitude = vector(args, 0.0); haveMagnitude = true; }
    else if (name === "real") { real = vector(args, 0.0); haveReal = true; }
    else if (name === "frequency_hz") { frequency = vector(args, 110.0); haveFrequency = true; }
    else if (name === "pan") { pan = vector(args, 0.0); havePan = true; }
    else if (name === "mode" && args.length) modeName = String(args[0]);
    else if (name === "outcome" && args.length) outcomeValue = Math.floor(num(args[0], -1));
    else if (name === "expectation" && args.length) expectationValue = num(args[0], 0.0);
    else if (name === "purity" && args.length) purityValue = num(args[0], 1.0);
    else if (name === "coherence" && args.length) coherenceValue = num(args[0], 0.0);
    else if (name === "final_probabilities") probabilities = vector(args, 0.0).slice(0, 2);
    if (!collecting && name !== "end") renderIfReady();
}

function vector(args, fallback) {
    var result = [];
    for (var i = 0; i < COUNT; i++) result.push(i < args.length ? num(args[i], fallback) : fallback);
    return result;
}

function renderIfReady() {
    if (!(haveMagnitude && haveReal && haveFrequency && havePan)) return;
    var left = [], right = [];
    for (var i = 0; i < COUNT; i++) {
        var amp = Math.max(0.0, magnitude[i]) * 0.52;
        var p = Math.max(-1.0, Math.min(1.0, pan[i]));
        left.push(frequency[i], amp * Math.sqrt((1.0 - p) * 0.5), 0.0);
        right.push(frequency[i], amp * Math.sqrt((1.0 + p) * 0.5), 0.0);
        outlet(2, "set", i % 2, Math.floor(i / 2), real[i]);
    }
    // These two model lists are the entire audio mapping for every protocol.
    outlet(0, left); outlet(1, right);
    var outcomeText = outcomeValue < 0 ? "none" : String(outcomeValue);
    outlet(3, "set", modeName.toUpperCase(), "outcome=" + outcomeText,
        "P(0/1)=" + probabilities[0].toFixed(3) + "/" + probabilities[1].toFixed(3),
        "purity=" + purityValue.toFixed(3), "coherence=" + coherenceValue.toFixed(3),
        "<A>=" + expectationValue.toFixed(3));
}

function num(value, fallback) { var result = Number(value); return isFinite(result) ? result : fallback; }
