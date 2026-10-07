/*
QMW Integrated Resonant Interaction add-on.

Load after QuantumResonantMembraneV1.scd. Hilbert scattering paths are
continuous availability: they may color pitch, brightness, damping, position,
and coupling, but never inject amplitude. Only probability quanta admitted by
the Python Hilbert-current accumulator become plucks. This file is a sound and
display adapter; it never evolves rho or a GPE field.
*/
(
var root = "/qmw/resonant_interaction/v1";
var port = (~qriPort ? 17922).asInteger;
var measurementRoot = "/qmw/measure/v1";
var measurementPort = (~qriMeasurementPort ? 17876).asInteger;
var measurementSchema = "qmw.projective_measurement.osc.v1";
var measurementControlPort = (~qriMeasurementControlPort ? 17877).asInteger;
var preparationControlPort = (~qriPreparationControlPort ? 17878).asInteger;
var qhoRoot = "/qmw/qho/v1";
var qhoPort = (~qriQHOPort ? 17830).asInteger;
var qhoSchema = "qmw.qho.osc.v1.2";
var controlPort = ("QMW_PLUCK_CONTROL_PORT".getenv ? "17923").asInteger;
var temporalMemoryControlPort = ("QMW_TEMPORAL_MEMORY_CONTROL_PORT".getenv ? "0").asInteger;
var modeCount = 20;
var schema = "qmw.resonant_interaction.adapter.v2";
var recordingDir = "QMW_PERFORMANCE_RECORDING_DIR".getenv
    ? (thisProcess.nowExecutingPath.dirname.dirname.dirname
        +/+ "recordings/unified_instrument_v3");
var buildEventSynth, buildMiRingsEventSynth, buildMIVoiceSynths, defineSynths, defineMiRingsSynth, defineFXSynths, renderEvent, enqueueEvent, popEvent;
var eventBucketKey, queuedQuantumCount;
var releaseTemporalPluck, commitFrame, refreshPanel, openPolyrhythmControls, openVoiceAllocatorControls;
var drawTriplePlane, drawAvailability, drawProjective, drawSourceOverview, openPanel, closePanel;
var defineProjectiveSynths, rebuildProjectiveBody, pushProjectiveCalibration;
var openMeasurementControls, openProjectiveOutputs, openTemporalMemoryControls, refreshMeasurementControls;
var openPreparationControls, refreshPreparationControls, openMiRingsControls, openMiRingsSixControls;
var openMIVoiceControls, openFXControls, ensureCloudsReturn, ensureVSTReturn, ensureVSTRack, stopFXReturns;
var ensureCloudsProxy, ensureVSTRackReturnProxy;
var applyVSTRackRouting, updateVSTRackLatency, recallVSTRackSlotPreset;
var scanVSTPlugins, openVSTChooser, openVSTInRackSlot;
var listeningBaseline, fieldListeningBaseline, renderMiRingsSix;
var openQHOControls, refreshQHOControls, openChebyshevControls, refreshParsevalControls;
var styleMenu, styleSlider, styleNumberBox;
var panelColor = Color.fromHexString("11151c");
var fieldColor = Color.fromHexString("080b10");
var textColor = Color.white;
var mutedTextColor = Color.white;

// Qt's platform defaults can be black text even when the parent window is
// dark. Style every editable/menu/slider text surface explicitly so the
// instrument remains legible under both macOS light and dark appearances.
styleMenu = { |menu|
    menu.background_(fieldColor).stringColor_(textColor);
    menu
};
styleSlider = { |slider|
    slider.labelView.stringColor_(mutedTextColor);
    // QNumberBox switches between normalColor and typingColor; stringColor
    // alone is overwritten on the next value update or focus change.
    slider.numberView
        .normalColor_(textColor)
        .typingColor_(textColor)
        .stringColor_(textColor)
        .background_(fieldColor);
    slider.sliderView.background_(fieldColor);
    slider
};
styleNumberBox = { |box|
    box.background_(fieldColor)
        .normalColor_(textColor)
        .typingColor_(textColor)
        .stringColor_(textColor);
    box
};

~qriCleanup !? { ~qriCleanup.value };
thisProcess.openUDPPort(port);
thisProcess.openUDPPort(measurementPort);
thisProcess.openUDPPort(qhoPort);

~qriPort = port;
~qriMeasurementPort = measurementPort;
~qriMeasurementControlPort = measurementControlPort;
~qriControlPort = controlPort;
~qriControlAddress = NetAddr("127.0.0.1", controlPort);
~qriRecordingActive = false;
~qriRecordingReady = false;
~qriRecordingWavPath = nil;
~qriRecordingMusicXMLPath = nil;
~qriRecordingEventJSONPath = nil;
~qriRecordButton = nil;
~qriMainRecordButton = nil;
~qriAudioRecordButton = nil;
~qriRecordingStatus = nil;
~qriSyncRecordingButtons = {
    var value = if(~qriRecordingActive, { 1 }, { 0 });
    ~qriRecordButton !? { |button| button.value_(value) };
    ~qriMainRecordButton !? { |button| button.value_(value) };
    ~qriAudioRecordButton !? { |button| button.value_(value) };
};
~qriStartPerformanceRecording = {
    var takeId;
    if(s.serverRunning.not, {
        ~qriRecordingStatus !? { |view|
            view.string_("record failed: SuperCollider audio server is not running")
        };
        ~qriRecordingActive = false;
        ~qriSyncRecordingButtons.value;
    }, {
        if(s.isRecording, {
            ~qriRecordingStatus !? { |view|
                view.string_("record failed: the audio server is already recording")
            };
            ~qriRecordingActive = false;
            ~qriSyncRecordingButtons.value;
        }, {
            takeId = Date.localtime.stamp;
            recordingDir.mkdir;
            ~qriRecordingWavPath = recordingDir +/+
                ("qmw_unified_resonant_" ++ takeId ++ ".wav");
            ~qriRecordingMusicXMLPath = nil;
            ~qriRecordingEventJSONPath = nil;
            s.recHeaderFormat = "wav";
            s.recSampleFormat = "float";
            ~qriRecordingReady = false;
            ~qriRecordingActive = true;
            ~qriSyncRecordingButtons.value;
            ~qriRecordingStatus !? { |view|
                view.string_("arming stereo WAV + notation event capture...")
            };
            s.record(~qriRecordingWavPath, 0, 2);
            Routine({
                100.do {
                    if(s.isRecording.not) { 0.05.wait };
                };
                if(s.isRecording and: { ~qriRecordingActive }, {
                    ~qriRecordingReady = true;
                    ~qriControlAddress.sendMsg(*(
                        [
                            root ++ "/control/performance-record",
                            1,
                            takeId,
                            "QMW Unified Resonant Instrument",
                            ~qriRecordingWavPath,
                            (~qrmFundamental ? 72).asFloat,
                            ~qriMaximumVoiceDecay.value,
                            120.0
                        ] ++ (~qrmPitchRatios ? Array.fill(modeCount, 1.0))
                            .collect(_.asFloat)
                    ));
                    ~qriRecordingStatus !? { |view|
                        view.string_("RECORDING WAV + MUSICXML: "
                            ++ ~qriRecordingWavPath.basename)
                    };
                }, {
                    if(s.isRecording) { s.stopRecording };
                    ~qriRecordingReady = false;
                    ~qriRecordingActive = false;
                    ~qriSyncRecordingButtons.value;
                    ~qriRecordingStatus !? { |view|
                        view.string_("record failed: WAV recorder did not become ready")
                    };
                });
            }).play(AppClock);
        });
    });
};
~qriStopPerformanceRecording = {
    if(s.isRecording) { s.stopRecording };
    if(~qriRecordingReady) {
        ~qriControlAddress.sendMsg(root ++ "/control/performance-record", 0);
        ~qriRecordingStatus !? { |view|
            view.string_("WAV saved; finalizing MusicXML notation...")
        };
    } {
        ~qriRecordingStatus !? { |view|
            view.string_("recording stopped before notation capture became ready")
        };
    };
    ~qriRecordingReady = false;
    ~qriRecordingActive = false;
    ~qriSyncRecordingButtons.value;
};
~qriTogglePerformanceRecording = { |button|
    if(button.value == 1, {
        ~qriStartPerformanceRecording.value
    }, {
        ~qriStopPerformanceRecording.value
    });
};
~qriTemporalMemoryControlAddress = if(temporalMemoryControlPort > 0, {
    NetAddr("127.0.0.1", temporalMemoryControlPort)
}, { nil });
~qriMeasurementControlAddress = NetAddr("127.0.0.1", measurementControlPort);
~qriPreparationControlAddress = NetAddr("127.0.0.1", preparationControlPort);
~qriQHOControlAddress = NetAddr("127.0.0.1", 17831);
~qriEnabled = ~qriEnabled ? true;
// A dedicated performance launcher may request the deliberately small
// six-MiRings experiment. This changes downstream sound routing only.
~qriSimpleSixMiRings = (("QMW_SIMPLE_SIX_MIRINGS".getenv ? "0").asInteger > 0);
~qriMix = ~qriMix ? 0.55;
~qriEventGain = ~qriEventGain ? 0.75;
// Downstream sound-adapter trim. The admitted probability magnitude remains
// authoritative; this only restores useful acoustic level after the modal
// bank's normalization and the main/mix controls. The final limiter remains
// the safety boundary.
~qriPluckAudibilityGain = (~qriPluckAudibilityGain ? 64.0).clip(0, 128);
~qriDecay = ~qriDecay ? 0.34;
// Each mixer lane owns its audible lifetime. Older sessions had one global
// decay, so missing indices migrate to that value and preserve their sound.
~qriVoiceDecays = (~qriVoiceDecays ? []).asArray;
~qriVoiceDecays = Array.fill(8, { |index|
    (~qriVoiceDecays[index] ? ~qriDecay).asFloat.clip(0.02, 6.0)
});
// Manual values are the eight base parameters. A typed downstream matrix may
// publish separate effective values, while the safety ceiling remains at least
// as large as every possible routed value.
~qriEffectiveVoiceDecays = (~qriEffectiveVoiceDecays ? ~qriVoiceDecays).copy;
~qriVoiceDecaySafetyCeilings = (~qriVoiceDecaySafetyCeilings
    ? ~qriEffectiveVoiceDecays).copy;
~qriMaximumVoiceDecay = {
    (~qriVoiceDecaySafetyCeilings ? (~qriEffectiveVoiceDecays
        ? (~qriVoiceDecays ? [~qriDecay]))).collect(_.asFloat).maxItem
        .max(0.02).min(6.0)
};
~qriDecay = ~qriVoiceDecays.maxItem;
~qriBodyMode = (~qriBodyMode ? 0).asInteger.clip(0, 2);
~qriBodyModeNames = ["EVENT PLUCK", "FIELD", "HYBRID"];
~qriVoiceNames = ["Simple", "Gaussian", "Layered", "QHO FM", "LPG", "MiRings", "MiPlaits", "MiElements"];
// Explicit index-wise migration preserves existing scenes while making every
// newly adopted third-party lane safe and silent until its visible fader rises.
~qriVoiceGains = (~qriVoiceGains ? []).asArray;
~qriVoiceGains = Array.fill(8, { |index|
    (~qriVoiceGains[index] ? [1.0, 0.65, 0.55, 1.0, 0.55, 0.0, 0.0, 0.0][index])
        .asFloat.clip(0, 1.5)
});
~qriVoiceMutes = (~qriVoiceMutes ? []).asArray;
~qriVoiceMutes = Array.fill(8, { |index|
    (~qriVoiceMutes[index] ? 0).asInteger.clip(0, 1)
});
// Each pluck voice owns a downstream fuzz send.  This is deliberately a
// mixer/send control, never a change to event admission or density dynamics.
// ~qrmFuzzMix remains the field-body send for compatibility; pluck fuzz is
// intentionally sourced only from ~qriVoiceFuzzSends below.
~qriVoiceFuzzSends = (~qriVoiceFuzzSends ? []).asArray;
~qriVoiceFuzzSends = Array.fill(8, { |index|
    (~qriVoiceFuzzSends[index] ? 0.0).asFloat.clip(0, 1)
});
// Every admitted voice owns a post-resonator temporal-memory send, just as it
// owns a fuzz send.  This is audio routing only; it cannot alter QMW state.
~qriVoiceTemporalSends = (~qriVoiceTemporalSends ? []).asArray;
~qriVoiceTemporalSends = Array.fill(8, { |index|
    (~qriVoiceTemporalSends[index] ? 0.0).asFloat.clip(0, 1)
});
// One post-voice stereo send bus feeds downstream effects.  It is neither an
// event source nor a quantum feedback path.  Every send and both returns begin
// at zero, so dormant third-party DSP cannot create sound or consume CPU.
~qriVoiceFXSends = (~qriVoiceFXSends ? []).asArray;
~qriVoiceFXSends = Array.fill(8, { |index|
    (~qriVoiceFXSends[index] ? 0.0).asFloat.clip(0, 1)
});
// This is an audio send from admitted plucks into the independent temporal
// return bus. It is not an event-admission or quantum-state control.
~qriTemporalMemorySend = (~qriTemporalMemorySend ? 0.72).asFloat.clip(0, 1);
~qriHmiSend = (~qriHmiSend ? 0.0).asFloat.clip(0, 1);
// A complete pluck has five independently processed voices across twenty
// modes.  Two graphs retain the instrument's original overlapping-pluck
// Independent rhythmic lanes require modest overlap, but still have a strict
// server-side safety cap. This is downstream polyphony policy only; it never
// changes the QMW event stream.
~qriMaxVoices = (~qriMaxVoices ? 8).asInteger.clip(2, 8);
~qriShedPlucks = 0;
// The hard cap above remains the performer's ceiling. This adaptive budget is
// a downstream sound-allocation policy: it observes scsynth load and local
// scheduler pressure, changes only future node admission, and never edits or
// discards an authoritative QMW frame. Existing tails are never force-freed.
~qriAllocatorEnabled = ~qriAllocatorEnabled ? true;
~qriAllocatorMinVoices = (~qriAllocatorMinVoices ? 2).asInteger.clip(1, ~qriMaxVoices);
~qriAllocatorHeadroomTarget = (~qriAllocatorHeadroomTarget ? 45).asFloat.clip(20, 70);
~qriAllocatorCriticalPeakCPU = (~qriAllocatorCriticalPeakCPU ? 78).asFloat.clip(55, 95);
~qriAllocatorRecoverySeconds = (~qriAllocatorRecoverySeconds ? 4.0).asFloat.clip(1, 20);
~qriAllocatorAuxShedding = ~qriAllocatorAuxShedding ? true;
~qriAllocatorGainCompensation = ~qriAllocatorGainCompensation ? true;
~qriDynamicVoiceBudget = (~qriDynamicVoiceBudget ? ~qriMaxVoices).asInteger
    .clip(~qriAllocatorMinVoices, ~qriMaxVoices);
~qriAllocatorState = \nominal;
~qriAllocatorSmoothedCPU = 0.0;
~qriAllocatorPeakCPU = 0.0;
~qriAllocatorHealthyTicks = 0;
~qriAllocatorLastAdjustAt = -1e12;
~qriAllocatorLastPressureTotal = 0;
~qriAllocatorAuxShedVoices = 0;
~qriAllocatorRoutine = nil;
~qriAllocatorWindow = nil;
~qriAllocatorStatus = nil;
~qriMaxQueuedPlucks = 512;
~qriHistoryLength = 14;
~qriViewMode = (~qriViewMode ? 0).asInteger.clip(0, 3);
~qriFieldBody = (~qriFieldBody ? 0).asInteger.clip(0, 2);
~qriFieldBodyNames = ["20-MODE MEMBRANE", "16 PROJECTIVE RESONATORS", "BOTH"];
// FIELD is a continuous auxiliary layer, not a sixth pluck voice.  Keep it
// silent until the performer deliberately raises its own visible fader.
~qriFieldGain = (~qriFieldGain ? 0.0).asFloat.clip(0, 0.35);
// QRM's legacy crossing renderer bypasses this six-channel mixer. In the
// unified instrument it must remain off: all admitted events are rendered by
// QRI, so all-zero QRI faders genuinely silence the session.
~qrmCrossingAudioEnabled = false;
~qriProjectiveGain = ~qriProjectiveGain ? 0.12;
// mi-UGens is an optional GPL-3.0 SuperCollider extension.  Its resonator is
// a selectable sound adapter only; QMW remains the authority for state and
// event admission.  No extension means no MiRings SynthDef is made.
~qriMiRingsAvailable = \MiRings.asClass.notNil;
~qriMiRingsPitch = (~qriMiRingsPitch ? 54).asFloat.clip(24, 96);
~qriMiRingsStructure = (~qriMiRingsStructure ? 0.32).asFloat.clip(0, 1);
~qriMiRingsBrightness = (~qriMiRingsBrightness ? 0.56).asFloat.clip(0, 1);
~qriMiRingsDamping = (~qriMiRingsDamping ? 0.58).asFloat.clip(0, 1);
~qriMiRingsPosition = (~qriMiRingsPosition ? 0.28).asFloat.clip(0, 1);
~qriMiRingsModel = (~qriMiRingsModel ? 0).asInteger.clip(0, 6);
~qriMiRingsGain = (~qriMiRingsGain ? 0.14).asFloat.clip(0, 0.3);
~qriMiRingsNode = nil;
~qriMiRingsNodes = List.new;
~qriMiRingsWindow = nil;
~qriMiPlaitsAvailable = \MiPlaits.asClass.notNil;
~qriMiElementsAvailable = \MiElements.asClass.notNil;
~qriMiCloudsAvailable = \MiClouds.asClass.notNil;
~qriVSTAvailable = \VSTPlugin.asClass.notNil and: { \VSTPluginController.asClass.notNil };
~qriPlaitsEngine = (~qriPlaitsEngine ? 2).asInteger.clip(0, 23);
~qriPlaitsHarmonics = (~qriPlaitsHarmonics ? 0.50).asFloat.clip(0, 1);
~qriPlaitsTimbre = (~qriPlaitsTimbre ? 0.60).asFloat.clip(0, 1);
~qriPlaitsMorph = (~qriPlaitsMorph ? 0.45).asFloat.clip(0, 1);
~qriPlaitsDecay = (~qriPlaitsDecay ? 0.50).asFloat.clip(0, 1);
~qriElementsContour = (~qriElementsContour ? 0.36).asFloat.clip(0, 1);
~qriElementsBow = (~qriElementsBow ? 0.0).asFloat.clip(0, 1);
~qriElementsBlow = (~qriElementsBlow ? 0.0).asFloat.clip(0, 1);
~qriElementsStrike = (~qriElementsStrike ? 0.72).asFloat.clip(0, 1);
~qriElementsGeometry = (~qriElementsGeometry ? 0.32).asFloat.clip(0, 1);
~qriElementsBrightness = (~qriElementsBrightness ? 0.58).asFloat.clip(0, 1);
~qriElementsDamping = (~qriElementsDamping ? 0.64).asFloat.clip(0, 1);
~qriElementsSpace = (~qriElementsSpace ? 0.30).asFloat.clip(0, 1);
~qriElementsModel = (~qriElementsModel ? 0).asInteger.clip(0, 2);
~qriMIVoiceWindow = nil;
~qriMiVoiceNodes = List.new;
~qriFXWindow = nil;
~qriFXSendBus = nil;
~qriVoiceFXSendBus = nil;
~qriFXGroup = nil;
~qriFXProxyGroup = nil;
~qriCloudsNode = nil;
~qriFXProxyFadeTime = (~qriFXProxyFadeTime ? 0.08).asFloat.clip(0.01, 1.0);
~qriCloudsProxy = nil;
~qriCloudsProxyActive = false;
~qriVSTNode = nil;
~qriVSTController = nil;
~qriVSTAutoScanEnabled = ~qriVSTAutoScanEnabled ? true;
~qriVSTRackMaxSlots = 4;
~qriVSTRackSlotCount = (~qriVSTRackSlotCount ? 2).asInteger.clip(2, 4);
~qriVSTRackTopology = (~qriVSTRackTopology ? 0).asInteger.clip(0, 1);
~qriVSTRackReturn = (~qriVSTRackReturn ? (~qriVSTReturn ? 0.0)).asFloat.clip(0, 1);
~qriVSTRackBypasses = Array.fill(4, { |index|
    ((~qriVSTRackBypasses ? [])[index] ? 0).asInteger.clip(0, 1)
});
~qriVSTRackSlotGains = Array.fill(4, { |index|
    ((~qriVSTRackSlotGains ? [])[index] ? 1.0).asFloat.clip(0, 1.5)
});
~qriVSTRackLoaded = Array.fill(4, false);
~qriVSTRackLatencies = Array.fill(4, 0);
~qriVSTRackPluginKeys = Array.fill(4, { |index| (~qriVSTRackPluginKeys ? [])[index] });
~qriVSTRackPresetNames = Array.fill(4, { |index| (~qriVSTRackPresetNames ? [])[index] });
~qriVSTRackNodes = Array.newClear(4);
~qriVSTRackControllers = Array.newClear(4);
~qriVSTRackControllerDependants = Array.newClear(4);
~qriVSTRackPendingOpens = Array.newClear(4);
~qriVSTRackStageBuses = Array.newClear(4);
~qriVSTRackMixBus = nil;
~qriVSTRackOutputNode = nil;
~qriVSTRackReturnProxy = nil;
~qriVSTRackReturnInputBus = nil;
~qriVSTRackLatencySamples = 0;
~qriVSTRackStatusViews = Array.newClear(4);
~qriVSTRackPresetFields = Array.newClear(4);
~qriVSTRackChooserWindows = Array.newClear(4);
~qriCloudsReturn = (~qriCloudsReturn ? 0.0).asFloat.clip(0, 1);
~qriVSTReturn = ~qriVSTRackReturn;
~qriCloudsPitch = (~qriCloudsPitch ? 0.0).asFloat.clip(-48, 48);
~qriCloudsPosition = (~qriCloudsPosition ? 0.50).asFloat.clip(0, 1);
~qriCloudsSize = (~qriCloudsSize ? 0.45).asFloat.clip(0, 1);
~qriCloudsDensity = (~qriCloudsDensity ? 0.65).asFloat.clip(0, 1);
~qriCloudsTexture = (~qriCloudsTexture ? 0.50).asFloat.clip(0, 1);
~qriCloudsDryWet = (~qriCloudsDryWet ? 1.0).asFloat.clip(0, 1);
~qriCloudsInputGain = (~qriCloudsInputGain ? 1.0).asFloat.clip(0.125, 8);
~qriCloudsSpread = (~qriCloudsSpread ? 0.50).asFloat.clip(0, 1);
~qriCloudsReverb = (~qriCloudsReverb ? 0.20).asFloat.clip(0, 1);
~qriCloudsFeedback = (~qriCloudsFeedback ? 0.20).asFloat.clip(0, 1);
~qriCloudsFreeze = (~qriCloudsFreeze ? 0).asInteger.clip(0, 1);
~qriCloudsMode = (~qriCloudsMode ? 0).asInteger.clip(0, 3);
~qriCloudsLofi = (~qriCloudsLofi ? 0).asInteger.clip(0, 1);
// A deliberately simple alternate renderer: six parallel MiRings voices in
// one bounded Synth, owned by the existing six mixer faders. It is an opt-in
// sound adapter, never a second event source or a QMW-state operation.
~qriMiRingsSixEnabled = ~qriMiRingsSixEnabled ? false;
~qriMiRingsSixPitchOffsets = (~qriMiRingsSixPitchOffsets ? [0, 5, 7, 12, 16, 19])
    .collect(_.asFloat);
~qriMiRingsSixDecay = (~qriMiRingsSixDecay ? 0.42).asFloat.clip(0.08, 0.80);
~qriMiRingsSixNodes = List.new;
~qriMiRingsSixWindow = nil;
~qriProjectiveOutBase = (~qriProjectiveOutBase ? 0).asInteger.max(0);
~qriProjectiveGains = (~qriProjectiveGains ? Array.fill(16, 1.0)).copy;
~qriProjectiveMutes = (~qriProjectiveMutes ? Array.fill(16, 0)).copy;
~qriProjectiveDelays = (~qriProjectiveDelays ? Array.fill(16, 0.0)).copy;
~qriNodes = List.new;
~qriPluckQueue = List.new;
~qriPolyLaneCount = 16;
// Sixteen independent lane clocks are intentionally opt-in. The authoritative
// event stream is still available when they are off; enabling the observer is
// an explicit performance choice because it can multiply render attempts.
~qriPolyEnabled = ~qriPolyEnabled ? false;
~qriPolyBaseHz = (~qriPolyBaseHz ? 0.25).asFloat.clip(0.05, 1.5);
~qriPolyLaneChannels = [0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7];
~qriPolyRateMultipliers = (~qriPolyRateMultipliers ? []).asArray;
~qriPolyRateMultipliers = Array.fill(~qriPolyLaneCount, { |index|
    (~qriPolyRateMultipliers[index] ? [
        1.0, 1.25, 1.5, 1.75, 2.0, 0.75, 1.125, 1.375,
        1.625, 1.875, 2.125, 2.375, 0.875, 1.167, 1.333, 1.667
    ][index]).asFloat.clip(0.25, 3.0)
});
~qriPolyPhaseFractions = (~qriPolyPhaseFractions ? []).asArray;
~qriPolyPhaseFractions = Array.fill(~qriPolyLaneCount, { |index|
    (~qriPolyPhaseFractions[index] ? [
        0, 0.5, 0.25, 0.75, 0.125, 0.625, 1/3, 2/3,
        0.2, 0.4, 0.6, 0.8, 1/7, 3/7, 5/7, 6/7
    ][index]).asFloat.clip(0, 0.99)
});
~qriPolyLaneEnabled = (~qriPolyLaneEnabled ? []).asArray;
~qriPolyLaneEnabled = Array.fill(~qriPolyLaneCount, { |index|
    (~qriPolyLaneEnabled[index] ? 1).asInteger.clip(0, 1)
});
~qriPolyLatestEvent = nil;
// Lanes may repeat an admitted descriptor, but only while the upstream field
// is still supplying one. This prevents a stopped field from becoming an
// unintended free-running background layer.
~qriPolyLatestEventAt = -1e12;
~qriPolyLaneRoutines = Array.new;
~qriPolyGeneration = 0;
// QRM Bures records and admitted Hilbert plucks travel in separate atomic OSC
// transactions.  Hold an audio release for one coordinator interval so a
// record is not consumed before its already-authoritative event is enqueued.
~qriBuresReleaseLatency = 0.10;
~qriBuresRecordCount = 0;
~qriBuresReleasedCount = 0;
~qriBuresEmptyCount = 0;
// Bures records can arrive in an eight-pulse burst on one source frame.  A
// physical-model audition must not turn that frame detail into a burst of
// synth scheduling.  These are downstream sound-adapter counters only.
~qriBuresReleasePending = false;
~qriBuresLastScheduledAt = -1e12;
~qriBuresCoalescedRecords = 0;
// The native event graph is deliberately expensive: each admitted pluck owns
// twenty modes and five parallel voice paths. A fixed 10 Hz release cadence
// therefore becomes unsafe as the audible tail grows. Keep at most two
// general-renderer tails in the decay-aware admission budget; the existing
// qriMaxVoices remains the final hard cap for every clock mode.
~qriEventDecayScaleCeiling = 1.75;
~qriBuresTailOverlapBudget = (~qriBuresTailOverlapBudget ? 2).asInteger
    .clip(1, ~qriMaxVoices);
~qriBuresMinimumReleaseInterval = 0.10;
~qriBuresLongDecayThreshold = 0.50;
~qriBuresLastReleaseInterval = ~qriBuresMinimumReleaseInterval;
~qriBuresQueueCoalescedQuanta = 0;
// Every downstream clock, including the optional 16-lane observer, eventually
// reaches this one render seam. Above the reported failure boundary, enforce
// the same tail-overlap budget before allocating another expensive event graph.
~qriLongDecayLastRenderAt = -1e12;
~qriLongDecayRenderDrops = 0;
~qriCurrentVoiceBudget = {
    if(~qriAllocatorEnabled, {
        (~qriDynamicVoiceBudget ? ~qriMaxVoices).asInteger
            .clip(~qriAllocatorMinVoices, ~qriMaxVoices)
    }, { ~qriMaxVoices })
};
~qriCurrentMIVoiceBudget = {
    (~qriCurrentVoiceBudget.value * 2).asInteger.clip(2, ~qriMaxVoices * 2)
};
~qriCurrentTailOverlapBudget = {
    (~qriBuresTailOverlapBudget ? 2).asInteger
        .clip(1, ~qriCurrentVoiceBudget.value)
};
~qriRequestedAudibleRate = {
    if(~qriPolyEnabled, {
        Array.fill(~qriPolyLaneCount, { |index|
            if((~qriPolyLaneEnabled[index] ? 0) > 0, {
                ~qriPolyBaseHz * ~qriPolyRateMultipliers[index]
            }, { 0.0 })
        }).sum.max(0.01)
    }, {
        case
        { ~qrmTimeMode == 2 } { (~qrmFixedRate * ~qrmClockScale).max(0.01) }
        { ~qrmTimeMode == 3 } {
            (~qrmFixedRate * ~qrmClockScale
                * (~qrmEuclideanHits / ~qrmEuclideanSteps.max(1))).max(0.01)
        }
        { 0.0 }
    })
};
// Fixed/Euclidean and polyrhythmic timing retain their requested rhythm. If a
// requested rate cannot fit the current live-node budget, shorten only newly
// allocated audio tails instead of replacing the clock with a slower pulse.
~qriAllocatorTailScale = { |requestedScale=1.0|
    var rate, longestTail, allowedTail, capacityScale;
    requestedScale = requestedScale.asFloat.clip(0.02, ~qriEventDecayScaleCeiling);
    rate = ~qriRequestedAudibleRate.value;
    if(~qriAllocatorEnabled and: { rate > 0 }, {
        longestTail = ~qriMaximumVoiceDecay.value.max(0.02);
        // Native event nodes remain alive for 1.75 times their longest voice
        // envelope, so budget against the actual node lifetime, not merely
        // the audible decay parameter.
        allowedTail = (~qriCurrentVoiceBudget.value * 0.82 / (rate * 1.75)).max(0.02);
        capacityScale = (allowedTail / longestTail).clip(0.02, ~qriEventDecayScaleCeiling);
        requestedScale.min(capacityScale)
    }, { requestedScale })
};
~qriAllocatorAdmitAuxiliary = { |voiceIndex=(-1)|
    var allowed = (~qriAllocatorAuxShedding.not)
        or: { ~qriAllocatorState == \nominal }
        or: { ~qriAllocatorState == \manual }
        or: { voiceIndex >= 5 };
    if(allowed.not) {
        ~qriAllocatorAuxShedVoices = ~qriAllocatorAuxShedVoices + 1
    };
    allowed
};
~qriAllocatorAmplitudeScale = {
    var active;
    if(~qriAllocatorGainCompensation.not, { 1.0 }, {
        active = (~qriNodes.size + ~qriMiVoiceNodes.size + ~qriMiRingsNodes.size + 1).max(1);
        (1 / active.sqrt).clip(0.35, 1.0)
    })
};
~qriApplyAllocatorPolicy = {
    ~qriMaxVoices = (~qriMaxVoices ? 8).asInteger.clip(2, 8);
    ~qriAllocatorMinVoices = (~qriAllocatorMinVoices ? 2).asInteger.clip(1, ~qriMaxVoices);
    ~qriAllocatorHeadroomTarget = (~qriAllocatorHeadroomTarget ? 45).asFloat.clip(20, 70);
    ~qriAllocatorCriticalPeakCPU = (~qriAllocatorCriticalPeakCPU ? 78).asFloat.clip(55, 95);
    ~qriAllocatorRecoverySeconds = (~qriAllocatorRecoverySeconds ? 4).asFloat.clip(1, 20);
    ~qriDynamicVoiceBudget = if(~qriAllocatorEnabled, {
        (~qriDynamicVoiceBudget ? ~qriMaxVoices).asInteger
            .clip(~qriAllocatorMinVoices, ~qriMaxVoices)
    }, { ~qriMaxVoices });
};
// Optional arguments make this seam deterministic in the parser probe. Live
// operation reads scsynth's status watcher plus downstream queue/drop pressure.
~qriUpdateDynamicAllocator = { |avgOverride=nil, peakOverride=nil, queueOverride=nil, pressureOverride=nil|
    var telemetryAvailable, averageCPU, peakCPU, queueDepth, pressureTotal, pressureDelta;
    var averageCeiling, critical, warning, healthy, now, cooldown, recoveryTicks;
    telemetryAvailable = s.serverRunning or: { avgOverride.notNil };
    now = Main.elapsedTime;
    if(~qriAllocatorEnabled.not, {
        ~qriDynamicVoiceBudget = ~qriMaxVoices;
        ~qriAllocatorState = \manual;
        ~qriAllocatorHealthyTicks = 0;
    }, {
        if(telemetryAvailable.not, {
            ~qriDynamicVoiceBudget = ~qriMaxVoices;
            ~qriAllocatorState = \offline;
            ~qriAllocatorHealthyTicks = 0;
        }, {
            averageCPU = (avgOverride ? s.avgCPU ? 0).asFloat.clip(0, 100);
            peakCPU = (peakOverride ? s.peakCPU ? averageCPU).asFloat.clip(0, 100);
            queueDepth = (queueOverride ? ~qriPluckQueue.size).asInteger.max(0);
            pressureTotal = (pressureOverride ? (
                (~qriShedPlucks ? 0) + (~qriLongDecayRenderDrops ? 0)
                + (~qriBuresCoalescedRecords ? 0)
            )).asInteger.max(0);
            pressureDelta = (pressureTotal - ~qriAllocatorLastPressureTotal).max(0);
            ~qriAllocatorLastPressureTotal = pressureTotal;
            ~qriAllocatorSmoothedCPU = if(~qriAllocatorSmoothedCPU <= 0, {
                averageCPU
            }, { (~qriAllocatorSmoothedCPU * 0.78) + (averageCPU * 0.22) });
            ~qriAllocatorPeakCPU = peakCPU;
            averageCeiling = 100 - ~qriAllocatorHeadroomTarget;
            critical = (~qriAllocatorSmoothedCPU >= (averageCeiling + 10).min(92))
                or: { peakCPU >= ~qriAllocatorCriticalPeakCPU }
                or: { queueDepth >= 24 }
                or: { pressureDelta >= 4 };
            warning = critical.not and: {
                (~qriAllocatorSmoothedCPU >= averageCeiling)
                or: { peakCPU >= (~qriAllocatorCriticalPeakCPU - 10) }
                or: { queueDepth >= 12 }
                or: { pressureDelta > 0 }
            };
            healthy = critical.not and: { warning.not }
                and: { ~qriAllocatorSmoothedCPU <= (averageCeiling - 10).max(5) }
                and: { peakCPU < (~qriAllocatorCriticalPeakCPU - 15) }
                and: { queueDepth <= 2 }
                and: { pressureDelta == 0 };
            cooldown = now - ~qriAllocatorLastAdjustAt;
            if(critical, {
                ~qriAllocatorState = \protect;
                ~qriAllocatorHealthyTicks = 0;
                if(cooldown >= 0.5) {
                    ~qriDynamicVoiceBudget = (~qriDynamicVoiceBudget - 2)
                        .max(~qriAllocatorMinVoices);
                    ~qriAllocatorLastAdjustAt = now;
                };
            }, {
                if(warning, {
                    ~qriAllocatorState = \warning;
                    ~qriAllocatorHealthyTicks = 0;
                    if(cooldown >= 1.0) {
                        ~qriDynamicVoiceBudget = (~qriDynamicVoiceBudget - 1)
                            .max(~qriAllocatorMinVoices);
                        ~qriAllocatorLastAdjustAt = now;
                    };
                }, {
                    ~qriAllocatorState = \nominal;
                    ~qriAllocatorHealthyTicks = if(healthy, {
                        ~qriAllocatorHealthyTicks + 1
                    }, { 0 });
                    recoveryTicks = (~qriAllocatorRecoverySeconds / 0.5).ceil.asInteger.max(1);
                    if((~qriAllocatorHealthyTicks >= recoveryTicks) and: { cooldown >= 1.0 }) {
                        ~qriDynamicVoiceBudget = (~qriDynamicVoiceBudget + 1).min(~qriMaxVoices);
                        ~qriAllocatorHealthyTicks = 0;
                        ~qriAllocatorLastAdjustAt = now;
                    };
                });
            });
            ~qriDynamicVoiceBudget = ~qriDynamicVoiceBudget.asInteger
                .clip(~qriAllocatorMinVoices, ~qriMaxVoices);
        });
    });
    ~qriRefreshAllocatorControls !? { |refresh| { refresh.value }.defer };
    ~qriDynamicVoiceBudget
};
~qriAllocatorRoutine !? _.stop;
~qriAllocatorRoutine = Routine({
    loop {
        0.5.wait;
        ~qriUpdateDynamicAllocator.value;
    }
}).play(AppClock);
~qriEffectiveLongDecayRenderInterval = {
    var longestDecay = ~qriMaximumVoiceDecay.value;
    if(~qriMiRingsSixEnabled
        or: { longestDecay < ~qriBuresLongDecayThreshold }, {
        0.0
    }, {
        ((longestDecay * ~qriEventDecayScaleCeiling)
            / ~qriCurrentTailOverlapBudget.value)
            .max(~qriBuresMinimumReleaseInterval)
    })
};
~qriLongDecayRenderAvailable = {
    var interval = ~qriEffectiveLongDecayRenderInterval.value;
    (interval <= 0) or: {
        (Main.elapsedTime - ~qriLongDecayLastRenderAt) >= interval
    }
};
~qriAdmitLongDecayRender = {
    var admitted = ~qriLongDecayRenderAvailable.value;
    if(admitted, {
        if(~qriMaximumVoiceDecay.value >= ~qriBuresLongDecayThreshold) {
            ~qriLongDecayLastRenderAt = Main.elapsedTime
        };
    }, {
        ~qriLongDecayRenderDrops = ~qriLongDecayRenderDrops + 1
    });
    admitted
};
// GUI painting is a read-only observer. Four latest-state refreshes per second
// are responsive enough for the meter while avoiding 12+ heavy redraws/sec.
~qriDisplayRefreshHz = (~qriDisplayRefreshHz ? 4).asFloat.clip(1, 12);
~qriLastPanelRefreshAt = -1e12;
~qriPanelRefreshPending = false;
~qriFieldHistory = List.new;
~qriEnvelopeHistory = List.new;
~qriFrame = (
    revision: -1, time: 0.0, mapping: "",
    drives: Array.fill(modeCount, Complex(0, 0)),
    availability: Array.new, events: Array.new,
    threshold: 0.1, accumulatorPeak: 0.0, omegaScale: 1.0, authority: ""
);
~qriStage = nil;
~qriCompatible = false;
~qriMeasurementStage = nil;
~qriMeasurementCompatible = false;
~qriMeasurementFrame = (
    revision: -1, time: 0.0, bank: "", entropy: 0.0, dominant: 0,
    bankMode: "computational", pauli: "XYXY", aperture: "off",
    apertureRate: 1.0, gaugeFlux: 0.0, holonomy: 0.0,
    probabilities: Array.fill(16, 0.0), stateFlow: Array.fill(16, 0.0),
    apertureFlow: Array.fill(16, 0.0), totalFlow: Array.fill(16, 0.0)
);
~qriWindow = nil;
~qriDiagram = nil;
~qriModeView = nil;
~qriModeLabel = nil;
~qriStatus = nil;
~qriThresholdSlider = nil;
~qriOmegaSlider = nil;
~qriPerformanceControlPendingUntil = 0.0;
~qriRequestedPluckThreshold = (~qriFrame[\threshold] ? 0.1).asFloat.clip(0.005, 0.5);
// One downstream sound-adapter control owns event admission. Both the compact
// performance window and the full interaction window call this setter, while
// confirmed Python-authority frames update both views without re-sending OSC.
~qriSetPluckThreshold = { |value|
    var bounded = value.asFloat.clip(0.005, 0.5);
    ~qriRequestedPluckThreshold = bounded;
    ~qriPerformanceControlPendingUntil = Main.elapsedTime + 0.18;
    ~qriThresholdSlider !? { |view| view.value_(bounded) };
    ~qrmPerformancePluckThresholdSlider !? { |view| view.value_(bounded) };
    ~qriControlAddress !? { |address|
        address.sendMsg(
            "/qmw/resonant_interaction/v1/control/pluck_threshold", bounded
        )
    };
    bounded
};
~qriVoiceGainBus = nil;
~qriVoiceDecayBus = nil;
~qriVoiceFuzzSendBus = nil;
~qriVoiceTemporalSendBus = nil;
~qriVoiceFXSendBus = nil;
~qriProjectiveProbabilityBus = nil;
~qriProjectiveGainBus = nil;
~qriProjectiveDelayBus = nil;
~qriProjectiveBody = nil;
~qriFieldGroup = nil;
~qriMeasurementControlWindow = nil;
~qriProjectiveOutputWindow = nil;
~qriTemporalMemoryWindow = nil;
~qriPolyWindow = nil;
~qriPriorQrmSphereDrawFunc = nil;
~qriMeasurementDeltaP = 0.0;
~qriMeasurementBankMenu = nil;
~qriMeasurementPauliMenu = nil;
~qriMeasurementApertureMenu = nil;
~qriMeasurementRateSlider = nil;
~qriMeasurementFluxSlider = nil;
~qriMeasurementAckStatus = nil;
~qriMeasurementResponseStatus = nil;
~qriMeasurementControlPendingUntil = 0.0;
~qriPreparationWindow = nil;
~qriPreparationAckStatus = nil;
~qriPreparationModeMenu = nil;
~qriPreparationIndexSlider = nil;
~qriPreparationThetaSlider = nil;
~qriPreparationPhaseSlider = nil;
~qriPreparationSqueezeSlider = nil;
~qriPreparationSqueezePhaseSlider = nil;
~qriPreparationTemperatureSlider = nil;
~qriPreparationAwaitingAck = false;
~qriPreparationRequestedAfterRevision = -1;
~qriQHOWindow = nil;
~qriChebWindow = nil;
~qriQHOStage = nil;
~qriQHOCompatible = false;
~qriQHOMix = ~qriQHOMix ? 1.0;
~qriFMRatio = ~qriFMRatio ? 1.618;
~qriFMIndex = ~qriFMIndex ? 5.0;
~qriQHOPopulationBus = nil;
~qriQHOCoherenceMagnitudeBus = nil;
~qriQHOCoherencePhaseBus = nil;
~qriQHOBasisPopulationBus = nil;
~qriQHOMatrixPowerBus = nil;
~qriQHOMatrixPhaseBus = nil;
~qriFMControlBus = nil;
~qriChebControlBus = nil;
~qriParsevalControlBus = nil;
~qriQHOFrame = (
    revision: -1, time: 0.0, state: "coherent", fock: 3,
    alphaRe: 0.9, alphaIm: 0.0, thermal: 1.5,
    squeezeR: 0.55, squeezePhase: 0.0, omega: 1.0,
    meanN: 0.0, purity: 1.0, coherence: 0.0,
    populations: Array.fill(16, 0.0),
    coherence1Magnitudes: Array.fill(15, 0.0),
    coherence1Phases: Array.fill(15, 0.0),
    coherence2Magnitudes: Array.fill(14, 0.0),
    coherence2Phases: Array.fill(14, 0.0),
    basisPopulations: Array.fill(3, { Array.fill(16, 0.0) }),
    matrixPowerBins: Array.fill(16, 0.0),
    matrixPhaseBins: Array.fill(16, 0.0),
    parsevalTrace: 1.0, matrixPowerSum: 1.0, parsevalResidual: 0.0
);
// The Chebyshev stage is a downstream event exciter. It is silent by default,
// never schedules events, and never changes the canonical QHO or four-qubit
// states.  Mode 0 is a nonnegative contact-force envelope; mode 1 is an
// explicitly active signed actuator using T_n(cos(theta)) = cos(n theta).
~qriChebGain = (~qriChebGain ? 0.0).asFloat.clip(0, 1.5);
~qriChebMode = (~qriChebMode ? 0).asInteger.clip(0, 1);
~qriChebCalibration = (~qriChebCalibration ? 1).asInteger.clip(0, 1);
~qriChebContactSeconds = (~qriChebContactSeconds ? 0.012).asFloat.clip(0.001, 0.5);
~qriChebIncidence = (~qriChebIncidence ? 0.0).asFloat.clip(0, pi / 2);
~qriChebOrder = (~qriChebOrder ? 8).asInteger.clip(1, 16);
~qriChebCoherenceDepth = (~qriChebCoherenceDepth ? 1.0).asFloat.clip(0, 1);
~qriChebDecay = (~qriChebDecay ? 0.8).asFloat.clip(0.02, 6.0);
// Mode 0 holds the actuator carrier RMS while redistributing basis
// probabilities. Mode 1 deliberately preserves matrix-spectrum norm so its
// carrier RMS is targetRMS * sqrt(purity). Neither mode changes rho.
~qriParsevalMode = (~qriParsevalMode ? 0).asInteger.clip(0, 1);
~qriParsevalBasis = (~qriParsevalBasis ? 0).asInteger.clip(0, 2);
~qriParsevalTargetRMS = (~qriParsevalTargetRMS ? 0.18).asFloat.clip(0, 0.5);
~qriChebGainSlider = nil;
~qriChebModeMenu = nil;
~qriChebCalibrationMenu = nil;
~qriChebContactSlider = nil;
~qriChebIncidenceSlider = nil;
~qriChebOrderSlider = nil;
~qriChebCoherenceSlider = nil;
~qriChebDecaySlider = nil;
~qriParsevalModeMenu = nil;
~qriParsevalBasisMenu = nil;
~qriParsevalTargetRMSSlider = nil;
~qriParsevalMetrics = nil;
~qriParsevalSpectrumView = nil;
~qriQHOStateMenu = nil;
~qriQHOPopulationView = nil;
~qriQHOStatus = nil;
~qriQHOFockSlider = nil;
~qriQHOAlphaReSlider = nil;
~qriQHOAlphaImSlider = nil;
~qriQHOThermalSlider = nil;
~qriQHOSqueezeSlider = nil;
~qriQHOSqueezePhaseSlider = nil;
~qriQHOOmegaSlider = nil;
~qriFMDepthSlider = nil;
~qriFMRatioSlider = nil;
~qriFMIndexSlider = nil;
~qriQHOAwaitingAck = false;
~qriQHORequested = nil;

~qriEffectiveVoiceGains = {
    Array.fill(8, { |index|
        (~qriVoiceGains[index] ? 0.0).clip(0, 1.5)
            * (1 - (~qriVoiceMutes[index] ? 0).clip(0, 1))
    })
};

~qriPushVoiceGains = {
    ~qriVoiceGainBus !? { |bus| bus.setn(~qriEffectiveVoiceGains.value) };
};

~qriPushVoiceDecays = {
    ~qriEffectiveVoiceDecays = ~qriVoiceDecays.copy;
    ~qriVoiceDecaySafetyCeilings = ~qriEffectiveVoiceDecays.copy;
    ~qriVoiceDecayBus !? { |bus| bus.setn(~qriEffectiveVoiceDecays) };
};

~qriPushVoiceFuzzSends = {
    ~qriVoiceFuzzSendBus !? { |bus| bus.setn(~qriVoiceFuzzSends) };
};

~qriPushVoiceTemporalSends = {
    ~qriVoiceTemporalSendBus !? { |bus| bus.setn(~qriVoiceTemporalSends) };
};

~qriPushVoiceFXSends = {
    ~qriVoiceFXSendBus !? { |bus| bus.setn(~qriVoiceFXSends) };
};

~qriPushFMControls = {
    ~qriFMControlBus !? { |bus|
        bus.setn([~qriFMRatio, ~qriFMIndex, ~qriQHOMix])
    };
};

~qriPushParsevalControls = {
    ~qriParsevalControlBus !? { |bus|
        bus.setn([~qriParsevalMode, ~qriParsevalBasis, ~qriParsevalTargetRMS])
    };
    ~qriParsevalModeMenu !? { |view| view.value_(~qriParsevalMode) };
    ~qriParsevalBasisMenu !? { |view| view.value_(~qriParsevalBasis) };
    ~qriParsevalTargetRMSSlider !? { |view| view.value_(~qriParsevalTargetRMS) };
    refreshParsevalControls !? { |refresh| refresh.value };
};

~qriPushChebControls = {
    ~qriChebControlBus !? { |bus|
        bus.setn([
            ~qriChebGain, ~qriChebMode, ~qriChebCalibration,
            ~qriChebContactSeconds, ~qriChebIncidence, ~qriChebOrder,
            ~qriChebCoherenceDepth, ~qriChebDecay
        ])
    };
    ~qriChebGainSlider !? { |view| view.value_(~qriChebGain) };
    ~qriChebModeMenu !? { |view| view.value_(~qriChebMode) };
    ~qriChebCalibrationMenu !? { |view| view.value_(~qriChebCalibration) };
    ~qriChebContactSlider !? { |view| view.value_(~qriChebContactSeconds) };
    ~qriChebIncidenceSlider !? { |view| view.value_(~qriChebIncidence * 180 / pi) };
    ~qriChebOrderSlider !? { |view| view.value_(~qriChebOrder) };
    ~qriChebCoherenceSlider !? { |view| view.value_(~qriChebCoherenceDepth) };
    ~qriChebDecaySlider !? { |view| view.value_(~qriChebDecay) };
};

// A non-destructive sound-adapter check: it uses the currently published QHO
// populations but injects no measurement or state change.  The temporary
// single-voice mix makes FM Ratio, Index, and State Depth directly audible.
~qriAuditionQHOFM = {
    var event;
    if(~qriPlucksEnabled.value and: { ~qriVoiceGainBus.notNil }) {
        ~qriVoiceGainBus.setn([0, 0, 0, 1.5, 0, 0, 0, 0]);
        event = (
            energy: 0.42,
            weights: Array.fill(modeCount, { |index|
                (1 - ((index - 7).abs / 13)).clip(0.22, 1)
            }),
            phases: Array.fill(modeCount, { |index| index * 0.19 })
        );
        ~qriRenderEvent.(event, 1.0);
        AppClock.sched((~qriMaximumVoiceDecay.value.max(0.34) * 1.3) + 0.3, {
            ~qriPushVoiceGains.value; nil
        });
    } {
        "QHO-FM audition needs EVENT PLUCK or HYBRID body mode".postln;
    };
};

// A/B audition of only the new exciter.  It consumes the current published
// QHO frame and one synthetic downstream test event; no preparation,
// measurement, event-admission, or authoritative state is changed.
~qriAuditionChebyshev = {
    var event, auditionGain;
    if(~qriPlucksEnabled.value and: { ~qriVoiceGainBus.notNil }
        and: { ~qriChebControlBus.notNil }) {
        auditionGain = ~qriChebGain.max(0.9);
        ~qriVoiceGainBus.setn(Array.fill(8, 0));
        ~qriChebControlBus.setn([
            auditionGain, ~qriChebMode, ~qriChebCalibration,
            ~qriChebContactSeconds, ~qriChebIncidence, ~qriChebOrder,
            ~qriChebCoherenceDepth, ~qriChebDecay
        ]);
        event = (
            energy: 0.42, voiceIndex: 0, dominant: 7,
            weights: Array.fill(modeCount, { |index|
                exp(-0.5 * ((index - 7) / 3.2).squared)
            }),
            phases: Array.fill(modeCount, { |index| index * 0.11 })
        );
        ~qriRenderEvent.(event, 1.0);
        AppClock.sched((~qriChebDecay.max(~qriMaximumVoiceDecay.value) * 1.8) + 0.3, {
            ~qriPushVoiceGains.value;
            ~qriPushChebControls.value;
            nil
        });
    } {
        "Chebyshev audition needs EVENT PLUCK or HYBRID mode and a ready audio layer".warn;
    };
};

~qriPlucksEnabled = { ~qriBodyMode != 1 };
~qriApplyBodyMode = {
    var fieldGain = ~qriFieldGain.clip(0, 0.35);
    var fieldEnabled = if(~qriBodyMode == 0, { 0 }, { 1 });
    var membraneEnabled = fieldEnabled * if(~qriFieldBody == 1, { 0 }, { 1 });
    var projectiveEnabled = fieldEnabled * if(~qriFieldBody == 0, { 0 }, { 1 });
    ~qrmBody !? { |node|
        node.set(\bodyEnabled, membraneEnabled, \fieldGain, fieldGain)
    };
    ~qriProjectiveBody !? { |node|
        node.set(
            \enabled, projectiveEnabled,
            \master, (~qriProjectiveGain * fieldGain).clip(0, 0.5)
        )
    };
    if(~qriBodyMode == 1) { ~qriPluckQueue.clear };
    ~qriDiagram !? _.refresh;
};

pushProjectiveCalibration = {
    var effective = Array.fill(16, { |index|
        ~qriProjectiveGains[index].clip(0, 2)
            * (1 - ~qriProjectiveMutes[index].clip(0, 1))
    });
    ~qriProjectiveGainBus !? { |bus| bus.setn(effective) };
    ~qriProjectiveDelayBus !? { |bus| bus.setn(~qriProjectiveDelays.clip(0, 0.05)) };
};
// Public scene-recall seam: this touches only the existing downstream
// projective calibration buses. It never changes a measurement frame or QMW
// state.
~qriPushProjectiveCalibration = { pushProjectiveCalibration.value };

defineProjectiveSynths = {
    SynthDef(\qriProjectiveBody16V1, { |outBase=0, probabilityBus=0,
        gainBus=0, delayBus=0, master=0.12, enabled=0, fundamental=55|
        var probabilities = In.kr(probabilityBus, 16).clip(0, 1);
        var gains = In.kr(gainBus, 16).clip(0, 2);
        var delays = In.kr(delayBus, 16).clip(0, 0.05);
        var signals = Array.fill(16, { |index|
            var frequency = (fundamental * (1 + (index * 0.185))).clip(28, 12000);
            var amplitude = Lag.kr(probabilities[index].sqrt, 0.08)
                * gains[index] * master.clip(0, 0.5) * Lag.kr(enabled, 0.05);
            var partial = SinOsc.ar(frequency, index * 0.17, amplitude)
                + SinOsc.ar(frequency * 2.01, index * -0.11, amplitude * 0.18);
            // Calibration delay and limiting are independent per physical lane.
            Limiter.ar(DelayC.ar(LeakDC.ar(partial), 0.05, delays[index]), 0.82)
        });
        Out.ar(outBase, signals);
    }).add;
    SynthDef(\qriProjectiveBodyMonitorV1, { |out=0, probabilityBus=0,
        gainBus=0, master=0.12, enabled=0, fundamental=55|
        var probabilities = In.kr(probabilityBus, 16).clip(0, 1);
        var gains = In.kr(gainBus, 16).clip(0, 2);
        var signals = Array.fill(16, { |index|
            var frequency = (fundamental * (1 + (index * 0.185))).clip(28, 12000);
            SinOsc.ar(frequency, index * 0.17,
                Lag.kr(probabilities[index].sqrt, 0.08) * gains[index]
                * master.clip(0, 0.5) * Lag.kr(enabled, 0.05))
        });
        Out.ar(out, Limiter.ar(Splay.ar(signals, 0.92, 1 / 4), 0.82));
    }).add;
};

rebuildProjectiveBody = {
    var synthName, args, projectiveNode;
    ~qriProjectiveBody !? _.free; ~qriProjectiveBody = nil;
    // This continuous renderer must never be a child of qrmStrikeGroup:
    // qrmSonicReset deliberately freeAlls that transient event group.
    if(~qriFieldGroup.isNil or: { ~qriFieldGroup.isPlaying.not }, {
        ~qriFieldGroup = Group.after(~qrmBody ? s.defaultGroup).register;
    });
    ~qriProjectiveProbabilityBus !? _.free;
    ~qriProjectiveGainBus !? _.free;
    ~qriProjectiveDelayBus !? _.free;
    ~qriProjectiveProbabilityBus = Bus.control(s, 16);
    ~qriProjectiveGainBus = Bus.control(s, 16);
    ~qriProjectiveDelayBus = Bus.control(s, 16);
    ~qriProjectiveProbabilityBus.setn(~qriMeasurementFrame[\probabilities]);
    pushProjectiveCalibration.value;
    synthName = if((~qrmOutputChannels ? 2) >= 16,
        { \qriProjectiveBody16V1 }, { \qriProjectiveBodyMonitorV1 });
    args = [
        \probabilityBus, ~qriProjectiveProbabilityBus.index,
        \gainBus, ~qriProjectiveGainBus.index,
        \master, 0,
        \enabled, 0,
        \fundamental, ~qrmFundamental ? 55
    ];
    if(synthName == \qriProjectiveBody16V1) {
        args = args ++ [
            \delayBus, ~qriProjectiveDelayBus.index,
            \outBase, ~qriProjectiveOutBase
        ]
    } {
        args = args ++ [\out, 0]
    };
    projectiveNode = Synth(
        synthName, args, ~qriFieldGroup, \addToTail
    ).register;
    ~qriProjectiveBody = projectiveNode;
    projectiveNode.onFree({
        if(~qriProjectiveBody === projectiveNode) { ~qriProjectiveBody = nil };
    });
    ~qriApplyBodyMode.value;
};
~qriRebuildProjectiveBody = rebuildProjectiveBody;

// Build this only when mi-UGens has been installed and SuperCollider has
// recompiled its class library.  Looking the class up dynamically keeps the
// core instrument launchable on systems without the optional extension.
defineMiRingsSynth = {
    var miRingsClass = \MiRings.asClass;
    ~qriMiRingsAvailable = miRingsClass.notNil;
    if(miRingsClass.notNil, {
        SynthDef(\qriMiRingsAuditionV1, { |out=0, pitch=54, structure=0.32,
            brightness=0.56, damping=0.58, position=0.28, model=0, gain=0.14,
            decay=0.34, decayScale=1, voiceDecayBus=0,
            temporalSendBus=0, temporalSend=0, fxSendBus=0, fxSend=0|
            var decayBusValues = In.kr(voiceDecayBus, 8);
            var voiceDecay = (Select.kr(voiceDecayBus > 0,
                [decay, decayBusValues[5]]) * decayScale.clip(0.02, 1.75))
                .clip(0.02, 6.0);
            var strike = HPF.ar(PinkNoise.ar(0.26), 720)
                * Decay2.ar(Impulse.ar(0), 0.0007, 0.014);
            var lifetime = EnvGen.kr(
                Env.linen(0.001, (voiceDecay * 3.0).clip(0.25, 6.0), 0.16),
                doneAction: 2
            );
            var resonator = miRingsClass.perform(
                \ar, strike, 0, pitch.clip(24, 96), structure.clip(0, 1),
                brightness.clip(0, 1), damping.clip(0, 1), position.clip(0, 1),
                model.round.clip(0, 6), 1, 0, 0, 0
            );
            var emitted = Limiter.ar(
                LeakDC.ar(resonator) * lifetime * Lag.kr(gain.clip(0, 0.3), 0.03),
                0.62
            );
            // The audible MiRings graph is also the delay source. This keeps
            // its sixth mixer lane and temporal send truthful to one signal.
            Out.ar(out, emitted);
            Out.ar(temporalSendBus, emitted * Lag.kr(temporalSend.clip(0, 1), 0.03));
            Out.ar(fxSendBus, emitted * Lag.kr(fxSend.clip(0, 1), 0.03));
        }).add;
        // Six physical-model voices share one finite lifetime. This is much
        // lighter and more predictable than six independently accumulated
        // event graphs, while each existing mixer channel still owns one
        // audible MiRings voice, its mute, fuzz send, and delay send.
        SynthDef(\qriMiRingsSixV1, { |out=0, pitch=48, decay=0.42, decayScale=1,
            structure=0.32, brightness=0.56, damping=0.58, position=0.28,
            model=0, magnitude=0.35, voiceGainBus=0, voiceFuzzSendBus=0,
            voiceDecayBus=0,
            voiceTemporalSendBus=0, temporalSendBus=0,
            voiceFXSendBus=0, fxSendBus=0,
            fuzzDrive=8, fuzzBias=0.12, fuzzTone=5200|
            var offsets = NamedControl.kr(\pitchOffsets, [0, 5, 7, 12, 16, 19]);
            var gains = In.kr(voiceGainBus, 8).clip(0, 1.5);
            var decayBusValues = In.kr(voiceDecayBus, 8);
            var voiceDecays = Array.fill(6, { |index|
                (Select.kr(voiceDecayBus > 0, [decay, decayBusValues[index]])
                    * decayScale.clip(0.02, 1.75)).clip(0.08, 0.80)
            });
            var fuzzSends = Lag.kr(In.kr(voiceFuzzSendBus, 8).clip(0, 1), 0.03);
            var temporalSends = Lag.kr(In.kr(voiceTemporalSendBus, 8).clip(0, 1), 0.03);
            var fxSends = Lag.kr(In.kr(voiceFXSendBus, 8).clip(0, 1), 0.03);
            var lifetimes = voiceDecays.collect { |voiceDecay|
                EnvGen.kr(Env.perc(0.002, voiceDecay, 1, -5))
            };
            var nodeLifetime = EnvGen.kr(Env.linen(0,
                (voiceDecays.inject(0.02, { |maximum, item| maximum.max(item) }) * 1.15)
                    .clip(0.10, 0.96), 0.04), doneAction: 2);
            var drive = Lag.kr(fuzzDrive.clip(1, 32), 0.03);
            var bias = Lag.kr(fuzzBias.clip(-0.45, 0.45), 0.03);
            var voices = Array.fill(6, { |index|
                var strike = HPF.ar(PinkNoise.ar(0.24 + (index * 0.008)), 620 + (index * 75))
                    * Decay2.ar(Impulse.ar(0), 0.0007, 0.014 + (index * 0.001));
                var rings = miRingsClass.perform(
                    \ar, strike, 0, (pitch + offsets[index]).clip(24, 108),
                    structure.clip(0, 1), brightness.clip(0, 1), damping.clip(0, 1),
                    (position + (index * 0.11)).wrap(0, 1), model.round.clip(0, 6),
                    1, 0, 0, 0
                );
                var fuzzed = LPF.ar(
                    LeakDC.ar(((HPF.ar(rings, 24) * drive) + bias).tanh),
                    fuzzTone.clip(800, 12000)
                ) * 0.84;
                var voiced = XFade2.ar(rings, fuzzed, (fuzzSends[index] * 2) - 1);
                Pan2.ar(LeakDC.ar(voiced) * lifetimes[index] * nodeLifetime * gains[index]
                    * magnitude.clip(0, 1).sqrt * 0.105,
                    index.linlin(0, 5, -0.72, 0.72));
            });
            var emitted = Limiter.ar(Mix(voices), 0.72);
            Out.ar(out, emitted);
            Out.ar(temporalSendBus, Limiter.ar(Mix.fill(6, { |index|
                voices[index] * temporalSends[index]
            }), 0.72));
            Out.ar(fxSendBus, Limiter.ar(Mix.fill(6, { |index|
                voices[index] * fxSends[index]
            }), 0.72));
        }).add;
    });
};

~qriAuditionMiRings = { |gain, temporalSend, decayScale=1|
    var audibleGain = (gain ? ~qriMiRingsGain).asFloat.clip(0, 0.3);
    var audibleTemporalSend = (temporalSend ? (~qriVoiceTemporalSends[5] ? 0))
        .asFloat.clip(0, 1);
    var temporalBus = if(~qmwTemporalMemoryInputBus.notNil, {
        ~qmwTemporalMemoryInputBus.index
    }, { 0 });
    var fxBus = if(~qriFXSendBus.notNil, { ~qriFXSendBus.index }, { 0 });
    var node;
    if(~qriMiRingsAvailable, {
        if(~qriMiRingsNode.notNil and: { ~qriMiRingsNode.isPlaying ? false }) {
            ~qriMiRingsNode.free
        };
        node = Synth(\qriMiRingsAuditionV1, [
            \out, 0, \pitch, ~qriMiRingsPitch,
            \structure, ~qriMiRingsStructure,
            \brightness, ~qriMiRingsBrightness,
            \damping, ~qriMiRingsDamping,
            \position, ~qriMiRingsPosition,
            \model, ~qriMiRingsModel, \gain, audibleGain,
            \decay, ~qriVoiceDecays[5], \decayScale, decayScale,
            \voiceDecayBus, ~qriVoiceDecayBus.index,
            \temporalSendBus, temporalBus,
            \temporalSend, if(temporalBus > 0, { audibleTemporalSend }, { 0 }),
            \fxSendBus, fxBus,
            \fxSend, if(fxBus > 0, { ~qriVoiceFXSends[5] ? 0 }, { 0 })
        ], ~qrmStrikeGroup ? s.defaultGroup, \addToTail).register;
        ~qriMiRingsNode = node;
        node.onFree({
            if(~qriMiRingsNode === node) { ~qriMiRingsNode = nil };
        });
    }, {
        "MiRings is unavailable: install mi-UGens and recompile SuperCollider.".warn;
    });
};

// The blue audition SynthDef is the proven physical-model audio path. The
// sixth event lane deliberately uses that same graph, so the mixer cannot
// select a second, silently divergent MiRings implementation.
~qriAuditionMiRingsEvent = {
    var laneGain = (~qriEffectiveVoiceGains.value[5] ? 0).clip(0, 1.5);
    if(~qriMiRingsAvailable and: { ~qriPlucksEnabled.value }) {
        ~qriAuditionMiRings.value((laneGain * 0.14).clip(0, 0.3),
            ~qriVoiceTemporalSends[5] ? 0, 1);
        "QMW MiRings sixth-channel event audition fired".postln;
    } {
        "MiRings event audition needs EVENT PLUCK or HYBRID mode and mi-UGens.".warn;
    };
};

renderMiRingsSix = { |event, level=1.0|
    var node, energy, temporalBus;
    energy = (event[\energy] ? 0.0).asFloat.max(0) * level.squared;
    temporalBus = if(~qmwTemporalMemoryInputBus.notNil, {
        ~qmwTemporalMemoryInputBus.index
    }, { 0 });
    if(~qriMiRingsAvailable and: { ~qriEnabled }
        and: { ~qriPlucksEnabled.value } and: { ~qrmSonify ? false }
        and: { ~qrmAudioReady ? false } and: { energy > 0 }, {
        ~qriMiRingsSixNodes = ~qriMiRingsSixNodes.select { |active| active.isPlaying };
        // Exactly one six-voice graph may ring at a time. New strikes are
        // intentionally shed instead of force-freeing a tail, so the simple
        // experiment stays click-free and cannot flood the audio engine.
        if(~qriMiRingsSixNodes.isEmpty, {
            node = Synth(\qriMiRingsSixV1, [
                \out, 0, \pitch, ~qriMiRingsPitch,
                \pitchOffsets, ~qriMiRingsSixPitchOffsets,
                \decay, ~qriMiRingsSixDecay,
                \decayScale, (event[\decayScale] ? 1.0).asFloat,
                \voiceDecayBus, ~qriVoiceDecayBus.index,
                \structure, ~qriMiRingsStructure,
                \brightness, ~qriMiRingsBrightness,
                \damping, ~qriMiRingsDamping,
                \position, ~qriMiRingsPosition, \model, ~qriMiRingsModel,
                \magnitude, energy, \voiceGainBus, ~qriVoiceGainBus.index,
                \voiceFuzzSendBus, ~qriVoiceFuzzSendBus.index,
                \voiceTemporalSendBus, ~qriVoiceTemporalSendBus.index,
                \temporalSendBus, temporalBus,
                \voiceFXSendBus, ~qriVoiceFXSendBus.index,
                \fxSendBus, ~qriFXSendBus.index,
                \fuzzDrive, ~qrmFuzzDrive ? 8, \fuzzBias, ~qrmFuzzBias ? 0.12,
                \fuzzTone, ~qrmFuzzTone ? 5200
            ], ~qrmStrikeGroup ? s.defaultGroup, \addToTail);
            node.register;
            ~qriMiRingsSixNodes.add(node);
            node.onFree({ ~qriMiRingsSixNodes.remove(node) });
        }, {
            ~qriShedPlucks = ~qriShedPlucks + 1;
        });
    });
};

~qriActivateMiRingsSix = {
    if(~qriMiRingsAvailable, {
        ~qriMiRingsSixEnabled = true;
        ~qriPolyEnabled = false;
        ~qriStopPolyLanes !? { |stop| stop.value };
        ~qriBodyMode = 0;
        ~qriFieldGain = 0.0;
        ~qriVoiceGains = Array.fill(8, { |index| if(index < 6, { 0.78 }, { 0.0 }) });
        ~qriVoiceMutes = Array.fill(8, 0);
        ~qriVoiceFuzzSends = Array.fill(8, 0.0);
        ~qriVoiceTemporalSends = Array.fill(8, 0.0);
        ~qriVoiceFXSends = Array.fill(8, 0.0);
        ~qriMix = 0.55;
        ~qriEventGain = 0.75;
        // This is a fresh, isolated audition. Do not let a queue accumulated
        // by another timing mode spill into the one-graph MiRings renderer.
        ~qriPluckQueue.clear;
        ~qriBuresReleasePending = false;
        ~qriBuresLastScheduledAt = -1e12;
        ~qriPushVoiceGains.value;
        ~qriPushVoiceFuzzSends.value;
        ~qriPushVoiceTemporalSends.value;
        ~qriPushVoiceFXSends.value;
        ~qriApplyBodyMode.value;
        "QMW six MiRings voices active: one finite six-voice graph, existing mixer owns voices 1-6.".postln;
    }, {
        "Six MiRings voices requires mi-UGens. Recompile SuperCollider after installing it.".warn;
    });
};
~qriDisableMiRingsSix = {
    ~qriMiRingsSixEnabled = false;
    ~qriMiRingsSixNodes.do(_.free); ~qriMiRingsSixNodes.clear;
};

// One MiRings graph per admitted event, never one per membrane mode.  This
// keeps the physical-model voice bounded and gives it a normal mixer lane.
buildMiRingsEventSynth = { |miRingsClass|
    SynthDef(\qriMiRingsEventVoiceV1, { |out=0, fundamental=72, ratio=1,
        magnitude=0.003, decay=0.34, decayScale=1, master=0.16, eventGain=0.75,
        voiceGainBus=0, voiceFuzzSendBus=0, voiceTemporalSendBus=0,
        voiceDecayBus=0, temporalSendBus=0, temporalSendEnabled=0,
        voiceFXSendBus=0, fxSendBus=0,
        structure=0.32, brightness=0.56, damping=0.58, position=0.28, model=0,
        fuzzDrive=8, fuzzBias=0.12, fuzzTone=5200|
        var decayBusValues = In.kr(voiceDecayBus, 8);
        var voiceDecay = (Select.kr(voiceDecayBus > 0, [decay, decayBusValues[5]])
            * decayScale.clip(0.02, 1.75)).clip(0.02, 6.0);
        var voiceGain = In.kr(voiceGainBus, 8)[5].clip(0, 1.5);
        var fuzzSend = Lag.kr(In.kr(voiceFuzzSendBus, 8)[5].clip(0, 1), 0.03);
        var temporalSend = Lag.kr(In.kr(voiceTemporalSendBus, 8)[5].clip(0, 1), 0.03)
            * temporalSendEnabled.clip(0, 1);
        var fxSend = Lag.kr(In.kr(voiceFXSendBus, 8)[5].clip(0, 1), 0.03);
        var lifetime = EnvGen.kr(
            Env.linen(0.001, (voiceDecay * 3.0).clip(0.25, 6.0), 0.12), doneAction: 2
        );
        var strike = HPF.ar(PinkNoise.ar(0.28), 720)
            * Decay2.ar(Impulse.ar(0), 0.0007, 0.016);
        var rings = miRingsClass.perform(
            \ar, strike, 0, (fundamental * ratio).clip(24, 12000),
            structure.clip(0, 1), brightness.clip(0, 1), damping.clip(0, 1),
            position.clip(0, 1), model.round.clip(0, 6), 1, 0, 0, 0
        );
        var drive = Lag.kr(fuzzDrive.clip(1, 32), 0.03);
        var bias = Lag.kr(fuzzBias.clip(-0.45, 0.45), 0.03);
        var fuzzed = LPF.ar(
            LeakDC.ar(((HPF.ar(rings, 24) * drive) + bias).tanh),
            fuzzTone.clip(800, 12000)
        ) * 0.86;
        var voiced = XFade2.ar(rings, fuzzed, (fuzzSend * 2) - 1);
        // A physical-model lane renders one resonator, while the native event
        // bank renders twenty. Its visible channel fader therefore owns the
        // audible level directly; it is event-gated but does not inherit the
        // native bank's 20-way normalization or disappear behind its master.
        var emitted = Limiter.ar(
            voiced * lifetime * (0.35 + (magnitude.clip(0, 1).sqrt * 0.65))
            * 0.22 * voiceGain,
            0.72
        );
        Out.ar(out, emitted);
        // The sixth voice sends its post-resonator/post-fuzz signal only;
        // this is audio routing, not an event or state feedback path.
        Out.ar(temporalSendBus, emitted * temporalSend);
        Out.ar(fxSendBus, emitted * fxSend);
    }).add;
};

// Plaits and Elements are bounded, one-graph-per-admitted-event sound
// adapters.  Their pitch and amplitude are derived from the already admitted
// descriptor; neither UGen can write back into QMW state or event admission.
buildMIVoiceSynths = {
    var plaitsClass = \MiPlaits.asClass;
    var elementsClass = \MiElements.asClass;
    ~qriMiPlaitsAvailable = plaitsClass.notNil;
    ~qriMiElementsAvailable = elementsClass.notNil;
    if(plaitsClass.notNil, {
        SynthDef(\qriMiPlaitsEventV1, { |out=0, fundamental=72, ratio=1,
            magnitude=0.003, decay=0.34, decayScale=1, voiceGainBus=0,
            voiceDecayBus=0, voiceFuzzSendBus=0,
            voiceTemporalSendBus=0, temporalSendBus=0, voiceFXSendBus=0, fxSendBus=0,
            engine=2, harmonics=0.5, timbre=0.6, morph=0.45, plaitsDecay=0.5,
            fuzzDrive=8, fuzzBias=0.12, fuzzTone=5200|
            var decayBusValues = In.kr(voiceDecayBus, 8);
            var voiceDecay = (Select.kr(voiceDecayBus > 0, [decay, decayBusValues[6]])
                * decayScale.clip(0.02, 1.75)).clip(0.02, 6.0);
            var gain = In.kr(voiceGainBus, 8)[6].clip(0, 1.5);
            var fuzzSend = Lag.kr(In.kr(voiceFuzzSendBus, 8)[6].clip(0, 1), 0.03);
            var temporalSend = Lag.kr(In.kr(voiceTemporalSendBus, 8)[6].clip(0, 1), 0.03);
            var fxSend = Lag.kr(In.kr(voiceFXSendBus, 8)[6].clip(0, 1), 0.03);
            var gate = Trig1.kr(Impulse.kr(0), 0.012);
            var lifetime = EnvGen.kr(Env.perc(0.002,
                (voiceDecay * 1.6).clip(0.08, 6), 1, -5), doneAction: 2);
            var source = plaitsClass.perform(\ar,
                (fundamental * ratio).clip(28, 12000).cpsmidi,
                engine.round.clip(0, 23), harmonics.clip(0, 1), timbre.clip(0, 1),
                morph.clip(0, 1), gate, 1, 0, 0, 0,
                plaitsDecay.clip(0, 1), timbre.clip(0, 1)
            );
            var drive = Lag.kr(fuzzDrive.clip(1, 32), 0.03);
            var bias = Lag.kr(fuzzBias.clip(-0.45, 0.45), 0.03);
            var fuzzed = LPF.ar(LeakDC.ar(((HPF.ar(source, 24) * drive) + bias).tanh),
                fuzzTone.clip(800, 12000)) * 0.84;
            var emitted = Limiter.ar(XFade2.ar(source, fuzzed, (fuzzSend * 2) - 1)
                * lifetime * (0.28 + (magnitude.clip(0, 1).sqrt * 0.72))
                * gain * 0.18, 0.72);
            Out.ar(out, emitted);
            Out.ar(temporalSendBus, emitted * temporalSend);
            Out.ar(fxSendBus, emitted * fxSend);
        }).add;
    });
    if(elementsClass.notNil, {
        SynthDef(\qriMiElementsEventV1, { |out=0, fundamental=72, ratio=1,
            magnitude=0.003, decay=0.34, decayScale=1, voiceGainBus=0,
            voiceDecayBus=0, voiceFuzzSendBus=0,
            voiceTemporalSendBus=0, temporalSendBus=0, voiceFXSendBus=0, fxSendBus=0,
            contour=0.36, bow=0, blow=0, strike=0.72, geometry=0.32,
            brightness=0.58, damping=0.64, space=0.30, model=0,
            fuzzDrive=8, fuzzBias=0.12, fuzzTone=5200|
            var decayBusValues = In.kr(voiceDecayBus, 8);
            var voiceDecay = (Select.kr(voiceDecayBus > 0, [decay, decayBusValues[7]])
                * decayScale.clip(0.02, 1.75)).clip(0.02, 6.0);
            var gain = In.kr(voiceGainBus, 8)[7].clip(0, 1.5);
            var fuzzSend = Lag.kr(In.kr(voiceFuzzSendBus, 8)[7].clip(0, 1), 0.03);
            var temporalSend = Lag.kr(In.kr(voiceTemporalSendBus, 8)[7].clip(0, 1), 0.03);
            var fxSend = Lag.kr(In.kr(voiceFXSendBus, 8)[7].clip(0, 1), 0.03);
            var gate = Trig1.kr(Impulse.kr(0), 0.014);
            var lifetime = EnvGen.kr(Env.linen(0.002,
                (voiceDecay * 2.4).clip(0.16, 6), 0.12), doneAction: 2);
            var source = elementsClass.perform(\ar,
                0, 0, gate, (fundamental * ratio).clip(28, 12000).cpsmidi,
                magnitude.clip(0, 1).sqrt, contour.clip(0, 1), bow.clip(0, 1),
                blow.clip(0, 1), strike.clip(0, 1), 0.5, 0.5, 0.5, 0.5, 0.5,
                geometry.clip(0, 1), brightness.clip(0, 1), damping.clip(0, 1),
                0.28, space.clip(0, 1), model.round.clip(0, 2), 0
            );
            var drive = Lag.kr(fuzzDrive.clip(1, 32), 0.03);
            var bias = Lag.kr(fuzzBias.clip(-0.45, 0.45), 0.03);
            var fuzzed = LPF.ar(LeakDC.ar(((HPF.ar(source, 24) * drive) + bias).tanh),
                fuzzTone.clip(800, 12000)) * 0.84;
            var emitted = Limiter.ar(XFade2.ar(source, fuzzed, (fuzzSend * 2) - 1)
                * lifetime * gain * 0.16, 0.72);
            Out.ar(out, emitted);
            Out.ar(temporalSendBus, emitted * temporalSend);
            Out.ar(fxSendBus, emitted * fxSend);
        }).add;
    });
};

defineFXSynths = {
    var cloudsClass = \MiClouds.asClass;
    var vstClass = \VSTPlugin.asClass;
    ~qriMiCloudsAvailable = cloudsClass.notNil;
    ~qriVSTAvailable = vstClass.notNil and: { \VSTPluginController.asClass.notNil };
    if(cloudsClass.notNil, {
        SynthDef(\qriMiCloudsReturnV1, { |inBus=0, out=0, returnGain=0,
            pit=0, pos=0.5, size=0.45, dens=0.65, tex=0.5, drywet=1,
            inGain=1, spread=0.5, rvb=0.2, fb=0.2, freeze=0, mode=0,
            lofi=0, trig=0|
            var source = In.ar(inBus, 2);
            var wet = cloudsClass.perform(\ar, source, pit.clip(-48, 48), pos.clip(0, 1),
                size.clip(0, 1), dens.clip(0, 1), tex.clip(0, 1), drywet.clip(0, 1),
                inGain.clip(0.125, 8), spread.clip(0, 1), rvb.clip(0, 1), fb.clip(0, 1),
                freeze.clip(0, 1), mode.round.clip(0, 3), lofi.clip(0, 1),
                Trig1.kr(trig, 0.001));
            Out.ar(out, Limiter.ar(wet * Lag.kr(returnGain.clip(0, 1), 0.04), 0.78));
        }).add;
    });
    if(vstClass.notNil, {
        // One stable UGen per slot lets the performer change topology without
        // unloading plugins. In serial mode an empty, inactive, or bypassed
        // slot is unity pass-through. In parallel mode it contributes silence.
        SynthDef(\qriVSTRackSlotV1, { |inBus=0, outBus=0, bypass=0,
            active=0, parallel=0, slotGain=1, alignDelay=0|
            var source = In.ar(inBus, 2);
            var processed = vstClass.perform(\ar, source, 2, bypass.clip(0, 1));
            var engaged = active.clip(0, 1) * (1 - bypass.clip(0, 1));
            var serialSignal = XFade2.ar(source, processed * Lag.kr(slotGain.clip(0, 1.5), 0.04),
                (engaged * 2) - 1);
            var parallelSignal = DelayC.ar(processed * engaged
                * Lag.kr(slotGain.clip(0, 1.5), 0.04), 4,
                Lag.kr(alignDelay.clip(0, 4), 0.04));
            Out.ar(outBus, Select.ar(parallel.clip(0, 1), [serialSignal, parallelSignal]));
        }).add;
        SynthDef(\qriVSTRackOutputV1, { |inBus=0, out=0, returnGain=0|
            var signal = In.ar(inBus, 2) * Lag.kr(returnGain.clip(0, 1), 0.04);
            Out.ar(out, Limiter.ar(signal, 0.78));
        }).add;
    });
};

// Persistent, explicitly owned JITLib shells keep return buses and output
// monitors stable while their DSP graphs are replaced with a short crossfade.
// Plugin instances themselves remain VSTPluginControllers because they own
// editor, preset, crash, and latency state that NodeProxy must not obscure.
ensureCloudsProxy = {
    var proxy, cloudsClass = \MiClouds.asClass;
    var sendBusIndex;
    if(cloudsClass.notNil and: { ~qriFXSendBus.notNil }
        and: { ~qriFXProxyGroup.notNil }, {
        sendBusIndex = ~qriFXSendBus.index;
        proxy = ~qriCloudsProxy;
        if(proxy.isNil, {
            proxy = NodeProxy.audio(s, 2);
            proxy.parentGroup = ~qriFXProxyGroup;
            proxy.fadeTime = ~qriFXProxyFadeTime;
            proxy.source = { Silent.ar(2) };
            proxy.play(0, 2, ~qriFXProxyGroup, false, 1.0,
                ~qriFXProxyFadeTime, \addToTail);
            ~qriCloudsProxy = proxy;
            ~qriCloudsProxyActive = false;
        });
        if(~qriCloudsReturn > 0.0001, {
            if(~qriCloudsProxyActive.not, {
                // Capturing only the stable bus index lets the proxy rebuild
                // the MiClouds graph without replacing the monitor or bus.
                proxy.source = { |returnGain=0, pit=0, pos=0.5, size=0.45,
                    dens=0.65, tex=0.5, drywet=1, inGain=1, spread=0.5,
                    rvb=0.2, fb=0.2, freeze=0, mode=0, lofi=0, trig=0|
                    var source = In.ar(sendBusIndex, 2);
                    var wet = cloudsClass.perform(\ar, source,
                        pit.clip(-48, 48), pos.clip(0, 1), size.clip(0, 1),
                        dens.clip(0, 1), tex.clip(0, 1), drywet.clip(0, 1),
                        inGain.clip(0.125, 8), spread.clip(0, 1), rvb.clip(0, 1),
                        fb.clip(0, 1), freeze.clip(0, 1), mode.round.clip(0, 3),
                        lofi.clip(0, 1), Trig1.kr(trig, 0.001));
                    Limiter.ar(wet * Lag.kr(returnGain.clip(0, 1), 0.04), 0.78)
                };
                ~qriCloudsProxyActive = true;
            });
            proxy.set(\returnGain, ~qriCloudsReturn,
                \pit, ~qriCloudsPitch, \pos, ~qriCloudsPosition,
                \size, ~qriCloudsSize, \dens, ~qriCloudsDensity,
                \tex, ~qriCloudsTexture, \drywet, ~qriCloudsDryWet,
                \inGain, ~qriCloudsInputGain, \spread, ~qriCloudsSpread,
                \rvb, ~qriCloudsReverb, \fb, ~qriCloudsFeedback,
                \freeze, ~qriCloudsFreeze, \mode, ~qriCloudsMode,
                \lofi, ~qriCloudsLofi);
        }, {
            if(~qriCloudsProxyActive, {
                proxy.set(\returnGain, 0);
                proxy.source = { Silent.ar(2) };
                ~qriCloudsProxyActive = false;
            });
        });
        // Compatibility alias for existing control and audition callbacks.
        ~qriCloudsNode = proxy;
    });
};
~qriEnsureCloudsProxy = ensureCloudsProxy;

ensureVSTRackReturnProxy = { |inBus|
    var proxy = ~qriVSTRackReturnProxy;
    var inputIndex = inBus.asInteger;
    if(~qriFXProxyGroup.notNil, {
        if(proxy.isNil, {
            proxy = NodeProxy.audio(s, 2);
            proxy.parentGroup = ~qriFXProxyGroup;
            proxy.fadeTime = ~qriFXProxyFadeTime;
            proxy.source = { Silent.ar(2) };
            proxy.play(0, 2, ~qriFXProxyGroup, false, 1.0,
                ~qriFXProxyFadeTime, \addToTail);
            ~qriVSTRackReturnProxy = proxy;
            ~qriVSTRackReturnInputBus = nil;
        });
        if(~qriVSTRackReturnInputBus != inputIndex, {
            proxy.source = { |returnGain=0|
                var signal = In.ar(inputIndex, 2)
                    * Lag.kr(returnGain.clip(0, 1), 0.04);
                Limiter.ar(signal, 0.78)
            };
            ~qriVSTRackReturnInputBus = inputIndex;
        });
        proxy.set(\returnGain, ~qriVSTRackReturn);
        ~qriVSTRackOutputNode = proxy;
    });
};
~qriEnsureVSTRackReturnProxy = ensureVSTRackReturnProxy;

ensureCloudsReturn = {
    if(~qriMiCloudsAvailable and: { ~qriFXSendBus.notNil }, {
        ensureCloudsProxy.value;
    });
};
~qriUpdateCloudsReturn = ensureCloudsReturn;
~qriTriggerClouds = {
    ensureCloudsReturn.value;
    ~qriCloudsNode !? { |node|
        node.set(\trig, 1); AppClock.sched(0.02, { node.set(\trig, 0); nil })
    };
};

~qriRefreshVSTRackStatus = {
    var topologyName = if(~qriVSTRackTopology == 0, { "SERIAL" }, { "PARALLEL" });
    // Controller dependants and latency callbacks arrive on the OSC/SystemClock
    // thread. Qt views must only be touched on AppClock.
    {
        ~qriVSTStatus !? { |view|
            view.string_("% slots / % / % samples (% ms)"
                .format(~qriVSTRackSlotCount, topologyName, ~qriVSTRackLatencySamples,
                    ((~qriVSTRackLatencySamples / (s.sampleRate ? 48000).max(1)) * 1000).round(0.01)))
        };
        4.do { |index|
            var view = ~qriVSTRackStatusViews[index];
            var controller = ~qriVSTRackControllers[index];
            var pluginName = "EMPTY";
            if(controller.notNil and: { controller.info.notNil }, {
                pluginName = controller.info.name.asString
            });
            view !? { |status|
                status.string_("SLOT %  %  /  % smp".format(index + 1, pluginName,
                    ~qriVSTRackLatencies[index] ? 0))
            };
        };
    }.defer;
};

applyVSTRackRouting = {
    var parallel = ~qriVSTRackTopology.clip(0, 1);
    var count = ~qriVSTRackSlotCount.clip(2, 4);
    var activeLatencies = Array.fill(count, { |index|
        if((~qriVSTRackLoaded[index] ? false) and: { (~qriVSTRackBypasses[index] ? 0) == 0 }, {
            ~qriVSTRackLatencies[index] ? 0
        }, { 0 })
    });
    var maxLatency = activeLatencies.maxItem ? 0;
    var sampleRate = (s.sampleRate ? 48000).max(1);
    if(~qriVSTRackNodes.notNil and: { ~qriFXSendBus.notNil }, {
        4.do { |index|
            var node = ~qriVSTRackNodes[index];
            var inBus = if(parallel == 1, { ~qriFXSendBus.index }, {
                if(index == 0, { ~qriFXSendBus.index }, { ~qriVSTRackStageBuses[index - 1].index })
            });
            var outBus = if(parallel == 1, { ~qriVSTRackMixBus.index }, {
                ~qriVSTRackStageBuses[index].index
            });
            var active = ((index < count) and: { ~qriVSTRackLoaded[index] ? false }).asInteger;
            var alignDelay = if(parallel == 1 and: { index < count }, {
                (maxLatency - (~qriVSTRackLatencies[index] ? 0)).max(0) / sampleRate
            }, { 0 });
            node !? { |slot|
                slot.set(\inBus, inBus, \outBus, outBus,
                    \bypass, ~qriVSTRackBypasses[index] ? 0,
                    \active, active, \parallel, parallel,
                    \slotGain, ~qriVSTRackSlotGains[index] ? 1,
                    \alignDelay, alignDelay)
            };
        };
        ~qriVSTRackLatencySamples = if(parallel == 1, { maxLatency }, {
            activeLatencies.sum
        });
        ensureVSTRackReturnProxy.value(if(parallel == 1,
            { ~qriVSTRackMixBus.index },
            { ~qriVSTRackStageBuses[count - 1].index }
        ));
        ~qriVSTReturn = ~qriVSTRackReturn;
        ~qriRefreshVSTRackStatus.value;
    });
};
~qriApplyVSTRackRouting = applyVSTRackRouting;

updateVSTRackLatency = { |index, samples=0|
    ~qriVSTRackLatencies[index] = samples.asInteger.max(0);
    applyVSTRackRouting.value;
};

ensureVSTRack = {
    var controllerClass = \VSTPluginController.asClass;
    if(~qriVSTAvailable and: { ~qriFXSendBus.notNil } and: { ~qriFXGroup.notNil }, {
        4.do { |index|
            if(~qriVSTRackStageBuses[index].isNil, {
                ~qriVSTRackStageBuses[index] = Bus.audio(s, 2)
            });
        };
        if(~qriVSTRackMixBus.isNil, { ~qriVSTRackMixBus = Bus.audio(s, 2) });
        4.do { |index|
            if(~qriVSTRackNodes[index].isNil or: { ~qriVSTRackNodes[index].isPlaying.not }, {
                var node = Synth(\qriVSTRackSlotV1,
                    [\inBus, ~qriFXSendBus.index, \outBus, ~qriVSTRackStageBuses[index].index,
                        \bypass, ~qriVSTRackBypasses[index], \active, 0,
                        \parallel, ~qriVSTRackTopology, \slotGain, ~qriVSTRackSlotGains[index]],
                    ~qriFXGroup, \addToTail).register;
                var controller = controllerClass.perform(\new, node);
                var dependant = { |object, what ...args|
                    if(what == \open, {
                        ~qriVSTRackLoaded[index] = args[1] ? false;
                        if(~qriVSTRackLoaded[index], {
                            ~qriVSTRackPluginKeys[index] = object.info.key;
                            ~qriVSTRackLatencies[index] = object.latency ? 0;
                        });
                        applyVSTRackRouting.value;
                    });
                    if(what == \close or: { what == \crashed } or: { what == \free }, {
                        ~qriVSTRackLoaded[index] = false;
                        ~qriVSTRackLatencies[index] = 0;
                        applyVSTRackRouting.value;
                    });
                    if(what == \close, {
                        ~qriVSTRackPendingOpens[index] !? { |pending|
                            ~qriVSTRackPendingOpens[index] = nil;
                            AppClock.sched(0.02, { pending.value; nil });
                        };
                    });
                    if(what == \latency, { updateVSTRackLatency.(index, args[0] ? 0) });
                    if(what == \preset_save or: { what == \preset_load }, {
                        object.preset !? { |preset|
                            ~qriVSTRackPresetNames[index] = preset.name.asString;
                            {
                                ~qriVSTRackPresetFields[index] !? { |field|
                                    field.string_(preset.name.asString)
                                };
                            }.defer;
                        };
                    });
                };
                controller.latencyChanged = { |samples| updateVSTRackLatency.(index, samples ? 0) };
                controller.addDependant(dependant);
                ~qriVSTRackNodes[index] = node;
                ~qriVSTRackControllers[index] = controller;
                ~qriVSTRackControllerDependants[index] = dependant;
            });
        };
        // Compatibility aliases expose slot one to older local performance code.
        ~qriVSTNode = ~qriVSTRackNodes[0];
        ~qriVSTController = ~qriVSTRackControllers[0];
        applyVSTRackRouting.value;
    });
};
~qriEnsureVSTRack = ensureVSTRack;

scanVSTPlugins = { |statusView, completion|
    var pluginClass = \VSTPlugin.asClass;
    if(pluginClass.isNil, {
        statusView !? { |view| view.string_("VSTPlugin extension unavailable.") };
        completion.value;
    }, {
        if(s.serverRunning.not, {
            statusView !? { |view| view.string_("Start the audio server before scanning VSTs.") };
            completion.value;
        }, {
            statusView !? { |view| view.string_("Scanning default VST paths...") };
            pluginClass.perform(\search, s, nil, nil, true, -1, {
                {
                    var count = pluginClass.perform(\pluginList, s, true).size;
                    statusView !? { |view|
                        view.string_("VST scan complete: % plugins found.".format(count))
                    };
                    completion.value;
                }.defer;
            });
        });
    });
};
~qriScanVSTPlugins = scanVSTPlugins;

openVSTInRackSlot = { |index, pluginKey|
    var controller, loadPlugin;
    ensureVSTRack.value;
    controller = ~qriVSTRackControllers[index];
    if(controller.isNil, {
        "QMW VST slot % is not ready; start or rebuild the audio server.".format(index + 1).warn;
        ~qriVSTStatus !? { |view| view.string_("Slot % is not ready; rebuild audio.".format(index + 1)) };
    }, {
        loadPlugin = {
            ~qriVSTStatus !? { |view|
                view.string_("Loading % into slot %...".format(pluginKey, index + 1))
            };
            controller.perform(\open, pluginKey.asString, true, true,
                { |self, success|
                    {
                        if(success, {
                            ~qriVSTRackPluginKeys[index] = self.info.key;
                            ~qriVSTRackLoaded[index] = true;
                            ~qriVSTStatus !? { |view|
                                view.string_("Slot % loaded: %".format(index + 1, self.info.name))
                            };
                            applyVSTRackRouting.value;
                        }, {
                            ~qriVSTStatus !? { |view|
                                view.string_("Slot % could not load %. See the post window."
                                    .format(index + 1, pluginKey))
                            };
                        });
                    }.defer;
                });
        };
        if(controller.info.notNil, {
            // Close is asynchronous in VSTPlugin. The controller dependant
            // opens the replacement only after the real close notification.
            ~qriVSTRackPendingOpens[index] = loadPlugin;
            controller.perform(\close);
        }, {
            loadPlugin.value;
        });
    });
};
~qriOpenVSTInRackSlot = openVSTInRackSlot;

openVSTChooser = { |index|
    var window, listView, filterField, filterButton, statusView;
    var plugins = [], visiblePlugins = [];
    var refreshList, chooseSelection, pluginClass = \VSTPlugin.asClass;
    if(pluginClass.isNil, {
        "VSTPlugin extension is unavailable. Recompile the class library after installation.".warn;
    }, {
        ensureVSTRack.value;
        ~qriVSTRackChooserWindows[index] !? _.close;
        window = Window("QMW VST slot % selector".format(index + 1),
            Rect(170 + (index * 24), 90 + (index * 24), 700, 570)).front
            .alwaysOnTop_(true).background_(panelColor);
        ~qriVSTRackChooserWindows[index] = window;
        StaticText(window, Rect(16, 12, 668, 26))
            .string_("SELECT AN EFFECT FOR VST RACK SLOT %".format(index + 1))
            .font_(Font("Helvetica Neue", 14, true)).stringColor_(textColor);
        StaticText(window, Rect(16, 42, 78, 26)).string_("Filter")
            .stringColor_(mutedTextColor);
        filterField = TextField(window, Rect(94, 42, 410, 28))
            .string_("").stringColor_(textColor).background_(fieldColor);
        filterButton = Button(window, Rect(514, 42, 80, 28))
            .states_([["FILTER", textColor, Color.fromHexString("263241")]]);
        Button(window, Rect(604, 42, 80, 28))
            .states_([["CLEAR", textColor, Color.fromHexString("263241")]])
            .action_({ filterField.string_(""); refreshList.value });
        listView = ListView(window, Rect(16, 82, 668, 388))
            .background_(fieldColor).stringColor_(textColor);
        statusView = StaticText(window, Rect(16, 480, 668, 26))
            .stringColor_(Color.fromHexString("a9c5dd"));
        refreshList = {
            var needle = filterField.string.asString.toLower;
            plugins = pluginClass.perform(\pluginList, s, true)
                .select { |info| info.synth.not };
            visiblePlugins = plugins.select { |info|
                var searchable = "% % %".format(
                    info.name ? "Unnamed", info.vendor ? "Unknown", info.key
                ).toLower;
                needle.isEmpty or: { searchable.find(needle).notNil }
            };
            listView.items_(visiblePlugins.collect { |info|
                "%  —  %".format(info.name ? info.key, info.vendor ? "Unknown vendor")
            });
            listView.value_(0);
            statusView.string_(if(visiblePlugins.isEmpty, {
                "No scanned VST effects match. Press RESCAN DEFAULT PATHS."
            }, {
                "% effects available. Select one, then press LOAD SELECTED or Return."
                    .format(visiblePlugins.size)
            }));
        };
        chooseSelection = {
            var selected;
            if(visiblePlugins.isEmpty, {
                statusView.string_("No effect is selected; scan or change the filter.");
            }, {
                selected = visiblePlugins[listView.value.clip(0, visiblePlugins.size - 1)];
                openVSTInRackSlot.(index, selected.key);
                window.close;
            });
        };
        filterField.action_({ refreshList.value });
        filterButton.action_({ refreshList.value });
        listView.enterKeyAction_({ chooseSelection.value });
        Button(window, Rect(16, 518, 216, 34))
            .states_([["RESCAN DEFAULT PATHS", textColor, Color.fromHexString("263241")]])
            .action_({ scanVSTPlugins.(statusView, refreshList) });
        Button(window, Rect(444, 518, 154, 34))
            .states_([["LOAD SELECTED", Color.black, Color.fromHexString("80ed99")]])
            .action_({ chooseSelection.value });
        Button(window, Rect(608, 518, 76, 34))
            .states_([["CANCEL", textColor, Color.fromHexString("532b35")]])
            .action_({ window.close });
        window.onClose = {
            if(~qriVSTRackChooserWindows[index] === window) {
                ~qriVSTRackChooserWindows[index] = nil
            }
        };
        refreshList.value;
        // Each sclang process starts with an empty client-side plugin
        // dictionary even when scsynth has a saved scan cache. Hydrate it on
        // first use so SELECT VST is a one-click path to a populated chooser.
        if((~qriVSTAutoScanEnabled ? true)
            and: { plugins.isEmpty } and: { s.serverRunning }, {
            scanVSTPlugins.(statusView, refreshList)
        });
        window.front;
    });
};
~qriOpenVSTChooser = openVSTChooser;

recallVSTRackSlotPreset = { |index|
    var controller = ~qriVSTRackControllers[index];
    var presetName = ~qriVSTRackPresetNames[index];
    if(controller.notNil and: { controller.info.notNil }
        and: { presetName.notNil } and: { presetName.asString.notEmpty }, {
        controller.perform(\loadPreset, presetName.asString, { |self, success|
            if(success, {
                "QMW VST slot % recalled preset %".format(index + 1, presetName).postln
            }, {
                "QMW VST slot % could not recall preset %".format(index + 1, presetName).warn
            })
        });
    });
};
~qriRecallVSTRackSlotPreset = recallVSTRackSlotPreset;

~qriApplyVSTRackScene = {
    ensureVSTRack.value;
    4.do { |index|
        var controller = ~qriVSTRackControllers[index];
        var key = ~qriVSTRackPluginKeys[index];
        if(controller.notNil and: { key.notNil } and: { key.asString.notEmpty }, {
            if(controller.info.notNil and: { controller.info.key.asString == key.asString }, {
                recallVSTRackSlotPreset.(index)
            }, {
                controller.perform(\close);
                AppClock.sched(0.05, {
                    controller.perform(\open, key.asString, true, false, { |self, success|
                        if(success, { recallVSTRackSlotPreset.(index) })
                    });
                    nil
                });
            });
        });
    };
    applyVSTRackRouting.value;
};

// Retain the original public seam while routing it to the rack.
ensureVSTReturn = { ensureVSTRack.value };
~qriEnsureVSTReturn = ensureVSTReturn;

stopFXReturns = {
    (~qriVSTRackChooserWindows ? []).do { |window| window !? _.close };
    ~qriVSTRackChooserWindows = Array.newClear(4);
    ~qriCloudsProxy !? { |proxy| proxy.clear(0) };
    ~qriCloudsProxy = nil; ~qriCloudsProxyActive = false; ~qriCloudsNode = nil;
    ~qriVSTRackPendingOpens = Array.newClear(4);
    (~qriVSTRackControllers ? []).do { |controller, index|
        controller !? { |item|
            ~qriVSTRackControllerDependants[index] !? { |dependant| item.removeDependant(dependant) };
            item.perform(\close)
        };
    };
    (~qriVSTRackNodes ? []).do { |node| node !? _.free };
    (~qriVSTRackStageBuses ? []).do { |bus| bus !? _.free };
    ~qriVSTRackMixBus !? _.free;
    ~qriVSTRackReturnProxy !? { |proxy| proxy.clear(0) };
    ~qriFXProxyGroup !? _.free;
    ~qriFXProxyGroup = nil;
    ~qriVSTRackNodes = Array.newClear(4);
    ~qriVSTRackControllers = Array.newClear(4);
    ~qriVSTRackControllerDependants = Array.newClear(4);
    ~qriVSTRackStageBuses = Array.newClear(4);
    ~qriVSTRackMixBus = nil;
    ~qriVSTRackOutputNode = nil;
    ~qriVSTRackReturnProxy = nil;
    ~qriVSTRackReturnInputBus = nil;
    ~qriVSTRackLoaded = Array.fill(4, false);
    ~qriVSTRackLatencies = Array.fill(4, 0);
    ~qriVSTRackLatencySamples = 0;
    ~qriVSTController = nil; ~qriVSTNode = nil;
};
~qriStopFXReturns = stopFXReturns;

buildEventSynth = { |name, outputChannels|
    SynthDef(name, { |out=0, fundamental=72, master=0.16, eventGain=0.75,
        audibilityGain=64,
        magnitude=0.003, decay=0.34, decayScale=1, voiceGainBus=0,
        voiceDecayBus=0, ringMix=0,
        voiceFuzzSendBus=0, voiceTemporalSendBus=0,
        temporalSendBus=0, voiceFXSendBus=0, fxSendBus=0,
        hmiSendBus=0, hmiSend=0,
        qhoPopulationBus=0, qhoCoherenceMagnitudeBus=0,
        qhoCoherencePhaseBus=0, qhoBasisPopulationBus=0,
        qhoMatrixPowerBus=0, qhoMatrixPhaseBus=0,
        fmControlBus=0, chebControlBus=0, parsevalControlBus=0,
        ringHarmonic=2, fuzzMix=0, fuzzDrive=8, fuzzBias=0.12,
        fuzzTone=5200|
        var ratios = NamedControl.kr(\frequencyRatios, Array.fill(modeCount, 1.0));
        var weights = NamedControl.kr(\modalWeights, Array.fill(modeCount, 0.0));
        var phases = NamedControl.kr(\modalPhases, Array.fill(modeCount, 0.0));
        var dynamicDetunes = NamedControl.kr(\dynamicDetunes, Array.fill(modeCount, 0));
        var dynamicBrightness = NamedControl.kr(
            \dynamicBrightness, Array.fill(modeCount, 0)
        );
        var dynamicDecayScales = NamedControl.kr(
            \dynamicDecayScales, Array.fill(modeCount, 1)
        );
        var dynamicDrives = NamedControl.kr(\dynamicDrives, Array.fill(modeCount, 1));
        var voiceMask = NamedControl.kr(\voiceMask, Array.fill(5, 1));
        var decayBusValues = In.kr(voiceDecayBus, 8);
        var voiceDecays = Array.fill(5, { |index|
            (Select.kr(voiceDecayBus > 0, [decay, decayBusValues[index]])
                * decayScale.clip(0.02, 1.75)).clip(0.02, 6.0)
        });
        var voiceGains = In.kr(voiceGainBus, 8).clip(0, 1.5)
            * (voiceMask ++ [1, 1, 1]);
        var voiceFuzzSends = Lag.kr(In.kr(voiceFuzzSendBus, 8).clip(0, 1), 0.03);
        var voiceTemporalSends = Lag.kr(In.kr(voiceTemporalSendBus, 8).clip(0, 1), 0.03);
        var voiceFXSends = Lag.kr(In.kr(voiceFXSendBus, 8).clip(0, 1), 0.03);
        var qhoPopulations = In.kr(qhoPopulationBus, 16).clip(0, 1);
        var qhoCoherenceMagnitudes = In.kr(qhoCoherenceMagnitudeBus, 15).clip(0, 1);
        var qhoCoherencePhases = In.kr(qhoCoherencePhaseBus, 15).clip(pi.neg, pi);
        var qhoBasisPopulations = In.kr(qhoBasisPopulationBus, 48).clip(0, 1);
        var qhoMatrixPowerBins = In.kr(qhoMatrixPowerBus, 16).clip(0, 1);
        var qhoMatrixPhaseBins = In.kr(qhoMatrixPhaseBus, 16).clip(pi.neg, pi);
        var fmControls = Lag.kr(In.kr(fmControlBus, 3), 0.03);
        var chebControls = Lag.kr(In.kr(chebControlBus, 8), 0.03);
        var parsevalControls = Lag.kr(In.kr(parsevalControlBus, 3), 0.03);
        var fmRatio = fmControls[0].clip(0.125, 12);
        var fmIndex = fmControls[1].clip(0, 18);
        var qhoDepth = fmControls[2].clip(0, 1);
        var qhoTotal = qhoPopulations.sum.max(0.0001);
        var qhoCentroid = (qhoPopulations * Array.series(16, 0, 1)).sum / qhoTotal;
        var chebGain = chebControls[0].clip(0, 1.5);
        var chebMode = chebControls[1].round.clip(0, 1);
        var chebCalibration = chebControls[2].round.clip(0, 1);
        var chebContactSeconds = chebControls[3].clip(0.001, 0.5);
        var chebIncidence = chebControls[4].clip(0, pi / 2);
        var chebOrder = chebControls[5].round.clip(1, 16);
        var chebCoherenceDepth = chebControls[6].clip(0, 1);
        var chebDecay = chebControls[7].clip(0.02, 6.0);
        var parsevalMode = parsevalControls[0].round.clip(0, 1);
        var parsevalBasis = parsevalControls[1].round.clip(0, 2);
        var parsevalTargetRMS = parsevalControls[2].clip(0, 0.5);
        var selectedBasisPopulations = Array.fill(16, { |index|
            Select.kr(parsevalBasis, [
                qhoBasisPopulations[index],
                qhoBasisPopulations[16 + index],
                qhoBasisPopulations[32 + index]
            ])
        });
        var chebSourcePowers = Array.fill(16, { |index|
            Select.kr(parsevalMode, [
                selectedBasisPopulations[index], qhoMatrixPowerBins[index]
            ])
        });
        var chebRelativePhases = Array.newClear(16);
        var chebActiveMask = Array.fill(16, { |index|
            (chebOrder - index).clip(0, 1)
                * ((fundamental * (index + 1)) < (SampleRate.ir * 0.45))
        });
        var chebActivePower = (chebSourcePowers * chebActiveMask).sum;
        // Fixed-RMS mode renormalizes only the active basis probabilities.
        // Purity mode deliberately leaves the unitary matrix-spectrum norm
        // untouched: RMS = targetRMS * sqrt(active matrix power).
        var chebCoefficientNorm = Select.kr(
            parsevalMode, [chebActivePower.sqrt.max(0.0001), 1.0]
        );
        // A finite Gaussian contact envelope. The exact Chebyshev identity
        // T_k(cos(theta)) = cos(k * theta) is realized by the harmonic bank
        // below, so this window supplies the time localization only.
        var chebWindow = LFGauss.ar(
            chebContactSeconds, 0.22, 0, 0, 0
        );
        var chebDurationRatio = 0.012 / chebContactSeconds;
        var chebPhysicalDurationGain = Select.kr(
            chebMode, [chebDurationRatio, 1.0]
        );
        var chebDurationGain = Select.kr(
            chebCalibration,
            [chebPhysicalDurationGain, chebDurationRatio.sqrt]
        ).clip(0.05, 12);
        var chebNormalGain = chebIncidence.cos;
        var chebHarmonics, chebImpact, chebActuator, chebExciter;
        var perModeVoices, signals, temporalVoiceStems;
        var temporalVoiceReturns, emitted, adapterGain, temporalReturnSend, dry;
        var ringAmount, ringFrequency, ringed, ringOutput, output;
        // MiRings is an independent sixth event lane; its fader must not
        // renormalize the original five voices.
        var voiceNorm = voiceGains.copyRange(0, 4).squared.sum.sqrt.max(1);
        var frequencies = (fundamental * ratios).clip(28, 16000);
        var fuzzVoice = { |source, send|
            var amount = send.clip(0, 1);
            var drive = Lag.kr(fuzzDrive.clip(1, 40), 0.03);
            var bias = Lag.kr(fuzzBias.clip(-0.45, 0.45), 0.03);
            var firstStage = ((HPF.ar(source, 24) * drive) + bias).tanh;
            var secondStage = ((firstStage * (1.6 + (drive.sqrt * 0.32)))
                + (bias * 0.55)).tanh;
            var fuzzed = LPF.ar(
                LeakDC.ar(secondStage.clip(-0.72 + (bias * 0.12), 0.50 + (bias * 0.12))),
                fuzzTone.clip(800, 12000)
            ) * 0.92;
            XFade2.ar(source, fuzzed, (amount * 2) - 1)
        };
        var voiceLifetimes = voiceDecays.collect { |voiceDecay|
            EnvGen.kr(Env.perc(0.002, voiceDecay, 1, -4))
        };
        // The node lives for the longest lane, while the five envelopes below
        // independently close their own stems. This avoids truncating a long
        // voice or keeping a short voice audible merely because they share a
        // server node.
        var nodeLifetime = EnvGen.kr(Env.linen(0,
            (voiceDecays.inject(chebDecay, { |maximum, item| maximum.max(item) }) * 1.75)
                .clip(0.04, 10.5), 0.04), doneAction: 2);
        // Each voice has an independent exciter. More importantly, it gets a
        // different modal coupling below. If all five exciters are summed
        // before one identically weighted Ringz bank, the membrane erases most
        // of their identity and the mixer sounds like five gain controls for
        // the same instrument.
        var simple = HPF.ar(PinkNoise.ar(0.34), 1100)
            * Decay2.ar(Impulse.ar(0), 0.0005, 0.018);
        var gaussianEnvelope = EnvGen.ar(Env(
            [0, 1, 0],
            [voiceDecays[1] * 0.18, voiceDecays[1] * 0.82],
            [4, -6]
        ));
        var gaussian = BPF.ar(
            WhiteNoise.ar(0.42),
            (fundamental * 5.5).clip(90, 12000), 0.62
        ) * gaussianEnvelope;
        var layered = (
            LPF.ar(BrownNoise.ar(0.30), (fundamental * 9).clip(180, 5200))
                * Decay2.ar(Impulse.ar(0), 0.002, 0.13)
        ) + (
            HPF.ar(WhiteNoise.ar(0.11), 3200)
                * Decay2.ar(Impulse.ar(0), 0.0003, 0.012)
        ) + (
            SinOsc.ar((fundamental * 0.5).clip(28, 3000), 0, 0.10)
                * Decay2.ar(Impulse.ar(0), 0.0015, 0.09)
        );
        var fmEnvelope = EnvGen.ar(Env.perc(
            0.002, (voiceDecays[3] * 0.72).clip(0.045, 3.2), 1, -4
        ));
        // Buchla-inspired LPG: the same envelope closes gain and brightness.
        // This is sound design, not a claim about quantum evolution.
        var lpgEnvelope = EnvGen.ar(Env.perc(0.003, voiceDecays[4], 1, -5));
        var lpg = RLPF.ar(
            PinkNoise.ar(0.3),
            (90 + (lpgEnvelope.squared * 11000)).clip(45, 15000), 0.34
        ) * lpgEnvelope;
        // Adjacent rho[n,n+1] phases form a declared coherence chain.  The
        // normalized magnitude is its reliability; phase influence fades to
        // zero as coherence vanishes. Mixed states are not treated as if they
        // possessed one hidden state-vector phase.
        chebRelativePhases[0] = 0.0;
        15.do { |index|
            var denominator = (qhoPopulations[index]
                * qhoPopulations[index + 1]).sqrt.max(1e-9);
            var reliability = (qhoCoherenceMagnitudes[index] / denominator)
                .clip(0, 1);
            chebRelativePhases[index + 1] = chebRelativePhases[index]
                - (qhoCoherencePhases[index] * reliability * chebCoherenceDepth);
        };
        // Exact unit-circle Chebyshev identity, rendered as a bounded harmonic
        // bank so inactive/ultrasonic orders do not fold back below Nyquist.
        chebHarmonics = Mix.fill(16, { |index|
            var harmonic = index + 1;
            var frequency = fundamental * harmonic;
            var basisPhase = Select.kr(parsevalBasis, [
                chebRelativePhases[index], 0.0, 0.0
            ]);
            var sourcePhase = Select.kr(parsevalMode, [
                basisPhase,
                qhoMatrixPhaseBins[index] * chebCoherenceDepth
            ]);
            var coefficient = chebSourcePowers[index].sqrt
                * chebActiveMask[index] / chebCoefficientNorm
                * parsevalTargetRMS * 2.sqrt;
            SinOsc.ar(frequency.min(SampleRate.ir * 0.45),
                sourcePhase, coefficient)
        });
        // Impact is a nonnegative contact envelope. Actuator is a signed,
        // Gaussian-windowed Chebyshev force and is therefore labelled as an
        // active driver rather than a passive mallet strike.
        chebImpact = chebWindow * chebDurationGain * chebNormalGain;
        chebActuator = chebHarmonics * chebWindow
            * chebDurationGain * chebNormalGain;
        chebExciter = Select.ar(chebMode, [chebImpact, chebActuator]) * chebGain;
        perModeVoices = Array.fill(modeCount, { |index|
            var phaseColor = 1 + (phases[index].sin * 0.006);
            var adapterBrightness = dynamicBrightness[index].clip(0, 1);
            var adapterDrive = dynamicDrives[index].clip(0.18, 2.8);
            var adapterDecay = dynamicDecayScales[index].clip(0.16, 4);
            var brightnessColor = weights[index].clip(0, 1).linlin(0, 1, 0.78, 1.0)
                * (0.78 + (adapterBrightness * 0.72));
            var position = index / (modeCount - 1);
            var gaussianProfile = (-0.5 * ((position - 0.52) / 0.18).squared).exp;
            var simpleProfile = position.linlin(0, 1, 0.42, 1.0);
            var layeredProfile = (1.0 - (position * 0.68))
                * if(index.even, 1.0, 0.58);
            var lpgProfile = (-2.8 * position).exp;
            // The canonical bosonic state redistributes only the QHO-FM
            // spectrum. Direct Fock weight plus a bounded centroid halo makes
            // changes of QHO preparation audible across the whole modal body;
            // the admitted Hilbert-current event still owns final gain.
            var qhoIndex = index % 16;
            var directQho = qhoPopulations[qhoIndex].sqrt;
            var centroidQho = (1 - ((qhoIndex - qhoCentroid).abs / 8)).clip(0, 1);
            var qhoProfile = ((directQho * 0.95) + (centroidQho * 0.65))
                .clip(0, 1.6);
            var modalFrequency = (frequencies[index] * phaseColor
                * (1 + (dynamicDetunes[index].clip(-0.18, 0.18) * 1.8))).clip(28, 16000);
            var resonatorScale = (0.72 + (index * 0.021)) * (0.5 + adapterDecay);
            var simpleResonatorDecay = (voiceDecays[0] * resonatorScale).clip(0.02, 6.0);
            var gaussianResonatorDecay = (voiceDecays[1] * resonatorScale).clip(0.02, 6.0);
            var layeredResonatorDecay = (voiceDecays[2] * resonatorScale).clip(0.02, 6.0);
            var lpgResonatorDecay = (voiceDecays[4] * resonatorScale).clip(0.02, 6.0);
            var chebResonatorDecay = (chebDecay * resonatorScale).clip(0.02, 6.0);
            // The pre-fuzz sum used one effect over five channels. Keep the
            // same modal body, but render its linear Ringz response per voice
            // so every fader has its own independent fuzz send.
            var simpleResonated = Ringz.ar(
                simple * voiceGains[0] * simpleProfile * brightnessColor
                    * adapterDrive.sqrt / voiceNorm,
                modalFrequency, simpleResonatorDecay
            );
            var gaussianResonated = Ringz.ar(
                gaussian * voiceGains[1] * gaussianProfile * brightnessColor
                    * adapterDrive.sqrt / voiceNorm,
                modalFrequency, gaussianResonatorDecay
            );
            var layeredResonated = Ringz.ar(
                layered * voiceGains[2] * layeredProfile * brightnessColor
                    * adapterDrive.sqrt / voiceNorm,
                modalFrequency, layeredResonatorDecay
            );
            var lpgResonated = Ringz.ar(
                lpg * voiceGains[4] * lpgProfile * 0.72 * brightnessColor
                    * adapterDrive.sqrt / voiceNorm,
                modalFrequency, lpgResonatorDecay
            );
            // The event's existing twenty-mode weights are the strike-position
            // coupling. Chebyshev/QHO data shape the force; they do not replace
            // or reschedule the admitted Hilbert-current event.
            var chebResonated = Ringz.ar(
                chebExciter * brightnessColor * adapterDrive.sqrt,
                modalFrequency, chebResonatorDecay
            );
            // FM remains a tonal oscillator bank instead of being reduced to
            // another impulse into Ringz. The interaction state still owns its
            // pitches, weights, phases, and admitted event envelope.
            var fmPhase = SinOsc.ar(
                (modalFrequency * fmRatio).clip(18, 16000),
                phases[index] * -0.5,
                fmIndex * (0.35 + (qhoDepth * 0.65))
                    * (0.45 + (position * 0.90))
            );
            var fmMode = SinOsc.ar(
                modalFrequency, phases[index] + fmPhase,
                0.30 * fmEnvelope * voiceGains[3] / voiceNorm
                * (0.20 + (0.80 * ((1 - qhoDepth) + (qhoDepth * qhoProfile))))
            );
            // A small direct LPG component preserves the audible closing
            // filter gesture instead of letting the resonator mask it.
            var lpgDirect = lpg * voiceGains[4] * lpgProfile
                * 0.028 / voiceNorm;
            [
                fuzzVoice.(simpleResonated, voiceFuzzSends[0]) * voiceLifetimes[0],
                fuzzVoice.(gaussianResonated, voiceFuzzSends[1]) * voiceLifetimes[1],
                fuzzVoice.(layeredResonated, voiceFuzzSends[2]) * voiceLifetimes[2],
                fuzzVoice.(fmMode, voiceFuzzSends[3]) * voiceLifetimes[3],
                fuzzVoice.(lpgResonated + lpgDirect, voiceFuzzSends[4]) * voiceLifetimes[4],
                chebResonated
            ] * weights[index].clip(0, 1).sqrt;
        });
        signals = perModeVoices.collect { |voices| voices.sum };
        // Keep each stereo voice stem until after the same shared ring stage
        // used by the dry output. The Temporal Memory send below is therefore
        // recognizably the source voice, not its exciter or a proxy click.
        temporalVoiceStems = perModeVoices.flop.collect { |voiceModes|
            Splay.ar(voiceModes, 0.9, 1.0, 0.0)
        };
        adapterGain = Lag.kr(audibilityGain.clip(0, 128), 0.03);
        // Retained solely for the separately gated harmonic-memory adapter;
        // Temporal Memory itself now receives the per-voice mixer sends below.
        temporalReturnSend = Splay.ar(signals, 0.9, 1.0, 0.0);
        dry = if(outputChannels == 2, {
            Splay.ar(signals, 0.9, 1.0, 0.0)
        }, {
            Mix.fill(modeCount, { |index|
                PanAz.ar(
                    outputChannels, signals[index],
                    (index.linlin(0, modeCount - 1, -1, 1)
                        + (phases[index] / pi)).wrap(-1, 1),
                    1, 2
                )
            }) / modeCount.sqrt
        });
        ringAmount = Lag.kr(ringMix.clip(0, 1), 0.03);
        ringFrequency = (fundamental
            * ringHarmonic.round.clip(1, 16)).clip(18, SampleRate.ir * 0.35);
        ringed = dry * SinOsc.ar(ringFrequency) * 2.sqrt;
        ringOutput = XFade2.ar(dry, ringed, (ringAmount * 2) - 1);
        output = ringOutput;
        temporalVoiceReturns = temporalVoiceStems.collect { |stem|
            XFade2.ar(stem, stem * SinOsc.ar(ringFrequency) * 2.sqrt,
                (ringAmount * 2) - 1)
        };
        emitted = Limiter.ar(
            output * nodeLifetime * magnitude.clip(0, 1).sqrt
            * eventGain.clip(0, 2) * master.clip(0, 0.9) * adapterGain, 0.84
        );
        // The admitted probability quantum owns amplitude. Continuous fields
        // appear only in weights, phase color, damping, and spatial position.
        Out.ar(out, emitted);
        // Each native voice has a real, independent post-voice delay send.
        // This follows its exact dry stereo stem through the shared ring stage
        // before summing to the shared stereo memory input.
        Out.ar(temporalSendBus, Mix.fill(5, { |voice|
            temporalVoiceReturns[voice] * voiceTemporalSends[voice]
        }) * nodeLifetime * magnitude.clip(0, 1).sqrt
            * eventGain.clip(0, 2) * master.clip(0, 0.9) * adapterGain);
        // The FX bus receives the same post-voice, post-ring stereo stems as
        // the dry mixer.  Its per-channel sends remain ordinary audio routing.
        Out.ar(fxSendBus, Mix.fill(5, { |voice|
            temporalVoiceReturns[voice] * voiceFXSends[voice]
        }) * nodeLifetime * magnitude.clip(0, 1).sqrt
            * eventGain.clip(0, 2) * master.clip(0, 0.9) * adapterGain);
        Out.ar(hmiSendBus, temporalReturnSend * nodeLifetime
            * magnitude.clip(0, 1).sqrt * eventGain.clip(0, 2)
            * master.clip(0, 0.9) * adapterGain
            * Lag.kr(hmiSend.clip(0, 1), 0.03));
    }).add;
};

defineSynths = {
    buildEventSynth.(\qriScatteringEvent2V1, 2);
    buildEventSynth.(\qriScatteringEvent8V1, 8);
    buildEventSynth.(\qriScatteringEvent16V1, 16);
    defineProjectiveSynths.value;
    defineMiRingsSynth.value;
    if(~qriMiRingsAvailable, { buildMiRingsEventSynth.(\MiRings.asClass) });
    buildMIVoiceSynths.value;
    defineFXSynths.value;
};
~qriDefineSynths = defineSynths;
// A recoverable, ordinary-stereo listening state. This does not change QMW
// state, event admission semantics, or any observer; it simply removes every
// auxiliary layer so the performer can add one audible decision at a time from
// a known reference. QRM's proven ring and fuzz settings are intentionally
// preserved: they remain part of the chosen Simple-pluck timbre.
listeningBaseline = {
    ~qriBodyMode = 0;
    ~qriFieldGain = 0.0;
    ~qrmCrossingAudioEnabled = false;
    ~qriPolyEnabled = false;
    ~qriStopPolyLanes.value;
    ~qriDisableMiRingsSix !? { |disable| disable.value };
    ~qriVoiceGains = [0.82, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
    ~qriVoiceDecays = Array.fill(8, 0.22); ~qriDecay = 0.22;
    ~qriVoiceMutes = Array.fill(8, 0);
    ~qriVoiceFuzzSends = Array.fill(8, 0.0);
    ~qriVoiceTemporalSends = Array.fill(8, 0.0);
    ~qriVoiceFXSends = Array.fill(8, 0.0);
    ~qriCloudsReturn = 0.0; ~qriVSTRackReturn = 0.0; ~qriVSTReturn = 0.0;
    stopFXReturns.value;
    ~qriMix = 0.45; ~qriEventGain = 0.60; ~qriDecay = 0.22;
    ~qriHmiSend = 0.0;
    ~qriNodes.do(_.free); ~qriNodes.clear;
    ~qriMiRingsNode !? _.free; ~qriMiRingsNode = nil;
    ~qriPushVoiceGains.value;
    ~qriPushVoiceDecays.value;
    ~qriPushVoiceFuzzSends.value;
    ~qriPushVoiceTemporalSends.value;
    ~qriPushVoiceFXSends.value;
    ~qriApplyBodyMode.value;
    ~qmwTemporalMemorySetMixer !? { |setter| setter.value(0.0, 0.0) };
    ~qmwTemporalMemorySetSelfFeedback !? { |setter| setter.value(0.0) };
    ~qmwTemporalMemorySetTapFocus !? { |setter| setter.value(0.0) };
    ~qmwHmiSetMixer !? { |setter| setter.value(0.0) };
    ~qriSetPluckThreshold.value(0.10);
    "QMW listening baseline: Simple pluck only; ring and fuzz preserved; auxiliary layers bypassed.".postln;
};
~qriListeningBaseline = listeningBaseline;

// A reciprocal, deliberately narrow listening state for the native field.
// QRM's Sound Lock owns whether its field body may speak; make that explicit
// here so selecting FIELD is a complete audible action, not a silent routing
// change that also requires finding a separate panel.
fieldListeningBaseline = {
    ~qriBodyMode = 1;
    ~qriFieldBody = 0;
    ~qriFieldGain = 0.18;
    ~qrmCrossingAudioEnabled = false;
    ~qriPolyEnabled = false;
    ~qriStopPolyLanes.value;
    ~qriDisableMiRingsSix !? { |disable| disable.value };
    ~qrmSonify = true;
    ~qrmSoundButton !? { |button| button.value_(1) };
    ~qrmBody !? { |node| node.set(\master, ~qrmMaster) };
    ~qriApplyBodyMode.value;
    "QMW field listen: native 20-mode field active; use field body gain for its audible level.".postln;
};
~qriFieldListeningBaseline = fieldListeningBaseline;
~qriRebuildAudioLayer = {
    stopFXReturns.value;
    defineSynths.value;
    s.sync;
    ~qriVoiceGainBus !? _.free;
    ~qriVoiceGainBus = Bus.control(s, 8);
    ~qriVoiceDecayBus !? _.free;
    ~qriVoiceDecayBus = Bus.control(s, 8);
    ~qriVoiceFuzzSendBus !? _.free;
    ~qriVoiceFuzzSendBus = Bus.control(s, 8);
    ~qriVoiceTemporalSendBus !? _.free;
    ~qriVoiceTemporalSendBus = Bus.control(s, 8);
    ~qriVoiceFXSendBus !? _.free;
    ~qriVoiceFXSendBus = Bus.control(s, 8);
    ~qriFXSendBus !? _.free;
    ~qriFXSendBus = Bus.audio(s, 2);
    ~qriFXGroup !? _.free;
    ~qriFXGroup = Group.after(~qrmStrikeGroup ? s.defaultGroup).register;
    ~qriFXProxyGroup = Group.after(~qriFXGroup).register;
    ~qriProjectiveBody !? _.free; ~qriProjectiveBody = nil;
    ~qriFieldGroup !? _.free;
    ~qriFieldGroup = Group.after(~qrmBody ? s.defaultGroup).register;
    ~qriQHOPopulationBus !? _.free;
    ~qriQHOPopulationBus = Bus.control(s, 16);
    ~qriQHOPopulationBus.setn(~qriQHOFrame[\populations]);
    ~qriQHOCoherenceMagnitudeBus !? _.free;
    ~qriQHOCoherenceMagnitudeBus = Bus.control(s, 15);
    ~qriQHOCoherenceMagnitudeBus.setn(~qriQHOFrame[\coherence1Magnitudes]);
    ~qriQHOCoherencePhaseBus !? _.free;
    ~qriQHOCoherencePhaseBus = Bus.control(s, 15);
    ~qriQHOCoherencePhaseBus.setn(~qriQHOFrame[\coherence1Phases]);
    ~qriQHOBasisPopulationBus !? _.free;
    ~qriQHOBasisPopulationBus = Bus.control(s, 48);
    ~qriQHOBasisPopulationBus.setn(~qriQHOFrame[\basisPopulations].flat);
    ~qriQHOMatrixPowerBus !? _.free;
    ~qriQHOMatrixPowerBus = Bus.control(s, 16);
    ~qriQHOMatrixPowerBus.setn(~qriQHOFrame[\matrixPowerBins]);
    ~qriQHOMatrixPhaseBus !? _.free;
    ~qriQHOMatrixPhaseBus = Bus.control(s, 16);
    ~qriQHOMatrixPhaseBus.setn(~qriQHOFrame[\matrixPhaseBins]);
    ~qriFMControlBus !? _.free;
    ~qriFMControlBus = Bus.control(s, 3);
    ~qriChebControlBus !? _.free;
    ~qriChebControlBus = Bus.control(s, 8);
    ~qriParsevalControlBus !? _.free;
    ~qriParsevalControlBus = Bus.control(s, 3);
    ~qriPushFMControls.value;
    ~qriPushChebControls.value;
    ~qriPushParsevalControls.value;
    ~qriPushVoiceGains.value;
    ~qriPushVoiceDecays.value;
    ~qriPushVoiceFuzzSends.value;
    ~qriPushVoiceTemporalSends.value;
    ~qriPushVoiceFXSends.value;
    // NodeProxy accepts a parent group only after NodeWatcher has observed it.
    // Confirm the insert and return groups before installing persistent shells.
    s.sync;
    rebuildProjectiveBody.value;
    ~qriApplyBodyMode.value;
    // Temporal Memory must begin only after QRM has built qrmStrikeGroup.
    // Its own dedicated effects group is then ordered after all event voices.
    ~qmwTemporalMemoryStart !? { |start| start.value };
    ensureCloudsReturn.value;
    if(~qriSimpleSixMiRings, {
        ~qriActivateMiRingsSix.value;
    });
    "QMW integrated resonant interaction synths ready".postln;
};
// In the unified launcher, QRM calls this hook after building/rebuilding its
// audio graph. Manual late loading still installs the layer immediately.
if(s.serverRunning and: { ~qrmAudioReady ? false }) {
    Routine({ ~qriRebuildAudioLayer.value }).play(AppClock)
};

~qriRenderEventUnsafe = { |event, level=1.0|
    var weights, phases, peak, synthName, node, miNode, energy, decayScale, allocationScale;
    var dominantIndex, dominantRatio;
    var temporalSendBus, hmiSendBus, voiceIndex, voiceMask;
    energy = event[\energy].asFloat.max(0) * level.squared;
    voiceIndex = (event[\voiceIndex] ? -1).asInteger.clip(-1, 7);
    voiceMask = Array.fill(5, { |index|
        if((voiceIndex < 0) or: { voiceIndex == index }, { 1 }, { 0 })
    });
    // Optional adapter-owned per-event decay. Absent metadata is exactly the
    // prior V1 behavior, so an observer may shape resonator lifetime without
    // changing the admitted event energy or any upstream authority.
    decayScale = ~qriAllocatorTailScale.value(
        (event[\decayScale] ? 1.0).asFloat
    );
    // Equal-power compensation protects the shared output sum. Per-node
    // Limiters remain the last local guard, but cannot see additive bus level.
    allocationScale = ~qriAllocatorAmplitudeScale.value;
    energy = energy * allocationScale.squared;
    temporalSendBus = if(~qmwTemporalMemoryInputBus.notNil, {
        ~qmwTemporalMemoryInputBus.index
    }, { 0 });
    hmiSendBus = if(~qmwHmiInputBus.notNil, { ~qmwHmiInputBus.index }, { 0 });
    if(~qriMiRingsSixEnabled and: { ~qriMiRingsAvailable }, {
        renderMiRingsSix.value(event, level);
    }, {
    if(~qriEnabled and: { ~qriPlucksEnabled.value }
        and: { ~qrmSonify ? false } and: { ~qrmAudioReady ? false }
        and: { ~qriVoiceGainBus.notNil } and: { ~qriVoiceDecayBus.notNil }
        and: { ~qriVoiceFuzzSendBus.notNil }
        and: { ~qriVoiceTemporalSendBus.notNil } and: { ~qriVoiceFXSendBus.notNil }
        and: { ~qriFXSendBus.notNil }
        and: { ~qriFMControlBus.notNil }
        and: { ~qriQHOCoherenceMagnitudeBus.notNil }
        and: { ~qriQHOCoherencePhaseBus.notNil }
        and: { ~qriQHOBasisPopulationBus.notNil }
        and: { ~qriQHOMatrixPowerBus.notNil }
        and: { ~qriQHOMatrixPhaseBus.notNil }
        and: { ~qriChebControlBus.notNil }
        and: { ~qriParsevalControlBus.notNil }
        and: { energy > 0 }) {
        weights = event[\weights].collect(_.asFloat.abs);
        phases = event[\phases].collect(_.asFloat);
        peak = weights.maxItem.max(1e-12);
        weights = weights / peak;
        // doneAction frees completed voices server-side; prune the client list
        // before admission. Crucially, do not free a live resonator merely to
        // make room: abrupt node removal is a click at longer pluck decays.
        ~qriNodes = ~qriNodes.select { |active| active.isPlaying };
        if(~qriNodes.size < ~qriCurrentVoiceBudget.value) {
            synthName = case
            { (~qrmOutputChannels ? 2) >= 16 } { \qriScatteringEvent16V1 }
            { (~qrmOutputChannels ? 2) >= 8 } { \qriScatteringEvent8V1 }
            { \qriScatteringEvent2V1 };
            node = Synth(synthName, [
                \fundamental, ~qrmFundamental ? 72,
                \master, (~qrmMaster ? 0.16) * ~qriMix,
                \eventGain, ~qriEventGain,
                \audibilityGain, ~qriPluckAudibilityGain,
                \magnitude, energy,
                \decay, ~qriDecay, \decayScale, decayScale,
                \voiceGainBus, ~qriVoiceGainBus.index,
                \voiceDecayBus, ~qriVoiceDecayBus.index,
                \voiceFuzzSendBus, ~qriVoiceFuzzSendBus.index,
                \voiceTemporalSendBus, ~qriVoiceTemporalSendBus.index,
                \temporalSendBus, temporalSendBus,
                \voiceFXSendBus, ~qriVoiceFXSendBus.index,
                \fxSendBus, ~qriFXSendBus.index,
                \hmiSendBus, hmiSendBus,
                \hmiSend, if(hmiSendBus > 0, { ~qriHmiSend }, { 0 }),
                \qhoPopulationBus, ~qriQHOPopulationBus.index,
                \qhoCoherenceMagnitudeBus, ~qriQHOCoherenceMagnitudeBus.index,
                \qhoCoherencePhaseBus, ~qriQHOCoherencePhaseBus.index,
                \qhoBasisPopulationBus, ~qriQHOBasisPopulationBus.index,
                \qhoMatrixPowerBus, ~qriQHOMatrixPowerBus.index,
                \qhoMatrixPhaseBus, ~qriQHOMatrixPhaseBus.index,
                \fmControlBus, ~qriFMControlBus.index,
                \chebControlBus, ~qriChebControlBus.index,
                \parsevalControlBus, ~qriParsevalControlBus.index,
                \ringMix, ~qrmRingMix ? 0,
                \ringHarmonic, ~qrmRingHarmonic ? 2,
                \fuzzDrive, ~qrmFuzzDrive ? 8,
                \fuzzBias, ~qrmFuzzBias ? 0.12,
                \fuzzTone, ~qrmFuzzTone ? 5200,
                \frequencyRatios, ~qrmPitchRatios ? Array.fill(modeCount, 1),
                \modalWeights, weights * (~qrmModeAudioWeights !? {
                    ~qrmModeAudioWeights.value
                } ? Array.fill(modeCount, 1)),
                \modalPhases, phases,
                \voiceMask, voiceMask,
                \dynamicDetunes, ~qrmPulseDetunes ? Array.fill(modeCount, 0),
                \dynamicBrightness, ~qrmPulseBrightness ? Array.fill(modeCount, 0),
                \dynamicDecayScales, ~qrmPulseDecayScales ? Array.fill(modeCount, 1),
                \dynamicDrives, ~qrmPulseDrives ? Array.fill(modeCount, 1)
            ], ~qrmStrikeGroup, \addToTail);
            node.register;
            ~qriNodes.add(node);
            node.onFree({ ~qriNodes.remove(node) });
            dominantIndex = (event[\dominant] ? 0).asInteger.clip(0, modeCount - 1);
            dominantRatio = ((~qrmPitchRatios ? Array.fill(modeCount, 1))[dominantIndex] ? 1)
                .asFloat.clip(0.125, 16);
            // The sixth lane must be a finite registered event node. The old
            // singleton audition path force-freed the preceding tail, made
            // polyrhythms monophonic, and could send /n_free after doneAction
            // had already removed the server node.
            ~qriMiRingsNodes = ~qriMiRingsNodes.select { |active| active.isPlaying };
            if(((voiceIndex < 0) or: { voiceIndex == 5 })
                and: { ~qriMiRingsAvailable }
                and: { ~qriEffectiveVoiceGains.value[5] > 0.0001 }
                and: { ~qriMiRingsNodes.size < ~qriCurrentMIVoiceBudget.value }
                and: { ~qriAllocatorAdmitAuxiliary.value(voiceIndex) }) {
                miNode = Synth(\qriMiRingsEventVoiceV1, [
                    \out, 0, \fundamental, ~qrmFundamental ? 72,
                    \ratio, dominantRatio, \magnitude, energy,
                    \decay, ~qriDecay, \decayScale, decayScale,
                    \voiceGainBus, ~qriVoiceGainBus.index,
                    \voiceDecayBus, ~qriVoiceDecayBus.index,
                    \voiceFuzzSendBus, ~qriVoiceFuzzSendBus.index,
                    \voiceTemporalSendBus, ~qriVoiceTemporalSendBus.index,
                    \temporalSendBus, temporalSendBus,
                    \temporalSendEnabled, if(temporalSendBus > 0, { 1 }, { 0 }),
                    \voiceFXSendBus, ~qriVoiceFXSendBus.index,
                    \fxSendBus, ~qriFXSendBus.index,
                    \structure, ~qriMiRingsStructure,
                    \brightness, ~qriMiRingsBrightness,
                    \damping, ~qriMiRingsDamping,
                    \position, ~qriMiRingsPosition, \model, ~qriMiRingsModel,
                    \fuzzDrive, ~qrmFuzzDrive ? 8,
                    \fuzzBias, ~qrmFuzzBias ? 0.12,
                    \fuzzTone, ~qrmFuzzTone ? 5200
                ], ~qrmStrikeGroup, \addToTail).register;
                ~qriMiRingsNodes.add(miNode);
                miNode.onFree({ ~qriMiRingsNodes.remove(miNode) });
            };
            ~qriMiVoiceNodes = ~qriMiVoiceNodes.select { |active| active.isPlaying };
            if(((voiceIndex < 0) or: { voiceIndex == 6 })
                and: { ~qriMiPlaitsAvailable }
                and: { ~qriEffectiveVoiceGains.value[6] > 0.0001 }
                and: { ~qriMiVoiceNodes.size < ~qriCurrentMIVoiceBudget.value }
                and: { ~qriAllocatorAdmitAuxiliary.value(voiceIndex) }) {
                miNode = Synth(\qriMiPlaitsEventV1, [
                    \fundamental, ~qrmFundamental ? 72, \ratio, dominantRatio,
                    \magnitude, energy, \decay, ~qriDecay, \decayScale, decayScale,
                    \voiceGainBus, ~qriVoiceGainBus.index,
                    \voiceDecayBus, ~qriVoiceDecayBus.index,
                    \voiceFuzzSendBus, ~qriVoiceFuzzSendBus.index,
                    \voiceTemporalSendBus, ~qriVoiceTemporalSendBus.index,
                    \temporalSendBus, temporalSendBus,
                    \voiceFXSendBus, ~qriVoiceFXSendBus.index, \fxSendBus, ~qriFXSendBus.index,
                    \engine, ~qriPlaitsEngine, \harmonics, ~qriPlaitsHarmonics,
                    \timbre, ~qriPlaitsTimbre, \morph, ~qriPlaitsMorph,
                    \plaitsDecay, ~qriPlaitsDecay,
                    \fuzzDrive, ~qrmFuzzDrive ? 8, \fuzzBias, ~qrmFuzzBias ? 0.12,
                    \fuzzTone, ~qrmFuzzTone ? 5200
                ], ~qrmStrikeGroup, \addToTail).register;
                ~qriMiVoiceNodes.add(miNode);
                miNode.onFree({ ~qriMiVoiceNodes.remove(miNode) });
            };
            if(((voiceIndex < 0) or: { voiceIndex == 7 })
                and: { ~qriMiElementsAvailable }
                and: { ~qriEffectiveVoiceGains.value[7] > 0.0001 }
                and: { ~qriMiVoiceNodes.size < ~qriCurrentMIVoiceBudget.value }
                and: { ~qriAllocatorAdmitAuxiliary.value(voiceIndex) }) {
                miNode = Synth(\qriMiElementsEventV1, [
                    \fundamental, ~qrmFundamental ? 72, \ratio, dominantRatio,
                    \magnitude, energy, \decay, ~qriDecay, \decayScale, decayScale,
                    \voiceGainBus, ~qriVoiceGainBus.index,
                    \voiceDecayBus, ~qriVoiceDecayBus.index,
                    \voiceFuzzSendBus, ~qriVoiceFuzzSendBus.index,
                    \voiceTemporalSendBus, ~qriVoiceTemporalSendBus.index,
                    \temporalSendBus, temporalSendBus,
                    \voiceFXSendBus, ~qriVoiceFXSendBus.index, \fxSendBus, ~qriFXSendBus.index,
                    \contour, ~qriElementsContour, \bow, ~qriElementsBow,
                    \blow, ~qriElementsBlow, \strike, ~qriElementsStrike,
                    \geometry, ~qriElementsGeometry, \brightness, ~qriElementsBrightness,
                    \damping, ~qriElementsDamping, \space, ~qriElementsSpace,
                    \model, ~qriElementsModel,
                    \fuzzDrive, ~qrmFuzzDrive ? 8, \fuzzBias, ~qrmFuzzBias ? 0.12,
                    \fuzzTone, ~qrmFuzzTone ? 5200
                ], ~qrmStrikeGroup, \addToTail).register;
                ~qriMiVoiceNodes.add(miNode);
                miNode.onFree({ ~qriMiVoiceNodes.remove(miNode) });
            };
        } {
            // Preserve the tail and explicitly report pressure rather than
            // hiding it behind a hard voice-steal click.
            ~qriShedPlucks = ~qriShedPlucks + 1;
        };
    };
    });
};
renderEvent = { |event, level=1.0|
    // Clock choice owns rhythm. Capacity is enforced by the live-node budget
    // and time-aware tail scaling, never by replacing every mode with a shared
    // long-decay metronome.
    ~qriRenderEventUnsafe.value(event, level)
};
~qriRenderEvent = renderEvent;

eventBucketKey = { |event|
    "%|%|%".format(event[\channel], event[\kind], event[\dominant])
};

queuedQuantumCount = {
    ~qriPluckQueue.inject(0, { |sum, event| sum + (event[\quantumCount] ? 1) })
};

// Long tails cannot truthfully replay an ever-growing historical audio queue.
// Collapse repeated quanta within each already-admitted descriptor bucket to
// one newest audible record. This is downstream voice allocation only: the
// committed QMW frame, event counters, and probability-current authority are
// untouched.
~qriCoalesceLongDecayQueue = {
    if((~qrmTimeMode == 1)
        and: { ~qriMaximumVoiceDecay.value >= ~qriBuresLongDecayThreshold }, {
        ~qriPluckQueue.do { |queued|
            var count = (queued[\quantumCount] ? 1).asInteger.max(1);
            if(count > 1) {
                ~qriBuresQueueCoalescedQuanta =
                    ~qriBuresQueueCoalescedQuanta + count - 1;
                queued[\quantumCount] = 1;
            };
        };
    });
};

~qriEffectiveBuresReleaseInterval = {
    var effectiveTail, overlapBudget, interval;
    interval = if(~qriMiRingsSixEnabled, {
        (~qriVoiceDecaySafetyCeilings ? ~qriVoiceDecays)
            .copyRange(0, 5).maxItem.asFloat.clip(0.08, 0.80) + 0.04
    }, {
        effectiveTail = (~qriMaximumVoiceDecay.value
            * ~qriEventDecayScaleCeiling).clip(0.02, 10.5);
        overlapBudget = ~qriCurrentTailOverlapBudget.value;
        (effectiveTail / overlapBudget)
            .max(~qriBuresMinimumReleaseInterval)
    });
    ~qriBuresLastReleaseInterval = interval;
    interval
};

popEvent = {
    var event = nil, stored, count;
    if(~qriPluckQueue.notEmpty) {
        stored = ~qriPluckQueue[0];
        count = (stored[\quantumCount] ? 1).asInteger.max(1);
        event = stored.copy;
        event.removeAt(\quantumCount);
        event.removeAt(\bucketKey);
        if(count > 1) {
            stored[\quantumCount] = count - 1;
            ~qriPluckQueue.removeAt(0);
            ~qriPluckQueue.add(stored);
        } {
            ~qriPluckQueue.removeAt(0)
        };
    };
    event
};

// Six mixer channels are timbral buses. Sixteen independently phased lanes
// are the musical voices: each lane chooses one bus, samples the latest
// admitted event, and makes a bounded downstream spectral variation. This is
// a rhythmic observer, never a change to event admission or QMW state.
~qriTriggerPolyLane = { |laneIndex|
    var source = ~qriPolyLatestEvent;
    var lane, channel, energyScale;
    if(~qriPolyEnabled and: { source.notNil }
        and: { (Main.elapsedTime - ~qriPolyLatestEventAt) <
            ((1 / (~qriPolyBaseHz * ~qriPolyRateMultipliers.minItem).max(0.01))
                * 1.25).clip(2.0, 12.0) }
        and: { ~qriPolyLaneEnabled[laneIndex] > 0 }
        and: { ~qriPlucksEnabled.value }) {
        channel = ~qriPolyLaneChannels[laneIndex];
        if((~qriEffectiveVoiceGains.value[channel] ? 0) > 0.0001) {
            lane = source.copy;
            energyScale = 0.62 + ((laneIndex % 4) * 0.08);
            lane[\voiceIndex] = channel;
            lane[\polyLane] = laneIndex;
            lane[\energy] = source[\energy].asFloat * energyScale;
            lane[\weights] = Array.fill(modeCount, { |mode|
                source[\weights][(mode + laneIndex) % modeCount]
            });
            lane[\phases] = Array.fill(modeCount, { |mode|
                source[\phases][mode] + (~qriPolyPhaseFractions[laneIndex] * 2pi)
            });
            renderEvent.(lane, 0.86);
        };
    };
};

~qriStopPolyLanes = {
    ~qriPolyGeneration = ~qriPolyGeneration + 1;
    ~qriPolyLaneRoutines.do { |routine| routine.stop };
    ~qriPolyLaneRoutines = Array.new;
};

~qriStartPolyLanes = {
    var generation;
    ~qriStopPolyLanes.value;
    generation = ~qriPolyGeneration;
    ~qriPolyLaneRoutines = Array.fill(~qriPolyLaneCount, { |laneIndex|
        Routine({
            var rate = (~qriPolyBaseHz * ~qriPolyRateMultipliers[laneIndex]).max(0.01);
            (~qriPolyPhaseFractions[laneIndex] / rate).wait;
            while { generation == ~qriPolyGeneration } {
                ~qriTriggerPolyLane.value(laneIndex);
                rate = (~qriPolyBaseHz * ~qriPolyRateMultipliers[laneIndex]).max(0.01);
                (1 / rate).wait;
            };
        }).play(SystemClock)
    });
};

enqueueEvent = { |event|
    var key, existing;
    if(~qriEnabled and: { ~qriPlucksEnabled.value }) {
        ~qriPolyLatestEvent = event.copy;
        ~qriPolyLatestEventAt = Main.elapsedTime;
        if(~qriPolyEnabled.not, {
            if(~qrmTimeMode == 0, {
                renderEvent.(event)
            }, {
                // Quantum/Bures timing is a record/release relation. In the
                // simple six-MiRings experiment, retain only the latest
                // record: a physical tail cannot faithfully render an
                // unbounded historical backlog, and replaying it is exactly
                // the scheduler burst that made longer decay choke.
                if(~qriMiRingsSixEnabled and: { ~qrmTimeMode == 1 }, {
                    ~qriPluckQueue.clear;
                    existing = event.copy;
                    existing[\bucketKey] = eventBucketKey.(event);
                    existing[\quantumCount] = 1;
                    ~qriPluckQueue.add(existing);
                }, {
                key = eventBucketKey.(event);
                existing = ~qriPluckQueue.detect { |queued|
                    queued[\bucketKey] == key
                };
                if(existing.notNil) {
                    if((~qrmTimeMode == 1)
                        and: { ~qriMaximumVoiceDecay.value >= ~qriBuresLongDecayThreshold }, {
                        // Replace the pending audible record with the newest
                        // descriptor instead of accumulating a future replay
                        // burst behind a long resonant tail.
                        ~qriBuresQueueCoalescedQuanta =
                            ~qriBuresQueueCoalescedQuanta
                            + (existing[\quantumCount] ? 1).asInteger.max(1);
                        existing[\quantumCount] = 1;
                    }, {
                        existing[\quantumCount] =
                            (existing[\quantumCount] ? 1) + 1;
                    });
                    // Short tails retain every admitted probability quantum.
                    // Long tails explicitly keep only the newest audible descriptor.
                    [\weights, \phases, \energy, \real, \imag].do { |field|
                        existing[field] = event[field]
                    };
                } {
                    existing = event.copy;
                    existing[\bucketKey] = key;
                    existing[\quantumCount] = 1;
                    ~qriPluckQueue.add(existing);
                };
                });
            });
        });
    };
};
~qriEnqueueEvent = enqueueEvent;

releaseTemporalPluck = { |geodesic=false|
    var event, step, hit, delays, generation;
    if(~qriEnabled and: { ~qriPlucksEnabled.value } and: { ~qriPolyEnabled.not }) {
        case
        { (~qrmTimeMode == 1) and: { geodesic.not } } {
            event = popEvent.value;
            if(event.notNil, {
                ~qriBuresReleasedCount = ~qriBuresReleasedCount + 1;
                renderEvent.(event);
            }, {
                ~qriBuresEmptyCount = ~qriBuresEmptyCount + 1;
            });
        }
        { (~qrmTimeMode == 4) and: { geodesic.not } } {
            step = ~qrmQuantumEuclideanStep % ~qrmEuclideanSteps;
            hit = ~qrmEuclideanMask[step];
            ~qrmQuantumEuclideanStep = ~qrmQuantumEuclideanStep + 1;
            if(hit > 0) { event = popEvent.value; event !? { renderEvent.(event) } };
        }
        { (~qrmTimeMode == 5) and: { geodesic } } {
            event = popEvent.value; event !? { renderEvent.(event) }
        }
        { (~qrmTimeMode == 6) and: { geodesic.not } } {
            event = popEvent.value;
            event !? {
                generation = ~qrmSonicGeneration;
                delays = [0, 0.125, 0.25, 0.5].copyRange(0, ~qrmRecursiveDepth)
                    / (~qrmFixedRate * ~qrmClockScale).max(0.01);
                delays.do { |delay, index|
                    var admitted = event.copy;
                    SystemClock.sched(delay, {
                        if(generation == ~qrmSonicGeneration) {
                            renderEvent.(admitted, 1 / (index + 1).sqrt)
                        };
                        nil
                    });
                };
            };
        };
    };
};
~qriReleaseTemporalPluck = releaseTemporalPluck;

// Once this integrated adapter is present, QRM clocks consume only admitted
// Hilbert-current plucks. They never retrigger a cached "latest" event.
~qriPriorRouteBuresPulse = ~qrmRouteBuresPulse;
~qriPriorRouteCrossing = ~qrmRouteCrossing;
~qriPriorTimeClock = ~qrmTimeClock;
~qrmTimeClock !? _.stop;
~qrmRouteBuresPulse = { |geodesic=false|
    var now, interval;
    if((~qrmTimeMode == 1) and: { geodesic.not }, {
        now = Main.elapsedTime;
        // The tail itself sets the safe release window.
        // Six-MiRings keeps one Bures release per active tail;
        // the general 20-mode renderer divides its worst-case effective tail
        // by the explicit overlap budget.
        ~qriCoalesceLongDecayQueue.value;
        interval = ~qriEffectiveBuresReleaseInterval.value;
        if(~qriBuresReleasePending.not
            and: { (now - ~qriBuresLastScheduledAt) >= interval }, {
            ~qriBuresReleasePending = true;
            ~qriBuresLastScheduledAt = now;
            ~qriBuresRecordCount = ~qriBuresRecordCount + 1;
            AppClock.sched(~qriBuresReleaseLatency, {
                ~qriBuresReleasePending = false;
                releaseTemporalPluck.(false); nil
            });
        }, {
            ~qriBuresCoalescedRecords = ~qriBuresCoalescedRecords + 1;
        });
    }, {
        releaseTemporalPluck.(geodesic);
    });
};
~qrmRouteCrossing = { |crossing| ~qrmLatestCrossing = crossing.copy };

~qriTimeClock = Routine({
    loop {
        if(~qriEnabled and: { ~qriPlucksEnabled.value }
            and: { ~qriPolyEnabled.not }
            and: { [2, 3].includes(~qrmTimeMode) }) {
            var hit = 1;
            if(~qrmTimeMode == 3) {
                hit = ~qrmEuclideanMask[~qrmEuclideanStep % ~qrmEuclideanSteps];
                ~qrmEuclideanStep = ~qrmEuclideanStep + 1;
            };
            if(hit > 0) {
                var event = popEvent.value;
                event !? { renderEvent.(event) };
            };
        };
        (1 / (~qrmFixedRate * ~qrmClockScale).max(0.01)).wait;
    };
}).play(AppClock);
~qriStartPolyLanes.value;

drawTriplePlane = {
    var bounds, fields, envelopes, rows, width, height, scale, title;
    var project, valueAt, fillQuad, drawSurface, frontRow, events;
    var hilbertCurrent, flux;
    bounds = ~qriDiagram.bounds;
    width = bounds.width; height = bounds.height;
    Pen.fillColor = Color.fromHexString("080b10"); Pen.fillRect(bounds);
    if(~qriViewMode == 1, {
        fields = (~qrmWaveHistory ? Array.new).asArray;
        envelopes = (~qrmWaveEnvelopeHistory ? Array.new).asArray;
        scale = (~qrmWaveScale ? 1e-6).max(1e-9);
        title = "NATIVE QRM MEMBRANE  /  TWO-QUBIT WORLD RESPONSE";
    }, {
        fields = ~qriFieldHistory.asArray;
        envelopes = ~qriEnvelopeHistory.asArray;
        scale = if(envelopes.isEmpty, { 1e-9 }, {
            envelopes.collect(_.maxItem).maxItem.max(1e-9)
        });
        title = "MAPPED FOUR-QUBIT INTERACTION  /  AUTO-NORMALIZED SOUND-ADAPTER SHAPE";
    });
    rows = fields.size;
    Pen.color = Color.fromHexString("5dd9ff");
    Pen.stringAtPoint(title, 14@12, Font("Helvetica Neue", 12, true));
    if(rows == 0, {
        Pen.color = Color.grey(0.58);
        Pen.stringAtPoint("waiting for mapped interaction availability", 190@(height * 0.48),
            Font("Helvetica Neue", 14));
    }, {
        if(rows == 1) {
            fields = [fields[0], fields[0]];
            envelopes = [envelopes[0], envelopes[0]];
            rows = 2;
        };
        project = { |row, site, value|
            var depth = row / (rows - 1).max(1);
            var left = width * (0.06 + (0.12 * (1 - depth)));
            var right = width * (0.94 - (0.12 * (1 - depth)));
            var baseline = height * (0.23 + (0.66 * depth));
            Point(
                site.linlin(0, modeCount - 1, left, right),
                baseline - ((value / scale).clip(-1.5, 1.5) * height * 0.18)
            )
        };
        valueAt = { |row, site, layer|
            fields[row][site] + (layer * envelopes[row][site] * 0.42)
        };
        fillQuad = { |points, color|
            Pen.fillColor = color; Pen.moveTo(points[0]);
            Pen.lineTo(points[1]); Pen.lineTo(points[2]);
            Pen.lineTo(points[3]); Pen.lineTo(points[0]); Pen.fill;
        };
        drawSurface = { |layer, fillColor, strokeColor|
            (rows - 1).do { |row|
                (modeCount - 1).do { |site|
                    fillQuad.([
                        project.(row, site, valueAt.(row, site, layer)),
                        project.(row, site + 1, valueAt.(row, site + 1, layer)),
                        project.(row + 1, site + 1, valueAt.(row + 1, site + 1, layer)),
                        project.(row + 1, site, valueAt.(row + 1, site, layer))
                    ], fillColor);
                };
            };
            Pen.strokeColor = strokeColor; Pen.width = if(layer == 0, { 0.9 }, { 1.15 });
            rows.do { |row|
                modeCount.do { |site|
                    var point = project.(row, site, valueAt.(row, site, layer));
                    if(site == 0, { Pen.moveTo(point) }, { Pen.lineTo(point) });
                };
                Pen.stroke;
            };
            modeCount.do { |site|
                rows.do { |row|
                    var point = project.(row, site, valueAt.(row, site, layer));
                    if(row == 0, { Pen.moveTo(point) }, { Pen.lineTo(point) });
                };
                Pen.stroke;
            };
        };
        drawSurface.(1, Color(0.98, 0.16, 0.72, 0.07), Color(1.0, 0.35, 0.82, 0.82));
        drawSurface.(-1, Color(0.08, 0.82, 1.0, 0.07), Color(0.18, 0.88, 1.0, 0.82));
        drawSurface.(0, Color(0.25, 0.95, 0.58, 0.13), Color(0.66, 1.0, 0.80, 0.82));
        frontRow = rows - 1;
        events = ~qriFrame[\events] ? [];
        events.do { |event|
            var point = project.(frontRow, event[\dominant],
                valueAt.(frontRow, event[\dominant], 0));
            Pen.fillColor = Color.white.alpha_(0.92);
            Pen.fillOval(Rect(point.x - 4, point.y - 4, 8, 8));
        };
    });
    if(~qriViewMode != 1) {
        hilbertCurrent = ((~qmw44QuantumFrame ? (currents: Array.new))[\currents]
            ? Array.new).inject(0.0, { |sum, edge| sum + edge[\magnitude].abs });
        flux = (~qriMeasurementFrame[\gaugeFlux] ? 0.0).round(0.001);
        Pen.color = Color.white;
        Pen.stringAtPoint(
            "ABSOLUTE SOURCE RESPONSE  sum|J_H| %  /  physical flux %"
            .format(hilbertCurrent.round(0.00001), flux),
            14@(height - 18), Font("Menlo", 9, true)
        );
    };
};

drawSourceOverview = { |view|
    var bounds = view.bounds;
    var boxWidth = (bounds.width - 64) / 3;
    var boxY = 92;
    var boxHeight = 108;
    var drawBox;
    Pen.fillColor = Color.fromHexString("080b10"); Pen.fillRect(bounds);
    Pen.color = Color.fromHexString("dcecff");
    Pen.stringAtPoint("INTEGRATED SOURCE / OBSERVER / SONIC-BODY MAP", 18@18,
        Font("Helvetica Neue", 13, true));
    Pen.color = Color.fromHexString("8ecae6");
    Pen.stringAtPoint(
        "The canonical triple-plane display is in HILBERT INTERACTION.",
        18@42, Font("Helvetica Neue", 11)
    );
    drawBox = { |index, heading, detail, color|
        var x = 16 + (index * (boxWidth + 16));
        var rect = Rect(x, boxY, boxWidth, boxHeight);
        Pen.fillColor = color.alpha_(0.13); Pen.fillRect(rect);
        Pen.strokeColor = color.alpha_(0.82); Pen.width = 1.2; Pen.strokeRect(rect);
        Pen.color = color; Pen.stringAtPoint(heading, (x + 10)@(boxY + 12),
            Font("Helvetica Neue", 10, true));
        Pen.color = Color.white.alpha_(0.70);
        Pen.stringInRect(detail, Rect(x + 10, boxY + 36, boxWidth - 20, 58),
            Font("Helvetica Neue", 9));
    };
    drawBox.(0, "NATIVE WORLD", "two-qubit rho\nQRM displacement", Color.cyan);
    drawBox.(1, "INTERACTION OBSERVER", "four-qubit current\n8 -> 20 mapping", Color.magenta);
    drawBox.(2, "SONIC BODY", "admitted plucks\n20 resonators", Color.green);
    Pen.strokeColor = Color.white.alpha_(0.32); Pen.width = 1.2;
    Pen.line(Point(16 + boxWidth, boxY + (boxHeight / 2)),
        Point(32 + boxWidth, boxY + (boxHeight / 2))); Pen.stroke;
    Pen.line(Point(32 + (boxWidth * 2), boxY + (boxHeight / 2)),
        Point(48 + (boxWidth * 2), boxY + (boxHeight / 2))); Pen.stroke;
    Pen.color = Color.white.alpha_(0.55);
    Pen.stringInRect(
        "Native membrane motion and mapped Hilbert interaction are distinct "
        ++ "datasets. Use the popup selector to compare them in one renderer.",
        Rect(20, 236, bounds.width - 40, 54), Font("Helvetica Neue", 10)
    );
};

drawAvailability = {
    var bounds, paths, center, railY, magnitude, drawLeg;
    bounds = ~qriDiagram.bounds;
    paths = ~qriFrame[\availability] ? [];
    Pen.fillColor = Color.fromHexString("080b10"); Pen.fillRect(bounds);
    Pen.color = Color.fromHexString("5dd9ff");
    Pen.stringAtPoint("CONTINUOUS SCATTERING AVAILABILITY  /  NOT EVENTS",
        14@12, Font("Helvetica Neue", 12, true));
    center = Point(bounds.width * 0.5, bounds.height * 0.46);
    railY = { |lane| 54 + (lane.asFloat.clip(0, 15) / 15 * (bounds.height * 0.67)) };
    drawLeg = { |from, to, color, strength|
        Pen.color = color.alpha_(0.3 + (strength * 0.65));
        Pen.width = 0.8 + (strength * 4); Pen.moveTo(from); Pen.lineTo(to); Pen.stroke;
    };
    paths.do { |path|
        magnitude = Complex(path[\real], path[\imag]).abs.clip(0, 1);
        path[\inputs].do { |lane|
            drawLeg.(Point(48, railY.(lane)), center, Color.cyan, magnitude)
        };
        path[\outputs].do { |lane|
            drawLeg.(center, Point(bounds.width - 48, railY.(lane)), Color.magenta, magnitude)
        };
    };
    Pen.fillColor = Color.white.alpha_(0.78);
    Pen.fillOval(Rect(center.x - 9, center.y - 9, 18, 18));
    if(paths.isEmpty) {
        Pen.color = Color.grey(0.58);
        Pen.stringAtPoint("waiting for scattering availability", 220@(bounds.height * 0.52),
            Font("Helvetica Neue", 14));
    };
};

drawProjective = {
    var bounds = ~qriDiagram.bounds;
    var frame = ~qriMeasurementFrame;
    var probabilities = frame[\probabilities];
    var stateFlow = frame[\stateFlow];
    var apertureFlow = frame[\apertureFlow];
    var maximumFlow = (stateFlow ++ apertureFlow).collect(_.abs).maxItem.max(1e-12);
    var left = 34, right = bounds.width - 24, top = 54, bottom = bounds.height - 38;
    var laneWidth = (right - left) / 16;
    Pen.fillColor = Color.fromHexString("080b10"); Pen.fillRect(bounds);
    Pen.color = Color.fromHexString("5dd9ff");
    Pen.stringAtPoint("PROJECTIVE FIELD  /  PRESENCE + STATE FLOW + APERTURE FLOW",
        14@12, Font("Helvetica Neue", 12, true));
    if(frame[\revision] < 0) {
        Pen.color = Color.grey(0.58);
        Pen.stringAtPoint("waiting for atomic projective measurement frame",
            190@(bounds.height * 0.48), Font("Helvetica Neue", 14));
    } {
        16.do { |index|
            var x = left + (index * laneWidth);
            var probabilityHeight = probabilities[index].clip(0, 1) * (bottom - top);
            var centerX = x + (laneWidth * 0.5);
            var stateHeight = (stateFlow[index] / maximumFlow).clip(-1, 1) * 34;
            var apertureHeight = (apertureFlow[index] / maximumFlow).clip(-1, 1) * 34;
            Pen.fillColor = if(index == frame[\dominant], {
                Color.fromHexString("ff67d4").alpha_(0.86)
            }, { Color.fromHexString("5dd9ff").alpha_(0.64) });
            Pen.fillRect(Rect(x + 3, bottom - probabilityHeight,
                (laneWidth - 6).max(2), probabilityHeight));
            Pen.color = Color.green.alpha_(0.90); Pen.width = 2.2;
            Pen.line(Point(centerX - 3, bottom), Point(centerX - 3, bottom - stateHeight)); Pen.stroke;
            Pen.color = Color.yellow.alpha_(0.90); Pen.width = 2.2;
            Pen.line(Point(centerX + 3, bottom), Point(centerX + 3, bottom - apertureHeight)); Pen.stroke;
            Pen.color = Color.white.alpha_(0.62);
            Pen.stringAtPoint(index.asString, Point(x + 5, bottom + 9), Font("Menlo", 8));
        };
        Pen.color = Color.white.alpha_(0.72);
        Pen.stringAtPoint("% / % @ %x / flux % / holonomy % / H % / dominant %"
            .format(frame[\bankMode], frame[\aperture], frame[\apertureRate].round(0.001),
                frame[\gaugeFlux].round(0.001), frame[\holonomy].round(0.001),
                frame[\entropy].round(0.001), frame[\dominant]),
            18@(bounds.height - 18), Font("Menlo", 9));
        Pen.color = Color.green; Pen.stringAtPoint("state", (bounds.width - 132)@18, Font("Helvetica Neue", 9));
        Pen.color = Color.yellow; Pen.stringAtPoint("aperture", (bounds.width - 80)@18, Font("Helvetica Neue", 9));
    };
};

refreshPanel = {
    var drives, peak, magnitudes;
    drives = ~qriFrame[\drives] ? Array.fill(modeCount, Complex(0, 0));
    magnitudes = if(~qriViewMode == 3, {
        ~qriMeasurementFrame[\probabilities] ++ Array.fill(4, 0.0)
    }, { drives.collect(_.abs) });
    peak = magnitudes.maxItem.max(1e-12);
    ~qriModeView !? { |view| view.value_(magnitudes / peak) };
    ~qriModeLabel !? { |view| view.string_(if(~qriViewMode == 3, {
        "P0-P15 projective probabilities  /  four unused display lanes"
    }, {
        "M1-M20 continuous availability  /  display normalized only"
    })) };
    // value_ updates the confirmed authority value without re-sending OSC.
    if(Main.elapsedTime >= (~qriPerformanceControlPendingUntil ? 0.0)) {
        ~qriRequestedPluckThreshold = (~qriFrame[\threshold] ? 0.1)
            .asFloat.clip(0.005, 0.5);
        ~qriThresholdSlider !? { |view|
            view.value_(~qriRequestedPluckThreshold)
        };
        ~qrmPerformancePluckThresholdSlider !? { |view|
            view.value_(~qriRequestedPluckThreshold)
        };
        ~qriOmegaSlider !? { |view| view.value_(~qriFrame[\omegaScale]) };
    };
    ~qriStatus !? { |view|
        view.string_(
            "rev % / admitted % / queued % / active %/% / shed % / Bures r% ok% miss% gate% queue% render% @ %s / quantum % / remainder % / omega %x / % @ %x"
            .format(
                ~qriFrame[\revision], (~qriFrame[\events] ? []).size,
                queuedQuantumCount.value, ~qriNodes.size, ~qriCurrentVoiceBudget.value, ~qriShedPlucks,
                ~qriBuresRecordCount, ~qriBuresReleasedCount, ~qriBuresEmptyCount,
                ~qriBuresCoalescedRecords, ~qriBuresQueueCoalescedQuanta,
                ~qriLongDecayRenderDrops,
                ~qriBuresLastReleaseInterval.round(0.001),
                ~qriFrame[\threshold].round(0.000001),
                ~qriFrame[\accumulatorPeak].round(0.001),
                ~qriFrame[\omegaScale].round(0.001),
                ~qrmTimeModeNames[~qrmTimeMode], ~qrmClockScale.round(0.001)
            )
        )
    };
    refreshPreparationControls.value;
    ~qriDiagram !? _.refresh;
};

~qriRequestPanelRefresh = {
    var now = Main.elapsedTime;
    var interval = 1 / ~qriDisplayRefreshHz.max(1);
    var remaining = interval - (now - ~qriLastPanelRefreshAt);
    if(remaining <= 0, {
        ~qriLastPanelRefreshAt = now;
        refreshPanel.value;
    }, {
        if(~qriPanelRefreshPending.not) {
            ~qriPanelRefreshPending = true;
            AppClock.sched(remaining.max(0.001), {
                ~qriPanelRefreshPending = false;
                ~qriLastPanelRefreshAt = Main.elapsedTime;
                refreshPanel.value;
                nil
            });
        };
    });
};

commitFrame = { |frame|
    var events, realField, envelope;
    ~qriFrame = frame;
    realField = frame[\drives].collect(_.real);
    envelope = frame[\drives].collect(_.abs);
    ~qriFieldHistory.add(realField);
    ~qriEnvelopeHistory.add(envelope);
    while { ~qriFieldHistory.size > ~qriHistoryLength } {
        ~qriFieldHistory.removeAt(0); ~qriEnvelopeHistory.removeAt(0)
    };
    events = (frame[\events] ? []).sort { |a, b| a[\energy] > b[\energy] };
    // Every admitted quantum enters the timing path. The accumulator already
    // bounds per-edge bursts; this layer must not silently discard admission.
    events.do { |event| enqueueEvent.(event) };
    ~qriRequestPanelRefresh.value;
};

closePanel = {
    ~qriWindow !? _.close;
    ~qriWindow = nil; ~qriDiagram = nil; ~qriModeView = nil;
    ~qriStatus = nil; ~qriModeLabel = nil;
    ~qriThresholdSlider = nil; ~qriOmegaSlider = nil;
};

refreshMeasurementControls = {
    var frame = ~qriMeasurementFrame;
    var bankValues = ["computational", "pauli", "hypercube"];
    var pauliValues = ["XYXY", "IXXX", "ZZXX", "XXIX", "XXXX", "ZZZZ"];
    var apertureValues = ["off", "orbit", "sweep", "geodesic"];
    var statePeak = (frame[\stateFlow] ? [0.0]).collect(_.abs).maxItem;
    var aperturePeak = (frame[\apertureFlow] ? [0.0]).collect(_.abs).maxItem;
    var hilbertCurrent = ((~qmw44QuantumFrame ? (currents: Array.new))[\currents]
        ? Array.new).inject(0.0, { |sum, edge| sum + edge[\magnitude].abs });
    // These are acknowledgements from a committed Python frame. value_ does
    // not invoke the GUI action, so synchronization cannot create OSC loops.
    ~qriMeasurementBankMenu !? { |view|
        view.value_(bankValues.indexOfEqual(frame[\bankMode]) ? 0)
    };
    ~qriMeasurementPauliMenu !? { |view|
        view.value_(pauliValues.indexOfEqual(frame[\pauli]) ? 0)
    };
    ~qriMeasurementApertureMenu !? { |view|
        view.value_(apertureValues.indexOfEqual(frame[\aperture]) ? 0)
    };
    // Do not let a slightly older 30 Hz ACK pull a slider backwards while a
    // performer is dragging it. Rejoin the authority shortly after release.
    if(Main.elapsedTime >= (~qriMeasurementControlPendingUntil ? 0.0)) {
        ~qriMeasurementRateSlider !? { |view| view.value_(frame[\apertureRate]) };
        ~qriMeasurementFluxSlider !? { |view| view.value_(frame[\gaugeFlux]) };
    };
    ~qriMeasurementAckStatus !? { |view|
        view.string_(
            "ACK rev %  /  bank %  /  Pauli %  /  aperture % @ %x  /  flux %  /  holonomy %"
            .format(frame[\revision], frame[\bankMode], frame[\pauli],
                frame[\aperture], frame[\apertureRate].round(0.001),
                frame[\gaugeFlux].round(0.001), frame[\holonomy].round(0.001))
        )
    };
    ~qriMeasurementResponseStatus !? { |view|
        view.string_(
            "RESPONSE  lane delta-P %  /  max|J state| %  /  max|J aperture| %  /  sum|J Hilbert| %"
            .format((~qriMeasurementDeltaP ? 0.0).round(0.0001),
                statePeak.round(0.0001), aperturePeak.round(0.0001),
                hilbertCurrent.round(0.0001))
        )
    };
};

openMeasurementControls = {
    var bankValues = ["computational", "pauli", "hypercube"];
    var pauliValues = ["XYXY", "IXXX", "ZZXX", "XXIX", "XXXX", "ZZZZ"];
    var apertureValues = ["off", "orbit", "sweep", "geodesic"];
    var pending = { |message|
        // Slider actions repeat throughout a drag, continually extending this
        // short guard. The next settled committed frame then snaps only once.
        ~qriMeasurementControlPendingUntil = Main.elapsedTime + 0.18;
        ~qriMeasurementAckStatus !? { |view|
            view.string_("REQUESTED " ++ message ++ "  /  waiting for committed-frame ACK")
        }
    };
    ~qriMeasurementControlWindow !? _.close;
    ~qriMeasurementControlWindow = Window(
        "QMW Projection / Gauge Controls", Rect(170, 110, 620, 366)
    ).front.background_(Color.fromHexString("11151c"));
    StaticText(~qriMeasurementControlWindow, Rect(16, 12, 588, 24))
        .string_("PHYSICAL QUESTION / APERTURE / U(1) CONNECTION")
        .font_(Font("Helvetica Neue", 14, true)).stringColor_(Color.fromHexString("dcecff"));
    StaticText(~qriMeasurementControlWindow, Rect(16, 38, 588, 32))
        .string_("QUESTION + APERTURE = OBSERVER.  LOOP FLUX = SOURCE HAMILTONIAN.")
        .font_(Font("Helvetica Neue", 11, true)).stringColor_(Color.white);
    ~qriMeasurementBankMenu = styleMenu.(PopUpMenu(~qriMeasurementControlWindow, Rect(16, 78, 184, 25))
        .items_(["COMPUTATIONAL", "PAULI EIGENBASIS", "Q4 HYPERCUBE GEOMETRY"])
        .value_(bankValues.indexOfEqual(~qriMeasurementFrame[\bankMode]) ? 0)
        .action_({ |menu|
            pending.("bank " ++ bankValues[menu.value]);
            ~qriMeasurementControlAddress.sendMsg(
                "/qmw/measure/v1/control/bank", bankValues[menu.value])
        }));
    ~qriMeasurementPauliMenu = styleMenu.(PopUpMenu(~qriMeasurementControlWindow, Rect(212, 78, 122, 25))
        .items_(pauliValues).value_(pauliValues.indexOfEqual(~qriMeasurementFrame[\pauli]) ? 0)
        .action_({ |menu|
            pending.("Pauli " ++ pauliValues[menu.value]);
            ~qriMeasurementControlAddress.sendMsg(
                "/qmw/measure/v1/control/pauli", pauliValues[menu.value])
        }));
    ~qriMeasurementApertureMenu = styleMenu.(PopUpMenu(~qriMeasurementControlWindow, Rect(346, 78, 154, 25))
        .items_(["APERTURE OFF", "ORBIT", "SWEEP", "GEODESIC"])
        .value_(apertureValues.indexOfEqual(~qriMeasurementFrame[\aperture]) ? 0)
        .action_({ |menu|
            pending.("aperture " ++ apertureValues[menu.value]);
            ~qriMeasurementControlAddress.sendMsg(
                "/qmw/measure/v1/control/aperture", apertureValues[menu.value])
        }));
    Button(~qriMeasurementControlWindow, Rect(512, 78, 92, 25))
        .states_([["RESET FLUX", textColor, Color.fromHexString("263241")]]).action_({
            pending.("flux 0");
            ~qriMeasurementControlAddress.sendMsg("/qmw/measure/v1/control/gauge_flux", 0.0)
        });
    ~qriMeasurementRateSlider = styleSlider.(EZSlider(~qriMeasurementControlWindow, Rect(16, 120, 286, 30),
        "aperture rate", ControlSpec(0.01, 8, \exp, 0.01), { |view|
            pending.("aperture rate " ++ view.value.round(0.01).asString);
            ~qriMeasurementControlAddress.sendMsg(
                "/qmw/measure/v1/control/aperture_rate", view.value.asFloat)
        }, ~qriMeasurementFrame[\apertureRate], labelWidth: 92, numberWidth: 62));
    ~qriMeasurementFluxSlider = styleSlider.(EZSlider(~qriMeasurementControlWindow, Rect(318, 120, 286, 30),
        "loop flux", ControlSpec(pi.neg, pi, \lin, 0.01), { |view|
            pending.("physical flux " ++ view.value.round(0.01).asString);
            ~qriMeasurementControlAddress.sendMsg(
                "/qmw/measure/v1/control/gauge_flux", view.value.asFloat)
        }, ~qriMeasurementFrame[\gaugeFlux], labelWidth: 78, numberWidth: 68));
    StaticText(~qriMeasurementControlWindow, Rect(16, 162, 588, 42))
        .string_("OBSERVER ROUTE: basis -> P0-P15 bars; aperture -> yellow flow marks.  SOURCE ROUTE: flux -> H_A -> rho -> Hilbert current -> admitted plucks.")
        .font_(Font("Helvetica Neue", 10, true)).stringColor_(Color.white);
    ~qriMeasurementAckStatus = StaticText(~qriMeasurementControlWindow, Rect(16, 214, 588, 42))
        .font_(Font("Menlo", 9, true)).stringColor_(Color.white);
    ~qriMeasurementResponseStatus = StaticText(~qriMeasurementControlWindow, Rect(16, 260, 588, 42))
        .font_(Font("Menlo", 9, true)).stringColor_(Color.white);
    StaticText(~qriMeasurementControlWindow, Rect(16, 310, 588, 40))
        .string_("Use PROJECTIVE FIELD for basis/aperture changes. Gauge-frame transformations are silent. The auto-normalized Hilbert view now reports absolute source current.")
        .stringColor_(Color.white);
    ~qriMeasurementControlWindow.onClose = {
        ~qriMeasurementControlWindow = nil;
        ~qriMeasurementBankMenu = nil; ~qriMeasurementPauliMenu = nil;
        ~qriMeasurementApertureMenu = nil; ~qriMeasurementRateSlider = nil;
        ~qriMeasurementFluxSlider = nil; ~qriMeasurementAckStatus = nil;
        ~qriMeasurementResponseStatus = nil;
    };
    refreshMeasurementControls.value;
};
~qriOpenMeasurementControls = openMeasurementControls;
~qriRefreshMeasurementControls = refreshMeasurementControls;

refreshPreparationControls = {
    var prep = (~qmw44QuantumFrame ? (preparation: nil))[\preparation];
    var modes = ["localized", "coherent", "squeezed", "thermal", "vacuum"];
    prep !? {
        if(~qriPreparationAwaitingAck and: {
            prep[\revision] > ~qriPreparationRequestedAfterRevision
        }) {
            ~qriPreparationAwaitingAck = false;
            ~qriPreparationModeMenu !? { |view| view.value_(modes.indexOfEqual(prep[\mode]) ? 0) };
            ~qriPreparationIndexSlider !? { |view| view.value_(prep[\localizedIndex]) };
            ~qriPreparationThetaSlider !? { |view| view.value_(prep[\coherentTheta]) };
            ~qriPreparationPhaseSlider !? { |view| view.value_(prep[\coherentPhase]) };
            ~qriPreparationSqueezeSlider !? { |view| view.value_(prep[\squeezeMagnitude]) };
            ~qriPreparationSqueezePhaseSlider !? { |view| view.value_(prep[\squeezePhase]) };
            ~qriPreparationTemperatureSlider !? { |view| view.value_(prep[\temperature]) };
        };
        if(~qriPreparationAwaitingAck.not) {
            ~qriPreparationAckStatus !? { |view|
                view.string_(
                    "CONFIRMED FOUR-QUBIT rho  /  rev %  /  %  /  index %  /  theta % phase %  /  squeeze % @ %  /  T %"
                    .format(prep[\revision], prep[\mode], prep[\localizedIndex],
                        prep[\coherentTheta].round(0.01), prep[\coherentPhase].round(0.01),
                        prep[\squeezeMagnitude].round(0.01), prep[\squeezePhase].round(0.01),
                        prep[\temperature].round(0.01))
                )
            };
        };
    };
};

openPreparationControls = {
    var modes = ["localized", "coherent", "squeezed", "thermal", "vacuum"];
    var prep = (~qmw44QuantumFrame ? (preparation: nil))[\preparation] ? (
        mode: "coherent", localizedIndex: 0, coherentTheta: 0.95,
        coherentPhase: 0.55, squeezeMagnitude: 0.62,
        squeezePhase: pi/2, temperature: 0.8, revision: 0
    );
    ~qriPreparationWindow !? _.close;
    ~qriPreparationWindow = Window("QMW Four-Qubit Preparation", Rect(180, 100, 660, 424))
        .front.background_(panelColor);
    StaticText(~qriPreparationWindow, Rect(16, 12, 628, 24))
        .string_("AUTHORITATIVE FOUR-QUBIT SOURCE  /  16 COMPUTATIONAL BASIS STATES")
        .font_(Font("Helvetica Neue", 13, true)).stringColor_(textColor);
    StaticText(~qriPreparationWindow, Rect(16, 40, 628, 38))
        .string_("Coherent is a four-spin product state. Squeezed is a GHZ-like finite analogue. The bosonic QHO is controlled separately.")
        .stringColor_(textColor);
    ~qriPreparationModeMenu = styleMenu.(PopUpMenu(~qriPreparationWindow, Rect(16, 86, 210, 26))
        .items_(["LOCALIZED", "COHERENT SPINS", "PAIR-CORRELATED", "THERMAL", "GROUND"])
        .value_(modes.indexOfEqual(prep[\mode]) ? 0));
    ~qriPreparationIndexSlider = styleSlider.(EZSlider(~qriPreparationWindow, Rect(16, 126, 300, 28),
        "basis index", ControlSpec(0, 15, \lin, 1), nil, prep[\localizedIndex], labelWidth: 96, numberWidth: 54));
    ~qriPreparationThetaSlider = styleSlider.(EZSlider(~qriPreparationWindow, Rect(330, 126, 314, 28),
        "coherent theta", ControlSpec(0, pi, \lin, 0.01), nil, prep[\coherentTheta], labelWidth: 106, numberWidth: 58));
    ~qriPreparationPhaseSlider = styleSlider.(EZSlider(~qriPreparationWindow, Rect(16, 166, 300, 28),
        "coherent phase", ControlSpec(pi.neg, pi, \lin, 0.01), nil, prep[\coherentPhase], labelWidth: 104, numberWidth: 58));
    ~qriPreparationSqueezeSlider = styleSlider.(EZSlider(~qriPreparationWindow, Rect(330, 166, 314, 28),
        "squeeze magnitude", ControlSpec(0, pi/2, \lin, 0.01), nil, prep[\squeezeMagnitude], labelWidth: 120, numberWidth: 58));
    ~qriPreparationSqueezePhaseSlider = styleSlider.(EZSlider(~qriPreparationWindow, Rect(16, 206, 300, 28),
        "squeeze phase", ControlSpec(pi.neg, pi, \lin, 0.01), nil, prep[\squeezePhase], labelWidth: 104, numberWidth: 58));
    ~qriPreparationTemperatureSlider = styleSlider.(EZSlider(~qriPreparationWindow, Rect(330, 206, 314, 28),
        "thermal T", ControlSpec(0.01, 10, \exp, 0.01), nil, prep[\temperature], labelWidth: 82, numberWidth: 58));
    Button(~qriPreparationWindow, Rect(16, 254, 628, 38))
        .states_([["APPLY / REPREPARE FOUR-QUBIT rho", Color.black, Color.fromHexString("80ed99")]])
        .action_({
            ~qriPreparationAwaitingAck = true;
            ~qriPreparationRequestedAfterRevision = (
                ((~qmw44QuantumFrame ? (preparation: (revision: -1)))[\preparation]
                    ? (revision: -1))[\revision]
            );
            ~qriPreparationAckStatus.string_("REQUESTED  /  waiting for committed four-qubit frame ACK");
            ~qriPreparationControlAddress.sendMsg(
                "/qmw/4_4/preparation/control/apply",
                modes[~qriPreparationModeMenu.value],
                ~qriPreparationIndexSlider.value.asInteger,
                ~qriPreparationThetaSlider.value.asFloat,
                ~qriPreparationPhaseSlider.value.asFloat,
                ~qriPreparationSqueezeSlider.value.asFloat,
                ~qriPreparationSqueezePhaseSlider.value.asFloat,
                ~qriPreparationTemperatureSlider.value.asFloat
            )
        });
    ~qriPreparationAckStatus = StaticText(~qriPreparationWindow, Rect(16, 306, 628, 58))
        .font_(Font("Menlo", 9, true)).stringColor_(textColor);
    StaticText(~qriPreparationWindow, Rect(16, 370, 628, 38))
        .string_("This resets rho only after APPLY. Gauge/projective controls remain observer and Hamiltonian controls; they do not masquerade as preparation.")
        .stringColor_(textColor);
    ~qriPreparationWindow.onClose = { ~qriPreparationWindow = nil };
    refreshPreparationControls.value;
};
~qriOpenPreparationControls = openPreparationControls;
~qriRefreshPreparationControls = refreshPreparationControls;

refreshQHOControls = {
    var frame = ~qriQHOFrame;
    var states = ["vacuum", "fock", "coherent", "thermal", "squeezed"];
    var requested = ~qriQHORequested;
    var matches = requested.notNil and: {
        frame[\state] == requested[\state]
    } and: { frame[\fock] == requested[\fock] }
        and: { (frame[\alphaRe] - requested[\alphaRe]).abs < 0.005 }
        and: { (frame[\alphaIm] - requested[\alphaIm]).abs < 0.005 }
        and: { (frame[\thermal] - requested[\thermal]).abs < 0.005 }
        and: { (frame[\squeezeR] - requested[\squeezeR]).abs < 0.005 }
        and: { (frame[\squeezePhase] - requested[\squeezePhase]).abs < 0.005 }
        and: { (frame[\omega] - requested[\omega]).abs < 0.005 };
    if(~qriQHOAwaitingAck and: { matches }) {
        ~qriQHOAwaitingAck = false;
        ~qriQHORequested = nil;
        ~qriQHOStateMenu !? { |view| view.value_(states.indexOfEqual(frame[\state]) ? 2) };
        ~qriQHOFockSlider !? { |view| view.value_(frame[\fock]) };
        ~qriQHOAlphaReSlider !? { |view| view.value_(frame[\alphaRe]) };
        ~qriQHOAlphaImSlider !? { |view| view.value_(frame[\alphaIm]) };
        ~qriQHOThermalSlider !? { |view| view.value_(frame[\thermal]) };
        ~qriQHOSqueezeSlider !? { |view| view.value_(frame[\squeezeR]) };
        ~qriQHOSqueezePhaseSlider !? { |view| view.value_(frame[\squeezePhase]) };
        ~qriQHOOmegaSlider !? { |view| view.value_(frame[\omega]) };
    };
    ~qriQHOPopulationView !? { |view| view.value_(frame[\populations]) };
    refreshParsevalControls !? { |refresh| refresh.value };
    if(~qriQHOAwaitingAck.not) {
        ~qriQHOStatus !? { |view|
            view.string_("CONFIRMED BOSONIC |psi/rho>  /  rev %  /  %  /  alpha (% + %i)  /  <n> %  /  purity %"
                .format(frame[\revision], frame[\state], frame[\alphaRe].round(0.01),
                    frame[\alphaIm].round(0.01), frame[\meanN].round(0.01), frame[\purity].round(0.001)))
        };
    };
};

openQHOControls = {
    var states = ["vacuum", "fock", "coherent", "thermal", "squeezed"];
    var frame = ~qriQHOFrame;
    ~qriQHOWindow !? _.close;
    ~qriQHOWindow = Window("QMW Canonical Bosonic QHO + FM Adapter", Rect(210, 70, 680, 682))
        .front.background_(panelColor);
    StaticText(~qriQHOWindow, Rect(16, 12, 648, 24))
        .string_("CANONICAL 16-LEVEL BOSONIC QHO  /  |0> ... |15>")
        .font_(Font("Helvetica Neue", 14, true)).stringColor_(textColor);
    StaticText(~qriQHOWindow, Rect(16, 40, 648, 34))
        .string_("This is not four physical qubits. Its 16 Fock populations reshape the event-gated QHO-FM spectrum.")
        .stringColor_(textColor);
    ~qriQHOStateMenu = styleMenu.(PopUpMenu(~qriQHOWindow, Rect(16, 82, 210, 26))
        .items_(["VACUUM", "FOCK", "COHERENT alpha", "THERMAL", "SQUEEZED"])
        .value_(states.indexOfEqual(frame[\state]) ? 2));
    ~qriQHOFockSlider = styleSlider.(EZSlider(~qriQHOWindow, Rect(238, 82, 210, 28),
        "Fock n", ControlSpec(0, 15, \lin, 1), nil, frame[\fock], labelWidth: 62, numberWidth: 48));
    ~qriQHOAlphaReSlider = styleSlider.(EZSlider(~qriQHOWindow, Rect(16, 124, 316, 28),
        "alpha Re", ControlSpec(-3, 3, \lin, 0.01), nil, frame[\alphaRe], labelWidth: 82, numberWidth: 58));
    ~qriQHOAlphaImSlider = styleSlider.(EZSlider(~qriQHOWindow, Rect(348, 124, 316, 28),
        "alpha Im", ControlSpec(-3, 3, \lin, 0.01), nil, frame[\alphaIm], labelWidth: 82, numberWidth: 58));
    ~qriQHOThermalSlider = styleSlider.(EZSlider(~qriQHOWindow, Rect(16, 164, 316, 28),
        "thermal <n>", ControlSpec(0, 10, \lin, 0.01), nil, frame[\thermal], labelWidth: 88, numberWidth: 58));
    ~qriQHOSqueezeSlider = styleSlider.(EZSlider(~qriQHOWindow, Rect(348, 164, 316, 28),
        "squeeze r", ControlSpec(0, 2.5, \lin, 0.01), nil, frame[\squeezeR], labelWidth: 82, numberWidth: 58));
    ~qriQHOSqueezePhaseSlider = styleSlider.(EZSlider(~qriQHOWindow, Rect(16, 204, 316, 28),
        "squeeze phase", ControlSpec(pi.neg, pi, \lin, 0.01), nil, frame[\squeezePhase], labelWidth: 104, numberWidth: 58));
    ~qriQHOOmegaSlider = styleSlider.(EZSlider(~qriQHOWindow, Rect(348, 204, 316, 28),
        "omega", ControlSpec(0.1, 8, \exp, 0.01), nil, frame[\omega], labelWidth: 62, numberWidth: 58));
    StaticText(~qriQHOWindow, Rect(16, 244, 648, 18))
        .string_("LIVE QHO-FM ADAPTER  /  affects active tails; no reprepare required. Use FM AUDITION to hear it alone.")
        .stringColor_(Color.fromHexString("f2cc8f"));
    ~qriFMDepthSlider = styleSlider.(EZSlider(~qriQHOWindow, Rect(16, 266, 210, 28),
        "state depth", ControlSpec(0, 1, \lin, 0.01), { |view|
            ~qriQHOMix = view.value; ~qriPushFMControls.value
        }, ~qriQHOMix, labelWidth: 82, numberWidth: 48));
    ~qriFMRatioSlider = styleSlider.(EZSlider(~qriQHOWindow, Rect(236, 266, 210, 28),
        "FM ratio", ControlSpec(0.125, 12, \exp, 0.01), { |view|
            ~qriFMRatio = view.value; ~qriPushFMControls.value
        }, ~qriFMRatio, labelWidth: 72, numberWidth: 48));
    ~qriFMIndexSlider = styleSlider.(EZSlider(~qriQHOWindow, Rect(456, 266, 208, 28),
        "FM index", ControlSpec(0, 18, \lin, 0.01), { |view|
            ~qriFMIndex = view.value; ~qriPushFMControls.value
        }, ~qriFMIndex, labelWidth: 72, numberWidth: 48));
    Button(~qriQHOWindow, Rect(16, 306, 316, 38))
        .states_([["FM AUDITION  /  no state change", Color.black, Color.fromHexString("f2cc8f")]])
        .action_({ ~qriAuditionQHOFM.value });
    Button(~qriQHOWindow, Rect(348, 306, 316, 38))
        .states_([["APPLY / REPREPARE BOSONIC QHO", Color.black, Color.fromHexString("5dd9ff")]])
        .action_({
            ~qriQHOAwaitingAck = true;
            ~qriQHORequested = (
                state: states[~qriQHOStateMenu.value],
                fock: ~qriQHOFockSlider.value.asInteger,
                alphaRe: ~qriQHOAlphaReSlider.value.asFloat,
                alphaIm: ~qriQHOAlphaImSlider.value.asFloat,
                thermal: ~qriQHOThermalSlider.value.asFloat,
                squeezeR: ~qriQHOSqueezeSlider.value.asFloat,
                squeezePhase: ~qriQHOSqueezePhaseSlider.value.asFloat,
                omega: ~qriQHOOmegaSlider.value.asFloat
            );
            ~qriQHOStatus.string_("REQUESTED  /  waiting for canonical QHO frame ACK");
            ~qriQHOControlAddress.sendMsg("/qmw/qho/v1/control/prepare",
                states[~qriQHOStateMenu.value], ~qriQHOFockSlider.value.asInteger,
                ~qriQHOAlphaReSlider.value.asFloat, ~qriQHOAlphaImSlider.value.asFloat,
                ~qriQHOThermalSlider.value.asFloat, ~qriQHOSqueezeSlider.value.asFloat,
                ~qriQHOSqueezePhaseSlider.value.asFloat);
            ~qriQHOControlAddress.sendMsg("/qmw/qho/v1/control/omega", ~qriQHOOmegaSlider.value.asFloat)
        });
    Button(~qriQHOWindow, Rect(16, 352, 648, 34))
        .states_([["QHO CHEB / PARSEVAL  /  fixed RMS + purity energy",
            Color.black, Color.fromHexString("ff7ac6")]])
        .action_({ openChebyshevControls.value });
    StaticText(~qriQHOWindow, Rect(16, 398, 648, 18))
        .string_("FOCK POPULATIONS  |0> ... |15>").stringColor_(Color.fromHexString("8ecae6"));
    ~qriQHOPopulationView = MultiSliderView(~qriQHOWindow, Rect(16, 420, 648, 100))
        .size_(16).isFilled_(true).value_(frame[\populations])
        .fillColor_(Color.fromHexString("5dd9ff")).background_(fieldColor);
    ~qriQHOStatus = StaticText(~qriQHOWindow, Rect(16, 532, 648, 42))
        .font_(Font("Menlo", 9, true)).stringColor_(textColor);
    StaticText(~qriQHOWindow, Rect(16, 584, 648, 62))
        .string_("alpha Re/Im prepare coherent |psi>. FM Depth, Ratio, and Index are live sound-adapter controls; they do not overwrite the four-qubit Hilbert/gauge state.")
        .stringColor_(textColor);
    ~qriQHOWindow.onClose = {
        ~qriQHOWindow = nil;
        ~qriFMDepthSlider = nil; ~qriFMRatioSlider = nil; ~qriFMIndexSlider = nil
    };
    refreshQHOControls.value;
};
~qriOpenQHOControls = openQHOControls;
~qriRefreshQHOControls = refreshQHOControls;

refreshParsevalControls = {
    var frame = ~qriQHOFrame;
    var basisNames = ["FOCK", "QFT-16", "WALSH-HADAMARD"];
    var basisBanks = frame[\basisPopulations]
        ? Array.fill(3, { Array.fill(16, 0.0) });
    var sourcePowers = if(~qriParsevalMode == 0, {
        basisBanks[~qriParsevalBasis] ? Array.fill(16, 0.0)
    }, {
        frame[\matrixPowerBins] ? Array.fill(16, 0.0)
    });
    var nyquist = ((s.sampleRate ? 48000) * 0.45);
    var activePowers = Array.fill(16, { |index|
        sourcePowers[index] * if(
            (index < ~qriChebOrder)
                and: { ((~qrmFundamental ? 72) * (index + 1)) < nyquist },
            { 1.0 }, { 0.0 }
        )
    });
    var activePower = activePowers.sum;
    var fullPower = sourcePowers.sum;
    var predictedRMS = if(~qriParsevalMode == 0, {
        if(activePower > 1e-12, { ~qriParsevalTargetRMS }, { 0.0 })
    }, {
        ~qriParsevalTargetRMS * activePower.sqrt
    });
    var displayPeak = sourcePowers.maxItem.max(1e-12);
    ~qriParsevalModeMenu !? { |view| view.value_(~qriParsevalMode) };
    ~qriParsevalBasisMenu !? { |view|
        view.value_(~qriParsevalBasis).enabled_(~qriParsevalMode == 0)
    };
    ~qriParsevalTargetRMSSlider !? { |view| view.value_(~qriParsevalTargetRMS) };
    ~qriParsevalSpectrumView !? { |view| view.value_(sourcePowers / displayPeak) };
    ~qriParsevalMetrics !? { |view|
        view.string_(
            (
                "%  /  basis %  /  target RMS %  predicted pre-window RMS %\n"
                ++ "active power % / full %  purity %  matrix sum %  Parseval residual %"
            ).format(
                if(~qriParsevalMode == 0, {
                    "FIXED RMS / BASIS TIMBRE"
                }, { "PURITY -> ENERGY" }),
                if(~qriParsevalMode == 0, {
                    basisNames[~qriParsevalBasis]
                }, { "unitary FFT2(rho), row-power pooled" }),
                ~qriParsevalTargetRMS.round(0.0001), predictedRMS.round(0.0001),
                activePower.round(0.000001), fullPower.round(0.000001),
                (frame[\purity] ? 0.0).round(0.000001),
                (frame[\matrixPowerSum] ? 0.0).round(0.000001),
                (frame[\parsevalResidual] ? 0.0).round(0.000000000001)
            )
        )
    };
};

openChebyshevControls = {
    if(~qriChebWindow.notNil, { ~qriChebWindow.front }, {
        ~qriChebWindow = Window("QHO Parseval Membrane Exciter", Rect(250, 54, 760, 680))
            .front.background_(panelColor);
        StaticText(~qriChebWindow, Rect(16, 12, 728, 24))
            .string_("QHO PARSEVAL MEMBRANE EXCITER  /  READ-ONLY SOUND MAPPING")
            .font_(Font("Helvetica Neue", 14, true)).stringColor_(textColor);
        StaticText(~qriChebWindow, Rect(16, 42, 728, 46))
            .string_("FIXED RMS redistributes basis probabilities; PURITY -> ENERGY preserves the unitary matrix-spectrum norm. Both consume the current rho without changing it or scheduling events.")
            .stringColor_(textColor);

        StaticText(~qriChebWindow, Rect(16, 100, 96, 20))
            .string_("POWER MODE").stringColor_(Color.fromHexString("8ecae6"));
        ~qriParsevalModeMenu = styleMenu.(PopUpMenu(~qriChebWindow, Rect(112, 96, 308, 26))
            .items_(["FIXED RMS / BASIS TIMBRE", "PURITY -> ENERGY"])
            .value_(~qriParsevalMode)
            .action_({ |menu|
                ~qriParsevalMode = menu.value; ~qriPushParsevalControls.value
            }));
        StaticText(~qriChebWindow, Rect(434, 100, 72, 20))
            .string_("BASIS").stringColor_(Color.fromHexString("8ecae6"));
        ~qriParsevalBasisMenu = styleMenu.(PopUpMenu(~qriChebWindow, Rect(506, 96, 238, 26))
            .items_(["FOCK", "QFT-16", "WALSH-HADAMARD"])
            .value_(~qriParsevalBasis)
            .action_({ |menu|
                ~qriParsevalBasis = menu.value; ~qriPushParsevalControls.value
            }));
        ~qriParsevalTargetRMSSlider = styleSlider.(EZSlider(
            ~qriChebWindow, Rect(16, 138, 354, 30),
            "target carrier RMS", ControlSpec(0, 0.5, \lin, 0.0001), { |view|
                ~qriParsevalTargetRMS = view.value; ~qriPushParsevalControls.value
            }, ~qriParsevalTargetRMS, labelWidth: 124, numberWidth: 58
        ));
        ~qriChebGainSlider = styleSlider.(EZSlider(~qriChebWindow, Rect(390, 138, 354, 30),
            "post-map gain", ControlSpec(0, 1.5, \lin, 0.001), { |view|
                ~qriChebGain = view.value; ~qriPushChebControls.value
            }, ~qriChebGain, labelWidth: 104, numberWidth: 54));

        StaticText(~qriChebWindow, Rect(16, 184, 94, 20))
            .string_("FORCE TYPE").stringColor_(Color.fromHexString("8ecae6"));
        ~qriChebModeMenu = styleMenu.(PopUpMenu(~qriChebWindow, Rect(112, 180, 258, 26))
            .items_(["IMPACT / nonnegative contact", "ACTUATOR / signed Chebyshev"])
            .value_(~qriChebMode)
            .action_({ |menu| ~qriChebMode = menu.value; ~qriPushChebControls.value }));
        StaticText(~qriChebWindow, Rect(390, 184, 116, 20))
            .string_("TIME CALIBRATION").stringColor_(Color.fromHexString("8ecae6"));
        ~qriChebCalibrationMenu = styleMenu.(PopUpMenu(~qriChebWindow, Rect(506, 180, 238, 26))
            .items_(["PHYSICAL impulse / peak", "ENERGY Parseval L2"])
            .value_(~qriChebCalibration)
            .action_({ |menu|
                ~qriChebCalibration = menu.value; ~qriPushChebControls.value
            }));
        ~qriChebContactSlider = styleSlider.(EZSlider(~qriChebWindow, Rect(16, 222, 354, 30),
            "contact (s)", ControlSpec(0.001, 0.5, \exp, 0.0001), { |view|
                ~qriChebContactSeconds = view.value; ~qriPushChebControls.value
            }, ~qriChebContactSeconds, labelWidth: 104, numberWidth: 62));
        ~qriChebIncidenceSlider = styleSlider.(EZSlider(~qriChebWindow, Rect(390, 222, 354, 30),
            "incidence deg", ControlSpec(0, 90, \lin, 0.1), { |view|
                ~qriChebIncidence = view.value * pi / 180; ~qriPushChebControls.value
            }, ~qriChebIncidence * 180 / pi, labelWidth: 104, numberWidth: 54));
        ~qriChebOrderSlider = styleSlider.(EZSlider(~qriChebWindow, Rect(16, 264, 354, 30),
            "Cheb order", ControlSpec(1, 16, \lin, 1), { |view|
                ~qriChebOrder = view.value.round.asInteger;
                ~qriPushChebControls.value; refreshParsevalControls.value
            }, ~qriChebOrder, labelWidth: 104, numberWidth: 54));
        ~qriChebCoherenceSlider = styleSlider.(EZSlider(~qriChebWindow, Rect(390, 264, 354, 30),
            "spectral phase", ControlSpec(0, 1, \lin, 0.001), { |view|
                ~qriChebCoherenceDepth = view.value; ~qriPushChebControls.value
            }, ~qriChebCoherenceDepth, labelWidth: 104, numberWidth: 54));
        ~qriChebDecaySlider = styleSlider.(EZSlider(~qriChebWindow, Rect(16, 306, 354, 30),
            "membrane decay", ControlSpec(0.02, 6, \exp, 0.001), { |view|
                ~qriChebDecay = view.value; ~qriPushChebControls.value
            }, ~qriChebDecay, labelWidth: 104, numberWidth: 54));
        Button(~qriChebWindow, Rect(390, 306, 354, 34))
            .states_([["AUDITION CURRENT QHO  /  no quantum-state change",
                Color.black, Color.fromHexString("80ed99")]])
            .action_({ ~qriAuditionChebyshev.value });
        ~qriParsevalMetrics = StaticText(~qriChebWindow, Rect(16, 356, 728, 54))
            .font_(Font("Menlo", 9, true)).stringColor_(Color.fromHexString("f2cc8f"));
        StaticText(~qriChebWindow, Rect(16, 420, 728, 18))
            .string_("SELECTED POWER DISTRIBUTION  /  display peak-normalized only")
            .stringColor_(Color.fromHexString("8ecae6"));
        ~qriParsevalSpectrumView = MultiSliderView(~qriChebWindow, Rect(16, 442, 728, 84))
            .size_(16).isFilled_(true)
            .fillColor_(Color.fromHexString("ff7ac6")).background_(fieldColor);
        StaticText(~qriChebWindow, Rect(16, 540, 728, 48))
            .string_("The Parseval modes apply to the signed ACTUATOR carrier. IMPACT remains a nonnegative Gaussian contact pulse. Target RMS is measured before its Gaussian window, event magnitude, membrane, and master gain.")
            .stringColor_(Color.fromHexString("f2cc8f"));
        StaticText(~qriChebWindow, Rect(16, 596, 728, 58))
            .string_("QFT/Hadamard populations reveal coherence through basis choice. PURITY mode uses unitary FFT2(rho) row-power pooling, so the 16 powers sum to Tr(rho^2). Strike position and timing remain owned by admitted Hilbert-current events.")
            .stringColor_(textColor);
        ~qriChebWindow.onClose = {
            ~qriChebWindow = nil;
            ~qriChebGainSlider = nil; ~qriChebModeMenu = nil;
            ~qriChebCalibrationMenu = nil; ~qriChebContactSlider = nil;
            ~qriChebIncidenceSlider = nil; ~qriChebOrderSlider = nil;
            ~qriChebCoherenceSlider = nil; ~qriChebDecaySlider = nil;
            ~qriParsevalModeMenu = nil; ~qriParsevalBasisMenu = nil;
            ~qriParsevalTargetRMSSlider = nil; ~qriParsevalMetrics = nil;
            ~qriParsevalSpectrumView = nil;
        };
        ~qriPushChebControls.value;
        ~qriPushParsevalControls.value;
    });
};
~qriOpenChebyshevControls = openChebyshevControls;

openMiRingsControls = {
    var modelMenu;
    ~qriMiRingsWindow !? _.close;
    ~qriMiRingsWindow = Window("QMW MiRings Resonator Audition", Rect(230, 150, 700, 330))
        .front.background_(Color.fromHexString("11151c"));
    StaticText(~qriMiRingsWindow, Rect(16, 12, 668, 26))
        .string_("MIRINGS PHYSICAL RESONATOR  /  OPTIONAL EVENT AUDITION")
        .font_(Font("Helvetica Neue", 14, true)).stringColor_(Color.fromHexString("dcecff"));
    StaticText(~qriMiRingsWindow, Rect(16, 44, 668, 22))
        .string_(if(~qriMiRingsAvailable, {
            "Installed mi-UGens adapter. Strike is a finite local audition; it does not alter QMW state or the Field body."
        }, {
            "MiRings unavailable. Recompile SuperCollider after installing mi-UGens, then relaunch this instrument."
        }))
        .stringColor_(if(~qriMiRingsAvailable, { Color.fromHexString("80ed99") }, { Color.fromHexString("ffd166") }));
    styleSlider.(EZSlider(~qriMiRingsWindow, Rect(16, 78, 320, 28), "pitch", ControlSpec(24, 96, \lin, 0.01),
        { |view| ~qriMiRingsPitch = view.value }, ~qriMiRingsPitch, labelWidth: 68, numberWidth: 52));
    styleSlider.(EZSlider(~qriMiRingsWindow, Rect(348, 78, 320, 28), "gain", ControlSpec(0, 0.3, \lin, 0.001),
        { |view| ~qriMiRingsGain = view.value }, ~qriMiRingsGain, labelWidth: 68, numberWidth: 52));
    styleSlider.(EZSlider(~qriMiRingsWindow, Rect(16, 116, 320, 28), "structure", ControlSpec(0, 1, \lin, 0.001),
        { |view| ~qriMiRingsStructure = view.value }, ~qriMiRingsStructure, labelWidth: 68, numberWidth: 52));
    styleSlider.(EZSlider(~qriMiRingsWindow, Rect(348, 116, 320, 28), "brightness", ControlSpec(0, 1, \lin, 0.001),
        { |view| ~qriMiRingsBrightness = view.value }, ~qriMiRingsBrightness, labelWidth: 68, numberWidth: 52));
    styleSlider.(EZSlider(~qriMiRingsWindow, Rect(16, 154, 320, 28), "damping", ControlSpec(0, 1, \lin, 0.001),
        { |view| ~qriMiRingsDamping = view.value }, ~qriMiRingsDamping, labelWidth: 68, numberWidth: 52));
    styleSlider.(EZSlider(~qriMiRingsWindow, Rect(348, 154, 320, 28), "position", ControlSpec(0, 1, \lin, 0.001),
        { |view| ~qriMiRingsPosition = view.value }, ~qriMiRingsPosition, labelWidth: 68, numberWidth: 52));
    modelMenu = styleMenu.(PopUpMenu(~qriMiRingsWindow, Rect(16, 202, 320, 28))
        .items_(["modal", "sympathetic", "modulated", "inharmonic", "string", "FM", "hidden"])
        .value_(~qriMiRingsModel).action_({ |menu| ~qriMiRingsModel = menu.value }));
    Button(~qriMiRingsWindow, Rect(348, 198, 154, 38))
        .states_([["STRIKE MIRINGS  /  finite audition", Color.black, Color.fromHexString("8ecae6")]])
        .enabled_(~qriMiRingsAvailable)
        .action_({ ~qriAuditionMiRings.value });
    Button(~qriMiRingsWindow, Rect(514, 198, 154, 38))
        .states_([["TEST EVENT LANE", Color.black, Color.fromHexString("80ed99")]])
        .enabled_(~qriMiRingsAvailable)
        .action_({ ~qriAuditionMiRingsEvent.value });
    StaticText(~qriMiRingsWindow, Rect(16, 258, 668, 40))
        .string_("TEST EVENT LANE uses the actual sixth mixer channel. This GPL-3.0 third-party plugin by v7b1 is an optional sound-design adapter, not QMW dynamics. MiClouds is intentionally not connected to the feedback path yet.")
        .stringColor_(textColor);
    ~qriMiRingsWindow.onClose = { ~qriMiRingsWindow = nil };
};
~qriOpenMiRingsControls = openMiRingsControls;

openMiRingsSixControls = {
    var sixWindow;
    if(~qriMiRingsSixWindow.notNil, { ~qriMiRingsSixWindow.front }, {
        sixWindow = Window("QMW Simple Six MiRings Voices", Rect(230, 120, 720, 480))
            .front.background_(Color.fromHexString("11151c"));
        ~qriMiRingsSixWindow = sixWindow;
        StaticText(sixWindow, Rect(16, 14, 688, 26))
            .string_("SIMPLE SIX MIRINGS VOICES  /  ONE BOUNDED PHYSICAL-MODEL GRAPH")
            .font_(Font("Helvetica Neue", 13, true)).stringColor_(Color.fromHexString("dcecff"));
        StaticText(sixWindow, Rect(16, 44, 688, 38))
            .string_(if(~qriMiRingsAvailable, {
                "Six parallel MiRings voices replace the native event bank. Simple through MiRings faders are voices 1-6; their mute, fuzz send, and delay send remain active."
            }, {
                "MiRings unavailable. Install mi-UGens, recompile SuperCollider, then relaunch V3."
            })).stringColor_(if(~qriMiRingsAvailable, { textColor }, { Color.fromHexString("ffd166") }));
        Button(sixWindow, Rect(16, 92, 260, 30))
            .states_([
                ["SIX MIRINGS BYPASSED", Color.fromHexString("ffd166"), Color.fromHexString("532b35")],
                ["SIX MIRINGS ACTIVE", Color.black, Color.fromHexString("80ed99")]
            ]).enabled_(~qriMiRingsAvailable).value_(~qriMiRingsSixEnabled.asInteger)
            .action_({ |button|
                if(button.value > 0, { ~qriActivateMiRingsSix.value }, { ~qriDisableMiRingsSix.value });
            });
        styleSlider.(EZSlider(sixWindow, Rect(292, 92, 196, 30), "base pitch",
            ControlSpec(24, 84, \lin, 0.01), { |view| ~qriMiRingsPitch = view.value },
            ~qriMiRingsPitch, labelWidth: 68, numberWidth: 48));
        styleSlider.(EZSlider(sixWindow, Rect(504, 92, 196, 30), "all tails s",
            ControlSpec(0.08, 0.80, \lin, 0.01), { |view|
                ~qriMiRingsSixDecay = view.value;
                6.do { |index| ~qriVoiceDecays[index] = view.value };
                ~qriDecay = ~qriVoiceDecays.maxItem;
                ~qriPushVoiceDecays.value;
                ~qriCoalesceLongDecayQueue.value;
            },
            ~qriMiRingsSixDecay, labelWidth: 48, numberWidth: 48));
        styleSlider.(EZSlider(sixWindow, Rect(16, 136, 214, 27), "structure",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriMiRingsStructure = view.value },
            ~qriMiRingsStructure, labelWidth: 68, numberWidth: 48));
        styleSlider.(EZSlider(sixWindow, Rect(246, 136, 214, 27), "brightness",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriMiRingsBrightness = view.value },
            ~qriMiRingsBrightness, labelWidth: 72, numberWidth: 48));
        styleSlider.(EZSlider(sixWindow, Rect(476, 136, 224, 27), "damping",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriMiRingsDamping = view.value },
            ~qriMiRingsDamping, labelWidth: 62, numberWidth: 48));
        StaticText(sixWindow, Rect(16, 178, 688, 22))
            .string_("VOICE PITCH OFFSETS  /  each lane is one existing mixer channel")
            .stringColor_(Color.fromHexString("8ecae6"));
        6.do { |index|
            var column = index % 2;
            var row = (index / 2).floor;
            var x = 16 + (column * 350);
            var y = 210 + (row * 62);
            StaticText(sixWindow, Rect(x, y, 120, 22))
                .string_("VOICE %  /  %".format(index + 1, ~qriVoiceNames[index]))
                .stringColor_(textColor);
            styleSlider.(EZSlider(sixWindow, Rect(x + 126, y, 208, 24), "semi",
                ControlSpec(-24, 36, \lin, 1), { |view|
                    ~qriMiRingsSixPitchOffsets[index] = view.value.round
                }, ~qriMiRingsSixPitchOffsets[index], labelWidth: 36, numberWidth: 44));
        };
        StaticText(sixWindow, Rect(16, 414, 688, 44))
            .string_("Safety: one finite six-voice graph at a time; each lane uses its mixer decay capped at 0.80 s here. ALL TAILS sets lanes 1-6 together. No active tail is force-freed.")
            .stringColor_(Color.fromHexString("ffcf70"));
        sixWindow.onClose = { if(~qriMiRingsSixWindow === sixWindow) { ~qriMiRingsSixWindow = nil } };
    });
};
~qriOpenMiRingsSixControls = openMiRingsSixControls;

~qriAuditionMIVoice = { |voiceIndex|
    if((~qriEffectiveVoiceGains.value[voiceIndex] ? 0) > 0.0001, {
        ~qriRenderEvent.value((
            energy: 0.48, dominant: 5, voiceIndex: voiceIndex,
            weights: Array.fill(modeCount, { |index| (1 - (index / 28)).max(0.22) }),
            phases: Array.fill(modeCount, { |index| index * 0.17 })
        ), 1.0);
    }, {
        ("Raise the % mixer fader before auditioning.".format(~qriVoiceNames[voiceIndex])).warn;
    });
};

openMIVoiceControls = {
    var window;
    if(~qriMIVoiceWindow.notNil, { ~qriMIVoiceWindow.front }, {
        window = Window("QMW MI Event Voices", Rect(210, 90, 760, 520)).front
            .background_(panelColor);
        ~qriMIVoiceWindow = window;
        StaticText(window, Rect(16, 12, 728, 24))
            .string_("MUTABLE INSTRUMENTS SOUND ADAPTERS  /  EVENT-GATED LANES 6-8")
            .font_(Font("Helvetica Neue", 14, true)).stringColor_(Color.fromHexString("dcecff"));
        StaticText(window, Rect(16, 42, 728, 38))
            .string_("MiRings, MiPlaits, and MiElements receive only admitted QMW event descriptors. Their faders, mutes, fuzz, delay, and FX sends remain the sole audio owners.")
            .stringColor_(Color.fromHexString("a9c5dd"));
        StaticText(window, Rect(16, 88, 352, 22)).string_(if(~qriMiPlaitsAvailable,
            { "MIPLAITS  /  INSTALLED" }, { "MIPLAITS  /  UNAVAILABLE" }))
            .stringColor_(if(~qriMiPlaitsAvailable, { Color.fromHexString("80ed99") }, { Color.fromHexString("ffd166") }));
        StaticText(window, Rect(392, 88, 352, 22)).string_(if(~qriMiElementsAvailable,
            { "MIELEMENTS  /  INSTALLED" }, { "MIELEMENTS  /  UNAVAILABLE" }))
            .stringColor_(if(~qriMiElementsAvailable, { Color.fromHexString("80ed99") }, { Color.fromHexString("ffd166") }));
        styleSlider.(EZSlider(window, Rect(16, 118, 352, 27), "engine / voice #",
            ControlSpec(0, 23, \lin, 1), { |view| ~qriPlaitsEngine = view.value.round },
            ~qriPlaitsEngine, labelWidth: 106, numberWidth: 48));
        styleSlider.(EZSlider(window, Rect(16, 152, 352, 27), "harmonics",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriPlaitsHarmonics = view.value },
            ~qriPlaitsHarmonics, labelWidth: 88, numberWidth: 50));
        styleSlider.(EZSlider(window, Rect(16, 186, 352, 27), "timbre",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriPlaitsTimbre = view.value },
            ~qriPlaitsTimbre, labelWidth: 88, numberWidth: 50));
        styleSlider.(EZSlider(window, Rect(16, 220, 352, 27), "morph",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriPlaitsMorph = view.value },
            ~qriPlaitsMorph, labelWidth: 88, numberWidth: 50));
        styleSlider.(EZSlider(window, Rect(16, 254, 352, 27), "LPG decay",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriPlaitsDecay = view.value },
            ~qriPlaitsDecay, labelWidth: 88, numberWidth: 50));
        Button(window, Rect(16, 292, 352, 34))
            .states_([["AUDITION MIPLAITS LANE 7", Color.black, Color.fromHexString("80ed99")]])
            .enabled_(~qriMiPlaitsAvailable).action_({ ~qriAuditionMIVoice.value(6) });
        styleSlider.(EZSlider(window, Rect(392, 118, 352, 27), "contour",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriElementsContour = view.value },
            ~qriElementsContour, labelWidth: 82, numberWidth: 50));
        styleSlider.(EZSlider(window, Rect(392, 152, 352, 27), "bow level",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriElementsBow = view.value },
            ~qriElementsBow, labelWidth: 82, numberWidth: 50));
        styleSlider.(EZSlider(window, Rect(392, 186, 352, 27), "blow level",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriElementsBlow = view.value },
            ~qriElementsBlow, labelWidth: 82, numberWidth: 50));
        styleSlider.(EZSlider(window, Rect(392, 220, 352, 27), "strike level",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriElementsStrike = view.value },
            ~qriElementsStrike, labelWidth: 82, numberWidth: 50));
        styleSlider.(EZSlider(window, Rect(392, 254, 352, 27), "geometry",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriElementsGeometry = view.value },
            ~qriElementsGeometry, labelWidth: 82, numberWidth: 50));
        styleSlider.(EZSlider(window, Rect(392, 288, 352, 27), "brightness",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriElementsBrightness = view.value },
            ~qriElementsBrightness, labelWidth: 82, numberWidth: 50));
        styleSlider.(EZSlider(window, Rect(392, 322, 352, 27), "damping",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriElementsDamping = view.value },
            ~qriElementsDamping, labelWidth: 82, numberWidth: 50));
        styleSlider.(EZSlider(window, Rect(392, 356, 352, 27), "space",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriElementsSpace = view.value },
            ~qriElementsSpace, labelWidth: 82, numberWidth: 50));
        styleSlider.(EZSlider(window, Rect(392, 390, 352, 27), "model #",
            ControlSpec(0, 2, \lin, 1), { |view| ~qriElementsModel = view.value.round },
            ~qriElementsModel, labelWidth: 82, numberWidth: 50));
        Button(window, Rect(392, 426, 352, 34))
            .states_([["AUDITION MIELEMENTS LANE 8", Color.black, Color.fromHexString("80ed99")]])
            .enabled_(~qriMiElementsAvailable).action_({ ~qriAuditionMIVoice.value(7) });
        Button(window, Rect(16, 344, 352, 34))
            .states_([["MIRINGS CONTROLS", textColor, Color.fromHexString("263241")]])
            .action_({ openMiRingsControls.value });
        Button(window, Rect(16, 386, 352, 34))
            .states_([["SIMPLE SIX MIRINGS EXPERIMENT", textColor, Color.fromHexString("263241")]])
            .action_({ openMiRingsSixControls.value });
        StaticText(window, Rect(16, 474, 728, 28))
            .string_("mi-UGens is optional GPL-3.0 runtime DSP; no Mutable Instruments source is copied here. These controls never evolve rho.")
            .stringColor_(Color.fromHexString("ffcf70"));
        window.onClose = { if(~qriMIVoiceWindow === window) { ~qriMIVoiceWindow = nil } };
    });
};
~qriOpenMIVoiceControls = openMIVoiceControls;

openFXControls = {
    var window, cloudsSetter, vstStatus, slotCountMenu, topologyMenu;
    if(~qriFXWindow.notNil, { ~qriFXWindow.front }, {
        cloudsSetter = { ensureCloudsReturn.value };
        window = Window("QMW Stereo FX Rack", Rect(110, 34, 1040, 930)).front
            .background_(panelColor);
        ~qriFXWindow = window;
        if(~qriVSTAvailable, { ensureVSTRack.value });
        StaticText(window, Rect(16, 12, 1008, 24))
            .string_("STEREO FX SEND / RETURN  /  MICLOUDS + FOUR-SLOT VST RACK")
            .font_(Font("Helvetica Neue", 14, true)).stringColor_(Color.fromHexString("dcecff"));
        StaticText(window, Rect(16, 42, 1008, 38))
            .string_("All eight post-voice sends converge here. Clouds remains parallel; VST slots can form a serial chain or latency-aligned parallel branches.")
            .stringColor_(Color.fromHexString("a9c5dd"));
        StaticText(window, Rect(16, 86, 384, 22)).string_(if(~qriMiCloudsAvailable,
            { "MICLOUDS  /  INSTALLED" }, { "MICLOUDS  /  UNAVAILABLE" }))
            .stringColor_(if(~qriMiCloudsAvailable, { Color.fromHexString("80ed99") }, { Color.fromHexString("ffd166") }));
        styleSlider.(EZSlider(window, Rect(16, 116, 384, 28), "Clouds return",
            ControlSpec(0, 1, \lin, 0.001), { |view|
                ~qriCloudsReturn = view.value; cloudsSetter.value
            }, ~qriCloudsReturn, labelWidth: 98, numberWidth: 52));
        styleSlider.(EZSlider(window, Rect(16, 150, 384, 28), "pitch",
            ControlSpec(-48, 48, \lin, 0.01), { |view| ~qriCloudsPitch = view.value; cloudsSetter.value },
            ~qriCloudsPitch, labelWidth: 76, numberWidth: 52));
        styleSlider.(EZSlider(window, Rect(16, 184, 384, 28), "position",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriCloudsPosition = view.value; cloudsSetter.value },
            ~qriCloudsPosition, labelWidth: 76, numberWidth: 52));
        styleSlider.(EZSlider(window, Rect(16, 218, 384, 28), "size",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriCloudsSize = view.value; cloudsSetter.value },
            ~qriCloudsSize, labelWidth: 76, numberWidth: 52));
        styleSlider.(EZSlider(window, Rect(16, 252, 384, 28), "density",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriCloudsDensity = view.value; cloudsSetter.value },
            ~qriCloudsDensity, labelWidth: 76, numberWidth: 52));
        styleSlider.(EZSlider(window, Rect(16, 286, 384, 28), "texture",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriCloudsTexture = view.value; cloudsSetter.value },
            ~qriCloudsTexture, labelWidth: 76, numberWidth: 52));
        styleSlider.(EZSlider(window, Rect(16, 320, 384, 28), "dry / wet",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriCloudsDryWet = view.value; cloudsSetter.value },
            ~qriCloudsDryWet, labelWidth: 76, numberWidth: 52));
        styleSlider.(EZSlider(window, Rect(16, 354, 384, 28), "input gain",
            ControlSpec(0.125, 8, \exp, 0.001), { |view| ~qriCloudsInputGain = view.value; cloudsSetter.value },
            ~qriCloudsInputGain, labelWidth: 76, numberWidth: 52));
        styleSlider.(EZSlider(window, Rect(420, 116, 384, 28), "spread",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriCloudsSpread = view.value; cloudsSetter.value },
            ~qriCloudsSpread, labelWidth: 76, numberWidth: 52));
        styleSlider.(EZSlider(window, Rect(420, 150, 384, 28), "reverb",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriCloudsReverb = view.value; cloudsSetter.value },
            ~qriCloudsReverb, labelWidth: 76, numberWidth: 52));
        styleSlider.(EZSlider(window, Rect(420, 184, 384, 28), "feedback",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriCloudsFeedback = view.value; cloudsSetter.value },
            ~qriCloudsFeedback, labelWidth: 76, numberWidth: 52));
        Button(window, Rect(420, 224, 120, 32)).states_([
            ["LIVE", textColor, Color.fromHexString("263241")],
            ["FREEZE", Color.fromHexString("ffd166"), Color.fromHexString("532b35")]
        ]).value_(~qriCloudsFreeze).action_({ |button|
            ~qriCloudsFreeze = button.value; cloudsSetter.value
        });
        Button(window, Rect(552, 224, 120, 32)).states_([
            ["HI-FI", textColor, Color.fromHexString("263241")],
            ["LO-FI", Color.fromHexString("ffd166"), Color.fromHexString("532b35")]
        ]).value_(~qriCloudsLofi).action_({ |button|
            ~qriCloudsLofi = button.value; cloudsSetter.value
        });
        styleMenu.(PopUpMenu(window, Rect(684, 224, 120, 32))
            .items_(["Granular", "Stretch", "Loop delay", "Spectral"])
            .value_(~qriCloudsMode).action_({ |menu|
                ~qriCloudsMode = menu.value; cloudsSetter.value
            }));
        Button(window, Rect(420, 268, 384, 36))
            .states_([["TRIGGER CLOUDS BUFFER", Color.black, Color.fromHexString("80ed99")]])
            .enabled_(~qriMiCloudsAvailable).action_({ ~qriTriggerClouds.value });
        StaticText(window, Rect(420, 320, 384, 62))
            .string_("Complete MiClouds surface: pit, pos, size, dens, tex, drywet, in_gain, spread, rvb, fb, freeze, mode, lofi, trig. The return fader owns its final gain.")
            .stringColor_(Color.fromHexString("ffcf70"));
        StaticText(window, Rect(16, 410, 1008, 22))
            .string_("VST EFFECT RACK  /  2-4 slots, hard bypass, user presets, reported latency")
            .stringColor_(Color.fromHexString("8ecae6"));
        styleSlider.(EZSlider(window, Rect(16, 442, 300, 28), "Rack return",
            ControlSpec(0, 1, \lin, 0.001), { |view|
                ~qriVSTRackReturn = view.value; ~qriVSTReturn = view.value;
                ensureVSTRack.value; applyVSTRackRouting.value
            }, ~qriVSTRackReturn, labelWidth: 98, numberWidth: 52));
        slotCountMenu = styleMenu.(PopUpMenu(window, Rect(330, 442, 132, 28))
            .items_(["2 slots", "3 slots", "4 slots"])
            .value_(~qriVSTRackSlotCount - 2).action_({ |menu|
                ~qriVSTRackSlotCount = menu.value + 2; applyVSTRackRouting.value
            }));
        topologyMenu = styleMenu.(PopUpMenu(window, Rect(476, 442, 146, 28))
            .items_(["SERIAL", "PARALLEL"])
            .value_(~qriVSTRackTopology).action_({ |menu|
                ~qriVSTRackTopology = menu.value; applyVSTRackRouting.value
            }));
        vstStatus = StaticText(window, Rect(636, 438, 388, 38))
            .string_(if(~qriVSTAvailable,
                { "VST rack ready; latency is reported in samples and milliseconds." },
                { "VSTPlugin language classes are unavailable in this sclang session; relaunch after enabling the extension." }))
            .stringColor_(if(~qriVSTAvailable, { Color.fromHexString("80ed99") }, { Color.fromHexString("ffd166") }));
        ~qriVSTStatus = vstStatus;
        Button(window, Rect(16, 480, 184, 32)).states_([["SCAN VST PATHS", textColor, Color.fromHexString("263241")]])
            .enabled_(~qriVSTAvailable).action_({
                scanVSTPlugins.(vstStatus, {
                    vstStatus.string_("VST scan complete. Press SELECT VST on any slot.")
                });
            });
        StaticText(window, Rect(216, 484, 808, 24))
            .string_("Parallel mode aligns loaded live branches to the largest VST latency. Serial mode reports the sum.")
            .stringColor_(Color.fromHexString("a9c5dd"));
        4.do { |index|
            var y = 524 + (index * 82);
            var presetField;
            ~qriVSTRackStatusViews[index] = StaticText(window, Rect(16, y, 200, 30))
                .string_("SLOT %  EMPTY  /  0 smp".format(index + 1))
                .stringColor_(Color.fromHexString("dcecff"));
            Button(window, Rect(224, y, 86, 30)).states_([
                ["LIVE", textColor, Color.fromHexString("263241")],
                ["BYPASS", Color.fromHexString("ffd166"), Color.fromHexString("532b35")]
            ]).value_(~qriVSTRackBypasses[index]).enabled_(~qriVSTAvailable).action_({ |button|
                ~qriVSTRackBypasses[index] = button.value; applyVSTRackRouting.value
            });
            styleSlider.(EZSlider(window, Rect(318, y, 220, 30), "trim",
                ControlSpec(0, 1.5, \lin, 0.001), { |view|
                    ~qriVSTRackSlotGains[index] = view.value; applyVSTRackRouting.value
                }, ~qriVSTRackSlotGains[index], labelWidth: 42, numberWidth: 48));
            Button(window, Rect(548, y, 92, 30))
                .states_([["SELECT VST", Color.black, Color.fromHexString("80ed99")]])
                .enabled_(~qriVSTAvailable).action_({
                    openVSTChooser.(index)
                });
            Button(window, Rect(648, y, 78, 30)).states_([["EDITOR", textColor, Color.fromHexString("263241")]])
                .enabled_(~qriVSTAvailable).action_({
                    ~qriVSTRackControllers[index] !? { |controller| controller.perform(\editor) }
                });
            Button(window, Rect(734, y, 78, 30)).states_([["GUI", textColor, Color.fromHexString("263241")]])
                .enabled_(~qriVSTAvailable).action_({
                    ~qriVSTRackControllers[index] !? { |controller| controller.perform(\gui) }
                });
            Button(window, Rect(820, y, 82, 30)).states_([["CLOSE", textColor, Color.fromHexString("532b35")]])
                .enabled_(~qriVSTAvailable).action_({
                    ~qriVSTRackControllers[index] !? { |controller| controller.perform(\close) }
                });
            presetField = TextField(window, Rect(224, y + 38, 314, 28))
                .string_((~qriVSTRackPresetNames[index] ? "QMW Rack Slot %".format(index + 1)).asString)
                .stringColor_(textColor).background_(Color.fromHexString("18212b"));
            ~qriVSTRackPresetFields[index] = presetField;
            StaticText(window, Rect(16, y + 38, 200, 28)).string_("User preset name")
                .stringColor_(Color.fromHexString("a9c5dd"));
            Button(window, Rect(548, y + 38, 92, 28)).states_([["STORE", textColor, Color.fromHexString("263241")]])
                .enabled_(~qriVSTAvailable).action_({
                    var controller = ~qriVSTRackControllers[index];
                    var name = presetField.string.stripWhiteSpace;
                    if(controller.notNil and: { controller.info.notNil } and: { name.notEmpty }, {
                        ~qriVSTRackPresetNames[index] = name;
                        controller.perform(\savePreset, name)
                    }, { "Load a plugin and enter a preset name first.".warn });
                });
            Button(window, Rect(648, y + 38, 92, 28)).states_([["RECALL", textColor, Color.fromHexString("263241")]])
                .enabled_(~qriVSTAvailable).action_({
                    ~qriVSTRackPresetNames[index] = presetField.string.stripWhiteSpace;
                    recallVSTRackSlotPreset.(index)
                });
        };
        ~qriRefreshVSTRackStatus.value;
        StaticText(window, Rect(16, 858, 1008, 30))
            .string_("Routing: 8 voice sends -> shared stereo bus -> Clouds plus VST rack -> outputs 1/2. The dry mixer is not latency-delayed.")
            .stringColor_(Color.fromHexString("a9c5dd"));
        StaticText(window, Rect(16, 892, 1008, 28))
            .string_("The FX bus is a downstream sound-design adapter. It does not alter H, Lindblad evolution, rho, observables, geometry, field evolution, memory, syndrome, recovery, or admitted-event energy.")
            .stringColor_(Color.fromHexString("ffcf70"));
        window.onClose = {
            if(~qriFXWindow === window) {
                ~qriFXWindow = nil; ~qriVSTStatus = nil;
                ~qriVSTRackStatusViews = Array.newClear(4);
                ~qriVSTRackPresetFields = Array.newClear(4)
            }
        };
    });
};
~qriOpenFXControls = openFXControls;

openProjectiveOutputs = {
    var gainView, delayView, bodyMenu, outBaseBox, masterSlider;
    ~qriProjectiveOutputWindow !? _.close;
    ~qriProjectiveOutputWindow = Window(
        "QMW 16 Projective Outputs", Rect(190, 130, 780, 370)
    ).front.background_(Color.fromHexString("11151c"));
    StaticText(~qriProjectiveOutputWindow, Rect(16, 10, 748, 24))
        .string_("P0-P15  /  DISCRETE OUTPUT GAIN + MUTE + CALIBRATION DELAY")
        .font_(Font("Helvetica Neue", 13, true)).stringColor_(Color.fromHexString("dcecff"));
    bodyMenu = styleMenu.(PopUpMenu(~qriProjectiveOutputWindow, Rect(16, 42, 224, 25))
        .items_(~qriFieldBodyNames).value_(~qriFieldBody).action_({ |menu|
            ~qriFieldBody = menu.value; ~qriApplyBodyMode.value
        }));
    masterSlider = styleSlider.(EZSlider(~qriProjectiveOutputWindow, Rect(252, 42, 260, 27),
        "field gain", ControlSpec(0, 0.4, \lin, 0.001), { |view|
            ~qriProjectiveGain = view.value;
            ~qriApplyBodyMode.value
        }, ~qriProjectiveGain, labelWidth: 70, numberWidth: 58));
    StaticText(~qriProjectiveOutputWindow, Rect(526, 44, 72, 22))
        .string_("out base").stringColor_(mutedTextColor);
    outBaseBox = styleNumberBox.(NumberBox(~qriProjectiveOutputWindow, Rect(598, 42, 54, 25))
        .value_(~qriProjectiveOutBase).clipLo_(0)
        .clipHi_((s.options.numOutputBusChannels - 16).max(0))
        .decimals_(0).action_({ |box|
            ~qriProjectiveOutBase = box.value.asInteger.clip(
                0, (s.options.numOutputBusChannels - 16).max(0)
            );
            if((~qrmOutputChannels ? 2) >= 16) { rebuildProjectiveBody.value };
        }));
    StaticText(~qriProjectiveOutputWindow, Rect(16, 80, 748, 18))
        .string_("CALIBRATION GAIN 0-2  /  one value per projector-output lane")
        .stringColor_(Color.fromHexString("8ecae6"));
    gainView = MultiSliderView(~qriProjectiveOutputWindow, Rect(16, 102, 748, 78))
        .size_(16).isFilled_(true).value_(~qriProjectiveGains / 2)
        .fillColor_(Color.fromHexString("ff67d4")).background_(Color.fromHexString("080b10"))
        .action_({ |view| ~qriProjectiveGains = view.value * 2; pushProjectiveCalibration.value });
    StaticText(~qriProjectiveOutputWindow, Rect(16, 188, 748, 18))
        .string_("TRANSDUCER DELAY 0-50 ms  /  per-lane alignment")
        .stringColor_(Color.fromHexString("8ecae6"));
    delayView = MultiSliderView(~qriProjectiveOutputWindow, Rect(16, 210, 748, 58))
        .size_(16).isFilled_(true).value_(~qriProjectiveDelays / 0.05)
        .fillColor_(Color.fromHexString("80ed99")).background_(Color.fromHexString("080b10"))
        .action_({ |view| ~qriProjectiveDelays = view.value * 0.05; pushProjectiveCalibration.value });
    16.do { |index|
        var x = 16 + (index * 47);
        Button(~qriProjectiveOutputWindow, Rect(x, 282, 42, 38))
            .states_([
                ["P%\nON".format(index), textColor, Color.fromHexString("263241")],
                ["P%\nMUTE".format(index), Color.fromHexString("ffd166"), Color.fromHexString("532b35")]
            ])
            .value_(~qriProjectiveMutes[index]).action_({ |button|
                ~qriProjectiveMutes[index] = button.value; pushProjectiveCalibration.value
            });
    };
    StaticText(~qriProjectiveOutputWindow, Rect(16, 332, 748, 24))
        .string_(if((~qrmOutputChannels ? 2) >= 16, {
            "TRUE 16-OUTPUT BODY ACTIVE: one projector per hardware output."
        }, {
            "Stereo monitor fold-down active. Select a 16-output device in the QRM audio panel for discrete transducers."
        })).stringColor_(Color.white.alpha_(0.74));
    ~qriProjectiveOutputWindow.onClose = { ~qriProjectiveOutputWindow = nil };
};
~qriOpenProjectiveOutputs = openProjectiveOutputs;

openTemporalMemoryControls = {
    var presetNames = ["rational", "cluster", "odd", "cascade"];
    var presetMenu, sendTemporal;
    if(~qriTemporalMemoryWindow.notNil, { ~qriTemporalMemoryWindow.front }, {
        sendTemporal = { |address, value|
            ~qriTemporalMemoryControlAddress !? { |socket| socket.sendMsg(address, value) }
        };
        ~qriTemporalMemoryWindow = Window(
            "QMW Temporal-Memory Performance", Rect(210, 100, 780, 400)
        ).front.background_(Color.fromHexString("11151c"));
        StaticText(~qriTemporalMemoryWindow, Rect(16, 12, 748, 24))
            .string_("TEMPORAL MEMORY  /  DOWNSTREAM 16-LINE DELAY FIELD")
            .font_(Font("Helvetica Neue", 14, true)).stringColor_(Color.fromHexString("dcecff"));
        StaticText(~qriTemporalMemoryWindow, Rect(16, 40, 748, 30))
            .string_("Time, rhythm, and feedback controls affect future observer frames only; tone, width, glide, and freeze are audio-adapter controls.")
            .stringColor_(textColor);
        presetMenu = styleMenu.(PopUpMenu(~qriTemporalMemoryWindow, Rect(16, 82, 224, 27))
            .items_(["RATIONAL", "CLUSTER", "ODD", "CASCADE"])
            .value_(presetNames.indexOfEqual(~qmwTemporalMemoryRatioPreset ? "rational") ? 0)
            .action_({ |view|
                ~qmwTemporalMemoryRatioPreset = presetNames[view.value];
                sendTemporal.value("/qmw/temporal_memory/v1/control/ratio_preset",
                    ~qmwTemporalMemoryRatioPreset)
            }));
        StaticText(~qriTemporalMemoryWindow, Rect(248, 84, 500, 22))
            .string_("RHYTHM MAP  /  declared musical delay ratios, not a quantum clock")
            .stringColor_(Color.fromHexString("8ecae6"));
        styleSlider.(EZSlider(~qriTemporalMemoryWindow, Rect(16, 122, 360, 27), "phase warp",
            ControlSpec(0, 0.40, \lin, 0.001), { |view|
                ~qmwTemporalMemoryPhaseWarp = view.value;
                sendTemporal.value("/qmw/temporal_memory/v1/control/phase_warp", view.value.asFloat)
            }, ~qmwTemporalMemoryPhaseWarp ? 0.23, labelWidth: 88, numberWidth: 56));
        styleSlider.(EZSlider(~qriTemporalMemoryWindow, Rect(388, 122, 376, 27), "cross feedback",
            ControlSpec(0, 0.42, \lin, 0.001), { |view|
                ~qmwTemporalMemoryFeedbackAmount = view.value;
                sendTemporal.value("/qmw/temporal_memory/v1/control/feedback_amount", view.value.asFloat)
            }, ~qmwTemporalMemoryFeedbackAmount ? 0.42, labelWidth: 70, numberWidth: 56));
        styleSlider.(EZSlider(~qriTemporalMemoryWindow, Rect(16, 162, 360, 27), "diffusion",
            ControlSpec(0, 1, \lin, 0.001), { |view|
                ~qmwTemporalMemoryDiffusion = view.value;
                sendTemporal.value("/qmw/temporal_memory/v1/control/diffusion", view.value.asFloat)
            }, ~qmwTemporalMemoryDiffusion ? 0, labelWidth: 74, numberWidth: 56));
        styleSlider.(EZSlider(~qriTemporalMemoryWindow, Rect(388, 162, 376, 27), "feedback tone",
            ControlSpec(700, 12000, \exp, 1), { |view|
                ~qmwTemporalMemorySetFeedbackTone !? { |setter| setter.value(view.value) }
            }, ~qmwTemporalMemoryFeedbackTone ? 6200, labelWidth: 98, numberWidth: 66));
        styleSlider.(EZSlider(~qriTemporalMemoryWindow, Rect(16, 202, 360, 27), "stereo width",
            ControlSpec(0, 1, \lin, 0.001), { |view|
                ~qmwTemporalMemorySetWidth !? { |setter| setter.value(view.value) }
            }, ~qmwTemporalMemoryWidth ? 0.7, labelWidth: 88, numberWidth: 56));
        styleSlider.(EZSlider(~qriTemporalMemoryWindow, Rect(388, 202, 376, 27), "glide",
            ControlSpec(0.005, 0.5, \exp, 0.001), { |view|
                ~qmwTemporalMemorySetGlideSeconds !? { |setter| setter.value(view.value) }
            }, ~qmwTemporalMemoryGlideSeconds ? 0.16, labelWidth: 54, numberWidth: 66));
        styleSlider.(EZSlider(~qriTemporalMemoryWindow, Rect(16, 242, 360, 27), "self feedback",
            ControlSpec(0, 0.92, \lin, 0.001), { |view|
                ~qmwTemporalMemorySetSelfFeedback !? { |setter| setter.value(view.value) }
            }, ~qmwTemporalMemorySelfFeedback ? 0.62, labelWidth: 126, numberWidth: 56));
        styleSlider.(EZSlider(~qriTemporalMemoryWindow, Rect(388, 242, 376, 27), "return fuzz",
            ControlSpec(0, 1, \lin, 0.001), { |view|
                ~qmwTemporalMemorySetMixer !? { |setter|
                    setter.value(~qmwTemporalMemoryMix ? 0.18, view.value)
                }
            }, ~qmwTemporalMemoryFuzzSend ? 0, labelWidth: 94, numberWidth: 56));
        Button(~qriTemporalMemoryWindow, Rect(16, 286, 244, 34))
            .states_([["AUDITION RETURN ONLY", textColor, Color.fromHexString("264653")]])
            .action_({ ~qmwTemporalMemoryAuditionReturn !? { |audition| audition.value } });
        Button(~qriTemporalMemoryWindow, Rect(272, 286, 244, 34))
            .states_([
                ["FOLLOW OBSERVER", textColor, Color.fromHexString("263241")],
                ["FREEZE DELAY FIELD", Color.fromHexString("ffd166"), Color.fromHexString("532b35")]
            ]).value_(if(~qmwTemporalMemoryFrozen, { 1 }, { 0 })).action_({ |button|
                ~qmwTemporalMemorySetFreeze !? { |setter| setter.value(button.value) }
            });
        StaticText(~qriTemporalMemoryWindow, Rect(528, 288, 236, 30))
            .string_("Freeze holds the last control frame; audio feedback continues.")
            .stringColor_(Color.fromHexString("ffcf70"));
        StaticText(~qriTemporalMemoryWindow, Rect(16, 346, 748, 34))
            .string_("AUDITION RETURN ONLY sends no dry main voice. MAIN MIXER: eight channel delay sends, return mix, self feedback, and base delay. Cross feedback is observer-derived; self feedback is the audible repeat control.")
            .stringColor_(textColor);
        ~qriTemporalMemoryWindow.onClose = { ~qriTemporalMemoryWindow = nil };
    });
};
~qriOpenTemporalMemoryControls = openTemporalMemoryControls;

openVoiceAllocatorControls = {
    var window, enabledButton, auxButton, sumButton;
    if(~qriAllocatorWindow.notNil, { ~qriAllocatorWindow.front }, {
        window = Window("QMW Dynamic Voice Allocator", Rect(220, 110, 690, 390))
            .front.background_(panelColor);
        ~qriAllocatorWindow = window;
        StaticText(window, Rect(16, 12, 658, 26))
            .string_("DYNAMIC VOICE ALLOCATION  /  CPU HEADROOM + OUTPUT SUM GUARD")
            .font_(Font("Helvetica Neue", 14, true))
            .stringColor_(Color.fromHexString("dcecff"));
        StaticText(window, Rect(16, 42, 658, 48))
            .string_("Measures scsynth average/peak CPU and downstream queue pressure. It changes only future sound-node admission and tail length; QMW frames and already-ringing nodes remain untouched.")
            .stringColor_(Color.fromHexString("a9c5dd"));
        enabledButton = Button(window, Rect(16, 98, 206, 30))
            .states_([
                ["ADAPTIVE BUDGET OFF", Color.fromHexString("ffd166"), Color.fromHexString("532b35")],
                ["ADAPTIVE BUDGET ON", Color.black, Color.fromHexString("80ed99")]
            ]).value_(~qriAllocatorEnabled.asInteger).action_({ |button|
                ~qriAllocatorEnabled = button.value > 0;
                ~qriApplyAllocatorPolicy.value;
                ~qriUpdateDynamicAllocator.value;
            });
        Button(window, Rect(238, 98, 206, 30))
            .states_([["RESET LIVE BUDGET TO MAX", textColor, Color.fromHexString("263241")]])
            .action_({
                ~qriDynamicVoiceBudget = ~qriMaxVoices;
                ~qriAllocatorHealthyTicks = 0;
                ~qriAllocatorLastAdjustAt = Main.elapsedTime;
                ~qriRefreshAllocatorControls.value;
            });
        Button(window, Rect(460, 98, 214, 30))
            .states_([["REFRESH TELEMETRY", textColor, Color.fromHexString("263241")]])
            .action_({ ~qriUpdateDynamicAllocator.value });
        styleSlider.(EZSlider(window, Rect(16, 144, 318, 30), "minimum voices",
            ControlSpec(1, 8, \lin, 1), { |view|
                ~qriAllocatorMinVoices = view.value.round.asInteger.min(~qriMaxVoices);
                ~qriApplyAllocatorPolicy.value;
            }, ~qriAllocatorMinVoices, labelWidth: 100, numberWidth: 48));
        styleSlider.(EZSlider(window, Rect(356, 144, 318, 30), "maximum voices",
            ControlSpec(2, 8, \lin, 1), { |view|
                ~qriMaxVoices = view.value.round.asInteger;
                ~qriAllocatorMinVoices = ~qriAllocatorMinVoices.min(~qriMaxVoices);
                ~qriApplyAllocatorPolicy.value;
            }, ~qriMaxVoices, labelWidth: 106, numberWidth: 48));
        styleSlider.(EZSlider(window, Rect(16, 184, 318, 30), "target headroom %",
            ControlSpec(20, 70, \lin, 1), { |view|
                ~qriAllocatorHeadroomTarget = view.value
            }, ~qriAllocatorHeadroomTarget, labelWidth: 112, numberWidth: 48));
        styleSlider.(EZSlider(window, Rect(356, 184, 318, 30), "critical peak CPU %",
            ControlSpec(55, 95, \lin, 1), { |view|
                ~qriAllocatorCriticalPeakCPU = view.value
            }, ~qriAllocatorCriticalPeakCPU, labelWidth: 122, numberWidth: 48));
        styleSlider.(EZSlider(window, Rect(16, 224, 318, 30), "recovery seconds",
            ControlSpec(1, 20, \lin, 0.5), { |view|
                ~qriAllocatorRecoverySeconds = view.value
            }, ~qriAllocatorRecoverySeconds, labelWidth: 106, numberWidth: 48));
        auxButton = Button(window, Rect(356, 224, 154, 30))
            .states_([
                ["AUX SHEDDING OFF", Color.fromHexString("ffd166"), Color.fromHexString("532b35")],
                ["AUX SHEDDING ON", Color.black, Color.fromHexString("80ed99")]
            ]).value_(~qriAllocatorAuxShedding.asInteger).action_({ |button|
                ~qriAllocatorAuxShedding = button.value > 0
            });
        sumButton = Button(window, Rect(520, 224, 154, 30))
            .states_([
                ["SUM GUARD OFF", Color.fromHexString("ffd166"), Color.fromHexString("532b35")],
                ["SUM GUARD ON", Color.black, Color.fromHexString("80ed99")]
            ]).value_(~qriAllocatorGainCompensation.asInteger).action_({ |button|
                ~qriAllocatorGainCompensation = button.value > 0
            });
        StaticText(window, Rect(16, 270, 658, 42))
            .string_("PROTECT falls fast; recovery adds one voice only after sustained headroom. Explicit MiRings/Plaits/Elements lanes remain eligible under pressure; only composite-event auxiliary fan-out is shed.")
            .stringColor_(Color.fromHexString("ffcf70"));
        ~qriAllocatorStatus = StaticText(window, Rect(16, 320, 658, 50))
            .font_(Font("Menlo", 11)).stringColor_(Color.fromHexString("80ed99"));
        ~qriRefreshAllocatorControls = {
            ~qriAllocatorStatus !? { |view|
                view.string_(
                    "state %  /  scsynth avg %%% peak %%%  /  live budget %/%\nnative %  MI %  queue %  shed %  auxiliary shed %"
                    .format(
                        ~qriAllocatorState.asString.toUpper,
                        ~qriAllocatorSmoothedCPU.round(0.1),
                        ~qriAllocatorPeakCPU.round(0.1),
                        ~qriCurrentVoiceBudget.value, ~qriMaxVoices,
                        ~qriNodes.size, ~qriMiVoiceNodes.size + ~qriMiRingsNodes.size,
                        ~qriPluckQueue.size, ~qriShedPlucks,
                        ~qriAllocatorAuxShedVoices
                    )
                )
            };
        };
        window.onClose = {
            if(~qriAllocatorWindow === window) {
                ~qriAllocatorWindow = nil;
                ~qriAllocatorStatus = nil;
                ~qriRefreshAllocatorControls = nil;
            };
        };
        ~qriRefreshAllocatorControls.value;
    });
};
~qriOpenVoiceAllocatorControls = openVoiceAllocatorControls;

openPolyrhythmControls = {
    var channelNames = ["Simple", "Gaussian", "Layered", "QHO FM", "LPG", "MiRings", "MiPlaits", "MiElements"];
    var polyWindow, enabledButton, baseSlider, rephaseButton;
    if(~qriPolyWindow.notNil, { ~qriPolyWindow.front }, {
        polyWindow = Window("QMW 16 Polyrhythmic Voices", Rect(150, 56, 850, 640));
        ~qriPolyWindow = polyWindow;
        polyWindow.background = panelColor;
        StaticText(polyWindow, Rect(16, 12, 818, 26))
            .string_("16 POLYRHYTHMIC VOICES  →  8 MIX CHANNELS")
            .font_(Font("Helvetica Neue", 16, true)).stringColor_(Color.fromHexString("dcecff"));
        StaticText(polyWindow, Rect(16, 42, 818, 36))
            .string_("Each lane has an independent clock and phase, but routes to a named mixer channel. Channel gain, mute, fuzz send, and delay send remain the sole audio owners.")
            .stringColor_(Color.fromHexString("a9c5dd"));
        enabledButton = Button(polyWindow, Rect(16, 88, 180, 30))
            .states_([
                ["16 LANE ENGINE OFF", Color.fromHexString("ffd166"), Color.fromHexString("532b35")],
                ["16 LANE ENGINE ON", Color.black, Color.fromHexString("80ed99")]
            ]).value_(~qriPolyEnabled.asInteger).action_({ |button|
                ~qriPolyEnabled = button.value > 0;
                if(~qriPolyEnabled, { ~qriStartPolyLanes.value }, { ~qriStopPolyLanes.value });
            });
        ~qriPolyEnabledButton = enabledButton;
        baseSlider = styleSlider.(EZSlider(polyWindow, Rect(210, 88, 300, 30), "base Hz",
            ControlSpec(0.05, 1.2, \exp, 0.001), { |view|
                ~qriPolyBaseHz = view.value
            }, ~qriPolyBaseHz, labelWidth: 60, numberWidth: 58));
        rephaseButton = Button(polyWindow, Rect(524, 88, 310, 30))
            .states_([["REPHASE 16 LANES ON NEXT CYCLE", textColor, Color.fromHexString("263241")]])
            .action_({ ~qriStartPolyLanes.value });
        StaticText(polyWindow, Rect(16, 128, 818, 18))
            .string_("rate = base × multiplier   /   phase is a fraction of that lane's cycle   /   no lane creates sound when its assigned mixer channel is down")
            .stringColor_(Color.fromHexString("8ecae6"));
        ~qriPolyLaneCount.do { |index|
            var column = (index / 8).floor;
            var row = index % 8;
            var x = 16 + (column * 414);
            var y = 156 + (row * 56);
            var channel = ~qriPolyLaneChannels[index];
            Button(polyWindow, Rect(x, y, 56, 46))
                .states_([
                    ["L%".format(index + 1), Color.fromHexString("ffd166"), Color.fromHexString("532b35")],
                    ["L%".format(index + 1), Color.black, Color.fromHexString("80ed99")]
                ]).value_(~qriPolyLaneEnabled[index]).action_({ |button|
                    ~qriPolyLaneEnabled[index] = button.value
                });
            StaticText(polyWindow, Rect(x + 62, y, 74, 20))
                .string_("→ " ++ channelNames[channel]).stringColor_(textColor);
            styleSlider.(EZSlider(polyWindow, Rect(x + 136, y, 168, 22), "×",
                ControlSpec(0.25, 3.0, \lin, 0.001), { |view|
                    ~qriPolyRateMultipliers[index] = view.value
                }, ~qriPolyRateMultipliers[index], labelWidth: 16, numberWidth: 40));
            styleSlider.(EZSlider(polyWindow, Rect(x + 136, y + 24, 168, 22), "φ",
                ControlSpec(0, 0.99, \lin, 0.001), { |view|
                    ~qriPolyPhaseFractions[index] = view.value
                }, ~qriPolyPhaseFractions[index], labelWidth: 16, numberWidth: 40));
        };
        StaticText(polyWindow, Rect(16, 612, 818, 18))
            .string_("This is a downstream rhythmic adapter over admitted events; it does not feed back into QMW state, Bures distance, or density evolution.")
            .stringColor_(Color.fromHexString("ffcf70"));
        polyWindow.onClose = {
            if(~qriPolyWindow === polyWindow) {
                ~qriPolyWindow = nil;
                ~qriPolyEnabledButton = nil;
            };
        };
        polyWindow.front;
    });
};
~qriOpenPolyrhythmControls = openPolyrhythmControls;

openPanel = {
    var enabledButton, bodyMenu, viewMenu, fieldGainSlider, mixSlider, gainSlider, decaySlider;
    var temporalMixSlider, temporalFocusSlider, temporalFeedbackSlider, temporalBaseDelaySlider;
    if(~qriWindow.notNil, { ~qriWindow.front }, {
        ~qriWindow = Window("QMW Integrated Resonant Instrument", Rect(130, 18, 860, 950)).front;
        ~qriWindow.background = Color.fromHexString("11151c");
        StaticText(~qriWindow, Rect(18, 12, 824, 28))
            .string_("HILBERT CURRENT + PROJECTIVE FIELD -> SELECTABLE RESONANT BODIES")
            .font_(Font("Helvetica Neue", 16, true))
            .stringColor_(Color.fromHexString("dcecff"));
        ~qriDiagram = UserView(~qriWindow, Rect(18, 50, 824, 300));
        ~qriDiagram.drawFunc = {
            case
            { ~qriViewMode == 2 } { drawAvailability.value }
            { ~qriViewMode == 3 } { drawProjective.value }
            { drawTriplePlane.value }
        };
        viewMenu = styleMenu.(PopUpMenu(~qriWindow, Rect(18, 360, 204, 25))
            .items_(["HILBERT INTERACTION", "NATIVE MEMBRANE", "PROCESS AVAILABILITY", "PROJECTIVE FIELD"])
            .value_(~qriViewMode)
            .action_({ |menu|
                ~qriViewMode = menu.value; refreshPanel.value; ~qriDiagram.refresh
            }));
        bodyMenu = styleMenu.(PopUpMenu(~qriWindow, Rect(232, 360, 172, 25))
            .items_(~qriBodyModeNames).value_(~qriBodyMode)
            .action_({ |menu| ~qriBodyMode = menu.value; ~qriApplyBodyMode.value }));
        enabledButton = Button(~qriWindow, Rect(414, 360, 150, 25))
            .states_([
                ["PLUCK LAYER MUTED", Color.fromHexString("ffd166"), Color.fromHexString("532b35")],
                ["PLUCK LAYER ACTIVE", Color.fromHexString("06130b"), Color.fromHexString("80ed99")]
            ])
            .value_(~qriEnabled.asInteger).action_({ |button|
                ~qriEnabled = button.value > 0;
                if(~qriEnabled.not) { ~qriPluckQueue.clear };
            });
        Button(~qriWindow, Rect(574, 360, 128, 25))
            .states_([["PROJECTION / FLUX", textColor, Color.fromHexString("263241")]])
            .action_({ openMeasurementControls.value });
        Button(~qriWindow, Rect(714, 360, 128, 25))
            .states_([["16 OUTPUTS", textColor, Color.fromHexString("263241")]])
            .action_({ openProjectiveOutputs.value });
        Button(~qriWindow, Rect(18, 392, 148, 25))
            .states_([["FOUR-QUBIT PREPARATION", textColor, Color.fromHexString("263241")]])
            .action_({ openPreparationControls.value });
        Button(~qriWindow, Rect(176, 392, 148, 25))
            .states_([["QHO / FM / CHEB", textColor, Color.fromHexString("263241")]])
            .action_({ openQHOControls.value });
        Button(~qriWindow, Rect(334, 392, 128, 25))
            .states_([["MI VOICES", textColor, Color.fromHexString("263241")]])
            .action_({ openMIVoiceControls.value });
        Button(~qriWindow, Rect(472, 392, 128, 25))
            .states_([["FX BUS / RETURNS", textColor, Color.fromHexString("263241")]])
            .action_({ openFXControls.value });
        Button(~qriWindow, Rect(610, 392, 110, 25))
            .states_([["ISOLATE SIMPLE", Color.black, Color.fromHexString("80ed99")]])
            .action_({
                listeningBaseline.value;
                { ~qriWindow !? _.close; openPanel.value }.defer;
            });
        Button(~qriWindow, Rect(732, 392, 110, 25))
            .states_([["FIELD LISTEN", Color.black, Color.fromHexString("8ecae6")]])
            .action_({
                fieldListeningBaseline.value;
                { ~qriWindow !? _.close; openPanel.value }.defer;
            });
        StaticText(~qriWindow, Rect(18, 428, 824, 18))
            .string_("EIGHT MIX CHANNELS  /  five native + MiRings + MiPlaits + MiElements")
            .stringColor_(Color.fromHexString("8ecae6"));
        8.do { |index|
            var x = 18 + (index * 103), voiceSlider, decayLaneSlider;
            var fuzzSlider, temporalSendSlider, fxSendSlider;
            voiceSlider = styleSlider.(EZSlider(~qriWindow, Rect(x, 450, 96, 28), ~qriVoiceNames[index],
                ControlSpec(0, 1.5, \lin, 0.001), { |view|
                    ~qriVoiceGains[index] = view.value; ~qriPushVoiceGains.value
                }, ~qriVoiceGains[index], labelWidth: 48, numberWidth: 28));
            Button(~qriWindow, Rect(x, 482, 96, 22))
                .states_([
                    ["ACTIVE", textColor, Color.fromHexString("263241")],
                    ["MUTED", Color.fromHexString("ffd166"), Color.fromHexString("532b35")]
                ]).value_(~qriVoiceMutes[index])
                .action_({ |button|
                ~qriVoiceMutes[index] = button.value; ~qriPushVoiceGains.value
            });
            decayLaneSlider = styleSlider.(EZSlider(~qriWindow, Rect(x, 510, 96, 27), "decay",
                ControlSpec(0.02, 6, \exp, 0.001), { |view|
                    ~qriVoiceDecays[index] = view.value;
                    ~qriDecay = ~qriVoiceDecays.maxItem;
                    ~qriPushVoiceDecays.value;
                    ~qriCoalesceLongDecayQueue.value;
                }, ~qriVoiceDecays[index], labelWidth: 42, numberWidth: 28));
            fuzzSlider = styleSlider.(EZSlider(~qriWindow, Rect(x, 540, 96, 27), "fuzz",
                ControlSpec(0, 1, \lin, 0.001), { |view|
                    ~qriVoiceFuzzSends[index] = view.value;
                    ~qriPushVoiceFuzzSends.value
                }, ~qriVoiceFuzzSends[index], labelWidth: 38, numberWidth: 28));
            temporalSendSlider = styleSlider.(EZSlider(~qriWindow, Rect(x, 570, 96, 27),
                if(~qmwTemporalMemoryInputBus.notNil, { "delay" }, { "delay off" }),
                ControlSpec(0, 1, \lin, 0.001), { |view|
                    ~qriVoiceTemporalSends[index] = view.value;
                    ~qriPushVoiceTemporalSends.value
                }, ~qriVoiceTemporalSends[index], labelWidth: 42, numberWidth: 28));
            fxSendSlider = styleSlider.(EZSlider(~qriWindow, Rect(x, 600, 96, 27), "FX send",
                ControlSpec(0, 1, \lin, 0.001), { |view|
                    ~qriVoiceFXSends[index] = view.value;
                    ~qriPushVoiceFXSends.value
                }, ~qriVoiceFXSends[index], labelWidth: 44, numberWidth: 28));
        };
        temporalMixSlider = styleSlider.(EZSlider(~qriWindow, Rect(18, 634, 198, 27), "memory mix",
            ControlSpec(0, 0.5, \lin, 0.001), { |view|
                ~qmwTemporalMemorySetMixer !? { |setter|
                    setter.value(view.value, ~qmwTemporalMemoryFuzzSend ? 0)
                }
            }, ~qmwTemporalMemoryMix ? 0.18, labelWidth: 76, numberWidth: 42));
        temporalFocusSlider = styleSlider.(EZSlider(~qriWindow, Rect(228, 634, 198, 27), "echo focus",
            ControlSpec(0, 1, \lin, 0.001), { |view|
                ~qmwTemporalMemorySetTapFocus !? { |setter| setter.value(view.value) }
            }, ~qmwTemporalMemoryTapFocus ? 0.0, labelWidth: 72, numberWidth: 42));
        temporalFeedbackSlider = styleSlider.(EZSlider(~qriWindow, Rect(438, 634, 198, 27), "feedback",
            ControlSpec(0, 0.92, \lin, 0.001), { |view|
                ~qmwTemporalMemorySetSelfFeedback !? { |setter| setter.value(view.value) }
            }, ~qmwTemporalMemorySelfFeedback ? 0.62, labelWidth: 64, numberWidth: 42));
        temporalBaseDelaySlider = styleSlider.(EZSlider(~qriWindow, Rect(648, 634, 194, 27), "delay (s)",
            ControlSpec(0.020, 2.500, \exp, 0.001, 0.137), { |view|
                ~qmwTemporalMemorySetBaseDelaySeconds !? { |setter| setter.value(view.value) };
                ~qriTemporalMemoryControlAddress !? { |address|
                    address.sendMsg(
                        "/qmw/temporal_memory/v1/control/base_delay_seconds",
                        view.value.asFloat
                    )
                }
            }, ~qmwTemporalMemoryBaseDelaySeconds ? 0.137, labelWidth: 56, numberWidth: 48));
        fieldGainSlider = styleSlider.(EZSlider(~qriWindow, Rect(18, 668, 824, 27), "field body gain",
            ControlSpec(0, 0.35, \lin, 0.001), { |view|
                ~qriFieldGain = view.value;
                ~qriApplyBodyMode.value
            }, ~qriFieldGain, labelWidth: 104, numberWidth: 54));
        Button(~qriWindow, Rect(18, 702, 390, 24))
            .states_([["TEMPORAL MEMORY CONTROLS  /  rhythm map, phase, feedback, tone, width, glide, freeze",
                textColor, Color.fromHexString("263241")]])
            .action_({ openTemporalMemoryControls.value });
        Button(~qriWindow, Rect(418, 702, 146, 24))
            .states_([["VOICE ALLOCATOR", Color.black, Color.fromHexString("80ed99")]])
            .action_({ openVoiceAllocatorControls.value });
        Button(~qriWindow, Rect(574, 702, 268, 24))
            .states_([["16 POLYRHYTHMIC VOICES", textColor, Color.fromHexString("263241")]])
            .action_({ openPolyrhythmControls.value });
        StaticText(~qriWindow, Rect(18, 734, 824, 18))
            .string_("FIELD BODY is independent and silent at 0  /  EACH VOICE: gain, mute, decay, fuzz, delay, FX send")
            .stringColor_(Color.fromHexString("ff7ac6"));
        mixSlider = styleSlider.(EZSlider(~qriWindow, Rect(18, 758, 250, 27), "pluck mix",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriMix = view.value }, ~qriMix,
            labelWidth: 68, numberWidth: 48));
        gainSlider = styleSlider.(EZSlider(~qriWindow, Rect(280, 758, 270, 27), "pluck output",
            ControlSpec(0, 128, \lin, 0.01), { |view|
                ~qriPluckAudibilityGain = view.value
            }, ~qriPluckAudibilityGain, labelWidth: 78, numberWidth: 48));
        decaySlider = styleSlider.(EZSlider(~qriWindow, Rect(562, 758, 280, 27), "all voice decay",
            ControlSpec(0.02, 6, \exp, 0.001), { |view|
                ~qriDecay = view.value;
                ~qriVoiceDecays = Array.fill(8, view.value);
                ~qriPushVoiceDecays.value;
                ~qriCoalesceLongDecayQueue.value;
            },
            ~qriDecay, labelWidth: 78, numberWidth: 54));
        ~qriThresholdSlider = styleSlider.(EZSlider(
            ~qriWindow, Rect(18, 794, 404, 28), "pluck quantum",
            ControlSpec(0.005, 0.5, \exp, 0.0001), { |view|
                ~qriSetPluckThreshold.value(view.value)
            }, ~qriFrame[\threshold], labelWidth: 92, numberWidth: 72
        ));
        ~qriOmegaSlider = styleSlider.(EZSlider(
            ~qriWindow, Rect(438, 794, 404, 28), "interaction omega",
            ControlSpec(0.1, 8, \exp, 0.001), { |view|
                ~qriPerformanceControlPendingUntil = Main.elapsedTime + 0.18;
                ~qriControlAddress.sendMsg(
                    "/qmw/resonant_interaction/v1/control/interaction_omega_scale",
                    view.value.asFloat
                )
            }, ~qriFrame[\omegaScale], labelWidth: 118, numberWidth: 72
        ));
        ~qriModeLabel = StaticText(~qriWindow, Rect(18, 834, 824, 18))
            .string_("M1-M20 continuous availability  /  display normalized only")
            .stringColor_(Color.fromHexString("8ecae6"));
        ~qriModeView = MultiSliderView(~qriWindow, Rect(18, 856, 824, 54))
            .size_(modeCount).isFilled_(true)
            .fillColor_(Color.fromHexString("ff67d4"))
            .strokeColor_(Color.clear).background_(Color.fromHexString("080b10"));
        ~qriStatus = StaticText(~qriWindow, Rect(18, 918, 824, 20))
            .font_(Font("Menlo", 10)).stringColor_(Color.fromHexString("80ed99"));
        ~qriWindow.onClose = {
            ~qriWindow = nil; ~qriDiagram = nil; ~qriModeView = nil;
            ~qriModeLabel = nil;
            ~qriStatus = nil;
            ~qriThresholdSlider = nil; ~qriOmegaSlider = nil;
        };
        refreshPanel.value;
    });
};
~qriOpenPanel = openPanel;

if(~qrmWindow.notNil, {
    ~qrmWindow.name_("QMW Integrated Resonant Instrument");
    ~qriMainButton = Button(~qrmWindow, Rect(748, 18, 150, 24))
        .states_([["HILBERT INTERACTION", textColor, Color.fromHexString("263241")]])
        .action_({ openPanel.value });
    ~qrmSphere !? { |view|
        ~qriPriorQrmSphereDrawFunc = view.drawFunc;
        view.drawFunc = { |sourceView| drawSourceOverview.(sourceView) };
        view.refresh;
    };
});

OSCdef(\qriPerformanceSavedV1, { |msg|
    {
        ~qriRecordingMusicXMLPath = msg[2].asString;
        ~qriRecordingEventJSONPath = msg[3].asString;
        ~qriRecordingStatus !? { |view|
            view.string_(
                "saved WAV + MusicXML (% events): %"
                .format(msg[1].asInteger, ~qriRecordingMusicXMLPath.basename)
            )
        };
    }.defer;
}, root ++ "/recording/saved", recvPort: port);

OSCdef(\qriQHOBeginV1, { |msg|
    ~qriQHOCompatible = (msg[3].asString == qhoSchema);
    if(~qriQHOCompatible) {
        ~qriQHOStage = ~qriQHOFrame.copy;
        ~qriQHOStage[\revision] = msg[1].asInteger;
        ~qriQHOStage[\time] = msg[2].asFloat;
        ~qriQHOStage[\populationSeen] = Array.fill(16, false);
        ~qriQHOStage[\populations] = Array.fill(16, 0.0);
        ~qriQHOStage[\coherence1MagnitudeSeen] = false;
        ~qriQHOStage[\coherence1PhaseSeen] = false;
        ~qriQHOStage[\coherence2MagnitudeSeen] = false;
        ~qriQHOStage[\coherence2PhaseSeen] = false;
        ~qriQHOStage[\coherence1Magnitudes] = Array.fill(15, 0.0);
        ~qriQHOStage[\coherence1Phases] = Array.fill(15, 0.0);
        ~qriQHOStage[\coherence2Magnitudes] = Array.fill(14, 0.0);
        ~qriQHOStage[\coherence2Phases] = Array.fill(14, 0.0);
        ~qriQHOStage[\qftPopulationSeen] = false;
        ~qriQHOStage[\hadamardPopulationSeen] = false;
        ~qriQHOStage[\matrixPowerSeen] = false;
        ~qriQHOStage[\matrixPhaseSeen] = false;
        ~qriQHOStage[\parsevalSeen] = false;
        ~qriQHOStage[\qftPopulations] = Array.fill(16, 0.0);
        ~qriQHOStage[\hadamardPopulations] = Array.fill(16, 0.0);
        ~qriQHOStage[\matrixPowerBins] = Array.fill(16, 0.0);
        ~qriQHOStage[\matrixPhaseBins] = Array.fill(16, 0.0);
    };
}, qhoRoot ++ "/frame/begin", recvPort: qhoPort);

OSCdef(\qriQHOPopulationsV1, { |msg|
    if(~qriQHOCompatible and: { ~qriQHOStage.notNil }
        and: { msg[1].asInteger == ~qriQHOStage[\revision] }
        and: { msg.size >= 18 }) {
        ~qriQHOStage[\populations] = msg.copyRange(2, 17).collect(_.asFloat);
        ~qriQHOStage[\populationSeen] = Array.fill(16, true);
    };
}, qhoRoot ++ "/populations", recvPort: qhoPort);

OSCdef(\qriQHOCoherence1MagnitudeV1, { |msg|
    if(~qriQHOCompatible and: { ~qriQHOStage.notNil }
        and: { msg[1].asInteger == ~qriQHOStage[\revision] }
        and: { msg.size >= 17 }) {
        ~qriQHOStage[\coherence1Magnitudes] = msg.copyRange(2, 16).collect(_.asFloat);
        ~qriQHOStage[\coherence1MagnitudeSeen] = true;
    };
}, qhoRoot ++ "/coherence/1/magnitude", recvPort: qhoPort);

OSCdef(\qriQHOCoherence1PhaseV1, { |msg|
    if(~qriQHOCompatible and: { ~qriQHOStage.notNil }
        and: { msg[1].asInteger == ~qriQHOStage[\revision] }
        and: { msg.size >= 17 }) {
        ~qriQHOStage[\coherence1Phases] = msg.copyRange(2, 16).collect(_.asFloat);
        ~qriQHOStage[\coherence1PhaseSeen] = true;
    };
}, qhoRoot ++ "/coherence/1/phase", recvPort: qhoPort);

OSCdef(\qriQHOCoherence2MagnitudeV1, { |msg|
    if(~qriQHOCompatible and: { ~qriQHOStage.notNil }
        and: { msg[1].asInteger == ~qriQHOStage[\revision] }
        and: { msg.size >= 16 }) {
        ~qriQHOStage[\coherence2Magnitudes] = msg.copyRange(2, 15).collect(_.asFloat);
        ~qriQHOStage[\coherence2MagnitudeSeen] = true;
    };
}, qhoRoot ++ "/coherence/2/magnitude", recvPort: qhoPort);

OSCdef(\qriQHOCoherence2PhaseV1, { |msg|
    if(~qriQHOCompatible and: { ~qriQHOStage.notNil }
        and: { msg[1].asInteger == ~qriQHOStage[\revision] }
        and: { msg.size >= 16 }) {
        ~qriQHOStage[\coherence2Phases] = msg.copyRange(2, 15).collect(_.asFloat);
        ~qriQHOStage[\coherence2PhaseSeen] = true;
    };
}, qhoRoot ++ "/coherence/2/phase", recvPort: qhoPort);

OSCdef(\qriQHOQFTPopulationsV1, { |msg|
    if(~qriQHOCompatible and: { ~qriQHOStage.notNil }
        and: { msg[1].asInteger == ~qriQHOStage[\revision] }
        and: { msg.size >= 18 }) {
        ~qriQHOStage[\qftPopulations] = msg.copyRange(2, 17).collect(_.asFloat);
        ~qriQHOStage[\qftPopulationSeen] = true;
    };
}, qhoRoot ++ "/basis/qft/populations", recvPort: qhoPort);

OSCdef(\qriQHOHadamardPopulationsV1, { |msg|
    if(~qriQHOCompatible and: { ~qriQHOStage.notNil }
        and: { msg[1].asInteger == ~qriQHOStage[\revision] }
        and: { msg.size >= 18 }) {
        ~qriQHOStage[\hadamardPopulations] = msg.copyRange(2, 17).collect(_.asFloat);
        ~qriQHOStage[\hadamardPopulationSeen] = true;
    };
}, qhoRoot ++ "/basis/hadamard/populations", recvPort: qhoPort);

OSCdef(\qriQHOMatrixPowerV1, { |msg|
    if(~qriQHOCompatible and: { ~qriQHOStage.notNil }
        and: { msg[1].asInteger == ~qriQHOStage[\revision] }
        and: { msg.size >= 18 }) {
        ~qriQHOStage[\matrixPowerBins] = msg.copyRange(2, 17).collect(_.asFloat);
        ~qriQHOStage[\matrixPowerSeen] = true;
    };
}, qhoRoot ++ "/matrix-spectrum/power", recvPort: qhoPort);

OSCdef(\qriQHOMatrixPhaseV1, { |msg|
    if(~qriQHOCompatible and: { ~qriQHOStage.notNil }
        and: { msg[1].asInteger == ~qriQHOStage[\revision] }
        and: { msg.size >= 18 }) {
        ~qriQHOStage[\matrixPhaseBins] = msg.copyRange(2, 17).collect(_.asFloat);
        ~qriQHOStage[\matrixPhaseSeen] = true;
    };
}, qhoRoot ++ "/matrix-spectrum/phase", recvPort: qhoPort);

OSCdef(\qriQHOParsevalV1, { |msg|
    if(~qriQHOCompatible and: { ~qriQHOStage.notNil }
        and: { msg[1].asInteger == ~qriQHOStage[\revision] }
        and: { msg.size >= 6 }) {
        ~qriQHOStage[\parsevalTrace] = msg[2].asFloat;
        ~qriQHOStage[\purity] = msg[3].asFloat;
        ~qriQHOStage[\matrixPowerSum] = msg[4].asFloat;
        ~qriQHOStage[\parsevalResidual] = msg[5].asFloat;
        ~qriQHOStage[\parsevalSeen] = true;
    };
}, qhoRoot ++ "/parseval", recvPort: qhoPort);

OSCdef(\qriQHOObservablesV1, { |msg|
    if(~qriQHOCompatible and: { ~qriQHOStage.notNil }
        and: { msg[1].asInteger == ~qriQHOStage[\revision] }) {
        ~qriQHOStage[\meanN] = msg[2].asFloat;
        ~qriQHOStage[\purity] = msg[8].asFloat;
        ~qriQHOStage[\coherence] = msg[9].asFloat;
        ~qriQHOStage[\omega] = msg[10].asFloat;
    };
}, qhoRoot ++ "/observables", recvPort: qhoPort);

OSCdef(\qriQHOStateV1, { |msg|
    if(~qriQHOCompatible and: { ~qriQHOStage.notNil }
        and: { msg[1].asInteger == ~qriQHOStage[\revision] }) {
        ~qriQHOStage[\state] = msg[2].asString;
        ~qriQHOStage[\fock] = msg[3].asInteger;
    };
}, qhoRoot ++ "/state", recvPort: qhoPort);

OSCdef(\qriQHOParametersV1, { |msg|
    if(~qriQHOCompatible and: { ~qriQHOStage.notNil }
        and: { msg[1].asInteger == ~qriQHOStage[\revision] }) {
        ~qriQHOStage[\alphaRe] = msg[2].asFloat;
        ~qriQHOStage[\alphaIm] = msg[3].asFloat;
        ~qriQHOStage[\thermal] = msg[4].asFloat;
        ~qriQHOStage[\squeezeR] = msg[5].asFloat;
        ~qriQHOStage[\squeezePhase] = msg[6].asFloat;
        ~qriQHOStage[\omega] = msg[7].asFloat;
    };
}, qhoRoot ++ "/parameters", recvPort: qhoPort);

OSCdef(\qriQHOEndV1, { |msg|
    var committed;
    if(~qriQHOCompatible and: { ~qriQHOStage.notNil }
        and: { msg[1].asInteger == ~qriQHOStage[\revision] }) {
        if(~qriQHOStage[\populationSeen].every { |seen| seen }
            and: { ~qriQHOStage[\coherence1MagnitudeSeen] }
            and: { ~qriQHOStage[\coherence1PhaseSeen] }
            and: { ~qriQHOStage[\coherence2MagnitudeSeen] }
            and: { ~qriQHOStage[\coherence2PhaseSeen] }
            and: { ~qriQHOStage[\qftPopulationSeen] }
            and: { ~qriQHOStage[\hadamardPopulationSeen] }
            and: { ~qriQHOStage[\matrixPowerSeen] }
            and: { ~qriQHOStage[\matrixPhaseSeen] }
            and: { ~qriQHOStage[\parsevalSeen] }) {
            committed = ~qriQHOStage;
            committed[\basisPopulations] = [
                committed[\populations], committed[\qftPopulations],
                committed[\hadamardPopulations]
            ];
            committed.removeAt(\populationSeen);
            committed.removeAt(\coherence1MagnitudeSeen);
            committed.removeAt(\coherence1PhaseSeen);
            committed.removeAt(\coherence2MagnitudeSeen);
            committed.removeAt(\coherence2PhaseSeen);
            committed.removeAt(\qftPopulationSeen);
            committed.removeAt(\hadamardPopulationSeen);
            committed.removeAt(\matrixPowerSeen);
            committed.removeAt(\matrixPhaseSeen);
            committed.removeAt(\parsevalSeen);
            committed.removeAt(\qftPopulations);
            committed.removeAt(\hadamardPopulations);
            ~qriQHOStage = nil; ~qriQHOCompatible = false;
            {
                ~qriQHOFrame = committed;
                ~qriQHOPopulationBus !? { |bus| bus.setn(committed[\populations]) };
                ~qriQHOCoherenceMagnitudeBus !? { |bus|
                    bus.setn(committed[\coherence1Magnitudes])
                };
                ~qriQHOCoherencePhaseBus !? { |bus|
                    bus.setn(committed[\coherence1Phases])
                };
                ~qriQHOBasisPopulationBus !? { |bus|
                    bus.setn(committed[\basisPopulations].flat)
                };
                ~qriQHOMatrixPowerBus !? { |bus|
                    bus.setn(committed[\matrixPowerBins])
                };
                ~qriQHOMatrixPhaseBus !? { |bus|
                    bus.setn(committed[\matrixPhaseBins])
                };
                refreshQHOControls.value;
                refreshParsevalControls !? { |refresh| refresh.value };
            }.defer;
        } {
            ~qriQHOStage = nil; ~qriQHOCompatible = false;
        };
    };
}, qhoRoot ++ "/frame/end", recvPort: qhoPort);

OSCdef(\qriBeginV1, { |msg|
    ~qriCompatible = (msg[3].asString == schema)
        and: { msg[4].asInteger == 8 }
        and: { msg[5].asInteger == modeCount };
    if(~qriCompatible, {
        ~qriStage = (
            revision: msg[1].asInteger, time: msg[2].asFloat,
            mapping: msg[6].asString, expectedEvents: msg[7].asInteger,
            threshold: msg[8].asFloat, accumulatorPeak: msg[9].asFloat,
            authority: msg[10].asString, expectedAvailability: msg[11].asInteger,
            omegaScale: if(msg.size > 12, { msg[12].asFloat }, { 1.0 }),
            drives: Array.fill(modeCount, Complex(0, 0)),
            availability: Array.new, events: Array.new
        );
    });
}, root ++ "/frame/begin", recvPort: port);

OSCdef(\qriAvailabilityV1, { |msg|
    var inputCount, outputCount, tail, path;
    if(~qriCompatible and: { ~qriStage.notNil }
        and: { msg[1].asInteger == ~qriStage[\revision] }) {
        inputCount = msg[7].asInteger; outputCount = msg[8].asInteger;
        tail = msg.copyRange(9, msg.size - 1);
        path = (
            channel: msg[3].asString, kind: msg[4].asString,
            real: msg[5].asFloat, imag: msg[6].asFloat,
            inputs: tail.copyRange(0, inputCount - 1).collect(_.asInteger),
            outputs: tail.copyRange(inputCount, inputCount + outputCount - 1)
                .collect(_.asInteger)
        );
        ~qriStage[\availability] = ~qriStage[\availability].add(path);
    };
}, root ++ "/availability", recvPort: port);

OSCdef(\qriDriveV1, { |msg|
    var mode;
    if(~qriCompatible and: { ~qriStage.notNil }
        and: { msg[1].asInteger == ~qriStage[\revision] }) {
        mode = msg[2].asInteger;
        if(mode.inclusivelyBetween(0, modeCount - 1)) {
            ~qriStage[\drives][mode] = Complex(msg[3].asFloat, msg[4].asFloat)
        };
    };
}, root ++ "/drive", recvPort: port);

OSCdef(\qriEventV1, { |msg|
    var event;
    if(~qriCompatible and: { ~qriStage.notNil }
        and: { msg[1].asInteger == ~qriStage[\revision] }) {
        event = (
            id: msg[3].asString, channel: msg[4].asString, kind: msg[5].asString,
            real: msg[6].asFloat, imag: msg[7].asFloat, energy: msg[8].asFloat,
            azimuth: msg[9].asFloat, dominant: msg[10].asInteger,
            inputs: [msg[11].asInteger], outputs: [msg[12].asInteger],
            weights: msg.copyRange(13, 32).collect(_.asFloat),
            phases: msg.copyRange(33, 52).collect(_.asFloat)
        );
        ~qriStage[\events] = ~qriStage[\events].add(event);
    };
}, root ++ "/event", recvPort: port);

OSCdef(\qriEndV1, { |msg|
    var committed, countsMatch;
    if(~qriCompatible and: { ~qriStage.notNil }
        and: { msg[1].asInteger == ~qriStage[\revision] }) {
        countsMatch = (~qriStage[\events].size == ~qriStage[\expectedEvents])
            and: { ~qriStage[\availability].size == ~qriStage[\expectedAvailability] }
            and: { msg[3].asInteger == ~qriStage[\expectedEvents] };
        if(countsMatch) {
            committed = ~qriStage;
            ~qriStage = nil; ~qriCompatible = false;
            { commitFrame.value(committed) }.defer;
        } {
            "QRI rejected incomplete OSC transaction %".format(msg[1]).warn;
            ~qriStage = nil; ~qriCompatible = false;
        };
    };
}, root ++ "/frame/end", recvPort: port);

OSCdef(\qriMeasureBeginV1, { |msg|
    ~qriMeasurementCompatible = (msg[3].asString == measurementSchema)
        and: { msg[5].asInteger == 16 };
    if(~qriMeasurementCompatible) {
        ~qriMeasurementStage = (
            revision: msg[1].asInteger, time: msg[2].asFloat,
            bank: msg[4].asString, expected: msg[5].asInteger,
            bankMode: ~qriMeasurementFrame[\bankMode],
            pauli: ~qriMeasurementFrame[\pauli],
            aperture: ~qriMeasurementFrame[\aperture],
            apertureRate: ~qriMeasurementFrame[\apertureRate],
            gaugeFlux: ~qriMeasurementFrame[\gaugeFlux],
            holonomy: ~qriMeasurementFrame[\holonomy],
            received: Array.fill(16, false), entropy: 0.0, dominant: 0,
            probabilities: Array.fill(16, 0.0), stateFlow: Array.fill(16, 0.0),
            apertureFlow: Array.fill(16, 0.0), totalFlow: Array.fill(16, 0.0)
        )
    };
}, measurementRoot ++ "/frame/begin", recvPort: measurementPort);

OSCdef(\qriMeasureChannelV1, { |msg|
    var index;
    if(~qriMeasurementCompatible and: { ~qriMeasurementStage.notNil }
        and: { msg[1].asInteger == ~qriMeasurementStage[\revision] }) {
        index = msg[2].asInteger;
        if(index.inclusivelyBetween(0, 15)) {
            ~qriMeasurementStage[\received][index] = true;
            ~qriMeasurementStage[\probabilities][index] = msg[4].asFloat;
            ~qriMeasurementStage[\stateFlow][index] = msg[5].asFloat;
            ~qriMeasurementStage[\apertureFlow][index] = msg[6].asFloat;
            ~qriMeasurementStage[\totalFlow][index] = msg[7].asFloat;
        };
    };
}, measurementRoot ++ "/channel", recvPort: measurementPort);

OSCdef(\qriMeasureConfigurationV1, { |msg|
    if(~qriMeasurementCompatible and: { ~qriMeasurementStage.notNil }
        and: { msg[1].asInteger == ~qriMeasurementStage[\revision] }) {
        ~qriMeasurementStage[\bankMode] = msg[2].asString;
        ~qriMeasurementStage[\pauli] = msg[3].asString;
        ~qriMeasurementStage[\aperture] = msg[4].asString;
        ~qriMeasurementStage[\apertureRate] = msg[5].asFloat;
        ~qriMeasurementStage[\gaugeFlux] = msg[6].asFloat;
        ~qriMeasurementStage[\holonomy] = msg[7].asFloat;
    };
}, measurementRoot ++ "/configuration", recvPort: measurementPort);

OSCdef(\qriMeasureSummaryV1, { |msg|
    if(~qriMeasurementCompatible and: { ~qriMeasurementStage.notNil }
        and: { msg[1].asInteger == ~qriMeasurementStage[\revision] }) {
        ~qriMeasurementStage[\entropy] = msg[2].asFloat;
        ~qriMeasurementStage[\dominant] = msg[3].asInteger.clip(0, 15);
    };
}, measurementRoot ++ "/summary", recvPort: measurementPort);

OSCdef(\qriMeasureEndV1, { |msg|
    var committed;
    if(~qriMeasurementCompatible and: { ~qriMeasurementStage.notNil }
        and: { msg[1].asInteger == ~qriMeasurementStage[\revision] }) {
        if(~qriMeasurementStage[\received].every { |received| received }) {
            committed = ~qriMeasurementStage;
            ~qriMeasurementStage = nil; ~qriMeasurementCompatible = false;
            {
                ~qriMeasurementDeltaP = if(~qriMeasurementFrame[\revision] < 0, {
                    0.0
                }, {
                    (committed[\probabilities] - ~qriMeasurementFrame[\probabilities])
                        .collect(_.abs).sum
                });
                ~qriMeasurementFrame = committed;
                ~qriProjectiveProbabilityBus !? { |bus|
                    bus.setn(committed[\probabilities])
                };
                refreshMeasurementControls.value;
                ~qriRequestPanelRefresh.value;
            }.defer;
        } {
            "QRI rejected incomplete projective frame %".format(msg[1]).warn;
            ~qriMeasurementStage = nil; ~qriMeasurementCompatible = false;
        };
    };
}, measurementRoot ++ "/frame/end", recvPort: measurementPort);

~qriCleanup = {
    [\qriBeginV1, \qriAvailabilityV1, \qriDriveV1, \qriEventV1, \qriEndV1,
        \qriPerformanceSavedV1,
        \qriQHOBeginV1, \qriQHOPopulationsV1,
        \qriQHOCoherence1MagnitudeV1, \qriQHOCoherence1PhaseV1,
        \qriQHOCoherence2MagnitudeV1, \qriQHOCoherence2PhaseV1,
        \qriQHOQFTPopulationsV1, \qriQHOHadamardPopulationsV1,
        \qriQHOMatrixPowerV1, \qriQHOMatrixPhaseV1, \qriQHOParsevalV1,
        \qriQHOObservablesV1,
        \qriQHOStateV1, \qriQHOParametersV1, \qriQHOEndV1,
        \qriMeasureBeginV1, \qriMeasureChannelV1, \qriMeasureConfigurationV1,
        \qriMeasureSummaryV1, \qriMeasureEndV1]
        .do { |key| OSCdef(key).free };
    ~qriTimeClock !? _.stop; ~qriTimeClock = nil;
    ~qriAllocatorRoutine !? _.stop; ~qriAllocatorRoutine = nil;
    if(~qriRecordingActive) { ~qriStopPerformanceRecording.value };
    ~qriStopPolyLanes !? _.value;
    ~qriNodes.do(_.free); ~qriNodes.clear; ~qriPluckQueue.clear;
    ~qriMiRingsNodes.do(_.free); ~qriMiRingsNodes.clear;
    ~qriMiVoiceNodes.do(_.free); ~qriMiVoiceNodes.clear;
    ~qriMiRingsNode !? _.free; ~qriMiRingsNode = nil;
    ~qriDisableMiRingsSix !? { |disable| disable.value };
    stopFXReturns.value;
    ~qriVoiceGainBus !? _.free; ~qriVoiceGainBus = nil;
    ~qriVoiceDecayBus !? _.free; ~qriVoiceDecayBus = nil;
    ~qriVoiceFuzzSendBus !? _.free; ~qriVoiceFuzzSendBus = nil;
    ~qriVoiceTemporalSendBus !? _.free; ~qriVoiceTemporalSendBus = nil;
    ~qriVoiceFXSendBus !? _.free; ~qriVoiceFXSendBus = nil;
    ~qriFXSendBus !? _.free; ~qriFXSendBus = nil;
    ~qriFXGroup !? _.free; ~qriFXGroup = nil;
    ~qriQHOPopulationBus !? _.free; ~qriQHOPopulationBus = nil;
    ~qriQHOCoherenceMagnitudeBus !? _.free; ~qriQHOCoherenceMagnitudeBus = nil;
    ~qriQHOCoherencePhaseBus !? _.free; ~qriQHOCoherencePhaseBus = nil;
    ~qriQHOBasisPopulationBus !? _.free; ~qriQHOBasisPopulationBus = nil;
    ~qriQHOMatrixPowerBus !? _.free; ~qriQHOMatrixPowerBus = nil;
    ~qriQHOMatrixPhaseBus !? _.free; ~qriQHOMatrixPhaseBus = nil;
    ~qriFMControlBus !? _.free; ~qriFMControlBus = nil;
    ~qriChebControlBus !? _.free; ~qriChebControlBus = nil;
    ~qriParsevalControlBus !? _.free; ~qriParsevalControlBus = nil;
    ~qriProjectiveBody !? _.free; ~qriProjectiveBody = nil;
    ~qriFieldGroup !? _.free; ~qriFieldGroup = nil;
    ~qriProjectiveProbabilityBus !? _.free; ~qriProjectiveProbabilityBus = nil;
    ~qriProjectiveGainBus !? _.free; ~qriProjectiveGainBus = nil;
    ~qriProjectiveDelayBus !? _.free; ~qriProjectiveDelayBus = nil;
    ~qriPriorRouteBuresPulse !? { ~qrmRouteBuresPulse = ~qriPriorRouteBuresPulse };
    ~qriPriorRouteCrossing !? { ~qrmRouteCrossing = ~qriPriorRouteCrossing };
    ~qriPriorRouteBuresPulse = nil; ~qriPriorRouteCrossing = nil;
    ~qrmSphere !? { |view|
        ~qriPriorQrmSphereDrawFunc !? { |function| view.drawFunc = function };
        view.refresh;
    };
    ~qriPriorQrmSphereDrawFunc = nil;
    closePanel.value;
    ~qriMeasurementControlWindow !? _.close; ~qriMeasurementControlWindow = nil;
    ~qriPreparationWindow !? _.close; ~qriPreparationWindow = nil;
    ~qriQHOWindow !? _.close; ~qriQHOWindow = nil;
    ~qriChebWindow !? _.close; ~qriChebWindow = nil;
    ~qriMiRingsWindow !? _.close; ~qriMiRingsWindow = nil;
    ~qriMiRingsSixWindow !? _.close; ~qriMiRingsSixWindow = nil;
    ~qriMIVoiceWindow !? _.close; ~qriMIVoiceWindow = nil;
    ~qriFXWindow !? _.close; ~qriFXWindow = nil; ~qriVSTStatus = nil;
    ~qriProjectiveOutputWindow !? _.close; ~qriProjectiveOutputWindow = nil;
    ~qriTemporalMemoryWindow !? _.close; ~qriTemporalMemoryWindow = nil;
    ~qriPolyWindow !? _.close; ~qriPolyWindow = nil;
    ~qriAllocatorWindow !? _.close; ~qriAllocatorWindow = nil;
    ~qriAllocatorStatus = nil; ~qriRefreshAllocatorControls = nil;
    ~qriMainButton !? _.remove; ~qriMainButton = nil;
    ~qriMainRecordButton !? _.remove; ~qriMainRecordButton = nil;
    ~qriAudioRecordButton !? _.remove; ~qriAudioRecordButton = nil;
    ~qriRecordingStatus !? _.remove; ~qriRecordingStatus = nil;
};

~qriApplyBodyMode.value;
{ openPanel.value }.defer;
"QMW Integrated Resonant Interaction listening on UDP % and projective UDP %"
    .format(port, measurementPort).postln;
)
