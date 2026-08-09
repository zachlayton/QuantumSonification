// Atomic density-wavetable receiver with click-latched double buffering.
autowatch = 1;
inlets = 2;
outlets = 4;

var expectedRevision = -1;
var expectedSamples = 256;
var expectedHarmonics = 16;
var expectedChunks = 0;
var referenceIndex = 0;
var pendingChunks = {};
var pendingAmplitudes = [];
var pendingPhases = [];
var stagedSamples = [];
var stagedAmplitudes = [];
var stagedRevision = -1;
var activeBuffer = 0;

function anything() {
    if (inlet === 1) {
        commit();
        return;
    }
    var args = arrayfromargs(arguments);
    var name = String(messagename);
    if (name === "begin") begin.apply(this, args);
    else if (name === "chunk") chunk.apply(this, args);
    else if (name === "harmonics") harmonics.apply(this, args);
    else if (name === "end") end.apply(this, args);
    else if (name === "test") test();
}

function bang() {
    if (inlet === 1) commit();
}

function begin(revision, sampleCount, harmonicCount, reference) {
    var rev = integer(revision, -1);
    var samples = integer(sampleCount, 0);
    var harmonicTotal = integer(harmonicCount, 0);
    if (rev < 0 || samples !== 256 || harmonicTotal !== 16) {
        status("rejected malformed wavetable begin");
        resetPending();
        return;
    }
    expectedRevision = rev;
    expectedSamples = samples;
    expectedHarmonics = harmonicTotal;
    expectedChunks = 0;
    referenceIndex = integer(reference, 0);
    pendingChunks = {};
    pendingAmplitudes = [];
    pendingPhases = [];
}

function chunk() {
    var args = arrayfromargs(arguments);
    if (args.length < 4 || expectedRevision < 0) return;
    var revision = integer(args.shift(), -1);
    var index = integer(args.shift(), -1);
    var total = integer(args.shift(), 0);
    if (
        revision !== expectedRevision
        || index < 0
        || total < 1
        || index >= total
    ) return;
    if (expectedChunks && total !== expectedChunks) return;
    expectedChunks = total;
    pendingChunks[index] = args.map(boundedSample);
}

function harmonics() {
    var args = arrayfromargs(arguments);
    if (args.length !== 1 + expectedHarmonics * 2) return;
    var revision = integer(args.shift(), -1);
    if (revision !== expectedRevision) return;
    pendingAmplitudes = args.slice(0, expectedHarmonics).map(numberValue);
    pendingPhases = args.slice(expectedHarmonics).map(numberValue);
}

function end(revision) {
    var rev = integer(revision, -1);
    if (rev !== expectedRevision || expectedChunks < 1) return;
    var assembled = [];
    for (var index = 0; index < expectedChunks; index++) {
        if (!pendingChunks.hasOwnProperty(index)) {
            status("incomplete wavetable " + rev + ": missing chunk " + index);
            return;
        }
        assembled = assembled.concat(pendingChunks[index]);
    }
    if (assembled.length !== expectedSamples) {
        status("rejected wavetable " + rev + ": expected 256 samples");
        resetPending();
        return;
    }
    stagedSamples = assembled;
    stagedAmplitudes = pendingAmplitudes.slice(0);
    stagedRevision = rev;
    status(
        "wavetable " + rev + " staged: reference " + referenceIndex
        + ", waiting for next temporal click"
    );
    resetPending();
}

function commit() {
    if (stagedSamples.length !== 256) return;
    var nextBuffer = activeBuffer ? 0 : 1;
    var bufferName = nextBuffer ? "qmw_tc_wave_B" : "qmw_tc_wave_A";
    try {
        var target = new Buffer(bufferName);
        target.poke(1, 0, stagedSamples);
    } catch (error) {
        status("buffer write failed: " + String(error));
        return;
    }
    outlet(0, stagedSamples);
    if (stagedAmplitudes.length === 16) outlet(3, stagedAmplitudes);
    outlet(1, nextBuffer);
    activeBuffer = nextBuffer;
    status("wavetable " + stagedRevision + " committed to " + bufferName);
    stagedSamples = [];
    stagedAmplitudes = [];
    stagedRevision = -1;
}

function test() {
    var samples = [];
    var amplitudes = [];
    for (var harmonic = 1; harmonic <= 16; harmonic++)
        amplitudes.push(Math.exp(-0.24 * (harmonic - 1)));
    for (var sample = 0; sample < 256; sample++) {
        var phase = 2.0 * Math.PI * sample / 256.0;
        var value = 0.0;
        for (harmonic = 1; harmonic <= 16; harmonic++)
            value += amplitudes[harmonic - 1]
                * Math.sin(harmonic * phase + 0.17 * harmonic);
        samples.push(value);
    }
    var peak = 0.0;
    for (sample = 0; sample < samples.length; sample++)
        peak = Math.max(peak, Math.abs(samples[sample]));
    for (sample = 0; sample < samples.length; sample++)
        samples[sample] = peak > 0.0 ? 0.95 * samples[sample] / peak : 0.0;
    stagedSamples = samples;
    stagedAmplitudes = amplitudes;
    stagedRevision = 0;
    commit();
}

function resetPending() {
    expectedRevision = -1;
    expectedChunks = 0;
    pendingChunks = {};
    pendingAmplitudes = [];
    pendingPhases = [];
}

function boundedSample(value) {
    return Math.max(-1.0, Math.min(1.0, numberValue(value)));
}

function numberValue(value) {
    var result = Number(value);
    return isFinite(result) ? result : 0.0;
}

function integer(value, fallback) {
    var result = Number(value);
    return isFinite(result) ? Math.floor(result) : fallback;
}

function status(message) {
    outlet(2, "set", message);
}
