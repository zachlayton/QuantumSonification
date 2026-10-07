/*
Quantum Resonant Membrane v1 -- standalone SuperCollider instrument.

Start the Python backend first (the bundled .command launcher does this).
The density engine is authoritative. This file is a capability-gated observer
and sound adapter; its controls never claim to perform quantum evolution.
*/
(
var modeCount = 20;
var harmonicCount = 16;
var dataPort = 17920;
var controlPort = 17921;
var root = "/qmw/qrm/v1";
var presetPath = thisProcess.nowExecutingPath.dirname.dirname
    +/+ "presets/qrm_v1_performance_slots.archive";
var interferenceTimbreAddonPath = thisProcess.nowExecutingPath.dirname
    +/+ "QMWInterferenceTimbreAddonV1.scd";
var scalaDirectory = thisProcess.nowExecutingPath.dirname.dirname
    +/+ "tunings/scala_archive/scl";
var styleMenu, styleTextField;
var qrmFieldColor = Color.fromHexString("080b10");
var qrmTextColor = Color.white;

// Explicit colors avoid black platform-default text on the dark instrument.
styleMenu = { |menu|
    menu.background_(qrmFieldColor).stringColor_(qrmTextColor);
    menu
};
styleTextField = { |field|
    field.background_(qrmFieldColor).stringColor_(qrmTextColor);
    field
};

// The 20-mode 16-output body is intentionally a large graph.  Reserve enough
// interconnect buffers before the server boots; this affects DSP capacity only.
s.options.numWireBufs = s.options.numWireBufs.max(2048);

~qrmCleanup !? { ~qrmCleanup.value };
if(File.exists(interferenceTimbreAddonPath)) {
    thisProcess.interpreter.executeFile(interferenceTimbreAddonPath);
} {
    "QRM phase-interference timbre panel is unavailable".warn;
};
~qrmSessionQuitting = false;
~qrmAvailable = false;
~qrmCompatible = false;
~qrmAudioReady = false;
~qrmSelectedOutputDevice = s.options.outDevice;
~qrmOutputChannels = case
{ s.options.numOutputBusChannels >= 16 } { 16 }
{ s.options.numOutputBusChannels >= 8 } { 8 }
{ 2 };
~qrmAudioDeviceValues = Array.new;
~qrmAudioDeviceItems = Array.new;
~qrmBodySynthName = \qrmMembraneBodyV1;
~qrmStrikeSynthName = \qrmBoundaryStrikeV1;
~qrmSonify = false;
// Standalone QRM retains its native boundary-strike renderer. The unified
// interaction layer explicitly disables it and owns admitted events through
// its six-channel mixer instead.
~qrmCrossingAudioEnabled = ~qrmCrossingAudioEnabled ? true;
~qrmLastFrameAt = 0.0;
~qrmRevision = -1;
~qrmStageRevision = -1;
~qrmStageCompatible = false;
~qrmResetEpoch = 0;
~qrmStageResetEpoch = 0;
~qrmSonicGeneration = 0;
~qrmSonicGateUntil = 0.0;
~qrmPopulations = [0.25, 0.25, 0.25, 0.25];
~qrmRhoReal = Array.fill(16, 0.0);
~qrmRhoImag = Array.fill(16, 0.0);
~qrmQ = Array.fill(4, 0.0);
~qrmQdot = Array.fill(4, 0.0);
~qrmModes = Array.fill(modeCount, 0.0);
~qrmRawModes = Array.fill(modeCount, 0.0);
~qrmModeVelocities = Array.fill(modeCount, 0.0);
~qrmRatios = Array.series(modeCount, 1.0, 0.15);
// Revision-matched downstream timbre projection. Unity is the neutral default;
// these gains never change rho, geometry, mode frequencies, or event identity.
~qrmInterferenceTimbreGains = Array.fill(modeCount, 1.0);
~qrmInterferenceTimbreOutputAmplitudes = Array.fill(modeCount, 0.0);
~qrmInterferenceTimbreSlew = 0.08;
~qrmInterferenceTimbrePhase = 0.0;
~qrmInterferenceTimbreSpread = 0.0;
~qrmInterferenceTimbreDepth = 0.0;
~qrmInterferenceTimbreSource = "designed_control";
~qrmInterferenceTimbreCancellation = false;
~qrmPitchMode = 1;
~qrmPitchModeNames = [
    "physical", "harmonics 1-16", "odd harmonics", "geometric tuning"
];
~qrmPitchRatios = Array.fill(modeCount, { |index| (index % 16) + 1.0 });
~qrmTuningFamilyNames = [
    "n-EDO", "Wilson", "Tenney", "La Monte Young", "Scala dictionary"
];
~qrmTuningFamily = 0;
~qrmEDO = 19;
~qrmTuningDegreeOffset = 0;
~qrmScalaFilter = "";
~qrmScalaAllPaths = if(PathName(scalaDirectory).isFolder, {
    PathName(scalaDirectory).files.select { |path| path.extension == "scl" }
        .sort { |left, right| left.fileName < right.fileName }
}, { Array.new });
~qrmScalaPaths = Array.new;
~qrmScalaNames = ["no Scala scales found"];
~qrmSelectedScalaPath = "";
~qrmActiveTuningDescription = "19 equal divisions of 2/1";
~qrmActiveTuningDegrees = [1.0];
~qrmActiveTuningPeriod = 2.0;
~qrmFlux = Array.fill(4, 0.0);
~qrmContact = [0.0, 0.0, 0.0];
~qrmCrossingFlash = 0.0;
~qrmPurity = 0.0;
~qrmEntropy = 0.0;
~qrmCoherence = 0.0;
~qrmHamiltonianSpan = 0.0;
~qrmDensitySubsteps = 0;
~qrmFieldMaxOffset = 0.0;
~qrmFieldMeanSusceptibility = 0.0;
~qrmFieldMinQ = 0.0;
~qrmFieldMaxQ = 0.0;
~qrmFieldMaxCoupling = 0.0;
~qrmFieldOffsets = Array.fill(modeCount, 0.0);
~qrmFieldSusceptibility = Array.fill(modeCount, 0.0);
~qrmEventProbability = 0.0;
~qrmEventCount = 0;
~qrmEventThreshold = 0.003;
~qrmEventAccumulatorFill = 0.0;
~qrmInjectedEnergy = 0.0;
~qrmPreparationItems = ["localized", "coherent", "squeezed", "thermal", "vacuum"];
~qrmPreparationMode = "localized";
~qrmPreparationSemantics = "computational-basis localized state";
~qrmMaxCurrent = 0.0;
~qrmTransport = 0.0;
~qrmMembraneEnergy = 0.0;
~qrmTerrainL = 0.0;
~qrmTerrainOmega = 0.0;
~qrmTerrainStabilityDt = 0.0;
~qrmTerrainSubsteps = 0;
~qrmMembraneOmega = 0.0;
~qrmMembraneStabilityDt = 0.0;
~qrmMembraneSubsteps = 0;
~qrmStagePopulations = ~qrmPopulations.copy;
~qrmStageRhoReal = ~qrmRhoReal.copy;
~qrmStageRhoImag = ~qrmRhoImag.copy;
~qrmStageQ = ~qrmQ.copy;
~qrmStageQdot = ~qrmQdot.copy;
~qrmStageModes = ~qrmModes.copy;
~qrmStageRawModes = ~qrmRawModes.copy;
~qrmStageModeVelocities = ~qrmModeVelocities.copy;
~qrmStageRatios = ~qrmRatios.copy;
~qrmStageInterferenceTimbreGains = ~qrmInterferenceTimbreGains.copy;
~qrmStageInterferenceTimbreOutputAmplitudes = ~qrmInterferenceTimbreOutputAmplitudes.copy;
~qrmStageInterferenceTimbreSlew = ~qrmInterferenceTimbreSlew;
~qrmStageInterferenceTimbrePhase = ~qrmInterferenceTimbrePhase;
~qrmStageInterferenceTimbreSpread = ~qrmInterferenceTimbreSpread;
~qrmStageInterferenceTimbreDepth = ~qrmInterferenceTimbreDepth;
~qrmStageInterferenceTimbreSource = ~qrmInterferenceTimbreSource;
~qrmStageInterferenceTimbreCancellation = ~qrmInterferenceTimbreCancellation;
~qrmStageInterferenceTimbreValid = false;
~qrmStageFlux = ~qrmFlux.copy;
~qrmStagePreparationMode = ~qrmPreparationMode;
~qrmStagePreparationSemantics = ~qrmPreparationSemantics;
~qrmStageFieldOffsets = ~qrmFieldOffsets.copy;
~qrmStageFieldSusceptibility = ~qrmFieldSusceptibility.copy;
~qrmStageCrossings = List.new;
~qrmBuresDelta = 0.0;
~qrmBuresLength = 0.0;
~qrmBuresRemainder = 0.0;
~qrmBuresPulses = 0;
~qrmBuresRecordIndex = 0;
~qrmBuresWeightedTime = 0.0;
~qrmBuresGeodesicRemainder = 0.0;
~qrmBuresGeodesicPulses = 0;
~qrmBuresGeodesicRecordIndex = 0;
~qrmBuresChord = 0.0;
~qrmBuresTriangleDefect = 0.0;
~qrmBuresNormalizedBending = 0.0;
~qrmBuresDistance = 0.025;
~qrmClockScale = 1.0;
~qrmGeodesicBendingDepth = 0.6;
~qrmStageBuresDelta = 0.0;
~qrmStageBuresLength = 0.0;
~qrmStageBuresRemainder = 0.0;
~qrmStageBuresPulses = 0;
~qrmStageBuresRecordIndex = 0;
~qrmStageBuresWeightedTime = 0.0;
~qrmStageBuresGeodesicRemainder = 0.0;
~qrmStageBuresGeodesicPulses = 0;
~qrmStageBuresGeodesicRecordIndex = 0;
~qrmStageBuresChord = 0.0;
~qrmStageBuresTriangleDefect = 0.0;
~qrmStageBuresNormalizedBending = 0.0;
~qrmFundamental = 72.0;
~qrmMaster = 0.16;
~qrmMotionGain = 0.75;
~qrmStrikeGain = 0.45;
~qrmBodyResponse = 0.055;
~qrmCrossingDecay = 0.09;
~qrmModeGains = Array.fill(modeCount, 1.0);
~qrmModeMutes = Array.fill(modeCount, 0);
~qrmAuditionMode = -1;
~qrmSelectedModeIndex = 0;
~qrmHarmonicMix = 0.45;
~qrmPulseDepth = 0.8;
~qrmPulseLevel = 1.0;
~qrmPulseAttack = 0.012;
~qrmPulseDecay = 0.28;
~qrmPulseRelease = 0.9;
// The default is the legacy shared pulse life.  Modal-geometry V3 replaces
// this with the exact per-mode Q/(pi*f) array only while it is applied.
~qrmModalDecaySeconds = Array.fill(modeCount, ~qrmPulseDecay);
~qrmEnergyDecayAmount = 0.55;
~qrmFieldTimbreDepth = 1.0;
~qrmMomentumTimbreDepth = 0.55;
~qrmRingMix = 0.0;
~qrmRingHarmonic = 2;
~qrmFuzzMix = 0.0;
~qrmFuzzDrive = 8.0;
~qrmFuzzBias = 0.12;
~qrmFuzzTone = 5200.0;
~qrmPulseRates = Array.fill(modeCount, { |index| 0.45 + (index * 0.055) });
~qrmPulseActivities = Array.fill(modeCount, 0.0);
~qrmPulseDecayScales = Array.fill(modeCount, 1.0);
~qrmPulseBrightness = Array.fill(modeCount, 0.0);
// These are explicitly downstream audio adapters.  They never feed back into
// the density, field, or membrane evolution; they only make those observers
// structurally audible in the modal body.
~qrmPulseDetunes = Array.fill(modeCount, 0.0);
~qrmPulseDrives = Array.fill(modeCount, 1.0);
~qrmHarmonicGains = Array.fill(harmonicCount, 1.0);
~qrmHarmonicMutes = Array.fill(harmonicCount, 0);
~qrmAuditionHarmonic = -1;
~qrmTimeMode = 0;
~qrmTimeModeNames = [
    "Event Threshold (live)", "Quantum / Bures", "Fixed", "Euclidean",
    "Q-Euclidean", "Q-Geodesic", "Q-Recursive"
];
~qrmFixedRate = 7.0;
~qrmEuclideanHits = 5;
~qrmEuclideanSteps = 8;
~qrmEuclideanStep = 0;
~qrmQuantumEuclideanStep = 0;
~qrmRecursiveDepth = 3;
~qrmLatestCrossing = nil;
~qrmStrikeNodes = List.new;
~qrmMaxStrikeVoices = 16;
~qrmMaxCrossingsPerFrame = 6;
~qrmWaveHistory = Array.new;
~qrmWaveEnvelopeHistory = Array.new;
~qrmWaveHistoryLength = 12;
~qrmWaveScale = 1e-6;
~qrmWaveFrameCounter = 0;
// Visual sampling is deliberately separate from 30 Hz source physics/audio.
// One updates the native mesh at the 15 Hz GUI cadence; larger divisors are
// available only as an explicit low-CPU presentation choice.
~qrmMeshRefreshDivisor = (~qrmMeshRefreshDivisor ? 1).asInteger.clip(1, 4);
~qrmPresetSlotCount = 32;
~qrmPresetSlots = if(File.exists(presetPath), {
    try { Object.readArchive(presetPath) } { Array.newClear(32) }
}, {
    Array.newClear(32)
});

// Downstream energy-to-decay adapter, matching V4.2's bipolar mapping without
// feeding sound parameters back into rho or the membrane integrator.
~qrmEffectiveCrossingDecay = {
    var energyControl = ((~qrmMembraneEnergy.max(0) + 1).log / 2.5.log).clip(0, 1);
    (~qrmCrossingDecay * 2.pow(
        ~qrmEnergyDecayAmount.clip(-1, 1) * energyControl
    )).clip(0.02, 4.0)
};
// Field / momentum / energy are state-derived observers.  Their map below is
// intentionally perceptual: field bends the struck-mode pitch, momentum adds
// strike density and brilliance, and energy changes ring time.  This gives
// each adapter a direct audible role without declaring it quantum dynamics.
~qrmUpdateDynamicAdapters = {
    var energyControl, energyDecayFactor;
    energyControl = (1 - (-0.55 * ~qrmMembraneEnergy.max(0)).exp).clip(0, 1);
    energyDecayFactor = 2.pow(
        ~qrmEnergyDecayAmount.clip(-1, 1) * energyControl * 3.0
    );
    ~qrmPulseRates = Array.fill(modeCount, { |index|
        var momentum = 1 - (-7.5 * ~qrmModeVelocities[index].abs).exp;
        (0.08 + (~qrmPulseActivities[index]
            * ~qrmFixedRate * ~qrmClockScale * (0.55 + (index / modeCount))
            * (1 + (momentum * ~qrmMomentumTimbreDepth.clip(0, 2) * 2.8))))
            .clip(0.08, 24)
    });
    ~qrmPulseDecayScales = Array.fill(modeCount, { |index|
        ((0.44 + (~qrmFieldSusceptibility[index] * 1.55))
            * energyDecayFactor).clip(0.16, 4.0)
    });
    ~qrmPulseBrightness = Array.fill(modeCount, { |index|
        var momentum = 1 - (-7.5 * ~qrmModeVelocities[index].abs).exp;
        var field = 1 - (-8.0 * ~qrmFieldOffsets[index].abs).exp;
        ((momentum * ~qrmMomentumTimbreDepth.clip(0, 2) * 1.1)
            + (field * ~qrmFieldTimbreDepth.clip(0, 2) * 1.15)
            + ((~qrmCoherence / 3).clip(0, 1) * 0.18)).clip(0, 1)
    });
    ~qrmPulseDetunes = Array.fill(modeCount, { |index|
        var field = 1 - (-8.0 * ~qrmFieldOffsets[index].abs).exp;
        (~qrmFieldOffsets[index].sign * field
            * ~qrmFieldTimbreDepth.clip(0, 2) * 0.09).clip(-0.18, 0.18)
    });
    ~qrmPulseDrives = Array.fill(modeCount, { |index|
        var momentum = 1 - (-7.5 * ~qrmModeVelocities[index].abs).exp;
        var field = 1 - (-8.0 * ~qrmFieldOffsets[index].abs).exp;
        (0.52 + (field * ~qrmFieldTimbreDepth.clip(0, 2) * 0.62)
            + (momentum * ~qrmMomentumTimbreDepth.clip(0, 2) * 0.92))
            .clip(0.18, 2.8)
    });
    if(~qrmAudioReady and: { ~qrmBody.notNil }) {
        ~qrmBody.setn(\pulseRates, ~qrmPulseRates);
        ~qrmBody.setn(\pulseDecayScales, ~qrmPulseDecayScales);
        ~qrmBody.setn(\pulseBrightness, ~qrmPulseBrightness);
        ~qrmBody.setn(\pulseDetunes, ~qrmPulseDetunes);
        ~qrmBody.setn(\pulseDrives, ~qrmPulseDrives);
    };
};
if(~qrmPresetSlots.isKindOf(Array).not) {
    ~qrmPresetSlots = Array.newClear(~qrmPresetSlotCount)
};
if(~qrmPresetSlots.size < ~qrmPresetSlotCount) {
    ~qrmPresetSlots = ~qrmPresetSlots ++ Array.newClear(
        ~qrmPresetSlotCount - ~qrmPresetSlots.size
    )
};
~qrmEuclideanMask = Array.fill(16, { |index|
    if(index < 8) { (((index * 5) % 8) < 5).asInteger } { 0 }
});
~qrmUpdateEuclideanMask = {
    var steps = ~qrmEuclideanSteps.clip(2, 16).asInteger;
    var hits = ~qrmEuclideanHits.clip(1, steps).asInteger;
    ~qrmEuclideanSteps = steps;
    ~qrmEuclideanHits = hits;
    ~qrmEuclideanMask = Array.fill(16, { |index|
        if(index < steps) { (((index * hits) % steps) < hits).asInteger } { 0 }
    });
};
~qrmParseScalaFile = { |path|
    var source, lines, description, declaredCount, pitchLines, ratios, period;
    var degrees, token, pieces, ratio;
    source = File.readAllString(path);
    lines = source.split(Char.nl).collect { |line| line.stripWhiteSpace }
        .select { |line| line.notEmpty and: { line.beginsWith("!").not } };
    if(lines.size < 2) {
        Error("invalid Scala file: missing description/count").throw
    };
    description = lines[0];
    declaredCount = lines[1].asInteger;
    pitchLines = lines.copyRange(2, (1 + declaredCount).min(lines.size - 1));
    if(pitchLines.size != declaredCount) {
        Error("invalid Scala file: declared degree count does not match data").throw
    };
    ratios = [1.0] ++ pitchLines.collect { |line|
        token = line.split($ )[0];
        if(token.contains("/"), {
            pieces = token.split($/);
            ratio = pieces[0].asFloat / pieces[1].asFloat;
        }, {
            ratio = if(token.contains("."), {
                2.pow(token.asFloat / 1200)
            }, {
                token.asFloat
            });
        });
        if(ratio.isNaN or: { ratio == inf } or: { ratio == -inf } or: { ratio <= 0 }) {
            Error("invalid Scala interval: " ++ token).throw
        };
        ratio
    };
    period = if(ratios.last > 1.0, { ratios.last }, { 2.0 });
    degrees = if(ratios.last > 1.0 and: { ratios.size > 1 }, {
        ratios.copyRange(0, ratios.size - 2)
    }, {
        ratios
    });
    if(degrees.isEmpty) { degrees = [1.0] };
    (
        description: description,
        degrees: degrees,
        period: period,
        path: path
    )
};
~qrmLoadScalaPath = { |path|
    var scale;
    try {
        scale = ~qrmParseScalaFile.(path);
        ~qrmSelectedScalaPath = path;
        ~qrmActiveTuningDescription = scale[\description];
        ~qrmActiveTuningDegrees = scale[\degrees];
        ~qrmActiveTuningPeriod = scale[\period];
        ~qrmTuningStatus !? { |view|
            view.string_("%  /  % degrees  /  period %".format(
                ~qrmActiveTuningDescription,
                ~qrmActiveTuningDegrees.size,
                ~qrmActiveTuningPeriod.round(0.00001)
            ))
        };
    } { |error|
        ~qrmTuningStatus !? { |view| view.string_("Scala error: " ++ error) };
        error.warn;
    };
};
~qrmRefreshTuningChoices = {
    var paths = ~qrmScalaAllPaths;
    var filter = ~qrmScalaFilter.toLower;
    var preferred;
    paths = case
    { ~qrmTuningFamily == 1 } {
        preferred = "wilson7.scl";
        paths.select { |path| path.fileName.toLower.contains("wilson") }
    }
    { ~qrmTuningFamily == 2 } {
        preferred = "tenney1.scl";
        paths.select { |path| path.fileName.toLower.contains("tenney") }
    }
    { ~qrmTuningFamily == 3 } {
        preferred = "young-lm_piano.scl";
        paths.select { |path| path.fileName.toLower.beginsWith("young-lm_") }
    }
    { ~qrmTuningFamily == 4 } {
        if(filter.notEmpty, {
            paths.select { |path| path.fileName.toLower.contains(filter) }
        }, {
            paths.copyRange(0, 511.min(paths.size - 1))
        })
    }
    { Array.new };
    ~qrmScalaPaths = paths;
    ~qrmScalaNames = if(paths.isEmpty, { ["no matching Scala scales"] }, {
        paths.collect { |path| path.fileNameWithoutExtension }
    });
    ~qrmScalaMenu !? { |menu|
        var selected = paths.detectIndex { |path|
            path.fullPath == ~qrmSelectedScalaPath
        };
        if(selected.isNil and: { preferred.notNil }) {
            selected = paths.detectIndex { |path| path.fileName == preferred }
        };
        selected = selected ? 0;
        menu.items_(~qrmScalaNames).value_(selected);
        if(paths.notEmpty) { ~qrmLoadScalaPath.(paths[selected].fullPath) };
    };
};
~qrmScaleRatioAt = { |degree|
    var count = ~qrmActiveTuningDegrees.size.max(1);
    var safeDegree = degree.asInteger.max(0);
    var cycle = (safeDegree / count).floor;
    ~qrmActiveTuningDegrees[safeDegree % count]
        * ~qrmActiveTuningPeriod.pow(cycle)
};
~qrmUpdatePitchRatios = {
    var offsetRatio;
    if(~qrmTuningFamily == 0) {
        ~qrmActiveTuningDescription = "% equal divisions of 2/1".format(~qrmEDO);
        ~qrmActiveTuningDegrees = Array.fill(~qrmEDO, { |index|
            2.pow(index / ~qrmEDO)
        });
        ~qrmActiveTuningPeriod = 2.0;
    };
    offsetRatio = ~qrmScaleRatioAt.(~qrmTuningDegreeOffset).max(1e-12);
    ~qrmPitchRatios = case
    { ~qrmPitchMode == 0 } { ~qrmRatios.copy }
    { ~qrmPitchMode == 1 } {
        Array.fill(modeCount, { |index| (index % 16) + 1.0 })
    }
    { ~qrmPitchMode == 2 } {
        Array.fill(modeCount, { |index| (2 * (index % 16)) + 1.0 })
    }
    {
        Array.fill(modeCount, { |index|
            ~qrmScaleRatioAt.(index + ~qrmTuningDegreeOffset) / offsetRatio
        })
    };
    ~qrmBody !? { |node| node.setn(\frequencyRatios, ~qrmPitchRatios) };
};
~qrmModeAudioWeights = {
    Array.fill(modeCount, { |index|
        ~qrmModeGains[index].clip(0, 2)
        * (1 - ~qrmModeMutes[index].clip(0, 1))
        * if(~qrmAuditionMode < 0 or: { ~qrmAuditionMode == index }) { 1 } { 0 }
    })
};
~qrmHarmonicAudioWeights = {
    Array.fill(harmonicCount, { |index|
        ~qrmHarmonicGains[index].clip(0, 2)
        * (1 - ~qrmHarmonicMutes[index].clip(0, 1))
        * if(~qrmAuditionHarmonic < 0 or: { ~qrmAuditionHarmonic == index }) { 1 } { 0 }
    })
};
~qrmPushModeMix = {
    var nativeWeights = ~qrmModeAudioWeights.();
    var harmonicWeights = ~qrmHarmonicAudioWeights.();
    ~qrmBody !? { |node|
        node.setn(\modalAmplitudes, ~qrmModes * nativeWeights);
        node.setn(\interferenceTimbreGains, ~qrmInterferenceTimbreGains);
        node.set(\interferenceTimbreSlew, ~qrmInterferenceTimbreSlew);
        // H1-H16 is a monitor derived from M1-M16. Native M gain is the
        // upstream source gain; the harmonic lane is an additional trim.
        node.setn(
            \harmonicAmplitudes,
            ~qrmModes.copyRange(0, harmonicCount - 1)
            * nativeWeights.copyRange(0, harmonicCount - 1)
            * harmonicWeights
        );
    };
};
~qrmSetModeGain = { |index, gain|
    var lane = index.asInteger.clip(0, modeCount - 1);
    ~qrmModeGains[lane] = gain.clip(0, 2);
    ~qrmSelectedModeIndex = lane;
    ~qrmModeGainStatus !? { |status|
        status.string_("M%  volume %".format(
            lane + 1, ~qrmModeGains[lane].round(0.01)
        ));
    };
    ~qrmPushModeMix.value;
};
~qrmSetModeCombination = { |gains|
    if(gains.size == modeCount) {
        ~qrmModeGains = gains.collect { |gain| gain.asFloat.clip(0, 2) };
        ~qrmModeGainView !? { |view| view.value_(~qrmModeGains / 2) };
        ~qrmModeGainStatus !? { |status|
            status.string_("20-mode combination loaded")
        };
        ~qrmPushModeMix.value;
    } {
        "QRM rejected mode combination: expected 20 gains".warn;
    };
};
~qrmPushPerformanceFx = {
    ~qrmBody !? { |node|
        node.set(
            \ringMix, ~qrmRingMix,
            \ringHarmonic, ~qrmRingHarmonic,
            \fuzzMix, ~qrmFuzzMix,
            \fuzzDrive, ~qrmFuzzDrive,
            \fuzzBias, ~qrmFuzzBias,
            \fuzzTone, ~qrmFuzzTone
        );
    };
    ~qmwTemporalMemoryPushFuzz !? { |push| push.value };
};
~qrmDataPort = dataPort;
~qrmControlPort = controlPort;

thisProcess.openUDPPort(dataPort);
~qrmControl = NetAddr("127.0.0.1", controlPort);

~qrmSonicReset = {
    ~qrmSonicGeneration = ~qrmSonicGeneration + 1;
    ~qrmSonicGateUntil = Main.elapsedTime + 0.25;
    ~qrmLatestCrossing = nil;
    ~qrmEuclideanStep = 0;
    ~qrmQuantumEuclideanStep = 0;
    ~qrmCrossingFlash = 0.0;
    ~qrmWaveHistory = Array.new;
    ~qrmWaveEnvelopeHistory = Array.new;
    ~qrmWaveScale = 1e-6;
    ~qrmStrikeGroup !? _.freeAll;
    ~qrmStrikeNodes.clear;
    ~qrmBody !? { |node|
        node.setn(\modalAmplitudes, Array.fill(modeCount, 0.0));
        node.setn(\harmonicAmplitudes, Array.fill(harmonicCount, 0.0));
        node.set(\master, 0.0);
    };
};

s.options.numWireBufs = s.options.numWireBufs.max(2048);
s.options.memSize = s.options.memSize.max(262144);

~qrmDefineSynths = {
    var performanceFx = {
        |dry, fundamental, ringMix, ringHarmonic,
        fuzzMix, fuzzDrive, fuzzBias, fuzzTone|
        var ringAmount = Lag.kr(ringMix.clip(0, 1), 0.03);
        var overtone = Lag.kr(ringHarmonic.round.clip(1, 16), 0.03);
        var ringFrequency = (fundamental * overtone).clip(
            1, SampleRate.ir * 0.45
        );
        var ringed = dry * SinOsc.ar(ringFrequency) * 2.sqrt;
        var ringOutput = XFade2.ar(dry, ringed, (ringAmount * 2) - 1);
        var fuzzAmount = Lag.kr(fuzzMix.clip(0, 1), 0.03);
        var drive = Lag.kr(fuzzDrive.clip(1, 40), 0.03);
        var bias = Lag.kr(fuzzBias.clip(-0.45, 0.45), 0.03);
        var tone = Lag.kr(fuzzTone.clip(800, 12000), 0.03);
        // Fuzz Face-inspired two-stage transfer: input coupling, biased first
        // transistor, frequency-shaped interstage loading, asymmetric second
        // transistor/diode limiting, output coupling, then a passive-like tone
        // rolloff. This is a bounded circuit-inspired model, not SPICE.
        var coupled = HPF.ar(ringOutput, 24);
        var firstStage = ((coupled * drive) + bias).tanh;
        var interstage = firstStage - (LPF.ar(firstStage, 720) * 0.24);
        var secondStage = (
            (interstage * (1.6 + (drive.sqrt * 0.32))) + (bias * 0.55)
        ).tanh;
        var asymmetric = secondStage.clip(
            -0.72 + (bias * 0.12), 0.50 + (bias * 0.12)
        );
        var fuzzed = LPF.ar(LeakDC.ar(asymmetric), tone) * 0.92;
        XFade2.ar(ringOutput, fuzzed, (fuzzAmount * 2) - 1)
    };
    SynthDef(\qrmMembraneBodyV1, { |out=0, fundamental=72, master=0.16,
        bodyEnabled=1, fieldGain=1,
        motionGain=0.75, response=0.055, harmonicMix=0.45, pulseDepth=0.8,
        interferenceTimbreSlew=0.08,
        pulseLevel=1.0, pulseAttack=0.012, pulseDecay=0.28, pulseRelease=0.9,
        ringMix=0, ringHarmonic=2, fuzzMix=0, fuzzDrive=8, fuzzBias=0.12,
        fuzzTone=5200|
        var ratios = NamedControl.kr(\frequencyRatios, Array.fill(modeCount, 1.0));
        var amplitudes = NamedControl.kr(\modalAmplitudes, Array.fill(modeCount, 0.0));
        var harmonicAmplitudes = NamedControl.kr(
            \harmonicAmplitudes, Array.fill(harmonicCount, 0.0)
        );
        var interferenceTimbreGains = NamedControl.kr(
            \interferenceTimbreGains, Array.fill(modeCount, 1.0)
        );
        var frequencies = (fundamental * ratios).clip(28, 16000);
        var pulseRates = NamedControl.kr(\pulseRates, Array.fill(modeCount, 1.0));
        var pulseActivities = NamedControl.kr(
            \pulseActivities, Array.fill(modeCount, 0.0)
        );
        var pulseDecayScales = NamedControl.kr(
            \pulseDecayScales, Array.fill(modeCount, 1.0)
        );
        var modalDecaySeconds = NamedControl.kr(
            \modalDecaySeconds, Array.fill(modeCount, 0.28)
        );
        var pulseBrightness = NamedControl.kr(
            \pulseBrightness, Array.fill(modeCount, 0.0)
        );
        var pulseDetunes = NamedControl.kr(
            \pulseDetunes, Array.fill(modeCount, 0.0)
        );
        var pulseDrives = NamedControl.kr(
            \pulseDrives, Array.fill(modeCount, 1.0)
        );
        var pulseExcitations = Array.fill(modeCount, { |index|
            var pulseEnvelope = EnvGen.ar(
                Env(
                    [0, 1, 0.42, 0],
                    [
                        pulseAttack.clip(0.001, 0.25),
                        pulseDecay.clip(0.02, 2.0),
                        pulseRelease.clip(0.05, 6.0)
                    ],
                    [4, -3, -5]
                ),
                Impulse.ar(pulseRates[index].clip(0.08, 24), index / modeCount)
                    * bodyEnabled.clip(0, 1)
            );
            HPF.ar(
                PinkNoise.ar(0.34),
                pulseBrightness[index].clip(0, 1).linexp(0, 1, 45, 5200)
            ) * pulseEnvelope
            // No autonomous excitation floor: a muted/zero-activity field must
            // be silent. Square-root activity still keeps weak, real motion
            // audible once the Field or Hybrid body has been intentionally enabled.
            * pulseActivities[index].clip(0, 1).sqrt
        });
        var signals = Array.fill(modeCount, { |index|
            var air = 1 + SinOsc.kr(0.025 + (index * 0.0017), index * 0.21, 0.0015);
            var timbreGain = Lag.kr(interferenceTimbreGains[index],
                interferenceTimbreSlew.clip(0, 10));
            var amplitude = Lag.kr(amplitudes[index], response.clip(0.005, 1.5))
                * timbreGain * bodyEnabled.clip(0, 1);
            var sustained = SinOsc.ar(frequencies[index] * air);
            var pulseFrequency = (frequencies[index] * air
                * (1 + pulseDetunes[index].clip(-0.18, 0.18))).clip(28, 16000);
            var resonant = Ringz.ar(
                pulseExcitations[index], pulseFrequency,
                modalDecaySeconds[index]
            ) * 1.15;
            // Pulses are an independently excited modal body, not merely a
            // tiny texture inside an already quiet sustained mode.  Thus all
            // four pulse controls have a clear structural effect.
            XFade2.ar(
                sustained * amplitude,
                resonant * amplitude * pulseLevel.clip(0, 2)
                    * pulseDrives[index].clip(0.18, 2.8),
                Lag.kr((pulseDepth.clip(0, 1) * 2) - 1, 0.03)
            );
        });
        var harmonicSignals = Array.fill(harmonicCount, { |index|
            var frequency = (fundamental * (index + 1)).clip(28, 16000);
            var timbreGain = Lag.kr(interferenceTimbreGains[index],
                interferenceTimbreSlew.clip(0, 10));
            var amplitude = Lag.kr(
                harmonicAmplitudes[index], response.clip(0.005, 1.5)
            ) * timbreGain * bodyEnabled.clip(0, 1) / (index + 1).sqrt;
            var sustained = SinOsc.ar(frequency);
            var pulseFrequency = (frequency
                * (1 + pulseDetunes[index].clip(-0.18, 0.18))).clip(28, 16000);
            var resonant = Ringz.ar(
                pulseExcitations[index], pulseFrequency,
                (pulseDecay * pulseDecayScales[index]
                    * (1 + (index * 0.018))).clip(0.02, 4.0)
            ) * 0.72;
            XFade2.ar(
                sustained * amplitude,
                resonant * amplitude * pulseLevel.clip(0, 2)
                    * pulseDrives[index].clip(0.18, 2.8),
                Lag.kr((pulseDepth.clip(0, 1) * 2) - 1, 0.03)
            )
        });
        var geometryOutput = Splay.ar(signals, 0.82, 1.0, 0.0);
        var harmonicOutput = Splay.ar(
            harmonicSignals, 0.82, harmonicMix.clip(0, 1.5), 0.0
        );
        var output = performanceFx.(
            LeakDC.ar(geometryOutput + harmonicOutput), fundamental,
            ringMix, ringHarmonic, fuzzMix, fuzzDrive, fuzzBias, fuzzTone
        );
        Out.ar(out, Limiter.ar(
            output * motionGain * Lag.kr(master, 0.08)
            * Lag.kr(fieldGain.clip(0, 1), 0.05), 0.82
        ));
    }).add;

    SynthDef(\qrmMembraneBody8V1, { |out=0, fundamental=72, master=0.16,
        bodyEnabled=1, fieldGain=1,
        motionGain=0.75, response=0.055, harmonicMix=0.45, pulseDepth=0.8,
        interferenceTimbreSlew=0.08,
        pulseLevel=1.0, pulseAttack=0.012, pulseDecay=0.28, pulseRelease=0.9,
        ringMix=0, ringHarmonic=2, fuzzMix=0, fuzzDrive=8, fuzzBias=0.12,
        fuzzTone=5200|
        var ratios = NamedControl.kr(\frequencyRatios, Array.fill(modeCount, 1.0));
        var amplitudes = NamedControl.kr(\modalAmplitudes, Array.fill(modeCount, 0.0));
        var harmonicAmplitudes = NamedControl.kr(
            \harmonicAmplitudes, Array.fill(harmonicCount, 0.0)
        );
        var interferenceTimbreGains = NamedControl.kr(
            \interferenceTimbreGains, Array.fill(modeCount, 1.0)
        );
        var frequencies = (fundamental * ratios).clip(28, 16000);
        var pulseRates = NamedControl.kr(\pulseRates, Array.fill(modeCount, 1.0));
        var pulseActivities = NamedControl.kr(
            \pulseActivities, Array.fill(modeCount, 0.0)
        );
        var pulseDecayScales = NamedControl.kr(
            \pulseDecayScales, Array.fill(modeCount, 1.0)
        );
        var modalDecaySeconds = NamedControl.kr(
            \modalDecaySeconds, Array.fill(modeCount, 0.28)
        );
        var pulseBrightness = NamedControl.kr(
            \pulseBrightness, Array.fill(modeCount, 0.0)
        );
        var pulseDetunes = NamedControl.kr(
            \pulseDetunes, Array.fill(modeCount, 0.0)
        );
        var pulseDrives = NamedControl.kr(
            \pulseDrives, Array.fill(modeCount, 1.0)
        );
        var pulseExcitations = Array.fill(modeCount, { |index|
            var pulseEnvelope = EnvGen.ar(
                Env(
                    [0, 1, 0.42, 0],
                    [
                        pulseAttack.clip(0.001, 0.25),
                        pulseDecay.clip(0.02, 2.0),
                        pulseRelease.clip(0.05, 6.0)
                    ],
                    [4, -3, -5]
                ),
                Impulse.ar(pulseRates[index].clip(0.08, 24), index / modeCount)
                    * bodyEnabled.clip(0, 1)
            );
            HPF.ar(
                PinkNoise.ar(0.34),
                pulseBrightness[index].clip(0, 1).linexp(0, 1, 45, 5200)
            ) * pulseEnvelope
            * pulseActivities[index].clip(0, 1).sqrt
        });
        var signals = Array.fill(modeCount, { |index|
            var air = 1 + SinOsc.kr(0.025 + (index * 0.0017), index * 0.21, 0.0015);
            var timbreGain = Lag.kr(interferenceTimbreGains[index],
                interferenceTimbreSlew.clip(0, 10));
            var amplitude = Lag.kr(amplitudes[index], response.clip(0.005, 1.5))
                * timbreGain * bodyEnabled.clip(0, 1);
            var sustained = SinOsc.ar(frequencies[index] * air);
            var pulseFrequency = (frequencies[index] * air
                * (1 + pulseDetunes[index].clip(-0.18, 0.18))).clip(28, 16000);
            var resonant = Ringz.ar(
                pulseExcitations[index], pulseFrequency,
                modalDecaySeconds[index]
            ) * 1.15;
            XFade2.ar(
                sustained * amplitude,
                resonant * amplitude * pulseLevel.clip(0, 2)
                    * pulseDrives[index].clip(0.18, 2.8),
                Lag.kr((pulseDepth.clip(0, 1) * 2) - 1, 0.03)
            );
        });
        var harmonicSignals = Array.fill(harmonicCount, { |index|
            var frequency = (fundamental * (index + 1)).clip(28, 16000);
            var timbreGain = Lag.kr(interferenceTimbreGains[index],
                interferenceTimbreSlew.clip(0, 10));
            var amplitude = Lag.kr(
                harmonicAmplitudes[index], response.clip(0.005, 1.5)
            ) * timbreGain * bodyEnabled.clip(0, 1) / (index + 1).sqrt;
            var sustained = SinOsc.ar(frequency);
            var pulseFrequency = (frequency
                * (1 + pulseDetunes[index].clip(-0.18, 0.18))).clip(28, 16000);
            var resonant = Ringz.ar(
                pulseExcitations[index], pulseFrequency,
                (pulseDecay * pulseDecayScales[index]
                    * (1 + (index * 0.018))).clip(0.02, 4.0)
            ) * 0.72;
            XFade2.ar(
                sustained * amplitude,
                resonant * amplitude * pulseLevel.clip(0, 2)
                    * pulseDrives[index].clip(0.18, 2.8),
                Lag.kr((pulseDepth.clip(0, 1) * 2) - 1, 0.03)
            )
        });
        // Twenty native modes and sixteen derived harmonics retain separate
        // azimuths as they wrap around the eight hardware output buses.
        var geometryOutput = Mix.fill(modeCount, { |index|
            PanAz.ar(8, signals[index], index.linlin(0, modeCount - 1, -1, 1), 1, 2)
        }) / modeCount.sqrt;
        var harmonicOutput = Mix.fill(harmonicCount, { |index|
            PanAz.ar(
                8, harmonicSignals[index],
                (index.linlin(0, harmonicCount - 1, -0.9375, 1.0625)).wrap(-1, 1),
                harmonicMix.clip(0, 1.5), 2
            )
        }) / harmonicCount.sqrt;
        var output = performanceFx.(
            LeakDC.ar(geometryOutput + harmonicOutput), fundamental,
            ringMix, ringHarmonic, fuzzMix, fuzzDrive, fuzzBias, fuzzTone
        );
        // Limiter expands per channel: no shared detector can duck all buses.
        Out.ar(out, Limiter.ar(
            output * motionGain * Lag.kr(master, 0.08)
            * Lag.kr(fieldGain.clip(0, 1), 0.05), 0.82
        ));
    }).add;

    SynthDef(\qrmMembraneBody16V1, { |out=0, fundamental=72, master=0.16,
        bodyEnabled=1, fieldGain=1,
        motionGain=0.75, response=0.055, harmonicMix=0.45, pulseDepth=0.8,
        interferenceTimbreSlew=0.08,
        pulseLevel=1.0, pulseAttack=0.012, pulseDecay=0.28, pulseRelease=0.9,
        ringMix=0, ringHarmonic=2, fuzzMix=0, fuzzDrive=8, fuzzBias=0.12,
        fuzzTone=5200|
        var ratios = NamedControl.kr(\frequencyRatios, Array.fill(modeCount, 1.0));
        var amplitudes = NamedControl.kr(\modalAmplitudes, Array.fill(modeCount, 0.0));
        var harmonicAmplitudes = NamedControl.kr(
            \harmonicAmplitudes, Array.fill(harmonicCount, 0.0)
        );
        var interferenceTimbreGains = NamedControl.kr(
            \interferenceTimbreGains, Array.fill(modeCount, 1.0)
        );
        var frequencies = (fundamental * ratios).clip(28, 16000);
        var pulseRates = NamedControl.kr(\pulseRates, Array.fill(modeCount, 1.0));
        var pulseActivities = NamedControl.kr(
            \pulseActivities, Array.fill(modeCount, 0.0)
        );
        var pulseDecayScales = NamedControl.kr(
            \pulseDecayScales, Array.fill(modeCount, 1.0)
        );
        var modalDecaySeconds = NamedControl.kr(
            \modalDecaySeconds, Array.fill(modeCount, 0.28)
        );
        var pulseBrightness = NamedControl.kr(
            \pulseBrightness, Array.fill(modeCount, 0.0)
        );
        var pulseDetunes = NamedControl.kr(
            \pulseDetunes, Array.fill(modeCount, 0.0)
        );
        var pulseDrives = NamedControl.kr(
            \pulseDrives, Array.fill(modeCount, 1.0)
        );
        var pulseExcitations = Array.fill(modeCount, { |index|
            var pulseEnvelope = EnvGen.ar(
                Env(
                    [0, 1, 0.42, 0],
                    [
                        pulseAttack.clip(0.001, 0.25),
                        pulseDecay.clip(0.02, 2.0),
                        pulseRelease.clip(0.05, 6.0)
                    ],
                    [4, -3, -5]
                ),
                Impulse.ar(pulseRates[index].clip(0.08, 24), index / modeCount)
                    * bodyEnabled.clip(0, 1)
            );
            HPF.ar(
                PinkNoise.ar(0.34),
                pulseBrightness[index].clip(0, 1).linexp(0, 1, 45, 5200)
            ) * pulseEnvelope
            * pulseActivities[index].clip(0, 1).sqrt
        });
        var signals = Array.fill(modeCount, { |index|
            var air = 1 + SinOsc.kr(0.025 + (index * 0.0017), index * 0.21, 0.0015);
            var timbreGain = Lag.kr(interferenceTimbreGains[index],
                interferenceTimbreSlew.clip(0, 10));
            var amplitude = Lag.kr(amplitudes[index], response.clip(0.005, 1.5))
                * timbreGain * bodyEnabled.clip(0, 1);
            var sustained = SinOsc.ar(frequencies[index] * air);
            var pulseFrequency = (frequencies[index] * air
                * (1 + pulseDetunes[index].clip(-0.18, 0.18))).clip(28, 16000);
            var resonant = Ringz.ar(
                pulseExcitations[index], pulseFrequency,
                modalDecaySeconds[index]
            ) * 1.15;
            XFade2.ar(
                sustained * amplitude,
                resonant * amplitude * pulseLevel.clip(0, 2)
                    * pulseDrives[index].clip(0.18, 2.8),
                Lag.kr((pulseDepth.clip(0, 1) * 2) - 1, 0.03)
            );
        });
        var harmonicSignals = Array.fill(harmonicCount, { |index|
            var frequency = (fundamental * (index + 1)).clip(28, 16000);
            var timbreGain = Lag.kr(interferenceTimbreGains[index],
                interferenceTimbreSlew.clip(0, 10));
            var amplitude = Lag.kr(
                harmonicAmplitudes[index], response.clip(0.005, 1.5)
            ) * timbreGain * bodyEnabled.clip(0, 1) / (index + 1).sqrt;
            var sustained = SinOsc.ar(frequency);
            var pulseFrequency = (frequency
                * (1 + pulseDetunes[index].clip(-0.18, 0.18))).clip(28, 16000);
            var resonant = Ringz.ar(
                pulseExcitations[index], pulseFrequency,
                (pulseDecay * pulseDecayScales[index]
                    * (1 + (index * 0.018))).clip(0.02, 4.0)
            ) * 0.72;
            XFade2.ar(
                sustained * amplitude,
                resonant * amplitude * pulseLevel.clip(0, 2)
                    * pulseDrives[index].clip(0.18, 2.8),
                Lag.kr((pulseDepth.clip(0, 1) * 2) - 1, 0.03)
            )
        });
        // Twenty membrane modes and sixteen derived harmonics are spatially
        // wrapped across sixteen hardware outputs without truncating M17-M20.
        var geometryOutput = Mix.fill(modeCount, { |index|
            PanAz.ar(16, signals[index], index.linlin(0, modeCount - 1, -1, 1), 1, 2)
        }) / modeCount.sqrt;
        var harmonicOutput = Mix.fill(harmonicCount, { |index|
            PanAz.ar(
                16, harmonicSignals[index],
                index.linlin(0, harmonicCount - 1, -0.9375, 0.9375),
                harmonicMix.clip(0, 1.5), 2
            )
        }) / harmonicCount.sqrt;
        var output = performanceFx.(
            LeakDC.ar(geometryOutput + harmonicOutput), fundamental,
            ringMix, ringHarmonic, fuzzMix, fuzzDrive, fuzzBias, fuzzTone
        );
        Out.ar(out, Limiter.ar(
            output * motionGain * Lag.kr(master, 0.08)
            * Lag.kr(fieldGain.clip(0, 1), 0.05), 0.82
        ));
    }).add;

    // Finite local audition for the continuous modal-body pulse controls.
    // It shares the field body's pulse parameters but does not depend on
    // incoming frame activity, create a persistent layer, or alter QMW state.
    SynthDef(\qrmModalPulseAuditionV1, { |out=0, fundamental=72, master=0.22,
        pulseLevel=1, pulseDepth=0.8, pulseAttack=0.012, pulseDecay=0.28,
        pulseRelease=0.9, ringMix=0, ringHarmonic=2, fuzzMix=0, fuzzDrive=8,
        fuzzBias=0.12, fuzzTone=5200|
        var dynamicDetunes = NamedControl.kr(\dynamicDetunes, Array.fill(modeCount, 0));
        var dynamicBrightness = NamedControl.kr(
            \dynamicBrightness, Array.fill(modeCount, 0)
        );
        var dynamicDecayScales = NamedControl.kr(
            \dynamicDecayScales, Array.fill(modeCount, 1)
        );
        var dynamicDrives = NamedControl.kr(\dynamicDrives, Array.fill(modeCount, 1));
        var auditionIndices = [0, 5, 10, 15];
        var envelope, ratios, detunes, brightness, decayScales, drives;
        var dry, excitation, resonant, signal;
        envelope = EnvGen.kr(
            Env([0, 1, 0.42, 0], [
                pulseAttack.clip(0.001, 0.25),
                pulseDecay.clip(0.02, 2),
                pulseRelease.clip(0.05, 6)
            ], [4, -3, -5]), doneAction: 2
        );
        ratios = [1, 1.25, 1.5, 1.875];
        detunes = auditionIndices.collect { |index| dynamicDetunes[index] };
        brightness = auditionIndices.collect { |index| dynamicBrightness[index] };
        decayScales = auditionIndices.collect { |index| dynamicDecayScales[index] };
        drives = auditionIndices.collect { |index| dynamicDrives[index] };
        dry = Mix(SinOsc.ar((fundamental * ratios * (1 + (detunes * 1.8))).clip(28, 16000)))
            * envelope * 0.06;
        excitation = HPF.ar(
            PinkNoise.ar(0.32), 680 + (brightness.mean.clip(0, 1) * 4200)
        ) * envelope;
        resonant = Mix(Ringz.ar(
            excitation, (fundamental * ratios * (1 + (detunes * 1.8))).clip(28, 16000),
            pulseDecay.clip(0.02, 2) * [1, 0.83, 0.67, 0.53]
                * (0.5 + decayScales.clip(0.16, 4))
        )) * pulseLevel.clip(0, 2) * drives.mean.clip(0.18, 2.8) * 0.42;
        signal = XFade2.ar(
            dry, resonant, Lag.kr((pulseDepth.clip(0, 1) * 2) - 1, 0.03)
        );
        signal = performanceFx.(
            LeakDC.ar(signal), fundamental, ringMix, ringHarmonic,
            fuzzMix, fuzzDrive, fuzzBias, fuzzTone
        );
        Out.ar(out, Limiter.ar(Pan2.ar(signal * master.clip(0, 0.35)), 0.72));
    }).add;

    SynthDef(\qrmBoundaryStrikeV1, { |out=0, fundamental=72, master=0.16,
        strikeGain=0.45, magnitude=0.1, phase=0, pan=0, azimuth=0, decay=0.09,
        coherence=0, localEnergy=0, persistence=1,
        fieldDepth=1, momentumDepth=0.55,
        ringMix=0, ringHarmonic=2, fuzzMix=0, fuzzDrive=8, fuzzBias=0.12,
        fuzzTone=5200|
        var ratios = NamedControl.kr(\frequencyRatios, Array.fill(modeCount, 1.0));
        var weights = NamedControl.kr(\modalWeights, Array.fill(modeCount, 0.0));
        var modalDecaySeconds = NamedControl.kr(
            \modalDecaySeconds, Array.fill(modeCount, 0.28)
        );
        var frequencies = (fundamental * ratios).clip(28, 16000);
        // A deterministic short pressure impulse, rather than a noise burst,
        // excites the canonical twenty-frame bank.  The exact Q/(pi*f) decay
        // seconds remain the frame's resonator lifetime.
        var excitation = Decay2.ar(Impulse.ar(0), 0.0007, 0.005) * 0.25;
        var fieldControl = (phase.sin * fieldDepth).tanh;
        var momentumControl = (
            phase.cos.sign * (magnitude * 6).tanh * momentumDepth
        ).tanh;
        var frequencyBend = 1 + (fieldControl * 0.012) + (momentumControl * 0.018);
        var bands = Ringz.ar(
            excitation, (frequencies * frequencyBend).clip(28, 16000), modalDecaySeconds
        );
        var envelope = EnvGen.kr(
            Env.linen(0, decay.clip(0.02, 4.0) * 1.35, 0.04), doneAction: 2
        );
        var signal = Mix(bands * weights) / modeCount.sqrt;
        signal = HPF.ar(LeakDC.ar(signal), 28);
        signal = performanceFx.(
            signal, fundamental, ringMix, ringHarmonic,
            fuzzMix, fuzzDrive, fuzzBias, fuzzTone
        );
        Out.ar(out, Limiter.ar(Pan2.ar(
            signal * envelope * magnitude.clip(0, 2).sqrt
            * (0.72 + (localEnergy.clip(0, 2) * 0.18))
            * strikeGain * master,
            pan
        ), 0.86));
    }).add;

    SynthDef(\qrmBoundaryStrike8V1, { |out=0, fundamental=72, master=0.16,
        strikeGain=0.45, magnitude=0.1, phase=0, pan=0, azimuth=0, decay=0.09,
        coherence=0, localEnergy=0, persistence=1,
        fieldDepth=1, momentumDepth=0.55,
        ringMix=0, ringHarmonic=2, fuzzMix=0, fuzzDrive=8, fuzzBias=0.12,
        fuzzTone=5200|
        var ratios = NamedControl.kr(\frequencyRatios, Array.fill(modeCount, 1.0));
        var weights = NamedControl.kr(\modalWeights, Array.fill(modeCount, 0.0));
        var modalDecaySeconds = NamedControl.kr(
            \modalDecaySeconds, Array.fill(modeCount, 0.28)
        );
        var frequencies = (fundamental * ratios).clip(28, 16000);
        var excitation = Decay2.ar(Impulse.ar(0), 0.0007, 0.005) * 0.25;
        var fieldControl = (phase.sin * fieldDepth).tanh;
        var momentumControl = (
            phase.cos.sign * (magnitude * 6).tanh * momentumDepth
        ).tanh;
        var frequencyBend = 1 + (fieldControl * 0.012) + (momentumControl * 0.018);
        var bands = Ringz.ar(
            excitation, (frequencies * frequencyBend).clip(28, 16000), modalDecaySeconds
        );
        var envelope = EnvGen.kr(
            Env.linen(0, decay.clip(0.02, 4.0) * 1.35, 0.04), doneAction: 2
        );
        var signal = Mix(bands * weights) / modeCount.sqrt;
        signal = HPF.ar(LeakDC.ar(signal), 28);
        signal = performanceFx.(
            signal, fundamental, ringMix, ringHarmonic,
            fuzzMix, fuzzDrive, fuzzBias, fuzzTone
        );
        Out.ar(out, Limiter.ar(PanAz.ar(
            8,
            signal * envelope * magnitude.clip(0, 2).sqrt
            * (0.72 + (localEnergy.clip(0, 2) * 0.18))
            * strikeGain * master,
            azimuth, 1, 2
        ), 0.86));
    }).add;

    SynthDef(\qrmBoundaryStrike16V1, { |out=0, fundamental=72, master=0.16,
        strikeGain=0.45, magnitude=0.1, phase=0, pan=0, azimuth=0, decay=0.09,
        coherence=0, localEnergy=0, persistence=1,
        fieldDepth=1, momentumDepth=0.55,
        ringMix=0, ringHarmonic=2, fuzzMix=0, fuzzDrive=8, fuzzBias=0.12,
        fuzzTone=5200|
        var ratios = NamedControl.kr(\frequencyRatios, Array.fill(modeCount, 1.0));
        var weights = NamedControl.kr(\modalWeights, Array.fill(modeCount, 0.0));
        var modalDecaySeconds = NamedControl.kr(
            \modalDecaySeconds, Array.fill(modeCount, 0.28)
        );
        var frequencies = (fundamental * ratios).clip(28, 16000);
        var excitation = Decay2.ar(Impulse.ar(0), 0.0007, 0.005) * 0.25;
        var fieldControl = (phase.sin * fieldDepth).tanh;
        var momentumControl = (
            phase.cos.sign * (magnitude * 6).tanh * momentumDepth
        ).tanh;
        var frequencyBend = 1 + (fieldControl * 0.012) + (momentumControl * 0.018);
        var bands = Ringz.ar(
            excitation, (frequencies * frequencyBend).clip(28, 16000), modalDecaySeconds
        );
        var envelope = EnvGen.kr(
            Env.linen(0, decay.clip(0.02, 4.0) * 1.35, 0.04), doneAction: 2
        );
        var modeSignals = bands * weights;
        var signal = Mix.fill(modeCount, { |index|
            PanAz.ar(
                16, modeSignals[index],
                (index.linlin(0, modeCount - 1, -1, 1) + azimuth).wrap(-1, 1),
                1, 2
            )
        }) / modeCount.sqrt;
        signal = performanceFx.(
            HPF.ar(LeakDC.ar(signal), 28), fundamental,
            ringMix, ringHarmonic, fuzzMix, fuzzDrive, fuzzBias, fuzzTone
        );
        Out.ar(out, Limiter.ar(
            signal * envelope * magnitude.clip(0, 2).sqrt
            * (0.72 + (localEnergy.clip(0, 2) * 0.18))
            * strikeGain * master,
            0.86
        ));
    }).add;
};

~qrmSetAudioStatus = { |message, color|
    {
        ~qrmAudioStatus !? { |view|
            view.string_(message);
            color !? { view.stringColor_(color) };
        };
    }.defer;
};

~qrmBuildAudio = {
    ~qrmAudioReady = false;
    ~qrmDefineSynths.value;
    s.sync;
    ~qrmBodySynthName = case
    { ~qrmOutputChannels >= 16 } { \qrmMembraneBody16V1 }
    { ~qrmOutputChannels >= 8 } { \qrmMembraneBody8V1 }
    { \qrmMembraneBodyV1 };
    ~qrmStrikeSynthName = case
    { ~qrmOutputChannels >= 16 } { \qrmBoundaryStrike16V1 }
    { ~qrmOutputChannels >= 8 } { \qrmBoundaryStrike8V1 }
    { \qrmBoundaryStrikeV1 };
    // Use an immediate bundle here. Server.bind applies the server latency;
    // a following /sync can otherwise complete before the future-dated node
    // bundle, letting the 30 Hz observer address a node that is not live yet.
    s.makeBundle(nil, {
        ~qrmBody = Synth(~qrmBodySynthName, [
            \fundamental, ~qrmFundamental,
            \master, 0.0,
            \bodyEnabled, if((~qriBodyMode ? 1) == 0, { 0 }, { 1 }),
            // The integrated Field body has its own explicit owner.  Before
            // that layer loads, retain the standalone membrane behaviour.
            \fieldGain, ~qriFieldGain ? 1.0,
            \motionGain, ~qrmMotionGain,
            \response, ~qrmBodyResponse,
            \harmonicMix, ~qrmHarmonicMix,
            \pulseDepth, ~qrmPulseDepth,
            \pulseLevel, ~qrmPulseLevel,
            \pulseAttack, ~qrmPulseAttack,
            \pulseDecay, ~qrmPulseDecay,
            \pulseRelease, ~qrmPulseRelease,
            \dynamicDetunes, ~qrmPulseDetunes,
            \dynamicBrightness, ~qrmPulseBrightness,
            \dynamicDecayScales, ~qrmPulseDecayScales,
            \dynamicDrives, ~qrmPulseDrives,
            \ringMix, ~qrmRingMix,
            \ringHarmonic, ~qrmRingHarmonic,
            \fuzzMix, ~qrmFuzzMix,
            \fuzzDrive, ~qrmFuzzDrive,
            \fuzzBias, ~qrmFuzzBias,
            \fuzzTone, ~qrmFuzzTone,
            \pulseRates, ~qrmPulseRates,
            \pulseActivities, ~qrmPulseActivities,
            \pulseDecayScales, ~qrmPulseDecayScales,
            \modalDecaySeconds, ~qrmModalDecaySeconds,
            \pulseBrightness, ~qrmPulseBrightness,
            \pulseDetunes, ~qrmPulseDetunes,
            \pulseDrives, ~qrmPulseDrives,
            \frequencyRatios, ~qrmPitchRatios
        ]);
        ~qrmStrikeGroup = Group.after(~qrmBody);
    });
    s.sync;
    ~qrmPushModeMix.value;
    ~qrmAudioReady = true;
    // Optional integrated event layer owns its own SynthDefs/control bus and
    // must be rebuilt after an output-device server reboot as well.
    ~qriRebuildAudioLayer !? { ~qriRebuildAudioLayer.value };
    ~qrmSetAudioStatus.(
        "ACTIVE  %  /  % discrete output buses  /  sound locked"
        .format(~qrmSelectedOutputDevice ? "system default", ~qrmOutputChannels),
        Color.fromHexString("80ed99")
    );
    "Quantum Resonant Membrane v1 %ch audio graph ready"
        .format(~qrmOutputChannels).postln;
};

~qrmResolveAbletonBridge = { |outputChannels=2|
    var candidates = ServerOptions.outDevices.select { |device|
        var name = device.asString.toLower;
        name.contains("blackhole") or: {
            name.contains("loopback") or: {
                name.contains("vb-cable") or: { name.contains("soundflower") }
            }
        }
    };
    if(outputChannels >= 8, {
        candidates.detect { |device|
            var name = device.asString.toLower;
            name.contains("2ch").not and: {
                name.contains("8ch") or: {
                    name.contains("16ch") or: { name.contains("64ch") }
                }
            }
        } ? candidates.detect { |device|
            device.asString.toLower.contains("2ch").not
        }
    }, {
        candidates.detect { |device| device.asString.toLower.contains("2ch") }
        ? candidates.first
    })
};

~qrmRefreshAudioDevices = { |requestedChannels|
    var outputChannels = requestedChannels ? ~qrmOutputChannels;
    var bridge = ~qrmResolveAbletonBridge.(outputChannels);
    var detected = ServerOptions.outDevices;
    var current = ~qrmSelectedOutputDevice;
    var selectedIndex;
    ~qrmAudioDeviceMenu !? { |menu|
        if(menu.value.notNil and: { ~qrmAudioDeviceValues.size > menu.value }) {
            current = ~qrmAudioDeviceValues[menu.value]
        };
    };
    ~qrmAudioDeviceValues = [nil, \qrmAbletonBridge] ++ detected;
    ~qrmAudioDeviceItems = [
        "system default",
        if(bridge.notNil, {
            "Ableton bridge  /  %".format(bridge)
        }, {
            "Ableton bridge  /  install BlackHole, Loopback, or VB-Cable"
        })
    ] ++ detected;
    ~qrmAudioDeviceMenu !? { |menu|
        menu.items_(~qrmAudioDeviceItems);
        selectedIndex = ~qrmAudioDeviceValues.indexOfEqual(current);
        menu.value_(selectedIndex ? 0);
    };
};

~qrmApplyAudioOutput = { |device, outputChannels=2|
    var configureAndReload, selectedDevice, name, invalidTwoChannelDevice;
    outputChannels = case
    { outputChannels.asInteger >= 16 } { 16 }
    { outputChannels.asInteger >= 8 } { 8 }
    { 2 };
    selectedDevice = if(device == \qrmAbletonBridge, {
        ~qrmResolveAbletonBridge.(outputChannels)
    }, {
        device
    });
    name = if(selectedDevice.isNil, { nil }, { selectedDevice.asString.toLower });
    invalidTwoChannelDevice = (outputChannels >= 8) and: {
        name.notNil and: { name.contains("2ch") }
    };
    if(selectedDevice.isNil and: { device == \qrmAbletonBridge }, {
        ~qrmSetAudioStatus.(
            if(outputChannels >= 8, {
                "%ch bridge needs BlackHole 16ch/64ch, Loopback, or another multichannel device"
                .format(outputChannels)
            }, {
                "Ableton bridge needs BlackHole, Loopback, VB-Cable, or Soundflower"
            }),
            Color.fromHexString("ffd166")
        );
    }, {
        if(invalidTwoChannelDevice, {
            ~qrmSetAudioStatus.(
                "BlackHole 2ch cannot carry % discrete buses; choose stereo or a multichannel bridge"
                .format(outputChannels),
                Color.fromHexString("ff7a8a")
            );
        }, {
            ~qrmAudioReady = false;
            ~qrmSonify = false;
            { ~qrmSoundButton !? { |button| button.value_(0) } }.defer;
            ~qrmSetAudioStatus.(
                "RESTARTING SUPERCOLLIDER AUDIO  /  backend state remains live",
                Color.fromHexString("ffd166")
            );
            configureAndReload = {
                s.options.outDevice = selectedDevice;
                s.options.numOutputBusChannels = outputChannels;
                ~qrmSelectedOutputDevice = selectedDevice;
                ~qrmOutputChannels = outputChannels;
                s.doWhenBooted({ ~qrmBuildAudio.value });
            };
            if(s.serverRunning, {
                s.reboot(configureAndReload, {
                    ~qrmSetAudioStatus.(
                        "AUDIO RESTART FAILED  /  inspect the SuperCollider post window",
                        Color.fromHexString("ff7a8a")
                    );
                });
            }, {
                configureAndReload.value;
                s.boot;
            });
        });
    });
};

~qrmServerQuitHandler !? { |handler| s.onQuitRemove(handler) };
~qrmServerQuitHandler = {
    ~qrmAudioReady = false;
    ~qrmStrikeNodes.clear;
    ~qrmBody = nil;
    ~qrmStrikeGroup = nil;
    ~qrmSetAudioStatus.(
        "AUDIO SERVER STOPPED  /  apply routing to restart",
        Color.fromHexString("ffd166")
    );
};
s.onQuitAdd(~qrmServerQuitHandler);

s.waitForBoot({ ~qrmBuildAudio.value });

~qrmAuditionModalPulse = {
    if(~qrmAudioReady) {
        Synth(\qrmModalPulseAuditionV1, [
            \fundamental, ~qrmFundamental,
            \pulseLevel, ~qrmPulseLevel,
            \pulseDepth, ~qrmPulseDepth,
            \pulseAttack, ~qrmPulseAttack,
            \pulseDecay, ~qrmPulseDecay,
            \pulseRelease, ~qrmPulseRelease,
            \ringMix, ~qrmRingMix,
            \ringHarmonic, ~qrmRingHarmonic,
            \fuzzMix, ~qrmFuzzMix,
            \fuzzDrive, ~qrmFuzzDrive,
            \fuzzBias, ~qrmFuzzBias,
            \fuzzTone, ~qrmFuzzTone
        ], ~qrmStrikeGroup ? s.defaultGroup, \addToTail);
    } {
        "QRM modal pulse audition unavailable: audio is not ready".warn;
    };
};

~qrmRenderCrossing = { |crossing, level=1.0|
    var magnitude = crossing[5].asFloat;
    var phase = crossing[6].asFloat;
    var contact = [crossing[8], crossing[9], crossing[10]].collect(_.asFloat);
    var weights = crossing.copyRange(13, 12 + modeCount).collect(_.asFloat);
    var node;
    ~qrmContact = contact;
    ~qrmCrossingFlash = 1.0;
    if((~qrmCrossingAudioEnabled ? true) and: { ~qrmSonify }
        and: { ~qrmAvailable and: { ~qrmAudioReady } }
        and: { Main.elapsedTime >= ~qrmSonicGateUntil }) {
        if(~qrmStrikeNodes.size >= ~qrmMaxStrikeVoices) {
            ~qrmStrikeNodes.removeAt(0).free;
        };
        node = Synth(~qrmStrikeSynthName, [
            \fundamental, ~qrmFundamental,
            \master, ~qrmMaster,
            \strikeGain, ~qrmStrikeGain,
            \decay, ~qrmEffectiveCrossingDecay.value,
            \magnitude, magnitude * level,
            \phase, phase,
            \coherence, (~qrmCoherence / 3).clip(0, 1),
            \localEnergy, ~qrmMembraneEnergy,
            \persistence, crossing[11].asFloat,
            \fieldDepth, ~qrmFieldTimbreDepth,
            \momentumDepth, ~qrmMomentumTimbreDepth,
            \pan, contact[0].clip(-1, 1),
            \azimuth, contact[1].atan2(contact[0]) / pi,
            \ringMix, ~qrmRingMix,
            \ringHarmonic, ~qrmRingHarmonic,
            \fuzzMix, ~qrmFuzzMix,
            \fuzzDrive, ~qrmFuzzDrive,
            \fuzzBias, ~qrmFuzzBias,
            \fuzzTone, ~qrmFuzzTone,
            \frequencyRatios, ~qrmPitchRatios,
            \modalDecaySeconds, ~qrmModalDecaySeconds,
            \modalWeights, weights * ~qrmModeAudioWeights.()
        ], ~qrmStrikeGroup, \addToTail);
        ~qrmStrikeNodes.add(node);
        node.onFree({
            ~qrmStrikeNodes.remove(node);
        });
    };
};

~qrmRouteCrossing = { |crossing|
    ~qrmLatestCrossing = crossing.copy;
    if(~qrmTimeMode == 0) { ~qrmRenderCrossing.(crossing) };
};

~qrmRouteBuresPulse = { |geodesic=false|
    var step, hit, delays, generation;
    if(~qrmLatestCrossing.notNil) {
        case
        { (~qrmTimeMode == 1) and: { geodesic.not } } {
            ~qrmRenderCrossing.(~qrmLatestCrossing)
        }
        { (~qrmTimeMode == 4) and: { geodesic.not } } {
            step = ~qrmQuantumEuclideanStep % ~qrmEuclideanSteps;
            hit = ~qrmEuclideanMask[step];
            ~qrmQuantumEuclideanStep = ~qrmQuantumEuclideanStep + 1;
            if(hit > 0) { ~qrmRenderCrossing.(~qrmLatestCrossing) };
        }
        { (~qrmTimeMode == 5) and: { geodesic } } {
            ~qrmRenderCrossing.(~qrmLatestCrossing)
        }
        { (~qrmTimeMode == 6) and: { geodesic.not } } {
            generation = ~qrmSonicGeneration;
            delays = [0, 0.125, 0.25, 0.5].copyRange(0, ~qrmRecursiveDepth)
                / (~qrmFixedRate * ~qrmClockScale).max(0.01);
            delays.do { |delay, index|
                SystemClock.sched(delay, {
                    if(generation == ~qrmSonicGeneration) {
                        ~qrmRenderCrossing.(
                            ~qrmLatestCrossing, 1 / (index + 1).sqrt
                        );
                    };
                    nil
                });
            };
        };
    };
};

~qrmTimeClock = Routine({
    loop {
        if([2, 3].includes(~qrmTimeMode) and: { ~qrmLatestCrossing.notNil }) {
            var hit = 1;
            if(~qrmTimeMode == 3) {
                hit = ~qrmEuclideanMask[~qrmEuclideanStep % ~qrmEuclideanSteps];
                ~qrmEuclideanStep = ~qrmEuclideanStep + 1;
            };
            if(hit > 0) { ~qrmRenderCrossing.(~qrmLatestCrossing) };
        };
        (1 / (~qrmFixedRate * ~qrmClockScale).max(0.01)).wait;
    };
}).play(AppClock);

OSCdef(\qrmFrameBeginV1, { |message|
    ~qrmStageRevision = message[1].asInteger;
    ~qrmStageCompatible = (message[3].asString == "qmw.quantum_resonant_membrane.osc.v1")
        and: { message[4].asInteger == 4 }
        and: { message[5].asInteger == modeCount }
        and: { message[6].asString == "quantum_probability_unitary" };
    ~qrmStageResetEpoch = if(message.size > 7) {
        message[7].asInteger
    } {
        ~qrmResetEpoch
    };
    ~qrmStagePopulations = ~qrmPopulations.copy;
    ~qrmStageRhoReal = ~qrmRhoReal.copy;
    ~qrmStageRhoImag = ~qrmRhoImag.copy;
    ~qrmStageQ = ~qrmQ.copy;
    ~qrmStageQdot = ~qrmQdot.copy;
    ~qrmStageModes = ~qrmModes.copy;
    ~qrmStageRawModes = ~qrmRawModes.copy;
    ~qrmStageModeVelocities = ~qrmModeVelocities.copy;
    ~qrmStageRatios = ~qrmRatios.copy;
    ~qrmStageInterferenceTimbreGains = ~qrmInterferenceTimbreGains.copy;
    ~qrmStageInterferenceTimbreOutputAmplitudes = ~qrmInterferenceTimbreOutputAmplitudes.copy;
    ~qrmStageInterferenceTimbreSlew = ~qrmInterferenceTimbreSlew;
    ~qrmStageInterferenceTimbrePhase = ~qrmInterferenceTimbrePhase;
    ~qrmStageInterferenceTimbreSpread = ~qrmInterferenceTimbreSpread;
    ~qrmStageInterferenceTimbreDepth = ~qrmInterferenceTimbreDepth;
    ~qrmStageInterferenceTimbreSource = ~qrmInterferenceTimbreSource;
    ~qrmStageInterferenceTimbreCancellation = ~qrmInterferenceTimbreCancellation;
    ~qrmStageInterferenceTimbreValid = false;
    ~qrmStageFlux = ~qrmFlux.copy;
    ~qrmStagePreparationMode = ~qrmPreparationMode;
    ~qrmStagePreparationSemantics = ~qrmPreparationSemantics;
    ~qrmStageFieldOffsets = ~qrmFieldOffsets.copy;
    ~qrmStageFieldSusceptibility = ~qrmFieldSusceptibility.copy;
    ~qrmStageFieldMaxOffset = ~qrmFieldMaxOffset;
    ~qrmStageFieldMeanSusceptibility = ~qrmFieldMeanSusceptibility;
    ~qrmStageFieldMinQ = ~qrmFieldMinQ;
    ~qrmStageFieldMaxQ = ~qrmFieldMaxQ;
    ~qrmStageFieldMaxCoupling = ~qrmFieldMaxCoupling;
    ~qrmStageEventProbability = 0.0;
    ~qrmStageEventCount = 0;
    ~qrmStageEventThreshold = ~qrmEventThreshold;
    ~qrmStageEventAccumulatorFill = ~qrmEventAccumulatorFill;
    ~qrmStageInjectedEnergy = 0.0;
    ~qrmStageCrossings = List.new;
    ~qrmStageTerrainOmega = ~qrmTerrainOmega;
    ~qrmStageTerrainStabilityDt = ~qrmTerrainStabilityDt;
    ~qrmStageTerrainSubsteps = ~qrmTerrainSubsteps;
    ~qrmStageMembraneOmega = ~qrmMembraneOmega;
    ~qrmStageMembraneStabilityDt = ~qrmMembraneStabilityDt;
    ~qrmStageMembraneSubsteps = ~qrmMembraneSubsteps;
    ~qrmStageHamiltonianSpan = ~qrmHamiltonianSpan;
    ~qrmStageDensitySubsteps = ~qrmDensitySubsteps;
    ~qrmStageBuresDelta = ~qrmBuresDelta;
    ~qrmStageBuresLength = ~qrmBuresLength;
    ~qrmStageBuresRemainder = ~qrmBuresRemainder;
    ~qrmStageBuresPulses = 0;
    ~qrmStageBuresRecordIndex = ~qrmBuresRecordIndex;
    ~qrmStageBuresWeightedTime = ~qrmBuresWeightedTime;
    ~qrmStageBuresGeodesicRemainder = ~qrmBuresGeodesicRemainder;
    ~qrmStageBuresGeodesicPulses = 0;
    ~qrmStageBuresGeodesicRecordIndex = ~qrmBuresGeodesicRecordIndex;
    ~qrmStageBuresChord = ~qrmBuresChord;
    ~qrmStageBuresTriangleDefect = ~qrmBuresTriangleDefect;
    ~qrmStageBuresNormalizedBending = ~qrmBuresNormalizedBending;
}, root ++ "/frame/begin", recvPort: dataPort);

OSCdef(\qrmAvailableV1, { |message|
    if(message[2].asInteger == 0) { ~qrmAvailable = false };
}, root ++ "/available", recvPort: dataPort);

OSCdef(\qrmDensityGlobalV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStagePurity = message[2].asFloat;
        ~qrmStageEntropy = message[3].asFloat;
        ~qrmStageCoherence = message[4].asFloat;
        ~qrmStageHamiltonianSpan = message[8].asFloat;
        ~qrmStageDensitySubsteps = message[9].asInteger;
    };
}, root ++ "/density/global", recvPort: dataPort);

OSCdef(\qrmDensityPreparationV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStagePreparationMode = message[2].asString;
        ~qrmStagePreparationSemantics = message[3].asString;
    };
}, root ++ "/density/preparation", recvPort: dataPort);

OSCdef(\qrmBuresTemporalGlobalV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageBuresDelta = message[3].asFloat;
        ~qrmStageBuresLength = message[4].asFloat;
        ~qrmStageBuresRemainder = message[5].asFloat;
        ~qrmStageBuresPulses = message[6].asInteger;
        ~qrmStageBuresRecordIndex = message[7].asInteger;
        ~qrmStageBuresWeightedTime = message[8].asFloat;
        ~qrmStageBuresGeodesicRemainder = message[9].asFloat;
        ~qrmStageBuresGeodesicPulses = message[10].asInteger;
        ~qrmStageBuresGeodesicRecordIndex = message[11].asInteger;
        ~qrmStageBuresChord = message[12].asFloat;
        ~qrmStageBuresTriangleDefect = message[13].asFloat;
        ~qrmStageBuresNormalizedBending = message[14].asFloat;
        ~qrmClockScale = message[16].asFloat;
        ~qrmBuresDistance = message[17].asFloat;
        ~qrmGeodesicBendingDepth = message[18].asFloat;
    };
}, root ++ "/temporal/global", recvPort: dataPort);

OSCdef(\qrmFieldGlobalV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageFieldMaxOffset = message[3].asFloat;
        ~qrmStageFieldMeanSusceptibility = message[4].asFloat;
        ~qrmStageFieldMinQ = message[5].asFloat;
        ~qrmStageFieldMaxQ = message[6].asFloat;
        ~qrmStageFieldMaxCoupling = message[7].asFloat;
    };
}, root ++ "/field/global", recvPort: dataPort);

OSCdef(\qrmFieldOffsetsV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageFieldOffsets = message.copyRange(2, 1 + modeCount).collect(_.asFloat);
    };
}, root ++ "/field/frequency_offsets", recvPort: dataPort);

OSCdef(\qrmFieldSusceptibilityV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageFieldSusceptibility = message.copyRange(2, 1 + modeCount).collect(_.asFloat);
    };
}, root ++ "/field/susceptibility", recvPort: dataPort);

OSCdef(\qrmEventGlobalV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageEventCount = message[3].asInteger;
        ~qrmStageEventProbability = message[4].asFloat;
        if(message.size > 5) { ~qrmStageEventThreshold = message[5].asFloat };
        if(message.size > 6) {
            ~qrmStageEventAccumulatorFill = message[6].asFloat
        };
    };
}, root ++ "/event/global", recvPort: dataPort);

// Downstream composition controls. M numbers are one-based to match the GUI.
// These alter only the SuperCollider mixer and never write into rho.
OSCdef(\qrmModeGainControlV1, { |message|
    var lane = message[1].asInteger - 1;
    var gain = message[2].asFloat;
    {
        ~qrmSetModeGain.(lane, gain);
        ~qrmModeGainView.value_(~qrmModeGains / 2);
    }.defer;
}, root ++ "/mixer/mode_gain", recvPort: dataPort);

OSCdef(\qrmModeCombinationControlV1, { |message|
    var gains = message.copyRange(1, message.size - 1).collect(_.asFloat);
    { ~qrmSetModeCombination.(gains) }.defer;
}, root ++ "/mixer/mode_gains", recvPort: dataPort);

OSCdef(\qrmPopulationsV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStagePopulations = message.copyRange(2, 5).collect(_.asFloat);
    };
}, root ++ "/density/populations", recvPort: dataPort);

OSCdef(\qrmRhoRealV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageRhoReal = message.copyRange(2, 17).collect(_.asFloat);
    };
}, root ++ "/density/rho_real", recvPort: dataPort);

OSCdef(\qrmRhoImagV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageRhoImag = message.copyRange(2, 17).collect(_.asFloat);
    };
}, root ++ "/density/rho_imag", recvPort: dataPort);

OSCdef(\qrmTerrainQV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageQ = message.copyRange(2, 5).collect(_.asFloat);
    };
}, root ++ "/terrain/q", recvPort: dataPort);

OSCdef(\qrmTerrainQdotV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageQdot = message.copyRange(2, 5).collect(_.asFloat);
    };
}, root ++ "/terrain/qdot", recvPort: dataPort);

OSCdef(\qrmTerrainGlobalV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageTerrainL = message[2].asFloat;
        ~qrmStageTerrainOmega = message[5].asFloat;
        ~qrmStageTerrainStabilityDt = message[6].asFloat;
        ~qrmStageTerrainSubsteps = message[7].asInteger;
    };
}, root ++ "/terrain/global", recvPort: dataPort);

OSCdef(\qrmFlowGlobalV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageMaxCurrent = message[2].asFloat;
        ~qrmStageTransport = message[3].asFloat;
    };
}, root ++ "/flow/global", recvPort: dataPort);

OSCdef(\qrmRegionFluxV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageFlux = message.copyRange(2, 5).collect(_.asFloat);
    };
}, root ++ "/flow/region", recvPort: dataPort);

OSCdef(\qrmModesV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageModes = message.copyRange(2, 1 + modeCount).collect(_.asFloat);
    };
}, root ++ "/membrane/modes", recvPort: dataPort);

OSCdef(\qrmRawModesV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageRawModes = message.copyRange(2, 1 + modeCount).collect(_.asFloat);
    };
}, root ++ "/membrane/raw_modes", recvPort: dataPort);

OSCdef(\qrmModeVelocitiesV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageModeVelocities = message.copyRange(2, 1 + modeCount).collect(_.asFloat);
    };
}, root ++ "/membrane/velocities", recvPort: dataPort);

OSCdef(\qrmRatiosV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageRatios = message.copyRange(2, 1 + modeCount).collect(_.asFloat);
    };
}, root ++ "/membrane/frequency_ratios", recvPort: dataPort);

// The interference metadata and gain vector are optional for backward
// compatibility, but a gain vector is committed only inside its matching QRM
// frame.  No free-running OSC message can partially replace the active timbre.
OSCdef(\qrmInterferenceTimbreMetaV1, { |message|
    var revision = message[1].asInteger;
    if((revision == ~qrmStageRevision) and: { message.size >= 12 }) {
        ~qrmStageInterferenceTimbrePhase = message[3].asFloat;
        ~qrmStageInterferenceTimbreSpread = message[4].asFloat;
        ~qrmStageInterferenceTimbreDepth = message[5].asFloat.clip(0, 1);
        ~qrmStageInterferenceTimbreSlew = message[6].asFloat.clip(0, 10);
        ~qrmStageInterferenceTimbreSource = message[7].asString;
        ~qrmStageInterferenceTimbreCancellation = message[8].asInteger != 0;
    };
}, root ++ "/timbre/interference", recvPort: dataPort);

OSCdef(\qrmInterferenceTimbreGainsV1, { |message|
    var revision = message[1].asInteger;
    var gains;
    if((revision == ~qrmStageRevision) and: { message.size == (modeCount + 2) }) {
        gains = message.copyRange(2, 1 + modeCount).collect(_.asFloat);
        if(gains.every { |gain| gain.isNaN.not and: { gain != inf }
            and: { gain != -inf } and: { gain >= 0 } }) {
            ~qrmStageInterferenceTimbreGains = gains;
            ~qrmStageInterferenceTimbreValid = true;
        };
    };
}, root ++ "/timbre/gain_factors", recvPort: dataPort);

OSCdef(\qrmInterferenceTimbreOutputV1, { |message|
    var revision = message[1].asInteger;
    if((revision == ~qrmStageRevision) and: { message.size == (modeCount + 2) }) {
        ~qrmStageInterferenceTimbreOutputAmplitudes = message
            .copyRange(2, 1 + modeCount).collect(_.asFloat);
    };
}, root ++ "/timbre/output_amplitudes", recvPort: dataPort);

OSCdef(\qrmMembraneGlobalV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageMembraneEnergy = message[5].asFloat;
        ~qrmStageMembraneOmega = message[6].asFloat;
        ~qrmStageMembraneStabilityDt = message[7].asFloat;
        ~qrmStageMembraneSubsteps = message[8].asInteger;
        if(message.size > 10) { ~qrmStageInjectedEnergy = message[10].asFloat };
    };
}, root ++ "/membrane/global", recvPort: dataPort);

OSCdef(\qrmCrossingV1, { |message|
    if(message[1].asInteger == ~qrmStageRevision) {
        ~qrmStageCrossings.add(message.copy);
    };
}, root ++ "/crossing", recvPort: dataPort);

OSCdef(\qrmFrameEndV1, { |message|
    var revision = message[1].asInteger;
    var resetFrame;
    if(revision == ~qrmStageRevision) {
        resetFrame = ~qrmStageResetEpoch != ~qrmResetEpoch;
        if(resetFrame) {
            ~qrmResetEpoch = ~qrmStageResetEpoch;
            ~qrmSonicReset.value;
        };
        ~qrmRevision = revision;
        ~qrmCompatible = ~qrmStageCompatible;
        ~qrmAvailable = ~qrmCompatible;
        ~qrmLastFrameAt = Main.elapsedTime;
        ~qrmPopulations = ~qrmStagePopulations;
        ~qrmRhoReal = ~qrmStageRhoReal;
        ~qrmRhoImag = ~qrmStageRhoImag;
        ~qrmQ = ~qrmStageQ;
        ~qrmQdot = ~qrmStageQdot;
        ~qrmModes = ~qrmStageModes;
        ~qrmRawModes = ~qrmStageRawModes;
        ~qrmModeVelocities = ~qrmStageModeVelocities;
        ~qrmRatios = ~qrmStageRatios;
        if(~qrmStageInterferenceTimbreValid) {
            ~qrmInterferenceTimbreGains = ~qrmStageInterferenceTimbreGains;
            ~qrmInterferenceTimbreOutputAmplitudes =
                ~qrmStageInterferenceTimbreOutputAmplitudes;
            ~qrmInterferenceTimbreSlew = ~qrmStageInterferenceTimbreSlew;
            ~qrmInterferenceTimbrePhase = ~qrmStageInterferenceTimbrePhase;
            ~qrmInterferenceTimbreSpread = ~qrmStageInterferenceTimbreSpread;
            ~qrmInterferenceTimbreDepth = ~qrmStageInterferenceTimbreDepth;
            ~qrmInterferenceTimbreSource = ~qrmStageInterferenceTimbreSource;
            ~qrmInterferenceTimbreCancellation =
                ~qrmStageInterferenceTimbreCancellation;
            ~qrmInterferenceTimbreUpdated !? { |function| function.value };
        };
        ~qrmFlux = ~qrmStageFlux;
        ~qrmPreparationMode = ~qrmStagePreparationMode;
        ~qrmPreparationSemantics = ~qrmStagePreparationSemantics;
        ~qrmFieldOffsets = ~qrmStageFieldOffsets;
        ~qrmFieldSusceptibility = ~qrmStageFieldSusceptibility;
        ~qrmFieldMaxOffset = ~qrmStageFieldMaxOffset;
        ~qrmFieldMeanSusceptibility = ~qrmStageFieldMeanSusceptibility;
        ~qrmFieldMinQ = ~qrmStageFieldMinQ;
        ~qrmFieldMaxQ = ~qrmStageFieldMaxQ;
        ~qrmFieldMaxCoupling = ~qrmStageFieldMaxCoupling;
        ~qrmEventProbability = ~qrmStageEventProbability;
        ~qrmEventCount = ~qrmStageEventCount;
        ~qrmEventThreshold = ~qrmStageEventThreshold;
        ~qrmEventAccumulatorFill = ~qrmStageEventAccumulatorFill;
        ~qrmInjectedEnergy = ~qrmStageInjectedEnergy;
        ~qrmPurity = ~qrmStagePurity ? ~qrmPurity;
        ~qrmEntropy = ~qrmStageEntropy ? ~qrmEntropy;
        ~qrmCoherence = ~qrmStageCoherence ? ~qrmCoherence;
        ~qrmHamiltonianSpan = ~qrmStageHamiltonianSpan ? ~qrmHamiltonianSpan;
        ~qrmDensitySubsteps = ~qrmStageDensitySubsteps ? ~qrmDensitySubsteps;
        ~qrmMaxCurrent = ~qrmStageMaxCurrent ? ~qrmMaxCurrent;
        ~qrmTransport = ~qrmStageTransport ? ~qrmTransport;
        ~qrmMembraneEnergy = ~qrmStageMembraneEnergy ? ~qrmMembraneEnergy;
        ~qrmTerrainL = ~qrmStageTerrainL ? ~qrmTerrainL;
        ~qrmTerrainOmega = ~qrmStageTerrainOmega ? ~qrmTerrainOmega;
        ~qrmTerrainStabilityDt = ~qrmStageTerrainStabilityDt ? ~qrmTerrainStabilityDt;
        ~qrmTerrainSubsteps = ~qrmStageTerrainSubsteps ? ~qrmTerrainSubsteps;
        ~qrmMembraneOmega = ~qrmStageMembraneOmega ? ~qrmMembraneOmega;
        ~qrmMembraneStabilityDt = ~qrmStageMembraneStabilityDt ? ~qrmMembraneStabilityDt;
        ~qrmMembraneSubsteps = ~qrmStageMembraneSubsteps ? ~qrmMembraneSubsteps;
        ~qrmBuresDelta = ~qrmStageBuresDelta;
        ~qrmBuresLength = ~qrmStageBuresLength;
        ~qrmBuresRemainder = ~qrmStageBuresRemainder;
        ~qrmBuresPulses = ~qrmStageBuresPulses;
        ~qrmBuresRecordIndex = ~qrmStageBuresRecordIndex;
        ~qrmBuresWeightedTime = ~qrmStageBuresWeightedTime;
        ~qrmBuresGeodesicRemainder = ~qrmStageBuresGeodesicRemainder;
        ~qrmBuresGeodesicPulses = ~qrmStageBuresGeodesicPulses;
        ~qrmBuresGeodesicRecordIndex = ~qrmStageBuresGeodesicRecordIndex;
        ~qrmBuresChord = ~qrmStageBuresChord;
        ~qrmBuresTriangleDefect = ~qrmStageBuresTriangleDefect;
        ~qrmBuresNormalizedBending = ~qrmStageBuresNormalizedBending;
        // Absolute activity is intentionally not normalized by the loudest
        // mode: unlike the previous implementation, low- and high-energy
        // frames now produce genuinely different rhythmic densities.
        ~qrmPulseActivities = Array.fill(modeCount, { |index|
            ((~qrmRawModes[index].abs * 0.45)
                + (~qrmModeVelocities[index].abs * 0.85)
                + (~qrmFieldOffsets[index].abs * 0.8)).clip(0, 1)
        });
        ~qrmUpdateDynamicAdapters.value;
        if(~qrmAudioReady and: { ~qrmBody.notNil } and: { resetFrame.not }) {
            ~qrmUpdatePitchRatios.value;
            ~qrmBody.setn(\pulseActivities, ~qrmPulseActivities);
            ~qrmPushModeMix.value;
            ~qrmBody.set(
                \fundamental, ~qrmFundamental,
                \motionGain, ~qrmMotionGain,
                \harmonicMix, ~qrmHarmonicMix,
                \master, if(~qrmSonify and: { ~qrmAvailable }
                    and: { Main.elapsedTime >= ~qrmSonicGateUntil }) { ~qrmMaster } { 0.0 }
            );
        };
        if(resetFrame.not) {
            ~qrmStageCrossings.do { |crossing, index|
                if(index < ~qrmMaxCrossingsPerFrame) { ~qrmRouteCrossing.(crossing) };
            };
            ~qrmBuresPulses.clip(0, 8).do {
                ~qrmRouteBuresPulse.(false)
            };
            ~qrmBuresGeodesicPulses.clip(0, 8).do {
                ~qrmRouteBuresPulse.(true)
            };
        };
    };
}, root ++ "/frame/end", recvPort: dataPort);

~qrmOpenAudioRouting = {
    var deviceLabel, layoutLabel, refreshButton, applyButton, explanation;
    ~qrmRoutingWindow !? _.close;
    ~qrmRoutingWindow = Window(
        "QRM Audio Routing  /  Core Audio + Ableton",
        Rect(170, 130, 620, 382)
    );
    ~qrmRoutingWindow.background = Color.fromHexString("11151c");
    StaticText(~qrmRoutingWindow, Rect(22, 16, 576, 28))
        .string_("SOUND DEVICE + OUTPUT LAYOUT")
        .font_(Font("Helvetica Neue", 18, true))
        .stringColor_(Color.fromHexString("dcecff"));
    deviceLabel = StaticText(~qrmRoutingWindow, Rect(22, 58, 130, 20))
        .string_("CORE AUDIO DEVICE")
        .font_(Font("Helvetica Neue", 10, true))
        .stringColor_(Color.fromHexString("8ecae6"));
    ~qrmAudioDeviceMenu = styleMenu.(
        PopUpMenu(~qrmRoutingWindow, Rect(22, 80, 454, 28))
    );
    refreshButton = Button(~qrmRoutingWindow, Rect(486, 80, 112, 28))
        .states_([["REFRESH"]])
        .action_({
            ~qrmRefreshAudioDevices.([
                2, 8, 16
            ][~qrmOutputLayoutMenu.value ? 0])
        });
    layoutLabel = StaticText(~qrmRoutingWindow, Rect(22, 122, 130, 20))
        .string_("OUTPUT GRAPH")
        .font_(Font("Helvetica Neue", 10, true))
        .stringColor_(Color.fromHexString("8ecae6"));
    ~qrmOutputLayoutMenu = PopUpMenu(~qrmRoutingWindow, Rect(22, 144, 276, 28))
        .items_([
            "STEREO  /  outputs 1-2",
            "8 DISCRETE CHANNELS  /  outputs 1-8",
            "16 TRANSDUCERS  /  outputs 1-16"
        ])
        .value_(case
            { ~qrmOutputChannels >= 16 } { 2 }
            { ~qrmOutputChannels >= 8 } { 1 }
            { 0 })
        .action_({ |menu| ~qrmRefreshAudioDevices.([2, 8, 16][menu.value]) });
    styleMenu.(~qrmOutputLayoutMenu);
    applyButton = Button(~qrmRoutingWindow, Rect(308, 144, 290, 28))
        .states_([["APPLY + REBOOT AUDIO GRAPH"]])
        .action_({
            ~qrmApplyAudioOutput.(
                ~qrmAudioDeviceValues[~qrmAudioDeviceMenu.value ? 0],
                [2, 8, 16][~qrmOutputLayoutMenu.value ? 0]
            )
        });
    ~qrmAudioStatus = StaticText(~qrmRoutingWindow, Rect(22, 187, 576, 42))
        .string_(
            "ACTIVE  %  /  % discrete output buses"
            .format(~qrmSelectedOutputDevice ? "system default", ~qrmOutputChannels)
        )
        .font_(Font("Menlo", 10, true))
        .stringColor_(Color.fromHexString("80ed99"));
    if(~qriTogglePerformanceRecording.notNil, {
        ~qriAudioRecordButton = Button(~qrmRoutingWindow, Rect(22, 237, 250, 32))
            .states_([
                ["RECORD WAV + MUSICXML", Color.black, Color.red(0.78)],
                ["STOP + WRITE WAV + XML", Color.white, Color.red(0.34)]
            ])
            .value_(if(~qriRecordingActive, { 1 }, { 0 }))
            .action_({ |button| ~qriTogglePerformanceRecording.value(button) });
        ~qriRecordingStatus = StaticText(~qrmRoutingWindow, Rect(284, 237, 314, 32))
            .string_("Stereo output WAV + admitted-event notation")
            .stringColor_(Color.fromHexString("ffcf70"));
    });
    explanation = StaticText(~qrmRoutingWindow, Rect(22, 279, 576, 84))
        .string_(
            "ABLETON: choose the bridge shortcut or BlackHole directly, then choose the same "
            ++ "device as Ableton's input. BlackHole 2ch supports stereo only; eight or sixteen "
            ++ "buses require BlackHole 16ch/64ch, Loopback, or another multichannel device. "
            ++ "Applying routing locks sound but does not reset rho, terrain, flow, or timing."
        )
        .font_(Font("Helvetica Neue", 11))
        .stringColor_(Color.fromHexString("a9c5dd"));
    ~qrmRoutingWindow.onClose = {
        ~qrmRoutingWindow = nil;
        ~qrmAudioDeviceMenu = nil;
        ~qrmOutputLayoutMenu = nil;
        ~qrmAudioStatus = nil;
        ~qriAudioRecordButton = nil;
        ~qriRecordingStatus = nil;
    };
    ~qrmRefreshAudioDevices.(~qrmOutputChannels);
    ~qrmRoutingWindow.front;
};

~qrmWindow = Window("Quantum Resonant Membrane v1", Rect(70, 35, 1120, 880));
~qrmWindow.background = Color.fromHexString("11151c");
~qrmTitle = StaticText(~qrmWindow, Rect(22, 14, 395, 32))
    .string_("QUANTUM RESONANT MEMBRANE  /  v1")
    .font_(Font("Helvetica Neue", 20, true)).stringColor_(Color.fromHexString("dcecff"));
~qrmPerformanceButton = Button(~qrmWindow, Rect(423, 18, 130, 24))
    .states_([["TIME + FX PRESETS"]])
    .action_({ ~qrmOpenPerformance.value });
~qrmAudioRoutingButton = Button(~qrmWindow, Rect(563, 18, 130, 24))
    .states_([["AUDIO 2/8/16"]])
    .action_({ ~qrmOpenAudioRouting.value });
~qrmInterferenceTimbreButton = Button(~qrmWindow, Rect(703, 18, 130, 24))
    .states_([["PHASE TIMBRE"]])
    .action_({ ~qrmOpenInterferenceTimbre !? { |function| function.value } });
~qrmStatus = StaticText(~qrmWindow, Rect(843, 18, 252, 24))
    .align_(\right).font_(Font("Helvetica Neue", 13, true))
    .stringColor_(Color.fromHexString("80ed99"));

~qrmSphere = UserView(~qrmWindow, Rect(22, 58, 500, 342));
~qrmSphere.background = Color.fromHexString("080b10");
~qrmSphere.drawFunc = { |view|
    var fields = ~qrmWaveHistory;
    var envelopes = ~qrmWaveEnvelopeHistory;
    var width = view.bounds.width;
    var height = view.bounds.height;
    var rows = fields.size;
    var scale = ~qrmWaveScale.max(1e-9);
    var project, surfaceValue, fillQuad, drawSurface, frontRow;
    var colors = [
        Color.fromHexString("5dd9ff"), Color.fromHexString("ff7ac6"),
        Color.fromHexString("ffd166"), Color.fromHexString("80ed99")
    ];
    Pen.stringAtPoint(
        "3D MODAL WAVEFIELD  /  raw motion + velocity envelope",
        12@10, Font("Helvetica Neue", 11, true), Color.white.alpha_(0.72)
    );
    Pen.stringAtPoint(
        "PINK top  /  GREEN field  /  BLUE bottom",
        12@27, Font("Helvetica Neue", 9, true), Color.white.alpha_(0.48)
    );
    if(rows == 0) {
        Pen.strokeColor = Color.grey(0.35, 0.55);
        Pen.width = 0.7;
        7.do { |row|
            var depth = row / 6;
            var left = width * (0.08 + (0.12 * (1 - depth)));
            var right = width * (0.92 - (0.12 * (1 - depth)));
            var y = height * (0.20 + (0.68 * depth));
            Pen.line(Point(left, y), Point(right, y)); Pen.stroke;
        };
        10.do { |lane|
            Pen.line(
                Point(lane.linlin(0, 9, width * 0.20, width * 0.80), height * 0.20),
                Point(lane.linlin(0, 9, width * 0.08, width * 0.92), height * 0.88)
            ); Pen.stroke;
        };
        Pen.stringAtPoint("waiting for committed membrane frames", 125@158,
            Font("Helvetica Neue", 12), Color.white.alpha_(0.5));
    };
    if(rows > 0) {
        if(rows == 1) {
            fields = [fields[0], fields[0]];
            envelopes = [envelopes[0], envelopes[0]];
            rows = 2;
        };
        project = { |row, mode, value, layer=0|
            var depth = row / (rows - 1).max(1);
            var left = width * (0.07 + (0.13 * (1 - depth)));
            var right = width * (0.93 - (0.13 * (1 - depth)));
            var baseline = height * (0.30 + (0.40 * depth))
                - (layer * height * 0.20);
            Point(
                mode.linlin(0, modeCount - 1, left, right),
                baseline - ((value / scale).clip(-1.35, 1.35) * height * 0.065)
            )
        };
        surfaceValue = { |row, mode, layer|
            fields[row][mode] + (layer * envelopes[row][mode])
        };
        fillQuad = { |points, color|
            Pen.fillColor = color;
            Pen.moveTo(points[0]);
            Pen.lineTo(points[1]);
            Pen.lineTo(points[2]);
            Pen.lineTo(points[3]);
            Pen.lineTo(points[0]);
            Pen.fill;
        };
        drawSurface = { |layer|
            var fillColor = case
            { layer == 1 } { Color(0.98, 0.16, 0.72, 0.22) }
            { layer == -1 } { Color(0.08, 0.82, 1.0, 0.22) }
            { Color(0.18, 0.95, 0.52, 0.28) };
            (rows - 1).do { |row|
                (modeCount - 1).do { |mode|
                    fillQuad.([
                        project.(row, mode, surfaceValue.(row, mode, layer), layer),
                        project.(row, mode + 1, surfaceValue.(row, mode + 1, layer), layer),
                        project.(row + 1, mode + 1, surfaceValue.(row + 1, mode + 1, layer), layer),
                        project.(row + 1, mode, surfaceValue.(row + 1, mode, layer), layer)
                    ], fillColor);
                };
            };
            Pen.strokeColor = case
            { layer == 1 } { Color(1.0, 0.38, 0.84, 0.82) }
            { layer == -1 } { Color(0.20, 0.88, 1.0, 0.82) }
            { Color(0.45, 1.0, 0.66, 0.84) };
            Pen.width = if(layer == 0, { 0.75 }, { 1.25 });
            rows.do { |row|
                if((layer == 0) or: { (row % 3) == 0 }) {
                    modeCount.do { |mode|
                        var point = project.(row, mode, surfaceValue.(row, mode, layer), layer);
                        if(mode == 0, { Pen.moveTo(point) }, { Pen.lineTo(point) });
                    };
                    Pen.stroke;
                };
            };
            modeCount.do { |mode|
                rows.do { |row|
                    var point = project.(row, mode, surfaceValue.(row, mode, layer), layer);
                    if(row == 0, { Pen.moveTo(point) }, { Pen.lineTo(point) });
                };
                Pen.stroke;
            };
        };
        drawSurface.(-1);
        drawSurface.(1);
        drawSurface.(0);
        frontRow = rows - 1;
        Pen.fillColor = Color.white.alpha_(0.68);
        modeCount.do { |mode|
            var point = project.(frontRow, mode, fields[frontRow][mode], 0);
            Pen.fillOval(Rect(point.x - 1.7, point.y - 1.7, 3.4, 3.4));
        };
    };
    4.do { |index|
        var radius = 3 + (~qrmPopulations[index].sqrt * 7);
        Pen.fillColor = colors[index].alpha_(0.82);
        Pen.fillOval(Rect(width - 102 + (index * 23) - radius,
            22 - radius, radius * 2, radius * 2));
    };
    Pen.fillColor = Color.white.alpha_(0.18 + (0.82 * ~qrmCrossingFlash));
    Pen.fillOval(Rect(
        ~qrmContact[0].linlin(-1, 1, width * 0.10, width * 0.90) - 6,
        (height * 0.88) - (~qrmContact[1] * height * 0.07) - 6,
        12, 12
    ));
    Pen.stringAtPoint("history -> now   white = boundary contact", 130@(height - 18),
        Font("Helvetica Neue", 10), Color.white.alpha_(0.5));
};

~qrmRhoView = UserView(~qrmWindow, Rect(388, 76, 120, 120));
~qrmRhoView.background = Color.fromHexString("070a0f");
~qrmRhoView.drawFunc = {
    var magnitudes = Array.fill(16, { |index|
        (~qrmRhoReal[index].squared + ~qrmRhoImag[index].squared).sqrt
    });
    var maxMagnitude = magnitudes.maxItem.max(1e-9);
    var cellSize = 22;
    var originX = 16;
    var originY = 25;
    Pen.stringAtPoint("rho  |.| / phase", 14@7,
        Font("Helvetica Neue", 9, true), Color.white.alpha_(0.72));
    4.do { |row|
        4.do { |column|
            var index = (row * 4) + column;
            var magnitude = (magnitudes[index] / maxMagnitude).clip(0, 1);
            var phase = ~qrmRhoImag[index].atan2(~qrmRhoReal[index]);
            var hue = phase.linlin(-pi, pi, 0.68, 0.0).wrap(0, 1);
            var cell = Rect(
                originX + (column * cellSize), originY + (row * cellSize),
                cellSize - 2, cellSize - 2
            );
            Pen.fillColor = Color.hsv(
                hue, 0.78, 0.16 + (0.84 * magnitude), 0.96
            );
            Pen.fillRect(cell);
            Pen.strokeColor = if(row == column) {
                Color.white.alpha_(0.72)
            } {
                Color.white.alpha_(0.16)
            };
            Pen.width = if(row == column, { 1.0 }, { 0.5 });
            Pen.strokeRect(cell);
        };
    };
};

~qrmMetrics = StaticText(~qrmWindow, Rect(545, 62, 550, 72))
    .font_(Font("Menlo", 10)).stringColor_(Color.fromHexString("a9c5dd"));
StaticText(~qrmWindow, Rect(545, 137, 550, 18)).string_("REGIONAL TERRAIN  q (cyan) / qdot (pink)")
    .font_(Font("Helvetica Neue", 11, true)).stringColor_(Color.fromHexString("8ea4b8"));
~qrmQView = MultiSliderView(~qrmWindow, Rect(545, 157, 550, 38))
    .size_(4).isFilled_(true).fillColor_(Color.fromHexString("5dd9ff")).strokeColor_(Color.clear)
    .background_(Color.fromHexString("080b10"));
~qrmQdotView = MultiSliderView(~qrmWindow, Rect(545, 200, 550, 36))
    .size_(4).isFilled_(true).fillColor_(Color.fromHexString("ff7ac6")).strokeColor_(Color.clear)
    .background_(Color.fromHexString("080b10")).valueThumbSize_(1);
StaticText(~qrmWindow, Rect(545, 245, 550, 18)).string_("GEOMETRY-NATIVE MEMBRANE MODES (20)")
    .font_(Font("Helvetica Neue", 11, true)).stringColor_(Color.fromHexString("8ea4b8"));
~qrmModeView = MultiSliderView(~qrmWindow, Rect(545, 267, 550, 133))
    .size_(modeCount).isFilled_(true).fillColor_(Color.fromHexString("ffd166"))
    .strokeColor_(Color.clear).background_(Color.fromHexString("080b10"));

~qrmSoundButton = Button(~qrmWindow, Rect(22, 416, 185, 32))
    .states_([["SOUND LOCKED", Color.gray, Color.fromHexString("252a32")],
        ["SONIFICATION ON", Color.black, Color.fromHexString("80ed99")]])
    .enabled_(false)
    .action_({ |button|
        ~qrmSonify = button.value == 1;
        ~qrmBody !? { |node| node.set(\master, if(~qrmSonify) { ~qrmMaster } { 0.0 }) };
    });
~qrmResetButton = Button(~qrmWindow, Rect(218, 416, 120, 32)).states_([["RESET FIELD"]])
    .action_({
        ~qrmSonicReset.value;
        ~qrmControl.sendMsg(root ++ "/control/reset", 1);
    });
~qrmFreezeButton = Button(~qrmWindow, Rect(349, 416, 173, 32))
    .states_([["EVOLUTION LIVE"], ["EVOLUTION FROZEN"]])
    .action_({ |button| ~qrmControl.sendMsg(root ++ "/control/freeze", button.value) });
~qrmPreparationMenu = PopUpMenu(~qrmWindow, Rect(545, 416, 190, 32))
    .items_(~qrmPreparationItems)
    .value_(0)
    .action_({ |menu|
        ~qrmSonicReset.value;
        ~qrmControl.sendMsg(root ++ "/control/state", ~qrmPreparationItems[menu.value]);
    });
styleMenu.(~qrmPreparationMenu);
~qrmPreparationStatus = StaticText(~qrmWindow, Rect(745, 416, 350, 32))
    .align_(\center).font_(Font("Helvetica Neue", 10))
    .stringColor_(Color.fromHexString("d8b4fe"));

~qrmAddKnob = { |x, label, initial, lo, hi, action, labelWidth=68, numberWidth=42, warp=\lin|
    var knob = EZSlider(
        ~qrmWindow, Rect(x, 462, 250, 34), label,
        ControlSpec(lo, hi, warp), action, initial,
        labelWidth: labelWidth, numberWidth: numberWidth
    );
    knob.labelView.stringColor = Color.white;
    knob.numberView.stringColor = Color.white;
    knob.numberView.normalColor = Color.white;
    knob.numberView.typingColor = Color.white;
    knob.numberView.background = Color.fromHexString("080b10");
    knob;
};
~qrmFundSlider = ~qrmAddKnob.(22, "base Hz", ~qrmFundamental, 35, 220, { |view|
    ~qrmFundamental = view.value; ~qrmBody !? { |node| node.set(\fundamental, view.value) };
});
~qrmMasterSlider = ~qrmAddKnob.(282, "master", ~qrmMaster, 0, 0.7, { |view|
    ~qrmMaster = view.value;
    ~qrmBody !? { |node| node.set(\master, if(~qrmSonify) { view.value } { 0.0 }) };
});
~qrmMotionSlider = ~qrmAddKnob.(542, "motion", ~qrmMotionGain, 0, 2, { |view|
    ~qrmMotionGain = view.value; ~qrmBody !? { |node| node.set(\motionGain, view.value) };
}, 44);
~qrmStrikeSlider = ~qrmAddKnob.(802, "strike", ~qrmStrikeGain, 0, 1.5, { |view|
    ~qrmStrikeGain = view.value;
}, 40);

StaticText(~qrmWindow, Rect(22, 505, 1073, 18))
    .string_("TIME ENGINE + TEMPORAL SOUND ADAPTER  (routes excitation; does not alter rho evolution)")
    .font_(Font("Helvetica Neue", 11, true)).stringColor_(Color.fromHexString("8ecae6"));
~qrmTimeModeMenu = PopUpMenu(~qrmWindow, Rect(22, 527, 190, 26))
    .items_(~qrmTimeModeNames)
    .value_(~qrmTimeMode)
    .action_({ |menu|
        ~qrmTimeMode = menu.value;
        // The optional sixteen-lane observer owns its own clocks. Selecting
        // any main time mode must hand timing authority back to this engine;
        // otherwise every time control appears inert while hidden poly lanes
        // continue to pulse.
        ~qriPolyEnabled = false;
        ~qriStopPolyLanes !? { |stop| stop.value };
        ~qriPolyEnabledButton !? { |button| button.value_(0) };
        ~qrmEuclideanStep = 0;
        ~qrmQuantumEuclideanStep = 0;
    });
styleMenu.(~qrmTimeModeMenu);
~qrmFixedRateSlider = ~qrmAddKnob.(222, "rate Hz", ~qrmFixedRate, 0.25, 20, { |view|
    ~qrmFixedRate = view.value;
}, 45); ~qrmFixedRateSlider.view.bounds = Rect(222, 527, 155, 26);
~qrmHitsSlider = ~qrmAddKnob.(387, "hits", ~qrmEuclideanHits, 1, 16, { |view|
    ~qrmEuclideanHits = view.value.round.asInteger; ~qrmUpdateEuclideanMask.();
}, 32); ~qrmHitsSlider.view.bounds = Rect(387, 527, 125, 26);
~qrmStepsSlider = ~qrmAddKnob.(522, "steps", ~qrmEuclideanSteps, 2, 16, { |view|
    ~qrmEuclideanSteps = view.value.round.asInteger; ~qrmUpdateEuclideanMask.();
}, 36); ~qrmStepsSlider.view.bounds = Rect(522, 527, 125, 26);
~qrmBuresSlider = ~qrmAddKnob.(657, "Bures d/p", ~qrmBuresDistance, 0.001, 0.2, { |view|
    ~qrmBuresDistance = view.value;
    ~qrmControl.sendMsg(root ++ "/control/temporal_distance", view.value);
}, 58, 54); ~qrmBuresSlider.view.bounds = Rect(657, 527, 220, 26);
~qrmClockScaleSlider = ~qrmAddKnob.(887, "sched x", ~qrmClockScale, 0.01, 4, { |view|
    ~qrmClockScale = view.value;
    ~qrmControl.sendMsg(root ++ "/control/clock_scale", view.value);
}, 40, 50); ~qrmClockScaleSlider.view.bounds = Rect(887, 527, 208, 26);
~qrmResponse = ~qrmAddKnob.(22, "body s", ~qrmBodyResponse, 0.005, 1.5, { |view|
    ~qrmBodyResponse = view.value; ~qrmBody !? { |node| node.set(\response, view.value) };
}, 42); ~qrmResponse.view.bounds = Rect(22, 560, 200, 30);
~qrmDecay = ~qrmAddKnob.(238, "event decay", ~qrmCrossingDecay, 0.02, 4.0, { |view|
    ~qrmCrossingDecay = view.value;
}, 72, 42, \exp); ~qrmDecay.view.bounds = Rect(238, 560, 200, 30);
~qrmHarmonicMixSlider = ~qrmAddKnob.(454, "H16", ~qrmHarmonicMix, 0, 1.5, { |view|
    ~qrmHarmonicMix = view.value; ~qrmBody !? { |node| node.set(\harmonicMix, view.value) };
}, 30); ~qrmHarmonicMixSlider.view.bounds = Rect(454, 560, 200, 30);
~qrmPulseDepthSlider = ~qrmAddKnob.(670, "pulse mix", ~qrmPulseDepth, 0, 1, { |view|
    ~qrmPulseDepth = view.value; ~qrmBody !? { |node| node.set(\pulseDepth, view.value) };
}, 38); ~qrmPulseDepthSlider.view.bounds = Rect(670, 560, 200, 30);
~qrmRecursiveSlider = ~qrmAddKnob.(886, "depth", ~qrmRecursiveDepth, 0, 3, { |view|
    ~qrmRecursiveDepth = view.value.round.asInteger;
}, 38); ~qrmRecursiveSlider.view.bounds = Rect(886, 560, 209, 30);

StaticText(~qrmWindow, Rect(22, 598, 1073, 18))
    .string_("PHYSICAL DENSITY-ENGINE CONTROLS  (these transform rho; they are not DSP effects)")
    .font_(Font("Helvetica Neue", 11, true)).stringColor_(Color.fromHexString("ff9f7a"));
~qrmDephase = ~qrmAddKnob.(22, "dephase", 0.08, 0, 0.8, { |view|
    ~qrmControl.sendMsg(root ++ "/control/dephasing_rate", view.value)
}, 50); ~qrmDephase.view.bounds = Rect(22, 618, 200, 30);
~qrmDamping = ~qrmAddKnob.(282, "damp", 0.025, 0, 0.5, { |view|
    ~qrmControl.sendMsg(root ++ "/control/damping_rate", view.value)
}, 38); ~qrmDamping.view.bounds = Rect(238, 618, 200, 30);
~qrmDepolarize = ~qrmAddKnob.(542, "depolar", 0.005, 0, 0.25, { |view|
    ~qrmControl.sendMsg(root ++ "/control/depolarizing_rate", view.value)
}, 46); ~qrmDepolarize.view.bounds = Rect(454, 618, 200, 30);
~qrmCoupling = ~qrmAddKnob.(802, "couple", 0.72, 0, 2.5, { |view|
    ~qrmControl.sendMsg(root ++ "/control/coupling", view.value)
}, 42); ~qrmCoupling.view.bounds = Rect(670, 618, 200, 30);
~qrmDrive = ~qrmAddKnob.(886, "drive", 1.15, 0, 4, { |view|
    ~qrmControl.sendMsg(root ++ "/control/drive", view.value)
}, 34); ~qrmDrive.view.bounds = Rect(886, 618, 209, 30);

StaticText(~qrmWindow, Rect(22, 657, 325, 18))
    .string_("20 INDEPENDENT MODE VOLUMES  0–2")
    .font_(Font("Helvetica Neue", 10, true)).stringColor_(Color.fromHexString("ffd166"));
~qrmModeGainStatus = StaticText(~qrmWindow, Rect(350, 657, 192, 18))
    .string_("M1  volume 1.0").align_(\right)
    .font_(Font("Menlo", 10, true)).stringColor_(Color.fromHexString("ffd166"));
~qrmModeGainView = MultiSliderView(~qrmWindow, Rect(22, 678, 520, 62))
    .size_(modeCount).value_(~qrmModeGains / 2).elasticMode_(true).gap_(2)
    .drawLines_(true).isFilled_(true).fillColor_(Color.fromHexString("ffd166"))
    .background_(Color.fromHexString("080b10"))
    .action_({ |view|
        var requested = view.value.collect { |value| (value * 2).clip(0, 2) };
        var difference = Array.fill(modeCount, { |index|
            (requested[index] - ~qrmModeGains[index]).abs
        });
        var changedLane = difference.maxIndex;
        ~qrmSetModeGain.(changedLane, requested[changedLane]);
    });
~qrmModeMuteButtons = Array.fill(modeCount, { |index|
    Button(~qrmWindow, Rect(22 + (index * 26), 746, 24, 21))
        .states_([[(index + 1).asString, Color.grey(0.85), Color.grey(0.22)],
            ["M", Color.white, Color.red(0.58)]])
        .value_(~qrmModeMutes[index])
        .action_({ |button|
            ~qrmModeMutes[index] = button.value;
            ~qrmSelectedModeIndex = index;
            ~qrmModeGainStatus.string_("M%  volume % %".format(
                index + 1,
                ~qrmModeGains[index].round(0.01),
                if(button.value == 1) { "MUTED" } { "" }
            ));
            ~qrmPushModeMix.value;
        });
});
~qrmModeAudition = PopUpMenu(~qrmWindow, Rect(22, 773, 165, 23))
    .items_(["all geometry modes"] ++ Array.fill(modeCount, { |index| "isolate M" ++ (index + 1) }))
    .action_({ |menu| ~qrmAuditionMode = menu.value - 1; ~qrmPushModeMix.value });
styleMenu.(~qrmModeAudition);
Button(~qrmWindow, Rect(197, 773, 105, 23)).states_([["unity gains"]]).action_({
    ~qrmModeGains = Array.fill(modeCount, 1.0);
    ~qrmModeGainView.value_(~qrmModeGains / 2);
    ~qrmModeGainStatus.string_("M1  volume 1.0");
    ~qrmPushModeMix.value;
});
Button(~qrmWindow, Rect(312, 773, 105, 23)).states_([["unmute all"]]).action_({
    ~qrmModeMutes = Array.fill(modeCount, 0);
    ~qrmModeMuteButtons.do { |button| button.value_(0) };
    ~qrmPushModeMix.value;
});

StaticText(~qrmWindow, Rect(575, 657, 520, 18))
    .string_("DERIVED HARMONIC MONITOR — M1–M16 revoiced as H1–H16")
    .font_(Font("Helvetica Neue", 10, true)).stringColor_(Color.fromHexString("80ed99"));
~qrmHarmonicGainView = MultiSliderView(~qrmWindow, Rect(575, 678, 520, 62))
    .size_(harmonicCount).value_(~qrmHarmonicGains / 2).elasticMode_(true).gap_(3)
    .drawLines_(true).isFilled_(true).fillColor_(Color.fromHexString("80ed99"))
    .background_(Color.fromHexString("080b10"))
    .action_({ |view|
        ~qrmHarmonicGains = view.value.collect { |value| (value * 2).clip(0, 2) };
        ~qrmPushModeMix.value;
    });
~qrmHarmonicMuteButtons = Array.fill(harmonicCount, { |index|
    Button(~qrmWindow, Rect(575 + (index * 32.5), 746, 30, 21))
        .states_([["H" ++ (index + 1), Color.grey(0.85), Color.grey(0.22)],
            ["M", Color.white, Color.red(0.58)]])
        .value_(~qrmHarmonicMutes[index])
        .action_({ |button| ~qrmHarmonicMutes[index] = button.value; ~qrmPushModeMix.value });
});
~qrmHarmonicAudition = PopUpMenu(~qrmWindow, Rect(575, 773, 175, 23))
    .items_(["all harmonic partials"] ++ Array.fill(harmonicCount, { |index| "isolate H" ++ (index + 1) }))
    .action_({ |menu| ~qrmAuditionHarmonic = menu.value - 1; ~qrmPushModeMix.value });
styleMenu.(~qrmHarmonicAudition);
Button(~qrmWindow, Rect(760, 773, 105, 23)).states_([["unity gains"]]).action_({
    ~qrmHarmonicGains = Array.fill(harmonicCount, 1.0);
    ~qrmHarmonicGainView.value_(~qrmHarmonicGains / 2);
    ~qrmPushModeMix.value;
});
Button(~qrmWindow, Rect(875, 773, 105, 23)).states_([["unmute all"]]).action_({
    ~qrmHarmonicMutes = Array.fill(harmonicCount, 0);
    ~qrmHarmonicMuteButtons.do { |button| button.value_(0) };
    ~qrmPushModeMix.value;
});

~qrmCapturePerformancePreset = {
    (
        schema: "qmw.quantum_resonant_membrane.performance_preset.v2",
        fundamental: ~qrmFundamental,
        master: ~qrmMaster,
        motionGain: ~qrmMotionGain,
        strikeGain: ~qrmStrikeGain,
        bodyResponse: ~qrmBodyResponse,
        crossingDecay: ~qrmCrossingDecay,
        harmonicMix: ~qrmHarmonicMix,
        pulseDepth: ~qrmPulseDepth,
        pulseLevel: ~qrmPulseLevel,
        pulseAttack: ~qrmPulseAttack,
        pulseDecay: ~qrmPulseDecay,
        pulseRelease: ~qrmPulseRelease,
        energyDecayAmount: ~qrmEnergyDecayAmount,
        fieldTimbreDepth: ~qrmFieldTimbreDepth,
        momentumTimbreDepth: ~qrmMomentumTimbreDepth,
        modeGains: ~qrmModeGains.copy,
        modeMutes: ~qrmModeMutes.copy,
        harmonicGains: ~qrmHarmonicGains.copy,
        harmonicMutes: ~qrmHarmonicMutes.copy,
        auditionMode: ~qrmAuditionMode,
        auditionHarmonic: ~qrmAuditionHarmonic,
        pitchMode: ~qrmPitchMode,
        tuningFamily: ~qrmTuningFamily,
        edo: ~qrmEDO,
        tuningDegreeOffset: ~qrmTuningDegreeOffset,
        scalaFile: if(~qrmSelectedScalaPath.notEmpty, {
            PathName(~qrmSelectedScalaPath).fileName
        }, { "" }),
        timeMode: ~qrmTimeMode,
        fixedRate: ~qrmFixedRate,
        euclideanHits: ~qrmEuclideanHits,
        euclideanSteps: ~qrmEuclideanSteps,
        recursiveDepth: ~qrmRecursiveDepth,
        buresDistance: ~qrmBuresDistance,
        clockScale: ~qrmClockScale,
        geodesicBendingDepth: ~qrmGeodesicBendingDepth,
        eventThreshold: ~qrmEventThreshold,
        ringMix: ~qrmRingMix,
        ringHarmonic: ~qrmRingHarmonic,
        fuzzMix: ~qrmFuzzMix,
        fuzzDrive: ~qrmFuzzDrive,
        fuzzBias: ~qrmFuzzBias,
        fuzzTone: ~qrmFuzzTone,
        // Complete V3 scene, deliberately limited to audible adapter state.
        // QMW density, preparation, measurements, and incoming observer
        // frames remain live authorities and are never captured here.
        v3Scene: (
            schema: "qmw.unified_instrument_resonator.v3_scene.v1",
            qri: (
                enabled: ~qriEnabled ? true, mix: ~qriMix ? 0.55,
                eventGain: ~qriEventGain ? 0.75, decay: ~qriDecay ? 0.34,
                bodyMode: ~qriBodyMode ? 0, fieldBody: ~qriFieldBody ? 0,
                fieldGain: ~qriFieldGain ? 0.0, projectiveGain: ~qriProjectiveGain ? 0.12,
                hmiSend: ~qriHmiSend ? 0.0,
                allocatorEnabled: ~qriAllocatorEnabled ? true,
                allocatorMinVoices: ~qriAllocatorMinVoices ? 2,
                allocatorMaxVoices: ~qriMaxVoices ? 8,
                allocatorHeadroomTarget: ~qriAllocatorHeadroomTarget ? 45,
                allocatorCriticalPeakCPU: ~qriAllocatorCriticalPeakCPU ? 78,
                allocatorRecoverySeconds: ~qriAllocatorRecoverySeconds ? 4.0,
                allocatorAuxShedding: ~qriAllocatorAuxShedding ? true,
                allocatorGainCompensation: ~qriAllocatorGainCompensation ? true,
                voiceGains: (~qriVoiceGains ? []).copy,
                voiceDecays: (~qriVoiceDecays ? []).copy,
                voiceMutes: (~qriVoiceMutes ? []).copy,
                voiceFuzzSends: (~qriVoiceFuzzSends ? []).copy,
                voiceTemporalSends: (~qriVoiceTemporalSends ? []).copy,
                voiceFXSends: (~qriVoiceFXSends ? []).copy,
                vstRackSlotCount: ~qriVSTRackSlotCount ? 2,
                vstRackTopology: ~qriVSTRackTopology ? 0,
                vstRackReturn: ~qriVSTRackReturn ? 0.0,
                vstRackBypasses: (~qriVSTRackBypasses ? []).copy,
                vstRackSlotGains: (~qriVSTRackSlotGains ? []).copy,
                vstRackPluginKeys: (~qriVSTRackPluginKeys ? []).copy,
                vstRackPresetNames: (~qriVSTRackPresetNames ? []).copy,
                projectiveOutBase: ~qriProjectiveOutBase ? 0,
                projectiveGains: (~qriProjectiveGains ? []).copy,
                projectiveMutes: (~qriProjectiveMutes ? []).copy,
                projectiveDelays: (~qriProjectiveDelays ? []).copy,
                polyEnabled: ~qriPolyEnabled ? false,
                polyBaseHz: ~qriPolyBaseHz ? 0.25,
                polyLaneChannels: (~qriPolyLaneChannels ? []).copy,
                polyRateMultipliers: (~qriPolyRateMultipliers ? []).copy,
                polyPhaseFractions: (~qriPolyPhaseFractions ? []).copy,
                polyLaneEnabled: (~qriPolyLaneEnabled ? []).copy,
                qhoMix: ~qriQHOMix ? 1.0, fmRatio: ~qriFMRatio ? 1.618,
                fmIndex: ~qriFMIndex ? 5.0,
                chebGain: ~qriChebGain ? 0.0,
                chebMode: ~qriChebMode ? 0,
                chebCalibration: ~qriChebCalibration ? 1,
                chebContactSeconds: ~qriChebContactSeconds ? 0.012,
                chebIncidence: ~qriChebIncidence ? 0.0,
                chebOrder: ~qriChebOrder ? 8,
                chebCoherenceDepth: ~qriChebCoherenceDepth ? 1.0,
                chebDecay: ~qriChebDecay ? 0.8,
                parsevalMode: ~qriParsevalMode ? 0,
                parsevalBasis: ~qriParsevalBasis ? 0,
                parsevalTargetRMS: ~qriParsevalTargetRMS ? 0.18,
                miRingsPitch: ~qriMiRingsPitch ? 54,
                miRingsStructure: ~qriMiRingsStructure ? 0.32,
                miRingsBrightness: ~qriMiRingsBrightness ? 0.56,
                miRingsDamping: ~qriMiRingsDamping ? 0.58,
                miRingsPosition: ~qriMiRingsPosition ? 0.28,
                miRingsModel: ~qriMiRingsModel ? 0,
                miRingsGain: ~qriMiRingsGain ? 0.14,
                miRingsSixEnabled: ~qriMiRingsSixEnabled ? false,
                miRingsSixPitchOffsets: (~qriMiRingsSixPitchOffsets ? []).copy,
                miRingsSixDecay: ~qriMiRingsSixDecay ? 0.42,
                plaitsEngine: ~qriPlaitsEngine ? 2,
                plaitsHarmonics: ~qriPlaitsHarmonics ? 0.5,
                plaitsTimbre: ~qriPlaitsTimbre ? 0.6,
                plaitsMorph: ~qriPlaitsMorph ? 0.45,
                plaitsDecay: ~qriPlaitsDecay ? 0.5,
                elementsContour: ~qriElementsContour ? 0.36,
                elementsBow: ~qriElementsBow ? 0.0,
                elementsBlow: ~qriElementsBlow ? 0.0,
                elementsStrike: ~qriElementsStrike ? 0.72,
                elementsGeometry: ~qriElementsGeometry ? 0.32,
                elementsBrightness: ~qriElementsBrightness ? 0.58,
                elementsDamping: ~qriElementsDamping ? 0.64,
                elementsSpace: ~qriElementsSpace ? 0.30,
                elementsModel: ~qriElementsModel ? 0,
                cloudsReturn: ~qriCloudsReturn ? 0.0,
                cloudsPitch: ~qriCloudsPitch ? 0.0,
                cloudsPosition: ~qriCloudsPosition ? 0.5,
                cloudsSize: ~qriCloudsSize ? 0.45,
                cloudsDensity: ~qriCloudsDensity ? 0.65,
                cloudsTexture: ~qriCloudsTexture ? 0.5,
                cloudsDryWet: ~qriCloudsDryWet ? 1.0,
                cloudsInputGain: ~qriCloudsInputGain ? 1.0,
                cloudsSpread: ~qriCloudsSpread ? 0.5,
                cloudsReverb: ~qriCloudsReverb ? 0.2,
                cloudsFeedback: ~qriCloudsFeedback ? 0.2,
                cloudsFreeze: ~qriCloudsFreeze ? 0,
                cloudsMode: ~qriCloudsMode ? 0,
                cloudsLofi: ~qriCloudsLofi ? 0
            ),
            modalSpectral: (
                enabled: ~qmsvEnabled ? false, level: ~qmsvLevel ? 0.34,
                exciterColor: ~qmsvExciterColor ? 0.56, centroid: ~qmsvCentroid ? 0.45,
                width: ~qmsvWidth ? 0.62, brightness: ~qmsvBrightness ? 0.35,
                decay: ~qmsvDecay ? 1.0, decaySlope: ~qmsvDecaySlope ? -0.20,
                hilbertFollow: ~qmsvHilbertFollow ? true,
                hilbertLevel: ~qmsvHilbertLevel ? 0.20,
                hilbertMotionDepth: ~qmsvHilbertMotionDepth ? 0.72,
                hilbertAttack: ~qmsvHilbertAttack ? 0.035,
                hilbertRelease: ~qmsvHilbertRelease ? 0.38,
                strikeNode: ~qmsvStrikeNode ? 0, leftNode: ~qmsvLeftNode ? 0,
                rightNode: ~qmsvRightNode ? 1
            ),
            modalGeometry: (
                enabled: ~qmgEnabled ? false, influence: ~qmgInfluence ? 0.35,
                motionEnabled: ~qmgMotionEnabled ? false,
                motionDepth: ~qmgMotionDepth ? 0.0,
                motionRateHz: ~qmgMotionRateHz ? 0.08
            ),
            temporalMemory: if(~qmwTemporalMemorySetMixer.notNil, {
                (
                    mix: ~qmwTemporalMemoryMix ? 0.18,
                    fuzzSend: ~qmwTemporalMemoryFuzzSend ? 0.0,
                    selfFeedback: ~qmwTemporalMemorySelfFeedback ? 0.62,
                    tapFocus: ~qmwTemporalMemoryTapFocus ? 0.0,
                    baseDelaySeconds: ~qmwTemporalMemoryBaseDelaySeconds ? 0.137,
                    ratioPreset: ~qmwTemporalMemoryRatioPreset ? "rational",
                    phaseWarp: ~qmwTemporalMemoryPhaseWarp ? 0.23,
                    feedbackAmount: ~qmwTemporalMemoryFeedbackAmount ? 0.42,
                    diffusion: ~qmwTemporalMemoryDiffusion ? 0.0,
                    feedbackTone: ~qmwTemporalMemoryFeedbackTone ? 6200,
                    width: ~qmwTemporalMemoryWidth ? 0.7,
                    glideSeconds: ~qmwTemporalMemoryGlideSeconds ? 0.16,
                    frozen: ~qmwTemporalMemoryFrozen ? false,
                    observerBed: ~qmwTemporalMemoryObserverBed ? 0.0
                )
            }, { nil }),
            harmonicMemory: if(~qmwHmiSetMixer.notNil, {
                (
                    mix: ~qmwHmiMix ? 0.0,
                    baseDelaySeconds: ~qmwHmiBaseDelaySeconds ? 0.037,
                    harmonicExponent: ~qmwHmiHarmonicExponent ? 1.0,
                    glideSeconds: ~qmwHmiGlideSeconds ? 0.08,
                    ratios: (~qmwHmiRatios ? []).copy
                )
            }, { nil }),
            matrix: if(~qmxRoutes.notNil, {
                (
                    routes: ~qmxRoutes.collect { |row|
                        row.collect { |route| if(route.notNil, { route.copy }, { nil }) }
                    },
                    selectedSource: ~qmxSelectedSource ? 3,
                    selectedDestination: ~qmxSelectedDestination ? 7,
                    decayRoutes: if(~qmxDecayRoutes.notNil, {
                        ~qmxDecayRoutes.collect { |row|
                            row.collect { |route| route.copy }
                        }
                    }, { nil }),
                    decayRangeOctaves: ~qmxDecayRangeOctaves ? 2.0,
                    decaySelectedSource: ~qmxDecaySelectedSource ? 0,
                    decaySelectedDestination: ~qmxDecaySelectedDestination ? 0
                )
            }, { nil })
        )
    )
};

~qrmRecallPerformancePreset = { |slot, source="GUI"|
    var preset = ~qrmPresetSlots[slot.asInteger.clip(0, ~qrmPresetSlotCount - 1)];
    if(preset.isNil, {
        ~qrmPresetStatus !? { |view|
            view.string_("slot % is empty".format(slot + 1))
        };
    }, {
        ~qrmFundSlider.valueAction_(preset[\fundamental] ? ~qrmFundamental);
        ~qrmMasterSlider.valueAction_(preset[\master] ? ~qrmMaster);
        ~qrmMotionSlider.valueAction_(preset[\motionGain] ? ~qrmMotionGain);
        ~qrmStrikeSlider.valueAction_(preset[\strikeGain] ? ~qrmStrikeGain);
        ~qrmResponse.valueAction_(preset[\bodyResponse] ? ~qrmBodyResponse);
        ~qrmDecay.valueAction_(preset[\crossingDecay] ? ~qrmCrossingDecay);
        ~qrmHarmonicMixSlider.valueAction_(preset[\harmonicMix] ? ~qrmHarmonicMix);
        ~qrmPulseDepthSlider.valueAction_(preset[\pulseDepth] ? ~qrmPulseDepth);
        ~qrmPulseLevel = preset[\pulseLevel] ? ~qrmPulseLevel;
        ~qrmPulseAttack = preset[\pulseAttack] ? ~qrmPulseAttack;
        ~qrmPulseDecay = preset[\pulseDecay] ? ~qrmPulseDecay;
        ~qrmPulseRelease = preset[\pulseRelease] ? ~qrmPulseRelease;
        ~qrmBody !? { |node|
            node.set(
                \pulseLevel, ~qrmPulseLevel,
                \pulseAttack, ~qrmPulseAttack,
                \pulseDecay, ~qrmPulseDecay,
                \pulseRelease, ~qrmPulseRelease
            )
        };
        ~qrmPulseLevelSlider !? { |view| view.value_(~qrmPulseLevel) };
        ~qrmPulseAttackSlider !? { |view| view.value_(~qrmPulseAttack) };
        ~qrmPulseDecaySlider !? { |view| view.value_(~qrmPulseDecay) };
        ~qrmPulseReleaseSlider !? { |view| view.value_(~qrmPulseRelease) };
        ~qrmEnergyDecayAmount = preset[\energyDecayAmount] ? ~qrmEnergyDecayAmount;
        ~qrmFieldTimbreDepth = preset[\fieldTimbreDepth] ? ~qrmFieldTimbreDepth;
        ~qrmMomentumTimbreDepth = preset[\momentumTimbreDepth]
            ? ~qrmMomentumTimbreDepth;
        ~qrmEnergyDecaySlider !? { |view| view.value_(~qrmEnergyDecayAmount) };
        ~qrmFieldTimbreSlider !? { |view| view.value_(~qrmFieldTimbreDepth) };
        ~qrmMomentumTimbreSlider !? { |view|
            view.value_(~qrmMomentumTimbreDepth)
        };
        ~qrmModeGains = (preset[\modeGains] ? ~qrmModeGains).copy;
        ~qrmModeMutes = (preset[\modeMutes] ? ~qrmModeMutes).copy;
        ~qrmHarmonicGains = (preset[\harmonicGains] ? ~qrmHarmonicGains).copy;
        ~qrmHarmonicMutes = (preset[\harmonicMutes] ? ~qrmHarmonicMutes).copy;
        ~qrmAuditionMode = preset[\auditionMode] ? -1;
        ~qrmAuditionHarmonic = preset[\auditionHarmonic] ? -1;
        ~qrmModeGainView.value_(~qrmModeGains / 2);
        ~qrmModeMuteButtons.do { |button, index| button.value_(~qrmModeMutes[index]) };
        ~qrmHarmonicGainView.value_(~qrmHarmonicGains / 2);
        ~qrmHarmonicMuteButtons.do { |button, index|
            button.value_(~qrmHarmonicMutes[index])
        };
        ~qrmModeAudition.value_(~qrmAuditionMode + 1);
        ~qrmHarmonicAudition.value_(~qrmAuditionHarmonic + 1);
        ~qrmPitchMode = (preset[\pitchMode] ? ~qrmPitchMode)
            .asInteger.clip(0, ~qrmPitchModeNames.size - 1);
        ~qrmPitchModeMenu !? { |menu| menu.value_(~qrmPitchMode) };
        ~qrmTuningFamily = (preset[\tuningFamily] ? ~qrmTuningFamily)
            .asInteger.clip(0, ~qrmTuningFamilyNames.size - 1);
        ~qrmEDO = (preset[\edo] ? ~qrmEDO).asInteger.clip(5, 72);
        ~qrmTuningDegreeOffset = (preset[\tuningDegreeOffset]
            ? ~qrmTuningDegreeOffset).asInteger.clip(0, 127);
        if((preset[\scalaFile] ? "").notEmpty) {
            var recalledScalaPath = scalaDirectory +/+ preset[\scalaFile];
            if(PathName(recalledScalaPath).isFile) {
                ~qrmLoadScalaPath.(recalledScalaPath)
            };
        };
        ~qrmTuningFamilyMenu !? { |menu| menu.value_(~qrmTuningFamily) };
        ~qrmEDOSlider !? { |view| view.value_(~qrmEDO) };
        ~qrmTuningDegreeSlider !? { |view| view.value_(~qrmTuningDegreeOffset) };
        ~qrmRefreshTuningChoices.value;
        ~qrmUpdatePitchRatios.value;
        ~qrmTimeMode = (preset[\timeMode] ? ~qrmTimeMode)
            .asInteger.clip(0, ~qrmTimeModeNames.size - 1);
        ~qrmTimeModeMenu.value_(~qrmTimeMode);
        ~qrmFixedRateSlider.valueAction_(preset[\fixedRate] ? ~qrmFixedRate);
        ~qrmHitsSlider.valueAction_(preset[\euclideanHits] ? ~qrmEuclideanHits);
        ~qrmStepsSlider.valueAction_(preset[\euclideanSteps] ? ~qrmEuclideanSteps);
        ~qrmRecursiveSlider.valueAction_(preset[\recursiveDepth] ? ~qrmRecursiveDepth);
        ~qrmBuresSlider.valueAction_(preset[\buresDistance] ? ~qrmBuresDistance);
        ~qrmClockScaleSlider.valueAction_(preset[\clockScale] ? ~qrmClockScale);
        ~qrmPerformanceBuresSlider !? { |view| view.value_(~qrmBuresDistance) };
        ~qrmPerformanceClockSlider !? { |view| view.value_(~qrmClockScale) };
        ~qrmEventThreshold = preset[\eventThreshold] ? ~qrmEventThreshold;
        ~qrmControl.sendMsg(
            root ++ "/control/event_threshold", ~qrmEventThreshold
        );
        ~qrmEventThresholdSlider !? { |view|
            view.value_(~qrmEventThreshold)
        };
        ~qrmGeodesicBendingDepth = preset[\geodesicBendingDepth]
            ? ~qrmGeodesicBendingDepth;
        ~qrmControl.sendMsg(
            root ++ "/control/geodesic_bending_depth", ~qrmGeodesicBendingDepth
        );
        ~qrmRingMix = preset[\ringMix] ? ~qrmRingMix;
        ~qrmRingHarmonic = (preset[\ringHarmonic] ? ~qrmRingHarmonic)
            .asInteger.clip(1, 16);
        ~qrmFuzzMix = preset[\fuzzMix] ? ~qrmFuzzMix;
        ~qrmFuzzDrive = preset[\fuzzDrive] ? ~qrmFuzzDrive;
        ~qrmFuzzBias = preset[\fuzzBias] ? ~qrmFuzzBias;
        ~qrmFuzzTone = preset[\fuzzTone] ? ~qrmFuzzTone;
        ~qrmRingMixSlider !? { |view| view.value_(~qrmRingMix) };
        ~qrmRingHarmonicSlider !? { |view| view.value_(~qrmRingHarmonic) };
        ~qrmFuzzMixSlider !? { |view| view.value_(~qrmFuzzMix) };
        ~qrmFuzzDriveSlider !? { |view| view.value_(~qrmFuzzDrive) };
        ~qrmFuzzBiasSlider !? { |view| view.value_(~qrmFuzzBias) };
        ~qrmFuzzToneSlider !? { |view| view.value_(~qrmFuzzTone) };
        ~qrmGeodesicBendSlider !? { |view|
            view.value_(~qrmGeodesicBendingDepth)
        };
        ~qrmEuclideanStep = 0;
        ~qrmQuantumEuclideanStep = 0;
        ~qrmUpdateEuclideanMask.value;
        ~qrmPushModeMix.value;
        ~qrmPushPerformanceFx.value;
        // V1 performance slots remain fully compatible: they simply have no
        // V3 scene payload, so their established recall path above is left
        // unchanged. A V2 capture restores every downstream audible adapter
        // through its own live apply seam, never through QMW state mutation.
        if(preset[\v3Scene].notNil, {
            var scene = preset[\v3Scene];
            var qri = scene[\qri];
            var modalSpectral = scene[\modalSpectral];
            var modalGeometry = scene[\modalGeometry];
            var temporalMemory = scene[\temporalMemory];
            var harmonicMemory = scene[\harmonicMemory];
            var matrix = scene[\matrix];
            if(qri.notNil, {
                ~qriEnabled = qri[\enabled] ? ~qriEnabled;
                ~qriMix = qri[\mix] ? ~qriMix;
                ~qriEventGain = qri[\eventGain] ? ~qriEventGain;
                ~qriDecay = qri[\decay] ? ~qriDecay;
                ~qriBodyMode = (qri[\bodyMode] ? ~qriBodyMode).asInteger.clip(0, 2);
                ~qriFieldBody = (qri[\fieldBody] ? ~qriFieldBody).asInteger.clip(0, 2);
                ~qriFieldGain = (qri[\fieldGain] ? ~qriFieldGain).asFloat.clip(0, 0.35);
                ~qriProjectiveGain = (qri[\projectiveGain] ? ~qriProjectiveGain).asFloat.clip(0, 0.5);
                ~qriHmiSend = (qri[\hmiSend] ? ~qriHmiSend).asFloat.clip(0, 1);
                ~qriAllocatorEnabled = qri[\allocatorEnabled] ? (~qriAllocatorEnabled ? true);
                ~qriAllocatorMinVoices = (qri[\allocatorMinVoices]
                    ? (~qriAllocatorMinVoices ? 2)).asInteger.clip(1, 8);
                ~qriMaxVoices = (qri[\allocatorMaxVoices] ? (~qriMaxVoices ? 8))
                    .asInteger.clip(2, 8);
                ~qriAllocatorHeadroomTarget = (qri[\allocatorHeadroomTarget]
                    ? (~qriAllocatorHeadroomTarget ? 45)).asFloat.clip(20, 70);
                ~qriAllocatorCriticalPeakCPU = (qri[\allocatorCriticalPeakCPU]
                    ? (~qriAllocatorCriticalPeakCPU ? 78)).asFloat.clip(55, 95);
                ~qriAllocatorRecoverySeconds = (qri[\allocatorRecoverySeconds]
                    ? (~qriAllocatorRecoverySeconds ? 4)).asFloat.clip(1, 20);
                ~qriAllocatorAuxShedding = qri[\allocatorAuxShedding]
                    ? (~qriAllocatorAuxShedding ? true);
                ~qriAllocatorGainCompensation = qri[\allocatorGainCompensation]
                    ? (~qriAllocatorGainCompensation ? true);
                // Migrate six-lane V3 scenes index-wise. Newly introduced MI
                // lanes and FX sends remain silent when older presets omit them.
                ~qriVoiceGains = Array.fill(8, { |index|
                    ((qri[\voiceGains] ? ~qriVoiceGains)[index] ? 0.0)
                        .asFloat.clip(0, 1.5)
                });
                // V3 scenes created before per-lane decay inherit their one
                // saved decay across all eight voices.
                ~qriVoiceDecays = Array.fill(8, { |index|
                    ((qri[\voiceDecays] ? Array.fill(8, ~qriDecay))[index]
                        ? ~qriDecay).asFloat.clip(0.02, 6.0)
                });
                ~qriDecay = ~qriVoiceDecays.maxItem;
                ~qriVoiceMutes = Array.fill(8, { |index|
                    ((qri[\voiceMutes] ? ~qriVoiceMutes)[index] ? 0)
                        .asInteger.clip(0, 1)
                });
                ~qriVoiceFuzzSends = Array.fill(8, { |index|
                    ((qri[\voiceFuzzSends] ? ~qriVoiceFuzzSends)[index] ? 0.0)
                        .asFloat.clip(0, 1)
                });
                ~qriVoiceTemporalSends = Array.fill(8, { |index|
                    ((qri[\voiceTemporalSends] ? ~qriVoiceTemporalSends)[index] ? 0.0)
                        .asFloat.clip(0, 1)
                });
                ~qriVoiceFXSends = Array.fill(8, { |index|
                    ((qri[\voiceFXSends] ? ~qriVoiceFXSends)[index] ? 0.0)
                        .asFloat.clip(0, 1)
                });
                ~qriVSTRackSlotCount = (qri[\vstRackSlotCount] ? (~qriVSTRackSlotCount ? 2))
                    .asInteger.clip(2, 4);
                ~qriVSTRackTopology = (qri[\vstRackTopology] ? (~qriVSTRackTopology ? 0))
                    .asInteger.clip(0, 1);
                ~qriVSTRackReturn = (qri[\vstRackReturn] ? (~qriVSTRackReturn ? 0.0))
                    .asFloat.clip(0, 1);
                ~qriVSTReturn = ~qriVSTRackReturn;
                ~qriVSTRackBypasses = Array.fill(4, { |index|
                    ((qri[\vstRackBypasses] ? (~qriVSTRackBypasses ? []))[index] ? 0)
                        .asInteger.clip(0, 1)
                });
                ~qriVSTRackSlotGains = Array.fill(4, { |index|
                    ((qri[\vstRackSlotGains] ? (~qriVSTRackSlotGains ? []))[index] ? 1.0)
                        .asFloat.clip(0, 1.5)
                });
                ~qriVSTRackPluginKeys = Array.fill(4, { |index|
                    (qri[\vstRackPluginKeys] ? (~qriVSTRackPluginKeys ? []))[index]
                });
                ~qriVSTRackPresetNames = Array.fill(4, { |index|
                    (qri[\vstRackPresetNames] ? (~qriVSTRackPresetNames ? []))[index]
                });
                ~qriProjectiveOutBase = (qri[\projectiveOutBase] ? ~qriProjectiveOutBase).asInteger.max(0);
                ~qriProjectiveGains = (qri[\projectiveGains] ? ~qriProjectiveGains).copy;
                ~qriProjectiveMutes = (qri[\projectiveMutes] ? ~qriProjectiveMutes).copy;
                ~qriProjectiveDelays = (qri[\projectiveDelays] ? ~qriProjectiveDelays).copy;
                ~qriQHOMix = qri[\qhoMix] ? ~qriQHOMix;
                ~qriFMRatio = qri[\fmRatio] ? ~qriFMRatio;
                ~qriFMIndex = qri[\fmIndex] ? ~qriFMIndex;
                ~qriChebGain = (qri[\chebGain] ? (~qriChebGain ? 0.0))
                    .asFloat.clip(0, 1.5);
                ~qriChebMode = (qri[\chebMode] ? (~qriChebMode ? 0))
                    .asInteger.clip(0, 1);
                ~qriChebCalibration = (qri[\chebCalibration]
                    ? (~qriChebCalibration ? 1)).asInteger.clip(0, 1);
                ~qriChebContactSeconds = (qri[\chebContactSeconds]
                    ? (~qriChebContactSeconds ? 0.012)).asFloat.clip(0.001, 0.5);
                ~qriChebIncidence = (qri[\chebIncidence]
                    ? (~qriChebIncidence ? 0.0)).asFloat.clip(0, pi / 2);
                ~qriChebOrder = (qri[\chebOrder] ? (~qriChebOrder ? 8))
                    .asInteger.clip(1, 16);
                ~qriChebCoherenceDepth = (qri[\chebCoherenceDepth]
                    ? (~qriChebCoherenceDepth ? 1.0)).asFloat.clip(0, 1);
                ~qriChebDecay = (qri[\chebDecay] ? (~qriChebDecay ? 0.8))
                    .asFloat.clip(0.02, 6.0);
                ~qriParsevalMode = (qri[\parsevalMode] ? (~qriParsevalMode ? 0))
                    .asInteger.clip(0, 1);
                ~qriParsevalBasis = (qri[\parsevalBasis] ? (~qriParsevalBasis ? 0))
                    .asInteger.clip(0, 2);
                ~qriParsevalTargetRMS = (qri[\parsevalTargetRMS]
                    ? (~qriParsevalTargetRMS ? 0.18)).asFloat.clip(0, 0.5);
                ~qriMiRingsPitch = qri[\miRingsPitch] ? ~qriMiRingsPitch;
                ~qriMiRingsStructure = qri[\miRingsStructure] ? ~qriMiRingsStructure;
                ~qriMiRingsBrightness = qri[\miRingsBrightness] ? ~qriMiRingsBrightness;
                ~qriMiRingsDamping = qri[\miRingsDamping] ? ~qriMiRingsDamping;
                ~qriMiRingsPosition = qri[\miRingsPosition] ? ~qriMiRingsPosition;
                ~qriMiRingsModel = qri[\miRingsModel] ? ~qriMiRingsModel;
                ~qriMiRingsGain = qri[\miRingsGain] ? ~qriMiRingsGain;
                ~qriMiRingsSixEnabled = qri[\miRingsSixEnabled] ? false;
                ~qriMiRingsSixPitchOffsets = (qri[\miRingsSixPitchOffsets]
                    ? ~qriMiRingsSixPitchOffsets).copy;
                ~qriMiRingsSixDecay = qri[\miRingsSixDecay] ? ~qriMiRingsSixDecay;
                ~qriPlaitsEngine = qri[\plaitsEngine] ? ~qriPlaitsEngine;
                ~qriPlaitsHarmonics = qri[\plaitsHarmonics] ? ~qriPlaitsHarmonics;
                ~qriPlaitsTimbre = qri[\plaitsTimbre] ? ~qriPlaitsTimbre;
                ~qriPlaitsMorph = qri[\plaitsMorph] ? ~qriPlaitsMorph;
                ~qriPlaitsDecay = qri[\plaitsDecay] ? ~qriPlaitsDecay;
                ~qriElementsContour = qri[\elementsContour] ? ~qriElementsContour;
                ~qriElementsBow = qri[\elementsBow] ? ~qriElementsBow;
                ~qriElementsBlow = qri[\elementsBlow] ? ~qriElementsBlow;
                ~qriElementsStrike = qri[\elementsStrike] ? ~qriElementsStrike;
                ~qriElementsGeometry = qri[\elementsGeometry] ? ~qriElementsGeometry;
                ~qriElementsBrightness = qri[\elementsBrightness] ? ~qriElementsBrightness;
                ~qriElementsDamping = qri[\elementsDamping] ? ~qriElementsDamping;
                ~qriElementsSpace = qri[\elementsSpace] ? ~qriElementsSpace;
                ~qriElementsModel = qri[\elementsModel] ? ~qriElementsModel;
                ~qriCloudsReturn = qri[\cloudsReturn] ? ~qriCloudsReturn;
                ~qriCloudsPitch = qri[\cloudsPitch] ? ~qriCloudsPitch;
                ~qriCloudsPosition = qri[\cloudsPosition] ? ~qriCloudsPosition;
                ~qriCloudsSize = qri[\cloudsSize] ? ~qriCloudsSize;
                ~qriCloudsDensity = qri[\cloudsDensity] ? ~qriCloudsDensity;
                ~qriCloudsTexture = qri[\cloudsTexture] ? ~qriCloudsTexture;
                ~qriCloudsDryWet = qri[\cloudsDryWet] ? ~qriCloudsDryWet;
                ~qriCloudsInputGain = qri[\cloudsInputGain] ? ~qriCloudsInputGain;
                ~qriCloudsSpread = qri[\cloudsSpread] ? ~qriCloudsSpread;
                ~qriCloudsReverb = qri[\cloudsReverb] ? ~qriCloudsReverb;
                ~qriCloudsFeedback = qri[\cloudsFeedback] ? ~qriCloudsFeedback;
                ~qriCloudsFreeze = qri[\cloudsFreeze] ? ~qriCloudsFreeze;
                ~qriCloudsMode = qri[\cloudsMode] ? ~qriCloudsMode;
                ~qriCloudsLofi = qri[\cloudsLofi] ? ~qriCloudsLofi;
                ~qriPolyEnabled = qri[\polyEnabled] ? ~qriPolyEnabled;
                ~qriPolyBaseHz = qri[\polyBaseHz] ? ~qriPolyBaseHz;
                ~qriPolyLaneChannels = (qri[\polyLaneChannels] ? ~qriPolyLaneChannels).copy;
                ~qriPolyRateMultipliers = (qri[\polyRateMultipliers] ? ~qriPolyRateMultipliers).copy;
                ~qriPolyPhaseFractions = (qri[\polyPhaseFractions] ? ~qriPolyPhaseFractions).copy;
                ~qriPolyLaneEnabled = (qri[\polyLaneEnabled] ? ~qriPolyLaneEnabled).copy;
                ~qriApplyAllocatorPolicy !? { |apply| apply.value };
                ~qriPushVoiceGains !? { |push| push.value };
                ~qriPushVoiceDecays !? { |push| push.value };
                ~qriPushVoiceFuzzSends !? { |push| push.value };
                ~qriPushVoiceTemporalSends !? { |push| push.value };
                ~qriPushVoiceFXSends !? { |push| push.value };
                ~qriUpdateCloudsReturn !? { |update| update.value };
                ~qriApplyVSTRackScene !? { |apply| apply.value };
                ~qriPushFMControls !? { |push| push.value };
                ~qriPushChebControls !? { |push| push.value };
                ~qriPushParsevalControls !? { |push| push.value };
                ~qriPushProjectiveCalibration !? { |push| push.value };
                ~qriApplyBodyMode !? { |apply| apply.value };
                if(~qriMiRingsSixEnabled, {
                    ~qriPolyEnabled = false;
                    ~qriStopPolyLanes !? { |stop| stop.value };
                }, {
                if(~qriPolyEnabled, {
                    ~qriStartPolyLanes !? { |start| start.value }
                }, {
                    ~qriStopPolyLanes !? { |stop| stop.value }
                });
                });
            });
            if(modalSpectral.notNil, {
                ~qmsvEnabled = modalSpectral[\enabled] ? ~qmsvEnabled;
                ~qmsvLevel = modalSpectral[\level] ? ~qmsvLevel;
                ~qmsvExciterColor = modalSpectral[\exciterColor] ? ~qmsvExciterColor;
                ~qmsvCentroid = modalSpectral[\centroid] ? ~qmsvCentroid;
                ~qmsvWidth = modalSpectral[\width] ? ~qmsvWidth;
                ~qmsvBrightness = modalSpectral[\brightness] ? ~qmsvBrightness;
                ~qmsvDecay = modalSpectral[\decay] ? ~qmsvDecay;
                ~qmsvDecaySlope = modalSpectral[\decaySlope] ? ~qmsvDecaySlope;
                ~qmsvHilbertFollow = modalSpectral[\hilbertFollow] ? ~qmsvHilbertFollow;
                ~qmsvHilbertLevel = modalSpectral[\hilbertLevel] ? ~qmsvHilbertLevel;
                ~qmsvHilbertMotionDepth = modalSpectral[\hilbertMotionDepth] ? ~qmsvHilbertMotionDepth;
                ~qmsvHilbertAttack = modalSpectral[\hilbertAttack] ? ~qmsvHilbertAttack;
                ~qmsvHilbertRelease = modalSpectral[\hilbertRelease] ? ~qmsvHilbertRelease;
                ~qmsvStrikeNode = modalSpectral[\strikeNode] ? ~qmsvStrikeNode;
                ~qmsvLeftNode = modalSpectral[\leftNode] ? ~qmsvLeftNode;
                ~qmsvRightNode = modalSpectral[\rightNode] ? ~qmsvRightNode;
                ~qmsvApplyScene !? { |apply| apply.value };
            });
            if(modalGeometry.notNil, {
                ~qmgEnabled = modalGeometry[\enabled] ? ~qmgEnabled;
                ~qmgInfluence = modalGeometry[\influence] ? ~qmgInfluence;
                ~qmgMotionEnabled = modalGeometry[\motionEnabled] ? ~qmgMotionEnabled;
                ~qmgMotionDepth = modalGeometry[\motionDepth] ? ~qmgMotionDepth;
                ~qmgMotionRateHz = modalGeometry[\motionRateHz] ? ~qmgMotionRateHz;
                ~qmgApplyScene !? { |apply| apply.value };
            });
            if(temporalMemory.notNil, {
                ~qmwTemporalMemorySetMixer !? { |set|
                    set.value(temporalMemory[\mix] ? ~qmwTemporalMemoryMix,
                        temporalMemory[\fuzzSend] ? ~qmwTemporalMemoryFuzzSend)
                };
                ~qmwTemporalMemorySetSelfFeedback !? { |set|
                    set.value(temporalMemory[\selfFeedback] ? ~qmwTemporalMemorySelfFeedback)
                };
                ~qmwTemporalMemorySetTapFocus !? { |set|
                    set.value(temporalMemory[\tapFocus] ? ~qmwTemporalMemoryTapFocus)
                };
                ~qmwTemporalMemorySetBaseDelaySeconds !? { |set|
                    set.value(temporalMemory[\baseDelaySeconds] ? ~qmwTemporalMemoryBaseDelaySeconds)
                };
                ~qmwTemporalMemorySetFeedbackTone !? { |set|
                    set.value(temporalMemory[\feedbackTone] ? ~qmwTemporalMemoryFeedbackTone)
                };
                ~qmwTemporalMemorySetWidth !? { |set|
                    set.value(temporalMemory[\width] ? ~qmwTemporalMemoryWidth)
                };
                ~qmwTemporalMemorySetGlideSeconds !? { |set|
                    set.value(temporalMemory[\glideSeconds] ? ~qmwTemporalMemoryGlideSeconds)
                };
                ~qmwTemporalMemorySetFreeze !? { |set|
                    set.value(temporalMemory[\frozen] ? ~qmwTemporalMemoryFrozen)
                };
                ~qmwTemporalMemorySetObserverBed !? { |set|
                    set.value(temporalMemory[\observerBed] ? ~qmwTemporalMemoryObserverBed)
                };
                ~qmwTemporalMemoryRatioPreset = temporalMemory[\ratioPreset] ? ~qmwTemporalMemoryRatioPreset;
                ~qmwTemporalMemoryPhaseWarp = temporalMemory[\phaseWarp] ? ~qmwTemporalMemoryPhaseWarp;
                ~qmwTemporalMemoryFeedbackAmount = temporalMemory[\feedbackAmount] ? ~qmwTemporalMemoryFeedbackAmount;
                ~qmwTemporalMemoryDiffusion = temporalMemory[\diffusion] ? ~qmwTemporalMemoryDiffusion;
                ~qriTemporalMemoryControlAddress !? { |address|
                    address.sendMsg("/qmw/temporal_memory/v1/control/ratio_preset", ~qmwTemporalMemoryRatioPreset);
                    address.sendMsg("/qmw/temporal_memory/v1/control/phase_warp", ~qmwTemporalMemoryPhaseWarp);
                    address.sendMsg("/qmw/temporal_memory/v1/control/feedback_amount", ~qmwTemporalMemoryFeedbackAmount);
                    address.sendMsg("/qmw/temporal_memory/v1/control/diffusion", ~qmwTemporalMemoryDiffusion);
                };
            });
            if(harmonicMemory.notNil and: { ~qmwHmiSetMixer.notNil }, {
                ~qmwHmiSetMixer.value(harmonicMemory[\mix] ? ~qmwHmiMix);
                ~qmwHmiSetBaseDelay.value(harmonicMemory[\baseDelaySeconds] ? ~qmwHmiBaseDelaySeconds);
                ~qmwHmiSetHarmonicExponent.value(harmonicMemory[\harmonicExponent] ? ~qmwHmiHarmonicExponent);
                ~qmwHmiSetGlideSeconds.value(harmonicMemory[\glideSeconds] ? ~qmwHmiGlideSeconds);
                ~qmwHmiRatios = (harmonicMemory[\ratios] ? ~qmwHmiRatios).copy;
                ~qmwHmiSynth !? { |synth| synth.setn(\ratios, ~qmwHmiRatios) };
            });
            if(matrix.notNil and: { matrix[\routes].notNil }, {
                ~qmxRoutes = matrix[\routes].collect { |row|
                    row.collect { |route| if(route.notNil, { route.copy }, { nil }) }
                };
                ~qmxSelectedSource = (matrix[\selectedSource] ? ~qmxSelectedSource).asInteger.clip(0, 7);
                ~qmxSelectedDestination = (matrix[\selectedDestination] ? ~qmxSelectedDestination).asInteger.clip(0, 7);
                if(matrix[\decayRoutes].notNil, {
                    ~qmxDecayRoutes = matrix[\decayRoutes].collect { |row|
                        row.collect { |route| route.copy }
                    };
                });
                ~qmxDecayRangeOctaves = (matrix[\decayRangeOctaves]
                    ? (~qmxDecayRangeOctaves ? 2.0)).asFloat.clip(0, 4);
                ~qmxDecaySelectedSource = (matrix[\decaySelectedSource]
                    ? (~qmxDecaySelectedSource ? 0)).asInteger.clip(0, 7);
                ~qmxDecaySelectedDestination = (matrix[\decaySelectedDestination]
                    ? (~qmxDecaySelectedDestination ? 0)).asInteger.clip(0, 7);
                ~qmxApplyDecayScene !? { |apply| apply.value };
                ~qmxApplyScene !? { |apply| apply.value };
            });
        });
        ~qrmPresetStatus !? { |view|
            view.string_("% recalled % slot %".format(source,
                if(preset[\v3Scene].notNil, { "complete scene" }, { "performance" }), slot + 1))
        };
    });
};

~qrmOpenTuning = {
    var tuningWindow, makeSlider;
    ~qrmTuningWindow !? _.close;
    ~qrmInterferenceTimbreWindow !? _.close;
    tuningWindow = Window(
        "QRM Geometric Tuning + Scala Dictionary", Rect(205, 95, 720, 330)
    );
    ~qrmTuningWindow = tuningWindow;
    tuningWindow.background = Color.fromHexString("11151c");
    makeSlider = { |label, rect, spec, initial, action, labelWidth=92|
        var slider = EZSlider(
            tuningWindow, rect, label, spec, action, initial,
            labelWidth: labelWidth, numberWidth: 54
        );
        slider.labelView.stringColor = Color.white;
        slider.numberView.stringColor = Color.white;
        slider.numberView.normalColor = Color.white;
        slider.numberView.typingColor = Color.white;
        slider.numberView.background = Color.fromHexString("080b10");
        slider
    };
    StaticText(tuningWindow, Rect(22, 14, 676, 26))
        .string_("GEOMETRIC TUNING  /  offline Huygens-Fokker Scala dictionary")
        .font_(Font("Helvetica Neue", 15, true))
        .stringColor_(Color.fromHexString("dcecff"));
    StaticText(tuningWindow, Rect(22, 52, 82, 26)).string_("family")
        .stringColor_(Color.fromHexString("ffd166"));
    ~qrmTuningFamilyMenu = PopUpMenu(tuningWindow, Rect(106, 50, 205, 28))
        .items_(~qrmTuningFamilyNames)
        .value_(~qrmTuningFamily)
        .action_({ |menu|
            ~qrmTuningFamily = menu.value;
            ~qrmRefreshTuningChoices.value;
            ~qrmUpdatePitchRatios.value;
        });
    styleMenu.(~qrmTuningFamilyMenu);
    ~qrmEDOSlider = makeSlider.(
        "n-EDO", Rect(329, 50, 175, 28),
        ControlSpec(5, 72, \lin, 1, ~qrmEDO), ~qrmEDO,
        { |view|
            ~qrmEDO = view.value.round.asInteger;
            if(~qrmTuningFamily == 0) { ~qrmUpdatePitchRatios.value };
        }, 58
    );
    ~qrmTuningDegreeSlider = makeSlider.(
        "degree", Rect(522, 50, 176, 28),
        ControlSpec(0, 127, \lin, 1, ~qrmTuningDegreeOffset),
        ~qrmTuningDegreeOffset,
        { |view|
            ~qrmTuningDegreeOffset = view.value.round.asInteger;
            ~qrmUpdatePitchRatios.value;
        }, 58
    );
    StaticText(tuningWindow, Rect(22, 94, 82, 26)).string_("search")
        .stringColor_(Color.fromHexString("8ecae6"));
    ~qrmScalaFilterField = styleTextField.(TextField(tuningWindow, Rect(106, 92, 405, 28))
        .string_(~qrmScalaFilter)
        .action_({ |field|
            ~qrmScalaFilter = field.string;
            ~qrmRefreshTuningChoices.value;
        }));
    Button(tuningWindow, Rect(522, 92, 176, 28)).states_([["FILTER DICTIONARY"]])
        .action_({
            ~qrmScalaFilter = ~qrmScalaFilterField.string;
            ~qrmRefreshTuningChoices.value;
        });
    StaticText(tuningWindow, Rect(22, 136, 82, 26)).string_("scale")
        .stringColor_(Color.fromHexString("8ecae6"));
    ~qrmScalaMenu = PopUpMenu(tuningWindow, Rect(106, 134, 592, 28))
        .items_(~qrmScalaNames)
        .action_({ |menu|
            if(~qrmScalaPaths.notEmpty) {
                ~qrmLoadScalaPath.(~qrmScalaPaths[menu.value].fullPath);
                ~qrmUpdatePitchRatios.value;
            };
        });
    styleMenu.(~qrmScalaMenu);
    ~qrmTuningStatus = StaticText(tuningWindow, Rect(22, 178, 676, 58))
        .font_(Font("Menlo", 10))
        .stringColor_(Color.fromHexString("80ed99"));
    StaticText(tuningWindow, Rect(22, 246, 676, 58))
        .string_(
            "n-EDO is generated locally. Wilson, Tenney, and La Monte Young are "
            ++ "curated filename views into the same archive. Scala dictionary "
            ++ "shows the first 512 matches; type a search to reach any scale."
        )
        .stringColor_(Color.fromHexString("a9c5dd"));
    tuningWindow.onClose = {
        if(~qrmTuningWindow === tuningWindow) {
            ~qrmTuningWindow = nil;
            ~qrmTuningFamilyMenu = nil;
            ~qrmEDOSlider = nil;
            ~qrmTuningDegreeSlider = nil;
            ~qrmScalaFilterField = nil;
            ~qrmScalaMenu = nil;
            ~qrmTuningStatus = nil;
        };
    };
    ~qrmRefreshTuningChoices.value;
    ~qrmUpdatePitchRatios.value;
    if(~qrmTuningFamily == 0) {
        ~qrmTuningStatus.string_(~qrmActiveTuningDescription)
    };
    tuningWindow.front;
};

~qrmOpenPerformance = {
    var makeSlider, performanceWindow;
    ~qrmPerformanceWindow !? _.close;
    performanceWindow = Window(
        "QRM Time + Performance FX + Presets", Rect(150, 20, 680, 764)
    );
    ~qrmPerformanceWindow = performanceWindow;
    ~qrmPerformanceWindow.background = Color.fromHexString("11151c");
    makeSlider = { |label, rect, spec, initial, action, labelWidth=118|
        var slider = EZSlider(
            ~qrmPerformanceWindow, rect, label, spec, action, initial,
            labelWidth: labelWidth, numberWidth: 58
        );
        slider.labelView.stringColor = Color.white;
        slider.numberView.stringColor = Color.white;
        slider.numberView.normalColor = Color.white;
        slider.numberView.typingColor = Color.white;
        slider.numberView.background = Color.fromHexString("080b10");
        slider;
    };
    StaticText(~qrmPerformanceWindow, Rect(22, 14, 636, 28))
        .string_("BURES TIME  /  16-HARMONIC RING  /  CIRCUIT-INSPIRED FUZZ")
        .font_(Font("Helvetica Neue", 16, true))
        .stringColor_(Color.fromHexString("dcecff"));
    ~qrmPresetMenu = PopUpMenu(~qrmPerformanceWindow, Rect(22, 52, 120, 28))
        .items_(Array.fill(~qrmPresetSlotCount, { |index| "slot " ++ (index + 1) }))
        .value_(0);
    styleMenu.(~qrmPresetMenu);
    Button(~qrmPerformanceWindow, Rect(152, 52, 100, 28))
        .states_([["STORE"]]).action_({
            var slot = ~qrmPresetMenu.value ? 0;
            ~qrmPresetSlots[slot] = ~qrmCapturePerformancePreset.value;
            presetPath.dirname.mkdir;
            ~qrmPresetSlots.writeArchive(presetPath);
            ~qrmPresetStatus.string_("stored performance slot %".format(slot + 1));
        });
    Button(~qrmPerformanceWindow, Rect(262, 52, 100, 28))
        .states_([["RECALL"]]).action_({
            ~qrmRecallPerformancePreset.(~qrmPresetMenu.value ? 0, "GUI")
        });
    ~qrmPresetStatus = StaticText(~qrmPerformanceWindow, Rect(376, 52, 282, 28))
        .string_("32 slots  /  MIDI C0-G2 recalls")
        .stringColor_(Color.fromHexString("80ed99"));
    ~qrmPerformanceMetrics = StaticText(
        ~qrmPerformanceWindow, Rect(22, 92, 636, 48)
    ).font_(Font("Menlo", 10)).stringColor_(Color.fromHexString("8ecae6"));
    ~qrmPerformanceBuresSlider = makeSlider.(
        "Bures distance/pulse", Rect(22, 148, 306, 30),
        ControlSpec(0.001, 0.2, \exp, 0.0001, ~qrmBuresDistance),
        ~qrmBuresDistance,
        { |view| ~qrmBuresSlider.valueAction_(view.value) }, 126
    );
    ~qrmPerformanceClockSlider = makeSlider.(
        "SCHEDULER / RECORD SCALE", Rect(350, 148, 308, 30),
        ControlSpec(0.01, 4, \exp, 0.001, ~qrmClockScale),
        ~qrmClockScale,
        { |view| ~qrmClockScaleSlider.valueAction_(view.value) }, 126
    );
    ~qrmEventThresholdSlider = makeSlider.(
        "QRM FLUX", Rect(22, 184, 202, 30),
        ControlSpec(0.00001, 0.05, \exp, 0.000001, ~qrmEventThreshold),
        ~qrmEventThreshold,
        { |view|
            ~qrmEventThreshold = view.value;
            ~qrmControl.sendMsg(root ++ "/control/event_threshold", view.value);
        }, 68
    );
    ~qrmEventThresholdSlider.view.toolTip_(
        "Standalone QRM crossing threshold; this is not the unified interaction pluck gate."
    );
    ~qrmPerformancePluckThresholdSlider = makeSlider.(
        "PLUCK QUANTUM", Rect(238, 184, 202, 30),
        ControlSpec(0.005, 0.5, \exp, 0.0001, 0.10),
        (~qriRequestedPluckThreshold ? 0.10),
        { |view|
            ~qriSetPluckThreshold !? { |setter| setter.value(view.value) }
        }, 86
    );
    ~qrmPerformancePluckThresholdSlider.view.toolTip_(
        "Unified event-admission threshold: lower means more frequent plucks; higher means fewer."
    );
    ~qrmGeodesicBendSlider = makeSlider.(
        "GEODESIC", Rect(454, 184, 204, 30),
        ControlSpec(0, 100, \lin, 0.01, ~qrmGeodesicBendingDepth),
        ~qrmGeodesicBendingDepth,
        { |view|
            ~qrmGeodesicBendingDepth = view.value;
            ~qrmControl.sendMsg(
                root ++ "/control/geodesic_bending_depth", view.value
            );
        }, 72
    );
    StaticText(~qrmPerformanceWindow, Rect(22, 224, 452, 18))
        .string_("MODAL BODY PULSES  /  FIELD or HYBRID only; audition includes dynamic adapters")
        .font_(Font("Helvetica Neue", 10, true))
        .stringColor_(Color.fromHexString("8ecae6"));
    Button(~qrmPerformanceWindow, Rect(492, 220, 166, 22))
        .states_([["AUDITION PULSE + ADAPTERS", Color.black, Color.fromHexString("8ecae6")]])
        .action_({ ~qrmAuditionModalPulse.value });
    ~qrmPulseLevelSlider = makeSlider.(
        "volume", Rect(22, 246, 146, 30),
        ControlSpec(0, 2, \lin, 0.001, ~qrmPulseLevel), ~qrmPulseLevel,
        { |view|
            ~qrmPulseLevel = view.value;
            ~qrmBody !? { |node| node.set(\pulseLevel, view.value) }
        }, 52
    );
    ~qrmPulseAttackSlider = makeSlider.(
        "attack", Rect(182, 246, 146, 30),
        ControlSpec(0.001, 0.25, \exp, 0.001, ~qrmPulseAttack), ~qrmPulseAttack,
        { |view|
            ~qrmPulseAttack = view.value;
            ~qrmBody !? { |node| node.set(\pulseAttack, view.value) }
        }, 52
    );
    ~qrmPulseDecaySlider = makeSlider.(
        "decay", Rect(342, 246, 146, 30),
        ControlSpec(0.02, 2, \exp, 0.001, ~qrmPulseDecay), ~qrmPulseDecay,
        { |view|
            ~qrmPulseDecay = view.value;
            ~qrmBody !? { |node| node.set(\pulseDecay, view.value) }
        }, 48
    );
    ~qrmPulseReleaseSlider = makeSlider.(
        "release", Rect(502, 246, 156, 30),
        ControlSpec(0.05, 6, \exp, 0.001, ~qrmPulseRelease), ~qrmPulseRelease,
        { |view|
            ~qrmPulseRelease = view.value;
            ~qrmBody !? { |node| node.set(\pulseRelease, view.value) }
        }, 52
    );
    StaticText(~qrmPerformanceWindow, Rect(22, 284, 104, 24))
        .string_("PITCH MAP")
        .font_(Font("Helvetica Neue", 10, true))
        .stringColor_(Color.fromHexString("ffd166"));
    ~qrmPitchModeMenu = PopUpMenu(~qrmPerformanceWindow, Rect(132, 282, 190, 28))
        .items_(~qrmPitchModeNames)
        .value_(~qrmPitchMode)
        .action_({ |menu|
            ~qrmPitchMode = menu.value;
            ~qrmUpdatePitchRatios.value;
        });
    styleMenu.(~qrmPitchModeMenu);
    StaticText(~qrmPerformanceWindow, Rect(334, 282, 180, 28))
        .string_("audio mapping; M1-M20 remain independent")
        .stringColor_(Color.fromHexString("b8a56a"));
    Button(~qrmPerformanceWindow, Rect(522, 282, 136, 28))
        .states_([["EDIT TUNING…"]]).action_({ ~qrmOpenTuning.value });
    StaticText(~qrmPerformanceWindow, Rect(22, 318, 636, 18))
        .string_("DYNAMIC ADAPTERS  /  sampled from field motion; never written into rho")
        .font_(Font("Helvetica Neue", 10, true))
        .stringColor_(Color.fromHexString("80ed99"));
    ~qrmFieldTimbreSlider = makeSlider.(
        "field depth", Rect(22, 340, 200, 30),
        ControlSpec(0, 2, \lin, 0.001, ~qrmFieldTimbreDepth), ~qrmFieldTimbreDepth,
        { |view| ~qrmFieldTimbreDepth = view.value; ~qrmUpdateDynamicAdapters.value }, 78
    );
    ~qrmMomentumTimbreSlider = makeSlider.(
        "momentum", Rect(240, 340, 200, 30),
        ControlSpec(0, 2, \lin, 0.001, ~qrmMomentumTimbreDepth),
        ~qrmMomentumTimbreDepth,
        { |view| ~qrmMomentumTimbreDepth = view.value; ~qrmUpdateDynamicAdapters.value }, 78
    );
    ~qrmEnergyDecaySlider = makeSlider.(
        "E→decay", Rect(458, 340, 200, 30),
        ControlSpec(-1, 1, \lin, 0.001, ~qrmEnergyDecayAmount),
        ~qrmEnergyDecayAmount,
        { |view| ~qrmEnergyDecayAmount = view.value; ~qrmUpdateDynamicAdapters.value }, 78
    );
    StaticText(~qrmPerformanceWindow, Rect(22, 386, 636, 18))
        .string_("RING MODULATION  /  balanced multiplication at base Hz × H1…H16")
        .font_(Font("Helvetica Neue", 10, true))
        .stringColor_(Color.fromHexString("ffd166"));
    ~qrmRingMixSlider = makeSlider.(
        "ring blend", Rect(22, 408, 306, 30),
        ControlSpec(0, 1, \lin, 0.001, ~qrmRingMix), ~qrmRingMix,
        { |view| ~qrmRingMix = view.value; ~qrmPushPerformanceFx.value }, 92
    );
    ~qrmRingHarmonicSlider = makeSlider.(
        "ring harmonic", Rect(350, 408, 308, 30),
        ControlSpec(1, 16, \lin, 1, ~qrmRingHarmonic), ~qrmRingHarmonic,
        { |view|
            ~qrmRingHarmonic = view.value.round.asInteger;
            ~qrmPushPerformanceFx.value
        }, 104
    );
    StaticText(~qrmPerformanceWindow, Rect(22, 444, 636, 30))
        .string_("Blend 0 is an exact dry bypass. The selected H number follows base Hz and presets.")
        .stringColor_(Color.fromHexString("b8a56a"));
    StaticText(~qrmPerformanceWindow, Rect(22, 480, 636, 18))
        .string_("FUZZ  /  two-stage biased transistor + asymmetric limiter approximation")
        .font_(Font("Helvetica Neue", 10, true))
        .stringColor_(Color.fromHexString("ff7ac6"));
    ~qrmFuzzMixSlider = makeSlider.(
        "field fuzz send", Rect(22, 502, 306, 30),
        ControlSpec(0, 1, \lin, 0.001, ~qrmFuzzMix), ~qrmFuzzMix,
        { |view| ~qrmFuzzMix = view.value; ~qrmPushPerformanceFx.value }, 92
    );
    ~qrmFuzzDriveSlider = makeSlider.(
        "fuzz drive", Rect(350, 502, 308, 30),
        ControlSpec(1, 40, \exp, 0.01, ~qrmFuzzDrive), ~qrmFuzzDrive,
        { |view| ~qrmFuzzDrive = view.value; ~qrmPushPerformanceFx.value }, 92
    );
    ~qrmFuzzBiasSlider = makeSlider.(
        "transistor bias", Rect(22, 538, 306, 30),
        ControlSpec(-0.45, 0.45, \lin, 0.001, ~qrmFuzzBias), ~qrmFuzzBias,
        { |view| ~qrmFuzzBias = view.value; ~qrmPushPerformanceFx.value }, 104
    );
    ~qrmFuzzToneSlider = makeSlider.(
        "passive tone Hz", Rect(350, 538, 308, 30),
        ControlSpec(800, 12000, \exp, 1, ~qrmFuzzTone), ~qrmFuzzTone,
        { |view| ~qrmFuzzTone = view.value; ~qrmPushPerformanceFx.value }, 104
    );
    StaticText(~qrmPerformanceWindow, Rect(22, 576, 636, 62))
        .string_(
            "Signal order: ring → input coupling → biased first stage → frequency-shaped "
            ++ "interstage loading → asymmetric second-stage limiting → tone rolloff. "
            ++ "Field fuzz send 0 is exact bypass; pluck-voice sends live in the Integrated Resonant Instrument mixer. "
            ++ "This is sound design, not quantum dynamics."
        )
        .stringColor_(Color.fromHexString("a9c5dd"));
    StaticText(~qrmPerformanceWindow, Rect(22, 652, 636, 68))
        .string_(
            "COMPLETE V3 SCENES store QRM sound plus every loaded downstream adapter: six-channel mixer/sends, "
            ++ "16-lane rhythm, Modal Spectral/Geometry, Temporal/Harmonic Memory, and Matrix routes. They deliberately do not "
            ++ "change rho, physical density controls, preparation, incoming frames, or the audio device."
        )
        .stringColor_(Color.fromHexString("80ed99"));
    ~qrmPerformanceWindow.onClose = {
        if(~qrmPerformanceWindow === performanceWindow) {
            ~qrmPerformanceWindow = nil;
            ~qrmPerformanceMetrics = nil;
            ~qrmPresetStatus = nil;
            ~qrmPerformanceBuresSlider = nil;
            ~qrmPerformanceClockSlider = nil;
            ~qrmEventThresholdSlider = nil;
            ~qrmPerformancePluckThresholdSlider = nil;
            ~qrmPulseLevelSlider = nil;
            ~qrmPulseAttackSlider = nil;
            ~qrmPulseDecaySlider = nil;
            ~qrmPulseReleaseSlider = nil;
            ~qrmPitchModeMenu = nil;
            ~qrmEnergyDecaySlider = nil;
            ~qrmFieldTimbreSlider = nil;
            ~qrmMomentumTimbreSlider = nil;
            ~qrmRingMixSlider = nil;
            ~qrmRingHarmonicSlider = nil;
            ~qrmFuzzMixSlider = nil;
            ~qrmFuzzDriveSlider = nil;
            ~qrmFuzzBiasSlider = nil;
            ~qrmFuzzToneSlider = nil;
            ~qrmGeodesicBendSlider = nil;
        };
    };
    ~qrmPerformanceWindow.front;
};

~qrmPresetMIDINoteOn !? _.free;
try {
    MIDIClient.init;
    MIDIIn.connectAll;
    ~qrmPresetMIDINoteOn = MIDIFunc.noteOn({ |velocity, note|
        var slot = note.asInteger - 12;
        if((velocity > 0) and: { slot.inclusivelyBetween(0, 31) }) {
            { ~qrmRecallPerformancePreset.(slot, "MIDI note %".format(note)) }.defer
        };
    });
} { |error|
    "QRM MIDI preset recall unavailable: %".format(error).warn;
};

~qrmFooter = StaticText(~qrmWindow, Rect(22, 826, 1073, 28))
    .string_("rho -> effective Lagrangian terrain -> probability current -> localized membrane modes -> sound")
    .align_(\center).font_(Font("Helvetica Neue", 13, true)).stringColor_(Color.fromHexString("6f879d"));

~qrmGuiRoutine = Routine({
    inf.do {
        var live = ~qrmAvailable and: { ~qrmCompatible }
            and: { (Main.elapsedTime - ~qrmLastFrameAt) < 2.0 };
        var peak, velocityPeak, envelopeDepth, envelope;
        ~qrmAvailable = live;
        ~qrmStatus.string = if(live) {
            "OBSERVER LIVE  /  revision " ++ ~qrmRevision
        } {
            if(~qrmCompatible.not and: { ~qrmRevision >= 0 }) {
                "INCOMPATIBLE CAPABILITY  /  sound gated"
            } {
                "BACKEND UNAVAILABLE  /  sound gated"
            }
        };
        ~qrmStatus.stringColor = if(live) { Color.fromHexString("80ed99") } { Color.fromHexString("ff7a8a") };
        ~qrmSoundButton.enabled = live and: { ~qrmAudioReady };
        ~qrmPreparationMenu.value = ~qrmPreparationItems.indexOfEqual(
            ~qrmPreparationMode
        ) ? 0;
        ~qrmPreparationStatus.string = "PREP  " ++ ~qrmPreparationSemantics;
        if(live.not and: { ~qrmSonify }) {
            ~qrmSonify = false;
            ~qrmSoundButton.value = 0;
            ~qrmBody !? { |node| node.set(\master, 0.0) };
        };
        ~qrmMetrics.string = "purity %  entropy % bit  coh L1 %\nFIELD dw %  chi %  Q %..%  g %\nEVENT +%  dP %  thr %  fill %   |j|max %\nrho dE % / n%   terrain w % h<% n%\nmembrane w % h<% n%   voices %/%   time %"
            .format(
                ~qrmPurity.round(0.0001), ~qrmEntropy.round(0.0001), ~qrmCoherence.round(0.0001),
                ~qrmFieldMaxOffset.round(0.0001),
                ~qrmFieldMeanSusceptibility.round(0.0001),
                ~qrmFieldMinQ.round(0.01), ~qrmFieldMaxQ.round(0.01),
                ~qrmFieldMaxCoupling.round(0.0001),
                ~qrmEventCount, ~qrmEventProbability.round(0.0001),
                ~qrmEventThreshold.round(0.00001),
                ~qrmEventAccumulatorFill.round(0.01),
                ~qrmMaxCurrent.round(0.0001),
                ~qrmHamiltonianSpan.round(0.001), ~qrmDensitySubsteps,
                ~qrmTerrainOmega.round(0.001), ~qrmTerrainStabilityDt.round(0.00001),
                ~qrmTerrainSubsteps, ~qrmMembraneOmega.round(0.001),
                ~qrmMembraneStabilityDt.round(0.00001), ~qrmMembraneSubsteps,
                ~qrmStrikeNodes.size, ~qrmMaxStrikeVoices,
                ~qrmTimeModeNames[~qrmTimeMode]
            );
        ~qrmPerformanceMetrics !? { |view|
            view.string_(
                (
                    "EVENT thr % fill %%% +% | PULSE activity % Hz %..% ADR %/%/%\n"
                    ++ "dBures %   intrinsic %   remainder %   records %  +%\n"
                    ++ "Q-geodesic weighted %   defect %   bend %   records %  +%"
                ).format(
                    ~qrmEventThreshold.round(0.00001),
                    (~qrmEventAccumulatorFill * 100).round(0.1), ~qrmEventCount,
                    ~qrmPulseActivities.maxItem.round(0.01),
                    ~qrmPulseRates.minItem.round(0.01),
                    ~qrmPulseRates.maxItem.round(0.01),
                    ~qrmPulseAttack.round(0.001),
                    ~qrmPulseDecay.round(0.001),
                    ~qrmPulseRelease.round(0.001),
                    ~qrmBuresDelta.round(0.000001),
                    ~qrmBuresLength.round(0.0001),
                    ~qrmBuresRemainder.round(0.0001),
                    ~qrmBuresRecordIndex, ~qrmBuresPulses,
                    ~qrmBuresWeightedTime.round(0.0001),
                    ~qrmBuresTriangleDefect.round(0.000001),
                    ~qrmBuresNormalizedBending.round(0.0001),
                    ~qrmBuresGeodesicRecordIndex, ~qrmBuresGeodesicPulses
                )
            );
        };
        ~qrmQView.value = ~qrmQ.collect { |value| value.clip(0, 1) };
        ~qrmQdotView.value = ~qrmQdot.collect { |value| value.linlin(-1, 1, 0, 1).clip(0, 1) };
        ~qrmModeView.value = ~qrmModes.collect { |value| value.linlin(-1, 1, 0, 1).clip(0, 1) };
        ~qrmCrossingFlash = (~qrmCrossingFlash * 0.82).max(0.0);
        ~qrmWaveFrameCounter = ~qrmWaveFrameCounter + 1;
        // Native mesh defaults to 15 visual frames/second. Physics and audio
        // stay at 30 Hz, and the divider remains presentation-only.
        if(live and: { (~qrmWaveFrameCounter % ~qrmMeshRefreshDivisor) == 0 }) {
            // A single rigid/lowest mode must not flatten the remaining field.
            // This changes only display scale; the raw OSC values are retained.
            peak = ~qrmRawModes.collect(_.abs).sort[17].max(1e-9);
            velocityPeak = ~qrmModeVelocities.collect(_.abs).maxItem.max(1e-9);
            ~qrmWaveScale = peak.max(~qrmWaveScale * 0.985).max(1e-6);
            envelopeDepth = ~qrmWaveScale
                * (0.12 + (0.18 * (~qrmCoherence / 3).clip(0, 1)));
            envelope = ~qrmModeVelocities.collect { |value|
                envelopeDepth * (0.4 + (0.6 * (value.abs / velocityPeak).clip(0, 1)))
            };
            ~qrmWaveHistory = ~qrmWaveHistory.add(~qrmRawModes.copy);
            ~qrmWaveEnvelopeHistory = ~qrmWaveEnvelopeHistory.add(envelope);
            if(~qrmWaveHistory.size > ~qrmWaveHistoryLength) {
                ~qrmWaveHistory = ~qrmWaveHistory.copyRange(
                    ~qrmWaveHistory.size - ~qrmWaveHistoryLength,
                    ~qrmWaveHistory.size - 1
                );
                ~qrmWaveEnvelopeHistory = ~qrmWaveEnvelopeHistory.copyRange(
                    ~qrmWaveEnvelopeHistory.size - ~qrmWaveHistoryLength,
                    ~qrmWaveEnvelopeHistory.size - 1
                );
            };
            ~qrmSphere.refresh;
            ~qrmRhoView.refresh;
        };
        (1 / 15).wait;
    };
}).play(AppClock);

~qrmCleanup = {
    ~qrmGuiRoutine !? _.stop;
    ~qrmTimeClock !? _.stop;
    ~qrmStrikeGroup !? _.freeAll;
    ~qrmStrikeGroup !? _.free;
    ~qrmBody !? _.free;
    ~qrmRoutingWindow !? _.close;
    ~qrmPerformanceWindow !? _.close;
    ~qrmTuningWindow !? _.close;
    ~qrmPresetMIDINoteOn !? _.free;
    ~qrmServerQuitHandler !? { |handler| s.onQuitRemove(handler) };
    [\qrmFrameBeginV1, \qrmAvailableV1, \qrmDensityGlobalV1,
        \qrmDensityPreparationV1, \qrmBuresTemporalGlobalV1,
        \qrmFieldGlobalV1, \qrmFieldOffsetsV1,
        \qrmFieldSusceptibilityV1, \qrmEventGlobalV1,
        \qrmModeGainControlV1, \qrmModeCombinationControlV1, \qrmPopulationsV1,
        \qrmRhoRealV1, \qrmRhoImagV1,
        \qrmTerrainQV1, \qrmTerrainQdotV1, \qrmTerrainGlobalV1, \qrmFlowGlobalV1,
        \qrmRegionFluxV1, \qrmModesV1, \qrmRawModesV1, \qrmModeVelocitiesV1,
        \qrmRatiosV1, \qrmInterferenceTimbreMetaV1,
        \qrmInterferenceTimbreGainsV1, \qrmInterferenceTimbreOutputV1,
        \qrmMembraneGlobalV1,
        \qrmCrossingV1, \qrmFrameEndV1].do { |key| OSCdef(key).free };
};
// The main QRM window is the session owner.  Closing it must release the
// audio server and end sclang so a shell launcher can reap every sidecar; a
// GUI-only cleanup leaves scsynth holding UDP 57120 after the window vanishes.
~qrmQuitSession = {
    if(~qrmSessionQuitting.not) {
        ~qrmSessionQuitting = true;
        ~qrmControl.sendMsg(root ++ "/control/quit", 1);
        ~qfrCleanup !? { |function| function.value };
        ~qriCleanup !? { |function| function.value };
        ~qrmCleanup.value;
        s.quit;
        AppClock.sched(0.35, { 0.exit; nil });
    };
};
~qrmWindow.onClose = {
    ~qrmQuitSession.value;
};
~qrmWindow.front;
)
