// Convert one committed QMB Heisenberg frame into a complex wavetable and
// sixteen row-addressed vb.mi.rngs~ control frames.

autowatch = 1;
inlets = 1;
outlets = 3;

var WAVE_SIZE = 2048;
var PITCH_ROOT = 38; // D2
var PITCH_FLOOR = 38;
var PITCH_CEILING = 74;
var PITCH_SCALE = [0, 3, 5, 7, 10]; // D minor pentatonic
var matrixNames = {};
var previousComplex = null;
var waveBanks = [makeWave("a"), makeWave("b")];
var activeWave = 0;
var mappingMorph = 1.0;
var MAP_DESTINATIONS = ["structure", "brightness", "damping", "position"];
var MAP_SOURCES = ["magnitude", "real", "imag", "phase", "frequency", "pan"];
var voiceMaps = [];
var cellMaps = [];

function mapping_morph(value) {
    mappingMorph = clamp(value, 0.0, 1.0);
    outlet(2, "mapping_morph", mappingMorph);
}

function voice_map(voice, destination, source, amount) {
    var first = Math.floor(Number(voice));
    var dest = String(destination).toLowerCase();
    var src = String(source).toLowerCase();
    var weight = clamp(amount, -1.0, 1.0);
    if (MAP_DESTINATIONS.indexOf(dest) < 0 || MAP_SOURCES.indexOf(src) < 0) {
        outlet(2, "rejected", "invalid_voice_map", voice, dest, src, amount);
        return;
    }
    var start = first === 0 ? 0 : first - 1;
    var end = first === 0 ? 15 : first - 1;
    if (start < 0 || end > 15) {
        outlet(2, "rejected", "invalid_voice", voice);
        return;
    }
    for (var row = start; row <= end; row++) {
        if (!voiceMaps[row]) voiceMaps[row] = {};
        if (!voiceMaps[row][dest]) voiceMaps[row][dest] = {};
        voiceMaps[row][dest][src] = weight;
    }
    outlet(2, "voice_map", first, dest, src, weight);
}

function voice_map_clear(voice) {
    var selected = arguments.length ? Math.floor(Number(voice)) : 0;
    if (selected === 0) {
        voiceMaps = [];
    } else if (selected >= 1 && selected <= 16) {
        voiceMaps[selected - 1] = {};
    } else {
        outlet(2, "rejected", "invalid_voice", selected);
        return;
    }
    outlet(2, "voice_map_clear", selected);
}

function cell_map(voice, destination, source, column, amount) {
    var first = Math.floor(Number(voice));
    var dest = String(destination).toLowerCase();
    var src = String(source).toLowerCase();
    var selectedColumn = Math.floor(Number(column)) - 1;
    var weight = clamp(amount, -1.0, 1.0);
    if (MAP_DESTINATIONS.indexOf(dest) < 0 || MAP_SOURCES.indexOf(src) < 0) {
        outlet(2, "rejected", "invalid_cell_map", voice, dest, src, column, amount);
        return;
    }
    if (selectedColumn < 0 || selectedColumn > 15) {
        outlet(2, "rejected", "invalid_column", column);
        return;
    }
    var start = first === 0 ? 0 : first - 1;
    var end = first === 0 ? 15 : first - 1;
    if (start < 0 || end > 15) {
        outlet(2, "rejected", "invalid_voice", voice);
        return;
    }
    for (var row = start; row <= end; row++) {
        if (!cellMaps[row]) cellMaps[row] = {};
        if (!cellMaps[row][dest]) cellMaps[row][dest] = {};
        cellMaps[row][dest][src] = { column: selectedColumn, amount: weight };
    }
    outlet(2, "cell_map", first, dest, src, selectedColumn + 1, weight);
}

function cell_map_clear(voice) {
    var selected = arguments.length ? Math.floor(Number(voice)) : 0;
    if (selected === 0) {
        cellMaps = [];
    } else if (selected >= 1 && selected <= 16) {
        cellMaps[selected - 1] = {};
    } else {
        outlet(2, "rejected", "invalid_voice", selected);
        return;
    }
    outlet(2, "cell_map_clear", selected);
}

function makeWave(label) {
    var matrix = new JitterMatrix(1, "float32", WAVE_SIZE, 1);
    matrix.name = "qmb_heisenberg_rings_wave_" + label;
    return matrix;
}

function anything() {
    var selector = String(messagename);
    var args = Array.prototype.slice.call(arguments);
    if (selector === "contributions" || selector === "magnitude" ||
            selector === "phase" || selector === "frequency_hz" || selector === "pan") {
        rememberMatrix(selector, args);
    } else if (selector === "commit") {
        commit.apply(this, args);
    }
}

function rememberMatrix(kind, args) {
    if (args.length >= 2 && String(args[0]) === "jit_matrix") {
        matrixNames[kind] = String(args[1]);
    } else if (args.length >= 1) {
        matrixNames[kind] = String(args[args.length - 1]);
    }
}

function commit(revision, dimension) {
    var stage = "validate";
    try {
        var d = Math.floor(Number(dimension));
        if (d < 1 || !haveRequiredMatrices()) {
            outlet(2, "rejected", "missing_matrix", revision, dimension);
            return;
        }
        stage = "attach_matrices";
        var contributions = matrixFromName(matrixNames.contributions);
        var magnitude = matrixFromName(matrixNames.magnitude);
        var phase = matrixFromName(matrixNames.phase);
        var frequency = matrixFromName(matrixNames.frequency_hz);
        var pan = matrixFromName(matrixNames.pan);
        stage = "check_dimensions";
        if (!sameSquareDimension([contributions, magnitude, phase, frequency, pan], d)) {
            outlet(2, "rejected", "dimension_mismatch", revision, dimension);
            return;
        }

        stage = "read_cells";
        var count = d * d;
        var complex = new Array(count);
        var magnitudes = new Array(count);
        var phases = new Array(count);
        var frequencies = new Array(count);
        var pans = new Array(count);
        var index = 0;
        for (var row = 0; row < d; row++) {
            for (var column = 0; column < d; column++) {
                var cell = readCell(contributions, column, row);
                complex[index] = [Number(cell[0]), Number(cell[1])];
                magnitudes[index] = scalar(readCell(magnitude, column, row));
                phases[index] = scalar(readCell(phase, column, row));
                frequencies[index] = scalar(readCell(frequency, column, row));
                pans[index] = scalar(readCell(pan, column, row));
                index++;
            }
        }

        stage = "publish_wavetable";
        publishWavetable(complex, revision);
        stage = "publish_voices";
        publishRows(d, complex, magnitudes, phases, frequencies, pans);
        previousComplex = complex;
        outlet(2, "musical_commit", Number(revision), d, activeWave);
    } catch (error) {
        var detail = error && error.message ? String(error.message) : String(error);
        outlet(2, "rejected", "commit_error", stage, detail);
        post("QMB_RINGS_CONTROLLER: commit_error " + stage + " " + detail + "\n");
    }
}

function publishWavetable(complex, revision) {
    // Use one fixed quadrature projection so adjacent smoothed quantum frames
    // remain adjacent acoustically. Revision-dependent rotation created a hard
    // discontinuity on every commit and masked upstream complex smoothing.
    var cosine = Math.SQRT1_2;
    var sine = Math.SQRT1_2;
    var source = [];
    var i;
    for (i = 0; i < complex.length; i++) {
        source.push(complex[i][0] * cosine + complex[i][1] * sine);
    }
    var mean = 0.0;
    for (i = 0; i < source.length; i++) mean += source[i];
    mean /= Math.max(1, source.length);
    for (i = 0; i < source.length; i++) source[i] -= mean;

    var wave = new Array(WAVE_SIZE);
    var sourceCount = source.length;
    for (i = 0; i < WAVE_SIZE; i++) {
        var position = i * sourceCount / WAVE_SIZE;
        var base = Math.floor(position) % sourceCount;
        var next = (base + 1) % sourceCount;
        var fraction = position - Math.floor(position);
        var value = source[base] * (1.0 - fraction) + source[next] * fraction;
        // A small circular three-point smoothing suppresses the harshest cell
        // boundaries while retaining matrix detail.
        var previous = source[(base + sourceCount - 1) % sourceCount];
        value = 0.25 * previous + 0.5 * value + 0.25 * source[next];
        wave[i] = value;
    }
    var peak = 0.0;
    for (i = 0; i < WAVE_SIZE; i++) peak = Math.max(peak, Math.abs(wave[i]));
    var scale = peak > 1.0e-12 ? 0.85 / peak : 0.0;
    for (i = 0; i < WAVE_SIZE; i++) wave[i] *= scale;

    activeWave = 1 - activeWave;
    writeWaveMatrix(waveBanks[activeWave], wave);
    outlet(0, "jit_matrix", waveBanks[activeWave].name);
}

function writeWaveMatrix(matrix, values) {
    // Use the same legacy-safe two-dimensional setter as the QMB adapter. The
    // wavetable is represented as a WAVE_SIZE by 1 matrix.
    for (var i = 0; i < values.length; i++) matrix.setcell2d(i, 0, values[i]);
}

function publishRows(d, complex, magnitudes, phases, frequencies, pans) {
    var totalMagnitude = sum(magnitudes);
    var peakMagnitude = maximum(magnitudes);
    for (var row = 0; row < d; row++) {
        var energy = 0.0;
        var offDiagonal = 0.0;
        var weightedFrequency = 0.0;
        var weightedPan = 0.0;
        var phaseX = 0.0;
        var phaseY = 0.0;
        var change = 0.0;
        var weightLogWeight = 0.0;
        var realSum = 0.0;
        var imagSum = 0.0;
        var dominantWeight = -1.0;
        var dominantPhase = 0.0;
        var dominantPan = 0.0;
        for (var column = 0; column < d; column++) {
            var index = row * d + column;
            var weight = Math.max(0.0, magnitudes[index]);
            energy += weight;
            if (row !== column) offDiagonal += weight;
            if (weight > 0.0) weightLogWeight += weight * Math.log(weight);
            weightedFrequency += weight * clamp(frequencies[index], 20.0, 16000.0);
            weightedPan += weight * clamp(pans[index], -1.0, 1.0);
            phaseX += weight * Math.cos(phases[index]);
            phaseY += weight * Math.sin(phases[index]);
            realSum += complex[index][0];
            imagSum += complex[index][1];
            if (weight > dominantWeight) {
                dominantWeight = weight;
                dominantPhase = phases[index];
                dominantPan = clamp(pans[index], -1.0, 1.0);
            }
            if (previousComplex && previousComplex.length === complex.length) {
                var dr = complex[index][0] - previousComplex[index][0];
                var di = complex[index][1] - previousComplex[index][1];
                change += Math.sqrt(dr * dr + di * di);
            }
        }
        var safeEnergy = Math.max(energy, 1.0e-12);
        var phaseOrder = Math.sqrt(phaseX * phaseX + phaseY * phaseY) / safeEnergy;
        var dispersion = clamp(1.0 - phaseOrder, 0.0, 1.0);
        var meanPhase = Math.atan2(phaseY, phaseX);
        var coherence = clamp(offDiagonal / safeEnergy, 0.0, 1.0);
        var entropy = energy > 1.0e-12 ?
            (Math.log(safeEnergy) - weightLogWeight / safeEnergy) / Math.log(Math.max(2, d)) : 0.0;
        entropy = clamp(entropy, 0.0, 1.0);
        var realBalance = clamp(realSum / safeEnergy, -1.0, 1.0);
        var imagBalance = clamp(imagSum / safeEnergy, -1.0, 1.0);
        var centerFrequency = weightedFrequency / safeEnergy;
        if (!isFinite(centerFrequency) || centerFrequency <= 0.0) centerFrequency = 55.0 * Math.pow(2.0, row / Math.max(1, d));
        // Preserve the logarithmic energy-gap pitch class without allowing
        // ultrasonic row centroids to collapse against one MIDI ceiling.
        // Octave folding and a shared lattice happen only in this musical
        // adapter; the canonical frequency_hz matrix remains unchanged.
        var rawMidi = 69.0 + 12.0 * Math.log(centerFrequency / 440.0) / Math.log(2.0);
        var midi = quantizeFoldedMidi(rawMidi);
        var relativeEnergy = energy / Math.max(totalMagnitude, 1.0e-12);
        // Do not strum rows that are numerically present but physically empty.
        // The previous amplitude floor made those rows excite Rings' internal
        // resonator and obscured the few meaningful XZ0 contributions.
        if (relativeEnergy < 1.0e-5) continue;
        var relationalStructure = clamp(0.12 + 0.82 * coherence, 0.0, 1.0);
        var componentStructure = clamp(0.08 + 0.86 * entropy, 0.0, 1.0);
        var realBrightness = 0.5 + 0.5 * realBalance;
        var normalizedChange = previousComplex ? clamp(change / safeEnergy, 0.0, 1.0) : 0.65;
        var phaseBrightness = 0.5 + 0.5 * Math.cos(meanPhase);
        var relationalBrightness = clamp(0.12 + 0.58 * dispersion + 0.28 * phaseBrightness, 0.0, 1.0);
        var componentBrightness = clamp(0.1 + 0.68 * realBrightness + 0.22 * dispersion, 0.0, 1.0);
        var relationalDamping = clamp(0.9 - 0.62 * normalizedChange, 0.15, 0.95);
        var componentDamping = clamp(0.22 + 0.68 * phaseOrder - 0.28 * normalizedChange, 0.12, 0.95);
        var relationalPosition = clamp(
            0.5 + 0.34 * weightedPan / safeEnergy + 0.16 * Math.sin(meanPhase),
            0.0,
            1.0
        );
        var componentPosition = clamp(
            0.5 + 0.32 * imagBalance + 0.18 * dominantPan,
            0.0,
            1.0
        );
        var structure = mix(relationalStructure, componentStructure, mappingMorph);
        var brightness = mix(relationalBrightness, componentBrightness, mappingMorph);
        var damping = mix(relationalDamping, componentDamping, mappingMorph);
        var position = mix(relationalPosition, componentPosition, mappingMorph);
        var featureValues = {
            magnitude: clamp(2.0 * Math.sqrt(relativeEnergy) - 1.0, -1.0, 1.0),
            real: realBalance,
            imag: imagBalance,
            phase: Math.sin(meanPhase),
            frequency: clamp((midi - PITCH_FLOOR) / (PITCH_CEILING - PITCH_FLOOR) * 2.0 - 1.0, -1.0, 1.0),
            pan: dominantPan
        };
        structure = applyVoiceMap(row, "structure", structure, featureValues);
        brightness = applyVoiceMap(row, "brightness", brightness, featureValues);
        damping = applyVoiceMap(row, "damping", damping, featureValues);
        position = applyVoiceMap(row, "position", position, featureValues);
        structure = applyCellMap(row, "structure", structure, complex, magnitudes, phases, frequencies, pans, d, peakMagnitude);
        brightness = applyCellMap(row, "brightness", brightness, complex, magnitudes, phases, frequencies, pans, d, peakMagnitude);
        damping = applyCellMap(row, "damping", damping, complex, magnitudes, phases, frequencies, pans, d, peakMagnitude);
        position = applyCellMap(row, "position", position, complex, magnitudes, phases, frequencies, pans, d, peakMagnitude);
        // Drive Rings decisively enough for sparse quantum frames to remain
        // audible. The per-voice and master limiters still protect the sum.
        var amplitude = clamp(1.8 * Math.sqrt(relativeEnergy), 0.0, 0.72);
        var phaseTurn = (dominantPhase + Math.PI) / (2.0 * Math.PI);
        var model = Math.floor(phaseTurn * 3.0) % 3;
        outlet(1, "voice", row + 1, midi, structure, brightness, damping, position, amplitude, model);
    }
}

function matrixFromName(name) {
    var matrix = new JitterMatrix();
    matrix.name = name;
    return matrix;
}

function haveRequiredMatrices() {
    return matrixNames.contributions && matrixNames.magnitude && matrixNames.phase &&
        matrixNames.frequency_hz && matrixNames.pan;
}

function sameSquareDimension(matrices, dimension) {
    for (var i = 0; i < matrices.length; i++) {
        if (Number(matrices[i].dim[0]) !== dimension || Number(matrices[i].dim[1]) !== dimension) return false;
    }
    return true;
}

function scalar(value) {
    return value instanceof Array ? Number(value[0]) : Number(value);
}

function readCell(matrix, column, row) {
    // Legacy Max `js` exposes getcell(x, y); V8-backed matrix wrappers may
    // additionally expose getcell2d. Prefer the API shared with Max 9's own
    // installed Jitter JavaScript examples.
    if (typeof matrix.getcell === "function") return matrix.getcell(column, row);
    if (typeof matrix.getcell2d === "function") return matrix.getcell2d(column, row);
    throw new Error("matrix has neither getcell nor getcell2d");
}

function sum(values) {
    var result = 0.0;
    for (var i = 0; i < values.length; i++) result += values[i];
    return result;
}

function maximum(values) {
    var result = 0.0;
    for (var i = 0; i < values.length; i++) result = Math.max(result, Number(values[i]));
    return result;
}

function clamp(value, minimum, maximum) {
    return Math.max(minimum, Math.min(maximum, Number(value)));
}

function mix(left, right, amount) {
    return Number(left) + clamp(amount, 0.0, 1.0) * (Number(right) - Number(left));
}

function applyVoiceMap(row, destination, defaultValue, features) {
    if (!voiceMaps[row] || !voiceMaps[row][destination]) return defaultValue;
    var weights = voiceMaps[row][destination];
    var weighted = 0.0;
    var total = 0.0;
    for (var index = 0; index < MAP_SOURCES.length; index++) {
        var source = MAP_SOURCES[index];
        var weight = Number(weights[source] || 0.0);
        weighted += weight * Number(features[source]);
        total += Math.abs(weight);
    }
    if (total <= 1.0e-12) return defaultValue;
    var customValue = clamp(0.5 + 0.5 * weighted / total, 0.0, 1.0);
    return mix(defaultValue, customValue, clamp(total, 0.0, 1.0));
}

function applyCellMap(row, destination, defaultValue, complex, magnitudes, phases, frequencies, pans, dimension, peakMagnitude) {
    if (!cellMaps[row] || !cellMaps[row][destination]) return defaultValue;
    var routes = cellMaps[row][destination];
    var weighted = 0.0;
    var total = 0.0;
    for (var sourceIndex = 0; sourceIndex < MAP_SOURCES.length; sourceIndex++) {
        var source = MAP_SOURCES[sourceIndex];
        var route = routes[source];
        if (!route) continue;
        var index = row * dimension + route.column;
        var value = rawCellFeature(source, index, complex, magnitudes, phases, frequencies, pans, peakMagnitude);
        weighted += Number(route.amount) * value;
        total += Math.abs(Number(route.amount));
    }
    if (total <= 1.0e-12) return defaultValue;
    var customValue = clamp(0.5 + 0.5 * weighted / total, 0.0, 1.0);
    return mix(defaultValue, customValue, clamp(total, 0.0, 1.0));
}

function rawCellFeature(source, index, complex, magnitudes, phases, frequencies, pans, peakMagnitude) {
    var safePeak = Math.max(Number(peakMagnitude), 1.0e-12);
    if (source === "magnitude") return clamp(2.0 * Number(magnitudes[index]) / safePeak - 1.0, -1.0, 1.0);
    if (source === "real") return clamp(Number(complex[index][0]) / safePeak, -1.0, 1.0);
    if (source === "imag") return clamp(Number(complex[index][1]) / safePeak, -1.0, 1.0);
    if (source === "phase") return clamp(Number(phases[index]) / Math.PI, -1.0, 1.0);
    if (source === "pan") return clamp(Number(pans[index]), -1.0, 1.0);
    if (source === "frequency") {
        var low = Math.log(20.0);
        var high = Math.log(16000.0);
        var value = Math.log(clamp(frequencies[index], 20.0, 16000.0));
        return clamp(2.0 * (value - low) / (high - low) - 1.0, -1.0, 1.0);
    }
    return 0.0;
}

function quantizeFoldedMidi(value) {
    var folded = Number(value);
    while (folded > PITCH_CEILING) folded -= 12.0;
    while (folded < PITCH_FLOOR) folded += 12.0;

    var best = PITCH_ROOT;
    var bestDistance = Infinity;
    for (var octave = -1; octave <= 5; octave++) {
        for (var degree = 0; degree < PITCH_SCALE.length; degree++) {
            var candidate = PITCH_ROOT + 12 * octave + PITCH_SCALE[degree];
            if (candidate < PITCH_FLOOR || candidate > PITCH_CEILING) continue;
            var distance = Math.abs(candidate - folded);
            if (distance < bestDistance) {
                best = candidate;
                bestDistance = distance;
            }
        }
    }
    return best;
}
