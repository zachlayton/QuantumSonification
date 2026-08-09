autowatch = 1;
inlets = 1;
outlets = 12;

var DIMENSION = 16;
var QUBITS = 4;
var CELL_COUNT = DIMENSION * DIMENSION;
var MAX_DIMENSION = 256;
var AUDIO_VOICES = 16;
var activeRevision = -1;
var activeMode = "";
var activeWeight = 0.0;
var rowsSeen = [];
var stagingReal = [];
var stagingImag = [];
var stagingProbabilities = [];
var stagingMetrics = [0, 0, 0, 0, 0, 0, 0];
var stagingBloch = [];
var frameOpen = false;
var frameStartedAt = 0;
var activePauliLabel = "";
var activePauliWeight = 0;
var activePauliTheta = 0.0;
var activePauliVerified = false;

var complexMatrix = new JitterMatrix(2, "float32", DIMENSION, DIMENSION);
var realMatrix = new JitterMatrix(1, "float32", DIMENSION, DIMENSION);
var imagMatrix = new JitterMatrix(1, "float32", DIMENSION, DIMENSION);
var magnitudeMatrix = new JitterMatrix(1, "float32", DIMENSION, DIMENSION);
var phaseMatrix = new JitterMatrix(1, "float32", DIMENSION, DIMENSION);


function configureDimension(dimension) {
    var qubits = Math.round(Math.log(dimension) / Math.log(2));
    if (
        dimension < 2
        || dimension > MAX_DIMENSION
        || Math.pow(2, qubits) !== dimension
    ) {
        return false;
    }
    if (dimension === DIMENSION) {
        return true;
    }
    DIMENSION = dimension;
    QUBITS = qubits;
    CELL_COUNT = DIMENSION * DIMENSION;
    complexMatrix = new JitterMatrix(2, "float32", DIMENSION, DIMENSION);
    realMatrix = new JitterMatrix(1, "float32", DIMENSION, DIMENSION);
    imagMatrix = new JitterMatrix(1, "float32", DIMENSION, DIMENSION);
    magnitudeMatrix = new JitterMatrix(1, "float32", DIMENSION, DIMENSION);
    phaseMatrix = new JitterMatrix(1, "float32", DIMENSION, DIMENSION);
    return true;
}


function resetStaging(revision, mode, weight) {
    activeRevision = revision;
    activeMode = mode;
    activeWeight = weight;
    rowsSeen = [];
    stagingReal = [];
    stagingImag = [];
    stagingProbabilities = [];
    stagingBloch = [];
    for (var row = 0; row < DIMENSION; row++) {
        rowsSeen[row] = false;
    }
    for (var index = 0; index < CELL_COUNT; index++) {
        stagingReal[index] = 0.0;
        stagingImag[index] = 0.0;
    }
}


function begin() {
    var args = arrayfromargs(arguments);
    if (args.length < 4) {
        outlet(11, "invalid density begin frame");
        return;
    }
    var incomingDimension = Number(args[2]);
    if (!configureDimension(incomingDimension)) {
        outlet(11, "unsupported density dimension " + incomingDimension);
        return;
    }
    var now = new Date().getTime();
    if (frameOpen && now - frameStartedAt < 250) {
        return;
    }
    frameOpen = true;
    frameStartedAt = now;
    resetStaging(Number(args[0]), String(args[1]), Number(args[3]));
    outlet(11, "receiving revision " + activeRevision + " · " + activeMode);
}


function meta() {
    var args = arrayfromargs(arguments);
    if (args.length < 7 || Number(args[0]) !== activeRevision) {
        return;
    }
    stagingMetrics = [
        Number(args[0]),
        Number(args[1]),
        Number(args[2]),
        Number(args[3]),
        Number(args[4]),
        Number(args[5]),
        Number(args[6])
    ];
}


function probabilities() {
    var args = arrayfromargs(arguments);
    if (
        args.length < DIMENSION + 1
        || Number(args[0]) !== activeRevision
    ) {
        return;
    }
    stagingProbabilities = [];
    for (var index = 0; index < DIMENSION; index++) {
        stagingProbabilities[index] = Number(args[index + 1]);
    }
}


function row() {
    var args = arrayfromargs(arguments);
    if (
        args.length < 2 + 2 * DIMENSION
        || Number(args[0]) !== activeRevision
    ) {
        return;
    }
    var rowIndex = Number(args[1]);
    if (rowIndex < 0 || rowIndex >= DIMENSION) {
        return;
    }
    for (var column = 0; column < DIMENSION; column++) {
        var flatIndex = rowIndex * DIMENSION + column;
        stagingReal[flatIndex] = Number(args[column + 2]);
        stagingImag[flatIndex] = Number(args[column + 2 + DIMENSION]);
    }
    rowsSeen[rowIndex] = true;
}


function bloch() {
    var args = arrayfromargs(arguments);
    if (args.length < 7 || Number(args[0]) !== activeRevision) {
        return;
    }
    var qubit = Number(args[1]);
    if (qubit < 0 || qubit >= QUBITS) {
        return;
    }
    stagingBloch[qubit] = [
        qubit,
        Number(args[2]),
        Number(args[3]),
        Number(args[4]),
        Number(args[5]),
        Number(args[6])
    ];
}


function allRowsPresent() {
    for (var rowIndex = 0; rowIndex < DIMENSION; rowIndex++) {
        if (!rowsSeen[rowIndex]) {
            return false;
        }
    }
    return true;
}


function clamp(value, minimum, maximum) {
    return Math.max(minimum, Math.min(maximum, value));
}


function commitFrame(message) {
    var magnitudes = [];
    var phases = [];
    var voiceFrequencies = [];
    var voiceAmplitudes = [];
    var maxMagnitude = 1.0e-12;

    for (var voice = 0; voice < AUDIO_VOICES; voice++) {
        voiceFrequencies[voice] = 55.0 * Math.pow(2.0, voice / 12.0);
        voiceAmplitudes[voice] = 0.0;
    }

    for (var index = 0; index < CELL_COUNT; index++) {
        var real = stagingReal[index];
        var imag = stagingImag[index];
        var magnitude = Math.sqrt(real * real + imag * imag);
        magnitudes[index] = magnitude;
        phases[index] = Math.atan2(imag, real);
        maxMagnitude = Math.max(maxMagnitude, magnitude);
    }

    for (var rowIndex = 0; rowIndex < DIMENSION; rowIndex++) {
        var coherence = 0.0;
        var circularReal = 0.0;
        var circularImag = 0.0;
        for (var column = 0; column < DIMENSION; column++) {
            var flatIndex = rowIndex * DIMENSION + column;
            var real = stagingReal[flatIndex];
            var imag = stagingImag[flatIndex];
            var magnitude = magnitudes[flatIndex];
            complexMatrix.setcell2d(column, rowIndex, [real, imag]);
            realMatrix.setcell2d(column, rowIndex, real);
            imagMatrix.setcell2d(column, rowIndex, imag);
            magnitudeMatrix.setcell2d(
                column,
                rowIndex,
                magnitude / maxMagnitude
            );
            phaseMatrix.setcell2d(
                column,
                rowIndex,
                phases[flatIndex] / Math.PI
            );
            if (column !== rowIndex) {
                coherence += magnitude;
                circularReal += real;
                circularImag += imag;
            }
        }
        var population = Math.max(
            0.0,
            stagingReal[rowIndex * DIMENSION + rowIndex]
        );
        var coherencePhase = Math.atan2(circularImag, circularReal);
        var voiceIndex = rowIndex % AUDIO_VOICES;
        voiceFrequencies[voiceIndex] = (
            55.0
            * Math.pow(2.0, voiceIndex / 12.0)
            * Math.pow(2.0, 0.08 * coherencePhase / (2.0 * Math.PI))
        );
        voiceAmplitudes[voiceIndex] += (
            0.13 * clamp(
                Math.sqrt(population) + 0.25 * coherence,
                0.0,
                1.0
            )
        );
    }
    for (var audioIndex = 0; audioIndex < AUDIO_VOICES; audioIndex++) {
        voiceAmplitudes[audioIndex] = clamp(
            voiceAmplitudes[audioIndex],
            0.0,
            0.22
        );
    }

    outlet(0, "jit_matrix", complexMatrix.name);
    outlet(1, "jit_matrix", realMatrix.name);
    outlet(2, "jit_matrix", imagMatrix.name);
    outlet(3, "jit_matrix", magnitudeMatrix.name);
    outlet(4, "jit_matrix", phaseMatrix.name);
    outlet(5, stagingProbabilities);
    outlet(6, stagingMetrics);
    for (var qubit = 0; qubit < QUBITS; qubit++) {
        if (stagingBloch[qubit]) {
            outlet(7, stagingBloch[qubit]);
            messnamed(
                "qmw.zx.density.bloch",
                stagingBloch[qubit][0],
                stagingBloch[qubit][1],
                stagingBloch[qubit][2],
                stagingBloch[qubit][3],
                stagingBloch[qubit][4],
                stagingBloch[qubit][5]
            );
        }
    }
    outlet(8, voiceFrequencies);
    outlet(9, voiceAmplitudes);
    outlet(10, activeRevision);
    outlet(
        11,
        "committed revision " + activeRevision + " · " + message
    );

    messnamed("qmw.zx.density.probabilities", stagingProbabilities);
    messnamed("qmw.zx.density.metrics", stagingMetrics);
    messnamed("qmw.zx.density.dimension", DIMENSION);
    messnamed("qmw.zx.density.qubits", QUBITS);
    if (CELL_COUNT <= 16384) {
        messnamed("qmw.zx.density.real", stagingReal);
        messnamed("qmw.zx.density.imag", stagingImag);
        messnamed("qmw.zx.density.magnitude", magnitudes);
        messnamed("qmw.zx.density.phase", phases);
    }
    publishActivePauliFromMatrix();
}


function end() {
    var args = arrayfromargs(arguments);
    if (args.length < 2 || Number(args[0]) !== activeRevision) {
        return;
    }
    if (!allRowsPresent()) {
        frameOpen = false;
        outlet(11, "rejected incomplete revision " + activeRevision);
        return;
    }
    commitFrame(String(args[1]));
    frameOpen = false;
}


function error() {
    outlet(11, "bridge error · " + arrayfromargs(arguments).join(" "));
}


function commit_sent() {
    var args = arrayfromargs(arguments);
    outlet(
        11,
        "engine candidate sent · revision " + args[0]
        + " → " + args[1] + ":" + args[2]
    );
}


function pauli_verified() {
    var args = arrayfromargs(arguments);
    if (args.length < 6) {
        return;
    }
    var label = String(args[0]);
    var weight = Number(args[1]);
    var theta = Number(args[2]);
    var verified = Number(args[3]) !== 0;
    var errorValue = Number(args[4]);
    activePauliLabel = label;
    activePauliWeight = weight;
    activePauliTheta = theta;
    activePauliVerified = verified;
    messnamed(
        "qmw.zx.pauli.verified",
        label,
        weight,
        theta,
        verified ? 1 : 0,
        errorValue
    );
    outlet(
        11,
        (verified ? "verified " : "rejected ")
        + label + " · θ " + theta + " · error " + errorValue
    );
}


function pauli_score_verified() {
    var args = arrayfromargs(arguments);
    if (args.length < 4) {
        return;
    }
    var count = Number(args[0]);
    var verified = Number(args[1]) !== 0;
    var errorValue = Number(args[2]);
    activePauliVerified = verified;
    messnamed(
        "qmw.zx.pauli.score.verified",
        count,
        verified ? 1 : 0,
        errorValue
    );
    outlet(
        11,
        (verified ? "verified ordered score · " : "rejected ordered score · ")
        + count + " gadgets · error " + errorValue
    );
}


function pauli_active() {
    var args = arrayfromargs(arguments);
    if (args.length < 4) {
        return;
    }
    activePauliLabel = String(args[1]);
    activePauliWeight = 0;
    for (var index = 0; index < activePauliLabel.length; index++) {
        if (activePauliLabel.charAt(index) !== "I")
            activePauliWeight++;
    }
    activePauliTheta = Number(args[2]);
    activePauliVerified = Number(args[3]) !== 0;
    messnamed(
        "qmw.zx.pauli.active",
        Number(args[0]),
        activePauliLabel,
        activePauliTheta,
        activePauliVerified ? 1 : 0
    );
}


function pauli_live() {
    var args = arrayfromargs(arguments);
    if (args.length < 6) {
        return;
    }
    var revision = Number(args[0]);
    var label = String(args[1]);
    var weight = Number(args[2]);
    var expectation = Number(args[3]);
    var theta = Number(args[4]);
    var verified = Number(args[5]) !== 0;
    activePauliLabel = label;
    activePauliWeight = weight;
    activePauliTheta = theta;
    activePauliVerified = verified;
    messnamed(
        "qmw.zx.pauli.live",
        revision,
        label,
        weight,
        expectation,
        theta,
        verified ? 1 : 0
    );
    messnamed("qmw.zx.pauli.label", label);
    messnamed("qmw.zx.pauli.weight", weight);
    messnamed("qmw.zx.pauli.expectation", expectation);
    messnamed("qmw.zx.pauli.theta", theta);
    outlet(
        11,
        label + " · weight " + weight
        + " · expectation " + expectation
        + " · θ " + theta
        + (verified ? " · PyZX✓" : " · unverified")
    );
}


function euler_result() {
    var args = arrayfromargs(arguments);
    if (args.length < 11) {
        return;
    }
    var request = Number(args[0]);
    var source = String(args[1]);
    var qubit = Number(args[2]);
    var basis = String(args[3]);
    var theta = Number(args[4]);
    var phi = Number(args[5]);
    var lambdaValue = Number(args[6]);
    var gamma = Number(args[7]);
    var zxScalarPhase = Number(args[8]);
    var verified = Number(args[9]) !== 0;
    var errorValue = Number(args[10]);

    messnamed(
        "qmw.euler.result",
        request,
        source,
        qubit,
        basis,
        theta,
        phi,
        lambdaValue,
        gamma,
        zxScalarPhase,
        verified ? 1 : 0,
        errorValue
    );
    messnamed("qmw.euler.theta", theta);
    messnamed("qmw.euler.phi", phi);
    messnamed("qmw.euler.lambda", lambdaValue);
    messnamed("qmw.euler.gamma", gamma);
    messnamed("qmw.euler.zx_scalar_phase", zxScalarPhase);
    messnamed("qmw.euler.verified", verified ? 1 : 0);
    messnamed("qmw.euler.theta_pi", theta / Math.PI);
    messnamed("qmw.euler.phi_pi", phi / Math.PI);
    messnamed("qmw.euler.lambda_pi", lambdaValue / Math.PI);
    messnamed("qmw.euler.gamma_pi", gamma / Math.PI);
    messnamed("qmw.euler.zx_scalar_phase_pi", zxScalarPhase / Math.PI);
    messnamed(
        "qmw.euler.pi_result",
        "theta/pi",
        theta / Math.PI,
        "phi/pi",
        phi / Math.PI,
        "lambda/pi",
        lambdaValue / Math.PI,
        "gamma/pi",
        gamma / Math.PI,
        "scalar/pi",
        zxScalarPhase / Math.PI
    );
    outlet(
        11,
        (verified ? "Euler verified · " : "Euler rejected · ")
        + basis + " · " + source + " · error " + errorValue
    );
}


function pauli_error() {
    outlet(11, "Pauli bridge error · " + arrayfromargs(arguments).join(" "));
}


function publishActivePauliFromMatrix() {
    if (DIMENSION !== 16 || activePauliLabel.length !== 4) {
        return;
    }
    var expectationReal = 0.0;
    var expectationImag = 0.0;
    for (var inputBasis = 0; inputBasis < DIMENSION; inputBasis++) {
        var outputBasis = inputBasis;
        var phaseReal = 1.0;
        var phaseImag = 0.0;
        for (var qubit = 0; qubit < 4; qubit++) {
            var axis = activePauliLabel.charAt(qubit);
            var bit = (inputBasis >> qubit) & 1;
            var axisReal = 1.0;
            var axisImag = 0.0;
            if (axis === "X") {
                outputBasis ^= (1 << qubit);
            } else if (axis === "Y") {
                outputBasis ^= (1 << qubit);
                axisReal = 0.0;
                axisImag = bit ? -1.0 : 1.0;
            } else if (axis === "Z") {
                axisReal = bit ? -1.0 : 1.0;
            }
            var nextReal = phaseReal * axisReal - phaseImag * axisImag;
            var nextImag = phaseReal * axisImag + phaseImag * axisReal;
            phaseReal = nextReal;
            phaseImag = nextImag;
        }
        var flatIndex = inputBasis * DIMENSION + outputBasis;
        var rhoReal = stagingReal[flatIndex];
        var rhoImag = stagingImag[flatIndex];
        expectationReal += rhoReal * phaseReal - rhoImag * phaseImag;
        expectationImag += rhoReal * phaseImag + rhoImag * phaseReal;
    }
    messnamed(
        "qmw.zx.pauli.live",
        activeRevision,
        activePauliLabel,
        activePauliWeight,
        expectationReal,
        activePauliTheta,
        activePauliVerified ? 1 : 0
    );
    messnamed("qmw.zx.pauli.expectation", expectationReal);
    if (Math.abs(expectationImag) > 1.0e-6) {
        outlet(
            11,
            "Pauli expectation warning · imaginary residue " + expectationImag
        );
    }
}


function anything() {
    var args = arrayfromargs(arguments);
    if (messagename === "begin") {
        begin.apply(this, args);
    } else if (messagename === "meta") {
        meta.apply(this, args);
    } else if (messagename === "probabilities") {
        probabilities.apply(this, args);
    } else if (messagename === "row") {
        row.apply(this, args);
    } else if (messagename === "bloch") {
        bloch.apply(this, args);
    } else if (messagename === "end") {
        end.apply(this, args);
    } else if (messagename === "error") {
        error.apply(this, args);
    } else if (messagename === "commit_sent") {
        commit_sent.apply(this, args);
    }
}
