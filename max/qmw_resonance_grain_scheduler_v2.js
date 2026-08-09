// qmw_resonance_grain_scheduler_v2.js
// Four-voice resonance-grain event scheduler for QMW Surface Reverb v2.

autowatch = 1;
inlets = 1;
outlets = 7;

var enabled = 1;
var modeValue = 2;       // 0 drone, 1 grains, 2 hybrid
var sourceValue = 0;     // 0 local rates, 1 quantum rhythm matrix, 2 OSC
var probabilityValue = 0.80;
var durationMs = 180.0;
var coherenceDurationDepth = 0.65;
var attackMs = 12.0;
var randomnessValue = 0.35;
var grainLevel = 1.35;
var droneMix = 0.65;
var entropyValue = 0.5;
var voiceIndex = 0;
var tickSeconds = 0.05;
// Rates are source-owned, not locked to a ratio. Local values come from the
// four UI controls. OSC may provide an explicit four-number rate list.
// Quantum mode is event-driven from magnitude onsets and never free-runs.
var localRates = [0.85, 1.10, 1.45, 1.90];
var oscRates = [0.85, 1.10, 1.45, 1.90];
var oscRateClockActive = 0;
var polyPhases = [0.0, 0.2, 0.4, 0.6];
var laneWeights = [1.0, 0.85, 0.70, 0.55];
var quantumThreshold = 0.012;
var quantumRefractoryMs = 400.0;
var quantumStepMs = 90.0;
var quantumGroove = 0.35;
var quantumCellThreshold = 0.20;
var quantumPreviousSalience = null;
var quantumLastFireMs = -100000;
var lastQuantumPattern = "0000/0000/0000/0000";
var quantumPatternTasks = [];
for (var patternTaskIndex = 0; patternTaskIndex < 64; patternTaskIndex++)
    quantumPatternTasks[patternTaskIndex] = null;
var eventCount = 0;
var rejectedCount = 0;
var randomState = 1732050807;
var releaseTasks = [null, null, null, null];

function clamp(value, low, high) {
    value = Number(value);
    if (!isFinite(value)) value = low;
    return Math.max(low, Math.min(high, value));
}

function randomUnit() {
    // Deterministic LCG: repeatable sessions and inexpensive Max-JS execution.
    randomState = (1664525 * randomState + 1013904223) >>> 0;
    return randomState / 4294967296.0;
}

function bipolarRandom() {
    return 2.0 * randomUnit() - 1.0;
}

function sourceName() {
    if (sourceValue === 1) return "quantum";
    if (sourceValue === 2) return "osc";
    return "local";
}

function modeName() {
    if (modeValue === 0) return "drone";
    if (modeValue === 1) return "grains";
    return "hybrid";
}

function activeRates() {
    if (sourceValue === 2) return oscRates;
    return localRates;
}

function effectiveProbability(voice) {
    if (sourceValue === 1) {
        var lane = voice === undefined ? 0 : Math.round(clamp(voice, 0, 3));
        return clamp((0.08 + 0.92 * entropyValue) * laneWeights[lane], 0.0, 1.0);
    }
    return probabilityValue;
}

function emitMix() {
    var droneGain = modeValue === 0 ? 1.0 : (modeValue === 1 ? 0.0 : droneMix);
    var eventGain = modeValue === 0 ? 0.0 : grainLevel;
    outlet(4, droneGain);
    outlet(5, eventGain);
}

function emitStatus(extra) {
    var suffix = extra || "state";
    var ratesNow = activeRates();
    outlet(6, "set", "grain", modeName(), sourceName(),
        "p", effectiveProbability(0), "events", eventCount,
        "rejected", rejectedCount, "Hz",
        Number(ratesNow[0].toFixed(2)), Number(ratesNow[1].toFixed(2)),
        Number(ratesNow[2].toFixed(2)), Number(ratesNow[3].toFixed(2)),
        "qgate", Number(quantumThreshold.toFixed(3)),
        "matrix", lastQuantumPattern, "step", Number(quantumStepMs.toFixed(1)),
        "groove", Number(quantumGroove.toFixed(2)),
        "cell", Number(quantumCellThreshold.toFixed(2)), suffix);
}

function releaseEnvelope(voice, decay) {
    outlet(voice, [0.0, decay]);
    releaseTasks[voice] = null;
}

function fireVoice(voice, amplitude, duration, attack) {
    if (!enabled || modeValue === 0) return false;

    voice = Math.round(clamp(voice, 0, 3));
    amplitude = clamp(amplitude, 0.0, 1.5);
    duration = clamp(duration, 12.0, 4000.0);
    attack = clamp(attack, 0.5, Math.max(0.5, duration * 0.8));
    var decay = Math.max(5.0, duration - attack);

    if (releaseTasks[voice] !== null) releaseTasks[voice].cancel();
    // Direct line~ commands avoid message-box comma/substitution semantics.
    outlet(voice, 0.0);
    outlet(voice, [amplitude, attack]);
    releaseTasks[voice] = new Task(releaseEnvelope, this, voice, decay);
    releaseTasks[voice].schedule(attack);
    eventCount++;
    emitStatus("fired");
    return true;
}

function fire(amplitude, duration, attack) {
    var voice = voiceIndex;
    voiceIndex = (voiceIndex + 1) % 4;
    return fireVoice(voice, amplitude, duration, attack);
}

function scheduleProbabilisticEvent(voice) {
    if (!enabled || modeValue === 0) return;
    var chance = effectiveProbability(voice);
    if (randomUnit() > chance) {
        rejectedCount++;
        emitStatus("rest");
        return;
    }

    var spread = randomnessValue;
    var amplitude = clamp(0.72 + 0.28 * bipolarRandom() * spread, 0.08, 1.2);
    var voiceDurationScale = 1.0 - 0.08 * voice;
    var duration = durationMs * voiceDurationScale
        * Math.max(0.15, 1.0 + bipolarRandom() * spread);
    var attack = attackMs * Math.max(0.15, 1.0 + bipolarRandom() * 0.65 * spread);
    fireVoice(voice, amplitude, duration, attack);
}

function bang() {
    if (!enabled || modeValue === 0 || sourceValue === 1) return;
    if (sourceValue === 2 && !oscRateClockActive) return;
    var ratesNow = activeRates();
    for (var voice = 0; voice < 4; voice++) {
        polyPhases[voice] += ratesNow[voice] * tickSeconds;
        if (polyPhases[voice] >= 1.0) {
            polyPhases[voice] %= 1.0;
            scheduleProbabilisticEvent(voice);
        }
    }
}

function trigger(amplitude, duration, requestedVoice) {
    amplitude = arguments.length > 0 ? Number(amplitude) : 1.0;
    duration = arguments.length > 1 ? Number(duration) : durationMs;
    if (arguments.length > 2) {
        fireVoice(requestedVoice, amplitude, duration, attackMs);
        return;
    }
    for (var voice = 0; voice < 4; voice++)
        fireVoice(voice, amplitude, duration * (1.0 - 0.08 * voice), attackMs);
}

function external(amplitude, duration, spectralPosition) {
    // /qmw/event/resonance amplitude duration [spectral] [spatial]
    if (sourceValue !== 2) return;
    amplitude = arguments.length > 0 ? Number(amplitude) : 1.0;
    duration = arguments.length > 1 ? Number(duration) : durationMs;
    spectralPosition = arguments.length > 2 ? Number(spectralPosition) : randomUnit();
    var voice = Math.min(3, Math.floor(clamp(spectralPosition, 0.0, 1.0) * 4.0));
    fireVoice(voice, amplitude, duration, attackMs);
}

function enable(value) {
    enabled = Number(value) !== 0 ? 1 : 0;
    emitStatus(enabled ? "enabled" : "disabled");
}

function mode(value) {
    modeValue = Math.round(clamp(value, 0, 2));
    emitMix();
    emitStatus("mode");
}

function trigger_source(value) {
    sourceValue = Math.round(clamp(value, 0, 2));
    emitStatus("source");
}

// Backward-compatible alias for early v2 automation messages.
function source(value) {
    trigger_source(value);
}

function probability(value) {
    probabilityValue = clamp(value, 0.0, 1.0);
    emitStatus("probability");
}

function setRate(bank, voice, value) {
    bank[voice] = clamp(value, 0.0, 20.0);
    emitStatus("rates");
}

function local_rate0(value) { setRate(localRates, 0, value); }
function local_rate1(value) { setRate(localRates, 1, value); }
function local_rate2(value) { setRate(localRates, 2, value); }
function local_rate3(value) { setRate(localRates, 3, value); }

function setRates(bank, values) {
    if (values.length < 4) return;
    for (var voice = 0; voice < 4; voice++)
        bank[voice] = clamp(values[voice], 0.0, 20.0);
    emitStatus("rates");
}

function local_rates() {
    setRates(localRates, arrayfromargs(arguments));
}

function osc_rates() {
    oscRateClockActive = 1;
    setRates(oscRates, arrayfromargs(arguments));
}

function rates() {
    var values = arrayfromargs(arguments);
    if (sourceValue === 2) setRates(oscRates, values);
    else setRates(localRates, values);
}

// Compatibility for earlier automation: density scales all four local lanes
// equally, preserving their current independently chosen relationships.
function density(value) {
    value = clamp(value, 0.0, 20.0);
    var reference = Math.max(localRates[0], 0.000001);
    var scale = value / reference;
    for (var voice = 0; voice < 4; voice++)
        localRates[voice] = clamp(localRates[voice] * scale, 0.0, 20.0);
    emitStatus("rates");
}

function magnitudes() {
    var values = arrayfromargs(arguments);
    var sums = [0.0, 0.0, 0.0, 0.0];
    var maximum = 0.000001;
    for (var voice = 0; voice < 4; voice++) {
        for (var index = 0; index < 4; index++)
            sums[voice] += Math.max(0.0, Number(values[voice * 4 + index] || 0.0));
        maximum = Math.max(maximum, sums[voice]);
    }
    for (var lane = 0; lane < 4; lane++) {
        laneWeights[lane] = 0.20 + 0.80 * sums[lane] / maximum;
    }
}

function fireQuantumStep(taskIndex, voice, amplitude, quantumDuration) {
    fireVoice(voice, amplitude, quantumDuration, attackMs);
    quantumPatternTasks[taskIndex] = null;
}

function quantum_state(
    salience, basisIndex, purity, coherence, entropyInput, basisProbability,
    probability0, probability1, probability2, probability3,
    phase0, phase1, phase2, phase3
) {
    salience = clamp(salience, 0.0, 1.0);
    basisIndex = Math.round(clamp(basisIndex, 0, 15));
    purity = clamp(purity, 0.0, 1.0);
    coherence = clamp(coherence, 0.0, 1.0);
    entropyValue = clamp(entropyInput, 0.0, 1.0);
    basisProbability = clamp(basisProbability, 0.0, 1.0);
    var probabilities = [
        arguments.length > 6 ? clamp(probability0, 0.0, 1.0) : 0.5,
        arguments.length > 7 ? clamp(probability1, 0.0, 1.0) : 0.5,
        arguments.length > 8 ? clamp(probability2, 0.0, 1.0) : 0.5,
        arguments.length > 9 ? clamp(probability3, 0.0, 1.0) : 0.5
    ];
    var phases = [
        arguments.length > 10 ? clamp(phase0, -1.0, 1.0) : 0.0,
        arguments.length > 11 ? clamp(phase1, -1.0, 1.0) : 0.0,
        arguments.length > 12 ? clamp(phase2, -1.0, 1.0) : 0.0,
        arguments.length > 13 ? clamp(phase3, -1.0, 1.0) : 0.0
    ];

    var field = [];
    var fieldMaximum = 0.000001;
    for (var cell = 0; cell < 16; cell++) {
        var fallback = cell === basisIndex ? 1.0 : 0.0;
        var cellProbability = arguments.length > 14 + cell
            ? clamp(arguments[14 + cell], 0.0, 1.0)
            : fallback;
        field[cell] = cellProbability;
        fieldMaximum = Math.max(fieldMaximum, cellProbability);
    }
    if (quantumPreviousSalience === null) {
        quantumPreviousSalience = salience;
        return;
    }
    var salienceOnset = Math.max(0.0, salience - quantumPreviousSalience);
    quantumPreviousSalience = salience;
    var nowMs = Date.now();
    if (sourceValue !== 1) return;
    if (salienceOnset < quantumThreshold) return;
    if (nowMs - quantumLastFireMs < quantumRefractoryMs) return;
    var amplitude = clamp(
        (0.20 + 0.45 * salience + 0.25 * purity)
        * (0.75 + 0.25 * basisProbability),
        0.15, 1.25
    );
    // Bipolar exponential mapping keeps the DURATION control as the musical
    // center. At +1, coherence spans one octave below/above that duration;
    // negative depth reverses the relationship.
    var quantumDuration = clamp(
        durationMs * Math.pow(2.0, coherenceDurationDepth * (2.0 * coherence - 1.0)),
        12.0, 4000.0
    );
    var grooveWindow = quantumGroove * quantumStepMs * 0.45;
    var scheduled = false;
    for (var oldTask = 0; oldTask < quantumPatternTasks.length; oldTask++) {
        if (quantumPatternTasks[oldTask] !== null) quantumPatternTasks[oldTask].cancel();
        quantumPatternTasks[oldTask] = null;
    }
    var matrixRows = ["", "", "", ""];
    for (var matrixCell = 0; matrixCell < 16; matrixCell++) {
        var voice = Math.floor(matrixCell / 4);
        var column = matrixCell % 4;
        var normalizedProbability = field[matrixCell] / fieldMaximum;
        var strikeChance = normalizedProbability < quantumCellThreshold
            ? 0.0
            : (normalizedProbability - quantumCellThreshold)
                / Math.max(1.0 - quantumCellThreshold, 0.000001);
        if (normalizedProbability >= 0.999999) strikeChance = 1.0;
        var activeBit = randomUnit() <= strikeChance;
        matrixRows[voice] += activeBit ? "1" : "0";
        if (!activeBit) continue;
        scheduled = true;
        // Less-certain cells permit more displacement; qbit phase gives the
        // signed early/late direction.
        var cellUncertainty = 1.0 - normalizedProbability;
        var qbitUncertainty = 1.0 - Math.abs(2.0 * probabilities[voice] - 1.0);
        var uncertainty = 0.65 * cellUncertainty + 0.35 * qbitUncertainty;
        var nudge = phases[voice] * uncertainty * grooveWindow;
        var delay = column * quantumStepMs + grooveWindow + nudge;
        var cellAmplitude = amplitude * (0.35 + 0.65 * Math.sqrt(normalizedProbability));
        if (delay <= 0.001) {
            fireVoice(voice, cellAmplitude, quantumDuration, attackMs);
        } else {
            quantumPatternTasks[matrixCell] = new Task(
                fireQuantumStep, this, matrixCell, voice, cellAmplitude, quantumDuration
            );
            quantumPatternTasks[matrixCell].schedule(delay);
        }
    }
    lastQuantumPattern = matrixRows.join("/");
    quantumLastFireMs = nowMs;
    emitStatus(scheduled ? "qpattern" : "q0000");
}

function quantum_threshold(value) {
    quantumThreshold = clamp(value, 0.001, 1.0);
    emitStatus("qgate");
}

function refractory(value) {
    quantumRefractoryMs = clamp(value, 0.0, 4000.0);
    emitStatus("refractory");
}

function quantum_step(value) {
    quantumStepMs = clamp(value, 5.0, 2000.0);
    emitStatus("qstep");
}

function groove(value) {
    quantumGroove = clamp(value, 0.0, 1.0);
    emitStatus("groove");
}

function cell_threshold(value) {
    quantumCellThreshold = clamp(value, 0.0, 0.99);
    emitStatus("cell");
}

function duration(value) {
    durationMs = clamp(value, 12.0, 4000.0);
}

function coherence_duration(value) {
    coherenceDurationDepth = clamp(value, -1.0, 1.0);
    emitStatus("coh_dur");
}

function attack(value) {
    attackMs = clamp(value, 0.5, 1000.0);
}

function randomness(value) {
    randomnessValue = clamp(value, 0.0, 1.0);
}

function level(value) {
    grainLevel = clamp(value, 0.0, 3.0);
    emitMix();
}

function drone_mix(value) {
    droneMix = clamp(value, 0.0, 1.0);
    emitMix();
}

function entropy(value) {
    entropyValue = clamp(value, 0.0, 1.0);
    if (sourceValue === 1) emitStatus("entropy");
}

function seed(value) {
    randomState = (Math.floor(Number(value)) >>> 0) || 1;
}

function reset() {
    for (var index = 0; index < releaseTasks.length; index++) {
        if (releaseTasks[index] !== null) releaseTasks[index].cancel();
        releaseTasks[index] = null;
        outlet(index, 0.0);
    }
    for (var taskIndex = 0; taskIndex < quantumPatternTasks.length; taskIndex++) {
        if (quantumPatternTasks[taskIndex] !== null) quantumPatternTasks[taskIndex].cancel();
        quantumPatternTasks[taskIndex] = null;
    }
    voiceIndex = 0;
    polyPhases = [0.0, 0.2, 0.4, 0.6];
    quantumPreviousSalience = null;
    quantumLastFireMs = -100000;
    lastQuantumPattern = "0000/0000/0000/0000";
    eventCount = 0;
    rejectedCount = 0;
    randomState = 1732050807;
    emitMix();
    emitStatus("reset");
}

function loadbang() {
    emitMix();
    emitStatus("ready");
}
