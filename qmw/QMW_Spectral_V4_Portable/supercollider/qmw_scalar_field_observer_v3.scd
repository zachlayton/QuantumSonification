/*
QMW Quantum Field Theory Instrument V3

Scientific frames arrive from qmw.qft.live_osc_v3 on UDP 17850. This file is
an explicit perceptual adapter: it never evolves, normalizes, or feeds back
into the authoritative scalar field.
*/
(
var instrumentVersion = (~qmwQFTInstrumentVersion ? 3).asInteger;
var displayVersion = (~qmwQFTDisplayVersion ? instrumentVersion).asString;
var siteCount = (~qmwQFTSiteCount ? 8).asInteger;
var dataPort = (~qmwQFTDataPort ? 17850).asInteger;
var controlPort = (~qmwQFTControlPort ? 17851).asInteger;
var terrainEnabled = (~qmwQFTEffectiveTerrainEnabled ? false);
var splitFieldOutput = (~qmwQFTSplitFieldOutput ? false);
// V4.2 may attach one persistent Bloch-spatial source to the existing four
// event-voice controls. The wrapper's explicit capability flag is the sole
// authority: display text must never silently remove an audio channel.
// Other versions retain the original four-lane mixer because they do not set
// this flag in their fresh sclang process.
var blochVoiceEnabled = (~qmwQFTV42BlochVoiceEnabled ? false).asBoolean;
var voiceCount = if(blochVoiceEnabled, { 5 }, { 4 });
var terrainPort = (~qmwQFTEffectiveTerrainPort ? 17863).asInteger;
var terrainRoot = "/qmw/qft/v4_2/effective_terrain";
// V4/V5 opt into a longer resonator tail while V3 retains its original range.
var decayMaximum = (~qmwQFTDecayMaximum ? 2.0).asFloat.max(0.03);
var pooledSlotCount = 32;
var oscRoot = "/qmw/qft/v" ++ instrumentVersion;
var control = NetAddr("127.0.0.1", controlPort);
var window, phiView, energyView, occupationView, correlationView;
var absoluteEnergyView, absoluteEnergyStatus;
var status, parameterStatus, temporalStatus, performanceStatus, stateMenu;
var bogoliubovStatus, meshScaleStatus, meshColorMenu, correlationMeshButton;
var makeLabel, makeSlider, makeFieldMesh;
var sendLocalized, sendDisplacement, sendSqueezing, sendField;
var sendPerformanceConfig, updateBogoliubov;
var presetMenu, applyPreset, capturePreset, recallPresetSlot;
var presetSlots, presetPath;
var presetSlotCount, loadedPresetSlots;
var temporalModeMenu, clockAdapterMenu, pitchMenu, voiceMenu;
var rendererModeMenu, fieldMixSlider;
var audioDeviceMenu, outputLayoutMenu, audioStatus;
var audioDeviceItems, audioDeviceValues, refreshAudioDevices;
var resolveAbletonBridgeDevice;
var midiInputMenu, midiInputStatus, midiInputItems, midiInputValues;
var refreshMIDIInputs, installMIDIPresetMapping;
var fundamentalSlider, fundamentalModeMenu, applyFundamental;
var oddEvenStereoSlider;
var coherentSlider, momentumSlider, fluctuationSlider;
var vacuumSlider, decaySlider, energyDecaySlider, masterSlider, distanceSlider, clockSlider;
var pulseSlider, recordingButton, recordingDir, recordingPath;
var siteGainView, siteMuteButtons, pulseMeterView, pulseMeterStatus;
var fieldGainView, fieldMuteButtons;
var voiceGainView, voiceMuteButtons, voiceMixerStatus;
var ringModBlendSlider, ringModHarmonicSlider, ringModFineTuneSlider;
var wavefoldBlendSlider, wavefoldDriveSlider, wavefoldWarpSlider, wavefoldWarpShapeMenu;
var fuzzBlendSlider, fuzzDriveSlider;
var fuzzSecondSlider, fuzzThirdSlider, fuzzBiasSlider, fuzzToneSlider;
var fmRatioSlider, fmIndexSlider, fmQuantumDepthSlider;
var descriptorSourceMenu, descriptorClockMenu, descriptorStatus;
var descriptorRotationSlider;
var descriptorManualSliders, descriptorDepthSliders;
var descriptorRateSliders, descriptorPhaseSliders;
var squeezingMagnitudeSlider, squeezingPhaseSlider, temperatureSlider;
var massSlider, propagationSlider, siteSlider, amplitudeSlider, modeSlider;
var displacementReSlider, displacementImSlider, soundButton;
var steadyRateSlider, euclidHitsSlider, euclidStepsSlider;
var geodesicBendSlider, recursiveDepthSlider, updateEuclideanPattern;
var terrainStatus, terrainGlobalStatus, terrainEventStatus;
var terrainAvailableButton, terrainSonifyButton, terrainEventButton;
var terrainQView, terrainQdotView;

thisProcess.openUDPPort(dataPort);
if(terrainEnabled) { thisProcess.openUDPPort(terrainPort) };

~qmwQFTV3Revision = -1;
~qmwQFTV3Time = 0;
~qmwQFTV3StageValid = false;
~qmwQFTV3Phi = Array.fill(siteCount, 0);
~qmwQFTV3Pi = Array.fill(siteCount, 0);
~qmwQFTV3Energy = Array.fill(siteCount, 0);
~qmwQFTV3Occupations = Array.fill(siteCount, 0);
~qmwQFTV3Frequencies = Array.fill(siteCount, 0.6);
~qmwQFTV3Correlation = Array.fill(siteCount * siteCount, 0);
~qmwQFTV3FieldHistory = Array.new;
~qmwQFTV3MomentumHistory = Array.new;
~qmwQFTV3EnergyHistory = Array.new;
~qmwQFTV3UncertaintyHistory = Array.new;
// The GUI shares sclang's scheduler with OSC/event handling.  At 32 sites a
// 48-row, three-surface mesh plus a 32x32 correlation repaint can starve pulse
// dispatch even though the server DSP and field evolution still have headroom.
// This is display decimation only: every physical frame is still received and
// committed to the synth at the full lattice resolution.
// The mesh is a read-only history view. A 24-frame, 4 Hz raster cadence keeps
// its perspective surface legible without allowing vector painting to contend
// with the live control or audio server threads.
~qmwQFTV3MeshHistoryLength = 24;
~qmwQFTV3MeshFrameStride = if(siteCount >= 32, { 6 }, { 4 });
// Start near zero so the first physical frame establishes the visible range.
// Starting at 1 flattened the normally sub-unit field into a black-looking line.
~qmwQFTV3MeshScale = 1e-6;
~qmwQFTV3MeshColorMode = 0;
~qmwQFTV3MeshCorrelations = 1;
~qmwQFTV3Global = [0, 1];
~qmwQFTV3Parameters = [
    "localized", 0.6, 1, siteCount.div(2), 1, 0, 0.8, 0, 0.5, 0, 0.8
];
~qmwQFTV3Site = siteCount.div(2);
~qmwQFTV3Amplitude = 1;
~qmwQFTV3DisplacementRe = 0.8;
~qmwQFTV3DisplacementIm = 0;
~qmwQFTV3SqueezingMagnitude = 0.5;
~qmwQFTV3SqueezingPhase = 0;
~qmwQFTV3Mass = 0.6;
~qmwQFTV3Speed = 1;
~qmwQFTV3PitchMode = 1;
~qmwQFTV3SitePitchRatios = Array.series(siteCount, 1, 1);
~qmwQFTV3SiteGains = Array.fill(siteCount, 1.0);
~qmwQFTV3SiteMutes = Array.fill(siteCount, 0);
~qmwQFTV3EffectiveSiteGains = {
    Array.fill(siteCount, { |site|
        ~qmwQFTV3SiteGains[site].clip(0, 2)
        * (1 - ~qmwQFTV3SiteMutes[site].clip(0, 1))
    })
};
~qmwQFTV3UpdateSiteAudioGains = {
    // Pulse gain and mute are sampled when each pulse node is created.
    // The continuous vacuum reference intentionally has no pulse-lane trim.
    nil
};
~qmwQFTV3PulseMeters = Array.fill(siteCount, 0.0);
~qmwQFTV3TemporalGlobal = [0, 0, 0, 0, 0, 0, 0, 0];
// The field process reports this back after a temporal control edit.  It is
// configuration/provenance only; it does not supplement the physical frame.
~qmwQFTV3TemporalConfig = [0, 0.025, 1.0, 0.6, "poisson"];
~qmwQFTV3TemporalControlPending = "";
~qmwQFTV3SitePulses = Array.fill(siteCount, 0);
~qmwQFTV3PulseVoiceMode = 1;
// Optional pooled renderer: thirty-two logical slots live in one persistent
// server Synth and are retriggered by control updates. It is an audio adapter
// and does not change the QFT/GPE/Hilbert event streams.
~qmwQFTV3PooledRendererEnabled = false;
~qmwQFTV3PooledSlotCount = pooledSlotCount;
~qmwQFTV3PooledSlotTokens = Array.fill(pooledSlotCount, 0.0);
~qmwQFTV3PooledSlotFreeAt = Array.fill(pooledSlotCount, -1e9);
~qmwQFTV3PooledFrequency = Array.fill(pooledSlotCount, 220.0);
~qmwQFTV3PooledStrength = Array.fill(pooledSlotCount, 0.0);
~qmwQFTV3PooledField = Array.fill(pooledSlotCount, 0.0);
~qmwQFTV3PooledMomentum = Array.fill(pooledSlotCount, 0.0);
~qmwQFTV3PooledEnergy = Array.fill(pooledSlotCount, 0.0);
~qmwQFTV3PooledDecay = Array.fill(pooledSlotCount, 0.28);
~qmwQFTV3PooledAmplitude = Array.fill(pooledSlotCount, 0.0);
~qmwQFTV3PooledLane = Array.fill(pooledSlotCount, 0.0);
~qmwQFTV3PooledBankSynth = nil;
~qmwQFTV3PooledMixerSynth = nil;
~qmwQFTV3PooledPulseBus = nil;
~qmwQFTV3VoiceCount = voiceCount;
~qmwQFTV3BlochVoiceEnabled = blochVoiceEnabled;
~qmwQFTV3VoiceGains = Array.fill(voiceCount, { |voice|
    if(voice == 1, { 1.0 }, { 0.0 })
});
// The persistent Bloch adapter has more intrinsic averaging than the transient
// pluck voices. V4.2 gives only that fifth lane another 6 dB of fader headroom:
// legacy voices remain 0..2, while Bloch reaches 0..4. All defaults are intact.
~qmwQFTV3VoiceGainCeilings = Array.fill(voiceCount, { |voice|
    if(blochVoiceEnabled and: { voice == 4 }, { 4.0 }, { 2.0 })
});
~qmwQFTV3VoiceMutes = Array.fill(voiceCount, 0);
~qmwQFTV3VoiceGainBus = nil;
// V4.2b ports the V3/QRI post-voice send idea into this instrument without
// changing the dry V4.2 graph. Seven named sources share a parallel stereo FX
// bus: four pluck timbres, Bloch, continuous field, and Parseval. Plain V4.2
// leaves the feature disabled and allocates no additional buses.
~qmwQFTV42BFXSourceNames = [
    "Simple", "Gaussian", "Layered", "QHO FM", "Bloch", "Field", "Parseval"
];
~qmwQFTV42BFXSends = Array.fill(7, { |index|
    ((~qmwQFTV42BFXSends ? [])[index] ? 0.0).asFloat.clip(0, 1)
});
~qmwQFTV42BFXSendBus = nil;
~qmwQFTV42BFXSendControlBus = nil;
~qmwQFTV42BUpdateFXSends = {
    ~qmwQFTV42BFXSendControlBus !? { |bus|
        bus.setn(~qmwQFTV42BFXSends)
    }
};
~qmwQFTV3EffectiveVoiceGains = {
    Array.fill(voiceCount, { |voice|
        ~qmwQFTV3VoiceGains[voice].clip(
            0, ~qmwQFTV3VoiceGainCeilings[voice]
        )
        * (1 - ~qmwQFTV3VoiceMutes[voice].clip(0, 1))
    })
};
~qmwQFTV3VoiceGainSliderValues = {
    Array.fill(voiceCount, { |voice|
        ~qmwQFTV3VoiceGains[voice]
            / ~qmwQFTV3VoiceGainCeilings[voice].max(0.0001)
    })
};
~qmwQFTV3UpdateVoiceMixer = {
    ~qmwQFTV3VoiceGainBus !? { |bus|
        bus.setn(~qmwQFTV3EffectiveVoiceGains.())
    }
};
~qmwQFTV3PulseMix = 0.8;
// The renderer selector is strictly downstream. Field is a persistent sonic
// observation of committed phi+i*pi lanes; Plucks retains the established
// event renderer; Hybrid makes both audible without changing either source.
~qmwQFTV3RendererMode = 2;
~qmwQFTV3FieldMix = 0.20;
~qmwQFTV3FieldLaneGains = Array.fill(siteCount, 1.0);
~qmwQFTV3FieldLaneMutes = Array.fill(siteCount, 0);
~qmwQFTV3EffectiveFieldLaneGains = {
    Array.fill(siteCount, { |site|
        ~qmwQFTV3FieldLaneGains[site].clip(0, 2)
        * (1 - ~qmwQFTV3FieldLaneMutes[site].clip(0, 1))
    })
};
~qmwQFTV3UpdateFieldSpectralMix = {
    ~qmwQFTV3Synth !? { |synth|
        synth.setn(\fieldLaneGains, ~qmwQFTV3EffectiveFieldLaneGains.())
    }
};
~qmwQFTV3UpdateRendererMode = {
    var mode = ~qmwQFTV3RendererMode.asInteger.clip(0, 2);
    var fieldLevel = if((mode == 0) or: { mode == 2 }, {
        ~qmwQFTV3FieldMix.clip(0, 0.6)
    }, { 0.0 });
    var pulseLevel = if(mode > 0, { 1.0 }, { 0.0 });
    ~qmwQFTV3Synth !? { |synth| synth.set(\fieldLevel, fieldLevel) };
    ~qmwQFTV3PulseMixerSynth !? { |synth|
        synth.set(\pulseLevel, pulseLevel)
    };
    ~qmwQFTV3PooledMixerSynth !? { |synth|
        synth.set(\pulseLevel, pulseLevel)
    };
};
// Stereo is a downstream presentation of harmonic/site lanes only. Lane 0 is
// harmonic 1, so even-numbered lane indices are odd harmonics and pan left;
// odd-numbered lane indices are even harmonics and pan right. Width zero is
// mono and width one is full separation.
~qmwQFTV3OddEvenStereoWidth = 1.0;
~qmwQFTV3UpdateOddEvenStereo = {
    var width = ~qmwQFTV3OddEvenStereoWidth.clip(0, 1);
    ~qmwQFTV3PulseMixerSynth !? { |synth|
        synth.set(\oddEvenWidth, width)
    };
    ~qmwQFTV3PooledMixerSynth !? { |synth|
        synth.set(\oddEvenWidth, width)
    };
    ~qmwQFTV3Synth !? { |synth|
        synth.set(\oddEvenWidth, width)
    };
};
~qmwQFTV3RingModBlend = 0;
~qmwQFTV3RingModHarmonic = 2;
// A manual, bipolar detune of the ring carrier only. This is an audio
// sideband control in cents; it never changes field frequencies or scale data.
~qmwQFTV3RingModFineTuneCents = 0.0;
~qmwQFTV3RingModMixBus = nil;
~qmwQFTV3RingModFrequencyBus = nil;
~qmwQFTV3WavefoldBlend = 0;
~qmwQFTV3WavefoldDrive = 4;
~qmwQFTV3WavefoldWarpAmount = 0;
~qmwQFTV3WavefoldWarpShape = 0;
~qmwQFTV3WavefoldMixBus = nil;
~qmwQFTV3WavefoldDriveBus = nil;
~qmwQFTV3WavefoldWarpAmountBus = nil;
~qmwQFTV3WavefoldWarpShapeBus = nil;
~qmwQFTV3FuzzBlend = 0;
~qmwQFTV3FuzzDrive = 2.5;
~qmwQFTV3FuzzSecond = 0.0;
~qmwQFTV3FuzzThird = 0.65;
~qmwQFTV3FuzzHigher = 0.85;
~qmwQFTV3FuzzBias = 0.0;
~qmwQFTV3FuzzTone = 0.35;
~qmwQFTV3FuzzMixBus = nil;
~qmwQFTV3FuzzDriveBus = nil;
~qmwQFTV3FuzzSecondBus = nil;
~qmwQFTV3FuzzThirdBus = nil;
~qmwQFTV3FuzzHigherBus = nil;
~qmwQFTV3FuzzBiasBus = nil;
~qmwQFTV3FuzzToneBus = nil;
~qmwQFTV3FMRatio = 2;
~qmwQFTV3FMIndex = 0.5;
~qmwQFTV3FMQuantumDepth = 2;
~qmwQFTV3UpdateRingMod = {
    ~qmwQFTV3RingModMixBus !? { |bus|
        bus.set(~qmwQFTV3RingModBlend.clip(0, 1))
    };
    ~qmwQFTV3RingModFrequencyBus !? { |bus|
        bus.set(
            (~qmwQFTV3Fundamental * ~qmwQFTV3RingModHarmonic
                * 2.pow(~qmwQFTV3RingModFineTuneCents.clip(-100, 100) / 1200))
            .clip(0.1, 16000)
        )
    };
};
~qmwQFTV3UpdateWavefold = {
    ~qmwQFTV3WavefoldMixBus !? { |bus|
        bus.set(~qmwQFTV3WavefoldBlend.clip(0, 1))
    };
    ~qmwQFTV3WavefoldDriveBus !? { |bus|
        bus.set(~qmwQFTV3WavefoldDrive.clip(1, 32))
    };
    ~qmwQFTV3WavefoldWarpAmountBus !? { |bus|
        bus.set(~qmwQFTV3WavefoldWarpAmount.clip(0, 1))
    };
    ~qmwQFTV3WavefoldWarpShapeBus !? { |bus|
        bus.set(~qmwQFTV3WavefoldWarpShape.clip(0, 3).round)
    };
};
~qmwQFTV3UpdateFuzz = {
    ~qmwQFTV3FuzzMixBus !? { |bus|
        bus.set(~qmwQFTV3FuzzBlend.clip(0, 1))
    };
    ~qmwQFTV3FuzzDriveBus !? { |bus| bus.set(~qmwQFTV3FuzzDrive.clip(0.25, 12)) };
    ~qmwQFTV3FuzzSecondBus !? { |bus| bus.set(~qmwQFTV3FuzzSecond.clip(0, 2)) };
    ~qmwQFTV3FuzzThirdBus !? { |bus| bus.set(~qmwQFTV3FuzzThird.clip(0, 2)) };
    ~qmwQFTV3FuzzHigherBus !? { |bus| bus.set(~qmwQFTV3FuzzHigher.clip(0, 2)) };
    ~qmwQFTV3FuzzBiasBus !? { |bus| bus.set(~qmwQFTV3FuzzBias.clip(-0.75, 0.75)) };
    ~qmwQFTV3FuzzToneBus !? { |bus| bus.set(~qmwQFTV3FuzzTone.clip(0, 1)) };
};
~qmwQFTV3ClockMode = 0;
~qmwQFTV3ClockScale = 1;
~qmwQFTV3SteadyRate = 7;
~qmwQFTV3EuclideanHits = 5;
~qmwQFTV3EuclideanSteps = 8;
~qmwQFTV3EuclideanStep = 0;
~qmwQFTV3QuantumEuclideanStep = 0;
~qmwQFTV3RecursiveDepth = 3;
~qmwQFTV3EuclideanMask = Array.fill(16, { |index|
    if(index < 8, { (((index * 5) % 8) < 5).asInteger }, { 0 })
});
~qmwQFTV3RefreshClockStatus = {
    var config = ~qmwQFTV3TemporalConfig;
    var bures = config[1].asFloat;
    var engineScale = config[2].asFloat;
    var recordCount = ~qmwQFTV3TemporalGlobal[1].asInteger;
    var delta = ~qmwQFTV3TemporalGlobal[3].asFloat;
    var localHz = (~qmwQFTV3SteadyRate * ~qmwQFTV3ClockScale)
        .min(1 / ~qmwQFTV3SteadyTargetSeconds);
    var localMilliseconds = 1000 / localHz.max(0.01);
    var pending = ~qmwQFTV3TemporalControlPending;
    var text;
    case
    { ~qmwQFTV3ClockMode == 0 } {
        text = "Quantum Bures: d %  scale %x  records %  delta %".format(
            bures.round(0.0001), engineScale.round(0.001), recordCount,
            delta.round(0.0001)
        );
    }
    { [1, 2].includes(~qmwQFTV3ClockMode) } {
        text = "% adapter: % Hz / % ms; Bures d % is parked".format(
            ["Steady", "Euclidean"][~qmwQFTV3ClockMode - 1],
            localHz.round(0.01), localMilliseconds.round(0.1),
            bures.round(0.0001)
        );
    }
    { ~qmwQFTV3ClockMode == 3 } {
        text = "Q-Euclidean: Bures d %  scale %x; records are Euclidean-gated".format(
            bures.round(0.0001), engineScale.round(0.001)
        );
    }
    { ~qmwQFTV3ClockMode == 4 } {
        text = "Q-Geodesic: Bures d %  scale %x; curvature weighting active".format(
            bures.round(0.0001), engineScale.round(0.001)
        );
    }
    {
        text = "Q-Recursive: Bures d %  scale %x; local delay fan-out active".format(
            bures.round(0.0001), engineScale.round(0.001)
        );
    };
    if(pending.size > 0) { text = text ++ "  | " ++ pending };
    { temporalStatus !? { |view| view.string_(text) } }.defer;
};
~qmwQFTV3PulseCache = Array.fill(siteCount, { |site|
    [site, 0.02, 0, 0, 0, 0, 0, 0, 1, 0, 0]
});
~qmwQFTV42TerrainRevision = -1;
~qmwQFTV42TerrainStageValid = false;
~qmwQFTV42TerrainAvailable = 0;
~qmwQFTV42TerrainDimension = 0;
~qmwQFTV42TerrainProvider = "none";
~qmwQFTV42TerrainQ = Array.fill(siteCount, 0.0);
~qmwQFTV42TerrainQdot = Array.fill(siteCount, 0.0);
~qmwQFTV42TerrainGlobal = Array.fill(10, 0.0);
~qmwQFTV42TerrainLastSeen = -1.0;
~qmwQFTV42TerrainSonify = 1;
~qmwQFTV42TerrainLastEvent = [0, 0, 0, 0.0, 0.0, "none"];
~qmwQFTV3DecaySeconds = 0.28;
// This is intentionally downstream from the scalar-field frame. It observes
// total energy to set resonator lifetime; it never writes into the field.
// The bipolar attenuverter is neutral at zero: positive lengthens tails,
// negative shortens them. Full scale equals one octave at the E=100 reference.
~qmwQFTV3EnergyDecayAttenuverter = 0.0;
~qmwQFTV3EffectiveDecaySeconds = ~qmwQFTV3DecaySeconds;
~qmwQFTV3EnergyDecayControl = {
    ((~qmwQFTV3Global[0].max(0) + 1).log / 101.log).clip(0, 1)
};
~qmwQFTV3EffectiveDecay = {
    (
        ~qmwQFTV3DecaySeconds
        * 2.pow(
            ~qmwQFTV3EnergyDecayAttenuverter.clip(-1, 1)
            * ~qmwQFTV3EnergyDecayControl.()
        )
    ).clip(0.03, decayMaximum)
};
~qmwQFTV3ApplyEnergyDecay = {
    ~qmwQFTV3EffectiveDecaySeconds = ~qmwQFTV3EffectiveDecay.();
    if(~qmwQFTV3AudioReady) {
        ~qmwQFTV3Synth !? { |synth|
            synth.set(\decaySeconds, ~qmwQFTV3EffectiveDecaySeconds)
        };
    };
};
~qmwQFTV3Fundamental = 72;
// Fundamental tuning is a downstream audio/performance choice. Smooth mode
// preserves continuous Hz control; 12-TET snaps to the nearest semitone with
// A4 = 440 Hz without changing the authoritative field frequencies.
~qmwQFTV3FundamentalMode = 0;
~qmwQFTV3MasterAmp = 0.32;
// Version wrappers may keep the adapter silent until a requested startup
// preset has configured every control.
~qmwQFTV3SoundEnabled = if(~qmwQFTV3StartupMuted == true, { 0 }, { 1 });
~qmwQFTV3CoherentMix = 1;
// Perceptual calibration for the Gaussian GenExpr pulse adapter.  This changes
// only audio gain; x/y/z, purity, coherence, entropy, and field evolution stay
// authoritative and untouched.
~qmwQFTV3GaussianPulseGain = 3.0;
// Equal-power attenuation keeps the two-voice layered mode near the loudness
// of either solo voice instead of simply summing both at full amplitude.
~qmwQFTV3LayeredVoiceGain = 0.707;
~qmwQFTV3MomentumMix = 0.45;
~qmwQFTV3FluctuationMix = 0;
~qmwQFTV3VacuumMix = 0.05;
// Descriptor modulation is an event-sampled sound adapter. It never writes
// back into the Gaussian field, its covariance, or the QMW temporal engine.
~qmwQFTV3DescriptorSource = 0;
~qmwQFTV3DescriptorClock = 0;
~qmwQFTV3DescriptorManual = [0.0, 0.0, 0.0];
~qmwQFTV3DescriptorLFODepth = [0.0, 0.0, 0.0];
~qmwQFTV3DescriptorLFORate = [0.11, 0.17, 0.23];
~qmwQFTV3DescriptorLFOPhase = [0.0, 120.0, 240.0];
~qmwQFTV3DescriptorRotationDegrees = 0;
~qmwQFTV3EffectiveDescriptor = { |x, y, z|
    var quantum = [x, y, z];
    var time = if(~qmwQFTV3DescriptorClock == 0, {
        Main.elapsedTime
    }, {
        ~qmwQFTV3TemporalGlobal[2]
    });
    var lfo = Array.fill(3, { |axis|
        (
            (2pi * ~qmwQFTV3DescriptorLFORate[axis] * time)
            + (~qmwQFTV3DescriptorLFOPhase[axis] * pi / 180)
        ).sin * ~qmwQFTV3DescriptorLFODepth[axis]
    });
    var result = case
    { ~qmwQFTV3DescriptorSource == 0 } { quantum }
    { ~qmwQFTV3DescriptorSource == 1 } { ~qmwQFTV3DescriptorManual }
    { ~qmwQFTV3DescriptorSource == 2 } {
        quantum + ~qmwQFTV3DescriptorManual
    }
    { ~qmwQFTV3DescriptorSource == 3 } { quantum + lfo }
    { ~qmwQFTV3DescriptorManual + lfo };
    var clipped = result.collect { |value| value.clip(-1, 1) };
    var theta = ~qmwQFTV3DescriptorRotationDegrees.clip(-180, 180)
        * pi / 180;
    var rotatedX = (clipped[0] * theta.cos) - (clipped[1] * theta.sin);
    var rotatedY = (clipped[0] * theta.sin) + (clipped[1] * theta.cos);
    [rotatedX.clip(-1, 1), rotatedY.clip(-1, 1), clipped[2]]
};
~qmwQFTV3SelectedOutputDevice = s.options.outDevice;
~qmwQFTV3OutputChannels = if(splitFieldOutput, {
    if(s.options.numOutputBusChannels >= 8, { 8 }, { 4 })
}, {
    if(s.options.numOutputBusChannels >= 8, { 8 }, { 2 })
});
// Timed pulse onsets use a bounded audio-server control block. At 48 kHz,
// 128 samples is 2.67 ms: enough resolution for the 20 ms steady target
// without the higher CPU cost of a 64-sample block. This is audio-only;
// it does not change the QFT/GPE state or its source-frame cadence.
~qmwQFTV3TimingBlockSize = 128;
~qmwQFTV3SteadyTargetSeconds = 0.020;
~qmwQFTV3SteadyLookaheadSeconds = 0.010;
~qmwQFTV3SteadyJitterBudgetSeconds = 0.003;
if(s.serverRunning.not, { s.options.blockSize = ~qmwQFTV3TimingBlockSize });
~qmwQFTV3AudioReady = false;
~qmwQFTV3RecordingReady = false;
~qmwQFTV3ActivePulseVoices = List.new;
// Audio-adapter safety governor. These limits do not discard or alter any
// field/flow frame: they only decide which simultaneous sonic excitations can
// be rendered safely by scsynth. A whole event is admitted or deferred, so a
// four-voice event is never reduced to an arbitrary partial subset.
~qmwQFTV3PulseGovernorEnabled = true;
// The transport/state layer may carry thirty-two logical density channels,
// while this independent nonlinear pulse renderer is bounded to sixteen
// physical voices. A 32-node nonlinear renderer exceeds real-time CPU on the
// target system; a future 32-voice audio mode must use pooled/shared DSP.
~qmwQFTV3MaximumPulseVoices = 16;
~qmwQFTV3PulseVoiceBudget = {
    var decay = ~qmwQFTV3EffectiveDecaySeconds;
    if(decay <= 0.35, { 16 }, {
        if(decay <= 0.75, { 14 }, {
            if(decay <= 1.25, { 12 }, { 10 })
        })
    })
};
// The steady scheduler targets 20 ms between server-timestamped attacks.
// This 17 ms admission floor leaves its declared 3 ms jitter budget without
// allowing a late language callback to create an arbitrary burst.
~qmwQFTV3MinimumPulseInterval = 0.017;
~qmwQFTV3PulseAdmissionInterval = {
    // At the default 280 ms tail this remains the 17 ms timing floor. Longer
    // tails lengthen only sonic re-admission, preventing overlap growth while
    // leaving the authoritative Bures records untouched.
    ~qmwQFTV3MinimumPulseInterval.max(
        (~qmwQFTV3EffectiveDecaySeconds * 0.06).min(0.18)
    )
};
~qmwQFTV3LastPulseTime = Array.fill(siteCount, -1e9);
~qmwQFTV3GovernorDroppedEvents = 0;
~qmwQFTV3SteadySiteCursor = 0;
~qmwQFTV3SteadyTickCount = 0;
~qmwQFTV3SteadyLateTickCount = 0;
~qmwQFTV3SteadyWorstLateSeconds = 0.0;
~qmwQFTV3ScheduledPulseTime = nil;
// Preserve approximate aggregate pulse level as lattice resolution grows.
~qmwQFTV3SiteGain = (8 / siteCount).sqrt;
recordingDir = thisProcess.nowExecutingPath.dirname.dirname
    +/+ "qmw/qft/recordings";
presetPath = thisProcess.nowExecutingPath.dirname.dirname
    +/+ if(instrumentVersion >= 5, {
        "qmw/qft/presets/qft_v%_%_slots.archive".format(
            instrumentVersion, siteCount
        )
    }, {
        "qmw/qft/presets/qft_v%_slots.archive".format(instrumentVersion)
    });
presetSlotCount = 32;
// SuperCollider follows the common MIDI convention in which note 12 is C0.
// Set ~qmwQFTMIDIPresetBaseNote before launching to accommodate keyboards that
// display another octave number for the same MIDI note.
~qmwQFTV3MIDIPresetBaseNote = (~qmwQFTMIDIPresetBaseNote ? 12)
    .asInteger.clip(0, 127);
~qmwQFTV3SelectedMIDIInputUID = ~qmwQFTV3SelectedMIDIInputUID ? nil;
loadedPresetSlots = if(File.exists(presetPath), {
    try { Object.readArchive(presetPath) } { Array.new }
}, {
    Array.new
});
// Copy old banks into the larger array instead of discarding eight-slot archives.
presetSlots = Array.newClear(presetSlotCount);
if(loadedPresetSlots.isKindOf(Array)) {
    loadedPresetSlots.size.min(presetSlotCount).do { |slot|
        presetSlots[slot] = loadedPresetSlots[slot];
    };
};
~qmwQFTV3SpawnPulseVoice = { |definition, arguments|
    var voice;
    // doneAction may free a short pulse before its deferred onFree callback
    // updates this client-side list. Never send a second /n_free for an
    // apparently old voice: prune confirmed completions and shed the new
    // event if the live cap is genuinely full.
    ~qmwQFTV3ActivePulseVoices = ~qmwQFTV3ActivePulseVoices.select {
        |item| item.isPlaying
    };
    if(
        ~qmwQFTV3ActivePulseVoices.size < ~qmwQFTV3MaximumPulseVoices,
        {
            voice = Synth.head(~qmwQFTV3SourceGroup, definition, arguments);
            voice.register;
            ~qmwQFTV3ActivePulseVoices.add(voice);
            voice.onFree({
                { ~qmwQFTV3ActivePulseVoices.remove(voice) }.defer
            });
            voice
        },
        { nil }
    )
};
~qmwQFTV3AdmitPulseEvent = { |site, requiredVoices, scheduledTime|
    // A timestamped steady event is admitted against its intended server
    // onset, not the incidental moment sclang happened to build its bundle.
    var now = scheduledTime ? Main.elapsedTime;
    var admitted = true;
    // Keep the client-side count accurate before admitting a new complete
    // event. doneAction frees the server node, while onFree updates this list.
    ~qmwQFTV3ActivePulseVoices = ~qmwQFTV3ActivePulseVoices.select {
        |item| item.isPlaying
    };
    if(~qmwQFTV3PulseGovernorEnabled == true, {
        if((now - ~qmwQFTV3LastPulseTime[site])
            < ~qmwQFTV3PulseAdmissionInterval.(), {
            admitted = false;
        });
        if((~qmwQFTV3ActivePulseVoices.size + requiredVoices)
            > ~qmwQFTV3PulseVoiceBudget.(), {
            admitted = false;
        });
        if(admitted, {
            ~qmwQFTV3LastPulseTime[site] = now;
        }, {
            ~qmwQFTV3GovernorDroppedEvents = ~qmwQFTV3GovernorDroppedEvents + 1;
        });
    });
    admitted
};
~qmwQFTV3UpdatePitchRatios = {
    ~qmwQFTV3SitePitchRatios = case
    { ~qmwQFTV3PitchMode == 0 } {
        ~qmwQFTV3Frequencies / ~qmwQFTV3Frequencies[0].max(0.001)
    }
    { ~qmwQFTV3PitchMode == 1 } { Array.series(siteCount, 1, 1) }
    { Array.series(siteCount, 1, 2) };
    if(~qmwQFTV3AudioReady) {
        ~qmwQFTV3Synth !? { |synth|
            synth.setn(\sitePitchRatios, ~qmwQFTV3SitePitchRatios)
        };
    };
};

~qmwQFTV3BuildAudio = {
    var fxEnabled = (~qmwQFTV42BFXEnabled ? false).asBoolean;
    var fxSendBusIndex = 0;
    var fxSendControlBase = 0;
    ~qmwQFTV3AudioReady = false;
    SynthDef(\qmwScalarFieldInstrumentV3, {
        |out=0, fundamental=72, vacuumMix=0.05,
        decaySeconds=0.28, fieldLevel=0.20, oddEvenWidth=1,
        masterAmp=0.32, soundEnabled=1, lagSeconds=0.08, gate=1,
        fxSendBus=0, fxSendControlBus=0, fxEnabled=0|
        var occupations = NamedControl.kr(
            \occupations, Array.fill(siteCount, 0), lagSeconds
        ).max(0);
        var frequencies = NamedControl.kr(
            \frequencies,
            Array.fill(siteCount, 0.6),
            lagSeconds
        ).max(0.001);
        var sitePitchRatios = NamedControl.kr(
            \sitePitchRatios, Array.series(siteCount, 1, 1), lagSeconds
        ).max(0.01);
        var fieldAmplitudes = NamedControl.kr(
            \fieldAmplitudes, Array.fill(siteCount, 0), lagSeconds
        ).clip(0, 1);
        var fieldPhases = NamedControl.kr(
            \fieldPhases, Array.fill(siteCount, 0), lagSeconds
        );
        var fieldDrives = NamedControl.kr(
            \fieldDrives, Array.fill(siteCount, 0), lagSeconds
        ).clip(-1, 1);
        var fieldLaneGains = NamedControl.kr(
            \fieldLaneGains, Array.fill(siteCount, 1), lagSeconds
        ).clip(0, 2);
        // phi+i*pi is exposed only as a read-only continuous sound adapter.
        // Its magnitude controls lane presence and its phase/real component
        // provide smooth phase and beating; this does not evolve the field or
        // claim that the oscillators are physical particles.
        var fieldStereoWidth = VarLag.kr(oddEvenWidth.clip(0, 1), 0.05);
        var fieldVoice = Mix.fill(siteCount, { |site|
            var frequency = Lag.kr(
                (fundamental * sitePitchRatios[site]).clip(1, 16000), 0.12
            );
            var amount = LagUD.kr(
                fieldAmplitudes[site],
                0.035 + (site * 0.002),
                0.42 + (site * 0.018)
            );
            var phase = Lag.kr(fieldPhases[site], 0.16);
            var detune = Lag.kr(fieldDrives[site], 0.18) * 0.0018;
            var carrier = SinOsc.ar(frequency * (1 + detune), phase);
            var companion = SinOsc.ar(
                frequency * (1 - (detune * 0.61)), phase * 0.618
            );
            Pan2.ar(
                (carrier + (companion * 0.38)) * amount
                    * fieldLaneGains[site],
                (((site % 2) * 2) - 1) * fieldStereoWidth
            )
        }) * Lag.kr(fieldLevel.clip(0, 0.6), 0.12) / siteCount.sqrt;
        // The free-field normal frequencies determine spectral ratios for the
        // optional vacuum reference. Pitch deviation is applied only to
        // site-local pulse records, where a local Gaussian descriptor exists;
        // the vacuum reference is not given a fictitious aggregate shift.
        var modeHz = fundamental
            * (frequencies / frequencies[0]).clip(0.5, 8);
        // Vacuum rendering is optional and separately labeled. Its weights are
        // proportional to sqrt(hbar/(2 omega_k)) with hbar=1; it does not claim
        // particles are present in the vacuum.
        var vacuumWeights = (0.5 / frequencies).sqrt.clip(0, 1.5);
        var vacuumVoice = Splay.ar(
            Ringz.ar(
                PinkNoise.ar(0.018 ! siteCount),
                modeHz,
                decaySeconds.clip(0.03, decayMaximum)
            ) * vacuumWeights,
            0.85,
            0.10
        ) * vacuumMix;
        var envelope = EnvGen.kr(
            // This is a persistent carrier owned by ~qmwQFTV3SourceGroup.
            // Its controls are updated for every accepted field frame, so it
            // must never self-free and leave the GUI with a stale node ID.
            // Group teardown in ~qmwQFTV3Stop remains its explicit lifetime.
            Env.asr(0.03, 1, 0.2), gate
        );
        var signal = fieldVoice + vacuumVoice;
        var emitted = Limiter.ar(
            LeakDC.ar(signal) * masterAmp * soundEnabled * envelope, 0.92
        );
        var fxSend = Lag.kr(In.kr(fxSendControlBus).clip(0, 1), 0.03)
            * fxEnabled.clip(0, 1);
        Out.ar(out, emitted);
        Out.ar(fxSendBus, emitted * fxSend);
    }).add;

    // One node is created per Gaussian record. Simultaneous site records and
    // repeated records at one site therefore overlap instead of overwriting a
    // shared trigger/site control.
    SynthDef(\qmwScalarFieldPulseSimpleV3, {
        |out=0, lane=0, frequency=220, strength=0.2,
        fieldColor=0, momentumColor=0, fieldDepth=1, momentumDepth=0.45,
        localEnergy=0, decaySeconds=0.28, amp=0.12,
        voiceGainBus=0,
        ringMixBus=0, ringFrequencyBus=0,
        wavefoldMixBus=0, wavefoldDriveBus=0, wavefoldWarpAmountBus=0,
        wavefoldWarpShapeBus=0, fuzzMixBus=0, fuzzDriveBus=0,
        fuzzSecondBus=0, fuzzThirdBus=0, fuzzHigherBus=0, fuzzBiasBus=0,
        fuzzToneBus=0, fxSendBus=0, fxSendControlBus=0, fxEnabled=0|
        var strike = PinkNoise.ar(0.24) * Decay2.ar(
            Impulse.ar(0), 0.001, 0.025
        );
        var fieldControl = (fieldColor * fieldDepth).tanh;
        var momentumControl = (momentumColor * momentumDepth).tanh;
        var fieldAmount = fieldControl.abs;
        var momentumAmount = momentumControl.abs;
        var fundamentalResonance = Ringz.ar(
            strike, frequency.clip(1, 16000),
            decaySeconds.clip(0.03, decayMaximum)
        );
        // Field depth exposes an overtone selected by the signed local field.
        // Momentum depth exposes a shorter, brighter transient resonance.
        var fieldPartial = Ringz.ar(
            strike,
            (frequency * fieldControl.linlin(-1, 1, 2, 6))
                .clip(20, SampleRate.ir * 0.45),
            (decaySeconds * 0.55).clip(0.03, decayMaximum)
        ) * fieldAmount * 0.52;
        var momentumStrike = HPF.ar(
            strike,
            (frequency * momentumAmount.linlin(0, 1, 1.5, 8))
                .clip(20, SampleRate.ir * 0.45)
        );
        var momentumPartial = Ringz.ar(
            momentumStrike,
            (frequency * momentumControl.linlin(-1, 1, 3, 9))
                .clip(20, SampleRate.ir * 0.45),
            (decaySeconds * 0.28).clip(0.03, decayMaximum)
        ) * momentumAmount * 0.46;
        var timbreAmount = (fieldAmount + momentumAmount).clip(0, 1);
        var coloredResonance = (fundamentalResonance * 0.72)
            + fieldPartial + momentumPartial;
        var resonance = XFade2.ar(
            fundamentalResonance, coloredResonance,
            (timbreAmount * 2) - 1
        );
        var life = EnvGen.kr(
            Env.linen(
                0, decaySeconds.clip(0.03, decayMaximum) * 1.4, 0.03
            ),
            doneAction: Done.freeSelf
        );
        var voiceGain = Lag.kr(In.kr(voiceGainBus).clip(0, 2), 0.03);
        var dry = resonance * strength.clip(0, 2)
            * (0.45 + (localEnergy.clip(0, 4) * 0.08))
            * life * amp * voiceGain;
        var ringMix = Lag.kr(In.kr(ringMixBus).clip(0, 1), 0.03);
        var ringFrequency = In.kr(ringFrequencyBus).clip(
            0.1, SampleRate.ir * 0.45
        );
        // sqrt(2) approximately loudness-compensates bipolar multiplication.
        var ringed = dry * SinOsc.ar(ringFrequency) * 2.sqrt;
        var ringOutput = XFade2.ar(dry, ringed, (ringMix * 2) - 1);
        var wavefoldMix = Lag.kr(
            In.kr(wavefoldMixBus).clip(0, 1), 0.03
        );
        var wavefoldDrive = Lag.kr(
            In.kr(wavefoldDriveBus).clip(1, 32), 0.03
        );
        var warpAmount = Lag.kr(In.kr(wavefoldWarpAmountBus).clip(0, 1), 0.03);
        var warpShape = In.kr(wavefoldWarpShapeBus).clip(0, 3).round;
        var bentPositive = ringOutput + (ringOutput.squared * 0.8);
        var bentNegative = ringOutput - (ringOutput.squared * 0.8);
        var sineWarp = (ringOutput * (pi * 0.5)).sin;
        var foldedWarp = (ringOutput * 2.5).fold(-1, 1);
        var warped = Select.ar(warpShape, [
            bentPositive, bentNegative, sineWarp, foldedWarp
        ]);
        // Warp is an exact bypass at zero. It changes the fold input shape,
        // while drive independently controls how densely that input is folded.
        var warpOutput = XFade2.ar(ringOutput, warped, (warpAmount * 2) - 1);
        // Pulse-only nonlinear chain: ring -> warp -> wavefolder -> fuzz.
        var folded = LeakDC.ar(
            (warpOutput * wavefoldDrive).fold(-1, 1)
        ) / wavefoldDrive.sqrt;
        var wavefoldOutput = XFade2.ar(
            ringOutput, folded, (wavefoldMix * 2) - 1
        );
        var fuzzMix = Lag.kr(In.kr(fuzzMixBus).clip(0, 1), 0.03);
        var fuzzDrive = Lag.kr(In.kr(fuzzDriveBus).clip(0.25, 12), 0.03);
        var fuzzSecond = Lag.kr(In.kr(fuzzSecondBus).clip(0, 2), 0.03);
        var fuzzThird = Lag.kr(In.kr(fuzzThirdBus).clip(0, 2), 0.03);
        var fuzzHigher = Lag.kr(In.kr(fuzzHigherBus).clip(0, 2), 0.03);
        var fuzzBias = Lag.kr(In.kr(fuzzBiasBus).clip(-0.75, 0.75), 0.03);
        var fuzzTone = Lag.kr(In.kr(fuzzToneBus).clip(0, 1), 0.03);
        // Big Muff-inspired topology: polynomial coloration provides explicit
        // 2nd/3rd/5th/7th-order content, then four coupling-capacitor-like
        // gain stages sustain and thicken it before the passive-style tone
        // stack. This is an audio adapter only, not quantum evolution.
        var fuzzInput = (HPF.ar(wavefoldOutput, 30) + fuzzBias).clip(-1, 1);
        var fuzzColor = fuzzInput + (fuzzInput.squared * fuzzSecond)
            + (fuzzInput.cubed * fuzzThird)
            + (fuzzInput.pow(5) * fuzzHigher * 0.55)
            + (fuzzInput.pow(7) * fuzzHigher * 0.24);
        var muffStage1 = (fuzzColor * (1.8 + fuzzDrive)).tanh;
        var muffStage2 = (HPF.ar(muffStage1, 48) * (2.4 + fuzzDrive * 0.8)).tanh;
        var muffStage3 = (LPF.ar(muffStage2, 7200) * (2.0 + fuzzDrive * 0.55)).tanh;
        var muffStage4 = (HPF.ar(muffStage3, 38) * (1.7 + fuzzDrive * 0.42)).tanh;
        // A low branch retains the woolly body while the high branch is the
        // familiar Muff tone network. Their equal-power weights prevent the
        // midpoint from collapsing into a thin, scooped-only sound.
        var muffLow = LPF.ar(muffStage4, 520 + ((1 - fuzzTone) * 2300));
        var muffHigh = HPF.ar(muffStage4, 420 + (fuzzTone * 2500));
        var muffBody = LPF.ar(muffStage4, 420) * 0.42;
        var muffToneStack = (muffLow * (1 - fuzzTone).sqrt)
            + (muffHigh * fuzzTone.sqrt) + muffBody;
        var fuzzed = LeakDC.ar(
            (muffToneStack * (1.25 + (fuzzDrive * 0.16))).tanh
        ) * 1.18;
        var emitted = XFade2.ar(wavefoldOutput, fuzzed, (fuzzMix * 2) - 1);
        var fxSend = Lag.kr(In.kr(fxSendControlBus).clip(0, 1), 0.03)
            * fxEnabled.clip(0, 1);
        Out.ar(
            out + lane,
            emitted
        );
        Out.ar(
            fxSendBus,
            Pan2.ar(emitted, (((lane % 2) * 2) - 1) * 0.8) * fxSend
        );
    }).add;

    // Gaussian adaptation of qmw_qubit_resonator.gendsp. The oscillator and
    // nonlinear basis topology is preserved, but x/y/z are explicitly local
    // Gaussian controls rather than Bloch coordinates.
    SynthDef(\qmwGaussianGenExprPulseV3, {
        |out=0, x=0, y=0, z=0, purity=1, entropy=0, coherence=0,
        baseFreq=72, strength=0.2, decaySeconds=0.28, lane=0, amp=0.12,
        fieldDepth=1, momentumDepth=0.45,
        voiceGain=1, voiceGainBus=0, ringMixBus=0, ringFrequencyBus=0,
        wavefoldMixBus=0, wavefoldDriveBus=0, wavefoldWarpAmountBus=0,
        wavefoldWarpShapeBus=0, fuzzMixBus=0, fuzzDriveBus=0,
        fuzzSecondBus=0, fuzzThirdBus=0, fuzzHigherBus=0, fuzzBiasBus=0,
        fuzzToneBus=0, fxSendBus=0, fxSendControlBus=0, fxEnabled=0|
        var sonicX = (x * fieldDepth).clip(-1, 1);
        var sonicY = (y * momentumDepth).clip(-1, 1);
        var radius = (
            sonicX.squared + sonicY.squared + z.squared
        ).sqrt.clip(0, 1);
        var shape = purity.clip(0, 1).linlin(0, 1, 0.65, 1.45);
        var tilt = (
            0.90 - (0.75 * coherence.clip(0, 1))
            + (0.25 * entropy.clip(0, 1))
        ).clip(0.05, 1);
        var basis = [
            sonicX, sonicY, z,
            2 * sonicX * sonicY, 2 * sonicY * z, 2 * z * sonicX,
            sonicX.squared - sonicY.squared,
            0.5 * ((3 * z.squared) - radius.squared)
        ];
        var harmonics = (1..8);
        var amplitudes = (basis.abs + 0.0001).pow(shape);
        var phaseMotion = sonicY * harmonics * 0.35 * pi;
        var phases = ((basis < 0) * pi) + phaseMotion;
        var spectralColor = 1 + (
            ((harmonics - 1) / 7)
            * ((sonicX.abs * 1.4) + (sonicY.abs * 1.1))
        );
        var partials = SinOsc.ar(
            (baseFreq * harmonics).clip(1, SampleRate.ir * 0.45), phases
        ) * amplitudes * spectralColor / harmonics.pow(tilt);
        var envelope = EnvGen.kr(
            Env.perc(
                0.002, decaySeconds.clip(0.03, decayMaximum), 1, -4
            ),
            doneAction: Done.freeSelf
        );
        var mixerGain = Lag.kr(In.kr(voiceGainBus).clip(0, 2), 0.03);
        var mono = (Mix(partials) * 0.42).tanh
            * (0.35 + (0.65 * radius))
            / (1 + (sonicX.abs * 0.35) + (sonicY.abs * 0.28))
            * strength.clip(0, 2) * amp * voiceGain * mixerGain * envelope;
        var ringMix = Lag.kr(In.kr(ringMixBus).clip(0, 1), 0.03);
        var ringFrequency = In.kr(ringFrequencyBus).clip(
            0.1, SampleRate.ir * 0.45
        );
        var ringed = mono * SinOsc.ar(ringFrequency) * 2.sqrt;
        var ringOutput = XFade2.ar(mono, ringed, (ringMix * 2) - 1);
        var wavefoldMix = Lag.kr(
            In.kr(wavefoldMixBus).clip(0, 1), 0.03
        );
        var wavefoldDrive = Lag.kr(
            In.kr(wavefoldDriveBus).clip(1, 32), 0.03
        );
        var warpAmount = Lag.kr(In.kr(wavefoldWarpAmountBus).clip(0, 1), 0.03);
        var warpShape = In.kr(wavefoldWarpShapeBus).clip(0, 3).round;
        var warped = Select.ar(warpShape, [
            ringOutput + (ringOutput.squared * 0.8),
            ringOutput - (ringOutput.squared * 0.8),
            (ringOutput * (pi * 0.5)).sin,
            (ringOutput * 2.5).fold(-1, 1)
        ]);
        var warpOutput = XFade2.ar(ringOutput, warped, (warpAmount * 2) - 1);
        var folded = LeakDC.ar(
            (warpOutput * wavefoldDrive).fold(-1, 1)
        ) / wavefoldDrive.sqrt;
        var wavefoldOutput = XFade2.ar(
            ringOutput, folded, (wavefoldMix * 2) - 1
        );
        var fuzzMix = Lag.kr(In.kr(fuzzMixBus).clip(0, 1), 0.03);
        var fuzzDrive = Lag.kr(In.kr(fuzzDriveBus).clip(0.25, 12), 0.03);
        var fuzzSecond = Lag.kr(In.kr(fuzzSecondBus).clip(0, 2), 0.03);
        var fuzzThird = Lag.kr(In.kr(fuzzThirdBus).clip(0, 2), 0.03);
        var fuzzHigher = Lag.kr(In.kr(fuzzHigherBus).clip(0, 2), 0.03);
        var fuzzBias = Lag.kr(In.kr(fuzzBiasBus).clip(-0.75, 0.75), 0.03);
        var fuzzTone = Lag.kr(In.kr(fuzzToneBus).clip(0, 1), 0.03);
        var fuzzInput = (HPF.ar(wavefoldOutput, 30) + fuzzBias).clip(-1, 1);
        var fuzzColor = fuzzInput + (fuzzInput.squared * fuzzSecond)
            + (fuzzInput.cubed * fuzzThird)
            + (fuzzInput.pow(5) * fuzzHigher * 0.55)
            + (fuzzInput.pow(7) * fuzzHigher * 0.24);
        var muffStage1 = (fuzzColor * (1.8 + fuzzDrive)).tanh;
        var muffStage2 = (HPF.ar(muffStage1, 48) * (2.4 + fuzzDrive * 0.8)).tanh;
        var muffStage3 = (LPF.ar(muffStage2, 7200) * (2.0 + fuzzDrive * 0.55)).tanh;
        var muffStage4 = (HPF.ar(muffStage3, 38) * (1.7 + fuzzDrive * 0.42)).tanh;
        var muffLow = LPF.ar(muffStage4, 520 + ((1 - fuzzTone) * 2300));
        var muffHigh = HPF.ar(muffStage4, 420 + (fuzzTone * 2500));
        var muffBody = LPF.ar(muffStage4, 420) * 0.42;
        var muffToneStack = (muffLow * (1 - fuzzTone).sqrt)
            + (muffHigh * fuzzTone.sqrt) + muffBody;
        var fuzzed = LeakDC.ar(
            (muffToneStack * (1.25 + (fuzzDrive * 0.16))).tanh
        ) * 1.18;
        var emitted = XFade2.ar(wavefoldOutput, fuzzed, (fuzzMix * 2) - 1);
        var fxSend = Lag.kr(In.kr(fxSendControlBus).clip(0, 1), 0.03)
            * fxEnabled.clip(0, 1);
        Out.ar(
            out + lane,
            emitted
        );
        Out.ar(
            fxSendBus,
            Pan2.ar(emitted, (((lane % 2) * 2) - 1) * 0.8) * fxSend
        );
    }).add;

    // QHO-FM is a downstream pulse voice, not a new Hamiltonian. The carrier
    // follows the selected oscillator/site pitch; its modulator is locked to
    // a selected overtone and its bounded index includes local descriptors.
    SynthDef(\qmwQHOFieldFMPulseV3, {
        |out=0, x=0, y=0, z=0, purity=1, entropy=0, coherence=0,
        baseFreq=72, strength=0.2, decaySeconds=0.28, lane=0, amp=0.12,
        fmRatio=2, fmIndex=0.5, fmQuantumDepth=2,
        fieldDepth=1, momentumDepth=0.45,
        voiceGainBus=0,
        ringMixBus=0, ringFrequencyBus=0,
        wavefoldMixBus=0, wavefoldDriveBus=0, wavefoldWarpAmountBus=0,
        wavefoldWarpShapeBus=0, fuzzMixBus=0, fuzzDriveBus=0,
        fuzzSecondBus=0, fuzzThirdBus=0, fuzzHigherBus=0, fuzzBiasBus=0,
        fuzzToneBus=0, fxSendBus=0, fxSendControlBus=0, fxEnabled=0|
        var sonicX = (x * fieldDepth).clip(-1, 1);
        var sonicY = (y * momentumDepth).clip(-1, 1);
        var radius = (
            sonicX.squared + sonicY.squared + z.squared
        ).sqrt.clip(0, 1);
        var descriptorPhase = sonicY.atan2(sonicX);
        var stateContribution = (
            (sonicX.abs * 0.38)
            + (sonicY.abs * 0.38)
            + (z.abs * 0.08)
            + (coherence.clip(0, 1) * 0.08)
            + ((1 - purity.clip(0, 1)) * 0.04)
            + (entropy.clip(0, 1) * 0.04)
        ).clip(0, 1);
        var effectiveIndex = (
            fmIndex.clip(0, 12)
            + (fmQuantumDepth.clip(0, 8) * stateContribution)
        ).clip(0, 16);
        var modulator = SinOsc.ar(
            (baseFreq * fmRatio.clip(1, siteCount))
                .clip(1, SampleRate.ir * 0.45),
            descriptorPhase,
            effectiveIndex
        );
        var carrier = SinOsc.ar(
            baseFreq.clip(1, SampleRate.ir * 0.45),
            descriptorPhase + modulator
        );
        var envelope = EnvGen.kr(
            Env.perc(
                0.002, decaySeconds.clip(0.03, decayMaximum), 1, -4
            ),
            doneAction: Done.freeSelf
        );
        var mixerGain = Lag.kr(In.kr(voiceGainBus).clip(0, 2), 0.03);
        var dry = carrier
            * (0.30 + (0.70 * radius))
            * strength.clip(0, 2) * amp * mixerGain * envelope;
        var ringMix = Lag.kr(In.kr(ringMixBus).clip(0, 1), 0.03);
        var ringFrequency = In.kr(ringFrequencyBus).clip(
            0.1, SampleRate.ir * 0.45
        );
        var ringed = dry * SinOsc.ar(ringFrequency) * 2.sqrt;
        var ringOutput = XFade2.ar(dry, ringed, (ringMix * 2) - 1);
        var wavefoldMix = Lag.kr(
            In.kr(wavefoldMixBus).clip(0, 1), 0.03
        );
        var wavefoldDrive = Lag.kr(
            In.kr(wavefoldDriveBus).clip(1, 32), 0.03
        );
        var warpAmount = Lag.kr(In.kr(wavefoldWarpAmountBus).clip(0, 1), 0.03);
        var warpShape = In.kr(wavefoldWarpShapeBus).clip(0, 3).round;
        var warped = Select.ar(warpShape, [
            ringOutput + (ringOutput.squared * 0.8),
            ringOutput - (ringOutput.squared * 0.8),
            (ringOutput * (pi * 0.5)).sin,
            (ringOutput * 2.5).fold(-1, 1)
        ]);
        var warpOutput = XFade2.ar(ringOutput, warped, (warpAmount * 2) - 1);
        var folded = LeakDC.ar(
            (warpOutput * wavefoldDrive).fold(-1, 1)
        ) / wavefoldDrive.sqrt;
        var wavefoldOutput = XFade2.ar(
            ringOutput, folded, (wavefoldMix * 2) - 1
        );
        var fuzzMix = Lag.kr(In.kr(fuzzMixBus).clip(0, 1), 0.03);
        var fuzzDrive = Lag.kr(In.kr(fuzzDriveBus).clip(0.25, 12), 0.03);
        var fuzzSecond = Lag.kr(In.kr(fuzzSecondBus).clip(0, 2), 0.03);
        var fuzzThird = Lag.kr(In.kr(fuzzThirdBus).clip(0, 2), 0.03);
        var fuzzHigher = Lag.kr(In.kr(fuzzHigherBus).clip(0, 2), 0.03);
        var fuzzBias = Lag.kr(In.kr(fuzzBiasBus).clip(-0.75, 0.75), 0.03);
        var fuzzTone = Lag.kr(In.kr(fuzzToneBus).clip(0, 1), 0.03);
        var fuzzInput = (HPF.ar(wavefoldOutput, 30) + fuzzBias).clip(-1, 1);
        var fuzzColor = fuzzInput + (fuzzInput.squared * fuzzSecond)
            + (fuzzInput.cubed * fuzzThird)
            + (fuzzInput.pow(5) * fuzzHigher * 0.55)
            + (fuzzInput.pow(7) * fuzzHigher * 0.24);
        var muffStage1 = (fuzzColor * (1.8 + fuzzDrive)).tanh;
        var muffStage2 = (HPF.ar(muffStage1, 48) * (2.4 + fuzzDrive * 0.8)).tanh;
        var muffStage3 = (LPF.ar(muffStage2, 7200) * (2.0 + fuzzDrive * 0.55)).tanh;
        var muffStage4 = (HPF.ar(muffStage3, 38) * (1.7 + fuzzDrive * 0.42)).tanh;
        var muffLow = LPF.ar(muffStage4, 520 + ((1 - fuzzTone) * 2300));
        var muffHigh = HPF.ar(muffStage4, 420 + (fuzzTone * 2500));
        var muffBody = LPF.ar(muffStage4, 420) * 0.42;
        var muffToneStack = (muffLow * (1 - fuzzTone).sqrt)
            + (muffHigh * fuzzTone.sqrt) + muffBody;
        var fuzzed = LeakDC.ar(
            (muffToneStack * (1.25 + (fuzzDrive * 0.16))).tanh
        ) * 1.18;
        var emitted = XFade2.ar(wavefoldOutput, fuzzed, (fuzzMix * 2) - 1);
        var fxSend = Lag.kr(In.kr(fxSendControlBus).clip(0, 1), 0.03)
            * fxEnabled.clip(0, 1);
        Out.ar(
            out + lane,
            emitted
        );
        Out.ar(
            fxSendBus,
            Pan2.ar(emitted, (((lane % 2) * 2) - 1) * 0.8) * fxSend
        );
    }).add;

    // Thirty-two retriggerable resonator slots in one persistent server node.
    // This avoids allocating/freeing a Synth for every event. Slot controls
    // are updated atomically by ~qmwQFTV3RenderPooledPulse below.
    SynthDef(\qmwQFTV3PooledPulseBank, { |out=0|
        var triggers = NamedControl.kr(\triggers, Array.fill(pooledSlotCount, 0));
        var frequencies = NamedControl.kr(\frequencies, Array.fill(pooledSlotCount, 220));
        var strengths = NamedControl.kr(\strengths, Array.fill(pooledSlotCount, 0));
        var fields = NamedControl.kr(\fields, Array.fill(pooledSlotCount, 0));
        var momenta = NamedControl.kr(\momenta, Array.fill(pooledSlotCount, 0));
        var energies = NamedControl.kr(\energies, Array.fill(pooledSlotCount, 0));
        var decays = NamedControl.kr(\decays, Array.fill(pooledSlotCount, 0.28));
        var amplitudes = NamedControl.kr(\amplitudes, Array.fill(pooledSlotCount, 0));
        var lanes = NamedControl.kr(\lanes, Array.fill(pooledSlotCount, 0));
        pooledSlotCount.do { |slot|
            var trigger = Changed.kr(triggers[slot]);
            var frequency = frequencies[slot].clip(1, 16000);
            var decay = decays[slot].clip(0.03, decayMaximum);
            var field = fields[slot].tanh;
            var momentum = momenta[slot].tanh;
            var strike = PinkNoise.ar(0.24)
                * Decay2.ar(K2A.ar(trigger), 0.001, 0.025);
            var fundamental = Ringz.ar(strike, frequency, decay);
            var fieldPartial = Ringz.ar(
                strike,
                (frequency * field.linlin(-1, 1, 2, 6)).clip(20, SampleRate.ir * 0.45),
                (decay * 0.55).clip(0.03, decayMaximum)
            ) * field.abs * 0.52;
            var momentumPartial = Ringz.ar(
                HPF.ar(strike, (frequency * momentum.abs.linlin(0, 1, 1.5, 8)).clip(20, SampleRate.ir * 0.45)),
                (frequency * momentum.linlin(-1, 1, 3, 9)).clip(20, SampleRate.ir * 0.45),
                (decay * 0.28).clip(0.03, decayMaximum)
            ) * momentum.abs * 0.46;
            var envelope = EnvGen.kr(
                Env.linen(0, decay * 1.4, 0.03), trigger
            );
            var signal = (fundamental * 0.72 + fieldPartial + momentumPartial)
                * strengths[slot].clip(0, 1.5)
                * (0.45 + (energies[slot].clip(0, 4) * 0.08))
                * amplitudes[slot].clip(0, 1.5) * envelope;
            Out.ar(out + lanes[slot].round.clip(0, siteCount - 1), signal);
        };
    }).add;

    // Pooled slots are clean resonators; ring, fold, and Muff-style fuzz are
    // applied once after their stereo sum instead of once per active slot.
    SynthDef(\qmwQFTV3PooledPulseMixer, {
        |inBus=0, out=0, ringMixBus=0, ringFrequencyBus=0,
        foldMixBus=0, foldDriveBus=0, fuzzMixBus=0, fuzzDriveBus=0,
        fuzzThirdBus=0, fuzzHigherBus=0, oddEvenWidth=1, pulseLevel=1,
        fxSendBus=0, fxSendControlBus=0, fxEnabled=0|
        var lanes = In.ar(inBus, siteCount);
        var levels = Amplitude.kr(lanes, 0.01, 0.18).clip(0, 1);
        var stereoWidth = VarLag.kr(oddEvenWidth.clip(0, 1), 0.05);
        var dry = Mix.fill(siteCount, { |site|
            // site 0 -> harmonic 1 (odd/left), site 1 -> harmonic 2
            // (even/right), alternating through the complete lattice.
            Pan2.ar(
                lanes[site],
                (((site % 2) * 2) - 1) * stereoWidth
            )
        });
        var ringMix = Lag.kr(In.kr(ringMixBus).clip(0, 1), 0.03);
        var ringFrequency = In.kr(ringFrequencyBus).clip(0.1, SampleRate.ir * 0.45);
        var ringed = dry * SinOsc.ar(ringFrequency) * 2.sqrt;
        var ringOutput = XFade2.ar(dry, ringed, (ringMix * 2) - 1);
        var foldMix = Lag.kr(In.kr(foldMixBus).clip(0, 1), 0.03);
        var foldDrive = Lag.kr(In.kr(foldDriveBus).clip(1, 32), 0.03);
        var folded = LeakDC.ar((ringOutput * foldDrive).fold(-1, 1)) / foldDrive.sqrt;
        var foldOutput = XFade2.ar(ringOutput, folded, (foldMix * 2) - 1);
        var fuzzMix = Lag.kr(In.kr(fuzzMixBus).clip(0, 1), 0.03);
        var fuzzDrive = Lag.kr(In.kr(fuzzDriveBus).clip(0.25, 12), 0.03);
        var fuzzThird = Lag.kr(In.kr(fuzzThirdBus).clip(0, 2), 0.03);
        var fuzzHigher = Lag.kr(In.kr(fuzzHigherBus).clip(0, 2), 0.03);
        var fuzzColor = foldOutput + (foldOutput.cubed * fuzzThird)
            + (foldOutput.pow(5) * fuzzHigher * 0.55)
            + (foldOutput.pow(7) * fuzzHigher * 0.24);
        var muff = (LPF.ar((fuzzColor * (1.8 + fuzzDrive)).tanh, 6200)
            * (2.1 + fuzzDrive * 0.55)).tanh;
        var fuzzed = LeakDC.ar((muff * (1.25 + fuzzDrive * 0.16)).tanh) * 1.18;
        var emitted = XFade2.ar(foldOutput, fuzzed, (fuzzMix * 2) - 1)
            * VarLag.kr(pulseLevel.clip(0, 1), 0.05);
        var fxSend = Lag.kr(In.kr(fxSendControlBus).clip(0, 1), 0.03)
            * fxEnabled.clip(0, 1);
        SendReply.kr(Impulse.kr(15), oscRoot ++ "/pulse/meters", levels);
        Out.ar(out, emitted);
        Out.ar(fxSendBus, emitted * fxSend);
    }).add;

    // Pulse voices retain their site identity through this dedicated lane bus.
    // Meter values are measured post ring/wavefolder/fuzz and post site trim,
    // immediately
    // before the fixed-site stereo field is constructed.
    SynthDef(\qmwQFTV3PulseLaneMixer, {
        |inBus=0, out=0, oddEvenWidth=1, pulseLevel=1|
        var lanes = In.ar(inBus, siteCount);
        var levels = Amplitude.kr(lanes, 0.01, 0.18).clip(0, 1);
        var stereoWidth = VarLag.kr(oddEvenWidth.clip(0, 1), 0.05);
        var stereo = Mix.fill(siteCount, { |site|
            Pan2.ar(
                lanes[site],
                (((site % 2) * 2) - 1) * stereoWidth
            )
        });
        SendReply.kr(
            Impulse.kr(15), oscRoot ++ "/pulse/meters", levels
        );
        // Per-event gain already carries the established site-count
        // compensation. Pan2 preserves equal-power loudness from mono through
        // full odd-left/even-right separation.
        Out.ar(out, stereo * VarLag.kr(pulseLevel.clip(0, 1), 0.05));
    }).add;

    SynthDef(\qmwQFTV3DryOutput, {
        |inBus=0, out=0, level=1, fadeTime=0.05|
        var signal = In.ar(inBus, 2);
        Out.ar(out, Limiter.ar(
            signal * VarLag.kr(level.clip(0, 1), fadeTime), 0.94, 0.01
        ));
    }).add;

    s.sync;
    ~qmwQFTV3RingModMixBus = Bus.control(s, 1);
    ~qmwQFTV3RingModFrequencyBus = Bus.control(s, 1);
    ~qmwQFTV3WavefoldMixBus = Bus.control(s, 1);
    ~qmwQFTV3WavefoldDriveBus = Bus.control(s, 1);
    ~qmwQFTV3WavefoldWarpAmountBus = Bus.control(s, 1);
    ~qmwQFTV3WavefoldWarpShapeBus = Bus.control(s, 1);
    ~qmwQFTV3FuzzMixBus = Bus.control(s, 1);
    ~qmwQFTV3FuzzDriveBus = Bus.control(s, 1);
    ~qmwQFTV3FuzzSecondBus = Bus.control(s, 1);
    ~qmwQFTV3FuzzThirdBus = Bus.control(s, 1);
    ~qmwQFTV3FuzzHigherBus = Bus.control(s, 1);
    ~qmwQFTV3FuzzBiasBus = Bus.control(s, 1);
    ~qmwQFTV3FuzzToneBus = Bus.control(s, 1);
    ~qmwQFTV3VoiceGainBus = Bus.control(s, voiceCount);
    if(fxEnabled, {
        ~qmwQFTV42BFXSendBus = Bus.audio(s, 2);
        ~qmwQFTV42BFXSendControlBus = Bus.control(s, 7);
        fxSendBusIndex = ~qmwQFTV42BFXSendBus.index;
        fxSendControlBase = ~qmwQFTV42BFXSendControlBus.index;
        ~qmwQFTV42BUpdateFXSends.();
    });
    ~qmwQFTV3UpdateRingMod.();
    ~qmwQFTV3UpdateWavefold.();
    ~qmwQFTV3UpdateFuzz.();
    ~qmwQFTV3UpdateVoiceMixer.();
    ~qmwQFTV3SourceBus = Bus.audio(s, 2);
    ~qmwQFTV3FieldBus = if(splitFieldOutput, {
        Bus.audio(s, 2)
    }, {
        ~qmwQFTV3SourceBus
    });
    ~qmwQFTV3PulseBus = Bus.audio(s, siteCount);
    ~qmwQFTV3UpdatePitchRatios.();
    ~qmwQFTV3ApplyEnergyDecay.();
    // Make graph creation explicitly transactional at the server boundary.
    // The former s.bind form could allocate client-side Node IDs before the
    // group/synth creation bundle had been acknowledged, leaving the live OSC
    // path to address nodes that had never reached scsynth.
    ~qmwQFTV3SourceGroup = Group.head(s);
    ~qmwQFTV3FXGroup = Group.after(~qmwQFTV3SourceGroup);
    s.sync;
    ~qmwQFTV3Synth = Synth.head(
        ~qmwQFTV3SourceGroup,
        \qmwScalarFieldInstrumentV3,
        [
            \out, ~qmwQFTV3FieldBus,
            \fundamental, ~qmwQFTV3Fundamental,
            \vacuumMix, ~qmwQFTV3VacuumMix,
            \decaySeconds, ~qmwQFTV3EffectiveDecaySeconds,
            \fieldLevel, if(~qmwQFTV3RendererMode == 1, {
                0.0
            }, { ~qmwQFTV3FieldMix }),
            \oddEvenWidth, ~qmwQFTV3OddEvenStereoWidth,
            \masterAmp, ~qmwQFTV3MasterAmp,
            \soundEnabled, ~qmwQFTV3SoundEnabled,
            \fxSendBus, fxSendBusIndex,
            \fxSendControlBus, fxSendControlBase + 5,
            \fxEnabled, fxEnabled.asInteger
        ]
    );
    ~qmwQFTV3PulseMixerSynth = Synth.head(
        ~qmwQFTV3FXGroup,
        \qmwQFTV3PulseLaneMixer,
        [
            \inBus, ~qmwQFTV3PulseBus, \out, ~qmwQFTV3SourceBus,
            \oddEvenWidth, ~qmwQFTV3OddEvenStereoWidth,
            \pulseLevel, if(~qmwQFTV3RendererMode == 0, { 0.0 }, { 1.0 })
        ]
    );
    ~qmwQFTV3DrySynth = Synth.tail(
        ~qmwQFTV3FXGroup,
        \qmwQFTV3DryOutput,
        [\inBus, ~qmwQFTV3SourceBus, \out, 0]
    );
    ~qmwQFTV3FieldDrySynth = if(splitFieldOutput, {
        Synth.tail(
            ~qmwQFTV3FXGroup,
            \qmwQFTV3DryOutput,
            [\inBus, ~qmwQFTV3FieldBus, \out, 2]
        )
    }, { nil });
    s.sync;
    ~qmwQFTV3Synth.setn(\occupations, ~qmwQFTV3Occupations);
    ~qmwQFTV3Synth.setn(\frequencies, ~qmwQFTV3Frequencies);
    ~qmwQFTV3Synth.setn(\sitePitchRatios, ~qmwQFTV3SitePitchRatios);
    ~qmwQFTV3Synth.setn(
        \fieldLaneGains, ~qmwQFTV3EffectiveFieldLaneGains.()
    );
    // Do not advertise audio readiness until the groups, buses, synth nodes,
    // and their initial array controls are acknowledged by scsynth. Live OSC
    // can already be arriving while this boot callback runs.
    s.sync;
    ~qmwQFTV3UpdateSiteAudioGains.();
    ~qmwQFTV3AudioReady = true;
    {
        audioStatus !? { |view| view.string_(
            if(splitFieldOutput, {
                "active: % — % channels; V% split: plucks 1–2, field 3–4"
            }, {
                "active: % — % channels; V% stereo on outputs 1–2"
            }).format(
                ~qmwQFTV3SelectedOutputDevice ? "system default",
                ~qmwQFTV3OutputChannels,
                instrumentVersion
            )
        ) };
    }.defer;
};

// Keep the established renderers completely unchanged at boot: the pooled
// graph is built only when its menu mode is selected. That means 32 resonator
// slots never consume server DSP while simple/Gaussian/FM rendering is used.
~qmwQFTV3EnsurePooledRenderer = {
    if(~qmwQFTV3AudioReady and: { ~qmwQFTV3PooledBankSynth.isNil }, {
        ~qmwQFTV3PooledPulseBus = Bus.audio(s, siteCount);
        ~qmwQFTV3PooledBankSynth = Synth.tail(
            ~qmwQFTV3SourceGroup,
            \qmwQFTV3PooledPulseBank,
            [\out, ~qmwQFTV3PooledPulseBus]
        );
        ~qmwQFTV3PooledMixerSynth = Synth.before(
            ~qmwQFTV3DrySynth,
            \qmwQFTV3PooledPulseMixer,
            [
                \inBus, ~qmwQFTV3PooledPulseBus, \out, ~qmwQFTV3SourceBus,
                \ringMixBus, ~qmwQFTV3RingModMixBus,
                \ringFrequencyBus, ~qmwQFTV3RingModFrequencyBus,
                \foldMixBus, ~qmwQFTV3WavefoldMixBus,
                \foldDriveBus, ~qmwQFTV3WavefoldDriveBus,
                \fuzzMixBus, ~qmwQFTV3FuzzMixBus,
                \fuzzDriveBus, ~qmwQFTV3FuzzDriveBus,
                \fuzzThirdBus, ~qmwQFTV3FuzzThirdBus,
                \fuzzHigherBus, ~qmwQFTV3FuzzHigherBus,
                \oddEvenWidth, ~qmwQFTV3OddEvenStereoWidth,
                \pulseLevel, if(~qmwQFTV3RendererMode == 0, { 0.0 }, { 1.0 }),
                \fxSendBus, if(~qmwQFTV42BFXSendBus.notNil, {
                    ~qmwQFTV42BFXSendBus.index
                }, { 0 }),
                \fxSendControlBus, if(~qmwQFTV42BFXSendControlBus.notNil, {
                    ~qmwQFTV42BFXSendControlBus.index
                }, { 0 }),
                \fxEnabled, (~qmwQFTV42BFXEnabled ? false).asInteger
            ]
        );
        s.sync;
        ~qmwQFTV3PooledBankSynth.setn(\triggers, ~qmwQFTV3PooledSlotTokens);
        ~qmwQFTV3PooledBankSynth.setn(\frequencies, ~qmwQFTV3PooledFrequency);
        ~qmwQFTV3PooledBankSynth.setn(\strengths, ~qmwQFTV3PooledStrength);
        ~qmwQFTV3PooledBankSynth.setn(\fields, ~qmwQFTV3PooledField);
        ~qmwQFTV3PooledBankSynth.setn(\momenta, ~qmwQFTV3PooledMomentum);
        ~qmwQFTV3PooledBankSynth.setn(\energies, ~qmwQFTV3PooledEnergy);
        ~qmwQFTV3PooledBankSynth.setn(\decays, ~qmwQFTV3PooledDecay);
        ~qmwQFTV3PooledBankSynth.setn(\amplitudes, ~qmwQFTV3PooledAmplitude);
        ~qmwQFTV3PooledBankSynth.setn(\lanes, ~qmwQFTV3PooledLane);
        s.sync;
    });
};

// A server quit invalidates every Node, Group, and Bus object held by sclang.
// Mark the adapter unavailable immediately so incoming temporal events cannot
// address stale group IDs while the audio server is down or rebooting.
~qmwQFTV3ServerQuitHandler !? { |handler| s.onQuitRemove(handler) };
~qmwQFTV3ServerQuitHandler = {
    ~qmwQFTV3AudioReady = false;
    ~qmwQFTV3RecordingReady = false;
    ~qmwQFTV3ActivePulseVoices.clear;
    ~qmwQFTV3Synth = nil;
    ~qmwQFTV3PulseMixerSynth = nil;
    ~qmwQFTV3PooledBankSynth = nil;
    ~qmwQFTV3PooledMixerSynth = nil;
    ~qmwQFTV3DrySynth = nil;
    ~qmwQFTV3FieldDrySynth = nil;
    ~qmwQFTV3SourceGroup = nil;
    ~qmwQFTV3FXGroup = nil;
    ~qmwQFTV3SourceBus = nil;
    ~qmwQFTV3FieldBus = nil;
    ~qmwQFTV3PulseBus = nil;
    ~qmwQFTV3PooledPulseBus = nil;
    ~qmwQFTV3RingModMixBus = nil;
    ~qmwQFTV3RingModFrequencyBus = nil;
    ~qmwQFTV3WavefoldMixBus = nil;
    ~qmwQFTV3WavefoldDriveBus = nil;
    ~qmwQFTV3FuzzMixBus = nil;
    ~qmwQFTV3VoiceGainBus = nil;
    ~qmwQFTV42BFXSendControlBus = nil;
    ~qmwQFTV42BFXSendBus = nil;
    {
        audioStatus !? { |view| view.string_(
            "audio server stopped — apply/reboot audio or relaunch V4"
        ).stringColor_(Color.yellow(0.82)) };
    }.defer;
};
s.onQuitAdd(~qmwQFTV3ServerQuitHandler);

~qmwQFTV3ApplyAudioOutput = { |device, outputChannels=2|
    var configureAndReload, selectedDevice;
    outputChannels = outputChannels.asInteger.clip(
        if(splitFieldOutput, { 4 }, { 2 }), 8
    );
    if(s.isRecording, {
        {
            audioStatus !? { |view| view.string_(
                "stop the current recording before changing audio devices"
            ) };
        }.defer;
    }, {
        selectedDevice = if(device == \qmwQFTV3AbletonLiveBridge, {
            resolveAbletonBridgeDevice.()
        }, {
            device
        });
        if(selectedDevice.isNil and: { device == \qmwQFTV3AbletonLiveBridge }, {
            {
                audioStatus !? { |view| view.string_(
                    "Ableton Live bridge needs BlackHole, Loopback, VB-Cable, or Soundflower"
                ).stringColor_(Color.yellow(0.82)) };
            }.defer;
        }, {
            ~qmwQFTV3AudioReady = false;
            configureAndReload = {
                s.options.outDevice = selectedDevice;
                s.options.numOutputBusChannels = outputChannels;
                s.options.blockSize = ~qmwQFTV3TimingBlockSize;
                ~qmwQFTV3SelectedOutputDevice = selectedDevice;
                ~qmwQFTV3OutputChannels = outputChannels;
                ~qmwQFTV3ActivePulseVoices.clear;
                s.doWhenBooted({ ~qmwQFTV3BuildAudio.() });
            };
            {
                audioStatus !? { |view| view.string_(
                    "restarting SuperCollider audio on %..."
                    .format(selectedDevice ? "system default")
                ) };
            }.defer;
            if(s.serverRunning, {
                s.reboot(configureAndReload, {
                    {
                        audioStatus !? { |view| view.string_(
                            "audio restart failed; inspect the SuperCollider post window"
                        ) };
                    }.defer;
                });
            }, {
                configureAndReload.();
                s.boot;
            });
        });
    });
};

s.waitForBoot { ~qmwQFTV3BuildAudio.() };

OSCdef(\qmwQFTV3Begin, { |msg|
    ~qmwQFTV3Revision = msg[1].asInteger;
    ~qmwQFTV3Time = msg[2].asFloat;
    ~qmwQFTV3StageValid = true;
}, oscRoot ++ "/frame/begin", recvPort: dataPort);

[
    [\qmwQFTV3Phi, oscRoot ++ "/phi", \phi],
    [\qmwQFTV3Pi, oscRoot ++ "/pi", \momentum],
    [\qmwQFTV3Energy, oscRoot ++ "/energy", nil],
    [\qmwQFTV3Occupations, oscRoot ++ "/occupations", \occupations],
    [\qmwQFTV3Frequencies, oscRoot ++ "/frequencies", \frequencies]
].do { |definition|
    OSCdef(definition[0], { |msg|
        if(~qmwQFTV3StageValid and: {
            msg[1].asInteger == ~qmwQFTV3Revision
        }) {
            var values = msg.copyRange(2, siteCount + 1).collect(_.asFloat);
            case
            { definition[0] == \qmwQFTV3Phi } { ~qmwQFTV3Phi = values }
            { definition[0] == \qmwQFTV3Pi } { ~qmwQFTV3Pi = values }
            { definition[0] == \qmwQFTV3Energy } { ~qmwQFTV3Energy = values }
            { definition[0] == \qmwQFTV3Occupations } {
                ~qmwQFTV3Occupations = values
            }
            { definition[0] == \qmwQFTV3Frequencies } {
                ~qmwQFTV3Frequencies = values
            };
        };
    }, definition[1], recvPort: dataPort);
};

OSCdef(\qmwQFTV3Correlation, { |msg|
    if(~qmwQFTV3StageValid and: { msg[1].asInteger == ~qmwQFTV3Revision }) {
        ~qmwQFTV3Correlation = msg.copyRange(
            2, (siteCount * siteCount) + 1
        ).collect(_.asFloat);
    };
}, oscRoot ++ "/correlation", recvPort: dataPort);

// V5 sends one covariance row per OSC message to avoid a fragmented 4 KB
// datagram at 32 sites. V3/V4 retain the original atomic matrix message.
OSCdef(\qmwQFTV3CorrelationRow, { |msg|
    if(~qmwQFTV3StageValid and: { msg[1].asInteger == ~qmwQFTV3Revision }) {
        var row = msg[2].asInteger.clip(0, siteCount - 1);
        var values = msg.copyRange(3, siteCount + 2).collect(_.asFloat);
        values.do { |value, column|
            ~qmwQFTV3Correlation[(row * siteCount) + column] = value;
        };
    };
}, oscRoot ++ "/correlation/row", recvPort: dataPort);

OSCdef(\qmwQFTV3Global, { |msg|
    if(~qmwQFTV3StageValid and: { msg[1].asInteger == ~qmwQFTV3Revision }) {
        ~qmwQFTV3Global = [msg[2].asFloat, msg[3].asFloat];
    };
}, oscRoot ++ "/global", recvPort: dataPort);

OSCdef(\qmwQFTV3Parameters, { |msg|
    if(~qmwQFTV3StageValid and: { msg[1].asInteger == ~qmwQFTV3Revision }) {
        ~qmwQFTV3Parameters = [
            msg[2].asString, msg[3].asFloat, msg[4].asFloat,
            msg[5].asInteger, msg[6].asFloat, msg[7].asInteger,
            msg[8].asFloat, msg[9].asFloat, msg[10].asFloat,
            msg[11].asFloat, msg[12].asFloat
        ];
    };
}, oscRoot ++ "/parameters", recvPort: dataPort);

OSCdef(\qmwQFTV3End, { |msg|
    if(~qmwQFTV3StageValid and: { msg[1].asInteger == ~qmwQFTV3Revision }) {
        if(~qmwQFTV3AudioReady) {
            var magnitudes = Array.fill(siteCount, { |site|
                (~qmwQFTV3Phi[site].squared + ~qmwQFTV3Pi[site].squared).sqrt
            });
            var peak = magnitudes.maxItem;
            var fieldScale = ~qmwQFTV3Phi.collect(_.abs).maxItem.max(1e-9);
            var amplitudes = if(peak > 1e-9, {
                magnitudes.collect { |value| (value / peak).sqrt }
            }, { Array.fill(siteCount, 0.0) });
            var phases = Array.fill(siteCount, { |site|
                ~qmwQFTV3Pi[site].atan2(~qmwQFTV3Phi[site])
            });
            var drives = ~qmwQFTV3Phi.collect { |value| value / fieldScale };
            ~qmwQFTV3Synth !? { |synth|
                synth.setn(\occupations, ~qmwQFTV3Occupations);
                synth.setn(\frequencies, ~qmwQFTV3Frequencies);
                synth.setn(\fieldAmplitudes, amplitudes);
                synth.setn(\fieldPhases, phases);
                synth.setn(\fieldDrives, drives);
                ~qmwQFTV3UpdatePitchRatios.();
            };
        };
        // Apply only after a complete atomic frame has supplied total energy.
        ~qmwQFTV3ApplyEnergyDecay.();
        if((~qmwQFTV3Revision % ~qmwQFTV3MeshFrameStride) == 0) {
            var uncertainty = Array.fill(siteCount, { |site|
                ~qmwQFTV3Correlation[(site * siteCount) + site].max(0).sqrt
            });
            var targetScale = Array.fill(siteCount, { |site|
                ~qmwQFTV3Phi[site].abs + uncertainty[site]
            }).maxItem.max(1e-6);
            ~qmwQFTV3MeshScale = if(~qmwQFTV3FieldHistory.isEmpty, {
                targetScale
            }, {
                // Fast enough to follow a shrinking field without pumping.
                targetScale.max(~qmwQFTV3MeshScale * 0.985)
            });
            ~qmwQFTV3FieldHistory = ~qmwQFTV3FieldHistory.add(
                ~qmwQFTV3Phi.copy
            );
            ~qmwQFTV3MomentumHistory = ~qmwQFTV3MomentumHistory.add(
                ~qmwQFTV3Pi.copy
            );
            ~qmwQFTV3EnergyHistory = ~qmwQFTV3EnergyHistory.add(
                ~qmwQFTV3Energy.copy
            );
            ~qmwQFTV3UncertaintyHistory = ~qmwQFTV3UncertaintyHistory.add(
                uncertainty
            );
            if(~qmwQFTV3FieldHistory.size > ~qmwQFTV3MeshHistoryLength) {
                var first = ~qmwQFTV3FieldHistory.size
                    - ~qmwQFTV3MeshHistoryLength;
                var last = ~qmwQFTV3FieldHistory.size - 1;
                ~qmwQFTV3FieldHistory = ~qmwQFTV3FieldHistory.copyRange(first, last);
                ~qmwQFTV3MomentumHistory = ~qmwQFTV3MomentumHistory.copyRange(first, last);
                ~qmwQFTV3EnergyHistory = ~qmwQFTV3EnergyHistory.copyRange(first, last);
                ~qmwQFTV3UncertaintyHistory = ~qmwQFTV3UncertaintyHistory.copyRange(first, last);
            };
        };
        {
            if((~qmwQFTV3Revision % ~qmwQFTV3MeshFrameStride) == 0) {
                phiView !? { |view| view.refresh };
                meshScaleStatus !? { |view| view.string_(
                    "height ±%    color %    history % frames"
                    .format(
                        ~qmwQFTV3MeshScale.round(0.001),
                        case
                        { ~qmwQFTV3MeshColorMode == 0 } { "<pi_j>" }
                        { ~qmwQFTV3MeshColorMode == 1 } { "local energy" }
                        { "local phase-space angle" },
                        ~qmwQFTV3FieldHistory.size
                    )
                ) };
            };
            // Meter, matrix, and label painting is visual telemetry, so keep it
            // on the same bounded GUI cadence as the mesh.  Audio/control state
            // above is still committed on every frame.
            if((~qmwQFTV3Revision % ~qmwQFTV3MeshFrameStride) == 0) {
                energyView !? { |view|
                    var maximum = ~qmwQFTV3Energy.maxItem.max(1e-9);
                    view.value = ~qmwQFTV3Energy.collect { |value| value / maximum };
                };
                absoluteEnergyView !? { |view| view.refresh };
                absoluteEnergyStatus !? { |view|
                    view.string_("ABS E %".format(
                        ~qmwQFTV3Global[0].round(0.0001)
                    ))
                };
                occupationView !? { |view|
                    var maximum = ~qmwQFTV3Occupations.maxItem.max(1e-9);
                    view.value = ~qmwQFTV3Occupations.collect {
                        |value| value / maximum
                    };
                };
                correlationView !? { |view| view.refresh };
                status !? { |view| view.string = (
                    "frame %    time %    total energy %    purity %"
                ).format(
                    ~qmwQFTV3Revision,
                    ~qmwQFTV3Time.round(0.001),
                    ~qmwQFTV3Global[0].round(0.0001),
                    ~qmwQFTV3Global[1].round(0.0001)
                ) };
                parameterStatus !? { |view| view.string = (
                    "state %    mass %    c %    site %    amplitude %    mode %"
                ).format(
                    ~qmwQFTV3Parameters[0],
                    ~qmwQFTV3Parameters[1].round(0.001),
                    ~qmwQFTV3Parameters[2].round(0.001),
                    ~qmwQFTV3Parameters[3],
                    ~qmwQFTV3Parameters[4].round(0.001),
                    ~qmwQFTV3Parameters[5]
                ) };
            };
        }.defer;
        ~qmwQFTV3StageValid = false;
    };
}, oscRoot ++ "/frame/end", recvPort: dataPort);

OSCdef(\qmwQFTV3TemporalGlobal, { |msg|
    ~qmwQFTV3TemporalGlobal = msg.copyRange(1, 8).collect(_.asFloat);
    ~qmwQFTV3RefreshClockStatus.();
}, oscRoot ++ "/temporal/global", recvPort: dataPort);

OSCdef(\qmwQFTV3TemporalConfig, { |msg|
    ~qmwQFTV3TemporalConfig = [
        msg[1].asInteger, msg[2].asFloat, msg[3].asFloat,
        msg[4].asFloat, msg[5].asString
    ];
    ~qmwQFTV3TemporalControlPending = "";
    ~qmwQFTV3RefreshClockStatus.();
}, oscRoot ++ "/temporal/config", recvPort: dataPort);

OSCdef(\qmwQFTV3PulseMeters, { |msg|
    ~qmwQFTV3PulseMeters = msg.copyRange(3, siteCount + 2)
        .collect { |value| value.asFloat.clip(0, 1) };
    {
        pulseMeterView !? { |view|
            view.value_(~qmwQFTV3PulseMeters)
        };
        pulseMeterStatus !? { |view|
            view.string_("post-FX peak %".format(
                ~qmwQFTV3PulseMeters.maxItem.round(0.001)
            ))
        };
    }.defer;
}, oscRoot ++ "/pulse/meters", srcID: s.addr);

OSCdef(\qmwQFTV3TemporalSite, { |msg|
    var site = msg[2].asInteger.clip(0, siteCount - 1);
    ~qmwQFTV3SitePulses[site] = msg[9].asInteger;
    ~qmwQFTV3PulseCache[site] = [
        site, msg[6].asFloat, msg[10].asFloat, msg[11].asFloat,
        msg[12].asFloat, msg[16].asFloat, msg[17].asFloat,
        msg[18].asFloat, msg[19].asFloat, msg[20].asFloat,
        msg[21].asFloat
    ];
}, oscRoot ++ "/temporal/site", recvPort: dataPort);

// The pooled renderer retains the transport/event semantics of the established
// pulse path, but reuses fixed slot controls and performs its nonlinear chain
// after summing. It is a sound adapter, not a second clock or evolution path.
~qmwQFTV3RenderPooledPulse = {
    |site, scaledIncrement, phi, momentum, localEnergy,
    x, y, z, purity, coherence, entropy|
    var descriptor = ~qmwQFTV3EffectiveDescriptor.(x, y, z);
    var deviationControl = (
        (descriptor[0] * 0.5) + (descriptor[1] * 0.3) + (descriptor[2] * 0.2)
    ).clip(-1, 1);
    var baseFrequency = (
        ~qmwQFTV3Fundamental * ~qmwQFTV3SitePitchRatios[site]
        * 2.pow((~qmwQFTV3FluctuationMix.clip(0, 1200) * deviationControl) / 1200)
    ).clip(1, 16000);
    var siteAudioGain = ~qmwQFTV3SiteGains[site].clip(0, 2)
        * (1 - ~qmwQFTV3SiteMutes[site].clip(0, 1));
    var amplitude = (~qmwQFTV3PulseMix * ~qmwQFTV3MasterAmp
        * ~qmwQFTV3SiteGain * siteAudioGain).clip(0, 1.5);
    var slot, decay;
    if(~qmwQFTV3AudioReady and: { ~qmwQFTV3SoundEnabled > 0 }
        and: { ~qmwQFTV3RendererMode > 0 }
        and: { ~qmwQFTV3PooledBankSynth.notNil }, {
        slot = ~qmwQFTV3PooledSlotFreeAt.minIndex;
        decay = ~qmwQFTV3EffectiveDecaySeconds.clip(0.03, decayMaximum);
        ~qmwQFTV3PooledSlotFreeAt[slot] = (SystemClock.seconds
            + (decay * 1.45) + 0.04);
        ~qmwQFTV3PooledFrequency[slot] = baseFrequency;
        ~qmwQFTV3PooledStrength[slot] = (0.12 + (scaledIncrement * 12))
            .clip(0.12, 1.5);
        ~qmwQFTV3PooledField[slot] = phi;
        ~qmwQFTV3PooledMomentum[slot] = momentum;
        ~qmwQFTV3PooledEnergy[slot] = localEnergy;
        ~qmwQFTV3PooledDecay[slot] = decay;
        ~qmwQFTV3PooledAmplitude[slot] = amplitude;
        ~qmwQFTV3PooledLane[slot] = site;
        // Incrementing this value gives Changed.kr one trigger per allocation.
        // Send it last so a slot never fires with a partially updated state.
        ~qmwQFTV3PooledSlotTokens[slot] =
            ~qmwQFTV3PooledSlotTokens[slot] + 1.0;
        ~qmwQFTV3PooledBankSynth.setn(\frequencies, ~qmwQFTV3PooledFrequency);
        ~qmwQFTV3PooledBankSynth.setn(\strengths, ~qmwQFTV3PooledStrength);
        ~qmwQFTV3PooledBankSynth.setn(\fields, ~qmwQFTV3PooledField);
        ~qmwQFTV3PooledBankSynth.setn(\momenta, ~qmwQFTV3PooledMomentum);
        ~qmwQFTV3PooledBankSynth.setn(\energies, ~qmwQFTV3PooledEnergy);
        ~qmwQFTV3PooledBankSynth.setn(\decays, ~qmwQFTV3PooledDecay);
        ~qmwQFTV3PooledBankSynth.setn(\amplitudes, ~qmwQFTV3PooledAmplitude);
        ~qmwQFTV3PooledBankSynth.setn(\lanes, ~qmwQFTV3PooledLane);
        ~qmwQFTV3PooledBankSynth.setn(\triggers, ~qmwQFTV3PooledSlotTokens);
    });
};

~qmwQFTV3RenderDynamicPulse = {
    |site, scaledIncrement, phi, momentum, localEnergy,
    x, y, z, purity, coherence, entropy|
    var strength = (0.12 + (scaledIncrement * 12)).clip(0.12, 1.5);
    // LFOs are sampled here once per pulse. Active Synth nodes do not acquire
    // extra continuous modulators, which keeps V5/32 performance bounded.
    var descriptor = ~qmwQFTV3EffectiveDescriptor.(x, y, z);
    var effectiveX = descriptor[0];
    var effectiveY = descriptor[1];
    var effectiveZ = descriptor[2];
    // Signed, site-local musical projection of the Gaussian descriptor.
    // x/y are dimensionless local field/momentum means and z is the local
    // covariance anisotropy. This is an explicit pitch adapter, not evolution.
    var deviationControl = (
        (effectiveX * 0.5) + (effectiveY * 0.3) + (effectiveZ * 0.2)
    ).clip(-1, 1);
    var deviationCents = ~qmwQFTV3FluctuationMix.clip(0, 1200)
        * deviationControl;
    var baseFrequency = (
        ~qmwQFTV3Fundamental * ~qmwQFTV3SitePitchRatios[site]
        * 2.pow(deviationCents / 1200)
    ).clip(1, 16000);
    var siteAudioGain = ~qmwQFTV3SiteGains[site].clip(0, 2)
        * (1 - ~qmwQFTV3SiteMutes[site].clip(0, 1));
    var baseAmp = ~qmwQFTV3PulseMix * ~qmwQFTV3MasterAmp
        * ~qmwQFTV3SiteGain * siteAudioGain;
    var voiceLevels = ~qmwQFTV3EffectiveVoiceGains.();
    var fxActive = (~qmwQFTV42BFXEnabled ? false).asBoolean
        and: { ~qmwQFTV42BFXSendBus.notNil }
        and: { ~qmwQFTV42BFXSendControlBus.notNil };
    var spawnSimple, spawnGaussian, spawnFM, requiredVoices, admitted;
    spawnSimple = { |voiceIndex, gainCompensation|
        ~qmwQFTV3SpawnPulseVoice.(
            \qmwScalarFieldPulseSimpleV3,
            [
                \out, ~qmwQFTV3PulseBus,
                \lane, site,
                \frequency, baseFrequency,
                \strength, strength,
                \fieldColor, phi,
                \momentumColor, momentum,
                \fieldDepth, ~qmwQFTV3CoherentMix,
                \momentumDepth, ~qmwQFTV3MomentumMix,
                \localEnergy, localEnergy,
                \decaySeconds, ~qmwQFTV3EffectiveDecaySeconds,
                \voiceGainBus, ~qmwQFTV3VoiceGainBus.index + voiceIndex,
                \ringMixBus, ~qmwQFTV3RingModMixBus,
                \ringFrequencyBus, ~qmwQFTV3RingModFrequencyBus,
                \wavefoldMixBus, ~qmwQFTV3WavefoldMixBus,
                \wavefoldDriveBus, ~qmwQFTV3WavefoldDriveBus,
                \wavefoldWarpAmountBus, ~qmwQFTV3WavefoldWarpAmountBus,
                \wavefoldWarpShapeBus, ~qmwQFTV3WavefoldWarpShapeBus,
                \fuzzMixBus, ~qmwQFTV3FuzzMixBus,
                \fuzzDriveBus, ~qmwQFTV3FuzzDriveBus,
                \fuzzSecondBus, ~qmwQFTV3FuzzSecondBus,
                \fuzzThirdBus, ~qmwQFTV3FuzzThirdBus,
                \fuzzHigherBus, ~qmwQFTV3FuzzHigherBus,
                \fuzzBiasBus, ~qmwQFTV3FuzzBiasBus,
                \fuzzToneBus, ~qmwQFTV3FuzzToneBus,
                \fxSendBus, if(fxActive, { ~qmwQFTV42BFXSendBus.index }, { 0 }),
                \fxSendControlBus, if(fxActive, {
                    ~qmwQFTV42BFXSendControlBus.index + voiceIndex
                }, { 0 }),
                \fxEnabled, fxActive.asInteger,
                \amp, baseAmp * gainCompensation
            ]
        )
    };
    spawnGaussian = { |voiceIndex, gainCompensation|
        ~qmwQFTV3SpawnPulseVoice.(
            \qmwGaussianGenExprPulseV3,
            [
                \out, ~qmwQFTV3PulseBus,
                \lane, site,
                \x, effectiveX,
                \y, effectiveY,
                \z, effectiveZ,
                \fieldDepth, ~qmwQFTV3CoherentMix,
                \momentumDepth, ~qmwQFTV3MomentumMix,
                \purity, purity,
                \coherence, coherence,
                \entropy, entropy,
                \baseFreq, baseFrequency,
                \strength, strength,
                \decaySeconds, ~qmwQFTV3EffectiveDecaySeconds,
                \voiceGain, ~qmwQFTV3GaussianPulseGain,
                \voiceGainBus, ~qmwQFTV3VoiceGainBus.index + voiceIndex,
                \ringMixBus, ~qmwQFTV3RingModMixBus,
                \ringFrequencyBus, ~qmwQFTV3RingModFrequencyBus,
                \wavefoldMixBus, ~qmwQFTV3WavefoldMixBus,
                \wavefoldDriveBus, ~qmwQFTV3WavefoldDriveBus,
                \wavefoldWarpAmountBus, ~qmwQFTV3WavefoldWarpAmountBus,
                \wavefoldWarpShapeBus, ~qmwQFTV3WavefoldWarpShapeBus,
                \fuzzMixBus, ~qmwQFTV3FuzzMixBus,
                \fuzzDriveBus, ~qmwQFTV3FuzzDriveBus,
                \fuzzSecondBus, ~qmwQFTV3FuzzSecondBus,
                \fuzzThirdBus, ~qmwQFTV3FuzzThirdBus,
                \fuzzHigherBus, ~qmwQFTV3FuzzHigherBus,
                \fuzzBiasBus, ~qmwQFTV3FuzzBiasBus,
                \fuzzToneBus, ~qmwQFTV3FuzzToneBus,
                \fxSendBus, if(fxActive, { ~qmwQFTV42BFXSendBus.index }, { 0 }),
                \fxSendControlBus, if(fxActive, {
                    ~qmwQFTV42BFXSendControlBus.index + voiceIndex
                }, { 0 }),
                \fxEnabled, fxActive.asInteger,
                \amp, baseAmp * gainCompensation
            ]
        )
    };
    spawnFM = { |voiceIndex|
        ~qmwQFTV3SpawnPulseVoice.(
            \qmwQHOFieldFMPulseV3,
            [
                \out, ~qmwQFTV3PulseBus,
                \lane, site,
                // Rotate first, then let field/momentum depths weight the
                // audible phase plane inside the FM voice.
                \x, effectiveX,
                \y, effectiveY,
                \z, effectiveZ,
                \fieldDepth, ~qmwQFTV3CoherentMix,
                \momentumDepth, ~qmwQFTV3MomentumMix,
                \purity, purity,
                \coherence, coherence,
                \entropy, entropy,
                \baseFreq, baseFrequency,
                \strength, strength,
                \decaySeconds, ~qmwQFTV3EffectiveDecaySeconds,
                \fmRatio, ~qmwQFTV3FMRatio,
                \fmIndex, ~qmwQFTV3FMIndex,
                \fmQuantumDepth, ~qmwQFTV3FMQuantumDepth,
                \voiceGainBus, ~qmwQFTV3VoiceGainBus.index + voiceIndex,
                \ringMixBus, ~qmwQFTV3RingModMixBus,
                \ringFrequencyBus, ~qmwQFTV3RingModFrequencyBus,
                \wavefoldMixBus, ~qmwQFTV3WavefoldMixBus,
                \wavefoldDriveBus, ~qmwQFTV3WavefoldDriveBus,
                \wavefoldWarpAmountBus, ~qmwQFTV3WavefoldWarpAmountBus,
                \wavefoldWarpShapeBus, ~qmwQFTV3WavefoldWarpShapeBus,
                \fuzzMixBus, ~qmwQFTV3FuzzMixBus,
                \fuzzDriveBus, ~qmwQFTV3FuzzDriveBus,
                \fuzzSecondBus, ~qmwQFTV3FuzzSecondBus,
                \fuzzThirdBus, ~qmwQFTV3FuzzThirdBus,
                \fuzzHigherBus, ~qmwQFTV3FuzzHigherBus,
                \fuzzBiasBus, ~qmwQFTV3FuzzBiasBus,
                \fuzzToneBus, ~qmwQFTV3FuzzToneBus,
                \fxSendBus, if(fxActive, { ~qmwQFTV42BFXSendBus.index }, { 0 }),
                \fxSendControlBus, if(fxActive, {
                    ~qmwQFTV42BFXSendControlBus.index + voiceIndex
                }, { 0 }),
                \fxEnabled, fxActive.asInteger,
                \amp, baseAmp
            ]
        )
    };
    // Calculate the complete node cost before rendering. Layered deliberately
    // costs two nodes; it cannot evade the governor by creating them one at a
    // time. This is a sonic safety boundary, not a change to event physics.
    requiredVoices =
        (if(voiceLevels[0] > 0.0001, { 1 }, { 0 }))
        + (if(voiceLevels[1] > 0.0001, { 1 }, { 0 }))
        + (if(voiceLevels[2] > 0.0001, { 2 }, { 0 }))
        + (if(voiceLevels[3] > 0.0001, { 1 }, { 0 }));
    if(~qmwQFTV3AudioReady and: { ~qmwQFTV3SoundEnabled > 0 }
        and: { ~qmwQFTV3RendererMode > 0 }) {
        admitted = ~qmwQFTV3AdmitPulseEvent.(
            site, requiredVoices, ~qmwQFTV3ScheduledPulseTime
        );
        if(admitted, {
        if(voiceLevels[0] > 0.0001) { spawnSimple.(0, 1.0) };
        if(voiceLevels[1] > 0.0001) { spawnGaussian.(1, 1.0) };
        // Layered remains its own mixer channel: it deliberately instantiates
        // both established voices with equal-power compensation.
        if(voiceLevels[2] > 0.0001) {
            spawnSimple.(2, ~qmwQFTV3LayeredVoiceGain);
            spawnGaussian.(2, ~qmwQFTV3LayeredVoiceGain);
        };
        if(voiceLevels[3] > 0.0001) { spawnFM.(3) };
        });
    };
};

~qmwQFTV3RenderPulse = {
    |site, scaledIncrement, phi, momentum, localEnergy,
    x, y, z, purity, coherence, entropy|
    if(~qmwQFTV3PooledRendererEnabled, {
        ~qmwQFTV3RenderPooledPulse.value(
            site, scaledIncrement, phi, momentum, localEnergy,
            x, y, z, purity, coherence, entropy
        );
    }, {
        ~qmwQFTV3RenderDynamicPulse.value(
            site, scaledIncrement, phi, momentum, localEnergy,
            x, y, z, purity, coherence, entropy
        );
    });
};

// Build the full pulse bundle now, but timestamp it for a future server onset.
// SystemClock may wake a little early or late; the audio server receives the
// desired onset time ahead of time and starts the node on its 64-sample grid.
~qmwQFTV3ScheduleSteadyPulse = { |event, onsetTime|
    var delay = (onsetTime - SystemClock.seconds).max(0.001);
    ~qmwQFTV3ScheduledPulseTime = onsetTime;
    s.makeBundle(delay, {
        ~qmwQFTV3RenderPulse.valueArray(event);
    });
    ~qmwQFTV3ScheduledPulseTime = nil;
};

OSCdef(\qmwQFTV3TemporalPulse, { |msg|
    var event = [
        msg[2].asInteger.clip(0, siteCount - 1), msg[5].asFloat,
        msg[6].asFloat, msg[7].asFloat, msg[8].asFloat,
        msg[9].asFloat, msg[10].asFloat, msg[11].asFloat,
        msg[12].asFloat, msg[13].asFloat, msg[14].asFloat
    ];
    var record = msg[1].asInteger;
    var step, hit, delays;
    case
    { ~qmwQFTV3ClockMode == 0 } {
        ~qmwQFTV3RenderPulse.valueArray(event)
    }
    { ~qmwQFTV3ClockMode == 3 } {
        step = ~qmwQFTV3QuantumEuclideanStep % ~qmwQFTV3EuclideanSteps;
        hit = ~qmwQFTV3EuclideanMask[step];
        ~qmwQFTV3QuantumEuclideanStep = ~qmwQFTV3QuantumEuclideanStep + 1;
        if(hit > 0) { ~qmwQFTV3RenderPulse.valueArray(event) };
    }
    { ~qmwQFTV3ClockMode == 5 } {
        delays = [0, 0.125, 0.25, 0.5].copyRange(
            0, ~qmwQFTV3RecursiveDepth
        ) / (~qmwQFTV3SteadyRate * ~qmwQFTV3ClockScale).max(0.01);
        delays.do { |delay|
            SystemClock.sched(delay, {
                ~qmwQFTV3RenderPulse.valueArray(event);
                nil
            });
        };
    };
}, oscRoot ++ "/temporal/pulse", recvPort: dataPort);

OSCdef(\qmwQFTV3GeodesicSite, { |msg|
    if(msg[2].asInteger == 0) {
        {
            temporalStatus !? { |view| view.string = (
                "Gaussian geodesic: length %    defect %    bend %    records %"
            ).format(
                msg[4].asFloat.round(0.0001), msg[8].asFloat.round(0.0001),
                msg[9].asFloat.round(0.0001), msg[3].asInteger
            ) };
        }.defer;
    };
}, oscRoot ++ "/geodesic/site", recvPort: dataPort);

OSCdef(\qmwQFTV3GeodesicPulse, { |msg|
    if(~qmwQFTV3ClockMode == 4) {
        ~qmwQFTV3RenderPulse.valueArray([
            msg[2].asInteger.clip(0, siteCount - 1), msg[5].asFloat,
            msg[6].asFloat, msg[7].asFloat, msg[8].asFloat,
            msg[9].asFloat, msg[10].asFloat, msg[11].asFloat,
            msg[12].asFloat, msg[13].asFloat, msg[14].asFloat
        ]);
    };
}, oscRoot ++ "/geodesic/pulse", recvPort: dataPort);

~qmwQFTV3SteadyClock !? { |routine| routine.stop };
~qmwQFTV3SteadyClock = Routine({
    var targetOnset = SystemClock.seconds + ~qmwQFTV3SteadyLookaheadSeconds;
    var period, dispatchTime, now, lateness, hit, event;
    loop {
        period = (1 / (~qmwQFTV3SteadyRate * ~qmwQFTV3ClockScale).max(0.01))
            .max(~qmwQFTV3SteadyTargetSeconds);
        // The 20 ms target is a performance-clock request.  If the GUI/OSC
        // language wakes more than 3 ms late, discard its backlog and resync
        // one future server bundle rather than bunching several late attacks.
        dispatchTime = targetOnset - ~qmwQFTV3SteadyLookaheadSeconds;
        now = SystemClock.seconds;
        lateness = now - dispatchTime;
        if(lateness > ~qmwQFTV3SteadyJitterBudgetSeconds, {
            ~qmwQFTV3SteadyLateTickCount = ~qmwQFTV3SteadyLateTickCount + 1;
            ~qmwQFTV3SteadyWorstLateSeconds = ~qmwQFTV3SteadyWorstLateSeconds
                .max(lateness);
            targetOnset = now + ~qmwQFTV3SteadyLookaheadSeconds;
        });
        if([1, 2].includes(~qmwQFTV3ClockMode)) {
            hit = 1;
            if(~qmwQFTV3ClockMode == 2) {
                hit = ~qmwQFTV3EuclideanMask[
                    ~qmwQFTV3EuclideanStep % ~qmwQFTV3EuclideanSteps
                ];
                ~qmwQFTV3EuclideanStep = ~qmwQFTV3EuclideanStep + 1;
            };
            // One cached mode per tick prevents the former 16-node burst.
            // The site cursor advances through the same observed descriptors,
            // so steady/euclidean remain sound adapters over the field rather
            // than inventing a replacement state.
            event = ~qmwQFTV3PulseCache.wrapAt(~qmwQFTV3SteadySiteCursor);
            ~qmwQFTV3SteadySiteCursor = ~qmwQFTV3SteadySiteCursor + 1;
            if(hit > 0) {
                ~qmwQFTV3ScheduleSteadyPulse.(event, targetOnset);
            };
            ~qmwQFTV3SteadyTickCount = ~qmwQFTV3SteadyTickCount + 1;
        };
        targetOnset = targetOnset + period;
        (targetOnset - ~qmwQFTV3SteadyLookaheadSeconds
            - SystemClock.seconds).max(0.0001).wait;
    };
}).play(SystemClock);

OSCdef(\qmwQFTV3PerformanceSaved, { |msg|
    {
        performanceStatus !? { |view| view.string_(
            "saved WAV + 64th MusicXML + LilyPond (% pulse events): %"
            .format(msg[1].asInteger, recordingPath.basename)
        ) };
    }.defer;
}, oscRoot ++ "/performance/saved", recvPort: dataPort);

if(terrainEnabled) {
    OSCdef(\qmwQFTV42TerrainBegin, { |msg|
        ~qmwQFTV42TerrainRevision = msg[1].asInteger;
        ~qmwQFTV42TerrainStageValid = true;
        ~qmwQFTV42TerrainAvailable = 1;
        ~qmwQFTV42TerrainProvider = msg[6].asString;
        ~qmwQFTV42TerrainLastSeen = Main.elapsedTime;
        {
            terrainStatus !? { |view| view.string_(
                "AVAILABLE — rho observer: % — effective terrain, not quantum evolution"
                .format(~qmwQFTV42TerrainProvider)
            ).stringColor_(Color.green(0.72)) };
            terrainAvailableButton !? { |button| button.value_(1) };
            terrainSonifyButton !? { |button| button.enabled_(true) };
        }.defer;
    }, terrainRoot ++ "/frame/begin", recvPort: terrainPort);

    OSCdef(\qmwQFTV42TerrainAvailable, { |msg|
        if(msg[1].asInteger == ~qmwQFTV42TerrainRevision) {
            ~qmwQFTV42TerrainAvailable = msg[2].asInteger.clip(0, 1);
        };
    }, terrainRoot ++ "/available", recvPort: terrainPort);

    OSCdef(\qmwQFTV42TerrainDimension, { |msg|
        if(~qmwQFTV42TerrainStageValid and: {
            msg[1].asInteger == ~qmwQFTV42TerrainRevision
        }) {
            ~qmwQFTV42TerrainDimension = msg[2].asInteger.max(1);
        };
    }, terrainRoot ++ "/dimension", recvPort: terrainPort);

    OSCdef(\qmwQFTV42TerrainQ, { |msg|
        if(~qmwQFTV42TerrainStageValid and: {
            msg[1].asInteger == ~qmwQFTV42TerrainRevision
        }) {
            ~qmwQFTV42TerrainQ = msg.copyRange(2, msg.size - 1)
                .collect(_.asFloat);
        };
    }, terrainRoot ++ "/q", recvPort: terrainPort);

    OSCdef(\qmwQFTV42TerrainQdot, { |msg|
        if(~qmwQFTV42TerrainStageValid and: {
            msg[1].asInteger == ~qmwQFTV42TerrainRevision
        }) {
            ~qmwQFTV42TerrainQdot = msg.copyRange(2, msg.size - 1)
                .collect(_.asFloat);
        };
    }, terrainRoot ++ "/qdot", recvPort: terrainPort);

    OSCdef(\qmwQFTV42TerrainGlobal, { |msg|
        if(~qmwQFTV42TerrainStageValid and: {
            msg[1].asInteger == ~qmwQFTV42TerrainRevision
        }) {
            ~qmwQFTV42TerrainGlobal = msg.copyRange(2, 11)
                .collect(_.asFloat);
        };
    }, terrainRoot ++ "/global", recvPort: terrainPort);

    OSCdef(\qmwQFTV42TerrainEvent, { |msg|
        if(~qmwQFTV42TerrainStageValid and: {
            msg[1].asInteger == ~qmwQFTV42TerrainRevision
        }) {
            var source = msg[2].asInteger;
            var destination = msg[3].asInteger;
            var direction = msg[5].asInteger;
            var magnitude = msg[6].asFloat.max(0);
            var phase = msg[7].asFloat;
            var currentKind = msg[8].asString;
            var dimension = ~qmwQFTV42TerrainDimension.max(1);
            var lane = destination.linlin(
                0, (dimension - 1).max(1), 0, siteCount - 1
            ).round.asInteger.clip(0, siteCount - 1);
            var q = ~qmwQFTV42TerrainQ.wrapAt(destination).asFloat;
            var qdot = ~qmwQFTV42TerrainQdot.wrapAt(destination).asFloat;
            ~qmwQFTV42TerrainLastEvent = [
                source, destination, direction, magnitude, phase, currentKind
            ];
            {
                terrainEventStatus !? { |view| view.string_(
                    "crossing % → %    dir %    flux %    phase %    %"
                    .format(
                        source, destination, direction,
                        magnitude.round(0.0001), phase.round(0.001), currentKind
                    )
                ) };
                terrainEventButton !? { |button|
                    button.value_(1);
                    AppClock.sched(0.12, { button.value_(0); nil });
                };
            }.defer;
            if(
                (~qmwQFTV42TerrainAvailable > 0)
                and: { ~qmwQFTV42TerrainSonify > 0 }
                and: { currentKind == "effective_terrain" }
            ) {
                // Explicit sound adapter only.  It samples the observed
                // crossing and never writes into rho or QFT field evolution.
                ~qmwQFTV3RenderPulse.(
                    lane,
                    (magnitude * 80).clip(0.01, 0.12),
                    q.clip(-1, 1),
                    qdot.clip(-1, 1),
                    ~qmwQFTV42TerrainGlobal[4].abs,
                    q.clip(-1, 1),
                    qdot.clip(-1, 1),
                    direction.clip(-1, 1),
                    ~qmwQFTV42TerrainGlobal[0].clip(0, 1),
                    ~qmwQFTV42TerrainGlobal[7].clip(0, 1),
                    0.0
                );
            };
        };
    }, terrainRoot ++ "/event", recvPort: terrainPort);

    OSCdef(\qmwQFTV42TerrainEnd, { |msg|
        if(~qmwQFTV42TerrainStageValid and: {
            msg[1].asInteger == ~qmwQFTV42TerrainRevision
        }) {
            {
                terrainQView !? { |view| view.value_(
                    ~qmwQFTV42TerrainQ.collect { |value|
                        value.linlin(-0.25, 1.25, 0, 1).clip(0, 1)
                    }
                ) };
                terrainQdotView !? { |view| view.value_(
                    ~qmwQFTV42TerrainQdot.collect { |value|
                        value.linlin(-1, 1, 0, 1).clip(0, 1)
                    }
                ) };
                terrainGlobalStatus !? { |view| view.string_(
                    "purity %    L %    E %    max flux %    crossings/frame %"
                    .format(
                        ~qmwQFTV42TerrainGlobal[0].round(0.001),
                        ~qmwQFTV42TerrainGlobal[1].round(0.0001),
                        ~qmwQFTV42TerrainGlobal[4].round(0.0001),
                        ~qmwQFTV42TerrainGlobal[8].round(0.0001),
                        ~qmwQFTV42TerrainGlobal[9].asInteger
                    )
                ) };
            }.defer;
            ~qmwQFTV42TerrainStageValid = false;
        };
    }, terrainRoot ++ "/frame/end", recvPort: terrainPort);

    ~qmwQFTV42TerrainWatchdog !? { |routine| routine.stop };
    ~qmwQFTV42TerrainWatchdog = Routine({
        loop {
            1.0.wait;
            if(
                (~qmwQFTV42TerrainLastSeen >= 0)
                and: { (Main.elapsedTime - ~qmwQFTV42TerrainLastSeen) > 2.0 }
            ) {
                ~qmwQFTV42TerrainAvailable = 0;
                {
                    terrainStatus !? { |view| view.string_(
                        "UNAVAILABLE — no density-terrain frames on UDP %"
                        .format(terrainPort)
                    ).stringColor_(Color.yellow(0.78)) };
                    terrainAvailableButton !? { |button| button.value_(0) };
                    terrainSonifyButton !? { |button| button.enabled_(false) };
                }.defer;
            };
        };
    }).play(AppClock);
};

{
    var visibleHeight = (Window.availableBounds.height - 80).clip(620, 1120);
    var siteMixerWidth = 520;
    var voiceMixerWidth = 240;
    var voiceColumnWidth = voiceMixerWidth / voiceCount;
    var descriptorAxisNames = ["X", "Y", "Z"];
    var voiceNames = ["Simple", "Gaussian", "Layered", "QHO FM"]
        ++ if(blochVoiceEnabled, { ["Bloch"] }, { [] });
    window = Window(
        "QMW Quantum Scalar Field V% — % QHOs".format(
            displayVersion, siteCount
        ),
        Rect(50, 24, 1120, visibleHeight),
        resizable: true,
        scroll: true
    );
    ~qmwQFTV3Window = window;
    window.background = Color.grey(0.105);
    window.view
        .autohidesScrollers_(false)
        .hasHorizontalScroller_(false)
        .hasVerticalScroller_(true);

    makeLabel = { |text, rect|
        StaticText(window, rect).string_(text).stringColor_(Color.grey(0.86));
    };
    makeSlider = { |label, rect, spec, initial, action, labelWidth=60|
        EZSlider(
            window, rect, label, spec, action, initial,
            labelWidth: labelWidth
        ).setColors(
            Color.grey(0.17), Color.grey(0.78), Color.cyan(0.7),
            Color.grey(0.45), Color.grey(0.9), Color.cyan(0.8)
        );
    };
    makeFieldMesh = { |rect|
        UserView(window, rect)
            .background_(Color.grey(0.08))
            .drawFunc_({ |view|
                var fields = ~qmwQFTV3FieldHistory;
                var momenta = ~qmwQFTV3MomentumHistory;
                var energies = ~qmwQFTV3EnergyHistory;
                var uncertainties = ~qmwQFTV3UncertaintyHistory;
                var width = view.bounds.width;
                var height = view.bounds.height;
                var rows = fields.size;
                var scale = ~qmwQFTV3MeshScale.max(1e-9);
                var colorHistory, colorScale, project, surfaceValue;
                var fillQuad, drawSurface, frontRow;
                var omegaRef, phaseAt, amplitudeAt;
                if(rows == 0) {
                    // A visible idle state distinguishes "waiting for data" from
                    // a failed or black renderer.
                    Pen.strokeColor = Color.grey(0.38, 0.55);
                    Pen.width = 0.7;
                    siteCount.do { |site|
                        var x = site.linlin(
                            0, siteCount - 1, width * 0.17, width * 0.83
                        );
                        Pen.line(Point(x, height * 0.25), Point(
                            site.linlin(
                                0, siteCount - 1, width * 0.05, width * 0.95
                            ),
                            height * 0.88
                        ));
                        Pen.stroke;
                    };
                    6.do { |row|
                        var depth = row / 5;
                        var left = width * (0.05 + (0.12 * (1 - depth)));
                        var right = width * (0.95 - (0.12 * (1 - depth)));
                        var y = height * (0.25 + (0.63 * depth));
                        Pen.line(Point(left, y), Point(right, y));
                        Pen.stroke;
                    };
                    Pen.fillColor = Color.grey(0.78);
                    Pen.font = Font("Helvetica", 13);
                    Pen.stringAtPoint(
                        "waiting for scalar-field frames on UDP %".format(dataPort),
                        Point(width * 0.25, height * 0.47)
                    );
                };
                if(rows > 0) {
                    // Duplicate the first received row locally so it already
                    // forms a surface rather than a single nearly invisible line.
                    if(rows == 1) {
                        fields = [fields[0], fields[0]];
                        momenta = [momenta[0], momenta[0]];
                        energies = [energies[0], energies[0]];
                        uncertainties = [uncertainties[0], uncertainties[0]];
                        rows = 2;
                    };
                    omegaRef = ~qmwQFTV3Frequencies[0].abs.max(1e-6);
                    phaseAt = { |row, site|
                        // Operational local phase-space angle, not global phase.
                        (0 - momenta[row][site]).atan2(
                            omegaRef * fields[row][site]
                        )
                    };
                    amplitudeAt = { |row, site|
                        (
                            fields[row][site].squared
                            + (momenta[row][site] / omegaRef).squared
                        ).sqrt
                    };
                    colorHistory = if(~qmwQFTV3MeshColorMode == 0, {
                        momenta
                    }, {
                        if(~qmwQFTV3MeshColorMode == 1, { energies }, { fields })
                    });
                    colorScale = if(~qmwQFTV3MeshColorMode == 2, {
                        rows.collect { |row|
                            siteCount.collect { |site|
                                amplitudeAt.(row, site)
                            }.maxItem
                        }.maxItem.max(1e-9)
                    }, {
                        colorHistory.collect { |row|
                            row.collect(_.abs).maxItem
                        }.maxItem.max(1e-9)
                    });
                    project = { |row, site, value|
                        var depth = row / (rows - 1).max(1);
                        var left = width * (0.05 + (0.12 * (1 - depth)));
                        var right = width * (0.95 - (0.12 * (1 - depth)));
                        var baseline = height * (0.24 + (0.64 * depth));
                        Point(
                            site.linlin(0, siteCount - 1, left, right),
                            baseline - ((value / scale).clip(-1.5, 1.5) * height * 0.20)
                        )
                    };
                    surfaceValue = { |row, site, layer|
                        fields[row][site] + case
                        { layer == 1 } { uncertainties[row][site] }
                        { layer == -1 } { 0 - uncertainties[row][site] }
                        { 0 }
                    };
                    fillQuad = { |points, color|
                        Pen.fillColor = color;
                        Pen.moveTo(points[0]);
                        Pen.lineTo(points[1]);
                        Pen.lineTo(points[2]);
                        Pen.lineTo(points[3]);
                        // QPen in SuperCollider 3.13 has no closePath method.
                        Pen.lineTo(points[0]);
                        Pen.fill;
                    };
                    drawSurface = { |layer|
                        (rows - 1).do { |row|
                            (siteCount - 1).do { |site|
                                var colorValue, hue, alpha, saturation, brightness;
                                var phases, phaseSin, phaseCos, phaseConfidence;
                                var surfaceColor;
                                if(~qmwQFTV3MeshColorMode == 2) {
                                    phases = [
                                        phaseAt.(row, site),
                                        phaseAt.(row + 1, site),
                                        phaseAt.(row, site + 1),
                                        phaseAt.(row + 1, site + 1)
                                    ];
                                    // Circular averaging avoids a false discontinuity at ±pi.
                                    phaseSin = phases.collect(_.sin).sum;
                                    phaseCos = phases.collect(_.cos).sum;
                                    hue = phaseSin.atan2(phaseCos).linlin(-pi, pi, 0, 1);
                                    phaseConfidence = (
                                        amplitudeAt.(row, site)
                                        + amplitudeAt.(row + 1, site)
                                        + amplitudeAt.(row, site + 1)
                                        + amplitudeAt.(row + 1, site + 1)
                                    ) * 0.25 / colorScale;
                                    phaseConfidence = phaseConfidence.clip(0, 1);
                                    // Near zero amplitude, phase is undefined: desaturate it.
                                    saturation = 0.12 + (0.83 * phaseConfidence);
                                    brightness = 0.48 + (0.42 * phaseConfidence);
                                    alpha = if(layer == 0, {
                                        0.32 + (0.48 * phaseConfidence)
                                    }, {
                                        0.045 + (0.07 * phaseConfidence)
                                    });
                                } {
                                    colorValue = (
                                        colorHistory[row][site]
                                        + colorHistory[row + 1][site]
                                        + colorHistory[row][site + 1]
                                        + colorHistory[row + 1][site + 1]
                                    ) * 0.25 / colorScale;
                                    hue = if(~qmwQFTV3MeshColorMode == 0, {
                                        colorValue.clip(-1, 1).linlin(-1, 1, 0.66, 0.12)
                                    }, {
                                        colorValue.clip(0, 1).linlin(0, 1, 0.66, 0.12)
                                    });
                                    saturation = 0.78;
                                    brightness = 0.9;
                                    alpha = if(layer == 0, { 0.72 }, { 0.075 });
                                };
                                surfaceColor = case
                                { layer == 1 } {
                                    // Upper covariance envelope: vivid magenta.
                                    Color(0.98, 0.16, 0.72, 0.30)
                                }
                                { layer == -1 } {
                                    // Lower covariance envelope: vivid cyan.
                                    Color(0.08, 0.82, 1.0, 0.30)
                                }
                                { Color.hsv(hue, saturation, brightness, alpha) };
                                fillQuad.([
                                    project.(row, site, surfaceValue.(row, site, layer)),
                                    project.(row, site + 1, surfaceValue.(row, site + 1, layer)),
                                    project.(row + 1, site + 1, surfaceValue.(row + 1, site + 1, layer)),
                                    project.(row + 1, site, surfaceValue.(row + 1, site, layer))
                                ], surfaceColor);
                            };
                        };
                        Pen.strokeColor = case
                        { layer == 1 } { Color(1.0, 0.35, 0.82, 0.88) }
                        { layer == -1 } { Color(0.18, 0.88, 1.0, 0.88) }
                        { Color.grey(0.88, 0.64) };
                        Pen.width = if(layer == 0, { 0.8 }, { 1.25 });
                        rows.do { |row|
                            if((layer == 0) or: { (row % 3) == 0 }) {
                                siteCount.do { |site|
                                    var point = project.(
                                        row, site, surfaceValue.(row, site, layer)
                                    );
                                    if(site == 0, { Pen.moveTo(point) }, {
                                        Pen.lineTo(point)
                                    });
                                };
                                Pen.stroke;
                            };
                        };
                        siteCount.do { |site|
                            rows.do { |row|
                                var point = project.(
                                    row, site, surfaceValue.(row, site, layer)
                                );
                                if(row == 0, { Pen.moveTo(point) }, {
                                    Pen.lineTo(point)
                                });
                            };
                            Pen.stroke;
                        };
                    };
                    // Uncertainty is drawn first as two translucent envelopes;
                    // the authoritative mean field remains the central surface.
                    drawSurface.(1);
                    drawSurface.(-1);
                    drawSurface.(0);
                    frontRow = rows - 1;
                    if(~qmwQFTV3MeshCorrelations > 0) {
                        (siteCount - 1).do { |leftSite|
                            ((leftSite + 1)..(siteCount - 1)).do { |rightSite|
                                var covariance = ~qmwQFTV3Correlation[
                                    (leftSite * siteCount) + rightSite
                                ];
                                var denominator = (
                                    ~qmwQFTV3Correlation[
                                        (leftSite * siteCount) + leftSite
                                    ]
                                    * ~qmwQFTV3Correlation[
                                        (rightSite * siteCount) + rightSite
                                    ]
                                ).max(1e-12).sqrt;
                                var coefficient = (covariance / denominator).clip(-1, 1);
                                if(coefficient.abs > 0.12) {
                                    Pen.strokeColor = if(coefficient >= 0, {
                                        Color.cyan(0.75, coefficient.abs * 0.45)
                                    }, {
                                        Color.magenta(0.75, coefficient.abs * 0.45)
                                    });
                                    Pen.width = 0.5 + coefficient.abs;
                                    Pen.line(
                                        project.(frontRow, leftSite, fields[frontRow][leftSite]),
                                        project.(frontRow, rightSite, fields[frontRow][rightSite])
                                    );
                                    Pen.stroke;
                                };
                            };
                        };
                    };
                    Pen.fillColor = Color.white.alpha_(0.85);
                    siteCount.do { |site|
                        var point = project.(
                            frontRow, site, fields[frontRow][site]
                        );
                        Pen.fillOval(Rect(point.x - 2, point.y - 2, 4, 4));
                    };
                };
            });
    };
    resolveAbletonBridgeDevice = {
        var candidates = ServerOptions.outDevices.select { |device|
            var name = device.asString.toLower;
            name.contains("blackhole") or: {
                name.contains("loopback") or: {
                    name.contains("vb-cable") or: { name.contains("soundflower") }
                }
            }
        };
        candidates.detect { |device| device.asString.toLower.contains("2ch") }
        ? candidates.first;
    };
    refreshAudioDevices = {
        var currentDevice = ~qmwQFTV3SelectedOutputDevice;
        var detectedDevices;
        var selectedIndex;
        var bridgeDevice;
        audioDeviceMenu !? { |menu|
            currentDevice = audioDeviceValues[menu.value];
        };
        detectedDevices = ServerOptions.outDevices;
        bridgeDevice = resolveAbletonBridgeDevice.();
        audioDeviceValues = [nil, \qmwQFTV3AbletonLiveBridge] ++ detectedDevices;
        audioDeviceItems = [
            "system default",
            if(bridgeDevice.notNil, {
                "Ableton Live bridge — %".format(bridgeDevice)
            }, {
                "Ableton Live bridge (virtual stereo device required)"
            })
        ] ++ detectedDevices;
        audioDeviceMenu !? { |menu|
            menu.items_(audioDeviceItems);
            selectedIndex = audioDeviceValues.indexOfEqual(currentDevice);
            menu.value_(selectedIndex ? 0);
        };
    };
    refreshAudioDevices.();
    refreshMIDIInputs = {
        var previousUID = ~qmwQFTV3SelectedMIDIInputUID;
        var selectedSource, selectedIndex;
        MIDIClient.init;
        MIDIIn.connectAll;
        midiInputValues = [nil] ++ MIDIClient.sources;
        midiInputItems = ["disabled"] ++ MIDIClient.sources.collect { |source|
            "% — %".format(source.device, source.name)
        };
        selectedSource = midiInputValues.detect { |source|
            source.notNil and: { source.uid == previousUID }
        };
        // Prefer the attached Akai MPK on first launch. Never fall through to
        // an unrelated source such as IAC unless the performer selects it.
        if(selectedSource.isNil, {
            selectedSource = midiInputValues.detect { |source|
                source.notNil and: {
                    source.device.asString.toLower.contains("mpk") or: {
                        source.name.asString.toLower.contains("mpk")
                    }
                }
            }
        });
        ~qmwQFTV3SelectedMIDIInputUID = if(selectedSource.isNil, {
            nil
        }, {
            selectedSource.uid
        });
        selectedIndex = midiInputValues.indexOfEqual(selectedSource) ? 0;
        midiInputMenu !? { |menu|
            menu.items_(midiInputItems);
            menu.value_(selectedIndex);
        };
    };
    installMIDIPresetMapping = {
        var selectedSource = midiInputValues.detect { |source|
            source.notNil and: {
                source.uid == ~qmwQFTV3SelectedMIDIInputUID
            }
        };
        var sourceLabel;
        ~qmwQFTV3MIDIPresetNoteOn !? { |handler| handler.free };
        ~qmwQFTV3MIDIPresetNoteOn = nil;
        if(selectedSource.isNil, {
            performanceStatus !? { |view| view.string_(
                "MIDI preset recall disabled"
            ) };
            midiInputStatus !? { |view| view.string_(
                "disabled — select the Akai MPK, then press C0 for preset 1"
            ).stringColor_(Color.yellow(0.78)) };
        }, {
            sourceLabel = "% — %".format(
                selectedSource.device, selectedSource.name
            );
            ~qmwQFTV3MIDIPresetNoteOn = MIDIFunc.noteOn({
                |velocity, note, channel, source|
                var slot = note.asInteger - ~qmwQFTV3MIDIPresetBaseNote;
                if((velocity > 0) and: {
                    slot.inclusivelyBetween(0, presetSlotCount - 1)
                }, {
                    {
                        recallPresetSlot.(
                            slot,
                            "% note %".format(sourceLabel, note)
                        );
                    }.defer;
                });
            }, nil, nil, selectedSource.uid);
            performanceStatus !? { |view| view.string_(
                "MIDI ready: C0-G2 recalls slots 1-32"
            ) };
            midiInputStatus !? { |view| view.string_(
                "listening: % | C0 = preset 1".format(sourceLabel)
            ).stringColor_(Color.green(0.76)) };
        });
    };
    refreshMIDIInputs.();
    sendLocalized = {
        control.sendMsg(
            oscRoot ++ "/control/localized",
            ~qmwQFTV3Site, ~qmwQFTV3Amplitude
        )
    };
    sendDisplacement = {
        control.sendMsg(
            oscRoot ++ "/control/displacement",
            ~qmwQFTV3DisplacementRe, ~qmwQFTV3DisplacementIm
        )
    };
    sendSqueezing = {
        control.sendMsg(
            oscRoot ++ "/control/squeezing",
            ~qmwQFTV3SqueezingMagnitude, ~qmwQFTV3SqueezingPhase
        )
    };
    updateBogoliubov = {
        var mu = ~qmwQFTV3SqueezingMagnitude.cosh;
        var betaMagnitude = ~qmwQFTV3SqueezingMagnitude.sinh;
        var betaReal = 0 - (
            betaMagnitude * ~qmwQFTV3SqueezingPhase.cos
        );
        var betaImaginary = 0 - (
            betaMagnitude * ~qmwQFTV3SqueezingPhase.sin
        );
        bogoliubovStatus !? { |view| view.string_(
            "derived Bogoliubov  α_B % + 0i    β_B % % %i    |α|²-|β|² = 1"
            .format(
                mu.round(0.001), betaReal.round(0.001),
                if(betaImaginary >= 0, { "+" }, { "-" }),
                betaImaginary.abs.round(0.001)
            )
        ) };
    };
    sendField = {
        control.sendMsg(
            oscRoot ++ "/control/field", ~qmwQFTV3Mass, ~qmwQFTV3Speed
        )
    };
    sendPerformanceConfig = {
        // Mode 3 is the local Scala/verified-geometry ratio adapter. It has
        // no corresponding QFT performance enum, so never misrepresent it
        // as a field-engine pitch mode in the performance control protocol.
        if(~qmwQFTV3PitchMode <= 2, {
            control.sendMsg(
                oscRoot ++ "/control/performance-config",
                ~qmwQFTV3Fundamental, ~qmwQFTV3PitchMode,
                ~qmwQFTV3DecaySeconds, ~qmwQFTV3FluctuationMix
            )
        })
    };
    applyFundamental = { |requestedFrequency|
        var appliedFrequency = requestedFrequency.asFloat.clip(1, 220);
        if(~qmwQFTV3FundamentalMode == 1, {
            appliedFrequency = appliedFrequency.cpsmidi.round.midicps.clip(1, 220)
        });
        ~qmwQFTV3Fundamental = appliedFrequency;
        fundamentalSlider !? { |view|
            if((view.value - appliedFrequency).abs > 0.0001, {
                view.value_(appliedFrequency)
            })
        };
        ~qmwQFTV3Synth !? { |synth|
            synth.set(\fundamental, appliedFrequency)
        };
        // Optional V4.2 adapters may follow the same downstream pitch root.
        // This callback changes audio mapping only, never field evolution.
        ~qmwQFTV42BlochPushAudio !? { |function| function.value };
        ~qmwQFTV3UpdateRingMod.();
        sendPerformanceConfig.();
        appliedFrequency
    };
    updateEuclideanPattern = {
        var steps = ~qmwQFTV3EuclideanSteps.clip(2, 16);
        var hits = ~qmwQFTV3EuclideanHits.clip(1, steps);
        ~qmwQFTV3EuclideanSteps = steps;
        ~qmwQFTV3EuclideanHits = hits;
        ~qmwQFTV3EuclideanMask = Array.fill(16, { |index|
            if(index < steps, {
                (((index * hits) % steps) < hits).asInteger
            }, { 0 })
        });
    };
    capturePreset = {
        (
            schema: "qmw.qft.v%.preset_slot.v1".format(instrumentVersion),
            sites: siteCount,
            state: stateMenu.value,
            mass: massSlider.value,
            propagation: propagationSlider.value,
            site: siteSlider.value,
            amplitude: amplitudeSlider.value,
            mode: modeSlider.value,
            displacementRe: displacementReSlider.value,
            displacementIm: displacementImSlider.value,
            squeeze: squeezingMagnitudeSlider.value,
            squeezePhase: squeezingPhaseSlider.value,
            temperature: temperatureSlider.value,
            sound: soundButton.value,
            rendererMode: rendererModeMenu.value,
            fundamentalMode: fundamentalModeMenu.value,
            fundamental: fundamentalSlider.value,
            coherent: coherentSlider.value,
            momentum: momentumSlider.value,
            fluctuations: fluctuationSlider.value,
            vacuum: vacuumSlider.value,
            fieldMix: fieldMixSlider.value,
            decay: decaySlider.value,
            energyDecayAmount: energyDecaySlider.value,
            master: masterSlider.value,
            fieldLaneGains: ~qmwQFTV3FieldLaneGains.copy,
            fieldLaneMutes: ~qmwQFTV3FieldLaneMutes.copy,
            siteGains: ~qmwQFTV3SiteGains.copy,
            siteMutes: ~qmwQFTV3SiteMutes.copy,
            temporal: temporalModeMenu.value,
            clockAdapter: clockAdapterMenu.value,
            pitch: pitchMenu.value,
            voice: voiceMenu.value,
            voiceGains: ~qmwQFTV3VoiceGains.copy,
            voiceMutes: ~qmwQFTV3VoiceMutes.copy,
            distance: distanceSlider.value,
            clock: clockSlider.value,
            pulses: pulseSlider.value,
            oddEvenStereoWidth: oddEvenStereoSlider.value,
            ringModBlend: ~qmwQFTV3RingModBlend,
            ringModHarmonic: ~qmwQFTV3RingModHarmonic,
            ringModFineTuneCents: ~qmwQFTV3RingModFineTuneCents,
            wavefoldBlend: ~qmwQFTV3WavefoldBlend,
            wavefoldDrive: ~qmwQFTV3WavefoldDrive,
            wavefoldWarpAmount: ~qmwQFTV3WavefoldWarpAmount,
            wavefoldWarpShape: ~qmwQFTV3WavefoldWarpShape,
            fuzzBlend: ~qmwQFTV3FuzzBlend,
            fuzzDrive: ~qmwQFTV3FuzzDrive,
            fuzzSecond: ~qmwQFTV3FuzzSecond,
            fuzzThird: ~qmwQFTV3FuzzThird,
            fuzzHigher: ~qmwQFTV3FuzzHigher,
            fuzzBias: ~qmwQFTV3FuzzBias,
            fuzzTone: ~qmwQFTV3FuzzTone,
            fmRatio: ~qmwQFTV3FMRatio,
            fmIndex: ~qmwQFTV3FMIndex,
            fmQuantumDepth: ~qmwQFTV3FMQuantumDepth,
            descriptorSource: ~qmwQFTV3DescriptorSource,
            descriptorClock: ~qmwQFTV3DescriptorClock,
            descriptorRotation: ~qmwQFTV3DescriptorRotationDegrees,
            descriptorManual: ~qmwQFTV3DescriptorManual.copy,
            descriptorLFODepth: ~qmwQFTV3DescriptorLFODepth.copy,
            descriptorLFORate: ~qmwQFTV3DescriptorLFORate.copy,
            descriptorLFOPhase: ~qmwQFTV3DescriptorLFOPhase.copy,
            steadyRate: steadyRateSlider.value,
            euclidHits: euclidHitsSlider.value,
            euclidSteps: euclidStepsSlider.value,
            geodesicBend: geodesicBendSlider.value,
            recursiveDepth: recursiveDepthSlider.value
        )
    };
    applyPreset = { |preset|
        var savedSiteGains = preset[\siteGains]
            ? Array.fill(siteCount, 1.0);
        var savedSiteMutes = preset[\siteMutes]
            ? Array.fill(siteCount, 0);
        var savedFieldLaneGains = preset[\fieldLaneGains]
            ? Array.fill(siteCount, 1.0);
        var savedFieldLaneMutes = preset[\fieldLaneMutes]
            ? Array.fill(siteCount, 0);
        var savedDescriptorManual = preset[\descriptorManual] ? [0, 0, 0];
        var savedDescriptorDepth = preset[\descriptorLFODepth] ? [0, 0, 0];
        var savedDescriptorRate = preset[\descriptorLFORate] ? [0.11, 0.17, 0.23];
        var savedDescriptorPhase = preset[\descriptorLFOPhase] ? [0, 120, 240];
        var savedVoiceMode = (preset[\voice] ? 1).asInteger.clip(0, 5);
        var defaultVoiceGains = Array.fill(voiceCount, 0.0);
        var savedVoiceGains, savedVoiceMutes, savedVoiceMenu;
        // Legacy exclusive presets stored menu values 0..3, while later banks
        // may contain custom-mix (4) or pooled (5) without a voiceGains array.
        // Those menu-only presets fall back to Gaussian instead of indexing
        // beyond the event-voice gain lanes. V4.2 may append its Bloch lane.
        defaultVoiceGains[
            if(savedVoiceMode < 4, { savedVoiceMode }, { 1 })
        ] = 1.0;
        savedVoiceGains = preset[\voiceGains] ? defaultVoiceGains;
        savedVoiceMutes = preset[\voiceMutes] ? Array.fill(voiceCount, 0);
        savedVoiceMenu = if(preset[\voiceGains].notNil, {
            (preset[\voice] ? 4).asInteger.clip(0, 5)
        }, {
            savedVoiceMode
        });
        stateMenu.valueAction_(preset[\state]);
        massSlider.valueAction_(preset[\mass]);
        propagationSlider.valueAction_(preset[\propagation]);
        siteSlider.valueAction_(preset[\site]);
        amplitudeSlider.valueAction_(preset[\amplitude]);
        modeSlider.valueAction_(preset[\mode]);
        displacementReSlider.valueAction_(preset[\displacementRe]);
        displacementImSlider.valueAction_(preset[\displacementIm]);
        rendererModeMenu.valueAction_(preset[\rendererMode] ? 2);
        fundamentalModeMenu.value_(
            (preset[\fundamentalMode] ? 0).asInteger.clip(0, 1)
        );
        ~qmwQFTV3FundamentalMode = fundamentalModeMenu.value;
        fundamentalSlider.valueAction_(preset[\fundamental]);
        coherentSlider.valueAction_(preset[\coherent]);
        momentumSlider.valueAction_(preset[\momentum]);
        fluctuationSlider.valueAction_(preset[\fluctuations]);
        vacuumSlider.valueAction_(preset[\vacuum]);
        fieldMixSlider.valueAction_(preset[\fieldMix] ? 0.20);
        decaySlider.valueAction_(preset[\decay]);
        energyDecaySlider.valueAction_(preset[\energyDecayAmount] ? 0);
        masterSlider.valueAction_(preset[\master]);
        ~qmwQFTV3FieldLaneGains = Array.fill(siteCount, { |site|
            (savedFieldLaneGains[site] ? 1.0).asFloat.clip(0, 2)
        });
        ~qmwQFTV3FieldLaneMutes = Array.fill(siteCount, { |site|
            (savedFieldLaneMutes[site] ? 0).asInteger.clip(0, 1)
        });
        fieldGainView !? { |view|
            view.value_(~qmwQFTV3FieldLaneGains / 2)
        };
        fieldMuteButtons !? { |buttons|
            buttons.do { |button, site|
                button.value_(~qmwQFTV3FieldLaneMutes[site])
            }
        };
        ~qmwQFTV3UpdateFieldSpectralMix.();
        ~qmwQFTV3SiteGains = Array.fill(siteCount, { |site|
            (savedSiteGains[site] ? 1.0).asFloat.clip(0, 2)
        });
        ~qmwQFTV3SiteMutes = Array.fill(siteCount, { |site|
            (savedSiteMutes[site] ? 0).asInteger.clip(0, 1)
        });
        siteGainView !? { |view|
            view.value_(~qmwQFTV3SiteGains / 2)
        };
        siteMuteButtons !? { |buttons|
            buttons.do { |button, site|
                button.value_(~qmwQFTV3SiteMutes[site])
            }
        };
        ~qmwQFTV3UpdateSiteAudioGains.();
        temporalModeMenu.valueAction_(preset[\temporal]);
        clockAdapterMenu.valueAction_(preset[\clockAdapter] ? 0);
        pitchMenu.valueAction_(preset[\pitch]);
        ~qmwQFTV3VoiceGains = Array.fill(voiceCount, { |voice|
            (savedVoiceGains[voice] ? 0).asFloat.clip(
                0, ~qmwQFTV3VoiceGainCeilings[voice]
            )
        });
        ~qmwQFTV3VoiceMutes = Array.fill(voiceCount, { |voice|
            (savedVoiceMutes[voice] ? 0).asInteger.clip(0, 1)
        });
        ~qmwQFTV3PulseVoiceMode = savedVoiceMenu;
        voiceMenu.value_(savedVoiceMenu);
        ~qmwQFTV3PooledRendererEnabled = (savedVoiceMenu == 5);
        if(~qmwQFTV3PooledRendererEnabled) { ~qmwQFTV3EnsurePooledRenderer.() };
        voiceGainView !? { |view|
            view.value_(~qmwQFTV3VoiceGainSliderValues.())
        };
        voiceMuteButtons !? { |buttons|
            buttons.do { |button, voice|
                button.value_(~qmwQFTV3VoiceMutes[voice])
            }
        };
        ~qmwQFTV3UpdateVoiceMixer.();
        distanceSlider.valueAction_(preset[\distance]);
        clockSlider.valueAction_(preset[\clock]);
        pulseSlider.valueAction_(preset[\pulses]);
        oddEvenStereoSlider.valueAction_(preset[\oddEvenStereoWidth] ? 1);
        ringModBlendSlider.valueAction_(preset[\ringModBlend] ? 0);
        ringModHarmonicSlider.valueAction_(preset[\ringModHarmonic] ? 2);
        ringModFineTuneSlider.valueAction_(preset[\ringModFineTuneCents] ? 0);
        wavefoldBlendSlider.valueAction_(preset[\wavefoldBlend] ? 0);
        wavefoldDriveSlider.valueAction_(preset[\wavefoldDrive] ? 4);
        wavefoldWarpSlider.valueAction_(preset[\wavefoldWarpAmount] ? 0);
        wavefoldWarpShapeMenu.valueAction_(preset[\wavefoldWarpShape] ? 0);
        // Older banks used the short-lived saturationBlend key; carry its
        // amount into the replacement fuzz stage rather than losing the mix.
        fuzzBlendSlider.valueAction_(
            preset[\fuzzBlend] ? (preset[\saturationBlend] ? 0)
        );
        fuzzDriveSlider.valueAction_(preset[\fuzzDrive] ? 2.5);
        fuzzSecondSlider.valueAction_(preset[\fuzzSecond] ? 0);
        fuzzThirdSlider.valueAction_(preset[\fuzzThird] ? 0.65);
        ~qmwQFTV3FuzzHigher = (preset[\fuzzHigher]
            ? (fuzzThirdSlider.value * 1.3)).clip(0, 2);
        ~qmwQFTV3UpdateFuzz.();
        fuzzBiasSlider.valueAction_(preset[\fuzzBias] ? 0);
        fuzzToneSlider.valueAction_(preset[\fuzzTone] ? 0.35);
        fmRatioSlider.valueAction_(preset[\fmRatio] ? 2);
        fmIndexSlider.valueAction_(preset[\fmIndex] ? 0.5);
        fmQuantumDepthSlider.valueAction_(preset[\fmQuantumDepth] ? 2);
        descriptorSourceMenu.valueAction_(preset[\descriptorSource] ? 0);
        descriptorClockMenu.valueAction_(preset[\descriptorClock] ? 0);
        descriptorRotationSlider.valueAction_(
            preset[\descriptorRotation] ? 0
        );
        3.do { |axis|
            descriptorManualSliders[axis].valueAction_(
                savedDescriptorManual[axis] ? 0
            );
            descriptorDepthSliders[axis].valueAction_(
                savedDescriptorDepth[axis] ? 0
            );
            descriptorRateSliders[axis].valueAction_(
                savedDescriptorRate[axis] ? [0.11, 0.17, 0.23][axis]
            );
            descriptorPhaseSliders[axis].valueAction_(
                savedDescriptorPhase[axis] ? [0, 120, 240][axis]
            );
        };
        steadyRateSlider.valueAction_(preset[\steadyRate] ? 7);
        euclidStepsSlider.valueAction_(preset[\euclidSteps] ? 8);
        euclidHitsSlider.valueAction_(preset[\euclidHits] ? 5);
        // V3 presets from before the normalized geodesic clock may hold the
        // former raw-defect values (up to 5000).  The live engine now defines
        // this as a dimensionless curvature-density gain in [0, 100].
        geodesicBendSlider.valueAction_(
            (preset[\geodesicBend] ? 0.6).clip(0, 100)
        );
        recursiveDepthSlider.valueAction_(preset[\recursiveDepth] ? 3);
        squeezingMagnitudeSlider.valueAction_(preset[\squeeze]);
        squeezingPhaseSlider.valueAction_(preset[\squeezePhase]);
        temperatureSlider.valueAction_(preset[\temperature]);
        soundButton.valueAction_(preset[\sound]);
    };
    recallPresetSlot = { |slot, source="GUI"|
        var preset;
        slot = slot.asInteger;
        if(slot.inclusivelyBetween(0, presetSlotCount - 1), {
            presetMenu.value_(slot);
            preset = presetSlots[slot];
            if(preset.isNil, {
                performanceStatus.string_(
                    "%: slot % is empty".format(source, slot + 1)
                );
            }, {
                applyPreset.(preset);
                performanceStatus.string_(
                    "%: recalled slot %".format(source, slot + 1)
                );
            });
        });
    };

    makeLabel.("PREPARED FIELD STATE", Rect(20, 16, 250, 22));
    stateMenu = PopUpMenu(window, Rect(20, 42, 210, 28))
        .items_(["localized", "coherent", "squeezed", "thermal", "vacuum"])
        .value_(0)
        .action_({ |menu|
            control.sendMsg(oscRoot ++ "/control/state", menu.items[menu.value])
        });
    Button(window, Rect(245, 42, 100, 28))
        .states_([["pause"], ["run"]])
        .action_({ |button|
            control.sendMsg(oscRoot ++ "/control/running", 1 - button.value)
        });
    Button(window, Rect(355, 42, 110, 28))
        .states_([["reset time"]])
        .action_({ control.sendMsg(oscRoot ++ "/control/reset", 1) });
    makeLabel.("PERFORMANCE", Rect(500, 16, 120, 22));
    performanceStatus = StaticText(window, Rect(620, 16, 470, 22))
        .string_("presets: MIDI C0-G2 recalls slots 1-32")
        .stringColor_(Color.green(0.75));
    presetMenu = PopUpMenu(window, Rect(500, 42, 90, 28))
        .items_(Array.series(presetSlotCount, 1, 1).collect { |number|
            "slot " ++ number
        })
        .value_(0);
    Button(window, Rect(600, 42, 90, 28))
        .states_([["store"]])
        .action_({
            var slot = presetMenu.value;
            presetSlots[slot] = capturePreset.();
            presetPath.dirname.mkdir;
            presetSlots.writeArchive(presetPath);
            performanceStatus.string_(
                "stored current configuration in slot " ++ (slot + 1)
            );
        });
    Button(window, Rect(700, 42, 90, 28))
        .states_([["recall"]])
        .action_({
            recallPresetSlot.(presetMenu.value, "GUI")
        });

    // Chromatic note-on recall: C0 (MIDI 12) selects slot 1, C#0 slot 2,
    // continuing through G2 for slot 32. The handler is filtered to the source
    // selected in the MIDI Input panel; unrelated inputs cannot recall presets.
    try {
        installMIDIPresetMapping.();
    } { |error|
        performanceStatus.string_(
            "MIDI preset input unavailable: " ++ error.asString
        );
        error.reportError;
    };
    recordingButton = Button(window, Rect(800, 42, 290, 28))
        .states_([
            ["record take (WAV + 64th Q score)", Color.black, Color.red(0.75)],
            ["stop + write score", Color.white, Color.red(0.35)]
        ])
        .action_({ |button|
            if(button.value == 1, {
                var takeId = Date.localtime.stamp;
                if(s.serverRunning.not, {
                    button.value_(0);
                    performanceStatus.string_(
                        "record failed: SuperCollider audio server is not running"
                    );
                }, {
                    recordingPath = recordingDir +/+
                        ("qmw_qft_v" ++ instrumentVersion ++ "_"
                            ++ takeId ++ ".wav");
                    recordingDir.mkdir;
                    s.recHeaderFormat = "wav";
                    s.recSampleFormat = "float";
                    ~qmwQFTV3RecordingReady = false;
                    s.record(
                        recordingPath, 0,
                        if(splitFieldOutput, { 4 }, { 2 })
                    );
                    Routine({
                        100.do {
                            if(s.isRecording.not) { 0.05.wait };
                        };
                        if(s.isRecording and: { button.value == 1 }, {
                            ~qmwQFTV3RecordingReady = true;
                            if(~qmwQFTV3PitchMode <= 2, {
                                control.sendMsg(
                                    oscRoot ++ "/control/performance-record",
                                    1, takeId, "slot " ++ (presetMenu.value + 1),
                                    ~qmwQFTV3Fundamental, ~qmwQFTV3PitchMode,
                                    ~qmwQFTV3DecaySeconds,
                                    ~qmwQFTV3FluctuationMix
                                );
                                performanceStatus.string_(
                                    "recording WAV: " ++ recordingPath.basename
                                );
                            }, {
                                performanceStatus.string_(
                                    "recording WAV only: local Scala/geometry pitch adapter is not a QFT score enum"
                                );
                            });
                        }, {
                            if(s.isRecording) { s.stopRecording };
                            ~qmwQFTV3RecordingReady = false;
                            button.value_(0);
                            performanceStatus.string_(
                                "record failed: WAV recorder did not become ready"
                            );
                        });
                    }).play(AppClock);
                });
            }, {
                if(s.isRecording) { s.stopRecording };
                if(~qmwQFTV3RecordingReady, {
                    control.sendMsg(
                        oscRoot ++ "/control/performance-record", 0
                    );
                    performanceStatus.string_(
                        "WAV saved; finalizing event JSON, 64th MusicXML, and LilyPond..."
                    );
                }, {
                    performanceStatus.string_("recording cancelled before ready");
                });
                ~qmwQFTV3RecordingReady = false;
            });
        });

    makeLabel.("FIELD PHYSICS", Rect(20, 84, 180, 22));
    massSlider = makeSlider.("mass", Rect(20, 110, 320, 28),
        ControlSpec(0.1, 2, \exp, 0.001, 0.6), 0.6,
        { |view| ~qmwQFTV3Mass = view.value; sendField.() });
    propagationSlider = makeSlider.("propagation c", Rect(360, 110, 320, 28),
        ControlSpec(0.1, 2, \exp, 0.001, 1), 1,
        { |view| ~qmwQFTV3Speed = view.value; sendField.() }, 105);
    siteSlider = makeSlider.("localized site", Rect(20, 148, 320, 28),
        ControlSpec(0, siteCount - 1, \lin, 1, siteCount.div(2)),
        siteCount.div(2),
        { |view| ~qmwQFTV3Site = view.value.asInteger; sendLocalized.() });
    amplitudeSlider = makeSlider.("localized amplitude", Rect(360, 148, 320, 28),
        ControlSpec(-2, 2, \lin, 0.01, 1), 1,
        { |view| ~qmwQFTV3Amplitude = view.value; sendLocalized.() });
    modeSlider = makeSlider.("normal mode", Rect(20, 186, 210, 28),
        ControlSpec(0, siteCount - 1, \lin, 1, 0), 0,
        { |view| control.sendMsg(
            oscRoot ++ "/control/mode", view.value.asInteger
        ) });
    displacementReSlider = makeSlider.("displacement Re", Rect(245, 186, 210, 28),
        ControlSpec(-1.5, 1.5, \lin, 0.01, 0.8), 0.8,
        { |view|
            ~qmwQFTV3DisplacementRe = view.value;
            sendDisplacement.()
        }, 100);
    displacementImSlider = makeSlider.("displacement Im", Rect(470, 186, 210, 28),
        ControlSpec(-1.5, 1.5, \lin, 0.01, 0), 0,
        { |view|
            ~qmwQFTV3DisplacementIm = view.value;
            sendDisplacement.()
        }, 100);
    squeezingMagnitudeSlider = makeSlider.("squeeze r", Rect(20, 224, 210, 28),
        ControlSpec(0, 1.5, \lin, 0.01, 0.5), 0.5,
        { |view|
            ~qmwQFTV3SqueezingMagnitude = view.value;
            sendSqueezing.();
            updateBogoliubov.();
        });
    squeezingPhaseSlider = makeSlider.("squeeze phase", Rect(245, 224, 210, 28),
        ControlSpec(0 - pi, pi, \lin, 0.001, 0), 0,
        { |view|
            ~qmwQFTV3SqueezingPhase = view.value;
            sendSqueezing.();
            updateBogoliubov.();
        }, 90);
    temperatureSlider = makeSlider.("temperature", Rect(470, 224, 210, 28),
        ControlSpec(0.05, 3, \exp, 0.001, 0.8), 0.8,
        { |view| control.sendMsg(
            oscRoot ++ "/control/temperature", view.value
        ) });
    bogoliubovStatus = StaticText(window, Rect(20, 254, 660, 20))
        .string_(
            "derived Bogoliubov  α_B 1.128 + 0i    β_B -0.521 + 0i    |α|²-|β|² = 1"
        )
        .stringColor_(Color.yellow(0.72));

    makeLabel.("RENDER", Rect(730, 84, 70, 22));
    rendererModeMenu = PopUpMenu(window, Rect(800, 82, 125, 26))
        .items_(["Field", "Plucks", "Hybrid"])
        .value_(~qmwQFTV3RendererMode)
        .toolTip_(
            "Field is the continuous phi+i*pi drone; Plucks uses admitted events; Hybrid combines both."
        )
        .action_({ |menu|
            ~qmwQFTV3RendererMode = menu.value;
            ~qmwQFTV3UpdateRendererMode.();
        });
    soundButton = Button(window, Rect(935, 82, 155, 26))
        .states_([
            ["sound: on", Color.black, Color.cyan(0.7)],
            ["sound: off", Color.grey(0.85), Color.grey(0.25)]
        ])
        .action_({ |button|
            ~qmwQFTV3SoundEnabled = 1 - button.value;
            ~qmwQFTV3Synth !? { |synth|
                synth.set(\soundEnabled, ~qmwQFTV3SoundEnabled)
            }
        });
    // V4.4 intentionally starts pulse audio muted. Reflect the authoritative
    // adapter state in the button rather than leaving an "on" label over a
    // zero-gain source; the next click must always be the audible action.
    soundButton.value_(1 - ~qmwQFTV3SoundEnabled);
    fundamentalSlider = makeSlider.("fundamental", Rect(730, 110, 225, 28),
        ControlSpec(1, 220, \exp, 0.01, 72), 72,
        { |view|
            applyFundamental.(view.value)
        }, 70);
    fundamentalModeMenu = PopUpMenu(window, Rect(965, 110, 125, 28))
        .items_(["smooth Hz", "12-TET (A=440)"])
        .value_(~qmwQFTV3FundamentalMode)
        .toolTip_(
            "Smooth continuous Hz or nearest 12-tone equal-tempered semitone."
        )
        .action_({ |menu|
            ~qmwQFTV3FundamentalMode = menu.value;
            applyFundamental.(fundamentalSlider.value);
        });
    coherentSlider = makeSlider.("field timbre depth", Rect(730, 148, 360, 28),
        ControlSpec(0, 2, \lin, 0.01, 1), 1,
        { |view|
            ~qmwQFTV3CoherentMix = view.value;
        });
    momentumSlider = makeSlider.("momentum timbre depth", Rect(730, 186, 360, 28),
        ControlSpec(0, 2, \lin, 0.01, 0.45), 0.45,
        { |view|
            ~qmwQFTV3MomentumMix = view.value;
        });
    fluctuationSlider = makeSlider.("site pitch deviation", Rect(730, 224, 360, 28),
        ControlSpec(0, 1200, \lin, 1, 0), 0,
        { |view|
            ~qmwQFTV3FluctuationMix = view.value;
            sendPerformanceConfig.()
        }, 100);
    fieldMixSlider = makeSlider.("field mix", Rect(730, 262, 175, 28),
        ControlSpec(0, 0.6, \lin, 0.001, 0.20), 0.20,
        { |view|
            ~qmwQFTV3FieldMix = view.value;
            ~qmwQFTV3UpdateRendererMode.();
        });
    vacuumSlider = makeSlider.("vacuum ref", Rect(915, 262, 175, 28),
        ControlSpec(0, 0.5, \lin, 0.001, 0.05), 0.05,
        { |view|
            ~qmwQFTV3VacuumMix = view.value;
            ~qmwQFTV3Synth !? { |synth|
                synth.set(\vacuumMix, view.value)
            }
        });
    decaySlider = makeSlider.("decay", Rect(730, 300, 175, 28),
        ControlSpec(0.03, decayMaximum, \exp, 0.001, 0.28), 0.28,
        { |view|
            ~qmwQFTV3DecaySeconds = view.value;
            ~qmwQFTV3ApplyEnergyDecay.();
            sendPerformanceConfig.();
        });
    masterSlider = makeSlider.("master", Rect(915, 300, 175, 28),
        ControlSpec(0, 1, \lin, 0.001, 0.32), 0.32,
        { |view|
            ~qmwQFTV3MasterAmp = view.value;
            ~qmwQFTV3Synth !? { |synth|
                synth.set(\masterAmp, view.value)
            }
        });

    energyDecaySlider = makeSlider.("E->decay", Rect(730, 338, 175, 28),
        ControlSpec(-1, 1, \lin, 0.01, 0), 0,
        { |view|
            ~qmwQFTV3EnergyDecayAttenuverter = view.value;
            ~qmwQFTV3ApplyEnergyDecay.();
        }, 70);

    oddEvenStereoSlider = makeSlider.("odd L / even R", Rect(915, 338, 175, 28),
        ControlSpec(0, 1, \lin, 0.01, 1), 1,
        { |view|
            ~qmwQFTV3OddEvenStereoWidth = view.value;
            ~qmwQFTV3UpdateOddEvenStereo.();
        }, 88);
    temporalModeMenu = PopUpMenu(window, Rect(730, 366, 110, 28))
        .items_(["fixed", "Poisson"])
        .value_(1)
        .action_({ |menu|
            control.sendMsg(
                oscRoot ++ "/control/temporal-mode",
                ["fixed", "poisson"][menu.value]
            )
        });
    pitchMenu = PopUpMenu(window, Rect(850, 366, 125, 28))
        .items_([
            "field normal modes", "harmonics 1-%".format(siteCount), "odd harmonics"
        ])
        .value_(1)
        .action_({ |menu|
            ~qmwQFTV3PitchMode = menu.value;
            ~qmwQFTV3UpdatePitchRatios.();
            sendPerformanceConfig.();
        });
    voiceMenu = PopUpMenu(window, Rect(985, 366, 105, 28))
        .items_([
            "simple", "Gaussian Gen", "layered", "QHO FM", "custom mix",
            "pooled 32"
        ])
        .value_(1)
        .action_({ |menu|
            ~qmwQFTV3PulseVoiceMode = menu.value;
            if(menu.value == 5) { ~qmwQFTV3EnsurePooledRenderer.() };
            ~qmwQFTV3PooledRendererEnabled = (menu.value == 5);
            if(menu.value < 4) {
                ~qmwQFTV3VoiceGains = Array.fill(voiceCount, { |voice|
                    if(voice == menu.value, { 1.0 }, { 0.0 })
                });
                ~qmwQFTV3VoiceMutes = Array.fill(voiceCount, 0);
                voiceGainView !? { |view|
                    view.value_(~qmwQFTV3VoiceGainSliderValues.())
                };
                voiceMuteButtons !? { |buttons|
                    buttons.do { |button| button.value_(0) }
                };
                ~qmwQFTV3UpdateVoiceMixer.();
                voiceMixerStatus !? { |view|
                    view.string_("exclusive audition: " ++ voiceNames[menu.value])
                };
            } {
                if(menu.value == 5) {
                    voiceMixerStatus !? { |view|
                        view.string_("pooled 32: shared nonlinear output")
                    };
                };
            };
        });
    distanceSlider = makeSlider.("Bures distance / pulse", Rect(730, 404, 360, 28),
        ControlSpec(0.001, 0.2, \exp, 0.0001, 0.025), 0.025,
        { |view|
            ~qmwQFTV3TemporalControlPending = "Bures threshold request sent";
            control.sendMsg(oscRoot ++ "/control/temporal-distance", view.value);
            ~qmwQFTV3RefreshClockStatus.();
        }, 125);
    clockSlider = makeSlider.("clock scale", Rect(730, 442, 175, 28),
        ControlSpec(0.01, 4, \exp, 0.001, 1), 1,
        { |view|
            ~qmwQFTV3ClockScale = view.value;
            ~qmwQFTV3TemporalControlPending = "clock-scale request sent";
            control.sendMsg(oscRoot ++ "/control/clock-scale", view.value);
            ~qmwQFTV3RefreshClockStatus.();
        });
    pulseSlider = makeSlider.("pulse mix", Rect(915, 442, 175, 28),
        ControlSpec(0, 1.5, \lin, 0.01, 0.8), 0.8,
        { |view| ~qmwQFTV3PulseMix = view.value });

    makeLabel.("TEMPORAL ADAPTER — DOES NOT ALTER FIELD EVOLUTION", Rect(730, 482, 360, 22));
    clockAdapterMenu = PopUpMenu(window, Rect(730, 506, 230, 28))
        .items_([
            "Quantum", "Steady", "Euclidean", "Q-Euclidean",
            "Q-Geodesic", "Q-Recursive"
        ])
        .value_(0)
        .action_({ |menu|
            ~qmwQFTV3ClockMode = menu.value;
            if(menu.value == 2) { ~qmwQFTV3EuclideanStep = 0 };
            if(menu.value == 3) { ~qmwQFTV3QuantumEuclideanStep = 0 };
            ~qmwQFTV3RefreshClockStatus.();
        });
    recursiveDepthSlider = makeSlider.("recursion", Rect(970, 506, 120, 28),
        ControlSpec(0, 3, \lin, 1, 3), 3,
        { |view| ~qmwQFTV3RecursiveDepth = view.value.asInteger }, 55);
    steadyRateSlider = makeSlider.("steady Hz (max 50)", Rect(730, 544, 175, 28),
        ControlSpec(0.25, 50, \exp, 0.01, 7), 7,
        { |view|
            ~qmwQFTV3SteadyRate = view.value;
            ~qmwQFTV3RefreshClockStatus.();
        });
    geodesicBendSlider = makeSlider.("geodesic bend", Rect(915, 544, 175, 28),
        // This is the normalized curvature-density gain accepted by
        // GaussianFieldTemporalEngine: 0 disables bending weighting.
        ControlSpec(0, 100, \lin, 0.1, 0.6), 0.6,
        { |view| control.sendMsg(
            oscRoot ++ "/control/geodesic-bending-depth", view.value
        ) }, 92);
    euclidHitsSlider = makeSlider.("euclid hits", Rect(730, 582, 175, 28),
        ControlSpec(1, 16, \lin, 1, 5), 5,
        { |view|
            ~qmwQFTV3EuclideanHits = view.value.asInteger;
            updateEuclideanPattern.();
        });
    euclidStepsSlider = makeSlider.("euclid steps", Rect(915, 582, 175, 28),
        ControlSpec(2, 16, \lin, 1, 8), 8,
        { |view|
            ~qmwQFTV3EuclideanSteps = view.value.asInteger;
            updateEuclideanPattern.();
        });
    // The V4.3/V4.4 tuning panel is independently closable. Keep a durable
    // entry point in the inherited main window, rather than requiring a full
    // instrument relaunch just to return to scale and pitch-source controls.
    if(~qmwQFTV43Enabled == true, {
        Button(window, Rect(730, 620, 360, 28))
            .states_([["OPEN TUNING + MEMBRANE", Color.black, Color.yellow(0.72)]])
            .action_({ ~qmwQFTV43OpenPanel !? { |openPanel| openPanel.value } });
        // V4.4/V4.5 observers are read-only windows over their own published
        // frames. Keeping their entry points beside tuning makes every main
        // instrument view reachable without a separate menu or relaunch.
        if(~qmwQFTV44Enabled == true, {
            Button(window, Rect(730, 654, 175, 28))
                .states_([["OPEN GEOMETRY", Color.black, Color.cyan(0.72)]])
                .action_({
                    if(~qmwQFTV44OpenFieldFrameGeometryPanel.notNil, {
                        ~qmwQFTV44OpenFieldFrameGeometryPanel.value
                    }, {
                        "QMW geometry viewer unavailable: start the V4.4 FieldFrame launcher.".warn
                    })
                });
            Button(window, Rect(915, 654, 175, 28))
                .states_([["OPEN SCATTERING", Color.black, Color.magenta(0.72)]])
                .action_({
                    if(~qmwInteractionV1OpenPanel.notNil, {
                        ~qmwInteractionV1OpenPanel.value
                    }, {
                        "QMW scattering viewer unavailable: start the V4.5 interaction launcher.".warn
                    })
                });
        });
    });

    meshScaleStatus = StaticText(window, Rect(20, 276, 400, 22))
        .string_("FIELD SPACETIME MESH — waiting for history")
        .stringColor_(Color.grey(0.86));
    meshColorMenu = PopUpMenu(window, Rect(430, 276, 120, 22))
        .items_(["color: momentum", "color: energy", "color: phase"])
        .value_(0)
        .action_({ |menu|
            ~qmwQFTV3MeshColorMode = menu.value;
            phiView !? { |view| view.refresh };
        });
    correlationMeshButton = Button(window, Rect(560, 276, 120, 22))
        .states_([
            ["correlation links: on"], ["correlation links: off"]
        ])
        .action_({ |button|
            ~qmwQFTV3MeshCorrelations = 1 - button.value;
            phiView !? { |view| view.refresh };
        });
    phiView = makeFieldMesh.(Rect(20, 302, 660, 238));
    makeLabel.("LOCAL ENERGY DENSITY — frame-normalized", Rect(20, 552, 400, 22));
    absoluteEnergyView = UserView(window, Rect(420, 555, 165, 16))
        .background_(Color.grey(0.12))
        .drawFunc_({ |view|
            var energy = ~qmwQFTV3Global[0].max(0);
            // Fixed logarithmic calibration: 0 is empty and E=100 is full.
            // Unlike the spatial bars below, this never rescales per frame.
            var meterValue = ((energy + 1).log / 101.log).clip(0, 1);
            var width = view.bounds.width;
            var height = view.bounds.height;
            Pen.fillColor = Color(1.0, 0.54, 0.08, 0.92);
            Pen.fillRect(Rect(0, 0, width * meterValue, height));
            Pen.strokeColor = Color(1.0, 0.82, 0.32, 0.9);
            Pen.width = 1;
            Pen.strokeRect(Rect(0.5, 0.5, width - 1, height - 1));
        });
    absoluteEnergyStatus = StaticText(window, Rect(590, 552, 90, 22))
        .string_("ABS E 0.0000")
        .stringColor_(Color.yellow(0.82));
    energyView = MultiSliderView(window, Rect(20, 578, 660, 100))
        .value_(~qmwQFTV3Energy).drawLines_(true).isFilled_(true)
        .fillColor_(Color.yellow(0.68, 0.75)).background_(Color.grey(0.16));
    makeLabel.("NORMAL-MODE OCCUPATIONS — frame-normalized", Rect(20, 690, 450, 22));
    occupationView = MultiSliderView(window, Rect(20, 716, 660, 100))
        .value_(~qmwQFTV3Occupations).drawLines_(true).isFilled_(true)
        .fillColor_(Color.green(0.64, 0.75)).background_(Color.grey(0.16));

    makeLabel.("CONNECTED FIELD CORRELATION", Rect(730, 660, 330, 22));
    correlationView = UserView(window, Rect(730, 688, 360, 360))
        .background_(Color.grey(0.14))
        .drawFunc_({ |view|
            var width = view.bounds.width / siteCount;
            var height = view.bounds.height / siteCount;
            var maximum = ~qmwQFTV3Correlation.collect(_.abs).maxItem.max(1e-9);
            siteCount.do { |row|
                siteCount.do { |column|
                    var value = ~qmwQFTV3Correlation[
                        (row * siteCount) + column
                    ];
                    var strength = (value.abs / maximum).sqrt.clip(0, 1);
                    Pen.fillColor = if(value >= 0, {
                        Color(0.05, 0.65 * strength, 0.8 * strength)
                    }, {
                        Color(0.75 * strength, 0.08, 0.55 * strength)
                    });
                    Pen.fillRect(Rect(
                        column * width, row * height, width - 1, height - 1
                    ));
                };
            };
        });

    temporalStatus = StaticText(window, Rect(20, 832, 680, 24))
        .string_("Gaussian clock: waiting for site-reduced Bures motion")
        .stringColor_(Color.yellow(0.75));
    status = StaticText(window, Rect(20, 860, 680, 24))
        .string_("waiting for scalar-field frames on UDP %".format(dataPort))
        .stringColor_(Color.grey(0.9));
    parameterStatus = StaticText(window, Rect(20, 888, 680, 48))
        .string_("state localized    mass 0.6    c 1    site 4    amplitude 1")
        .stringColor_(Color.cyan(0.8));

    makeLabel.(
        "PULSE SITE MIXER — post-adapter gain 0-2; center is unity",
        Rect(20, 944, 500, 22)
    );
    siteGainView = MultiSliderView(window, Rect(20, 970, siteMixerWidth, 150))
        .value_(~qmwQFTV3SiteGains / 2)
        .elasticMode_(true)
        .gap_(2)
        .drawLines_(true)
        .isFilled_(true)
        .fillColor_(Color.cyan(0.68, 0.78))
        .background_(Color.grey(0.16))
        .action_({ |view|
            ~qmwQFTV3SiteGains = view.value.collect { |value|
                (value * 2).clip(0, 2)
            };
            ~qmwQFTV3UpdateSiteAudioGains.();
        });
    siteMuteButtons = Array.fill(siteCount, { |site|
        Button(
            window,
            Rect(
                20 + (site * (siteMixerWidth / siteCount)), 1128,
                (siteMixerWidth / siteCount) - 2, 26
            )
        )
            .states_([
                [(site + 1).asString, Color.grey(0.85), Color.grey(0.24)],
                ["M" ++ (site + 1), Color.white, Color.red(0.58)]
            ])
            .value_(~qmwQFTV3SiteMutes[site])
            .action_({ |button|
                ~qmwQFTV3SiteMutes[site] = button.value;
                ~qmwQFTV3UpdateSiteAudioGains.();
            });
    });
    Button(window, Rect(20, 1164, 150, 28))
        .states_([["all gains to unity"]])
        .action_({
            ~qmwQFTV3SiteGains = Array.fill(siteCount, 1.0);
            siteGainView.value_(~qmwQFTV3SiteGains / 2);
            ~qmwQFTV3UpdateSiteAudioGains.();
        });
    Button(window, Rect(180, 1164, 150, 28))
        .states_([["unmute all"]])
        .action_({
            ~qmwQFTV3SiteMutes = Array.fill(siteCount, 0);
            siteMuteButtons.do { |button| button.value_(0) };
            ~qmwQFTV3UpdateSiteAudioGains.();
        });
    StaticText(window, Rect(20, 1200, siteMixerWidth, 46))
        .string_(
            "Pulse mixer controls audio adapters only: scientific field values, "
            ++ "energy, correlations, and evolution remain unchanged."
        )
        .stringColor_(Color.grey(0.68));
    makeLabel.("PULSE RING MODULATION", Rect(20, 1254, 260, 22));
    ringModBlendSlider = makeSlider.(
        "ring blend", Rect(20, 1280, 210, 28),
        ControlSpec(0, 1, \lin, 0.001, 0), 0,
        { |view|
            ~qmwQFTV3RingModBlend = view.value;
            ~qmwQFTV3UpdateRingMod.();
        },
        82
    );
    ringModHarmonicSlider = makeSlider.(
        "overtone", Rect(245, 1280, 210, 28),
        ControlSpec(1, siteCount, \lin, 1, 2), 2,
        { |view|
            ~qmwQFTV3RingModHarmonic = view.value.asInteger;
            ~qmwQFTV3UpdateRingMod.();
        },
        82
    );
    ringModFineTuneSlider = makeSlider.(
        "fine (cents)", Rect(470, 1280, 210, 28),
        ControlSpec(-100, 100, \lin, 0.1, 0), 0,
        { |view|
            ~qmwQFTV3RingModFineTuneCents = view.value;
            ~qmwQFTV3UpdateRingMod.();
        },
        82
    );
    StaticText(window, Rect(20, 1314, 660, 42))
        .string_(
            "Modulator = audible fundamental × selected overtone, then fine-detuned ±100 cents; "
            ++ "blend 0 is dry and 1 is fully ring-modulated."
        )
        .stringColor_(Color.yellow(0.72));
    makeLabel.("PULSE WAVEFOLDER", Rect(20, 1362, 260, 22));
    wavefoldBlendSlider = makeSlider.(
        "fold blend", Rect(20, 1388, 320, 28),
        ControlSpec(0, 1, \lin, 0.001, 0), 0,
        { |view|
            ~qmwQFTV3WavefoldBlend = view.value;
            ~qmwQFTV3UpdateWavefold.();
        },
        82
    );
    wavefoldDriveSlider = makeSlider.(
        "fold drive", Rect(360, 1388, 320, 28),
        ControlSpec(1, 32, \exp, 0.01, 4), 4,
        { |view|
            ~qmwQFTV3WavefoldDrive = view.value;
            ~qmwQFTV3UpdateWavefold.();
        },
        82
    );
    wavefoldWarpSlider = makeSlider.(
        "warp amount", Rect(20, 1422, 320, 28),
        ControlSpec(0, 1, \lin, 0.001, 0), 0,
        { |view|
            ~qmwQFTV3WavefoldWarpAmount = view.value;
            ~qmwQFTV3UpdateWavefold.();
        },
        90
    );
    wavefoldWarpShapeMenu = PopUpMenu(window, Rect(360, 1422, 320, 28))
        .items_(["warp: Bend +", "warp: Bend -", "warp: Sine", "warp: Fold"])
        .value_(0)
        .action_({ |menu|
            ~qmwQFTV3WavefoldWarpShape = menu.value;
            ~qmwQFTV3UpdateWavefold.();
        });
    makeLabel.("PULSE FUZZ", Rect(20, 1472, 260, 22));
    fuzzBlendSlider = makeSlider.(
        "fuzz blend", Rect(20, 1498, 320, 28),
        ControlSpec(0, 1, \lin, 0.001, 0), 0,
        { |view|
            ~qmwQFTV3FuzzBlend = view.value;
            ~qmwQFTV3UpdateFuzz.();
        },
        82
    );
    fuzzDriveSlider = makeSlider.(
        "fuzz drive", Rect(360, 1498, 320, 28),
        ControlSpec(0.25, 12, \exp, 0.01, 2.5), 2.5,
        { |view|
            ~qmwQFTV3FuzzDrive = view.value;
            ~qmwQFTV3UpdateFuzz.();
        },
        82
    );
    fuzzSecondSlider = makeSlider.(
        "2nd order (even)", Rect(20, 1532, 320, 28),
        ControlSpec(0, 2, \lin, 0.001, 0), 0,
        { |view|
            ~qmwQFTV3FuzzSecond = view.value;
            ~qmwQFTV3UpdateFuzz.();
        },
        98
    );
    fuzzThirdSlider = makeSlider.(
        "3rd + 5th + 7th (odd)", Rect(360, 1532, 320, 28),
        ControlSpec(0, 2, \lin, 0.001, 0.65), 0.65,
        { |view|
            ~qmwQFTV3FuzzThird = view.value;
            // The linked higher-order control gives sustained Muff density
            // without adding another narrow performance fader.
            ~qmwQFTV3FuzzHigher = (view.value * 1.3).clip(0, 2);
            ~qmwQFTV3UpdateFuzz.();
        },
        98
    );
    fuzzBiasSlider = makeSlider.(
        "bias", Rect(20, 1566, 320, 28),
        ControlSpec(-0.75, 0.75, \lin, 0.001, 0), 0,
        { |view|
            ~qmwQFTV3FuzzBias = view.value;
            ~qmwQFTV3UpdateFuzz.();
        },
        82
    );
    fuzzToneSlider = makeSlider.(
        "Muff tone (dark → bright)", Rect(360, 1566, 320, 28),
        ControlSpec(0, 1, \lin, 0.001, 0.35), 0.35,
        { |view|
            ~qmwQFTV3FuzzTone = view.value;
            ~qmwQFTV3UpdateFuzz.();
        },
        128
    );

    makeLabel.("GAUSSIAN DESCRIPTOR — SOUND ADAPTER ONLY", Rect(20, 1582, 420, 22));
    descriptorSourceMenu = PopUpMenu(window, Rect(20, 1608, 250, 28))
        .items_([
            "Quantum", "Manual", "Quantum + Manual",
            "Quantum + LFO", "Manual + LFO"
        ])
        .value_(0)
        .action_({ |menu|
            ~qmwQFTV3DescriptorSource = menu.value;
            descriptorStatus !? { |view|
                view.string_(
                    "source: % — sampled once per pulse"
                    .format(menu.items[menu.value])
                )
            };
        });
    descriptorClockMenu = PopUpMenu(window, Rect(280, 1608, 190, 28))
        .items_(["LFO clock: free Hz", "LFO clock: QMW time"])
        .value_(0)
        .action_({ |menu| ~qmwQFTV3DescriptorClock = menu.value });
    descriptorStatus = StaticText(window, Rect(480, 1608, 200, 28))
        .string_("source: Quantum")
        .stringColor_(Color.cyan(0.72));
    descriptorRotationSlider = makeSlider.(
        "descriptor phase rotation", Rect(20, 1646, 660, 28),
        ControlSpec(-180, 180, \lin, 1, 0), 0,
        { |view|
            ~qmwQFTV3DescriptorRotationDegrees = view.value;
        },
        138
    );
    descriptorManualSliders = Array.fill(3, { |axis|
        makeSlider.(
            descriptorAxisNames[axis] ++ " manual",
            Rect(20, 1684 + (axis * 38), 155, 28),
            ControlSpec(-1, 1, \lin, 0.001, 0), 0,
            { |view| ~qmwQFTV3DescriptorManual[axis] = view.value }, 58
        )
    });
    descriptorDepthSliders = Array.fill(3, { |axis|
        makeSlider.(
            descriptorAxisNames[axis] ++ " depth",
            Rect(185, 1684 + (axis * 38), 155, 28),
            ControlSpec(0, 1, \lin, 0.001, 0), 0,
            { |view| ~qmwQFTV3DescriptorLFODepth[axis] = view.value }, 55
        )
    });
    descriptorRateSliders = Array.fill(3, { |axis|
        makeSlider.(
            descriptorAxisNames[axis] ++ " rate",
            Rect(350, 1684 + (axis * 38), 155, 28),
            ControlSpec(0.001, 20, \exp, 0.001, [0.11, 0.17, 0.23][axis]),
            [0.11, 0.17, 0.23][axis],
            { |view| ~qmwQFTV3DescriptorLFORate[axis] = view.value }, 48
        )
    });
    descriptorPhaseSliders = Array.fill(3, { |axis|
        makeSlider.(
            descriptorAxisNames[axis] ++ " phase",
            Rect(515, 1684 + (axis * 38), 165, 28),
            ControlSpec(0, 360, \lin, 1, [0, 120, 240][axis]),
            [0, 120, 240][axis],
            { |view| ~qmwQFTV3DescriptorLFOPhase[axis] = view.value }, 55
        )
    });
    StaticText(window, Rect(20, 1800, 660, 48))
        .string_(
            "Event-sampled X/Y/Z modulation and X/Y phase-plane rotation affect "
            ++ "sound only; this is not physical quantum or squeezing phase."
        )
        .stringColor_(Color.yellow(0.70));

    makeLabel.(
        "Correlation color: cyan positive, magenta negative; intensity is frame-normalized.",
        Rect(730, 1024, 360, 46)
    );

    makeLabel.("AUDIO OUTPUT", Rect(730, 1080, 180, 22));
    audioDeviceMenu = PopUpMenu(window, Rect(730, 1106, 360, 28))
        .items_(audioDeviceItems)
        .value_(
            audioDeviceValues.indexOfEqual(
                ~qmwQFTV3SelectedOutputDevice
            ) ? 0
        );
    outputLayoutMenu = PopUpMenu(window, Rect(730, 1144, 230, 28))
        .items_(if(splitFieldOutput, {[
            "4-ch: plucks 1–2 | field 3–4",
            "8-ch: plucks 1–2 | field 3–4"
        ]}, {[
            "stereo — outputs 1–2",
            "8-channel device — stereo on 1–2"
        ]}))
        .value_(if(~qmwQFTV3OutputChannels >= 8, { 1 }, { 0 }));
    Button(window, Rect(970, 1144, 120, 28))
        .states_([["refresh devices"]])
        .action_({ refreshAudioDevices.() });
    Button(window, Rect(730, 1182, 360, 30))
        .states_([["apply + reboot SuperCollider audio"]])
        .action_({
            ~qmwQFTV3ApplyAudioOutput.(
                audioDeviceValues[audioDeviceMenu.value],
                if(splitFieldOutput, { [4, 8] }, { [2, 8] })[
                    outputLayoutMenu.value
                ]
            )
        });
    audioStatus = StaticText(window, Rect(730, 1218, 360, 46))
        .string_(
            if(splitFieldOutput, {
                "active: % — % channels; V% split: plucks 1–2, field 3–4"
            }, {
                "active: % — % channels; V% stereo on outputs 1–2"
            }).format(
                ~qmwQFTV3SelectedOutputDevice ? "system default",
                ~qmwQFTV3OutputChannels,
                instrumentVersion
            )
        )
        .stringColor_(Color.cyan(0.8));

    makeLabel.(
        "PULSE POST-RING / FOLD / FUZZ VU — % LANES".format(siteCount),
        Rect(730, 1280, 360, 22)
    );
    pulseMeterView = MultiSliderView(window, Rect(730, 1306, 360, 150))
        .value_(~qmwQFTV3PulseMeters)
        .elasticMode_(true)
        .gap_(2)
        .drawLines_(true)
        .isFilled_(true)
        .fillColor_(Color(1.0, 0.42, 0.10, 0.88))
        .background_(Color.grey(0.12));
    pulseMeterStatus = StaticText(window, Rect(730, 1462, 360, 22))
        .string_("post-FX peak 0.000")
        .stringColor_(Color.yellow(0.82));
    makeLabel.("QHO-FM PULSE VOICE — EVENT-SAMPLED", Rect(730, 1500, 360, 22));
    fmRatioSlider = makeSlider.(
        "FM overtone", Rect(730, 1526, 360, 28),
        ControlSpec(1, siteCount, \lin, 1, 2), 2,
        { |view| ~qmwQFTV3FMRatio = view.value.asInteger }, 95
    );
    fmIndexSlider = makeSlider.(
        "base index", Rect(730, 1564, 360, 28),
        ControlSpec(0, 12, \lin, 0.01, 0.5), 0.5,
        { |view| ~qmwQFTV3FMIndex = view.value }, 95
    );
    fmQuantumDepthSlider = makeSlider.(
        "descriptor depth", Rect(730, 1602, 360, 28),
        ControlSpec(0, 8, \lin, 0.01, 2), 2,
        { |view| ~qmwQFTV3FMQuantumDepth = view.value }, 105
    );
    StaticText(window, Rect(730, 1640, 360, 80))
        .string_(
            "Select QHO FM above. Carrier follows the site/QHO pitch; the "
            ++ "modulator is locked to the chosen overtone. Local Gaussian "
            ++ "descriptors add a bounded modulation-index contribution."
        )
        .stringColor_(Color.yellow(0.70));
    makeLabel.(
        "%-VOICE MIXER — LIVE GAIN".format(voiceCount),
        Rect(730, 1730, voiceMixerWidth, 22)
    );
    voiceGainView = MultiSliderView(window, Rect(730, 1756, voiceMixerWidth, 88))
        .value_(~qmwQFTV3VoiceGainSliderValues.())
        .elasticMode_(true)
        .gap_(3)
        .drawLines_(true)
        .isFilled_(true)
        .fillColor_(Color(0.20, 0.78, 1.0, 0.86))
        .background_(Color.grey(0.12))
        .action_({ |view|
            ~qmwQFTV3VoiceGains = view.value.collect { |value, voice|
                (value * ~qmwQFTV3VoiceGainCeilings[voice]).clip(
                    0, ~qmwQFTV3VoiceGainCeilings[voice]
                )
            };
            ~qmwQFTV3PulseVoiceMode = 4;
            voiceMenu.value_(4);
            ~qmwQFTV3UpdateVoiceMixer.();
            voiceMixerStatus.string_("custom mix — active tails follow faders");
        });
    Array.fill(voiceCount, { |voice|
        StaticText(window, Rect(
            730 + (voice * voiceColumnWidth), 1848,
            voiceColumnWidth - 2, 18
        ))
            .align_(\center)
            .string_(voiceNames[voice])
            .stringColor_(Color.grey(0.82))
    });
    voiceMuteButtons = Array.fill(voiceCount, { |voice|
        Button(window, Rect(
            730 + (voice * voiceColumnWidth), 1870,
            voiceColumnWidth - 2, 26
        ))
            .states_([
                ["on", Color.grey(0.85), Color.grey(0.24)],
                ["mute", Color.white, Color.red(0.58)]
            ])
            .value_(~qmwQFTV3VoiceMutes[voice])
            .action_({ |button|
                ~qmwQFTV3VoiceMutes[voice] = button.value;
                ~qmwQFTV3PulseVoiceMode = 4;
                voiceMenu.value_(4);
                ~qmwQFTV3UpdateVoiceMixer.();
                voiceMixerStatus.string_("custom mix — active tails follow mutes");
            })
    });
    voiceMixerStatus = StaticText(window, Rect(730, 1904, 360, 58))
        .string_(
            if(blochVoiceEnabled, {
                "Gaussian only by default. Bloch is a persistent read-only "
                ++ "fifth channel; its fader reaches 4x (+6 dB above the "
                ++ "other voice ceilings) and follows the full-engine OSC mirror."
            }, {
                "Gaussian only by default. Layered is its own channel and creates "
                ++ "both Simple and Gaussian voices with equal-power trim."
            })
        )
        .stringColor_(Color.cyan(0.72));

    makeLabel.(
        "FIELD SPECTRAL MIXER — CONTINUOUS FIELD ONLY",
        Rect(730, 1980, 360, 22)
    );
    fieldGainView = MultiSliderView(window, Rect(730, 2006, 360, 120))
        .value_(~qmwQFTV3FieldLaneGains / 2)
        .elasticMode_(true)
        .gap_(2)
        .drawLines_(true)
        .isFilled_(true)
        .fillColor_(Color(0.30, 0.92, 0.62, 0.84))
        .background_(Color.grey(0.12))
        .action_({ |view|
            ~qmwQFTV3FieldLaneGains = view.value.collect { |value|
                (value * 2).clip(0, 2)
            };
            ~qmwQFTV3UpdateFieldSpectralMix.();
        });
    fieldMuteButtons = Array.fill(siteCount, { |site|
        Button(window, Rect(
            730 + (site * (360 / siteCount)), 2132,
            (360 / siteCount) - 1, 24
        ))
            .states_([
                [(site + 1).asString, Color.grey(0.85), Color.grey(0.24)],
                ["M", Color.white, Color.red(0.58)]
            ])
            .value_(~qmwQFTV3FieldLaneMutes[site])
            .action_({ |button|
                ~qmwQFTV3FieldLaneMutes[site] = button.value;
                ~qmwQFTV3UpdateFieldSpectralMix.();
            })
    });
    Button(window, Rect(730, 2164, 175, 28))
        .states_([["field gains to unity"]])
        .action_({
            ~qmwQFTV3FieldLaneGains = Array.fill(siteCount, 1.0);
            fieldGainView.value_(~qmwQFTV3FieldLaneGains / 2);
            ~qmwQFTV3UpdateFieldSpectralMix.();
        });
    Button(window, Rect(915, 2164, 175, 28))
        .states_([["unmute field"]])
        .action_({
            ~qmwQFTV3FieldLaneMutes = Array.fill(siteCount, 0);
            fieldMuteButtons.do { |button| button.value_(0) };
            ~qmwQFTV3UpdateFieldSpectralMix.();
        });
    StaticText(window, Rect(730, 2198, 360, 38))
        .string_(
            "Shapes the 16 continuous field components only; pluck lane gains remain independent."
        )
        .stringColor_(Color.green(0.72));

    makeLabel.("MIDI INPUT — PRESET RECALL", Rect(730, 2250, 360, 22));
    midiInputMenu = PopUpMenu(window, Rect(730, 2276, 360, 28))
        .items_(midiInputItems)
        .value_(
            midiInputValues.detectIndex { |source|
                source.notNil and: {
                    source.uid == ~qmwQFTV3SelectedMIDIInputUID
                }
            } ? 0
        )
        .action_({ |menu|
            var selectedSource = midiInputValues[menu.value];
            ~qmwQFTV3SelectedMIDIInputUID = if(selectedSource.isNil, {
                nil
            }, {
                selectedSource.uid
            });
            installMIDIPresetMapping.();
        });
    Button(window, Rect(730, 2314, 120, 28))
        .states_([["refresh MIDI"]])
        .action_({
            refreshMIDIInputs.();
            installMIDIPresetMapping.();
        });
    midiInputStatus = StaticText(window, Rect(860, 2310, 230, 58))
        .string_("Select the Akai MPK; C0 recalls preset 1.")
        .stringColor_(Color.yellow(0.78));
    installMIDIPresetMapping.();

    if(terrainEnabled) {
        makeLabel.(
            "V4.2 DENSITY LAGRANGIAN → EFFECTIVE MEMBRANE FLOW",
            Rect(20, 2380, 1070, 24)
        );
        terrainStatus = StaticText(window, Rect(20, 2408, 1070, 24))
            .string_(
                "UNAVAILABLE — waiting for density-terrain capability on UDP %"
                .format(terrainPort)
            )
            .stringColor_(Color.yellow(0.78));
        terrainAvailableButton = Button(window, Rect(20, 2440, 180, 28))
            .states_([
                ["terrain unavailable", Color.grey(0.74), Color.grey(0.22)],
                ["terrain available", Color.black, Color.green(0.72)]
            ])
            .enabled_(false);
        terrainSonifyButton = Button(window, Rect(210, 2440, 230, 28))
            .states_([
                ["sonify crossings: off"],
                ["sonify crossings: on", Color.black, Color.cyan(0.72)]
            ])
            .value_(~qmwQFTV42TerrainSonify)
            .enabled_(false)
            .action_({ |button|
                ~qmwQFTV42TerrainSonify = button.value;
            });
        terrainEventButton = Button(window, Rect(450, 2440, 210, 28))
            .states_([
                ["membrane crossing", Color.grey(0.72), Color.grey(0.22)],
                ["MEMBRANE CROSSED", Color.black, Color(1.0, 0.55, 0.10)]
            ])
            .enabled_(false);
        StaticText(window, Rect(680, 2440, 410, 36))
            .string_(
                "Sound adapter only: crossings excite existing pulse voices; "
                ++ "rho and the QFT field remain authoritative."
            )
            .stringColor_(Color.grey(0.68));
        makeLabel.("TERRAIN COORDINATES q", Rect(20, 2480, 520, 22));
        makeLabel.("TERRAIN VELOCITIES qdot", Rect(570, 2480, 520, 22));
        terrainQView = MultiSliderView(window, Rect(20, 2506, 520, 104))
            .value_(~qmwQFTV42TerrainQ)
            .drawLines_(true)
            .isFilled_(true)
            .fillColor_(Color.green(0.62, 0.78))
            .background_(Color.grey(0.14));
        terrainQdotView = MultiSliderView(window, Rect(570, 2506, 520, 104))
            .value_(Array.fill(siteCount, 0.5))
            .drawLines_(true)
            .isFilled_(true)
            .fillColor_(Color(1.0, 0.46, 0.12, 0.82))
            .background_(Color.grey(0.14));
        terrainGlobalStatus = StaticText(window, Rect(20, 2618, 1070, 24))
            .string_("purity —    L —    E —    max flux —    crossings/frame —")
            .stringColor_(Color.cyan(0.76));
        terrainEventStatus = StaticText(window, Rect(20, 2648, 1070, 28))
            .string_("No effective membrane crossing observed yet.")
            .stringColor_(Color.yellow(0.76));
    };

    window.onClose_({
        // OSC callbacks can already be queued on AppClock when Qt destroys
        // the window. Clear their lexical view references first so a deferred
        // status update cannot call stringColor_ on a dead Qt palette.
        ~qmwQFTV3Window = nil;
        window = nil;
        terrainStatus = nil; terrainGlobalStatus = nil;
        terrainEventStatus = nil; terrainAvailableButton = nil;
        terrainSonifyButton = nil; terrainEventButton = nil;
        performanceStatus = nil; audioStatus = nil;
        ~qmwQFTV3Stop.()
    });
    // A wrapper may request a saved startup slot. Apply only after every
    // control exists, so the preset configures the actual pulse voices.
    ~qmwQFTV3StartupPresetSlot !? { |slot|
        recallPresetSlot.(slot, "startup")
    };
    window.front;
}.defer;

~qmwQFTV3Stop = {
    ~qmwQFTV3AudioReady = false;
    ~qmwQFTV3ServerQuitHandler !? { |handler| s.onQuitRemove(handler) };
    ~qmwQFTV3ServerQuitHandler = nil;
    ~qmwQFTV3MIDIPresetNoteOn !? { |handler| handler.free };
    ~qmwQFTV3MIDIPresetNoteOn = nil;
    [
        \qmwQFTV3Begin, \qmwQFTV3Phi, \qmwQFTV3Pi,
        \qmwQFTV3Energy, \qmwQFTV3Occupations, \qmwQFTV3Frequencies,
        \qmwQFTV3Correlation, \qmwQFTV3CorrelationRow,
        \qmwQFTV3Global, \qmwQFTV3Parameters,
        \qmwQFTV3End, \qmwQFTV3TemporalGlobal, \qmwQFTV3TemporalConfig,
        \qmwQFTV3PulseMeters,
        \qmwQFTV3TemporalSite, \qmwQFTV3TemporalPulse,
        \qmwQFTV3GeodesicSite, \qmwQFTV3GeodesicPulse,
        \qmwQFTV3PerformanceSaved
    ].do { |key| OSCdef(key).free };
    if(terrainEnabled) {
        [
            \qmwQFTV42TerrainBegin, \qmwQFTV42TerrainAvailable,
            \qmwQFTV42TerrainDimension, \qmwQFTV42TerrainQ,
            \qmwQFTV42TerrainQdot, \qmwQFTV42TerrainGlobal,
            \qmwQFTV42TerrainEvent, \qmwQFTV42TerrainEnd
        ].do { |key| OSCdef(key).free };
        ~qmwQFTV42TerrainWatchdog !? { |routine| routine.stop };
        ~qmwQFTV42TerrainWatchdog = nil;
    };
    if(s.isRecording) { s.stopRecording };
    ~qmwQFTV3RecordingReady = false;
    ~qmwQFTV3Synth !? { |synth| synth.set(\gate, 0) };
    ~qmwQFTV3PulseMixerSynth !? { |synth| synth.free };
    ~qmwQFTV3PooledBankSynth !? { |synth| synth.free };
    ~qmwQFTV3PooledMixerSynth !? { |synth| synth.free };
    ~qmwQFTV3DrySynth !? { |synth| synth.free };
    ~qmwQFTV3FieldDrySynth !? { |synth| synth.free };
    ~qmwQFTV3SteadyClock !? { |routine| routine.stop };
    ~qmwQFTV3ActivePulseVoices.clear;
    ~qmwQFTV3SourceGroup !? { |group| group.freeAll; group.free };
    ~qmwQFTV3FXGroup !? { |group| group.freeAll; group.free };
    ~qmwQFTV3SourceBus !? { |bus| bus.free };
    if(splitFieldOutput) { ~qmwQFTV3FieldBus !? { |bus| bus.free } };
    ~qmwQFTV3PulseBus !? { |bus| bus.free };
    ~qmwQFTV3PooledPulseBus !? { |bus| bus.free };
    ~qmwQFTV3RingModMixBus !? { |bus| bus.free };
    ~qmwQFTV3RingModFrequencyBus !? { |bus| bus.free };
    ~qmwQFTV3WavefoldMixBus !? { |bus| bus.free };
    ~qmwQFTV3WavefoldDriveBus !? { |bus| bus.free };
    ~qmwQFTV3WavefoldWarpAmountBus !? { |bus| bus.free };
    ~qmwQFTV3WavefoldWarpShapeBus !? { |bus| bus.free };
    ~qmwQFTV3FuzzMixBus !? { |bus| bus.free };
    ~qmwQFTV3FuzzDriveBus !? { |bus| bus.free };
    ~qmwQFTV3FuzzSecondBus !? { |bus| bus.free };
    ~qmwQFTV3FuzzThirdBus !? { |bus| bus.free };
    ~qmwQFTV3FuzzHigherBus !? { |bus| bus.free };
    ~qmwQFTV3FuzzBiasBus !? { |bus| bus.free };
    ~qmwQFTV3FuzzToneBus !? { |bus| bus.free };
    ~qmwQFTV3VoiceGainBus !? { |bus| bus.free };
    ~qmwQFTV42BFXSendControlBus !? { |bus| bus.free };
    ~qmwQFTV42BFXSendBus !? { |bus| bus.free };
    ~qmwQFTV3RingModMixBus = nil;
    ~qmwQFTV3RingModFrequencyBus = nil;
    ~qmwQFTV3WavefoldMixBus = nil;
    ~qmwQFTV3WavefoldDriveBus = nil;
    ~qmwQFTV3WavefoldWarpAmountBus = nil;
    ~qmwQFTV3WavefoldWarpShapeBus = nil;
    ~qmwQFTV3FuzzMixBus = nil;
    ~qmwQFTV3FuzzDriveBus = nil;
    ~qmwQFTV3FuzzSecondBus = nil;
    ~qmwQFTV3FuzzThirdBus = nil;
    ~qmwQFTV3FuzzHigherBus = nil;
    ~qmwQFTV3FuzzBiasBus = nil;
    ~qmwQFTV3FuzzToneBus = nil;
    ~qmwQFTV3VoiceGainBus = nil;
    ~qmwQFTV42BFXSendControlBus = nil;
    ~qmwQFTV42BFXSendBus = nil;
    ~qmwQFTV3Synth = nil;
    ~qmwQFTV3SourceGroup = nil;
    ~qmwQFTV3FXGroup = nil;
    ~qmwQFTV3SourceBus = nil;
    ~qmwQFTV3FieldBus = nil;
    ~qmwQFTV3PulseMixerSynth = nil;
    ~qmwQFTV3PulseBus = nil;
    ~qmwQFTV3PooledBankSynth = nil;
    ~qmwQFTV3PooledMixerSynth = nil;
    ~qmwQFTV3PooledPulseBus = nil;
    control.sendMsg(oscRoot ++ "/control/quit", 1);
    "QMW scalar field V% instrument stopped."
        .format(instrumentVersion).postln;
};

"QMW scalar field V% ready: % QHOs, data UDP %, controls UDP %, % audio voices (Bloch %)."
    .format(
        instrumentVersion, siteCount, dataPort, controlPort, voiceCount,
        if(blochVoiceEnabled, { "enabled" }, { "disabled" })
    ).postln;
)
