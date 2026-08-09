// qmw_resonance_grain_scheduler_v3.js
// Independent-lane extension of the QMW v2 resonance-grain scheduler.
//
// V2 already provides the UI/control protocol, four independent line~
// outlets, local clocks, OSC clocks, envelope generation, and status outlet.
// V3 replaces only the two behaviours that made the quantum result sound
// like one shared clock:
//   1. an unaddressed trigger now advances round-robin instead of striking
//      all four voices together;
//   2. each quantum row owns its onset history, refractory time, pattern
//      tasks, and data-derived step duration.

include("qmw_resonance_grain_scheduler_v2.js");

var qmwV2Reset = reset;
var quantumPreviousFieldV3 = null;
var quantumLaneLastFireMsV3 = [-100000, -100000, -100000, -100000];

function triggerV3(amplitude, duration, requestedVoice) {
    amplitude = arguments.length > 0 ? Number(amplitude) : 1.0;
    duration = arguments.length > 1 ? Number(duration) : durationMs;
    if (arguments.length > 2) {
        fireVoice(requestedVoice, amplitude, duration, attackMs);
        return;
    }
    // A generic FIRE/OSC trigger is a single event. Repeated triggers walk
    // across the voices; they never impose one common envelope on all four.
    fire(amplitude, duration, attackMs);
}

function resetV3() {
    qmwV2Reset();
    quantumPreviousFieldV3 = null;
    quantumLaneLastFireMsV3 = [-100000, -100000, -100000, -100000];
}

function quantumStateV3(
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
    for (var cell = 0; cell < 16; cell++) {
        var fallback = cell === basisIndex ? 1.0 : 0.0;
        field[cell] = arguments.length > 14 + cell
            ? clamp(arguments[14 + cell], 0.0, 1.0)
            : fallback;
    }

    if (quantumPreviousFieldV3 === null) {
        quantumPreviousFieldV3 = field.slice(0);
        quantumPreviousSalience = salience;
        return;
    }

    var salienceOnset = quantumPreviousSalience === null
        ? 0.0
        : Math.max(0.0, salience - quantumPreviousSalience);
    quantumPreviousSalience = salience;

    var rowEnergies = [0.0, 0.0, 0.0, 0.0];
    var rowMaxima = [0.000001, 0.000001, 0.000001, 0.000001];
    var rowPositiveMotion = [0.0, 0.0, 0.0, 0.0];
    var rowCentroids = [0.5, 0.5, 0.5, 0.5];
    var maximumRowEnergy = 0.000001;
    for (var voice = 0; voice < 4; voice++) {
        var weightedColumn = 0.0;
        for (var column = 0; column < 4; column++) {
            var fieldIndex = voice * 4 + column;
            var value = field[fieldIndex];
            rowEnergies[voice] += value;
            rowMaxima[voice] = Math.max(rowMaxima[voice], value);
            rowPositiveMotion[voice] += Math.max(
                0.0, value - quantumPreviousFieldV3[fieldIndex]
            );
            weightedColumn += column * value;
        }
        if (rowEnergies[voice] > 0.000001) {
            rowCentroids[voice] = weightedColumn / (3.0 * rowEnergies[voice]);
        }
        maximumRowEnergy = Math.max(maximumRowEnergy, rowEnergies[voice]);
    }

    var amplitude = clamp(
        (0.20 + 0.45 * salience + 0.25 * purity)
        * (0.75 + 0.25 * basisProbability),
        0.15, 1.25
    );
    var quantumDuration = clamp(
        durationMs * Math.pow(
            2.0, coherenceDurationDepth * (2.0 * coherence - 1.0)
        ),
        12.0, 4000.0
    );
    var nowMs = Date.now();
    var scheduled = false;
    var matrixRows = ["", "", "", ""];

    for (var lane = 0; lane < 4; lane++) {
        var strikeBits = [];
        for (var bitColumn = 0; bitColumn < 4; bitColumn++) {
            var bitIndex = lane * 4 + bitColumn;
            var rowNormalized = field[bitIndex] / rowMaxima[lane];
            var strikeChance = rowNormalized < quantumCellThreshold
                ? 0.0
                : (rowNormalized - quantumCellThreshold)
                    / Math.max(1.0 - quantumCellThreshold, 0.000001);
            if (rowNormalized >= 0.999999) strikeChance = 1.0;
            strikeBits[bitColumn] = randomUnit() <= strikeChance;
            matrixRows[lane] += strikeBits[bitColumn] ? "1" : "0";
        }

        // Each row qualifies independently. Row motion is the primary gate;
        // the global salience onset contributes in proportion to that row's
        // actual population, rather than striking every row together.
        var rowShare = rowEnergies[lane] / maximumRowEnergy;
        var laneOnset = 0.70 * rowPositiveMotion[lane]
            + 0.30 * salienceOnset * Math.sqrt(rowShare);
        var laneRefractory = quantumRefractoryMs
            * (0.55 + 0.90 * (1.0 - probabilities[lane]));
        if (sourceValue !== 1
            || rowEnergies[lane] <= 0.000001
            || laneOnset < quantumThreshold
            || nowMs - quantumLaneLastFireMsV3[lane] < laneRefractory) {
            continue;
        }

        // Probability, phase, and the row's center of mass continuously set
        // the lane period around STEP ms. There are no fixed integer ratios.
        var periodExponent = 1.25 * (probabilities[lane] - 0.5)
            + 0.55 * phases[lane]
            + 0.75 * (rowCentroids[lane] - 0.5);
        var laneStep = clamp(
            quantumStepMs * Math.pow(2.0, periodExponent),
            5.0, 2000.0
        );
        var phaseOffset = quantumGroove * laneStep * 0.45
            * (0.5 + 0.5 * phases[lane]);

        // A new event in one lane replaces only that lane's unfinished row;
        // other voices continue on their own timelines.
        for (var oldColumn = 0; oldColumn < 4; oldColumn++) {
            var oldTaskIndex = lane * 4 + oldColumn;
            if (quantumPatternTasks[oldTaskIndex] !== null) {
                quantumPatternTasks[oldTaskIndex].cancel();
                quantumPatternTasks[oldTaskIndex] = null;
            }
        }

        for (var eventColumn = 0; eventColumn < 4; eventColumn++) {
            if (!strikeBits[eventColumn]) continue;
            var eventTaskIndex = lane * 4 + eventColumn;
            var delay = phaseOffset + eventColumn * laneStep;
            var rowAmplitude = amplitude
                * (0.25 + 0.75 * Math.sqrt(rowShare));
            var normalizedCell = field[eventTaskIndex] / rowMaxima[lane];
            var cellAmplitude = rowAmplitude
                * (0.35 + 0.65 * Math.sqrt(normalizedCell));
            if (delay <= 0.001) {
                fireVoice(lane, cellAmplitude, quantumDuration, attackMs);
            } else {
                quantumPatternTasks[eventTaskIndex] = new Task(
                    fireQuantumStep, this, eventTaskIndex, lane,
                    cellAmplitude, quantumDuration
                );
                quantumPatternTasks[eventTaskIndex].schedule(delay);
            }
            scheduled = true;
        }
        quantumLaneLastFireMsV3[lane] = nowMs;
    }

    quantumPreviousFieldV3 = field.slice(0);
    lastQuantumPattern = matrixRows.join("/");
    emitStatus(scheduled ? "independent" : "waiting");
}

trigger = triggerV3;
quantum_state = quantumStateV3;
reset = resetV3;
