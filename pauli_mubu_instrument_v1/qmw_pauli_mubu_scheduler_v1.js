autowatch = 1;
inlets = 1;
outlets = 6;

var magneticFactors = [-2.0, 0.0, -1.0, 1.0, 0.0, 2.0];
var modulationRates = [0.19, 0.23, 0.29, 0.31, 0.37, 0.43];
var statisticsName = "fermion";
var particleCount = 4;
var fieldValue = 1.0;
var shellCenter = 0.0;
var shellWidth = 4.0;
var exploration = 0.35;
var coherenceValue = 0.75;
var eventDensity = 0.88;
var deviationSemitones = 1.5;
var eventPeriodMs = 55.0;
var grainDurationMs = 140.0;
var positionSpread = 0.18;
var fmDepthCents = 35.0;
var sampleRate = 48000.0;
var atlasSamples = 98304;
var seedValue = 0x2468ace1;
var previous = [0, 0, 0, 0, 0, 0];
var fmPhases = [0, 0, 0, 0, 0, 0];
var initialized = false;
var epochMs = 0;

function clamp(value, low, high) {
    return Math.max(low, Math.min(high, Number(value)));
}

function maybeTick() { if (initialized) tick(); }
function statistics(value) {
    var name = String(value).toLowerCase();
    if (name === "fermion" || name === "boson" || name === "classical") {
        statisticsName = name;
        maybeTick();
    }
}
function particles(value) { particleCount = Math.max(0, Math.floor(Number(value))); maybeTick(); }
function field(value) { fieldValue = clamp(value, 0.0, 20.0); maybeTick(); }
function center(value) { shellCenter = Number(value); maybeTick(); }
function width(value) { shellWidth = Math.max(0.0, Number(value)); maybeTick(); }
function entropy(value) { exploration = clamp(value, 0.0, 1.0); maybeTick(); }
function coherence(value) { coherenceValue = clamp(value, 0.0, 1.0); maybeTick(); }
function density(value) { eventDensity = clamp(value, 0.0, 1.0); }
function deviation(value) { deviationSemitones = clamp(value, 0.0, 24.0); }
function grainperiod(value) { eventPeriodMs = clamp(value, 5.0, 2000.0); updateInterval(); }
function duration(value) { grainDurationMs = clamp(value, 2.0, 5000.0); }
function positionvar(value) { positionSpread = clamp(value, 0.0, 1.0); }
function fmindex(value) { fmDepthCents = clamp(value, 0.0, 2400.0); }
function samplerate(value) { sampleRate = Math.max(8000.0, Number(value)); }
function reseed(value) { seedValue = (Math.floor(Number(value)) >>> 0) || 1; maybeTick(); }
function bang() { tick(); }

function randomUnit() {
    seedValue = ((1664525 * seedValue + 1013904223) % 4294967296) >>> 0;
    return seedValue / 4294967296.0;
}

function accessible() {
    var result = [];
    var half = shellWidth * 0.5;
    var closest = 0;
    var closestDistance = Infinity;
    for (var i = 0; i < magneticFactors.length; i++) {
        var distance = Math.abs(fieldValue * magneticFactors[i] - shellCenter);
        if (distance <= half) result.push(i);
        if (distance < closestDistance) { closest = i; closestDistance = distance; }
    }
    if (!result.length) result.push(closest);
    return result;
}

function combination(n, k) {
    if (k < 0 || k > n) return 0;
    k = Math.min(k, n - k);
    var value = 1;
    for (var i = 1; i <= k; i++) value = value * (n - k + i) / i;
    return Math.round(value);
}

function microstates(modes, particlesValue) {
    if (statisticsName === "fermion") return particlesValue <= modes ? combination(modes, particlesValue) : 0;
    if (statisticsName === "boson") return combination(modes + particlesValue - 1, particlesValue);
    return Math.pow(modes, particlesValue);
}

function deterministicConfiguration(modes) {
    var config = [0, 0, 0, 0, 0, 0];
    if (statisticsName === "fermion") {
        for (var i = 0; i < Math.min(particleCount, modes.length); i++) config[modes[i]] = 1;
    } else if (particleCount > 0) {
        config[modes[0]] = particleCount;
    }
    return config;
}

function sampledConfiguration(modes) {
    var config = [0, 0, 0, 0, 0, 0];
    if (statisticsName === "fermion") {
        var pool = modes.slice();
        var draws = Math.min(particleCount, pool.length);
        for (var i = 0; i < draws; i++) {
            var selected = Math.floor(randomUnit() * pool.length);
            config[pool.splice(selected, 1)[0]] = 1;
        }
    } else {
        for (var particle = 0; particle < particleCount; particle++) {
            var selectedMode = modes[Math.min(modes.length - 1, Math.floor(randomUnit() * modes.length))];
            config[selectedMode] += 1;
        }
    }
    return config;
}

function tick() {
    var modes = accessible();
    var omega = microstates(modes.length, particleCount);
    var config;
    var transitionProbability = exploration * (1.0 - 0.75 * coherenceValue);
    if (omega === 0) {
        config = [0, 0, 0, 0, 0, 0];
    } else if (!initialized || omega === 1 || exploration <= 0.000001) {
        config = deterministicConfiguration(modes);
    } else if (randomUnit() <= transitionProbability) {
        config = sampledConfiguration(modes);
    } else {
        config = previous.slice();
    }
    initialized = true;
    previous = config;
    outlet(1, config);

    var entropyValue = omega > 0 ? Math.log(omega) : -1.0;
    outlet(2, "set", statisticsName.toUpperCase() + " | N=" + particleCount +
        " M=" + modes.length + " Omega=" + omega + " S/k=" + entropyValue.toFixed(4) +
        (omega === 0 ? " | EXCLUDED OVERFILL" : ""));
    appendState(modes.length, omega, entropyValue, config);
    emitGrains(config);
    advanceModulation();
}

function appendState(modeCount, omega, entropyValue, config) {
    var elapsed = Math.max(0, new Date().getTime() - epochMs);
    outlet(4, "append", elapsed, particleCount, modeCount, omega, entropyValue, fieldValue,
        config[0], config[1], config[2], config[3], config[4], config[5], statisticsName);
}

function emitGrains(config) {
    var total = 0;
    for (var i = 0; i < config.length; i++) total += config[i];
    if (total <= 0) return;
    var atlasMs = atlasSamples * 1000.0 / sampleRate;
    var slotMs = atlasMs / 6.0;
    for (var stream = 0; stream < config.length; stream++) {
        var occupancy = config[stream];
        for (var particle = 0; particle < occupancy; particle++) {
            if (randomUnit() > eventDensity) continue;
            var jitter = (randomUnit() * 2.0 - 1.0) * positionSpread * slotMs * 0.45;
            var positionMs = (stream + 0.5) * slotMs + jitter;
            var zeemanCents = fieldValue * magneticFactors[stream] * 200.0;
            var modulationCents = fmDepthCents * Math.sin(fmPhases[stream]);
            var resamplingCents = zeemanCents + modulationCents;
            var levelDb = 20.0 * Math.log(Math.sqrt(Math.max(1, occupancy) / total)) / Math.log(10.0);
            // MuBu's level control is a linear percentage (the help patch uses
            // 100), not a dB value. Keep dB for corpus metadata only.
            var levelPercent = 100.0 * Math.pow(10.0, levelDb / 20.0);
            var gains = [0, 0, 0, 0, 0, 0];
            gains[stream] = 1.0;
            outlet(0, "position", positionMs);
            outlet(0, "positionvar", positionSpread * slotMs * 0.12);
            outlet(0, "duration", grainDurationMs, 0.0);
            outlet(0, "durationvar", exploration * grainDurationMs * 0.35, 0.0);
            outlet(0, "resampling", resamplingCents);
            outlet(0, "resamplingvar", exploration * deviationSemitones * 100.0);
            outlet(0, "level", levelPercent);
            outlet(0, "levelvar", exploration * 3.0);
            outlet(0, "reverse", randomUnit() < exploration * 0.25 ? 1 : 0);
            outlet(0, "outputgains", gains[0], gains[1], gains[2], gains[3], gains[4], gains[5]);
            outlet(0, "bang");
            appendGrain(stream, positionMs, resamplingCents, grainDurationMs, levelDb);
        }
    }
}

function appendGrain(stream, positionMs, resamplingCents, durationMs, levelDb) {
    var elapsed = Math.max(0, new Date().getTime() - epochMs);
    outlet(5, "append", elapsed, stream + 1, positionMs, resamplingCents, durationMs, levelDb,
        statisticsName + "_mode_" + (stream + 1));
}

function advanceModulation() {
    for (var i = 0; i < fmPhases.length; i++) {
        fmPhases[i] += 2.0 * Math.PI * modulationRates[i] * eventPeriodMs / 1000.0;
        while (fmPhases[i] >= 2.0 * Math.PI) fmPhases[i] -= 2.0 * Math.PI;
    }
}

function initialize() {
    epochMs = new Date().getTime();
    outlet(0, "play", 0);
    outlet(0, "cyclic", 1);
    outlet(0, "microtiming", 1);
    outlet(0, "varmetro", 1);
    outlet(0, "centered", 1);
    outlet(0, "duplicatechannels", 0);
    outlet(0, "channeloffset", 0);
    outlet(0, "outputposition", 1);
    outlet(0, "attack", 0.0, 0.5);
    outlet(0, "release", 0.0, 0.5);
    updateInterval();
    tick();
}

function updateInterval() { outlet(3, eventPeriodMs); }
