// Convert living eigenfield history into a pfft~ magnitude mask.
//
// Eigenfield phase deltas are intentionally not written into the audio FFT
// phase.  The pfft~ patch preserves its own STFT phase and uses this module
// only to build a stochastic, transient-adaptive magnitude mask.

autowatch = 1;
inlets = 1;
outlets = 2;

var BUFFER_NAME = "qmw_living_spectral_mask";
var fftSize = 4096;
var sampleRate = 48000.0;
var binCount = fftSize / 2;
var frameCount = 0;
var modeCount = 0;
var magnitudesData = [];
var frequenciesData = [];
var transientsData = [];
var blurWidthValue = 4;
var transitionValue = 1.0;
var freezeValue = 0;
var maskFloor = 0.02;
var previousMask = [];
var initializationTask = null;

function _numbers(args) {
    var source = arrayfromargs(args);
    var result = [];
    for (var i = 0; i < source.length; i++) {
        var value = Number(source[i]);
        if (isFinite(value)) {
            result.push(value);
        }
    }
    return result;
}

function shape(frames, modes) {
    frameCount = Math.max(0, Math.floor(Number(frames)));
    modeCount = Math.max(0, Math.floor(Number(modes)));
}

function magnitudes() {
    magnitudesData = _numbers(arguments);
}

function frequencies_hz() {
    frequenciesData = _numbers(arguments);
}

function transients() {
    transientsData = _numbers(arguments);
}

function blur_width(value) {
    blurWidthValue = Math.max(1, Math.floor(Number(value)));
}

function transition(value) {
    transitionValue = Math.max(0.0, Math.min(1.0, Number(value)));
}

function freeze(value) {
    freezeValue = Number(value) ? 1 : 0;
    outlet(0, ["freeze", freezeValue]);
}

function floor(value) {
    maskFloor = Math.max(0.0, Math.min(1.0, Number(value)));
}

function fft_size(value) {
    fftSize = Math.max(2, Math.floor(Number(value)));
    binCount = Math.floor(fftSize / 2);
    previousMask = [];
}

function sample_rate(value) {
    sampleRate = Math.max(1.0, Number(value));
}

function _frameOffset(frame) {
    return frame * modeCount;
}

function _frameMagnitudeMaximum(frame) {
    var offset = _frameOffset(frame);
    var maximum = 0.0;
    for (var mode = 0; mode < modeCount; mode++) {
        maximum = Math.max(maximum, Math.abs(magnitudesData[offset + mode] || 0.0));
    }
    return Math.max(maximum, 1e-12);
}

function _interpolateFrame(frame, frequency) {
    var offset = _frameOffset(frame);
    var maximum = _frameMagnitudeMaximum(frame);
    if (modeCount === 0) {
        return 1.0;
    }
    if (modeCount === 1) {
        return Math.abs(magnitudesData[offset] || 0.0) / maximum;
    }
    var firstFrequency = frequenciesData[offset] || 0.0;
    var lastFrequency = frequenciesData[offset + modeCount - 1] || firstFrequency;
    if (frequency < firstFrequency || frequency > lastFrequency) {
        return 0.0;
    }
    for (var mode = 0; mode < modeCount - 1; mode++) {
        var leftFrequency = frequenciesData[offset + mode] || 0.0;
        var rightFrequency = frequenciesData[offset + mode + 1] || leftFrequency;
        if (frequency <= rightFrequency) {
            var span = Math.max(rightFrequency - leftFrequency, 1e-12);
            var mix = Math.max(0.0, Math.min(1.0, (frequency - leftFrequency) / span));
            var left = Math.abs(magnitudesData[offset + mode] || 0.0) / maximum;
            var right = Math.abs(magnitudesData[offset + mode + 1] || 0.0) / maximum;
            return left + mix * (right - left);
        }
    }
    return Math.abs(magnitudesData[offset + modeCount - 1] || 0.0) / maximum;
}

function commit(revision) {
    if (freezeValue) {
        outlet(0, ["held", Number(revision)]);
        return;
    }
    var expected = frameCount * modeCount;
    if (!frameCount || !modeCount || magnitudesData.length < expected || frequenciesData.length < expected) {
        outlet(0, ["error", "incomplete_history", frameCount, modeCount]);
        return;
    }
    var transient = transientsData.length ? Number(transientsData[transientsData.length - 1]) : 0.0;
    transient = Math.max(0.0, Math.min(1.0, transient));
    var requested = Math.min(blurWidthValue, frameCount);
    var effectiveBlur = 1 + Math.round((requested - 1) * (1.0 - transient));
    var target = [];
    var nyquist = sampleRate * 0.5;
    for (var bin = 0; bin < binCount; bin++) {
        var frame = frameCount - 1 - Math.floor(Math.random() * effectiveBlur);
        var frequency = nyquist * bin / Math.max(binCount, 1);
        var modalValue = _interpolateFrame(frame, frequency);
        target[bin] = maskFloor + (1.0 - maskFloor) * modalValue;
    }
    var output = [];
    for (var index = 0; index < binCount; index++) {
        var previous = previousMask.length === binCount ? previousMask[index] : target[index];
        output[index] = previous + transitionValue * (target[index] - previous);
    }
    try {
        new Buffer(BUFFER_NAME).poke(1, 0, output);
        previousMask = output;
        outlet(0, ["rendered", Number(revision), effectiveBlur, transient]);
        outlet(1, transient);
    } catch (error) {
        outlet(0, ["error", String(error)]);
    }
}

function _writeDiagnosticMask(kind) {
    var output = [];
    for (var bin = 0; bin < binCount; bin++) {
        if (kind === "test") {
            output[bin] = 0.1 + 0.9 * Math.abs(Math.sin(bin * 0.025));
        } else {
            output[bin] = 1.0;
        }
    }
    try {
        new Buffer(BUFFER_NAME).poke(1, 0, output);
        previousMask = output;
        outlet(0, [kind, "mask", binCount]);
    } catch (error) {
        outlet(0, ["error", String(error)]);
    }
}

function test_mask() {
    _writeDiagnosticMask("test");
}

function passthrough() {
    _writeDiagnosticMask("passthrough");
}

function loadbang() {
    initializationTask = new Task(passthrough, this);
    initializationTask.schedule(100);
}

function bang() {
    commit(-1);
}
