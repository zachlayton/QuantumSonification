autowatch = 1;
inlets = 1;
outlets = 4;

var magneticFactors = [-2.0, 0.0, -1.0, 1.0, 0.0, 2.0];
var statisticsName = "fermion";
var particleCount = 4;
var fieldValue = 1.0;
var shellCenter = 0.0;
var shellWidth = 4.0;
var exploration = 0.35;
var coherenceValue = 0.75;
var baseDensity = 0.88;
var deviationSemitones = 1.5;
var seedValue = 0x13579bdf;
var previous = [0, 0, 0, 0, 0, 0];
var initialized = false;

function clamp(value, low, high) {
    return Math.max(low, Math.min(high, Number(value)));
}

function statistics(value) {
    var name = String(value).toLowerCase();
    if (name === "fermion" || name === "boson" || name === "classical") {
        statisticsName = name;
        tick();
    }
}

function particles(value) { particleCount = Math.max(0, Math.floor(Number(value))); tick(); }
function field(value) { fieldValue = clamp(value, 0.0, 20.0); tick(); }
function center(value) { shellCenter = Number(value); tick(); }
function width(value) { shellWidth = Math.max(0.0, Number(value)); tick(); }
function entropy(value) { exploration = clamp(value, 0.0, 1.0); updateInterval(); tick(); }
function coherence(value) { coherenceValue = clamp(value, 0.0, 1.0); updateInterval(); tick(); }
function density(value) { baseDensity = clamp(value, 0.0, 1.0); emitConfiguration(previous); }
function deviation(value) { deviationSemitones = clamp(value, 0.0, 24.0); emitConfiguration(previous); }
function reseed(value) { seedValue = (Math.floor(Number(value)) >>> 0) || 1; tick(); }
function bang() { tick(); }

function randomUnit() {
    seedValue = ((1664525 * seedValue + 1013904223) % 4294967296) >>> 0;
    return seedValue / 4294967296.0;
}

function chooseIndex(values) {
    return values[Math.min(values.length - 1, Math.floor(randomUnit() * values.length))];
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

function microstates(modes, particles) {
    if (statisticsName === "fermion") return particles <= modes ? combination(modes, particles) : 0;
    if (statisticsName === "boson") return combination(modes + particles - 1, particles);
    return Math.pow(modes, particles);
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
        for (var particle = 0; particle < particleCount; particle++) config[chooseIndex(modes)] += 1;
    }
    return config;
}

function tick() {
    var modes = accessible();
    var omega = microstates(modes.length, particleCount);
    var unique = omega <= 1;
    var config;
    if (omega === 0) {
        config = [0, 0, 0, 0, 0, 0];
    } else if (!initialized || exploration <= 0.000001 || unique) {
        config = deterministicConfiguration(modes);
    } else if (randomUnit() <= exploration) {
        config = sampledConfiguration(modes);
    } else {
        config = previous.slice();
    }
    initialized = true;
    previous = config;
    emitConfiguration(config);
    var entropyValue = omega > 0 ? Math.log(omega) : -1;
    outlet(2, "set", statisticsName.toUpperCase() + " | N=" + particleCount +
        " M=" + modes.length + " Omega=" + omega + " S/k=" + entropyValue.toFixed(4) +
        (omega === 0 ? " | EXCLUDED OVERFILL" : ""));
}

function emitConfiguration(config) {
    var total = 0;
    var peak = 0;
    for (var i = 0; i < config.length; i++) { total += config[i]; peak = Math.max(peak, config[i]); }
    var gap = 0.05 + 0.65 * (1.0 - coherenceValue);
    for (var stream = 0; stream < config.length; stream++) {
        var occupancy = config[stream];
        var active = occupancy > 0;
        var streamNumber = stream + 1;
        var probability = active ? Math.min(1.0, baseDensity * (1.0 + 0.22 * (occupancy - 1))) : 0.0;
        var amplitude = active ? Math.sqrt(occupancy / Math.max(1, total)) : 0.0;
        var energySemitones = fieldValue * magneticFactors[stream] * 2.0;
        var centerRate = Math.pow(2.0, energySemitones / 12.0);
        var deviationRatio = Math.pow(2.0, exploration * deviationSemitones / 12.0);
        var rate = centerRate / deviationRatio;
        var rateRandom = centerRate * deviationRatio - rate;
        outlet(0, "stream", streamNumber, "density", probability);
        outlet(0, "stream", streamNumber, "amp", amplitude);
        outlet(0, "stream", streamNumber, "rate", rate);
        outlet(0, "stream", streamNumber, "rateRandom", rateRandom);
        outlet(0, "stream", streamNumber, "space", gap);
        outlet(0, "stream", streamNumber, "windowRandom", exploration * 0.85);
        outlet(0, "stream", streamNumber, "delayRandom", exploration * 40.0);
        outlet(0, "stream", streamNumber, "direction", 1.0 - exploration);
    }
    var display = [];
    for (var j = 0; j < config.length; j++) display.push(peak > 0 ? config[j] / peak : 0.0);
    outlet(1, display);
}

function initialize() {
    for (var stream = 0; stream < 6; stream++) {
        outlet(0, "stream", stream + 1, "startPoint", stream / 6.0);
        outlet(0, "stream", stream + 1, "stopPoint", (stream + 1) / 6.0);
        outlet(0, "stream", stream + 1, "loopMode", 1);
    }
    updateInterval();
    tick();
}

function updateInterval() {
    var interval = 45.0 + 1955.0 * coherenceValue * (1.0 - 0.75 * exploration);
    outlet(3, Math.max(25.0, interval));
}
