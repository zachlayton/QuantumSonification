// Atomic OSC-to-Jitter bridge and resonators~ boundary for Quantum Chladni v1.
autowatch = 1;
inlets = 5;
outlets = 25;

var revision = -1;
var modeCount = 24;
var purity = 1.0;
var entropy = 0.0;
var coherence = 0.0;
var modes = [];
var received = [];
var quantumDepth = 1.0;
var decayScale = 1.0;
var frequencyScale = 1.0;
var temporalRecord = -1;
var temporalTime = 0.0;
var temporalPhase = 0.0;
var temporalCoherence = 0.0;
var temporalPurity = 1.0;
var temporalFlux = 0.0;
var populationGate = 0.01;
var basisPopulations = fill(16, 1.0 / 16.0);
var basisPhases = fill(16, 0.0);
var previousPulseMillis = 0;
var pulseWindowMillis = 250.0;
var scheduledVoiceTasks = [];

var sampleCount = 0;
var geometryModeCount = 0;
var geometryReceived = [];
var coordinates = null;
var eigenvectors = null;
var modeMatrix = null;
var amplitudeMatrix = null;

function anything() {
    var args = arrayfromargs(arguments);
    if (inlet === 1) { quantumDepth = clip(number(args[0], 1), 0, 1); rebuild(); return; }
    if (inlet === 2) { decayScale = clip(number(args[0], 1), 0.1, 8); rebuild(); return; }
    if (inlet === 3) { frequencyScale = clip(number(args[0], 1), 0.125, 8); rebuild(); return; }
    if (inlet === 4) { populationGate = clip(number(args[0], 0.01), 0, 1); return; }
    dispatch(String(messagename), args);
}

function msg_float(value) {
    if (inlet === 1) quantumDepth = clip(value, 0, 1);
    else if (inlet === 2) decayScale = clip(value, 0.1, 8);
    else if (inlet === 3) frequencyScale = clip(value, 0.125, 8);
    else if (inlet === 4) populationGate = clip(value, 0, 1);
    rebuild();
}

function dispatch(name, args) {
    if (name === "begin") begin.apply(this, args);
    else if (name === "mode") mode.apply(this, args);
    else if (name === "end") end.apply(this, args);
    else if (name === "strike") strike(args.length ? args[0] : 0.7);
    else if (name === "status") status(args.join(" "));
    else if (name === "geometry_begin") geometry_begin.apply(this, args);
    else if (name === "geometry_vertex") geometry_vertex.apply(this, args);
    else if (name === "geometry_end") geometry_end.apply(this, args);
    else if (name === "populations") populations.apply(this, args);
    else if (name === "temporal_state") temporal_state.apply(this, args);
    else if (name === "temporal_pulse") temporal_pulse.apply(this, args);
    else if (name === "demo") demo();
}

function begin(nextRevision, count, nextPurity, nextEntropy, nextCoherence) {
    revision = integer(nextRevision, -1);
    modeCount = integer(count, 0);
    if (revision < 0 || modeCount < 1 || modeCount > 128) {
        status("rejected malformed frame");
        revision = -1;
        return;
    }
    purity = clip(number(nextPurity, 1), 0, 1);
    entropy = clip(number(nextEntropy, 0), 0, 1);
    coherence = clip(number(nextCoherence, 0), 0, 1);
    modes = new Array(modeCount);
    received = fill(modeCount, false);
}

function mode(frameRevision, index, frequency, decay, weight, probability, phase, pan) {
    var i = integer(index, -1);
    if (integer(frameRevision, -2) !== revision || i < 0 || i >= modeCount) return;
    modes[i] = [
        Math.max(1, number(frequency, 110)),
        Math.max(0.01, number(decay, 1)),
        Math.max(0, number(weight, 1)),
        Math.max(0, number(probability, 0)),
        number(phase, 0),
        clip(number(pan, 0), -1, 1)
    ];
    received[i] = true;
}

function end(frameRevision) {
    if (integer(frameRevision, -2) !== revision) return;
    for (var i = 0; i < modeCount; i++) {
        if (!received[i]) { status("incomplete quantum frame " + revision); return; }
    }
    rebuild();
}

function populations(frameRevision) {
    var args = arrayfromargs(arguments);
    if (args.length !== 33) return;
    for (var voice = 0; voice < 16; voice++) {
        basisPopulations[voice] = clip(number(args[1 + voice * 2], 0), 0, 1);
        basisPhases[voice] = number(args[2 + voice * 2], 0);
    }
}

function hasCompleteQuantumFrame() {
    if (revision < 0 || modes.length !== modeCount || received.length !== modeCount) return false;
    for (var i = 0; i < modeCount; i++) {
        if (!received[i] || !modes[i] || modes[i].length < 6) return false;
    }
    return true;
}

function spatialDimensionsMatch() {
    return eigenvectors && geometryModeCount === modeCount;
}

function rebuild() {
    // Sliders can emit while an OSC frame is between /begin and /end.  Keep
    // the previous committed output until every slot in the new frame exists.
    if (!hasCompleteQuantumFrame()) return;
    modeMatrix = new JitterMatrix(6, "float32", modeCount, 1);
    amplitudeMatrix = new JitterMatrix(2, "float32", 1, modeCount);
    var maxProbability = 0.0000001;
    var materialEnergy = 0.0;
    var shapedEnergy = 0.0;
    // The engine's 24-way projection is deliberately high-entropy.  A strong
    // sonification exponent makes its small probability contrasts audible.
    var contrastExponent = 10.0;
    for (var i = 0; i < modeCount; i++) {
        maxProbability = Math.max(maxProbability, modes[i][3]);
        materialEnergy += modes[i][2] * modes[i][2];
    }
    for (var energyIndex = 0; energyIndex < modeCount; energyIndex++) {
        var probabilityRatio = clip(modes[energyIndex][3] / maxProbability, 0.000001, 1.0);
        var material = modes[energyIndex][2];
        var selected = Math.sqrt(probabilityRatio) * Math.pow(probabilityRatio, contrastExponent);
        var shaped = (1.0 - quantumDepth) * material + quantumDepth * selected;
        shapedEnergy += shaped * shaped;
    }
    // Preserve approximate bank energy while Q changes timbre rather than volume.
    var energyCompensation = Math.sqrt(materialEnergy / Math.max(shapedEnergy, 0.0000001));
    energyCompensation = Math.min(energyCompensation, 4.0);
    var left = [];
    var right = [];
    var dominant = 0;
    var dominantProbability = -1;
    for (var index = 0; index < modeCount; index++) {
        var data = modes[index];
        var qratio = clip(data[3] / maxProbability, 0.000001, 1.0);
        // Q=0 is the fixed material spectrum; Q=1 is the quantum population
        // spectrum. This is an explicit, audible and visible crossfade.
        var materialGain = data[2];
        var quantumGain = Math.sqrt(qratio) * Math.pow(qratio, contrastExponent);
        var gain = ((1.0 - quantumDepth) * materialGain
            + quantumDepth * quantumGain) * energyCompensation;
        var pan = data[5] * quantumDepth;
        var leftGain = Math.sqrt(0.5 * (1 - pan));
        var rightGain = Math.sqrt(0.5 * (1 + pan));
        var clockPhase = data[4] + quantumDepth * temporalPhase
            * (0.35 + index / Math.max(modeCount, 1));
        var phaseBend = Math.sin(clockPhase + index * 1.61803398875);
        var frequency = data[0] * frequencyScale
            * (1.0 + quantumDepth * 0.045 * phaseBend);
        var selectedDecay = data[1] * (0.3 + 3.7 * Math.pow(qratio, 2.0));
        var decay = ((1.0 - quantumDepth) * data[1]
            + quantumDepth * selectedDecay) * decayScale;
        left.push(frequency, gain * leftGain, decay);
        right.push(frequency, gain * rightGain, decay);
        modeMatrix.setcell2d(
            index, 0,
            data[0], data[1], data[2], data[3], data[4], data[5]
        );
        amplitudeMatrix.setcell2d(
            0, index,
            gain * Math.cos(clockPhase), gain * Math.sin(clockPhase)
        );
        if (data[3] > dominantProbability) { dominantProbability = data[3]; dominant = index; }
    }
    outlet(0, left);
    outlet(1, right);
    // Six-mode resonator bank for each four-qubit computational basis state.
    // Density diagonal controls energy; the basis phase controls event offset.
    for (var voice = 0; voice < 16; voice++) {
        var bank = [];
        var populationGain = Math.sqrt(Math.max(0, basisPopulations[voice]));
        for (var slot = 0; slot < 6; slot++) {
            var bankIndex = (voice + 4 * slot) % modeCount;
            var bankData = modes[bankIndex];
            var bankRatio = clip(bankData[3] / maxProbability, 0.000001, 1.0);
            var bankMaterial = bankData[2];
            var bankQuantum = Math.sqrt(bankRatio) * Math.pow(bankRatio, contrastExponent);
            var bankGain = ((1.0 - quantumDepth) * bankMaterial
                + quantumDepth * bankQuantum) * energyCompensation * populationGain;
            var bankPhase = bankData[4] + basisPhases[voice];
            var bankFrequency = bankData[0] * frequencyScale
                * (1.0 + quantumDepth * 0.035 * Math.sin(bankPhase));
            var bankSelectedDecay = bankData[1] * (0.3 + 3.7 * bankRatio * bankRatio);
            var bankDecay = ((1.0 - quantumDepth) * bankData[1]
                + quantumDepth * bankSelectedDecay) * decayScale;
            bank.push(bankFrequency, bankGain, bankDecay);
        }
        outlet(9 + voice, bank);
    }
    outlet(3, "jit_matrix", modeMatrix.name);
    outlet(4, "jit_matrix", amplitudeMatrix.name);
    // The eigenbasis is the hot jit.la.mult inlet.  Only trigger it after the
    // amplitude vector has been rebuilt with the same inner dimension.
    if (spatialDimensionsMatch()) outlet(6, "jit_matrix", eigenvectors.name);
    if (coordinates) outlet(5, "jit_matrix", coordinates.name);
    var basis = ["noise.gradient", "fractal.multi", "fractal.multi.ridged"][dominant % 3];
    outlet(7, "basis", basis);
    outlet(7, "scale", 1.5 + 7 * entropy, 1.5 + 5 * purity, 1 + 3 * coherence);
    outlet(7, "offset", coherence * 9 + revision * 0.006, entropy * 7, purity * 3);
    status(
        "frame " + revision + " / clock record " + temporalRecord
        + " / dominant " + (dominant + 1) + " / Q " + quantumDepth.toFixed(2)
    );
}

function geometry_begin(samples, count) {
    sampleCount = integer(samples, 0);
    geometryModeCount = integer(count, 0);
    if (sampleCount < 1 || geometryModeCount < 1) return;
    coordinates = new JitterMatrix(3, "float32", 1, sampleCount);
    // Two planes make the eigenbasis explicitly complex for jit.la.mult.
    eigenvectors = new JitterMatrix(2, "float32", geometryModeCount, sampleCount);
    geometryReceived = fill(sampleCount, false);
}

function geometry_vertex() {
    var args = arrayfromargs(arguments);
    var index = integer(args[0], -1);
    if (!coordinates || index < 0 || index >= sampleCount || args.length !== 4 + geometryModeCount) return;
    coordinates.setcell2d(
        0, index,
        number(args[1], 0), number(args[2], 0), number(args[3], 0)
    );
    for (var modeIndex = 0; modeIndex < geometryModeCount; modeIndex++) {
        eigenvectors.setcell2d(
            modeIndex, index, number(args[4 + modeIndex], 0), 0
        );
    }
    geometryReceived[index] = true;
}

function geometry_end(samples) {
    if (integer(samples, -1) !== sampleCount) return;
    for (var i = 0; i < sampleCount; i++) if (!geometryReceived[i]) return;
    outlet(5, "jit_matrix", coordinates.name);
    if (hasCompleteQuantumFrame() && spatialDimensionsMatch()) {
        // rebuild sends the matching amplitude matrix to the cold inlet first,
        // then the eigenbasis to the hot inlet.
        rebuild();
        status("Jitter geometry committed: " + sampleCount + " samples x " + geometryModeCount + " modes");
    } else {
        status("Jitter geometry buffered: waiting for matching " + geometryModeCount + "-mode quantum frame");
    }
}

function strike(value) { outlet(2, clip(number(value, 0.7), 0, 1)); }

function temporal_state(sourceRevision, record, intrinsicTime, deltaBures,
    remainder, phase, nextCoherence, nextPurity, populationFlux) {
    temporalRecord = integer(record, temporalRecord);
    temporalTime = number(intrinsicTime, temporalTime);
    temporalPhase = number(phase, temporalPhase);
    temporalCoherence = clip(number(nextCoherence, temporalCoherence), 0, 1);
    temporalPurity = clip(number(nextPurity, temporalPurity), 0, 1);
    temporalFlux = Math.max(0, number(populationFlux, temporalFlux));
    rebuild();
}

function temporal_pulse(record, intrinsicTime, deltaBures, phase, nextCoherence,
    populationFlux, coherenceFlux, nextPurity, negativity, projectionError,
    coherenceGain, hazardIncrement) {
    temporalRecord = integer(record, temporalRecord);
    temporalTime = number(intrinsicTime, temporalTime);
    temporalPhase = number(phase, temporalPhase);
    temporalCoherence = clip(number(nextCoherence, temporalCoherence), 0, 1);
    temporalPurity = clip(number(nextPurity, temporalPurity), 0, 1);
    temporalFlux = Math.max(0, number(populationFlux, temporalFlux));
    var distanceEnergy = clip(number(deltaBures, 0) / 0.05, 0, 1);
    var fluxEnergy = clip(temporalFlux * 8.0, 0, 1);
    var gainEnergy = clip(number(coherenceGain, 1) / 4.0, 0, 1);
    var pulseEnergy = 0.16 + 0.34 * distanceEnergy + 0.22 * fluxEnergy + 0.12 * gainEnergy;
    var now = new Date().getTime();
    if (previousPulseMillis > 0) {
        var measuredWindow = now - previousPulseMillis;
        pulseWindowMillis = 0.75 * pulseWindowMillis
            + 0.25 * clip(measuredWindow, 40, 1200);
    }
    previousPulseMillis = now;
    var maximumPopulation = 0.000001;
    for (var maximumIndex = 0; maximumIndex < 16; maximumIndex++)
        maximumPopulation = Math.max(maximumPopulation, basisPopulations[maximumIndex]);
    for (var voice = 0; voice < 16; voice++) {
        var voicePopulation = basisPopulations[voice];
        if (voicePopulation < populationGate) continue;
        var normalizedPhase = basisPhases[voice] / (2.0 * Math.PI);
        normalizedPhase = normalizedPhase - Math.floor(normalizedPhase);
        var delayMillis = normalizedPhase * Math.min(900, 0.92 * pulseWindowMillis);
        var voiceEnergy = pulseEnergy * Math.sqrt(voicePopulation / maximumPopulation);
        var task = new Task(temporal_voice_strike, this, voice, voiceEnergy);
        scheduledVoiceTasks.push(task);
        task.schedule(delayMillis);
    }
    if (scheduledVoiceTasks.length > 256)
        scheduledVoiceTasks = scheduledVoiceTasks.slice(scheduledVoiceTasks.length - 128);
    status("TEMPORAL STRIKE record " + temporalRecord
        + " / intrinsic time " + temporalTime.toFixed(3));
}

function temporal_voice_strike(voice, amplitude) {
    outlet(9 + integer(voice, 0), clip(number(amplitude, 0.2), 0, 1));
}

function demo() {
    // Supply a complete 32 x 24 surface and 24 analytic eigenmodes.  The old
    // demo only made resonator lists, leaving jit.gl.mesh with zero vertices.
    var columns = 32;
    var rows = 24;
    var samples = columns * rows;
    geometry_begin(samples, 24);
    for (var yIndex = 0; yIndex < rows; yIndex++) {
        for (var xIndex = 0; xIndex < columns; xIndex++) {
            var x = -1 + 2 * xIndex / (columns - 1);
            var y = -1 + 2 * yIndex / (rows - 1);
            var vertex = [yIndex * columns + xIndex, x, y, 0];
            for (var modeIndex = 0; modeIndex < 24; modeIndex++) {
                var mx = 1 + (modeIndex % 6);
                var my = 1 + Math.floor(modeIndex / 6);
                vertex.push(Math.sin(mx * Math.PI * (x + 1) * 0.5)
                    * Math.sin(my * Math.PI * (y + 1) * 0.5));
            }
            geometry_vertex.apply(this, vertex);
        }
    }
    geometry_end(samples);
    begin(0, 24, 0.79, 0.24, 0.59);
    for (var i = 0; i < 24; i++) {
        var probability = 0.4 + 0.6 * Math.pow(Math.sin(i * 1.71 + 0.4), 2);
        mode(0, i, 82 * Math.sqrt(2 + i), 2.4 / (1 + 0.05 * i), 1 / Math.sqrt(1 + i), probability, i * 0.17, Math.sin(i * 2.3999));
    }
    end(0);
    strike(0.72);
}

function fill(count, value) { var result = []; for (var i = 0; i < count; i++) result.push(value); return result; }
function number(value, fallback) { var result = Number(value); return isFinite(result) ? result : fallback; }
function integer(value, fallback) { return Math.floor(number(value, fallback)); }
function clip(value, low, high) { return Math.max(low, Math.min(high, value)); }
function status(message) { outlet(8, "set", message); }
