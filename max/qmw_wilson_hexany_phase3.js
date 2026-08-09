autowatch = 1;
inlets = 1;
outlets = 3;

var voiceCount = 6;
var transposeSemitones = 0.0;
var baseFrequency = [220, 366.6667, 256.6667, 275, 385, 320.8333];
var activation = [0, 0, 0, 0, 0, 0];
var phase = [0, 0, 0, 0, 0, 0];
var coherence = [0, 0, 0, 0, 0, 0];
var panBase = [-0.82, -0.46, -0.12, 0.12, 0.46, 0.82];
var ratioLabel = ["1/1", "5/3", "7/6", "5/4", "7/4", "35/24"];
var factorLabel = ["1·3", "1·5", "1·7", "3·5", "3·7", "5·7"];
var currentRevision = -1;
var shellProbability = 0.0;
var leakageProbability = 1.0;
var shellPurity = 0.0;

function multiplier() {
    return Math.pow(2.0, transposeSemitones / 12.0);
}

function sendVoice(index) {
    if (index < 0 || index >= voiceCount) return;
    var dynamicPan = panBase[index] + 0.12 * Math.sin(phase[index]) * coherence[index];
    dynamicPan = Math.max(-0.95, Math.min(0.95, dynamicPan));
    outlet(0, "target", index + 1);
    outlet(0, [
        baseFrequency[index] * multiplier(),
        activation[index],
        phase[index],
        coherence[index],
        dynamicPan
    ]);
}

function definition() {
    var a = arrayfromargs(arguments);
    if (a.length >= 6) {
        outlet(2, "topology", a[1] + ")" + a[2], a[3], "voices", a[4], "anchor", a[5]);
    }
}

function edge() {
    // Static graph geometry is consumed by Processing. Max receives the same
    // packet so future coupling renderers do not require a second protocol.
}

function frame() {
    var a = arrayfromargs(arguments);
    if (a.length < 8) return;
    currentRevision = a[0];
    shellProbability = a[3];
    leakageProbability = a[4];
    shellPurity = a[5];
}

function vertex() {
    var a = arrayfromargs(arguments);
    if (a.length < 13) return;
    var index = a[1];
    if (index < 0 || index >= voiceCount) return;
    factorLabel[index] = ("" + a[3]).replace(/,/g, "·");
    ratioLabel[index] = a[4] + "/" + a[5];
    baseFrequency[index] = a[6];
    activation[index] = Math.max(0.0, Math.min(1.0, a[9]));
    phase[index] = a[10];
    coherence[index] = Math.max(0.0, Math.min(1.0, a[11]));
    sendVoice(index);
}

function end() {
    outlet(1, activation);
    outlet(
        2,
        "revision", currentRevision,
        "shell", shellProbability.toFixed(4),
        "leak", leakageProbability.toFixed(4),
        "purity", shellPurity.toFixed(4)
    );
}

function flow() {
    var a = arrayfromargs(arguments);
    if (a.length < 11) return;
    var destination = a[3];
    var conditionalFlow = Math.max(0.0, Math.min(1.0, a[7]));
    if (destination >= 0 && destination < voiceCount) {
        outlet(0, "target", destination + 1);
        outlet(0, "accent", Math.sqrt(conditionalFlow));
    }
    outlet(2, "flow", a[2], "to", destination, conditionalFlow.toFixed(4));
}

function measurement() {
    var a = arrayfromargs(arguments);
    if (a.length < 5) return;
    var vertexIndex = a[2];
    if (a[4] && vertexIndex >= 0 && vertexIndex < voiceCount) {
        outlet(0, "target", vertexIndex + 1);
        outlet(0, "accent", Math.sqrt(Math.max(0.0, Math.min(1.0, a[3]))));
    }
    outlet(2, "measurement", "basis", a[1], "vertex", vertexIndex);
}

function transpose(value) {
    transposeSemitones = Math.max(-48.0, Math.min(48.0, Number(value)));
    for (var index = 0; index < voiceCount; index++) sendVoice(index);
    outlet(2, "transposition", transposeSemitones, "semitones");
}

function test() {
    activation = [0.72, 0.36, 0.48, 0.42, 0.30, 0.58];
    phase = [0, 1.05, -0.74, 2.1, -1.6, 0.42];
    coherence = [1, 0.85, 0.72, 0.90, 0.65, 0.82];
    for (var index = 0; index < voiceCount; index++) sendVoice(index);
    outlet(1, activation);
    outlet(2, "local", "six-voice", "test");
}
