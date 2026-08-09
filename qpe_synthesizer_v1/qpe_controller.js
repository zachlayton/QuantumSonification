autowatch = 1;
inlets = 1;
outlets = 5;

var phases = [0.125, 0.301, 0.547, 0.823];
var weights = [0.42, 0.27, 0.20, 0.11];
var bits = 5;
var rootHz = 55.0;
var spanOctaves = 4.0;
var shotNumber = 0;

function clamp(value, lo, hi) { return Math.max(lo, Math.min(hi, Number(value))); }
function precision(value) { bits = Math.round(clamp(value, 2, 10)); describe(); }
function root(value) { rootHz = clamp(value, 20.0, 440.0); describe(); }
function span(value) { spanOctaves = clamp(value, 0.5, 7.0); describe(); }
function setphases() {
    var values = arrayfromargs(arguments);
    for (var i = 0; i < 4 && i < values.length; i++) phases[i] = ((Number(values[i]) % 1) + 1) % 1;
    describe();
}
function setweights() {
    var values = arrayfromargs(arguments);
    for (var i = 0; i < 4 && i < values.length; i++) weights[i] = Math.max(0, Number(values[i]));
    describe();
}

function sinc(value) {
    if (Math.abs(value) < 1e-12) return 1.0;
    return Math.sin(Math.PI * value) / (Math.PI * value);
}

function distribution(phase) {
    var size = Math.pow(2, bits);
    var values = [];
    var total = 0.0;
    for (var y = 0; y < size; y++) {
        var delta = phase - y / size;
        var ratio = sinc(size * delta) / sinc(delta);
        var probability = ratio * ratio;
        values.push(probability);
        total += probability;
    }
    for (var i = 0; i < values.length; i++) values[i] /= total;
    return values;
}

function choose(values) {
    var total = 0.0;
    for (var i = 0; i < values.length; i++) total += Math.max(0, values[i]);
    if (total <= 0) return 0;
    var draw = Math.random() * total;
    var running = 0.0;
    for (var j = 0; j < values.length; j++) {
        running += Math.max(0, values[j]);
        if (draw <= running) return j;
    }
    return values.length - 1;
}

function bitstring(value, width) {
    var text = Math.floor(value).toString(2);
    while (text.length < width) text = "0" + text;
    return text;
}

function tick() {
    var state = choose(weights);
    var probabilities = distribution(phases[state]);
    var measured = choose(probabilities);
    var size = Math.pow(2, bits);
    var measuredPhase = measured / size;
    var error = (measuredPhase - phases[state] + 0.5) % 1.0 - 0.5;
    var frequency = rootHz * Math.pow(2, spanOctaves * measuredPhase);
    var normalizedWeight = weights[state] / Math.max(0.000001, weights[0] + weights[1] + weights[2] + weights[3]);
    var gain = 0.28 + 0.42 * Math.sqrt(normalizedWeight);
    var pan = -0.8 + 1.6 * phases[state];
    shotNumber++;
    outlet(0, frequency);
    outlet(1, gain);
    outlet(2, probabilities);
    outlet(3, "set", "SHOT " + shotNumber + " | collapsed to u" + state +
        " | phase register |" + bitstring(measured, bits) + "> = " + measuredPhase.toFixed(6) +
        " | exact phi=" + phases[state].toFixed(6) + " | error=" + error.toFixed(6));
    outlet(4, pan);
}

function describe() {
    outlet(3, "set", "READY | " + bits + " estimation qubits | " + Math.pow(2, bits) +
        " phase bins | pitch range " + rootHz.toFixed(1) + "–" +
        (rootHz * Math.pow(2, spanOctaves)).toFixed(1) + " Hz");
}

function bang() { describe(); }
